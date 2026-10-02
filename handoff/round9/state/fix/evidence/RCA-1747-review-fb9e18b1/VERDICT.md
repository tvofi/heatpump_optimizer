merge fb9e18b1423d8c8da2dda2f203ad6a4d5426445b

Review of record PR #1787 (R9-RCA-1747), round 1, head fb9e18b1 (live PR head re-read at posting; origin/main still 830f84ad, the PR base).

1. Scope: the diff at merge-base 830f84ad (three-dot) is 20 files, all additions: tools/audit/rca/R9-RCA-1747.md, 16 files under tools/audit/round9/rca/1747, one appended carry each in .claude/workflows/carry-1644.json and carry-1743.json, and docs/delivery/1787.md. No production, test, VERSION, manifest, notes-heading or claim-file change (prepr: "no version edit" ok, "claim files byte-identical to origin/main").
2. Carries lint: node .claude/workflows/brief_lint.mjs rc=0; carry-1644.json and carry-1743.json each "0 error(s), 0 warning(s)"; the carry schema's CARRY self-test ok (brief_lint.txt). carry-1644 now holds 4 carries, carry-1743 holds 2, matching the RCA's "carry 3" and "carry 1" labels.
3. Figures: every committed output re-derived here on Linux, CPython 3.11.15, numpy 2.4.6, scipy 1.17.1, 1 BLAS thread:
   RESULT census_reach 1b43198e: IDENTICAL (as-is [True, True] pass; no-replan and off-spy reach FAIL; off-spy ships 9.22 kWh, breach 0.629)
   RESULT census_reach 754d2319: IDENTICAL
   RESULT coil_trigger 754d2319: IDENTICAL
   RESULT probe 754d2319, 81aa0c3b, 894b3310: IDENTICAL
   RESULT kwarg_seams package: 64a54195=19, 754d2319=63, 1b43198e=62, SEAM lines IDENTICAL modulo the file prefix; per module 39 config_flow / 7 coordinator / 10 optimizer / 6 thermal_model at 1b43198e
   RESULT suite reach features.py 754d2319: IDENTICAL, "ALL 3597 FEATURE CHECKS PASSED"
   RESULT suite reach features.py 64a54195: IDENTICAL, "ALL 1430 FEATURE CHECKS PASSED"
   History (history.txt): 38 v* tags contain 81aa0c3b (v6.3.16 dated 2026-09-06 to v6.7.12); 56 contain 64a54195 but not 81aa0c3b; 894b3310 = 81aa0c3b^; 81aa0c3b adds the "not coil_replan" guard; git log -G between 64a54195 and 754d2319 on optimizer.py returns 4a7bdb69 and 5ec32572 only; commit dates match.
   Register (register.txt): bugclasses.json P2 total 66, R9 27, detector null, barrier null, status open, rca_planned R9-F1.11; #1747 absent. Instrument sha1s e29cc879 and 25ec2ea2 match.
   Not re-derived: the cost test's seat and PR timestamps (121 min, 42 min) and kwarg_seams wall-clock (3.2 to 3.6 s); the RCA states these as its own.
4. CI at fb9e18b1: no check red. Record lanes green: delivery-status, policy-docs, briefs, pr-contract, wave-script, instrument-self-tests, budget-raise-gate, nightly-status, closures, closure-scope, fast (3.14), mutation, typing, env-matrix. "record" and delivery-status-publish skipped, as on a PR. coverage and CodeQL Analyze (python) were still running when I posted; neither is a record lane.
5. Extras: prepr.sh at the head rc=0, MODE: SCOPED, codeowners_gap uncovered_files=0, and no self-test red this time. git merge-tree against origin/main exits 0.
