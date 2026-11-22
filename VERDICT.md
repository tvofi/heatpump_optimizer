Fix review: merge 08c19e58ae3381a6c726f4c5f2efb1e624451c48

bus-nonce: a593ba56db653aca64250e14c5077bbd

Round 2 of #3735: the delta from the reviewed head 20edc8b3cd (`Fix review: merge 20edc8b3cd...`, probe/rev-3735-498d9347) to 08c19e58ae. `review_carry.py 20edc8b3cd 08c19e58ae` prints `FRESH-REVIEW` because tests/structure_budgets.json changed, so this round takes that delta and re-runs the cheap checks at the new head. Worktrees were detached at head 08c19e58ae, at merge base f269ecccb5, and at the merge of the head with origin/main 505ed38e97.

Note: body-stale: the body's `## Head` names f0f7ff15c2 as the head. The head is now 08c19e58ae, which is the bot's `ci: merge main` of f269ecccb5 (#3729) on top of it, and `review_packet` refuses `head-note`. The PR's own diff is unchanged by that merge. Carry: dismissed: paperwork; the body is refreshed by update_pr.sh at the next body push and blocks nothing (C5)
Note: root-cause-unanswered: codeql / Analyze (python) failed in run 44970786457 (job 137054838963). The check output is empty and its log returns HTTP 404 to this seat. The same check passed at this head in run 44970777378 (job 137088965863), but `gate` (job 137088940481) still read the failed run. It is in the owed-reds set and `## Red checks` does not name it. The diff touches only tests/structure.py, tests/structure_budgets.json and dev/programme/delivery/3735.md. Carry: dismissed: a C5 note for the orchestrator at merge; the re-run at the same head is green and no code of this PR is implicated

## Evidence

- Delta: on its first-parent line, 20edc8b3cd..08c19e58ae holds three bot `ci: merge main` commits (5e4a4a6a24, d4bd8ed29e, 08c19e58ae), the merge f0f7ff15c2 and one PR commit, 611f843468, which re-records `module_excess_loc` 21718 -> 21779 and moves `recorded_at` to 4ebd430fbf. I compared `git diff a8efe1d1c2...20edc8b3cd` with `git diff f269ecccb5...08c19e58ae`. The tests/structure.py hunks are identical apart from line offsets. The budget file differs only in the `module_excess_loc` value and `recorded_at`; `class_excess_loc` 17317 and `seam_cut_total` 413 are main's own values carried in through the merges. No `custom_components/` file is in the PR's own diff, so nothing widens the review.
- Merge with main: `git merge-tree --write-tree origin/main 08c19e58ae` rc 0, tree f5b1ef41cb, no conflict (`ev/merge-tree.txt`). origin/main 505ed38e97 is ahead of the merge base f269ecccb5 and changes no `custom_components/` file after it.
- Structure at the head: `PYTHONPATH=tests/hastub python3 tests/structure.py` printed `const_modules_over_50 4 <= 4`, `module_excess_loc 21779 <= 21779`, `STRUCTURE RATCHET PASSED`, rc 0 (`ev/structure_head.txt`). The same command on the head merged with origin/main 505ed38e97 printed the same lines, rc 0 (`ev/structure_merge_main505ed38e.txt`).
- The +61 re-record, re-derived by an independent text rule rather than the PR's AST (`ev/prior/recount.py`: the last non-blank, non-comment line of each module past 2000, summed; `ev/recount.txt`):
  - main's first parents a8efe1d1c2 21718, 35402f7817 (#3737) 21816, 6fdc15354f 21816, 4ebd430fbf (#3728) 21779; f269ecccb5, origin/main and the head are also 21779.
  - #3737 moved pump_arbiter.py 283 -> 375 (+92) and coordinator.py 9393 -> 9399 (+6).
  - #3728 moved pump_arbiter.py 375 -> 360 (-15), coordinator.py 9399 -> 9376 (-23) and sensor.py 1205 -> 1206 (+1).
  - Every figure in the body's `## Head` and in 611f843468's message re-derives. No line of this PR moves the row.
- Re-record reason: 611f843468's commit message states the reason, the moving modules and the ruling it records under, as rule 2 requires. `module_excess_loc` is a new row, absent on main, so it is not a raise the gate reads.
- Mutation proof, re-run at 08c19e58ae (`ev/prior/mut.py`, `ev/mutants.txt`): the same 8 mutants as round 1, all killed. A (binding read off) and B (`module_excess` zeroed) each produce 2 self-check FAILs, as the body states. C (alias ignored), E (`end_lineno` -> `lineno`) and H (limit off by one) fail the self-checks. D (const filter dropped) and G (attribute read off any name) breach `const_modules_over_50 6 > 4`. F crashes the run, rc 2. After the run the file was restored and the worktree is clean.
- Finder's harness: m1_ratchet_census.py from plan/r11 819aa2e354, sha1 e2f94c69129a1e2840e5b4b83e67dab96b576f7b, which is the body's figure (`ev/harness-sha1.txt`). I ran it at both ends (`ev/census_*`).
  - Base f269ecccb5: `ratchet_const_modules_over_50=3`, `any_spelling=4`, `const_unseen_modules=1`. `--perturb const-respell` drops the ratchet to 2 while any_spelling stays 4. `--perturb module-growth` moves `coordinator_py_unpriced_loc` 2951 -> 4374 with `ratchet_rows_off_budget=0`. This is the defect.
  - Head 08c19e58ae: ratchet 4, `const_unseen_modules=0`. const-respell keeps the ratchet at 4. module-growth reads `ratchet_rows_off_budget=1 (module_excess_loc 21779->23202)`. This is the fix.
  - The base's unpriced figure is 2951 where the body quotes 2963 at e698fc8ac3. #3728's coordinator.py shrink explains the difference; the direction and the null-control shape hold.
- Earned movement (step 14): round 1's analysis stands, because the counter code is unchanged. Removing the mechanism (mutant A) returns the const row to the from-import count. The only budget value new in this delta, 21779, is main's measured growth (above) and not produced by the instrument.
- VERSION, the manifest, RELEASE_NOTES.md and tests/golden are untouched. No claim file is owed.
- CI: I polled `merge_train.py classify 08c19e58ae... --pr 3735` from 03:36 to 04:09 UTC (`ev/classify.log`). It read WAIT until 04:09:45, then `RED 08c19e58ae3381a6c726f4c5f2efb1e624451c48 pending: none red: gate` (rc 1), not APPROVAL-OWED. `gate` (job 137088940481) prints three reds, all from run 44970786457 (`ev/ci-reds.txt`):
  - `codeql / Analyze (python)`: the Note above; green on the re-run.
  - `budget-raise-gate / budget-raise-gate`: the approval that follows this verdict for `const_modules_over_50: 3 -> 4`.
  - `pr-contract / pr-contract` (jobs 137084188245 and 137088941589): `[figure-block] line 54: block scope-line names head=f0f7ff15c296 mb=4ebd430fbff9, this run is head=08c19e58ae33 mb=f269ecccb5f1`, and `FAIL closed: this run's codeql jobs were not listed finished after 600 s`. These come from the stale body (Note above) and the CodeQL run.
  - None of the three is a code, test or harness defect, so none blocks (C5). The relay holds this `merge` until CI reads green at this head: a refreshed body and figure block, a fresh gate run, and the approval.
  - The owed-reds set is in `ev/owed-reds.txt`.
- Review packet: rendered at this head with REFUSE `head-note` and `red-unanswered` (both are Notes above). The packet's carry_audit read 0 items, and figure_lint resolved 4 with 1 not verified. That one is the scope line, which the body renders at f0f7ff15c2; I did not re-derive it.
- The role contract was read from origin/main 505ed38e97, the current version.

## Findings

- Out of scope: `const_names_read` does not see a `getattr(const, <name>)` read. thermal_model.py has three, all with dynamic names, and the module is already over the limit at 137 names, so no row depends on them. This is unchanged from round 1. Carry: dismissed: no module's row depends on it; the names are dynamic and cannot be resolved statically
- Residual: at the head the finder's harness prints `RECOUNT const_modules_over_50 ratchet=4 recount=3 MISMATCH`, because its recount keeps the from-import rule this PR replaces. Its `any_spelling` arm reads 4 at both ends. The body discloses this. Carry: dismissed: a round-11 audit instrument pinned to the pre-fix rule, not a defect of this PR
