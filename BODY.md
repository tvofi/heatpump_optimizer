R10-SAV-VALUATION-RESIDUE. Under a part-load derate `_terminal_cost` and `_deferred_energy_cost` bought stored heat back at a COP with no draw. Both now buy it back through one law, `optimizer._refill_law`: `thermal_model.refill_power_kwh`, the tree's own inverse (`power_for_heat_per_cop_kw`) at the heat spread evenly over the cheapest quarter of the horizon, the hours the 25th-percentile refill price (`_refill_price`) is drawn from. The terminal and the deferred figure change together, as `_terminal_cost`'s docstring binds them. With no derate `_refill_law` is `None` and every figure is the linear one, bit for bit.

Decision (Carry 2's "price refill at a stated rate's derated heat, or segment the hot-water LP"): the stated rate. The LP segmentation was built, measured and refused: see `## Forward-carry`. The unattributed savings residual (Carry 1) is attributed: it is the booked reference's, not stored heat's and not COP's.

Alternatives and why each lost: (a) the rate at max power: one figure for every deficit, over-charging every refill a floor run would buy (the carried `at-max` bound). (b) the plan's own energy-weighted draw `P_r` (`r10_partload_residue.py refill`): unknown when `_terminal_cost` is built, before the plan exists, so the objective and the settlement could not share it. (c) segmenting the hot-water LP: measured worse (`## Figures`). The rate taken is a property of the deficit and the window, known to both twins at build time.

The brief's three carries: Carry 1 (the residual): attributed in `## Figures`, its fix carried in `## Forward-carry`. Carry 2 (part-load refill pricing): built for `_terminal_cost` and `_deferred_energy_cost` together; the hot-water LP's secant measured, its segmentation refused and carried. Carry 3 (Carry 2's segmenting and refill-rate decision and its zero-derate control): the decision is the paragraph above, the control `## Null control` and the companion's `d = 0` rows.

Carries 4, 5 and 6 on the roster entry are this body's own `Carry: R10-SAV-VALUATION-RESIDUE` items, landed by the carry fold, not further work: Carry 4 is the merge-base residual in `## Figures` (-3.90 % flat, -8.02 % varying), Carry 5 the residual's attribution in `## Forward-carry`, Carry 6 the hot-water LP's secant in `## Forward-carry`.

## Head

0edaebae75064f52642718f9c6595f2c764ef529, `origin/main` dbd1ab5b0712ebc51e29ef8c001a2c0ef68af3cd merged in (a `tests/features.py` conflict: both sides appended at the end; both kept). Base figures below are at 32aea942, the branch's cut; head figures re-taken at 0edaebae after the merge.

## Mutation proof

Each production line neutralised in turn, the new `tests/features.py` check run (its block standalone), restored; each run printed FAIL `R10-SAV-VALUATION-RESIDUE: under a part-load derate the terminal cost and the deferred settlement ...`. The four mutants: `_deferred_energy_cost`'s conversion made the identity (at the first commit, `electrical = refill(electrical)` to `pass`); `_terminal_cost` passing `None` for the law; `_refill_law`'s derate guard made always-`None`; `refill_power_kwh` returning its input.

## Null control

At `d = 0` the companion harness reads every terminal, deferred and LP gap 0 over 32 solves at both ends (`null rows not zero 0`), and the check asserts `_refill_law` is `None` with no derate. The base tree reads the defect: the same check FAILs at 32aea942 (the derated terminal equals the linear one).

Flat-price null (mandatory): the flat day's rows are printed beside the spread day's; the derated refill's move of the savings figure is the `predicted_savings` column of `r10_sav_valuation_residue.py` at both ends, apart from the stored-heat term (the residual attribution runs at `d = 0`, so it reads the same at both ends: no part-load term is in it).

## Figures

- Carried figures re-measured at the merge base, `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_partload_pricing.py`: flat `d=0.112` lp_err max 0.267290 (dhw cost max 7.0145), terminal-at-max max 4.368455, deferred-at-max max 2.140129; `null rows not zero 0`. The harness applies the linear rule's bound to the production figure, so at the head its terminal and deferred columns still print a bound: it measures what this fix replaces, and the companion below reads the defect.
- Companion, `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_sav_valuation_residue.py` (production figure against `power_for_heat_per_cop_kw` at the refill hours applied to the zero-derate figure): base 32aea942: spread `d=0.112` terminal gap max 3.150490, deferred gap max 0.440868; flat `d=0.112` terminal gap max 2.835283, deferred gap max 0.187447. Head 5c368ab, and again at 0edaebae: all four 0.000000. LP gap (left): spread 0.202595, flat 0.335995 at both ends. `d=0` rows 0 at both ends; `null rows not zero 0`, `failures 0`. 7b60fb7 and 21f178bc change only `tests/`.
- Residual at the merge base, `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py valve-flat` and `valve-vary`: -3.90 % (flat), -8.02 % (varying); these arms run at `d = 0`, unchanged by this diff. Attributed below; the finding is the first `## Forward-carry` item. Carry: R10-SAV-VALUATION-RESIDUE
- Attribution (carried in `## Forward-carry`), `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_residual_attribution.py flat` and `winter_typical`, kWh_th over the arm's plant steps (`plant steps seen 192 of 192`): flat, the booked reference stepped from its held state draws -34.85 from its stores and loses +12.52 beyond the steady comfort term, together -22.33 kWh_th, the residual; varying -34.85 and +11.89. The store term is price-independent; a reference at equilibrium reads 0 on it. Ruled out first by a probe on the same loop: the buffer tank's standby loss, plan less held reference, +0.07 kWh_e against the flat arm's -5.21 kWh_e gap.
- LP segmentation, refused: the hot-water LP cut into four equal draw slices of the band, each step's energy priced at its slice's slope, `r10_partload_pricing.py` at that tree: every derated hot-water cell's published hot-water cost rose, flat 7.0145 to 7.8780 and spread 8.0681 to 8.8053 (every draw at the floor, 1.500 kW). The base LP publishes the true inverse of the energy it buys, so its secant is a valuation error, not a delivery one; a convex-exact program cannot cost more in truth, so the chord model misprices, and the segmentation was reverted.
- Structure, `python3 tests/structure.py`: `class_excess_loc` 17537 to 17536 (re-recorded: the law and the shared refill price at module level).
- Gate: `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` (`tests/closure.py select --diff 32aea942`); `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` at 5c368ab: 26 scripts ok, `tests/features.py` red on R9-F2.5's capture builder (it wrapped `_terminal_row_cost` at four arguments); the builder forwards the law at 7b60fb7, and `PYTHONPATH=tests/hastub python3 tests/features.py` there prints `ALL 5188 FEATURE CHECKS PASSED`; at 0edaebae `ALL 5223 FEATURE CHECKS PASSED`, `tests/structure.py` exit 0, and the scope at the merge reads `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`

## Red checks

`tests / mutation`, predicted by `prepr.sh` step 6d (13 added unpinned sites; the stale pin of `_deferred_energy_cost`'s moved return dropped at 21f178bc, its successor among the 13): owed to `mutation-autofix`, see `## Unpinned sites`. Root-cause answer: the cheaper detector is step 6d itself, which predicted it locally at no added standing cost; none further exists to build.

## Unpinned sites

Each is on `custom_components/`, the lane `mutation-autofix` mutates; a local `tests/mutation_table.py --pin-killed` at 21f178bc ran two hours without finishing its driver baselines, so every disposition below is `unmeasured` here and owed to that lane's `ci: pin killed mutants`. The new check kills the guard, return and constant sites by the mutation proof's four arms; the CLAMP_DROP sites re-spell the linear arm's `max(cop, 1e-6)`, a floor no install's COP reaches, expected survivors as the linear arm's own clamp sites are.

- custom_components/heatpump_optimizer/optimizer.py:137 CONST: pinned by `mutation-autofix` (unmeasured)
- custom_components/heatpump_optimizer/optimizer.py:2629 RETURN_DEL: pinned by `mutation-autofix` (unmeasured)
- custom_components/heatpump_optimizer/optimizer.py:2644 GUARD_OFF: pinned by `mutation-autofix` (unmeasured)
- custom_components/heatpump_optimizer/optimizer.py:2647 RETURN_DEL: pinned by `mutation-autofix` (unmeasured)
- custom_components/heatpump_optimizer/optimizer.py:2656 RETURN_DEL: pinned by `mutation-autofix` (unmeasured)
- custom_components/heatpump_optimizer/optimizer.py:2712 GUARD_OFF: pinned by `mutation-autofix` (unmeasured)
- custom_components/heatpump_optimizer/optimizer.py:2718 CLAMP_DROP: expected equivalent survivor; triage owed if `tests / mutation` reports it
- custom_components/heatpump_optimizer/optimizer.py:2719 CLAMP_DROP: expected equivalent survivor; triage owed if `tests / mutation` reports it
- custom_components/heatpump_optimizer/optimizer.py:2722 GUARD_OFF: pinned by `mutation-autofix` (unmeasured)
- custom_components/heatpump_optimizer/optimizer.py:2723 CLAMP_DROP: expected equivalent survivor; triage owed if `tests / mutation` reports it
- custom_components/heatpump_optimizer/optimizer.py:5640 RETURN_DEL: pinned by `mutation-autofix` (unmeasured)
- custom_components/heatpump_optimizer/thermal_model.py:2603 CMP_BOUND: pinned by `mutation-autofix` (unmeasured)
- custom_components/heatpump_optimizer/thermal_model.py:2603 GUARD_OFF: pinned by `mutation-autofix` (unmeasured)

## Forward-carry

- The savings residual's attribution: the booked reference's held state is not held by the power booked for it (-34.85 kWh_th over the arm, price-independent) and loses +12.52 / +11.89 kWh_th beyond the steady comfort term. A fix there changes the reference (`_thermostat_held_state`, `_compute_baseline_power`'s first step), not stored-heat valuation; legitimate only if the store term reads 0 on a reference at equilibrium and the flat arm's residual moves by the term's share. Re-measure with `r10_sav_residual_attribution.py` at the merge base. Pending the orchestrator's ruling on its owner. Carry: R10-SAV-VALUATION-RESIDUE
- The hot-water LP's secant (`_plan_dhw_min_cost`, flat 0.335995 / spread 0.202595 per day against the tree's inverse) is left: equal-slice segmentation measured worse in truth (`## Figures`). A segmented LP is legitimate only if, on `r10_partload_pricing.py`'s cells, the published plan's true hot-water cost does not rise at any derated cell and the `d = 0` rows stay bitwise. Pending the orchestrator's ruling on its owner. Carry: R10-SAV-VALUATION-RESIDUE

## Friction

none
