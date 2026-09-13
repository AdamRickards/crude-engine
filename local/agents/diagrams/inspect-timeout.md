# Inspect timeout resolution (open vs call)

After `#179`, inspect timeouts carry `phase=open` or `phase=call`.
Attribution is the **finder**. Resolution is a **Test-bot poke loop**
(classify + route — never author a fix). Living law:
[`../test-bot/flow.md`](../test-bot/flow.md) § Call-timeout resolution.

```mermaid
flowchart TD
  T[timeout receipt] --> P{phase?}
  P -->|open| Open[["Open path: login/prompt/budget.\n#92 class until fail-fast HITL.\nDo not Schema-fake overlay."]]
  P -->|call| Decl[["List declared SSH *read* commands\nfrom wire overlay for this method"]]
  Decl --> Cli[["CLI.json / CLI_REFERENCE:\nspelling exists? placeholder?"]]
  Cli --> Bucket{Bucket}
  Bucket -->|literal placeholder / invalid spelling| Inv[["Invalid-cmd candidate.\nTrail + #92 fail-fast HITL\n(or Schema if overlay invents bad CLI)"]]
  Bucket -->|N x per-index fanout under call budget| Fan[["Fanout-budget leftover.\nRoute Schema: table show vs\nper-port {index} loop"]]
  Bucket -->|few valid shows; still call-timeout| Slow[["Slow-or-hang call.\nNote harness: hang returns no cli.\nOptional Engine: last_command heartbeat"]]
  Bucket -->|call completes; cli listed n=0| Parse[["Not timeout — SSH parse/overlay.\nClose timeout intention; one remainder ticket"]]
  Inv --> Trail[Decision trail on issue]
  Fan --> Trail
  Slow --> Trail
  Parse --> Trail
  Trail --> End[["END: leftover / NO_HOLE / green.\nNever invent a seventh clerk."]]
```

## Why CLI.json before another live poke

On `phase=call` **timeout**, the worker thread never returns — so
`trace:true` often has **no** `cli` / `last_cli` in the receipt (hang
never hits `_collect_cli`). Declared commands from
`crude_engine/wire/ssh/*.yaml` + `local/reference/CLI/cli_ref_hios_merged.json`
are the first honest poke. Live re-inspect still proves budgets/phase;
it does not by itself name the stuck `show`.

## Buckets (glance lines for the issue)

| Bucket | Meaning | Route |
| --- | --- | --- |
| open-budget | `phase=open` under current `inspect.yaml` | #92 / budget; not overlay |
| call-budget-fanout | Many `{index}` / per-row reads vs call budget | Schema (collapse to table `show`) |
| call-invalid-cmd | CLI not in CLI.json, or literal `{index}` in transcript when call completes | #92 fail-fast HITL and/or Schema |
| call-unknown-hang | Few valid shows; still `phase=call` timeout; no cli | Trail; Engine `NO_HOLE` if need last_command heartbeat |
| timeout-cleared-parse | `status=ok` but n=0 / wrong shape | SSH remainder ticket; not #92 |

