Fix review: merge 775191091567676376bf2e5c69d67e7182c322a5
bus-nonce: d7242dd0662edfd76c56318eb0681252

# Fix review -- PR #2106 (R9-RO-PC1), one census arm in tests/doc_claims.py

Reviewed from a detached worktree at
/Users/timmalmstrom/hpo-seats/r9-review-2106/head, head
775191091567676376bf2e5c69d67e7182c322a5, on 2026-10-10. Round 1.

## Head
`git diff --name-status 090a4067 775191091` prints exactly one added row,
`dev/programme/delivery/2106.md`; the reviewed code head 090a4067 is unchanged.
Head is still 775191091 (pulls/2106 head.sha). merge-tree
`git merge-tree --write-tree origin/main 775191091` -> rc 0, no conflicting path.

## What I built (mine, not the fixer's)
`/Users/timmalmstrom/hpo-seats/r9-review-2106/harness/plant.py` and
`harness/perturb.py`: they drive the head's `doc_claims` module directly and
plant at the row spans `prose_count_scan` returns.

## RESULT lines (my harness)
RESULT coverage: 17 rows over 11 shapes all presently read; plant +1 at each
  row -> the row fires. All 11 shapes load-bearing.
RESULT six-instance coverage (the LANE's own RCA six unprotected instances,
  planted +1 and run through the arm):
    READ   README.md        'all 31 fields'          -> fields_of_set_thermal_parameters
    READ   configuration.md 'the 23 options pages'   -> options_pages
    READ   setup.md         'the 23 options pages'   -> options_pages
    READ   README.md        '22 you can edit'        -> editable_options_pages
    BLIND  dashboard-card.md'its five pages'         (word-spelled)
    BLIND  ecl110.md        'All eight settings'     (word-spelled)
  4 of 6 covered; the 2 blind are exactly the "count spelled as a word" limit
  the body and the I5.barrier Not-reached clause both name.
RESULT perturbation per quantity: for each of the 7 quantities the arm reads,
  plant_live=RED and plant_shape_neutralized=green -- each comparison moves
  under its own removal. (check_prose_tree_counts, no per-shape silence.)
RESULT M1 re-run (delete the comparison): with the plant present the main
  check FAILS; with `measured := stated` (M1 `wrong = []`) the same planted
  tree is fully green. The red comes from the comparison and nothing else.
RESULT null control on unmodified origin/main corpus: 9 ok / 0 fail; head
  corpus 9 ok / 0 fail. The reader corpus is byte-identical to origin/main
  (sha256 4444839ac0aa716d, 12 files) so main's corpus reads green too.
RESULT fail-closed: delete architecture.md from CORPUS -> 1 FAIL, "no
  occurrence of" the 5 module shapes. Refuses, does not pass by reading less.
RESULT layout guard at head: `python3 tests/layout.py --guard --base origin/main`
  -> `0 refusal(s)` rc 0. At dc1abe654 the same command -> `2 refusal(s)`
  (placement: prose_counts_census.py unclassified; new-reference: retired
  tools/audit/harnesses/), so the body's failing-first answer is accurate.
RESULT full arm run at head: `python3 tests/doc_claims.py` -> ALL 169 checks
  PASSED (9 added by this diff; 160 at origin/main).
RESULT census at head: seam_rows=161 nouns=27 refused=0 dead=0 (body matches).
RESULT fold_ledger check: 28 classes, 549 instances, 102 rca entries,
  0 violation(s); self-test ok. RCA doc present and cited.
RESULT structure ratchet: PASSED. VERSION / manifest / RELEASE_NOTES / both
  claim files: byte-identical to origin/main (empty git diff).
RESULT budget: tests/doc_claims.py is in neither `files` nor `roles` of
  dev/governance/config/policy_budgets.json (claim confirmed).

## Required contexts (ruleset 23698884), at 775191091 (check-runs API)
16 of 17 present-and-success; 1 present-in_progress (`Analyze (python)`, CodeQL,
  no conclusion yet); 0 absent; 0 red. `fast (3.14)` is success at this head.
  The only branch HEAD whose `fast (3.14)` went red is dc1abe654 (failure),
  which the body names and answers with the cheaper `tests/layout.py --guard`
  (~0.4 s CPU); I reproduced that refusal. Red-check trigger answered.

## Moratorium (0012)
Agreed with the body: one arm added to an existing test script that already is
the I5 barrier, no new policy file, no new `.claude/rules/*`, no new lint class
-- the barrier's unit extended from the sentence to the shape (root-cause.md
§2). No owner stop is triggered.

## Instance vs shape (the overstatement risk)
The arm covers the SHAPE across the corpus and, measured, 4 of the lane's 6
unprotected INSTANCES; the remaining 2 are word-spelled and named as a limit.
The body states this limit; it does not overstate the coverage.

## What I could not re-derive
The 358.8-minute defect cost and the exposure counts are the RCA seat's
artifacts, not re-derivable at this head; I did not re-take them. They are not
this PR's gate figures and the countermeasure's own cost (250.3 ms CPU) is an
order of magnitude below them either way.
