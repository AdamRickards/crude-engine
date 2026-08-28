#!/usr/bin/env python3
"""Run full audit across devices and protocols.

Usage:
    python3 audit_all.py                          # all devices, default protocol
    python3 audit_all.py --protocols mops snmp    # specific protocols
    python3 audit_all.py --devices 192.168.60.80  # specific device
    python3 audit_all.py --setters                # include setter audit
    python3 audit_all.py --compare old_results/   # compare against previous run

Devices default to lab ring: 192.168.60.80-85
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime


DEFAULT_DEVICES = {
    "192.168.60.80": "L2A-RM",
    "192.168.60.81": "L2A-RC",
    "192.168.60.82": "L2A-RC",
    "192.168.60.85": "L2S",
}


def run_getter_audit(host, protocol=None, output_dir=None):
    cmd = [sys.executable, os.path.join(os.path.dirname(__file__), "audit_getters.py"), host]
    if protocol:
        cmd += ["--protocol", protocol]
    if output_dir:
        proto_label = protocol or "default"
        fname = f"getters_{host.replace('.', '-')}_{proto_label}.json"
        cmd += ["-o", os.path.join(output_dir, fname)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    return result.stdout, result.returncode


def run_setter_audit(host, protocol=None, output_dir=None):
    cmd = [sys.executable, os.path.join(os.path.dirname(__file__), "audit_setters.py"), host]
    if protocol:
        cmd += ["--protocol", protocol]
    if output_dir:
        proto_label = protocol or "default"
        sub_dir = os.path.join(output_dir, f"setters_{host.replace('.', '-')}_{proto_label}")
        cmd += ["-o", sub_dir]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    return result.stdout, result.returncode


def main():
    parser = argparse.ArgumentParser(description="Full audit across devices and protocols")
    parser.add_argument("--devices", nargs="+", default=None,
                        help="Device IPs (default: lab ring)")
    parser.add_argument("--protocols", nargs="+", default=None,
                        choices=["mops", "snmp", "ssh"],
                        help="Protocols to test (default: device default)")
    parser.add_argument("--setters", action="store_true",
                        help="Include setter audit")
    parser.add_argument("-o", "--output", default=None,
                        help="Output directory")
    parser.add_argument("--compare", default=None,
                        help="Compare against previous audit directory")
    args = parser.parse_args()

    devices = args.devices or list(DEFAULT_DEVICES.keys())
    protocols = args.protocols or [None]  # None = device default

    if args.output:
        os.makedirs(args.output, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Full audit — {len(devices)} devices × {len(protocols)} protocols")
    print(f"Timestamp: {timestamp}")
    print(f"{'='*70}\n")

    summary = {"timestamp": timestamp, "devices": {}}

    for host in devices:
        label = DEFAULT_DEVICES.get(host, host)
        print(f"--- {host} ({label}) ---")

        for protocol in protocols:
            proto_label = protocol or "default"
            print(f"\n  [{proto_label}] Getters:")
            stdout, rc = run_getter_audit(host, protocol, args.output)
            # Extract pass/fail line
            for line in stdout.strip().split("\n")[-3:]:
                if "/" in line and ("OK" in line or "pass" in line.lower()):
                    print(f"    {line.strip()}")

            if args.setters:
                print(f"  [{proto_label}] Setters:")
                stdout, rc = run_setter_audit(host, protocol, args.output)
                for line in stdout.strip().split("\n")[-3:]:
                    if "PASS" in line or "FAIL" in line or "Total" in line:
                        print(f"    {line.strip()}")

        print()

    # Compare mode
    if args.compare and args.output:
        print(f"\n{'='*70}")
        print(f"Comparing {args.output} vs {args.compare}")
        for host in devices:
            for protocol in protocols:
                proto_label = protocol or "default"
                new_file = os.path.join(args.output,
                    f"getters_{host.replace('.', '-')}_{proto_label}.json")
                old_file = os.path.join(args.compare,
                    f"getters_{host.replace('.', '-')}_{proto_label}.json")
                if os.path.exists(new_file) and os.path.exists(old_file):
                    cmd = [sys.executable,
                           os.path.join(os.path.dirname(__file__), "audit_getters.py"),
                           host, "--compare", old_file]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                    for line in result.stdout.strip().split("\n"):
                        if "difference" in line.lower() or "diff" in line.lower():
                            print(f"  {host} [{proto_label}]: {line.strip()}")


if __name__ == "__main__":
    main()
