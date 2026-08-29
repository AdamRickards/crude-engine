#!/usr/bin/env python3
"""Offline proofs for inspect budgets and protocol fan-out. No device."""
from __future__ import annotations

import sys
import threading
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
                "open_ms": None,
                "call_ms": None,
                "error": "overall deadline exceeded",
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

    rc |= _fanout()
    return rc


def _fanout() -> int:
    rc = 0
    orig_driver = rm.get_network_driver
    orig_budget = rm._inspect_budget_s

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

    class _Parallel:
        opens: dict = {}
        closes: dict = {}

        def __init__(self, *args, **kwargs):
            self.proto = (kwargs.get("optional_args") or {}).get("protocol")

        def open(self):
            type(self).opens[self.proto] = threading.get_ident()
            time.sleep(0.25)

        def get_dns(self, **kwargs):
            return {"enabled": True, "servers": {"1": {}}}

        def close(self):
            type(self).closes[self.proto] = threading.get_ident()

    class _HangMops:
        closed: dict = {}

        def __init__(self, *args, **kwargs):
            self.proto = (kwargs.get("optional_args") or {}).get("protocol")

        def open(self):
            pass

        def get_dns(self, **kwargs):
            if self.proto == "mops":
                time.sleep(2)
            return {"enabled": True, "servers": {"1": {}}}

        def close(self):
            type(self).closed[self.proto] = threading.get_ident()

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

        _Parallel.opens = {}
        _Parallel.closes = {}
        rm.get_network_driver = lambda _name: _Parallel

        def _wide(proto, key):
            return 1.0

        rm._inspect_budget_s = _wide
        t0 = time.monotonic()
        out = rm.run_inspect("get_dns", "192.0.2.10", None)
        wall = time.monotonic() - t0
        statuses = {
            k: (v or {}).get("status")
            for k, v in (out.get("protocols") or {}).items()
        }
        if wall > 0.60:
            rc |= fail(f"fan-out wall {wall:.2f}s looks sequential (want ~max 0.25s)")
        elif any(s != "ok" for s in statuses.values()):
            rc |= fail(f"fan-out statuses {statuses}")
        elif set(_Parallel.opens) != set(_Parallel.closes):
            rc |= fail(f"open/close proto mismatch {_Parallel.opens} {_Parallel.closes}")
        elif any(_Parallel.opens[p] != _Parallel.closes[p] for p in _Parallel.opens):
            rc |= fail(
                f"close() on a different thread than open(): "
                f"open={_Parallel.opens} close={_Parallel.closes}"
            )
        else:
            rc |= ok(f"fan-out wall {wall:.2f}s (max not sum), owner-thread close()")

        _HangMops.closed = {}
        rm.get_network_driver = lambda _name: _HangMops

        def _short(proto, key):
            return 0.2

        rm._inspect_budget_s = _short
        t0 = time.monotonic()
        out = rm.run_inspect("get_dns", "192.0.2.10", None)
        wall = time.monotonic() - t0
        protos = out.get("protocols") or {}
        mops = protos.get("mops") or {}
        others = {k: (v or {}).get("status") for k, v in protos.items() if k != "mops"}
        if mops.get("status") != "timeout":
            rc |= fail(f"hung mops should be overall timeout, got {mops}")
        elif wall > 1.0:
            rc |= fail(f"overall wait hung {wall:.2f}s")
        elif any(s != "ok" for s in others.values()):
            rc |= fail(f"siblings should be ok, got {others}")
        elif "mops" in _HangMops.closed:
            rc |= fail("caller must not close() a hung worker's device")
        else:
            rc |= ok(
                f"hung sibling isolated ({wall:.2f}s); others {others}; "
                "no cross-thread close"
            )

        class _WithCli:
            def __init__(self, *args, **kwargs):
                blob = [
                    {
                        "command": "show dns client servers",
                        "level": "enable",
                        "response": "Index Address\n0 1.1.1.1",
                    }
                ]
                self._transports = {"ssh": type("T", (), {"last_cli": blob})()}

            def open(self):
                pass

            def get_dns(self, **kwargs):
                return {"enabled": True, "servers": {"0": {"address": "1.1.1.1"}}}

            def close(self):
                pass

        rm.get_network_driver = lambda _name: _WithCli
        rm._inspect_budget_s = lambda proto, key: 1.0
        quiet = rm.run_inspect("get_dns", "192.0.2.10", "ssh")
        ssh = (quiet.get("protocols") or {}).get("ssh") or {}
        if "cli" in ssh:
            rc |= fail(f"cli present without trace: {ssh}")
        else:
            rc |= ok("no cli on default inspect")
        traced = rm.run_inspect("get_dns", "192.0.2.10", "ssh", trace=True)
        ssh = (traced.get("protocols") or {}).get("ssh") or {}
        cli = ssh.get("cli") or []
        cmds = [c.get("command") for c in cli]
        if "show dns client servers" not in cmds:
            rc |= fail(f"trace last_cli missing show: {cli}")
        else:
            rc |= ok("trace last_cli round-trips show dns client servers")
    finally:
        rm.get_network_driver = orig_driver
        rm._inspect_budget_s = orig_budget
    return rc


if __name__ == "__main__":
    sys.exit(main())
