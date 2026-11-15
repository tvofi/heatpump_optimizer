Fix review: merge b58c6ca3684f7b1b358f6c6104c9a91af368cec8

bus-nonce: 21c42d3258e4d918163dfb98671f7891
pending-ci: gate

## Scope

Later round over the reviewed head b88d4b541a691c0fe714a461cd28c8028b54e43c (round 1, probe 94f29ddbe8eb: merge). The delta `git diff b88d4b541a69..b58c6ca3684f` is one bot commit, `ci: pin killed mutants` by github-actions[bot], adding one file: `tests/mutation_ledger/killed_by/ledger.py/@module.CONST.481451d2.json`. No production, policy, budget or body-claimed file changes in the delta, so nothing widens the scope (fix-review.md step 12). `review_carry.py b88d4b541 b58c6ca36` prints `CARRY`. The packet printed `## Review scope: full` only because round 1's verdict was not posted to `verdict/<pr>`; the PR's three-dot diff is 4 files, +34/-6, so I re-checked the fix itself as well (below).

## Evidence

- Delta (ev/delta.diff): the pin's anchor is `custom_components/heatpump_optimizer/ledger.py:<module> CONST 481451d2`, `old: REFERENCE_BASIS = 3`, `killed_by: tests/features.py`. sha1(`REFERENCE_BASIS = 3`)[:8] = 481451d2 (ev/anchor.txt), the digest rule at tests/mutation_table.py:622, so the pin names the new line. The stale `1e17aeec` (`= 2`) pin is absent at the head, deleted by the fixer as the body states. No `tests/mutation_budgets.json` change.
- features.py at the head, run locally with `PYTHONPATH=tests/hastub` (ev/features-wt.summary.txt): `ALL 5652 FEATURE CHECKS PASSED`, rc=0.
- Mutant `REFERENCE_BASIS = 6`, the bot's pinned move (ev/features-m6.summary.txt): `2 of 5652 FEATURE CHECKS FAILED`, rc=1, failing the literal-3.0 pin and the stamp-3 check. KILLED. The pin's reason says `failed=3` for this move. My local count is 2. The kill, which is what the pin records, holds either way. That count is the bot's text, not a body figure.
- Mutant `REFERENCE_BASIS = 2`, reverting the fix (ev/features-m2.summary.txt): `3 of 5652 FEATURE CHECKS FAILED`, rc=1. The failures are the literal pin, the stamp-2 check and the stamp-3 check, which matches the body's three failing-first checks. KILLED.
- `## Red checks` answers `tests / mutation` as red by construction on the one unpinned `REFERENCE_BASIS = 3` site, which mutation-autofix pins after the push. This delta is that pin, so the answer still holds. `tests / mutation` is in the owed-reds set (ev/owed-reds.txt), and it is answered.
- Merge with main: `git merge-tree --write-tree origin/main b58c6ca3684f` rc=0, no conflict (ev/merge-tree.txt).
- review_packet `head-note` refusal: the body's `## Head` names b88d4b541a69, not this bot-commit head. The commit is the expected autofix pin that the body's `## Unpinned sites` and `## Red checks` anticipate, and `review_carry` reads the range as CARRY. Whether pr-contract requires the line is pr-contract's call, which classify reads.
- `tests / nightly-status` concluded failure at this head. It is not in `owed-reds`, so it is neither answered nor a block.
- CI: classify lines in ev/classify.log.
- CI at 00:26 UTC, after about 30 min of polling: `WAIT b58c6ca3684f7b1b358f6c6104c9a91af368cec8 pending: gate red: none`. Every other required check had concluded without an owed red, so this returns with `pending-ci: gate`.
