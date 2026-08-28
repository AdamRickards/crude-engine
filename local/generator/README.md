# crude-engine Generators

Tools that generate wire YAMLs from device truth and documentation from schema + wire YAMLs.

## Documentation Generators

All documentation in `docs/` that can be derived from the codebase SHOULD be generated, not hand-maintained. Run these after any schema, wire, or protocol YAML changes.

| Generator | Output | What it reads |
|-----------|--------|---------------|
| `generate_docs.py` | `docs/API_REFERENCE.md` | Schemas + wire + transport_registry. Full reference: return schemas, per-protocol source blocks, wire metadata |
| `generate_method_ref.py` | `docs/METHOD_REFERENCE.md` | Schemas + protocol YAMLs. Quick reference: one line per method, return keys, CRUDE type |
| `generate_protocols.py` | `docs/PROTOCOLS.md` | transport_registry + protocol YAMLs. Connection, config, execute methods, coverage |
| `validate_schemas.py` | stdout | Schemas + wire. Structural errors + canonical shape warnings |

### Usage

```bash
# Regenerate all docs
python3 local/generator/generate_docs.py
python3 local/generator/generate_method_ref.py
python3 local/generator/generate_protocols.py

# Validate schemas against the canonical model
python3 local/generator/validate_schemas.py
python3 local/generator/validate_schemas.py --canonical   # shape warnings only
python3 local/generator/validate_schemas.py --errors      # structural errors only
python3 local/generator/validate_schemas.py --json        # machine-readable
```

### What's generated vs hand-authored

| Document | Source |
|----------|--------|
| `docs/API_REFERENCE.md` | **Generated** by `generate_docs.py` |
| `docs/METHOD_REFERENCE.md` | **Generated** by `generate_method_ref.py` |
| `docs/PROTOCOLS.md` | **Generated** by `generate_protocols.py` |
| `docs/SCHEMA_MODEL.md` | **Authored** — formal spec, validated by `validate_schemas.py` |
| `docs/ARCHITECTURE.md` | **Authored** — three-gate model, layer rules |
| `docs/ENGINE_PRINCIPLES.md` | **Authored** — operating principles, block definitions |
| `docs/WIRE_SPEC.md` | **Authored** — wire generation pipeline |
| `docs/DIAGNOSTIC_PROCESS.md` | **Authored** — mandatory fault-finding ladder |
| `docs/SCHEMA_PRIMITIVES.md` | **Authored** — YAML key reference |
| `docs/ROADMAP.md` | **Authored** — milestones |
| `docs/TODO.md` | **Authored** — work items |

## Wire Generators

Tools that produce wire YAMLs from MIB/MOPS device truth.

| Generator | Output | What it reads |
|-----------|--------|---------------|
| `batch_generate_MIB.py` | `local/reference/webUI/*.yaml` | MIB XML (`local/reference/MOPS/mops_hios.xml`) + optional WebUI captures |

### Wire Generation Pipeline

```bash
# Step 1: Generate wire YAMLs from MIB
python3 local/generator/batch_generate_MIB.py

# Step 2: Map schemas to generated wires
python3 local/generator/heal_schemas.py

# Step 3: Audit integrity
python3 local/generator/validate_v26_all.py
```

See the [WIRE_SPEC.md](../../docs/WIRE_SPEC.md) for format details.

## Other Tools

| Tool | Purpose |
|------|---------|
| `heal_schemas.py` | Remap schema `source:` fields to MIB-named wire files |
| `cross_validate_v26.py` | Validate generated YAMLs against schema contract |
| `validate_v26_all.py` | Full broken-link + duplicate OID audit |
| `audit_claims.py` | Audit v2.6 coverage claims against wire reality |
| `audit_wire.py` | Wire-level integrity checks |
| `overrides.yaml` | Manual corrections for generator output (create_method, type) |
