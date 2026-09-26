"""D12 verify-v1 (round 9): D12-s2-01 method attack -- the finder's consequence
arm actuates an ON step at its PLANNED power; an on/off pump that is switched ON
runs at max_electrical_power. This measures the plan-vs-actuated energy both ways.

Metric (one line): per cell, actuated_full_kwh = sum over steps with production
heat_pump_on_schedule True of max_electrical_power*dt, divided by the plan's
planned space+DHW kWh (net_ratio; < 1 means the switch path delivers less than
the plan books, > 1 more). Also the finder's withheld_frac for the same cell.
Setpoint seam (same x10 divisor, optimizer._power_to_setpoints): count of plan
steps at >= 0.99*max power whose setpoint equals min_temp.
Count key: the production heat_pump_on_schedule / _power_to_setpoints output.

Run:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D12/verify-v1/onoff_delivered.py [--min 6.0]
Perturbation: --min 1.0 (modulating): net_ratio moves toward the modulating arm and the
setpoint count falls to 0.
Expected: onoff shoulder net_ratio reported exactly; setpoint count > 0 on onoff, 0 on modulating.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round9 evidence tree 6f51db2c).
Machine: G2-V1 cloud container, 4 vCPU, Python 3.14, numpy/OpenBLAS. Counts and ratios only.
Root rule: cwd (repository root), reuses s2/onoff_switch.py's solve() and CELLS.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time

sys.path.insert(0, "tools/audit/round9/D12/s2")
import numpy as np  # noqa: E402
import onoff_switch as ow  # noqa: E402

P_MAX = 6.0


def main():
    p_min = float(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else 6.0
    t0p, t0t = time.process_time(), time.thread_time()
    ratios, fracs, sp_bad = {}, {}, 0
    for name in ow.CELLS:
        built, opt, res = ow.solve(name, p_min)
        tot, off_kwh, frac, _n = ow.withheld(res)
        on = np.asarray(res.heat_pump_on_schedule, dtype=bool)
        act = float(on.sum() * P_MAX * ow.DT)
        ratios[name] = act / tot if tot > 1e-9 else float("nan")
        fracs[name] = frac
        sp = np.asarray(res.power_schedule, dtype=float)
        rooms = np.asarray(res.room_temp_trajectory[: len(sp)] if getattr(res, "room_temp_trajectory", None) is not None else np.zeros_like(sp), dtype=float)
        if len(rooms) < len(sp):
            rooms = np.pad(rooms, (0, len(sp) - len(rooms)), mode="edge")
        sps = opt._power_to_setpoints(sp, rooms, np.asarray(built["outdoor"], dtype=float))
        full = sp >= 0.99 * P_MAX
        bad = int(sum(1 for i in np.flatnonzero(full) if abs(sps[i] - opt.config.min_temp) < 1e-6))
        sp_bad += bad
        print(f"CELL cell={name} planned_kwh={tot:.2f} actuated_full_kwh={act:.2f} "
              f"net_ratio={ratios[name]:.3f} withheld_frac={frac:.3f} full_steps={int(full.sum())} "
              f"full_steps_setpoint_at_min={bad}")
    vals = sorted(v for v in ratios.values() if v == v)
    print(f"RESULT net_ratio_range={vals[0]:.3f}..{vals[-1]:.3f} ratio")
    print(f"RESULT cells_net_ratio_below_0_9={sum(1 for v in vals if v < 0.9)} cells")
    print(f"RESULT cells_withheld_gt_0_10={sum(1 for v in fracs.values() if v > 0.10)} cells")
    print(f"RESULT shoulder_net_ratio={ratios['shoulder']:.3f} ratio")
    print(f"RESULT full_power_steps_setpoint_at_min={sp_bad} steps")
    proc, thr = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={proc / max(thr, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        sw = int([ln for ln in open("/proc/vmstat") if ln.startswith("pswpin ")][0].split()[1])
    except Exception:  # noqa: BLE001
        pass
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
