Fix review: merge cf84e0a45dacffab7d337c74fb9312fc9f298ad3
bus-nonce: 195c5a1a62665ae208de44f7db2c5470

Round 1. PR #2061 (R9-RO-9a, Part of #1922, closes nothing). Reviewed from a detached worktree at cf84e0a4; live head re-read at posting: unchanged. Contract diff `git diff $(merge-base)...origin/main -- dev/governance/roles/` empty.

## RESULT lines (reviewer's own runs; harnesses mine unless named, copies in evidence/)
- RESULT C9a twin (c9.py, old = merge-base mutation_table, new = head): head order [_padded@10, _seed@41] -> old charges `_seed:41` (the base's line), new charges `_padded:10`; reversed order both `_padded:10`; re-indent null control: [] at both ends.
- RESULT C9b: three CMP_BOUND mutants on one line -> old 3 bare copies of one key, new one key `...:2 CMP_BOUND*3`.
- RESULT fuzz 20000 random multisets (with and without move sides): added COUNT identical old vs new in 20000/20000; identity differs in 2501 (which twin is charged, the point of the fix).
- RESULT real replay, 12 most recent custom_components merges on main (replay_added.py, each merge's own inventory and base): old_added == new_added == 0, same=True, 12/12.
- RESULT CI mutation lane at head: `4642 unpinned site(s) ... 4642 at the ratchet base 0b89f781`, `MUTATION TABLE PASSED (empty scope)` -- no pin/ratchet count shifted. (The PR changes no production line, so this lane draws no mutant; read from the log, not the conclusion.)
- RESULT tmp_paths ledger arm vs the three real recurrences (coordinator's ask): #2025 head 9c664109 refused (`...54c3c7b5.json:4 /Users/.../hpo-seats/r9c-egb11/ev7/equiv_6840.py`); #2010 commit 9a8255b3 refused (`idle_codes.CMP_BOUND.a02b3552.json:4 .../probe_idle_codes.py`); #2024 head 1e92e0e8 refused (`normalize_flow_kg_s.GUARD_OFF.b46fca00.json:4 .../r9-ux9-fix2/ev/probe_inputs.py`). Same three refs under the merge-base tmp_paths: 0 refused each (control). In-tree versions accepted: #2010's fixed head 6eafd3a5 (cites dev/audit/harnesses/ux5_idle_codes_sites.py) 0 refused; each real row with its path re-pointed to a tracked path: 0 refused. Full per-commit walk of all three PRs in ledger_three_prs.txt.
- RESULT body figures re-derived: `--ref 00da22db5` 33 ledger refusals, `--ref 00da22db5^1` 0; 31 stock ledger files on main.
- RESULT finder harness plant_r2.sh (sha1 a725cc4e..., SRC re-pointed only), base vs head: B (lane-file comment, main's red) rc=1 NO RECORDING -> rc=0; C control fires at both; E2/E3 refused at both, head names found+expected heading; E6 `:12 CONST` named only as `CONST_X`: base "disposes of all 1" rc=0 -> head "omits" rc=1; A, D, E1, E4, E5 identical.
- RESULT mutation proofs (each applied, self-test run, restored): M8 boundary deleted -> layout 1 FAIL; M10 rules exemptions removed -> 2 FAIL; Mc4 -> closure 1 of 40 FAIL; record_row (i) `if green` -> 1 FAIL; (ii) `3 if pending` -> 1 FAIL; merge_train delete-rc ignored -> 1 of 81 FAIL; tmp_paths stock check removed -> 2 FAIL. Old added_unpinned/added_keys -> C9a/C9b red (c9.py above).
- RESULT head self-tests: layout ok; closure 40 PASSED; record_row all passed; tmp_paths 50/0 and --check 0 refused; merge_train 81/0; entities.py ALL 2214 PASSED (both R9-RO-9a checks ok).
- RESULT merge with current main 0b89f781: merge-tree rc=0, no conflict (5 overlapping files merge clean); on the simulated merge merge_train, layout, closure, tmp_paths, record_row self-tests pass and structure.py RATCHET PASSED.

## Settled CI at cf84e0a4 (check-runs API)
fast (3.14) `MODE: FULL -- every test script runs` and `ALL TEST SCRIPTS PASSED`; closures, mutation, instrument-self-tests (`tmp_paths: 0 refused ... ledger lines added since 0b89f781`), pr-contract, budget-raise-gate, policy-docs, briefs, wave-script, typing, env-matrix, browser, closure-scope: success. Red: delivery-status (`DELIVERY STATUS UNCHECKED -- 78 rowed, 0 pending, 0 overdue`, main's unread commits) and nightly-status (`closures, mutation-nightly, nightly-ha ... failed last night`) -- neither reads a file this diff touches, so neither is this PR's (fix-review step 11); body's `none` stands. coverage not required.

## Other checks
No policy file (policy_lint --corpus-filter over the diff prints nothing; orchestrator.md untouched by design). VERSION, manifest, RELEASE_NOTES, claim files, every *_budgets.json and closures.json untouched. #2012 merged as 45142cc3 confirmed; governance.yml field-coverage/agreement steps confirmed for the RCA correction.

## Notes for the orchestrator (not blocking)
1. Body/carry gap: the two carries sent after the PR opened -- prepr 6d vs closures-autofix contradiction, and the stamp rows gate vs rowless direct pushes -- are in neither the body, carry-1922.json (head or main) nor the roster. Not claimed, so not a code block; they still need a home (RO-9b/9c brief or their own carry).
2. Body scanning: neither tmp_paths nor prepr scans PR bodies; tmp_paths scans ledger JSON lines a diff adds. The body records this as a decision not to build (fixer.md step 3 cites out-of-tree finder harnesses by path).
3. Residual: the stock exemption matches by line text, so a new ledger row whose reason line copies a stock line verbatim passes. Low risk; recorded, not blocking.
4. After merge the ledger arm refuses #2024 at 1e92e0e8 (its reviewer passed it) and #2025 at 9c664109 until their reasons drop the seat paths.
