import os, sys, hashlib, subprocess
from datetime import datetime
CWD = os.getcwd()
sys.path.insert(0, os.path.join(CWD, "custom_components"))
sys.path.insert(0, os.path.join(CWD, "tests"))
import numpy as np
from harness import UTC
from profiles import solve_inputs
import heatpump_optimizer.optimizer as om
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState

HAS = hasattr(OptimizationConfig(), "duty_switch_stop_probability")
if HAS:
    from heatpump_optimizer import duty_legs

STEPS = np.arange(96)
PRICES = 1.3 + 0.9 * np.sin(2 * np.pi * (STEPS - 30) / 96.0)
PROFILES = {"varied": PRICES, "flat": np.full(96, float(np.mean(PRICES)))}
INSTALLS = {
    "duty-cycle": dict(clamp=False),
    "modulating clamped": dict(clamp=True),
    "fixed-speed": dict(clamp=True, p_min=5.5),
}
PAIR, OFF = (1.0, 0.0), (501.0, 0.0)


def H(x):
    return hashlib.sha256(np.asarray(x, dtype=float).round(9).tobytes()).hexdigest()[:16]


def P(*a):
    print("RESULT", *a, flush=True)


def solve(kw, prices, pair=None, off=None, cyc=0.3):
    clamp = kw.get("clamp", False)
    p_min = kw.get("p_min", 1.5)
    p_max = kw.get("p_max", 5.5)
    params = ThermalParameters()
    params.mixing_valve_mode = "none"
    params.buffer_tank_volume = 750.0
    params.min_electrical_power, params.max_electrical_power = p_min, p_max
    params.dhw_enabled = True
    cfg = OptimizationConfig(clamp_planned_levels=clamp, cycling_cost=cyc)
    if pair is not None:
        cfg.duty_switch_stop_probability, cfg.duty_switch_off_seconds = pair, off
    opt = HeatPumpOptimizer(ThermalModel(params), cfg)
    outdoor = 2.0 + 3.0 * np.sin(2 * np.pi * (STEPS - 50) / 96.0)
    return opt.optimize(inputs=solve_inputs(
        initial_state=ThermalState(
            room_temperature=20.5, upper_floor_temperature=20.5,
            lower_floor_temperature=20.5, slab_temperature=21.0,
            outdoor_temperature=float(outdoor[0]),
            buffer_tank_temperature=30.0, dhw_temperature=45.0,
            dhw_hours_since_legionella=20.0,
        ),
        prices=prices, outdoor_temps=outdoor,
        start_time=datetime(2026, 1, 10, tzinfo=UTC), dhw_pins=None,
    ))


def floor_of(kw):
    return kw.get("p_min", 1.5) if kw.get("clamp") else None


def line(prefix, fn):
    try:
        fn()
    except Exception as e:
        P(prefix, "ERROR", repr(e))


# Part A
base = {}
for name, kw in INSTALLS.items():
    for prof, pr in PROFILES.items():
        def f():
            r = solve(kw, pr)
            base[(name, prof)] = r
            P("nopair", name, prof, f"space={H(r.power_schedule)}", f"dhw={H(r.dhw_power_schedule)}",
              f"obj={float(r.objective_value)!r}", f"status={getattr(r, 'status', '?')}")
        line(f"nopair {name} {prof}", f)

for tag, vec in (("constant_draw_cycling", [0, 3.0, 3.0, 0]), ("lone_run_cycling", [0, 3.0, 0, 0])):
    def f():
        P(f"{tag}={om.cycling_penalty(np.array(vec, float), 0.3, 5.5)!r}")
    line(tag, f)

if HAS:
    dl = duty_legs
    sw = dl.switch_weight
    A = np.array
    for tag, s, d in (("dhw_then_space", [0, 0, 3, 0], [0, 3, 0, 0]),
                      ("idle_between", [0, 0, 0, 3], [0, 3, 0, 0]),
                      ("reverse_zero_pair", [0, 3, 0, 0], [0, 0, 3, 0]),
                      ("two_leg_step", [0, 2, 0, 0], [0, 2, 0, 0])):
        def f():
            P(f"switch_weight_{tag}={sw(A(s, float), A(d, float), (1.0, 0.0), 5.5, None)!r}")
        line(f"switch_weight_{tag}", f)

    def w(r, fl):
        return sw(np.asarray(r.power_schedule, float), np.asarray(r.dhw_power_schedule, float), PAIR, 5.5, fl)

    def moved(a, b):
        return not (np.array_equal(a.power_schedule, b.power_schedule)
                    and np.array_equal(a.dhw_power_schedule, b.dhw_power_schedule))

    for name, kw in INSTALLS.items():
        for prof, pr in PROFILES.items():
            def f():
                r = solve(kw, pr, PAIR, OFF)
                b = base[(name, prof)]
                fl = floor_of(kw)
                P("priced", name, prof, f"space={H(r.power_schedule)}", f"dhw={H(r.dhw_power_schedule)}",
                  f"obj={float(r.objective_value)!r}", f"w_nopair={w(b, fl)!r}", f"w_priced={w(r, fl)!r}",
                  f"moved={moved(r, b)}")
            line(f"priced {name} {prof}", f)

    for name, kw in INSTALLS.items():
        def f():
            r = solve(kw, PRICES, (0.0, 0.0), (0.0, 0.0))
            b = base[(name, "varied")]
            same = (not moved(r, b)) and r.objective_value == b.objective_value
            P("zeropair", name, "varied", f"same_as_nopair={same}")
        line(f"zeropair {name} varied", f)

    for name, kw in INSTALLS.items():
        for tag, off, cyc in (("priced_cyc0", OFF, 0.0), ("priced_nooff", (0.0, 0.0), 0.3)):
            def f():
                r = solve(kw, PRICES, PAIR, off, cyc=cyc)
                # reference no-pair plan at the same cyc
                b = base[(name, "varied")] if cyc == 0.3 else solve(kw, PRICES, None, None, cyc=cyc)
                P(tag, name, "varied", f"moved={moved(r, b)}", f"w_priced={w(r, floor_of(kw))!r}")
            line(f"{tag} {name} varied", f)

    def old_share(space, dhw, minute):
        dhw_min = 15.0 * dhw / (space + dhw)
        if dhw_min < 5.0:
            return "space"
        if 15.0 - dhw_min < 5.0:
            return "dhw"
        return "dhw" if minute < dhw_min else "space"

    def f():
        g = np.linspace(0.2, 5.5, 54)
        bad = tot = 0
        for s in g:
            for d in g:
                legs = dl.both_step_legs(float(s), float(d), 15.0)
                for m in (0.0, 2.5, 4.999, 5.0, 7.5, 10.0, 10.001, 14.9):
                    new = legs[0][0] if m < legs[0][1] else legs[-1][0]
                    tot += 1
                    bad += new != old_share(float(s), float(d), m)
        P(f"leg_rule_mismatches={bad} of {tot}")
        bad = tot = 0
        for s in g:
            for d in g:
                two = dl.leg_ends(np.array([s]), np.array([d]), None)[2]
                tot += 1
                bad += bool(np.asarray(two).reshape(-1)[0]) != (len(dl.both_step_legs(float(s), float(d), 15.0)) == 2)
        P(f"leg_ends_two_mismatches={bad} of {tot}")
    line("leg_rule", f)

    def f():
        rng = np.random.default_rng(7)
        space = rng.uniform(0, 5.5, (200, 96)) * (rng.random((200, 96)) >= 0.3)
        dhw = rng.uniform(0, 3, 96) * (rng.random(96) >= 0.6)
        for tag, fl in (("scalar_batch_mismatches", None), ("scalar_batch_mismatches_floor", 1.5)):
            batch = dl.switch_weights_batch(space, dhw, (0.7, 0.4), 5.5, fl)
            bad = sum(float(batch[i]) != sw(space[i], dhw, (0.7, 0.4), 5.5, fl) for i in range(200))
            P(f"{tag}={bad} of 200")
    line("scalar_batch", f)
else:
    for n in ("switch_weight", "priced", "zeropair", "priced_cyc0", "priced_nooff", "leg_rule", "scalar_batch"):
        P(f"{n}=SKIPPED-no-feature")

tree = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
P(f"probe_done tree={tree}")
