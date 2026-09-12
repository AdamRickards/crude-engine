# Effort board — tangible goals (bubbles)

Owned by Architect. Chart first: when HITL names a multi-session goal, it
becomes an Effort issue; children split off; the Effort stays open until
pieces resolve or HITL parks it. This mermaid is the glance; GitHub Issues
are the objects clerks bounce inside.

Update when a bubble splits, greens, or blocks. Do not leave the board only
in chat.

```mermaid
flowchart TD
  HITL["HITL idea / discussion"] --> E["Mint or update Effort issue"]
  E --> Split["Split into child issues\nnamed proof each"]
  Split --> A["Lane A: Offline↔gold floors\n#169 DONE 50 / look-into #193"]
  Split --> Ap["Lane A′: Live MOPS triad\nOPEN — not started"]
  Split --> B["Lane B: Generator→SNMP\n#162 IN PROGRESS"]
  Split --> C["Lane C: SSH after two floors\n#92 / #41 / #178 BLOCKED"]
  A --> Re["Recombine: Effort WHERE\nthen close or park Effort"]
  Ap --> Re
  B --> Re
  C --> Re
```

Rules:

- Chat is signal, not storage.
- Local Architect MD is cache.
- User-owned Projects V2 is not writable via fine-grained PAT — do not depend on it.
- Six clerks only; Architect holds the board and assigns hops.
