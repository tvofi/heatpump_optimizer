Fix review: merge eda078bac41473246ff7d87a5736de58d64ad97a

bus-nonce: 42ecf6c01c417139694139063dc7aac3
pending-ci: gate

## Scope

Resolution delta, round 5 counting the body's rounds 1-4. A merge verdict stands at 8c45afd38f2378350bd2e532b68da28e7f682f0e. `review_carry.py 8c45afd38 eda078bac` prints FRESH-REVIEW because 7cca4543b is not the automatic merge of its parents, so this review covers the delta (fix-review.md step 12): the merge resolution, and whether the branch's own patch is the one already reviewed. The delta writes no production line by hand (see below), so the review does not widen.

## Evidence

- Branch patch unchanged: `git diff d72963a7 8c45afd3` (reviewed head against its merge base) and `git diff cbe8d93b eda078ba` (this head against its merge base) touch the same 16 files, 573+/68- each. Per file, the sequences of added and removed lines are byte-identical in all 16 (ev/patch-compare.txt). So this head's tree is main at cbe8d93b plus exactly the reviewed patch. Every line main carried survives except the lines the branch replaces, and main had not changed those lines (their `-` content is identical on both bases).
- Both parents reconstructed: `git merge-tree --write-tree --merge-base=d72963a7 cbe8d93b 8c45afd3` conflicts in two files (ev/resolution.txt). Files both sides touched: the card JS, docs/index.html and card_claimed_drift.txt.
  - tests/golden/card_claimed_drift.txt: `MERGE-CLAIM: refused`, CONFLICTING CLAIMS (base 7.1.11, branch 7.1.12, incoming 7.1.11). Resolution read back: main's stamped file (`claims-for: 7.1.12`, the R10-HOTFIX claim lines emptied by the stamp) kept verbatim, and the branch's R10-CARD-COLLAPSE block (a blank line, an 8-line comment and 44 state lines) appended unchanged. Nothing from either side was dropped, and no stale 7.1.11 claim was carried. VERSION reads 7.1.12, which equals claims-for.
  - docs/index.html: main's product-page rewrite kept. The branch's one changed line (the `#card` lead, `data-src="README.md#dashboard-card"`) was re-applied; `git diff cbe8d93b eda078ba -- docs/index.html` is one removed line and one added line. Main's adjacent edit at the old line 283 is present.
  - custom_components/.../heatpump-optimizer-card.js auto-merged. Main's only change between the two bases is line 14 (the v7.1.12 stamp's version constant), which does not interact with the fold code.
  - tests/closures.json: `git diff cbe8d93b eda078ba -- tests/closures.json` is empty. The entities.py rc re-derivation (1 to 0) is already on main, so the branch adds nothing there.
- Head check: `git ls-remote origin refs/heads/fix/r10-card-collapse` prints eda078bac41473246ff7d87a5736de58d64ad97a. The body's `## Head` names this head and its handoff 30f1b6c8fe007b8d4400ba262e51fecd10afb4d2. The body's merge-repair account matches the reconstruction above.
- `git merge-tree --write-tree origin/main eda078ba` (origin/main 19baca76): rc 0, no conflict.
- VERSION, the manifest and RELEASE_NOTES.md: `git diff --stat cbe8d93b eda078ba` over them is empty.
- `python3 tests/env_drift.py --claims-only cbe8d93b`: `claims hygiene: ... ok`, rc 0 (ev/claims-only.txt).
- Runs at this head, all with `PYTHONPATH=tests/hastub GOLDEN_MODE=drift`, after `tests/plan_view.py` (rc 0):
  - `node tests/card.mjs`: ALL CARD CHECKS PASSED, rc 0 (ev/card-null.txt).
  - Mutant R1, `this._folds = { narrative: false, whynow: false };` added to the card's `set hass` at line 15243: rc 1, `FAIL collapse: a hass refresh rebuilds the card and keeps each fold as it was` (ev/card-R1.txt), then restored. This is the body's round-4 figure.
  - `node tests/card_drift.mjs cbe8d93b`: `card_drift: 44 state(s) moved and claimed, 1 identical`, rc 0 (ev/card_drift.tail.txt). This is the body's figure, re-derived.
  - Null control: with card_claimed_drift.txt replaced by main's copy, the same command is rc 1, refusing unclaimed moved states (ev/card_drift-null.tail.txt). Every moved state is claimed, and every claim moves.
- Not re-run here; CI's heavy runs are cited instead: the full scoped gate, `tests/card_browser.mjs`, `env_drift.py --all`, structure.py and archscore. The delta writes no code line, so the figures already reviewed at 8c45afd stand.
- Red checks: `tests / nightly-status` is red at this head. It is outside the `merge_train.py owed-reds` set (ev/owed-reds.txt), grades main, and blocks nothing. The body's `## Red checks` answers `tests / fast (3.14)` from an earlier head.
- CI: `merge_train.py classify eda078ba --pr 3441` polled 13:47-14:17 UTC, last line `WAIT eda078bac41473246ff7d87a5736de58d64ad97a pending: gate red: none`, rc 3 (ev/classify.log). At 14:09 the check runs showed `tests / coverage` and `tests / fast (3.14)` in progress. Already green at this head: closures, browser, typing, mutation, arch-instrument, briefs, closure-scope, arch-score, budget-raise-gate, codeql x3, env-matrix, policy-docs, wave-script, instrument-self-tests, hassfest and validate-hacs. A `gate` run completed `failure` at 13:48, before those lanes finished; classify does not report it red, and the relay re-checks it at posting.

## Findings

none
