"""Shared driver of the _valve_two_zone_delivery probes: evaluates baseline and one-line mutant over a grid."""
import itertools, math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import mutmod

def run(line, old, new, grid=None):
    base, mut = mutmod.load(line, old, new)
    def call(m, T_up, T_sl, T_buf, T_w, tp, ext, loss, tgt, dt, two):
        p = m.ThermalParameters(); p.wood_tank_configured = True
        s = m.ThermalState(); s.upper_floor_temperature = T_up; s.slab_temperature = T_sl
        s.buffer_tank_temperature = T_buf; s.wood_tank_temperature = T_w
        try:
            return tuple(float(x) for x in m._valve_two_zone_delivery(p, s, tp, ext, loss, tgt, 5.0, 0.2, dt, two))
        except ZeroDivisionError:
            return ("ZeroDivisionError",)
    grid = grid or dict(
        T_up=(18.0, 21.0, 24.0), T_sl=(15.0, 21.0, 27.0), T_buf=(25.0, 40.0, 60.0), T_w=(30.0, 55.0, 80.0),
        tp=(0.0, 1.0, 6.0), ext=(0.0, 2.0, 10.0), loss=(0.0, 0.1, 3.0), tgt=(None, 35.0), dt=(0.0, 1e-7, 0.25, 1.0), two=(True, False))
    n = moved = 0; first = None; worst = 0.0
    for combo in itertools.product(*grid.values()):
        b, m = call(base, *combo), call(mut, *combo)
        n += 1
        if b != m:
            moved += 1
            if first is None: first = (combo, b, m)
            if len(b) == len(m) == 5: worst = max(worst, max(abs(x - y) for x, y in zip(b, m)))
            else: worst = max(worst, float("inf"))
    return n, moved, first, worst

def report(line, old, new, grid=None):
    n, moved, first, worst = run(line, old, new, grid)
    print(f"RESULT inputs_tried={n} count")
    print(f"RESULT inputs_moved={moved} count")
    print(f"RESULT max_abs_diff={worst!r}")
    if first:
        print("FIRST combo(T_up,T_sl,T_buf,T_w,tp,ext,loss,tgt,dt,two)=", first[0]); print("  baseline=", first[1]); print("  mutant  =", first[2])
    return n, moved, first, worst
