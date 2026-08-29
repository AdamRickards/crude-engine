#!/usr/bin/env python3
"""Offline proofs for issue 20. Mocked inspect. No device. No WireGuard."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from http.client import HTTPConnection
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ["CRUDE_SIDECAR_MODE"] = "read-only"
os.environ["CRUDE_SIDECAR_TRANSPORT"] = "fake"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sidecar.app import (  # noqa: E402
    call_inspect,
    handle_run,
    make_server,
    name_to_inspect,
)


def fail(msg):
    print(f"FAIL  {msg}")
    return 1


def ok(msg):
    print(f"PASS  {msg}")
    return 0


def post_http(port, name):
    conn = HTTPConnection("127.0.0.1", port, timeout=5)
    body = json.dumps({"name": name}).encode("utf-8")
    conn.request("POST", "/v1/run", body=body, headers={"Content-Type": "application/json"})
    resp = conn.getresponse()
    raw = resp.read()
    conn.close()
    return resp.status, json.loads(raw.decode("utf-8"))


def main():
    errors = 0

    mapping = name_to_inspect("get_dns.read", {"method": "get_dns", "name": "get_dns.read"})
    if mapping != "get_dns":
        errors += fail(f"name map {mapping!r}")
    else:
        errors += ok("get_dns.read → --inspect --method get_dns")

    fake = call_inspect("get_dns", None)
    if not isinstance(fake, dict) or fake.get("exit") != 0 or not fake.get("fake"):
        errors += fail(f"fake inspect should return dict exit=0 fake=True, got {fake!r}")
    else:
        errors += ok("fake/mocked inspect (no switch)")

    code, body = handle_run({"name": "get_dns.read"})
    result = body.get("result") or {}
    if (
        code != 200
        or result.get("rollback") != "not_armed"
        or "parity_diffs" not in result
        or "protocols" not in result
        or result.get("passed") is not True
    ):
        errors += fail(f"get_dns.read → {code} {body}")
    else:
        errors += ok("POST get_dns.read → 200 rollback=not_armed + inspect map")

    code, body = handle_run({"name": "set_dns.roundtrip"})
    if code != 400 or body.get("error") != "bad_name":
        errors += fail(f"set_dns.roundtrip → {code} {body}")
    else:
        errors += ok("POST set_dns.roundtrip → 400 bad_name (inspect not called)")

    code, body = handle_run({"name": "get_no_such_method.read"})
    if code != 404 or body.get("error") != "unknown_name":
        errors += fail(f"unknown → {code} {body}")
    else:
        errors += ok("unknown well-formed name → 404 unknown_name")

    httpd = make_server("127.0.0.1", 0)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        st, body = post_http(port, "get_dns.read")
        if st != 200 or body.get("result", {}).get("rollback") != "not_armed":
            errors += fail(f"HTTP get_dns.read → {st} {body}")
        else:
            errors += ok("HTTP POST /v1/run get_dns.read → 200")
        st, body = post_http(port, "dns.lifecycle.mops")
        if st != 400 or body.get("error") != "bad_name":
            errors += fail(f"HTTP lifecycle → {st} {body}")
        else:
            errors += ok("HTTP POST dns.lifecycle.mops → 400 bad_name")
    finally:
        httpd.shutdown()

    hits = []
    for path in (ROOT / "sidecar").rglob("*"):
        if path.suffix.lower() not in {".yaml", ".yml", ".md", ".py"}:
            continue
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(errors="replace")
        for i, line in enumerate(text.splitlines(), 1):
            if "https://" in line.lower():
                hits.append(f"{path.relative_to(ROOT)}:{i}")
    if hits:
        errors += fail("https URL in sidecar/: " + ", ".join(hits))
    else:
        errors += ok("no https URL in sidecar/")

    help_proc = subprocess.run(
        [sys.executable, "-m", "sidecar", "--help"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
    )
    text = (help_proc.stdout + help_proc.stderr).lower()
    if help_proc.returncode != 0 or "usage:" not in text:
        errors += fail(f"python -m sidecar --help exit {help_proc.returncode}: {help_proc.stderr}")
    else:
        errors += ok("python -m sidecar --help")

    print()
    if errors:
        print(f"{errors} sidecar proof(s) failed")
        return 1
    print("sidecar read-only proofs passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
