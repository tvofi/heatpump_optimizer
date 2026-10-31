# R10-COP-GATE part D: the learned top reaching the plan (architect note)

Code read at `origin/main` 4822c8f9b7f7ca6201cea05a9c80f7797e5f56a6 and at part 6's handoff `handoff/r10-cop-gate-p6` f40be9c9756ba7cc84ba7a5daa77e1ba449b0b05 (main's code plus part 6; no production commit on main since part 6's base be7584c49). Scope: carry 12 only. Probe: `dev/programme/designs/R10-COP-GATE-D-probes/band_probe.py`, output beside it, run at f40be9c9. Names in *italics* are proposed and do not exist yet.

## Ruling on scope (why D needed one)

Carry 12 names the behaviour: the reference's learned top must reach "the surfaces that publish and use it". The user is the solve, so D changes what the plan books. That contradicts the group's architect note ("a published reason, no threshold change"). It is not a two-owner change: the owner is `draw_range.py`'s answer to "what range may a solve book", and the coordinator and sensor only wire it. **The orchestrator owes three things before a fixer starts.** (1) An architect note for part D naming this seam. (2) `custom_components/heatpump_optimizer/draw_range.py` added to the group's `files`. (3) An `after` edge on R10-CEILING-PROBE. **No threshold changes**: D reads `AGREE_TOLERANCE` and CEILING-PROBE's twelve-sample and 45-day constants unchanged, and every COP gate keeps reading the hub's configured figures.

**Producer status (a gating fact, not a stop).** The learned top does not exist yet. CEILING-PROBE's accessor (*learned_max_kw()* on `DrawRange`, per its note at `design/r10-ceiling-probe` 2212054e9) is absent from main and from f40be9c9: *git grep learned_max_kw* finds nothing. Its design review closed the reader seam ("The reader is closed", `design-verdict/R10-CEILING-PROBE` e8da829f1), so D can design against that interface. D cannot be built or measured until CEILING-PROBE merges.

## Owning seam and function boundaries

- **Owner, `draw_range.py`**: one new pure function *solve_band(draw, params, cap)*. It returns a frozen ruling with *max_kw* (`float | None`), *min_kw*, `source` and `reason`, plus `as_dict()`. It takes no coordinator. `planned_range` and `diagnostics_view` keep their behaviour. `planned_range`'s docstring ("a solve may book") is corrected to say diagnostics only: no solve has read it since it landed (22e16ea81).
- **Wiring, `coordinator.py`**, all three edits in place: (a) `_solve_hubs` builds the params copy from *draw_range.solve_params(ctx._thermal_params, ...)* instead of `copy.deepcopy(ctx._thermal_params)`; (b) `arbiter_inputs` passes the same *solve_params(...)* as `params=`; (c) `_learning_view` publishes *solve_band(...).as_dict()* under *pump_max_power*.
- **Publish, `sensor.py`**: `ModelStatusSensor` copies *pump_max_power* from the payload. `diagnostics_view` adds the same four keys.
- **Not touched**: `pump_arbiter.py`, because `_band_kw` already reads `inp.params`, and `optimizer.py`.

## The rule

Let `cfg_min` and `cfg_max` be the hub's configured figures and `L` CEILING-PROBE's raw median, which is `None` below twelve samples or 45 days after the newest sample.

| case | *max_kw* booked | `source` | `reason` |
|---|---|---|---|
| `cap.plan_writes_power()` | `cfg_max` | `configured` | `plan_writes_power` (the draw is the plan's echo) |
| fewer than twelve store samples | `cfg_max` | `configured` | *awaiting_probe* (+ sample count) |
| store lapsed | `cfg_max` | `configured` | `lapsed` (+ newest sample date) |
| `L >= (1 - AGREE_TOLERANCE) * cfg_max` | `cfg_max` | `configured` | *not_below_configured* (+ `L`) |
| `L < (1 - AGREE_TOLERANCE) * cfg_max` | `L` | *ceiling_probe* | *measured_below_configured* (+ `L`, date) |

*min_kw = min(cfg_min, max_kw)*. The bottom end never moves, the same rule `planned_range` applies on a duty-cycling install. The ruling never raises the top: a learned top above the configured one books the configured one. That books less heat, never fictional heat, which is CEILING-PROBE's own rationale. **Fallback** is every `configured` row: the solve's params are the hub's figures byte for byte. The published payload always carries *configured_max_kw*, *planned_max_kw*, `source` and `reason`, so a plan booking below the nameplate always shows why, and one that does not says which evidence is missing.

## Invariants (each one has a test)

1. **The hub never carries the learned top.** It goes only into the solve copy and the arbiter's input, never through `_model_corrections` and `_publish_params`. Probe P1: `DrawRange.observe` re-keys on the configured pair it is handed, so one fold keyed on `(1.0, 3.0)` cuts a 60-sample window to 1 (null: 61 folds on the configured key keep 61). The same rule keeps three things on the configured figures: `nameplate_power_floor_kw`, the COP duty floor, and the system-identification probe's commanded power (a probe at the learned top would measure its own clamp).
2. **The arbiter maps by the solve's band.** Probe P2: a 3.0 kW plan step mapped on the configured (1.0, 5.0) band writes 42.50 degC, not the 55.0 ceiling. On (1.0, 3.0) it writes 55.00 (null: 5.0 kW on the configured band writes 55.00). Without (b), the plan's top step never commands full power and the window's `full` evidence disappears.
3. **One function, two reads, one answer.** The store changes only on probe-routed intervals (CEILING-PROBE re-cut B) and at lapse, never on a plan interval. So the solve and the arbiter passes that follow it read the same ruling. Test: a non-probe fold between the two leaves *solve_band* unchanged.

## Alternatives, and why each lost

- **Publish through `_model_corrections` into the hub.** It lost on invariant 1: every fold would wipe the window and the latch (P1), and it would move the COP gates' nameplate figures, which is a threshold change.
- **Reshape `planned_range` into the one answer, latched window included.** It lost because it switches on a second behaviour no finding in this group names: the window clamp, including a raised bottom end on installs that cannot duty-cycle. It would also move 5 killed-mutant pins under `tests/mutation_ledger/killed_by/draw_range.py/` and 8 `tests/features.py` sites.
- **Carry the band on the plan's result for the arbiter.** It lost because it adds a field to the optimizer's result class and a builder line inside `HeatPumpOptimizer` (`class_excess_loc` has no headroom) to cover a drift invariant 3 already rules out.
- **`min(store top, window top)`.** It lost because the window latch never releases within a configuration (`draw_range.py:19-31`, "So it latches for the configuration it judged"), so one low window top would outvote every later probe measurement.

## The `_propagated_slab` lead: not absorbed

The lead is the same family of bug (plan split against observed dwell), but it has a different owner and consumer. It attributes a metered draw to the slab replay, through the attribution owner part 6 uses (`heat_energy.meter_of(coord).attribution`, `ran_hot_water`). D rules the band a solve books. Absorbing it would give D two owners. It belongs to part 6's seam: a part E after part 6 merges, measured first on the switch-back dwell with the all-space null, as the carry states.

## Sibling sites

`git grep -n max_electrical_power -- custom_components` lists every site. The fixer classifies each one as either (i) reading the solve's params, which takes the learned top (the optimizer, the quiet-window caps and price tiles in `_solve_record`, the what-if solve built by `_solve_hubs`, and away recovery when it is handed the solve's model), or (ii) reading the hub, which stays configured by invariant 1 (the fold's key, the COP gates, system identification, immersion detection, the capacity envelope, energy accounting, fixed mode). Each line of the classification goes in the body. `_max_pump_rise` and `battery.py` read the hub: list both as out of scope with the reason.

## Evidence plan

- **Finder's harness**: `evidence/r3_probe_reader.py` at `design-verdict/R10-CEILING-PROBE` 3a261d864, the measurement carry 12 cites. Commit it under `dev/audit/harnesses/` as the part's own harness (r10_cop_gate_top), extended to print *solve_band* and the solve params' top. Run it at the merge base and at the head. Expected at the base: the store's median is published, and the solve and the arbiter book `cfg_max`. Expected at the head: eleven store samples book `cfg_max` and twelve book `L`.
- **Failing tests first** (`tests/features.py`), on a synthetic pump with a 3.0 kW real maximum configured as (1.0, 5.0): every row of the rule table; the twelve/eleven pair; invariants 1-3; and the published four keys on the model status sensor and in diagnostics.
- **Controls**: the known-maximum pump recovered within 0.1 kW at both CEILING-PROBE step lengths. This catches the 2.25-vs-3.0 bias carry 12 names; if CEILING-PROBE's interval-owned pairing regressed, D would book a top 25 % low. A gate-held draw above idle leaves the band unchanged.
- **Nulls**: a store within 15 % (4.5 of 5.0) gives a byte-identical `power_schedule` at base and head. So do a `plan_writes_power` install with a full store, and a fresh install with no store. Every golden fixture has no store, so no golden may move; one that moves is a defect, never claimed. Flat-price arm: the clamp is the same under a flat price. The body states booked heat at the top step, not savings, and claims no cost figure.
- **Mutation targets**: the 15 % comparison, the twelve-sample read, the `plan_writes_power` branch, the *min_kw* rule, and both wiring sites (hub instead of copy, arbiter on the hub).

## Hot files and serial order

`coordinator.py`: R10-LEARNER-ETA (PR 2775) and R10-HEAT-METER (PR 2854) are done, so D waits on neither. Part 6 (open, f40be9c9) edits `_interval_space_power` and `_record_accuracy`, which are disjoint from D's three lines. D still starts from part 6's merge, by the architect note's rule. R10-CEILING-PROBE (unbuilt) edits `draw_range.py`, `coordinator.py` and `sensor.py` and is D's producer. **Order: part 6 and R10-CEILING-PROBE, in either order, then D.** `sensor.py`'s model status `cop` block came from part 5 and is disjoint.

## Structure ratchet

Every metric sits at its budget (measured at 4822c8f9b; part 6 lowers two of them). D's draw_range addition is module-level: `DrawRange`'s span stays at 194, below the class limit. Coordinator edits (a) and (b) substitute expressions on existing lines, so the class gains nothing. Edit (c) costs one line in `HeatPumpOptimizerCoordinator`, plus one key in the `LearningView` type. **Payment**: move one self-free helper out of the coordinator class to module level, named in the commit body, so the class's net lines stay at or below zero. Re-measure after CEILING-PROBE merges, because it spends coordinator lines too. No budget raise is foreseen.

## Notes for the fixer

- Carry: R10-CEILING-PROBE (item D1). Keep the accessor raw: the median, `None` only below twelve samples or past the lapse. The 15 % rule lives once, in D's ruling, so the published reason can tell *not_below_configured* from *awaiting_probe*. CEILING-PROBE's spike returning `None` for twelve samples at 4.5 kW puts the rule in the accessor; settle this before either fixer starts.
- Carry: R10-COP-GATE (item D2). `draw_range.py`'s module docstring says the plan is clamped to the metered range, but the latched window's band has never reached a solve. D corrects the docstring and does not switch the clamp on. Switching it on is a separate behaviour change, which the orchestrator routes by `finding-propagation.md`.
- Carry: R10-COP-GATE (item D3). Before writing to the solve copy, check that replacing the top keeps `ThermalParameters`' own floors (`replace` re-runs them) and that *min_kw <= max_kw* holds in every row.
