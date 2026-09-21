#!/usr/bin/env python3
"""Generate docs/FLOORS_BOARD.md — living method × protocol × floor glance (#195).

SoT page: docs/FLOORS_BOARD.md (never hand-edit). Separate from status.html.

Row set (documented source):
  Schema gather/read methods from crude_engine/schemas/*.yaml whose method
  `type:` is dict | list | list_append (same READ_TYPES as generate_catalog.py).
  Keys present only in tests/fixtures/offline_gold/gold_floors.json are unioned
  in so catalogue floors are never silently dropped if a schema hole appears.

Provenance (Test-owned fixture):
  tests/fixtures/floors_provenance.json — redacted method →
  {floor_source, offline, mops, snmp, ssh}. Aggregates only; no host/IP keys.
  floor_source=gold only when device-proved MOPS exists (release_matrix mops
  verdict=pass). Sanitized gold_floors.json alone never sets gold.
  Missing method → floor_source=no-floor, protocol cells=untested.

Cell enum: pass | fail | untested | no-floor | empty (optional)

    python3 scripts/generate_floors_board.py          # write docs/FLOORS_BOARD.md
    python3 scripts/generate_floors_board.py --check  # fail if generated file stale
"""
from __future__ import annotations

import argparse
import json
import os
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("pyyaml required\n")
    sys.exit(2)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCHEMAS = os.path.join(ROOT, "crude_engine", "schemas")
GOLD = os.path.join(ROOT, "tests", "fixtures", "offline_gold", "gold_floors.json")
PROVENANCE = os.path.join(ROOT, "tests", "fixtures", "floors_provenance.json")
OUT = os.path.join(ROOT, "docs", "FLOORS_BOARD.md")

READ_TYPES = {"dict", "list", "list_append"}
COLUMNS = ("method", "floor_source", "offline", "mops", "snmp", "ssh")
CELL_ENUM = ("pass", "fail", "untested", "no-floor", "empty")
FLOOR_SOURCES = ("gold", "no-floor")
PROTO_CELLS = ("pass", "fail", "untested", "empty")


def load_yaml(path: str):
    with open(path) as f:
        return yaml.safe_load(f) or {}


def schema_read_methods() -> list[str]:
    """Gather/read method names from schemas (typed dict|list|list_append)."""
    names: set[str] = set()
    if not os.path.isdir(SCHEMAS):
        return []
    for fname in sorted(os.listdir(SCHEMAS)):
        if not fname.endswith(".yaml"):
            continue
        data = load_yaml(os.path.join(SCHEMAS, fname))
        if not isinstance(data, dict):
            continue
        methods = data.get("methods") or {}
        if not isinstance(methods, dict):
            continue
        for name, mdef in methods.items():
            if not isinstance(mdef, dict):
                continue
            if mdef.get("type") in READ_TYPES:
                names.add(str(name))
    return sorted(names)


def gold_method_keys() -> list[str]:
    """Method keys from gold_floors.json (sanitized sample — not device-proved)."""
    if not os.path.isfile(GOLD):
        return []
    with open(GOLD) as f:
        data = json.load(f)
    methods = data.get("methods") if isinstance(data, dict) else None
    if not isinstance(methods, dict):
        return []
    return sorted(str(k) for k in methods.keys())


def row_methods() -> list[str]:
    return sorted(set(schema_read_methods()) | set(gold_method_keys()))


def load_provenance() -> dict[str, dict[str, str]]:
    """Redacted aggregates; empty dict if fixture missing (honest stub)."""
    if not os.path.isfile(PROVENANCE):
        return {}
    with open(PROVENANCE) as f:
        data = json.load(f)
    methods = data.get("methods") if isinstance(data, dict) else None
    if not isinstance(methods, dict):
        return {}
    out: dict[str, dict[str, str]] = {}
    for name, entry in methods.items():
        if not isinstance(entry, dict):
            continue
        floor = str(entry.get("floor_source") or "no-floor")
        if floor not in FLOOR_SOURCES:
            floor = "no-floor"
        cells = {"floor_source": floor}
        for col in ("offline", "mops", "snmp", "ssh"):
            v = str(entry.get(col) or "untested")
            if v not in PROTO_CELLS:
                v = "untested"
            cells[col] = v
        # Sanitize rule: never promote gold from missing mops pass
        if cells["floor_source"] == "gold" and cells["mops"] != "pass":
            cells["floor_source"] = "no-floor"
        out[str(name)] = cells
    return out


def cell_for(method: str, prov: dict[str, dict[str, str]]) -> dict[str, str]:
    if method in prov:
        return prov[method]
    return {
        "floor_source": "no-floor",
        "offline": "untested",
        "mops": "untested",
        "snmp": "untested",
        "ssh": "untested",
    }


def render(methods: list[str], prov: dict[str, dict[str, str]]) -> str:
    n_gold = sum(1 for m in methods if cell_for(m, prov)["floor_source"] == "gold")
    n_off_pass = sum(1 for m in methods if cell_for(m, prov)["offline"] == "pass")
    n_mops_pass = sum(1 for m in methods if cell_for(m, prov)["mops"] == "pass")
    n_snmp_pass = sum(1 for m in methods if cell_for(m, prov)["snmp"] == "pass")
    n_ssh_pass = sum(1 for m in methods if cell_for(m, prov)["ssh"] == "pass")
    has_prov = bool(prov)

    lines: list[str] = []
    lines.append("# FLOORS_BOARD")
    lines.append("")
    lines.append(
        "> Auto-generated by `scripts/generate_floors_board.py`. **Do not edit.**"
    )
    lines.append(
        "> Effort companion: [#195](https://github.com/AdamRickards/crude-engine/issues/195). "
        "Glance chart: `local/agents/diagrams/effort-board.md`."
    )
    lines.append("")
    if has_prov:
        lines.append("## Provenance")
        lines.append("")
        lines.append(
            "Cells from Test-owned `tests/fixtures/floors_provenance.json` "
            "(redacted aggregates — **no host/IP identity**)."
        )
        lines.append("")
        lines.append(
            "**floor_source=`gold`** only when device-proved MOPS exists "
            "(`mops=pass` from `tests/release_matrix.json` verdicts). "
            "Sanitized `gold_floors.json` alone never sets gold."
        )
        lines.append("")
        lines.append(
            f"Counts: floor_source gold **{n_gold}** / {len(methods)}; "
            f"offline pass **{n_off_pass}**; mops pass **{n_mops_pass}**; "
            f"snmp pass **{n_snmp_pass}**; ssh pass **{n_ssh_pass}**."
        )
        # End-game coverage: among gold rows, protocol cells that pass
        # vs cells that could meet a floor (offline/mops/snmp/ssh).
        protocols = ("offline", "mops", "snmp", "ssh")
        possible = 0
        proven = 0
        for m in methods:
            c = cell_for(m, prov)
            if c["floor_source"] != "gold":
                continue
            for proto in protocols:
                possible += 1
                if c[proto] == "pass":
                    proven += 1
        pct = (100.0 * proven / possible) if possible else 0.0
        lines.append("")
        lines.append("## Coverage (Σ end-game progress)")
        lines.append("")
        lines.append(
            "Effort **Σ Coverage** (`local/agents/diagrams/effort-board.md` + "
            "`diagrams/resolution-loop.md`). "
            "**Possible** = rows with `floor_source=gold` × "
            "`{offline,mops,snmp,ssh}`. **Proven** = those cells = `pass`. "
            "HITL exceptions are explicit only — never silent gaps."
        )
        lines.append("")
        lines.append(
            f"**Rollup: proven `{proven}` / possible `{possible}` "
            f"({pct:.1f}%).** Create→Execute→Resolve thickens this forever; "
            "lanes A′/B/C feed it."
        )
    else:
        lines.append("## Stub note — provenance fixture missing")
        lines.append("")
        lines.append(
            "No `tests/fixtures/floors_provenance.json`. "
            "All rows `floor_source=no-floor`, protocol cells `untested`."
        )
    lines.append("")
    lines.append("### Cell vocabulary")
    lines.append("")
    lines.append("| value | meaning |")
    lines.append("| --- | --- |")
    lines.append("| `pass` | meets floor / matrix green |")
    lines.append("| `fail` | compare red vs floor |")
    lines.append("| `untested` | no honest signal yet |")
    lines.append("| `no-floor` | no device-proved floor |")
    lines.append("| `empty` | optional — both sides empty look-into |")
    lines.append("")
    lines.append("### Row source")
    lines.append("")
    lines.append(
        f"Schema typed reads (`type:` in `{', '.join(sorted(READ_TYPES))}`) "
        f"union `gold_floors.json` method keys. "
        f"Rows: **{len(methods)}**."
    )
    lines.append("")
    lines.append("## Glance")
    lines.append("")
    lines.append("| " + " | ".join(COLUMNS) + " |")
    lines.append("| " + " | ".join("---" for _ in COLUMNS) + " |")
    for method in methods:
        c = cell_for(method, prov)
        cells = [
            f"`{method}`",
            f"`{c['floor_source']}`",
            f"`{c['offline']}`",
            f"`{c['mops']}`",
            f"`{c['snmp']}`",
            f"`{c['ssh']}`",
        ]
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(
        "Regenerate: `python3 scripts/generate_floors_board.py`. "
        "Stale check: `python3 scripts/generate_floors_board.py --check` "
        "(wired in `scripts/ci_offline.sh`)."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Generate docs/FLOORS_BOARD.md (floors glance, #195)"
    )
    p.add_argument(
        "--check",
        action="store_true",
        help="fail if docs/FLOORS_BOARD.md is missing or stale",
    )
    args = p.parse_args()

    methods = row_methods()
    if not methods:
        print("FAIL  no gather methods found (schemas / gold_floors)")
        return 1
    prov = load_provenance()
    text = render(methods, prov)
    rel = os.path.relpath(OUT, ROOT)
    print(
        f"floors board rows={len(methods)} provenance={len(prov)} "
        f"enum={','.join(CELL_ENUM)}"
    )

    if args.check:
        if not os.path.isfile(OUT):
            print(f"FAIL  missing {rel}; re-run scripts/generate_floors_board.py")
            return 1
        on_disk = open(OUT).read()
        if on_disk != text:
            print(f"FAIL  {rel} is stale; re-run scripts/generate_floors_board.py")
            return 1
        print(f"PASS  {rel} matches generator")
        return 0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write(text)
    print(f"wrote {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
