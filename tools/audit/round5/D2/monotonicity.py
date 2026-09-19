"""D2 round-5 harness 2: monotonicity and physical bounds.

METRIC DEFINITIONS
------------------
* ``mono_wrong_<store>`` — over a swept grid of (outdoor, initial state,
  valve mode), the NUMBER of cells where raising the electrical power by
  +0.1 kW LOWERS that store's end-of-step temperature by more than 1e-9 K.
  Physics says zero for every store the compressor charges.  ``buffer`` and
  the zone stores are compressor-charged; ``wood`` is charged only by
  external heat, so its count is reported separately and not claimed.
* ``bound_max_over_<name>`` — over every golden scenario, the largest amount
  by which the simulated trajectory exceeds a physical bound the tree itself
  states: ``buffer_max_temp``, ``dhw_hard_max_temp``, ``WOOD_TANK_MAX_TEMP``,
  the comfort ``max_temp``, and the cold floor (DHW inlet / -40 degC).
  Units: K.

COMMAND
-------
    PYTHONPATH=tests/hastub python3 tools/audit/round5/D2/monotonicity.py

Expected: every ``mono_wrong_*`` zero for the compressor-charged stores, and
every ``bound_max_over_*`` at or below 1e-6 K.  Baseline
9bcb7352cabb43b413f5e3ca41b6dda1ac6d69.  Machine: darwin arm64, 8-core M1.

ROOT RULE: repository root from ``__file__`` (four parents up).
"""
import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

import golden  # noqa: E402
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

RESULT = []


def emit(name, value, unit):
    RESULT.append((name, value, unit))
    print(f"RESULT {name}={value} {unit}", flush=True)


STORES = (
    "room",
    "slab",
    "upper",
    "lower",
    "buffer",
    "wood",
)


def _state(t_out, buf, wood=None, upper=21.0, slab=22.0):
    return ThermalState(
        room_temperature=upper,
        slab_temperature=slab,
        outdoor_temperature=t_out,
        upper_floor_temperature=upper,
        lower_floor_temperature=upper,
        buffer_tank_temperature=buf,
        wood_tank_temperature=wood,
    )


def monotonicity():
    wrong = {s: 0 for s in STORES}
    cells = 0
    worst = 0.0
    worst_where = ""
    for valve in ("off", "manual", "smart_write"):
        for t_out in (-20.0, -10.0, -2.0, 4.0, 10.0):
            for buf in (25.0, 35.0, 45.0, 55.0):
                for wood in (None, 25.0, 40.0, 60.0):
                    for p_el in (0.0, 1.0, 2.0, 3.0):
                        cfg = golden.house(two_zone=True, dhw=False)
                        cfg["mixing_valve_mode"] = valve
                        cfg["buffer_tank_volume"] = 750.0
                        cfg["buffer_max_temperature"] = 70.0
                        if wood is not None:
                            cfg["wood_tank_top_entity"] = "sensor.wood_top"
                            cfg["wood_tank_volume"] = 500.0
                        params = ThermalParameters.from_config(cfg)
                        m = ThermalModel(params)
                        a = _state(t_out, buf, wood)
                        b = _state(t_out, buf, wood)
                        lo = m.simulate_step(
                            a, p_el, t_out, external_heat_kw=2.0
                        )
                        hi = m.simulate_step(
                            b, p_el + 0.1, t_out, external_heat_kw=2.0
                        )
                        cells += 1
                        for name, attr in (
                            ("room", "room_temperature"),
                            ("slab", "slab_temperature"),
                            ("upper", "upper_floor_temperature"),
                            ("lower", "lower_floor_temperature"),
                            ("buffer", "buffer_tank_temperature"),
                            ("wood", "wood_tank_temperature"),
                        ):
                            av = getattr(lo, attr)
                            bv = getattr(hi, attr)
                            if av is None or bv is None:
                                continue
                            d = bv - av
                            if d < -1e-9:
                                wrong[name] += 1
                                if -d > worst:
                                    worst = -d
                                    worst_where = (
                                        f"{name} valve={valve} Tout={t_out} "
                                        f"Tbuf={buf} Twood={wood} P={p_el}"
                                    )
    emit("mono_cells", cells, "count")
    for s in STORES:
        emit(f"mono_wrong_{s}", wrong[s], "count")
    emit("mono_worst_drop", f"{worst:.6f}", "K")
    emit("mono_worst_where", worst_where or "-", "label")


def bounds():
    worst = {
        "room_below_min": 0.0,
        "room_above_max": 0.0,
        "buffer_above_cap": 0.0,
        "buffer_below_floor": 0.0,
        "dhw_above_hard_max": 0.0,
        "wood_above_cap": 0.0,
        "dhw_below_inlet": 0.0,
    }
    cells = 0
    for name, spec in sorted(golden.SCENARIOS.items()):
        built = golden.make(**spec)
        opt = built["optimizer"]
        params = opt.model.params
        n = len(built["prices"])
        surplus = (
            golden.pv_surplus_for(n, built["solar"])
            if name in golden.PV_SCENARIOS
            else None
        )
        ext = (
            golden.external_heat_for(n)
            if name in golden.EXTERNAL_HEAT_SCENARIOS
            else None
        )
        caps = (
            np.full(n, params.max_electrical_power * 0.6)
            if name in golden.CAP_SCENARIOS
            else None
        )
        res = opt.optimize(
            built["state"], built["prices"], built["outdoor"], built["wind"],
            built["rain"], built["solar"], golden.START, pv_surplus=surplus,
            external_heat_kw=ext, power_caps_extra=caps,
        )
        cells += 1
        room = np.asarray(res.room_temp_trajectory, dtype=float)
        buf = np.asarray(res.buffer_temp_trajectory, dtype=float)
        dhw = np.asarray(res.dhw_temp_trajectory, dtype=float)
        wood = res.wood_temp_trajectory
        worst["room_below_min"] = max(
            worst["room_below_min"],
            float(np.max(opt.config.min_temp - room)),
        )
        worst["room_above_max"] = max(
            worst["room_above_max"],
            float(np.max(room - opt.config.max_temp)),
        )
        cap = float(params.buffer_max_temp)
        if buf.size:
            worst["buffer_above_cap"] = max(
                worst["buffer_above_cap"], float(np.max(buf - cap))
            )
            worst["buffer_below_floor"] = max(
                worst["buffer_below_floor"], float(np.max(0.0 - buf))
            )
        if dhw.size:
            worst["dhw_above_hard_max"] = max(
                worst["dhw_above_hard_max"],
                float(np.max(dhw - float(params.dhw_hard_max_temp))),
            )
            worst["dhw_below_inlet"] = max(
                worst["dhw_below_inlet"],
                float(np.max(float(params.dhw_inlet_reference) - dhw)),
            )
        if wood is not None and np.size(wood):
            from heatpump_optimizer.thermal_model import WOOD_TANK_MAX_TEMP

            w = np.asarray(wood, dtype=float)
            worst["wood_above_cap"] = max(
                worst["wood_above_cap"], float(np.max(w - WOOD_TANK_MAX_TEMP))
            )
    emit("bounds_cells", cells, "count")
    for k in sorted(worst):
        emit(f"bound_max_over_{k}", f"{worst[k]:.6f}", "K")


def main():
    t0 = time.monotonic()
    monotonicity()
    bounds()
    import resource

    tc, pc = time.thread_time(), time.process_time()
    emit("process_cpu", f"{pc:.3f}", "s")
    emit("thread_cpu", f"{tc:.3f}", "s")
    emit("thread_factor", f"{pc / max(tc, 1e-9):.4f}", "ratio")
    emit("load1", f"{os.getloadavg()[0]:.2f}", "count")
    emit("swapins", resource.getrusage(resource.RUSAGE_SELF).ru_majflt, "count")
    emit("wall", f"{time.monotonic() - t0:.2f}", "s")


if __name__ == "__main__":
    main()
