Carry text main must land, verbatim, as a new entry in R10-FLY-SUITE-ENV-FLAKES's `carry` list on handoff/audit-r10-roster (it corrects that group's second carry, from d37aa1b1, which says "coverage-ratchet failed after it"; while the two disagree this one is right):

> From #2632 (R10-LOOP-CPU) round 3, correcting the carry above: coverage-ratchet's red in run 39874068348 (package 85.89 % against 96.0 %, 45 modules below 95.0 %) was neither the entities flake nor a flake. It was #2632's own defect, fixed in that PR: tests/features.py left 740 live process-worker children at its exit, and their coverage data files landed after the script's own process exited. tools/coverage/coverage_tree.sh's `measure()` checks `ls "$WORK/data/$s"/.coverage.*` the moment `tests/$s.py` returns, so it recorded `features.nodata` with no error, and the ratchet read a package-wide drop. A local run at ab6216ce reproduced the red: `features.nodata` and 85.88 % (18987/22108). A second run printed "could not combine tests/features.py's data" instead. The control at fef4a135 read 98.66 % (21801/22097). The seam left here is the instrument's: any measured script whose descendants outlive it loses its whole measurement silently. Make `coverage_tree.sh` refuse a measured script that exited 0 and left no data, or wait for the script's process group before the check, so a red names the script rather than 45 modules. Plant a script that leaves one child writing coverage after its exit; it must read red. Files: tools/coverage/coverage_tree.sh. Re-measure at your merge base.

Moves the away recovery estimate and the interval replay off the event loop (R10-LOOP-CPU, finding D14-s1-01). `away.resolve` and `_apply_return` are awaited and take `estimate_recovery`, which `_recovery_off_loop` runs in the process worker. `_replay_interval` ships the pure `_replay_step` by name. `_resolve_away` publishes only when the live away state is unchanged across its await, and the override expiry sits in the sync `_expire_away_override`. `_run_in_process` serialises each job with `pickle.dumps` before it touches the pipe, so a job that will not pickle degrades to the executor and leaves the worker serving. A transport fault reaps the child before its handle is dropped. Closes #2237.

This head adds two things on the bot's `2f66e909` (`ci: pin killed mutants`), then merges `origin/main`:
- **A fail-fast keystone in `tests/features.py`**, run straight after `R = Results("Feature modules")`. It calls `_expire_away_override` on a bare coordinator (`object.__new__(Coord)`, with `_away_state` and a recording `_spawn`). It asserts the returned (active, return-time) pair for a live override and for a lapsed one, the pair `_resolve_away` unpacks. On failure it ends the run with `R.close`, so the `RETURN_DEL` mutant at `return active, ret` is killed in seconds. Without the keystone, features.py under that mutant timed out in CI's pin run.
- **The pin** `tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._expire_away_override.RETURN_DEL.67e36ad4.json`, `killed_by: tests/features.py`. It was recorded by `mutation_table.py --pin-killed --base origin/main` and is not hand-written.

The production code is unchanged in this round. `git diff f38f91852 2f66e909 -- custom_components | git patch-id --stable` and `git diff $(git merge-base origin/main HEAD) HEAD -- custom_components | git patch-id --stable` print the same id, `d9403fd5`.

## Head

`4bae3ae2c7cf00188feaee7aa73c9bd7b01e7f68`. It is a fast-forward from `2f66e909ea99ffef43bc5ef5c5b9bee542c9c3b9`, with three commits on top:
- `05ec7931`: the keystone;
- `8d25663f`: the pin;
- `4bae3ae2`: the merge of `origin/main` at `bfd61aaf167f87ddb582437f8626c49f76e1a0fa`.

The merge base is `bfd61aaf` (`origin/main`'s tip at 2026-10-23, read after the merge). The merge was clean, with no conflict. Every figure below was taken at this head unless it names another commit. The pin was recorded at `8d25663f`'s parent `05ec7931`, against `f38f9185`. Python is `/opt/hpo/venv-ci` (3.14), and `PYTHONPATH=tests/hastub` throughout.

## Mutation proof

Each mutant was applied alone at this head by an exact-once `str.replace` (scratch driver `muts.py`), then `tests/features.py` was run whole and the file restored.

| site | mutant | red |
|---|---|---|
| `_run_in_process`: `job = pickle.dumps((fn, args), ...)` and `stdin.write(job)` | M1: the pre-serialising `try` deleted and `pickle.dump((fn, args), stdin, ...)` restored | `R10-LOOP-CPU: a job that will not pickle degrades without touching the worker, which serves the next job as the same process` (`pid before=9609 after=9610 handle kept=False`); `1 of 4311 FEATURE CHECKS FAILED`, rc 1 |
| `_run_in_process`'s transport `except`: the guarded `worker.kill()` / `worker.wait()` | M2: the reap deleted | `R10-LOOP-CPU: a reply stream that faults reaps the child it came from, never leaves it running unheld` (`child returncode=None`); `1 of 4311 FEATURE CHECKS FAILED`, rc 1 |
| `_expire_away_override`: `if active != self._away_state.override_active or ret != parsed:` | M3: `if False:` (the table's `GUARD_OFF`, pinned by the bot in `2f66e909`) | the keystone, `[((True, datetime(2026, 1, 10, 18, 0, tzinfo=utc)), (False, None), [])]`: a lapse no longer saved; `1 of 1 FEATURE CHECKS FAILED`, rc 1, 2 s |
| `_expire_away_override`: `return active, ret` | M4: `pass` (the table's `RETURN_DEL`, the round-3 blocker) | the keystone, `[(None, None, ['persist_override'])]`; `1 of 1 FEATURE CHECKS FAILED`, rc 1, 2 s (whole features.py, vs CI's pin-run timeouts) |

**The pin run.** The command was `PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main`, run at `05ec7931` with `origin/main` at `c6ef0668`. It printed `baseline tests/features.py: rc=0 failed=0 549s` and `pinned custom_components/heatpump_optimizer/coordinator.py:9568 RETURN_DEL -- killed by tests/features.py`, then `PIN KILLED: 1 pinned, 0 left unpinned`, rc 0. The pin's recorded reason is `RETURN_DEL (\`pass\`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1`.

**Failing test first.** This uses the head's `tests/features.py` over the production code without round 3's transport fix: a worktree at this head with `git show bca40aa9 -- custom_components | git apply -R` (coordinator.py, +1 -16). It reads `2 of 4311 FEATURE CHECKS FAILED`, rc 1. Both worker checks are red: `pid before=9777 after=9778 handle kept=False`, and `child returncode=None (None: still running, with no handle left to reap it)`. The keystone is a pin on existing code, not a fix, so it is green there; its proof is M4.

## Null control

- **Unmutated head.** The scoped gate's `tests/features.py` read `ALL 4311 FEATURE CHECKS PASSED`, and the pin run's baseline read `rc=0 failed=0`.
- **The keystone's own null.** Run alone on the unmutated tree, the slice of `tests/features.py` up to and including the keystone prints `ok keystone: ...` and continues past the `sys.exit`. Under M4 the whole script prints `FAIL keystone: ... [(None, None, ['persist_override'])]` and `1 of 1 FEATURE CHECKS FAILED`, rc 1, `real 0m3.056s`. That run was at `05ec7931`, whose production code is this head's. The `saved == ['persist_override']` arm reads the same under the mutant, so the red comes from the returned pair and not from the write-back.
- **The pin run's null.** `null control custom_components/heatpump_optimizer/coordinator.py:509 NULL_COMMENT survived tests/features.py`, and it survived `tests/entities.py` and `tests/config_flow_steps.py` too.
- **The finder's harness null.** `--away --deficit 0` reads 0 at both ends (`## Figures`).

## Figures

**The finder's harness:** `dev/audit/rounds/round10/D14/s1/p10_seams.py`, sha1 `c8ba174c3fa7f6768a7576d31b6597835df45589` at both ends (`sha1sum` of each worktree's copy). It was run as `HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 <harness> <args>` from a worktree at `bfd61aaf` (base) and at this head:

| args | base `bfd61aaf` | head `4bae3ae2` |
|---|---|---|
| `--away` | `cycles=6`, `loop_kernels_all=183`, `loop_kernels_away_seam=183`, `loop_kernels_per_cycle=30.50` | 0, 0, 0.00 |
| `--away --deficit 0` (null) | `loop_kernels_per_cycle=0.00` | `0.00` |

**The scoped gate:** `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 23 script(s) run, 10 scoped out.` The gate ran as `PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=bfd61aaf167f87ddb582437f8626c49f76e1a0fa bash tests/run.sh`. It printed `25 TEST SCRIPT(S) PASSED; 9 SCOPED OUT AND NOT RUN`, rc 0, with `ALL 4311 FEATURE CHECKS PASSED`, `ALL 2408 ENTITY CHECKS PASSED` and `STRUCTURE RATCHET PASSED` among them. That is scoped mode, not a full gate.

**Structure:** `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED` at `05ec7931`, `8d25663f` and this head. Nothing was re-recorded.

**Predictor:** `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` prints `CI PREDICT: no closures or fast red predicted against bfd61aaf167f (a data-file read is not seen)` at this head.

**Architecture score:** `python3 tools/audit/archscore/score.py --diff origin/main` at this head prints `Architecture score: dS +0.1687 WORSENS (inadmissible: coord_footprint 2489->2491)`. Its lines are `coord_footprint 2489 -> 2491 -0.0012` and `params_over_10 8 -> 7 +0.1699`. This round's commits touch only `tests/`, which the score does not read here, so the figure is the round-1 production diff's.

**The class census (fixer.md step 8)** for the transport fix: `grep -nE "pickle\.dump\(|stdin\.write\(|stdout\.write\(|_PROCESS_WORKER = None|subprocess\.Popen\(" custom_components/heatpump_optimizer/*.py`. Each site it returns at this head, and its disposition:
- `coordinator.py` `_ensure_worker`'s `subprocess.Popen(`: the one spawn site. It reuses a live worker and respawns only on a `None` or dead handle; guarded.
- `_shutdown_process_pool`'s `_PROCESS_WORKER = None`: set after the kill and wait, and only if the handle is still the installed one; guarded.
- `_run_in_process`'s `stdin.write(job)`: closed in this diff; the job is pre-serialised. M1 is its proof.
- `_run_in_process`'s transport-`except` `_PROCESS_WORKER = None`: closed in this diff; the child is reaped first. M2 is its proof.
- `_run_in_process`'s `load-err` `_PROCESS_WORKER = None`: the child returned from `run_worker` after dumping `load-err`, so it exits on its own; guarded by the child.
- `process_worker.py` `_dump`'s `stdout.write(blob)`: serialised before the write since #511; guarded.

For the mutation lane's class, a timed-out site the bot can never pin, the rule is `prepr.sh` step 6d's `ADDED UNPINNED` list via `ci_predict.py`. It returns no site at this head (`## Unpinned sites`).

## Architecture score

- `coord_footprint` 2489 -> 2491: the net of the publish guard and the expiry split that the P10 await in `_resolve_away` requires, against the replay step moved out to `_replay_step`. Without the guard and the split, either the switch's override write is reverted, or the expiry's in-place writes sit in an async method (`shared_inplace_writes 17 -> 19`, measured in round 1 before the split). This round adds no production line.
- `params_over_10` 8 -> 7: an improvement, from the replay step's move.

## Alternatives

- **Pin `killed_by: tests/entities.py`**, which runs the barrier `replay.kernel_checks()` (it reads 3 of 5 under the mutant, the round-3 review's M4). That records a kill but leaves features.py, the driver CI's pin run tries first, timing out on the site. It also leaves the method's own return pinned only through an end-to-end replay. The keystone pins the return where it is produced and ends the slow driver's run early.
- **Raise the pin run's per-mutant budget.** This is refused by the brief, and it would make every timed-out mutant slower to judge rather than the one fixable.
- **A non-fail-fast check placed anywhere in features.py.** The existing check `an unexpired away override is not re-persisted each cycle; a lapsed one is cleared and saved once` already reads this return, about 62000 lines into the file. Under the mutant the run outruns its budget before the verdict is read, so the check's position and the early exit are the fix.

## Red checks

- **`mutation`**, red at `5b068048` (job 120230312005) and at `577ec62d` (job 120235979635), each with `ADDED UNPINNED coordinator.py:9553` / `:9568 RETURN_DEL: return active, ret`.
  - Cause: the site's only killing route in features.py ran under the mutant past the pin run's per-mutant timeout, which is `TIMEOUT_SCALE` (3) times the driver's own measured seconds. Both of CI's pin runs, `mutation-pins` jobs 120155543073 and 120236183357, recorded `skip-timed-out in tests/features.py`. `mutation-autofix` pins only killed mutants, so it would never pin this one.
  - Answer: the fail-fast keystone kills the mutant in about 3 s, and `--pin-killed` pinned it, both in this branch.
  - Cheaper detector: `ci_predict.py`, run by `prepr.sh` step 6d and by `body_push.sh`, named the site as added and unpinned before the round-3 handoff, at a standing cost of seconds. The miss was the disposition: the body deferred to a bot pin that a timed-out site never receives.
  - Countermeasure: none beyond this fix. A local `--pin-killed` before the handoff would have shown the timeout, at about 80 min per run here, and `ci-autofix.md` already places that run.
  - Carry: dismissed: fixed in this branch by the keystone and its pin
- **`coverage-ratchet`**, red in run 39874068348 (job 120165113949) at `ab6216ce`, package 85.89 %. This was this PR's defect: the process-worker children leaked from features.py wrote their coverage after the script returned, so the lane recorded `features.nodata`. It is fixed by the transport fix, M1 and M2. CI's coverage-ratchet passed at `577ec62d` (job 120243722102). Cheaper detector: none ran, since features.py passed with the children alive. The instrument's silent `nodata` is carried to R10-FLY-SUITE-ENV-FLAKES (top of this body). Carry: R10-FLY-SUITE-ENV-FLAKES
- **`fast (3.14)`**, red in run 39874068348 (job 120155413953) on `1 of 2401 ENTITY CHECKS FAILED`, and green in the sibling run at the same head. This is the gate-lease timing check in `tests/entities.py`, which this diff does not touch; it is already routed. Carry: dismissed: timing check outside this diff, routed at d37aa1b1
- **`closures`**, UNDER-SCOPED in run 39871545349: repaired by `closures-autofix` in `ab6216ce`, and not duplicated. `ci_predict.py` predicts no closures red at this head. Carry: dismissed: repaired by the autofix bot
- **`nightly-status`**, failed at `577ec62d` (job 120235979624): it grades main, and this diff does not reach what it reads. Carry: dismissed: grades main, not this diff

## Unpinned sites

None. `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` at this head prints `CI PREDICT: no closures or fast red predicted` and lists no `ADDED UNPINNED` site. `_expire_away_override`'s `RETURN_DEL` is pinned by `8d25663f`, and its `GUARD_OFF` by the bot's `2f66e909`.

## Forward-carry

- **R10-FLY-SUITE-ENV-FLAKES: coverage_tree.sh's per-script data check races a script's descendants.** The carry text is at the top of this body for main to land. It is not yet on `origin/main` or on `handoff/audit-r10-roster`: `grep -c "correcting the carry above"` on each roster prints 0. It corrects the d37aa1b1 carry's claim that coverage-ratchet "failed after" the entities flake, and adds `tools/coverage/coverage_tree.sh` to that group's files. Re-measure at your merge base.

  Carry: R10-FLY-SUITE-ENV-FLAKES

- **R10-LIVESTATE inherits an awaiting `_resolve_away`.** `async_set_away` can write the live away state inside the resolve's await. The resolve publishes only when the live state is unchanged across the await, and the expiry's in-place writes sit in the sync `_expire_away_override`. A copy-then-publish-whole of the away state keeps that guard or an equivalent. Its controls are the features.py checks `D14-s1-01 the away recovery estimate is handed off the loop, and a switch written during its await is not reverted by the resolve's publish` and `an unexpired away override is not re-persisted each cycle; a lapsed one is cleared and saved once`, plus this round's keystone on `_expire_away_override`'s returned pair. Round 1's text was landed on `handoff/audit-r10-roster` at `cccbf4fb`. The second and third controls are not on either roster yet (`grep -c "an unexpired away override is not re-persisted"` prints 0). Re-measure at your merge base.

  Carry: R10-LIVESTATE

## Friction

- orchestrator.md#5: contradiction: R10-LOOP-CPU's architect note names one owning seam, the `_replay_interval` call site, but the group's brief also moves `estimate_recovery_hours`, whose only route is `_resolve_away`. Carry: dismissed: raised for the orchestrator's after-edge call
- ci-autofix.md: unclear: `mutation-autofix` pins only killed mutants, so a site whose only driver times out in the pin run stays `ADDED UNPINNED` indefinitely. Nothing tells a seat to stop waiting for the bot after one timed-out pin run. Carry: dismissed: answered here by a fail-fast keystone, left to the orchestrator
