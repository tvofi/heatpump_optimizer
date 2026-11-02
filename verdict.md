Fix review: blocked ef456f2b24b622c928603b26d8d1ce37b9b75014 body-carry-missing: the PR body has no literal line "Carry: R10-REPLAY-OPEN-LOG" for the unpinned default-SQLite open line

bus-nonce: 136c1ee252ada24b26f1c40ab6803dc3

Round 9 scoped re-check at ef456f2b24b622c928603b26d8d1ce37b9b75014 (review_carry.py from bbcbe259: CARRY).

## Block

The split ruling carries the round-8 mutation-vacuous finding (the open line on the default-SQLite branch of open_recorder in tools/replay/export.py is unpinned) to R10-REPLAY-OPEN-LOG, on condition that the body names it with the literal line "Carry: R10-REPLAY-OPEN-LOG". The live body at this head has only "Carry: R10-REPLAY-COST-BUDGET" (Forward-carry) and no mention of R10-REPLAY-OPEN-LOG. Patch the body to add the line, then re-dispatch for a merge verdict. Blocked on this alone per the brief.

## Findings

- The default-SQLite open line (the else branch of open_recorder in tools/replay/export.py) is unpinned by any FAST row, so deleting it, making it constant or making it say MySQL/MariaDB leaves every check green. Carry: R10-REPLAY-OPEN-LOG

## Evidence

- Read at this head: the open line names the recorder by a per-branch constant (MYSQL_LABEL, SQLITE_URL_LABEL), and the typed --db path only on the --db branch. No URL-derived value reaches it. I did not re-plant mutants or finish the null run of tests/replay.py, since the block does not depend on them.
- git merge-tree --write-tree origin/main head: exit 0 (ev/merge-tree.txt).
- Diff against the merge base touches none of VERSION, RELEASE_NOTES.md or the two claim files.
- CI classify at this head: WAIT, pending (ev/classify.txt); CodeQL check run id=125061160308 reads neutral and Analyze (python) was in_progress at render, so alert 47 closure is not confirmed.
- Not re-run: structure.py, scoped-gate MODE line, delivery row, mutants on the other three branches.
