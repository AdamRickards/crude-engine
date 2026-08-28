"""Negative tests for SCHEMA_MODEL MUSTs the live tree already satisfies.

ISSUES #7: index_key on create/delete; wire+source on setter attrs.

Usage (from crude-engine root or this directory):
    python3 local/generator/test_validate_musts.py
"""
import os
import sys
import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from validate_schemas import validate_schema  # noqa: E402

FIXTURES = os.path.join(BASE_DIR, 'fixtures')


def load(name):
    path = os.path.join(FIXTURES, name)
    with open(path) as fh:
        return yaml.safe_load(fh) or {}


def report(title, filename, schema):
    errors, warnings = validate_schema(filename, schema, overlay_dirs={})
    print(f"=== {title} ===")
    print(f"fixture: {os.path.join(FIXTURES, filename)}")
    print(f"errors ({len(errors)}):")
    if errors:
        for e in errors:
            print(f"  ERROR: {e}")
    else:
        print("  (none)")
    print(f"warnings ({len(warnings)}):")
    if warnings:
        for w in warnings:
            print(f"  WARN: {w}")
    else:
        print("  (none)")
    print()
    return errors, warnings


def main():
    failed = []

    e1, _ = report(
        "NEGATIVE: missing index_key",
        'missing_index_key.yaml',
        load('missing_index_key.yaml'))
    ik_hits = [e for e in e1 if 'index_key' in e]
    if not ik_hits:
        failed.append('index_key MUST did not fire on missing_index_key.yaml')
    else:
        print(f"PROOF index_key MUST fired ({len(ik_hits)} hit(s))")
        for e in ik_hits:
            print(f"  -> {e}")
        print()

    e2, _ = report(
        "NEGATIVE: missing setter wire+source",
        'missing_setter_wire_source.yaml',
        load('missing_setter_wire_source.yaml'))
    ws_hits = [e for e in e2 if 'wire' in e or 'source' in e]
    # compute-only 'derived' must NOT be flagged
    derived_hits = [e for e in e2 if "setter attr 'derived'" in e]
    if not ws_hits:
        failed.append('setter wire+source MUST did not fire on payload')
    else:
        print(f"PROOF setter wire+source MUST fired ({len(ws_hits)} hit(s))")
        for e in ws_hits:
            print(f"  -> {e}")
        print()
    if derived_hits:
        failed.append("compute-only attr 'derived' was incorrectly flagged")

    e3, w3 = report(
        "POSITIVE control: both MUSTs present",
        'ok_crud_and_setter.yaml',
        load('ok_crud_and_setter.yaml'))
    if e3:
        failed.append(f'positive fixture had errors: {e3}')

    print('=' * 60)
    if failed:
        print('FAILED:')
        for f in failed:
            print(f'  - {f}')
        sys.exit(1)
    print('All SCHEMA_MODEL MUST negative/positive fixtures passed.')
    sys.exit(0)


if __name__ == '__main__':
    main()
