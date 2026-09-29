# Round 9, D0-s1: finder report (D0)

Rendered by the box B1 thread from the JSON report D0-s1 returned, which is stored verbatim in `tools/audit/round9/reports-B1.json`. The seat's own Write tool refused to create a report `.md` file. The JSON is the record, and this file adds nothing to it.

Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`

## Exposure

None: I read nothing under docs/ and nothing on GitHub. In-tree context I read: the seed and stop-rule comments in optimizer.py, and the certificate grid, bars and claims in tests/optimality.py. REPORT.md was NOT written: this session's Write tool refuses report .md files from subagents, so everything REPORT.md would hold is in this JSON.

## Coverage

- **D0.M1** (deep): race.py wraps optimizer:_multi_start_minimize with mock.patch.object. For every call it records objective, candidates, bounds, args (the fixed DHW schedule), maxiter, batch_objective, fd_eps and the returned x. Challengers replay production's own jac path (_batch_fd_gradient where _bounds_supported_by_batch holds). Every plan is scored on the exact captured objective. coord.py captures the same seam through a real HeatPumpOptimizerCoordinator.async_run_optimization cycle, with _await_optimize patched to run optimize_in_process inline.
- **D0.M2** (deep): Per captured call the challengers were: a tight polish (ftol 1e-12, gtol 1e-9, maxiter 3000, maxfun 1e6); every production candidate refined alone through the real seam; 13 bang-bang anchors at 0 to 3.0x production's own baseline-thermostat energy (hooked at HeatPumpOptimizer._compute_baseline_power), each refined alone; then a warm-start tight polish of the best one. Two A/B harnesses change one production input each: seeds_ab.py (the DHW path's seed set) and stoprule_ab.py (ftol 1e-6 -> 1e-9, with nit/nfev counts). No global outer bound was run (see unfinished).
- **D0.M3** (deep): A challenger counts only if its floor and ceiling breach (degree-steps outside 17-23 C, summed over room for single-zone and upper+lower zones for two-zone, the zones the objective scores) is no worse than production's plus 0.01. On the DHW path the DHW schedule is a fixed argument of the captured call, and the minimum DHW temperature printed by every A/B pair is identical. Power bounds are the captured bounds. Result: cells_feasibility_worse=0 on every seed arm and 3 on the ftol arm.
- **D0.M4** (deep): The shipped 24 h horizon over 4 winter prices x 5 weathers x {single, two-zone} x {DHW on, off} = 80 cells (race.py): gap max 0.5340 %, mean 0.0767 %, 20 cells over 0.1 %. Coordinator captures: 4 configs x 4 prices = 16 cells (coord.py), max 0.1552 %. 6 h and 48 h runs on a 6-cell subset. Valve and wood topologies were not swept, and the 6/48 h runs cover only the subset (see unfinished).

## Findings

### D0-s1-01: The two-zone 0.20x deep anchor is built only in _optimize_space_only; the DHW path's _solve_space never gets it

- step D0.M2, severity low, class bug, class_guess P4, provisional None

**Claim.** The DHW path, which every default install runs, builds its own cold-start seed set in HeatPumpOptimizer._solve_space, and that set does not include the two-zone 0.20x baseline-energy anchor. Adding that anchor lowers the shipped objective on two-zone DHW-on winter cells by up to 0.2507 % (0.3396 objective units per day). The paired flat-price cells show 0.0000 %.

**Mechanism.** _optimize_space_only seeds from the baseline thermostat: its power, plus bang-bang anchors at 1.0x and 0.35x of its energy, plus 0.20x for two-zone houses. _solve_space seeds instead from init_base: an init_base-shaped guess, bang-bang at init_base energy, headroom*0.5, and bang-bang at 0.35x init_base energy. So the DHW path has no baseline-power seed, keys its anchors on a different energy, and never gets the 0.20x under-heat anchor that round 7 found the price-driven two-zone optimum needs.

**Metric.** Per cell: (objective_value shipped by production - objective_value shipped with the 0.20x baseline-energy anchor added to _solve_space's cold-start candidates) / |shipped|.

**Instrumented symbol.** `heatpump_optimizer.optimizer:_multi_start_minimize (the cold-start call from HeatPumpOptimizer._solve_space; read back through HeatPumpOptimizer.optimize(...).objective_value)`

**Phenomenon property.** Every cold-start _multi_start_minimize call for a given topology should get the same structural seed set, keyed on the same baseline energy, whichever solve path (space-only or DHW) makes the call.

**Seam rule.** `grep -n "_multi_start_minimize(\|_price_ranked_start(\|_LOW_ENERGY_START_FRACTION\|_DEEP_LOW_ENERGY_START_FRACTION" custom_components/heatpump_optimizer/optimizer.py`

**Proposed fix scope.** Build the cold-start structural seeds once, in a helper keyed on the baseline thermostat energy (baseline power, 1.0x, 0.35x, and 0.20x for two-zone). Call it from both _optimize_space_only and _solve_space; this means computing _compute_baseline_power before the DHW path's space solve. Add a DHW-on two-zone winter cell to tests/optimality.py's _CERT_CELLS so the DHW path is certified at all; today every certificate cell is DHW-off.

**Files.** custom_components/heatpump_optimizer/optimizer.py, tests/optimality.py

**Evidence**

```json
{
  "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D0/s1/seeds_ab.py --perturb deep_anchor_dhw --jobs 3",
  "harness_path": "tools/audit/round9/D0/s1/seeds_ab.py",
  "value": 0.2507,
  "unit": "% of the shipped objective (drop_rel_max over 40 DHW-on cells)",
  "baseline_sha": "1936d5ca72a06556eeed4e8e5bf3dea520e517e1",
  "machine": "box B1: 4 vCPU Linux, CPython 3.14.0rc2, numpy 2.4.6, scipy 1.17.1",
  "cpu_or_wall": "count",
  "contention_note": "Shared box with up to two other compute seats, load1 3.26. The number is an objective value, so it is contention-immune.",
  "tolerance": "±0.05 pp (the basin choice is BLAS-build dependent)",
  "load1": 3.26,
  "thread_factor": 1.735
}
```

**Perturbation**

```json
{
  "change": "Production edit: in HeatPumpOptimizer._solve_space's `if warm_start is None:` block, append np.minimum(_price_ranked_start(prices, baseline_energy * _DEEP_LOW_ENERGY_START_FRACTION, p_max, dt), headroom) for two-zone houses, with baseline_energy taken from _compute_baseline_power before the space solve. Better: one shared seed helper used by both solve paths. The harness's arm B then duplicates an existing seed.",
  "expected_direction": "to_zero",
  "observed_value": "In the harness's in-memory arm: 135.443194 -> 135.103629 (two|dhw|winter_narrow|winter_cold), 58.215499 -> 58.136299 (two|dhw|winter_narrow|winter_mild), 129.340129 -> 129.283828 (two|dhw|winter_extreme|winter_cold). All 20 single-zone cells show drop 0.0000 exactly (built-in no-op control)."
}
```

**null_control**

```json
{
  "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D0/s1/seeds_ab.py --perturb deep_anchor_dhw --flat --jobs 3",
  "value": "Flat prices, 10 cells: the paired winter_cold and winter_mild two-zone DHW cells are 0.0000 % (107.886615 -> 107.886615; 47.054120 -> 47.054120). One flat cell moves (two-zone shoulder weather, 0.2342 %) while its winter-price twin does not.",
  "note": "On the cells that carry the gap it is price-driven. The wider arm (--perturb space_seeds_dhw, which also adds the baseline-power seed and the 1.0x/0.35x baseline anchors) gives max 0.2751 %, mean 0.0398 % at winter prices, but survives flat prices (mean 0.0718 %, 6 of 10 cells). That wider part is a comfort/energy basin gap, not price optimality, and is recorded only as context for the fix scope."
}
```

**leave_one_out**

```json
{
  "cells": 20,
  "min": 0,
  "max": 0.2507,
  "drop_most_favourable": 0.0094
}
```

**reproduction_steps**

```json
[
  "From /home/claude/audit-r9-D0-s1: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D0/s1/seeds_ab.py --perturb deep_anchor_dhw",
  "Read the three moving CELL lines (two|dhw|winter_narrow|winter_cold, two|dhw|winter_narrow|winter_mild, two|dhw|winter_extreme|winter_cold) and RESULT drop_rel_max",
  "Control: add --dhw off (40/40 cells drop exactly 0) and --flat (the paired winter-weather cells stay at 0)",
  "Race context: race.py --cells two:dhw:winter_extreme:winter_cold gives a gap of 0.2616 % whose best seed is anchor 0.0; anchor 0.2 lands within 0.0003 units of it"
]
```

## Non-findings

- Across the 80-cell 24 h grid, production's plan is within 0.54 % of the best feasible challenger on its own objective. The largest gaps sit on low-bill shoulder-weather days (5 to 7 SEK) whose winning anchors are 2.0x to 2.5x the baseline energy. That is the refused-ladder class the certificate already claims for one|winter_narrow|shoulder.: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D0/s1/race.py --jobs 3` gave gap_rel_max=0.5340 % (one|nodhw|winter_moderate|shoulder, 0.0457 units on a 5.20 SEK day); mean 0.0767 %; mean with the worst cell dropped 0.0709 %; 20/80 cells over 0.1 %. DHW on: mean 0.0811 %, max 0.3870 %. DHW off: mean 0.0723 %, max 0.5340 %.
- Coordinator captures (the real async_run_optimization input assembly, 4 configs x 4 winter prices) show no material gap.: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D0/s1/coord.py` gave 16 cells: max 0.1552 % (coord_two_zone|winter_extreme), mean 0.0247 %, mean with the worst cell dropped 0.0160 %, 2 cells over 0.1 %.
- The ftol=1e-6 stop-rule residue is not price-attributable in aggregate, and tightening the stop rule is an existing refused disposition (#1293, per the certificate claim in tests/optimality.py).: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D0/s1/stoprule_ab.py --jobs 2 ; ... --flat --jobs 3` gave Winter prices, 80 cells: 15 over 0.1 %, max 0.9837 %, mean 0.0646 %, min -0.0187 %, 3 cells with a worse floor, nit_ratio 1.6294, nfev_ratio 1.9296. Flat prices, 20 cells: mean 0.0563 %, max 0.2791 %. Paired excess of winter over flat: mean 0.0083 %.
- The 6 h horizon shows no gap.: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D0/s1/race.py --horizon 6 --jobs 3 --cells two:dhw:winter_narrow:winter_cold,two:dhw:winter_extreme:winter_cold,one:dhw:winter_typical:winter_cold,two:nodhw:winter_typical:winter_cold,one:nodhw:winter_extreme:winter_mild,two:dhw:winter_moderate:winter_mild` gave gap_rel_max=0.0003 % over 6 cells
- The 48 h horizon shows up to 1.43 %, mostly stop-rule residue, but no user can reach it: OptimizationConfig.from_mapping never reads a horizon and the dataclass default is 24.0.: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D0/s1/race.py --horizon 48 --jobs 3 --cells <same 6 cells>` gave gap_rel_max=1.4264 % (two|dhw|winter_moderate|winter_mild, of which 1.28 % is closed by the tight polish from production's own point); 3/6 cells over 0.1 %.
- The seed A/B harness is a no-op on the space-only path, which already carries the seeds (a control for finding 01).: `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D0/s1/seeds_ab.py --dhw off --jobs 3` gave 40/40 cells drop 0.0000 %
- The multi-start refines every candidate it is handed. On the DHW path the co-optimisation re-solve gets one warm-start candidate.: `race.py capture (the n_cand field per call in the JSON the harness prints the path of)` gave n_cand is 4 on the DHW cold-start call and 4 to 5 on the space path; no candidate is discarded

## Harnesses

- `tools/audit/round9/D0/s1/race.py`
- `tools/audit/round9/D0/s1/coord.py`
- `tools/audit/round9/D0/s1/seeds_ab.py`
- `tools/audit/round9/D0/s1/stoprule_ab.py`

## Unfinished

- **D0.M2**: No global outer bound was run (scipy differential_evolution, or a DP on a coarsened grid). The best challenger is the best of 13 energy anchors, every production candidate refined alone, and tight polishes.
- **D0.M4**: The valve-storage and wood topologies were not swept, and horizons 6 h and 48 h ran on a 6-cell subset only. 48 h is not user-reachable: OptimizationConfig.from_mapping never reads a horizon, so it stays at the 24.0 default.

## Leads

- owner D3-s3, `tests/optimality.py` `score_plan / pin_result`: The pin 'the plan holds the comfort floor' reads the room series even for two-zone houses, but the objective's floor is on the upper and lower zones. On two-zone DHW-on winter_typical/winter_cold the shipped upper zone reaches 16.53 C (1.34 degree-steps below 17) while room stays at or above 17.57, so the pin cannot see the breach. Separately, _CERT_CELLS contains no DHW-on cell although DHW is on by default.
- owner D0-s3, `custom_components/heatpump_optimizer/optimizer.py` `HeatPumpOptimizer._solve_space / _co_optimize`: M6: does MPC re-planning mask finding D0-s1-01? Step-0 power moves only 1.197 -> 1.200 kW in the largest cell and not at all in the other two. M7: the co-optimisation re-solve is handed a single warm-start candidate.
- owner unknown, `custom_components/heatpump_optimizer/optimizer.py` `HeatPumpOptimizer._comfort_terms`: D2 scope: on the default two-zone winter day, shipped two-zone plans breach the upper-zone floor by 1.34 degree-steps, a trade the soft penalty accepts. Whether that is intended belongs to the objective's owner.
