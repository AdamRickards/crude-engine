# TODO — cycle 0, honest catalogue

Curated 2026-08-17 from `docs/program/cycles.yaml`, `docs/TODO_HITLIST.md`, and `docs/REVIEW_PRIORITIES.md`.
Raw matrix failures stay in `TODO_HITLIST.md` (generated — do not edit).

A tag lives here **or** in `ROADMAP.md`, never both.

---

## This cycle (offline first)

- [ ] `#release #Docs-E-Count` — header walks schema `type:` only; count E from protocol YAML
      Proof: `python3 scripts/check_catalogue.py --e-count`
      Blocks: honest API_REFERENCE / METHOD_REFERENCE

- [ ] `#release #Docs-Composed-Label` — `Protocols: None` on composed methods reads as unimplemented
      Proof: `python3 scripts/check_catalogue.py --composed`
      See also `#schema #Defaults-Attr-Mismatch` (some Nones are real holes)

- [ ] `#release #Docs-Cli-Hatch` — flag `cli()` as the unbounded escape hatch
      Proof: `python3 scripts/check_catalogue.py --cli`

- [ ] `#schema #Defaults-Attr-Mismatch` — defaults keys that are not attributes (`get_config`, loop/auto-disable/fan, …)
      Proof: same composed check, after the YAML is truthful
      Verified: not yet

- [ ] `#engine #Principles-Grep` — `except Exception: pass` in `ssh_transport.py`, `snmp_transport.py`
      Proof: `python3 scripts/check_principles.py`
      Note: `if protocol ==` is already absent in `crude_engine/`

- [x] `#test #Validator-Exit-Code` — validator printed errors and exited 0; now exits 1
      Proof: `python3 local/generator/validate_schemas.py --errors`

- [ ] `#schema #Validate-Existing-Errors` — 6 structural errors now visible (alias `type`, qos_mapping defaults, software compute.from)
      Proof: `python3 local/generator/validate_schemas.py --errors`

- [ ] `#schema #Validate-MUSTs` — implement SCHEMA_MODEL MUSTs the validator still skips (`index_key`, setter `wire`+`source`)
      Proof: same, after existing errors are green

- [ ] `#release #Docs-Regen` — regenerate API_REFERENCE + METHOD_REFERENCE after the generator/schema fixes
      Proof: `python3 scripts/check_catalogue.py`

---

## Same cycle, lab (do not start until offline is green)

- [ ] `#driver #SNMP-Compound-Index-Decode` — ~139 parity cells
      Blocks: 2.10 gate
      Verified: last seen 2026-04-14
      First move: `release_matrix.py --inspect --method get_mac_address_table --device 192.168.60.80 --trace`
      Compare to passing sibling `get_arp_table`. Do not jump to engine code.

- [ ] `#wire #NTP-Server-Enabled-Mismatch` — 6 cells, `get_ntp.server_enabled`
      First move: `--inspect --method get_ntp --device 192.168.60.80 --trace`

- [ ] `#release #Setter-Matrix` — 260 planned setter/CRUD jobs never executed in the April run
      Devices: `192.168.60.80`–`.85` (`safe_for: setter,crud`)
      Command: `release_matrix.py --execute --kind setter` then `--kind crud` then `--render`

---

## Parked (roadmap, not this cycle)

See `docs/ROADMAP.md`: SSH 1st-class, Offline verdict, HiSecOS, gNMI, tools, NILS.
