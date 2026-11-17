"""D2.M5 learner-clamps: the house heat-loss and COP learners at zero evidence
and on their clamps, through the production update arithmetic and the
production clamp seams.

Each learner is iterated exactly as the coordinator iterates it per accepted
interval: the heat-loss scale by thermal_model.learner_newton_step (trust
region coordinator._LEARNER_TRUST_REGION, alpha coordinator.HOUSE_LOSS_ALPHA)
and then HeatPumpOptimizerCoordinator._apply_house_heat_loss_scale; the COP
scale by flow_meter.cop_evidence, the EWMA/step bound of
_fold_cop_evidence (COP_LEARNING_ALPHA, COP_LEARNING_MAX_STEP) and then
HeatPumpOptimizerCoordinator._apply_cop_scale. The evidence is synthetic and
exact: the residual a true plant at scale s_true produces against the model at
the learner's current scale (first-order: e = -(u_true - u_now) dT dt / C), and
the electrical draw a true COP at cop_true gives for the commanded heat.

Metric definitions (one line each):
  zero_drift     = |scale after 2000 zero-evidence intervals - start|        (identity: 0)
  clamp_overrun  = max(scale) - clamp max (and clamp min - min(scale)) while the
                   truth sits past the clamp for 2000 intervals              (identity: <= 0)
  windup_steps   = intervals to come within 2 % of a truth inside the band after
                   2000 intervals pinned at the clamp, minus the same from a fresh
                   learner started at the clamp value                         (identity: 0)
Run:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D2/s3/m5_learners.py
Perturbation: --perturb-noclamp makes both _apply_* seams skip the clip:
  clamp_overrun must go up.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine B6 (shared).
"""
import _common  # noqa: F401
from _common import footer, np

import argparse
import sys
from types import SimpleNamespace

sys.path.insert(0, "custom_components")
import harness  # noqa: F401,E402
import heatpump_optimizer.coordinator as cm  # noqa: E402
from heatpump_optimizer import const, flow_meter  # noqa: E402
from heatpump_optimizer.thermal_model import learner_newton_step  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--perturb-noclamp", action="store_true")
A = ap.parse_args()

cm._publish_params = lambda coord, /, **f: None  # the seam's write, not its arithmetic
if A.perturb_noclamp:
    cm.np = SimpleNamespace(**{k: getattr(np, k) for k in dir(np) if not k.startswith("__")})
    cm.np.clip = lambda v, lo, hi: v

BASE_U, CAP, DT, DT_H = 0.2, 10.0, 20.0, 0.5


class Holder:
    pass


def loss_run(start, truths, n_each):
    h = Holder()
    h._house_heat_loss_scale = start
    trace = []
    for s_true in truths:
        for _ in range(n_each):
            cur = h._house_heat_loss_scale
            e = -(BASE_U * s_true - BASE_U * cur) * DT * DT_H / CAP
            step = learner_newton_step(cur, BASE_U, CAP, e, DT, DT_H,
                                       trust_region=cm._LEARNER_TRUST_REGION, alpha=cm.HOUSE_LOSS_ALPHA)
            if step is not None:
                cm.HeatPumpOptimizerCoordinator._apply_house_heat_loss_scale(h, step[1])
            trace.append(h._house_heat_loss_scale)
    return np.array(trace)


def cop_run(start, truths, n_each):
    h = Holder()
    h._cop_scale = start
    trace = []
    nameplate = 3.0
    for c_true in truths:
        for _ in range(n_each):
            modelled = nameplate * h._cop_scale
            commanded = 2.0
            heat = commanded * modelled  # the plan's intended heat
            electrical = heat / (nameplate * c_true)
            _obs, target = flow_meter.cop_evidence(modelled, commanded, electrical, None, h._cop_scale)
            new = (1 - cm.COP_LEARNING_ALPHA) * h._cop_scale + cm.COP_LEARNING_ALPHA * target
            ms = h._cop_scale * cm.COP_LEARNING_MAX_STEP
            new = float(np.clip(new, h._cop_scale - ms, h._cop_scale + ms))
            cm.HeatPumpOptimizerCoordinator._apply_cop_scale(h, new)
            trace.append(h._cop_scale)
    return np.array(trace)


def steps_to(trace, target, tol=0.02):
    hit = np.flatnonzero(np.abs(trace / target - 1.0) <= tol)
    return int(hit[0]) + 1 if hit.size else len(trace) + 1


rows = {}
# zero evidence
z_loss = loss_run(1.0, [1.0], 2000)
z_cop = cop_run(1.0, [1.0], 2000)
print(f"CELL learner-clamps evidence=zero heat_loss_drift={abs(z_loss[-1] - 1.0):.3e} cop_drift={abs(z_cop[-1] - 1.0):.3e}")
rows["zero_drift_max"] = max(abs(z_loss[-1] - 1.0), abs(z_cop[-1] - 1.0))
# on the clamp: truth past each end, then back inside
lo_l, hi_l = const.HOUSE_HEAT_LOSS_SCALE_MIN, const.HOUSE_HEAT_LOSS_SCALE_MAX
lo_c, hi_c = const.COP_SCALE_MIN, const.COP_SCALE_MAX
over, wind = 0.0, 0
details = []
for name, run, lo, hi, past_hi, past_lo, inside in (
        ("heat_loss", loss_run, lo_l, hi_l, hi_l * 1.5, lo_l * 0.5, 1.0),
        ("cop", cop_run, lo_c, hi_c, hi_c * 1.3, lo_c * 0.7, 1.0)):
    for end, past, clampv in (("max", past_hi, hi), ("min", past_lo, lo)):
        tr = run(1.0, [past, inside], 2000)
        pinned = tr[:2000]
        ov = float(np.max(pinned) - hi) if end == "max" else float(lo - np.min(pinned))
        back = steps_to(tr[2000:], inside)
        fresh = steps_to(run(clampv, [inside], 2000), inside)
        over = max(over, ov)
        wind = max(wind, back - fresh)
        details.append(f"{name}_{end}: reached={pinned[-1]:.4f} overrun={ov:+.3e} back={back} fresh={fresh}")
print(f"CELL learner-clamps evidence=on_clamp {' | '.join(details)}")
print(f"RESULT zero_drift_max={rows['zero_drift_max']:.3e} ratio")
print(f"RESULT clamp_overrun_max={over:.3e} ratio")
print(f"RESULT windup_steps_max={wind} count")
footer()
