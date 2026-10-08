This is the countermeasure from #2056's root cause, in group R9-CI-2. `nightly-ha` ran only on `schedule` and `workflow_dispatch`, so #2041's A16 check, whose container half no pull-request lane executed, merged unrun. Both arms then went red at the next schedule on `main` (run 37753990323).

With this change, `nightly-ha` runs, still unrequired, on a pull request whose three-dot diff touches what the lane's driver reads outside the package:

- **`closure-scope`** emits a new output, `nightly_ha`. It is `true` when `git diff --quiet "$BASE"..."$HEAD" -- <pathspecs>` finds a change.
- **`nightly-ha`** now `needs: [closure-scope]`, and its `if:` admits `pull_request` only when that output is `'true'`. `!cancelled()` keeps it running on `schedule` and `workflow_dispatch`, where `closure-scope` is skipped.
- **`nightly-ha` declares `HPO_JOB_GRADES: nothing`.** It is reachable from a pull request now, and it runs `tests/nightly_ha.py` and `tests/ha_floor.py` from that pull request's own copy. `codeowners_gap.py` refuses that for a grading job (`prepr.sh` printed `uncovered_files=2 ... REFUSED` before this line). The job is unrequired, and on a pull request its verdict is about that pull request's own driver, so it grades nothing. `codeowners_gap.py --check` now tags both files `NO-PR-JOB`.
- **The pathspecs are measured, not guessed.** `closure.py record` was run over a real run of the lane (throwaway branch `handoff/r9-nightly-ha-measure`, run 37764931838). Both images opened the same 127 repository files, 37 of them outside `custom_components/`: `tests/nightly_ha.py`, `tests/ha_contract.py`, `tests/harness.py`, `tests/golden/config_flow.json` and 33 files under `tests/hastub/`. The pathspecs are those paths, plus `tests/requirements-nightly-ha.txt`, which the job installs.
- **Not triggers:**
  - The package itself. Catching a product change late in real Home Assistant is this lane's charter, and running it on every product pull request would put a registry outage or a Home Assistant release on all of them.
  - `tests/ha_floor.py`. The PR gate already checks its snapshot offline.
  - The `nightly-ha` job's own definition in `tests.yml`. The `tests/entities.py` reach check below covers a change to it, not a run.
- **`tests/entities.py` pins three things.**
  - REACH: `nightly-ha`'s `if:` is evaluated over five events and three values of the output. It runs on schedule, on dispatch, and on a pull request with `nightly_ha == 'true'`, and on nothing else.
  - THE OUTPUT: it is declared from the `decide` step.
  - COVERAGE: every repository file outside the package that `_stage` opens is matched by the pathspecs, re-measured on each gate run with an audit hook around a real `_stage`. The package's own files are not copied during that measurement. The first version copied them, and the closure re-record (`e8701d2e`) then widened `tests/entities.py`'s measured closure from 80 to 90 production files. That broke the deployment-shape lane's #1218 selection-cost checks: `tests/entities.py` exited 1, 2 of 2214 failing, at the merge with `main`. `tests/closures.json` is back to `main`'s recording, and `closures-autofix` re-records anything this run measures as missing.
- **The reporter's derivation** in `tests/entities.py` no longer counts a diff-gated pull-request admission as visibility. So `nightly-ha` stays in `nightly_status.REQUIRED_LANES`, and `nightly-status` still grades it on `main`.
- **`tests/nightly_ha.py`** gains a docstring paragraph saying when the lane runs. That paragraph is also this pull request's "fires" trigger.

**The proof on this pull request's own runs:**

- **Does not fire.** At head `aa88452d`, whose three-dot diff touches no pathspec, pull-request run 37777137892 has `closure-scope` success (job 113311361795) and `nightly-ha` skipped (job 113311471940).
- **Detects the defect.** At head `e8701d2e`, which still lacked #2056's fix in its base, workflow_dispatch run 37784310008 has `nightly-ha` failure on both images (jobs 113335020479 and 113335020245): `FAILED: 3 of 64 checks: ['a16:debug_inline', 'a16:debug_capped', 'run:exit_status']`. That is the A16 defect, and the code head below merges `main` with #2056.
- **Fires.** At the head this body describes, `tests/nightly_ha.py` is in the diff. Its pull-request run's `nightly-ha` arms are cited after they conclude, in a comment and in the next body re-take.

## Head

`3b9b6fc69cdfb928202faba5043a5e7a9d683fcd`

## Mutation proof

Each mutant was applied at `3b9b6fc6` in a scratch worktree, then `PYTHONPATH=tests/hastub python3 tests/entities.py` was run (seat venv-ci). Unmutated, it prints `ALL 2214 ENTITY CHECKS PASSED`.

- N1: the `pull_request` clause deleted from `nightly-ha`'s `if:`. The reach check fails (`('pull_request', 'true', False)`).
- N2: the flag condition deleted, so every pull request runs it. The reach check fails, and so does `the reporter watches exactly the lanes a pull request cannot see`.
- N3: `tests/ha_contract.py` deleted from the pathspecs. `every file nightly-ha's driver stages from outside the package is a path whose change runs nightly-ha on the pull request` fails.
- N4: the `nightly_ha` output line deleted from `closure-scope`. The reach check fails.
- N5: `_stage` made to copy `tests/layout.py` into the driver mount as well. The coverage check fails.

The same five, run at `4a7c846f` before the merges, failed the same way, at that tree's count of 2212 checks.

## Null control

With `main`'s `tests.yml` (merge base `816547ef`) and this branch's `tests/entities.py`, the run exits 1 with 2 checks failing:

- The reach check: `('pull_request', 'true', False)`.
- The coverage check: no pathspecs, and `_stage`'s reads uncovered, starting `tests/golden/config_flow.json`, `tests/ha_contract.py`, `tests/hastub/...`.

## Figures

- **Measured read set**: run 37764931838, jobs 113270143734 (stable) and 113270143203 (2025.2.0). Each printed the record between `MEASURED-READS-BEGIN` and `MEASURED-READS-END`, and both printed 127 paths, with identical sets. Paths outside `custom_components/` were counted with `grep -v '^custom_components/'`. These are CI's results, read through `gh api repos/tvofi/heatpump_optimizer/actions/jobs/<id>/logs`.
- **Closure widening**: `git show <ref>:tests/closures.json`, counting entries under `custom_components/` in `tests/entities.py`'s closure, gives 80 at `origin/main` and 90 at `e8701d2e`.
- **Gate scope**: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` reports `MODE: FULL` (`tests.yml` changes the gate), so CI runs the full suite. Locally at `3b9b6fc6`:
  - `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  - `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2214 ENTITY CHECKS PASSED`.
  - `PYTHONPATH=tests/hastub python3 tests/debug_collect.py`: `ALL 64 DEBUG COLLECT CHECKS PASSED`, run at `ab4675fd`; the commit after it changes only `tests/entities.py` and `tests/closures.json`.

## Red checks

Five checks were red on this branch's earlier heads. Each is named, with its answer.

- **`nightly-ha`, both arms, dispatch run 37784310008 at `e8701d2e`** (jobs 113335020479 and 113335020245): `FAILED: 3 of 64 checks: ['a16:debug_inline', 'a16:debug_capped', 'run:exit_status']`. This is #2056's A16 defect, present because that head's base predates #2056's merge. The code head here merges `main` with #2056 (`4647321d`), which clears it. This red is the countermeasure detecting the defect it was built for. A cheaper detector for it, `tests/debug_collect.py`'s writer checks, landed with #2056.
- **`closures`** (job 113311468769 at `aa88452d`): `UNDER-SCOPED: tests/entities.py really reads 11 file(s) the committed closure does not list`. These were the package files that the first version of the coverage pin copied through a real `_stage`. `closures-autofix` re-recorded them as `e8701d2e`, which then caused the next red. The pin no longer opens package files, and `tests/closures.json` is back to `main`'s recording. Anything this head's run still measures is re-recorded by `closures-autofix`, as `ci-autofix.md` has it. Cheaper detector: none for this diff. The recording is CI's Linux recorder, and `gate-scoping.md` forbids a local full derive off Linux.
- **`fast (3.14)`** (jobs 113335112750 and 113335104886 at `e8701d2e`): `FAILED python3 tests/entities.py`, the two #1218 deployment-shape selection-cost checks. This is the 80-to-90 widening described above, caused by this branch's first pin and fixed at this head. The cheaper detector was a local `tests/entities.py` run after the autofix commit, at seconds of standing cost per merge. It is now part of how this branch is checked: it found the failure at `ab4675fd` before this push.
- **`nightly-status`** (job 113311361395 of run 37777137892) reads `NIGHTLY FAILED: mutation-ledger, mutation-nightly, record-autofix failed 1 night ago`. That is scheduled run 37595831734 at `be0cb82`, the last concluded nightly on `main`. None of those three jobs is changed here. This diff keeps `nightly-ha` in `REQUIRED_LANES`, and the reporter's derivation check passes, so the reporter grades the same lanes as before. The red is `main`'s, and its fix and proof belong to `main`: a dispatch of Tests on `main` once the mutation lanes are repaired. No cheaper detector applies to this diff.
- **`delivery-status`** (job 113310733902) prints `DELIVERY STATUS UNCHECKED -- 76 rowed, 0 pending, 0 overdue`. The UNCHECKED comes from its `merge-collection` skip ("9 merge commit(s) in the window name no pull request"), a property of `main`'s merge subjects. This diff adds only its own row, `dev/programme/delivery/2058.md`. Its `tests.yml` change touches no step `delivery_status.py` reads: `closure-scope`, `nightly-ha` and comments only. No cheaper detector applies to this diff.

## Forward-carry

none

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
