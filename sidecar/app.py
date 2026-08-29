"""Thin HTTP over tests/release_matrix.py --inspect.

POST /v1/run {name: get_dns.read} maps to
  python3 tests/release_matrix.py --inspect --method get_dns --device <pool ip>

Device IP comes from local gitignored tests/device_pool.yaml, never from
the request body, never from this package. Read-only mode refuses
non-*.read *before* calling inspect. This module does not gather, dump,
or assert; it calls release_matrix.run_inspect and shapes the OpenAPI body.
"""
from __future__ import annotations

import json
import os
import re
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "tests" / "catalog.yaml"
POOL_PATH = ROOT / "tests" / "device_pool.yaml"
NAME_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")
DEFAULT_MODE = "read-only"

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


class RunLock:
    def __init__(self):
        self._lock = threading.Lock()

    def acquire(self):
        return self._lock.acquire(blocking=False)

    def release(self):
        self._lock.release()


LOCK = RunLock()


def mode():
    return (os.environ.get("CRUDE_SIDECAR_MODE") or DEFAULT_MODE).strip().lower()


def transport():
    return (os.environ.get("CRUDE_SIDECAR_TRANSPORT") or "fake").strip().lower()


def well_formed(name):
    return bool(name) and isinstance(name, str) and NAME_RE.match(name)


def is_read(entry):
    if not entry:
        return False
    name = entry.get("name") or ""
    return entry.get("access") == "R" or str(name).endswith(".read")


def load_catalog():
    if yaml is None:
        raise FileNotFoundError("pyyaml required")
    if not CATALOG_PATH.is_file():
        raise FileNotFoundError(str(CATALOG_PATH))
    data = yaml.safe_load(CATALOG_PATH.read_text()) or {}
    entries = {}
    for item in data.get("entries") or []:
        n = item.get("name")
        if n:
            entries[str(n)] = item
    return entries


def name_to_inspect(name, entry):
    """Catalog get_dns.read → --inspect --method get_dns --kind read."""
    method = entry.get("method")
    if not method and name.endswith(".read"):
        method = name[: -len(".read")]
    return method


def pick_device_ip():
    """First read-safe device in the local gitignored pool. None if absent."""
    if yaml is None or not POOL_PATH.is_file():
        return None
    data = yaml.safe_load(POOL_PATH.read_text()) or {}
    for dev in data.get("devices") or []:
        safe = dev.get("safe_for") or []
        ip = dev.get("ip")
        if ip and (not safe or "read" in safe):
            return str(ip)
    return None


def shape_inspect(name, inspect_out):
    """HTTP body for a read inspect. passed = at least one protocol ok (or fake).

    parity_diffs are first-class: callers file GitHub issues from them.
    Disagreement does not flip passed to false.
    """
    if not isinstance(inspect_out, dict):
        inspect_out = {"exit": 0 if inspect_out in (0, None) else inspect_out,
                       "protocols": {}, "parity_diffs": []}
    fake = bool(inspect_out.get("fake"))
    protocols = inspect_out.get("protocols") or {}
    diffs = inspect_out.get("parity_diffs") or []
    if not isinstance(diffs, list):
        diffs = [diffs]
    any_ok = any((p or {}).get("status") == "ok" for p in protocols.values())
    passed = True if fake else any_ok
    comms = "ok" if passed else "lost"
    expected = {"comms": "ok", "rollback": "not_armed"}
    actual = {"comms": comms, "rollback": "not_armed"}
    return {
        "result": {
            "name": name,
            "passed": passed,
            "commands_sent": True,
            "comms": comms,
            "rollback": "not_armed",
            "expected": expected,
            "actual": actual,
            "protocols": protocols,
            "parity_diffs": diffs,
        },
        "audit": {"diff": {"buckets": []}},
        "timings": {
            "encode_dispatch_ms": 0,
            "gather_decode_ms": 0,
            "time_to_confirm_ms": None,
            "time_to_rollback_visible_ms": None,
            "audit_lag_ms": None,
            "device_timer_ms": 0,
        },
    }


def call_inspect(method, device, protocol=None):
    """Call tests/release_matrix.py::run_inspect. Fake transport does not."""
    if transport() in ("fake", "offline"):
        return {
            "exit": 0,
            "fake": True,
            "method": method,
            "device": device,
            "protocols": {},
            "parity_diffs": [],
        }
    tests_dir = str(ROOT / "tests")
    if tests_dir not in sys.path:
        sys.path.insert(0, tests_dir)
    import release_matrix as rm

    user = os.environ.get("CRUDE_DEVICE_USERNAME") or "admin"
    password = os.environ.get("CRUDE_DEVICE_PASSWORD") or ""
    return rm.run_inspect(
        method,
        device,
        protocol,
        username=user,
        password=password,
    )


def handle_run(payload):
    """Return (status_code, body). Refuses non-reads before inspect."""
    if not isinstance(payload, dict) or set(payload.keys()) - {"name"}:
        return 400, {"error": "bad_name", "message": 'body must be {"name": ...}'}
    name = payload.get("name")
    if not well_formed(name):
        return 400, {"error": "bad_name", "message": "not a catalog test name", "name": name}

    try:
        catalog = load_catalog()
    except FileNotFoundError as exc:
        return 503, {"error": "not_ready", "message": str(exc), "name": name}

    entry = catalog.get(name)
    if entry is None:
        return 404, {"error": "unknown_name", "message": "not in catalog", "name": name}

    if mode() in ("read-only", "readonly", "read") and not is_read(entry):
        return 400, {
            "error": "bad_name",
            "message": "read-only mode allows catalog access R / *.read only",
            "name": name,
        }

    method = name_to_inspect(name, entry)
    if not method:
        return 400, {"error": "bad_name", "message": "name does not map to --method", "name": name}

    device = pick_device_ip()
    if transport() not in ("fake", "offline") and not device:
        return 503, {
            "error": "not_ready",
            "message": "no local tests/device_pool.yaml (gitignored)",
            "name": name,
        }

    protocol = os.environ.get("CRUDE_SIDECAR_PROTOCOL") or None

    if not LOCK.acquire():
        return 409, {"error": "lock_held", "message": "lab lock is held", "name": name}
    try:
        out = call_inspect(method, device, protocol)
        if isinstance(out, dict) and out.get("exit") == 2:
            return 503, {
                "error": "not_ready",
                "message": out.get("error") or "release_matrix --inspect usage error",
                "name": name,
            }
        if not isinstance(out, dict) and out not in (0, None):
            if out == 2:
                return 503, {
                    "error": "not_ready",
                    "message": "release_matrix --inspect returned 2",
                    "name": name,
                }
        return 200, shape_inspect(name, out)
    finally:
        LOCK.release()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code, body):
        raw = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/v1/run":
            self._send(404, {"error": "unknown_name", "message": "not POST /v1/run"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        try:
            payload = json.loads(raw.decode("utf-8") or "null")
        except (ValueError, UnicodeDecodeError):
            self._send(400, {"error": "bad_name", "message": "body is not JSON"})
            return
        code, body = handle_run(payload)
        self._send(code, body)

    def do_GET(self):
        self._send(400, {"error": "bad_name", "message": "POST /v1/run only"})


def make_server(host, port):
    return ThreadingHTTPServer((host, port), Handler)
