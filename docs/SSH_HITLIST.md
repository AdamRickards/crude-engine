# SSH Wire Hitlist

> Per-schema SSH wire coverage. Each schema's methods share the same attr pool —
> fixing attrs for a schema fixes all its methods (get, set, create, delete).

## Status Key

| Status | Meaning |
|--------|---------|
| FULL | All attrs have SSH sources (read + write where applicable) |
| PARTIAL | Some attrs covered, missing listed |
| EXEMPTED | Missing attrs are in wire_exemptions.yaml or have no CLI equivalent |
| NEEDS_PARSER | CLI data exists but format needs custom SSH driver parser |
| NEEDS_DRIVER | Wire correct but SSH driver can't handle data shape |

---

## FULL — read + write complete (14 schemas)

| Schema | SSH | Methods | Notes |
|--------|-----|---------|-------|
| banner | 2/2 | 2 | show system pre-login-banner + writes |
| config | 6/6 | 6 | show config status/profiles/watchdog + writes |
| dai_global | 3/3 | 2 | show ip arp-inspection global + writes |
| dhcp_snooping | 4/4 | 2 | show ip dhcp-snooping global/interfaces + writes |
| hidiscovery | 4/4 | 2 | show network hidiscovery + writes. relay empty on L2 (defaults handle it) |
| mac | 4/4 | 1 | show mac-addr-table |
| mrp | 15/15 | 4 | show mrp + full CRUD via mrp domain add/modify/delete |
| poe | 3/3 | 2 | show inlinepower port table + writes. Field names from GRS1042 headers |
| route | 5/6 | 1 | show ip route all table. age not in SSH output |
| rstp | 9/9 | 4 | show spanning-tree global + port {index}. Full read+write |
| services | 8/8 | 2 | show http/https/telnet/ssh server. SNMP attrs already wired in mgmtaccess |
| session_config | 3/4 | 2 | show ssh server + show telnet + writes. web_timeout has no show command |
| snmp_information | 3/3 | 2 | show snmp access + writes |
| system | 11/12 | 5 | show system info + system name/location/contact writes. uptime EXEMPTED (needs to_timeticks) |

## EXEMPTED remaining (8 schemas) — effectively done

| Schema | SSH | Methods | Missing (all exempted) |
|--------|-----|---------|----------------------|
| dns | 10/11 | 4 | addr_type |
| ntp | 14/15 | 6 | server_stratum |
| remote_auth | 19/21 | 8 | radius_addr_type, tacacs_addr_type |
| syslog | 9/10 | 4 | addr_type |
| user | 15/18 | 6 | snmp_auth_password, snmp_enc_password, default_password |
| ip_restrict | 14/18 | 4 | logging, addr_type, interface, per_rule_logging |
| profile | 12/13 | 3 | storage_type |
| snmp | 11/19 | 5 | VACM cross-refs (community_security_name, group_name, access) |

## EXEMPTED — no CLI (2 schemas)

| Schema | Methods | Notes |
|--------|---------|-------|
| gmrp | 3 | Requires running-config parsing |
| gvrp | 3 | Requires running-config parsing |

## PARTIAL — reads + writes wired, gaps remain (10 schemas)

| Schema | SSH | Methods | Status | Gaps |
|--------|-----|---------|--------|------|
| devsec | 21/24 | 3 | 19 monitors read+write. state/trap_enabled/history need show device-status state/events |
| interface | 8/43 | 7 | admin_status, alias, cable_crossing, power_state, power_save, flow_control writes added. MAU, tracking, RMON, diagnostic read attrs still missing |
| lldp | 3/17 | 4 | 3 global writes (enabled, tx-interval, tx-hold). Neighbor reads NEEDS_PARSER (block format) |
| management | 4/5 | 4 | ip+gateway+vlan read+write. prefix_length EXEMPTED (CLI uses mask) |
| port_security | 13/19 | 4 | Per-port detail read+write done. Missing: static_macs/ips (list), auto_disable_enabled (cross-wire) |
| router | 3/13 | 6 | show ip interface (ip/mask read). All per-port set commands wired. Detail attrs read-only via MOPS/SNMP |
| sflow | 9/14 | 6 | Sampler+poller read+write. Receiver partial (read only). Missing: receiver_index, max_datagram_size, port, datagram_version |
| software | 4/10 | 2 | Globals read+write (bootcode, secure_boot, dev_mode, allow_unsigned). Image table needs parser |
| vrrp | 17/25 | 11 | Globals+stats+instance table read. Full CRUD+tracking+modify writes. Per-instance detail (master_ip, virtual_mac, uptime, etc.) read via MOPS/SNMP only |
| qos/qos_mapping | 4/8 | 4 | Reads partial. classofservice writes not yet wired |

## PARTIAL — needs investigation (4 schemas)

| Schema | SSH | Methods | Status |
|--------|-----|---------|--------|
| aca | 1/11 | 2 | Needs show config envm commands |
| ipv6 | 3/6 | 2 | ipv6_address, ipv6_state, state missing |
| optics | 1/4 | 1 | tx_power, rx_power, temperature from show sfp |
| protection | 4/9 | 7 | loop_protection + auto_disable commands exist but not yet wired |

## NEEDS_PARSER (3 schemas)

| Schema | Attrs | Methods | Notes |
|--------|-------|---------|-------|
| signal_contact | 18 | 2 | show signal-contact {n} multi-command format |
| system_health | 7 | 5 | show device-status multi-section format |
| vlan (egress) | 3 | 2 | show vlan member current T/U/F/- per-port bitmask |

## NEEDS_DRIVER (1 schema)

| Schema | Attrs | Methods | Notes |
|--------|-------|---------|-------|
| mrp_sub_ring | 13 | 4 | SSH driver can't decompose dot_keys into table shape |

---

## Summary

| Category | Schemas | Methods |
|----------|---------|---------|
| FULL | 14 | 37 |
| EXEMPTED (done) | 10 | 36 |
| PARTIAL (wired) | 10 | 40 |
| PARTIAL (needs investigation) | 4 | 12 |
| NEEDS_PARSER | 3 | 9 |
| NEEDS_DRIVER | 1 | 4 |
| **Total** | **42** | **138** |

> 3 schemas (arp, ip_source_guard, protection) overlap between PARTIAL categories above.
> Method counts approximate — some schemas share methods across categories.
