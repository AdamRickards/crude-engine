#!/usr/bin/env python3
"""Issue 24 hole: run_inspect must reach get_network_driver without sidecar fake.

Does not use CRUDE_SIDECAR_TRANSPORT=fake. Does not need a live switch.
Patches release_matrix.get_network_driver so the protocol loop runs.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))
os.environ.pop("CRUDE_SIDECAR_TRANSPORT", None)

import release_matrix as rm  # noqa: E402


def fail(msg):
    print(f"FAIL  {msg}")
    return 1


def ok(msg):
    print(f"PASS  {msg}")
    return 0


class _Boom:
    def __init__(self, *args, **kwargs):
        pass

    def open(self):
        raise OSError("TEST-NET unreachable")

    def close(self):
        pass


def _driver(_name):
    return _Boom


def main() -> int:
    rc = 0
    if rm.get_network_driver is None:
        # Module imported without napalm. Bind a stub so run_inspect can call it.
        rm.get_network_driver = _driver
        rc |= ok("bound stub get_network_driver (napalm not installed)")
    else:
        rm.get_network_driver = _driver
        rc |= ok("patched get_network_driver")

    out = rm.run_inspect("get_dns", "192.0.2.10", None)
    if not isinstance(out, dict):
        return fail(f"run_inspect returned {type(out)}")
    if out.get("exit") not in (0, None):
        rc |= fail(f"exit {out.get('exit')} error={out.get('error')}")
    else:
        rc |= ok(f"run_inspect exit={out.get('exit')}")

    protos = out.get("protocols") or {}
    if not protos:
        rc |= fail("no per-protocol entries")
    else:
        statuses = {k: (v or {}).get("status") for k, v in protos.items()}
        bad = [f"{k}={s}" for k, s in statuses.items()
               if s not in ("connect_failed", "timeout", "dispatch_error")]
        if bad:
            rc |= fail("expected connect_failed/timeout/dispatch_error, got " + ", ".join(bad))
        else:
            rc |= ok(f"protocol statuses {statuses}")
        if any(s == "ok" for s in statuses.values()):
            rc |= fail("TEST-NET stub must not report status=ok")
    return rc


if __name__ == "__main__":
    sys.exit(main())
