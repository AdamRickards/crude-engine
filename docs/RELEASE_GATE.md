# RELEASE_GATE.md

> Process doc. Survives context loss. Read this first when resuming release work.
> Archive to `local/archive/` once the release ships.

## Why this doc exists

We are preparing crude-engine for its first real release. The work plan, the matrix tool design, the cross-reference scheme, and the exit criteria all live here so a fresh session can pick up without re-deriving the plan from archived leftover Claude (`local/archive/docs-legacy/claude/CLAUDE.md`) and stale TODO files.

The old `docs/TODO.md` and `docs/ROADMAP.md` have been renamed to `TODO-old.md` and `ROADMAP-old.md`. **They are not trusted.** Anything in them is a hint, not a fact. New `TODO.md` and `ROADMAP.md` will be generated from matrix tool output and reviewed by the user.

## Phase 0 status (2026-04-14): COMPLETE

The matrix tool is built, validated, and produces real signal. Phase 0 exit criteria all met:

- `tests/release_matrix.py` runs end-to-end (gather → plan → execute → derive → render)
- `tests/audit_common.py` provides `gather_device()` and `load_all_method_metadata()`
- `tests/safety_runner.py` + `tests/safety_protocols.yaml` provide CLAMPS-style pre/post hooks
- `tests/device_pool.yaml` describes the fleet (capability vocabulary auto-validates against schemas)
- `tests/release_matrix.json` is the central DB (lock+backoff hierarchical writes)
- `docs/RELEASE_MATRIX.md` and `docs/TODO_HITLIST.md` are auto-generated from the DB

**Validated against the live fleet:**
- Read sweep: **916/916 PASS** across 7 devices × 2 protocols (mops + snmp)
- Tiny setter validation: **4/4 PASS** on `set_banner` / `.85` (banner_text + banner_enabled, both protocols)
- Comms-loss handling: wired but not yet exercised against a real failure
- Auto-derive of `has_configured_from_gather`: produces accurate per-device feature lists from live read data

**Implementation has diverged from the initial design in several meaningful ways:**

1. **Auto-derived `has_configured`** — the static pool entry is a bootstrap hint only. After every read sweep, `release_matrix.py` derives `has_configured_from_gather` from the matrix DB cells (where verdict=pass and the read returned non-default data) and writes it into `tests/device_state.json`. The resolver unions both sources, so live truth wins. The pool's `has_configured` field can shrink/disappear over time.

2. **Structural `_is_configured` heuristic** — uses the schema's `sub_tables` and `primary_key` declarations, NOT comparison against schema defaults (those are for type validation, not state detection). The check is:
   - sub-tabled schemas → configured iff any sub-table dict has rows (ignoring the `globals` wrapper)
   - primary-key tables → configured iff top-level dict has rows
   - flat globals → configured iff non-empty (imperfect; per-method overrides via `tests/configured_probes.yaml` is a follow-up)

3. **Cell key for setter/CRUD uses `test_id`** at the second level, not the canonical method name. Multiple tests can share the same setter method (e.g., `banner_text` and `banner_enabled` both call `set_banner`); using test_id keeps them uniquely addressable. Reads stay keyed by method name (1:1).

4. **`--kind` filter** for surgical execution. `release_matrix.py --execute --kind read` runs only read jobs without dispatching setter/CRUD jobs in the plan.

5. **`last_execute` meta** in the matrix DB — records the scope of the most recent execute run (kind/method/schema/device/protocol filters). The renderer uses it to scope the `not_run` count correctly: jobs filtered out by `--kind read` are NOT counted as "missing," they're "out of this run's scope."

6. **Resolver relaxation for reads** — reads use `has_capable`, not `has_configured`. Lets reads run on every device that supports the feature even if no data is configured yet. Vacuous passes are accepted because the contract+type checks still fire on whatever the method returns. The gather-derived `has_configured_from_gather` then feeds the setter/crud resolver with TRUE configured state.

7. **Perf renderer section** — the matrix tool already records `time_ms` per cell. The renderer now computes per-(method, protocol) averages, SNMP/MOPS ratios, and per-device totals into a `## Perf` section in `RELEASE_MATRIX.md`. Surfaces multi-request anomalies (e.g., `get_mrp` on SNMP at ~88× MOPS time, indicating an N+1 round-trip pattern).

8. **`audit_common.py`** is the shared utility module for test scripts (gather + method metadata loader). NOT a `crude_tools_common` cross-project library — that was an earlier framing the user explicitly rejected.

9. **Cross-protocol parity is per-row, per-field — NOT count-only.** `_compute_parity` recursively descends into table rows and sub_tables, comparing every non-timing scalar field across protocols. Tolerant equality (True == 1, "1" == 1). Caps output at 25 diffs per (method, device, protocol-pair) to keep cells small. The original count-only check was silently passing methods like `get_interfaces` where MOPS and SNMP returned 13 rows each but with disagreeing `autoneg_enabled` values inside. Real value parity caught at least 6 hidden-bug methods that count-only missed: `get_interfaces`, `get_signal_contact`, `get_software`, `get_qos_mapping`, `get_optics` (false positive — added rx_power/tx_power to TIMING_FIELDS), `get_ntp.server_enabled`. **The parity check now does what its name implies.**

10. **Method exemption render-time override** — `tests/method_exemptions.yaml` declares known firmware-limit gaps (e.g., `.85` BRS50 L2S has no LDAP MIB, no DHCP-snooping MIB). The renderer matches cell verdicts against exemption patterns at render time and reclassifies `fail`/`error` → `exempt` with the documented reason. Underlying matrix DB cells unchanged (audit trail preserved); summary counts and gate verdict reflect the override. Plan-time exemption is a follow-up — currently the device still gets the failing call attempted, just gets reclassified at render.

11. **`--inspect` investigation mode** — single CLI for fault-finding. Runs ONE method on ONE device across every supported protocol (or just one), dumps raw output side-by-side, runs the parity check, captures pipeline trace if `--trace`, bypasses validation if `--no-validate`. Always uses `napalm_compat=False`. Never writes to the matrix DB. **Use this instead of throwaway Python scripts** — the strong rule documented in `tests/README_TESTS.md` and `AGENTS.md`. Future sessions diagnosing parity failures or wire bugs reach for `release_matrix.py --inspect --method X --device Y --trace` first, write code never. The investigation surface is now a first-class, persistent, documented part of the harness.

## How --inspect changes diagnostic workflow

Before (pattern I kept falling into this session):
1. Open Python REPL or write a tmp script
2. Import napalm, get_network_driver, open device
3. Call method, print output
4. Compare protocols by hand or with another script
5. Lose all of the above when the file is deleted

After:
1. `release_matrix.py --inspect --method X --device Y --trace`
2. Done

The harness owns the wiring, the credentials, the protocol enumeration, the parity comparison, and the trace capture. A future session diagnosing the same class of bug uses the same command. Investigation knowledge accumulates in the harness, not in tmp/.

## Findings catalogue (early signal from the matrix tool)

These would land in `docs/TODO_HITLIST.md` once curated. Capturing them here so they survive context loss:

### From the value-parity check (added later in session)

- **`#driver #SNMP-Compound-Index-Decode`** — broadest finding. Affects ~22+ table methods with compound MIB indexes (e.g. `dot1qFdbId+dot1qTpFdbAddress`, `lldpRemPort+lldpRemIndex`, `inetCidrRouteNextHop`, etc.). MOPS keys its walked dict by one column from the row (via wire `index_field`); SNMP walks return raw OID suffix as key. The two key formats don't match → engine's row-builder can't cross-reference → SNMP-side rows look empty even though the underlying walks returned data. Methods affected include: `get_mac_address_table`, `get_vlans`, `get_vlan_egress`, `get_arp_table`, `get_lldp_neighbors*`, `get_ipv6_neighbors*`, `get_route_to`, `get_qos_mapping`, `get_aca`, `get_devsec_history`, `get_mrp`, `get_mrp_sub_ring`, `get_sflow_*`, `get_users`, `get_signal_contact`, `get_software`, and **silently `get_interfaces.autoneg_enabled`/`autoneg_supported`/`media_type`/`manual_config`** (compound-indexed attrs from MAU-MIB inside an otherwise-passing method)
- **`#driver #SNMP-Implied-String-Index`** — pysnmp `NoSuchObjectError` for SNMP CRUD on string-indexed tables (`snmp_trap`, `user`, `static_binding`). 9 cells. Distinct from the compound-index-decode bug.
- **`#wire #Facts-Uptime-Units`** — `get_facts.uptime` returns ~100× the real value (likely SNMP TimeTicks not divided by 100). Single attribute, but visible across every device.
- **`#driver #SNMP-get_mrp-N+1`** / **`#driver #SNMP-get_snmp_config-Cascade`** — perf outliers (88× and 26× MOPS time respectively). Likely related to the compound-index decode issue but possibly distinct.
- **`#driver #SNMP-Multi-Request-Pattern`** — 8 methods exhibit > 5× SNMP/MOPS ratio (`get_ip_restrict`, `get_signal_contact`, `get_lldp_neighbors_detail*`, `get_mrp_sub_ring`, `get_vrrp_instances`). Single root-cause investigation worth doing.
- **`#wire #TACACS-CRUD-NoCreation`** — TACACS CRUD `noCreation` errors on every device, both protocols. 6 cells. Likely RowStatus lifecycle issue.
- **`#wire #User-CRUD-NoCreation`** — User CRUD `noCreation` on MOPS path. 3 cells. Distinct from the SNMP implied-string bug for users (which is in #driver #SNMP-Implied-String-Index).
- **`#wire #DNS-CRUD-Mixed`** — DNS CRUD has different failure modes per device: `noSuchName` on `.85` (probably a different MIB issue) and `noCreation` on `.80`/`.83` (RowStatus lifecycle).
- **`#schema #IP-Source-Guard-Port-Field-Mismatch`** — 2 cells. set returns enabled=True but verify GET returns None — setter and getter probably reading/writing different field names.
- **`#driver #SNMP-PortSec-WrongType`** / **`#driver #SNMP-LLDP-NoCreation`** — 5 setter cells. SNMP-side encoding bugs.
- **`#firmware #L2S-No-LDAP`** / **`#firmware #L2S-No-DHCP-Snooping`** — already handled via `tests/method_exemptions.yaml`. .85 BRS50 L2S firmware doesn't ship the LDAP or DHCP-snooping MIB modules. Reclassified `fail` → `exempt` at render time.

### Test-infrastructure gaps (matrix tool itself)

- **`#test #Setter-Coverage-Gaps`** — `test_setter_pairs.TESTS` (43 tests) and `test_crud_pairs.TESTS` (11 tests) are far short of full schema coverage (68 upsert + 16 create + 16 delete methods). Notable missing: `set_mrp`, `set_rstp`, `mrp` CRUD, `vrrp` CRUD.
- **`#test #L2A-Sibling-Coverage`** — the resolver's "best device per (sw_level, protocol)" picker always lands on `.80` for L2A, so `.81` and `.82` get zero setter/CRUD jobs. Round-robin or sw_level+device-class would give better coverage.
- **`#test #Configured-Probes-Override`** — sidecar YAML for per-method "is this configured" overrides. The structural `_is_configured` heuristic uses sub_tables/primary_key but has no way to handle flat-global schemas where "configured" means something specific (e.g., text != "" for banner).
- **`#test #Perf-Multiplier-Aware`** — compute expected SNMP/MOPS multipliers per method by scanning wire YAMLs for `lookup:`/`key_map:`/`linked_tables:` declarations. Anomaly = `actual_ratio > expected × tolerance`.

### Fixed during this session (history, not action items)

- **`#engine #Cell-Key-Test-Collision`** — setter/CRUD cells were addressed by canonical method name, causing collisions when multiple tests shared a method (`banner_text` + `banner_enabled` both → `set_banner`). Fixed: cell key uses test_id at level 2.
- **`#engine #Cell-Key-Test-Collision-Followup`** — `_summarize`'s `not_run` check was looking up cells by method name (mismatching the new test_id keying), causing all CRUD cells to count as "missing" in the gate verdict. Fixed: use the same `_cell_key_for_job` helper.
- **`#test #Parity-Check-Shallow`** — original `_compute_parity` only compared row counts for tables, missing all per-row value disagreements. Fixed: recursive per-field comparison with tolerant equality and timing-field exclusion. Surfaced 6 previously-hidden bug methods.
- **`#test #Investigation-Throwaway-Scripts`** — was: every parity diff investigation required writing a one-shot Python script that called `device.get_*()` and dumped output. Lost work, inconsistent invocations, easy to make mistakes. Fixed: `--inspect` flag + `--trace` + `--no-validate`, documented in tests/README_TESTS.md and AGENTS.md as the **strong rule**: never write throwaway scripts, use `--inspect`.

## Release gate definition

**1st-class citizens for this release:** MOPS + SNMP, consumed via the `napalm-hios` adapter.
**Post-release citizens:** SSH, OFFLINE.

Caveat: OFFLINE may already qualify as a 1st-class citizen — we just have not tested it. The Phase 3 OFFLINE verdict run will decide. If it passes a real test, it moves into the release scope. Otherwise its work moves to `ROADMAP.md`.

The release gate is **not** "every method works on every protocol." It is:

> Every method has a verified verdict on MOPS and SNMP. Verified means executed by the matrix tool against live devices, not claimed by a doc.

A verdict is one of:

| Verdict | Meaning |
|---|---|
| `pass` | Live execution succeeded, contract+type checks passed, parity (where applicable) passed |
| `fail` | Live execution failed or returned wrong shape — must fix before release |
| `exempt` | Documented reason in `tests/wire_exemptions.yaml` or equivalent — accepted gap |
| `not_applicable` | Method requires a feature/firmware/L3 that the test device doesn't have — not a failure |
| `not_run` | Skipped this pass — must be `pass`/`exempt`/`not_applicable` for any cell to count toward gate |

**Truth comes from execution.** Documented PASS means nothing until the matrix tool re-runs it.

## Cross-reference tag scheme

> Replaces file pointers between TODO and ROADMAP. Grep-recoverable. Dangling tags are obvious.

**Format:** `#<bucket> #<short-id>`

**Buckets:**

| Tag | Meaning |
|---|---|
| `#engine` | Work in `crude_engine/engine/` (interpreter, gates, dispatch) |
| `#schema` | Work in `crude_engine/schemas/` (a feature YAML) |
| `#wire` | Work in `crude_engine/wire/` (wire YAMLs, includes SSH overlays) |
| `#driver` | Work in `crude_engine/drivers/` (transport/driver/parsers) |
| `#crude` | Work in `crude_engine/engine/crude.py` or `crude_matrix.yaml` |
| `#test` | Work in `tests/` (test scripts, fixtures, exemption lists) |
| `#release` | Work that is part of the v2.10 release scope (or whatever the number ends up as) |
| `#roadmap` | Post-release work, lives in ROADMAP.md only |

**ID rules:** kebab-case, descriptive, stable forever once written. Examples:
- `#VRRP-MOPS-Compound`
- `#SSH-LLDP-Parser`
- `#Modbus-Transport`
- `#Offline-1st-Class`
- `#Generator-INDEX-Inference`

**Entries always have at least two tags:** one bucket + one ID. They may have multiple buckets if the work spans layers (e.g., `#engine #driver #VRRP-MOPS-Compound`).

**TODO.md entry shape:**
```
- [ ] #engine #VRRP-MOPS-Compound — MOPS row decomposition gap on compound indexes
      Blocks: get_vrrp_instances parity, vrrp CRUD on .83
      Verified: not yet (Phase 1 matrix run pending)
      See ROADMAP if rolled forward.
```

**ROADMAP.md entry shape:**
```
## #roadmap #SSH-1st-Class
Goal: SSH joins MOPS+SNMP as a 1st-class citizen.
Sub-items:
- #driver #SSH-LLDP-Parser
- #driver #SSH-PortList-Parser
- #driver #SSH-MRP-SubRing-Decompose
- #driver #SSH-System-Health-Parser
- #driver #SSH-Signal-Contact-Parser
- #wire #SSH-Partial-Coverage  (the 10 PARTIAL schemas in old SSH_HITLIST)
Exit: matrix tool reports SSH `pass` for all methods that have CLI equivalents,
      `exempt` for the rest with reasons in wire_exemptions.yaml.
```

**Cleanup discipline:**
- A tag should appear in TODO.md OR ROADMAP.md, never both at the same time.
- When work ships from TODO → CHANGELOG, grep the tag across `docs/`. Any other hit is dangling and must be cleaned up.
- `grep -r '#VRRP-MOPS-Compound' docs/` should return zero lines once shipped.
- Tags inside CHANGELOG.md are OK as historical record — they're prefixed with the version.

## Matrix tool — `tests/release_matrix.py`

### Architecture

Five components, each one job. Designed so the tool can run surgically (one cell, one device, one protocol) AND at full scale (whole fleet in parallel) with the same code path.

```
                        ┌─────────────────────────┐
                        │  device_pool.yaml       │  static, capability-tagged
                        │  (1) Device pool        │
                        └────────────┬────────────┘
                                     │
                        ┌────────────▼────────────┐
                        │  (2) Gather phase       │  short live pass per device
                        │      - facts            │  to discover unused ports,
                        │      - lldp neighbors   │  ring members, configured
                        │      - mrp / ring       │  features, etc.
                        │      - interfaces       │
                        │  → device_state.json    │
                        └────────────┬────────────┘
                                     │
                        ┌────────────▼────────────┐
                        │  (3) Test plan          │  pure function, no I/O
                        │      generator          │  enumerates schema × method
                        │  → release_test_plan    │  × protocol × matched device
                        │      .json              │  with `requires` resolution
                        └────────────┬────────────┘
                                     │
                        ┌────────────▼────────────┐
                        │  (4) Resolver           │  assigns each job to one
                        │      device-pool match  │  device based on requires
                        │  → per-device queues    │  / has / has_not / safe_for
                        └────────────┬────────────┘
                                     │
              ┌──────────┬───────────┼───────────┬──────────┐
              ▼          ▼           ▼           ▼          ▼
          Worker      Worker      Worker      Worker      Worker
          (.4)        (.80)       (.83)       (.85)       (.254)
          opens       opens       opens       opens       opens
          device      device      device      device      device
          once        once        once        once        once
              │          │           │           │          │
              └──────────┴────┬──────┴───────────┴──────────┘
                              ▼
                  release_matrix.json  (per-worker shards
                                        merged at end → no locks)
                              │
                  ┌───────────▼───────────┐
                  │  (5) Orchestrator     │  CLI, gate verdict, doc render
                  │      release_matrix   │
                  │      .py              │
                  └───────────────────────┘
```

The `run_one_read` / `run_one_setter` / `run_one_crud` callables added to the existing test scripts ARE the worker call surface. One job in, one cell dict out, append to JSON. Same unit of work whether you call it surgically from CLI or from inside a worker.

### Component 1: Device pool — `tests/device_pool.yaml`

Declarative, capability-tagged. The tool never hardcodes IPs.

```yaml
devices:
  - ip: 192.168.1.4
    label: BRS50-Office-Prod
    sw_level: L2A
    has_capable:    [mac, lldp, snmp, sflow, mops, ssh, vlan, rstp, mrp,
                     dns, ntp, syslog, banner, user, hidiscovery]
    has_configured: [mac, lldp, vlan, dns, ntp, syslog, user]
    safe_for: [read]
    notes: "Office production. READ ONLY. Never set. Never CRUD."

  - ip: 192.168.1.254
    label: GRS1042-Office-Prod
    sw_level: L3A
    has_capable:    [mac, lldp, snmp, mops, ssh, vlan, rstp, ipv6, route, vrrp,
                     dns, ntp, syslog, banner, user, hidiscovery]
    has_configured: [mac, lldp, vlan, ipv6, route, dns, ntp, syslog, user]
    safe_for: [read]
    notes: "L3 office prod. READ ONLY."

  - ip: 192.168.60.80
    label: BRS50-RM-Lab
    sw_level: L2A
    has_capable:    [mac, lldp, snmp, sflow, mops, ssh, vlan, rstp, mrp,
                     dns, ntp, syslog, banner, user, hidiscovery, port_security,
                     dhcp_snooping, dai_global, ip_source_guard, storm_control]
    has_configured: [mac, lldp, vlan, mrp, dns, ntp, syslog, user]
    safe_for: [read, setter, crud]
    notes: "Ring master. CRUD/MRP/RSTP target. Don't break the ring."

  - ip: 192.168.60.83
    label: GRS105-L3A-Lab
    sw_level: L3A
    has_capable:    [mac, lldp, snmp, mops, ssh, vlan, rstp, ipv6, route, vrrp,
                     dns, ntp, syslog, banner, user]
    has_configured: [mac, lldp, vlan, dns, ntp, syslog, user]
    safe_for: [read, setter, crud, sacrificial]
    notes: "L3 lab. VRRP CRUD lives here. Sacrificial."

  - ip: 192.168.60.85
    label: BRS50-L2S-Lab
    sw_level: L2S
    has_capable:    [mac, lldp, snmp, mops, ssh, vlan, rstp,
                     dns, ntp, syslog, banner, user, hidiscovery]
    has_configured: [mac, lldp, vlan, dns, ntp, syslog, user]
    safe_for: [read, setter, crud, sacrificial]
    notes: "Sacrificial setter target. Wipe-and-restore safe."
```

| Field | Meaning |
|---|---|
| `has_capable` | Feature IDs the device supports (firmware/hardware allows it). Tags are schema filenames without `.yaml` |
| `has_configured` | Feature IDs that are currently active on the device. Subset of `has_capable` |
| `safe_for` | What kinds of work are allowed. `read` is always safe; `setter`/`crud` need lab devices; `sacrificial` lets the resolver pick this device when there's any chance of damage |
| `notes` | Free text for humans |

**Capability vocabulary = schema filenames.** Every entry in `has_capable` / `has_configured` must match a `crude_engine/schemas/<id>.yaml`. The plan generator validates this on load. This means the vocabulary is automatically discovered, never hardcoded, and grows naturally as new schemas are added.

**Initial maintenance:** static — user maintains `has_configured` by hand. **v2 enhancement (post-release):** the gather phase auto-refreshes `has_configured` by reading from the device.

### Component 2: Gather phase — `device_state.json`

Short read pass against each device. Discovers state that informs job assignment but isn't static enough for `device_pool.yaml`. Runs once per orchestrator invocation.

What it captures per device:

```json
{
  "192.168.60.85": {
    "facts": {
      "model": "BRS50",
      "fw": "10.3.04",
      "sw_level": "L2S",
      "uptime_sec": 412300
    },
    "ports": {
      "all": ["1/1", "1/2", "1/3", "1/4", "1/5", "1/6", "1/7", "1/8"],
      "management": "1/1",
      "ring_member": [],
      "lldp_neighbor": ["1/1"],
      "link_up": ["1/1"],
      "unused_safe_to_touch": ["1/2", "1/3", "1/4", "1/5", "1/6", "1/7", "1/8"]
    },
    "ring": null,
    "mrp_configured": false,
    "vrrp_configured": false,
    "vlans_configured": [1],
    "gathered_at": "2026-04-13T10:00:00Z"
  }
}
```

**Unused-port pool computation** (the user's catch):
- Start with all physical ports from `get_interfaces`
- Subtract the management port (from `get_management`)
- Subtract any port with an LLDP neighbor (could be an uplink we're connected through, or a neighbor switch we don't want to disturb)
- Subtract any port that's a ring member (from `get_mrp` if MRP is configured, from `get_rstp_port` topology data otherwise)
- Subtract the port we're talking to the device on (the one carrying our MOPS/SNMP/SSH session — derive from ARP or just from "the port whose LLDP-discovered neighbor's mgmt IP is OUR mgmt IP")
- Whatever's left = `unused_safe_to_touch`

Per-port setter cells get assigned a port from this list at job-creation time. The device pool stays clean (no per-port lab assumptions).

**Note on existing behavior:** `test_setter_pairs.py` currently hardcodes port `1/3`. That works for the lab BRS50s today but bakes in a lab assumption. The gather phase's `unused_safe_to_touch` replaces the hardcode. As an interim, the tool can still default to `1/3` if `unused_safe_to_touch` is empty or missing — backward compatible.

### Component 3: Test plan generator — `release_test_plan.json`

Pure function. Reads schemas, wire YAMLs, device pool, device state. Outputs the manifest of every cell that should exist.

```json
{
  "schema_version": 1,
  "generated_at": "2026-04-13T10:00:00Z",
  "scope": ["mops", "snmp"],
  "jobs": [
    {
      "job_id": "get_mrp__mops__192.168.60.80",
      "kind": "read",
      "schema": "mrp",
      "method": "get_mrp",
      "protocol": "mops",
      "device": "192.168.60.80",
      "requires": ["mrp_configured"],
      "depends_on": [],
      "verify_after": null,
      "estimated_ms": 500,
      "tags": []
    },
    {
      "job_id": "set_storm_control__mops__192.168.60.85__1-3",
      "kind": "setter",
      "schema": "protection",
      "method": "set_storm_control",
      "protocol": "mops",
      "device": "192.168.60.85",
      "args": {"port": "1/3"},
      "requires": [],
      "depends_on": [],
      "verify_after": "get_storm_control",
      "estimated_ms": 1500,
      "tags": []
    },
    {
      "job_id": "create_vrrp__mops__192.168.60.83",
      "kind": "crud",
      "schema": "vrrp",
      "method": "create_vrrp",
      "protocol": "mops",
      "device": "192.168.60.83",
      "requires": ["vrrp_capable"],
      "requires_not": ["vrrp_configured"],
      "depends_on": [],
      "verify_after": "get_vrrp_instances",
      "estimated_ms": 3000,
      "tags": []
    },
    {
      "job_id": "create_mrp__snmp__NO_DEVICE",
      "kind": "crud",
      "method": "create_mrp",
      "protocol": "snmp",
      "device": null,
      "verdict_at_plan_time": "not_applicable",
      "reason": "no device in pool with mrp_capable AND not mrp_configured"
    }
  ],
  "summary": {
    "total_jobs": 0,
    "by_kind": {"read": 0, "setter": 0, "crud": 0, "execute": 0},
    "by_device": {},
    "not_applicable_at_plan_time": 0
  }
}
```

The plan is the **contract**: any planned job that doesn't have a corresponding cell in `release_matrix.json` after execution is automatically `not_run` and counts as a gate failure. No silent skips.

The plan is also where we get parallelism efficiency: jobs are pre-assigned to devices, so each worker knows up front exactly what it will do. No mid-flight rebalancing.

### Component 4: Resolver

**No new schema metadata.** The schema already has everything. Each schema file IS a feature — `mrp.yaml` is the MRP feature, `vrrp.yaml` is VRRP, etc. — and each method already declares its `type:` (`get`/`set`/`create`/`delete`/`update`/`execute`). The resolver reads what's already there.

**Mechanical rule from existing schema fields:**

| Method `type:` | Device requirement (matched against `device_pool.yaml`) |
|---|---|
| `create` | `feature_id ∈ device.has_capable` AND `feature_id ∉ device.has_configured` |
| `delete` | `feature_id ∈ device.has_configured` |
| `set` / `update` | `feature_id ∈ device.has_configured` |
| `get` (returning a table with rows) | `feature_id ∈ device.has_configured` (otherwise the test passes vacuously on empty data) |
| `get` (returning global scalars only) | `feature_id ∈ device.has_capable` (no configuration needed to read globals) |
| `execute` | `feature_id ∈ device.has_capable` |

`feature_id` = schema filename without `.yaml`. So `mrp.yaml` defines `feature_id = mrp`, and a method on it requires `mrp` to appear in `device.has_capable` or `device.has_configured` per the table above.

**Per-port methods** additionally need the device to have entries in `device_state.json[device].ports.unused_safe_to_touch` (computed by the gather phase). Detected from method args declaring a `port` / `interface` parameter. The resolver picks one port from the pool per cell; multiple per-port cells on the same device may share a port (sequential within the worker means no conflict).

**Resolution algorithm:**
1. For each `(schema, method, protocol)` combination from the loaded schemas
2. Look up requirement from method `type:` per the table above
3. Walk `device_pool.yaml`. Find devices where requirement is satisfied AND `kind ∈ device.safe_for` (read kinds use `safe_for: read`, setter kinds use `safe_for: setter`, etc.)
4. From matches, pick the most "scratch" one: `sacrificial > lab > prod`
5. If no match → emit `not_applicable` plan entry with the unmet requirement as reason
6. Cells targeting the same device are grouped into that device's worker queue in dependency order (creates before reads-of-created, deletes after sets-of-existing, etc.)

**Device pool fields** simplified accordingly — no more `has` vs `has_not` distinction:

```yaml
devices:
  - ip: 192.168.60.80
    label: BRS50-RM-Lab
    sw_level: L2A
    has_capable:
      - mrp        # device supports MRP
      - rstp
      - vlan
      - ...
    has_configured:
      - mrp        # AND has an MRP ring already running on it
      - vlan
      - ...
    safe_for: [read, setter, crud]
    notes: "Ring master."
```

`has_capable` is the superset (everything the device CAN do). `has_configured` is the subset that's actually live right now. Gather phase can refresh `has_configured` automatically by introspecting the device, OR we leave it static and the user maintains it. Initial implementation: static, gather phase auto-refreshes as a v2 enhancement.

### Component 5: Worker pool

One worker thread per device. `concurrent.futures.ThreadPoolExecutor(max_workers = len(assigned_devices))`. Threads work because device communication is I/O-bound (sockets, HTTPS) — the GIL releases on every syscall. Process pool would add IPC complexity for zero throughput gain. Threads share the orchestrator's `matrix_db` handle for free.

```python
def worker(device_ip, jobs, matrix_db):
    """Owned by one device for its lifetime. Strictly serial within the device."""
    device = open_device(device_ip)
    try:
        for job in jobs:
            try:
                cell = dispatch(job, device)
            except CommsLostError as e:
                cell = {**job, "verdict": "comms_lost",
                        "evidence": {"error": str(e),
                                     "remaining_jobs": jobs[jobs.index(job)+1:]}}
                matrix_db.write_cell(job["schema"], job["method"],
                                     job["protocol"], device_ip, cell)
                matrix_db.write_marker(device_ip, "WORKER_STOPPED", cell)
                return  # stop this worker, others keep going
            matrix_db.write_cell(job["schema"], job["method"],
                                 job["protocol"], device_ip, cell)
    finally:
        try:
            device.close()
        except Exception:
            pass

def dispatch(job, device):
    if job["kind"] == "read":
        return run_one_read(device, job["method"], schema_lookup[job["method"]])
    if job["kind"] == "setter":
        return run_one_setter(device, job["test_id"], setter_test_lookup[job["test_id"]])
    if job["kind"] == "crud":
        return run_one_crud(device, job["test_id"], crud_test_lookup[job["test_id"]])
    if job["kind"] == "execute":
        return run_one_execute(device, job["method"], job.get("args", {}))
```

**Comms loss detection**: a worker catches transport-level exceptions (socket timeout, connection reset, SSH disconnect) and treats them as `CommsLostError`. The worker:
1. Writes the current job as a `comms_lost` cell to the matrix DB
2. Writes a `WORKER_STOPPED` marker
3. Closes (or tries to close) and returns
4. **Does not retry, does not assume cause**

Other workers keep running on their own devices. The orchestrator collects markers after `executor.shutdown()` and prompts the user:

```
WORKER_STOPPED on 192.168.60.80 after set_mrp(domain=2)
Last successful cell: get_mrp passed 412ms
Remaining queue: 23 jobs (delete_mrp, get_mrp_sub_ring, ...)

Manual verification required. Did the SET cause the comms loss?
After confirming device state, resume with:
  release_matrix.py --device 192.168.60.80 --resume
```

### Matrix DB — central JSON treated as a database

`tests/release_matrix.json` is the single source of truth. Hierarchical key structure, lock-and-backoff write protocol, no shards.

**Structure:**

```json
{
  "schema_version": 1,
  "generated_at": "2026-04-13T10:00:00Z",
  "engine_version": "2.9.0",
  "scope": ["mops", "snmp"],
  "results": {
    "mrp": {
      "get_mrp": {
        "mops": {
          "192.168.60.80": {
            "verdict": "pass",
            "kind": "read",
            "time_ms": 412,
            "evidence": {"contract_errors": [], "type_errors": []},
            "tags": [],
            "ran_at": "2026-04-13T10:01:23Z"
          },
          "192.168.60.85": {
            "verdict": "not_applicable",
            "reason": "mrp not in has_configured for this device"
          }
        },
        "snmp": {
          "192.168.60.80": {"verdict": "pass", "...": "..."}
        }
      },
      "create_mrp": {
        "mops": {
          "192.168.60.85": {"verdict": "pass", "kind": "crud", "...": "..."}
        }
      }
    },
    "vrrp": {
      "get_vrrp_instances": {
        "mops": {
          "192.168.60.83": {
            "verdict": "fail",
            "kind": "read",
            "evidence": {"contract_errors": ["row [1/2:] missing keys: ['vrid']"]},
            "tags": ["#engine", "#driver", "#VRRP-MOPS-Compound"]
          }
        }
      }
    }
  },
  "markers": [
    {"type": "WORKER_STOPPED", "device": "192.168.60.80",
     "after_job": "set_mrp__mops__192.168.60.80", "at": "2026-04-13T10:05:00Z"}
  ],
  "summary": {
    "by_protocol": {"mops": {"pass": 0, "fail": 0, "...": 0}},
    "release_gate": {"scope": ["mops", "snmp"], "verdict": "fail | pass"}
  }
}
```

**Key insight:** every cell has a unique address `results[schema][method][protocol][device]`. Two workers can never logically conflict — they're writing to different cells. The only conflict is a literal disk-write race when two workers happen to flush at the same instant.

**Write protocol:**

```python
def write_cell(self, schema, method, protocol, device, cell):
    """CSMA/CD for the matrix DB. Lock, modify slot, release. Backoff on contention."""
    backoff_ms = 0
    for attempt in range(20):
        try:
            with file_lock(self.path, timeout_ms=100):
                data = json.load(open(self.path))
                data["results"].setdefault(schema, {}) \
                              .setdefault(method, {}) \
                              .setdefault(protocol, {})[device] = cell
                json.dump(data, open(self.path, "w"), indent=2)
                return
        except LockTimeout:
            backoff_ms = random.randint(50, 200)
            time.sleep(backoff_ms / 1000)
    raise MatrixDBContention(f"could not acquire lock after 20 attempts on {schema}/{method}")
```

`file_lock` uses `fcntl.flock` on Linux (we're Linux-only for development). The lock is held for milliseconds — read+modify+write of a small JSON file. With 5 workers each writing ~1 cell per second, contention is statistically negligible. The 20-attempt × 50–200ms backoff ceiling is ~3 seconds, far longer than any realistic queue time.

**No shards directory. No merge step.** The matrix DB is always current. A `Ctrl-C` mid-run leaves a valid (partial) JSON behind. A subsequent surgical `--method X --device Y` re-run updates exactly that cell, leaving everything else intact. This is the "treat it as a DB" property — every operation is independent and addressable.

### Component 6: Orchestrator (`tests/release_matrix.py`)

Single CLI entry point. All other components are imported, not subprocessed.

### Output contracts (the artifacts)

Two files, both authoritative:

| File | Purpose | Authoritative for |
|---|---|---|
| `tests/release_test_plan.json` | What SHOULD be tested | Gate: every planned job has a cell |
| `tests/release_matrix.json` | What WAS tested | Gate: every cell has a `pass`/`exempt`/`not_applicable` verdict |

A planned job missing from results = `not_run` = gate fail. The two files are compared by the gate check.

### Cell verdict enum

| Verdict | Meaning |
|---|---|
| `pass` | Live execution succeeded, all checks passed |
| `fail` | Live execution failed or returned wrong shape — release blocker |
| `comms_lost` | Worker stopped mid-job. Requires manual user verification before resume |
| `exempt` | In `tests/wire_exemptions.yaml` or `tests/method_exemptions.yaml` with documented reason |
| `not_applicable` | Resolver found no device matching `requires`, OR method not supported on this protocol per wire YAML |
| `not_run` | Planned but never attempted — gate fail |

### CLI surface

```bash
# === Surgical (debug, "test one thing real quick") ===

# Single cell — one method on one protocol on one device
python3 tests/release_matrix.py --method get_vrrp_instances --protocol mops --device 192.168.60.83

# One schema's worth of cells on one device
python3 tests/release_matrix.py --schema vrrp --device 192.168.60.83 --protocol mops

# === Full pipeline (release gate) ===

# Step 1: gather (live read pass on every device, ~30s per device)
python3 tests/release_matrix.py --gather

# Step 2: plan (pure function, no I/O — uses device_state.json from gather)
python3 tests/release_matrix.py --plan

# Step 3: execute (worker pool, parallel by device)
python3 tests/release_matrix.py --execute

# Step 4: render docs/RELEASE_MATRIX.md from latest results
python3 tests/release_matrix.py --render

# All four in one shot:
python3 tests/release_matrix.py --gate

# === Resume / recovery ===

# Resume one device after manual verification of comms loss
python3 tests/release_matrix.py --resume --device 192.168.60.80

# Re-render only — no execution
python3 tests/release_matrix.py --render

# === Scope filters ===

--scope mops snmp     # default release scope
--scope mops          # narrower
--scope all           # everything including SSH and OFFLINE (post-release scope)
```

### Behavior rules

1. **Surgical-by-default for human runs.** A bare `--method X` runs ONE thing. `--gate` is the explicit "run everything" switch. A user typing the command should never accidentally hammer the fleet.
2. **Plan is the contract.** The plan is generated and saved BEFORE execution begins. Execution can only produce verdicts for planned jobs. New methods discovered at execution time do NOT auto-add to the plan — the plan is regenerated explicitly via `--plan`.
3. **Workers own devices.** One worker per device. Eliminates write collision risk. Trades a small amount of scheduling flexibility for full safety.
4. **Comms loss = stop and ask.** As described above. Orchestrator collects markers from any stopped workers and presents them to the user as a single block, after the run, never mid-flight.
5. **`not_applicable` is a verdict, not a skip.** Every `not_applicable` cell has a `reason`. If you can't explain why, it's `not_run` (gate fail).
6. **`exempt` requires a reason.** Reads from `tests/wire_exemptions.yaml` (existing, attr-level) and `tests/method_exemptions.yaml` (new, method-level). Both formats require a `reason` field per entry.
7. **Central matrix DB with lock+backoff writes.** Workers write directly to `tests/release_matrix.json` via `matrix_db.write_cell(...)`. Hierarchical key (`schema/method/protocol/device`) means cells never logically conflict. `fcntl.flock` + 50–200ms random backoff handles disk-write races. No shards, no merge step, always current.
8. **No subprocess shelling between components.** Everything is imported. The independent CLIs of `audit_getters_v2.py`, `test_setter_pairs.py`, `test_crud_pairs.py` keep working as before — they're still standalone tools.
9. **`run_one_*` is the unit of work.** The refactored `run_one_read` / `run_one_setter` / `run_one_crud` callables are what workers invoke. One job in, one cell dict out. Adding a new test kind = adding a new `run_one_*` function and registering it in the dispatcher.

### Doc generation from matrix

The renderer produces THREE files from `release_matrix.json` + `release_test_plan.json`:

| File | Generated? | Purpose | Edited? |
|---|---|---|---|
| `docs/RELEASE_MATRIX.md` | Yes, every run | Read-only status summary. The "scoreboard" | Never |
| `docs/TODO_HITLIST.md` | Yes, every run | Raw working list of failures grouped by `#bucket` tag. The "to-fix queue" | Never |
| `docs/TODO.md` | No, curated | Release-blocking work, judgement-applied. What we actually work on | By session |

**`docs/RELEASE_MATRIX.md` sections:**
- Plan vs results summary (planned, ran, passed, failed, exempt, n/a, not_run, comms_lost)
- Per-protocol counts table
- Per-device fleet table (which devices participated, capabilities)
- Per-schema status table (rows = methods, columns = protocol×device, cells = verdict)
- `comms_lost` list (if any) with manual-verification instructions

**`docs/TODO_HITLIST.md` structure:**

```markdown
# TODO Hitlist (auto-generated 2026-04-13)

> Raw failures from release_matrix.json grouped by tag bucket.
> NOT the curated TODO. See docs/TODO.md for the working list.

## #engine
- [ ] #engine #VRRP-MOPS-Compound
      get_vrrp_instances on 192.168.60.83 via mops
      contract_errors: row [1/2:] missing keys: ['vrid']
      first seen: 2026-04-13T10:01:23Z

## #wire
- [ ] #wire #DNS-AddrType-SSH
      get_dns on 192.168.60.85 via ssh
      type_errors: addr_type expected int got str
      first seen: 2026-04-13T10:02:11Z

## NEEDS TRIAGE — no tag assigned
- [ ] get_qos on 192.168.60.80 via mops
      contract_errors: missing keys: ['cos_to_tc_map']
      Suggest tag in tests/tag_map.yaml then re-render.
```

**Tag stickiness via `tests/tag_map.yaml`:**

```yaml
# Failure-pattern → tag mapping. Match by method+protocol+evidence-substring.
# Add entries here after triaging untagged failures so they auto-categorize next run.
patterns:
  - match: {method: get_vrrp_instances, protocol: mops, evidence_contains: "missing keys: ['vrid']"}
    tags: ["#engine", "#driver", "#VRRP-MOPS-Compound"]

  - match: {method: get_dns, protocol: ssh, evidence_contains: "addr_type expected int"}
    tags: ["#wire", "#DNS-AddrType-SSH"]
```

**The curation flow** (one session pass after each matrix run):

1. Matrix tool runs → `release_matrix.json` updated
2. Renderer runs → `RELEASE_MATRIX.md` + `TODO_HITLIST.md` regenerated
3. Session reads `TODO_HITLIST.md`, looks at "NEEDS TRIAGE" section
4. For each triage item: assign a `#bucket #ID`, write to `tag_map.yaml`, decide if it's release-scope or roadmap
5. Re-run renderer (no execution) → triage section empties
6. Session updates `docs/TODO.md` with release-scope items only, ordered by priority
7. Items that go to roadmap get added to `docs/ROADMAP.md` with the same `#ID`

**Cleanup discipline:** when a fix ships, the cell verdict flips to `pass`. The renderer drops it from `TODO_HITLIST.md`. The session removes it from `TODO.md`. `grep -r '#VRRP-MOPS-Compound' docs/ tests/` should return zero hits — any remaining hit is a dangling reference.

`docs/ROADMAP.md` is hand-curated for post-release scope using the same `#bucket #ID` tag scheme.

### Safety protocols (CLAMPS-style pre/post)

Some methods need ordering safety: e.g., `set_mrp` shouldn't reconfigure a live ring without first admin-downing the secondary ring port. CLAMPS does this externally; for the matrix tool we declare it once in `tests/safety_protocols.yaml` and the runner applies it automatically.

**Layering — engine stays clean.** Safety protocols are a TEST infrastructure concern, NOT an engine concern. They live in `tests/safety_protocols.yaml`, applied by `tests/safety_runner.py`. The engine schemas in `crude_engine/schemas/` know nothing about them. Production callers using `napalm-hios` directly do not get safety wrapping — that's still their responsibility (or use a tool like CLAMPS). The matrix tool, `test_setter_pairs.py`, and `test_crud_pairs.py` all funnel through the same shared runner, so they all get safety for free.

**Two layers, one shared runner:**

| Layer | Where declared | Scope | Purpose |
|---|---|---|---|
| Method safety | `tests/safety_protocols.yaml` | EVERY call to the named method | "Always admin-down ring port 2 before set_mrp" — universal |
| Test prep | `setup:` / `teardown:` in test definitions | Only that specific test | "This test needs DHCP snooping enabled first" — per-test |

**Execution order around a wrapped method call:**

```
method-safety capture+pre  →  test-prep setup  →  method  →  test-prep teardown  →  method-safety restore
```

**Capture-on-entry / restore-on-exit pattern.** Safety protocols don't hardcode the restore value — they capture whatever was there before the change, restore it after. Matches the existing `test_setter_pairs.py` pattern (capture original, restore at end), one fewer mental model.

**File shape:**

```yaml
# tests/safety_protocols.yaml
protocols:
  set_mrp:
    description: "MRP changes need secondary ring port admin-down to prevent loops"
    requires_state: [ring_port_secondary]    # gather must populate; absent → not_applicable
    require_during:
      - target:
          read_method: get_interfaces       # how to read the current value
          write_method: set_interface       # how to apply new + restore captured
          index: "{ring_port_secondary}"    # resolved per-device from device_state
          field: admin_status
        must_equal: down                    # required value DURING the wrapped call
        # restore is implicit — captured live, applied on exit

  delete_mrp:
    description: "Same as set_mrp"
    requires_state: [ring_port_secondary]
    require_during:
      - target:
          read_method: get_interfaces
          write_method: set_interface
          index: "{ring_port_secondary}"
          field: admin_status
        must_equal: down
```

**Variable substitution:** `{ring_port_secondary}` etc. resolve from `tests/device_state.json` (gather phase output) at execute time, per device. If a required variable is missing, the runner emits `not_applicable` for that cell with reason "safety prerequisites not satisfied."

**v2 enhancement (post-release):** if a variable like `ring_port_secondary` is not in `device_state.json` BUT the relevant feature is configured on the device (e.g., MRP IS running), the runner can derive it on-demand by calling the relevant getter (`get_mrp` returns the secondary port). For v1 we use what gather captures — explicit and predictable.

**Runner sequence (`tests/safety_runner.py:apply_safety_protocol`):**

```
for each require_during entry:
    current = device.read_method(index)[field]
    if current == must_equal:
        will_restore = False                  # already in safe state, no-op
    else:
        device.write_method(index, **{field: must_equal})
        captured[entry] = current
        will_restore = True

run test-prep setup (existing test_setter_pairs/test_crud_pairs setup loop)
result = wrapped_method(*args, **kwargs)
run test-prep teardown

for each entry in REVERSE order:
    if will_restore:
        try:
            device.write_method(index, **{field: captured[entry]})
        except Exception as e:
            mark cell evidence with "safety_restore_failed: <method> <error>"

return result
```

**Failure handling:** if a `require_during` write fails before the wrapped method runs, the cell verdict is `error` with reason "safety pre-condition failed". If the wrapped method fails but pre succeeded, the runner still attempts the restore (best-effort) and reports both the wrapped failure and any restore failure in evidence. If the restore fails, the device is left in an unsafe state — the runner reports this clearly and the matrix tool emits a `WORKER_STOPPED` marker so the user can manually verify.

**Implementation footprint** — most of the work is refactoring, not new code:

| File | Change | Size |
|---|---|---|
| `tests/safety_protocols.yaml` | NEW data file | ~30 lines for v1 (set_mrp, delete_mrp, etc.) |
| `tests/safety_runner.py` | NEW shared module — `apply_safety_protocol(device, method_name, fn, device_state)` | ~120 lines |
| `tests/test_setter_pairs.py` | Refactor `run_test` setup/teardown loop into shared helper | ~10 line diff |
| `tests/test_crud_pairs.py` | Same | ~10 line diff |
| `tests/release_matrix.py` worker | Use the shared helper when dispatching setter/crud cells | ~5 lines |

Total: ~165 lines new code + ~25 lines refactored. Nothing in `crude_engine/`.

### Performance expectation

5 devices × ~80 read methods × ~3 protocols ≈ 1200 read cells. With one worker per device, the wall time should be roughly the time of the SLOWEST device's full read sweep, NOT 5× that. Setters and CRUD are slower per cell but also distribute by device. Initial target: `--gate` completes in < 10 minutes on the lab fleet.

Scale-out path (post-release): if test_replay fixture mode is added, fixture-based "dry runs" can run a 1000-cell matrix in seconds, no live device. Useful for CI on every commit.

## Phase plan

### Phase 0 — Tooling (no risk, all local)

**Completed in design session (2026-04-13):**
- [x] Read existing test scripts (`audit_getters_v2.py`, `audit_setters.py`, `test_setter_pairs.py`, `test_crud_pairs.py`, `audit_all.py`, `capture.py`, `test_replay.py`)
- [x] Rename `TODO.md` / `ROADMAP.md` → `-old` variants
- [x] Write `tests/README_TESTS.md` — script catalog
- [x] Write `docs/RELEASE_GATE.md` (this doc)
- [x] Update `CLAUDE.md` (now `local/archive/docs-legacy/claude/CLAUDE.md`) with tag scheme + RELEASE_GATE pointer + comms-loss rule
- [x] Refactor `audit_getters_v2.py` to expose `run_one_read(device, method, schema)`. Existing CLI unchanged.
- [x] Refactor `test_setter_pairs.py` to expose `run_one_setter(device, name, spec)`. Existing CLI unchanged.
- [x] Refactor `test_crud_pairs.py` to expose `run_one_crud(device, name, spec)`. Existing CLI unchanged.

**Build remaining (the orchestrator and its components):**
- [ ] **0.1 — Device pool YAML** (`tests/device_pool.yaml`): the 5 lab+prod devices with `has`/`has_not`/`safe_for` annotations. Capability vocabulary documented in this doc.
- [ ] **0.2 — Gather phase** (`tests/release_matrix.py --gather`): live read pass per device (facts, lldp, mrp, interfaces, management). Computes `unused_safe_to_touch` port pool. Outputs `tests/device_state.json`. **Surgical fallback**: if device unreachable, mark in state, plan generator emits `not_applicable` for all jobs targeting that device.
- [ ] **0.3 — Test plan generator** (`tests/release_matrix.py --plan`): pure function, schemas + wire YAMLs + device pool + device_state → `tests/release_test_plan.json`. Includes `requires` inference rules and explicit override support. NO live device I/O.
- [ ] **0.4 — Resolver**: integrated into plan generator. Walks device pool, picks best device per job, emits `not_applicable` plan entries when no match exists.
- [ ] **0.4 — Matrix DB write API** (`tests/release_matrix.py:MatrixDB`): `write_cell(schema, method, protocol, device, cell)`, `write_marker(...)`, `read()`, `gate_verdict()`. fcntl.flock + random backoff. Hierarchical key structure per design above.
- [ ] **0.5 — Worker function**: `run_worker(device_ip, jobs, matrix_db)` in `release_matrix.py`. Opens device once, dispatches jobs to `run_one_*`, catches `CommsLostError`, writes via `matrix_db.write_cell`. Strictly serial within a device.
- [ ] **0.6 — Orchestrator** (`tests/release_matrix.py`): CLI flags (`--gather`, `--plan`, `--execute`, `--render`, `--gate`, `--method`, `--device`, `--protocol`, `--schema`, `--scope`, `--resume`), worker pool via `concurrent.futures.ThreadPoolExecutor` (one thread per device), marker collection, gate verdict computation.
- [ ] **0.7 — Doc renderer**: generates `docs/RELEASE_MATRIX.md` from `release_matrix.json` + `release_test_plan.json`. Uses the section list above.
- [ ] **0.8 — Empty data files**: `tests/method_exemptions.yaml`, `tests/tag_map.yaml`.
- [ ] **0.9 — Smoke test**: surgical run `release_matrix.py --method get_facts --protocol mops --device 192.168.1.4`. Verifies wiring end-to-end on the smallest possible job. If this passes, Phase 0 is done.

**Phase 0 exit:** Surgical and full-pipeline modes both produce valid JSON + rendered MD. `--gate` correctly identifies pass/fail. Smoke test passes.

**Out of Phase 0 scope (deferred):**
- Optimization of read-method parallelism within a single device (e.g., concurrent MOPS+SNMP on one box) — workers stay strictly serial within a device for v1.
- Fixture-based dry-run mode (replay tap1 → cells without live device) — defer to ROADMAP.md.
- Scheduled / hook-driven runs — defer to ROADMAP.md.

### Phase 1 — Ground-truth pass (MOPS + SNMP, all kinds)

- [ ] Run `release_matrix.py --release-scope` against the fleet (.4, .254, .80, .83, .85)
- [ ] **One device + one protocol at a time** for the SET/CRUD kinds. Read kind can run all-at-once because it's safe.
- [ ] Capture the JSON. Inspect failures.
- [ ] Diff against current TODO-old.md / SSH_HITLIST claims. Every discrepancy = "doc was wrong, here's the new truth."
- [ ] Generate first draft of `docs/TODO.md` from the failure list, with tag assignments. User reviews.
- [ ] Generate first draft of `docs/ROADMAP.md` for post-release scope (SSH 1st-class, OFFLINE 1st-class if not done in Phase 3, HiSecOS, gNMI, Modbus, generator improvements, schema rework, benchmarking).

**Phase 1 exit:** truth JSON exists, TODO.md and ROADMAP.md drafts exist, every failure is tagged.

### Phase 2 — Execute the categorized work

Order matters. Engine first (highest blast radius, can invalidate later test results).

- [ ] `#engine` items — interpreter, dispatch, driver bug fixes that affect MOPS/SNMP path
- [ ] `#crude` items — matrix transforms (only if any are needed for MOPS/SNMP)
- [ ] `#wire` items — wire YAML fixes, generator-vs-manual reconciliation
- [ ] `#schema` items — schema YAML fixes
- [ ] `#driver` items — MOPS/SNMP driver fixes only. SSH driver work is `#roadmap`.

After each fix:
1. Surgical re-run: `release_matrix.py --method X --protocol Y --device Z`
2. Verify the cell flips to `pass`
3. After a batch (e.g., all engine fixes done): re-run the full release-scope matrix once. As proof, not as debugging.

**Phase 2 exit:** matrix tool reports zero `fail` and zero `not_run` for MOPS+SNMP across the fleet. Every `not_applicable` and `exempt` has a reason.

### Phase 3 — OFFLINE verdict (cheap, may extend release scope)

- [ ] `release_matrix.py --offline` against `local/reference/configs/*.xml`
- [ ] Inspect results
- [ ] Decision point:
  - If most cells `pass`: OFFLINE is already a citizen. Add `#release #Offline-1st-Class` to TODO.md. Update README. Test it for SET/CRUD too via the `set_config_remote` / `load_config` execute path. Move it into release scope.
  - If results are messy: every gap is categorized into the 5 buckets, tagged `#roadmap #Offline-1st-Class`, and rolled to post-release.

**Phase 3 exit:** OFFLINE has a verdict — citizen now, or citizen later, with reason.

### Phase 4 — Release prep

- [ ] Final full matrix run (release scope), single artifact
- [ ] Verify gate verdict = `pass`
- [ ] CHANGELOG.md — write release section, include matrix summary, include shipped tags
- [ ] README.md — update method counts, protocol coverage table, OFFLINE section if applicable
- [ ] Bump version (2.10.0 most likely)
- [ ] Patch via `local/reference/RELEASE.md` process
- [ ] Hand patch to user
- [ ] After user commits, push, tags: archive this RELEASE_GATE.md to `local/archive/RELEASE_GATE-v2.10.md`. Archive TODO-old.md and ROADMAP-old.md alongside.

**Release exit:** v2.10 (or chosen number) on PyPI. MOPS+SNMP first-class. OFFLINE per Phase 3 verdict. SSH explicitly post-release with full ROADMAP entry.

## Standing rules during this work

1. **Surgical testing always.** Full matrix runs are proof, not debugging. To debug one method on one protocol on one device, re-run only that cell.
2. **Comms loss = stop and ask.** If a SET/CRUD run breaks the device's responsiveness, the matrix tool stops, dumps state, and asks the user. No assumptions about cause.
3. **Re-verify, don't trust docs.** Every claim in TODO-old.md, SSH_HITLIST.md, and archived leftover Claude (`local/archive/docs-legacy/claude/CLAUDE.md`) is a hint. The matrix tool's output is the truth.
4. **No throwaway work.** Every script, every YAML, every doc must have post-release reuse value (CI input, regression suite, generator input). If it's a one-shot, push back and propose something reusable.
5. **Tag everything.** Every TODO entry has at least `#bucket #ID`. Every ROADMAP entry has `#roadmap #ID`. Every CHANGELOG entry references the shipped tags so the cleanup grep works.
6. **MOPS + SNMP only for the gate.** SSH work that surfaces during Phase 1 (e.g., a wire that's missing for SSH) does not block release. It gets a `#roadmap` tag and moves on. The exception is if the SSH gap reveals a real `#engine` or `#schema` bug that also affects MOPS/SNMP — then it's release scope.

## Resolved decisions

- **Tool name** — `tests/release_matrix.py` ✓
- **JSON file location** — `tests/release_matrix.json` ✓
- **Rendered doc location** — `docs/RELEASE_MATRIX.md` ✓
- **Tag scheme** — `#bucket #ID` two-token format ✓ (see "Cross-reference tag scheme" above)
- **TODO/ROADMAP rename** — `TODO-old.md` / `ROADMAP-old.md`, archive to `local/archive/` once release ships ✓

## Deferred until needed

- **Version number** — 2.10.0 vs 1.0.0. User said "could be 1.0.0 for all I care since we never released it yet." Decide at Phase 4.
- **`tag_map.yaml` shape** — (failure-pattern → tag) or (method → default tag) or both. Decide when first Phase 1 failures come in.

## What's NOT in scope for this release gate

Listed here so they don't sneak in. All of these go to ROADMAP.md.

- SSH 1st-class push (parsers, overlays, driver work for SSH)
- HiSecOS support
- Modbus transport
- gNMI adapter
- Multi-OS YAML structure
- Benchmarking
- Generator improvements (we work around manual wire fixes for now)
- Bidirectional `compute:` via `set_format:`
- `auto_disable` schema split
- API shape pass on remaining schemas
- Custom skill for matrix operations

If something in this list turns out to block MOPS+SNMP correctness during Phase 1/2, it's promoted to release scope and tagged accordingly. Otherwise it stays out.
