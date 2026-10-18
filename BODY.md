_Requested by **tvofi**_

O17 item 2(i), from the roster-cost pre-study the orchestrator accepted on 2026-10-18 (tvofi asked to keep the roster and state docs from costing CI). Part of #201. No roster group lists an issue for this work, so this body closes none.

**Owner gate.** `.github/workflows/codeql.yml`, `.github/workflows/governance.yml`, `.github/CODEOWNERS` and the new `tools/pr/codeql_scope.py` are code-owned, so tvofi approves this at merge. The ruleset is unchanged: every required `Analyze (<leg>)` context still reports.

**What it fixes.** A pull request whose diff is a roster or a delivery row paid CodeQL's python leg, 23-26 minutes and its critical path, for an analysis of no python file. Measured in the pre-study: #2380 at `cdbca726` spent 23.5 of its 54.1 runner-minutes and 24.6 min to green on `Analyze (python)`, and the newest record PR head spent 26 min there. 76 of the 144 PRs merged since 2026-10-14 contain no `.py`, `.js` or `.yml` file.

**The change.**
- A new `scope` job in `codeql.yml`, `permissions: contents: read`, no credentials on disk. It diffs the PR three-dot and runs `tools/pr/codeql_scope.py decide` once per leg.
- `analyze` now `needs: scope` with `if: ${{ !cancelled() }}`, so a failed scope never skips a required context through `needs`. Its checkout, init and analyze steps run unless that leg's output is exactly `skip`; empty (a failed or skipped scope) analyzes. A skipped leg's job concludes `success`, which the merge rule accepts.
- The decision is fail-closed in every arm:
  - Only `pull_request` may skip. `push`, `schedule`, `merge_group` and `workflow_dispatch` always analyze, so main keeps a full analysis of every merged tree.
  - A leg skips only when every changed file's suffix is on that leg's INERT allow-list (prose and raster files, plus `.json` for python and actions only, since the javascript-typescript extractor reads JSON).
  - Any file under `.github/` analyzes every leg. An empty or unreadable list analyzes.
- `governance.yml`'s `instrument-self-tests` runs its self-test and greps the `0 failed` tally, as it does for `contract_rerun.py`. `CODEOWNERS` owns the script.

**Alternatives considered.**
1. A workflow-level `paths-ignore`. Refused: the run would not exist, the required context would never report and the merge would block.
2. The decision as workflow expressions. Refused: nothing could test it; `tests/lane_skip.py` set the precedent of a self-tested script.
3. Deciding inside `analyze`, which holds `security-events: write`. Refused for least privilege: the read-only `scope` job runs the tree's code instead.
4. A deny-list of the suffixes each extractor reads. Refused: an extension nobody listed would skip. The allow-list fails toward analysis.
5. Extending `tests/lane_skip.py`. Refused: it is item 2(ii)'s file in `handoff/r10-roster-fastpath`, and the coordinator asked for disjoint files.

## Head

`54a69b23a2a03f64ee8504e9a37ff2d5490ca9ff`, one commit on origin/main `63816b857` (`git merge origin/main` at 2026-10-18 12:50Z reported up to date).

## Mutation proof

Each mutant deletes the predicate line and the `return` under it from `decide` in a scratch copy outside the worktree (a three-line script that deletes an exact line and the next one), then runs `python3 -I <copy> --self-test`. The unmutated head prints `codeql_scope self-test: 42 checks, 0 failed`.

- **Event guard** (`if event != "pull_request":`): `42 checks, 15 failed`. Among them are `event push analyzes actions on an inert diff` and `event schedule analyzes actions on an inert diff`.
- **Suffix allow-list** (`if suffix not in INERT[language]:`, so every leg always skips): `42 checks, 10 failed`. Among them are `a .py file analyzes python (null control)`, `a .mjs file analyzes javascript-typescript (null control)` and `a roster PR analyzes javascript-typescript: its extractor reads .json`.
- **`.github/` force** (`if f.startswith(FORCE_PREFIXES):`): `42 checks, 3 failed`, the three `a .md under .github/ analyzes <leg>`.
- **Empty list** (`if not files:`): `42 checks, 2 failed`, `an empty file list analyzes` and `a blank-lines-only file list analyzes`.
- **Failing first.** The self-test run with `decide` patched to today's behaviour (always `analyze`) prints `42 checks, 7 failed`. Among them are `a roster PR skips python` and `a record PR (one .md row) skips python`.
- **CODEOWNERS.** With the new `CODEOWNERS` line removed, `python3 -I dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check` exits 1 with `UNCOVERED tools/pr/codeql_scope.py` and `uncovered_files=1`.

## Null control

- **The unmodified tree** (origin/main `63816b857`): `codeowners_gap.py --check` reads `enforcement_surface_files=85`, `covered_by_an_owner=44`, `uncovered_files=0`. At the head it reads 86, 45 and 0, and the one added file is `COVERED tools/pr/codeql_scope.py`.
- **Inside the self-test.** Every skip arm has an analyze twin one file away: the roster plus `roster_lib.py`, a row plus `brief_lint.mjs`, a row plus `.github/workflows/codeql.yml`, and the same inert row under each non-PR event.
- **This PR's own head** is the workflow-level null control. Its diff touches `.github/`, so all three legs must log `codeql scope for <leg>: analyze` and run in full. That is to be read from this head's CodeQL run, not predicted here.

## Figures

- `python3 -I tools/pr/codeql_scope.py --self-test` at the head: `codeql_scope self-test: 42 checks, 0 failed`.
- `python3 -I dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check`: base 85/44/0, head 86/45/0 (surface, owned, uncovered).
- `python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`.
- `node tools/policy/policy_lint.mjs` at the head: `TOTAL: 0 error(s) across 41 policy file(s)`.
- **Gate scope.** `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out`: `tests/entities.py` and `tests/harness_headers.py`. `harness_headers.py` ran locally (`ALL 109 HARNESS HEADER CHECKS PASSED`). `entities.py` is left to CI under the owner's heavy-scripts rule (load average 91 when measured).
- **PROJECTION, not a measurement.** For a roster or record PR after this merges, the python leg goes from 23.5 min (#2380 `cdbca726`, check-runs API, `completed_at - started_at`) and 26.1 min (the newest record head) to the length of one echo step, and its time to green loses that critical path.
  - Record PRs (one `.md`) skip all three legs.
  - Roster PRs skip python and actions and still analyze javascript-typescript (about 1.2 min on #2380).
  - The rule to re-measure on the first such head after merge: `gh api repos/tvofi/heatpump_optimizer/commits/<head>/check-runs --jq '.check_runs[] | select(.name|startswith("Analyze")) | [.name,.started_at,.completed_at] | @tsv'`, with that run's `scope` log lines.
  - This PR's own heads cannot show it, because they touch `.github/`.

## Unpinned sites

The workflow wiring (the `scope` outputs and the three step `if:`s) is pinned by no local check, since no tool drives a workflow file offline. Its proof is this head's CodeQL run (every leg analyzes: the `.github/` arm) and the first roster or record head after merge (python skips and reports `success`).

## Red checks

none

## Forward-carry

none. The remaining CodeQL-free lanes are O17 item 2(ii), built in `handoff/r10-roster-fastpath`, the coordinator's own split.

## Friction

none
