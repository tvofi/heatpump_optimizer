Fix review: merge 502b0df305cee6ac265f75043bd58563cbff2578

bus-nonce: 1e4bf53b65f13a0e7aa6f7287219df98

## Scope
Resolution delta only: eab999bc6230b5f9668826b25dc64dcf657e46bf..502b0df305cee6ac265f75043bd58563cbff2578, the merge of main 1148ee635e8278ebbb033b524d54001b2a89218c (PR #2917) into the branch, reviewed three-dot against origin/main.

## Findings
None. The merge resolution is a pure union; nothing is deferred or owed.

## Evidence
- tests/golden/claimed_drift.txt at the head is byte-identical to main's (1148ee635e8278ebbb033b524d54001b2a89218c). The branch claims nothing there: its copy was byte-identical to its fork point. Main's own removal of the R10-BUFFER-STORE and R10-HOUSE-GRADE claims and its addition of R10-COP-GATE are kept, and no branch claim was reinstated. That is exactly main's claims plus this branch's own (none).
- card_claimed_drift.txt: head equals main and the branch; no diff.
- The three-dot diff touches no file under tests/golden. The PR's file list is .github/workflows/gate-sweep.yml, dev/programme/delivery/2955.md, tests/arch_score.py, tests/closures.json, tests/entities.py, tools/policy/agreement.mjs.
- Ledger: delivery/2955.md is the branch's own row; delivery/2917.md is main's, kept unchanged.
- The files differing from both parents are tests/closures.json and tests/entities.py. The branch's own +/- lines in each are identical before and after the merge. closures.json still parses as JSON.
- git merge-tree --write-tree origin/main HEAD is clean (tree 3f3ed0c9...). origin/main is still 1148ee635e8278ebbb033b524d54001b2a89218c.
- CI check-runs at this head: gate, pr-contract, lane-proofs, fast (3.14), coverage, coverage-ratchet, closures, typing, browser, briefs, hassfest, CodeQL and arch-instrument all succeeded. The skipped ones are autofix and replay jobs. tests / nightly-status concluded failure; it is a nightly status job, not a required check, and does not block.
- Not re-run: the mutation proof from the earlier verdict at eab999bc6230b5f9668826b25dc64dcf657e46bf. Only the merge resolution changed, and the branch's own diff to closures.json and entities.py is unchanged.
