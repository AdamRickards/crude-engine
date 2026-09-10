# Agents — sieve, tools, bounded gap

Flowcharts in this folder are the process. They are how a human sees the
holes, and how a Bot gets its personality (derived, fixed format, not a
novel). Anything that fits an existing hole runs to done with no human.
Anything that does not fit is HITL — then the chart gets a new hole, or a
new fixed-code tool, so the next one falls through.

This folder is the 2.0 of `docs/program/METHOD.md` for bot labour. Destination
still lives in `docs/program/SEED.md`. Do not treat `SEED.md`'s "loose
instructions" as a license to narrate. Speech is a receipt or `NO_HOLE`.

## The sieve

Alphabet-shaped work, holes for letters we already know. `a` `b` `c` fall
through and the team finishes them. A `d` does not squeeze through `c`.
HITL looks at the object, adds a hole or a tool, and the next `d` is an `a`.

Do not pre-drill holes for letters you have not seen. A fake yes/no is the
same mistake as skipping the check.

Glance: [`diagrams/base-flow.md`](diagrams/base-flow.md) (does it fit a
hole?) and [`diagrams/conform.md`](diagrams/conform.md) (conform smash:
method × transport × CRUDE, MOPS floor then SNMP then SSH). Clerk-specific
trees sit next to that clerk as `flow.md`. Update the chart when a real
object does not fit. Then regenerate the Bot instructions from the chart —
do not patch prose and leave the mermaid lying.

## Two HITL gates

**Fits a hole (schema/wire/docs, no human):** something does not work against a contract that
already exists.

```
issue → reproduce with a named tool → propose a small change inside bounds →
run the same tool → implement when green
```

Online devices matter. Offline CI is a cheap pre-filter, not a substitute
for live-device proof. Grok Bot reaches live devices only through the sidecar on the VPS
(WireGuard, firewalled). If the sidecar cannot run the proof, that is
`NO_HOLE` (mesh missing), not a prompt to guess.

**HITL (`NO_HOLE` / `LOGIC`):** the object needs logic that is not already
in the system — a new primitive, a new invariant, a behaviour change, or a
new test tool so this shape can be proven. That is the work the human wants:
better testing logic, and decisions that change how things work.

New meaning is one gate. Engine files are a second, separate, absolute one:
`interpreter.py`, `crude.py`, `drivers/base.py` never merge without a human
looking, full stop — a proven bugfix against existing declared behaviour
still needs a HITL glance before it ships. No exception, no matter how
small the diff or how clean the sweep. This is Adam's rule, not something
a Bot (Grok included) reasons its way past. Kept cheap on purpose: the
sign-off is a receipt (sweep result + one line naming why this is existing
meaning, not new), not a case-file essay.

Every `NO_HOLE` also names the missing hole or missing tool. Otherwise the
same `d` recurs forever.

## A Bot, fixed format

Personality comes from its `flow.md` (or the base flow). Instructions are
only: hole, start, end, tools, bounds, never, `NO_HOLE`.

- **Start:** this issue, this exact proof command, currently red (or not
  yet run).
- **End:** the same command, green, against the tree that contains the
  change. Live proofs go through the sidecar and must say which tree ran.
- **Tools:** the listed fixed-code commands only. No throwaway
  `device.get_*()` scripts. If the harness cannot do it, add a flag later
  (HITL / tool work) — do not improvise.
- **Bounds:** the only AI gap. What YAML/code to try between red and green,
  inside the hole. Not whether it is proven. Not what the architecture
  should become.
- **Never:** essays, new primitives, guessing device behaviour from a
  code-read, claiming a fix without a receipt from the named tool.

## Architect orchestration

Logic checks for how Architect multiplexes clerks live in
`architect/INSTRUCTIONS.md` § Orchestration checks (e.g. schema
hole ⇒ schema→wire ask ⇒ 1.17 differential). HITL-named checks
get written there — not only in chat memory.

## Roster

Six holes. Do not add a seventh until a real object collides two of these.

| Clerk | Hole | Flow | Ships when |
|---|---|---|---|
| **Architect** | Route. Does not fix. | [`diagrams/base-flow.md`](diagrams/base-flow.md) | N/A |
| **Schema clerk** | `schemas/*.yaml` and, for now, `wire/**` | base flow + diagnostic ladder steps 1–6 | named proof green, no new primitive |
| **Engine clerk** | `engine/interpreter.py`, `engine/crude.py`, `drivers/base.py` | [`engine-clerk/flow.md`](engine-clerk/flow.md) | named proof green, diff uses existing meaning, **and HITL sign-off — always, no exception** |
| **Docs clerk** | regen generated docs; catch stale hand-written claims | (none yet — add only after a real branch) | docs-only, generators current |
| **Test bot** | Run the named proof. Never authors. | [`test-bot/flow.md`](test-bot/flow.md) | receipt (pass/fail/blocked), not a merge |
| **1.17 clerk** | Does a known-good anchor exist, and what does it say? | (three answers only) | an anchor or a plain no |

Wire stays under schema clerk until real PRs show the two roles colliding.

## Fixture confidence (when capturing)

Not all "known good" is equal. Tag `tests/fixtures/` honestly:

- `verified_via: webUI-manual` — human read the device WebUI. Highest.
- `verified_via: cli-manual` — human ran the CLI by hand.
- `verified_via: cross-protocol-agreement` — two protocols agreed. The
  collapse bug had MOPS and SNMP agreeing while both were wrong. Not proof.
- `verified_via: unverified` — snapshot only. Not an anchor.

Conform smash is [`diagrams/conform.md`](diagrams/conform.md): HITL/1.17
confirms MOPS, SNMP is fitted to that value (often generated-wire type or
lookup), then SSH toward the same two known goods. Nested
`method × transport × CRUDE op`. Reads before writes. Classify an SSH miss
as wire, driver, or engine/primitive — do not smash all three at once.

## Diagram convention

- Cross-cutting → `diagrams/<name>.md`
- One clerk's tree → `<clerk>/flow.md` next to `INSTRUCTIONS.md`
- Never paste mermaid into instructions. Personality is derived from the
  chart; instructions stay the fixed format above.

## Sidecar

The VPS sidecar is how Grok Bot proves work on live devices. It is not a
second Grok and not a substitute for the Bot. Widen sidecar *verbs* when a
proof cannot be run (HITL / tool work). Until a verb exists, `NO_HOLE`.

Privacy (personal cyber + physical security): do **not** mention a
restricted site on GitHub or in anything a Bot posts externally. No model
names, hostnames, pool labels, IPs, inventory size, or counts that imply
how much hardware exists. Home-office may be named in the abstract. Public
language is tested/untested and pass/fail. Architect enforces at ingress.
Device identity stays in gitignored `device_pool` / local sidecar notes.



## Decision trail (glance value)

Auditable for improvement, not distrust. The GitHub issue is the log
(on-disk only when there is no ticket). Do **not** paste mermaids onto the
issue — the charts stay in this folder; the issue holds the decisions.

Fixed shape, short lines:

1. **Architect triage** — hole pick + named proof command  
   e.g. `hole: schema/wire · proof: release_matrix --inspect --method X`
2. **Clerk steps** — which flow step, what was ruled out, tool run, receipt  
   e.g. `step: ladder-4 · ruled-out: overlay miss · tool: validate_schemas --errors · receipt: …`
3. **End** — green on that proof, leftover filed, or `NO_HOLE` naming the
   missing hole/tool

Open the issue → see the logic. Wrong bounce → feedback into the chart.
Right bounce → obvious. Speech on the issue is a receipt or `NO_HOLE`, not
an essay.

**Multi-hop is normal.** One issue may bounce Schema → 1.17 → Engine (or
run two asks in parallel) so clerks scale. One clerk could walk the whole
path alone; splitting is throughput. Architect multiplexes each ask with a
named proof. Each hop adds decision-trail lines. Clerk helpers/subagents
are fine when their work collapses into those same glance lines — no
silent side channel.

## Living law (how this stays true)

`local/agents/` on `main` is process law for bot labour. Update it in-tree;
do not let bot profile prose drift ahead of this folder.

1. **Change the chart first** (`diagrams/*.md` or a clerk `flow.md`) when a
   real object does not fit. Then shorten that clerk's `INSTRUCTIONS.md` to
   match. Never patch instructions and leave the mermaid lying.
2. **Ship via PR** into `AdamRickards/crude-engine`. Architect owns GitHub
   ingress and redaction. Historical snapshots (`AGENTS-TODO.md`,
   `AUDIT-*.md`) are not law.
3. **Bot profiles follow the roster.** Each live clerk description is a
   short leash derived from its `INSTRUCTIONS.md` (hole, tools, never) plus
   a pointer to this folder. Architect does not invent a seventh clerk.
4. **Weekday sync.** Architect diffs live bot profiles against the roster
   here and reports differentials in the Architect chat: missing clerk,
   extra bot, description drift, or chart/instructions mismatch. Fix by
   updating the profile or the pack — keep one truth.
5. **Decision trail on the issue** (see above). Profiles and INSTRUCTIONS
   require those glance lines; weekday sync flags essays or silent work.
6. **Claude on the VPS** stays local-only (no push). Architect turns
   detailed sidecar receipts into GitHub issues without device identity.

## Not standing law

`AGENTS-TODO.md` and `AUDIT-2026-09-04.md` are historical snapshots. Bots
do not read them. The living spec of this refactor is
[`local-agents-refactor.md`](local-agents-refactor.md).
