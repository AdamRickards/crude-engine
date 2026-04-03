# crude-engine — Operating Principles

## Purpose

The engine (`interpreter.py`) takes a method name, a protocol, a transport,
and user kwargs. It returns shaped data. It makes zero decisions about what data
means — those decisions live in YAML. Python executes. YAML declares.

Every change to the engine must have a clear answer to: which block does
this belong to, and why? If the answer is unclear, the change belongs in YAML.

---

## The Stack

```
USER INTENT         what the caller said, may be ambiguous or shorthand
ADAPTER→SCHEMA      load schema, resolve method, strip engine-internal flags
INTENT RESOLUTION   translate user shorthand into concrete engine inputs
GATE 1              adapter→schema: is this call structurally valid?
GATE 2              schema→wire: is this attr wired correctly?
PIPELINE            execute steps declared in steps.yaml, bidirectional
GATE 3              engine→wire: does the transformed value satisfy wire constraints?
TRANSPORT           gather/set on the device using the active protocol
WIRE                generated YAML, device truth, never edited by hand
DEVICE              the physical target
```

Each layer has one job. No layer reaches into another layer's concerns.

---

## Block Definitions

### Block 1 — Adapter → Schema boundary
**What it does:** Load the schema for the requested method. Extract `method_def`.
Pop `debug` and `validate` from kwargs — these are engine flags, not user data.
Determine direction: getter (egress) or setter/create/delete (ingress).

**What it must not do:** Know anything about wire names, OIDs, protocol specifics,
or output shaping. It hands a clean method_def and cleaned kwargs to the next block.

**Where it lives:** Top of `execute()`.

---

### Block 2 — Intent Resolution
**What it does:** Translate everything ambiguous in user input into concrete values
the engine can act on without further interpretation.

Responsibilities (all must complete before any gate or pipeline runs):
- Dotted path kwargs (`"http.enabled"`) → flat kwargs (`http_enabled`)
- Nested dict kwargs (`http={"enabled": True}`) → flat kwargs
- `index="all"` → full index list via schema `key_map` context map
- Index list filtered by `index_filter` regex declared on the method
- `is_` prefix aliases if declared

**What it must not do:** Touch wire names, call the transport, or make validation
decisions. It only resolves what the user meant.

**Where it lives:** `_resolve_intent()` — called once, before any gate.

**Design rule:** If a future shorthand needs resolving (e.g. `index="active"`),
it goes here and nowhere else. The schema declares what it means. This block
executes it.

---

### Block 3 — Gate 1 (Adapter → Schema)
**What it does:** Confirm the call is structurally valid against the schema.
- Field exists in schema attributes
- Field is writable (access allows it)
- Method permits this field (fields: scope)

**What it must not do:** Check wire files, call the transport, or transform values.

**Catches:** Caller mistakes — wrong field name, read-only field, out-of-scope field.

---

### Block 4 — Gate 2 (Schema → Wire)
**What it does:** Confirm each schema attr is correctly wired.
- Wire source file exists
- Wire attribute exists in that file
- Protocol source exists for active protocol
- Wire access is not read-only

**What it must not do:** Transform values or touch the transport.

**Catches:** Schema authoring mistakes — broken wire reference, wrong source name.

---

### Block 5 — Pipeline Executor
**What it does:** Run the steps declared in `steps.yaml` in the correct direction.
- Egress (GET): top → bottom
- Ingress (SET/CREATE/DELETE): bottom → top

Steps are declared in YAML. The executor runs them. It does not decide which
steps apply — the schema and steps.yaml do.

For a list of indexes (resolved in Block 2): the pipeline runs once per index.
This is iteration, not recursion. The pipeline does not call `execute()` or
`_execute_ingress()` again — it iterates internally over the resolved index list.

**What it must not do:** Make decisions about field validity (gates do that),
resolve user intent (Block 2 does that), or know about specific protocols.

**Design rule:** `_translate` is the single choke point. Every step runs through
it. Debug trace appends here and nowhere else. If a step is not in steps.yaml,
it does not run.

---

### Block 6 — Gate 3 (Engine → Wire)
**What it does:** Validate the transformed value against wire constraints.
- min/max range from wire `validation:`
- allowed values list from wire `validation:`

**What it must not do:** Know about schema field names or user intent.
If the wire YAML has no validation block, the value passes through — the device
decides.

**Catches:** Value mistakes — number out of range, value not in allowed set.

---

### Block 7 — Transport
**What it does:** Execute the actual device communication.
- Gather: bulk fetch all attrs scoped to the current method (not all attrs in schema)
- Set: batch write transformed values
- Scoping: only attrs present in the method's defaults/fields are gathered

**What it must not do:** Transform values, validate, or know about schema structure
beyond the list of attrs it has been handed.

**Design rule:** The transport receives a list of wire attr+source pairs and
returns raw values. Everything above the transport is protocol-agnostic.
Everything below the transport is engine-agnostic.

---

## Invariants

These must hold after every change:

1. **YAML declares, Python executes.** No hardcoded field names, OIDs, protocol
   names, or enum values in the engine. These live in YAML files.

2. **Intent resolution runs once, before everything else.** No intent logic
   inside gates, pipeline steps, or transport calls.

3. **Gates are read-only.** They inspect and either pass or raise. They do not
   modify kwargs, values, or state.

4. **The pipeline does not recurse into `execute()`.** Index iteration is a loop
   inside the pipeline, not a recursive dispatch call. Recursive re-entry
   re-runs gates and intent resolution — that is always wrong.

5. **Each block has one failure mode.** Gate 1 raises on schema violations.
   Gate 2 raises on wire violations. Gate 3 raises on value violations.
   Transport raises on device communication failures. No block swallows
   exceptions silently.

6. **`import` statements belong at module level.** No imports inside functions
   or loops.

7. **Trace has two homes: `_translate` for pipeline steps, gates for gate results.**
   Pipeline step trace (`{step, attr, direction, input, output}`) appends in `_translate`.
   Gate trace (`{gate, check, result}`) appends in the gate function that produced it.
   No trace appends anywhere else.

---

## Where New Code Goes

| Concern | Block |
|---|---|
| New user-facing shorthand (e.g. `index="active"`) | Block 2 — Intent Resolution |
| New schema primitive validation (e.g. new access level) | Block 3 — Gate 1 |
| New wire file format check | Block 4 — Gate 2 |
| New pipeline step (e.g. new transform type) | Block 5 — steps.yaml + crude.py |
| New wire value constraint type | Block 6 — Gate 3 |
| New protocol transport | Block 7 — transport class + transport_registry.py |
| New output shape | Schema YAML or adapter YAML — not interpreter.py |
| New method type (create/delete/upsert) | Block 1 dispatch + Block 5 direction |

If a proposed change does not fit cleanly into one row of this table, the change
is either in the wrong place or should be expressed in YAML instead.

---

## What the Engine Must Never Contain

- Hardcoded OIDs, MIB names, or field names
- Protocol-specific branching (`if protocol == 'snmp'`)
- Silent exception swallowing (`except Exception: pass`)
- Output shaping logic (belongs in adapter or crude.py)
- Credential handling
- Device-specific knowledge of any kind
- Recursive calls to `execute()` or any pipeline runner for index iteration
