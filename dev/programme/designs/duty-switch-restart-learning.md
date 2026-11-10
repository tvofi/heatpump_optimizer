# A duty switch can cost a compressor start: learn it per pump, then plan around it

## Summary

On some pumps a switch from hot water to space heating stops the compressor even though both duties are planned on: the controller judges the new heating request on a sensor the hot-water leg has just heated, sees no demand, stops, and restarts minutes later. Each such switch costs one compressor start and several minutes without delivery. On other pumps the same switch keeps the compressor running, so this has to be learned per install, not configured.

HPO does not see it today. The cycling penalty prices swings in the *combined* planned draw (`optimizer.cycling_penalty` over space + DHW), so a hot-water → space switch at constant total power costs nothing. No learner observes what a duty switch does to a running compressor.

Proposal: observe duty-switch episodes, learn per direction how often a switch while running ends in a stop and how long the pump then stays off. Then price planned transitions with that, and let the arbiter avoid the costly direction where it chooses the order itself. Behaviour is unchanged until an install has enough evidence and a learned probability above a threshold.

## Install

alpha innotec LWDV 91-1/3 (air/water, inverter), Luxtronik 2.1, firmware V3.92.3, controlled through its Smart Home Interface (Modbus/TCP, integration Bankaifan/ha-luxtronik-shi). HPO v7.1.9, Pump duty control = Control, optimisation interval 15 min, `heat_pump_mode_entity` = a select with `heating` / `dhw_hot_water` / `heating_dhw`, `space_setpoint_unit: return`, `flow_heat_c` 32 °C, `compressor_freq_sensor` and `heat_pump_power_entity` configured. One 600 l combined tank (#3225). Controller heating hysteresis 0.5 K. The controller's return sensor sits in the shared condenser circuit, so it reads the hot-water leg's temperature while hot water is made.

Signals used below, all outside HPO: the controller's status (`hot_water` / `heating` / `no_request` / `defrost`), its compressor-running flag, its return sensor; plus HPO's own mode and return set-point writes and the compressor frequency.

## Measurements (2026-11-10, Home Assistant history, local time)

**Hot water → heating while the compressor runs: every case after a real hot-water leg stopped**

| Mode write (HPO) | Hot-water leg before | Return at write | Return set-point written | Status → `no_request`, 0 Hz | Next compressor start | Off |
|---|---|---|---|---|---|---|
| 14:02:53 | 17 min | 44.2 °C | 32.0 °C | 14:03:12 | 14:11:24, heating, return 28.6 °C | 8.2 min |
| 14:18:53 | 3 min (return 28.4 °C → 43.6 °C) | 43.6 °C | 32.0 °C | 14:19:05 | 14:31:25, hot water, after HPO's next mode write | censored |
| 15:00:01 | 29 min | 51.0 °C | 32.0 °C | 15:00:13 | 15:08:45, heating, return 28.4 °C | 8.5 min |

The compressor stopped 12–19 s after each write. In both uncensored cases the return had been below set-point − hysteresis for several minutes before the restart, so the pump's own restart interlocks set the off time, not the cooling alone.

**Heating → hot water while the compressor runs: no stop** (03:32:32, 13:45:53, 14:15:53; each ran on in hot water until HPO's next write or supply switch-off).

**Control case:** at 13:29:53 → 13:30:07 the select went to hot water and back within 14 s (status `hot_water` for 10 s). The return did not heat up, and the compressor ran on.

The three stops are 3 of the 12 compressor starts the controller's compressor-running flag shows that day.

**Where the writes came from is not established.** Two of the three hot-water legs (3 min, and the 14:00 step's 2.9 min) are shorter than `SPLIT_MIN_MINUTES`, so they cannot be shares from `pump_arbiter._share`. They come from a step change, a re-solve or the hot-water lease (`_leased`). We could not tell which from history alone. The arbiter's step log in the diagnostics would show it, and attributing each episode is the first acceptance step below. The proposal therefore does not rely on `_share` being the cause.

## Relation to #3405 (power feedback on the water set-point)

#3405 does not cover this case, by our reading of its head:

- the target never exceeds the ceiling (`_feedback_bounds`: `highs = [_heat_ceiling_c, …]`, here 32 °C);
- a run's first `FEEDBACK_START_HOLD` writes today's base;
- `_note_stop` learns only stops the loop caused (`sent_c < base`).

With a 44–51 °C inlet after a hot-water leg, every write is below the inlet, and the stop is not attributed to anyone. The two are complementary. #3405 is also the precedent for what this proposes: `held.stop_gap_k` learns from an observed stop how the controller reacts, and bounds later writes by it.

## Why this has to be learned, not configured

Whether a switch stops the compressor depends on things HPO cannot read from a datasheet. That includes which sensor gates the heating request, whether it sits in the leg the diverter valve just used, the controller's hysteresis and restart interlocks, and the set-point unit HPO writes. A pump with a separate buffer sensor, or one that keeps the compressor running through a valve change, will never show it. The effect is observable from what HPO already holds: its own mode write and the compressor's running state.

Scope: installs whose mode entity offers single duties (the select transport). On the set-point gate transport (no single-duty mode, `desired`'s `both` branch with a lowered gate), a duty change is a set-point change, and this learner sees nothing. That needs its own episode definition and is out of scope here.

## Proposal

### 1. Observe: duty-switch episodes

An episode opens where the arbiter writes a mode that changes the served single duty (`dhw` → `space` or `space` → `dhw`). That is in `_command`, when the mode slot is written. The episode is recorded on `ArbiterState` and persisted with it. It counts only if all of these hold at the write:

- the compressor runs. Use `compressor_freq_sensor` above zero where configured, else the measured power at or above `thermal_model.on_threshold_kw`;
- the source leg has heated the circuit. Where a return or flow entity is configured, require `return_at_write − target set-point ≥ hysteresis margin` (proposal: 2 K; the stopped cases here were 12–19 K, the 14-s control case near 0). Without one, require the source leg to have lasted at least `T_SRC`. 1 min is a guess, chosen between the 14-s control case and the 3-min stopped one;
- the target duty has demand by HPO's own reading: for space, the room is below the plan's room temperature for the step (`_planned_room`); for hot water, the tank is below its set-point. This separates the sensor artefact from a genuine no-demand stop;
- the plan keeps the pump on for the target duty for the whole window.

Outcome within `W_STOP` (proposal: 3 min; the stops here came after 12–19 s):

- **stopped**: the running signal drops;
- **kept**: still running at `W_STOP`;
- **void**: anything else could explain a stop inside the window. That covers a supply switch-off, a gate set-point, another mode write, defrost, a fault, a boost, a manual change, a disinfection hold, an active immersion element (the meter then mixes compressor and resistive draw; `wear.StartCounter` freezes on it for the same reason), or an unavailable running signal.

**Off time** of a stopped episode runs until the compressor runs again. It is censored, not used, if HPO wrote the mode, the supply or a set-point in between: row 2 above is censored.

The running signal is read by its own edge listener: debounced, emitting only running → stopped and back. It must not go into the arbiter's `_listen`, which runs a full pass on every state change, while an inverter's frequency changes constantly. The peak guard's throttled meter listener is the pattern.

### 2. Estimate

Per direction `d ∈ {dhw→space, space→dhw}`:

- `p_d = k_d / n_d` on exponentially time-decayed counts (proposal: half-life 14 days), so evidence fades by age, not only by new episodes. Once stage 3 avoids a costly direction, that direction produces fewer episodes. The decay lets `p_d` fall back under the threshold, the default behaviour runs again, and the next episodes re-test it. That is how a firmware or setting change gets relearned;
- `p_d` is used only when the decayed `n_d ≥ N_MIN` (proposal: 5) and the episodes span at least two days. Below that, `p_d` counts as 0, which is today's behaviour;
- `t_off,d` is the median of uncensored off times.

Publish `p_d`, `n_d` and `t_off,d` as diagnostics, for example on the compressor-starts sensor, so a user can see what was learned.

### 3. Use

Every use is gated on `p_d ≥ P_ON` (proposal: 0.5). Below it, nothing changes.

**a. Planner (origin-agnostic, the main lever).** Price every planned transition `d` while the pump runs at `p_d × effective cycling cost`. Treat `t_off,d` as a period without delivery in the planner's own simulation of that step. Hot water then moves next to planned stops, or before a space block instead of into it. This covers step changes and re-solves, which the arbiter cannot reorder. Where it belongs depends on how the hot-water schedule (`dhw_planner.py`) and the space schedule are coupled in the solve. That is your call.

**b. Arbiter, where it picks the order itself (`_share`).** For a planned "both" step whose costly direction is `dhw→space` and whose other direction is not, serve space first, then hot water. The order is latched per step on `ArbiterState`, so the 1-min tick and a mid-step re-solve cannot flip it. This does not remove a `dhw→space` switch at the boundary to the next step, which only (a) can.

**c. Arbiter, minimum share.** If the second share would enter the costly direction and is shorter than `t_off + SPLIT_MIN_MINUTES`, give the whole step to the first duty. With `t_off` of 8–9 min that is true for essentially every 15-min step. In effect this means "never split into the costly direction". The step's planned second share is then not delivered in this step, and the next re-solve sees and replans it. That is a comfort or tank trade-off the planner absorbs; it is not hidden.

The lease (`_leased`) can also end a hot-water stretch into a space duty. Whether it should wait for a planned stop when `p_dhw→space ≥ P_ON` is worth considering, but it is not proposed here, because the lease protects comfort.

**Considered and not proposed:** bridging the switch with a temporarily higher space set-point (above the hot inlet), so the controller keeps running. It would bypass `flow_heat_c`, which protects floor heating without a mixing valve. A general integration should not do that.

### 4. Related: the start counter misses short cycles

`wear.StartCounter` is fed once per optimisation interval (`coordinator._record_accuracy` → `_observe_compressor_start`; 15 min here, default 30) and needs `START_HYSTERESIS_SAMPLES = 2` consecutive samples past `on_threshold_kw`. Runs and pauses shorter than about two intervals are invisible. On 2026-11-10 it counted 5 starts against the 12 the controller's compressor flag shows. That feeds `wear_autotune_enabled` and the monthly receipt. The edge listener from step 1 could feed the counter instead. That is a separate fix on the same signal.

### Side observation

When HPO switches the supply on after an idle period, the mode follows 5–29 s later on this install (01:51:18 → 01:51:31, 03:00:03 → 03:00:08, 09:16:37 → 09:17:06, 10:56:52 → 10:57:07). Idle writes no mode (`desired`). The arbiter writes nothing while the switch reads off (`_pump_off`), and switching the supply on triggers no pass, so the mode waits for the next tick. Meanwhile the select still reads hot water only, and the controller raises a hot-water request (status `hot_water` for about 10 s) before the heating mode arrives. No compressor start resulted here, but a controller that starts faster would start in the wrong duty. Writing only the mode for the new step just before the supply goes on would avoid it, without lifting the reason `_pump_off` exists.

## Acceptance (what we can verify on this install)

1. Attribute each observed `dhw→space` episode to its origin (split, step change, re-solve, lease) from the arbiter's step log, and report how many of the stops (a), (b) and (c) would each have prevented.
2. After `N_MIN` decayed episodes over at least two days, the learner publishes `p_dhw→space ≥ 0.5`, and `p_space→dhw` stays below 0.5.
3. With the uses active, a day with comparable hot-water load shows fewer switch-caused stops (status `no_request` within `W_STOP` of an HPO mode write while running, outside the void cases). Compressor starts per day drop by that count.
4. On an install below `N_MIN`, or with every `p_d < P_ON`, plan, split order and shares are identical to today's.
5. With step 4: the start counter matches the controller's compressor flag within ±1 start per day.

We can run this on the install above and report the same tables.
