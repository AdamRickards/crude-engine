# Test bot — which proof lane

Branch this chart when a real object does not fit. Do not invent lanes.

```mermaid
flowchart TD
    Start[Verification requested] --> Q1{What kind of change?}
    Q1 -->|Docs-only| Skip[["generate_status.py --check\n+ check_catalogue.py"]]
    Q1 -->|Schema or wire, one method| Q2{Known-good anchor?}
    Q1 -->|Engine or shared primitive| Full["audit_getters.py --compare\nfull sweep"]
    Q1 -->|Matrix / CRUDE type transform| Matrix["test_crude_matrix.py\nprove | discover | all"]
    Q1 -->|MOPS/Offline kinship / expand floors| OfflineGold["offline_gold_matrix.py\nSTART Offline+XML; END mismatch-only fail"]
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

**Goal:** prove Offline (saved config / OfflineHIOS). Offline shares the MOPS
driver path, so a green prove is also kinship that MOPS gather shape works
against that config. Gold is not a second offline loader — it is the
**floor** (what should come back) and the mismatch catcher. Config prove
first, gold floor second; live sidecar is not required for this lane.

- **START:** schema method + Offline transport + saved mibconf XML
  (config = configured state = Offline’s literal intention). Named proof:
  `PYTHONPATH=. python3 tests/offline_gold_matrix.py` (optional bag
  `--config` / `--gold`; never commit identity — sanitized floors stay under
  `tests/fixtures/offline_gold/`).
- **WHERE WE ARE:** method coverage vs floors (committed sanitized vs
  bag-local), last proof counts, open `config_absent` followups. Expand
  floors method-by-method after the lane is named.
- **END:** receipt with classifications — real fail only on `mismatch`;
  `config_absent`∩gold = followup (oper/live not in NVM), not fail. Exit ≠ 0
  only on `mismatch`.

When: after MOPS/Offline client or FeatureEngine gather changes; when
expanding sanitized floors; before treating Offline as kinship-proof for
live MOPS.

