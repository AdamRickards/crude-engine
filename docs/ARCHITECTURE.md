# Architecture — Three-Gate Model (v2.9)

> Wire is generated. Schema is authored. Adapter is per-consumer.
> Context is gate output. Every layer operates on context produced by the gate it passed through.
> No gate transit, no context, no operation.

## How It Works

```
   You                    YAML                   Engine                 Device
    │                      │                       │                      │
    │  "I want DNS"        │                       │                      │
    │─────────────────────▶│                       │                      │
    │                      │  schemas/dns.yaml     │                      │
    │                      │  ┌─────────────────┐  │                      │
    │                      │  │ get_dns:        │  │                      │
    │                      │  │   defaults:     │  │                      │
    │                      │  │     enabled: F  │  │                      │
    │                      │  │ attributes:     │  │                      │
    │                      │  │   enabled:      │  │                      │
    │                      │  │     wire: ...   │──▶  Gate 1 → Gate 2     │
    │                      │  │     source: dns │  │  Gate 3 → driver  ──▶ SNMP walk
    │                      │  └─────────────────┘  │  pipeline transform ◀── hex bytes
    │                      │                       │  Gate 1 exit check   │
    │  d.get_dns()         │                       │                      │
    │◀─────────────────────│───────────────────────│                      │
    │  {"enabled": True}   │                       │                      │
```

## Data Flow — Three Gates, Both Directions

```
[user intent]
  → resolve_intent (schema kwargs)
    → GATE 1 INGRESS (valid? here's SchemaContext)
      → engine translate (schema transforms per kwarg)
        → GATE 2 INGRESS (wire exists? access? here's WireContext)
          → GATE 3 INGRESS (CRUDE encode, dispatch_batch)
            → DRIVER → TRANSPORT → DEVICE

[device response]
  → TRANSPORT → DRIVER
    → GATE 3 EGRESS (gather_and_decode, CRUDE decode)
      → GATE 2 EGRESS (wire context for engine, validate=False)
        → engine translate (schema transforms per attr)
          → GATE 1 EGRESS (output matches schema defaults?)
            → ADAPTER → user
```

Every arrow is a gate transit. Every gate produces context the next layer needs.
Remove a gate, the next layer has nothing to work with.

## Layer Terminology

```
ADAPTER     = hios.py (future: gnmi.py, rest.py)
             Consumer-facing. Connection management, output reshaping.

SCHEMA      = schemas/*.yaml (authored by humans)
             Declares methods, attributes, wire pointers, value_maps.

ENGINE      = interpreter.py
             YAML-driven pipeline. Gates, translate, shape output.

WIRE        = wire/*.yaml (generated from device MIBs)
             Device truth. OIDs, syntax, type, access, sources.
             Protocol overlays in wire/{protocol}/ (e.g. wire/ssh/)

DRIVER      = base.py + {snmp_driver.py, mops_driver.py, ssh_driver.py}
             Extends BaseDriver. Owns CRUDE encode/decode, transport dispatch.
             dispatch_batch (ingress), gather_and_decode (egress).

TRANSPORT   = {snmp_transport.py, mops_transport.py, ssh_transport.py}
             Raw protocol I/O. Sessions, auth, walks, gets, sets.

REGISTRY    = transport_registry.py
             Single source of truth: driver class, transport class,
             protocol YAML, wire overlay directory — per protocol.
```

## File Structure

```
crude_engine/
  wire/                      # Generated from device (Gemini/MIB/MOPS)
    dns.yaml                 # MIB-named files for complete coverage
    if.yaml, bridge.yaml     # Context map sources (ifindex, bridge_port)
    ssh/                     # SSH wire overlays (CLI sources)
      dns.yaml, usermgmt.yaml, ...
  schemas/                   # Authored by humans — the switchboard
    dns.yaml, ntp.yaml, interface.yaml, ...
  engine/                    # Pipeline engine (protocol-agnostic)
    interpreter.py           # 3 dataclasses, 3 gates, pipeline, dispatch
    crude.py                 # 9 crude_* bidirectional transforms
    crude_matrix.yaml        # (syntax, type) → function mapping
    steps.yaml               # Step registry (transition + formatter)
    context_maps.yaml        # Declares ifindex, bridge_port wire sources
  drivers/                   # Protocol drivers + transports
    base.py                  # BaseDriver, dispatch_batch, gather_and_decode
    snmp_driver.py + SNMP.yaml
    mops_driver.py + MOPS.yaml
    ssh_driver.py + SSH.yaml
    snmp_transport.py, mops_transport.py, ssh_transport.py
  transport_registry.py      # Single source of truth for all protocol mappings
```

## The Three Gates

### Gate 1 — Schema Contract (interpreter.py)

Owns: `SchemaContext`. The boundary between adapter and engine.
- **INGRESS**: validates kwargs against schema (field exists, value_map keys valid, method scope). Returns `SchemaContext` (schema_attrs, method_def, methods, defaults, primary_key, index_fields, feature_id).
- **EGRESS**: validates output matches `defaults` contract (all declared keys present). Returns validated response.
- Cannot: touch wire YAMLs, protocol, transport.
- `validate=False`: skips rejection, still produces context.

### Gate 2 — Wire Contract (interpreter.py)

Owns: `WireContext`. The boundary between engine and wire.
- **INGRESS**: loads wire YAML, resolves wire attr, checks access (`"u"` or `"c"`), resolves protocol source. Returns `WireContext` (wire_def, wire_attr, proto_src, value_maps, access, wire_name, wire_source, syntax, schema_type, validation).
- **EGRESS**: same resolution, no access check. Returns `WireContext`.
- Cannot: CRUDE encode/decode (Gate 3), transport dispatch (Gate 3).
- `validate=False`: skips rejection, still produces context.
- **Sole wire accessor**: no `load_wire` calls outside Gate 2 (except `get_capabilities` infrastructure).
- **Sole access checker**: no access checks outside `_gate2_resolve`.

### Gate 3 — Encode/Decode + Transport (base.py)

Owns: CRUDE encode/decode, protocol field extraction, transport dispatch.
- **INGRESS** (`dispatch_batch`): receives `(wire_name, translated_value, WireContext)` tuples, CRUDE encodes, extracts protocol field names, groups by table, dispatches to transport. MOPS groups by (mib, table) for atomic SET. SNMP builds OID list. SSH dispatches per-command.
- **EGRESS** (`gather_and_decode`): receives WireContext list, builds sources, dispatches gather to transport, CRUDE decodes return values.
- Cannot: know about schemas, translate values, check access (Gate 2 did that).

## Public API

```python
# Adapter calls engine
resolved = engine.resolve_intent(method_name, is_setter=True, **kwargs)
result = engine.execute_resolved(resolved, protocol, transport)

# ResolvedIntent is frozen — protocol/transport-independent
# execute_resolved dispatches through all 3 gates

# Trace is a side channel
result = device.get_dns(trace=True)
trace = device.last_trace  # list of pipeline step records
```

`execute()` is a backward-compat wrapper. `_call()` in hios.py is the single adapter entry point for all verbs.

## Context Maps

Device-specific mappings (ifindex→port name, bridge_port→port name) are context maps. Resolved lazily on first use via `_resolve_context_map()`.

- **Declared** in `engine/context_maps.yaml` — points at real generated wire files
- **Resolved** through Gate 2 → Gate 3 pipeline (no direct device I/O, no protocol branching)
- **Cached** per session (`is not None` check — empty `{}` is valid resolved-but-empty)
- **Zero I/O at connect**: `build_context()` stores refs only. Maps populate on first getter that needs them
- **No protocol-specific branching**: wire declares what's available. SSH has no MIB sources → empty proto_src → empty map → raw values used. Works for any future protocol (Modbus, gNMI)
- **Dependencies**: bridge_port depends on ifindex (cross-reference). Declared in YAML

Schema declares: `value_map: ifindex` or `key_map: ifindex`
Engine resolves: `_resolve_context_map("ifindex")` — one function replaces all 5 former lazy-resolve blocks.

## The Three Files

### 1. Wire YAML (generated, device truth)

Owner: Machine-generated from MIB/MOPS/webUI proxy. Never hand-edited.
Changes when: Firmware updates add/remove MIB objects.
**Full spec**: See `docs/WIRE_SPEC.md` for generation pipeline, file locations, and format details.
**Not in git**: Wire YAMLs are generated per firmware version from `local/reference/` sources.

**Protocol-specific overlays**: `load_wire()` checks for `wire/{protocol}/{wire_id}.yaml` via `transport_registry.get_wire_overlay_dir()`. SSH CLI sources live in `wire/ssh/`. SNMP/MOPS use base wire files only. Adding overlays for a new protocol = one `wire_overlay_dir` entry in the registry.

```yaml
# wire/dns.yaml
version: 2.7.0
feature: dns
attributes:
  hm2dnsclientadminstate:
    syntax: HmEnabledStatus
    type: boolean
    access: ru
    sources:
      snmp: {read: {oid: 1.3.6.1.4.1.248.11.90.1.1.1}}
      mops: {mib: HM2-DNS-MIB, table: hm2DnsClientGroup, field: hm2DnsClientAdminState}
```

### 2. Schema YAML (authored, human intent)

Owner: Driver developer (us).
Changes when: We add/change exposed functionality.
**Responsibility**: Maps human-readable names to MIB-named wire files. Declares schema-level operations.

**Schema primitives** (declared in YAML, executed by engine):

Attribute-level:
- `wire:` + `source:` — attribute → wire attribute mapping
- `value_map:` — dict: inline enum decode/encode (GET: wire→human, SET: human→wire). String: context map reference (e.g. `ifindex` → resolve from `ifindex_map` in context)
- `key_map:` — remap dict keys via context map (e.g. `ifindex` → port names)
- `bit_map:` — dict: inline bit position names. String: named reference in wire YAML `value_maps`
- `access:` — attribute-level access override (r, ru, crud)
- `collect:` — shape walked data. Transition step (runs in YAML key order). String shorthand: `collect: value` (first/only value as scalar), `collect: list` (all values as list). Dict form: `collect: {type: value, key: "1"}` (specific row by key), `collect: {type: list, filter: "active"}` (values matching filter). Handles both dict and list input. Unknown types raise ValueError
- `compute:` — derive value from other gathered attrs. Sub-keys: `format:` (string template), `expr:` (Python eval with restricted builtins: `len`, `str`, `int`, `list`), `fallback:` (use this attr if `from:` fields missing), `sort: natural` (natural sort dict keys — ports before non-ports, numeric segments sorted numerically), `from:` (list of source attr names)
- `set_format:` — assemble value from multiple schema kwargs on SET path (reverse of `compute:`). Template fields (e.g. `{vlan}`, `{mac}`) consumed after assembly, method `fields:` respected
- `index_filter:` — targeted cell read from indexed table. Resolves human name via attr's own `value_map` (e.g. `mac-based-port-security` → `7`). SNMP: direct GET at `OID.index` (no walk). MOPS: filters `get_multi` result. Bidirectional — same resolution on ingress
- `membership_of:` — cross-table boolean check ("is this key in that table?")
- `lookup:` — cross-table join chain (`from:`, `index_field:` override, `resolve:` expression)
- `regex:` — extract/transform value with regex pattern. Transition step (runs in YAML key order, per-value on dicts). String config: `regex: '(\d+)$'` returns group(1). Dict config: `regex: {regex: '(\d+)\.(\d+)', format: '{0}.{1}'}` for multi-group format. Preserves input shape — dict in → dict out, scalar in → scalar out. Combine with `collect: value` before `regex:` when a walk attr needs scalar extraction

Method-level:
- `type:` — CRUDE operation: `dict`, `list`, `upsert`, `create`, `delete`
- `defaults:` — output contract (only these keys appear in GET output, defines method gather scope)
- `fields:` — write scope (only these attrs can be SET by this method)
- `schema:` — method alias (reuse another method's definition)
- `index_key:` — which field IS the row index
- `key_map:` — remap output dict keys via context map
- `primary_key:` — table key field for table-type methods
- `required:` — required fields for create operations
- `row_status:` — RowStatus column name for CRUD lifecycle
- `linked_tables:` — multi-table CRUD (ordered RowStatus lifecycle across N tables)
- `sub_tables:` — nest flat attrs into sub-dicts in output
- `index_fields:` — compound index decomposition (egress: split walk suffix into fields)
- `index_type:` — compound index encoding type (e.g. `implied_string`)
- `attributes:` — method-scoped attribute overrides (same attr name, different wire per method)

### 3. Adapter (per-consumer, shaping)

Owner: Integration developer.
Changes when: Consumer spec changes (NAPALM version, gNMI model).

NAPALM standard getters accept `napalm_compat=True`. `True` = reshape for NAPALM spec. `False` = canonical engine output. All other methods auto-discover via `__getattr__`.

## Layer Rules

| | Adapter (NAPALM) | Schema | Engine | Wire | Driver | Transport |
|---|---|---|---|---|---|---|
| **Owns** | Method names, output shaping | Intent, attribute mapping | Gates, dispatch, pipeline | MIB truth, OIDs, access | CRUDE encode/decode, dispatch_batch, gather_and_decode | Session, auth, raw I/O |
| **Can** | Rename fields, reshape dicts | Declare what to expose, join tables | Read any YAML, call drivers via gates | Declare sources per protocol | Resolve tags, apply pipeline | Send/receive raw data |
| **Cannot** | Know about OIDs or MIB names | Know about protocol encoding | Hardcode protocol behavior, sniff data | Interpret data meaning | Know about schemas | Decide what to gather |

## CRUDE Matrix

The CRUDE matrix maps `(syntax, type)` pairs to bidirectional transform functions. Declared in `crude_matrix.yaml`, executed by `crude.py`.

**9 crude_* functions**: `crude_boolean`, `crude_numeric`, `crude_text`, `crude_timestamp`, `crude_bits`, `crude_octet`, `crude_address`, `crude_enum`, `crude_taddress`. Each handles both directions (egress: wire→Python, ingress: Python→wire).

**Resolution order**: CRUDE matrix (syntax+type) → wire_type_defaults (type only) → pass through.

## Pipeline Steps

All attribute transforms run through `_translate` in YAML key order. Steps are registered in `steps.yaml`.

**Transition steps** (bidirectional, run per-attribute):
- `value_map:` — enum translation
- `key_map:` — dict key remapping via context map
- `index_fields:` — compound index decomposition/encoding
- `collect:` — shape walked data
- `regex:` — pattern extraction

**Formatter steps** (single-direction, run as batch after translate):
- `compute:` — derive from other attrs (egress)
- `assemble:` / `set_format:` — build wire value from multiple kwargs (ingress)
- `lookup:` — cross-table join (egress)
- `membership_of:` — cross-table boolean check (egress)
- `sub_tables:` — nest flat attrs into sub-dicts (egress)

## Principles

- **Wire is truth** — generated from device, never hand-edited.
- **Schema is intent** — human authored, declares what's exposed.
- **Adapter is consumer** — per-consumer shaping, doesn't own data.
- **Engine reads contracts, never sniffs data** — if the engine checks data to decide processing, the schema is missing a declaration.
- **No special cases** — when something breaks, fix the YAML declaration, not the engine.
- **Gates always produce or raise** — no try/except around gate calls. If a gate fails, the operation fails. `validate=False` skips rejection, still produces context.
- **No protocol-specific branching in the engine** — wire declares what's available per protocol.
- **Each file has one owner, one reason to change, one test strategy.**
