# BLOCKED: r10-advisor-steady-start (fixer), at 273079db5 on origin/main 8f97247fc

Question: the approved estimator (design/R10-ADVISOR-STEADY-START d2d663c32: both plans from held starts, spend plus `deferred_energy_cost`) reads a degree cooler as a COST on the suite's default-configuration coordinator fixture at 6 of 12 start hours, where the figure the panel shows today is wrong-signed at 2 of 12. Does this go back to the designer (the brief's sign item fails off the three harness instants), or does the owner accept the panel's degree figure as designed with the measured rate disclosed?

## Measured (head 273079db5; the estimator is implemented as designed)

- Finder's harness, the brief's rows: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_advisor_residue.py whatif` prints `RESULT whatif steady rows 24 steady_moves_by_start 0 degree figures against the held sign 0/36 cap figures reading a saving (< -1) 0/36`. The brief's sign and start items hold on every row it names.
- Same harness, new arm in this branch, every second start hour instead of three: `... r10_advisor_residue.py steadysign` prints `RESULT steadysign rows 48 steady_wrong_sign 1 held_wrong_sign 0` (varying 05:00 target_plus_1 steady -0.1, target_minus_1 -0.6: the figure collapses to zero there). Null control: the held figure's sign turns on 0 of 48.
- Coordinator fixture (`_solve_coord` in tests/features.py: default entry, target 21, min 19, night 19.5, comfort weight 5, outdoor -5 flat), `async_simulate(spec, steady=True)` at hours 01..23 step 2, one frozen instant each: steady degree figures against the held sign 6/24 (all six are target_minus_1 reading +4.0 to +42.1 at 05, 07, 09, 11, 19, 21); settled 11/24; the plan's own figure (the panel's at the merge base) 2/24. Cap tile reading a saving (< -1): steady 0/12, settled 0/12, plan 11/12. This run was a scratch probe driving the fixture; the in-tree witness is the red check below.
- Red check at this head: tests/features.py, "#2257: under the steady figure a degree warmer costs and a degree cooler saves at every start, with the held figure's sign", at the frozen 07:07 instant: target_minus_1 steady +23.1 at all three starts (held -42.05).

## Cause, as far as measured

At 07:07 on that fixture the two held solves read: live (target 21) spend 14.49, deferred +3.31, 23.0 kWh; a degree cooler (target 20) spend 18.93, deferred -0.37, 26.8 kWh. Both plans ride the comfort floor (min 19) whatever the schedule, so they differ mainly by the stored heat each held start begins with (a kelvin of house), which the live plan drains inside the horizon; the end settlement buys it back only up to its caps. Not established: which of the caps, the floor or the solver basin carries the residue. The held start itself is right: spread by start is 0 on every row, and the start gap reads 0 within 1e-9.

## What is on this ref

Done and passing in a scratch run of the new block (21 of 22 checks): SolveInputs.held_start and the shared held reference; monthly_steady_cost_delta in price_tiles.monthly_deltas; whatif.py (side-table state, limiter gate, override routine, steady pair with the one-slot live memo keyed on plan identity, solve instant, measured start and away band); async_simulate(steady=) with the _whatif_solve builder; the panel, cap tile and fuse advisor reading the steady key with no fallback; card strings en/sv/de; docs; eight structure budgets recorded down.

Owed before any handoff, none started unless listed: the full tests/features.py run (one known red besides the sign check: "the advisor publishes a verdict for the next-smaller fuse", whose stub still answers with the settled key); the two-tank held-start check (the design's fixture, `_grad_parity(True, wood=True, valve="manual")`, is not two-tank: `two_tank_modelled` is a property of `topology_layout`, the config key of that name sets nothing; a real two-tank fixture is still to be built); tests/card.mjs checks for the steady money line and the fuse row; classifying whatif.py in tests/closure.py and docs/architecture.md; the reviewer's mutants; solve count and wall time per what-if; GOLDEN_MODE=drift; prepr.sh; the body.

Departures from the note, for the reviewer: the state is a WeakKeyDictionary side table (`boost.py`'s discipline), not an attribute, so coordinator_attrs fell by two; the held reference is a module-level function beside its two parts, not a method (a method cost class_excess_loc 13 lines with no payment available).

Carry: R10-ADVISOR-STEADY-START (the question above is this group's own, pending the orchestrator's or owner's ruling)
