Carry 1 (the group's only carry) is built in full. Owner ruling (tvofi, 2026-11-07, triage P419, batch 136 entry 427, carry 0): a fixer hands off at its first clean `prepr.sh` head and merges origin/main only when `git merge-tree --write-tree origin/main HEAD` conflicts; a reviewer blocks on main only on a merge-tree conflict. The rendered fixer prompt (`tools/audit/seat/cloud_dispatch.py`) no longer instructs a re-merge and second prepr run on a moved main; the rendered reviewer prompt and `fix-review.md` step 13 block on main only on a merge-tree conflict. `fixer.md` already states the conditional rule (line 93), so no carry to R10-FIXER-MD-SPELLING-CORPUS is owed. The `--preamble` flag is not built (unmeasured benefit). Instrument doc updated. fix-review.md is code-owned policy and merges under mandate 6715477401 or on tvofi review.

## Head

bc59a13f63cb2280b602b90ec9f700aa6c98f115. Base 8a4cf2618c53 was behind main (8a4974d1522f); `git merge-tree --write-tree origin/main HEAD` is clean, so no merge was made, per this change's own rule.

## Mutation proof

Restoring the unconditional sentence ("when origin/main has moved ... `git merge origin/main`, rerun") fails check "the fixer hands off at its first clean prepr.sh head and re-merges main only on a merge-tree conflict". Reverting the reviewer line to "(`git merge-tree --write-tree`)" failed the reviewer arm (observed: the first self-test run, before the reviewer edit landed, printed FAIL on "the reviewer blocks on main only for a merge-tree conflict, never a clean head behind main"; 129 checks, 1 failed).

## Null control

Third new check: no role other than the reviewer carries "behind main but merges cleanly" in its prompt. The probe and other role prompts are unchanged. After the fix `python3 tools/audit/seat/cloud_dispatch.py --self-test` prints 129 checks, 0 failed.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none

## Approval

Owed, not yet given: this diff changes `dev/governance/roles/fix-review.md` (step 13, one sentence). The change implements tvofi's own 2026-11-07 ruling quoted in the carry; it merges on the orchestrator's approval under mandate 6715477401 or on tvofi's review. No approval is claimed here.
