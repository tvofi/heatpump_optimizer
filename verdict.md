Fix review: blocked bbad7959ae2bacf68d01f190f28e87f849932179 root-cause-unanswered: tests / fast (3.14) is red at this head and the body's Red checks reads none; env_drift --all against main's tip cbd23f1 refuses the branch for lacking #3398's combi leaves; pr-contract refuses the body for the same omission

bus-nonce: 69316311c24df4be599be6739a04a68b

Round: second review (round 2), delta scope over the reviewed head b55fc8eb5bfce6a3c2022314116d0b19d1a901e6. Measured head: bbad7959ae2bacf68d01f190f28e87f849932179. At return time it is still the tip of fix/r10-card-collapse (git ls-remote).

## Block

- **The required check `tests / fast (3.14)` is red at this head.** Job 130425759160 failed with `1 TEST SCRIPT(S) FAILED`. `merge_train.py classify` exits 1 with `RED bbad7959ae2bacf68d01f190f28e87f849932179 pending: none red: gate` (`ev/classify_final.txt`). `tests / fast (3.14)` and `pr-contract / pr-contract` are both in the `merge_train.py owed-reds` set (`ev/owed_reds.txt`).
- **`pr-contract` refuses the body for this red.** Job 130443885989, started 09:40 UTC, after fast concluded red at 09:23. Its error reads: `check tests / fast (3.14) is red and ## Red checks does not name it`. Every workflow at this head has concluded. The body still reads `## Red checks` / `none`.
- **Cause (reviewer's local reproduction, not the CI log line).** The CI log tail I could read shows `card_drift.mjs` passing (`card_drift: 44 state(s) moved and claimed, 1 identical`) and `harness_headers.py` passing. The fast lane's `GOLDEN_REF` was `cbd23f1c8bf6185c3a6c10f6e4aaf562417e75bf`, main's tip after #3398 (fix/r10-combi-tank-b) merged. This branch forked at a7628041dc02e298c5399003d4c0576391dd5c4e, before that merge. I ran `CLAIM_HEAD=bbad7959… PYTHONPATH=tests/hastub python3 tests/env_drift.py --all cbd23f1c8bf6185c3a6c10f6e4aaf562417e75bf` at the head and got rc=1. It reports `DRIFT` on config_flow, coord_all_features, coord_dhw and others, all on combi and legionella leaves `present on one side only`, then `This branch moved scenarios the baseline does not move` (`ev/env_drift_all_vs_main_tip.txt`). Every other fast-lane script I re-ran at the head exits 0: doc_claims, md_tables, layout, deployment_shape, entities, features, plan_view, card.mjs. So env_drift is the one failing script. The CI log section naming it was too large to fetch through the job-log API (526 KB tail), so the attribution rests on this reproduction.
- **Not a production defect of this PR.** `git merge-tree --write-tree origin/main bbad7959…` exits 0 with no conflict (`ev/merge_tree.txt`). The red comes from a stale base, not from the card change. It still blocks, because a required check is red at this head and the body leaves it unanswered (defect-root-cause.md Enforcement; fix-review step 11).
- **What clears it.**
  1. Merge origin/main into the branch. It merges cleanly. Let fast re-run against the current tip.
  2. In `## Red checks`, name `tests / fast (3.14)` at bbad7959 and answer the trigger: the cheaper detector (e.g. `env_drift.py --all origin/main` or a main merge before the push) with its standing cost, or the finding that none exists, because main moved under the run (state d).
  No card or test change is needed. Every item of the round-1 block is resolved; see Evidence.

## Findings

none beyond the block

## Evidence

- Round-1 block, item by item:
  - **R1 (fold reset on hass refresh): resolved.** `R1_reset_on_refresh: KILLED rc=1 fails=1` on the new check `collapse: a hass refresh rebuilds the card and keeps each fold as it was`. That check carries its own precondition: the moved savings figure 98.76 is present and 12.34 is gone, so the card did rebuild.
  - **R2 (focus to the card copy behind the dialog): resolved.** `R2_focus_first_copy: KILLED rc=1 fails=1` on `collapse: focus returns to the dialog's copy of the pressed header`. That check asserts 4 heads before and after, and activeElement at index 2.
  - The body quotes both as 1 FAIL each, which matches.
- Mutant driver at the head (`ev/mut_driver.py`, `ev/mutants_all.txt`): the finder's (round-1 reviewer's) driver, run against `tests/card.mjs`, and the file is restored after each run. `git -C <worktree> status` was clean afterwards.
  - NULL: SURVIVED (rc 0), as a null must.
  - M1 KILLED (7 fails), M2 (21), M3 (7), M4 (2), M5 (1), M6 (5), M7 (2).
  - R1 KILLED (1), R2 (1), R3 (4), R4 (1), R5 (3).
- The class sweep, each claim of the body's new claim table re-proved with the reviewer's own mutant:
  - R6, the chart ignores the saved `hidden`: KILLED (6).
  - R7, a chip toggle without `save()`: KILLED (2), incl. the fresh-card arm.
  - R8 (= body M8), divider rule removed: KILLED (1).
  - R9 (= body M9), summary nowrap/ellipsis: KILLED (1).
  - R10 (= body M11), an id on the fold head: KILLED (2).
  - M10, `visible: true`: KILLED (6), as the body says.
  - M12, the `hl-stats` block moved after the folds: KILLED (1), as the body says.
- Body figures checked: the round-1 per-mutant fail counts (R1 1, R2 1, M8 1, M9 1, M10 6, M11 2, M12 1) all re-derive at this head. M1-M7's counts in the body are quoted at d7c39135, an earlier head. The higher counts here (M1 7, M4 2) come from the new checks also failing, which is consistent.
- RESULT `PYTHONPATH=tests/hastub node tests/card.mjs` at the head: `ALL CARD CHECKS PASSED`, rc=0 (`ev/card_head.txt`, after `tests/plan_view.py`).
- RESULT from the reviewer's local re-run of the fast lane's other scripts at the head: each rc=0 (`ev/doc_claims.py.txt`, `ev/deployment_shape.py.txt`, `ev/md_tables.mjs.txt`, `ev/entities.tail.txt`, `ev/features.tail.txt`).
- The delta is test-only (`git diff b55fc8eb…bbad7959` touches `tests/card.mjs` alone, 65 insertions), so the review scope was not widened. The bbad7959 tree equals e277484c's, the authored code head the body names.
- VERSION, the manifest version and the RELEASE_NOTES heading are untouched in the three-dot diff (`ev/version_untouched.txt`).
- CI, read live: `tests / nightly-status` is red too. It is outside owed-reds, so it is not this PR's. `tests / browser` is green and `tests / mutation` is green; this round's diff writes no production line, so the mutation lane drew no new mutant.
- `ev/ci_fast_tail.log` is the last 330 lines of the fast job's log (the card_drift diff and the summary).
