# Effort board — tangible goals (bubbles)

Owned by Architect. Lives **in this repo** under `local/agents/` so HITL can
open it on GitHub anytime. Chart first: when HITL names a multi-session goal,
update this board before (or as) clerks spin. Children are GitHub issues.
Chat is signal, not storage.

## Live bubbles (update in PRs — not only in chat)

| Bubble | Status | Children |
| --- | --- | --- |
| **A** Offline↔gold floor growth | **DONE** floors=50 | #169 closeout; unfloorables → #193 |
| **A′** Live MOPS triad (gold / config Offline / live) | **OPEN** | not started |
| **B** Generator → SNMP vs MOPS known-good | **IN PROGRESS** | #162 reopened; Docs re-emit |
| **C** SSH after two good floors | **BLOCKED** | #92 budgets; #41 banner live; #178 get_aca SSH |

```mermaid
flowchart TD
  HITL["HITL idea / discussion"] --> E["Update this Effort board MD"]
  E --> Split["Split into child GitHub issues\nnamed proof each"]
  Split --> A["A Offline↔gold floors\nDONE 50 / #193 look-into"]
  Split --> Ap["A′ Live MOPS triad\nOPEN"]
  Split --> B["B Generator→SNMP\n#162 IN PROGRESS"]
  Split --> C["C SSH after two floors\nBLOCKED"]
  A --> Re["Recombine: update WHERE here\nthen park or open next bubble"]
  Ap --> Re
  B --> Re
  C --> Re
```

## Rules

- Tangibility: if it is not on GitHub in this folder (or a child issue), it is not the Effort.
- Architect updates this file when a bubble splits, greens, or blocks.
- Six clerks only; Architect holds the board and assigns hops.
- No lab identity on GitHub.
