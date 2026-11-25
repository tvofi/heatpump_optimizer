#H Metric: ThermalModel._simulate_step_two_zone's next buffer temperature (or the exception) on a throttled single-tank
#H   plant whose tank charges toward buffer_max_temp, across dt_hours including 0 and below the 1e-6 floor; count of
#H   inputs that differ between `/ max(dt_hours, 1e-6)` and `/ (dt_hours)`.
#H EXPECTED RESULT production_moved=0 count (dt_hours >= 1e-6: the floor is inert) ; dt0 and dt<1e-6 may move
#H Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel._simulate_step_two_zone, line 4019
#H   `dT_cap = max(0.0, p.buffer_max_temp - T_buf) / max(dt_hours, 1e-6)`.
#H Perturbation: key c5e678a5d1812e40 CLAMP_DROP `max(dt_hours, 1e-6)` -> `(dt_hours)`, in memory. Direction: at dt 0,
#H   finite -> ZeroDivisionError; below 1e-6, the cap admits more heat (tank lands exactly at the cap).
#H Null control: dt_hours in production's range (0.25, 1/12, 1/60 and the substep sizes), where the floor is inert.
#INCLUDE _tm_common.txt
mut = mutant(TM._simulate_step_two_zone,
             "            dT_cap = max(0.0, p.buffer_max_temp - T_buf) / max(dt_hours, 1e-6)",
             "            dT_cap = max(0.0, p.buffer_max_temp - T_buf) / (dt_hours)")
p = tm.ThermalParameters(two_zone_enabled=True, mixing_valve_mode="manual")
assert not p.two_tank_modelled


def step(fn, st, pw, out, dt):
    with mock.patch.object(TM, "_simulate_step_two_zone", fn):
        return outcome(TM(p)._simulate_step_two_zone, st, pw, out, dt_hours=dt)


prod = (0.25, 1 / 12, 1 / 60, 0.25 / 8, 1e-3, 1e-6)
tiny = (5e-7, 1e-7, 1e-9, 0.0)
pm = tm_ = 0
for dt in prod + tiny:
    mv = 0
    for buf in (40.0, 69.0, 69.9999999, 70.0, 75.0):
        for pw in (1.0, 5.0):
            st = tm.ThermalState(upper_floor_temperature=21.0, lower_floor_temperature=21.0, slab_temperature=22.0,
                                 buffer_tank_temperature=buf)
            b, m = step(TM._simulate_step_two_zone, st, pw, 0.0, dt), step(mut, st, pw, 0.0, dt)
            mv += not same(b, m)
            if buf == 69.9999999 and pw == 5.0:
                bb = b[1].buffer_tank_temperature if b[0] == "ok" else b[1]
                mb = m[1].buffer_tank_temperature if m[0] == "ok" else m[1]
                print(f"RESULT dt{dt:g}_buf_baseline={bb!r} ; dt{dt:g}_buf_mutant={mb!r}")
    print(f"RESULT moved_dt{dt:g}={mv} count (of 10)")
    if dt in prod:
        pm += mv
    else:
        tm_ += mv
print(f"RESULT production_moved={pm} count")
print(f"RESULT below_floor_moved={tm_} count")
