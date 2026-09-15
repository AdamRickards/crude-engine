# ROADMAP — crude-engine

Curated. Destination + bot process law: `local/agents/README.md`.
Effort progress: `local/agents/diagrams/effort-board.md`.

**Now:** 2.9.0 shipped as architecture.
**Next:** 2.10.0 first PyPI.
**Host:** GitHub (`AdamRickards/crude-engine`).

---

## #release #v2.10.0 — First PyPI

**Citizens:** MOPS + SNMP via napalm-hios.
**SSH / Offline:** post-release unless a matrix run promotes them.

### Exit criteria

| ID | Lane | Proof | Why |
|----|------|-------|-----|
| `catalogue-honest` | offline | `scripts/check_catalogue.py` | The page is the product. It must not say `0E` or `Protocols: None` on a live method. |
| `schema-musts` | offline | `validate_schemas.py --errors` | Stated invariants decay. Checked ones don't. |
| `principles-grep` | offline | `scripts/check_principles.py` | `if protocol ==` and `except Exception: pass` stay banned. |
| `parity-gate` | lab | `release_matrix.py --execute --kind parity --render` | 145 blocking cells (2026-04-14), almost all `#SNMP-Compound-Index-Decode`. |
| `setter-crud-fleet` | lab | `--kind setter` then `--kind crud` | Read path green ≠ write path proven. |
| `docs-curated` | offline | `generate_status.py --check` | Agents Destination + Effort board + ROADMAP present. Leftovers live on GitHub issues. |

Gate definition (unchanged): every in-scope method has a verified MOPS and SNMP verdict. Truth from execution, not prose.

Version number: **2.10.0** (not a 1.0 reset). 2.9 already exists in the package.

### Current focus — honest catalogue + Effort board

Offline proofs first. Live progress: `local/agents/diagrams/effort-board.md`.
Leftover work is GitHub issues.

---

## #roadmap #v2.11.0 — SSH + Offline

Promote or park with exemptions after 2.10.

- `#driver` SSH parsers still untrusted until the matrix re-verifies
- `#release #Offline-1st-Class` — one real matrix run decides

## #roadmap #v3.0.0 — Second OS or transport

HiSecOS wire pack and/or Modbus. Additive. Same engine.
Claim is "any device with a formal interface description," not "any vendor."

## #roadmap #later — not this product's critical path

gNMI shim. Tools inversion (CLAMPS contracts). NILS. Separate seeds, separate repos or later packages.

---

## What will not be a version

- Interpreter line-count reduction
- Rewriting `compute.expr` to ban `if/else`
- Anticipated `crude-tools-common`
- Moving NAPALM reshapes back into the engine
