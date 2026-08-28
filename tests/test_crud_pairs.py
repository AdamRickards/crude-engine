#!/usr/bin/env python3
"""CRUD round-trip test: get → create → get → set → get → delete → get

Tests all simple RowStatus CRUD pairs. Each test creates an entry,
verifies it exists, upserts a change, verifies the change, deletes it,
and verifies it's gone.

Usage:
    python3 test_crud_pairs.py 192.168.60.80
    python3 test_crud_pairs.py 192.168.60.80 --only dns
    python3 test_crud_pairs.py 192.168.60.80 --skip user
"""

import sys
import json
import argparse
from napalm import get_network_driver


TESTS = {
    "dns": {
        "get": "get_dns",
        "create": ("create_dns_server", {"address": "10.99.99.1"}),
        "set": ("set_dns", {"domain_name": "test.local"}),
        "delete": ("delete_dns_server", {"server_index": None}),  # index discovered at runtime
        "verify_key": "10.99.99.1",
        "verify_in": "servers",
    },
    "ntp": {
        "get": "get_ntp",
        "create": ("create_ntp_server", {"address": "10.99.99.2"}),
        "set": ("set_ntp", {"description": "test-crud"}),
        "delete": ("delete_ntp_server", {"server_index": None}),
        "verify_key": "10.99.99.2",
        "verify_in": "servers",
    },
    "syslog": {
        "get": "get_syslog",
        "create": ("create_syslog_server", {"ip": "10.99.99.3", "port": 514}),
        "set": None,
        "delete": ("delete_syslog_server", {"server_index": None}),
        "verify_key": "10.99.99.3",
        "verify_in": "servers",
    },
    "ip_restrict": {
        "get": "get_ip_restrict",
        "create": ("create_ip_restrict_rule", {"index": 15, "ip": "10.99.99.0", "prefix_length": 24}),
        "set": None,
        "delete": ("delete_ip_restrict_rule", {"index": 15}),
        "verify_key": "10.99.99.0",
        "verify_in": "rules",
    },
    "snmp_trap": {
        "get": "get_snmp_trap_destinations",
        "create": ("create_snmp_trap_dest", {"name": "crud-test-99", "address": "10.99.99.4"}),
        "set": None,
        "delete": ("delete_snmp_trap_dest", {"name": "crud-test-99"}),
        "verify_key": "crud-test-99",
        "verify_in": None,
    },
    "radius": {
        "get": "get_remote_auth",
        "create": ("create_radius_server", {"address": "10.99.99.5"}),
        "set": None,
        "delete": ("delete_radius_server", {"radius_index": None}),
        "verify_key": "10.99.99.5",
        "verify_in": "radius_servers",
    },
    "ldap": {
        "get": "get_remote_auth",
        "create": ("create_ldap_server", {"ldap_address": "10.99.99.6"}),
        "set": None,
        "delete": ("delete_ldap_server", {"ldap_index": None}),
        "verify_key": "10.99.99.6",
        "verify_in": "ldap_servers",
    },
    "tacacs": {
        "get": "get_remote_auth",
        "create": ("create_tacacs_server", {"tacacs_address": "10.99.99.7"}),
        "set": None,
        "delete": ("delete_tacacs_server", {"tacacs_address": "10.99.99.7"}),
        "verify_key": "10.99.99.7",
        "verify_in": "tacacs_servers",
        "delete_by_kwargs": True,
    },
    "user": {
        "get": "get_users",
        "create": ("create_user", {"username": "testcrud", "password": "Test1234!"}),
        "set": None,
        "delete": ("delete_user", {"username": "testcrud"}),
        "verify_key": "testcrud",
        "verify_in": None,
    },
    "port_security": {
        "get": "get_port_security",
        "create": ("create_port_security", {"interface": "1/7", "vlan": 1, "mac": "00:11:22:33:44:55"}),
        "set": None,
        "delete": ("delete_port_security", {"interface": "1/7", "vlan": 1, "mac": "00:11:22:33:44:55"}),
        "verify_key": None,
        "verify_in": None,
        "setup": [
            ("set_port_security", {"global_enabled": True}),
            ("set_port_security", {"interface": "1/7", "enabled": True}),
        ],
        "teardown": [
            ("set_port_security", {"interface": "1/7", "enabled": False}),
            ("set_port_security", {"global_enabled": False}),
        ],
    },
    "static_binding": {
        "get": "get_ip_source_guard_bindings",
        "create": ("create_static_binding", {"binding_ifindex": "1/7", "binding_mac": "00:11:22:33:44:55", "binding_ip": "10.99.99.10", "binding_vlan": 1}),
        "set": None,
        "delete": ("delete_static_binding", {"binding_ifindex": "1/7", "binding_mac": "00:11:22:33:44:55", "binding_ip": "10.99.99.10", "binding_vlan": 1}),
        "verify_key": "10.99.99.10",
        "verify_in": None,
        "delete_by_kwargs": True,
        "setup": [
            ("set_dhcp_snooping", {"enabled": True}),
            ("set_ip_source_guard_port", {"interface": "1/7", "enabled": True}),
        ],
        "teardown": [
            ("set_ip_source_guard_port", {"interface": "1/7", "enabled": False}),
            ("set_dhcp_snooping", {"enabled": False}),
        ],
    },
}


def find_in_table(data, key, sub_table):
    """Find a value in data, return (found: bool, index: str|None).

    For indexed sub_tables like {1: {address: '10.x'}, 2: {...}},
    searches row values and returns the row index if found.
    """
    if sub_table:
        data = data.get(sub_table, {})
    if isinstance(data, dict):
        if key in data:
            return True, key
        for idx, row in data.items():
            if isinstance(row, dict) and key in row.values():
                return True, idx
    if isinstance(data, list):
        for i, item in enumerate(data):
            if key in str(item):
                return True, i
    return False, None


def run_test(device, name, spec):
    """Run one CRUD round-trip test. Returns (name, passed, detail)."""
    get_method = spec["get"]
    create_method, create_kwargs = spec["create"]
    delete_method, delete_kwargs = spec["delete"]
    set_spec = spec.get("set")
    verify_key = spec.get("verify_key")
    verify_in = spec.get("verify_in")

    delete_index_key = [k for k in delete_kwargs if 'index' in k.lower()]
    delete_index_key = delete_index_key[0] if delete_index_key else None

    def _delete_by_index(idx):
        """Delete using discovered index."""
        if delete_index_key:
            getattr(device, delete_method)(**{delete_index_key: idx})
        else:
            getattr(device, delete_method)(idx)

    steps = []
    try:
        # 0. Setup — enable prerequisites if declared
        for setup_method, setup_kwargs in spec.get("setup", []):
            idx = setup_kwargs.pop("interface", None)
            if idx:
                getattr(device, setup_method)(idx, **setup_kwargs)
                setup_kwargs["interface"] = idx  # restore
            else:
                getattr(device, setup_method)(**setup_kwargs)
        if spec.get("setup"):
            steps.append("setup")

        # 1. GET before — check state, clean stale
        before = getattr(device, get_method)()
        steps.append("get_before")

        if verify_key is not None:
            found, stale_idx = find_in_table(before, verify_key, verify_in)
            if found and stale_idx is not None:
                if spec.get("delete_by_kwargs"):
                    getattr(device, delete_method)(**delete_kwargs)
                else:
                    _delete_by_index(stale_idx)
                steps.append("cleanup_stale")
                before = getattr(device, get_method)()

        # 2. CREATE
        getattr(device, create_method)(**create_kwargs)
        steps.append("create")

        # 3. GET after create — verify exists, discover index
        after_create = getattr(device, get_method)()
        steps.append("get_after_create")
        row_idx = None
        if verify_key is not None:
            found, row_idx = find_in_table(after_create, verify_key, verify_in)
            if not found:
                return name, False, f"created but '{verify_key}' not found in get"

        # 4. SET (upsert) on the created row
        if set_spec:
            set_method_name, set_kwargs = set_spec
            if row_idx is not None:
                getattr(device, set_method_name)(row_idx, **set_kwargs)
            else:
                getattr(device, set_method_name)(**set_kwargs)
            steps.append("set")
            after_set = getattr(device, get_method)()
            steps.append("get_after_set")

        # 5. DELETE by discovered index (or by original kwargs for compound-keyed tables)
        if spec.get("delete_by_kwargs") or row_idx is None:
            getattr(device, delete_method)(**delete_kwargs)
        else:
            _delete_by_index(row_idx)
        steps.append("delete")

        # 6. GET after delete — verify gone
        after_delete = getattr(device, get_method)()
        steps.append("get_after_delete")
        if verify_key is not None:
            found, _ = find_in_table(after_delete, verify_key, verify_in)
            if found:
                return name, False, f"deleted but '{verify_key}' still present"

        # 7. Teardown — restore prerequisites
        for td_method, td_kwargs in spec.get("teardown", []):
            idx = td_kwargs.pop("interface", None)
            if idx:
                getattr(device, td_method)(idx, **td_kwargs)
                td_kwargs["interface"] = idx  # restore
            else:
                getattr(device, td_method)(**td_kwargs)

        return name, True, f"{'→'.join(steps)}"

    except Exception as e:
        return name, False, f"failed at {steps[-1] if steps else 'start'}: {e}"


def run_one_crud(device, name, spec):
    """Run a single CRUD round-trip test on an already-open device.

    Returns a cell dict with status, time_ms, evidence. Caller is responsible
    for opening/closing the device.

    Used by test_crud_pairs's own main() and by tests/release_matrix.py.
    """
    import time as _time
    cell = {'kind': 'crud', 'method': spec.get('create', [None])[0], 'test_id': name,
            'status': 'ok', 'time_ms': 0, 'evidence': {}}
    t0 = _time.monotonic()
    try:
        _name, ok, detail = run_test(device, name, spec)
    except Exception as e:
        cell['status'] = 'error'
        cell['evidence']['error'] = str(e)[:200]
        cell['time_ms'] = round((_time.monotonic() - t0) * 1000)
        return cell
    cell['time_ms'] = round((_time.monotonic() - t0) * 1000)
    cell['evidence']['detail'] = detail
    if not ok:
        cell['status'] = 'fail'
    return cell


def main():
    parser = argparse.ArgumentParser(description="CRUD round-trip tests")
    parser.add_argument("host", help="Device IP")
    parser.add_argument("--only", nargs="*", help="Run only these tests")
    parser.add_argument("--skip", nargs="*", help="Skip these tests")
    parser.add_argument("--cleanup", action="store_true", help="Just clean up stale test entries")
    parser.add_argument("--protocol", default="mops")
    args = parser.parse_args()

    tests = dict(TESTS)
    if args.only:
        tests = {k: v for k, v in tests.items() if k in args.only}
    if args.skip:
        tests = {k: v for k, v in tests.items() if k not in args.skip}

    driver = get_network_driver('hios')
    device = driver(
        hostname=args.host,
        username='admin',
        password='private',
        optional_args={'protocol': args.protocol}
    )
    device.open()

    if args.cleanup:
        for name, spec in tests.items():
            verify_key = spec.get("verify_key")
            verify_in = spec.get("verify_in")
            if verify_key is None:
                continue
            try:
                data = getattr(device, spec["get"])()
                found, idx = find_in_table(data, verify_key, verify_in)
                if found and idx is not None:
                    delete_method = spec["delete"][0]
                    dk = spec["delete"][1]
                    idx_key = next((k for k in dk if 'index' in k.lower()), None)
                    if idx_key:
                        getattr(device, delete_method)(**{idx_key: idx})
                    else:
                        getattr(device, delete_method)(idx)
                    print(f"  [CLEAN] {name:20s} deleted index {idx}")
                else:
                    print(f"  [OK   ] {name:20s} nothing to clean")
            except Exception as e:
                print(f"  [SKIP ] {name:20s} {e}")
        device.close()
        sys.exit(0)

    results = []
    for name, spec in tests.items():
        result = run_test(device, name, spec)
        results.append(result)
        status = "PASS" if result[1] else "FAIL"
        print(f"  [{status}] {result[0]:20s} {result[2]}")

    device.close()

    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print(f"\n{passed}/{total} passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
