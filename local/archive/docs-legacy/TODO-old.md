# TODO

## Current state (2026-04-04, v2.9.0)

- **45 schema YAMLs**, 77 read methods, 183 total CRUDE methods (16C 77R 64U 16D 10E)
- **Canonical output**: interface (17 attrs), lldp, mac, optics, arp_inspection (global+ports+vlans)
- **Package split**: `crude_engine` + `napalm_hios`
- **MOPS batching**: single gather call, context maps in batch
- **Gate check**: `audit_getters_v2.py` — 77/77 MOPS+SNMP on 4 devices, zero parity failures
- **Documentation**: 4 generators + SCHEMA_MODEL.md + validator

## SSH wire source parity

**47/63 getters have no SSH sources.** 61/7927 wire attrs have SSH, 53/174 methods covered (30%).

CLI reference: `local/reference/CLI/cli_ref_hios_merged.json` (1,849 commands)
Wire overlay dir: `crude_engine/wire/ssh/` (13 overlay files currently)

- [x] Partial overlays completed — all 12 partial schemas updated
- [x] New overlays: snmpv2, devmgmt, if, ip, netconfig, trafficmgmt, platform-switching, platform-qos-cos, l2forwarding, sflow, diagnostic — system/interface/mac/arp/management/storm-control/banner/qos/config/sflow/ip-source-guard
- [x] SSH gate check: 50/77 pass, 0 fail, 27 skip on .4 BRS50
- [ ] VLAN PortList SSH parser — `show vlan member current` T/U/F/- format. Needs custom parser
- [ ] LLDP SSH parser — `show lldp remote-data` block format. Needs custom parser
- [ ] SSH uptime — `show system info` returns human string, needs to_timeticks CRUDE transform
- [ ] Remaining 26 methods need per-item investigation:
  - `signal_contact` — `show signal-contact {n} mode/state` works, needs multi-command wiring
  - `rstp` — `show spanning-tree global` works for globals, port command syntax TBD
  - `system_health` — `show device-status all` complex multi-section format
  - `software` — partially in filemgmt, `show system info` has more
  - `route`, `router` — L3 only, need .83 or .254
  - `devsec`, `devsec_history` — need to find CLI commands
  - `dhcp_snooping`, `dai_global` — no CLI found on .4
  - `mrp`, `mrp_sub_ring` — SSH wire added, `show mrp` works on .80 but SSH driver returns flat dot_keys for table methods (driver gap). SNMP walk data exists (66 entries) but driver can't decompose 16-byte compound OID suffix for domain ID (compound index decomposition gap). MOPS works correctly. Both driver gaps, wires correct
  - `gmrp`, `gvrp` — no CLI found
  - `poe` — no CLI found (hardware dependent)
  - `vrrp` ×4 — no CLI found on .4 (L3 only)
  - `hidiscovery` — need to find command
  - `session_config` — no CLI found
- [ ] Verify SSH overlays with populated data on devices that have real entries
- [x] Accepted SSH gaps in `tests/wire_exemptions.yaml`: addr_type, VACM, secrets, stratum, storage_type, uptime, membership_of

## Generator improvements

These prevent manual wire fixes from being lost on regeneration:

- [ ] `index_field` from MIB TABLE INDEX declarations (IF-MIB 19 attrs, P-BRIDGE-MIB 15 attrs, Q-BRIDGE-MIB 4 attrs manually fixed)
- [ ] `InetAddressType` TC → `type: integer` (affects DNS, NTP, syslog, RADIUS, LDAP, TACACS addr_type fields)
- [ ] `VlanId` TC → `type: integer` (manually fixed in platform-routing.yaml)
- [ ] `index_type: composite` detection for multi-field INDEX with mixed types (manually fixed: ip_source_guard 4-part)
- [ ] TextualConvention → base syntax for BITS types (LldpLinkAggStatusMap, LldpSystemCapabilitiesMap manually fixed)
- [ ] `INTEGER{enabled(1),disabled(2)}` → `type: boolean` (ifLinkUpDownTrapEnable manually fixed in if.yaml)
- [ ] `SFlowReceiver` TC wraps Integer32 → `type: integer` (manually fixed in sflow.yaml)
- [ ] `hm2Ntp*` vs `hm2Sntp*` prefix mismatch — generator used NTP OIDs/tables but device responds to SNTP variants. Affects hm2NtpServerAdminState (manually fixed: OID + MOPS table/field to hm2Sntp* in timesync.yaml). Generator needs to check which prefix the device actually uses

## Open items

- [x] Hardcoded `createAndWait` in drivers — fixed: mops_driver.py, snmp_driver.py now read `create_method_default` from protocol YAML
- [ ] `get_login_policy` / `set_login_policy` — 4 missing wire attrs in usermgmt wire (password complexity fields)
- [ ] MRP/SRM `enabled`/`redundancy` raw integers — need HmEnabledStatus value_maps
- [ ] Bidirectional `compute:` via `set_format:` — allow computed attrs to be SET by reversing the compute

## VRRP & Compound Index Decomposition

- [x] `get_vrrp_instances` — works on MOPS+SNMP, compound keys correct (SNMP decomposes, MOPS returns rows)
- [x] `get_vrrp_tracking` — works on MOPS+SNMP, 3-part compound key
- [x] Cross-protocol parity (SNMP vs MOPS) — verified via gate check
- [ ] MOPS compound index decomposition — MOPS keys show `1/2:` (missing vrid), SNMP shows `vlan/1:2` (correct). MOPS driver doesn't decompose row data into compound key fields
- [ ] `set_vrrp_instance` / `create_vrrp` / `delete_vrrp` — compound index CRUD (untested)
- [ ] Tracking objects schema (`hm2TrackingConfigEntry`)

## Schema Rework — API Design Review (pre-gNMI, not blocking v2.9)

> Separate from canonical compliance (done). This is about whether the API *shape* makes sense
> for users — global vs per-instance, feature separation, method-scoped attrs.

- [x] mrp_sub_ring — global `enabled` from `hm2srmglobaladminstate` + instances sub_table
- [ ] auto_disable — split: timer (per-port), reason (per-reason), status (read), reset (action)
- [x] protection — 3 features sharing one schema file is fine (separate getters/setters each)
- [x] interface — `set_interface` scoped to `[admin_status, alias, mtu]`
- [ ] All remaining schemas — quick pass for sensible GET shape + SET args

## Test infrastructure

- [x] `tests/audit_getters.py` — 78/78 on .4 (MOPS, SNMP, SSH)
- [x] `tests/test_crud_pairs.py` — 11/11 CRUD round-trips on .80 (MOPS)
- [x] `tests/METHOD_TEST_LIST.md` — full tracking
- [x] `docs/DIAGNOSTIC_PROCESS.md` — 7-step fault-finding ladder
- [ ] `test_setter_pairs.py` — SET round-trips for ~30 untested setters
- [ ] VRRP compound index CRUD on .83
- [ ] Parity suite v1 vs v2 output comparison
- [ ] Fixture capture on GRS1042 (.254) and BRS50 L2S (.85)

## Documentation — DONE

- [x] `docs/API_REFERENCE.md` — auto-generated by `generate_docs.py`
- [x] `docs/METHOD_REFERENCE.md` — auto-generated by `generate_method_ref.py`
- [x] `docs/PROTOCOLS.md` — auto-generated by `generate_protocols.py`
- [x] `docs/SCHEMA_MODEL.md` — formal canonical schema contract
- [x] `local/generator/README.md` — generator index

## Done

- [x] v2.6 three-file model (wire + schema + adapter)
- [x] v2.7 directional pipeline
- [x] v2.8 interpreter decomposition, 3 pipeline runners, CRUD lifecycle
- [x] v2.9 three-gate model (SchemaContext, WireContext, dispatch_batch/gather_and_decode)
- [x] Package split (crude-engine + napalm-hios)
- [x] MOPS egress batching (one HTTP per getter)
- [x] Context maps in gather batch (zero extra round trips)
- [x] Canonical schema shapes (interface, lldp, mac, optics)
- [x] 15 CRUD features migrated
- [x] All engine primitives (compute, set_format, membership_of, lookup, linked_tables, key_map, value_map, fields, index_key, index_type, regex, collect, compound index)
- [x] Execute methods on all transports
- [x] NAPALM config management (load_merge, commit, discard, rollback)
- [x] Protocol-free adapter, registry, lazy context maps
- [x] SNMP pysnmp 7.x compatibility
- [x] RSTP method-scoped attrs (set_rstp_port)
- [x] SNMP community/trap/info schemas
- [x] NTP stats + server CRUD
- [x] VLAN egress/ingress SET
- [x] LLDP crude_bits + aggregation as list
- [x] GMRP, GVRP, ACA, software, devsec schemas (JUSTIN wired)
