# R10-HEAT-METER design note (designer seat)

The group's architect note, extended (`dev/governance/roles/designer.md`). It lives on `design/R10-HEAT-METER` only and is never merged. Issue #2261, owner request 2026-10-15. **No finder harness: owner report.** The evidence is the owner's report as #2261 quotes it.

**Read at.** `origin/main` is `da12aa37dee15b9e9567bd6c848493436f2592dd`. The predecessor that moves this group's ground is R10-THERMAL-POWER-OPTION, PR #2753, open and unmerged, head `8a133f390df73f560b588ab570aedbab95ee5ae1`, whose merge base is `da12aa37d`. Every symbol below marked "(#2753)" exists at that head and not at main. **This note relies on #2753 merging with those names.** If it merges changed, or does not merge, step 9's revalidation applies, and without #2753 the XL size stands.

## Premise, measured

- **At main, the premise still holds.** `git grep CONF_THERMAL_POWER_ENTITY da12aa37d -- custom_components` returns nothing.
- **At #2753's head, it is superseded.** `probe_install(cfg).measured_heat` (#2753) flags a thermal power entity. `read_heat_output_kw` in `custom_components/heatpump_optimizer/flow_meter.py` answers it first, with no fallback. `cop_evidence` (#2753) folds heat over electricity and skips `MeasuredCop.judge_ratio`. `space_reference_cop` (#2753) judges the result at the supply it ran at. `_interval_measured_heat_kw` replays measured heat. `replay_freeze` (#2753) lifts the (c) freeze. `_fold_capacity_envelope` samples at all loads.
- **What #2753 leaves undone.** These seven items were measured at `8a133f390`:
  1. **No energy counter.** `dir(const)` has no `HEAT_ENERGY` key. `CONF_ENERGY_ENTITY` is read into `_measured_energy` and only published. No counter delta exists anywhere: a grep for `delta|rollover|total_increasing` over `custom_components/heatpump_optimizer/*.py` finds only tariff and ledger month rollover.
  2. **A mixed interval is refused, not split.** `_interval_measured_heat_kw` returns `None` whenever the commanded `dhw_kw > 0`.
  3. **The mode is never timed.** No reader of the mode keeps time. `PumpSignals` holds one cycle's mode; `pump_signals.read` sees the state object, so `last_changed` is in reach there.
  4. **The mode entity is not required.** The config flow lets the thermal key be saved without a mode entity. #2753's config-flow diff is two lines: an import and an `_F` row.
  5. **Adding the meter does not re-anchor.** A probe run with the venv-ha interpreter at `8a133f390` gives `heat_loss_basis({power, thermal}) == "metered"`, the same as `{power}` alone. `heat_loss_basis_voids("metered", ...)` is `False`, so adding the meter voids nothing.
  6. **The ledger splits by plan, not by mode.** `_accumulate_energy` splits by `planned_dhw / planned_total` (SAV carry).
  7. **The time share cannot split a COP.** Split H and E by any share s, and both halves read H/E (probe: s = 0.25, 0.5 and 0.75 all give 3.0/3.0). One interval's time share carries no information about a per-mode COP.

## Size verdict: L, not XL, conditional on #2753

#2753 is size M. Its production diff is 173 added and 84 deleted lines over 8 files (`git diff --numstat da12aa37d...8a133f390 -- custom_components`), and it delivered the consumer side: the COP sample site, the house replay, the freeze lift, the envelope and the reference COP. The residual is items 1 to 7: a new pure module, two coordinator wiring calls, four rule changes at existing sites, one config refusal and one basis entry. Estimated at about 1.2 to 1.4 times #2753's production lines, with about eight owed checks. That fits L (6 h in the plan's nominal size table, `tools/plan/replan.py`). XL priced the consumer side twice.

## Owning seam

**The new module `custom_components/heatpump_optimizer/heat_energy.py` (would be new) owns interval energy accounting.** It is pure and has no `homeassistant` import. It holds:
- `CounterDelta`: one cumulative counter's previous reading and the delta rule. It serves the heat counter and the existing electric `CONF_ENERGY_ENTITY` alike.
- `ModeDwell`: a bounded log of `(start, mode_class)` segments, with `shares(since, until) -> DwellShares(space, dhw, blended, other)` summing to 1.

**Callers only:**
- `flow_meter.read_heat_output_kw` stays the single answer to "how much heat this cycle" and gains one source.
- `coordinator.py` holds one `HeatEnergyMeter` per coordinator and calls it at two edges.
- `pump_signals.read` publishes `mode_changed_at`.
- `thermal_model.heat_loss_basis` and `const.HEAT_LOSS_BASES` gain one basis.
- `config_flow.py` gains one refusal.

No concern needs two owners.

## Shape

- **Key.** `CONF_HEAT_ENERGY_ENTITY = "heat_pump_heat_energy_entity"`: a kWh counter, `reader.read`, which already normalises kWh through `normalize_energy_kwh`. Its `INPUT_MAX_AGE_MINUTES` is beside `CONF_ENERGY_ENTITY`'s, and its `INPUT_ON_CHANGE_MAX_AGE_MINUTES` is `math.inf`, because a counter holds while the pump idles (INPUT-STALENESS carry). Add the `_F` row in `entities_metering` and its strings in en and sv.
  - `probe_install(...).measured_heat` becomes true for either heat key. It is the one predicate "has a heat meter", and COP-GATE keys on it.
- **Precedence (carry from #2753).** The heat counter wins over the thermal power entity, which wins over the flow meter. A configured source whose reading is unusable answers `None` and never falls back. Why the counter wins: it integrates compressor cycling over the interval, where a power entity is a point sample. That is the reason `CONF_ENERGY_ENTITY`'s own description gives.
- **Counter rule** (`CounterDelta.observe(value_kwh, at) -> kWh | None`):
  - The first reading, or one after a restart, is `None` and sets the baseline. Nothing persists.
  - A delta below 0 is a reset: `None`, and re-baseline.
  - A delta above the physical bound (`p_max_thermal * span_h * HEAT_COUNTER_SLACK`) is a rollover or a meter swap: `None`, and re-baseline.
  - A delta in `(0, HEAT_ENERGY_MIN_DELTA_KWH)` is quantised: `None`.
  - A delta of exactly 0 counts as 0 only when the electric side reads idle. Otherwise it is `None`: the counter was silent while the pump drew.
  - The baseline advances every cycle, so a span is always one read-to-read cycle.
  - Each literal is justified next to its constant, in the new module.
- **Interval mean.** `heat_kw = delta / span_h`. The house replay uses it only when `span_h` matches the replay's `dt_h` to within one cycle; otherwise it is `None`.
- **COP.**
  - With the counter as the source, the electrical figure is the electric counter's delta over the same read instants, never the point `_measured_power`.
  - With no electric counter, the COP fold refuses with a new code, `COP_REFUSED_UNALIGNED = "unaligned_meters"` in `custom_components/heatpump_optimizer/accuracy.py`. The house replay still uses the heat.
  - Either counter older than `HEAT_COUNTER_MAX_LAG_MINUTES` at the read is also `unaligned_meters`.
  - `cop_evidence` (#2753) is called unchanged.
- **Mode classes.**
  - Each read classes `PumpSignals.mode`: `space` (`space_heat` and not `dhw`), `dhw` (`dhw` and not `space_heat`), `blended` (`concurrent`, or both flags set), and `other` (cooling, or mode unobserved).
  - `pump_signals.read` adds `mode_changed_at` from the state's `last_changed`. A change inside the interval splits it at that instant.
  - The same class at both ends with a change inside the interval means at least two changes, which cannot be split: that span is `blended`.
- **Space heat for the house replay** (`_interval_measured_heat_kw`):
  - Mode observed, with `blended + other == 0`: the replay gets `heat_kw * shares.space`, which may be 0 for an all-DHW interval: the replay's "no space heat".
  - Mode observed with blended or other time: `None`.
  - Mode not observed: #2753's commanded rule, unchanged.
  - `replay_freeze` (#2753) reads this figure, so a DHW charge the mode shows is never replayed as space heat. This closes #2753's carry for every pump whose mode shows the charge.
- **COP bin** (`_cop_reference_curve`). Only when heat is measured and the mode is observed, observed shares replace the commanded split against the existing `_COP_CURVE_SHARE`: space if `shares.space >= 1 - share`, DHW if `shares.dhw >= 1 - share`, otherwise `COP_REFUSED_BLENDED`. Probe 7 is why a mixed interval is not time-split for COP. Installs without a heat meter keep the commanded split, which is COP-GATE's ground.
- **Ledger** (`_accumulate_energy`). When the mode is observed, `dhw_share = shares.dhw + (shares.blended + shares.other) * planned_dhw / planned_total`. With no mode entity it is bit-identical.
- **Required mode.** The options step refuses either heat key without `CONF_HEAT_PUMP_MODE_ENTITY`, with the error key `heat_meter_needs_mode` (strings, en, sv). At runtime, an entry saved before this, or a stale mode, falls back to the not-observed rules above: the result is #2753's behaviour, never a guess.
- **Re-anchor.** `HEAT_LOSS_BASES = ("commanded", "metered", "measured_heat")`, and `heat_loss_basis` returns the third entry when `measured_heat` is set. Adding either heat key then voids the earlier evidence through RATIO-ANCHOR's `heat_loss_basis_voids` path, and `reanchor_heat_loss` runs at zero confidence.

```
cycle: reader --> HeatEnergyMeter.observe_counters(heat, elec, at) --> IntervalEnergy{heat_kwh, elec_kwh, span_h | refusal}
       observe_water --> read_heat_output_kw: counter > thermal kW > flow (no fallback) --> bias.heat_output_kw
       pump_signals.read(+mode_changed_at) --> HeatEnergyMeter.observe_mode --> ModeDwell
learners/COP/ledger: shares(since, until) --> _interval_measured_heat_kw | _cop_reference_curve | _accumulate_energy
```

**Invariants.**
- No heat key and no mode entity: bit-identical goldens.
- Thermal key only, with no mode: #2753's figures.
- A refusal is `None` or a code, never 0.

## Alternatives rejected

- **The counter in `flow_meter.py`.** The counter rule serves the electric counter too, and the dwell log is mode accounting. Neither is "heat off the water", and flow_meter would gain cross-cycle state, where today its functions are stateless.
- **Sampling the mode once per cycle**, the start or end word. With the 30 min default interval, a person's mid-interval change books the whole interval to one mode. `last_changed` is already on the state object `pump_signals.read` holds.
- **The HA recorder for dwell.** That is a database read per cycle on Pi-class hardware (D9) and a new edge.
- **Time-split COP into both bins.** Probe 7: both bins would get the same ratio.
- **Refusing both heat keys together in the config flow.** That forces a user to delete a working key, and precedence already answers which one is used.
- **Electric COP side from `_measured_power`.** A point sample divided into a 30 min mean is the misalignment the brief names.

## Sibling sites (enumerated at `8a133f390`)

`git grep -nE "_commanded_split\(\)|planned_dhw / planned_total" -- custom_components` returns 8 sites. In scope: `_interval_measured_heat_kw`, `_cop_reference_curve` and `_accumulate_energy`. Out of scope, each with its reason:
- `_fold_flow_lift` and `_commanded_power`: these are about the plan's ask, not the delivered split.
- `_interval_space_power` and `_propagated_slab`: electric replay without a heat meter. A mode-dwell rewrite of those is a behaviour change no finding names.
- `draw_range.fold`: the draw-follows evidence, which is COP-GATE's.

`git grep -n "heat_output_kw\|measured_heat\b"` adds `sensor.py`'s `measured_heat_output_kw` attribute. It needs no change, because the counter mean is published there as the cycle's kW.

## Evidence plan, by file

- **Failing tests first**, in `tests/features.py`, beside #2753's checks:
  - a synthetic plant with a known COP gives an exact fold through `cop_evidence`;
  - null: heat = modelled COP x elec keeps `target_scale == cop_scale`;
  - a planted reset is refused, then re-baselines;
  - a planted rollover is refused;
  - a sub-quantum delta is refused;
  - a mixed space/DHW interval splits the replay heat by `last_changed`;
  - a two-change interval is `blended`;
  - a concurrent mode gives `None`;
  - precedence: a counter outranks the thermal kW, and an unusable counter does not fall back (mirror #2753's M1 check);
  - `heat_meter_needs_mode` refuses in the options step;
  - the basis voids on adding the counter.
  - A dead-counter test re-reports the unchanged value first (INPUT-STALENESS carry).
- **Harness.** Port `dev/audit/harnesses/r10_thermal_power_option.py` (#2753) to `dev/audit/harnesses/r10_heat_meter.py` (would be new). The synthetic counter plant runs at the base (no key: refused or absent) and at the head.
- **Null controls.** The flat-COP plant reads a fold of zero, and an install without the heat key or the mode entity reproduces the base goldens. Expected moving goldens: none. If the store schema golden moves for `HEAT_LOSS_BASES`, the fixer claims it in `tests/golden/claimed_drift.txt`.
- **Mutation targets:**
  - the `delta < 0` branch;
  - the min-delta comparison;
  - the counter-first precedence guard in `read_heat_output_kw`;
  - the `last_changed` split arithmetic;
  - the `blended` two-change rule;
  - the third `HEAT_LOSS_BASES` index.
- **Classification.** `heat_energy.py` goes into a measured closure (`tests/closures.json`), or `tests/entities.py` refuses it.

## Hot files and serial position

`files` must grow by: `custom_components/heatpump_optimizer/heat_energy.py` (would be new), `custom_components/heatpump_optimizer/pump_signals.py`, `custom_components/heatpump_optimizer/thermal_model.py`, `custom_components/heatpump_optimizer/accuracy.py` and `custom_components/heatpump_optimizer/translations/sv.json`. No open group other than ARCH-SHAPES (`thermal_model.py`, already before us) and UX-HEALTH (`strings.json`, already after us) touches them.

Position: `config_flow.py` 2 of 3 (after RATIO-ANCHOR, before CONFIGFLOW-PAGES); `const.py` last; `coordinator.py` after THERMAL-POWER-OPTION and before COP-GATE.

## Notes for the fixer

- **The #2698 clamp-reset decision: keep "clamp means reset".** It is orthogonal to this group. The void path enters `reanchor_heat_loss` at confidence 0, and its clamp test is `if a and not ...`, so a basis change can never trip it. Main's total-only law hands the upper zone the lower zone's share, which is the failure `reanchor_heat_loss`'s docstring records. Carry: dismissed: decided by this design, recorded decision kept.
- **SAV carry: partly closed, the rest unobservable.** The dwell split fixes attribution where the mode shows the duty. Under a concurrent mode, one whole-unit meter cannot separate the channels, so the plan split and its docstrings stay. Carry: dismissed: unobservable with one whole-unit meter under a concurrent mode.
- Carry: R10-COP-GATE. "Has a heat meter" is `probe_install(...).measured_heat`, which now covers both heat keys. Render the new codes `unaligned_meters` and the counter refusals, and override neither.
- Carry: R10-UX-HEALTH. Two new input rows (`heat_pump_heat_energy_entity`, and #2753's `heat_pump_thermal_power_entity`) take their role labels from `strings.json`'s `entities_metering` data. The COP refusal `unaligned_meters` needs a Health string.
