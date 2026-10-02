Fix review: blocked 53017884ee943bef9d961d59de788e7178fd9c15 honesty: fold_ledger.py and prepr.sh say the lane runs the base's pinned copy, but it runs the branch's own; two stated refusals unpinned; nightly-status red unanswered in the body
bus-nonce: ff28a5a7402da04d2795972108aa456c

Round 1. Reviewer: fix-review seat for #1862 (R9-EG-R1). This verdict covers head 53017884ee943bef9d961d59de788e7178fd9c15, measured from a detached worktree at that SHA. The PR body names the same head (step 7). Merge base aa7a81192. `git diff <mb>...origin/main -- tools/audit/briefs/` is empty, so this contract is current.

## Blocking

1. **The checker's ownership weakness is stated falsely in the tree (dispatch item 5).** The body's "Design points", the `governance.yml` comment and the `CODEOWNERS` comment all say it honestly: the lane runs the pull request's own copy, and only ownership protects it. Two in-tree statements say the opposite, left over from the first, pinned form:
   - `tools/audit/fold_ledger.py:41-44` (docstring): "the lane runs the base's copy of this file against the pull request's tree (--root), so a branch cannot edit the grader it is graded by."
   - `tools/audit/prepr.sh:1239-1240` (step 3f5): "which `wave-script` runs from the base once the base carries it".
   The wave-script lane's restore step in `governance.yml` (around line 459) restores `tools/audit/*.sh` and named files from the base, but not `tools/audit/fold_ledger.py`. The lane then runs `python3 -I tools/audit/fold_ledger.py check`, which is the branch's copy. A later seat that reads the checker's own docstring will believe a protection exists that does not. Fix: rewrite both sentences to match governance.yml (the branch's own copy, protected by CODEOWNERS), so the weakness is stated in every place.

2. **Two refusals the PR states pass the self-test when mutated (step 1).** I built 9 mutants of my own; 7 turn the self-test red and 2 survive:
   - `if _has(u.get("reason")):` -> `if True:`. A survivor in `_unclassified` with an empty reason then counts as placed. The body's forward-carry says "each `_unclassified` row R9 adds needs a reason (the check requires one)", but no expectation pins that.
   - `_intree` loses `rel.startswith(RCA_DIR + "/") and`. An `in_tree_home` naming an existing file outside `tools/audit/rca` is then accepted. The docstring and `defect-root-cause.md` both name `tools/audit/rca` as where the document must be.
   Fix: add two expectations (an `_unclassified` row with an empty reason is UNPLACED; an `in_tree_home` naming an existing file outside `tools/audit/rca` is DANGLING), and show each red under its mutant.

3. **root-cause-unanswered: pr-contract and nightly-status went red, and the body does not answer them (step 11).**
   - pr-contract (check-run 110994412635) fails with `PR-BODY: 1 error(s)`: "check `nightly-status` is red and `## Red checks` does not name it ... this diff touches what it reads (.github/workflows/governance.yml)".
   - The body's `## Red checks` still reads "none. No CI run exists for this head yet". This diff edits governance.yml, so the body check voids the not-this-PR exemption, and the body owes a named answer for nightly-status.
   - Fix: re-take `## Red checks` to name nightly-status and budget-raise-gate. For nightly-status, give the evidence it is main-wide: #1856's head a8bba2e6 carries the same red, and its job lives in tests.yml, which this diff does not touch.
   - The preflight line `REFUSE 'Fixes #1759' ... not in the intended list` runs under `|| true` and is advisory. `Fixes #1759` was already ruled under the mandate.

## Verified

- **Register demonstration (item 1).** I ran the PR's checker with `--ledger`/`--judge` taken from each ref, and the finder's harness `bulk2/register_check.py` (from c5c32f2b) with `register/register_rows.tsv` (486 rows) at the same refs:
  - RESULT check ref=3490cb16 rc=1: 195 violations (39 UNPLACED, 12 OWED, 17 UNPARSED, 127 DRIFT). Finder's harness: 186 rows in no class, 12 OWED.
  - RESULT check ref=9d52e5a11 rc=1: 159 violations (39 UNPLACED, 15 OWED, 105 DRIFT). Finder's harness: 201 rows in no class, 14 OWED.
  - RESULT check ref=948671af1 (R0-v2) rc=1: 93 violations (79 DANGLING, 10 DRIFT, 4 OWED: P4, P8, P10, N-name-sort). Run with the head's rca directory, as the body says.
  - RESULT check ref=53017884 rc=0: 0 violations; 28 classes, 549 instances, 39 in-tree survivors (round 8 only), 95 rca entries.
  - At the head, the finder's harness reports 10 rows in no class and OWED []. All 10 are reasoned `_unclassified` (7) or `_excluded` (3) entries. The harness predates both buckets, so this is not a defect.
  - Scope note: `check` reads in-tree JUDGE.json only, so round 8 is the only round it validates today. R1-R7 and R9 survivors are not checked. The body says this for R9.
- **Perturbation at the head (item 1).** Each RESULT names the perturbation, the exit code and the violation count:
  - RESULT perturb=drop-one-R8-instance rc=1 3 (UNPLACED)
  - RESULT perturb=R8-instance-in-two-classes rc=1 3 (DOUBLE)
  - RESULT perturb=P4-rca-removed rc=1 2 (OWED)
  - RESULT perturb=in_tree_home-dangling rc=1 1 (DANGLING)
  - RESULT perturb=carried-total+1 rc=1 1 (DRIFT)
  - RESULT perturb=unclassified-without-reason rc=1 3
  - RESULT perturb=null-unchanged rc=0 0
- **Self-test.** 28/28 ok locally, under Python 3.14. Mutants that turned it red: no isfile, total-5 arm, window off-by-one, barriered_any, UNKNOWN-RCA, UNPARSED, fold idempotence.
- **check-wave-script.mjs.** 160 passed. The mutant where N ignores beyond_finding turns 1 red, matching the body's claim.
- **Data (item 2).**
  - Trigger: exactly 10 classes changed, `barriered_any` only, False to True, and every one is status `barriered`: P1 P2 P3 P6 P9 I1 I2 I5 N-solve-recompute N-structure-blind. No other class field changed.
  - `_rca`: 80 dangling entries are now 13 repointed + 66 nulled + 1 resolved by the added document. Nothing else in `_rca` changed. All 16 non-null homes left unchanged exist.
  - All 13 repoints spot-checked: each target `RCA-BULK-{1,2,3,4}.md` exists and covers its subject (P4/P7/P8/P10; I2/structure-blind/R-register; 1721/1545/1070/v6.6.0 freeze/1041; name-sort).
  - `tools/audit/rca/R9-N-solve-recompute.md` is blob 13628872b4ef. At 763b0ba4, `handoff/round9/state/rca/avoidable-interpreter-bound-recomputation/RCA.md` is the same blob, so the file is byte-identical, and that path is the one the entry's own `doc[0]` cites.
- **Policy clauses (item 3).** Each matches RCA-BULK-2 section 3.4 at c5c32f2b:
  - `judge.md`: (ii) reuse before minting; a class is a mechanism, never a site; nearest and differs; two sharing a nearest count as one.
  - `defect-root-cause.md`: (iii) the window arm and the 5-while-open arm, and (v) "Where it is recorded". The one extra sentence names `fold_ledger.py check` as the lister.
  - `D8.md` step 3: the declared-families line (#1760).
  - Nothing else changed in policy. `.mdc` is regenerated: `rules_sync --check` is ok, and `policy_lint` reports 0 errors.
  - Non-blocking wording gap: the policy says "five while it is open" but the code tests `status != "barriered"`. That differs for status `detector` (P4, 18 instances), which already meets per_round, so no outcome changes today.
- **Caps (item 4).** `policy_lint --budgets` at the head gives defect-root-cause.md 150/150 lines and 1848/1848 tokens, D8.md 56/56 and 808/808, judge.md 30/30 and 469/469. The raised caps equal the measured values exactly, and all five aggregates are inside their band.
  - Interaction with #1856 (open, head a8bba2e6): `git merge-tree` auto-merges defect-root-cause.md and the .mdc, but **conflicts on policy_budgets.json**. #1856 sets the cap to 149/1813; this PR sets 150/1848. Whichever merges second must re-measure on the merged tree and re-record the cap. The body already states this.
- `VERSION`, the manifest version and the notes heading are untouched. No claim files changed. `git merge-tree` against origin/main exits 0.

## CI (step 11), the head's check-runs API

- budget-raise-gate is red. This is expected until tvofi's approving review at the head, and the body names it.
- nightly-status is red. On substance it is main-wide: its job is in tests.yml, and #1856's head a8bba2e6 carries the same red. But pr-contract's body check counts it against this PR because the diff touches governance.yml, so it is blocking item 3.
- pr-contract is red, for the body reason in blocking item 3.
- The other 32 of 35 check-runs are green, skipped or neutral, including wave-script (the new lane), policy-docs, briefs, mutation, closures, coverage, fast and instrument-self-tests.

I did not re-run the gate or the mutation table; I cite CI. tests/entities.py at the head, run under the F11.4 venv with GOLDEN_MODE=drift: ALL 2071 ENTITY CHECKS PASSED. The body reported 1 of 2071 failing, in tests.yml's mutation-ledger; that failure did not reproduce here.
