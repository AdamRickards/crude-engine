# Changelog

## Post-v2.9 Enhancements

### MOPS egress batching — one HTTP round trip per getter

`_egress_gather` no longer groups by wire source and calls `gather_and_decode` per group. All wire contexts are flattened into a single gather call — the driver owns batching strategy. MOPS merges everything into one `get_multi()` POST. SNMP categorizes by walk method. SSH deduplicates by command. No engine branching on protocol.

- **Multi-source getters now match v1 performance**: `get_snmp_config` 4→1 POST, `get_interfaces` 3→1, `get_remote_auth` 3→1, `get_lldp_neighbors_detail` 3→1
- **Context maps batched into gather**: ifindex and bridge_port tables are injected into the same gather batch instead of separate `_resolve_context_map` round trips. First getter that needs a context map pays zero extra cost — the map data arrives with the getter data. Subsequent getters hit cache as before
- **Cold-start elimination**: `get_gvrp` dropped from 1956ms to 630ms (was paying 2 extra round trips for bridge_port cascade). `get_sflow_sampler` dropped from 1803ms to 506ms
- **78/78 getters verified** on MOPS, SNMP, SSH — no breakage

### Wire overlay attr-level overrides

`load_wire()` overlay merge now copies all attr-level keys from SSH overlays (type, syntax, etc.), not just sources. This lets SSH overlays declare `type: string` when the base wire says `type: integer` — CRUDE uses the right transform per protocol. Previously overlays could only add protocol sources.

### Table output keying fix

`_shape_table_output` was using raw wire index (`index_field`) as output key when `key_map` was set, instead of the `primary_key` attribute value. This caused LLDP neighbors to return `lldpRemIndex` values (74, 94, 102) instead of port names. Fixed: output key always comes from `primary_key` attribute value, `key_map` remaps after. One line change.

### Files changed

- `engine/interpreter.py`: `_egress_gather()` flattened gather, `_collect_context_map_needs()`, `_get_context_map_spec()`, `_populate_context_maps()` — context map wire contexts injected into batch
- `drivers/` — no changes. Drivers already handled mixed-source input

---

## 2.9.0

### Architecture — Three-Gate Model

Gates as gatekeepers — every layer operates on context produced by the gate it passed through. No gate transit, no context, no operation.

- **Gate 1** (Schema Contract): `SchemaContext` dataclass. Validates kwargs on ingress, validates output matches `defaults` on egress. Boundary between adapter and engine
- **Gate 2** (Wire Contract): `WireContext` dataclass. Sole wire accessor (`_gate2_resolve`), sole access checker. 10-field frozen dataclass. `validate=False` skips rejection, still produces context
- **Gate 3** (Encode/Decode): `dispatch_batch` on BaseDriver (ingress — atomic multi-attr SET), `gather_and_decode` (egress). CRUDE encode/decode moved from engine to driver layer
- **Public API**: `resolve_intent()` → `execute_resolved()`. `ResolvedIntent` frozen dataclass. `_call()` single adapter entry point
- **Context maps**: lazy resolution via `_resolve_context_map()`, declared in `context_maps.yaml`, zero device I/O at connect time. No protocol-specific branching — wire declares what's available
- **Registry**: `transport_registry.py` single source of truth — driver class, transport class, protocol YAML, wire overlay directory per protocol
- **Wire overlays**: moved from `*-ssh.yaml` naming to `wire/ssh/` directory structure
- **Trace/debug separation**: `trace=True` (engine, pipeline recording via `last_trace`), `debug=True` (adapter, transport logging)
- **`napalm_compat`**: all NAPALM standard getters accept `napalm_compat=True` for future canonical output reshaping

### Deleted

`step_source_bind`, `_build_pipeline_ctx`, `_execute_v28`, `_validate_wire`, `_gate2_wire`, `_gate1_schema`, `_build_context`, `_get_wire_source`, `_register_napalm_shapes`, `shape_registry`, `context-sources.yaml`

### File renames

`SNMP.py` → `snmp_driver.py`, `MOPS.py` → `mops_driver.py`, `SSH_gather.py` → `ssh_driver.py`, `ssh.py` → `ssh_transport.py`

### Function renames

`_resolve_intent_v28` → `_resolve_intent`, `_resolve_intent` → `_flatten_kwargs`

### Adapter cleanup (post-refactor)

- **Protocol-free adapter**: zero protocol names in hios.py. `_transports` dict replaces `self.ssh`/`self.snmp`/`self.mops`/`self.offline`. `_try_connect` uses registry `port_key`/`default_port`. `_engine_protocol()` via `get_engine_protocol()`. `_ensure_execute_transport(method)` finds protocol by capability
- **Registry extended**: `engine_protocol`, `port_key`, `default_port`, `DEFAULT_PREFERENCE` (mops > snmp > ssh). Protocol validation on init
- **`execute()` simplified**: no debug/trace compat tuple return. Trace via `last_trace` side channel only
- **`release_cleanup.py`**: replaces `toolclean.py`, cleans package artifacts (pycache, egg-info, .pyc, backup tarballs) + tools
- **Removed**: `ncclient` dependency (skeleton leftover), `examples/` directory (v1 era), `interpreter.tar.gz` backup
- **Version**: 2.9.0 in setup.py + version.py

---

## 2.8.0

### Interpreter decomposition

Decomposed monolithic `_execute()` into coordinator + 3 pipeline runners + named helpers. Each block has one job. Dispatch driven by `method_def.get("type")` from YAML.

- **3 pipeline runners**: `_pipeline_egress`, `_pipeline_ingress`, `_pipeline_crud`
- **Validation gates**: Gate 1 (schema), Gate 2 (wire), Gate 3 (wire value constraints). On by default, `validate=False` to skip
- **CRUD lifecycle**: RowStatus create/delete with `linked_tables` for multi-table operations. 11/11 CRUD methods live-tested
- **43/43 setter tests** passing on live devices
- **Driver registry**: `transport_registry.py` — no hardcoded protocol imports in engine

---

## 2.7.0

### Directional pipeline

Unified pipeline replacing 5 separate code paths (~887 lines → single `_translate` dispatcher). Schema key order = pipeline order.

- **`_translate()`**: bidirectional pipeline executor. Egress runs top→bottom, ingress bottom→top
- **Step registry**: `steps.yaml` declares transition + formatter steps
- **Bidirectional steps**: `step_source_bind`, `step_value_map`, `step_key_map`, `step_index_codec`, `step_collect`, `step_regex`
- **Formatter steps**: `_apply_compute`, `_apply_lookup`, `_apply_membership`, `_apply_sub_tables`, `_apply_assemble`
- **Debug trace**: per-step recording in `_translate`, `{step, attr, direction, input, output}`

---

## 2.6.0

### Architecture — Three-File Model (first YAML-driven version)

### Architecture — Three-File Model

Complete rewrite from v1's handwritten Python to declarative YAML-driven engine. Wire YAMLs (generated from MIB) + Schema YAMLs (human-authored intent) + NAPALM adapter (thin shim). Zero business logic in Python — everything declared in YAML.

- **148 methods**: 11 Create, 64 Read, 49 Upsert, 13 Delete, 11 Execute
- **40 schema YAMLs** — all features declarative, no feature-specific Python
- **Engine**: 1479 lines, protocol-agnostic, dispatches to SNMP/MOPS/SSH drivers
- **Dynamic dispatch**: `__getattr__` auto-discovers methods from schema YAMLs
- **Execute methods**: declared in protocol YAML, enforced by adapter, exposed through NAPALM
- **MOPS staging**: `start_staging()`, `commit_staging()`, `discard_staging()`, `get_staged_mutations()` through adapter
- **NAPALM parity**: 32 base methods overridden, 8 inapplicable return `{}`
- **CRUDE_MATRIX**: 57 bidirectional transforms, syntax+type driven
- **Wire generation**: `batch_generate_webui.py` produces 134 wire YAMLs from MIB/MOPS proxy

### Schema primitives

`compute:`, `set_format:`, `membership_of:`, `lookup:`, `linked_tables:`, `key_map:`, `value_map:`, `fields:`, `index_key:`, `index_type:`, `regex_format:`, `collect:`, `sub_tables:`

### Execute methods

| Method | MOPS | SNMP | SSH |
|--------|------|------|-----|
| save_config | ✓ | ✓ | ✓ |
| load_config | ✓ | | |
| onboard | ✓ | | ✓ |
| clear_config | ✓ | ✓ | ✓ |
| clear_factory | ✓ | ✓ | ✓ |
| start_staging | ✓ | | |
| commit_staging | ✓ | | |
| discard_staging | ✓ | | |
| get_staged_mutations | ✓ | | |
| cli | | | ✓ |
| ping | | | ✓ |

---

## 2.5.0

### CRUDE engine

The declarative CRUDE engine — finite, bidirectional, MIB-driven. Every attribute is a self-contained contract with syntax, type, access, and sources.

- **CRUDE_MATRIX**: `crude_matrix.yaml` maps `(syntax, type)` → `crude_*` function. 9 bidirectional transform functions
- **crude.py**: replaces transforms.py. Functions are verbs (fixed set), YAML is the lookup (grows with new syntaxes)
- **Wire generation**: `batch_generate_webui.py` produces wire YAMLs from MIB/MOPS proxy
- **Three-file model**: wire (generated) + schema (authored) + adapter (per-consumer)

---

## 2.0.0

### Initial YAML conversion

First-generation YAML-driven rewrite of napalm-hios v1.16.2. Ported the handwritten Python driver into declarative YAML schema + wire files. v1.17.0 features were not ported until ~v2.8.

---

