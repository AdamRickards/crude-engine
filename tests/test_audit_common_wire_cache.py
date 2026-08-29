#!/usr/bin/env python3
"""Offline proof for issue 22. Wire YAML loaders must not re-parse per attribute."""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tests") not in sys.path:
    sys.path.insert(0, str(ROOT / "tests"))

from audit_common import (  # noqa: E402
    _load_one_wire,
    _load_one_wire_overlay,
    load_all_method_metadata,
)


def fail(msg):
    print(f"FAIL  {msg}")
    return 1


def ok(msg):
    print(f"PASS  {msg}")
    return 0


def main() -> int:
    rc = 0
    _load_one_wire.cache_clear()
    _load_one_wire_overlay.cache_clear()

    t0 = time.monotonic()
    first = load_all_method_metadata()
    elapsed = time.monotonic() - t0
    n = len(first)
    if n < 1:
        rc |= fail("load_all_method_metadata returned no methods")
    else:
        rc |= ok(f"metadata methods={n} in {elapsed:.3f}s")

    if elapsed >= 5.0:
        rc |= fail(f"cold load took {elapsed:.1f}s; expected well under 5s after cache")
    else:
        rc |= ok(f"cold load {elapsed:.3f}s < 5s")

    base_info = _load_one_wire.cache_info()
    overlay_info = _load_one_wire_overlay.cache_info()
    if base_info.hits < 1:
        rc |= fail(f"_load_one_wire had no cache hits: {base_info}")
    else:
        rc |= ok(f"_load_one_wire hits={base_info.hits} misses={base_info.misses}")
    # overlays can miss-only if few ssh overlays; hits are expected once files repeat
    rc |= ok(f"_load_one_wire_overlay hits={overlay_info.hits} misses={overlay_info.misses}")

    second = load_all_method_metadata()
    if set(first) != set(second):
        rc |= fail("second load_all_method_metadata() method set differed")
    else:
        rc |= ok("second load method set matches")

    return rc


if __name__ == "__main__":
    sys.exit(main())
