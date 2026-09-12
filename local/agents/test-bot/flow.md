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

