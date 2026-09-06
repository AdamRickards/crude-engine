# local/agents refactor — spec for humans (and Claude)

Chiseled 2026-09-05. Target: flowchart personality, fixed-code tools,
small AI gap between a red named proof and a green one. HITL only when
the object does not fit a hole (new logic, or a new tool so it can be
proven).

Claude: poke this file and the standing files it names. Do not restore
session-stale counts into `INSTRUCTIONS.md`. Do not invent a dashboard,
check-in protocol, or seventh clerk.

**Amendment, 2026-09-05, Adam, overriding the cut below:** engine never
merges without HITL sign-off is reinstated, full stop, no exception —
including for a proven bug against existing meaning. This is Adam's call,
not Grok's, not Claude's, not a thing a Bot gets to reason its way past.
Kept cheap: the sign-off is a receipt (sweep result + one line naming why
this is existing meaning, not new), not a case-file essay — that part of
the cut stands. What's reinstated is only that the gate exists and is
unconditional. See `README.md`, `engine-clerk/INSTRUCTIONS.md`,
`engine-clerk/flow.md`, `diagrams/base-flow.md` — all updated to match.

## Intent

```
Flowchart  = personality + sieve (human glance, Bot derived from it)
Fixed tools = almost all judgment (inspect, trace, validate, compare)
AI bounds  = what YAML/code to try between red and green, inside the hole
Start      = issue + exact proof command, red
End        = same command, green, on the tree that contains the change
NO_HOLE    = new meaning, or the named tool cannot run → HITL
```

Schema/wire/docs: proven bug vs existing declared behaviour ships without a
human. Engine files (`interpreter.py`, `crude.py`, `drivers/base.py`):
same proof loop, but HITL glance before merge — receipt + one line, not an
essay. Inventing a primitive, invariant, or pipeline rule is always HITL.

Sidecar on the VPS is how Grok Bot reaches live devices (WireGuard). It is
not a second Grok. Offline CI is a pre-filter. Live-device proof is the proof.

Do not build HTML5 / leases / sidecar-as-state-machine yet. Get this loop
boring on real issues first.

## Standing files (Bots may read)

| File | Role |
|---|---|
| `README.md` | Sieve, HITL cut, roster, fixture tiers, sidecar, privacy |
| `diagrams/base-flow.md` | Cross-cutting holes |
| `diagrams/conform.md` | Conform smash: method × transport × CRUDE, MOPS floor then SNMP then SSH |
| `*/INSTRUCTIONS.md` | Fixed format: hole, start, end, tools, bounds, never, NO_HOLE |
| `engine-clerk/flow.md` | Engine ladder as a tree (`trace=True`) |
| `test-bot/flow.md` | Which proof lane |

## Historical (Bots must not read)

| File | Role |
|---|---|
| `AGENTS-TODO.md` | Stub pointing here |
| `AUDIT-2026-09-04.md` | Bannered snapshot. Useful archaeology. Claims about
  tool status, issue numbers, and the sidecar checkout may be wrong on
  *this* tree. |

## What was cut on purpose

- ~~Hard gate "never merge engine without HITL." Wrong cut. New **meaning**
  is the gate.~~ **Reinstated 2026-09-05 — see amendment above.** New
  meaning is still *a* gate (on top of the hard one), not a replacement
  for it.
- Session numbers as law ("40/45 compliant", "79 replay failures",
  "3 live principles violations"). Those rot and Bots recite them.
- Long narrative INSTRUCTIONS (case-file novels, cron sketches, memory
  porting). Personality is the mermaid; instructions are the leash.
- Dashboard, check-in/out, IR compiler, GitHub `triage:*` lifecycle.
  Too much bus before the loop works.
- Treating sidecar as "Grok is a constrained agent." Grok Bot is the
  worker; sidecar is the proof plane.

## What was kept

- Narrow clerks (a clerk that can touch anything will).
- Proof-or-stop. A code-read is not a receipt.
- Three-way branches already earned: no-anchor vs anchor-says-no;
  sweep-regression vs sweep-infra.
- Fixture `verified_via` tiers and MOPS→SNMP→SSH bootstrap.
- Diagrams separate from instructions (they change on different rhythms).
- Architect privacy redaction at ingress.
- Wire still under schema clerk until a real collision.

## Poke list (Claude)

Verify, then either fix in-tree or file as `NO_HOLE` / missing tool — do
not quietly rewrite the sieve.

1. **`docs/DIAGNOSTIC_PROCESS.md` Step 2** still says `debug=True` for
   pipeline trace. Engine clerk now says `trace=True`. One-line doc fix
   if Adam wants docs clerk to ship it; until then Bots follow
   `engine-clerk/INSTRUCTIONS.md`.
2. **Tool commands in INSTRUCTIONS** — run or read each listed command on
   *this* checkout. Dead `napalm-hios-v2` paths, missing
   `WIRING_GUIDE.md`, sidecar only exposing inspect: confirm and leave as
   `NO_HOLE` (mesh), do not tell Bots to use broken generators.
3. **`validate_schemas.py --errors` current count** — do not write it into
   instructions. If it is green, good. If not, that is schema work with
   that command as the proof, not a roster edit.
4. **Dual trees** — this folder lives in a Syncthing copy. The audit's
   `/home/adamr/crude-sidecar/crude-engine` may be gone. Do not assume
   GitHub or the VPS matches until a SHA/receipt says so.
5. **No new `flow.md`** for architect, schema, docs, 1.17 unless a real
   issue fails to fall through an existing hole. Then branch the mermaid
   first, then shorten INSTRUCTIONS to match.
6. **Do not port Claude `feedback_*` memory** into instructions as essays.
   If a lesson is load-bearing, it is already a required step (full sweep
   after engine; content not shape). Anything else waits for a `d`.

## Open (Adam / HITL, not a Bot)

- Widen sidecar verbs (`--trace`, `--no-validate`, `--compare`, replay)
  so Tester is not `BLOCKED` on mesh.
- Tree identity on every live receipt (what SHA/generation the VPS ran).
- Whether schema vs wire needs its own hole — only after they collide.
- Conform smash loop is now `diagrams/conform.md` (method × transport × CRUDE,
  MOPS HITL floor → SNMP → SSH, classify layer). Do not "improve" it into
  three protocols voting.
- `DIAGNOSTIC_PROCESS.md` Step 2 fix (docs clerk bounds already allow it).

## Done looks like

A Bot given one issue can: read its flowchart, run only listed tools,
loop inside bounds until the named proof is green, implement, or stop
with `NO_HOLE`. A human can glance the mermaid and see which hole that
was. No essay. No new meaning. No dashboard required.
