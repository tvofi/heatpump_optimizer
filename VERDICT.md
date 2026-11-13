Fix review: merge 0e60a6f9a681992f4f983ee79dce2fa2d980c4d5

bus-nonce: 4300f7a1c2b619e6b73e4e22237c4700
pending-ci: gate

## Scope

Resolution delta, round 6, counting the body's rounds 1 to 5. The previous verdict was `merge` at eda078bac41473246ff7d87a5736de58d64ad97a and recorded no findings. This review covers only the delta from eda078ba to 0e60a6f9 (fix-review.md step 12). The delta is two merges:
- a72f090b5: tree-identical to b09b5f9c, which is hpo-fixer's merge of origin/main 4145f285 into eda078ba. It has one hand-resolved conflict, in tests/card_browser.mjs.
- 0e60a6f9: merges origin/main f44e761c (the v7.1.13 stamp). Its tree is identical to git's automatic merge of its parents.

The delta writes no production line by hand, so the review does not widen.

## Evidence

- Branch patch unchanged: `git diff cbe8d93b eda078ba` (the reviewed head against its merge base) and `git diff f44e761c 0e60a6f9` (this head against its merge base) touch the same 16 files, 573+/68- each. The sequences of added and removed lines are identical in all 16 files (ev/patch-compare.txt), and all six PNG blobs are identical at both heads. So this head is main at f44e761c plus exactly the patch already reviewed.
- Conflict reconstructed: `git merge-tree --write-tree eda078ba 4145f285` gives rc 1, a content conflict in tests/card_browser.mjs only (ev/resolution.txt). `git diff <that tree> b09b5f9c` is the whole hand resolution: 3 lines added and 3 removed, all in one hunk (ev/resolution-diff.txt). It drops the three conflict markers, closes the branch's `cardCollapse` function (`  }` / `}` / blank) and begins main's `themeLiveSwitch`. That is a union with both functions kept whole, as the body says.
- Merged file read back at the head:
  - Every line added by main's own change (cbe8d93b..f44e761c) is present, and so is every line added by the branch (cbe8d93b..eda078ba).
  - Definitions: themeMismatch at :423, cardCollapse at :537 and themeLiveSwitch at :647.
  - Call sites: `await themeMismatch` at :3292, `await themeLiveSwitch` at :3294 and `await cardCollapse` at :3299.
  - `node --check` passes.
- Body figures re-derived (ev/body-figures.txt):
  - `git diff eda078ba HEAD --stat -- tests/card_browser.mjs` gives 147+/34-, which equals main's own diff of the file since the old base.
  - `git diff origin/main HEAD -- tests/card_browser.mjs` removes exactly 2 lines: the `hidden_series` scenario line and the `.legend-chip, .chip` query.
  - The head has 0 conflict markers.
- `PYTHONPATH=tests/hastub node tests/card_browser.mjs` at this head: `ALL BROWSER CHECKS PASSED`, rc 0, 0 FAIL lines (ev/card_browser.txt). That covers all 10 `collapse (light|dark)` checks and all 7 `R10 live` checks from main's themeLiveSwitch.
- `PYTHONPATH=tests/hastub GOLDEN_MODE=drift node tests/card.mjs`, run after tests/plan_view.py (rc 0): `ALL CARD CHECKS PASSED`, rc 0 (ev/card.txt).
- Mutant R1: `this._folds = { narrative: false, whynow: false };` inserted after the card's `set hass(hass) {` at line 15243. card.mjs gives rc 1 with one failure, `collapse: a hass refresh rebuilds the card and keeps each fold as it was` (ev/card-R1.txt). The file was restored and `git diff --quiet` passed.
- Null control: ` // null` appended to line 15243 gives rc 0, 0 FAIL (ev/card-null.txt).
- `node tests/card_drift.mjs origin/main`: `card_drift: 44 state(s) moved and claimed, 1 identical`, rc 0 (ev/card_drift.tail.txt). This re-derives the body's figure against main at f44e761c.
- Claims and versions:
  - `python3 tests/env_drift.py --claims-only origin/main`: `claims hygiene: origin/main ok`, rc 0 (ev/claims-only.txt).
  - VERSION reads 7.1.13, which equals card_claimed_drift.txt's `claims-for: 7.1.13`.
  - VERSION, the manifest and RELEASE_NOTES.md show no change against f44e761c (ev/version-untouched.txt).
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2709 ENTITY CHECKS PASSED`, rc 0 (ev/entities.txt).
- `git merge-tree --write-tree origin/main 0e60a6f9`: rc 0. origin/main is f44e761c, which is this head's own merge base (ev/merge-tree-main.txt).
- No change to dev/governance/roles/ between the merge base and origin/main.
- Head check: the body's `## Head` names 0e60a6f9 and its parent b09b5f9c. `git ls-remote` still prints 0e60a6f9 for fix/r10-card-collapse at posting.
- The previous verdict recorded no findings, so none needed resolving.
- CI: `merge_train.py classify 0e60a6f9 --pr 3441` was polled from 23:39 to 00:08 UTC, at least 60 s apart. Every run printed `WAIT 0e60a6f9a681992f4f983ee79dce2fa2d980c4d5 pending: gate red: none`, rc 3 (ev/classify.log). No red is reported, so no `## Red checks` answer is owed (ev/owed-reds.txt). The heavy gate is cited from CI and was not re-run here.

## Findings

none
