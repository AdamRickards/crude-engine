# NAPALM HiOS Driver (v2)

NAPALM driver for Hirschmann HiOS industrial switches by Belden. YAML-driven declarative engine — four protocols (MOPS, SNMP, SSH, Offline), three-gate architecture, 174 methods across 45 schemas.

## Architecture

Declarative YAML engine — no feature-specific Python. Wire YAMLs (generated from MIB) declare device truth. Schema YAMLs (human-authored) declare intent. The engine reads contracts, never sniffs data.

- **174 methods**: 16 Create, 78 Read, 64 Upsert, 16 Delete
- **45 schema YAMLs** — drop a YAML, the method exists
- **Three gates**: Schema Contract (SchemaContext), Wire Contract (WireContext), Encode/Decode (dispatch_batch/gather_and_decode)
- **Four protocols**: MOPS (default, atomic writes), SNMPv3, SSH, Offline (config XML files)

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full three-gate model, layer rules, and data flow.

## Installation

```
pip install napalm-hios
```

## Quick Start

```python
from napalm import get_network_driver

driver = get_network_driver('hios')

# Default: MOPS (HTTPS, atomic writes, no SNMP dependency)
device = driver('192.168.1.4', 'admin', 'private')

# Or force a specific protocol:
# device = driver('192.168.1.4', 'admin', 'private',
#                 optional_args={'protocol_preference': ['snmp']})

device.open()
print(device.get_facts())
print(device.get_interfaces())
device.close()
```

## Documentation

| Document | Contents |
|----------|----------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Three-gate model, layer rules, data flow, public API |
| [docs/SCHEMA_PRIMITIVES.md](docs/SCHEMA_PRIMITIVES.md) | Every YAML key — what it does, which gate handles it |
| [docs/DIAGNOSTIC_PROCESS.md](docs/DIAGNOSTIC_PROCESS.md) | Mandatory ladder for fixing failing methods |
| [docs/WIRE_SPEC.md](docs/WIRE_SPEC.md) | Wire YAML generation pipeline and format |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Project milestones and future work |
| [docs/usage.md](docs/usage.md) | Standard NAPALM methods — arguments, return values, examples |
| [docs/vendor_specific.md](docs/vendor_specific.md) | Vendor methods — MRP, RSTP, CRUD, factory lifecycle |
| [docs/protocols.md](docs/protocols.md) | Protocol details — MOPS/SNMP/SSH config, cross-protocol diffs |

> **TODO**: `usage.md`, `vendor_specific.md`, `protocols.md` — auto-generate from schema YAMLs + API introspection as part of release pipeline.

## Protocol Support

Default order: MOPS → SNMP → SSH. Override with `protocol_preference` in `optional_args`.

| Protocol | Transport | Auth | Atomic Write | Dependencies |
|----------|-----------|------|--------------|-------------|
| **MOPS** | HTTPS 443 | HTTP Basic | Yes (single POST) | `requests` |
| **SNMP** | UDP 161 | SNMPv3 authPriv (MD5/DES) | No | `pysnmp` |
| **SSH** | TCP 22 | Password | No | `netmiko` |
| **Offline** | XML file | None | N/A (file) | None |

## Testing

```bash
# Getter audit against live device (78 methods)
python3 tests/audit_getters.py 192.168.60.80

# Replay tests (offline, from captured fixtures)
pytest tests/test_replay.py -v
```

## Contributing

Issues and PRs welcome at [GitHub](https://github.com/AdamRickards/napalm-hios). Driver tested against BRS50 and GRS1042 hardware. If you have a HiOS device and find a bug, include firmware version and getter output.

## License

Apache License 2.0 — see [LICENSE](LICENSE).
