"""Leftover v26/monolith script. Not live law. Do not run.

Hardcoded napalm-hios-v2 / napalm_hios paths from the old monolith.
Kept (not deleted) as archive. Live generators: generate_docs.py,
generate_method_ref.py, generate_protocols.py. Live schema check:
validate_schemas.py. See local/generator/README.md.
"""

import yaml, os

WIRE_DIR = "/home/adamr/obsidian-vault/Projects/napalm-hios-v2/local/reference/webUI"
SCHEMA_DIR = "/home/adamr/obsidian-vault/Projects/napalm-hios-v2/napalm_hios/schemas"

# Build wire attr index
wire_index = {}
for f in sorted(os.listdir(WIRE_DIR)):
    if not f.endswith('.yaml'): continue
    with open(os.path.join(WIRE_DIR, f)) as fh:
        data = yaml.safe_load(fh)
    for attr in data.get('attributes', {}):
        wire_index[attr] = f[:-5]

# Check each schema
total = found = 0
missing = []
for f in sorted(os.listdir(SCHEMA_DIR)):
    if not f.endswith('.yaml'): continue
    with open(os.path.join(SCHEMA_DIR, f)) as fh:
        s = yaml.safe_load(fh)
    for attr, ref in s.get('attributes', {}).items():
        if not isinstance(ref, dict) or 'wire' not in ref: continue
        total += 1
        src = ref.get('source', '')
        wp = os.path.join(WIRE_DIR, f"{src}.yaml")
        if os.path.exists(wp):
            with open(wp) as wf:
                wd = yaml.safe_load(wf)
            if ref['wire'] in wd.get('attributes', {}):
                found += 1
                continue
        actual = wire_index.get(ref['wire'], 'NOT_IN_ANY_WIRE')
        missing.append((f, attr, ref['wire'], src, actual))

pct = found * 100 // total if total else 0
print(f"Schema→Wire: {found}/{total} ({pct}%)")
if missing:
    fixable = [m for m in missing if m[4] != 'NOT_IN_ANY_WIRE']
    gone = [m for m in missing if m[4] == 'NOT_IN_ANY_WIRE']
    if fixable:
        print(f"\nFIXABLE ({len(fixable)}) — wrong source, attr exists elsewhere:")
        for s, a, w, src, actual in fixable:
            print(f"  {s}:{a} source={src} → should be {actual}")
    if gone:
        print(f"\nMISSING ({len(gone)}) — attr not in any wire file:")
        for s, a, w, src, actual in gone:
            print(f"  {s}:{a} wire={w} source={src}")
else:
    print("ALL RESOLVED")
