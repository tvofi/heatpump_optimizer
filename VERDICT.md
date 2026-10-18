Fix review: merge aad55ffb4de4a12db5ac222160333bc4fda36050

bus-nonce: df9e42d81b56e40fe065518340dc153e

Round 2 (round 1: blocked 5f6d8fbd7, mutation: audit-find.js's cut-off arm unpinned). Measured head aad55ffb4de4a12db5ac222160333bc4fda36050, still the PR head and origin/fix/r10-tick-drivers when written; base = merge base 07a09406a1cc (origin/main tip). Detached worktrees at both. The contract is current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
Code-owned: .claude/workflows/audit-find.js, audit-verify.js, tools/audit/fold_ledger.py. tvofi approves at merge, whatever this verdict says.

## OPEN BEFORE MERGE: pr-contract is red at this head (a body edit, not a head move)
pr-contract job 117781735553 (started 20:29:53, after wave-script and delivery-status concluded red) fails with exactly one error: "check `wave-script` is red and `## Red checks` does not name it". The body's ## Red checks names only 03c0766bf's reds and says "This head has had no CI run yet".
- The wave-script red (job 117780978357) is main's, the case the dispatch names. The wave-script checker passes 187/0. The agreement step refuses on `merge-subject-pr` with 2 divergent: "Merge pull request #2401 (R10-ARCHSCORE-COVERAGE p5)" and "#2379 (R10-SENSOR-PAYLOAD)", where policy_lint.mjs reads null. I reproduced those same 2 divergent lines at base 07a09406 (ev/checks.txt and the agreement run). The R10-MERGE-SUBJECT fix is in flight for it.
- delivery-status (job 117780978317) is OVERDUE on main's rows #2413, #2412 and #2407. The diff only adds its own row 2390.md, so it is not this PR's (step 11; pr-contract does not list it).
- I have not posted `root-cause-unanswered`. The fixer did not turn this check red: main did. Also, not all of the head's workflows had concluded, because closures and Analyze (python) were still in_progress. The PR still needs a body line naming wave-script as main's merge-subject-pr divergence, then a pr-contract re-run. Until then the required pr-contract stays red. The orchestrator owns that edit; this review cannot make it.

## Round-1 blocker: fixed
64f855dcb adds the cut-off pin. Mutants were applied in a detached worktree at the head and restored, with `git status` empty after each (ev/mutants.txt):
- M1, `replyField` catch reads cut-off text as empty: check-wave-script 197 passed, 1 failed, on "...and one whose findings came back cut off is a seat not reported...". This mutant survived at 197/0 on 5f6d8fbd7 in round 1, so it is now killed.
- M2, the refusal kept but its log dropped: 197/1 on the same case.
- M3, `replyField` returns the reply as given in both drivers: 193/4, the 4 cases the body names.
- M4, FINDING_REPORT's expected_direction enum dropped:
  - checker 197/1 ("the finder's return schema is finding.schema.json itself...");
  - agreement prints 4 DIVERGENT finder-report-form lines (up, down, to_zero, sign_flip), RESULT divergent=4.
- M5, fold without sync: fold_ledger --self-test prints the 4 FAIL lines the body names.
- M6, `repairs()` returns [] and body_push's predictor call disabled: prepr --self-test 287 passed, 3 failed, rc 2, the 3 M2/M3 arms the body names.
Every figure in the body's Mutation proof reproduces at this head.

## RESULT lines: dev/audit/harnesses/r10_tick_drivers.py (sha1 b99267a7..., matches the body), --evidence = head tree, jsonschema 4.26.0 venv
base: findings=44 form_file_rej=35 form_driver_rej=0 form_gap=35 form_both_ok=9 gather_replies=1 gather_max_kb=193.9 gather_missing=3 text_gather=-1 text_read=-1
head: findings=44 form_file_rej=35 form_driver_rej=35 form_gap=0 form_both_ok=9 gather_replies=10 gather_max_kb=34.0 gather_missing=3 text_gather=3 text_read=44
head --perturb: form_gap=11 form_driver_rej=24 (now drops the expected_direction enum alone, per fc145b97c; round 1's step-8 note is resolved)
All match the body. The body took its base at 106af95a33f8; mine is 07a09406, with the same numbers.
Null controls hold:
- form_file_rej and form_both_ok are the same at both ends.
- gather_missing=3 is the same at both ends (D15 seats on B11, outside BOXES).
Step 9: the harness is the fixer's, not the finder's. The body says so ("The R10-TICK-DRIVERS fixer wrote it"; #2265's evidence had no committed harness). The jsonschema-unpinned friction is disclosed under ## Friction.

## Cheap checks at head (ev/checks.txt)
- check-wave-script: 198 passed, 0 failed.
- Base checker over the head's drivers: 187/0.
- agreement: pair finder-report-form, 214 items, 0 divergent; self-test 13 of 13.
- fold_ledger: --self-test 0 FAIL; check 0 violation(s); sync reports "already carries" and leaves the tree clean.
- ci_predict --base origin/main: no closures or fast red predicted against 07a09406a1cc.
- closure select: MODE: SCOPED -- 1 script(s) run, 32 scoped out.
- structure.py: STRUCTURE RATCHET PASSED.
- throwaway_git --check: 0 refused.
- ref_privacy --self-test: 66 checks, 0 failed.
- env_drift --claims-only: ok.
- archscore: dS +0.0000 NULL.
- prepr.sh --self-test: 290 passed, 0 failed, rc 0 (ev/prepr_selftest_head.txt).
Step 5: VERSION, the manifest, RELEASE_NOTES.md and both claim files are untouched (three-dot). No golden fixture is in any changed file's closure.
Step 14: closures.json gains one line, an inert_reads entry for the new harness. The new file earns it.

## Step 6, class rule (the body's grep)
- Base: audit-find 3, audit-verify 9.
- Head: 0 and 0.
- Outside this group's files, unchanged: audit-fix 2, web-decomp-stage 4, web-fix-wave 1, web-stamp 3. That is the 10 the body dispositions (scalar replies; type-drift arm unmeasured, not carried).
No undispositioned seam.

## Steps 12 and 13, the merges
- `git merge-tree --write-tree origin/main aad55ffb` exits rc 0, giving tree 05c1665b. That equals the head's own tree, so the head already contains main.
- Recomputing the final merge (efcc131e7 + 07a09406) gives "LEDGER-MERGE: resolved tests/closures.json", with the same tree as aad55ffb's. It is an automatic resolution.
- efcc131e7 recomputes to its own tree exactly.
- Authored delta since round 1: 64f855dcb (the pin) and fc145b97c (the --perturb scope). Both were reviewed above.

## CI on this head (check-runs API, 45 runs)
- failure: wave-script and delivery-status (both main's, above), and pr-contract 117781735553 (the body gap above). An earlier pr-contract run, 117780976514, succeeded.
- in_progress at writing: closures and Analyze (python).
- Every other concluded run is success, skipped or neutral. That includes instrument-self-tests, mutation, fast (3.14), coverage, coverage-ratchet, typing, env-matrix, policy-docs, closure-scope, arch-score, budget-raise-gate, browser, hassfest and validate-hacs.
- mutation's green is cited by conclusion only. The body says no changed line is in the mutation inventory.

## Step 10, forward-carry
The body says none. Round 1 found the tick-fold follow-up (O14) recorded by tvofi on #2265 as cut from main after this merges. Nothing new needs carrying. Round 1's NOT VERIFIED note on the item IDs L03..P57 and L12(a/b/c) stands unchanged; the orchestrator should confirm it.
