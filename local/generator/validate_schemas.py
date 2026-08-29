"""
validate_schemas.py — Schema compliance validator for crude-engine.

Validates all schema YAMLs against the formal spec in docs/SCHEMA_MODEL.md.
Produces structural errors (must fix) and canonical shape warnings (reshaping hitlist).

Usage:
    python3 validate_schemas.py              # full report
    python3 validate_schemas.py --errors     # structural errors only
    python3 validate_schemas.py --canonical  # canonical shape warnings only
    python3 validate_schemas.py --json       # machine-readable output
"""
import os
import sys
import json
import yaml
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.join(BASE_DIR, '../../crude_engine')
SCHEMAS_DIR = os.path.join(PACKAGE_DIR, 'schemas')
WIRE_DIR = os.path.join(PACKAGE_DIR, 'wire')

# ── Valid keys per level ─────────────────────────────────────────────

VALID_TOP_KEYS = {'version', 'feature', 'description', 'methods', 'attributes', 'debug'}

VALID_METHOD_KEYS = {
    'type', 'defaults', 'primary_key', 'key_map', 'index_fields',
    'index_type',
    'sub_tables', 'row_status', 'index_key', 'required', 'fields',
    'index_filter', 'linked_tables', 'attributes', 'schema',
}

VALID_SUB_TABLE_KEYS = {
    'primary_key', 'field_map', 'defaults', 'key_map', 'child_key',
}

VALID_ATTR_KEYS = {
    'wire', 'source', 'access', 'value_map', 'compute', 'lookup',
    'membership_of', 'collect', 'regex', 'set_format', 'index_filter',
    'key_map',
}

VALID_METHOD_TYPES = {'dict', 'list', 'list_append', 'upsert', 'create', 'delete'}

READ_TYPES = {'dict', 'list', 'list_append'}
WRITE_TYPES = {'upsert', 'create', 'delete'}

# ── NAPALM-shaped key detection ──────────────────────────────────────

NAPALM_KEYS = {
    'is_up', 'is_enabled', 'last_flapped',
    'remote_hostname', 'remote_port', 'remote_port_description',
    'remote_chassis_id', 'remote_system_name', 'remote_system_description',
    'remote_system_capab', 'remote_system_enable_capab',
    'active', 'static', 'moves', 'last_move',
    'physical_channels', 'physical_values',
}

NAPALM_STANDARD_METHODS = {
    'get_facts', 'get_interfaces', 'get_interfaces_ip',
    'get_interfaces_counters', 'get_lldp_neighbors',
    'get_lldp_neighbors_detail', 'get_mac_address_table',
    'get_arp_table', 'get_ntp_servers', 'get_ntp_stats',
    'get_users', 'get_snmp_information', 'get_optics',
    'get_config', 'get_environment', 'get_vlans',
    'get_route_to', 'get_ipv6_neighbors_table',
}

# Keys that are NAPALM-standard but also MIB-canonical (acceptable)
CANONICAL_NAPALM_KEYS = {
    'hostname', 'vendor', 'model', 'serial_number', 'os_version',
    'uptime', 'interface_list', 'mac', 'interface', 'vlan', 'age',
    'destination', 'protocol', 'next_hop', 'preference',
    'contact', 'location', 'chassis_id',
    'username', 'level', 'password',
    'temperature', 'fans', 'power', 'cpu', 'memory',
}


def load_yaml(path):
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return None


def load_overlays():
    """Discover wire overlay directories."""
    overlay_dirs = {}
    ssh_dir = os.path.join(WIRE_DIR, 'ssh')
    if os.path.isdir(ssh_dir):
        overlay_dirs['ssh'] = 'ssh'
    return overlay_dirs


def wire_exists(wire_file, wire_attr, overlay_dirs):
    """Check if a wire attribute exists in base or overlay."""
    base = load_yaml(os.path.join(WIRE_DIR, f"{wire_file}.yaml"))
    if base and wire_attr in base.get('attributes', {}):
        return True
    for proto, overlay_dir in overlay_dirs.items():
        overlay = load_yaml(os.path.join(WIRE_DIR, overlay_dir, f"{wire_file}.yaml"))
        if overlay and wire_attr in overlay.get('attributes', {}):
            return True
    return False



def resolve_method_def(method_name, methods, errors, seen=None):
    """Follow schema: aliases to the concrete method definition."""
    m_def = methods.get(method_name)
    if not isinstance(m_def, dict):
        return m_def
    alias = m_def.get('schema')
    if not alias:
        return m_def
    seen = set() if seen is None else seen
    if method_name in seen:
        errors.append(f"Method '{method_name}': circular schema alias")
        return None
    if alias not in methods:
        errors.append(
            f"Method '{method_name}': schema alias '{alias}' not found")
        return None
    seen.add(method_name)
    target = resolve_method_def(alias, methods, errors, seen)
    if not isinstance(target, dict):
        return None
    resolved = dict(target)
    for k, v in m_def.items():
        if k != 'schema':
            resolved[k] = v
    return resolved


def _crud_pair_name(method_name, m_type):
    """create_foo <-> delete_foo share one table's row addressing."""
    if not isinstance(method_name, str):
        return None
    if m_type == 'delete' and method_name.startswith('delete_'):
        return 'create_' + method_name[len('delete_'):]
    if m_type == 'create' and method_name.startswith('create_'):
        return 'delete_' + method_name[len('create_'):]
    return None


def crud_declares_index(m_def):
    """True if a CRUD method declares row addressing.

    SCHEMA_MODEL CRUD table: index_key MUST — "Index field for row addressing".
    The same declaration also exists as:
    - index_fields: RFC 2578 compound index (SCHEMA_MODEL / SCHEMA_PRIMITIVES)
    - linked_tables: multi-table CRUD (same alternative this validator
      already uses for the sibling MUST row_status)
    - required: SCHEMA_PRIMITIVES — "required fields for create — checked
      for index derivation"
    """
    if not isinstance(m_def, dict):
        return False
    ik = m_def.get('index_key')
    if isinstance(ik, str) and ik:
        return True
    ifs = m_def.get('index_fields')
    if isinstance(ifs, list) and ifs:
        return True
    linked = m_def.get('linked_tables')
    if isinstance(linked, list) and linked:
        return True
    req = m_def.get('required')
    if isinstance(req, list) and req:
        return True
    return False


def check_crud_index_key(method_name, m_def, methods, errors):
    """SCHEMA_MODEL: type create/delete — index_key MUST."""
    m_type = m_def.get('type')
    if m_type not in ('create', 'delete'):
        return
    if crud_declares_index(m_def):
        return
    pair = _crud_pair_name(method_name, m_type)
    pair_def = methods.get(pair) if pair else None
    if isinstance(pair_def, dict) and pair_def.get('schema'):
        pair_def = resolve_method_def(pair, methods, errors)
    if crud_declares_index(pair_def):
        return
    errors.append(
        f"Method '{method_name}': {m_type} method missing 'index_key' "
        f"(MUST per SCHEMA_MODEL)")


def merged_attr(name, attributes, method_attrs):
    """Catalog attr overlaid by method-scoped attributes (_load_method)."""
    base = attributes.get(name) if isinstance(attributes, dict) else None
    over = method_attrs.get(name) if isinstance(method_attrs, dict) else None
    if isinstance(base, dict) and isinstance(over, dict):
        merged = dict(base)
        merged.update(over)
        return merged
    if isinstance(over, dict):
        return over
    if isinstance(base, dict):
        return base
    return None


def setter_attr_names(m_def, attributes):
    """Attribute names this write method actually writes.

    SCHEMA_MODEL: fields restricts writable attrs; empty/missing = all attrs
    (upsert). create/delete write required + defaults + row_status +
    index_key + linked_tables fields. Method-scoped attributes always count.
    """
    names = set()
    if not isinstance(m_def, dict):
        return names
    m_type = m_def.get('type')
    fields = m_def.get('fields')
    method_attrs = m_def.get('attributes') if isinstance(
        m_def.get('attributes'), dict) else {}
    if isinstance(fields, list) and fields:
        names.update(fields)
    elif m_type == 'upsert':
        if isinstance(attributes, dict):
            names.update(attributes.keys())
    else:
        req = m_def.get('required')
        if isinstance(req, list):
            names.update(req)
        defaults = m_def.get('defaults')
        if isinstance(defaults, dict):
            names.update(defaults.keys())
        rs = m_def.get('row_status')
        if isinstance(rs, str) and rs:
            names.add(rs)
        ik = m_def.get('index_key')
        if isinstance(ik, str) and ik:
            names.add(ik)
        linked = m_def.get('linked_tables')
        if isinstance(linked, list):
            for lt in linked:
                if not isinstance(lt, dict):
                    continue
                lrs = lt.get('row_status')
                if isinstance(lrs, str) and lrs:
                    names.add(lrs)
                lf = lt.get('fields')
                if isinstance(lf, list):
                    names.update(lf)
    names.update(method_attrs.keys())
    return names


def check_setter_wire_source(method_name, m_def, attributes, errors):
    """SCHEMA_MODEL: wire + source MUST for setter attrs.

    Principle 4: compute-only MAY omit. Empty dicts are index-only.
    index_key / index_fields names are row addressing (value_map remaps
    allowed without a device column).
    """
    if m_def.get('type') not in WRITE_TYPES:
        return
    method_attrs = m_def.get('attributes') if isinstance(
        m_def.get('attributes'), dict) else {}
    names = setter_attr_names(m_def, attributes)
    index_names = set()
    ik = m_def.get('index_key')
    if isinstance(ik, str) and ik:
        index_names.add(ik)
    ifs = m_def.get('index_fields')
    if isinstance(ifs, list):
        index_names.update(x for x in ifs if isinstance(x, str))
    for attr_name in sorted(names):
        if attr_name in index_names:
            continue
        attr_def = merged_attr(attr_name, attributes, method_attrs)
        if not isinstance(attr_def, dict):
            continue
        if not attr_def:
            continue  # empty {} — index-only
        if attr_def.get('compute') and not attr_def.get('wire'):
            continue  # compute-only MAY omit
        wire = attr_def.get('wire')
        source = attr_def.get('source')
        if not wire or not source:
            missing = []
            if not wire:
                missing.append('wire')
            if not source:
                missing.append('source')
            errors.append(
                f"Method '{method_name}': setter attr '{attr_name}' missing "
                f"{' and '.join(missing)} (MUST per SCHEMA_MODEL)")



def validate_schema(filename, schema, overlay_dirs):
    """Validate one schema. Returns (errors, warnings)."""
    errors = []
    warnings = []
    feature = filename.replace('.yaml', '')

    # ── Top-level keys ───────────────────────────────────────────
    unknown_top = set(schema.keys()) - VALID_TOP_KEYS
    if unknown_top:
        errors.append(f"Unknown top-level keys: {unknown_top}")

    for req in ('version', 'feature', 'methods', 'attributes'):
        if req not in schema:
            errors.append(f"Missing required top-level key: {req}")

    if 'description' not in schema:
        warnings.append("Missing recommended key: description")

    methods = schema.get('methods', {})
    attributes = schema.get('attributes', {})

    if not isinstance(methods, dict):
        errors.append("'methods' must be a dict")
        return errors, warnings
    if not isinstance(attributes, dict):
        errors.append("'attributes' must be a dict")
        return errors, warnings

    # ── Attribute validation ─────────────────────────────────────
    for attr_name, attr_def in attributes.items():
        if not isinstance(attr_def, dict):
            continue  # empty attrs ({}) are valid — index-only fields

        unknown_attr = set(attr_def.keys()) - VALID_ATTR_KEYS
        if unknown_attr:
            errors.append(f"Attribute '{attr_name}': unknown keys {unknown_attr}")

        # Compute.from references
        compute = attr_def.get('compute')
        if isinstance(compute, dict):
            from_list = compute.get('from', [])
            if isinstance(from_list, list):
                for ref in from_list:
                    if ref not in attributes:
                        errors.append(
                            f"Attribute '{attr_name}': compute.from "
                            f"references '{ref}' which doesn't exist")

        # Lookup.from references
        lookup = attr_def.get('lookup')
        if isinstance(lookup, dict):
            from_ref = lookup.get('from')
            if isinstance(from_ref, str) and from_ref not in attributes:
                errors.append(
                    f"Attribute '{attr_name}': lookup.from "
                    f"references '{from_ref}' which doesn't exist")

    # ── Method validation ────────────────────────────────────────
    for method_name, m_def in methods.items():
        if not isinstance(m_def, dict):
            errors.append(f"Method '{method_name}': definition must be a dict")
            continue

        unknown_method = set(m_def.keys()) - VALID_METHOD_KEYS
        if unknown_method:
            errors.append(f"Method '{method_name}': unknown keys {unknown_method}")

        if m_def.get('schema'):
            m_def = resolve_method_def(method_name, methods, errors)
            if not isinstance(m_def, dict):
                continue

        m_type = m_def.get('type')
        if not m_type:
            errors.append(f"Method '{method_name}': missing 'type'")
            continue
        if m_type not in VALID_METHOD_TYPES:
            errors.append(f"Method '{method_name}': invalid type '{m_type}'")

        # Read methods must have defaults
        if m_type in READ_TYPES:
            if 'defaults' not in m_def:
                errors.append(f"Method '{method_name}': read method missing 'defaults'")

            # Table methods must have primary_key
            defaults = m_def.get('defaults', {})
            if isinstance(defaults, dict) and any(
                isinstance(v, dict) for v in defaults.values()
            ):
                # Has nested dicts — might be sub_table, not necessarily primary_key
                pass
            # primary_key required if key_map is present
            if m_def.get('key_map') and not m_def.get('primary_key'):
                errors.append(
                    f"Method '{method_name}': has key_map but no primary_key")

        # CRUD methods must have row_status + index_key
        if m_type == 'create':
            if 'row_status' not in m_def and 'linked_tables' not in m_def:
                errors.append(
                    f"Method '{method_name}': create method needs "
                    f"'row_status' or 'linked_tables'")

        if m_type == 'delete':
            if 'row_status' not in m_def and 'linked_tables' not in m_def:
                errors.append(
                    f"Method '{method_name}': delete method needs "
                    f"'row_status' or 'linked_tables'")

        # SCHEMA_MODEL CRUD: index_key MUST ("Index field for row addressing")
        check_crud_index_key(method_name, m_def, methods, errors)

        # SCHEMA_MODEL: wire + source MUST for setter attrs
        check_setter_wire_source(method_name, m_def, attributes, errors)

        # Sub-table validation
        sub_tables = m_def.get('sub_tables', {})
        if isinstance(sub_tables, dict):
            for sub_name, sub_def in sub_tables.items():
                if not isinstance(sub_def, dict):
                    errors.append(
                        f"Method '{method_name}': sub_table "
                        f"'{sub_name}' must be a dict")
                    continue

                unknown_sub = set(sub_def.keys()) - VALID_SUB_TABLE_KEYS
                if unknown_sub:
                    errors.append(
                        f"Method '{method_name}': sub_table "
                        f"'{sub_name}' unknown keys {unknown_sub}")

                if 'primary_key' not in sub_def:
                    errors.append(
                        f"Method '{method_name}': sub_table "
                        f"'{sub_name}' missing primary_key")

                # field_map targets must exist in attributes
                field_map = sub_def.get('field_map', {})
                if isinstance(field_map, dict):
                    for output_name, attr_ref in field_map.items():
                        if attr_ref not in attributes:
                            errors.append(
                                f"Method '{method_name}': sub_table "
                                f"'{sub_name}' field_map target "
                                f"'{attr_ref}' not in attributes")

        # Linked tables validation
        linked = m_def.get('linked_tables', [])
        if isinstance(linked, list):
            for lt in linked:
                if not isinstance(lt, dict):
                    continue
                rs = lt.get('row_status')
                if rs and rs not in attributes:
                    errors.append(
                        f"Method '{method_name}': linked_tables "
                        f"row_status '{rs}' not in attributes")

        # ── Canonical shape checks ───────────────────────────────
        if m_type in READ_TYPES:
            defaults = m_def.get('defaults', {})
            if isinstance(defaults, dict):
                napalm_shaped = set(defaults.keys()) & NAPALM_KEYS
                # Filter out keys that are also MIB-canonical
                contorted = napalm_shaped - CANONICAL_NAPALM_KEYS
                if contorted and method_name in NAPALM_STANDARD_METHODS:
                    warnings.append(
                        f"Method '{method_name}': NAPALM-shaped keys "
                        f"{sorted(contorted)} — reshaping needed")
                elif contorted:
                    warnings.append(
                        f"Method '{method_name}': NAPALM-convention keys "
                        f"{sorted(contorted)} on non-NAPALM method")

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Schema compliance validator")
    parser.add_argument('--errors', action='store_true',
                        help="Show structural errors only")
    parser.add_argument('--canonical', action='store_true',
                        help="Show canonical shape warnings only")
    parser.add_argument('--json', action='store_true',
                        help="Machine-readable JSON output")
    args = parser.parse_args()

    overlay_dirs = load_overlays()
    schema_files = sorted(f for f in os.listdir(SCHEMAS_DIR) if f.endswith('.yaml'))

    results = {}
    total_errors = 0
    total_warnings = 0

    for sf in schema_files:
        schema = load_yaml(os.path.join(SCHEMAS_DIR, sf))
        if not schema:
            results[sf] = {'errors': [f"Failed to load {sf}"], 'warnings': []}
            total_errors += 1
            continue

        errors, warnings = validate_schema(sf, schema, overlay_dirs)
        results[sf] = {'errors': errors, 'warnings': warnings}
        total_errors += len(errors)
        total_warnings += len(warnings)

    if args.json:
        print(json.dumps(results, indent=2))
        sys.exit(1 if total_errors else 0)

    # ── Report ───────────────────────────────────────────────────
    compliant = sum(1 for r in results.values()
                    if not r['errors'] and not r['warnings'])

    print(f"Schema Compliance Report")
    print(f"{'=' * 60}")
    print(f"{len(schema_files)} schemas | {compliant} compliant | "
          f"{total_errors} errors | {total_warnings} warnings\n")

    if not args.canonical:
        error_schemas = {sf: r for sf, r in results.items() if r['errors']}
        if error_schemas:
            print("STRUCTURAL ERRORS (must fix)")
            print("-" * 40)
            for sf, r in sorted(error_schemas.items()):
                print(f"\n  {sf}:")
                for e in r['errors']:
                    print(f"    ERROR: {e}")
        elif not args.errors:
            print("No structural errors.\n")

    if not args.errors:
        warn_schemas = {sf: r for sf, r in results.items() if r['warnings']}
        if warn_schemas:
            print("\nCANONICAL SHAPE WARNINGS (reshaping hitlist)")
            print("-" * 40)
            for sf, r in sorted(warn_schemas.items()):
                print(f"\n  {sf}:")
                for w in r['warnings']:
                    print(f"    WARN: {w}")
        elif not args.canonical:
            print("No canonical shape warnings.\n")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Compliant: {compliant}/{len(schema_files)}")
    if total_errors:
        print(f"Errors: {total_errors} (must fix)")
    if total_warnings:
        print(f"Warnings: {total_warnings} (reshaping hitlist for consumers)")

    sys.exit(1 if total_errors else 0)


if __name__ == "__main__":
    main()
