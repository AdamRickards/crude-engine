# Roadmap — From Driver to Framework

> "From Writing Drivers to Defining Knowledge."

## v2.9 — Gates as Gatekeepers — DONE

Three-gate architecture. Layer enforcement. No gate transit, no context, no operation.

- **3 dataclasses**: `ResolvedIntent`, `SchemaContext`, `WireContext`
- **3 gates**: Schema Contract, Wire Contract, Encode/Decode + Transport
- **Public API**: `resolve_intent()` → `execute_resolved()`
- **174 methods** (16C 78R 64U 16D) across 45 schemas
- **dispatch_batch** (atomic multi-attr SET), **gather_and_decode** (egress)
- **Lazy context maps** via `_resolve_context_map()`, zero I/O at connect, batched into getter gather
- **Protocol-free adapter** — zero protocol names in hios.py
- **Registry** — single source of truth for all protocol mappings

## v3.0 — HiSecOS + Modbus Transport — NOT STARTED

Additive — new wire YAMLs, new transport, same engine. Proves the multi-OS and multi-transport design.

**HiSecOS** (EAGLE40 family):
- Different MIB set from HiOS — new wire YAMLs needed
- Guard system for OS-conditional attributes (engine guard infrastructure exists)
- Schema YAMLs may need per-OS nesting (`hios:`, `hisecos:`) for attrs that differ
- Test devices running HiSecOS required

**Modbus Transport**:
- New transport class + driver in registry
- Protocol YAML (`Modbus.yaml`) with wire_type_defaults
- Wire attrs that support Modbus get `modbus:` source blocks
- No CRUDE changes — Modbus values go through same matrix

**What's needed**:
- Wire YAMLs for HiSecOS MIBs (generator may need HiSecOS firmware input)
- `modbus_transport.py` + `modbus_driver.py`
- Registry entries for both
- Live test devices (HiSecOS + Modbus-capable)

## v3.1 — gNMI Adapter (get/set) — NOT STARTED

Second consumer of the engine. Forces the packaging decision: shared engine library (`hios-engine`) with per-consumer adapters (`napalm-hios`, `gnmi-hios`), or monorepo?

**Path registry from schemas**: every schema declares `method_name → attributes → wire + source`. A gNMI path auto-derives:

```
Schema: dns.yaml, method: get_dns, attr: enabled
  → /napalm-hios/dns/enabled                    (canonical path)

Schema: interface.yaml, method: get_interfaces, primary_key: name
  → /napalm-hios/interfaces/interface[name=1/1]/admin_status  (table path)
```

Optional OpenConfig mapping via `gnmi:` key in schema YAML:

```yaml
attributes:
  enabled:
    wire: hm2dnsclientadminstate
    source: dns
    gnmi:
      path: /system/dns/config/enabled    # OpenConfig override
```

**What's needed**:
- `build_path_registry()` on FeatureEngine — `gnmi_path → (feature_id, method_name, attr_name)` reverse map
- `gnmi.py` adapter — uses `resolve_intent` / `execute_resolved` (same as hios.py)
- gNMI transport class (Protobuf/gRPC)
- Protocol YAML (`gNMI.yaml`)
- **Packaging decision**: engine as shared dep, or embedded?

**What v2.9 gives for free**:
- gNMI Get = `resolve_intent("get_dns")` → `execute_resolved(resolved, protocol, transport)`
- gNMI Set = `resolve_intent("set_dns", is_setter=True, enabled=True)` → `execute_resolved(...)`
- All methods exposed via path registry with zero engine work
- The engine doesn't know gNMI exists. It returns its contract. The adapter translates.

## v3.2 — gNMI Subscribe + SNMP Trap Transport — DESIGN PHASE

Push transport and streaming subscriptions. New engine concept — current engine is request/response only.

**Three subscription modes**:
- **SAMPLE** (poll worker) — timer-driven `execute_resolved`, diff against last result, send gNMI notification on change
- **ON_CHANGE** (SNMP trap-backed) — trap listener → Gate 3 decode → engine pipeline → notification. Falls back to poll for paths without trap coverage
- **TARGET_DEFINED** — server decides mode per path based on trap availability

**SNMP Trap Transport** (new transport class):
- Listens for SNMP traps
- Trap data flows: DEVICE → trap listener → Gate 3 DECODE → engine translate
- Same egress pipeline as a GET, but push-triggered
- Reverse-lookup: OID → wire_file + wire_attr via path registry

**What's needed**:
- `SNMPTrapTransport` class — trap listener, varbind decode, callback registration
- Poll worker infrastructure — timer, diff, notification dispatch
- Subscribe model in engine — new concept

## Canonical Schema Shapes — v2.9 RELEASE GATE

Schemas currently output NAPALM-shaped data (historical — schemas were written to match NAPALM spec). This is backwards. The schema should define OUR canonical shape, and NAPALM is one consumer that reshapes for its spec.

**Canonical shape contract**: `get_dns()` returns `{ global values, Nx dict of sub_tables by index, { any nested sub_table sub_tables } }`. Consistent, predictable, our definition. Gate 1 exit validates this contract.

**NAPALM as consumer**: each NAPALM standard getter calls the engine, gets canonical output, then reshapes through its own shaper (the `_shape_*` methods on hios.py). `napalm_compat=True` (default) = NAPALM shape. `napalm_compat=False` = canonical shape. The flag is already in place on all 18 NAPALM getters — the reshaping just isn't wired yet because schemas still output NAPALM shapes.

**What needs to happen**:
- Define the canonical shape contract per schema (review each schema's `defaults:` + `sub_tables:`)
- Where schemas currently contort to match NAPALM spec, straighten them to canonical
- Wire the `_shape_*` methods into the NAPALM getters behind `napalm_compat` guards
- Add shapers for getters that currently match NAPALM by coincidence but diverge from canonical
- Gate 1 exit already validates — canonical shapes just need to be correct

**Why this matters**: gNMI (v3.0) and any future adapter get canonical from the engine. They don't know or care about NAPALM. If schemas output NAPALM shapes, every non-NAPALM consumer has to undo NAPALM's opinions. Canonical first, consumer reshaping second.

## Package Split — crude-engine + napalm-hios — DONE

The engine is the product. The adapter is a consumer. Split into two packages (2026-04-02):

- **crude-engine** (`/Projects/crude-engine/`): `crude_engine/` Python package, v2.9.0. Engine + drivers + schemas + wire + transport_registry
- **napalm-hios** (`/Projects/napalm-hios/`): `napalm_hios/` Python package, v2.0.0. Thin adapter shim, requires crude-engine

**napalm-hios is mostly static** — it's the adapter shim + NAPALM reshaping. Feature work happens in crude-engine. New schemas, new wire files, new transports, new protocols — all crude-engine.

**Deployment pipeline**:
1. Work on crude-engine locally (Syncthing syncs to dev machine)
2. PyPI publish crude-engine from dev machine
3. `pip install crude-engine` pulls the engine
4. napalm-hios `install_requires = ["crude-engine>=2.9", "napalm>=3.0"]`
5. `pip install napalm-hios` pulls both

## napalm-skeleton-yaml — SPINOFF FROM v2.9

Community-ready YAML-driven NAPALM skeleton. Fork this instead of napalm-skeleton to build a declarative driver for any vendor.

**What it contains**:
- Clean engine (interpreter.py, crude.py, crude_matrix.yaml, steps.yaml, context_maps.yaml)
- Clean adapter (hios.py pattern — protocol-free, gate-driven)
- Wire generator (from MIB/webUI/API → wire YAMLs)
- Transport registry pattern
- Example schema YAMLs for NAPALM standard getters
- AI authoring guide — instructions for creating schemas beyond NAPALM standards (vendor-specific methods, CRUD, sub_tables, compute, lookup)

**Why**: the engine is vendor-agnostic. Wire YAMLs are per-device. Schemas are per-driver. The skeleton gives you the engine + adapter + generator, you supply the wire + schema for your vendor.

**Depends on**: v2.9 canonical shapes (so the skeleton ships with the right shape contract, not NAPALM-shaped schemas)

## Multi-OS — NOT STARTED

YAML spec supports per-OS nesting (`hios:`, `hisecos:`, `gardeos:`). Schema + wire files are OS-agnostic by design. Wire YAMLs are per-MIB, not per-vendor.

**What's needed**:
- Wire YAMLs for HiSecOS (EAGLE40 family) — different MIB set
- Guard system for OS-conditional attributes (engine guard infrastructure exists)
- Test devices running HiSecOS

## Current State (2026-04-02)

| Milestone | Status |
|-----------|--------|
| Three-gate model (v2.9) | Done |
| 174 methods (16C 78R 64U 16D) | Done |
| Protocol-free adapter | Done |
| Lazy context maps (zero I/O connect) | Done |
| dispatch_batch (atomic multi-attr SET) | Done |
| MOPS egress batching (one HTTP per getter) | Done |
| Context maps in gather batch (zero extra round trips) | Done |
| Canonical schema shapes (v2.9 release gate) | Done — interface, lldp, mac, optics canonicalized |
| NAPALM reshaping via napalm_compat | TODO — napalm-hios side (see napalm-hios/docs/TODO.md) |
| Package split (crude-engine + napalm-hios) | Done — crude_engine 2.9.0 + napalm-hios 2.0.0 |
| HiSecOS + Modbus transport (v3.0) | Not started |
| gNMI adapter get/set (v3.1) | Not started — forces packaging decision |
| gNMI subscribe + trap transport (v3.2) | Design phase |
