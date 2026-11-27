Fix review: merge cd52e10e014d943ade2bc403b100ee1bc206feae
bus-nonce: b2b625f68b08a11e654de4e486cf574b

Round: first review (full scope, no reviewed-head).

RESULT mutation: d6_register._pick's final `return theirs` made to refuse gives 2 FAIL lines in `python3 -I tools/merge/ledger_merge.py --self-test` (the arm's cases and the md rendering case); restored, all passed.
RESULT harness: `dev/audit/harnesses/hotfile_conflicts.py` (built by the fixer, no finder's harness named) at cd52e10e014d943ade2bc403b100ee1bc206feae reproduces the body's table: claims.json and claims.md 13 before, 0 driver, 0 after; merges with any conflict 76/74/49. Under the mutant above the register's driver column returns to 13, so the harness moves under its own perturbation.
RESULT null-control: `other files` reads 84 in all three columns at the head and under the mutant; no OTHER-FILE-MOVED line.
RESULT layout: merge_json and merge_md round-trip the committed claims.json and claims.md byte for byte (125 rows each), so the layout guard does not refuse the real register.
RESULT conflict: `git merge-tree --write-tree origin/main cd52e10e014d943ade2bc403b100ee1bc206feae` exits 0.
RESULT version: VERSION, manifest version and the notes heading are untouched; neither claim file is touched.
RESULT checks: the latest `gate` run at the head (140464302077) is success; `tests / nightly-status` failure is a non-required check.
Note: harness: the replay harness is the fixer's, not a finder's; the `after` column models #3911's merged change, as the body states.
