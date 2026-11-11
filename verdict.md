Fix review: blocked 9647bc111d7e57b2928ca887ed1f6724a873b44e body-stale: Forward-carry reverted to superseded R10-REVIEW-DISPATCH-RESIDUE without its control; code and mutation proof are sound

bus-nonce: 0b5b9f378214405da7ab89a471bb081c

This is round 3, the second repair round. It is a handoff review with no pull request at this tip. I measured the handoff tip 9647bc111d7e57b2928ca887ed1f6724a873b44e (base cbd23f1c8bf6185c3a6c10f6e4aaf562417e75bf) from a detached worktree.

The delta against the reviewed head befd1f54144062002c51c88c0c181eccdd37c00c is one commit that adds seven lines to the self-test of `tools/audit/seat/cloud_relay.sh`. It is a test delta only, so it widens nothing (step 12). `review_carry.py befd1f54 9647bc11` prints FRESH-REVIEW (`ev/review-carry.txt`).

The round-2 mutation-vacuous finding is resolved. m7 and m8 are now killed, and every mutant of the full set is killed (Evidence). The body is the one thing that still blocks.

## Block

- body-stale. BODY.md at `refs/heads/handoff-body/r10-relay-arm-order` (147609f47, `ev/body-handoff-body-147609f4.md`) was not re-taken whole. Its Head and Mutation proof sections are current, but its `## Forward-carry` has reverted to the round-1 line: "Carry 1 (OPENER-LIVE-TIP, tools/audit/seat/open_driver.py): not built here ... Carry: R10-REVIEW-DISPATCH-RESIDUE". That is the destination the round-1 verdict blocked as carry-missing. The roster now marks that carry superseded:
  - R10-REVIEW-DISPATCH-RESIDUE carry 27 is tagged `[moved: R10-SEAT-IDENTITY-P5]`.
  - R10-SEAT-IDENTITY-P5 carry 6 "supersedes R10-REVIEW-DISPATCH-RESIDUE carry 27 ..., which dropped the control" (`ev/carry-destination.txt`, roster `origin/handoff/audit-r10-roster`).

  The line in this body states no control (no self-test, mutation proof, null control or measurement). If folded, it would add a second control-less P603 item to the wrong group. The roster already holds the correct destination with its control: R10-SEAT-IDENTITY-P5 carries 6 and 7. So the fix is to the body only. Restore the forward-carry from the previous body (`ev/body-refused-handoff-wip-cb33f120.md`, refused at handoff-wip cb33f120): "Carry 1 (P603 OPENER-LIVE-TIP, ...). Carry: R10-SEAT-IDENTITY-P5. Control to keep with it: self-test (board line at A, live clean tip B opens at B), mutation proof (restoring the skip fails it), null control (handoff ref gone still prints SKIP moved), measurement (18 SKIP moved lines)." Then re-run `body_push.sh`. No code change is owed, and the code at this tip needs no re-review for a body-only push.

## Findings

- Follow-up: the body's mutant labels collide with the previous verdict's. The body's "m9 original order" is that verdict's m1, and its m9 was the lone-handoff_arm fallback. The body also says "m1-m6 ... I did not re-run it this round". I re-ran them; all are killed (Evidence), so nothing is owed for the code. When re-taking the body, number the mutants to match the verdict, or say which scheme is used. Carry: dismissed: body wording only; settled by the same body re-take this block requires.

## Evidence

- No review packet and no CI. No pull request exists at this tip, so there are no check runs and no red to answer. PR #3465 has not taken this tip. The owed-reds set is in `ev/owed-reds.txt`. Main's two reds, `tests / fast (3.14)` and `governance / instrument-self-tests`, are not this tip's.
- RESULT head self-test: `bash tools/audit/seat/cloud_relay.sh --self-test` rc 0, "424 checks, 0 failed" (`ev/selftest-head.log`). This matches the body's 424.
- Mutant drive. Each mutant ran in its own detached worktree at the tip with exactly one change, then the full self-test (`ev/mutant-<id>.diff`, `ev/RESULT-mutant-<id>.txt`, `ev/selftest-mutant-<id>.log`, `ev/drive.log`). Mutants m1 to m9 use the previous verdict's numbering, and its m2 to m6 and m9 diffs were re-applied at this tip.
  - RESULT m1, old order (handoff, carry_fold, probe, confirm): KILLED, rc 1, 3 failed. The body's "m9" reports 3, which matches.
  - RESULT m2, the `open_prs` listing line deleted: KILLED, rc 1, 1 failed.
  - RESULT m3, `handoff_arm` always lists: KILLED, rc 1, 1 failed.
  - RESULT m4, `confirm_arm` always lists: KILLED, rc 1, 1 failed.
  - RESULT m5, the listing `rm -f` dropped: KILLED, rc 1, 2 failed.
  - RESULT m6, a failed listing leaves the file (`|| true`): KILLED, rc 1, 1 failed.
  - RESULT m7, `carry_fold_arm` first: KILLED, rc 1, 2 failed. The failing checks are `pass --confirm runs the arms probe, confirm, handoff, carry_fold, stuck, noreturn in that order` and its no-`--confirm` null control. The body reports 2, which matches. Round 2's survivor is now fixed.
  - RESULT m8, `confirm_arm` after `handoff_arm`: KILLED, rc 1, 1 failed (the order check). The body reports 1, which matches. Round 2's survivor is now fixed.
  - RESULT m9, the lone `handoff_arm` fallback lists nothing: KILLED, rc 1, 90 failed.
  - RESULT m10, `confirm_arm` first: KILLED, rc 1, 5 failed. Matches the body.
  - RESULT m11, `carry_fold_arm` before `handoff_arm`: KILLED, rc 1, 2 failed. Matches the body.
  - RESULT m12, `confirm_arm` dropped: KILLED, rc 1, 9 failed. Matches the body.
  - RESULT m13, `carry_fold_arm` dropped: KILLED, rc 1, 2 failed. Matches the body.
  - RESULT m14, `handoff_arm` dropped (mine): KILLED, rc 1, 10 failed.
  - RESULT m15, `probe_arm` dropped (mine): KILLED, rc 1, 15 failed.
  - RESULT m16, `stuck_arm` and `noreturn_arm` swapped (mine): KILLED, rc 1, 2 failed.
  - RESULT m17, `stuck_arm` and `noreturn_arm` moved ahead of `probe_arm` (mine): KILLED, rc 1, 2 failed.
  - Survivors: none of m1 to m17.
- Null control. The new order check's own control is green at the tip and red under m7, so it reads the order: without `--confirm`, the same order holds with `confirm_arm` absent. The other controls named in the body are all green at the tip:
  - a second pass with no new probe ref posts nothing more;
  - `handoff_arm` runs once per pass;
  - no listing file is left behind;
  - the counting lister runs once per pass.
- Finder's harness: the s6-batch182 probe-to-POSTED latency measurement has no committed harness, as rounds 1 and 2 recorded. I did not re-run it at either end. The self-test arms are the fixer's instruments.
- Class rule: the issue states one seam, the arm order in `pass()`, and the body names no enumeration rule. This is a one-seam class, and every slot of the arm line is now pinned (m7, m8, m10 to m17).
- Body figures:
  - 424 checks: re-derived.
  - Per-mutant fail counts: re-derived; all match.
  - Head line: names 9647bc111d7e57b2928ca887ed1f6724a873b44e, which is the tip measured here (step 7).
  - "`PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh` rc=0": not re-derived by me.
- Merge with main: `git merge-tree --write-tree origin/main <tip>` rc 0, origin/main 0e28afd38b (`ev/merge-tree.txt`).
- The diff against the merge base touches only `cloud_relay.sh` and its instrument doc (`ev/diffstat.txt`). VERSION, the manifest, RELEASE_NOTES and both claim files are untouched. `tests/structure.py`: STRUCTURE RATCHET PASSED (`ev/structure-head.txt`).
- The tip I measured is `ev/HEAD.txt`. It was still `refs/heads/handoff/r10-relay-arm-order` when I wrote this verdict.
