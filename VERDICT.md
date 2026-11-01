Fix review: merge 9cddcb4f673ee4bed26a316c4a22128433414eb8

bus-nonce: da2390ae2ac258586b5bd20a531539e9

## Summary

Round 5 of this group's fix review. This is a scoped re-check of the range `7f6d7e72..9cddcb4f` under the r4 verdict (`verdict/3047`, merge at `7f6d7e72`). I measured from a detached worktree at `9cddcb4f673ee4bed26a316c4a22128433414eb8`, against origin/main `407eb0cb38f3cd43e71f4ed7be1c23f80dc32cc1`.

The range holds two commits. The first is the bot's `ci: pin killed mutants` (`2df0b81e`): 13 killed_by records and nothing else. The second is one automatic merge of origin/main at `407eb0cb`, which itself contains `ca6333333`. That merge needed no resolution. Every item in the brief is answered, so the verdict is merge.

The head moved during the review. It went from `9cddcb4f` to `ace2e21a6f22cc3e9af22b5b1eed6a92b55105d9`, which merges the handoff tip `3f9f152e`. That commit has the same tree, `e58eadb7`, and `review_carry.py 9cddcb4f ace2e21a` prints `CARRY` (all three of its branch-only commits are automatic merges). By fix-review.md step 12 this verdict therefore attaches to `9cddcb4f` and carries to `ace2e21a`; it is not a head-moved case. CI at `9cddcb4f` was cancelled when the new head superseded it, so the CI evidence is taken at `ace2e21a`, the same tree.

## Findings

- The PR body's `## Head` lists `2cfd6be38070335f5cdd8d4caa08b4ebfb7a1401` and `7aa2a455bfcc26d8ec035b7bc3a5233bf4dd994f` as merges of `ca6333333`. Neither commit is on the remote: `git fetch` answers `not our ref`, and neither is an ancestor of the head. The actual merge of `ca6333333` is `895f0315` on the handoff branch. `## Head` also does not name the live head `ace2e21a`. It does name `9cddcb4f`, which carries, so step 7 is met. Fix by editing the body: drop the two phantom lines and add `ace2e21a` (the handoff merge, tree-identical). Carry: R10-FACTORY-RESET
- The current-head paragraph of the body's `## Red checks` was written at `2df0b81e`, 18:09 UTC. It still says `tests / mutation` is `in_progress` with "green is not yet read". At the live head that lane now reads `MUTATION TABLE PASSED`. Every red at this head is still named and answered in the body (`budget-raise-gate / budget-raise-gate`, and `gate` as its aggregate), and `pr-contract / pr-contract` passed after the last red. So the trigger is answered, and only the wording is stale. Fix by editing the body to bring the paragraph up to this head. Carry: R10-FACTORY-RESET
- The `seam_cut_total` 422 -> 423 raise still needs the owner's approving review at the head before `budget-raise-gate` (and therefore `gate`) can go green. This verdict does not give that approval. Carry: R10-FACTORY-RESET

## Evidence

Contract: fix-review.md was read from origin/main, and `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty because the merge base is origin/main. The review packet was rendered here (ev/review-packet-2.md, ev/review-packet-ace2e21a.md). Its `handoff-not-applied` refusal is the one the orchestrator overrode. Its `required-red: gate` refusal is answered below.

(1) Range and bot commit (ev/range.txt, ev/branch_only_compare.txt, ev/review_carry.txt, ev/merge-tree.txt):
- The first-parent range `7f6d7e72..9cddcb4f` is `2df0b81e` (author `github-actions[bot]`, subject `ci: pin killed mutants`) followed by `9cddcb4f` (a merge of origin/main `407eb0cb`).
- `git diff --name-status 7f6d7e72 2df0b81e` lists 13 paths, all `A`, all under `tests/mutation_ledger/killed_by/`, for 78 insertions. No production line, test line or budget line is touched.
- RESULT: re-doing `git merge-tree --write-tree 2df0b81e 407eb0cb` gives `e58eadb7b511cae6dacae67a63891bdd6cfad5b7`, which is the head's own tree. So the merge carries no resolution.
- Branch-only diff, three-dot, compared at `7f6d7e72` (base `d052f80f7`) and at the head (base `407eb0cb`): the file lists differ only by the 13 records. RESULT: 0 changed lines differ other than those records' added lines. No branch-own production line changed in the merge.
- `review_carry.py 7f6d7e72 9cddcb4f` prints `FRESH-REVIEW` (rc 1), because the pin commit is branch-only content. That is why this scoped re-check exists, and every record has been checked below.
- Dispatch override basis, re-derived: `git merge-tree --write-tree 9cddcb4f 3f9f152e` gives `e58eadb7…`, equal to `9cddcb4f`'s tree. The equality holds.

Records (ev/ledger_records.txt):
- The 13 anchors are `_current_humidity CMP_BOUND` (the CMP_BOUND*2 pair, one anchor); `_dhw_probe_temperature` BOOLOP and GUARD_OFF; `_async_rewrite_entry GUARD_OFF`; `_async_undo_factory_reset RETURN_DEL`; `async_factory_reset.voided` GUARD_OFF and RETURN_DEL; `entry_config` `_side_pair GUARD_OFF`, `undo_point` GUARD_OFF and RETURN_DEL, `undone_settings` GUARD_OFF and RETURN_DEL; and `services.handle_factory_reset GUARD_OFF`.
- That is 13 records, matching the r4 verdict's 5 + 4 + 4 = 13 shard anchors and the 13 sites the body's `## Unpinned sites` lists as discharged.
- The ledger reader `tests/mutation_table.py` at the head reports: `ledger_form_problems` [] and `layout_problems` [], so the files are well-formed. `stale_pins` returns 0 in total, and each record's `old` text is present in its file. Each record's key set is {anchor, killed_by, old, reason}, and each sits at its `ledger_relpath`.
- CI's `tests / mutation` at `ace2e21a` (same tree) prints `PIN RE-VERIFICATION: 9 reproduced, 0 not reproduced` and `1 survivor(s) of 10 evaluated = 0.0% (1 triaged equivalent ...)`, then `MUTATION TABLE PASSED`. The one survivor is `entry_config.py:360 RETURN_DEL`, the triaged trailing `return None` that r4 agreed with. This is a real evaluation, not `INCONCLUSIVE`.

(2) Body (read live at 20:2x UTC):
- The r4-owed edit has landed. `## Mutation proof` carries Round 3 at `fcbf8ec95`: U6 and U7 killed, the null control, and the two equivalent `return None` triages. `## Figures` carries the [round 3] line: 31 FR checks, 4713 feature checks, 2499 entity checks. `## Red checks` carries the `d1662cf7b` `_svc_fr_record` stub red, with its cheaper detector (`tests/entities.py` whole on Linux).
- `## Red checks` answers `tests / mutation` at `7f6d7e72` (the 14 added sites, answered by the bot's pins), `tests / mutation-autofix`, and `budget-raise-gate` (red until the owner's approval). It also covers `gate` (the aggregate; it follows those) and `pr-contract`.
- `## Unpinned sites` accounts for the bot's 13 records against its 19 lines.

(3) Raise:
- The `## Raise justification` is unchanged from what r4 judged: six payments, and `Architecture score: dS +0.0030 IMPROVES`.
- `budget_raise_gate.py --check-body` on that section, `--base 407eb0cb --head 9cddcb4f`, prints `the body's \`## Raise justification\` names the payments tried and the arch_score figures`, rc 0 (ev/check_body.txt).
- RESULT: at the head, `score.py --diff 407eb0cb` gives `Architecture score: dS +0.0030 IMPROVES`, `coord_footprint 2387 -> 2382` (ev/archscore_head.txt). The Architecture score line stands.
- RESULT: `tests/structure.py` gives `seam_cut_total 423 <= 423`, `STRUCTURE RATCHET PASSED`, rc 0 (ev/structure_head.txt). The three-dot budget diff shows `seam_cut_total` 422 -> 423, unchanged since `7f6d7e72`.

(4) Head (ev/HEAD.txt, ev/head_moved.txt):
- At the start, `git ls-remote refs/pull/3047/head` returned `9cddcb4f…`. At 19:11 UTC it returned `ace2e21a…` and still did at verdict time.
- `ace2e21a` has parents `9cddcb4f` and `3f9f152e`. Its tree is `e58eadb7`, and `git diff 9cddcb4f ace2e21a` is 0 lines. `review_carry` prints `CARRY`, so every number above holds at `ace2e21a`.
- `## Head` names `9cddcb4f` and its merge of `407eb0cb3`.
- `git merge-tree --write-tree origin/main 9cddcb4f` exits 0 with tree `e58eadb7`. No claim file conflicts.

CI (ev/classify-log.txt, ev/classify-ace-log.txt):
- `merge_train.py classify 9cddcb4f` exited 1 (RED, `red: gate`). At `9cddcb4f`, `gate`, `tests / mutation`, `tests / fast (3.14)` and the rest were `cancelled` when `ace2e21a` superseded them (ev/review-packet-2.md), so that head can never conclude.
- At `ace2e21a` (same tree), `classify` exited 1 (RED, `red: gate`). The `gate` log (job 124965229240) reads only `FAIL budget-raise-gate / budget-raise-gate: failure`.
- At `ace2e21a`, `budget-raise-gate` concluded failure (two runs) and `gate` follows it. Every other check concluded success or skipped. That includes `tests / mutation`, `tests / fast (3.14)`, `tests / closures`, `tests / coverage`, `tests / typing`, `governance / instrument-self-tests` and `codeql / Analyze (python)`.
- `pr-contract / pr-contract` succeeded at 20:08 UTC and again in run 124964535572, which started 20:13 UTC, after the last red (`budget-raise-gate`, 20:10:58). So the body's red-check record was checked after the last red concluded.
