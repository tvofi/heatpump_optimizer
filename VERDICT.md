Fix review: merge a2576fcb2f0928d0a0fc467bc0ba66d5d629f511

Fresh review at this head after the earlier confirmed `merge` at 7c1d3b1b7 (head moved one
commit). This is not a blocked verdict and not a repair round: the delta since the judged
head is a main merge plus one budget leaf, and the leaf is correct and minimal.

RESULT head_measured a2576fcb2f0928d0a0fc467bc0ba66d5d629f511 (ls-remote and gh agree at post time)
RESULT merge_base 7cd5a588cbbbef354c00148040da2d720b8a888c
RESULT diff_vs_merge_base_files 5 (.claude/workflows/web-fix-wave.js, dev/governance/config/policy_budgets.json, dev/governance/roles/fix-review.md, dev/governance/roles/orchestrator.md, dev/programme/delivery/2063.md); nothing other than the one leaf and the review-timing changes the earlier review passed
RESULT budget_leaf_moved 1 (policy_budgets.json files_tokens["tools/audit/briefs/fix-review.md"] 2393 -> 2451); budget_raise_gate.py reports budget_raises=1 count
RESULT token_measure_at_head 2451 (dev/governance/roles/fix-review.md, 9805 bytes, Math.round(bytes/4) via the tree's own checkBudgets; `policy_lint --budgets` prints 2451 beside cap 2451)
RESULT token_measure_at_merge_base 2389 (9555 bytes, cap then 2393)
RESULT raise_is_minimal cap 2450 -> policy_lint rc=1; cap 2451 -> rc=0, so 2451 is the least passing value
RESULT mutation_proof head cap 2451 rc=0; cap 2446 rc=1; cap 2393 rc=1; restored rc=0 (exit codes taken on node, not on a tee pipeline)
RESULT policy_lint_rc_at_head 0 (TOTAL 0 error(s) across 40 policy file(s); FIXTURE ok 92 error(s) hold 243 pins)
RESULT entities_D11_05_arm resolves to the same program (layout.locate('.claude/workflows/policy_lint.mjs') -> tools/policy/policy_lint.mjs), green at 2451, red at 2446
RESULT claim_files_identical_to_origin_main 2 of 2 (claimed_drift.txt c30b94a9c, card_claimed_drift.txt 816d1eac2; neither in the diff)
RESULT env_drift_all rc=0, NO UNCLAIMED DRIFT 56 scenario(s), NO STALE FIXTURE 56 fixture(s)
RESULT structure_py rc=0, STRUCTURE RATCHET PASSED, every metric at its budget
RESULT aggregates_moved_by_this_diff 1 (corpus_tokens, +62 from fix-review.md +250 bytes; orchestrator.md +0). always_loaded and all three role caps untouched. corpus ~59960 was already over its 59591 cap and inside the +500 band at the merge base; the cap is not raised
RESULT red_check_at_head budget-raise-gate (failure, x2) -- the owner-approval gate, answered in the body as having no cheaper detector; the orchestrator's to clear by decision 0013, I saw it and do not block on it. Every other gate context at the head is success or skipped, including the four recarry reds the body answers
RESULT merge_tree rc=0, no conflicting path, no MERGE-CLAIM line; mergeStateStatus BLOCKED (the approval gate), mergeable MERGEABLE
RESULT forward_carry_present .claude/workflows/web-fix-wave.js reviewer prompt states the settle-then-post condition as a precondition, inside the diff
RESULT rca_figures_rederived RCA-2028 is in this head's tree; 19 on 12 PRs, A 7 / B 5 = 12, 3 body-only rounds of 7, 341 of 574 min, A 2/249 (#2007 #2049), B 1/92 (#2018) -- all re-derived from the document
RESULT body_inaccuracy 1, non-blocking: the body calls R9-RCA-2028.md "on PR #2062's branch (not on main yet)"; #2062 is MERGED and the file is at origin/main and at this head
RESULT payment_hunted_and_found 0 missing: every aggregate the body names is the one that moved, no other budget file changed, and no ledger/structure/arch-score figure moved
RESULT budget_raise_envelope tvofi's 2026-10-08 confirmation (<=142 lines, <=2461 tokens) covers the landed 140 lines / 2451 tokens
RESULT round this is the third review of #2063 (two pre-verdict rounds, then the merge verdict, then this re-review after the head moved); not a fourth-round re-cut

On step 14's plant: I set a cap raise on the same instrument with nothing improved and
policy_lint stayed green, which is expected -- a cap raise cannot be distinguished from an
earned one by the instrument alone. That is not this diff's shape: the file itself grew by
the 62 tokens the new step-11 rule is made of, and the recorded cap equals that file's own
measure, so the movement is earned by the change. It is an instrument limitation worth
carrying, not a defect in this branch.

The one thing I do not clear is the owner's approving review. decision 0013 / the
code-owner rule requires tvofi's APPROVED review at this exact head for the raise, and
tvofi's existing approval sits on ae6fbdd5eed2, an earlier commit. With that review at
a2576fcb2 this is merge-ready; the change itself is sound.

bus-nonce: d8317c20797380603dd8267bdf4b4ecc
