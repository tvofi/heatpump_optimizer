Fix review: merge 957818d6ea3d2dee9a71e2c01f450b673dfc327b

bus-nonce: 9734f03599206744a41b661c72d0a923
pending-ci: gate

## Scope

Round 2 (a delta round) over reviewed-head 74ae5f90aa476e1c6293449a506dd24e91903000, measured at head 957818d6ea3d2dee9a71e2c01f450b673dfc327b. The packet prints `Review scope: full` only because verdict/3582 names f14a2fbcf5, not 74ae5f90. `review_carry.py f14a2fbcf5 74ae5f90` prints CARRY: the one commit between them is the mutation-autofix pin. So the round-1 merge verdict covers 74ae5f90, and by fix-review.md step 12 this round is its delta. `review_carry.py 74ae5f90 957818d6` prints FRESH-REVIEW (ev/delta.txt).

The delta has three parts. 0ef4857190 merges PR 3532's head fd5fe52fa7 as a stacked head; remerge-diff shows no hand resolution, only the ledger driver's `LEGACY-MERGE: resolved tests/closures.json` set-merge. That code is 3532's and is reviewed there. 5eda176a1d is this group's one authored commit: two lines in docs/architecture.md. 957818d6ea merges 5eda176a1d onto 74ae5f90, with an empty remerge-diff. The production delta comes entirely from the stacked head, and it is reviewed on 3532. The added doc row puts no already-reviewed code at risk, so the scope is not widened.

## Evidence

- The doc claim holds at the head. The new `duty_switch` row text is "and what orders the legs of a both step the arbiter serves". `duty_switch.both_step_duty` (duty_switch.py:547-561) orders the step's legs with `duty_legs.both_step_legs(..., rec.learner.split(), ...)`. `DutySwitchLearner.split` (:402-410) is `duty_legs.leg_rule(*self.planner_pairs())`, read only through the latches. `pump_arbiter.py:1852` calls `both_step_duty`. So a latched direction's estimate orders the arbiter's both-step legs, as the row says (ev/doc_claim_code.txt).
- Doc controls at the head: `python3 tests/doc_claims.py` prints ALL 348 checks PASSED. `--markers --roster dev/programme/rosters/wave-r10-groups.json` prints 0 of 0 marker(s) due. Both match the body (ev/doc_claims.txt).
- Step 1 mutation: n/a. The group's own delta is two documentation lines, with no production line to delete.
- Step 2: no finder's harness is named (packet: none). For a docs-delta group, the doc checks above are the controls.
- Step 4: neither claim file changes between 74ae5f90 and the head (ev/merge_and_version.txt).
- Step 5: the three-dot diff against merge base 0f37833e21 touches neither VERSION nor the manifest. RELEASE_NOTES.md gains one body paragraph and no heading. That paragraph is the "Upgrade note, added 2026-11-13" from 693313ff4b (R10-HOTFIX-FLOW-SETPOINT-STUCK, PR 3561's line). It arrives through the stacked 3532 head, which carries 3561's head 30b069508f. It is not on origin/main, and this group did not author it. CLAUDE.md rule 4 refuses only a change to the heading (ev/merge_and_version.txt).
- Step 13: `git merge-tree --write-tree origin/main 957818d6ea` gives rc=0 with no conflict, with origin/main at a77d71fb75 (ev/merge_and_version.txt).
- Step 7: the body's `## Head` names 957818d6ea3d2dee9a71e2c01f450b673dfc327b, which merges authored head 5eda176a1d. It matches.
- Step 11, red checks: the owed-reds set is in ev/owed_reds.txt. I read each job the body names from the Actions API (ev/red_checks.txt):
  - `tests / mutation` job 132318156274, at f14a2fbcf5: `MUTATION TABLE REFUSED ... 7 of them added by this diff`. This matches the body.
  - `arch-score` job 131942718609, at e9b1651aae: `FAIL: dS +0.0221 WORSENS; unexplained: coord_footprint 2505->2513`. This matches the body's figures.
  - `tests / briefs` job 131889367213, at 0cb8073467: `LEGACY-CONTROL VACUOUS: carry-1412.json`. This matches the body.
  - `tests / fast (3.14)` jobs 131831771785 (at 0cb8073467) and 132302973404 (at d712c2ba4a, started on a Saturday): both conclusions are failure in "Run the suite". I did not read the failing test names from the logs, so the body's attribution to the flakes fixed by PRs 3579 and 3578 is not re-derived here.
  - All five reds are on stacked-head commits, and the body answers each one: a cheaper detector, or the finding that none exists. The trigger is therefore answered.
- Figures I could not re-derive: the body's 32 HA-importer and 92 module counts were re-derived in round 1 (92) and not again here. The `prepr.sh` rc=0 and "self-test 553 passed" were not re-run, because the role cites CI's heavy runs.
- CI at this head: `merge_train.py classify 957818d6ea3d2dee9a71e2c01f450b673dfc327b --pr 3582` printed WAIT (rc=3) on every poll from 11:22:51 to 11:52:55 UTC. The last line was `WAIT 957818d6ea3d2dee9a71e2c01f450b673dfc327b pending: gate red: none` (ev/classify.log). No required check was red while I polled. The verdict carries `pending-ci: gate`. The arch-score at this head is CI's to read: at render time the packet's digest showed arch-score success (id 132430255595).
- Step 12: the head was still 957818d6ea3d2dee9a71e2c01f450b673dfc327b when the verdict was written (`git ls-remote` of fix/r10-arch-docs-delta).

## Findings

- Residual: the body's `## Red checks` attributes the `arch-score` red (coord_footprint 2505->2513, job 131942718609 at e9b1651aae) to "3574's branch". The job ran in `CI edit pr=3481`, and `git branch -r --contains e9b1651aae` lists only 3481's branches and this PR's, so the growth and its owed `## Architecture score` line belong to 3481. The red is still inherited and answered, and arch-score is success at 74ae5f90aa. Carry: dismissed: the misattribution changes no obligation of this PR, and 3481's own review reads its own arch-score.
- Residual: the body says 3561 is "read but not merged". The stacked 3532 head carries 3561's head 30b069508f (ff45fd27c7), including its RELEASE_NOTES.md upgrade-note paragraph. The null result for 3561 still holds, because the head is in the tree the doc checks ran on. Carry: dismissed: a wording slip in the body; the documentation result does not change.
