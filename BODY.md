Fold (e) of #1955: an optional thermal power entity (`heat_pump_thermal_power_entity`, "Heat pump thermal power meter", on the options' Power and energy group beside the electrical meter). #2006 built (a)-(d) and closed the issue; (e) was left unbuilt. Absent the key every path is the one it was.

Closes #1955

**The one probe.** `thermal_model.probe_install` gains `measured_heat` (the key is set); no second probe. (a)'s clamp, (c)'s freeze and (d)'s duty-cycle reading do not read it, so `fully_metered()`, `levels_clamped()` and `learner_unmetered()` answer what they answered.

**Heat meter and flow meter: which wins.** `flow_meter.read_heat_output_kw` is the one answer to "what heat did the pump deliver this cycle", and both sources land in the same `FlowCurveBias.heat_output_kw` holder every consumer already reads (#2016). A configured heat meter answers alone, whatever else the install has: unlike the flow meter, a power or frequency signal does not switch it off, because it is the direct reading rather than a stand-in. When it is configured the flow meter is not consulted at all, even in a cycle the heat reading is unusable (stale, unavailable, unknown unit, negative): that cycle carries no measured heat, and the learners that read it freeze on the configured slot's health rather than silently changing estimator mid-learning. Without the heat meter the flow meter keeps its #2016 rule exactly (only with no power and no frequency signal).

**The three consumers.**
1. *Measured COP into `cop_scale`.* With a heat reading and an electrical one, `_fold_measured_cop` takes heat over electricity as the observed COP (`flow_meter.cop_evidence`) and skips the commanded-ratio tracking gates, which exist only because delivered heat was not measured (v4.0.5). It is judged against the model's own COP law at the supply the pump ran at (`flow_meter.space_reference_cop`, through `compute_cop_dhw`, the one law at a known water temperature), so the scale learns what is left once lift is accounted for: on a direct plant it no longer absorbs the weather-driven lift as wear (`flow_lift.py`'s documented failure). Without a fresh supply reading the reference is the plan's own price, as today. Without a heat reading the commanded inference runs in its own float order, bit for bit. The frozen/duty-floor/frost/distorted/blended guards are unchanged and still apply. A configured heat meter whose reading is unusable freezes the fold (`COP_REFUSED_FROZEN`), it does not fall back.
2. *House heat-loss learner.* It already replays a measured heat for a space-only interval (#2016's `_interval_measured_heat_kw`); the heat meter now feeds that same path, on any install. On a switch-plus-setpoint install without electrical metering the (c) unmetered-power freeze lifts for an interval the heat meter measured (`flow_meter.replay_freeze`), because the commanded-kW assumption it guards against is no longer in the replay; every other freeze reason stands, an interval without a reading stays frozen, and a flow-meter figure keeps today's freeze. The lower-floor learner replays through the same `_replay_interval`, so it takes the same rule rather than diverging from its sibling about what the interval delivered.
3. *Capacity envelope.* A measured heat is sampled at every load, as a floor: delivered heat is a lower bound on capacity, so at partial load it may raise (or seed) its bucket, but it never decays the bucket and never counts towards `CAPACITY_MIN_SAMPLES`. At or above 95 % of nameplate a measured heat replaces the modelled `observed_cop x measured_power` and is forgotten and counted as before. Design choice, stated: counting partial-load samples would re-open the self-censoring ratchet `_fold_capacity_envelope`'s docstring describes (caps limit the plan, the plan limits the samples), so "samples at all loads" is taken as a raise-only floor rather than a full sample.

**Not built, and why.** `thermal_model._FEEDBACK_CLASSES` (#1956's card recommendation) does not offer the heat meter: adding a class adds a row to every unmetered install's recommendation and so moves published state, which this fold's byte-identical contract rules out; a heat meter without an electrical one also makes no COP observable.

**Alternatives considered (fixer step 17).** (i) Lifting the unmetered freeze in `learner_unmetered` for any install with a heat meter: rejected, it would lift it for every learner and for hot-water intervals the meter cannot attribute, where the replay falls back to commanded kW. (ii) A second reference COP method on `ThermalModel`: rejected, `compute_cop_dhw` already is the one law at a known water temperature, and a method would grow a class already past its size limit. (iii) Keeping the reference choice and the two inferences inline in the coordinator: rejected, `coordinator.py` orchestrates and does not compute; they moved to `flow_meter.py`, which owns measured heat, and the coordinator class got 7 lines smaller.

## Head

`1e04be57142ea615b82aaaf618d0ff2fbed6e5b5`, merge base `50af6174f53c0f9bec3f705c3a4bb99615f71acc` (origin/main at the time of measuring; `git merge-base origin/main HEAD`).

## Mutation proof

Each mutant applied to a detached worktree of the head and `PYTHONPATH=tests/hastub python3 tests/features.py` run in full (a one-off driver, not kept: each mutant is the one-line edit named); every one goes red:
- `flow_meter.read_heat_output_kw`'s `if cap.measured_heat:` to `if False:` -- 5 failing: "a configured heat meter answers in kW, and outranks the flow meter's estimate ...", "a power and a frequency signal do not switch the heat meter off ...", "an unusable heat reading is absent, and the flow meter is not consulted in its place ...", "on an unmetered switch-plus-setpoint install both interval learners replay the measured heat ...", "where the learner already runs it replays the measured heat, and a stale heat reading freezes it ...".
- `_fold_measured_cop`'s `if heat_kw is None and (refusal := ...)` to `if (refusal := ...)` -- 1 failing: "a measured heat is not judged by the commanded-ratio gates ...".
- `cop_evidence`'s `if heat_kw is None:` to `if True:` -- 3 failing: "without a heat reading the evidence is the commanded inference, bit for bit ...", "a measured COP holds cop_scale at the pump's own 0.9 across the weather ...", "a measured heat is not judged by the commanded-ratio gates ...".
- `space_reference_cop`'s `if heat_kw is None or supply_c is None:` to `if True:` -- 2 failing: "a measured COP holds cop_scale at the pump's own 0.9 across the weather ...", "a metered interval is judged at the supply it ran at ...".
- `_fold_capacity_envelope`'s `not (nameplate or heat_kw is not None)` to `not nameplate` -- 1 failing: "a measured partial-load heat seeds or raises its bucket, never counts and never lowers it ...".
- `replay_freeze`'s `return None if lifted else frozen` to `return frozen` -- 2 failing: "the unmetered freeze lifts only for a heat-metered interval with a reading", "on an unmetered switch-plus-setpoint install both interval learners replay the measured heat ...".
- the house learner's freeze keys without `CONF_THERMAL_POWER_ENTITY` -- 1 failing: "where the learner already runs it replays the measured heat, and a stale heat reading freezes it ...".
- the COP fold's freeze keys without `CONF_THERMAL_POWER_ENTITY` -- 1 failing: "a configured heat meter with a stale reading freezes the COP fold rather than falling back to the commanded inference ...". (This mutant survived the first test set at `a727309a5`, ALL 4367 passing; the check "a configured heat meter with a stale reading freezes the COP fold rather than falling back to the commanded inference ..." was added for it.)

## Null control

The unmodified tree (merge base) ignores a heat reading entirely: the harness below feeds both trees the same heat-metered direct plant, and the base's `cop_scale` walks with the weather exactly as its commanded inference does. An install without the key: every coord_* golden capture is byte-identical to the merge base (`env_drift.py --all`, below), which includes the fully metered `coord_all_features`; the harness's `commanded` arm prints bitwise-identical scales at both trees.

## Figures

- `python3 dev/audit/harnesses/r10_thermal_power_option.py 50af6174f53c0f9bec3f705c3a4bb99615f71acc` -- a direct plant at 0.9 x the model's law at a weather-curve supply, 400 folds at each of 7 outdoor points: head `metered` spread 0.0000 with every scale within 6e-7 of 0.9; base `metered` spread 0.1321 (0.6356 at -15 degC to 0.7677 at 12 degC), the defect; `commanded` spread 0.1321 and bitwise identical at both trees (null control: had the commanded path moved, the reprs would differ). Both ends of the input range: `first_fold` (zero evidence, one fold per point) moves the scale by at most `COP_LEARNING_MAX_STEP` per fold (0.997 after the first); `clamp` (a meter reading 4 x the law) stops at `COP_SCALE_MAX` 1.6 at every point, at both trees.
- `PYTHONPATH=tests/hastub python3 tests/features.py` -- ALL 4368 FEATURE CHECKS PASSED at the head; the new block's checks each assert a null control in their own predicate.
- `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 50af6174f53c0f9bec3f705c3a4bb99615f71acc` -- NO UNCLAIMED DRIFT over 56 scenarios, NO STALE FIXTURE; the one moved fixture is the float-free `config_flow` (3 leaves, the new field's keys), re-recorded with `tests/golden.py --record --only config_flow` and claimed in `tests/golden/claimed_drift.txt`.
- `python3 tests/structure.py` -- STRUCTURE RATCHET PASSED after recording `class_excess_loc` 18217 -> 18210 and `max_class_loc` 8457 -> 8450 (the coordinator class shrank; reason in the recording commit's message). No budget raised.
- `python3 tests/closure.py select --diff 50af6174f53c0f9bec3f705c3a4bb99615f71acc --workdir <tmp>` -- `MODE: SCOPED -- 30 script(s) run, 3 scoped out`; the scoped run (`GATE_SCOPE=auto GOLDEN_MODE=drift tests/run.sh`) went red on three scripts, all repaired on this branch and re-run green: `tests/typing_ruler.py` (two no-any-return in `flow_meter.py`, now rc=0), `tests/env_drift.py --all` (config_flow, above) and `tests/entities.py` (two ledger rows pinning lines this branch rewrote, deleted; the two checks still red, "gate-sweep.yml: on CI's completion ..." and "graders-head-copy's delivery_status step ...", fail identically at the merge base on this box, 2 of 2425 at both trees).
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` -- ALL 112 HARNESS HEADER CHECKS PASSED; `option_doc_coverage.py`'s header moved 200 -> 201 and 233 -> 234 for the new options field and its `docs/configuration.md` row.
- `python3 tools/audit/archscore/score.py --diff 50af6174f53c0f9bec3f705c3a4bb99615f71acc HEAD` -- `Architecture score: dS +0.0000 NULL`.
- Seams (fixer step 8): the instrument is `tools/pr/ci_predict.py --base origin/main` for the mutation sites (17, each dispositioned below) and the R8-P3 humidity barrier in `tests/features.py`, whose file set this diff widens to `flow_meter.py` so the two COP calls that moved there stay under the rule (both entries are live-condition calls at the current outdoor temperature, as the coordinator entry they replace was).

## Architecture score

Architecture score: dS +0.0000

## Unpinned sites

- custom_components/heatpump_optimizer/coordinator.py:4878 GUARD_OFF: pinned by mutation-autofix (the freeze guard's earlier pin was killed by tests/features.py)
- custom_components/heatpump_optimizer/coordinator.py:4927 BOOLOP: pinned by mutation-autofix (an `or` leaves `refusal` unbound on the commanded path)
- custom_components/heatpump_optimizer/coordinator.py:4927 GUARD_OFF: pinned by mutation-autofix (the tracking-gate check refuses a mutant that never refuses)
- custom_components/heatpump_optimizer/coordinator.py:9113 CMP_BOUND: pinned by mutation-autofix; value check "a command at exactly 95 % of nameplate is still nameplate evidence, as before"
- custom_components/heatpump_optimizer/coordinator.py:9114 CMP_BOUND: pinned by mutation-autofix; value check "a nameplate of 0.1 kW or less keeps the envelope empty, measured heat or not"
- custom_components/heatpump_optimizer/coordinator.py:9114 GUARD_OFF: pinned by mutation-autofix (the partial-load censoring check)
- custom_components/heatpump_optimizer/coordinator.py:9123 CLAMP_DROP: pinned by mutation-autofix; value check: a lower measured heat leaves a seeded bucket at [5.0, 7]
- custom_components/heatpump_optimizer/flow_meter.py:61 GUARD_OFF: pinned by mutation-autofix (killed in the mutation proof above)
- custom_components/heatpump_optimizer/flow_meter.py:64 BOOLOP: pinned by mutation-autofix (a negative reading is then returned; the unusable-reading check)
- custom_components/heatpump_optimizer/flow_meter.py:64 CMP_BOUND: pinned by mutation-autofix; value check "a heat meter reading zero is a measured 0 kW, not absent"
- custom_components/heatpump_optimizer/flow_meter.py:64 RETURN_DEL: pinned by mutation-autofix (every reading checks a value)
- custom_components/heatpump_optimizer/flow_meter.py:97 RETURN_DEL: pinned by mutation-autofix (every reason then lifts; the replay_freeze check)
- custom_components/heatpump_optimizer/flow_meter.py:115 GUARD_OFF: pinned by mutation-autofix (killed in the mutation proof above)
- custom_components/heatpump_optimizer/flow_meter.py:117 RETURN_DEL: pinned by mutation-autofix (the evidence check unpacks it)
- custom_components/heatpump_optimizer/flow_meter.py:119 RETURN_DEL: pinned by mutation-autofix (the evidence check unpacks it)
- custom_components/heatpump_optimizer/flow_meter.py:136 GUARD_OFF: pinned by mutation-autofix (killed in the mutation proof above)
- custom_components/heatpump_optimizer/flow_meter.py:138 RETURN_DEL: pinned by mutation-autofix (the reference check compares its value)

## Red checks

none

## Forward-carry

none

## Friction

none
