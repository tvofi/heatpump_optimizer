#!/usr/bin/env python3
"""The heat-loss learners' step on an install's own stores, reseeded or not (#2252).

Written by the R10-TRUST-RELATIVE fixer. STUDY R10-RESEED found the learner's
trust region fixed in multiplier units: a saturated step is ``base_u *
trust_region`` in UA, so it grows with learned/prior, and moving the learned
value into the settings (a reseed) changed nothing but the step size. This
drives the production step (``thermal_model.learner_newton_step``, the
coordinator's own constants, the ``_apply_*`` bounds) on the configuration
and learned state of a diagnostics bundle, per learner, in paired arms on one
noise stream:

  * ``as_is``    -- base = the configured nameplate, current = the learned value;
  * ``reseeded`` -- base = nameplate x learned, current = 1.0 (settings match
    the learned values: the forward-carried null control);
  * ``zero_evidence`` -- current = 1.0 and the truth is the nameplate (an
    install with no evidence);
  * ``at_min`` / ``at_max`` -- current on the ``_apply_*`` clamp, truth there.

The plant is the learner's own linear relation: an interval's residual is
``(U_cur - U_true) * dT * dt / C`` plus Gaussian sensor noise, so the learned
value is right (U_true = base x current) and every arm should hold it. Per
arm it prints the effective UA's std and RMSE against the truth (W/K) and the
one-step forecast MAE (degC, the |residual| the learner sees); per learner
the reseeded/as-is ratios. Expected: ratios exactly 1.0000 once the trust
region is relative; != 1 at a baseline whose trust region is fixed.
Perturbation: ``--trust-region 1e9`` (the study's) collapses the ratios to
1.0000 at either tree. Null control: ``--learned 1.0`` (prior already right)
reads ratios of 1.0000 at either tree.

The bundle is given on the command line and never committed (a user's
private data). Run from a worktree root, at the base and at the head:

    PYTHONPATH=tests/hastub:custom_components \\
        python3 dev/audit/harnesses/r10_trust_relative_bundle.py BUNDLE.json
"""
from __future__ import annotations

import argparse
import json

import numpy as np

from heatpump_optimizer import coordinator as coord_mod
from heatpump_optimizer.const import (
    HOUSE_HEAT_LOSS_SCALE_MAX,
    HOUSE_HEAT_LOSS_SCALE_MIN,
    LOWER_FLOOR_LOSS_RATIO_MAX,
    LOWER_FLOOR_LOSS_RATIO_MIN,
)
from heatpump_optimizer.thermal_model import ThermalParameters, learner_newton_step


def walk(base_u, capacity, current, truth_u, noise, delta_t, dt_h, bounds, trust_region):
    """The learner's walk on one noise stream; (UA path, |residual| path)."""
    ua, err = [], []
    for n in noise:
        resid = (base_u * current - truth_u) * delta_t * dt_h / capacity + n
        err.append(abs(resid))
        if abs(resid) <= coord_mod.HOUSE_LOSS_MAX_RESIDUAL:
            step = learner_newton_step(
                current, base_u, capacity, resid, delta_t, dt_h,
                trust_region=trust_region,
                alpha=coord_mod.HOUSE_LOSS_ALPHA,
            )
            if step is not None:
                current = float(np.clip(step[1], *bounds))
        ua.append(base_u * current)
    return np.asarray(ua), np.asarray(err)


def arms(name, base_u, capacity, learned, bounds, noise, a):
    truth = base_u * learned
    lo, hi = bounds
    spec = {
        "as_is": (base_u, learned, truth),
        "reseeded": (truth, 1.0, truth),
        "zero_evidence": (base_u, 1.0, base_u),
        "at_min": (base_u, lo, base_u * lo),
        "at_max": (base_u, hi, base_u * hi),
    }
    out = {}
    for arm, (b, cur, t) in spec.items():
        ua, err = walk(b, capacity, cur, t, noise, a.delta_t, a.dt_hours, bounds, a.trust_region)
        out[arm] = {
            "ua_std_w_per_k": float(np.std(ua)) * 1000.0,
            "ua_rmse_w_per_k": float(np.sqrt(np.mean((ua - t) ** 2))) * 1000.0,
            "fc_mae_c": float(np.mean(err)),
        }
        for k, v in out[arm].items():
            print(f"RESULT {name}.{arm}.{k}={v:.6f}")
    for k in ("ua_std_w_per_k", "ua_rmse_w_per_k", "fc_mae_c"):
        print(f"RESULT {name}.ratio_reseeded_over_as_is.{k}="
              f"{out['reseeded'][k] / out['as_is'][k]:.4f}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle")
    ap.add_argument("--samples", type=int, default=4000)
    ap.add_argument("--sigma", type=float, default=0.1, help="sensor noise, degC")
    ap.add_argument("--delta-t", type=float, default=20.0, help="indoor-outdoor, K")
    ap.add_argument("--dt-hours", type=float, default=0.25)
    ap.add_argument("--seed", type=int, default=2252)
    ap.add_argument("--learned", type=float, default=None,
                    help="override both learned values (null control: 1.0)")
    ap.add_argument("--trust-region", type=float, default=coord_mod._LEARNER_TRUST_REGION)
    a = ap.parse_args()
    with open(a.bundle) as fh:
        data = json.load(fh)["data"]
    th = next(v for k, v in data["debug"]["stores"].items() if k.endswith("_thermal_learning"))
    s = float(th["house_heat_loss_scale"]) if a.learned is None else a.learned
    r = float(th["lower_floor_loss_ratio"]) if a.learned is None else a.learned
    p = ThermalParameters.from_config(dict(data["config"]))
    print(f"trust_region={a.trust_region} learned_scale={s:.4f} learned_ratio={r:.4f} "
          f"two_zone={p.two_zone_enabled} samples={a.samples} sigma={a.sigma}")
    rng = np.random.default_rng(a.seed)
    noise = rng.normal(0.0, a.sigma, a.samples)
    base_u, capacity = coord_mod._house_loss_terms(p)
    arms("house", base_u, capacity, s,
         (HOUSE_HEAT_LOSS_SCALE_MIN, HOUSE_HEAT_LOSS_SCALE_MAX), noise, a)
    if p.two_zone_enabled:
        arms("lower", p.lower_floor_heat_loss * s, p.lower_floor_thermal_mass, r,
             (LOWER_FLOOR_LOSS_RATIO_MIN, LOWER_FLOOR_LOSS_RATIO_MAX), noise, a)


if __name__ == "__main__":
    main()
