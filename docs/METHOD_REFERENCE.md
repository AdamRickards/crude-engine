# Method Quick Reference

Auto-generated from schema + protocol YAMLs. For full detail including per-protocol sources, see [API_REFERENCE.md](API_REFERENCE.md).

**186 methods** (174C/R/U/D + 12E) across **45 features**

## aca
_External NVM (ACA) configuration — selected memory, sync state, per-slot settings_

- **`get_aca()`** — Read
  Returns: `selected_memory`, `envm_state`, `slots`
- **`set_aca()`** — Update

## arp
_ARP table and Dynamic ARP Inspection (DAI) settings_

- **`get_arp_table()`** — Read, keyed by `ip`
  Returns: `interface`, `mac`, `ip`, `age`
- **`get_arp_inspection()`** — Read
  Returns: `enabled`, `validate_src_mac`, `validate_dst_mac`, `validate_ip`
- **`set_arp_inspection()`** — Update

## banner
_Login banner configuration (NERC CIP compliant)_

- **`get_banner()`** — Read
  Returns: `pre_login_enabled`, `pre_login_text`
- **`set_banner()`** — Update

## config
_Configuration management and watchdog status_

- **`get_config()`** — Read
  Returns: `running`, `startup`
- **`get_config_status()`** — Read
  Returns: `saved`, `last_changed`, `nvm`, `aca`, `boot`
- **`get_config_fingerprint()`** — Read
  Returns: `running`, `startup`
- **`get_config_remote()`** — Read
  Returns: `url`, `status`
- **`set_config_remote()`** — Update
- **`get_watchdog_status()`** — Read
  Returns: `watchdog_enabled`, `watchdog_interval`, `watchdog_remaining`
- **`set_watchdog()`** — Update

## dai_global
_Dynamic ARP Inspection global validation settings_

- **`get_dai_global()`** — Read
  Returns: `validate_src_mac`, `validate_dst_mac`, `validate_ip`
- **`set_dai_global()`** — Update

## devsec
_Device security monitoring — per-check enable/disable, status history, global state_

- **`get_devsec()`** — Read
  Returns: `state`, `trap_enabled`, `monitors`, `history`
- **`set_devsec()`** — Update
- **`get_devsec_history()`** — Read, keyed by `history_index`
  Returns: `cause`, `timestamp`

## dhcp_snooping
_DHCP Snooping global settings and port configuration_

- **`get_dhcp_snooping()`** — Read
  Returns: `enabled`, `verify_mac`, `database_file`, `ports`
- **`set_dhcp_snooping()`** — Update

## dns
_DNS client configuration and server table_

- **`get_dns()`** — Read
  Returns: `enabled`, `config_source`, `domain_name`, `timeout`, `retransmits`, `cache_enabled`, `servers`
- **`set_dns()`** — Update
- **`create_dns_server()`** — Create, requires: `address`
  Returns: `addr_type`
- **`delete_dns_server()`** — Delete

## gmrp
_GMRP (GARP Multicast Registration Protocol) configuration_

- **`get_gmrp()`** — Read
  Returns: `enabled`, `unknown_multicast`, `ports`
- **`set_gmrp()`** — Update
- **`set_gmrp_port()`** — Update

## gvrp
_GVRP (GARP VLAN Registration Protocol) configuration_

- **`get_gvrp()`** — Read
  Returns: `enabled`, `ports`
- **`set_gvrp()`** — Update
- **`set_gvrp_port()`** — Update

## hidiscovery
_HiDiscovery protocol settings_

- **`get_hidiscovery()`** — Read
  Returns: `enabled`, `mode`, `relay_enabled`, `blinking`
- **`set_hidiscovery()`** — Update

## interface
_Physical and logical interface configuration and status_

- **`get_interfaces()`** — Read, keyed by `name`
  Returns: `oper_status`, `admin_status`, `alias`, `speed`, `mtu`, `phys_address`
- **`get_interfaces_counters()`** — Read, keyed by `name`
  Returns: `tx_errors`, `rx_errors`, `tx_discards`, `rx_discards`, `tx_octets`, `rx_octets`, `tx_unicast_packets`, `rx_unicast_packets`, `tx_multicast_packets`, `rx_multicast_packets`, `tx_broadcast_packets`, `rx_broadcast_packets`
- **`get_ip_addresses()`** — Read
  Returns: `ipv4`
- **`get_interfaces_ip()`** — read
- **`set_interface()`** — Update

## ip_restrict
_IP restriction rules for management access_

- **`get_ip_restrict()`** — Read
  Returns: `enabled`, `logging`, `rules`
- **`create_ip_restrict_rule()`** — Create, requires: `ip`
  Returns: `addr_type`, `prefix_length`, `http`, `https`, `snmp`, `telnet`, `ssh`, `iec61850`, `modbus`, `ethernet_ip`, `profinet`, `per_rule_logging`
- **`delete_ip_restrict_rule()`** — Delete
- **`set_ip_restrict()`** — Update

## ip_source_guard
_IP Source Guard per-port settings and static binding table_

- **`get_ip_source_guard_port()`** — Read, keyed by `enabled`
  Returns: `enabled`, `port_security`
- **`set_ip_source_guard_port()`** — Update
- **`get_ip_source_guard_bindings()`** — Read, keyed by `binding_ip`
  Returns: `binding_ifindex`, `binding_vlan`, `binding_mac`, `binding_ip`, `binding_active`, `binding_hw_status`
- **`set_ip_source_guard_binding()`** — Update
- **`create_static_binding()`** — Create, requires: `binding_ifindex`
  Returns: `binding_vlan`
- **`delete_static_binding()`** — Delete

## ipv6
_IPv6 configuration and neighbor discovery_

- **`get_ipv6_neighbors()`** — Read
  Returns: `interface`, `ip`, `mac`, `state`
- **`get_ipv6_neighbors_table()`** — Read
  Returns: `interface`, `ip`, `mac`, `state`

## lldp
_LLDP configuration and neighbor table_

- **`get_lldp_neighbors()`** — Read, keyed by `local_port`
  Returns: `sys_name`, `port_id`
- **`get_lldp_neighbors_detail()`** — Read, keyed by `local_port`
  Returns: `port_id`, `sys_name`, `port_description`, `chassis_id`, `sys_description`, `sys_capabilities`, `sys_enabled_capabilities`, `autoneg_supported`, `autoneg_enabled`, `mau_type`, `pvid`, `aggregation_enabled`, `aggregation_port_id`
- **`get_lldp_neighbors_detail_extended()`** — read
- **`set_lldp()`** — Update

## mac
_MAC address table (FDB) mapping_

- **`get_mac_address_table()`** — Read, keyed by `mac`
  Returns: `mac`, `interface`, `vlan`, `status`

## management
_Management interface and access configuration_

- **`get_management()`** — Read
  Returns: `ip_address`, `prefix_length`, `netmask`, `gateway`, `vlan_id`, `protocol`
- **`set_management()`** — Update
- **`get_management_priority()`** — Read
  Returns: `source`, `priority`
- **`set_management_priority()`** — Update

## mrp
_Media Redundancy Protocol (MRP) domain configuration_

- **`get_mrp()`** — Read, keyed by `domain_id`
  Returns: `operation`, `role`, `domain_name`, `vlan`, `ring_port1`, `ring_port2`, `ring_port1_state`, `ring_port2_state`, `ring_state`, `recovery_delay`, `advanced_mode`, `manager_priority`, `fixed_backup`
- **`set_mrp()`** — Update
- **`create_mrp()`** — Create
  Returns: `domain_id`
- **`delete_mrp()`** — Delete
  Returns: `domain_id`

## mrp_sub_ring
_MRP Sub-Ring (SRM) configuration and status_

- **`get_mrp_sub_ring()`** — Read, keyed by `ring_id`
  Returns: `enabled`, `admin_state`, `oper_state`, `vlan`, `domain_id`, `sub_ring_name`, `sub_ring_port`, `sub_ring_port_state`, `sub_ring_state`, `redundancy`
- **`set_mrp_sub_ring()`** — Update
- **`create_mrp_sub_ring()`** — Create
- **`delete_mrp_sub_ring()`** — Delete

## ntp
_NTP/SNTP client configuration and server list_

- **`get_ntp()`** — Read
  Returns: `enabled`, `request_interval`, `server_enabled`, `server_stratum`, `servers`
- **`get_ntp_stats()`** — Read, keyed by `server_index`
  Returns: `remote`, `referenceid`, `synchronized`, `stratum`, `type`, `when`, `hostpoll`, `reachability`, `delay`, `offset`, `jitter`
- **`set_ntp()`** — Update
- **`get_ntp_servers()`** — Read, keyed by `server_index`
  Returns: `address`, `port`, `description`, `status`
- **`create_ntp_server()`** — Create, requires: `address`
  Returns: `addr_type`
- **`delete_ntp_server()`** — Delete

## optics
_SFP Transceiver digital diagnostics (DDM)_

- **`get_optics()`** — Read, keyed by `name`
  Returns: `tx_power`, `rx_power`, `temperature`

## poe
_Power over Ethernet (PoE) status and configuration_

- **`get_poe()`** — Read, keyed by `name`
  Returns: `enabled`, `power_limit`, `status`
- **`set_poe()`** — Update

## port_security
_Port Security (MAC limiting) per-port configuration_

- **`get_port_security()`** — Read
  Returns: `global_enabled`, `mode`, `auto_disable_enabled`, `ports`
- **`set_port_security()`** — Update
- **`create_port_security()`** — Update
- **`delete_port_security()`** — Update

## profile
_Device configuration profiles (NVM/ENVM)_

- **`get_profiles()`** — Read, keyed by `index`
  Returns: `name`, `active`, `fingerprint`, `firmware_version`, `datetime`, `fingerprint_verified`, `encrypted`, `encryption_verified`
- **`activate_profile()`** — Update
- **`delete_profile()`** — Update

## protection
_Network protection features: Storm Control, Loop Protection, and Auto-Disable_

- **`get_storm_control()`** — Read, keyed by `broadcast_enabled`
  Returns: `broadcast_enabled`, `broadcast_threshold`, `multicast_enabled`, `multicast_threshold`
- **`set_storm_control()`** — Update
- **`get_loop_protection()`** — Read
  Returns: `enabled`, `transmission_interval`, `rx_threshold`
- **`set_loop_protection()`** — Update
- **`get_auto_disable()`** — Read, keyed by `name`
  Returns: `enabled`, `reason`, `remaining_time`
- **`set_auto_disable()`** — Update
- **`set_auto_disable_reason()`** — Update

## qos
_Quality of Service (QoS) and Traffic Class mapping_

- **`get_qos()`** — Read
  Returns: `global_trust_mode`, `port_trust_mode`
- **`set_qos()`** — Update

## qos_mapping
_Global dot1p and DSCP to traffic class mapping tables_

- **`get_qos_mapping()`** — Read
- **`set_qos_mapping()`** — Update

## remote_auth
_RADIUS, TACACS+, and LDAP remote authentication_

- **`get_remote_auth()`** — Read
  Returns: `radius_enabled`, `radius_timeout`, `radius_retransmits`, `tacacs_enabled`, `tacacs_timeout`, `ldap_enabled`, `radius_servers`, `ldap_servers`, `tacacs_servers`
- **`set_remote_auth()`** — Update
- **`create_radius_server()`** — Create, requires: `address`
  Returns: `radius_addr_type`, `radius_port`
- **`delete_radius_server()`** — Delete
- **`create_ldap_server()`** — Create, requires: `ldap_address`
  Returns: `ldap_addr_type`, `ldap_port`
- **`delete_ldap_server()`** — Delete
- **`create_tacacs_server()`** — Create, requires: `tacacs_address`
  Returns: `tacacs_addr_type`
- **`delete_tacacs_server()`** — Delete
  Returns: `tacacs_addr_type`

## route
_IP routing table mapping_

- **`get_route_to()`** — Read, keyed by `destination`
  Returns: `protocol`, `next_hop`, `outgoing_interface`, `preference`, `age`

## router
_IP routing — global config, per-port L3 interfaces, VLAN router interfaces (VRI)_

- **`get_router()`** — Read
  Returns: `routing_enabled`, `ports`, `vri`
- **`set_router()`** — Update
- **`set_router_port()`** — Update
- **`set_router_vri()`** — Update
- **`create_router_vri()`** — Create
- **`delete_router_vri()`** — Delete

## rstp
_Rapid Spanning Tree Protocol (RSTP) configuration_

- **`get_rstp()`** — Read
  Returns: `enabled`, `priority`, `hello_time`, `max_age`, `forward_delay`, `bpdu_guard`
- **`set_rstp()`** — Update
- **`get_rstp_port()`** — Read, keyed by `enabled`
  Returns: `enabled`, `priority`, `path_cost`, `edge_port`
- **`set_rstp_port()`** — Update

## services
_Network services management (HTTP, HTTPS, Telnet, SSH, SNMP)_

- **`get_services()`** — Read
  Returns: `http`, `https`, `telnet`, `ssh`, `snmp_v1`, `snmp_v2`, `snmp_v3`
- **`set_services()`** — Update

## session_config
_Management session timeouts and limits_

- **`get_session_config()`** — Read
  Returns: `ssh_timeout`, `telnet_timeout`, `web_timeout`, `max_ssh_sessions`
- **`set_session_config()`** — Update

## sflow
_sFlow receiver, per-port sampler, and per-port poller configuration_

- **`get_sflow_receiver()`** — Read, keyed by `receiver_index`
  Returns: `receiver_index`, `owner`, `timeout`, `max_datagram_size`, `address`, `port`, `datagram_version`
- **`set_sflow_receiver()`** — Update
- **`get_sflow_sampler()`** — Read, keyed by `sampler_datasource`
  Returns: `sampler_datasource`, `sampler_receiver`, `sampling_rate`, `max_header_size`
- **`set_sflow_sampler()`** — Update
- **`get_sflow_poller()`** — Read, keyed by `poller_datasource`
  Returns: `poller_datasource`, `poller_receiver`, `interval`
- **`set_sflow_poller()`** — Update

## signal_contact
_Signal contact (relay) per-contact configuration, sense flags, and status_

- **`get_signal_contact()`** — Read, keyed by `contact_id`
  Returns: `contact_id`, `mode`, `state`, `trap_enabled`, `sense_link_failure`, `sense_temperature`, `sense_fan`, `sense_fan_module`, `sense_module`, `sense_module_removal`, `sense_ps_state`, `sense_envm_removal`, `sense_envm_not_in_sync`, `sense_ring_redundancy`, `sense_ethernet_loops`, `sense_humidity`, `sense_stp_port_block`, `sense_if_link_alarm`
- **`set_signal_contact()`** — Update

## snmp
_SNMP configuration — versions, port, communities, trap destinations_

- **`get_snmp_config()`** — Read
  Returns: `v1_enabled`, `v2_enabled`, `v3_enabled`, `port`, `trap_service`, `community_access`, `trap_destinations`
- **`set_snmp_config()`** — Update
- **`get_snmp_trap_destinations()`** — Read, keyed by `name`
  Returns: `address`, `security_model`, `security_name`, `security_level`
- **`create_snmp_trap_dest()`** — Create, requires: `name`, `address`
  Returns: `port`, `security_model`, `security_name`, `security_level`, `tag_list`
- **`delete_snmp_trap_dest()`** — Delete

## snmp_information
_NAPALM standard — system name, contact, location_

- **`get_snmp_information()`** — Read
  Returns: `chassis_id`, `contact`, `location`
- **`set_snmp_information()`** — Update

## software
_Software images, boot configuration, and integrity settings_

- **`get_software()`** — Read
  Returns: `allow_unsigned`, `secure_boot`, `dev_mode`, `bootcode`, `images`
- **`set_software()`** — Update

## syslog
_Syslog client configuration and server table_

- **`get_syslog()`** — Read
  Returns: `enabled`, `servers`
- **`set_syslog()`** — Update
- **`create_syslog_server()`** — Create, requires: `ip`
  Returns: `addr_type`, `port`, `severity`, `transport`, `log_type`
- **`delete_syslog_server()`** — Delete

## system
_System identity and hardware monitoring_

- **`get_system_info()`** — Read
  Returns: `hostname`, `contact`, `location`, `uptime`
- **`get_facts()`** — Read
  Returns: `hostname`, `fqdn`, `vendor`, `model`, `serial_number`, `os_version`, `uptime`, `interface_list`
- **`get_environment()`** — Read
  Returns: `temperature`, `fans`, `power`, `cpu`, `memory`
- **`get_system_health()`** — Read
  Returns: `temperature`, `humidity`, `hardware_version`, `product_description`
- **`set_system_info()`** — Update

## system_health
_Device monitoring and security status_

- **`get_device_monitor()`** — Read
  Returns: `oper_state`, `status_index`, `trap_cause`
- **`set_device_monitor()`** — Update
- **`get_devsec_status()`** — Read
  Returns: `oper_state`, `status_index`, `trap_cause`
- **`set_devsec_status()`** — Update
- **`get_fan_status()`** — Read
  Returns: `status`

## user
_User account management and password policy_

- **`get_users()`** — Read, keyed by `username`
  Returns: `level`, `locked`, `policy_check`, `snmp_auth`, `snmp_enc`, `default_password`
- **`set_user()`** — Update
- **`create_user()`** — Create, requires: `username`, `password`
  Returns: `level`
- **`delete_user()`** — Delete
- **`get_login_policy()`** — Read
  Returns: `min_length`, `max_attempts`, `lockout_time`
- **`set_login_policy()`** — Update

## vlan
_VLAN configuration, port membership and ingress/egress rules_

- **`get_vlans()`** — Read, keyed by `vlan_id`
  Returns: `name`, `ports`
- **`create_vlan()`** — Create, requires: `vlan_id`
- **`set_vlan()`** — Update
- **`delete_vlan()`** — Delete
- **`get_vlan_ingress()`** — Read, keyed by `pvid`
  Returns: `pvid`, `ingress_filtering`, `acceptable_frame_types`
- **`set_vlan_ingress()`** — Update
- **`set_access_port()`** — Update
- **`get_vlan_egress()`** — Read, keyed by `vlan_id`
  Returns: `egress_ports`, `untagged_ports`
- **`set_vlan_egress()`** — Update

## vrrp
_VRRP virtual router redundancy — global config, per-instance CRUD, stats_

- **`get_vrrp()`** — Read
  Returns: `enabled`, `trap_auth_failure`, `trap_new_master`
- **`get_vrrp_instances()`** — Read, keyed by `state`
  Returns: `vrid`, `admin_state`, `priority`, `current_priority`, `preempt`, `interval`, `accept_mode`, `primary_ip`, `virtual_ip`, `auth_type`, `state`, `master_ip`, `virtual_mac`, `uptime`, `ip_count`
- **`set_vrrp()`** — Update
- **`set_vrrp_instance()`** — Update
- **`create_vrrp()`** — Create, requires: `interface`, `vrid`, `primary_ip`
- **`delete_vrrp()`** — Delete
- **`get_vrrp_tracking()`** — Read, keyed by `oper_status`
  Returns: `track_vrid`, `track_name`, `decrement`, `oper_status`
- **`create_vrrp_tracking()`** — Create, requires: `track_interface`, `track_vrid`, `track_name`, `decrement`
- **`delete_vrrp_tracking()`** — Delete
- **`set_vrrp_tracking()`** — Update
- **`get_vrrp_stats()`** — Read
  Returns: `checksum_errors`, `version_errors`, `vrid_errors`

## Transport Execute Methods
_Operations declared in protocol YAMLs — connection, config, staging, CLI._

- **`clear_config()`** — Execute (MOPS, SNMP, SSH)
- **`clear_factory()`** — Execute (MOPS, SNMP, SSH)
- **`cli()`** — Execute (SSH)
- **`commit_staging()`** — Execute (MOPS)
- **`discard_staging()`** — Execute (MOPS)
- **`get_staged_mutations()`** — Execute (MOPS)
- **`is_factory_default()`** — Execute (MOPS, SSH)
- **`load_config()`** — Execute (MOPS)
- **`onboard()`** — Execute (MOPS, SSH)
- **`ping()`** — Execute (SSH)
- **`save_config()`** — Execute (MOPS, SNMP, SSH)
- **`start_staging()`** — Execute (MOPS)
