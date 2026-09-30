# R9-EG-B10 resume — solve lifecycle (#1754, #1755)

Seat: opus fixer, high effort. Lane EG, group R9-EG-B10, class architecture,
`rca: false` — the Root-cause sections were posted on the issues by this seat
(#1754 comment 5902898846, #1755 5902899081).

## State (round 2, current)

- branch `handoff/r9-eg-solve-lifecycle`, worktree
  `/Users/timmalmstrom/fix-r9-eg-solve-lifecycle` (Mac). PR **#1779** (open,
  author app/hpo-author, tvofi's review requested).
- merge base `9d578722` (origin/main tip after the absorb).
- commits: `4be53607` fix + the two failing-test blocks → `c4995d3f` merge
  origin/main → `f66f6762` round-1 budget re-record → `8aee72d8` round-1 resume
  note (PR created here) → `ce3df669` round-2 unload-latch closure + leak test →
  `58879e08` round-2 budget re-record → this resume note.
- **Round 1 review: BLOCKED, 3 items** (reviewer evidence
  `/private/tmp/audit-7/review-1779/`, head 8aee72d8). All three addressed in
  round 2:
  1. (fix) a removed entry's latched cause never withdrew — `_release_registrations`
     now calls `_clear_worker_fallback(hass, entry_id)`; the `#1755` leak arm in
     features.py (A latches, A released, B fails-then-recovers) FAILS at 8aee72d8
     and PASSES at round-2 head. Done in `ce3df669`.
  2. (claims) "C1 reads flat at head" was FALSE — the `extra` arm's first interval
     moves `issue=Y`→`issue=n` because the rename `_WORKER_FALLBACK_CAUSE`→
     `_WORKER_FALLBACK_CAUSES` invalidated C1's `reset()` (it sets a dead
     attribute; the dict carries cause state across arms). The probe arm (8/0) IS
     flat both ends (reviewer-confirmed). Body corrected.
  3. (claims/raise) "payment pool empty" was FALSE — `reach.py --list` returns 4
     dead coordinator properties (13 LOC). The raise CONCLUSION stands (13 < 24
     owed; the deletions are scheduled to R9-F10.4/#1661 and barred by the
     borrowed-file rule). Reason corrected in the body, in `58879e08`'s message,
     and in a #201 CORRECTION comment (f66f6762's message is immutable, not
     rewritten).
- features.py at round-2 head: `1 of 3588 FEATURE CHECKS FAILED` — the
  pre-existing Mac-float `R9-F2.1 P3` only (green in the container); all 4 #1754
  and all 4 #1755 checks (incl. the leak arm) pass.
- structure.py: `STRUCTURE RATCHET PASSED`. Round-2 raise vs base 9d578722:
  coordinator_attrs 153→154, coordinator_loc 9010→9034, coordinator_multiassigned_attrs
  115→116, internal_call_edges 307→308, max_class_loc 9010→9034.
- Mutation proof: round-1 M1–M4 (reviewer re-ran, 4/4 killed, 0 survivors) + the
  round-2 leak arm is its own closure mutant (removing the closure = the 8aee72d8
  FAIL).

## The budget raise (posted before each push)

Round-1 raise posted on #201 comment 5902714958. Round-2 CORRECTION (the honest
payment reason + the 9034 values) is posted on #201 before the round-2 push. The
PR requests @tvofi's approving review at the head (budget-raise-gate 0013; this
diff touches no CODEOWNERS path, so the raise gate is the sole owner-review
trigger). Never self-approve.

## Next steps

1. Post the #201 CORRECTION comment (honest payment reason + the round-2 caps).
2. Re-take the PR body at the round-2 tip (## Head, the C1 extra-arm correction,
   the payment-reason correction, the merge-base reconcile f88e6af8→9d578722, the
   leak fix + its mutation arm, the mutation-lane timeout note); `prepr.sh`;
   `app_push.sh` PATCHes the body and pushes (the coordinator re-posts if it
   re-takes the body at the final head).
3. Watch CI to the first full conclusion. KNOWN: `budget-raise-gate` red by design
   (awaiting tvofi); the round-1 `mutation` lane TIMED OUT at 60 min driving the
   new unpinned sites (they are killed by the slow features.py driver) and
   `mutation-autofix` went red with it — per the orchestrator, no `--pin-killed`
   /`--triage-survivors` shortcut; the new arms kill the latch-path sites. If the
   bot pushes a `ci: pin killed mutants` commit, WAIT and build on top, never
   duplicate. Flag the timeout to the orchestrator if it recurs.

## Evidence locations

- finder harnesses + companions: `/tmp/eg-b10-evidence/`. features runs:
  `-base.log` (6/3587), `-head2.log` (1/3587 @4be53607), `-merged.log` (1/3587
  @c4995d3f), `-r1-leak.log` (2/3588: the leak arm FAILS @8aee72d8 + R9-F2.1 P3),
  `-r2.log` (1/3588 @round-2 head). mutation `/tmp/eg-b10-mutation.log`.
- reviewer evidence: `/private/tmp/audit-7/review-1779/` (VERDICT.md, leak_probe.py,
  C1-base/head*.log, reach-*-list.txt, mutants/).
