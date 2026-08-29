#!/usr/bin/env python3
"""Offline proofs for issue 24. No device. YAML declares inspect timeouts."""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))

from release_matrix import (  # noqa: E402
    _call_with_timeout,
    _inspect_timeout_s,
    _load_inspect_yaml,
)
from sidecar.app import shape_inspect  # noqa: E402


def fail(msg):
    print(f"FAIL  {msg}")
    return 1


def ok(msg):
    print(f"PASS  {msg}")
    return 0


def main() -> int:
    rc = 0
    data = _load_inspect_yaml()
    protos = data.get("protocols") or {}
    for name in ("mops", "snmp", "ssh"):
        if "timeout_s" not in (protos.get(name) or {}):
            rc |= fail(f"inspect.yaml missing protocols.{name}.timeout_s")
        else:
            rc |= ok(f"inspect.yaml protocols.{name}.timeout_s={_inspect_timeout_s(name)}")

    mops, snmp, ssh = (_inspect_timeout_s(p) for p in ("mops", "snmp", "ssh"))
    if not (mops < snmp <= ssh):
        rc |= fail(f"budgets should be mops < snmp <= ssh, got {mops} {snmp} {ssh}")
    else:
        rc |= ok("MOPS tighter than SNMP, SSH slackest")

    t0 = time.monotonic()
    try:
        _call_with_timeout(0.2, time.sleep, 5)
        rc |= fail("timeout helper did not raise")
    except TimeoutError:
        elapsed = time.monotonic() - t0
        if elapsed > 2.0:
            rc |= fail(f"timeout helper hung {elapsed:.1f}s")
        else:
            rc |= ok(f"timeout helper raised in {elapsed:.2f}s")

    disagreed = {
        "exit": 0,
        "protocols": {
            "mops": {"status": "ok", "elapsed_ms": 10, "raw": {"servers": {"1": {}}}},
            "ssh": {"status": "ok", "elapsed_ms": 20, "raw": {"servers": {"0": {}}}},
        },
        "parity_diffs": ["servers.mops-only rows: ['1']"],
    }
    body = shape_inspect("get_dns.read", disagreed)
    result = body["result"]
    if result.get("passed") is not True:
        rc |= fail("parity diffs must not flip passed to false")
    elif result.get("parity_diffs") != disagreed["parity_diffs"]:
        rc |= fail(f"parity_diffs not passed through: {result.get('parity_diffs')}")
    else:
        rc |= ok("passed true with non-empty parity_diffs (issue-proof)")

    dead = {
        "exit": 0,
        "protocols": {
            "snmp": {"status": "timeout", "elapsed_ms": 5000, "error": "exceeded 5.0s"},
        },
        "parity_diffs": [],
    }
    body = shape_inspect("get_dns.read", dead)
    if body["result"].get("passed") is not False:
        rc |= fail("no protocol ok should be passed false")
    else:
        rc |= ok("all timeout/connect_failed → passed false")

    fake = {"exit": 0, "fake": True, "protocols": {}, "parity_diffs": []}
    if shape_inspect("get_dns.read", fake)["result"].get("passed") is not True:
        rc |= fail("fake transport should pass")
    else:
        rc |= ok("fake transport passed true")

    return rc


if __name__ == "__main__":
    sys.exit(main())
