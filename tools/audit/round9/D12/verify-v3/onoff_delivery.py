"""D12 verify-v3 (round 9), own harness for D12-s2-01: what an on/off pump
actually delivers when actuated by the production switch schedule, under two
plant readings of "ON".

Metric (one line): per cell, for min == max == 6 kW, sub_floor_heat_frac =
planned space+DHW kWh in steps whose planned power is > 0.1 kW but below the
production on-threshold (HeatPumpOptimizer._power_to_heat_pump_schedule returns
False) over all planned kWh; and, re-simulated through ThermalModel.simulate_step,
Kh_below_plan for two actuation models of an enabled step:
  (a) "plan-power": an ON step delivers the planned power (the finder's model),
  (b) "rated-power": an ON step runs the fixed-speed compressor at 6 kW for the
      whole step (a fixed-speed pump cannot run at the plan's 3-6 kW either),
and Kh_below_min (degree-hours below min_temperature) for both.
Cells: shoulder, shoulder_two_zone, winter_two_zone_dhw (the finder's failing
cells), flat_prices (a passing cell). Builders: tests/golden.make + SCENARIOS.

Perturbation --threshold01: _power_to_heat_pump_schedule patched in memory to a
0.1 kW on-threshold (the finder's perturbation); sub_floor_heat_frac -> 0.

Run:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D12/verify-v3/onoff_delivery.py [--threshold01]
Expected: shoulder sub_floor_heat_frac ~0.67 (+-0.05); Kh_below_min 0 in both models; see report. Deterministic.
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence 6f51db2c).
Machine: G2-V3 cloud container, 4 vCPU, CPython 3.14.0rc2, numpy/OpenBLAS.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys
import time
from unittest import mock

import numpy as np

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import golden  # noqa: E402
from golden import START, make  # noqa: E402
from heatpump_optimizer.optimizer import HeatPumpOptimizer  # noqa: E402

DT = 0.25
CELLS = ("shoulder", "shoulder_two_zone", "winter_two_zone_dhw", "flat_prices")


def _thr01(self, space, dhw=None):
    s = np.asarray(space, float)
    d = np.zeros_like(s) if dhw is None else np.asarray(dhw, float)[: len(s)]
    return (np.maximum(s, d) >= 0.1).tolist()


def run(name):
    spec = dict(golden.SCENARIOS[name])
    po = dict(spec.pop("param_overrides", None) or {})
    po["min_electrical_power"] = 6.0
    po["max_electrical_power"] = 6.0
    b = make(param_overrides=po, **spec)
    opt = b["optimizer"]
    res = opt.optimize(b["state"], b["prices"], b["outdoor"], b["wind"], b["rain"], b["solar"], START)
    sp = np.asarray(res.power_schedule, float)
    n = len(sp)
    dh = np.asarray(res.dhw_power_schedule or np.zeros(n), float)
    dh = dh[:n] if len(dh) >= n else np.pad(dh, (0, n - len(dh)))
    on = np.asarray(opt._power_to_heat_pump_schedule(sp, dh), bool)
    tot = float((sp + dh).sum() * DT)
    sub = float(((sp + dh) * (~on) * ((sp + dh) > 0.1)).sum() * DT)
    floor = float(opt.config.min_temp)
    rooms = {}
    for arm, power in (("planned", sp), ("plan_power", sp * on),
                       ("rated_power", np.where(on & (sp > 0.1), 6.0, 0.0))):
        st = b["state"]
        r = []
        for i in range(n):
            st = opt.model.simulate_step(st, float(power[i]), float(b["outdoor"][i]), float(b["wind"][i]),
                                         float(b["rain"][i]), float(b["solar"][i]), DT)
            r.append(float(st.room_temperature))
        rooms[arm] = (np.asarray(r), float(power.sum() * DT))
    plan_r = rooms["planned"][0]
    out = {"planned_kwh": round(tot, 2), "sub_floor_heat_frac": round(sub / tot, 3) if tot else 0.0}
    for arm in ("plan_power", "rated_power"):
        r, kwh = rooms[arm]
        out[f"{arm}_space_kwh"] = round(kwh, 2)
        out[f"{arm}_Kh_below_plan"] = round(float(np.clip(plan_r - r, 0, None).sum() * DT), 2)
        out[f"{arm}_Kh_above_plan"] = round(float(np.clip(r - plan_r, 0, None).sum() * DT), 2)
        out[f"{arm}_Kh_below_min"] = round(float(np.clip(floor - r, 0, None).sum() * DT), 2)
        out[f"{arm}_min_room"] = round(float(r.min()), 2)
    out["planned_space_kwh"] = round(rooms["planned"][1], 2)
    out["planned_min_room"] = round(float(plan_r.min()), 2)
    return out


def main():
    t0, tt0 = time.process_time(), time.thread_time()
    ctx = (mock.patch.object(HeatPumpOptimizer, "_power_to_heat_pump_schedule", _thr01)
           if "--threshold01" in sys.argv else mock.patch.object(HeatPumpOptimizer, "__doc__", HeatPumpOptimizer.__doc__))
    with ctx:
        for c in CELLS:
            r = run(c)
            print(f"CELL {c}: {r}")
            for k in ("sub_floor_heat_frac", "plan_power_Kh_below_plan", "rated_power_Kh_below_plan",
                      "rated_power_Kh_above_plan", "plan_power_Kh_below_min", "rated_power_Kh_below_min"):
                print(f"RESULT {c}_{k}={r[k]}")
    pc, tc = time.process_time() - t0, time.thread_time() - tt0
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
    except Exception:  # noqa: BLE001
        sw = "na"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
