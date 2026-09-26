# S5 class sweep: P5 -- a sysid/adoption gate keyed on a quantity other than the bias it gates

Ledger class `P5`, open since round 1, instances in rounds 1-7. Round-9 verified findings:
D2-s4-01, D2-s4-81, D14-s3-03.

## Enumerator

Reused `tools/audit/round9/D14/s3/p5_gate.py` (the D14-s3 finder's detector) unchanged: a
synthetic-bias sweep through the production experiment (`sysid.SystemIdentification.arm/step`,
rolled on the production `ThermalModel`) ruled by `sysid.adoption_decision`, plus a static
`--seams` listing of every site that writes a learned thermal parameter.

Command: `PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/s3/p5_gate.py [--seams] [--perturb prior_true]`

## Controls (re-run on this box, this session)

- **Baseline** (72 cells: 3 presets x 5 bias sources x graded magnitudes): `p5_cells=72`,
  `p5_admitted=39`, `p5_admitted_over_bar=3`, `p5_admitted_over_bar_null=0`,
  `p5_worst_blended_shift_pct=7.970%`, `p5_worst_admitted_err_pct=21.431%`. Identical to the
  D14-s3 finder's recorded numbers.
- **Null control**: the magnitude-0 cell of every source (no injected bias) is included in the
  same sweep and is 0/15 admitted-over-bar (`p5_admitted_over_bar_null=0`).
- **Perturbation** (`--perturb prior_true`, the fit is given the true free-heat prior):
  `p5_admitted_over_bar` goes 3 -> 0 on every source, `p5_worst_blended_shift_pct` 7.970% ->
  3.110%. Moves in the documented direction.

## Seams (`--seams`, static)

19 sites across `coordinator.py` write one of 6 learned thermal parameters
(`house_heat_loss_scale`, `defrost_derate`, `buffer_cooling_rate`, `cop_scale`,
`lower_floor_loss_ratio`, plus the two `async_run_optimization` writes of
`internal_gains_profile` / `solar_aperture_scale`). Full list in `seams.txt` beside this file.

## Disposition

- **3 instance** (verified, sysid seam): the 3 admitted-over-bar cells at baseline
  (`typical_slab`/gains mag 0.4, mag 0.8; `heavy_old`/gains mag 0.8) -- these are D2-s4-01 /
  D2-s4-81 / D14-s3-03, all one mechanism (the gate keys on `UA_ADOPTION_HALFWIDTH_BAR`, which
  moves far less than the true UA error).
- **1 not applicable**: `coordinator:_adopt_system_identification` -- this is the gated writer
  itself (the seam the sweep measures), not a sibling seam.
- **15 not applicable**: the passive-learner seams (`_learn_measured_cop`, `_async_learn_*`,
  `_reanchor_house_heat_loss_scale`, `_apply_learner_payloads`, `_async_load_thermal_learning`,
  `_init_features`, `_init_measurements`) each apply their own EWMA / bounded-step update with no
  single-fit admission gate to key inconsistently -- there is no "bias vs. gated quantity"
  mismatch to have, because there is no discrete admit/reject decision at these seams. This
  reproduces the D14-s3 finder's own scope note (only the sysid seam is swept) rather than
  widening it: I checked each of the 15 for a discrete gate (grepped for `if .* > .*bar\|halfwidth\|adopt`
  around each write site) and found none.
- **0 guarded.**

## Count and RCA

N = 3 verified findings (D2-s4-01, D2-s4-81, D14-s3-03) + 0 additional sweep-confirmed instances
= 3. **rca: true** (N >= 3), matching the brief's table.

## Barrier proposal

`p5_gate.py` (no flags) as a `tests/` script asserting `p5_admitted_over_bar == 0`. Cost: ~1.8s
wall (measured this run, uncontended).

## Unfinished / exposure

- `async_update_thermal_params` (the direct-write seam from `set_thermal_parameters`, D1-s2-53's
  seam) writes `house_heat_loss_scale` and `buffer_cooling_rate` with NO admission gate at all --
  this is not a P5 instance (there is no gate to key wrong), but it is the same two attributes P5's
  sysid gate protects, written un-gated from a service call. Flagged as a **lead** for D1/whoever
  owns D1-s2-53's fix: an honest P5-shaped fix (tightening the sysid gate) does nothing if this
  sibling writer bypasses the gate outright.
- Pre-#1410 P5 instances were not re-found at their pre-fix commits (reused the D14-s3 finder's
  own "Unfinished" note).
