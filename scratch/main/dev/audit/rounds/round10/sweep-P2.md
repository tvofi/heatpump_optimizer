# Round 10, class P2 sweep (D14 method steps 3-4)

Seat: class-sweep P2, PLAN phase D. Tree: `handoff/audit-r10-register` at `9355f107d`.
Class P2: a fact the package uses at several places is decided at each place by a local
copy of the rule, not by one owner the others call (`dev/audit/rca/R9-P2.md`). Ledger status in
`dev/audit/config/bugclasses.json`: the class row (#1644) is `prototype-only` (owners lint, not
landed), so the class is **not barriered**. The two instance-level rows (#1499, R8-P2) are `done`.

Machine: macOS arm64, venv-ci python 3.14, load1 about 8.5. Every count is a static AST count or a
deterministic probe, so load does not affect it.

## Enumerator

`python3 dev/audit/rounds/round10/D14/sweep-P2/enumerate_p2.py` covers the whole package. It has
seven fact-families. Each family is a finding's `seam_rule`, widened from the files that finding
named to every module:

| family | rule | finding | seams |
|---|---|---|---|
| F1 run_threshold | a 0.05/0.1 literal compared with a power/draw value, or a `threshold` default of one, instead of `MIN_RUNNING_DRAW_KW` | D8-s1-01 | 20 |
| F2 learner_gate | a coordinator learner `.observe(`/`.fold(` whose enclosing function makes no `_learning_frozen(` refusal of its own | D7-s2-01 | 8 |
| F3 cop_law_fork | a function that branches on `cop_flow_carnot` (it holds its own choice of COP law) | D2-s2-01 | 3 |
| F4 entry_resolve | a service handler that returns before it resolves `entry_id` through `_loaded_entries`/`_loaded_coordinators`/`_manual_targets` | D10-s1-51 | 1 |
| F5 clone | archscore gapped clone classes (the C3 census) | D7-s2-52..56, 59 | 43 |
| F6 hour_clock | a function that rounds `h*60` and reduces by `24*60` | D7-s2-57 | 5 |
| F7 scrub_mixin | an entity class, or a mixin of one, that publishes a property from outside `HeatPumpOptimizerEntity` | D7-s2-51 | 0 |

Total: 80 seams (`RESULT seams_total=80`).

**Controls**, all rc 0:

- **Positive** (`--control`): every judged site of the 11 findings that have a site at baseline is
  found again, with `missed_sites=0` over 21 site checks. D7-s2-51 is latent: its own finding reads
  `escapes 0 at baseline`. Its control is the F7 perturbation below, which reproduces arch-s2
  patch 01's shape.
- **Null** (`--fixture`): a clean synthetic package. In it, one owner holds each fact, and the
  running threshold, the learner gate, the COP law, the entry resolution, the clock and the
  published property all go through that owner. Result: `fixture.total=0`, and 0 in every family,
  including F5 run through the real archscore counter.
- **Perturbation** (`--perturb`): one re-introduction per family on a temp copy. Each moves its
  family by exactly +1:
  - F1: `optimizer.count_compressor_starts` default back to `0.05`, 20→21.
  - F2: `_fold_flow_lift`'s `_learning_frozen` line becomes `if False:`, 8→9.
  - F3: a second flag-forked COP helper, 3→4.
  - F4: an early `return` before `_loaded_entries` in a handler, 1→2.
  - F5: a second copy of `thermal_model._flow_curve_values`, 43→44.
  - F6: a sixth clock function, 5→6.
  - F7: a sensor that takes `native_value` from a mixin, 0→1.

The F3 and F5 perturbations append a few lines rather than edit one, because the rule needs a whole
function to match.

**Probes for the new instances**: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-P2/probes_p2.py`
gives `probes_failed=6 of 6`. Each probe asks the seam and the owner (`thermal_model.planned_draw_runs`)
the same question on the D8-s1-01 step (0.07 kW asked), and fails when the answers differ.

Under `--perturb`, every copy's literal is set to the owner's 0.1 on a temp copy, and the result is
`probes_failed=0 of 6`. So the probes detect the literal and nothing else.

The F5 instances have no behavioural probe. Their probe is the census: under one owner, the class
would list 0 members. This is the same standard as the judged D7-s2-52..56/59 findings, whose metric
was the duplication score.

## Dispositions (80 seams)

### F1 run_threshold (20)

The fact is "does the plan run this step". Its owner is `thermal_model.planned_draw_runs` /
`MIN_RUNNING_DRAW_KW = 0.1` kW on space+DHW (`optimizer.count_compressor_starts` already defaults to it).

| seam | disposition |
|---|---|
| coordinator `_build_plan_views:4161`, `:4178` (`active_now`) | **instance, judged** (D8-s1-01) |
| coordinator `_plan_slots:3920` (`threshold=0.05`) | **instance, judged** (D8-s1-01) |
| sensor `native_value:1274`, `:1277` (DHW schedule fallback) | **instance, judged** (D8-s1-01 seam_rule) |
| optimizer `classify_space_steps:1137` (`threshold=0.05`) | **instance, new**: a 0.07 kW step gets `terminal_value`, but the owner says off. Both production callers use the default |
| optimizer `classify_dhw_steps:1213` (`threshold=0.05`) | **instance, new**: `dhw_ready` on a step the owner says is off |
| freq_control `FrequencyMap.recommend:179` (`target_kw <= 0.05`) | **instance, new**: `_command_frequency` passes `_commanded_power()`, and 0.07 kW gives a 33.0 Hz write on a step the plan declares off |
| freq_control `FrequencyMap.evidence_exhausted:206` | **instance, new**: the same gate, on the published view |
| coordinator `_async_learn_buffer_cooling:4873` (`power > 0.05`) | **instance, new**: `heating=True` on a step the owner says is off, so an idle interval is refused for the cooling fold |
| coordinator `_observe_frequency:10664` (`_commanded_power() > 0.05`) | **instance, new**: the frequency watchdog is armed on a step the plan declares off |
| coordinator `_detect_immersion:8768` (`_commanded_power() > 0.1`) | not applicable: a value-equal copy, so no input separates it from the owner. It is latent, and is listed for the barrier |
| optimizer `get_current_action:5560` (`dhw_power > 0.1`) | not applicable: the per-channel DHW flag. Its value equals the owner's, and its divergent counterpart is the judged `active_now` |
| climate `hvac_action:181` (`power_norm > 0.1 or heat_pump_on`) | guarded: it reads the owner's own `heat_pump_on` bit, and `power_norm` is a 0..1 fraction, not kW (#1683 fix) |
| accuracy `delivered_ratio:633` (×2, `<= 0.05`) | not applicable: a measured-ratio validity floor, not the running fact |
| coordinator `_fold_capacity_envelope:9000`, `_capacity_caps:9031` (`p_max <= 0.1`) | not applicable: a nameplate sanity floor |
| dhw_learning `async_learn_usage:518` | not applicable: a °C/h draw intensity, not kW |
| freq_control `observe:136` (`kw <= 0.05`) | not applicable: a measured-kW noise floor for the fold, not the plan's decision |

### F2 learner_gate (8)

| seam | disposition |
|---|---|
| coordinator `_observe_frequency:10696` `_freq_map.observe` | **instance, judged** (D7-s2-01). `_freq_fold_blocked` keeps only the `":"` reasons of `_learning_frozen` |
| coordinator `_settle_defrost:9711` `_defrost.observe` | guarded: `power_frozen = self._learning_frozen(CONF_POWER_ENTITY)` at coordinator.py:9736 in the caller, plus `_cop_fold_blocked`. learner_gates.py shows defrost_derate frozen on external_heat, pump_offline and open_window, and ingesting on defrost by design |
| coordinator `_update_current_state:6169`, `_on_defrost_event:8380` `_defrost_window.observe` | not applicable: they record the defrost state itself |
| coordinator `_update_current_state:6194` `_legionella.disinfect.observe` | not applicable: an event tracker for tank temperature, not a rate learner |
| coordinator `_track_realised_peak:8331`, `_on_power_event:8450` `_peak_tracker.observe` | not applicable: a billing peak of real grid draw, where a defrost or a booster is a real kW |
| coordinator `_observe_compressor_start:10259` `_start_counter.observe` | not applicable: a start counter |

### F3 cop_law_fork (3)

| seam | disposition |
|---|---|
| thermal_model `compute_cop_dhw:2189` | **instance, judged** (D2-s2-01) |
| thermal_model `compute_cop:2015` | not applicable: it is the owner (`_cop_law` plus a lift) that the others follow |
| thermal_model `_batch_cop:3314` | guarded: the batch/scalar parity in `tests/features.py` (`simulate_trajectory_batch` block, about line 5868). cop_laws.py also gives `batch_scalar_cop_mismatch=0 of 63570` |

### F4 entry_resolve (1)

services `handle_apply_schedule:980`: **instance, judged** (D10-s1-51). No other handler returns
before it resolves the entry.

### F5 clone (43)

The 11 classes numbered below are **instances**. The rest share windows that are boilerplate or an
idiom, sit inside an owner, belong to another class, or are guarded.

- **Judged instances (10)**:
  - #0 [11] and #3 [4] sensor `native_value`: D7-s2-52.
  - #2 [5] and #37 [2] sensor `native_value`: D7-s2-53.
  - #6 zone-setpoint attributes: D7-s2-54.
  - #13 config_flow suggested helpers: D7-s2-55.
  - #1, #14 and #15 options pages: D7-s2-56.
  - #23 grid_fee range parser: D7-s2-59.
- **Judged under F6**: #21 dhw_draws `_fmt` / dhw_schedule `fmt` is D7-s2-57, the same sites as F6.
- **New instances (11)**:
  - #7: the pending interval's planned split, read three times in coordinator.
  - #16: the sample-acceptance rule of the house and lower-floor loss learners. The lower one even
    logs "House heat loss".
  - #17: the sensed-zone trajectory choice.
  - #18: the sensed-zone capacity choice.
  - #30: house UA in `_buffer_charge_ceiling` / `hold_demand_kw`.
  - #31: peak-window factor padding (`optimizer._grid_report` / `tariff._peak_excess`).
  - #32: the metering-window count.
  - #36: accuracy and last_diagnosis attributes.
  - #39: peaks and peak_days unpacked twice.
  - #40: steps per metering window, scalar and batch, with no parity test (no `tests/` hit for
    `_window_means_batch`).
  - #41: the window-slot base.
- **Guarded**:
  - #4: the tariff smooth top-k scalar/batch twins, held by the `peak_cost_batch` bit-parity check
    in `tests/features.py` (about line 6819).
  - #10: `_simulate_step_*` / `simulate_trajectory_batch`, held by the `tests/features.py`
    `simulate_trajectory_batch` parity block.
  - #33: `objective` / `objective_batch`, held by `tests/features.py` (about line 6498) and
    `tests/optimality.py`.
- **Not applicable**:
  - Rejected as "not one operation" by arch-s2 N3: #5 `available`, #9 `_waiting_for`, #22
    drift/power_guard `_note`, #27 ledger `_prune` / wear `observe`, #28 ledger `add` /
    `observe_meta_mean`, #29 legionella checks.
  - Inside the owner module `inputs` itself: #24, #25, #26.
  - Class P3 (coercion and numeric guard, arch2-08 and arch2-11): #11 away / wood_fuel, #12 climate
    / defrost numeric guard, #19 raw state float reads, #34 price_model entry validation.
  - Step-grid class (`dev/audit/rounds/round10/D14/s1/stepgrid_seams.py`): #35 pump_arbiter step
    index.
  - Boilerplate: #20, InputReader construction from the shared ctx config.
  - Already routed through owners: #8, optimizer pin seeding (`_apply_pins_to_bounds`,
    `_seed_pinned_guess`); #42, trajectory seeding (`_seeded_tracks`, `weather_or_calm`), whose
    residue is per-step writeback.
  - Numerical idiom: #38, the sysid finite-difference step.

### F6 hour_clock (5)

dhw_draws `_fmt`, dhw_schedule `fmt`, pump_arbiter `_night_clock`, quiet_windows `_gchv_at` and
quiet_windows `_fmt`: **instance, judged** (D7-s2-57).

### F7 scrub_mixin (0)

There is no seam at baseline, which matches D7-s2-51's weakened verdict ("latent hazard only"). The
perturbation shows the family fires on the hazard's shape.

## Count

- **Instances beyond the findings: 17.** That is 6 in F1, each with a failing behavioural probe, and
  11 in F5, each with a census probe.
- **Judged sites listed: 21.**
- **Guarded: 6.** F1 climate; F2 `_settle_defrost`; F3 `_batch_cop`; F5 #4, #10 and #33.
- **Not applicable: the rest.**

The F1 cluster is the one that matters for behaviour. Four more copies of the running rule disagree
with the owner on the same 0.05–0.1 kW band that D8-s1-01 judged. One of them
(`FrequencyMap.recommend` via `_command_frequency`) writes a compressor frequency in control mode on
a step the plan declares off.

## Proposed barrier

`defect-root-cause.md` decides the barrier on these counts. The detectors are:

- **F1**: refuse a numeric literal compared with a power/draw name, or a `threshold` default, other
  than `MIN_RUNNING_DRAW_KW`. This is the enumerator's F1 rule, run as a `tests/` lint, with value-equal
  copies counted too so the latent `_detect_immersion` site is caught.
- **F4**: a handler may not `return` before entry resolution.
- **F5**: the archscore duplication ratchet that already exists.

All three are static AST passes over the package, under a second in total. This was not measured as
gate seconds.

## Files

- `dev/audit/rounds/round10/D14/sweep-P2/enumerate_p2.py`
- `dev/audit/rounds/round10/D14/sweep-P2/probes_p2.py`
- `dev/audit/rounds/round10/sweep-P2.json`
