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
    handle_sync,
    make_server,
    name_to_inspect,
)
import sidecar.app as sidecar_app  # noqa: E402


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
        or (body.get("sidecar") or {}).get("ref") != "main"
    ):
        errors += fail(f"get_dns.read → {code} {body}")
    else:
        errors += ok("POST get_dns.read → 200 rollback=not_armed + inspect map")

    code, body = handle_run({"name": "set_dns.roundtrip"})
    if code != 400 or body.get("error") != "bad_name":
        errors += fail(f"set_dns.roundtrip → {code} {body}")
    else:
        errors += ok("POST set_dns.roundtrip → 400 bad_name (inspect not called)")

    code, body = handle_run({"name": "get_dns.read", "device": "192.0.2.10"})
    if code != 400 or body.get("error") != "bad_name":
        errors += fail(f"extra key → {code} {body}")
    else:
        errors += ok("extra POST key → 400 bad_name")

    code, body = handle_run({"name": "get_dns.read", "trace": True})
    result = body.get("result") or {}
    if code != 200 or result.get("passed") is not True:
        errors += fail(f"trace true → {code} {body}")
    elif "cli" in str(result.get("protocols") or {}):
        errors += fail(f"fake trace should have empty protocols, got {result}")
    else:
        errors += ok("POST get_dns.read trace=true still 200 (fake)")

    def boom(*_a, **_k):
        raise AssertionError("git must not run on fake or 403")

    sidecar_app._git_sync_main = boom
    sidecar_app._git_sync_pr = boom

    code, body = handle_sync({"op": "main"})
    if code != 200 or body.get("ref") != "main" or body.get("restart") is not False:
        errors += fail(f"sync main fake → {code} {body}")
    else:
        errors += ok("POST /v1/sync op=main fake → 200 no git")

    code, body = handle_sync({"op": "clean"})
    if code != 200 or body.get("ref") != "main":
        errors += fail(f"sync clean fake → {code} {body}")
    else:
        errors += ok("POST /v1/sync op=clean fake → 200")

    code, body = handle_sync({"op": "pr"})
    if code != 400 or body.get("error") != "bad_name":
        errors += fail(f"sync pr missing number → {code} {body}")
    else:
        errors += ok("POST /v1/sync pr without number → 400")

    code, body = handle_sync({"op": "pr", "number": 2, "ref": "heads/x"})
    if code != 400 or body.get("error") != "bad_name":
        errors += fail(f"sync extra key → {code} {body}")
    else:
        errors += ok("POST /v1/sync extra key → 400")

    sidecar_app.pr_author_lookup = lambda n: "stranger"
    code, body = handle_sync({"op": "pr", "number": 2})
    if code != 403 or body.get("error") != "forbidden":
        errors += fail(f"foreign author → {code} {body}")
    else:
        errors += ok("POST /v1/sync pr foreign author → 403 no git")

    sidecar_app.pr_author_lookup = lambda n: "AdamRickards"
    code, body = handle_sync({"op": "pr", "number": 1})
    if (
        code != 200
        or body.get("ref") != "pr-1"
        or body.get("restart") is not False
        or body.get("ok") is not True
    ):
        errors += fail(f"allowlisted pr fake → {code} {body}")
    else:
        errors += ok("POST /v1/sync pr AdamRickards fake → 200 no git")
    sidecar_app.pr_author_lookup = None

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
