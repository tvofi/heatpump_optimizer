Pins the recorder open line in `tools/replay/export.py`'s `open_recorder` on every branch. The default-SQLite branch's line was unpinned: deleting it, making it constant or labelling it MySQL/MariaDB left every fast check green. `tests/replay.py` gains `_open_line_branches`, which drives `export.open_recorder` on the default, `--db`, MySQL URL and SQLite URL branches and asserts the exact stderr line for each: the kind by constant, the path only on `--db`, and no URL-derived text (user, password, host, database) anywhere. Production code is unchanged because the test found no real defect. Code-scanning alert 47 (py/clear-text-logging-sensitive-data) stays closed, as no production line changed.

Carry (#3078 r8 blocked finding, mutation-vacuous default-SQLite open line): discharged. The default-SQLite line is now pinned by `recorder:open_recorder_line:default`, and every mutant below is killed.

## Head

77e3f018ca0d6488fd9353fcd403c30e3c115c9b

## Mutation proof

Each mutant replaced one `print(... "reading the recorder: ...")` line in `open_recorder` and was run against the recorder checks. Null green on the clean head, restored afterwards (`git diff tools/` empty). All 12 went red on the named check:

- default-SQLite branch: delete, constant, mislabel as MySQL/MariaDB all red on `recorder:open_recorder_line:default`
- `--db` branch: delete, constant, mislabel all red on `recorder:open_recorder_line:db_path`
- MySQL URL branch: delete, constant, mislabel (as SQLite) all red on `recorder:open_recorder_line:mysql_url`
- SQLite URL branch: delete, constant, mislabel (as MySQL/MariaDB) all red on `recorder:open_recorder_line:sqlite_url`

## Null control

On the unmodified production code the five new checks (`recorder:open_recorder_line:default`, `:db_path`, `:mysql_url`, `:sqlite_url` and `recorder:open_recorder_lines_carry_no_url_value`) all pass.

## Figures

- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED -- 3 script(s) run` (debug_collect, entities, features); all three passed.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, no budget touched.
- `bash tools/pr/prepr.sh --verbose`: rc=0 at the head above.
- origin/main moved from c7aa121 to 8f28629 after that run, changing only `dev/programme/delivery/*.md`; `git merge-tree --write-tree origin/main HEAD` reports no conflict, so main was not merged and prepr was not re-run.

## Red checks

none

## Forward-carry

none

## Friction

none
