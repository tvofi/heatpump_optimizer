Fix review: blocked e82a26569c3d27015f74627c8e25bca42d89ce58 mutation-vacuous: M10_room_record_unsaved

bus-nonce: 0061843014489516f9df5acea4105936
pending-ci: WAIT e82a26569c3d27015f74627c8e25bca42d89ce58 pending: gate red: none

Round 1 of this PR's review (no earlier `Fix review:` verdict; the packet's scope is full, first round).

## Block

1. **mutation-vacuous: `room_record._persist`'s dirty mark (M10_room_record_unsaved).** The body claims "`duty_switch._persist` and `room_record._persist` keep their dirty marks on a failed save through `save_held`'s return value". The mutant `custom_components/heatpump_optimizer/room_record.py:72-75` makes the `if await save_held(...)` body `pass` and runs `rec.unsaved = 0` unconditionally, so a failed save drops the owed history. It SURVIVED all of these: the PR's block (`ALL 12 FEATURES BLOCK PASSED`, `ev/ev_mut3.txt`), the full `tests/features.py` (`ev/ev_mut4.txt`, rc=0), `tests/finite_boundary.py` and `tests/deployment_shape.py` (`ev/ev_mut5.txt`). These are the only test scripts that name `room_record`. The reviewer's driver (`ev/drive.py`) made the edit and restored it after each run. A re-drive with `tools/audit/seat/mutant_run.py --spec ev/m10.json --in-place` printed `SURVIVED NULL` and was then stopped at the session's 30-minute background limit before the mutant run finished (`ev/ev_mutant_run_M10.txt`). The survival therefore rests on the reviewer's driver, not on a `mutant_run.py` line. The twin mutant on `duty_switch._persist` (M9: `rec.dirty = False` unconditional) is KILLED by `tests/features.py`'s pre-existing "a pass whose read of the record failed saves nothing over it, … a save that failed leaves the change owed, and the next pass lands it" (`1 of 6041 FEATURE CHECKS FAILED`). The repair is the room-history twin of that check: a `save_fails=1` store, one `_persist`, and an assertion that `unsaved` is still owed and that the next pass lands it.
2. **stale-comment (custom_components/): `quality_scale.yaml` lines 18-21 still say the tier is platinum.** They read "every row below is now done or exempt, so that tier is the top of the scale: platinum. docs-examples was the last row short of it". At this head the diff sets `strict-typing: status: todo` and the manifest's `quality_scale: "gold"`, so these lines in the shipped register are false. fix-review.md C5: a paperwork defect on `custom_components/` blocks. Repair: state the tier the rows support (gold, short at `strict-typing` until `threadpoolctl` is typed), or say that the derived tier is in `tests/entities.py` without naming it.

## Evidence

- Head: `e82a26569c` is `1f5aac7557` (the body's head) plus one autofix commit, "ci: pin killed mutants", which adds four `killed_by` ledger pins. `tools/audit/seat/review_carry.py 1f5aac7557 e82a26569c` prints `CARRY`.
- Merge with main: `git merge-tree --write-tree origin/main e82a26569c` exits 0 (tree 4f887bd49cf2). It merges cleanly, so nothing here blocks on main.
- Role files: `git diff <merge-base>...origin/main -- dev/governance/roles/` is not empty (fix-review.md and fixer.md moved on main). The role pack was rendered from origin/main 2ceb62bf66, so the current contract was applied.
- Mutation proof (`ev/drive.py`, a scratch worktree at the head, restored after each mutant; `ev/ev_mut1.txt`, `ev/ev_mut2.txt`):
  - M1 KILLED (3 of 12 block checks).
  - M2 KILLED, and M2b (latch keyed on the coordinator) KILLED: the D1-s3-06 check each time.
  - M3 KILLED (2).
  - M4 KILLED (1).
  - M5 (the context edits the config in place) KILLED (2).
  - M6 (`opt_config=ctx._opt_config` deleted from the `ArbiterInputs` build) KILLED: the ADR-003 stale-holder check, AttributeError on None.
  - M7 KILLED: `tests/doc_claims.py` `1 of 443 checks FAILED`, the D10-s3-02 census.
  - M8 (`strict-typing` back to `done`) KILLED: `tests/entities.py` `1 of 2740 ENTITY CHECKS FAILED`, "the manifest declares the tier the register supports cumulatively" (`ev/ev_mut_M8_entities.tail.txt`).
  - Reviewer's own: M9 (duty_switch) KILLED by the full suite; M10 SURVIVED (Block 1).
  - Unmutated: the block prints `ALL 12 FEATURES BLOCK PASSED` (`ev/ev_block_head.txt`).
- Finder's harnesses, from `git archive dbdc1d95fef3 dev/audit/rounds/round11`. Each sha1[:12] matches the body. Run at merge base f269ecccb5 and at the head (`ev/ev_h_{base,head}_*`):
  - `svc_set_away.py`: `acknowledged_unparseable` 6 → 0, `cleared_existing_return` 3 → 0, `control_accepted` 1 → 1.
  - `m4_order_context.py`: `holder_torn_fields` 2 → 0.
  - `enum_m4.py`: `ctx_inplace` 2 → 0, `ctx_held` 8 → 8.
  - `platinum_rules.py`: `untyped_requirements_under_done_row` 1 → 0, `coordinator_untyped_config_entry` 1 → 0, `coordinator_untyped_under_done_row` 1 → 0, `untyped_requirements` 1 → 1, `entry_point_bare` 0 → 0.
  - `persist_seams.py`: `persist_handlers` 18 → 0.
  - `silent_broad.py --seams`: 34 → 20. Grouped by the line numbers it prints, the 20 match the body's three disposition rows: 5 recorded through a helper, 10 carried as a value, 5 secondary cleanup arms.
  - All of these match the body.
  - Not re-run: `excepts_inject.py`'s lifecycle injection, which the body ported itself (it calls it a port with a scratch reader). Its figures (9 → 0, 3 → 0, 7 → 0) are the fixer's instrument and were not re-derived here.
- D10-s1-01 seam rule: `grep -nE 'cv\.string' services.py` prints 22 lines at the head: entry_id ×10, quiet_silent_windows ×3, quiet_off_windows ×3, dhw_windows ×3, entity_id, expires_at, return_time. This matches the body. `handle_set_away` refuses before any write; `ArbiterInputs` has one production builder (`coordinator.py:4114`); no other in-place `opt_config` write remains (`grep` over the package).
- Claims: `tests/env_drift.py --claims-only f269ecccb5` prints `claims hygiene: … ok` (`ev/ev_claims.txt`). The diff touches no golden fixture or claim file. `VERSION`, `RELEASE_NOTES.md` and the manifest `version` are untouched; the manifest diff is only `quality_scale`.
- Structure: `tests/structure_budgets.json` moves `class_excess_loc` 17317 → 17313 and `max_class_loc` 7868 → 7860, both down. The body's 17322 → 17318 and 7873 → 7865 were taken against the older base a8efe1d1c2a8, and the ledger merge driver re-based them. Not gamed: `_fail_update_held` is a module function, out of the class.
- CI: see `## CI` below. The heavy runs are CI's and were not re-run here.

## Findings

none

## CI

- `merge_train.py classify e82a26569c --pr 3845` printed `WAIT … pending: gate red: none` on every run from 06:25Z to 07:37Z (`ev/classify.log`). At 07:19Z the head's check runs showed `tests / mutation-autofix` queued; `gate` red with "FAIL run(s) [44989199243] at this head are still being judged; their gate decides"; `pr-contract / pr-contract` red; `tests / mutation` red; `tests / replay` cancelled.
- Red checks: `tests / mutation` is an owed red, and the body's `## Red checks` answers it (cheaper detector `ci_predict.py`, unpinned sites the autofix pins). `gate` and `pr-contract` were still being judged by an unfinished run, so I left them unclassified here and classify decides.

