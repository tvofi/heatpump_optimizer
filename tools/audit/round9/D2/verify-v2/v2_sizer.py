#!/usr/bin/env python3
"""V2 (independent) re-measure of D2-s4-02: sysid step sized to the abort bound.

Metric (one line): per preset plant (stress.BUILDINGS via presets.derive, its own
max_electrical_power), the sizer's noiseless headroom  max_excursion_c - peak  (K),
where the step is SystemIdentification._size_step_power's and the room path is the
production sizer plant (sysid._held_state / _valve_drive) sampled at the coordinator
cadence; and the Monte-Carlo probability (4000 draws) that
SystemIdentification._over_excursion fires on at least one noisy reading of that
path (baseline reading noisy too), for white sigma {0.01, 0.02, 0.05} degC and a
0.1 degC-quantised sensor, at cadence {0.5 h (the default interval), 0.25 h}.
Count key: the production _over_excursion verdict on each reading.
Hooks: sysid:SystemIdentification._size_step_power, _over_excursion, sysid:_held_state, _valve_drive.
Perturbation: --perturb margin (step x 0.85, the finder's): abort probability must fall.
Null control: sigma 0 -> probability 0.
Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/verify-v2/v2_sizer.py [--perturb margin]
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; box G3-V2 (4-core linux, py3.14.0rc2). Seeded, exact.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
from profiles import house  # noqa: E402
from stress import BUILDINGS  # noqa: E402
from heatpump_optimizer import presets, sysid as S  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

t0p, t0t = time.process_time(), time.thread_time()
MARGIN = "margin" in sys.argv
COP, OUT, BASE = 3.0, 0.0, 21.0


def params(name):
    cfg = house(two_zone=False, dhw=False)
    d = presets.derive(BUILDINGS[name])
    d.pop("heating_response_hours", None)
    cfg.update(d)
    p = ThermalParameters.from_config(cfg)
    p.two_zone_enabled = False
    return p


def path(p, q_th, cad):
    """Noiseless room excursion at each reading: 1 h settle at hold, 2 h step, 2 h relax."""
    m = S._sizing_model(p.heat_loss_coefficient, p.room_thermal_mass, p.internal_gains,
                        p.slab_thermal_mass, p.slab_heat_transfer)
    st = S._held_state(m, BASE, OUT)
    ex = [0.0]
    hold = max(p.heat_loss_coefficient * (BASE - OUT) - p.internal_gains, 0.0)
    for q, hours in ((hold, 1.0), (q_th, 2.0), (0.0, 2.0)):
        for _ in range(int(round(hours / cad))):
            sub = 12
            for _ in range(sub):
                st = S._valve_drive(m, st, q, OUT, cad / sub)
            ex.append(st.upper_floor_temperature - BASE)
    return np.array(ex)


rng = np.random.default_rng(424242)
worst_margin = 1.0
tot = {}
for name in BUILDINGS:
    p = params(name)
    sid = S.SystemIdentification(S.SysIdConfig(enabled=True))
    q_el = sid._size_step_power(float(p.max_electrical_power), COP, BASE, OUT,
                                float(p.heat_loss_coefficient), float(p.room_thermal_mass),
                                float(p.internal_gains), float(p.slab_thermal_mass),
                                float(p.slab_heat_transfer))
    if q_el is None:
        print(f"# {name}: sizer refused")
        continue
    if MARGIN:
        q_el *= 0.85
    peak, _ = S._predict_step_excursion_plant(p.heat_loss_coefficient, p.room_thermal_mass,
                                              p.internal_gains, BASE, OUT, q_el * COP, 2.0, 2.0,
                                              slab_thermal_mass=p.slab_thermal_mass,
                                              slab_heat_transfer=p.slab_heat_transfer)
    margin = sid.config.max_excursion_c - peak
    worst_margin = min(worst_margin, margin)
    at_max = abs(q_el - float(p.max_electrical_power)) < 1e-9
    print(f"RESULT {name}_step_kw={q_el:.3f} (plant max {p.max_electrical_power:.2f}, at_max={at_max})")
    print(f"RESULT {name}_noiseless_headroom={margin:.4f} K")
    for cad in (0.5, 0.25):
        ex = path(p, q_el * COP, cad)
        for arm in ("s0", "s0.01", "s0.02", "s0.05", "quant0.1"):
            n = 1 if arm == "s0" else 4000
            ab = 0
            for _ in range(n):
                if arm.startswith("s") and arm != "s0":
                    sg = float(arm[1:])
                    rd = BASE + ex + rng.normal(0.0, sg, ex.size)
                elif arm == "quant0.1":
                    rd = np.round((BASE + ex + rng.normal(0.0, 0.005, ex.size)) / 0.1) * 0.1
                else:
                    rd = BASE + ex
                sid._baseline_temp = float(rd[0])
                ab += any(sid._over_excursion(float(r)) for r in rd[1:])
            pr = ab / n
            tot.setdefault(arm, []).append(pr)
            print(f"RESULT {name}_cad{cad}_{arm}_abort_prob={pr:.4f}")
for arm, v in tot.items():
    print(f"RESULT all_{arm}_abort_prob_mean={np.mean(v):.4f} (cells {len(v)}, max {max(v):.4f})")
print(f"RESULT worst_noiseless_headroom={worst_margin:.4f} K")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / max(tc, 1e-9):.4f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = next(int(ln.split()[1]) for ln in open("/proc/vmstat") if ln.startswith("pswpin"))
except Exception:
    sw = -1
print(f"RESULT swapins={sw}")
