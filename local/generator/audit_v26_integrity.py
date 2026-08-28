import os
import yaml
import re

# Paths
V1_HIOS_PY = "/home/adamr/obsidian-vault/Projects/napalm-hios/napalm_hios/hios.py"
ADAPTER_YAML = "/home/adamr/obsidian-vault/Projects/napalm-hios-v2/napalm_hios/adapters/napalm.yaml"
SCHEMA_DIR = "/home/adamr/obsidian-vault/Projects/napalm-hios-v2/napalm_hios/schemas"
WIRE_DIR = "/home/adamr/obsidian-vault/Projects/napalm-hios-v2/local/reference/webUI"

def get_v1_methods():
    methods = set()
    if not os.path.exists(V1_HIOS_PY): return methods
    with open(V1_HIOS_PY, "r") as f:
        for line in f:
            match = re.search(r"def (get_|set_|create_|delete_|add_|remove_)([a-z0-9_]+)\(", line)
            if match:
                methods.add(match.group(1) + match.group(2))
    return methods

def audit_coverage():
    print("Starting v2.6 Deep Coverage & Integrity Audit...")
    v1_methods = get_v1_methods()
    
    with open(ADAPTER_YAML, "r") as f:
        adapter = yaml.safe_load(f)
    
    adapter_methods = adapter.get("methods", {})
    missing_in_adapter = v1_methods - set(adapter_methods.keys())
    
    broken_wire_files = []
    missing_wire_attrs = []
    missing_schema_methods = []
    
    schema_cache = {}
    wire_cache = {}
    
    for a_method, mapping in adapter_methods.items():
        s_id = mapping.get("feature")
        s_method = mapping.get("schema")
        
        s_path = os.path.join(SCHEMA_DIR, f"{s_id}.yaml")
        if not os.path.exists(s_path):
            continue # Already caught by adapter-level checks if needed
            
        if s_id not in schema_cache:
            with open(s_path, "r") as f:
                schema_cache[s_id] = yaml.safe_load(f)
        
        schema_data = schema_cache[s_id]
        methods_in_schema = schema_data.get("methods", {})
        
        if s_method not in methods_in_schema:
            missing_schema_methods.append(f"{a_method} -> {s_id}.yaml::{s_method}")
            continue

        # Audit Attribute Resolution (Schema -> Wire)
        # We check ALL attributes in the schema file associated with this feature
        for h_attr, a_map in schema_data.get("attributes", {}).items():
            w_id = a_map.get("source")
            w_attr = a_map.get("wire")
            
            w_path = os.path.join(WIRE_DIR, f"{w_id}.yaml")
            if not os.path.exists(w_path):
                link = f"{s_id}.yaml -> {w_id}.yaml (Missing Wire File)"
                if link not in broken_wire_files: broken_wire_files.append(link)
                continue
                
            if w_id not in wire_cache:
                with open(w_path, "r") as f:
                    wire_cache[w_id] = yaml.safe_load(f)
            
            wire_data = wire_cache[w_id]
            if w_attr not in wire_data.get("attributes", {}):
                missing_wire_attrs.append(f"{s_id}.yaml::{h_attr} -> {w_id}.yaml::{w_attr} (Missing Attribute)")

    print(f"\n--- INTEGRITY REPORT ---")
    print(f"Missing in Adapter:        {len(missing_in_adapter)}")
    print(f"Missing Schema Methods:    {len(missing_schema_methods)}")
    print(f"Broken Wire File Links:    {len(broken_wire_files)}")
    print(f"Missing Wire Attributes:   {len(missing_wire_attrs)}")
    
    if broken_wire_files:
        print("\n[!] Broken Wire File Links:")
        for m in broken_wire_files: print(f"  - {m}")

    if missing_wire_attrs:
        print("\n[!] Missing Wire Attributes (Defined in Schema but missing in Wire YAML):")
        # Deduplicate and sort
        for m in sorted(list(set(missing_wire_attrs))): print(f"  - {m}")

if __name__ == "__main__":
    audit_coverage()
