Fix review: merge 40683e8d7dcae31c6958434d9606682fcd7141f1
bus-nonce: 5aeeb606b950b717cc46bfc0e3c5dab6

R10-STRUCTURE-BLIND (#2340). Reviewed adversarially from a fresh detached
worktree at the head, per fix-review.md. Every figure below is my own re-run at
this head; RESULT lines are in the evidence dir. The corpus re-measure
(`calibrate.py --measure-corpus`) is a heavy run (87 stored trees via git
archive); I did not complete it locally — I cite CI's `arch-score` check
(success in the head's check-runs) and my `score.py --diff origin/main` for
corpus/expected.json consistency, per fix-review.md's "cite CI's heavy runs".

## Verdict: merge

All five dispatch checks pass, and every fix-review step that binds a reviewer
here passes.

### (1) Budget re-record is a genuine improvement, not gamed (step 14)
`budget_raise_gate.py --base d7b171229 --head HEAD --pr 2340` -> `RESULT
budget_raises=0 count`, PASS. `class_excess_loc` 18468 is honestly earned by
#2336's coordinator shrink, measured at both ends: pre-merge authored head
`b3090df34` reads coordinator 8688 LOC / 410 helper lines / class_excess_loc
18498; the head reads 8635 LOC / 431 helper lines / class_excess_loc 18468,
with `sysid.py` SystemIdentification 1063 -> 1065 (+2). Delta -30 = (-53 span)
+ (+21 helpers) + (+2 sysid). The PR's own dead-member deletions (drift.py -4,
inputs.py -21) are present in both trees, so they contribute 0 to that -30; the
-30 is entirely the #2336 main merge. archscore reads the deletions as
IMPROVEMENT (dead_members 5->1, duplication_copies 66->65), never worse. Not
gamed.

### (2) Structure-blind fix: harnesses both ends + mutation proof
- class_growth.py (D7-s1-01): base `keys_moved_second_class=0`,
  `keys_moved_coordinator=1`; head `=1` / `=2`; `lines_added_per_arm=1201`.
- namekept_receivers.py (D7-s3-01): flat both ends, `candidates_with_zero_typed_hits=6`,
  `total_typed_hits=0`.
- Companion `dev/audit/harnesses/r10_structure_blind.py`: all three arms match
  the body's table (head 0/2/4 dead; merge-base package 4/2/0; base census 0/6,
  name_kept 153).
- Mutation proof re-executed on `tests/structure.py` (sha1 56c81605... before
  and after): M0 `STRUCTURE RATCHET PASSED`; M1, M2, M3 each red with exactly
  1 / 1 / 3 counting-rule breaks and rc 1; M3 on the merge-base package reads
  `six_measured_dead=0`, `six_name_kept=6`.

### (3) No other budget metric moved; ratchet passes; dS correct
Only `tests/structure_budgets.json` (class_excess_loc added 18468,
duplication_copies 35->34, recorded_at -> d7b171229) and `tests/closures.json`
(one inert_reads line for the new harness). `STRUCTURE RATCHET PASSED`.
`score.py --diff origin/main` -> `dS +1.7787 IMPROVES` (dead_members 5->1,
duplication_copies 66->65), no metric up.

### (4) Red checks
Head check-runs: `fast (3.14)` = success. The body's "## Red checks" names
`fast (3.14)` and answers it (the unrecorded improvement; the re-record is the
fix); arch-score passed in CI.

### (5) VERSION / manifest / notes untouched
Confirmed (empty diff for VERSION, RELEASE_NOTES.md, manifest.json).

## fix-review steps
- 0 roles current (only nudge.md differs on main, irrelevant).
- 4 claim files byte-identical; env_drift.py --all -> NO UNCLAIMED DRIFT, NO STALE FIXTURE.
- 6 class open: enumerator seams=10, instances=5, every seam disposed in the body.
- 7 head SHA in body == measured head 40683e8d.
- 9 harness committed in-tree (not out-of-tree).
- 10 forward-carry: in the tree at dev/programme/rosters/wave-r10-groups.json
  R10-ARCHSCORE-COVERAGE carry (added on main), carrying the control and the
  precondition.
- 11 red checks answered and head green.
- 13 merge-tree origin/main + head -> exit 0, no conflict.
- 15 architecture sound: production change is pure dead-code deletion; the added
  lines are measurement code in tests/ and the harness; no architect note set.

## RESULT lines
RESULT budget_raises=0 count
RESULT class_excess_loc=18468 count
RESULT max_class_loc=8635 count
RESULT dead_methods=0 count
RESULT duplication_copies=34 count
RESULT structure_ratchet=STRUCTURE RATCHET PASSED
RESULT dS=+1.7787 IMPROVES
RESULT mutation_M0_M1_M2_M3=PASS(1/1/3 rules broken, rc 1)
RESULT keys_moved_second_class=0(base)->1(head)
RESULT keys_moved_coordinator=1(base)->2(head)
RESULT candidates_with_zero_typed_hits=6 flat both ends
RESULT six_measured_dead=4 on merge-base package (vs 0 for the base census)
RESULT seams=10 instances=5
RESULT env_drift=NO UNCLAIMED DRIFT, NO STALE FIXTURE
RESULT merge_tree=clean exit 0
