R10-RELAY-ARM-ORDER (P601): `cloud_relay.sh pass()` ran `handoff_arm` (serial `update_pr.sh` plus full prepr per PR) before `probe_arm`/`confirm_arm`, so a returned verdict waited behind every queued update. Now `pass()` takes the one open-PR listing first (`open_prs`, into `cloud-prs-open.$$`), then runs probe_arm, confirm_arm, handoff_arm, carry_fold_arm, stuck_arm, noreturn_arm. `handoff_arm` and `confirm_arm` reuse the listing; a failed listing leaves no file and each arm lists for itself as before. Updates are not detached (update_pr.sh already answers BUSY per branch).

Closes nothing (triage s6-batch182 P601).

## Head
332f882cf8e9ba5c0415df400d89dda1682babf1 (base cbd23f1c8bf6185c3a6c10f6e4aaf562417e75bf)

## Mutation proof
Mutated the predicate (the order line in `pass()`) back to `handoff_arm; carry_fold_arm; probe_arm; confirm_arm`, ran `bash tools/audit/seat/cloud_relay.sh --self-test`: `FAIL a verdict returned before the pass is POSTED before handoff_arm starts`, 420 checks, 1 failed. Restored.

## Null control
Unmodified order fails that check (above). Within the new tree: a second pass with no new probe ref posts nothing more (`POSTED` count for #71 stays 1) and handoff_arm still ran once per pass (2 runs); no listing file is left in the state dir. Pre-existing checks (including the pass-banner checks) stay green: 420 checks, 0 failed.

## Figures
- self-test result: `bash tools/audit/seat/cloud_relay.sh --self-test` (420 checks, 0 failed at this head).

## Red checks
none at this head by my run; main's `tests / fast` (features.py combi census, since #3398) is inherited from main and not caused by this diff.

## Forward-carry
Carry 1 (OPENER-LIVE-TIP, tools/audit/seat/open_driver.py): not built here; a different file and seam from the arm order in cloud_relay.sh pass(), outside this group's files. Carry: R10-REVIEW-DISPATCH-RESIDUE

## Friction
none
