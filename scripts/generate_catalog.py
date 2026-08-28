#!/usr/bin/env python3
"""Generate the named test catalog from live YAML.

Named entries come from schema `type:` (C/R/U/D) plus protocol
`execute_methods` (E). Do not invent CRUDE methods. Hand-grown TESTS
dicts in tests/ are left alone.

    python3 scripts/generate_catalog.py          # write tests/catalog.yaml
    python3 scripts/generate_catalog.py --check  # proof only (file must match)

Proof (AGENTS.md §5 / ISSUES #9): entry count > 0, and every schema
read method (`type:` dict|list|list_append) has a `*.read`.
"""
from __future__ import annotations

import argparse
import os
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("pyyaml required\n")
    sys.exit(2)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCHEMAS = os.path.join(ROOT, "crude_engine", "schemas")
DRIVERS = os.path.join(ROOT, "crude_engine", "drivers")
CATALOG = os.path.join(ROOT, "tests", "catalog.yaml")

# SCHEMA_MODEL + generate_method_ref TYPE_LABELS. Missing type is a
# schema hole (alias via `schema:`), not a catalog method.
READ_TYPES = {"dict", "list", "list_append"}
WRITE_MAP = {"create": "C", "upsert": "U", "delete": "D"}
ACCESS_SUFFIX = {"R": "read", "C": "roundtrip", "U": "roundtrip", "D": "roundtrip", "E": "execute"}


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f) or {}


def schema_methods():
    """Yield (feature, method, schema_type) from schemas/*.yaml."""
    rows = []
    skipped = []
    for fname in sorted(os.listdir(SCHEMAS)):
        if not fname.endswith(".yaml"):
            continue
        data = load_yaml(os.path.join(SCHEMAS, fname))
        if not isinstance(data, dict):
            continue
        feature = data.get("feature") or fname[:-5]
        methods = data.get("methods") or {}
        if not isinstance(methods, dict):
            continue
        for name, mdef in methods.items():
            if not isinstance(mdef, dict):
                skipped.append((feature, name, "not a mapping"))
                continue
            schema_type = mdef.get("type")
            if schema_type is None:
                skipped.append((feature, name, "no type (alias/hole)"))
                continue
            rows.append((str(feature), str(name), str(schema_type)))
    return rows, skipped


def execute_methods():
    """Union of execute_methods across drivers/*.yaml, with protocol labels."""
    found = {}
    if not os.path.isdir(DRIVERS):
        return found
    for fname in sorted(os.listdir(DRIVERS)):
        if not fname.endswith(".yaml"):
            continue
        data = load_yaml(os.path.join(DRIVERS, fname))
        if not isinstance(data, dict):
            continue
        names = data.get("execute_methods") or []
        if not names:
            continue
        proto = data.get("protocol") or fname[:-5]
        label = str(proto).upper()
        for name in names:
            found.setdefault(str(name), [])
            if label not in found[name]:
                found[name].append(label)
    return found


def build_entries():
    rows, skipped = schema_methods()
    entries = []
    seen = set()
    features_with_write = set()

    def add(entry):
        name = entry["name"]
        if name in seen:
            return
        seen.add(name)
        entries.append(entry)

    for feature, method, schema_type in rows:
        if schema_type in READ_TYPES:
            add({
                "name": f"{method}.read",
                "access": "R",
                "method": method,
                "feature": feature,
                "schema_type": schema_type,
            })
        elif schema_type in WRITE_MAP:
            access = WRITE_MAP[schema_type]
            features_with_write.add(feature)
            add({
                "name": f"{method}.roundtrip",
                "access": access,
                "method": method,
                "feature": feature,
                "schema_type": schema_type,
            })
        else:
            skipped.append((feature, method, f"unknown type {schema_type!r}"))

    for method, protocols in sorted(execute_methods().items()):
        add({
            "name": f"{method}.execute",
            "access": "E",
            "method": method,
            "protocols": protocols,
        })

    for feature in sorted(features_with_write):
        add({
            "name": f"{feature}.lifecycle.mops",
            "access": "lifecycle",
            "feature": feature,
            "protocol": "mops",
        })

    entries.sort(key=lambda e: e["name"])
    return entries, skipped


def counts(entries):
    out = {
        "entries": len(entries),
        "read": 0,
        "roundtrip": 0,
        "execute": 0,
        "lifecycle": 0,
    }
    for e in entries:
        name = e["name"]
        if name.endswith(".lifecycle.mops"):
            out["lifecycle"] += 1
        elif name.endswith(".execute"):
            out["execute"] += 1
        elif name.endswith(".roundtrip"):
            out["roundtrip"] += 1
        elif name.endswith(".read"):
            out["read"] += 1
    return out


def proof(entries, rows):
    """Return list of fail strings. Empty means green."""
    errors = []
    if len(entries) <= 0:
        errors.append("named entry count is 0")
    names = {e["name"] for e in entries}
    reads = [(f, m) for f, m, t in rows if t in READ_TYPES]
    missing = [m for _, m in reads if f"{m}.read" not in names]
    if missing:
        errors.append(
            "schema read method(s) missing *.read: " + ", ".join(sorted(set(missing)))
        )
    return errors, len(reads), len(reads) - len(set(missing))


def catalog_doc(entries, skipped):
    c = counts(entries)
    return {
        "generated": True,
        "generator": "scripts/generate_catalog.py",
        "source": "crude_engine/schemas/*.yaml type: + drivers/*.yaml execute_methods",
        "counts": c,
        "skipped_untyped": [
            {"feature": f, "method": m, "reason": r} for f, m, r in skipped
        ],
        "entries": entries,
    }


def dump_catalog(doc):
    header = (
        "# Generated by scripts/generate_catalog.py. Do not hand-edit.\n"
        "# Named tests from schema type: (C/R/U/D) + protocol execute_methods (E).\n"
        "# Examples: get_dns.read, set_dns.roundtrip, dns.lifecycle.mops.\n"
        "# Untyped alias methods are listed under skipped_untyped, not invented.\n"
    )
    body = yaml.safe_dump(
        doc,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=100,
    )
    return header + body


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true", help="proof + match tests/catalog.yaml")
    args = p.parse_args()

    rows, _ = schema_methods()
    entries, skipped = build_entries()
    errors, n_reads, n_covered = proof(entries, rows)
    c = counts(entries)
    print(
        f"catalog entries={c['entries']} "
        f"read={c['read']} roundtrip={c['roundtrip']} "
        f"execute={c['execute']} lifecycle={c['lifecycle']}"
    )
    print(f"schema reads covered {n_covered}/{n_reads}")
    if skipped:
        print("skipped_untyped: " + ", ".join(f"{m} ({r})" for _, m, r in skipped))

    if errors:
        for e in errors:
            print(f"FAIL  {e}")
        return 1
    print("PASS  named entry count > 0")
    print(f"PASS  every schema read method has *.read ({n_covered}/{n_reads})")

    doc = catalog_doc(entries, skipped)
    text = dump_catalog(doc)
    if args.check:
        if not os.path.isfile(CATALOG):
            print(f"FAIL  missing {CATALOG}")
            return 1
        on_disk = open(CATALOG).read()
        if on_disk != text:
            print(f"FAIL  {CATALOG} is stale; re-run scripts/generate_catalog.py")
            return 1
        print(f"PASS  {CATALOG} matches generator")
        return 0

    os.makedirs(os.path.dirname(CATALOG), exist_ok=True)
    with open(CATALOG, "w") as f:
        f.write(text)
    print(f"wrote {CATALOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
