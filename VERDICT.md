Fix review: blocked 93ba227138a2c024bf81e44e74f2b11cb572bd76 ci-red: gate is red because governance / policy-docs was cancelled at its 5-minute timeout in run 43688486622; re-run that job, and the delta review below holds

bus-nonce: 546905d0ae546008ea6b475c6ccf1f5c

## Block

- `merge_train.py classify 93ba227138a2c024bf81e44e74f2b11cb572bd76 --pr 3451` exits 1: `RED 93ba227138a2c024bf81e44e74f2b11cb572bd76 pending: none red: gate` (ev/classify_log.txt, ev/classify_last.txt). This is not APPROVAL-OWED (exit 4), unlike the previous round.
- The gate job 132741691093 (run 43688486622) prints `FAIL governance / policy-docs: cancelled (this run)` next to the expected `budget-raise-gate` red. Both `gate` and `governance / policy-docs` are in the `merge_train.py owed-reds` set (ev/owed_reds.txt).
- The job `governance / policy-docs` 132734039270 started at 07:07:47Z and ended `cancelled` at 07:12:51Z. That is the job's `timeout-minutes: 5` in `.github/workflows/governance.yml` (ev/ci_gate_red.txt).
- I ran the job's content steps locally at the head, and each one passes (ev/policy_docs_steps_head.txt):
  - `rules_sync.mjs --check`: rc 0, 0 s.
  - `codeowners_gap.py --check`: rc 0, 2 s.
  - `policy_lint.mjs`: rc 0, 36 s.
  - `fragments_sync.mjs`: rc 0, 1 s.
  - `policy_lint.mjs --hooks`: rc 0, 6 s.
  - I did not run `machinery_ratchet.py --check-event`, which needs the CI event.
- So nothing in the tree is known to fail. The required check simply never concluded.
- **What unblocks it.** Re-run `governance / policy-docs` at this head. Once the gate reads GREEN, or APPROVAL-OWED for the budget raise alone, every finding of this review stands as a merge, with no further review owed for an unchanged head.
- If the job times out again at this head, the PR body owes a `## Red checks` answer for it (defect-root-cause.md).

## Findings

- Residual: line 9 of the PR body is stale at this head, as it already was at 7f4a9be8. It says "39 files changed, 578 insertions, 761 deletions (`git diff --shortstat 0a8033305d...HEAD`)". That command now prints `2216 files changed, 138804 insertions(+), 9608 deletions(-)` because 0a8033305d is far behind the merge base. The PR's own diff, `git diff --shortstat $(git merge-base origin/main HEAD)...HEAD`, is `40 files changed, 602 insertions(+), 755 deletions(-)`, the same at 7f4a9be8 and at this head (ev/delta_checks.txt). The sentence's claim, deletion over machinery, still holds. Only the figure and its base are stale. The fixer can refresh it at the next body edit. Carry: dismissed: body hygiene, no later stage reads the figure, and the PR's own measured diff (40/602/755) still deletes more than it adds

## Evidence

- **Round.** This is a delta round over the reviewed head 7f4a9be89c98d6ff59dc396c479b95b73b761cf6 (`Fix review: merge`). verdict/3451 holds 6 verdicts before this one (ev/verdict_ref_history.txt), so this is at least round 7. The rounds since the merge verdicts have been merge-of-main reconciles. The brief scopes this round as a delta and does not ask me to judge a re-cut.
- **Delta structure.**
  - `review_carry.py 7f4a9be8 93ba2271` prints FRESH-REVIEW, because c3149607 is a hand-resolved merge.
  - 1efe8398 and 93ba2271 are each the automatic merge of their parents. Their trees equal `git merge-tree --write-tree` of the parents: b7b0e388 and cd15f7d7 (ev/delta_checks.txt).
  - No `custom_components/` line is in the delta, so the scope does not widen.
- **The PR's own patch is unchanged.**
  - At 7f4a9be8 it is `git diff 29b3e5a74c...7f4a9be8`; at this head it is `git diff 13cbe48de4...93ba2271`. Both are `40 files changed, 602 insertions(+), 755 deletions(-)`.
  - Their sorted `+`/`-` line sets are identical: diff rc 0 (ev/delta_checks.txt).
  - So none of this PR's slimming is undone. Every line of the head outside the patch equals main at 13cbe48de4, so none of main's changes is lost, including the 12 lines main added to `bus.sh` in #3491.
- **The bus.sh conflict resolution.**
  - `git merge-tree --write-tree 2c69fb35 7f4a9be8` reports `CONFLICT (content)` in `tools/audit/seat/bus.sh` alone, as the body says.
  - At the head, main's `HPO_SEAT_GEN` guard is at the top of `dispatch()` (bus.sh:727-729), and main's two seat_gen arms come right before the PR's card C4 `dhid()` helper and the card C5 arm.
  - `bash tools/audit/seat/bus.sh --self-test` at the head on Linux prints `bus self-test: 239 checks, 0 failed`, rc 0 (ev/bus_selftest_head.txt). That is 237 + 2, as the body says. The body's two macOS-only FAILs do not reproduce on Linux, which matches its account.
  - **Mutant A, main's side.** I deleted the `HPO_SEAT_GEN` guard (bus.sh:727-729). The run prints `239 checks, 2 failed`, rc 1, with FAIL on `dispatch under a superseded HPO_SEAT_GEN refuses and records nothing` and on its null control. The control fails because the unrefused G1 dispatch records a row and shifts the count (ev/bus_selftest_mutantA_no_seatgen_guard.txt). So main's guard and arms are live inside the resolved block.
  - **Mutant B, this PR's side.** I deleted the card C4 `dhid()` helper. The run prints `239 checks, 34 failed`, rc 1 (ev/bus_selftest_mutantB_no_dhid.txt). So the PR's half of the union is load-bearing.
- **The two refreshed body lines match the tree at the head.**
  - Line 52: `grep -c proposal-triage dev/governance/config/policy_budgets.json` prints 2 at 93ba2271 and 2 at origin/main 60aefaf7.
  - The `budget-raise-gate` line under `## Red checks`: `git diff origin/main 93ba2271 -- dev/governance/config/policy_budgets.json` moves exactly `proposal-triage.md` lines 36 -> 40 and tokens 489 -> 563. `policy_lint.mjs --budgets` at the head prints `dev/governance/roles/proposal-triage.md 40 40 563 563` (ev/budgets_head.txt).
  - These resolve both findings of the previous verdict.
  - The `## Head` paragraph is also correct:
    - It names 93ba2271.
    - #3600, #3491, #3599 and #3603 are the merges in 29b3e5a7..2c69fb35.
    - `git merge-tree --write-tree 946eb6d2 c3149607` exits 0.
    - The conflict is in bus.sh alone.
- **The owner ruling on proposal-triage.md still holds.** `git diff --name-status $(git merge-base origin/main H)...H -- dev/governance/roles/proposal-triage.md` prints `M`, not `D`. `git diff 7f4a9be8 93ba2271 -- dev/governance/roles/proposal-triage.md` is empty, so the once-per-round shape the previous round verified is unchanged (ev/proposal_triage_diff.txt).
- **Budgets on the head merged with origin/main.**
  - `git merge-tree --write-tree origin/main 93ba2271` at origin/main 60aefaf7b0d1f53a932f184e1e41efc206c435d4 exits 0, tree b3b4f7bd0f0138deabf82497dd1a52dbd023fe4d (ev/merge_tree.txt). It merges cleanly.
  - On a commit of that tree, `node tools/policy/policy_lint.mjs --budgets` prints `corpus: ~69077 tokens, cap 69333 +band 500 = 69833`, rc 0 (ev/budgets_merged.txt). That is within the corpus cap.
  - It also prints:
    - `always-loaded ~3604 / 3849`
    - `CLAUDE.md 213 221 3604 3605`
    - `role fixer ~6279 / 6352`
    - `role record ~7236 / 7905`
    - `role policy ~10012 / 10458`
- **Versions.** The PR's own patch is identical to the one the previous round reviewed, which touches no `VERSION`, manifest, `RELEASE_NOTES.md` or claim file.
- **CI at this head, live.** The reds are:
  - `gate`: the owed block above.
  - `budget-raise-gate`: the owner's approval for the raise, which follows the verdict.
  - `governance / policy-docs`: cancelled.

  Everything else that is required is green. That includes `tests / closures`, `tests / fast (3.14)`, `governance / instrument-self-tests`, `tests / mutation` and `pr-contract / pr-contract` (run 43688486622).
- **Mutation.** The delta writes no production line. The targeted mutants are A and B above.
