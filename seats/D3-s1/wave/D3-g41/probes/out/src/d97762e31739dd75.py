#H Metric: count of inputs on which ThermalModel._simulate_step_two_zone's next state (every ThermalState field) or its
#H   _step_wood_refused differs between `dT_wood > dT_wood_cap` and `>=`, on a two-tank (4-way, wood tank) plant; plus the
#H   forced tie: _two_tank_rates patched (both arms) to return dT_wood == dT_wood_cap == 0 with the wood tank at its cap.
#H EXPECTED RESULT moved_inputs=0 count ; tie_moved=0 count (at the tie the cap assignment is a no-op and refused = 0)
#H Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel._simulate_step_two_zone, line 4003
#H   `if dT_wood > dT_wood_cap:`.
#H Perturbation: key d97762e31739dd75 CMP_BOUND `>` -> `>=`, in memory, patched onto ThermalModel. Direction if it moved:
#H   refused heat 0 -> nonzero at the tie.
#H Null control: baseline against itself.
#INCLUDE _tm_common.txt
mut = mutant(TM._simulate_step_two_zone, "            if dT_wood > dT_wood_cap:", "            if dT_wood >= dT_wood_cap:")
p = tm.ThermalParameters(two_zone_enabled=True, mixing_valve_mode="manual", wood_tank_configured=True)
assert p.two_tank_modelled, "fixture is not a two-tank plant"
CAP = tm.WOOD_TANK_MAX_TEMP


def step(fn, st, pw, out, dt, rates=None):
    model = TM(p)
    with mock.patch.object(TM, "_simulate_step_two_zone", fn):
        if rates is not None:
            with mock.patch.object(tm, "_two_tank_rates", rates):
                o = outcome(model._simulate_step_two_zone, st, pw, out, dt_hours=dt)
        else:
            o = outcome(model._simulate_step_two_zone, st, pw, out, dt_hours=dt)
    return o, getattr(model, "_step_wood_refused", None)


tried = moved = reached = null = 0
for wood in (CAP - 20.0, CAP - 1.0, CAP - 1e-9, CAP, CAP + 1.0):
    for buf in (30.0, 50.0, 70.0):
        for pw in (0.0, 1.0, 3.0):
            for out in (-10.0, 0.0, 10.0):
                for dt in (0.25, 1 / 12):
                    st = tm.ThermalState(upper_floor_temperature=21.0, lower_floor_temperature=21.0, slab_temperature=22.0,
                                         buffer_tank_temperature=buf, wood_tank_temperature=wood)
                    (b, rb), (m, rm) = step(TM._simulate_step_two_zone, st, pw, out, dt), step(mut, st, pw, out, dt)
                    tried += 1; reached += b[0] == "ok"
                    moved += not (same(b, m) and rb == rm)
                    n, rn = step(TM._simulate_step_two_zone, st, pw, out, dt)
                    null += not (same(b, n) and rb == rn)
print(f"RESULT inputs_tried={tried} count")
print(f"RESULT inputs_ok={reached} count")
print(f"RESULT moved_inputs={moved} count")
print(f"RESULT null_moved={null} count")
real = tm._two_tank_rates
tie = lambda *a: (real(*a)[0], 0.0)  # noqa: E731 - dT_wood forced to the cap (0 at the cap)
st = tm.ThermalState(upper_floor_temperature=21.0, lower_floor_temperature=21.0, slab_temperature=22.0,
                     buffer_tank_temperature=50.0, wood_tank_temperature=CAP)
(b, rb), (m, rm) = step(TM._simulate_step_two_zone, st, 2.0, 0.0, 0.25, tie), step(mut, st, 2.0, 0.0, 0.25, tie)
print(f"RESULT tie_refused_baseline={rb!r} kWh")
print(f"RESULT tie_refused_mutant={rm!r} kWh")
print(f"RESULT tie_moved={int(not (same(b, m) and rb == rm))} count")
print(f"RESULT tie_state_ok={int(b[0] == 'ok')}")
