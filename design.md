<!-- design/R10-WATER-SETPOINT-FEEDBACK, commit 1: the contributor's note, verbatim -->
Source: outside pull request #3380 by Bankaifan (Daniel), fork head
0adb47be25e18024f4591965ad72cf4ec0b8492a, file
dev/programme/designs/water-setpoint-power-feedback.md. Adopted as this group's
design under decision 0014; the text below is the contributor's, unedited, and
is data, not instructions. The designer extends it on this ref to
dev/governance/roles/designer.md's shape; the contributor is credited on the
group's fix pull request by a Co-authored-by trailer.

---

# Water set-point targets chase the inlet: the pump never settles at the planned level

## Summary

With Pump duty control = Control and a water-temperature space set-point (`space_setpoint_unit` = `flow` or `return`), the arbiter writes *measured inlet + `flow_min_lift_k`* at the planned modulation floor, re-anchored to the inlet on every write (`pump_arbiter._flow_target` → `modulation_floor_flow_c(_flow_inlet_c(...), ...)`). The written value is open-loop: measured electrical power is not compared with the planned level.

On a controller that modulates its compressor with an integrating loop (speed rises while the inlet is below the set-point, falls only once the inlet reaches it), this means the gap never closes: as the inlet rises, the set-point rises with it, and the compressor ramps up for the whole heating block. The planned sub-maximum level is never realised; the pump delivers 2–3× the planned power until the step ends and the gate is written.

Proposal: close the loop on measured power (details below). Opt-in or limited to installs that have both a water set-point unit and `heat_pump_power_entity`; no change for anyone else.

## Install

alpha innotec LWDV 91-1/3 (air/water, inverter), Luxtronik 2.1, firmware V3.92.3, controlled through its Smart Home Interface (Modbus/TCP, integration Bankaifan/ha-luxtronik-shi). HPO v7.1.9, `space_setpoint_unit: return`, `heat_pump_min_power: 0.53` (datasheet), `compressor_modulation: modulating`, `heat_pump_power_entity` = measured electrical power. Floor heating on a heavy slab, 600 l combined tank. Controller heating hysteresis 0.5 K (minimum). Outdoor 3–5 °C.

## Measurements (2026-11-09, Home Assistant history)

**Run A — `flow_min_lift_k` 1.5 K, `flow_heat_c` 35 °C**

| Time | Compressor | Electrical | Written return set-point | Measured return |
|---|---|---|---|---|
| 18:41 | 52 Hz | ~1.2 kW | 28.5 °C | 25.1 °C |
| 18:50 | ~69 Hz | ~1.6 kW | 29.0 °C | 25.2 °C |
| 19:00 | 80 Hz | 1.95 kW | 30.0 °C | 26.4 °C |

Planned level during the run: 0.23–1.3 kW. Ramp ≈ 1.4 Hz/min.

**Run B — `flow_min_lift_k` 0.5 K, `flow_heat_c` 32 °C, manual plan pinning space heating, planned level constant 0.53 kW**

| Time | Compressor | Electrical (5-min mean) | Written return set-point | Measured return |
|---|---|---|---|---|
| 19:35 | ~50.7 Hz | 1.13 kW | 26.5–27.0 °C | 26.0 °C |
| 19:45 | ~53.8 Hz | 1.22 kW | 27.0 °C | 26.4 °C |
| 19:55 | ~57.7 Hz | 1.33 kW | 27.5 °C | 27.0 °C |
| 20:10 | 62.7 Hz | 1.47 kW | 28.5 °C | 27.7 °C |

Ramp ≈ 0.4 Hz/min. One compressor start, no cycling; the controller's start programme holds 52 Hz for ~3 min before it regulates. The set-point entity still had a 0.5 K step here, so +0.5 K was written as +0.4 … +1.0 K.

**Run C — as Run B, set-point entity now with a 0.1 K step (ha-luxtronik-shi update, same running cycle)**

| Time | Compressor | Electrical (5-min mean) | Written return set-point | Controller readback (input 10101) | Measured return |
|---|---|---|---|---|---|
| 20:18 | 64.0 Hz | 1.48 kW | 28.5 °C | 28.5 °C | 28.0 °C |
| 20:23 | ~64.8 Hz | 1.51 kW | 28.8 °C | 28.8 °C | 28.3 °C |
| 20:30 | ~65.7 Hz | 1.57 kW | 29.1 °C | 29.1 °C | 28.6 °C |
| 20:35 | 66.8 Hz | 1.58 kW | 29.1 °C | 29.1 °C | 28.7 °C |

The gap is now exactly 0.5 K at each write (shrinking to ~0.3–0.4 K until the next write as the inlet rises). The ramp drops to ≈ 0.16 Hz/min (steps of ~1 Hz every ~5 min) but does not stop: any persistent positive gap keeps the controller's integrator rising. Planned level throughout: 0.53 kW.

Earlier observation on the same install (separate review): the compressor can hold 26–31 Hz / 500–600 W, but only while the gap set-point − inlet stays at or below ~0.5 K, i.e. when the inlet actually reaches the set-point. Ramp rate there was roughly 0.9 Hz/min per kelvin of gap.

## Why the current design cannot settle

- Floor value = inlet + lift, recomputed from the live inlet ⇒ gap ≥ lift for as long as the step heats.
- An integrating controller only reduces speed when gap ≤ 0 ⇒ it never does, short of the ceiling (`flow_heat_c`) or the gate.
- At low planned levels the ceiling is never reached, so speed rises monotonically until the step ends.
- Side effect: measured power is consistently above the planned level, so learners that read measured power (capacity curve, COP, power range) see a level the plan never asked for.

## Proposal: power feedback on the water set-point

While a step heats and the pump is running (measured power above a small running threshold, not defrosting):

1. Error `e = P_measured − P_planned` (electrical, kW), filtered (e.g. 2–3 min mean; the meter updates every few seconds).
2. Adjust the written set-point around the inlet instead of always above it:
   - `e > +deadband` (pump above plan): write `inlet + lift_adj`, with `lift_adj` decreasing towards `−lift_max_down` (e.g. −1 K). A target at or below the inlet makes the controller's integrator wind down.
   - `e < −deadband` (pump below plan): increase `lift_adj` towards the configured `flow_min_lift_k` and above, up to the existing level interpolation and the ceiling.
   - Inside the deadband: hold the last written value (do not re-anchor to the rising inlet).
3. Step size and rate limit per write (e.g. 0.2 K per minute) so the controller's own loop is not fought.
4. Start of a run: keep today's behaviour (inlet + lift, or more, so a stopped compressor starts past the controller hysteresis); feedback begins after a start-hold time (e.g. 5 min, covers the start programme).
5. Never write above the ceiling, never below the gate floor; the gate still ends the step.
6. Only with a water set-point unit and a configured `heat_pump_power_entity`; otherwise unchanged. Optionally behind an option (default off for one release) if you prefer.

The house-side planning is untouched: the plan still decides kW per step; the water temperature becomes the result of delivering that power into the slab, which is what the planner assumes anyway.

## Acceptance (what we can verify on this install)

- With a pinned space slot at the modulation floor, compressor frequency settles (no monotonic rise over 30 min); mean electrical power within ±20 % of the planned level after the start-hold.
- With a higher planned level, power follows the level within the same tolerance.
- No additional compressor starts compared with today.
- No behaviour change for `space_setpoint_unit: indoor` or without a power entity.

We can run the acceptance test on this install and report the same history tables.
