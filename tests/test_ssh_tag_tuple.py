#!/usr/bin/env python3
"""Offline proof: SSH gather must not crash when _resolve_tag returns a tuple."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from crude_engine.drivers.base import AGGREGATE_TAGS, BaseDriver  # noqa: E402
from crude_engine.drivers.ssh_driver import SSHGatherDriver  # noqa: E402

SHOW = (
    "Port    Acceptable   Ingress     \n"
    "Interface VLAN ID Frame Types  Filtering Priority\n"
    "--------- ------- ------------ --------- --------\n"
    "1/1       1       admit all    disable   0        \n"
    "1/2       1       admit all    disable   0        \n"
)


def fail(msg):
    print(f"FAIL  {msg}")
    return 1


def ok(msg):
    print(f"PASS  {msg}")
    return 0


class _FakeTransport:
    def cli(self, cmd, cmd_verify=None):
        return SHOW

    def navigate_to(self, *args, **kwargs):
        return None

    def _enable(self):
        return None


def main() -> int:
    rc = 0
    tuple_tag = ("crude_text", {"decode": False})
    if BaseDriver._tag_name("crude_text") != "crude_text":
        rc |= fail("_tag_name string")
    else:
        rc |= ok("_tag_name string passthrough")
    if BaseDriver._tag_name(tuple_tag) != "crude_text":
        rc |= fail(f"_tag_name tuple got {BaseDriver._tag_name(tuple_tag)!r}")
    else:
        rc |= ok("_tag_name unwraps (function, args)")

    raised = False
    try:
        tuple_tag in AGGREGATE_TAGS
    except TypeError:
        raised = True
    if not raised:
        rc |= fail("raw tuple membership should TypeError")
    else:
        rc |= ok("raw tuple in AGGREGATE_TAGS is unhashable")
    try:
        BaseDriver._tag_name(tuple_tag) in AGGREGATE_TAGS
    except TypeError:
        rc |= fail("_tag_name membership still TypeError")
    else:
        rc |= ok("_tag_name membership does not raise")

    drv = SSHGatherDriver(
        _FakeTransport(),
        attr_types={"dot1qportacceptableframetypes": "string"},
    )
    try:
        results = drv.gather(
            [
                (
                    "dot1qportacceptableframetypes",
                    {
                        "command": "show vlan port",
                        "parser": "table",
                        "column": 2,
                        "level": "user",
                    },
                )
            ]
        )
    except TypeError as e:
        rc |= fail(f"gather TypeError: {e}")
        return rc
    raw = results.get("dot1qportacceptableframetypes")
    if not isinstance(raw, dict) or len(raw) < 1:
        rc |= fail(f"gather expected dict rows, got {raw!r}")
    else:
        rc |= ok(f"gather table rows n={len(raw)} without TypeError")
    return rc


if __name__ == "__main__":
    sys.exit(main())
