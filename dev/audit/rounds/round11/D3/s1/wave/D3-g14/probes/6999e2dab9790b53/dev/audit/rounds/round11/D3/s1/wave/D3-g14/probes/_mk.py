# Writes the probe files of box D3-g14 (one per key). Run once; the probes are the harnesses.
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
P = {}

COMMON_BUILD = '''
W = parse_windows("18:00-20:00")
N = 96


def state(T=48.0, hsl=20.0, **kw):
    return ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=-5.0,
                        dhw_temperature=T, dhw_hours_since_legionella=hsl,
                        buffer_tank_temperature=40.0, **kw)


def arms(pl, h, key, **kw):
    """(baseline DhwPlan, mutant DhwPlan) of _build_dhw_requirements on one horizon."""
    b, _ = pl._build_dhw_requirements(h, **kw)
    with mutated("_build_dhw_requirements", key):
        m, _ = pl._build_dhw_requirements(h, **kw)
    return b, m


def realistic_delta(key, method="_build_dhw_requirements"):
    """Max |schedule| difference over three ordinary planning days (flat, cheap night, evening peak)."""
    pl, _ = planner(dhw_schedule_enabled=True, dhw_windows=W, dhw_min_temp=45.0)
    worst = 0.0
    for pr in (np.full(N, 1.0), np.r_[np.full(24, 0.2), np.full(72, 1.0)],
               np.r_[np.full(68, 1.0), np.full(16, 3.0), np.full(12, 1.0)]):
        h = horizon(prices=pr)
        b, _ = pl._build_dhw_requirements(h, p_max=4.0)
        with mutated(method, key):
            m, _ = pl._build_dhw_requirements(h, p_max=4.0)
        worst = max(worst, float(np.max(np.abs(b.schedule - m.schedule))))
    return worst
'''


def header(key, metric, symbol, perturb, inputs, null):
    return f'''#!/usr/bin/env python3
# Metric: {metric}
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g14/probes/probe_{key}.py
# Expected: the EXPECTED lines below (counts and kW exact to 1e-6; floats printed to 4-6 places).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g14 (cloud, 4 vCPU Intel Xeon @ 2.30GHz, Linux);
#   no timing is measured, every number is a count or a plan value (contention-immune).
# Instrumented symbol: {symbol}
# Perturbation: mutant {key} (dev/audit/rounds/round11/D3/s1/state/results/complete/{key}.json), applied IN MEMORY:
#   the method's own source re-compiled with that one line replaced (_g14lib.mutated), never on disk. {perturb}
# Inputs tried: {inputs}
# Null control: {null}
'''


def write(key, hdr, body):
    (HERE / f"probe_{key}.py").write_text(hdr + '''import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
warnings.simplefilter("ignore")
from _g14lib import *  # noqa: E402,F401,F403
''' + COMMON_BUILD + body)


# ---------------------------------------------------------------- _apply_dhw_min_run
MINRUN = '''
pl, params = planner()
n = 8
OUT, DR, MT = np.full(n, -5.0), np.zeros(n), np.full(n, 55.0)  # 55 C: the default dhw_max_temp


def call(plan, T0, fn=None):
    kw = dict(plan=np.array(plan, float), initial_temp=T0, outdoor_temps=OUT, draw_rates=DR, dt=0.25,
              p_dhw_max=3.0, min_run_power=0.6, max_temp=MT)
    return (fn or DhwPlanner._apply_dhw_min_run)(pl, **kw)


MUT = mutant_method("_apply_dhw_min_run", mutant_dict(KEY))
'''
write("3685cdbd27c1680f", header(
    "3685cdbd27c1680f",
    "max |plan| difference (kW) between baseline and mutant _apply_dhw_min_run on one plan whose entries lie outside [0, p_dhw_max] and whose weak slots all fit jointly (the line-2076 return).",
    "custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._apply_dhw_min_run line 2076 `jointly_raised = np.clip(joint, 0.0, p_dhw_max)`",
    "Direction: the mutant returns the unclipped plan (5.0 kW where p_dhw_max=3.0; -1.0 kW).",
    "plan [5.0, 0.1, 0...] and [-1.0, 0.1, 0...] at tank 30 C; in-range plan [3.0, 0.1, 0...]; the three ordinary days through _build_dhw_requirements (realistic_delta).",
    "an in-range plan ([3.0, 0.1, 0, ...]): the clip is the identity, delta 0."),
    "KEY = '3685cdbd27c1680f'\n" + MINRUN + '''
b, m = call([5.0, 0.1] + [0.0] * 6, 30.0), call([5.0, 0.1] + [0.0] * 6, 30.0, MUT)
print(f"RESULT baseline_step0_kw={b[0]:.6f} kW")
print(f"RESULT mutant_step0_kw={m[0]:.6f} kW")
b2, m2 = call([-1.0, 0.1] + [0.0] * 6, 30.0), call([-1.0, 0.1] + [0.0] * 6, 30.0, MUT)
print(f"RESULT negative_entry_delta_kw={abs(b2[0] - m2[0]):.6f} kW")
print(f"RESULT null_delta_kw={float(np.max(np.abs(call([3.0, 0.1] + [0.0] * 6, 30.0) - call([3.0, 0.1] + [0.0] * 6, 30.0, MUT)))):.6f} kW")
print(f"RESULT realistic_delta_kw={realistic_delta(KEY, '_apply_dhw_min_run'):.6f} kW")
''')

write("1c0e818b4bb24fcd", header(
    "1c0e818b4bb24fcd",
    "max |plan| difference (kW) between baseline and mutant _apply_dhw_min_run on a plan with entries outside [0, p_dhw_max] that takes the per-slot path (joint raise does not fit; the line-2106 return); and the count of 400 seeded random plans that separate.",
    "custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._apply_dhw_min_run line 2106 `repaired = np.clip(plan, 0.0, p_dhw_max)`",
    "Direction: the mutant returns entries above p_dhw_max and below 0 unclipped.",
    "plan [0,3,3,-1,0.1,5,0.3,-1] at 48.971 C (per-slot path); 400 random plans over {-1,0,0.1,0.3,3,5}^8 with tank 30..56 C (seed 0), ceiling 55 C; in-range plans; the three ordinary days (realistic_delta).",
    "the same plan with every entry in [0, p_dhw_max] ([0,3,3,0,0.1,3,0.3,0]): delta 0."),
    "KEY = '1c0e818b4bb24fcd'\n" + MINRUN + '''
P = [0.0, 3.0, 3.0, -1.0, 0.1, 5.0, 0.3, -1.0]
T0 = 48.97104160717855
b, m = call(P, T0), call(P, T0, MUT)
print(f"RESULT baseline_plan={fmt(b)} kW")
print(f"RESULT mutant_plan={fmt(m)} kW")
print(f"RESULT delta_kw={float(np.max(np.abs(b - m))):.6f} kW")
rng = np.random.default_rng(0)
hits = 0
for _ in range(400):
    p = rng.choice([-1.0, 0.0, 0.1, 0.3, 3.0, 5.0], size=n)
    t = float(rng.uniform(30, 56))
    hits += int(float(np.max(np.abs(call(p, t) - call(p, t, MUT)))) > 1e-12)
print(f"RESULT random_plans_separating={hits} of 400")
Q = [0.0, 3.0, 3.0, 0.0, 0.1, 3.0, 0.3, 0.0]
print(f"RESULT null_delta_kw={float(np.max(np.abs(call(Q, T0) - call(Q, T0, MUT)))):.6f} kW")
print(f"RESULT realistic_delta_kw={realistic_delta(KEY, '_apply_dhw_min_run'):.6f} kW")
''')

# ---------------------------------------------------------------- _apply_dhw_pins
write("0b51e1d1975513aa", header(
    "0b51e1d1975513aa",
    "outcome of DhwPlanner._apply_dhw_pins on a pins array shorter than the plan: 1 = returns a plan, 0 = raises IndexError.",
    "custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._apply_dhw_pins line 1645 `for i in range(min(len(out), len(dhw_pins))):`",
    "Direction: returns_plan 1 -> 0 (IndexError) when len(dhw_pins) < len(plan).",
    "pins shorter than the plan (2 of 4), equal length, longer (6 of 4), empty pins; production reach: HeatPumpOptimizer._normalise_pins pads every pin array to the horizon (optimizer.py:5003-5018).",
    "equal-length and longer pins: both arms return the same plan."),
    "KEY = '0b51e1d1975513aa'\n" + '''
MUT = mutant_method("_apply_dhw_pins", mutant_dict(KEY))
plan = np.array([0.0, 0.0, 2.0, 2.0])


def ok(fn, pins):
    try:
        return 1, fn(plan, np.array(pins, float), 0.6)
    except IndexError:
        return 0, None


for label, pins in (("short", [1.0, 0.0]), ("empty", [])):
    rb, _ = ok(DhwPlanner._apply_dhw_pins, pins)
    rm, _ = ok(MUT.__func__ if isinstance(MUT, staticmethod) else MUT, pins)
    print(f"RESULT {label}_pins_returns_plan_baseline={rb}")
    print(f"RESULT {label}_pins_returns_plan_mutant={rm}")
same = 0
for pins in ([1.0, 0.0, float("nan"), 0.0], [1.0, 0.0, float("nan"), 0.0, 1.0, 1.0]):
    rb, pb = ok(DhwPlanner._apply_dhw_pins, pins)
    rm, pm = ok(MUT.__func__ if isinstance(MUT, staticmethod) else MUT, pins)
    same += int(rb == rm == 1 and np.array_equal(pb, pm))
print(f"RESULT null_equal_or_longer_identical={same} of 2")
''')

write("0e3fc2bc64c2bf63", header(
    "0e3fc2bc64c2bf63",
    "plan value (kW) _apply_dhw_pins returns at a step pinned exactly 0.5 (planned 0 kW, min_run_power 0.6).",
    "custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._apply_dhw_pins line 1649 `if pin >= 0.5:`",
    "Direction: 0.6 kW (force-on) -> 0.0 kW (force-off) at pin == 0.5.",
    "pins 0.5, 0.49999, 0.50001, 0, 1, NaN; production reach: manual_plan.channel_pins emits only PIN_ON 1.0, PIN_OFF 0.0 and NaN (manual_plan.py:41-42, 215-220); the three ordinary days with pins {0,1,NaN} (realistic_delta).",
    "pins 0, 1, NaN and 0.5 +- 1e-5: identical in both arms."),
    "KEY = '0e3fc2bc64c2bf63'\n" + '''
MUT = mutant_method("_apply_dhw_pins", mutant_dict(KEY))
MUTF = MUT.__func__ if isinstance(MUT, staticmethod) else MUT
plan = np.zeros(1)
print(f"RESULT baseline_kw_at_pin_0p5={DhwPlanner._apply_dhw_pins(plan, np.array([0.5]), 0.6)[0]:.6f} kW")
print(f"RESULT mutant_kw_at_pin_0p5={MUTF(plan, np.array([0.5]), 0.6)[0]:.6f} kW")
d = 0.0
for p in (0.0, 1.0, float("nan"), 0.49999, 0.50001):
    d = max(d, abs(DhwPlanner._apply_dhw_pins(plan, np.array([p]), 0.6)[0] - MUTF(plan, np.array([p]), 0.6)[0]))
print(f"RESULT null_delta_kw={d:.6f} kW")
pl, _ = planner(dhw_schedule_enabled=True, dhw_windows=W, dhw_min_temp=45.0)
pins = np.full(N, np.nan); pins[8:16] = 0.0; pins[40:44] = 1.0
h = horizon(prices=np.r_[np.full(24, 0.2), np.full(72, 1.0)], dhw_pins=pins)
b, _ = pl._build_dhw_requirements(h, p_max=4.0)
with mock.patch.object(DhwPlanner, "_apply_dhw_pins", MUT):
    m, _ = pl._build_dhw_requirements(h, p_max=4.0)
print(f"RESULT realistic_delta_kw={float(np.max(np.abs(b.schedule - m.schedule))):.6f} kW")
''')

# ---------------------------------------------------------------- _build_dhw_requirements
write("4813f0fd25bc8bb4", header(
    "4813f0fd25bc8bb4",
    "number of p_max / p_run_cap inputs (of 11) on which _build_dhw_requirements' schedule differs between baseline and mutant.",
    "custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._build_dhw_requirements line 1138 `p_dhw_run = max(0.1, min(p_max * 0.8, p_max))`",
    "Direction (if any): p_dhw_run changes only where p_max*0.8 > p_max, i.e. p_max < 0, where max(0.1, .) returns 0.1 in both arms.",
    "p_max 4, 0, -1, 1e-9, 0.125, +inf, -inf, NaN; p_max 4 with p_run_cap None, 0.05, 2.0.",
    "p_max 4.0 (ordinary): both arms equal by construction of min(0.8p, p) = 0.8p for p >= 0."),
    "KEY = '4813f0fd25bc8bb4'\n" + '''
pl, _ = planner(dhw_schedule_enabled=True, dhw_windows=W, dhw_min_temp=45.0)
pr = np.full(N, 1.0); pr[8:16] = 0.1
cases = [dict(p_max=v) for v in (4.0, 0.0, -1.0, 1e-9, 0.125, float("inf"), float("-inf"), float("nan"))]
cases += [dict(p_max=4.0, p_run_cap=c) for c in (None, 0.05, 2.0)]
diff = 0
for kw in cases:
    b, m = arms(pl, horizon(prices=pr), KEY, **kw)
    diff += int(not np.array_equal(b.schedule, m.schedule))
print(f"RESULT inputs_separating={diff} of {len(cases)}")
b, m = arms(pl, horizon(prices=pr), KEY, p_max=4.0)
print(f"RESULT null_delta_kw={float(np.max(np.abs(b.schedule - m.schedule))):.6f} kW")
''')

PINS_BODY = '''
pl, _ = planner(dhw_schedule_enabled=True, dhw_windows=W, dhw_min_temp=45.0)
pr = np.full(N, 1.0); pr[8:16] = 0.1
pins = np.full(N, np.nan); pins[8:16] = 0.0   # the user pins the cheap night steps OFF


def gap(p):
    """Worst shortfall (C) of the simulated tank below the plan's own floor/ready requirement."""
    t = pl.model.simulate_dhw_only(initial_temp=48.0, dhw_power_schedule=p.schedule, outdoor_temps=np.full(N, -5.0),
                                   draw_rates=p.draw_rates, dt_hours=0.25)
    return float(np.max(np.maximum(p.floor_temps, p.ready_temps) - t[1:]))


b, m = arms(pl, horizon(prices=pr, dhw_pins=pins), KEY, p_max=4.0)
print(f"RESULT baseline_shortfall_c={gap(b):.4f} C")
print(f"RESULT mutant_shortfall_c={gap(m):.4f} C")
print(f"RESULT baseline_kwh={b.schedule.sum() * 0.25:.4f} kWh")
print(f"RESULT mutant_kwh={m.schedule.sum() * 0.25:.4f} kWh")
b0, m0 = arms(pl, horizon(prices=pr), KEY, p_max=4.0)
print(f"RESULT null_delta_kw={float(np.max(np.abs(b0.schedule - m0.schedule))):.6f} kW")
pins_on = np.full(N, np.nan); pins_on[40:44] = 1.0
b1, m1 = arms(pl, horizon(prices=pr, dhw_pins=pins_on), KEY, p_max=4.0)
print(f"RESULT null_on_only_delta_kw={float(np.max(np.abs(b1.schedule - m1.schedule))):.6f} kW")
'''
write("b25e80c59b31c20d", header(
    "b25e80c59b31c20d",
    "worst simulated tank shortfall (C) below the plan's own floor/ready requirement, for a plan built with manual DHW pins forcing the cheap night steps 8-15 OFF.",
    "custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._build_dhw_requirements line 1184 `if dhw_pins is not None:` (the forced_off mask from pins)",
    "Direction: shortfall up (the planners buy energy in the pinned-off steps, the pin overlay deletes it, nothing re-buys it).",
    "pins OFF on steps 8-15 under a cheap night (prices 0.1 there, 1.0 elsewhere), window 18:00-20:00, min 45 C, tank 48 C; no pins; pins only ON (steps 40-43).",
    "no pins, and on-only pins: the forced_off mask is None in both arms, delta 0."),
    "KEY = 'b25e80c59b31c20d'\n" + PINS_BODY)
write("cd7bc939ea82fecd", header(
    "cd7bc939ea82fecd",
    "worst simulated tank shortfall (C) below the plan's own floor/ready requirement, for a plan built with manual DHW pins forcing the cheap night steps 8-15 OFF.",
    "custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._build_dhw_requirements line 1188 `if mask.any():` (forced_off = mask)",
    "Direction: shortfall up (pinned-off steps never reach forced_off; the overlay deletes energy nothing re-buys).",
    "pins OFF on steps 8-15 under a cheap night, window 18:00-20:00, min 45 C, tank 48 C; no pins; pins only ON (steps 40-43, mask all False).",
    "no pins, and on-only pins (mask.any() False in both arms): delta 0."),
    "KEY = 'cd7bc939ea82fecd'\n" + PINS_BODY)

write("6999e2dab9790b53", header(
    "6999e2dab9790b53",
    "max |schedule| difference (kW) of _build_dhw_requirements with one DHW pin exactly 0.5 at step 13 (others free).",
    "custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._build_dhw_requirements line 1187 `mask[...] = ~np.isnan(pins_arr) & (pins_arr < 0.5)`",
    "Direction: a 0.5 pin becomes forced-off for the planners (then force-on by the overlay), moving the plan's energy.",
    "pin 0.5 at step 13 under a cheap night; pins 0, 1, NaN, 0.49999, 0.50001 at the same step; production reach: manual_plan.channel_pins emits only 0.0, 1.0, NaN (manual_plan.py:41-42, 215-220).",
    "pin 1.0, 0.0, NaN and 0.5 +- 1e-5 at step 13: identical in both arms."),
    "KEY = '6999e2dab9790b53'\n" + '''
pl, _ = planner(dhw_schedule_enabled=True, dhw_windows=W, dhw_min_temp=45.0)
pr = np.full(N, 1.0); pr[8:16] = 0.1


def at(v):
    pins = np.full(N, np.nan); pins[13] = v
    return arms(pl, horizon(prices=pr, dhw_pins=pins), KEY, p_max=4.0)


b, m = at(0.5)
print(f"RESULT pin0p5_delta_kw={float(np.max(np.abs(b.schedule - m.schedule))):.6f} kW")
print(f"RESULT pin0p5_kwh_baseline={b.schedule.sum() * 0.25:.4f} kWh")
print(f"RESULT pin0p5_kwh_mutant={m.schedule.sum() * 0.25:.4f} kWh")
d = 0.0
for v in (1.0, 0.0, float("nan"), 0.49999, 0.50001):
    b, m = at(v)
    d = max(d, float(np.max(np.abs(b.schedule - m.schedule))))
print(f"RESULT null_delta_kw={d:.6f} kW")
''')

write("de02e0a048abc451", header(
    "de02e0a048abc451",
    "DhwPlan.external_heat_suppressed_steps (count) published by _build_dhw_requirements with blocked=True while external heat is active, and the schedule sum (kW).",
    "custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._build_dhw_requirements line 1190 `if blocked:` (forced_off = all steps)",
    "Direction: suppressed count 0 -> 1 (the mutant plans slots in a blocked mode, then suppresses one of them); the final schedule is zeroed by the restated invariant at line 1368 in both arms.",
    "blocked=True with external_heat_active True and False, tank 48 C, cheap steps 1-7; blocked=False.",
    "external heat inactive (the suppression branch does not run): both arms 0; blocked=False: identical."),
    "KEY = 'de02e0a048abc451'\n" + '''
pl, _ = planner(dhw_schedule_enabled=True, dhw_windows=W, dhw_min_temp=45.0)
pr = np.full(N, 1.0); pr[1:8] = 0.05
b, m = arms(pl, horizon(prices=pr, state=state(48.0, external_heat_active=True)), KEY, p_max=4.0, blocked=True)
print(f"RESULT suppressed_steps_baseline={b.external_heat_suppressed_steps}")
print(f"RESULT suppressed_steps_mutant={m.external_heat_suppressed_steps}")
print(f"RESULT schedule_sum_baseline={b.schedule.sum():.6f} kW")
print(f"RESULT schedule_sum_mutant={m.schedule.sum():.6f} kW")
b, m = arms(pl, horizon(prices=pr, state=state(48.0, external_heat_active=False)), KEY, p_max=4.0, blocked=True)
print(f"RESULT null_ext_off_suppressed={b.external_heat_suppressed_steps},{m.external_heat_suppressed_steps}")
b, m = arms(pl, horizon(prices=pr, state=state(48.0, external_heat_active=True)), KEY, p_max=4.0, blocked=False)
print(f"RESULT null_unblocked_delta_kw={float(np.max(np.abs(b.schedule - m.schedule))):.6f} kW")
''')

write("7f026b4dd7d44269", header(
    "7f026b4dd7d44269",
    "max |schedule| difference (kW) and kWh of _build_dhw_requirements on a cheap-night day, per tank cooling rate (the hold hours that set max_lead_steps).",
    "custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._build_dhw_requirements line 1214 `max_lead_steps = max(1, min(n_steps, int(np.ceil(max_lead_hours / dt))))`",
    "Direction: the lead window widens to the whole horizon, so a leaky tank pre-heats further ahead than its hold time (kWh up).",
    "dhw_cooling_rate 0.3 (default-like, hold 28 h > horizon), 2.0 (hold 4.2 h), 5.0 (hold 2.8 h); prices 0.01 on steps 0-7, 1.0 elsewhere; window 18:00-20:00, min 45 C.",
    "cooling rate 0.3: hold 28 h, min(n_steps, ceil) == n_steps in both arms, delta 0."),
    "KEY = '7f026b4dd7d44269'\n" + '''
pr = np.full(N, 1.0); pr[0:8] = 0.01
for cr in (0.3, 2.0, 5.0):
    pl, _ = planner(dhw_schedule_enabled=True, dhw_windows=W, dhw_min_temp=45.0, dhw_cooling_rate=cr)
    b, m = arms(pl, horizon(prices=pr), KEY, p_max=4.0)
    tag = f"cr{cr:g}".replace(".", "p")
    print(f"RESULT {tag}_hold_hours={b.max_lead_hours:.4f} h")
    print(f"RESULT {tag}_kwh_baseline={b.schedule.sum() * 0.25:.4f} kWh")
    print(f"RESULT {tag}_kwh_mutant={m.schedule.sum() * 0.25:.4f} kWh")
    print(f"RESULT {tag}_delta_kw={float(np.max(np.abs(b.schedule - m.schedule))):.6f} kW")
''')

write("a1576c7241b67401", header(
    "a1576c7241b67401",
    "DhwPlan.external_heat_suppressed_steps and schedule[0] (kW) of _build_dhw_requirements with external heat active, at the initial tank temperature where the coasting temperature after step 0 equals requirement[0] - 0.5 exactly.",
    "custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._build_dhw_requirements line 1342 `covered = free_temps[1:] >= requirement - 0.5`",
    "Direction: at the tie the step is no longer 'covered': suppressed 1 -> 0, schedule[0] 0.0 -> 3.2 kW.",
    "tank 44.646992926832446 C (found by bisection on the production simulation, free_temps[1] - (requirement[0] - 0.5) == 0.0), its float predecessor and +0.01 C; dhw schedule off, price 0.01 at step 0, 1.0 elsewhere.",
    "the float predecessor (free < req - 0.5) and +0.01 C (free > req - 0.5): both arms equal."),
    "KEY = 'a1576c7241b67401'\n" + '''
pl, _ = planner(dhw_schedule_enabled=False)
pr = np.full(N, 1.0); pr[0] = 0.01
T_TIE = 44.646992926832446
b, m = arms(pl, horizon(prices=pr, state=state(T_TIE, hsl=1.0, external_heat_active=True)), KEY, p_max=4.0)
print(f"RESULT suppressed_baseline={b.external_heat_suppressed_steps}")
print(f"RESULT suppressed_mutant={m.external_heat_suppressed_steps}")
print(f"RESULT step0_kw_baseline={b.schedule[0]:.6f} kW")
print(f"RESULT step0_kw_mutant={m.schedule[0]:.6f} kW")
d = 0.0
for T in (float(np.nextafter(T_TIE, -np.inf)), T_TIE + 0.01):
    b, m = arms(pl, horizon(prices=pr, state=state(T, hsl=1.0, external_heat_active=True)), KEY, p_max=4.0)
    d = max(d, float(np.max(np.abs(b.schedule - m.schedule))))
print(f"RESULT null_delta_kw={d:.6f} kW")
''')

write("8fa714bbb756e11e", header(
    "8fa714bbb756e11e",
    "DhwPlan.external_heat_suppressed_steps and the kWh planned in steps 0-7 by _build_dhw_requirements with external heat active and the tank coasting above its requirement.",
    "custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._build_dhw_requirements line 1343 `horizon = min(n_steps, max(1, int(round(2.0 / max(dt, 1e-6)))))`",
    "Direction: the suppression horizon shrinks from 2 h (8 steps) to 1 step: suppressed 1 -> 0 and electric DHW bought under a running external source (kWh in steps 0-7 up).",
    "tank 48 and 55 C, external heat on/off, prices 0.05 on steps 1-7, 1.0 elsewhere; window 18:00-20:00, min 45 C.",
    "external heat off (branch not run), and tank 55 C (nothing planned early): both arms equal."),
    "KEY = '8fa714bbb756e11e'\n" + '''
pl, _ = planner(dhw_schedule_enabled=True, dhw_windows=W, dhw_min_temp=45.0)
pr = np.full(N, 1.0); pr[1:8] = 0.05
b, m = arms(pl, horizon(prices=pr, state=state(48.0, external_heat_active=True)), KEY, p_max=4.0)
print(f"RESULT suppressed_baseline={b.external_heat_suppressed_steps}")
print(f"RESULT suppressed_mutant={m.external_heat_suppressed_steps}")
print(f"RESULT kwh_steps0_7_baseline={b.schedule[:8].sum() * 0.25:.4f} kWh")
print(f"RESULT kwh_steps0_7_mutant={m.schedule[:8].sum() * 0.25:.4f} kWh")
d = 0.0
for T, ext in ((48.0, False), (55.0, True), (55.0, False)):
    b, m = arms(pl, horizon(prices=pr, state=state(T, external_heat_active=ext)), KEY, p_max=4.0)
    d = max(d, float(np.max(np.abs(b.schedule - m.schedule))))
print(f"RESULT null_delta_kw={d:.6f} kW")
''')

write("8fbdb8a5c1e67d5e", header(
    "8fbdb8a5c1e67d5e",
    "number of (dt, tank, n) inputs on which _build_dhw_requirements' schedule, suppressed count or raised exception differs between baseline and mutant, external heat active.",
    "custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._build_dhw_requirements line 1343 `... 2.0 / max(dt, 1e-6) ...`",
    "Direction (if any): only dt <= 0 can differ; dt == 0 raises ZeroDivisionError earlier at line 1214 in both arms; dt < 0 gives horizon n (baseline) vs 1 (mutant).",
    "dt 0.25, 1.0, 1e-7, 1e-9, 0, -0.25, -1.0, -1e-9, NaN, +inf; tanks 30/44/46/50/60 C; n 8 and 24; an all-day window (min 45 C) so the planner buys; linear prices 0.1..1.0.",
    "dt 0.25: max(dt, 1e-6) == dt, both arms identical."),
    "KEY = '8fbdb8a5c1e67d5e'\n" + '''
pl, _ = planner(dhw_schedule_enabled=True, dhw_windows=parse_windows("00:00-23:59"), dhw_min_temp=45.0)


def outcome(h, mut):
    try:
        if mut:
            with mutated("_build_dhw_requirements", KEY):
                p, _ = pl._build_dhw_requirements(h, p_max=4.0)
        else:
            p, _ = pl._build_dhw_requirements(h, p_max=4.0)
        return (tuple(np.round(p.schedule, 9)), p.external_heat_suppressed_steps)
    except Exception as e:  # noqa: BLE001 - the raised type is the outcome
        return type(e).__name__


tried = sep = 0
for dt in (0.25, 1.0, 1e-7, 1e-9, 0.0, -0.25, -1.0, -1e-9, float("nan"), float("inf")):
    for T in (30.0, 44.0, 46.0, 50.0, 60.0):
        for n in (8, 24):
            h = horizon(prices=np.linspace(0.1, 1.0, n), n=n, dt=dt, step_hours=np.full(n, 19.0),
                        state=state(T, hsl=1.0, external_heat_active=True))
            tried += 1
            sep += int(outcome(h, False) != outcome(h, True))
print(f"RESULT inputs_separating={sep} of {tried}")
''')

write("94c2cc27ea61db25", header(
    "94c2cc27ea61db25",
    "number of horizons (legionella due, external heat active) on which _build_dhw_requirements' schedule or suppressed count differs between baseline and mutant.",
    "custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._build_dhw_requirements line 1346 `if legionella_step is not None:` (protects the disinfection step from external-heat suppression)",
    "Direction (if any): energy at the legionella step zeroed by the suppression mask.",
    "legionella enabled 60 C / 7 d; hours since 160-169 (legionella steps 0,1,3,5,7 seen); tank 58-62 C in 0.1 C; a single cheap step at 1,3,5,7 or none; windows 18:00-20:00, 01:00-03:00, 04:00-06:00, 10:00-12:00 with min 45/55 C and draw 150/400 L/day; step 0 at 0.01 against 3.0. 2 x 240 + 60 + 21 horizons.",
    "external heat inactive: the branch does not run, delta 0."),
    "KEY = '94c2cc27ea61db25'\n" + '''
LEG = dict(dhw_legionella_enabled=True, dhw_legionella_temp=60.0, dhw_legionella_interval_days=7.0)
tried = sep = 0
legs = set()


def one(pl, h):
    global tried, sep
    b, m = arms(pl, h, KEY, p_max=4.0)
    legs.add(b.legionella_step)
    tried += 1
    sep += int(not np.array_equal(b.schedule, m.schedule)
               or b.external_heat_suppressed_steps != m.external_heat_suppressed_steps)


pl, _ = planner(dhw_schedule_enabled=True, dhw_windows=W, dhw_min_temp=45.0, **LEG)
for T in np.arange(59.0, 61.01, 0.1):
    one(pl, horizon(prices=np.full(N, 1.0), state=state(float(T), hsl=169.0, external_heat_active=True)))
for hsl in (160.0, 163.0, 165.0, 166.0, 167.0, 168.0):
    for cheap in (None, 1, 3, 5, 7):
        for T in (59.0, 59.5, 59.8, 60.0, 60.3, 60.6, 61.0, 62.0):
            pr = np.full(N, 1.0)
            if cheap is not None:
                pr[cheap] = 0.01
            one(pl, horizon(prices=pr, state=state(T, hsl=hsl, external_heat_active=True)))
for win in ("01:00-03:00", "04:00-06:00", "10:00-12:00"):
    for mint in (45.0, 55.0):
        for cons in (150.0, 400.0):
            plw, _ = planner(dhw_schedule_enabled=True, dhw_windows=parse_windows(win), dhw_min_temp=mint,
                             dhw_daily_consumption=cons, **LEG)
            for T in (59.6, 59.8, 60.0, 60.5, 61.0):
                pr = np.full(N, 3.0); pr[0] = 0.01
                one(plw, horizon(prices=pr, state=state(T, hsl=169.0, external_heat_active=True)))
print(f"RESULT inputs_separating={sep} of {tried}")
print(f"RESULT legionella_steps_seen={sorted(s for s in legs if s is not None)}")
''')

write("defeacb89de279a1", header(
    "defeacb89de279a1",
    "number of horizons on which DhwPlan.external_heat_suppressed_steps differs between baseline and mutant, and the count of planned slots in (0, 1e-5] kW (the only values `>=` and `>` 1e-6 can split) the pipeline ever leaves before the suppression line.",
    "custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._build_dhw_requirements line 1348 `suppress_steps = int(np.sum(mask & (schedule > 1e-6)))`",
    "Direction (if any): suppressed count +1 at a slot of exactly 1e-6 kW.",
    "external heat on; tanks 40-56 C in 2 C steps; cheap blocks at steps 0-7, 1-7, 2-5 and flat; window 18:00-20:00 and 06:00-08:00; min 45 C; p_max 4.0 and 0.3 (a 0.24 kW block); also the slot values seen by a spy on _repair_dhw_floor's output.",
    "external heat off: the branch does not run, both 0."),
    "KEY = 'defeacb89de279a1'\n" + '''
tried = sep = tiny = 0
for win in ("18:00-20:00", "06:00-08:00"):
    pl, _ = planner(dhw_schedule_enabled=True, dhw_windows=parse_windows(win), dhw_min_temp=45.0)
    for T in np.arange(40.0, 56.01, 2.0):
        for blk in ((0, 8), (1, 8), (2, 6), None):
            for pmax in (4.0, 0.3):
                pr = np.full(N, 1.0)
                if blk:
                    pr[blk[0]:blk[1]] = 0.05
                h = horizon(prices=pr, state=state(float(T), external_heat_active=True))
                b, m = arms(pl, h, KEY, p_max=pmax)
                tried += 1
                sep += int(b.external_heat_suppressed_steps != m.external_heat_suppressed_steps)
                tiny += int(np.sum((b.schedule > 0.0) & (b.schedule <= 1e-5)))
print(f"RESULT inputs_separating={sep} of {tried}")
print(f"RESULT slots_in_0_1e-5_kw={tiny}")
''')

write("c9404a6ea551b041", header(
    "c9404a6ea551b041",
    "number of empty-plan inputs on which DhwPlanner._clamp_dhw_to_capacity's return (or raised type) differs between baseline and mutant.",
    "custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._clamp_dhw_to_capacity line 1943 `if plan.size == 0:`",
    "Direction (if any): the mutant runs the setup (np.asarray(max_temp), float(initial_temp)) and the empty loop, then returns the same empty plan.",
    "empty plan with max_temp scalar 60, empty array, NaN, inf, None; initial_temp 50, NaN, inf, -inf; plus out-of-type initial_temp None (TypeError in the mutant only, recorded separately); a horizon of n=0 through _build_dhw_requirements.",
    "a non-empty plan ([1.0, 2.0]): the guard is not taken, both arms identical."),
    "KEY = 'c9404a6ea551b041'\n" + '''
pl, _ = planner()
MUT = mutant_method("_clamp_dhw_to_capacity", mutant_dict(KEY))


def out(fn, plan, T, mt):
    try:
        r = fn(pl, np.array(plan, float), T, np.full(len(plan), -5.0), np.zeros(len(plan)), 0.25, mt)
        return ("ok", tuple(r.tolist()), r.dtype.str)
    except Exception as e:  # noqa: BLE001
        return type(e).__name__


tried = sep = 0
for mt in (60.0, np.zeros(0), float("nan"), float("inf"), None):
    for T in (50.0, float("nan"), float("inf"), float("-inf")):
        tried += 1
        sep += int(out(DhwPlanner._clamp_dhw_to_capacity, [], T, mt) != out(MUT, [], T, mt))
print(f"RESULT typed_inputs_separating={sep} of {tried}")
print(f"RESULT out_of_type_initial_none_baseline={out(DhwPlanner._clamp_dhw_to_capacity, [], None, 60.0)[0]}")
print(f"RESULT out_of_type_initial_none_mutant={out(MUT, [], None, 60.0)}")
print(f"RESULT null_nonempty_equal={int(out(DhwPlanner._clamp_dhw_to_capacity, [1.0, 2.0], 50.0, np.full(2, 60.0)) == out(MUT, [1.0, 2.0], 50.0, np.full(2, 60.0)))}")
pl2, _ = planner(dhw_schedule_enabled=True, dhw_windows=W, dhw_min_temp=45.0)
h0 = horizon(prices=np.zeros(0), n=0)
def n0(mut):
    try:
        if mut:
            with mutated("_clamp_dhw_to_capacity", KEY):
                p, _ = pl2._build_dhw_requirements(h0, p_max=4.0)
        else:
            p, _ = pl2._build_dhw_requirements(h0, p_max=4.0)
        return ("ok", p.schedule.size)
    except Exception as e:  # noqa: BLE001
        return type(e).__name__
print(f"RESULT n0_build_baseline={n0(False)}")
print(f"RESULT n0_build_mutant={n0(True)}")
''')
print("written", len(list(HERE.glob("probe_*.py"))))
