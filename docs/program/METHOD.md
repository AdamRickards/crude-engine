# METHOD — seed → cycle → proof → next

Read this when you sit down to work, or when an agent resumes.

## Daily loop

1. Open `docs/status.html` (or run `python3 scripts/generate_status.py`).
2. Open `docs/program/cycles.yaml`. Take the first task with `status: open`.
3. Read its `proof`. Run it. Watch it fail (or confirm it still fails).
4. Do the smallest change that can make that proof pass.
5. Re-run **all** of `scripts/ci_offline.sh`. Do not "just run the one check."
6. If the proof is a lab proof (`lab: true`), use `tests/release_matrix.py --inspect` first, then the surgical execute, then `--render`.
7. Mark the task `done` in `cycles.yaml`. If it shipped a user-visible fix, record the tag in `CHANGELOG.md`. Comment-close the GitHub issue.
8. Regenerate status. Commit when git exists.

## What each file is allowed to be

| File | Authority | Who edits |
|------|-----------|-----------|
| `docs/program/SEED.md` | Destination + bans | Human, rarely |
| `docs/program/roadmap.yaml` | Version exit criteria (machine) | Human when the destination moves |
| `docs/ROADMAP.md` | Same, for reading | Human; keep aligned with yaml |
| `docs/program/cycles.yaml` | Current iteration tasks | Human or agent; one cycle |
| GitHub issues | Leftover work (prove-then-file or comment-close) | Not `docs/TODO.md` / `TODO_HITLIST.md` |
| `docs/RELEASE_MATRIX.md` | Gate scoreboard | **Generated only** |
| `docs/API_REFERENCE.md` | Catalogue rendering | **Generated only** (`generate_docs.py`) |
| `docs/status.html` | Poster | **Generated only** (`generate_status.py`) |

If two files disagree, the machine file wins and the human file is regenerated or fixed.

## Two proof lanes

| Lane | Command | Needs hardware | Blocks |
|------|---------|----------------|--------|
| Offline / PR | `scripts/ci_offline.sh` | No | Every change |
| Release / lab | `scripts/ci_release.sh` (wraps matrix) | Yes | 2.10.0 tag |

A change that makes offline CI red does not ship, even if it "fixes" a lab cell.

## Adding a task

Append to `cycles.yaml`:

```yaml
- id: short-kebab
  title: One sentence
  tags: ["#bucket", "#Short-Id"]
  proof: "the exact command"
  lab: false
  status: open
  notes: "why / where / what done looks like"
```

`#bucket #Short-Id` follows `docs/RELEASE_GATE.md`. A tag lives in a GitHub issue **or** ROADMAP.md, never both.

## Closing a cycle

When every task in the cycle is `done` or `parked`:

1. Bump or keep `cycle:` number.
2. Comment-close leftover GitHub issues for this cycle (what this cycle proved).
3. Open the next cycle from the remaining ROADMAP exit criteria.
4. Do not open tools/NILS work as a cycle until 2.10 exit is met or explicitly parked.

## GitHub, when it exists

```
git init
git add …
git commit -m "program: seed, roadmap, cycle 0"
gh repo create AdamRickards/crude-engine --private --source=. --remote=origin --push
```

Then Actions run `scripts/ci_offline.sh` on every push. Releases still use `.github/workflows/publish-to-pypi.yml`.

Issues may be opened from `cycles.yaml` as a convenience. If an Issue disagrees with `cycles.yaml`, the yaml is right.

## Resume after context loss

1. `docs/program/SEED.md`
2. `docs/status.html`
3. `docs/program/cycles.yaml` — first `open` task
4. `docs/RELEASE_GATE.md` only if the task is a matrix/lab proof
5. `docs/DIAGNOSTIC_PROCESS.md` only if a live method is failing
