Fix review: blocked aef1975a7f7adf3c1b3df2513842d76ca4eb1e3d stale-self-test: prepr.sh self-test arm 6a still expects an untouched inheriting branch to be refused; instrument-self-tests is red at PR head 34dde3d9

Reviewer: hpo-approver seat (opus), R9-F10.8, PR #1811.

## Blocking
- CI `instrument-self-tests` (run 36871971202, job 110401743099) at 34dde3d9: `bash tools/audit/prepr.sh --self-test` -> `FAIL 6a refuses a branch that inherits main's claim list, naming --drop-inherited (got 0:, wanted 1:--drop-inherited)`, 127 passed / 1 failed, exit 2.
- Cause: the fixture at tools/audit/prepr.sh ~859-893 builds `inh` = fork of a main that claims `main_lane`, never touching tests/golden/claimed_drift.txt. That is exactly the byte-identical shape this PR makes the no-claim state, so `0:` is now the correct answer. The arm encodes the retired rule; the fix is in prepr.sh's self-test, not in env_drift.
- Fix asked: (1) make `inh` the touched shape (append a note line to claimed_drift.txt on `inh`, keeping main's list), which must still give `1:--drop-inherited`; (2) add an untouched arm (fork of main, edits only code) asserting `0:`; (3) update the comment above the fixture ("one branch inherits the list (refused)"). Re-check `claims_remedy`'s INHERITED hint still reads right for the touched shape (it does: --drop-inherited empties an edited inherited list).
- `pr-contract` is red only because `## Red checks` does not name `instrument-self-tests`; it clears once that check is green.

## Verified (holds; carries to the next round)
- Red first: at d156fac5 entities.py 4 of 2012 fail (incl. "a carried claim line does not excuse a moved fixture"), card.mjs 4 fail; at aef1975a all 2014 entity checks and all card checks pass.
- #213 stays closed: mutants M3 (judge_drift excusing = all claims) killed by entities.py; M5 (judgeCardClaims excusing = tree claims) killed by 3 card checks; extra mutant keying `carried` on the parsed list instead of bytes killed by 3 checks (edit-but-keep-list still refused, both working tree and CLAIM_HEAD).
- Main's push shape (probe_main.py): after a --no-ff claiming merge, `check_claims_hygiene(HEAD^1)` = None and the merged lines excuse; after a later non-claiming merge, hygiene = None and the carried line does NOT excuse a moved fixture (DRIFT); squash claiming merge: new line excuses, carried one does not.
- CI ref semantics: PR runs pass ref = main tip (merge-base of the synthetic merge), claims read from the merge tree, fork_point = tip, so authored = lines differing from main's tip; hygiene uses CLAIM_HEAD vs merge-base(tip, head). Consistent.
- Wording: claim-files.md change is accurate; ci-autofix.md unchanged and still correct.
- Merge delta 34dde3d9: tree == merge-tree(aef1975a, 2f2b167d); main's side touches none of the 7 PR files; no resume/handoff files in code-head ancestry.
- CI at 34dde3d9 otherwise: fast (3.14), typing, mutation, closures, browser, policy-docs, env-matrix, budget-raise-gate green; coverage and CodeQL python still running when read.

## For the coordinator / Mac
- PR #1811's title is the merge commit subject ("Merge remote-tracking branch 'origin/main' into fix/r9-f10-claims-8"); it should be the F10.8 title. GitHub also reports mergeable_state "dirty".
