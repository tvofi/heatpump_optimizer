## Root cause

Analysis: `dev/audit/rca/R10-RCA-2671-WAVE-SCRIPT.md` (handoff/r10-rca-2671-wave-script).

**State (c)**, three causes; none of them is a seat failing to follow an instruction.
1. `wave-script`: `prepr.sh` steps 3e–3g run each pinned grader from the head's copy, which is the push-to-main direction. The pull-request run grades with the base's copy. Reproduced on 338c9ba49: the branch's `agreement.mjs` gives `unregistered=0`, rc 0. The base's, under CI's restore, gives `unregistered=3`, rc 1. Null control #2669 passes, rc 0. `ci_predict.py` does not run the lane at all.
2. `instrument-self-tests`: `ref_privacy.py --check` has no local path. At 338c9ba49 it prints `1 refused` (`ledger.py:726`); at origin/main, `0 refused`.
3. The lane admits no passing tree for a new shared grammar. Registering it beside its second writer is UNREGISTERED under the base copy. Registering it first is `dead=3`. `wave-script` is required. #2423 merged red.

**Cost test**, in seconds per pull request. The defect floor is about 600 s: run 39996377402 took 9 min 47 s. P is 0.68 % (3 PRs in 440 merges, 2026-10-09..10-23) for causes 1 and 3, and at least 0.45 % (2 instances) for cause 2.
- (A) The base-pinned arm, keyed on the lane's reader closure: 0.85 s standing against 4.1 s expected. Build.
- The same arm keyed on any wave-script pin: 5.0 s standing. Not built.
- (B) `ref_privacy --check`: 1.46 s standing against 2.7 s expected. Build.
- (C) A route for a registration: no bounded defect cost, because the head stays red until a bypass. This is the owner's decision.

**Countermeasures**: A and B are carried to R10-FLY-CIPREDICT-LAYOUT; this corrects #2671's own carry, which named neither CI's restore nor a narrow key. C is carried to R10-MERGE-SUBJECT-HARDEN; the orchestrator should confirm that destination. Both are queued to the roster seat.
