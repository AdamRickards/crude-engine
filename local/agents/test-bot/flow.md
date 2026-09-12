# Test bot — which proof lane

Branch this chart when a real object does not fit. Do not invent lanes.

```mermaid
flowchart TD
    Start[Verification requested] --> Q1{What kind of change?}
    Q1 -->|Docs-only| Skip[["generate_status.py --check\n+ check_catalogue.py"]]
    Q1 -->|Schema or wire, one method| Q2{Known-good anchor?}
    Q1 -->|Engine or shared primitive| Full["audit_getters.py --compare\nfull sweep"]
    Q1 -->|Matrix / CRUDE type transform| Matrix["test_crude_matrix.py\nprove | discover | all"]
    Q1 -->|MOPS/Offline kinship / expand floors| OfflineGold["offline_gold_matrix.py\nOffline vs gold/config"]
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

## Offline vs gold (standing)

Run `PYTHONPATH=. python3 tests/offline_gold_matrix.py` after MOPS/Offline
client or FeatureEngine gather changes, when expanding sanitized floors, or
before treating Offline as kinship-proof for live MOPS. Optional
`--config` / `--gold` may point at a **local bag** NVM XML + floors for a
wider prove — never commit device identity; committed floors stay sanitized
under `tests/fixtures/offline_gold/`. Receipt: match / mismatch /
`config_absent` counts (`config_absent`∩gold = followup, not fail). Exit ≠ 0
only on real `mismatch`.

