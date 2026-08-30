"""Leftover v26/monolith script. Not live law. Do not run.

Hardcoded napalm-hios-v2 / napalm_hios paths from the old monolith.
Kept (not deleted) as archive. Live generators: generate_docs.py,
generate_method_ref.py, generate_protocols.py. Live schema check:
validate_schemas.py. See local/generator/README.md.
"""

import os
import yaml
import re

SCHEMA_PATH = "/home/adamr/obsidian-vault/Projects/napalm-hios-v2/docs/napalm-hios-2-6-schema.md"
WEBUI_FEATURES = "/home/adamr/obsidian-vault/Projects/napalm-hios-v2/local/reference/webUI"

def load_schema_db():
    """Parse the markdown schema into a searchable database."""
    db = {}
    if not os.path.exists(SCHEMA_PATH): return {}
    with open(SCHEMA_PATH, "r") as f:
        content = f.read()
    
    # Extract feature sections
    sections = content.split("## Feature: ")
    for section in sections[1:]:
        lines = section.split("\n")
        feature_line = lines[0].strip()
        feature_name = feature_line.split("(")[0].strip().lower()
        if feature_name not in db: db[feature_name] = {}
        
        for line in lines[1:]:
            if "|" in line and "::" in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 5:
                    attr_name = parts[0].lower()
                    mib_field = parts[1]
                    oid = parts[2]
                    syntax = parts[3]
                    access = parts[4]
                    
                    db[feature_name][attr_name] = {
                        "oid": oid,
                        "syntax": syntax,
                        "access": access
                    }
    return db

def validate_v26_yaml(path, schema_db, report):
    with open(path, "r") as f:
        try:
            data = yaml.safe_load(f)
        except Exception as e:
            report["errors"].append(f"YAML Parse Error in {os.path.basename(path)}: {str(e)}")
            return
    
    if not data: return
    feature_name = data.get("feature", "").lower()
    
    # 1. Feature check
    if feature_name not in schema_db:
        report["missing_features"].append(feature_name)
        return
        
    # 2. Schema terminology check
    schemas = data.get("schemas", {})
    for s_name in schemas:
        if s_name.startswith("get_"):
            report["terminology_violations"].append(f"{feature_name}: Schema '{s_name}' uses legacy 'get_' prefix")
    
    attrs = data.get("attributes", {})
    for attr_name, definition in attrs.items():
        if not isinstance(definition, dict): continue
        
        clean_attr = attr_name.lower()
        if clean_attr not in schema_db[feature_name]:
            # This is expected for some auto-gen features that haven't been manually curated
            # report["missing_attributes"].append(f"{feature_name}.{attr_name}")
            continue
            
        schema_meta = schema_db[feature_name][clean_attr]
        
        # 3. Syntax consistency
        if definition.get("syntax") != schema_meta["syntax"]:
            report["syntax_mismatches"].append({
                "target": f"{feature_name}.{attr_name}",
                "yaml": definition.get("syntax"),
                "schema": schema_meta["syntax"]
            })
            
        # 4. Access consistency
        yaml_access = definition.get("access", "r").lower()
        schema_access = schema_meta["access"].lower()
        if yaml_access != schema_access:
             report["access_mismatches"].append({
                "target": f"{feature_name}.{attr_name}",
                "yaml": yaml_access,
                "schema": schema_access
            })
            
        # 5. Terminology & Minimalism check in sources
        sources = definition.get("sources", {})
        for proto, src_def in sources.items():
            if not isinstance(src_def, dict): continue
            
            # Terminology: 'get' is forbidden
            if "get" in src_def:
                report["terminology_violations"].append(f"{feature_name}.{attr_name}.{proto}: Source uses legacy 'get' key")
            
            # Minimalism: if ru/crud, 'write' should usually be omitted in Wire YAML
            if yaml_access in ("ru", "crud") and "write" in src_def:
                 report["minimalism_warnings"].append(f"{feature_name}.{attr_name}.{proto}: 'write' block exists despite 'access: {yaml_access}'")

def run_validation():
    print(f"Starting v2.6 Compliance Validation...")
    schema_db = load_schema_db()
    print(f"Loaded {len(schema_db)} features from master schema.")
    
    report = {
        "errors": [],
        "missing_features": [],
        "missing_attributes": [],
        "syntax_mismatches": [],
        "access_mismatches": [],
        "terminology_violations": [],
        "minimalism_warnings": []
    }
    
    count = 0
    for fname in os.listdir(WEBUI_FEATURES):
        if not fname.endswith(".yaml"): continue
        validate_v26_yaml(os.path.join(WEBUI_FEATURES, fname), schema_db, report)
        count += 1
        
    print(f"Validated {count} Wire YAMLs.")
    print("\n--- v2.6 COMPLIANCE REPORT ---")
    print(f"Errors (Parse/IO):          {len(report['errors'])}")
    print(f"Features Missing in Schema: {len(report['missing_features'])}")
    print(f"Terminology Violations:     {len(report['terminology_violations'])}")
    print(f"Minimalism Warnings:        {len(report['minimalism_warnings'])}")
    print(f"Syntax Mismatches:          {len(report['syntax_mismatches'])}")
    print(f"Access Mismatches:          {len(report['access_mismatches'])}")
    
    if report["terminology_violations"]:
        print("\nSample Terminology Violations:")
        for v in report["terminology_violations"][:5]: print(f"  {v}")

    if report["syntax_mismatches"]:
        print("\nSample Syntax Mismatches (showing first 5):")
        for m in report["syntax_mismatches"][:5]:
            print(f"  {m['target']}: YAML='{m['yaml']}' vs Schema='{m['schema']}'")

if __name__ == "__main__":
    run_validation()
