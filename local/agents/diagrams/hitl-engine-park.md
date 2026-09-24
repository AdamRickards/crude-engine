# HITL / Engine park list

Architect-owned. When a leftover needs **Engine HITL**, a **new primitive**,
or Schema/Docs `NO_HOLE` that only Engine can fill: **auto-park here** and
keep soft Schema/Docs/Test proveable hops moving. Do **not** widget-wait
HITL (Jaysue 2026-09-13).

Glance: open rows = parked for human/Engine. Close rows when the primitive
lands or HITL kills the need.

| Parked | Why | Consumers | Soft path meanwhile |
| --- | --- | --- | --- |
| #12 SNMP compound-index / `key_format` (ascii) | Engine primitive — Schema tools exhausted | #231 `community_access` mops ascii vs snmp 0; trap-dest class | Lane B continues; leave #231 open as NO_HOLE consumer |
| TC-BITS (~3) prove-before-flip | Generator teach needs live prove first | #205 residual | Parked — not overnight flip |
| MOPS/SNMP multi-field INDEX / singular `index_field` collapse | Driver `_list_to_dict` / compound INDEX — Schema cannot un-collapse | #68 get_software images; #106 MOPS multi-field INDEX; #12 SNMP compound | Soft hops elsewhere; park Engine |
| SNMP inspect `last_oid` / walk heartbeat | Hang never returns; snmp call-timeout has no last_command (SSH-only today) | #47 get_interfaces snmp fanout (closed) | Schema walk fan-in first; park Engine heartbeat |
| #272 get_interface_statistics | Engine NO_HOLE (accepted 2026-09-13) — `index_filter` only applies on writes, and physical-only read parity needs a read-side filter in Engine. | #272 get_interface_statistics | Next step: park Engine until HITL opens. |
| #62 get_rstp_port | Engine NO_HOLE — `enabled` / `edge` / `priority` / `path_cost` exist only on per-port `show spanning-tree port {port}`; `{index}` is never bound on dict reads, and `iterate_from` fanout hits the HARD call-timeout class. Needs Engine index binding or a fanout budget | #62 get_rstp_port | No honest Schema-only path; park Engine until HITL opens |
| #30 SNMPHIOS.close() asyncio tax | Engine/transport — ~2s close destroys pending tasks | sequential sidecar / concurrent prove noise | Soft floors continue; Engine park until HITL opens |
| #115 `to_bool` English/SNMP false-vocab hardcoded | Checker-blind Engine; schema cannot declare | bool matrices / parity | Soft YAML elsewhere; park Engine |
| #116 `compute sort:natural` HiOS port-name heuristic | Checker-blind Engine encodes vendor sort | port-ordered tables | Soft elsewhere; park Engine |
| #156 Engine/tools debug↔trace conflation (post Docs #262) | Docs wording cleared; code still maps debug→trace / missing --debug / audit_setters debug=True | napalm-hios _call; tools CLI; interpreter schema debug alias; sidecar/release_matrix; audit_setters | Soft Docs done; park Engine/tools until HITL opens |
| Fail-fast / invalid-CLI redefine | Needs HITL eyes on live invalid/missing/bad-attr | was #92 title — **do not reopen #92**; new ticket if poked | Timeout detection done (#179–#225); SSH parse = #226/#227/#228 |
| SSH gather `last_cli` / multi-cmd visibility (ifindex re-gather overwrite) | Engine — last_cli does not retain all shows when overlay multi-cmd gather runs; Schema YAML-only cannot evidence multi-show in cli | #226 get_interfaces Rank1 (mtu/sysinfo fields may populate; cli lists show port only) | Schema soft overlays continue; do not reopen #92 |
| SSH VLAN PortList / `show vlan member` T/U/F | Schema NO_HOLE — per-VLAN `show vlan id` fanout call-timeouts (#290 HARD); invent from PVID ruled out; CLI.json `show vlan member current|static` needs custom T/U/F PortList parser = Engine primitive | #291 get_vlan_egress; #290 Rank2 T/F remainder | Soft PVID Rank1v2 merged (#303); other Σ SSH close-format continue |
| SSH MAC table composite PK / per-row VLAN | Schema NO_HOLE — dict `primary_key: mac` collapses VLAN when MAC repeats; YAML composite PK / `type: list` / `list_append` / fake key_map invent ruled out; 1.17 returns list of rows | #296 get_mac_address_table | Soft Σ SSH close-format continue (#297+) |

| SSH QoS DSCP table key normalize (`key_tag` / `key_regex`) | Schema NO_HOLE — SNMP/MOPS drivers apply `key_tag`; SSH table gather is per-value only. Rank1 tried value_map/key_map/dot_keys/fanout ruled out; Fastpath keys are `N(name)` vs MOPS bare numeric | #318 get_qos_mapping | Soft Σ SSH close-format continue (#319+) |

| SSH get_software images / DevmodeStatus honesty | Schema NO_HOLE — no CLI SwVers table / no honest image wires; invent-wrong Admin state ≠ DevmodeStatus; support-mode has no captured field label. Prefer existing tools exhausted. Related #68 MOPS multi-field INDEX already parked | #322 get_software | Soft Σ SSH close-format continue (#323+) |

| SSH get_config execute-blob gather | Schema NO_HOLE — composed Protocols:None; running/startup honest {}; no MIB wire for `show running-config` / startup. Prefer existing tools exhausted | #324 get_config | Soft Σ SSH no-cli continue (#325+) |

| SSH GARP GVRP/GMRP field-label capture | Schema NO_HOLE — CLI.json names shows but no captured field labels (archive TODO); invent risk without sample. Soft Rank1 exhausted | #327 get_gmrp; #328 get_gvrp | Soft Σ SSH no-cli continue (#329+); HITL/1.17 sample capture when opened |

| SSH get_ip_addresses nested ip_table / composed ipv4 | Schema NO_HOLE — defaults only `ipv4: {}` (no sub_tables) → attr scope empty → cli=[] honest; CLI.json names `show ip interface` (L3) + `show network parms` (L2 fallback) but archive needs `tag: ip_table` / intf→ipv4→ip→prefix_length nest (Engine). Binding management scalars invents NAPALM floor (both empty). Soft Rank1 exhausted | #329 get_ip_addresses | Soft Σ SSH no-cli continue (#330+); Engine ip_table / HITL when opened |

| SSH get_lldp_neighbors(_detail) remote-data sections/block parser | Schema NO_HOLE — CLI.json names `show lldp remote-data` (+ global/port); archive fixture + `local/archive/lldp.yaml` need `parser: sections` (block headers `Remote data, M/N - #port` + dotted field labels). Live `wire/ssh/lldp.yaml` write-only ("reads need block parser"). Live parsers only table/paired_rows/simple_table/regex — cannot multi-section list_append by local_port. Scalar `field:` invents single-record floor. `cli=show port` is ifindex key_map only. Detail = same show + same sections need (more rem fields). Prefer existing tools exhausted. Soft Rank1 exhausted | #333 get_lldp_neighbors; #334 get_lldp_neighbors_detail | Soft Σ SSH fail pack #333–#334 closed; Engine sections/block parser / HITL when opened |

| SSH get_fan_status multi-row `parser: fan_status` | Schema NO_HOLE — CLI.json `show fan`; archive uses Engine `parser: fan_status` (multi-row walk). No scalar field for `hm2fanmgmtstatus`; schema invent floor `defaults.status: running` vs MOPS `{}`. Soft Rank1 exhausted | #332 get_fan_status | Soft Σ SSH fail continue (#333+#334); Engine fan_status / HITL when opened |


## Rules

1. Engine merge still needs HITL sign-off when it invents meaning / new primitive.
2. Soft changes (YAML overlay, floors, docs, harness prove) keep the poke loop.
3. One row per park reason; consumers link in, do not duplicate umbrellas.
4. No lab identity on this page.