# Diagnostic Process — Fixing Failing Methods

> Follow this order strictly. Do NOT skip steps. Do NOT jump to engine code.

## The Ladder

### Step 1: Compare to a passing sibling

Find a method that passes using the same schema, engine path, or primitive. Diff the YAML declarations. Shape mismatch = contract bug, not engine bug. If radius passes and tacacs fails in the same schema, the answer is in the YAML difference.

### Step 2: Trace

`device.method_name(args, debug=True)` — see exactly what the pipeline produces at each step. What did intent resolution emit? What did the wire transform produce? What did the driver receive?

### Step 3: Validate off

`device.method_name(args, validate=False)` — if Gate 2 or 3 blocks, does it work without validation? If yes, the gate declaration is wrong, not the data.

### Step 4: Wire audit

Check against MIB source (`local/reference/MIBs/`) and MOPS schema (`local/reference/MOPS/mops_hios.xml`). Is `access:` right? Is `type:` right? Is `index_field:` present? Is `create_method:` correct? Is `index_type:` declared?

### Step 5: v1 reference

How did v1 (`/home/adamr/obsidian-vault/Projects/napalm-hios/`) handle this table? Not to copy code, but to understand what encoding/sequence the device expects. v1's working code is empirical proof of what the wire needs.

### Step 6: Fix the declaration, not the engine

Schema fix first. Wire fix second. Engine fix never — unless the primitive genuinely doesn't exist and affects multiple features.

If you fix a wire YAML manually, add a TODO in `docs/TODO.md` for the generator to learn.

### Step 7: Engine changes — last resort

Only after proving the gap affects multiple features and can't be declared away. Then design the primitive generically. Never add `if/else` for specific features.

## Key Principles

- **The YAML declares what should happen.** The engine executes unambiguously.
- **The CRUDE matrix encodes and decodes.** Not the transports. Transports are stupid — they send what they're given.
- **Schemas group by user intent**, not MIB structure. Cross-MIB attrs in one schema is correct when they serve the same user intent. WebUI pages are a good reference for what belongs together.
- **Standard output pattern**: globals + indexed sub_table for any feature with scalar config + table rows.
- **Never sniff data** to decide processing. If the engine needs to branch, the schema is missing a declaration.

## Common Root Causes

| Symptom | Likely cause | Fix layer |
|---------|-------------|-----------|
| `commitFailed` on CREATE | Missing required fields in create `defaults:` | Schema |
| `commitFailed` on SET | Feature/port not enabled (prerequisite) | Test setup |
| `unknown field` in Gate 1 | `set_format` template fields not consumed, or method `fields:` missing | Schema / assemble |
| HTTP 400 on compound table | Missing `index_type` or `index_fields` on wire, or `defaults:` missing addr_type | Wire / Schema |
| Value not encoded (raw IP instead of hex) | Syntax not registered for driver — compound fields not in `attr_syntaxes` | Engine (syntax registration) |
| DELETE requires index | Compound index: `_resolve_compound_index` needs values in kwargs or defaults | Schema `defaults:` |
| Walk returns full table instead of scalar | Use `index_filter:` with `value_map:` for targeted cell read | Schema |
