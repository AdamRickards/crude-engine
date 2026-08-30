"""Read-only schema→wire integrity audit.

Retargeted from leftover napalm-hios-v2 / napalm_hios paths to this
repo's crude_engine/{wire,schemas}. Does not mutate YAML.
Live schema law is validate_schemas.py (CI). This is an extra
broken-link / duplicate-OID walk, not a live doc generator.
"""
import os
import yaml
import json
from collections import defaultdict

# Default paths — this repo's crude_engine/ (not napalm-hios-v2)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.join(BASE_DIR, "../../crude_engine")
WIRE_DIR = os.path.join(PACKAGE_DIR, "wire")
SCHEMA_DIR = os.path.join(PACKAGE_DIR, "schemas")

def run_validation(wire_path=WIRE_DIR, schema_path=SCHEMA_DIR):
    print(f"Starting v2.6 Multi-Stage Validation...")
    print(f"  Wire Folder:   {wire_path}")
    print(f"  Schema Folder: {schema_path}\n")

    errors = {
        "broken_links": [],
        "missing_attributes": [],
        "duplicate_oids": defaultdict(list),
        "malformed_sources": []
    }

    # 1. Index the Wire
    wire_db = {}
    oid_index = defaultdict(list)
    
    for fname in os.listdir(wire_path):
        if not fname.endswith(".yaml"): continue
        w_id = fname.replace(".yaml", "")
        w_full = os.path.join(wire_path, fname)
        with open(w_full, "r") as f:
            try:
                data = yaml.safe_load(f)
                wire_db[w_id] = data
                for attr, attr_def in data.get("attributes", {}).items():
                    # Check OID duplicates
                    snmp_oid = attr_def.get("sources", {}).get("snmp", {}).get("read", {}).get("oid")
                    if snmp_oid and snmp_oid != "N/A":
                        oid_index[snmp_oid].append(f"{w_id}::{attr}")
                    
                    # Check source integrity
                    sources = attr_def.get("sources", {})
                    if not sources or ("snmp" not in sources and "mops" not in sources):
                        errors["malformed_sources"].append(f"{w_id}::{attr} (No physical source defined)")
            except Exception as e:
                print(f"  [!] Failed to parse {fname}: {str(e)}")

    # 2. Audit Schemas
    for fname in os.listdir(schema_path):
        if not fname.endswith(".yaml"): continue
        s_full = os.path.join(schema_path, fname)
        with open(s_full, "r") as f:
            try:
                s_data = yaml.safe_load(f)
                if not s_data or "attributes" not in s_data: continue
                
                for h_attr, a_map in s_data["attributes"].items():
                    w_id = a_map.get("source")
                    w_attr = a_map.get("wire")
                    
                    if w_id not in wire_db:
                        errors["broken_links"].append(f"{fname}: {h_attr} -> {w_id}.yaml (Wire File Not Found)")
                        continue
                    
                    if w_attr not in wire_db[w_id].get("attributes", {}):
                        errors["missing_attributes"].append(f"{fname}: {h_attr} -> {w_id}.yaml::{w_attr} (Attribute Not Found)")
            except: continue

    # 3. Finalize Duplicate OIDs
    duplicates = {oid: sources for oid, sources in oid_index.items() if len(sources) > 1}

    # --- Print Report ---
    print("--- VALIDATION REPORT ---")
    print(f"Broken Wire Links:      {len(errors['broken_links'])}")
    print(f"Missing Wire Attributes: {len(errors['missing_attributes'])}")
    print(f"Duplicate OIDs Found:   {len(duplicates)}")
    print(f"Malformed Sources:      {len(errors['malformed_sources'])}\n")

    if errors["broken_links"]:
        print("[!] Broken Links (Schema -> Wire File):")
        for m in errors["broken_links"][:10]: print(f"  - {m}")
        if len(errors["broken_links"]) > 10: print("    ...")

    if errors["missing_attributes"]:
        print("\n[!] Missing Attributes (Schema -> Wire Field):")
        for m in sorted(errors["missing_attributes"])[:10]: print(f"  - {m}")
        if len(errors["missing_attributes"]) > 10: print("    ...")

    if duplicates:
        print("\n[!] Duplicate OIDs (Multiple YAMLs pointing to same OID):")
        # Filter out common ones like bridge address if needed, but show for now
        for oid, sources in list(duplicates.items())[:5]:
            print(f"  - {oid}: {', '.join(sources)}")
        if len(duplicates) > 5: print("    ...")

    if errors["malformed_sources"]:
        print("\n[!] Malformed Sources (No SNMP/MOPS definition):")
        for m in errors["malformed_sources"][:10]: print(f"  - {m}")

    success = not (errors["broken_links"] or errors["missing_attributes"] or errors["malformed_sources"])
    print(f"\nFinal Result: {'PASSED' if success else 'FAILED'}")
    return success

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--wire", default=WIRE_DIR)
    parser.add_argument("--schema", default=SCHEMA_DIR)
    args = parser.parse_args()
    
    run_validation(args.wire, args.schema)
