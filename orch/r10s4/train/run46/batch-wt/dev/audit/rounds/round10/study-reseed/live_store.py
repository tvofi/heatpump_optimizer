"""Reseed study (R10): what a reseed would and would not change on a real install.

Reads a diagnostics bundle given ON THE COMMAND LINE (never commit one: it is
a user's private data) and prints, from data.debug.stores and data.config:

  * the effective heat-loss trajectory the snapshot ring recorded (weekly),
    as anchor x scale, its week-on-week steps and Spearman trend;
  * how much of each learned value is still the starting prior, from the
    learner's own constant: (1 - alpha) ** samples (house_loss_confidence);
  * the reseed identity on THIS install's configuration: a 48-h rollout of
    the model at (nameplate, s, r) against (nameplate*s, ..., 1, 1), and the
    two seams that read the raw lower-zone nameplate without the ratio;
  * the recorded one-step temperature MAE / bias of the accuracy tracker.

Metric (one line): |delta| between arm A (as is) and arm B (prior := learned)
on each production seam, at the install's learned state; and the effective
UA's weekly path in W/K.
Command (repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/study-reseed/live_store.py /path/to/diag.json
Expected: rollout delta 0; prior residual share < 1 % (house), ~5 % (lower);
    space-demand and sysid-adoption seams off by (U+L*r)/(U+L) - 1.
Baseline SHA: 17f1c55fa. Machine: macOS arm64, Python 3.11.
Instrumented symbols: thermal_model:ThermalModel.simulate_step,
    coordinator:house_loss_confidence, coordinator:HeatPumpOptimizerCoordinator._space_demand_kw,
    sysid:adoption_decision.
Perturbation: --ratio-override 1.0 -- the ratio-dependent seam deltas fall to 0.
Null control: --scale-override 1.0 --ratio-override 1.0 -- every delta 0.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from dataclasses import replace  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass  # noqa: E402

from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer import sysid  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402


def spearman(x):
    x = np.asarray(x, float)
    if len(x) < 3:
        return float("nan")
    rk = np.argsort(np.argsort(x))
    return float(np.corrcoef(rk, np.arange(len(x)))[0, 1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle")
    ap.add_argument("--scale-override", type=float, default=None)
    ap.add_argument("--ratio-override", type=float, default=None)
    a = ap.parse_args()
    c0, t0 = time.process_time(), time.thread_time()
    with open(a.bundle) as fh:
        d = json.load(fh)
    data = d["data"]
    stores = data["debug"]["stores"]
    pick = lambda suffix: next(v for k, v in stores.items() if k.endswith(suffix))  # noqa: E731
    th = pick("_thermal_learning")
    cfg = dict(data["config"])
    s = a.scale_override if a.scale_override is not None else float(th["house_heat_loss_scale"])
    r = a.ratio_override if a.ratio_override is not None else float(th["lower_floor_loss_ratio"])

    # --- the weekly path the snapshot ring kept ---
    snaps = pick("_snapshots").get("snapshots", [])
    eff = []
    for sn in snaps:
        tl = (sn.get("learners") or {}).get("thermal_learning") or {}
        if tl.get("house_heat_loss_anchor") and tl.get("house_heat_loss_scale"):
            eff.append(float(tl["house_heat_loss_anchor"]) * float(tl["house_heat_loss_scale"]) * 1000.0)
    eff.append(float(th["house_heat_loss_anchor"]) * float(th["house_heat_loss_scale"]) * 1000.0)
    steps = np.diff(eff) / np.asarray(eff[:-1]) if len(eff) > 1 else np.array([])
    print("effective UA path (W/K, snapshots then now): " + ", ".join(f"{v:.1f}" for v in eff))
    print(f"RESULT live_ua_path_points={len(eff)}")
    print(f"RESULT live_ua_first_to_now_ratio={eff[-1] / eff[0]:.3f}")
    print(f"RESULT live_ua_weekly_step_mean_pct={100 * float(np.mean(steps)):.1f}")
    print(f"RESULT live_ua_weekly_step_min_pct={100 * float(np.min(steps)):.1f}")
    print(f"RESULT live_ua_trend_spearman={spearman(eff):.3f}")

    # --- how much of each learned value is still the prior ---
    n_h, n_l = int(th["house_heat_loss_samples"]), int(th["lower_floor_loss_samples"])
    print(f"RESULT prior_residual_share_house={1 - coord_mod.house_loss_confidence(n_h):.4f}  (n={n_h})")
    print(f"RESULT prior_residual_share_lower={1 - coord_mod.house_loss_confidence(n_l):.4f}  (n={n_l}, same alpha)")
    n_cop = int(th.get("cop_samples") or 0)
    print(f"RESULT prior_residual_share_cop={(1 - coord_mod.COP_LEARNING_ALPHA) ** n_cop:.4f}  (n={n_cop})")

    # --- the reseed on this install's own configuration ---
    pa = ThermalParameters.from_config(cfg)
    pa.house_heat_loss_scale, pa.lower_floor_loss_ratio = s, r
    pb = ThermalParameters.from_config(cfg)
    pb.heat_loss_coefficient *= s
    if pb.two_zone_enabled:
        pb.upper_floor_heat_loss *= s
        pb.lower_floor_heat_loss *= s * r
    ma, mb = ThermalModel(pa), ThermalModel(pb)
    st = ThermalState(room_temperature=20.5, slab_temperature=22.0, outdoor_temperature=0.0,
                      upper_floor_temperature=20.5, lower_floor_temperature=20.0)
    sa = sb = st
    worst = 0.0
    rng = np.random.default_rng(7)
    for k in range(192):
        pw = float(rng.uniform(0, 5))
        sa = ma.simulate_step(sa, pw, 2.0 * np.sin(k / 12), dt_hours=0.25)
        sb = mb.simulate_step(sb, pw, 2.0 * np.sin(k / 12), dt_hours=0.25)
        worst = max(worst, abs(sa.upper_floor_temperature - sb.upper_floor_temperature),
                    abs(sa.room_temperature - sb.room_temperature))
    print(f"RESULT live_reseed_rollout_max_abs_diff_c={worst:.3e}")
    if pa.two_zone_enabled:
        ca = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
        ca._thermal_params = pa
        ca._current_state = replace(st, room_temperature=20.5, outdoor_temperature=0.0)
        model_ua = (pa.upper_floor_heat_loss + pa.lower_floor_heat_loss * r) * s
        dem = ca._space_demand_kw()
        print(f"RESULT live_space_demand_rel_err={abs(dem / (model_ua * 20.5) - 1):.4f}  "
              f"({dem:.3f} kW vs model {model_ua * 20.5:.3f} kW)")
        res = sysid.SysIdResult(completed=True, heat_loss_kw_per_c=model_ua, ua_profile_halfwidth=0.0,
                                ua_prior_halfwidth=0.0, ua_told_halfwidth=0.0)
        dec = sysid.adoption_decision(res, pa, sysid.SysIdConfig())
        adopted = (pa.upper_floor_heat_loss + pa.lower_floor_heat_loss * r) * dec.scale
        print(f"RESULT live_sysid_adopt_rel_err={abs(adopted / model_ua - 1):.4f}  "
              f"(a perfect fit of {model_ua * 1000:.1f} W/K adopts as {adopted * 1000:.1f} W/K; {dec.reason})")

    acc = pick("_accuracy").get("accuracy", {})
    smp = [x for x in acc.get("samples", []) if x.get("predicted_temp") is not None and x.get("actual_temp") is not None]
    if smp:
        e = np.array([x["actual_temp"] - x["predicted_temp"] for x in smp])
        print(f"RESULT live_onestep_mae_c={float(np.mean(np.abs(e))):.3f}  (n={len(e)}; a reseed leaves every"
              f" prediction bit-identical, see live_reseed_rollout_max_abs_diff_c)")
        print(f"RESULT live_onestep_bias_c={float(np.mean(e)):.3f}")
    tf = (time.process_time() - c0) / max(time.thread_time() - t0, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=n/a(macOS)")


if __name__ == "__main__":
    main()
