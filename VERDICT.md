Fix review: merge 12d32a204c923e768f6146a510445374c23f548c

bus-nonce: c46f1a9fb6285618a32110c63bb4375a

Round 1. Record PR (triage s8 batch 84, P321): two new files, dev/programme/triage/s6-batch84.md and dev/programme/delivery/3030.md. No production code, so no mutation proof, finder harness or both-ends measurement applies.

## Findings

- The ruling defers the "BUSY on a dead lock, no retry for 4 minutes" part as one instance with its cause unmeasured, and reopens it on R10-FLOW-BODY-ONLY if a relay BUSY on a dead holder lasts more than two passes. I judge the deferral sound: update_pr.sh:12-16 (checked at origin/main) documents exit 75 with retry on the next pass, and the filing gives no evidence beyond the 4-minute gap, which may be the pass interval. Carry: dismissed: one instance, cause unmeasured; the reopen condition is recorded in the ruling itself.

## Evidence

- Head 12d32a204c923e768f6146a510445374c23f548c is the PR head, and I measured it. origin/main is 861f949ae, the base the ruling cites. It has not moved.
- The claim "no Code: line at 861f949ae" re-derives. `git grep -n 'Code:' 861f949ae -- tools/audit/seat/body_push.sh tools/audit/seat/cloud_relay.sh` prints nothing (rc=1), and the same at origin/main. See ev/grep-code-base.txt.
- The claim that P233 is the built form of the fix re-derives. s6-batch46.md#P233 at origin/main specifies the Code: trailer in body_push.sh, the handoff-body-stale level line in cloud_relay.sh's handoff arm, and the REFUSE reason in the update level line. Group R10-FLOW-BODY-ONLY on the roster is size S, resume.stage not-started, with after-groups R10-UPDATE-PR-SIGNALS, R10-FLOW-BODY-PATCH and R10-FLY-OPENPR-ATOMIC. The roster's next_step reads "DISPATCH NOW", and the group's carry contains P233, handoff-body-stale and the Code: trailer text.
- The reasoning that rejects the timestamp variant holds. Clock skew and a re-body of an unchanged head are both real, and an identity trailer needs neither.
- Instance figures for #3016, #2890, #2891 and #2894 are the orchestrator's account and P233's recorded instances. I did not re-derive the #3016 sha and count figures (460e4b76, af5caa138, 11 unpinned sites, 5 reds), which are outside the tree. The packet's figure_lint reports 1 resolved and 3 not verified, with 0 refused.
- The ruling quotes P233's date as "since 2026-10-28" while the roster's next_step says "since 2026-10-27". That is a one-day wording mismatch between a ruling date and a next_step date, and it changes no conclusion.
- Merge: `git merge-tree --write-tree origin/main 12d32a204c923e768f6146a510445374c23f548c` exits 0 with no conflict (ev/merge-tree.txt).
- carry_audit at the head reports 0 finding items, 0 unrouted, 0 bad destinations.
- CI at this head: merge_train.py classify exits 0 (GREEN, pending none, red none). The gate, pr-contract, budget-raise-gate, arch-score, mutation, delivery-status and instrument-self-tests all concluded success. No gate check went red, so the red-check answer rule of fix-review.md step 11 has nothing to answer.
- A record PR changes no VERSION, manifest version or notes heading (step 5); the three-dot diff touches only the two files above. It moves no budget, closure, golden or claim file (step 14), and the mutation-ledger diff is none.
- The carry text is the ruling's own, for a later roster append. The PR itself writes no roster, which fits a record PR. The carry names the null control (a Code: naming the current head updates).
