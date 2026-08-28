"""
generate_protocols.py — Protocol reference generator for crude-engine.

Produces docs/PROTOCOLS.md from transport_registry.py + protocol YAMLs.
Covers connection, configuration, execute methods, and coverage counts.
Wire-level detail lives in API_REFERENCE.md — not duplicated here.

Usage:
    python3 generate_protocols.py
"""
import os
import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.join(BASE_DIR, '../../crude_engine')
SCHEMAS_DIR = os.path.join(PACKAGE_DIR, 'schemas')
WIRE_DIR = os.path.join(PACKAGE_DIR, 'wire')
DRIVERS_DIR = os.path.join(PACKAGE_DIR, 'drivers')
OUTPUT_FILE = os.path.join(BASE_DIR, '../../docs/PROTOCOLS.md')


def load_registry():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "registry", os.path.join(PACKAGE_DIR, 'transport_registry.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.PROTOCOLS, mod.DEFAULT_PREFERENCE


def load_yaml(path):
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return None


def count_coverage(protocols):
    """Count wire attrs and schema methods per protocol."""
    overlay_dirs = {}
    for proto, cfg in protocols.items():
        if 'wire_overlay_dir' in cfg:
            overlay_dirs[proto] = cfg['wire_overlay_dir']

    active = [p for p in protocols if p != 'offline']
    wire_counts = {p: 0 for p in active}
    total_attrs = 0

    # Wire attrs
    for wf in sorted(os.listdir(WIRE_DIR)):
        if not wf.endswith('.yaml') or not os.path.isfile(os.path.join(WIRE_DIR, wf)):
            continue
        base = load_yaml(os.path.join(WIRE_DIR, wf))
        if not base:
            continue
        for attr_def in base.get('attributes', {}).values():
            if not isinstance(attr_def, dict):
                continue
            total_attrs += 1
            for p in active:
                if p in attr_def.get('sources', {}):
                    wire_counts[p] += 1

    for proto, overlay_dir in overlay_dirs.items():
        overlay_path = os.path.join(WIRE_DIR, overlay_dir)
        if not os.path.isdir(overlay_path):
            continue
        for wf in os.listdir(overlay_path):
            if not wf.endswith('.yaml'):
                continue
            overlay = load_yaml(os.path.join(overlay_path, wf))
            if not overlay:
                continue
            for attr_def in overlay.get('attributes', {}).values():
                if isinstance(attr_def, dict) and proto in attr_def.get('sources', {}):
                    wire_counts[proto] += 1

    # Schema methods
    method_counts = {p: 0 for p in active}
    total_methods = 0
    for sf in sorted(os.listdir(SCHEMAS_DIR)):
        if not sf.endswith('.yaml'):
            continue
        schema = load_yaml(os.path.join(SCHEMAS_DIR, sf))
        if not schema:
            continue
        feature = sf.replace('.yaml', '')
        attrs = schema.get('attributes', {})
        for m_def in schema.get('methods', {}).values():
            if not isinstance(m_def, dict):
                continue
            total_methods += 1
            for p in active:
                for attr_def in attrs.values():
                    if not isinstance(attr_def, dict):
                        continue
                    wire_file = attr_def.get('source', feature)
                    wire_attr = attr_def.get('wire', '')
                    base = load_yaml(os.path.join(WIRE_DIR, f"{wire_file}.yaml"))
                    if base:
                        wa = base.get('attributes', {}).get(wire_attr, {})
                        if p in wa.get('sources', {}):
                            method_counts[p] += 1
                            break
                    if p in overlay_dirs:
                        ov = load_yaml(os.path.join(WIRE_DIR, overlay_dirs[p], f"{wire_file}.yaml"))
                        if ov:
                            wa = ov.get('attributes', {}).get(wire_attr, {})
                            if p in wa.get('sources', {}):
                                method_counts[p] += 1
                                break

    return wire_counts, total_attrs, method_counts, total_methods


def generate():
    protocols, default_pref = load_registry()
    active = [p for p in protocols if p != 'offline']

    doc = ['# Protocol Reference\n']
    doc.append('Auto-generated from `transport_registry.py` + protocol YAMLs. '
               'Per-attribute wire sources are in [API_REFERENCE.md](API_REFERENCE.md).\n')

    # ── Connection ───────────────────────────────────────────────
    doc.append('## Connection\n')
    doc.append(f'**Default order:** {" > ".join(p.upper() for p in default_pref)}')
    doc.append('')
    doc.append('```python')
    doc.append('# Use default order (MOPS > SNMP > SSH)')
    doc.append('device = driver("192.168.1.4", "admin", "private")')
    doc.append('')
    doc.append('# Force specific protocol')
    doc.append('device = driver("192.168.1.4", "admin", "private",')
    doc.append('                optional_args={"protocol": "snmp"})')
    doc.append('')
    doc.append('# Offline (config XML file)')
    doc.append('device = driver("config.xml", "", "")')
    doc.append('```\n')

    doc.append('| Protocol | Transport | Port | Port Override |')
    doc.append('| :--- | :--- | :--- | :--- |')
    for proto in active:
        cfg = protocols[proto]
        port = cfg.get('default_port', '—')
        port_key = cfg.get('port_key', '—')
        engine = cfg.get('engine_protocol', proto)
        ttype = {'mops': 'HTTPS', 'snmp': 'UDP/SNMPv3', 'ssh': 'TCP/SSH'}.get(engine, '—')
        doc.append(f'| **{proto.upper()}** | {ttype} | {port} | `{port_key}` |')
    if 'offline' in protocols:
        doc.append('| **OFFLINE** | XML file | — | — |')
    doc.append('')

    # ── Per-protocol sections ────────────────────────────────────
    for proto in active:
        cfg = protocols[proto]
        yaml_name = cfg.get('protocol_yaml')
        proto_yaml = load_yaml(os.path.join(DRIVERS_DIR, yaml_name)) if yaml_name else {}
        if not proto_yaml:
            continue

        doc.append(f'---\n')
        doc.append(f'## {proto.upper()}\n')
        doc.append(f'Protocol YAML: `drivers/{yaml_name}`\n')

        # Index encodings
        idx_enc = proto_yaml.get('index_encodings', {})
        if idx_enc:
            doc.append('**Index encodings:**')
            for idx_type, idx_def in idx_enc.items():
                fmt = idx_def.get('format', '—') if isinstance(idx_def, dict) else idx_def
                doc.append(f'- `{idx_type}` → `{fmt}`')
            doc.append('')

        # Create method
        create_default = proto_yaml.get('create_method_default')
        if create_default:
            doc.append(f'**Create method:** `{create_default}`\n')

        # Execute methods
        execute = proto_yaml.get('execute_methods', [])
        if execute:
            doc.append(f'**Execute methods ({len(execute)}):** '
                       f'{", ".join(f"`{m}()`" for m in execute)}\n')

        # Protocol-specific config
        defaults = proto_yaml.get('defaults', {})
        specific_keys = {}
        for key in ('method', 'decode_strings', 'parser', 'cmd_verify',
                    'column_overflow', 'scalar_suffix'):
            val = proto_yaml.get(key) or defaults.get(key)
            if val is not None:
                specific_keys[key] = val
        sentinels = proto_yaml.get('empty_table_sentinels') or defaults.get('empty_table_sentinels')
        if sentinels:
            specific_keys['empty_table_sentinels'] = sentinels
        unsigned = proto_yaml.get('unsigned_syntaxes')
        if unsigned:
            specific_keys['unsigned_syntaxes'] = f'{len(unsigned)} types'

        if specific_keys:
            doc.append('**Configuration:**')
            for k, v in specific_keys.items():
                doc.append(f'- `{k}`: `{v}`')
            doc.append('')

    # ── Offline ──────────────────────────────────────────────────
    if 'offline' in protocols:
        cfg = protocols['offline']
        doc.append('---\n')
        doc.append('## OFFLINE\n')
        doc.append('Config XML file acts as a device. Uses MOPS engine protocol '
                   'internally. Auto-detected when hostname ends with `.xml`.\n')

    # ── Wire overlays ────────────────────────────────────────────
    overlay_dirs = {p: cfg['wire_overlay_dir'] for p, cfg in protocols.items()
                    if 'wire_overlay_dir' in cfg}
    if overlay_dirs:
        doc.append('---\n')
        doc.append('## Wire Overlays\n')
        for proto, overlay_dir in overlay_dirs.items():
            overlay_path = os.path.join(WIRE_DIR, overlay_dir)
            if os.path.isdir(overlay_path):
                count = len([f for f in os.listdir(overlay_path) if f.endswith('.yaml')])
                doc.append(f'- **{proto.upper()}**: `wire/{overlay_dir}/` '
                           f'({count} overlay files)')
        doc.append('')

    # ── Coverage ─────────────────────────────────────────────────
    wire_counts, total_wire, method_counts, total_methods = count_coverage(protocols)

    doc.append('---\n')
    doc.append('## Coverage\n')
    doc.append('| Protocol | Wire Attrs | Methods | Method % |')
    doc.append('| :--- | :--- | :--- | :--- |')
    for p in active:
        wc = wire_counts.get(p, 0)
        mc = method_counts.get(p, 0)
        pct = f'{mc / total_methods * 100:.0f}%' if total_methods else '0%'
        doc.append(f'| {p.upper()} | {wc} / {total_wire} | {mc} / {total_methods} | {pct} |')
    doc.append('')

    output = '\n'.join(doc)
    with open(OUTPUT_FILE, 'w') as f:
        f.write(output)
    print(f'Generated: {OUTPUT_FILE} ({len(active)} protocols)')


if __name__ == '__main__':
    generate()
