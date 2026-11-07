R10-HOTFIX-NIGHTLY-STATUS: `tests / nightly-status` read red on main and every PR ("slow failed in the last verification dispatch") because the nightly now takes ~3.5 h and the check graded the newest *concluded* run, which a newer in-flight run had already answered.

Cause is both (c): (b) the grader named a stale run, and (a) the `slow` lane really is intermittently red. Measured with the Actions API at 20:00Z: dispatch 42235215315 (14:35Z, head 33e60b5) failed `slow`; dispatches 42242870295 (15:25Z) and 42247578523 (15:55Z) passed `slow` in about 30 min, but their `mutation-nightly` and `mutation-ledger-push` ran until 19:17Z and 19:34Z, so at 18:56Z (PR 3252, job 128089771822) both were in flight and the check printed the 14:35Z failure.

The lane failures are in `cycle_cost` (tests/replay.py): "runner class unknown: ref_ms 41.5 lies in no band of COST_RUNNER_CLASSES" (job 127950940724, and ref_ms 40.1 in schedule run 41943946464), plus budget overruns in 41555367389 and 41749544997. That is the R10-REPLAY-COST-BUDGET seam, which I did not touch. This PR fixes only the grading. The lane flake is still open on main after the merged R10-REPLAY-COST-BUDGET work (ref_ms 40.1 on 11-05, 41.5 on 11-06 still fall in no band); I could not land a roster carry from a fixer seat, so the orchestrator should route it to a replay-cost group. Note: i read only the header of the r10-process-slim handoff-body and did not confirm whether it holds this cause.

## Head

b0ef8f54964a832950dce1ddd02423f3cfb60aa8 (merged with origin/main at 198b8f7ed21f; prepr.sh rerun after that merge).

## Mutation proof

Predicate mutated: `superseded = [j for j in bad if j.get("name") in greens]` replaced by `superseded = []`, run through the scoped gate. `tests/entities.py` went FAILED (376 s); the unmutated tree passes "ALL 2638 ENTITY CHECKS PASSED", including the new check "a failed lane is superseded only by a NEWER in-flight run that concluded the same job green; every other arm stays FAILED". I did not capture which check the failing mutant run named, since the gate log shows only the script line. Restored after.

## Null control

Same check, four arms that must stay FAILED: no newer run; a newer run whose `slow` failed; a newer run whose `slow` is still pending; an in-flight run that is older than the concluded one. Only a strictly newer in-flight run with the same job concluded `success` yields PASSED, and the report names the superseding run. A really failing lane therefore still reads red. Run failed-on-unfixed-tree: without the change the first arm reads FAILED (the live behaviour above).

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
