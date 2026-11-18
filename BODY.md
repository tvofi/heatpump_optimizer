R11-OUTSIDE-HONEST-METERED-FLOOR part 2 (outside pull request 3529 by Bankaifan; part 1 is #3670): roster carry 2 built at the scope the orchestrator's dispatch names (a store-wide check that every store declaration's cost is what the real loader measures, in both directions, plus `draw/engaged`'s declaration); carry 3 measured at the merge base and routed to the group owning its seam, not built (below). Carry: dismissed: this part's scope statement; each item it names carries its own marker below

- **The check, over-broad half.** `tests/finite_boundary.py` Arm 6's `_a6_whole_cost`: for a swept field, each bad value (the arm's own out-of-domain probes, then `None`, `"x"` and `[1]` where the domain refuses them) is driven through the real loader and saver, and the leaves of the store other than the cell that change are counted. A `whole=` declaration under which no bad value, on any sampled cell, changes another leaf is refused (`every whole= declaration is used`). Design choice: `whole` is a licence that at least one bad value must use, not every one (a loader may clamp one bad value and drop the grid on another, as `internal_gains_profile/#` does). Unchanged in this round, and so is its control.
- **The check, under-declared half (this round, the review's block).** The same cost probe now drives every non-key field, not only `whole=` ones. A cell-only declaration (no `whole`) under which some bad value changes another leaf is refused (`no cell-only declaration costs another leaf beyond its recorded entry`), unless `_A6_CELL_SPENT` records that field at that cost or more. That table is the per-field disposition: the cell-only declarations that already cost other leaves at head 2469c526 (rule below), each with its measured cost. The check also refuses an entry whose field no longer costs any other leaf, or is no longer swept (stale). The table's key is the store and field label, widened by the cost. `draw/engaged` is not in it, so a loader that makes its latch cost other leaves is refused at any cost. A listed field whose cost grows past its entry is refused too. Its own control: `draw/config/#` with its `whole` stripped through `store.stored_fields` is refused (`the cell sweep refuses the configuration that keys the draw record when it is planted cell-only`).
- **The repair.** `store.py`: `draw/engaged` drops `whole=_DRAW_KEY` and is `_FLAG`. A comment states its cost: `DrawRange.from_dict` reads the latch as `data.get("engaged") is True`, so an unreadable latch reads disengaged and the samples stay. The under-declared half now holds that comment (M5b below). No loader changed.
- **Alternatives.** (a) Declare `whole=` with a reason on each of the recorded cell-only fields. That is a production change across `store.py`'s declarations for ten stores, each needing its loader's reason established, which is outside this group's scope (owner `draw_range.py`/`store.py`'s draw record). It is carried, and the table is the ratchet that carries it. (b) Restrict the cell half to the draw record. That leaves the class open in every other store, which the review's block names.
- **Carry 3, raised.** The brief's measurement is the `tail` arm. That arm exists only in `dev/audit/harnesses/r11_honest_dhw_runs.py` on R11-OUTSIDE-HONEST-DHW-RUNS's unmerged branch (`fix/r11-outside-honest-dhw-runs` at `c5111367a979`), not in `r11_honest_starts_runs.py` on main. It needs that group's commit stage (`dhw_planner.commit_charges`), which main does not have. The planner's run power is on main: `DhwPlanner` sets `p_dhw_run = max(0.1, min(p_max * 0.8, p_max))`, so on the fixed-speed install (floor = maximum = 5.5 kW) it plans 4.4 kW and the optimizer's projection raises it when it ships. The repair changes how `dhw_planner.py` sizes a charge's level. The design note `design/R11-OUTSIDE-HONEST-STARTS-RUNS` (a63a2ca6) gives that to group B (R11-OUTSIDE-HONEST-DHW-RUNS, owner `dhw_planner.py`), not to group C. Building it here would depart from the note. Carry: R11-OUTSIDE-HONEST-DHW-RUNS

## Head

`e449f2b4781c238b45711c6bdf34e49f13db3774`, two commits on review head `2469c52668c90af0c143b6905c9ee6e25e140add` (merge base `99a4010e479f04af984c30a4b5cfc2f98d3736ad`). The delta since the review head is `tests/finite_boundary.py` only. Measured 2026-11-18T05:45Z, UTC, at origin/main `7c2f4c30cab5610cf8f5b040c326836ab544d27d`. `git merge-tree --write-tree origin/main HEAD` exits 0, so main is not merged.

prepr: passed rc=0 at e449f2b4781c238b45711c6bdf34e49f13db3774

## Block answered

- Block (class-open, `draw/engaged` cell-only cost unguarded): Arm 6's cost probe now covers every declared non-key field. A cell-only declaration that some bad value makes cost another leaf is refused, unless the per-field disposition `_A6_CELL_SPENT` records it. The reviewer's M5b now fails first: rc 1, `FAIL no cell-only declaration costs another leaf beyond its recorded entry ... refused=['accuracy:accuracy/draw/engaged costs 16 other leaves, declared cell-only (recorded 0)']`. At review head 2469c526 the same M5b passed (`ALL 116 FINITE BOUNDARY CHECKS PASSED`, the review's `ev/m5b_finite_boundary.txt`). The over-broad half and its control are byte-unchanged.
- Note (figure `draw/config/#`): 17, from the in-tree rule. Arm 6 now prints each `whole=` field's measured cost (`COST <label> <n> other leaves (whole)`), and `COST accuracy:accuracy/draw/config/# 17` is that line at the head.
- Note (figure `duty_switch`): 5 or 6, from the same in-tree `COST` lines (below). The `/tmp` probe figures are dropped.

## Mutation proof

Command for each: `PYTHONPATH=tests/hastub python3 tests/finite_boundary.py`. Each mutant was applied in place and the tree restored with `git checkout -- custom_components tests`; `git status --short` was clean after the last run.

- **M5b** (review's `ev/m5b.diff`, `DrawRange.from_dict` returns before the samples on a non-bool latch): rc 1, `1 of 118 FINITE BOUNDARY CHECKS FAILED`, the cell check (above).
- **M1** (review's `ev/m1.diff`, the cell itself counted): rc 1, two failures: `FAIL the whole sweep refuses a whole planted ... [overdraws=1 config=18]`, and the cell check (`draw/floor_kw costs 1`).
- **M2** (review's `ev/m2.diff` no longer applies; its line is now `if not is_key and store != "snapshots":`): equivalent `if False and not is_key ...`, rc 1, four failures (`whole=0`, `overdraws=None config=None`, `cell=0` with every entry stale, cell control `refused=[]`).
- **M3** (review's `ev/m3.diff` no longer applies; its line is now `side[label] = max(...)`): equivalent, whole cost dropped to 1 (`side[label] = 1 if domain.whole else max(...)`). rc 1, `FAIL the whole sweep refuses a whole planted ... [overdraws=1 config=1]`.
- **L1**, the `draw/idle/#` entry deleted from `_A6_CELL_SPENT`: rc 1, the cell check (`draw/idle/# costs 1 ... (recorded 0)`).
- **L2**, a stale entry `draw/engaged: 1` planted: rc 1, the cell check (`draw/engaged recorded at 1, and no bad value costs another leaf (stale)`).
- **L3**, the comparison off (`if False and cost > known`): rc 1, `FAIL the cell sweep refuses the configuration ... [refused=[]]`.
- **L4**, the cell cost never recorded (`... if domain.whole else 0`): rc 1, two failures (every entry stale, cell control `refused=[]`).
- **Base `store.py`** (`draw/engaged` declared `whole=_DRAW_KEY`): rc 1, `FAIL every whole= declaration is used ... [whole=34 unused=['accuracy:accuracy/draw/engaged']]`.
- 9 of 9 killed. The head: `ALL 118 FINITE BOUNDARY CHECKS PASSED`, rc 0.

## Null control

- The cell half's control is green at the head. With `draw/config/#` planted cell-only, it is refused, exactly once. Without the plant, `RESULT domain_cell_refused=0 count`.
- The over-broad half's control is unchanged and green: `overdraws` planted `whole` measures 0, and `config/#` measures 17.
- Arm 6's existing null is unchanged: the healthy rich seed round-trips unchanged through every loader and saver.
- Carry 3's probe: the duty-cycle install (unclamped, floor 1.5 kW) plans and ships the same 9 sub-floor hot-water steps, where the two clamped installs ship 0 of what they plan.

## Figures

<!-- figure-block: scope-line mb=99a4010e479f04af984c30a4b5cfc2f98d3736ad head=e449f2b4781c238b45711c6bdf34e49f13db3774 -->
~~~text
MODE: SCOPED -- 22 script(s) run, 11 scoped out.
~~~
<!-- /figure-block -->

- Class seams, rule: every non-key field of every store `store.stored_fields` enumerates over the rich seed, the snapshot ring excepted, driven by Arm 6 itself. The `RESULT domain_whole_*`, `RESULT domain_cell_*` and `COST` lines come from `PYTHONPATH=tests/hastub python3 tests/finite_boundary.py`. At the head: 33 `whole=` fields, 0 unused; 232 cell-only fields, of which 86 cost another leaf, every one recorded in `_A6_CELL_SPENT` at its cost (disposition: carried below), and 0 refused. `draw/engaged` is cell-only and costs 0.
- In-tree per-field `whole` costs at the head (`COST` lines): `draw/config/#` 17; `draw/samples/#/#` 9; `draw/ceiling/#/#` 1; `dhw_profile` profiles 23; `duty_switch` fields 5 or 6; `price_model` `days`/`quarter_days` 1, `shapes`/`residual_var` 24, `quarter_factors` 96; `internal_gains_profile/#` 24.
- `PYTHONPATH=tests/hastub python3 tests/finite_boundary.py` at the head: `ALL 118 FINITE BOUNDARY CHECKS PASSED`, rc 0. At review head 2469c526 it gives 116, and at the merge base 114; the two added in this round are the cell check and its control.
- Scope: `python3 tests/closure.py select --diff 99a4010e...`: `MODE: SCOPED -- 22 script(s) run, 11 scoped out.` The gate was not re-run locally for this test-only delta: `finite_boundary.py` is the script it changes, and was run above. CI is the authority.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff 99a4010e HEAD`: `Architecture score: dS +0.0000 NULL`.
- Carry 3 was measured at origin/main 7ae657e0 and has no head figure, because nothing for it is built. The probe is the `tail` arm's install fixture (`_install_solve` of `r11_honest_dhw_runs.py` at `c5111367a979`: 96 quarter-hour steps, hot water on, cycling cost 0.3, p_max 5.5 kW), with `DhwPlanner._build_dhw_requirements` spied for the planned schedule. It counts hot-water steps between `MIN_RUNNING_DRAW_KW` and the floor, as planned and as shipped: fixed-speed (clamped, floor 5.5) 4 and 0, at planned run levels 3.3, 4.179 and 4.4 kW; modulating clamped (floor 1.5) 9 and 0; duty-cycle (unclamped, floor 1.5) 9 and 9.

## Red checks

none

## Forward-carry

- The 86 cell-only declarations recorded in `_A6_CELL_SPENT` cost other leaves through their real loaders at head 2469c526: each owes a `whole=` reason or a loader that keeps its neighbours. Control: the cell check refuses any such field missing from the table, and refuses a stale entry. Re-measure with `PYTHONPATH=tests/hastub python3 tests/finite_boundary.py` (`RESULT domain_cell_spent`). This group is carries-open, so the carry goes to the intake group. Carry: R11-INTAKE-R10-RESIDUE
- Carry 3 (body item 7502c4d5) is raised, not built: the planner's run power on a clamped install sits under the floor at main, and its repair is in `dhw_planner.py`, group B's seam by the design note. Control: the duty-cycle install's 9 planned and 9 shipped against the clamped installs' 0 shipped. Re-measure at the building group's merge base with the `tail` arm once it is on main. Carry: R11-OUTSIDE-HONEST-DHW-RUNS

## Friction

- brief: contradiction: the brief's step ref `handoff-wip/r11-outside-honest-metered-floor-p2` (fast-forward only) still holds the previous round's `BLOCKED.md` commit (f51d20e6), which is not an ancestor of this round's head. A fast-forward step push was rejected, and the seat's permission layer refused deleting the stale ref, so no step was pushed there in this round. Carry: dismissed: a stale ref the orchestrator clears; this round's code is on the handoff ref
- brief: stale: carry 3 names the `tail` arm of `dev/audit/harnesses/r11_honest_starts_runs.py`, which has no `tail` arm at main 7ae657e0; the arm is in `r11_honest_dhw_runs.py` on R11-OUTSIDE-HONEST-DHW-RUNS's unmerged branch and needs that group's commit stage. Carry: dismissed: the brief is this part's dispatch, answered in this body; carry 3 itself is routed above
