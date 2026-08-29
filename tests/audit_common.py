"""audit_common.py — shared utilities for tests/ scripts.

Common code used by release_matrix.py, test_setter_pairs.py, and
test_crud_pairs.py. Anything shared between two or more test scripts
lives here so we don't duplicate it.

Currently provides:
  - gather_device(device, label) — live-read pass producing a per-device
    state dict (facts, ports, ring, management, unused_safe_to_touch,
    flattened safety variables).
  - gather_one_ip(...) — convenience wrapper for one-shot diagnostic use.

Tolerant by design: any individual gather op can fail (method not
supported on this firmware, device returns malformed data, etc.) without
aborting the whole gather. Failures are captured in `state['errors']`.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _safely_call(state: dict, key: str, fn, *args, **kwargs):
    """Run a gather function, capture exceptions to state['errors']."""
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        state.setdefault("errors", []).append({
            "phase": key,
            "error": str(e)[:200],
            "type": type(e).__name__,
        })
        return None


def _is_up(iface_data: dict) -> bool:
    """Return True if the interface row indicates an active link.

    Handles both schema-native field names (`oper_status`) and NAPALM-compat
    field names (`is_up`). Default False on uncertainty (safer for the
    unused-port computation — a link we can't classify is not "down").
    """
    if not isinstance(iface_data, dict):
        return False
    if "is_up" in iface_data:
        return bool(iface_data["is_up"])
    oper = iface_data.get("oper_status")
    if isinstance(oper, str):
        return oper.lower() in ("up", "1", "enabled", "active")
    if isinstance(oper, bool):
        return oper
    if isinstance(oper, int):
        return oper == 1
    return False


def _gather_facts(device) -> dict:
    """NAPALM standard get_facts → trimmed dict."""
    f = device.get_facts()
    if isinstance(f, tuple):
        f = f[0]
    if not isinstance(f, dict):
        return {}
    return {
        "hostname": f.get("hostname"),
        "vendor": f.get("vendor"),
        "model": f.get("model"),
        "serial_number": f.get("serial_number"),
        "os_version": f.get("os_version"),
        "uptime_sec": f.get("uptime"),
        "interface_count": len(f.get("interface_list", []) or []),
    }


_PHYSICAL_PORT_RE = __import__("re").compile(r"^\d+/\d+$")


def _is_physical_port(name) -> bool:
    """HiOS physical ports are '<slot>/<port>' with both fields all-digits.

    'cpu/1' passes the simpler '/ in name' check but is the CPU virtual
    interface and must not be admin-toggled. This is stricter.
    """
    return isinstance(name, str) and bool(_PHYSICAL_PORT_RE.match(name))


def _gather_ports(device) -> dict:
    """get_interfaces + get_lldp_neighbors → port classification dict.

    Returns:
        {
          "all": [sorted port names],
          "link_up": [sorted port names with active link],
          "link_down": [sorted port names with no link],
          "lldp_neighbor": [sorted port names with an LLDP neighbor],
        }
    """
    interfaces = device.get_interfaces()
    if isinstance(interfaces, tuple):
        interfaces = interfaces[0]
    if not isinstance(interfaces, dict):
        return {}

    # Filter to physical-looking ports only. Excludes 'cpu/1' and other
    # internal/virtual interfaces that must never be admin-toggled.
    physical = {p: d for p, d in interfaces.items() if _is_physical_port(p)}

    all_ports = sorted(physical.keys())
    link_up = sorted(p for p, d in physical.items() if _is_up(d))
    link_down = sorted(p for p, d in physical.items() if not _is_up(d))

    lldp_neighbor: list[str] = []
    try:
        lldp = device.get_lldp_neighbors()
        if isinstance(lldp, tuple):
            lldp = lldp[0]
        if isinstance(lldp, dict):
            lldp_neighbor = sorted(p for p in lldp.keys() if _is_physical_port(p))
    except Exception:
        # LLDP disabled or method failed — tolerate. unused_safe_to_touch
        # falls back to link_down only, which is still a safe pool.
        pass

    return {
        "all": all_ports,
        "link_up": link_up,
        "link_down": link_down,
        "lldp_neighbor": lldp_neighbor,
    }


def _gather_ring(device) -> dict:
    """get_mrp → ring config dict.

    Returns:
        {
          "configured": True,
          "domain_id": ...,
          "role": "manager" | "client" | ...,
          "ring_port_primary": "1/5",
          "ring_port_secondary": "1/6",
          "ring_state": ...,
          "operation": "enabled" | "disabled" | ...,
        }
    or {"configured": False} if MRP isn't running.
    """
    try:
        mrp = device.get_mrp()
    except Exception:
        return {"configured": False}
    if isinstance(mrp, tuple):
        mrp = mrp[0]
    if not isinstance(mrp, dict) or not mrp:
        return {"configured": False}

    # mrp is keyed by domain_id, take the first (typically only) entry
    first_key = next(iter(mrp))
    row = mrp[first_key]
    if not isinstance(row, dict):
        return {"configured": False}

    operation = row.get("operation")
    is_enabled = operation in ("enabled", True, 1, "1") or row.get("admin_status") == "up"

    return {
        "configured": bool(is_enabled),
        "domain_id": first_key,
        "role": row.get("role"),
        "ring_port_primary": row.get("ring_port1"),
        "ring_port_secondary": row.get("ring_port2"),
        "ring_port_primary_state": row.get("ring_port1_state"),
        "ring_port_secondary_state": row.get("ring_port2_state"),
        "operation": operation,
        "vlan": row.get("vlan"),
    }


def _gather_management(device) -> dict:
    """get_management → trimmed mgmt dict."""
    try:
        mgmt = device.get_management()
    except Exception:
        return {}
    if isinstance(mgmt, tuple):
        mgmt = mgmt[0]
    if not isinstance(mgmt, dict):
        return {}
    return {
        "ip_address": mgmt.get("ip_address"),
        "prefix_length": mgmt.get("prefix_length"),
        "gateway": mgmt.get("gateway"),
        "vlan_id": mgmt.get("vlan_id"),
        "protocol": mgmt.get("protocol"),
    }


def _compute_unused_safe_to_touch(state: dict) -> list[str]:
    """Compute the pool of ports a setter test can freely admin-down/up.

    Definition: link is currently DOWN AND port is not a ring member.

    A link-down port has no traffic, no neighbor connection, and can be
    safely toggled or reconfigured without disrupting anything. A
    link-up port might be an end host (camera, sensor, client) we should
    not touch, or part of an inter-switch path we should not disrupt —
    so it stays out of the pool.

    Ring members are removed even if they happen to be link-down (a
    transient state during ring failover; the ring management is still
    using the port).
    """
    ports = state.get("ports") or {}
    link_down = set(ports.get("link_down", []) or [])

    ring = state.get("ring") or {}
    ring_members: set[str] = set()
    if ring.get("configured"):
        for k in ("ring_port_primary", "ring_port_secondary"):
            v = ring.get(k)
            if v:
                ring_members.add(v)

    safe = sorted(link_down - ring_members)
    return safe


def gather_device(device, label: str | None = None) -> dict:
    """Gather state for one already-open NAPALM device.

    Pure function: no disk I/O, no globals. Caller is responsible for
    opening/closing the device and for writing the result somewhere.

    Returns a dict with the structure:
        {
          "label": str,
          "gathered_at": ISO timestamp,
          "facts": {...},
          "ports": {...},
          "ring": {...},
          "management": {...},
          "unused_safe_to_touch": [port names],
          "ring_port_primary": str | None,    # flattened for safety_runner
          "ring_port_secondary": str | None,
          "management_port": str | None,
          "errors": [{"phase": ..., "error": ..., "type": ...}, ...],
        }
    """
    state: dict[str, Any] = {
        "label": label,
        "gathered_at": _now_iso(),
        "errors": [],
    }

    state["facts"] = _safely_call(state, "facts", _gather_facts, device) or {}
    state["ports"] = _safely_call(state, "ports", _gather_ports, device) or {}
    state["ring"] = _safely_call(state, "ring", _gather_ring, device) or {"configured": False}
    state["management"] = _safely_call(state, "management", _gather_management, device) or {}

    # Derived state
    state["unused_safe_to_touch"] = _compute_unused_safe_to_touch(state)

    # Flatten safety variables to top level so safety_runner can substitute
    # them with simple {var} lookup. Future variables go here.
    ring = state.get("ring") or {}
    if ring.get("configured"):
        state["ring_port_primary"] = ring.get("ring_port_primary")
        state["ring_port_secondary"] = ring.get("ring_port_secondary")

    # management_port is currently undiscoverable — get_management returns
    # the management VLAN/IP but not the physical port. v2 enhancement.
    state["management_port"] = None

    return state


# ---------------------------------------------------------------------------
# Convenience entry point — for use as a standalone diagnostic
# ---------------------------------------------------------------------------

def gather_one_ip(ip: str, username: str = "admin", password: str = "private",
                  protocol: str = "mops", label: str | None = None) -> dict:
    """Open a device, gather, close. Returns the per-device state dict.

    Convenience wrapper for ad-hoc CLI use. The release_matrix orchestrator
    manages devices itself and calls gather_device() directly.
    """
    from napalm import get_network_driver
    driver = get_network_driver("hios")
    device = driver(ip, username, password, optional_args={"protocol": protocol})
    device.open()
    try:
        return gather_device(device, label=label)
    finally:
        try:
            device.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Schema metadata loader — used by the plan generator
# ---------------------------------------------------------------------------
#
# Mirrors audit_getters_v2.load_schemas() but covers ALL method kinds
# (reads + setters + CRUD), not just reads. Enriches each method with a
# `kind` field derived from `type`, and the set of protocols that can
# satisfy it (computed from wire source presence per attribute).
#
# Returns a flat dict of method_name → metadata.

import functools
import os as _os
import yaml as _yaml

_SCHEMAS_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                             "..", "crude_engine", "schemas")
_WIRE_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                          "..", "crude_engine", "wire")
_WIRE_EXEMPTIONS_PATH = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                                      "wire_exemptions.yaml")

_ALL_PROTOCOLS = ("mops", "snmp", "ssh")

# Method type → kind classification
_TYPE_TO_KIND = {
    "dict": "read",
    "list_append": "read",
    "upsert": "setter",
    "create": "crud_create",
    "delete": "crud_delete",
}


def _load_wire_exemptions() -> dict:
    """Load attr-level exemptions from tests/wire_exemptions.yaml."""
    if not _os.path.exists(_WIRE_EXEMPTIONS_PATH):
        return {}
    with open(_WIRE_EXEMPTIONS_PATH) as f:
        data = _yaml.safe_load(f) or {}
    out = {}
    for key, protocols in (data.get("exemptions") or {}).items():
        parts = key.split(":", 1)
        if len(parts) == 2:
            for proto in protocols:
                out[(parts[0], parts[1], proto)] = True
    return out


@functools.lru_cache(maxsize=None)
def _load_one_wire(wire_file: str) -> dict:
    """Load and return base wire YAML for `wire_file` (no .yaml extension)."""
    p = _os.path.join(_WIRE_DIR, f"{wire_file}.yaml")
    if not _os.path.exists(p):
        return {}
    with open(p) as f:
        return _yaml.safe_load(f) or {}


@functools.lru_cache(maxsize=None)
def _load_one_wire_overlay(wire_file: str, protocol: str) -> dict:
    """Load wire overlay for a protocol (e.g., wire/ssh/<wire_file>.yaml)."""
    p = _os.path.join(_WIRE_DIR, protocol, f"{wire_file}.yaml")
    if not _os.path.exists(p):
        return {}
    with open(p) as f:
        return _yaml.safe_load(f) or {}


def load_all_method_metadata(schemas_dir: str | None = None) -> dict:
    """Load every schema method with feature/type/kind/protocols metadata.

    Returns a dict keyed by method name:

        {
          "get_mrp": {
            "feature": "mrp",            # schema filename without .yaml
            "type": "dict",              # raw schema type field
            "kind": "read",              # bucketed: read|setter|crud_create|crud_delete
            "protocols": {"mops", "snmp"},  # protocols with at least one wire source
            "primary_key": "domain_id",
            "defaults": {...},
            "sub_tables": {...},
          },
          "set_mrp": {"feature": "mrp", "kind": "setter", ...},
          "create_mrp": {"feature": "mrp", "kind": "crud_create", ...},
          "delete_mrp": {"feature": "mrp", "kind": "crud_delete", ...},
          ...
        }

    The protocol detection mirrors audit_getters_v2.load_schemas: a
    protocol "supports" a method if any attribute used by the method has
    a wire source for that protocol (and the source isn't exempted).
    """
    schemas_dir = schemas_dir or _SCHEMAS_DIR
    exemptions = _load_wire_exemptions()
    out: dict[str, dict] = {}

    for sf in sorted(_os.listdir(schemas_dir)):
        if not sf.endswith(".yaml"):
            continue
        with open(_os.path.join(schemas_dir, sf)) as f:
            schema = _yaml.safe_load(f) or {}

        feature = sf[:-len(".yaml")]
        attrs = schema.get("attributes") or {}

        # Compute protocol support once per schema (shared across all methods
        # of this schema, since they all draw from the same attribute pool).
        supported_protocols: set[str] = set()
        for attr_name, attr_def in attrs.items():
            if not isinstance(attr_def, dict):
                continue
            wire_file = attr_def.get("source", feature)
            wire_attr = attr_def.get("wire", "")
            if not wire_file or not wire_attr:
                continue
            base = _load_one_wire(wire_file)
            wa = (base.get("attributes") or {}).get(wire_attr) or {}
            for proto in _ALL_PROTOCOLS:
                if (wire_file, wire_attr, proto) in exemptions:
                    continue
                if proto in (wa.get("sources") or {}):
                    supported_protocols.add(proto)
            # SSH overlay
            ssh_overlay = _load_one_wire_overlay(wire_file, "ssh")
            if ssh_overlay:
                ssh_wa = (ssh_overlay.get("attributes") or {}).get(wire_attr) or {}
                if "ssh" in (ssh_wa.get("sources") or {}):
                    if (wire_file, wire_attr, "ssh") not in exemptions:
                        supported_protocols.add("ssh")

        # Now enumerate methods
        for method_name, m_def in (schema.get("methods") or {}).items():
            if not isinstance(m_def, dict):
                continue
            # Resolve schema reference (the v2 audit pattern)
            if "schema" in m_def:
                ref = m_def["schema"]
                ref_def = (schema.get("methods") or {}).get(ref) or {}
                if isinstance(ref_def, dict):
                    m_def = {**ref_def, **{k: v for k, v in m_def.items() if k != "schema"}}

            m_type = m_def.get("type")
            kind = _TYPE_TO_KIND.get(m_type)
            if not kind:
                continue  # unknown type — skip

            out[method_name] = {
                "feature": feature,
                "type": m_type,
                "kind": kind,
                "protocols": set(supported_protocols),
                "primary_key": m_def.get("primary_key"),
                "defaults": m_def.get("defaults") or {},
                "sub_tables": m_def.get("sub_tables") or {},
            }

    return out


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Gather device state for one device (diagnostic mode)"
    )
    parser.add_argument("ip", help="Device IP")
    parser.add_argument("-u", default="admin")
    parser.add_argument("-p", default="private")
    parser.add_argument("--protocol", default="mops",
                        choices=["mops", "snmp", "ssh"])
    parser.add_argument("--label", default=None)
    args = parser.parse_args()

    state = gather_one_ip(args.ip, args.u, args.p, args.protocol, args.label)
    print(json.dumps(state, indent=2, default=str))
