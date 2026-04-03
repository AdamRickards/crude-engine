# crude-engine API Reference

Automatically generated from schema, wire, and protocol YAMLs.

**45 features** | **174 methods** (16C 68R 64U 16D 0E) | **Protocols:** MOPS, SNMP, SSH

## Table of Contents

- **[aca](#aca)** — `get_aca` (Read, MOPS/SNMP), `set_aca` (Update, MOPS/SNMP)
- **[arp](#arp)** — `get_arp_table` (list, MOPS/SNMP), `get_arp_inspection` (Read, MOPS/SNMP), `set_arp_inspection` (Update, MOPS/SNMP)
- **[banner](#banner)** — `get_banner` (Read, MOPS/SNMP), `set_banner` (Update, MOPS/SNMP)
- **[config](#config)** — `get_config` (Read, None), `get_config_status` (Read, MOPS/SNMP), `get_config_fingerprint` (Read, None), `get_config_remote` (Read, None), `set_config_remote` (Update, MOPS/SNMP), `get_watchdog_status` (Read, MOPS/SNMP), `set_watchdog` (Update, MOPS/SNMP)
- **[dai_global](#dai_global)** — `get_dai_global` (Read, MOPS/SNMP), `set_dai_global` (Update, MOPS/SNMP)
- **[devsec](#devsec)** — `get_devsec` (Read, MOPS/SNMP), `set_devsec` (Update, MOPS/SNMP), `get_devsec_history` (Read, MOPS/SNMP)
- **[dhcp_snooping](#dhcp_snooping)** — `get_dhcp_snooping` (Read, MOPS/SNMP), `set_dhcp_snooping` (Update, MOPS/SNMP)
- **[dns](#dns)** — `get_dns` (Read, MOPS/SNMP/SSH), `set_dns` (Update, MOPS/SNMP/SSH), `create_dns_server` (Create, MOPS/SNMP/SSH), `delete_dns_server` (Delete, MOPS/SNMP/SSH)
- **[gmrp](#gmrp)** — `get_gmrp` (Read, MOPS/SNMP), `set_gmrp` (Update, MOPS/SNMP), `set_gmrp_port` (Update, MOPS/SNMP)
- **[gvrp](#gvrp)** — `get_gvrp` (Read, MOPS/SNMP), `set_gvrp` (Update, MOPS/SNMP), `set_gvrp_port` (Update, MOPS/SNMP)
- **[hidiscovery](#hidiscovery)** — `get_hidiscovery` (Read, MOPS/SNMP), `set_hidiscovery` (Update, MOPS/SNMP)
- **[interface](#interface)** — `get_interfaces` (Read, MOPS/SNMP), `get_interfaces_counters` (Read, MOPS/SNMP), `get_ip_addresses` (Read, None), `get_interfaces_ip` (Read, MOPS/SNMP), `set_interface` (Update, MOPS/SNMP)
- **[ip_restrict](#ip_restrict)** — `get_ip_restrict` (Read, MOPS/SNMP/SSH), `create_ip_restrict_rule` (Create, MOPS/SNMP/SSH), `delete_ip_restrict_rule` (Delete, MOPS/SNMP/SSH), `set_ip_restrict` (Update, MOPS/SNMP/SSH)
- **[ip_source_guard](#ip_source_guard)** — `get_ip_source_guard_port` (Read, MOPS/SNMP), `set_ip_source_guard_port` (Update, MOPS/SNMP), `get_ip_source_guard_bindings` (list, MOPS/SNMP), `set_ip_source_guard_binding` (Update, MOPS/SNMP), `create_static_binding` (Create, MOPS/SNMP), `delete_static_binding` (Delete, MOPS/SNMP)
- **[ipv6](#ipv6)** — `get_ipv6_neighbors` (list, MOPS/SNMP), `get_ipv6_neighbors_table` (list, MOPS/SNMP)
- **[lldp](#lldp)** — `get_lldp_neighbors` (list_append, MOPS/SNMP), `get_lldp_neighbors_detail` (list_append, MOPS/SNMP), `get_lldp_neighbors_detail_extended` (Read, MOPS/SNMP), `set_lldp` (Update, MOPS/SNMP)
- **[mac](#mac)** — `get_mac_address_table` (list, MOPS/SNMP)
- **[management](#management)** — `get_management` (Read, MOPS/SNMP), `set_management` (Update, MOPS/SNMP), `get_management_priority` (list, None), `set_management_priority` (Update, MOPS/SNMP)
- **[mrp](#mrp)** — `get_mrp` (Read, MOPS/SNMP), `set_mrp` (Update, MOPS/SNMP), `create_mrp` (Create, MOPS/SNMP), `delete_mrp` (Delete, MOPS/SNMP)
- **[mrp_sub_ring](#mrp_sub_ring)** — `get_mrp_sub_ring` (Read, MOPS/SNMP), `set_mrp_sub_ring` (Update, MOPS/SNMP), `create_mrp_sub_ring` (Create, MOPS/SNMP), `delete_mrp_sub_ring` (Delete, MOPS/SNMP)
- **[ntp](#ntp)** — `get_ntp` (Read, MOPS/SNMP/SSH), `get_ntp_stats` (list, MOPS/SNMP/SSH), `set_ntp` (Update, MOPS/SNMP/SSH), `get_ntp_servers` (Read, MOPS/SNMP/SSH), `create_ntp_server` (Create, MOPS/SNMP/SSH), `delete_ntp_server` (Delete, MOPS/SNMP/SSH)
- **[optics](#optics)** — `get_optics` (Read, MOPS/SNMP)
- **[poe](#poe)** — `get_poe` (Read, MOPS/SNMP), `set_poe` (Update, MOPS/SNMP)
- **[port_security](#port_security)** — `get_port_security` (Read, MOPS/SNMP/SSH), `set_port_security` (Update, MOPS/SNMP/SSH), `create_port_security` (Update, MOPS/SNMP/SSH), `delete_port_security` (Update, MOPS/SNMP/SSH)
- **[profile](#profile)** — `get_profiles` (Read, MOPS/SNMP/SSH), `activate_profile` (Update, MOPS/SNMP/SSH), `delete_profile` (Update, MOPS/SNMP/SSH)
- **[protection](#protection)** — `get_storm_control` (Read, MOPS/SNMP), `set_storm_control` (Update, MOPS/SNMP), `get_loop_protection` (Read, None), `set_loop_protection` (Update, MOPS/SNMP), `get_auto_disable` (Read, None), `set_auto_disable` (Update, MOPS/SNMP), `set_auto_disable_reason` (Update, MOPS/SNMP)
- **[qos](#qos)** — `get_qos` (Read, MOPS/SNMP), `set_qos` (Update, MOPS/SNMP)
- **[qos_mapping](#qos_mapping)** — `get_qos_mapping` (Read, MOPS/SNMP), `set_qos_mapping` (Update, MOPS/SNMP)
- **[remote_auth](#remote_auth)** — `get_remote_auth` (Read, MOPS/SNMP/SSH), `set_remote_auth` (Update, MOPS/SNMP/SSH), `create_radius_server` (Create, MOPS/SNMP/SSH), `delete_radius_server` (Delete, MOPS/SNMP/SSH), `create_ldap_server` (Create, MOPS/SNMP/SSH), `delete_ldap_server` (Delete, MOPS/SNMP/SSH), `create_tacacs_server` (Create, MOPS/SNMP/SSH), `delete_tacacs_server` (Delete, MOPS/SNMP)
- **[route](#route)** — `get_route_to` (Read, MOPS/SNMP)
- **[router](#router)** — `get_router` (Read, MOPS/SNMP), `set_router` (Update, MOPS/SNMP), `set_router_port` (Update, MOPS/SNMP), `set_router_vri` (Update, MOPS/SNMP), `create_router_vri` (Create, MOPS/SNMP), `delete_router_vri` (Delete, MOPS/SNMP)
- **[rstp](#rstp)** — `get_rstp` (Read, MOPS/SNMP), `set_rstp` (Update, MOPS/SNMP), `get_rstp_port` (Read, MOPS/SNMP), `set_rstp_port` (Update, MOPS/SNMP)
- **[services](#services)** — `get_services` (Read, MOPS/SNMP), `set_services` (Update, MOPS/SNMP)
- **[session_config](#session_config)** — `get_session_config` (Read, MOPS/SNMP), `set_session_config` (Update, MOPS/SNMP)
- **[sflow](#sflow)** — `get_sflow_receiver` (Read, MOPS/SNMP), `set_sflow_receiver` (Update, MOPS/SNMP), `get_sflow_sampler` (Read, MOPS/SNMP), `set_sflow_sampler` (Update, MOPS/SNMP), `get_sflow_poller` (Read, MOPS/SNMP), `set_sflow_poller` (Update, MOPS/SNMP)
- **[signal_contact](#signal_contact)** — `get_signal_contact` (Read, MOPS/SNMP), `set_signal_contact` (Update, MOPS/SNMP)
- **[snmp](#snmp)** — `get_snmp_config` (Read, MOPS/SNMP/SSH), `set_snmp_config` (Update, MOPS/SNMP/SSH), `get_snmp_trap_destinations` (Read, MOPS/SNMP/SSH), `create_snmp_trap_dest` (Create, MOPS/SNMP/SSH), `delete_snmp_trap_dest` (Delete, MOPS/SNMP/SSH)
- **[snmp_information](#snmp_information)** — `get_snmp_information` (Read, MOPS/SNMP), `set_snmp_information` (Update, MOPS/SNMP)
- **[software](#software)** — `get_software` (Read, MOPS/SNMP), `set_software` (Update, MOPS/SNMP)
- **[syslog](#syslog)** — `get_syslog` (Read, MOPS/SNMP/SSH), `set_syslog` (Update, MOPS/SNMP/SSH), `create_syslog_server` (Create, MOPS/SNMP/SSH), `delete_syslog_server` (Delete, MOPS/SNMP/SSH)
- **[system](#system)** — `get_system_info` (Read, MOPS/SNMP), `get_facts` (Read, MOPS/SNMP), `get_environment` (Read, MOPS/SNMP), `get_system_health` (Read, MOPS/SNMP), `set_system_info` (Update, MOPS/SNMP)
- **[system_health](#system_health)** — `get_device_monitor` (Read, None), `set_device_monitor` (Update, MOPS/SNMP), `get_devsec_status` (Read, None), `set_devsec_status` (Update, MOPS/SNMP), `get_fan_status` (list, None)
- **[user](#user)** — `get_users` (Read, MOPS/SNMP/SSH), `set_user` (Update, MOPS/SNMP/SSH), `create_user` (Create, MOPS/SNMP/SSH), `delete_user` (Delete, MOPS/SNMP/SSH), `get_login_policy` (Read, MOPS/SNMP/SSH), `set_login_policy` (Update, MOPS/SNMP/SSH)
- **[vlan](#vlan)** — `get_vlans` (Read, MOPS/SNMP), `create_vlan` (Create, MOPS/SNMP), `set_vlan` (Update, MOPS/SNMP/SSH), `delete_vlan` (Delete, MOPS/SNMP/SSH), `get_vlan_ingress` (Read, MOPS/SNMP), `set_vlan_ingress` (Update, MOPS/SNMP/SSH), `set_access_port` (Update, MOPS/SNMP/SSH), `get_vlan_egress` (Read, MOPS/SNMP), `set_vlan_egress` (Update, MOPS/SNMP/SSH)
- **[vrrp](#vrrp)** — `get_vrrp` (Read, MOPS/SNMP), `get_vrrp_instances` (Read, MOPS/SNMP), `set_vrrp` (Update, MOPS/SNMP), `set_vrrp_instance` (Update, MOPS/SNMP), `create_vrrp` (Create, MOPS/SNMP), `delete_vrrp` (Delete, None), `get_vrrp_tracking` (Read, MOPS/SNMP), `create_vrrp_tracking` (Create, MOPS/SNMP), `delete_vrrp_tracking` (Delete, None), `set_vrrp_tracking` (Update, MOPS/SNMP), `get_vrrp_stats` (Read, MOPS/SNMP)

---

## Transport Operations

Operational methods declared in protocol YAMLs.

**MOPS:** `save_config()`, `load_config()`, `onboard()`, `clear_config()`, `clear_factory()`, `start_staging()`, `commit_staging()`, `discard_staging()`, `get_staged_mutations()`, `is_factory_default()`
**SNMP:** `save_config()`, `clear_config()`, `clear_factory()`
**SSH:** `save_config()`, `clear_config()`, `clear_factory()`, `onboard()`, `cli()`, `ping()`, `is_factory_default()`

---

## aca

_External NVM (ACA) configuration — selected memory, sync state, per-slot settings_

### `get_aca()`

**Read** | **Protocols:** MOPS, SNMP

```
get_aca() -> {
    selected_memory: "none"  // "none" | "sd" | "usb" | "serial"
    envm_state: "absent"  // "ok" | "outOfSync" | "absent"
    slots: {...}  // dict
}
```

> Sub-table: **`slots`** — key: `slot_type`

<details><summary>MOPS sources (11/11 attrs)</summary>

```
MOPS {
  config_load_priority: {HM2-DEVMGMT-MIB / hm2ExtNvmEntry.hm2ExtNvmConfigLoadPriority}  # INTEGER, access=ru, allowed=['disable', 'first', 'second', 'third']
  slot_type: {HM2-DEVMGMT-MIB / hm2ExtNvmEntry.hm2ExtNvmTableIndex}  # Hm2DeviceExtNVMType, access=r
  auto_update: {HM2-DEVMGMT-MIB / hm2ExtNvmEntry.hm2ExtNvmAutomaticSoftwareLoad}  # HmEnabledStatus, access=ru, allowed=[True, False]
  config_save: {HM2-DEVMGMT-MIB / hm2ExtNvmEntry.hm2ExtNvmConfigSave}  # HmEnabledStatus, access=ru, allowed=[True, False]
  auto_ssh_key: {HM2-DEVMGMT-MIB / hm2ExtNvmEntry.hm2ExtNvmAutomaticSshKeyLoad}  # HmEnabledStatus, access=ru, allowed=[True, False]
  slot_serial: {HM2-DEVMGMT-MIB / hm2ExtNvmEntry.hm2ExtNvmSerialNum}  # DisplayString, access=r
  selected_memory: {HM2-DEVMGMT-MIB / hm2ExtNvmGeneralGroup.hm2ExtNvmChooseActive}  # Hm2DeviceExtNVMType, access=ru
  envm_state: {HM2-FILEMGMT-MIB / hm2FileMgmtStatusGroup.hm2FMEnvmState}  # INTEGER, access=r, allowed=['ok', 'outOfSync', 'absent']
  slot_name: {HM2-DEVMGMT-MIB / hm2ExtNvmEntry.hm2ExtNvmProductName}  # DisplayString, access=r
  slot_status: {HM2-DEVMGMT-MIB / hm2ExtNvmEntry.hm2ExtNvmStatus}  # INTEGER, access=r
  slot_writable: {HM2-DEVMGMT-MIB / hm2ExtNvmEntry.hm2ExtNvmWritable}  # HmEnabledStatus, access=r, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (11/11 attrs)</summary>

```
SNMP {
  config_load_priority: {oid: 1.3.6.1.4.1.248.11.10.1.8.2.1.9}  # INTEGER, access=ru, allowed=['disable', 'first', 'second', 'third']
  slot_type: {oid: 1.3.6.1.4.1.248.11.10.1.8.2.1.1}  # Hm2DeviceExtNVMType, access=r
  auto_update: {oid: 1.3.6.1.4.1.248.11.10.1.8.2.1.8}  # HmEnabledStatus, access=ru, allowed=[True, False]
  config_save: {oid: 1.3.6.1.4.1.248.11.10.1.8.2.1.10}  # HmEnabledStatus, access=ru, allowed=[True, False]
  auto_ssh_key: {oid: 1.3.6.1.4.1.248.11.10.1.8.2.1.12}  # HmEnabledStatus, access=ru, allowed=[True, False]
  slot_serial: {oid: 1.3.6.1.4.1.248.11.10.1.8.2.1.7}  # DisplayString, access=r
  selected_memory: {oid: 1.3.6.1.4.1.248.11.10.1.8.1.1, method: get}  # Hm2DeviceExtNVMType, access=ru
  envm_state: {oid: 1.3.6.1.4.1.248.11.21.1.3.2, method: get}  # INTEGER, access=r, allowed=['ok', 'outOfSync', 'absent']
  slot_name: {oid: 1.3.6.1.4.1.248.11.10.1.8.2.1.5}  # DisplayString, access=r
  slot_status: {oid: 1.3.6.1.4.1.248.11.10.1.8.2.1.2}  # INTEGER, access=r
  slot_writable: {oid: 1.3.6.1.4.1.248.11.10.1.8.2.1.11}  # HmEnabledStatus, access=r, allowed=[True, False]
}
```
</details>

### `set_aca()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (11/11 attrs)</summary>

```
MOPS {
  config_load_priority: {HM2-DEVMGMT-MIB / hm2ExtNvmEntry.hm2ExtNvmConfigLoadPriority}  # INTEGER, access=ru, allowed=['disable', 'first', 'second', 'third']
  slot_type: {HM2-DEVMGMT-MIB / hm2ExtNvmEntry.hm2ExtNvmTableIndex}  # Hm2DeviceExtNVMType, access=r
  auto_update: {HM2-DEVMGMT-MIB / hm2ExtNvmEntry.hm2ExtNvmAutomaticSoftwareLoad}  # HmEnabledStatus, access=ru, allowed=[True, False]
  config_save: {HM2-DEVMGMT-MIB / hm2ExtNvmEntry.hm2ExtNvmConfigSave}  # HmEnabledStatus, access=ru, allowed=[True, False]
  auto_ssh_key: {HM2-DEVMGMT-MIB / hm2ExtNvmEntry.hm2ExtNvmAutomaticSshKeyLoad}  # HmEnabledStatus, access=ru, allowed=[True, False]
  slot_serial: {HM2-DEVMGMT-MIB / hm2ExtNvmEntry.hm2ExtNvmSerialNum}  # DisplayString, access=r
  selected_memory: {HM2-DEVMGMT-MIB / hm2ExtNvmGeneralGroup.hm2ExtNvmChooseActive}  # Hm2DeviceExtNVMType, access=ru
  envm_state: {HM2-FILEMGMT-MIB / hm2FileMgmtStatusGroup.hm2FMEnvmState}  # INTEGER, access=r, allowed=['ok', 'outOfSync', 'absent']
  slot_name: {HM2-DEVMGMT-MIB / hm2ExtNvmEntry.hm2ExtNvmProductName}  # DisplayString, access=r
  slot_status: {HM2-DEVMGMT-MIB / hm2ExtNvmEntry.hm2ExtNvmStatus}  # INTEGER, access=r
  slot_writable: {HM2-DEVMGMT-MIB / hm2ExtNvmEntry.hm2ExtNvmWritable}  # HmEnabledStatus, access=r, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (11/11 attrs)</summary>

```
SNMP {
  config_load_priority: {oid: 1.3.6.1.4.1.248.11.10.1.8.2.1.9}  # INTEGER, access=ru, allowed=['disable', 'first', 'second', 'third']
  slot_type: {oid: 1.3.6.1.4.1.248.11.10.1.8.2.1.1}  # Hm2DeviceExtNVMType, access=r
  auto_update: {oid: 1.3.6.1.4.1.248.11.10.1.8.2.1.8}  # HmEnabledStatus, access=ru, allowed=[True, False]
  config_save: {oid: 1.3.6.1.4.1.248.11.10.1.8.2.1.10}  # HmEnabledStatus, access=ru, allowed=[True, False]
  auto_ssh_key: {oid: 1.3.6.1.4.1.248.11.10.1.8.2.1.12}  # HmEnabledStatus, access=ru, allowed=[True, False]
  slot_serial: {oid: 1.3.6.1.4.1.248.11.10.1.8.2.1.7}  # DisplayString, access=r
  selected_memory: {oid: 1.3.6.1.4.1.248.11.10.1.8.1.1, method: get}  # Hm2DeviceExtNVMType, access=ru
  envm_state: {oid: 1.3.6.1.4.1.248.11.21.1.3.2, method: get}  # INTEGER, access=r, allowed=['ok', 'outOfSync', 'absent']
  slot_name: {oid: 1.3.6.1.4.1.248.11.10.1.8.2.1.5}  # DisplayString, access=r
  slot_status: {oid: 1.3.6.1.4.1.248.11.10.1.8.2.1.2}  # INTEGER, access=r
  slot_writable: {oid: 1.3.6.1.4.1.248.11.10.1.8.2.1.11}  # HmEnabledStatus, access=r, allowed=[True, False]
}
```
</details>

---

## arp

_ARP table and Dynamic ARP Inspection (DAI) settings_

### `get_arp_table()`

**list** | **Protocols:** MOPS, SNMP
Primary key: `ip`

```
get_arp_table() -> {
    interface: ""  // str
    mac: ""  // str
    ip: ""  // str
    age: 0.0  // float
}
```


<details><summary>MOPS sources (4/4 attrs)</summary>

```
MOPS {
  interface: {IP-MIB / ipNetToPhysicalEntry.ipNetToPhysicalIfIndex}  # InterfaceIndex, access=r
  age: {IP-MIB / ipNetToPhysicalEntry.ipNetToPhysicalLastUpdated}  # TimeStamp, access=r
  mac: {IP-MIB / ipNetToPhysicalEntry.ipNetToPhysicalPhysAddress}  # PhysAddress, access=ru, range=0–65535
  ip: {IP-MIB / ipNetToPhysicalEntry.ipNetToPhysicalNetAddress}  # InetAddress, access=r
}
```
</details>

<details><summary>SNMP sources (4/4 attrs)</summary>

```
SNMP {
  interface: {oid: 1.3.6.1.2.1.4.35.1.1}  # InterfaceIndex, access=r
  age: {oid: 1.3.6.1.2.1.4.35.1.5}  # TimeStamp, access=r
  mac: {oid: 1.3.6.1.2.1.4.35.1.4}  # PhysAddress, access=ru, range=0–65535
  ip: {oid: 1.3.6.1.2.1.4.35.1.3}  # InetAddress, access=r
}
```
</details>

### `get_arp_inspection()`

**Read** | **Protocols:** MOPS, SNMP

```
get_arp_inspection() -> {
    enabled: False  // bool
    validate_src_mac: False  // bool
    validate_dst_mac: False  // bool
    validate_ip: False  // bool
}
```


<details><summary>MOPS sources (4/4 attrs)</summary>

```
MOPS {
  validate_ip: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentDaiConfigGroup.hm2AgentDaiIPValidate}  # TruthValue, access=ru, allowed=[True, False]
  enabled: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentDaiVlanConfigEntry.hm2AgentDaiVlanDynArpInspEnable}  # TruthValue, access=ru, allowed=[True, False]
  validate_src_mac: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentDaiConfigGroup.hm2AgentDaiSrcMacValidate}  # TruthValue, access=ru, allowed=[True, False]
  validate_dst_mac: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentDaiConfigGroup.hm2AgentDaiDstMacValidate}  # TruthValue, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (4/4 attrs)</summary>

```
SNMP {
  validate_ip: {oid: 1.3.6.1.4.1.248.12.1.2.8.21.3, method: get}  # TruthValue, access=ru, allowed=[True, False]
  enabled: {oid: 1.3.6.1.4.1.248.12.1.2.8.21.4.1.2}  # TruthValue, access=ru, allowed=[True, False]
  validate_src_mac: {oid: 1.3.6.1.4.1.248.12.1.2.8.21.1, method: get}  # TruthValue, access=ru, allowed=[True, False]
  validate_dst_mac: {oid: 1.3.6.1.4.1.248.12.1.2.8.21.2, method: get}  # TruthValue, access=ru, allowed=[True, False]
}
```
</details>

### `set_arp_inspection()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (8/8 attrs)</summary>

```
MOPS {
  enabled: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentDaiVlanConfigEntry.hm2AgentDaiVlanDynArpInspEnable}  # TruthValue, access=ru, allowed=[True, False]
  validate_src_mac: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentDaiConfigGroup.hm2AgentDaiSrcMacValidate}  # TruthValue, access=ru, allowed=[True, False]
  age: {IP-MIB / ipNetToPhysicalEntry.ipNetToPhysicalLastUpdated}  # TimeStamp, access=r
  validate_ip: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentDaiConfigGroup.hm2AgentDaiIPValidate}  # TruthValue, access=ru, allowed=[True, False]
  mac: {IP-MIB / ipNetToPhysicalEntry.ipNetToPhysicalPhysAddress}  # PhysAddress, access=ru, range=0–65535
  validate_dst_mac: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentDaiConfigGroup.hm2AgentDaiDstMacValidate}  # TruthValue, access=ru, allowed=[True, False]
  interface: {IP-MIB / ipNetToPhysicalEntry.ipNetToPhysicalIfIndex}  # InterfaceIndex, access=r
  ip: {IP-MIB / ipNetToPhysicalEntry.ipNetToPhysicalNetAddress}  # InetAddress, access=r
}
```
</details>

<details><summary>SNMP sources (8/8 attrs)</summary>

```
SNMP {
  enabled: {oid: 1.3.6.1.4.1.248.12.1.2.8.21.4.1.2}  # TruthValue, access=ru, allowed=[True, False]
  validate_src_mac: {oid: 1.3.6.1.4.1.248.12.1.2.8.21.1, method: get}  # TruthValue, access=ru, allowed=[True, False]
  age: {oid: 1.3.6.1.2.1.4.35.1.5}  # TimeStamp, access=r
  validate_ip: {oid: 1.3.6.1.4.1.248.12.1.2.8.21.3, method: get}  # TruthValue, access=ru, allowed=[True, False]
  mac: {oid: 1.3.6.1.2.1.4.35.1.4}  # PhysAddress, access=ru, range=0–65535
  validate_dst_mac: {oid: 1.3.6.1.4.1.248.12.1.2.8.21.2, method: get}  # TruthValue, access=ru, allowed=[True, False]
  interface: {oid: 1.3.6.1.2.1.4.35.1.1}  # InterfaceIndex, access=r
  ip: {oid: 1.3.6.1.2.1.4.35.1.3}  # InetAddress, access=r
}
```
</details>

---

## banner

_Login banner configuration (NERC CIP compliant)_

### `get_banner()`

**Read** | **Protocols:** MOPS, SNMP

```
get_banner() -> {
    pre_login_enabled: False  // bool
    pre_login_text: ""  // str
}
```


<details><summary>MOPS sources (2/2 attrs)</summary>

```
MOPS {
  pre_login_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessPreLoginBannerGroup.hm2PreLoginBannerAdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  pre_login_text: {HM2-MGMTACCESS-MIB / hm2MgmtAccessPreLoginBannerGroup.hm2PreLoginBannerText}  # HmLargeDisplayString, access=ru, range=0–512
}
```
</details>

<details><summary>SNMP sources (2/2 attrs)</summary>

```
SNMP {
  pre_login_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.5.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  pre_login_text: {oid: 1.3.6.1.4.1.248.11.25.1.5.2, method: get}  # HmLargeDisplayString, access=ru, range=0–512
}
```
</details>

### `set_banner()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (2/2 attrs)</summary>

```
MOPS {
  pre_login_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessPreLoginBannerGroup.hm2PreLoginBannerAdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  pre_login_text: {HM2-MGMTACCESS-MIB / hm2MgmtAccessPreLoginBannerGroup.hm2PreLoginBannerText}  # HmLargeDisplayString, access=ru, range=0–512
}
```
</details>

<details><summary>SNMP sources (2/2 attrs)</summary>

```
SNMP {
  pre_login_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.5.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  pre_login_text: {oid: 1.3.6.1.4.1.248.11.25.1.5.2, method: get}  # HmLargeDisplayString, access=ru, range=0–512
}
```
</details>

---

## config

_Configuration management and watchdog status_

### `get_config()`

**Read** | **Protocols:** None

```
get_config() -> {
    running: ""  // str
    startup: ""  // str
}
```


### `get_config_status()`

**Read** | **Protocols:** MOPS, SNMP

```
get_config_status() -> {
    saved: True  // bool (computed)
    last_changed: ""  // str
    nvm: "ok"  // "ok" | "outOfSync" | "busy"
    aca: "absent"  // "ok" | "outOfSync" | "absent"
    boot: "ok"  // "ok" | "outOfSync"
}
```


<details><summary>MOPS sources (3/4 attrs)</summary>

```
MOPS {
  aca: {HM2-FILEMGMT-MIB / hm2FileMgmtStatusGroup.hm2FMEnvmState}  # INTEGER, access=r, allowed=['ok', 'outOfSync', 'absent']
  nvm: {HM2-FILEMGMT-MIB / hm2FileMgmtStatusGroup.hm2FMNvmState}  # INTEGER, access=r, allowed=['ok', 'outOfSync', 'busy']
  boot: {HM2-FILEMGMT-MIB / hm2FileMgmtStatusGroup.hm2FMBootParamState}  # INTEGER, access=r, allowed=['ok', 'outOfSync']
}
```
</details>

<details><summary>SNMP sources (3/4 attrs)</summary>

```
SNMP {
  aca: {oid: 1.3.6.1.4.1.248.11.21.1.3.2, method: get}  # INTEGER, access=r, allowed=['ok', 'outOfSync', 'absent']
  nvm: {oid: 1.3.6.1.4.1.248.11.21.1.3.1, method: get}  # INTEGER, access=r, allowed=['ok', 'outOfSync', 'busy']
  boot: {oid: 1.3.6.1.4.1.248.11.21.1.3.3, method: get}  # INTEGER, access=r, allowed=['ok', 'outOfSync']
}
```
</details>

### `get_config_fingerprint()`

**Read** | **Protocols:** None

```
get_config_fingerprint() -> {
    running: ""  // str
    startup: ""  // str
}
```


### `get_config_remote()`

**Read** | **Protocols:** None

```
get_config_remote() -> {
    url: ""  // str
    status: "idle"  // str
}
```


### `set_config_remote()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (6/7 attrs)</summary>

```
MOPS {
  aca: {HM2-FILEMGMT-MIB / hm2FileMgmtStatusGroup.hm2FMEnvmState}  # INTEGER, access=r, allowed=['ok', 'outOfSync', 'absent']
  watchdog_interval: {HM2-FILEMGMT-MIB / hm2FileMgmtConfigWatchdogControl.hm2ConfigWatchdogTimeInterval}  # Integer32 (30..600), access=ru, range=30–600
  watchdog_remaining: {HM2-FILEMGMT-MIB / hm2FileMgmtConfigWatchdogControl.hm2ConfigWatchdogTimerValue}  # Integer32, access=r
  nvm: {HM2-FILEMGMT-MIB / hm2FileMgmtStatusGroup.hm2FMNvmState}  # INTEGER, access=r, allowed=['ok', 'outOfSync', 'busy']
  watchdog_enabled: {HM2-FILEMGMT-MIB / hm2FileMgmtConfigWatchdogControl.hm2ConfigWatchdogAdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  boot: {HM2-FILEMGMT-MIB / hm2FileMgmtStatusGroup.hm2FMBootParamState}  # INTEGER, access=r, allowed=['ok', 'outOfSync']
}
```
</details>

<details><summary>SNMP sources (6/7 attrs)</summary>

```
SNMP {
  aca: {oid: 1.3.6.1.4.1.248.11.21.1.3.2, method: get}  # INTEGER, access=r, allowed=['ok', 'outOfSync', 'absent']
  watchdog_interval: {oid: 1.3.6.1.4.1.248.11.21.1.4.1.3, method: get}  # Integer32 (30..600), access=ru, range=30–600
  watchdog_remaining: {oid: 1.3.6.1.4.1.248.11.21.1.4.1.4, method: get}  # Integer32, access=r
  nvm: {oid: 1.3.6.1.4.1.248.11.21.1.3.1, method: get}  # INTEGER, access=r, allowed=['ok', 'outOfSync', 'busy']
  watchdog_enabled: {oid: 1.3.6.1.4.1.248.11.21.1.4.1.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  boot: {oid: 1.3.6.1.4.1.248.11.21.1.3.3, method: get}  # INTEGER, access=r, allowed=['ok', 'outOfSync']
}
```
</details>

### `get_watchdog_status()`

**Read** | **Protocols:** MOPS, SNMP

```
get_watchdog_status() -> {
    watchdog_enabled: False  // bool
    watchdog_interval: 0  // int
    watchdog_remaining: 0  // int
}
```


<details><summary>MOPS sources (3/3 attrs)</summary>

```
MOPS {
  watchdog_remaining: {HM2-FILEMGMT-MIB / hm2FileMgmtConfigWatchdogControl.hm2ConfigWatchdogTimerValue}  # Integer32, access=r
  watchdog_enabled: {HM2-FILEMGMT-MIB / hm2FileMgmtConfigWatchdogControl.hm2ConfigWatchdogAdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  watchdog_interval: {HM2-FILEMGMT-MIB / hm2FileMgmtConfigWatchdogControl.hm2ConfigWatchdogTimeInterval}  # Integer32 (30..600), access=ru, range=30–600
}
```
</details>

<details><summary>SNMP sources (3/3 attrs)</summary>

```
SNMP {
  watchdog_remaining: {oid: 1.3.6.1.4.1.248.11.21.1.4.1.4, method: get}  # Integer32, access=r
  watchdog_enabled: {oid: 1.3.6.1.4.1.248.11.21.1.4.1.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  watchdog_interval: {oid: 1.3.6.1.4.1.248.11.21.1.4.1.3, method: get}  # Integer32 (30..600), access=ru, range=30–600
}
```
</details>

### `set_watchdog()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (6/7 attrs)</summary>

```
MOPS {
  aca: {HM2-FILEMGMT-MIB / hm2FileMgmtStatusGroup.hm2FMEnvmState}  # INTEGER, access=r, allowed=['ok', 'outOfSync', 'absent']
  watchdog_interval: {HM2-FILEMGMT-MIB / hm2FileMgmtConfigWatchdogControl.hm2ConfigWatchdogTimeInterval}  # Integer32 (30..600), access=ru, range=30–600
  watchdog_remaining: {HM2-FILEMGMT-MIB / hm2FileMgmtConfigWatchdogControl.hm2ConfigWatchdogTimerValue}  # Integer32, access=r
  nvm: {HM2-FILEMGMT-MIB / hm2FileMgmtStatusGroup.hm2FMNvmState}  # INTEGER, access=r, allowed=['ok', 'outOfSync', 'busy']
  watchdog_enabled: {HM2-FILEMGMT-MIB / hm2FileMgmtConfigWatchdogControl.hm2ConfigWatchdogAdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  boot: {HM2-FILEMGMT-MIB / hm2FileMgmtStatusGroup.hm2FMBootParamState}  # INTEGER, access=r, allowed=['ok', 'outOfSync']
}
```
</details>

<details><summary>SNMP sources (6/7 attrs)</summary>

```
SNMP {
  aca: {oid: 1.3.6.1.4.1.248.11.21.1.3.2, method: get}  # INTEGER, access=r, allowed=['ok', 'outOfSync', 'absent']
  watchdog_interval: {oid: 1.3.6.1.4.1.248.11.21.1.4.1.3, method: get}  # Integer32 (30..600), access=ru, range=30–600
  watchdog_remaining: {oid: 1.3.6.1.4.1.248.11.21.1.4.1.4, method: get}  # Integer32, access=r
  nvm: {oid: 1.3.6.1.4.1.248.11.21.1.3.1, method: get}  # INTEGER, access=r, allowed=['ok', 'outOfSync', 'busy']
  watchdog_enabled: {oid: 1.3.6.1.4.1.248.11.21.1.4.1.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  boot: {oid: 1.3.6.1.4.1.248.11.21.1.3.3, method: get}  # INTEGER, access=r, allowed=['ok', 'outOfSync']
}
```
</details>

---

## dai_global

_Dynamic ARP Inspection global validation settings_

### `get_dai_global()`

**Read** | **Protocols:** MOPS, SNMP

```
get_dai_global() -> {
    validate_src_mac: False  // bool
    validate_dst_mac: False  // bool
    validate_ip: False  // bool
}
```


<details><summary>MOPS sources (3/3 attrs)</summary>

```
MOPS {
  validate_ip: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentDaiConfigGroup.hm2AgentDaiIPValidate}  # TruthValue, access=ru, allowed=[True, False]
  validate_src_mac: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentDaiConfigGroup.hm2AgentDaiSrcMacValidate}  # TruthValue, access=ru, allowed=[True, False]
  validate_dst_mac: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentDaiConfigGroup.hm2AgentDaiDstMacValidate}  # TruthValue, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (3/3 attrs)</summary>

```
SNMP {
  validate_ip: {oid: 1.3.6.1.4.1.248.12.1.2.8.21.3, method: get}  # TruthValue, access=ru, allowed=[True, False]
  validate_src_mac: {oid: 1.3.6.1.4.1.248.12.1.2.8.21.1, method: get}  # TruthValue, access=ru, allowed=[True, False]
  validate_dst_mac: {oid: 1.3.6.1.4.1.248.12.1.2.8.21.2, method: get}  # TruthValue, access=ru, allowed=[True, False]
}
```
</details>

### `set_dai_global()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (3/3 attrs)</summary>

```
MOPS {
  validate_ip: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentDaiConfigGroup.hm2AgentDaiIPValidate}  # TruthValue, access=ru, allowed=[True, False]
  validate_src_mac: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentDaiConfigGroup.hm2AgentDaiSrcMacValidate}  # TruthValue, access=ru, allowed=[True, False]
  validate_dst_mac: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentDaiConfigGroup.hm2AgentDaiDstMacValidate}  # TruthValue, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (3/3 attrs)</summary>

```
SNMP {
  validate_ip: {oid: 1.3.6.1.4.1.248.12.1.2.8.21.3, method: get}  # TruthValue, access=ru, allowed=[True, False]
  validate_src_mac: {oid: 1.3.6.1.4.1.248.12.1.2.8.21.1, method: get}  # TruthValue, access=ru, allowed=[True, False]
  validate_dst_mac: {oid: 1.3.6.1.4.1.248.12.1.2.8.21.2, method: get}  # TruthValue, access=ru, allowed=[True, False]
}
```
</details>

---

## devsec

_Device security monitoring — per-check enable/disable, status history, global state_

### `get_devsec()`

**Read** | **Protocols:** MOPS, SNMP

```
get_devsec() -> {
    state: "noerror"  // "noerror" | "error"
    trap_enabled: False  // bool
    monitors: {...}  // dict
    history: {...}  // dict
}
```

> Sub-table: **`monitors`** — key: `mon_http`

<details><summary>MOPS sources (21/21 attrs)</summary>

```
MOPS {
  mon_password_min_length: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSensePasswordMinLength}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_sysmon: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseSysmonEnabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_ext_nvm_config_load: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseExtNvmConfigLoadUnsecure}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_https_cert_warning: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseHttpsCertificateWarning}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_dev_mode: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseDevModeEnabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_ethernet_ip: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseEtherNetIpEnabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_snmp_unsecure: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseSnmpUnsecure}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_hidiscovery: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseHiDiscoveryEnabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_password_change: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSensePasswordChange}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_ext_nvm_update: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseExtNvmUpdateEnabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_pml_disabled: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSensePMLDisabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_no_link: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseNoLinkEnabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_password_policy: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSensePasswordStrengthNotConfigured}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_iec61850_mms: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseIec61850MmsEnabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_secure_boot: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseSecureBootDisabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_http: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseHttpEnabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  trap_enabled: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecTrapEnable}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_modbus_tcp: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseModbusTcpEnabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  state: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecOperState}  # INTEGER, access=r, allowed=['noerror', 'error']
  mon_telnet: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseTelnetEnabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_profinet_io: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseProfinetIOEnabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (21/21 attrs)</summary>

```
SNMP {
  mon_password_min_length: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.7, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_sysmon: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.13, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_ext_nvm_config_load: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.17, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_https_cert_warning: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.19, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_dev_mode: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.25, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_ethernet_ip: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.21, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_snmp_unsecure: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.12, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_hidiscovery: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.16, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_password_change: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.6, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_ext_nvm_update: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.14, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_pml_disabled: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.23, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_no_link: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.15, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_password_policy: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.8, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_iec61850_mms: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.18, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_secure_boot: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.24, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_http: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.11, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  trap_enabled: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_modbus_tcp: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.20, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  state: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.4, method: get}  # INTEGER, access=r, allowed=['noerror', 'error']
  mon_telnet: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.10, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_profinet_io: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.22, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

### `set_devsec()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (24/24 attrs)</summary>

```
MOPS {
  mon_password_min_length: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSensePasswordMinLength}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_sysmon: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseSysmonEnabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  history_timestamp: {HM2-DIAGNOSTIC-MIB / hm2DevSecStatusEntry.hm2DevSecStatusTimeStamp}  # HmTimeSeconds1970, access=r
  mon_ext_nvm_config_load: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseExtNvmConfigLoadUnsecure}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_https_cert_warning: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseHttpsCertificateWarning}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_dev_mode: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseDevModeEnabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_ethernet_ip: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseEtherNetIpEnabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_snmp_unsecure: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseSnmpUnsecure}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_hidiscovery: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseHiDiscoveryEnabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_password_change: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSensePasswordChange}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_ext_nvm_update: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseExtNvmUpdateEnabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_pml_disabled: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSensePMLDisabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_no_link: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseNoLinkEnabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_password_policy: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSensePasswordStrengthNotConfigured}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_iec61850_mms: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseIec61850MmsEnabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  history_cause: {HM2-DIAGNOSTIC-MIB / hm2DevSecStatusEntry.hm2DevSecStatusTrapCause}  # INTEGER, access=r, allowed=['none', 'password-change', 'password-min-length', 'password-policy-not-configured', 'password-policy-inactive', 'telnet-enabled', 'http-enabled', 'snmp-unsecure', 'sysmon-enabled', 'ext-nvm-update-enabled', 'no-link', 'hidisc-enabled', 'ext-nvm-config-load-unsecure', 'iec61850-mms-enabled', 'https-certificate-warning', 'modbus-tcp-enabled', 'ethernet-ip-enabled', 'profinet-io-enabled', 'pml-disabled', 'secure-boot-disabled', 'dev-mode-enabled']
  mon_secure_boot: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseSecureBootDisabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_http: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseHttpEnabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  trap_enabled: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecTrapEnable}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_modbus_tcp: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseModbusTcpEnabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  state: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecOperState}  # INTEGER, access=r, allowed=['noerror', 'error']
  history_index: {HM2-DIAGNOSTIC-MIB / hm2DevSecStatusEntry.hm2DevSecStatusIndex}  # Integer32, access=r
  mon_telnet: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseTelnetEnabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_profinet_io: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecSenseProfinetIOEnabled}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (24/24 attrs)</summary>

```
SNMP {
  mon_password_min_length: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.7, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_sysmon: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.13, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  history_timestamp: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.10.1.2}  # HmTimeSeconds1970, access=r
  mon_ext_nvm_config_load: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.17, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_https_cert_warning: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.19, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_dev_mode: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.25, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_ethernet_ip: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.21, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_snmp_unsecure: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.12, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_hidiscovery: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.16, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_password_change: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.6, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_ext_nvm_update: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.14, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_pml_disabled: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.23, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_no_link: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.15, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_password_policy: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.8, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_iec61850_mms: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.18, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  history_cause: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.10.1.3}  # INTEGER, access=r, allowed=['none', 'password-change', 'password-min-length', 'password-policy-not-configured', 'password-policy-inactive', 'telnet-enabled', 'http-enabled', 'snmp-unsecure', 'sysmon-enabled', 'ext-nvm-update-enabled', 'no-link', 'hidisc-enabled', 'ext-nvm-config-load-unsecure', 'iec61850-mms-enabled', 'https-certificate-warning', 'modbus-tcp-enabled', 'ethernet-ip-enabled', 'profinet-io-enabled', 'pml-disabled', 'secure-boot-disabled', 'dev-mode-enabled']
  mon_secure_boot: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.24, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_http: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.11, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  trap_enabled: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_modbus_tcp: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.20, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  state: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.4, method: get}  # INTEGER, access=r, allowed=['noerror', 'error']
  history_index: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.10.1.1}  # Integer32, access=r
  mon_telnet: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.10, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mon_profinet_io: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.22, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

### `get_devsec_history()`

**Read** | **Protocols:** MOPS, SNMP
Primary key: `history_index`

```
get_devsec_history() -> {
    cause: ""  // str
    timestamp: ""  // str
}
```


<details><summary>MOPS sources (1/1 attrs)</summary>

```
MOPS {
  history_index: {HM2-DIAGNOSTIC-MIB / hm2DevSecStatusEntry.hm2DevSecStatusIndex}  # Integer32, access=r
}
```
</details>

<details><summary>SNMP sources (1/1 attrs)</summary>

```
SNMP {
  history_index: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.10.1.1}  # Integer32, access=r
}
```
</details>

---

## dhcp_snooping

_DHCP Snooping global settings and port configuration_

### `get_dhcp_snooping()`

**Read** | **Protocols:** MOPS, SNMP

```
get_dhcp_snooping() -> {
    enabled: False  // bool
    verify_mac: False  // bool
    database_file: ""  // str
    ports: {...}  // dict
}
```


<details><summary>MOPS sources (3/3 attrs)</summary>

```
MOPS {
  verify_mac: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentDhcpSnoopingConfigGroup.hm2AgentDhcpSnoopingVerifyMac}  # TruthValue, access=ru, allowed=[True, False]
  database_file: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentDhcpSnoopingConfigGroup.hm2AgentDhcpSnoopingRemoteFileName}  # DisplayString, access=ru, range=0–255
  enabled: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentDhcpSnoopingConfigGroup.hm2AgentDhcpSnoopingAdminMode}  # TruthValue, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (3/3 attrs)</summary>

```
SNMP {
  verify_mac: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.2, method: get}  # TruthValue, access=ru, allowed=[True, False]
  database_file: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.12, method: get}  # DisplayString, access=ru, range=0–255
  enabled: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.1, method: get}  # TruthValue, access=ru, allowed=[True, False]
}
```
</details>

### `set_dhcp_snooping()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (4/4 attrs)</summary>

```
MOPS {
  verify_mac: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentDhcpSnoopingConfigGroup.hm2AgentDhcpSnoopingVerifyMac}  # TruthValue, access=ru, allowed=[True, False]
  port_trusted: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentDhcpSnoopingIfConfigEntry.hm2AgentDhcpSnoopingIfTrustEnable}  # TruthValue, access=ru, allowed=[True, False]
  database_file: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentDhcpSnoopingConfigGroup.hm2AgentDhcpSnoopingRemoteFileName}  # DisplayString, access=ru, range=0–255
  enabled: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentDhcpSnoopingConfigGroup.hm2AgentDhcpSnoopingAdminMode}  # TruthValue, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (4/4 attrs)</summary>

```
SNMP {
  verify_mac: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.2, method: get}  # TruthValue, access=ru, allowed=[True, False]
  port_trusted: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.4.1.1}  # TruthValue, access=ru, allowed=[True, False]
  database_file: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.12, method: get}  # DisplayString, access=ru, range=0–255
  enabled: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.1, method: get}  # TruthValue, access=ru, allowed=[True, False]
}
```
</details>

---

## dns

_DNS client configuration and server table_

### `get_dns()`

**Read** | **Protocols:** MOPS, SNMP, SSH

```
get_dns() -> {
    enabled: False  // bool
    config_source: "protocol"  // "user" | "mgmt-dhcp" | "provider"
    domain_name: ""  // str
    timeout: 3  // int
    retransmits: 2  // int
    cache_enabled: False  // bool
    servers: {...}  // dict
}
```

> Sub-table: **`servers`** — key: `address`

<details><summary>MOPS sources (9/9 attrs)</summary>

```
MOPS {
  enabled: {HM2-DNS-MIB / hm2DnsClientGroup.hm2DnsClientAdminState}  # HmEnabledStatus, access=ru, allowed=[True, False]
  config_source: {HM2-DNS-MIB / hm2DnsClientGroup.hm2DnsClientConfigSource}  # INTEGER, access=ru, allowed=['user', 'mgmt-dhcp', 'provider']
  retransmits: {HM2-DNS-MIB / hm2DnsClientGlobalGroup.hm2DnsClientRequestRetransmits}  # Integer32, access=ru, range=0–100
  servers: {HM2-DNS-MIB / hm2DnsClientServerCfgEntry.hm2DnsClientServerAddress}  # InetAddress, access=ru
  timeout: {HM2-DNS-MIB / hm2DnsClientGlobalGroup.hm2DnsClientRequestTimeout}  # Integer32, access=ru, range=0–3600
  addr_type: {HM2-DNS-MIB / hm2DnsClientServerCfgEntry.hm2DnsClientServerAddressType}  # InetAddressType, access=ru
  address: {HM2-DNS-MIB / hm2DnsClientServerCfgEntry.hm2DnsClientServerAddress}  # InetAddress, access=ru
  cache_enabled: {HM2-DNS-MIB / hm2DnsCacheGroup.hm2DnsCacheAdminState}  # HmEnabledStatus, access=ru, allowed=[True, False]
  domain_name: {HM2-DNS-MIB / hm2DnsClientGlobalGroup.hm2DnsClientDefaultDomainName}  # SnmpAdminString, access=ru, range=0–255
}
```
</details>

<details><summary>SNMP sources (9/9 attrs)</summary>

```
SNMP {
  enabled: {oid: 1.3.6.1.4.1.248.11.90.1.1.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  config_source: {oid: 1.3.6.1.4.1.248.11.90.1.1.2, method: get}  # INTEGER, access=ru, allowed=['user', 'mgmt-dhcp', 'provider']
  retransmits: {oid: 1.3.6.1.4.1.248.11.90.1.1.5.3, method: get}  # Integer32, access=ru, range=0–100
  servers: {oid: 1.3.6.1.4.1.248.11.90.1.1.3.1.3}  # InetAddress, access=ru
  timeout: {oid: 1.3.6.1.4.1.248.11.90.1.1.5.2, method: get}  # Integer32, access=ru, range=0–3600
  addr_type: {oid: 1.3.6.1.4.1.248.11.90.1.1.3.1.2}  # InetAddressType, access=ru
  address: {oid: 1.3.6.1.4.1.248.11.90.1.1.3.1.3}  # InetAddress, access=ru
  cache_enabled: {oid: 1.3.6.1.4.1.248.11.90.1.2.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  domain_name: {oid: 1.3.6.1.4.1.248.11.90.1.1.5.1, method: get}  # SnmpAdminString, access=ru, range=0–255
}
```
</details>

<details><summary>SSH sources (8/9 attrs)</summary>

```
SSH {
  enabled: {read: "show dns client info", write: "{'' if value else 'no '}dns client adminstate"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  config_source: {read: "show dns client info", write: "dns client source {value}"}  # INTEGER, access=ru, allowed=['user', 'mgmt-dhcp', 'provider']
  retransmits: {read: "show dns client info", write: "dns client retry {value}"}  # Integer32, access=ru, range=0–100
  servers: {read: "show dns client servers", write: "dns client servers add {index} ip {address}"}  # InetAddress, access=ru
  timeout: {read: "show dns client info", write: "dns client timeout {value}"}  # Integer32, access=ru, range=0–3600
  address: {read: "show dns client servers", write: "dns client servers add {index} ip {address}"}  # InetAddress, access=ru
  cache_enabled: {read: "show dns client info", write: "{'' if value else 'no '}dns client cache adminstate"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  domain_name: {read: "show dns client info", write: "dns client domain-name {value}"}  # SnmpAdminString, access=ru, range=0–255
}
```
</details>

### `set_dns()`

**Update** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (11/11 attrs)</summary>

```
MOPS {
  enabled: {HM2-DNS-MIB / hm2DnsClientGroup.hm2DnsClientAdminState}  # HmEnabledStatus, access=ru, allowed=[True, False]
  config_source: {HM2-DNS-MIB / hm2DnsClientGroup.hm2DnsClientConfigSource}  # INTEGER, access=ru, allowed=['user', 'mgmt-dhcp', 'provider']
  server_index: {HM2-DNS-MIB / hm2DnsClientServerCfgEntry.hm2DnsClientServerIndex}  # Integer32, access=r, range=1–4
  retransmits: {HM2-DNS-MIB / hm2DnsClientGlobalGroup.hm2DnsClientRequestRetransmits}  # Integer32, access=ru, range=0–100
  servers: {HM2-DNS-MIB / hm2DnsClientServerCfgEntry.hm2DnsClientServerAddress}  # InetAddress, access=ru
  timeout: {HM2-DNS-MIB / hm2DnsClientGlobalGroup.hm2DnsClientRequestTimeout}  # Integer32, access=ru, range=0–3600
  addr_type: {HM2-DNS-MIB / hm2DnsClientServerCfgEntry.hm2DnsClientServerAddressType}  # InetAddressType, access=ru
  address: {HM2-DNS-MIB / hm2DnsClientServerCfgEntry.hm2DnsClientServerAddress}  # InetAddress, access=ru
  cache_enabled: {HM2-DNS-MIB / hm2DnsCacheGroup.hm2DnsCacheAdminState}  # HmEnabledStatus, access=ru, allowed=[True, False]
  server_status: {HM2-DNS-MIB / hm2DnsClientServerCfgEntry.hm2DnsClientServerRowStatus}  # RowStatus, access=crud
  domain_name: {HM2-DNS-MIB / hm2DnsClientGlobalGroup.hm2DnsClientDefaultDomainName}  # SnmpAdminString, access=ru, range=0–255
}
```
</details>

<details><summary>SNMP sources (11/11 attrs)</summary>

```
SNMP {
  enabled: {oid: 1.3.6.1.4.1.248.11.90.1.1.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  config_source: {oid: 1.3.6.1.4.1.248.11.90.1.1.2, method: get}  # INTEGER, access=ru, allowed=['user', 'mgmt-dhcp', 'provider']
  server_index: {oid: 1.3.6.1.4.1.248.11.90.1.1.3.1.1}  # Integer32, access=r, range=1–4
  retransmits: {oid: 1.3.6.1.4.1.248.11.90.1.1.5.3, method: get}  # Integer32, access=ru, range=0–100
  servers: {oid: 1.3.6.1.4.1.248.11.90.1.1.3.1.3}  # InetAddress, access=ru
  timeout: {oid: 1.3.6.1.4.1.248.11.90.1.1.5.2, method: get}  # Integer32, access=ru, range=0–3600
  addr_type: {oid: 1.3.6.1.4.1.248.11.90.1.1.3.1.2}  # InetAddressType, access=ru
  address: {oid: 1.3.6.1.4.1.248.11.90.1.1.3.1.3}  # InetAddress, access=ru
  cache_enabled: {oid: 1.3.6.1.4.1.248.11.90.1.2.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  server_status: {oid: 1.3.6.1.4.1.248.11.90.1.1.3.1.4}  # RowStatus, access=crud
  domain_name: {oid: 1.3.6.1.4.1.248.11.90.1.1.5.1, method: get}  # SnmpAdminString, access=ru, range=0–255
}
```
</details>

<details><summary>SSH sources (9/11 attrs)</summary>

```
SSH {
  enabled: {read: "show dns client info", write: "{'' if value else 'no '}dns client adminstate"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  config_source: {read: "show dns client info", write: "dns client source {value}"}  # INTEGER, access=ru, allowed=['user', 'mgmt-dhcp', 'provider']
  retransmits: {read: "show dns client info", write: "dns client retry {value}"}  # Integer32, access=ru, range=0–100
  servers: {read: "show dns client servers", write: "dns client servers add {index} ip {address}"}  # InetAddress, access=ru
  timeout: {read: "show dns client info", write: "dns client timeout {value}"}  # Integer32, access=ru, range=0–3600
  address: {read: "show dns client servers", write: "dns client servers add {index} ip {address}"}  # InetAddress, access=ru
  cache_enabled: {read: "show dns client info", write: "{'' if value else 'no '}dns client cache adminstate"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  server_status: {write: "dns client servers add {index} ip {address}"}  # RowStatus, access=crud
  domain_name: {read: "show dns client info", write: "dns client domain-name {value}"}  # SnmpAdminString, access=ru, range=0–255
}
```
</details>

### `create_dns_server()`

**Create** | **Protocols:** MOPS, SNMP, SSH
Required: `address`

```
create_dns_server() -> {
    addr_type: 1  // int
}
```


<details><summary>MOPS sources (2/2 attrs)</summary>

```
MOPS {
  address: {HM2-DNS-MIB / hm2DnsClientServerCfgEntry.hm2DnsClientServerAddress}  # InetAddress, access=ru
  addr_type: {HM2-DNS-MIB / hm2DnsClientServerCfgEntry.hm2DnsClientServerAddressType}  # InetAddressType, access=ru
}
```
</details>

<details><summary>SNMP sources (2/2 attrs)</summary>

```
SNMP {
  address: {oid: 1.3.6.1.4.1.248.11.90.1.1.3.1.3}  # InetAddress, access=ru
  addr_type: {oid: 1.3.6.1.4.1.248.11.90.1.1.3.1.2}  # InetAddressType, access=ru
}
```
</details>

<details><summary>SSH sources (1/2 attrs)</summary>

```
SSH {
  address: {read: "show dns client servers", write: "dns client servers add {index} ip {address}"}  # InetAddress, access=ru
}
```
</details>

### `delete_dns_server()`

**Delete** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (11/11 attrs)</summary>

```
MOPS {
  enabled: {HM2-DNS-MIB / hm2DnsClientGroup.hm2DnsClientAdminState}  # HmEnabledStatus, access=ru, allowed=[True, False]
  config_source: {HM2-DNS-MIB / hm2DnsClientGroup.hm2DnsClientConfigSource}  # INTEGER, access=ru, allowed=['user', 'mgmt-dhcp', 'provider']
  server_index: {HM2-DNS-MIB / hm2DnsClientServerCfgEntry.hm2DnsClientServerIndex}  # Integer32, access=r, range=1–4
  retransmits: {HM2-DNS-MIB / hm2DnsClientGlobalGroup.hm2DnsClientRequestRetransmits}  # Integer32, access=ru, range=0–100
  servers: {HM2-DNS-MIB / hm2DnsClientServerCfgEntry.hm2DnsClientServerAddress}  # InetAddress, access=ru
  timeout: {HM2-DNS-MIB / hm2DnsClientGlobalGroup.hm2DnsClientRequestTimeout}  # Integer32, access=ru, range=0–3600
  addr_type: {HM2-DNS-MIB / hm2DnsClientServerCfgEntry.hm2DnsClientServerAddressType}  # InetAddressType, access=ru
  address: {HM2-DNS-MIB / hm2DnsClientServerCfgEntry.hm2DnsClientServerAddress}  # InetAddress, access=ru
  cache_enabled: {HM2-DNS-MIB / hm2DnsCacheGroup.hm2DnsCacheAdminState}  # HmEnabledStatus, access=ru, allowed=[True, False]
  server_status: {HM2-DNS-MIB / hm2DnsClientServerCfgEntry.hm2DnsClientServerRowStatus}  # RowStatus, access=crud
  domain_name: {HM2-DNS-MIB / hm2DnsClientGlobalGroup.hm2DnsClientDefaultDomainName}  # SnmpAdminString, access=ru, range=0–255
}
```
</details>

<details><summary>SNMP sources (11/11 attrs)</summary>

```
SNMP {
  enabled: {oid: 1.3.6.1.4.1.248.11.90.1.1.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  config_source: {oid: 1.3.6.1.4.1.248.11.90.1.1.2, method: get}  # INTEGER, access=ru, allowed=['user', 'mgmt-dhcp', 'provider']
  server_index: {oid: 1.3.6.1.4.1.248.11.90.1.1.3.1.1}  # Integer32, access=r, range=1–4
  retransmits: {oid: 1.3.6.1.4.1.248.11.90.1.1.5.3, method: get}  # Integer32, access=ru, range=0–100
  servers: {oid: 1.3.6.1.4.1.248.11.90.1.1.3.1.3}  # InetAddress, access=ru
  timeout: {oid: 1.3.6.1.4.1.248.11.90.1.1.5.2, method: get}  # Integer32, access=ru, range=0–3600
  addr_type: {oid: 1.3.6.1.4.1.248.11.90.1.1.3.1.2}  # InetAddressType, access=ru
  address: {oid: 1.3.6.1.4.1.248.11.90.1.1.3.1.3}  # InetAddress, access=ru
  cache_enabled: {oid: 1.3.6.1.4.1.248.11.90.1.2.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  server_status: {oid: 1.3.6.1.4.1.248.11.90.1.1.3.1.4}  # RowStatus, access=crud
  domain_name: {oid: 1.3.6.1.4.1.248.11.90.1.1.5.1, method: get}  # SnmpAdminString, access=ru, range=0–255
}
```
</details>

<details><summary>SSH sources (9/11 attrs)</summary>

```
SSH {
  enabled: {read: "show dns client info", write: "{'' if value else 'no '}dns client adminstate"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  config_source: {read: "show dns client info", write: "dns client source {value}"}  # INTEGER, access=ru, allowed=['user', 'mgmt-dhcp', 'provider']
  retransmits: {read: "show dns client info", write: "dns client retry {value}"}  # Integer32, access=ru, range=0–100
  servers: {read: "show dns client servers", write: "dns client servers add {index} ip {address}"}  # InetAddress, access=ru
  timeout: {read: "show dns client info", write: "dns client timeout {value}"}  # Integer32, access=ru, range=0–3600
  address: {read: "show dns client servers", write: "dns client servers add {index} ip {address}"}  # InetAddress, access=ru
  cache_enabled: {read: "show dns client info", write: "{'' if value else 'no '}dns client cache adminstate"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  server_status: {write: "dns client servers add {index} ip {address}"}  # RowStatus, access=crud
  domain_name: {read: "show dns client info", write: "dns client domain-name {value}"}  # SnmpAdminString, access=ru, range=0–255
}
```
</details>

---

## gmrp

_GMRP (GARP Multicast Registration Protocol) configuration_

### `get_gmrp()`

**Read** | **Protocols:** MOPS, SNMP

```
get_gmrp() -> {
    enabled: False  // bool
    unknown_multicast: "flood"  // "flood" | "discard"
    ports: {...}  // dict
}
```

> Sub-table: **`ports`** — key: `port_enabled`, map: `bridge_port`

<details><summary>MOPS sources (3/3 attrs)</summary>

```
MOPS {
  unknown_multicast: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentSwitchGARPGroup.hm2AgentSwitchGmrpUnknownMulticastFilterMode}  # INTEGER, access=ru, allowed=['flood', 'discard']
  port_enabled: {P-BRIDGE-MIB / dot1dPortGmrpEntry.dot1dPortGmrpStatus}  # EnabledStatus, access=ru
  enabled: {P-BRIDGE-MIB / dot1dExtBase.dot1dGmrpStatus}  # EnabledStatus, access=ru
}
```
</details>

<details><summary>SNMP sources (3/3 attrs)</summary>

```
SNMP {
  unknown_multicast: {oid: 1.3.6.1.4.1.248.12.1.2.8.249.1, method: get}  # INTEGER, access=ru, allowed=['flood', 'discard']
  port_enabled: {oid: 1.3.6.1.2.1.17.6.1.4.1.1.1}  # EnabledStatus, access=ru
  enabled: {oid: 1.3.6.1.2.1.17.6.1.1.3, method: get}  # EnabledStatus, access=ru
}
```
</details>

### `set_gmrp()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (3/3 attrs)</summary>

```
MOPS {
  unknown_multicast: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentSwitchGARPGroup.hm2AgentSwitchGmrpUnknownMulticastFilterMode}  # INTEGER, access=ru, allowed=['flood', 'discard']
  port_enabled: {P-BRIDGE-MIB / dot1dPortGmrpEntry.dot1dPortGmrpStatus}  # EnabledStatus, access=ru
  enabled: {P-BRIDGE-MIB / dot1dExtBase.dot1dGmrpStatus}  # EnabledStatus, access=ru
}
```
</details>

<details><summary>SNMP sources (3/3 attrs)</summary>

```
SNMP {
  unknown_multicast: {oid: 1.3.6.1.4.1.248.12.1.2.8.249.1, method: get}  # INTEGER, access=ru, allowed=['flood', 'discard']
  port_enabled: {oid: 1.3.6.1.2.1.17.6.1.4.1.1.1}  # EnabledStatus, access=ru
  enabled: {oid: 1.3.6.1.2.1.17.6.1.1.3, method: get}  # EnabledStatus, access=ru
}
```
</details>

### `set_gmrp_port()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (3/3 attrs)</summary>

```
MOPS {
  unknown_multicast: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentSwitchGARPGroup.hm2AgentSwitchGmrpUnknownMulticastFilterMode}  # INTEGER, access=ru, allowed=['flood', 'discard']
  port_enabled: {P-BRIDGE-MIB / dot1dPortGmrpEntry.dot1dPortGmrpStatus}  # EnabledStatus, access=ru
  enabled: {P-BRIDGE-MIB / dot1dExtBase.dot1dGmrpStatus}  # EnabledStatus, access=ru
}
```
</details>

<details><summary>SNMP sources (3/3 attrs)</summary>

```
SNMP {
  unknown_multicast: {oid: 1.3.6.1.4.1.248.12.1.2.8.249.1, method: get}  # INTEGER, access=ru, allowed=['flood', 'discard']
  port_enabled: {oid: 1.3.6.1.2.1.17.6.1.4.1.1.1}  # EnabledStatus, access=ru
  enabled: {oid: 1.3.6.1.2.1.17.6.1.1.3, method: get}  # EnabledStatus, access=ru
}
```
</details>

---

## gvrp

_GVRP (GARP VLAN Registration Protocol) configuration_

### `get_gvrp()`

**Read** | **Protocols:** MOPS, SNMP

```
get_gvrp() -> {
    enabled: False  // bool
    ports: {...}  // dict
}
```

> Sub-table: **`ports`** — key: `port_enabled`, map: `bridge_port`

<details><summary>MOPS sources (2/2 attrs)</summary>

```
MOPS {
  port_enabled: {Q-BRIDGE-MIB / dot1qPortVlanEntry.dot1qPortGvrpStatus}  # EnabledStatus, access=ru
  enabled: {Q-BRIDGE-MIB / dot1qBase.dot1qGvrpStatus}  # EnabledStatus, access=ru
}
```
</details>

<details><summary>SNMP sources (2/2 attrs)</summary>

```
SNMP {
  port_enabled: {oid: 1.3.6.1.2.1.17.7.1.4.5.1.4}  # EnabledStatus, access=ru
  enabled: {oid: 1.3.6.1.2.1.17.7.1.1.5, method: get}  # EnabledStatus, access=ru
}
```
</details>

### `set_gvrp()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (2/2 attrs)</summary>

```
MOPS {
  port_enabled: {Q-BRIDGE-MIB / dot1qPortVlanEntry.dot1qPortGvrpStatus}  # EnabledStatus, access=ru
  enabled: {Q-BRIDGE-MIB / dot1qBase.dot1qGvrpStatus}  # EnabledStatus, access=ru
}
```
</details>

<details><summary>SNMP sources (2/2 attrs)</summary>

```
SNMP {
  port_enabled: {oid: 1.3.6.1.2.1.17.7.1.4.5.1.4}  # EnabledStatus, access=ru
  enabled: {oid: 1.3.6.1.2.1.17.7.1.1.5, method: get}  # EnabledStatus, access=ru
}
```
</details>

### `set_gvrp_port()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (2/2 attrs)</summary>

```
MOPS {
  port_enabled: {Q-BRIDGE-MIB / dot1qPortVlanEntry.dot1qPortGvrpStatus}  # EnabledStatus, access=ru
  enabled: {Q-BRIDGE-MIB / dot1qBase.dot1qGvrpStatus}  # EnabledStatus, access=ru
}
```
</details>

<details><summary>SNMP sources (2/2 attrs)</summary>

```
SNMP {
  port_enabled: {oid: 1.3.6.1.2.1.17.7.1.4.5.1.4}  # EnabledStatus, access=ru
  enabled: {oid: 1.3.6.1.2.1.17.7.1.1.5, method: get}  # EnabledStatus, access=ru
}
```
</details>

---

## hidiscovery

_HiDiscovery protocol settings_

### `get_hidiscovery()`

**Read** | **Protocols:** MOPS, SNMP

```
get_hidiscovery() -> {
    enabled: False  // bool
    mode: "readOnly"  // "readWrite" | "readOnly"
    relay_enabled: False  // bool
    blinking: False  // bool
}
```


<details><summary>MOPS sources (4/4 attrs)</summary>

```
MOPS {
  mode: {HM2-NETCONFIG-MIB / hm2NetHiDiscoveryGroup.hm2NetHiDiscoveryMode}  # INTEGER, access=ru, allowed=['readWrite', 'readOnly']
  enabled: {HM2-NETCONFIG-MIB / hm2NetHiDiscoveryGroup.hm2NetHiDiscoveryOperation}  # HmEnabledStatus, access=ru, allowed=[True, False]
  relay_enabled: {HM2-NETCONFIG-MIB / hm2NetHiDiscoveryGroup.hm2NetHiDiscoveryRelay}  # HmEnabledStatus, access=ru, allowed=[True, False]
  blinking: {HM2-NETCONFIG-MIB / hm2NetHiDiscoveryGroup.hm2NetHiDiscoveryBlinking}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (4/4 attrs)</summary>

```
SNMP {
  mode: {oid: 1.3.6.1.4.1.248.11.20.1.4.2, method: get}  # INTEGER, access=ru, allowed=['readWrite', 'readOnly']
  enabled: {oid: 1.3.6.1.4.1.248.11.20.1.4.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  relay_enabled: {oid: 1.3.6.1.4.1.248.11.20.1.4.5, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  blinking: {oid: 1.3.6.1.4.1.248.11.20.1.4.3, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

### `set_hidiscovery()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (4/4 attrs)</summary>

```
MOPS {
  mode: {HM2-NETCONFIG-MIB / hm2NetHiDiscoveryGroup.hm2NetHiDiscoveryMode}  # INTEGER, access=ru, allowed=['readWrite', 'readOnly']
  enabled: {HM2-NETCONFIG-MIB / hm2NetHiDiscoveryGroup.hm2NetHiDiscoveryOperation}  # HmEnabledStatus, access=ru, allowed=[True, False]
  relay_enabled: {HM2-NETCONFIG-MIB / hm2NetHiDiscoveryGroup.hm2NetHiDiscoveryRelay}  # HmEnabledStatus, access=ru, allowed=[True, False]
  blinking: {HM2-NETCONFIG-MIB / hm2NetHiDiscoveryGroup.hm2NetHiDiscoveryBlinking}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (4/4 attrs)</summary>

```
SNMP {
  mode: {oid: 1.3.6.1.4.1.248.11.20.1.4.2, method: get}  # INTEGER, access=ru, allowed=['readWrite', 'readOnly']
  enabled: {oid: 1.3.6.1.4.1.248.11.20.1.4.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  relay_enabled: {oid: 1.3.6.1.4.1.248.11.20.1.4.5, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  blinking: {oid: 1.3.6.1.4.1.248.11.20.1.4.3, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

---

## interface

_Physical and logical interface configuration and status_

### `get_interfaces()`

**Read** | **Protocols:** MOPS, SNMP
Primary key: `name` | Key map: `ifindex`

```
get_interfaces() -> {
    oper_status: "down"  // "up" | "down" | "testing" | "unknown" | "dormant" | "not_present" | "lower_layer_down"
    admin_status: "disabled"  // "enabled" | "disabled"
    alias: ""  // str
    speed: 0  // int
    mtu: 1500  // int
    phys_address: ""  // str
}
```


<details><summary>MOPS sources (7/7 attrs)</summary>

```
MOPS {
  phys_address: {IF-MIB / ifEntry.ifPhysAddress}  # PhysAddress, access=r
  admin_status: {IF-MIB / ifEntry.ifAdminStatus}  # INTEGER, access=ru, allowed=['up', 'down', 'testing']
  speed: {IF-MIB / ifXEntry.ifHighSpeed}  # Gauge32, access=r
  oper_status: {IF-MIB / ifEntry.ifOperStatus}  # INTEGER, access=r, allowed=['up', 'down', 'testing', 'unknown', 'dormant', 'notPresent', 'lowerLayerDown']
  mtu: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentPortConfigEntry.hm2AgentPortMaxFrameSize}  # Integer32, access=ru
  alias: {IF-MIB / ifXEntry.ifAlias}  # DisplayString, access=ru, range=0–64
  name: {IF-MIB / ifXEntry.ifName}  # DisplayString, access=r
}
```
</details>

<details><summary>SNMP sources (7/7 attrs)</summary>

```
SNMP {
  phys_address: {oid: 1.3.6.1.2.1.2.2.1.6}  # PhysAddress, access=r
  admin_status: {oid: 1.3.6.1.2.1.2.2.1.7}  # INTEGER, access=ru, allowed=['up', 'down', 'testing']
  speed: {oid: 1.3.6.1.2.1.31.1.1.1.15}  # Gauge32, access=r
  oper_status: {oid: 1.3.6.1.2.1.2.2.1.8}  # INTEGER, access=r, allowed=['up', 'down', 'testing', 'unknown', 'dormant', 'notPresent', 'lowerLayerDown']
  mtu: {oid: 1.3.6.1.4.1.248.12.1.2.13.1.19}  # Integer32, access=ru
  alias: {oid: 1.3.6.1.2.1.31.1.1.1.18}  # DisplayString, access=ru, range=0–64
  name: {oid: 1.3.6.1.2.1.31.1.1.1.1}  # DisplayString, access=r
}
```
</details>

### `get_interfaces_counters()`

**Read** | **Protocols:** MOPS, SNMP
Primary key: `name`

```
get_interfaces_counters() -> {
    tx_errors: 0  // int
    rx_errors: 0  // int
    tx_discards: 0  // int
    rx_discards: 0  // int
    tx_octets: 0  // int
    rx_octets: 0  // int
    tx_unicast_packets: 0  // int
    rx_unicast_packets: 0  // int
    tx_multicast_packets: 0  // int
    rx_multicast_packets: 0  // int
    tx_broadcast_packets: 0  // int
    rx_broadcast_packets: 0  // int
}
```


<details><summary>MOPS sources (13/13 attrs)</summary>

```
MOPS {
  rx_broadcast_packets: {IF-MIB / ifXEntry.ifHCInBroadcastPkts}  # Counter64, access=r
  tx_discards: {IF-MIB / ifEntry.ifOutDiscards}  # Counter32, access=r
  rx_unicast_packets: {IF-MIB / ifXEntry.ifHCInUcastPkts}  # Counter64, access=r
  tx_unicast_packets: {IF-MIB / ifXEntry.ifHCOutUcastPkts}  # Counter64, access=r
  tx_broadcast_packets: {IF-MIB / ifXEntry.ifHCOutBroadcastPkts}  # Counter64, access=r
  rx_errors: {IF-MIB / ifEntry.ifInErrors}  # Counter32, access=r
  rx_discards: {IF-MIB / ifEntry.ifInDiscards}  # Counter32, access=r
  rx_octets: {IF-MIB / ifEntry.ifInOctets}  # Counter32, access=r
  tx_multicast_packets: {IF-MIB / ifXEntry.ifHCOutMulticastPkts}  # Counter64, access=r
  rx_multicast_packets: {IF-MIB / ifXEntry.ifHCInMulticastPkts}  # Counter64, access=r
  tx_errors: {IF-MIB / ifEntry.ifOutErrors}  # Counter32, access=r
  name: {IF-MIB / ifXEntry.ifName}  # DisplayString, access=r
  tx_octets: {IF-MIB / ifEntry.ifOutOctets}  # Counter32, access=r
}
```
</details>

<details><summary>SNMP sources (13/13 attrs)</summary>

```
SNMP {
  rx_broadcast_packets: {oid: 1.3.6.1.2.1.31.1.1.1.9}  # Counter64, access=r
  tx_discards: {oid: 1.3.6.1.2.1.2.2.1.19}  # Counter32, access=r
  rx_unicast_packets: {oid: 1.3.6.1.2.1.31.1.1.1.7}  # Counter64, access=r
  tx_unicast_packets: {oid: 1.3.6.1.2.1.31.1.1.1.11}  # Counter64, access=r
  tx_broadcast_packets: {oid: 1.3.6.1.2.1.31.1.1.1.13}  # Counter64, access=r
  rx_errors: {oid: 1.3.6.1.2.1.2.2.1.14}  # Counter32, access=r
  rx_discards: {oid: 1.3.6.1.2.1.2.2.1.13}  # Counter32, access=r
  rx_octets: {oid: 1.3.6.1.2.1.2.2.1.10}  # Counter32, access=r
  tx_multicast_packets: {oid: 1.3.6.1.2.1.31.1.1.1.12}  # Counter64, access=r
  rx_multicast_packets: {oid: 1.3.6.1.2.1.31.1.1.1.8}  # Counter64, access=r
  tx_errors: {oid: 1.3.6.1.2.1.2.2.1.20}  # Counter32, access=r
  name: {oid: 1.3.6.1.2.1.31.1.1.1.1}  # DisplayString, access=r
  tx_octets: {oid: 1.3.6.1.2.1.2.2.1.16}  # Counter32, access=r
}
```
</details>

### `get_ip_addresses()`

**Read** | **Protocols:** None

```
get_ip_addresses() -> {
    ipv4: {...}  // dict
}
```


### `get_interfaces_ip()`

**Read** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (22/22 attrs)</summary>

```
MOPS {
  ipv4_address: {HM2-NETCONFIG-MIB / hm2NetStaticGroup.hm2NetLocalIPAddr}  # InetAddress, access=ru
  tx_broadcast_packets: {IF-MIB / ifXEntry.ifHCOutBroadcastPkts}  # Counter64, access=r
  rx_errors: {IF-MIB / ifEntry.ifInErrors}  # Counter32, access=r
  tx_discards: {IF-MIB / ifEntry.ifOutDiscards}  # Counter32, access=r
  rx_unicast_packets: {IF-MIB / ifXEntry.ifHCInUcastPkts}  # Counter64, access=r
  ipv4_prefix: {HM2-NETCONFIG-MIB / hm2NetStaticGroup.hm2NetPrefixLength}  # InetAddressPrefixLength, access=ru
  speed: {IF-MIB / ifXEntry.ifHighSpeed}  # Gauge32, access=r
  rx_octets: {IF-MIB / ifEntry.ifInOctets}  # Counter32, access=r
  rx_discards: {IF-MIB / ifEntry.ifInDiscards}  # Counter32, access=r
  ipv4_gateway: {HM2-NETCONFIG-MIB / hm2NetStaticGroup.hm2NetGatewayIPAddr}  # InetAddress, access=ru
  oper_status: {IF-MIB / ifEntry.ifOperStatus}  # INTEGER, access=r, allowed=['up', 'down', 'testing', 'unknown', 'dormant', 'notPresent', 'lowerLayerDown']
  tx_errors: {IF-MIB / ifEntry.ifOutErrors}  # Counter32, access=r
  tx_octets: {IF-MIB / ifEntry.ifOutOctets}  # Counter32, access=r
  rx_broadcast_packets: {IF-MIB / ifXEntry.ifHCInBroadcastPkts}  # Counter64, access=r
  tx_unicast_packets: {IF-MIB / ifXEntry.ifHCOutUcastPkts}  # Counter64, access=r
  admin_status: {IF-MIB / ifEntry.ifAdminStatus}  # INTEGER, access=ru, allowed=['up', 'down', 'testing']
  tx_multicast_packets: {IF-MIB / ifXEntry.ifHCOutMulticastPkts}  # Counter64, access=r
  rx_multicast_packets: {IF-MIB / ifXEntry.ifHCInMulticastPkts}  # Counter64, access=r
  mtu: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentPortConfigEntry.hm2AgentPortMaxFrameSize}  # Integer32, access=ru
  phys_address: {IF-MIB / ifEntry.ifPhysAddress}  # PhysAddress, access=r
  name: {IF-MIB / ifXEntry.ifName}  # DisplayString, access=r
  alias: {IF-MIB / ifXEntry.ifAlias}  # DisplayString, access=ru, range=0–64
}
```
</details>

<details><summary>SNMP sources (22/22 attrs)</summary>

```
SNMP {
  ipv4_address: {oid: 1.3.6.1.4.1.248.11.20.1.1.3, method: get}  # InetAddress, access=ru
  tx_broadcast_packets: {oid: 1.3.6.1.2.1.31.1.1.1.13}  # Counter64, access=r
  rx_errors: {oid: 1.3.6.1.2.1.2.2.1.14}  # Counter32, access=r
  tx_discards: {oid: 1.3.6.1.2.1.2.2.1.19}  # Counter32, access=r
  rx_unicast_packets: {oid: 1.3.6.1.2.1.31.1.1.1.7}  # Counter64, access=r
  ipv4_prefix: {oid: 1.3.6.1.4.1.248.11.20.1.1.4, method: get}  # InetAddressPrefixLength, access=ru
  speed: {oid: 1.3.6.1.2.1.31.1.1.1.15}  # Gauge32, access=r
  rx_octets: {oid: 1.3.6.1.2.1.2.2.1.10}  # Counter32, access=r
  rx_discards: {oid: 1.3.6.1.2.1.2.2.1.13}  # Counter32, access=r
  ipv4_gateway: {oid: 1.3.6.1.4.1.248.11.20.1.1.6, method: get}  # InetAddress, access=ru
  oper_status: {oid: 1.3.6.1.2.1.2.2.1.8}  # INTEGER, access=r, allowed=['up', 'down', 'testing', 'unknown', 'dormant', 'notPresent', 'lowerLayerDown']
  tx_errors: {oid: 1.3.6.1.2.1.2.2.1.20}  # Counter32, access=r
  tx_octets: {oid: 1.3.6.1.2.1.2.2.1.16}  # Counter32, access=r
  rx_broadcast_packets: {oid: 1.3.6.1.2.1.31.1.1.1.9}  # Counter64, access=r
  tx_unicast_packets: {oid: 1.3.6.1.2.1.31.1.1.1.11}  # Counter64, access=r
  admin_status: {oid: 1.3.6.1.2.1.2.2.1.7}  # INTEGER, access=ru, allowed=['up', 'down', 'testing']
  tx_multicast_packets: {oid: 1.3.6.1.2.1.31.1.1.1.12}  # Counter64, access=r
  rx_multicast_packets: {oid: 1.3.6.1.2.1.31.1.1.1.8}  # Counter64, access=r
  mtu: {oid: 1.3.6.1.4.1.248.12.1.2.13.1.19}  # Integer32, access=ru
  phys_address: {oid: 1.3.6.1.2.1.2.2.1.6}  # PhysAddress, access=r
  name: {oid: 1.3.6.1.2.1.31.1.1.1.1}  # DisplayString, access=r
  alias: {oid: 1.3.6.1.2.1.31.1.1.1.18}  # DisplayString, access=ru, range=0–64
}
```
</details>

### `set_interface()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (22/22 attrs)</summary>

```
MOPS {
  ipv4_address: {HM2-NETCONFIG-MIB / hm2NetStaticGroup.hm2NetLocalIPAddr}  # InetAddress, access=ru
  tx_broadcast_packets: {IF-MIB / ifXEntry.ifHCOutBroadcastPkts}  # Counter64, access=r
  rx_errors: {IF-MIB / ifEntry.ifInErrors}  # Counter32, access=r
  tx_discards: {IF-MIB / ifEntry.ifOutDiscards}  # Counter32, access=r
  rx_unicast_packets: {IF-MIB / ifXEntry.ifHCInUcastPkts}  # Counter64, access=r
  ipv4_prefix: {HM2-NETCONFIG-MIB / hm2NetStaticGroup.hm2NetPrefixLength}  # InetAddressPrefixLength, access=ru
  speed: {IF-MIB / ifXEntry.ifHighSpeed}  # Gauge32, access=r
  rx_octets: {IF-MIB / ifEntry.ifInOctets}  # Counter32, access=r
  rx_discards: {IF-MIB / ifEntry.ifInDiscards}  # Counter32, access=r
  ipv4_gateway: {HM2-NETCONFIG-MIB / hm2NetStaticGroup.hm2NetGatewayIPAddr}  # InetAddress, access=ru
  oper_status: {IF-MIB / ifEntry.ifOperStatus}  # INTEGER, access=r, allowed=['up', 'down', 'testing', 'unknown', 'dormant', 'notPresent', 'lowerLayerDown']
  tx_errors: {IF-MIB / ifEntry.ifOutErrors}  # Counter32, access=r
  tx_octets: {IF-MIB / ifEntry.ifOutOctets}  # Counter32, access=r
  rx_broadcast_packets: {IF-MIB / ifXEntry.ifHCInBroadcastPkts}  # Counter64, access=r
  tx_unicast_packets: {IF-MIB / ifXEntry.ifHCOutUcastPkts}  # Counter64, access=r
  admin_status: {IF-MIB / ifEntry.ifAdminStatus}  # INTEGER, access=ru, allowed=['up', 'down', 'testing']
  tx_multicast_packets: {IF-MIB / ifXEntry.ifHCOutMulticastPkts}  # Counter64, access=r
  rx_multicast_packets: {IF-MIB / ifXEntry.ifHCInMulticastPkts}  # Counter64, access=r
  mtu: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentPortConfigEntry.hm2AgentPortMaxFrameSize}  # Integer32, access=ru
  phys_address: {IF-MIB / ifEntry.ifPhysAddress}  # PhysAddress, access=r
  name: {IF-MIB / ifXEntry.ifName}  # DisplayString, access=r
  alias: {IF-MIB / ifXEntry.ifAlias}  # DisplayString, access=ru, range=0–64
}
```
</details>

<details><summary>SNMP sources (22/22 attrs)</summary>

```
SNMP {
  ipv4_address: {oid: 1.3.6.1.4.1.248.11.20.1.1.3, method: get}  # InetAddress, access=ru
  tx_broadcast_packets: {oid: 1.3.6.1.2.1.31.1.1.1.13}  # Counter64, access=r
  rx_errors: {oid: 1.3.6.1.2.1.2.2.1.14}  # Counter32, access=r
  tx_discards: {oid: 1.3.6.1.2.1.2.2.1.19}  # Counter32, access=r
  rx_unicast_packets: {oid: 1.3.6.1.2.1.31.1.1.1.7}  # Counter64, access=r
  ipv4_prefix: {oid: 1.3.6.1.4.1.248.11.20.1.1.4, method: get}  # InetAddressPrefixLength, access=ru
  speed: {oid: 1.3.6.1.2.1.31.1.1.1.15}  # Gauge32, access=r
  rx_octets: {oid: 1.3.6.1.2.1.2.2.1.10}  # Counter32, access=r
  rx_discards: {oid: 1.3.6.1.2.1.2.2.1.13}  # Counter32, access=r
  ipv4_gateway: {oid: 1.3.6.1.4.1.248.11.20.1.1.6, method: get}  # InetAddress, access=ru
  oper_status: {oid: 1.3.6.1.2.1.2.2.1.8}  # INTEGER, access=r, allowed=['up', 'down', 'testing', 'unknown', 'dormant', 'notPresent', 'lowerLayerDown']
  tx_errors: {oid: 1.3.6.1.2.1.2.2.1.20}  # Counter32, access=r
  tx_octets: {oid: 1.3.6.1.2.1.2.2.1.16}  # Counter32, access=r
  rx_broadcast_packets: {oid: 1.3.6.1.2.1.31.1.1.1.9}  # Counter64, access=r
  tx_unicast_packets: {oid: 1.3.6.1.2.1.31.1.1.1.11}  # Counter64, access=r
  admin_status: {oid: 1.3.6.1.2.1.2.2.1.7}  # INTEGER, access=ru, allowed=['up', 'down', 'testing']
  tx_multicast_packets: {oid: 1.3.6.1.2.1.31.1.1.1.12}  # Counter64, access=r
  rx_multicast_packets: {oid: 1.3.6.1.2.1.31.1.1.1.8}  # Counter64, access=r
  mtu: {oid: 1.3.6.1.4.1.248.12.1.2.13.1.19}  # Integer32, access=ru
  phys_address: {oid: 1.3.6.1.2.1.2.2.1.6}  # PhysAddress, access=r
  name: {oid: 1.3.6.1.2.1.31.1.1.1.1}  # DisplayString, access=r
  alias: {oid: 1.3.6.1.2.1.31.1.1.1.18}  # DisplayString, access=ru, range=0–64
}
```
</details>

---

## ip_restrict

_IP restriction rules for management access_

### `get_ip_restrict()`

**Read** | **Protocols:** MOPS, SNMP, SSH

```
get_ip_restrict() -> {
    enabled: False  // bool
    logging: False  // bool
    rules: {...}  // dict
}
```

> Sub-table: **`rules`** — key: `index`

<details><summary>MOPS sources (15/15 attrs)</summary>

```
MOPS {
  http: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvHttp}  # HmEnabledStatus, access=ru, allowed=[True, False]
  enabled: {HM2-MGMTACCESS-MIB / hm2RestrictedMgmtAccessGroup.hm2RmaOperation}  # HmEnabledStatus, access=ru, allowed=[True, False]
  modbus: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvModbusTcp}  # HmEnabledStatus, access=ru, allowed=[True, False]
  profinet: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvProfinetIO}  # HmEnabledStatus, access=ru, allowed=[True, False]
  prefix_length: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaPrefixLength}  # InetAddressPrefixLength, access=ru
  logging: {HM2-MGMTACCESS-MIB / hm2RestrictedMgmtAccessGroup.hm2RmaLoggingGlobal}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ssh: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvSsh}  # HmEnabledStatus, access=ru, allowed=[True, False]
  iec61850: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvIEC61850}  # HmEnabledStatus, access=ru, allowed=[True, False]
  telnet: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvTelnet}  # HmEnabledStatus, access=ru, allowed=[True, False]
  per_rule_logging: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaLogging}  # HmEnabledStatus, access=ru, allowed=[True, False]
  https: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvHttps}  # HmEnabledStatus, access=ru, allowed=[True, False]
  snmp: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvSnmp}  # HmEnabledStatus, access=ru, allowed=[True, False]
  index: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaIndex}  # Integer32, access=r, range=1–16
  ethernet_ip: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvEthernetIP}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ip: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaIpAddr}  # InetAddress, access=ru
}
```
</details>

<details><summary>SNMP sources (15/15 attrs)</summary>

```
SNMP {
  http: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.6}  # HmEnabledStatus, access=ru, allowed=[True, False]
  enabled: {oid: 1.3.6.1.4.1.248.11.25.1.7.2, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  modbus: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.12}  # HmEnabledStatus, access=ru, allowed=[True, False]
  profinet: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.14}  # HmEnabledStatus, access=ru, allowed=[True, False]
  prefix_length: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.5}  # InetAddressPrefixLength, access=ru
  logging: {oid: 1.3.6.1.4.1.248.11.25.1.7.3, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ssh: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.10}  # HmEnabledStatus, access=ru, allowed=[True, False]
  iec61850: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.11}  # HmEnabledStatus, access=ru, allowed=[True, False]
  telnet: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.9}  # HmEnabledStatus, access=ru, allowed=[True, False]
  per_rule_logging: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.16}  # HmEnabledStatus, access=ru, allowed=[True, False]
  https: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.7}  # HmEnabledStatus, access=ru, allowed=[True, False]
  snmp: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.8}  # HmEnabledStatus, access=ru, allowed=[True, False]
  index: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.1}  # Integer32, access=r, range=1–16
  ethernet_ip: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.13}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ip: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.4}  # InetAddress, access=ru
}
```
</details>

<details><summary>SSH sources (10/15 attrs)</summary>

```
SSH {
  http: {write: "network management access modify {_row_index} http {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  modbus: {write: "network management access modify {_row_index} modbus-tcp {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  profinet: {write: "network management access modify {_row_index} profinet-io {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ssh: {write: "network management access modify {_row_index} ssh {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  iec61850: {write: "network management access modify {_row_index} iec61850-mms {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  telnet: {write: "network management access modify {_row_index} telnet {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  https: {write: "network management access modify {_row_index} https {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  snmp: {write: "network management access modify {_row_index} snmp {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ethernet_ip: {write: "network management access modify {_row_index} ethernet-ip {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ip: {read: "show network management access rules"}  # InetAddress, access=ru
}
```
</details>

### `create_ip_restrict_rule()`

**Create** | **Protocols:** MOPS, SNMP, SSH
Required: `ip`

```
create_ip_restrict_rule() -> {
    addr_type: 1  // int
    prefix_length: 32  // int
    http: True  // bool
    https: True  // bool
    snmp: True  // bool
    telnet: True  // bool
    ssh: True  // bool
    iec61850: True  // bool
    modbus: True  // bool
    ethernet_ip: True  // bool
    profinet: True  // bool
    per_rule_logging: False  // bool
}
```


<details><summary>MOPS sources (13/13 attrs)</summary>

```
MOPS {
  http: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvHttp}  # HmEnabledStatus, access=ru, allowed=[True, False]
  modbus: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvModbusTcp}  # HmEnabledStatus, access=ru, allowed=[True, False]
  profinet: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvProfinetIO}  # HmEnabledStatus, access=ru, allowed=[True, False]
  prefix_length: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaPrefixLength}  # InetAddressPrefixLength, access=ru
  ssh: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvSsh}  # HmEnabledStatus, access=ru, allowed=[True, False]
  addr_type: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaIpAddrType}  # InetAddressType, access=ru
  iec61850: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvIEC61850}  # HmEnabledStatus, access=ru, allowed=[True, False]
  telnet: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvTelnet}  # HmEnabledStatus, access=ru, allowed=[True, False]
  per_rule_logging: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaLogging}  # HmEnabledStatus, access=ru, allowed=[True, False]
  https: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvHttps}  # HmEnabledStatus, access=ru, allowed=[True, False]
  snmp: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvSnmp}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ethernet_ip: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvEthernetIP}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ip: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaIpAddr}  # InetAddress, access=ru
}
```
</details>

<details><summary>SNMP sources (13/13 attrs)</summary>

```
SNMP {
  http: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.6}  # HmEnabledStatus, access=ru, allowed=[True, False]
  modbus: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.12}  # HmEnabledStatus, access=ru, allowed=[True, False]
  profinet: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.14}  # HmEnabledStatus, access=ru, allowed=[True, False]
  prefix_length: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.5}  # InetAddressPrefixLength, access=ru
  ssh: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.10}  # HmEnabledStatus, access=ru, allowed=[True, False]
  addr_type: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.3}  # InetAddressType, access=ru
  iec61850: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.11}  # HmEnabledStatus, access=ru, allowed=[True, False]
  telnet: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.9}  # HmEnabledStatus, access=ru, allowed=[True, False]
  per_rule_logging: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.16}  # HmEnabledStatus, access=ru, allowed=[True, False]
  https: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.7}  # HmEnabledStatus, access=ru, allowed=[True, False]
  snmp: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.8}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ethernet_ip: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.13}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ip: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.4}  # InetAddress, access=ru
}
```
</details>

<details><summary>SSH sources (10/13 attrs)</summary>

```
SSH {
  http: {write: "network management access modify {_row_index} http {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  modbus: {write: "network management access modify {_row_index} modbus-tcp {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  profinet: {write: "network management access modify {_row_index} profinet-io {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ssh: {write: "network management access modify {_row_index} ssh {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  iec61850: {write: "network management access modify {_row_index} iec61850-mms {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  telnet: {write: "network management access modify {_row_index} telnet {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  https: {write: "network management access modify {_row_index} https {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  snmp: {write: "network management access modify {_row_index} snmp {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ethernet_ip: {write: "network management access modify {_row_index} ethernet-ip {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ip: {read: "show network management access rules"}  # InetAddress, access=ru
}
```
</details>

### `delete_ip_restrict_rule()`

**Delete** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (18/18 attrs)</summary>

```
MOPS {
  http: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvHttp}  # HmEnabledStatus, access=ru, allowed=[True, False]
  enabled: {HM2-MGMTACCESS-MIB / hm2RestrictedMgmtAccessGroup.hm2RmaOperation}  # HmEnabledStatus, access=ru, allowed=[True, False]
  modbus: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvModbusTcp}  # HmEnabledStatus, access=ru, allowed=[True, False]
  profinet: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvProfinetIO}  # HmEnabledStatus, access=ru, allowed=[True, False]
  prefix_length: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaPrefixLength}  # InetAddressPrefixLength, access=ru
  logging: {HM2-MGMTACCESS-MIB / hm2RestrictedMgmtAccessGroup.hm2RmaLoggingGlobal}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ssh: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvSsh}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ethernet_ip: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvEthernetIP}  # HmEnabledStatus, access=ru, allowed=[True, False]
  addr_type: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaIpAddrType}  # InetAddressType, access=ru
  iec61850: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvIEC61850}  # HmEnabledStatus, access=ru, allowed=[True, False]
  telnet: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvTelnet}  # HmEnabledStatus, access=ru, allowed=[True, False]
  per_rule_logging: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaLogging}  # HmEnabledStatus, access=ru, allowed=[True, False]
  rule_status: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaRowStatus}  # RowStatus, access=crud
  index: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaIndex}  # Integer32, access=r, range=1–16
  https: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvHttps}  # HmEnabledStatus, access=ru, allowed=[True, False]
  snmp: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvSnmp}  # HmEnabledStatus, access=ru, allowed=[True, False]
  interface: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaInterface}  # InterfaceIndexOrZero, access=ru
  ip: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaIpAddr}  # InetAddress, access=ru
}
```
</details>

<details><summary>SNMP sources (18/18 attrs)</summary>

```
SNMP {
  http: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.6}  # HmEnabledStatus, access=ru, allowed=[True, False]
  enabled: {oid: 1.3.6.1.4.1.248.11.25.1.7.2, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  modbus: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.12}  # HmEnabledStatus, access=ru, allowed=[True, False]
  profinet: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.14}  # HmEnabledStatus, access=ru, allowed=[True, False]
  prefix_length: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.5}  # InetAddressPrefixLength, access=ru
  logging: {oid: 1.3.6.1.4.1.248.11.25.1.7.3, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ssh: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.10}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ethernet_ip: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.13}  # HmEnabledStatus, access=ru, allowed=[True, False]
  addr_type: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.3}  # InetAddressType, access=ru
  iec61850: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.11}  # HmEnabledStatus, access=ru, allowed=[True, False]
  telnet: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.9}  # HmEnabledStatus, access=ru, allowed=[True, False]
  per_rule_logging: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.16}  # HmEnabledStatus, access=ru, allowed=[True, False]
  rule_status: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.2}  # RowStatus, access=crud
  index: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.1}  # Integer32, access=r, range=1–16
  https: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.7}  # HmEnabledStatus, access=ru, allowed=[True, False]
  snmp: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.8}  # HmEnabledStatus, access=ru, allowed=[True, False]
  interface: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.15}  # InterfaceIndexOrZero, access=ru
  ip: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.4}  # InetAddress, access=ru
}
```
</details>

<details><summary>SSH sources (11/18 attrs)</summary>

```
SSH {
  http: {write: "network management access modify {_row_index} http {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  modbus: {write: "network management access modify {_row_index} modbus-tcp {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  profinet: {write: "network management access modify {_row_index} profinet-io {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ssh: {write: "network management access modify {_row_index} ssh {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ethernet_ip: {write: "network management access modify {_row_index} ethernet-ip {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  iec61850: {write: "network management access modify {_row_index} iec61850-mms {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  telnet: {write: "network management access modify {_row_index} telnet {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  rule_status: {write: "network management access add {index} ip {ip}"}  # RowStatus, access=crud
  https: {write: "network management access modify {_row_index} https {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  snmp: {write: "network management access modify {_row_index} snmp {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ip: {read: "show network management access rules"}  # InetAddress, access=ru
}
```
</details>

### `set_ip_restrict()`

**Update** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (18/18 attrs)</summary>

```
MOPS {
  http: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvHttp}  # HmEnabledStatus, access=ru, allowed=[True, False]
  enabled: {HM2-MGMTACCESS-MIB / hm2RestrictedMgmtAccessGroup.hm2RmaOperation}  # HmEnabledStatus, access=ru, allowed=[True, False]
  modbus: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvModbusTcp}  # HmEnabledStatus, access=ru, allowed=[True, False]
  profinet: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvProfinetIO}  # HmEnabledStatus, access=ru, allowed=[True, False]
  prefix_length: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaPrefixLength}  # InetAddressPrefixLength, access=ru
  logging: {HM2-MGMTACCESS-MIB / hm2RestrictedMgmtAccessGroup.hm2RmaLoggingGlobal}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ssh: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvSsh}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ethernet_ip: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvEthernetIP}  # HmEnabledStatus, access=ru, allowed=[True, False]
  addr_type: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaIpAddrType}  # InetAddressType, access=ru
  iec61850: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvIEC61850}  # HmEnabledStatus, access=ru, allowed=[True, False]
  telnet: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvTelnet}  # HmEnabledStatus, access=ru, allowed=[True, False]
  per_rule_logging: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaLogging}  # HmEnabledStatus, access=ru, allowed=[True, False]
  rule_status: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaRowStatus}  # RowStatus, access=crud
  index: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaIndex}  # Integer32, access=r, range=1–16
  https: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvHttps}  # HmEnabledStatus, access=ru, allowed=[True, False]
  snmp: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaSrvSnmp}  # HmEnabledStatus, access=ru, allowed=[True, False]
  interface: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaInterface}  # InterfaceIndexOrZero, access=ru
  ip: {HM2-MGMTACCESS-MIB / hm2RmaEntry.hm2RmaIpAddr}  # InetAddress, access=ru
}
```
</details>

<details><summary>SNMP sources (18/18 attrs)</summary>

```
SNMP {
  http: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.6}  # HmEnabledStatus, access=ru, allowed=[True, False]
  enabled: {oid: 1.3.6.1.4.1.248.11.25.1.7.2, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  modbus: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.12}  # HmEnabledStatus, access=ru, allowed=[True, False]
  profinet: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.14}  # HmEnabledStatus, access=ru, allowed=[True, False]
  prefix_length: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.5}  # InetAddressPrefixLength, access=ru
  logging: {oid: 1.3.6.1.4.1.248.11.25.1.7.3, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ssh: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.10}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ethernet_ip: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.13}  # HmEnabledStatus, access=ru, allowed=[True, False]
  addr_type: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.3}  # InetAddressType, access=ru
  iec61850: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.11}  # HmEnabledStatus, access=ru, allowed=[True, False]
  telnet: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.9}  # HmEnabledStatus, access=ru, allowed=[True, False]
  per_rule_logging: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.16}  # HmEnabledStatus, access=ru, allowed=[True, False]
  rule_status: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.2}  # RowStatus, access=crud
  index: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.1}  # Integer32, access=r, range=1–16
  https: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.7}  # HmEnabledStatus, access=ru, allowed=[True, False]
  snmp: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.8}  # HmEnabledStatus, access=ru, allowed=[True, False]
  interface: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.15}  # InterfaceIndexOrZero, access=ru
  ip: {oid: 1.3.6.1.4.1.248.11.25.1.7.1.1.4}  # InetAddress, access=ru
}
```
</details>

<details><summary>SSH sources (11/18 attrs)</summary>

```
SSH {
  http: {write: "network management access modify {_row_index} http {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  modbus: {write: "network management access modify {_row_index} modbus-tcp {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  profinet: {write: "network management access modify {_row_index} profinet-io {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ssh: {write: "network management access modify {_row_index} ssh {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ethernet_ip: {write: "network management access modify {_row_index} ethernet-ip {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  iec61850: {write: "network management access modify {_row_index} iec61850-mms {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  telnet: {write: "network management access modify {_row_index} telnet {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  rule_status: {write: "network management access add {index} ip {ip}"}  # RowStatus, access=crud
  https: {write: "network management access modify {_row_index} https {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  snmp: {write: "network management access modify {_row_index} snmp {'enable' if value else 'disable'}"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ip: {read: "show network management access rules"}  # InetAddress, access=ru
}
```
</details>

---

## ip_source_guard

_IP Source Guard per-port settings and static binding table_

### `get_ip_source_guard_port()`

**Read** | **Protocols:** MOPS, SNMP
Primary key: `enabled` | Key map: `ifindex`

```
get_ip_source_guard_port() -> {
    enabled: False  // bool
    port_security: False  // bool
}
```


<details><summary>MOPS sources (2/2 attrs)</summary>

```
MOPS {
  enabled: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentIpsgIfConfigEntry.hm2AgentIpsgIfVerifySource}  # TruthValue, access=ru, allowed=[True, False]
  port_security: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentIpsgIfConfigEntry.hm2AgentIpsgIfPortSecurity}  # TruthValue, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (2/2 attrs)</summary>

```
SNMP {
  enabled: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.5.1.1}  # TruthValue, access=ru, allowed=[True, False]
  port_security: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.5.1.2}  # TruthValue, access=ru, allowed=[True, False]
}
```
</details>

### `set_ip_source_guard_port()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (9/9 attrs)</summary>

```
MOPS {
  enabled: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentIpsgIfConfigEntry.hm2AgentIpsgIfVerifySource}  # TruthValue, access=ru, allowed=[True, False]
  binding_mac: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingMacAddr}  # MacAddress, access=ru
  binding_ip: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingIpAddr}  # IpAddress, access=ru
  binding_status: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingRowStatus}  # RowStatus, access=crud
  binding_ifindex: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingIfIndex}  # InterfaceIndex, access=ru
  binding_hw_status: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingHwStatus}  # TruthValue, access=r, allowed=[True, False]
  binding_active: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingRowStatus}  # RowStatus, access=crud
  port_security: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentIpsgIfConfigEntry.hm2AgentIpsgIfPortSecurity}  # TruthValue, access=ru, allowed=[True, False]
  binding_vlan: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingVlanId}  # VlanIndex, access=ru, range=1–4094
}
```
</details>

<details><summary>SNMP sources (9/9 attrs)</summary>

```
SNMP {
  enabled: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.5.1.1}  # TruthValue, access=ru, allowed=[True, False]
  binding_mac: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.3}  # MacAddress, access=ru
  binding_ip: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.4}  # IpAddress, access=ru
  binding_status: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.5}  # RowStatus, access=crud
  binding_ifindex: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.1}  # InterfaceIndex, access=ru
  binding_hw_status: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.248}  # TruthValue, access=r, allowed=[True, False]
  binding_active: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.5}  # RowStatus, access=crud
  port_security: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.5.1.2}  # TruthValue, access=ru, allowed=[True, False]
  binding_vlan: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.2}  # VlanIndex, access=ru, range=1–4094
}
```
</details>

### `get_ip_source_guard_bindings()`

**list** | **Protocols:** MOPS, SNMP
Primary key: `binding_ip`

```
get_ip_source_guard_bindings() -> {
    binding_ifindex: ""  // str
    binding_vlan: 0  // int
    binding_mac: ""  // str
    binding_ip: ""  // str
    binding_active: False  // "True"
    binding_hw_status: False  // bool
}
```


<details><summary>MOPS sources (6/6 attrs)</summary>

```
MOPS {
  binding_mac: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingMacAddr}  # MacAddress, access=ru
  binding_ip: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingIpAddr}  # IpAddress, access=ru
  binding_ifindex: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingIfIndex}  # InterfaceIndex, access=ru
  binding_hw_status: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingHwStatus}  # TruthValue, access=r, allowed=[True, False]
  binding_active: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingRowStatus}  # RowStatus, access=crud
  binding_vlan: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingVlanId}  # VlanIndex, access=ru, range=1–4094
}
```
</details>

<details><summary>SNMP sources (6/6 attrs)</summary>

```
SNMP {
  binding_mac: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.3}  # MacAddress, access=ru
  binding_ip: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.4}  # IpAddress, access=ru
  binding_ifindex: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.1}  # InterfaceIndex, access=ru
  binding_hw_status: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.248}  # TruthValue, access=r, allowed=[True, False]
  binding_active: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.5}  # RowStatus, access=crud
  binding_vlan: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.2}  # VlanIndex, access=ru, range=1–4094
}
```
</details>

### `set_ip_source_guard_binding()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (9/9 attrs)</summary>

```
MOPS {
  enabled: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentIpsgIfConfigEntry.hm2AgentIpsgIfVerifySource}  # TruthValue, access=ru, allowed=[True, False]
  binding_mac: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingMacAddr}  # MacAddress, access=ru
  binding_ip: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingIpAddr}  # IpAddress, access=ru
  binding_status: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingRowStatus}  # RowStatus, access=crud
  binding_ifindex: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingIfIndex}  # InterfaceIndex, access=ru
  binding_hw_status: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingHwStatus}  # TruthValue, access=r, allowed=[True, False]
  binding_active: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingRowStatus}  # RowStatus, access=crud
  port_security: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentIpsgIfConfigEntry.hm2AgentIpsgIfPortSecurity}  # TruthValue, access=ru, allowed=[True, False]
  binding_vlan: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingVlanId}  # VlanIndex, access=ru, range=1–4094
}
```
</details>

<details><summary>SNMP sources (9/9 attrs)</summary>

```
SNMP {
  enabled: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.5.1.1}  # TruthValue, access=ru, allowed=[True, False]
  binding_mac: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.3}  # MacAddress, access=ru
  binding_ip: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.4}  # IpAddress, access=ru
  binding_status: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.5}  # RowStatus, access=crud
  binding_ifindex: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.1}  # InterfaceIndex, access=ru
  binding_hw_status: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.248}  # TruthValue, access=r, allowed=[True, False]
  binding_active: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.5}  # RowStatus, access=crud
  port_security: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.5.1.2}  # TruthValue, access=ru, allowed=[True, False]
  binding_vlan: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.2}  # VlanIndex, access=ru, range=1–4094
}
```
</details>

### `create_static_binding()`

**Create** | **Protocols:** MOPS, SNMP
Required: `binding_ifindex`

```
create_static_binding() -> {
    binding_vlan: 1  // int
}
```


<details><summary>MOPS sources (2/2 attrs)</summary>

```
MOPS {
  binding_ifindex: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingIfIndex}  # InterfaceIndex, access=ru
  binding_vlan: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingVlanId}  # VlanIndex, access=ru, range=1–4094
}
```
</details>

<details><summary>SNMP sources (2/2 attrs)</summary>

```
SNMP {
  binding_ifindex: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.1}  # InterfaceIndex, access=ru
  binding_vlan: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.2}  # VlanIndex, access=ru, range=1–4094
}
```
</details>

### `delete_static_binding()`

**Delete** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (9/9 attrs)</summary>

```
MOPS {
  enabled: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentIpsgIfConfigEntry.hm2AgentIpsgIfVerifySource}  # TruthValue, access=ru, allowed=[True, False]
  binding_mac: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingMacAddr}  # MacAddress, access=ru
  binding_ip: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingIpAddr}  # IpAddress, access=ru
  binding_status: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingRowStatus}  # RowStatus, access=crud
  binding_ifindex: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingIfIndex}  # InterfaceIndex, access=ru
  binding_hw_status: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingHwStatus}  # TruthValue, access=r, allowed=[True, False]
  binding_active: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingRowStatus}  # RowStatus, access=crud
  port_security: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentIpsgIfConfigEntry.hm2AgentIpsgIfPortSecurity}  # TruthValue, access=ru, allowed=[True, False]
  binding_vlan: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStaticIpsgBindingEntry.hm2AgentStaticIpsgBindingVlanId}  # VlanIndex, access=ru, range=1–4094
}
```
</details>

<details><summary>SNMP sources (9/9 attrs)</summary>

```
SNMP {
  enabled: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.5.1.1}  # TruthValue, access=ru, allowed=[True, False]
  binding_mac: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.3}  # MacAddress, access=ru
  binding_ip: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.4}  # IpAddress, access=ru
  binding_status: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.5}  # RowStatus, access=crud
  binding_ifindex: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.1}  # InterfaceIndex, access=ru
  binding_hw_status: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.248}  # TruthValue, access=r, allowed=[True, False]
  binding_active: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.5}  # RowStatus, access=crud
  port_security: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.5.1.2}  # TruthValue, access=ru, allowed=[True, False]
  binding_vlan: {oid: 1.3.6.1.4.1.248.12.1.2.8.23.8.1.2}  # VlanIndex, access=ru, range=1–4094
}
```
</details>

---

## ipv6

_IPv6 configuration and neighbor discovery_

### `get_ipv6_neighbors()`

**list** | **Protocols:** MOPS, SNMP

```
get_ipv6_neighbors() -> {
    interface: ""  // str
    ip: ""  // str
    mac: ""  // str
    state: "reachable"  // "reachable" | "stale" | "delay" | "probe" | "invalid" | "unknown" | "incomplete"
}
```


<details><summary>MOPS sources (4/4 attrs)</summary>

```
MOPS {
  interface: {IP-MIB / ipNetToPhysicalEntry.ipNetToPhysicalIfIndex}  # InterfaceIndex, access=r
  state: {IP-MIB / ipNetToPhysicalEntry.ipNetToPhysicalState}  # INTEGER, access=r, allowed=['reachable', 'stale', 'delay', 'probe', 'invalid', 'unknown', 'incomplete']
  mac: {IP-MIB / ipNetToPhysicalEntry.ipNetToPhysicalPhysAddress}  # PhysAddress, access=ru, range=0–65535
  ip: {IP-MIB / ipNetToPhysicalEntry.ipNetToPhysicalNetAddress}  # InetAddress, access=r
}
```
</details>

<details><summary>SNMP sources (4/4 attrs)</summary>

```
SNMP {
  interface: {oid: 1.3.6.1.2.1.4.35.1.1}  # InterfaceIndex, access=r
  state: {oid: 1.3.6.1.2.1.4.35.1.7}  # INTEGER, access=r, allowed=['reachable', 'stale', 'delay', 'probe', 'invalid', 'unknown', 'incomplete']
  mac: {oid: 1.3.6.1.2.1.4.35.1.4}  # PhysAddress, access=ru, range=0–65535
  ip: {oid: 1.3.6.1.2.1.4.35.1.3}  # InetAddress, access=r
}
```
</details>

### `get_ipv6_neighbors_table()`

**list** | **Protocols:** MOPS, SNMP

```
get_ipv6_neighbors_table() -> {
    interface: ""  // str
    ip: ""  // str
    mac: ""  // str
    state: "reachable"  // "reachable" | "stale" | "delay" | "probe" | "invalid" | "unknown" | "incomplete"
}
```


<details><summary>MOPS sources (4/4 attrs)</summary>

```
MOPS {
  interface: {IP-MIB / ipNetToPhysicalEntry.ipNetToPhysicalIfIndex}  # InterfaceIndex, access=r
  state: {IP-MIB / ipNetToPhysicalEntry.ipNetToPhysicalState}  # INTEGER, access=r, allowed=['reachable', 'stale', 'delay', 'probe', 'invalid', 'unknown', 'incomplete']
  mac: {IP-MIB / ipNetToPhysicalEntry.ipNetToPhysicalPhysAddress}  # PhysAddress, access=ru, range=0–65535
  ip: {IP-MIB / ipNetToPhysicalEntry.ipNetToPhysicalNetAddress}  # InetAddress, access=r
}
```
</details>

<details><summary>SNMP sources (4/4 attrs)</summary>

```
SNMP {
  interface: {oid: 1.3.6.1.2.1.4.35.1.1}  # InterfaceIndex, access=r
  state: {oid: 1.3.6.1.2.1.4.35.1.7}  # INTEGER, access=r, allowed=['reachable', 'stale', 'delay', 'probe', 'invalid', 'unknown', 'incomplete']
  mac: {oid: 1.3.6.1.2.1.4.35.1.4}  # PhysAddress, access=ru, range=0–65535
  ip: {oid: 1.3.6.1.2.1.4.35.1.3}  # InetAddress, access=r
}
```
</details>

---

## lldp

_LLDP configuration and neighbor table_

### `get_lldp_neighbors()`

**list_append** | **Protocols:** MOPS, SNMP
Primary key: `local_port` | Key map: `ifindex`

```
get_lldp_neighbors() -> {
    sys_name: ""  // str
    port_id: ""  // str
}
```


<details><summary>MOPS sources (3/3 attrs)</summary>

```
MOPS {
  sys_name: {LLDP-MIB / lldpRemEntry.lldpRemSysName}  # SnmpAdminString, access=r, range=0–255
  port_id: {LLDP-MIB / lldpRemEntry.lldpRemPortId}  # LldpPortId, access=r
  local_port: {LLDP-MIB / lldpRemEntry.lldpRemLocalPortNum}  # LldpPortNumber, access=r
}
```
</details>

<details><summary>SNMP sources (3/3 attrs)</summary>

```
SNMP {
  sys_name: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.9}  # SnmpAdminString, access=r, range=0–255
  port_id: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.7}  # LldpPortId, access=r
  local_port: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.2}  # LldpPortNumber, access=r
}
```
</details>

### `get_lldp_neighbors_detail()`

**list_append** | **Protocols:** MOPS, SNMP
Primary key: `local_port` | Key map: `ifindex`

```
get_lldp_neighbors_detail() -> {
    port_id: ""  // str
    sys_name: ""  // str
    port_description: ""  // str
    chassis_id: ""  // str
    sys_description: ""  // str
    sys_capabilities: [...]  // list
    sys_enabled_capabilities: [...]  // list
    autoneg_supported: False  // bool
    autoneg_enabled: False  // bool
    mau_type: 0  // int
    pvid: 0  // int
    aggregation_enabled: [...]  // list
    aggregation_port_id: 0  // int
}
```


<details><summary>MOPS sources (14/14 attrs)</summary>

```
MOPS {
  port_description: {LLDP-MIB / lldpRemEntry.lldpRemPortDesc}  # SnmpAdminString, access=r, range=0–255
  port_id: {LLDP-MIB / lldpRemEntry.lldpRemPortId}  # LldpPortId, access=r
  sys_capabilities: {LLDP-MIB / lldpRemEntry.lldpRemSysCapSupported}  # LldpSystemCapabilitiesMap, access=r
  autoneg_enabled: {LLDP-EXT-DOT3-MIB / lldpXdot3RemPortEntry.lldpXdot3RemPortAutoNegEnabled}  # TruthValue, access=r, allowed=[True, False]
  aggregation_port_id: {LLDP-EXT-DOT3-MIB / lldpXdot3RemLinkAggEntry.lldpXdot3RemLinkAggPortId}  # Integer32, access=r
  sys_enabled_capabilities: {LLDP-MIB / lldpRemEntry.lldpRemSysCapEnabled}  # LldpSystemCapabilitiesMap, access=r
  local_port: {LLDP-MIB / lldpRemEntry.lldpRemLocalPortNum}  # LldpPortNumber, access=r
  sys_name: {LLDP-MIB / lldpRemEntry.lldpRemSysName}  # SnmpAdminString, access=r, range=0–255
  chassis_id: {LLDP-MIB / lldpRemEntry.lldpRemChassisId}  # LldpChassisId, access=r
  pvid: {LLDP-EXT-DOT1-MIB / lldpXdot1RemEntry.lldpXdot1RemPortVlanId}  # Integer32, access=r
  autoneg_supported: {LLDP-EXT-DOT3-MIB / lldpXdot3RemPortEntry.lldpXdot3RemPortAutoNegSupported}  # TruthValue, access=r, allowed=[True, False]
  sys_description: {LLDP-MIB / lldpRemEntry.lldpRemSysDesc}  # SnmpAdminString, access=r, range=0–255
  mau_type: {LLDP-EXT-DOT3-MIB / lldpXdot3RemPortEntry.lldpXdot3RemPortOperMauType}  # Integer32, access=r, range=0–2147483647
  aggregation_enabled: {LLDP-EXT-DOT3-MIB / lldpXdot3RemLinkAggEntry.lldpXdot3RemLinkAggStatus}  # LldpLinkAggStatusMap, access=r
}
```
</details>

<details><summary>SNMP sources (14/14 attrs)</summary>

```
SNMP {
  port_description: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.8}  # SnmpAdminString, access=r, range=0–255
  port_id: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.7}  # LldpPortId, access=r
  sys_capabilities: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.11}  # LldpSystemCapabilitiesMap, access=r
  autoneg_enabled: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.5.4623.1.3.1.1.2}  # TruthValue, access=r, allowed=[True, False]
  aggregation_port_id: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.5.4623.1.3.3.1.2}  # Integer32, access=r
  sys_enabled_capabilities: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.12}  # LldpSystemCapabilitiesMap, access=r
  local_port: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.2}  # LldpPortNumber, access=r
  sys_name: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.9}  # SnmpAdminString, access=r, range=0–255
  chassis_id: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.5}  # LldpChassisId, access=r
  pvid: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.5.32962.1.3.1.1.1}  # Integer32, access=r
  autoneg_supported: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.5.4623.1.3.1.1.1}  # TruthValue, access=r, allowed=[True, False]
  sys_description: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.10}  # SnmpAdminString, access=r, range=0–255
  mau_type: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.5.4623.1.3.1.1.4}  # Integer32, access=r, range=0–2147483647
  aggregation_enabled: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.5.4623.1.3.3.1.1}  # LldpLinkAggStatusMap, access=r
}
```
</details>

### `get_lldp_neighbors_detail_extended()`

**Read** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (17/17 attrs)</summary>

```
MOPS {
  port_description: {LLDP-MIB / lldpRemEntry.lldpRemPortDesc}  # SnmpAdminString, access=r, range=0–255
  enabled: {HM2-LLDP-MIB / hm2LLDPConfigGroup.hm2LLDPAdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_id: {LLDP-MIB / lldpRemEntry.lldpRemPortId}  # LldpPortId, access=r
  hello_interval: {LLDP-MIB / lldpConfiguration.lldpMessageTxInterval}  # Integer32, access=ru, range=5–32768
  hold_multiplier: {LLDP-MIB / lldpConfiguration.lldpMessageTxHoldMultiplier}  # Integer32, access=ru, range=2–10
  sys_capabilities: {LLDP-MIB / lldpRemEntry.lldpRemSysCapSupported}  # LldpSystemCapabilitiesMap, access=r
  autoneg_enabled: {LLDP-EXT-DOT3-MIB / lldpXdot3RemPortEntry.lldpXdot3RemPortAutoNegEnabled}  # TruthValue, access=r, allowed=[True, False]
  aggregation_port_id: {LLDP-EXT-DOT3-MIB / lldpXdot3RemLinkAggEntry.lldpXdot3RemLinkAggPortId}  # Integer32, access=r
  sys_enabled_capabilities: {LLDP-MIB / lldpRemEntry.lldpRemSysCapEnabled}  # LldpSystemCapabilitiesMap, access=r
  local_port: {LLDP-MIB / lldpRemEntry.lldpRemLocalPortNum}  # LldpPortNumber, access=r
  sys_name: {LLDP-MIB / lldpRemEntry.lldpRemSysName}  # SnmpAdminString, access=r, range=0–255
  chassis_id: {LLDP-MIB / lldpRemEntry.lldpRemChassisId}  # LldpChassisId, access=r
  pvid: {LLDP-EXT-DOT1-MIB / lldpXdot1RemEntry.lldpXdot1RemPortVlanId}  # Integer32, access=r
  autoneg_supported: {LLDP-EXT-DOT3-MIB / lldpXdot3RemPortEntry.lldpXdot3RemPortAutoNegSupported}  # TruthValue, access=r, allowed=[True, False]
  sys_description: {LLDP-MIB / lldpRemEntry.lldpRemSysDesc}  # SnmpAdminString, access=r, range=0–255
  mau_type: {LLDP-EXT-DOT3-MIB / lldpXdot3RemPortEntry.lldpXdot3RemPortOperMauType}  # Integer32, access=r, range=0–2147483647
  aggregation_enabled: {LLDP-EXT-DOT3-MIB / lldpXdot3RemLinkAggEntry.lldpXdot3RemLinkAggStatus}  # LldpLinkAggStatusMap, access=r
}
```
</details>

<details><summary>SNMP sources (17/17 attrs)</summary>

```
SNMP {
  port_description: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.8}  # SnmpAdminString, access=r, range=0–255
  enabled: {oid: 1.3.6.1.4.1.248.11.34.1.1.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_id: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.7}  # LldpPortId, access=r
  hello_interval: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.1.1, method: get}  # Integer32, access=ru, range=5–32768
  hold_multiplier: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.1.2, method: get}  # Integer32, access=ru, range=2–10
  sys_capabilities: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.11}  # LldpSystemCapabilitiesMap, access=r
  autoneg_enabled: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.5.4623.1.3.1.1.2}  # TruthValue, access=r, allowed=[True, False]
  aggregation_port_id: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.5.4623.1.3.3.1.2}  # Integer32, access=r
  sys_enabled_capabilities: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.12}  # LldpSystemCapabilitiesMap, access=r
  local_port: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.2}  # LldpPortNumber, access=r
  sys_name: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.9}  # SnmpAdminString, access=r, range=0–255
  chassis_id: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.5}  # LldpChassisId, access=r
  pvid: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.5.32962.1.3.1.1.1}  # Integer32, access=r
  autoneg_supported: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.5.4623.1.3.1.1.1}  # TruthValue, access=r, allowed=[True, False]
  sys_description: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.10}  # SnmpAdminString, access=r, range=0–255
  mau_type: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.5.4623.1.3.1.1.4}  # Integer32, access=r, range=0–2147483647
  aggregation_enabled: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.5.4623.1.3.3.1.1}  # LldpLinkAggStatusMap, access=r
}
```
</details>

### `set_lldp()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (17/17 attrs)</summary>

```
MOPS {
  port_description: {LLDP-MIB / lldpRemEntry.lldpRemPortDesc}  # SnmpAdminString, access=r, range=0–255
  enabled: {HM2-LLDP-MIB / hm2LLDPConfigGroup.hm2LLDPAdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_id: {LLDP-MIB / lldpRemEntry.lldpRemPortId}  # LldpPortId, access=r
  hello_interval: {LLDP-MIB / lldpConfiguration.lldpMessageTxInterval}  # Integer32, access=ru, range=5–32768
  hold_multiplier: {LLDP-MIB / lldpConfiguration.lldpMessageTxHoldMultiplier}  # Integer32, access=ru, range=2–10
  sys_capabilities: {LLDP-MIB / lldpRemEntry.lldpRemSysCapSupported}  # LldpSystemCapabilitiesMap, access=r
  autoneg_enabled: {LLDP-EXT-DOT3-MIB / lldpXdot3RemPortEntry.lldpXdot3RemPortAutoNegEnabled}  # TruthValue, access=r, allowed=[True, False]
  aggregation_port_id: {LLDP-EXT-DOT3-MIB / lldpXdot3RemLinkAggEntry.lldpXdot3RemLinkAggPortId}  # Integer32, access=r
  sys_enabled_capabilities: {LLDP-MIB / lldpRemEntry.lldpRemSysCapEnabled}  # LldpSystemCapabilitiesMap, access=r
  local_port: {LLDP-MIB / lldpRemEntry.lldpRemLocalPortNum}  # LldpPortNumber, access=r
  sys_name: {LLDP-MIB / lldpRemEntry.lldpRemSysName}  # SnmpAdminString, access=r, range=0–255
  chassis_id: {LLDP-MIB / lldpRemEntry.lldpRemChassisId}  # LldpChassisId, access=r
  pvid: {LLDP-EXT-DOT1-MIB / lldpXdot1RemEntry.lldpXdot1RemPortVlanId}  # Integer32, access=r
  autoneg_supported: {LLDP-EXT-DOT3-MIB / lldpXdot3RemPortEntry.lldpXdot3RemPortAutoNegSupported}  # TruthValue, access=r, allowed=[True, False]
  sys_description: {LLDP-MIB / lldpRemEntry.lldpRemSysDesc}  # SnmpAdminString, access=r, range=0–255
  mau_type: {LLDP-EXT-DOT3-MIB / lldpXdot3RemPortEntry.lldpXdot3RemPortOperMauType}  # Integer32, access=r, range=0–2147483647
  aggregation_enabled: {LLDP-EXT-DOT3-MIB / lldpXdot3RemLinkAggEntry.lldpXdot3RemLinkAggStatus}  # LldpLinkAggStatusMap, access=r
}
```
</details>

<details><summary>SNMP sources (17/17 attrs)</summary>

```
SNMP {
  port_description: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.8}  # SnmpAdminString, access=r, range=0–255
  enabled: {oid: 1.3.6.1.4.1.248.11.34.1.1.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_id: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.7}  # LldpPortId, access=r
  hello_interval: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.1.1, method: get}  # Integer32, access=ru, range=5–32768
  hold_multiplier: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.1.2, method: get}  # Integer32, access=ru, range=2–10
  sys_capabilities: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.11}  # LldpSystemCapabilitiesMap, access=r
  autoneg_enabled: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.5.4623.1.3.1.1.2}  # TruthValue, access=r, allowed=[True, False]
  aggregation_port_id: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.5.4623.1.3.3.1.2}  # Integer32, access=r
  sys_enabled_capabilities: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.12}  # LldpSystemCapabilitiesMap, access=r
  local_port: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.2}  # LldpPortNumber, access=r
  sys_name: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.9}  # SnmpAdminString, access=r, range=0–255
  chassis_id: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.5}  # LldpChassisId, access=r
  pvid: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.5.32962.1.3.1.1.1}  # Integer32, access=r
  autoneg_supported: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.5.4623.1.3.1.1.1}  # TruthValue, access=r, allowed=[True, False]
  sys_description: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.4.1.1.10}  # SnmpAdminString, access=r, range=0–255
  mau_type: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.5.4623.1.3.1.1.4}  # Integer32, access=r, range=0–2147483647
  aggregation_enabled: {oid: 1.3.6.1.2.1.0.8802.1.1.2.1.5.4623.1.3.3.1.1}  # LldpLinkAggStatusMap, access=r
}
```
</details>

---

## mac

_MAC address table (FDB) mapping_

### `get_mac_address_table()`

**list** | **Protocols:** MOPS, SNMP
Primary key: `mac`

```
get_mac_address_table() -> {
    mac: ""  // str
    interface: ""  // str (via bridge_port)
    vlan: 0  // int
    status: "other"  // "other" | "invalid" | "learned" | "self" | "mgmt"
}
```


<details><summary>MOPS sources (4/4 attrs)</summary>

```
MOPS {
  interface: {Q-BRIDGE-MIB / dot1qTpFdbEntry.dot1qTpFdbPort}  # INTEGER, access=r, range=0–65535
  status: {Q-BRIDGE-MIB / dot1qTpFdbEntry.dot1qTpFdbStatus}  # INTEGER, access=r
  mac: {Q-BRIDGE-MIB / dot1qTpFdbEntry.dot1qTpFdbAddress}  # MacAddress, access=r
  vlan: {Q-BRIDGE-MIB / dot1qFdbEntry.dot1qFdbId}  # Unsigned32, access=r
}
```
</details>

<details><summary>SNMP sources (4/4 attrs)</summary>

```
SNMP {
  interface: {oid: 1.3.6.1.2.1.17.7.1.2.2.1.2}  # INTEGER, access=r, range=0–65535
  status: {oid: 1.3.6.1.2.1.17.7.1.2.2.1.3}  # INTEGER, access=r
  mac: {oid: 1.3.6.1.2.1.17.7.1.2.2.1.1}  # MacAddress, access=r
  vlan: {oid: 1.3.6.1.2.1.17.7.1.2.1.1.1}  # Unsigned32, access=r
}
```
</details>

---

## management

_Management interface and access configuration_

### `get_management()`

**Read** | **Protocols:** MOPS, SNMP

```
get_management() -> {
    ip_address: ""  // str
    prefix_length: 0  // int
    netmask: ""  // str (computed)
    gateway: ""  // str
    vlan_id: 1  // int
    protocol: ""  // "static" | "bootp" | "dhcp"
}
```


<details><summary>MOPS sources (5/6 attrs)</summary>

```
MOPS {
  gateway: {HM2-NETCONFIG-MIB / hm2NetStaticGroup.hm2NetGatewayIPAddr}  # InetAddress, access=ru
  protocol: {HM2-NETCONFIG-MIB / hm2NetStaticGroup.hm2NetConfigProtocol}  # INTEGER, access=ru, allowed=['none', 'bootp', 'dhcp']
  prefix_length: {HM2-NETCONFIG-MIB / hm2NetStaticGroup.hm2NetPrefixLength}  # InetAddressPrefixLength, access=ru
  vlan_id: {HM2-NETCONFIG-MIB / hm2NetStaticGroup.hm2NetVlanID}  # Integer32, access=ru, range=1–4042
  ip_address: {HM2-NETCONFIG-MIB / hm2NetStaticGroup.hm2NetLocalIPAddr}  # InetAddress, access=ru
}
```
</details>

<details><summary>SNMP sources (5/6 attrs)</summary>

```
SNMP {
  gateway: {oid: 1.3.6.1.4.1.248.11.20.1.1.6, method: get}  # InetAddress, access=ru
  protocol: {oid: 1.3.6.1.4.1.248.11.20.1.1.1, method: get}  # INTEGER, access=ru, allowed=['none', 'bootp', 'dhcp']
  prefix_length: {oid: 1.3.6.1.4.1.248.11.20.1.1.4, method: get}  # InetAddressPrefixLength, access=ru
  vlan_id: {oid: 1.3.6.1.4.1.248.11.20.1.1.7, method: get}  # Integer32, access=ru, range=1–4042
  ip_address: {oid: 1.3.6.1.4.1.248.11.20.1.1.3, method: get}  # InetAddress, access=ru
}
```
</details>

### `set_management()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (5/6 attrs)</summary>

```
MOPS {
  gateway: {HM2-NETCONFIG-MIB / hm2NetStaticGroup.hm2NetGatewayIPAddr}  # InetAddress, access=ru
  protocol: {HM2-NETCONFIG-MIB / hm2NetStaticGroup.hm2NetConfigProtocol}  # INTEGER, access=ru, allowed=['none', 'bootp', 'dhcp']
  prefix_length: {HM2-NETCONFIG-MIB / hm2NetStaticGroup.hm2NetPrefixLength}  # InetAddressPrefixLength, access=ru
  vlan_id: {HM2-NETCONFIG-MIB / hm2NetStaticGroup.hm2NetVlanID}  # Integer32, access=ru, range=1–4042
  ip_address: {HM2-NETCONFIG-MIB / hm2NetStaticGroup.hm2NetLocalIPAddr}  # InetAddress, access=ru
}
```
</details>

<details><summary>SNMP sources (5/6 attrs)</summary>

```
SNMP {
  gateway: {oid: 1.3.6.1.4.1.248.11.20.1.1.6, method: get}  # InetAddress, access=ru
  protocol: {oid: 1.3.6.1.4.1.248.11.20.1.1.1, method: get}  # INTEGER, access=ru, allowed=['none', 'bootp', 'dhcp']
  prefix_length: {oid: 1.3.6.1.4.1.248.11.20.1.1.4, method: get}  # InetAddressPrefixLength, access=ru
  vlan_id: {oid: 1.3.6.1.4.1.248.11.20.1.1.7, method: get}  # Integer32, access=ru, range=1–4042
  ip_address: {oid: 1.3.6.1.4.1.248.11.20.1.1.3, method: get}  # InetAddress, access=ru
}
```
</details>

### `get_management_priority()`

**list** | **Protocols:** None

```
get_management_priority() -> {
    source: "local"  // str
    priority: 1  // int
}
```


### `set_management_priority()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (5/6 attrs)</summary>

```
MOPS {
  gateway: {HM2-NETCONFIG-MIB / hm2NetStaticGroup.hm2NetGatewayIPAddr}  # InetAddress, access=ru
  protocol: {HM2-NETCONFIG-MIB / hm2NetStaticGroup.hm2NetConfigProtocol}  # INTEGER, access=ru, allowed=['none', 'bootp', 'dhcp']
  prefix_length: {HM2-NETCONFIG-MIB / hm2NetStaticGroup.hm2NetPrefixLength}  # InetAddressPrefixLength, access=ru
  vlan_id: {HM2-NETCONFIG-MIB / hm2NetStaticGroup.hm2NetVlanID}  # Integer32, access=ru, range=1–4042
  ip_address: {HM2-NETCONFIG-MIB / hm2NetStaticGroup.hm2NetLocalIPAddr}  # InetAddress, access=ru
}
```
</details>

<details><summary>SNMP sources (5/6 attrs)</summary>

```
SNMP {
  gateway: {oid: 1.3.6.1.4.1.248.11.20.1.1.6, method: get}  # InetAddress, access=ru
  protocol: {oid: 1.3.6.1.4.1.248.11.20.1.1.1, method: get}  # INTEGER, access=ru, allowed=['none', 'bootp', 'dhcp']
  prefix_length: {oid: 1.3.6.1.4.1.248.11.20.1.1.4, method: get}  # InetAddressPrefixLength, access=ru
  vlan_id: {oid: 1.3.6.1.4.1.248.11.20.1.1.7, method: get}  # Integer32, access=ru, range=1–4042
  ip_address: {oid: 1.3.6.1.4.1.248.11.20.1.1.3, method: get}  # InetAddress, access=ru
}
```
</details>

---

## mrp

_Media Redundancy Protocol (MRP) domain configuration_

### `get_mrp()`

**Read** | **Protocols:** MOPS, SNMP
Primary key: `domain_id`

```
get_mrp() -> {
    operation: False  // "True" | "False"
    role: "undefined"  // "client" | "manager" | "undefined"
    domain_name: ""  // str
    vlan: 0  // int
    ring_port1: ""  // str (via ifindex)
    ring_port2: ""  // str (via ifindex)
    ring_port1_state: "notConnected"  // "disabled" | "blocked" | "forwarding" | "notConnected"
    ring_port2_state: "notConnected"  // "disabled" | "blocked" | "forwarding" | "notConnected"
    ring_state: "undefined"  // "open" | "closed" | "undefined"
    recovery_delay: ""  // "500ms" | "200ms" | "30ms" | "10ms"
    advanced_mode: False  // bool
    manager_priority: 0  // int
    fixed_backup: False  // bool
}
```


<details><summary>MOPS sources (14/14 attrs)</summary>

```
MOPS {
  ring_state: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpRingOperState}  # INTEGER, access=r, allowed=['open', 'closed', 'undefined']
  ring_port2_state: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpRingport2OperState}  # INTEGER, access=r, allowed=['disabled', 'blocked', 'forwarding', 'notConnected']
  operation: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpRowStatus}  # RowStatus, access=crud
  domain_id: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpDomainID}  # OCTET STRING, access=r
  ring_port2: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpRingport2IfIndex}  # Integer32, access=ru
  ring_port1_state: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpRingport1OperState}  # INTEGER, access=r, allowed=['disabled', 'blocked', 'forwarding', 'notConnected']
  fixed_backup: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpRingport2FixedBackup}  # HmEnabledStatus, access=ru, allowed=[True, False]
  role: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpRoleAdminState}  # INTEGER, access=ru, allowed=['client', 'manager']
  ring_port1: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpRingport1IfIndex}  # Integer32, access=ru
  domain_name: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpDomainName}  # SnmpAdminString, access=ru
  recovery_delay: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpRecoveryDelay}  # INTEGER, access=ru, allowed=['delay500', 'delay200', 'delay30', 'delay10']
  advanced_mode: {HM2-L2REDUNDANCY-MIB / hm2MrpMibGroup.hm2MrpFastMrp}  # INTEGER, access=r, allowed=['supported', 'notSupported']
  manager_priority: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpMRMPriority}  # Integer32 (0..65535), access=ru, range=0–65535
  vlan: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpVlanID}  # Integer32, access=ru
}
```
</details>

<details><summary>SNMP sources (14/14 attrs)</summary>

```
SNMP {
  ring_state: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.23}  # INTEGER, access=r, allowed=['open', 'closed', 'undefined']
  ring_port2_state: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.8}  # INTEGER, access=r, allowed=['disabled', 'blocked', 'forwarding', 'notConnected']
  operation: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.26}  # RowStatus, access=crud
  domain_id: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.1}  # OCTET STRING, access=r
  ring_port2: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.7}  # Integer32, access=ru
  ring_port1_state: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.5}  # INTEGER, access=r, allowed=['disabled', 'blocked', 'forwarding', 'notConnected']
  fixed_backup: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.27}  # HmEnabledStatus, access=ru, allowed=[True, False]
  role: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.9}  # INTEGER, access=ru, allowed=['client', 'manager']
  ring_port1: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.4}  # Integer32, access=ru
  domain_name: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.2}  # SnmpAdminString, access=ru
  recovery_delay: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.11}  # INTEGER, access=ru, allowed=['delay500', 'delay200', 'delay30', 'delay10']
  advanced_mode: {oid: 1.3.6.1.4.1.248.11.40.1.1.3, method: get}  # INTEGER, access=r, allowed=['supported', 'notSupported']
  manager_priority: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.14}  # Integer32 (0..65535), access=ru, range=0–65535
  vlan: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.13}  # Integer32, access=ru
}
```
</details>

### `set_mrp()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (15/15 attrs)</summary>

```
MOPS {
  ring_state: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpRingOperState}  # INTEGER, access=r, allowed=['open', 'closed', 'undefined']
  ring_port2_state: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpRingport2OperState}  # INTEGER, access=r, allowed=['disabled', 'blocked', 'forwarding', 'notConnected']
  operation: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpRowStatus}  # RowStatus, access=crud
  mrp_status: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpRowStatus}  # RowStatus, access=crud
  domain_id: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpDomainID}  # OCTET STRING, access=r
  ring_port2: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpRingport2IfIndex}  # Integer32, access=ru
  ring_port1_state: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpRingport1OperState}  # INTEGER, access=r, allowed=['disabled', 'blocked', 'forwarding', 'notConnected']
  fixed_backup: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpRingport2FixedBackup}  # HmEnabledStatus, access=ru, allowed=[True, False]
  role: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpRoleAdminState}  # INTEGER, access=ru, allowed=['client', 'manager']
  ring_port1: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpRingport1IfIndex}  # Integer32, access=ru
  domain_name: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpDomainName}  # SnmpAdminString, access=ru
  recovery_delay: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpRecoveryDelay}  # INTEGER, access=ru, allowed=['delay500', 'delay200', 'delay30', 'delay10']
  advanced_mode: {HM2-L2REDUNDANCY-MIB / hm2MrpMibGroup.hm2MrpFastMrp}  # INTEGER, access=r, allowed=['supported', 'notSupported']
  manager_priority: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpMRMPriority}  # Integer32 (0..65535), access=ru, range=0–65535
  vlan: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpVlanID}  # Integer32, access=ru
}
```
</details>

<details><summary>SNMP sources (15/15 attrs)</summary>

```
SNMP {
  ring_state: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.23}  # INTEGER, access=r, allowed=['open', 'closed', 'undefined']
  ring_port2_state: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.8}  # INTEGER, access=r, allowed=['disabled', 'blocked', 'forwarding', 'notConnected']
  operation: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.26}  # RowStatus, access=crud
  mrp_status: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.26}  # RowStatus, access=crud
  domain_id: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.1}  # OCTET STRING, access=r
  ring_port2: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.7}  # Integer32, access=ru
  ring_port1_state: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.5}  # INTEGER, access=r, allowed=['disabled', 'blocked', 'forwarding', 'notConnected']
  fixed_backup: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.27}  # HmEnabledStatus, access=ru, allowed=[True, False]
  role: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.9}  # INTEGER, access=ru, allowed=['client', 'manager']
  ring_port1: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.4}  # Integer32, access=ru
  domain_name: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.2}  # SnmpAdminString, access=ru
  recovery_delay: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.11}  # INTEGER, access=ru, allowed=['delay500', 'delay200', 'delay30', 'delay10']
  advanced_mode: {oid: 1.3.6.1.4.1.248.11.40.1.1.3, method: get}  # INTEGER, access=r, allowed=['supported', 'notSupported']
  manager_priority: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.14}  # Integer32 (0..65535), access=ru, range=0–65535
  vlan: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.13}  # Integer32, access=ru
}
```
</details>

### `create_mrp()`

**Create** | **Protocols:** MOPS, SNMP

```
create_mrp() -> {
    domain_id: "ff:ff:ff:ff:ff:ff:ff:ff:ff:ff:ff:ff:ff:ff:ff:ff"  // str
}
```


<details><summary>MOPS sources (1/1 attrs)</summary>

```
MOPS {
  domain_id: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpDomainID}  # OCTET STRING, access=r
}
```
</details>

<details><summary>SNMP sources (1/1 attrs)</summary>

```
SNMP {
  domain_id: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.1}  # OCTET STRING, access=r
}
```
</details>

### `delete_mrp()`

**Delete** | **Protocols:** MOPS, SNMP

```
delete_mrp() -> {
    domain_id: "ff:ff:ff:ff:ff:ff:ff:ff:ff:ff:ff:ff:ff:ff:ff:ff"  // str
}
```


<details><summary>MOPS sources (1/1 attrs)</summary>

```
MOPS {
  domain_id: {HM2-L2REDUNDANCY-MIB / hm2MrpEntry.hm2MrpDomainID}  # OCTET STRING, access=r
}
```
</details>

<details><summary>SNMP sources (1/1 attrs)</summary>

```
SNMP {
  domain_id: {oid: 1.3.6.1.4.1.248.11.40.1.1.1.1.1}  # OCTET STRING, access=r
}
```
</details>

---

## mrp_sub_ring

_MRP Sub-Ring (SRM) configuration and status_

### `get_mrp_sub_ring()`

**Read** | **Protocols:** MOPS, SNMP
Primary key: `ring_id`

```
get_mrp_sub_ring() -> {
    enabled: False  // "True" | "False"
    admin_state: "manager"  // "manager" | "redundantManager" | "singleManager"
    oper_state: "disabled"  // "manager" | "redundantManager" | "singleManager" | "disabled"
    vlan: 0  // int
    domain_id: ""  // str
    sub_ring_name: ""  // str
    sub_ring_port: ""  // str (via ifindex)
    sub_ring_port_state: "not-connected"  // "disabled" | "blocked" | "forwarding" | "not-connected"
    sub_ring_state: "undefined"  // "undefined" | "open" | "closed"
    redundancy: False  // "True" | "False"
}
```


<details><summary>MOPS sources (11/11 attrs)</summary>

```
MOPS {
  ring_id: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmRingID}  # Integer32, access=r
  enabled: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmConfigOperState}  # INTEGER, access=r, allowed=['noError', 'ringPortLinkError', 'multipleSRM', 'noPartnerManager', 'concurrentVLAN', 'concurrentPort', 'concurrentRedundancy', 'trunkMember', 'sharedVLAN']
  domain_id: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmMRPDomainID}  # OCTET STRING, access=ru
  sub_ring_name: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmSubRingName}  # SnmpAdminString, access=ru
  admin_state: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmAdminState}  # INTEGER, access=ru, allowed=['manager', 'redundantManager', 'singleManager']
  sub_ring_port: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmSubRingPortIfIndex}  # Integer32, access=ru
  sub_ring_port_state: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmSubRingPortOperState}  # INTEGER, access=r, allowed=['disabled', 'blocked', 'forwarding', 'not-connected']
  sub_ring_state: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmSubRingOperState}  # INTEGER, access=r, allowed=['undefined', 'open', 'closed']
  oper_state: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmOperState}  # INTEGER, access=r, allowed=['manager', 'redundantManager', 'singleManager', 'disabled']
  redundancy: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmRedundancyOperState}  # INTEGER, access=r, allowed=['redGuaranteed', 'redNotGuaranteed']
  vlan: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmVlanID}  # Integer32, access=ru, range=0–4042
}
```
</details>

<details><summary>SNMP sources (11/11 attrs)</summary>

```
SNMP {
  ring_id: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.1}  # Integer32, access=r
  enabled: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.13}  # INTEGER, access=r, allowed=['noError', 'ringPortLinkError', 'multipleSRM', 'noPartnerManager', 'concurrentVLAN', 'concurrentPort', 'concurrentRedundancy', 'trunkMember', 'sharedVLAN']
  domain_id: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.5}  # OCTET STRING, access=ru
  sub_ring_name: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.8}  # SnmpAdminString, access=ru
  admin_state: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.2}  # INTEGER, access=ru, allowed=['manager', 'redundantManager', 'singleManager']
  sub_ring_port: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.9}  # Integer32, access=ru
  sub_ring_port_state: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.10}  # INTEGER, access=r, allowed=['disabled', 'blocked', 'forwarding', 'not-connected']
  sub_ring_state: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.11}  # INTEGER, access=r, allowed=['undefined', 'open', 'closed']
  oper_state: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.3}  # INTEGER, access=r, allowed=['manager', 'redundantManager', 'singleManager', 'disabled']
  redundancy: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.12}  # INTEGER, access=r, allowed=['redGuaranteed', 'redNotGuaranteed']
  vlan: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.4}  # Integer32, access=ru, range=0–4042
}
```
</details>

### `set_mrp_sub_ring()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (12/12 attrs)</summary>

```
MOPS {
  ring_id: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmRingID}  # Integer32, access=r
  enabled: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmConfigOperState}  # INTEGER, access=r, allowed=['noError', 'ringPortLinkError', 'multipleSRM', 'noPartnerManager', 'concurrentVLAN', 'concurrentPort', 'concurrentRedundancy', 'trunkMember', 'sharedVLAN']
  srm_status: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmRowStatus}  # RowStatus, access=crud
  domain_id: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmMRPDomainID}  # OCTET STRING, access=ru
  sub_ring_name: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmSubRingName}  # SnmpAdminString, access=ru
  admin_state: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmAdminState}  # INTEGER, access=ru, allowed=['manager', 'redundantManager', 'singleManager']
  sub_ring_port: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmSubRingPortIfIndex}  # Integer32, access=ru
  sub_ring_port_state: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmSubRingPortOperState}  # INTEGER, access=r, allowed=['disabled', 'blocked', 'forwarding', 'not-connected']
  sub_ring_state: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmSubRingOperState}  # INTEGER, access=r, allowed=['undefined', 'open', 'closed']
  oper_state: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmOperState}  # INTEGER, access=r, allowed=['manager', 'redundantManager', 'singleManager', 'disabled']
  redundancy: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmRedundancyOperState}  # INTEGER, access=r, allowed=['redGuaranteed', 'redNotGuaranteed']
  vlan: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmVlanID}  # Integer32, access=ru, range=0–4042
}
```
</details>

<details><summary>SNMP sources (12/12 attrs)</summary>

```
SNMP {
  ring_id: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.1}  # Integer32, access=r
  enabled: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.13}  # INTEGER, access=r, allowed=['noError', 'ringPortLinkError', 'multipleSRM', 'noPartnerManager', 'concurrentVLAN', 'concurrentPort', 'concurrentRedundancy', 'trunkMember', 'sharedVLAN']
  srm_status: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.20}  # RowStatus, access=crud
  domain_id: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.5}  # OCTET STRING, access=ru
  sub_ring_name: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.8}  # SnmpAdminString, access=ru
  admin_state: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.2}  # INTEGER, access=ru, allowed=['manager', 'redundantManager', 'singleManager']
  sub_ring_port: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.9}  # Integer32, access=ru
  sub_ring_port_state: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.10}  # INTEGER, access=r, allowed=['disabled', 'blocked', 'forwarding', 'not-connected']
  sub_ring_state: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.11}  # INTEGER, access=r, allowed=['undefined', 'open', 'closed']
  oper_state: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.3}  # INTEGER, access=r, allowed=['manager', 'redundantManager', 'singleManager', 'disabled']
  redundancy: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.12}  # INTEGER, access=r, allowed=['redGuaranteed', 'redNotGuaranteed']
  vlan: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.4}  # Integer32, access=ru, range=0–4042
}
```
</details>

### `create_mrp_sub_ring()`

**Create** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (12/12 attrs)</summary>

```
MOPS {
  ring_id: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmRingID}  # Integer32, access=r
  enabled: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmConfigOperState}  # INTEGER, access=r, allowed=['noError', 'ringPortLinkError', 'multipleSRM', 'noPartnerManager', 'concurrentVLAN', 'concurrentPort', 'concurrentRedundancy', 'trunkMember', 'sharedVLAN']
  srm_status: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmRowStatus}  # RowStatus, access=crud
  domain_id: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmMRPDomainID}  # OCTET STRING, access=ru
  sub_ring_name: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmSubRingName}  # SnmpAdminString, access=ru
  admin_state: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmAdminState}  # INTEGER, access=ru, allowed=['manager', 'redundantManager', 'singleManager']
  sub_ring_port: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmSubRingPortIfIndex}  # Integer32, access=ru
  sub_ring_port_state: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmSubRingPortOperState}  # INTEGER, access=r, allowed=['disabled', 'blocked', 'forwarding', 'not-connected']
  sub_ring_state: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmSubRingOperState}  # INTEGER, access=r, allowed=['undefined', 'open', 'closed']
  oper_state: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmOperState}  # INTEGER, access=r, allowed=['manager', 'redundantManager', 'singleManager', 'disabled']
  redundancy: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmRedundancyOperState}  # INTEGER, access=r, allowed=['redGuaranteed', 'redNotGuaranteed']
  vlan: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmVlanID}  # Integer32, access=ru, range=0–4042
}
```
</details>

<details><summary>SNMP sources (12/12 attrs)</summary>

```
SNMP {
  ring_id: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.1}  # Integer32, access=r
  enabled: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.13}  # INTEGER, access=r, allowed=['noError', 'ringPortLinkError', 'multipleSRM', 'noPartnerManager', 'concurrentVLAN', 'concurrentPort', 'concurrentRedundancy', 'trunkMember', 'sharedVLAN']
  srm_status: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.20}  # RowStatus, access=crud
  domain_id: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.5}  # OCTET STRING, access=ru
  sub_ring_name: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.8}  # SnmpAdminString, access=ru
  admin_state: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.2}  # INTEGER, access=ru, allowed=['manager', 'redundantManager', 'singleManager']
  sub_ring_port: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.9}  # Integer32, access=ru
  sub_ring_port_state: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.10}  # INTEGER, access=r, allowed=['disabled', 'blocked', 'forwarding', 'not-connected']
  sub_ring_state: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.11}  # INTEGER, access=r, allowed=['undefined', 'open', 'closed']
  oper_state: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.3}  # INTEGER, access=r, allowed=['manager', 'redundantManager', 'singleManager', 'disabled']
  redundancy: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.12}  # INTEGER, access=r, allowed=['redGuaranteed', 'redNotGuaranteed']
  vlan: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.4}  # Integer32, access=ru, range=0–4042
}
```
</details>

### `delete_mrp_sub_ring()`

**Delete** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (12/12 attrs)</summary>

```
MOPS {
  ring_id: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmRingID}  # Integer32, access=r
  enabled: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmConfigOperState}  # INTEGER, access=r, allowed=['noError', 'ringPortLinkError', 'multipleSRM', 'noPartnerManager', 'concurrentVLAN', 'concurrentPort', 'concurrentRedundancy', 'trunkMember', 'sharedVLAN']
  srm_status: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmRowStatus}  # RowStatus, access=crud
  domain_id: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmMRPDomainID}  # OCTET STRING, access=ru
  sub_ring_name: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmSubRingName}  # SnmpAdminString, access=ru
  admin_state: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmAdminState}  # INTEGER, access=ru, allowed=['manager', 'redundantManager', 'singleManager']
  sub_ring_port: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmSubRingPortIfIndex}  # Integer32, access=ru
  sub_ring_port_state: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmSubRingPortOperState}  # INTEGER, access=r, allowed=['disabled', 'blocked', 'forwarding', 'not-connected']
  sub_ring_state: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmSubRingOperState}  # INTEGER, access=r, allowed=['undefined', 'open', 'closed']
  oper_state: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmOperState}  # INTEGER, access=r, allowed=['manager', 'redundantManager', 'singleManager', 'disabled']
  redundancy: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmRedundancyOperState}  # INTEGER, access=r, allowed=['redGuaranteed', 'redNotGuaranteed']
  vlan: {HM2-L2REDUNDANCY-MIB / hm2SrmEntry.hm2SrmVlanID}  # Integer32, access=ru, range=0–4042
}
```
</details>

<details><summary>SNMP sources (12/12 attrs)</summary>

```
SNMP {
  ring_id: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.1}  # Integer32, access=r
  enabled: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.13}  # INTEGER, access=r, allowed=['noError', 'ringPortLinkError', 'multipleSRM', 'noPartnerManager', 'concurrentVLAN', 'concurrentPort', 'concurrentRedundancy', 'trunkMember', 'sharedVLAN']
  srm_status: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.20}  # RowStatus, access=crud
  domain_id: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.5}  # OCTET STRING, access=ru
  sub_ring_name: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.8}  # SnmpAdminString, access=ru
  admin_state: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.2}  # INTEGER, access=ru, allowed=['manager', 'redundantManager', 'singleManager']
  sub_ring_port: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.9}  # Integer32, access=ru
  sub_ring_port_state: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.10}  # INTEGER, access=r, allowed=['disabled', 'blocked', 'forwarding', 'not-connected']
  sub_ring_state: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.11}  # INTEGER, access=r, allowed=['undefined', 'open', 'closed']
  oper_state: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.3}  # INTEGER, access=r, allowed=['manager', 'redundantManager', 'singleManager', 'disabled']
  redundancy: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.12}  # INTEGER, access=r, allowed=['redGuaranteed', 'redNotGuaranteed']
  vlan: {oid: 1.3.6.1.4.1.248.11.40.1.4.3.1.4}  # Integer32, access=ru, range=0–4042
}
```
</details>

---

## ntp

_NTP/SNTP client configuration and server list_

### `get_ntp()`

**Read** | **Protocols:** MOPS, SNMP, SSH

```
get_ntp() -> {
    enabled: False  // bool
    request_interval: 30  // int
    server_enabled: False  // bool
    server_stratum: 1  // int
    servers: {...}  // dict
}
```

> Sub-table: **`servers`** — key: `address`

<details><summary>MOPS sources (9/9 attrs)</summary>

```
MOPS {
  enabled: {HM2-TIMESYNC-MIB / hm2SntpClientGroup.hm2SntpClientAdminState}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerPort}  # InetPortNumber, access=ru, range=1–65535
  server_enabled: {HM2-TIMESYNC-MIB / hm2NtpServerConfigGroup.hm2NtpServerAdminState}  # HmEnabledStatus, access=ru, allowed=[True, False]
  description: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerDescr}  # DisplayString, access=ru
  servers: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerAddr}  # InetAddress, access=ru
  request_interval: {HM2-TIMESYNC-MIB / hm2SntpClientGroup.hm2SntpClientRequestInterval}  # Integer32, access=ru, range=5–3600
  server_stratum: {HM2-TIMESYNC-MIB / hm2NtpServerConfigGroup.hm2NtpServerLocalClockStratum}  # Integer32 (1..16), access=ru, range=1–16
  address: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerAddr}  # InetAddress, access=ru
  server_oper_status: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerStatus}  # HmSntpClientServerStatus, access=r
}
```
</details>

<details><summary>SNMP sources (9/9 attrs)</summary>

```
SNMP {
  enabled: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.4}  # InetPortNumber, access=ru, range=1–65535
  server_enabled: {oid: 1.3.6.1.4.1.248.11.50.1.3.2.1.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  description: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.5}  # DisplayString, access=ru
  servers: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.3}  # InetAddress, access=ru
  request_interval: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.4, method: get}  # Integer32, access=ru, range=5–3600
  server_stratum: {oid: 1.3.6.1.4.1.248.11.50.1.3.2.1.3, method: get}  # Integer32 (1..16), access=ru, range=1–16
  address: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.3}  # InetAddress, access=ru
  server_oper_status: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.6}  # HmSntpClientServerStatus, access=r
}
```
</details>

<details><summary>SSH sources (3/9 attrs)</summary>

```
SSH {
  enabled: {read: "show sntp client status", write: "{'' if value else 'no '}sntp client operation"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  servers: {read: "show sntp client server", write: "sntp client server add {index} {address}"}  # InetAddress, access=ru
  address: {read: "show sntp client server", write: "sntp client server add {index} {address}"}  # InetAddress, access=ru
}
```
</details>

### `get_ntp_stats()`

**list** | **Protocols:** MOPS, SNMP, SSH
Primary key: `server_index`

```
get_ntp_stats() -> {
    remote: ""  // str
    referenceid: ""  // str
    synchronized: False  // "False" | "True" | "False" | "False" | "False"
    stratum: 0  // int
    type: "-"  // str
    when: ""  // str
    hostpoll: 0  // int
    reachability: 0  // int
    delay: 0.0  // float
    offset: 0.0  // float
    jitter: 0.0  // float
}
```


<details><summary>MOPS sources (3/3 attrs)</summary>

```
MOPS {
  synchronized: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerStatus}  # HmSntpClientServerStatus, access=r
  server_index: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerIndex}  # Integer32, access=r, range=1–4
  remote: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerAddr}  # InetAddress, access=ru
}
```
</details>

<details><summary>SNMP sources (3/3 attrs)</summary>

```
SNMP {
  synchronized: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.6}  # HmSntpClientServerStatus, access=r
  server_index: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.1}  # Integer32, access=r, range=1–4
  remote: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.3}  # InetAddress, access=ru
}
```
</details>

<details><summary>SSH sources (1/3 attrs)</summary>

```
SSH {
  remote: {read: "show sntp client server", write: "sntp client server add {index} {address}"}  # InetAddress, access=ru
}
```
</details>

### `set_ntp()`

**Update** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (15/15 attrs)</summary>

```
MOPS {
  enabled: {HM2-TIMESYNC-MIB / hm2SntpClientGroup.hm2SntpClientAdminState}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerPort}  # InetPortNumber, access=ru, range=1–65535
  remote: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerAddr}  # InetAddress, access=ru
  server_enabled: {HM2-TIMESYNC-MIB / hm2NtpServerConfigGroup.hm2NtpServerAdminState}  # HmEnabledStatus, access=ru, allowed=[True, False]
  synchronized: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerStatus}  # HmSntpClientServerStatus, access=r
  server_index: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerIndex}  # Integer32, access=r, range=1–4
  description: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerDescr}  # DisplayString, access=ru
  request_interval: {HM2-TIMESYNC-MIB / hm2SntpClientGroup.hm2SntpClientRequestInterval}  # Integer32, access=ru, range=5–3600
  servers: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerAddr}  # InetAddress, access=ru
  addr_type: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerAddrType}  # InetAddressType, access=ru
  server_stratum: {HM2-TIMESYNC-MIB / hm2NtpServerConfigGroup.hm2NtpServerLocalClockStratum}  # Integer32 (1..16), access=ru, range=1–16
  address: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerAddr}  # InetAddress, access=ru
  client_status: {HM2-TIMESYNC-MIB / hm2SntpClientGroup.hm2SntpClientStatus}  # INTEGER, access=r, allowed=['disabled', 'notSynchronized', 'synchronizedToRemoteServer']
  server_oper_status: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerStatus}  # HmSntpClientServerStatus, access=r
  server_row_status: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerRowStatus}  # RowStatus, access=crud
}
```
</details>

<details><summary>SNMP sources (15/15 attrs)</summary>

```
SNMP {
  enabled: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.4}  # InetPortNumber, access=ru, range=1–65535
  remote: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.3}  # InetAddress, access=ru
  server_enabled: {oid: 1.3.6.1.4.1.248.11.50.1.3.2.1.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  synchronized: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.6}  # HmSntpClientServerStatus, access=r
  server_index: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.1}  # Integer32, access=r, range=1–4
  description: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.5}  # DisplayString, access=ru
  request_interval: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.4, method: get}  # Integer32, access=ru, range=5–3600
  servers: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.3}  # InetAddress, access=ru
  addr_type: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.2}  # InetAddressType, access=ru
  server_stratum: {oid: 1.3.6.1.4.1.248.11.50.1.3.2.1.3, method: get}  # Integer32 (1..16), access=ru, range=1–16
  address: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.3}  # InetAddress, access=ru
  client_status: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.5, method: get}  # INTEGER, access=r, allowed=['disabled', 'notSynchronized', 'synchronizedToRemoteServer']
  server_oper_status: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.6}  # HmSntpClientServerStatus, access=r
  server_row_status: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.7}  # RowStatus, access=crud
}
```
</details>

<details><summary>SSH sources (5/15 attrs)</summary>

```
SSH {
  enabled: {read: "show sntp client status", write: "{'' if value else 'no '}sntp client operation"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  remote: {read: "show sntp client server", write: "sntp client server add {index} {address}"}  # InetAddress, access=ru
  servers: {read: "show sntp client server", write: "sntp client server add {index} {address}"}  # InetAddress, access=ru
  address: {read: "show sntp client server", write: "sntp client server add {index} {address}"}  # InetAddress, access=ru
  server_row_status: {write: "sntp client server add {index} {address}"}  # RowStatus, access=crud
}
```
</details>

### `get_ntp_servers()`

**Read** | **Protocols:** MOPS, SNMP, SSH
Primary key: `server_index`

```
get_ntp_servers() -> {
    address: ""  // str
    port: 123  // int
    description: ""  // str
    status: ""  // str
}
```


<details><summary>MOPS sources (4/4 attrs)</summary>

```
MOPS {
  port: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerPort}  # InetPortNumber, access=ru, range=1–65535
  description: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerDescr}  # DisplayString, access=ru
  server_index: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerIndex}  # Integer32, access=r, range=1–4
  address: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerAddr}  # InetAddress, access=ru
}
```
</details>

<details><summary>SNMP sources (4/4 attrs)</summary>

```
SNMP {
  port: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.4}  # InetPortNumber, access=ru, range=1–65535
  description: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.5}  # DisplayString, access=ru
  server_index: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.1}  # Integer32, access=r, range=1–4
  address: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.3}  # InetAddress, access=ru
}
```
</details>

<details><summary>SSH sources (1/4 attrs)</summary>

```
SSH {
  address: {read: "show sntp client server", write: "sntp client server add {index} {address}"}  # InetAddress, access=ru
}
```
</details>

### `create_ntp_server()`

**Create** | **Protocols:** MOPS, SNMP, SSH
Required: `address`

```
create_ntp_server() -> {
    addr_type: 1  // int
}
```


<details><summary>MOPS sources (2/2 attrs)</summary>

```
MOPS {
  address: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerAddr}  # InetAddress, access=ru
  addr_type: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerAddrType}  # InetAddressType, access=ru
}
```
</details>

<details><summary>SNMP sources (2/2 attrs)</summary>

```
SNMP {
  address: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.3}  # InetAddress, access=ru
  addr_type: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.2}  # InetAddressType, access=ru
}
```
</details>

<details><summary>SSH sources (1/2 attrs)</summary>

```
SSH {
  address: {read: "show sntp client server", write: "sntp client server add {index} {address}"}  # InetAddress, access=ru
}
```
</details>

### `delete_ntp_server()`

**Delete** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (15/15 attrs)</summary>

```
MOPS {
  enabled: {HM2-TIMESYNC-MIB / hm2SntpClientGroup.hm2SntpClientAdminState}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerPort}  # InetPortNumber, access=ru, range=1–65535
  remote: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerAddr}  # InetAddress, access=ru
  server_enabled: {HM2-TIMESYNC-MIB / hm2NtpServerConfigGroup.hm2NtpServerAdminState}  # HmEnabledStatus, access=ru, allowed=[True, False]
  synchronized: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerStatus}  # HmSntpClientServerStatus, access=r
  server_index: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerIndex}  # Integer32, access=r, range=1–4
  description: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerDescr}  # DisplayString, access=ru
  request_interval: {HM2-TIMESYNC-MIB / hm2SntpClientGroup.hm2SntpClientRequestInterval}  # Integer32, access=ru, range=5–3600
  servers: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerAddr}  # InetAddress, access=ru
  addr_type: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerAddrType}  # InetAddressType, access=ru
  server_stratum: {HM2-TIMESYNC-MIB / hm2NtpServerConfigGroup.hm2NtpServerLocalClockStratum}  # Integer32 (1..16), access=ru, range=1–16
  address: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerAddr}  # InetAddress, access=ru
  client_status: {HM2-TIMESYNC-MIB / hm2SntpClientGroup.hm2SntpClientStatus}  # INTEGER, access=r, allowed=['disabled', 'notSynchronized', 'synchronizedToRemoteServer']
  server_oper_status: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerStatus}  # HmSntpClientServerStatus, access=r
  server_row_status: {HM2-TIMESYNC-MIB / hm2SntpClientServerAddrEntry.hm2SntpClientServerRowStatus}  # RowStatus, access=crud
}
```
</details>

<details><summary>SNMP sources (15/15 attrs)</summary>

```
SNMP {
  enabled: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.4}  # InetPortNumber, access=ru, range=1–65535
  remote: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.3}  # InetAddress, access=ru
  server_enabled: {oid: 1.3.6.1.4.1.248.11.50.1.3.2.1.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  synchronized: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.6}  # HmSntpClientServerStatus, access=r
  server_index: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.1}  # Integer32, access=r, range=1–4
  description: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.5}  # DisplayString, access=ru
  request_interval: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.4, method: get}  # Integer32, access=ru, range=5–3600
  servers: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.3}  # InetAddress, access=ru
  addr_type: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.2}  # InetAddressType, access=ru
  server_stratum: {oid: 1.3.6.1.4.1.248.11.50.1.3.2.1.3, method: get}  # Integer32 (1..16), access=ru, range=1–16
  address: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.3}  # InetAddress, access=ru
  client_status: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.5, method: get}  # INTEGER, access=r, allowed=['disabled', 'notSynchronized', 'synchronizedToRemoteServer']
  server_oper_status: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.6}  # HmSntpClientServerStatus, access=r
  server_row_status: {oid: 1.3.6.1.4.1.248.11.50.1.2.3.10.1.7}  # RowStatus, access=crud
}
```
</details>

<details><summary>SSH sources (5/15 attrs)</summary>

```
SSH {
  enabled: {read: "show sntp client status", write: "{'' if value else 'no '}sntp client operation"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  remote: {read: "show sntp client server", write: "sntp client server add {index} {address}"}  # InetAddress, access=ru
  servers: {read: "show sntp client server", write: "sntp client server add {index} {address}"}  # InetAddress, access=ru
  address: {read: "show sntp client server", write: "sntp client server add {index} {address}"}  # InetAddress, access=ru
  server_row_status: {write: "sntp client server add {index} {address}"}  # RowStatus, access=crud
}
```
</details>

---

## optics

_SFP Transceiver digital diagnostics (DDM)_

### `get_optics()`

**Read** | **Protocols:** MOPS, SNMP
Primary key: `name` | Key map: `ifindex`

```
get_optics() -> {
    tx_power: 0.0  // float
    rx_power: 0.0  // float
    temperature: 0.0  // float
}
```


<details><summary>MOPS sources (4/4 attrs)</summary>

```
MOPS {
  temperature: {HM2-DEVMGMT-MIB / hm2SfpDiagEntry.hm2SfpCurrentTemperature}  # Integer32, access=r
  rx_power: {HM2-DEVMGMT-MIB / hm2SfpDiagEntry.hm2SfpCurrentRxPower}  # Integer32, access=r
  name: {IF-MIB / ifXEntry.ifName}  # DisplayString, access=r
  tx_power: {HM2-DEVMGMT-MIB / hm2SfpDiagEntry.hm2SfpCurrentTxPower}  # Integer32, access=r
}
```
</details>

<details><summary>SNMP sources (4/4 attrs)</summary>

```
SNMP {
  temperature: {oid: 1.3.6.1.4.1.248.11.10.1.7.2.1.2}  # Integer32, access=r
  rx_power: {oid: 1.3.6.1.4.1.248.11.10.1.7.2.1.4}  # Integer32, access=r
  name: {oid: 1.3.6.1.2.1.31.1.1.1.1}  # DisplayString, access=r
  tx_power: {oid: 1.3.6.1.4.1.248.11.10.1.7.2.1.3}  # Integer32, access=r
}
```
</details>

---

## poe

_Power over Ethernet (PoE) status and configuration_

### `get_poe()`

**Read** | **Protocols:** MOPS, SNMP
Primary key: `name`

```
get_poe() -> {
    enabled: False  // bool
    power_limit: 0.0  // float
    status: "searching"  // str
}
```


<details><summary>MOPS sources (3/3 attrs)</summary>

```
MOPS {
  power_limit: {HM2-POE-MIB / hm2PoeMgmtPortEntry.hm2PoeMgmtPortPowerLimit}  # Integer32 (0..30000), access=ru, range=0–30000
  enabled: {HM2-POE-MIB / hm2PoeMgmtPortEntry.hm2PoeMgmtPortAdminEnable}  # HmEnabledStatus, access=ru, allowed=[True, False]
  status: {HM2-POE-MIB / hm2PoeMgmtPortEntry.hm2PoeMgmtPortDetectionStatus}  # INTEGER, access=r, allowed=['disabled', 'searching', 'deliveringPower', 'fault', 'test', 'otherFault']
}
```
</details>

<details><summary>SNMP sources (3/3 attrs)</summary>

```
SNMP {
  power_limit: {oid: 1.3.6.1.4.1.248.11.12.1.1.3.1.14}  # Integer32 (0..30000), access=ru, range=0–30000
  enabled: {oid: 1.3.6.1.4.1.248.11.12.1.1.3.1.1}  # HmEnabledStatus, access=ru, allowed=[True, False]
  status: {oid: 1.3.6.1.4.1.248.11.12.1.1.3.1.3}  # INTEGER, access=r, allowed=['disabled', 'searching', 'deliveringPower', 'fault', 'test', 'otherFault']
}
```
</details>

### `set_poe()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (3/3 attrs)</summary>

```
MOPS {
  power_limit: {HM2-POE-MIB / hm2PoeMgmtPortEntry.hm2PoeMgmtPortPowerLimit}  # Integer32 (0..30000), access=ru, range=0–30000
  enabled: {HM2-POE-MIB / hm2PoeMgmtPortEntry.hm2PoeMgmtPortAdminEnable}  # HmEnabledStatus, access=ru, allowed=[True, False]
  status: {HM2-POE-MIB / hm2PoeMgmtPortEntry.hm2PoeMgmtPortDetectionStatus}  # INTEGER, access=r, allowed=['disabled', 'searching', 'deliveringPower', 'fault', 'test', 'otherFault']
}
```
</details>

<details><summary>SNMP sources (3/3 attrs)</summary>

```
SNMP {
  power_limit: {oid: 1.3.6.1.4.1.248.11.12.1.1.3.1.14}  # Integer32 (0..30000), access=ru, range=0–30000
  enabled: {oid: 1.3.6.1.4.1.248.11.12.1.1.3.1.1}  # HmEnabledStatus, access=ru, allowed=[True, False]
  status: {oid: 1.3.6.1.4.1.248.11.12.1.1.3.1.3}  # INTEGER, access=r, allowed=['disabled', 'searching', 'deliveringPower', 'fault', 'test', 'otherFault']
}
```
</details>

---

## port_security

_Port Security (MAC limiting) per-port configuration_

### `get_port_security()`

**Read** | **Protocols:** MOPS, SNMP, SSH

```
get_port_security() -> {
    global_enabled: False  // bool
    mode: ""  // "mac-based" | "ip-based"
    auto_disable_enabled: False  // "mac-based-port-security"
    ports: {...}  // dict
}
```

> Sub-table: **`ports`** — key: `enabled`, map: `ifindex`

<details><summary>MOPS sources (12/12 attrs)</summary>

```
MOPS {
  mode: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityGroup.hm2AgentPortSecurityOperationMode}  # INTEGER, access=ru, allowed=['macAddressBased', 'ipAddressBased']
  enabled: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  static_limit: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityStaticLimit}  # Unsigned32, access=ru, range=0–64
  auto_disable_enabled: {HM2-DEVMGMT-MIB / hm2AutoDisableReasonEntry.hm2AutoDisableReasonOperation}  # HmEnabledStatus, access=ru, allowed=[True, False]
  dynamic_limit: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityDynamicLimit}  # Unsigned32, access=ru, range=0–600
  violation_trap_frequency: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityViolationTrapFrequency}  # Unsigned32, access=ru, range=0–3600
  auto_disable: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityAutoDisable}  # TruthValue, access=ru, allowed=[True, False]
  static_count: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityStaticCount}  # Unsigned32, access=r
  last_discarded_mac: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityLastDiscardedMAC}  # DisplayString, access=r
  violation_trap_mode: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityViolationTrapMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  dynamic_count: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityDynamicCount}  # Unsigned32, access=r
  global_enabled: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityGroup.hm2AgentGlobalPortSecurityMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (12/12 attrs)</summary>

```
SNMP {
  mode: {oid: 1.3.6.1.4.1.248.12.20.1.12, method: get}  # INTEGER, access=ru, allowed=['macAddressBased', 'ipAddressBased']
  enabled: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.1}  # HmEnabledStatus, access=ru, allowed=[True, False]
  static_limit: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.3}  # Unsigned32, access=ru, range=0–64
  auto_disable_enabled: {oid: 1.3.6.1.4.1.248.11.10.1.9.2.1.2}  # HmEnabledStatus, access=ru, allowed=[True, False]
  dynamic_limit: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.2}  # Unsigned32, access=ru, range=0–600
  violation_trap_frequency: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.23}  # Unsigned32, access=ru, range=0–3600
  auto_disable: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.248}  # TruthValue, access=ru, allowed=[True, False]
  static_count: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.21}  # Unsigned32, access=r
  last_discarded_mac: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.7}  # DisplayString, access=r
  violation_trap_mode: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.4}  # HmEnabledStatus, access=ru, allowed=[True, False]
  dynamic_count: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.20}  # Unsigned32, access=r
  global_enabled: {oid: 1.3.6.1.4.1.248.12.20.1.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SSH sources (4/12 attrs)</summary>

```
SSH {
  enabled: {read: "show port-security interface", write: "{'' if value else 'no '}port-security operation"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  static_limit: {read: "show port-security interface", write: "port-security max-static {value}"}  # Unsigned32, access=ru, range=0–64
  dynamic_limit: {read: "show port-security interface", write: "port-security dynamic-limit {value}"}  # Unsigned32, access=ru, range=0–600
  global_enabled: {read: "show port-security global", write: "{'' if value else 'no '}port-security operation"}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

### `set_port_security()`

**Update** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (19/19 attrs)</summary>

```
MOPS {
  static_limit: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityStaticLimit}  # Unsigned32, access=ru, range=0–64
  static_ip_count: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityStaticIpCount}  # Unsigned32, access=r
  auto_disable_enabled: {HM2-DEVMGMT-MIB / hm2AutoDisableReasonEntry.hm2AutoDisableReasonOperation}  # HmEnabledStatus, access=ru, allowed=[True, False]
  global_enabled: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityGroup.hm2AgentGlobalPortSecurityMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mode: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityGroup.hm2AgentPortSecurityOperationMode}  # INTEGER, access=ru, allowed=['macAddressBased', 'ipAddressBased']
  enabled: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ip_remove: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityIPAddressRemove}  # DisplayString, access=ru
  ip_add: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityIPAddressAdd}  # DisplayString, access=ru
  static_ips: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityStaticIPs}  # DisplayString, access=r, range=0–1536
  mac_remove: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityMACAddressRemove}  # DisplayString, access=ru
  dynamic_count: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityDynamicCount}  # Unsigned32, access=r
  dynamic_limit: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityDynamicLimit}  # Unsigned32, access=ru, range=0–600
  auto_disable: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityAutoDisable}  # TruthValue, access=ru, allowed=[True, False]
  violation_trap_mode: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityViolationTrapMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  static_macs: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityStaticMACs}  # DisplayString, access=r, range=0–1536
  mac_add: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityMACAddressAdd}  # DisplayString, access=ru
  violation_trap_frequency: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityViolationTrapFrequency}  # Unsigned32, access=ru, range=0–3600
  static_count: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityStaticCount}  # Unsigned32, access=r
  last_discarded_mac: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityLastDiscardedMAC}  # DisplayString, access=r
}
```
</details>

<details><summary>SNMP sources (19/19 attrs)</summary>

```
SNMP {
  static_limit: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.3}  # Unsigned32, access=ru, range=0–64
  static_ip_count: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.249}  # Unsigned32, access=r
  auto_disable_enabled: {oid: 1.3.6.1.4.1.248.11.10.1.9.2.1.2}  # HmEnabledStatus, access=ru, allowed=[True, False]
  global_enabled: {oid: 1.3.6.1.4.1.248.12.20.1.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mode: {oid: 1.3.6.1.4.1.248.12.20.1.12, method: get}  # INTEGER, access=ru, allowed=['macAddressBased', 'ipAddressBased']
  enabled: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.1}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ip_remove: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.252}  # DisplayString, access=ru
  ip_add: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.251}  # DisplayString, access=ru
  static_ips: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.250}  # DisplayString, access=r, range=0–1536
  mac_remove: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.9}  # DisplayString, access=ru
  dynamic_count: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.20}  # Unsigned32, access=r
  dynamic_limit: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.2}  # Unsigned32, access=ru, range=0–600
  auto_disable: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.248}  # TruthValue, access=ru, allowed=[True, False]
  violation_trap_mode: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.4}  # HmEnabledStatus, access=ru, allowed=[True, False]
  static_macs: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.6}  # DisplayString, access=r, range=0–1536
  mac_add: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.8}  # DisplayString, access=ru
  violation_trap_frequency: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.23}  # Unsigned32, access=ru, range=0–3600
  static_count: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.21}  # Unsigned32, access=r
  last_discarded_mac: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.7}  # DisplayString, access=r
}
```
</details>

<details><summary>SSH sources (4/19 attrs)</summary>

```
SSH {
  static_limit: {read: "show port-security interface", write: "port-security max-static {value}"}  # Unsigned32, access=ru, range=0–64
  global_enabled: {read: "show port-security global", write: "{'' if value else 'no '}port-security operation"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  enabled: {read: "show port-security interface", write: "{'' if value else 'no '}port-security operation"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  dynamic_limit: {read: "show port-security interface", write: "port-security dynamic-limit {value}"}  # Unsigned32, access=ru, range=0–600
}
```
</details>

### `create_port_security()`

**Update** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (19/19 attrs)</summary>

```
MOPS {
  static_limit: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityStaticLimit}  # Unsigned32, access=ru, range=0–64
  static_ip_count: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityStaticIpCount}  # Unsigned32, access=r
  auto_disable_enabled: {HM2-DEVMGMT-MIB / hm2AutoDisableReasonEntry.hm2AutoDisableReasonOperation}  # HmEnabledStatus, access=ru, allowed=[True, False]
  global_enabled: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityGroup.hm2AgentGlobalPortSecurityMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mode: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityGroup.hm2AgentPortSecurityOperationMode}  # INTEGER, access=ru, allowed=['macAddressBased', 'ipAddressBased']
  enabled: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ip_remove: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityIPAddressRemove}  # DisplayString, access=ru
  ip_add: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityIPAddressAdd}  # DisplayString, access=ru
  static_ips: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityStaticIPs}  # DisplayString, access=r, range=0–1536
  mac_remove: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityMACAddressRemove}  # DisplayString, access=ru
  dynamic_count: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityDynamicCount}  # Unsigned32, access=r
  dynamic_limit: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityDynamicLimit}  # Unsigned32, access=ru, range=0–600
  auto_disable: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityAutoDisable}  # TruthValue, access=ru, allowed=[True, False]
  violation_trap_mode: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityViolationTrapMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  static_macs: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityStaticMACs}  # DisplayString, access=r, range=0–1536
  mac_add: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityMACAddressAdd}  # DisplayString, access=ru
  violation_trap_frequency: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityViolationTrapFrequency}  # Unsigned32, access=ru, range=0–3600
  static_count: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityStaticCount}  # Unsigned32, access=r
  last_discarded_mac: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityLastDiscardedMAC}  # DisplayString, access=r
}
```
</details>

<details><summary>SNMP sources (19/19 attrs)</summary>

```
SNMP {
  static_limit: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.3}  # Unsigned32, access=ru, range=0–64
  static_ip_count: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.249}  # Unsigned32, access=r
  auto_disable_enabled: {oid: 1.3.6.1.4.1.248.11.10.1.9.2.1.2}  # HmEnabledStatus, access=ru, allowed=[True, False]
  global_enabled: {oid: 1.3.6.1.4.1.248.12.20.1.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mode: {oid: 1.3.6.1.4.1.248.12.20.1.12, method: get}  # INTEGER, access=ru, allowed=['macAddressBased', 'ipAddressBased']
  enabled: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.1}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ip_remove: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.252}  # DisplayString, access=ru
  ip_add: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.251}  # DisplayString, access=ru
  static_ips: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.250}  # DisplayString, access=r, range=0–1536
  mac_remove: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.9}  # DisplayString, access=ru
  dynamic_count: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.20}  # Unsigned32, access=r
  dynamic_limit: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.2}  # Unsigned32, access=ru, range=0–600
  auto_disable: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.248}  # TruthValue, access=ru, allowed=[True, False]
  violation_trap_mode: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.4}  # HmEnabledStatus, access=ru, allowed=[True, False]
  static_macs: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.6}  # DisplayString, access=r, range=0–1536
  mac_add: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.8}  # DisplayString, access=ru
  violation_trap_frequency: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.23}  # Unsigned32, access=ru, range=0–3600
  static_count: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.21}  # Unsigned32, access=r
  last_discarded_mac: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.7}  # DisplayString, access=r
}
```
</details>

<details><summary>SSH sources (4/19 attrs)</summary>

```
SSH {
  static_limit: {read: "show port-security interface", write: "port-security max-static {value}"}  # Unsigned32, access=ru, range=0–64
  global_enabled: {read: "show port-security global", write: "{'' if value else 'no '}port-security operation"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  enabled: {read: "show port-security interface", write: "{'' if value else 'no '}port-security operation"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  dynamic_limit: {read: "show port-security interface", write: "port-security dynamic-limit {value}"}  # Unsigned32, access=ru, range=0–600
}
```
</details>

### `delete_port_security()`

**Update** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (19/19 attrs)</summary>

```
MOPS {
  static_limit: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityStaticLimit}  # Unsigned32, access=ru, range=0–64
  static_ip_count: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityStaticIpCount}  # Unsigned32, access=r
  auto_disable_enabled: {HM2-DEVMGMT-MIB / hm2AutoDisableReasonEntry.hm2AutoDisableReasonOperation}  # HmEnabledStatus, access=ru, allowed=[True, False]
  global_enabled: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityGroup.hm2AgentGlobalPortSecurityMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mode: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityGroup.hm2AgentPortSecurityOperationMode}  # INTEGER, access=ru, allowed=['macAddressBased', 'ipAddressBased']
  enabled: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ip_remove: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityIPAddressRemove}  # DisplayString, access=ru
  ip_add: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityIPAddressAdd}  # DisplayString, access=ru
  static_ips: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityStaticIPs}  # DisplayString, access=r, range=0–1536
  mac_remove: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityMACAddressRemove}  # DisplayString, access=ru
  dynamic_count: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityDynamicCount}  # Unsigned32, access=r
  dynamic_limit: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityDynamicLimit}  # Unsigned32, access=ru, range=0–600
  auto_disable: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityAutoDisable}  # TruthValue, access=ru, allowed=[True, False]
  violation_trap_mode: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityViolationTrapMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  static_macs: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityStaticMACs}  # DisplayString, access=r, range=0–1536
  mac_add: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityMACAddressAdd}  # DisplayString, access=ru
  violation_trap_frequency: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityViolationTrapFrequency}  # Unsigned32, access=ru, range=0–3600
  static_count: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityStaticCount}  # Unsigned32, access=r
  last_discarded_mac: {HM2-PLATFORM-PORTSECURITY-MIB / hm2AgentPortSecurityEntry.hm2AgentPortSecurityLastDiscardedMAC}  # DisplayString, access=r
}
```
</details>

<details><summary>SNMP sources (19/19 attrs)</summary>

```
SNMP {
  static_limit: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.3}  # Unsigned32, access=ru, range=0–64
  static_ip_count: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.249}  # Unsigned32, access=r
  auto_disable_enabled: {oid: 1.3.6.1.4.1.248.11.10.1.9.2.1.2}  # HmEnabledStatus, access=ru, allowed=[True, False]
  global_enabled: {oid: 1.3.6.1.4.1.248.12.20.1.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mode: {oid: 1.3.6.1.4.1.248.12.20.1.12, method: get}  # INTEGER, access=ru, allowed=['macAddressBased', 'ipAddressBased']
  enabled: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.1}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ip_remove: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.252}  # DisplayString, access=ru
  ip_add: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.251}  # DisplayString, access=ru
  static_ips: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.250}  # DisplayString, access=r, range=0–1536
  mac_remove: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.9}  # DisplayString, access=ru
  dynamic_count: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.20}  # Unsigned32, access=r
  dynamic_limit: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.2}  # Unsigned32, access=ru, range=0–600
  auto_disable: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.248}  # TruthValue, access=ru, allowed=[True, False]
  violation_trap_mode: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.4}  # HmEnabledStatus, access=ru, allowed=[True, False]
  static_macs: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.6}  # DisplayString, access=r, range=0–1536
  mac_add: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.8}  # DisplayString, access=ru
  violation_trap_frequency: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.23}  # Unsigned32, access=ru, range=0–3600
  static_count: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.21}  # Unsigned32, access=r
  last_discarded_mac: {oid: 1.3.6.1.4.1.248.12.20.1.2.1.7}  # DisplayString, access=r
}
```
</details>

<details><summary>SSH sources (4/19 attrs)</summary>

```
SSH {
  static_limit: {read: "show port-security interface", write: "port-security max-static {value}"}  # Unsigned32, access=ru, range=0–64
  global_enabled: {read: "show port-security global", write: "{'' if value else 'no '}port-security operation"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  enabled: {read: "show port-security interface", write: "{'' if value else 'no '}port-security operation"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  dynamic_limit: {read: "show port-security interface", write: "port-security dynamic-limit {value}"}  # Unsigned32, access=ru, range=0–600
}
```
</details>

---

## profile

_Device configuration profiles (NVM/ENVM)_

### `get_profiles()`

**Read** | **Protocols:** MOPS, SNMP, SSH
Primary key: `index`

```
get_profiles() -> {
    name: ""  // str
    active: False  // "True" | "False" | "True" | "False"
    fingerprint: ""  // str
    firmware_version: ""  // str (computed)
    datetime: ""  // str
    fingerprint_verified: False  // bool
    encrypted: False  // bool
    encryption_verified: False  // bool
}
```


<details><summary>MOPS sources (8/9 attrs)</summary>

```
MOPS {
  encryption_verified: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileEncryptionVerified}  # TruthValue, access=r, allowed=[True, False]
  fingerprint_verified: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileFingerprintVerified}  # TruthValue, access=r, allowed=[True, False]
  active: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileActive}  # INTEGER, access=ru, allowed=['active', 'inactive']
  encrypted: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileEncryptionActive}  # TruthValue, access=r, allowed=[True, False]
  fingerprint: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileFingerprint}  # DisplayString (SIZE(40)), access=r
  index: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileIndex}  # Integer32 (1..100), access=r, range=1–100
  datetime: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileDateTime}  # HmTimeSeconds1970, access=r
  name: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileName}  # DisplayString (SIZE(0..32)), access=r, range=0–32
}
```
</details>

<details><summary>SNMP sources (8/9 attrs)</summary>

```
SNMP {
  encryption_verified: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.9}  # TruthValue, access=r, allowed=[True, False]
  fingerprint_verified: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.14}  # TruthValue, access=r, allowed=[True, False]
  active: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.5}  # INTEGER, access=ru, allowed=['active', 'inactive']
  encrypted: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.8}  # TruthValue, access=r, allowed=[True, False]
  fingerprint: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.13}  # DisplayString (SIZE(40)), access=r
  index: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.2}  # Integer32 (1..100), access=r, range=1–100
  datetime: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.4}  # HmTimeSeconds1970, access=r
  name: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.3}  # DisplayString (SIZE(0..32)), access=r, range=0–32
}
```
</details>

<details><summary>SSH sources (8/9 attrs)</summary>

```
SSH {
  encryption_verified: {read: "show config profiles nvm"}  # TruthValue, access=r, allowed=[True, False]
  fingerprint_verified: {read: "show config profiles nvm"}  # TruthValue, access=r, allowed=[True, False]
  active: {read: "show config profiles nvm", write: "config profile select nvm {_row_index}"}  # INTEGER, access=ru, allowed=['active', 'inactive']
  encrypted: {read: "show config profiles nvm"}  # TruthValue, access=r, allowed=[True, False]
  fingerprint: {read: "show config profiles nvm"}  # DisplayString (SIZE(40)), access=r
  index: {read: "show config profiles nvm"}  # Integer32 (1..100), access=r, range=1–100
  datetime: {read: "show config profiles nvm"}  # HmTimeSeconds1970, access=r
  name: {read: "show config profiles nvm"}  # DisplayString (SIZE(0..32)), access=r, range=0–32
}
```
</details>

### `activate_profile()`

**Update** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (13/14 attrs)</summary>

```
MOPS {
  sw_minor: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileSwMinorRelNum}  # Integer32, access=r
  encryption_verified: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileEncryptionVerified}  # TruthValue, access=r, allowed=[True, False]
  storage_type: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileStorageType}  # INTEGER, access=r, allowed=['nvm', 'envm']
  fingerprint_verified: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileFingerprintVerified}  # TruthValue, access=r, allowed=[True, False]
  sw_bugfix: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileSwBugfixRelNum}  # Integer32, access=r
  active: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileActive}  # INTEGER, access=ru, allowed=['active', 'inactive']
  sw_major: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileSwMajorRelNum}  # Integer32, access=r
  encrypted: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileEncryptionActive}  # TruthValue, access=r, allowed=[True, False]
  fingerprint: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileFingerprint}  # DisplayString (SIZE(40)), access=r
  profile_action: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileAction}  # INTEGER, access=ru
  index: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileIndex}  # Integer32 (1..100), access=r, range=1–100
  datetime: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileDateTime}  # HmTimeSeconds1970, access=r
  name: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileName}  # DisplayString (SIZE(0..32)), access=r, range=0–32
}
```
</details>

<details><summary>SNMP sources (13/14 attrs)</summary>

```
SNMP {
  sw_minor: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.11}  # Integer32, access=r
  encryption_verified: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.9}  # TruthValue, access=r, allowed=[True, False]
  storage_type: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.1}  # INTEGER, access=r, allowed=['nvm', 'envm']
  fingerprint_verified: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.14}  # TruthValue, access=r, allowed=[True, False]
  sw_bugfix: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.12}  # Integer32, access=r
  active: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.5}  # INTEGER, access=ru, allowed=['active', 'inactive']
  sw_major: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.10}  # Integer32, access=r
  encrypted: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.8}  # TruthValue, access=r, allowed=[True, False]
  fingerprint: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.13}  # DisplayString (SIZE(40)), access=r
  profile_action: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.6}  # INTEGER, access=ru
  index: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.2}  # Integer32 (1..100), access=r, range=1–100
  datetime: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.4}  # HmTimeSeconds1970, access=r
  name: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.3}  # DisplayString (SIZE(0..32)), access=r, range=0–32
}
```
</details>

<details><summary>SSH sources (10/14 attrs)</summary>

```
SSH {
  encryption_verified: {read: "show config profiles nvm"}  # TruthValue, access=r, allowed=[True, False]
  fingerprint_verified: {read: "show config profiles nvm"}  # TruthValue, access=r, allowed=[True, False]
  active: {read: "show config profiles nvm", write: "config profile select nvm {_row_index}"}  # INTEGER, access=ru, allowed=['active', 'inactive']
  sw_major: {read: "show config profiles nvm"}  # Integer32, access=r
  encrypted: {read: "show config profiles nvm"}  # TruthValue, access=r, allowed=[True, False]
  fingerprint: {read: "show config profiles nvm"}  # DisplayString (SIZE(40)), access=r
  profile_action: {write: "config profile delete nvm num {_row_index}"}  # INTEGER, access=ru
  index: {read: "show config profiles nvm"}  # Integer32 (1..100), access=r, range=1–100
  datetime: {read: "show config profiles nvm"}  # HmTimeSeconds1970, access=r
  name: {read: "show config profiles nvm"}  # DisplayString (SIZE(0..32)), access=r, range=0–32
}
```
</details>

### `delete_profile()`

**Update** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (13/14 attrs)</summary>

```
MOPS {
  sw_minor: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileSwMinorRelNum}  # Integer32, access=r
  encryption_verified: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileEncryptionVerified}  # TruthValue, access=r, allowed=[True, False]
  storage_type: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileStorageType}  # INTEGER, access=r, allowed=['nvm', 'envm']
  fingerprint_verified: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileFingerprintVerified}  # TruthValue, access=r, allowed=[True, False]
  sw_bugfix: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileSwBugfixRelNum}  # Integer32, access=r
  active: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileActive}  # INTEGER, access=ru, allowed=['active', 'inactive']
  sw_major: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileSwMajorRelNum}  # Integer32, access=r
  encrypted: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileEncryptionActive}  # TruthValue, access=r, allowed=[True, False]
  fingerprint: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileFingerprint}  # DisplayString (SIZE(40)), access=r
  profile_action: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileAction}  # INTEGER, access=ru
  index: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileIndex}  # Integer32 (1..100), access=r, range=1–100
  datetime: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileDateTime}  # HmTimeSeconds1970, access=r
  name: {HM2-FILEMGMT-MIB / hm2FMProfileEntry.hm2FMProfileName}  # DisplayString (SIZE(0..32)), access=r, range=0–32
}
```
</details>

<details><summary>SNMP sources (13/14 attrs)</summary>

```
SNMP {
  sw_minor: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.11}  # Integer32, access=r
  encryption_verified: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.9}  # TruthValue, access=r, allowed=[True, False]
  storage_type: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.1}  # INTEGER, access=r, allowed=['nvm', 'envm']
  fingerprint_verified: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.14}  # TruthValue, access=r, allowed=[True, False]
  sw_bugfix: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.12}  # Integer32, access=r
  active: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.5}  # INTEGER, access=ru, allowed=['active', 'inactive']
  sw_major: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.10}  # Integer32, access=r
  encrypted: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.8}  # TruthValue, access=r, allowed=[True, False]
  fingerprint: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.13}  # DisplayString (SIZE(40)), access=r
  profile_action: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.6}  # INTEGER, access=ru
  index: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.2}  # Integer32 (1..100), access=r, range=1–100
  datetime: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.4}  # HmTimeSeconds1970, access=r
  name: {oid: 1.3.6.1.4.1.248.11.21.1.1.1.1.3}  # DisplayString (SIZE(0..32)), access=r, range=0–32
}
```
</details>

<details><summary>SSH sources (10/14 attrs)</summary>

```
SSH {
  encryption_verified: {read: "show config profiles nvm"}  # TruthValue, access=r, allowed=[True, False]
  fingerprint_verified: {read: "show config profiles nvm"}  # TruthValue, access=r, allowed=[True, False]
  active: {read: "show config profiles nvm", write: "config profile select nvm {_row_index}"}  # INTEGER, access=ru, allowed=['active', 'inactive']
  sw_major: {read: "show config profiles nvm"}  # Integer32, access=r
  encrypted: {read: "show config profiles nvm"}  # TruthValue, access=r, allowed=[True, False]
  fingerprint: {read: "show config profiles nvm"}  # DisplayString (SIZE(40)), access=r
  profile_action: {write: "config profile delete nvm num {_row_index}"}  # INTEGER, access=ru
  index: {read: "show config profiles nvm"}  # Integer32 (1..100), access=r, range=1–100
  datetime: {read: "show config profiles nvm"}  # HmTimeSeconds1970, access=r
  name: {read: "show config profiles nvm"}  # DisplayString (SIZE(0..32)), access=r, range=0–32
}
```
</details>

---

## protection

_Network protection features: Storm Control, Loop Protection, and Auto-Disable_

### `get_storm_control()`

**Read** | **Protocols:** MOPS, SNMP
Primary key: `broadcast_enabled` | Key map: `ifindex`

```
get_storm_control() -> {
    broadcast_enabled: False  // bool
    broadcast_threshold: 0  // int
    multicast_enabled: False  // bool
    multicast_threshold: 0  // int
}
```


<details><summary>MOPS sources (4/4 attrs)</summary>

```
MOPS {
  broadcast_enabled: {HM2-TRAFFICMGMT-MIB / hm2TrafficMgmtIfEntry.hm2TrafficMgmtIfIngressStormCtlBcastMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  broadcast_threshold: {HM2-TRAFFICMGMT-MIB / hm2TrafficMgmtIfEntry.hm2TrafficMgmtIfIngressStormCtlBcastThreshold}  # Unsigned32, access=ru, range=0–14880000
  multicast_threshold: {HM2-TRAFFICMGMT-MIB / hm2TrafficMgmtIfEntry.hm2TrafficMgmtIfIngressStormCtlMcastThreshold}  # Unsigned32, access=ru, range=0–14880000
  multicast_enabled: {HM2-TRAFFICMGMT-MIB / hm2TrafficMgmtIfEntry.hm2TrafficMgmtIfIngressStormCtlMcastMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (4/4 attrs)</summary>

```
SNMP {
  broadcast_enabled: {oid: 1.3.6.1.4.1.248.11.31.1.1.1.5}  # HmEnabledStatus, access=ru, allowed=[True, False]
  broadcast_threshold: {oid: 1.3.6.1.4.1.248.11.31.1.1.1.6}  # Unsigned32, access=ru, range=0–14880000
  multicast_threshold: {oid: 1.3.6.1.4.1.248.11.31.1.1.1.8}  # Unsigned32, access=ru, range=0–14880000
  multicast_enabled: {oid: 1.3.6.1.4.1.248.11.31.1.1.1.7}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

### `set_storm_control()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (9/9 attrs)</summary>

```
MOPS {
  broadcast_enabled: {HM2-TRAFFICMGMT-MIB / hm2TrafficMgmtIfEntry.hm2TrafficMgmtIfIngressStormCtlBcastMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  multicast_threshold: {HM2-TRAFFICMGMT-MIB / hm2TrafficMgmtIfEntry.hm2TrafficMgmtIfIngressStormCtlMcastThreshold}  # Unsigned32, access=ru, range=0–14880000
  loop_enabled: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentSwitchKeepaliveGroup.hm2AgentSwitchKeepaliveState}  # INTEGER, access=ru, allowed=['enable', 'disable']
  auto_disable_timer: {HM2-DEVMGMT-MIB / hm2AutoDisableIntfEntry.hm2AutoDisableIntfTimer}  # Unsigned32, access=ru
  multicast_enabled: {HM2-TRAFFICMGMT-MIB / hm2TrafficMgmtIfEntry.hm2TrafficMgmtIfIngressStormCtlMcastMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  auto_disable_reason: {HM2-DEVMGMT-MIB / hm2AutoDisableIntfEntry.hm2AutoDisableIntfErrorReason}  # INTEGER, access=r, allowed=['none', 'link-flap', 'crc-error', 'duplex-mismatch', 'dhcp-snooping', 'arp-rate', 'bpdu-rate', 'mac-based-port-security', 'overload-detection', 'speed-duplex', 'loop-protection']
  broadcast_threshold: {HM2-TRAFFICMGMT-MIB / hm2TrafficMgmtIfEntry.hm2TrafficMgmtIfIngressStormCtlBcastThreshold}  # Unsigned32, access=ru, range=0–14880000
  loop_interval: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentSwitchKeepaliveGroup.hm2AgentSwitchKeepaliveTransmitInterval}  # Integer32, access=ru, range=1–10
  auto_disable_reset: {HM2-DEVMGMT-MIB / hm2AutoDisableIntfEntry.hm2AutoDisableIntfReset}  # TruthValue, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (9/9 attrs)</summary>

```
SNMP {
  broadcast_enabled: {oid: 1.3.6.1.4.1.248.11.31.1.1.1.5}  # HmEnabledStatus, access=ru, allowed=[True, False]
  multicast_threshold: {oid: 1.3.6.1.4.1.248.11.31.1.1.1.8}  # Unsigned32, access=ru, range=0–14880000
  loop_enabled: {oid: 1.3.6.1.4.1.248.12.1.2.8.43.1, method: get}  # INTEGER, access=ru, allowed=['enable', 'disable']
  auto_disable_timer: {oid: 1.3.6.1.4.1.248.11.10.1.9.1.1.4}  # Unsigned32, access=ru
  multicast_enabled: {oid: 1.3.6.1.4.1.248.11.31.1.1.1.7}  # HmEnabledStatus, access=ru, allowed=[True, False]
  auto_disable_reason: {oid: 1.3.6.1.4.1.248.11.10.1.9.1.1.3}  # INTEGER, access=r, allowed=['none', 'link-flap', 'crc-error', 'duplex-mismatch', 'dhcp-snooping', 'arp-rate', 'bpdu-rate', 'mac-based-port-security', 'overload-detection', 'speed-duplex', 'loop-protection']
  broadcast_threshold: {oid: 1.3.6.1.4.1.248.11.31.1.1.1.6}  # Unsigned32, access=ru, range=0–14880000
  loop_interval: {oid: 1.3.6.1.4.1.248.12.1.2.8.43.2, method: get}  # Integer32, access=ru, range=1–10
  auto_disable_reset: {oid: 1.3.6.1.4.1.248.11.10.1.9.1.1.5}  # TruthValue, access=ru, allowed=[True, False]
}
```
</details>

### `get_loop_protection()`

**Read** | **Protocols:** None

```
get_loop_protection() -> {
    enabled: False  // bool
    transmission_interval: 2  // int
    rx_threshold: 0  // int
}
```


### `set_loop_protection()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (9/9 attrs)</summary>

```
MOPS {
  broadcast_enabled: {HM2-TRAFFICMGMT-MIB / hm2TrafficMgmtIfEntry.hm2TrafficMgmtIfIngressStormCtlBcastMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  multicast_threshold: {HM2-TRAFFICMGMT-MIB / hm2TrafficMgmtIfEntry.hm2TrafficMgmtIfIngressStormCtlMcastThreshold}  # Unsigned32, access=ru, range=0–14880000
  loop_enabled: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentSwitchKeepaliveGroup.hm2AgentSwitchKeepaliveState}  # INTEGER, access=ru, allowed=['enable', 'disable']
  auto_disable_timer: {HM2-DEVMGMT-MIB / hm2AutoDisableIntfEntry.hm2AutoDisableIntfTimer}  # Unsigned32, access=ru
  multicast_enabled: {HM2-TRAFFICMGMT-MIB / hm2TrafficMgmtIfEntry.hm2TrafficMgmtIfIngressStormCtlMcastMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  auto_disable_reason: {HM2-DEVMGMT-MIB / hm2AutoDisableIntfEntry.hm2AutoDisableIntfErrorReason}  # INTEGER, access=r, allowed=['none', 'link-flap', 'crc-error', 'duplex-mismatch', 'dhcp-snooping', 'arp-rate', 'bpdu-rate', 'mac-based-port-security', 'overload-detection', 'speed-duplex', 'loop-protection']
  broadcast_threshold: {HM2-TRAFFICMGMT-MIB / hm2TrafficMgmtIfEntry.hm2TrafficMgmtIfIngressStormCtlBcastThreshold}  # Unsigned32, access=ru, range=0–14880000
  loop_interval: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentSwitchKeepaliveGroup.hm2AgentSwitchKeepaliveTransmitInterval}  # Integer32, access=ru, range=1–10
  auto_disable_reset: {HM2-DEVMGMT-MIB / hm2AutoDisableIntfEntry.hm2AutoDisableIntfReset}  # TruthValue, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (9/9 attrs)</summary>

```
SNMP {
  broadcast_enabled: {oid: 1.3.6.1.4.1.248.11.31.1.1.1.5}  # HmEnabledStatus, access=ru, allowed=[True, False]
  multicast_threshold: {oid: 1.3.6.1.4.1.248.11.31.1.1.1.8}  # Unsigned32, access=ru, range=0–14880000
  loop_enabled: {oid: 1.3.6.1.4.1.248.12.1.2.8.43.1, method: get}  # INTEGER, access=ru, allowed=['enable', 'disable']
  auto_disable_timer: {oid: 1.3.6.1.4.1.248.11.10.1.9.1.1.4}  # Unsigned32, access=ru
  multicast_enabled: {oid: 1.3.6.1.4.1.248.11.31.1.1.1.7}  # HmEnabledStatus, access=ru, allowed=[True, False]
  auto_disable_reason: {oid: 1.3.6.1.4.1.248.11.10.1.9.1.1.3}  # INTEGER, access=r, allowed=['none', 'link-flap', 'crc-error', 'duplex-mismatch', 'dhcp-snooping', 'arp-rate', 'bpdu-rate', 'mac-based-port-security', 'overload-detection', 'speed-duplex', 'loop-protection']
  broadcast_threshold: {oid: 1.3.6.1.4.1.248.11.31.1.1.1.6}  # Unsigned32, access=ru, range=0–14880000
  loop_interval: {oid: 1.3.6.1.4.1.248.12.1.2.8.43.2, method: get}  # Integer32, access=ru, range=1–10
  auto_disable_reset: {oid: 1.3.6.1.4.1.248.11.10.1.9.1.1.5}  # TruthValue, access=ru, allowed=[True, False]
}
```
</details>

### `get_auto_disable()`

**Read** | **Protocols:** None
Primary key: `name` | Key map: `ifindex`

```
get_auto_disable() -> {
    enabled: False  // bool
    reason: "none"  // str
    remaining_time: 0  // int
}
```


### `set_auto_disable()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (9/9 attrs)</summary>

```
MOPS {
  broadcast_enabled: {HM2-TRAFFICMGMT-MIB / hm2TrafficMgmtIfEntry.hm2TrafficMgmtIfIngressStormCtlBcastMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  multicast_threshold: {HM2-TRAFFICMGMT-MIB / hm2TrafficMgmtIfEntry.hm2TrafficMgmtIfIngressStormCtlMcastThreshold}  # Unsigned32, access=ru, range=0–14880000
  loop_enabled: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentSwitchKeepaliveGroup.hm2AgentSwitchKeepaliveState}  # INTEGER, access=ru, allowed=['enable', 'disable']
  auto_disable_timer: {HM2-DEVMGMT-MIB / hm2AutoDisableIntfEntry.hm2AutoDisableIntfTimer}  # Unsigned32, access=ru
  multicast_enabled: {HM2-TRAFFICMGMT-MIB / hm2TrafficMgmtIfEntry.hm2TrafficMgmtIfIngressStormCtlMcastMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  auto_disable_reason: {HM2-DEVMGMT-MIB / hm2AutoDisableIntfEntry.hm2AutoDisableIntfErrorReason}  # INTEGER, access=r, allowed=['none', 'link-flap', 'crc-error', 'duplex-mismatch', 'dhcp-snooping', 'arp-rate', 'bpdu-rate', 'mac-based-port-security', 'overload-detection', 'speed-duplex', 'loop-protection']
  broadcast_threshold: {HM2-TRAFFICMGMT-MIB / hm2TrafficMgmtIfEntry.hm2TrafficMgmtIfIngressStormCtlBcastThreshold}  # Unsigned32, access=ru, range=0–14880000
  loop_interval: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentSwitchKeepaliveGroup.hm2AgentSwitchKeepaliveTransmitInterval}  # Integer32, access=ru, range=1–10
  auto_disable_reset: {HM2-DEVMGMT-MIB / hm2AutoDisableIntfEntry.hm2AutoDisableIntfReset}  # TruthValue, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (9/9 attrs)</summary>

```
SNMP {
  broadcast_enabled: {oid: 1.3.6.1.4.1.248.11.31.1.1.1.5}  # HmEnabledStatus, access=ru, allowed=[True, False]
  multicast_threshold: {oid: 1.3.6.1.4.1.248.11.31.1.1.1.8}  # Unsigned32, access=ru, range=0–14880000
  loop_enabled: {oid: 1.3.6.1.4.1.248.12.1.2.8.43.1, method: get}  # INTEGER, access=ru, allowed=['enable', 'disable']
  auto_disable_timer: {oid: 1.3.6.1.4.1.248.11.10.1.9.1.1.4}  # Unsigned32, access=ru
  multicast_enabled: {oid: 1.3.6.1.4.1.248.11.31.1.1.1.7}  # HmEnabledStatus, access=ru, allowed=[True, False]
  auto_disable_reason: {oid: 1.3.6.1.4.1.248.11.10.1.9.1.1.3}  # INTEGER, access=r, allowed=['none', 'link-flap', 'crc-error', 'duplex-mismatch', 'dhcp-snooping', 'arp-rate', 'bpdu-rate', 'mac-based-port-security', 'overload-detection', 'speed-duplex', 'loop-protection']
  broadcast_threshold: {oid: 1.3.6.1.4.1.248.11.31.1.1.1.6}  # Unsigned32, access=ru, range=0–14880000
  loop_interval: {oid: 1.3.6.1.4.1.248.12.1.2.8.43.2, method: get}  # Integer32, access=ru, range=1–10
  auto_disable_reset: {oid: 1.3.6.1.4.1.248.11.10.1.9.1.1.5}  # TruthValue, access=ru, allowed=[True, False]
}
```
</details>

### `set_auto_disable_reason()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (9/9 attrs)</summary>

```
MOPS {
  broadcast_enabled: {HM2-TRAFFICMGMT-MIB / hm2TrafficMgmtIfEntry.hm2TrafficMgmtIfIngressStormCtlBcastMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  multicast_threshold: {HM2-TRAFFICMGMT-MIB / hm2TrafficMgmtIfEntry.hm2TrafficMgmtIfIngressStormCtlMcastThreshold}  # Unsigned32, access=ru, range=0–14880000
  loop_enabled: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentSwitchKeepaliveGroup.hm2AgentSwitchKeepaliveState}  # INTEGER, access=ru, allowed=['enable', 'disable']
  auto_disable_timer: {HM2-DEVMGMT-MIB / hm2AutoDisableIntfEntry.hm2AutoDisableIntfTimer}  # Unsigned32, access=ru
  multicast_enabled: {HM2-TRAFFICMGMT-MIB / hm2TrafficMgmtIfEntry.hm2TrafficMgmtIfIngressStormCtlMcastMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  auto_disable_reason: {HM2-DEVMGMT-MIB / hm2AutoDisableIntfEntry.hm2AutoDisableIntfErrorReason}  # INTEGER, access=r, allowed=['none', 'link-flap', 'crc-error', 'duplex-mismatch', 'dhcp-snooping', 'arp-rate', 'bpdu-rate', 'mac-based-port-security', 'overload-detection', 'speed-duplex', 'loop-protection']
  broadcast_threshold: {HM2-TRAFFICMGMT-MIB / hm2TrafficMgmtIfEntry.hm2TrafficMgmtIfIngressStormCtlBcastThreshold}  # Unsigned32, access=ru, range=0–14880000
  loop_interval: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentSwitchKeepaliveGroup.hm2AgentSwitchKeepaliveTransmitInterval}  # Integer32, access=ru, range=1–10
  auto_disable_reset: {HM2-DEVMGMT-MIB / hm2AutoDisableIntfEntry.hm2AutoDisableIntfReset}  # TruthValue, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (9/9 attrs)</summary>

```
SNMP {
  broadcast_enabled: {oid: 1.3.6.1.4.1.248.11.31.1.1.1.5}  # HmEnabledStatus, access=ru, allowed=[True, False]
  multicast_threshold: {oid: 1.3.6.1.4.1.248.11.31.1.1.1.8}  # Unsigned32, access=ru, range=0–14880000
  loop_enabled: {oid: 1.3.6.1.4.1.248.12.1.2.8.43.1, method: get}  # INTEGER, access=ru, allowed=['enable', 'disable']
  auto_disable_timer: {oid: 1.3.6.1.4.1.248.11.10.1.9.1.1.4}  # Unsigned32, access=ru
  multicast_enabled: {oid: 1.3.6.1.4.1.248.11.31.1.1.1.7}  # HmEnabledStatus, access=ru, allowed=[True, False]
  auto_disable_reason: {oid: 1.3.6.1.4.1.248.11.10.1.9.1.1.3}  # INTEGER, access=r, allowed=['none', 'link-flap', 'crc-error', 'duplex-mismatch', 'dhcp-snooping', 'arp-rate', 'bpdu-rate', 'mac-based-port-security', 'overload-detection', 'speed-duplex', 'loop-protection']
  broadcast_threshold: {oid: 1.3.6.1.4.1.248.11.31.1.1.1.6}  # Unsigned32, access=ru, range=0–14880000
  loop_interval: {oid: 1.3.6.1.4.1.248.12.1.2.8.43.2, method: get}  # Integer32, access=ru, range=1–10
  auto_disable_reset: {oid: 1.3.6.1.4.1.248.11.10.1.9.1.1.5}  # TruthValue, access=ru, allowed=[True, False]
}
```
</details>

---

## qos

_Quality of Service (QoS) and Traffic Class mapping_

### `get_qos()`

**Read** | **Protocols:** MOPS, SNMP

```
get_qos() -> {
    global_trust_mode: "none"  // str
    port_trust_mode: {...}  // dict
}
```


<details><summary>MOPS sources (1/1 attrs)</summary>

```
MOPS {
  port_trust_mode: {HM2-PLATFORM-QOS-COS-MIB / hm2AgentCosMapIntfTrustEntry.hm2AgentCosMapIntfTrustMode}  # INTEGER, access=ru, allowed=['untrusted', 'trustDot1p', 'trustIpPrecedence', 'trustIpDscp']
}
```
</details>

<details><summary>SNMP sources (1/1 attrs)</summary>

```
SNMP {
  port_trust_mode: {oid: 1.3.6.1.4.1.248.12.3.3.1.3.1.2}  # INTEGER, access=ru, allowed=['untrusted', 'trustDot1p', 'trustIpPrecedence', 'trustIpDscp']
}
```
</details>

### `set_qos()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (4/4 attrs)</summary>

```
MOPS {
  default_priority: {P-BRIDGE-MIB / dot1dPortPriorityEntry.dot1dPortDefaultUserPriority}  # INTEGER, access=ru, range=0–7
  port_trust_mode: {HM2-PLATFORM-QOS-COS-MIB / hm2AgentCosMapIntfTrustEntry.hm2AgentCosMapIntfTrustMode}  # INTEGER, access=ru, allowed=['untrusted', 'trustDot1p', 'trustIpPrecedence', 'trustIpDscp']
  num_traffic_classes: {P-BRIDGE-MIB / dot1dPortPriorityEntry.dot1dPortNumTrafficClasses}  # INTEGER, access=ru, range=1–8
  port_untrusted_tc: {HM2-PLATFORM-QOS-COS-MIB / hm2AgentCosMapIntfTrustEntry.hm2AgentCosMapUntrustedTrafficClass}  # Unsigned32, access=r
}
```
</details>

<details><summary>SNMP sources (4/4 attrs)</summary>

```
SNMP {
  default_priority: {oid: 1.3.6.1.2.1.17.6.1.2.1.1.1}  # INTEGER, access=ru, range=0–7
  port_trust_mode: {oid: 1.3.6.1.4.1.248.12.3.3.1.3.1.2}  # INTEGER, access=ru, allowed=['untrusted', 'trustDot1p', 'trustIpPrecedence', 'trustIpDscp']
  num_traffic_classes: {oid: 1.3.6.1.2.1.17.6.1.2.1.1.2}  # INTEGER, access=ru, range=1–8
  port_untrusted_tc: {oid: 1.3.6.1.4.1.248.12.3.3.1.3.1.3}  # Unsigned32, access=r
}
```
</details>

---

## qos_mapping

_Global dot1p and DSCP to traffic class mapping tables_

### `get_qos_mapping()`

**Read** | **Protocols:** MOPS, SNMP
> Sub-table: **`dot1p`** — key: `dot1p_priority`
> Sub-table: **`dscp`** — key: `dscp_value`

<details><summary>MOPS sources (4/4 attrs)</summary>

```
MOPS {
  dot1p_priority: {HM2-L2FORWARDING-MIB / hm2TrafficClassEntry.hm2TrafficClassPriority}  # Integer32, access=r, range=0–7
  dscp_value: {HM2-L2FORWARDING-MIB / hm2CosMapIpDscpEntry.hm2CosMapIpDscpValue}  # Unsigned32, access=r, range=0–63
  dscp_traffic_class: {HM2-L2FORWARDING-MIB / hm2CosMapIpDscpEntry.hm2CosMapIpDscpTrafficClass}  # Unsigned32, access=ru, range=0–7
  dot1p_traffic_class: {HM2-L2FORWARDING-MIB / hm2TrafficClassEntry.hm2TrafficClass}  # Integer32, access=ru, range=0–7
}
```
</details>

<details><summary>SNMP sources (4/4 attrs)</summary>

```
SNMP {
  dot1p_priority: {oid: 1.3.6.1.4.1.248.11.30.1.2.1.1.1}  # Integer32, access=r, range=0–7
  dscp_value: {oid: 1.3.6.1.4.1.248.11.30.1.2.2.1.1}  # Unsigned32, access=r, range=0–63
  dscp_traffic_class: {oid: 1.3.6.1.4.1.248.11.30.1.2.2.1.2}  # Unsigned32, access=ru, range=0–7
  dot1p_traffic_class: {oid: 1.3.6.1.4.1.248.11.30.1.2.1.1.2}  # Integer32, access=ru, range=0–7
}
```
</details>

### `set_qos_mapping()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (4/4 attrs)</summary>

```
MOPS {
  dot1p_priority: {HM2-L2FORWARDING-MIB / hm2TrafficClassEntry.hm2TrafficClassPriority}  # Integer32, access=r, range=0–7
  dscp_value: {HM2-L2FORWARDING-MIB / hm2CosMapIpDscpEntry.hm2CosMapIpDscpValue}  # Unsigned32, access=r, range=0–63
  dscp_traffic_class: {HM2-L2FORWARDING-MIB / hm2CosMapIpDscpEntry.hm2CosMapIpDscpTrafficClass}  # Unsigned32, access=ru, range=0–7
  dot1p_traffic_class: {HM2-L2FORWARDING-MIB / hm2TrafficClassEntry.hm2TrafficClass}  # Integer32, access=ru, range=0–7
}
```
</details>

<details><summary>SNMP sources (4/4 attrs)</summary>

```
SNMP {
  dot1p_priority: {oid: 1.3.6.1.4.1.248.11.30.1.2.1.1.1}  # Integer32, access=r, range=0–7
  dscp_value: {oid: 1.3.6.1.4.1.248.11.30.1.2.2.1.1}  # Unsigned32, access=r, range=0–63
  dscp_traffic_class: {oid: 1.3.6.1.4.1.248.11.30.1.2.2.1.2}  # Unsigned32, access=ru, range=0–7
  dot1p_traffic_class: {oid: 1.3.6.1.4.1.248.11.30.1.2.1.1.2}  # Integer32, access=ru, range=0–7
}
```
</details>

---

## remote_auth

_RADIUS, TACACS+, and LDAP remote authentication_

### `get_remote_auth()`

**Read** | **Protocols:** MOPS, SNMP, SSH

```
get_remote_auth() -> {
    radius_enabled: False  // bool
    radius_timeout: 5  // int
    radius_retransmits: 3  // int
    tacacs_enabled: False  // bool
    tacacs_timeout: 5  // int
    ldap_enabled: False  // bool
    radius_servers: {...}  // dict
    ldap_servers: {...}  // dict
    tacacs_servers: {...}  // dict
}
```

> Sub-table: **`radius_servers`** — key: `address`
> Sub-table: **`ldap_servers`** — key: `ldap_address`
> Sub-table: **`tacacs_servers`** — key: `tacacs_address`

<details><summary>MOPS sources (13/13 attrs)</summary>

```
MOPS {
  radius_retransmits: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusConfigGroup.hm2AgentRadiusMaxTransmit}  # Unsigned32, access=ru, range=1–15
  tacacs_port: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsServerEntry.hm2AgentTacacsPortNumber}  # Unsigned32, access=ru, range=1–65535
  ldap_enabled: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapConfigGroup.hm2LdapClientAdminState}  # HmEnabledStatus, access=ru, allowed=[True, False]
  tacacs_timeout: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsServerEntry.hm2AgentTacacsTimeOut}  # Unsigned32, access=ru, range=1–30
  radius_port: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerPort}  # Unsigned32, access=ru, range=0–65535
  address: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerInetAddress}  # InetAddress, access=ru
  secret: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerSecret}  # DisplayString, access=ru
  radius_enabled: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusConfigGroup.hm2AgentRadiusAccountingMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  tacacs_address: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsServerEntry.hm2AgentTacacsServerIpAddress}  # InetAddress, access=r
  ldap_port: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapClientServerAddrEntry.hm2LdapClientServerPort}  # InetPortNumber, access=ru
  ldap_address: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapClientServerAddrEntry.hm2LdapClientServerAddr}  # InetAddress, access=ru
  radius_timeout: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusConfigGroup.hm2AgentRadiusTimeout}  # Unsigned32, access=ru, range=1–30
  tacacs_enabled: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsAccountingGroup.hm2AgentTacacsCmdAccountingMode}  # INTEGER, access=ru
}
```
</details>

<details><summary>SNMP sources (13/13 attrs)</summary>

```
SNMP {
  radius_retransmits: {oid: 1.3.6.1.4.1.248.12.8.1.1, method: get}  # Unsigned32, access=ru, range=1–15
  tacacs_port: {oid: 1.3.6.1.4.1.248.12.18.1.2.1.3}  # Unsigned32, access=ru, range=1–65535
  ldap_enabled: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  tacacs_timeout: {oid: 1.3.6.1.4.1.248.12.18.1.2.1.4}  # Unsigned32, access=ru, range=1–30
  radius_port: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.4}  # Unsigned32, access=ru, range=0–65535
  address: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.11}  # InetAddress, access=ru
  secret: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.5}  # DisplayString, access=ru
  radius_enabled: {oid: 1.3.6.1.4.1.248.12.8.1.3, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  tacacs_address: {oid: 1.3.6.1.4.1.248.12.18.1.2.1.2}  # InetAddress, access=r
  ldap_port: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.20.1.5}  # InetPortNumber, access=ru
  ldap_address: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.20.1.4}  # InetAddress, access=ru
  radius_timeout: {oid: 1.3.6.1.4.1.248.12.8.1.2, method: get}  # Unsigned32, access=ru, range=1–30
  tacacs_enabled: {oid: 1.3.6.1.4.1.248.12.18.1.249.1, method: get}  # INTEGER, access=ru
}
```
</details>

<details><summary>SSH sources (3/13 attrs)</summary>

```
SSH {
  address: {read: "show radius auth servers", write: "radius server auth add {index} ip {address}"}  # InetAddress, access=ru
  tacacs_address: {read: "show tacacs server", write: "tacacs server add {tacacs_address}"}  # InetAddress, access=r
  ldap_address: {read: "show ldap servers", write: "ldap client server add {index} {ldap_address}"}  # InetAddress, access=ru
}
```
</details>

### `set_remote_auth()`

**Update** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (21/21 attrs)</summary>

```
MOPS {
  ldap_enabled: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapConfigGroup.hm2LdapClientAdminState}  # HmEnabledStatus, access=ru, allowed=[True, False]
  radius_timeout: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusConfigGroup.hm2AgentRadiusTimeout}  # Unsigned32, access=ru, range=1–30
  secret: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerSecret}  # DisplayString, access=ru
  address: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerInetAddress}  # InetAddress, access=ru
  tacacs_addr_type: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsServerEntry.hm2AgentTacacsServerIpAddrType}  # InetAddressType, access=r
  ldap_address: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapClientServerAddrEntry.hm2LdapClientServerAddr}  # InetAddress, access=ru
  tacacs_enabled: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsAccountingGroup.hm2AgentTacacsCmdAccountingMode}  # INTEGER, access=ru
  radius_retransmits: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusConfigGroup.hm2AgentRadiusMaxTransmit}  # Unsigned32, access=ru, range=1–15
  radius_index: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerIndex}  # Integer32, access=r, range=1–2147483647
  tacacs_timeout: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsServerEntry.hm2AgentTacacsTimeOut}  # Unsigned32, access=ru, range=1–30
  ldap_addr_type: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapClientServerAddrEntry.hm2LdapClientServerAddrType}  # InetAddressType, access=ru
  ldap_row_status: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapClientServerAddrEntry.hm2LdapClientServerRowStatus}  # RowStatus, access=crud
  ldap_index: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapClientServerAddrEntry.hm2LdapClientServerIndex}  # Integer32, access=r, range=1–4
  ldap_port: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapClientServerAddrEntry.hm2LdapClientServerPort}  # InetPortNumber, access=ru
  tacacs_port: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsServerEntry.hm2AgentTacacsPortNumber}  # Unsigned32, access=ru, range=1–65535
  radius_addr_type: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerInetAddrType}  # InetAddressType, access=ru
  radius_port: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerPort}  # Unsigned32, access=ru, range=0–65535
  radius_enabled: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusConfigGroup.hm2AgentRadiusAccountingMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  tacacs_address: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsServerEntry.hm2AgentTacacsServerIpAddress}  # InetAddress, access=r
  tacacs_row_status: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsServerEntry.hm2AgentTacacsServerStatus}  # RowStatus, access=crud
  radius_row_status: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerRowStatus}  # RowStatus, access=crud
}
```
</details>

<details><summary>SNMP sources (21/21 attrs)</summary>

```
SNMP {
  ldap_enabled: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  radius_timeout: {oid: 1.3.6.1.4.1.248.12.8.1.2, method: get}  # Unsigned32, access=ru, range=1–30
  secret: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.5}  # DisplayString, access=ru
  address: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.11}  # InetAddress, access=ru
  tacacs_addr_type: {oid: 1.3.6.1.4.1.248.12.18.1.2.1.1}  # InetAddressType, access=r
  ldap_address: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.20.1.4}  # InetAddress, access=ru
  tacacs_enabled: {oid: 1.3.6.1.4.1.248.12.18.1.249.1, method: get}  # INTEGER, access=ru
  radius_retransmits: {oid: 1.3.6.1.4.1.248.12.8.1.1, method: get}  # Unsigned32, access=ru, range=1–15
  radius_index: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.1}  # Integer32, access=r, range=1–2147483647
  tacacs_timeout: {oid: 1.3.6.1.4.1.248.12.18.1.2.1.4}  # Unsigned32, access=ru, range=1–30
  ldap_addr_type: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.20.1.3}  # InetAddressType, access=ru
  ldap_row_status: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.20.1.8}  # RowStatus, access=crud
  ldap_index: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.20.1.1}  # Integer32, access=r, range=1–4
  ldap_port: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.20.1.5}  # InetPortNumber, access=ru
  tacacs_port: {oid: 1.3.6.1.4.1.248.12.18.1.2.1.3}  # Unsigned32, access=ru, range=1–65535
  radius_addr_type: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.248}  # InetAddressType, access=ru
  radius_port: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.4}  # Unsigned32, access=ru, range=0–65535
  radius_enabled: {oid: 1.3.6.1.4.1.248.12.8.1.3, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  tacacs_address: {oid: 1.3.6.1.4.1.248.12.18.1.2.1.2}  # InetAddress, access=r
  tacacs_row_status: {oid: 1.3.6.1.4.1.248.12.18.1.2.1.7}  # RowStatus, access=crud
  radius_row_status: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.9}  # RowStatus, access=crud
}
```
</details>

<details><summary>SSH sources (6/21 attrs)</summary>

```
SSH {
  address: {read: "show radius auth servers", write: "radius server auth add {index} ip {address}"}  # InetAddress, access=ru
  ldap_address: {read: "show ldap servers", write: "ldap client server add {index} {ldap_address}"}  # InetAddress, access=ru
  ldap_row_status: {write: "ldap client server add {index} {ldap_address}"}  # RowStatus, access=crud
  tacacs_address: {read: "show tacacs server", write: "tacacs server add {tacacs_address}"}  # InetAddress, access=r
  tacacs_row_status: {write: "tacacs server add {tacacs_address}"}  # RowStatus, access=crud
  radius_row_status: {write: "radius server auth add {index} ip {address}"}  # RowStatus, access=crud
}
```
</details>

### `create_radius_server()`

**Create** | **Protocols:** MOPS, SNMP, SSH
Required: `address`

```
create_radius_server() -> {
    radius_addr_type: 1  // int
    radius_port: 1812  // int
}
```


<details><summary>MOPS sources (3/3 attrs)</summary>

```
MOPS {
  radius_addr_type: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerInetAddrType}  # InetAddressType, access=ru
  address: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerInetAddress}  # InetAddress, access=ru
  radius_port: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerPort}  # Unsigned32, access=ru, range=0–65535
}
```
</details>

<details><summary>SNMP sources (3/3 attrs)</summary>

```
SNMP {
  radius_addr_type: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.248}  # InetAddressType, access=ru
  address: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.11}  # InetAddress, access=ru
  radius_port: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.4}  # Unsigned32, access=ru, range=0–65535
}
```
</details>

<details><summary>SSH sources (1/3 attrs)</summary>

```
SSH {
  address: {read: "show radius auth servers", write: "radius server auth add {index} ip {address}"}  # InetAddress, access=ru
}
```
</details>

### `delete_radius_server()`

**Delete** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (21/21 attrs)</summary>

```
MOPS {
  ldap_enabled: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapConfigGroup.hm2LdapClientAdminState}  # HmEnabledStatus, access=ru, allowed=[True, False]
  radius_timeout: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusConfigGroup.hm2AgentRadiusTimeout}  # Unsigned32, access=ru, range=1–30
  secret: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerSecret}  # DisplayString, access=ru
  address: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerInetAddress}  # InetAddress, access=ru
  tacacs_addr_type: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsServerEntry.hm2AgentTacacsServerIpAddrType}  # InetAddressType, access=r
  ldap_address: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapClientServerAddrEntry.hm2LdapClientServerAddr}  # InetAddress, access=ru
  tacacs_enabled: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsAccountingGroup.hm2AgentTacacsCmdAccountingMode}  # INTEGER, access=ru
  radius_retransmits: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusConfigGroup.hm2AgentRadiusMaxTransmit}  # Unsigned32, access=ru, range=1–15
  radius_index: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerIndex}  # Integer32, access=r, range=1–2147483647
  tacacs_timeout: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsServerEntry.hm2AgentTacacsTimeOut}  # Unsigned32, access=ru, range=1–30
  ldap_addr_type: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapClientServerAddrEntry.hm2LdapClientServerAddrType}  # InetAddressType, access=ru
  ldap_row_status: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapClientServerAddrEntry.hm2LdapClientServerRowStatus}  # RowStatus, access=crud
  ldap_index: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapClientServerAddrEntry.hm2LdapClientServerIndex}  # Integer32, access=r, range=1–4
  ldap_port: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapClientServerAddrEntry.hm2LdapClientServerPort}  # InetPortNumber, access=ru
  tacacs_port: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsServerEntry.hm2AgentTacacsPortNumber}  # Unsigned32, access=ru, range=1–65535
  radius_addr_type: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerInetAddrType}  # InetAddressType, access=ru
  radius_port: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerPort}  # Unsigned32, access=ru, range=0–65535
  radius_enabled: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusConfigGroup.hm2AgentRadiusAccountingMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  tacacs_address: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsServerEntry.hm2AgentTacacsServerIpAddress}  # InetAddress, access=r
  tacacs_row_status: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsServerEntry.hm2AgentTacacsServerStatus}  # RowStatus, access=crud
  radius_row_status: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerRowStatus}  # RowStatus, access=crud
}
```
</details>

<details><summary>SNMP sources (21/21 attrs)</summary>

```
SNMP {
  ldap_enabled: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  radius_timeout: {oid: 1.3.6.1.4.1.248.12.8.1.2, method: get}  # Unsigned32, access=ru, range=1–30
  secret: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.5}  # DisplayString, access=ru
  address: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.11}  # InetAddress, access=ru
  tacacs_addr_type: {oid: 1.3.6.1.4.1.248.12.18.1.2.1.1}  # InetAddressType, access=r
  ldap_address: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.20.1.4}  # InetAddress, access=ru
  tacacs_enabled: {oid: 1.3.6.1.4.1.248.12.18.1.249.1, method: get}  # INTEGER, access=ru
  radius_retransmits: {oid: 1.3.6.1.4.1.248.12.8.1.1, method: get}  # Unsigned32, access=ru, range=1–15
  radius_index: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.1}  # Integer32, access=r, range=1–2147483647
  tacacs_timeout: {oid: 1.3.6.1.4.1.248.12.18.1.2.1.4}  # Unsigned32, access=ru, range=1–30
  ldap_addr_type: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.20.1.3}  # InetAddressType, access=ru
  ldap_row_status: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.20.1.8}  # RowStatus, access=crud
  ldap_index: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.20.1.1}  # Integer32, access=r, range=1–4
  ldap_port: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.20.1.5}  # InetPortNumber, access=ru
  tacacs_port: {oid: 1.3.6.1.4.1.248.12.18.1.2.1.3}  # Unsigned32, access=ru, range=1–65535
  radius_addr_type: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.248}  # InetAddressType, access=ru
  radius_port: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.4}  # Unsigned32, access=ru, range=0–65535
  radius_enabled: {oid: 1.3.6.1.4.1.248.12.8.1.3, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  tacacs_address: {oid: 1.3.6.1.4.1.248.12.18.1.2.1.2}  # InetAddress, access=r
  tacacs_row_status: {oid: 1.3.6.1.4.1.248.12.18.1.2.1.7}  # RowStatus, access=crud
  radius_row_status: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.9}  # RowStatus, access=crud
}
```
</details>

<details><summary>SSH sources (6/21 attrs)</summary>

```
SSH {
  address: {read: "show radius auth servers", write: "radius server auth add {index} ip {address}"}  # InetAddress, access=ru
  ldap_address: {read: "show ldap servers", write: "ldap client server add {index} {ldap_address}"}  # InetAddress, access=ru
  ldap_row_status: {write: "ldap client server add {index} {ldap_address}"}  # RowStatus, access=crud
  tacacs_address: {read: "show tacacs server", write: "tacacs server add {tacacs_address}"}  # InetAddress, access=r
  tacacs_row_status: {write: "tacacs server add {tacacs_address}"}  # RowStatus, access=crud
  radius_row_status: {write: "radius server auth add {index} ip {address}"}  # RowStatus, access=crud
}
```
</details>

### `create_ldap_server()`

**Create** | **Protocols:** MOPS, SNMP, SSH
Required: `ldap_address`

```
create_ldap_server() -> {
    ldap_addr_type: 1  // int
    ldap_port: 636  // int
}
```


<details><summary>MOPS sources (3/3 attrs)</summary>

```
MOPS {
  ldap_address: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapClientServerAddrEntry.hm2LdapClientServerAddr}  # InetAddress, access=ru
  ldap_addr_type: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapClientServerAddrEntry.hm2LdapClientServerAddrType}  # InetAddressType, access=ru
  ldap_port: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapClientServerAddrEntry.hm2LdapClientServerPort}  # InetPortNumber, access=ru
}
```
</details>

<details><summary>SNMP sources (3/3 attrs)</summary>

```
SNMP {
  ldap_address: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.20.1.4}  # InetAddress, access=ru
  ldap_addr_type: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.20.1.3}  # InetAddressType, access=ru
  ldap_port: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.20.1.5}  # InetPortNumber, access=ru
}
```
</details>

<details><summary>SSH sources (1/3 attrs)</summary>

```
SSH {
  ldap_address: {read: "show ldap servers", write: "ldap client server add {index} {ldap_address}"}  # InetAddress, access=ru
}
```
</details>

### `delete_ldap_server()`

**Delete** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (21/21 attrs)</summary>

```
MOPS {
  ldap_enabled: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapConfigGroup.hm2LdapClientAdminState}  # HmEnabledStatus, access=ru, allowed=[True, False]
  radius_timeout: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusConfigGroup.hm2AgentRadiusTimeout}  # Unsigned32, access=ru, range=1–30
  secret: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerSecret}  # DisplayString, access=ru
  address: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerInetAddress}  # InetAddress, access=ru
  tacacs_addr_type: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsServerEntry.hm2AgentTacacsServerIpAddrType}  # InetAddressType, access=r
  ldap_address: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapClientServerAddrEntry.hm2LdapClientServerAddr}  # InetAddress, access=ru
  tacacs_enabled: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsAccountingGroup.hm2AgentTacacsCmdAccountingMode}  # INTEGER, access=ru
  radius_retransmits: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusConfigGroup.hm2AgentRadiusMaxTransmit}  # Unsigned32, access=ru, range=1–15
  radius_index: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerIndex}  # Integer32, access=r, range=1–2147483647
  tacacs_timeout: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsServerEntry.hm2AgentTacacsTimeOut}  # Unsigned32, access=ru, range=1–30
  ldap_addr_type: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapClientServerAddrEntry.hm2LdapClientServerAddrType}  # InetAddressType, access=ru
  ldap_row_status: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapClientServerAddrEntry.hm2LdapClientServerRowStatus}  # RowStatus, access=crud
  ldap_index: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapClientServerAddrEntry.hm2LdapClientServerIndex}  # Integer32, access=r, range=1–4
  ldap_port: {HM2-REMOTE-AUTHENTICATION-MIB / hm2LdapClientServerAddrEntry.hm2LdapClientServerPort}  # InetPortNumber, access=ru
  tacacs_port: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsServerEntry.hm2AgentTacacsPortNumber}  # Unsigned32, access=ru, range=1–65535
  radius_addr_type: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerInetAddrType}  # InetAddressType, access=ru
  radius_port: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerPort}  # Unsigned32, access=ru, range=0–65535
  radius_enabled: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusConfigGroup.hm2AgentRadiusAccountingMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  tacacs_address: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsServerEntry.hm2AgentTacacsServerIpAddress}  # InetAddress, access=r
  tacacs_row_status: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsServerEntry.hm2AgentTacacsServerStatus}  # RowStatus, access=crud
  radius_row_status: {HM2-PLATFORM-RADIUS-MIB / hm2AgentRadiusServerConfigEntry.hm2AgentRadiusServerRowStatus}  # RowStatus, access=crud
}
```
</details>

<details><summary>SNMP sources (21/21 attrs)</summary>

```
SNMP {
  ldap_enabled: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  radius_timeout: {oid: 1.3.6.1.4.1.248.12.8.1.2, method: get}  # Unsigned32, access=ru, range=1–30
  secret: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.5}  # DisplayString, access=ru
  address: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.11}  # InetAddress, access=ru
  tacacs_addr_type: {oid: 1.3.6.1.4.1.248.12.18.1.2.1.1}  # InetAddressType, access=r
  ldap_address: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.20.1.4}  # InetAddress, access=ru
  tacacs_enabled: {oid: 1.3.6.1.4.1.248.12.18.1.249.1, method: get}  # INTEGER, access=ru
  radius_retransmits: {oid: 1.3.6.1.4.1.248.12.8.1.1, method: get}  # Unsigned32, access=ru, range=1–15
  radius_index: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.1}  # Integer32, access=r, range=1–2147483647
  tacacs_timeout: {oid: 1.3.6.1.4.1.248.12.18.1.2.1.4}  # Unsigned32, access=ru, range=1–30
  ldap_addr_type: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.20.1.3}  # InetAddressType, access=ru
  ldap_row_status: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.20.1.8}  # RowStatus, access=crud
  ldap_index: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.20.1.1}  # Integer32, access=r, range=1–4
  ldap_port: {oid: 1.3.6.1.4.1.248.11.26.1.1.10.20.1.5}  # InetPortNumber, access=ru
  tacacs_port: {oid: 1.3.6.1.4.1.248.12.18.1.2.1.3}  # Unsigned32, access=ru, range=1–65535
  radius_addr_type: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.248}  # InetAddressType, access=ru
  radius_port: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.4}  # Unsigned32, access=ru, range=0–65535
  radius_enabled: {oid: 1.3.6.1.4.1.248.12.8.1.3, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  tacacs_address: {oid: 1.3.6.1.4.1.248.12.18.1.2.1.2}  # InetAddress, access=r
  tacacs_row_status: {oid: 1.3.6.1.4.1.248.12.18.1.2.1.7}  # RowStatus, access=crud
  radius_row_status: {oid: 1.3.6.1.4.1.248.12.8.1.8.1.9}  # RowStatus, access=crud
}
```
</details>

<details><summary>SSH sources (6/21 attrs)</summary>

```
SSH {
  address: {read: "show radius auth servers", write: "radius server auth add {index} ip {address}"}  # InetAddress, access=ru
  ldap_address: {read: "show ldap servers", write: "ldap client server add {index} {ldap_address}"}  # InetAddress, access=ru
  ldap_row_status: {write: "ldap client server add {index} {ldap_address}"}  # RowStatus, access=crud
  tacacs_address: {read: "show tacacs server", write: "tacacs server add {tacacs_address}"}  # InetAddress, access=r
  tacacs_row_status: {write: "tacacs server add {tacacs_address}"}  # RowStatus, access=crud
  radius_row_status: {write: "radius server auth add {index} ip {address}"}  # RowStatus, access=crud
}
```
</details>

### `create_tacacs_server()`

**Create** | **Protocols:** MOPS, SNMP, SSH
Required: `tacacs_address`

```
create_tacacs_server() -> {
    tacacs_addr_type: 1  // int
}
```


<details><summary>MOPS sources (2/2 attrs)</summary>

```
MOPS {
  tacacs_address: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsServerEntry.hm2AgentTacacsServerIpAddress}  # InetAddress, access=r
  tacacs_addr_type: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsServerEntry.hm2AgentTacacsServerIpAddrType}  # InetAddressType, access=r
}
```
</details>

<details><summary>SNMP sources (2/2 attrs)</summary>

```
SNMP {
  tacacs_address: {oid: 1.3.6.1.4.1.248.12.18.1.2.1.2}  # InetAddress, access=r
  tacacs_addr_type: {oid: 1.3.6.1.4.1.248.12.18.1.2.1.1}  # InetAddressType, access=r
}
```
</details>

<details><summary>SSH sources (1/2 attrs)</summary>

```
SSH {
  tacacs_address: {read: "show tacacs server", write: "tacacs server add {tacacs_address}"}  # InetAddress, access=r
}
```
</details>

### `delete_tacacs_server()`

**Delete** | **Protocols:** MOPS, SNMP

```
delete_tacacs_server() -> {
    tacacs_addr_type: 1  // int
}
```


<details><summary>MOPS sources (1/1 attrs)</summary>

```
MOPS {
  tacacs_addr_type: {HM2-PLATFORM-TACACSCLIENT-MIB / hm2AgentTacacsServerEntry.hm2AgentTacacsServerIpAddrType}  # InetAddressType, access=r
}
```
</details>

<details><summary>SNMP sources (1/1 attrs)</summary>

```
SNMP {
  tacacs_addr_type: {oid: 1.3.6.1.4.1.248.12.18.1.2.1.1}  # InetAddressType, access=r
}
```
</details>

---

## route

_IP routing table mapping_

### `get_route_to()`

**Read** | **Protocols:** MOPS, SNMP
Primary key: `destination`

```
get_route_to() -> {
    protocol: "other"  // "other" | "local" | "netmgmt" | "icmp" | "rip" | "ospf" | "bgp"
    next_hop: ""  // str
    outgoing_interface: ""  // str
    preference: 0  // int
    age: 0  // int
}
```


<details><summary>MOPS sources (6/6 attrs)</summary>

```
MOPS {
  outgoing_interface: {IP-FORWARD-MIB / inetCidrRouteEntry.inetCidrRouteIfIndex}  # InterfaceIndexOrZero, access=ru
  protocol: {IP-FORWARD-MIB / inetCidrRouteEntry.inetCidrRouteProto}  # IANAipRouteProtocol, access=r
  age: {IP-FORWARD-MIB / inetCidrRouteEntry.inetCidrRouteAge}  # Gauge32, access=r
  destination: {IP-FORWARD-MIB / inetCidrRouteEntry.inetCidrRouteDest}  # InetAddress, access=r
  preference: {IP-FORWARD-MIB / inetCidrRouteEntry.inetCidrRouteMetric1}  # Integer32, access=ru
  next_hop: {IP-FORWARD-MIB / inetCidrRouteEntry.inetCidrRouteNextHop}  # InetAddress, access=r
}
```
</details>

<details><summary>SNMP sources (6/6 attrs)</summary>

```
SNMP {
  outgoing_interface: {oid: 1.3.6.1.2.1.4.24.7.1.7}  # InterfaceIndexOrZero, access=ru
  protocol: {oid: 1.3.6.1.2.1.4.24.7.1.9}  # IANAipRouteProtocol, access=r
  age: {oid: 1.3.6.1.2.1.4.24.7.1.10}  # Gauge32, access=r
  destination: {oid: 1.3.6.1.2.1.4.24.7.1.2}  # InetAddress, access=r
  preference: {oid: 1.3.6.1.2.1.4.24.7.1.12}  # Integer32, access=ru
  next_hop: {oid: 1.3.6.1.2.1.4.24.7.1.6}  # InetAddress, access=r
}
```
</details>

---

## router

_IP routing — global config, per-port L3 interfaces, VLAN router interfaces (VRI)_

### `get_router()`

**Read** | **Protocols:** MOPS, SNMP

```
get_router() -> {
    routing_enabled: False  // bool
    ports: {...}  // dict
    vri: {...}  // dict
}
```

> Sub-table: **`ports`** — key: `port_ifindex`, map: `ifindex`
> Sub-table: **`vri`** — key: `vri_vlan_id`

<details><summary>MOPS sources (12/12 attrs)</summary>

```
MOPS {
  port_ip_address: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIpAddress}  # IpAddress, access=ru
  port_icmp_unreachables: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIcmpUnreachables}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_proxy_arp: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceProxyARPMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  routing_enabled: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpGroup.hm2AgentSwitchIpRoutingMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_ifindex: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIfIndex}  # InterfaceIndex, access=r
  vri_vlan_id: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpVlanEntry.hm2AgentSwitchIpVlanId}  # VlanId, access=r
  vri_ifindex: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpVlanEntry.hm2AgentSwitchIpVlanIfIndex}  # InterfaceIndex, access=ru
  port_directed_broadcast: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceNetdirectedBCMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_mtu: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceMtuValue}  # Unsigned32, access=ru
  port_netmask: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceNetMask}  # IpAddress, access=ru
  port_routing_mode: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceRoutingMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_icmp_redirects: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIcmpRedirects}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (12/12 attrs)</summary>

```
SNMP {
  port_ip_address: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.3}  # IpAddress, access=ru
  port_icmp_unreachables: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.11}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_proxy_arp: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.7}  # HmEnabledStatus, access=ru, allowed=[True, False]
  routing_enabled: {oid: 1.3.6.1.4.1.248.12.2.2.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_ifindex: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.1}  # InterfaceIndex, access=r
  vri_vlan_id: {oid: 1.3.6.1.4.1.248.12.2.2.5.1.1}  # VlanId, access=r
  vri_ifindex: {oid: 1.3.6.1.4.1.248.12.2.2.5.1.2}  # InterfaceIndex, access=ru
  port_directed_broadcast: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.248}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_mtu: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.8}  # Unsigned32, access=ru
  port_netmask: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.4}  # IpAddress, access=ru
  port_routing_mode: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.6}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_icmp_redirects: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.12}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

### `set_router()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (13/13 attrs)</summary>

```
MOPS {
  port_ip_address: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIpAddress}  # IpAddress, access=ru
  port_icmp_unreachables: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIcmpUnreachables}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_proxy_arp: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceProxyARPMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  routing_enabled: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpGroup.hm2AgentSwitchIpRoutingMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_ifindex: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIfIndex}  # InterfaceIndex, access=r
  vri_vlan_id: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpVlanEntry.hm2AgentSwitchIpVlanId}  # VlanId, access=r
  vri_ifindex: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpVlanEntry.hm2AgentSwitchIpVlanIfIndex}  # InterfaceIndex, access=ru
  port_directed_broadcast: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceNetdirectedBCMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_mtu: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceMtuValue}  # Unsigned32, access=ru
  port_netmask: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceNetMask}  # IpAddress, access=ru
  port_routing_mode: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceRoutingMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_icmp_redirects: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIcmpRedirects}  # HmEnabledStatus, access=ru, allowed=[True, False]
  vri_status: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpVlanEntry.hm2AgentSwitchIpVlanRoutingStatus}  # RowStatus, access=crud
}
```
</details>

<details><summary>SNMP sources (13/13 attrs)</summary>

```
SNMP {
  port_ip_address: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.3}  # IpAddress, access=ru
  port_icmp_unreachables: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.11}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_proxy_arp: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.7}  # HmEnabledStatus, access=ru, allowed=[True, False]
  routing_enabled: {oid: 1.3.6.1.4.1.248.12.2.2.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_ifindex: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.1}  # InterfaceIndex, access=r
  vri_vlan_id: {oid: 1.3.6.1.4.1.248.12.2.2.5.1.1}  # VlanId, access=r
  vri_ifindex: {oid: 1.3.6.1.4.1.248.12.2.2.5.1.2}  # InterfaceIndex, access=ru
  port_directed_broadcast: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.248}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_mtu: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.8}  # Unsigned32, access=ru
  port_netmask: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.4}  # IpAddress, access=ru
  port_routing_mode: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.6}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_icmp_redirects: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.12}  # HmEnabledStatus, access=ru, allowed=[True, False]
  vri_status: {oid: 1.3.6.1.4.1.248.12.2.2.5.1.3}  # RowStatus, access=crud
}
```
</details>

### `set_router_port()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (13/13 attrs)</summary>

```
MOPS {
  port_ip_address: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIpAddress}  # IpAddress, access=ru
  port_icmp_unreachables: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIcmpUnreachables}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_proxy_arp: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceProxyARPMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  routing_enabled: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpGroup.hm2AgentSwitchIpRoutingMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_ifindex: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIfIndex}  # InterfaceIndex, access=r
  vri_vlan_id: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpVlanEntry.hm2AgentSwitchIpVlanId}  # VlanId, access=r
  vri_ifindex: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpVlanEntry.hm2AgentSwitchIpVlanIfIndex}  # InterfaceIndex, access=ru
  port_directed_broadcast: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceNetdirectedBCMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_mtu: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceMtuValue}  # Unsigned32, access=ru
  port_netmask: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceNetMask}  # IpAddress, access=ru
  port_routing_mode: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceRoutingMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_icmp_redirects: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIcmpRedirects}  # HmEnabledStatus, access=ru, allowed=[True, False]
  vri_status: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpVlanEntry.hm2AgentSwitchIpVlanRoutingStatus}  # RowStatus, access=crud
}
```
</details>

<details><summary>SNMP sources (13/13 attrs)</summary>

```
SNMP {
  port_ip_address: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.3}  # IpAddress, access=ru
  port_icmp_unreachables: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.11}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_proxy_arp: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.7}  # HmEnabledStatus, access=ru, allowed=[True, False]
  routing_enabled: {oid: 1.3.6.1.4.1.248.12.2.2.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_ifindex: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.1}  # InterfaceIndex, access=r
  vri_vlan_id: {oid: 1.3.6.1.4.1.248.12.2.2.5.1.1}  # VlanId, access=r
  vri_ifindex: {oid: 1.3.6.1.4.1.248.12.2.2.5.1.2}  # InterfaceIndex, access=ru
  port_directed_broadcast: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.248}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_mtu: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.8}  # Unsigned32, access=ru
  port_netmask: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.4}  # IpAddress, access=ru
  port_routing_mode: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.6}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_icmp_redirects: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.12}  # HmEnabledStatus, access=ru, allowed=[True, False]
  vri_status: {oid: 1.3.6.1.4.1.248.12.2.2.5.1.3}  # RowStatus, access=crud
}
```
</details>

### `set_router_vri()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (13/13 attrs)</summary>

```
MOPS {
  port_ip_address: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIpAddress}  # IpAddress, access=ru
  port_icmp_unreachables: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIcmpUnreachables}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_proxy_arp: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceProxyARPMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  routing_enabled: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpGroup.hm2AgentSwitchIpRoutingMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_ifindex: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIfIndex}  # InterfaceIndex, access=r
  vri_vlan_id: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpVlanEntry.hm2AgentSwitchIpVlanId}  # VlanId, access=r
  vri_ifindex: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpVlanEntry.hm2AgentSwitchIpVlanIfIndex}  # InterfaceIndex, access=ru
  port_directed_broadcast: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceNetdirectedBCMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_mtu: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceMtuValue}  # Unsigned32, access=ru
  port_netmask: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceNetMask}  # IpAddress, access=ru
  port_routing_mode: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceRoutingMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_icmp_redirects: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIcmpRedirects}  # HmEnabledStatus, access=ru, allowed=[True, False]
  vri_status: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpVlanEntry.hm2AgentSwitchIpVlanRoutingStatus}  # RowStatus, access=crud
}
```
</details>

<details><summary>SNMP sources (13/13 attrs)</summary>

```
SNMP {
  port_ip_address: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.3}  # IpAddress, access=ru
  port_icmp_unreachables: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.11}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_proxy_arp: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.7}  # HmEnabledStatus, access=ru, allowed=[True, False]
  routing_enabled: {oid: 1.3.6.1.4.1.248.12.2.2.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_ifindex: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.1}  # InterfaceIndex, access=r
  vri_vlan_id: {oid: 1.3.6.1.4.1.248.12.2.2.5.1.1}  # VlanId, access=r
  vri_ifindex: {oid: 1.3.6.1.4.1.248.12.2.2.5.1.2}  # InterfaceIndex, access=ru
  port_directed_broadcast: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.248}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_mtu: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.8}  # Unsigned32, access=ru
  port_netmask: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.4}  # IpAddress, access=ru
  port_routing_mode: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.6}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_icmp_redirects: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.12}  # HmEnabledStatus, access=ru, allowed=[True, False]
  vri_status: {oid: 1.3.6.1.4.1.248.12.2.2.5.1.3}  # RowStatus, access=crud
}
```
</details>

### `create_router_vri()`

**Create** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (13/13 attrs)</summary>

```
MOPS {
  port_ip_address: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIpAddress}  # IpAddress, access=ru
  port_icmp_unreachables: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIcmpUnreachables}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_proxy_arp: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceProxyARPMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  routing_enabled: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpGroup.hm2AgentSwitchIpRoutingMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_ifindex: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIfIndex}  # InterfaceIndex, access=r
  vri_vlan_id: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpVlanEntry.hm2AgentSwitchIpVlanId}  # VlanId, access=r
  vri_ifindex: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpVlanEntry.hm2AgentSwitchIpVlanIfIndex}  # InterfaceIndex, access=ru
  port_directed_broadcast: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceNetdirectedBCMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_mtu: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceMtuValue}  # Unsigned32, access=ru
  port_netmask: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceNetMask}  # IpAddress, access=ru
  port_routing_mode: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceRoutingMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_icmp_redirects: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIcmpRedirects}  # HmEnabledStatus, access=ru, allowed=[True, False]
  vri_status: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpVlanEntry.hm2AgentSwitchIpVlanRoutingStatus}  # RowStatus, access=crud
}
```
</details>

<details><summary>SNMP sources (13/13 attrs)</summary>

```
SNMP {
  port_ip_address: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.3}  # IpAddress, access=ru
  port_icmp_unreachables: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.11}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_proxy_arp: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.7}  # HmEnabledStatus, access=ru, allowed=[True, False]
  routing_enabled: {oid: 1.3.6.1.4.1.248.12.2.2.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_ifindex: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.1}  # InterfaceIndex, access=r
  vri_vlan_id: {oid: 1.3.6.1.4.1.248.12.2.2.5.1.1}  # VlanId, access=r
  vri_ifindex: {oid: 1.3.6.1.4.1.248.12.2.2.5.1.2}  # InterfaceIndex, access=ru
  port_directed_broadcast: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.248}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_mtu: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.8}  # Unsigned32, access=ru
  port_netmask: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.4}  # IpAddress, access=ru
  port_routing_mode: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.6}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_icmp_redirects: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.12}  # HmEnabledStatus, access=ru, allowed=[True, False]
  vri_status: {oid: 1.3.6.1.4.1.248.12.2.2.5.1.3}  # RowStatus, access=crud
}
```
</details>

### `delete_router_vri()`

**Delete** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (13/13 attrs)</summary>

```
MOPS {
  port_ip_address: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIpAddress}  # IpAddress, access=ru
  port_icmp_unreachables: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIcmpUnreachables}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_proxy_arp: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceProxyARPMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  routing_enabled: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpGroup.hm2AgentSwitchIpRoutingMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_ifindex: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIfIndex}  # InterfaceIndex, access=r
  vri_vlan_id: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpVlanEntry.hm2AgentSwitchIpVlanId}  # VlanId, access=r
  vri_ifindex: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpVlanEntry.hm2AgentSwitchIpVlanIfIndex}  # InterfaceIndex, access=ru
  port_directed_broadcast: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceNetdirectedBCMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_mtu: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceMtuValue}  # Unsigned32, access=ru
  port_netmask: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceNetMask}  # IpAddress, access=ru
  port_routing_mode: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceRoutingMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_icmp_redirects: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpInterfaceEntry.hm2AgentSwitchIpInterfaceIcmpRedirects}  # HmEnabledStatus, access=ru, allowed=[True, False]
  vri_status: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSwitchIpVlanEntry.hm2AgentSwitchIpVlanRoutingStatus}  # RowStatus, access=crud
}
```
</details>

<details><summary>SNMP sources (13/13 attrs)</summary>

```
SNMP {
  port_ip_address: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.3}  # IpAddress, access=ru
  port_icmp_unreachables: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.11}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_proxy_arp: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.7}  # HmEnabledStatus, access=ru, allowed=[True, False]
  routing_enabled: {oid: 1.3.6.1.4.1.248.12.2.2.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_ifindex: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.1}  # InterfaceIndex, access=r
  vri_vlan_id: {oid: 1.3.6.1.4.1.248.12.2.2.5.1.1}  # VlanId, access=r
  vri_ifindex: {oid: 1.3.6.1.4.1.248.12.2.2.5.1.2}  # InterfaceIndex, access=ru
  port_directed_broadcast: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.248}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_mtu: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.8}  # Unsigned32, access=ru
  port_netmask: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.4}  # IpAddress, access=ru
  port_routing_mode: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.6}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_icmp_redirects: {oid: 1.3.6.1.4.1.248.12.2.2.3.1.12}  # HmEnabledStatus, access=ru, allowed=[True, False]
  vri_status: {oid: 1.3.6.1.4.1.248.12.2.2.5.1.3}  # RowStatus, access=crud
}
```
</details>

---

## rstp

_Rapid Spanning Tree Protocol (RSTP) configuration_

### `get_rstp()`

**Read** | **Protocols:** MOPS, SNMP

```
get_rstp() -> {
    enabled: False  // bool
    priority: 32768  // int
    hello_time: 2  // int
    max_age: 20  // int
    forward_delay: 15  // int
    bpdu_guard: False  // bool
}
```


<details><summary>MOPS sources (6/6 attrs)</summary>

```
MOPS {
  hello_time: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpCstConfigGroup.hm2AgentStpCstBridgeHelloTime}  # Unsigned32, access=ru, range=1–2
  enabled: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpSwitchConfigGroup.hm2AgentStpAdminMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  forward_delay: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpCstConfigGroup.hm2AgentStpCstBridgeFwdDelay}  # Unsigned32, access=ru, range=4–30
  max_age: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpCstConfigGroup.hm2AgentStpCstBridgeMaxAge}  # Unsigned32, access=ru, range=6–40
  priority: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpCstConfigGroup.hm2AgentStpCstBridgePriority}  # Unsigned32, access=ru, range=0–61440
  bpdu_guard: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpSwitchConfigGroup.hm2AgentStpBpduGuardMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (6/6 attrs)</summary>

```
SNMP {
  hello_time: {oid: 1.3.6.1.4.1.248.12.1.2.15.8.7, method: get}  # Unsigned32, access=ru, range=1–2
  enabled: {oid: 1.3.6.1.4.1.248.12.1.2.15.6, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  forward_delay: {oid: 1.3.6.1.4.1.248.12.1.2.15.8.6, method: get}  # Unsigned32, access=ru, range=4–30
  max_age: {oid: 1.3.6.1.4.1.248.12.1.2.15.8.9, method: get}  # Unsigned32, access=ru, range=6–40
  priority: {oid: 1.3.6.1.4.1.248.12.1.2.15.8.11, method: get}  # Unsigned32, access=ru, range=0–61440
  bpdu_guard: {oid: 1.3.6.1.4.1.248.12.1.2.15.13, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

### `set_rstp()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (9/9 attrs)</summary>

```
MOPS {
  hello_time: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpCstConfigGroup.hm2AgentStpCstBridgeHelloTime}  # Unsigned32, access=ru, range=1–2
  enabled: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpSwitchConfigGroup.hm2AgentStpAdminMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  forward_delay: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpCstConfigGroup.hm2AgentStpCstBridgeFwdDelay}  # Unsigned32, access=ru, range=4–30
  port_path_cost: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpCstPortEntry.hm2AgentStpCstPortPathCost}  # Unsigned32, access=ru, range=0–200000000
  max_age: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpCstConfigGroup.hm2AgentStpCstBridgeMaxAge}  # Unsigned32, access=ru, range=6–40
  priority: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpCstConfigGroup.hm2AgentStpCstBridgePriority}  # Unsigned32, access=ru, range=0–61440
  bpdu_guard: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpSwitchConfigGroup.hm2AgentStpBpduGuardMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_priority: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpCstPortEntry.hm2AgentStpCstPortPriority}  # Unsigned32, access=ru, range=0–240
  edge_port: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpCstPortEntry.hm2AgentStpCstPortEdge}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (9/9 attrs)</summary>

```
SNMP {
  hello_time: {oid: 1.3.6.1.4.1.248.12.1.2.15.8.7, method: get}  # Unsigned32, access=ru, range=1–2
  enabled: {oid: 1.3.6.1.4.1.248.12.1.2.15.6, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  forward_delay: {oid: 1.3.6.1.4.1.248.12.1.2.15.8.6, method: get}  # Unsigned32, access=ru, range=4–30
  port_path_cost: {oid: 1.3.6.1.4.1.248.12.1.2.15.9.1.7}  # Unsigned32, access=ru, range=0–200000000
  max_age: {oid: 1.3.6.1.4.1.248.12.1.2.15.8.9, method: get}  # Unsigned32, access=ru, range=6–40
  priority: {oid: 1.3.6.1.4.1.248.12.1.2.15.8.11, method: get}  # Unsigned32, access=ru, range=0–61440
  bpdu_guard: {oid: 1.3.6.1.4.1.248.12.1.2.15.13, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_priority: {oid: 1.3.6.1.4.1.248.12.1.2.15.9.1.8}  # Unsigned32, access=ru, range=0–240
  edge_port: {oid: 1.3.6.1.4.1.248.12.1.2.15.9.1.4}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

### `get_rstp_port()`

**Read** | **Protocols:** MOPS, SNMP
Primary key: `enabled` | Key map: `ifindex`

```
get_rstp_port() -> {
    enabled: False  // bool
    priority: 128  // int
    path_cost: 0  // int
    edge_port: False  // bool
}
```


<details><summary>MOPS sources (3/3 attrs)</summary>

```
MOPS {
  enabled: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpSwitchConfigGroup.hm2AgentStpAdminMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  priority: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpCstConfigGroup.hm2AgentStpCstBridgePriority}  # Unsigned32, access=ru, range=0–61440
  edge_port: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpCstPortEntry.hm2AgentStpCstPortEdge}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (3/3 attrs)</summary>

```
SNMP {
  enabled: {oid: 1.3.6.1.4.1.248.12.1.2.15.6, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  priority: {oid: 1.3.6.1.4.1.248.12.1.2.15.8.11, method: get}  # Unsigned32, access=ru, range=0–61440
  edge_port: {oid: 1.3.6.1.4.1.248.12.1.2.15.9.1.4}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

### `set_rstp_port()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (9/9 attrs)</summary>

```
MOPS {
  hello_time: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpCstConfigGroup.hm2AgentStpCstBridgeHelloTime}  # Unsigned32, access=ru, range=1–2
  enabled: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpSwitchConfigGroup.hm2AgentStpAdminMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  forward_delay: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpCstConfigGroup.hm2AgentStpCstBridgeFwdDelay}  # Unsigned32, access=ru, range=4–30
  port_path_cost: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpCstPortEntry.hm2AgentStpCstPortPathCost}  # Unsigned32, access=ru, range=0–200000000
  max_age: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpCstConfigGroup.hm2AgentStpCstBridgeMaxAge}  # Unsigned32, access=ru, range=6–40
  priority: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpCstConfigGroup.hm2AgentStpCstBridgePriority}  # Unsigned32, access=ru, range=0–61440
  bpdu_guard: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpSwitchConfigGroup.hm2AgentStpBpduGuardMode}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_priority: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpCstPortEntry.hm2AgentStpCstPortPriority}  # Unsigned32, access=ru, range=0–240
  edge_port: {HM2-PLATFORM-SWITCHING-MIB / hm2AgentStpCstPortEntry.hm2AgentStpCstPortEdge}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (9/9 attrs)</summary>

```
SNMP {
  hello_time: {oid: 1.3.6.1.4.1.248.12.1.2.15.8.7, method: get}  # Unsigned32, access=ru, range=1–2
  enabled: {oid: 1.3.6.1.4.1.248.12.1.2.15.6, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  forward_delay: {oid: 1.3.6.1.4.1.248.12.1.2.15.8.6, method: get}  # Unsigned32, access=ru, range=4–30
  port_path_cost: {oid: 1.3.6.1.4.1.248.12.1.2.15.9.1.7}  # Unsigned32, access=ru, range=0–200000000
  max_age: {oid: 1.3.6.1.4.1.248.12.1.2.15.8.9, method: get}  # Unsigned32, access=ru, range=6–40
  priority: {oid: 1.3.6.1.4.1.248.12.1.2.15.8.11, method: get}  # Unsigned32, access=ru, range=0–61440
  bpdu_guard: {oid: 1.3.6.1.4.1.248.12.1.2.15.13, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port_priority: {oid: 1.3.6.1.4.1.248.12.1.2.15.9.1.8}  # Unsigned32, access=ru, range=0–240
  edge_port: {oid: 1.3.6.1.4.1.248.12.1.2.15.9.1.4}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

---

## services

_Network services management (HTTP, HTTPS, Telnet, SSH, SNMP)_

### `get_services()`

**Read** | **Protocols:** MOPS, SNMP

```
get_services() -> {
    http: {...}  // dict
    https: {...}  // dict
    telnet: {...}  // dict
    ssh: {...}  // dict
    snmp_v1: {...}  // dict
    snmp_v2: {...}  // dict
    snmp_v3: {...}  // dict
}
```

> Sub-table: **`http`** — key: `http_enabled`
> Sub-table: **`https`** — key: `https_enabled`
> Sub-table: **`telnet`** — key: `telnet_enabled`
> Sub-table: **`ssh`** — key: `ssh_enabled`
> Sub-table: **`snmp_v1`** — key: `snmp_v1_enabled`
> Sub-table: **`snmp_v2`** — key: `snmp_v2_enabled`
> Sub-table: **`snmp_v3`** — key: `snmp_v3_enabled`

<details><summary>MOPS sources (11/11 attrs)</summary>

```
MOPS {
  snmp_v3_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSnmpGroup.hm2SnmpV3AdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  http_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessWebGroup.hm2WebHttpAdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  snmp_v2_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSnmpGroup.hm2SnmpV2AdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  https_port: {HM2-MGMTACCESS-MIB / hm2MgmtAccessWebGroup.hm2WebHttpsPortNumber}  # InetPortNumber, access=ru
  http_port: {HM2-MGMTACCESS-MIB / hm2MgmtAccessWebGroup.hm2WebHttpPortNumber}  # InetPortNumber, access=ru
  ssh_port: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSshGroup.hm2SshPortNumber}  # InetPortNumber, access=ru
  https_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessWebGroup.hm2WebHttpsAdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  telnet_port: {HM2-MGMTACCESS-MIB / hm2MgmtAccessTelnetGroup.hm2TelnetServerPort}  # InetPortNumber, access=ru
  telnet_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessTelnetGroup.hm2TelnetServerAdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  snmp_v1_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSnmpGroup.hm2SnmpV1AdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ssh_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSshGroup.hm2SshAdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (11/11 attrs)</summary>

```
SNMP {
  snmp_v3_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.1.3, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  http_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.2.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  snmp_v2_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.1.2, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  https_port: {oid: 1.3.6.1.4.1.248.11.25.1.2.4, method: get}  # InetPortNumber, access=ru
  http_port: {oid: 1.3.6.1.4.1.248.11.25.1.2.3, method: get}  # InetPortNumber, access=ru
  ssh_port: {oid: 1.3.6.1.4.1.248.11.25.1.4.3, method: get}  # InetPortNumber, access=ru
  https_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.2.2, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  telnet_port: {oid: 1.3.6.1.4.1.248.11.25.1.3.2, method: get}  # InetPortNumber, access=ru
  telnet_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.3.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  snmp_v1_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.1.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ssh_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.4.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

### `set_services()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (12/12 attrs)</summary>

```
MOPS {
  snmp_v3_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSnmpGroup.hm2SnmpV3AdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  http_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessWebGroup.hm2WebHttpAdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  snmp_v2_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSnmpGroup.hm2SnmpV2AdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ssh_port: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSshGroup.hm2SshPortNumber}  # InetPortNumber, access=ru
  https_port: {HM2-MGMTACCESS-MIB / hm2MgmtAccessWebGroup.hm2WebHttpsPortNumber}  # InetPortNumber, access=ru
  http_port: {HM2-MGMTACCESS-MIB / hm2MgmtAccessWebGroup.hm2WebHttpPortNumber}  # InetPortNumber, access=ru
  snmp_port: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSnmpGroup.hm2SnmpPortNumber}  # InetPortNumber, access=ru
  https_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessWebGroup.hm2WebHttpsAdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  telnet_port: {HM2-MGMTACCESS-MIB / hm2MgmtAccessTelnetGroup.hm2TelnetServerPort}  # InetPortNumber, access=ru
  telnet_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessTelnetGroup.hm2TelnetServerAdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  snmp_v1_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSnmpGroup.hm2SnmpV1AdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ssh_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSshGroup.hm2SshAdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (12/12 attrs)</summary>

```
SNMP {
  snmp_v3_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.1.3, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  http_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.2.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  snmp_v2_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.1.2, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ssh_port: {oid: 1.3.6.1.4.1.248.11.25.1.4.3, method: get}  # InetPortNumber, access=ru
  https_port: {oid: 1.3.6.1.4.1.248.11.25.1.2.4, method: get}  # InetPortNumber, access=ru
  http_port: {oid: 1.3.6.1.4.1.248.11.25.1.2.3, method: get}  # InetPortNumber, access=ru
  snmp_port: {oid: 1.3.6.1.4.1.248.11.25.1.1.4, method: get}  # InetPortNumber, access=ru
  https_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.2.2, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  telnet_port: {oid: 1.3.6.1.4.1.248.11.25.1.3.2, method: get}  # InetPortNumber, access=ru
  telnet_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.3.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  snmp_v1_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.1.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  ssh_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.4.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

---

## session_config

_Management session timeouts and limits_

### `get_session_config()`

**Read** | **Protocols:** MOPS, SNMP

```
get_session_config() -> {
    ssh_timeout: 0  // int
    telnet_timeout: 0  // int
    web_timeout: 0  // int
    max_ssh_sessions: 0  // int
}
```


<details><summary>MOPS sources (4/4 attrs)</summary>

```
MOPS {
  max_ssh_sessions: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSshGroup.hm2SshMaxSessionsCount}  # Integer32, access=ru, range=1–5
  telnet_timeout: {HM2-MGMTACCESS-MIB / hm2MgmtAccessTelnetGroup.hm2TelnetServerSessionsTimeOut}  # Integer32, access=ru, range=0–160
  web_timeout: {HM2-MGMTACCESS-MIB / hm2MgmtAccessWebGroup.hm2WebIntfTimeOut}  # Integer32, access=ru, range=0–160
  ssh_timeout: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSshGroup.hm2SshSessionTimeout}  # Integer32, access=ru, range=0–160
}
```
</details>

<details><summary>SNMP sources (4/4 attrs)</summary>

```
SNMP {
  max_ssh_sessions: {oid: 1.3.6.1.4.1.248.11.25.1.4.5, method: get}  # Integer32, access=ru, range=1–5
  telnet_timeout: {oid: 1.3.6.1.4.1.248.11.25.1.3.5, method: get}  # Integer32, access=ru, range=0–160
  web_timeout: {oid: 1.3.6.1.4.1.248.11.25.1.2.8, method: get}  # Integer32, access=ru, range=0–160
  ssh_timeout: {oid: 1.3.6.1.4.1.248.11.25.1.4.6, method: get}  # Integer32, access=ru, range=0–160
}
```
</details>

### `set_session_config()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (4/4 attrs)</summary>

```
MOPS {
  max_ssh_sessions: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSshGroup.hm2SshMaxSessionsCount}  # Integer32, access=ru, range=1–5
  telnet_timeout: {HM2-MGMTACCESS-MIB / hm2MgmtAccessTelnetGroup.hm2TelnetServerSessionsTimeOut}  # Integer32, access=ru, range=0–160
  web_timeout: {HM2-MGMTACCESS-MIB / hm2MgmtAccessWebGroup.hm2WebIntfTimeOut}  # Integer32, access=ru, range=0–160
  ssh_timeout: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSshGroup.hm2SshSessionTimeout}  # Integer32, access=ru, range=0–160
}
```
</details>

<details><summary>SNMP sources (4/4 attrs)</summary>

```
SNMP {
  max_ssh_sessions: {oid: 1.3.6.1.4.1.248.11.25.1.4.5, method: get}  # Integer32, access=ru, range=1–5
  telnet_timeout: {oid: 1.3.6.1.4.1.248.11.25.1.3.5, method: get}  # Integer32, access=ru, range=0–160
  web_timeout: {oid: 1.3.6.1.4.1.248.11.25.1.2.8, method: get}  # Integer32, access=ru, range=0–160
  ssh_timeout: {oid: 1.3.6.1.4.1.248.11.25.1.4.6, method: get}  # Integer32, access=ru, range=0–160
}
```
</details>

---

## sflow

_sFlow receiver, per-port sampler, and per-port poller configuration_

### `get_sflow_receiver()`

**Read** | **Protocols:** MOPS, SNMP
Primary key: `receiver_index`

```
get_sflow_receiver() -> {
    receiver_index: 0  // int
    owner: ""  // str
    timeout: 0  // int
    max_datagram_size: 1400  // int
    address: ""  // str
    port: 6343  // int
    datagram_version: 5  // int
}
```


<details><summary>MOPS sources (7/7 attrs)</summary>

```
MOPS {
  port: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrPort}  # Integer32, access=ru
  receiver_index: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrIndex}  # Integer32, access=r, range=1–65535
  owner: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrOwner}  # OwnerString, access=ru
  timeout: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrTimeout}  # Integer32, access=ru, range=-1–2147483647
  address: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrAddress}  # InetAddress, access=ru
  max_datagram_size: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrMaximumDatagramSize}  # Integer32, access=ru
  datagram_version: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrDatagramVersion}  # Integer32, access=ru
}
```
</details>

<details><summary>SNMP sources (7/7 attrs)</summary>

```
SNMP {
  port: {oid: 1.3.6.1.4.1.14706.1.1.4.1.7}  # Integer32, access=ru
  receiver_index: {oid: 1.3.6.1.4.1.14706.1.1.4.1.1}  # Integer32, access=r, range=1–65535
  owner: {oid: 1.3.6.1.4.1.14706.1.1.4.1.2}  # OwnerString, access=ru
  timeout: {oid: 1.3.6.1.4.1.14706.1.1.4.1.3}  # Integer32, access=ru, range=-1–2147483647
  address: {oid: 1.3.6.1.4.1.14706.1.1.4.1.6}  # InetAddress, access=ru
  max_datagram_size: {oid: 1.3.6.1.4.1.14706.1.1.4.1.4}  # Integer32, access=ru
  datagram_version: {oid: 1.3.6.1.4.1.14706.1.1.4.1.8}  # Integer32, access=ru
}
```
</details>

### `set_sflow_receiver()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (14/14 attrs)</summary>

```
MOPS {
  port: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrPort}  # Integer32, access=ru
  sampler_datasource: {SFLOW-MIB / sFlowFsEntry.sFlowFsDataSource}  # SFlowDataSource, access=r
  receiver_index: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrIndex}  # Integer32, access=r, range=1–65535
  sampler_receiver: {SFLOW-MIB / sFlowFsEntry.sFlowFsReceiver}  # SFlowReceiver, access=ru
  max_header_size: {SFLOW-MIB / sFlowFsEntry.sFlowFsMaximumHeaderSize}  # Integer32, access=ru
  owner: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrOwner}  # OwnerString, access=ru
  timeout: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrTimeout}  # Integer32, access=ru, range=-1–2147483647
  interval: {SFLOW-MIB / sFlowCpEntry.sFlowCpInterval}  # Integer32, access=ru
  address: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrAddress}  # InetAddress, access=ru
  max_datagram_size: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrMaximumDatagramSize}  # Integer32, access=ru
  datagram_version: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrDatagramVersion}  # Integer32, access=ru
  sampling_rate: {SFLOW-MIB / sFlowFsEntry.sFlowFsPacketSamplingRate}  # Integer32, access=ru
  poller_datasource: {SFLOW-MIB / sFlowCpEntry.sFlowCpDataSource}  # SFlowDataSource, access=r
  poller_receiver: {SFLOW-MIB / sFlowCpEntry.sFlowCpReceiver}  # SFlowReceiver, access=ru
}
```
</details>

<details><summary>SNMP sources (14/14 attrs)</summary>

```
SNMP {
  port: {oid: 1.3.6.1.4.1.14706.1.1.4.1.7}  # Integer32, access=ru
  sampler_datasource: {oid: 1.3.6.1.4.1.14706.1.1.5.1.1}  # SFlowDataSource, access=r
  receiver_index: {oid: 1.3.6.1.4.1.14706.1.1.4.1.1}  # Integer32, access=r, range=1–65535
  sampler_receiver: {oid: 1.3.6.1.4.1.14706.1.1.5.1.3}  # SFlowReceiver, access=ru
  max_header_size: {oid: 1.3.6.1.4.1.14706.1.1.5.1.5}  # Integer32, access=ru
  owner: {oid: 1.3.6.1.4.1.14706.1.1.4.1.2}  # OwnerString, access=ru
  timeout: {oid: 1.3.6.1.4.1.14706.1.1.4.1.3}  # Integer32, access=ru, range=-1–2147483647
  interval: {oid: 1.3.6.1.4.1.14706.1.1.6.1.4}  # Integer32, access=ru
  address: {oid: 1.3.6.1.4.1.14706.1.1.4.1.6}  # InetAddress, access=ru
  max_datagram_size: {oid: 1.3.6.1.4.1.14706.1.1.4.1.4}  # Integer32, access=ru
  datagram_version: {oid: 1.3.6.1.4.1.14706.1.1.4.1.8}  # Integer32, access=ru
  sampling_rate: {oid: 1.3.6.1.4.1.14706.1.1.5.1.4}  # Integer32, access=ru
  poller_datasource: {oid: 1.3.6.1.4.1.14706.1.1.6.1.1}  # SFlowDataSource, access=r
  poller_receiver: {oid: 1.3.6.1.4.1.14706.1.1.6.1.3}  # SFlowReceiver, access=ru
}
```
</details>

### `get_sflow_sampler()`

**Read** | **Protocols:** MOPS, SNMP
Primary key: `sampler_datasource`

```
get_sflow_sampler() -> {
    sampler_datasource: ""  // str
    sampler_receiver: 0  // int
    sampling_rate: 0  // int
    max_header_size: 128  // int
}
```


<details><summary>MOPS sources (4/4 attrs)</summary>

```
MOPS {
  sampler_datasource: {SFLOW-MIB / sFlowFsEntry.sFlowFsDataSource}  # SFlowDataSource, access=r
  sampler_receiver: {SFLOW-MIB / sFlowFsEntry.sFlowFsReceiver}  # SFlowReceiver, access=ru
  max_header_size: {SFLOW-MIB / sFlowFsEntry.sFlowFsMaximumHeaderSize}  # Integer32, access=ru
  sampling_rate: {SFLOW-MIB / sFlowFsEntry.sFlowFsPacketSamplingRate}  # Integer32, access=ru
}
```
</details>

<details><summary>SNMP sources (4/4 attrs)</summary>

```
SNMP {
  sampler_datasource: {oid: 1.3.6.1.4.1.14706.1.1.5.1.1}  # SFlowDataSource, access=r
  sampler_receiver: {oid: 1.3.6.1.4.1.14706.1.1.5.1.3}  # SFlowReceiver, access=ru
  max_header_size: {oid: 1.3.6.1.4.1.14706.1.1.5.1.5}  # Integer32, access=ru
  sampling_rate: {oid: 1.3.6.1.4.1.14706.1.1.5.1.4}  # Integer32, access=ru
}
```
</details>

### `set_sflow_sampler()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (14/14 attrs)</summary>

```
MOPS {
  port: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrPort}  # Integer32, access=ru
  sampler_datasource: {SFLOW-MIB / sFlowFsEntry.sFlowFsDataSource}  # SFlowDataSource, access=r
  receiver_index: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrIndex}  # Integer32, access=r, range=1–65535
  sampler_receiver: {SFLOW-MIB / sFlowFsEntry.sFlowFsReceiver}  # SFlowReceiver, access=ru
  max_header_size: {SFLOW-MIB / sFlowFsEntry.sFlowFsMaximumHeaderSize}  # Integer32, access=ru
  owner: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrOwner}  # OwnerString, access=ru
  timeout: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrTimeout}  # Integer32, access=ru, range=-1–2147483647
  interval: {SFLOW-MIB / sFlowCpEntry.sFlowCpInterval}  # Integer32, access=ru
  address: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrAddress}  # InetAddress, access=ru
  max_datagram_size: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrMaximumDatagramSize}  # Integer32, access=ru
  datagram_version: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrDatagramVersion}  # Integer32, access=ru
  sampling_rate: {SFLOW-MIB / sFlowFsEntry.sFlowFsPacketSamplingRate}  # Integer32, access=ru
  poller_datasource: {SFLOW-MIB / sFlowCpEntry.sFlowCpDataSource}  # SFlowDataSource, access=r
  poller_receiver: {SFLOW-MIB / sFlowCpEntry.sFlowCpReceiver}  # SFlowReceiver, access=ru
}
```
</details>

<details><summary>SNMP sources (14/14 attrs)</summary>

```
SNMP {
  port: {oid: 1.3.6.1.4.1.14706.1.1.4.1.7}  # Integer32, access=ru
  sampler_datasource: {oid: 1.3.6.1.4.1.14706.1.1.5.1.1}  # SFlowDataSource, access=r
  receiver_index: {oid: 1.3.6.1.4.1.14706.1.1.4.1.1}  # Integer32, access=r, range=1–65535
  sampler_receiver: {oid: 1.3.6.1.4.1.14706.1.1.5.1.3}  # SFlowReceiver, access=ru
  max_header_size: {oid: 1.3.6.1.4.1.14706.1.1.5.1.5}  # Integer32, access=ru
  owner: {oid: 1.3.6.1.4.1.14706.1.1.4.1.2}  # OwnerString, access=ru
  timeout: {oid: 1.3.6.1.4.1.14706.1.1.4.1.3}  # Integer32, access=ru, range=-1–2147483647
  interval: {oid: 1.3.6.1.4.1.14706.1.1.6.1.4}  # Integer32, access=ru
  address: {oid: 1.3.6.1.4.1.14706.1.1.4.1.6}  # InetAddress, access=ru
  max_datagram_size: {oid: 1.3.6.1.4.1.14706.1.1.4.1.4}  # Integer32, access=ru
  datagram_version: {oid: 1.3.6.1.4.1.14706.1.1.4.1.8}  # Integer32, access=ru
  sampling_rate: {oid: 1.3.6.1.4.1.14706.1.1.5.1.4}  # Integer32, access=ru
  poller_datasource: {oid: 1.3.6.1.4.1.14706.1.1.6.1.1}  # SFlowDataSource, access=r
  poller_receiver: {oid: 1.3.6.1.4.1.14706.1.1.6.1.3}  # SFlowReceiver, access=ru
}
```
</details>

### `get_sflow_poller()`

**Read** | **Protocols:** MOPS, SNMP
Primary key: `poller_datasource` | Key map: `ifindex`

```
get_sflow_poller() -> {
    poller_datasource: ""  // str
    poller_receiver: 0  // int
    interval: 0  // int
}
```


<details><summary>MOPS sources (3/3 attrs)</summary>

```
MOPS {
  interval: {SFLOW-MIB / sFlowCpEntry.sFlowCpInterval}  # Integer32, access=ru
  poller_datasource: {SFLOW-MIB / sFlowCpEntry.sFlowCpDataSource}  # SFlowDataSource, access=r
  poller_receiver: {SFLOW-MIB / sFlowCpEntry.sFlowCpReceiver}  # SFlowReceiver, access=ru
}
```
</details>

<details><summary>SNMP sources (3/3 attrs)</summary>

```
SNMP {
  interval: {oid: 1.3.6.1.4.1.14706.1.1.6.1.4}  # Integer32, access=ru
  poller_datasource: {oid: 1.3.6.1.4.1.14706.1.1.6.1.1}  # SFlowDataSource, access=r
  poller_receiver: {oid: 1.3.6.1.4.1.14706.1.1.6.1.3}  # SFlowReceiver, access=ru
}
```
</details>

### `set_sflow_poller()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (14/14 attrs)</summary>

```
MOPS {
  port: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrPort}  # Integer32, access=ru
  sampler_datasource: {SFLOW-MIB / sFlowFsEntry.sFlowFsDataSource}  # SFlowDataSource, access=r
  receiver_index: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrIndex}  # Integer32, access=r, range=1–65535
  sampler_receiver: {SFLOW-MIB / sFlowFsEntry.sFlowFsReceiver}  # SFlowReceiver, access=ru
  max_header_size: {SFLOW-MIB / sFlowFsEntry.sFlowFsMaximumHeaderSize}  # Integer32, access=ru
  owner: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrOwner}  # OwnerString, access=ru
  timeout: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrTimeout}  # Integer32, access=ru, range=-1–2147483647
  interval: {SFLOW-MIB / sFlowCpEntry.sFlowCpInterval}  # Integer32, access=ru
  address: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrAddress}  # InetAddress, access=ru
  max_datagram_size: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrMaximumDatagramSize}  # Integer32, access=ru
  datagram_version: {SFLOW-MIB / sFlowRcvrEntry.sFlowRcvrDatagramVersion}  # Integer32, access=ru
  sampling_rate: {SFLOW-MIB / sFlowFsEntry.sFlowFsPacketSamplingRate}  # Integer32, access=ru
  poller_datasource: {SFLOW-MIB / sFlowCpEntry.sFlowCpDataSource}  # SFlowDataSource, access=r
  poller_receiver: {SFLOW-MIB / sFlowCpEntry.sFlowCpReceiver}  # SFlowReceiver, access=ru
}
```
</details>

<details><summary>SNMP sources (14/14 attrs)</summary>

```
SNMP {
  port: {oid: 1.3.6.1.4.1.14706.1.1.4.1.7}  # Integer32, access=ru
  sampler_datasource: {oid: 1.3.6.1.4.1.14706.1.1.5.1.1}  # SFlowDataSource, access=r
  receiver_index: {oid: 1.3.6.1.4.1.14706.1.1.4.1.1}  # Integer32, access=r, range=1–65535
  sampler_receiver: {oid: 1.3.6.1.4.1.14706.1.1.5.1.3}  # SFlowReceiver, access=ru
  max_header_size: {oid: 1.3.6.1.4.1.14706.1.1.5.1.5}  # Integer32, access=ru
  owner: {oid: 1.3.6.1.4.1.14706.1.1.4.1.2}  # OwnerString, access=ru
  timeout: {oid: 1.3.6.1.4.1.14706.1.1.4.1.3}  # Integer32, access=ru, range=-1–2147483647
  interval: {oid: 1.3.6.1.4.1.14706.1.1.6.1.4}  # Integer32, access=ru
  address: {oid: 1.3.6.1.4.1.14706.1.1.4.1.6}  # InetAddress, access=ru
  max_datagram_size: {oid: 1.3.6.1.4.1.14706.1.1.4.1.4}  # Integer32, access=ru
  datagram_version: {oid: 1.3.6.1.4.1.14706.1.1.4.1.8}  # Integer32, access=ru
  sampling_rate: {oid: 1.3.6.1.4.1.14706.1.1.5.1.4}  # Integer32, access=ru
  poller_datasource: {oid: 1.3.6.1.4.1.14706.1.1.6.1.1}  # SFlowDataSource, access=r
  poller_receiver: {oid: 1.3.6.1.4.1.14706.1.1.6.1.3}  # SFlowReceiver, access=ru
}
```
</details>

---

## signal_contact

_Signal contact (relay) per-contact configuration, sense flags, and status_

### `get_signal_contact()`

**Read** | **Protocols:** MOPS, SNMP
Primary key: `contact_id`

```
get_signal_contact() -> {
    contact_id: 0  // int
    mode: "monitor"  // "manual" | "monitor" | "deviceState" | "deviceSecurity" | "deviceStateAndSecurity"
    state: "closed"  // "open" | "closed"
    trap_enabled: False  // bool
    sense_link_failure: False  // bool
    sense_temperature: False  // bool
    sense_fan: False  // bool
    sense_fan_module: False  // bool
    sense_module: False  // bool
    sense_module_removal: False  // bool
    sense_ps_state: False  // bool
    sense_envm_removal: False  // bool
    sense_envm_not_in_sync: False  // bool
    sense_ring_redundancy: False  // bool
    sense_ethernet_loops: False  // bool
    sense_humidity: False  // bool
    sense_stp_port_block: False  // bool
    sense_if_link_alarm: False  // bool
}
```


<details><summary>MOPS sources (18/18 attrs)</summary>

```
MOPS {
  sense_ethernet_loops: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConSenseEthernetLoops}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mode: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConMode}  # INTEGER, access=ru, allowed=['manual', 'monitor', 'deviceState', 'deviceSecurity', 'deviceStateAndSecurity']
  sense_ps_state: {HM2-DIAGNOSTIC-MIB / hm2SigConPSEntry.hm2SigConSensePSState}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_module_removal: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConSenseModuleRemoval}  # HmEnabledStatus, access=ru, allowed=[True, False]
  trap_enabled: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConTrapEnable}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_module: {HM2-DIAGNOSTIC-MIB / hm2SigConModuleEntry.hm2SigConSenseModule}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_if_link_alarm: {HM2-DIAGNOSTIC-MIB / hm2SigConInterfaceEntry.hm2SigConSenseIfLinkAlarm}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_humidity: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConSenseHumidity}  # HmEnabledStatus, access=ru, allowed=[True, False]
  contact_id: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConID}  # Integer32, access=r, range=1–2
  sense_envm_not_in_sync: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConSenseExtNvmNotInSync}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_ring_redundancy: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConSenseRingRedundancy}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_fan: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConSenseFan}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_fan_module: {HM2-DIAGNOSTIC-MIB / hm2SigConFanModuleEntry.hm2SigConSenseFanModule}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_stp_port_block: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConSenseStpPortBlock}  # HmEnabledStatus, access=ru, allowed=[True, False]
  state: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConOperState}  # INTEGER, access=r, allowed=['open', 'close']
  sense_envm_removal: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConSenseExtNvmRemoval}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_link_failure: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConSenseLinkFailure}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_temperature: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConSenseTemperature}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (18/18 attrs)</summary>

```
SNMP {
  sense_ethernet_loops: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.16}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mode: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.5}  # INTEGER, access=ru, allowed=['manual', 'monitor', 'deviceState', 'deviceSecurity', 'deviceStateAndSecurity']
  sense_ps_state: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.2.1.1}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_module_removal: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.12}  # HmEnabledStatus, access=ru, allowed=[True, False]
  trap_enabled: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.2}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_module: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.4.1.2}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_if_link_alarm: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.3.1.1}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_humidity: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.17}  # HmEnabledStatus, access=ru, allowed=[True, False]
  contact_id: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.1}  # Integer32, access=r, range=1–2
  sense_envm_not_in_sync: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.14}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_ring_redundancy: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.15}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_fan: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.11}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_fan_module: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.5.1.2}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_stp_port_block: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.18}  # HmEnabledStatus, access=ru, allowed=[True, False]
  state: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.6}  # INTEGER, access=r, allowed=['open', 'close']
  sense_envm_removal: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.13}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_link_failure: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.9}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_temperature: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.10}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

### `set_signal_contact()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (18/18 attrs)</summary>

```
MOPS {
  sense_ethernet_loops: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConSenseEthernetLoops}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mode: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConMode}  # INTEGER, access=ru, allowed=['manual', 'monitor', 'deviceState', 'deviceSecurity', 'deviceStateAndSecurity']
  sense_ps_state: {HM2-DIAGNOSTIC-MIB / hm2SigConPSEntry.hm2SigConSensePSState}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_module_removal: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConSenseModuleRemoval}  # HmEnabledStatus, access=ru, allowed=[True, False]
  trap_enabled: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConTrapEnable}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_module: {HM2-DIAGNOSTIC-MIB / hm2SigConModuleEntry.hm2SigConSenseModule}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_if_link_alarm: {HM2-DIAGNOSTIC-MIB / hm2SigConInterfaceEntry.hm2SigConSenseIfLinkAlarm}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_humidity: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConSenseHumidity}  # HmEnabledStatus, access=ru, allowed=[True, False]
  contact_id: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConID}  # Integer32, access=r, range=1–2
  sense_envm_not_in_sync: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConSenseExtNvmNotInSync}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_ring_redundancy: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConSenseRingRedundancy}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_fan: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConSenseFan}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_fan_module: {HM2-DIAGNOSTIC-MIB / hm2SigConFanModuleEntry.hm2SigConSenseFanModule}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_stp_port_block: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConSenseStpPortBlock}  # HmEnabledStatus, access=ru, allowed=[True, False]
  state: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConOperState}  # INTEGER, access=r, allowed=['open', 'close']
  sense_envm_removal: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConSenseExtNvmRemoval}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_link_failure: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConSenseLinkFailure}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_temperature: {HM2-DIAGNOSTIC-MIB / hm2SigConCommonEntry.hm2SigConSenseTemperature}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (18/18 attrs)</summary>

```
SNMP {
  sense_ethernet_loops: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.16}  # HmEnabledStatus, access=ru, allowed=[True, False]
  mode: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.5}  # INTEGER, access=ru, allowed=['manual', 'monitor', 'deviceState', 'deviceSecurity', 'deviceStateAndSecurity']
  sense_ps_state: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.2.1.1}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_module_removal: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.12}  # HmEnabledStatus, access=ru, allowed=[True, False]
  trap_enabled: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.2}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_module: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.4.1.2}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_if_link_alarm: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.3.1.1}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_humidity: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.17}  # HmEnabledStatus, access=ru, allowed=[True, False]
  contact_id: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.1}  # Integer32, access=r, range=1–2
  sense_envm_not_in_sync: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.14}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_ring_redundancy: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.15}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_fan: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.11}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_fan_module: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.5.1.2}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_stp_port_block: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.18}  # HmEnabledStatus, access=ru, allowed=[True, False]
  state: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.6}  # INTEGER, access=r, allowed=['open', 'close']
  sense_envm_removal: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.13}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_link_failure: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.9}  # HmEnabledStatus, access=ru, allowed=[True, False]
  sense_temperature: {oid: 1.3.6.1.4.1.248.11.22.1.3.1.1.1.10}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

---

## snmp

_SNMP configuration — versions, port, communities, trap destinations_

### `get_snmp_config()`

**Read** | **Protocols:** MOPS, SNMP, SSH

```
get_snmp_config() -> {
    v1_enabled: False  // bool
    v2_enabled: False  // bool
    v3_enabled: False  // bool
    port: 161  // int
    trap_service: False  // bool
    community_access: {...}  // dict
    trap_destinations: [...]  // list
}
```


<details><summary>MOPS sources (7/7 attrs)</summary>

```
MOPS {
  v2_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSnmpGroup.hm2SnmpV2AdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSnmpGroup.hm2SnmpPortNumber}  # InetPortNumber, access=ru
  community_access: {SNMP-VIEW-BASED-ACM-MIB / vacmAccessEntry.vacmAccessWriteViewName}  # SnmpAdminString, access=ru, range=0–32
  trap_service: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSnmpGroup.hm2SnmpTrapServiceAdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  v3_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSnmpGroup.hm2SnmpV3AdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  trap_destinations: {SNMP-TARGET-MIB / snmpTargetAddrEntry.snmpTargetAddrName}  # SnmpAdminString, access=r, range=1–32
  v1_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSnmpGroup.hm2SnmpV1AdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (7/7 attrs)</summary>

```
SNMP {
  v2_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.1.2, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port: {oid: 1.3.6.1.4.1.248.11.25.1.1.4, method: get}  # InetPortNumber, access=ru
  community_access: {oid: 1.3.6.1.6.3.16.1.4.1.6}  # SnmpAdminString, access=ru, range=0–32
  trap_service: {oid: 1.3.6.1.4.1.248.11.25.1.1.6, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  v3_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.1.3, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  trap_destinations: {oid: 1.3.6.1.6.3.12.1.2.1.1}  # SnmpAdminString, access=r, range=1–32
  v1_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.1.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SSH sources (1/7 attrs)</summary>

```
SSH {
  trap_destinations: {read: "show snmp trap"}  # SnmpAdminString, access=r, range=1–32
}
```
</details>

### `set_snmp_config()`

**Update** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (19/19 attrs)</summary>

```
MOPS {
  port: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSnmpGroup.hm2SnmpPortNumber}  # InetPortNumber, access=ru
  trap_destinations: {SNMP-TARGET-MIB / snmpTargetAddrEntry.snmpTargetAddrName}  # SnmpAdminString, access=r, range=1–32
  security_model: {SNMP-TARGET-MIB / snmpTargetParamsEntry.snmpTargetParamsSecurityModel}  # SnmpSecurityModel, access=ru, range=1–2147483647
  community_security_name: {SNMP-COMMUNITY-MIB / snmpCommunityEntry.snmpCommunitySecurityName}  # SnmpAdminString, access=ru, range=1–32
  address: {SNMP-TARGET-MIB / snmpTargetAddrEntry.snmpTargetAddrTAddress}  # TAddress, access=ru
  security_name: {SNMP-TARGET-MIB / snmpTargetParamsEntry.snmpTargetParamsSecurityName}  # SnmpAdminString, access=ru
  params_row_status: {SNMP-TARGET-MIB / snmpTargetParamsEntry.snmpTargetParamsRowStatus}  # RowStatus, access=crud
  community_group_name: {SNMP-VIEW-BASED-ACM-MIB / vacmSecurityToGroupEntry.vacmGroupName}  # SnmpAdminString, access=ru, range=1–32
  security_level: {SNMP-TARGET-MIB / snmpTargetParamsEntry.snmpTargetParamsSecurityLevel}  # SnmpSecurityLevel, access=ru
  params_ref: {SNMP-TARGET-MIB / snmpTargetAddrEntry.snmpTargetAddrParams}  # SnmpAdminString, access=ru, range=1–32
  v2_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSnmpGroup.hm2SnmpV2AdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  trap_service: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSnmpGroup.hm2SnmpTrapServiceAdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  communities: {SNMP-COMMUNITY-MIB / snmpCommunityEntry.snmpCommunityName}  # OCTET STRING, access=ru
  community_access: {SNMP-VIEW-BASED-ACM-MIB / vacmAccessEntry.vacmAccessWriteViewName}  # SnmpAdminString, access=ru, range=0–32
  v3_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSnmpGroup.hm2SnmpV3AdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  tag_list: {SNMP-TARGET-MIB / snmpTargetAddrEntry.snmpTargetAddrTagList}  # SnmpTagList, access=ru
  v1_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSnmpGroup.hm2SnmpV1AdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  name: {SNMP-TARGET-MIB / snmpTargetAddrEntry.snmpTargetAddrName}  # SnmpAdminString, access=r, range=1–32
  addr_row_status: {SNMP-TARGET-MIB / snmpTargetAddrEntry.snmpTargetAddrRowStatus}  # RowStatus, access=crud
}
```
</details>

<details><summary>SNMP sources (19/19 attrs)</summary>

```
SNMP {
  port: {oid: 1.3.6.1.4.1.248.11.25.1.1.4, method: get}  # InetPortNumber, access=ru
  trap_destinations: {oid: 1.3.6.1.6.3.12.1.2.1.1}  # SnmpAdminString, access=r, range=1–32
  security_model: {oid: 1.3.6.1.6.3.12.1.3.1.3}  # SnmpSecurityModel, access=ru, range=1–2147483647
  community_security_name: {oid: 1.3.6.1.6.3.18.1.1.1.3}  # SnmpAdminString, access=ru, range=1–32
  address: {oid: 1.3.6.1.6.3.12.1.2.1.3}  # TAddress, access=ru
  security_name: {oid: 1.3.6.1.6.3.12.1.3.1.4}  # SnmpAdminString, access=ru
  params_row_status: {oid: 1.3.6.1.6.3.12.1.3.1.7}  # RowStatus, access=crud
  community_group_name: {oid: 1.3.6.1.6.3.16.1.2.1.3}  # SnmpAdminString, access=ru, range=1–32
  security_level: {oid: 1.3.6.1.6.3.12.1.3.1.5}  # SnmpSecurityLevel, access=ru
  params_ref: {oid: 1.3.6.1.6.3.12.1.2.1.7}  # SnmpAdminString, access=ru, range=1–32
  v2_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.1.2, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  trap_service: {oid: 1.3.6.1.4.1.248.11.25.1.1.6, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  communities: {oid: 1.3.6.1.6.3.18.1.1.1.2}  # OCTET STRING, access=ru
  community_access: {oid: 1.3.6.1.6.3.16.1.4.1.6}  # SnmpAdminString, access=ru, range=0–32
  v3_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.1.3, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  tag_list: {oid: 1.3.6.1.6.3.12.1.2.1.6}  # SnmpTagList, access=ru
  v1_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.1.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  name: {oid: 1.3.6.1.6.3.12.1.2.1.1}  # SnmpAdminString, access=r, range=1–32
  addr_row_status: {oid: 1.3.6.1.6.3.12.1.2.1.9}  # RowStatus, access=crud
}
```
</details>

<details><summary>SSH sources (5/19 attrs)</summary>

```
SSH {
  trap_destinations: {read: "show snmp trap"}  # SnmpAdminString, access=r, range=1–32
  params_row_status: {write: "snmp notification host add {name} {address}:{port} user {security_name} {security_level}"}  # RowStatus, access=crud
  communities: {read: "show snmp community", write: "snmp community ro {community_name}"}  # OCTET STRING, access=ru
  name: {read: "show snmp trap"}  # SnmpAdminString, access=r, range=1–32
  addr_row_status: {write: "snmp notification host add {name} {address}:{port} user {security_name} {security_level}"}  # RowStatus, access=crud
}
```
</details>

### `get_snmp_trap_destinations()`

**Read** | **Protocols:** MOPS, SNMP, SSH
Primary key: `name`

```
get_snmp_trap_destinations() -> {
    address: ""  // str
    security_model: ""  // str
    security_name: ""  // str
    security_level: ""  // "no-auth" | "auth-no-priv" | "auth-priv"
}
```


<details><summary>MOPS sources (5/5 attrs)</summary>

```
MOPS {
  security_model: {SNMP-TARGET-MIB / snmpTargetParamsEntry.snmpTargetParamsSecurityModel}  # SnmpSecurityModel, access=ru, range=1–2147483647
  address: {SNMP-TARGET-MIB / snmpTargetAddrEntry.snmpTargetAddrTAddress}  # TAddress, access=ru
  security_name: {SNMP-TARGET-MIB / snmpTargetParamsEntry.snmpTargetParamsSecurityName}  # SnmpAdminString, access=ru
  name: {SNMP-TARGET-MIB / snmpTargetAddrEntry.snmpTargetAddrName}  # SnmpAdminString, access=r, range=1–32
  security_level: {SNMP-TARGET-MIB / snmpTargetParamsEntry.snmpTargetParamsSecurityLevel}  # SnmpSecurityLevel, access=ru
}
```
</details>

<details><summary>SNMP sources (5/5 attrs)</summary>

```
SNMP {
  security_model: {oid: 1.3.6.1.6.3.12.1.3.1.3}  # SnmpSecurityModel, access=ru, range=1–2147483647
  address: {oid: 1.3.6.1.6.3.12.1.2.1.3}  # TAddress, access=ru
  security_name: {oid: 1.3.6.1.6.3.12.1.3.1.4}  # SnmpAdminString, access=ru
  name: {oid: 1.3.6.1.6.3.12.1.2.1.1}  # SnmpAdminString, access=r, range=1–32
  security_level: {oid: 1.3.6.1.6.3.12.1.3.1.5}  # SnmpSecurityLevel, access=ru
}
```
</details>

<details><summary>SSH sources (1/5 attrs)</summary>

```
SSH {
  name: {read: "show snmp trap"}  # SnmpAdminString, access=r, range=1–32
}
```
</details>

### `create_snmp_trap_dest()`

**Create** | **Protocols:** MOPS, SNMP, SSH
Required: `name`, `address`

**Linked tables:** `params_row_status`, `addr_row_status`

```
create_snmp_trap_dest() -> {
    port: 162  // int
    security_model: 3  // int
    security_name: "admin"  // str
    security_level: "auth-priv"  // "no-auth" | "auth-no-priv" | "auth-priv"
    tag_list: "trap"  // str
}
```


<details><summary>MOPS sources (7/7 attrs)</summary>

```
MOPS {
  port: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSnmpGroup.hm2SnmpPortNumber}  # InetPortNumber, access=ru
  security_model: {SNMP-TARGET-MIB / snmpTargetParamsEntry.snmpTargetParamsSecurityModel}  # SnmpSecurityModel, access=ru, range=1–2147483647
  address: {SNMP-TARGET-MIB / snmpTargetAddrEntry.snmpTargetAddrTAddress}  # TAddress, access=ru
  security_name: {SNMP-TARGET-MIB / snmpTargetParamsEntry.snmpTargetParamsSecurityName}  # SnmpAdminString, access=ru
  tag_list: {SNMP-TARGET-MIB / snmpTargetAddrEntry.snmpTargetAddrTagList}  # SnmpTagList, access=ru
  name: {SNMP-TARGET-MIB / snmpTargetAddrEntry.snmpTargetAddrName}  # SnmpAdminString, access=r, range=1–32
  security_level: {SNMP-TARGET-MIB / snmpTargetParamsEntry.snmpTargetParamsSecurityLevel}  # SnmpSecurityLevel, access=ru
}
```
</details>

<details><summary>SNMP sources (7/7 attrs)</summary>

```
SNMP {
  port: {oid: 1.3.6.1.4.1.248.11.25.1.1.4, method: get}  # InetPortNumber, access=ru
  security_model: {oid: 1.3.6.1.6.3.12.1.3.1.3}  # SnmpSecurityModel, access=ru, range=1–2147483647
  address: {oid: 1.3.6.1.6.3.12.1.2.1.3}  # TAddress, access=ru
  security_name: {oid: 1.3.6.1.6.3.12.1.3.1.4}  # SnmpAdminString, access=ru
  tag_list: {oid: 1.3.6.1.6.3.12.1.2.1.6}  # SnmpTagList, access=ru
  name: {oid: 1.3.6.1.6.3.12.1.2.1.1}  # SnmpAdminString, access=r, range=1–32
  security_level: {oid: 1.3.6.1.6.3.12.1.3.1.5}  # SnmpSecurityLevel, access=ru
}
```
</details>

<details><summary>SSH sources (1/7 attrs)</summary>

```
SSH {
  name: {read: "show snmp trap"}  # SnmpAdminString, access=r, range=1–32
}
```
</details>

### `delete_snmp_trap_dest()`

**Delete** | **Protocols:** MOPS, SNMP, SSH

**Linked tables:** `addr_row_status`, `params_row_status`

<details><summary>MOPS sources (19/19 attrs)</summary>

```
MOPS {
  port: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSnmpGroup.hm2SnmpPortNumber}  # InetPortNumber, access=ru
  trap_destinations: {SNMP-TARGET-MIB / snmpTargetAddrEntry.snmpTargetAddrName}  # SnmpAdminString, access=r, range=1–32
  security_model: {SNMP-TARGET-MIB / snmpTargetParamsEntry.snmpTargetParamsSecurityModel}  # SnmpSecurityModel, access=ru, range=1–2147483647
  community_security_name: {SNMP-COMMUNITY-MIB / snmpCommunityEntry.snmpCommunitySecurityName}  # SnmpAdminString, access=ru, range=1–32
  address: {SNMP-TARGET-MIB / snmpTargetAddrEntry.snmpTargetAddrTAddress}  # TAddress, access=ru
  security_name: {SNMP-TARGET-MIB / snmpTargetParamsEntry.snmpTargetParamsSecurityName}  # SnmpAdminString, access=ru
  params_row_status: {SNMP-TARGET-MIB / snmpTargetParamsEntry.snmpTargetParamsRowStatus}  # RowStatus, access=crud
  community_group_name: {SNMP-VIEW-BASED-ACM-MIB / vacmSecurityToGroupEntry.vacmGroupName}  # SnmpAdminString, access=ru, range=1–32
  security_level: {SNMP-TARGET-MIB / snmpTargetParamsEntry.snmpTargetParamsSecurityLevel}  # SnmpSecurityLevel, access=ru
  params_ref: {SNMP-TARGET-MIB / snmpTargetAddrEntry.snmpTargetAddrParams}  # SnmpAdminString, access=ru, range=1–32
  v2_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSnmpGroup.hm2SnmpV2AdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  trap_service: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSnmpGroup.hm2SnmpTrapServiceAdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  communities: {SNMP-COMMUNITY-MIB / snmpCommunityEntry.snmpCommunityName}  # OCTET STRING, access=ru
  community_access: {SNMP-VIEW-BASED-ACM-MIB / vacmAccessEntry.vacmAccessWriteViewName}  # SnmpAdminString, access=ru, range=0–32
  v3_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSnmpGroup.hm2SnmpV3AdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  tag_list: {SNMP-TARGET-MIB / snmpTargetAddrEntry.snmpTargetAddrTagList}  # SnmpTagList, access=ru
  v1_enabled: {HM2-MGMTACCESS-MIB / hm2MgmtAccessSnmpGroup.hm2SnmpV1AdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  name: {SNMP-TARGET-MIB / snmpTargetAddrEntry.snmpTargetAddrName}  # SnmpAdminString, access=r, range=1–32
  addr_row_status: {SNMP-TARGET-MIB / snmpTargetAddrEntry.snmpTargetAddrRowStatus}  # RowStatus, access=crud
}
```
</details>

<details><summary>SNMP sources (19/19 attrs)</summary>

```
SNMP {
  port: {oid: 1.3.6.1.4.1.248.11.25.1.1.4, method: get}  # InetPortNumber, access=ru
  trap_destinations: {oid: 1.3.6.1.6.3.12.1.2.1.1}  # SnmpAdminString, access=r, range=1–32
  security_model: {oid: 1.3.6.1.6.3.12.1.3.1.3}  # SnmpSecurityModel, access=ru, range=1–2147483647
  community_security_name: {oid: 1.3.6.1.6.3.18.1.1.1.3}  # SnmpAdminString, access=ru, range=1–32
  address: {oid: 1.3.6.1.6.3.12.1.2.1.3}  # TAddress, access=ru
  security_name: {oid: 1.3.6.1.6.3.12.1.3.1.4}  # SnmpAdminString, access=ru
  params_row_status: {oid: 1.3.6.1.6.3.12.1.3.1.7}  # RowStatus, access=crud
  community_group_name: {oid: 1.3.6.1.6.3.16.1.2.1.3}  # SnmpAdminString, access=ru, range=1–32
  security_level: {oid: 1.3.6.1.6.3.12.1.3.1.5}  # SnmpSecurityLevel, access=ru
  params_ref: {oid: 1.3.6.1.6.3.12.1.2.1.7}  # SnmpAdminString, access=ru, range=1–32
  v2_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.1.2, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  trap_service: {oid: 1.3.6.1.4.1.248.11.25.1.1.6, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  communities: {oid: 1.3.6.1.6.3.18.1.1.1.2}  # OCTET STRING, access=ru
  community_access: {oid: 1.3.6.1.6.3.16.1.4.1.6}  # SnmpAdminString, access=ru, range=0–32
  v3_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.1.3, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  tag_list: {oid: 1.3.6.1.6.3.12.1.2.1.6}  # SnmpTagList, access=ru
  v1_enabled: {oid: 1.3.6.1.4.1.248.11.25.1.1.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  name: {oid: 1.3.6.1.6.3.12.1.2.1.1}  # SnmpAdminString, access=r, range=1–32
  addr_row_status: {oid: 1.3.6.1.6.3.12.1.2.1.9}  # RowStatus, access=crud
}
```
</details>

<details><summary>SSH sources (5/19 attrs)</summary>

```
SSH {
  trap_destinations: {read: "show snmp trap"}  # SnmpAdminString, access=r, range=1–32
  params_row_status: {write: "snmp notification host add {name} {address}:{port} user {security_name} {security_level}"}  # RowStatus, access=crud
  communities: {read: "show snmp community", write: "snmp community ro {community_name}"}  # OCTET STRING, access=ru
  name: {read: "show snmp trap"}  # SnmpAdminString, access=r, range=1–32
  addr_row_status: {write: "snmp notification host add {name} {address}:{port} user {security_name} {security_level}"}  # RowStatus, access=crud
}
```
</details>

---

## snmp_information

_NAPALM standard — system name, contact, location_

### `get_snmp_information()`

**Read** | **Protocols:** MOPS, SNMP

```
get_snmp_information() -> {
    chassis_id: ""  // str
    contact: ""  // str
    location: ""  // str
}
```


<details><summary>MOPS sources (3/3 attrs)</summary>

```
MOPS {
  contact: {SNMPv2-MIB / system.sysContact}  # DisplayString, access=ru, range=0–255
  chassis_id: {SNMPv2-MIB / system.sysName}  # DisplayString, access=ru, range=0–255
  location: {SNMPv2-MIB / system.sysLocation}  # DisplayString, access=ru, range=0–255
}
```
</details>

<details><summary>SNMP sources (3/3 attrs)</summary>

```
SNMP {
  contact: {oid: 1.3.6.1.2.1.1.4, method: get}  # DisplayString, access=ru, range=0–255
  chassis_id: {oid: 1.3.6.1.2.1.1.5, method: get}  # DisplayString, access=ru, range=0–255
  location: {oid: 1.3.6.1.2.1.1.6, method: get}  # DisplayString, access=ru, range=0–255
}
```
</details>

### `set_snmp_information()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (3/3 attrs)</summary>

```
MOPS {
  contact: {SNMPv2-MIB / system.sysContact}  # DisplayString, access=ru, range=0–255
  chassis_id: {SNMPv2-MIB / system.sysName}  # DisplayString, access=ru, range=0–255
  location: {SNMPv2-MIB / system.sysLocation}  # DisplayString, access=ru, range=0–255
}
```
</details>

<details><summary>SNMP sources (3/3 attrs)</summary>

```
SNMP {
  contact: {oid: 1.3.6.1.2.1.1.4, method: get}  # DisplayString, access=ru, range=0–255
  chassis_id: {oid: 1.3.6.1.2.1.1.5, method: get}  # DisplayString, access=ru, range=0–255
  location: {oid: 1.3.6.1.2.1.1.6, method: get}  # DisplayString, access=ru, range=0–255
}
```
</details>

---

## software

_Software images, boot configuration, and integrity settings_

### `get_software()`

**Read** | **Protocols:** MOPS, SNMP

```
get_software() -> {
    allow_unsigned: False  // bool
    secure_boot: False  // bool
    dev_mode: False  // bool
    bootcode: ""  // str
    images: {...}  // dict
}
```

> Sub-table: **`images`** — key: `image_name`

<details><summary>MOPS sources (10/11 attrs)</summary>

```
MOPS {
  dev_mode: {HM2-DEVMGMT-MIB / hm2DeviceMgmtSoftwareSecureBootGroup.hm2DevMgmtSwSecureBootDevmodeStatus}  # HmEnabledStatus, access=r, allowed=[True, False]
  image_major: {HM2-DEVMGMT-MIB / hm2DevMgmtSwVersEntry.hm2DevMgmtSwMajorRelNum}  # Integer32, access=r
  allow_unsigned: {HM2-DEVMGMT-MIB / hm2DeviceMgmtSoftwareVersionGroup.hm2DevMgmtSwVersAllowUnsigned}  # HmEnabledStatus, access=ru, allowed=[True, False]
  bootcode: {HM2-DEVMGMT-MIB / hm2DeviceMgmtSoftwareVersionGroup.hm2DevMgmtSwVersBootcode}  # DisplayString, access=r
  image_minor: {HM2-DEVMGMT-MIB / hm2DevMgmtSwVersEntry.hm2DevMgmtSwMinorRelNum}  # Integer32, access=r
  image_name: {HM2-DEVMGMT-MIB / hm2DevMgmtSwVersEntry.hm2DevMgmtSwFileName}  # DisplayString, access=r
  image_location: {HM2-DEVMGMT-MIB / hm2DevMgmtSwVersEntry.hm2DevMgmtSwFileLocation}  # INTEGER, access=r, allowed=['ram', 'flash', 'sd-card', 'usb']
  secure_boot: {HM2-DEVMGMT-MIB / hm2DeviceMgmtSoftwareSecureBootGroup.hm2DevMgmtSwSecureBootAdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  image_bugfix: {HM2-DEVMGMT-MIB / hm2DevMgmtSwVersEntry.hm2DevMgmtSwBugfixRelNum}  # Integer32, access=r
  image_type: {HM2-DEVMGMT-MIB / hm2DevMgmtSwVersEntry.hm2DevMgmtSwFileType}  # INTEGER, access=r, allowed=['firmware', 'applet', 'logic']
}
```
</details>

<details><summary>SNMP sources (10/11 attrs)</summary>

```
SNMP {
  dev_mode: {oid: 1.3.6.1.4.1.248.11.10.1.3.2.2, method: get}  # HmEnabledStatus, access=r, allowed=[True, False]
  image_major: {oid: 1.3.6.1.4.1.248.11.10.1.3.1.10.1.6}  # Integer32, access=r
  allow_unsigned: {oid: 1.3.6.1.4.1.248.11.10.1.3.1.2, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  bootcode: {oid: 1.3.6.1.4.1.248.11.10.1.3.1.1, method: get}  # DisplayString, access=r
  image_minor: {oid: 1.3.6.1.4.1.248.11.10.1.3.1.10.1.7}  # Integer32, access=r
  image_name: {oid: 1.3.6.1.4.1.248.11.10.1.3.1.10.1.4}  # DisplayString, access=r
  image_location: {oid: 1.3.6.1.4.1.248.11.10.1.3.1.10.1.1}  # INTEGER, access=r, allowed=['ram', 'flash', 'sd-card', 'usb']
  secure_boot: {oid: 1.3.6.1.4.1.248.11.10.1.3.2.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  image_bugfix: {oid: 1.3.6.1.4.1.248.11.10.1.3.1.10.1.8}  # Integer32, access=r
  image_type: {oid: 1.3.6.1.4.1.248.11.10.1.3.1.10.1.2}  # INTEGER, access=r, allowed=['firmware', 'applet', 'logic']
}
```
</details>

### `set_software()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (10/11 attrs)</summary>

```
MOPS {
  dev_mode: {HM2-DEVMGMT-MIB / hm2DeviceMgmtSoftwareSecureBootGroup.hm2DevMgmtSwSecureBootDevmodeStatus}  # HmEnabledStatus, access=r, allowed=[True, False]
  image_major: {HM2-DEVMGMT-MIB / hm2DevMgmtSwVersEntry.hm2DevMgmtSwMajorRelNum}  # Integer32, access=r
  allow_unsigned: {HM2-DEVMGMT-MIB / hm2DeviceMgmtSoftwareVersionGroup.hm2DevMgmtSwVersAllowUnsigned}  # HmEnabledStatus, access=ru, allowed=[True, False]
  bootcode: {HM2-DEVMGMT-MIB / hm2DeviceMgmtSoftwareVersionGroup.hm2DevMgmtSwVersBootcode}  # DisplayString, access=r
  image_minor: {HM2-DEVMGMT-MIB / hm2DevMgmtSwVersEntry.hm2DevMgmtSwMinorRelNum}  # Integer32, access=r
  image_name: {HM2-DEVMGMT-MIB / hm2DevMgmtSwVersEntry.hm2DevMgmtSwFileName}  # DisplayString, access=r
  image_location: {HM2-DEVMGMT-MIB / hm2DevMgmtSwVersEntry.hm2DevMgmtSwFileLocation}  # INTEGER, access=r, allowed=['ram', 'flash', 'sd-card', 'usb']
  secure_boot: {HM2-DEVMGMT-MIB / hm2DeviceMgmtSoftwareSecureBootGroup.hm2DevMgmtSwSecureBootAdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  image_bugfix: {HM2-DEVMGMT-MIB / hm2DevMgmtSwVersEntry.hm2DevMgmtSwBugfixRelNum}  # Integer32, access=r
  image_type: {HM2-DEVMGMT-MIB / hm2DevMgmtSwVersEntry.hm2DevMgmtSwFileType}  # INTEGER, access=r, allowed=['firmware', 'applet', 'logic']
}
```
</details>

<details><summary>SNMP sources (10/11 attrs)</summary>

```
SNMP {
  dev_mode: {oid: 1.3.6.1.4.1.248.11.10.1.3.2.2, method: get}  # HmEnabledStatus, access=r, allowed=[True, False]
  image_major: {oid: 1.3.6.1.4.1.248.11.10.1.3.1.10.1.6}  # Integer32, access=r
  allow_unsigned: {oid: 1.3.6.1.4.1.248.11.10.1.3.1.2, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  bootcode: {oid: 1.3.6.1.4.1.248.11.10.1.3.1.1, method: get}  # DisplayString, access=r
  image_minor: {oid: 1.3.6.1.4.1.248.11.10.1.3.1.10.1.7}  # Integer32, access=r
  image_name: {oid: 1.3.6.1.4.1.248.11.10.1.3.1.10.1.4}  # DisplayString, access=r
  image_location: {oid: 1.3.6.1.4.1.248.11.10.1.3.1.10.1.1}  # INTEGER, access=r, allowed=['ram', 'flash', 'sd-card', 'usb']
  secure_boot: {oid: 1.3.6.1.4.1.248.11.10.1.3.2.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  image_bugfix: {oid: 1.3.6.1.4.1.248.11.10.1.3.1.10.1.8}  # Integer32, access=r
  image_type: {oid: 1.3.6.1.4.1.248.11.10.1.3.1.10.1.2}  # INTEGER, access=r, allowed=['firmware', 'applet', 'logic']
}
```
</details>

---

## syslog

_Syslog client configuration and server table_

### `get_syslog()`

**Read** | **Protocols:** MOPS, SNMP, SSH

```
get_syslog() -> {
    enabled: False  // bool
    servers: {...}  // dict
}
```

> Sub-table: **`servers`** — key: `ip`

<details><summary>MOPS sources (6/6 attrs)</summary>

```
MOPS {
  port: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerUdpPort}  # InetPortNumber, access=ru
  enabled: {HM2-LOGGING-MIB / hm2LogSyslogGroup.hm2LogSyslogAdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  servers: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerIPAddr}  # InetAddress, access=ru
  transport: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerTransportType}  # INTEGER, access=ru
  severity: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerLevelUpto}  # INTEGER, access=ru, allowed=['alert', 'critical', 'error', 'warning', 'notice', 'info', 'debug']
  ip: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerIPAddr}  # InetAddress, access=ru
}
```
</details>

<details><summary>SNMP sources (6/6 attrs)</summary>

```
SNMP {
  port: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.4}  # InetPortNumber, access=ru
  enabled: {oid: 1.3.6.1.4.1.248.11.23.1.5.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  servers: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.3}  # InetAddress, access=ru
  transport: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.8}  # INTEGER, access=ru
  severity: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.5}  # INTEGER, access=ru, allowed=['alert', 'critical', 'error', 'warning', 'notice', 'info', 'debug']
  ip: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.3}  # InetAddress, access=ru
}
```
</details>

<details><summary>SSH sources (3/6 attrs)</summary>

```
SSH {
  enabled: {read: "show logging syslog", write: "{'' if value else 'no '}logging syslog operation"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  servers: {read: "show logging host", write: "logging host add {index} addr {ip} port {port} severity {severity}"}  # InetAddress, access=ru
  ip: {read: "show logging host", write: "logging host add {index} addr {ip} port {port} severity {severity}"}  # InetAddress, access=ru
}
```
</details>

### `set_syslog()`

**Update** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (10/10 attrs)</summary>

```
MOPS {
  enabled: {HM2-LOGGING-MIB / hm2LogSyslogGroup.hm2LogSyslogAdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerUdpPort}  # InetPortNumber, access=ru
  server_index: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerIndex}  # Integer32, access=r, range=1–8
  servers: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerIPAddr}  # InetAddress, access=ru
  transport: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerTransportType}  # INTEGER, access=ru
  addr_type: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerIPAddrType}  # InetAddressType, access=ru
  log_type: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerLogType}  # INTEGER, access=ru
  severity: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerLevelUpto}  # INTEGER, access=ru, allowed=['alert', 'critical', 'error', 'warning', 'notice', 'info', 'debug']
  server_row_status: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerRowStatus}  # RowStatus, access=crud
  ip: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerIPAddr}  # InetAddress, access=ru
}
```
</details>

<details><summary>SNMP sources (10/10 attrs)</summary>

```
SNMP {
  enabled: {oid: 1.3.6.1.4.1.248.11.23.1.5.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.4}  # InetPortNumber, access=ru
  server_index: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.1}  # Integer32, access=r, range=1–8
  servers: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.3}  # InetAddress, access=ru
  transport: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.8}  # INTEGER, access=ru
  addr_type: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.2}  # InetAddressType, access=ru
  log_type: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.6}  # INTEGER, access=ru
  severity: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.5}  # INTEGER, access=ru, allowed=['alert', 'critical', 'error', 'warning', 'notice', 'info', 'debug']
  server_row_status: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.7}  # RowStatus, access=crud
  ip: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.3}  # InetAddress, access=ru
}
```
</details>

<details><summary>SSH sources (4/10 attrs)</summary>

```
SSH {
  enabled: {read: "show logging syslog", write: "{'' if value else 'no '}logging syslog operation"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  servers: {read: "show logging host", write: "logging host add {index} addr {ip} port {port} severity {severity}"}  # InetAddress, access=ru
  server_row_status: {write: "logging host add {index} addr {ip} port {port} severity {severity}"}  # RowStatus, access=crud
  ip: {read: "show logging host", write: "logging host add {index} addr {ip} port {port} severity {severity}"}  # InetAddress, access=ru
}
```
</details>

### `create_syslog_server()`

**Create** | **Protocols:** MOPS, SNMP, SSH
Required: `ip`

```
create_syslog_server() -> {
    addr_type: 1  // int
    port: 514  // int
    severity: 6  // "emergency" | "alert" | "critical" | "error" | "warning" | "notice" | "informational" | "debug"
    transport: 1  // "udp" | "tls"
    log_type: 1  // int
}
```


<details><summary>MOPS sources (6/6 attrs)</summary>

```
MOPS {
  port: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerUdpPort}  # InetPortNumber, access=ru
  transport: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerTransportType}  # INTEGER, access=ru
  addr_type: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerIPAddrType}  # InetAddressType, access=ru
  log_type: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerLogType}  # INTEGER, access=ru
  severity: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerLevelUpto}  # INTEGER, access=ru, allowed=['alert', 'critical', 'error', 'warning', 'notice', 'info', 'debug']
  ip: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerIPAddr}  # InetAddress, access=ru
}
```
</details>

<details><summary>SNMP sources (6/6 attrs)</summary>

```
SNMP {
  port: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.4}  # InetPortNumber, access=ru
  transport: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.8}  # INTEGER, access=ru
  addr_type: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.2}  # InetAddressType, access=ru
  log_type: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.6}  # INTEGER, access=ru
  severity: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.5}  # INTEGER, access=ru, allowed=['alert', 'critical', 'error', 'warning', 'notice', 'info', 'debug']
  ip: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.3}  # InetAddress, access=ru
}
```
</details>

<details><summary>SSH sources (1/6 attrs)</summary>

```
SSH {
  ip: {read: "show logging host", write: "logging host add {index} addr {ip} port {port} severity {severity}"}  # InetAddress, access=ru
}
```
</details>

### `delete_syslog_server()`

**Delete** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (10/10 attrs)</summary>

```
MOPS {
  enabled: {HM2-LOGGING-MIB / hm2LogSyslogGroup.hm2LogSyslogAdminStatus}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerUdpPort}  # InetPortNumber, access=ru
  server_index: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerIndex}  # Integer32, access=r, range=1–8
  servers: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerIPAddr}  # InetAddress, access=ru
  transport: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerTransportType}  # INTEGER, access=ru
  addr_type: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerIPAddrType}  # InetAddressType, access=ru
  log_type: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerLogType}  # INTEGER, access=ru
  severity: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerLevelUpto}  # INTEGER, access=ru, allowed=['alert', 'critical', 'error', 'warning', 'notice', 'info', 'debug']
  server_row_status: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerRowStatus}  # RowStatus, access=crud
  ip: {HM2-LOGGING-MIB / hm2LogSyslogServerEntry.hm2LogSyslogServerIPAddr}  # InetAddress, access=ru
}
```
</details>

<details><summary>SNMP sources (10/10 attrs)</summary>

```
SNMP {
  enabled: {oid: 1.3.6.1.4.1.248.11.23.1.5.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  port: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.4}  # InetPortNumber, access=ru
  server_index: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.1}  # Integer32, access=r, range=1–8
  servers: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.3}  # InetAddress, access=ru
  transport: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.8}  # INTEGER, access=ru
  addr_type: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.2}  # InetAddressType, access=ru
  log_type: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.6}  # INTEGER, access=ru
  severity: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.5}  # INTEGER, access=ru, allowed=['alert', 'critical', 'error', 'warning', 'notice', 'info', 'debug']
  server_row_status: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.7}  # RowStatus, access=crud
  ip: {oid: 1.3.6.1.4.1.248.11.23.1.5.10.1.3}  # InetAddress, access=ru
}
```
</details>

<details><summary>SSH sources (4/10 attrs)</summary>

```
SSH {
  enabled: {read: "show logging syslog", write: "{'' if value else 'no '}logging syslog operation"}  # HmEnabledStatus, access=ru, allowed=[True, False]
  servers: {read: "show logging host", write: "logging host add {index} addr {ip} port {port} severity {severity}"}  # InetAddress, access=ru
  server_row_status: {write: "logging host add {index} addr {ip} port {port} severity {severity}"}  # RowStatus, access=crud
  ip: {read: "show logging host", write: "logging host add {index} addr {ip} port {port} severity {severity}"}  # InetAddress, access=ru
}
```
</details>

---

## system

_System identity and hardware monitoring_

### `get_system_info()`

**Read** | **Protocols:** MOPS, SNMP

```
get_system_info() -> {
    hostname: ""  // str
    contact: ""  // str
    location: ""  // str
    uptime: 0  // int
}
```


<details><summary>MOPS sources (4/4 attrs)</summary>

```
MOPS {
  contact: {SNMPv2-MIB / system.sysContact}  # DisplayString, access=ru, range=0–255
  uptime: {SNMPv2-MIB / system.sysUpTime}  # TimeTicks, access=r
  hostname: {SNMPv2-MIB / system.sysName}  # DisplayString, access=ru, range=0–255
  location: {SNMPv2-MIB / system.sysLocation}  # DisplayString, access=ru, range=0–255
}
```
</details>

<details><summary>SNMP sources (4/4 attrs)</summary>

```
SNMP {
  contact: {oid: 1.3.6.1.2.1.1.4, method: get}  # DisplayString, access=ru, range=0–255
  uptime: {oid: 1.3.6.1.2.1.1.3, method: get}  # TimeTicks, access=r
  hostname: {oid: 1.3.6.1.2.1.1.5, method: get}  # DisplayString, access=ru, range=0–255
  location: {oid: 1.3.6.1.2.1.1.6, method: get}  # DisplayString, access=ru, range=0–255
}
```
</details>

### `get_facts()`

**Read** | **Protocols:** MOPS, SNMP

```
get_facts() -> {
    hostname: ""  // str
    fqdn: ""  // str (computed)
    vendor: ""  // str (computed)
    model: ""  // str
    serial_number: ""  // str
    os_version: ""  // str
    uptime: 0  // int
    interface_list: [...]  // list
}
```


<details><summary>MOPS sources (6/8 attrs)</summary>

```
MOPS {
  serial_number: {HM2-DEVMGMT-MIB / hm2DeviceMgmtGroup.hm2DevMgmtSerialNumber}  # DisplayString, access=r
  interface_list: {IF-MIB / ifXEntry.ifName}  # DisplayString, access=r
  model: {HM2-DEVMGMT-MIB / hm2DeviceMgmtGroup.hm2DevMgmtProductDescr}  # DisplayString, access=r
  os_version: {HM2-DEVMGMT-MIB / hm2DevMgmtSwVersEntry.hm2DevMgmtSwVersion}  # DisplayString, access=r
  uptime: {SNMPv2-MIB / system.sysUpTime}  # TimeTicks, access=r
  hostname: {SNMPv2-MIB / system.sysName}  # DisplayString, access=ru, range=0–255
}
```
</details>

<details><summary>SNMP sources (6/8 attrs)</summary>

```
SNMP {
  serial_number: {oid: 1.3.6.1.4.1.248.11.10.1.1.3, method: get}  # DisplayString, access=r
  interface_list: {oid: 1.3.6.1.2.1.31.1.1.1.1}  # DisplayString, access=r
  model: {oid: 1.3.6.1.4.1.248.11.10.1.1.2, method: get}  # DisplayString, access=r
  os_version: {oid: 1.3.6.1.4.1.248.11.10.1.3.1.10.1.5}  # DisplayString, access=r
  uptime: {oid: 1.3.6.1.2.1.1.3, method: get}  # TimeTicks, access=r
  hostname: {oid: 1.3.6.1.2.1.1.5, method: get}  # DisplayString, access=ru, range=0–255
}
```
</details>

### `get_environment()`

**Read** | **Protocols:** MOPS, SNMP

```
get_environment() -> {
    temperature: {...}  // dict
    fans: {...}  // dict
    power: {...}  // dict
    cpu: {...}  // dict
    memory: {...}  // dict
}
```

> Sub-table: **`temperature`** — key: `temperature`

<details><summary>MOPS sources (1/1 attrs)</summary>

```
MOPS {
  temperature: {HM2-DEVMGMT-MIB / hm2DeviceMgmtTemperatureGroup.hm2DevMgmtTemperature}  # Integer32, access=r
}
```
</details>

<details><summary>SNMP sources (1/1 attrs)</summary>

```
SNMP {
  temperature: {oid: 1.3.6.1.4.1.248.11.10.1.5.1, method: get}  # Integer32, access=r
}
```
</details>

### `get_system_health()`

**Read** | **Protocols:** MOPS, SNMP

```
get_system_health() -> {
    temperature: 0  // int
    humidity: 0  // int
    hardware_version: ""  // str
    product_description: ""  // str
}
```


<details><summary>MOPS sources (4/4 attrs)</summary>

```
MOPS {
  hardware_version: {HM2-DEVMGMT-MIB / hm2DeviceMgmtHardwareGroup.hm2DevMgmtHwVersion}  # DisplayString, access=r
  humidity: {HM2-DEVMGMT-MIB / hm2DeviceMgmtHumidityGroup.hm2DevMgmtHumidity}  # Unsigned32, access=r, range=0–100
  product_description: {HM2-DEVMGMT-MIB / hm2DeviceMgmtGroup.hm2DevMgmtProductDescr}  # DisplayString, access=r
  temperature: {HM2-DEVMGMT-MIB / hm2DeviceMgmtTemperatureGroup.hm2DevMgmtTemperature}  # Integer32, access=r
}
```
</details>

<details><summary>SNMP sources (4/4 attrs)</summary>

```
SNMP {
  hardware_version: {oid: 1.3.6.1.4.1.248.11.10.1.4.1, method: get}  # DisplayString, access=r
  humidity: {oid: 1.3.6.1.4.1.248.11.10.1.12.1, method: get}  # Unsigned32, access=r, range=0–100
  product_description: {oid: 1.3.6.1.4.1.248.11.10.1.1.2, method: get}  # DisplayString, access=r
  temperature: {oid: 1.3.6.1.4.1.248.11.10.1.5.1, method: get}  # Integer32, access=r
}
```
</details>

### `set_system_info()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (12/14 attrs)</summary>

```
MOPS {
  serial_number: {HM2-DEVMGMT-MIB / hm2DeviceMgmtGroup.hm2DevMgmtSerialNumber}  # DisplayString, access=r
  product_description: {HM2-DEVMGMT-MIB / hm2DeviceMgmtGroup.hm2DevMgmtProductDescr}  # DisplayString, access=r
  interface_list: {IF-MIB / ifXEntry.ifName}  # DisplayString, access=r
  contact: {SNMPv2-MIB / system.sysContact}  # DisplayString, access=ru, range=0–255
  uptime: {SNMPv2-MIB / system.sysUpTime}  # TimeTicks, access=r
  model: {HM2-DEVMGMT-MIB / hm2DeviceMgmtGroup.hm2DevMgmtProductDescr}  # DisplayString, access=r
  os_version: {HM2-DEVMGMT-MIB / hm2DevMgmtSwVersEntry.hm2DevMgmtSwVersion}  # DisplayString, access=r
  temperature: {HM2-DEVMGMT-MIB / hm2DeviceMgmtTemperatureGroup.hm2DevMgmtTemperature}  # Integer32, access=r
  humidity: {HM2-DEVMGMT-MIB / hm2DeviceMgmtHumidityGroup.hm2DevMgmtHumidity}  # Unsigned32, access=r, range=0–100
  location: {SNMPv2-MIB / system.sysLocation}  # DisplayString, access=ru, range=0–255
  hardware_version: {HM2-DEVMGMT-MIB / hm2DeviceMgmtHardwareGroup.hm2DevMgmtHwVersion}  # DisplayString, access=r
  hostname: {SNMPv2-MIB / system.sysName}  # DisplayString, access=ru, range=0–255
}
```
</details>

<details><summary>SNMP sources (12/14 attrs)</summary>

```
SNMP {
  serial_number: {oid: 1.3.6.1.4.1.248.11.10.1.1.3, method: get}  # DisplayString, access=r
  product_description: {oid: 1.3.6.1.4.1.248.11.10.1.1.2, method: get}  # DisplayString, access=r
  interface_list: {oid: 1.3.6.1.2.1.31.1.1.1.1}  # DisplayString, access=r
  contact: {oid: 1.3.6.1.2.1.1.4, method: get}  # DisplayString, access=ru, range=0–255
  uptime: {oid: 1.3.6.1.2.1.1.3, method: get}  # TimeTicks, access=r
  model: {oid: 1.3.6.1.4.1.248.11.10.1.1.2, method: get}  # DisplayString, access=r
  os_version: {oid: 1.3.6.1.4.1.248.11.10.1.3.1.10.1.5}  # DisplayString, access=r
  temperature: {oid: 1.3.6.1.4.1.248.11.10.1.5.1, method: get}  # Integer32, access=r
  humidity: {oid: 1.3.6.1.4.1.248.11.10.1.12.1, method: get}  # Unsigned32, access=r, range=0–100
  location: {oid: 1.3.6.1.2.1.1.6, method: get}  # DisplayString, access=ru, range=0–255
  hardware_version: {oid: 1.3.6.1.4.1.248.11.10.1.4.1, method: get}  # DisplayString, access=r
  hostname: {oid: 1.3.6.1.2.1.1.5, method: get}  # DisplayString, access=ru, range=0–255
}
```
</details>

---

## system_health

_Device monitoring and security status_

### `get_device_monitor()`

**Read** | **Protocols:** None

```
get_device_monitor() -> {
    oper_state: ""  // str
    status_index: 0  // int
    trap_cause: ""  // str
}
```


### `set_device_monitor()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (7/7 attrs)</summary>

```
MOPS {
  sec_state: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecOperState}  # INTEGER, access=r, allowed=['noerror', 'error']
  sec_status: {HM2-DIAGNOSTIC-MIB / hm2DevSecStatusEntry.hm2DevSecStatusIndex}  # Integer32, access=r
  monitor_status: {HM2-DIAGNOSTIC-MIB / hm2DevMonStatusEntry.hm2DevMonStatusIndex}  # Integer32, access=r
  fan_status: {HM2-FAN-MIB / hm2FanMgmtEntry.hm2FanMgmtStatus}  # Hm2FanModuleStatus, access=r
  sec_trap: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecTrapCause}  # INTEGER, access=r, allowed=['none', 'password-change', 'password-min-length', 'password-policy-not-configured', 'password-policy-inactive', 'telnet-enabled', 'http-enabled', 'snmp-unsecure', 'sysmon-enabled', 'ext-nvm-update-enabled', 'no-link', 'hidisc-enabled', 'ext-nvm-config-load-unsecure', 'iec61850-mms-enabled', 'https-certificate-warning', 'modbus-tcp-enabled', 'ethernet-ip-enabled', 'profinet-io-enabled', 'pml-disabled', 'secure-boot-disabled', 'dev-mode-enabled']
  monitor_trap: {HM2-DIAGNOSTIC-MIB / hm2DevMonCommonEntry.hm2DevMonTrapCause}  # INTEGER, access=r, allowed=['none', 'power-supply', 'link-failure', 'temperature', 'fan-failure', 'module-removal', 'ext-nvm-removal', 'ext-nvm-not-in-sync', 'ring-redundancy', 'humidity', 'stp-port-blocked']
  monitor_state: {HM2-DIAGNOSTIC-MIB / hm2DevMonCommonEntry.hm2DevMonOperState}  # INTEGER, access=r, allowed=['noerror', 'error']
}
```
</details>

<details><summary>SNMP sources (7/7 attrs)</summary>

```
SNMP {
  sec_state: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.4, method: get}  # INTEGER, access=r, allowed=['noerror', 'error']
  sec_status: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.10.1.1}  # Integer32, access=r
  monitor_status: {oid: 1.3.6.1.4.1.248.11.22.1.3.2.10.1.1}  # Integer32, access=r
  fan_status: {oid: 1.3.6.1.4.1.248.11.13.1.1.3.1.2}  # Hm2FanModuleStatus, access=r
  sec_trap: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.2, method: get}  # INTEGER, access=r, allowed=['none', 'password-change', 'password-min-length', 'password-policy-not-configured', 'password-policy-inactive', 'telnet-enabled', 'http-enabled', 'snmp-unsecure', 'sysmon-enabled', 'ext-nvm-update-enabled', 'no-link', 'hidisc-enabled', 'ext-nvm-config-load-unsecure', 'iec61850-mms-enabled', 'https-certificate-warning', 'modbus-tcp-enabled', 'ethernet-ip-enabled', 'profinet-io-enabled', 'pml-disabled', 'secure-boot-disabled', 'dev-mode-enabled']
  monitor_trap: {oid: 1.3.6.1.4.1.248.11.22.1.3.2.1.1.3}  # INTEGER, access=r, allowed=['none', 'power-supply', 'link-failure', 'temperature', 'fan-failure', 'module-removal', 'ext-nvm-removal', 'ext-nvm-not-in-sync', 'ring-redundancy', 'humidity', 'stp-port-blocked']
  monitor_state: {oid: 1.3.6.1.4.1.248.11.22.1.3.2.1.1.5}  # INTEGER, access=r, allowed=['noerror', 'error']
}
```
</details>

### `get_devsec_status()`

**Read** | **Protocols:** None

```
get_devsec_status() -> {
    oper_state: ""  // str
    status_index: 0  // int
    trap_cause: ""  // str
}
```


### `set_devsec_status()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (7/7 attrs)</summary>

```
MOPS {
  sec_state: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecOperState}  # INTEGER, access=r, allowed=['noerror', 'error']
  sec_status: {HM2-DIAGNOSTIC-MIB / hm2DevSecStatusEntry.hm2DevSecStatusIndex}  # Integer32, access=r
  monitor_status: {HM2-DIAGNOSTIC-MIB / hm2DevMonStatusEntry.hm2DevMonStatusIndex}  # Integer32, access=r
  fan_status: {HM2-FAN-MIB / hm2FanMgmtEntry.hm2FanMgmtStatus}  # Hm2FanModuleStatus, access=r
  sec_trap: {HM2-DIAGNOSTIC-MIB / hm2DevSecConfigGroup.hm2DevSecTrapCause}  # INTEGER, access=r, allowed=['none', 'password-change', 'password-min-length', 'password-policy-not-configured', 'password-policy-inactive', 'telnet-enabled', 'http-enabled', 'snmp-unsecure', 'sysmon-enabled', 'ext-nvm-update-enabled', 'no-link', 'hidisc-enabled', 'ext-nvm-config-load-unsecure', 'iec61850-mms-enabled', 'https-certificate-warning', 'modbus-tcp-enabled', 'ethernet-ip-enabled', 'profinet-io-enabled', 'pml-disabled', 'secure-boot-disabled', 'dev-mode-enabled']
  monitor_trap: {HM2-DIAGNOSTIC-MIB / hm2DevMonCommonEntry.hm2DevMonTrapCause}  # INTEGER, access=r, allowed=['none', 'power-supply', 'link-failure', 'temperature', 'fan-failure', 'module-removal', 'ext-nvm-removal', 'ext-nvm-not-in-sync', 'ring-redundancy', 'humidity', 'stp-port-blocked']
  monitor_state: {HM2-DIAGNOSTIC-MIB / hm2DevMonCommonEntry.hm2DevMonOperState}  # INTEGER, access=r, allowed=['noerror', 'error']
}
```
</details>

<details><summary>SNMP sources (7/7 attrs)</summary>

```
SNMP {
  sec_state: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.4, method: get}  # INTEGER, access=r, allowed=['noerror', 'error']
  sec_status: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.10.1.1}  # Integer32, access=r
  monitor_status: {oid: 1.3.6.1.4.1.248.11.22.1.3.2.10.1.1}  # Integer32, access=r
  fan_status: {oid: 1.3.6.1.4.1.248.11.13.1.1.3.1.2}  # Hm2FanModuleStatus, access=r
  sec_trap: {oid: 1.3.6.1.4.1.248.11.22.1.3.3.1.2, method: get}  # INTEGER, access=r, allowed=['none', 'password-change', 'password-min-length', 'password-policy-not-configured', 'password-policy-inactive', 'telnet-enabled', 'http-enabled', 'snmp-unsecure', 'sysmon-enabled', 'ext-nvm-update-enabled', 'no-link', 'hidisc-enabled', 'ext-nvm-config-load-unsecure', 'iec61850-mms-enabled', 'https-certificate-warning', 'modbus-tcp-enabled', 'ethernet-ip-enabled', 'profinet-io-enabled', 'pml-disabled', 'secure-boot-disabled', 'dev-mode-enabled']
  monitor_trap: {oid: 1.3.6.1.4.1.248.11.22.1.3.2.1.1.3}  # INTEGER, access=r, allowed=['none', 'power-supply', 'link-failure', 'temperature', 'fan-failure', 'module-removal', 'ext-nvm-removal', 'ext-nvm-not-in-sync', 'ring-redundancy', 'humidity', 'stp-port-blocked']
  monitor_state: {oid: 1.3.6.1.4.1.248.11.22.1.3.2.1.1.5}  # INTEGER, access=r, allowed=['noerror', 'error']
}
```
</details>

### `get_fan_status()`

**list** | **Protocols:** None

```
get_fan_status() -> {
    status: "running"  // str
}
```


---

## user

_User account management and password policy_

### `get_users()`

**Read** | **Protocols:** MOPS, SNMP, SSH
Primary key: `username`

```
get_users() -> {
    level: "guest"  // "unauthorized" | "guest" | "auditor" | "custom1" | "custom2" | "custom3" | "operator" | "administrator"
    locked: False  // bool
    policy_check: False  // bool
    snmp_auth: ""  // "" | "md5" | "sha"
    snmp_enc: ""  // "none" | "des" | "aes128" | "aes256"
    default_password: False  // bool
}
```


<details><summary>MOPS sources (7/7 attrs)</summary>

```
MOPS {
  default_password: {HM2-USERMGMT-MIB / hm2PwdMgmtDefaultPwdStatusEntry.hm2PwdMgmtDefaultPwdStatusUserName}  # SnmpAdminString, access=r
  locked: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserLockoutStatus}  # TruthValue, access=ru, allowed=[True, False]
  policy_check: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserPwdPolicyChk}  # HmEnabledStatus, access=ru, allowed=[True, False]
  username: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserName}  # SnmpAdminString, access=r, range=1–32
  snmp_enc: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserSnmpEncType}  # INTEGER, access=ru, allowed=['none', 'des', 'aesCfb128', 'aesCfb256']
  level: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserAccessRole}  # Hm2UserAccessRoles, access=ru
  snmp_auth: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserSnmpAuthType}  # INTEGER, access=ru, allowed=['hmacmd5', 'hmacsha']
}
```
</details>

<details><summary>SNMP sources (7/7 attrs)</summary>

```
SNMP {
  default_password: {oid: 1.3.6.1.4.1.248.11.24.1.2.100.100.1.2}  # SnmpAdminString, access=r
  locked: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.4}  # TruthValue, access=ru, allowed=[True, False]
  policy_check: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.6}  # HmEnabledStatus, access=ru, allowed=[True, False]
  username: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.1}  # SnmpAdminString, access=r, range=1–32
  snmp_enc: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.8}  # INTEGER, access=ru, allowed=['none', 'des', 'aesCfb128', 'aesCfb256']
  level: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.3}  # Hm2UserAccessRoles, access=ru
  snmp_auth: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.7}  # INTEGER, access=ru, allowed=['hmacmd5', 'hmacsha']
}
```
</details>

<details><summary>SSH sources (1/7 attrs)</summary>

```
SSH {
  username: {read: "show users"}  # SnmpAdminString, access=r, range=1–32
}
```
</details>

### `set_user()`

**Update** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (14/18 attrs)</summary>

```
MOPS {
  default_password: {HM2-USERMGMT-MIB / hm2PwdMgmtDefaultPwdStatusEntry.hm2PwdMgmtDefaultPwdStatusUserName}  # SnmpAdminString, access=r
  snmp_auth_password: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserSnmpAuthPassword}  # DisplayString, access=ru, range=0–64
  username: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserName}  # SnmpAdminString, access=r, range=1–32
  locked: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserLockoutStatus}  # TruthValue, access=ru, allowed=[True, False]
  policy_check: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserPwdPolicyChk}  # HmEnabledStatus, access=ru, allowed=[True, False]
  max_attempts: {HM2-USERMGMT-MIB / hm2PwdMgmtGroup.hm2PwdMgmtLoginAttempts}  # Integer32, access=ru, range=0–5
  lockout_time: {HM2-USERMGMT-MIB / hm2PwdMgmtGroup.hm2PwdMgmtLoginAttemptsTimePeriod}  # Integer32, access=ru, range=0–60
  min_length: {HM2-USERMGMT-MIB / hm2PwdMgmtGroup.hm2PwdMgmtMinLength}  # Integer32, access=ru, range=1–64
  snmp_enc: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserSnmpEncType}  # INTEGER, access=ru, allowed=['none', 'des', 'aesCfb128', 'aesCfb256']
  level: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserAccessRole}  # Hm2UserAccessRoles, access=ru
  password: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserPassword}  # DisplayString, access=ru, range=0–64
  snmp_auth: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserSnmpAuthType}  # INTEGER, access=ru, allowed=['hmacmd5', 'hmacsha']
  user_status: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserStatus}  # RowStatus, access=crud
  snmp_enc_password: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserSnmpEncPassword}  # DisplayString, access=ru, range=0–64
}
```
</details>

<details><summary>SNMP sources (14/18 attrs)</summary>

```
SNMP {
  default_password: {oid: 1.3.6.1.4.1.248.11.24.1.2.100.100.1.2}  # SnmpAdminString, access=r
  snmp_auth_password: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.10}  # DisplayString, access=ru, range=0–64
  username: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.1}  # SnmpAdminString, access=r, range=1–32
  locked: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.4}  # TruthValue, access=ru, allowed=[True, False]
  policy_check: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.6}  # HmEnabledStatus, access=ru, allowed=[True, False]
  max_attempts: {oid: 1.3.6.1.4.1.248.11.24.1.2.2, method: get}  # Integer32, access=ru, range=0–5
  lockout_time: {oid: 1.3.6.1.4.1.248.11.24.1.2.7, method: get}  # Integer32, access=ru, range=0–60
  min_length: {oid: 1.3.6.1.4.1.248.11.24.1.2.1, method: get}  # Integer32, access=ru, range=1–64
  snmp_enc: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.8}  # INTEGER, access=ru, allowed=['none', 'des', 'aesCfb128', 'aesCfb256']
  level: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.3}  # Hm2UserAccessRoles, access=ru
  password: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.2}  # DisplayString, access=ru, range=0–64
  snmp_auth: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.7}  # INTEGER, access=ru, allowed=['hmacmd5', 'hmacsha']
  user_status: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.9}  # RowStatus, access=crud
  snmp_enc_password: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.11}  # DisplayString, access=ru, range=0–64
}
```
</details>

<details><summary>SSH sources (10/18 attrs)</summary>

```
SSH {
  min_lowercase: {read: "show passwords"}
  min_numeric: {read: "show passwords"}
  username: {read: "show users"}  # SnmpAdminString, access=r, range=1–32
  min_uppercase: {read: "show passwords"}
  max_attempts: {read: "show passwords"}  # Integer32, access=ru, range=0–5
  lockout_time: {read: "show passwords"}  # Integer32, access=ru, range=0–60
  min_length: {read: "show passwords"}  # Integer32, access=ru, range=1–64
  min_special: {read: "show passwords"}
  password: {write: "users password {index} {password}"}  # DisplayString, access=ru, range=0–64
  user_status: {write: "users add {username}"}  # RowStatus, access=crud
}
```
</details>

### `create_user()`

**Create** | **Protocols:** MOPS, SNMP, SSH
Required: `username`, `password`

```
create_user() -> {
    level: "administrator"  // "unauthorized" | "guest" | "auditor" | "custom1" | "custom2" | "custom3" | "operator" | "administrator"
}
```


<details><summary>MOPS sources (3/3 attrs)</summary>

```
MOPS {
  level: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserAccessRole}  # Hm2UserAccessRoles, access=ru
  password: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserPassword}  # DisplayString, access=ru, range=0–64
  username: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserName}  # SnmpAdminString, access=r, range=1–32
}
```
</details>

<details><summary>SNMP sources (3/3 attrs)</summary>

```
SNMP {
  level: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.3}  # Hm2UserAccessRoles, access=ru
  password: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.2}  # DisplayString, access=ru, range=0–64
  username: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.1}  # SnmpAdminString, access=r, range=1–32
}
```
</details>

<details><summary>SSH sources (2/3 attrs)</summary>

```
SSH {
  password: {write: "users password {index} {password}"}  # DisplayString, access=ru, range=0–64
  username: {read: "show users"}  # SnmpAdminString, access=r, range=1–32
}
```
</details>

### `delete_user()`

**Delete** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (14/18 attrs)</summary>

```
MOPS {
  default_password: {HM2-USERMGMT-MIB / hm2PwdMgmtDefaultPwdStatusEntry.hm2PwdMgmtDefaultPwdStatusUserName}  # SnmpAdminString, access=r
  snmp_auth_password: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserSnmpAuthPassword}  # DisplayString, access=ru, range=0–64
  username: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserName}  # SnmpAdminString, access=r, range=1–32
  locked: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserLockoutStatus}  # TruthValue, access=ru, allowed=[True, False]
  policy_check: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserPwdPolicyChk}  # HmEnabledStatus, access=ru, allowed=[True, False]
  max_attempts: {HM2-USERMGMT-MIB / hm2PwdMgmtGroup.hm2PwdMgmtLoginAttempts}  # Integer32, access=ru, range=0–5
  lockout_time: {HM2-USERMGMT-MIB / hm2PwdMgmtGroup.hm2PwdMgmtLoginAttemptsTimePeriod}  # Integer32, access=ru, range=0–60
  min_length: {HM2-USERMGMT-MIB / hm2PwdMgmtGroup.hm2PwdMgmtMinLength}  # Integer32, access=ru, range=1–64
  snmp_enc: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserSnmpEncType}  # INTEGER, access=ru, allowed=['none', 'des', 'aesCfb128', 'aesCfb256']
  level: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserAccessRole}  # Hm2UserAccessRoles, access=ru
  password: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserPassword}  # DisplayString, access=ru, range=0–64
  snmp_auth: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserSnmpAuthType}  # INTEGER, access=ru, allowed=['hmacmd5', 'hmacsha']
  user_status: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserStatus}  # RowStatus, access=crud
  snmp_enc_password: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserSnmpEncPassword}  # DisplayString, access=ru, range=0–64
}
```
</details>

<details><summary>SNMP sources (14/18 attrs)</summary>

```
SNMP {
  default_password: {oid: 1.3.6.1.4.1.248.11.24.1.2.100.100.1.2}  # SnmpAdminString, access=r
  snmp_auth_password: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.10}  # DisplayString, access=ru, range=0–64
  username: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.1}  # SnmpAdminString, access=r, range=1–32
  locked: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.4}  # TruthValue, access=ru, allowed=[True, False]
  policy_check: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.6}  # HmEnabledStatus, access=ru, allowed=[True, False]
  max_attempts: {oid: 1.3.6.1.4.1.248.11.24.1.2.2, method: get}  # Integer32, access=ru, range=0–5
  lockout_time: {oid: 1.3.6.1.4.1.248.11.24.1.2.7, method: get}  # Integer32, access=ru, range=0–60
  min_length: {oid: 1.3.6.1.4.1.248.11.24.1.2.1, method: get}  # Integer32, access=ru, range=1–64
  snmp_enc: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.8}  # INTEGER, access=ru, allowed=['none', 'des', 'aesCfb128', 'aesCfb256']
  level: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.3}  # Hm2UserAccessRoles, access=ru
  password: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.2}  # DisplayString, access=ru, range=0–64
  snmp_auth: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.7}  # INTEGER, access=ru, allowed=['hmacmd5', 'hmacsha']
  user_status: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.9}  # RowStatus, access=crud
  snmp_enc_password: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.11}  # DisplayString, access=ru, range=0–64
}
```
</details>

<details><summary>SSH sources (10/18 attrs)</summary>

```
SSH {
  min_lowercase: {read: "show passwords"}
  min_numeric: {read: "show passwords"}
  username: {read: "show users"}  # SnmpAdminString, access=r, range=1–32
  min_uppercase: {read: "show passwords"}
  max_attempts: {read: "show passwords"}  # Integer32, access=ru, range=0–5
  lockout_time: {read: "show passwords"}  # Integer32, access=ru, range=0–60
  min_length: {read: "show passwords"}  # Integer32, access=ru, range=1–64
  min_special: {read: "show passwords"}
  password: {write: "users password {index} {password}"}  # DisplayString, access=ru, range=0–64
  user_status: {write: "users add {username}"}  # RowStatus, access=crud
}
```
</details>

### `get_login_policy()`

**Read** | **Protocols:** MOPS, SNMP, SSH

```
get_login_policy() -> {
    min_length: 8  // int
    max_attempts: 3  // int
    lockout_time: 300  // int
}
```


<details><summary>MOPS sources (3/3 attrs)</summary>

```
MOPS {
  lockout_time: {HM2-USERMGMT-MIB / hm2PwdMgmtGroup.hm2PwdMgmtLoginAttemptsTimePeriod}  # Integer32, access=ru, range=0–60
  max_attempts: {HM2-USERMGMT-MIB / hm2PwdMgmtGroup.hm2PwdMgmtLoginAttempts}  # Integer32, access=ru, range=0–5
  min_length: {HM2-USERMGMT-MIB / hm2PwdMgmtGroup.hm2PwdMgmtMinLength}  # Integer32, access=ru, range=1–64
}
```
</details>

<details><summary>SNMP sources (3/3 attrs)</summary>

```
SNMP {
  lockout_time: {oid: 1.3.6.1.4.1.248.11.24.1.2.7, method: get}  # Integer32, access=ru, range=0–60
  max_attempts: {oid: 1.3.6.1.4.1.248.11.24.1.2.2, method: get}  # Integer32, access=ru, range=0–5
  min_length: {oid: 1.3.6.1.4.1.248.11.24.1.2.1, method: get}  # Integer32, access=ru, range=1–64
}
```
</details>

<details><summary>SSH sources (3/3 attrs)</summary>

```
SSH {
  lockout_time: {read: "show passwords"}  # Integer32, access=ru, range=0–60
  max_attempts: {read: "show passwords"}  # Integer32, access=ru, range=0–5
  min_length: {read: "show passwords"}  # Integer32, access=ru, range=1–64
}
```
</details>

### `set_login_policy()`

**Update** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (14/18 attrs)</summary>

```
MOPS {
  default_password: {HM2-USERMGMT-MIB / hm2PwdMgmtDefaultPwdStatusEntry.hm2PwdMgmtDefaultPwdStatusUserName}  # SnmpAdminString, access=r
  snmp_auth_password: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserSnmpAuthPassword}  # DisplayString, access=ru, range=0–64
  username: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserName}  # SnmpAdminString, access=r, range=1–32
  locked: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserLockoutStatus}  # TruthValue, access=ru, allowed=[True, False]
  policy_check: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserPwdPolicyChk}  # HmEnabledStatus, access=ru, allowed=[True, False]
  max_attempts: {HM2-USERMGMT-MIB / hm2PwdMgmtGroup.hm2PwdMgmtLoginAttempts}  # Integer32, access=ru, range=0–5
  lockout_time: {HM2-USERMGMT-MIB / hm2PwdMgmtGroup.hm2PwdMgmtLoginAttemptsTimePeriod}  # Integer32, access=ru, range=0–60
  min_length: {HM2-USERMGMT-MIB / hm2PwdMgmtGroup.hm2PwdMgmtMinLength}  # Integer32, access=ru, range=1–64
  snmp_enc: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserSnmpEncType}  # INTEGER, access=ru, allowed=['none', 'des', 'aesCfb128', 'aesCfb256']
  level: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserAccessRole}  # Hm2UserAccessRoles, access=ru
  password: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserPassword}  # DisplayString, access=ru, range=0–64
  snmp_auth: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserSnmpAuthType}  # INTEGER, access=ru, allowed=['hmacmd5', 'hmacsha']
  user_status: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserStatus}  # RowStatus, access=crud
  snmp_enc_password: {HM2-USERMGMT-MIB / hm2UserConfigEntry.hm2UserSnmpEncPassword}  # DisplayString, access=ru, range=0–64
}
```
</details>

<details><summary>SNMP sources (14/18 attrs)</summary>

```
SNMP {
  default_password: {oid: 1.3.6.1.4.1.248.11.24.1.2.100.100.1.2}  # SnmpAdminString, access=r
  snmp_auth_password: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.10}  # DisplayString, access=ru, range=0–64
  username: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.1}  # SnmpAdminString, access=r, range=1–32
  locked: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.4}  # TruthValue, access=ru, allowed=[True, False]
  policy_check: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.6}  # HmEnabledStatus, access=ru, allowed=[True, False]
  max_attempts: {oid: 1.3.6.1.4.1.248.11.24.1.2.2, method: get}  # Integer32, access=ru, range=0–5
  lockout_time: {oid: 1.3.6.1.4.1.248.11.24.1.2.7, method: get}  # Integer32, access=ru, range=0–60
  min_length: {oid: 1.3.6.1.4.1.248.11.24.1.2.1, method: get}  # Integer32, access=ru, range=1–64
  snmp_enc: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.8}  # INTEGER, access=ru, allowed=['none', 'des', 'aesCfb128', 'aesCfb256']
  level: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.3}  # Hm2UserAccessRoles, access=ru
  password: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.2}  # DisplayString, access=ru, range=0–64
  snmp_auth: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.7}  # INTEGER, access=ru, allowed=['hmacmd5', 'hmacsha']
  user_status: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.9}  # RowStatus, access=crud
  snmp_enc_password: {oid: 1.3.6.1.4.1.248.11.24.1.1.1.1.11}  # DisplayString, access=ru, range=0–64
}
```
</details>

<details><summary>SSH sources (10/18 attrs)</summary>

```
SSH {
  min_lowercase: {read: "show passwords"}
  min_numeric: {read: "show passwords"}
  username: {read: "show users"}  # SnmpAdminString, access=r, range=1–32
  min_uppercase: {read: "show passwords"}
  max_attempts: {read: "show passwords"}  # Integer32, access=ru, range=0–5
  lockout_time: {read: "show passwords"}  # Integer32, access=ru, range=0–60
  min_length: {read: "show passwords"}  # Integer32, access=ru, range=1–64
  min_special: {read: "show passwords"}
  password: {write: "users password {index} {password}"}  # DisplayString, access=ru, range=0–64
  user_status: {write: "users add {username}"}  # RowStatus, access=crud
}
```
</details>

---

## vlan

_VLAN configuration, port membership and ingress/egress rules_

### `get_vlans()`

**Read** | **Protocols:** MOPS, SNMP
Primary key: `vlan_id`

```
get_vlans() -> {
    name: ""  // str
    ports: {...}  // dict (computed)
}
```


<details><summary>MOPS sources (2/3 attrs)</summary>

```
MOPS {
  vlan_id: {Q-BRIDGE-MIB / dot1qVlanCurrentEntry.dot1qVlanIndex}  # VlanIndex, access=r, range=1–4094
  name: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanStaticName}  # SnmpAdminString, access=ru, range=0–32
}
```
</details>

<details><summary>SNMP sources (2/3 attrs)</summary>

```
SNMP {
  vlan_id: {oid: 1.3.6.1.2.1.17.7.1.4.2.1.2}  # VlanIndex, access=r, range=1–4094
  name: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.1}  # SnmpAdminString, access=ru, range=0–32
}
```
</details>

### `create_vlan()`

**Create** | **Protocols:** MOPS, SNMP
Required: `vlan_id`

<details><summary>MOPS sources (1/1 attrs)</summary>

```
MOPS {
  vlan_id: {Q-BRIDGE-MIB / dot1qVlanCurrentEntry.dot1qVlanIndex}  # VlanIndex, access=r, range=1–4094
}
```
</details>

<details><summary>SNMP sources (1/1 attrs)</summary>

```
SNMP {
  vlan_id: {oid: 1.3.6.1.2.1.17.7.1.4.2.1.2}  # VlanIndex, access=r, range=1–4094
}
```
</details>

### `set_vlan()`

**Update** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (10/11 attrs)</summary>

```
MOPS {
  ingress_filtering: {Q-BRIDGE-MIB / dot1qPortVlanEntry.dot1qPortIngressFiltering}  # TruthValue, access=ru, allowed=[True, False]
  untagged_ports: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanStaticUntaggedPorts}  # PortList, access=ru
  vlan_status: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanStaticRowStatus}  # RowStatus, access=crud
  egress_ports: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanStaticEgressPorts}  # PortList, access=ru
  interface_name: {IF-MIB / ifXEntry.ifName}  # DisplayString, access=r
  vlan_id: {Q-BRIDGE-MIB / dot1qVlanCurrentEntry.dot1qVlanIndex}  # VlanIndex, access=r, range=1–4094
  pvid: {Q-BRIDGE-MIB / dot1qPortVlanEntry.dot1qPvid}  # VlanIndex, access=ru, range=1–4094
  acceptable_frame_types: {Q-BRIDGE-MIB / dot1qPortVlanEntry.dot1qPortAcceptableFrameTypes}  # INTEGER, access=ru, allowed=['admitAll', 'admitOnlyVlanTagged']
  name: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanStaticName}  # SnmpAdminString, access=ru, range=0–32
  forbidden_ports: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanForbiddenEgressPorts}  # PortList, access=ru
}
```
</details>

<details><summary>SNMP sources (10/11 attrs)</summary>

```
SNMP {
  ingress_filtering: {oid: 1.3.6.1.2.1.17.7.1.4.5.1.3}  # TruthValue, access=ru, allowed=[True, False]
  untagged_ports: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.4}  # PortList, access=ru
  vlan_status: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.5}  # RowStatus, access=crud
  egress_ports: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.2}  # PortList, access=ru
  interface_name: {oid: 1.3.6.1.2.1.31.1.1.1.1}  # DisplayString, access=r
  vlan_id: {oid: 1.3.6.1.2.1.17.7.1.4.2.1.2}  # VlanIndex, access=r, range=1–4094
  pvid: {oid: 1.3.6.1.2.1.17.7.1.4.5.1.1}  # VlanIndex, access=ru, range=1–4094
  acceptable_frame_types: {oid: 1.3.6.1.2.1.17.7.1.4.5.1.2}  # INTEGER, access=ru, allowed=['admitAll', 'admitOnlyVlanTagged']
  name: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.1}  # SnmpAdminString, access=ru, range=0–32
  forbidden_ports: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.3}  # PortList, access=ru
}
```
</details>

<details><summary>SSH sources (1/11 attrs)</summary>

```
SSH {
  vlan_status: {write: "vlan add {index}"}  # RowStatus, access=crud
}
```
</details>

### `delete_vlan()`

**Delete** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (10/11 attrs)</summary>

```
MOPS {
  ingress_filtering: {Q-BRIDGE-MIB / dot1qPortVlanEntry.dot1qPortIngressFiltering}  # TruthValue, access=ru, allowed=[True, False]
  untagged_ports: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanStaticUntaggedPorts}  # PortList, access=ru
  vlan_status: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanStaticRowStatus}  # RowStatus, access=crud
  egress_ports: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanStaticEgressPorts}  # PortList, access=ru
  interface_name: {IF-MIB / ifXEntry.ifName}  # DisplayString, access=r
  vlan_id: {Q-BRIDGE-MIB / dot1qVlanCurrentEntry.dot1qVlanIndex}  # VlanIndex, access=r, range=1–4094
  pvid: {Q-BRIDGE-MIB / dot1qPortVlanEntry.dot1qPvid}  # VlanIndex, access=ru, range=1–4094
  acceptable_frame_types: {Q-BRIDGE-MIB / dot1qPortVlanEntry.dot1qPortAcceptableFrameTypes}  # INTEGER, access=ru, allowed=['admitAll', 'admitOnlyVlanTagged']
  name: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanStaticName}  # SnmpAdminString, access=ru, range=0–32
  forbidden_ports: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanForbiddenEgressPorts}  # PortList, access=ru
}
```
</details>

<details><summary>SNMP sources (10/11 attrs)</summary>

```
SNMP {
  ingress_filtering: {oid: 1.3.6.1.2.1.17.7.1.4.5.1.3}  # TruthValue, access=ru, allowed=[True, False]
  untagged_ports: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.4}  # PortList, access=ru
  vlan_status: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.5}  # RowStatus, access=crud
  egress_ports: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.2}  # PortList, access=ru
  interface_name: {oid: 1.3.6.1.2.1.31.1.1.1.1}  # DisplayString, access=r
  vlan_id: {oid: 1.3.6.1.2.1.17.7.1.4.2.1.2}  # VlanIndex, access=r, range=1–4094
  pvid: {oid: 1.3.6.1.2.1.17.7.1.4.5.1.1}  # VlanIndex, access=ru, range=1–4094
  acceptable_frame_types: {oid: 1.3.6.1.2.1.17.7.1.4.5.1.2}  # INTEGER, access=ru, allowed=['admitAll', 'admitOnlyVlanTagged']
  name: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.1}  # SnmpAdminString, access=ru, range=0–32
  forbidden_ports: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.3}  # PortList, access=ru
}
```
</details>

<details><summary>SSH sources (1/11 attrs)</summary>

```
SSH {
  vlan_status: {write: "vlan add {index}"}  # RowStatus, access=crud
}
```
</details>

### `get_vlan_ingress()`

**Read** | **Protocols:** MOPS, SNMP
Primary key: `pvid` | Key map: `bridge_port`

```
get_vlan_ingress() -> {
    pvid: 1  // int
    ingress_filtering: False  // bool
    acceptable_frame_types: "admitAll"  // "admitAll" | "admitOnlyVlanTagged"
}
```


<details><summary>MOPS sources (3/3 attrs)</summary>

```
MOPS {
  acceptable_frame_types: {Q-BRIDGE-MIB / dot1qPortVlanEntry.dot1qPortAcceptableFrameTypes}  # INTEGER, access=ru, allowed=['admitAll', 'admitOnlyVlanTagged']
  ingress_filtering: {Q-BRIDGE-MIB / dot1qPortVlanEntry.dot1qPortIngressFiltering}  # TruthValue, access=ru, allowed=[True, False]
  pvid: {Q-BRIDGE-MIB / dot1qPortVlanEntry.dot1qPvid}  # VlanIndex, access=ru, range=1–4094
}
```
</details>

<details><summary>SNMP sources (3/3 attrs)</summary>

```
SNMP {
  acceptable_frame_types: {oid: 1.3.6.1.2.1.17.7.1.4.5.1.2}  # INTEGER, access=ru, allowed=['admitAll', 'admitOnlyVlanTagged']
  ingress_filtering: {oid: 1.3.6.1.2.1.17.7.1.4.5.1.3}  # TruthValue, access=ru, allowed=[True, False]
  pvid: {oid: 1.3.6.1.2.1.17.7.1.4.5.1.1}  # VlanIndex, access=ru, range=1–4094
}
```
</details>

### `set_vlan_ingress()`

**Update** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (10/11 attrs)</summary>

```
MOPS {
  ingress_filtering: {Q-BRIDGE-MIB / dot1qPortVlanEntry.dot1qPortIngressFiltering}  # TruthValue, access=ru, allowed=[True, False]
  untagged_ports: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanStaticUntaggedPorts}  # PortList, access=ru
  vlan_status: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanStaticRowStatus}  # RowStatus, access=crud
  egress_ports: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanStaticEgressPorts}  # PortList, access=ru
  interface_name: {IF-MIB / ifXEntry.ifName}  # DisplayString, access=r
  vlan_id: {Q-BRIDGE-MIB / dot1qVlanCurrentEntry.dot1qVlanIndex}  # VlanIndex, access=r, range=1–4094
  pvid: {Q-BRIDGE-MIB / dot1qPortVlanEntry.dot1qPvid}  # VlanIndex, access=ru, range=1–4094
  acceptable_frame_types: {Q-BRIDGE-MIB / dot1qPortVlanEntry.dot1qPortAcceptableFrameTypes}  # INTEGER, access=ru, allowed=['admitAll', 'admitOnlyVlanTagged']
  name: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanStaticName}  # SnmpAdminString, access=ru, range=0–32
  forbidden_ports: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanForbiddenEgressPorts}  # PortList, access=ru
}
```
</details>

<details><summary>SNMP sources (10/11 attrs)</summary>

```
SNMP {
  ingress_filtering: {oid: 1.3.6.1.2.1.17.7.1.4.5.1.3}  # TruthValue, access=ru, allowed=[True, False]
  untagged_ports: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.4}  # PortList, access=ru
  vlan_status: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.5}  # RowStatus, access=crud
  egress_ports: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.2}  # PortList, access=ru
  interface_name: {oid: 1.3.6.1.2.1.31.1.1.1.1}  # DisplayString, access=r
  vlan_id: {oid: 1.3.6.1.2.1.17.7.1.4.2.1.2}  # VlanIndex, access=r, range=1–4094
  pvid: {oid: 1.3.6.1.2.1.17.7.1.4.5.1.1}  # VlanIndex, access=ru, range=1–4094
  acceptable_frame_types: {oid: 1.3.6.1.2.1.17.7.1.4.5.1.2}  # INTEGER, access=ru, allowed=['admitAll', 'admitOnlyVlanTagged']
  name: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.1}  # SnmpAdminString, access=ru, range=0–32
  forbidden_ports: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.3}  # PortList, access=ru
}
```
</details>

<details><summary>SSH sources (1/11 attrs)</summary>

```
SSH {
  vlan_status: {write: "vlan add {index}"}  # RowStatus, access=crud
}
```
</details>

### `set_access_port()`

**Update** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (10/11 attrs)</summary>

```
MOPS {
  ingress_filtering: {Q-BRIDGE-MIB / dot1qPortVlanEntry.dot1qPortIngressFiltering}  # TruthValue, access=ru, allowed=[True, False]
  untagged_ports: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanStaticUntaggedPorts}  # PortList, access=ru
  vlan_status: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanStaticRowStatus}  # RowStatus, access=crud
  egress_ports: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanStaticEgressPorts}  # PortList, access=ru
  interface_name: {IF-MIB / ifXEntry.ifName}  # DisplayString, access=r
  vlan_id: {Q-BRIDGE-MIB / dot1qVlanCurrentEntry.dot1qVlanIndex}  # VlanIndex, access=r, range=1–4094
  pvid: {Q-BRIDGE-MIB / dot1qPortVlanEntry.dot1qPvid}  # VlanIndex, access=ru, range=1–4094
  acceptable_frame_types: {Q-BRIDGE-MIB / dot1qPortVlanEntry.dot1qPortAcceptableFrameTypes}  # INTEGER, access=ru, allowed=['admitAll', 'admitOnlyVlanTagged']
  name: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanStaticName}  # SnmpAdminString, access=ru, range=0–32
  forbidden_ports: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanForbiddenEgressPorts}  # PortList, access=ru
}
```
</details>

<details><summary>SNMP sources (10/11 attrs)</summary>

```
SNMP {
  ingress_filtering: {oid: 1.3.6.1.2.1.17.7.1.4.5.1.3}  # TruthValue, access=ru, allowed=[True, False]
  untagged_ports: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.4}  # PortList, access=ru
  vlan_status: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.5}  # RowStatus, access=crud
  egress_ports: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.2}  # PortList, access=ru
  interface_name: {oid: 1.3.6.1.2.1.31.1.1.1.1}  # DisplayString, access=r
  vlan_id: {oid: 1.3.6.1.2.1.17.7.1.4.2.1.2}  # VlanIndex, access=r, range=1–4094
  pvid: {oid: 1.3.6.1.2.1.17.7.1.4.5.1.1}  # VlanIndex, access=ru, range=1–4094
  acceptable_frame_types: {oid: 1.3.6.1.2.1.17.7.1.4.5.1.2}  # INTEGER, access=ru, allowed=['admitAll', 'admitOnlyVlanTagged']
  name: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.1}  # SnmpAdminString, access=ru, range=0–32
  forbidden_ports: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.3}  # PortList, access=ru
}
```
</details>

<details><summary>SSH sources (1/11 attrs)</summary>

```
SSH {
  vlan_status: {write: "vlan add {index}"}  # RowStatus, access=crud
}
```
</details>

### `get_vlan_egress()`

**Read** | **Protocols:** MOPS, SNMP
Primary key: `vlan_id`

```
get_vlan_egress() -> {
    egress_ports: [...]  // list (via ifindex)
    untagged_ports: [...]  // list (via ifindex)
}
```


<details><summary>MOPS sources (3/3 attrs)</summary>

```
MOPS {
  untagged_ports: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanStaticUntaggedPorts}  # PortList, access=ru
  vlan_id: {Q-BRIDGE-MIB / dot1qVlanCurrentEntry.dot1qVlanIndex}  # VlanIndex, access=r, range=1–4094
  egress_ports: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanStaticEgressPorts}  # PortList, access=ru
}
```
</details>

<details><summary>SNMP sources (3/3 attrs)</summary>

```
SNMP {
  untagged_ports: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.4}  # PortList, access=ru
  vlan_id: {oid: 1.3.6.1.2.1.17.7.1.4.2.1.2}  # VlanIndex, access=r, range=1–4094
  egress_ports: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.2}  # PortList, access=ru
}
```
</details>

### `set_vlan_egress()`

**Update** | **Protocols:** MOPS, SNMP, SSH

<details><summary>MOPS sources (10/11 attrs)</summary>

```
MOPS {
  ingress_filtering: {Q-BRIDGE-MIB / dot1qPortVlanEntry.dot1qPortIngressFiltering}  # TruthValue, access=ru, allowed=[True, False]
  untagged_ports: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanStaticUntaggedPorts}  # PortList, access=ru
  vlan_status: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanStaticRowStatus}  # RowStatus, access=crud
  egress_ports: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanStaticEgressPorts}  # PortList, access=ru
  interface_name: {IF-MIB / ifXEntry.ifName}  # DisplayString, access=r
  vlan_id: {Q-BRIDGE-MIB / dot1qVlanCurrentEntry.dot1qVlanIndex}  # VlanIndex, access=r, range=1–4094
  pvid: {Q-BRIDGE-MIB / dot1qPortVlanEntry.dot1qPvid}  # VlanIndex, access=ru, range=1–4094
  acceptable_frame_types: {Q-BRIDGE-MIB / dot1qPortVlanEntry.dot1qPortAcceptableFrameTypes}  # INTEGER, access=ru, allowed=['admitAll', 'admitOnlyVlanTagged']
  name: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanStaticName}  # SnmpAdminString, access=ru, range=0–32
  forbidden_ports: {Q-BRIDGE-MIB / dot1qVlanStaticEntry.dot1qVlanForbiddenEgressPorts}  # PortList, access=ru
}
```
</details>

<details><summary>SNMP sources (10/11 attrs)</summary>

```
SNMP {
  ingress_filtering: {oid: 1.3.6.1.2.1.17.7.1.4.5.1.3}  # TruthValue, access=ru, allowed=[True, False]
  untagged_ports: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.4}  # PortList, access=ru
  vlan_status: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.5}  # RowStatus, access=crud
  egress_ports: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.2}  # PortList, access=ru
  interface_name: {oid: 1.3.6.1.2.1.31.1.1.1.1}  # DisplayString, access=r
  vlan_id: {oid: 1.3.6.1.2.1.17.7.1.4.2.1.2}  # VlanIndex, access=r, range=1–4094
  pvid: {oid: 1.3.6.1.2.1.17.7.1.4.5.1.1}  # VlanIndex, access=ru, range=1–4094
  acceptable_frame_types: {oid: 1.3.6.1.2.1.17.7.1.4.5.1.2}  # INTEGER, access=ru, allowed=['admitAll', 'admitOnlyVlanTagged']
  name: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.1}  # SnmpAdminString, access=ru, range=0–32
  forbidden_ports: {oid: 1.3.6.1.2.1.17.7.1.4.3.1.3}  # PortList, access=ru
}
```
</details>

<details><summary>SSH sources (1/11 attrs)</summary>

```
SSH {
  vlan_status: {write: "vlan add {index}"}  # RowStatus, access=crud
}
```
</details>

---

## vrrp

_VRRP virtual router redundancy — global config, per-instance CRUD, stats_

### `get_vrrp()`

**Read** | **Protocols:** MOPS, SNMP

```
get_vrrp() -> {
    enabled: False  // bool
    trap_auth_failure: False  // bool
    trap_new_master: False  // bool
}
```


<details><summary>MOPS sources (3/3 attrs)</summary>

```
MOPS {
  trap_auth_failure: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSnmpTrapFlagsConfigGroupLayer3.hm2AgentSnmpVRRPAuthFailureTrapFlag}  # HmEnabledStatus, access=ru, allowed=[True, False]
  enabled: {HM2-PLATFORM-ROUTING-MIB / hm2AgentRouterVrrpConfigGroup.hm2AgentRouterVrrpAdminState}  # HmEnabledStatus, access=ru, allowed=[True, False]
  trap_new_master: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSnmpTrapFlagsConfigGroupLayer3.hm2AgentSnmpVRRPNewMasterTrapFlag}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

<details><summary>SNMP sources (3/3 attrs)</summary>

```
SNMP {
  trap_auth_failure: {oid: 1.3.6.1.4.1.248.12.2.5.2, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  enabled: {oid: 1.3.6.1.4.1.248.12.2.8.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  trap_new_master: {oid: 1.3.6.1.4.1.248.12.2.5.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
}
```
</details>

### `get_vrrp_instances()`

**Read** | **Protocols:** MOPS, SNMP
Primary key: `state` | Key map: `ifindex`

```
get_vrrp_instances() -> {
    vrid: 0  // int
    admin_state: "down"  // "up" | "down"
    priority: 100  // int
    current_priority: 0  // int
    preempt: True  // bool
    interval: 1  // int
    accept_mode: False  // bool
    primary_ip: ""  // str
    virtual_ip: ""  // str
    auth_type: "none"  // "none" | "simple" | "ip_ah"
    state: "initialize"  // "initialize" | "backup" | "master"
    master_ip: ""  // str
    virtual_mac: ""  // str
    uptime: ""  // str
    ip_count: 0  // int
}
```


<details><summary>MOPS sources (14/16 attrs)</summary>

```
MOPS {
  current_priority: {VRRP-MIB / vrrpOperEntry.vrrpOperPriority}  # Integer32, access=ru, range=0–255
  preempt: {VRRP-MIB / vrrpOperEntry.vrrpOperPreemptMode}  # TruthValue, access=ru, allowed=[True, False]
  master_ip: {VRRP-MIB / vrrpOperEntry.vrrpOperMasterIpAddr}  # IpAddress, access=r
  virtual_ip: {HM2-PLATFORM-ROUTING-MIB / hm2AgentVrrpExtEntry.hm2AgentVrrpPrimaryVirtualAddress}  # IpAddress, access=r
  ip_count: {VRRP-MIB / vrrpOperEntry.vrrpOperIpAddrCount}  # Integer32, access=r, range=0–255
  uptime: {VRRP-MIB / vrrpOperEntry.vrrpOperVirtualRouterUpTime}  # TimeStamp, access=r
  admin_state: {VRRP-MIB / vrrpOperEntry.vrrpOperAdminState}  # INTEGER, access=ru
  priority: {HM2-PLATFORM-ROUTING-MIB / hm2AgentVrrpExtEntry.hm2AgentVrrpExtCfgPriority}  # Integer32, access=ru, range=1–254
  interval: {VRRP-MIB / vrrpOperEntry.vrrpOperAdvertisementInterval}  # Integer32, access=ru, range=1–255
  accept_mode: {VRRP-MIB / vrrpOperEntry.vrrpOperAcceptMode}  # TruthValue, access=ru, allowed=[True, False]
  auth_type: {VRRP-MIB / vrrpOperEntry.vrrpOperAuthType}  # INTEGER, access=ru
  state: {VRRP-MIB / vrrpOperEntry.vrrpOperState}  # INTEGER, access=r
  virtual_mac: {VRRP-MIB / vrrpOperEntry.vrrpOperVirtualMacAddr}  # MacAddress, access=r
  primary_ip: {VRRP-MIB / vrrpOperEntry.vrrpOperPrimaryIpAddr}  # IpAddress, access=ru
}
```
</details>

<details><summary>SNMP sources (14/16 attrs)</summary>

```
SNMP {
  current_priority: {oid: 1.3.6.1.2.1.68.1.3.1.5}  # Integer32, access=ru, range=0–255
  preempt: {oid: 1.3.6.1.2.1.68.1.3.1.12}  # TruthValue, access=ru, allowed=[True, False]
  master_ip: {oid: 1.3.6.1.2.1.68.1.3.1.7}  # IpAddress, access=r
  virtual_ip: {oid: 1.3.6.1.4.1.248.12.2.260.2.1.12}  # IpAddress, access=r
  ip_count: {oid: 1.3.6.1.2.1.68.1.3.1.6}  # Integer32, access=r, range=0–255
  uptime: {oid: 1.3.6.1.2.1.68.1.3.1.13}  # TimeStamp, access=r
  admin_state: {oid: 1.3.6.1.2.1.68.1.3.1.4}  # INTEGER, access=ru
  priority: {oid: 1.3.6.1.4.1.248.12.2.260.2.1.8}  # Integer32, access=ru, range=1–254
  interval: {oid: 1.3.6.1.2.1.68.1.3.1.11}  # Integer32, access=ru, range=1–255
  accept_mode: {oid: 1.3.6.1.2.1.68.1.3.1.16}  # TruthValue, access=ru, allowed=[True, False]
  auth_type: {oid: 1.3.6.1.2.1.68.1.3.1.9}  # INTEGER, access=ru
  state: {oid: 1.3.6.1.2.1.68.1.3.1.3}  # INTEGER, access=r
  virtual_mac: {oid: 1.3.6.1.2.1.68.1.3.1.2}  # MacAddress, access=r
  primary_ip: {oid: 1.3.6.1.2.1.68.1.3.1.8}  # IpAddress, access=ru
}
```
</details>

### `set_vrrp()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (25/30 attrs)</summary>

```
MOPS {
  current_priority: {VRRP-MIB / vrrpOperEntry.vrrpOperPriority}  # Integer32, access=ru, range=0–255
  preempt: {VRRP-MIB / vrrpOperEntry.vrrpOperPreemptMode}  # TruthValue, access=ru, allowed=[True, False]
  master_ip: {VRRP-MIB / vrrpOperEntry.vrrpOperMasterIpAddr}  # IpAddress, access=r
  uptime: {VRRP-MIB / vrrpOperEntry.vrrpOperVirtualRouterUpTime}  # TimeStamp, access=r
  admin_state: {VRRP-MIB / vrrpOperEntry.vrrpOperAdminState}  # INTEGER, access=ru
  trap_new_master: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSnmpTrapFlagsConfigGroupLayer3.hm2AgentSnmpVRRPNewMasterTrapFlag}  # HmEnabledStatus, access=ru, allowed=[True, False]
  row_status: {VRRP-MIB / vrrpOperEntry.vrrpOperRowStatus}  # RowStatus, access=crud
  auth_type: {VRRP-MIB / vrrpOperEntry.vrrpOperAuthType}  # INTEGER, access=ru
  enabled: {HM2-PLATFORM-ROUTING-MIB / hm2AgentRouterVrrpConfigGroup.hm2AgentRouterVrrpAdminState}  # HmEnabledStatus, access=ru, allowed=[True, False]
  virtual_ip: {HM2-PLATFORM-ROUTING-MIB / hm2AgentVrrpExtEntry.hm2AgentVrrpPrimaryVirtualAddress}  # IpAddress, access=r
  version_errors: {VRRP-MIB / vrrpStatistics.vrrpRouterVersionErrors}  # Counter32, access=r
  accept_mode: {VRRP-MIB / vrrpOperEntry.vrrpOperAcceptMode}  # TruthValue, access=ru, allowed=[True, False]
  vrid_errors: {VRRP-MIB / vrrpStatistics.vrrpRouterVrIdErrors}  # Counter32, access=r
  virtual_mac: {VRRP-MIB / vrrpOperEntry.vrrpOperVirtualMacAddr}  # MacAddress, access=r
  primary_ip: {VRRP-MIB / vrrpOperEntry.vrrpOperPrimaryIpAddr}  # IpAddress, access=ru
  trap_auth_failure: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSnmpTrapFlagsConfigGroupLayer3.hm2AgentSnmpVRRPAuthFailureTrapFlag}  # HmEnabledStatus, access=ru, allowed=[True, False]
  checksum_errors: {VRRP-MIB / vrrpStatistics.vrrpRouterChecksumErrors}  # Counter32, access=r
  priority: {HM2-PLATFORM-ROUTING-MIB / hm2AgentVrrpExtEntry.hm2AgentVrrpExtCfgPriority}  # Integer32, access=ru, range=1–254
  oper_status: {HM2-PLATFORM-ROUTING-MIB / hm2AgentVrrpTrackingEntry.hm2AgentVrrpTrackOperStatus}  # INTEGER, access=r
  track_row_status: {HM2-PLATFORM-ROUTING-MIB / hm2AgentVrrpTrackingEntry.hm2AgentVrrpTrackRowStatus}  # RowStatus, access=crud
  ip_count: {VRRP-MIB / vrrpOperEntry.vrrpOperIpAddrCount}  # Integer32, access=r, range=0–255
  interval: {VRRP-MIB / vrrpOperEntry.vrrpOperAdvertisementInterval}  # Integer32, access=ru, range=1–255
  decrement: {HM2-PLATFORM-ROUTING-MIB / hm2AgentVrrpTrackingEntry.hm2AgentVrrpTrackDecrement}  # Integer32, access=ru, range=1–253
  state: {VRRP-MIB / vrrpOperEntry.vrrpOperState}  # INTEGER, access=r
  auth_key: {VRRP-MIB / vrrpOperEntry.vrrpOperAuthKey}  # OCTET STRING, access=ru, range=0–16
}
```
</details>

<details><summary>SNMP sources (25/30 attrs)</summary>

```
SNMP {
  current_priority: {oid: 1.3.6.1.2.1.68.1.3.1.5}  # Integer32, access=ru, range=0–255
  preempt: {oid: 1.3.6.1.2.1.68.1.3.1.12}  # TruthValue, access=ru, allowed=[True, False]
  master_ip: {oid: 1.3.6.1.2.1.68.1.3.1.7}  # IpAddress, access=r
  uptime: {oid: 1.3.6.1.2.1.68.1.3.1.13}  # TimeStamp, access=r
  admin_state: {oid: 1.3.6.1.2.1.68.1.3.1.4}  # INTEGER, access=ru
  trap_new_master: {oid: 1.3.6.1.4.1.248.12.2.5.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  row_status: {oid: 1.3.6.1.2.1.68.1.3.1.15}  # RowStatus, access=crud
  auth_type: {oid: 1.3.6.1.2.1.68.1.3.1.9}  # INTEGER, access=ru
  enabled: {oid: 1.3.6.1.4.1.248.12.2.8.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  virtual_ip: {oid: 1.3.6.1.4.1.248.12.2.260.2.1.12}  # IpAddress, access=r
  version_errors: {oid: 1.3.6.1.2.1.68.2.2, method: get}  # Counter32, access=r
  accept_mode: {oid: 1.3.6.1.2.1.68.1.3.1.16}  # TruthValue, access=ru, allowed=[True, False]
  vrid_errors: {oid: 1.3.6.1.2.1.68.2.3, method: get}  # Counter32, access=r
  virtual_mac: {oid: 1.3.6.1.2.1.68.1.3.1.2}  # MacAddress, access=r
  primary_ip: {oid: 1.3.6.1.2.1.68.1.3.1.8}  # IpAddress, access=ru
  trap_auth_failure: {oid: 1.3.6.1.4.1.248.12.2.5.2, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  checksum_errors: {oid: 1.3.6.1.2.1.68.2.1, method: get}  # Counter32, access=r
  priority: {oid: 1.3.6.1.4.1.248.12.2.260.2.1.8}  # Integer32, access=ru, range=1–254
  oper_status: {oid: 1.3.6.1.4.1.248.12.2.260.1.1.5}  # INTEGER, access=r
  track_row_status: {oid: 1.3.6.1.4.1.248.12.2.260.1.1.6}  # RowStatus, access=crud
  ip_count: {oid: 1.3.6.1.2.1.68.1.3.1.6}  # Integer32, access=r, range=0–255
  interval: {oid: 1.3.6.1.2.1.68.1.3.1.11}  # Integer32, access=ru, range=1–255
  decrement: {oid: 1.3.6.1.4.1.248.12.2.260.1.1.4}  # Integer32, access=ru, range=1–253
  state: {oid: 1.3.6.1.2.1.68.1.3.1.3}  # INTEGER, access=r
  auth_key: {oid: 1.3.6.1.2.1.68.1.3.1.10}  # OCTET STRING, access=ru, range=0–16
}
```
</details>

### `set_vrrp_instance()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (25/30 attrs)</summary>

```
MOPS {
  current_priority: {VRRP-MIB / vrrpOperEntry.vrrpOperPriority}  # Integer32, access=ru, range=0–255
  preempt: {VRRP-MIB / vrrpOperEntry.vrrpOperPreemptMode}  # TruthValue, access=ru, allowed=[True, False]
  master_ip: {VRRP-MIB / vrrpOperEntry.vrrpOperMasterIpAddr}  # IpAddress, access=r
  uptime: {VRRP-MIB / vrrpOperEntry.vrrpOperVirtualRouterUpTime}  # TimeStamp, access=r
  admin_state: {VRRP-MIB / vrrpOperEntry.vrrpOperAdminState}  # INTEGER, access=ru
  trap_new_master: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSnmpTrapFlagsConfigGroupLayer3.hm2AgentSnmpVRRPNewMasterTrapFlag}  # HmEnabledStatus, access=ru, allowed=[True, False]
  row_status: {VRRP-MIB / vrrpOperEntry.vrrpOperRowStatus}  # RowStatus, access=crud
  auth_type: {VRRP-MIB / vrrpOperEntry.vrrpOperAuthType}  # INTEGER, access=ru
  enabled: {HM2-PLATFORM-ROUTING-MIB / hm2AgentRouterVrrpConfigGroup.hm2AgentRouterVrrpAdminState}  # HmEnabledStatus, access=ru, allowed=[True, False]
  virtual_ip: {HM2-PLATFORM-ROUTING-MIB / hm2AgentVrrpExtEntry.hm2AgentVrrpPrimaryVirtualAddress}  # IpAddress, access=r
  version_errors: {VRRP-MIB / vrrpStatistics.vrrpRouterVersionErrors}  # Counter32, access=r
  accept_mode: {VRRP-MIB / vrrpOperEntry.vrrpOperAcceptMode}  # TruthValue, access=ru, allowed=[True, False]
  vrid_errors: {VRRP-MIB / vrrpStatistics.vrrpRouterVrIdErrors}  # Counter32, access=r
  virtual_mac: {VRRP-MIB / vrrpOperEntry.vrrpOperVirtualMacAddr}  # MacAddress, access=r
  primary_ip: {VRRP-MIB / vrrpOperEntry.vrrpOperPrimaryIpAddr}  # IpAddress, access=ru
  trap_auth_failure: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSnmpTrapFlagsConfigGroupLayer3.hm2AgentSnmpVRRPAuthFailureTrapFlag}  # HmEnabledStatus, access=ru, allowed=[True, False]
  checksum_errors: {VRRP-MIB / vrrpStatistics.vrrpRouterChecksumErrors}  # Counter32, access=r
  priority: {HM2-PLATFORM-ROUTING-MIB / hm2AgentVrrpExtEntry.hm2AgentVrrpExtCfgPriority}  # Integer32, access=ru, range=1–254
  oper_status: {HM2-PLATFORM-ROUTING-MIB / hm2AgentVrrpTrackingEntry.hm2AgentVrrpTrackOperStatus}  # INTEGER, access=r
  track_row_status: {HM2-PLATFORM-ROUTING-MIB / hm2AgentVrrpTrackingEntry.hm2AgentVrrpTrackRowStatus}  # RowStatus, access=crud
  ip_count: {VRRP-MIB / vrrpOperEntry.vrrpOperIpAddrCount}  # Integer32, access=r, range=0–255
  interval: {VRRP-MIB / vrrpOperEntry.vrrpOperAdvertisementInterval}  # Integer32, access=ru, range=1–255
  decrement: {HM2-PLATFORM-ROUTING-MIB / hm2AgentVrrpTrackingEntry.hm2AgentVrrpTrackDecrement}  # Integer32, access=ru, range=1–253
  state: {VRRP-MIB / vrrpOperEntry.vrrpOperState}  # INTEGER, access=r
  auth_key: {VRRP-MIB / vrrpOperEntry.vrrpOperAuthKey}  # OCTET STRING, access=ru, range=0–16
}
```
</details>

<details><summary>SNMP sources (25/30 attrs)</summary>

```
SNMP {
  current_priority: {oid: 1.3.6.1.2.1.68.1.3.1.5}  # Integer32, access=ru, range=0–255
  preempt: {oid: 1.3.6.1.2.1.68.1.3.1.12}  # TruthValue, access=ru, allowed=[True, False]
  master_ip: {oid: 1.3.6.1.2.1.68.1.3.1.7}  # IpAddress, access=r
  uptime: {oid: 1.3.6.1.2.1.68.1.3.1.13}  # TimeStamp, access=r
  admin_state: {oid: 1.3.6.1.2.1.68.1.3.1.4}  # INTEGER, access=ru
  trap_new_master: {oid: 1.3.6.1.4.1.248.12.2.5.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  row_status: {oid: 1.3.6.1.2.1.68.1.3.1.15}  # RowStatus, access=crud
  auth_type: {oid: 1.3.6.1.2.1.68.1.3.1.9}  # INTEGER, access=ru
  enabled: {oid: 1.3.6.1.4.1.248.12.2.8.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  virtual_ip: {oid: 1.3.6.1.4.1.248.12.2.260.2.1.12}  # IpAddress, access=r
  version_errors: {oid: 1.3.6.1.2.1.68.2.2, method: get}  # Counter32, access=r
  accept_mode: {oid: 1.3.6.1.2.1.68.1.3.1.16}  # TruthValue, access=ru, allowed=[True, False]
  vrid_errors: {oid: 1.3.6.1.2.1.68.2.3, method: get}  # Counter32, access=r
  virtual_mac: {oid: 1.3.6.1.2.1.68.1.3.1.2}  # MacAddress, access=r
  primary_ip: {oid: 1.3.6.1.2.1.68.1.3.1.8}  # IpAddress, access=ru
  trap_auth_failure: {oid: 1.3.6.1.4.1.248.12.2.5.2, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  checksum_errors: {oid: 1.3.6.1.2.1.68.2.1, method: get}  # Counter32, access=r
  priority: {oid: 1.3.6.1.4.1.248.12.2.260.2.1.8}  # Integer32, access=ru, range=1–254
  oper_status: {oid: 1.3.6.1.4.1.248.12.2.260.1.1.5}  # INTEGER, access=r
  track_row_status: {oid: 1.3.6.1.4.1.248.12.2.260.1.1.6}  # RowStatus, access=crud
  ip_count: {oid: 1.3.6.1.2.1.68.1.3.1.6}  # Integer32, access=r, range=0–255
  interval: {oid: 1.3.6.1.2.1.68.1.3.1.11}  # Integer32, access=ru, range=1–255
  decrement: {oid: 1.3.6.1.4.1.248.12.2.260.1.1.4}  # Integer32, access=ru, range=1–253
  state: {oid: 1.3.6.1.2.1.68.1.3.1.3}  # INTEGER, access=r
  auth_key: {oid: 1.3.6.1.2.1.68.1.3.1.10}  # OCTET STRING, access=ru, range=0–16
}
```
</details>

### `create_vrrp()`

**Create** | **Protocols:** MOPS, SNMP
Required: `interface`, `vrid`, `primary_ip`

<details><summary>MOPS sources (1/3 attrs)</summary>

```
MOPS {
  primary_ip: {VRRP-MIB / vrrpOperEntry.vrrpOperPrimaryIpAddr}  # IpAddress, access=ru
}
```
</details>

<details><summary>SNMP sources (1/3 attrs)</summary>

```
SNMP {
  primary_ip: {oid: 1.3.6.1.2.1.68.1.3.1.8}  # IpAddress, access=ru
}
```
</details>

### `delete_vrrp()`

**Delete** | **Protocols:** None

### `get_vrrp_tracking()`

**Read** | **Protocols:** MOPS, SNMP
Primary key: `oper_status` | Key map: `ifindex`

```
get_vrrp_tracking() -> {
    track_vrid: 0  // int
    track_name: ""  // str
    decrement: 0  // int
    oper_status: "down"  // "up" | "down"
}
```


<details><summary>MOPS sources (2/5 attrs)</summary>

```
MOPS {
  oper_status: {HM2-PLATFORM-ROUTING-MIB / hm2AgentVrrpTrackingEntry.hm2AgentVrrpTrackOperStatus}  # INTEGER, access=r
  decrement: {HM2-PLATFORM-ROUTING-MIB / hm2AgentVrrpTrackingEntry.hm2AgentVrrpTrackDecrement}  # Integer32, access=ru, range=1–253
}
```
</details>

<details><summary>SNMP sources (2/5 attrs)</summary>

```
SNMP {
  oper_status: {oid: 1.3.6.1.4.1.248.12.2.260.1.1.5}  # INTEGER, access=r
  decrement: {oid: 1.3.6.1.4.1.248.12.2.260.1.1.4}  # Integer32, access=ru, range=1–253
}
```
</details>

### `create_vrrp_tracking()`

**Create** | **Protocols:** MOPS, SNMP
Required: `track_interface`, `track_vrid`, `track_name`, `decrement`

<details><summary>MOPS sources (1/4 attrs)</summary>

```
MOPS {
  decrement: {HM2-PLATFORM-ROUTING-MIB / hm2AgentVrrpTrackingEntry.hm2AgentVrrpTrackDecrement}  # Integer32, access=ru, range=1–253
}
```
</details>

<details><summary>SNMP sources (1/4 attrs)</summary>

```
SNMP {
  decrement: {oid: 1.3.6.1.4.1.248.12.2.260.1.1.4}  # Integer32, access=ru, range=1–253
}
```
</details>

### `delete_vrrp_tracking()`

**Delete** | **Protocols:** None

### `set_vrrp_tracking()`

**Update** | **Protocols:** MOPS, SNMP

<details><summary>MOPS sources (25/30 attrs)</summary>

```
MOPS {
  current_priority: {VRRP-MIB / vrrpOperEntry.vrrpOperPriority}  # Integer32, access=ru, range=0–255
  preempt: {VRRP-MIB / vrrpOperEntry.vrrpOperPreemptMode}  # TruthValue, access=ru, allowed=[True, False]
  master_ip: {VRRP-MIB / vrrpOperEntry.vrrpOperMasterIpAddr}  # IpAddress, access=r
  uptime: {VRRP-MIB / vrrpOperEntry.vrrpOperVirtualRouterUpTime}  # TimeStamp, access=r
  admin_state: {VRRP-MIB / vrrpOperEntry.vrrpOperAdminState}  # INTEGER, access=ru
  trap_new_master: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSnmpTrapFlagsConfigGroupLayer3.hm2AgentSnmpVRRPNewMasterTrapFlag}  # HmEnabledStatus, access=ru, allowed=[True, False]
  row_status: {VRRP-MIB / vrrpOperEntry.vrrpOperRowStatus}  # RowStatus, access=crud
  auth_type: {VRRP-MIB / vrrpOperEntry.vrrpOperAuthType}  # INTEGER, access=ru
  enabled: {HM2-PLATFORM-ROUTING-MIB / hm2AgentRouterVrrpConfigGroup.hm2AgentRouterVrrpAdminState}  # HmEnabledStatus, access=ru, allowed=[True, False]
  virtual_ip: {HM2-PLATFORM-ROUTING-MIB / hm2AgentVrrpExtEntry.hm2AgentVrrpPrimaryVirtualAddress}  # IpAddress, access=r
  version_errors: {VRRP-MIB / vrrpStatistics.vrrpRouterVersionErrors}  # Counter32, access=r
  accept_mode: {VRRP-MIB / vrrpOperEntry.vrrpOperAcceptMode}  # TruthValue, access=ru, allowed=[True, False]
  vrid_errors: {VRRP-MIB / vrrpStatistics.vrrpRouterVrIdErrors}  # Counter32, access=r
  virtual_mac: {VRRP-MIB / vrrpOperEntry.vrrpOperVirtualMacAddr}  # MacAddress, access=r
  primary_ip: {VRRP-MIB / vrrpOperEntry.vrrpOperPrimaryIpAddr}  # IpAddress, access=ru
  trap_auth_failure: {HM2-PLATFORM-ROUTING-MIB / hm2AgentSnmpTrapFlagsConfigGroupLayer3.hm2AgentSnmpVRRPAuthFailureTrapFlag}  # HmEnabledStatus, access=ru, allowed=[True, False]
  checksum_errors: {VRRP-MIB / vrrpStatistics.vrrpRouterChecksumErrors}  # Counter32, access=r
  priority: {HM2-PLATFORM-ROUTING-MIB / hm2AgentVrrpExtEntry.hm2AgentVrrpExtCfgPriority}  # Integer32, access=ru, range=1–254
  oper_status: {HM2-PLATFORM-ROUTING-MIB / hm2AgentVrrpTrackingEntry.hm2AgentVrrpTrackOperStatus}  # INTEGER, access=r
  track_row_status: {HM2-PLATFORM-ROUTING-MIB / hm2AgentVrrpTrackingEntry.hm2AgentVrrpTrackRowStatus}  # RowStatus, access=crud
  ip_count: {VRRP-MIB / vrrpOperEntry.vrrpOperIpAddrCount}  # Integer32, access=r, range=0–255
  interval: {VRRP-MIB / vrrpOperEntry.vrrpOperAdvertisementInterval}  # Integer32, access=ru, range=1–255
  decrement: {HM2-PLATFORM-ROUTING-MIB / hm2AgentVrrpTrackingEntry.hm2AgentVrrpTrackDecrement}  # Integer32, access=ru, range=1–253
  state: {VRRP-MIB / vrrpOperEntry.vrrpOperState}  # INTEGER, access=r
  auth_key: {VRRP-MIB / vrrpOperEntry.vrrpOperAuthKey}  # OCTET STRING, access=ru, range=0–16
}
```
</details>

<details><summary>SNMP sources (25/30 attrs)</summary>

```
SNMP {
  current_priority: {oid: 1.3.6.1.2.1.68.1.3.1.5}  # Integer32, access=ru, range=0–255
  preempt: {oid: 1.3.6.1.2.1.68.1.3.1.12}  # TruthValue, access=ru, allowed=[True, False]
  master_ip: {oid: 1.3.6.1.2.1.68.1.3.1.7}  # IpAddress, access=r
  uptime: {oid: 1.3.6.1.2.1.68.1.3.1.13}  # TimeStamp, access=r
  admin_state: {oid: 1.3.6.1.2.1.68.1.3.1.4}  # INTEGER, access=ru
  trap_new_master: {oid: 1.3.6.1.4.1.248.12.2.5.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  row_status: {oid: 1.3.6.1.2.1.68.1.3.1.15}  # RowStatus, access=crud
  auth_type: {oid: 1.3.6.1.2.1.68.1.3.1.9}  # INTEGER, access=ru
  enabled: {oid: 1.3.6.1.4.1.248.12.2.8.1, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  virtual_ip: {oid: 1.3.6.1.4.1.248.12.2.260.2.1.12}  # IpAddress, access=r
  version_errors: {oid: 1.3.6.1.2.1.68.2.2, method: get}  # Counter32, access=r
  accept_mode: {oid: 1.3.6.1.2.1.68.1.3.1.16}  # TruthValue, access=ru, allowed=[True, False]
  vrid_errors: {oid: 1.3.6.1.2.1.68.2.3, method: get}  # Counter32, access=r
  virtual_mac: {oid: 1.3.6.1.2.1.68.1.3.1.2}  # MacAddress, access=r
  primary_ip: {oid: 1.3.6.1.2.1.68.1.3.1.8}  # IpAddress, access=ru
  trap_auth_failure: {oid: 1.3.6.1.4.1.248.12.2.5.2, method: get}  # HmEnabledStatus, access=ru, allowed=[True, False]
  checksum_errors: {oid: 1.3.6.1.2.1.68.2.1, method: get}  # Counter32, access=r
  priority: {oid: 1.3.6.1.4.1.248.12.2.260.2.1.8}  # Integer32, access=ru, range=1–254
  oper_status: {oid: 1.3.6.1.4.1.248.12.2.260.1.1.5}  # INTEGER, access=r
  track_row_status: {oid: 1.3.6.1.4.1.248.12.2.260.1.1.6}  # RowStatus, access=crud
  ip_count: {oid: 1.3.6.1.2.1.68.1.3.1.6}  # Integer32, access=r, range=0–255
  interval: {oid: 1.3.6.1.2.1.68.1.3.1.11}  # Integer32, access=ru, range=1–255
  decrement: {oid: 1.3.6.1.4.1.248.12.2.260.1.1.4}  # Integer32, access=ru, range=1–253
  state: {oid: 1.3.6.1.2.1.68.1.3.1.3}  # INTEGER, access=r
  auth_key: {oid: 1.3.6.1.2.1.68.1.3.1.10}  # OCTET STRING, access=ru, range=0–16
}
```
</details>

### `get_vrrp_stats()`

**Read** | **Protocols:** MOPS, SNMP

```
get_vrrp_stats() -> {
    checksum_errors: 0  // int
    version_errors: 0  // int
    vrid_errors: 0  // int
}
```


<details><summary>MOPS sources (3/3 attrs)</summary>

```
MOPS {
  vrid_errors: {VRRP-MIB / vrrpStatistics.vrrpRouterVrIdErrors}  # Counter32, access=r
  checksum_errors: {VRRP-MIB / vrrpStatistics.vrrpRouterChecksumErrors}  # Counter32, access=r
  version_errors: {VRRP-MIB / vrrpStatistics.vrrpRouterVersionErrors}  # Counter32, access=r
}
```
</details>

<details><summary>SNMP sources (3/3 attrs)</summary>

```
SNMP {
  vrid_errors: {oid: 1.3.6.1.2.1.68.2.3, method: get}  # Counter32, access=r
  checksum_errors: {oid: 1.3.6.1.2.1.68.2.1, method: get}  # Counter32, access=r
  version_errors: {oid: 1.3.6.1.2.1.68.2.2, method: get}  # Counter32, access=r
}
```
</details>

---
