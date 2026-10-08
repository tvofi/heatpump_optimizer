`tools/release/stamp.py --self-test` fails intermittently in CI with `OSError: [Errno 39] Directory not empty: '/tmp/tmp…/.git/objects/pack'`. `tests/entities.py` runs it as the check "tools/release/stamp.py's --self-test passes", so the failure turns PR checks red when no diff caused it. The same self-check runs during a real stamp.

The cause is the runner's git. CI's git is 2.55.0. Since 2.54, after every `commit` or `merge`, git starts a detached geometric repack. That repack runs once two loose objects share the `objects/17` shard, at any repository size, because git estimates the loose-object count as the entries in `objects/17` times 256. The self-test's undo repository commits the blob `# Notes\n`, whose id `17e0f0de…` is fixed by its content. So each of that repository's two commits has a 1/256 chance of starting a repack, which writes into `.git/objects/pack` while `TemporaryDirectory` removes the repository.

That 2/256 per self-test run is the rate at which a repack is **started**, not the rate at which the run fails. A failure also needs the repack to still be writing when the cleanup reaches `objects/pack`. This body does not derive the CI failure rate. Its only measure of frequency is the two CI sightings.

The fix: both throwaway repositories now take one shared helper, `_throwaway_git_env()`. It replaces the two duplicated environment blocks and adds `maintenance.auto=false` through `GIT_CONFIG_COUNT`. Git checks that key first, before it spawns any auto-maintenance, so no repack starts. A new self-test check reads the value back through the real `git config`. Stamp semantics are unchanged, because only `self_test()` reaches the helper.

The RCA is `dev/audit/rca/R9-RCA-stamp-race.md`. It records process state (d), the cost test, the census of the class, and section 4's corrected alternatives. The perturbation is `dev/audit/harnesses/git_auto_maintenance_race.sh`. Its `realgit` and `realgit-forced` arms are the #2051 fix reviewer's method (its `realgit_race.sh`, real git 2.55.0 built from git/git v2.55.0), adopted with credit.

## Head

dda217b3d2658ffc20363623c06a0ed0cfd3f46e

This is the authored code head. It is the previous PR head 811846b5 merged into the seat branch, plus one commit answering review round 1. Its merge base is ef3ca6571f5f6ef6b3cc0360b7ce4835f56eb702. The round-1 commit makes three changes. The harness takes the canonical `repo_root` walk from `tools/audit/repo_root.sh` instead of the `../../..` depth root, and gains the real-git arms. RCA section 4 corrects the `gc.auto=0` claim. The RCA separates the trigger rate from the failure rate.

## Mutation proof

The mutant deletes the three `GIT_CONFIG_*` keys from `_throwaway_git_env()` at dda217b3, as a working-tree edit, and restores them with `git checkout`:

    python3 tools/release/stamp.py --self-test
      FAIL throwaway repo: git itself reads auto-maintenance as off, so no detached repack outlives the directory
    RESULT stamp_self_test=fail
    GIT_BIN=<review-2051>/git255/bin bash dev/audit/harnesses/git_auto_maintenance_race.sh 10 realgit-forced
    last: OSError: [Errno 66] Directory not empty: 'pack'
    arm=realgit-forced git=2.55.0 runs=10 directory_not_empty=4 nonzero_exit=10

After the restore, `git diff --quiet` held and the self-test printed `RESULT stamp_self_test=pass`.

## Null control

The base is a `git archive` of ef3ca657 with the harness copied in. There, `realgit-forced 20` (real git 2.55.0) printed `directory_not_empty=9 nonzero_exit=9` and `shim 3` printed `directory_not_empty=3 nonzero_exit=3`. At dda217b3, `realgit-forced 20` printed `directory_not_empty=0 nonzero_exit=0`.

With nothing forced, the reviewer's real-git 2.55.0 run printed 0 of 300 at the base and 0 of 300 at the fix on this Mac. That is why the body gives no failure rate.

Under real git 2.55.0, the seat built a repository with two objects in shard 17, both committed. That probe is in this turn's transcript and not in the tree, because it reproduces the reviewer's `evidence/realgit/gcauto0.txt`. The default configuration gave a repack (`packs=1`). Each of `gc.auto=0` and `maintenance.auto=false` gave `spawns=0 packs=0`.

## Figures

`python3 tests/closure.py select --diff ef3ca657 --workdir "$D"` printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out`. Its `scope.run` names `tests/doc_claims.py` and `tests/entities.py`.

The `run_always` scripts in `tests/run.sh` run whatever the scope says, so they were also run at dda217b3. All were run with `PYTHONPATH=tests/hastub` under the CI venv's Python 3.14.7:

- `tests/harness_headers.py` printed `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `tests/layout.py` printed `layout self-test: ok`.
- `tests/env_drift.py --claims-only origin/main` printed `claims hygiene: origin/main ok`.
- `tests/closure.py selftest` printed `ALL 39 closure shrink pins PASSED`.

`tests/doc_claims.py` printed `ALL 160 checks PASSED`. `tests/entities.py` printed `ALL 2203 ENTITY CHECKS PASSED`. `tests/structure.py` printed `STRUCTURE RATCHET PASSED`. `tools/release/stamp.py --self-test` printed `RESULT stamp_self_test=pass`.

The CI sighting is check-run 113149021777 (`fast (3.14)` on #2049, run 37727537796, attempt 1). Its log line 7847, read through `gh api repos/tvofi/heatpump_optimizer/actions/jobs/113149021777/logs`, carries the `Errno 39 ... /.git/objects/pack` failure, and the same log prints `git version 2.55.0`.

The census of the class uses `git grep -n -E '"git", "init"|git init|"init", "-q"' 6b91e238 -- tests tools .claude .github | wc -l`, which printed `37`. That is one comment, stamp's two sites (closed here) and 34 other throwaway-repository sites, which are not closed here. They are in RCA section 5.

## Red checks

`fast (3.14)`: check-run 113185847660, run 37739163225, at the previous head 811846b5. This diff caused it. `tests/harness_headers.py` is `run_always` and printed `FAIL depth seams: dev/audit/harnesses/git_auto_maintenance_race.sh:34`, because the new harness found the root by a `../../..` depth instead of the canonical `repo_root` walk. Fixed at dda217b3, where `tests/harness_headers.py` prints `ALL 109 HARNESS HEADER CHECKS PASSED`. The cheaper detector exists: `python3 tests/harness_headers.py`, about 105 s locally. The seat ran only what `scope.run` named and missed it, because `scope.run` does not list `run_always` scripts. This time the `run_always` set was run as well (see `## Figures`).

`budget-raise-gate` at 811846b5 ended `cancelled`, not failed. The diff touches no `*_budgets.json`, and the cancelled twin needs a rerun before merge.

`delivery-status` at 811846b5 printed `UNCHECKED — 72 rowed, 0 pending, 0 overdue`. It grades main and is not a required context, and this diff touches none of its inputs, so it is not this pull request's.

## Forward-carry

The class barrier is not built here. It is one workflow-level `env:` (`GIT_CONFIG_COUNT=1`, `GIT_CONFIG_KEY_0=maintenance.auto`, `GIT_CONFIG_VALUE_0=false`) in `.github/workflows/tests.yml` and `governance.yml`, and it covers CI only. The full closure is a shared throwaway-repository helper for the other 34 sites. Both are recorded in `dev/audit/rca/R9-RCA-stamp-race.md`, sections 5 and 6, as the orchestrator's decision.

## Friction

fixer.md-step-5: unclear: the step says to run what scope.run names, and scope.run omits run_always scripts (tests/harness_headers.py), so a seat following it literally misses a red that fast (3.14) then reports.
