# Round 9 — D2-s4 (D2.M5 estimators), baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1

Seat D2-s4, box B6 (4 CPU cloud container, shared with other finders; load1 5-6.5 during runs).
Cells: all files, step D2.M5 only. Interpreter /home/claude/venv/bin/python, PYTHONPATH=tests/hastub,
run from the export root. All finding numbers are counts or ratios over fixed seed sets (exact,
contention-immune); no wall/CPU/RSS number is claimed.

Exposure: none. No earlier-round evidence (tools/audit/round3..round8) was read; no docs/, no GitHub.

## Method

The production step experiment is driven end to end: `SystemIdentification.arm(plant=...)`
and `.step(...)` every coordinator tick on a two-state preset plant (`tests/stress.py:BUILDINGS`
via `presets.derive`, rolled on the production `ThermalModel`), the sensor corrupted by white,
quantised (0.05/0.1 degC), drifting (0.02-0.10 degC/h) noise or a mis-set free-heat prior;
`_finish` routes to `identify_slab` (the production fit — `identify()` is harness-only per #1395
and was not measured); the result goes through `sysid.adoption_decision`, the gate the
coordinator's `_adopt_system_identification` applies. Cadence 0.5 h (the production default
`DEFAULT_OPTIMIZATION_INTERVAL`) and 0.25 h. The passive heat-loss learner's
`learner_newton_step` is iterated separately for stationary bias.

## Findings

### D2-s4-01 — the adoption interval is uncalibrated on the fits it admits (P5)

`tools/audit/round9/D2/s4/coverage.py`: over 2 presets x 3 sigma x 2 cadences x 40 seeds,
the gate admits 22 fits; **14 of them (0.636) have their true UA outside their own 95 %
interval** (`slab_ua_adoption_halfwidth(profile, prior)`), against ~0.05 for a calibrated
interval. 21 of 22 admitted fits over-estimate UA (mean +7.26 %, max +18.64 %); the blended
house scale is off by up to +8.95 % (mean +2.71 %) when the learner stood at the truth.
Leave-one-out over the 9 cells with admissions: cell rates 0.286-1.000; dropping the worst
cell 0.611. The ensemble spread of completed fits' log UA has a 95 % half-width of
0.146-0.271 while admitted fits report 0.05-0.09 (diagnostic run, 60 seeds, typical_slab and
heavy_old at 0.01/0.02 degC): the gate selects the noise realisations that happen to produce
a sharp profile, and those are biased high.

Perturbations: `--perturb sigma0` (null control, no sensor noise): 0 of 12 missed.
`--perturb anchor` (the rollout's `first_room_c` replaced by the true first temperature,
i.e. `_simulate_slab_path` no longer anchors the hidden stores on a single noisy reading):
miss rate 0.636 -> 0.439, admitted mean bias +7.26 -> +5.58 % — one identified contributor,
not the whole mechanism. `--perturb bar5`: admitted 22 -> 4, all 4 still missed.
Second seam (`gate_bias.py`, 16 seeds, 0.5 h): with the true free heat 0.2 kW under or
0.4 kW over the configured prior (`gains_prior_kw`), typical_slab admits 3/12 and 2/6
fits beyond the +-10 % bar.

### D2-s4-02 — the step is sized to the abort bound with no noise margin (new)

`tools/audit/round9/D2/s4/sizer_margin.py`: with the plant's own max_electrical_power,
`_size_step_power` targets a peak of `max_excursion_c` and `step()` aborts on the same bound,
so sensor noise alone aborts the experiment: **100 of 294 runs aborted**; light_new 81 of 96
noisy runs (0.5 h cadence: 47/48), typical_slab 18/96 at sigma >= 0.02, heavy_old 0/96.
Noisy-cell abort rate 0.000-1.000, mean 0.344, 0.305 with the worst cell dropped.
Perturbation `--perturb margin` (the returned step x 0.85): 3 of 294. Null control:
sigma 0 at 0.25 h cadence, 0 aborts on every preset. On a light house the estimator
effectively never produces a fit. (The σ=0, 0.5 h light_new abort is the integrator's dt
dependence, filed as a lead to D2-s1.)

## Non-findings

- Drifting sensor (0.02/0.05/0.10 degC/h, typical_slab + heavy_old, 16 seeds, 0.5 h): 0 fits
  admitted of 96 although completed fits are biased -18 % to -49 % — the interval gate refuses
  them (`gate_bias.py --cells drift002,drift005,drift010`).
- 0.1 degC quantisation: 0 of 32 admitted (all "unbounded" interval).
- Noise-free null: every completed fit exact (bias +0.00 %) on typical_slab and heavy_old.
- Passive learner `learner_newton_step`: stationary bias <= 0.0016 of scale at residual noise
  0.05-0.2 degC and true scale 0.6/1.0/1.6 (`newton_bias.py`); the pre-#193 one-sided clamp
  (`--perturb asym`) moves it to 0.473, so the harness sees the class.

## Harnesses

- `gate_bias.py` — the production drive (shared) and per-cell admitted/over-bar counts.
- `coverage.py` — D2-s4-01.
- `sizer_margin.py` — D2-s4-02.
- `newton_bias.py` — learner stationary bias (non-finding).

## Unfinished

- COP learner (`_learn_measured_cop`: EWMA gate, per-step +-5 % and [0.5, 1.6] clamps) — not
  measured; needs a coordinator drive with a noisy power meter (Jensen bias of 1/measured).
- `identify()` one-state regression: harness-only in production (#1395); not measured.
- Two-zone declared-plant fit (`_two_zone_plant`) and throttling-valve plants: not driven.
