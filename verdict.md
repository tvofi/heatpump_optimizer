Fix review: merge 76e2224896fb04cf3481252de9728fa8f24cecdc

bus-nonce: 958c415e8063637d454c51b3f23bcadf
pending-ci: gate

Round 3 of #3821. Cloud reviewer seat, Linux. Review scope: delta over the reviewed head ef157f1551c0ec3981ad4286fd81f00ab00d3796, whose verdict was `merge` with no findings (fix-review.md step 12).

## Findings

none

## Evidence

- The delta is one commit, 76e2224896 (`Merge remote-tracking branch 'origin/main' into HEAD`), with parents ef157f1551 and 63c6d1cff9 (origin/main at review). `review_carry.py ef157f1551 76e2224896` prints `FRESH-REVIEW`: the head is not the automatic merge of its parents. `git merge-tree --write-tree ef157f1551 63c6d1cff9` reports a conflict in `tests/card.mjs` alone; `tests/closures.json` reads `LEDGER-MERGE: resolved`.
- The hand resolution, read as `git diff <automatic merge tree bec68ca3af> 76e2224896`: one hunk in `tests/card.mjs` (+1/-13). It keeps the branch's status-colour comment above the D4-s1-01 / P9-rca1 / D4-s3-04 check, changes its `etc:` to `etc.` (main's sentence split), and drops main's older text of the same comment. Comment lines only; no code line changes. This matches the body's `## Head`.
- The PR's own diff is unchanged apart from that comment. `git diff 86859b9594...ef157f1551` and `git diff 63c6d1cff9...76e2224896` both read 23 files, +947/-276. With `index` and `@@` lines stripped, they differ in three comment lines of `tests/card.mjs`. The one production file, `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`, is byte-identical in both diffs. Because the delta changes no production code, the review is not widened.
- `node tests/card.mjs` at 76e2224896, in a detached worktree, after `PYTHONPATH=tests/hastub python3 tests/plan_view.py`, reads ALL CARD CHECKS PASSED, 1467 `ok` lines, rc 0 (ev/card_mjs_head.log). That is the same count as at ef157f1551.
- Round 2's mutants and the finder harness figures are not re-run, because the card file did not change. They stand as recorded in the previous verdict.
- Merge: origin/main is 63c6d1cff9, the head's second parent. `git merge-tree --write-tree origin/main 76e2224896` exits 0 (ev/merge_tree.txt). `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Versions and claims: the three-dot diff leaves `VERSION`, `manifest.json` and `RELEASE_NOTES.md` untouched (ev/version_untouched.txt is empty). `tests/golden/card_claimed_drift.txt` reads `claims-for: 10.1.1`, which equals `VERSION`. `tests/golden/claimed_drift.txt` is untouched.
- Body: `## Head` names 76e2224896fb04cf3481252de9728fa8f24cecdc, which is the head reviewed. The packet's figure_lint reads 22 resolved, 6 not verified (`$EXPORT` templates), 0 refused. Carry: `## Forward-carry` and `## Friction` read none, and the D4-s1-01 residual carries a valid `dismissed:` (packet carry_audit: 1 routed, 0 unrouted).
- CI at this head: `merge_train.py classify 76e2224896 --pr 3821` was polled from 19:27Z to 20:01Z, 29 reads at least 60 s apart. Every read was `WAIT 76e2224896fb04cf3481252de9728fa8f24cecdc pending: gate red: none` (ev/classify_poll.log), so this verdict carries `pending-ci: gate`. There is no red at this head, so no `## Red checks` answer is owed. Prior rounds' owed reds are answered under the body's `## Red checks`.
- The final re-read by `git ls-remote` shows the branch tip still at 76e2224896fb04cf3481252de9728fa8f24cecdc (ev/head_reread.txt).
