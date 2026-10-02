Fix review: blocked 5619ead8eee2841e75b50f27dbe54b1e07be1479 root-cause-unanswered: budget-raise-gate went red, unanswered (`## Red checks` says none; pr-contract red on it); also the Approval head, the A1/A7 placement and a "nothing else deviates" claim
bus-nonce: ceaee3b2e1d70b6613ab6490224a61b8
evidence: /Users/timmalmstrom/hpo-seats/1856-review/ev
Round 1. Measured at 5619ead8eee2841e75b50f27dbe54b1e07be1479 (merge base 5f87e25a1), detached worktree. fix-review.md current (MB...origin/main empty for tools/audit/briefs/).

RESULT policy_lint head: TOTAL: 0 error(s) across 40 policy file(s)
RESULT policy_lint head with MB's policy_budgets.json: TOTAL: 9 error(s) (body's mutation proof reproduced)
RESULT caps == measured (policy_lint --budgets): fixer.md 295/295 4866/4866; D1.md 60/60 818/818; root-cause.md 84/84 998/998; defect-root-cause.md 149/149 1812/1812; corpus 56037 cap 56037; tests/README.md 459/800 6671/6686 (no raise needed, true)
RESULT nothing else loosened: policy_budgets.json diff is those nine values only; _band untouched; no other *_budgets.json in the diff; budget-raise-gate lists exactly 9 RAISE lines
RESULT rules_sync --check: ok; structure.py: STRUCTURE RATCHET PASSED
RESULT #201 comment 5956454383 (2026-10-02T16:15Z) announces the same five raises before the push
RESULT VERSION / manifest / notes heading untouched (pr-contract: "no version edit")
RESULT merge-tree origin/main 8fa06663c: clean; main's move since MB touches no POLICY_GLOBS file
RESULT CI (waitci, 33 runs): NOTGREEN budget-raise-gate (REFUSED: no decisive review by tvofi -- expected until the review), NOTGREEN pr-contract

Clauses against drafts (sources: handoff/audit-r9-plan:handoff/round9/state/rca/<slug>/RCA.md):
- A1 (p2) verbatim. A7 (i4) verbatim. A3 (recompute) verbatim, in step 15 as drafted. A6 (i5) verbatim, root-cause.md section 2. A5: draft wording kept, as new step 16; no obligation beyond the draft. A8: "; and one governance tool must not re-implement another" -- the draft's clause in the section's own "must never" grammar; no added obligation.
- A4 is NOT verbatim: draft "Add one perturbation to the store-fuzz set", landed "Add one more perturbation to the set". In step 2 (store fuzzing) the referent is the same, so no obligation changes, but it is an undisclosed deviation.
- A9: draft "registered in `field_coverage.mjs`"; landed "is covered by `field_coverage.mjs`: a governance check is in its derived set and registers its input or declares none". The derived-set clause is the brief's adjustment and matches field_coverage.mjs (derivedSet, DECLARED, "declares neither an arm nor a reason"); "registered in" -> "covered by" is a second wording change the body does not name.

Blocking items (fixer owes all four; none needs a policy re-approval):
1. root-cause-unanswered: budget-raise-gate is red at the head and `## Red checks` reads "none"; pr-contract fails on exactly that ("check `budget-raise-gate` is red and `## Red checks` does not name it"). Name it and answer it: the red is the designed gate awaiting tvofi's approving review at the head, and no cheaper detector exists or is needed (the finding that none exists).
2. `## Approval` says the PR merges on tvofi's approving review "at head e90c1b7a…". budget_raise_gate.py (approval(): commit_id must equal the PR head) and the code-owner rule need the review at the PR head, 5619ead8… today. As written it points tvofi at a commit whose approval the gate refuses. Name the PR head (or "the PR head at merge").
3. Placement (A1/A7, fixer.md step 8): the two inserted paragraphs sit between "say what you did instead." and "This is step 11 applied to your own instrument: … A root-cause analysis on **#592** added this step". "This" and the #592 provenance now read as attached to the A7 agreement.mjs sentence, which is even on the same line. That misattributes the provenance of the new text and the rationale of the old. Move the A1 and A7 paragraphs below "…a reviewer refuted all three a draft quoted." (or keep the old sentences together ahead of them). Same words, no cap change expected; re-check policy_lint.
4. The body's "Nothing else deviates from the drafts" is false: A4 ("store-fuzz set" -> "the set", "one" -> "one more") and A9's lead clause ("registered in" -> "covered by …:") deviate. Either restore the draft words (A4: "Add one perturbation to the store-fuzz set:") or list the deviations under the seat's choices. Restoring A4's draft words keeps D1.md within 60 lines; re-measure tokens if you do.

Minor, not blocking: Figures cite "origin/main 948671af" for the main-side lint; the merge base is 5f87e25a1 -- say which.
Not run: mutation table, gate (cited CI per fix-review.md step 11). No numeric scripts touched. Class sweep: the roster names no class, so the body's "no enumerator" is correct.
