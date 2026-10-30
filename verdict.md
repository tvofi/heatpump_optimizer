Fix review: merge 27bb23875cf0248028d243b4643523e6f4c7f04e

bus-nonce: c3d19294ad8d9f008216eaad907dc1f4

## Scope

Resolution-delta review (fix-review.md step 12). The previous verdict was merge at 891b8b7834f5bafc08e5856ad71515a8c2baacee. review_carry.py prints FRESH-REVIEW, because f4dc68a48 is not the automatic merge of its parents. So only the resolution is reviewed here; the authored fix stands on the round-3 review. This is not a fourth repair round. It is a main merge that a hand resolution made necessary.

## Findings

None.

## Evidence

- Head measured: 27bb23875cf0248028d243b4643523e6f4c7f04e. Re-read at post time with ls-remote: the PR branch is still 27bb23875cf0248028d243b4643523e6f4c7f04e, and origin/main is 2d151411f80c3f868c4de5b3a878c673cb88df02 (ev/ls_remote_at_post.txt).
- 27bb23875 merges f4dc68a48 into 891b8b783. Its tree equals f4dc68a48's tree, 2055d2f187e8 for both (ev/trees.txt), so the head carries nothing beyond the fixer's merge. The body's `## Head` sentence for 27bb23875 reads as if that commit itself merged origin/main again. In fact f4dc68a48 already holds c0a1d4635. The body describes this tree correctly either way.
- Conflicts replayed with `git merge-tree --write-tree 891b8b783 c0a1d4635`, with the claimnotes and ledgermerge drivers installed. It exits 1 on exactly two files, `dev/audit/rounds/round4/D6/claims.py` and `claims.md` (ev/conflicts_replay.txt). LEDGER-MERGE resolved `tests/structure_budgets.json` and `tests/closures.json`. Neither claim file conflicted.
- Resolution compared with the automatic merge tree 05818d2c (ev/resolution_vs_automerge.diff): only those two files differ, and the difference is 11 deletions, all conflict markers plus the losing side's lines. Every other path, including all production code (optimizer.py, thermal_model.py, coordinator.py) and both ledgers, is byte-identical to the automatic merge. Nothing in production changed beyond what the two sides already carried.
- Both sides' clauses are present. claims.py keeps this PR's Range-count history clause ("92 with R10-COP-PARTLOAD's part-load derate Range row") and main's `arch_modules_on_disk=84` line with its plan_slots.py history. claims.md keeps C31 from the PR (92 rows) and C32/C33 from main (84 modules). Neither side's clause was dropped.
- Read-back: at the head, `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` exits 0 and prints RESULT config_ranges_compared=92 rows, arch_modules_on_disk=84, arch_map_listed=84, arch_map_missing=0, claims_false=0 and claims_stale=0. Afterwards `git status` is clean, so the committed claims.md is what the generator writes (ev/claims_run.txt).
- Claim files: `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` are unchanged between 891b8b783 and the head. Three-dot from the merge base, the branch's claim is still its single `config_flow` line. `claims-for: 7.0.5` matches VERSION 7.0.5 at both the head and main. No claim was reinstated or dropped.
- VERSION, manifest.json and RELEASE_NOTES.md: three-dot from the merge base prints nothing.
- Mergeability: `git merge-tree --write-tree origin/main 27bb23875cf0248028d243b4643523e6f4c7f04e` against origin/main 2d151411 exits 0 with tree 55d0747a (ev/merge_tree.txt).
- The PR's own test at the head: `tests/features.py` reads ALL 4596 FEATURE CHECKS PASSED, exit 0 (ev/features_head.txt).
- Mutation proof re-run at the head. The resolution touched no production line, so this is a spot check. M1: `partload_factor` returns `1.0` instead of `1.0 - params.cop_partload_derate * x`. Result: 7 of 4596 FEATURE CHECKS FAILED, the same seven checks the body names (linear law, max-power heat, scalar step slab, buffer charge ceiling, flat-price max-power share, hot-water schedule, trajectory hot-water track). After restore the worktree is clean (ev/mutant_M1.txt, ev/mutant_M1_full.txt). The body cites 4593 checks; the head has 4596 because main's merge added three. The seven failures are unchanged.
- Body figures checked at this head: C31 = 92 rows, C32/C33 = 84 modules, merge-tree exit 0, three-dot version files empty. Not re-derived, per the step-11 rule to cite CI's heavy runs: the body's local scoped-gate line ("MODE: SCOPED (30 scripts)", "32 TEST SCRIPT(S) PASSED; 2 SCOPED OUT") and `STRUCTURE RATCHET PASSED`. The script counts in that line do not add up on their own reading, and I did not reconcile them. CI's `tests / closures` is green at this head.
- CI on 27bb23875cf0248028d243b4643523e6f4c7f04e, read from the check-runs API: success for closures, coverage, coverage-ratchet, typing, replay, browser, arch-instrument, nightly-ha (2025.2.0 and stable), graders-head-copy, closure-scope, briefs, arch-score, budget-raise-gate, delivery-status, policy-docs, wave-script, env-matrix, instrument-self-tests, validate-hacs, hassfest and codeql (actions, javascript-typescript). `tests / fast (3.14)`, `tests / mutation` and `codeql / Analyze (python)` had not concluded when I read them. This verdict does not stand in for them; the merge train's required-check gate reads their conclusions.
- Red checks: only `tests / nightly-status` is red. It grades main's nightly record, the body's `## Red checks` answers it as main-graded, and this diff does not reach what it reads (defect-root-cause.md). No other gate check is red at this head.
- Review packet rendered (`review_packet.py render --pr 2872 --head 27bb23875cf0248028d243b4643523e6f4c7f04e`), exit 0. It reported FIGURES: 8 resolved, 13 not verified, 0 refused, with no host-path signal (ev/review_packet_render.txt).
- Instruments are the tree's own: claims.py, features.py, merge-tree, review_carry.py and review_packet.py. I built no harness. The M1 mutant was an exact-match string replacement asserted to hit once.
