#!/usr/bin/env python3
"""ENGINE_PRINCIPLES grep-gates. No hardware.

Bans inside crude_engine/ (not docs, not tests, not local/):
  - if protocol == 'snmp' / \"mops\" style branches
  - except Exception: pass

    python3 scripts/check_principles.py
"""
from __future__ import annotations

import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PKG = os.path.join(ROOT, "crude_engine")

# Match decision-in-code protocol forks. Allow `protocol` as a variable
# name and as a YAML key. Ban the explicit string compare.
IF_PROTOCOL = re.compile(
    r"""if\s+.*protocol\s*==\s*['\"](?:mops|snmp|ssh|offline)['\"]"""
)
EXCEPT_PASS = re.compile(r"except\s+Exception\s*:\s*(pass\s*$|\n\s+pass\s*$)", re.M)


def iter_py(root):
    for dirpath, _, files in os.walk(root):
        if "__pycache__" in dirpath:
            continue
        for name in files:
            if name.endswith(".py"):
                yield os.path.join(dirpath, name)


def main():
    if not os.path.isdir(PKG):
        print(f"FAIL  missing package {PKG}")
        return 1
    errors = []
    for path in iter_py(PKG):
        text = open(path, encoding="utf-8").read()
        rel = os.path.relpath(path, ROOT)
        for m in IF_PROTOCOL.finditer(text):
            line = text[: m.start()].count("\n") + 1
            errors.append(f"{rel}:{line}: if protocol == <name>")
        # except Exception: pass — also catch one-liners and next-line pass
        for i, line in enumerate(text.splitlines(), 1):
            if re.search(r"except\s+Exception\s*:\s*pass\b", line):
                errors.append(f"{rel}:{i}: except Exception: pass")
                continue
            if re.match(r"\s*except\s+Exception\s*:\s*$", line):
                nxt = text.splitlines()[i] if i < len(text.splitlines()) else ""
                if re.match(r"\s*pass\s*$", nxt):
                    errors.append(f"{rel}:{i}: except Exception: pass")
    if errors:
        print("FAIL  principle violations:")
        for e in errors:
            print(f"  {e}")
        print(f"\n{len(errors)} violation(s)")
        return 1
    print("PASS  no if protocol == <name> and no except Exception: pass in crude_engine/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
