Fix review: blocked c0bc81e0a196a6aeb5fdb386fe85be385a0e53d3 ci-red: required gate is red at this head on tests / mutation's 32 unpinned sites and mutation-autofix was cancelled, so no pin commit comes; no code defect found

bus-nonce: 9eae24af387cf455ef72ab7ddbaa275a

Round 2: a delta review over the reviewed head efc63b60e8a9cf5e90adc1fea09bc584bddf8fe0. The round 1 code block is resolved. The only blocker is the red required check.

## Block

- `merge_train.py classify c0bc81e0a196a6aeb5fdb386fe85be385a0e53d3 --pr 3670` prints `RED c0bc81e0a196a6aeb5fdb386fe85be385a0e53d3 pending: none red: gate` (rc 1), read twice, the last time at 23:18Z (`ev/classify.txt`). `bus.sh post` refuses a merge verdict at a red (C8), and the relay refuses a `pending-ci` draft over a red, so this round cannot return a merge.
- `gate` (job 133661326036, `ev/ci_gate_133661326036.txt`) fails on two lines. The first is `FAIL tests / mutation: failure (run 43941602050)`. The second is `pr-contract: no run at this head judged base 'main'`, because pr-contract was skipped at this head.
- `tests / mutation` (job 133563694805) prints `MUTATION TABLE REFUSED -- 2197 unpinned site(s) against 2165 at the ratchet base 92d38ecb64..., 32 of them added by this diff`, as 27 `ADDED UNPINNED` lines (`ev/ci_mutation_133563694805_tail.txt`). This is the pin lag the body answers. The repair it names did not happen: `tests / mutation-pins (4)` ran 20:04Z to 22:29Z and was cancelled, and `tests / mutation-autofix` (job 133661095737) was cancelled at 22:29:10Z. Run 43941602050 (`CI code`) concluded `cancelled`. Under `ci-autofix.md` a cancelled autofix pushes no bot commit, so waiting does not clear this red.
- Repair: re-run the `CI code` run at this head so the pins and autofix finish, or pin locally with `python3 tests/mutation_table.py --pin-killed --base origin/main`. Either way, the pr-contract run at the new head must judge base `main`. If the head moves by a pin commit only, `review_carry.py` should answer whether this round's code findings carry.

## Findings

- Follow-up: `tests/finite_boundary.py` still has no store-wide check that refuses a `whole=` declaration whose cell costs only itself (round 1's follow-up). This diff's new `metered floor, declared cost` check settles it for the two leaves the diff adds. The body names `draw/engaged` (on main before this diff) as the first sibling. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR (pending orchestrator ruling on a store-wide whole cost check, the fixer.md exception the body names)
- Residual: no committed finder harness exists for this group. The body discloses it, and the approved design's mutation targets and null controls stand in. Carry: dismissed: disclosed in the body; an outside finding whose rows are a range, approved design's own harness stands in
- Residual: round 1's mutant M13 (dropping `np.isfinite(floor) and` in `_stored_floor`) is equivalent behind `_sanitize`. Carry: dismissed: equivalent mutant behind the store boundary's _sanitize

## Notes

- Note: root-cause: the owed red `gate` is not named in the body's `## Red checks`. Its only FAIL is `tests / mutation`, which the body answers as pin lag. That answer now needs updating: the autofix was cancelled, and pr-contract did not judge base `main`.

## Evidence

- Head reviewed: c0bc81e0a196a6aeb5fdb386fe85be385a0e53d3 (`ev/HEAD.txt`). It was still `refs/pull/3670/head` when this verdict was written. Contract drift: `git diff $(merge-base)...origin/main -- dev/governance/roles/` touches only `COMMON.md` (the finder's contract), not `fix-review.md`.
- Delta: `git log efc63b60e8..c0bc81e0a1` has one PR-own commit, 95e70c96d4. It edits `store.py` (the `_ACCURACY` declarations `draw/floor_kw: Domain("real", _POS)` and `draw/floor_since: _COUNT`, with `whole=_DRAW_KEY` dropped) and adds 34 lines to `tests/features.py`. Everything else is main merges (f4e48cca12, c0bc81e0a1). The PR's own three-dot diff is 31 files, the same file list as at efc63b60e8. No path widening: `grep -rn '\.whole' custom_components/` finds no reader, because `whole` is declaration metadata that only tests read. Dropping it changes no runtime behaviour.
- Round 1 block resolved: both floor leaves now declare no `whole`. The new check reads each leaf's declaration from `store._ACCURACY` and compares it with the cost `DrawRange.from_dict` measures for the round 1 probe's bad values. At the head, the extracted floor block up to that check prints `ALL 5 FEATURES BLOCK PASSED`.
- Reviewer mutants (`ev/reviewer_mutants.txt`, driver `ev/reviewer_mutants_driver.py`, every file restored, `git status` clean afterwards), run against that extracted block: R1 restores `whole=_DRAW_KEY` on `draw/floor_kw` and is KILLED rc=1. R2 does the same on `draw/floor_since` and is KILLED rc=1. R3, a loader that drops the samples on a bad `floor_kw`, is KILLED rc=1. R4, a loader that drops the samples on a non-int `floor_since`, is KILLED rc=1. 4 of 4 killed. Each failure's message names the declared/measured mismatch, so the check binds both directions (declaration and loader).
- `finite_boundary.py`: `ALL 114 FINITE BOUNDARY CHECKS PASSED`. `structure.py`: `STRUCTURE RATCHET PASSED` (`ev/cheap_checks.txt`).
- Claims: `tests/env_drift.py --all 92d38ecb64` at the head prints `CLAIMED` for exactly coord_all_features, coord_dhw, coord_grid_fee, coord_minimal and coord_two_zone (3 leaves each), then `NO UNCLAIMED DRIFT: 56 scenario(s) checked` and `NO STALE FIXTURE`, rc 0 (`ev/env_drift_all_vs_92d38ecb64.txt`). The three-dot diff leaves `card_claimed_drift.txt` untouched. `VERSION` is 10.0.2.
- Versions: the three-dot diff of `VERSION`, `manifest.json` and `RELEASE_NOTES.md` is empty.
- Merge: `git merge-tree --write-tree origin/main c0bc81e0a1` at origin/main c82f014a63 returns rc=0 (tree 683bb51113), with no conflict (`ev/merge_tree.txt`).
- Body head line: the body's `## Head` names c0bc81e0a196a6aeb5fdb386fe85be385a0e53d3 as a clean main merge, which matches.
- Other reds at the head, outside the owed set `merge_train.py owed-reds` prints, so neither answered nor blocking: `tests / replay` (1 of 198 failed, `owner-2026-10-30-away.json: cycle_cost cpu_ratio 443.9 over its budget 332.8`, `ev/ci_replay_133566336613_tail.txt`) and `tests / nightly-status` (answered in the body).
- I did not re-run the gate or the full mutation table, which are CI's job. The body's figure `ALL 5733 FEATURE CHECKS PASSED` is not re-derived. CI's `tests / fast (3.14)` is green at this head.
- Class: one seam (the configured floor's declarations), unchanged from round 1. Release (step 16): the delta adds no refusal on an actuator write.
