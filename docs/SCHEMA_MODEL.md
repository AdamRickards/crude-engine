# Schema Model — Canonical Contract

> The engine defines what the device looks like. Consumers decide what they want it to look like.

This document is the formal specification for schema YAMLs in crude-engine. Every schema MUST comply with the structural rules. Schemas SHOULD comply with the canonical shape rules — violations become the consumer reshaping hitlist.

---

## Principles

1. **Schemas describe the device, not the consumer.** Key names come from MIB concepts, not NAPALM conventions. The adapter reshapes for its consumer.
2. **`defaults` is the output contract.** Every key in `defaults` MUST appear in the getter output. Gate 1 exit enforces this.
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

`defaults` defines every key the getter returns. Gate 1 exit enforces this — if a key is in `defaults`, it MUST appear in the output.

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
| `type` | MUST | enum | `dict`, `list`, or `list_append` |
| `defaults` | MUST | dict | Output contract — every key appears in output with this default |
| `primary_key` | COND | string | Required for table getters (dict keyed by this field) |
| `key_map` | OPT | string | Context map name for key remapping (e.g. `ifindex`) |
| `index_fields` | OPT | list | RFC 2578 compound index decomposition fields |
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
| `value_map` | OPT | dict or string | Dict = inline enum map. String = context map reference. |
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

No other attribute-level keys are valid.

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

| Schema | Keys | Canonical Alternative | Consumer Reshaper |
|--------|------|----------------------|-------------------|
| `interface` | `is_up`, `is_enabled`, `last_flapped`, `speed`, `mtu`, `mac_address`, `description` | `oper_status`, `admin_status`, `last_change`, `highspeed`, `mtu`, `phys_address`, `alias` | napalm-hios maps back |
| `lldp` | `remote_hostname`, `remote_port`, `remote_chassis_id`, `remote_system_description` | `sys_name`, `port_id`, `chassis_id`, `sys_description` | napalm-hios maps back |
| `mac` | `active`, `static`, `moves`, `last_move` | `status` (forward/permanent/etc) | napalm-hios derives booleans |
| `optics` | Nested `physical_channels` structure | Flat `tx_power_dbm`, `rx_power_dbm` per port | napalm-hios nests for NAPALM |
| `vlan` (get_vlans) | `ports` dict with U/T/F values | Separate `egress_ports`, `untagged_ports`, `forbidden_ports` lists | napalm-hios merges to ports dict |

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
