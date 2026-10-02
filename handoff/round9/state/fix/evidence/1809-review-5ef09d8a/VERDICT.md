Fix review: merge 5ef09d8acd8ad3fd21ba4bc1ec155f0be989e6cb

This reviews the merge delta of PR #1809 (F10.1d). The base verdict, merge at e52f5970, was round 2. The PR head was 5ef09d8a at posting. Main is f67f598a (#1806 merged).

## RESULT lines
- RESULT merge 7ab5fe2f (e52f5970 + origin/main f67f598a), tree 62d75468: it is identical to `git merge-tree --write-tree origin/main e52f5970` (claimnotes driver installed). That command exits 0, so the merge contains no hand resolution.
- RESULT drop 5ef09d8a: I ran CI's own call on a worktree at 7ab5fe2f, `env_drift.apply_inherited_claims(".", ref="origin/main")` (tests.yml claims-autofix step). It returned `changed`. Afterwards `git diff 5ef09d8a` is empty, so the hand commit is byte-identical to what claims-autofix would push. The change deletes the 5 F6.4 `coord_*` claim lines from tests/golden/claimed_drift.txt. It leaves the notes and card_claimed_drift.txt untouched, because claim_kinds marks the card file False.
- RESULT dst_checks at 5ef09d8a, with F6.4's coordinator.py merged in: ALL 96 DST / QUARTER-GRID CHECKS PASSED.

## Notes
- The commit subject is `claims: drop claims inherited ...`, not the bot's `ci: drop inherited claims`. That only matters to the loop guard. A later claims-autofix run on this head finds nothing left to drop.
- When #1809 merges, main's claimed_drift.txt loses F6.4's 5 claim lines. Per the coordinator, this is the accepted record-loss class that R9-F10.8 owns. ci-autofix.md does not itself state that acceptance; I did not re-derive it.
- CI at 5ef09d8a: typing, briefs, policy-docs, pr-contract, budget-raise-gate, closure-scope, env-matrix, browser, hassfest, validate-hacs, delivery-status, nightly-status and instrument-self-tests are green. fast (3.14), mutation, closures, coverage and Analyze (python) were in progress at posting. I cite them rather than re-run them; merge only on green.
