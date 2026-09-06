# Base flow — does this fit a hole?

Owned by no single clerk. Architect routes through this. Branch this chart
when a real object does not fit — then update the owning clerk's
`INSTRUCTIONS.md` to match. Do not invent holes speculatively.

```mermaid
flowchart TD
    A[Signal: issue, sweep, or HITL] --> B{Fits a known hole?}
    B -->|Yes: schema/wire, docs regen,\nengine bug vs existing meaning,\nanchor check, named proof| C[Assign owning clerk]
    B -->|No: new meaning, no tool can prove it,\nambiguous after the named tools| S[NO_HOLE]
    S --> S1[HITL: new hole, new tool, or park]
    S --> S2[["Name the missing hole or missing tool.\nThat is how the sieve grows."]]
    S1 --> C
    C --> D[Start: named proof command, currently red]
    D --> E[Owning clerk: one small change inside bounds]
    E --> F[Test bot: run the SAME proof\nlive via sidecar, or offline if the hole says so]
    F --> G{Receipt?}
    G -->|Red, still inside bounds| E
    G -->|Green, no new meaning| G2{Touches engine/interpreter.py,\nengine/crude.py, or drivers/base.py?}
    G2 -->|Yes| Gate[["HITL sign-off. Always, no exception —\nreceipt + one-line why-existing-meaning.\nNot a Bot's call, not Grok's to skip."]]
    G2 -->|No| L[Implement. Done.]
    Gate --> L
    G -->|Tool failed to run: tunnel, SHA, infra| I[BLOCKED — mesh.\nNot evidence either way.]
    G -->|Would need a new primitive / invariant / behaviour| S
    L --> N[Docs clerk if methods/docs now stale]
    L --> O[Test bot: capture/update fixture + verified_via]
```
