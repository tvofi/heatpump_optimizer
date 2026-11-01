Fix review: merge b8ecad2dc4c5cd112a80eb3d4d5532f3e801d511

bus-nonce: 86f85dc43e852117688e10611717cf94

## Summary

Round 2 of the fix review for #3097 (R10-PLAN-REAL-DURATIONS). Round 1 blocked 3fd85299d on `mutation-survivor: theil-sen-ordered-pairs`. The repair is commit 4d6244659 (2 files, +7 lines): a row-order arm in `size_durations.py --self-test` (the 5.5 h fixture given ascending, reversed and shuffled) and the mutant `theil-sen-ordered-pairs` in `dev/audit/harnesses/r10_plan_durations_mutants.py`. Both later commits are clean merges. The round-1 survivor is now killed, every planted mutant is killed, and CI is GREEN at this head.

## Findings

- The body's `## Red checks` gives the right answer, `none`, for the wrong head: it counts the 55 check runs at the previous head 3fd85299d and says this head's checks "have not run". They have now run. At b8ecad2dc there are 55 check runs, none red, and both `pr-contract` runs are green (ev/checkruns.txt). So the conclusion holds, but the paragraph should be re-taken from this head's own runs when the body is next edited. Carry: R10-PLAN-REAL-DURATIONS

## Evidence

- Head reviewed: b8ecad2dc4c5cd112a80eb3d4d5532f3e801d511 (ev/HEAD.txt), from detached worktrees at this head and at the round-1 head 3fd85299d. The PR head ref and refs/pull/3097/head were re-read before writing and are still b8ecad2dc. The contract is current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Delta since round 1: `review_carry.py 3fd85299d b8ecad2dc` prints FRESH-REVIEW (one code commit), so this is a full re-review (ev/review_carry.txt). 271403e9d has the same tree as 4d6244659 (73844385c). b8ecad2dc's tree be4d2873e is identical to the automatic `merge-tree` of its parents, so the merge has no hand resolution. `r10_away_presence_listener.py` is in the two-dot range only because main brought it (it is identical at d052f80f7). The new commits touch nothing outside the repair (ev/delta.txt).
- Merge with origin/main (ca6333333): `git merge-tree --write-tree origin/main b8ecad2dc` exits 0. Only the LEDGER-MERGE driver ran, on tests/closures.json (resolved). No claim-file driver ran (ev/merge_tree.txt).
- Finder's harness (round-1 reviewer's own instrument, rebuilt here as mine/rev_mutants.py, disclosed as mine and not landed), at both ends (ev/reviewer_mutants_old.txt, ev/reviewer_mutants_new.txt):
  - At the old head: `theil-sen-ordered-pairs` rc=0 verdict=SURVIVED. This reproduces the round-1 block.
  - At the new head: R0-null rc=0 fails=0.
  - Killed at the new head: pctl-scale, theil-sen-p75, theil-sen-ordered-pairs (rc=1, 1 FAIL, the row-order arm), theil-sen-descending-pairs (my addition, `k2 < k1`), rounds-not-added-back, carry-baseline-p75, per-carry-unadjusted, active-gap-merged and min-cell-6.
  - My own plant on the new arm (the fixture's reversed and shuffled rows replaced by ascending ones), as controls: the fixture change alone passes rc=0, as it should, since it changes no production line. With the ordered-pairs production mutant added on top, it passes rc=0 too. The kill therefore comes from the unsorted rows and nothing else.
  - Keeping only the reversed rows, or only the shuffled rows, each still kills the production mutant (rc=1).
  - Production-line survivors at the new head: 0. The two passes the script counts as `reviewer-survived=2` are these fixture-only controls.
- Fixer's harness, as evidence: `r10_plan_durations_mutants.py` at the old head prints M0 null and 19 killed. At the new head it prints `RESULT mutant=M0 rc=0 fails=0 verdict=null`, then 20 named mutants `verdict=killed` rc=1, including `theil-sen-ordered-pairs` (fails=1), then `RESULT survived=0`, rc=0 (ev/harness_old.txt, ev/harness_new.txt). I counted 20 `RESULT mutant=` lines less M0. That matches the body's "twenty one-occurrence replacements" and its list of names.
- Body figure re-derived by hand: shuffled rows (3,2),(1,0),(4,30),(2,1) under `k2 > k1` keep the slopes 28, 10 and 1, median 10. Reversed rows keep no pair, so the slope is 0.0. Both match the body.
- Self-tests at the head: `size_durations self-test: 0 failed`, `self-test: 0 failed` (replan.py) and `plan_page self-test: 66 checks, 0 failed`, each rc=0 (ev/selftest_*.txt).
- Model figures: `tools/plan/durations.json` has a zero-line diff between 3fd85299d and b8ecad2dc. The fixer did not re-take them, so round 1's re-derivation stands.
- Ownership: the body names group R10-PLAN-REAL-DURATIONS at origin/handoff/audit-r10-roster 5229384ba. That commit exists and is an ancestor of the current tip c4918c9ff, which has no diff to the group. The group there has size M, wave 1, fixer sonnet / reviewer opus, after R10-PLAN-ARTIFACT and R10-ORCH-PLANPAGE, the four named files and resume branch handoff/r10-plan-real-durations, all as the body states (ev/roster_group.txt).
- Standing checks:
  - Delivery row dev/programme/delivery/3097.md is in the three-dot diff (ev/files.txt).
  - Claim files, VERSION, manifest and RELEASE_NOTES.md are untouched (grep count 0).
  - `tests/structure.py` prints `STRUCTURE RATCHET PASSED` rc=0.
  - `closure.py select --diff d052f80f7` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (ev/closure_select.txt).
  - `carry_audit.py --roster-ref origin/handoff/audit-r10-roster pr 3097` prints 0 items, rc=0 (ev/carry_audit_pr.txt).
  - No added line matches a host path (ev/privacy.txt, empty).
- CI at this head: `merge_train.py classify b8ecad2dc...` exited 0 at 18:22:02Z: `GREEN ... pending: none red: none` (ev/classify.txt, ev/classify.log). There are 55 check runs, all success or skipped. The `pr-contract` runs finished 18:18:05Z and 18:21:05Z, both green (ev/checkruns.txt). I cited CI's heavy lanes and re-ran none.
