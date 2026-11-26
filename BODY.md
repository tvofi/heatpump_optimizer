#3885 L5 (design `design.md` on `design/r11-ci-3885-queue` at 43ff5ae6c1464d640acbce4ee03ab7cd23579c26, approved at adbd80a4): ci.yml's `refresh` and `cancel-superseded` jobs held the same grant (`contents: read`, `pull-requests: read`, `actions: write`) and both acted at the pull-request event, so every event paid two runner allocations and two checkouts. `refresh` is now the last step of `cancel-superseded`:
- one checkout (`fetch-depth: 2`, `persist-credentials: false`) and one restore of the base's `tools/pr/cancel_superseded.py` and `tools/ci/*.py`, before any step holds the token;
- the cancel step keeps its old job condition as a step `if:` (pull_request, non-bot sender, same-repo head);
- the refresh step runs on pull_request and review events, fork heads included, as its job did; `!cancelled() && steps.restore.outcome == 'success'` keeps it independent of the cancel step's outcome (the two were separate jobs) and never lets it run the head's `tools/ci` after a failed restore;
- `timeout-minutes: 5`, the larger of the two.
Alternative not taken: keeping the job name `refresh` and folding cancel into it; the design names `cancel-superseded` as the survivor, and the name is what `tests/entities.py`'s supersession pins read. Leaves #3885 open.

## Head

4f0c7af26b961b8478d2ac2e24368f7d08a956cf on `origin/main` fd93aa3e9b161e92ead26e04ba8311b3fc0fc7e5 (2026-11-26T23:37:45Z).

## Mutation proof

`PYTHONPATH=tests/hastub python3 tests/entities.py` at three mutants of the head's ci.yml (each a detached worktree at the head):
- M1, ci.yml back to the base (two jobs): 3 failed -- `FAIL a body edit starts a run of the contract job and the budget gate, and of no other job` (lists `refresh`), `FAIL #3885 L5: the same job re-runs the stale green gates ...`, `FAIL and the same ci.yml and tests.yml with their restores and token hygiene undone are refused ...` (refuses `ci.yml:refresh` too)
- M2, the refresh step's `if:` deleted: 1 failed -- `FAIL #3885 L5: the same job re-runs the stale green gates ...` (no `!cancelled()` and restore guard)
- M3, the cancel step's `if:` deleted: 1 failed -- `FAIL ci.yml's cancel-superseded cancels a superseded older SHA, from the base's program, on a non-bot same-repo pull_request run only` (a review event, a bot sender and a fork head would cancel)

Diff mutants: the diff adds no Python outside `tests/` and `dev/` (ci.yml and `tests/entities.py` only), so `mutant_run.py` draws no mutant; the three hand mutants above are the proof.

## Unpinned sites

none: no Python outside `tests/` and `dev/` is added, so no diff mutant is drawn.

## Null control

At the base (fd93aa3e9b) `tests/entities.py` reads the two jobs; the new L5 row's nulls are inside it: push and workflow_dispatch admit no housekeeping job, and the cancel step is false on a review event, a bot sender and a fork head (each an `_if_under` evaluation in the row `ci.yml's cancel-superseded cancels a superseded older SHA ...`). The token-hygiene control (`... refused on each of the three autofix jobs ... and on ci.yml's cancel-superseded and sweep-self jobs (null control)`) still refuses the folded job once its restore is undone.

## Figures

- Housekeeping jobs per pull_request event: base 2 (`refresh`, `cancel-superseded`), head 1; rule: `python3 -c "import yaml; print(sorted(yaml.safe_load(open('.github/workflows/ci.yml'))['jobs']))"` -- base lists both names, head lists `cancel-superseded` and no `refresh`.
- Cost being removed, one run's own listing (`list_workflow_jobs` of CI run 45907700288, attempt 1, 2026-11-26): `refresh` 75 s from start to completion (checkout 8 s, base fetch 63 s), `cancel-superseded` 13 s (checkout 7 s); run 45891233921: `refresh` 49 s, `cancel-superseded` 12 s. The folded job pays one allocation and one checkout; the base fetch moves into its restore step (the cancel step skipped it when the pin was already in the depth-2 clone). The design's harness `census` arm figure (11-25: 329 + 143 runner-min over 254 + about 150 jobs) was not re-run: `ci3885_queue.py fetch` shells `gh api`, which this container does not run; GitHub is reachable here only through the MCP tools. After: owed on the first busy day past the merge (the arm reads CI history).
- Architecture score: not run (workflow and test only).

## Red checks

none

## Forward-carry

none

## Friction

none
