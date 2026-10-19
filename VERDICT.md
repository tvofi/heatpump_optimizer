Fix review: merge 328813ad5fb2055a07a4867c33f7cfc96d961168

bus-nonce: cb60f35e59a9e8d79d6f40191eb086b4

Round 1: PR #2420 has no earlier `Fix review:` comment (ev/comments.tsv is empty).
Contract: dev/governance/roles/fix-review.md from origin/main fa5026c42. `git diff merge-base...origin/main -- dev/governance/roles/` is empty, so the copy is current.

RESULT head-measured=328813ad5fb2055a07a4867c33f7cfc96d961168 (PR head when the verdict was written: ev/head_at_post.txt)
RESULT merge-tree origin/main(fa5026c42) vs head: exit 0, tree cd9334246. origin/main is an ancestor of the head, so the head tree is the merged tree.
RESULT diff-scope: 11 files, all dev/programme/delivery/<N>.md (10 rewritten, 1 new: 2420.md). No other file changed. VERSION, manifest and notes are untouched (ev/diff.txt).
RESULT rows-vs-API: 10 of 10 merged rows match. Each PR has state=closed and merged=true, and its merge_commit_sha starts with the short SHA in its row: 2379 5756f2b, 2394 3d46d69, 2396 106af95, 2401 07a0940, 2407 3126b86, 2412 003c373, 2413 be2d367, 2416 fd64a23, 2418 86010e8, 2423 89e3385. Every one of those SHAs is an ancestor of origin/main. Row subjects match the API titles. The #2420 row reads open, which matches the API (ev/prs.tsv, ev/on_main.txt).
RESULT delivery_status.py --check at head (== merged with origin/main): exit 0, "136 rowed, 1 pending, 0 overdue" (ev/delivery_status_check.txt)
RESULT null control: setting the #2413 row back to its pre-PR "open" text makes the check fail with "1 overdue #2413", exit 1. The repair is what clears the OVERDUE, and the check can see a missing repair (ev/null_control_2413_open.txt).
RESULT record_row.py --pr 2420 --automerge-check: "AUTOMERGE OK #2420", exit 0 (ev/automerge_check.txt)
RESULT policy_lint.mjs --record --since v7.0.0: 0 errors over 137 merged PRs, exit 0 (ev/policy_lint_record.txt)
RESULT CI at head (check-runs API, every run, not one per name): all completed. None failed. Each one either succeeded or was skipped by its trigger conditions (ev/checks.tsv). Both pr-contract runs succeeded.

DEVIATION FROM DISPATCH — read this before routing.
The dispatch asks for "0 overdue and 0 pending". The measured result is 0 overdue and 1 pending. The pending row is #2424 (fa5026c, 0 commits since). #2424 merged at 00:14:52Z, and the orchestrator's script merged origin/main into this head 32 s later. It is the newest merge on main. No row commit in this PR was computed after it, and the body does not claim it. delivery-status-tracking.md treats pending as the ordinary state between record beats, and fix-review.md does not make 0 pending a blocking criterion. So I do not block on it. The next record beat should row #2424. If the orchestrator holds the 0-pending bar as a hard requirement, treat this verdict as blocked: "record: #2424 pending".

Red checks on earlier heads (step 11): the body names and answers both of them. delivery-status OVERDUE (#2407, #2412, #2413 open rows) is fixed here, and the null control above confirms that. wave-script merge-subject-pr was fixed on main by #2423. I checked that the trigger was answered, not the answer itself.
Mutation proof: n/a. The diff is record-only and writes no production line. The null control above stands in for it at the instrument.
Figures in the body: "--check prints OK, 0 overdue" is confirmed at this head. The body quotes no other number.
Head section: it names 328813ad5, which is the head I measured.
Identity: the two merge commits at the head (9c5157077, 328813ad5) have the git author tvofi. The body says they come from "an automatic merge by the orchestrator's script". The row content comes from hpo-author[bot] commits plus c76799c54. pr-contract passed, and that is the check that enforces authorship. I note it and do not block on it.
Head stability: PR head and origin/main (fa5026c42) were unchanged when this verdict was written.
