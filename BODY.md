Root-cause record for the third instance of the deferral-red class (#3293 fefaa492, #3267 cc6ee11f, #3268 64fe84b2 skipped on `ci: red at the head: gate` while each code run was unfinished). Cause: gate.py publishes an edit run's deferral as a failed `gate` at once; `merge_train.py classify` reads a conclusion alone (rule dates from 9262e6f43, 2026-10-22; the producer moved at fa921fd59, cc100c275 and 52f9fc5b3). #3287's harnesses and review had the producer in their unit, never a consumer; its reviewer saw `classify` read RED on a deferral and waited. Process state (c). Record: `dev/audit/rca/r10-gate-busy-defer-4.md`. Changes no file #3290 owns (`train.sh` is left to it); #3290 prevents all three skips (code run unfinished at each); it does not prevent the settle gap (code run green, sweep not yet re-run), which the record shows only as a synthetic scene.

Carries not routed here: the four carries (settle gap; the six readers outside `classify`'s family and the shared predicate; `orchestrator_tick.py`'s stale 720 s text; `train.sh add <pr> --front` with no verdict) are written in the record's Forward-carry section with their owners. body_push refuses a `Carry:` line whose destination's brief does not hold it, and landing one is a push to the round's roster branch, which this seat may not make: the orchestrator lands them (carry_audit.py land-ops).

Carry R10-HOTFIX-TRAIN-DEFER-WAIT (refused as a `Carry:` line by body_push: that group's brief does not hold it, so it is prose here and in the record's Forward-carry; the orchestrator lands it): `train.sh add <pr> <verdict> --front` is refused by `merge_train.py` as an unknown argument after `--`; #3290 owns `train.sh` and should add the pass-through and its argv pin.

## Head

68277a92172af185228019fba5f7fdb572288e19, on origin/main 425b858495432c8dceb89d8d13866550352ba54f (main moved, merged; `PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh` rerun at this head: rc=0, `PRE-PR: 68277a92...`).

## Head note

Repair of the red the dispatch seat's bus dispatch refused at 330159042 (`tests / fast (3.14)`: `python3 tests/harness_headers.py`, run 42528461690). Two defects in `dev/audit/harnesses/r10_rca_gate_busy_defer_4.py`, both the branch's own: (1) `ROOT = Path(__file__).resolve().parents[3]` is a depth root, which the harness_headers depth-seam check refuses (`FAIL depth seams ... :37`); it now resolves by the canonical `repo_root(start)` copy. (2) `replay` built `Train` with `object.__new__` and no `wall`, and main's `classify_at` now calls `sweep_settling(runs, self.wall())`, so the replay died with `AttributeError: 'Train' object has no attribute 'wall'` (not caught by harness_headers; the harness is not executed there); the harness now sets `t.wall` to five seconds after the newest completion in the scene. No production file changed.

## Mutation proof

The countermeasure is the replay harness; its mutant is #3290's wait removed (`deferred = {GATE} if busy else set()` replaced by `set()` in an export of `pr3290` a38bd141): `replay` goes from `defects=0` back to `RESULT replay defects=3 settle_gap=1 null_bad=0 scenes=7`, rc 1.

## Null control

At origin/main dee8b413 the replay reads the three evidence heads RED (`defects=3`, rc 1); at #3290 a38bd141 it reads WAIT (`defects=0`, rc 0). Controls in the same run: a code run that ended failure reads RED, an all-green head reads GREEN, a red non-gate required context beside a running code run reads RED (`null_bad=0`). The settle-gap scene is synthetic (built from the #3293 fixture) and reads RED at both programs; counted apart as `settle_gap=1`.

## Figures

- `python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_4.py replay` : defects=3 at dee8b413 (re-run at this head after the repair), 0 at this head (`RESULT replay defects=0 settle_gap=0 null_bad=0 scenes=7`; the earlier a38bd141 figure is the pre-merge read), 3 with the wait mutated out; wall 0.055 s (`time` around it).
- `python3 dev/audit/harnesses/r10_gate_busy_defer_3.py census --since 2026-11-07T19:14:31Z --until 2026-11-07T21:30:00Z` : deferral_fails=14 heads=14 held_runner_s=1844 resolved=3 by_bot=3 by_human=0 median_min=0.9 (88 s run; window from #3287's merge to the run). Not measured by me: the train's SKIP count (its log is not in the tree); the 32 of 56 SKIPs in the record are quoted from #3290.
- Seams (reach enumeration, section 3 of the record, a read of origin/main for readers of a `gate` conclusion): eight rows read the deferral as final, six outside the `classify` family (`platform_gate`, `policy_refusal`, `gate_digest`, `merge_pr.sh`, `ci-watch.sh`, `ruleset_cutover.py`); none is closed by this diff, each is dispositioned under Forward-carry. No instrument enumerates them; I used a grep-based read.
- Mutant step: `MUTANT_CMD="python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_4.py replay"` through `prepr.sh` step 6d: `diff mutants no survivor` (survivors 0). Wall time not separately printed.

## Unpinned sites

none: prepr step 6d listed no unpinned site.

## Red checks

- `tests / fast (3.14)`, `python3 tests/harness_headers.py` at 330159042: caused by this branch (new harness with a depth root). Cheaper detector: `tests/harness_headers.py` itself, ~2 min locally with `PYTHONPATH=tests/hastub`, and in `run_always`; it was not run before the earlier handoff. No new countermeasure: the detector exists and ran at the first gate that was run. Fixed: at this head it prints `ALL 112 HARNESS HEADER CHECKS PASSED`; at 330159042 it printed `1 of 112 HARNESS HEADER CHECKS FAILED`.
- main's red: none found; the gate failed twice on this one check.
- Null control: other checks green at 330159042 are untouched, the diff since is the one harness file plus the main merge.

## Forward-carry

none

## Friction

none
