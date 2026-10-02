Fix review: merge a8bba2e6861c03f4aaef3f8ccfeaa011b2b0ca61
bus-nonce: 1286467a60027f327905e3cd53a616f5
evidence: /Users/timmalmstrom/hpo-seats/1856-review/ev2
Round 2. Measured at a8bba2e6861c03f4aaef3f8ccfeaa011b2b0ca61 (merge base aa7a81192), detached worktree; fix-review.md current (MB...origin/main empty for tools/audit/briefs/). Round-1 verdict was blocked at 5619ead8 (review/1856 88014b71); this round judges the authored delta 4fa6bbe86 plus the main merges.

RESULT item 1: `## Red checks` names budget-raise-gate and answers it (the designed gate, no cheaper detector); pr-contract now success at this head
RESULT item 2: `## Approval` says the review is owed at the final PR head and cites budget_raise_gate.py's head-only acceptance
RESULT item 3: fixer.md step 8 -- the "This is step 11 ... #592 ... a draft quoted." sentences are back after "say what you did instead."; the A1 and A7 paragraphs follow them, words unchanged (4fa6bbe86 diff: only the three closing lines move)
RESULT item 4: A4 now "Add one perturbation to the store-fuzz set: an instant written by a clock ahead of the one that reads it back, driven across a restart." = draft; A9 now "A check over a structured input is registered in `field_coverage.mjs`: a governance check is in the derived set and registers its input or declares none." = draft lead + the brief's C10 clause verbatim. All nine landed clauses now match their drafts or the disclosed A5/A8 choices
RESULT caps == policy_lint --budgets: fixer.md 295/295 4866/4866; D1.md 60/60 819/819; root-cause.md 84/84 998/998; defect-root-cause.md 149/149 1813/1813; corpus 56039 cap 56039; tests/README.md 459/800 6671/6686
RESULT nothing else loosened: three-dot policy_budgets.json diff is those nine values only; _band untouched; no other *_budgets.json
RESULT policy_lint head TOTAL 0; with 5f87e25a1's policy_budgets.json TOTAL 9; rules_sync --check ok; structure.py PASSED
RESULT merge-tree origin/main aa7a81192: clean
RESULT CI (waitci, 35 runs): NOTGREEN budget-raise-gate -- expected, answered in the body, goes green on the mandate approval at this head; NOTGREEN nightly-status -- "NIGHTLY ABSENT" about main's scheduled run at 492d840; the three-dot diff reaches no reporter input (only its own row docs/delivery/1856.md), so not this PR's (fix-review.md step 11)

Notes for the orchestrator, not blocking (body text only, no head move):
- The #201 announcement 5956454383 lists D1.md 784->818 and defect-root-cause.md 1774->1812 tokens and corpus "about 56037"; the pushed caps are 819, 1813 and 56039. Post the exact values on #201 before giving the mandate approval, so the announced raise equals the merged one (CLAUDE.md rule 2).
- Body table row A9 still summarises "covered by `field_coverage.mjs`"; the text now says "registered in".
- Figures: "at the merge base 8fa06663c: 0" -- the merge base is now aa7a81192.
Not run: gate and mutation table (CI cited, step 11). No numeric scripts touched.
