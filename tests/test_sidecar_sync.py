#!/usr/bin/env python3
"""Offline proofs for issue #159: real op:clean + richer dirty/head reporting.

Exercises real git against throwaway local repos (never the working repo:
sidecar_app.ROOT is monkeypatched per test). No network. No live device.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ["CRUDE_SIDECAR_MODE"] = "read-only"
os.environ["CRUDE_SIDECAR_TRANSPORT"] = "fake"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sidecar.app import handle_run, handle_sync  # noqa: E402
import sidecar.app as sidecar_app  # noqa: E402

FAKE_CFG = {
    "allow_pr_authors": ["AdamRickards"],
    "repo": "example/example",
    "api_host": "example.invalid",
}


def _run(args, cwd):
    result = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, (args, result.stdout, result.stderr)
    return result.stdout.strip()


def _init_repo():
    """origin (bare-ish, with a GitHub-style refs/pull/1/head) + clone."""
    base = Path(tempfile.mkdtemp())
    origin = base / "origin"
    origin.mkdir()
    _run(["git", "init", "-b", "main"], origin)
    _run(["git", "config", "user.email", "t@example.invalid"], origin)
    _run(["git", "config", "user.name", "t"], origin)
    (origin / "f.txt").write_text("v1\n")
    _run(["git", "add", "f.txt"], origin)
    _run(["git", "commit", "-m", "v1"], origin)

    _run(["git", "checkout", "-b", "pr-branch"], origin)
    (origin / "f.txt").write_text("v2-pr\n")
    _run(["git", "commit", "-am", "v2 pr change"], origin)
    pr_sha = _run(["git", "rev-parse", "HEAD"], origin)
    _run(["git", "update-ref", "refs/pull/1/head", pr_sha], origin)
    _run(["git", "checkout", "main"], origin)
    _run(["git", "branch", "-D", "pr-branch"], origin)

    clone = base / "clone"
    _run(["git", "clone", str(origin), str(clone)], base)
    _run(["git", "config", "user.email", "t@example.invalid"], clone)
    _run(["git", "config", "user.name", "t"], clone)
    return origin, clone, pr_sha


class _Sandbox:
    """Point sidecar_app at a throwaway repo + fake sync.yaml/PR lookup."""

    def __init__(self, root):
        self.root = root

    def __enter__(self):
        self.prev_root = sidecar_app.ROOT
        self.prev_load = sidecar_app.load_sync_yaml
        self.prev_lookup = sidecar_app.pr_author_lookup
        self.prev_transport = os.environ.get("CRUDE_SIDECAR_TRANSPORT")
        sidecar_app.ROOT = self.root
        sidecar_app.load_sync_yaml = lambda: dict(FAKE_CFG)
        sidecar_app.pr_author_lookup = lambda n: "AdamRickards"
        os.environ["CRUDE_SIDECAR_TRANSPORT"] = "live"
        return self

    def __exit__(self, *exc):
        sidecar_app.ROOT = self.prev_root
        sidecar_app.load_sync_yaml = self.prev_load
        sidecar_app.pr_author_lookup = self.prev_lookup
        if self.prev_transport is None:
            os.environ.pop("CRUDE_SIDECAR_TRANSPORT", None)
        else:
            os.environ["CRUDE_SIDECAR_TRANSPORT"] = self.prev_transport


def test_dirty_tree_pr_refuses_with_dirty_and_head_detail():
    origin, clone, _pr_sha = _init_repo()
    (clone / "f.txt").write_text("local edit\n")
    with _Sandbox(clone):
        code, body = handle_sync({"op": "pr", "number": 1})
    assert code == 503, (code, body)
    assert body.get("error") == "not_ready", body
    assert body.get("op") == "pr", body
    assert any("f.txt" in d for d in body.get("dirty") or []), body
    head = body.get("head") or {}
    assert head.get("ref") == "main", body
    assert head.get("sha"), body


def test_dirty_tree_main_refuses_with_dirty_detail():
    origin, clone, _pr_sha = _init_repo()
    (clone / "untracked.txt").write_text("scratch\n")
    with _Sandbox(clone):
        code, body = handle_sync({"op": "main"})
    assert code == 503, (code, body)
    assert body.get("op") == "main", body
    assert any("untracked.txt" in d for d in body.get("dirty") or []), body


def test_clean_tree_main_and_pr_do_not_return_dirty_detail():
    origin, clone, _pr_sha = _init_repo()
    with _Sandbox(clone):
        code, body = handle_sync({"op": "main"})
        assert code == 200, (code, body)
        assert "dirty" not in body, body


def test_op_clean_discards_dirty_and_untracked_then_lands_on_main():
    origin, clone, _pr_sha = _init_repo()
    (clone / "f.txt").write_text("local edit\n")
    (clone / "untracked.txt").write_text("scratch\n")
    with _Sandbox(clone):
        code, body = handle_sync({"op": "clean"})
        assert code == 200, (code, body)
        assert body.get("ref") == "main", body
        assert body.get("ok") is True, body

    assert (clone / "f.txt").read_text() == "v1\n"
    assert not (clone / "untracked.txt").exists()
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=str(clone), capture_output=True, text=True
    )
    assert status.stdout.strip() == "", status.stdout


def test_op_clean_then_pr_proves_correct_branch():
    """Named case from #159: dirty + clean → 200, then op:pr proves the PR content."""
    origin, clone, pr_sha = _init_repo()
    (clone / "f.txt").write_text("local edit\n")
    with _Sandbox(clone):
        code, body = handle_sync({"op": "clean"})
        assert code == 200, (code, body)

        code, body = handle_sync({"op": "pr", "number": 1})
        assert code == 200, (code, body)
        assert body.get("ref") == "pr-1", body
        assert body.get("head") == pr_sha, body

    assert (clone / "f.txt").read_text() == "v2-pr\n"


def test_foreign_pr_author_still_forbidden_with_clean_available():
    """Out of scope guard: clean does not bypass the PR-author allowlist."""
    origin, clone, _pr_sha = _init_repo()
    with _Sandbox(clone):
        sidecar_app.pr_author_lookup = lambda n: "stranger"
        code, body = handle_sync({"op": "pr", "number": 1})
    assert code == 403, (code, body)
    assert body.get("error") == "forbidden", body


def test_run_receipt_echoes_sidecar_head_sha_and_ref():
    """Issue #159 bullet 3: /v1/run receipts identify which commit was tested."""
    code, body = handle_run({"name": "get_dns.read"})
    assert code == 200, (code, body)
    sidecar = body.get("sidecar") or {}
    assert sidecar.get("ref") == "main", body
    assert sidecar.get("sha"), body


def main():
    tests = [
        test_dirty_tree_pr_refuses_with_dirty_and_head_detail,
        test_dirty_tree_main_refuses_with_dirty_detail,
        test_clean_tree_main_and_pr_do_not_return_dirty_detail,
        test_op_clean_discards_dirty_and_untracked_then_lands_on_main,
        test_op_clean_then_pr_proves_correct_branch,
        test_foreign_pr_author_still_forbidden_with_clean_available,
        test_run_receipt_echoes_sidecar_head_sha_and_ref,
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
        print(f"{failed} sync proof(s) failed")
        return 1
    print("sync proofs passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
