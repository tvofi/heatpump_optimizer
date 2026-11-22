Fix review: merge eb1df490312d4f574bc262e87c5fdd485f586ed5

bus-nonce: 2a2ca7a936ea9c897f1e59d47b7a7ce4

Round 4 of #3821. This is a delta review (fix-review.md step 12) over the last `merge` verdict at 76e2224896 (probe/rev-3821-456ef1db, 3d797c3269). Cloud reviewer seat, Linux. `review_carry.py 76e2224896 eb1df49031` prints `FRESH-REVIEW` because the branch's own commit 068fd74a33 changes content (ev/review_carry.txt). This is the fourth round, so by fix-review.md a re-cut is owed only if this round does not merge.

## Findings

- Note: stale-figure: the body's `## Figures` still says `claims-for: 10.1.1`, equal to `VERSION`. The tree now reads 10.1.2 on both sides, so the claim is consistent; only the body's figure is stale. Paperwork, no block. Carry: dismissed: the body figure is superseded by the tree at merge, and env_drift checks the live claim line

## Evidence

- Head: `git ls-remote origin refs/pull/3821/head` reads eb1df490312d4f574bc262e87c5fdd485f586ed5 (ev/head_reread.txt). The PR body's `## Head` names that SHA and its authored code head 068fd74a33.
- Delta: 76e2224896..eb1df49031 is one merge of main (68c2ee613c, onto f269ecccb5), one authored commit (068fd74a33) and the merge of that commit. The three-dot own diff is 23 files, +947/-276, at both heads. Diffing the two own diffs (ev/own_diff_delta.txt) shows only index hashes, hunk offsets, the `CARD_VERSION` context line (10.1.1 to 10.1.2, main's stamp, not a line the branch writes), and one comment sentence in `tests/card.mjs` (the HistorySource bound block) split in two. No production (`custom_components/`) line moved, so the review is not widened. Round 1's and round 2's mutation and harness results stand.
- The delta is earned: `python3 tests/comment_ratchet.py --base origin/main` at the head reads `long_units_base=2301 long_units_head=2300`, `comment_ratchet: OK`, rc 0 (ev/comment_ratchet_head.log). Restoring the old sentence on the head's tree reads `REFUSE tests/card.mjs: long units 0 -> 1`, `comment_ratchet: FAIL`, rc 1 (ev/comment_ratchet_reverted.log). That is the red the body's `## Red checks` answers for run 44940315955.
- Suites at the head, in a detached worktree: `PYTHONPATH=tests/hastub python3 tests/plan_view.py` rc 0; `node tests/card.mjs` ALL CARD CHECKS PASSED, 1467 ok lines, 0 FAIL, rc 0 (ev/card_mjs_head.log), the same count as rounds 2 and 3; `tests/doc_claims.py` ALL 441 checks PASSED, rc 0 (ev/doc_claims_head.log), matching the body's figure.
- Merge: `git merge-tree --write-tree origin/main eb1df49031` against origin/main 35c3e31cc9 exits 0, so there is no conflict (ev/merge_tree.txt).
- Claims and versions: at the head, `tests/golden/card_claimed_drift.txt` and `tests/golden/claimed_drift.txt` both read `claims-for: 10.1.2`, equal to `VERSION` 10.1.2. The three-dot diff leaves `VERSION`, `manifest.json` and `RELEASE_NOTES.md` untouched (ev/version_untouched.txt is empty).
- Review packet at the head: no refusals, no advisories. carry_audit reads 1 routed, 0 unrouted (the pipe-target residual's `dismissed:`). figure_lint reads 22 resolved, 6 not verified, 0 refused.
- Role contract: rendered by `role_pack.py` from origin/main 35c3e31cc9, the current main.
- CI: `merge_train.py classify eb1df49031 --pr 3821` was polled from 04:39Z, at least 60 s between reads. It read `WAIT ... pending: gate red: none` until 05:30:13Z, when it read `GREEN eb1df490312d4f574bc262e87c5fdd485f586ed5 pending: none red: none`, rc 0 (ev/classify_poll.log). There is no red at this head, so no `## Red checks` answer is owed (owed-reds set in ev/owed_reds.txt). The earlier owed reds at 76e2224896 (`tests / fast (3.14)`, `gate`) are answered in the body's `## Red checks`, and the comment-ratchet re-run above confirms the fast red's repair.
- Head re-read after GREEN: still eb1df490312d4f574bc262e87c5fdd485f586ed5.
- Self-audit: `carry_audit.py check` on this verdict exits rc 0 (ev/carry_audit_verdict.txt). The body's items were audited by the packet at the head.
