Check r10-feedback-settle-large-lift (non-gating, S): does the power-feedback loop settle to the planned draw after a large floor lift? Result: harness repaired and extended; over-draw is not established beyond the synthetic controller, so no production code changes and the refusal is recorded below.

## Head

d025fb38f5125380d29d025934409e1de579be6a, cut from origin/main 50373173d486faf394b24637c177ab38b691b394, measured Sat 2026-11-14 UTC.

## Mutation proof

n/a: no production change (step 4's condition not met). The only diff is `dev/audit/harnesses/r10_water_setpoint_feedback.py`.

## Null control

Step 1, failing run at main (`PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_water_setpoint_feedback.py`): `TypeError: cannot create weak reference to 'types.SimpleNamespace' object` at `off_restore.py` `_armed_record` (`_RECORDS.get(entry)`). After the stand-in config entry became a plain class (`_Entry`), the same command runs to the end and prints its original rows (the loop-default arm reads settled, the loop-off arm does not).

Step 2 null control: each lift arm is run twice inside `lift_row`; every row prints `repeat identical True`.

## Figures

Command for all rows: `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_water_setpoint_feedback.py --lift`. Plan 0.53 kW for 3 h books 1.59 kWh. Settle minute = first minute from which the 5-minute mean draw stays within 20 % of plan to the run's end; "within one step" = settle at or before minute 15.

| lift K | loop | drew kWh | last 30 min kW | settle minute | within one plan step |
|---|---|---|---|---|---|
| 0.5 | on | 2.29 | 0.526 | 103 | no |
| 2 | on | 2.92 | 0.544 | 149 | no |
| 4 | on | 4.75 | 1.159 | never | no |
| 6 | on | 5.31 | 1.361 | never | no |
| 0.5 / 2 / 4 / 6 | off | 5.76 / 6.43 / 6.52 / 6.55 | 2.222 | never | no |

Settles within the run: 0.5 K and 2 K only. Within one 15-minute step: none, loop on or off. Arms with the controller hysteresis at 0.5 K and at the lift print identical rows (the lift, not the hysteresis, is what the model reads). The loop trims 60 % of the loop-off over-draw at 0.5 K, 55 % at 2 K, 27 % at 4 K, 19 % at 6 K, so the loop's rate (`FEEDBACK_RATE_K_PER_MIN` 0.2 K/min after the 5-minute `FEEDBACK_START_HOLD`) is the limit: a 4 K lift needs about 20 min of wind-down by its arithmetic, and the synthetic controller's integration lag dominates the rest.

These rows reproduce the analysis seat's unverified first reading to the digit (same synthetic controller).

Limits of the model: one synthetic integrating controller (`draw_kw`, a linear 0.0269 kW/Hz speed-to-power map; 0.9 Hz per K per minute integration; 3-minute fixed-speed start programme), the plan floor at 0.53 kW, one seed, magnitudes illustrative. It does not carry a real return-temperature response, defrost or a real hysteresis stop.

Step 3, reality check: `git ls-files tests dev/audit` holds no recording with per-minute power and set-point after a start. The only bundles (`dev/audit/rounds/round9/prestudy/runs/day1-bundle.json.gz`, `.../week/bundle.json.gz`) are generated (their generator is not in the tree), at 15-minute cycle rows whose keys include no measured power and no set-point. The reporting install's runs (#3380) are cited in `pump_arbiter.py` but their traces are not in the tree. No measured settle time exists to set against the harness's.

Step 4 refusal: over-draw is established only on the synthetic controller, so `pump_arbiter.py` is unchanged. A candidate (start the run at the lower of the lifted floor and the last settled trim, or wind down faster after the start hold) would be tuned to the synthetic integration lag; it needs a real trace first.

## Red checks

none at the time of writing; `prepr.sh` result below.

## Forward-carry

none

## Friction

harness-docs: stale: `dev/audit/harnesses/r10_water_setpoint_feedback.py` docstring named `PYTHONPATH=tests/hastub:custom_components:tests` yet crashed at main on a SimpleNamespace stand-in; fixed here. Carry: dismissed: repaired in this diff.
