#!/usr/bin/env python3
"""Proofs that the generated catalogue matches live YAML.

Tight checks, no hardware. Exit 0 only when the generated page is honest.

    python3 scripts/check_catalogue.py              # all
    python3 scripts/check_catalogue.py --e-count
    python3 scripts/check_catalogue.py --composed
    python3 scripts/check_catalogue.py --cli
"""
from __future__ import annotations

import argparse
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("pyyaml required\n")
    sys.exit(2)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCHEMAS = os.path.join(ROOT, "crude_engine", "schemas")
DRIVERS = os.path.join(ROOT, "crude_engine", "drivers")
API_REF = os.path.join(ROOT, "docs", "API_REFERENCE.md")
METH_REF = os.path.join(ROOT, "docs", "METHOD_REFERENCE.md")

# Methods that are allowed to have no wire protocols *if* labelled Derived/Composed.
# Until labelled, they fail --composed.
KNOWN_COMPOSED = {
    "get_config",
    "get_config_fingerprint",
    "get_config_remote",
    "get_ip_addresses",
    "get_loop_protection",
    "get_auto_disable",
    "get_fan_status",
    "get_management_priority",
    "get_device_monitor",
    "get_devsec_status",
    "delete_vrrp",
    "delete_vrrp_tracking",
}


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f) or {}


def execute_methods():
    """E is drivers/*.yaml execute_methods keys, never schema type: fields."""
    names = set()
    if not os.path.isdir(DRIVERS):
        return []
    for fname in sorted(os.listdir(DRIVERS)):
        if not fname.endswith(".yaml"):
            continue
        data = load_yaml(os.path.join(DRIVERS, fname))
        if not isinstance(data, dict):
            continue
        for name in data.get("execute_methods") or []:
            names.add(name)
    return sorted(names)


def schema_count():
    return len([f for f in os.listdir(SCHEMAS) if f.endswith(".yaml")])


def parse_api_header(text):
    # **45 features** | **174 methods** (16C 68R 64U 16D 0E)
    m = re.search(
        r"\*\*(\d+) features\*\* \| \*\*(\d+) methods\*\* "
        r"\((\d+)C (\d+)R (\d+)U (\d+)D (\d+)E\)",
        text,
    )
    if not m:
        return None
    return {
        "features": int(m.group(1)),
        "methods": int(m.group(2)),
        "C": int(m.group(3)),
        "R": int(m.group(4)),
        "U": int(m.group(5)),
        "D": int(m.group(6)),
        "E": int(m.group(7)),
    }


def protocols_none(text):
    """Return method names whose TOC/header line says Protocols: None
    or `(…, None)` without Derived/Composed."""
    found = []
    # TOC: `get_config` (Read, None)
    for m in re.finditer(r"`([A-Za-z0-9_]+)` \([^)]*, None\)", text):
        found.append(m.group(1))
    # Body: **Protocols:** None
    current = None
    for line in text.splitlines():
        hm = re.match(r"### `([A-Za-z0-9_]+)\(\)`", line)
        if hm:
            current = hm.group(1)
            continue
        if current and "**Protocols:** None" in line:
            if "Derived" not in line and "Composed" not in line:
                found.append(current)
    return sorted(set(found))


def fail(msg, errors):
    errors.append(msg)
    print(f"FAIL  {msg}")


def ok(msg):
    print(f"PASS  {msg}")


def check_e_count(errors):
    if not os.path.isfile(API_REF):
        fail(f"missing {API_REF}", errors)
        return
    text = open(API_REF).read()
    header = parse_api_header(text)
    live_e = execute_methods()
    print(
        f"E={len(live_e)} (drivers/*.yaml execute_methods, not schema type:)"
        + (f": {', '.join(live_e)}" if live_e else "")
    )
    if header is None:
        fail("API_REFERENCE.md has no CRUDE header (NC NR NU ND NE)", errors)
        return
    if header["E"] != len(live_e):
        fail(
            f"API_REFERENCE header E={header['E']} but protocol YAML "
            f"declares {len(live_e)} execute methods: {', '.join(live_e)}",
            errors,
        )
    else:
        ok(f"E count matches protocol YAML ({len(live_e)})")
    if header["features"] != schema_count():
        fail(
            f"header features={header['features']} but schemas/ has {schema_count()}",
            errors,
        )
    else:
        ok(f"feature count matches schemas/ ({schema_count()})")


def check_composed(errors):
    if not os.path.isfile(API_REF):
        fail(f"missing {API_REF}", errors)
        return
    text = open(API_REF).read()
    none = protocols_none(text)
    if none:
        fail(
            "Protocols: None (unlabelled) on: " + ", ".join(none),
            errors,
        )
        hint = [n for n in none if n in KNOWN_COMPOSED]
        if hint:
            print("      known-composed candidates: " + ", ".join(hint))
    else:
        ok("no unlabelled Protocols: None")


def check_cli(errors):
    texts = []
    for path in (API_REF, METH_REF):
        if os.path.isfile(path):
            texts.append((path, open(path).read()))
    if not texts:
        fail("no generated reference to search for cli()", errors)
        return
    mentioned = any("cli()" in t or "`cli`" in t for _, t in texts)
    if not mentioned:
        fail("cli() not mentioned in generated references", errors)
        return
    flagged = False
    needles = ("escape hatch", "unbounded", "undeclared capability")
    for path, t in texts:
        low = t.lower()
        if "cli" in low and any(n in low for n in needles):
            flagged = True
            break
    if not flagged:
        fail(
            "cli() is listed but not flagged as the unbounded escape hatch",
            errors,
        )
    else:
        ok("cli() flagged as escape hatch")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--e-count", action="store_true")
    p.add_argument("--composed", action="store_true")
    p.add_argument("--cli", action="store_true")
    args = p.parse_args()
    run_all = not (args.e_count or args.composed or args.cli)
    errors = []
    if run_all or args.e_count:
        check_e_count(errors)
    if run_all or args.composed:
        check_composed(errors)
    if run_all or args.cli:
        check_cli(errors)
    print()
    if errors:
        print(f"{len(errors)} catalogue proof(s) failed")
        return 1
    print("catalogue proofs passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
