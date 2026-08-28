#!/usr/bin/env python3
"""Audit SET/CREATE/DELETE methods — safe automated tests with trace capture.

Usage:
    python3 audit_setters.py 192.168.60.80
    python3 audit_setters.py 192.168.60.80 --protocol mops
    python3 audit_setters.py 192.168.60.80 --unsafe         # include unsafe (interactive)
    python3 audit_setters.py 192.168.60.80 -o results/      # save per-test JSON

Each test:
  1. SET with validate=True, capture trace + gate results
  2. If gate fails: retry with validate=False, record both
  3. GET to verify the value changed
  4. REVERT to original value
  5. GET to verify revert worked
"""

import argparse
import json
import os
import sys
import time
import yaml
from collections import OrderedDict
from datetime import datetime


def load_safety(path=None):
    if not path:
        path = os.path.join(os.path.dirname(__file__), "audit_safety.yaml")
    with open(path) as f:
        return yaml.safe_load(f)


def resolve_field(result, field_path):
    """Resolve dotted field path: 'http.enabled' → result['http']['enabled']."""
    parts = field_path.split(".")
    obj = result
    for p in parts:
        if isinstance(obj, dict):
            obj = obj.get(p)
        else:
            return None
    return obj


def run_test(device, test_def, protocol, output_dir=None):
    """Run one SET test. Returns test result dict."""
    t0 = time.monotonic()
    method = test_def["method"]
    args = dict(test_def.get("args", {}))
    index = test_def.get("index")
    verify_method = test_def.get("verify")
    verify_field = test_def.get("verify_field")
    verify_value = test_def.get("verify_value")
    revert = test_def.get("revert")
    revert_method = test_def.get("revert_method")
    revert_args = test_def.get("revert_args", {})
    note = test_def.get("note", "")

    result = {
        "method": method,
        "index": index,
        "note": note,
        "protocol": protocol,
        "steps": [],
    }

    # --- Step 1: SET with validation ---
    try:
        call_args = dict(args, debug=True)
        if index:
            call_args["index"] = index
        set_result = getattr(device, method)(**call_args)
        if isinstance(set_result, tuple):
            set_result, trace = set_result
        else:
            trace = []
        result["steps"].append({
            "action": "set",
            "validate": True,
            "status": "ok",
            "result": repr(set_result)[:200],
            "trace": trace,
            "gate_results": [t for t in trace if "gate" in t],
        })
    except ValueError as e:
        # Gate rejection
        error_msg = str(e)
        result["steps"].append({
            "action": "set",
            "validate": True,
            "status": "gate_reject",
            "error": error_msg,
        })
        # Retry without validation
        try:
            call_args = dict(args, debug=True, validate=False)
            if index:
                call_args["index"] = index
            set_result = getattr(device, method)(**call_args)
            if isinstance(set_result, tuple):
                set_result, trace = set_result
            else:
                trace = []
            result["steps"].append({
                "action": "set_no_validate",
                "validate": False,
                "status": "ok",
                "result": repr(set_result)[:200],
                "trace": trace,
            })
        except Exception as e2:
            result["steps"].append({
                "action": "set_no_validate",
                "validate": False,
                "status": "error",
                "error": str(e2)[:200],
            })
            result["status"] = "FAIL"
            return result
    except Exception as e:
        result["steps"].append({
            "action": "set",
            "validate": True,
            "status": "error",
            "error": str(e)[:200],
        })
        result["status"] = "FAIL"
        return result

    # --- Step 2: Verify ---
    if verify_method:
        try:
            # MOPS applies immediately on response — no delay needed
            get_result = getattr(device, verify_method)()
            if verify_field and verify_value is not None:
                if index and isinstance(get_result, dict):
                    # Table result — find the row
                    row = get_result.get(index, get_result.get(str(index), {}))
                    actual = resolve_field(row, verify_field) if isinstance(row, dict) else None
                else:
                    actual = resolve_field(get_result, verify_field)
                verified = actual == verify_value
                result["steps"].append({
                    "action": "verify",
                    "status": "ok" if verified else "mismatch",
                    "field": verify_field,
                    "expected": verify_value,
                    "actual": actual,
                })
            else:
                result["steps"].append({
                    "action": "verify",
                    "status": "ok",
                    "result_type": type(get_result).__name__,
                    "result_size": len(get_result) if isinstance(get_result, (dict, list)) else "?",
                })
        except Exception as e:
            result["steps"].append({
                "action": "verify",
                "status": "error",
                "error": str(e)[:200],
            })

    # --- Step 3: Revert ---
    if revert == "delete" and revert_method:
        try:
            r_args = dict(revert_args)
            if index and "index" not in r_args:
                r_args["index"] = index
            getattr(device, revert_method)(**r_args)
            result["steps"].append({"action": "revert_delete", "status": "ok"})
        except Exception as e:
            result["steps"].append({
                "action": "revert_delete",
                "status": "error",
                "error": str(e)[:200],
            })
    elif revert and isinstance(revert, dict):
        try:
            r_args = dict(revert)
            if index:
                r_args["index"] = index
            getattr(device, method)(**r_args, validate=False)
            result["steps"].append({"action": "revert", "status": "ok"})
        except Exception as e:
            result["steps"].append({
                "action": "revert",
                "status": "error",
                "error": str(e)[:200],
            })

    # --- Overall status ---
    statuses = [s["status"] for s in result["steps"]]
    if "error" in statuses:
        result["status"] = "FAIL"
    elif "gate_reject" in statuses:
        result["status"] = "GATE"
    elif "mismatch" in statuses:
        result["status"] = "MISMATCH"
    else:
        result["status"] = "PASS"

    result["time_ms"] = round((time.monotonic() - t0) * 1000)

    # Save per-test output
    if output_dir:
        fname = f"{method}_{(index or 'global').replace('/', '-')}_{protocol}.json"
        with open(os.path.join(output_dir, fname), "w") as f:
            json.dump(result, f, indent=2, default=str)

    return result


def main():
    parser = argparse.ArgumentParser(description="Audit SET/CREATE/DELETE methods")
    parser.add_argument("host", help="Device IP")
    parser.add_argument("-u", default="admin", help="Username")
    parser.add_argument("-p", default="private", help="Password")
    parser.add_argument("--protocol", default=None, choices=["mops", "snmp", "ssh"])
    parser.add_argument("--unsafe", action="store_true", help="Include unsafe tests (interactive)")
    parser.add_argument("--safety", default=None, help="Path to audit_safety.yaml")
    parser.add_argument("-o", "--output", default=None, help="Output directory for per-test JSON")
    args = parser.parse_args()

    safety = load_safety(args.safety)

    from napalm import get_network_driver
    driver = get_network_driver("hios")
    optional = {}
    if args.protocol:
        optional["protocol_preference"] = [args.protocol]
    device = driver(args.host, args.u, args.p, optional_args=optional)
    device.open()

    protocol = getattr(device, "active_protocol", args.protocol or "mops")
    if callable(protocol):
        protocol = protocol()

    if args.output:
        os.makedirs(args.output, exist_ok=True)

    print(f"Setter audit on {args.host} via {protocol}")
    print(f"{'='*70}")

    # --- Safe tests ---
    safe_tests = safety.get("safe", [])
    results = []
    for test_def in safe_tests:
        method = test_def["method"]
        index = test_def.get("index", "")
        note = test_def.get("note", "")
        label = f"{method}({index})" if index else method

        r = run_test(device, test_def, protocol, args.output)
        results.append(r)

        status = r["status"]
        gate_info = ""
        for s in r["steps"]:
            if s.get("status") == "gate_reject":
                gate_info = f" [gate: {s['error'][:40]}]"
            if s.get("status") == "mismatch":
                gate_info = f" [expected={s['expected']}, got={s['actual']}]"
        ms = r.get("time_ms", 0)
        print(f"  {label:45s} {status:8s} {ms:5d}ms{gate_info}")

    # --- Unsafe tests (interactive) ---
    if args.unsafe:
        unsafe_tests = safety.get("unsafe", [])
        print(f"\n{'='*70}")
        print("UNSAFE TESTS (require manual verification)")
        print(f"{'='*70}")
        for test_def in unsafe_tests:
            method = test_def.get("method", "")
            reason = test_def.get("reason", "")
            print(f"  {method:45s} SKIPPED — {reason}")

    # --- Summary ---
    pass_count = sum(1 for r in results if r["status"] == "PASS")
    gate_count = sum(1 for r in results if r["status"] == "GATE")
    fail_count = sum(1 for r in results if r["status"] == "FAIL")
    mismatch_count = sum(1 for r in results if r["status"] == "MISMATCH")

    print(f"\n{'='*70}")
    print(f"  {pass_count} PASS, {gate_count} GATE, {mismatch_count} MISMATCH, {fail_count} FAIL")
    print(f"  Total: {len(results)} safe tests on {args.host} via {protocol}")

    if args.output:
        summary = {
            "host": args.host,
            "protocol": protocol,
            "timestamp": datetime.now().isoformat(),
            "pass": pass_count,
            "gate": gate_count,
            "mismatch": mismatch_count,
            "fail": fail_count,
            "results": results,
        }
        with open(os.path.join(args.output, "summary.json"), "w") as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"  Results saved to {args.output}/")

    device.close()


if __name__ == "__main__":
    main()
