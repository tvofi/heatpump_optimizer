Fix review: merge 76e2224896fb04cf3481252de9728fa8f24cecdc

bus-nonce: 456ef1db5ac51791a99505aea55e49bc
pending-ci: gate

Round 3 of #3821, re-fired at the same head. Cloud reviewer seat, Linux. The previous fire at this head (probe/rev-3821-958c415e, aa78dc91be) returned `merge` with `pending-ci: gate`. The head has not moved since then, so its review stands. This fire re-checks the merge against the current main, re-runs the card suite and waits on CI again.

## Findings

none

## Evidence

- Head: `git ls-remote origin refs/pull/3821/head` still reads 76e2224896fb04cf3481252de9728fa8f24cecdc (ev/head_reread.txt). The delta review over ef157f1551 is unchanged: it is one main-merge commit, and it touches only comment lines in `tests/card.mjs`. See the previous verdict's `## Evidence`.
- Merge: origin/main has moved to 4ebd430fbf, which includes the v10.1.2 stamp. `git merge-tree --write-tree origin/main 76e2224896` exits 0 (ev/merge_tree.txt). The claimnotes driver prints `MERGE-CLAIM: resolved tests/golden/card_claimed_drift.txt` and the ledger driver prints `LEDGER-MERGE: resolved tests/closures.json`. The head is behind main but merges cleanly, so it is not blocked.
- Claims: the head's `card_claimed_drift.txt` reads `claims-for: 10.1.1`. That matched `VERSION` at the head's base. Main now reads 10.1.2, so a merge inherits the claim, and the merge driver resolves it as shown above. The train re-proves the merge on current main.
- Versions: the three-dot diff leaves `VERSION`, `manifest.json` and `RELEASE_NOTES.md` untouched (ev/version_untouched.txt is empty).
- Card suite: in a detached worktree at the head, `node tests/card.mjs` (run after `tests/plan_view.py`) reads ALL CARD CHECKS PASSED, rc 0, with 1467 `ok` lines (ev/card_mjs_head.log). That matches both earlier rounds.
- Review packet at the head: no refusals. The `required-wait` advisory reports an earlier concluded `gate` failure, but classify reads WAIT, and classify decides. carry_audit reads 1 routed, 0 unrouted. figure_lint reads 22 resolved, 6 not verified, 0 refused.
- CI: `merge_train.py classify 76e2224896 --pr 3821` was polled from 23:59Z to 00:30Z, 29 reads at least 60 s apart. Every read was `WAIT 76e2224896fb04cf3481252de9728fa8f24cecdc pending: gate red: none` (ev/classify_poll.log), so this verdict carries `pending-ci: gate`. There is no red, so no `## Red checks` answer is owed (owed-reds set in ev/owed_reds.txt).
