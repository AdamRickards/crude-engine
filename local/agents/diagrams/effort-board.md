# Effort board — tangible goals (bubbles)

Owned by Architect. Lives **in this repo** under `local/agents/` so HITL can
open it on GitHub anytime. Chart first: when HITL names a multi-session goal,
update this board before (or as) clerks spin. Children are GitHub issues.
Chat is signal, not storage.

**Living floors glance + Σ coverage rollup (generated SoT):** [`docs/FLOORS_BOARD.md`](../../../docs/FLOORS_BOARD.md) — `python3 scripts/generate_floors_board.py` (never hand-edit). Loop chart: [`resolution-loop.md`](resolution-loop.md).

## What an Effort is

1. **Goal** — multi-session, broadly named (not a single PR).
2. **Finished looks like** — concrete enough to say yes/no without re-arguing.
3. **Poke loop** — Architect/clerks keep opening small issues, PRs, and named
   proofs until finished-looks-like is true (or HITL parks it). Middle may be
   wrong; start and end stay fixed.

Chat names the Effort once. The board + child issues *are* the Effort after that.

## Live bubbles (update in PRs — not only in chat)

| Bubble | Status | Children |
| --- | --- | --- |
| **Σ** Coverage end-game | **IN PROGRESS** | Every floored method×protocol → `pass` (or HITL exception). Glance+rollup: `docs/FLOORS_BOARD.md`. Loop: `resolution-loop.md`. HITL source: `architect/resolution-methodology.md` (#287). Lanes A′/B/C **feed** Σ. |
| **A** Offline↔gold floor growth | **DONE** floors=**52** | #169 trail; unfloorables → #193 (poe status-null + route_to); merge #257 `3ca9974` (#258 closed duplicate) |
| **A′** Live MOPS triad (gold / Offline / live) | **IN PROGRESS** | #229 — floored MOPS receipts done (49/49 class); look-intos as filed |
| **B** Generator → SNMP vs MOPS known-good | **IN PROGRESS** | #162 **closed**; residuals **#205**; Schema #233–#235 **closed**; #231→#12 parked; TC-BITS parked — see `hitl-engine-park.md` |
| **C** SSH after two good floors | **SOFT** | Timeout detection done; **#92 stays closed**. Open soft: #226 #227 #228 #217 #178 #62; **#272** + **last_cli** Engine park; Rank1 #226/#285 soft win. Check **9** SSH floor ladder. Prefer A′/B over stalling. |

```mermaid
flowchart TD
  HITL["HITL idea / discussion"] --> E["Update this Effort board MD"]
  E --> Split["Split into child GitHub issues\nnamed proof each"]
  Split --> Sig["Σ Coverage end-game\nFLOORS_BOARD rollup"]
  Split --> A["A Offline↔gold floors\nDONE 52 / #193 look-into"]
  Split --> Ap["A′ Live MOPS triad\nIN PROGRESS"]
  Split --> B["B Generator→SNMP\n#205 residuals"]
  Split --> C["C SSH after two floors\nSOFT"]
  A --> Sig
  Ap --> Sig
  B --> Sig
  C --> Sig
  Sig --> Re["Recombine: update WHERE here\nCreate→Execute→Resolve"]
```

## Rules

- Every open issue hangs on this board, companion #195, or `hitl-engine-park.md` — fold orphans in; do not leave silent backlog.
- Companion issue [#195](https://github.com/AdamRickards/crude-engine/issues/195) mirrors this table — update **both** in one hop when bubbles change.
- HITL/Engine park lives in `hitl-engine-park.md` (not duplicated as a Coverage child).
- **Σ** is the end-game progress bar; **R** in the fold-in table remains Release/RC (different letter, different bucket).
- Tangibility: if it is not on GitHub in this folder (or a child issue), it is not the Effort.
- Architect updates this file when a bubble splits, greens, or blocks.
- Six clerks only; Architect holds the board and assigns hops.
- No lab identity on GitHub.


## Tracked outside floors Effort (fold-in 2026-09-14)

Every open issue must hang on this board or `hitl-engine-park.md`. These were open but unnamed; reprocessed under current mechanics (no seventh clerk; soft hops vs Engine/HITL park).

| Bucket | Status | Children |
| --- | --- | --- |
| **R** Release / RC | **PARKED** — needs HITL `--gate` | #14 setter/CRUD matrix (260 jobs). Not a floors poke; Architect does not close release without hand-back. |
| **L** Lab / fixture capture | **PARKED** — HITL | #110 multi-device leftover fixture trees (office L3 vs other profiles). No lab identity on GitHub. |
| **F** Feature gap (webUI tab) | **INVENTORY DONE** | #129 → proposed `get_egress_shaping` (ask map on issue); implement when ordered; not A′/B blocker. |
| **T** Tooling | **SOFT** | #156 honour `debug=foreign` / `trace=engine` (post #155). Docs/Engine soft when free; not floors-critical. |

Engine cycle-0 that need primitives or checker work live on **`hitl-engine-park.md`**: #30 SNMPHIOS.close tax; #115 `to_bool` false-vocab; #116 `sort:natural` port heuristic — plus existing #12/#68/#106 rows.

## Finished looks like (this board)

| Bubble | Finished looks like |
| --- | --- |
| **Σ** | Coverage rollup → 100% of *possible* (gold rows × offline/mops/snmp/ssh), or every shortfall is an explicit HITL exception with evidence — no silent gaps. Loop never “ends the product”; it only ends *this* board when that count is true. |
| **A** | Offline↔gold floor growth done for floorable methods; unfloorables filed — **met** (52 floors, #193) |
| **A′** | MOPS + Offline proved against Gold, Config/XML Offline, and Live (named sweeps; look-into list exists) |
| **B** | Generator emit≈live for teachable residuals; SNMP meets MOPS known-good floor on named proves |
| **C** | SSH leftovers worked only after A′+B floors hold; timeout *detection* done (#179–#225); #92 stays closed; parse/parity soft backlog includes older fold-ins |
