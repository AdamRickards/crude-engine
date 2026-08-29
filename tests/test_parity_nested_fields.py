#!/usr/bin/env python3
"""Offline fixtures for issue #89: nested row fields that are not sub_tables.

No device. No SIDECAR_URL. Does not reopen #71/#73.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from release_matrix import _compute_parity  # noqa: E402


def test_get_vlans_ports_empty_vs_populated():
    meta = {
        "defaults": {"name": "", "ports": {}},
        "primary_key": "vlan_id",
        "sub_tables": {},
    }
    results = {
        "mops": {"1": {"name": "default", "ports": {"1/1": "U", "1/2": "T"}}},
        "snmp": {"1": {"name": "default", "ports": {"1/1": "U", "1/2": "T"}}},
        "ssh": {"1": {"name": "default", "ports": {}}},
    }
    diffs = _compute_parity("get_vlans", meta, results)
    joined = "\n".join(diffs)
    assert any("ports" in d for d in diffs), diffs
    assert "keys=" in joined, diffs
    # scalars still equal — should not invent a name miss
    assert not any("name:" in d for d in diffs), diffs


def test_get_vlan_egress_empty_list_vs_populated():
    meta = {
        "defaults": {"egress_ports": [], "untagged_ports": []},
        "primary_key": "vlan_id",
        "sub_tables": {},
    }
    results = {
        "mops": {"1": {"egress_ports": ["1/1"], "untagged_ports": []}},
        "snmp": {"1": {"egress_ports": ["1/1"], "untagged_ports": []}},
        "ssh": {"1": {"egress_ports": [], "untagged_ports": []}},
    }
    diffs = _compute_parity("get_vlan_egress", meta, results)
    assert any("egress_ports" in d and "len=" in d for d in diffs), diffs
    assert not any("untagged_ports" in d for d in diffs), diffs


def test_named_sub_tables_not_double_compared_as_flat():
    meta = {
        "defaults": {"enabled": True, "servers": {}},
        "sub_tables": {"servers": {"defaults": {"address": ""}}},
    }
    results = {
        "mops": {"enabled": True, "servers": {"1": {"address": "10.0.0.1"}}},
        "ssh": {"enabled": True, "servers": {"1": {"address": "10.0.0.1"}}},
    }
    diffs = _compute_parity("get_dns", meta, results)
    assert diffs == [], diffs


def test_named_sub_table_row_diffs_still_fire():
    meta = {
        "defaults": {"enabled": True, "servers": {}},
        "sub_tables": {"servers": {"defaults": {"address": ""}}},
    }
    results = {
        "mops": {"enabled": True, "servers": {"1": {"address": "10.0.0.1"}}},
        "ssh": {"enabled": True, "servers": {"0": {"address": "10.0.0.1"}}},
    }
    diffs = _compute_parity("get_dns", meta, results)
    assert any("servers." in d for d in diffs), diffs


def main():
    tests = [
        test_get_vlans_ports_empty_vs_populated,
        test_get_vlan_egress_empty_list_vs_populated,
        test_named_sub_tables_not_double_compared_as_flat,
        test_named_sub_table_row_diffs_still_fire,
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
        print(f"{failed} nested-parity proof(s) failed")
        return 1
    print("nested-parity proofs passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
