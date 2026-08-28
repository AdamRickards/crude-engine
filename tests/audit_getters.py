#!/usr/bin/env python3
"""Audit all read methods — structure, types, key names, value types.

Usage:
    python3 audit_getters.py 192.168.1.4
    python3 audit_getters.py 192.168.1.4 -o audit_v27.json
    python3 audit_getters.py 192.168.1.4 --compare audit_v1.json

Outputs a JSON audit per method:
  {method: {keys, types, sample_values, row_count, structure}}

Compare mode diffs two audits and reports:
  - Missing/extra methods
  - Missing/extra keys per method
  - Type mismatches
  - Structure mismatches (dict vs list vs scalar)
"""

import argparse
import json
import sys
import time
from collections import OrderedDict


def describe_value(v, depth=0):
    """Describe a value's type and structure without exposing data."""
    if isinstance(v, dict):
        if not v:
            return {"type": "dict", "keys": [], "count": 0}
        sample_key = next(iter(v))
        sample_val = v[sample_key]
        return {
            "type": "dict",
            "count": len(v),
            "key_type": type(sample_key).__name__,
            "key_sample": str(sample_key)[:30],
            "value_structure": describe_value(sample_val, depth + 1) if depth < 2 else type(sample_val).__name__,
        }
    elif isinstance(v, list):
        if not v:
            return {"type": "list", "count": 0}
        return {
            "type": "list",
            "count": len(v),
            "item_structure": describe_value(v[0], depth + 1) if depth < 2 else type(v[0]).__name__,
        }
    else:
        return {"type": type(v).__name__, "value_sample": str(v)[:50]}


def describe_row(row):
    """Describe a dict row's field names and types."""
    if not isinstance(row, dict):
        return {"type": type(row).__name__}
    fields = OrderedDict()
    for k, v in row.items():
        fields[k] = type(v).__name__
    return dict(fields)


def audit_method(device, method_name):
    """Call a method and return its structural audit."""
    t0 = time.monotonic()
    try:
        result = getattr(device, method_name)()
    except Exception as e:
        return {"status": "error", "error": str(e)[:100], "time_ms": 0}
    dt = round((time.monotonic() - t0) * 1000)

    # Handle (result, trace) tuple from debug
    if isinstance(result, tuple):
        result = result[0]

    audit = {
        "status": "ok",
        "time_ms": dt,
        "structure": describe_value(result),
    }

    # For dict-of-dicts (table output), describe the row structure
    if isinstance(result, dict) and result:
        first_val = next(iter(result.values()))
        if isinstance(first_val, dict):
            audit["row_fields"] = describe_row(first_val)
    # For list-of-dicts, describe the row structure
    elif isinstance(result, list) and result and isinstance(result[0], dict):
        audit["row_fields"] = describe_row(result[0])

    return audit


def compare_audits(old, new):
    """Compare two audits and return differences."""
    diffs = []
    all_methods = sorted(set(list(old.keys()) + list(new.keys())))

    for method in all_methods:
        if method not in old:
            diffs.append({"method": method, "issue": "NEW method (not in old)"})
            continue
        if method not in new:
            diffs.append({"method": method, "issue": "MISSING method (was in old)"})
            continue

        o, n = old[method], new[method]

        if o.get("status") != n.get("status"):
            diffs.append({"method": method, "issue": f"status: {o.get('status')} → {n.get('status')}",
                          "old_error": o.get("error", ""), "new_error": n.get("error", "")})
            continue

        if o.get("status") == "error":
            continue

        # Structure type
        o_type = o.get("structure", {}).get("type")
        n_type = n.get("structure", {}).get("type")
        if o_type != n_type:
            diffs.append({"method": method, "issue": f"structure: {o_type} → {n_type}"})

        # Row fields
        o_fields = o.get("row_fields", {})
        n_fields = n.get("row_fields", {})
        if o_fields or n_fields:
            o_keys = set(o_fields.keys())
            n_keys = set(n_fields.keys())
            missing = o_keys - n_keys
            extra = n_keys - o_keys
            if missing:
                diffs.append({"method": method, "issue": f"missing fields: {sorted(missing)}"})
            if extra:
                diffs.append({"method": method, "issue": f"new fields: {sorted(extra)}"})
            for k in o_keys & n_keys:
                if o_fields[k] != n_fields[k]:
                    diffs.append({"method": method, "issue": f"field '{k}' type: {o_fields[k]} → {n_fields[k]}"})

    return diffs


def main():
    parser = argparse.ArgumentParser(description="Audit all read methods")
    parser.add_argument("host", help="Device IP")
    parser.add_argument("-u", default="admin", help="Username")
    parser.add_argument("-p", default="private", help="Password")
    parser.add_argument("--protocol", default=None, choices=["mops", "snmp", "ssh"])
    parser.add_argument("-o", "--output", help="Save audit to JSON file")
    parser.add_argument("--compare", help="Compare against a previous audit JSON")
    args = parser.parse_args()

    from napalm import get_network_driver
    driver = get_network_driver("hios")
    optional = {}
    if args.protocol:
        optional["protocol_preference"] = [args.protocol]
    device = driver(args.host, args.u, args.p, optional_args=optional)
    device.open()

    cap = device.get_capabilities()
    reads = sorted(cap["crude"]["read"])
    print(f"Auditing {len(reads)} read methods on {args.host}...")

    audit = OrderedDict()
    for method in reads:
        a = audit_method(device, method)
        status = "OK" if a["status"] == "ok" else "FAIL"
        detail = f"{a['structure'].get('type', '?')}({a['structure'].get('count', '?')})" if status == "OK" else a.get("error", "")[:40]
        print(f"  {method:40s} {status:4s}  {a.get('time_ms', 0):5d}ms  {detail}")
        audit[method] = a

    device.close()

    ok = sum(1 for a in audit.values() if a["status"] == "ok")
    print(f"\n{ok}/{len(reads)} OK")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(audit, f, indent=2)
        print(f"Saved to {args.output}")

    if args.compare:
        with open(args.compare) as f:
            old_audit = json.load(f)
        diffs = compare_audits(old_audit, audit)
        if diffs:
            print(f"\n{len(diffs)} differences vs {args.compare}:")
            for d in diffs:
                print(f"  {d['method']:40s} {d['issue']}")
        else:
            print(f"\nNo differences vs {args.compare}")


if __name__ == "__main__":
    main()
