Fix review: merge 312913795abd5f2865384afdc0f1f9c9659bd466

bus-nonce: 4fd4b4e852996a7a5036c86e7c40e745

PR #2480, group R10-FOLLOWER-DEBOUNCE, head 312913795abd5f2865384afdc0f1f9c9659bd466, round 2.
Reviewed from a detached worktree at the head; head was still that SHA when this was written.
Round 1 blocked at 5748642ff (review/2480 = 5d33e39c); the two round-1 blocks are repaired.

RESULT head=312913795abd5f2865384afdc0f1f9c9659bd466
RESULT recarry: HEAD parents = 5748642ff (old head) + a25de7a6 (current origin/main); diff old->new on the five PR files is empty
RESULT three-dot vs base a25de7a6 = 5 files, 223 insertions, 12 deletions (identical to round 1)
RESULT merge-tree vs origin/main a25de7a6 exits 0 (no conflict)
RESULT follower_debounce=9 cases, 0 failed at the head; origin/main's file prints REFUSED (first step None)
RESULT mutants M1 (deferral unreachable), M2 (oldest red), M3 (trigger not excluded) each fail the named case; M4 (red-only job if:) yields 1 defect starting `if:`
RESULT structure=STRUCTURE RATCHET PASSED
RESULT closure select=MODE: SCOPED -- 2 script(s) run (tests/entities.py, tests/harness_headers.py)
RESULT carry_audit on the live body=3 finding items, 3 routed, 0 unrouted, 0 bad destination (rc 0)
RESULT CI: fast (3.14), closures, coverage, pr-contract (x2), instrument-self-tests, mutation all success
RESULT CI: Analyze (python) cancelled at the 30-minute job timeout (success in ~21.5 min at 5748642)

## Round-1 blocks, resolved

- carry-missing: the destination now carries the finding. R10-CI-LAYOUT's `carry`
  array at roster commit `5ab01bbb098d9d7eb3a28c00c95f242b5d05cc62` (the live tip of
  `origin/handoff/audit-r10-roster`) holds an entry from R10-FOLLOWER-DEBOUNCE (#2480)
  that states the debounce semantics, its control (`follower_debounce.py`, 9 cases,
  the null control, mutants M1-M4), the re-measurement instruction, the precondition
  ("measure the per-head red count BEFORE keeping it") and the API-lag gap. The body's
  three `## Forward-carry` bullets each end in `Carry: R10-CI-LAYOUT` and cite
  `5ab01bbb`. Evidence: `roster-carry.txt`, `carry_audit.txt`.
- pr-contract was red at 5748642ff on two unrouted Forward-carry bullets. It is now
  `success` twice at 312913795, and the body's `## Red checks` names it and answers it
  (cheaper detector `tools/audit/carry_audit.py check --body`, ~1 s). Evidence:
  `check-runs-3129137.txt`.

## Recarry

`312913795` is a clean merge: its second parent is origin/main `a25de7a6`, and the diff
from the old head to the new head touches only files main advanced (RCA doc, delivery
rows, INSTRUMENTS.md, three seat scripts). None of the PR's five files changed, so the
round-1 measurements stand at the new head. Evidence: `recarry.txt`.

## Notes (non-blocking)

- The body's `## Figures` says `tests/entities.py` printed `ALL 2351 ENTITY CHECKS PASSED`.
  That figure is a snapshot at the authored head `f210e78` against base `64b0ae69`, which
  `## Head` states; at the merged head it is 2359 (the head's `tests/entities.py` is
  byte-identical to 5748642ff, where I measured 2359 after main added 8 `R.check` calls).
  I did not re-run at `f210e78`, so 2351 is not independently re-derived; the head's
  own `fast (3.14)` job is green. `Carry: dismissed: figure is scoped to the authored head and disclosed in ## Head`
- `Analyze (python)` is `cancelled` at this head. It is a 30-minute job timeout
  (`codeql.yml` line 184), not a `failure`; the same job was `success` in ~21.5 minutes
  at 5748642ff, the diff changes no production Python, and pr-contract's red list is over
  `failure` conclusions only, so the body's red-check obligation does not cover it. It is
  a required check, so the orchestrator must re-run it green before merge.
  `Carry: dismissed: orchestrator re-runs the cancelled required check (not a failure, not diff-attributable)`
- The design residuals from round 1 stand and are now carried in the destination brief:
  the API-lag gap, the "after" call count as a model rather than a measurement (a
  `workflow_run` file cannot be exercised before merge), and the changed-head null control
  as a structural pin (`tests/entities.py` exact-equality on the head-keyed group) rather
  than a driven case. `Carry: R10-CI-LAYOUT (landed at 5ab01bbb)`
- Both round-1 blocks are henceforth owned by this PR's head, not a later stage.
  `Carry: dismissed: repaired in round 2`
