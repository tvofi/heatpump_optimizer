# D7 — Architecture and maintainability (round 2)

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884` (VERSION 6.2.14), export
`/Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-baseline`, no `.git`.
Machine: 8-core Apple M1, 8 GB, shared with ten other auditors (`load1` 8–73 during the
runs). Every number below is a count, a ratio or a deterministic simulation value; none
is a timing, so none is provisional. Exposure: none (no `docs/` read beyond a grep for the
doc-anchor counts in step 6; `docs/plan-card-decomposition.md` was not opened).

Interpreter and invocation for every harness, from the export root:

```
PYTHONPATH=tests/hastub /Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/tvofi-claude/.venv/bin/python tools/audit/round2/D7/<harness>.py
```

## Method

The brief's seven steps, one harness each, all under `tools/audit/round2/D7/`:

| step | harness | what it drives |
|---|---|---|
| 1 metrics | `metrics_ast.py` | AST of every module: lines, classes, methods, instance attributes and multi-writer attributes, McCabe CC per function, intra-package import graph and its SCCs |
| 2 coordinator seams | `coordinator_clusters.py` | method–attribute bipartite graph of `HeatPumpOptimizerCoordinator`; seeded (greedy, `_init_*` homes) and spectral (k-means++ on the normalized-Laplacian embedding, seed 0) clusterings; cross-cluster attribute/call fractions; cut cost per cluster |
| 3 sysid plant | `sysid_plant.py` | production `SystemIdentification.step/identify` in closed loop against production `ThermalModel.simulate_step` for the three `tests/stress.py` presets, plus a first-order positive control; two-store least-squares comparison fit |
| 4 learner gates | `learner_gates.py` | (A) AST gate table per learner; (B) a real coordinator, one contamination injected, each learner's own counter; (C) the defrost mechanism's magnitude with the real learner and real model |
| 5 `last_buffer_trajectory` | `trajectory_order.py` | the `_terminal_cost` closure on schedule A's returned trajectories with the side channel read before / after an intervening simulation / after a batch; AST census of writers and readers |
| 6 this year's train | `train_mutations.py` | one textual deletion per addition on a tree copy, the gate scripts run there, detection = exit status or `FAIL`/`DIFF` count rising above the unmutated copy's |
| 7 dead code | `dead_code.py` + `d7_monitor_boot.py` | AST reference census (names, attributes, non-docstring string tokens) joined with a `sys.monitoring` PY_START sentinel over the gate's Python scripts |

Spot mutations and the monitored suite run on `shutil.copytree` copies under a private temp
root carrying a one-line stub `RELEASE_NOTES.md` (the export omits it and
`tests/entities.py:4360` aborts without it). Nothing under `custom_components/` or `tests/`
in the export was edited.

## Step 1 — metrics (`metrics_ast.py`)

```
RESULT total_lines=37843            RESULT modules=45
RESULT coordinator_lines=10902      RESULT coordinator_share_of_package_lines=0.2881
RESULT coordinator_methods=256      RESULT coordinator_instance_attrs=174
RESULT coordinator_instance_attrs_multi_writer=132
RESULT functions_total=1062  functions_cc_gt_10=83  functions_cc_gt_20=16  functions_cc_gt_30=5  max_cc=86
RESULT import_edges_module_level=87  import_edges_deferred=2  import_cycle_sccs_module_level=0  import_cycle_sccs_with_deferred=0
```

Top complexity: `HeatPumpOptimizer.optimize` CC 86 (540 lines), `_build_dhw_requirements`
CC 49 (625 lines), `ThermalModel.simulate_trajectory_batch` CC 44 (378 lines),
`HeatPumpOptimizerCoordinator._update_current_state` CC 35 (266 lines),
`HeatPumpOptimizer.get_current_action` CC 34, `async_run_optimization` CC 28. The
coordinator class alone is 10,269 lines; the next largest class (`HeatPumpOptimizer`) is
4,591 lines with 7 instance attributes. The import graph is acyclic even counting the two
function-level imports (`grid_fee`→`const`, `thermal_model`→`const`).

## Step 2 — coordinator seams (`coordinator_clusters.py`)

256 methods, 179 distinct `self.<attr>` names, 132 written in more than one method,
1,679 attribute references, 407 self-calls, 14 stateless methods.

Seeded by the `__init__`/`_init_*` homes (9 clusters): cross-cluster attribute references
**0.309**, cross-cluster calls **0.661**. Cut costs (shared attrs + crossing calls):
`_init_ecl110` 15 (4 methods), `_init_measurements` 48 (11), `_init_insurance` 67 (13),
`_init_grid` 91 (32), `__init__` 96 (41), `_init_features` 100 (37), `_init_model` 114
(29), `_init_dhw_learning` 116 (35), `_init_runtime_state` 157 (54).

Spectral, k = 10: cross-attr **0.330**, cross-call **0.752** (k=6 0.368/0.722, k=8
0.357/0.705, k=12 0.390/0.784, k=16 0.418/0.848 — the class does not fall apart into
low-coupling pieces at any k). Seam candidates (≥ 8 methods) by cut cost per method:

| seam (token name) | methods | lines | owned attrs | shared attrs | crossing calls | cut | cut/method |
|---|---|---|---|---|---|---|---|
| manual/plan | 10 | 152 | 3 | 6 | 11 | 17 | 1.70 |
| price/setup (the `__init__`… bulk) | 76 | 2681 | 48 | 94 | 151 | 245 | 3.22 |
| dhw/heat (`_init_model`… bulk) | 67 | 3075 | 43 | 85 | 135 | 220 | 3.28 |
| month/load (grid, price model, ledger, freq) | 15 | 464 | 14 | 34 | 24 | 58 | 3.87 |
| fetch/weather | 10 | 159 | 6 | 18 | 24 | 42 | 4.20 |
| dhw/profile | 9 | 322 | 9 | 14 | 24 | 38 | 4.22 |
| dhw/save (`_init_features` group) | 28 | 1296 | 24 | 53 | 87 | 140 | 5.00 |
| dhw/legionella | 9 | 505 | 11 | 35 | 28 | 63 | 7.00 |
| learning/load (thermal-learning persistence) | 9 | 454 | 17 | 42 | 29 | 71 | 7.89 |
| prices/price (solve entry) | 9 | 554 | 4 | 23 | 49 | 72 | 8.00 |

The attributes every seam would have to share: `self._config` (77 methods),
`self._thermal_params` (63), `self.hass` (42), `self._current_state` (36),
`self._opt_config` (32), `self._current_action` (23) — six attributes with fan-in ≥ 20.
Full membership and per-cluster shared-attribute names are in
`coordinator_clusters.json`.

Reading for the decomposition program: the one cheap cut is the manual-plan group (6
attributes, 11 calls); every other seam pays 40–250 in shared state and calls, and the
two 60–80-method blobs are not separable by shared state at all — they are separable
only by the six hub attributes, which is a "pass the context object" refactor, not a
"move a cluster" one.

## Step 3 — the first-order sysid plant (`sysid_plant.py`)

Plant: production `ThermalModel` (single zone; room store C_room, slab store C_slab
coupled by k) for the three `tests/stress.py` presets derived through
`presets.derive`; the production `SystemIdentification` state machine armed at 23:00 at
T_out 0 °C, cheap price, pump at the steady-state power until the machine overrides it,
plant stepped at 1-minute sub-steps. 24 preset cells = 3 presets × {30-min production
cycle, 5-min} × {noiseless, σ 0.05 °C} × {production bound 0.8 °C, bound lifted to 10 °C}.

| preset | UA kW/°C | C_room | C_slab | k | outcome at the production bound, 30 min | any cell with a usable fit |
|---|---|---|---|---|---|---|
| light_new | 0.0660 | 3.60 | 0.24 | 0.24 | **aborted** (room drifted 0.92 °C past the 0.8 °C bound before the sample-instant check) | no: lifted bound → "fit gave implausible signs", peak excursion 4.1 °C |
| heavy_old | 0.3100 | 11.0 | 23.0 | 2.0 | done, "fitted gains outside plausible bounds" | no |
| typical_slab | 0.1725 | 5.25 | 16.5 | 1.5 | done, "fit gave implausible signs" | no |

```
RESULT cells=24  RESULT admitted_cells=0  RESULT aborted_at_production_bound=4
RESULT peak_excursion_max_at_production_bound=0.9204 C
RESULT control_cells=8  RESULT control_admitted=4  RESULT control_abs_bias_pct_max=8.056
```

Positive control (typical_slab with C_slab 0.5, k 5 — a 6-minute lag, first-order to
within the sampling): `identify()` completes with "ok", confidence 0.34–0.93, UA bias
−3.5 … −8.1 %, and the adoption gate admits all four lifted-bound cells; at the
production bound the control aborts too (peak 1.10 °C at 30 min: the excursion is
checked only at sample instants, so at the production cycle the room overshoots the
bound by up to 0.3 °C before the abort). The two-store least-squares fit of the same
samples recovers UA within 0.0/5.9/6.4 % (light/heavy/typical, noiseless, 30 min) — the
data identify the plant; the first-order regression does not. Mechanism: with the
step's heat entering the slab store, the room rate in RELAX stays positive at zero
input, and the regression `rate = −(UA/C)ΔT + Q/C + G/C` resolves that as a wrong-signed
UA/C or an intercept outside the ±0.5…2 kW gains band.

## Step 4 — learner freeze versus COP flow (`learner_gates.py`)

(A) AST gate table (D direct, T through `_learning_frozen` / a gated caller /
`_interval_space_power`, – none) for the 22 learner-ish methods: every thermal learner
is covered for open window, pump signals and external heat through `_learning_frozen`;
**defrost** is consulted directly only by `_learn_measured_cop` and `_settle_defrost`
(15 of 22 methods have no defrost gate, including both fabric learners); **away** only by
`_track_curve_comfort`.

(B) Runtime, one contamination per arm, 1 = the learner's counter advanced:

| learner | clean | open window | pump offline | external heat | defrost | away |
|---|---|---|---|---|---|---|
| house_loss | 1 | 0 | 0 | 0 | **1** | 1 |
| lower_floor_loss | 1 | 0 | 0 | 0 | **1** | 1 |
| measured_cop | 1 | 0 | 0 | 0 | 0 | 0 |
| buffer_cooling | 1 | 0 | 0 | 0 | 1 | 1 |
| dhw_cooling | 1 | 0 | 0 | 0 | 1 | 1 |
| dhw_usage | 1 | 0 | 0 | 0 | 1 | 1 |
| accuracy_record | 1 | **1** | 0 | **1** | 1 | 1 |
| curve_comfort | 1 | 0 | 0 | 0 | 1 | 0 |

(Away and defrost do not contaminate tank-cooling or DHW-usage physics, and away is
deliberately only a comfort-evidence gate; those 1s are not defects.)

(C) Magnitude of the defrost gap, real learner replaying the real model against a plant
that delivers 75 % of the command on a fraction f of 30-min intervals, 400 intervals:

```
RESULT defrost_scale_sz_f00=1.000000  sz_f20=1.000000  sz_f50=1.000000   (single zone: structurally blind)
RESULT defrost_scale_tz_f00=1.000000  tz_f20=1.041379  tz_f50=1.095282   (two zone, radiator share 0.4)
```

Single zone is blind because every watt passes the slab store and the explicit-Euler
room update reads the previous slab temperature, so a one-step replay cannot see a
delivered-power error in the room; two zone routes the radiator share straight into the
upper zone and the shortfall lands in the residual. f = 0 is the null and holds exactly.

## Step 5 — `last_buffer_trajectory` (`trajectory_order.py`)

Two-zone house, `mixing_valve_mode` manual, 200 L tank (`buffer_is_store` True); schedule
A = the smooth price guess; terminal cost = the `_terminal_cost` closure on A's four
returned trajectories.

```
RESULT tc_production=15.305845 SEK           (A energy cost 76.54 SEK)
RESULT tc_delta_after_coast=+5.416717 SEK    tc_delta_after_full=-5.195302   tc_delta_after_random=-0.649172
RESULT tc_delta_abs_max=5.416717 SEK         tc_delta_rel_to_energy=0.070771
RESULT null_delta_abs=0.000000 SEK           (no valve: buffer_is_store False)
RESULT poison_raises=1                       (after simulate_trajectory_batch the read raises)
RESULT writer_sites=3  reader_sites_optimizer=4  readers_with_model_call_between=0  reader_max_line_distance=51
```

Call order the production objective relies on: `simulate_trajectory` (writes the
attribute) → `terminal_cost(..., self.model.last_buffer_trajectory)` in the same
expression, at `optimizer.py:2721→2772` and `4564→4615`; the assembly reads at
`2875→2891` and `4755→4774` are likewise adjacent with no model call between. So
today no reader is stale. The hazard is the size of the number if one ever is: one
intervening simulation of a different schedule moves the terminal cost by up to
5.42 SEK (7.1 % of the schedule's energy cost) with no error, and only the batch path
carries a poison. The single-zone / no-valve configuration is a genuine null (0.000000).

## Step 6 — this year's train (`train_mutations.py`)

One textual deletion per addition on a tree copy; detection = a gate script's exit status or its
`FAIL`/`DIFF` count rising above the unmutated copy's. Unmutated copy: `features.py` exit 0 / 0 fail lines, `entities.py` exit 0 / 0 fail lines, `golden.py` exit 1 / 34 fail lines, `plan_view.py` exit 0 / 0 fail lines, `card.mjs` exit 0 / 0 fail lines, `frontend.py` exit 0 / 0 fail lines. (`golden.py` shows 34/55 `DIFF` at baseline on this box — the fixtures were recorded elsewhere — and the
count never rose for any mutant: the wood/coil/valve scenarios that would move are already among the 34, so
the golden net adds nothing here; `features.py` carried every detection.)

| addition | owning module | deleted symbol | detected | docs files | features.py exit/FAIL | other scripts |
|---|---|---|---|---|---|---|
| batched gradient (#97) and its bounds gate (D9-01) | `optimizer.py` | `optimizer:_bounds_supported_by_batch` | **1** | 1 | 1/2 | entities.py=0/0 golden.py=1/34 |
| the bounds gate's zero-range carve-out (D9-01) | `optimizer.py` | `optimizer:_bounds_supported_by_batch` | **1** | 0 | 1/2 | entities.py=0/0 golden.py=1/34 |
| the drift detector primitive (drift.py Cusum, T4a) behind the open-window, COP-health and drift gates | `drift.py` | `drift:Cusum.update` | **1** | 4 | 1/8 | entities.py=0/0 golden.py=1/34 |
| weekly DHW windows (weekdays/weekend selectors) | `dhw_schedule.py` | `dhw_schedule:windows_for_day` | **1** | 5 | 1/3 | entities.py=0/0 golden.py=1/34 |
| the topology catalogue (topology.py LAYOUTS / match_layout) | `topology.py` | `topology:match_layout` | **1** | 6 | 1/3 | entities.py=0/0 golden.py=1/34 |
| the wood two-tank variant (thermal_model.wood_share priority law, #40) | `thermal_model.py` | `thermal_model:wood_share` | **1** | 6 | 1/5 | entities.py=0/0 golden.py=1/34 |
| the DHW wood-coil variant (thermal_model.dhw_coil_draw_reduction, v3.15.1) | `thermal_model.py` | `thermal_model:dhw_coil_draw_reduction` | **1** | 5 | 1/5 | entities.py=0/0 golden.py=1/34 |
| the DHW confidence band (v5.2.0, coordinator._dhw_confidence_band) | `coordinator.py` | `coordinator:HeatPumpOptimizerCoordinator._dhw_confidence_band` | **1** | 1 | 1/1 | entities.py=0/0 golden.py=1/34 |
| the Tuya heat-pump signals (v5.3.0 pump_signals.read: the offline/fault/cooling learner freeze) | `pump_signals.py` | `pump_signals:read` | **1** | 1 | 1/12 | entities.py=0/0 golden.py=1/34 |
| the re-anchor law (#86, coordinator._reanchor_house_heat_loss_scale) | `coordinator.py` | `coordinator:HeatPumpOptimizerCoordinator._reanchor_house_heat_loss_scale` | **1** | 2 | 1/7 | entities.py=0/0 golden.py=1/34 |
| the card collaborators (PR 5b LaneEditor of the decomposition program, #136) | `www/heatpump-optimizer-card.js` | `heatpump-optimizer-card.js:LaneEditor` | **1** | 1 | — | plan_view.py=0/0 card.mjs=1/0 frontend.py=0/0 |
| the drift gate (tests/env_drift.py, CI GOLDEN_MODE=drift) | `tests/env_drift.py` | — | n/a | 2 | — | needs `git worktree add`: not executable in a git-less export; no test tests the gate |
| the scoped gate (tests/run.sh GATE_SCOPE=auto, tests/closure.py, closures.json) | `tests/closure.py` | — | n/a | 3 | — | probed below: `closure.py select` with and without closures.json |
| the stress solve-time budgets (tests/stress.py Calibration / SOLVE_BUDGET_RATIO) | `tests/stress.py` | — | n/a | 2 | — | a timing guard; needs the quiet box and runs alone -- not mutated here |

Scoped-gate probe (`closure.py select --files custom_components/heatpump_optimizer/optimizer.py`): with
`closures.json`: `MODE: SCOPED -- 14 script(s) run, 2 scoped out.`; without it: `MODE: FULL -- every test script runs, nothing is scoped out.`.

```
RESULT additions_mutated=11  additions_detected=11  additions_undetected=0  additions_without_doc_file=1
```

Every production-side addition has a test that fails when it is deleted, one owning module, and — except the
bounds gate's zero-range carve-out, which is documented only in its docstring — at least one `docs/` file that
mentions it. The three gate-side additions (drift gate, scoped gate, stress budgets) are not testable by deletion
here: the drift gate needs `git worktree`, the budgets need the quiet box, and the scoped gate was probed instead
of mutated. No test tests a gate; that is by construction, not a finding.

## Step 7 — dead code (`dead_code.py` + `d7_monitor_boot.py`)

Runtime sentinel: the gate's thirteen Python scripts under `sys.monitoring` PY_START in a tree copy:

| script | exit | code objects started |
|---|---|---|
| `tests/features.py` | 0 | 824 |
| `tests/entities.py` | 0 | 740 |
| `tests/golden.py` | 0 | 511 |
| `tests/backtest.py` | 0 | 214 |
| `tests/optimality.py` | 0 | 249 |
| `tests/validate.py` | 0 | 257 |
| `tests/edge.py` | 0 | 258 |
| `tests/manual_plan.py` | 0 | 299 |
| `tests/open_meteo.py` | 0 | 18 |
| `tests/solar_alignment.py` | 0 | 138 |
| `tests/plan_view.py` | 0 | 255 |
| `tests/frontend.py` | 0 | 3 |
| `tests/dst_checks.py` | 0 | 230 |

```
RESULT defs_total=1062  started_by_suite=983  static_unreferenced_prod=63
RESULT dead_candidates=5  dead_candidate_lines=46  dynamic_reach_started_unreferenced=7  referenced_never_started=63
```

Dead candidates (never started, unreferenced in production and in tests, not a framework hook):

- `comfort_learning.py:ComfortLearner.set_configured:180` (6 lines)
- `config_flow.py:_translated_text:890` (19 lines)
- `coordinator.py:HeatPumpOptimizerCoordinator.optimization_result:1253` (3 lines, @property)
- `coordinator.py:HeatPumpOptimizerCoordinator.current_state:1363` (2 lines, @property)
- `presets.py:_floor_heated_area:162` (16 lines)

Started at runtime but statically unreferenced in production (the sentinel's job — reached only through a
dynamic lookup or through tests):

- `coordinator.py:HeatPumpOptimizerCoordinator._async_update_data:4342` (107 lines) — HA `DataUpdateCoordinator` hook
- `coordinator.py:HeatPumpOptimizerCoordinator._prepare_forecast_data:5705` (5 lines) — test-only reach (tests refs 6)
- `dhw_draws.py:DrawStats.ready_energy:108` (14 lines) — test-only reach (tests refs 3)
- `grid_fee.py:max_abs_component:282` (26 lines) — test-only reach (tests refs 1)
- `pv.py:piecewise_cost:104` (18 lines) — test-only reach (tests refs 4)
- `tariff.py:peak_penalty:439` (23 lines) — test-only reach (tests refs 4)
- `topology.py:match_layout:328` (54 lines) — test-only reach (tests refs 0)

63 defs are referenced by production but never started by the suite (uncovered, not dead;
40 of them in `coordinator.py`, 8 in `open_meteo.py`) — coverage, not this dimension.

## Findings

### D7-01 — Active system identification cannot identify the production plant (bug, medium)

**Claim.** `SystemIdentification.identify()` returns no usable result for any of the three
building presets driven against the production `ThermalModel`: 0 of 24 cells completes
with `reason == "ok"`, so `_adopt_system_identification` never admits anything; a
first-order control plant (C_slab 0.5, k 5) is admitted in 4 of 8 cells with −3.5…−8.1 %
UA bias, so the harness can pass and the plant's second store is the cause.

**Evidence.** `sysid_plant.py`: `RESULT admitted_cells=0 count` over `cells=24`;
`control_admitted=4` of `control_cells=8`; `aborted_at_production_bound=4` (the light
house, 0.92 °C past a 0.8 °C bound); two-store fit recovers UA to 0.0/5.9/6.4 %.
Leave-one-out over the 24 cells: admitted min 0, max 0, drop-most-favourable 0.

**Mechanism.** The step's heat enters the slab store; in RELAX the room rate stays
positive at zero input, and the first-order regression `rate = −(UA/C)ΔT + Q/C + G/C`
resolves that as a wrong-signed coefficient ("fit gave implausible signs") or an
intercept outside the −0.5…2 kW gains band ("fitted gains outside plausible bounds").
A second effect: the comfort bound is checked only at sample instants, so at the 30-min
production cycle the room overshoots the bound by up to 0.3 °C before the abort.

**Consequence.** Opt-in (`DEFAULT_SYSID_ENABLED` False). When enabled it spends a 2-h
step at 0.6·Pmax and 2 h with the pump forced off on every qualifying night and adopts
nothing; the reason is visible only in the diagnostics. No wrong money is written
because nothing is adopted — hence medium, not high.

**Perturbation.** config `slab_thermal_mass` → 0.5 and `slab_heat_transfer` → 5 on
`typical_slab` (the control): `admitted_cells` moves **up** from 0 (observed 4 of 8 on
the control). Files: `sysid.py:324-474`, `coordinator.py:10550-10642`. Fix scope:
identify against the two-store model (replay `simulate_step` over the experiment window
with UA, C_room free and the slab state carried, as the house learner already does per
interval), and abort on a predicted excursion rather than a sampled one.

### D7-02 — The defrost flag freezes the COP learner but not the fabric learners (bug, medium)

**Claim.** A defrost-flagged interval in the frost band is rejected by
`_learn_measured_cop` (v5.3.0) and ingested by `_async_learn_house_heat_loss` and
`_async_learn_lower_floor_loss`, which replay the commanded power and book the
delivered-heat shortfall as heat loss; on the two-zone radiator house the learned
`house_heat_loss_scale` reaches 1.041 at 20 % defrost intervals and 1.095 at 50 %.

**Evidence.** `learner_gates.py`: `ingest_house_loss_defrost=1`,
`ingest_lower_floor_loss_defrost=1`, `ingest_measured_cop_defrost=0`;
`defrost_scale_tz_f20=1.041379`, `defrost_scale_tz_f50=1.095282`; null control
`defrost_scale_tz_f00=1.000000`; single-zone `defrost_scale_sz_f50=1.000000`
(structurally blind: every watt passes the slab store and a one-step replay cannot see
it in the room). AST: 15 of 22 learner methods consult no defrost signal.

**Consequence.** A 4–10 % UA over-estimate for as long as the frost band lasts, in
two-zone houses with a radiator share; every plan is priced through the scale and the
learner walks back at 2 %/sample when defrosts stop — bounded, hence medium.

**Perturbation.** add the COP learner's gate (`in_frost_band(...)` and
`self._defrost_window.peek(now).any_defrost` → return) at the top of
`_async_learn_house_heat_loss`: `defrost_scale_tz_f50 − 1` **to_zero**;
`ingest_house_loss_defrost` to_zero. Files: `coordinator.py:3175-3401`,
`coordinator.py:3403-3553`, `coordinator.py:2765-2908`. Fix scope: one shared
predicate ("this interval contained a defrost") consulted by all three.

### D7-03 — The accuracy tracker records through open-window and external-heat intervals (bug, low)

**Claim.** `_record_accuracy` skips `self._accuracy.record(sample)` only on a pump-signal
freeze; an interval frozen for every learner by an open window or an external heat
source is still recorded, and the recorded error feeds `_confidence_margins`
(`sigma(lead) × (1 − trust)`, opt-in) and `temperature_bias()` for the snapshot bias
watch.

**Evidence.** `learner_gates.py`: `ingest_accuracy_record_open_window=1`,
`ingest_accuracy_record_external_heat=1`, `ingest_accuracy_record_pump_offline=0`;
every thermal learner scores 0 in the same two arms (`learners_ingesting_open_window=1`,
`learners_ingesting_external_heat=1` — the one is the tracker).

**Perturbation.** gate the record on `self._learning_frozen(CONF_INDOOR_TEMP_ENTITY)
is None` (the same predicate the lead-time scoring three statements above already
uses): both ingest results **to_zero**. Files: `coordinator.py:9179-9372`. Severity low:
the margin is capped (`CONFIDENCE_MARGIN_CAP_C`) and opt-in; the rollback decision is
separately gated by `_inputs_healthy`.

### D7-04 — `last_buffer_trajectory` is a 5 SEK side channel with one poison (hygiene, low)

**Claim.** On a store configuration the terminal cost read through
`ThermalModel.last_buffer_trajectory` moves by up to 5.42 SEK (7.1 % of the schedule's
energy cost) if any simulation intervenes between the writer and the reader, silently;
only the batch path poisons the attribute. Today every reader is adjacent to its writer
(`readers_with_model_call_between=0`), so this is a hazard, not a live defect.

**Evidence.** `trajectory_order.py`: `tc_delta_abs_max=5.416717 SEK`,
`tc_delta_rel_to_energy=0.070771`, `null_delta_abs=0.000000` (no valve),
`poison_raises=1`, `writer_sites=3`, `reader_sites_optimizer=4`,
`reader_max_line_distance=51`.

**Perturbation.** config `mixing_valve_mode` → none: `tc_delta_abs_max` **to_zero**
(observed 0.000000). Fix scope: return the buffer trajectory from
`simulate_trajectory` / `_with_dhw` (the "nine call sites unpack a four-tuple" reason in
`thermal_model.py:2270` is four production sites after the census) and delete the
attribute. Files: `thermal_model.py:1248,2275,2652,2813`, `optimizer.py:2772,2891,4615,4774`.

### D7-05 — `coordinator.py` has no cheap seam but one (hygiene, low)

**Claim.** The coordinator class is 10,269 lines / 256 methods / 174 instance attributes
(132 written from more than one method); its `_init_*` groups share 30.9 % of attribute
references and 66.1 % of self-calls across group boundaries, and no clustering at
k = 6…16 pushes cross-cluster attribute references below 0.33; the only seam with a cut
cost under 40 is the manual-plan group (10 methods, 152 lines, cut 17).

**Evidence.** `metrics_ast.py`: `coordinator_lines=10902`, `coordinator_methods=256`,
`coordinator_instance_attrs=174`, `coordinator_instance_attrs_multi_writer=132`,
`coordinator_share_of_package_lines=0.2881`, `max_cc=86`, `functions_cc_gt_20=16`.
`coordinator_clusters.py`: `cross_attr_fraction_seeded=0.3091`,
`cross_call_fraction_seeded=0.6609`, `cross_attr_fraction_k10=0.33`,
`cross_call_fraction_k10=0.7518`, `seam_min_cut_name=manual/plan`,
`seam_min_cut_cost=17`, `seam_max_cut_cost=72`, `attr_max_fan_in=77`,
`attrs_fan_in_ge_20=6`.

**Perturbation.** move the manual-plan group (`_async_load_manual_plan`,
`_async_save_manual_plan`, `_manual_pins`, `_record_manual_release`,
`_manual_plan_state`, `async_apply_manual_plan`, `async_clear_manual_plan`, …) into its
own module: `n_methods` **down** by 10 and `cross_attr_fraction_k10` down. Fix scope: a
decomposition program that first extracts the six hub attributes (`_config`,
`_thermal_params`, `hass`, `_current_state`, `_opt_config`, `_current_action`) into a
context object, then peels seams in cut-cost order (manual plan, measurements, ECL110,
insurance).

### D7-06 — Five dead defs and six production functions only tests call (hygiene, low)

**Claim.** 5 defs (46 lines) are never started by the suite and never named
anywhere in production or tests; a further 6 production defs (140 lines) are started only because
tests call them — production never references them.

**Evidence.** `dead_code.py`: `RESULT dead_candidates=5 count`, `dead_candidate_lines=46`, `dynamic_reach_started_unreferenced=7` (one is the `_async_update_data` framework hook); `started_by_suite=983` of `defs_total=1062`.

**Perturbation.** delete one listed candidate: `dead_candidates` **down** by 1 and the suite still passes; add a
production call to one: down by 1 with `started_by_suite` unchanged. Files: comfort_learning.py, config_flow.py, coordinator.py, dhw_draws.py, grid_fee.py, presets.py, pv.py, tariff.py, topology.py.

## Non-findings (checked and held)

| claim | command | value |
|---|---|---|
| The intra-package import graph is acyclic, module-level and with the two function-level imports | `metrics_ast.py` | `import_cycle_sccs_module_level=0`, `import_cycle_sccs_with_deferred=0`, `import_edges_deferred=2` |
| Every production reader of `last_buffer_trajectory` is adjacent to its writer | `trajectory_order.py` | `readers_with_model_call_between=0` over 4 readers |
| The batch poison fires on a stale read | `trajectory_order.py` | `poison_raises=1` |
| No-valve configuration is a true null for the side channel | `trajectory_order.py` | `null_delta_abs=0.000000` |
| `_learning_frozen` freezes all seven thermal learners on open window, pump offline and external heat | `learner_gates.py` | `learners_ingesting_pump_offline=0`; open window and external heat: 1 of 8 each, the accuracy tracker (D7-03) |
| The COP learner's v5.3.0 defrost gate works | `learner_gates.py` | `ingest_measured_cop_defrost=0`, clean arm 1 |
| Single-zone house learner is immune to delivered-power error (all heat via slab) | `learner_gates.py` | `defrost_scale_sz_f50=1.000000` |
| The defrost null holds exactly | `learner_gates.py` | `defrost_scale_tz_f00=1.000000` after 400 samples |
| The sysid harness can pass: first-order control completes and is admitted | `sysid_plant.py` | `control_admitted=4` of 8, bias ≤ 8.1 % |
| The two-store fit identifies UA from the same samples (noiseless, 30 min) | `sysid_plant.py` | 0.0 / 5.9 / 6.4 % on light/heavy/typical |
| Comfort bound respected on the heavy and slab presets | `sysid_plant.py` | peak excursion 0.08 / 0.33 °C |
| The scoped gate scopes an optimizer change and falls back to FULL without closures | `train_mutations.py` (probe) | 14 run / 2 scoped out; `closures.json` missing → FULL |

## Harnesses

| harness | one command |
|---|---|
| `tools/audit/round2/D7/metrics_ast.py` | `PYTHONPATH=tests/hastub python tools/audit/round2/D7/metrics_ast.py` |
| `tools/audit/round2/D7/coordinator_clusters.py` | `... coordinator_clusters.py` (writes `coordinator_clusters.json`) |
| `tools/audit/round2/D7/sysid_plant.py` | `... sysid_plant.py` |
| `tools/audit/round2/D7/learner_gates.py` | `... learner_gates.py` |
| `tools/audit/round2/D7/trajectory_order.py` | `... trajectory_order.py` |
| `tools/audit/round2/D7/train_mutations.py` | `... train_mutations.py --jobs 3` (writes `train_mutations.json`; ~10 min) |
| `tools/audit/round2/D7/dead_code.py` (+ `d7_monitor_boot.py`) | `... dead_code.py` (writes `dead_code.json`; ~4 min) |

All run from the export root with `PYTHONPATH=tests/hastub`, pin the BLAS threads before numpy,
print `RESULT` lines, and write only under `tools/audit/round2/D7/` or a private temp root
(`D7_TMP`, else `tempfile.mkdtemp`).

## Not finished, and why

- `rolling.py` (SLOW) and `stress.py` (runs alone) were not included in the dead-code
  sentinel; the 66 "referenced but never started" defs may shrink under them.
- The drift gate (`tests/env_drift.py`) and the stress budgets were not spot-mutated: the
  first needs `git worktree add`, which the export cannot do; the second is a timing guard
  that needs the quiet box.
- The two-store comparison fit in `sysid_plant.py` is a scipy least-squares over five
  parameters on 9–49 samples; with σ = 0.05 °C noise at the 30-min cadence it is itself
  ill-conditioned (up to +78 % on the control), so only its noiseless cells are cited.
- Harness gaps found and fixed during the round, recorded so the judge is not surprised:
  the first clustering used average linkage, whose ties at cosine distance 1.0 collapsed
  every k to one cluster (replaced by spectral); the first dead-code census subtracted a
  def count the AST never adds (fixed); the monitor bootstrap lacked `tests/` on
  `sys.path[0]` (fixed); and `HASTUB_TZ` exported to every script made `features.py`
  abort on a naive/aware datetime — the first mutation and dead-code runs saw a truncated
  `features.py` (all 11 mutants were still detected); the committed harnesses scope the
  variable to `dst_checks.py` and the numbers above are from the re-runs.

## Exposure

None. No `docs/` file was read for content; step 6 greps `docs/*.md` and `README.md` for
anchor words to count files only.
