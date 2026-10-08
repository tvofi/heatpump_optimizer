`tools/release/stamp.py --self-test` fails intermittently in CI with `OSError: [Errno 39] Directory not empty: '/tmp/tmp…/.git/objects/pack'`. `tests/entities.py` runs it as the check "tools/release/stamp.py's --self-test passes", so the failure turns PR checks red when no diff caused it. The same self-check runs during a real stamp.

The cause is the runner's git. CI's git is 2.55.0. Since 2.54, git detaches a geometric repack after every `commit` or `merge`, and the repack's `--auto` condition fires once two loose objects share the `objects/17` shard. That is true at any repository size, because the loose-object count is estimated from `objects/17` times 256. The self-test's undo repository commits the blob `# Notes\n`, whose id `17e0f0de…` is fixed by its content. So each of that repository's two commits has a 1/256 chance of starting a repack, and the repack writes into `.git/objects/pack` while `TemporaryDirectory` removes the repository.

The fix: both throwaway repositories now take one shared helper, `_throwaway_git_env()`, which replaces the two duplicated environment blocks and adds `maintenance.auto=false` through `GIT_CONFIG_COUNT`. Git checks that setting before it spawns any auto-maintenance, so no repack starts. A new self-test check reads the value back through the real `git config`. Stamp semantics are unchanged, because the helper is reached only from `self_test()`.

The RCA is `dev/audit/rca/R9-RCA-stamp-race.md`. It records process state (d), the cost test, and the census of the class. The perturbation is `dev/audit/harnesses/git_auto_maintenance_race.sh`.

## Head

6fc5d9f6832bbd541d5f0b55be3ec4f5e17f60ef

Merge base and origin/main 6b91e238f6883af6eedef0fc541bce76b14fc46c (read 2026-10-08T07:50Z).

## Mutation proof

The mutant deletes the three `GIT_CONFIG_*` keys from `_throwaway_git_env()` in a working-tree edit at c0664ae6, then restores them with `git checkout`:

    python3 tools/release/stamp.py --self-test
      FAIL throwaway repo: git itself reads auto-maintenance as off, so no detached repack outlives the directory
    RESULT stamp_self_test=fail
    bash dev/audit/harnesses/git_auto_maintenance_race.sh 3 shim
    last: OSError: [Errno 66] Directory not empty: 'pack'
    arm=shim git=2.38.1 runs=3 directory_not_empty=3 nonzero_exit=3

After the restore, `git diff --quiet` held and the self-test printed `RESULT stamp_self_test=pass`.

## Null control

At base 6b91e238, the harness without its shim printed `arm=plain git=2.38.1 runs=5 directory_not_empty=0 nonzero_exit=0`, so the harness itself does not make the self-test fail. At this head, the shim arm printed `arm=shim git=2.38.1 runs=5 directory_not_empty=0 nonzero_exit=0`, and the plain arm printed `directory_not_empty=0 nonzero_exit=0`. The real-git arm needs no model. `bash dev/audit/harnesses/git_auto_maintenance_race.sh 0 spawn` printed `config=default maintenance_spawns=1` and `config=off maintenance_spawns=0`: the env-config route stops the real git from spawning `git maintenance run --auto`.

## Figures

`bash dev/audit/harnesses/git_auto_maintenance_race.sh 5 shim` at base 6b91e238 printed `last: OSError: [Errno 66] Directory not empty: 'pack'` and `arm=shim git=2.38.1 runs=5 directory_not_empty=5 nonzero_exit=5`. That is the reproduction. The harness is a model, because this Mac's git 2.38.1 never reaches 2.55's condition on its own: its shim applies 2.55's own gate (`maintenance.auto`, falling back to `gc.auto > 0`), reads it through the real `git config`, and forks a detached writer into `objects/pack`. The upstream lines it models are cited in its header and in the RCA, section 1.

The per-run rate of 2/256 for the undo repository is derived from the blob id above. `printf '# Notes\n' | git hash-object --stdin` prints `17e0f0de…`, and each commit id is time-dependent and lands in shard `17` with probability 1/256. The record-class repository has no fixed-content object in `17`, so for it the rate is about C(7,2)/65536.

The CI sighting is check-run 113149021777 (`fast (3.14)`, run 37727537796, attempt 1). Its log line 7847, read through `gh api repos/tvofi/heatpump_optimizer/actions/jobs/113149021777/logs`, carries the `Errno 39 ... /.git/objects/pack` failure. The same log prints `git version 2.55.0`.

The census of the class uses `git grep -n -E '"git", "init"|git init|"init", "-q"' 6b91e238 -- tests tools .claude .github | wc -l`, which printed `37`. That is one comment, stamp's two sites (closed here) and 34 other throwaway-repository sites, which are not closed here. The RCA's section 5 gives the disposition and section 6 the proposed barrier.

`python3 tests/closure.py select --diff 6b91e238 --workdir "$D"` printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out`. Its `scope.run` names `tests/doc_claims.py` and `tests/entities.py`. `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` printed `ALL 160 checks PASSED`. `PYTHONPATH=tests/hastub` with the CI venv's Python 3.14.7, `tests/entities.py` printed `ALL 2203 ENTITY CHECKS PASSED`. `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`. `python3 -I tools/audit/seat/tmp_paths.py --check` printed `tmp_paths: 0 refused, 0 stale allow entries at HEAD`.

## Red checks

none. This head has no CI run yet. The red this pull request answers is the intermittent `fast (3.14)` failure above, on #2049 and #2048, and no commit of this branch caused it. The cheaper detector: none exists that is cheaper than the gate. The race needs CI's git (≥ 2.54) and about a 1-in-128 commit-id draw, and the seat's git cannot produce it. The barrier is therefore removing the cause, and that is built here.

## Forward-carry

The class barrier is not built here. It is one workflow-level `env:` (`GIT_CONFIG_COUNT=1`, `GIT_CONFIG_KEY_0=maintenance.auto`, `GIT_CONFIG_VALUE_0=false`) in `.github/workflows/tests.yml` and `governance.yml`, covering the other 34 throwaway-repository sites. It is recorded in `dev/audit/rca/R9-RCA-stamp-race.md` sections 5 and 6, as a decision for the orchestrator: it is a code-owned workflow edit with its own `tests/entities.py` pins.

## Friction

none
