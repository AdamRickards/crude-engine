#!/usr/bin/env python3
"""Offline proof for issue 33: SSH DNS overlay declares key_column 0."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402
from crude_engine.drivers.ssh_driver import SSHGatherDriver  # noqa: E402

SHOW = (
    "No.                  IP address                Active            \n"
    "---  ----------------------------------------  ------\n"
    "  1  192.168.3.1                               [x]\n"
)


def fail(msg):
    print(f"FAIL  {msg}")
    return 1


def ok(msg):
    print(f"PASS  {msg}")
    return 0


def main() -> int:
    rc = 0
    overlay = yaml.safe_load(
        (ROOT / "crude_engine" / "wire" / "ssh" / "dns.yaml").read_text()
    )
    attrs = overlay["attributes"]
    for name, col in (
        ("hm2dnsclientserveraddress", 1),
        ("hm2dnsclientserverindex", 0),
    ):
        read = attrs[name]["sources"]["ssh"]["read"]
        if read.get("key_column") != 0 or read.get("column") != col:
            rc |= fail(f"{name} read {read}")
        else:
            rc |= ok(f"{name} table column={col} key_column=0")

    drv = SSHGatherDriver.__new__(SSHGatherDriver)
    drv._driver_config = {}
    row_num = drv._parse_table(SHOW, {"parser": "table", "column": 1})
    keyed = drv._parse_table(
        SHOW, {"parser": "table", "column": 1, "key_column": 0}
    )
    if list(row_num.keys()) != ["0"]:
        rc |= fail(f"without key_column expected ['0'], got {row_num}")
    else:
        rc |= ok("live show without key_column keys by row_num 0")
    if list(keyed.keys()) != ["1"] or keyed.get("1") != "192.168.3.1":
        rc |= fail(f"with key_column expected {{'1': address}}, got {keyed}")
    else:
        rc |= ok("live show with key_column 0 keys by No. 1")
    return rc


if __name__ == "__main__":
    sys.exit(main())
