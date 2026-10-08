Fix review: blocked e50d432ee51655915c2ec272ba1e1d3939615706 other: step 11's "newest pr-contract run re-checked the body" and "Never wait on coverage" contradict at class B; the re-check is keyed on workflow completion, which waits for coverage

bus-nonce: ef6e23e5a4be7260669f4cfe46a0d320

Round 1. Measured head `e50d432ee51655915c2ec272ba1e1d3939615706` (merge base `af79f2114`), read from a detached worktree. Policy was read from fresh origin/main `af79f2114`. The contract is unchanged between the merge base and main.

## The block

The new step-11 text sets two conditions for a `root-cause-unanswered` block: (a) the head's required checks have settled, and (b) the newest `pr-contract` run has re-checked the body. It then adds "Never wait on `coverage`, `delivery-status` or `nightly-status`: not required."

The re-check does not follow required checks. `pr-contract-rerun.yml` runs on `workflow_run: completed`. `tools/pr/contract_rerun.py:66` compares the newest contract run's start with the triggering **workflow run's** `updated_at`. `coverage` and `nightly-status` are jobs in `Tests`, next to the required `fast (3.14)`, `closures`, `mutation`, `browser`, `briefs` and `typing`. `delivery-status` is a job in `Governance`, next to the required `policy-docs`, `env-matrix` and `wave-script`. So when a required `Tests` job turns red, the contract is re-checked only after `Tests` ends, and `Tests` ends only after `coverage` ends.

This head shows the gap (`evidence/check-runs.12.json`):

- The last required check settled at 17:21:44Z (`Analyze (python)`).
- `coverage` ran from 17:00:36Z to 18:00:54Z.
- The newest `pr-contract` run started at 18:01:29Z, 35 s after `coverage` ended, and about 40 min after every required check had settled.

Class B is the class this change targets: a required check goes red after push and the body is silent. In that case the reviewer cannot obey both sentences. Condition (b) says to wait for the re-check, which means waiting on `coverage`. The last sentence says never to wait on `coverage`. A reviewer who follows the last sentence posts on a stale contract run, which is exactly class B again.

A second ambiguity: "re-checked" has no ordering anchor. Take a head where the red is on an earlier commit (RCA class D). No red concludes at that head, so no re-run ever comes. The push-time run is then the only run, and the text does not say whether that run counts as the re-check.

Section 6, item 3 of the RCA already states an anchored form: the head's workflows concluded, and the newest `pr-contract` run at the head started after them. The cost it states is a wait of up to one `Tests` run.

A suggested repair, for the fixer to choose (not imposed):
- Anchor the re-check as "a `pr-contract` run at the head that started after the last red check concluded".
- Then either drop the "Never wait on coverage..." sentence, or limit it to "their own state never holds a verdict".

This probably also shrinks the raise. If the repair changes what option 2 means, it goes back to tvofi.

## RESULT lines

- RESULT policy_lint at head: `TOTAL: 0 error(s) across 40 policy file(s)`, rc 0 (`evidence/policy_lint.head.txt`).
- RESULT structure.py at head: `STRUCTURE RATCHET PASSED`, rc 0 (`evidence/structure.head.txt`).
- RESULT entities.py at head (CI venv, `PYTHONPATH=tests/hastub:custom_components:tests`): `ALL 2212 ENTITY CHECKS PASSED`, rc 0 (`evidence/entities.head.txt`).
- RESULT mutation (raise removed, text kept): 2 `[budgets]` errors on fix-review.md, 142 > 140 lines and ~2461 > 2393 tokens (`evidence/mutant_no_raise.txt`).
- RESULT control (raise and text both reverted): 0 errors (`evidence/control_no_raise_no_text.txt`). The raise is used only by the step-11 text.
- RESULT raise is minimal for this text: the measured size equals the new cap exactly, 142/142 lines and 2461/2461 tokens (`evidence/budgets.head.txt`). The base is 138 lines and 2387 tokens (`evidence/budgets.base.txt`).
- RESULT not stated in the body: the corpus goes from ~59562 to ~59636 tokens. That crosses its cap of 59591 into the +500 band (60091). This is not a lint error, but the body's Figures section says it lists corpus totals and gives none.
- RESULT orchestrator.md: 290 lines and 4096 tokens at both ends, within cap. The edit pays for itself, as the body says.
- RESULT required contexts: the live ruleset 23698884 equals `tools/policy/fixtures/required-contexts.json`, 17 contexts (`evidence/ruleset.raw`). None of `coverage`, `delivery-status` or `nightly-status` is required; `pr-contract` is. The sentence's list is correct as a statement of fact.
- RESULT RCA figures (from `origin/fix/r9-rca-2028` 5964b583, `dev/audit/rca/R9-RCA-2028.md`):
  - 19 blocks; A = 7 and B = 5, so 12 of 19 (section 2).
  - 7 body-only rounds totalling 574 min; A = 2 rounds and 249 min (#2007, #2049), B = 1 round and 92 min (#2018), so 3 of 7 rounds and 341 of 574 min (section 6).
  - The body cites these correctly and ties the minutes to rounds, not to the 12 blocks.
- RESULT head checks, read from the API (`evidence/check-runs.12.json`; this verdict was posted only after all 38 runs completed):
  - Red: `budget-raise-gate` x2. It is red only for want of the owner's approval and is answered in `## Red checks`; this is not a block.
  - Red: `nightly-status`. It grades main, and the diff touches none of its inputs (defect-root-cause.md).
  - `pr-contract` is green on all three runs: 17:00:03, the re-run at 17:00:56, and 18:01:29.
- RESULT `## Approval`: it records tvofi's option-2 choice and the "raise the cap" confirmation before the push, and says a merge needs tvofi's approving review at the head. That is correct for a policy and budget raise. The approval is the orchestrator's to give under mandate 5951564627. Not given here.
- RESULT VERSION, manifest and notes heading: untouched (the diff is 4 files under dev/).

## Non-blocking

1. `.claude/workflows/web-fix-wave.js:305`, the reviewer prompt, teaches `root-cause-unanswered` with no settle condition. A wave-dispatched reviewer reads that prompt. Carry it, or say why not.
2. The null control names base `b296779f0`, while the merge base is `af79f2114`. The governance and policy-tool trees are identical between the two (`git diff --stat` is empty), so this is immaterial.
3. In `## Head`, the authored-head SHA is repeated as a bare line at the end of the section.
4. defect-root-cause.md:140 still names the verdict `blocked: root-cause trigger unanswered for <check>`, a shape that differs from step 11's grammar. This predates the PR.
