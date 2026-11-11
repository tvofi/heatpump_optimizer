R10-RELAY-ARM-ORDER (P601): `cloud_relay.sh pass()` ran `handoff_arm` (serial `update_pr.sh` plus full prepr per PR) before `probe_arm`/`confirm_arm`, so a returned verdict waited behind every queued update. Now `pass()` takes the one open-PR listing first (`open_prs`, into `cloud-prs-open.$$`), then runs probe_arm, confirm_arm (with --confirm), handoff_arm, carry_fold_arm, stuck_arm, noreturn_arm. `handoff_arm` and `confirm_arm` reuse the listing; a failed listing leaves no file and each arm lists for itself as before. Updates are not detached (update_pr.sh already answers BUSY per branch). Repair round: the self-test now pins the arm order itself, killing mutants m7 and m8 that survived.

Closes nothing (triage s6-batch182 P601).

## Head
9647bc111d7e57b2928ca887ed1f6724a873b44e (base cbd23f1c8bf6185c3a6c10f6e4aaf562417e75bf)

## Mutation proof
Predicate: the arm-order line in `pass()` (`probe_arm; [ -z "${CONFIRM:-}" ] || confirm_arm; handoff_arm; carry_fold_arm`). Each mutant is a copy of `tools/audit/seat/cloud_relay.sh` with that line replaced, run as `bash mut_<m>.sh --self-test` (424 checks at the head; unmutated: 0 failed):
- m7 `carry_fold_arm` before `probe_arm`: 2 failed (new order arms)
- m8 `confirm_arm` after `handoff_arm`: 1 failed (`pass --confirm runs the arms probe, confirm, handoff, carry_fold, stuck, noreturn in that order`)
- m9 original order (handoff, carry_fold, probe, confirm): 3 failed
- m10 `confirm_arm` first: 5 failed
- m11 `carry_fold_arm` before `handoff_arm`: 2 failed
- m12 `confirm_arm` dropped: 9 failed
- m13 `carry_fold_arm` dropped: 2 failed
Survivors: none of m7-m13. (The earlier m1-m6 set is the previous round's; its kills are unchanged since only a test arm was added, but I did not re-run it this round.)

## Null control
Without `--confirm` the same order holds with `confirm_arm` absent (own check). A second pass with no new probe ref posts nothing more; handoff_arm runs once per pass; no listing file is left in the state dir; a counting lister runs once per pass under --confirm and once for a lone handoff_arm.

## Figures
- `bash tools/audit/seat/cloud_relay.sh --self-test`: 424 checks, 0 failed at 9647bc111 (command prints the count).
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh` (interpreter lacks homeassistant; ruled allowed): rc=0 at 9647bc111.

## Red checks
none owed by my run. Main's reds (`tests / fast (3.14)` combi census, PR #3466; `governance / instrument-self-tests`, R10-HOTFIX-PUSHER-CENSUS) are inherited from main, not caused by this diff.

## Forward-carry
Carry 1 (OPENER-LIVE-TIP, tools/audit/seat/open_driver.py): not built here; a different file and seam from the arm order in cloud_relay.sh pass(). Carry: R10-REVIEW-DISPATCH-RESIDUE

## Friction
none
