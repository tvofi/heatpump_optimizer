Fix review: merge a8f86edd6b2508ce6ff8fdca831f88516895a37e
bus-nonce: 7351de69db2033e405cc622887ebbbf0

Round 2 of #1862 (R9-EG-R1). This reviews the delta since round 1's blocked verdict at 53017884 (review/1862 2b24be6e). I measured from a detached worktree at a8f86edd, which was still the live head when I posted. The head contains origin/main 51ce8f2a7, which includes #1856, #1857 and #1859. `git merge-tree` against origin/main exits 0. `tools/audit/briefs/` has no diff from the merge base to main.

## Round 1's owed items
1. Fixed: the ownership statement. `fold_ledger.py`'s docstring and `prepr.sh` step 3f5 now say the wave-script lane runs the branch's own copy, and that ownership (CODEOWNERS) is the only protection. This agrees with governance.yml, CODEOWNERS and the body.
2. Fixed: the two surviving mutants. The self-test now passes 31 of 31. Each of my mutants turns it red:
   - RESULT mutant=unclassified-reason-ignored rc=1 red=1
   - RESULT mutant=intree-no-prefix rc=1 red=1
   - RESULT mutant=intree-no-isfile rc=1 red=1
   - RESULT mutant=total5-arm-dropped rc=1 red=1
   - RESULT mutant=window-off-by-one rc=1 red=1
   - RESULT mutant=barriered_any-dropped rc=1 red=2
   - RESULT mutant=unknown-rca-dropped rc=1 red=1
   - RESULT mutant=unparsed-dropped rc=1 red=1

   The unclassified-reason expectation has a null control: the same placement with a reason passes.
3. Fixed: `## Red checks` now names nightly-status and answers it. The exemption is void because the diff touches governance.yml, and no cheaper detector exists. pr-contract is green at this head.
4. Noted in the body: "five while open" in the policy against "not barriered" in the code. Only P4 (status `detector`) is affected.

## Re-checked at this head
- RESULT `fold_ledger.py check` rc=0: 0 violations, 28 classes, 549 instances, 39 in-tree survivors. The register data is unchanged from round 1's verified state.
- Caps match `policy_lint --budgets` exactly: `defect-root-cause.md` 153/153 lines and 1887/1887 tokens, `D8.md` 56/808, `judge.md` 30/469. All five aggregates are inside their band. #201 comment 5960185195 (tvofi's account, 19:48Z) posts 153 and 1887.
- Conflict resolution in `policy_budgets.json`: compared with origin/main, only this PR's six per-file values differ. No key was added or removed, and main's other values are kept, including #1856's aggregate and per-file raises.
- The policy text against origin/main is only this PR's clauses; #1856's text is intact from main. `rules_sync --check` is ok, and `policy_lint` reports 0 errors.
- One small wording slip in the body ("the exemption for these two" names one check). It does not block.

## CI (head check-runs API, 35 runs)
- budget-raise-gate is red, as expected until tvofi's approving review at the head.
- nightly-status is red because it is main's red, and the body answers it.
- Everything else is green, skipped or neutral, including pr-contract, wave-script, policy-docs, briefs, mutation and closures.

This diff touches code-owned paths, policy and a budget raise. It still needs tvofi's approving review at the head.
