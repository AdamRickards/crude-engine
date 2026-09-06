# Conform — known state → finished state

The smash loop once live devices are reachable. Nested, ordered, always against a
HITL-agreed value — never three protocols agreeing with each other.

```
for each method in schema:
  for each CRUDE op the method declares (read first; C/U/D/E only after read floor):
    1. MOPS  — HITL baseline (WebUI / 1.17). This is the floor.
    2. SNMP  — conform to that MOPS value (generated wire: type, lookup, index).
    3. SSH   — same floor. Classify miss: wire | driver | engine/primitive.
```

Two known goods after step 1: the MOPS receipt **and** 1.17/WebUI. SNMP and
SSH steer toward those, not toward each other.

```mermaid
flowchart TD
    M[Next method × CRUDE op] --> R{Read floor exists for this method?}
    R -->|No, and this op is C/U/D/E| Wait[["Skip writes until read floor.\nDo not CRUD against a guess."]]
    R -->|Yes, or this is a read| Mops[MOPS live inspect]
    Mops --> H{HITL / 1.17 agrees with MOPS?}
    H -->|No — MOPS wrong vs WebUI/CLI| FixM[["Schema/wire MOPS until it matches the anchor.\nDo not 'fix' 1.17 to match MOPS."]]
    FixM --> Mops
    H -->|No anchor yet| A[["1.17 clerk / HITL. NO_HOLE until a floor exists."]]
    H -->|Yes — MOPS is the floor| Snmp[SNMP inspect vs MOPS value]
    Snmp --> Qs{SNMP matches MOPS?}
    Qs -->|Yes| Ssh[SSH inspect vs MOPS floor]
    Qs -->|No — type / lookup / index / syntax| Wsnmp[["Wire YAML. Generated SNMP: fix the declaration.\nSchema clerk."]]
    Wsnmp --> Snmp
    Qs -->|No — not a wire declaration| Lsnmp[["Ladder: driver vs engine.\nMostly still not engine."]]
    Lsnmp --> Ssh
    Ssh --> Qh{SSH matches MOPS floor?}
    Qh -->|Yes| Done[["Floor for this method × op × all in-scope transports.\nCapture fixture + verified_via."]]
    Qh -->|Miss| C{Which layer?}
    C -->|CLI overlay, command, prompt, field map| Wssh[["Wire SSH overlay. Schema clerk."]]
    C -->|Parse, state machine, transport I/O| Dssh[["Driver function. Still a bug vs existing meaning if the command already works by hand."]]
    C -->|Cannot declare it in YAML; need a new primitive| E[["LOGIC. Engine clerk + HITL.\nDo not invent meaning in SSH."]]
    Wssh --> Ssh
    Dssh --> Ssh
```
