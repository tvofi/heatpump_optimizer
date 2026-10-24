# D7-s1 report (round 10, baseline 17f1c55fad1b)

Cells: D7.M1, D7.M5 over `**`. Box B5, load1 68-84 during the run (heavily shared).

## Method
- M1: ran `tests/structure.py` (16 budget keys, all at zero headroom, ratchet passes).
  Then drove the production `tests/structure.py:measure` over an in-memory padded
  tree (`class_growth.py`): 1201 lines of new, called, non-duplicated, CC-1 code
  added to the second-largest class (`HeatPumpOptimizer`, 3510 lines) versus the
  same pad in the coordinator.
- M5: spot only (see Unfinished).

## Findings
### D7-s1-01 (low, hygiene/instrument) — class growth below the coordinator is unpriced
`max_class_loc` is `max(...)` over god classes, so only the largest class is
budgeted. Adding 1201 lines to `HeatPumpOptimizer` moves 0 of 16 budget keys;
the same pad in the coordinator moves 1 (`max_class_loc` 8705 -> 9906).
Perturbation: `"max_class_loc": sum((g[0] for g in god_classes))` -> second-class
arm moves 1 (executed). Headroom for unpriced growth: 8705 - 3510 = 5195 lines in
`optimizer.py` alone. The same "only the worst is priced" shape the docstring
(#374) fixed for functions remains for classes.
Command: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/s1/class_growth.py [--structure <edited copy>]`

## Non-findings
- structure ratchet at baseline: 16/16 metrics ok at equality (structure.py RESULT lines).
- coordinator arm control: max_class_loc moves 8705 -> 9906 exactly (+1201), no other key moves (seam_cut_total unchanged, dead_methods 0).

## Readings (M1)
- coordinator: 8705-line class, 228 methods, 151 attrs (118 multi-assigned), max_cc 45, max_method_loc 373.
- D7.md's "all 24" and "the `cut_*` keys and `cross_seam_edges`" do not match the
  budget file (16 keys; seam cost is `seam_cut_total`). Brief text, routed as a lead.

## Unfinished
- M5: executed spot-mutation table not produced. Spot evidence only: `_dhw_confidence_band`
  (coordinator.py:4004) is asserted by tests/plan_view.py:91-104 and tests/features.py:31889-31982;
  Tuya-named code appears in 13 integration modules (no single owning module) by grep.
  Box load 68-84 made a features.py run per mutation infeasible inside the budget.

## Exposure
none
