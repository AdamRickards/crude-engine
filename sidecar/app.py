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
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "tests" / "catalog.yaml"
POOL_PATH = ROOT / "tests" / "device_pool.yaml"
SYNC_YAML = ROOT / "sidecar" / "sync.yaml"
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

# Tests assign a callable(number) -> login. Live uses GitHub. Never a PAT.
pr_author_lookup = None


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


def _load_pool_devices():
    """Local gitignored pool. Empty if the file is absent."""
    if yaml is None or not POOL_PATH.is_file():
        return []
    data = yaml.safe_load(POOL_PATH.read_text()) or {}
    return list(data.get("devices") or [])


def _matches_read(dev, feature):
    """Same read resolver as generate_plan / _device_matches kind=read."""
    tests_dir = str(ROOT / "tests")
    if tests_dir not in sys.path:
        sys.path.insert(0, tests_dir)
    from release_matrix import _device_matches
    return _device_matches(dev, feature, "read")


def pick_device_ip(feature, devices=None):
    """First pool device with feature in has_capable and read in safe_for.

    Same rule as generate_plan. First match. None if none qualify.
    """
    if devices is None:
        devices = _load_pool_devices()
    if not feature:
        return None
    for dev in devices:
        ip = dev.get("ip")
        if not ip:
            continue
        ok, _reason = _matches_read(dev, feature)
        if ok:
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
        "sidecar": current_head(),
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


def call_inspect(method, device, protocol=None, trace=False):
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
        trace=bool(trace),
        username=user,
        password=password,
    )


def handle_run(payload):
    """Return (status_code, body). Refuses non-reads before inspect."""
    if not isinstance(payload, dict) or set(payload.keys()) - {"name", "trace"}:
        return 400, {"error": "bad_name", "message": 'body must be {"name": ...} or {"name": ..., "trace": true}'}
    name = payload.get("name")
    trace = bool(payload.get("trace"))
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

    feature = entry.get("feature")
    if not feature:
        return 400, {
            "error": "bad_name",
            "message": "catalog entry has no feature",
            "name": name,
        }

    device = pick_device_ip(feature)
    if transport() not in ("fake", "offline"):
        if not POOL_PATH.is_file():
            return 503, {
                "error": "not_ready",
                "message": "no local tests/device_pool.yaml (gitignored)",
                "name": name,
            }
        if not device:
            return 503, {
                "error": "not_ready",
                "message": (
                    f"no eligible device: {feature} not in has_capable "
                    "or read not in safe_for"
                ),
                "name": name,
            }

    protocol = os.environ.get("CRUDE_SIDECAR_PROTOCOL") or None

    if not LOCK.acquire():
        return 409, {"error": "lock_held", "message": "lab lock is held", "name": name}
    try:
        out = call_inspect(method, device, protocol, trace=trace)
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


def load_sync_yaml():
    """Allowlist and repo. YAML declares; Python only reads."""
    if yaml is None:
        raise FileNotFoundError("pyyaml required")
    if not SYNC_YAML.is_file():
        raise FileNotFoundError(str(SYNC_YAML))
    data = yaml.safe_load(SYNC_YAML.read_text()) or {}
    authors = [str(a) for a in (data.get("allow_pr_authors") or []) if a]
    repo = data.get("repo")
    api_host = data.get("api_host")
    if not authors:
        raise ValueError("sidecar/sync.yaml allow_pr_authors is empty")
    if not repo or not api_host:
        raise ValueError("sidecar/sync.yaml missing repo or api_host")
    return {
        "allow_pr_authors": authors,
        "repo": str(repo),
        "api_host": str(api_host),
    }


def current_head():
    """sha + ref of this checkout. Fake transport does not git."""
    if transport() in ("fake", "offline"):
        return {"sha": "fake", "ref": "main"}
    sha = _git("rev-parse", "HEAD")
    ref = _git("rev-parse", "--abbrev-ref", "HEAD")
    sha_s = sha.stdout.strip() if sha.returncode == 0 else None
    ref_s = ref.stdout.strip() if ref.returncode == 0 else None
    if ref_s == "HEAD":
        ref_s = "detached"
    return {"sha": sha_s, "ref": ref_s}


def _git(*args):
    return subprocess.run(
        ["git", *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )


def _git_sync_main():
    dirty = _git("status", "--porcelain")
    if dirty.returncode != 0:
        raise RuntimeError(dirty.stderr[-300:] or "git status failed")
    if dirty.stdout.strip():
        raise RuntimeError("working tree dirty")
    fetched = _git("fetch", "origin", "main")
    if fetched.returncode != 0:
        raise RuntimeError((fetched.stderr or fetched.stdout)[-300:])
    checked = _git("checkout", "main")
    if checked.returncode != 0:
        raise RuntimeError((checked.stderr or checked.stdout)[-300:])
    merged = _git("merge", "--ff-only", "origin/main")
    if merged.returncode != 0:
        raise RuntimeError((merged.stderr or merged.stdout)[-300:])


def _git_sync_pr(number):
    dirty = _git("status", "--porcelain")
    if dirty.returncode != 0:
        raise RuntimeError(dirty.stderr[-300:] or "git status failed")
    if dirty.stdout.strip():
        raise RuntimeError("working tree dirty")
    refspec = "pull/%d/head" % int(number)
    fetched = _git("fetch", "origin", refspec)
    if fetched.returncode != 0:
        raise RuntimeError((fetched.stderr or fetched.stdout)[-300:])
    checked = _git("checkout", "--detach", "FETCH_HEAD")
    if checked.returncode != 0:
        raise RuntimeError((checked.stderr or checked.stdout)[-300:])


def lookup_pr_author_github(number, cfg):
    """Public PR lookup. No PAT. Host comes from YAML, not a committed URL."""
    import urllib.error
    import urllib.request

    scheme = "https"
    path = "/repos/%s/pulls/%d" % (cfg["repo"], int(number))
    url = scheme + "://" + cfg["api_host"] + path
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        raise RuntimeError("PR lookup failed: %s" % exc) from exc
    user = data.get("user") if isinstance(data, dict) else None
    login = user.get("login") if isinstance(user, dict) else None
    return str(login) if login else None


def lookup_pr_author(number, cfg):
    if pr_author_lookup is not None:
        return pr_author_lookup(number)
    if transport() in ("fake", "offline"):
        return None
    return lookup_pr_author_github(number, cfg)


def _sync_restart_pending():
    """Live sync asks systemd to bring us back. Tests never set this."""
    if transport() in ("fake", "offline"):
        return False
    return True


def handle_sync(payload):
    """Return (status_code, body). Git only after allowlist. Fake skips git."""
    if not isinstance(payload, dict):
        return 400, {"error": "bad_name", "message": "body must be JSON object"}
    op = payload.get("op")
    keys = set(payload.keys())
    if op not in ("main", "pr", "clean"):
        return 400, {
            "error": "bad_name",
            "message": 'body.op must be "main", "pr", or "clean"',
        }
    if op == "pr":
        if keys - {"op", "number"}:
            return 400, {"error": "bad_name", "message": 'pr body is {"op":"pr","number": N}'}
        number = payload.get("number")
        if not isinstance(number, int) or isinstance(number, bool) or number < 1:
            return 400, {"error": "bad_name", "message": "number must be a positive integer"}
    elif keys - {"op"}:
        return 400, {"error": "bad_name", "message": 'body is {"op":"main"} or {"op":"clean"}'}

    try:
        cfg = load_sync_yaml()
    except (FileNotFoundError, ValueError) as exc:
        return 503, {"error": "not_ready", "message": str(exc)}

    if op == "pr":
        try:
            login = lookup_pr_author(number, cfg)
        except RuntimeError as exc:
            return 503, {"error": "not_ready", "message": str(exc)}
        if not login or login not in cfg["allow_pr_authors"]:
            return 403, {
                "error": "forbidden",
                "message": "PR author not allowlisted",
                "author": login,
            }

    if not LOCK.acquire():
        return 409, {"error": "lock_held", "message": "lab lock is held"}
    try:
        fake = transport() in ("fake", "offline")
        if not fake:
            try:
                if op == "pr":
                    _git_sync_pr(number)
                else:
                    _git_sync_main()
            except RuntimeError as exc:
                return 503, {"error": "not_ready", "message": str(exc)}
        if fake:
            if op == "pr":
                head = {"sha": "fake", "ref": "pr-%d" % number}
            else:
                head = {"sha": "fake", "ref": "main"}
        else:
            head = current_head()
            if op == "pr":
                head = {"sha": head.get("sha"), "ref": "pr-%d" % number}
        restart = False if fake else _sync_restart_pending()
        body = {
            "ok": True,
            "op": op,
            "head": head.get("sha"),
            "ref": head.get("ref"),
            "restart": restart,
        }
        if op == "pr":
            body["number"] = number
        return 200, body
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
        if path not in ("/v1/run", "/v1/sync"):
            self._send(404, {"error": "unknown_name", "message": "not POST /v1/run or /v1/sync"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        try:
            payload = json.loads(raw.decode("utf-8") or "null")
        except (ValueError, UnicodeDecodeError):
            self._send(400, {"error": "bad_name", "message": "body is not JSON"})
            return
        try:
            if path == "/v1/sync":
                code, body = handle_sync(payload)
            else:
                code, body = handle_run(payload)
        except Exception as exc:
            self._send(
                500,
                {
                    "error": "not_ready",
                    "message": f"{type(exc).__name__}: {exc}",
                },
            )
            return
        self._send(code, body)
        if (
            path == "/v1/sync"
            and code == 200
            and isinstance(body, dict)
            and body.get("restart")
        ):
            threading.Thread(target=_exit_after_flush, daemon=True).start()

    def do_GET(self):
        self._send(400, {"error": "bad_name", "message": "POST /v1/run or /v1/sync"})


def _exit_after_flush():
    time.sleep(0.3)
    os._exit(0)


def make_server(host, port):
    return ThreadingHTTPServer((host, port), Handler)
