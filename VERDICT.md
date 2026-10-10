Fix review: merge 7706b39a16e782236b61e5d6de5cb8e6f691cd8b

bus-nonce: 424c9844dba7da9f0d9c328407906262

Independent adversarial review of the CURRENT head (round 10 re-cut). I wrote no
production code and pushed nothing to the branch. All numbers below are my own
re-runs at the head; my evidence directory is
/Users/timmalmstrom/hpo-seats/r9rev-2066/ev/.

RESULT head_measured=7706b39a16e782236b61e5d6de5cb8e6f691cd8b
RESULT merge_base=1301d7e45df08bc224d420db4508195050b88972
RESULT origin_main_is_ancestor_of_head=NO (live main c729bb32e is 16 commits past the merge base; the body's "both the pull request's live tip and live origin/main are ancestors" was true when written, not now -- drift, not a defect)
RESULT production_delta_over_main=239 added / 53 removed over 6 files (two-dot and three-dot agree)

## 1. Mutation proof -- RE-RUN, and not vacuous

I applied the three mutants the body names to the head tree (accuracy.py
MeasuredCop.judge_ratio) and drove the real tests/features.py at each:

RESULT mutant_M11 no_evidence_branch_folds_always = 4 FAILED (control 1); the named check "with no draw evidence a departure folds only past the nameplate third: it waits for evidence on 14 kW and folds on 4 kW, as base" FAILED [1 (None) / 1], and the named off-ask check FAILED
RESULT mutant_M12 no_evidence_branch_refuses_always = 9 FAILED (control 1); the same named check FAILED [0 (awaiting_draw_evidence)]
RESULT mutant_M13 draw_does_not_follow_made_to_fold = 2 FAILED (control 1); the named check "a draw that ignores the ask (varying or flat) is refused as off-ask; a matched draw and a 0.7 shift on a draw that follows its ask still teach" FAILED
RESULT mutation_control_features_at_head = 1 of 4014 FAILED, the single known macOS BLAS float R9-F2.1 P3 [shipped 110.4366, seeded 110.1297]

Every mutant kills a check that names the line it mutated; nothing survives.
The named checks are not vacuous. (The body said the head's features.py run was
killed by the box and never measured; I measured it: 1 of 4014, the BLAS float.)

## 2. The finder's harness -- the finding committed none; I re-ran what exists

The in-tree harness dev/audit/harnesses/cop_duty_floor.py says in its own header
"Written by the #2066 fixer, not by the finder: the live-install finding
committed no harness", and the body calls it "the fixer's harness". That is the
disclosure fix-review.md step 9 requires, in the file and in the body, so this
is soundness-by-disclosure and not a defect. I re-ran it anyway, plus every
out-of-tree instrument the body quotes.

RESULT finder_harness=absent (fixer's, disclosed); my re-run at head rc=0, 31 RESULT lines, `diff` of RESULT lines vs the fixer's ev/r9/harness_final.out and ev/r10/harness2.out is EMPTY
RESULT harness_min1_running=0/15 base -> 15/15 head
RESULT harness_min3_running=0/15 -> 3/15
RESULT harness_selfmod_matched=0/96 -> 96/96 at 1.000
RESULT harness_selfmod_independent=1.000 -> 0.976
RESULT harness_selfmod_independent_4kw=0.636 -> 0.780 (orchestrator-accepted residual; carried)
RESULT harness_true_cops_head=0.604 / 0.704 / 0.805 / 1.307, true_0.7_4kw=0.704 at both ends
RESULT harness_fixed3_duty50_duty70=5/5 -> 0/5 (the disclosed behaviour change)
RESULT probe5_selfset 1.000/1.000/1.000 -> 0.978/1.000/1.000 (round-2 reviewer's probe, re-run by me)
RESULT probe6_matched 356/400 -> 400/400 at 1.000; selfset_hourly 1.600 -> 1.170; partial_b0.3 1.600 -> 1.375; heat-led 0.7 rows within 0.002
RESULT probe7 0.751 -> 0.751, 0.750 -> 0.750, 0.750 -> 0.749
RESULT probe3b_pmax4 0.636 -> 0.590 (the disclosed in-tolerance regression direction)
RESULT probe3_independent 1.000 -> 0.976; probe4 p4 rows 1.028 / 1.123 / 0.563 / 0.998

Every base->head figure the body quotes reproduces at my own two baselines
(#2065's head 9b39bb7c6 and the merge base 1301d7e45 -- the harness reads
identically at both, so the fix is what moves the numbers, not the base).

## 3. Null controls and both-ends

RESULT null_harness_matched_draw=0/96 -> 96/96 at 1.000 (the row that must hold, holds)
RESULT null_probe6_matched=356/400 -> 400/400; null_probe6_selfset_flat folded=0/400 both ends
RESULT null_probe6_heatled0.7_unchanged=0.707/0.706 -> 0.707/0.705, 0.686 -> 0.688, 0.700 -> 0.700 (within 0.002)
RESULT null_harness_own_liveness=liveness_folded=3/3 at both ends

## 4. Claim files, VERSION, drift

RESULT claimed_drift_sha1=10169742b92c06960fbcd3987ccc46f970104415 (head = origin/main)
RESULT card_claimed_drift_sha1=7b50a0c5d73d435fd719abb853fba4418351f183 (head = origin/main)
RESULT golden_diff_origin_main_to_head=empty (this branch claims nothing)
RESULT env_drift_all=NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main; NO STALE FIXTURE: 56 committed fixture(s) still match
RESULT VERSION=6.7.17 at head and at main; manifest version=6.7.17 at both; RELEASE_NOTES heading="## v6.7.17" at both; branch touches none of them

## 5. Class-open, forward-carry, red checks, merge state

RESULT rederive_added_unpinned=0 added_keys=0, unpinned 4593 <= base 4608, ratchet_refusal None, pin_shard_count 1, validators all [] (reproduced with the round-9 reviewer's own probe, WT repointed at my tree)
RESULT rederive_pool_not_charged=2: coordinator.py:4562 CMP_BOUND + GUARD_OFF, anchor 6deb0603 -- both inside the diff's hunk region and both dispositioned in the body (## Unpinned sites / ## Forward-carry); no returned seam is neither in the diff nor dispositioned
RESULT carry_2066_and_2065=brief_lint 0 error(s) / 0 warning(s) on each; carry-2066 states the precondition and carries the control (probe6 selfset_hourly 1.170, harness selfmod_independent_4kw 0.780) with nulls selfmod_matched and true_0.7_4kw; carry-2065 to 7b likewise with min3_running_folded 3/15
RESULT range_reds_enumerated_by_me=28 rows over exactly 6 names in 35 commits, 0 read failures: mutation 13, nightly-status 7, fast (3.14) 3, nightly-ha (stable) 2, briefs 2, nightly-ha (2025.2.0) 1 -- exactly the body's enumeration; the body names and answers all six (cheaper detector + standing cost, or the stated grades-outside-this-diff refusal)
RESULT head_check_runs_now=35; fast (3.14) completed SUCCESS at this head; coverage SUCCESS; closures SUCCESS; mutation IN PROGRESS at publish (job timeout 160 min); no gate check red at this head
RESULT merge_tree_write_tree_origin_main_head=rc=0, no conflict; no MERGE-CLAIM/LEDGER-MERGE marker needed. The round-9 `conflict` block is genuinely resolved, and the head also merges clean against the NEWER live main

## 6. Metric-gamed, architecture

RESULT structure_ratchet=PASSED rc=0, every metric at measured
RESULT structure_budget_moves=all DOWN vs main (coordinator_attrs 153->151, coordinator_multiassigned 120->118, max_class_loc 8818->8808, seam_cut_total 762->760); no raise sought, budget-raise-gate green
RESULT budget_move_null_control=the PRE-fix tree (merge base) measures 153/120/8818/762 -- so the decrease is caused by this change, not by the instrument
RESULT arch_added_lines=sound: one owner per concern (MeasuredCop and the COP_REFUSED_* codes in accuracy.py, follows_ask in draw_range.py, the floor in thermal_model.py), no homeassistant import added to any learner/model module, judge_* are pure functions with the evidence passed in, missing input refuses or returns None rather than guessing, and it extends the existing store-domain, diagnostics-_VIEWS and _fold_measured_cop mechanisms rather than adding a parallel one

## 7. Numbers I could NOT re-derive -- recorded, not confirmed

Per fix-review.md step 8, these are body figures that do not reproduce at this
head. They do not change any conclusion, so the verdict is not blocked on them,
but they are not verified either:

- "**14 hunks, 349 added lines, 30 removed**" for `diff -u <(git show origin/main:tests/features.py) tests/features.py`. At the head it is **14 hunks, 384 added, 30 removed** (`git diff --numstat` reads 384/30 against origin/main, against the merge base, and against 7cd5a588c alike; no ref in the range gives 349). The body's own breakdown -- the 351-line COP hunk plus "13 small ones" (which sum to 33) -- is the 384 figure, so 349 is a slip in one number, not a wrong measurement.
- The same sentence's "its hunk 359 with context": hunk 14 is `@@ -60477,6 +60480,357 @@`, i.e. 357 new-file lines.
- "`CI PREDICT: no closures or fast red predicted against 7cd5a588cbbb`": at this head the same command prints `against 1301d7e45df0`, the head's merge base. The substance (rc=0, one line, no "unpinned sites the diff adds" warning) reproduces exactly.
- "`tools/pr/ci_predict.py` ... **6.1 s**": on this (loaded) box the same command is 12.9 s wall / 4.2 s user. The standing cost is "seconds" either way; the quoted figure is a capture from an earlier base.
- "No check has run at this head yet": false now -- the head carries 35 check runs, and `fast (3.14)` is green at it.

Everything else the body quantifies that I could reach, I reproduced: the 239/53
production delta; the union proof (R.check( 3625 = main's 3602 + 23; 0 main names
lost); the census (33 scripts / 528 pairs / 29 / 406 comparable / 123 at >= 0.80 /
18 at exactly 1.00 / 93 files / 75 modules, and 120/18 at d8a4bd36f); the
four-tree debug_collect control (59/74 = 0.7973 -> 60/75 = 0.8000); the HA-boundary
rule (75 / 27 / 28 / 47); claims.py 125 / 123 / 0-false / 2-unverifiable and
75 / 75 / 0 / 27; entities.py ALL 2250 PASSED; structure PASSED; closure selftest
57; guard_pins 50; layout ok; deployment_shape PASSED; brief_lint rc=0 with 0
findings on both carry files; the corpus `--normalize` identity (1406
dispositions); and that every one of the 30 lines the features.py merge removed
names a symbol this fix renames (`grep -vc` = 0).

The docstring-provenance correction at 025b779c4 is real and the four-tree control
for it reproduces: the "+3 debug_collect pairs" clause moving from #2066's merge
to #2065's is a corrected cause, and the numbers beside it are unchanged.

## Residuals the body discloses and I confirm

- The self-setting-pump departure folds before follows_ask has evidence: probe6
  selfset_hourly 1.170 (right 1.000), harness selfmod_independent_4kw 0.780
  (right 1.000), probe3b 0.590 at 4 kW. Carried as a precondition to fix 3 in
  dev/programme/carries/carry-2066.json, with its control and nulls.
- Fixed-speed pumps with min > 0.375 x max lose their 50 %/70 % duty-averaged
  intervals (harness fixed3_duty50/duty70 5/5 -> 0/5). Disclosed in the body.
- The two-site drive pool at coordinator.py:4562 is the branch's own disposition
  and is stated as such, not deferred to mutation-autofix.
- The `briefs` recurrence (twice in round 4) is answered in the body with its
  cheaper detector and standing cost; the root-cause seat it owes (dev/audit/rca/)
  is recorded as owed, not written. fix-review.md step 11 asks whether the trigger
  was answered, not whether the answer is complete, so this does not block.

## Verdict

merge. The proof is non-vacuous, every quoted figure I could reach re-derives,
the claim files are main's own bytes, no budget moved up, the merge is clean
against live main, and the head's heavy lane that has finished (`fast (3.14)`)
is green. The four stale figures in section 7 are recorded above rather than
confirmed, and none of them carries the soundness argument.
