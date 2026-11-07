Root-cause record for the third instance of the deferral-red class (#3293 fefaa492, #3267 cc6ee11f, #3268 64fe84b2 skipped on `ci: red at the head: gate` while each code run was unfinished). Cause: gate.py publishes an edit run's deferral as a failed `gate` at once; `merge_train.py classify` reads a conclusion alone (rule dates from 9262e6f43, 2026-10-22; the producer moved at fa921fd59, cc100c275 and 52f9fc5b3). #3287's harnesses and review had the producer in their unit, never a consumer; its reviewer saw `classify` read RED on a deferral and waited. Process state (c). Record: `dev/audit/rca/r10-gate-busy-defer-4.md`. Changes no file #3290 owns (`train.sh` is left to it); #3290 prevents all three skips (code run unfinished at each); it does not prevent the settle gap (code run green, sweep not yet re-run), which the record shows only as a synthetic scene.

Carries not routed here: the four carries (settle gap; the six readers outside `classify`'s family and the shared predicate; `orchestrator_tick.py`'s stale 720 s text; `train.sh add <pr> --front` with no verdict) are written in the record's Forward-carry section with their owners. body_push refuses a `Carry:` line whose destination's brief does not hold it, and landing one is a push to the round's roster branch, which this seat may not make: the orchestrator lands them (carry_audit.py land-ops).

Carry R10-HOTFIX-TRAIN-DEFER-WAIT (refused as a `Carry:` line by body_push: that group's brief does not hold it, so it is prose here and in the record's Forward-carry; the orchestrator lands it): `train.sh add <pr> <verdict> --front` is refused by `merge_train.py` as an unknown argument after `--`; #3290 owns `train.sh` and should add the pass-through and its argv pin.

## Head

0f71c6d7b6075266010c2687e7d65e6dccc449b7, on origin/main dee8b413fd7da7b07f13e28a93d7d49b4a9e978a (unmoved since the last `tools/pr/prepr.sh` run: rc=0, `PRE-PR: 0f71c6d7...`). `git diff origin/main...HEAD -- tools/audit/seat/train.sh` is empty.

## Mutation proof

The countermeasure is the replay harness; its mutant is #3290's wait removed (`deferred = {GATE} if busy else set()` replaced by `set()` in an export of `pr3290` a38bd141): `replay` goes from `defects=0` back to `RESULT replay defects=3 settle_gap=1 null_bad=0 scenes=7`, rc 1.

## Null control

At origin/main dee8b413 the replay reads the three evidence heads RED (`defects=3`, rc 1); at #3290 a38bd141 it reads WAIT (`defects=0`, rc 0). Controls in the same run: a code run that ended failure reads RED, an all-green head reads GREEN, a red non-gate required context beside a running code run reads RED (`null_bad=0`). The settle-gap scene is synthetic (built from the #3293 fixture) and reads RED at both programs; counted apart as `settle_gap=1`.

## Figures

- `python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_4.py replay` : defects=3 at dee8b413, 0 at a38bd141 (`--tree` export of each), 3 with the wait mutated out; wall 0.055 s (`time` around it).
- `python3 dev/audit/harnesses/r10_gate_busy_defer_3.py census --since 2026-11-07T19:14:31Z --until 2026-11-07T21:30:00Z` : deferral_fails=14 heads=14 held_runner_s=1844 resolved=3 by_bot=3 by_human=0 median_min=0.9 (88 s run; window from #3287's merge to the run). Not measured by me: the train's SKIP count (its log is not in the tree); the 32 of 56 SKIPs in the record are quoted from #3290.
- Seams (reach enumeration, section 3 of the record, a read of origin/main for readers of a `gate` conclusion): eight rows read the deferral as final, six outside the `classify` family (`platform_gate`, `policy_refusal`, `gate_digest`, `merge_pr.sh`, `ci-watch.sh`, `ruleset_cutover.py`); none is closed by this diff, each is dispositioned under Forward-carry. No instrument enumerates them; I used a grep-based read.
- Mutant step: `MUTANT_CMD="python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_4.py replay"` through `prepr.sh` step 6d: `diff mutants no survivor` (survivors 0). Wall time not separately printed.

## Unpinned sites

none: prepr step 6d listed no unpinned site.

## Red checks

none known at this head; CI not yet run. No red check triggered this record.

## Forward-carry

none

## Friction

none
