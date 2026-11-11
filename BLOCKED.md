# BLOCKED: R10-HOTFIX-RESTORE-BASE-SKEW part 1, second dispatch -- a handoff already exists

Question: Part 1 is already handed off by an earlier seat (handoff/r10-hotfix-restore-base-skew at 5ec2425619, handoff-body at fa03981c21), and is blocked only on the relay folding the R10-PROCESS-SLIM carry (the note below). Should the relay fold that carry and re-run body_push.sh for 5ec2425619, as that note asks, or replace 5ec2425619 with this seat's head a27995c354, which adds the gate_lock fix so that prepr.sh is clean with no HPO_GATE_PRIORITY override? This seat did not overwrite handoff/ (non-fast-forward) and pushed no body.

The dispatch said an earlier session had pushed nothing, so this seat cut part 1 again from origin/main f24d107bd7. It found the existing handoff only when the push to handoff/ was refused as non-fast-forward.

## What a27995c354 adds over 5ec2425619 (local only; the diff is below, recoverable)

tests/gate_lock.py `_priority_cases`: the normal waiter in `priority_first` and `slot_priority` now enters under `_Env(None)`. prepr.sh exports `HPO_GATE_PRIORITY` (2 on this branch), and the waiter inherited it, so recording tests/entities.py in prepr's closures step failed with `2 of 2707 ENTITY CHECKS FAILED`, both arms reading `order=['normal', 'urgent']`. 5ec2425619's seat worked around this by running prepr with HPO_GATE_PRIORITY=0 and carried it to R10-PROCESS-SLIM (the carry that body_push refused). Measured here by a scratch driver over `_priority_cases(g)`:
- before the fix, HPO_GATE_PRIORITY=2: both arms `FAIL ... order=['normal', 'urgent']`;
- after the fix, HPO_GATE_PRIORITY=2: both arms `ok ... order=['urgent', 'normal']`;
- before and after the fix, with it unset: both arms `ok`.
At a27995c354, `tools/pr/prepr.sh <body>` exits rc=0 with no override; `tests/entities.py` prints `ALL 2707 ENTITY CHECKS PASSED`, `tests/doc_claims.py` prints `ALL 315 checks PASSED`, and `tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

```diff
diff --git a/tests/gate_lock.py b/tests/gate_lock.py
index b496343862..aef8d9f328 100644
--- a/tests/gate_lock.py
+++ b/tests/gate_lock.py
@@ -1625,9 +1625,12 @@ def _priority_cases(g) -> list[tuple[str, bool, str]]:
             time.sleep(0.15)
             g.release(who, lock_dir=d)
 
-        normal = threading.Thread(target=one, args=("normal",), daemon=True)
-        normal.start()
-        normal_queued = bool(ticket_text(d, "normal"))
+        # The normal waiter enters with no priority, whatever the caller
+        # exports (prepr.sh exports its own HPO_GATE_PRIORITY).
+        with _Env(None):
+            normal = threading.Thread(target=one, args=("normal",), daemon=True)
+            normal.start()
+            normal_queued = bool(ticket_text(d, "normal"))
         with _Env("2"):
             urgent = threading.Thread(target=one, args=("urgent",), daemon=True)
             urgent.start()
@@ -1735,9 +1738,10 @@ def _priority_cases(g) -> list[tuple[str, bool, str]]:
             time.sleep(0.1)
             g.release_slot(who, lock_dir=d, slots=1)
 
-        normal = threading.Thread(target=one, args=("normal",), daemon=True)
-        normal.start()
-        normal_queued = bool(ticket_text(pool, "normal"))
+        with _Env(None):
+            normal = threading.Thread(target=one, args=("normal",), daemon=True)
+            normal.start()
+            normal_queued = bool(ticket_text(pool, "normal"))
         with _Env("2"):
             urgent = threading.Thread(target=one, args=("urgent",), daemon=True)
             urgent.start()
```

---

# BLOCKED: R10-HOTFIX-RESTORE-BASE-SKEW part 1 -- body_push REFUSED CARRY-LANDED

Question: Will the relay fold the R10-PROCESS-SLIM carry below into the round's roster and re-run body_push.sh for part 1? This seat may not write the roster.

Part 1's code head is pushed to handoff/r10-hotfix-restore-base-skew at 5ec2425619 (the grader admission only, on origin/main a7628041dc). prepr.sh is clean there (rc=0, run with HPO_GATE_PRIORITY=0; the body says why). The refused body is kept at handoff-wip/r10-hotfix-restore-base-skew-body 8393d32874.

body_push.sh output (exit 4):

```
fill-red: the diff adds no unpinned mutation site; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R10-HOTFIX-RESTORE-BASE-SKEW at 5ec242561916, 2 carries, 0 refused
CARRY-MISSING R10-PROCESS-SLIM body item 84d0892c: not in its brief or carries: '- tests/entities.py\'s two `gate lease priority` checks ("an urgent waiter takes before an older norm'
CARRY-LANDED: 1 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r10-hotfix-restore-base-skew-body 8393d32874984a55b28d261c4b4b46927a2db094
```

The commits below this one (4f9fc83dc7, 5ab1c861c8, e8d0311b2f, 033d619595) are part 2's source and are left in place. The part-1 blocked note they carried follows, unchanged.

---

# BLOCKED: R10-HOTFIX-RESTORE-BASE-SKEW

Question: May this group land in two pull requests, the grader admission e8d0311b2f first (alone, onto main) and then the workflow fix 4f9fc83dc7+5ab1c861c8+033d619595 rebased onto it? Or does the owner rule that this PR merges with the two base-graded reds below, which are predicted and cannot be repaired from this branch?

## Why it cannot go green as one pull request

The fix changes every restore site's `PINNED:` value. For example:

    PINNED: ${{ inputs.restore_source || github.event.pull_request.base.sha || ... }}

The new first alternative is the merge commit's first parent, which ci.yml's prelude resolves once per run. Two pinned graders read these lines against exact-form allowlists, and CI runs both from the BASE's copy:

- `dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check` (`PINNED_OK`, `_bad_pinned`). It runs in governance `policy-docs` and is restored from the base there.
- `tools/pr/prepr.sh` step "pinned graders" (the `PIN_AWK` pinstyle regexes). It runs in pr-contract and is restored from the base there.

Measured at 033d619595:
- main's `codeowners_gap.py` on the head's workflows prints `RESULT uncovered_files=19` and `REFUSED`.
- At origin/main dbd1ab5b07 the same command prints `RESULT uncovered_files=0`.
- With the head's own `codeowners_gap.py` (commit e8d0311b2f, which admits the resolver prefix ahead of any admitted form) it prints `RESULT uncovered_files=0` and `SELF-TEST: 58 probe(s), 17 null(s), 0 wrong`.
- Mutating that admission back to the exact-set test prints `uncovered_files=19` and `2 wrong`.

So on this PR's own run, the base's graders refuse it until e8d0311b2f is on main. e8d0311b2f alone only admits additional forms, which no workflow on main uses yet, so it is inert on main.

## State of the fix (on this ref)

- Replay of PR 3424's merge, `dev/audit/harnesses/r10_restore_base_skew.py`:
  - old source d08ed31049: `RESULT exit=1`, `RESULT attributeerror=True`, with "3 file(s) differ", the same as job log line 8819;
  - the head's resolver: `RESULT source=c620ebba96...`, `RESULT exit=0`, `RESULT attributeerror=False`;
  - the workflows at origin/main: `RESULT source=none`, so the defect remains;
  - fresh-base null control: identical under both sources;
  - an event base newer than the merge parent: the resolver prints FAIL.
- `tests/entities.py` at 5ab1c861c8: `ALL 2709 ENTITY CHECKS PASSED`. With pr-contract's site reverted, it fails only the new barrier check (`pr-contract.yml:pr-contract restores from BASESHA`).
- `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `ci_predict.py --apply-inert`: no red predicted.
- Not yet re-taken at 033d619595: entities.py and the prepr.sh body check.

Draft body: the `## Head` and the figures still name 5ab1c861c8, and `## Red checks` does not yet name the two base-graded reds.
