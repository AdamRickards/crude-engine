import os
import yaml
import re
from collections import defaultdict

# Paths
BASE_DIR = '/home/adamr/obsidian-vault/Projects/napalm-hios-v2'
SCHEMAS_DIR = os.path.join(BASE_DIR, 'napalm_hios/schemas')
WIRE_DIR = os.path.join(BASE_DIR, 'napalm_hios/wire')
DRIVERS_DIR = os.path.join(BASE_DIR, 'napalm_hios/drivers')
ENGINE_PY = os.path.join(BASE_DIR, 'napalm_hios/engine/interpreter.py')
TRANSFORMS_PY = os.path.join(BASE_DIR, 'napalm_hios/engine/transforms.py')
HIOS_PY = os.path.join(BASE_DIR, 'napalm_hios/hios.py')
ARCH_MD = os.path.join(BASE_DIR, 'docs/ARCHITECTURE.md')
RFC_MD = os.path.join(BASE_DIR, 'docs/RFC_MAPPING.md')
API_REF_MD = os.path.join(BASE_DIR, 'docs/API_REFERENCE.md')
OUTPUT_FILE = os.path.join(BASE_DIR, 'docs/CLAIMS_AUDIT.md')

def load_yaml(path):
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f) or {}
    except: return {}

def get_arch_claims():
    """Extract claims from ARCHITECTURE.md"""
    claims = {'primitives': []}
    if not os.path.exists(ARCH_MD): return claims
    with open(ARCH_MD, 'r') as f:
        content = f.read()
    
    m = re.search(r"(\d+) schema YAMLs", content)
    if m: claims['schema_count'] = int(m.group(1))
    
    m = re.search(r"(\d+) methods", content)
    if m: claims['method_total'] = int(m.group(1))
    
    m = re.search(r"(\d+)C (\d+)R (\d+)U (\d+)D (\d+)E", content)
    if m:
        claims['breakdown'] = {'create': int(m.group(1)), 'read': int(m.group(2)), 'upsert': int(m.group(3)), 'delete': int(m.group(4)), 'execute': int(m.group(5))}
    
    m = re.search(r"([\d,]+) attrs", content)
    if m: claims['attr_count'] = int(m.group(1).replace(',', ''))

    # Execute methods matrix from doc
    methods = []
    table_started = False
    for line in content.split('\n'):
        if "| Method | MOPS | SNMP | SSH |" in line:
            table_started = True; continue
        if table_started and line.startswith('|'):
            if '---' in line: continue
            parts = line.split('|')
            if len(parts) > 1: methods.append(parts[1].strip('` '))
        elif table_started: break
    claims['execute_methods'] = set([m for m in methods if m])

    # Qualitative (Primitives)
    prim_section = False
    for line in content.split('\n'):
        if "**Schema primitives**" in line: prim_section = True; continue
        if prim_section and line.startswith('- `'):
            claims['primitives'].append(line.split('`')[1].replace(':', ''))
        elif prim_section and line.startswith('###'): prim_section = False

    return claims

def method_exists_in_file(file_path, method_name):
    if not os.path.exists(file_path): return False
    with open(file_path, 'r') as f:
        content = f.read()
    return f"def {method_name}(" in content

def audit():
    print("Performing 3-Link Integrity Audit (YAML -> Driver -> Adapter)...")
    claims = get_arch_claims()
    
    results = {
        'schemas': set(),
        'wire_files': 0,
        'attrs_total': 0,
        'methods': defaultdict(set),
        'engine': {},
        'leaks': [],
        'documented': set(),
        'execute': {}
    }

    # 1. Implementation Reality
    for sf in os.listdir(SCHEMAS_DIR):
        if sf.endswith('.yaml'):
            name = sf.replace('.yaml', '')
            results['schemas'].add(name)
            data = load_yaml(os.path.join(SCHEMAS_DIR, sf))
            for m_name, m_def in data.get('methods', {}).items():
                m_type = m_def.get('type', 'read')
                if m_type in ('dict', 'list', 'table'): m_type = 'read'
                results['methods'][m_type].add(m_name)

    for wf in os.listdir(WIRE_DIR):
        if wf.endswith('.yaml'):
            results['wire_files'] += 1
            data = load_yaml(os.path.join(WIRE_DIR, wf))
            results['attrs_total'] += len(data.get('attributes', {}))

    # 2. Engine Capability
    with open(ENGINE_PY, 'r') as f: engine_code = f.read()
    for p in claims['primitives']:
        results['engine'][p] = p in engine_code

    # 3. Execute Integrity Check
    with open(HIOS_PY, 'r') as f: hios_code = f.read()
    
    for proto in ['SSH', 'SNMP', 'MOPS']:
        proto_yaml = load_yaml(os.path.join(DRIVERS_DIR, f"{proto}.yaml"))
        methods = proto_yaml.get('execute_methods', [])
        
        py_file = os.path.join(DRIVERS_DIR, f"{proto.lower()}.py")
        if proto == 'MOPS': py_file = os.path.join(DRIVERS_DIR, "mops_transport.py")
        if proto == 'SNMP': py_file = os.path.join(DRIVERS_DIR, "snmp_transport.py")
        
        results['execute'][proto] = {}
        for m in methods:
            in_driver = method_exists_in_file(py_file, m)
            in_adapter = f"def {m}(" in hios_code
            results['execute'][proto][m] = {'driver': in_driver, 'adapter': in_adapter}

    # 4. REPORT
    doc = "# Architecture Integrity Audit (v2.6)\n\n"
    doc += "> Verifying the **3-Link Chain**: YAML Declaration → Driver Implementation → Adapter Exposure.\n\n"
    
    doc += "## 1. Execute Matrix Integrity\n"
    doc += "Verifies if methods claimed in protocol YAMLs are backed by code.\n\n"
    
    for proto in ['SSH', 'SNMP', 'MOPS']:
        doc += f"### {proto} Operations\n"
        doc += "| Method | In YAML | In Driver Code | In hios.py | Status |\n"
        doc += "| :--- | :---: | :---: | :---: | :--- |\n"
        
        for m, status in results['execute'][proto].items():
            s_drv = "✅" if status['driver'] else "❌ Missing"
            s_adp = "✅" if status['adapter'] else "⚠️ Internal Only"
            final = "🟢 Ready" if status['driver'] and status['adapter'] else "🔴 Broken"
            if status['driver'] and not status['adapter']: final = "🟡 Hidden"
            
            doc += f"| `{m}` | ✅ | {s_drv} | {s_adp} | {final} |\n"
        doc += "\n"

    doc += "## 2. Metric Variances\n"
    doc += "| Metric | Design (Spec) | Reality (Code) | Status |\n"
    doc += "| :--- | :--- | :--- | :--- |\n"
    doc += f"| Schema YAMLs | {claims.get('schema_count', '?')} | {len(results['schemas'])} | {'✅' if claims.get('schema_count') == len(results['schemas']) else '⚠️ Update Spec'} |\n"
    doc += f"| Wire YAMLs | 134 | {results['wire_files']} | {'✅' if results['wire_files'] >= 134 else '❌ Low'} |\n"
    doc += f"| Total Attributes | {claims.get('attr_count', '?')} | {results['attrs_total']} | {'✅' if results['attrs_total'] >= 4058 else '❌ Low'} |\n"
    
    doc += "\n## 3. Claimed Primitives Verification\n"
    doc += "| Primitive | Engine Support | Status |\n"
    doc += "| :--- | :---: | :---: |\n"
    for p in sorted(claims['primitives']):
        doc += f"| `{p}` | {'✅' if results['engine'].get(p) else '❌'} | {'✅' if results['engine'].get(p) else '❌'} |\n"

    with open(OUTPUT_FILE, 'w') as f: f.write(doc)
    print(f"Integrity Audit complete: {OUTPUT_FILE}")

if __name__ == "__main__":
    audit()
