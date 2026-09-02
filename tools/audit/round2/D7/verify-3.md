# D7 — verifier seat 3 (perturbation and scope)

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, worktree
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/v-D7-3` (clean at the baseline SHA;
the finder's harnesses were copied in under `tools/audit/round2/D7/` — `tools/` is
`tests/closure.py` `INERT`, nothing under `custom_components/` or `tests/` was left modified;
`git status` at the end is `?? tools/audit/` and nothing else). My own harnesses are in
`/private/tmp/claude-501/audit-scratch/D7-3/`. Interpreter
`…/tvofi-claude/.venv/bin/python`, `PYTHONPATH=tests/hastub`, BLAS pinned. Every number below
is a count, a ratio or a deterministic simulation value; none is a timing, so contention does
not make any of them provisional. `thread_factor=1.0` on every run; `load1` 3.7–13.0.

Stance: I executed **every** finding's stated perturbation, and I attacked scope by varying
single- versus two-zone, DHW on and off, the mixing valve, the wood tank, the capacity/peak
tariff and 24- versus 48-hour horizons wherever the finding's number could see them.

**No finding is void.** Every one of the six moved under its own perturbation. Two findings
carry numbers that are wrong (D7-05, D7-06) and two carry fix scopes that fail on execution
(D7-02 fails `tests/features.py` as written; D7-04 understates its blast radius by 15×).

## Re-runs of the finder's harnesses (all reproduce)

| harness | key RESULTs | thread_factor | load1 |
|---|---|---|---|
| `sysid_plant.py` | `cells=24 admitted_cells=0 aborted_at_production_bound=4 peak_excursion_max=0.9204 control_cells=8 control_admitted=4 control_abs_bias_pct_max=8.056` | 1.0 | 3.68 |
| `learner_gates.py` | every one of the 54 `ingest_*` counts identical; `defrost_scale_tz_f20=1.041379 tz_f50=1.095282 tz_f00=1.000000 sz_f50=1.000000` | 1.0 | 9.23 |
| `trajectory_order.py` | `tc_production=15.305845 tc_delta_abs_max=5.416717 tc_delta_rel_to_energy=0.070771 null_delta_abs=0.000000 poison_raises=1 readers_with_model_call_between=0` | 1.0 | 9.17 |
| `metrics_ast.py` | `coordinator_lines=10902 coordinator_methods=256 coordinator_instance_attrs=174 …multi_writer=132 max_cc=86 import_cycle_sccs=0` | 1.0 | 8.03 |
| `coordinator_clusters.py` | `n_methods=256 cross_attr_fraction_seeded=0.3091 cross_attr_fraction_k10=0.33 seam_min_cut_name=manual/plan seam_min_cut_cost=17` | 1.0 | 8.30 |
| `dead_code.py` | `defs_total=1062 started_by_suite=983 dead_candidates=5 dead_candidate_lines=46 dynamic_reach_started_unreferenced=7`, list byte-identical | 1.0 | 12.99 |

`train_mutations.py` was not re-run (≈10 min, and no finding rests on it: step 6 produced
`additions_undetected=0` and no finding).

---

## D7-01 — Active system identification cannot identify the production two-store plant

**Re-run.** `RESULT admitted_cells=0 count` over `cells=24`; `control_admitted=4` of
`control_cells=8`; `aborted_at_production_bound=4`;
`peak_excursion_max_at_production_bound=0.9204 C`. Exact match, `thread_factor=1.0`,
`load1=3.68`.

**My own number.** Harness `d7_01_scope.py`.
*Metric, one line:* **`admitted` = the count of production-reachable house/experiment cells in
which `SystemIdentification.identify()` returns `completed` with `confidence >= 0.3` — the exact
conjunction `_adopt_system_identification` tests — driving the production
`ThermalModel.simulate_step` at 1-minute sub-steps from the plant's own numerically settled
equilibrium.** Three deliberate differences from the finder: (i) the plant is pre-settled by
bisecting the constant electrical power until the 72-hour equilibrium room temperature is
21.00 ± 0.005 °C, so no cell can be blamed on a baseline that was already drifting; (ii) the
sweep is randomized over the whole preset catalogue (4 structures × 5 eras × 2×2 emitters ×
area 70–320 m² × two-zone × upper-area ratio), over `heat_pump_max_power` 3–20 kW — **which is
the excitation, since the step is 0.6·Pmax** — over `T_out` across the whole safe band −5…10 °C,
over the production-reachable `optimization_interval` 10/15/20/30/60/120 min, and over five
noise models (none, σ 0.05, σ 0.10, 0.1 °C quantization, AR(1) φ=0.8); (iii) two-zone and DHW
are varied, which the finder fixes to False.

```
RESULT sweep_cells=300  sweep_admitted=0  sweep_completed=14  sweep_aborted=179
RESULT sweep_admitted_two_zone=0 of 163      sweep_admitted_single_zone=0 of 137
RESULT sweep_admitted_dhw_on=0  of 156       sweep_admitted_dhw_off=0    of 144
RESULT sweep_admitted_cadence_le20=0 of 154  sweep_admitted_cadence_ge60=0 of 99
RESULT sweep_admitted_noise_none=0 of 70     sweep_admitted_noise_any=0  of 230
RESULT sweep_admitted_settled_only=0 of 288  sweep_completed_max_confidence=0.2522
```

**Perturbation, executed independently** (`d7_01_pert.py`, not the finder's control row):
collapse the second store on `typical_slab` (`slab_thermal_mass` 16.5 → 0.5 kWh/°C,
`slab_heat_transfer` 1.5 → 5 kW/°C) and re-run four cells (30/5 min × noiseless/σ 0.05) at the
lifted bound: **`admitted` 0 → 4 of 4**, reason `ok` in all four. At the production 0.8 °C bound
the collapsed plant still aborts (0 of 4). The number moves in the stated direction and is not
computed from constants.

**Attacks.**
- *Is it one captured step response?* No. `d7_01_scope.py --mode axis --bound 10.0` holds the
  preset fixed and moves one axis at a time with the comfort bound lifted, so the fit — not the
  abort — is what is measured: `RESULT axis_cells=35 axis_admitted=0`. Excitation `Pmax`
  2/3/4.5/6/9/12/16/20 kW: 0 admitted. Cadence 10/15/20/30/60/120 min: 0 admitted. Five noise
  models × 3 seeds: 0 admitted. `T_out` −5/−2/0/3/6/10 °C: 0 admitted. The failure survives every
  axis the seat brief names.
- *Settling artefact?* The finder's analytic steady state is off by 0.18 kW on `heavy_old` and
  0.076 kW on `typical_slab` (`RESULT settle_power_gap_heavy_old=0.1805 kW`), but by only
  0.0021 kW on `light_new` — the preset whose 0.92 °C overshoot carries the abort claim. Under my
  bisected equilibrium the residual 2-hour drift is ≤ 0.03 °C, and the result is unchanged.
  Restricting to the 288 of 300 cells that settled cleanly: still 0 admitted.
- *Grid artefact / leave-one-out.* Every marginal cell removed changes nothing: the maximum is 0.
- *Scope, extended in the finding's favour.* Two failure modes the report does not name.
  (a) At `optimization_interval` 60 and 120 min — both inside the config-flow range 10…120 —
  `identify()` returns **"not enough samples"**: the 2 h step + 2 h relax yields fewer than the
  six usable samples the fit requires, so on those installs the experiment cannot ever produce a
  fit, whatever the plant. 51 of my 300 cells fail this way. (b) 14 of 300 cells do return
  `reason == "ok"`, so the report's "0 of 24 completes" is a preset artefact — but their maximum
  confidence is **0.2522**, under the 0.3 gate, and their UA biases run −25.0 % … +64.5 %. The
  operative claim (`_adopt_system_identification` never admits) holds at **0 of 300**.
- *Severity by consequence.* Opt-in (`DEFAULT_SYSID_ENABLED` False), and nothing wrong is
  persisted because nothing is adopted; against that, an enabled install spends 2 h at 0.6·Pmax
  and 2 h with the pump forced off per qualifying night for nothing, and the comfort bound is
  breached before the abort in 179 of 300 cells. Medium is earned.

**Vote: `verify` (medium).** Decisive number: **0 of 300 randomized production-reachable cells
admitted** (0 of 288 among cleanly settled cells), against 4 of 4 once the second store is
collapsed.

*Claim wording to correct:* "completes with a usable fit in 0 of 24 preset cells" is
preset-specific — over a wide sweep `identify()` completes in 14 of 300; what is 0 everywhere is
**admission**. And the report should add the 60/120-minute "not enough samples" mode, which is
production-reachable and independent of the plant.

---

## D7-02 — The defrost flag freezes the COP learner but not the fabric learners

**Re-run.** `ingest_house_loss_defrost=1`, `ingest_lower_floor_loss_defrost=1`,
`ingest_measured_cop_defrost=0`; `defrost_scale_tz_f20=1.041379`, `tz_f50=1.095282`,
null `tz_f00=1.000000`, `sz_f50=1.000000`. Exact match, `thread_factor=1.0`, `load1=9.23`.

**My own number.** Harness `d7_02_scope.py`.
*Metric, one line:* **`ua_overestimate` = `house_heat_loss_scale − 1` after 400 30-minute
intervals in which the plant delivers 75 % of the commanded electrical power on a Bernoulli(f)
fraction of intervals, with the real coordinator's `_async_learn_house_heat_loss` replaying the
real `ThermalModel` each interval — swept over topology.**

```
configuration                 f=0        f=0.2      f=0.5     n(f=.5)
single_zone_dhw_on          1.000000   1.000000   1.000000     400
single_zone_dhw_off         1.000000   1.000000   1.000000     400
two_zone_rad000             1.000000   1.000000   1.000000     400
two_zone_rad020             1.000000   1.021264   1.048926     400
two_zone_rad040 (finder's)  1.000000   1.041379   1.095282     400
two_zone_rad070             1.000000   1.069596   1.160424     400
two_zone_rad100             1.000000   1.095701   1.220811     400
two_zone_valve_manual       1.000000   1.022769   1.050021     400
two_zone_valve_smart_write  1.000000   1.022769   1.050021     400
two_zone_valve_none         1.000000   1.041379   1.095282     400
two_zone_wood_tank          1.000000   1.041379   1.095282     400
two_zone_dhw_wood_coil      1.000000   1.041379   1.095282     400
two_zone_peak_tariff        1.000000   1.041379   1.095282     400
two_zone_interval60         1.000000   1.041379   1.095282     400
RESULT scope_configs=14  scope_configs_biased_at_f50=11  scope_worst_abs_bias_f50=0.220811
```

**Perturbation, executed as a production edit.** I inserted the COP learner's gate
(`in_frost_band(self._current_state.outdoor_temperature)` and
`peek(now).observed/any_defrost → return`) at the top of `_async_learn_house_heat_loss` in
`custom_components/heatpump_optimizer/coordinator.py` and re-ran `learner_gates.py`:
`ingest_house_loss_defrost` **1 → 0**, `defrost_scale_tz_f20` **1.041379 → 1.000000**,
`tz_f50` **1.095282 → 1.000000**. Direction as stated. Edit reverted; tree clean.

**Attacks.**
- *Does the perturbation move for the right reason?* Partly not. Under the same edit
  `defrost_samples_tz_f50` goes **400 → 0**: with no defrost flag configured, `window.observed`
  is False and the whole-band fallback blocks *every* frost-band sample, so the bias goes to zero
  by switching the learner off, not by cleaning it. My `--mode fix` arm separates the two:
  `fix_full_gate_no_flag` scale 1.000000 / **samples 0**; `fix_full_gate_flag_observed` (the
  window actually observed with a 7.5-minute defrost inside each flagged interval, closed each
  cycle as `_record_accuracy` does) scale **1.000000 / samples 217** of 400. So the mechanism is
  genuine when a flag exists; it is a learner-off switch when one does not.
- *Fix scope versus the repo's own gate.* **The stated fix location fails
  `tests/features.py`.** With the gate at the top of the method, `tests/features.py` (run by
  `tests/run.sh`) exits 1 with **4 of 1557 checks failed**: "the fourth trips the detector through
  the real learner", "a tripped detector freezes every learner with reason ventilation", "while
  frozen, cold residuals feed the detector but never the model", "but a third consecutive one is
  a window, not a glitch". The method is what *clears* the ventilation freeze (its own comment at
  `coordinator.py:3216-3221` says so), and an early frost-band return blinds the open-window CUSUM.
  I then moved the identical gate to *after* the `vent_only` return (`coordinator.py:3314`) and
  re-ran: **`ALL 1557 FEATURE CHECKS PASSED`**, with `defrost_scale_tz_f50` still 1.000000. The
  fix is feasible; "at the top of `_async_learn_house_heat_loss`" is not.
- *Scope.* Single zone is an exact null at every f (structurally blind), and so is two-zone with
  `radiator_power_fraction = 0`: the mechanism is the direct radiator share, not "two zone". A
  throttling mixing valve halves it (1.095 → 1.050). The wood tank, the DHW wood coil, the peak
  tariff and a 60-minute optimization interval move it by exactly 0 — the learner never sees
  prices or the horizon. Outdoor temperature barely matters (1.0846 at +12 °C to 1.0986 at −8 °C),
  so the *bias* is not a frost-band phenomenon; only the *gate that would prevent it* is.
- *Null control.* `f = 0` holds at exactly 1.000000 in all 14 configurations.
- *Severity.* The over-estimate is 4.9 %–22.1 % at f = 0.5 depending on radiator share — the
  upper end is more than double what the finding claims — and `house_heat_loss_scale` prices
  every plan. Bounded and self-correcting; medium is earned, not more.

**Vote: `verify` (medium).** Decisive number: **`defrost_scale_tz_f50 − 1` = 0.0953 before the
gate and 0.0000 after it, with 217 of 400 samples retained when a defrost flag exists** — the
hole is real and closable.

*Corrections the finding needs:* (1) the fix scope must say "after the ventilation detector's
feed and the `vent_only` return", not "at the top" — as written it fails `tests/features.py` 4/1557;
(2) the magnitude sentence should name `radiator_power_fraction` as the driver and give the range
0.000–0.221, not the single 0.041/0.095 pair; (3) it should record that on an install with no
defrost flag the gate costs all frost-band house-loss learning (400 → 0 samples).

---

## D7-03 — The accuracy tracker records through open-window and external-heat intervals

**Re-run.** `ingest_accuracy_record_open_window=1`, `…_external_heat=1`,
`…_pump_offline=0`, `…_clean=1`; `learners_ingesting_open_window=1`,
`learners_ingesting_external_heat=1`. Exact match.

**My own number.** Harness `d7_03_scope.py`.
*Metric, one line:* **`recorded` = 1 if `len(AccuracyTracker.samples)` grows when the real
coordinator's `_record_accuracy()` settles one matured prediction under exactly one
contamination — swept over topology.**

```
config                  clean  open_window  external_heat  pump_offline
single_zone                 1            1              1             0
single_zone_dhw             1            1              1             0
two_zone                    1            1              1             0
two_zone_valve              1            1              1             0
two_zone_wood               1            1              1             0
two_zone_peak_tariff        1            1              1             0
interval_60                 1            1              1             0
RESULT acc_configs=7  acc_configs_recording_through_open_window=7  …through_external_heat=7
```

**Perturbation, executed as a production edit.** Guarded the record with
`self._learning_frozen(CONF_INDOOR_TEMP_ENTITY) is None` at `coordinator.py:9297`:
`ingest_accuracy_record_open_window` **1 → 0**, `ingest_accuracy_record_external_heat`
**1 → 0**, `ingest_accuracy_record_clean` stays **1**, `learners_ingesting_open_window` **1 → 0**,
`learners_ingesting_external_heat` **1 → 0**. Reverted.

**Attacks.**
- *Fix scope versus the repo's own gate.* Clean. With the guard in place
  `tests/features.py` → `ALL 1557 FEATURE CHECKS PASSED` (exit 0) and `tests/entities.py` →
  `ALL 538 ENTITY CHECKS PASSED` (exit 0). The proposed predicate is not algebraically the
  shipping code either: the shipping condition is `self._pump_signals.freeze_reason is None`,
  which my sweep shows is a strictly different predicate (it fires on `pump_offline` and not on
  the other two, in 7 of 7 configurations).
- *Does the fix switch the tracker off?* No — the clean arm stays 1, so it is not the degenerate
  kind of "to_zero".
- *Scope.* Configuration-independent by construction and by measurement: identical in 7 of 7
  topologies including single/two zone, DHW, mixing valve, wood tank, peak tariff and a 60-minute
  interval. Nothing here is horizon-sensitive.
- *Severity by consequence.* `_confidence_margins` is opt-in and capped by
  `CONFIDENCE_MARGIN_CAP_C`, and the rollback decision is separately gated by `_inputs_healthy`.
  Low is right.

**Vote: `verify` (low).** Decisive number: **7 of 7 configurations record through an open window
and through external heat; 0 of 7 after the one-line guard, with the clean arm still recording.**

---

## D7-04 — `last_buffer_trajectory` is a 5 SEK side channel with one poison

**Re-run.** `tc_production=15.305845`, `tc_delta_abs_max=5.416717 SEK`,
`tc_delta_rel_to_energy=0.070771`, `null_delta_abs=0.000000`, `poison_raises=1`,
`writer_sites=3`, `reader_sites_optimizer=4`, `readers_with_model_call_between=0`. Exact.

**My own number.** Harness `d7_04_scope.py`.
*Metric, one line:* **`stale_share` = max over three intervening schedules of |terminal cost
computed on schedule A's returned trajectories with the buffer trajectory read after one
intervening `simulate_trajectory` − the same cost read in the production order| ÷ A's own energy
cost, per configuration and per price profile.**

```
case                            store  energy SEK   tc SEK  abs SEK    rel  poison
tz_manual_200L_24h_wintyp (finder)  1       76.54   15.306   5.4167  0.0708      1
tz_manual_200L_24h_FLAT             1       86.40   22.818  10.3756  0.1201      1
tz_manual_200L_48h_wintyp           1      153.08   17.223   6.2225  0.0406      1
tz_manual_200L_24h_winextr          1      135.68   10.793  11.4233  0.0842      1
tz_manual_200L_24h_summneg          1        7.88    9.533   2.7872  0.3536      1
tz_smartwrite / tz_smartread        1       76.54   15.306   5.4167  0.0708      1
tz_valve_none_200L_24h              0       76.54    3.997   0.0000  0.0000      1
tz_manual_35L_24h                   0       76.54   14.146   0.0000  0.0000      1
tz_manual_500L_24h                  1       76.54   24.008  16.0926  0.2103      1
tz_manual_200L_DHW_24h              1       76.54   15.306   5.4167  0.0708      1
sz_manual_200L_24h                  1       76.54    0.000   0.0000  0.0000      1
sz_manual_200L_DHW_24h              1       76.54    0.000   0.0000  0.0000      1
tz_manual_wood_24h                  1       76.54   15.306   5.4167  0.0708      1
tz_manual_peaktariff_24h            1       76.54   15.306   5.4167  0.0708      1
RESULT cases=15  cases_buffer_is_store=13  cases_with_nonzero_delta=11
RESULT worst_abs_delta=16.092613 SEK  worst_rel_delta=0.353650  flat_price_abs_delta=10.375625 SEK
```

**Perturbation.** `mixing_valve_mode → none`: `tc_delta_abs_max` **5.4167 → 0.000000 SEK**
(`buffer_is_store` False). Reproduced in the finder's harness and independently in mine
(`tz_valve_none_200L_24h abs=0.0000`), and a second null appears at the 35 L default volume.
The number moves; it is not a constant.

**Attacks.**
- *Flat-price null.* The delta does **not** vanish at flat prices — it grows to 10.38 SEK
  (12.0 % of energy). So the hazard is arithmetic in the terminal-cost term, not a price artefact.
  (This is a hazard, not a claimed gain, so the flat control is a robustness check rather than a
  disqualifier.)
- *Scope — the finding is narrower than "a store configuration".* Two of my 13 cases with
  `buffer_is_store == True` give **exactly 0.000000**: both single-zone. Single zone has no valve
  branch, the buffer trajectory never moves, and the terminal cost itself is 0.000. The hazard
  needs *two-zone* **and** a throttling valve **and** volume ≥ `BUFFER_STORE_MIN_VOLUME`, not
  `buffer_is_store` alone.
- *Scope — the finding is weaker than the true worst case.* 5.42 SEK is the finder's one cell.
  A 500 L tank gives **16.09 SEK (21.0 %)** and `summer_negative` gives **35.4 % of energy cost**.
  A 48-hour horizon gives 6.22 SEK (4.1 %). DHW on/off, the wood tank and the peak tariff move it
  by exactly 0.
- *Fix scope.* Understated by an order of magnitude. "Return the buffer trajectory from
  `simulate_trajectory`/`_with_dhw` … and delete the attribute" touches 4 production unpack sites
  — but also **11 test unpack sites**, and there are **28 reads of `last_buffer_trajectory` in
  `tests/`** against 4 in production. Changing the return arity therefore breaks
  `tests/features.py`/`tests/golden.py`, the repo's own gate. Worse, the same expression writes two
  sibling side channels with the identical hazard — `last_buffer_refused` (1 production read,
  7 test reads) and `last_wood_trajectory` (2 production reads, 19 test reads) — which "delete the
  attribute" leaves in place. The code comment the fix quotes ("nine call sites unpack a
  four-tuple") is wrong in both directions: 4 in production, 24 in total.
- *Live defect?* None. `readers_with_model_call_between=0` reproduces; today every reader is
  adjacent to its writer, and the batch path poisons (`poison_raises=1` in all 15 of my cases,
  including the nulls).

**Vote: `verify` (low).** Decisive number: **worst stale delta 16.09 SEK = 21.0 % of the
schedule's energy cost** (finder: 5.42 SEK / 7.1 %), against **0.000000 in every single-zone and
every non-store configuration**.

*Title to correct:* "a 5 SEK side channel" is one cell of a 0–16 SEK range; and the qualifier
should be "on a two-zone store configuration", since single-zone `buffer_is_store` installs are
an exact null.

---

## D7-05 — `coordinator.py` has one cheap seam and no others

**Re-run.** `n_methods=256`, `n_attrs=179`, `n_attrs_multi_writer=132`,
`cross_attr_fraction_seeded=0.3091`, `cross_call_fraction_seeded=0.6609`,
`cross_attr_fraction_k10=0.33`, `seam_min_cut_name=manual/plan`, `seam_min_cut_cost=17`,
`attr_max_fan_in=77`, `attrs_fan_in_ge_20=6`. Exact match. `metrics_ast.py` likewise.

**My own numbers.** Two independent tools, neither the finder's script.
*Metric A, one line:* **class size measured by plain text: lines from the `class` line to EOF,
methods = lines matching `^    (async )?def `, instance attributes = distinct `self.<name>` on the
left of an assignment.** Result: **10,269 class lines / 256 methods / 174 attributes** — identical
to the finder's AST figures.
*Metric B, one line:* **multi-writer attribute = a `self.<name>` that appears in `Store`/`Del`
context inside more than one method of the class, method names excluded.** Result: **132 of 174** —
identical.

*Metric C (the one that matters here), one line:* **`cross_attr_fraction_k10` recomputed with the
finder's own `spectral()`/`fractions()` over `kmeans2` seeds 0…9 and k ∈ {6,8,10,12,16}, and after
deleting the 10 manual/plan methods versus after deleting 10 random methods (20 draws).**

```
RESULT base_cross_attr_k10=0.3300     (seed 0, the harness's seed)
seeds 0..9 at k=10: 0.3300 0.3443 0.3871 0.4002 0.3907 0.3228 0.3633 0.3967 0.3508 0.3401
RESULT seed_spread_k10=0.0774
RESULT seam_removed_cross_attr_k10=0.3830      RESULT seam_move=+0.0530
RESULT random10_mean_cross_attr_k10=0.3772     RESULT random10_mean_move=+0.0472
RESULT random10_min=0.3382  random10_max=0.4044  RESULT seam_move_z=+0.35 sigma
RESULT min_cross_attr_any_k_any_seed=0.2138 (k=6 seed=4)
RESULT k_seed_cells_with_cross_attr_below_0p33=6 of 50
```

**Perturbation, executed.** I deleted the ten manual/plan methods from a copy of
`coordinator.py` (AST-exact excision, file still parses, 10,902 → 10,749 lines) and re-ran
`coordinator_clusters.py` against that tree:

```
n_methods                   256 -> 246     (down, as stated)
cross_attr_fraction_k10     0.33 -> 0.3851 (UP; the finding states "down")
cross_attr_fraction_seeded  0.3091 -> 0.3111 (up)
seam_min_cut_name           manual/plan -> dhw/heat, seam_min_cut_cost 17 -> 173
```

**Attacks.**
- *The perturbation's discriminating half fails.* `n_methods` moving 256 → 246 is arithmetic —
  delete ten methods, the count drops by ten — and tests nothing about the metric. The half that
  would have tested it, `cross_attr_fraction_k10` **down**, moves **up** by +0.0530. And it is not
  even attributable to the seam: deleting 10 *random* methods moves the same number up by
  **+0.0472** on average (20 draws), putting the seam's move at **+0.35 σ** of the control
  distribution. The metric is responding to the method set shrinking under a fixed k, not to the
  seam's coupling.
- *Metric instability.* At k=10 alone the `kmeans2` seed moves `cross_attr_fraction` over
  0.3228…0.4002, a spread of **0.0774** — more than twice the 0.055 the perturbation produced.
  The reported 0.33 is one draw from that distribution, and the finder's expected value is quoted
  to four decimals.
- *A stated claim is false as written.* "no clustering at k = 6…16 pushes cross-cluster attribute
  references below 0.33": **6 of 50 (k, seed) cells are below 0.33, minimum 0.2138** at k=6 seed 4.
  In fairness that partition is degenerate — 109 + 89 of 256 methods in two clusters — so the
  qualitative reading ("the class does not fall apart into low-coupling pieces") survives; the
  numeric claim does not, and the harness has no guard against a coarse partition scoring well.
- *A second stated claim is contradicted by the finder's own table.* "the only seam with cut cost
  under 40 is the manual-plan group": the same k=10 table lists **`dhw/profile` at cut 38**, also
  under 40. Two seams, not one. Across seeds the cheapest ≥8-method cluster is the manual/plan
  group in only **20 of 50** (k, seed) cells, and its cut ranges 17…50.
- *What survives.* The size and shape numbers, which I reproduced with two independent tools:
  10,269 class lines, 256 methods, 174 attributes, 132 of them written from more than one method,
  six attributes with fan-in ≥ 20, `max_cc = 86`, an acyclic import graph. Those are exact and they
  carry the finding's real content.

**Vote: `weaken(low)`.** Severity stays at the floor, but three numbers must be struck: the
"under 0.33" threshold (falsified at 0.2138), "the only seam under 40" (`dhw/profile` is 38), and
the perturbation's stated direction (measured **up** +0.0530, indistinguishable from a
random-10-method deletion at +0.35 σ). Decisive number: **`cross_attr_fraction_k10` 0.33 → 0.3851
under the finding's own perturbation, against a random-deletion control of 0.3772**. The finding
should be restated on the counts alone: *the coordinator class is 10,269 lines with 132
multi-writer attributes and six hub attributes of fan-in ≥ 20; the manual-plan group is the one
cluster whose cut cost is 17.*

---

## D7-06 — Five dead defs and six production functions only tests call

**Re-run.** `defs_total=1062`, `started_by_suite=983`, `dead_candidates=5`,
`dead_candidate_lines=46`, `dynamic_reach_started_unreferenced=7`,
`referenced_never_started=63`; `dead_candidate_list` byte-identical. `thread_factor=1.0`,
`load1=12.99`.

**My own number.** No AST at all — a plain identifier census.
*Metric, one line:* **for each listed def, the number of occurrences of its bare identifier
anywhere under `custom_components/` and `tests/` other than its own definition line.**

```
ComfortLearner.set_configured        0
config_flow._translated_text         0
coordinator.optimization_result      0
coordinator.current_state            0
presets._floor_heated_area           0
```

All five appear exactly once in the tree — their own `def`. The dead-5 half verifies under a
completely different tool.

**Perturbation, executed.** Deleted `presets._floor_heated_area` (lines 162–177) from production
and re-ran `dead_code.py` on the modified tree:

```
dead_candidates       5 -> 4        dead_candidate_lines  46 -> 30
defs_total         1062 -> 1061     started_by_suite      983 -> 983 (unchanged, as stated)
dead_candidate_list  the remaining four, unchanged
```

and the suite still passes: `tests/features.py` → `ALL 1557 FEATURE CHECKS PASSED` (exit 0),
`tests/entities.py` → `ALL 538 ENTITY CHECKS PASSED` (exit 0), `tests/closure.py no-copies` → ok.
Both halves of the stated perturbation hold. `presets.py` reverted.

**Attacks — and the second half of the claim does not hold.**
- **`grid_fee.max_abs_component` is live production code, not test-only.**
  `coordinator.py:351` imports it as
  `max_abs_component as grid_fee_max_abs_component`, `coordinator.py:6217` calls it inside
  `_audit_grid_fee`, and `_audit_grid_fee` is called from `_fee_series` at
  `coordinator.py:6199`. So of the six "production defs only tests call", one is called on the
  production fee path every solve. **6 → 5**, and 140 lines → 114.
- *Same blind spot, second instance.* The report records `topology.match_layout` as "tests refs 0",
  but `tests/features.py:6013` imports it as `match_layout as _match_layout` and calls it at
  6039, 6050, 6071, 6079, 6092 and 6227. Its classification (started, production never references
  it) is right; its evidence figure is wrong.
- *Root cause.* Both errors are the same harness gap: `import X as Y` is counted as a reference to
  `X`'s name only at the alias node, and the uses — which are spelled `Y` — are never connected
  back. Nothing else in the census is affected: I re-checked the other five and
  `pv.piecewise_cost`'s two production hits are `#` comments, not code.
- *Scope.* A static/runtime census over the whole package; single- versus two-zone, DHW, valve,
  wood, tariff and horizon cannot move it, and I did not pretend otherwise.
- *Severity.* Hygiene, 46 lines. Low.

**Vote: `weaken(low)`.** The dead-5 half verifies exactly and its perturbation lands
(5 → 4, suite green). The second half must be corrected from six to **five**, with
`grid_fee.max_abs_component` removed from the list, and the `topology.match_layout` "tests refs 0"
figure corrected. Decisive number: **`grid_fee_max_abs_component` is called at
`coordinator.py:6217` from `_audit_grid_fee`, itself called at `coordinator.py:6199` — a
production call path, so the "6 production defs only tests call" is 5.**

---

## Summary of executed perturbations

| finding | stated direction | executed result | moves? |
|---|---|---|---|
| D7-01 | `admitted_cells` up | 0 → 4 of 4 (independent re-implementation) | yes |
| D7-02 | `defrost_scale_tz_f50 − 1` to zero | 0.0953 → 0.0000 (production edit) | yes |
| D7-03 | both ingests to zero | 1 → 0 and 1 → 0, clean arm still 1 (production edit) | yes |
| D7-04 | `tc_delta_abs_max` to zero | 5.4167 → 0.000000 SEK | yes |
| D7-05 | `n_methods` down, `cross_attr_k10` down | 256 → 246 (arithmetic); **0.33 → 0.3851, up** | half fails |
| D7-06 | `dead_candidates` down by 1, suite passes | 5 → 4, features 1557/1557, entities 538/538 | yes |

Nothing here is computed from constants; no harness is void. Two fix scopes fail on execution
(D7-02 at the stated location: `tests/features.py` 4/1557; D7-04's return-arity change: 11 test
unpack sites and 28 test reads it does not mention) and one finding's own perturbation
contradicts it (D7-05).
