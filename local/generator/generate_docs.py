"""
generate_docs.py — Registry-driven API reference generator for crude-engine.

Reads transport_registry.py for protocol discovery, schema YAMLs for methods,
wire YAMLs for attribute sources. Produces a single self-contained markdown
reference organized by feature → method → return schema → per-protocol sources.
"""
import os
import json
import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.join(BASE_DIR, '../../crude_engine')
SCHEMAS_DIR = os.path.join(PACKAGE_DIR, 'schemas')
WIRE_DIR = os.path.join(PACKAGE_DIR, 'wire')
DRIVERS_DIR = os.path.join(PACKAGE_DIR, 'drivers')
OUTPUT_FILE = os.path.join(BASE_DIR, '../../docs/API_REFERENCE.md')

TYPE_LABELS = {
    'read': 'Read', 'dict': 'Read', 'upsert': 'Update',
    'create': 'Create', 'delete': 'Delete', 'execute': 'Execute',
}


def load_registry():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "registry", os.path.join(PACKAGE_DIR, 'transport_registry.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return {k: v for k, v in mod.PROTOCOLS.items() if k != 'offline'}


def load_yaml(path):
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return None


def execute_methods():
    """E is drivers/*.yaml execute_methods keys, never schema type: fields."""
    names = set()
    if not os.path.isdir(DRIVERS_DIR):
        return []
    for fname in sorted(os.listdir(DRIVERS_DIR)):
        if not fname.endswith(".yaml"):
            continue
        data = load_yaml(os.path.join(DRIVERS_DIR, fname))
        if not isinstance(data, dict):
            continue
        for name in data.get("execute_methods") or []:
            names.add(name)
    return sorted(names)


def get_wire_attribute(wire_file, attr_name, overlay_dirs):
    base = load_yaml(os.path.join(WIRE_DIR, f"{wire_file}.yaml"))
    attr = base.get('attributes', {}).get(attr_name, {}) if base else {}
    for proto, overlay_dir in overlay_dirs.items():
        overlay = load_yaml(os.path.join(WIRE_DIR, overlay_dir, f"{wire_file}.yaml"))
        if not overlay:
            continue
        ov_attr = overlay.get('attributes', {}).get(attr_name, {})
        if ov_attr and proto in ov_attr.get('sources', {}):
            if 'sources' not in attr:
                attr['sources'] = {}
            attr['sources'][proto] = ov_attr['sources'][proto]
    return attr


def format_wire_meta(wire_data):
    """Format wire-level metadata: syntax, access, validation."""
    parts = []
    syntax = wire_data.get('syntax', '')
    if syntax:
        parts.append(syntax)
    access = wire_data.get('access', '')
    if access:
        parts.append(f"access={access}")
    val = wire_data.get('validation', {})
    if val:
        if 'allowed' in val:
            parts.append(f"allowed={val['allowed']}")
        elif 'min' in val or 'max' in val:
            parts.append(f"range={val.get('min', '')}\u2013{val.get('max', '')}")
    return f"  # {', '.join(parts)}" if parts else ""


def format_source_block(proto_label, sources_by_attr, engine_proto, wire_data_by_attr):
    """Build a code-block-style source listing for one protocol."""
    lines = []
    for attr_name, src in sources_by_attr.items():
        wire_data = wire_data_by_attr.get(attr_name, {})
        meta = format_wire_meta(wire_data)

        if engine_proto == 'snmp':
            read = src.get('read', {})
            oid = read.get('oid', '')
            method = read.get('method', 'walk')
            write_oid = src.get('write', {}).get('oid', '')
            parts = [f"oid: {oid}"]
            if method != 'walk':
                parts.append(f"method: {method}")
            if write_oid and write_oid != oid:
                parts.append(f"write_oid: {write_oid}")
            lines.append(f"  {attr_name}: {{{', '.join(parts)}}}{meta}")
        elif engine_proto == 'mops':
            read = src.get('read', src)
            mib = read.get('mib', '')
            table = read.get('table', '')
            field = read.get('field', '')
            lines.append(f"  {attr_name}: {{{mib} / {table}.{field}}}{meta}")
        elif engine_proto == 'ssh':
            read_cmd = src.get('read', {}).get('command', '')
            write_cmd = (src.get('write', {}).get('command')
                         or src.get('create', {}).get('command', ''))
            parts = []
            if read_cmd:
                parts.append(f"read: \"{read_cmd}\"")
            if write_cmd:
                parts.append(f"write: \"{write_cmd}\"")
            lines.append(f"  {attr_name}: {{{', '.join(parts)}}}{meta}")
        else:
            lines.append(f"  {attr_name}: {src}{meta}")
    return lines


def build_method_scope(schema, method_def):
    defaults = method_def.get('defaults', {})
    sub_tables = method_def.get('sub_tables', {})
    required = method_def.get('required', [])
    primary_key = method_def.get('primary_key')
    index_fields = method_def.get('index_fields', [])

    scope = set(defaults.keys()) if defaults else set()
    for r in required:
        scope.add(r)
    if primary_key:
        scope.add(primary_key)
    for f in index_fields:
        scope.add(f.get('field', '') if isinstance(f, dict) else f)
    for sub_def in sub_tables.values():
        for attr_name in sub_def.get('field_map', {}).values():
            scope.add(attr_name)
        sub_pk = sub_def.get('primary_key')
        if sub_pk:
            scope.add(sub_pk)
    if not scope:
        scope = set(schema.get('attributes', {}).keys())
    return scope


def build_return_schema(method_def, schema_attrs, wire_attrs):
    """Build a dict showing the return shape — schema-level types only.

    Wire-level validation and MIB syntax belong in the source blocks,
    not here. CRUDE matrix bridges the gap between schema and wire types.
    """
    defaults = method_def.get('defaults', {})
    if not defaults:
        return None

    result = {}
    for field, default in defaults.items():
        attr_def = schema_attrs.get(field, {})

        # Annotation from Python type of the default value
        annotation = type(default).__name__
        if isinstance(attr_def, dict):
            vm = attr_def.get('value_map')
            if isinstance(vm, dict):
                annotation = " | ".join(f'"{v}"' for v in vm.values())
            elif isinstance(vm, str):
                annotation = f"{annotation} (via {vm})"
            if attr_def.get('compute'):
                annotation += " (computed)"

        if isinstance(default, dict):
            result[field] = f"{{...}}  // {annotation}"
        elif isinstance(default, list):
            result[field] = f"[...]  // {annotation}"
        elif isinstance(default, bool):
            result[field] = f"{default}  // {annotation}"
        elif isinstance(default, (int, float)):
            result[field] = f"{default}  // {annotation}"
        elif isinstance(default, str):
            result[field] = f'"{default}"  // {annotation}'
        else:
            result[field] = f"{default}  // {annotation}"

    return result


def generate():
    registry = load_registry()
    protocols = list(registry.keys())
    proto_labels = {p: p.upper() for p in protocols}

    overlay_dirs = {}
    for proto, cfg in registry.items():
        if 'wire_overlay_dir' in cfg:
            overlay_dirs[proto] = cfg['wire_overlay_dir']

    proto_yamls = {}
    for proto, cfg in registry.items():
        yaml_name = cfg.get('protocol_yaml')
        if yaml_name:
            proto_yamls[proto] = load_yaml(os.path.join(DRIVERS_DIR, yaml_name))

    schema_files = sorted([f for f in os.listdir(SCHEMAS_DIR) if f.endswith('.yaml')])

    # ── Pass 1: gather ───────────────────────────────────────────────
    features = []
    total_methods = {'read': 0, 'upsert': 0, 'create': 0, 'delete': 0}

    for sf in schema_files:
        feature_name = sf.replace('.yaml', '')
        schema = load_yaml(os.path.join(SCHEMAS_DIR, sf))
        if not schema:
            continue

        wire_attrs = {}
        for attr_name, attr_def in schema.get('attributes', {}).items():
            wire_file = attr_def.get('source', feature_name)
            wire_attr = attr_def.get('wire', attr_name)
            wire_attrs[attr_name] = {
                'schema_def': attr_def,
                'wire_data': get_wire_attribute(wire_file, wire_attr, overlay_dirs),
                'wire_file': wire_file,
                'wire_attr': wire_attr,
            }

        methods_info = []
        for method_name, m_def in schema.get('methods', {}).items():
            m_type = m_def.get('type', 'read')
            count_type = 'read' if m_type in ('dict', 'read') else m_type
            # E is protocol YAML execute_methods, never schema type:
            if count_type != 'execute':
                total_methods[count_type] = total_methods.get(count_type, 0) + 1

            scope = build_method_scope(schema, m_def)

            method_protos = {p: False for p in protocols}
            scoped_attrs = []
            for attr_name in scope:
                if attr_name not in wire_attrs:
                    continue
                wa = wire_attrs[attr_name]
                sources = wa['wire_data'].get('sources', {})
                for p in protocols:
                    if p in sources:
                        method_protos[p] = True
                scoped_attrs.append(attr_name)

            methods_info.append({
                'name': method_name,
                'def': m_def,
                'type': m_type,
                'type_label': TYPE_LABELS.get(m_type, m_type),
                'protos': method_protos,
                'scope': scope,
                'scoped_attrs': scoped_attrs,
            })

        features.append({
            'name': feature_name,
            'description': schema.get('description', ''),
            'schema': schema,
            'wire_attrs': wire_attrs,
            'methods': methods_info,
        })

    # ── Pass 2: generate ─────────────────────────────────────────────
    doc = []
    doc.append("# crude-engine API Reference\n")
    doc.append("Automatically generated from schema, wire, and protocol YAMLs.\n")

    e_names = execute_methods()
    e_count = len(e_names)
    total = sum(total_methods.values()) + e_count
    doc.append(f"**{len(features)} features** | **{total} methods** "
               f"({total_methods.get('create', 0)}C "
               f"{total_methods.get('read', 0)}R "
               f"{total_methods.get('upsert', 0)}U "
               f"{total_methods.get('delete', 0)}D "
               f"{e_count}E) | "
               f"**Protocols:** {', '.join(proto_labels[p] for p in protocols)}\n")

    # ── Table of Contents ────────────────────────────────────────────
    doc.append("## Table of Contents\n")
    for feat in features:
        method_list = []
        for m in feat['methods']:
            proto_str = "/".join(
                proto_labels[p] for p in protocols if m['protos'][p])
            # No wire sources: honest label is Composed, not fake MOPS/SNMP/SSH.
            # check_catalogue.protocols_none fails `(..., None)` without Derived/Composed.
            if not proto_str:
                proto_str = "Composed"
            method_list.append(f"`{m['name']}` ({m['type_label']}, {proto_str})")
        doc.append(f"- **[{feat['name']}](#{feat['name']})** \u2014 {', '.join(method_list)}")
    doc.append("")

    # ── Transport Operations ─────────────────────────────────────────
    doc.append("---\n")
    doc.append("## Transport Operations\n")
    doc.append("Operational methods declared in protocol YAMLs.\n")

    for proto in protocols:
        py = proto_yamls.get(proto)
        if not py:
            continue
        proto_execute = py.get('execute_methods', [])
        if not proto_execute:
            continue
        names = []
        for m in proto_execute:
            if m == "cli":
                # check_catalogue.check_cli needles: escape hatch / unbounded / undeclared capability
                names.append("`cli()` (unbounded escape hatch \u2014 undeclared capability)")
            else:
                names.append(f"`{m}()`")
        doc.append(f"**{proto_labels[proto]}:** " + ", ".join(names))
    doc.append("")

    # ── Per-Feature Sections ─────────────────────────────────────────
    doc.append("---\n")

    for feat in features:
        doc.append(f"## {feat['name']}\n")
        if feat['description']:
            doc.append(f"_{feat['description']}_\n")

        for mi in feat['methods']:
            m_def = mi['def']
            proto_tags = [proto_labels[p] for p in protocols if mi['protos'][p]]

            doc.append(f"### `{mi['name']}()`\n")
            # Empty proto_tags = no direct wire protocol. Label Composed so
            # **Protocols:** None is not unlabelled (check_catalogue --composed).
            if proto_tags:
                proto_line = ", ".join(proto_tags)
            else:
                proto_line = "None (Composed)"
            doc.append(f"**{mi['type_label']}** | **Protocols:** {proto_line}")

            # Required / primary key / key map
            meta = []
            required = m_def.get('required', [])
            if required:
                meta.append(f"Required: {', '.join(f'`{r}`' for r in required)}")
            pk = m_def.get('primary_key')
            if pk:
                meta.append(f"Primary key: `{pk}`")
            km = m_def.get('key_map')
            if km:
                meta.append(f"Key map: `{km}`")
            if meta:
                doc.append(" | ".join(meta))

            # Linked tables
            linked = m_def.get('linked_tables', [])
            if linked:
                doc.append("\n**Linked tables:** "
                           + ", ".join(f"`{lt.get('row_status')}`" for lt in linked))

            # Return schema as pseudo-code block
            return_schema = build_return_schema(
                m_def, feat['schema'].get('attributes', {}), feat['wire_attrs'])
            if return_schema:
                doc.append("\n```")
                doc.append(f"{mi['name']}() -> {{")
                for field, annotation in return_schema.items():
                    doc.append(f"    {field}: {annotation}")
                doc.append("}")
                doc.append("```\n")

            # Sub-tables
            sub_tables = m_def.get('sub_tables', {})
            if sub_tables:
                for sub_key, sub_def in sub_tables.items():
                    sub_pk = sub_def.get('primary_key', '')
                    sub_km = sub_def.get('key_map', '')
                    detail = ""
                    if sub_pk:
                        detail = f" \u2014 key: `{sub_pk}`"
                    if sub_km:
                        detail += f", map: `{sub_km}`"
                    doc.append(f"> Sub-table: **`{sub_key}`**{detail}")

            # Per-protocol source blocks
            for proto in protocols:
                if not mi['protos'][proto]:
                    continue
                engine_proto = registry[proto].get('engine_protocol', proto)

                # Collect sources and wire data for scoped attrs
                sources_by_attr = {}
                wire_data_by_attr = {}
                for attr_name in mi['scoped_attrs']:
                    wa = feat['wire_attrs'].get(attr_name)
                    if not wa:
                        continue
                    wire_data = wa['wire_data']
                    sources = wire_data.get('sources', {})
                    if proto in sources:
                        sources_by_attr[attr_name] = sources[proto]
                        wire_data_by_attr[attr_name] = wire_data

                if not sources_by_attr:
                    continue

                lines = format_source_block(
                    proto_labels[proto], sources_by_attr, engine_proto,
                    wire_data_by_attr)
                doc.append(f"\n<details><summary>{proto_labels[proto]} sources "
                           f"({len(sources_by_attr)}/{len(mi['scoped_attrs'])} attrs)"
                           f"</summary>\n")
                doc.append("```")
                doc.append(f"{proto_labels[proto]} {{")
                doc.extend(lines)
                doc.append("}")
                doc.append("```")
                doc.append("</details>")

            doc.append("")

        doc.append("---\n")

    output = "\n".join(doc)
    with open(OUTPUT_FILE, 'w') as f:
        f.write(output)
    print(f"Generated: {OUTPUT_FILE} ({len(output):,} bytes, {len(features)} features)")


if __name__ == "__main__":
    generate()
