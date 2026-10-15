Fix review: merge f3cbd393c8aa12ae5406b66ee894c500bac0a1cb

bus-nonce: 574da3c473cdf7c8daaaa921f8849caf

Round 1. PR #2281 (R10-TICK-ORCH items b, d, j; part of #2264). I measured head f3cbd393c8aa12ae5406b66ee894c500bac0a1cb from a detached worktree. It is code head 9b3fd503 plus the merge of main 78324e4a1, which brings in record rows only and leaves the PR's 13 files byte-identical to 9b3fd503, plus the delivery row. Merge base 78324e4a1. `git merge-tree --write-tree origin/main` returned rc 0. Policy roles at origin/main are unchanged since the merge base.

## RESULT lines (r10_tick_which_roster.py, run by me; roster ref handoff/audit-r10-roster at dd03b502)
- base 93f5970e (the earlier merge base; the only difference from 78324e4a1 is record rows): wire_r10_rc=2, wire_r10_touched_r10_file=0, null_r9_main_rc=0, tick_plan_r9_lines=13, tick_plan_r10_lines=0, daemonize_dashdash_rc=2
- head f3cbd393: wire_r10_rc=0, wire_r10_touched_r10_file=1, null_r9_main_rc=0, tick_plan_r9_lines=0, tick_plan_r10_lines=52, daemonize_dashdash_rc=0
- head with the perturbation `--roster-path dev/programme/rosters/wave-r9-groups.json`: wire_r10_rc=2, tick_plan_r9_lines=13, tick_plan_r10_lines=0. This returns to the base readings.
- Null control: null_r9_main_rc=0 at both ends. The 52 equals the round-10 roster's group count at dd03b502. The body cites db71fe47, and every figure reproduces at the newer roster tip.
- Step 9 disclosure: the harness is the fixer's own, and its header says so. R10-TICK has no committed finder harness. I re-derived its arms independently below.

## Mutation proof (step 1)
The body lists 9 mutants (M1-M8 plus M4b), not 10. I re-ran all 9 and added one of my own. All 10 were killed, and the tree was clean after each restore:
- M1 text compare: roster_lib (5 named FAILs), orchestrator_tick (3), roster_edit rc 1
- M2 override ignored: roster_lib (4), roster_edit (2)
- M3 silent round-9 fallback: roster_lib (2), roster_edit rc 1
- M4 state_of fixed to 9: state_docs `round 10's state`
- M4b roster_round_of returns 9: state_docs (3)
- M5 no `--` split: daemonize (3)
- M6 tick on a fixed r9 path: orchestrator_tick (4)
- M7 tick ignores --roster-path: orchestrator_tick (1)
- M8 default branch equals the base ref: roster_edit rc 1. It fails by crashing before the named never-main check is reached, but the run is still red.
- M9 (mine) `_git` ignores repo: roster_lib (6)

roster_lib's self-test reaches CI through tests/entities.py. fast (3.14) printed "ok tools/audit/seat/roster_lib.py --self-test passes" and ALL 2319 ENTITY CHECKS PASSED.

## Attacks (step 6)
- A, text sort: newest_roster over r9, r10, r11, r1 and an r100 .bak returns wave-r11. Integer comparison, and non-rosters are ignored.
- B, wave-r10 on the checkout but absent at the ref: roster_path(ref) gives r9 and roster_path(disk) gives r10. Every ref reader stays on the ref's tree: plan_table at origin/main lists R9-A and not R10-A, and state_docs derives round 9. Disk and ref are never mixed.
- C, an override naming a missing file:
  - roster_edit rc 2 REFUSED, state_docs rc 2 REFUSED ("which round"), tick `UNREADABLE: roster at origin/main:nope.json`.
  - plan_table, resume_doc and handover_prompt exit rc 1 with an uncaught RosterNotFound traceback. That is loud but untidy (residual, below).
- D, roster_edit with no ref or branch arguments, using --push, in a throwaway origin:
  - main carrying only r9: lands on handoff/audit-r9-roster, main unmoved.
  - an r10 group in that state: REFUSED rc 2.
  - main carrying r9 and r10: lands on handoff/audit-r10-roster, main unmoved.
  - Residual, unchanged from base: an explicit `--roster-ref main` with no `--branch` still targets main. This is documented, and the ruleset refuses the push.
- E, state_docs write set: a dry run at origin/handoff/audit-r10-roster gives handoff/audit-r10-plan. Its commit tree is exactly handoff/round10/state/{NEXT-SESSION-PROMPT,PLAN-TABLE,RESUME-CURRENT}.md (no previous tip). The default origin/main still derives round 9 until the round-10 roster merges to main, which is the stated design.
- Class (step 6): I ran the body's grep rule at the head: 39 hits in seat tools, all fixtures, docstrings, or prune_refs' archive-tag example. Tree-wide, ROSTER_PATH and LEGACY_ROSTER_PATHS appear only in the tests.yml record-autofix comment, line 3908. Every roster reader goes through roster_lib (roster_edit, orchestrator_tick, state_docs, plan_table, resume_doc, handover_prompt, record_row, and prune_refs via DONE_STAGES and branch_of).

## Gate and instruments
- Every required check (17, ruleset 23698884) is success at f3cbd393, read through the commit check-runs API. No check went red, so step 11 has nothing to answer.
- closures: the Linux recording lists dev/audit/harnesses/r10_tick_which_roster.py in harness_headers.py's recorded inert_reads, the same entry the PR added by hand. check.txt's last line is "closure: committed closures cover every file this run touched". closures-autofix was skipped, with no commit to make.
- Unrelated: in that recording run, harness_headers.py exited 1 on round4/D7/sysid_estimator_frontier.py's CPU bound (288s against 240s) under tracing. fast's own harness_headers run passed 109/109.
- Local: closure select gave MODE: SCOPED -- 2 script(s) run, 31 scoped out. structure.py: STRUCTURE RATCHET PASSED. archscore --diff: dS +0.0000 NULL. harness_headers: 109 passed.
- Step 14: no *_budgets.json, VERSION, manifest, notes heading or claim file is in the diff. The one instrument move is the closures inert_reads entry, and CI's own recording reproduces it, so the new harness earns it. Removing the harness would leave the entry dangling, not gamed.
- Step 10, forward-carry: the R10-TICK-ORCH brief at handoff/audit-r10-roster (2298eb73) carries the tests.yml ROSTER_PATH comment fix and keeps items a and c open.

## Residuals (not blocking)
- tests.yml line 3908 comment names the removed roster_lib.ROSTER_PATH. It is code-owned and routed to TICK-ORCH.
- plan_table, resume_doc and handover_prompt do not catch RosterNotFound, so they print a traceback where the other tools print a REFUSED line.
- An explicit `--roster-ref main` with no `--branch` still targets main.
