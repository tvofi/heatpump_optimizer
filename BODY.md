R10-SAV-VALUATION-RESIDUE. Under a part-load derate, `_terminal_cost` and `_deferred_energy_cost` bought stored heat back at a COP with no draw. Both now buy it back through one law, `optimizer._refill_law`. The law is `thermal_model.refill_power_kwh`, the tree's own inverse (`power_for_heat_per_cop_kw`), applied with the heat spread evenly over the cheapest quarter of the horizon. Those are the hours the 25th-percentile refill price (`_refill_price`) is drawn from. The terminal and the deferred figure change together, as `_terminal_cost`'s docstring binds them. With no derate `_refill_law` is `None` and every figure is the linear one, bit for bit.

Decision (Carry 2's "price refill at a stated rate's derated heat, or segment the hot-water LP"): the stated rate. The LP segmentation was built, measured and refused: see `## Forward-carry`. The unattributed savings residual (Carry 1) is now attributed. It belongs to the booked reference, not to stored heat and not to COP.

Alternatives and why each lost:
- (a) The rate at max power: one figure for every deficit. It over-charges every refill a floor run would buy (the carried `at-max` bound).
- (b) The plan's own energy-weighted draw `P_r` (`r10_partload_residue.py refill`): unknown when `_terminal_cost` is built, before the plan exists, so the objective and the settlement could not share it.
- (c) Segmenting the hot-water LP: measured worse (`## Figures`).
The rate taken is a property of the deficit and the window, known to both twins at build time.

The brief's three carries:
- Carry 1 (the residual): attributed in `## Figures`; its fix is carried in `## Forward-carry`.
- Carry 2 (part-load refill pricing): built for `_terminal_cost` and `_deferred_energy_cost` together. The hot-water LP's secant was measured, and its segmentation refused and carried.
- Carry 3 (Carry 2's segmenting and refill-rate decision, and its zero-derate control): the decision is the paragraph above; the control is `## Null control` and the companion's `d = 0` rows.

Carries 4, 5 and 6 on the roster entry are this body's own `Carry: R10-SAV-VALUATION-RESIDUE` items, landed by the carry fold, not further work:
- Carry 4 is the merge-base residual in `## Figures` (-3.90 % flat, -8.02 % varying).
- Carry 5 is the residual's attribution in `## Forward-carry`.
- Carry 6 is the hot-water LP's secant in `## Forward-carry`.

## Head

61241004989d6a432faf2e4d8523b8a2883439e8 (round 2). It is cut from 9394a652, round 1's head, with `origin/main` cbd23f1c8bf6185c3a6c10f6e4aaf562417e75bf merged in at 56a5572a.

That merge had one textual conflict, `tests/structure_budgets.json`'s `class_excess_loc`. The ledger merge driver resolved it (`17537 + both deltas = 17533`), and it was re-measured on the merged tree: `python3 tests/structure.py` prints `ok class_excess_loc 17533 <= 17533` and `STRUCTURE RATCHET PASSED`. No cap was raised. VERSION, the manifest and RELEASE_NOTES are untouched (`prepr.sh` `no version edit` ok).

Base figures are at 32aea942, the branch's cut. Round-2 figures were re-taken at 61241004 on 2026-11-11 (UTC), with main at cbd23f1c.

## Round 2

Round 1's block (`Fix review: blocked 9394a652 mutation-vacuous`) named three gaps:
- The split buffer/building arm of `_terminal_row_cost` was unpinned: the `if refill is not None:` inside `if cop_buffer != cop_end:`.
- The 2723 `CLAMP_DROP` survivor had no triage.
- The `hours <= 0.0` arm of `refill_power_kwh`'s guard survived and had no triage.

What this round did:
- **Valved arm.** A new `tests/features.py` check, `R10-SAV-VALUATION-RESIDUE: on a valved install ...`.
  - The install is two-zone, with a `manual` valve, a 300 L tank and `cop_flow_carnot`. So `buffer_is_store` holds, and `cop_buffer` 1.4551 differs from `cop_end` 2.4500.
  - Both conditions are asserted as preconditions, read off `_terminal_row_cost`'s own arguments through a spy.
  - The check asserts that the derated terminal (`d = 0.2`) equals the law applied to the split linear figure, within 1e-9. The law is `power_for_heat_per_cop_kw` at the refill hours.
  - It also asserts that `_terminal_cost_batch`'s row equals the scalar at both derates.
  - Head readings: linear 65.425760, derated 81.782200, law 81.782200.
- **`refill_power_kwh`'s guard deleted, not triaged.**
  - `power_for_heat_per_cop_kw` already returns its input unchanged when `d == 0` or `band <= 0`, and `hours <= 0` makes `band <= 0`. So neither arm of the guard could change a result.
  - Both mutants survived even a direct contract check: the guard made `if False:`, and the `hours` arm dropped.
  - Deleting the guard removes both sites.
  - A third new check, `refill_power_kwh returns its input bit for bit ...`, pins the pass-through and the `copysign` that carries the sign. The pass-through is checked with no derate at either sign, and at `hours` 0 and -1.
- **Clamps triaged as equivalent.** The three sites are `optimizer.py` 2718, 2719 and 2723, all `CLAMP_DROP`.
  - Triage rows: `tests/mutation_ledger/survivor_triage/optimizer.py/_terminal_row_cost.row_cost.CLAMP_DROP.{374beae5,bce793a5,9e69f3b6}.json`, written by `mutation_table.row_text` at the inventory's own anchors.
  - `cop_end` is `compute_cop(...)`. `cop_buffer` is `marginal_cop(..., "buffer", ...)`, which is `compute_cop(..., flow_temp=...)`.
  - Both end in `_cop_law`'s `return max(cop, 1.0)`, so the 1e-6 floor never binds.

Alternative that lost: triaging `refill_power_kwh`'s two guard arms as equivalent. Deleting the guard won because it duplicated the inverse's own pass-through, and a triage on a deletable line keeps dead code (`fixer.md` step 17).

Class sweep. Rule: `git grep -n -E "_refill_law|_bought_back|refill_power_kwh|refill\(" -- custom_components/` enumerates every site that applies the law. Every site it returns, with its disposition:
- `optimizer.py:2713`: the split arm. Closed in this diff by the valved check (M7 below).
- `optimizer.py:2723`: the single-sum arm. Already guarded by round 1's check (round 1 M8).
- `optimizer.py:3081`: `_terminal_cost` builds the law both terminal arms receive. Already guarded (round 1 M2).
- `optimizer.py:5640`: `_deferred_energy_cost` applies the law once, to the total after the per-store COP corrections (`for store, ... in tanks`). It has no split arm. Already guarded (round 1 M1).
- `optimizer.py:2647` and `2655`: `_refill_law` and `_bought_back`, the law's definition and its one wrapper. Already guarded (round 1 M3, M4).
- `thermal_model.py:2601`: `refill_power_kwh` itself. Closed in this diff (guard deleted; contract check; M11 below).

The rule's other hits are `config_flow.py`'s `async_step_*_prefill`, which match on the name only.

## Mutation proof

Round 1, at 5c368ab. Each production line was neutralised in turn, the new `tests/features.py` check run (its block standalone), and the line restored. Each run printed FAIL `R10-SAV-VALUATION-RESIDUE: under a part-load derate the terminal cost and the deferred settlement ...`. The four mutants were: `_deferred_energy_cost`'s conversion made the identity (at the first commit, `electrical = refill(electrical)` to `pass`); `_terminal_cost` passing `None` for the law; `_refill_law`'s derate guard made always-`None`; and `refill_power_kwh` returning its input.

Round 2, at 61241004. The block was run standalone: `tests/features.py` from `# --- R10-SAV-VALUATION-RESIDUE` to the next block, under `PYTHONPATH=tests/hastub`. Each production line was neutralised in turn, then restored:
- M7, `optimizer.py:2712` `if refill is not None:` to `if False:`: FAIL `... on a valved install ...`.
- M11, `refill_power_kwh`'s `math.copysign(...)` to its bare first argument: FAIL `... under a part-load derate ...` and FAIL `... refill_power_kwh returns its input bit for bit ...`.
- M8b, the 2723 clamp `max(cop_end, 1e-6)` to `(cop_end)`: all three PASS. Equivalent; triaged in `## Round 2`.
- NULL, a comment line added inside `_terminal_row_cost`: all three PASS.

At the head all three PASS.

## Null control

At `d = 0` the companion harness reads every terminal, deferred and LP gap as 0, over 32 solves at both ends (`null rows not zero 0`). The check asserts `_refill_law` is `None` with no derate, and the valved check's `d = 0` figure is the split linear one, which its batch row equals. The base tree reads the defect: the same check FAILs at 32aea942, where the derated terminal equals the linear one.

Flat-price null (mandatory): the flat day's rows are printed beside the spread day's. The derated refill's move of the savings figure is the `predicted_savings` column of `r10_sav_valuation_residue.py` at both ends, apart from the stored-heat term. The residual attribution runs at `d = 0`, so it reads the same at both ends: no part-load term is in it.

## Figures

- **Carried figures**, re-measured at the merge base: `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_partload_pricing.py`.
  - Flat `d=0.112`: lp_err max 0.267290 (dhw cost max 7.0145), terminal-at-max max 4.368455, deferred-at-max max 2.140129; `null rows not zero 0`.
  - The harness applies the linear rule's bound to the production figure. So at the head its terminal and deferred columns still print a bound: it measures what this fix replaces, and the companion below reads the defect.
- **Companion**, `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_sav_valuation_residue.py`. It compares the production figure against `power_for_heat_per_cop_kw` at the refill hours, applied to the zero-derate figure.
  - Base 32aea942: spread `d=0.112` terminal gap max 3.150490, deferred gap max 0.440868; flat `d=0.112` terminal gap max 2.835283, deferred gap max 0.187447.
  - Head 5c368ab, and again at 0edaebae: all four 0.000000.
  - LP gap (left by this fix): spread 0.202595, flat 0.335995 at both ends.
  - `d=0` rows read 0 at both ends; `null rows not zero 0`, `failures 0`.
  - 7b60fb7 and 21f178bc change only `tests/`.
- **Companion, round 2**, at 61241004 (sha1 146c08d9faf2823f2779f01b68cf44f6f1b62648): `spread d=0.112 ... terminal gap max 0.000000 deferred gap max 0.000000`, and `flat d=0.112` the same; LP gap 0.202595 / 0.335995; `null rows not zero 0`, `failures 0`. Its 16 cells set no `cop_flow_carnot`, so none takes the split arm. The valved check in `## Round 2` is the split arm's reading.
- **Residual** at the merge base, `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py valve-flat` and `valve-vary`: -3.90 % (flat), -8.02 % (varying). These arms run at `d = 0`, unchanged by this diff. It is attributed below; the finding is the first `## Forward-carry` item. Carry: R10-SAV-VALUATION-RESIDUE
- **Attribution** (carried in `## Forward-carry`), `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_residual_attribution.py flat` and `winter_typical`. Units are kWh_th over the arm's plant steps (`plant steps seen 192 of 192`).
  - Flat: the booked reference, stepped from its held state, draws -34.85 from its stores and loses +12.52 beyond the steady comfort term. Together that is -22.33 kWh_th, the residual.
  - Varying: -34.85 and +11.89.
  - The store term is price-independent; a reference at equilibrium reads 0 on it.
  - Ruled out first by a probe on the same loop: the buffer tank's standby loss, plan less held reference, is +0.07 kWh_e against the flat arm's -5.21 kWh_e gap.
- **LP segmentation, refused.** The hot-water LP was cut into four equal draw slices of the band, each step's energy priced at its slice's slope, and `r10_partload_pricing.py` run at that tree.
  - Every derated hot-water cell's published hot-water cost rose: flat 7.0145 to 7.8780, spread 8.0681 to 8.8053 (every draw at the floor, 1.500 kW).
  - The base LP publishes the true inverse of the energy it buys, so its secant is a valuation error, not a delivery one.
  - A convex-exact program cannot cost more in truth, so the chord model misprices. The segmentation was reverted.
- **Structure**, `python3 tests/structure.py`: `class_excess_loc` 17537 to 17536 at round 1 (re-recorded: the law and the shared refill price at module level). At round 2's merge, 17533 <= 17533.
- **Gate, round 1**: `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` (`tests/closure.py select --diff 32aea942`). `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` at 5c368ab: 26 scripts ok, and `tests/features.py` red on R9-F2.5's capture builder, which wrapped `_terminal_row_cost` at four arguments. The builder forwards the law at 7b60fb7, and `PYTHONPATH=tests/hastub python3 tests/features.py` there prints `ALL 5188 FEATURE CHECKS PASSED`.
- **Gate, round 2**, at 61241004:
  - `tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`
  - `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` prints `1 TEST SCRIPT(S) FAILED`. The one red is `tests/features.py`, `1 of 5240 FEATURE CHECKS FAILED`: `combi_type_branch census`. That red is inherited from main, not made by this diff. The vendor regex `alpha.?innotec|mfs ?[0-9]|luxtronik` matches 6 lines in the package's top-level `*.py`, against `_CB_VENDOR_BASE = 4`. The count is 6 at both `origin/main` cbd23f1c and this head, by `git grep -i -E` on each ref, so this diff adds none. `ALL 116 STRESS CHECKS PASSED`.
  - `tools/pr/prepr.sh` exits 0; its `merged structure` step prints `STRUCTURE RATCHET PASSED`.

## Red checks

`tests / mutation` is red, as `prepr.sh` step 6d predicts.
- At round 2 it names 11 added unpinned sites, which `tools/pr/ci_predict.py --base origin/main` lists. After the three triage rows, 8 remain.
- Those 8 are owed to `mutation-autofix`; see `## Unpinned sites`.
- Root-cause answer: the cheaper detector is step 6d itself. It predicted the red locally at no added standing cost, and none further exists to build.

## Unpinned sites

Each site is on `custom_components/`, the lane `mutation-autofix` mutates. A kill marked "measured" was read in a standalone mutation proof: round 1's or round 2's (`## Mutation proof`). The lane records each kill, and `tests / mutation-pins` confirms it.

- custom_components/heatpump_optimizer/optimizer.py:137 CONST: pinned by `mutation-autofix` (round 1, quantile 0.25 to 0.5 killed, measured)
- custom_components/heatpump_optimizer/optimizer.py:2629 RETURN_DEL: pinned by `mutation-autofix` (unmeasured)
- custom_components/heatpump_optimizer/optimizer.py:2644 GUARD_OFF: pinned by `mutation-autofix` (round 1, the derate guard, measured)
- custom_components/heatpump_optimizer/optimizer.py:2647 RETURN_DEL: pinned by `mutation-autofix` (unmeasured)
- custom_components/heatpump_optimizer/optimizer.py:2656 RETURN_DEL: pinned by `mutation-autofix` (unmeasured)
- custom_components/heatpump_optimizer/optimizer.py:2712 GUARD_OFF: pinned by `mutation-autofix` (round 2 M7, measured)
- custom_components/heatpump_optimizer/optimizer.py:2718 CLAMP_DROP: triage `survivor_triage/optimizer.py/_terminal_row_cost.row_cost.CLAMP_DROP.374beae5.json` (equivalent)
- custom_components/heatpump_optimizer/optimizer.py:2719 CLAMP_DROP: triage `survivor_triage/optimizer.py/_terminal_row_cost.row_cost.CLAMP_DROP.bce793a5.json` (equivalent)
- custom_components/heatpump_optimizer/optimizer.py:2722 GUARD_OFF: pinned by `mutation-autofix` (round 1, the single-sum guard, measured)
- custom_components/heatpump_optimizer/optimizer.py:2723 CLAMP_DROP: triage `survivor_triage/optimizer.py/_terminal_row_cost.row_cost.CLAMP_DROP.9e69f3b6.json` (equivalent; round 2 M8b survived)
- custom_components/heatpump_optimizer/optimizer.py:5640 RETURN_DEL: pinned by `mutation-autofix` (round 1, the deferred conversion, measured)

Round 1's `thermal_model.py:2603` sites (`GUARD_OFF` and `CMP_BOUND`, plus the `hours` arm the reviewer's M10 dropped) left the tree with the guard. `ci_predict.py` lists no site in `thermal_model.py`.

## Forward-carry

- **The savings residual's attribution.** The booked reference's held state is not held by the power booked for it: -34.85 kWh_th over the arm, price-independent. It also loses +12.52 / +11.89 kWh_th beyond the steady comfort term.
  - A fix there changes the reference (`_thermostat_held_state`, `_compute_baseline_power`'s first step), not stored-heat valuation.
  - Legitimate only if the store term reads 0 on a reference at equilibrium and the flat arm's residual moves by the term's share.
  - Re-measure with `r10_sav_residual_attribution.py` at the merge base.
  - Pending the orchestrator's ruling on its owner. Carry: R10-SAV-VALUATION-RESIDUE
- **The hot-water LP's secant** (`_plan_dhw_min_cost`, flat 0.335995 / spread 0.202595 per day against the tree's inverse) is left. Equal-slice segmentation measured worse in truth (`## Figures`).
  - A segmented LP is legitimate only if, on `r10_partload_pricing.py`'s cells, the published plan's true hot-water cost does not rise at any derated cell and the `d = 0` rows stay bitwise.
  - Pending the orchestrator's ruling on its owner. Carry: R10-SAV-VALUATION-RESIDUE

## Friction

none
