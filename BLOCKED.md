# R10-DUTY-SWITCH-PLANNER-PRICE: blocked on its predecessor

Question: R10-DUTY-SWITCH-RESTART-LEARNING (pull request 3461, handoff head bf9707ae03) is open and not on `origin/main` (61afd4f2db), so the learner module this design reads does not exist at my base. Do I wait for 3461 to merge and resume from this ref, or build the learner read, the count cap and the coordinator line stacked on bf9707ae03?

The design (439d17c930) and the brief both say "after that group merges"; my contract cuts from `origin/main`. Stacking is a departure, so it is raised here and not made.

## Built on this ref (design sections in brackets)

- `duty_legs.py`, the leaf: the leg rule moved out of `pump_arbiter._share` with `SPLIT_MIN_MINUTES`, the switch weight (scalar and batch), the availability vector, the delivered draw, the headroom, the ban mask. [Owning seam, Shape]
- `optimizer.py`: two config fields beside `cycling_cost`; the switch term in both objective closures; lost time on the bound (duty-cycle) or the delivered draw (clamped); the vector riding beside its plan to the publication; one banned candidate after `_co_optimize`, not on a combi store. [Shape, Invariants]
- `dhw_planner.py`: the placement ban, one keyword, OR'd into `forced_off` only. [The ban's channel]
- `tests/features.py`: the group's section, design tests 1 to 6, 8 and 9 and verdict items r14 to r17.
- At 35b33489b: `PYTHONPATH=tests/hastub python3 tests/features.py` exits 0, `GOLDEN_MODE=drift PYTHONPATH=tests/hastub python3 tests/golden.py` reports no unclaimed drift and no stale fixture, `python3 tests/structure.py` passes with `class_excess_loc` recorded lower. Neither claim file is touched.

## Not built: needs the predecessor

- The learner's read for the planner (both pairs, zeros unless latched) and the count cap of 10 in the direction record's booking. [Config and learner, Bound on the learned count]
- The coordinator's one argument beside `cycling_cost` in `_solve_hubs`.
- Design test 7 (cap, 12 and 13 kept episodes, 28 days, round trip, zeros while unlatched) and the learner-state arm of test 4. Until then the two config fields are zeros on every install and nothing ships changed.

## Owed before a handoff, deliberately left for the resume

Each of these is redone by the merge with the predecessor, which edits the same files (`tests/closures.json`, `tests/deployment_shape.py`, `docs/architecture.md`).

- `tests / closures`: `tools/pr/ci_predict.py` predicts UNDER-SCOPED for every script that now reaches `duty_legs.py` and, through it, `plan_step.py`. Only `tests/arch_score_head.py` is re-recorded here. `tests/deployment_shape.py`'s closure and the file counts its docstring cites are stale by one module, and `tests/entities.py` is red on those until they are re-recorded.
- `## Unpinned sites`: the predictor's `--only mutation` arm lists the sites the diff adds; none is pinned in the ledger yet. Seven stale pins whose lines moved are deleted.
- `tools/audit/archscore/score.py --diff` and `tools/pr/prepr.sh` have not been run.
- The mutation proof was taken with a scratch driver over the section's checks (43 mutants on private copies, an unmutated control first); it is not in the tree. Step 18 wants it under `dev/audit/harnesses/`, classified.

## Findings for the orchestrator

- `DEFAULT_CYCLING_COST` is 0.0 and the design's term is `cycling_cost` times the weight, so on an install that left the cycling cost at its default the price and the banned candidate are both inert; only the lost running time is charged. The acceptance checks run at a cycling cost of 0.3. Whether the contributor's install prices a cycle is not something this tree can answer.
- On the fixed-speed fixture the priced solve keeps every hot water to heating switch: a charged step delivers a part-power step the pump cannot otherwise make, and the score falls. The switch weight there is unchanged by pricing. This is the design's delivered draw doing what it says; it is reported, not altered.
- Design item c2: no planner method was added. The guard calls the planner's own `_dhw_shortfall` with the draw rates the candidate plan returns, which are the uncredited ones on a wood-coil install, for the incumbent and the candidate alike.
- Design test 6's refusal runs on the due-disinfection fixture with the heating placed by hand after the run-up, calling the candidate pass directly: no solved fixture was found whose own plan holds a priced switch there.
- `_cost_terms_batch` went over the ten-parameter line with two more arguments; it now takes one level cost in place of the two closures and has one parameter fewer than on main.
