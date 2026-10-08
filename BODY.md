A reviewer now posts `root-cause-unanswered` only after two things are true: the head's workflows have concluded, and a `pr-contract` run that started after them has re-checked the body. While that run refuses the body, the reviewer waits, or hands back without a verdict and says so. Prepping at push is unchanged.

The edits:
- `dev/governance/roles/fix-review.md` step 11 carries the rule.
- `dev/governance/roles/orchestrator.md` section 11 points to step 11.
- `.claude/workflows/web-fix-wave.js` carries the same condition into the wave reviewer prompt, which teaches `root-cause-unanswered`.

Evidence: R9-RCA-2028, section 6, "Not built" item 3, at `dev/audit/rca/R9-RCA-2028.md` on PR #2062's branch (not on main yet).
- 12 of its 19 `root-cause-unanswered` blocks are in two classes: A, where `pr-contract` had already refused the body before the verdict (7 blocks), and B, where the verdict came before the head's workflows concluded (5 blocks).
- Measured as body-only repair rounds, A and B account for 3 of 7 rounds and 341 of 574 minutes. A is 2 rounds and 249 min (#2007, #2049); B is 1 round and 92 min (#2018).
- The RCA states the cost: no compute, and a wait of up to one `Tests` run on a review that would otherwise block.

**Round 1 repair.** The round-1 review blocked `e50d432ee` because two sentences in step 11 contradicted each other:
- "newest `pr-contract` run re-checked the body";
- "never wait on `coverage`, `delivery-status` or `nightly-status`".

`pr-contract-rerun.yml` fires on `workflow_run: completed`, so a re-check after a red required check already waits for `coverage` to finish. The coordinator decided under the round-9 mandate to anchor the rule as RCA section 6 item 3 words it, and to drop the coverage sentence. It treats this as still option 2: that sentence was the coordinator's addition, not part of the option. The anchor "started after them" also settles the review's class-D question: a push-time run that started before the head's workflows concluded does not count as the re-check.

## Head

The authored code head is `fa9ee29c2f54db8354e543a11191af875717d130`.

## Approval

**Owner decision**, taken by tvofi in the orchestrator session's chat on 2026-10-08: tvofi chose option 2, settle-then-post, answering "2". The round-1 anchoring was decided by the coordinator under the round-9 mandate, as described above.

**Budget raise.** tvofi confirmed it in the same chat on 2026-10-08, "raise the cap", before this branch was first pushed. That confirmation covered 142 lines and 2461 tokens. After the repair, the raise is lower: `fix-review.md` goes from main's 140 lines and 2393 tokens to 141 and 2442. That is exactly what the new text measures.

Paying for it inside `fix-review.md` would mean rewording existing step-11 rules. `orchestrator.md` pays for its own edit and stays at its cap.

The corpus total moves into its tolerance band: from about 59562 tokens at main `af79f2114` to about 59617 at the merged tree, over its cap of 59591 but within the 500-token band (60091). That is not a lint error, and the corpus cap is not raised.

Merging still needs tvofi's approving review at the head, required by `budget-raise-gate` and the code-owner rule.

## Mutation proof

These were measured on the tree `git merge-tree --write-tree origin/main fa9ee29c2` gives at main `af79f2114`:
- **This PR as it stands:** `node tools/policy/policy_lint.mjs` reports `TOTAL: 0 error(s)`, and `--budgets` reports `fix-review.md` at 141 of 141 lines and 2442 of 2442 tokens.
- **Raise removed, at the round-0 head:** `policy_lint` reported 2 `[budgets]` errors on `fix-review.md`, and `tests/entities.py` reported `1 of 2212 ENTITY CHECKS FAILED`, the template-arm acceptance.
- **Raise removed and `fix-review.md` reverted to main:** all 2212 entity checks pass. So the raise is used only by the step-11 text.

The round-1 review re-ran both the raise-removed case and the reverted case and got the same results.

## Null control

At `origin/main` `af79f2114`:
- `policy_lint --budgets` measures `fix-review.md` at 138 lines and about 2387 tokens, and `orchestrator.md` at 290 lines and 4096 tokens.
- The corpus is about 59562 tokens.

## Figures

- `node tools/policy/policy_lint.mjs --budgets`: per-file lines and tokens for both role files, and the corpus total, at main and at the merged tree.
- `node tools/policy/policy_lint.mjs`: total errors.
- `python tests/structure.py`: ratchet result.
- `PYTHONPATH=tests/hastub:custom_components:tests python tests/entities.py`: entity checks.
- `git show origin/fix/r9-rca-2028:dev/audit/rca/R9-RCA-2028.md`: the RCA's section 2 class table and section 6 cost test, which hold the block, round and minute counts quoted above.
- `git diff origin/main -- dev/governance/config/policy_budgets.json`: the cap raise.

## Red checks

- `budget-raise-gate`: this diff raises a per-file cap in `dev/governance/config/policy_budgets.json`, so the gate is red until tvofi approves at the head. No cheaper detector exists: the raise is the change, and only the owner's review clears it.
- `nightly-status` was red at `e50d432ee`. It grades main, and this diff touches none of its inputs (`defect-root-cause.md`), so no cheaper detector is owed by this PR.

## Forward-carry

`.claude/workflows/web-fix-wave.js`, the reviewer prompt: it now states the settle condition, so a wave-dispatched reviewer gets it as a precondition.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
