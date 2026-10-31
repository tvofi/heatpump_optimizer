"""D12-s2 (round 9, D12.M3): on an on/off heat pump (min == max power) every
full-power step publishes as "eco" on the Heat Pump Action sensor, and
power_normalized leaves [0, 1].

Metric (one line): full_power_mislabelled = number of plan steps whose planned
space power is >= 0.99 * max_electrical_power and whose published
``HeatPumpActionSensor.native_value`` is not "boost"; summed over the grid.
Second metric: norm_out_of_range = steps whose published ``power_normalized``
attribute is < -0.01 or > 1.01.

Count key: the value the production seam delivers -- the sensor's own
``native_value`` / ``extra_state_attributes["power_normalized"]`` fed the dict
``HeatPumpOptimizer.get_current_action`` returns for that step -- not the
config's min/max.

Arms: modulating (profiles.house(): min 1.0, max 6.0 kW; null control) and
onoff (min == max == 6.0 kW; a fixed-speed pump, accepted by
config_flow._power_errors). Grid: 9 golden SCENARIOS cells; leave-one-out printed.

Perturbation (--min 5.0): the onoff arm's min_electrical_power set to 5.0 kW
(a 1 kW modulation range): full_power_mislabelled must fall to 0 (DOWN).
One-line production alternative the judge may run instead: in
``HeatPumpOptimizer.get_current_action`` replace ``max(p_range, 0.1)`` by
``max(p_range, 1e-9)`` and guard p_range == 0 -> p_norm = 1.0 when on.

Run:   PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D12/s2/onoff_label.py
Expected (baseline): RESULT onoff_full_power_mislabelled > 100 steps, modulating_full_power_mislabelled=0,
       onoff_power_normalized_min << -1 (exact values printed; +-10%)
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
Machine: box B7 cloud container, Linux 6.18, 4 vCPU, numpy/OpenBLAS; counts only.
Root rule: run from the repository root; relative tests/ and custom_components/.
"""
import os

for _threads in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_threads, "1")

import argparse
import sys
import time
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np

import golden
from golden import START, make

CELLS = (
    "winter_single_dhw",
    "winter_single_no_dhw",
    "winter_two_zone_dhw",
    "winter_two_zone_no_dhw",
    "shoulder",
    "shoulder_two_zone",
    "summer_dhw_only",
    "flat_prices",
    "mild_windy_rain",
)
P_MAX = 6.0


def _sensor(p_min):
    from harness import FakeEntry, FakeHass
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    from heatpump_optimizer.sensor import HeatPumpActionSensor

    cfg = {
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "heat_pump_max_power": P_MAX,
        "heat_pump_min_power": p_min,
    }
    entry = FakeEntry(data=cfg)
    coord = HeatPumpOptimizerCoordinator(FakeHass(), entry)
    return coord, HeatPumpActionSensor(coord, entry)


def cell(name, p_min, coord, sensor):
    spec = dict(golden.SCENARIOS[name])
    po = dict(spec.pop("param_overrides", None) or {})
    po["min_electrical_power"] = p_min
    built = make(param_overrides=po, **spec)
    res = built["optimizer"].optimize(
        built["state"], built["prices"], built["outdoor"], built["wind"],
        built["rain"], built["solar"], START,
    )
    mis = oor = 0
    norms = []
    for i, ts in enumerate(res.timestamps):
        action = coord._optimizer.get_current_action(res, ts + timedelta(minutes=1))
        coord.data = {"current_action": action}
        state = sensor.native_value
        norm = sensor.extra_state_attributes.get("power_normalized")
        norms.append(norm)
        if float(res.power_schedule[i]) >= 0.99 * P_MAX and state != "boost":
            mis += 1
        if norm is not None and (norm < -0.01 or norm > 1.01):
            oor += 1
    return mis, oor, min(norms), max(norms)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=float, default=6.0, help="onoff arm's min kW")
    args = ap.parse_args()
    t0p, t0t = time.process_time(), time.thread_time()
    for arm, p_min in (("modulating", 1.0), ("onoff", args.min)):
        coord, sensor = _sensor(p_min)
        per = {}
        tot_oor = 0
        lo, hi = 1e9, -1e9
        for name in CELLS:
            mis, oor, nmin, nmax = cell(name, p_min, coord, sensor)
            per[name] = mis
            tot_oor += oor
            lo, hi = min(lo, nmin), max(hi, nmax)
            print(f"CELL arm={arm} cell={name} full_power_mislabelled={mis} "
                  f"norm_out_of_range={oor} norm_min={nmin} norm_max={nmax}")
        vals = sorted(per.values())
        print(f"RESULT {arm}_full_power_mislabelled={sum(vals)} steps")
        print(f"RESULT {arm}_cells_with_mislabel={sum(1 for v in vals if v)} cells")
        print(f"RESULT {arm}_mislabel_range={vals[0]}..{vals[-1]} steps")
        print(f"RESULT {arm}_full_power_mislabelled_loo={sum(vals[:-1])} steps")
        print(f"RESULT {arm}_norm_out_of_range={tot_oor} steps")
        print(f"RESULT {arm}_power_normalized_min={lo} ratio")
        print(f"RESULT {arm}_power_normalized_max={hi} ratio")
    proc, thr = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={proc / max(thr, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    swap = 0
    try:
        with open("/proc/vmstat") as fh:
            for line in fh:
                if line.startswith("pswpin "):
                    swap = int(line.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={swap}")


if __name__ == "__main__":
    main()
