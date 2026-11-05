Fix review: blocked 4e4bb291b503be5abac829a6a068358ffdea1091 ci-red: gate concluded cancelled at this head (run 41924350700 cancelled with tests / fast (3.14) and tests / coverage unfinished), no gate verdict exists; code review otherwise clean

bus-nonce: 4c809e022e9139d2738a5285fd3d8b50

## Head

Measured 4e4bb291b503be5abac829a6a068358ffdea1091 (round 2, a delta review after the round-1 block of 7637d663 on ci-red). review_carry.py 7637d663 -> head prints FRESH-REVIEW (c3c308ed is a manual merge), so the code was measured afresh. The branch head was still 4e4bb291b503be5abac829a6a068358ffdea1091 at 00:01 UTC. The head and the code handoff c3c308ed are identical under tests/, tools/ and custom_components/ (git diff --stat is empty), so the orchestrator's merge of origin/main 086a59da4 added no code. Three-dot diff: tests/replay.py +44/-0 and dev/programme/delivery/3167.md +1, which matches the body's "additions only".

## Block

The required context `gate` has no conclusion other than `cancelled` at this head. Both gate runs were cancelled: run 41924352912 (gate 126914223696, 22:38:53) and run 41924350700 (gate 126935055893, 23:22:31). Run 41924350700 was cancelled while `tests / fast (3.14)` (started 23:12:14) and `tests / coverage` (started 23:05:05) were still running. Its lanes ci-ratchet, lane-proofs, claims-autofix, coverage-ratchet and graders-head-copy were cancelled too, and pr-contract was skipped. `merge_train.py classify 4e4bb291b503be5abac829a6a068358ffdea1091 --pr 3167` prints `RED 4e4bb291b503be5abac829a6a068358ffdea1091 pending: none red: gate` (rc=1) and did not change in a 20-minute wait after every workflow had concluded (23:41 to 00:01 UTC). The branch did not move, and I found nothing in the PR that explains the cancellation. No lane concluded failure: every lane that finished, except main-owned nightly-status, is green, including `tests / replay` (the round-1 red). The remedy is to re-run CI at this head. A green gate with a pr-contract run over the body discharges this block. I am not claiming GREEN, and step 11 cannot be closed without a pr-contract run at this head.

## Findings

- Follow-up: both CI runs at this head ended `cancelled` with no new push and no later run, which leaves the PR without a gate verdict. The orchestrator owes a re-run of CI at 4e4bb291b503be5abac829a6a068358ffdea1091, then this delta review again on CI alone, because the code measurements below carry. Carry: dismissed: task owed by the orchestrator after this verdict, a CI re-run on an unchanged head; not a code defect

## Evidence

- Mutation proof, re-run by me on the head worktree (ev/mutants.txt, ev/mutant-mysql-sqlite-label.txt). I planted four mutant kinds (delete, constant, mislabel, print the db/url) on each of the four `print("reading the recorder ...")` lines in tools/replay/export.py open_recorder (lines 340, 350, 352, 354), ran recorder_checks() once per mutant, and restored the file each time (git status --short empty). Results:
  - Default branch (354): every kind is red on `recorder:open_recorder_line:default` alone. That is the carry #3078 r8 named, now discharged.
  - db_path, sqlite_url and mysql_url branches: every kind is red on the branch's own open_recorder_line check plus the older checks the body names.
  - The one survivor in the grid, the MySQL line "mislabelled" as `MySQL/MariaDB database`, is an equivalent mutant: MYSQL_LABEL is that exact string.
  - The non-equivalent MySQL mislabel (SQLite database) is red on `recorder:open_recorder_line:mysql_url` and two older checks.
  - Null: unmutated recorder_checks() returns 28 checks, 0 failed, which matches the body's 28.
- Body figures re-derived at this head:
  - `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints MODE: SCOPED -- 3 script(s) run, 30 scoped out (ev/closure.txt).
  - debug_collect: ALL 162 passed. entities: ALL 2616 passed. features: ALL 4791 passed (ev/*.txt).
  - structure.py: STRUCTURE RATCHET PASSED.
  - The claim files, VERSION, RELEASE_NOTES.md and manifest.json are identical to origin/main (claims-identical).
  - numstat is 44/0 on tests/replay.py.
  - Full tests/replay.py locally: 186 checks, and all five new recorder checks are ok. The local run had 2 FAILED, both synthetic-dhw-only.json cycle_cost: this sandbox reads ref_ms 28.65, which lies in no COST_RUNNER_CLASSES band, while running concurrently with my scoped scripts. The body reports 4 failing on its sandbox. The count is runner-dependent and I did not re-derive it. CI's `tests / replay` at this head concluded success (126913989042), which settles the lane.
  - prepr.sh rc: not re-run. The body defers it to the handoff line.
- Step 6, class: the finding names one seam, the open line of open_recorder. The diff pins all four of its branches (default, --db, MySQL URL, SQLite URL). recorder_url-derived URLs reach the same two URL branches. No other print site in open_recorder exists (grep of "reading the recorder" returns 4 lines, all covered).
- Steps 4, 5 and 14: the diff changes no production code, no claim file, no budget, closures.json or INERT, and no version. No instrument moved.
- Step 13: `git merge-tree --write-tree origin/main 4e4bb291b503be5abac829a6a068358ffdea1091` exits 0 against origin/main af941ad4 (tree c802beb7) and again against d91e464a, re-fetched before the return (tree ac151142). Main since base 086a59da4 does not touch tests/replay.py, tools/replay or custom_components. At the return, the branch head is still 4e4bb291 and classify still prints RED pending: none red: gate.
- Step 10, forward-carry: the body says none. No later stage changes.
- Step 11, red checks (ev/check-runs.txt, all 55 runs, one page):
  - `tests / replay`, the round-1 red, is answered in the body and is green at this head.
  - `tests / nightly-status` failed. It is not this PR's: the diff reaches nothing it reads.
  - `gate` was cancelled, which is the block above.
  - No pr-contract run at this head checked the body, so the step-11 answer is unverified here.
- CodeQL python analysis concluded success at this head. Code-scanning alert 47 was not readable from this seat.
- Harness: the finding has no committed finder harness. The new recorder checks in tests/replay.py serve as the pin, and I measured with my own mutation driver, built for this review and kept out of tree (its output is in ev/mutants.txt).
