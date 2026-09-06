"""Leftover v26/monolith script. Not live law.

Paths are repo-relative (no machine-absolute hardcodes). Do not treat
this as a live generator. Live: generate_docs.py, generate_method_ref.py,
generate_protocols.py, validate_schemas.py. See local/generator/README.md.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_WIRE = _REPO_ROOT / "crude_engine" / "wire"
_SCHEMAS = _REPO_ROOT / "crude_engine" / "schemas"


def _parse_paths(argv: list[str] | None = None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--wire-dir",
        type=Path,
        default=_WIRE,
        help="Wire YAML dir (default: repo crude_engine/wire)",
    )
    p.add_argument(
        "--schema-dir",
        type=Path,
        default=_SCHEMAS,
        help="Schema YAML dir (default: repo crude_engine/schemas)",
    )
    p.add_argument(
        "--run-archive",
        action="store_true",
        help="Required to actually execute this leftover script",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_paths(argv)
    if not args.run_archive:
        raise SystemExit(
            "leftover archive script; pass --run-archive to execute "
            "(still not live law). Defaults are repo-relative."
        )
    raise SystemExit(
        "archive body not ported to relative paths as a safe mutator; "
        "use validate_schemas.py / isolated batch_generate_MIB.py instead"
    )


if __name__ == "__main__":
    main()
