"""Leftover v26/monolith script. Not live law. Do not run.

Hardcoded napalm-hios-v2 / napalm_hios paths from the old monolith.
Kept (not deleted) as archive. Live generators: generate_docs.py,
generate_method_ref.py, generate_protocols.py. Live schema check:
validate_schemas.py. See local/generator/README.md.
"""

import os
import xml.etree.ElementTree as ET
import re

SCHEMA_PATH = "/home/adamr/obsidian-vault/Projects/napalm-hios-v2/docs/napalm-hios-2-6-schema.md"
XML_PATH = "/home/adamr/obsidian-vault/Projects/MOPS_Emulator/data/mops_schema.xml"

def get_mib_data(root):
    mib_db = {}
    for obj in root.findall(".//ObjectType"):
        name = obj.get("name")
        if not name: continue
        desc_node = obj.find("Description")
        desc = desc_node.get("text").replace("\r", " ").replace("\n", " ").strip() if desc_node is not None else ""
        desc = re.sub(r'\s+', ' ', desc)
        # Extract Constraints (Range or Enums)
        constraints = ""
        syntax_node = obj.find("Syntax")
        syntax_name = "Unknown"
        if syntax_node is not None:
            syntax_name = syntax_node.get("name", "Unknown")
            enums = syntax_node.findall("Enumeration")
            if enums:
                constraints = "Enums: [" + ", ".join([f"{e.get('value')}:{e.get('name')}" for e in enums]) + "]"
            else:
                range_node = syntax_node.find("Range")
                if range_node is not None:
                    lv = range_node.get('lowerValue') or range_node.get('value') or "0"
                    uv = range_node.get('upperValue')
                    if uv: constraints = f"Range: {lv}..{uv}"
                    else: constraints = f"Value: {lv}"

                # Fallback: Extract range from description text (e.g. Unsigned32(0..600))
                if not constraints and desc:
                    rm = re.search(r"\((\d+)\.\.(\d+)\)", desc)
                    if rm:
                        constraints = f"Range: {rm.group(1)}..{rm.group(2)}"

        
        # Determine high-fidelity access
        mib_access = obj.get("access", "read-only").lower().replace(" ", "-")
        crud_access = "r"
        
        # RowStatus ALWAYS gets CRUD (Forceful override for automation)
        if syntax_name == "RowStatus":
            crud_access = "crud"
        elif "read-create" in mib_access or "read-write" in mib_access:
            crud_access = "ru"
        elif "write-only" in mib_access:
            crud_access = "u"

        mib_db[name] = {"desc": desc, "const": constraints, "access": crud_access, "syntax": syntax_name}
    return mib_db

def enrich_schema():
    print("Performing Deep Enrichment of 2.6 Schema...")
    tree = ET.parse(XML_PATH); root = tree.getroot(); mib_db = get_mib_data(root)
    with open(SCHEMA_PATH, "r") as f: lines = f.readlines()
    
    new_lines = []
    enriched_count = 0
    for line in lines:
        if "|" in line and "::" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 9:
                mib_field_raw = parts[2]
                if "::" in mib_field_raw:
                    field_name = mib_field_raw.split("::")[-1]
                    if field_name in mib_db:
                        meta = mib_db[field_name]
                        # OVERWRITE with high-fidelity truth
                        if meta["const"]: parts[6] = f" {meta['const']} "
                        if meta["desc"]: parts[9] = f" {meta['desc'][:150]}... "
                        parts[5] = f" {meta['access']} "
                        # Update syntax string if it's currently low-fidelity (e.g. 'INTEGER')
                        if len(parts[4]) < len(meta["syntax"]) or "INTEGER" in parts[4]:
                            parts[4] = f" {meta['syntax']} "
                        
                        line = "|" + "|".join(parts[1:-1]) + "|\n"
                        enriched_count += 1
        new_lines.append(line)
        
    with open(SCHEMA_PATH, "w") as f: f.writelines(new_lines)
    print(f"Enriched {enriched_count} attributes with High-Fidelity truth.")

if __name__ == "__main__":
    enrich_schema()
