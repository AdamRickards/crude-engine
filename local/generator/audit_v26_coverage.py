"""Leftover v26/monolith script. Not live law. Do not run.

Hardcoded napalm-hios-v2 / napalm_hios paths from the old monolith.
Kept (not deleted) as archive. Live generators: generate_docs.py,
generate_method_ref.py, generate_protocols.py. Live schema check:
validate_schemas.py. See local/generator/README.md.
"""

import os
import yaml
import re

# Paths
V1_HIOS_PY = "/home/adamr/obsidian-vault/Projects/napalm-hios/napalm_hios/hios.py"
ADAPTER_YAML = "/home/adamr/obsidian-vault/Projects/napalm-hios-v2/napalm_hios/adapters/napalm.yaml"
SCHEMA_DIR = "/home/adamr/obsidian-vault/Projects/napalm-hios-v2/napalm_hios/schemas"

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
    print("Starting v2.6 Deep Coverage Audit...")
    v1_methods = get_v1_methods()
    
    with open(ADAPTER_YAML, "r") as f:
        adapter = yaml.safe_load(f)
    
    adapter_methods = adapter.get("methods", {})
    
    # 1. Check for v1 methods missing from Adapter
    missing_in_adapter = v1_methods - set(adapter_methods.keys())
    
    # 2. Check for Adapter methods pointing to broken Schemas
    broken_links = []
    missing_schema_methods = []
    missing_crud_attrs = []
    
    schema_cache = {}
    
    for a_method, mapping in adapter_methods.items():
        s_id = mapping.get("feature")
        s_method = mapping.get("schema")
        
        s_path = os.path.join(SCHEMA_DIR, f"{s_id}.yaml")
        if not os.path.exists(s_path):
            broken_links.append(f"{a_method} -> {s_id}.yaml (Missing File)")
            continue
            
        if s_id not in schema_cache:
            with open(s_path, "r") as f:
                schema_cache[s_id] = yaml.safe_load(f)
        
        schema_data = schema_cache[s_id]
        methods_in_schema = schema_data.get("methods", {})
        
        if s_method not in methods_in_schema:
            missing_schema_methods.append(f"{a_method} -> {s_id}.yaml::{s_method} (Missing Method)")
            continue
            
        # 3. CRUD Validation
        m_type = methods_in_schema[s_method].get("type")
        if m_type in ("create", "delete"):
            # Check if any attribute in this schema has 'access: crud'
            has_crud = False
            for attr, attr_def in schema_data.get("attributes", {}).items():
                if attr_def.get("access") == "crud":
                    has_crud = True
                    break
            if not has_crud:
                missing_crud_attrs.append(f"{a_method} ({m_type}) in {s_id}.yaml (No CRUD attribute found)")

    print(f"\n--- AUDIT REPORT ---")
    print(f"Total v1 Methods:          {len(v1_methods)}")
    print(f"Total Adapter Methods:     {len(adapter_methods)}")
    print(f"Missing in Adapter:        {len(missing_in_adapter)}")
    print(f"Broken Schema Files:       {len(broken_links)}")
    print(f"Missing Schema Methods:    {len(missing_schema_methods)}")
    print(f"Missing CRUD Attributes:   {len(missing_crud_attrs)}")
    
    if missing_in_adapter:
        print("\n[!] v1 Methods not in Adapter:")
        for m in sorted(missing_in_adapter): print(f"  - {m}")
        
    if broken_links:
        print("\n[!] Broken Schema Links:")
        for m in broken_links: print(f"  - {m}")

    if missing_schema_methods:
        print("\n[!] Missing Schema Methods (Defined in Adapter but not in YAML):")
        for m in missing_schema_methods: print(f"  - {m}")

    if missing_crud_attrs:
        print("\n[!] CRUD Mismatch (Methods need a 'crud' access attribute):")
        for m in missing_crud_attrs: print(f"  - {m}")

if __name__ == "__main__":
    audit_coverage()
