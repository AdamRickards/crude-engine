# crude-engine

**CRUDE — Canonical Representation Under Declarative Execution**

The vendor-agnostic engine that turns raw device truth (wire YAMLs) into clean, canonical data through three strict gates. Four protocols (MOPS, SNMP, SSH, Offline).

Built for Hirschmann HiOS industrial switches by Belden. Consumer-agnostic — adapters (NAPALM, gNMI, etc.) consume the engine's canonical output and reshape for their own spec.

## Architecture

No feature-specific Python. Wire YAMLs (generated from MIB) declare device truth. Schema YAMLs (human-authored) declare intent. The engine reads contracts, never sniffs data.

- **CRUDE methods**: **C**reate, **R**ead, **U**psert, **D**elete, **E**xecute — drop a YAML, the method exists
- **Three gates**: Schema Contract, Wire Contract, Encode/Decode
- **Four protocols**: MOPS (default, atomic writes), SNMPv3, SSH, Offline (config XML)
- **Canonical output** — schemas describe the device, not the consumer
- See [API_REFERENCE.md](docs/API_REFERENCE.md) for the full method and schema inventory

![The three-gate model](docs/Images/three-gates.svg)

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
device = driver('192.0.2.10', 'admin', 'private')  # HiOS factory defaults
device.open()
device.get_interfaces()   # canonical output
device.get_dns()          # 184 methods available
device.close()
```

### Discover available methods

```python
device.open()
caps = device.get_capabilities()
for operation in ['create', 'read', 'upsert', 'delete', 'execute']:
    print(f"{operation}: {caps['crude'][operation]}")
```

## Documentation

| Document | Contents |
|----------|----------|
| [status.html](docs/status.html) | Program poster — where we are, next task, proofs |
| [SEED.md](docs/program/SEED.md) | Why + how work is allowed to happen |
| [ROADMAP.md](docs/ROADMAP.md) | Versions and exit criteria (2.10 = first PyPI) |
| [TODO.md](docs/TODO.md) | Current cycle tasks |
| [METHOD_REFERENCE.md](docs/METHOD_REFERENCE.md) | Quick reference — methods, return keys, one line each |
| [API_REFERENCE.md](docs/API_REFERENCE.md) | Full reference — return schemas, per-protocol sources, wire detail |
| [SCHEMA_MODEL.md](docs/SCHEMA_MODEL.md) | Canonical schema contract — structural rules + shape rules |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Three-gate model, layer rules, data flow |
| [ENGINE_PRINCIPLES.md](docs/ENGINE_PRINCIPLES.md) | Operating principles — where new code goes |
| [SCHEMA_PRIMITIVES.md](docs/SCHEMA_PRIMITIVES.md) | Every YAML key — what it does, which gate handles it |
| [WIRE_SPEC.md](docs/WIRE_SPEC.md) | Wire YAML generation pipeline and format |
| [DIAGNOSTIC_PROCESS.md](docs/DIAGNOSTIC_PROCESS.md) | Mandatory ladder for fixing failing methods |

## Generators

```bash
# Offline proofs (no switch) — same script GitHub Actions will run
bash scripts/ci_offline.sh

# Regenerate API reference from schema + wire YAMLs
python3 local/generator/generate_docs.py

# Validate all schemas against the canonical model
python3 local/generator/validate_schemas.py

# Regenerate the program status page
python3 scripts/generate_status.py
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
# Getter audit against live device
python3 tests/audit_getters.py 192.0.2.10 --protocol mops

# All protocols
python3 tests/audit_getters.py 192.0.2.10 --protocol snmp
python3 tests/audit_getters.py 192.0.2.10 --protocol ssh
```

## License

Apache License 2.0 — see [LICENSE](LICENSE).
