CODE CHANGED bca40aa9e97373c83c3a46dc958b07f9b570063d

Carry text main must land, verbatim, as a new entry in R10-FLY-SUITE-ENV-FLAKES's `carry` list on handoff/audit-r10-roster (it corrects that group's second carry, from d37aa1b1, which says "coverage-ratchet failed after it"; while the two disagree this one is right):

> From #2632 (R10-LOOP-CPU) round 3, correcting the carry above: coverage-ratchet's red in run 39874068348 (package 85.89 % against 96.0 %, 45 modules below 95.0 %) was neither the entities flake nor a flake. It was #2632's own defect, fixed in that PR: tests/features.py left 740 live process-worker children at its exit, and their coverage data files landed after the script's own process exited. tools/coverage/coverage_tree.sh's `measure()` checks `ls "$WORK/data/$s"/.coverage.*` the moment `tests/$s.py` returns, so it recorded `features.nodata` with no error, and the ratchet read a package-wide drop. A local run at ab6216ce reproduced the red: `features.nodata` and 85.88 % (18987/22108). A second run printed "could not combine tests/features.py's data" instead. The control at fef4a135 read 98.66 % (21801/22097). The seam left here is the instrument's: any measured script whose descendants outlive it loses its whole measurement silently. Make `coverage_tree.sh` refuse a measured script that exited 0 and left no data, or wait for the script's process group before the check, so a red names the script rather than 45 modules. Plant a script that leaves one child writing coverage after its exit; it must read red. Files: tools/coverage/coverage_tree.sh. Re-measure at your merge base.

Moves the away recovery estimate and the interval replay off the event loop (R10-LOOP-CPU). Round 3 fixes the defect behind the coverage-ratchet red. `_run_in_process` pickled each job straight into the worker's stdin, and a transport fault dropped the worker handle without reaping the child. This PR ships the model to the worker, and many learner tests stub a local closure onto that model. Each of those jobs failed to pickle and left one live child that no handle held: 740 of them at tests/features.py's exit (`## Figures`). Their coverage writes landed after features.py returned, and the coverage lane recorded no data for the script. The job is now serialised whole before the pipe is touched, as the worker's own replies already are (`process_worker._dump`). A stream that faults now reaps its child. Closes #2237.

**What changed in round 3** (one commit on the bot's `a4ccf1762`, which pinned two killed mutants):
- `coordinator._run_in_process` pickles `(fn, args)` with `pickle.dumps` before it takes the lock or the worker. A job that will not pickle raises `ProcessWorkerUnavailable("job cannot be pickled: ...")`, which `_await_off_loop` and `_await_optimize` already degrade to the executor. The worker is untouched and serves the next job.
- In the transport `except`, the child is killed and waited on before the handle is dropped. The reap is guarded like `_shutdown_process_pool`'s, so a reap that raises cannot escape untranslated, which would break the D1-s2-55 contract that every transport fault reaches the fallback as `ProcessWorkerUnavailable`. The return code in the message is still read before the kill.
- `tests/features.py` gains two checks beside the D1-s2-55 and D1-s2-05 worker checks. They run against a real worker: a job that will not pickle, and a reply stream the job corrupts (`print` writes ahead of the reply frame).
- It also gains a value check for CI's surviving mutant at `_expire_away_override`'s write-back guard: an unexpired override is not re-written or re-persisted, and a lapsed one is cleared and saved once.

Rounds 1 and 2 are unchanged: `away.resolve` and `_apply_return` are awaited and take `estimate_recovery`, bound by `_recovery_off_loop`. `_replay_interval` ships the pure `_replay_step` by name. `_resolve_away` publishes only when the live away state is unchanged across its await. The override expiry sits in the sync `_expire_away_override`. The barrier has `away` and `learner` arms with worker-route witnesses. The architect-note departure stands as raised in round 1 (`## Friction`).

## Head

`bca40aa9e97373c83c3a46dc958b07f9b570063d`: one commit on `a4ccf1762` (`ci: pin killed mutants`, mutation-autofix, 01:13:49Z; it adds two files under `tests/mutation_ledger/killed_by/` only), which sits on the round-2 head `ab6216cee6b688b45d6f4b89b70f84563307cacc`. Fast-forward from both. The commit touches `custom_components/heatpump_optimizer/coordinator.py` (+17 -1) and `tests/features.py` (+85).

The merge base is `fef4a1351db3e8e328d714e84299284c6876eecb`. `origin/main` was `e30b24bbc45afd1174f64f7051d05021e31b6a89` at 2026-10-23T02:35:19Z, and `git merge-tree --write-tree origin/main HEAD` exits 0 (the claim driver prints `LEDGER-MERGE: resolved tests/closures.json`). Python is `/opt/hpo/venv-ci` (3.14), with `tests/requirements-coverage.txt` installed into it for the coverage lane. CI's coverage lane runs 3.13.16.

The coverage lane and the scoped gate were run at this head. Figures marked `a08ed973` or `dc2df886` were taken at this commit before the last re-cut. `a08ed973` has this commit's production code on `ab6216ce`; `dc2df886` is the same code cherry-picked onto `a4ccf176`. Each differs from this head by named files: `git diff --name-only a08ed973a bca40aa9e` prints the two pin files and `tests/features.py`, and `git diff --name-only dc2df886b bca40aa9e` prints `tests/features.py` alone.

## Mutation proof

Each mutant was applied alone by an exact-once `str.replace` in a detached worktree at this head's commit (M1 and M2 at `a08ed973`'s identical production code), run, then discarded. `features.py` was run whole: `PYTHONPATH=tests/hastub python tests/features.py`.

| site | mutant | red |
|---|---|---|
| `_run_in_process`: `job = pickle.dumps((fn, args), ...)` and `stdin.write(job)` | M1: the pre-serialising `try` deleted and `pickle.dump((fn, args), stdin, ...)` restored | `R10-LOOP-CPU: a job that will not pickle degrades without touching the worker, which serves the next job as the same process` (`pid before=10495 after=10496 handle kept=False`); `1 of 4309 FEATURE CHECKS FAILED`, rc 1 |
| `_run_in_process`'s transport `except`: `worker.kill()` / `worker.wait()` | M2: the guarded reap deleted | `R10-LOOP-CPU: a reply stream that faults reaps the child it came from, never leaves it running unheld` (`child returncode=None`); `1 of 4309`, rc 1 |
| `_expire_away_override`: `if active != self._away_state.override_active or ret != parsed:` | M3: the table's `GUARD_OFF`, `if False:` (CI's survivor) | `an unexpired away override is not re-persisted each cycle; a lapsed one is cleared and saved once` (`[]` saved where `['persist_override']` is owed); `1 of 4310`, rc 1 |
| `_expire_away_override`: `return active, ret` | M4: `pass` (the table's `RETURN_DEL`, which CI's pin run timed out on) | the barrier, `replay.kernel_checks()`: `P10: an armed system identification ...` and `P10: an away override's recovery estimate ...`, 2 of 5 failed |

Round 1's mutants of the away and replay offloads (`_replay_interval`'s and `_recovery_off_loop`'s `_await_off_loop` calls inlined; `_recovery_off_loop:return estimate` deleted; `_resolve_away`'s guard `if True:`) are unchanged code and are not re-run. CI's pin run read the guard's `GUARD_OFF` (`if False:`) killed by `features.py`, and `_recovery_off_loop`'s `RETURN_DEL` killed, and `a4ccf1762` pins both.

**Failing test first.** The head's `tests/features.py` over the round-2 production code (`git checkout ab6216cee -- custom_components/` in a worktree at `a08ed973`, whose `features.py` held the two worker checks and not M3's) reads `2 of 4309 FEATURE CHECKS FAILED`, rc 1. Both new worker checks are red: `pid before=10499 after=10500 handle kept=False`, and `child returncode=None`. M3's check is a pin for an existing survivor, not a fix, so it reads green at the round-2 code; its proof is M3.

## Null control

- **Unmutated head.** `ALL 4310 FEATURE CHECKS PASSED`, rc 0, and the barrier reads 5 of 5.
- **The worker checks' arm.** Each new check first runs a picklable `os.getpid` job and records the worker's pid. The reuse comparison is between two real jobs on one live worker, so a probe that could not see a respawn would also fail the M1 run, which reads `after=10496` against `before=10495`.
- **The leak probe's control.** The spawn probe (`## Figures`) wraps `subprocess.Popen` and counts spawns of `process_worker.py` by `features.py` call site. At the merge base `fef4a135` it reads `spawns=26 live_at_probe_exit=0`. At `ab6216ce` it reads `spawns=765 live_at_probe_exit=740`. At the fix's first cut `82c63cf69` it reads `spawns=27 live_at_probe_exit=0`; the extra spawn is the new check's own worker, at its call site. That cut differs from this head's production code only in an `if rc is None:` around the reap, which was later dropped as needless because `kill()` is a no-op on a reaped child. The reap is not on the pickling route the probe counts.
- **The coverage lane's control.** The same instrument, `tools/coverage/coverage_tree.sh fast` with every script measured, reads 98.66 % at `fef4a135` and 85.88 % with `features.nodata` at the PR's merge tree. It reads 98.68 % at `a08ed973`, and this head's figure is in `## Figures`.

## Figures

**The coverage-ratchet red, read from its own logs** (job logs cached once each: coverage 120155414070 and coverage-ratchet 120165113949 of run 39874068348, and coverage 120155346133 of the sibling run 39874062299):
- Red run, coverage job: every measured script `exit=0` but `tests/golden.py exit=1 wall=206s`. The pre-grade printed `reused measurement grades below the floor; re-measuring the reused scripts`. It re-measured the three reused scripts (`ha_contract`, `open_meteo`, `frontend`), and coverage-ratchet then graded `FAIL package coverage 85.89 % >= 96.0 % (18988/22108 statements ...)`, `FAIL config_flow.py coverage 99.79 %` and `FAIL every module >= 95.0 % (45 below)`.
- Sibling run, coverage job: also `tests/golden.py exit=1 wall=167s`, and its coverage-ratchet passed.
- **golden.py's exit 1 is not the cause.** `coverage_tree.sh` runs `golden` under `GOLDEN_MODE=strict` and writes its output to `$OUT/logs/golden.log`, which is not in the job log. So its FAIL lines were read from a local run instead: `GOLDEN_MODE=strict PYTHONPATH=tests/hastub python tests/golden.py` exits 1 at both `fef4a135` and `ab6216ce` with the same five `DIFF` blocks (`winter_single_dhw` ... `summer_dhw_only`). `diff` of the two logs' `fail|drift|differ|mismatch` lines prints nothing, and the instrument's header states that golden runs strict on purpose: "coverage records which lines ran whatever the fixture comparison decides".
- **Reproduced locally**, with every script measured (`W5P_WORK=$(mktemp -d) PYTHON=python tools/coverage/coverage_tree.sh fast`, then `python3 -I -S tests/coverage_ratchet.py --coverage $W5P_WORK/out/coverage.json`):
  - PR merge tree (`ab6216ce` merged into `cf01e82e`, CI's merge base): `features.nodata`, `85.88 % (18987/22108)`, 45 below;
  - `ab6216ce` alone: `could not combine tests/features.py's data`, stage rc 1;
  - `fef4a135`: `98.66 % (21801/22097)`, ok;
  - `a08ed973`: `98.68 % (21824/22117)`, ok, every module >= 95.0 %, no `nodata`, 29 features data files combined.
- **The race, timed** (the merge-tree run): `$OUT/per/features.nodata` was written at 01:23:40.19. 741 of the 770 files in `$WORK/data/features` carry a 01:23 mtime, and the last was written at 01:23:41.9, after the check (`stat -c '%y' .coverage.*`). At `fef4a135` the same lane combined 28 features data files; at the merge tree it combined 0.
- **The spawn sites** (scratch probe `spawn_probe.py`, which wraps `subprocess.Popen`, runs `tests/features.py` by `runpy`, and reports at exit after the pool's own `atexit` reap). At `ab6216ce`, 717 of the 765 spawns come from `features.py:16843`, `_feed_residual`'s `_asyncio.run(c._async_learn_house_heat_loss())`, whose model carries the local `_sim` stub, and 18 from `features.py:41726`. A scratch probe of `_run_in_process` alone shows the mechanism at `ab6216ce`: `unpicklable=translated (process worker exited rc=None: Can't pickle <function <lambda> ...>)`, `first=7320 again=7321 kept=False first_child_alive=True`. At the fix it reads `job cannot be pickled: ...`, `first=8274 again=8274 kept=True`, and the corrupt-stream child `rc=-9`.

**The class census (fixer.md step 8).** The rule covers every site in the package that spawns a child, writes a frame to a child's pipe, or drops a child's handle: `grep -nE "pickle\.dump\(|stdin\.write\(|stdout\.write\(|_PROCESS_WORKER = None|subprocess\.Popen\(" custom_components/heatpump_optimizer/*.py`. Each site it returns at this head, and its disposition:
- `coordinator.py` `_ensure_worker`'s `subprocess.Popen(`: the one spawn site. It reuses a live worker and spawns only when the handle is `None` or dead; guarded.
- `_shutdown_process_pool`'s `_PROCESS_WORKER = None`: set after `kill`/`terminate` and `wait`, and only if the handle is still the installed one; guarded.
- `_run_in_process`'s `stdin.write(job)`: was `pickle.dump((fn, args), stdin, ...)`; closed in this diff.
- `_run_in_process`'s transport-`except` `_PROCESS_WORKER = None`: closed in this diff (reaped first).
- `_run_in_process`'s `load-err` `_PROCESS_WORKER = None`: the child itself has returned from `run_worker` after dumping `load-err`, so it exits on its own; guarded by the child.
- `process_worker.py` `_dump`'s `stdout.write(blob)`: serialised before the write since #511; guarded.

**The finder's harness:** `dev/audit/rounds/round10/D14/s1/p10_seams.py`, sha1 `c8ba174c3fa7f6768a7576d31b6597835df45589`. It is byte-identical at `fef4a135` and here (`git diff --quiet fef4a1351 HEAD -- <path>` exits 0) and roots at the cwd. It ran at `a08ed973` and at `fef4a135` as `HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 <harness> <args>`:

| args | base `fef4a135` | `a08ed973` |
|---|---|---|
| `--away` | `loop_kernels_away_seam=183`, `loop_kernels_all=183` | 0, 0 |
| `--away --deficit 0` | 0, 0 | 0, 0 |
| `--arm base` / `sysid` | `loop_kernels_all=0` | `loop_kernels_all=0` |
| `--arm fallback` | `loop_kernels_all=0`, `barrier_set_executor=3881` | the same |

**The barrier:** `replay.kernel_checks()` (scratch driver `barrier.py`) reads 5 of 5 at `a08ed973`.

**The scoped gate:** `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 23 script(s) run, 10 scoped out.` The gate was run as `PYTHONPATH=tests/hastub GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=fef4a1351db3e8e328d714e84299284c6876eecb bash tests/run.sh`: `25 TEST SCRIPT(S) PASSED; 9 SCOPED OUT AND NOT RUN`, rc 0, with `ALL 4310 FEATURE CHECKS PASSED` and `ALL 2401 ENTITY CHECKS PASSED` among them. That is scoped mode, not a full gate; CI's push to main runs it unscoped.

**Coverage lane at this head:** `W5P_WORK=$(mktemp -d) PYTHON=python tools/coverage/coverage_tree.sh fast` (every script measured), with `tests/features.py exit=0` and stage rc 0, then `python3 -I -S tests/coverage_ratchet.py --coverage $W5P_WORK/out/coverage.json`: `ok package coverage 98.68 % >= 96.0 % (21824/22117 statements ...)`, `ok config_flow.py coverage 100.00 %`, `ok every module >= 95.0 % (0 below)`, rc 0. No `nodata` entry is in `$OUT/per`, and 28 features data files were combined.

**Carry audit:** `python3 -I tools/audit/carry_audit.py --roster-ref origin/main check --body <this body>` prints `CARRY-AUDIT: 5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)`, exit 0, with `origin/main` at `e30b24bb`; `--roster-ref origin/handoff/audit-r10-roster` prints the same. Read against the branch's own tree (merge base `fef4a135`, which predates the group) it prints `1 bad destination(s)`, R10-FLY-SUITE-ENV-FLAKES. `pr-contract` reads the PR's merge with main, which carries the group.

**Structure:** `python3 tests/structure.py` exits 0 at `dc2df886`. No row moved, so nothing was re-recorded.

**Architecture score:** `python3 tools/audit/archscore/score.py --diff origin/main` prints `dS +0.1687 WORSENS (inadmissible: coord_footprint 2489->2491)` with `params_over_10 8 -> 7`, as in round 1. `_run_in_process` is a module function, and the score does not move with it.

**Cost.** No timing figure is taken; the defect is a count of live children, which contention cannot move. The fix adds one `pickle.dumps` into a `bytes` buffer per job, in place of the streamed `pickle.dump`.

## Architecture score

- `coord_footprint` 2489 -> 2491: unchanged from round 1, and explained there. It is the net of the publish guard and the expiry split that the P10 await in `_resolve_away` requires, against the replay step moved out to `_replay_step`. Without the guard and the split, the switch's override write is reverted, or the expiry's in-place writes sit in an async method (`shared_inplace_writes 17 -> 19`, measured before the split). Round 3's change is in the module function `_run_in_process`, which this metric does not read.

## Alternatives

- **Make the learner tests' stub picklable**, a module-level function in place of `_feed_residual`'s local `_sim`. This clears the test-suite leak but leaves the production route that produced it: a job that fails to pickle mid-write, or a stream that faults, still drops a live child unheld. The stub is also the faithful shape of the defect, and changing it would hide that.
- **Kill the worker on any transport fault, without pre-serialising.** This closes the leak, but a job that will not pickle then costs a worker respawn on every call. Under this PR that would mean every cycle a model carries an unpicklable attribute.
- **Shut the pool down at the end of each learner call in the tests.** This shapes the suite to the defect and leaves production unchanged.
- **Make the coverage instrument wait for descendants.** That is the instrument's own seam, carried to R10-FLY-SUITE-ENV-FLAKES (top of this body). It would have turned this red into a clearer one, not removed the leak.
- Round 1's alternatives (cache the estimate per solve, always precompute it, run all of `away.resolve` in the worker, publish first and fold in afterwards, ship the step as a `functools.partial`, keep `_resolve_away` whole and async) stand as written there.

## Red checks

Read for `ab6216cee6b688b45d6f4b89b70f84563307cacc` from the check-runs and the job logs of runs 39874068348 and 39874062299, at 2026-10-23T02:46Z.

- **`coverage-ratchet`**, red in run 39874068348 (job 120165113949) and green in the sibling run 39874062299: this PR's defect, fixed in this commit. It was not the entities flake. Round 2's body said "the failed entities step leaving the coverage data short", which was wrong: entities.py ran `exit=0` in that coverage job.
  - The cause: features.py's 740 leaked workers wrote their coverage after the script returned, so the instrument recorded `features.nodata` (`## Figures`). The sibling run went green because its check happened to land after those writes; the leak is deterministic at `ab6216ce`, and the race is not.
  - The answer: the job is serialised before the pipe, and a faulted stream reaps its child. Two features checks pin this, with M1 and M2 as proof, and the coverage lane reads 98.68 % at the fix.
  - Cheaper detector: none ran. prepr.sh and the scoped gate pass at `ab6216ce`; features.py passes there with 740 children alive. The first instrument to see the leak was CI's coverage lane, and it saw it only as a package-wide drop.
  - Countermeasure, carried: the two checks above fence the transport route itself. The instrument's silent `nodata` for a script that exited 0 is carried to R10-FLY-SUITE-ENV-FLAKES (carry text at the top of this body), whose fix makes the red name the script. Standing cost: a per-script check in `coverage_tree.sh`'s `measure()`, unmeasured until that group builds it. Carry: R10-FLY-SUITE-ENV-FLAKES
- **`fast (3.14)`**, red in run 39874068348 (job 120155413953) on `1 of 2401 ENTITY CHECKS FAILED` and green in the sibling run, the gate-lease priority concurrency control in `tests/entities.py` (round 2's reading, carried on handoff/audit-r10-roster at d37aa1b1). The 740-child leak was present in both runs, since it is deterministic at that head, so the leak alone does not produce that red. Whether its load contributed to the timing check failing was not measured; the fix removes it, and a re-run at this head is the measurement. This diff touches neither `tests/gate_lock.py` nor that check. Carry: dismissed: a timing check this diff does not touch, already routed to R10-FLY-SUITE-ENV-FLAKES at d37aa1b1
- **`closures`**, UNDER-SCOPED in run 39871545349: repaired by `closures-autofix` in `ab6216cee` (`tests/closures.json` only), per `ci-autofix.md`, accepted and not duplicated. The cheaper detector is prepr.sh's closures step, which seats skip under `PREPR_SKIP_CLOSURES=1` (CI owns closures); its standing cost is CI's own run. Round 3 adds no import, and `ci_predict.py` reads `no closures or fast red predicted`. Carry: dismissed: repaired by the bot commit ab6216ce, nothing further owed
- **`mutation`** and **`mutation-pins (1)`** (job 120155543073): mutation-pins was not hung. It ran attempt 2 from 23:48:19Z and completed `success` at 01:13:25Z, and mutation-autofix then pushed `a4ccf1762` (01:13:49Z), which moved the head; this round works from it. The run's own summary is `PIN KILLED: 2 pinned, 2 left unpinned (1 survived, ... 1 timed out ...)`.
  - The survivor is `coordinator.py:9549 GUARD_OFF -- lives` at `ab6216ce` (`_expire_away_override`'s write-back guard, line 9564 here). This round answers it with a killing check, M3. Survivor triage is never automated, and this one is answered by a check rather than a verdict.
  - The timed-out site is `9553 RETURN_DEL -- skip-timed-out in tests/features.py` (`return active, ret`, line 9568 here). It is killed by the barrier, M4. Carry: dismissed: both answered in this commit, M3 and M4, and re-measured by CI's next pin run

## Unpinned sites

`PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` at `dc2df886` (the same production code as this head) lists one:
- `custom_components/heatpump_optimizer/coordinator.py:9568 RETURN_DEL: return active, ret`: killed by the value checks `P10: an away override's recovery estimate simulates the ramp in the process worker, never on the loop (D14-s1-01)` and `P10: an armed system identification sizes, gates and fits its night in the process worker, never on the loop` in `tests/replay.py`, which `tests/entities.py` runs (M4). CI's pin run timed out driving it through `features.py`. `mutation-autofix` pins what CI kills (`ci-autofix.md`).

The guard at `:9564`, CI's survivor, is not in the predictor's list, but CI's table drives it; it is killed by M3's check in `features.py`. The round-3 sites in `_run_in_process` add no unpinned site to the predictor's list.

## Forward-carry

- **R10-FLY-SUITE-ENV-FLAKES: coverage_tree.sh's per-script data check races a script's descendants.** The carry text is at the top of this body for main to land. It corrects the d37aa1b1 carry's claim that coverage-ratchet "failed after" the entities flake, and adds `tools/coverage/coverage_tree.sh` to that group's files. The control: the coverage lane at `ab6216ce` reads `features.nodata` and 85.88 %, at `fef4a135` 98.66 %, and at this commit's fix 98.68 %. Re-measure at your merge base.

  Carry: R10-FLY-SUITE-ENV-FLAKES

- **R10-LIVESTATE inherits an awaiting `_resolve_away`.**
  - `away.resolve` takes `estimate_recovery`, run in the process worker by `_recovery_off_loop`.
  - `async_set_away` can therefore write the live away state inside the resolve.
  - The resolve publishes only when the live state is unchanged across the await, and the override expiry's in-place writes sit in the sync `_expire_away_override`.
  - A copy-then-publish-whole of the away state keeps that guard or an equivalent. Its controls are the `features.py` checks `D14-s1-01 the away recovery estimate is handed off the loop, and a switch written during its await is not reverted by the resolve's publish` (red with the guard as `if True:`) and, new in round 3, `an unexpired away override is not re-persisted each cycle; a lapsed one is cleared and saved once` (red with the expiry guard as `if False:`).
  - Re-measure at your merge base.
  - Round 1's text was landed on `handoff/audit-r10-roster` at `cccbf4fb508cca8ce711dd06add13cc034ac0edb`; the second control is new here.

  Carry: R10-LIVESTATE

- **`ux10_flow_into_model.py`'s summary step raises `KeyError: 'UPPER_PLANTED'` at the base as at the head** (round 1, `de69745ff`). It is a harness defect outside this group's seam, left for the orchestrator to route. No issue was filed.

  Carry: dismissed: pre-existing at base de69745ff, routed to the orchestrator in this body

## Friction

- orchestrator.md#5: contradiction: R10-LOOP-CPU's architect note names one owning seam, the `_replay_interval` call site. The group's brief moves `estimate_recovery_hours`, whose only route runs through `_resolve_away` and its call site, so the brief cannot land within the note. Carry: dismissed: raised in this body for the orchestrator's after-edge call
- ci-autofix.md: unclear: mutation-autofix pins only killed mutants. CI's survivor at `_expire_away_override`'s guard was not in `ci_predict.py`'s `ADDED UNPINNED` list, so `prepr.sh` step 6d never named it and the round-2 body owed it no line. It surfaced only in the pin job's log. Carry: dismissed: answered by M3's check in this commit; the predictor's move-versus-add reading is R10-FLY-CIPREDICT-LAYOUT's file, but not its defect, so it is left to the orchestrator
