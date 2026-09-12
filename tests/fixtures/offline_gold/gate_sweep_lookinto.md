# offline_gold gate sweep — look-into list (draft)

Generated from catalogue-wide `offline_gold_matrix` (79 get_*). No device identity.
Re-proved on main after #170 squash (`b88e60c`); prior look-into commit had missed the squash.

## Sanitized fixtures (CI candidate)

- Methods: 79 schema gather
- Result: **PASS** (mismatch=0)
- Counts: match=25, config_absent=4, gold_absent=71, blocked=0, offline_empty=0
- Config sha256:d1724a093177  gold sha256:689585e062be

### Look-intos

1. **Missing floors (`gold_absent`, 71 methods)** — expand method-by-method; not a CI fail today.
2. **Oper followups (`config_absent`∩gold, 4)** — iface `oper_status` ×2; MRP `ring_port1_state` / `ring_state`.
3. **No harness blocked/crash** on full sanitized catalogue run.

### gold_absent methods

- `get_aca`
- `get_arp_inspection`
- `get_arp_table`
- `get_auto_disable`
- `get_auto_disable_reasons`
- `get_config`
- `get_config_remote`
- `get_config_status`
- `get_dai_global`
- `get_device_monitor`
- `get_devsec`
- `get_devsec_history`
- `get_devsec_status`
- `get_dhcp_snooping`
- `get_environment`
- `get_fan_status`
- `get_gmrp`
- `get_gvrp`
- `get_interface_statistics`
- `get_interfaces_ip`
- `get_ip_addresses`
- `get_ip_restrict`
- `get_ip_source_guard_bindings`
- `get_ip_source_guard_port`
- `get_ipv6_neighbors`
- `get_ipv6_neighbors_table`
- `get_lldp_neighbors`
- `get_lldp_neighbors_detail`
- `get_lldp_neighbors_detail_extended`
- `get_login_policy`
- `get_loop_protection`
- `get_mac_address_table`
- `get_management`
- `get_management_priority`
- `get_mrp_sub_ring`
- `get_ntp_servers`
- `get_ntp_stats`
- `get_optics`
- `get_poe`
- `get_port_security`
- `get_profiles`
- `get_qos`
- `get_qos_mapping`
- `get_remote_auth`
- `get_route_to`
- `get_router`
- `get_rstp`
- `get_rstp_port`
- `get_services`
- `get_session_config`
- `get_sflow_poller`
- `get_sflow_receiver`
- `get_sflow_sampler`
- `get_signal_contact`
- `get_snmp_config`
- `get_snmp_information`
- `get_snmp_trap_destinations`
- `get_software`
- `get_storm_control`
- `get_system_health`
- `get_system_info`
- `get_tracking`
- `get_users`
- `get_vlan_egress`
- `get_vlan_ingress`
- `get_vlans`
- `get_vrrp`
- `get_vrrp_instances`
- `get_vrrp_stats`
- `get_vrrp_tracking`
- `get_watchdog_status`

## Bag config + sanitized gold (local only)

- Result: **FAIL** mismatch=4 (expected — sanitized floors ≠ bag device)
- Mismatches: `get_facts.hostname`, `get_mrp` ring ports, `get_hidiscovery.relay_enabled`
- Look-into: bag prove needs **bag-local gold** (never commit); CI gate stays on sanitized fixtures.

## Gate-ready?

- **CI inclusion (narrow):** YES for DEFAULT_METHODS / floored set — exit≠0 only on mismatch; gold_absent is feedback.
- **CI inclusion (full 79):** informational only until floors grow; currently PASS with 71 gold_absent (does not fail).
- **Blocking full-floor CI:** missing sanitized floors + sample XML MIB coverage for honest config-backed attrs.
- **Bag:** optional wider prove; not CI.

## Update (floor expand)

Floors now **11** (+`get_login_policy`, `get_gvrp`, `get_gmrp`). DEFAULT prove match=35 mismatch=0 config_absent=4. Catalogue: config_backed=11, gold_ready_no_floor=43. 79-stress: see PR trail.

## Update (floor expand #2)

Floors **14** (+`get_dai_global`, `get_dhcp_snooping`, `get_session_config`).

## Update (floor expand #3)

Floors **17** (+`get_snmp_config`, `get_services`, `get_rstp`).

## Update (floor expand #4)

Floors **20** (+`get_loop_protection`, `get_vlan_ingress`, `get_auto_disable_reasons`). `get_vlans` still empty Offline gather — look-into.
