#!/usr/bin/env python3
# Shared helper of the D3-g43 probes (not a probe itself). A probe builds a scratch copy of the baseline
# package with ONE production line edited (`make_variant`), runs `child_digest` in a subprocess per
# variant (so both versions import under the same package name) and compares the arrays.
# Nothing under the gate's tree changes: the copies live under a temp dir.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve()


def repo_root():
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in HERE.parents:
        if (cand / marker).is_file():
            return cand
    raise RuntimeError("no repository root")


ROOT = repo_root()
# Source of the scratch copies: an untouched baseline checkout (the gate mutates ROOT while it runs).
SRC = Path(os.environ.get("D3G43_SRC", "/home/user/heatpump_optimizer"))
if not (SRC / "custom_components").is_dir():
    SRC = ROOT
TM = Path("custom_components") / "heatpump_optimizer" / "thermal_model.py"


def make_variant(line, old, new, tag):
    """Scratch tree: the baseline's package, tests/hastub and tests/profiles.py, thermal_model.py:line edited."""
    d = Path(tempfile.mkdtemp(prefix=f"d3g43-{tag}-"))
    shutil.copytree(SRC / "custom_components", d / "custom_components")
    (d / "tests").mkdir()
    shutil.copytree(SRC / "tests" / "hastub", d / "tests" / "hastub")
    shutil.copy(SRC / "tests" / "profiles.py", d / "tests" / "profiles.py")
    if old is not None:
        f = d / TM
        lines = f.read_text().split("\n")
        assert old in lines[line - 1], (line, old, lines[line - 1])
        lines[line - 1] = lines[line - 1].replace(old, new, 1)
        f.write_text("\n".join(lines))
    return d


def digest(variant, scenario_fn, args):
    """Run `scenario_fn(args)` (a function name of this module) in a child with `variant` as the tree."""
    env = dict(os.environ, PYTHONPATH=f"{variant}/tests/hastub:{variant}/tests:{variant}", D3G43_CHILD="1")
    out = subprocess.run(
        [sys.executable, str(HERE), scenario_fn, json.dumps(args)],
        cwd=variant, env=env, capture_output=True, text=True, timeout=900)
    if out.returncode:
        return {"error": (out.stderr or out.stdout)[-600:]}
    return json.loads(out.stdout.strip().splitlines()[-1])


# ---------------------------------------------------------------- child side
def _setup(a):
    import numpy as np
    from datetime import datetime
    from profiles import house, weather
    from custom_components.heatpump_optimizer.thermal_model import (
        ThermalModel, ThermalParameters, ThermalState)
    from custom_components.heatpump_optimizer.weather_series import WeatherSeries  # noqa
    return np, datetime, house, weather, ThermalModel, ThermalParameters, ThermalState, WeatherSeries


def batch_scenario(a):
    """a: dict(two_zone, extra, param_over, state_over, dt, n, weather, ext, start_hour, seed, pmax, scalar)
    -> flat arrays of batch (and optionally scalar) trajectories, as lists."""
    np, datetime, house, weather, ThermalModel, ThermalParameters, ThermalState, WeatherSeries = _setup_ws(a)
    cfg = house(two_zone=a.get("two_zone", True))
    p = ThermalParameters.from_config({**cfg, **a.get("extra", {})})
    for k, v in a.get("param_over", {}).items():
        setattr(p, k, v)
    m = ThermalModel(p)
    n = a.get("n", 24)
    rng = np.random.default_rng(a.get("seed", 7))
    powers = rng.uniform(0, a.get("pmax", 3.0), size=(4, n))
    ot, wi, ra, so = (x[:n] for x in weather(a.get("weather", "winter_cold"), datetime(2026, 1, 15)))
    ext = np.full(n, a.get("ext", 0.0)) if a.get("ext") is not None else None
    wood = a.get("wood", False)
    sk = dict(room_temperature=20.5, slab_temperature=22.0, outdoor_temperature=float(ot[0]),
              upper_floor_temperature=21.2, lower_floor_temperature=20.1, buffer_tank_temperature=48.0,
              wood_tank_temperature=52.0 if wood else None)
    sk.update(a.get("state_over", {}))
    st = ThermalState(**sk)
    ws = WeatherSeries(outdoor_temps=ot, wind_speeds=wi, precipitation=ra, solar_radiation=so,
                       humidity=np.full(n, 78.0), external_heat_kw=ext)
    vt = np.linspace(30.0, 60.0, n) if a.get("valve_targets") else None
    res = m.simulate_trajectory_batch(st, powers, ws, dt_hours=a.get("dt", 0.25),
                                      start_hour=a.get("start_hour", 7.0), valve_targets=vt)
    out = {}
    for k in ("room", "slab", "upper", "lower", "buffer", "wood", "refused"):
        v = res.get(k)
        out["b_" + k] = None if v is None else np.asarray(v).ravel().tolist()
    if a.get("scalar", True):
        for k in ("room", "slab", "upper", "lower", "buffer", "wood"):
            out["s_" + k] = []
        for b in range(powers.shape[0]):
            tr = m.simulate_trajectory(st, powers[b], ws, dt_hours=a.get("dt", 0.25),
                                       start_hour=a.get("start_hour", 7.0))
            r, s, u, l, buf, _, w = tr
            for k, v in (("room", r), ("slab", s), ("upper", u), ("lower", l), ("buffer", buf), ("wood", w)):
                out["s_" + k] += ([] if v is None else np.asarray(v).ravel().tolist())
    return out


def _setup_ws(a):
    import numpy as np
    from datetime import datetime
    from profiles import house, weather
    from custom_components.heatpump_optimizer import thermal_model as tm
    ws_cls = getattr(tm, "WeatherSeries", None)
    if ws_cls is None:
        import importlib, inspect
        for name in ("weather_series", "types", "models"):
            try:
                mod = importlib.import_module("custom_components.heatpump_optimizer." + name)
                if hasattr(mod, "WeatherSeries"):
                    ws_cls = mod.WeatherSeries
                    break
            except Exception:
                pass
    return np, datetime, house, weather, tm.ThermalModel, tm.ThermalParameters, tm.ThermalState, ws_cls


def battery(scenarios):
    """Child side: run every scenario, one result (or the exception text) each."""
    res = []
    for a in scenarios:
        try:
            res.append(batch_scenario(a))
        except Exception as e:  # noqa
            res.append({"error": f"{type(e).__name__}: {e}"[:200]})
    return res


def default_battery():
    sc = []
    cfgs = {
        "novalve": ({"mixing_valve_mode": "none"}, False),
        "single": ({"mixing_valve_mode": "manual", "two_zone_mode": "on"}, False),
        "twotank": ({"mixing_valve_mode": "manual", "two_zone_mode": "on", "wood_furnace_enabled": True,
                     "wood_tank_top_entity": "sensor.w_top"}, True),
        "slabdirect": ({"mixing_valve_mode": "manual", "two_zone_mode": "on",
                        "topology_layout": "valve_upper_direct_slab"}, False),
        "smartread_twotank": ({"mixing_valve_mode": "smart_read", "two_zone_mode": "on", "wood_furnace_enabled": True,
                               "wood_tank_bottom_entity": "sensor.w_bot"}, True),
        "singlezone_valve": ({"mixing_valve_mode": "manual", "two_zone_mode": "off"}, False),
    }
    for name, (ex, wood) in cfgs.items():
        sc.append({"two_zone": name != "singlezone_valve", "extra": ex, "wood": wood, "label": name, "cfgname": name})
    base = list(sc)
    # state / weather / step-length variations on the throttled two-zone valve configs
    for b in base:
        if b["cfgname"] == "novalve":
            continue
        for tag, over in (
            ("hotbuf", {"state_over": {"buffer_tank_temperature": 75.0}}),
            ("coldbuf", {"state_over": {"buffer_tank_temperature": 15.0}}),
            ("hotwood", {"state_over": {"wood_tank_temperature": 85.0}}),
            ("coldwood", {"state_over": {"wood_tank_temperature": 20.0}}),
            ("midbuf", {"state_over": {"buffer_tank_temperature": 24.0, "slab_temperature": 23.0}}),
            ("ext", {"ext": 4.0}),
            ("pmax0", {"pmax": 0.0}),
            ("pmax9", {"pmax": 9.0}),
            ("mild", {"weather": "summer_warm"}),
            ("dt1h", {"dt": 1.0}),
            ("dt0", {"dt": 0.0, "scalar": False}),
            ("dttiny", {"dt": 1e-7, "scalar": False}),
            ("nohour", {"start_hour": None}),
            ("gains", {"start_hour": 18.0, "param_over_gains": True}),
        ):
            c = dict(b); c.update(over)
            c["label"] = b["label"] + " " + tag
            if over.get("param_over_gains"):
                c["param_over"] = {**b.get("param_over", {}), "internal_gains_profile": [0.1 * (1 + (i % 7)) for i in range(24)]}
            sc.append(c)
    extra = []
    for name in ("single", "twotank", "slabdirect", "smartread_twotank"):
        ex, wood = cfgs[name]
        for tag, over in (
            ("buf_just_below_floor_p0", {"pmax": 0.0, "state_over": {"buffer_tank_temperature": 20.8}}),
            ("slab_colder_than_upper", {"state_over": {"slab_temperature": 12.0, "upper_floor_temperature": 24.0}}),
            ("slab_cold_buf_cold_p0", {"pmax": 0.0, "state_over": {"slab_temperature": 12.0, "upper_floor_temperature": 24.0,
                                                                "buffer_tank_temperature": 15.0}}),
            ("slab_cold_buf_hot", {"state_over": {"slab_temperature": 12.0, "upper_floor_temperature": 24.0,
                                                 "buffer_tank_temperature": 70.0, "wood_tank_temperature": 80.0 if wood else None}}),
            ("wood_just_below_floor_p0", {"pmax": 0.0, "state_over": {"buffer_tank_temperature": 20.8,
                                                                      "wood_tank_temperature": 20.9 if wood else None}}),
            ("wood_hot_buf_cold_ext", {"ext": 3.0, "state_over": {"buffer_tank_temperature": 21.0,
                                                                  "wood_tank_temperature": 85.0 if wood else None}}),
            ("dt0_hotwood", {"dt": 0.0, "scalar": False, "state_over": {"wood_tank_temperature": 85.0 if wood else None}}),
            ("dttiny_hotwood", {"dt": 1e-7, "scalar": False, "state_over": {"wood_tank_temperature": 85.0 if wood else None}}),
            ("dt0_p0_flat", {"dt": 0.0, "pmax": 0.0, "scalar": False, "state_over": {"buffer_tank_temperature": 20.0, "slab_temperature": 20.0}}),
            ("tiny_dt_nosub", {"dt": 1e-4, "scalar": False}),
            ("valve_target", {"valve_targets": True, "scalar": False}),
            ("hot_floors_cold_buf_p0", {"pmax": 0.0, "state_over": {"buffer_tank_temperature": 40.0, "slab_temperature": 45.0,
                                         "upper_floor_temperature": 45.0, "lower_floor_temperature": 45.0, "room_temperature": 45.0}}),
            ("hot_floors_cold_buf_p0_ext", {"pmax": 0.0, "ext": 2.0, "state_over": {"buffer_tank_temperature": 40.0, "slab_temperature": 45.0,
                                         "upper_floor_temperature": 45.0, "lower_floor_temperature": 45.0, "room_temperature": 45.0,
                                         "wood_tank_temperature": 38.0 if wood else None}}),
            ("dt0_coldwood", {"dt": 0.0, "scalar": False, "state_over": {"wood_tank_temperature": 10.0 if wood else None, "buffer_tank_temperature": 10.0}}),
            ("dt0_coldbuf", {"dt": 0.0, "pmax": 0.0, "scalar": False, "state_over": {"buffer_tank_temperature": 10.0, "slab_temperature": 30.0}}),
            ("dt1e6_boundary", {"dt": 1e-6, "scalar": False, "state_over": {"buffer_tank_temperature": 10.0, "slab_temperature": 30.0, "wood_tank_temperature": 10.0 if wood else None}}),
            ("dtneg", {"dt": -0.25, "scalar": False}),
        ):
            c = {"two_zone": True, "extra": ex, "wood": wood, "cfgname": name, "label": f"{name} {tag}"}
            c.update(over)
            extra.append(c)
    return sc + extra


def step_battery(scenarios):
    """Child side: ThermalModel.simulate_step on one state per scenario (n_sub as the model derives it)."""
    import dataclasses
    import numpy as np
    from profiles import house
    from custom_components.heatpump_optimizer import thermal_model as tm
    cfgs = default_cfgs()
    out = []
    for a in scenarios:
        try:
            ex, wood = cfgs[a["cfgname"]]
            p = tm.ThermalParameters.from_config({**house(two_zone=a["cfgname"] != "singlezone_valve"), **ex, **a.get("cfg_over", {})})
            for k, v in a.get("param_over", {}).items():
                setattr(p, k, v)
            m = tm.ThermalModel(p)
            sk = dict(room_temperature=20.5, slab_temperature=22.0, outdoor_temperature=a.get("out", -5.0),
                      upper_floor_temperature=21.2, lower_floor_temperature=20.1, buffer_tank_temperature=48.0,
                      wood_tank_temperature=52.0 if wood else None)
            sk.update(a.get("state_over", {}))
            st = tm.ThermalState(**sk)
            args = dict(a.get("kw", {}))
            r = m.simulate_step(st, a.get("power", 1.5), a.get("out", -5.0), a.get("wind", 2.0), a.get("rain", 0.0),
                                a.get("solar", 50.0), a.get("dt", 0.25), a.get("ext", 0.0), a.get("valve", None),
                                a.get("hum", 78.0), a.get("hour", 7.0), **args)
            d = dataclasses.asdict(r)
            vec = [v for v in d.values() if v is not None and isinstance(v, (int, float))]
            vec += [m._step_buffer_refused, m._step_wood_refused]
            out.append({"vec": vec, "nsub": m._substeps_and_loss(a.get("wind", 2.0), a.get("rain", 0.0), a.get("dt", 0.25))[0]})
        except Exception as e:  # noqa
            out.append({"error": f"{type(e).__name__}: {e}"[:300]})
    return out


def default_cfgs():
    return {
        "novalve": ({"mixing_valve_mode": "none"}, False),
        "single": ({"mixing_valve_mode": "manual", "two_zone_mode": "on"}, False),
        "twotank": ({"mixing_valve_mode": "manual", "two_zone_mode": "on", "wood_furnace_enabled": True,
                     "wood_tank_top_entity": "sensor.w_top"}, True),
        "slabdirect": ({"mixing_valve_mode": "manual", "two_zone_mode": "on",
                        "topology_layout": "valve_upper_direct_slab"}, False),
        "singlezone_valve": ({"mixing_valve_mode": "manual", "two_zone_mode": "off"}, False),
        "plain": ({}, False),
    }


def step_scenarios():
    sc = []
    for name in ("plain", "novalve", "single", "twotank", "slabdirect", "singlezone_valve"):
        for tag, over in (
            ("base", {}), ("windy", {"wind": 25.0, "rain": 5.0}), ("hot", {"out": 25.0, "solar": 700.0, "hum": 40.0}),
            ("cold", {"out": -25.0, "hum": 95.0}), ("dt1", {"dt": 1.0}), ("dt4", {"dt": 4.0}), ("dtsmall", {"dt": 0.01}),
            ("meas", {"kw": {"measured_heat_kw": 3.2}}), ("exo", {"kw": {"buffer_exo_kw": 1.5}}),
            ("ext", {"ext": 2.5}), ("valve", {"valve": 40.0}), ("nopower", {"power": 0.0}), ("maxpower", {"power": 6.0}),
            ("nohum", {"hum": None}), ("nohour", {"hour": None}), ("hotbuf", {"state_over": {"buffer_tank_temperature": 80.0}}),
            ("coldbuf", {"state_over": {"buffer_tank_temperature": 12.0}}),
            ("lightmass", {"param_over": {"room_thermal_mass": 0.2}}),
        ):
            c = {"cfgname": name, "label": f"{name} {tag}"}
            c.update(over)
            sc.append(c)
    return sc


def run_step_probe(metric_prefix, line, old, new):
    sc = step_scenarios()
    bv = make_variant(line, None, None, "base"); mv = make_variant(line, old, new, "mut")
    rb = digest(bv, "step_battery", sc); rm = digest(mv, "step_battery", sc)
    if isinstance(rb, dict) or isinstance(rm, dict):
        print("child error:", rb if isinstance(rb, dict) else rm); return []
    moved, errs, worst, nsubs = [], 0, 0.0, {}
    for a, x, y in zip(sc, rb, rm):
        if "error" in x or "error" in y:
            errs += 1
            if "error" in x and "error" in y and errs <= 2: print("  err:", a["label"], x["error"][:120])
            continue
        nsubs[x["nsub"]] = nsubs.get(x["nsub"], 0) + 1
        d = maxdiff(x["vec"], y["vec"])
        if d != 0: moved.append((a["label"], d))
        worst = max(worst, d)
    print(f"scenarios={len(sc)} errored={errs} n_sub_histogram={nsubs} moved={len(moved)}")
    for lab, d in moved[:6]: print(f"  moved: {lab} maxdiff={d:.6g}")
    print(f"RESULT {metric_prefix}_baseline_vs_mutant_max_abs_diff={worst:.6g}")
    print(f"RESULT {metric_prefix}_scenarios_moved={len(moved)}")
    return moved


def maxdiff(x, y):
    """Largest |x-y|; a NaN/inf that appears on one side only counts as inf (it is a difference)."""
    import math
    if x is None and y is None:
        return 0.0
    if x is None or y is None or len(x) != len(y):
        return float("inf")
    worst = 0.0
    for p, q in zip(x, y):
        if p == q or (p != p and q != q):
            continue
        d = abs(p - q)
        worst = max(worst, float("inf") if d != d else d)
    return worst


def run_probe(metric_prefix, line, old, new, *, scenarios=None, scalar_cmp=True):
    """Parent side: baseline vs mutant over the battery. Prints RESULT lines; returns the list of moved scenarios."""
    sc = scenarios if scenarios is not None else default_battery()
    base_v = make_variant(line, None, None, "base")
    mut_v = make_variant(line, old, new, "mut")
    rb = digest(base_v, "battery", sc)
    rm = digest(mut_v, "battery", sc)
    if isinstance(rb, dict) or isinstance(rm, dict):
        print("child error:", rb if isinstance(rb, dict) else rm)
        return []
    moved, errs = [], 0
    wood_presence = 0
    worst = 0.0
    parity_base = 0.0
    parity_mut = 0.0
    for a, x, y in zip(sc, rb, rm):
        if "error" in x or "error" in y:
            errs += 1
            continue
        d = max(maxdiff(x[k], y[k]) for k in x if k.startswith("b_") and k != "b_wood")
        if (x["b_wood"] is None) != (y["b_wood"] is None):
            wood_presence += 1
        elif x["b_wood"] is not None:
            d = max(d, maxdiff(x["b_wood"], y["b_wood"]))
        if d > 0:
            moved.append((a["label"], d))
        worst = max(worst, d)
        if a.get("scalar", True):
            for pb, res in ((0, x), (1, y)):
                pd = max(maxdiff(res["b_" + k], res["s_" + k]) for k in ("room", "slab", "upper", "lower", "buffer"))
                if pb == 0:
                    parity_base = max(parity_base, pd)
                else:
                    parity_mut = max(parity_mut, pd)
    print(f"scenarios={len(sc)} errored={errs} moved={len(moved)}")
    for lab, d in moved[:6]:
        print(f"  moved: {lab} maxdiff={d:.6g}")
    print(f"RESULT {metric_prefix}_baseline_vs_mutant_max_abs_diff={worst:.6g}")
    print(f"RESULT {metric_prefix}_scenarios_moved={len(moved)}")
    print(f"RESULT {metric_prefix}_wood_array_dropped_scenarios={wood_presence}")
    print(f"RESULT batch_vs_scalar_parity_baseline={parity_base:.6g}")
    print(f"RESULT batch_vs_scalar_parity_mutant={parity_mut:.6g}")
    return moved


if __name__ == "__main__" and os.environ.get("D3G43_CHILD"):
    fn = globals()[sys.argv[1]]
    print(json.dumps(fn(json.loads(sys.argv[2]))))
