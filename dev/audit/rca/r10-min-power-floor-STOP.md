# r10-min-power-floor: stopped for a design (issue 3289)

Fixer seat, base 4b5d771bdf8feb1f83d7d9443e5117b771a0ab76 (origin/main at the run). No production code changed.

## Measurement (the brief's MEASURE FIRST)

The reporting hypothesis is refuted. A merged slot averages only its own heating steps
(`plan_slots.plan_slots`, steps from `thermal_model.channel_heating_steps`), so a 6 h slot
averaging 0.4 kW cannot be made of steps at or above 2.5 kW: the steps themselves are below
the floor.

Harness `dev/audit/harnesses/r10_min_power_floor.py` (sha1 e21d29905d30bc08dcb8ec4cc1427c8ce824419d),
min 2.5 / max 3.5 kW, 96 x 15 min steps, rule: a step runs when space+DHW > 0.1 kW
(`MIN_RUNNING_DRAW_KW`) and counts when that total is < 2.5 kW.

```
clamp=False prices=spread dhw=False out=-4.0: steps_on=34 total_below_min=0 space_steps_below_min=0 slots=2 min_slot_avg=3.5 cost=30.869
clamp=False prices=spread dhw=False out=5.0: steps_on=19 total_below_min=0 space_steps_below_min=0 slots=2 min_slot_avg=3.5 cost=14.825
clamp=False prices=spread dhw=True out=-4.0: steps_on=43 total_below_min=7 space_steps_below_min=4 slots=2 min_slot_avg=3.2 cost=37.317
clamp=False prices=spread dhw=True out=5.0: steps_on=26 total_below_min=5 space_steps_below_min=1 slots=2 min_slot_avg=3.25 cost=19.497
clamp=False prices=flat dhw=False out=-4.0: steps_on=85 total_below_min=62 space_steps_below_min=62 slots=2 min_slot_avg=1.42 cost=57.823
clamp=False prices=flat dhw=False out=5.0: steps_on=41 total_below_min=27 space_steps_below_min=27 slots=4 min_slot_avg=0.13 cost=28.815
clamp=False prices=flat dhw=True out=-4.0: steps_on=84 total_below_min=55 space_steps_below_min=64 slots=2 min_slot_avg=1.45 cost=63.745
clamp=False prices=flat dhw=True out=5.0: steps_on=54 total_below_min=39 space_steps_below_min=39 slots=3 min_slot_avg=0.31 cost=33.794
clamp=True prices=spread dhw=False out=-4.0: steps_on=34 total_below_min=0 space_steps_below_min=0 slots=2 min_slot_avg=3.5 cost=30.869
clamp=True prices=spread dhw=False out=5.0: steps_on=20 total_below_min=0 space_steps_below_min=0 slots=2 min_slot_avg=3.39 cost=14.876
clamp=True prices=spread dhw=True out=-4.0: steps_on=45 total_below_min=0 space_steps_below_min=0 slots=4 min_slot_avg=2.5 cost=38.844
clamp=True prices=spread dhw=True out=5.0: steps_on=26 total_below_min=0 space_steps_below_min=0 slots=2 min_slot_avg=3.39 cost=20.652
clamp=True prices=flat dhw=False out=-4.0: steps_on=53 total_below_min=0 space_steps_below_min=0 slots=2 min_slot_avg=2.5 cost=58.944
clamp=True prices=flat dhw=False out=5.0: steps_on=9 total_below_min=0 space_steps_below_min=0 slots=1 min_slot_avg=3.39 cost=32.407
clamp=True prices=flat dhw=True out=-4.0: steps_on=40 total_below_min=0 space_steps_below_min=0 slots=1 min_slot_avg=3.4 cost=67.571
clamp=True prices=flat dhw=True out=5.0: steps_on=20 total_below_min=0 space_steps_below_min=0 slots=1 min_slot_avg=3.47 cost=39.167
```

- `clamp_planned_levels=False` (the duty-cycle reading): sub-minimum running steps in 6 of 8
  cells; flat prices put 27 of 41 (out 5 C) and 62 of 85 (out -4 C) running steps below 2.5 kW,
  with space steps of 0.01-0.23 kW and a slot averaging 0.21 kW -- the shape the issue reports.
- `clamp_planned_levels=True`, identical inputs (null control): 0 sub-minimum steps in all 8 cells.
- Flat-price control on cost: the flat-price cells are in the table; the cost figures above are
  objective values under each arm and are not a savings claim.

## Why this stops

The solver treats `heat_pump_min_power` as the bottom of a modulation band, and a level in
`(0, p_min)` as a duty-cycle average (#1955). The floor is honoured only by the post-solve
projection `thermal_model.project_planned_levels`, which ships only when `levels_clamped`
holds: `probe_install` sees a switch plus a setpoint write and no frequency entity or sensor.
`duty_cycle_realizable` lets `clamp_planned_levels: false` opt out but offers no opt-in, so a
non-modulating pump on any other write surface, or with a frequency sensor, plans sub-minimum
steps. Honouring the minimum as an on/off floor for those installs is a choice between (a) an
explicit non-modulating declaration that forces the existing projection (and its relaxed-start
scoring, `optimizer._relaxed_starts`), (b) an on/off (integer) constraint in the solve, or
(c) changing the probe's default; each changes which installs the #1955 design clamps and the
goldens of those installs. Per the brief, this is size L for `designer.md` before any fixer.

## For the designer

- Rerun the harness above at both ends; its clamp=True arm is the control.
- The reporter's config surface (which entities they map) is not in the issue; the design must
  not assume it is switch plus setpoint.
- With clamp=False and DHW on, slot averages stay above 2.5 kW while 5-7 running steps are below
  the floor (time-shared steps): a slot-average test does not detect this, a per-step one does.
