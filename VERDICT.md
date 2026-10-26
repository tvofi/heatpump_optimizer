Fix review: merge 9deee69ad12ff84e117b806137e234c5df3bf83d

bus-nonce: 2cd60e59bf0218c7843fca6e6d056e11

Round 1. Record-shaped review of #2857 (roster batch 19). I measured head 9deee69ad12ff84e117b806137e234c5df3bf83d from a detached worktree. refs/pull/2857/head re-read just before writing: unchanged. origin/main is 5fb8339304e10b2b1416d9c439587ae1806d820e (#2851, batch 18, merged), so the three-dot diff is exactly this batch's ten ops plus the row. Roles are current: `git diff merge-base...origin/main -- dev/governance/roles/` is empty.

## Findings

- Op 8c918fd2b (append-carry R10-REPLAY-REAL-DAY) cites neither a merged ruling nor a merged PR. Its text says "From R10-HEAT-METER (#2261; D15 lead L9 ...)". #2261 is the issue. The text is verbatim the third `## Forward-carry` item of #2854 (R10-HEAT-METER), which is still open and draft. Routing it before the producer merges is the order finding-propagation.md prescribes, so this does not block. But the carry says "Each weekly learner snapshot now records `unhealthy_input`", and that is true only after #2854 merges: `git grep unhealthy_input origin/main` outside the rosters is empty. R10-REPLAY-REAL-DAY's `after` (R10-REPLAY-SCOPED, R10-DIAG-REDACT) does not include R10-HEAT-METER. Owed: give the carry the precondition "after #2854 merges" (or add the after-edge), and name #2854 as its source. Carry: R10-REPLAY-REAL-DAY | #2272 | O1 | dismissed: none, precondition owed on the roster
- R10-HOTFIX-BATCH-ERREXIT was set to done (63b1cfd03) while its one carry was still on it. That breaks the done-before-reroute order: finding-propagation.md says a done group "is not a destination". The body discloses this and schedules the drop as batch 20's first op. The carry is the group's own defect statement, and #2848 landed it: e0ffb1213 is an ancestor of main, and nightly.yml:751 reads `--batch-due ... || batch=$?`. So nothing actionable is stranded. The drop is still a task owed after this merge. Carry: R10-ROSTER | #201 | O2 | dismissed: none, owed as batch 20's first op
- One body figure does not reproduce. The body says brief_lint prints `TOTAL: 10 error(s) across 48 file(s)` on both origin/main and the merged tree. Run in git worktrees of origin/main and of the merged tree (0ede8f0cd), it prints `TOTAL: 0 error(s) across 48 file(s)` on both, exit 0, with output byte-identical. The body ran it on git-archive extracts with a fresh init, which is a different setup I did not reproduce. The delta is zero either way, and that is what the check requires. Carry: R10-ROSTER | #201 | O3 | dismissed: delta zero under both methods; the extract-method count is the seat's instrument, not the roster's

## Evidence

- Ops: the ten commits listed in the body, all present in merge-base..head. The PR changes two files: wave-r10-groups.json (+7/-12) and the new delivery/2857.md (ev/diff-stat.txt). The delivery row is in the three-dot diff. VERSION, manifest.json, RELEASE_NOTES.md, claimed_drift.txt and card_claimed_drift.txt are untouched: 0 paths (ev/untouched-count.txt).
- set-stage done: #2825's merge ed1c9045e140b14e6a98fdb642942b6fa39aca71 and #2848's merge e0ffb12130436f1cef00e770aed436ac8b4f067e are both ancestors of origin/main (`git merge-base --is-ancestor`). The set-stage commit messages cite no PR. The body cites #2825 review 6407989264 and #2848 for them, and the refs confirm both merges.
- The six drops on R10-UPDATE-PR-SIGNALS, each checked at main against #2825 (ev/landed-at-main.txt):
  - carry 1: pr_args.sh pr_push_hold/flock holder, the holder ignoring TERM/INT/HUP, and "no other stop exits 75".
  - carry 2: superseded by the flock design, because a kernel lock frees itself on death. The self-test bound pr_bounded landed too.
  - carry 3: update_pr.sh `pr_branch_lock ... detach` landed, citing #2513/#2544/#2547. The open_pr half is on R10-FLY-OPENPR-ATOMIC (not-started, P-D carry present).
  - carry 4: re-routed verbatim to R10-FLOW-JIDOKA. Exact-string match, count 1, no prior copy.
  - carry 5: pr_own_group/setpgid in cloud_relay.sh, with self-tests for TERM and KILL to the group.
  - carry 6: cloud_relay.sh STUCK andon on HPO_PUSH_STUCK_SECS, default 900.
  Each drop was made before c6f5863fd set the stage.
- R10-REPLAY-REAL-DAY: the appended carry is not a duplicate of its three existing carries (#2514 x2 and #2810). The same lead appears as R10-HEAT-METER's carry 13, the verification request on the producing group, which is a different stage.
- Group count: 197 at origin/main and 197 at the head, none added or removed. R10-UPDATE-PR-SIGNALS: carry 6 -> 0, stage done. R10-HOTFIX-BATCH-ERREXIT: stage done, carry 1. JSON loads.
- `python3 -I tools/audit/carry_audit.py pr 2857`: `0 routed, 0 unrouted, 0 bad destination(s)`, exit 0 (ev/carry_audit.txt).
- brief_lint (the roster lint gate roster_edit.py uses), merged tree and origin/main: `TOTAL: 0 error(s) across 48 file(s)`, exit 0 on both (ev/brief_lint_*.txt).
- `git merge-tree --write-tree origin/main 9deee69ad` prints tree 0ede8f0cd4715bcd97843dc59dd59e77ab842c37 and exits 0, with no conflict and no MERGE-CLAIM line (ev/merge-tree.txt).
- CI on this head (check-runs API, 55 runs): no red. Every run is success or skipped, including gate (x2), pr-contract (x2), tests / closures, fast (3.14), mutation, briefs, governance / delivery-status, instrument-self-tests and env-matrix. No red check, so no root-cause trigger.
- Not applicable to a roster-only diff: mutation proof, finder's harness and class enumeration. No production or test code changed.
