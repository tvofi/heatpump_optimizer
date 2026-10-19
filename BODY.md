R10-CI-LAYOUT PR 0: the inert `ci.yml` stub (DESIGN-P1 step 5b), and the three ci-ratchet payments the design review placed in PR 0 (`DESIGN-REVIEW.md` section 3, rows PR 0-R(a), R(b) and R(c)). The stub lets `workflow_dispatch` dispatch the umbrella from `probe/ci-layout-*` refs. GitHub dispatches only a file that is on the default branch, so without the stub on main the fan-out's live work cannot run. The payments turn main's red `ci-ratchet` job green. It has failed on main's push runs with `GREW critical_path_minutes` and `GREW script_runs_per_push`, and it failed again at this branch's base: push run 39310145738 at `4a3cbcf62`, job `ci-ratchet`, conclusion `failure`.

- **stub**: `.github/workflows/ci.yml`, `name: CI`, `on: workflow_dispatch` only, with the inputs `pr`, `base`, `recheck` and `no-skip` (each an optional string, so PR 2's dispatches already validate). It has `permissions: {}` at both levels and one job `stub` that runs `true`. `tests/entities.py` pins it inert, and `tests/closure.py` lists it in `GATE_FILES`.
- **R(a)**: `tests/arch_score.py` and `tests/arch_score_head.py` move from `lane_units` to `lane_golden` in `tests/run.sh`. `lane_units` ends last in CI's `fast` job. The total work is unchanged: the move only changes which lane runs the pair. An entities pin holds the placement.
- **R(b)**: `tools/coverage/coverage_tree.sh`'s floor re-validation re-measures only the scripts it reused, not all of them. Push run 39213675232 re-ran all 20 scripts, `entities` twice. Each script it re-measures loses its `reused` row in `scripts.tsv` and `per/provenance.tsv`, so each script still has exactly one row in each. The review's `_coverage_revalidation` test, with its floor-met null, is landed. Round 2 adds a check that reads both ledgers: after a floor-FAIL re-validation, each holds one row per script and no `reused` row.
- **R(c)**: `tests/ci_ratchet.py` `script_runs()` stops counting a `reused` coverage row. Such a row is a copy of the base's data and executes nothing. `script_runs_per_push` is re-recorded from 68 down to 53, the every-script-measured-once count, re-derived below. **This is a tightening, not a raise**: excluding the 19 reused rows alone would have loosened the ratchet by 19 without anyone deciding it. The review's `_CIR_REUSE` test and its null are landed. A planted extra script run turns the ratchet red, and the budget is pinned equal to the count derived from the two instruments' own enumerations.

Alternatives considered (fixer step 17). For (a), a separate job for the arch-score pair would add a check name and a runner for the same work, so it lost to the lane move, as the review found. For (b), keeping the full re-measure and only excluding its rows from the count would have hidden the duplicate execution without removing it, so it lost: the duplicate re-run is the cost, and it is also what made efdc055a's run take 67.0 min. For (c), recording the window maximum (about 34 on a floor-met push) would turn a legitimate floor-FAIL push red. Under (b) such a push measures each script once, so the count it must stay under is the every-script-once count, not the window maximum.

## Head

`b4d7bf9c748caa93b8baf2ce013961bb9d273d4f`. Its merge base is origin/main `4a3cbcf62e6f5e7b6594d376d714388caf2915cf`. Round 2 adds four commits to the round-1 head `c5b5d06c3`, the bot's `ci: re-record closures` over `4d1730bd1`, the delivery row:
- `544b5dbaf` pins the coverage ledgers (round-1 item 2, mutant M7) and adds M7 to the harness.
- `d4f2e06a6` adds `dev/audit/harnesses/r10_ci_layout_p0_fast_offsets.py`, the FULL-run control as an instrument (round-1 item 1).
- `b4d7bf9c7` records that harness as an inert read of `tests/harness_headers.py` (`tools/pr/ci_predict.py --apply-inert`).

origin/main has since moved to `d1db05dfc`. This head is not re-merged: after the handoff, that merge is the orchestrator's (fixer step 6). Every local figure was taken on this seat with CPython 3.14.7, the seat interpreter.

## Mutation proof

`python3 dev/audit/harnesses/r10_ci_layout_p0_mutants.py`, run from the head's worktree at `544b5dbaf`. Each mutant gets its own detached worktree of HEAD and one text substitution that must apply exactly once, then a full `PYTHONPATH=tests/hastub python3 tests/entities.py` run. A mutant reads KILLED only when entities exits non-zero **and** one of its aimed checks is among the FAIL lines. Any other red reads OFF-TARGET and counts as a survivor. The commits after `544b5dbaf` touch only the two harness files and one `closures.json` inert row, and none of them is a mutated file or an aimed check. M0 was re-run at the head (Null control). rc=0:

```
M0 PASS rc=0 | ALL 2357 ENTITY CHECKS PASSED | aimed red: []
M1 KILLED rc=1 | 1 of 2357 ENTITY CHECKS FAILED | aimed red: ['the ci.yml umbrella stub is inert: dispatch only, one `true` job, no grant, no `uses:`, and a gate file']
M2 KILLED rc=1 | 1 of 2357 ENTITY CHECKS FAILED | aimed red: ['the ci.yml umbrella stub is inert: dispatch only, one `true` job, no grant, no `uses:`, and a gate file']
M3 KILLED rc=1 | 1 of 2357 ENTITY CHECKS FAILED | aimed red: ['the architecture-score pair runs in lane_golden and not in lane_units']
M4 KILLED rc=1 | 1 of 2357 ENTITY CHECKS FAILED | aimed red: ['the coverage floor re-validation re-measures only the scripts it reused']
M5 KILLED rc=1 | 2 of 2357 ENTITY CHECKS FAILED | aimed red: ['the CI ratchet counts no `reused` coverage row as a script run']
M6 KILLED rc=1 | 1 of 2357 ENTITY CHECKS FAILED | aimed red: ['one script run past the every-script-once budget turns the CI ratchet red, and the budget is that count']
M7 KILLED rc=1 | 1 of 2357 ENTITY CHECKS FAILED | aimed red: ['after a floor-FAIL re-validation each coverage ledger holds one row per script and no `reused` row']
RESULT survivors=0
```

What each mutant breaks:
- M1, stub: a `push:` trigger is added to `ci.yml`.
- M2, stub: `ci.yml` is removed from `GATE_FILES`.
- M3, R(a): `arch_score_head.py` goes back into `lane_units`.
- M4, R(b): the base's re-measure-everything lines are restored. Under a floor FAIL every fresh script then runs twice.
- M5, R(c): `and r["class"] != "reused"` is deleted.
- M6, the recorded budget: 53 becomes 54. Since round 1, the check requires the budget to equal `_cir_once_count()`, which is derived from `closure.test_scripts()` less `SLOW_GATED` and `composed_scripts()`, plus coverage_tree.sh's own `DERIVED` and `fast)` lines run by bash.
- **M7, the round-1 survivor**: the `for _f in scripts.tsv provenance.tsv; awk '$2!="reused"'` loop is deleted (the reviewer's `m7.diff`). It is now killed by `after a floor-FAIL re-validation each coverage ledger holds one row per script and no `reused` row`. `_coverage_revalidation` returns both ledgers, read from `out/scripts.tsv` and `out/per/provenance.tsv`. Under a floor FAIL, each must hold each executed script once with 0 `reused` rows. With M7, each holds 21 rows, 1 of them `reused`, which is the reviewer's `m7_ledger_mutant.txt` reading.

## Null control

- M0, the unmutated head: `python3 dev/audit/harnesses/r10_ci_layout_p0_mutants.py M0` at `b4d7bf9c7` printed `M0 PASS rc=0 | ALL 2357 ENTITY CHECKS PASSED` and `RESULT survivors=0`. The full harness at `544b5dbaf` printed the same M0 line (the first line of the block above).
- Each new check carries its own null, run inside every entities run:
  - The stub check runs the same parser over three planted stubs (a `push:` trigger, a `contents: read` grant, a second job), and each must report a defect, so a parser that reads nothing fails.
  - The placement pin reads `structure.py` inside `lane_units`, so a lane reader that returns empty fails.
  - `_coverage_revalidation(floor_fails=False)` must leave the reused script unexecuted. On that same arm, the new ledger check requires exactly one `reused` row in each ledger, so a reader that sees no rows fails.
  - `_CIR_REUSE_NULL` relabels the same rows `scoped`, and they count 4.
  - `_cir_planted(0)` puts exactly the budget's executions beside 20 reused copies, and they must grade `ok`.
- `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`. `PYTHONPATH=tests/hastub python3 tests/closure.py selftest` printed `ALL 124 closure shrink pins PASSED`. `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` printed `CI PREDICT: no closures or fast red predicted against 4a3cbcf62e6f`. `python3 -I tools/audit/seat/tmp_paths.py --check` printed `0 refused`.

**The FULL-run control (review section 3, R(a) stage one): round 1 failed it on one run; round 2 re-measures it on a run set.** Round 1's single run, 39333417268, ended `fast (3.14)` 53.13 min after the run was created, against a 52.8 min bar (57.80 at the base's push run, less 5). Its job duration was 51.85 min, but its queue was 1.28 min, against 0.05-0.08 min on every base push run below. The single-run bar sits inside the noise of its own comparator: the base layout's FULL runs end `fast` anywhere from 53.85 to 59.57 min, or 34.42 counting one outlier, a spread wider than the 5 min bar. So one run on each side cannot pass or fail that bar. The instrument compares medians over run sets instead: `python3 dev/audit/harnesses/r10_ci_layout_p0_fast_offsets.py --before <9 base-layout push runs> --after <3 PR 0-layout FULL runs>`:

```
before 39310145738 push 4a3cbcf62 attempt=1 success queue=0.07 dur=57.73 offset=57.80
before 39309509899 push daca95c5d attempt=1 success queue=0.05 dur=57.97 offset=58.02
before 39309055147 push 28ebd0b07 attempt=1 success queue=0.08 dur=53.77 offset=53.85
before 39307877535 push d5d0b465b attempt=1 success queue=0.08 dur=54.80 offset=54.88
before 39302900612 push 8b14bcecc attempt=1 success queue=0.08 dur=58.43 offset=58.52
before 39301525639 push f118e2644 attempt=1 success queue=0.07 dur=57.77 offset=57.83
before 39299026662 push 91f011950 attempt=1 success queue=0.07 dur=58.73 offset=58.80
before 39298637824 push 76e96a406 attempt=1 success queue=0.07 dur=59.50 offset=59.57
before 39293926561 push 5b9c33d58 attempt=1 success queue=0.05 dur=34.37 offset=34.42
before: counted 9 of 9; median offset=57.83 median dur=57.77
after 39333417268 pull_request 4d1730bd1 attempt=1 success queue=1.28 dur=51.85 offset=53.13
after 39337586935 pull_request c5b5d06c3 attempt=2 success queue=1.22 dur=31.10 offset=32.32
after 39337584363 workflow_dispatch c5b5d06c3 attempt=1 success queue=1.00 dur=46.50 offset=47.50
after: counted 3 of 3; median offset=47.50 median dur=46.50
RESULT saved_offset=10.33 bar=5.0 PASS
```

- **Before set**: the 9 newest completed push Tests runs on main whose head is at or before this PR's base `4a3cbcf62` (39293926561 through 39310145738). Each is FULL by construction, because a push forces FULL, and each is at attempt 1, so none was re-run.
- **After set**: every Tests run at this PR's layout whose `fast` job completed. 39333417268 is at `4d1730bd1`. 39337586935 and 39337584363 are at `c5b5d06c3`, which differs from `4d1730bd1` only in `tests/closures.json` and the delivery row. All three printed `MODE: FULL -- every test script runs` with the reason `.github/workflows/ci.yml changes the gate itself`, read from their `fast (3.14)` job logs. This seat started none of them and re-ran none of them. 39337586935 is at attempt 2: a pull_request run was re-run, not a push run.
- **Null**: the same instrument over the same three base runs on both sides prints `RESULT saved_offset=0.00 bar=5.0 FAIL` (rc=1). So a PASS needs a real difference between the sets.
- **What it does not settle**: the after set is small and widely spread (32.32-53.13 min), and its event classes (pull_request, dispatch) differ from the before set's (push). PASS here means the median moved 10.33 min, past the bar. It is not a measured per-run saving.
- **Why the payments stay in PR 0** (the A3 Fallback not taken): the fallback is for the case where R(a)-(c) cannot be verified. Here the round-1 failure is 20 s of a single run whose queue alone was 74 s longer than any comparator's. Every structural claim the reviewer checked held. R(b) and R(c) are unaffected by fast timing: they remove a second execution of the same scripts and stop counting copies as executions, which is the waste itself, and the `script_runs_per_push` half turns green on the first push run after the merge. Shipping the stub alone would leave `ci-ratchet` red and the stamp blocked for one more FULL PR cycle, to defer a change whose only failed measure is noise. The binding confirmation is still push against push, stage two below.

**The window rule, the post-merge control (review B4), owed by CI.** `script_runs_per_push` must be green on the first push run after the merge. `critical_path_minutes` is the median wall time of the 8 newest completed push Tests runs, so it goes green only once **at least 5 of those 8** fall under 54.825 min, about 5 merges after this one. A red `ci-ratchet` on the first push runs after the merge is that window still filling, not a failed payment. **Never re-run a push Tests run to check**: a re-run moves `updated_at`, and that run's wall time then counts the whole gap. If the window is still red 6 push runs after this merge, stop and re-measure. The model's 4-worker contention bound is the assumption most likely to fail, and a raise is the last resort, under rule 2. `r10_ci_layout_p0_fast_offsets.py --before <the 9 runs above> --after <the post-merge push runs>` re-reads stage one push against push.

## Figures

- `MODE: FULL`, `reason: .github/workflows/ci.yml changes the gate itself`: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"; cat "$D/scope.txt"`. This is expected: the diff edits three gate files, `tests/run.sh`, `tests/closure.py` and `.github/workflows/ci.yml`.
- The every-script-measured-once count, 53 = 34 − 1 + 20, from the tree at `4a3cbcf62`:
  - 34: `PYTHONPATH=tests/hastub python3 tests/closure.py lane-plan --all-scripts --out-dir "$D"; wc -l < "$D/scripts.txt"`, the closures lane's full plan.
  - 1: `tests/composed_closures.json` `scripts`, which lists `tests/boost_drift_replay.py`. The closures lane consumes it from the coverage job and does not re-record it.
  - 20: coverage_tree.sh's `DERIVED` pipeline and its `fast)` filter, which is `grep -oE 'run "\$PYTHON" tests/[a-z_]+\.py' tests/run.sh | sed 's#.*tests/##;s#\.py##' | awk '!seen[$0]++' | grep -vxE "arch_score|arch_score_head" | grep -vxE "env_drift|rolling|stress|validate|edge|backtest|optimality" | wc -l`.
  - The same figure, as entities derives it: `_cir_once_count()` returns `(53, [])` at the head. The null, M6, is a budget of 54 against that count.
- The window cross-check, from the CI-RATCHET-RED planning seat's saved ci-metrics artifacts (one zip per artifact, read with `tests/ci_ratchet.read_metrics` and counted per push run by lane and class; the copies are out of tree, so this is an unverified cross-check). The three push runs without reuse, 39213947578, 39217093836 and 39217450549, read closures `full` 33 + coverage `full` 20 = 53 each. Push run 39213675232 (efdc055a) read 33 + 19 `reused` + 21 `scoped` = 73, the GREW reading. Its coverage `scoped` rows hold `entities` twice: one fresh run, then the re-validation re-ran all 20. Push run 39216811946 read closures 34 (`boost_drift_replay` was recorded bare because coverage reused it) + 16 `reused` + 4 `scoped`. That is 54 under the old rule and 38 under the new one.
- The old budget, 68: `tests/ci_budgets.json` `script_runs_per_push` at `4a3cbcf62` (`git show 4a3cbcf62:tests/ci_budgets.json`).
- Every `fast (3.14)` queue, duration and offset, the medians 57.83 / 47.50 and `saved_offset=10.33`: `python3 dev/audit/harnesses/r10_ci_layout_p0_fast_offsets.py --before 39310145738 39309509899 39309055147 39307877535 39302900612 39301525639 39299026662 39298637824 39293926561 --after 39333417268 39337586935 39337584363`. The null `saved_offset=0.00` comes from the same command with `--before 39310145738 39309509899 39309055147 --after 39310145738 39309509899 39309055147`.
- The after runs' `MODE: FULL`: `gh api --allow-escape-sequences repos/tvofi/heatpump_optimizer/actions/jobs/<fast job id>/logs | grep 'MODE:'` for jobs 118337404382 (run 39333417268), 118350962689 (run 39337584363) and 118351012870 (run 39337586935).
- M7's ledger reading, at the head: `_coverage_revalidation(True)[3]` gives `scripts.tsv` and `provenance.tsv` 20 rows each, every script once, `reused: 0`. `_coverage_revalidation(False)[3]` gives 20 rows each with `reused: 1`.

## Red checks

- Round 1's run 39333417268 at `4d1730bd1`: `closures` failed UNDER-SCOPED (`tests/entities.py`, `tests/harness_headers.py`), and one `closures-autofix` cycle followed and succeeded with `c5b5d06c3`, `ci: re-record closures`. That red was expected and is answered by `ci-autofix.md`'s rule: the bot's Linux re-recording. At `c5b5d06c3`, the check-runs listing shows no failed run. `closures` and `composed-proof` were still in progress when it was read.
- This head adds two harness files, each recorded as an inert read here, and one new entities check that reads files under a temp dir. Another `closures` UNDER-SCOPED, with one autofix cycle, is possible if the Linux recording sees reads the Darwin predictor does not. It is named here, not analysed.
- `ci-ratchet`, for `critical_path_minutes`, on the first push runs after the merge, until the window rule is met. It is red at the base too (push run 39310145738), so it is not a red this branch introduces.
- The reviewer's container showed one environmental entities red, `graders-head-copy's delivery_status step`, which fails identically at the base there and is green in CI. It is not reproduced on this seat: M0 is green here.

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
