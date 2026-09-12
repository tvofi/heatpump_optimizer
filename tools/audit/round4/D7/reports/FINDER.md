# D7 — Architecture and maintainability — round 4

- baseline: `7dd68dd327fe3dbfb09f3bd0fe38910c58877697`
- tree: `/Users/timmalmstrom/heatpump_optimizer/.claude/worktrees/audit-r4-baseline` (export, no `.git`)
- interpreter: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`,
  always `PYTHONPATH=tests/hastub`, always from the export root
- machine: 8-core Apple M1, 8 GB, macOS 25.6, numpy on OpenBLAS, BLAS threads
  pinned to 1 in every harness
- box conditions during the fan-out: `load1` 4.0–11.6 (quoted per RESULT line).
  **Every number in this report is a count or a ratio.** Timing is not this
  dimension and none is claimed, so contention does not bear on any figure here.

## Method, in the brief's order

### 1. Metrics: read, not re-derived

`tests/structure_budgets.json` was **read**, never re-derived. The metric count
is derived from the file itself — its keys less `recorded_at`, which is
metadata — and is **24** (`RESULT budget_metrics=24`, printed by
`dead_methods_r4.py`). `tests/structure.py` was run once, unmodified, and its
own output is quoted rather than reproduced by a second AST pass.

**The reading of a metric the file does carry.** All 24 metrics sit at exactly
zero headroom: every `ok` line in the ratchet block reads `N <= N`, for all 24
rows, with no row below its budget. The coordinator class is 9082 LOC
(`coordinator_loc` = `max_class_loc`, i.e. it *is* the largest class in the
package) across 227 methods and 152 attributes, 116 of them multi-assigned;
`max_cc` is 50 and `max_method_loc` 393. So the ratchet is not a budget with
room in it — it is a freeze. Any production line added to a measured class must
be paid for by a removal in the same pull request, in the same metric.

**The metric the file does NOT carry: dead methods.** `dead_top_level_symbols`
is scoped, by `structure.py`'s own documentation of it, to *top-level*
defs/classes/assignments. The package defines **912 methods under 621 distinct
names** and not one of the 24 metrics looks at them.
`tools/audit/round4/D7/dead_methods_r4.py` measures them with the same
reference universe the top-level screen uses, plus a runtime sentinel. Result:
36 methods are never referenced by name inside the package, **all 36 are Home
Assistant convention entry points**, 30 of the 36 were observed actually
executing under the sentinel (9838 wrapped calls while `tests/entities.py`
drove the real `async_setup_entry` for every platform), and
**`dead_methods = 0`**. This is a non-finding, but it is a non-finding the
ratchet cannot currently produce.

### 2–6

See Findings and Non-findings below. Item 5 of the brief (the spot-mutation
table for this year's train) was **not completed** — see "What I could not
finish".

---

## Findings

### D7-01 — the sysid experiment cannot complete on any building preset the gate ships

**Claim.** Run the production system-identification protocol
(`sysid.SystemIdentification.step` → `identify`) against the production
`ThermalModel` single-zone plant for the three building presets `stress.py`
sweeps (`light_new`, `heavy_old`, `typical_slab`), across the whole outdoor
band `SysIdConfig` admits (-5, 0, +5 °C) and both plausible cadences (15 min
and the 30-min `DEFAULT_OPTIMIZATION_INTERVAL`), and the production adoption
gate (`coordinator.py:_adopt_system_identification`, `completed and
confidence >= 0.3`) admits **0 of 18 cells**. Six cells breach the comfort
allowance and abort; the other twelve fail the fit's own sign or gains guards
(`"fit gave implausible signs"`, `"fitted gains outside plausible bounds"`).

The cause is structural, not tuning. The identifier regresses room rate on
(ΔT, Q, 1, t) — one state. The plant is two states: heat lands in the slab and
reaches the room only through `slab_heat_transfer`, so the room keeps rising
after the step ends and the least-squares slope on ΔT comes out the wrong sign.
The same relax window fitted with two exponentials instead of one drops the
residual sum by **41× to 155×** (`sse1_over_sse2`), which is the misspecification
measured directly.

**The control that proves the instrument can adopt.** The identical protocol,
identical code path, on a plant whose slab coupling is multiplied by 100 —
collapsing it towards the single state the identifier assumes — completes and
is adopted at confidence **0.940** with a UA bias of **+5.58 %**
(`null_onestate_adopted=1`). The harness is not one that can only print zero.

**Favourability.** `internal_gains` is pinned to 0.3 kW, exactly
`SysIdConfig.gains_prior_kw`, so the fit's intercept prior is exactly right.
That is the most favourable case available and it still fails.

- evidence: `RESULT adopted_cells=0 count` over `RESULT grid_cells=18 count`,
  `RESULT null_onestate_adopted=1`, `RESULT sse1_over_sse2_min=40.68`,
  `RESULT sse1_over_sse2_max=154.98`
- harness: `tools/audit/round4/D7/sysid_plant_r4.py`
- instrumented symbol: `custom_components/heatpump_optimizer/sysid.py:SystemIdentification.identify`
- perturbation: `HPO_D7_SLABK=100` multiplies the plant's `slab_heat_transfer`
  by 100. **Executed:** `adopted_cells` moves 0 → 9. Direction: up.
- metric definition: the number of (preset × outdoor × cadence) cells in which
  `SysIdResult.completed` is true and `confidence >= 0.3`.
- leave-one-out: not applicable to a count that is 0 in every one of 18 cells;
  the per-cell reasons are printed individually so no cell is carrying the
  result.
- severity: **medium** — the feature is opt-in (`DEFAULT_SYSID_ENABLED = False`)
  and adopts nothing, so no wrong parameter reaches a plan. What is lost is the
  whole feature, plus the night the experiment spends running.
- stop-rule class: `bug`
- files: `custom_components/heatpump_optimizer/sysid.py`,
  `custom_components/heatpump_optimizer/coordinator.py`
- proposed fix scope: either fit the two-state structure the plant actually has
  (a second regressor for the slab, or a two-exponential fit as the estimator),
  or state in `sysid.py` that the identifier is only valid for houses whose
  slab coupling is fast relative to the step, and gate on that.

### D7-02 — the step sizer's plant is not the house's plant, and the comfort bound is breached

**Claim.** `sysid._sizing_model` builds the plant it sizes the step against
from four numbers — UA, room mass, gains, `two_zone_enabled` — and leaves
`slab_thermal_mass` and `slab_heat_transfer` at `ThermalParameters`' defaults
(5.0 kWh/°C and 0.8 kW/°C). The three shipped presets carry (0.24, 0.24),
(23.0, 2.0) and (16.5, 1.5). `_predict_step_excursion_plant`'s prediction is
therefore about a different building, and the ratio of the excursion the real
plant actually makes to the one the sizer predicted ranges over **0.486 to
1.329** across the 18 cells. On `light_new` the sized step drives the room
**1.01–1.06 °C** from baseline against a `max_excursion_c` of **0.80 °C** — the
comfort constraint the module's own docstring calls "not negotiable" — in
**6 of 18 cells**. In the other direction (`heavy_old`, `typical_slab`) the
step is roughly half the size the comfort bound would have allowed, so the
experiment gathers about half the excitation it was permitted.

**The counterfactual, executed in the same run.** Replacing `_sizing_model`
(harness side only) with one carrying the plant's own slab mass and coupling
drives `peak_ratio` to **0.97–1.00** and comfort breaches to **0**.

- evidence: `RESULT comfort_breach_cells=6 count`,
  `RESULT peak_ratio_min=0.486`, `RESULT peak_ratio_max=1.329`,
  `RESULT honest_sizer_breach_cells=0`,
  `RESULT honest_sizer_peak_ratio_max=1.000`
- harness: `tools/audit/round4/D7/sysid_plant_r4.py`
- instrumented symbol: `custom_components/heatpump_optimizer/sysid.py:_sizing_model`
- perturbation: the built-in `honest_sizer` arm swaps `sysid._sizing_model` for
  one carrying `params.slab_thermal_mass` / `params.slab_heat_transfer`.
  **Executed:** `honest_sizer_peak_ratio_max` falls 1.329 → 1.000 and
  `honest_sizer_breach_cells` falls 3 → 0 on the same three presets.
  Direction: down.
- metric definition: per cell, the peak `|T_room − baseline|` the production
  `ThermalModel` actually reaches, divided by the peak
  `sysid._predict_step_excursion_plant` predicted for the step it sized; and
  the count of cells whose achieved peak exceeds `max_excursion_c`.
- leave-one-out: 18 cells; range 0.486–1.329; mean 0.760; mean with the single
  cell closest to 1.0 dropped, 0.735. No cell carries the result.
- severity: **medium** — a real comfort excursion 33 % past the stated
  allowance, but on an opt-in night experiment, caught one interval later by
  `_over_excursion` and aborted.
- stop-rule class: `bug`
- files: `custom_components/heatpump_optimizer/sysid.py`
- proposed fix scope: pass the configured `ThermalParameters` (or at least the
  slab pair) into `_sizing_model` instead of reconstructing a partial copy;
  `_begin_step_phase` already has the coordinator's params one frame up.

### D7-03 — the shared learner freeze never consults the defrost flag

**Claim.** `coordinator.py:HeatPumpOptimizerCoordinator._learning_frozen` is the
one gate every thermal learner consults. It refuses an interval for external
heat, for `pump_signals.freeze_reason` (offline / fault / cooling), for any
unusable configured input, and for the ventilation CUSUM. It never looks at
`self._pump_signals.defrosting`, even though the coordinator reads that flag
every cycle and folds it into `_defrost_window` a few lines earlier.

Driven directly, with a live positive control on every cell: of the four
learners exercised, **3 of 4 ingest an interval in which the pump says it
defrosted** — `_async_learn_house_heat_loss` (writes the persisted
`_house_heat_loss_scale`), `_async_learn_buffer_cooling` (writes the persisted
`_buffer_cooling_rate`), and `DhwProfileLearner.async_learn_dynamics` (writes
the persisted cooling rate, hourly profile and draw stats). The one that
refuses is `_learn_measured_cop`, and it refuses because it carries its **own**
bespoke `in_frost_band` / `any_defrost` block — a guard written once, at one
call site, for a contaminant the shared gate does not know about.

A defrost reverses the cycle: it takes heat out of the circuit. The interval's
delivered heat is therefore *negative* while the learners replay it as if the
commanded/measured electrical power had delivered heat, so the residual is
one-directional. That is precisely the class `_learning_frozen`'s own docstring
describes ("a learner that trains ... on heat it did not supply corrupts a
parameter that is persisted to disk").

Every one of the 20 cells has a positive control: the identical interval with
no contaminant, shown to move the learner's persisted value
(`positive_control_dead_learners=0`), so a `frozen` reading is the gate and not
a dead setup.

- evidence: `RESULT ingesting_cells_defrost=3 count` of
  `RESULT live_learner_cells=20 count`; the other four contaminants read
  `ingesting_cells_external_heat=0`, `_open_window=0`, `_pump_fault=0`
- harness: `tools/audit/round4/D7/learner_freeze_r4.py`
- instrumented symbol:
  `custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._learning_frozen`
- perturbation: wrap `_learning_frozen` so it also returns a reason when
  `self._pump_signals.defrosting` — the one line it lacks. **Executed in the
  same run:** `ingesting_cells_defrost` falls 3 → 0
  (`RESULT perturbed_ingesting_cells_defrost=0`). Direction: down. The opposite
  direction: deleting the bespoke `in_frost_band` block inside
  `_learn_measured_cop` raises it 3 → 4.
- metric definition: the number of (learner × contaminant) cells in which the
  learner's persisted parameter changes value when handed an interval the named
  signal says is contaminated, counted only over cells whose clean control
  changed.
- severity: **high** — a persisted parameter (`house_heat_loss_scale`) that
  prices every plan the integration publishes is fed one-directionally biased
  samples with no gate. I did **not** measure the resulting drift magnitude;
  if the judge wants the severity anchored to a °C or a currency figure, that
  measurement is owed and I flag it as unmade.
- stop-rule class: `bug`
- files: `custom_components/heatpump_optimizer/coordinator.py`
- proposed fix scope: one condition at the head of `_learning_frozen`, in the
  same "freeze on the presence of a reading" block as the three pump-signal
  conditions already there; and then `_learn_measured_cop`'s bespoke block
  becomes the narrowing (the derate learns from that interval) rather than the
  only guard.

### The away column, reported and not claimed

All four learners ingest an interval flagged away. I am **not** filing that as a
finding: away-mode setback does not invalidate a thermal measurement — the
physics is the same house — and `_learning_frozen` looking past it is defensible
by design. The brief asked for the enumeration and it is in the table; the
judgement it invites is that `away` belongs in the table's "does not gate"
column and not in a fix.

---

## Non-findings — what held, with the command and the number

| what was checked | command | number |
|---|---|---|
| `last_buffer_trajectory` and every other `last_*` simulation side-channel on the long-lived `ThermalModel` / `HeatPumpOptimizer` | `PYTHONPATH=tests/hastub python3 tools/audit/round4/D7/objective_statefulness_r4.py` | `model_last_attrs=0`, `optimizer_last_attrs=0`; positive control, injecting one such attribute, reads `positive_control_last_attrs=1` |
| reordering the objective / a second `optimize()` on the same instance in between | same harness | `reorder_distinct_results=0` over `reorder_pairs=5` scenario pairs (`valve_storage`, `winter_two_zone_dhw`, `everything_on`, `wood_two_tank`, `legionella_due`); `terminal_cost_reorder_max_delta=0.000e+00` — A and A' identical bit for bit with a different scenario solved in between |
| dead methods across the package (the metric the ratchet does not carry), AST reachability + runtime sentinel | `PYTHONPATH=tests/hastub python3 tools/audit/round4/D7/dead_methods_r4.py` | `methods_total=912`, `methods_distinct_names=621`, `name_unreferenced_methods=36`, `ha_convention_methods=36`, `dead_methods=0`; sentinel live at `sentinel_calls_observed=9838`; injected probe moves the screen 36 → 37 |
| the structural ratchet itself | `PYTHONPATH=tests/hastub python3 tests/structure.py` | `STRUCTURE RATCHET PASSED`, 24 of 24 rows at `N <= N` (zero headroom on every one) |
| external heat / open window / pump fault as learner gates | `PYTHONPATH=tests/hastub python3 tools/audit/round4/D7/learner_freeze_r4.py` | `ingesting_cells_external_heat=0`, `ingesting_cells_open_window=0`, `ingesting_cells_pump_fault=0` — all four learners freeze on all three, and the clean controls are live |
| `_learn_measured_cop` against a defrost inside the frost band | same harness | `ingesting_cells_learner_measured_cop=1` (the away cell only) — its own `in_frost_band`/`any_defrost` block refuses the defrost interval |

## Harnesses

All under `tools/audit/round4/D7/`, each runnable by the single command in its
own header, each pinning BLAS threads before importing numpy, each resolving
the repository root as `Path(".")` — i.e. **they measure the working directory
they are run from**, so run them from the tree under test.

| harness | what it measures |
|---|---|
| `sysid_plant_r4.py` | D7-01 and D7-02: the sysid protocol driven against the production plant for 3 presets × 3 outdoor temps × 2 cadences, with a one-state null arm and an honest-sizer counterfactual arm |
| `learner_freeze_r4.py` | D7-03: the learner × contaminant ingestion matrix, with a live clean control per cell and the fix's perturbation executed in-process |
| `objective_statefulness_r4.py` | the `last_*` side-channel screen and the call-reorder determinism check, with a positive control |
| `dead_methods_r4.py` | dead methods by AST reachability plus a runtime sentinel (it writes and runs `_sentinel_run.py` in the same directory) |

## What I could not finish

- **Item 5 of the brief — this year's train, one row per addition since v4 with
  an executed spot-mutation result — was not done at all.** No row, no mutation.
  It is the single largest piece of the brief left open and it needs its own
  session: each row is a production deletion plus a scoped gate run, and the
  gate lease was never taken.
- **The drift magnitude behind D7-03 is unmeasured.** I proved the sample is
  ingested; I did not measure how far `_house_heat_loss_scale` walks over a
  defrost-heavy week. The severity I assigned (`high`) rests on the consequence
  class, not on a measured °C or currency figure.
- **Only four learners are in the freeze matrix** (house heat loss, buffer
  cooling, measured COP, DHW dynamics). The lower-floor loss ratio, the curve
  bias learner, the comfort-weight learner, the accuracy records, the capacity
  envelope, the COP health baseline and the defrost derate are enumerated in
  the code but were not driven. The count `ingesting_cells_defrost=3` is
  therefore a **lower bound** on the defrost exposure.
- The two-exponential fit is used here as a *misspecification test* (residual
  ratio on the relax window), not as a competing UA estimator — a two-state UA
  estimate needs a mass split the step response alone does not pin. That is a
  deliberate scope cut, not an omission I discovered late.

## exposure

- No `gh`, no GitHub, no `docs/audit-*.md`, no `docs/backlog.md`, no round-3
  material. `tools/audit/round3/` is absent from this export.
- One accidental exposure to a plan document, recorded honestly: a `grep -rn
  last_buffer_trajectory` across the tree printed one matching line each from
  `docs/plan-open-issues.md:269` and `RELEASE_NOTES.md:2484`. I read the two
  grep output lines; I did not open either file, and neither line carries a
  verdict.
- I read `tests/features.py:7600-7700`, which contains a code comment citing
  `R3-D7-02`. `COMMON.md` names that case explicitly as context, not a to-do,
  and I treated it so: the statefulness harness was written to measure the
  property independently rather than to confirm the comment.
- Nothing under `custom_components/` or `tests/` was modified. Every
  perturbation is a harness-side monkeypatch restored in a `finally`.
