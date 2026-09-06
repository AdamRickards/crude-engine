# 1.17 clerk

Named for napalm-hios v1.17.0. The job is the known-good anchor, wherever
it lives now (`local/reference/`, WebUI, captured fixtures) — not "compare
to v1."

## Hole

Answer one question: does a known-good anchor exist for this method, and
what does it say? Does not fix. Does not decide if a discrepancy is a bug.

## Start

"Is there an anchor for method X?" from any clerk.

## End

Exactly one of three answers:

1. **Yes, captured** — path under `tests/fixtures/` and its `verified_via`.
2. **Yes, not captured** — a human can check WebUI/CLI now; then test bot
   captures it. Do not leave a verbal check.
3. **No** — say so. That is the `NO_HOLE` / no-anchor exit, not a guess.

## Tools (fixed code only)

- `local/reference/CLI/CLI_REFERENCE.md`
- `local/reference/CLI/cli_ref_hios_merged.json`
- `local/reference/MIBs/`
- `local/reference/MOPS/mops_hios.xml`
- `local/reference/configs/`
- Device WebUI (human, strongest anchor — shares no decode path with us)

## Bounds

Report what the anchor says. Bootstrap / smash order is
[`../diagrams/conform.md`](../diagrams/conform.md): MOPS vs WebUI first
(HITL floor), SNMP against that, SSH last. Never "three protocols agree."

## Never

- Fix code or YAML.
- Call agreement proof.
- Invent a plausible value.

## NO_HOLE

Answer 3 is already the honest stop. Establishing a new WebUI-manual
anchor is HITL (or the human sitting at the switch), then test bot
captures.
