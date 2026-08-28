#!/usr/bin/env python3
"""Render docs/status.html from program/*.yaml + TODO/ROADMAP presence.

    python3 scripts/generate_status.py
    python3 scripts/generate_status.py --check   # fail if human files missing
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import os
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("pyyaml required\n")
    sys.exit(2)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROG = os.path.join(ROOT, "docs", "program")
OUT = os.path.join(ROOT, "docs", "status.html")


def load(name):
    path = os.path.join(PROG, name)
    with open(path) as f:
        return yaml.safe_load(f)


def badge(status):
    return {
        "open": ("open", "#f5a524"),
        "doing": ("doing", "#5b9dff"),
        "done": ("done", "#3dd68c"),
        "parked": ("parked", "#8b93a7"),
        "active": ("active", "#5b9dff"),
        "shipped": ("shipped", "#3dd68c"),
        "later": ("later", "#8b93a7"),
        "FAIL": ("FAIL", "#f31260"),
        "PASS": ("PASS", "#3dd68c"),
    }.get(status, (status, "#8b93a7"))


def esc(s):
    return html.escape("" if s is None else str(s))


def render(roadmap, cycles):
    now = dt.date.today().isoformat()
    cycle_tasks = cycles.get("tasks") or []
    open_n = sum(1 for t in cycle_tasks if t.get("status") == "open")
    done_n = sum(1 for t in cycle_tasks if t.get("status") == "done")
    lab_open = [t for t in cycle_tasks if t.get("lab") and t.get("status") == "open"]
    off_open = [t for t in cycle_tasks if not t.get("lab") and t.get("status") == "open"]

    versions = roadmap.get("versions") or []
    vrows = []
    for v in versions:
        label, color = badge(v.get("status", ""))
        vrows.append(
            f"<tr><td class='mono'>{esc(v.get('id'))}</td>"
            f"<td>{esc(v.get('name'))}</td>"
            f"<td><span class='pill' style='--c:{color}'>{esc(label)}</span></td>"
            f"<td>{esc(v.get('notes', ''))}</td></tr>"
        )

    def task_card(t):
        label, color = badge(t.get("status", "open"))
        lane = "lab" if t.get("lab") else "offline"
        tags = " ".join(t.get("tags") or [])
        return (
            f"<article class='task'>"
            f"<header><span class='pill' style='--c:{color}'>{esc(label)}</span>"
            f"<span class='lane'>{esc(lane)}</span>"
            f"<h3>{esc(t.get('title'))}</h3></header>"
            f"<p class='mono tags'>{esc(tags)}</p>"
            f"<p class='proof'>proof: <code>{esc(t.get('proof'))}</code></p>"
            f"<p class='notes'>{esc((t.get('notes') or '').strip())}</p>"
            f"</article>"
        )

    next_task = next((t for t in cycle_tasks if t.get("status") in ("open", "doing")), None)
    next_html = (
        "<p class='lede'>Cycle complete. Open the next cycle from the roadmap.</p>"
        if not next_task
        else (
            f"<p class='lede'>Next task: <strong>{esc(next_task.get('title'))}</strong></p>"
            f"<p class='proof'>Run: <code>{esc(next_task.get('proof'))}</code></p>"
        )
    )

    gate = roadmap.get("gate", "?")
    g_label, g_color = badge(gate)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>crude-engine — program status</title>
<style>
:root {{
  --bg:#0b0d12; --panel:#151922; --border:#2a3142; --text:#e8ecf4;
  --muted:#8b93a7; --accent:#5b9dff;
  --font:"IBM Plex Sans","Segoe UI",system-ui,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,monospace;
}}
* {{ box-sizing:border-box; }}
html,body {{ margin:0; background:var(--bg); color:var(--text); font-family:var(--font); }}
.wrap {{ max-width:1040px; margin:0 auto; padding:28px 20px 72px; }}
h1 {{ margin:0 0 6px; font-size:26px; }}
h2 {{ margin:32px 0 12px; font-size:12px; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); }}
.kicker {{ font-family:var(--mono); font-size:11px; color:var(--muted); letter-spacing:.12em; text-transform:uppercase; }}
.lede {{ font-size:16px; color:#d5dae6; }}
.meta {{ display:flex; flex-wrap:wrap; gap:10px; margin:16px 0 8px; }}
.pill {{ --c:var(--muted); display:inline-block; border:1px solid var(--c); color:var(--c);
  border-radius:999px; padding:2px 8px; font-family:var(--mono); font-size:11px; }}
.card {{ background:var(--panel); border:1px solid var(--border); border-radius:10px; padding:16px 18px; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
table {{ width:100%; border-collapse:collapse; background:var(--panel); border:1px solid var(--border); }}
th,td {{ text-align:left; padding:8px 10px; border-bottom:1px solid var(--border); font-size:13px; vertical-align:top; }}
th {{ color:var(--muted); font-weight:500; font-size:11px; text-transform:uppercase; letter-spacing:.08em; }}
.task {{ background:var(--panel); border:1px solid var(--border); border-radius:10px; padding:12px 14px; margin:0 0 10px; }}
.task header {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; }}
.task h3 {{ margin:0; font-size:15px; flex:1; }}
.lane {{ font-family:var(--mono); font-size:11px; color:var(--muted); }}
.tags,.proof {{ font-size:12px; color:var(--muted); }}
.notes {{ font-size:13px; color:#c8cedb; white-space:pre-wrap; }}
.mono {{ font-family:var(--mono); font-size:12px; }}
code {{ font-family:var(--mono); font-size:12px; color:#cde3ff; }}
a {{ color:var(--accent); }}
footer {{ margin-top:36px; color:var(--muted); font-family:var(--mono); font-size:11px; }}
@media (max-width:800px) {{ .grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<div class="wrap">
  <p class="kicker">crude-engine program · generated {esc(now)}</p>
  <h1>Cycle {esc(cycles.get("cycle"))}: {esc(cycles.get("name"))}</h1>
  {next_html}
  <div class="meta">
    <span class="pill">now {esc(roadmap.get("current"))}</span>
    <span class="pill">target {esc(roadmap.get("target"))}</span>
    <span class="pill" style="--c:{g_color}">matrix {esc(g_label)} · {esc(roadmap.get("gate_blocking"))} blocking</span>
    <span class="pill">{done_n} done / {open_n} open</span>
    <span class="pill">host {esc(roadmap.get("host"))}</span>
  </div>
  <p class="mono">last matrix {esc(roadmap.get("last_matrix"))} · repo {esc(roadmap.get("repo"))}</p>

  <h2>How this works</h2>
  <div class="card">
    <p>SEED → ROADMAP → cycle tasks → proof command → this page. Brain is the repo. GitHub is the host.</p>
    <p class="mono">
      <a href="program/SEED.md">SEED.md</a> ·
      <a href="program/METHOD.md">METHOD.md</a> ·
      <a href="ROADMAP.md">ROADMAP.md</a> ·
      <a href="TODO.md">TODO.md</a> ·
      <a href="program/cycles.yaml">cycles.yaml</a>
    </p>
  </div>

  <h2>Offline next (do these first)</h2>
  {''.join(task_card(t) for t in off_open) or "<p class='lede'>None open.</p>"}

  <h2>Lab (after offline is green)</h2>
  {''.join(task_card(t) for t in lab_open) or "<p class='lede'>None open.</p>"}

  <h2>All cycle tasks</h2>
  {''.join(task_card(t) for t in cycle_tasks)}

  <h2>Versions</h2>
  <table>
    <thead><tr><th>id</th><th>name</th><th>status</th><th>notes</th></tr></thead>
    <tbody>{''.join(vrows)}</tbody>
  </table>

  <footer>
    Regenerated by scripts/generate_status.py. Do not edit this file.
    Offline proofs: scripts/ci_offline.sh
  </footer>
</div>
</body>
</html>
"""


def check_human_files():
    missing = []
    for rel in ("docs/ROADMAP.md", "docs/TODO.md", "docs/program/SEED.md",
                "docs/program/METHOD.md", "docs/program/cycles.yaml",
                "docs/program/roadmap.yaml"):
        if not os.path.isfile(os.path.join(ROOT, rel)):
            missing.append(rel)
    return missing


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    missing = check_human_files()
    if args.check and missing:
        print("FAIL  missing program files:")
        for m in missing:
            print(f"  {m}")
        return 1
    roadmap = load("roadmap.yaml")
    cycles = load("cycles.yaml")
    html_out = render(roadmap, cycles)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write(html_out)
    print(f"wrote {os.path.relpath(OUT, ROOT)}")
    if args.check:
        print("PASS  program files present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
