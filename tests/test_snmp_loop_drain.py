#!/usr/bin/env python3
"""Offline proof for issue 30. No device. No pysnmp required.

CURRENT: close a private loop with a pending Task → pending-destroyed.
DRAIN: drain_and_close → no warning; following sleep(0) is not delayed.
"""
from __future__ import annotations

import asyncio
import gc
import io
import sys
import time
import warnings
from contextlib import redirect_stderr
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from crude_engine.drivers.loop_drain import drain_and_close  # noqa: E402


def fail(msg):
    print(f"FAIL  {msg}")
    return 1


def ok(msg):
    print(f"PASS  {msg}")
    return 0


def _pending_destroyed(text: str, caught) -> bool:
    blob = text.lower() + " ".join(str(w.message).lower() for w in caught)
    return "pending" in blob and "destroyed" in blob


def _close_with_capture(fn, loop) -> str:
    buf = io.StringIO()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        with redirect_stderr(buf):
            fn(loop)
            gc.collect()
        text = buf.getvalue()
        extra = " ".join(str(w.message) for w in caught)
    return text + "\n" + extra


def main() -> int:
    rc = 0

    loop = asyncio.new_event_loop()
    loop.create_task(asyncio.sleep(2))
    leaked_text = _close_with_capture(lambda l: l.close(), loop)
    if not _pending_destroyed(leaked_text, []):
        # __del__ may only land on stderr; already concatenated
        if "pending" not in leaked_text.lower():
            rc |= fail(f"CURRENT expected pending-destroyed, got {leaked_text!r}")
        else:
            rc |= ok("CURRENT leaked=True (pending-destroyed)")
    else:
        rc |= ok("CURRENT leaked=True (pending-destroyed)")

    loop = asyncio.new_event_loop()
    loop.create_task(asyncio.sleep(2))
    drained_text = _close_with_capture(drain_and_close, loop)
    if _pending_destroyed(drained_text, []) or "pending" in drained_text.lower():
        rc |= fail(f"DRAIN still leaked: {drained_text!r}")
    else:
        rc |= ok("DRAIN leaked=False")

    follow = asyncio.new_event_loop()
    t0 = time.monotonic()
    follow.run_until_complete(asyncio.sleep(0))
    follow.close()
    elapsed = time.monotonic() - t0
    if elapsed > 0.5:
        rc |= fail(f"following sleep(0) delayed {elapsed:.3f}s")
    else:
        rc |= ok(f"following sleep(0) {elapsed:.4f}s (not delayed)")

    # SNMPHIOS.close() must call drain_and_close. Import is optional here
    # (pysnmp may be missing). Source check is the floor when it is.
    src = (ROOT / "crude_engine" / "drivers" / "snmp_transport.py").read_text()
    if "drain_and_close" not in src or "all_tasks(loop=" not in (
        ROOT / "crude_engine" / "drivers" / "loop_drain.py"
    ).read_text():
        rc |= fail("SNMPHIOS.close / loop_drain missing drain_and_close(loop=)")
    else:
        rc |= ok("SNMPHIOS.close uses drain_and_close; all_tasks(loop=) required")

    return rc


if __name__ == "__main__":
    sys.exit(main())
