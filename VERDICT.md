Fix review: blocked 38aee2235ae2dbc72ef1023e5baa27b8ffa1d619 harness: design-trace-missing every key line kept: quiet mode hides the per-car MERGED, post-merge OWED and failing-check-name lines, drops the SKIP lines that skip-share reads, and five mutants of the quiet rules survive

bus-nonce: 02e6a9b482fbb4ee5b8cd5fd966037a7

## Block

This is round 1 of the review, a handoff review at the handoff tip `38aee2235ae2dbc72ef1023e5baa27b8ffa1d619`. The body's `## Head` names the same SHA.

The brief's carry 0 (roster `handoff/audit-r10-roster`, group R10-SEAT-SCRIPT-OUTPUT) requires "one result line per step, the failing step's tail, ... and every key line kept (mode, the failing check names, the final summary)". Its control requires that "the exit codes agree across quiet and verbose; each rule has a mutant." At this head:

1. **Key lines are dropped.** `KEY_LINE` keeps only lines that start with its 14 alternatives. I fed `quiet_log` a clean two-car run built from the real `log()` f-strings in merge_train.py: `#{pr} {st}` for the merge, `#{pr} {ln}` for postmerge OWED, `#{pr} post-merge steps OWED (rc=..)`, `#{pr} {h} ci red={red}`, `#{pr} dropped to serial: the proof is red at ...` and `serial: ...`. Of the 10 lines, 8 were hidden (`ev/quiet-demo.txt`). Quiet stdout shows only `TRAIN pid=..`, then `TRAIN DONE`, and `TRAIN DONE` carries no summary. Nothing reports which PRs merged. A post-merge OWED obligation, the failing check names and the serial mode are all invisible unless a `TRAIN STOPPED` follows within 20 lines. I classified every production `log(` literal in merge_train.py by its first word against `KEY_LINE`. Among the hidden first words are `#<pr>` (35 call sites), `INFRA-RED`, `STALE`, `OVERLAP`, `REJOIN`, `[MAIN-MOVED]`, `LEFT`, `QUEUE`, `FRONT`/`REMOVED`, `serial`, `rehearsal` and `grade`.
2. **The exit-code agreement is asserted "by construction", not measured.** The body's `## Null control` runs nothing in quiet mode against verbose mode.
3. **The quiet rules have no mutant.** Five mutants survive the full `merge_train.py --self-test` (614 checks, 0 failed each; `ev/mutants.txt`):
   - M5 removes the injection in `main` (`opts["log"] = quiet_log(...)` → `pass`), so quiet mode is never wired.
   - M6 drops the `TRAIN_VERBOSE=1` switch.
   - M7 flushes held chatter on every key line, not only on a stop.
   - M4 drops `REFUSE` from `KEY_LINE`.
   - M8 reduces `KEY_LINE` to `(TRAIN)` alone.

   Only the predicate, the tail bound and the stop flush are pinned.

4. **A downstream instrument loses its input.** `train.sh` writes the train's stdout to `train.log`. `merge_throughput.bottleneck_metrics`, which serves bottleneck_check.py, plan_page.py and state_docs.py, parses `SKIP #<pr> <phase>:` lines there. Under quiet mode those lines reach only `train-full.log`, so every batch reads `skips=[]` and the skip-share measure reads zero. The fix must either keep `SKIP #` lines in the quiet stream or point the readers at the full log.

A fix keeps every per-car result, OWED and failing-check line in quiet mode, or folds them into a `TRAIN DONE` summary. It also measures exit-code agreement across the two modes on a seeded failure and gives each KEY_LINE member, the `main` injection and `TRAIN_VERBOSE` a killing check.

## Findings

none

## Evidence

- Head reviewed: `38aee2235ae2dbc72ef1023e5baa27b8ffa1d619` (`ev/HEAD.txt`). Merge base `ba544faa2dd25b75b0129879112d6409affe9662`. Diff: 13 files, +59/-9 (`ev/diff.patch`).
- No review packet and no CI: the pull request does not exist yet, so I read no checks and no red is owed an answer. `merge_train.py owed-reds` prints `tests / mutation`, `tests / typing`, `validate / validate-hacs`.
- `git merge-tree --write-tree origin/main <head>`: rc 0, tree `dd662c845b4db18e1a374ba820bbf0c4d78393b9`, no conflict (`ev/mergetree.txt`).
- VERSION, the manifest, RELEASE_NOTES.md and `tests/golden`: untouched (diff stat empty). No claim file is touched, and no fixture is in scope.
- RESULT selftest-head: `merge_train self-test: 614 checks, 0 failed` (`ev/selftest-head.txt`).
- RESULT body-mutant (M1, `if not KEY_LINE.match(m):` → `if False:`): 2 failed, the two checks the body names. Reproduced.
- RESULT M2 (tail bound removed): 2 failed. M3 (stop flush removed): 1 failed. Killed.
- RESULT M4, M5, M6, M7, M8: 0 failed each. These are the survivors above.
- RESULT pr_bounded: heartbeat 8/0, delivery_row 6/0, cloud-setup 22/0 and failure_logs 7/0, all rc 0. The bound null: `PR_SELFTEST_SECONDS=1 tick_loop.sh --self-test` printed `BOUND: the self-test passed 1 s` and exited 124 after 1 s, so the bound is entered (`ev/pb-summary.txt`). I did not re-run the other 8 seat self-tests.
- Body figure "12 scripts": re-derived. The diff touches 12 scripts besides merge_train.py.
- Body figure "the self-tests of 8 scripts ran rc 0": verified for the 4 above, not re-derived for ci-watch, handoff_push, seat_venv or tick_loop's full run.
- The body says update_pr.sh and open_pr.sh "already" print only key lines. That claim is not verified by this review, and carry 0 names both scripts.
- The harness is the fixer's own self-test checks. Carry 0 names no committed finder harness, and the demo in `ev/quiet-demo.txt` is this reviewer's.
- I mapped the readers of `train.log` with a delegated scout and spot-checked the result myself. `tools/audit/merge_throughput.py:1204`, `TRAIN_SKIP_RE = ^SKIP #(\d+) ([a-z-]+): (.*)$`, reads the writer `SKIP #{pr} {phase}: ...` at merge_train.py:3715. That line does not match `KEY_LINE` (`ev/skip-lines.txt`), so it now goes only to `train-full.log`. This is block item 4.
