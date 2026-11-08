The gate sweep's `settle` branch re-runs red gates in a loop, and the loop uses up the CI concurrency every PR waits on. GitHub re-stamps every skipped job of a run each time that run's gate is re-run. `undecided()` arm 1 in `tools/ci/sweep.py` read those stamps as sources that finished after a sibling's gate started. So a sibling's sweep re-ran that gate, the re-run re-stamped its own skipped jobs, and the two runs kept re-running each other until `ATTEMPT_CAP`. #3308 at head 6016f9dd shows it: runs 42470642055, 42470643072 and 42471173865 were at attempts 39, 25 and 24 when this was recorded.

Fix, in `tools/ci/sweep.py` only (with doc corrections):
1. `undecided()` arm 1 reads `sources(jobs)`: jobs that are neither a gate nor `skipped`.
2. `settle` leaves a gate whose latest attempt the bot started (`SWEEP_ACTOR`, `github-actions[bot]`: the sweep's `github.token`, which ci.yml's `refresh` also posts as) unless a source finished after that attempt started (`settled()`). So it re-runs a gate at most once per source change, whichever arm reads the gate as undecided.
3. Unchanged: the `run()` branch (green gate that covers the newest event), `covers_newest`, and gate.py's own refresh and defer re-runs.
4. Corrected: the false no-loop claim in sweep.py's module doc ("the branch cannot loop"), the same claim in gate.py's DEFERRAL doc ("settle cannot loop"), and `undecided()`'s "nothing loops".

Root cause: release trigger, introduced by #3287 (52f9fc5b34, r10-gate-busy-defer-3) in v7.1.6, process state (c). The process was followed: the self-test's fixtures modelled skipped jobs as sources, and no fixture was recorded from a real re-run listing. The full analysis is owed by a separate RCA seat at `dev/audit/rca/R10-RCA-SWEEP-SETTLE-LOOP.md`, not part of this diff.

Topic r10-hotfix-sweep-settle-loop. VERSION, the manifest, the RELEASE_NOTES heading, the budgets and both claim files are untouched. Scope: `MODE: FULL`, because the gate.py doc correction "changes the gate itself". Locally I ran the self-tests of both changed programs, `tests/entities.py` (the one closure that reads sweep.py) and the `run_always` scripts. The FULL suite is left to CI (fixer.md step 5).

## Head

6158186e11747e9f145eb761264b458453326f9d (base 4fe7d5934b0a4bc092c9398f29b579fbd2df8b50)

## Mutation proof

Each mutant was applied to `tools/ci/sweep.py` alone, then `python3 -I tools/ci/sweep.py --self-test` was run, then the file was restored from a copy:
- M1, a skipped job counts as a source again (drop `and j.get("conclusion") != "skipped"` in `sources`): 5 failed: `#3308: skipped jobs re-stamped by a sibling's gate re-run are no source; settle re-runs nothing` (swept from each of the three runs), `#3308 null: a non-skipped source (codeql python) ... re-runs that gate, once`, `#3308 null: that re-run ... is final; no sweep re-runs a gate`.
- M2, `settled()` returns False: 1 failed: `settle: an overlapping pair of re-run gates, re-run by github-actions[bot], with no source after them, is final`.
- M3, `settled()` drops its `not source_after(...)` clause: 1 failed: `#3308 null: a non-skipped source (codeql python) finishing after a sibling gate started re-runs that gate, once`.
- M4, settle skips the `settled()` test (`if False:`): 1 failed: the same overlapping-pair check as M2.

## Null control

- Base tree (4fe7d593 sweep.py with the new self-test): `sweep self-test: 60 checks, 7 failed`. The #3308 replay posts `jobs/128721143069/rerun` and `jobs/128721143539/rerun` from every run. Those are the gates of 42470642055 and 42470643072, and the recorded listings show both re-run at 11:48:33Z (attempts 39 and 25).
- A real source still triggers a re-run. With codeql python of 42470642055 set to finish at 11:47:30Z, after 42470643072's gate started at 11:46:43Z, there is exactly one post (`jobs/128721143539/rerun`). Once that re-run starts after the source and re-stamps its own skips, a sweep from each of the three runs posts nothing.
- A human re-run is not the bot's. The same overlapping pair with `triggering_actor` `tvofi` still re-runs the lower id (`jobs/10/rerun`).
- Every pre-existing settle and run() check passes unchanged (52 of them, including the eight-ordering census and its no-loop second round).

## Figures

- head self-test: `python3 -I tools/ci/sweep.py --self-test` -> `sweep self-test: 60 checks, 0 failed`
- base self-test: base sweep.py from `git show <base>:tools/ci/sweep.py` placed next to the new `tools/ci/sweep_selftest.py`, then `python3 sweep.py --self-test` -> `sweep self-test: 60 checks, 7 failed`
- #3308 replay, posts per triggering run: `python3 -c "import sweep_selftest as t; [print(v, (w:=t.world3308(v)).sweep() and w.posts) for v in t.REC3308]"` run in tools/ci -> `[]` for each of the three runs at head; at base, two posts for each run (listed under Null control)
- gate self-test (unchanged behaviour, doc-only edit): `python3 -I tools/ci/gate.py --self-test` -> `gate self-test: 77 checks, 0 failed`
- recorded attempts: `gh api repos/tvofi/heatpump_optimizer/actions/runs/<id>` for the three runs -> run_attempt 39, 25 and 24 when this was recorded, triggering_actor `github-actions[bot]` on all three. This figure grows while main runs the unfixed sweep.
- fixture source: `gh api repos/tvofi/heatpump_optimizer/actions/runs/<id>/attempts/<n>/jobs` for 42470642055/38, 42470643072/24 and 42471173865/24. The edit runs are kept whole. 42470642055 is trimmed from 41 jobs to its gate, its 9 skipped jobs and 5 non-skipped sources.
- class census, as a rule: `git grep -n "completed_at\|started_at" -- 'tools/ci/*.py' ':!tools/ci/*selftest*'`. Outside sweep.py it returns only gate.py lines 662, 664, 682, 739 and 740, all inside `self_test()` (the #3282 recording's `at_time`/`replay`). Disposition: test-only, no production reader. In production, the only reader of job stamps is sweep.py's `undecided()`/`settled()`, closed in this diff. gate.py's `busy()`/`judging()`/`started()` read job status, never stamps.
- The diagnosis seat's cost figures (bot re-attempts across PR runs, runs at the cap, Gate sweep runs) were not re-measured here and are not stated as this PR's.
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`
- `tests/harness_headers.py` -> `ALL 112 HARNESS HEADER CHECKS PASSED`; `tests/closure.py selftest` -> `ALL 118 closure shrink pins PASSED`; `tests/env_drift.py --claims-only <base>` -> `claims hygiene: ... ok`; `tests/layout.py` -> `layout self-test: ok`
- `tests/entities.py` locally: it crashes in `_hb_stdlib_reads` with `PermissionError: Cannot get task port` (the macOS sampler entitlement, which this machine lacks). That is this machine's limitation and has nothing to do with this diff. CI's Linux runner runs it.

## Red checks

none

## Forward-carry

none

## Friction

none
