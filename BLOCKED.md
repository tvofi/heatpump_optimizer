# R10-NUDGE-RETIRE: handoff held by the hot-file rule

Question: hand off once #3499 boards a train or merges, or have the orchestrator order the two? `body_push.sh` refuses only `hot-file: #3499 holds an unboarded merge verdict and shares tools/audit/seat/orchestrator_tick.py`; every other arm passes.

- Code head `4e620f9b1e3cbd57cc412e43a386513792f15f79` is on `handoff/r10-nudge-retire`; `tools/pr/prepr.sh` exits 0 there (`PRE-PR: 4e620f9b1e3c ... rc=0`), and `git merge-tree --write-tree origin/main HEAD` reports no conflict at origin/main `0731b35877`.
- The body, with `Carry 0` answered, is kept at `handoff-wip/r10-nudge-retire-body` (`02a3570131de`); `body_push.sh r10-nudge-retire <that BODY.md>` is the handoff once the hold clears.
- #3499 (R10-GATE-DEFER-BARRIER) also edits `dev/governance/roles/nudge.md` step 15, which this group deletes. Its new clause (a red that `merge_train.py classify <head> --pr <N>` reads WAIT is not returned) is already stated in `tools/audit/seat/sweep_template.md` step (6) at this head. If #3499 merges first, this head meets a modify/delete conflict on that file: resolved by the deletion, then `prepr.sh` re-run. If this lands first, #3499 resolves it the same way and loses nothing.
