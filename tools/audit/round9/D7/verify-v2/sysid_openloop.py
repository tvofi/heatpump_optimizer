#!/usr/bin/env python3
"""D7 verify-v2 for D7-s2-01: discretization bias of the production slab rollout, open loop.

Metric (one line): UA bias (fitted/true - 1) of a least-squares fit of the
PRODUCTION rollout sysid:_simulate_slab_path (UA, C_r, G free; slab pair given,
exactly as identify_slab frees them) to a noise-free room series whose truth is
the SAME candidate family (sysid's own ThermalParameters construction) at the
preset's true values, integrated with N sub-steps per 30-min sample; the
experiment is an open-loop power step (6 h hold, 8 h +step, 8 h hold), not the
state machine, so neither the step sizer nor the adoption gate is involved.

Per preset (tests/stress.py BUILDINGS light_new, heavy_old, typical_slab via
presets.derive), per truth sub-steps in (1, 30): the fit with the production
0.5 h rollout, and the same fit with the rollout at dt/30 (arrays repeated).
RESULT presets_bias_gt5pct_native = presets whose native-rollout fit on the
30-substep truth is off by >5 %; null control: the 1-substep truth (fit and
truth share the discretization) must give ~0; perturbation: the fine rollout
must give ~0 on the 30-substep truth. Counts/ratios, contention-immune.

Run (repository root):
    PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D7/verify-v2/sysid_openloop.py
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, cloud container linux. Writes nothing.
"""
from __future__ import annotations
import os
for _p in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_p, "1")
import sys, time  # noqa: E402
sys.path.insert(0, ".")
sys.path.insert(0, "tests")
import numpy as np  # noqa: E402
from scipy.optimize import least_squares  # noqa: E402
from custom_components.heatpump_optimizer import sysid as S  # noqa: E402
from custom_components.heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402
from custom_components.heatpump_optimizer.presets import BuildingPreset, derive  # noqa: E402
from profiles import house  # noqa: E402
from stress import BUILDINGS  # noqa: E402

DT = 0.5
OUT = 0.0
ROOM0 = 21.0


def truth_params(b):
    cfg = house(two_zone=False, dhw=False)
    cfg.update({k: v for k, v in derive(BuildingPreset(**{**vars(BUILDINGS[b]), "two_zone": False})).items()
                if k != "heating_response_hours"})
    p = ThermalParameters.from_config(cfg)
    return (p.heat_loss_coefficient * p.house_heat_loss_scale, p.room_thermal_mass,
            p.internal_gains, p.slab_thermal_mass, p.slab_heat_transfer)


def experiment(ua, cr, g, cs, ks):
    hold = max(ua * (ROOM0 - OUT) - g, 0.0)
    step = 0.35 * hold + 0.5
    q = np.array([hold] * 12 + [hold + step] * 16 + [hold] * 16)
    return q, np.full(len(q), OUT), np.full(len(q), DT)


def roll(x, pair, q, out, dt, n):
    ua, cr, g = np.exp(x[0]), np.exp(x[1]), x[2]
    r = S._simulate_slab_path(ua, cr, g, pair[0], pair[1], ROOM0,
                              np.repeat(out, n), np.repeat(q, n), np.repeat(dt, n) / n)
    return r[::n]


def main() -> int:
    c0, t0 = time.process_time(), time.thread_time()
    gt5 = 0
    null_max = fine_max = 0.0
    for b in ("light_new", "heavy_old", "typical_slab"):
        ua, cr, g, cs, ks = truth_params(b)
        q, out, dt = experiment(ua, cr, g, cs, ks)
        xt = np.array([np.log(ua), np.log(cr), g])
        for sub in (1, 30):
            rooms = roll(xt, (cs, ks), q, out, dt, sub)
            for rn in (1, 30):
                best = None
                for m in (1 / 3, 1.0, 3.0):
                    x0 = np.array([np.log(ua * 1.3), np.log(cr * m), g])
                    r = least_squares(lambda x: roll(x, (cs, ks), q, out, dt, rn) - rooms,
                                      x0, max_nfev=400)
                    if best is None or r.cost < best.cost:
                        best = r
                bias = float(np.exp(best.x[0]) / ua - 1)
                print(f"RESULT ua_bias_{b}_truth{sub}_rollout{rn}={bias:+.5f} ratio  # rms={np.sqrt(2*best.cost/len(rooms)):.2e}")
                if sub == 30 and rn == 1 and abs(bias) > 0.05:
                    gt5 += 1
                if sub == 1 and rn == 1:
                    null_max = max(null_max, abs(bias))
                if sub == 30 and rn == 30:
                    fine_max = max(fine_max, abs(bias))
    print(f"RESULT presets_bias_gt5pct_native={gt5} count  # of 3")
    print(f"RESULT null_truth1_max_abs_bias={null_max:.5f} ratio")
    print(f"RESULT perturb_fine_rollout_max_abs_bias={fine_max:.5f} ratio")
    c1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={(c1-c0)/max(t1-t0,1e-9):.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
