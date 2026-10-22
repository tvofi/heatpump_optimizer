Fix review: merge 79888f045b89f4dc6c87e5f5d75688d41986a716

bus-nonce: ee6cea512b2ddaaa0f44a4aa4d7a3f0a

Round 4, a delta re-review at head 79888f045b89f4dc6c87e5f5d75688d41986a716 (ev/HEAD.txt). It judges the resolution delta of the merge of main 0b162da1 into 37d1d0d3 and nothing else. The role contract is current: the role diff from the merge base to origin/main is empty. origin/main has since moved to 04c1dd77; the head also merges clean there.

## Findings

- None. The resolution delta is the one conflict resolution and nothing else, and every figure re-measured as the body states. Carry: dismissed: nothing owed beyond this verdict (item 2584r4a1)

## Evidence

- Resolution delta. I merged the two parents with git (`merge-tree 37d1d0d3 0b162da1`) and diffed that tree against the head's tree. The only difference is in dev/audit/harnesses/r10_seat_selftests_mutants.py: the conflict markers are gone, 10 lines removed. The docstring keeps the PR's wording ("S01..S38, and each per-file id (<file>-<n>)"), which is true of the merged list. Nothing else differs (ev/resolution_delta.txt). `git diff 0b162da1 HEAD --stat` touches only the PR's own 8 files (ev/vs_main_stat.txt), so main's side carries nothing the PR did not write.
- Mutant union. Parsing MUTANTS with ast: 37d1d0d3 has 64 ids, 0b162da1 has 42, the head has 65, all distinct. Head set equals the union of the two sides' tuples, with 0 dropped and 0 altered. It holds S01..S38, the 23 per-file ids (merge_train-1..18, merge_pr-1, orchestrator_tick-1..4), body_patch-1, tick_loop-1..2 and heartbeat-1..4.
- Auto-merged files (merge_train.py, orchestrator_tick.py, INSTRUMENTS.md, closures.json). Main's side is #2585's nightly.yml rename and the MAIN D-1 arm. They compose: the tick self-test passes 194/0 including that arm, and merge_train passes 219/0 with the renamed workflow. The tick, merge_train and the harness agree with each other, so no semantic conflict was found. closures.json merged by the ledger driver (LEDGER-MERGE: resolved tests/closures.json), and vs main it differs by the PR's two lines only.
- Mutation harness re-run in full at the head, no names (ev/mutants.txt): `M0: 0 seat step(s) red`, 72 KILLED, `RESULT survivors=0`, exit 0, working tree clean afterwards. The null control for each mutant is the same step on the unmutated file, which the harness runs first and reports NOT RUN otherwise (none printed). This equals the body's 72.
- Self-tests at the head (ev/st_*.txt): merge_train 219 checks 0 failed, orchestrator_tick 194 checks 0 failed, merge_pr 18 checks 0 failed, selftest_wiring 77 self-testing 77 wired 0 unwired. All equal the body. Their null controls are the mutant runs above, where each mutated file turns the same step red.
- `carry_audit.py check --body` (the PR body as read from the API, ev/pr_body.md) prints `CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)`, with and without `--roster-ref origin/handoff/audit-r10-roster` (ev/carry_audit.txt).
- `git merge-tree --write-tree origin/main 79888f045b89f4dc6c87e5f5d75688d41986a716` exits 0 and is clean at origin/main 04c1dd77 (ev/merge_tree.txt). It was also clean against 0b162da1.
- CI from the check-runs API at the head, read 10:23Z (ev/ci_head.txt): of 35 runs, `nightly-status` is the only failure, and it is not a required check and does not block, and this diff reaches nothing it reads (the body answers it under Red checks). `closures` was still in progress when I read it, so I cannot cite its conclusion. The others are success, skipped or neutral, apart from a few still in progress at 10:05Z. I did not re-run any heavy lane.
- Not re-measured, since the delta does not reach them: the entities, structure, archscore and closure-pin figures in the body at 79888f04 (2388 entity checks, 112 closure pins). Round 3 re-derived the earlier-head equivalents. I did not re-derive these.
- This is round 4, and the fixer has made no code change since round 3; the only block was a main conflict. Nothing here asks for a re-cut.
- Checked by grep: no macOS home-directory or private-tmp path appears in this verdict or in ev/.
