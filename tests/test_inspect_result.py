#!/usr/bin/env python3
"""Offline proofs for inspect budgets. No device. YAML declares open/call."""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))

import release_matrix as rm  # noqa: E402
from sidecar.app import shape_inspect  # noqa: E402


def fail(msg):
    print(f"FAIL  {msg}")
    return 1


def ok(msg):
    print(f"PASS  {msg}")
    return 0


def main() -> int:
    rc = 0
    data = rm._load_inspect_yaml()
    protos = data.get("protocols") or {}
    for name in ("mops", "snmp", "ssh"):
        entry = protos.get(name) or {}
        missing = [k for k in ("open_timeout_s", "call_timeout_s") if k not in entry]
        if missing:
            rc |= fail(f"inspect.yaml missing protocols.{name}.{missing}")
            continue
        if "timeout_s" in entry:
            rc |= fail(f"inspect.yaml protocols.{name} still has combined timeout_s")
            continue
        open_s = rm._inspect_budget_s(name, "open_timeout_s")
        call_s = rm._inspect_budget_s(name, "call_timeout_s")
        rc |= ok(f"inspect.yaml {name} open={open_s}s call={call_s}s")

    # Live get_dns measurement that the old combined 2s budget failed:
    # open 1459ms + call 596ms = 2055ms. Split budgets must cover that.
    mops_open = rm._inspect_budget_s("mops", "open_timeout_s")
    mops_call = rm._inspect_budget_s("mops", "call_timeout_s")
    if mops_open * 1000 <= 1459 or mops_call * 1000 <= 596:
        rc |= fail(
            f"MOPS budgets {mops_open}/{mops_call}s would still fail measured "
            "open 1459ms / call 596ms"
        )
    elif (1459 + 596) <= 2000:
        rc |= fail("fixture numbers no longer exceed the old 2s combined budget")
    else:
        rc |= ok("measured MOPS 1459+596ms exceeds old 2s combined, fits split budgets")

    t0 = time.monotonic()
    try:
        rm._call_with_timeout(0.2, time.sleep, 5)
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
            "mops": {
                "status": "ok",
                "elapsed_ms": 10,
                "open_ms": 7,
                "call_ms": 3,
                "raw": {"servers": {"1": {}}},
            },
            "ssh": {
                "status": "ok",
                "elapsed_ms": 20,
                "open_ms": 15,
                "call_ms": 5,
                "raw": {"servers": {"0": {}}},
            },
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
            "snmp": {
                "status": "timeout",
                "elapsed_ms": 4000,
                "open_ms": 200,
                "call_ms": 3800,
                "phase": "call",
                "error": "exceeded 4.0s",
            },
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

    rc |= _split_phases()
    return rc


def _split_phases() -> int:
    """open+call that would blow a combined 0.25s budget still reports ok."""
    rc = 0

    class _Healthy:
        closed = 0

        def __init__(self, *args, **kwargs):
            pass

        def open(self):
            time.sleep(0.18)

        def get_dns(self, **kwargs):
            time.sleep(0.10)
            return {"enabled": True, "servers": {"1": {"address": "1.1.1.1"}}}

        def close(self):
            type(self).closed += 1

    class _HangCall:
        closed = 0

        def __init__(self, *args, **kwargs):
            pass

        def open(self):
            pass

        def get_dns(self, **kwargs):
            time.sleep(8)

        def close(self):
            type(self).closed += 1

    orig_driver = rm.get_network_driver
    orig_budget = rm._inspect_budget_s
    try:
        rm.get_network_driver = lambda _name: _Healthy

        def _tiny(proto, key):
            if proto != "mops":
                return 0.05
            return 0.35 if key == "open_timeout_s" else 0.25

        rm._inspect_budget_s = _tiny
        out = rm.run_inspect("get_dns", "192.0.2.10", "mops")
        proto = (out.get("protocols") or {}).get("mops") or {}
        if proto.get("status") != "ok":
            rc |= fail(f"healthy split should be ok, got {proto}")
        elif proto.get("open_ms") is None or proto.get("call_ms") is None:
            rc |= fail(f"ok result missing open_ms/call_ms: {proto}")
        elif _Healthy.closed < 1:
            rc |= fail("healthy path did not close()")
        else:
            rc |= ok(
                f"split ok open_ms={proto.get('open_ms')} "
                f"call_ms={proto.get('call_ms')} "
                f"(combined would miss 0.25s)"
            )

        rm.get_network_driver = lambda _name: _HangCall

        def _call_tight(proto, key):
            if key == "open_timeout_s":
                return 1.0
            return 0.2

        rm._inspect_budget_s = _call_tight
        out = rm.run_inspect("get_dns", "192.0.2.10", "mops")
        proto = (out.get("protocols") or {}).get("mops") or {}
        if proto.get("status") != "timeout" or proto.get("phase") != "call":
            rc |= fail(f"hung call should be timeout phase=call, got {proto}")
        elif _HangCall.closed < 1:
            rc |= fail("call-phase timeout did not close()")
        else:
            rc |= ok("call-phase timeout still runs close()")
    finally:
        rm.get_network_driver = orig_driver
        rm._inspect_budget_s = orig_budget
    return rc


if __name__ == "__main__":
    sys.exit(main())
