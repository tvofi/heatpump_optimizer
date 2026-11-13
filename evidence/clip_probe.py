"""Reviewer's probe (builder: the fix-review seat). Repair 2 removed np.clip(start, 0, p_max)
from optimizer._stop_availability; this compares the head's function on a raw start with the
same function on the clipped start (what the removed line computed), over starts outside the band."""
import sys, itertools, inspect
from types import SimpleNamespace as NS
import numpy as np
sys.path.insert(0, ".")
from custom_components.heatpump_optimizer import optimizer as O, duty_legs
print("duty_floor src:", inspect.getsource(O._duty_floor).strip().replace("\n", " | ")[:400])
rng = np.random.default_rng(3526)
n = mism = none = ctl = 0
for clamp, p_min, p_max, pair, offs in itertools.product(
        (False, True), (0.0, 0.8, 1.5), (3.0, 5.5), ((1.0, 0.0), (0.0, 1.0), (0.6, 0.9)), ((501.0, 0.0), (0.0, 300.0), (501.0, 240.0))):
    opt = NS(config=NS(clamp_planned_levels=clamp, duty_switch_stop_probability=pair, duty_switch_off_seconds=offs,
                       cycling_cost=0.3, time_step_hours=0.25, dt_hours=0.25),
             model=NS(params=NS(min_electrical_power=p_min, max_electrical_power=p_max)), _levels_relaxed=False)
    for trial in range(60):
        T = 24
        start = rng.choice([-2.0, -0.3, -0.0, 0.0, 0.2, p_min, p_min * 0.5, 1.0, p_max - 0.1, p_max, p_max + 0.4, 2 * p_max, 9.0], T) + rng.choice([0.0, 0.0, 0.01, -0.01], T)
        dhw = rng.choice([0.0, 0.0, 0.3, p_min, 1.2, p_max * 0.5, p_max, p_max + 0.5], T)
        try:
            a = O._stop_availability(opt, start.copy(), dhw.copy(), p_max)
            b = O._stop_availability(opt, np.clip(start, 0.0, p_max), dhw.copy(), p_max)
        except AttributeError as e:
            print("FAKE-OPT MISSING ATTRIBUTE:", e); sys.exit(2)
        n += 1
        c = O._stop_availability(opt, np.clip(start, 0.0, 0.5 * p_max), dhw.copy(), p_max)
        ctl += (a is not None and c is not None and not np.array_equal(np.asarray(a), np.asarray(c), equal_nan=True))
        if a is None or b is None:
            none += 1; mism += (a is None) != (b is None); continue
        if not np.array_equal(np.asarray(a), np.asarray(b), equal_nan=True):
            mism += 1
            if mism <= 3: print("MISMATCH clamp", clamp, p_min, p_max, pair, offs, "\n start", start, "\n dhw", dhw, "\n raw", a, "\n clip", b)
print(f"RESULT clip_probe_cases={n} none={none} compared={n-none} mismatches={mism}")
print(f"RESULT clip_probe_null_control_clip_at_half_pmax_moves={ctl}")
# does the vector vary at all on these inputs (the probe is not reading a constant)?
opt = NS(config=NS(clamp_planned_levels=True, duty_switch_stop_probability=(1.0, 0.0), duty_switch_off_seconds=(501.0, 0.0), cycling_cost=0.3, time_step_hours=0.25, dt_hours=0.25),
         model=NS(params=NS(min_electrical_power=0.8, max_electrical_power=3.0)), _levels_relaxed=False)
v = O._stop_availability(opt, np.array([0., 2., 2., 0., 2.]), np.array([2., 0., 0., 2., 2.]), 3.0)
print("RESULT clip_probe_vector_varies=", v is not None and len(set(np.round(np.asarray(v, float), 6))) > 1, v)
print("planner_fields src:"); from custom_components.heatpump_optimizer import duty_switch
print(inspect.getsource(duty_switch.planner_fields))
