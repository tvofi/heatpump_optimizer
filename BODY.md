Pins the recorder open line in `tools/replay/export.py`'s `open_recorder` on every branch. The default-SQLite branch's line was unpinned: deleting it, making it constant or labelling it MySQL/MariaDB left every fast check green. `tests/replay.py` gains `_open_line_branches`, which drives `export.open_recorder` on the default, `--db`, MySQL URL and SQLite URL branches and asserts the exact stderr line for each: the kind by constant, the path only on `--db`, no URL-derived text. Production code is unchanged; the test found no real defect, so code-scanning alert 47 stays closed.

Carry (#3078 r8 blocked finding, mutation-vacuous default-SQLite open line): discharged by `recorder:open_recorder_line:default`.

Merge-forward after #3174 (62f94f3f), round 2. `tests/replay.py` conflicted at one hunk in `recorder_checks`: main added the `recorder:unsupported_scheme_refusal_prints_none_of_the_url` block, this PR added the call `res.extend(_open_line_branches(tmp, fake, marked))`. Resolution keeps both: main's block byte-identical, this PR's call line and function added (`git diff origin/main -- tests/replay.py` shows additions only). #3174's cost-budget code (`COST_CLASS_BUDGETS`, `class_budget`, `COST_RUNNER_CLASSES`) is untouched by this PR's diff. Round 1 blocked only on `tests / replay` (synthetic-dhw-only.json cycle_cost cpu_ratio 2.615 over budget 2.173), the budget #3174 re-centres.

## Head

c3c308ed11fa6300b506942f80114c5799675be9

## Mutation proof

Twelve mutants in `tools/replay/export.py` `open_recorder`, one `print("reading the recorder ...")` line each (default, `--db`, MySQL URL, SQLite URL branch x delete, constant, mislabel), each run through `recorder_checks()` and restored afterwards (`git status --short` empty). All twelve red; the new check named for the branch is red in every case:

- default: `recorder:open_recorder_line:default` (x3)
- `--db`: `recorder:open_recorder_line:db_path`, also `recorder:open_line_names_kind_and_db_path` (x3)
- MySQL URL: `recorder:open_recorder_line:mysql_url`, also `recorder:db_url_credentials_never_printed`, `recorder:open_line_names_kind_and_db_path` (x3)
- SQLite URL: `recorder:open_recorder_line:sqlite_url`, also `recorder:sqlite_db_url_named_by_kind_not_path` (x3)

The default-branch row is the one no check but this PR's pinned before: it is the only one of the four red on a single check.

## Null control

Unmutated `recorder_checks()` at this head: 28 checks, failed list empty (the mutation driver's first line). Full `tests/replay.py` at origin/main 783d8dc7 prints 181 checks, 4 failed; at this head 186 checks, the same 4 failed: the difference is exactly the five new `recorder:open_recorder_line:*` and `recorder:open_recorder_lines_carry_no_url_value` checks, all passing.

The 44 added lines do not execute inside the cycle_cost timed span. `git diff --numstat origin/main HEAD -- tests/replay.py` reports 44 added, 0 deleted. They sit in `_open_line_branches` and its call inside `recorder_checks`, which `main()` reaches through the self-checks aggregate (`... + tibber_price_checks() + recorder_checks() + mask_checks() ...`); the timed span is `run_fixture`'s per-cycle `time.process_time()` / `time.thread_time()` window (began = `time.process_time()` through `cycle_cpu.append`), a different function executed in a separate `--one` subprocess per fixture. Neither calls the other.

## Figures

- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED -- 3 script(s) run` (debug_collect, entities, features). `PYTHONPATH=tests/hastub python3 tests/debug_collect.py` ALL 162 checks passed; `tests/entities.py` ALL 2616 checks passed; `tests/features.py` ALL 4791 checks passed.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, no budget touched.
- Replay lane locally, `PYTHONPATH=tests/hastub python3 tests/replay.py` on this sandbox: 4 of 186 FAILED, all `synthetic-dhw-only.json: cycle_cost` (clean run and the cpu/memory/loop doubled arms), every one `runner class unknown: ref_ms 37.02 lies in no band of COST_RUNNER_CLASSES`. The sandbox's reference solve reads 36-40 ms, in none of the four recorded bands. The null control is the same command at origin/main: the same 4 fail with the same message (ref_ms 37.16), so the failure is the sandbox's runner class, not this diff. The cost budget itself is not exercised here; CI's runner reads a band.
- Claim files, `VERSION`, `RELEASE_NOTES.md`: `git diff --quiet origin/main -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION RELEASE_NOTES.md && echo claims-identical` printed claims-identical.
- `bash tools/pr/prepr.sh` rc recorded in the handoff line below the body push.

## Red checks

Read: check runs of PR #3167 at 7637d663, `pull_request_read get_check_runs` perPage 100, page 1 returned total_count 55 = the whole set, no further page. Red: `tests / replay` (failure at 7637d663, run 41405222589), `gate` and `pr-contract / pr-contract` (both runs 41405222130 and 41405222589).

- `tests / replay`: inherited runner noise on a tight budget (cycle_cost cpu_ratio 2.615 over 2.173 on synthetic-dhw-only.json), fixed by #3174, which re-centres it; this PR adds nothing to the timed span (Null control). Cheaper detector: none for a runner-class reading; the value is a property of the runner CI draws, so the only detector is the lane that reads it.
- `gate`, `pr-contract`: not examined at 7637d663; re-run at the new head by `tools/pr/prepr.sh` and by CI. Neither is a runner-class reading, so prepr is their cheaper detector and ran locally before this handoff.

## Forward-carry

none

## Friction

none
