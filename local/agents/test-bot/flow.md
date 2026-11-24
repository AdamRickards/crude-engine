# Test bot — which proof lane

Branch this chart when a real object does not fit. Do not invent lanes.

```mermaid
flowchart TD
    Start[Verification requested] --> Q1{What kind of change?}
    Q1 -->|Docs-only| Skip[["generate_status.py --check\n+ check_catalogue.py"]]
    Q1 -->|Schema or wire, one method| Q2{Known-good anchor?}
    Q1 -->|Engine or shared primitive| Full["audit_getters.py --compare\nfull sweep"]
    Q1 -->|Matrix / CRUDE type transform| Matrix["test_crude_matrix.py\nprove | discover | all"]
    Q1 -->|MOPS/Offline kinship / expand floors| OfflineGold["offline_gold_matrix.py\nCI gate: Offline+gold; END mismatch fail"]
    Q2 -->|No anchor| Anchor[["NO_HOLE for 1.17 / HITL.\nDo not verify against a guess."]]
    Q2 -->|Fixture with verified_via| Replay["test_replay.py"]
    Q2 -->|Manual WebUI/CLI, not captured| Inspect["sidecar / release_matrix.py --inspect\nthen capture fixture + verified_via"]
    Replay --> Q3{Receipt?}
    Inspect --> Q3
    Skip --> Q3
    Matrix --> Q3
    OfflineGold --> Q3
    Q3 -->|Fail| Back[["Back to owning clerk with the diff."]]
    Q3 -->|Pass| Q4{Touches a shared primitive?}
    Q4 -->|Yes or unsure| Full
    Q4 -->|No| Done[["Verified. Fixture + verified_via if live."]]
    Full --> Q5{Sweep receipt?}
    Q5 -->|Regression| Back
    Q5 -->|Sweep did not run — infra| Infra[["BLOCKED. Not pass, not fail."]]
    Q5 -->|Clean| Done
```

## Offline vs gold (standing) — CI/CD gate

**Purpose / END:** gate MOPS/Offline changes. Offline prove vs saved config +
gold floors = kinship that MOPS gather shape holds. Gold is the **floor**
(mismatch catcher), not a second loader. Live sidecar not required for this
lane. Prove the tool **by using it** (fuller sweeps); sweep feedback →
look-into list (issues later). If the harness breaks: issue → temp fix →
prove → PR → merge.

- **START:** schema gather method(s) + Offline + mibconf XML. Named proofs:
  - CI / sanitized: `PYTHONPATH=. python3 tests/offline_gold_matrix.py`
    (DEFAULT_METHODS = floored set). Optional `--methods` catalogue-wide
    for stress (missing floors → `gold_absent` feedback, not fail).
  - Bag-local (optional, never CI identity): `--config` / `--gold` against
    a local bag NVM + bag gold. Committed floors stay under
    `tests/fixtures/offline_gold/`.
- **WHERE WE ARE:** floored coverage vs catalogue; last sanitized + bag
  counts; look-into list (`gold_absent`, `config_absent` followups,
  `offline_empty`, mismatches, blocked). Improve this section when
  good/bad/ugly hits (what is CI vs bag-only).
- **END:** receipt — fail only on `mismatch` (exit ≠ 0). `config_absent`∩gold
  = oper/live followup, not fail. `gold_absent` = missing floor (feedback).
  Gate-ready for CI when floored DEFAULT_METHODS stay green on sanitized
  fixtures after MOPS/Offline/FeatureEngine gather changes.

When: after MOPS/Offline client or FeatureEngine gather changes; expanding
floors; catalogue stress sweeps; before treating Offline as kinship for live
MOPS.


## Call-timeout resolution (standing) — after phase attribution

**Purpose / END:** when inspect reports `status=timeout` with
`phase=call` (or `phase=open`), **classify why** and route — do not stop
at "still timeout under budgets." Chart:
[`../diagrams/inspect-timeout.md`](../diagrams/inspect-timeout.md).

**START (every timeout leftover):**

1. Quote per-protocol `status`, `phase`, `open_ms`, `call_ms`, budgets from
   `tests/inspect.yaml`. `trace:true` on the named read.
2. **Split on phase** (finder from `#179`):
   - `phase=open` → open path (login/prompt/budget). Park as `#92` class
     until fail-fast HITL. Do not Schema-fake an overlay.
   - `phase=call` → continue this ladder (call path).
3. **Declared CLI inventory** (required on call-timeout — hang often has
   **no** `cli` in the receipt): from `crude_engine/wire/ssh/` for this
   method, list every **read** `command:`. Count distinct shows vs
   `{index}` / per-row fanouts.
4. **CLI.json cross-check** (`local/reference/CLI/cli_ref_hios_merged.json`
   + `CLI_REFERENCE.md`): does each base `show …` exist? Any invented
   spelling? Literal placeholder tokens?
5. **Bucket** (one glance line on the issue — see diagram table):
   `open-budget` | `call-budget-fanout` | `call-invalid-cmd` |
   `call-unknown-hang` | `timeout-cleared-parse`.
6. **Route** (Architect multiplexes; Test bot does not fix):
   - fanout / wrong CLI spelling → Schema (overlay honesty).
   - invalid hang / fail-fast redefine → `#92` HITL (user eyes).
   - unknown hang after inventory → trail + optional Engine `NO_HOLE`
     for harness `last_command` heartbeat on timeout.
   - timeout cleared, parse/shape wrong → close timeout intention; one
     SSH remainder ticket (standing SSH-split law).

**WHERE WE ARE:** learn by repeating this poke on each call-timeout
leftover; wrong bounce feeds the chart; right bounce is obvious on the
decision trail.

**END:** decision-trail comment with bucket + declared command list +
CLI.json hit/miss + route. Green only when live receipt clears *this*
leftover's intention — not when budgets alone move.

**Never:** author the fix; treat pre-`#179` "overall deadline" null timings
as the same as phase-attributed call; skip CLI.json because mops/snmp
were ok (finder, not a vote).


## SSH remainder (standing) — after timeout cleared

When call-timeout is cleared but parse/shape/`n` misses the shared floor:
Architect orchestration **check 9** (`../architect/INSTRUCTIONS.md`) —
prove CLI.json / overlay guesses vs device-proved **MOPS floor**; not
2-of-3; do not reopen `#92`.

## Create vs Execute (Σ Coverage — Architect check 10)

Do not conflate jobs (HITL #287 distill / `diagrams/resolution-loop.md`):

| Job | Test bot does | Does not |
| --- | --- | --- |
| **Create** | Own Tier-1/2 capture→fixture when ordered (`tests/capture.py` Tier 1; sidecar Tier 2 for `test_napalm` only) | Invent expected values; use sanitized `gold_floors.json` as tap fixture |
| **Execute** | Run named proves / matrix / offline_gold / sidecar inspect; file disagreements | Fix YAML or engine |
| **Resolve** | Re-prove a clerk's tip vs floor | Author the fix |

**Tier 1** (`test_engine` / tap1+tap3): direct capture — sidecar never exposes MOPS/SNMP tap1 raw. **Tier 2** (`test_napalm`): sidecar OK; fixture dirs keyed by sidecar `label`, never IP.

FLOORS_BOARD ssh/mops/… cells thicken only from honest Execute receipts into `floors_provenance.json`.

