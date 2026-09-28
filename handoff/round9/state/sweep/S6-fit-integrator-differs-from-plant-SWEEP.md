# Class sweep — "fit integrator differs from the simulated plant"

Not in `tools/audit/bugclasses.json` (new class this round).

Round-9 finding: **D7-s2-01** (verified, medium — `sysid:identify_slab` rolls the candidate
plant through `_simulate_slab_path` → `_valve_drive` → `ThermalModel.simulate_step`, taking one
explicit-Euler step per recorded 30-min sample: coarser than the optimizer's own 0.25 h step, let
alone a continuous rollout. On a noise-free, parameter-exact house the fit is biased 17–25 % low
or refuses outright, adopting on 0 of 3 presets at the fit's own resolution; a `--substep-rollout`
perturbation (`_valve_drive` split into 6 equal sub-steps) drops
`continuous_presets_bias_gt5pct` from 3 to 0 and lets 2 of 3 presets adopt).

## Enumerator

Heavy per-preset rollout grids are **not re-run** (moderate-cost numeric harness, small-N class
per the sweep brief). `tools/audit/round9/D14/sweep/fit-integrator-differs-from-plant/enumerate.sh`
lists every call site in the fit/identification chain (`_simulate_slab_path`, `_valve_drive`,
`identify`/`identify_slab`) to check whether any *other* fitting routine in `sysid.py` rolls the
plant at a resolution coarser than the path the fitted parameters are later used at.

Positive control: the finder's own `REPORT.md` table (`tools/audit/round9/D7/s2/REPORT.md`,
`D7-s2-01`) is the executed evidence; re-derive with `PYTHONPATH=tests/hastub python3
tools/audit/round9/D7/s2/sysid_plant.py` if a from-scratch re-run is wanted.
Null control: `identify` (the one-state comparator at line 1475, using the closed-form
exponential `_predict_step_excursion`) is a deliberately-kept *control* per its own docstring —
not a production fit path — so it is out of scope for this class, not a null instance of it.
Perturbation: `--substep-rollout` (documented in the harness, a one-line edit splitting
`_valve_drive` into 6 equal sub-steps) is the judge's own perturbation for this finding, not
re-run here.

## Disposition

| seam | disposition | note |
|---|---|---|
| `sysid.py:576-627 _simulate_slab_path` (one `_valve_drive` call per recorded sample interval, `dt_hours` = the sample cadence, ~0.5 h) | **instance** | D7-s2-01 itself — the only call site (`sysid.py:800`, inside `identify_slab`). |
| `sysid.py:1475 identify` (one-state, closed-form exponential fit) | **not applicable** | Not an integrator at all (analytic solution, no step size) and explicitly documented as the retained one-state *control*, not a production fit path this class' mechanism applies to. |
| `sysid.py:231-248 _valve_drive` itself | **not applicable** | Correctly delegates to `ThermalModel.simulate_step` — the mismatch is in the caller's step size (`_simulate_slab_path`'s per-sample `dt_hours`), not in `_valve_drive`. |

## Count

N = 1 verified finding (D7-s2-01) + 0 additional sweep-confirmed instances (only one fitting call
chain rolls the plant; the one-state comparator is out of scope by design). **rca = false** (N=1
< 3, not a ledger class, not barriered).

## Barrier proposal

None proposed at N=1: the fix is a step-size choice inside one function
(`_simulate_slab_path`/`_valve_drive`'s sub-stepping), not a pattern worth a permanent structural
gate.
