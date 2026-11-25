import sys
KEYS = {
"19404e3632806509": (2554, "floor_temp = min(T_upper, T_slab)", "floor_temp = (T_upper)", "the coldest-store floor of the energy bound drops the slab"),
"beeb068352333132": (2573, ") / max(dt_hours, 1e-6)", ") / (dt_hours)", "the wood-tank energy bound loses its dt floor"),
"ea9c4705de428b28": (2576, ") / max(dt_hours, 1e-6)", ") / (dt_hours)", "the heat-pump-tank energy bound loses its dt floor"),
"98853a541b6b5d6a": (2581, "hp_draw = min(drawn - wood_draw, max(avail_hp, 0.0))", "hp_draw = min(drawn - wood_draw, (avail_hp))", "a negative availability is no longer floored at zero"),
"fdf5872fd576c405": (2581, "hp_draw = min(drawn - wood_draw, max(avail_hp, 0.0))", "hp_draw = (drawn - wood_draw)", "the heat-pump tank draw is no longer capped by what it holds"),
"39041ccf21eedba6": (2583, "if drawn > delivered > 0.0:", "if False:", "a partly starved two-tank step no longer scales the emitter draw down"),
}
for key, (line, old, new, what) in KEYS.items():
    open(f"probe_{key}.py", "w").write(f'''#!/usr/bin/env python3
# Metric: number of grid inputs (of 34992) on which _valve_two_zone_delivery's 5-tuple (q_rad, q_floor, wood_draw, q_wood_loss, C_w)
#   differs between baseline and mutant; plus the same count restricted to ordinary dt_hours (>= 0.25) and to dt_hours < 1e-6.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g45/probes/probe_{key}.py
# EXPECTED RESULT baseline-vs-baseline moved=0 (null); inputs_moved>0 (see FIRST combo)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g45 (4 vCPU Xeon @ 2.10GHz), provisional.
# Instrumented symbol: thermal_model.py:{line} _valve_two_zone_delivery `{old}`
#   (called from _simulate_step_two_zone, thermal_model.py:3963).
# Perturbation: key {key}, `{old}` -> `{new}` ({what}), in an in-memory module copy. Direction: output changes.
# Null control: the same grid run baseline vs baseline (identical module text) moves 0 inputs.
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import valvecommon as v
base_n, base_moved, _, _ = v.run({line}, {old!r}, {old!r})
print(f"RESULT null_moved={{base_moved}} count")
n, moved, first, worst = v.report({line}, {old!r}, {new!r})
for label, dts in (("ordinary_dt_ge_0.25", (0.25, 1.0)), ("tiny_dt_lt_1e-6", (0.0, 1e-7))):
    g = dict(T_up=(18.0, 21.0, 24.0), T_sl=(15.0, 21.0, 27.0), T_buf=(25.0, 40.0, 60.0), T_w=(30.0, 55.0, 80.0),
             tp=(0.0, 1.0, 6.0), ext=(0.0, 2.0, 10.0), loss=(0.0, 0.1, 3.0), tgt=(None, 35.0), dt=dts, two=(True, False))
    gn, gm, _, _ = v.run({line}, {old!r}, {new!r}, g)
    print(f"RESULT moved_{{label}}={{gm}} of {{gn}} count")
''')
