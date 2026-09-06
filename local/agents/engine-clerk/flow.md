# Engine clerk — decision flow

Same ladder as `docs/DIAGNOSTIC_PROCESS.md`, as a tree. Most symptoms exit
before step 7. Branch this chart when a real object does not fit.

Pipeline trace is `trace=True`, not `debug=True`.

```mermaid
flowchart TD
    Start[Symptom reported] --> S1[Step 1: compare to a passing sibling]
    S1 --> Q1{Shape mismatch vs sibling\nexplains it?}
    Q1 -->|Yes| Exit1[["YAML contract. Schema/wire clerk."]]
    Q1 -->|No| S2[Step 2: inspect with trace=True]
    S2 --> S3[Step 3: inspect with --no-validate]
    S3 --> Q3{Works with validate off?}
    Q3 -->|Yes| Exit3[["Gate declaration wrong. Schema/wire clerk."]]
    Q3 -->|No| S4[Step 4: wire audit — MIB / MOPS / CLI_REFERENCE]
    S4 --> S5[Step 5: ask 1.17 clerk — does an anchor exist?]
    S5 -->|No anchor| Exit5a[["NO_HOLE. Establish an anchor first.\nDo not guess."]]
    S5 -->|Anchor exists| Q5{Anchor says engine gap,\nnot wire?}
    Q5 -->|No — wire| Exit5b[["Wire fix. Schema/wire clerk."]]
    Q5 -->|Yes| S7{Step 7: existing meaning?\n>= 2 features, YAML cannot declare it away}
    S7 -->|Declare in YAML instead| Exit7[["Schema clerk. Not engine."]]
    S7 -->|Would be a NEW primitive / rule| ExitL[["LOGIC. HITL.\nDo not invent meaning."]]
    S7 -->|Bug vs existing meaning| Draft[Smallest engine diff that makes the declared behaviour true]
    Draft --> Sweep[audit_getters.py --compare vs last-known-good]
    Sweep --> Q8{Receipt?}
    Q8 -->|Regression| Draft
    Q8 -->|Sweep did not run — infra| Infra[["BLOCKED. Not pass, not fail."]]
    Q8 -->|Green| Gate[["HITL sign-off. Always, no exception —\nsweep receipt + one-line why-existing-meaning,\nnot a case-file essay. Not a Bot's call."]]
    Gate --> L[Implement. Done.]
    L --> H1[Test bot: fixture capture/update]
    L --> H2[Docs clerk: DIAGNOSTIC_PROCESS / ARCHITECTURE now stale?]
```
