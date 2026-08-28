# Project Review — Priorities & Perspective

> **Author:** Grok (review session, 2026-07-05)  
> **Scope:** crude-engine 2.9.0 + napalm-hios 2.0.0 (napalm-hios-v2 lineage)  
> **Purpose:** Capture project state and a prioritized work list for PM review. No code changes — analysis only.  
> **Status:** Draft for Adam's review. Not authoritative until adopted into `TODO.md` / `ROADMAP.md`.

---

## Executive summary

The project is **past prototype and in pre-release hardening**. Architecture is settled (v2.9 three-gate model, package split, CRUDE vocabulary, release matrix harness). What blocks first PyPI release is **not** fundamental redesign — it is:

1. **MOPS↔SNMP value parity** (145 failures, overwhelmingly one root cause)
2. **Fleet-scale setter/CRUD matrix execution** (planned but not yet run)
3. **Documentation hygiene** (stale counts, missing curated TODO/ROADMAP)

The NAPALM adapter (`napalm-hios`) is largely complete. The engine is production-ready for **per-protocol reads** (916/916 pass on MOPS and SNMP individually). The release gate fails on **cross-protocol agreement**, not single-protocol correctness.

---

## Where the code lives today

| Package | Path | Version | Role |
|---------|------|---------|------|
| **crude-engine** | `obsidian-vault/Projects/crude-engine/` | 2.9.0 | Engine, drivers, schemas, wire YAMLs |
| **napalm-hios** | `obsidian-vault/Projects/napalm-hios/` | 2.0.0 | Thin NAPALM adapter shim |
| **napalm-hios-v2** (legacy) | `obsidian-vault/Projects/napalm-hios-v2/` | — | Orphaned `tests/` only; history in `Backup/napalm-hios-v2-*.tar.gz` |

---

## Release gate snapshot (2026-04-14)

Source: `docs/RELEASE_MATRIX.md` / `tests/release_matrix.json`

| Verdict | Count |
|---------|-------|
| pass | 1,229 |
| **fail** | **145** (all parity) |
| not_applicable | 162 |
| **Gate** | **FAIL** |

| Kind | Pass | Fail |
|------|------|------|
| read (MOPS + SNMP each) | 916 / 916 | 0 |
| parity (MOPS vs SNMP, same device) | 313 | **145** |

**Key insight:** MOPS alone: 458 pass, 0 fail. SNMP alone: 458 pass, 0 fail. Blockers are **cross-protocol value agreement**, not broken getters on either protocol in isolation.

### Failure buckets (`docs/TODO_HITLIST.md`)

| Tag | Cells | Theme |
|-----|-------|-------|
| `#driver #SNMP-Compound-Index-Decode` | ~139 | SNMP walk keys (OID suffix) don't align with MOPS `index_field` keys; multi-table getters can't join rows |
| `#wire #NTP-Server-Enabled-Mismatch` | 6 | `get_ntp.server_enabled` disagrees MOPS vs SNMP |

---

## Architectural perspective (what's working)

### Core thesis — consistently enforced

> **Wire is generated. Schema is authored. Adapter is per-consumer. YAML declares, Python executes.**

### Major wins since March 2026 audit

| Area | Was | Now |
|------|-----|-----|
| NAPALM shapes in engine (Rule 6) | `_shape_*` in `interpreter.py` | **Fixed** — all reshaping in `napalm-hios/hios.py` |
| Adapter protocol branching (Rule 5) | `if active_protocol == 'snmp'` | **Fixed** — registry-driven, protocol-free adapter |
| Schema canonical keys | NAPALM-shaped defaults | **Fixed** — `oper_status`, `sys_name`, `status` etc. |
| Impure transforms (Rule 3) | `transforms.py` + pysnmp objects | **Fixed** — `crude.py` on bytes/str |
| YAML logic blobs (Rule 4) | 708 hits in old `features/*.yaml` | **Reduced** — handful of declared `compute.expr` / `lookup.resolve` |
| Package structure | Monolithic napalm-hios-v2 | **Split** — crude-engine (product) + napalm-hios (shim) |

### Context maps (ifindex) — correct design, not a violation

Declared in `engine/context_maps.yaml`. Engine resolves lazily via `_resolve_context_map()` through Gate 2 → Gate 3. v2.9 batches context-map gathers into getter round-trips. **Necessary and YAML-driven.**

Transport/offline encoding translation (XML port names ↔ SNMP ifIndex, hex portlists) is **legitimate transport-boundary work**, not adapter/engine leakage.

### Dead code note

`mops_transport._get_with_ifindex()` is **defined but never called** — pre-v2.9 leftover superseded by context maps. Cleanup candidate, not an active architecture problem.

---

## Priority list

Priorities are ordered by **release leverage** (how many gate cells one fix unlocks) and **risk** (what breaks if wrong). Tags use the project's `#bucket #id` scheme where applicable.

---

### P0 — Release blockers

#### P0.1 — SNMP compound index key alignment

| | |
|---|---|
| **Tag** | `#driver #SNMP-Compound-Index-Decode` |
| **Impact** | ~139 of 145 parity failures |
| **Symptom** | Multi-table getters return correct shape on each protocol but different values/keys when compared |
| **Affected methods** | `get_interfaces`, `get_mac_address_table`, `get_lldp_neighbors*`, `get_vlans`, `get_mrp`, sFlow tables, `get_ipv6_neighbors*`, `get_route_to`, and others |
| **Likely root cause** | SNMP walk produces raw OID suffix keys; MOPS produces `index_field`-keyed rows. Row join / `index_fields` / lookup correlation fails |
| **Engine smell** | `interpreter.py` lookup suffix fallback (`wk.endswith(lookup_value)`) — data sniffing instead of declared key alignment |
| **Fix layer** | Driver + schema `index_fields` declarations first. Engine suffix fallback is a band-aid, not the fix |
| **Diagnostic** | `release_matrix.py --inspect --method <failing> --device <device> --trace` |
| **Doc** | `docs/DIAGNOSTIC_PROCESS.md` — compare to passing sibling (e.g. `get_arp_table`) |

**Why P0:** Single highest-leverage item. Per-protocol reads are already green; this is the gate.

#### P0.2 — NTP server_enabled wire mismatch

| | |
|---|---|
| **Tag** | `#wire #NTP-Server-Enabled-Mismatch` |
| **Impact** | 6 parity cells, all devices |
| **Symptom** | `get_ntp.server_enabled` differs MOPS vs SNMP |
| **Fix layer** | Wire or schema — isolated, good second target after index decode |
| **Diagnostic** | `--inspect --method get_ntp --trace` on one lab device |

#### P0.3 — Run setter + CRUD matrix on lab fleet

| | |
|---|---|
| **Tag** | `#release #Setter-Matrix` / `#release #Crud-Matrix` |
| **Impact** | 260 planned jobs (200 setter, 60 crud) not executed in latest matrix run |
| **Current proof** | CHANGELOG: 43/43 setter round-trips, 11/11 CRUD lifecycle on live devices — but not fleet-scale matrix |
| **Devices** | `192.168.60.80`–`.85` (lab, `safe_for: setter,crud`) |
| **Command** | `release_matrix.py --execute --kind setter` then `--kind crud` per `RELEASE_GATE.md` |
| **Why P0** | Read path green ≠ write path proven at release scope |

---

### P1 — Pre-release hygiene (low effort, high clarity)

#### P1.1 — Regenerate curated `TODO.md` and `ROADMAP.md`

| | |
|---|---|
| **Source** | `docs/TODO_HITLIST.md` (auto-generated failures) |
| **Process** | `RELEASE_GATE.md` — curate hitlist into `TODO.md`; post-release scope into `ROADMAP.md` |
| **Why** | Archived leftover Claude (`local/archive/docs-legacy/claude/CLAUDE.md`) explicitly marks old `TODO-old.md` as untrusted; curated lists don't exist yet |

#### P1.2 — Sync method/schema counts across docs

| | |
|---|---|
| **Drift** | README says 184 methods; `METHOD_REFERENCE.md` says 186; `API_REFERENCE.md` says 174; archived leftover Claude (`local/archive/docs-legacy/claude/CLAUDE.md`) says 43 schemas, repo has 45 |
| **Fix** | Regenerate from `local/generator/generate_docs.py` or matrix tool output |
| **Why** | Onboarding confusion; undermines "truth from execution" principle |

#### P1.3 — Update `SCHEMA_MODEL.md` reshaping hitlist

| | |
|---|---|
| **Stale** | Lists `interface`, `lldp`, `mac` as NAPALM-shaped — schemas are now canonical |
| **Still valid** | `vlan.yaml` `ports` compute builds NAPALM `U/T/F` dict in schema (see P2.2) |

#### P1.4 — Remove dead transport code

| | |
|---|---|
| **Target** | `mops_transport._get_with_ifindex()` — unused since v2.9 context maps |
| **Why** | Prevents future confusion during audits (as happened in this review) |

---

### P2 — Principle alignment (post-gate or parallel if quick)

#### P2.1 — Replace lookup suffix fallback with declared primitive

| | |
|---|---|
| **Location** | `interpreter.py` `_apply_lookup` suffix match |
| **Principle** | `DIAGNOSTIC_PROCESS.md` — never sniff data; schema missing a declaration |
| **Relation to P0.1** | May be the same fix viewed from engine side |
| **Risk** | Removing fallback without fixing index decode could expose more failures temporarily |

#### P2.2 — Move `vlan.ports` U/T/F compute to adapter

| | |
|---|---|
| **Location** | `schemas/vlan.yaml` compute expr |
| **Principle** | `SCHEMA_MODEL.md` Rule 3 — no consumer-specific value derivation in schema |
| **Target** | Canonical: separate `egress_ports`, `untagged_ports`, `forbidden_ports` lists; adapter merges to NAPALM `ports` dict |
| **Note** | `get_vlans()` in `hios.py` currently passes through with no reshaper |

#### P2.3 — Decouple crude-engine from NAPALM exceptions

| | |
|---|---|
| **Location** | `snmp_transport.py`, `mops_transport.py`, `ssh_transport.py`, `mops_client.py` import `napalm.base.exceptions.ConnectionException` |
| **Principle** | crude-engine is consumer-agnostic |
| **Fix** | Engine-native exception hierarchy; adapter maps to NAPALM if needed |
| **Priority** | Can wait until post-PyPI unless publish tooling requires clean deps |

#### P2.4 — Eliminate silent exception swallowing

| | |
|---|---|
| **Locations** | `hios.py` `_fetch_device_info` (`except Exception: pass`); `interpreter.py` `get_capabilities` (`except FileNotFoundError: pass`); compute expr failures log-and-continue |
| **Principle** | `ENGINE_PRINCIPLES.md` Invariant 5 — each block has one failure mode |
| **Fix** | Log at warning minimum; empty device_info should be explicit, not silent |

#### P2.5 — Document `get_capabilities` Gate 2 exemption

| | |
|---|---|
| **Location** | `interpreter.py` `load_wire()` outside `_gate2_resolve` |
| **Fix** | One line in `ARCHITECTURE.md` — infrastructure discovery is an allowed exception |
| **Priority** | Low; principle hygiene only |

---

### P3 — Post-release (explicitly out of gate)

| Item | Notes |
|------|-------|
| SSH first-class parity | ~65% per session notes; `SSH_HITLIST.md` untrusted until matrix re-verifies |
| HiSecOS / multi-OS wire YAMLs | Not started |
| gNMI adapter | Planned v3.1 |
| Modbus transport | Planned |
| `local/` generator restore | Wire regen not runnable in vault copy; manual wire fixes risk generator drift |
| Execute methods matrix | 0 execute jobs in current plan |
| PyPI publish | Target ~v2.10.0; blocked on P0 |

---

## Principle violations — corrected perspective

From review session + Adam's clarification on transport vs engine terminology.

### Not violations (or resolved)

| Item | Verdict |
|------|---------|
| Context maps / ifindex | **Correct design** — YAML-declared, engine-resolved |
| `offline_client` encoding (`convert: portlist`, `ifname`) | **Legitimate transport work** — XML↔MOPS format translation |
| `snmp_transport._normalize()` | **Intentional** — pysnmp→hex-spaced bytes for MOPS/SNMP wire parity |
| NAPALM reshaping in `hios.py` | **Correct layer** |
| Canonical schema keys (`oper_status`, `sys_name`, `status`) | **Fixed** |

### Still worth addressing

| Item | Layer | Severity |
|------|-------|----------|
| SNMP compound index decode | Driver/schema | **Critical** (P0.1) |
| Lookup suffix fallback | Engine | **High** (P2.1, tied to P0.1) |
| `vlan.ports` U/T/F in schema | Schema | **Medium** (P2.2) |
| NAPALM `ConnectionException` in engine | Transport | **Low** (P2.3) |
| Silent `except: pass` | Adapter/engine | **Low** (P2.4) |
| Dead `_get_with_ifindex` | Transport | **Cleanup** (P1.4) |

### Gray areas (intentional tensions)

| Item | Notes |
|------|-------|
| `compute.expr` / `lookup.resolve` with `if/else` | Declared primitives per `SCHEMA_PRIMITIVES.md`; evolved from strict Rule 4 |
| `base._apply_math` / driver pipeline | YAML-driven driver transforms; conflicts with strictest "CRUDE only" reading of `DIAGNOSTIC_PROCESS.md` but works in practice |
| `snmp_driver._format_index_value` | RFC 2578 INDEX formatting in driver — borderline but aligned with `RFC_MAPPING.md` |

---

## Suggested execution order

```
Phase A — Unlock the gate (1–2 focused sessions)
  P0.1  SNMP compound index decode (inspect → fix driver/schema → re-run parity)
  P0.2  NTP server_enabled mismatch
  Re-run: release_matrix.py --execute --kind parity --render

Phase B — Prove write path (1 session, lab devices)
  P0.3  Setter + CRUD matrix on .80–.85
  Re-run: release_matrix.py --render

Phase C — Ship hygiene (half session)
  P1.1  Curate TODO.md + ROADMAP.md from hitlist
  P1.2  Sync doc counts
  P1.3  Update SCHEMA_MODEL hitlist
  P1.4  Remove dead _get_with_ifindex

Phase D — Principle cleanup (optional pre- or post-PyPI)
  P2.1–P2.5 as bandwidth allows

Phase E — Post-release
  P3 items per ROADMAP
```

---

## What I would *not* prioritize

| Temptation | Why defer |
|------------|-----------|
| Interpreter size reduction (~2,325 lines) | v2.9 decomposition is done; works; P0 fixes matter more |
| SSH parity | Explicitly post-release per `RELEASE_GATE.md` |
| Rewriting `compute.expr` to remove all `if/else` | Declared primitive; 3 instances, not 708 |
| Moving `snmp_transport._normalize` to crude.py | Intentional wire-layer normalization; changing it risks re-breaking parity |
| Fundamental architecture redesign | Not warranted — gate failures are correctness, not design |

---

## Open questions for Adam

1. **Release version:** Ship as crude-engine 2.10.0 or reset to 1.0.0 for first PyPI? (`RELEASE_GATE.md` notes either is fine.)
2. **Parity strictness:** Any accepted diffs beyond current exemptions? (`tests/wire_exemptions.yaml`, `tests/method_exemptions.yaml`)
3. **vlan.ports:** Keep NAPALM-shaped canonical output for convenience, or refactor to list-based canonical + adapter reshape before PyPI?
4. **Generator `local/`:** Where does the canonical copy live? Vault copy appears incomplete for wire regen.
5. **Setter matrix scope:** All 200 planned jobs, or phased by schema risk (CLAMPS-wrapped MRP first)?

---

## Reference documents

| Doc | Role |
|-----|------|
| `docs/RELEASE_GATE.md` | Release process authority |
| `docs/RELEASE_MATRIX.md` | Auto-generated scoreboard |
| `docs/TODO_HITLIST.md` | Auto-generated failure queue |
| `docs/ENGINE_PRINCIPLES.md` | Block ownership rules |
| `docs/ARCHITECTURE.md` | Three-gate model |
| `docs/DIAGNOSTIC_PROCESS.md` | Fix ladder |
| `docs/SCHEMA_MODEL.md` | Canonical contract |
| `AGENTS.md` | Standing law (only root agent law) |
| `local/archive/docs-legacy/claude/CLAUDE.md` | Leftover Claude session context (archived, not law) |
| `../CRUDE_AUDIT_REPORT.md` | March 2026 audit (partially superseded by v2.9) |
| `../hios_comparison_report.md` | v1 vs v2 architecture |
| `../FINITE_MATRIX_ACTION_PLAN.md` | Eviction plan (largely executed) |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-05 | Initial draft from Grok review session (architecture review + principles audit + Adam clarifications on transport/context maps) |