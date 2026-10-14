Main went red at `a77faf30d9e4` (the #2210 merge). The failing job is `ci-ratchet` (run 38639862216, job 116129703139), in the step "Grade the ratchet". It printed `GREW  script_runs_per_push: 69 (budget 68)`. The growth was not CI cost. It was test-fixture rows written into the run's real metrics files. The #2210 diff (`tests/replay.py`, `tools/replay/export.py`) plays no part.

The cause. `run.sh`, `derive_closures.sh` and `coverage_tree.sh` read `HPO_CI_METRICS` from the environment and left it exported, so every child process they ran inherited it. Two children are instruments under test:

- `closure.py selftest` drives `derive_closures.sh` under a stub interpreter (the #1987 block, the lane-runner block and the full-arm block). It appended `closures tests/x.py`, `tests/p1.py`..`tests/p4.py` and `tests/q1.py`..`tests/q3.py` rows to `ci-metrics-fast.tsv`.
- `entities.py`'s lease probe starts a nested `GATE_SCOPE=full ./tests/run.sh` and kills it after about a second. The nested run appended a second `fast mode full` line. When the runner got as far as the selftest's #1987 block before the kill, it also appended a second `x.py` pair.

The ratchet counts every row whose lane is `closures` or `coverage`, whatever file it came from. Push run 38629708082 (main `554e2ecfa`, ratchet green) carried 13 such fixture rows in its fast artifact. Push run 38639862216 carried 15. The +2 was the nested run.sh winning that race, so the step from 67 to 69 rows was timing. Both runs measure 54 real executions: 34 closures rows plus 20 coverage rows.

The fix has two owners.

1. `tests/ci_ratchet.py`: a row counts only from its own lane's artifact. `file_lane` reads the lane from the `ci-metrics-<lane>.tsv` basename that each job writes and the window keeps. A row of another lane is dropped, and a `not counted: N row(s)` line on stderr reports the drops. A `.tsv` that names no lane is refused, not guessed. This is what turns main green on the next push: the polluted artifacts stay in the 15-run window until they age out, and without this owner each of them would keep grading 69.
2. The three emitters read the variable once into a shell-local `_hpo_ci_metrics` and `unset HPO_CI_METRICS`. Their own lanes are subshells and background functions, so they still see it, but no script they run inherits it. This stops the leak at its source. It also stops a nested run.sh writing `fast mode full` into a scoped pull-request run's fast artifact, which would make the ratchet read that run as full-case.

No budget is touched: `tests/ci_budgets.json` is byte-identical to the base. Headroom on `script_runs_per_push` rises from about 0 to 14, because the recorded 68 already included fixture rows. Tightening it is the next deliberate `--record`, which this fix does not take.

## Head

cc326217bb7a94c04561a089af5bded80f3815ca (merge base and origin/main tip a77faf30d9e4dd0f7c5f3074f0b1a16de50f34c4, checked 2026-10-14T22:51:42Z)

## Mutation proof

The failing tests were committed first, at `a16c6dc1c`. That is the unfixed tree plus three new checks in `tests/entities.py`. At it, `PYTHONPATH=tests/hastub python3 tests/entities.py` returned rc=1 with `3 of 2316 ENTITY CHECKS FAILED`, and all three failures were the new checks:

- `the CI ratchet counts a lane's rows only from that lane's own artifact`: the leaked window counted 5 (want 2), and the unnamed file was not refused.
- `every HPO_CI_METRICS emitter keeps the file from the children it runs`: all 3 emitters were exporting it.
- `derive_closures.sh writes its own metrics row and hands its child none`: the recorded script saw the metrics path.

One combined mutant was then run at the head. In `tests/ci_ratchet.py`, the predicate `if parts[0] != lane:` became `if False:`. In `tests/derive_closures.sh`, `unset HPO_CI_METRICS` became `:`. Result: rc=1 with `3 of 2316 ENTITY CHECKS FAILED`, the same three checks. The second check now named only `tests/derive_closures.sh`, the one emitter mutated. Both files were restored with `git checkout --`, and `git status --short` printed nothing afterwards.

## Null control

The unmutated head: `tests/entities.py` returned rc=0 with `ALL 2316 ENTITY CHECKS PASSED`. The lane check carries its own control: the same three rows placed in a closures artifact count to 5, so the predicate drops only rows that are out of place. The pre-existing checks `the CI ratchet's main() refuses a script-run count above its budget` and `and main() passes the committed table at its own recorded count (the null control)` stay green. Their scratch file was renamed from `run.tsv` to `ci-metrics-closures.tsv`, because a file that names no lane is now refused.

## Figures

- The red grade, `GREW script_runs_per_push: 69 (budget 68)`: from `gh api --allow-escape-sequences repos/tvofi/heatpump_optimizer/actions/jobs/116129703139/logs`. The escape-stripped copy is `/private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/ratchet-fix/job.txt`, sha1 32534d7aef32ab68e140988842351242ef1df484.
- Reproduced at the base: `python3 tests/ci_ratchet.py --metrics-dir <scratch>/m69` gave rc=1 and `GREW  script_runs_per_push: 69 (budget 68)`. `<scratch>/m69` holds run 38639862216's own three artifacts, fetched with `gh run download 38639862216 --name ci-metrics-<lane>`. This is not the job's full 38-artifact window, which has since moved. It is the run that set the maximum. Critical path was not passed, so it was not graded.
- At the head, the same command gave rc=0, `ci-ratchet: not counted: 17 row(s) carried by another lane's artifact` and `ok    script_runs_per_push: 54 (budget 68)`.
- The 17 dropped rows, by `cut -f1 <file> | sort | uniq -c` per artifact: `ci-metrics-fast.tsv` 15 closures + 2 fast, `ci-metrics-closures.tsv` 34 closures + 1 fast, `ci-metrics-coverage.tsv` 20 coverage + 1 fast. So 15 + 1 + 1 rows sat in another lane's file. The closures and coverage jobs each carried one leaked `fast mode` line from a nested run.sh.
- Row diff between push runs 38629708082 (green) and 38639862216 (red): two extra `closures tests/x.py full` rows, and coverage `features` reused in one and scoped in the other. Lane-class counts: 47 vs 49 closures, 20 vs 20 coverage. Command: `diff` of the non-fast rows' `lane, script, class` columns, sorted.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` at the head: rc=0, `ALL 2316 ENTITY CHECKS PASSED`. Log sha1 0b89bf20243df91fc49cc2ebcad43ff7152269f4. Test-first log sha1 66853a5b95d5d86f8d5a8b3442b5fd082ec14a79. Mutant log sha1 4b6944293f47fc0ab0aa231673232af8b3072447.
- `PYTHONPATH=tests/hastub python3 tests/closure.py selftest` at the head: rc=0, `ALL 115 closure shrink pins PASSED`.
- `python3 tests/structure.py` at the head: rc=0, `STRUCTURE RATCHET PASSED`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: FULL`, reason "tests/derive_closures.sh changes the gate itself". The full suite is left to CI, and only the scripts this diff touches were run locally.
- Seam rule: `git grep -l HPO_CI_METRICS -- '*.sh'` returns `tests/derive_closures.sh`, `tests/run.sh` and `tools/coverage/coverage_tree.sh`, and all three are closed in this diff. `git grep -n HPO_CI_METRICS` over the rest of the tree, excluding `dev/`, returns only `.github/workflows/tests.yml`, which sets the variable for each job and never reads it, and comments. No Python file reads the variable. The rule is now a check, `every HPO_CI_METRICS emitter keeps the file from the children it runs`, so a fourth emitter that exports it is refused.
- Diff: `git diff --stat $(git merge-base origin/main HEAD)...HEAD` lists 5 files: `tests/ci_ratchet.py`, `tests/derive_closures.sh`, `tests/entities.py`, `tests/run.sh` and `tools/coverage/coverage_tree.sh`. No budget file, claim file, `VERSION`, manifest or `RELEASE_NOTES.md` is touched, and no tracked file is added.

## Red checks

`ci-ratchet` on main, push run 38639862216 (job 116129703139), at `a77faf30d9e4`. The root-cause answer belongs to the separate root-cause seat that runs beside this fix, by `defect-root-cause.md`. This body does not perform it. A cheaper detector now exists as the three `tests/entities.py` checks above, which run in `fast` on every pull request that reaches `tests/ci_ratchet.py` or the emitters. Before them, the leak was visible only to the push-only `ci-ratchet` job, and only when the race pushed the count over the budget.

## Forward-carry

none

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
