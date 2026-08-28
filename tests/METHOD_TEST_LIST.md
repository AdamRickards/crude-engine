# Method Test List — v2.8.0

> Every schema method, where to test it, what to verify.
> Devices: .4 (BRS50 L2A), .254 (GRS1042 L3A), .80-.85 (lab BRS50s)
> Source: `get_capabilities()` on .80 — 166 methods (18C 76R 52U 19D 1E)

## Getters (76) — ALL PASS

> 76/76 OK on .80 (L2A) — `audit_getters.py` v2.8.0, 2026-03-30
> Baselines: `tests/audit_v28_4.json`, `audit_v28_80.json`, `audit_v28_254.json`

| Method | Feature | Device | Notes |
|--------|---------|--------|-------|
| get_aca | aca | .85 | NEW v2.8 — JUSTIN audit tested |
| get_arp_inspection | arp | .254 | L3 only |
| get_arp_table | arp | .254 | L3: full ARP, L2: empty |
| get_auto_disable | protection | .4 | L2A+ (not L2S) |
| get_banner | banner | .4 | |
| get_config | config | .4 | broken — TODO |
| get_config_fingerprint | config | .4 | |
| get_config_remote | config | .4 | |
| get_config_status | config | .4 | |
| get_dai_global | dai_global | .4 | |
| get_device_monitor | system_health | .4 | |
| get_devsec | devsec | .85 | NEW v2.8 — JUSTIN audit tested, 19 monitors |
| get_devsec_history | devsec | .85 | NEW v2.8 — status event table |
| get_devsec_status | system_health | .4 | legacy — global state only |
| get_dhcp_snooping | dhcp_snooping | .4 | |
| get_dns | dns | .4 | |
| get_environment | system | .4 | temp sensors |
| get_facts | system | .4 | NAPALM standard |
| get_fan_status | system_health | .254 | GRS has fans |
| get_gmrp | gmrp | .4 | |
| get_gvrp | gvrp | .4 | |
| get_hidiscovery | hidiscovery | .4 | |
| get_interfaces | interface | .4 | NAPALM standard |
| get_interfaces_counters | interface | .4 | NAPALM standard |
| get_interfaces_ip | interface | .254 | L3 IP addresses |
| get_ip_addresses | interface | .254 | L3 |
| get_ip_restrict | ip_restrict | .4 | reworked: globals + sub_tables: rules (indexed 1-16) |
| get_ip_source_guard_port | ip_source_guard | .4 | reworked: per-port enabled/port_security dict (was get_ip_source_guard) |
| get_ip_source_guard_bindings | ip_source_guard | .80 | NEW — static binding table as list, CRUD verified |
| get_ipv6_neighbors | ipv6 | .254 | L3 |
| get_ipv6_neighbors_table | ipv6 | .254 | NAPALM standard |
| get_lldp_neighbors | lldp | .4 | NAPALM standard |
| get_lldp_neighbors_detail | lldp | .4 | NAPALM standard |
| get_lldp_neighbors_detail_extended | lldp | .4 | vendor extended |
| get_login_policy | user | .4 | |
| get_loop_protection | protection | .4 | L2A+ |
| get_mac_address_table | mac | .4 | NAPALM standard |
| get_management | management | .4 | |
| get_management_priority | management | .4 | |
| get_mrp | mrp | .80 | ring must exist |
| get_mrp_sub_ring | mrp_sub_ring | .80 | SRM must exist |
| get_ntp | ntp | .4 | |
| get_ntp_servers | ntp | .4 | |
| get_ntp_stats | ntp | .4 | NAPALM standard |
| get_optics | optics | .254 | SFP ports |
| get_software | software | .85 | NEW v2.8 — JUSTIN audit tested |
| get_poe | poe | .4 | if PoE model |
| get_port_security | port_security | .4 | reworked: globals + sub_tables: ports (key_map ifindex), cross-MIB auto_disable_enabled via index_filter |
| get_port_security_global | port_security | .4 | merged into get_port_security (globals + sub_tables) |
| get_profiles | profile | .4 | |
| get_qos | qos | .4 | |
| get_qos_mapping | qos_mapping | .4 | |
| get_remote_auth | remote_auth | .4 | |
| get_route_to | route | .254 | L3 routing table |
| get_rstp | rstp | .4 | |
| get_rstp_port | rstp | .4 | |
| get_services | services | .4 | |
| get_session_config | session_config | .4 | |
| get_sflow | sflow | .4 | |
| get_sflow_port | sflow | .4 | |
| get_signal_contact | signal_contact | .4 | |
| get_snmp_config | snmp | .4 | |
| get_snmp_information | snmp_information | .4 | NAPALM standard |
| get_snmp_trap_destinations | snmp | .4 | |
| get_storm_control | protection | .4 | |
| get_syslog | syslog | .4 | |
| get_system_health | system | .4 | |
| get_system_info | system | .4 | |
| get_users | user | .4 | NAPALM standard |
| get_vlan_egress | vlan | .4 | PortList decode |
| get_vlan_ingress | vlan | .4 | fixed: was keyed by VLAN name, now keyed by port (bridge_port). VIKTOR tested |
| get_vlans | vlan | .4 | NAPALM standard |
| get_vrrp | vrrp | .254 | L3, needs VRRP config |
| get_vrrp_instances | vrrp | .254 | compound index |
| get_vrrp_stats | vrrp | .254 | |
| get_vrrp_tracking | vrrp | .254 | 3-part compound index |
| get_watchdog_status | config | .4 | |

## Setters/Upsert (56)

| Method | Feature | Device | Notes |
|--------|---------|--------|-------|
| set_access_port | vlan | .85 | sacrificial L2S |
| set_arp_inspection | arp | .254 | L3 only |
| set_auto_disable | protection | .80 | per-port, L2A+ — CLAMPS tested |
| set_auto_disable_reason | protection | .80 | method-scoped enabled — CLAMPS tested |
| set_banner | banner | .85 | |
| set_config_remote | config | .85 | MOHAWC wired |
| set_dai_global | dai_global | .85 | |
| set_device_monitor | system_health | .85 | |
| set_devsec_status | system_health | .85 | |
| set_dhcp_snooping | dhcp_snooping | .85 | |
| set_dns | dns | .85 | |
| set_gmrp | gmrp | .85 | JUSTIN wired |
| set_gmrp_port | gmrp | .85 | needs bridge_port reverse |
| set_gvrp | gvrp | .85 | JUSTIN wired |
| set_gvrp_port | gvrp | .85 | needs bridge_port reverse |
| set_hidiscovery | hidiscovery | .85 | JUSTIN wired + MOHAWC tested (on/off/ro/blink) |
| set_interface | interface | .80 | key_map: ifindex — CLAMPS tested |
| set_ip_restrict | ip_restrict | .85 | |
| set_ip_source_guard_port | ip_source_guard | .85 | reworked (was set_ip_source_guard) — CRUD setup tested |
| set_ip_source_guard_binding | ip_source_guard | .85 | NEW — upsert on existing binding row |
| set_lldp | lldp | .85 | |
| set_login_policy | user | .85 | JUSTIN wired |
| set_loop_protection | protection | .80 | L2A+ — CLAMPS tested |
| set_management | management | .85 | MOHAWC wired |
| set_management_priority | management | .85 | |
| set_mrp | mrp | .80 | ring must exist |
| set_mrp_sub_ring | mrp_sub_ring | .80 | method-scoped enabled (global SRM) — CLAMPS tested |
| set_ntp | ntp | .85 | JUSTIN wired |
| set_poe | poe | .4 | if PoE model |
| set_port_security | port_security | .85 | |
| set_qos | qos | .85 | VIKTOR tested — PCP set on .85 |
| set_qos_mapping | qos_mapping | .85 | |
| set_remote_auth | remote_auth | .85 | |
| set_rstp | rstp | .80 | global admin — CLAMPS tested |
| set_rstp_port | rstp | .80 | method-scoped enabled (per-port) — CLAMPS tested |
| set_services | services | .85 | sub_tables intent mapping — JUSTIN wired |
| set_session_config | session_config | .85 | |
| set_sflow | sflow | .85 | |
| set_sflow_port | sflow | .85 | |
| set_signal_contact | signal_contact | .85 | |
| set_snmp_config | snmp | .85 | JUSTIN wired |
| set_snmp_information | snmp_information | .85 | MOHAWC wired |
| set_storm_control | protection | .80 | per-port — CLAMPS tested |
| set_syslog | syslog | .85 | JUSTIN wired |
| set_system_info | system | .85 | |
| set_user | user | .85 | |
| set_vlan_egress | vlan | .85 | PortList encode — VIKTOR tested (.85 L2S + .83 L3A), T/U/none modes |
| set_vlan_ingress | vlan | .85 | VIKTOR tested (.85 L2S + .83 L3A), PVID set |
| set_vrrp | vrrp | .83 | L3 lab |
| set_vrrp_instance | vrrp | .83 | compound index SET |
| set_vrrp_tracking | vrrp | .83 | 3-part compound SET |
| set_watchdog | config | .85 | JUSTIN wired |
| set_aca | aca | .85 | JUSTIN wired — per-slot via index |
| set_devsec | devsec | .85 | JUSTIN wired — per-monitor enable/disable |
| set_software | software | .85 | JUSTIN wired — allow_unsigned, secure_boot |
| set_vlan | vlan | .85 | VIKTOR tested (.85 L2S + .83 L3A), rename |
| create_port_security | port_security | .85 | upsert-typed (action value, not RowStatus) — CRUD tested |
| delete_port_security | port_security | .85 | upsert-typed (action value) — CRUD tested |
| delete_profile | profile | .85 | upsert-typed (action value) — MOHAWC wired |

## Execute (10)

| Method | Feature | Device | Notes |
|--------|---------|--------|-------|
| save_config | transport | .85 | NVM save — CLAMPS tested (when save=true) |
| load_config | transport | .85 | config XML upload |
| onboard | transport | .85 | factory password change |
| clear_config | transport | .85 | reset running config |
| clear_factory | transport | .85 | factory reset — destructive |
| start_staging | transport | .85 | MOPS staging mode |
| commit_staging | transport | .85 | MOPS atomic commit |
| discard_staging | transport | .85 | MOPS discard staged |
| get_staged_mutations | transport | .85 | inspect staging buffer |
| is_factory_default | transport | .85 | check if factory state |

## Create (15 RowStatus)

| Method | Feature | Device | Notes |
|--------|---------|--------|-------|
| create_dns_server | dns | .85 | |
| create_ip_restrict_rule | ip_restrict | .85 | CRUD tested — user-provided index (1-16), service boolean defaults |
| create_ldap_server | remote_auth | .85 | |
| create_mrp | mrp | .80 | RowStatus + auto-index — CLAMPS tested |
| create_mrp_sub_ring | mrp_sub_ring | .80 | RowStatus — CLAMPS tested |
| create_ntp_server | ntp | .85 | |
| create_port_security | port_security | .85 | CRUD tested — set_format assembly (vlan+mac), requires feature enabled |
| create_radius_server | remote_auth | .85 | |
| create_snmp_trap_dest | snmp | .85 | CRUD tested — linked_tables (params+addr), createAndWait, implied_string hex index |
| create_static_binding | ip_source_guard | .80 | CRUD tested — 4-part composite index (ifIndex+VLAN+MAC+IP), createAndWait, setup: DHCP snooping + IPSG enabled |
| create_syslog_server | syslog | .85 | |
| create_tacacs_server | remote_auth | .85 | |
| create_user | user | .85 | |
| create_vlan | vlan | .85 | VIKTOR tested (.85 L2S + .83 L3A), RowStatus + user index |
| create_vrrp | vrrp | .83 | compound index CREATE |
| create_vrrp_tracking | vrrp | .83 | 3-part compound CREATE |

## Delete (19)

| Method | Feature | Device | Notes |
|--------|---------|--------|-------|
| delete_dns_server | dns | .85 | |
| delete_ip_restrict_rule | ip_restrict | .85 | CRUD tested |
| delete_ldap_server | remote_auth | .85 | |
| delete_mrp | mrp | .80 | CLAMPS tested |
| delete_mrp_sub_ring | mrp_sub_ring | .80 | CLAMPS tested |
| delete_ntp_server | ntp | .85 | |
| delete_port_security | port_security | .85 | CRUD tested — set_format assembly (vlan+mac) |
| delete_profile | profile | .85 | |
| delete_radius_server | remote_auth | .85 | |
| delete_snmp_trap_dest | snmp | .85 | CRUD tested — linked_tables (addr first, then params), index_key: name |
| delete_static_binding | ip_source_guard | .80 | CRUD tested — compound index delete, all 4 fields required in kwargs |
| delete_syslog_server | syslog | .85 | |
| delete_tacacs_server | remote_auth | .85 | |
| delete_user | user | .85 | |
| delete_vlan | vlan | .85 | VIKTOR tested (.85 L2S + .83 L3A) |
| delete_vrrp | vrrp | .83 | |
| delete_vrrp_tracking | vrrp | .83 | |

## Activate (1)

| Method | Feature | Device | Notes |
|--------|---------|--------|-------|
| activate_profile | profile | .85 | MOHAWC wired |

## Test Device Assignment

| Device | Role | Methods |
|--------|------|---------|
| .4 (BRS50 L2A) | Read-only getters | 55 getters (safe, production-like) |
| .83 (GRS L3A lab) | L3 features + VRRP | VRRP CRUD, compound index, failover with .254 |
| .254 (GRS1042 L3A) | L3 prod | L3 getters, VRRP failover partner for .83 |
| .80 (BRS50 L2A lab) | Ring + protection setters | MRP, RSTP, storm control, auto-disable |
| .85 (BRS50 L2S lab) | Sacrificial setter target | All non-ring setters, CRUD create/delete cycles |

## Engine Primitives Covered

| Primitive | Methods That Exercise It |
|-----------|------------------------|
| method-scoped attributes | set_rstp_port, set_auto_disable_reason, set_mrp_sub_ring |
| key_map: ifindex | get_rstp_port, set_interface, get_storm_control, get_auto_disable |
| value_map (inline dict) | get_mrp (role, ring_state), get_rstp_port (enabled) |
| value_map (context map) | get_lldp (ifindex), set_rstp_port (ifindex reverse) |
| index_filter (method) | set_rstp_port, set_auto_disable |
| index_filter (attr) | get_port_security (auto_disable_enabled from devmgmt reason table) |
| set_format / assemble | create_port_security, delete_port_security (mac_add/mac_remove from vlan+mac) |
| compound index (CRUD) | create_tacacs_server, delete_tacacs_server (inet_address: addr_type + address) |
| sub_tables | get_services, set_services, get_ip_restrict (rules), get_port_security (ports) |
| compute | get_system_health, get_profiles |
| lookup | get_lldp_neighbors_detail_extended |
| membership_of | get_interfaces (is_enabled cross-check) |
| regex | get_environment, get_system_info |
| bit_map | get_lldp (capabilities), get_vlan_egress (PortList) |
| compound index_fields | get_vrrp_instances, get_vrrp_tracking |
| composite index CRUD | create_static_binding, delete_static_binding (4-part: ifIndex+VLAN+MAC+IP, `index_type: composite`) |
| crude_address encoding | create_static_binding (IpAddress dotted pass-through vs InetAddress hex) |
| linked_tables (N-table CRUD) | create_snmp_trap_dest, delete_snmp_trap_dest (2 tables: params+addr, each with own RowStatus, createAndWait, implied_string index) |
| RowStatus auto-index | create_dns_server, create_syslog_server |
| assemble | set_services (sub_table reassembly) |
| sub_table compute | get_software (version from major/minor/bugfix per image row) |
| key_map: bridge_port | get_vlan_ingress (per-port PVID/ingress filtering) |

## Tool Coverage Summary

> All 6 tools confirmed on v2.8.0 (2026-03-29)

| Tool | Status | Methods | Key Tests |
|------|--------|---------|-----------|
| CLAMPS | tested | 22 | clamp+unclamp+sub-ring, idempotent, cable-out |
| VIKTOR | tested | 12 | VLAN CRUD, access/trunk, QoS PCP, export/import CSV |
| JUSTIN | tested | 19 | 16/16 checks, 0 not assessed, ACA/devsec/software schemas |
| STONE | tested | 2 | get_optics on SFP devices |
| AARON | tested | 3 | MAC/LLDP classification on .85 |
| MOHAWC | tested | 19 | status, profiles, system, management, hidiscovery on/off/ro/blink |

**Tested live**: 118/166 methods (71%)
**Untested**: 48 methods — simple setters on .85, VRRP compound CRUD on .83

## CRUD Round-Trip Tests (`tests/test_crud_pairs.py`)

> Pattern: get (guard) → create → get (verify) → set (upsert on index) → get (verify) → delete (by index) → get (verify gone)
> Script handles stale cleanup from previous runs via initial GET guard.

```bash
python3 tests/test_crud_pairs.py 192.168.60.80                     # all tests
python3 tests/test_crud_pairs.py 192.168.60.80 --only dns ntp      # specific tests
python3 tests/test_crud_pairs.py 192.168.60.80 --cleanup           # remove stale test entries
python3 tests/test_crud_pairs.py 192.168.60.80 --protocol snmp     # force SNMP
```

### Results (2026-03-30, .80 L2A, MOPS verified — 11/11 passing)

| Test | Status | Lifecycle | Notes |
|------|--------|-----------|-------|
| dns | PASS | createAndGo | full round trip with indexed SET |
| ntp | PASS | createAndWait | full round trip with indexed SET (notInService→set→active) |
| syslog | PASS | createAndGo | create + delete |
| radius | PASS | createAndWait | create + delete |
| ldap | PASS | createAndWait | create + delete |
| user | PASS | createAndGo | create + delete |
| ip_restrict | PASS | createAndGo | user-provided index (1-16), service booleans in create defaults |
| port_security | PASS | action-value | set_format assembly (vlan+mac), setup/teardown enables feature first |
| tacacs | PASS | createAndGo | compound index (addr_type + address), CRUDE-encoded via _resolve_compound_index helper |
| snmp_trap | PASS | linked_tables | multi-table CRUD (addr + params), createAndWait, implied_string hex index, `set_format` auto-derives params_ref from name |
| static_binding | PASS | createAndWait | 4-part composite index (ifIndex+VLAN+MAC+IP), `index_type: composite`, `crude_address` dotted encoding, setup: DHCP snooping + IPSG. Binding table visible via `get_ip_source_guard_bindings` |

### Schema rework completed for CRUD

All passing CRUD schemas follow the standard pattern: globals + indexed sub_table.

| Schema | Changes |
|--------|---------|
| dns.yaml | `servers: []` → indexed sub_table, added `server_index`, `index_key` on create/delete |
| ntp.yaml | `servers: []` → indexed sub_table, added `index_key` on create/delete |
| syslog.yaml | `servers: []` → indexed sub_table, added `server_index`, `index_key` on create/delete |
| remote_auth.yaml | 3 flat lists → 3 indexed sub_tables (radius/ldap/tacacs), added index attrs |
| ip_restrict.yaml | flat `primary_key` dict → globals + `sub_tables: rules:`, added `index_key` + service boolean defaults on create/delete |
| port_security.yaml | merged `get_port_security_global` into `get_port_security`, globals + `sub_tables: ports:` with `key_map: ifindex`, cross-MIB `auto_disable_enabled` via `index_filter` |
| remote_auth.yaml | `delete_tacacs_server` added `defaults: {tacacs_addr_type: 1}` for compound index |
| snmp.yaml | `delete_snmp_trap_dest` added `index_key: name`. `params_ref` added `set_format: "{name}"` to auto-derive addr→params link. Create: params first, then addr. Delete: addr first, then params (reversed, matching v1 and RFC 3413 dependency order) |
| ip_source_guard.yaml | Split: `get_ip_source_guard` → `get_ip_source_guard_port` (per-port config) + `get_ip_source_guard_bindings` (static binding list). Added `set_ip_source_guard_binding` upsert. `binding_active` value_map for RowStatus→boolean |

### Wire fixes for CRUD

| Fix | Files |
|-----|-------|
| `InetAddressType: type: string → integer` | dns.yaml, timesync.yaml, platform-radius.yaml, mgmtaccess.yaml, logging.yaml, remote-authentication.yaml, platform-tacacsclient.yaml |
| `dot1qPortVlanEntry: added index_field: dot1dBasePort` | q-bridge.yaml (3 attrs: dot1qPvid, AcceptableFrameTypes, IngressFiltering) |

### Engine/Driver fixes for CRUD

| Fix | Location |
|-----|----------|
| RowStatus lifecycle in `set_values` | MOPS.py + SNMP.py — driver reads `create_method` from wire, wraps SET in notInService→set→active for createAndWait tables |
| pysnmp 5.x/7.x compat | snmp_transport.py — fallback imports for both API naming conventions |
| CRUD index from intent resolution | interpreter.py — user-provided index was consumed by `_resolve_intent_v28`, now passed back to `_pipeline_crud` |
| `_wire_def` passed to driver | interpreter.py → source dict — driver needs wire definition to find RowStatus attrs |
| `index_filter` attr primitive | interpreter.py + SNMP.py + MOPS.py — targeted cell read via value_map reversal, SNMP scalar GET, MOPS dict filter |
| `_apply_assemble` before Gate 1 | interpreter.py — set_format template fields consumed before validation, method `fields:` respected |
| `_resolve_compound_index` helper | interpreter.py — shared by create and delete, builds compound dict from wire `index_fields` |
| Compound index syntax registration | interpreter.py — `_dispatch_crud_create/delete` registers all compound field syntaxes for driver |
| SNMP `_resolve_oid_suffix` helper | SNMP.py — shared by `create_row` and `delete_row`, handles scalar and compound |
| MOPS `_resolve_row_index` compound | MOPS.py — encodes compound dict fields same as scalar path |
| `_resolve_rs_context` helper | interpreter.py — shared row_status→wire context resolution for all 4 CRUD dispatch sites (create/delete × top-level/linked) |
| Linked tables per-table context | interpreter.py — create+delete linked loops resolve per-table wire/proto/driver/create_method instead of reusing top-level |
| Linked tables index syntax registration | interpreter.py — both create+delete linked loops register index field syntax so driver can CRUDE-encode implied_string indexes |
| `create_method_default` in protocol YAML | SNMP.yaml, MOPS.yaml, SSH.yaml — RowStatus lifecycle default declared in YAML, not hardcoded in Python |
| `index_type: composite` wire declaration | platform-switching.yaml — gates `_resolve_compound_index` for multi-typed compound indexes (not inet_address or implied_string) |
| `crude_address` encoding arg | crude.py + crude_matrix.yaml — `IpAddress` uses `{encoding: dotted}` (pass-through on ingress), `InetAddress` uses default hex encoding. MOPS expects dotted-quad for SMIv1 IpAddress |

### CRUD complete — all 11/11 passing

All RowStatus CRUD features fully tested on .80 via MOPS.
