# Resolution methodology — HITL handover, not final system law

This is HITL-articulated methodology from a working session (2026-09-20/21),
handed over as raw input for Architect to fold into `local/agents/` as fits —
same as any other multi-session goal named in chat before the board picks it
up. Distill, restructure, or split across existing files freely; nothing
below is meant to survive verbatim as written. Two live pilots (fresh,
context-free agents, isolated worktrees) already exercised parts of this
against the real repo and real sidecar — findings are included inline where
they changed the rule, not just where they confirmed it.

## The goal (end state)

> Every function that exists works on every protocol it's possible to.
> Exceptions only by HITL, requested by a clerk, with evidence.

Operationalized as a countable number, not a feeling:

```
coverage = (function × protocol pairs proven against a floor)
         / (function × protocol pairs declared possible)

exceptions = { HITL-approved gaps }, each carrying: requesting clerk, evidence, reason

done when: coverage → 100%, everything short of that is either
           in-flight or an explicit, evidenced exception — never a silent gap
```

This is the same move `config_backed=52` already makes for one lane
(Offline↔gold), `36/43` makes for another (SNMP vs MOPS), and `49/49` for a
third (A′ live MOPS). What's missing is rolling every lane's count into one
top-level number instead of N separate ones nobody's summed.

## The core distinction (why this resists a linear spec)

Two different kinds of knowledge get conflated when trying to write this
down start-to-finish:

| | Solution-knowledge | Readiness-knowledge |
| --- | --- | --- |
| Question | "How do I fix *this* thing?" | "Am I *allowed* to attempt a fix right now?" |
| Shape | Circular, emergent, context-dependent | Finite, checklist-shaped |
| Can it be pre-specified? | No — discovered in the doing | Yes — same five questions every time |
| Lives in | Clerk judgment + role rules + reference docs | A written gate, checked before any attempt |

The thing that can't be spelled out discretely is *how to solve a given bug*.
The thing that can is *whether you're standing on solid enough ground to
try* — and that's exactly the five things named below.

## Floors are built, not written — construction order vs. validation order

Two different sequences, easy to conflate:

- **Construction order** (how a floor comes into existence, cannot be
  reordered): live device → capture the real response → *then* author it as
  a unit test fixture. A fixture invented from what the code/model *expects*
  the device to say is not a floor — it only proves the code agrees with an
  assumption, and will pass forever even after the real device disagrees.
  napalm-hios v1's ~693 protocol unit tests (`test_mops_hios.py` 343,
  `test_snmp_hios.py` 265, `test_ssh_hios.py` 85 — tag `v1.17.0`) are
  trustworthy specifically because every one was built this way: real device
  response captured first, unit test authored second, never the reverse.
- **Validation order** (how to re-check cheaply once floors exist, fastest
  first): unit test → offline/config-XML → MOPS live → SNMP live → CLI live.
  This is the pipeline `release_matrix.py`/the sidecar already runs — it was
  missing the unit-test rung underneath it, which is the gap being filled now.

**Rule:** never author a mock/fixture from invented or expected values, even
under time pressure, even for "just a quick unit test." If there's no real
capture yet, that's a construction-order task (go get one), not a shortcut to
take. Once enough real-captured examples exist for a protocol, a new one
becomes "find a similar existing test, reuse its *shape*, capture fresh real
*values* for the new case" — the pattern is reusable, the data never is.

## SSH/CLI floors need multiple captures per getter — MOPS/SNMP don't

MOPS and SNMP are structurally uniform regardless of data volume: more rows
is just more rows, the row *format* doesn't change with size. SSH/CLI text
tables genuinely change shape with size:

- **Row count** — pagination / `--More--` prompts. The driver already sends
  `cli numlines 0` at connect to disable paging (`SSH_state.yaml`'s
  `on_enter`) — worth re-verifying that actually suppresses it rather than
  just delaying it once a table gets big enough.
- **Value width** — a longer-than-usual value in a fixed-width column can
  shift or wrap subsequent columns, breaking a regex/anchored-position parser
  that was only ever exercised against short example values.

**Rule:** a single real capture per SSH getter is not a sufficient floor.
Each table-shaped SSH getter needs at minimum three real captures — typical
size, large row-count, and a long-value case — to actually exercise the
failure modes unique to text-table parsing. MOPS/SNMP getters don't need this
multiplication; their shape doesn't depend on size the same way.

**"Large" and "long" are not guesses — they're declared, go look them up
first.** Three reference sources already exist and carry authoritative
*metadata about the data* (table size limits, max value lengths, types), not
just sample data:

- **CLI reference** (`local/reference/CLI/cli_ref_hios_merged.json`, from the
  CLI reference PDF, 1,849 commands / versions 9.0–10.3)
- **MOPS gold gathering** data (crude-engine's own gathered gold + the
  `offline_gold_matrix.py` fixtures)
- **SNMP MIB dataset** (formal SMI syntax, table INDEX structure, max-access
  — already the basis for `#162`'s syntax-to-type rules)

Before capturing the "large row-count" / "long-value" SSH cases, check
whether the true declared max is in one of these first. If SSH's actual max
table size for a given getter is, say, 50 rows and the floor only ever
captures 5, a real bug living between row 6 and row 50 has zero chance of
being caught — not because the process was skipped, but because the bound
used to construct the floor was a guess instead of a lookup. Same failure
mode either way: an unproven claim of "proof."

## Mining v1: expect renames, not just bugs

crude-engine is **not a drop-in replacement** for v1 — some output field
names changed, some method names changed. When mining v1's unit tests for
floors, a chunk of "mismatches" the diff surfaces will be exactly this, not
real regressions. Don't spend real time resolving each one in place.

**Rule:** if a v1-vs-crude-engine mismatch is small (naming/shape drift,
loosely <10% different), it's very likely just a rename — note it and move
on. If it's genuinely different (>10%), park it rather than force a
resolution in the moment. Pilot finding: this threshold is a judgment call,
not a formula — a real case (`get_dns`'s `servers`/`active_servers` reshape
from list to dict) had no clean percentage to compute. Treat it as "does this
look like a rename/reshape, or a removed/changed capability," not a diff-tool
output.

## Batch-scan the park pile before resolving anything in it

Already proven twice: `#92` turned ~9 separately-filed "SSH timeout" issues
into one shared root cause; `#162` turned 68 generator/wire diffs into 3
shared type-conversion rules. Both times the win came from scanning the
*set* of failures for a common pattern before resolving any one of them —
not from getting faster at resolving each individually.

**Rule:** treat this as the standard first move whenever a park list
(`hitl-engine-park.md`, or the v1-mining rename pile above) has more than a
couple of entries. Periodically re-read the whole pile looking for
coincidence/similarity across entries — a shared cause found this way
answers several parked items at once, faster than resolving even one of them
in isolation would.

## The readiness gate (run before any resolution attempt)

For the function × protocol pair in question:

1. **Floor** — does a known-good reference value exist (Gold / Config-XML
   Offline / Live device — whichever applies to this lane)?
2. **Test** — does something check current output against that floor?
3. **Reference material** — if 1 or 2 is missing, is there something to
   build it from (MIB, schema, a sibling protocol's already-proven floor)?
4. **Device** — is live ground truth reachable if needed?
5. **Comparative floor** — is there a *different* already-passing
   protocol/source to triangulate against?

**Rule:** if 1 and 2 both fail, and 3 can't build them either → stop, park to
HITL. No floor, no agentic attempt — you cannot resolve into the unknown,
only build the ground to stand on first, or hand it to a human.

If 1+2 exist (or get built via 3/4/5): the clerk may attempt resolution.

## The resolution rule (gates, not hacks)

A fix passing its test is **necessary, not sufficient**. Before it counts as
resolved, it also has to answer: *does this follow the declared system
contract (schema/wire YAML, gate philosophy — gates produce or raise, no
try/except; no engine special-casing) rather than just making the test go
green by any means?*

This isn't a new rule — it's the existing engine-HITL-gate / no-engine-hacks
principle, generalized from "only applies to engine changes" to "applies to
every clerk's resolution, in every lane." Test-green is a necessary
checkpoint. Contract-respecting is the other one, and it needs its own
check, because a test suite can't see "this technically works but violates
the design."

## Role-bounded resolution (clerks)

A clerk = a bounded rule-set (what moves are legal for this role) +
supporting documentation + test tooling to prove correctness inside that
boundary. Hitting the edge of legal moves (needs an engine primitive, needs
a new schema concept) is not something a clerk improvises past — it parks
to HITL with evidence, same shape as `hitl-engine-park.md` already uses. The
boundary is what makes "six clerks, no chaos" work: different personalities
because different roles carry different legal-move sets, not because they
disagree on the goal.

## Execution shape — three separate jobs, not one loop

Create, Execute, and Resolve are different jobs with different success
criteria. Conflating them is its own failure mode (judging Create by
pass/fail invites massaging a fixture until code agrees with it, which
destroys it as a floor).

**Job 1 — Create.** Produces the unit test. Success = "this fixture is a
real, authoritative capture" — never "does the code pass." No resolution
happens here, nothing gets fixed here.

```
for each method in schemas (crude_engine/schemas/*.yaml)
  for each protocol the method's wire declares a source for (mops | snmp | ssh)
    create unit test from an authoritative capture for (method, protocol)
```

(Protocol and transport collapse to one axis in this codebase — mops/snmp/ssh
*are* both the wire's declared source and what fetches it — two-level nest,
not three.)

**Two pilots found the authorization model for this job needs two tiers, not
one path** — see below before treating "go through the sidecar" as universal.

**Job 2 — Execute.** Runs an already-created test, observes the outcome,
files an issue with evidence if it disagrees. Attempts zero resolution.
Mechanical enough to hand to a bot swarm at scale: "here's a pack of tests,
run them, tell me what disagrees" — nothing more is asked of this job. Two
modes, both still Execute, neither is Create: replay against the static
fixture (fast, no device, catches code regressions); run live against real
hardware (slower, catches device/firmware drift from what was captured).
*This* job is where the sidecar's lock/mode gating matters — frequent,
scaled, needs the safety rail Create doesn't.

**Job 3 — Resolve.** Starts only from what Execute filed, never invents its
own problems to chase. Everything above (readiness gate, gates not hacks,
park + batch-scan) applies here.

## Pilot findings — Job 1's authorization model needs two tiers

Two fresh, context-free agents ran Job 1 for real, in isolated worktrees
verified against the actual `origin/main` tip, one `(method, protocol)` pair
each, told to name every gap rather than paper over one with a guess.

**Use the capture/replay tooling that already exists.** `tests/capture.py` +
`tests/test_replay.py` (`tests/fixtures/<device>/<protocol>/{tap1_transport,
tap3_engine,tap4_napalm}/`) is Job 1's real output shape — not a hand-written
`test_*.py` file, not hand-deriving an expected value from reading source
(pilot 1 got visibly unsure of one type-mapping doing exactly that).

**The conflict pilot 2 found:** there are three taps, not two.
`test_engine` needs `tap1`+`tap3` and validates the actual transform
pipeline (schema/wire mapping — where essentially every real bug this
project has had actually lived). `test_napalm` needs only `tap3`+`tap4` and
validates the thin shim layer only. The sidecar's `/v1/run` **never exposes
tap1 raw data for MOPS/SNMP, even with `trace:true`** — deliberately, the
same boundary that keeps device IPs out of responses. So "go through the
sidecar" cannot produce the higher-value `test_engine` artifact for those
two protocols. Not a missing feature — the privacy boundary doing its job
somewhere it wasn't accounted for.

**Resolution — two tiers:**

- **Tier 1 (full — `tap1`+`tap3`, enables `test_engine`)**: requires
  *direct* device access via `tests/capture.py`, not the sidecar. Deliberate
  exception to "go through the sidecar" — Create is rare and careful by
  nature (construction-order already requires this); Execute is where
  frequent/scaled access needs the sidecar's lock/mode gating. Reachability:
  real TCP probe against `tests/device_pool.yaml`'s declared IP — that file
  only exists for this privileged, local, Tier-1 path.
- **Tier 2 (partial — `tap3`+`tap4`, enables `test_napalm` only)**: via the
  sidecar's `/v1/run`, same value written to both taps. Achievable by any
  clerk without special device authorization; genuinely valid, just doesn't
  touch the transform pipeline. Reachability: read the sidecar's own
  `protocols.<proto>.status` field, not a client-side probe — the sidecar
  never discloses an IP to probe in the first place. Fixture directory: key
  by the sidecar-provided `label`, never an IP.

**SSH is a partial third case, still open.** `trace:true` genuinely returns
real raw command/response text (`cli` array) — actual tap1-equivalent data,
unlike MOPS/SNMP — but shaped as `{command, level, response}`, not
`capture.py`'s expected transport-mock shape. Reshaping it needs a
translation step (`cmd_verify`, list-vs-string `commands`) not yet
specified. Next thing to pin down if SSH floors go through the sidecar
route rather than Tier 1 direct.

**Trap to flag:** `tests/fixtures/offline_gold/gold_floors.json` looks like
a ready-made floor and explicitly isn't one (its own description says
"sanitized... no device identity") — verified this isn't actually a problem
for the one method checked (`get_dns`'s `floor_source: gold` is backed by a
real `release_matrix.json` mops `verdict: pass`, not the sanitized file
alone — the existing provenance rule already guards this correctly), but the
file is still easy to grab by mistake as a fixture source under time
pressure. Treat it as off-limits for that specific use, full stop.

## Local store — per-machine, not shared, rebuilt not restored

`tests/fixtures/` is already fully gitignored (confirmed by both pilots) —
nothing in it ever reaches GitHub. Not an accident to route around — the
correct design: this data only matters locally, and what's local never needs
uploading. Precedent already exists for this category (`local/agents/`,
`local/generator/`, `local/reference/`).

**Property this buys:** the process may run on multiple machines, and only
some can reach lab devices. A fixture cache is per-machine, not shared.
**Rule:** a missing fixture is not a broken state, it's a cache miss. If the
current machine has device access (Tier 1), regather it. If not, fall back
per the readiness gate (mine an existing corpus, or park). Side benefit: a
cache that gets rebuilt rather than trusted-forever also catches real
device/firmware drift, not just code regressions.

## Visualization is a derived view, never a source

The objects are what matter — `tests/catalog.yaml` (the known
method×protocol grid), `tests/fixtures/floors_provenance.json` (per-pair
floor status). A visualization is a rendering of those, generated fresh each
time, never hand-maintained — same discipline as
`local/generator/generate_docs.py` / `generate_method_ref.py` already use.
If a visualization ever needs hand-editing to stay accurate, that's a sign
the underlying object is wrong or incomplete, not a reason to patch the view.

**Scoped task for docs-clerk:** generate a static page, flat visual grid
(rows = methods, columns = protocols, cell = floor status from
`floors_provenance.json`), regenerated on every merge to `main` that touches
`catalog.yaml` or `floors_provenance.json` — same trigger pattern the
existing doc generators use. Publish via GitHub Pages (fits "if it's not on
GitHub, it's not the Effort" directly, zero extra accounts) or Cloudflare
Pages with GitHub auto-deploy if a custom domain matters enough to justify
the extra credential surface. docs-clerk's job here is rendering only — it
never originates a status, only reflects what the source files already say.

**Not ready yet:** a second axis ("expand known space" — new methods
discovered from the WebUI) has no tracked object yet — no file plays the
role `catalog.yaml` plays for known methods. That axis isn't ready to
visualize regardless of hosting choice; the blocking step is defining what
holds "candidate methods found in the WebUI, not yet schematized," not
picking a page host.

## Open, not yet resolved

- The five-question readiness gate should become its own file every clerk's
  instructions point to, rather than restated per-lane.
- Where the rolled-up global coverage number lives and who updates it —
  probably `effort-board.md`, one more row, same pattern it already uses for
  lane status.
- SSH's tap1 shape-translation (above).
- The "expand known space" tracked-object question (above).
