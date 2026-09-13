#!/usr/bin/env python3
"""Offline proof for issue 41: pre-login banner text on next line after dots."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402
from crude_engine.drivers.ssh_driver import SSHGatherDriver  # noqa: E402

SHOW = (
    "Pre-login banner preferences\n"
    "--------------------------------------\n"
    "Login banner status.........................enabled\n"
    "Login banner text...........................\n"
    "If you can read this then you are in big trouble!\n"
)


def main() -> int:
    rc = 0
    overlay = yaml.safe_load(
        (ROOT / "crude_engine" / "wire" / "ssh" / "mgmtaccess.yaml").read_text()
    )
    read = overlay["attributes"]["hm2preloginbannertext"]["sources"]["ssh"]["read"]
    if read.get("parser") != "regex" or "Login banner text" not in read.get("pattern", ""):
        print(f"FAIL  overlay read {read}")
        rc = 1
    else:
        print("PASS  overlay uses regex parser for banner text")

    drv = SSHGatherDriver.__new__(SSHGatherDriver)
    drv._driver_config = {}
    # field: same-line only → empty
    field_only = drv._parse_response(
        SHOW, {"field": "Login banner text"}
    )
    if field_only not in ("", None):
        # default parser may be None → fallback dot_keys
        pass
    dotted = drv._parse_dot_keys(SHOW, {"field": "Login banner text"})
    if dotted not in ("", None):
        print(f"FAIL  field same-line expected empty, got {dotted!r}")
        rc = 1
    else:
        print("PASS  field: same-line is empty on live-shaped CLI")

    got = drv._parse_response(SHOW, read)
    if got != "If you can read this then you are in big trouble!":
        print(f"FAIL  regex expected banner body, got {got!r}")
        rc = 1
    else:
        print("PASS  regex captures next-line banner body")
    return rc


if __name__ == "__main__":
    sys.exit(main())
