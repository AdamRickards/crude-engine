# Schema Primitives Reference

> Every YAML key that can appear in a schema attribute or method definition,
> which pipeline stage handles it, and which helper function implements it.

## Attribute-Level Primitives

| Key | Type | Direction | Stage | Handler | Interactions |
|-----|------|-----------|-------|---------|-------------|
| `wire:` | str | both | Gate 2 resolve (both), Gate 3 gather/dispatch | `_gate2_resolve`, `gather_and_decode`, `dispatch_batch` | requires `source:` |
| `source:` | str | both | Gate 2 resolve (both), Gate 3 gather/dispatch | `_gate2_resolve`, `gather_and_decode`, `dispatch_batch` | requires `wire:` |
| `value_map:` (dict) | dict | both | pipeline step | `step_value_map` | egress: wire→human, ingress: human→wire (reverse) |
| `value_map:` (str) | str | both | pipeline step | `step_value_map` | context map reference (e.g. `ifindex` → `ifindex_map`). Lazy loaded via `_resolve_context_map` |
| `key_map:` (on attr) | str | egress | pipeline step | `step_key_map` | remaps dict keys via context map |
| `bit_map:` (dict) | dict | both | CRUDE transform | `crude_bits` via `to_bits` | inline bit position → name mapping |
| `bit_map:` (str) | str | both | CRUDE transform | `crude_bits` via `to_bits` | named reference in wire YAML `value_maps` |
| `collect: walk` | str | egress | resolve | `_egress_gather` | gathers as dict, resolves to `list(dict.values())` at read time |
| `compute:` | dict | egress | Phase C formatters (scalar), per-row in table shaper | `_apply_compute`, `_shape_table_output` | keys: `from`, `format`, `expr`, `fallback`, `sort` |
| `assemble:` / `set_format:` | str | ingress | pre-pipeline | `_apply_assemble` | reverse of compute — builds one wire value from multiple kwargs |
| `membership_of:` | str | egress | Phase C formatters | `_apply_membership` | cross-table boolean: is key in that attr's value set? |
| `lookup:` | dict | egress | Phase C formatters | `_apply_lookup` | cross-table join. Keys: `from`, `index_field`, `resolve` |
| `lookup.index_field` | str | egress | gather | `_egress_gather` | injected into proto_source so driver rekeys the table |
| `regex:` | str | egress | Phase C formatters | `_apply_regex` | extract/transform via regex pattern |
| `access:` | str | ingress | Gate 2 | `_gate2_resolve` | `r` = read only, `ru` = read+upsert, `crud` = full lifecycle |

## Method-Level Primitives

| Key | Type | Direction | Stage | Handler | Interactions |
|-----|------|-----------|-------|---------|-------------|
| `type:` | str | both | coordinator dispatch | `execute_resolved` | `dict`, `list` = egress. `upsert` = ingress. `create`, `delete` = CRUD |
| `defaults:` | dict | egress | output contract, method scope | `_pipeline_egress`, `_build_method_scope` | defines which attrs to gather and which keys appear in output |
| `fields:` | list | ingress | Gate 1 | `_gate1_validate` / `_validate_schema` | restricts which attrs can be SET by this method |
| `schema:` | str | both | method loading | `_load_method` | method alias — reuse another method's definition |
| `index_key:` | str | ingress | intent resolution, CRUD index | `_resolve_intent`, `_resolve_crud_index_create`, `_resolve_crud_index_delete` | which kwarg/default IS the row index |
| `key_map:` (on method) | str | both | index resolution, output shaping | `_resolve_index`, `_shape_table_output` | remap output dict keys or reverse index via context map |
| `primary_key:` | str | egress | output shaping | `_shape_table_output`, `_pipeline_egress` | which attr provides the table row keys |
| `required:` | list | ingress | CRUD index resolution | `_resolve_crud_index_create` | required fields for create — checked for index derivation |
| `row_status:` | str | ingress | CRUD lifecycle | `_pipeline_crud`, `_dispatch_crud_create`, `_dispatch_crud_delete` | RowStatus column name for create/destroy lifecycle |
| `linked_tables:` | list | ingress | CRUD dispatch | `_dispatch_crud_create`, `_dispatch_crud_delete` | multi-table CRUD — internal loop per table (NOT recursive) |
| `sub_tables:` | dict | egress | output shaping | `_apply_sub_tables` | nest flat attrs into sub-dicts. Keys: `primary_key`, `field_map`, `defaults`, `key_map` |
| `index_fields:` | list | egress | table shaping | `_shape_table_output`, `step_index_codec` | compound index decomposition |
| `index_type:` | str | egress | table shaping | `_shape_table_output` | compound index encoding type (e.g. `implied_string`) |
| `index_filter:` | str | ingress | intent resolution | `_resolve_intent` | regex to filter index list (e.g. exclude `cpu/1` from `all`) |
| `attributes:` (on method) | dict | both | method loading | `_load_method` | method-scoped attr overrides — same name, different wire per method |
| `create_method:` | str | ingress | CRUD dispatch | `_dispatch_crud_create` | RowStatus creation style: `createAndWait` (default) or `createAndGo` |

## Engine Flags (popped from kwargs, not schema primitives)

| Key | Default | Purpose |
|-----|---------|---------|
| `trace` | `False` | Enable pipeline trace — stored on `engine.last_trace` / `device.last_trace` |
| `debug` | `False` | Adapter-level: enables trace + transport logging. Never reaches engine |
| `validate` | `True` | Enable validation gates — `False` skips rejection, gates still produce context |
| `index` | `None` | Row index for per-row operations. Also accepted as first positional arg |
| `interface` | `None` | Alias for `index` (popped from kwargs) |

## Wire YAML Keys (read by engine, not authored in schema)

| Key | Where read | Purpose |
|-----|-----------|---------|
| `syntax:` | CRUDE matrix lookup | MIB syntax → crude_* function |
| `type:` | CRUDE matrix lookup, wire_type_defaults | schema data type (boolean, integer, string, list) |
| `access:` | Gate 2 (`_gate2_resolve`) | read/write permission |
| `validation:` | Gate 2 (`_gate2_check_constraints`) | `min`, `max` range constraints |
| `sources:` | Gate 2 + Gate 3 | per-protocol source definitions |
| `bit_map:` | CRUDE transform | inline or named bit position mapping |
| `index_type:` | compound index decomposition | `implied_string` etc. |
| `index_field:` | gather, driver | which field is the table index |
| `value_maps:` | CRUDE transform | wire-level named maps (referenced by `bit_map:` string) |

## Protocol YAML Keys

| Key | Where read | Purpose |
|-----|-----------|---------|
| `wire_type_defaults:` | `_resolve_tag` in base driver | fallback CRUDE function per type when no matrix match. Supports `{function, args}` |
| `execute_methods:` | `_execute_transport` | transport-direct operations list |
| `unsigned_syntaxes:` | SNMP driver | ASN.1 types needing Unsigned32 encoding |
| `column_overflow:` | SSH driver | table parser behavior |

## Primitive Interactions

- `compute.from` references other schema attrs → `_build_method_scope` expands scope to include dependencies
- `lookup.from` references other schema attrs → scope expansion includes them
- `membership_of` references another schema attr → scope expansion includes it
- `sub_tables.field_map` values are schema attr names → scope expansion includes them
- `collect: walk` and normal attrs sharing same `wire:` + `source:` → no collision, collect resolved at read time from same `raw_walked` data
- `value_map: ifindex` on attr + `key_map: ifindex` on method → different operations: value_map maps VALUES, key_map maps KEYS
- `index_filter` only applies when index is a list (from `all` expansion) — single index passes through unchanged
- Method-scoped `attributes:` overrides schema-level attrs with same name — `_load_method` merges method on top of schema
