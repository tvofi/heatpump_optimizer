Fix review: blocked 6ef32c22f3d3cc8e80207cd85900879ab1816d05 mutation-vacuous: coordinator.py:6311 and coordinator.py:11334 reverted to the margins-only keyword survive every test

bus-nonce: 531c711f6ccb4e9c2d94af95e3e0cb55

Round 1 (first review of this PR; review scope full).

## Block

- **mutation-vacuous: the feature's only production entry is unpinned.** Mutant C1 (`ev/C1_coordinator_splat_mutant.diff`) reverts both coordinator builds the body names, `coordinator.py:6311` (scheduled solve) and `coordinator.py:11334` (what-if), from `**rooms.floor_limits(...)` to `min_temp_margins=rooms.floor_limits(...)["min_temp_margins"]`. That keeps the plan and drops `SolveLimits.room_lifts`, so no installed system ever gets a `room_floor` step or a `room_lift` driver. With C1 applied, the full `PYTHONPATH=tests/hastub python3 tests/features.py` run in place (a git worktree at the head) prints `ALL 6030 FEATURE CHECKS PASSED`, rc 0 (`ev/C1_features_tail.txt`).
  - `tests/edge.py` cannot kill it: its `room lift named` check builds the `SolveLimits` keywords itself through `rooms.floor_limits` and never calls the coordinator.
  - No test under `tests/` sets `room_lift_enabled` (`grep -rln room_lift_enabled tests/` returns only `tests/golden/config_flow.json`). No golden fixture has a room list, so every coordinator-driven solve in the suite gets `room_lifts` None either way.
  - The body's `coordinator.py:6285` and `:11296` kills are STMT_DEL of the `SolveRecord` and what-if returns. Those are different statements; the splat lines themselves are not drawn by `mutant_run.py`.
  - The design note's evidence item "The what-if's room-lifts equal the baseline's after the readings change (carry r4)" is tested only on `rooms.floor_limits` directly (`tests/features.py` 3B block), not through the what-if build at `coordinator.py:11334`.
  - Repair: a check that drives the coordinator's scheduled build with the lift enabled and a short room, and asserts `room_lifts` reaches `SolveLimits` (or `room_floor`/`room_lift` on the result). Add the same for the what-if build, and show both fail under C1.

## Findings

- None beyond the block. Each other survivor of this review is equivalent (see Evidence). Carry: dismissed: no finding outside the block

## Evidence

- Head reviewed: `6ef32c22f3d3cc8e80207cd85900879ab1816d05` (`ev/HEAD.txt`). It is the PR body's head (body `## Head`). Merge base `35402f78175090abecbac8859c50d4d816ccd95b`.
- Role contracts current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Merges with main: `git merge-tree --write-tree origin/main 6ef32c22f3` exits 0 (tree `aa5f74c9a3`).
- Mutants in the 3B block (`features_block.py` with the emitted prelude `ev/block_prelude.py`; unmutated `ALL 8 FEATURES BLOCK PASSED`). Driver and output: `ev/mutants.py`, `ev/run.sh`, `ev/block.txt`, `ev/edge.txt`. Results for my own 18 targeted mutants:
  - 13 killed by the block. These include `_mark_room_floor`'s next-temperature index, its 0.15 K tolerance and its reason guard; the unlifted build's mold argument; `_raised_floor`'s ceiling constant and early return; `DRIVER_CODES` order; the comfort push against the lifted floor; the room-lift push scale; and `floor_limits`' lift half and `lift.any()` guard.
  - A14, A15 and A16 (the `_Horizon` field, `limits.room_lifts` not passed to `_build_comfort_bounds`, and `_mark_room_floor` handed None) survive the block. `tests/edge.py` kills each of them (unmutated `ALL EDGE CASES PASS`).
  - Equivalent, not blocking: A4 at `optimizer.py:4937` (`np.maximum(..., 0.0)` dropped). The held and unlifted floors run the same monotone add/max/min arithmetic on margins that differ only by a non-negative lift, so the difference is never negative.
  - Equivalent, not blocking: A17 at `optimizer.py:737` (the mold fill `-inf` becomes `0.0`). It only matters beyond a short mold series, where the floor is about 19 °C and greater than 0, and `mold_guard` clips `mold - floor` at 0.
- The body's M1 to M7 are reproduced in kind by my mutants A2, A1/A3, A5/A6, A13, A18 and A10.
- Null control: `dev/audit/harnesses/room_lift_solve.py` prints byte-identical output at the merge base (git archive of `35402f7817`) and at the head (`ev/room_lift_solve_base.txt`, `ev/room_lift_solve_head.txt`). The lift row is `edde566a7f8d` against `none`'s `eda725c0be09`.
- Enumeration (design note's sibling-site rules re-run at the head, `ev/enumeration.txt`):
  - `min_temp_margins=` returns the two coordinator builds, both in the diff.
  - Every `comfort_floor`/`REASON_COMFORT_FLOOR` registry site has its `room_floor` twin. `_MANUAL_KEEP_REASONS` excludes it by design (the `manual_pin` gate gives no lift; pinned by the P2 block's manual-pin gate check). `ledger.py:643` treats it as a draw (not in `IDLE_REASONS`).
  - `why_now_at` skips absent codes (`slot_drivers.py:180`).
- `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched. `tests/golden` is unchanged against the merge base.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`, with `class_excess_loc 17306 <= 17306` (`ev/structure.txt`). The 16-line drop is earned: the T5 arithmetic moved out of `HeatPumpOptimizer` into `_raised_floor`, and the attribution calls it a second time.
- `tools/audit/archscore/score.py --diff 35402f7817` (merge base) at the head: `Architecture score: dS +0.0000 NULL` (`ev/archscore_mb.txt`).
- `archscore.py --diff e698fc8ac3` (the body's figure) at the merged head reads `dS -0.0006 WORSENS (inadmissible: coord_footprint 2528->2529)` (`ev/archscore.txt`). That figure includes main's 50 commits since `e698fc8ac3`. The body's NULL holds against the actual merge base, and CI `arch-score` is success.
- CI: `tests / mutation` is red, as the body predicts under `## Red checks` (unpinned added sites for mutation-autofix). `gate` concluded failure while lanes were still running. The last classify line was `22:44:57 rc=3 WAIT 6ef32c22f3d3cc8e80207cd85900879ab1816d05 pending: gate red: none` (`ev/classify.log`). A block on tests does not wait on CI.
