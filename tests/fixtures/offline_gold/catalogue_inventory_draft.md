# Offline-gold catalogue inventory (draft) — #169

No device identity. Classes are first-pass heuristics from schema + wire +
mops/ssh capture fixtures + sanitized floors. Untestable oper attrs are
hints until a method is floored and `config_absent` receipts list them.

**Counts:** `{"config_backed": 44, "gold_ready_no_floor": 11, "no_gold_yet": 11, "online_only": 13}`

| method | class | note |
| --- | --- | --- |
| `get_banner` | `config_backed` | sanitized floor; oper-ish schema attrs: [] |
| `get_dns` | `config_backed` | sanitized floor; oper-ish schema attrs: ['server_status'] |
| `get_facts` | `config_backed` | sanitized floor; oper-ish schema attrs: ['uptime', 'temperature'] |
| `get_hidiscovery` | `config_backed` | sanitized floor (PR after inventory); oper followups none in floor |
| `get_interfaces` | `config_backed` | sanitized floor; admin_status=config-backed (not oper); oper-ish schema attrs: ['oper_status', 'power_state', 'signal', 'flush_statistics'] |
| `get_mrp` | `config_backed` | sanitized floor; oper-ish schema attrs: ['operation', 'ring_port1_state', 'ring_port2_state', 'ring_state', 'mrp_status'] |
| `get_ntp` | `config_backed` | sanitized floor (PR after inventory); oper followups none in floor |
| `get_syslog` | `config_backed` | sanitized floor (PR after inventory); oper followups none in floor |
| `get_arp_inspection` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_arp_table` | `gold_ready_no_floor` | mops-fix+ssh-fix; wire=yes; oper-ish=['dai_vlan_acl_static'] |
| `get_auto_disable` | `gold_ready_no_floor` | mops-fix+ssh-fix; wire=yes; oper-ish=[] |
| `get_config` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_config_remote` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_config_status` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_dai_global` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_devsec_status` | `gold_ready_no_floor` | mops-fix+ssh-fix; wire=yes; oper-ish=['monitor_state', 'monitor_status', 'sec_state', 'sec_status', 'fan_status'] |
| `get_dhcp_snooping` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_gmrp` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_gvrp` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_interfaces_ip` | `gold_ready_no_floor` | mops-fix+ssh-fix; wire=yes; oper-ish=['oper_status', 'power_state', 'signal', 'flush_statistics'] |
| `get_ip_addresses` | `gold_ready_no_floor` | mops-fix+ssh-fix; wire=yes; oper-ish=['oper_status', 'power_state', 'signal', 'flush_statistics'] |
| `get_ip_restrict` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_login_policy` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_loop_protection` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_mac_address_table` | `gold_ready_no_floor` | mops-fix+ssh-fix; wire=yes; oper-ish=['status'] |
| `get_management` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_management_priority` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_mrp_sub_ring` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_ntp_servers` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_poe` | `gold_ready_no_floor` | mops-fix+ssh-fix; wire=yes; oper-ish=['status'] |
| `get_port_security` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_profiles` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_qos` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_qos_mapping` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_remote_auth` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_route_to` | `gold_ready_no_floor` | mops-fix+ssh-fix; wire=yes; oper-ish=[] |
| `get_rstp` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_rstp_port` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_services` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_session_config` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_signal_contact` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_snmp_config` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_snmp_information` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_snmp_trap_destinations` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_storm_control` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_system_info` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_users` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_vlan_egress` | `gold_ready_no_floor` | mops-fix+ssh-fix; wire=yes; oper-ish=['vlan_status'] |
| `get_vlan_ingress` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_vlans` | `gold_ready_no_floor` | mops-fix+ssh-fix; wire=yes; oper-ish=['vlan_status'] |
| `get_vrrp` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_vrrp_instances` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_vrrp_tracking` | `gold_ready_no_floor` | mops-fix+ssh-fix; wire=yes; oper-ish=['admin_state', 'row_status', 'state', 'uptime', 'oper_status', 'track_row_status'] |
| `get_watchdog_status` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_aca` | `no_gold_yet` | wire yes; no capture fixture; oper-ish=['envm_state', 'slot_status'] |
| `get_auto_disable_reasons` | `config_backed` | sanitized floor; config-backed attrs only |
| `get_devsec` | `no_gold_yet` | wire yes; no capture fixture; oper-ish=['state'] |
| `get_devsec_history` | `no_gold_yet` | wire yes; no capture fixture; oper-ish=['state'] |
| `get_ip_source_guard_bindings` | `no_gold_yet` | wire yes; no capture fixture; oper-ish=['binding_hw_status', 'binding_status'] |
| `get_ip_source_guard_port` | `no_gold_yet` | wire yes; no capture fixture; oper-ish=['binding_hw_status', 'binding_status'] |
| `get_router` | `no_gold_yet` | wire yes; no capture fixture; oper-ish=['vri_status'] |
| `get_sflow_poller` | `no_gold_yet` | wire yes; no capture fixture; oper-ish=[] |
| `get_sflow_receiver` | `no_gold_yet` | wire yes; no capture fixture; oper-ish=[] |
| `get_sflow_sampler` | `no_gold_yet` | wire yes; no capture fixture; oper-ish=[] |
| `get_software` | `no_gold_yet` | wire yes; no capture fixture; oper-ish=[] |
| `get_tracking` | `no_gold_yet` | wire yes; no capture fixture; oper-ish=['operstate', 'status'] |
| `get_device_monitor` | `online_only` | oper/live-leaning gather; fixtures mops=True ssh=True |
| `get_environment` | `online_only` | oper/live-leaning gather; fixtures mops=True ssh=True |
| `get_fan_status` | `online_only` | oper/live-leaning gather; fixtures mops=True ssh=True |
| `get_interface_statistics` | `online_only` | oper/live-leaning gather; fixtures mops=False ssh=False |
| `get_ipv6_neighbors` | `online_only` | oper/live-leaning gather; fixtures mops=True ssh=True |
| `get_ipv6_neighbors_table` | `online_only` | oper/live-leaning gather; fixtures mops=True ssh=True |
| `get_lldp_neighbors` | `online_only` | oper/live-leaning gather; fixtures mops=True ssh=True |
| `get_lldp_neighbors_detail` | `online_only` | oper/live-leaning gather; fixtures mops=True ssh=True |
| `get_lldp_neighbors_detail_extended` | `online_only` | oper/live-leaning gather; fixtures mops=True ssh=True |
| `get_ntp_stats` | `online_only` | oper/live-leaning gather; fixtures mops=False ssh=False |
| `get_optics` | `online_only` | oper/live-leaning gather; fixtures mops=True ssh=True |
| `get_system_health` | `online_only` | oper/live-leaning gather; fixtures mops=True ssh=True |
| `get_vrrp_stats` | `online_only` | oper/live-leaning gather; fixtures mops=True ssh=True |
