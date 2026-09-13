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
| SNMP inspect `last_oid` / walk heartbeat | Hang never returns; snmp call-timeout has no last_command (SSH-only today) | #47 get_interfaces snmp fanout | Schema walk fan-in first; park Engine heartbeat |
| PR #76 `get_optics` (open since 2026-08-29) | Held for napalm-hios v1.17 compare; outside current A/A′/B/C lanes | silent backlog if ignored | HITL: revive compare+prove **or** close/park explicitly |
| #30 SNMPHIOS.close() asyncio tax | Engine/transport — ~2s close destroys pending tasks | sequential sidecar / concurrent prove noise | Soft floors continue; Engine park until HITL opens |
| #115 `to_bool` English/SNMP false-vocab hardcoded | Checker-blind Engine; schema cannot declare | bool matrices / parity | Soft YAML elsewhere; park Engine |
| #116 `compute sort:natural` HiOS port-name heuristic | Checker-blind Engine encodes vendor sort | port-ordered tables | Soft elsewhere; park Engine |
| #156 Engine/tools debug↔trace conflation (post Docs #262) | Docs wording cleared; code still maps debug→trace / missing --debug / audit_setters debug=True | napalm-hios _call; tools CLI; interpreter schema debug alias; sidecar/release_matrix; audit_setters | Soft Docs done; park Engine/tools until HITL opens |
| Fail-fast / invalid-CLI redefine | Needs HITL eyes on live invalid/missing/bad-attr | was #92 title — **do not reopen #92**; new ticket if poked | Timeout detection done (#179–#225); SSH parse = #226/#227/#228 |

## Rules

1. Engine merge still needs HITL sign-off when it invents meaning / new primitive.
2. Soft changes (YAML overlay, floors, docs, harness prove) keep the poke loop.
3. One row per park reason; consumers link in, do not duplicate umbrellas.
4. No lab identity on this page.
