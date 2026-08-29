#!/usr/bin/env python3
"""release_matrix.py — release-gate orchestrator for crude-engine.

Reads YAML inputs (schemas, device_pool, tag_map, exemptions) and produces
a single authoritative JSON output (release_matrix.json) describing the live
state of every (schema, method, protocol, device) cell.

See docs/RELEASE_GATE.md for the full design. This file implements:

  Component 4 — MatrixDB (write API for the central JSON, lock+backoff)
  Component 5 — worker function (one thread per device)
  Component 6 — orchestrator CLI
  Component 7 — doc renderer (RELEASE_MATRIX.md + TODO_HITLIST.md)

Phases 0.2 (gather) and 0.3 (plan generator) live below as well.

CLI surface (see docs/RELEASE_GATE.md § "CLI surface"):

    # Surgical (debug a single cell)
    release_matrix.py --method get_facts --protocol mops --device 192.168.1.4

    # Full pipeline
    release_matrix.py --gather                       # live read pass per device
    release_matrix.py --plan                         # generate test plan
    release_matrix.py --execute                      # run the plan
    release_matrix.py --render                       # regenerate docs
    release_matrix.py --gate                         # all four in one shot

    # Recovery
    release_matrix.py --resume --device 192.168.60.80
"""

from __future__ import annotations

import argparse
import functools
import concurrent.futures
import errno
import fcntl
import json
import os
import random
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any

try:
    from napalm import get_network_driver
except ImportError:
    get_network_driver = None

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
SCHEMAS_DIR = os.path.join(PROJECT, "crude_engine", "schemas")
WIRE_DIR = os.path.join(PROJECT, "crude_engine", "wire")

DEVICE_POOL_PATH = os.path.join(HERE, "device_pool.yaml")
TAG_MAP_PATH = os.path.join(HERE, "tag_map.yaml")
METHOD_EXEMPTIONS_PATH = os.path.join(HERE, "method_exemptions.yaml")
WIRE_EXEMPTIONS_PATH = os.path.join(HERE, "wire_exemptions.yaml")
INSPECT_YAML_PATH = os.path.join(HERE, "inspect.yaml")

MATRIX_PATH = os.path.join(HERE, "release_matrix.json")
PLAN_PATH = os.path.join(HERE, "release_test_plan.json")
DEVICE_STATE_PATH = os.path.join(HERE, "device_state.json")

DOCS_DIR = os.path.join(PROJECT, "docs")
RENDERED_MATRIX_PATH = os.path.join(DOCS_DIR, "RELEASE_MATRIX.md")
RENDERED_HITLIST_PATH = os.path.join(DOCS_DIR, "TODO_HITLIST.md")

# Make `tests/` importable so we can pull in the run_one_* callables.
sys.path.insert(0, HERE)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# =============================================================================
# Component 4 — MatrixDB
# =============================================================================
#
# Treat tests/release_matrix.json as a tiny database. Hierarchical keys mean
# cells never logically conflict: results[schema][method][protocol][device] is
# a unique address per worker job. The only conflict is two workers trying to
# rewrite the file at the same instant; fcntl.flock + random backoff handles
# that race.
#
# All writers go through MatrixDB.write_cell / .write_marker / .set_meta.
# Readers use MatrixDB.read() (returns a deep copy — caller can mutate freely).
# -----------------------------------------------------------------------------


class MatrixDBContention(RuntimeError):
    """Raised when MatrixDB cannot acquire the file lock after the retry budget."""


_EMPTY_DB = {
    "schema_version": 1,
    "generated_at": None,
    "engine_version": None,
    "scope": [],
    "results": {},
    "markers": [],
    "summary": {},
}


@contextmanager
def _flocked(path: str, timeout_ms: int = 100):
    """Acquire an exclusive flock on `path`. Creates the file if missing.

    Caller is responsible for the read-modify-write cycle; this only owns
    the lock. Raises BlockingIOError on timeout.
    """
    # Open in r+ so we can both read and write through the same fd. If the
    # file doesn't exist yet, create it with an empty DB body first.
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(_EMPTY_DB, f, indent=2)
    fd = open(path, "r+")
    deadline = time.monotonic() + timeout_ms / 1000
    try:
        while True:
            try:
                fcntl.flock(fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(0.005)
        yield fd
    finally:
        try:
            fcntl.flock(fd.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        fd.close()


class MatrixDB:
    """Lock-and-backoff writer for the central matrix JSON.

    Hierarchical addressing: results[schema][method][protocol][device].
    Each worker thread owns one device, so logical cell collisions are
    impossible. The lock only protects the literal disk write race.
    """

    def __init__(self, path: str = MATRIX_PATH,
                 max_attempts: int = 20,
                 backoff_min_ms: int = 50,
                 backoff_max_ms: int = 200):
        self.path = path
        self.max_attempts = max_attempts
        self.backoff_min_ms = backoff_min_ms
        self.backoff_max_ms = backoff_max_ms

    # ----- read -----

    def read(self) -> dict:
        """Return a fresh dict of the current DB state. Safe to mutate."""
        with _flocked(self.path, timeout_ms=500) as fd:
            fd.seek(0)
            try:
                data = json.load(fd)
            except json.JSONDecodeError:
                # File exists but is empty or corrupt — fall back to empty.
                data = json.loads(json.dumps(_EMPTY_DB))
        return data

    # ----- internal write helper -----

    def _modify(self, mutator) -> None:
        """Read-modify-write the JSON under flock with backoff retry.

        `mutator` is a function that takes the loaded dict and mutates it
        in place. The DB is rewritten on success. Raises MatrixDBContention
        if all retries are exhausted.
        """
        last_err: Exception | None = None
        for attempt in range(self.max_attempts):
            try:
                with _flocked(self.path, timeout_ms=100) as fd:
                    fd.seek(0)
                    raw = fd.read()
                    if raw.strip():
                        try:
                            data = json.loads(raw)
                        except json.JSONDecodeError:
                            data = json.loads(json.dumps(_EMPTY_DB))
                    else:
                        data = json.loads(json.dumps(_EMPTY_DB))
                    mutator(data)
                    fd.seek(0)
                    fd.truncate()
                    json.dump(data, fd, indent=2, sort_keys=False)
                    fd.flush()
                    os.fsync(fd.fileno())
                return
            except BlockingIOError as e:
                last_err = e
                backoff_ms = random.randint(self.backoff_min_ms,
                                            self.backoff_max_ms)
                time.sleep(backoff_ms / 1000)
        raise MatrixDBContention(
            f"could not acquire {self.path} after {self.max_attempts} attempts"
        ) from last_err

    # ----- write API -----

    def write_cell(self, schema: str, method: str, protocol: str,
                   device: str, cell: dict) -> None:
        """Write a single cell at results[schema][method][protocol][device].

        Stamps `ran_at` if not already present. Overwrites any prior cell at
        the same address (this is how surgical re-runs work).
        """
        if "ran_at" not in cell:
            cell = {**cell, "ran_at": _now_iso()}

        def mutate(data: dict) -> None:
            results = data.setdefault("results", {})
            schema_node = results.setdefault(schema, {})
            method_node = schema_node.setdefault(method, {})
            protocol_node = method_node.setdefault(protocol, {})
            protocol_node[device] = cell

        self._modify(mutate)

    def write_marker(self, type_: str, device: str, info: dict) -> None:
        """Append a marker (e.g., WORKER_STOPPED) to the markers list."""
        marker = {
            "type": type_,
            "device": device,
            "at": _now_iso(),
            **info,
        }

        def mutate(data: dict) -> None:
            data.setdefault("markers", []).append(marker)

        self._modify(mutate)

    def set_meta(self, **fields) -> None:
        """Set top-level metadata fields (generated_at, engine_version, scope, summary)."""

        def mutate(data: dict) -> None:
            for k, v in fields.items():
                data[k] = v

        self._modify(mutate)

    def get_cell(self, schema: str, method: str, protocol: str,
                 device: str) -> dict | None:
        """Read a single cell. Returns None if it doesn't exist."""
        data = self.read()
        try:
            return data["results"][schema][method][protocol][device]
        except KeyError:
            return None

    def reset(self) -> None:
        """Wipe the DB to an empty state. Used by --gather --plan --execute pipeline."""
        with _flocked(self.path, timeout_ms=500) as fd:
            fd.seek(0)
            fd.truncate()
            json.dump(_EMPTY_DB, fd, indent=2)


# =============================================================================
# Component 2 — Gather phase
# =============================================================================
#
# Wraps audit_common.gather_device for the whole device pool. Opens each
# device once (sequentially for v1; can parallelize later if needed),
# gathers state, writes tests/device_state.json.
#
# device_pool.yaml is the source of truth for which devices to gather.
# --device <ip> filters to one device.
# -----------------------------------------------------------------------------


def _load_device_pool() -> dict:
    """Load and validate tests/device_pool.yaml."""
    import yaml
    with open(DEVICE_POOL_PATH) as f:
        pool = yaml.safe_load(f) or {}
    # Validate vocabulary against schema directory
    schema_ids = {f[:-5] for f in os.listdir(SCHEMAS_DIR) if f.endswith(".yaml")}
    for dev in pool.get("devices", []):
        for key in ("has_capable", "has_configured"):
            for tag in dev.get(key, []) or []:
                if tag not in schema_ids:
                    raise ValueError(
                        f"device_pool.yaml: {dev['label']!r}.{key} has unknown "
                        f"tag {tag!r} (not a schema in crude_engine/schemas/)"
                    )
        if set(dev.get("has_configured", [])) - set(dev.get("has_capable", [])):
            extra = set(dev["has_configured"]) - set(dev["has_capable"])
            raise ValueError(
                f"device_pool.yaml: {dev['label']!r}.has_configured contains "
                f"tags not in has_capable: {sorted(extra)}"
            )
    return pool


def _filter_pool(pool: dict, device_ip: str | None = None) -> list[dict]:
    """Return the subset of devices matching --device filter (or all)."""
    devices = pool.get("devices", []) or []
    if device_ip:
        devices = [d for d in devices if d.get("ip") == device_ip]
        if not devices:
            raise ValueError(f"--device {device_ip} not found in device_pool.yaml")
    return devices


def run_gather(device_ip: str | None = None,
               protocol: str = "mops",
               username: str = "admin",
               password: str = "private") -> dict:
    """Gather phase entry point. Walks the device pool, populates device_state.

    Returns the full device_state dict that was written to disk.
    """
    from audit_common import gather_device

    pool = _load_device_pool()
    devices = _filter_pool(pool, device_ip)

    # Existing state may be present — load and merge so a single-device
    # gather doesn't wipe other devices' state.
    if os.path.exists(DEVICE_STATE_PATH) and not device_ip:
        existing: dict = {}  # full reset on a no-filter run
    elif os.path.exists(DEVICE_STATE_PATH):
        with open(DEVICE_STATE_PATH) as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                existing = {}
    else:
        existing = {}

    state = existing if isinstance(existing, dict) else {}
    state.setdefault("schema_version", 1)
    state.setdefault("devices", {})
    state["gathered_at"] = _now_iso()

    driver = get_network_driver("hios")

    for dev in devices:
        ip = dev["ip"]
        label = dev.get("label", ip)
        print(f"  gather {ip:18s} ({label})", end=" ", flush=True)
        try:
            d = driver(ip, username, password,
                       optional_args={"protocol": protocol})
            d.open()
        except Exception as e:
            print(f"CONNECT FAILED: {str(e)[:80]}")
            state["devices"][ip] = {
                "label": label,
                "errors": [{"phase": "connect", "error": str(e)[:200]}],
            }
            continue

        try:
            per_device = gather_device(d, label=label)
        except Exception as e:
            print(f"GATHER FAILED: {str(e)[:80]}")
            state["devices"][ip] = {
                "label": label,
                "errors": [{"phase": "gather", "error": str(e)[:200]}],
            }
            continue
        finally:
            try:
                d.close()
            except Exception:
                pass

        # Merge in pool metadata so the resolver can use it without re-loading
        per_device["sw_level"] = dev.get("sw_level")
        per_device["safe_for"] = dev.get("safe_for", [])
        per_device["has_capable"] = list(dev.get("has_capable", []))
        per_device["has_configured"] = list(dev.get("has_configured", []))

        state["devices"][ip] = per_device
        ports = per_device.get("ports") or {}
        ring = per_device.get("ring") or {}
        ring_str = "ring=yes" if ring.get("configured") else "ring=no"
        unused = per_device.get("unused_safe_to_touch") or []
        print(f"OK ports={len(ports.get('all', []))} {ring_str} "
              f"unused={len(unused)} errors={len(per_device.get('errors', []))}")

    with open(DEVICE_STATE_PATH, "w") as f:
        json.dump(state, f, indent=2, default=str)
    print(f"  wrote {DEVICE_STATE_PATH}")

    return state


# =============================================================================
# Component 3 — Plan generator + resolver
# =============================================================================
#
# Pure function: schemas + device_pool + device_state → release_test_plan.json
#
# For each (schema method, protocol-in-scope, eligible-device), emit a job.
#
# Read jobs go to ALL eligible devices (parity testing — same getter on
# multiple devices to compare results).
#
# Setter and CRUD jobs go to ONE eligible device per protocol (best match:
# sacrificial > crud > setter > read). Running setters on multiple devices
# is more disruptive than reads; v1 settles for "works on at least one
# matching device per protocol." Multi-device-per-sw-level is a v2 enhancement.
#
# Resolver rules (mechanical from method `kind` + device pool):
#   read       → feature ∈ device.has_configured
#   setter     → feature ∈ device.has_configured AND 'setter' ∈ device.safe_for
#   crud_create→ feature ∈ device.has_capable AND 'crud' ∈ device.safe_for
#                (test_crud_pairs handles its own state lifecycle)
#   crud_delete→ feature ∈ device.has_capable AND 'crud' ∈ device.safe_for
# -----------------------------------------------------------------------------


def _is_configured(result, schema_meta: dict) -> bool:
    """Determine if a read result represents configured (non-default) state.

    Uses schema STRUCTURE — not value comparison against defaults — to
    decide. Three shapes:

      Sub-tabled schemas    (e.g. mrp_sub_ring with sub_tables: {instances: ...})
        → configured iff any sub_table dict has at least one row
        → ignores the always-present `globals` wrapper

      Primary-key tables    (e.g. get_lldp_neighbors with primary_key: local_port)
        → configured iff the top-level dict has at least one row

      Flat global dicts     (e.g. get_banner — no primary_key, no sub_tables)
        → configured iff non-empty (imperfect — can't distinguish factory
          defaults from user values without a baseline; per-schema overrides
          can refine later)

    Schema defaults are intentionally NOT used here — schema defaults
    describe the contract shape for type validation, not the device's
    factory state.
    """
    if result is None:
        return False
    if not isinstance(result, dict):
        if isinstance(result, list):
            return len(result) > 0
        if isinstance(result, str):
            return result != ""
        return bool(result)

    # 1. Sub-tabled schema → check the sub-tables, ignore the globals wrapper
    sub_tables = schema_meta.get("sub_tables") or {}
    if sub_tables:
        for st_name in sub_tables:
            st_data = result.get(st_name)
            if isinstance(st_data, (dict, list)) and len(st_data) > 0:
                return True
        return False

    # 2. Primary-key table → top-level dict IS the rows
    if schema_meta.get("primary_key"):
        return len(result) > 0

    # 3. Flat global dict → fall back to "non-empty" (imperfect)
    return len(result) > 0


def derive_has_configured_from_matrix() -> dict:
    """Walk release_matrix.json, derive `has_configured_from_gather` per device.

    For each device, a feature is "configured" if ANY read cell for a method
    belonging to that feature returned `empty=False`. The matrix tool
    already captures this flag at read time. This function is the
    derivation step that turns that signal into a pool-equivalent list.

    Writes the derived lists into `tests/device_state.json` under
    `devices.<ip>.has_configured_from_gather`. Called automatically after
    any run_execute() that ran read jobs; can also be invoked standalone.

    Returns the updated device_state dict.
    """
    db = MatrixDB().read()
    device_state: dict = {"devices": {}}
    if os.path.exists(DEVICE_STATE_PATH):
        with open(DEVICE_STATE_PATH) as f:
            try:
                device_state = json.load(f)
            except json.JSONDecodeError:
                pass
    device_state.setdefault("devices", {})

    # Group: device_ip -> set of feature ids with non-empty read data
    configured: dict[str, set[str]] = {}
    for schema, methods in (db.get("results") or {}).items():
        for method_name, protocols in methods.items():
            for proto, devices_dict in protocols.items():
                for device_ip, cell in devices_dict.items():
                    if cell.get("kind") != "read":
                        continue
                    if cell.get("verdict") != "pass":
                        continue
                    if cell.get("empty", True):
                        continue
                    configured.setdefault(device_ip, set()).add(schema)

    # Merge into device_state (union with any existing derivation)
    for ip, features in configured.items():
        dev = device_state["devices"].setdefault(ip, {})
        existing = set(dev.get("has_configured_from_gather") or [])
        dev["has_configured_from_gather"] = sorted(existing | features)

    with open(DEVICE_STATE_PATH, "w") as f:
        json.dump(device_state, f, indent=2, default=str)

    return device_state


_SAFETY_RANK = {"sacrificial": 4, "crud": 3, "setter": 2, "read": 1}


def _device_safety_score(dev: dict) -> int:
    """Higher score = more sacrificial. Used as TIEBREAKER when multiple
    devices of the same sw_level are eligible for a setter/crud job."""
    return max((_SAFETY_RANK.get(s, 0) for s in dev.get("safe_for", [])), default=0)


def _pick_one_per_sw_level(eligible_devices: list[dict]) -> dict[str, dict]:
    """Group devices by sw_level, return {sw_level: chosen_device}.

    Setter/CRUD coverage axis: ONE representative per device class
    (L2S, L2A, L3A, ...) per protocol per test. Multiple devices of the
    same class are redundant for setter testing — we pick the most
    sacrificial as the representative for that class.
    """
    by_level: dict[str, dict] = {}
    for dev in eligible_devices:
        level = dev.get("sw_level") or "unknown"
        if level not in by_level:
            by_level[level] = dev
        else:
            if _device_safety_score(dev) > _device_safety_score(by_level[level]):
                by_level[level] = dev
    return by_level


def _device_matches(dev: dict, feature: str, kind: str,
                    state_for_device: dict | None = None) -> tuple[bool, str | None]:
    """Resolver: does this device satisfy the requirement for this feature+kind?

    `state_for_device` is the entry from device_state.json for this device.
    If present, its `has_configured_from_gather` field is union'd with the
    pool's has_configured — gather-derived data is the source of truth.

    Resolver rules:
      read       → feature ∈ has_capable           (cheap, vacuous-ok)
      setter     → feature ∈ has_configured ∪ gather-derived
      crud       → feature ∈ has_capable           (test handles state)

    The "read uses has_capable" relaxation lets reads run on every device
    that supports the feature, even if no data is configured yet. Vacuous
    passes are accepted because the contract checks still fire on whatever
    the method returns. The gather-derived has_configured then feeds the
    setter/crud resolver with TRUE state of each device.

    Returns (matches, reason_if_not).
    """
    has_cap = set(dev.get("has_capable") or [])
    has_cfg = set(dev.get("has_configured") or [])
    safe_for = set(dev.get("safe_for") or [])

    if state_for_device:
        has_cfg = has_cfg | set(state_for_device.get("has_configured_from_gather") or [])

    if kind == "read":
        if "read" not in safe_for:
            return False, "read not in safe_for"
        if feature not in has_cap:
            return False, f"{feature} not in has_capable"
        return True, None

    if kind == "setter":
        if "setter" not in safe_for:
            return False, "setter not in safe_for"
        if feature not in has_cfg:
            return False, f"{feature} not configured (pool ∪ gather)"
        return True, None

    if kind in ("crud_create", "crud_delete"):
        if "crud" not in safe_for:
            return False, "crud not in safe_for"
        if feature not in has_cap:
            return False, f"{feature} not in has_capable"
        return True, None

    return False, f"unknown kind {kind!r}"


def _load_setter_tests() -> dict:
    """Import test_setter_pairs.TESTS without triggering its CLI."""
    import test_setter_pairs
    return dict(test_setter_pairs.TESTS)


def _load_crud_tests() -> dict:
    """Import test_crud_pairs.TESTS without triggering its CLI."""
    import test_crud_pairs
    return dict(test_crud_pairs.TESTS)


def generate_plan(scope: list[str],
                  device_filter: str | None = None,
                  method_filter: str | None = None,
                  schema_filter: str | None = None,
                  protocol_filter: str | None = None) -> dict:
    """Generate the test plan. Pure function — no device I/O.

    Inputs: schemas (loaded from disk), device_pool (loaded from disk),
            device_state (loaded from disk if present).
    Output: dict matching the release_test_plan.json contract.
    """
    from audit_common import load_all_method_metadata

    method_meta = load_all_method_metadata()
    pool = _load_device_pool()
    devices = _filter_pool(pool, device_filter)

    # device_state is optional at plan time — methods that need it (per-port
    # via unused_safe_to_touch, safety protocols via ring_port_secondary)
    # will get a not_applicable verdict if state is missing.
    device_state: dict = {}
    if os.path.exists(DEVICE_STATE_PATH):
        with open(DEVICE_STATE_PATH) as f:
            try:
                device_state = json.load(f)
            except json.JSONDecodeError:
                device_state = {}
    state_devices: dict = device_state.get("devices") or {}

    setter_tests = _load_setter_tests()
    crud_tests = _load_crud_tests()

    jobs: list[dict] = []

    # -----------------------------------------------------------------
    # READ jobs — emit on every matching device
    # -----------------------------------------------------------------
    for method_name, meta in sorted(method_meta.items()):
        if meta["kind"] != "read":
            continue
        if method_filter and method_name != method_filter:
            continue
        if schema_filter and meta["feature"] != schema_filter:
            continue

        for proto in sorted(meta["protocols"]):
            if proto not in scope:
                continue
            if protocol_filter and proto != protocol_filter:
                continue

            for dev in devices:
                ok, reason = _device_matches(dev, meta["feature"], "read",
                                             state_for_device=state_devices.get(dev["ip"]))
                if not ok:
                    jobs.append({
                        "job_id": f"{method_name}__{proto}__{dev['ip']}",
                        "kind": "read",
                        "schema": meta["feature"],
                        "method": method_name,
                        "protocol": proto,
                        "device": dev["ip"],
                        "verdict_at_plan_time": "not_applicable",
                        "reason": reason,
                    })
                    continue
                jobs.append({
                    "job_id": f"{method_name}__{proto}__{dev['ip']}",
                    "kind": "read",
                    "schema": meta["feature"],
                    "method": method_name,
                    "protocol": proto,
                    "device": dev["ip"],
                })

    # -----------------------------------------------------------------
    # SETTER jobs — ONE device per (sw_level, protocol) per test
    #
    # Coverage axis: every test must run on every sw_level (L2S, L2A,
    # L3A, ...) for every in-scope protocol. Multiple devices of the
    # same sw_level are redundant — pick the most sacrificial as the
    # representative for that class.
    # -----------------------------------------------------------------
    for test_id, spec in sorted(setter_tests.items()):
        set_method = spec.get("set")
        if not set_method or set_method not in method_meta:
            continue  # setter test points at a method we don't know about
        meta = method_meta[set_method]
        if method_filter and set_method != method_filter:
            continue
        if schema_filter and meta["feature"] != schema_filter:
            continue

        for proto in sorted(meta["protocols"]):
            if proto not in scope:
                continue
            if protocol_filter and proto != protocol_filter:
                continue

            # Find all eligible devices
            eligible = []
            for dev in devices:
                ok, _ = _device_matches(dev, meta["feature"], "setter",
                                        state_for_device=state_devices.get(dev["ip"]))
                if ok:
                    req_level = spec.get("requires")
                    if req_level and not _level_includes(dev.get("sw_level"), req_level):
                        continue
                    eligible.append(dev)

            if not eligible:
                jobs.append({
                    "job_id": f"setter__{test_id}__{proto}",
                    "kind": "setter",
                    "schema": meta["feature"],
                    "method": set_method,
                    "test_id": test_id,
                    "protocol": proto,
                    "device": None,
                    "verdict_at_plan_time": "not_applicable",
                    "reason": "no device matches setter requirements",
                })
                continue

            # ONE device per sw_level
            for sw_level, chosen in _pick_one_per_sw_level(eligible).items():
                jobs.append({
                    "job_id": f"setter__{test_id}__{proto}__{chosen['ip']}",
                    "kind": "setter",
                    "schema": meta["feature"],
                    "method": set_method,
                    "test_id": test_id,
                    "protocol": proto,
                    "device": chosen["ip"],
                    "sw_level": sw_level,
                })

    # -----------------------------------------------------------------
    # CRUD jobs — ONE device per (sw_level, protocol) per test
    # (full lifecycle: create → get → set → get → delete → get)
    # -----------------------------------------------------------------
    for test_id, spec in sorted(crud_tests.items()):
        create_pair = spec.get("create")
        if not create_pair or not isinstance(create_pair, tuple):
            continue
        create_method = create_pair[0]
        if create_method not in method_meta:
            continue
        meta = method_meta[create_method]
        if method_filter and create_method != method_filter:
            continue
        if schema_filter and meta["feature"] != schema_filter:
            continue

        for proto in sorted(meta["protocols"]):
            if proto not in scope:
                continue
            if protocol_filter and proto != protocol_filter:
                continue

            eligible = []
            for dev in devices:
                ok, _ = _device_matches(dev, meta["feature"], "crud_create",
                                        state_for_device=state_devices.get(dev["ip"]))
                if ok:
                    eligible.append(dev)

            if not eligible:
                jobs.append({
                    "job_id": f"crud__{test_id}__{proto}",
                    "kind": "crud",
                    "schema": meta["feature"],
                    "method": create_method,
                    "test_id": test_id,
                    "protocol": proto,
                    "device": None,
                    "verdict_at_plan_time": "not_applicable",
                    "reason": "no device matches crud requirements",
                })
                continue

            # ONE device per sw_level
            for sw_level, chosen in _pick_one_per_sw_level(eligible).items():
                jobs.append({
                    "job_id": f"crud__{test_id}__{proto}__{chosen['ip']}",
                    "kind": "crud",
                    "schema": meta["feature"],
                    "method": create_method,
                    "test_id": test_id,
                    "protocol": proto,
                    "device": chosen["ip"],
                    "sw_level": sw_level,
                })

    # -----------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------
    by_kind = {"read": 0, "setter": 0, "crud": 0, "execute": 0}
    by_device: dict[str, int] = {}
    not_applicable_count = 0
    for j in jobs:
        by_kind[j["kind"]] = by_kind.get(j["kind"], 0) + 1
        if j.get("device"):
            by_device[j["device"]] = by_device.get(j["device"], 0) + 1
        if j.get("verdict_at_plan_time") == "not_applicable":
            not_applicable_count += 1

    plan = {
        "schema_version": 1,
        "generated_at": _now_iso(),
        "scope": list(scope),
        "device_filter": device_filter,
        "method_filter": method_filter,
        "schema_filter": schema_filter,
        "protocol_filter": protocol_filter,
        "jobs": jobs,
        "summary": {
            "total_jobs": len(jobs),
            "by_kind": by_kind,
            "by_device": by_device,
            "not_applicable_at_plan_time": not_applicable_count,
        },
    }
    return plan


_SW_LEVELS = ["L2S", "L2E", "L2A", "L3S", "L3A_UR", "L3A_MR", "L3A"]


def _level_includes(device_level: str | None, required: str) -> bool:
    """Mirror test_setter_pairs.level_includes — does device level meet requirement?"""
    if not required or not device_level:
        return True
    try:
        return _SW_LEVELS.index(device_level) >= _SW_LEVELS.index(required)
    except ValueError:
        return True  # unknown level — try anyway


def run_plan(scope: list[str],
             device_filter: str | None = None,
             method_filter: str | None = None,
             schema_filter: str | None = None,
             protocol_filter: str | None = None) -> dict:
    """Generate the test plan and write it to disk."""
    plan = generate_plan(scope, device_filter, method_filter, schema_filter,
                         protocol_filter)
    with open(PLAN_PATH, "w") as f:
        json.dump(plan, f, indent=2, default=str)
    s = plan["summary"]
    print(f"  plan: {s['total_jobs']} jobs total")
    print(f"        by_kind: {s['by_kind']}")
    print(f"        by_device: {s['by_device']}")
    print(f"        not_applicable_at_plan_time: {s['not_applicable_at_plan_time']}")
    print(f"  wrote {PLAN_PATH}")
    return plan


# =============================================================================
# Component 5 — Worker function
# =============================================================================
#
# One worker per device. Opens the device once, dispatches all assigned
# jobs in order, writes each result to the MatrixDB. Catches transport
# exceptions (sockets, timeouts) as comms-loss → writes a marker → exits.
#
# The worker is a plain function — no class — so it's trivial to call
# from a thread pool, a subprocess, or interactively for debugging.
# -----------------------------------------------------------------------------


# Exceptions that indicate the device is unreachable, not a logic bug.
_COMMS_LOST_TYPES = (
    ConnectionError,
    BrokenPipeError,
    OSError,        # broad — includes socket.error, timeouts on some stacks
    TimeoutError,
)


def _is_comms_lost(exc: Exception) -> bool:
    """Heuristic: does this exception look like 'device went away'?"""
    if isinstance(exc, _COMMS_LOST_TYPES):
        return True
    # napalm/SSH/HTTPS layers wrap underlying socket errors. Inspect message.
    msg = str(exc).lower()
    needles = ("connection refused", "connection reset", "timed out",
               "no route to host", "host unreachable", "broken pipe",
               "ssh session not active", "remote end closed")
    return any(n in msg for n in needles)


def _dispatch_job(job: dict, device, device_state: dict, schemas_meta: dict,
                  setter_tests: dict, crud_tests: dict) -> dict:
    """Run a single job against an already-open device. Returns a cell dict.

    May raise — comms-loss is caught at the worker level so it can write
    a WORKER_STOPPED marker. Logic exceptions are converted to error cells.
    """
    from audit_getters_v2 import run_one_read
    from test_setter_pairs import run_one_setter
    from test_crud_pairs import run_one_crud
    from safety_runner import default_runner, SafetyPrerequisiteMissing, SafetyError

    kind = job["kind"]
    method = job["method"]
    schema = job["schema"]

    if kind == "read":
        meta = schemas_meta.get(method)
        if not meta:
            return {"verdict": "error", "kind": kind, "method": method,
                    "evidence": {"error": f"unknown method {method!r}"}}
        # audit_getters_v2.run_one_read needs the schema dict in its
        # original v2 shape (defaults, type, primary_key, sub_tables,
        # feature, protocols). load_all_method_metadata produces a
        # superset, so we can pass it directly.
        cell = run_one_read(device, method, meta)
        # run_one_read returns its own status field; map to verdict
        cell["verdict"] = (
            "pass" if cell.get("status") == "ok" else
            "fail" if cell.get("status") == "fail" else
            "error"
        )
        cell["kind"] = kind
        # Capture configured-state signal for has_configured_from_gather
        # derivation. Uses schema structure (sub_tables, primary_key) to
        # decide what "configured" means for this method's shape.
        raw = cell.get("result")
        cell["empty"] = not _is_configured(raw, meta)
        # Stash raw result on the cell as `_raw_result` for the worker's
        # parity collector. The worker pops it before writing to the DB
        # so the result blob never lands in matrix_db.json.
        cell["_raw_result"] = raw
        cell.pop("result", None)
        return cell

    if kind == "setter":
        test_id = job["test_id"]
        spec = setter_tests.get(test_id)
        if not spec:
            return {"verdict": "error", "kind": kind, "method": method,
                    "evidence": {"error": f"unknown setter test_id {test_id!r}"}}

        runner = default_runner()
        try:
            cell = runner.run_with_safety(
                device, method,
                lambda: run_one_setter(device, test_id, spec),
                device_state=device_state,
            )
        except SafetyPrerequisiteMissing as e:
            return {"verdict": "not_applicable", "kind": kind, "method": method,
                    "test_id": test_id,
                    "reason": f"safety prerequisite missing: {e}"}
        except SafetyError as e:
            return {"verdict": "error", "kind": kind, "method": method,
                    "test_id": test_id,
                    "evidence": {"error": f"safety: {e}"}}
        cell["verdict"] = (
            "pass" if cell.get("status") == "ok" else
            "fail" if cell.get("status") == "fail" else
            "error"
        )
        cell["kind"] = kind
        return cell

    if kind == "crud":
        test_id = job["test_id"]
        spec = crud_tests.get(test_id)
        if not spec:
            return {"verdict": "error", "kind": kind, "method": method,
                    "evidence": {"error": f"unknown crud test_id {test_id!r}"}}

        runner = default_runner()
        try:
            cell = runner.run_with_safety(
                device, method,
                lambda: run_one_crud(device, test_id, spec),
                device_state=device_state,
            )
        except SafetyPrerequisiteMissing as e:
            return {"verdict": "not_applicable", "kind": kind, "method": method,
                    "test_id": test_id,
                    "reason": f"safety prerequisite missing: {e}"}
        except SafetyError as e:
            return {"verdict": "error", "kind": kind, "method": method,
                    "test_id": test_id,
                    "evidence": {"error": f"safety: {e}"}}
        cell["verdict"] = (
            "pass" if cell.get("status") == "ok" else
            "fail" if cell.get("status") == "fail" else
            "error"
        )
        cell["kind"] = kind
        return cell

    return {"verdict": "error", "kind": kind,
            "evidence": {"error": f"unknown job kind {kind!r}"}}


# Fields excluded from parity value comparison — they legitimately change
# between calls or depend on when the read was done.
_PARITY_TIMING_FIELDS = {
    "uptime", "age", "last_flapped", "last_move", "when", "timestamp",
    "utilization", "tx_octets", "rx_octets", "tx_errors", "rx_errors",
    "tx_discards", "rx_discards", "tx_unicast_packets", "rx_unicast_packets",
    "tx_multicast_packets", "rx_multicast_packets",
    "tx_broadcast_packets", "rx_broadcast_packets",
    "fragments", "crc_errors", "collisions", "late_collisions",
    "checksum_errors", "version_errors", "vrid_errors",
    "humidity", "temperature", "cpu", "memory",
    # Real-time analog measurements (SFP optics) — fluctuate per read
    "rx_power", "tx_power", "tx_bias", "voltage",
}


_MAX_DIFFS_PER_PAIR = 25  # cap output to keep cells small


def _values_equal(a, b) -> bool:
    """Tolerant equality — handles type coercion that's safe across protocols.

    True == 1, False == 0, "1" == 1, "True" == True (case-insensitive).
    None never equals anything except None.
    Empty string and None are NOT equal — protocols may legitimately differ
    on whether an empty field is "" or null.
    """
    if a == b:
        return True
    if a is None or b is None:
        return False
    # Numeric/bool coercion
    try:
        if isinstance(a, (int, float, bool)) and isinstance(b, (int, float, bool)):
            return float(a) == float(b)
        if isinstance(a, str) and isinstance(b, (int, float, bool)):
            return float(a) == float(b)
        if isinstance(b, str) and isinstance(a, (int, float, bool)):
            return float(b) == float(a)
    except (ValueError, TypeError):
        pass
    # String case-insensitive (only safe for boolean-ish values)
    if isinstance(a, str) and isinstance(b, str):
        if a.lower() == b.lower():
            return True
    return False


def _compare_nested(diffs: list, pa: str, pb: str, va, vb, default_val,
                    path: str) -> None:
    """Compare a row-level dict/list that is not a named sub_table."""
    if isinstance(default_val, dict):
        da = va if isinstance(va, dict) else {}
        db = vb if isinstance(vb, dict) else {}
        if da == db:
            return
        if len(da) != len(db):
            diffs.append(f"{path}: {pa} keys={len(da)} vs {pb} keys={len(db)}")
            return
        diffs.append(
            f"{path}: {pa}={repr(da)[:40]} vs {pb}={repr(db)[:40]}"
        )
        return
    if isinstance(default_val, list):
        la = va if isinstance(va, list) else []
        lb = vb if isinstance(vb, list) else []
        if la == lb:
            return
        if len(la) != len(lb):
            diffs.append(f"{path}: {pa} len={len(la)} vs {pb} len={len(lb)}")
            return
        diffs.append(
            f"{path}: {pa}={repr(la)[:40]} vs {pb}={repr(lb)[:40]}"
        )


def _compare_flat(diffs: list, pa: str, pb: str, a: dict, b: dict,
                  defaults: dict, path: str = "",
                  skip_nested: set | None = None) -> None:
    """Compare two dicts field-by-field. Adds diffs in place. Caps at MAX.

    Named sub_tables (skip_nested) are walked by the caller. Other dict/list
    defaults are row-level nested fields and must compare (issue #89).
    """
    skip_nested = skip_nested or set()
    if len(diffs) >= _MAX_DIFFS_PER_PAIR:
        return
    for field in defaults:
        if len(diffs) >= _MAX_DIFFS_PER_PAIR:
            diffs.append(f"{path}... (truncated)")
            return
        if field in _PARITY_TIMING_FIELDS:
            continue
        default_val = defaults[field]
        if isinstance(default_val, (dict, list)):
            if field in skip_nested:
                continue
            _compare_nested(
                diffs, pa, pb, a.get(field), b.get(field), default_val,
                path=f"{path}{field}",
            )
            continue
        va = a.get(field)
        vb = b.get(field)
        if _values_equal(va, vb):
            continue
        # Treat None vs missing-key as equal (one protocol omits, default fills)
        if va is None or vb is None:
            continue
        diffs.append(
            f"{path}{field}: {pa}={repr(va)[:40]} vs {pb}={repr(vb)[:40]}"
        )


def _compare_table(diffs: list, pa: str, pb: str,
                   table_a: dict, table_b: dict,
                   defaults: dict, path: str = "",
                   skip_nested: set | None = None) -> None:
    """Compare two table dicts (keyed by row identity) row-by-row.

    Reports row keys present in one but not the other, then for common
    rows compares each field via _compare_flat.
    """
    if not isinstance(table_a, dict) or not isinstance(table_b, dict):
        if table_a != table_b:
            diffs.append(f"{path}type/value mismatch: "
                         f"{pa}={type(table_a).__name__} vs {pb}={type(table_b).__name__}")
        return

    keys_a = set(table_a.keys())
    keys_b = set(table_b.keys())

    # Row count diff (always informative)
    if len(keys_a) != len(keys_b):
        diffs.append(f"{path}row count: {pa}={len(keys_a)} vs {pb}={len(keys_b)}")

    # Keys in one protocol only — only show if both protocols had SOME data
    # (if one is totally empty the count diff above already says it)
    only_a = keys_a - keys_b
    only_b = keys_b - keys_a
    if keys_a and keys_b:
        if only_a:
            diffs.append(f"{path}{pa}-only rows: {sorted(str(k) for k in only_a)[:5]}")
        if only_b:
            diffs.append(f"{path}{pb}-only rows: {sorted(str(k) for k in only_b)[:5]}")

    # Compare common rows field-by-field
    common = keys_a & keys_b
    for row_key in sorted(common, key=str):
        if len(diffs) >= _MAX_DIFFS_PER_PAIR:
            diffs.append(f"{path}... (truncated, {len(common)} common rows)")
            return
        row_a = table_a[row_key]
        row_b = table_b[row_key]
        if isinstance(row_a, dict) and isinstance(row_b, dict):
            _compare_flat(diffs, pa, pb, row_a, row_b, defaults,
                          path=f"{path}[{row_key}].",
                          skip_nested=skip_nested)
        elif row_a != row_b:
            diffs.append(f"{path}[{row_key}]: {pa}={repr(row_a)[:40]} "
                         f"vs {pb}={repr(row_b)[:40]}")


def _compute_parity(method_name: str, schema_meta: dict,
                    results_by_proto: dict) -> list[str]:
    """Compare read results across protocols for one method.

    Real cross-protocol value parity — not just row-count comparison.
    Recursively descends into named sub_tables. Compares every non-timing
    scalar field, plus row-level dict/list fields that are not named
    sub_tables (issue #89).

    Returns a list of diff strings. Empty list = parity OK.
    """
    diffs: list[str] = []
    protos = list(results_by_proto.keys())
    if len(protos) < 2:
        return diffs

    defaults = schema_meta.get("defaults") or {}
    pk = schema_meta.get("primary_key")
    sub_tables = schema_meta.get("sub_tables") or {}

    for i, pa in enumerate(protos):
        for pb in protos[i + 1:]:
            a = results_by_proto.get(pa)
            b = results_by_proto.get(pb)

            if not isinstance(a, dict) or not isinstance(b, dict):
                if a != b:
                    diffs.append(f"{pa} vs {pb}: type mismatch "
                                 f"({type(a).__name__} vs {type(b).__name__})")
                continue

            skip_nested = set(sub_tables)
            if pk:
                # Top-level dict IS a table keyed by row identity
                _compare_table(diffs, pa, pb, a, b, defaults,
                               skip_nested=skip_nested)
            elif sub_tables:
                # Flat globals + named sub_tables
                _compare_flat(diffs, pa, pb, a, b, defaults,
                              skip_nested=skip_nested)
                for st_name, st_def in sub_tables.items():
                    sa = a.get(st_name)
                    sb = b.get(st_name)
                    st_defaults = st_def.get("defaults") or {}
                    if isinstance(sa, dict) and isinstance(sb, dict):
                        _compare_table(diffs, pa, pb, sa, sb, st_defaults,
                                       path=f"{st_name}.")
                    elif sa != sb:
                        diffs.append(f"{st_name}: {pa}={type(sa).__name__} "
                                     f"vs {pb}={type(sb).__name__}")
            else:
                # Pure flat dict (nested row fields still compare)
                _compare_flat(diffs, pa, pb, a, b, defaults,
                              skip_nested=skip_nested)

            if len(diffs) >= _MAX_DIFFS_PER_PAIR:
                break
        if len(diffs) >= _MAX_DIFFS_PER_PAIR:
            break

    return diffs


def _cell_key_for_job(job: dict) -> str:
    """Return the second-level key for the cell address.

    Multiple setter/crud tests can share the same canonical method
    (banner_text and banner_enabled both call set_banner), so for those
    kinds we use the test_id to keep cells uniquely addressable. Reads
    are 1:1 with methods so we use the method name directly.
    """
    if job.get("test_id"):
        return job["test_id"]
    return job["method"]


def run_worker(device_ip: str, jobs: list[dict], matrix_db: MatrixDB,
               device_state: dict, schemas_meta: dict,
               setter_tests: dict, crud_tests: dict,
               username: str = "admin", password: str = "private") -> dict:
    """One worker, one device. Owns the device for its lifetime.

    Walks through `jobs` (already filtered to this device), dispatches each,
    writes the resulting cell to matrix_db. On comms-loss: writes a
    WORKER_STOPPED marker, returns immediately, leaves remaining jobs as
    `not_run` (they'll be picked up in the gate verdict pass).

    Returns a summary dict for orchestrator logging.
    """

    # Group jobs by protocol — we can only have one open device per
    # protocol at a time. Open per-protocol within the same worker.
    by_proto: dict[str, list[dict]] = {}
    for j in jobs:
        if j.get("verdict_at_plan_time") == "not_applicable":
            # Already classified, just write it through
            matrix_db.write_cell(j["schema"], _cell_key_for_job(j), j["protocol"],
                                 device_ip,
                                 {"verdict": "not_applicable",
                                  "kind": j["kind"],
                                  "method": j["method"],
                                  "reason": j.get("reason"),
                                  "test_id": j.get("test_id")})
            continue
        by_proto.setdefault(j["protocol"], []).append(j)

    summary = {"device": device_ip, "ran": 0, "passed": 0, "failed": 0,
               "errored": 0, "na": 0, "comms_lost": False, "parity_diffs": 0}

    # Collect raw read results across protocols for cross-protocol parity.
    # Key: (schema, method) -> {protocol: raw_result}
    parity_collector: dict[tuple, dict] = {}

    driver = get_network_driver("hios")

    for proto in sorted(by_proto.keys()):
        proto_jobs = by_proto[proto]
        device = None
        try:
            device = driver(device_ip, username, password,
                            optional_args={"protocol": proto})
            device.open()
        except Exception as e:
            # Connection failed entirely — every job becomes error
            for j in proto_jobs:
                cell = {"verdict": "error", "kind": j["kind"], "method": j["method"],
                        "evidence": {"error": f"connect: {str(e)[:200]}"}}
                if j.get("test_id"):
                    cell["test_id"] = j["test_id"]
                matrix_db.write_cell(j["schema"], _cell_key_for_job(j),
                                     j["protocol"], device_ip, cell)
                summary["errored"] += 1
                summary["ran"] += 1
            if _is_comms_lost(e):
                matrix_db.write_marker("WORKER_STOPPED", device_ip,
                    {"phase": "connect", "protocol": proto,
                     "error": str(e)[:200],
                     "remaining_jobs": len(proto_jobs)})
                summary["comms_lost"] = True
                return summary
            continue

        try:
            for idx, job in enumerate(proto_jobs):
                try:
                    cell = _dispatch_job(job, device, device_state,
                                         schemas_meta, setter_tests, crud_tests)
                except Exception as e:
                    if _is_comms_lost(e):
                        # Mark current cell, leave the rest for resume
                        matrix_db.write_cell(
                            job["schema"], _cell_key_for_job(job),
                            job["protocol"], device_ip,
                            {"verdict": "comms_lost", "kind": job["kind"],
                             "method": job["method"],
                             "test_id": job.get("test_id"),
                             "evidence": {"error": str(e)[:200]}})
                        matrix_db.write_marker("WORKER_STOPPED", device_ip,
                            {"phase": "execute", "protocol": proto,
                             "after_job": job["job_id"],
                             "error": str(e)[:200],
                             "remaining_jobs": len(proto_jobs) - idx - 1})
                        summary["comms_lost"] = True
                        return summary
                    # Logic error, not comms — write as error cell, continue
                    cell = {"verdict": "error", "kind": job["kind"],
                            "method": job["method"],
                            "test_id": job.get("test_id"),
                            "evidence": {"error": f"dispatch: {str(e)[:200]}"}}

                # Stash raw result for cross-protocol parity check, then
                # strip it from the cell before persisting.
                raw_result = cell.pop("_raw_result", None)
                if (cell.get("kind") == "read" and cell.get("verdict") == "pass"
                        and raw_result is not None):
                    key = (job["schema"], job["method"])
                    parity_collector.setdefault(key, {})[proto] = raw_result

                # Persist the cell and update summary
                matrix_db.write_cell(job["schema"], _cell_key_for_job(job),
                                     job["protocol"], device_ip, cell)
                summary["ran"] += 1
                v = cell.get("verdict")
                if v == "pass":
                    summary["passed"] += 1
                elif v == "fail":
                    summary["failed"] += 1
                elif v == "not_applicable":
                    summary["na"] += 1
                else:
                    summary["errored"] += 1
        finally:
            try:
                device.close()
            except Exception:
                pass

    # -----------------------------------------------------------------
    # Cross-protocol parity — AFTER all protocols for this device ran.
    # For each (schema, method) that returned data on at least 2
    # protocols, compare results and write a parity cell.
    # -----------------------------------------------------------------
    for (schema, method_name), proto_results in parity_collector.items():
        if len(proto_results) < 2:
            continue  # need at least two protocols to compare
        meta = schemas_meta.get(method_name) or {}
        diffs = _compute_parity(method_name, meta, proto_results)
        parity_cell = {
            "kind": "parity",
            "method": method_name,
            "verdict": "pass" if not diffs else "fail",
            "compared_protocols": sorted(proto_results.keys()),
            "diffs": diffs,
            "ran_at": _now_iso(),
        }
        # Parity cell address: protocol slot holds the literal "parity",
        # distinct from any real protocol. The worker writes one parity
        # cell per method per device.
        matrix_db.write_cell(schema, method_name, "parity", device_ip, parity_cell)
        if diffs:
            summary["parity_diffs"] += 1

    return summary


# =============================================================================
# Component 6 — Orchestrator
# =============================================================================
#
# Wires everything together. Reads the plan, groups jobs by device, spins
# up a thread per device, calls run_worker for each, collects summaries.
# -----------------------------------------------------------------------------


def run_execute(scope: list[str],
                device_filter: str | None = None,
                method_filter: str | None = None,
                schema_filter: str | None = None,
                protocol_filter: str | None = None,
                kind_filter: str | None = None,
                username: str = "admin",
                password: str = "private") -> dict:
    """Execute the plan. One worker thread per device with assigned jobs.

    Loads the existing plan from disk. To regenerate first, the caller
    runs --plan or --gate explicitly.
    """
    import concurrent.futures as cf
    from audit_common import load_all_method_metadata

    if not os.path.exists(PLAN_PATH):
        raise FileNotFoundError(
            f"{PLAN_PATH} missing — run --plan or --gate first"
        )
    with open(PLAN_PATH) as f:
        plan = json.load(f)

    schemas_meta = load_all_method_metadata()
    setter_tests = _load_setter_tests()
    crud_tests = _load_crud_tests()

    # Load device_state for safety_runner. Empty dict if no gather has run.
    device_state_full: dict = {}
    if os.path.exists(DEVICE_STATE_PATH):
        with open(DEVICE_STATE_PATH) as f:
            try:
                device_state_full = json.load(f)
            except json.JSONDecodeError:
                pass
    state_devices = device_state_full.get("devices") or {}

    # Group plan jobs by device, applying the surgical filters
    jobs_by_device: dict[str, list[dict]] = {}
    for j in plan.get("jobs", []):
        if j.get("device") is None:
            # Plan-time not_applicable with no device — skip silently
            continue
        if device_filter and j["device"] != device_filter:
            continue
        if method_filter and j["method"] != method_filter:
            continue
        if schema_filter and j["schema"] != schema_filter:
            continue
        if protocol_filter and j["protocol"] != protocol_filter:
            continue
        if kind_filter and j["kind"] != kind_filter:
            continue
        jobs_by_device.setdefault(j["device"], []).append(j)

    if not jobs_by_device:
        print("  no jobs match filters")
        return {"workers": 0, "summaries": []}

    matrix_db = MatrixDB()
    # Record the effective scope of THIS execute run. The renderer uses it to
    # correctly classify "not_run" — a setter job filtered out by --kind read
    # is NOT a coverage gap, it's out of scope for this run.
    execute_meta = {
        "at": _now_iso(),
        "scope": list(scope),
        "kind_filter": kind_filter,
        "method_filter": method_filter,
        "schema_filter": schema_filter,
        "device_filter": device_filter,
        "protocol_filter": protocol_filter,
    }
    matrix_db.set_meta(generated_at=_now_iso(), scope=list(scope),
                       last_execute=execute_meta)

    print(f"  spawning {len(jobs_by_device)} workers, "
          f"{sum(len(v) for v in jobs_by_device.values())} jobs total")
    summaries = []
    with cf.ThreadPoolExecutor(max_workers=len(jobs_by_device)) as exe:
        futures = {
            exe.submit(run_worker, ip, jobs, matrix_db,
                       state_devices.get(ip, {}), schemas_meta,
                       setter_tests, crud_tests, username, password): ip
            for ip, jobs in jobs_by_device.items()
        }
        for fut in cf.as_completed(futures):
            ip = futures[fut]
            try:
                s = fut.result()
                summaries.append(s)
                cl = " COMMS_LOST" if s.get("comms_lost") else ""
                print(f"    {ip:18s} ran={s['ran']:4d} pass={s['passed']:4d} "
                      f"fail={s['failed']:3d} err={s['errored']:3d} "
                      f"na={s['na']:3d}{cl}")
            except Exception as e:
                print(f"    {ip:18s} WORKER CRASHED: {e}")
                summaries.append({"device": ip, "error": str(e)[:200]})

    # Top-level summary
    total_ran = sum(s.get("ran", 0) for s in summaries)
    total_pass = sum(s.get("passed", 0) for s in summaries)
    total_fail = sum(s.get("failed", 0) for s in summaries)
    total_err = sum(s.get("errored", 0) for s in summaries)
    total_cl = sum(1 for s in summaries if s.get("comms_lost"))
    print(f"  TOTAL: ran={total_ran} pass={total_pass} fail={total_fail} "
          f"err={total_err} comms_lost_workers={total_cl}")

    # Auto-derive has_configured_from_gather if any reads ran. The next
    # plan/execute uses the updated device_state, closing the feedback
    # loop on the manual pool maintenance problem.
    if any(any(j.get("kind") == "read" for j in jobs)
           for jobs in jobs_by_device.values()):
        derive_has_configured_from_matrix()
        print("  derived has_configured_from_gather → device_state.json")

    return {"workers": len(jobs_by_device), "summaries": summaries}


# =============================================================================
# Component 7 — Doc renderer
# =============================================================================
#
# Generates two files from release_matrix.json + release_test_plan.json:
#
#   docs/RELEASE_MATRIX.md  — read-only scoreboard. Summary tables, fleet
#                              overview, per-schema verdict matrix, comms_lost
#                              list. Never hand-edited.
#
#   docs/TODO_HITLIST.md   — failures grouped by #bucket tag. Untagged
#                              failures land in NEEDS TRIAGE for human
#                              assignment. tag_map.yaml provides the
#                              auto-categorization.
#
# Both files are regenerated on every --render call. Manual additions
# happen in tests/tag_map.yaml (sticky across runs) and docs/TODO.md
# (human-curated, not regenerated).
# -----------------------------------------------------------------------------


def _load_tag_map() -> list[dict]:
    """Load tests/tag_map.yaml. Returns the patterns list."""
    if not os.path.exists(TAG_MAP_PATH):
        return []
    import yaml
    with open(TAG_MAP_PATH) as f:
        data = yaml.safe_load(f) or {}
    return data.get("patterns") or []


def _load_method_exemptions() -> list[dict]:
    """Load tests/method_exemptions.yaml. Returns the exemptions list.

    Each exemption matches by (method, device?, protocol?). When matched,
    the renderer overrides the cell verdict to 'exempt' and stamps the
    reason. Underlying matrix DB cells are unchanged — the override is
    cosmetic at render time but reflected in the gate verdict.
    """
    if not os.path.exists(METHOD_EXEMPTIONS_PATH):
        return []
    import yaml
    with open(METHOD_EXEMPTIONS_PATH) as f:
        data = yaml.safe_load(f) or {}
    return data.get("exemptions") or []


def _apply_exemptions(db: dict, exemptions: list[dict]) -> int:
    """Walk the matrix DB, override fail/error cells to 'exempt' where matched.

    Mutates `db` in place (caller passes a fresh read; safe to mutate).
    Returns the number of cells overridden.
    """
    if not exemptions:
        return 0
    overridden = 0
    for schema, methods in (db.get("results") or {}).items():
        for cell_key, protocols in methods.items():
            for protocol, devices in protocols.items():
                for device, cell in devices.items():
                    if cell.get("verdict") not in ("fail", "error"):
                        continue
                    method_name = cell.get("method") or cell_key
                    for ex in exemptions:
                        if ex.get("method") and ex["method"] != method_name:
                            continue
                        if ex.get("device") and ex["device"] != device:
                            continue
                        if ex.get("protocol") and ex["protocol"] != protocol:
                            continue
                        cell["original_verdict"] = cell["verdict"]
                        cell["verdict"] = "exempt"
                        cell["exempt_reason"] = ex.get("reason", "exemption matched")
                        overridden += 1
                        break
    return overridden


def _classify_failure(cell: dict, schema: str, method: str, protocol: str,
                      patterns: list[dict]) -> list[str]:
    """Match a failure cell against tag_map patterns. Returns list of tags."""
    for pat in patterns:
        m = pat.get("match") or {}
        if "method" in m and m["method"] != method:
            continue
        if "protocol" in m and m["protocol"] != protocol:
            continue
        if "kind" in m and m["kind"] != cell.get("kind"):
            continue
        if "schema" in m and m["schema"] != schema:
            continue
        evidence_substr = m.get("evidence_contains")
        if evidence_substr:
            # Build a haystack from every place evidence might live:
            # cell.evidence (dict), cell.contract (list), cell.types (list),
            # cell.diffs (parity cells), cell.reason (exemptions/NA).
            haystack_parts = [
                json.dumps(cell.get("evidence", {}) or {}),
                " ".join(cell.get("contract", []) or []),
                " ".join(cell.get("types", []) or []),
                " ".join(cell.get("diffs", []) or []),
                str(cell.get("reason") or ""),
            ]
            ev_str = " ".join(haystack_parts)
            if evidence_substr not in ev_str:
                continue
        return list(pat.get("tags") or [])
    return []


def _iter_cells(db: dict):
    """Walk results[schema][method][protocol][device] — yield (s, m, p, d, cell)."""
    for schema, methods in (db.get("results") or {}).items():
        for method, protocols in methods.items():
            for protocol, devices in protocols.items():
                for device, cell in devices.items():
                    yield schema, method, protocol, device, cell


def _summarize(db: dict, plan: dict | None) -> dict:
    """Compute the summary statistics block for the matrix doc.

    "not_run" counts jobs that were IN SCOPE for the last execute run but
    have no corresponding cell. Jobs filtered out by --kind/--device/etc.
    are NOT counted as not_run — they're out-of-scope, not missing.

    Scope is read from db['last_execute'] (set by run_execute at runtime).
    If no last_execute meta is present, falls back to counting all plan
    jobs with device != None.
    """
    counts = {"pass": 0, "fail": 0, "error": 0, "exempt": 0,
              "not_applicable": 0, "comms_lost": 0, "not_run": 0}
    by_protocol: dict[str, dict] = {}
    by_device: dict[str, dict] = {}
    by_kind: dict[str, dict] = {}

    for schema, method, protocol, device, cell in _iter_cells(db):
        verdict = cell.get("verdict", "error")
        counts[verdict] = counts.get(verdict, 0) + 1
        # Don't pollute the per-protocol table with the synthetic "parity"
        # slot — parity is not a real transport.
        if protocol != "parity":
            by_protocol.setdefault(protocol, {})[verdict] = \
                by_protocol.setdefault(protocol, {}).get(verdict, 0) + 1
        by_device.setdefault(device, {})[verdict] = \
            by_device.setdefault(device, {}).get(verdict, 0) + 1
        kind = cell.get("kind", "unknown")
        by_kind.setdefault(kind, {})[verdict] = \
            by_kind.setdefault(kind, {}).get(verdict, 0) + 1

    # Compute not_run: jobs in plan AND in last execute scope with no cell
    if plan:
        last_exec = db.get("last_execute") or {}
        kind_filter = last_exec.get("kind_filter")
        method_filter = last_exec.get("method_filter")
        schema_filter = last_exec.get("schema_filter")
        device_filter = last_exec.get("device_filter")
        protocol_filter = last_exec.get("protocol_filter")

        present: set[tuple] = set()
        for s, m, p, d, _ in _iter_cells(db):
            present.add((s, m, p, d))

        for j in plan.get("jobs", []):
            if j.get("device") is None:
                continue  # plan-time NA, not expected to have a cell
            # Apply last-execute filters — jobs filtered out were out of scope
            if kind_filter and j.get("kind") != kind_filter:
                continue
            if method_filter and j.get("method") != method_filter:
                continue
            if schema_filter and j.get("schema") != schema_filter:
                continue
            if device_filter and j.get("device") != device_filter:
                continue
            if protocol_filter and j.get("protocol") != protocol_filter:
                continue
            # Use the same cell key derivation as the writer
            cell_key = j.get("test_id") or j["method"]
            key = (j["schema"], cell_key, j["protocol"], j["device"])
            if key not in present:
                counts["not_run"] += 1

    return {
        "counts": counts,
        "by_protocol": by_protocol,
        "by_device": by_device,
        "by_kind": by_kind,
    }


_VERDICT_ORDER = ["pass", "fail", "error", "exempt", "not_applicable",
                  "comms_lost", "not_run"]
_VERDICT_GLYPH = {
    "pass": ".", "fail": "F", "error": "E", "exempt": "x",
    "not_applicable": "-", "comms_lost": "!", "not_run": "?",
}


def _perf_summary(db: dict) -> dict:
    """Compute SNMP/MOPS timing ratios and per-device totals from cell timings.

    Read cells store time_ms as captured by run_one_read. We aggregate per
    (method, protocol) and compute SNMP/MOPS ratios. A high ratio means
    the SNMP path is making more round trips than the MOPS path for the
    same data — typically because SNMP iterates compound indexes or
    cross-references auxiliary tables (ifIndex, VACM, etc.) that MOPS
    handles atomically in a single XML response.

    Expected multipliers (rough):
      - getter with no joins         → ~1×
      - getter with ifIndex resolve  → ~2×
      - getter with VACM cross-ref   → ~3×
      - getter with both             → ~6×
      - VRRP-class compound          → ~3-6×

    Anything significantly above its expected multiplier is an anomaly
    worth investigating. Per-method expected multipliers are not yet
    computed from the wire YAMLs (that's a follow-up); for v1 we just
    surface raw ratios and let the reader judge.
    """
    from collections import defaultdict
    by_method_proto: dict[tuple, list[int]] = defaultdict(list)
    by_device_proto: dict[tuple, list[int]] = defaultdict(list)

    for schema, methods in (db.get("results") or {}).items():
        for method_or_test, protos in methods.items():
            for proto, devs in protos.items():
                for dev, cell in devs.items():
                    if cell.get("verdict") != "pass":
                        continue
                    if cell.get("kind") != "read":
                        continue
                    t = cell.get("time_ms", 0)
                    if not t or t <= 0:
                        continue
                    by_method_proto[(method_or_test, proto)].append(t)
                    by_device_proto[(dev, proto)].append(t)

    ratios = []
    for (method, proto), times in by_method_proto.items():
        if proto != "mops":
            continue
        snmp_times = by_method_proto.get((method, "snmp"))
        if not snmp_times:
            continue
        mops_avg = sum(times) / len(times)
        snmp_avg = sum(snmp_times) / len(snmp_times)
        if mops_avg <= 0:
            continue
        ratios.append({
            "method": method,
            "mops_ms": round(mops_avg),
            "snmp_ms": round(snmp_avg),
            "ratio": round(snmp_avg / mops_avg, 1),
        })
    ratios.sort(key=lambda r: -r["ratio"])

    device_perf = []
    for (dev, proto), times in sorted(by_device_proto.items()):
        device_perf.append({
            "device": dev,
            "protocol": proto,
            "cells": len(times),
            "total_ms": round(sum(times)),
            "avg_ms": round(sum(times) / len(times)) if times else 0,
            "max_ms": round(max(times)) if times else 0,
        })

    return {"ratios": ratios, "device_perf": device_perf}


def _render_matrix_md(db: dict, plan: dict | None, device_pool: dict) -> str:
    """Generate the docs/RELEASE_MATRIX.md content."""
    summary = _summarize(db, plan)
    lines: list[str] = []

    lines.append("# RELEASE_MATRIX")
    lines.append("")
    lines.append("> Auto-generated by `tests/release_matrix.py --render`. Do not edit.")
    lines.append(f"> Last run: `{db.get('generated_at') or 'never'}`")
    lines.append(f"> Scope: `{db.get('scope') or '?'}`")
    lines.append(f"> Source: `tests/release_matrix.json` + `tests/release_test_plan.json`")
    lines.append("")

    # ---- Summary ----
    lines.append("## Summary")
    lines.append("")
    counts = summary["counts"]
    total = sum(counts.values())
    lines.append("| Verdict | Count |")
    lines.append("|---|---|")
    for v in _VERDICT_ORDER:
        lines.append(f"| `{v}` | {counts.get(v, 0)} |")
    lines.append(f"| **total** | **{total}** |")
    lines.append("")

    # Release gate verdict
    blocking = counts.get("fail", 0) + counts.get("error", 0) + \
               counts.get("comms_lost", 0) + counts.get("not_run", 0)
    gate = "PASS" if blocking == 0 and total > 0 else "FAIL"
    lines.append(f"**Release gate verdict: `{gate}`** "
                 f"(blocking: {blocking})")
    lines.append("")

    # ---- Per-protocol breakdown ----
    lines.append("## Per-protocol")
    lines.append("")
    headers = ["protocol"] + _VERDICT_ORDER
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    for proto in sorted(summary["by_protocol"].keys()):
        row = [proto]
        for v in _VERDICT_ORDER:
            row.append(str(summary["by_protocol"][proto].get(v, 0)))
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # ---- Per-kind breakdown ----
    lines.append("## Per-kind")
    lines.append("")
    headers = ["kind"] + _VERDICT_ORDER
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    for kind in sorted(summary["by_kind"].keys()):
        row = [kind]
        for v in _VERDICT_ORDER:
            row.append(str(summary["by_kind"][kind].get(v, 0)))
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # ---- Fleet ----
    lines.append("## Fleet")
    lines.append("")
    pool_devices = {d["ip"]: d for d in (device_pool.get("devices") or [])}
    lines.append("| device | label | sw_level | safe_for | total | pass | fail | err | n/a |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for ip in sorted(summary["by_device"].keys()):
        meta = pool_devices.get(ip, {})
        d = summary["by_device"][ip]
        total_dev = sum(d.values())
        lines.append(
            f"| `{ip}` | {meta.get('label', '?')} | {meta.get('sw_level', '?')} "
            f"| {','.join(meta.get('safe_for', []))} | {total_dev} "
            f"| {d.get('pass', 0)} | {d.get('fail', 0)} | {d.get('error', 0)} "
            f"| {d.get('not_applicable', 0)} |"
        )
    lines.append("")

    # ---- Per-schema status grid ----
    lines.append("## Per-schema verdict grid")
    lines.append("")
    lines.append("Glyphs: `" + "  ".join(f"{g} = {v}" for v, g in _VERDICT_GLYPH.items()) + "`")
    lines.append("")

    # Build the column header: (protocol, device) pairs that actually have cells.
    # Skip the synthetic "parity" protocol — it's rendered in its own section.
    col_keys: set[tuple] = set()
    for s, m, p, d, _ in _iter_cells(db):
        if p == "parity":
            continue
        col_keys.add((p, d))
    cols = sorted(col_keys)

    for schema in sorted(db.get("results") or {}):
        methods = db["results"][schema]
        lines.append(f"### {schema}")
        lines.append("")
        # Header
        head = "| method |"
        sep = "|---|"
        for p, d in cols:
            head += f" {p[:4]}/{d.split('.')[-1]} |"
            sep += "---|"
        lines.append(head)
        lines.append(sep)
        for method in sorted(methods.keys()):
            # Skip method entries that only have a parity slot (no real
            # protocol cells). Parity-only rows would render as all dots.
            method_data = methods.get(method, {})
            if all(p == "parity" for p in method_data.keys()):
                continue
            row = f"| `{method}` |"
            for p, d in cols:
                cell = method_data.get(p, {}).get(d)
                if cell is None:
                    row += " . |"  # not in scope
                else:
                    row += f" {_VERDICT_GLYPH.get(cell.get('verdict'), '?')} |"
            lines.append(row)
        lines.append("")

    # ---- Protocol wire coverage — independent of run results ----
    # Shows which protocols have at least one wire source declared per
    # method. Surfaces "schema declares this method but no SSH wire source
    # exists" gaps that are otherwise invisible because SSH wasn't in scope.
    try:
        from audit_common import load_all_method_metadata
        wire_meta = load_all_method_metadata()
    except Exception:
        wire_meta = {}

    if wire_meta:
        from collections import defaultdict
        protos = ("mops", "snmp", "ssh")
        coverage = defaultdict(list)
        gaps_per_proto = {p: [] for p in protos}
        total_methods = 0

        for method_name, m in sorted(wire_meta.items()):
            total_methods += 1
            entry = {
                "method": method_name,
                "kind": m["kind"],
                "feature": m["feature"],
                **{p: (p in m["protocols"]) for p in protos},
            }
            coverage[m["feature"]].append(entry)
            for p in protos:
                if not entry[p]:
                    gaps_per_proto[p].append(entry)

        lines.append("## Protocol wire coverage")
        lines.append("")
        lines.append("Independent of run results. Shows which protocols have at "
                     "least one wire source declared per method, per the schema "
                     "YAMLs in `crude_engine/schemas/` + `crude_engine/wire/`.")
        lines.append("")
        lines.append(f"**{total_methods} methods total across "
                     f"{len(coverage)} schemas.**")
        lines.append("")
        lines.append("| protocol | declared | missing | coverage |")
        lines.append("|---|---|---|---|")
        for p in protos:
            decl = total_methods - len(gaps_per_proto[p])
            pct = round(100.0 * decl / total_methods) if total_methods else 0
            lines.append(f"| `{p}` | {decl}/{total_methods} | "
                         f"{len(gaps_per_proto[p])} | {pct}% |")
        lines.append("")

        for p in protos:
            if not gaps_per_proto[p]:
                continue
            lines.append(f"### Methods missing `{p}` wire source "
                         f"({len(gaps_per_proto[p])})")
            lines.append("")
            by_schema_gap: dict[str, list[str]] = defaultdict(list)
            for e in gaps_per_proto[p]:
                by_schema_gap[e["feature"]].append(
                    f"{e['method']} ({e['kind']})"
                )
            lines.append("Grouped by schema feature. These methods exist in "
                         "the schema but have NO wire source for this protocol "
                         "— calling them via this protocol will fail with "
                         '"no wire source" or be marked `not_applicable` at '
                         "plan time.")
            lines.append("")
            for feature in sorted(by_schema_gap.keys()):
                lines.append(f"- **{feature}**: " +
                             ", ".join(f"`{m}`" for m in by_schema_gap[feature]))
            lines.append("")

    # ---- Cross-protocol parity — value comparison across protocols ----
    # Parity cells have kind="parity" and are addressed with protocol="parity"
    # in the DB. They're the output of the worker's post-execute parity
    # collector. A parity fail means the same method returned different
    # data on different protocols — a real bug regardless of shape.
    parity_fails = []
    parity_passes = 0
    for schema, methods in (db.get("results") or {}).items():
        for method_key, protocols in methods.items():
            parity_slot = protocols.get("parity")
            if not parity_slot:
                continue
            for device, cell in parity_slot.items():
                if cell.get("verdict") == "fail":
                    parity_fails.append({
                        "schema": schema, "method": method_key,
                        "device": device,
                        "compared": cell.get("compared_protocols") or [],
                        "diffs": cell.get("diffs") or [],
                    })
                else:
                    parity_passes += 1

    if parity_fails or parity_passes:
        lines.append("## Cross-protocol parity")
        lines.append("")
        lines.append("For each method that returned data on ≥ 2 protocols on the "
                     "same device, the matrix tool compared the results. A fail "
                     "here means the same getter returned different data via "
                     "different protocols — a real engine/driver/wire bug "
                     "regardless of whether the shape checks passed.")
        lines.append("")
        lines.append(f"**{parity_passes + len(parity_fails)} parity checks run, "
                     f"{parity_passes} passed, {len(parity_fails)} failed.**")
        lines.append("")
        if parity_fails:
            lines.append("### Parity failures")
            lines.append("")
            lines.append("| method | device | compared | diffs |")
            lines.append("|---|---|---|---|")
            for pf in parity_fails[:100]:
                compared = "/".join(pf["compared"])
                diff_str = "; ".join(pf["diffs"][:2])
                if len(diff_str) > 80:
                    diff_str = diff_str[:77] + "..."
                lines.append(f"| `{pf['method']}` | `{pf['device']}` "
                             f"| {compared} | {diff_str} |")
            if len(parity_fails) > 100:
                lines.append(f"| … | … | … | ({len(parity_fails) - 100} more) |")
            lines.append("")

    # ---- Perf — SNMP/MOPS timing ratios + per-device totals ----
    perf = _perf_summary(db)
    if perf["ratios"] or perf["device_perf"]:
        lines.append("## Perf — SNMP vs MOPS timing")
        lines.append("")
        lines.append("Each cell's `time_ms` is captured at read time. Comparing per-method "
                     "averages across protocols surfaces SNMP getters that make more "
                     "round trips than their MOPS counterparts.")
        lines.append("")
        lines.append("**Expected multipliers** (rough):")
        lines.append("- no joins → ~1×")
        lines.append("- ifIndex resolve → ~2×")
        lines.append("- VACM cross-ref → ~3×")
        lines.append("- both → ~6×")
        lines.append("- VRRP / compound index → ~3–6×")
        lines.append("")
        lines.append("Methods well above their expected multiplier are anomalies "
                     "worth investigating. Flags: `!` = ratio > 5×, `!!` = ratio > 10× "
                     "(definitely anomalous regardless of joins).")
        lines.append("")
        if perf["ratios"]:
            lines.append("### Top 20 by SNMP/MOPS ratio")
            lines.append("")
            lines.append("| method | mops_ms | snmp_ms | ratio | flag |")
            lines.append("|---|---|---|---|---|")
            for r in perf["ratios"][:20]:
                flag = "!!" if r["ratio"] > 10 else "!" if r["ratio"] > 5 else ""
                lines.append(f"| `{r['method']}` | {r['mops_ms']} | {r['snmp_ms']} "
                             f"| {r['ratio']}× | {flag} |")
            lines.append("")
            big = sum(1 for r in perf["ratios"] if r["ratio"] > 10)
            mid = sum(1 for r in perf["ratios"] if 5 < r["ratio"] <= 10)
            lines.append(f"**Summary:** {big} method(s) > 10× ratio, "
                         f"{mid} method(s) between 5× and 10×, "
                         f"{len(perf['ratios'])} methods compared.")
            lines.append("")
        if perf["device_perf"]:
            lines.append("### Per-device per-protocol totals")
            lines.append("")
            lines.append("| device | protocol | cells | total_ms | avg_ms | max_ms |")
            lines.append("|---|---|---|---|---|---|")
            for d in perf["device_perf"]:
                lines.append(f"| `{d['device']}` | `{d['protocol']}` | {d['cells']} "
                             f"| {d['total_ms']} | {d['avg_ms']} | {d['max_ms']} |")
            lines.append("")

    # ---- Comms lost ----
    markers = db.get("markers") or []
    if markers:
        lines.append("## Comms-lost markers — manual verification required")
        lines.append("")
        for m in markers:
            if m.get("type") != "WORKER_STOPPED":
                continue
            lines.append(f"### {m.get('device')} — {m.get('phase', '?')}")
            lines.append("")
            lines.append(f"- After job: `{m.get('after_job', '(none)')}`")
            lines.append(f"- Protocol: `{m.get('protocol', '?')}`")
            lines.append(f"- Error: `{m.get('error', '?')}`")
            lines.append(f"- Remaining jobs at stop: {m.get('remaining_jobs', '?')}")
            lines.append(f"- Stopped at: `{m.get('at')}`")
            lines.append("")
            lines.append("Verify device state manually before resuming. Then:")
            lines.append("")
            lines.append(f"```")
            lines.append(f"release_matrix.py --resume --device {m.get('device')}")
            lines.append(f"```")
            lines.append("")

    return "\n".join(lines) + "\n"


def _render_hitlist_md(db: dict, patterns: list[dict]) -> str:
    """Generate docs/TODO_HITLIST.md from failures grouped by tag."""
    lines: list[str] = []
    lines.append("# TODO_HITLIST")
    lines.append("")
    lines.append("> Auto-generated by `tests/release_matrix.py --render`. Do not edit.")
    lines.append("> Source: `tests/release_matrix.json` failures, grouped by `#bucket` tag.")
    lines.append("> Curated working list lives in `docs/TODO.md` (not auto-generated).")
    lines.append("> Tag stickiness: add patterns to `tests/tag_map.yaml` to auto-categorize "
                 "future runs.")
    lines.append("")

    # Walk failures and bucket them by tag
    by_bucket: dict[str, list[dict]] = {}
    triage: list[dict] = []
    failure_count = 0
    for schema, method, protocol, device, cell in _iter_cells(db):
        verdict = cell.get("verdict")
        if verdict not in ("fail", "error"):
            continue
        failure_count += 1
        tags = _classify_failure(cell, schema, method, protocol, patterns)
        item = {
            "schema": schema, "method": method, "protocol": protocol,
            "device": device, "cell": cell, "tags": tags,
        }
        if not tags:
            triage.append(item)
            continue
        # Use the first bucket tag as the section
        bucket = next((t for t in tags if t.startswith("#") and
                       t in ("#engine", "#schema", "#wire", "#driver",
                             "#crude", "#test", "#release", "#roadmap")), None)
        if bucket is None:
            triage.append(item)
            continue
        by_bucket.setdefault(bucket, []).append(item)

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total failures:** {failure_count}")
    lines.append(f"- **Tagged (auto-categorized):** {failure_count - len(triage)}")
    lines.append(f"- **Needs triage:** {len(triage)}")
    lines.append(f"- **Buckets:** {len(by_bucket)}")
    lines.append("")

    if failure_count == 0:
        lines.append("Nothing failing. RELEASE_MATRIX.md verdict will tell you "
                     "if the gate is open.")
        lines.append("")
        return "\n".join(lines) + "\n"

    # Render each bucket
    bucket_order = ["#engine", "#schema", "#wire", "#driver", "#crude",
                    "#test", "#release", "#roadmap"]
    for bucket in bucket_order:
        if bucket not in by_bucket:
            continue
        lines.append(f"## {bucket}")
        lines.append("")
        for item in by_bucket[bucket]:
            tag_line = " ".join(item["tags"])
            ev = item["cell"].get("evidence") or {}
            ev_str = json.dumps(ev, default=str) if ev else ""
            contract = item["cell"].get("contract") or []
            types = item["cell"].get("types") or []
            lines.append(f"- [ ] {tag_line}")
            lines.append(f"      `{item['method']}` on `{item['device']}` via "
                         f"`{item['protocol']}` (kind={item['cell'].get('kind', '?')})")
            if contract:
                lines.append(f"      contract: `{contract}`")
            if types:
                lines.append(f"      type: `{types}`")
            if ev_str and ev_str != "{}":
                lines.append(f"      evidence: `{ev_str[:200]}`")
            lines.append(f"      first seen: `{item['cell'].get('ran_at', '?')}`")
            lines.append("")

    if triage:
        lines.append("## NEEDS TRIAGE — no tag assigned")
        lines.append("")
        lines.append("Review each item below, decide its `#bucket #ID` tag, and add a "
                     "matching pattern to `tests/tag_map.yaml`. On the next `--render` "
                     "the item will move into the appropriate bucket above.")
        lines.append("")
        for item in triage:
            ev = item["cell"].get("evidence") or {}
            ev_str = json.dumps(ev, default=str) if ev else ""
            contract = item["cell"].get("contract") or []
            types = item["cell"].get("types") or []
            lines.append(f"- [ ] `{item['method']}` on `{item['device']}` via "
                         f"`{item['protocol']}`")
            lines.append(f"      kind: `{item['cell'].get('kind', '?')}`  "
                         f"verdict: `{item['cell'].get('verdict')}`")
            if contract:
                lines.append(f"      contract: `{contract}`")
            if types:
                lines.append(f"      type: `{types}`")
            if ev_str and ev_str != "{}":
                lines.append(f"      evidence: `{ev_str[:200]}`")
            lines.append("")

    return "\n".join(lines) + "\n"


def run_render() -> None:
    """Generate docs/RELEASE_MATRIX.md and docs/TODO_HITLIST.md from current state."""
    db = MatrixDB().read()
    plan: dict | None = None
    if os.path.exists(PLAN_PATH):
        with open(PLAN_PATH) as f:
            try:
                plan = json.load(f)
            except json.JSONDecodeError:
                plan = None

    pool = _load_device_pool()
    patterns = _load_tag_map()
    exemptions = _load_method_exemptions()

    # Apply method exemptions — fail/error cells matching an exemption pattern
    # are reclassified as exempt with the documented reason. Cosmetic at render
    # time but reflected in summary counts and gate verdict.
    n_overridden = _apply_exemptions(db, exemptions)
    if n_overridden:
        print(f"  applied {n_overridden} method exemption(s)")

    matrix_md = _render_matrix_md(db, plan, pool)
    hitlist_md = _render_hitlist_md(db, patterns)

    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(RENDERED_MATRIX_PATH, "w") as f:
        f.write(matrix_md)
    with open(RENDERED_HITLIST_PATH, "w") as f:
        f.write(hitlist_md)

    print(f"  wrote {RENDERED_MATRIX_PATH} ({len(matrix_md)} bytes)")
    print(f"  wrote {RENDERED_HITLIST_PATH} ({len(hitlist_md)} bytes)")


# =============================================================================
# Inspect mode — investigation tool, never writes to matrix DB
# =============================================================================


@functools.lru_cache(maxsize=1)
def _load_inspect_yaml() -> dict:
    """Read tests/inspect.yaml. YAML declares; this only loads."""
    import yaml
    if not os.path.isfile(INSPECT_YAML_PATH):
        raise FileNotFoundError(INSPECT_YAML_PATH)
    with open(INSPECT_YAML_PATH) as f:
        return yaml.safe_load(f) or {}


def _inspect_budget_s(protocol: str, key: str) -> float:
    """One budget from tests/inspect.yaml. key is open_timeout_s or call_timeout_s."""
    data = _load_inspect_yaml()
    entry = ((data.get("protocols") or {}).get(protocol) or {})
    if key not in entry:
        raise KeyError(
            f"tests/inspect.yaml protocols.{protocol}.{key} is not declared"
        )
    return float(entry[key])


def _call_with_timeout(seconds: float, fn, *args, **kwargs):
    """Run fn, raise TimeoutError after seconds.

    Kept for offline proofs. Live inspect does not abandon a worker
    mid-call; each protocol owns open/call/close on one thread.
    """
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    fut = pool.submit(fn, *args, **kwargs)
    try:
        return fut.result(timeout=seconds)
    except concurrent.futures.TimeoutError as exc:
        raise TimeoutError(f"exceeded {seconds}s") from exc
    finally:
        pool.shutdown(wait=False)



def _collect_cli(device):
    """Raw CLI blobs stashed by SSH gather (transport/driver/device)."""
    found = []
    seen = set()
    objs = [device, getattr(device, "engine", None)]
    transports = getattr(device, "_transports", None)
    if isinstance(transports, dict):
        objs.extend(transports.values())
    elif transports:
        objs.append(transports)
    for obj in objs:
        if obj is None:
            continue
        cli = getattr(obj, "last_cli", None)
        if not cli or id(cli) in seen:
            continue
        seen.add(id(cli))
        found.extend(cli)
    return found


def _inspect_one_protocol(
    driver,
    proto: str,
    device_filter: str,
    username: str,
    password: str,
    method_name: str,
    call_kwargs: dict,
    trace: bool,
):
    """One thread, one device, full lifecycle. Never raises.

    Hang never returns; the caller wait() marks timeout without
    touching this device. close() only runs in this thread.
    """
    t_open = time.monotonic()
    try:
        _inspect_budget_s(proto, "open_timeout_s")
        _inspect_budget_s(proto, "call_timeout_s")
    except (KeyError, FileNotFoundError, ValueError, TypeError) as e:
        return proto, {
            "status": "dispatch_error",
            "elapsed_ms": 0,
            "open_ms": None,
            "call_ms": None,
            "error": str(e),
        }

    device = None
    try:
        try:
            device = driver(
                device_filter,
                username,
                password,
                optional_args={"protocol": proto},
            )
            device.open()
        except Exception as e:
            open_ms = round((time.monotonic() - t_open) * 1000)
            return proto, {
                "status": "connect_failed",
                "phase": "open",
                "elapsed_ms": open_ms,
                "open_ms": open_ms,
                "call_ms": None,
                "error": str(e)[:300],
            }
        open_ms = round((time.monotonic() - t_open) * 1000)

        t_call = time.monotonic()
        try:
            fn = getattr(device, method_name)
            try:
                raw = fn(**call_kwargs)
            except TypeError:
                raw = fn()
            last_trace = getattr(device, "last_trace", None) if trace else None
            last_cli = _collect_cli(device) if trace else []
            if isinstance(raw, tuple):
                raw = raw[0]
            call_ms = round((time.monotonic() - t_call) * 1000)
            out = {
                "status": "ok",
                "elapsed_ms": open_ms + call_ms,
                "open_ms": open_ms,
                "call_ms": call_ms,
                "raw": _jsonable(raw),
            }
            if trace:
                out["trace"] = last_trace
                if last_cli:
                    out["cli"] = last_cli
            return proto, out
        except Exception as e:
            call_ms = round((time.monotonic() - t_call) * 1000)
            return proto, {
                "status": "dispatch_error",
                "phase": "call",
                "elapsed_ms": open_ms + call_ms,
                "open_ms": open_ms,
                "call_ms": call_ms,
                "error": str(e)[:300],
            }
    finally:
        if device is not None:
            try:
                device.close()
            except Exception:
                pass


def _print_inspect_protocol(proto: str, result: dict, trace: bool) -> None:
    open_s = None
    call_s = None
    try:
        open_s = _inspect_budget_s(proto, "open_timeout_s")
        call_s = _inspect_budget_s(proto, "call_timeout_s")
    except (KeyError, FileNotFoundError, ValueError, TypeError):
        pass
    if open_s is not None:
        print(f"--- {proto} (open {open_s}s / call {call_s}s) ---")
    else:
        print(f"--- {proto} ---")
    status = result.get("status")
    if status == "ok":
        print(
            f"  open_ms={result.get('open_ms')} "
            f"call_ms={result.get('call_ms')} "
            f"elapsed_ms={result.get('elapsed_ms')}"
        )
        raw = result.get("raw")
        if isinstance(raw, dict):
            print(f"  raw type=dict len={len(raw)}")
            if raw:
                first_key = next(iter(raw))
                first_val = raw[first_key]
                print(f"  first key:  {first_key!r}")
                if isinstance(first_val, dict):
                    print("  first row:")
                    for k, v in sorted(first_val.items()):
                        print(f"    {k}: {repr(v)[:80]}")
                else:
                    print(f"  first val:  {repr(first_val)[:120]}")
        elif isinstance(raw, list):
            print(f"  raw type=list len={len(raw)}")
            if raw:
                print(f"  first item: {repr(raw[0])[:200]}")
        else:
            print(f"  raw: {repr(raw)[:200]}")
        last_trace = result.get("trace")
        if trace and last_trace:
            print(f"  trace ({len(last_trace)} entries):")
            for entry in last_trace:
                if isinstance(entry, dict):
                    parts = []
                    for k in sorted(entry.keys()):
                        v = entry[k]
                        sval = repr(v) if not isinstance(v, str) else v
                        if len(sval) > 60:
                            sval = sval[:57] + "..."
                        parts.append(f"{k}={sval}")
                    print(f"    {' '.join(parts)}")
                else:
                    print(f"    {repr(entry)[:200]}")
        elif trace:
            print("  trace: (empty — device.last_trace was None)")
    elif status == "timeout":
        print(
            f"  TIMEOUT: {result.get('error')} "
            f"open_ms={result.get('open_ms')} call_ms={result.get('call_ms')}"
        )
    elif status == "connect_failed":
        print(f"  CONNECT_FAILED: {(result.get('error') or '')[:200]}")
    else:
        err = result.get("error") or ""
        print(f"  {str(status).upper()}: {err[:200]}")
    print()


def _jsonable(obj):
    try:
        return json.loads(json.dumps(obj, default=str))
    except TypeError:
        return repr(obj)[:500]


def run_inspect(method_name: str | None,
                device_filter: str | None,
                protocol_filter: str | None,
                schema_filter: str | None = None,
                trace: bool = False,
                no_validate: bool = False,
                username: str = "admin",
                password: str = "private"):
    """Investigation mode for fault finding.

    Runs the named read method on the named device across every supported
    protocol (or just the named one). Prints for interactive use AND returns
    a dict the sidecar can put on the wire:

        {
          "exit": 0|2,
          "method": ...,
          "device": ...,
          "protocols": {proto: {status, open_ms, call_ms, elapsed_ms, raw|error}},
          "parity_diffs": [...],
        }

    `exit` 2 is usage (missing method/device). `exit` 0 means the inspect
    ran; it is not "all protocols agreed." Parity diffs stay in
    parity_diffs so callers can file issues. Does NOT write the matrix DB.
    """
    def usage(msg: str) -> dict:
        print(msg)
        return {
            "exit": 2,
            "error": msg,
            "method": method_name,
            "device": device_filter,
            "protocols": {},
            "parity_diffs": [],
        }

    if not method_name:
        return usage("--inspect requires --method")
    if not device_filter:
        return usage("--inspect requires --device")

    from audit_common import load_all_method_metadata
    schemas_meta = load_all_method_metadata()
    if method_name not in schemas_meta:
        return usage(f"unknown method: {method_name}")

    meta = schemas_meta[method_name]
    if meta["kind"] != "read":
        return usage(f"--inspect only supports read methods (got {meta['kind']})")

    declared_protocols = sorted(meta["protocols"])
    if protocol_filter:
        if protocol_filter not in declared_protocols:
            return usage(
                f"protocol {protocol_filter!r} has no wire source for {method_name}"
            )
        protocols = [protocol_filter]
    else:
        protocols = declared_protocols

    print(f"=== INSPECT {method_name} on {device_filter} ===")
    print(f"  feature: {meta['feature']}")
    print(f"  declared protocols: {declared_protocols}")
    print(f"  inspecting:         {protocols}")
    print(f"  primary_key:        {meta.get('primary_key') or '(flat)'}")
    sub_tables = meta.get("sub_tables") or {}
    if sub_tables:
        print(f"  sub_tables:         {sorted(sub_tables.keys())}")
    flags = []
    if trace:
        flags.append("trace=True")
    if no_validate:
        flags.append("validate=False")
    flags.append("napalm_compat=False")
    print(f"  engine flags:       {', '.join(flags)}")
    print()

    if get_network_driver is None:
        raise ImportError("napalm is required for live inspect")
    driver = get_network_driver("hios")
    raw_results: dict[str, object] = {}
    protocols_out: dict[str, dict] = {}

    call_kwargs: dict = {"napalm_compat": False}
    if trace:
        call_kwargs["trace"] = True
    if no_validate:
        call_kwargs["validate"] = False

    to_run = []
    overall_s = 0.0
    for proto in protocols:
        try:
            open_s = _inspect_budget_s(proto, "open_timeout_s")
            call_s = _inspect_budget_s(proto, "call_timeout_s")
        except (KeyError, FileNotFoundError, ValueError, TypeError) as e:
            protocols_out[proto] = {
                "status": "dispatch_error",
                "elapsed_ms": 0,
                "open_ms": None,
                "call_ms": None,
                "error": str(e),
            }
            continue
        to_run.append(proto)
        overall_s = max(overall_s, open_s + call_s)

    pool = concurrent.futures.ThreadPoolExecutor(max_workers=max(1, len(to_run)))
    futures: dict = {}
    try:
        for proto in to_run:
            fut = pool.submit(
                _inspect_one_protocol,
                driver,
                proto,
                device_filter,
                username,
                password,
                method_name,
                call_kwargs,
                trace,
            )
            futures[fut] = proto
        done, not_done = concurrent.futures.wait(futures, timeout=overall_s)
        for fut in done:
            proto, result = fut.result()
            protocols_out[proto] = result
        for fut in not_done:
            proto = futures[fut]
            protocols_out[proto] = {
                "status": "timeout",
                "elapsed_ms": round(overall_s * 1000),
                "open_ms": None,
                "call_ms": None,
                "error": "overall deadline exceeded",
            }
    finally:
        # Hung workers stay isolated. Waiting would hold sidecar RunLock.
        # Do not close() their device from this thread.
        pool.shutdown(wait=False)

    for proto in protocols:
        result = protocols_out.get(proto) or {}
        _print_inspect_protocol(proto, result, trace)
        raw = result.get("raw")
        if result.get("status") == "ok" and raw is not None:
            raw_results[proto] = raw

    diffs: list = []
    if len(raw_results) >= 2:
        print("=== parity ===")
        diffs = list(_compute_parity(method_name, meta, raw_results) or [])
        if not diffs:
            print("  PARITY OK — all protocols return matching values for "
                  "non-timing fields")
        else:
            print(f"  {len(diffs)} parity diff(s):")
            for d in diffs:
                print(f"    {d}")
    else:
        print("=== parity ===")
        print("  (need ≥ 2 protocols with results to compare)")

    return {
        "exit": 0,
        "method": method_name,
        "device": device_filter,
        "protocols": protocols_out,
        "parity_diffs": _jsonable(diffs),
    }



# =============================================================================
# CLI
# =============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="release_matrix.py — release-gate orchestrator for crude-engine"
    )
    parser.add_argument("--gather", action="store_true",
                        help="Live read pass per device → tests/device_state.json")
    parser.add_argument("--plan", action="store_true",
                        help="Generate test plan from schemas + device_pool")
    parser.add_argument("--execute", action="store_true",
                        help="Execute the test plan (worker pool)")
    parser.add_argument("--render", action="store_true",
                        help="Render docs/RELEASE_MATRIX.md and docs/TODO_HITLIST.md")
    parser.add_argument("--gate", action="store_true",
                        help="Full pipeline: gather → plan → execute → render → verdict")
    parser.add_argument("--resume", action="store_true",
                        help="Resume one device after manual comms-loss verification")

    parser.add_argument("--method", help="Surgical: run a single method")
    parser.add_argument("--schema", help="Surgical: run all methods of one schema")
    parser.add_argument("--protocol", help="Surgical: limit to one protocol")
    parser.add_argument("--device", help="Surgical: limit to one device IP")
    parser.add_argument("--kind", choices=["read", "setter", "crud"],
                        help="Surgical: limit to one job kind (read/setter/crud). "
                        "Useful for read-only safety dry runs.")
    parser.add_argument("--scope", nargs="+", default=["mops", "snmp"],
                        help="Protocols in release scope (default: mops snmp)")

    parser.add_argument("--reset", action="store_true",
                        help="Wipe release_matrix.json before running")
    parser.add_argument("--db-info", action="store_true",
                        help="Print a one-line summary of the current matrix DB and exit")
    parser.add_argument("--inspect", action="store_true",
                        help="Investigation mode: run --method on --device across "
                        "every supported protocol, dump raw output side-by-side, "
                        "run the parity check, do NOT touch the matrix DB. "
                        "Use this for fault finding instead of writing throwaway "
                        "Python scripts.")
    parser.add_argument("--trace", action="store_true",
                        help="Inspect modifier: pass trace=True to the engine, "
                        "capture device.last_trace, dump pipeline steps. "
                        "Reveals what the engine actually did with the data.")
    parser.add_argument("--no-validate", action="store_true",
                        help="Inspect modifier: pass validate=False to the "
                        "engine. Skips Gate 1/2 rejection, still produces "
                        "context. Useful when something would normally fail "
                        "validation but you want to see the underlying data.")

    args = parser.parse_args()

    if args.reset:
        MatrixDB().reset()
        print(f"reset {MATRIX_PATH}")
        if not any([args.gather, args.plan, args.execute, args.render,
                    args.gate, args.resume, args.method, args.schema,
                    args.db_info]):
            return 0

    if args.db_info:
        db = MatrixDB().read()
        cells = 0
        for schema in db.get("results", {}).values():
            for method in schema.values():
                for proto in method.values():
                    cells += len(proto)
        markers = len(db.get("markers", []))
        print(f"matrix: {cells} cells, {markers} markers, "
              f"generated_at={db.get('generated_at')}, "
              f"engine_version={db.get('engine_version')}")
        return 0

    if args.inspect:
        inspect_out = run_inspect(method_name=args.method,
                                  device_filter=args.device,
                                  protocol_filter=args.protocol,
                                  schema_filter=args.schema,
                                  trace=args.trace,
                                  no_validate=args.no_validate)
        if isinstance(inspect_out, dict):
            return int(inspect_out.get("exit", 0))
        return inspect_out

    did_something = False

    if args.gather:
        print("=== gather phase ===")
        run_gather(device_ip=args.device,
                   protocol=args.protocol or "mops")
        did_something = True

    if args.plan:
        print("=== plan generation ===")
        run_plan(scope=args.scope,
                 device_filter=args.device,
                 method_filter=args.method,
                 schema_filter=args.schema,
                 protocol_filter=args.protocol)
        did_something = True

    if args.execute:
        print("=== execute ===")
        run_execute(scope=args.scope,
                    device_filter=args.device,
                    method_filter=args.method,
                    schema_filter=args.schema,
                    protocol_filter=args.protocol,
                    kind_filter=args.kind)
        did_something = True

    if args.gate:
        print("=== full gate pipeline (gather → plan → execute → render) ===")
        run_gather(device_ip=args.device, protocol=args.protocol or "mops")
        run_plan(scope=args.scope,
                 device_filter=args.device,
                 method_filter=args.method,
                 schema_filter=args.schema,
                 protocol_filter=args.protocol)
        run_execute(scope=args.scope,
                    device_filter=args.device,
                    method_filter=args.method,
                    schema_filter=args.schema,
                    protocol_filter=args.protocol,
                    kind_filter=args.kind)
        run_render()
        did_something = True

    if args.render:
        print("=== render ===")
        run_render()
        did_something = True

    if args.resume:
        print("--resume — not yet implemented (deferred)")
        did_something = True

    # Surgical shortcut: --method or --schema without an explicit --plan
    # implies "regenerate plan with this filter, then execute it."
    if (args.method or args.schema) and not did_something:
        print("=== surgical (auto plan + execute) ===")
        run_plan(scope=args.scope,
                 device_filter=args.device,
                 method_filter=args.method,
                 schema_filter=args.schema,
                 protocol_filter=args.protocol)
        run_execute(scope=args.scope,
                    device_filter=args.device,
                    method_filter=args.method,
                    schema_filter=args.schema,
                    protocol_filter=args.protocol,
                    kind_filter=args.kind)
        did_something = True

    if not did_something:
        print("release_matrix.py — phase 0 build in progress")
        print("Available now: --reset, --db-info, --gather, --plan, --execute,")
        print("              --gate, --method/--schema/--device/--protocol")
        print("Coming soon: --render, --resume")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
