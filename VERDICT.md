Fix review: merge 6e398dd29efff5486aef0428f63b7c451271deaf

bus-nonce: 1ca78be7a2a7a0c3d39aed402a1c2a41

Round 1. Record PR: reviewed from a detached worktree at the head.

## Findings

- The carry's mutant is weaker than stated. It says a mutant trying (iii) before (i) "resolves r10-roster-ops-2 to R10-ROSTER-OPS and fails its row". But a stripped match opens only when the body names the group as a whole name, and that body names R10-ROSTER-OPS-2, not R10-ROSTER-OPS. So the (iii)-first mutant fails the body check and falls through to (i), and the row still passes. The fixer must build the mutant as dropping the body check, or add a row whose body names both groups. Carry: R10-OPENER-REUSE
- The file says r10-roster-ops-2-p1 "resolves at (ii) to R10-ROSTER-OPS-2, which its first line names". Its own text also says that first line begins "Adds the roster's two missing field-writing ops", and no handoff body is in the tree. The claim that the first three lines name the group is not re-derivable here, and the fixer should assert it on a real body. Carry: R10-OPENER-REUSE
- Naming nit: the file heading says "session s10" while the PR title and delivery row say "s9 batch 106". Not blocking. Carry: dismissed: label only, no consumer reads it

## Evidence

- Three-dot diff changes exactly dev/programme/delivery/3146.md and dev/programme/triage/s6-batch106.md (121 insertions). There is no change to VERSION, manifest, RELEASE_NOTES, claim files or goldens, and no host path in the added lines.
- Facts re-derived at origin/main and at the roster (origin/handoff/audit-r10-roster, which is now 6b279e3b5, not 41268f418; the checked figures are identical at both). Five suffix-named groups exist (R10-STALE-PATHS-2, R10-CI-LAYOUT-P1, R10-CI-LAYOUT-P2, R10-ROSTER-OPS-2, R10-TICK-DRIVERS-2). R10-OPENER-REUSE is not-started with no after, has 6 carries and owns open_pr.sh. R10-FLY-OPENPR-ATOMIC is done at 437f1ba9b, with P337 and P350 as carries 9 and 10, each matching a 100-character slice on that group only. R10-FLY-STANDING-CONTRACTS carry 6 is the P103 re-route. #2989 merged on 2026-10-30 and batch 96 was ruled on 2026-10-31. R10-PREPR-CAP exists and R10-PREPR-CAP-2 does not.
- Session-local opener log counts (69 RESULT lines, 7 NEEDS-TITLE lines, the 14-minute wait) and the ledger and title-override file are not in the tree, so I could not re-derive them.
- The body's mutation proof and null control (`triage_refusal`, `op_append_carry` 6 to 9) were not re-run by me.
- PR body: ## Head names the head. ## Red checks says none, and the concluded set at this head has no red.
- merge-tree with origin/main exits 0 (clean).
- CI: merge_train classify returns GREEN, pending none, red none (ev/classify.txt).
- The packet's carry_audit and figure_lint are clean.
- The delivery row is present and follows the format of the other rows.
