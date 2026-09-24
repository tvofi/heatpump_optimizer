# D7 seat s1 report: sysid plant and gate, learner freeze, objective statefulness

Round 8, baseline `cdf82daabcfe3777d98b31489f36df5555ec9d82`. Tree: `/home/claude/audit-r8/seats/D7-s1` (copy tree).
Machine: a 4-vCPU cloud container shared with about 13 other seats (load1 13 to 26). Every number here is a
count or a ratio, deterministic at sensor noise sigma=0, and every harness printed `thread_factor=1.000`.
Nothing here is a timing. My focus was method steps 2, 3 and 4. Seat s2 covers steps 1, 5 and 6.

## Method

- **Step 2** (`s1_sysid.py`): the plant is the production `ThermalModel` for the three `tests/stress.py:BUILDINGS`
  presets, run through the production protocol (`arm(plant=...)` → `step` → `_finish` → `identify_slab`). The
  decision is made by the production gate `_adopt_system_identification`, called on a stub coordinator; the
  count is keyed on the scale that gate writes. Arms: the matched plant (the null control), the one-state
  `identify()`, a free four-constant fit (`--free`), and the true slab pair misdeclared by x0.5, 0.7, 1.4
  and 2.0 on k_s and x0.5 and 2.0 on C_s. That arm also covers the two-zone plant (`s1_sysid_twozone.py`).
- **Step 3** (`s1_learner_freeze.py`): each learner has one production entry point, called on a real
  coordinator (FakeHass) once in a clean interval and once under each contamination. The count is keyed on the
  learner's own counter. Contaminations: external heat, defrost, pump fault, pump offline, open window
  (vent CUSUM), stale indoor reading, and away. `s1_sysid_contam.py` then shows what a contaminated experiment
  night does to the adopted UA. `s1_gate_silent.py` reads what the gate publishes.
- **Step 4** (`s1_statefulness.py`): the production objective closures are captured at `_scoped_minimize`, and
  the terminal-cost closures at `_terminal_cost`. Each is evaluated around interleaved evaluations and around
  a second `optimize()` on the same optimizer. A perturbation that re-introduces a model-held buffer series
  shows that the instrument moves.

## Findings

### D7-s1-01 (medium, bug): the sysid experiment ignores the learning freeze, and contaminated nights get adopted
`_run_system_identification` checks only `space_blocked` and `freeze_reason`. It never consults `_learning_frozen`.

| learner | clean | ext heat | defrost | fault | offline | window | stale indoor | away |
|---|---|---|---|---|---|---|---|---|
| house_heat_loss | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| **sysid** | 1 | **1** | **1** | 0 | 0 | **1** | **1** | 1 |
| measured_cop | 1 | 0 | 0 | 0 | 0 | 0 | 1 (not its key) | 1 |
| flow_lift_fold | 1 | 0 | 0 | 0 | 0 | 0 | 1 (not its key) | 1 |
| buffer_cooling | 1 | 0 | 0 | 0 | 0 | 0 | 1 (not its key) | 1 |

- **Result:** `sysid_contaminated_ingest=4`. Under `--perturb` (the guard added as a method wrap) it drops to 0.
- **What it costs** (`s1_sysid_contam.py`): the clean fit error is 0.000 % on all three presets. Of 12
  contaminated nights, 4 are adopted: heavy_old wood -2.90 %, heavy_old defrost +6.47 %, typical_slab wood
  -1.35 % and typical_slab defrost +3.14 % adopted-UA error.
- **Why the rest are not adopted:** the window and stale-reading nights are refused only because their
  interval came out infinite.
- **Perturbation:** under `--perturb`, 4 drops to 0.
- **Fix:** add one `_learning_frozen` abort in `_run_system_identification`.

### D7-s1-02 (medium, bug): the one-room sysid plant cannot run on a two-zone house
`sysid.py:127` (the sizer) and `sysid.py:508` (the fit) hard-code `two_zone_enabled=False`, but the sensor they
read is the upper zone. Result from `s1_sysid_twozone.py`: `twozone_admitted=0` of 3.

- light_new and typical_slab abort in the step phase at 0.83 K and 0.91 K. The allowance is 0.8 K, so the
  room had already passed it before the abort fired.
- heavy_old finishes with a -5.66 % UA error and an infinite interval, so it is refused.
- **Null control:** the same presets derived single-zone give `singlezone_admitted=2`.
- **Perturbation:** with the plant alone made single-zone, the count goes 0 → 1.
- **Fix:** refuse `arm()` on a two-zone plant with a named reason, or model the two zones.

### D7-s1-03 (medium, bug): the #1410 adoption gate refuses silently
`coordinator.py:10495-10496` returns on the interval bar without writing a reason or a log line. Result from
`s1_gate_silent.py`: `silent_refusals=10` of 19 finished experiments.

- Each of these 10 still publishes `completed=True`, `reason='ok'` and the fitted UA. One example is a heavy_old
  open-window night: 0.5328 kW/K, which is +72 %.
- This contradicts `identify_slab`'s docstring, which says such a window is "refused by name".
- **Perturbations:** `--perturb-fix` (the one-line named refusal, applied in memory) takes 10 to 0.
  `--perturb-bar` takes 10 to 8.
- **Null control:** the adopted results publish `reason='adopted'` and emit one log line each.

## Non-findings

- **Matched plant:** the production two-state fit gives 0.000 % UA bias on all three presets.
- **One-state `identify()`:** on the two-state plant it refuses on all three presets and adopts nothing.
- **Free four-constant fit:** on light_new it recovers UA at -0.000 %.
- **light_new:** the gate refuses it even on a perfect fit, because the prior half-width (0.1446) is above the
  bar (0.0953). This is the round-7 design trade, so the experiment never adopts on this preset.
- **Slab-pair misdeclaration:** 18 cells, 15 of them completed. No fit with |bias| > 10 % is admitted
  (`admitted_biased_cells=0`). The largest bias is 25.83 %, or 14.93 % with the worst cell dropped. The
  largest adopted error is 2.53 %. With `--perturb-declared`, every bias is 0.00 %.
- **House heat-loss learner:** it freezes on every physical contamination.
- **Measured COP, flow-lift fold and buffer cooling:** they freeze on the plant-wide reasons. Freezing also on
  window and external heat is the documented fail-closed trade.
- **Objective statefulness (step 4):** `order_mismatch=0` of 9, `tc_order_mismatch=0` of 2, `scratch_attrs=0`,
  `side_series=0`. The instrument moves under `--perturb` (1, 1, 1).
- **Hygiene note:** `optimizer.py:1040-1041` still says the model stashes the buffer series for the terminal
  cost. That is no longer true.

## Harnesses
`s1_sysid.py`, `s1_sysid_contam.py`, `s1_sysid_twozone.py`, `s1_learner_freeze.py`, `s1_gate_silent.py`, `s1_statefulness.py`.
They are all under `tools/audit/round8/D7/` and each runs with `PYTHONPATH=tests/hastub python3 -u <path>`.

## Not finished
- **Free four-constant fit:** not run for heavy_old or typical_slab. It is slow under load; run it with `--free`.
- **Noise ensembles:** not run, so every number is at sigma=0.
- **Finding ids:** they use the task's `D7-s1-NN` form, which the schema's id pattern rejects. The file
  validates apart from those three id errors.
- **Two-zone abort cause:** it is attributed to the one-room sizer by the `--perturb` arm only. I did not
  instrument the sizer's prediction against the upper-zone trace.

## Exposure
None. No docs, no GitHub, no earlier findings read.
