# crude-engine

**CRUDE — Canonical Representation Under Declarative Execution**

The vendor-agnostic engine that turns raw device truth (wire YAMLs) into clean, canonical data through three strict gates. Four protocols (MOPS, SNMP, SSH, Offline), 184 methods across 45 schemas.

Built for Hirschmann HiOS industrial switches by Belden. Consumer-agnostic — adapters (NAPALM, gNMI, etc.) consume the engine's canonical output and reshape for their own spec.

## Architecture

No feature-specific Python. Wire YAMLs (generated from MIB) declare device truth. Schema YAMLs (human-authored) declare intent. The engine reads contracts, never sniffs data.

- **184 CRUDE methods**: 16 **C**reate, 78 **R**ead, 64 **U**psert, 16 **D**elete, 10 **E**xecute
- **45 schema YAMLs** — drop a YAML, the method exists
- **Three gates**: Schema Contract, Wire Contract, Encode/Decode
- **Four protocols**: MOPS (default, atomic writes), SNMPv3, SSH, Offline (config XML)
- **Canonical output** — schemas describe the device, not the consumer

## Installation

```
pip install crude-engine
```

For NAPALM integration: `pip install napalm-hios` (installs crude-engine as a dependency).

## Usage

### Direct (engine API)

```python
from crude_engine import FeatureEngine

engine = FeatureEngine()
# ... connect transport, resolve intent, execute
```

### Via NAPALM adapter

```python
from napalm import get_network_driver

driver = get_network_driver('hios')
device = driver('192.168.1.4', 'admin', 'private')
device.open()
device.get_interfaces()   # canonical output
device.get_dns()          # 184 methods available
device.close()
```

### Discover available methods

```python
device.open()
caps = device.get_capabilities()
print(caps['crude']['create'])     # 16 Create
print(caps['crude']['read'])      # 78 Read
print(caps['crude']['upsert'])    # 64 Upsert
print(caps['crude']['delete'])    # 16 Delete
print(caps['crude']['execute'])   # 10 Execute
```

## Documentation

| Document | Contents |
|----------|----------|
| [METHOD_REFERENCE.md](docs/METHOD_REFERENCE.md) | Quick reference — 184 methods, return keys, one line each |
| [API_REFERENCE.md](docs/API_REFERENCE.md) | Full reference — return schemas, per-protocol sources, wire detail |
| [SCHEMA_MODEL.md](docs/SCHEMA_MODEL.md) | Canonical schema contract — structural rules + shape rules |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Three-gate model, layer rules, data flow |
| [ENGINE_PRINCIPLES.md](docs/ENGINE_PRINCIPLES.md) | Operating principles — where new code goes |
| [SCHEMA_PRIMITIVES.md](docs/SCHEMA_PRIMITIVES.md) | Every YAML key — what it does, which gate handles it |
| [WIRE_SPEC.md](docs/WIRE_SPEC.md) | Wire YAML generation pipeline and format |
| [DIAGNOSTIC_PROCESS.md](docs/DIAGNOSTIC_PROCESS.md) | Mandatory ladder for fixing failing methods |
| [ROADMAP.md](docs/ROADMAP.md) | Milestones and future work |
| [TODO.md](docs/TODO.md) | Current work items |

## Generators

```bash
# Regenerate API reference from schema + wire YAMLs
python3 local/generator/generate_docs.py

# Validate all schemas against the canonical model
python3 local/generator/validate_schemas.py
```

## Protocol Support

Default order: MOPS > SNMP > SSH. Override with `protocol_preference` in `optional_args`.

| Protocol | Transport | Auth | Atomic Write | Dependencies |
|----------|-----------|------|--------------|-------------|
| **MOPS** | HTTPS 443 | HTTP Basic | Yes (single POST) | `requests` |
| **SNMP** | UDP 161 | SNMPv3 authPriv (MD5/DES) | No | `pysnmp` |
| **SSH** | TCP 22 | Password | No | `netmiko` |
| **Offline** | XML file | None | N/A (file) | None |

## Testing

```bash
# Getter audit against live device (78 methods)
python3 tests/audit_getters.py 192.168.1.4 --protocol mops

# All protocols
python3 tests/audit_getters.py 192.168.1.4 --protocol snmp
python3 tests/audit_getters.py 192.168.1.4 --protocol ssh
```

## License

Apache License 2.0 — see [LICENSE](LICENSE).
