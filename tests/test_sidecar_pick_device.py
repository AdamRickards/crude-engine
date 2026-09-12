#!/usr/bin/env python3
"""Offline fixtures for issue #91: sidecar pick by has_capable.

TEST-NET addresses only. Does not read the live gitignored pool.
Does not add hosts. Does not call a switch. #74 stays open.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ["CRUDE_SIDECAR_MODE"] = "read-only"
os.environ["CRUDE_SIDECAR_TRANSPORT"] = "fake"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sidecar.app import handle_run, pick_device, pick_device_ip  # noqa: E402
import sidecar.app as sidecar_app  # noqa: E402

L2 = {
    "ip": "192.0.2.10",
    "label": "example-l2",
    "sw_level": "L2A",
    "safe_for": ["read"],
    "has_capable": ["vlan", "dns"],
}
L3 = {
    "ip": "192.0.2.20",
    "label": "example-l3",
    "sw_level": "L3A_MR",
    "safe_for": ["read"],
    "has_capable": ["vrrp", "route", "router"],
}
L3_NO_READ = {
    "ip": "192.0.2.30",
    "label": "example-l3-noread",
    "safe_for": ["setter"],
    "has_capable": ["vrrp"],
}


def test_vrrp_skips_first_l2():
    picked = pick_device_ip("vrrp", [L2, L3])
    assert picked == "192.0.2.20", picked


def test_dns_still_first_match():
    picked = pick_device_ip("dns", [L2, L3])
    assert picked == "192.0.2.10", picked


def test_no_capable_returns_none():
    assert pick_device_ip("vrrp", [L2]) is None
    assert pick_device_ip("vrrp", [L2, L3_NO_READ]) is None


def test_route_and_router_same_rule():
    assert pick_device_ip("route", [L2, L3]) == "192.0.2.20"
    assert pick_device_ip("router", [L2, L3]) == "192.0.2.20"
    assert pick_device_ip("route", [L2]) is None


def test_handle_run_no_eligible_does_not_inspect():
    prev_pool = sidecar_app.POOL_PATH
    prev_inspect = sidecar_app.call_inspect
    prev_transport = os.environ.get("CRUDE_SIDECAR_TRANSPORT")
    called = []

    def boom(*_a, **_k):
        called.append(True)
        raise AssertionError("inspect must not run when no eligible device")

    tmp = Path(tempfile.mkdtemp()) / "device_pool.yaml"
    tmp.write_text(
        "devices:\n"
        "  - ip: 192.0.2.10\n"
        "    label: example-l2\n"
        "    safe_for: [read]\n"
        "    has_capable: [vlan, dns]\n"
    )
    sidecar_app.POOL_PATH = tmp
    sidecar_app.call_inspect = boom
    os.environ["CRUDE_SIDECAR_TRANSPORT"] = "live"
    try:
        code, body = handle_run({"name": "get_vrrp_instances.read"})
    finally:
        sidecar_app.POOL_PATH = prev_pool
        sidecar_app.call_inspect = prev_inspect
        if prev_transport is None:
            os.environ.pop("CRUDE_SIDECAR_TRANSPORT", None)
        else:
            os.environ["CRUDE_SIDECAR_TRANSPORT"] = prev_transport

    assert called == [], called
    assert code == 503, (code, body)
    assert body.get("error") == "not_ready", body
    msg = body.get("message") or ""
    assert "has_capable" in msg and "vrrp" in msg, body
    assert "192." not in msg, body


def test_handle_run_picks_l3_for_vrrp():
    prev_pool = sidecar_app.POOL_PATH
    prev_inspect = sidecar_app.call_inspect
    prev_transport = os.environ.get("CRUDE_SIDECAR_TRANSPORT")
    seen = []

    def fake_inspect(method, device, protocol=None, trace=False):
        seen.append((method, device))
        return {"exit": 0, "fake": True, "protocols": {}, "parity_diffs": []}

    tmp = Path(tempfile.mkdtemp()) / "device_pool.yaml"
    tmp.write_text(
        "devices:\n"
        "  - ip: 192.0.2.10\n"
        "    label: example-l2\n"
        "    safe_for: [read]\n"
        "    has_capable: [vlan, dns]\n"
        "  - ip: 192.0.2.20\n"
        "    label: example-l3\n"
        "    safe_for: [read]\n"
        "    has_capable: [vrrp, route, router]\n"
    )
    sidecar_app.POOL_PATH = tmp
    sidecar_app.call_inspect = fake_inspect
    os.environ["CRUDE_SIDECAR_TRANSPORT"] = "live"
    try:
        code, body = handle_run({"name": "get_vrrp_instances.read"})
    finally:
        sidecar_app.POOL_PATH = prev_pool
        sidecar_app.call_inspect = prev_inspect
        if prev_transport is None:
            os.environ.pop("CRUDE_SIDECAR_TRANSPORT", None)
        else:
            os.environ["CRUDE_SIDECAR_TRANSPORT"] = prev_transport

    assert code == 200, (code, body)
    assert seen == [("get_vrrp_instances", "192.0.2.20")], seen


def test_pick_device_returns_full_record_not_just_ip():
    dev = pick_device("vrrp", [L2, L3])
    assert dev is L3, dev
    assert dev["label"] == "example-l3", dev
    assert dev["sw_level"] == "L3A_MR", dev


def test_pick_device_none_when_no_match():
    assert pick_device("vrrp", [L2]) is None


def test_handle_run_echoes_label_sw_level_and_feature():
    """Issue #131: result.feature + result.device must name the box that ran."""
    prev_pool = sidecar_app.POOL_PATH
    prev_inspect = sidecar_app.call_inspect
    prev_transport = os.environ.get("CRUDE_SIDECAR_TRANSPORT")

    def fake_inspect(method, device, protocol=None, trace=False):
        return {"exit": 0, "fake": True, "protocols": {}, "parity_diffs": []}

    tmp = Path(tempfile.mkdtemp()) / "device_pool.yaml"
    tmp.write_text(
        "devices:\n"
        "  - ip: 192.0.2.10\n"
        "    label: example-l2\n"
        "    sw_level: L2A\n"
        "    safe_for: [read]\n"
        "    has_capable: [vlan, dns]\n"
        "  - ip: 192.0.2.20\n"
        "    label: example-l3\n"
        "    sw_level: L3A_MR\n"
        "    safe_for: [read]\n"
        "    has_capable: [vrrp, route, router]\n"
    )
    sidecar_app.POOL_PATH = tmp
    sidecar_app.call_inspect = fake_inspect
    os.environ["CRUDE_SIDECAR_TRANSPORT"] = "live"
    try:
        code, body = handle_run({"name": "get_vrrp_instances.read"})
    finally:
        sidecar_app.POOL_PATH = prev_pool
        sidecar_app.call_inspect = prev_inspect
        if prev_transport is None:
            os.environ.pop("CRUDE_SIDECAR_TRANSPORT", None)
        else:
            os.environ["CRUDE_SIDECAR_TRANSPORT"] = prev_transport

    assert code == 200, (code, body)
    result = body.get("result") or {}
    assert result.get("feature") == "vrrp", result
    device = result.get("device") or {}
    assert device.get("label") == "example-l3", result
    assert device.get("sw_level") == "L3A_MR", result
    assert "192.0.2.20" not in json.dumps(result), "ip must not leak into the body"


def test_handle_run_device_null_on_fake_transport():
    """No pool device is picked under fake/offline; device must be null, not omitted."""
    code, body = handle_run({"name": "get_dns.read"})
    assert code == 200, (code, body)
    result = body.get("result") or {}
    assert result.get("feature") == "dns", result
    assert result.get("device") is None, result


def main():
    tests = [
        test_vrrp_skips_first_l2,
        test_dns_still_first_match,
        test_no_capable_returns_none,
        test_route_and_router_same_rule,
        test_handle_run_no_eligible_does_not_inspect,
        test_handle_run_picks_l3_for_vrrp,
        test_pick_device_returns_full_record_not_just_ip,
        test_pick_device_none_when_no_match,
        test_handle_run_echoes_label_sw_level_and_feature,
        test_handle_run_device_null_on_fake_transport,
    ]
    failed = 0
    for fn in tests:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL  {fn.__name__}: {exc}")
    if failed:
        print(f"{failed} pick-device proof(s) failed")
        return 1
    print("pick-device proofs passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
