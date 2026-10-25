# R10-HEAT-METER design note (designer seat)

This is the group's architect note, extended (`dev/governance/roles/designer.md`). It lives on `design/R10-HEAT-METER` only and is never merged. Issue #2261, owner request 2026-10-15. **No finder harness: owner report.**

**Revision 2** answers round 2 (`design-verdict/R10-HEAT-METER` at `636a85b3`, revise on `e23ace899`, points A-D):
- A: the span closes on elapsed time.
- B: per-cycle gates are ANDed across the span for the learners.
- C: a point sample is never time-split.
- D: no store migration.

**Revision 1** answered the design review `design-verdict/R10-HEAT-METER` at `fabd19b8a`, which returned revise on `04de6ae7f` with points 1-5. It also follows two sets of orchestrator rulings under mandate 6329234399:
- Combination modes fall back to #2753's whole-unit treatment.
- The mode entity becomes optional and the refusal goes.
- Adding a meter does not wipe the scale unless the replay will use the meter.
- "Clamp means reset" is kept, routed as a carry.
- The fixer is held until #2753 merges.

**Read at.** `origin/main` `da12aa37dee15b9e9567bd6c848493436f2592dd`, and R10-THERMAL-POWER-OPTION's head `8a133f390df73f560b588ab570aedbab95ee5ae1` (PR #2753, open, merge base `da12aa37d`). Symbols marked "(#2753)" exist only at that head.

**Hold.** Dispatch no fixer until #2753 merges. Then re-check every "(#2753)" name at its merge SHA within the 1 h box (step 9), or report `revalidation failed`.

## Premise, measured

- **At main, the premise holds.** `git grep CONF_THERMAL_POWER_ENTITY da12aa37d -- custom_components` returns nothing.
- **At #2753's head, it is superseded on the consumer side.**
  - `read_heat_output_kw` in `custom_components/heatpump_optimizer/flow_meter.py` answers a thermal key first, with no fallback.
  - `cop_evidence` (#2753) folds heat over electricity and skips `judge_ratio`.
  - `space_reference_cop` (#2753) and `replay_freeze` (#2753) are wired in.
  - `_interval_measured_heat_kw` replays measured heat on commanded space-only intervals.
  - `_fold_capacity_envelope` samples at all loads.
- **What is still owed, measured at `8a133f390`:**
  1. No energy counter, and no counter delta anywhere.
  2. A mixed interval is refused, never split.
  3. Nothing keeps time on the mode.
  4. Adding a meter re-anchors nothing: `heat_loss_basis({power, thermal}) == "metered"` (venv-ha probe).
  5. The ledger and the diagnosis triple split by the plan.
  6. Splitting by time share cannot give a per-mode COP. Splitting H and E by any share gives H/E on both sides (probe: 3.0/3.0 at s = 0.25, 0.5 and 0.75).

## Size verdict: L, conditional on #2753

#2753 (size M) is 173+/84- production lines over 8 files (`git diff --numstat da12aa37d...8a133f390 -- custom_components`) and delivers the consumer side. What remains is a pure module, two wiring calls, span-aligned sampling for counter installs, four call-site swaps to one owner, and one basis entry. The reviewer confirmed L against #2753's head, and XL against main alone.

## Selector semantics (review point 1)

`CONF_HEAT_PUMP_MODE_ENTITY` is the pump's mode **selector**: what it may do, never what it is doing (`custom_components/heatpump_optimizer/pump_mode.py`). Under a single-duty selector (`heat`, `DHW`, `cool`), the pump cannot run the other duty, so the selector's dwell is the duty split. Under a combination selector (`HEATDHW`, `COOLDHW`, `concurrent`), the duty is unobserved: the pump charges hot water on its own initiative and the selector does not change.

The mode source of each segment:
- An observed single-duty mode, read or written by the arbiter (`mode_owned`, its step decision), is **observed**.
- Everything else falls back to **#2753's whole-unit rule** for that interval, bit-identical to #2753, by ruling. "Everything else" covers a combination mode, owned or not, an unobserved or absent mode, and a `MODE_SOURCE_LAST_GOOD` reading.
- An interval is observed only when every segment in it is.

**Activity signal: rejected.** A rising `CONF_DHW_TEMP_ENTITY` names a charge but not its share. A flat tank does not exclude a charge masked by a draw. Under the ruling it could only refine the combination arm, which takes #2753's rule anyway.

**The mode entity is optional.** `heat_meter_needs_mode` is removed: without the mode entity, every interval takes #2753's rule. That is the owner's request, overruled under the mandate; record it so in the pull request.

## Owning seam

**The new module `custom_components/heatpump_optimizer/heat_energy.py` (would be new) owns interval energy accounting and attribution.** It is pure and has no `homeassistant` import. It holds:
- `CounterDelta`: one counter's fixed-span delta rule.
- `ModeDwell`: segments with `(start, duty, observed)`, and `shares(since, until) -> DwellShares | None`. `None` means some segment in the window is not observed.
- `HeatEnergyMeter`: the per-coordinator holder of the heat counter, the electric counter (`CONF_ENERGY_ENTITY`), the dwell and the span state.
- **Attribution, one owner** (review point 4): `attribution(shares, plan_split) -> Attribution(space_frac, dhw_frac, observed)`.
  - With `shares` it returns the observed fractions; with `None`, the caller's `plan_split` fractions.
  - Its consumers are pure functions next to it:
    - `space_heat_kw(heat_kw, a, integrated)`:
      - Observed with `integrated` (a counter span's mean, energy over the same window as the dwell): returns `heat_kw * space_frac`.
      - Observed with a point source (thermal kW, flow): returns `heat_kw` only when `dhw_frac == 0`, else `None`. A point sample is never time-split (point C).
      - Unobserved: #2753's rule, `heat_kw` iff `dhw_frac == 0 and space_frac > 0`, else `None`.
    - `cop_duty(a, share_limit)`: space, DHW or blended, against the caller's `_COP_CURVE_SHARE`.
    - `dhw_share(a)`.

**Callers only:**
- `flow_meter.read_heat_output_kw`: the single heat answer, which gains the counter source.
- `pump_signals.read`: adds `mode_changed_at` from `last_changed`.
- `thermal_model.heat_loss_basis` and `const.HEAT_LOSS_BASES`.
- Five coordinator sites, which compute nothing. Each passes the plan split it reads today, so the unobserved arm is unchanged:
  - `_interval_measured_heat_kw`: commanded split;
  - `_cop_reference_curve`: commanded split;
  - `_accumulate_energy`: `pending` split;
  - `_settle_interval_diag`: `pending` split;
  - the re-anchor.

## Shape

- **Key.** `CONF_HEAT_ENERGY_ENTITY = "heat_pump_heat_energy_entity"` (kWh, `reader.read`).
  - Its max age sits beside `CONF_ENERGY_ENTITY`'s, and its on-change limit is `math.inf` (INPUT-STALENESS carry).
  - It gets an `_F` row in `entities_metering`, with strings in en and sv.
  - `probe_install(...).measured_heat` is true for either heat key.
- **Precedence.** Counter, then thermal kW, then flow meter. A configured source that reads unusable gives `None` and never falls back. The counter wins because it integrates cycling, where the thermal key is a point sample.
- **Counter rule** (review point 2; probe `dev/programme/designs/R10-HEAT-METER-probes/fixed_span_probe.py`).
  - **The span closes on elapsed time, not on a cycle count** (point A). The figure is `elapsed_h`, measured between read instants since the span's first reading.
    - It closes at the first read with `elapsed_h >= max(HOUSE_LOSS_MIN_SAMPLE_HOURS, HOUSE_LOSS_MAX_SAMPLE_HOURS - interval_h - SPAN_CLOSE_ALLOWANCE_H)`.
    - A span with `elapsed_h > HOUSE_LOSS_MAX_SAMPLE_HOURS` is refused and re-baselined. That is the same strict comparison as the learner's own check in `_async_learn_house_heat_loss`, so a span the meter accepts never reaches that check out of range.
    - `SPAN_CLOSE_ALLOWANCE_H = 0.05` (3 min) is the refresh-drift tolerance. Home Assistant schedules a refresh after the previous one ends, so the cadence is the interval plus the solve time, and an event-driven refresh lands at any time.
  - At span close, `delta = counter_now - counter_at_span_start`, divided by the measured `elapsed_h`.
  - Probe `dev/programme/designs/R10-HEAT-METER-probes/time_span_probe.py`. The drift is the interval plus the solve time: 2.5 s, the largest `solve_cpu_ms` measured in the tree, in `dev/audit/rounds/round10/catchup/d9/out/cont_fuse.txt`; 25 s as a Pi-class x10 allowance; and a 120 s stress row. Event-driven refreshes land at a 5 % rate per cycle.
    - The time rule with the allowance accepts all 20000 spans in every row, with `dt_h` 0.950-1.483.
    - Without the allowance, it refuses up to 128.
    - Null: the K = 3 cycle rule accepts 0 of 20000 at every solve time without events, which is the reviewer's finding.
    - The owner's bundle, which would give the real cadence, is not in this container. The fixer re-measures there.
  - A span is accepted or refused on an independent figure, never on the quantised delta itself. The test is `q / expected_kwh <= HEAT_RESOLUTION_EPS`, where:
    - `expected_kwh` is the electric counter's span delta times the reference COP, or with no electric counter the commanded energy times the modelled COP;
    - `q` is the smallest positive step the counter has shown, and the span is refused until one is seen.
  - Refused spans re-baseline at the close. A negative delta (reset) or one above `p_max_thermal * span_h * HEAT_COUNTER_SLACK` (rollover) refuses and re-baselines.
  - Alignment is by read instant (carry dr1-lag-idle): both counters are read in the same cycle, so the paired deltas share instants.
  - Probe, integer-kWh counter, `EPS = 0.5`: 0.6 kW refuses every span; 1.5 kW reads 1.500 (sd 0.289); 2.2 kW reads 2.200; null 3.0 reads 3.000. #04de6ae7f's rule read 0.6 kW as 2.000 (the reviewer's probe).
- **Span-aligned learners** (counter installs only).
  - Each learner keeps its span-start snapshot (state and time) in `HeatEnergyMeter`. At span close, it replays from that snapshot over `elapsed_h` with the span's `space_heat_kw`.
  - **Per-cycle gates, ANDed** (point B). Every cycle still runs `_async_learn_house_heat_loss`'s and the lower-floor learner's gate block exactly as today:
    - the freeze (`replay_freeze` over `_learning_frozen`, stale inputs included);
    - the boost freeze;
    - `vent_only`;
    - a `None` `_interval_space_power`;
    - the min/max `dt_h`.
    Each learner ANDs its outcome into its own `span_clean` flag. One gated cycle refuses that learner's span.
  - **Ventilation detector cadence: unchanged, per cycle.** The per-cycle path keeps snapshotting every cycle and keeps replaying, so the detector gets its residual each cycle with the inputs #2753 gives it (draw-inferred heat on a counter install).
  - **Which path folds the scale.** Until the basis is earned, the per-cycle path also folds the scale, as #2753 does. The first accepted span's fold earns the basis, and the void path wipes the per-cycle evidence. From then on, on a counter install, the per-cycle path feeds the detector only, and the scale folds at span close alone. No window is counted twice.
  - The COP fold runs at span close on the paired deltas. Each per-cycle gate (frozen, frost, distorted, duty floor) is ANDed across the span: one gated cycle refuses the span.
  - With a thermal-kW or flow source, sampling stays per cycle, as #2753 has it.
- **COP.** On a counter span, the electrical figure is the electric counter delta. With no electric counter, the fold refuses with `COP_REFUSED_UNALIGNED = "unaligned_meters"` (`custom_components/heatpump_optimizer/accuracy.py`); the house replay still uses the heat. `cop_evidence` (#2753) is called unchanged.
- **Re-anchor, earned not configured.** `HEAT_LOSS_BASES = ("commanded", "metered", "measured_heat")`.
  - The learner's live basis becomes `measured_heat` at the **first fold whose replay used a non-`None` `space_heat_kw`**. That fold runs the existing void path (`heat_loss_basis_voids`, then `reanchor_heat_loss` at confidence 0) before it applies.
  - A meter the replay never uses, such as an install whose selector stays a combination mode on mixed plans, keeps its scale.
  - **No store migration** (point D). The earned basis is written to the existing `house_heat_loss_basis` choice field. `_heat_loss_anchors` returns `measured_heat` only when the stored basis is already `measured_heat` and `probe_install(...).measured_heat` still holds; otherwise it returns the configured basis, as today. A missing value reads as not earned.
  - The field's `unread` text in `custom_components/heatpump_optimizer/store.py` still says "re-derived from the configured meters". Per the orchestrator's ruling, store.py is out of `files`, so that text goes stale. See the first note for the fixer.
- **Invariants.**
  - No heat key and no mode entity: bit-identical.
  - Thermal key with no observed single-duty mode: #2753's figures.
  - A refusal is `None` or a code, never 0.

```
cycle: reader -> HeatEnergyMeter.observe_counters(heat, elec, at) -> span close? IntervalEnergy | refusal
       observe_water -> read_heat_output_kw: counter > thermal kW > flow (no fallback)
       pump_signals.read(+mode_changed_at, mode_owned) -> HeatEnergyMeter.observe_mode -> ModeDwell
sites: attribution(dwell.shares(span), their plan split) -> space_heat_kw | cop_duty | dhw_share
```

## Alternatives rejected

- **Counter state in `flow_meter.py`:** its functions are stateless, and the dwell is mode accounting.
- **A cycle-count span** (K cycles): refused against the learner's strict `dt_h > MAX` bound on every span (null rows of `time_span_probe.out`).
- **Per-cycle counter deltas,** with zero refused and the baseline advanced: a selection on the quantised value, so 0.6 kW reads 2.0 (verdict probe).
- **Keep the baseline and accept at the first quantum:** the stopping rule still biases. `dev/programme/designs/R10-HEAT-METER-probes/first_quantum_probe.py`, N=1: the mean of span means reads 1.667 at 1.5 kW.
- **Refuse combination modes:** strictly worse than #2753 on every such install (review point 1).
- **Void on configuration:** it wipes the scale for a meter the replay may never use (ruling).
- **The policy at each site:** three owners of one concern (review point 4).
- **The recorder for dwell:** a database read per cycle (D9).

## Sibling sites

`git grep -nE "_commanded_split\(\)|planned_dhw / planned_total|space_share\(" -- custom_components` at `8a133f390` returns these sites.
- **In scope:** `_interval_measured_heat_kw`, `_cop_reference_curve`, `_accumulate_energy` and `_settle_interval_diag` (review point 3). The last apportions the diagnosis triple by the same `dhw_share`, so its docstring stays true.
- **Out of scope:**
  - `_fold_flow_lift` and `_commanded_power`: these concern the plan's ask.
  - `_interval_space_power` and `_propagated_slab`: electric replay without a heat meter, a behaviour no finding names.
  - `draw_range.fold` and `draw_range.space_share`'s own use in `space_draw_kw`: the draw evidence, which belongs to COP-GATE.

## Evidence plan, by file

- **Failing tests first** in `tests/features.py`:
  - exact fold on a known-COP plant;
  - null: heat equal to COP times electric keeps the scale;
  - a planted reset is refused;
  - a planted rollover is refused;
  - a planted integer counter at 0.6 kW is refused and at 1.5 kW reads unbiased over N spans;
  - a jittered cadence plus one event-driven cycle closes the span inside `[MIN, MAX]`;
  - a span with one frozen, boosted or `vent_only` middle cycle is refused for that learner;
  - the detector still steps every cycle on a counter install;
  - a `heat` then `DHW` interval on a thermal-kW install gives `None`, not half;
  - single-duty `heat` then `DHW` inside one span splits at `last_changed`;
  - an owned single-duty step counts as observed;
  - a combination mode and a last-good mode both reproduce #2753's figure;
  - precedence and no fallback (mirroring #2753's M1);
  - the basis upgrades only on the first measured-heat fold;
  - the ledger and the diagnosis triple share one split;
  - a dead counter re-reports first (INPUT-STALENESS carry).
- **Harness:** `dev/audit/harnesses/r10_heat_meter.py` (would be new), ported from `dev/audit/harnesses/r10_thermal_power_option.py` (#2753), run at the base and at the head.
- **Goldens** (review point 5):
  - `tests/golden/config_flow.json` moves with the new `_F` row, claimed as `config_flow` in `tests/golden/claimed_drift.txt`, as #2753 claimed it.
  - The coordinator goldens `coord_all_features`, `coord_dhw`, `coord_grid_fee`, `coord_minimal` and `coord_two_zone` all publish mode `"Unknown"` (unobserved; `mode_observed` is absent from every one), so attribution takes the plan arm and none of them moves. The fixer re-checks this.
- **Mutation targets:**
  - the span-close condition;
  - the `q / expected_kwh` bound;
  - the reset branch;
  - counter-first precedence;
  - the `observed` test in `attribution`;
  - the `last_changed` split;
  - the earned-basis upgrade;
  - the time-close comparison;
  - the `span_clean` AND;
  - the `integrated` branch in `space_heat_kw`.
- **Classification:** `heat_energy.py` goes into a measured closure.

## Hot files and serial position

`files` grows by `custom_components/heatpump_optimizer/heat_energy.py` (would be new), `custom_components/heatpump_optimizer/pump_signals.py`, `custom_components/heatpump_optimizer/thermal_model.py`, `custom_components/heatpump_optimizer/accuracy.py`, and `custom_components/heatpump_optimizer/translations/sv.json`. Open groups on these files are R10-ARCH-SHAPES (already before) and R10-UX-HEALTH (after).

Serial positions:
- `config_flow.py`: 2 of 3.
- `const.py`: last.
- `coordinator.py`: after THERMAL-POWER-OPTION, before COP-GATE.

## Notes for the fixer

- Carry: R10-RATIO-ANCHOR. On #2698's clamp-reset item, the decision under mandate 6329234399 is **keep "clamp means reset"**. It is orthogonal to this group: the void path enters `reanchor_heat_loss` at confidence 0, where both clamp branches (`if a and not`, `if b and not`) are skipped. The re-measurement at this group's merge base stays with the fixer.
- Carry: dismissed: unobservable with one meter under a combination selector. The SAV attribution residue: the observed split fixes single-duty intervals, and under a combination selector the plan split and its docstrings stay.
- Decision: orchestrator. The verdict at `636a85b3` keeps store.py in `files` for one string, the `unread` text of `house_heat_loss_basis`, which becomes "earned at the first measured-heat fold". The orchestrator's ruling removes store.py. If it stays out, that text is stale after this group. The recommendation is to re-admit store.py for that one string, with no version bump and no migration.
- Carry: R10-HEAT-METER (item dr1-basis-mix). After the upgrade, on a thermal-kW install, an interval with `None` heat still replays draw-inferred heat under `measured_heat`, as #2753 does. On a counter install, the scale folds only at span close, so there is no mix. Say so in `HEAT_LOSS_BASES`'s comment, because freezing them would be worse than #2753 on combination selectors.
- Carry: R10-HEAT-METER (item dr1-store-choice). `house_heat_loss_basis` is a `Domain("choice")` (`custom_components/heatpump_optimizer/store.py`). Test a downgrade reading `measured_heat` and the schema check's acceptance of the third choice.
- Carry: R10-HEAT-METER (item dr1-lag-idle). Align on the read instant, never on `last_updated`. An idle counter is old and correct.
- Carry: R10-HEAT-METER (item dr1-last-good). A `MODE_SOURCE_LAST_GOOD` reading's `last_changed` is the stale state's own, so the segment is unobserved.
- Carry: R10-COP-GATE. "Has a heat meter" is `probe_install(...).measured_heat`, for either heat key. Render and do not override `unaligned_meters` and the counter refusals. On a counter install, COP folds at span close, not per cycle.
- Carry: R10-UX-HEALTH. New input rows for `heat_pump_heat_energy_entity` and `heat_pump_thermal_power_entity`, labelled from `strings.json` `entities_metering`. A Health string for `unaligned_meters`. The mode entity is optional; no refusal string.
