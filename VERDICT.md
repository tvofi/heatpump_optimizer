Fix review: blocked db9badf4cca06967539de272c8f038460671ce53 body-claim-wrong: title and body credit this PR with a P98 re-cut on R10-FLOW-ROSTER-FREEZE and a P97 re-cut on R10-ORCH-BEATD that no commit in it makes; both entries are already on origin/main

bus-nonce: 572df1bb9c26ee0b6e627738d71b4660

## Block

The body's opening paragraph lists "two carries on R10-FLOW-ROSTER-FREEZE (the P98 text re-cut and the #2792 review's mutant R1), two on R10-ORCH-BEATD (P97 re-cut and the arm (a) retirement note)". The title, which becomes the merge subject, says "ORCH-BEATD P97 and arm (a) carries". That is five carries plus a set-after, but the same body says four ops, and its Figures section lists four. The three-dot diff and a replay of each commit show only one carry appended per group. The P98 entry on R10-FLOW-ROSTER-FREEZE and the P97 entry on R10-ORCH-BEATD are byte-identical at the merge base and at origin/main. Their only line change in the diff is a trailing comma, which the JSON append adds. They were added by 9a019e994 and afeb76c02, which are both ancestors of origin/main. So two of the described ops are not reproduced by any stated commit. A later seat reading the merge subject would think P97 was carried by #2797.

Fix (body and title only, no roster change): drop "P98 text re-cut" and "P97 re-cut". Describe the ops as the set-after adding R10-UPDATE-PR-SIGNALS to R10-FLOW-ROSTER-FREEZE, one carry on R10-FLOW-ROSTER-FREEZE (the #2792 review's mutant R1), one on R10-ORCH-BEATD (the arm (a) standing-roster retirement note) and one on R10-MERGE-SUBJECT-CASEARM (the #2697 r8 verdict). Change the title to match. A body/title-only edit leaves the reviewed head unchanged, so the roster checks below still hold at it.

## Findings

- The new R10-ORCH-BEATD carry (e78d7dedd) says "this group merges after ROSTER-FREEZE, so its contract edit owns the standing roster seat's retirement". At this head, R10-ORCH-BEATD's after-edges are R10-ORCH-DISPATCH-REG, R10-POLICY-FIXER-MD and R10-ORCH-REVIEW-PACKET. Neither group names the other, and both are not-started, so nothing enforces the order. R10-FLOW-ROSTER-FREEZE's carry 3 assigns the edit to "whichever merges later, not both". If ROSTER-FREEZE lands second, both groups or neither may make the edit to dev/governance/roles/standing-roster.md. Either add the edge with `roster_edit.py set-after R10-ORCH-BEATD ...,R10-FLOW-ROSTER-FREEZE`, or have BEATD's fixer confirm ROSTER-FREEZE is merged as a precondition before taking the edit. Carry: R10-ORCH-BEATD

## Evidence

- Head reviewed: db9badf4cca06967539de272c8f038460671ce53 (ev/HEAD.txt). The PR head is still db9badf4cca06967539de272c8f038460671ce53. The PR base is 102f74975, which is the merge base and the current origin/main.
- Round 1 review of this PR.
- Roles current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Paths (three-dot, ev/paths.txt): only dev/programme/delivery/2797.md and dev/programme/rosters/wave-r10-groups.json change. Neither is a policy file under CLAUDE.md's index. Neither is code-owned: CODEOWNERS names tests/delivery_status.py, not the row. VERSION, the manifest and RELEASE_NOTES.md are untouched.
- Op replay (ev/replay.txt): I applied each commit's subject op through roster_edit.apply_op to its parent's roster and dumped the result with roster_edit.dump. All four, 461550d9a set-after, c6097875c, e78d7dedd and f57b6d52e append-carry, reproduce their commit's file byte-for-byte. Each changes only the named group and the named field. Each append keeps the prior carry list as a prefix, and each file round-trips through dump unchanged, which shows canonical indent=1 bytes.
- The head roster blob equals f57b6d52e's. The merge 6f64a9923 changes the roster by nothing relative to f57b6d52e. Main's roster equals the merge base's and 4a18b96b1's, which confirms the body's null control.
- JSON is valid. Group order (189 groups), top-level key order and per-group key order are identical between the merge base and the head (ev/order.txt).
- brief_lint from a fresh origin/main worktree (tools/policy/brief_lint.mjs) on the head roster prints `TOTAL: 0 error(s) across 1 file(s)`, as main's does (ev/brief_lint_head.txt, ev/brief_lint_main.txt).
- Body figures re-derived (ev/figures.txt): 189 then 189 groups, none removed or new. Three changed: R10-FLOW-ROSTER-FREEZE, R10-ORCH-BEATD and R10-MERGE-SUBJECT-CASEARM. The stage counts match the body exactly (done 115, in-progress 12, not-started 50, queued 6, carries-open 5, absorbed 1, at both ends). The CASEARM carry has n_carry=1 and length 469. The ops log in ev/ops_log.txt matches the body.
- Merge with origin/main: `git merge-tree --write-tree` exits 0 with no conflict (ev/merge_tree.txt).
- CI on the head (ev/ci.txt): every check run concluded success or skipped, with no red check, so the red-check trigger does not apply. pr-contract is green on both runs.
- Mutation proof is n/a: the diff writes no production or test line, so no mutant is drawn. There is no harness, null control or claim-file drift to re-measure. The head's diff touches neither claim file.
