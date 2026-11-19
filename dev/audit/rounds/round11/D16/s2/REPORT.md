# D16-s2 — round 11, actuator write: timing and order (M3), effect (M4)

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. Seat D16-s2, cells M3+M4 over every file
(`check_scopes.py --seat D16-s2`). Exposure: none (no `docs/`, no GitHub).

## Method

- Universe of both steps: `python3 tools/audit/enumerate.py d16-writes --cells`, 532 lines
  (38 sites x 14 states). Every line is examined for M3 and for M4: `cells.py` runs one scenario
  per state (upgrade on a store written by the previous tag v10.0.1, exported with `git archive`
  and run in a subprocess), in two configuration arms, and attributes every service call and
  every `log_held` to its enumerator site by the caller's file and line (`rig.Attribution`;
  `unattributed_sites=0`). Per-cell verdicts: `cells_verdicts.txt`.
- Plant: `coord_all_features` with the actuators wired (switch, Tuya mode select, tank and flow
  set-points, circulation pump, ECL110 set and legacy topics, heat-curve offset entity, smart
  valve, disinfection switch); arm B adds frequency control and the persistent curve kind.
- Oracle: the plan the harness books (`rig.plan`); the step covering a minute is found by plain
  arithmetic on its timestamps and its command read by plain indexing. No oracle imports a step
  selection from `pump_arbiter`.
- Clock: minute by minute; the production cycle tail every 30 min (input read, adoption, valve,
  boost overlay, `_apply_action`, frequency, circulation pumps), the arbiter's and the supply's
  one-minute ticks every minute; a device stub applies every write to its entity.
- M4 pump model (`effect.Pump`): integrating speed loop, start and stop hysteresis, first-order
  water lag, a tank thermostat with its own hysteresis, read back through the power and return
  sensors the arbiter reads.

## Harnesses

| file | what |
|---|---|
| `rig.py` | shared rig (no RESULT lines) |
| `timing.py` | M3 walk over six cycle phases + owed cells 3478, 3530, 3512; `--perturb P1|null-docstring|lead-hold`, `--interval/--phases` |
| `disinfect.py` | M3, the disinfection switch against its booked window; `--perturb track-after-adopt` |
| `effect.py` | M4 power and starts per plant; `--cfg flow_min_lift_k=8` |
| `cells.py` | every enumerator cell, both steps; `--cells-out` |

## Findings

- **D16-s2-01** (M3, medium) frequency, ECL110 displace and the heat-curve offset are cut once
  per cycle from `_current_action` and never re-derived at a step boundary: stale share
  0.4480 / 0.5732 / 0.4644 over six phases (leave-one-out 0.41-0.73 for MQTT); 0 with a cycle on
  every boundary (null). Cell 3478: a cycle cut in a partial step and written in the next (full)
  one leaves partial's 65.5 Hz and displace 4 in force where the step's own cut writes 90 Hz and 6.
- **D16-s2-02** (M3, high) the disinfection switch follows the previous solve's action: on 0 of
  30 booked minutes and 30 minutes after; the space-only steps stay Heating (0/30 Heating + DHW).
  `track-after-adopt` gives 29/30. Null: no booking, 0.
- **D16-s2-03** (M3, low) `_lead_mode` skips the lead when the arbiter's record matches though
  the entity reads otherwise (changed while off): the switch-on lands in the hot-water mode,
  Heating one tick later. `lead-hold` gives 0; null arm 0.
- **D16-s2-04** (M4, medium) floor-level steps on a plant whose floor lift exceeds min lift plus
  stop hysteresis short-cycle: 30 starts / 0.60 kW (8 K/kW), 38 / 0.50 kW (10 K/kW) against one
  run at 1.0 kW; 2-6.5 K/kW one run. The feedback loop folds only running samples.
  `flow_min_lift_k=8` gives 1 start.

## Non-findings (held, with the number)

- Supply, mode, flow class follow the step: stale 0/1434, 0/906, 0/906 over six phases. P1 (every
  arbiter step lookup one step late) moves them to 0.4561, 0.3510, 0.6364, cell 3478's step k to
  13/13 minutes off its row and cell 3530 to a switch-on in the wrong mode; the docstring edited
  alone moves nothing (`--perturb null-docstring`: identical RESULTs).
- Cell 3530 (partial from idle): mode written before the switch-on (minute 30, Heating); 60
  switch-ons in the walk, 0 with the wrong mode.
- Cell 3512: a re-solve 3 min after a switch-on holds the off to minute 40 (run 10 min = MIN_RUN);
  one 2 min after the off holds the on to minute 50 (pause 10 min). Short runs 0, pauses 0.
- Both: DHW first then Heating in every both step (2/2 cells, 2/2 walk).
- Boost-partial: flow target at the band top (60 C) every minute of the boost.
- Unavailable: 0 calls to and 0 writes recorded for the flow entity while unavailable; partial's
  row on return (stale 0/22).
- Observe and off duty modes: 0 arbiter writes.
- Baseline: Heating + DHW and the configured 50 C in force from minute 47 (plan ended at 45).
- Restart and upgrade (v10.0.1 store): partial's row back at the first solve; the 2 stale minutes
  are the one-minute solve delay the scenario sets.
- Partial effect: |power error| <= 0.0873 on 2-8 K/kW (inside the loop's 10 % deadband), one run
  each; 10 K/kW reads 2.445 kW, capped by the 55 C heating ceiling (the solve band's job).
- Dhw-only on a 47 C tank (set-point 50, hysteresis 5): the write is the configured 50 (its row);
  0 kWh delivered, ledger `not-startable` with the hysteresis entity, `idle-instead` without.
- The perturbation P2 is step 2's (D16-s1); not run here.

## Unfinished

None: both steps closed over the 532 cells. Wall/CPU numbers: none produced (counts and ratios).

## Leads

In REPORT.json.
