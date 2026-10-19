R10-CI-LAYOUT PR 0: the inert `ci.yml` stub (DESIGN-P1 step 5b), and the three ci-ratchet payments the design review placed in PR 0 (`DESIGN-REVIEW.md` section 3, rows PR 0-R(a), R(b) and R(c)). The stub lets `workflow_dispatch` dispatch the umbrella from `probe/ci-layout-*` refs. GitHub dispatches only a file that is on the default branch, so without the stub on main the fan-out's live work cannot run. The payments turn main's red `ci-ratchet` job green. It has failed on main's push runs with `GREW critical_path_minutes` and `GREW script_runs_per_push`, and it failed again at this branch's base: push run 39310145738 at `4a3cbcf62`, job `ci-ratchet`, conclusion `failure`.

- **stub**: `.github/workflows/ci.yml`, `name: CI`, `on: workflow_dispatch` only, with the inputs `pr`, `base`, `recheck` and `no-skip` (each an optional string, so PR 2's dispatches already validate). It has `permissions: {}` at both levels and one job `stub` that runs `true`. `tests/entities.py` pins it inert, and `tests/closure.py` lists it in `GATE_FILES`.
- **R(a)**: `tests/arch_score.py` and `tests/arch_score_head.py` move from `lane_units` to `lane_golden` in `tests/run.sh`. `lane_units` ends last in CI's `fast` job. The total work is unchanged: the move only changes which lane runs the pair. An entities pin holds the placement.
- **R(b)**: `tools/coverage/coverage_tree.sh`'s floor re-validation re-measures only the scripts it reused, not all of them. Push run 39213675232 re-ran all 20 scripts, `entities` twice. Each script it re-measures loses its `reused` row in `scripts.tsv` and `per/provenance.tsv`, so each script still has exactly one row in each. The review's `_coverage_revalidation` test, with its floor-met null, is landed.
- **R(c)**: `tests/ci_ratchet.py` `script_runs()` stops counting a `reused` coverage row. Such a row is a copy of the base's data and executes nothing. `script_runs_per_push` is re-recorded from 68 down to 53, the every-script-measured-once count, re-derived below. **This is a tightening, not a raise**: excluding the 19 reused rows alone would have loosened the ratchet by 19 without anyone deciding it. The review's `_CIR_REUSE` test and its null are landed. A planted extra script run turns the ratchet red, and the budget is pinned equal to the count derived from the two instruments' own enumerations.

Alternatives considered (fixer step 17). For (a), a separate job for the arch-score pair would add a check name and a runner for the same work, so it lost to the lane move, as the review found. For (b), keeping the full re-measure and only excluding its rows from the count would have hidden the duplicate execution without removing it, so it lost: the duplicate re-run is the cost, and it is also what made efdc055a's run take 67.0 min. For (c), recording the window maximum (about 34 on a floor-met push) would turn a legitimate floor-FAIL push red. Under (b) such a push measures each script once, so the count it must stay under is the every-script-once count, not the window maximum.

## Head

`385b3a0d375b68f53d016c8b53eea7956a906fee`. Its merge base is origin/main `4a3cbcf62e6f5e7b6594d376d714388caf2915cf`, which was also origin/main's tip at 2026-10-19T20:23Z, so this head carries no merge. The head is four commits on that base: the change (`71f0bb69f`); the budget-equality pin (`b30ca33fe`, added after mutant M6 survived the first proof, see below); the mutation harness (`a83a01a5a`); and `tests/closures.json` recording that harness as an inert read of `tests/harness_headers.py` (`385b3a0d3`, written by `tools/pr/ci_predict.py --apply-inert` after prepr's ci-predict step refused). The full harness ran at `a83a01a5a`. The last commit edits only that one data row, which none of the mutated files or aimed checks read, so M0 was re-run at this head (below). Every local figure was taken on this seat with CPython 3.14.7, the seat interpreter.

## Mutation proof

`python3 dev/audit/harnesses/r10_ci_layout_p0_mutants.py`, run from the head's worktree. Each mutant gets its own detached worktree of HEAD and one text substitution that must apply exactly once, and then a full `PYTHONPATH=tests/hastub python3 tests/entities.py` run. A mutant reads KILLED only when entities exits non-zero **and** one of the checks it is aimed at is among the FAIL lines. Any other red reads OFF-TARGET, which counts as a survivor.

At the head, rc=0:

```
M0 PASS rc=0 | ALL 2356 ENTITY CHECKS PASSED | aimed red: []
M1 KILLED rc=1 | 1 of 2356 ENTITY CHECKS FAILED | aimed red: ['the ci.yml umbrella stub is inert: dispatch only, one `true` job, no grant, no `uses:`, and a gate file']
M2 KILLED rc=1 | 2 of 2356 ENTITY CHECKS FAILED | aimed red: ['the ci.yml umbrella stub is inert: dispatch only, one `true` job, no grant, no `uses:`, and a gate file']
M3 KILLED rc=1 | 1 of 2356 ENTITY CHECKS FAILED | aimed red: ['the architecture-score pair runs in lane_golden and not in lane_units']
M4 KILLED rc=1 | 1 of 2356 ENTITY CHECKS FAILED | aimed red: ['the coverage floor re-validation re-measures only the scripts it reused']
M5 KILLED rc=1 | 2 of 2356 ENTITY CHECKS FAILED | aimed red: ['the CI ratchet counts no `reused` coverage row as a script run']
M6 KILLED rc=1 | 1 of 2356 ENTITY CHECKS FAILED | aimed red: ['one script run past the every-script-once budget turns the CI ratchet red, and the budget is that count']
RESULT survivors=0
```

What each mutant breaks, and the failing check's own text from the first proof run (at `71f0bb69f`, the same mutants applied by hand in six worktrees):
- M1, stub: a `push:` trigger is added to `ci.yml`. Fails `the ci.yml umbrella stub is inert: ...` with `defects=["triggers ['push', 'workflow_dispatch'] (want only workflow_dispatch)"]`.
- M2, stub: `ci.yml` is removed from `GATE_FILES`. Fails the same check with `gate=False`. It also fails `every tracked file is either measured or deliberately classified` (`these force the FULL suite when touched: .github/workflows/ci.yml`).
- M3, R(a): `arch_score_head.py` goes back into `lane_units`. Fails `the architecture-score pair runs in lane_golden and not in lane_units` with `in lane_units: ['run "$PYTHON" tests/arch_score_head.py']`.
- M4, R(b): the base's re-measure-everything lines are restored. Fails `the coverage floor re-validation re-measures only the scripts it reused`: under a floor FAIL, executions `{'entities': 2, 'block_duty': 2, ..., 'frontend': 2, 'features': 1}`, so every fresh script ran twice and the reused one ran once.
- M5, R(c): `and r["class"] != "reused"` is deleted. Fails `the CI ratchet counts no `reused` coverage row as a script run` (`two reused copies beside two executions counted 4 (want 2)`). It also fails the planted-run check, because 20 reused copies push the exact-budget null to 73.
- M6, the recorded budget: 53 becomes 54. **It survived the first proof**: the planted-run check read its budget from `ci_budgets.json`, so a loosened budget still passed (`ALL 2356 ENTITY CHECKS PASSED`). `b30ca33fe` fixes the check. It now derives the every-script-once count with `_cir_once_count()`, from `closure.test_scripts()` less `SLOW_GATED`, less `closure.composed_scripts()`, plus coverage_tree.sh's own `DERIVED` and `fast)` lines run by bash, and requires the budget to equal that count. The harness re-runs M6 against that check.

Every mutant is applied to a disposable worktree, never to the head's tree. `git -C <head worktree> status --short` printed nothing after the run.

## Null control

- M0, the unmutated head: `python3 dev/audit/harnesses/r10_ci_layout_p0_mutants.py M0` at `385b3a0d3` printed `M0 PASS rc=0 | ALL 2356 ENTITY CHECKS PASSED` and `RESULT survivors=0`. At `a83a01a5a` the full harness printed the same M0 line (the first line of the result block above).
- Each new check carries its own null, run inside every entities run:
  - The stub check runs the same parser over three planted stubs (a `push:` trigger, a `contents: read` grant, a second job), and each must report a defect, so a parser that reads nothing fails.
  - The placement pin reads `structure.py` inside `lane_units`, so a lane reader that returns empty fails.
  - `_coverage_revalidation(floor_fails=False)` must leave the reused script unexecuted.
  - `_CIR_REUSE_NULL` relabels the same rows `scoped`, and they count 4.
  - `_cir_planted(0)` puts exactly the budget's executions beside 20 reused copies, and they must grade `ok`.
- `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`. `PYTHONPATH=tests/hastub python3 tests/closure.py selftest` printed `ALL 124 closure shrink pins PASSED`. `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` printed `CI PREDICT: no closures or fast red predicted against 4a3cbcf62e6f`. `python3 -I tools/audit/seat/tmp_paths.py --check` printed `0 refused`.

**The CI controls, owed by CI rather than this seat** (fixer step 5: heavy lanes run in CI and are cited by check-run):
1. **The FULL-run control (review section 3, R(a) stage one).** On this PR's own FULL Tests run, the `fast (3.14)` job must end at least 5 min sooner than it ended on its base's FULL run. The offset is the job's `completed_at` minus the run's `created_at`. The base's FULL run is push run 39310145738 at `4a3cbcf62`, where `fast (3.14)` ran 19:20:27Z → 20:18:11Z on a run created at 19:20:23Z, an offset of 57.8 min. So this PR's `fast (3.14)` must end within 52.8 min of its run's creation. That run is a `pull_request` run and the comparator is a `push` run. Both are FULL, because this diff edits a gate file and a push forces FULL, but the event classes differ. Stage two below compares push with push. If this control fails, R(a) did not pay: the A3 Fallback applies, and the stub ships alone.
2. **The window rule, the post-merge control (review B4).** `script_runs_per_push` must be green on the first push run after the merge. `critical_path_minutes` is the median wall time of the 8 newest completed push Tests runs, so it goes green only once **at least 5 of those 8** fall under 54.825 min, about 5 merges after this one. A red `ci-ratchet` on the first push runs after the merge is that window still filling, not a failed payment. **Never re-run a push Tests run to check**: a re-run moves `updated_at`, and that run's wall time then counts the whole gap. If the window is still red 6 push runs after this merge, stop and re-measure. The model's 4-worker contention bound is the assumption most likely to fail, and a raise is the last resort, under rule 2.

## Figures

- `MODE: FULL`, `reason: .github/workflows/ci.yml changes the gate itself`: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"; cat "$D/scope.txt"`. This is expected: the diff edits three gate files, `tests/run.sh`, `tests/closure.py` and `.github/workflows/ci.yml`.
- The every-script-measured-once count, 53 = 34 − 1 + 20, from the tree at `4a3cbcf62`:
  - 34: `PYTHONPATH=tests/hastub python3 tests/closure.py lane-plan --all-scripts --out-dir "$D"; wc -l < "$D/scripts.txt"`, the closures lane's full plan.
  - 1: `tests/composed_closures.json` `scripts`, which lists `tests/boost_drift_replay.py`. The closures lane consumes it from the coverage job and does not re-record it.
  - 20: coverage_tree.sh's `DERIVED` pipeline and its `fast)` filter, which is `grep -oE 'run "\$PYTHON" tests/[a-z_]+\.py' tests/run.sh | sed 's#.*tests/##;s#\.py##' | awk '!seen[$0]++' | grep -vxE "arch_score|arch_score_head" | grep -vxE "env_drift|rolling|stress|validate|edge|backtest|optimality" | wc -l`.
  - The same figure, as entities derives it: `_cir_once_count()` returns `(53, [])` at the head. The null, M6, is a budget of 54 against that count.
- The window cross-check, from the CI-RATCHET-RED planning seat's saved ci-metrics artifacts (one zip per artifact, read with `tests/ci_ratchet.read_metrics` and counted per push run by lane and class; the copies are out of tree, so this is an unverified cross-check). The three push runs without reuse, 39213947578, 39217093836 and 39217450549, read closures `full` 33 + coverage `full` 20 = 53 each. Push run 39213675232 (efdc055a) read 33 + 19 `reused` + 21 `scoped` = 73, the GREW reading. Its coverage `scoped` rows hold `entities` twice: one fresh run, then the re-validation re-ran all 20. Push run 39216811946 read closures 34 (`boost_drift_replay` was recorded bare because coverage reused it) + 16 `reused` + 4 `scoped`. That is 54 under the old rule and 38 under the new one.
- The old budget, 68: `tests/ci_budgets.json` `script_runs_per_push` at `4a3cbcf62` (`git show 4a3cbcf62:tests/ci_budgets.json`).
- The base's `fast (3.14)` end offset, 57.8 min: `gh api 'repos/tvofi/heatpump_optimizer/actions/runs/39310145738/jobs?per_page=100' --jq '.jobs[] | select(.name|test("^fast")) | [.started_at,.completed_at]'`, with the run's `created_at` from `gh api repos/tvofi/heatpump_optimizer/actions/runs/39310145738`.

## Red checks

At the time of this handoff there is no CI run at this head (the orchestrator opens the PR). Two reds are expected:
- `closures` UNDER-SCOPED, followed by one `closures-autofix` cycle: `tests/entities.py` now reads `.github/workflows/ci.yml` and runs `tools/coverage/coverage_tree.sh` under a stub, so its recorded closure grows. Its answer is `ci-autofix.md`'s: the bot's `ci: re-record closures` from the Linux recording. It is named here, not analysed (fixer, "answer any check your branch turned red").
- `ci-ratchet` on this PR's run, if the job runs on `pull_request`, and on the first push runs after the merge, for `critical_path_minutes` only, until the window rule above is met. That job is red at the base as well (push run 39310145738), so it is not a red this branch introduces.

## Unpinned sites

n/a: prepr step 6d reports that the diff adds no unpinned mutation site.

## Forward-carry

- PR 1's W1 deletes the composed-closure path (`tests/composed_closures.json`, DESIGN-P1 step 5a). After that, the closures lane records `boost_drift_replay.py` bare on every FULL push, and the every-script-once count becomes 54. This PR's budget-equality check (`_cir_once_count()` against `script_runs_per_push`) then refuses until PR 1 re-derives the count and re-records the budget, with the reason stated in that commit. R(b)'s `_coverage_revalidation` must also stay green across W1 (review section 3). Carry: R10-CI-LAYOUT
- U9's re-keyed `ci_ratchet.py` reader (PR 2) must keep R(c)'s `reused` exclusion, `_CIR_REUSE` and the budget-equality pin unchanged (review section 3, "After PR 2"). Carry: R10-CI-LAYOUT
- R10-STAMP: `stamp.py` rule 2 needs a green Tests push run at HEAD, and `ci-ratchet` is part of that run. The stamp can run once the B4 window above reads green, which is before PR 1 (review B7). It must not wait for the first push run after this merge alone. Carry: R10-STAMP

## Friction

none

## Approval

`tests/run.sh` and `.github/workflows/` are code-owned by tvofi (`.github/CODEOWNERS`), so this diff merges only on tvofi's approving review at its head, or under tvofi's mandate on #201, comment 6175172275, whose first line reads verbatim: "MANDATE: agents may approve as tvofi, scope all, from 2026-10-14T18:14Z until 2026-10-28T18:14Z". The PR 0 split and its contents (the stub plus R(a)-(c)) are the design review's amended packaging (A3), approved under the R10 grant ("decisions = recommended"). The `script_runs_per_push` re-record is a tightening, 68 → 53, so it needs no `## Raise justification`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
