# Schema Model — Canonical Contract

> The engine defines what the device looks like. Consumers decide what they want it to look like.

This document is the formal specification for schema YAMLs in crude-engine. Every schema MUST comply with the structural rules. Schemas SHOULD comply with the canonical shape rules — violations become the consumer reshaping hitlist.

---

## Principles

1. **Schemas describe the device, not the consumer.** Key names come from MIB concepts, not NAPALM conventions. The adapter reshapes for its consumer.
2. **`defaults` is the output contract.** Every key in `defaults` MUST appear in the getter output. Gate 1 exit enforces this.
   - A getter returns its `defaults` keys.
   - Every `defaults` key MUST exist as an attribute (feature-level or method-scoped).
   - Device-touching attributes MUST have `wire` + `source` so Gate 2 resolves — that is the matrix lookup and the formatting.
   - An undeclared `defaults` key never enters Gate 2; Gate 1 exit alone is a lie.
   - Empty `{}` is only for honest no-wire (e.g. SSH execute blobs like `get_config` running/startup).
   - Floor for this class: `python3 scripts/check_catalogue.py --composed`.
3. **`type` determines shape.** `dict` = flat or keyed dict. `list` / `list_append` = list of dicts. `upsert` / `create` / `delete` = write operations.
4. **`wire` + `source` bind to the device.** Every attribute that touches the device MUST declare its wire binding. Compute-only attributes MAY omit them.
5. **Method scope is explicit.** `defaults` keys define what a getter returns. `fields` restrict what a setter accepts. `sub_tables.field_map` declares nested structure.

---

## How It Fits Together

A schema describes one feature. It has methods (what you can do) and attributes (what the device exposes).

```
Schema (one per feature)
├── version, feature, description
├── methods:
│   ├── get_<feature>()        → Read: returns defaults contract
│   ├── set_<feature>()        → Update: writes to device
│   ├── create_<feature>()     → Create: RowStatus lifecycle
│   └── delete_<feature>()     → Delete: RowStatus lifecycle
└── attributes:
    ├── <name>: wire + source   → bound to device via wire YAML
    ├── <name>: compute         → derived from other attrs (no wire)
    └── <name>: lookup          → joined from another attr's index
```

### Read method output contract

`defaults` defines every key the getter returns. Gate 1 exit enforces this — if a key is in `defaults`, it MUST appear in the output. Every `defaults` key MUST also exist as an attribute; undeclared keys never enter Gate 2 (principle 2).

```yaml
get_dns:
  type: dict
  defaults:
    enabled: false
    domain_name: ''
    timeout: 3
    servers: {}           # sub_table placeholder
```

If the method has a `primary_key`, the output is a dict of rows keyed by that field:

```python
get_interfaces() -> {"1/1": {defaults...}, "1/2": {defaults...}}
```

If `key_map: ifindex`, raw numeric indices are remapped to port names via the context map.

### Sub-tables

When `defaults` contains a dict placeholder (e.g. `servers: {}`), a `sub_tables` block declares how to populate it:

```yaml
sub_tables:
  servers:                # matches the 'servers: {}' in defaults
    primary_key: address  # each row keyed by this field
    field_map:            # output field → schema attribute
      address: address
      addr_type: addr_type
```

Sub-tables reflect real MIB table hierarchies — parent scalars plus child rows.

### Write methods

Write methods (`upsert`) don't have `defaults` — they take kwargs and push to the device. `fields` optionally restricts which attrs are writable. `attributes` optionally provides method-scoped wire overrides.

### CRUD lifecycle

Create/delete methods manage RowStatus table rows:

```yaml
create_dns_server:
  type: create
  row_status: server_status    # RowStatus attr for createAndWait/Go
  index_key: server_index      # which field is the row index
  required: [address]          # must provide these
  defaults:                    # defaults for optional create fields
    addr_type: 1
```

`linked_tables` extends this to multi-table creates where multiple RowStatus attrs coordinate in transaction order.

### Attributes are wire bindings

Each attribute declares where its data comes from on the device:

```yaml
enabled:
  wire: hm2dnsclientadminstate     # name in wire YAML
  source: dns                       # which wire file
```

Optional transform keys modify how data flows through the pipeline: `value_map` translates enums, `compute` derives from other attrs (no wire needed), `lookup` joins across attrs, `collect` aggregates rows, `regex` extracts from raw values, `set_format` templates write values.

---

## Top-Level Keys

| Key | Req | Type | Description |
|-----|-----|------|-------------|
| `version` | MUST | string | Schema version (e.g. `2.9.0`) |
| `feature` | MUST | string | Feature identifier (e.g. `dns`, `interface`) |
| `description` | SHOULD | string | Human-readable purpose |
| `methods` | MUST | dict | Method definitions (see Method-Level Keys) |
| `attributes` | MUST | dict | Attribute catalog (see Attribute-Level Keys) |

No other top-level keys are valid.

---

## Method-Level Keys

### Read Methods (`type: dict`, `type: list`, `type: list_append`)

| Key | Req | Type | Description |
|-----|-----|------|-------------|
| `type` | MUST | enum | `dict` |
| `defaults` | MUST | dict | Output contract — every key appears in output with this default |
| `primary_key` | COND | string | Required for table getters (dict keyed by this field) |
| `key_map` | OPT | string | Context map name for key remapping (e.g. `ifindex`) |
| `index_fields` | OPT | list | RFC 2578 compound index decomposition fields |
| `index_type` | OPT | string | Last INDEX field encoding. `implied_string` = RFC 2578 IMPLIED (remaining sub-IDs as ASCII). Used with `index_fields`. |
| `sub_tables` | OPT | dict | Nested table definitions (see Sub-Table Keys) |
| `index_filter` | OPT | string | Regex filter on valid index values |

### Write Methods (`type: upsert`)

| Key | Req | Type | Description |
|-----|-----|------|-------------|
| `type` | MUST | enum | `upsert` |
| `fields` | OPT | list | Whitelist of allowed fields (empty = all attrs) |
| `index_filter` | OPT | string | Regex filter on valid index values |
| `attributes` | OPT | dict | Method-scoped attribute overrides |

### CRUD Methods (`type: create`, `type: delete`)

| Key | Req | Type | Description |
|-----|-----|------|-------------|
| `type` | MUST | enum | `create` or `delete` |
| `row_status` | MUST | string | RowStatus attribute name |
| `index_key` | MUST | string | Index field for row addressing |
| `required` | OPT | list | Fields required for create |
| `defaults` | OPT | dict | Default values for create (e.g. `addr_type: 1`) |
| `linked_tables` | OPT | list | Multi-table CRUD (see Linked Tables) |

### Sub-Table Keys (nested under `sub_tables`)

| Key | Req | Type | Description |
|-----|-----|------|-------------|
| `primary_key` | MUST | string | Key field for this sub-table |
| `field_map` | MUST | dict | Output field name → schema attribute name |
| `defaults` | SHOULD | dict | Per-row defaults |
| `key_map` | OPT | string | Context map for this sub-table |
| `child_key` | OPT | string | Wrapper key for nesting mode |

### Linked Tables (list items under `linked_tables`)

| Key | Req | Type | Description |
|-----|-----|------|-------------|
| `row_status` | MUST | string | RowStatus attribute for this table |
| `fields` | MUST | list | Fields managed by this table |

---

## Attribute-Level Keys

### Wire Binding

| Key | Req | Type | Description |
|-----|-----|------|-------------|
| `wire` | COND | string | Wire YAML attribute name. MUST for setter attrs. |
| `source` | COND | string | Wire feature file name. MUST for setter attrs. |

### Data Transformation (Egress)

| Key | Req | Type | Description |
|-----|-----|------|-------------|
| `value_map` | OPT | dict or string | Dict = inline enum map. String = context map reference. **Do not use for booleans** — see note below. |
| `compute` | OPT | dict | Derived from other attributes (keys: `from`, `expr`/`format`, `fallback`, `sort`) |
| `lookup` | OPT | dict | Cross-attribute join (keys: `from`, `index_field`, `resolve`) |
| `membership_of` | OPT | string | Test if row key exists in another attr's values |
| `collect` | OPT | enum | `value` (scalar) or `list` (aggregate as list) |
| `regex` | OPT | string | Regex with capture group to extract from wire value |
| `index_filter` | OPT | string | Filter this attr's index in source wiring |

### Data Transformation (Ingress)

| Key | Req | Type | Description |
|-----|-----|------|-------------|
| `set_format` | OPT | string | Format template for write values |

### Access (RowStatus columns)

| Key | Req | Type | Description |
|-----|-----|------|-------------|
| `access` | OPT | string | Attribute access mode. Live count: **15** attributes, all `access: crud` (RowStatus lifecycle columns). Values in use: `crud`. SCHEMA_PRIMITIVES also names `r` / `ru`. This is an attribute key, not a method `type:` — Execute (E) stays in protocol YAML `execute_methods`, not `type: execute`. |

No other attribute-level keys are valid.

### value_map vs CRUDE — don't double-transform

When the wire declares `type: boolean`, CRUDE automatically handles `True↔1, False↔2` via `crude_boolean`. Do NOT also add a `value_map: {'1': true, '2': false}` on the schema attr — the value_map runs first (pipeline phase), then CRUDE runs second (Gate 3 encode), and CRUDE will undo the value_map's work (because `'2'` is truthy in Python, `crude_boolean` converts it back to `1`).

**Rule:** `value_map` is for enum translations (string vocabularies like `up`/`down`/`testing`). Booleans (`HmEnabledStatus`, `TruthValue`) are handled by CRUDE automatically — no value_map needed.

```yaml
# WRONG — value_map fights with crude_boolean
signal:
  wire: hm2ledportsignaling
  source: diagnostic
  value_map:
    '1': true
    '2': false

# RIGHT — CRUDE handles boolean translation automatically
signal:
  wire: hm2ledportsignaling
  source: diagnostic
```

---

## Canonical Output Shape Rules

These rules define what "canonical" means. Violations are not errors — they are reshaping work for consumers.

### Rule 1: Keys reflect the device, not the consumer

**Violation:** `is_up`, `is_enabled` (NAPALM convention)
**Canonical:** `oper_status`, `admin_status` (MIB concept)

**Violation:** `remote_hostname`, `remote_port` (NAPALM LLDP keys)
**Canonical:** `sys_name`, `port_id`, `chassis_id` (LLDP MIB fields)

### Rule 2: No consumer-specific nesting

**Violation:** `physical_channels: {channel: [{index: 0, state: {input_power: ...}}]}`
**Canonical:** flat `tx_power`, `rx_power`, `bias_current` per port

### Rule 3: No consumer-specific value derivation in defaults

**Violation:** `active: true`, `static: false` (derived from FDB status for NAPALM)
**Canonical:** `status: "forward"` or `status: "permanent"` (MIB value)

### Rule 4: Sub-tables for natural hierarchy only

**Violation:** sub_table created to match consumer's expected nesting
**Canonical:** sub_table reflects actual MIB table relationship (parent scalar + child rows)

### Rule 5: Method names follow feature, not consumer

**Acceptable:** `get_interfaces` — this IS the canonical name for interface data
**Acceptable:** `get_arp_table` — ARP table is what it is
**Flag:** Method name matches NAPALM AND keys are NAPALM-shaped = consumer contortion

---

## Known NAPALM-Shaped Schemas (Reshaping Hitlist)

Live `defaults` (`origin/main` `139fe69`, 45 schemas): four of these five rows are already canonical. Only `vlan` `get_vlans` is still a consumer/shim leftover. Extra scan found no further hitlist rows. Canonical shape stays engine formatters; consumer reshape stays adapter/shim.

| Schema | Live defaults keys | Status | Consumer |
|--------|--------------------|--------|----------|
| `interface` (`get_interfaces`) | `oper_status`, `admin_status` (was `is_up`/`is_enabled`). `phys_address`, `alias` present; `last_flapped`, `mac_address`, `description` gone. | Already canonical. Leftover naming: `speed` vs canonical `highspeed` (wire `ifhighspeed`). `mtu` is live and canonical — not a NAPALM violation. | napalm-hios maps back if needed |
| `lldp` (`get_lldp_neighbors`, `get_lldp_neighbors_detail`) | `sys_name`, `port_id`, `chassis_id`, `sys_description` (was `remote_*`) | Already canonical | napalm-hios maps back if needed |
| `mac` (`get_mac_address_table`) | `status` MIB enum `other`/`invalid`/`learned`/`self`/`mgmt` (was `active`/`static`/`moves`/`last_move`) | Already canonical | napalm-hios derives booleans if needed |
| `optics` (`get_optics`) | flat `tx_power`, `rx_power`, `temperature` (was nested `physical_channels`) | Already canonical | napalm-hios nests for NAPALM if needed |
| `vlan` (`get_vlans`) | `ports` dict with U/T/F | Honest leftover. Canonical already exists as `get_vlan_egress`. | Consumer/shim still merges if needed |

### Acceptable (MIB-standard keys, NAPALM method name coincidence)

These schemas have NAPALM method names but canonical keys — no reshaping needed:

- `arp` (get_arp_table) — keys are MIB-standard
- `ipv6` (get_ipv6_neighbors_table) — keys from ipNetToPhysicalEntry
- `ntp` (get_ntp_servers, get_ntp_stats) — keys are canonical
- `route` (get_route_to) — keys from inetCidrRoute
- `snmp_information` (get_snmp_information) — keys from SNMPv2-MIB
- `system` (get_facts, get_environment) — keys are MIB-standard
- `user` (get_users) — keys follow usermgmt MIB
- `config` (get_config) — keys are canonical
