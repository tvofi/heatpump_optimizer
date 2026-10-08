A reviewer now posts `root-cause-unanswered` only after two things are true: the head's required checks have settled, and the newest `pr-contract` run at that head has re-checked the body. While that run refuses the body, the reviewer waits, or hands back without a verdict and says so. It never waits on `coverage`, `delivery-status` or `nightly-status`, none of which is required. Prepping at push is unchanged. The edits are `dev/governance/roles/fix-review.md` step 11 and `dev/governance/roles/orchestrator.md` section 11.

Evidence: R9-RCA-2028, section 6, "Not built" item 3, at `dev/audit/rca/R9-RCA-2028.md` on PR #2062's branch (not on main yet). 12 of its 19 `root-cause-unanswered` blocks are in two classes: A, where `pr-contract` had already refused the body before the verdict (7), and B, where the verdict came before the head's workflows concluded (5). Measured as body-only repair rounds, A and B account for 3 of 7 rounds and 341 of 574 minutes: A is 2 rounds and 249 min (#2007, #2049), B is 1 round and 92 min (#2018).

## Head

`93e173373d77d4b3381a55a2c0324bcb13ff1ee6`

## Approval

Owner decision, taken by tvofi in the orchestrator session's chat on 2026-10-08. tvofi chose option 2, settle-then-post, answering "2". This diff writes that option.

Budget raise: tvofi confirmed it in the same chat on 2026-10-08, "raise the cap", before this branch was pushed. `fix-review.md`'s per-file cap goes from 140 to 142 lines and from 2393 to 2461 tokens. The new step-11 text needs those 2 lines and 68 tokens. Paying for them inside the file would mean rewording existing step-11 rules, which this change was told not to do. `orchestrator.md` pays for its own edit: its bullet now points to step 11 instead of repeating the verdict string, so it stays at its cap. Merging still needs tvofi's approving review at the head, from `budget-raise-gate` and the code-owner rule.

## Mutation proof

With the cap raise and the step-11 edit together, `node tools/policy/policy_lint.mjs` reports `TOTAL: 0 error(s)`, and `tests/entities.py` reports `ALL 2212 ENTITY CHECKS PASSED`.

With the cap raise removed, `policy_lint` reports 2 `[budgets]` errors on `fix-review.md`: 142 lines over a cap of 140, and about 2461 tokens over a cap of 2393. `entities.py` reports `1 of 2212 ENTITY CHECKS FAILED`, in the template-arm acceptance, because the real template exits 1.

With the cap removed and `fix-review.md` reverted to main, `entities.py` reports `ALL 2212 ENTITY CHECKS PASSED`. So the raise is used only by the step-11 text.

## Null control

At `origin/main` (`b296779f0`), `policy_lint --budgets` measures `fix-review.md` at 138 lines and about 2387 tokens, under the old caps, and `orchestrator.md` at 290 lines and 4096 tokens. `policy_lint` reports `TOTAL: 0 error(s)`.

## Figures

- `node tools/policy/policy_lint.mjs --budgets`: per-file lines and tokens for both files, plus corpus and role totals.
- `node tools/policy/policy_lint.mjs`: total errors.
- `python tests/structure.py`: ratchet result.
- `PYTHONPATH=tests/hastub:custom_components:tests python tests/entities.py`: entity checks.
- `git show origin/fix/r9-rca-2028:dev/audit/rca/R9-RCA-2028.md`: the RCA's section 2 class table and section 6 cost test, which hold the block, round and minute counts quoted above.
- `git diff origin/main -- dev/governance/config/policy_budgets.json`: the cap raise.

## Red checks

`budget-raise-gate`: this diff raises a per-file cap in `dev/governance/config/policy_budgets.json`, so the gate is red until tvofi approves at the head. No cheaper detector exists: the raise is the change, and only the owner's review clears it.

## Forward-carry

none

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
