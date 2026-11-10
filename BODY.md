Fix review: merge 31969d9cd47906e73b2e0daa93e445cc61881574

## Findings
- None blocking. coordinator.py:1081-1088 apportions the slab's draw by the mode dwell's (space, dhw) hours where observed (heat_energy.attribution), else the plan split; draw_range.py:408 docstring matches. `space_served=a.observed or ...` is required for the switch-out arm (otherwise 0 kW).
- Minor, not blocking: coordinator.py:988 refactor is behaviour-neutral (same attribution call, two fewer locals).

## Evidence
- Diff read: `git diff a5dce6b9e...31969d9cd` (coordinator.py, draw_range.py, tests/features.py, two harnesses, closures.json, delivery row).
- Finder harness r10_cop_gate_slab.py at head (PYTHONPATH=tests/hastub:custom_components:tests): all_space booked 4.0 over 0.0; switch_back 2.0 over 0.0; switch_out 2.0 over 0.0; truth 2.0. Perturbed --drawn 8: books 4.0/4.0, over 0.0 (scales). Same harness at base sources: switch_back booked 4.0 over +2.0; switch_out booked 0.0 over -2.0 (defect reproduced, fixed at head).
- r10_cop_gate_band.py runs at head (RESULT lines, fit=none on replay fixtures).
- tests/features.py at head: full run, 0 FAIL lines; the three R10-COP-GATE-E checks ok (null control included).
- Mutation 1 (revert `(a.space, a.dhw)` to `coord._commanded_split()`): both switch checks FAIL (24.1700/23.5050/22.8400), null control ok.
- Mutation 2 (drop `a.observed or` from space_served): switch-out check FAIL (22.8400 vs 23.5050), others ok.
- Not run: CI, closure/ratchet tools (no CI per brief).
