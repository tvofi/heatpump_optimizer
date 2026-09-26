"""D12 verify-v3 (round 9), own harness for D12-s2-03: every production
p_norm formula (the finding's seam_rule lists them) evaluated on one
full-power step and one idle step, per compressor kind.

Metric (one line): full_power_bottomed = number of production seams that map
a full-power step (P = max_electrical_power) to the BOTTOM of their output
range (p_norm <= 0.01, i.e. the same output an idle step gets), per arm.
Seams: get_current_action (published band + power_normalized),
_power_to_setpoints (published optimal_setpoints), _power_to_displace_schedule
(ECL110 displace, an actuation seam), _zone_setpoints (two-zone setpoints).
Second metric: power_normalized published for an idle step (P = 0).

Arms: modulating (min 1.0, max 6.0 kW; null control) and onoff (min == max == 6.0 kW).
Perturbation --guard: the onoff arm's min_electrical_power becomes 5.0 kW (a
1 kW range, the finder's --min 5.0 config perturbation, applied here to all
four seams at once); onoff full_power_bottomed must fall to 0.

Run:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D12/verify-v3/pnorm_seams.py [--guard]
Expected: modulating 0 seams; onoff 4 seams bottomed, idle power_normalized -60.0; --guard onoff 0. Exact.
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence 6f51db2c).
Machine: G2-V3 cloud container, 4 vCPU, CPython 3.14.0rc2, numpy/OpenBLAS.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys
import time
from datetime import datetime, timedelta, timezone

import numpy as np

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from heatpump_optimizer import optimizer as O  # noqa: E402
from heatpump_optimizer import thermal_model as T  # noqa: E402

GUARD = "--guard" in sys.argv


def build(pmin, pmax, two_zone=True):
    params = T.ThermalParameters()
    params.min_electrical_power = pmin
    params.max_electrical_power = pmax
    params.two_zone_enabled = two_zone
    cfg = O.OptimizationConfig()
    return O.HeatPumpOptimizer(T.ThermalModel(params), cfg), params, cfg


def seams(opt, params, cfg, p):
    out = {}
    t0 = datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc)
    ts = [t0 + timedelta(minutes=15 * i) for i in range(2)]
    power = np.array([p, p])
    import dataclasses
    res = O.OptimizationResult.__new__(O.OptimizationResult)
    for f in dataclasses.fields(O.OptimizationResult):
        if f.default is not dataclasses.MISSING:
            setattr(res, f.name, f.default)
        elif f.default_factory is not dataclasses.MISSING:
            setattr(res, f.name, f.default_factory())
        else:
            setattr(res, f.name, [0.0, 0.0])  # required series: zeros; overwritten below where it matters
    res.timestamps = ts
    res.power_schedule = list(power)
    res.dhw_power_schedule = [0.0, 0.0]
    res.heat_pump_on_schedule = [p > 0.05] * 2
    res.optimal_setpoints = [21.0, 21.0]
    res.displace_schedule = [0.0, 0.0]
    res.room_temp_trajectory = [21.0, 21.0, 21.0]
    res.slab_temp_trajectory = [22.0, 22.0, 22.0]
    try:
        act = opt.get_current_action(res, t0 + timedelta(minutes=1))
        out["get_current_action"] = float(act.get("power_normalized"))
        out["_action_label"] = act.get("action") or act.get("band") or act.get("state")
    except Exception as exc:  # noqa: BLE001
        out["get_current_action"] = f"ERR {exc!r}"[:120]
    sp = opt._power_to_setpoints(power, np.array([21.0, 21.0]), np.array([-3.0, -3.0]))
    out["_power_to_setpoints"] = (sp[0] - cfg.min_temp) / max(cfg.max_temp - cfg.min_temp, 1e-9)
    ds = opt._power_to_displace_schedule(power, np.array([-3.0, -3.0]))
    # displace has additive biases; compare against the idle step's output instead
    out["_power_to_displace_schedule_raw"] = ds[0]
    zu, _zl = opt._zone_setpoints(power)
    out["_zone_setpoints"] = (zu[0] - cfg.min_temp) / max(cfg.max_temp - cfg.min_temp, 1e-9) if zu else None
    return out


def arm(name, pmin, pmax):
    if GUARD and pmin == pmax:
        pmin = 5.0
    opt, params, cfg = build(pmin, pmax)
    full = seams(opt, params, cfg, pmax)
    idle = seams(opt, params, cfg, 0.0)
    bottomed = 0
    for key in ("get_current_action", "_power_to_setpoints", "_zone_setpoints"):
        v = full.get(key)
        if isinstance(v, float) and v <= 0.01:
            bottomed += 1
    # displace: full power must be strictly above the idle step's displace
    if full["_power_to_displace_schedule_raw"] <= idle["_power_to_displace_schedule_raw"] + 1e-9:
        bottomed += 1
    print(f"ARM {name} min={pmin} max={pmax}")
    print(f"  full-power step: {full}")
    print(f"  idle step:       {idle}")
    print(f"RESULT {name}_full_power_bottomed={bottomed} seams")
    print(f"RESULT {name}_idle_power_normalized={idle['get_current_action']} ratio")
    return bottomed


def main():
    t0, tt0 = time.process_time(), time.thread_time()
    arm("modulating", 1.0, 6.0)
    arm("onoff", 6.0, 6.0)
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
