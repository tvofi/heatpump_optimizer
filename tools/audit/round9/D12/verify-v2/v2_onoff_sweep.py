"""D12 verify-v2 for D12-s2-01 and D12-s2-03: an on/off (min == max) pump over the stress.py season sweep.

Cells: tests/stress.py SEASONS (7) x {single-zone + DHW, two-zone no DHW} =
14 cells, built by stress.build_case (not the golden SCENARIOS the finder
used), 24 h at 15 min. Pump rating P = 5.0 kW (the shipped
DEFAULT_HEAT_PUMP_MAX_POWER, not the finder's 6.0).
Arms: onoff = heat_pump_min_power = heat_pump_max_power = P;
modulating (null control) = min 1.0, max P.

Metric s2-01 (count key: OptimizationResult.heat_pump_on_schedule, the
production _power_to_heat_pump_schedule output): off_heated_step_frac = steps
with max(space, dhw) planned power > 0.1 kW whose heat_pump_on_schedule is
False, over all such steps, pooled over cells; plus withheld kWh fraction
pooled; cells with withheld kWh frac > 0.10.
Metric s2-03 (count key: HeatPumpOptimizer.get_current_action(t_i)["mode"]
and ["power_normalized"], what HeatPumpActionSensor publishes): steps with
space power >= 0.99 P whose mode is not "boost"; min power_normalized.

Perturbations: --perturb-threshold patches
HeatPumpOptimizer._power_to_heat_pump_schedule in memory to a 0.1 kW
on-threshold (s2-01 must fall toward 0); --min-offset X sets the onoff arm's
min to P - X (s2-03 count must fall to 0 for X >= ~0.5).

Run:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D12/verify-v2/v2_onoff_sweep.py [--perturb-threshold] [--min-offset X]
Expected (deterministic solves; counts exact): onoff cells_withheld_gt10pct 4 of 14
(LOO 3), off_heated_step_frac 0.296, withheld_kwh_frac_pooled 0.109, full_power_not_boost
203 of 203, power_normalized_min -50.00; modulating 0 of 14, 0.051, 0.005, 0 of 189, -0.25.
--perturb-threshold: onoff 0 of 14, 0.000. --min-offset 1.0: onoff full_power_not_boost 0,
power_normalized_min -4.00, cells_withheld_gt10pct 3 of 14.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: G2-V2 cloud container, 4 vCPU, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys
import time
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402
import stress  # noqa: E402
from heatpump_optimizer.optimizer import HeatPumpOptimizer  # noqa: E402

P = 5.0
OFFSET = float(sys.argv[sys.argv.index("--min-offset") + 1]) if "--min-offset" in sys.argv else 0.0


def _thresh01(self, space, dhw=None):
    s = np.asarray(space, dtype=float)
    d = np.zeros_like(s) if dhw is None else np.asarray(dhw, dtype=float)
    return (np.maximum(s, d) >= 0.1).tolist()


def cell(season, two_zone, dhw, p_min):
    b = stress.build_case(season=season, two_zone=two_zone, dhw=dhw,
                          config={"heat_pump_min_power": p_min, "heat_pump_max_power": P})
    r = b["result"]
    space = np.asarray(r.power_schedule, dtype=float)
    dh = np.asarray(r.dhw_power_schedule or np.zeros_like(space), dtype=float)
    if len(dh) != len(space):
        dh = np.zeros_like(space)
    on = list(r.heat_pump_on_schedule)
    heat = np.maximum(space, dh)
    heated = heat > 0.1
    off_heated = sum(1 for i in range(len(space)) if heated[i] and not on[i])
    tot = float((space + dh).sum()) * 0.25
    withheld = float(sum((space[i] + dh[i]) for i in range(len(space)) if not on[i])) * 0.25
    return dict(heated=int(heated.sum()), off_heated=off_heated, tot=tot, withheld=withheld,
                result=r)


def actions(r, p_min):
    from heatpump_optimizer.thermal_model import ThermalModel
    from golden import house
    from heatpump_optimizer.thermal_model import ThermalParameters
    from heatpump_optimizer.optimizer import OptimizationConfig
    params = ThermalParameters.from_config({**house(), "heat_pump_min_power": p_min, "heat_pump_max_power": P})
    opt = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig())
    mis, pmin, fulls = 0, 1e9, 0
    for i, ts in enumerate(r.timestamps):
        a = opt.get_current_action(r, ts)
        pmin = min(pmin, float(a["power_normalized"]))
        if float(r.power_schedule[i]) >= 0.99 * P:
            fulls += 1
            if a["mode"] != "boost":
                mis += 1
    return fulls, mis, pmin


def main():
    t0, tt0 = time.process_time(), time.thread_time()
    ctx = (mock.patch.object(HeatPumpOptimizer, "_power_to_heat_pump_schedule", _thresh01)
           if "--perturb-threshold" in sys.argv else mock.patch.dict({}))
    with ctx:
        for arm, p_min in (("onoff", P - OFFSET), ("modulating", 1.0)):
            H = OFF = 0
            T = W = 0.0
            failing = 0
            fulls = mis = 0
            pnmin = 1e9
            fr = []
            for season in stress.SEASONS:
                for two_zone, dhw in ((False, True), (True, False)):
                    c = cell(season, two_zone, dhw, p_min)
                    H += c["heated"]
                    OFF += c["off_heated"]
                    T += c["tot"]
                    W += c["withheld"]
                    f = c["withheld"] / c["tot"] if c["tot"] > 0 else 0.0
                    fr.append(f)
                    failing += f > 0.10
                    fu, mi, pm = actions(c["result"], p_min)
                    fulls += fu
                    mis += mi
                    pnmin = min(pnmin, pm)
                    print(f"CELL arm={arm} {season}/{'2z' if two_zone else '1z'}/{'dhw' if dhw else 'space'} "
                          f"heated={c['heated']} off_heated={c['off_heated']} kwh={c['tot']:.2f} "
                          f"withheld={c['withheld']:.2f} frac={f:.3f} full={fu} full_not_boost={mi} pn_min={pm:.2f}")
            fr_sorted = sorted(fr)
            print(f"RESULT {arm}_off_heated_step_frac={OFF / max(H, 1):.3f} ({OFF}/{H} steps)")
            print(f"RESULT {arm}_withheld_kwh_frac_pooled={W / max(T, 1e-9):.3f} ({W:.2f}/{T:.2f} kWh)")
            print(f"RESULT {arm}_cells_withheld_gt10pct={failing} of {len(fr)} cells")
            print(f"RESULT {arm}_cells_withheld_gt10pct_loo={failing - (fr_sorted[-1] > 0.10)} cells (worst cell dropped)")
            print(f"RESULT {arm}_withheld_frac_range={fr_sorted[0]:.3f}..{fr_sorted[-1]:.3f}")
            print(f"RESULT {arm}_full_power_steps={fulls} steps")
            print(f"RESULT {arm}_full_power_not_boost={mis} steps")
            print(f"RESULT {arm}_power_normalized_min={pnmin:.2f}")
    pc, tc = time.process_time() - t0, time.thread_time() - tt0
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [ln for ln in open('/proc/vmstat') if ln.startswith('pswpin')][0].split()[1]
    except Exception:  # noqa: BLE001
        sw = "na"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
