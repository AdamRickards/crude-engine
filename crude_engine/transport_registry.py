"""
Transport & driver registry — single source of truth for protocol mappings.

This module owns the mapping between protocol names and their transport,
driver, protocol YAML, wire overlay, engine protocol, and connection args.
No protocol-specific imports or file paths leak into higher layers.
"""

import os

_cache = {}

PROTOCOLS = {
    "mops": {
        "driver": "crude_engine.drivers.mops_driver.MOPSDriver",
        "transport": "crude_engine.drivers.mops_transport.MOPSHIOS",
        "protocol_yaml": "MOPS.yaml",
        "engine_protocol": "mops",
        "port_key": "mops_port",
        "default_port": 443,
    },
    "snmp": {
        "driver": "crude_engine.drivers.snmp_driver.SNMPDriver",
        "transport": "crude_engine.drivers.snmp_transport.SNMPHIOS",
        "protocol_yaml": "SNMP.yaml",
        "engine_protocol": "snmp",
        "port_key": "snmp_port",
        "default_port": 161,
    },
    "ssh": {
        "driver": "crude_engine.drivers.ssh_driver.SSHGatherDriver",
        "transport": "crude_engine.drivers.ssh_transport.SSHDriver",
        "protocol_yaml": "SSH.yaml",
        "engine_protocol": "ssh",
        "wire_overlay_dir": "ssh",
        "port_key": "ssh_port",
        "default_port": 22,
    },
    "offline": {
        "transport": "crude_engine.drivers.offline_hios.OfflineHIOS",
        "protocol_yaml": "MOPS.yaml",
        "engine_protocol": "mops",
    },
}

# Default connection order (excludes offline — that's auto-detect only)
DEFAULT_PREFERENCE = [p for p in PROTOCOLS if p != "offline"]

# Backward-compat flat registries (derived from PROTOCOLS)
REGISTRY = {k: v["transport"] for k, v in PROTOCOLS.items() if "transport" in v}
DRIVER_REGISTRY = {k: v["driver"] for k, v in PROTOCOLS.items() if "driver" in v}


def _resolve(dotted):
    """Lazy-import a dotted class path. Cached."""
    if dotted in _cache:
        return _cache[dotted]
    module_path, class_name = dotted.rsplit(".", 1)
    import importlib
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    _cache[dotted] = cls
    return cls


def get_transport_class(protocol):
    """Return the transport class for a protocol."""
    entry = PROTOCOLS.get(protocol)
    if not entry or "transport" not in entry:
        raise ValueError(f"Unknown protocol: {protocol}")
    return _resolve(entry["transport"])


def get_driver_class(protocol):
    """Return the gather/set driver class for a protocol."""
    entry = PROTOCOLS.get(protocol)
    if not entry or "driver" not in entry:
        raise ValueError(f"Unknown driver protocol: {protocol}")
    return _resolve(entry["driver"])


def get_engine_protocol(protocol):
    """Return the engine protocol name (wire source resolution)."""
    entry = PROTOCOLS.get(protocol)
    if not entry:
        raise ValueError(f"Unknown protocol: {protocol}")
    return entry.get("engine_protocol", protocol)


def get_connect_port(protocol, optional_args=None):
    """Return the connection port from optional_args or protocol default."""
    entry = PROTOCOLS.get(protocol, {})
    port_key = entry.get("port_key")
    default = entry.get("default_port")
    if port_key and optional_args:
        return optional_args.get(port_key, default)
    return default


def get_wire_overlay_dir(protocol):
    """Return the wire overlay subdirectory for a protocol, or None."""
    entry = PROTOCOLS.get(protocol)
    if not entry:
        return None
    return entry.get("wire_overlay_dir")


def get_protocol_yaml_path(protocol):
    """Return the absolute path to the protocol YAML for a protocol."""
    entry = PROTOCOLS.get(protocol)
    if not entry or "protocol_yaml" not in entry:
        return None
    drivers_dir = os.path.join(os.path.dirname(__file__), "drivers")
    return os.path.join(drivers_dir, entry["protocol_yaml"])
