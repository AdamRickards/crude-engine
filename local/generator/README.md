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
| GitHub issues | Leftover work (prove-then-file or comment-close). Not `docs/TODO.md`. |

## Optional read-only audits (retargeted at `crude_engine/`)

These are leftover v26 walks whose `BASE_DIR` was retargeted at this
repo's `crude_engine/{wire,schemas}`. They do not mutate YAML. They are
**not** live doc generators — do not treat their output as catalogue law.

| Audit | Output | What it reads |
|-------|--------|---------------|
| `validate_v26_all.py` | stdout | Schema→wire broken links + duplicate OIDs |
| `audit_wire.py` | `docs/WIRE_INTEGRITY.md` (only if you run it) | Wire protocol coverage + duplicate names |

Live schema law remains `validate_schemas.py` (CI).

## Leftover v26/monolith scripts (not live law)

These still hardcode `napalm-hios-v2` / `napalm_hios/` (or the old
`local/reference/webUI` / v1 `hios.py` / LocalUI tree). **Kept, not
deleted.** Do not heal/enrich/batch-generate against live YAML.
`batch_generate_MIB.py` may be invoked **isolated** into a TEMP outdir
for emit-diff only — never `crude_engine/wire`:

```bash
python3 local/generator/batch_generate_MIB.py --isolated --outdir /tmp/crude-mib-emit
```

| File | Why leftover |
|------|----------------|
| `batch_generate_MIB.py` | One-shot MIB→wire generator; not live law. Isolated `--outdir` only |
| `batch_generate_webui.py.stable` | Same class (sibling one-shot) |
| `heal_schemas.py` | Mutates schema `source:` against old webUI wires |
| `enrich_schema_v26.py` | Mutates `docs/napalm-hios-2-6-schema.md` |
| `cross_validate_v26.py` | v26 master-schema markdown vs webUI |
| `validate_schema_wire.py` | Post-heal check against `local/reference/webUI` |
| `audit_v26_coverage.py` | Needs v1 `hios.py` + shim `adapters/napalm.yaml` |
| `audit_v26_integrity.py` | Same + old webUI wires |
| `audit_web_coverage.py` | Needs machine-local LocalUI captures |
| `audit_claims.py` | Needs monolith `hios.py` adapter + v2.6 claim numbers |

`overrides.yaml` is data for the leftover MIB generator, not live law.

See [WIRE_SPEC.md](../../docs/WIRE_SPEC.md) for live wire format.