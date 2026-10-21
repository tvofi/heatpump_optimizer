ci-ratchet: list the metrics window lane by lane, and let a failed listing fail the step (fly-in R10-FLY-CI-RATCHET-WINDOW, size S).

The `ci-ratchet` step "Gather this run's and the recent window's metrics" in `.github/workflows/tests.yml` listed every artifact in the repository unfiltered (`actions/artifacts?per_page=100`), with `|| true` after it. The repository holds ~18,000 artifacts, and GitHub now answers that unfiltered listing with HTTP 500 and an empty body on most calls from the job's token. `|| true` swallowed the failure, `window.json` was empty, and the heredoc's `json.load` raised `JSONDecodeError`. Main push run 39611184226's `ci-ratchet` job (119281753833) logs `unexpected end of JSON input`, then that traceback. Per the brief, every main push run from 39585970262 onward is red the same way.

The fix:
- **`LANES` names the lanes once.** Both loops in the step read it (this run's downloads and the window). `entities.py` derives the same set from the workflow's own `actions/upload-artifact` steps named `ci-metrics-*` and refuses any disagreement. It also checks the set against `ci_ratchet.py`'s `("fast", *LANES)`.
- **The window is listed per lane by name** (`?name=ci-metrics-$lane&per_page=100`). Each listing keeps the null-safe `.workflow_run.id // .run_id` exclusion of this run, keeps the newest artifact per run, and caps at the newest 15 runs. That is the comment's own "last 15 runs" per lane, and the reader's existing `[:45]` (3 × 15) is unchanged. `jq -s add` merges the three arrays into `window.json`.
- **`|| true` is gone.** Under the step's `set -euo pipefail`, a failed listing stops the step with gh's own `HTTP <status>` line on stderr, before any window is read.

The file is code-owned: `.github/CODEOWNERS` lists `/.github/workflows/ @tvofi`, so merging needs @tvofi's approving review. `tests/entities.py` is not code-owned. `dev/audit/harnesses/r10_ci_ratchet_window_mutants.py` is new and falls under the `INERT` `dev/audit/` prefix. Its docstring carries no EXPECTED RESULT lines, so `harness_headers.py` does not execute it. Its entry under `harness_headers.py`'s inert reads in `tests/closures.json` was written by `python3 tools/pr/ci_predict.py --apply-inert`.

Alternatives considered:
- **Keep the unfiltered query and add a bounded retry.** Rejected: it still pages through every artifact in the repository to find three names, and it fails the same way the next time the artifact count grows.
- **Retry on the named query.** Not built: per-lane listings answered 200 on every call this seat made. A transient 500 now reds the job loudly instead of grading a short window. That is the direction the brief asks for.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_017ZKExRc24iNBEFEjyoUeL6

## Head

d0c4989f683541b8c4c753c7b8294c3b81ab4d5f. Measured on merge base 5d433771aa88bbfd49b8868a9b53ea1241ab85a3 (the base the brief gave). Its last commit adds only the `tests/closures.json` inert-reads entry `ci_predict.py --apply-inert` wrote for the new harness; `entities.py`, `structure.py` and `closure.py selftest` were re-run at it. The mutation run was taken at c4c5db7b, whose tracked tree differs from this head only by that entry. `origin/main` was at e7c664856776 at 2026-10-21T15:10Z. Its commits since the base touch only `tests/requirements-ci.txt`, `tests/requirements-typing.txt` and `dev/programme/delivery/2544.md`, none of them in this diff, and `git merge-tree --write-tree HEAD origin/main` merges clean. So the head was not re-cut.

## Mutation proof

`python3 dev/audit/harnesses/r10_ci_ratchet_window_mutants.py --jobs 3` runs one detached worktree per mutant at c4c5db7b, each with a full `tests/entities.py` (the runner is `r10_ci_layout_p0_mutants.py`'s, reused). `RESULT survivors=0`; every mutant reads `1 of 2377 ENTITY CHECKS FAILED`, the aimed check:
- M0 (unmutated head): PASS, `ALL 2377 ENTITY CHECKS PASSED`
- M1, `|| true` back on the per-lane listing: KILLED by "a failed artifacts listing stops the gather step before the window is read, naming the HTTP status (every listing answered 500)"
- M2, the unfiltered `artifacts?per_page=100` listing restored: KILLED by "the ci-ratchet window lists each upload lane by name, newest 15 runs each, this run excluded"
- M3, `closures` dropped from `LANES`: KILLED, same check
- M4, the `.[:15]` per-lane cap deleted: KILLED, same check
- M5, this run's exclusion replaced by `!= -1`: KILLED, same check

## Null control

The base's own step under the same stub `gh`, which answers HTTP 500 to an unfiltered artifacts listing as GitHub does. Both new checks were run against the base's `run:` text before the fix: the step exits 1 with `json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`. That is the traceback main's job 119281753833 logs, so the stub reproduces the production failure rather than one shaped to the fix. M2 is that state's listing half and M1 its `|| true` half; each goes red alone (above).

The live endpoint is the other control. The base's unfiltered query, run once from this seat at 2026-10-21T14:4xZ, answered 200 (the 500 is intermittent and token-dependent). Its window was 39 artifacts over 23 runs: closures 12, coverage 12, fast 15. The fixed step's listings over the same live repository gave 45 artifacts over 24 runs, 15 per lane. The window is comparable in size, so the fix does not silently widen what the ratchet grades.

## Figures

- Mutants: `python3 dev/audit/harnesses/r10_ci_ratchet_window_mutants.py --jobs 3` → `RESULT survivors=0`, M0 `ALL 2377 ENTITY CHECKS PASSED` (Python 3.13 venv built from `tests/requirements-ci.txt`; the seat's 3.14.7 is not downloadable here).
- Full entities at head: `PYTHONPATH=tests/hastub python3 tests/entities.py` → `ALL 2377 ENTITY CHECKS PASSED`, rc 0.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` → `MODE: FULL`, reason "`.github/workflows/tests.yml` changes the gate itself, so every closure is suspect". Locally I ran `entities.py` and the `run_always` lines: `env_drift.py --claims-only` (ok), `closure.py selftest` (`ALL 124 closure shrink pins PASSED`), `layout.py` (ok), `harness_headers.py` (`ALL 109 HARNESS HEADER CHECKS PASSED`). The rest of the full suite is left to CI. `PREPR_SKIP_CLOSURES=1` per the brief.
- Structure: `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`.
- Architecture score: `python3 tools/audit/archscore/score.py --diff origin/main HEAD` → `dS +0.0000 NULL`.
- Temp paths: `python3 -I tools/audit/seat/tmp_paths.py --check` → `0 refused`.
- Live listings, rule: for each lane in `LANES`, the fixed step's `gh api …?name=ci-metrics-$lane&per_page=100 --jq …` with `GITHUB_RUN_ID=0`, merged by `jq -s add`. Counted with `jq 'length'`, `group_by(.name)` and unique `.run`: 45 artifacts, 15 per lane, 24 runs. Base, same counting on the old unfiltered query: 39 artifacts, 23 runs.
- Seam enumeration (step 8). Rule: `grep -n 'gh api\|gh run download\||| true' .github/workflows/tests.yml` within the `ci-ratchet` job.
  - The per-lane listing: closed in this diff.
  - `gh run download … || echo` for this run's lanes: unchanged and correct. An absent lane artifact this run is a legitimate state, and it is echoed.
  - The artifact zip download in the heredoc: already `check=True`.
  - "Fetch the recent push runs' durations" `gh api …/runs?…&per_page=8`: a filtered listing with no `|| true`; it fails loudly already.

## Unpinned sites

none: `tools/pr/ci_predict.py --base origin/main` reports `no closures or fast red predicted`, and the diff adds no production line.

## Red checks

- **`ci-ratchet` on main** is the defect being fixed: it went red because the window listing's HTTP 500 was swallowed (above). It is not a required context (ruleset 23698884), but it kept main push runs red and made the tick report a false main-red.
- **`nightly-status`** grades main and reads the same red. It needs no change of its own and clears once `ci-ratchet` is green on main.

Cheaper detector: this PR adds one. `entities.py` (fast lane, every PR that touches the workflow) now runs the step's own `run:` text under a 500-answering stub, so a swallowed listing failure goes red on the PR rather than on main after the merge. Its standing cost is two bash runs of the step with a Python stub, a few seconds.

## Forward-carry

none: the finding changes no later stage's brief. The roster row R10-FLY-CI-RATCHET-WINDOW is the orchestrator's to register.

## Friction

- gate-scoping: cost: a seat's `seat_venv.sh` requires Python 3.14.7, which `uv` cannot download in this cloud container ("No download found for request: cpython-3.14.7-linux-x86_64-gnu"); I measured on a 3.13 venv from the same hash-pinned `tests/requirements-ci.txt`. Carry: dev/programme/HANDOVER.md
