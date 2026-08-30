"""Leftover v26/monolith script. Not live law. Do not run.

Hardcoded napalm-hios-v2 / napalm_hios paths from the old monolith.
Kept (not deleted) as archive. Live generators: generate_docs.py,
generate_method_ref.py, generate_protocols.py. Live schema check:
validate_schemas.py. See local/generator/README.md.
"""

import os
import yaml
import xml.etree.ElementTree as ET
from collections import defaultdict

# Paths
BASE_DIR = '/home/adamr/obsidian-vault/Projects/napalm-hios-v2'
LOCAL_UI_DIR = '/home/adamr/obsidian-vault/Projects/LocalUI'
SCHEMAS_DIR = os.path.join(BASE_DIR, 'napalm_hios/schemas')
WIRE_DIR = os.path.join(BASE_DIR, 'napalm_hios/wire')
CAPTURED_DIR = os.path.join(LOCAL_UI_DIR, 'captured')
OUTPUT_FILE = os.path.join(BASE_DIR, 'local/reference/WEB_VS_DRIVER.md')

def load_yaml(path):
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f) or {}
    except: return {}

def normalize_mib(mib):
    return mib.replace('_', '-').lower()

def get_exposed_map():
    """Build map: (mib, table, field) -> [schema_feature.attr]"""
    exposed = {}
    wire_db = {}
    for wf in os.listdir(WIRE_DIR):
        if wf.endswith('.yaml'):
            wire_db[wf.replace('.yaml', '')] = load_yaml(os.path.join(WIRE_DIR, wf))

    schema_files = [f for f in os.listdir(SCHEMAS_DIR) if f.endswith('.yaml')]
    for sf in schema_files:
        feature = sf.replace('.yaml', '')
        data = load_yaml(os.path.join(SCHEMAS_DIR, sf))
        for attr_name, attr_def in data.get('attributes', {}).items():
            source = attr_def.get('source', feature)
            wire = attr_def.get('wire', attr_name)
            
            w_data = wire_db.get(source, {})
            w_attr = w_data.get('attributes', {}).get(wire, {})
            mops = w_attr.get('sources', {}).get('mops', {}).get('read', {})
            
            if mops and 'mib' in mops and 'table' in mops and 'field' in mops:
                key = (normalize_mib(mops['mib']), mops['table'].lower(), mops['field'].lower())
                if key not in exposed: exposed[key] = []
                exposed[key].append(f"{feature}.{attr_name}")
    return exposed

def parse_mops_xml(file_path):
    """Extract all (mib, table, field) tuples from a MOPS XML."""
    found = set()
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        ns = {'m': 'urn:x-mops:1.0'}
        for mib in root.findall('.//m:MIB', ns):
            mib_name = mib.get('name')
            for node in mib.findall('./m:Node', ns):
                table_name = node.get('name')
                for attr in node.findall('.//m:Attribute', ns):
                    field_name = attr.get('name')
                    if mib_name and table_name and field_name:
                        found.add((normalize_mib(mib_name), table_name.lower(), field_name.lower()))
    except: pass
    return found

def audit():
    print("Building exposure map from Schemas...")
    exposed_map = get_exposed_map()
    
    print("Scanning WebUI captures with file-tracing...")
    page_stats = {}
    
    for page_folder in sorted(os.listdir(CAPTURED_DIR)):
        page_path = os.path.join(CAPTURED_DIR, page_folder)
        if not os.path.isdir(page_path): continue
        
        all_attrs_on_page = set()
        attr_to_files = defaultdict(set)
        
        for xml_file in os.listdir(page_path):
            if xml_file.endswith('.xml'):
                attrs = parse_mops_xml(os.path.join(page_path, xml_file))
                for a in attrs:
                    all_attrs_on_page.add(a)
                    attr_to_files[a].add(xml_file)
        
        if not all_attrs_on_page: continue
        
        covered_attrs = [a for a in all_attrs_on_page if a in exposed_map]
        missing_attrs = [a for a in all_attrs_on_page if a not in exposed_map]
        
        page_stats[page_folder] = {
            'total': len(all_attrs_on_page),
            'covered': len(covered_attrs),
            'percent': (len(covered_attrs) / len(all_attrs_on_page)) * 100,
            'attr_to_files': attr_to_files,
            'missing': missing_attrs
        }

    doc = "# WebUI vs Driver Deep Trace Audit\n\n"
    doc += "This audit traces every attribute found in **WebUI XML Captures** back to the driver **Schemas**.\n"
    doc += "Includes file-tracing to show exactly which XML file contains the unexposed data.\n\n"
    
    doc += "## Summary Scorecard\n"
    doc += "| | WebUI Page | Coverage | Exposed / Total |\n"
    doc += "| :--- | :--- | :--- | :--- |\n"
    
    for page, stats in sorted(page_stats.items(), key=lambda x: (x[1]['percent'], x[0]), reverse=True):
        status = "✅" if stats['percent'] == 100 else ("⚠️" if stats['percent'] > 0 else "❌")
        doc += f"| {status} | `{page}` | {stats['percent']:.0f}% | {stats['covered']}/{stats['total']} |\n"

    doc += "\n\n---\n\n## Unexposed Data Breakdown (with Source Files)\n"
    doc += "Ranked by attribute count. Shows exactly which captured XMLs to inspect for new schema attributes.\n\n"
    
    unexposed = [p for p in page_stats.items() if p[1]['percent'] < 100]
    unexposed.sort(key=lambda x: x[1]['total'] - x[1]['covered'], reverse=True)
    
    for page, stats in unexposed[:30]:
        missing = stats['missing']
        if not missing: continue
        
        doc += f"### {page} ({len(missing)} missing / {stats['total']} total)\n"
        
        # Group by MIB for readability
        mibs = defaultdict(list)
        for attr in missing:
            mib, table, field = attr
            files = ", ".join(sorted(list(stats['attr_to_files'][attr])))
            mibs[mib].append(f"`{table}.{field}` <small>(in {files})</small>")
        
        for mib, entries in list(mibs.items())[:8]:
            doc += f"- **{mib.upper()}**\n"
            for entry in entries[:10]:
                doc += f"  - {entry}\n"
            if len(entries) > 10:
                doc += f"  - ... and {len(entries)-10} more fields\n"
        doc += "\n"

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        f.write(doc)
    
    print(f"Deep Trace Audit with file tracing complete: {OUTPUT_FILE}")

if __name__ == "__main__":
    audit()
