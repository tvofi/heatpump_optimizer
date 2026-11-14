"""Enumerate entity ranges x targets; compare the head predicate, the `>` mutant and the alternative."""
import sys, math, itertools; sys.path.insert(0, 'tests')
import guard_pins as g
cycle_write = g.cycle_write if hasattr(g, "cycle_write") else __import__("custom_components.heatpump_optimizer.pump_arbiter", fromlist=["x"]).cycle_write
import importlib; L = sys.modules[g.LegionellaGuard.__module__]; H, I = L.CREDIT_HOLD_MARGIN_K, L.CREDIT_INSTANT_MARGIN_K; cycle_write = L.cycle_write
cfg = {"pump_duty_mode": "control", "dhw_setpoint_entity": "number.dhw"}
rows = diff_mut = diff_alt = raised = 0; ex_mut = []; ex_alt = []; eq_hits = 0; bad_oracle = []
def grid(unit):
    if unit == "C":
        mins = (5, 20, 30, 40, 55, 58, 60, 62, 65, 66, 70); maxs = (50, 55, 57, 58, 60, 62, 63, 64, 65, 66, 67, 68, 70, 75, 80, 90)
        steps = (0.1, 0.5, 1, 2, 2.5, 3, 5, 10)
    else:
        mins = (41, 86, 104, 131, 140); maxs = (122, 131, 140, 145, 149, 158, 176)
        steps = (0.5, 1, 2, 5, 10)
    for lo, hi, st in itertools.product(mins, maxs, steps):
        if hi > lo:
            a = {"min": lo, "max": hi, "step": st}
            if unit == "F": a["unit_of_measurement"] = "°F"
            yield a
for unit in ("C", "F"):
    for attrs in grid(unit):
        hass = g.FakeHass({"number.dhw": g.FakeState("50", attributes=attrs)})
        for d in [71.0, 72.0, 75.0, 80.0]:
            for every in (40, 50, 55, 58, 60, 62, 65, 68, 70):
                p = g.ThermalParameters(dhw_setpoint=float(every), dhw_legionella_temp=d, dhw_legionella_enabled=True, dhw_enabled=True)
                w = cycle_write(hass, cfg, p)
                if w is None: continue
                for m in (H, I):
                    rows += 1
                    short = w.written_c < d - m
                    head = short and w.above_c >= d
                    mut = short and w.above_c > d
                    alt = short and w.below_c < w.above_c
                    raised += head
                    if w.above_c == d: eq_hits += 1
                    if head != mut:
                        diff_mut += 1; ex_mut.append((unit, attrs, d, every, m, w))
                    if head != alt:
                        diff_alt += 1; ex_alt.append((unit, attrs, d, every, m, w))
print(f"RESULT out-of-slider(71-80) rows={rows} head_raised={raised} rows_with_above_eq_target={eq_hits} head_vs_gt_mutant_differ={diff_mut} head_vs_alternative_differ={diff_alt}")
for e in ex_mut[:10]: print("MUT", e)
for e in ex_alt[:10]: print("ALT", e)
