# SEED — why this project exists and how work is allowed to happen

Stable. Change rarely. Everything else (roadmap, cycle, docs, CI) is a rendering of this.

## Destination

A **typed, enumerable, self-describing capability surface** for Hirschmann HiOS (then any device with a formal interface description).

YAML declares. Python executes. No decisions in code.

The engine is the commodity. **The contracts are the product.**

First public artifact: **crude-engine 2.10.0 on PyPI**, with MOPS + SNMP verified through the napalm-hios adapter by the release matrix.

## Non-goals (until 2.10 ships)

- Tools inversion (CLAMPS contracts)
- NILS graph / arbitration
- gNMI, HiSecOS, Modbus, SSH as a 1st-class citizen
- Anticipated frameworks

Those live on the roadmap as later versions. They do not steal cycles from the catalogue.

## How an idea becomes work

```
SEED                 why / destination / bans          (this file)
  → ROADMAP          versions + exit criteria          (docs/ROADMAP.md + program/roadmap.yaml)
    → cycle          this iteration's tasks            (program/cycles.yaml → docs/TODO.md)
      → proof        a command that fails when wrong   (scripts/ + matrix)
        → status     human HTML + machine JSON         (docs/status.html)
```

A task without a **proof** is not a task. "Verified: correct" in prose is not a proof.

## Rules

1. **Brain is the repo.** GitHub is the host (CI, releases, Issues as a *presenter*). Issues are not the source of truth.
2. **Tight proofs, loose instructions.** The agent may take any route that survives the check.
3. **Extract before generate.** Contracts from working code, not from vision.
4. **Failure changes the spec**, not just the Python. If the generated page is wrong, fix the generator or the schema — do not patch the markdown.
5. **Regenerate by default.** Incremental doc edits drift.
6. **Lab truth ≠ PR truth.** Offline CI must stay green without a switch. The matrix is the release gate and runs on the fleet.
7. **One cycle at a time.** Finish or park. Do not open a second inversion.

## Host decision

**GitHub.** Already named in `setup.py`. Already has a PyPI publish workflow. Issues, Actions, Releases, and Pages are enough. Do not add Gitea, Linear, or a task SaaS as a second brain.

Until `git init` + remote exist, the same files work locally: `scripts/ci_offline.sh` is what Actions will call.

## Next file

[METHOD.md](METHOD.md) — how to pick the next task and close it.
