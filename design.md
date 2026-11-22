# Design note: R11-OWNER-FROST-HOLD -- frost hold instead of a switch-off

Code read at `origin/main` 3a98735a7e (no predecessor). Evidence: owner report
from a private diagnostics bundle; **no finder harness: owner report**. The
report, generically: the integration switches the pump's power switch off on
idle steps whatever the outdoor temperature; switched off for hours near 0 °C
the unit can run no defrost, and fault activity followed the morning
switch-on. Nothing in the tree guards an OFF by outdoor temperature (sites
below). Owner rulings (2026-11-22): threshold +2 °C; a stale sensor keeps
holding; the hold set-point is the pump's own floor.

## Behaviour

While the outdoor temperature is below `frost_hold_below_c`, an OFF the
integration would write to the power switch becomes a **frost hold**: the
switch stays on (or is switched on), and the arbiter writes the hold row --
a heating-capable mode and the space set-point at the pump's own floor -- so
the unit keeps its defrost, antifreeze and circulation logic, and its own
water thermostat starts it only if the water falls below that floor.

- **Latch, 1 K hysteresis.** Enters when a usable reading is below the
  threshold; leaves when a usable reading is at or above threshold + 1.0 K.
- **Unusable outdoor reading** (stale, unavailable, missing; the existing
  `InputHealth` verdict for `outdoor_temperature`): the latch does not move.
  An active hold keeps holding (ruling); an inactive latch starts none, since
  there is no evidence of cold. The latch is persisted, so a restart during an
  outage keeps holding. A latch never set (fresh install, no reading yet) is
  inactive.
- **Control only.** The hold needs the arbiter to write the floor; with
  `pump_duty_mode` other than control an OFF is written as today (a pump left
  on without the floor would heat on its own curve through every idle step).
- **Never** under Optimizer Off (the coordinator writes no switch there),
  nor while the pump's mode reads cooling or blocks both channels
  (`supply_write` already returns `None`; the hold only converts a `False`).
- **No "off" value.** Any threshold is a plain number; −25 °C (the selector
  minimum) never holds in practice. Not a sentinel, so no branch.

## Owning seam and shape

Owner: a new module `custom_components/heatpump_optimizer/frost_hold.py`
(new), the sibling of `custom_components/heatpump_optimizer/supply_hold.py`
and built on the same pattern: it imports `pump_arbiter` and writes fields on
`ArbiterState`, as `supply_hold` writes `supply_held`/`held_until`. It is the
**one writer** of the hold state. `pump_arbiter` only reads it; `coordinator`
and `early_cutoff` only call it. No import cycle (arbiter never imports it).

- `ArbiterState` gains `frost: bool | None` (the latch, persisted in
  `_persist`/`_load` beside `written`) and `frost_holding: bool` (this
  supply command was taken by a hold; in memory).
- `frost_hold.latch(held, outdoor_c: float | None, below_c) -> bool` -- the
  hysteresis; `None` leaves the latch.
- `frost_hold.gate(held, inp, value: bool | None, outdoor_c) -> bool | None` --
  applied **last** in `coordinator._write_supply`, after
  `supply_hold.hold_supply`: `True` clears `frost_holding`, passes; `None`
  passes; `False` with the latch active and control on sets `frost_holding`
  and returns `None` (switch untouched), or `True` where the switch reads
  off (entering a hold from the warm side). After `hold_supply`, so MIN_RUN /
  MIN_PAUSE never delay or carry a hold (a hold is not a planned run), and a
  held write (`None`) is not reinterpreted.
- `frost_hold.take_off(held, outdoor_c, config) -> bool` -- the early
  cut-off's question: latch active and control on sets `frost_holding` and
  returns `True`. `CutoffInputs` gains `frost_off: Callable[[], bool]`, bound
  by the coordinator; `on_room_event` calls it before
  `switch_supply(..., False)` and writes nothing when it returns `True`.
  Above the threshold the cut path is byte-identical to today.
- `pump_arbiter`: a helper `_held_duty(coord, held, inp, now)` returns
  `FROST_DUTY = "frost_hold"` when `held.frost_holding`, else `_step_duty`
  (which still runs, for the hot-water lease). `_arbitrate` and `_lead_mode`
  use it. `desired()` maps `FROST_DUTY` to the `"space"` row with the space
  set-point replaced by the floor and no feedback: flow unit `_gate_c(inp)`
  (the entity's minimum, never below `FLOW_GATE_C` / the return gate);
  indoor-set-point unit the entity's minimum (`setpoint_range_c`). The
  existing branch `duty == "space" and mode != MODE_HEAT` then gives
  Heat + DHW with the DHW set-point at `DHW_GATE_C` on GCHV.
- `frost_hold.freeze_reason(held, measured_kw, ran_kw)` -- `"frost_hold"` for
  two intervals after a pass under a hold measured a run; chained into the
  learner freeze at `coordinator.py` (`supply_hold.freeze_reason(...) or ...`).
  An idle hold with the compressor off is not frozen: freezing every hold
  interval would starve the fabric learner of its winter cooldowns.

Flow, idle step below threshold: `_apply_action` → `cycle_supply` (False) →
`_write_supply`: `allow_on` → `supply_write` (False) → `hold_supply` (False)
→ `frost_hold.gate` (None, `frost_holding`) → no switch write. Arbiter tick
(≤ 1 min): `_held_duty` = `frost_hold` → `desired` → `_command` writes mode
and floor into `held.written`.

**Mode per transport.** Tuya fork: Heating, DHW channel as on an idle step.
GCHV (no heating-only mode): Heat + DHW, DHW set-point at its gate. Both are
`_mode_for(inp, "space")`, unchanged.

**Ownership and re-sends.** The hold row goes through `_command`, so it is
recorded in `held.written`, re-sent after `ECHO_GRACE_S` on drift, retried on
a miss, and arms `off_restore` like any first space write. **Unload**:
`release()` and `off_restore` unchanged -- the space baseline is restored, the
switch is left as it reads, the pump is the person's. **Boost**: makes
`step_supply` `True`, which clears the hold; a boost ending below threshold
returns an OFF, which the gate turns back into a hold. **Entering from off**:
the gate's `True` runs `write_supply` → `_lead_mode`, which with
`_held_duty` leads with the heating-capable mode; the space set-point is the
pump's own reset while off, which is the floor (ruling), so `_lead_mode` is
not extended to the space slot. Entry from off waits for the next cycle (the
step tick writes only a change): at most one optimisation interval.

**Sensors and ledger.** `async_publish_current_action` publishes reason
`frost_hold` while held; `heat_pump_on` stays the plan's. `_verdict` scores a
row whose planned duty is `frost_hold` as the new verdict `frost-hold`, never
`idle-instead`/`space-instead`. Arbiter diagnostics gain `frost`
(latch, holding, threshold); the module docstring's verdict list gains it.

## Option

`CONF_FROST_HOLD_BELOW_C = "frost_hold_below_c"`, `DEFAULT_FROST_HOLD_BELOW_C
= 2.0` in `custom_components/heatpump_optimizer/const.py`; an `_F` row in
`custom_components/heatpump_optimizer/config_flow.py` beside
`CONF_FLOW_HEAT_C`, `_number(-25, 10, 0.5, '°C')`, shown only where a power
switch is configured; read through `EntryConfig`. Default on for existing
installs: that is the behaviour change the release note states.

## Alternatives

1. Logic inside `pump_arbiter.py` -- lost: the module is past
   `MODULE_LOC_LIMIT`, so every line is `module_excess_loc`, and it would
   make the arbiter decide the supply that `coordinator._write_supply` gates.
2. Route the cut-off through `_write_supply` (one gate for every switch
   write) -- lost: it subjects the cut to `hold_supply`'s MIN_RUN, which
   differs from the cut-off's own `MIN_ON`/`MIN_OFF`, changing above-threshold
   behaviour; `take_off` changes only the below-threshold path.
3. The draft's `frost_hold_flow_c` override and away-temperature floor --
   dropped by the ruling (the pump's own floor).
4. Freeze learners on every hold interval -- lost, see `freeze_reason`.

## Sibling sites

`grep -rn "switch_supply(\|write_supply(\|supply_write(" custom_components/heatpump_optimizer/*.py`
finds three callers: `coordinator._write_supply` (covered by `gate`),
`early_cutoff.on_room_event` (covered by `take_off`), and `write_supply`
itself. `supply_tick` writes through `wiring.write` = `_write_supply`
(covered). `release()` writes no switch (out of scope, stated above).

## Evidence plan

Tests in `tests/features.py` beside the `supply_hold.hold_supply` cases,
failing first:

1. Below threshold, an idle step writes no OFF, and the pass writes the floor
   and a heating-capable mode. **Null control**: threshold −25 °C gives
   today's OFF on the same fixture.
2. Usable reading ≥ threshold + 1 K: OFF written as today.
3. Hysteresis: a reading in [threshold, threshold + 1) does not flip either
   latch state.
4. Unusable reading: an active hold holds; an inactive latch starts none;
   after a simulated restart (store reload) with an unusable reading the
   persisted hold holds.
5. Early cut-off below threshold: no `turn_off`, `frost_holding` set, hold row
   written; above threshold: `turn_off` as today (null control).
6. Switch reads off on entering the hold: mode led, then `turn_on`.
7. Optimizer Off: no switch write; cooling / both-blocked: no hold; observe
   duty mode: OFF written.
8. Hold set-point drifted: re-sent after `ECHO_GRACE_S`.
9. GCHV: Heat + DHW with DHW at `DHW_GATE_C`; indoor-set-point unit at the
   entity minimum.
10. Boost end below threshold returns to the hold.
11. MIN_RUN / MIN_PAUSE never delay a hold's switch-on or carry it.
12. Ledger `frost-hold` verdict; learner freeze only on a measured run.
13. Config flow: option, bounds, three translations; `const.py` symbol check.
14. Synthetic replay (no install data): a 24 h idle-heavy step series with
    outdoor crossing 0 °C; count of OFF writes at outdoor below threshold must
    be 0, with the null control at −25 °C reproducing the series' OFF count.

Mutation targets: the latch comparisons and the `+ 1.0` hysteresis, the
`None`-keeps-latch guard, the `False`→hold branch and the switch-off→`True`
branch in `gate`, `take_off`'s guard, `_held_duty`'s condition, the
`desired()` floor substitution, the `_verdict` branch, and `freeze_reason`'s
run guard. No golden moves (default fixtures carry no outdoor below +2 °C
on an idle step, to be confirmed by the fixer's gate run; any that moves is
claimed, never re-recorded).

## Hot files, ratchet and docs

Hot: `pump_arbiter.py`, `coordinator.py`, `early_cutoff.py`,
`config_flow.py`, `const.py`, `strings.json`, `translations/en.json`,
`translations/sv.json`, `translations/de.json`, `tests/features.py`. Both
`pump_arbiter.py` and `coordinator.py` are past `MODULE_LOC_LIMIT`: the
fixer pays their added lines inside those files (`module_excess_loc`), and
classifies `frost_hold.py` in a measured closure (`tests/closures.json`).

Docs: `docs/configuration.md` -- a bullet beside "A pump switched off is left
alone" and the option's row; `docs/how-it-works.md` where the cut-off and the
idle step are described; the option's description in `strings.json` and
translations.

Release-note line: "Below +2 °C outdoors (option *Frost hold below*) the
optimizer no longer switches the heat pump off on idle steps: it keeps it on
at its own minimum set-point so the unit can defrost and protect itself; set
the option to −25 °C to keep the old behaviour."

## Notes for the fixer

- Carry: R11-OWNER-FROST-HOLD -- check `_without_block`, `_share`,
  `_leased`, `pass_origin` (FROST is not in space/both, so origin gate) and
  `duty_switch.note_pass` accept the new duty value unchanged.
- Carry: R11-OWNER-FROST-HOLD -- the arbiter must not read `frost_holding`
  under `MODE_OFF` (its off branch returns first); clear it in `gate` on any
  `True`.
- Pricing the hold's standby in the planner -- dismissed: bounded by the
  floor, and no finding names a planner change.
