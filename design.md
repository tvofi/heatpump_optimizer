# Design note: R11-OWNER-FROST-HOLD -- frost hold instead of a switch-off (rev 2)

Rev 2 answers `design-verdict/R11-OWNER-FROST-HOLD` a330ce0a (revise, class-open,
R1-R9 on aefc8bc416). Code read at `origin/main` 3a98735a7e; no predecessor.
Evidence: owner report from a private diagnostics bundle; **no finder
harness: owner report**. Generically: the integration switches the power
switch off on idle steps whatever the outdoor temperature; off for hours near
0 °C the unit can run no defrost, and fault activity followed the switch-on.
No OFF path is guarded by outdoor temperature today.

Owner rulings (tvofi 2026-11-22): threshold +2 °C; a stale reading keeps a
hold **and starts one**; the hold covers every install where the integration
controls an on/off switch; the hold set-point is the pump's own floor.
Orchestrator decisions on the review's open questions, pending owner
override: no sensor configured → the weather forecast is the reading; the
hold wins over a space-heating block; the hold overrides a quiet off window;
an explicit opt-out; the floor is the entity minimum or the controller's
lower-limit sensor; no latch persistence.

## Behaviour

While the latch is active, an OFF the integration would write to the power
switch becomes a **frost hold**: the switch stays on (or is switched on). In
duty control the arbiter also writes the hold row; elsewhere nothing else is
written and the pump runs on its own thermostat and curve.

- **Reading** (R1): `ArbiterInputs` gains `outdoor_c: float | None`, built by
  `frost_hold.reading(health, forecast_c, configured)` from the
  `InputHealth` verdict for `outdoor_temperature` -- never from
  `state.outdoor_temperature`, which `coordinator.py` back-fills from the
  forecast, the prior value or a 5.0 default. Sensor configured: its value
  when ok, else `None`. No sensor configured: `forecast_outdoor_now(...)`,
  else `None`.
- **Latch, 1 K hysteresis**: `None` (stale, unavailable, missing, no sensor and
  no forecast) **sets** the latch; a reading below the threshold sets it; only
  a reading at or above threshold + 1.0 K clears it. In memory only (R7): a
  restart starts unset, and the first pass sets it from the reading; a
  restart with a reading inside [threshold, threshold + 1) starts inactive.
  The latch is updated in synchronous code with no `await`, so it is atomic on
  the event loop without `held.lock`.
- **Opt-out** (R3): `frost_hold` boolean, default on. Off is a branch:
  `gate` and `take_off` return their input unchanged, a stale sensor
  included.
- **Visible**: the action reason is `frost_hold` (cold) or
  `frost_hold_no_reading` (latched by `None`), and diagnostics carry the latch,
  the cause, the threshold and the reading, so a stale-started summer hold is
  visible beside the existing `input_health` summary. No new repair: the
  sensor's staleness is already reported there.

**Install cases** (R2; the gate sits above `on_off_service`, so the switch
domain -- `switch`, `input_boolean`, `climate` -- does not matter):

| install | the hold does |
|---|---|
| no power switch | nothing to hold; out of scope |
| switch, duty mode off (the default) | switch stays on; nothing else written; pump on its own curve |
| switch, duty observe | as off; the ledger scores the step `frost-hold` |
| switch, control, Tuya fork (Heating / DHW-only) | switch on, Heating, space at the floor |
| switch, control, GCHV/Rotenso (no heating-only mode) | Heat + DHW, DHW at `DHW_GATE_C`, space at the floor |
| switch, control, generic number/climate set-point (flow, return or indoor), with or without mode select | floor written; no mode entity, no mode written |
| switch, control, no space set-point entity | switch-on only (`desired` writes no missing slot) |
| pump mode cooling, or both channels blocked | unchanged: `supply_write` returns `None`, there is no OFF to convert |
| Optimizer Off | unchanged: the coordinator writes no switch |

**Cost, stated** (R2): outside duty control, a held pump can run its
compressor on its own curve through idle steps below the threshold, which the
plan does not price, and those runs freeze the learners for their intervals.
The release note says both.

**Quiet off windows** (R6): a `quiet_windows.ACTION_OFF` step is an idle step,
and the hold converts its OFF too. **Space block** (R4): the hold wins --
frost protection is not space heating.

## Owning seam and shape

Owner: new module `custom_components/heatpump_optimizer/frost_hold.py` (new),
the sibling of `custom_components/heatpump_optimizer/supply_hold.py` on its
pattern: it imports `pump_arbiter` and writes `ArbiterState` fields, the
**one writer** of the hold. `pump_arbiter` only reads; `coordinator` and
`early_cutoff` only call. No import cycle.

- `ArbiterState` gains `frost: bool | None` (latch), `frost_holding: bool`,
  `frost_ran_until: datetime | None`. Nothing persisted.
- `frost_hold.gate(held, inp, value)` -- last in `coordinator._write_supply`,
  after `supply_hold.hold_supply`, so MIN_RUN/MIN_PAUSE never delay or carry
  a hold and a held write (`None`) is never reinterpreted. `True` clears
  `frost_holding` and passes; `None` passes; `False` with the latch active
  sets `frost_holding` and returns `None`, or `True` where the switch reads
  off (entry from the warm side, at the next cycle).
- `frost_hold.take_off(held, inp) -> bool` -- the early cut-off's question.
  `early_cutoff.arm` gains `frost_off: Callable[[], bool]`, built by
  `frost_hold.cutoff_hook(coord)` in the existing one-line `arm` call;
  `on_room_event` asks it before `switch_supply(..., False)` and writes nothing
  on `True`. Above the threshold, or opted out, the cut is byte-identical.
- **Resolved once** (R4): no new duty string. `_arbitrate` and `_lead_mode`
  read `held.frost_holding` once: served becomes `"space"`, bypassing
  `_without_block`, and `desired(..., frost=True)` replaces the space
  set-point with `_hold_floor_c(inp)` and skips `_feedback` and the boost
  mapping. Every other consumer sees only a duty it already knows:
  `_mode_for(inp, "space")` gives Heating on Tuya (so `_lead_mode` leads with
  Heating, not Heat + DHW) and Heat + DHW where no heating-only mode exists;
  the existing `duty == "space" and mode != MODE_HEAT` branch writes the DHW
  gate; `_note_pass` is handed `"idle"` so `pass_origin` is `ORIGIN_GATE` and
  `draw_range` reads no heating pass; `_observe` sets `row["frost"]`, which
  `_verdict` reads first (`frost-hold`); `_step_duty`, `_leased`, `_share` and
  `duty_switch.note_pass` still run on the plan's duty, unchanged;
  `_disinfecting` keeps its mapping, so a disinfection hold still arms the
  tank.
- **Floor** (R5): `_hold_floor_c(inp)` = the entity's own minimum
  (`setpoint_range_c`), raised to the controller lower-limit sensor
  (`_setpoint_limits_c`) where one reads; where the entity states no minimum,
  the gate in its own terms for a water unit (`_gate_floor_c`; what
  `FLOW_GATE_C`'s comment says it is for) and the existing 5.0 °C bound for an
  indoor unit. `_gate_c` is not used.
- `frost_hold.freeze_reason(held, inp)` -- `"frost_hold"` until
  `frost_ran_until`, set for two intervals whenever `gate` or the freeze check
  sees a hold with `measured_power_kw >= pump_arbiter.ran_kw(inp)`
  (`_ran_kw` made public, renamed), or a hold with no meter (fail closed).
  Chained in `_tail_freeze` beside `supply_hold.freeze_reason`. An unmetered
  idle hold is frozen; a metered one with the compressor off is not.

Flow, idle step below threshold: `_apply_action` → `cycle_supply` (False) →
`_write_supply`: `allow_on` → `supply_write` → `hold_supply` → `frost_hold.gate`
(None, holding) → no switch write; arbiter tick (≤ 1 min, control) → hold row
via `_command` → `held.written`, `ECHO_GRACE_S` re-send, retry on a miss,
`off_restore` armed as by any first space write. Unload, `release()` and
`off_restore` unchanged: the baseline is restored and the switch left as it
reads. A boost makes `step_supply` `True` and clears the hold; its end returns
an OFF that the gate holds again. Readers mask `frost_holding` while
`inp.mode == MODE_OFF`, so diagnostics show no stale hold.

## Option

`CONF_FROST_HOLD` (`"frost_hold"`, default `True`) and
`CONF_FROST_HOLD_BELOW_C` (`"frost_hold_below_c"`, default 2.0) in
`custom_components/heatpump_optimizer/const.py`; two `_F` rows in
`custom_components/heatpump_optimizer/config_flow.py` beside
`CONF_FLOW_HEAT_C`, shown where a power switch is configured, the threshold
`_number(-15, 10, 0.5, '°C')`; read through `EntryConfig`.

## Alternatives

1. Logic in `pump_arbiter.py` -- lost: past `MODULE_LOC_LIMIT`, and it would
   make the arbiter decide the supply `_write_supply` gates.
2. Cut-off through `_write_supply` -- lost: subjects the cut to MIN_RUN,
   which differs from the cut-off's own `MIN_ON`/`MIN_OFF`.
3. A `frost_hold` duty string -- lost (R4): `_without_block` drops it to idle
   under a block and `_mode_for` maps it to Heat + DHW.
4. Control only -- lost (R2, ruling): the default duty mode is off.
5. A persisted latch -- lost (R7): `_load` runs only on arbiter paths outside
   duty off, and R1 already makes an outage restart hold.
6. −25 °C as the opt-out -- lost (R3): a stale reading still holds.

## Sibling sites

`grep -rn "switch_supply(\|write_supply(\|supply_write(" custom_components/heatpump_optimizer/*.py`:
`coordinator._write_supply` (gate), `early_cutoff.on_room_event` (take_off),
`write_supply` itself; `supply_tick` writes through `_write_supply`.
`grep -rn "ACTION_OFF" custom_components/heatpump_optimizer/*.py`: quiet off
reaches the switch only as an idle step (covered).

## Evidence plan

Tests in `tests/features.py` beside the `supply_hold.hold_supply` cases,
failing first; null control in each: the same fixture with `frost_hold` off
gives today's OFF.

1. Control, below threshold: no OFF; pass writes the floor and Heating (Tuya).
2. Reading ≥ threshold + 1 K: OFF as today. 3. Band [t, t + 1): no flip.
4. Stale, unavailable, missing: latch set from inactive; an active hold holds;
   a 5.0 back-filled `state.outdoor_temperature` does not clear it.
5. No sensor: forecast below → hold, above + 1 K → OFF; no forecast → hold.
6. Opt-out off with a stale sensor: OFF as today.
7. Duty off and duty observe: switch stays on, no arbiter write; observe
   ledger `frost-hold`.
8. Control with no space set-point / no mode entity: switch-on only.
9. GCHV: Heat + DHW, DHW at `DHW_GATE_C`; indoor unit at its minimum.
10. Floor: entity minimum below 25 °C is written as is; lower-limit sensor
    raises it; no stated minimum → the gate.
11. Tuya lead into a hold from off: mode Heating, then `turn_on`; a mutant
    mapping the hold to Heat + DHW fails.
12. DHW block and space block: hold row still written.
13. Quiet off window below threshold: held, not switched off.
14. Early cut-off below threshold: no `turn_off`, hold row; above: as today.
15. Drifted floor re-sent after `ECHO_GRACE_S`; boost end returns to the hold.
16. MIN_RUN / MIN_PAUSE never delay a hold's switch-on.
17. Freeze on a metered run and on an unmetered hold; none on a metered idle.
18. Config flow: both options, bounds, three translations; `const.py` check.
19. Synthetic replay (no install data): 24 h idle-heavy series crossing 0 °C
    with a stale stretch; OFF writes while latched must be 0; null control
    (opt-out) reproduces the series' OFF count.

Mutation targets: the latch comparisons, `+ 1.0`, the `None`-sets-latch
branch, the opt-out branch, `gate`'s `False` and switch-off branches,
`take_off`'s guard, the `frost_holding` read in `_arbitrate`/`_lead_mode`, the
block bypass, `_hold_floor_c`'s limit max, `_verdict`'s frost branch,
`freeze_reason`'s run guard. Goldens: the fixer's gate run decides; a moved
fixture is claimed, never re-recorded.

## Hot files, ratchet and docs

Hot: `pump_arbiter.py`, `coordinator.py`, `early_cutoff.py`,
`config_flow.py`, `const.py`, `strings.json`, `translations/en.json`,
`translations/sv.json`, `translations/de.json`, `tests/features.py`;
`frost_hold.py` classified into a measured closure (`tests/closures.json`).
Ratchet (R8): the coordinator class gains about three lines (the
`arbiter_inputs` field, the `gate` wrap, the `arm` argument on its existing
line). They count in `module_excess_loc`, `class_excess_loc` and
`max_class_loc`. They are paid inside the class by moving `_write_supply`'s
eight-line "Not switching off" debug branch into `frost_hold` as
`log_skip(entity, label)`. `_tail_freeze` is a module function (module
excess only). `pump_arbiter.py` additions (state fields, `_hold_floor_c`, the
`desired` flag, the verdict branch) are paid in-file. The fixer runs
`tools/audit/archscore/` before and after.

Docs: `docs/configuration.md` -- a bullet beside "A pump switched off is
left alone", the options, and a line at the quiet windows; `docs/how-it-works.md`
at the cut-off and the idle step; the option descriptions in `strings.json`
and translations.

Release note: "On every install with a heat pump power switch, the optimizer
no longer switches the pump off on idle steps while it is below +2 °C outdoors
(option *Frost hold below*), or while the outdoor reading is stale or missing:
the pump stays on so it can defrost and protect itself. With *Pump duty* in
control it is held at its own minimum set-point; otherwise it runs on its own
curve while held, which can use energy the plan does not price, and learning
pauses for those runs. Quiet off windows are held too. Turn *Frost hold* off
to keep the old behaviour."

## Notes for the fixer

- Carry: R11-OWNER-FROST-HOLD (circulation-rail) -- `pump_schedule.space_pump_should_run`
  keeps its 0 °C rail and does not read the new option: it protects the
  external emitter loop, while the hold keeps the unit's own circulation
  running; state this in its docstring.
- Carry: R11-OWNER-FROST-HOLD (clear-on-off) -- masked by readers under
  `MODE_OFF` as above; `gate` clears it on the first call after Off ends.
- Pricing the hold in the planner -- dismissed: no finding names a planner
  change; the release note states the cost.
