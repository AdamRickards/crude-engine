import os
import yaml
from collections import defaultdict

# Paths
BASE_DIR = '/home/adamr/obsidian-vault/Projects/napalm-hios-v2'
WIRE_DIR = os.path.join(BASE_DIR, 'napalm_hios/wire')
OUTPUT_FILE = os.path.join(BASE_DIR, 'docs/WIRE_INTEGRITY.md')

def load_yaml(path):
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f) or {}
    except: return {}

def audit_wire():
    print("Performing Wire Integrity Audit...")
    
    wire_files = [f for f in os.listdir(WIRE_DIR) if f.endswith('.yaml')]
    
    total_attributes = 0
    attr_map = defaultdict(list) # global name -> [files]
    file_duplicates = defaultdict(list)
    protocol_stats = {'snmp': 0, 'mops': 0, 'ssh': 0}
    
    for wf in sorted(wire_files):
        data = load_yaml(os.path.join(WIRE_DIR, wf))
        attrs = data.get('attributes', {})
        
        seen_in_file = set()
        for name, defn in attrs.items():
            total_attributes += 1
            attr_map[name].append(wf)
            
            # 1. Local duplicate check
            if name in seen_in_file:
                file_duplicates[wf].append(name)
            seen_in_file.add(name)
            
            # 2. Protocol coverage
            sources = defn.get('sources', {})
            for p in ['snmp', 'mops', 'ssh']:
                if p in sources: protocol_stats[p] += 1

    # Generate Report
    doc = "# Wire Integrity Audit\n\n"
    doc += f"- **Total Wire Files:** {len(wire_files)}\n"
    doc += f"- **Total Unique Attributes Found:** {len(attr_map)}\n"
    doc += f"- **Raw Attribute Count (with global overlap):** {total_attributes}\n\n"
    
    doc += "## 1. Protocol Coverage\n"
    doc += "| Protocol | Attributes Supported | % Coverage |\n"
    doc += "| :--- | :--- | :--- |\n"
    for p, count in protocol_stats.items():
        pct = (count / total_attributes) * 100 if total_attributes > 0 else 0
        doc += f"| {p.upper()} | {count} | {pct:.1f}% |\n"
    
    doc += "\n## 2. Duplicate Analysis\n"
    
    # Global overlaps (same attribute name in multiple files)
    global_overlaps = {k: v for k, v in attr_map.items() if len(v) > 1}
    doc += f"### Global Name Overlaps ({len(global_overlaps)})\n"
    doc += "Attributes with the same name across different MIB files.\n\n"
    if global_overlaps:
        doc += "| Attribute Name | Found in Files |\n"
        doc += "| :--- | :--- |\n"
        # Sort by number of occurrences
        sorted_overlaps = sorted(global_overlaps.items(), key=lambda x: len(x[1]), reverse=True)
        for name, files in sorted_overlaps[:20]: # Top 20
            doc += f"| `{name}` | {', '.join(files)} |\n"
        if len(sorted_overlaps) > 20:
            doc += f"| ... and {len(sorted_overlaps)-20} more |\n"
    else:
        doc += "✅ Zero global name overlaps.\n"

    # Internal File Duplicates
    doc += f"\n### Internal File Duplicates ({len(file_duplicates)})\n"
    if file_duplicates:
        doc += "Attributes defined more than once within the same file.\n\n"
        for wf, dups in file_duplicates.items():
            doc += f"- `{wf}`: {', '.join(dups)}\n"
    else:
        doc += "✅ Zero internal file duplicates.\n"

    with open(OUTPUT_FILE, 'w') as f: f.write(doc)
    print(f"Wire Integrity complete: {OUTPUT_FILE}")

if __name__ == "__main__":
    audit_wire()
