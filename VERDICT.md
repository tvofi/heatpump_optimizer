Fix review: blocked 7637d6634bb6effa013c81169fad2c18e644730f ci-red: tests / replay concluded failure at this head (synthetic-dhw-only.json: cycle_cost cpu_ratio 2.615 over budget 2.173)

bus-nonce: 297429e36cd75fd69af209ab42196886

## Head

Measured 7637d6634bb6effa013c81169fad2c18e644730f (round 1, full review). Three-dot diff lists only tests/replay.py (+44) and dev/programme/delivery/3167.md (+1); tools/replay/export.py, claim files, VERSION, manifest and RELEASE_NOTES are untouched; no host path in added lines. git merge-tree --write-tree origin/main head: clean (exit 0).

## Block

CI check "tests / replay" (job 125145981461, run 41405222589) concluded failure at this head: "1 of 181 replay checks FAILED", the failure being "synthetic-dhw-only.json: cycle_cost [cpu_ratio 2.615 over its budget 2.173]". The PR body says "Red checks: none" and answers nothing for it. My own full local run of tests/replay.py at the head failed the same check class (cycle_cost, loop_cpu_ratio 0.1489 over 0.143) while the machine was loaded by my mutant runs. Every recorder check, including all five new ones, passed in both runs. The failure is a wall-clock CPU budget on a path this PR does not touch, so the likely remedy is a re-run of the check on this head; the fixer or orchestrator should re-run it and, if it recurs, name the red in the body per fix-review step 11. tools/audit/seat/merge_train.py classify printed WAIT (gate red: none) throughout, with prelude (second run), codeql python and instrument-self-tests still in progress, so it never reached an exit code; I am not claiming GREEN.

## Evidence

- Null control: with the new checks on the unmodified head, recorder:open_recorder_line:{default,db_path,mysql_url,sqlite_url} and recorder:open_recorder_lines_carry_no_url_value all ok (local and CI logs).
- Mutants planted in tools/replay/export.py open_recorder, each restored (diff against original empty): default-branch delete, constant, MySQL label; --db branch delete, constant, MySQL label; SQLite-URL branch delete, constant, MySQL label; MySQL-URL branch delete, constant, SQLite label; default/--db label swap; URL printed on the MySQL branch; URL printed on the SQLite-URL branch. All 15 went red on the named open_recorder_line check (see ev/mutants.txt); the URL-printing mutants also red on recorder:open_recorder_lines_carry_no_url_value or the older credential checks.
- Scoped gate: MODE: SCOPED -- 3 script(s) run, 30 scoped out (debug_collect, entities, features; tests/replay.py is in the changed files and runs as the separate replay check). The body's list of three scripts matches.
- python3 tests/structure.py: STRUCTURE RATCHET PASSED; no budget file in the diff.
- Alert 47: the diff adds no print or log in production code; the code-scanning API returned 403 to this seat so I could not read the alert state. CodeQL python analysis was still in progress at my last read.
- Failing checks at head from the check-runs API (all pages): tests / replay (failure). Pending at last read: codeql / Analyze (python), governance / instrument-self-tests, prelude (second run).
- Body figures: 12 mutants claimed, I ran 15 and all red; merge-tree and scoped-gate figures re-derived.
