#!/usr/bin/env python3
"""Offline proof: --render writes RELEASE_MATRIX.md, not TODO_HITLIST.md.

Does not run against live docs/. No schema YAML. No ROADMAP archive.
#104 leftover: Docs already archived the TODO trio.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

import release_matrix as rm  # noqa: E402


def test_run_render_does_not_write_hitlist():
    tmp = Path(tempfile.mkdtemp())
    prev = {
        "DOCS_DIR": rm.DOCS_DIR,
        "RENDERED_MATRIX_PATH": rm.RENDERED_MATRIX_PATH,
        "PLAN_PATH": rm.PLAN_PATH,
        "MatrixDB": rm.MatrixDB,
        "_load_device_pool": rm._load_device_pool,
        "_load_method_exemptions": rm._load_method_exemptions,
    }

    class FakeDB:
        def read(self):
            return {"results": {}, "generated_at": "never", "scope": "offline-proof"}

    rm.DOCS_DIR = str(tmp)
    rm.RENDERED_MATRIX_PATH = str(tmp / "RELEASE_MATRIX.md")
    rm.PLAN_PATH = str(tmp / "no-plan.json")
    rm.MatrixDB = lambda: FakeDB()
    rm._load_device_pool = lambda: {"devices": []}
    rm._load_method_exemptions = lambda: []
    try:
        rm.run_render()
    finally:
        for k, v in prev.items():
            setattr(rm, k, v)

    scoreboard = tmp / "RELEASE_MATRIX.md"
    hitlist = tmp / "TODO_HITLIST.md"
    assert scoreboard.is_file(), list(tmp.iterdir())
    text = scoreboard.read_text()
    assert text.startswith("# RELEASE_MATRIX"), text[:80]
    assert not hitlist.exists(), "zombie HITLIST recreated"
    # live docs/ must not have been written by this proof
    live_hit = ROOT / "docs" / "TODO_HITLIST.md"
    assert not live_hit.exists() or "archived" in str(live_hit)


def main():
    try:
        test_run_render_does_not_write_hitlist()
        print("PASS  run_render writes RELEASE_MATRIX.md, not TODO_HITLIST.md")
        return 0
    except AssertionError as exc:
        print(f"FAIL  {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
