#!/usr/bin/env python3
"""SET round-trip test: get (original) → set (new) → get (verify) → set (restore) → get (verify)

Tests all simple upsert setters. Each test reads the current value, sets a new
value, verifies it changed, restores the original, and verifies restoration.

For per-port setters, uses port 1/3 (non-ring, non-management).

Usage:
    python3 test_setter_pairs.py 192.168.60.85
    python3 test_setter_pairs.py 192.168.60.85 --only banner dns
    python3 test_setter_pairs.py 192.168.60.85 --skip devsec software
    python3 test_setter_pairs.py 192.168.60.85 --protocol snmp
"""

import sys
import json
import argparse
from napalm import get_network_driver


# ---------- test definitions ----------
# Each test:
#   get: getter method name
#   set: setter method name
#   field: dotted path to verify in GET result
#   test_value: value to SET
#   default_value: value to restore (if None, captured from initial GET)
#   index: port/row index for per-port setters (optional)
#   sub_table: sub_table key to dig into for per-port fields (optional)
#   setup: list of (method, kwargs) to run before test (optional)
#   teardown: list of (method, kwargs) to run after test (optional)
#   note: human-readable (optional)

TESTS = {
    # ---- Global scalars ----
    "banner_enabled": {
        "get": "get_banner",
        "set": "set_banner",
        "field": "pre_login_enabled",
        "test_value": True,
        "default_value": None,
    },
    "banner_text": {
        "get": "get_banner",
        "set": "set_banner",
        "field": "pre_login_text",
        "test_value": "SETTER-TEST",
        "default_value": None,
    },
    "dai_src_mac": {
        "get": "get_dai_global",
        "set": "set_dai_global",
        "field": "validate_src_mac",
        "test_value": True,
        "default_value": None,
        "requires": "L2A",
    },
    "dai_dst_mac": {
        "get": "get_dai_global",
        "set": "set_dai_global",
        "field": "validate_dst_mac",
        "test_value": True,
        "default_value": None,
        "requires": "L2A",
    },
    "dai_ip": {
        "get": "get_dai_global",
        "set": "set_dai_global",
        "field": "validate_ip",
        "test_value": True,
        "default_value": None,
        "requires": "L2A",
    },
    "dhcp_snooping_enabled": {
        "get": "get_dhcp_snooping",
        "set": "set_dhcp_snooping",
        "field": "enabled",
        "test_value": True,
        "default_value": None,
        "requires": "L2A",
    },
    "dhcp_snooping_verify_mac": {
        "get": "get_dhcp_snooping",
        "set": "set_dhcp_snooping",
        "field": "verify_mac",
        "test_value": True,
        "default_value": None,
        "requires": "L2A",
        "setup": [("set_dhcp_snooping", {"enabled": True})],
        "teardown": [("set_dhcp_snooping", {"enabled": False})],
    },
    "dns_enabled": {
        "get": "get_dns",
        "set": "set_dns",
        "field": "enabled",
        "test_value": True,
        "default_value": None,
        "requires": "L2A",
    },
    "dns_domain_name": {
        "get": "get_dns",
        "set": "set_dns",
        "field": "domain_name",
        "test_value": "setter-test.local",
        "default_value": None,
        "requires": "L2A",
    },
    "dns_cache": {
        "get": "get_dns",
        "set": "set_dns",
        "field": "cache_enabled",
        "test_value": True,
        "default_value": None,
        "requires": "L2A",
    },
    "gmrp_enabled": {
        "get": "get_gmrp",
        "set": "set_gmrp",
        "field": "enabled",
        "test_value": True,
        "default_value": None,
    },
    "gmrp_unknown_multicast": {
        "get": "get_gmrp",
        "set": "set_gmrp",
        "field": "unknown_multicast",
        "test_value": "discard",
        "default_value": None,
    },
    "gvrp_enabled": {
        "get": "get_gvrp",
        "set": "set_gvrp",
        "field": "enabled",
        "test_value": True,
        "default_value": None,
    },
    "lldp_enabled": {
        "get": "get_lldp_neighbors_detail",
        "set": "set_lldp",
        "field": None,  # no simple field — just verify no error
        "test_value": None,
        "default_value": None,
        "set_kwargs": {"enabled": True},
        "restore_kwargs": {"enabled": True},
        "note": "LLDP enable (already on) — smoke test",
    },
    "lldp_interval": {
        "get": "get_lldp_neighbors_detail",
        "set": "set_lldp",
        "field": None,  # hello_interval not in neighbor detail output
        "test_value": None,
        "default_value": None,
        "set_kwargs": {"hello_interval": 60},
        "restore_kwargs": {"hello_interval": 30},
        "note": "LLDP tx interval (default 30)",
    },
    "ntp_enabled": {
        "get": "get_ntp",
        "set": "set_ntp",
        "field": "enabled",
        "test_value": True,
        "default_value": None,
    },
    "ntp_description": {
        "get": "get_ntp",
        "set": "set_ntp",
        "field": "request_interval",
        "test_value": 60,
        "default_value": None,
    },
    "syslog_enabled": {
        "get": "get_syslog",
        "set": "set_syslog",
        "field": "enabled",
        "test_value": True,
        "default_value": None,
    },
    "session_ssh_timeout": {
        "get": "get_session_config",
        "set": "set_session_config",
        "field": "ssh_timeout",
        "test_value": 120,
        "default_value": None,
    },
    "session_telnet_timeout": {
        "get": "get_session_config",
        "set": "set_session_config",
        "field": "telnet_timeout",
        "test_value": 120,
        "default_value": None,
    },
    "session_web_timeout": {
        "get": "get_session_config",
        "set": "set_session_config",
        "field": "web_timeout",
        "test_value": 120,
        "default_value": None,
    },
    "snmp_v1": {
        "get": "get_snmp_config",
        "set": "set_snmp_config",
        "field": "v1_enabled",
        "test_value": True,
        "default_value": None,
    },
    "snmp_trap_service": {
        "get": "get_snmp_config",
        "set": "set_snmp_config",
        "field": "trap_service",
        "test_value": True,
        "default_value": None,
    },
    "signal_mode": {
        "get": "get_signal_contact",
        "set": "set_signal_contact",
        "field": "mode",
        "test_value": "manual",
        "default_value": None,
        "index": 1,
    },
    "signal_sense_link": {
        "get": "get_signal_contact",
        "set": "set_signal_contact",
        "field": "sense_link_failure",
        "test_value": True,
        "default_value": None,
        "index": 1,
    },
    "signal_trap": {
        "get": "get_signal_contact",
        "set": "set_signal_contact",
        "field": "trap_enabled",
        "test_value": True,
        "default_value": None,
        "index": 1,
    },
    "watchdog_enabled": {
        "get": "get_watchdog_status",
        "set": "set_watchdog",
        "field": "watchdog_enabled",
        "test_value": True,
        "default_value": None,
    },
    "watchdog_interval": {
        "get": "get_watchdog_status",
        "set": "set_watchdog",
        "field": "watchdog_interval",
        "test_value": 300,
        "default_value": None,
    },
    # ---- devsec monitors (19 booleans) ----
    "devsec_trap": {
        "get": "get_devsec",
        "set": "set_devsec",
        "field": "trap_enabled",
        "test_value": True,
        "default_value": None,
    },
    "devsec_mon_http": {
        "get": "get_devsec",
        "set": "set_devsec",
        "field": "monitors.http",
        "test_value": True,
        "default_value": None,
        "set_kwargs": {"monitors.http": True},
        "note": "devsec sub_table intent mapping via dotted path",
    },
    "devsec_mon_telnet": {
        "get": "get_devsec",
        "set": "set_devsec",
        "field": "monitors.telnet",
        "test_value": True,
        "default_value": None,
        "set_kwargs": {"monitors.telnet": True},
    },
    "devsec_mon_password_change": {
        "get": "get_devsec",
        "set": "set_devsec",
        "field": "monitors.password_change",
        "test_value": True,
        "default_value": None,
        "set_kwargs": {"monitors.password_change": True},
    },
    # ---- software ----
    "software_allow_unsigned": {
        "get": "get_software",
        "set": "set_software",
        "field": "allow_unsigned",
        "test_value": True,
        "default_value": None,
    },
    # ---- aca (per-slot, requires SD card inserted — state != absent) ----
    "aca_config_save": {
        "get": "get_aca",
        "set": "set_aca",
        "field": None,
        "test_value": None,
        "default_value": None,
        "index": 2,
        "requires": "L2A",
        "set_kwargs": {"config_save": False},
        "restore_kwargs": {"config_save": True},
        "note": "ACA slot 2 config_save toggle (needs SD card)",
    },
    # ---- system ----
    "system_contact": {
        "get": "get_system_info",
        "set": "set_system_info",
        "field": "contact",
        "test_value": "setter-test-contact",
        "default_value": None,
    },
    "system_location": {
        "get": "get_system_info",
        "set": "set_system_info",
        "field": "location",
        "test_value": "setter-test-location",
        "default_value": None,
    },
    "snmp_info_contact": {
        "get": "get_snmp_information",
        "set": "set_snmp_information",
        "field": "contact",
        "test_value": "setter-test-snmp-contact",
        "default_value": None,
    },
    "snmp_info_location": {
        "get": "get_snmp_information",
        "set": "set_snmp_information",
        "field": "location",
        "test_value": "setter-test-snmp-location",
        "default_value": None,
    },
    # ---- per-port setters (port 1/3, non-ring, non-mgmt) ----
    "port_security_global": {
        "get": "get_port_security",
        "set": "set_port_security",
        "field": "global_enabled",
        "test_value": True,
        "default_value": None,
    },
    "port_security_dynamic_limit": {
        "get": "get_port_security",
        "set": "set_port_security",
        "field": "dynamic_limit",
        "test_value": 10,
        "default_value": None,
        "index": "1/3",
        "sub_table": "ports",
    },
    "ip_restrict_enabled": {
        "get": "get_ip_restrict",
        "set": "set_ip_restrict",
        "field": "enabled",
        "test_value": True,
        "default_value": None,
        "setup": [
            ("create_ip_restrict_rule", {"index": 16, "ip": "10.2.1.0", "prefix_length": 24}),
        ],
        "teardown": [
            ("set_ip_restrict", {"enabled": False}),
            ("delete_ip_restrict_rule", {"index": 16}),
        ],
        "note": "ip_restrict enable — setup creates rule allowing test host 10.2.1.0/24 first",
    },
    "ip_source_guard_port": {
        "get": "get_ip_source_guard_port",
        "set": "set_ip_source_guard_port",
        "field": "enabled",
        "test_value": True,
        "default_value": None,
        "index": "1/3",
        "requires": "L2A",
        "setup": [("set_dhcp_snooping", {"enabled": True})],
        "teardown": [
            ("set_ip_source_guard_port", {"interface": "1/3", "enabled": False}),
            ("set_dhcp_snooping", {"enabled": False}),
        ],
    },
    "sflow_receiver_port": {
        "get": "get_sflow_receiver",
        "set": "set_sflow_receiver",
        "field": None,
        "test_value": None,
        "default_value": None,
        "index": 1,
        "requires": "L2A",
        "set_kwargs": {"port": 9995},
        "restore_kwargs": {"port": 6343},
        "note": "sFlow receiver 1 port (default 6343)",
    },
}


def resolve_field(data, field_path):
    """Resolve dotted field path: 'monitors.http' → data['monitors']['http']."""
    if not field_path:
        return None
    parts = field_path.split(".")
    obj = data
    for p in parts:
        if isinstance(obj, dict):
            obj = obj.get(p)
        else:
            return None
    return obj


def run_test(device, name, spec):
    """Run one SET round-trip test. Returns (name, passed, detail)."""
    get_method = spec["get"]
    set_method = spec["set"]
    field = spec.get("field")
    test_value = spec.get("test_value")
    default_value = spec.get("default_value")
    index = spec.get("index")
    sub_table = spec.get("sub_table")
    set_kwargs = spec.get("set_kwargs")
    restore_kwargs = spec.get("restore_kwargs")

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

        # 1. GET original value
        before = getattr(device, get_method)()
        steps.append("get_before")

        # Extract original value for restoration
        if field and default_value is None:
            if index and sub_table:
                row = before.get(sub_table, {}).get(index, {})
                original = resolve_field(row, field)
            elif index:
                original = resolve_field(before.get(index, {}), field)
            else:
                original = resolve_field(before, field)
        else:
            original = default_value

        # 2. SET new value
        if set_kwargs:
            # Custom kwargs mode (for setters without simple field mapping)
            if index:
                getattr(device, set_method)(index, **set_kwargs)
            else:
                getattr(device, set_method)(**set_kwargs)
        elif field and test_value is not None:
            leaf = field.split(".")[-1]
            if index:
                getattr(device, set_method)(index, **{leaf: test_value})
            else:
                getattr(device, set_method)(**{leaf: test_value})
        else:
            return name, False, "no test_value or set_kwargs defined"
        steps.append("set_new")

        # 3. GET after set — verify change
        after_set = getattr(device, get_method)()
        steps.append("get_after_set")

        if field and test_value is not None:
            if index and sub_table:
                actual = resolve_field(after_set.get(sub_table, {}).get(index, {}), field)
            elif index:
                actual = resolve_field(after_set.get(index, {}), field)
            else:
                actual = resolve_field(after_set, field)

            if actual != test_value:
                return name, False, f"set {field}={test_value!r} but got {actual!r}"

        # 4. SET restore original
        if restore_kwargs:
            if index:
                getattr(device, set_method)(index, **restore_kwargs)
            else:
                getattr(device, set_method)(**restore_kwargs)
        elif set_kwargs and field and original is not None:
            # Rebuild restore from set_kwargs key pattern + captured original
            restore = {list(set_kwargs.keys())[0]: original}
            if index:
                getattr(device, set_method)(index, **restore)
            else:
                getattr(device, set_method)(**restore)
        elif field and original is not None:
            leaf = field.split(".")[-1]
            if index:
                getattr(device, set_method)(index, **{leaf: original})
            else:
                getattr(device, set_method)(**{leaf: original})
        steps.append("set_restore")

        # 5. GET after restore — verify restored
        after_restore = getattr(device, get_method)()
        steps.append("get_after_restore")

        if field and original is not None:
            if index and sub_table:
                restored = resolve_field(after_restore.get(sub_table, {}).get(index, {}), field)
            elif index:
                restored = resolve_field(after_restore.get(index, {}), field)
            else:
                restored = resolve_field(after_restore, field)

            if restored != original:
                return name, False, f"restore {field}={original!r} but got {restored!r}"

        # 6. Teardown
        for td_method, td_kwargs in spec.get("teardown", []):
            idx = td_kwargs.pop("interface", None)
            if idx:
                getattr(device, td_method)(idx, **td_kwargs)
                td_kwargs["interface"] = idx  # restore
            else:
                getattr(device, td_method)(**td_kwargs)

        return name, True, f"{'->'.join(steps)}"

    except Exception as e:
        # Attempt teardown even on failure
        for td_method, td_kwargs in spec.get("teardown", []):
            try:
                idx = td_kwargs.pop("interface", None)
                if idx:
                    getattr(device, td_method)(idx, **td_kwargs)
                    td_kwargs["interface"] = idx
                else:
                    getattr(device, td_method)(**td_kwargs)
            except Exception:
                pass
        return name, False, f"failed at {steps[-1] if steps else 'start'}: {e}"


def run_one_setter(device, name, spec):
    """Run a single setter round-trip test on an already-open device.

    Returns a cell dict with status, time_ms, evidence. Caller is responsible
    for opening/closing the device and for SW-level filtering via level_includes().

    Used by test_setter_pairs's own main() and by tests/release_matrix.py.
    """
    import time as _time
    cell = {'kind': 'setter', 'method': spec.get('set'), 'test_id': name,
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
        # run_test returns ok=False for both gate failures and exceptions —
        # they're already captured in detail. Caller can grep for "failed at"
        # to distinguish a process exception from a verify mismatch.
        cell['status'] = 'fail'
    return cell


SW_LEVELS = ["L2S", "L2E", "L2A", "L3S", "L3A"]


def level_includes(device_level, required_level):
    """Check if device SW level includes the required level."""
    if not required_level:
        return True
    try:
        return SW_LEVELS.index(device_level) >= SW_LEVELS.index(required_level)
    except ValueError:
        return True  # unknown level — try anyway


def main():
    parser = argparse.ArgumentParser(description="SET round-trip tests")
    parser.add_argument("host", help="Device IP")
    parser.add_argument("--only", nargs="*", help="Run only these tests")
    parser.add_argument("--skip", nargs="*", help="Skip these tests")
    parser.add_argument("--protocol", default="mops")
    parser.add_argument("--level", default="L2S",
                        help="Device SW level (L2S, L2A, L3A) — filters tests by requires")
    parser.add_argument("--cleanup", action="store_true",
                        help="Just run all teardowns (clean up stale state)")
    args = parser.parse_args()

    tests = dict(TESTS)
    if args.only:
        tests = {k: v for k, v in tests.items() if k in args.only}
    if args.skip:
        tests = {k: v for k, v in tests.items() if k not in args.skip}
    # Filter by SW level
    skipped_level = {k: v for k, v in tests.items()
                     if not level_includes(args.level, v.get("requires"))}
    tests = {k: v for k, v in tests.items()
             if level_includes(args.level, v.get("requires"))}

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
            for td_method, td_kwargs in spec.get("teardown", []):
                try:
                    idx = td_kwargs.pop("interface", None)
                    if idx:
                        getattr(device, td_method)(idx, **td_kwargs)
                        td_kwargs["interface"] = idx
                    else:
                        getattr(device, td_method)(**td_kwargs)
                    print(f"  [CLEAN] {name:35s} teardown OK")
                except Exception as e:
                    td_kwargs["interface"] = td_kwargs.get("interface", idx)
                    print(f"  [SKIP ] {name:35s} {e}")
        device.close()
        sys.exit(0)

    if skipped_level:
        for name in skipped_level:
            print(f"  [SKIP ] {name:35s} requires {skipped_level[name].get('requires')}")

    results = []
    for name, spec in tests.items():
        result = run_test(device, name, spec)
        results.append(result)
        status = "PASS" if result[1] else "FAIL"
        print(f"  [{status}] {result[0]:35s} {result[2]}")

    device.close()

    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    skipped = len(skipped_level)
    print(f"\n{passed}/{total} passed" + (f", {skipped} skipped (SW level)" if skipped else ""))
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
