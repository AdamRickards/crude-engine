#!/usr/bin/env python3
"""v2.9 Getter Validation Suite — schema contract, types, cross-protocol consistency.

For each schema, for each read method, for each protocol, for each device:
  1. CONTRACT: Does the output match schema defaults? (keys present, correct shape)
  2. TYPES: Are value types correct per defaults?
  3. PARITY: Cross-protocol consistency (same data, different transport)

Protocols without wire sources for a method are silently skipped (not failures).

Usage:
    python3 audit_getters_v2.py --fleet                    # full gate check
    python3 audit_getters_v2.py 192.168.1.4                # single device, all protocols
    python3 audit_getters_v2.py 192.168.1.4 --protocol mops  # single protocol
    python3 audit_getters_v2.py --fleet -o results.json    # save results
"""
import argparse
import json
import sys
import time
import os
import yaml
from collections import OrderedDict

def load_exemptions():
    """Load wire_exemptions.yaml — attrs that are legitimately unavailable per protocol."""
    path = os.path.join(os.path.dirname(__file__), 'wire_exemptions.yaml')
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        data = yaml.safe_load(f) or {}
    # Build lookup: (wire_file, wire_attr, protocol) → True
    exempt = {}
    for key, protocols in data.get('exemptions', {}).items():
        parts = key.split(':', 1)
        if len(parts) == 2:
            for proto in protocols:
                exempt[(parts[0], parts[1], proto)] = True
    return exempt

WIRE_EXEMPTIONS = load_exemptions()

FLEET = [
    ('192.168.1.254', 'GRS1042'),
    ('192.168.1.4', 'BRS50'),
    ('192.168.60.80', 'BRS50-RM'),
    ('192.168.60.83', 'GRS105'),
    ('192.168.60.85', 'BRS50-L2S'),
]

ALL_PROTOCOLS = ['mops', 'snmp', 'ssh']

# Fields that change between calls — excluded from parity value comparison
TIMING_FIELDS = {
    'uptime', 'age', 'last_flapped', 'last_move', 'when',
    'utilization', 'tx_octets', 'rx_octets',
    'tx_errors', 'rx_errors', 'tx_discards', 'rx_discards',
    'tx_unicast_packets', 'rx_unicast_packets',
    'tx_multicast_packets', 'rx_multicast_packets',
    'tx_broadcast_packets', 'rx_broadcast_packets',
    'fragments', 'crc_errors', 'collisions', 'late_collisions',
    'checksum_errors', 'version_errors', 'vrid_errors',
    'humidity', 'temperature',
}


def load_schemas():
    """Load all schema YAMLs — method defaults + protocol support per method."""
    schema_dir = os.path.join(os.path.dirname(__file__), '..', 'crude_engine', 'schemas')
    wire_dir = os.path.join(os.path.dirname(__file__), '..', 'crude_engine', 'wire')
    schemas = {}

    for sf in sorted(os.listdir(schema_dir)):
        if not sf.endswith('.yaml'):
            continue
        with open(os.path.join(schema_dir, sf)) as f:
            schema = yaml.safe_load(f) or {}

        feature = sf.replace('.yaml', '')
        attrs = schema.get('attributes', {})

        for method_name, m_def in schema.get('methods', {}).items():
            if not isinstance(m_def, dict):
                continue
            # Resolve schema references
            if 'schema' in m_def:
                ref = m_def['schema']
                ref_def = schema.get('methods', {}).get(ref, {})
                if isinstance(ref_def, dict):
                    m_def = {**ref_def, **{k: v for k, v in m_def.items() if k != 'schema'}}

            m_type = m_def.get('type', 'dict')
            if m_type not in ('dict', 'list', 'list_append'):
                continue

            # Determine which protocols support this method
            # A protocol supports this method if ANY non-exempt attr has a wire source for it
            supported_protocols = set()
            for attr_name, attr_def in attrs.items():
                if not isinstance(attr_def, dict):
                    continue
                wire_file = attr_def.get('source', feature)
                wire_attr = attr_def.get('wire', '')
                if not wire_file or not wire_attr:
                    continue
                # Check base wire
                wire_path = os.path.join(wire_dir, f'{wire_file}.yaml')
                if os.path.exists(wire_path):
                    with open(wire_path) as f:
                        wire = yaml.safe_load(f) or {}
                    wa = wire.get('attributes', {}).get(wire_attr, {})
                    for p in ALL_PROTOCOLS:
                        if (wire_file, wire_attr, p) in WIRE_EXEMPTIONS:
                            continue
                        if p in wa.get('sources', {}):
                            supported_protocols.add(p)
                # Check SSH overlay
                ssh_path = os.path.join(wire_dir, 'ssh', f'{wire_file}.yaml')
                if os.path.exists(ssh_path):
                    if (wire_file, wire_attr, 'ssh') in WIRE_EXEMPTIONS:
                        continue
                    with open(ssh_path) as f:
                        wire = yaml.safe_load(f) or {}
                    wa = wire.get('attributes', {}).get(wire_attr, {})
                    if 'ssh' in wa.get('sources', {}):
                        supported_protocols.add('ssh')

            schemas[method_name] = {
                'defaults': m_def.get('defaults', {}),
                'type': m_type,
                'primary_key': m_def.get('primary_key'),
                'sub_tables': m_def.get('sub_tables', {}),
                'feature': feature,
                'protocols': supported_protocols,
            }

    return schemas


def check_contract(method_name, result, schema):
    """Level 1: Does output match schema defaults contract?"""
    errors = []
    defaults = schema['defaults']
    m_type = schema['type']
    pk = schema.get('primary_key')

    if not isinstance(result, dict):
        if m_type in ('list', 'list_append'):
            # list types may return dict in engine — check for list-of-dicts
            pass
        errors.append(f'expected dict, got {type(result).__name__}')
        return errors

    if pk:
        # Table output — check first row has all defaults keys
        if result:
            first_key = next(iter(result))
            first_val = result[first_key]
            if isinstance(first_val, dict):
                missing = set()
                for k in defaults:
                    if isinstance(defaults[k], dict):
                        continue  # sub_table placeholder
                    if k not in first_val:
                        missing.add(k)
                if missing:
                    errors.append(f'row [{first_key}] missing keys: {sorted(missing)}')
            elif isinstance(first_val, list) and first_val:
                # list_append: dict of lists
                if isinstance(first_val[0], dict):
                    missing = set()
                    for k in defaults:
                        if isinstance(defaults[k], dict):
                            continue
                        if k not in first_val[0]:
                            missing.add(k)
                    if missing:
                        errors.append(f'row [{first_key}][0] missing keys: {sorted(missing)}')
    else:
        # Flat dict — all defaults keys present
        missing = set()
        for k in defaults:
            if isinstance(defaults[k], dict):
                continue
            if k not in result:
                missing.add(k)
        if missing:
            errors.append(f'missing keys: {sorted(missing)}')

    return errors


def check_types(method_name, result, schema):
    """Level 2: Are value types correct per defaults?"""
    errors = []
    defaults = schema['defaults']
    pk = schema.get('primary_key')

    def check_row(row, label):
        for key, default_val in defaults.items():
            if key not in row or isinstance(default_val, (dict, list)):
                continue
            actual = row[key]
            if actual is None:
                continue
            expected_type = type(default_val)
            if expected_type in (int, float) and isinstance(actual, (int, float)):
                continue
            if not isinstance(actual, expected_type):
                errors.append(
                    f'{label}.{key}: expected {expected_type.__name__}, '
                    f'got {type(actual).__name__} = {repr(actual)[:40]}')

    if not isinstance(result, dict):
        return errors

    if pk and result:
        first_key = next(iter(result))
        first_val = result[first_key]
        if isinstance(first_val, dict):
            check_row(first_val, f'[{first_key}]')
        elif isinstance(first_val, list) and first_val and isinstance(first_val[0], dict):
            check_row(first_val[0], f'[{first_key}][0]')
    elif not pk:
        check_row(result, 'top')

    return errors


def check_parity(method_name, results_by_proto, schema):
    """Level 3: Cross-protocol consistency."""
    errors = []
    protos = list(results_by_proto.keys())
    if len(protos) < 2:
        return errors

    defaults = schema['defaults']
    pk = schema.get('primary_key')

    # Compare entry counts (allow SSH to have fewer)
    counts = {}
    for proto, result in results_by_proto.items():
        if isinstance(result, dict):
            counts[proto] = len(result)
        else:
            counts[proto] = 0

    # Flag count mismatch between MOPS and SNMP
    mops_count = counts.get('mops')
    snmp_count = counts.get('snmp')
    if mops_count is not None and snmp_count is not None:
        if mops_count != snmp_count:
            errors.append(f'entry count: mops={mops_count} vs snmp={snmp_count}')

    # For flat dicts, compare non-timing values between MOPS and SNMP
    if not pk:
        for pa, pb in [('mops', 'snmp'), ('mops', 'ssh'), ('snmp', 'ssh')]:
            if pa not in results_by_proto or pb not in results_by_proto:
                continue
            a = results_by_proto[pa]
            b = results_by_proto[pb]
            if not isinstance(a, dict) or not isinstance(b, dict):
                continue
            for key in defaults:
                if key in TIMING_FIELDS or isinstance(defaults[key], (dict, list)):
                    continue
                va = a.get(key)
                vb = b.get(key)
                if va != vb and va is not None and vb is not None:
                    # SSH returning defaults/empty is expected gap, not parity failure
                    if pb == 'ssh' and (vb == defaults.get(key) or vb == '' or vb == 0 or vb is False):
                        continue
                    if pa == 'ssh' and (va == defaults.get(key) or va == '' or va == 0 or va is False):
                        continue
                    errors.append(f'{pa} vs {pb}: {key} = {repr(va)[:30]} vs {repr(vb)[:30]}')

    return errors


def run_one_read(device, method, schema):
    """Run a single read method against an already-open device.

    Returns a cell dict with status, time_ms, contract, types, error, result.
    Caller is responsible for opening/closing the device and for the protocol-
    support check (`schema['protocols']` membership).

    Used by audit_getters_v2's own run_device() and by tests/release_matrix.py.
    """
    entry = {'status': 'ok', 'contract': [], 'types': [], 'time_ms': 0}

    t0 = time.monotonic()
    try:
        fn = getattr(device, method)
        try:
            result = fn(napalm_compat=False)
        except TypeError:
            result = fn()
    except Exception as e:
        entry['status'] = 'error'
        entry['error'] = str(e)[:200]
        return entry
    entry['time_ms'] = round((time.monotonic() - t0) * 1000)

    if isinstance(result, tuple):
        result = result[0]

    entry['result'] = result
    entry['contract'] = check_contract(method, result, schema)
    entry['types'] = check_types(method, result, schema)

    if entry['contract'] or entry['types']:
        entry['status'] = 'fail'

    return entry


def run_device(host, username, password, protocols, schemas):
    """Run audit on one device across specified protocols."""
    from napalm import get_network_driver

    device_results = OrderedDict()

    for proto in protocols:
        driver = get_network_driver('hios')
        try:
            device = driver(host, username, password,
                            optional_args={'protocol': proto})
            device.open()
        except Exception as e:
            device_results[proto] = {'_connection': f'FAILED: {e}'}
            continue

        proto_results = OrderedDict()
        for method, schema in schemas.items():
            # Skip if this protocol doesn't support this method
            if proto not in schema['protocols']:
                proto_results[method] = {'status': 'skip', 'reason': 'no wire source'}
                continue
            proto_results[method] = run_one_read(device, method, schema)

        device.close()
        device_results[proto] = proto_results

    return device_results


def print_report(all_results, schemas):
    """Print report and return failure count."""
    total_pass = 0
    total_fail = 0
    total_error = 0
    total_skip = 0
    all_parity_errors = 0

    for device_label, proto_results in all_results.items():
        print(f'\n{"=" * 70}')
        print(f'{device_label}')
        print(f'{"=" * 70}')

        device_data = {}  # proto → {method → result} for parity

        for proto, results in proto_results.items():
            if '_connection' in results:
                print(f'\n  {proto.upper()}: {results["_connection"]}')
                continue

            pass_count = 0
            fail_count = 0
            error_count = 0
            skip_count = 0
            failures = []

            for method, entry in results.items():
                status = entry['status']
                if status == 'skip':
                    skip_count += 1
                    total_skip += 1
                elif status == 'ok':
                    pass_count += 1
                    total_pass += 1
                elif status == 'error':
                    error_count += 1
                    total_error += 1
                    failures.append((method, entry))
                else:
                    fail_count += 1
                    total_fail += 1
                    failures.append((method, entry))

            print(f'\n  {proto.upper()}: {pass_count} pass, {fail_count} fail, '
                  f'{error_count} error, {skip_count} skip')

            for method, entry in failures:
                time_ms = entry.get('time_ms', 0)
                if entry['status'] == 'error':
                    print(f'    {method:40s} ERROR  {entry.get("error", "")[:60]}')
                else:
                    print(f'    {method:40s} FAIL   {time_ms:5d}ms')
                    for e in entry.get('contract', []):
                        print(f'      CONTRACT: {e}')
                    for e in entry.get('types', []):
                        print(f'      TYPE: {e}')

            # Collect for parity
            device_data[proto] = {
                m: e.get('result') for m, e in results.items()
                if e.get('status') == 'ok' and 'result' in e
            }

        # Parity check
        protos_with_data = {p: r for p, r in device_data.items() if r}
        if len(protos_with_data) >= 2:
            parity_fails = 0
            parity_methods = 0
            parity_details = []

            for method, schema in schemas.items():
                method_results = {}
                for proto, results in protos_with_data.items():
                    if method in results and results[method] is not None:
                        method_results[proto] = results[method]
                if len(method_results) >= 2:
                    parity_methods += 1
                    errs = check_parity(method, method_results, schema)
                    if errs:
                        parity_fails += 1
                        parity_details.append((method, errs))

            print(f'\n  PARITY: {parity_methods - parity_fails}/{parity_methods} consistent')
            for method, errs in parity_details:
                print(f'    {method:40s} DIFF')
                for e in errs:
                    print(f'      {e}')
            all_parity_errors += parity_fails

    # Summary
    total = total_pass + total_fail + total_error
    print(f'\n{"=" * 70}')
    print(f'GATE CHECK: {total_pass} pass, {total_fail} fail, '
          f'{total_error} error, {total_skip} skip ({total} tested)')
    if all_parity_errors:
        print(f'PARITY: {all_parity_errors} cross-protocol differences')
    if total_fail == 0 and total_error == 0 and all_parity_errors == 0:
        print('RESULT: PASS')
    else:
        print('RESULT: FAIL')
    print(f'{"=" * 70}')

    return total_fail + total_error + all_parity_errors


def main():
    parser = argparse.ArgumentParser(description='v2.9 Getter Gate Check')
    parser.add_argument('host', nargs='?', help='Device IP (or use --fleet)')
    parser.add_argument('-u', default='admin', help='Username')
    parser.add_argument('-p', default='private', help='Password')
    parser.add_argument('--protocol', default=None, choices=ALL_PROTOCOLS)
    parser.add_argument('--fleet', action='store_true',
                        help='All fleet devices')
    parser.add_argument('-o', '--output', help='Save results to JSON')
    args = parser.parse_args()

    if not args.host and not args.fleet:
        parser.error('Provide host IP or --fleet')

    schemas = load_schemas()
    print(f'Loaded {len(schemas)} read methods')

    devices = FLEET if args.fleet else [(args.host, args.host)]
    protocols = [args.protocol] if args.protocol else ALL_PROTOCOLS

    all_results = OrderedDict()
    for ip, name in devices:
        label = f'{name} ({ip})'
        print(f'\n--- {label} ---')
        all_results[label] = run_device(ip, args.u, args.p, protocols, schemas)

    failures = print_report(all_results, schemas)

    if args.output:
        save = OrderedDict()
        for dev, protos in all_results.items():
            save[dev] = OrderedDict()
            for proto, results in protos.items():
                if '_connection' in results:
                    save[dev][proto] = results
                    continue
                save[dev][proto] = OrderedDict()
                for method, entry in results.items():
                    save[dev][proto][method] = {k: v for k, v in entry.items() if k != 'result'}
        with open(args.output, 'w') as f:
            json.dump(save, f, indent=2)
        print(f'\nSaved to {args.output}')

    sys.exit(1 if failures else 0)


if __name__ == '__main__':
    main()
