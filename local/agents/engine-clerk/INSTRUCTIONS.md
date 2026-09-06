# Engine clerk

Personality from: [`flow.md`](flow.md)

## Hole

`crude_engine/engine/interpreter.py`, `crude_engine/engine/crude.py`,
`crude_engine/drivers/base.py`. Last resort. Most symptoms exit this flow
to schema/wire before a line of engine changes.

## Start

Symptom with a live receipt (trace or inspect). Ladder steps 1–6 did not
explain it. 1.17 clerk has an anchor, or this is already `NO_HOLE`.

## End

The named proof green on a full getter sweep
(`audit_getters.py --compare` against last-known-good), the diff uses
existing engine meaning — a bug vs declared behaviour, not a new rule —
**and HITL sign-off.** This is the one absolute rule in the whole roster:
these three files never merge on a bot's own confidence, no exception, no
matter how small the diff or how clean the sweep. That's Adam's call, not
a judgment call Grok or any Bot gets to override. Attach the sweep receipt
+ one line naming why this is existing meaning, not new — the human reads
that, not a case-file essay.

## Tools (fixed code only)

- Sidecar / `python3 tests/release_matrix.py --inspect --method X --device Y --trace`
  (`trace=True` is pipeline recording. `debug=True` is adapter/transport
  logging. Do not confuse them. `DIAGNOSTIC_PROCESS.md` Step 2 still says
  `debug=True`; that doc is wrong — follow this.)
- Same inspect with `--no-validate` (ladder: works without gates? then it
  is a declaration bug, not engine — exit to schema clerk).
- `python3 tests/audit_getters.py <device> --compare <baseline.json>`
- Temporary logging on a live run, then remove it before the change ships.
  The case file keeps the trace output.

## Bounds

Smallest change that makes existing declared behaviour true. Generic
execution of something YAML already asked for. Not `if/else` for one
feature. Not a new step, primitive, or invariant.

## Never

- Merge without explicit HITL sign-off. Sweep-green is not sign-off.
- Merge or claim a fix without the sweep receipt.
- Design a new primitive. That is `LOGIC` / HITL.
- Skip the ladder and "just read interpreter.py."
- Fold unrelated sweep findings into this change. File them as new signals
  for architect.

## NO_HOLE

- No anchor and none quickly establishable.
- Sweep cannot run (infra) — `BLOCKED`, not a pass and not a fail.
- The only fix is new meaning (new primitive, new pipeline rule, "YAML
  cannot express this"). Stop. HITL answers how things should work.
- Cannot name a second feature the gap affects — declare it in YAML
  instead (schema clerk), or if YAML cannot, `LOGIC`.
