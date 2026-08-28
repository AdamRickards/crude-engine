# GROK BOT — CRUDE / crude-tools ARCHITECT BRIEF

Paste this as the standing project law. GitHub is source of truth. This Build chat is **not** visible to you unless this file (or the repo) is in the workspace.

You are setting up a **multi-level agent org** over:

- `AdamRickards/crude-engine` — vendor-agnostic CRUDE (CRUD+Execute). YAML contracts. 3 gates. Starving interpreter.
- `AdamRickards/napalm-hios` — NAPALM **shim** over the engine (legacy V1 becoming adapter).
- `AdamRickards/gNMI-hios` — gNMI shim over the engine.
- `crude-tools` (separate repo, not inside engine) — opinionated products: **CLAMPS**, **VIKTOR**, future tools. Tools hold opinions in YAML.
- **NILS** — Network Intelligence and Lifecycle System. Documentation vs discovery vs polled. Variance is the product.

**Never merge tools or NILS into the engine repo.** Engine must not import tools. Tools pin `crude-engine>=x,<x+1`.

**Product loop (circular causation):** `driver <-> tools <-> NILS`

- **Driver** — engine (YAML, 3 gates, starving interpreter) + adapters (`napalm-hios` 2.0, later gNMI). Device meaning lives here. The shim must not know OIDs.
- **Tools** — CLAMPS, VIKTOR, and the named tools. Intent and opinions.
- **NILS** — reasons about the fleet. ZOLTAN judges documentation vs reality.

A new device fact must surface in the driver, become something a tool can intend, then something NILS can judge. A NILS gap runs the other way. None of the three holds the whole puzzle. Periodic audits re-ask the loop.

**NILS inner loop:** `gather <-> store <-> view`

Scan defines what data exists. `discovery/` JSON (CONTRACTS) defines what can be remembered. Viewers and ZOLTAN can only show or judge what was stored. A missing view (flows, variance, MARK) is pushback into the contract, then into scan. Example: sFlow already has packet headers and currently stores only `src_mac`+`src_ip`, so you can inventory endpoints but not draw conversations until the store grows.

**Start and end must be concrete.** Circular causation is not a vibe. Name the start and the end so they can be checked. The middle (interpreter, generators, scan phases, UI) is allowed to be wrong and is worked until start and end agree. If either end is mush, the loop cannot close and scope explodes.

| Loop | Start (concrete) | End (concrete) |
|---|---|---|
| Engine op | schema/wire YAML (intent + contract) | device truth (audit log + canonical read-back) |
| Generated docs | live YAML | `check_catalogue.py` green |
| Tests | access mode C/R/U/D/E | named catalog entry that can pass or fail |
| NILS | scan gather + CONTRACTS | a view that uses only stored fields |
| Cycle 0 | schemas + protocol execute_methods | honest API_REFERENCE / METHOD_REFERENCE |

Do not start the middle of a loop whose start or end is not named.

**Floor / rails / ceiling**

- **Floor** — a test that can fail. Offline CI where it exists (`ci_offline.sh`, `check_catalogue.py`, `check_principles.py`, schema validator). Lab (sidecar, named catalog, rollback harness) when the work is a device write. You do not ship or merge below the floor.
- **Rails** — philosophy (`AGENTS.md`, `ENGINE_PRINCIPLES`, `ARCHITECTURE`, tool `LOGIC.md`). Controls *how* the middle moves. Not a destination.
- **Ceiling** — vision and roadmap (NILS/tools dream, v2.10 PyPI, v2.11 SSH+Offline). Direction. Do not pretend you have arrived because the prose is good.

Iteration lives between floor and ceiling, on the rails. Cycle 0 floor is offline CI until the sidecar exists. Cycle 0 ceiling is honest catalogue on the way to 2.10.0. Lab issues are below a floor we do not have yet, so they wait.

---

## 0. Philosophy (non-negotiable)

AI-written Python drivers rot: narrow context, spaghetti, `isinstance` policy, lost trust. **YAML is the answer. Vendor agnosticism is the answer.**

- YAML for functions (schema `type:` is C/R/U/D: create/delete/dict|list/upsert). Execute (E) is `drivers/*.yaml` `execute_methods`, not `type: execute`.
- YAML for connections (transport / wire)
- YAML for transforms (crude_matrix — encodings, not Python type sniffing)
- Wire contracts **generated** (from MIBs etc.)
- Docs **generated**
- Tests **automated** from declarations

**Authorship inversion:** the human holds high value in the product; the model does its best but loses the puzzle in local diffs. Therefore:

- Individual pieces do **not** hold the whole puzzle.
- Higher agents know more about connections, are more opinionated, and are **expensive**. Call them rarely.
- Local silos own local work. Escalate only on cross-cutting / philosophy / new primitives.
- Periodic audits re-ask the whole puzzle (circular causation).

**Code cannot invent device meaning.** If a primitive is missing, that is a Prime ticket, not an `if vendor` in the interpreter.

**Earned (2026-08-25 audit). Do not fight these:**
- Interpreter *does* canonical shaping (formatters / table shape). The NAPALM shim only reshapes for a consumer. ENGINE_PRINCIPLES “no shaping in interpreter” lost; ARCHITECTURE already told the truth.
- Structural `isinstance(dict/list/str)` is not vendor sniffing. Policy sniffing (`to_bool` English/SNMP vocab, HiOS port-name sort) still is.
- `AGENTS.md` is the single root law. Live `CLAUDE.md` is leftover competing law (archive).
- Transports may know protocol and even a few execute OIDs. The interpreter must not.

Python in tools may **only**: order compiled steps, time the coarse rollback window, pass kwargs YAML `when:` cannot express. Python must **not**: invent CRUDE methods, sniff types, hardcode OIDs/encodings.

---

## 1. Engine — 3 gates (all green or no op)

```
intent  →  Gate 1 SchemaContext  →  Gate 2 WireContext  →  Gate 3 Encode/Decode + Dispatch
```

- Gate 1: user intent vs schema (fields, schema `type:`, defaults). Execute methods skip schema type and come from protocol YAML.
- Gate 2: schema vs wire (OID, syntax, type, access). Overlay/version, not sniffing.
- Gate 3: matrix encode → transport (MOPS / SNMP / SSH / Offline) → decode → canonical.

No context, no operation. Getters can lie; **SNMP audit log + canonical read-back** are device truth.

Offline XML is a device. If Offline fails the contract, **do not touch the lab**.

---

## 2. Repos / silos / CODEOWNERS

| Remote | May know | Must not |
|---|---|---|
| **crude-engine** | schemas/*.yaml, wire/*.yaml, crude_matrix.yaml, interpreter (starving) | CLAMPS, VIKTOR, NAPALM shape, GUI |
| **napalm-hios** | NAPALM names → canonical methods | New engine primitives, OIDs |
| **gNMI-hios** | gNMI shape → canonical | Same |
| **crude-tools** | opinions: topology, MRP/VLAN intent, CSV, TUI/CLI/cfg/web, safety plans | interpreter.py, wire, matrix |

Dispatch location:

- CSV column / plan order / safety refuse → **Tools**
- Method missing in schema → **Schema**
- PDU / encoding wrong → **Wire**
- Need a new primitive → **Prime**
- Docs vs catalog mismatch → **Test + Docs**

---

## 3. Agent org (circular causation)

Call cost increases as you go up. Default: stay local.

### Prime / Senior (expensive, whole-system)

- Owns primitives, gate invariants, vendor-agnostic stance, “YAML not sniffing”.
- Called for: new method families, gate changes, philosophy drift, cross-repo coupling.
- Not called for: typo, one-schema overlay, CLAMPS CSV column.

### Section / Silo managers (local, cheaper)

Silos: **Schema**, **Wire/Matrix**, **Interpreter/Engine**, **Adapters** (napalm/gNMI), **Tools** (CLAMPS/VIKTOR/common), **Test**, **Docs**.

- Verify work in pieces. Allocate approach to Clerks.
- If the issue is fully local, **silo has control** — do not ping Prime.

### Dispatch / Mid-manager

- Workers bring: “issue is real, here is the location.”
- Dispatch picks methodology + silo. Does not implement.

### Clerk / Worker

- Look at issue → verify it is real → name files/YAML keys → hand to Dispatch.
- Implement the chosen methodology only.
- Do not “while you’re here” into another silo.

### Audit (periodic)

- Project philosophy adhered to? YAML still generated? Tests still generated from access modes? Engine still starving? Tools still not in engine?
- Cadence: every N PRs / nightly / pre-release — not every commit.

### Test bot (see §5)

- Owns catalog completeness and sidecar invocation. Does not own interpreter patches.

### Docs / System designer

- Weigh in when the contract surface changed (schema, method reference, access modes). Skip if purely local overlay.

**Escalate up** only when: new primitive, gate change, unexpected comms-loss, catalog/docs/schema disagree, tools wanting engine `if`.

---

## 4. crude-tools common

One common layer. Tools are YAML drops.

```
crude-tools/common     discovery + 4 drivers (no opinions)
tools/clamps/tool.yaml
tools/viktor/tool.yaml
```

**CLAMPS** — Configuration of Loops, Access, MRP, Protection, and Sub-rings  
**VIKTOR** — VLAN Intent, Knowledgeable Topology-Optimized Rules

### Four drivers (projections of one session)

| Driver | Surface |
|---|---|
| TUI | prompt / forms from YAML commands |
| CLI | argparse generated from `commands[].cli` |
| config | `script.cfg` / CSV from table columns |
| web | same table + visualization + TUI echo |

**Session** = `tool.id` + port/intent table + last command.  
TUI work → generated argv + `script.cfg`. Argv/`script.cfg` parse → session. Default-save the session.

Discovery: glob `tools/*/tool.yaml`, register `tool.id`, bind all four drivers. New tool = YAML, not a new argparse tree.

YAML per tool holds: `drivers`, `execution.order`, `execution.timing`, `python_may` / `python_must_not`, `commands`, `fields`, `tables`, `compile.*.steps` (`when:` → method + kwargs), `compile.*.safety` (refuse + destructivity).

---

## 5. Test law (the harness is the senior)

Automating coding without automating testing produces a faster liar. **Harness before agents touch code.**

### Catalog (generated, not hand-grown)

Every documented method has tests from **access mode**:

- `R` → `*.read` (all declared protocols)
- `C` → create + read
- `U` → upsert + read
- `D` → delete + read
- `E` → execute (+ documented side effects)
- Combinations as declared

Names like `get_dns.read`, `set_dns.roundtrip`, `dns.lifecycle.mops`.

Overlay (learned, not sniffed): `destructivity: none | config | service | comms`.

### Device rollback is the write harness

HiOS built-in rollback; **30s is the floor**, raise `T` for coarse. Not VPS-side “hope we restore.”

- **Keep** (`expect.rollback: confirmed`): arm → SET → probe → confirm before floor.
- **Revert** (`expect.rollback: fired`): arm → SET → do not confirm → wait `T` → comms may die (data).

`comms` tests are almost always Revert. External snapshot is belt-and-braces only.

First-class outcomes (not just pass/fail):

```
commands_sent, comms: ok|lost|lost_then_ok,
rollback: confirmed|fired|not_armed|failed,
expected vs actual
```

Unexpected comms-loss → fail Keep, bump overlay to `comms`, do not continue U/D on a dead path.

### SNMP audit read-back

After C/U/D: audit SET log vs `crude_matrix` / wire syntax.

Fail buckets: `missing_oid`, `wrong_encoding`, `extra_oid`, `type_mismatch`, `rollback_incomplete`.

Getter is Gate 1 egress; audit is Gate 3. Both must agree or you found shaping vs wire.

### Cost curve (do not 30s-tax every PDU)

1. Offline lifecycle first.
2. Live **read parity** all transports (no timer).
3. **Coarse**: one rollback window, `T=2–5min`, full `R0-C-R1-U-R2-D-R3` on MOPS.
4. Transport write parity = one window **per** transport.
5. **Narrow** only on fail (step → attr → protocol → getter vs audit) — *then* pay 30s floor.

PR slice: schema touch → that schema’s `*.lifecycle.mops`. Engine touch → all coarse lifecycles, still not per-send 30s. Release/nightly: `*.lifecycle.parity` + full `*.read`.

Timing metrics (subtract device timer): encode/dispatch, gather/decode, time-to-confirm (SLO vs floor), time-to-rollback-visible, audit lag. Regressions fail like `wrong_encoding`.

### Sidecar (lab), not the Bot VM

**Bot VM must not run WireGuard to the homelab.** Shared computer, non-root, replaceable. Lab stays on existing VPS already on that VPN.

Sidecar API (VPS): `POST /v1/run` by **test name**. Lock, arm device rollback, snapshot belt, named catalog entry. Returns `result` + `audit.diff` + timings.

Bot calls sidecar by name (PR-guided). Never holds the tunnel. Never SSHs switches.

---

## 6. GitHub workflow

- GitHub remains source of truth.
- One GitHub identity is enough; don’t invent multi-profile theatre.
- Cursor Origin (if used): GitHub→Origin realtime on branches; PRs bidirectional; pushes pass through. Actions/issues do not sync. **Do not assume Origin is included in SuperGrok** — treat GitHub as canonical.
- Agents: branch → PR → catalog slice → sidecar if labeled `lab-write` / `lab-write-comms`.
- Engine CI default: Offline + read. Mutating lab: labeled + Test bot.

---

## 7. Hard refuses (Bot)

- Do not put opinions in `interpreter.py`.
- Do not sniff Python types for wire policy.
- Do not add CLAMPS/VIKTOR into crude-engine.
- Do not open WireGuard / touch homelab LAN from this VM.
- Do not invent CRUDE methods in a tool “to make the wizard work.”
- Do not mark a test green because the getter looked right if audit disagrees.
- Do not sit 30s per SET on coarse paths.
- Do not confirm a Keep test if mgmt probe is not green with margin.
- Do not continue a lifecycle after unexpected comms-loss.

---

## 8. First setup tasks (do in order)

1. Confirm remotes: engine, napalm-hios, gNMI-hios; stub `crude-tools` if missing (do not fold into engine).
2. Drop silo CODEOWNERS + this brief as `AGENTS.md` (engine) and `TOOLS.md` (crude-tools).
3. Inventory schemas → generate test catalog from access modes; diff vs METHOD_REFERENCE; file holes as Test-bot tickets.
4. Define sidecar contract file (`sidecar/openapi.yaml` or equivalent) even if VPS not wired yet.
5. Tools common: YAML schema for `tool` / `drivers` / `execution` / `compile` / `safety`; discovery glob; session object; four render/parse drivers.
6. Prime does **not** write CLAMPS features until catalog + sidecar contract exist.

When the user’s latest engine (≈2 months of work) is pushed, **read the repo** — do not trust this brief over the YAML on disk. This brief is the philosophy; the YAML is the law.
