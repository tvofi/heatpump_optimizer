Two reds `prepr.sh` step 6d's CI predictor (`tools/pr/ci_predict.py`) should have predicted and did not: (1) `wiring_preds` kept only `UNWIRED` lines of `selftest_wiring.py --check`, so #3004 round 3's MISMATCH on the instrument page it added went red on `instrument-self-tests` unpredicted; (2) `prepr` predicted the `mutation` ratchet but not the null-control refusal (#2997 rounds 1 and 2). `wiring_preds` now returns every gap kind (UNWIRED, MISMATCH, UNINDEXED, DUPLICATE, MISSING) that names a changed file; the `mutation` arm adds `NO NULL CONTROL` (via `mutation_table.null_for`) as a real red (rc 1, counted in the jobs/reds summary). `ci-autofix.md` names the refusal in its table; no autofix job repairs it. Policy file: needs the owner/mandate approval before merge.

## Head

eceed7d2a8db463577747e293ee0947edba4461d (merge of `origin/main` 2fc0e95b2 into the fix; the merge changed only `dev/programme/` rows). `prepr.sh` ran on this head: every step ok but `pr-body`, whose `## Head` and `## Approval` refusals this body answers; the earlier run at 1110bd45d (before the main merge) was rc=0.

## Mutation proof

Predicate mutated: `kinds = ("UNWIRED", "MISMATCH", "UNINDEXED", "DUPLICATE", "MISSING")` -> `kinds = ("UNWIRED",)` (the old behaviour); `python3 tools/pr/ci_predict.py --self-test` then prints `FAIL a planted MISMATCH on a changed instrument page is predicted red` and `1 failed`; restored, `0 failed`.
Disclosed gap: mutating `is_red`'s `NO NULL CONTROL` clause (rc only) leaves the self-test green (`0 failed`); the self-test drives `null_control_preds` directly, not the rc path.

## Null control

`python3 tools/pr/ci_predict.py --self-test`: the same MISMATCH on a page the diff leaves alone predicts nothing; a consistent index predicts nothing; a pool holding `button.py` (comment present) predicts nothing; a mixed pool and an empty pool predict nothing. A pool of only `flow_meter.py` predicts `NO NULL CONTROL`.

## Figures

- `python3 tools/pr/ci_predict.py --self-test | tail -1` -> `ci_predict self-test: 0 failed` (control: with the filter mutated as above, `1 failed`).
- `python3 tests/structure.py | tail -1` -> `STRUCTURE RATCHET PASSED`.
- `node tools/policy/policy_lint.mjs | grep TOTAL` -> `TOTAL: 0 error(s)`; `ci-autofix.md` stays within its line and token caps (the first draft, a prose paragraph, exceeded both and was cut to one table row plus spent citations).
- `bash tools/pr/prepr.sh` -> rc=0 at 1110bd45d, MODE: SCOPED.

Alternatives: filtering gap lines in `selftest_wiring.py` itself was rejected (the check's CI output must stay whole; the predictor owns the diff scoping). Mutation arm: pool is the added sites, not a fresh sampled pool, since the refusal fires for the pin pool CI draws.

## Red checks

`none` on this branch. Answer for the two reds that motivated it: cheaper detector = this change (`ci_predict` wiring and mutation arms); standing cost = one `selftest_wiring.py --check` run (already run) and one `null_for` file scan per added site.

## Forward-carry

`none`

## Friction

`none`

## Approval

Not yet given. `dev/governance/rules/ci-autofix.md` (policy; its generated `.claude/rules/` and `.cursor/rules/` copies follow) gains one table row naming the null-control refusal. The owner's approving review, or the orchestrator under the mandate in force, is owed before merge.
