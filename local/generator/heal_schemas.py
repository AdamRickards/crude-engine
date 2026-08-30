"""Leftover v26/monolith script. Not live law. Do not run.

Hardcoded napalm-hios-v2 / napalm_hios paths from the old monolith.
Kept (not deleted) as archive. Live generators: generate_docs.py,
generate_method_ref.py, generate_protocols.py. Live schema check:
validate_schemas.py. See local/generator/README.md.
"""

import os
import yaml

# Paths
WIRE_DIR = "/home/adamr/obsidian-vault/Projects/napalm-hios-v2/local/reference/webUI"
SCHEMA_DIR = "/home/adamr/obsidian-vault/Projects/napalm-hios-v2/napalm_hios/schemas"

def heal_schemas():
    print("Building Wire Attribute Index...")
    wire_index = {} # attribute_name -> wire_file_base_name
    
    for fname in sorted(os.listdir(WIRE_DIR)):
        if not fname.endswith(".yaml"): continue
        w_id = fname.replace(".yaml", "").lower()
        with open(os.path.join(WIRE_DIR, fname), "r") as f:
            try:
                data = yaml.safe_load(f)
                if not data or "attributes" not in data: continue
                for attr in data["attributes"].keys():
                    attr_low = attr.lower()
                    # Preference: MIB > everything else
                    if "-mib" in w_id:
                        wire_index[attr_low] = w_id
                    elif attr_low not in wire_index:
                        wire_index[attr_low] = w_id
            except: continue
            
    print(f"Indexed {len(wire_index)} unique wire attributes.")
    
    healed_count = 0
    
    for fname in sorted(os.listdir(SCHEMA_DIR)):
        if not fname.endswith(".yaml"): continue
        s_path = os.path.join(SCHEMA_DIR, fname)
        with open(s_path, "r") as f:
            try:
                s_data = yaml.safe_load(f)
            except: continue
            
        if not s_data or "attributes" not in s_data: continue
        
        # Read raw text for surgical source: replacement
        with open(s_path, "r") as f:
            raw = f.read()

        new_raw = raw
        changed = False
        for h_attr, a_map in s_data["attributes"].items():
            old_wire = a_map.get("wire", "").lower()
            old_source = str(a_map.get("source", "")).lower().replace(".yaml", "")

            new_source = wire_index.get(old_wire)

            if new_source and new_source != old_source:
                print(f"  Fixing {fname}: {h_attr} ({old_wire}) -> {new_source}")
                # Replace only the source: line for this attribute
                new_raw = new_raw.replace(
                    f"source: {a_map.get('source', '')}",
                    f"source: {new_source}",
                    1  # only first occurrence per iteration
                )
                changed = True

        if changed:
            with open(s_path, "w") as f:
                f.write(new_raw)
            healed_count += 1
            
    print(f"Healed {healed_count} schema files.")

if __name__ == "__main__":
    heal_schemas()
