#!/usr/bin/env python3
"""offline_gold_matrix.py — read-only Offline vs gold/config matrix (#165).

Runs schema methods through FeatureEngine + OfflineHIOS (same MOPS driver
path; hostname = config XML path). Classifies each gold leaf:

  match | mismatch | config_absent | offline_empty_gold_present
  | gold_absent | blocked

config_absent is derived by indexing OfflineClient data for the wire
attribute — not a hardcoded oper-attr list. Exit ≠ 0 only on mismatch
(unless --strict, which also fails offline_empty_gold_present).

Examples:
  PYTHONPATH=. python3 tests/offline_gold_matrix.py
  PYTHONPATH=. python3 tests/offline_gold_matrix.py \\
    --config /path/to/config_nvm_config.xml \\
    --gold tests/fixtures/offline_gold/gold_floors.json \\
    --methods get_facts,get_mrp,get_dns
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_CONFIG = HERE / "fixtures" / "offline_gold" / "config_nvm_sample.xml"
DEFAULT_GOLD = HERE / "fixtures" / "offline_gold" / "gold_floors.json"
DEFAULT_METHODS = ("get_facts", "get_mrp", "get_dns", "get_interfaces", "get_banner")

# Schema defaults that count as "empty" for offline vs gold (not a hard
# oper list — used only to detect empty offline leaves).
_EMPTY = (None, "", [], {}, False)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()[:12]


def _is_empty(v: Any) -> bool:
    if v is None:
        return True
    if v == "" or v == [] or v == {}:
        return True
    return False


def _values_equal(a: Any, b: Any) -> bool:
    if a == b:
        return True
    # numeric string / int soft match
    try:
        if a is not None and b is not None and float(a) == float(b):
            return True
    except (TypeError, ValueError):
        pass
    if isinstance(a, str) and isinstance(b, str) and a.lower() == b.lower():
        return True
    return False


def _walk_leaves(obj: Any, prefix: str = "") -> list[tuple[str, Any]]:
    """Flatten dict/list trees to (path, leaf_value)."""
    out: list[tuple[str, Any]] = []
    if isinstance(obj, dict):
        if not obj:
            out.append((prefix or "$", obj))
            return out
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else str(k)
            out.extend(_walk_leaves(v, path))
        return out
    if isinstance(obj, list):
        if not obj:
            out.append((prefix or "$", obj))
            return out
        for i, v in enumerate(obj):
            out.extend(_walk_leaves(v, f"{prefix}[{i}]"))
        return out
    out.append((prefix or "$", obj))
    return out


def _get_path(obj: Any, path: str) -> Any:
    """Best-effort get of a dotted path including [n] segments."""
    if not path or path == "$":
        return obj
    cur = obj
    # tokenize: a.b[0].c → ['a','b',0,'c']
    tokens: list[Any] = []
    buf = ""
    i = 0
    while i < len(path):
        ch = path[i]
        if ch == ".":
            if buf:
                tokens.append(buf)
                buf = ""
            i += 1
            continue
        if ch == "[":
            if buf:
                tokens.append(buf)
                buf = ""
            j = path.index("]", i)
            tokens.append(int(path[i + 1 : j]))
            i = j + 1
            continue
        buf += ch
        i += 1
    if buf:
        tokens.append(buf)
    for tok in tokens:
        if isinstance(cur, dict) and tok in cur:
            cur = cur[tok]
        elif isinstance(cur, list) and isinstance(tok, int) and 0 <= tok < len(cur):
            cur = cur[tok]
        else:
            return None
    return cur


def _top_field(path: str) -> str:
    return path.split(".", 1)[0].split("[", 1)[0]


def _wire_source_for_field(engine, feature: str, field: str, protocol: str = "mops",
                           attrs: dict | None = None):
    """Return (mib, table, field_name) for a schema attribute, or None."""
    if attrs is None:
        try:
            schema = engine.load_feature(feature) or {}
        except Exception:
            return None
        attrs = schema.get("attributes") or {}
    spec = attrs.get(field)
    if not spec:
        return None
    wire_name = spec.get("wire")
    source_name = spec.get("source")
    if not wire_name or not source_name:
        return None
    try:
        wire = engine.load_wire(source_name, protocol) or {}
    except Exception:
        return None
    wa = (wire.get("attributes") or {}).get(wire_name) or {}
    sources = wa.get("sources") or {}
    # Wire shape: sources.mops.read.{mib,table,field} (or snmp/ssh).
    proto_block = sources.get(protocol) or sources.get("mops") or {}
    if isinstance(proto_block, dict) and "mib" not in proto_block:
        src = proto_block.get("read") or proto_block.get("walk") or {}
    else:
        src = proto_block
    if not src and isinstance(sources.get("read"), dict):
        src = sources.get("read") or {}
    mib = src.get("mib")
    table = src.get("table")
    fld = src.get("field")
    if isinstance(src.get("fields"), dict):
        # multi-field — take first matching or any
        fld = fld or next(iter(src["fields"].values()), None)
    if mib and table and fld:
        return mib, table, fld
    return None


def _config_has_attr(client, mib: str, table: str, field: str) -> bool:
    mib_data = client._data.get(mib) or {}
    entries = mib_data.get(table)
    if entries is None:
        return False
    if not entries:
        return False
    return any(field in (e or {}) for e in entries)


def _feature_for_method(engine, method: str) -> str | None:
    try:
        resolved = engine.resolve_intent(method)
        schema_def = getattr(resolved, "schema_def", None) or {}
        if isinstance(schema_def, dict) and schema_def.get("feature"):
            return schema_def["feature"]
        return getattr(resolved, "feature", None)
    except Exception:
        pass
    mm = getattr(engine, "method_map", None) or {}
    if method in mm:
        meta = mm[method]
        if isinstance(meta, dict):
            return meta.get("feature")
        return str(meta)
    return None


def classify_method(
    method: str,
    offline_result: Any,
    gold_floor: Any,
    engine,
    client,
    *,
    error: str | None = None,
) -> list[dict]:
    rows: list[dict] = []
    if error:
        rows.append({
            "method": method,
            "path": "*",
            "class": "blocked",
            "detail": error,
        })
        return rows
    if gold_floor is None:
        rows.append({
            "method": method,
            "path": "*",
            "class": "gold_absent",
            "detail": "no gold floor for method",
        })
        return rows

    feature = _feature_for_method(engine, method)
    schema_attrs = None
    try:
        resolved = engine.resolve_intent(method)
        schema_attrs = getattr(resolved, "schema_attrs", None)
    except Exception:
        schema_attrs = None
    gold_leaves = _walk_leaves(gold_floor)
    for path, gold_val in gold_leaves:
        off_val = _get_path(offline_result, path)
        # Prefer the leaf attribute name (row fields), not the row key.
        field = path.rsplit(".", 1)[-1].split("[", 1)[0]

        if not _is_empty(off_val) and _values_equal(off_val, gold_val):
            rows.append({
                "method": method, "path": path, "class": "match",
                "offline": off_val, "gold": gold_val,
            })
            continue

        if not _is_empty(off_val) and not _is_empty(gold_val) and not _values_equal(off_val, gold_val):
            rows.append({
                "method": method, "path": path, "class": "mismatch",
                "offline": off_val, "gold": gold_val,
            })
            continue

        # offline empty (or missing) while gold has a value
        if _is_empty(off_val) and not _is_empty(gold_val):
            wire = None
            if feature:
                wire = _wire_source_for_field(
                    engine, feature, field, attrs=schema_attrs)
            if wire is None:
                # nested row field — try field name alone under feature attrs
                rows.append({
                    "method": method, "path": path,
                    "class": "config_absent",
                    "detail": "no wire map for field; treat as config/oper gap",
                    "offline": off_val, "gold": gold_val,
                    "followup": True,
                })
                continue
            mib, table, wfield = wire
            if _config_has_attr(client, mib, table, wfield):
                rows.append({
                    "method": method, "path": path,
                    "class": "offline_empty_gold_present",
                    "detail": f"config has {mib}::{table}.{wfield}",
                    "offline": off_val, "gold": gold_val,
                })
            else:
                rows.append({
                    "method": method, "path": path,
                    "class": "config_absent",
                    "detail": f"{mib}::{table}.{wfield} not in saved config",
                    "offline": off_val, "gold": gold_val,
                    "followup": True,
                })
            continue

        # gold empty / both empty
        rows.append({
            "method": method, "path": path, "class": "match",
            "detail": "both empty",
            "offline": off_val, "gold": gold_val,
        })
    return rows


def run(config: Path, gold_path: Path, methods: list[str], strict: bool) -> int:
    from crude_engine import FeatureEngine
    from crude_engine.drivers.offline_hios import OfflineHIOS

    if not config.is_file():
        print(f"blocked: config missing: {config}")
        return 2
    if not gold_path.is_file():
        print(f"blocked: gold missing: {gold_path}")
        return 2

    gold_doc = json.loads(gold_path.read_text())
    gold_methods = (gold_doc.get("methods") or {}) if isinstance(gold_doc, dict) else {}

    transport = OfflineHIOS(str(config), "", "", 5)
    transport.open()
    client = transport.client

    all_rows: list[dict] = []
    results: dict[str, Any] = {}

    # Fresh FeatureEngine per method — shared caches can remap row keys
    # across methods (e.g. get_mrp then get_interfaces → "1/1" vs ifIndex).
    for method in methods:
        engine = FeatureEngine()
        try:
            results[method] = engine.execute(method, "mops", transport)
            err = None
        except Exception as exc:
            results[method] = None
            err = f"{type(exc).__name__}: {exc}"
        all_rows.extend(
            classify_method(
                method,
                results[method],
                gold_methods.get(method),
                engine,
                client,
                error=err,
            )
        )

    transport.close()

    counts = {
        "match": 0,
        "mismatch": 0,
        "config_absent": 0,
        "offline_empty_gold_present": 0,
        "gold_absent": 0,
        "blocked": 0,
    }
    for row in all_rows:
        counts[row["class"]] = counts.get(row["class"], 0) + 1

    followups = [
        r for r in all_rows
        if r["class"] == "config_absent" and r.get("followup")
    ]
    mismatches = [r for r in all_rows if r["class"] == "mismatch"]
    empties = [r for r in all_rows if r["class"] == "offline_empty_gold_present"]

    print("════════════════════════════════════════")
    print("offline_gold_matrix  (#165)")
    print("════════════════════════════════════════")
    print(f"config:  {config}")
    print(f"  sha256:{_sha256(config)}")
    print(f"gold:    {gold_path}")
    print(f"  sha256:{_sha256(gold_path)}")
    print(f"methods: {', '.join(methods)}")
    print()
    print("counts:")
    for k in ("match", "mismatch", "config_absent", "offline_empty_gold_present",
              "gold_absent", "blocked"):
        print(f"  {k:28} {counts.get(k, 0)}")
    print()
    if followups:
        print("followup (config_absent ∩ gold present — not fail):")
        for r in followups:
            print(f"  - {r['method']}.{r['path']}: {r.get('detail')}")
        print()
    if empties:
        print("offline_empty_gold_present (investigate):")
        for r in empties:
            print(f"  - {r['method']}.{r['path']}: {r.get('detail')}")
        print()
    if mismatches:
        print("mismatch (fail):")
        for r in mismatches:
            print(f"  - {r['method']}.{r['path']}: offline={r.get('offline')!r} gold={r.get('gold')!r}")
        print()

    report = {
        "config": str(config),
        "config_sha256_12": _sha256(config),
        "gold": str(gold_path),
        "gold_sha256_12": _sha256(gold_path),
        "methods": methods,
        "counts": counts,
        "followups": followups,
        "mismatches": mismatches,
        "offline_empty_gold_present": empties,
        "rows": all_rows,
        "offline_results": results,
    }
    out_path = Path(os.environ.get("OFFLINE_GOLD_REPORT") or "/tmp/offline_gold_matrix_report.json")
    out_path.write_text(json.dumps(report, indent=2, default=str))
    print(f"report:  {out_path}")

    if mismatches:
        print("RESULT FAIL  mismatch")
        return 1
    if strict and empties:
        print("RESULT FAIL  strict offline_empty_gold_present")
        return 1
    if counts.get("blocked"):
        print("RESULT BLOCKED")
        return 2
    print("RESULT PASS")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Offline vs gold read matrix (#165)")
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG,
                   help="Saved config mibconf XML (Offline hostname)")
    p.add_argument("--gold", type=Path, default=DEFAULT_GOLD,
                   help="Gold floors JSON (methods → schema-shaped dicts)")
    p.add_argument("--methods", default=",".join(DEFAULT_METHODS),
                   help="Comma-separated schema method names")
    p.add_argument("--strict", action="store_true",
                   help="Also fail on offline_empty_gold_present")
    args = p.parse_args(argv)
    methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    return run(args.config, args.gold, methods, args.strict)


if __name__ == "__main__":
    sys.exit(main())
