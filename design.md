# R11-OWNER-STEP-KICK: the space set-point's step-start kick to the ceiling (design note, rev 1)

Base: `origin/main` 3a98735a7ecc59e7ecc095a0429cdf6251d956ec. There is no predecessor handoff. R11-OWNER-FLOWCAP's clamp handoff (13290409848b) is read for overlap only.
Evidence: the owner's live report, read against a private diagnostics bundle that stays local. **No finder harness: owner report.** Every number below is either invented or a code constant.

## 1. Why the kick exists

The code has no deliberate kick. Nothing writes the ceiling because a step started. The kick comes from three rules that each had a sound reason when added:

1. `pump_arbiter.FLOW_HEAT_C` (55 °C, option `flow_heat_c`) is the top of the level map. It dates from 34339ad4e0, a production report of 2026-09-26: written as the pricing curve, the flow set-point held 25 °C and underheated the house. Its comment gives the reason: "so the pump's own water thermostat never cuts a planned heating step short".
2. The bottom of the map is `thermal_model.modulation_floor_flow_c`: the measured inlet plus a lift. It dates from 25c3bd7b40 (R10-SETPOINT-POWER, 2026-10-19: "the set-point is a power command"). `start_flow_min_lift_k` keeps that lift at or above the pump's heating start hysteresis, because "its controller starts only once the target sits that far above the water". This is the code's only start-forcing rule, and it acts on the floor, not on 55.
3. The inlet is the first fresh rung of `pump_arbiter.FLOW_INLET_KEYS`, and the pump-loop return comes first.

After a hot-water leg, the pump-loop return still reads the tank coil's water for one to a few minutes. So `floor = inlet + lift` lands at or above the ceiling. `flow_setpoint_for_level` then clamps the target to `heat_c`, and the step writes 55. As space-loop water reaches the probe, the floor falls, and each minute's write follows it down to the level-mapped value. That is the 1–4 minute ramp the owner sees. `FEEDBACK_START_HOLD` (5 min) writes this open-loop base unchanged, so the feedback loop does not damp the ramp.

Checked locally against the bundle (values stay local): most step-start ceiling writes came right after a hot-water leg, with the pump-loop return at or near the ceiling. A minority came with a cool inlet, after a fault stop. Their cause is not determined, and this design does not cover them (§4, class `other`).

Tests that pin it: the R10-SETPOINT-POWER cells in `tests/features.py` (`_sp_write`: the rung order, inlet plus lift at the floor, the ceiling at full power), and the R10-SETPOINT-BOOST cells (`_bst_write`). None of them pins the post-swap transient. The docs state the rule in `docs/configuration.md`, under "Pump duty control".

The likely reason the owner guessed is half right. On a supply-target controller, a target above the hot water keeps the heating request on across the swap. The duty-switch learner's finding (`docs/design/2026-11-10-duty-switch-restart-learning/design.md`) shows the opposite case on a return-target controller: a target below a just-heated return stops the compressor. Removing the kick therefore has a real start and stop risk, and the harness must measure it.

## 2. Options and their risks

| option | risk / why it loses |
|---|---|
| A. Keep | No new start risk. It keeps asking for maximum lift against space-loop water right after the swap. Its effect on P3 trips and strain is unproven, so it is not refuted either. |
| B. Start at supply + k K and ramp up | At the swap the supply probe reads the hot-water leg's water, which is hotter than the return. So supply + k sits above the ceiling and the kick comes back. Ramping only after the swap needs the same settle detection as D, plus a ramp state machine and one write per minute. Each write is a cloud round trip on the Tuya fork (`ECHO_GRACE_S`). More state and more writes for the same end value. |
| C. Cap the first-minute lift | A cap needs a reference. Against the live return or the supply it caps nothing, because both are hot. A fixed time cap is install-specific, and it misses minutes 2–4, while the probe is still hot. |
| **D. Skip the kick only right after a hot-water→space swap (recommended)** | During the swap settle, anchor the floor on the space loop's own water instead of the hot probe. Risk: the controller still sees hot water and may stop or delay the compressor. The harness (§4) gates this, and setting `SWAP_SETTLE` to 0 restores today's behaviour. |

## 3. Recommendation: D, the swap-settle inlet anchor

**Owning seam:** `pump_arbiter.py`, through `_map_inputs`, the one place the floor is mapped for the write and for the pass record. A new pure module, `custom_components/heatpump_optimizer/flow_anchor.py` (no `homeassistant` import), owns the anchor rule. The coordinator, `ArbiterInputs` and `const.py` stay unchanged. One owner: report-and-stop does not apply.

**Shape.**
- New in `flow_anchor.py`: `settled_inlet_c(live_c, space_c, next_rung_c, swap_at, now) -> float | None`.
  - Outside `[swap_at, swap_at + SWAP_SETTLE)` it returns `live_c` unchanged.
  - Inside the window it returns `min(live_c, x)`, where `x` is the first of these that exists: the remembered space inlet (`space_c`, if younger than `SPACE_INLET_MAX_AGE`); the first fresh rung other than the pump-loop return (`next_rung_c`); or `None`. `None` makes `_or_hold` use the rated `FLOW_HOLD_C`.
  - `FLOW_INLET_KEYS` and `RETURN_SKIPPED_RUNG` move here with their comment. `pump_arbiter` re-exports them in one line.
- New `ArbiterState` fields, never persisted (a restart's first pass is not a swap):
  - `swap_at: datetime | None`, set on a Control pass whose **served** duty (`_served`, not `_step_duty`) is `space` or `both` while the previous pass served `dhw`, and cleared on the next `dhw`.
  - `space_inlet: tuple[float, datetime] | None`, the live inlet on a space-served pass outside the settle while the compressor runs (`_ran_kw`).
- Constants in `flow_anchor.py`:
  - `SWAP_SETTLE` is not a constant of its own: the caller passes `pump_arbiter.FEEDBACK_START_HOLD` in as an argument, which avoids an import cycle. So the settle ends when the loop's start hold ends, and the two never disagree. The off switch in §2 and §4 is that argument set to zero.
  - `SPACE_INLET_MAX_AGE = timedelta(minutes=LEASE_MINUTES)`. A hot-water lease cannot outlast it while the house wants heat.
- Data flow: `_arbitrate` → `_served` → (new: note the swap and the space inlet) → `desired` → `_space_target` → `_flow_target` → `_map_inputs` → `settled_inlet_c` → `modulation_floor_flow_c` → `flow_setpoint_for_level`.

**Invariants.**
- I1: the anchor is `min(live, …)`, so a write is never higher than today's.
- I2: outside the settle window every write is byte-identical to today's.
- I3: the gate-plus-step floor (`_bounded`) holds.
- I4: no change on a return-unit or indoor-unit set-point.
- I5: a planned level at the band top, or a boost, still writes the ceiling.

**Defaults and generalisation.**
- Tuya fork (select transport, flow target, pump-loop return): applies. This is the reported case.
- GCHV/Rotenso Modbus (set-point gate transport, no single-duty mode): the swap is a served-duty change with no mode write. Because the trigger keys on the served duty, this install is covered the same way.
- Return target (Luxtronik smart-home interface): **excluded**. The hot return is the controlled variable there, and Bankaifan's table shows that a low target at this swap stops the compressor.
- Generic installs with no inlet sensor: the floor is already `FLOW_HOLD_C`, so the rule is a no-op.
- Buffer-tank plants: the buffer rung reads space-side water, so the rule is rarely active and harmless when it is.
- No new option: `config_flow.py` is over `MODULE_LOC_LIMIT`, and the module keeps such numbers as constants (as `supply_hold` does).

**Sibling sites** (`grep -n "_flow_inlet_c(" custom_components/heatpump_optimizer/pump_arbiter.py`):
- `_map_inputs`: changed.
- `_full_draw_c`: return unit only, out of scope by I4.
- `_feedback`: live inlet on purpose. During the settle the loop is in its start hold and its bounds are unread.
- `_pass_record` inlet column: stays a live measurement. Its `floor_c` comes through `_map_inputs`, so `draw_range` rows agree with the write.
- The duty-switch context (`inlet_c=`): stays live, because its heated gate measures the real return.

## 4. Harness

The harness is `dev/audit/harnesses/r11_owner_step_kick.py <bundle.json>`. It prints counts only and never echoes values. The bundle is passed in as a path and never committed.

- **Step start:** a mode write to Heating, or a space write rising off the gate, within 90 s of a plan step boundary.
- **Kick class** (by the first space write of the step):
  - `hot-inlet`: at least the ceiling minus 0.5 K, with the pump-loop return within the lift of the ceiling.
  - `other`: at least the ceiling minus 0.5 K, with a cool return.
  - `none`: below that.
- **H1, faults:** fault-alarm onsets within 5 min after each step start, per class.
  - Null 1: the same windows shifted +7.5 min, which gives the base rate of onsets in any 5-min window.
  - Null 2: space step starts with no hot-water leg in the previous 15 min.
  - H1 is evidence only. It is underpowered and gates nothing.
- **H2, latency:**
  - Time from step start to the first meter reading at or above `_ran_kw`.
  - Missed starts: none before the step ends.
  - Stop at swap: running at the swap, then below `_ran_kw` within `duty_switch.STOP_WINDOW_S`.
  - Null: the same measures on space→space step starts.
- **Perturbation:** inject a ceiling write at the shifted starts in a copy. The `hot-inlet` and `other` counts must move.
- **Pass, run before and after:**
  - The synthetic replay shows zero `hot-inlet` kicks.
  - In the owner's soak bundle:
    - median latency is at most the before value + 60 s;
    - missed starts do not exceed the before count;
    - the stop-at-swap rate does not exceed the before rate by more than the null's spread.
  - On failure, set `SWAP_SETTLE` to 0 and report.

## 5. Tests and structure payment

**Tests**, all in `tests/features.py`, with invented readings: return 54 °C after the leg, remembered space inlet 29 °C, band 1.5–5.5 kW.
- T1, the failing test: a swap pass at a mid-band level writes below the ceiling, equal to the map from 29 + lift. On main it writes the ceiling.
- T2, null: the same pass with the previous pass served `space` writes the same value as on main.
- T3, null: a hot inlet with no swap still clamps to the ceiling. The rule keys on the swap, not on heat.
- T4: once `SWAP_SETTLE` has elapsed, or once the live inlet is at or below the anchor, the live value is used.
- T5: no remembered inlet → the next rung other than the pump-loop return; no such rung → `FLOW_HOLD_C`.
- T6: a return unit and an indoor unit are unchanged (null).
- T7: band-top level and boost still write the ceiling (I5).
- T8: on the gate transport (no single-duty option in the mode select), the served-duty swap triggers the rule.

**Mutation targets:** the settle comparison, the `min`, the served-duty predicate, the max-age guard, and the return-unit exclusion.

**Payment:**
- `module_excess_loc` has zero headroom, and `pump_arbiter.py` is over `MODULE_LOC_LIMIT`.
- Moving `FLOW_INLET_KEYS`, `RETURN_SKIPPED_RUNG` and their comment block out of `pump_arbiter.py` frees more lines than the new fields, the swap note and the call add. They move into `flow_anchor.py`, which owns the anchor concept.
- The fixer measures the net with `python3 tests/structure.py` at its merge base, and it must be zero or below. It also runs `tools/audit/archscore/` before and after.
- The new module and harness must be classified (closure, or `tests/closure.py` INERT). The CI autofix repairs `UNDER-SCOPED`; never run a full `derive_closures.sh` off Linux.
- No budget raise is expected.

## 6. Hot files, order, overlap

Hot files: `pump_arbiter.py`, `tests/features.py`, the new `flow_anchor.py`, and `tests/closures.json`.

- **R11-OWNER-FLOWCAP** lands first, by orchestrator ruling. It also edits `_map_inputs` (`heat_c` capped by the effective limit), and it pays its own `module_excess_loc` in `pump_arbiter.py`. Its fallback payment moves `_full_draw_c`, which calls `_flow_inlet_c`. The two compose cleanly: FLOWCAP lowers the top and this group lowers the floor anchor. This group goes after FLOWCAP and rebases `_map_inputs` onto it.
- **R11-OWNER-MODE-LEGS** governs how often hot-water→space swaps happen and when (minimum leg duration, the cycle-vs-tick 12-s leg). Its served-duty history and this group's `swap_at` must have one owner: whichever lands second reuses the other's field. Order: after MODE-LEGS. The harness's "before" baseline is taken on MODE-LEGS' merged code.
- **R11-OWNER-FROST-HOLD** adds a hold row and `ArbiterInputs.outdoor_c`. Leaving a frost hold is not a hot-water→space swap, so the rules do not interact. They share only the hot file, so their order is free.

## Notes for the fixer

- Read the duty-switch learner's evidence shift (`duty_switch.py`). Its heated gate needs the inlet at least 2 K above the command's set-point. While the kick wrote the ceiling, Tuya swaps rarely opened an episode. After this change they will, so the learner starts measuring exactly the stop-at-swap risk H2 measures. State this in the body. Carry: R11-OWNER-STEP-KICK
- The `other` kick class (ceiling with a cool inlet, after a fault stop) is not covered by this design. Classify it in the harness and report its count, so the orchestrator can route it. Carry: R11-OWNER-STEP-KICK
