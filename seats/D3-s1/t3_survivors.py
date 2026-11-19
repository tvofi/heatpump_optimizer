#!/usr/bin/env python3
"""D3-s1 M3/M4: what each full-gate survivor changes, measured on its production symbol.

Every mutant here SURVIVED the full GATE_SCOPE=full GOLDEN_MODE=drift gate
(state/gates/<key>.json). For each, this harness loads the mutated file's
BASELINE source (`git show <baseline>:<file>`, so a mutant commit in the
working tree cannot leak in), applies the one-line mutant in memory under a
private module name inside the package, drives the named production symbol on
a fixed boundary input, and prints the value in both arms.

Metric (one line): per key, `value` = the production symbol's delivered output
on the probe input (stated per probe); `moved` = 1 when the mutant arm differs
from the baseline arm. Count key: the value the production symbol delivers.

Perturbation: the survivor's own one-line mutant (results/complete/<key>.json
`old` -> `new`); direction stated per probe in `expect`. Null control: the same
probe on a non-boundary input (`null_value`), equal in both arms.

Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/t3_survivors.py [<key> ...]
Expected: moved=1 for every key but the equivalent mutant a4b00ac3ca662eec
(moved=0 over its whole grid). Exact values (contention-immune).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import importlib.util
import json
import math
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
PKG = "heatpump_optimizer"  # the package name the suite itself imports (tests/hastub)
_cache: dict = {}


def mutant_of(key: str) -> dict:
    return json.loads((HERE / "state/results/complete" / f"{key}.json").read_text())["mutant"]


def load(rel: str, mut: dict | None):
    tag = (rel, None if mut is None else (mut["line"], mut["new"]))
    if tag in _cache:
        return _cache[tag]
    import harness  # noqa: F401  (tests/harness.py puts custom_components on sys.path, as features.py relies on)
    import heatpump_optimizer  # noqa: F401

    text = subprocess.run(["git", "-C", str(ROOT), "show", f"{BASE}:{rel}"],
                          check=True, capture_output=True, text=True).stdout
    if mut is not None:
        lines = text.split("\n")
        i = int(mut["line"]) - 1
        assert lines[i] == mut["old"], f"{rel}:{mut['line']} is {lines[i]!r}, not {mut['old']!r}"
        lines[i] = mut["new"]
        text = "\n".join(lines)
    name = f"{PKG}._d3s1_{Path(rel).stem}_{len(_cache)}"
    spec = importlib.util.spec_from_loader(name, loader=None, origin=rel)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = PKG
    mod.__file__ = str(ROOT / rel)
    sys.modules[name] = mod
    exec(compile(text, str(ROOT / rel), "exec"), mod.__dict__)
    _cache[tag] = mod
    return mod


def _err(fn):
    try:
        return repr(fn())
    except Exception as e:  # the exception IS the delivered output for a guard
        return f"{type(e).__name__}: {e}"


# ---- probes: (module file, probe(mod) -> value, null(mod) -> value, expect) ----

def p_parse_rule(m):
    return _err(lambda: m._parse_rule("Nov-Mar"))


def n_parse_rule(m):
    return _err(lambda: m._parse_rule("Nov-Mar = 0.5"))


def p_holiday_windows(m):
    from heatpump_optimizer import const
    return _err(lambda: m._holiday_dhw_windows({const.CONF_HOLIDAY_DHW_WINDOWS: ""}))


def n_holiday_windows(m):
    from heatpump_optimizer import const
    return _err(lambda: m._holiday_dhw_windows({const.CONF_HOLIDAY_DHW_WINDOWS: "06:00-07:00"}))


def _bias(m, pairs):
    b = m.FlowCurveBias()
    for meas, curve in pairs:
        b.observe(meas, curve)
    return (b.bias_k, b.samples)


def p_flow_nonfinite(m):
    return repr(_bias(m, [(40.0, float("inf")), (float("nan"), 30.0)]))


def n_flow_nonfinite(m):
    return repr(_bias(m, [(40.0, 35.0)]))


def p_flow_settled(m):  # five seeding folds of +10 K, then one 0 K residual
    return repr(_bias(m, [(50.0, 40.0)] * 5 + [(40.0, 40.0)]))


def n_flow_settled(m):  # still in the plain-mean phase: alpha and the boundary are not consulted
    return repr(_bias(m, [(50.0, 40.0)] * 3 + [(40.0, 40.0)]))


def p_tau_fast(m):
    return _err(lambda: m.slab_mode_tau_fast(1.0, 1.0, -1.0))


def n_tau_fast(m):
    return _err(lambda: m.slab_mode_tau_fast(1.0, 1.0, 1.0))


def p_holiday_flags(m):
    return _err(lambda: m._holiday_flags_for([datetime(2026, 11, 19, 0, 0)], frozenset()))


def n_holiday_flags(m):
    from datetime import date
    return _err(lambda: m._holiday_flags_for([datetime(2026, 11, 19, 0, 0)], frozenset({date(2026, 11, 19)})))


def _seeded_shape_model(m):
    pm = m.PriceShapeModel()
    pm.days = [m.SHAPE_CONFIDENCE_DAYS, m.SHAPE_CONFIDENCE_DAYS]
    return pm


def p_daily_min(m):
    return _err(lambda: _seeded_shape_model(m).expected_daily_min([0], 0.0))


def n_daily_min(m):
    return _err(lambda: _seeded_shape_model(m).expected_daily_min([0], 1.0))


def _quarter_day(m, level):
    pm = m.PriceShapeModel()
    vals = [level] * m.QUARTERS_PER_DAY
    ok = pm.observe_day_quarters(datetime(2026, 11, 18), vals)
    return (ok, pm.quarter_days[0] + pm.quarter_days[1], float(np.mean(np.asarray(vals))) == level)


def p_quarter_floor(m):
    return repr(_quarter_day(m, 1e-6))


def n_quarter_floor(m):
    return repr(_quarter_day(m, 1.0))


def _sched(m, fixed, rate):
    return m.GridFeeSchedule(mode=m.MODE_RULES, fixed=fixed, rules=[m.FeeRule(rate=rate)])


def p_max_abs_tie(m):
    return repr(m.max_abs_component(_sched(m, 0.5, 0.5)))


def n_max_abs_tie(m):
    return repr(m.max_abs_component(_sched(m, 0.5, 0.7)))


def p_min_tie(m):
    return repr(m.min_component(_sched(m, -0.2, -0.2)))


def n_min_tie(m):
    return repr(m.min_component(_sched(m, -0.2, -0.3)))


def _valve_grid(m):
    """max |q_rad|+|q_floor| over a grid of buffer temperatures just above the coldest zone."""
    p = m.ThermalParameters()
    for name, val in (("buffer_tank_volume", 100.0),):
        if hasattr(p, name):
            setattr(p, name, val)
    out = []
    for t_buf in (20.2, 20.5, 21.0, 22.0, 25.0, 30.0, 40.0):
        s = m.ThermalState()
        s.upper_floor_temperature = 20.0
        s.slab_temperature = 20.0
        s.buffer_tank_temperature = t_buf
        r = m._valve_two_zone_delivery(p, s, 0.0, 0.0, 0.0, None, 0.0, 0.2, 0.25, False)
        out.append((t_buf, round(r[0], 9), round(r[1], 9)))
    return out


def p_valve(m):
    return repr(_valve_grid(m))


def n_valve(m):  # the unthrottled side: a tank far above the zones with the HP covering the draw
    p = m.ThermalParameters()
    s = m.ThermalState()
    s.upper_floor_temperature = 20.0
    s.slab_temperature = 20.0
    s.buffer_tank_temperature = 45.0
    r = m._valve_two_zone_delivery(p, s, 50.0, 0.0, 0.0, None, 0.0, 0.2, 0.25, False)
    return repr((round(r[0], 9), round(r[1], 9)))


def p_inlet(m):
    p = m.ThermalParameters()
    vals = []
    for amp in (0.0, -0.0, 1e-300, -1.0):
        p.dhw_inlet_seasonal_amplitude = amp
        for d in range(1, 367, 5):
            vals.append(p.seasonal_inlet_temp(d))
    return repr(round(float(np.sum(vals)), 12))


def n_inlet(m):
    p = m.ThermalParameters()
    p.dhw_inlet_seasonal_amplitude = 3.0
    return repr(p.seasonal_inlet_temp(100))


def p_topk(m):
    x = np.array([1.0, 3.0, 3.0, 3.0, 3.0, 2.0, 0.5, 1.5])
    return repr(float(m._smooth_topk_sum(x, 0, m._PEAK_SMOOTH_TAU)))


def n_topk(m):
    x = np.array([1.0, 3.0, 3.0, 3.0, 3.0, 2.0, 0.5, 1.5])
    return repr(float(m._smooth_topk_sum(x, 1, m._PEAK_SMOOTH_TAU)))


def _guard_after_two_events(m, retained_peaks):
    """Tariff DISABLED, a 32 A fuse (7.36 kW), a steady 6.5 kW house, and the
    month's capacity peaks the tracker still holds; two spaced meter events."""
    from datetime import timedelta
    from types import SimpleNamespace

    from harness import FakeEntry, FakeHass, FakeState

    states = {
        "sensor.indoor": FakeState("21.0", unit="\u00b0C"),
        "sensor.outdoor": FakeState("-5.0", unit="\u00b0C"),
        "sensor.house_power": FakeState("6500", unit="W"),
    }
    cfg = {
        "tibber_token": "x", "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
        "peak_guard_enabled": True, "house_power_entity": "sensor.house_power",
        "main_fuse_amperes": 32.0, "main_fuse_phases": 1,
    }
    c = m.HeatPumpOptimizerCoordinator(FakeHass(states), FakeEntry(data=cfg))
    c._peak_tracker.peaks = list(retained_peaks)
    ev = SimpleNamespace(data={"new_state": FakeState("6500", unit="W")})
    c._on_power_event(ev)
    c._peak_guard._last_event -= timedelta(hours=1)
    c._guard_last_fold -= timedelta(hours=1)
    c._on_power_event(ev)
    return (bool(c._peak_guard.suppressing), bool(c._capacity_tariff().enabled))


def p_power_event(m):
    return _err(lambda: _guard_after_two_events(m, [2.0]))


def n_power_event(m):
    return _err(lambda: _guard_after_two_events(m, []))


PROBES = {
    "121362d48b408236": ("grid_fee._parse_rule('Nov-Mar') error text", p_parse_rule, n_parse_rule, "message changes"),
    "050fdc4a20eba212": ("thermal_model._holiday_dhw_windows(spec='')", p_holiday_windows, n_holiday_windows, "None -> []"),
    "3885e472b8297a90": ("flow_lift.FlowCurveBias.observe non-finite pairs -> (bias_k, samples)", p_flow_nonfinite, n_flow_nonfinite, "(0.0, 0) -> folded"),
    "460217277822d5bd": ("sysid.slab_mode_tau_fast(1, 1, -1)", p_tau_fast, n_tau_fast, "0.0 -> -0.5"),
    "65f121eb047174ad": ("optimizer._holiday_flags_for(steps, frozenset())", p_holiday_flags, n_holiday_flags, "None -> array"),
    "0c3e91a6a349409a": ("flow_lift.FlowCurveBias bias_k after 5x(+10 K) then 0 K", p_flow_settled, n_flow_settled, "9.0 -> 8.0"),
    "2719aef4cbb8b464": ("price_model.PriceShapeModel.expected_daily_min([0], level=0.0)", p_daily_min, n_daily_min, "None -> 0.0"),
    "95779f9d6d71c50d": ("grid_fee.max_abs_component tie fixed=rule=0.5", p_max_abs_tie, n_max_abs_tie, "'fixed' -> 'rules'"),
    "a0b3b28854fa500c": ("flow_lift.FlowCurveBias bias_k after 5x(+10 K) then 0 K", p_flow_settled, n_flow_settled, "9.0 -> 8.333"),
    "c38d53ab787ddbfa": ("price_model.observe_day_quarters(96 x 1e-6) -> (accepted, quarter_days, mean==1e-6)", p_quarter_floor, n_quarter_floor, "False -> True"),
    "22b5ec8775d5bd50": ("thermal_model._valve_two_zone_delivery throttled branch, (T_buf, q_rad, q_floor) grid", p_valve, n_valve, "throttled -> unthrottled"),
    "5cc84148fa68bda1": ("grid_fee.min_component tie fixed=rule=-0.2", p_min_tie, n_min_tie, "'fixed' -> 'rules'"),
    "a4b00ac3ca662eec": ("thermal_model.ThermalParameters.seasonal_inlet_temp sum over amplitude {0,-0,1e-300,-1} x 74 days", p_inlet, n_inlet, "equivalent: no move"),
    "5e8d48eff7e4fa8d": ("coordinator._on_power_event: peak_guard.suppressing with tariff disabled, retained peak 2 kW", p_power_event, n_power_event, "False -> True"),
    "d931ab195b940b0c": ("tariff._smooth_topk_sum(plateau, k=0)", p_topk, n_topk, "0.0 -> top-1 soft sum"),
}


def main() -> None:
    keys = [a for a in sys.argv[1:] if not a.startswith("-")] or list(PROBES)
    moved_total = 0
    for key in keys:
        what, probe, null, expect = PROBES[key]
        mut = mutant_of(key)
        rel = mut["file"]
        mb, mm = load(rel, None), load(rel, mut)
        vb, vm = probe(mb), probe(mm)
        nb, nm = null(mb), null(mm)
        moved = int(vb != vm)
        moved_total += moved
        print(f"RESULT key={key} site={Path(rel).name}:{mut['line']} probe={what!r}")
        print(f"RESULT key={key} value_baseline={vb}")
        print(f"RESULT key={key} value_mutant={vm}")
        print(f"RESULT key={key} moved={moved} expect={expect!r}")
        print(f"RESULT key={key} null_equal={int(nb == nm)} null_value={nb}")
    print(f"RESULT keys={len(keys)} moved={moved_total}")
    print("RESULT thread_factor=1.0")


if __name__ == "__main__":
    main()
