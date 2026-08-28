"""
generate_method_ref.py — Quick method reference generator for crude-engine.

Produces a scannable one-line-per-method reference from schema YAMLs +
protocol YAMLs (execute methods). E is the union of execute_methods keys
across every drivers/*.yaml (same source as check_catalogue.execute_methods).

Usage:
    python3 generate_method_ref.py
"""
import os
import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.join(BASE_DIR, '../../crude_engine')
SCHEMAS_DIR = os.path.join(PACKAGE_DIR, 'schemas')
DRIVERS_DIR = os.path.join(PACKAGE_DIR, 'drivers')
OUTPUT_FILE = os.path.join(BASE_DIR, '../../docs/METHOD_REFERENCE.md')

TYPE_LABELS = {
    'dict': 'Read', 'list': 'Read', 'list_append': 'Read',
    'upsert': 'Update', 'create': 'Create', 'delete': 'Delete',
}


def load_yaml(path):
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return None


def generate():
    # E is the union of execute_methods keys across every drivers/*.yaml
    # (same source of truth as scripts/check_catalogue.py execute_methods()).
    # Protocol labels come from each YAML's protocol: field when present.
    execute_methods = {}
    if os.path.isdir(DRIVERS_DIR):
        for fname in sorted(os.listdir(DRIVERS_DIR)):
            if not fname.endswith(".yaml"):
                continue
            proto_yaml = load_yaml(os.path.join(DRIVERS_DIR, fname))
            if not isinstance(proto_yaml, dict):
                continue
            proto = proto_yaml.get("protocol") or fname.replace(".yaml", "")
            label = str(proto).upper()
            for m in proto_yaml.get("execute_methods") or []:
                if m not in execute_methods:
                    execute_methods[m] = []
                if label not in execute_methods[m]:
                    execute_methods[m].append(label)

    # Collect schema methods
    schema_files = sorted(f for f in os.listdir(SCHEMAS_DIR) if f.endswith('.yaml'))

    doc = ['# Method Quick Reference\n']
    doc.append('Auto-generated from schema + protocol YAMLs. '
               'For full detail including per-protocol sources, '
               'see [API_REFERENCE.md](API_REFERENCE.md).\n')

    schema_count = 0
    method_count = 0

    for sf in schema_files:
        schema = load_yaml(os.path.join(SCHEMAS_DIR, sf))
        if not schema:
            continue
        feature = sf.replace('.yaml', '')
        desc = schema.get('description', '')
        methods = schema.get('methods', {})
        if not methods:
            continue

        schema_count += 1
        doc.append(f'## {feature}')
        if desc:
            doc.append(f'_{desc}_\n')

        for method_name, m_def in methods.items():
            if not isinstance(m_def, dict):
                continue
            m_type = m_def.get('type', 'read')
            label = TYPE_LABELS.get(m_type, m_type)
            defaults = m_def.get('defaults', {})
            pk = m_def.get('primary_key')
            required = m_def.get('required', [])

            line = f'- **`{method_name}()`** \u2014 {label}'
            if pk:
                line += f', keyed by `{pk}`'
            if required:
                line += f', requires: {", ".join(f"`{r}`" for r in required)}'
            doc.append(line)

            if defaults:
                keys = ', '.join(f'`{k}`' for k in defaults.keys())
                doc.append(f'  Returns: {keys}')

            method_count += 1

        doc.append('')

    # Execute methods section
    if execute_methods:
        doc.append('## Transport Execute Methods')
        doc.append('_Operations declared in protocol YAMLs — '
                   'connection, config, staging, CLI._\n')
        for method, protos in sorted(execute_methods.items()):
            line = f'- **`{method}()`** \u2014 Execute ({", ".join(protos)})'
            if method == "cli":
                # check_catalogue.check_cli needles: escape hatch / unbounded / undeclared capability
                line += "; unbounded escape hatch (undeclared capability)"
            doc.append(line)
            method_count += 1
        doc.append('')

    # Insert summary after header
    doc.insert(2, f'**{method_count} methods** '
               f'({method_count - len(execute_methods)}C/R/U/D + '
               f'{len(execute_methods)}E) across '
               f'**{schema_count} features**\n')

    output = '\n'.join(doc)
    with open(OUTPUT_FILE, 'w') as f:
        f.write(output)
    print(f'Generated: {OUTPUT_FILE} ({method_count} methods, {schema_count} features)')


if __name__ == '__main__':
    generate()
