# tests/ — script catalog

> One-pager. Every script in `tests/` listed once with: what it does, when to use it,
> what NOT to use it for, and how to invoke it. Read this before adding new test code.
> Linked from `AGENTS.md` (the only root agent law) and `docs/RELEASE_GATE.md`. Leftover Claude is archive, not law: `local/archive/docs-legacy/claude/CLAUDE.md`.

## TL;DR — which script for which job

| I want to... | Use |
|---|---|
| **INVESTIGATE a bug — see actual returned data side-by-side across protocols** | **`release_matrix.py --inspect --method X --device Y`** ⭐ |
| **Run the release gate on the fleet** | **`release_matrix.py --gate`** |
| **Surgical: one method, one device, one protocol** | **`release_matrix.py --method X --protocol Y --device Z`** |
| **Surgical: one schema, one device** | **`release_matrix.py --schema X --device Y`** |
| **Read-only sweep across the fleet (no writes)** | **`release_matrix.py --execute --kind read`** |
| **Render docs from latest matrix state without re-running** | **`release_matrix.py --render`** |
| **Reset matrix DB before a clean run** | **`release_matrix.py --reset`** |

**STRONG RULE**: when fault-finding, **never write throwaway Python scripts** to call `device.get_*()` and inspect output. Use `release_matrix.py --inspect` instead. The harness has the wiring (gather, parity check, raw dump, multi-protocol comparison) baked in. Throwaway scripts:
- Get lost when the file is deleted
- Have no shared state with the rest of the harness
- Repeat invocation patterns that should be standardized
- Easy to make mistakes (wrong protocol arg, wrong credentials, missing napalm_compat=False)

If you find yourself wanting to write a one-shot script, ask "can `release_matrix.py --inspect` do this?" first. If it can't but should — add a flag, don't write the script.
| Check ALL getters on a device, with cross-protocol parity (legacy) | `audit_getters_v2.py` |
| Re-run ONE getter on ONE protocol after a fix (legacy) | `audit_getters_v2.py --method X --protocol Y <ip>` |
| Capture a per-method audit (shape, types, samples) for a device | `audit_getters.py` |
| Diff two getter audits to see what changed between versions | `audit_getters.py --compare old.json` |
| Run safe automated SET tests via `audit_safety.yaml` | `audit_setters.py` |
| Run the full SET round-trip suite directly | `test_setter_pairs.py` |
| Run the CRUD round-trips directly | `test_crud_pairs.py` |
| Capture multi-layer fixtures (transport/driver/engine/adapter) | `capture.py` |
| Replay captured fixtures as offline regression tests (pytest) | `test_replay.py` |
| Orchestrate getters + setters across the lab fleet (legacy) | `audit_all.py` |
| Gather one device's state for diagnostics | `audit_common.py <ip>` |

**Rule:** to test "one thing real quick" never run the full suite. Use the surgical flag of the right script. Full suite runs are for proof, not debugging.

---

## Read-side scripts

### `audit_getters_v2.py` — the keeper

**Purpose:** schema-driven validation of every read method across protocols and devices.

**What it does:**
- Loads all schema YAMLs from `crude_engine/schemas/`
- For each method, infers which protocols support it by scanning wire YAMLs (no hardcoded lists)
- Runs each supported method against each requested device + protocol
- Three checks per call:
  - **Contract** — does the output match the schema `defaults` shape (keys present, dict vs list, sub_table structure)
  - **Types** — do value types match what `defaults` declares
  - **Parity** — cross-protocol consistency (MOPS↔SNMP↔SSH for the same data, with `TIMING_FIELDS` excluded)
- Reads `tests/wire_exemptions.yaml` to skip attrs that are legitimately unavailable per protocol
- Outputs JSON optionally; prints a `GATE CHECK:` summary line at the end
- Exits non-zero if any failure or parity error

**When to use it:**
- Surgical re-run after fixing one getter: `python3 tests/audit_getters_v2.py 192.168.60.80 --protocol mops` then read the section for the affected method
- Single-device gate check before a larger refactor commits
- Single-protocol verification when you know the others are unchanged

**When NOT to use it:**
- Don't use it for setters or CRUD — read-only.
- Don't use it as a release-gate orchestrator across the whole fleet — that's `release_matrix.py`'s job. This script is one-device-at-a-time.

**Invocation:**
```bash
# Single device, all protocols
python3 tests/audit_getters_v2.py 192.168.1.4

# Single device, single protocol
python3 tests/audit_getters_v2.py 192.168.60.80 --protocol mops

# Full lab fleet
python3 tests/audit_getters_v2.py --fleet

# With JSON output
python3 tests/audit_getters_v2.py --fleet -o gate_check.json
```

**Fleet (hardcoded inside the script):** `.4` BRS50, `.254` GRS1042, `.80` BRS50-RM, `.83` GRS105, `.85` BRS50-L2S.

### `audit_getters.py` — the per-method describer

**Purpose:** describe the SHAPE of every getter's output (keys, types, structure, row counts) without comparing values. Used for version-to-version diffing.

**What it does:**
- Calls every read method
- Records `{keys, types, sample_values, row_count, structure}` per method
- Compare mode: diff two audit JSONs and report missing/extra methods, missing/extra keys, type mismatches

**When to use it:**
- Before starting a refactor, capture a baseline. After the refactor, compare.
- Confirming v1 → v2 schema migration didn't drop keys.

**When NOT to use it:**
- Not for live correctness — it doesn't validate values, only shapes.
- Not for parity — single-protocol only.

**Invocation:**
```bash
python3 tests/audit_getters.py 192.168.1.4 -o audit_today.json
python3 tests/audit_getters.py 192.168.1.4 --compare audit_old.json
```

---

## Write-side scripts

### `audit_setters.py` — declarative safe-set tests

**Purpose:** automated SET tests driven by `audit_safety.yaml`. Each test does set → verify → revert with gate trace capture.

**What it does:**
- Reads `tests/audit_safety.yaml` (`safe:` and `unsafe:` lists)
- For each safe entry: calls SET with `validate=True`, captures the gate trace, calls a verify GET, calls revert
- If gate rejects: retries with `validate=False` and records both
- Per-test JSON output if `-o` is given
- Prints PASS / GATE / MISMATCH / FAIL summary

**When to use it:**
- Smoke-testing the gate behavior on a sacrificial device after engine changes.
- Making sure newly-added setters survive ingress validation.

**When NOT to use it:**
- Not the full setter coverage — `test_setter_pairs.py` is more comprehensive (43 vs ~30 entries).
- Don't run on a production device; the safe-list only protects against gross damage, not against config churn.

**Invocation:**
```bash
python3 tests/audit_setters.py 192.168.60.85
python3 tests/audit_setters.py 192.168.60.85 --protocol mops
python3 tests/audit_setters.py 192.168.60.85 -o results/
python3 tests/audit_setters.py 192.168.60.85 --unsafe   # interactive, currently SKIPPED
```

**Companion file:** `audit_safety.yaml` — declarative test entries. Add new tests here, not in Python.

### `test_setter_pairs.py` — the comprehensive setter suite

**Purpose:** SET round-trip coverage for every simple upsert setter. 43 test entries covering global scalars, per-port settings, sub_tables, etc.

**What it does:**
- For each entry: `get` (capture original) → `set` (test value) → `get` (verify changed) → `set` (restore original) → `get` (verify restored)
- Per-port tests use port `1/3` (non-ring, non-management on the lab BRS50s)
- `setup` / `teardown` hooks for tests that need the feature enabled first
- `requires:` field for L2A/L3A-only methods (skips on lower SW level)
- `--only` and `--skip` for surgical runs

**When to use it:**
- Setter parity gate before a release.
- After an engine change that touches the SET pipeline (Gate 1, dispatch_batch, RowStatus lifecycle).
- Surgical re-test of one schema: `--only banner`.

**When NOT to use it:**
- Don't run on .80 (it's the ring) or .83 (L3 lab) without the `requires:` filter — there's no kill switch beyond your judgement.
- Don't run all 43 to "test something quick" — use `--only`.

**Invocation:**
```bash
python3 tests/test_setter_pairs.py 192.168.60.85
python3 tests/test_setter_pairs.py 192.168.60.85 --only banner_text dns_domain
python3 tests/test_setter_pairs.py 192.168.60.85 --skip devsec software
python3 tests/test_setter_pairs.py 192.168.60.85 --protocol snmp
```

**Note:** test definitions are hardcoded at the top of the file in a `TESTS = {...}` dict. Add new entries there. The release_matrix.py orchestrator (planned) will import this dict directly.

### `test_crud_pairs.py` — CRUD round-trip suite

**Purpose:** RowStatus CRUD lifecycle coverage. 11 entries: dns, ntp, syslog, ip_restrict, snmp_trap, radius, ldap, tacacs, user, port_security, static_binding.

**What it does:**
- For each entry: `get` (guard, clean stale) → `create` → `get` (verify exists) → `set` (upsert on index) → `get` (verify updated) → `delete` (by index) → `get` (verify gone)
- Handles user-provided index and runtime-discovered index
- `--cleanup` flag wipes stale test entries from a prior run
- `--only` for surgical

**When to use it:**
- Validating CRUD lifecycle after engine/driver changes (RowStatus, linked_tables, compound index).
- Confirming a CRUD-bearing schema rework didn't break the round trip.

**When NOT to use it:**
- Don't use it for non-CRUD setters — that's `test_setter_pairs.py`.
- Don't run on .85 — RowStatus tables are ring-friendly but the test entries are designed for .80.

**Invocation:**
```bash
python3 tests/test_crud_pairs.py 192.168.60.80
python3 tests/test_crud_pairs.py 192.168.60.80 --only dns ntp
python3 tests/test_crud_pairs.py 192.168.60.80 --cleanup
python3 tests/test_crud_pairs.py 192.168.60.80 --protocol snmp
```

---

## Fixture / replay scripts

### `capture.py` — multi-layer fixture capture

**Purpose:** record everything that happens on a single device call, at four boundaries, so it can be replayed offline.

**What it captures:**
- **tap1** — raw transport responses (SNMP walks, MOPS XML, SSH command output)
- **tap2** — driver `gather()` output (post-decode dict)
- **tap3** — engine output (schema-shaped, post-compute/lookup)
- **tap4** — NAPALM adapter output (post-shape, consumer-facing)

**When to use it:**
- Building a regression fixture before refactoring engine or driver code.
- Reproducing a bug offline (capture once, debug repeatedly without hitting the device).

**When NOT to use it:**
- Not a test runner — pairs with `test_replay.py` for assertions.
- Not for parity — `audit_getters_v2.py` is the parity tool.

**Invocation:**
```bash
python3 tests/capture.py 192.168.1.4
python3 tests/capture.py 192.168.1.4 --protocols mops snmp ssh
python3 tests/capture.py 192.168.1.4 --methods get_facts get_interfaces
```

**Output:** `tests/fixtures/<ip>/{mops,snmp,ssh}/<method>.json` plus `context.json` and `metadata.json`. Currently only `192.168.1.4` is captured.

### `test_replay.py` — pytest-based fixture replay

**Purpose:** offline regression tests using captured fixtures. No live device needed.

**What it does:**
- Loads fixtures from `tests/fixtures/<ip>/`
- Mocks the transport layer so engine sees the recorded tap1 data
- `test_engine` — tap1 → engine → compare against tap3
- `test_napalm` — tap3 → adapter shape → compare against tap4
- Standard pytest discovery; `-k` filters work

**When to use it:**
- CI / pre-commit gate (fast, no network).
- Refactoring engine internals without risking a regression.
- Testing on a plane.

**When NOT to use it:**
- Not for SET/CRUD — captures are read-only.
- Not for live verification — fixtures can be stale; live tools are authoritative.

**Invocation:**
```bash
/tmp/crude-engine/.venv/bin/pytest tests/test_replay.py -v
/tmp/crude-engine/.venv/bin/pytest tests/test_replay.py -k "mops and get_facts"
```

---

## Orchestration

### `audit_all.py` — legacy fleet orchestrator (being replaced)

**Purpose:** loop `audit_getters.py` and `audit_setters.py` across the lab fleet via subprocess, print summary lines.

**Status:** **being superseded by `release_matrix.py`** (see `docs/RELEASE_GATE.md`). Keep it for now as a fallback. Don't add features.

**When to use it:**
- Quick fleet sanity check before `release_matrix.py` exists.

**When NOT to use it:**
- Don't extend it. Don't depend on its output format. New work goes into `release_matrix.py`.

## Investigation workflow — `--inspect`

When the matrix tool reports a parity failure or a method behaves suspiciously,
use `--inspect` to drill in. It runs ONE method on ONE device across every
supported protocol, dumps the raw return data side-by-side, and runs the
parity check. **Never touches the matrix DB.** Pure investigation tool.

### CLI surface

```bash
# Look at get_interfaces on .80 — see actual MOPS vs SNMP vs SSH output
release_matrix.py --inspect --method get_interfaces --device 192.168.60.80

# Constrain to one protocol
release_matrix.py --inspect --method get_mac_address_table --device 192.168.60.80 --protocol snmp

# With engine pipeline trace — shows what the engine actually did per attribute
release_matrix.py --inspect --method get_interfaces --device 192.168.60.80 --protocol snmp --trace

# Bypass Gate 1/2 validation rejection — see underlying data even when it would normally fail
release_matrix.py --inspect --method get_xyz --device 192.168.60.80 --no-validate

# Combine: constrain to one protocol, capture trace, skip validation
release_matrix.py --inspect --method get_xyz --device 192.168.60.80 --protocol mops --trace --no-validate
```

### Engine flags exposed

| Inspect flag | Engine kwarg | What it does |
|---|---|---|
| (always set) | `napalm_compat=False` | Returns raw engine/schema output, no NAPALM reshaping |
| `--trace` | `trace=True` | Captures `device.last_trace`, dumps pipeline steps (attr, direction, input, output, step) |
| `--no-validate` | `validate=False` | Skips Gate 1/2 rejection — context still produced, just not enforced |
| `--protocol` | `optional_args={"protocol": ...}` | Constrains to a single protocol; default = run on every protocol that has wire support |

### What you get

- Per-protocol raw output with first-row sample (or scalar for flat methods)
- `time_ms` per protocol
- `--trace` dumps each pipeline step's attr/direction/input/output/step (compact, one line per step)
- Cross-protocol parity diff at the bottom — same `_compute_parity` the gate uses

### When to use it

- The matrix tool reports a parity failure → `--inspect` shows you what's actually different at the value level
- A getter "passes" the gate but you suspect silent value bugs → `--inspect` shows raw output
- Triaging a `#wire` or `#driver` finding → see exact returned values before reading code
- Adding `--trace` reveals exactly which pipeline step transformed the data wrong (value_map, regex, compute, lookup)
- Suspecting a wire / RFC INDEX decomposition issue → trace input dict shows raw walk keys (e.g. `'1'` vs `'1.1'` reveals key-format mismatch instantly)
- A method fails Gate 1/2 validation → `--no-validate` lets you see what the underlying call returned

### Worked example: catching the autoneg bug

```bash
release_matrix.py --inspect --method get_interfaces --device 192.168.60.80 --protocol snmp --trace
```

Trace output reveals:
```
attr=admin_status    input={'1': 1, '2': 1, '3': 1, ...}        ← keyed by ifIndex
attr=autoneg_enabled input={'1.1': 2, '2.1': 2, '3.1': 2, ...}  ← compound suffix, different MIB table
```

Two different key formats inside the same method → the engine's row-builder
can't cross-reference and `walked[autoneg_enabled]['1']` returns nothing →
autoneg_enabled silently defaults to False. Found in one command, no
throwaway script.

### When NOT to use it

- Setter / CRUD investigation — `--inspect` is read-only by design
- Bulk verification across many methods — use `--execute --kind read` then look at the rendered doc
- Anywhere the device write path is involved — inspect calls getters only

### The strong rule

**Do NOT write throwaway Python scripts that call `device.get_*()` for fault-finding.**
Use `--inspect` instead. The harness already knows about every method, every
protocol, every device, every engine flag. If the inspect mode is missing
something you need, **add a flag** — don't write a one-shot script that gets
deleted tomorrow. Reasons:

1. Throwaway scripts are deleted with `/tmp` cleanup or session end — investigation knowledge is lost
2. Easy to make mistakes (wrong creds, wrong protocol arg, missing `napalm_compat=False`)
3. Reinvents wiring the harness already has correctly
4. No shared state with the rest of the test infrastructure
5. Inconsistent invocation patterns across sessions

Add features to `--inspect`. Don't write scripts.

---

### `release_matrix.py` — release-gate orchestrator

THE tool that produces the per-cell matrix JSON used as the release gate.
Imports the internals of `audit_getters_v2.py`, `test_setter_pairs.py`,
`test_crud_pairs.py` (no subprocess), merges results into a hierarchical
JSON DB, supports surgical re-runs, generates `docs/RELEASE_MATRIX.md`
and `docs/TODO_HITLIST.md`.

**Built and validated.** See `docs/RELEASE_GATE.md` for the full design.

**Pipeline phases:**
```
gather → plan → execute → derive → render
```

- **gather**  — live read pass per device, populates `tests/device_state.json`
                (facts, ports, ring, management, unused_safe_to_touch)
- **plan**    — pure function: schemas + device_pool + device_state →
                `tests/release_test_plan.json` (no I/O)
- **execute** — one worker thread per device, dispatches jobs to `run_one_*`,
                writes cells to `tests/release_matrix.json` via lock+backoff
- **derive**  — auto-runs after any execute that included reads; updates
                `device_state.devices.<ip>.has_configured_from_gather`
                so the next plan/execute uses live truth
- **render**  — generates `docs/RELEASE_MATRIX.md` + `docs/TODO_HITLIST.md`

**CLI:**
```bash
# Surgical
release_matrix.py --method get_facts --protocol mops --device 192.168.1.4
release_matrix.py --schema mrp --device 192.168.60.80 --kind setter
release_matrix.py --method set_banner --device 192.168.60.85 --kind setter

# Pipeline phases (each independently runnable)
release_matrix.py --gather
release_matrix.py --plan
release_matrix.py --execute --kind read   # read-only sweep, no writes
release_matrix.py --execute --kind setter # setter sweep
release_matrix.py --execute --kind crud   # CRUD sweep
release_matrix.py --render

# Full gate (all phases in one)
release_matrix.py --gate

# Maintenance
release_matrix.py --reset       # wipe matrix DB
release_matrix.py --db-info     # one-line summary

# Filters (apply to any phase)
--scope mops snmp        # protocols in scope (default mops+snmp)
--device <ip>            # one device only
--method <name>          # one schema method only
--schema <feature>       # all methods of one schema
--protocol <mops|snmp>   # one protocol only
--kind <read|setter|crud># one job kind only
```

**Outputs:**

| File | Contract | Edited? |
|---|---|---|
| `tests/release_matrix.json` | Cell DB, hierarchical `results[schema][method_or_test_id][protocol][device]` | Never (auto-managed by MatrixDB) |
| `tests/release_test_plan.json` | Job manifest from plan generator | Never (regenerated each `--plan`) |
| `tests/device_state.json` | Per-device gather output + auto-derived `has_configured_from_gather` | Never (regenerated each `--gather` and after each `--execute --kind read`) |
| `docs/RELEASE_MATRIX.md` | Read-only scoreboard: summary, per-protocol, fleet, per-schema grid, perf, comms-lost | Never |
| `docs/TODO_HITLIST.md` | Failures grouped by `#bucket` tag, NEEDS TRIAGE for untagged | Never |

**Standing rules:**
- `safe_for: [read]` devices CANNOT receive setter/CRUD jobs at any code path. Verified.
- Every cell has a `verdict` (`pass`/`fail`/`error`/`exempt`/`not_applicable`/`comms_lost`/`not_run`)
- Worker per device, threads (not processes), I/O-bound parallelism
- Comms loss → worker stops, writes `WORKER_STOPPED` marker, other workers continue
- `not_run` only counts jobs in the LAST execute scope (filtered jobs aren't "missing")

### `audit_common.py` — shared utilities for tests/ scripts

Common code used by `release_matrix.py` and (eventually) `test_setter_pairs.py` /
`test_crud_pairs.py`. Anything shared between two or more test scripts lives
here so we don't duplicate it.

**Provides:**
- `gather_device(device, label)` — live read pass producing a per-device state
  dict (facts, ports, ring, management, unused_safe_to_touch, flattened
  safety variables). Pure function — no I/O outside the device handle.
- `gather_one_ip(ip, ...)` — convenience wrapper that opens, gathers, closes
  in one call. Useful for diagnostics.
- `load_all_method_metadata()` — reads every schema YAML, returns a flat dict
  of `{method_name: {feature, type, kind, protocols, primary_key, defaults,
  sub_tables}}`. Mirrors `audit_getters_v2.load_schemas` but covers all
  method kinds (read/setter/crud), not just reads.

**NOT a `crude_tools_common` cross-project library.** Just a tests/ utility.

**Standalone diagnostic mode:**
```bash
python3 tests/audit_common.py 192.168.1.4 --label BRS50-Office
# Prints the per-device gather state as JSON
```

### `safety_runner.py` + `safety_protocols.yaml` — CLAMPS-style pre/post hooks

Method-level safety wrapping for setters/CRUD that need ordering safety
(e.g., `set_mrp` shouldn't reconfigure a live ring without first admin-downing
the secondary ring port).

**Layering:** lives in `tests/`, NOT in `crude_engine/schemas/`. The engine
knows nothing about these hooks. They are TEST infrastructure, not engine
behavior. Production callers using `napalm-hios` directly don't get safety
wrapping — that's still their responsibility (or use a tool like CLAMPS).

**Format** (`safety_protocols.yaml`):
```yaml
protocols:
  set_mrp:
    description: "MRP changes need secondary ring port admin-down to prevent loops"
    requires_state: [ring_port_secondary]
    require_during:
      - target:
          read_method: get_interfaces
          write_method: set_interface
          index: "{ring_port_secondary}"
          field: admin_status
        must_equal: down
        # restore is implicit — captured live, restored after
```

**Pattern:** capture-on-entry / restore-on-exit. The runner reads the field's
current value before applying `must_equal`, restores after the wrapped
method returns (or fails). If the captured value already equals
`must_equal`, no change is made and no restore is needed.

**Variable substitution:** `{ring_port_secondary}` etc. resolve from
`tests/device_state.json` (gather phase output) at execute time, per device.
Missing variable → cell becomes `not_applicable` with reason "safety
prerequisites not satisfied" (does NOT bypass the safety).

**Used by:** the `release_matrix.py` worker dispatch wraps every setter/CRUD
call via `default_runner().run_with_safety(...)`. Methods without a protocol
declaration get a no-op wrap (run normally).

---

## Data files

| File | Read by | Purpose |
|---|---|---|
| `audit_safety.yaml` | `audit_setters.py` | Declarative safe-set test definitions |
| `wire_exemptions.yaml` | `audit_getters_v2.py`, `release_matrix.py` (planned) | Per-(wire_file, wire_attr, protocol) accepted gaps |
| `parity_exceptions.yaml` (in repo root, not `tests/`) | `parity_suite.py` (older) | Accepted cross-protocol diffs |
| `method_exemptions.yaml` (PLANNED) | `release_matrix.py` | Whole-method accepted gaps with reasons |
| `tag_map.yaml` (PLANNED) | `release_matrix.py` | Failure-pattern → tag mappings for auto-tagging |
| `fixtures/<ip>/...` | `test_replay.py` | Captured multi-layer fixtures |

---

## Standing test rules

1. **Surgical by default.** Use `--method` / `--only` / `--protocol` / `--device` to test ONE thing. Full-suite runs are for proof at the end of a work batch, not for debugging.
2. **Comms loss = stop and ask.** If a SET / CRUD run loses the device, stop the script, dump partial state, and ask the user before assuming cause. Never auto-retry, never assume the change broke it, never assume something else broke it.
3. **Test on the right device.** `.4` for prod read-only smoke, `.85` for sacrificial setters, `.80` for ring/CRUD, `.83` for L3/VRRP, `.254` for L3 prod read-only smoke.
4. **No throwaway scripts.** New test code goes into one of the existing scripts, into `release_matrix.py`, or into a YAML data file. If you can't find a home for it, ask before writing.
5. **Truth comes from execution.** Doc claims and prior JSON results are hints. The current script run is truth.

## Venv

```bash
/tmp/crude-engine/.venv/bin/python3 tests/<script>.py ...
```

If the venv doesn't exist, from this repo root (engine is not on PyPI yet; the napalm-hios 2.0 shim is a separate unpublished repo):
```bash
python3 -m venv /tmp/crude-engine/.venv
/tmp/crude-engine/.venv/bin/pip install -e .
```
