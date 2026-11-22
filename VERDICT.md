Fix review: blocked 9516fcc55ccd6c40d58ca1d6b3d152d0b17aed4a architecture-unsound: raised_floor and mark_room_floor moved into rooms.py against the approved note's owning seam, unraised in the body

bus-nonce: 680c002128484fbc5fcc0a1d185290ec

Round 2 (later round over the reviewed head `6ef32c22f3d3cc8e80207cd85900879ab1816d05`; review scope delta, per the packet's `## Review scope` line). Run as a local seat in place of the cloud reviewer.

## Block

- **architecture-unsound (fix-review.md step 15; fixer.md step 17, "one owner per concern").** The delta's production commit `c03b640cd6` moves `_raised_floor` and `_mark_room_floor` out of `optimizer.py` into `rooms.py` as `raised_floor` and `mark_room_floor`. `optimizer.py` now imports both from `.rooms` (`ev/delta_c03b640cd6.diff`). The commit gives the reason: `optimizer.py` was 43 lines over `module_excess_loc`, and `rooms.py` is "a module under the 2000-line limit".
  - The approved design note (`design/R11-OUTSIDE-ROOMS-3B` at `09049ddb`, `ev/design_note_09049ddb.md`) assigns the seam the other way. Line 13 says "**`optimizer.py` owns the attribution.** It records on `_Horizon` which part of the floor the solve held is the rooms' part, and it classifies steps from that". Line 15 says "`rooms.py` keeps the lift". Line 85 says the mold floor and ceiling clip are what "only `_build_comfort_bounds` sees".
  - `raised_floor` is not a room concept. It is the T5 (#16 #54) comfort-floor arithmetic: confidence margins, the mold-guard maximum and the ceiling clip. Its own docstring calls it "the single site the bounds are built, so every consumer (objectives, safety releases, pin repair) sees the same effective floor". Every solve runs it, including one with no room list. After the move, the optimizer's core bound build depends on the room-list module, whose docstring says it "owns that list's reading record, its summary ... and the payload block".
  - `mark_room_floor` is the step classification that the note gives to `optimizer.py`.
  - The PR body raises one departure from the note (interface 4, the post-pass). It does not raise this one. Its `## Red checks` entry describes the move only as the repair for `tests / fast` and says the two helpers "belong to the room lift". That is true of the second, attribution-only call of `raised_floor`. It is not true of the function.
  - Step 14 plant: moving any about 50 lines of `optimizer.py` into a module under its limit moves `module_excess_loc` the same way, whether or not the code is better placed. The 21779 -> 21770 re-record is earned here only by this move, which is the shape step 14 refuses unless the move improves the code.
  - Repair (the fixer's choice): either keep both helpers on the optimizer side of the seam and pay the module budget by a move the note supports (code `optimizer.py` holds for a concept another module owns), or put them in a small new module owned by the bound build (fixer.md step 17: "the module owning the concept, or a small new one"). Alternatively, raise the departure in the body for design review. The re-record then follows whichever move lands.

## Findings

- Residual: the move dropped a clip that is unreachable today. Before the move, `_raised_floor` padded and clipped its `margins` at zero, so the unlifted build read `clip(margins - room_lifts, 0)`. At the head, `raised_floor` takes margins already padded, and the unlifted call passes `margins - _padded_nonneg(room_lifts, n_steps)` unclipped.
  - On inputs shaped as `rooms.floor_limits` returns them (`margins = _margins(base) + lift`, `room_lifts = lift`), the two are identical: 20000 random cases, 0 differ (`ev/equiv.py`, `ev/equiv.txt`). Both production callers, `coordinator.py:6293` and `:11311`, splat `floor_limits`. My equivalence mutant E1, which restores the clip, survives both detectors for that reason.
  - Null control: a `room_lifts` with `min_temp_margins` None, or a lift longer than the margins, makes the head attribute the whole lift where the old code attributed 0 (`old [0,0,0,0] new [1,1,1,1]`). No caller produces either input. Carry: dismissed: unreachable from every production caller (both splat rooms.floor_limits); the repair above re-cuts this code, and the fixer may restore the clip there

## Evidence

- Head reviewed: `9516fcc55ccd6c40d58ca1d6b3d152d0b17aed4a` (`ev/HEAD.txt`). The body's `## Head` names `8800ed7c6f` as the head. `9516fcc55c` is the bot's `ci: pin killed mutants` on top of it, and it changes only `tests/mutation_ledger/killed_by/`.
- Role contracts current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Delta: `git log --first-parent 6ef32c22f3..9516fcc55c` has one authored production commit (`c03b640cd6`), one test commit (`ffb12a9319`, the two coordinator-build checks), a delivery row (`5ac06973d1`), three bot pin commits and main merges.
  - Main merges: `--cc` shows a resolution only in `tests/structure_budgets.json` (`9d3d6d129b`, `84ae6ce8aa`, `0c0b146b5a`), each taking the lower row.
  - Per file, the PR's own diff at the reviewed head and at this head differs only in `optimizer.py`, `rooms.py`, `tests/features.py` and `tests/structure_budgets.json`.
- Prior finding resolved. The round-1 block was mutant C1, the two coordinator splats reverted to `["min_temp_margins"]`. Under C1, C1a (scheduled build alone) and C1b (what-if alone), the P2 block now fails (`ev/mutants_out.txt`).
  - C1 and C1a fail "the scheduled build hands the solve its room lifts ...". C1b fails "the what-if build hands its solve the baseline's room lifts ...". Unmutated: `ALL 26 FEATURES BLOCK PASSED`.
  - Detector: `features_block.py` with an emitted prelude. The P2 emit exits 1 on the missing `asyncio` import the body names. I used the same local overlay: `import asyncio as _asyncio` prepended (`ev/mut.sh`).
- Mutants on the moved code (`ev/mutants.py`; 3B block unmutated `ALL 8 FEATURES BLOCK PASSED`, `#224 stage 2` comfort-envelope block `ALL 8 FEATURES BLOCK PASSED`):
  - Killed by the 3B block: `raised_floor`'s margin add, ceiling clip and mold maximum; `mark_room_floor`'s 0.15 K tolerance and its `- room_lifts[i]`; the unlifted build without the lift.
  - Killed by the `#224` block: the call site's new `_padded_nonneg` replaced by an unclipped array.
  - E1 (the old clip restored) survives, as explained under Findings.
- `python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`, `ok module_excess_loc 21770 <= 21770`, `ok class_excess_loc 17301 <= 17301` (`ev/structure.txt`).
- Merges with main: `git merge-tree --write-tree origin/main 9516fcc55c` exits 0 at origin/main `9276ddf6b1`. The ledger driver printed `LEDGER-MERGE: resolved tests/structure_budgets.json` (`module_excess_loc: 21779 + both deltas = 21766`; `ev/merge_tree.txt`).
- Finder's harness: none named (owner report #3616; the packet reads `none named`). The delta's production change is a code move. Its behaviour is pinned by the differential above and by the mutants. `dev/audit/harnesses/room_lift_solve.py` was not re-run at this head: the round-1 verdict measured it byte-identical across the feature, and this move is equivalent on every reachable input.
- CI at the head: the last classify line is `23:43:43 rc=3 WAIT 9516fcc55ccd6c40d58ca1d6b3d152d0b17aed4a pending: gate red: none` (`ev/classify.log`). In the packet's digest, `tests / mutation` (job 137368604976) is `failure`, with `mutation-pins (1)/(2)` still running. Its log could not be read while run 45073670749 was in progress. It is in the owed-reds set. The body's `## Red checks` answers the same lane at `0edc7fbd8b` (unmeasured and unpinned sites, re-pinned by the bot). A block on code does not wait on CI.
- Instrument friction (local): my `gate_lock.py slot-take --label rev-3838-local` held slot 3. At release it printed `no slot`, and slot 3 was held by `rev-3841-local`. The lease was taken without `--owner-pid`, and the run finished before the slot was lost.
