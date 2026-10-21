"""Reseed study (R10): which production seams see the reseed at all.

A reseed sets the configured nameplate to the learned value and the learned
multiplier to 1.0. Arm A = (nameplate U, L; scale s; ratio r). Arm B = the
reseed (U*s, L*r*s; 1.0; 1.0). Effective UA is identical by construction, so
every seam that reads only the product is unmoved; this harness executes each
seam on both arms and prints the relative difference.

Metric (one line): |value_B / value_A - 1| per seam, at the owner-shaped
learned state s=1.567, r=1.922 (Health tab, 2026-10-14) on the stock two-zone
test house (tests/profiles.py:house(two_zone=True)) -- no private data.

Command (repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/study-reseed/reparam_sites.py
Expected: model rollout, optimizer-facing view and sysid prior ~0 (<1e-9);
    _space_demand_kw and sysid adoption base != 0 (they read the raw lower
    nameplate without the ratio); options-edit reseed of the lower zone
    double-applies the ratio (lower effective = r x learned).
Baseline SHA: 17f1c55fa. Machine: macOS arm64, Python 3.11.

Instrumented symbols:
    heatpump_optimizer.thermal_model:ThermalModel.simulate_step
    heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._space_demand_kw
    heatpump_optimizer.coordinator:_effective_house_heat_loss
    heatpump_optimizer.sysid:adoption_decision, sysid:_zone_heat_loss
    heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_load_thermal_learning
        (+ _reanchor_house_heat_loss_scale), ._apply_learner_payloads
    heatpump_optimizer.thermal_model:learner_newton_step (trust region)
Perturbation: --ratio 1.0 -- with no learned lower-zone split every
    ratio-dependent seam (space demand, sysid base, lower double-apply) must
    fall to 0 difference; the trust-region seam keeps moving with s.
Null control: --scale 1.0 --ratio 1.0 (prior already right): every row 0.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import asyncio  # noqa: E402
import copy  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from dataclasses import replace  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass  # noqa: E402
from profiles import house  # noqa: E402

from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer import sysid  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState, learner_newton_step  # noqa: E402


class MemStore:
    """In-memory stand-in for homeassistant.helpers.storage.Store."""

    def __init__(self, data=None):
        self.data = copy.deepcopy(data)

    async def async_load(self):
        return copy.deepcopy(self.data)

    async def async_save(self, data):
        self.data = copy.deepcopy(data)

    async def async_wait_for_read(self):
        return None


def coordinator(cfg, store=None):
    c = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
    c._thermal_learning_store = store or MemStore({})
    return c


def rel(a, b):
    return abs(b / a - 1.0) if abs(a) > 1e-15 else abs(b - a)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=float, default=1.567)
    ap.add_argument("--ratio", type=float, default=1.922)
    a = ap.parse_args()
    s, r = a.scale, a.ratio
    c0, t0 = time.process_time(), time.thread_time()
    cfg = house(two_zone=True, dhw=False)
    cfg["lower_floor_temp_entity"] = "sensor.lower_floor"
    U, L = cfg["upper_floor_heat_loss"], cfg["lower_floor_heat_loss"]
    cfg_b = dict(cfg, upper_floor_heat_loss=U * s, lower_floor_heat_loss=L * r * s)
    print(f"scale={s} ratio={r} U={U} L={L}")

    # --- 1. the model rollout (what plans and forecasts are made from) ---
    pa = ThermalParameters.from_config(cfg)
    pa.house_heat_loss_scale, pa.lower_floor_loss_ratio = s, r
    pb = ThermalParameters.from_config(cfg_b)
    ma, mb = ThermalModel(pa), ThermalModel(pb)
    st_a = st_b = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=-5.0,
                               upper_floor_temperature=21.0, lower_floor_temperature=20.5)
    worst = 0.0
    rng = np.random.default_rng(1)
    for k in range(192):
        pw = float(rng.uniform(0, 6))
        st_a = ma.simulate_step(st_a, pw, -5.0 + 3 * np.sin(k / 15), dt_hours=0.25)
        st_b = mb.simulate_step(st_b, pw, -5.0 + 3 * np.sin(k / 15), dt_hours=0.25)
        worst = max(worst, abs(st_a.upper_floor_temperature - st_b.upper_floor_temperature),
                    abs(st_a.lower_floor_temperature - st_b.lower_floor_temperature))
    print(f"RESULT model_rollout_48h_max_abs_diff_c={worst:.3e}")

    # --- 2. the published effective UA (Health tab's W/K) ---
    ea = coord_mod._effective_house_heat_loss(pa, s)
    eb = coord_mod._effective_house_heat_loss(pb, 1.0)
    print(f"RESULT effective_ua_rel_diff={rel(ea, eb):.3e}  (A {ea * 1000:.1f} W/K, B {eb * 1000:.1f} W/K)")

    # --- 3. coordinator._space_demand_kw (feeds the pump-demand path) ---
    ca, cb = coordinator(cfg), coordinator(cfg_b)
    ca._thermal_params, cb._thermal_params = pa, pb
    for c in (ca, cb):
        c._current_state = replace(st_a, room_temperature=21.0, outdoor_temperature=-5.0)
    da, db = ca._space_demand_kw(), cb._space_demand_kw()
    true_ua = (U + L * r) * s
    print(f"RESULT space_demand_rel_diff={rel(da, db):.4f}  (A {da:.3f} kW, B {db:.3f} kW, "
          f"model-consistent {true_ua * 26:.3f} kW)")

    # --- 4. sysid: the experiment's prior and its adoption base ---
    prior_a = sysid._zone_heat_loss(pa) * pa.house_heat_loss_scale
    prior_b = sysid._zone_heat_loss(pb) * pb.house_heat_loss_scale
    print(f"RESULT sysid_prior_ua_rel_diff={rel(prior_a, prior_b):.4f}  "
          f"(A {prior_a * 1000:.1f}, B {prior_b * 1000:.1f}, model {true_ua * 1000:.1f} W/K)")
    fitted = true_ua  # an experiment that measured the model's own UA exactly
    res = sysid.SysIdResult(completed=True, heat_loss_kw_per_c=fitted,
                            ua_profile_halfwidth=0.0, ua_prior_halfwidth=0.0, ua_told_halfwidth=0.0)
    dec_a = sysid.adoption_decision(res, pa, sysid.SysIdConfig())
    dec_b = sysid.adoption_decision(res, pb, sysid.SysIdConfig())
    # Adopted at full weight, the coordinator sets scale := decision.scale.
    after_a = (U + L * r) * dec_a.scale
    after_b = (pb.upper_floor_heat_loss + pb.lower_floor_heat_loss * 1.0) * dec_b.scale
    print(f"RESULT sysid_adopt_effective_rel_err_A={rel(fitted, after_a):.4f}  "
          f"(adopted {after_a * 1000:.1f} W/K for a fit of {fitted * 1000:.1f}; reason {dec_a.reason})")
    print(f"RESULT sysid_adopt_effective_rel_err_B={rel(fitted, after_b):.4f}  "
          f"(adopted {after_b * 1000:.1f} W/K; reason {dec_b.reason})")

    # --- 5. the learner step: trust region is absolute in multiplier units ---
    cap, dT, dt = pa.upper_floor_thermal_mass, 26.0, 0.25
    for resid in (0.02, 0.1, 0.3):
        ta = learner_newton_step(s, U, cap, resid, dT, dt, trust_region=coord_mod._LEARNER_TRUST_REGION,
                                 alpha=coord_mod.HOUSE_LOSS_ALPHA)
        tb = learner_newton_step(1.0, U * s, cap, resid, dT, dt, trust_region=coord_mod._LEARNER_TRUST_REGION,
                                 alpha=coord_mod.HOUSE_LOSS_ALPHA)
        step_a = (ta[1] - s) * U
        step_b = (tb[1] - 1.0) * U * s
        print(f"RESULT newton_step_ua_ratio_B_over_A_resid{resid}={step_b / step_a:.4f}  "
              f"(A {step_a * 1000:.3f} W/K, B {step_b * 1000:.3f} W/K per sample)")

    # --- 6. reseed through the OPTIONS path: reload over the learned store ---
    src = coordinator(cfg)
    src._thermal_params = pa
    src._apply_house_heat_loss_scale(s)
    src._apply_lower_floor_loss_ratio(r)
    src._house_heat_loss_samples, src._lower_floor_loss_samples = 310, 147
    asyncio.run(src._async_save_thermal_learning())
    stored = src._thermal_learning_store.data
    learned_house = (U + L * r) * s
    learned_lower = L * r * s
    for label, ccfg in (("options_reseed_both_zones", cfg_b),
                        ("options_reseed_upper_only", dict(cfg, upper_floor_heat_loss=U * s, lower_floor_heat_loss=L * s))):
        dst = coordinator(ccfg, MemStore(stored))
        asyncio.run(dst._async_load_thermal_learning())
        p = dst._thermal_params
        eh = (p.upper_floor_heat_loss + p.lower_floor_heat_loss * dst._lower_floor_loss_ratio) * dst._house_heat_loss_scale
        el = p.lower_floor_heat_loss * dst._lower_floor_loss_ratio * dst._house_heat_loss_scale
        eu = p.upper_floor_heat_loss * dst._house_heat_loss_scale
        print(f"RESULT {label}.house_rel_err={rel(learned_house, eh):.4f}  ({eh * 1000:.1f} vs learned {learned_house * 1000:.1f} W/K)")
        print(f"RESULT {label}.upper_rel_err={rel(U * s, eu):.4f}  ({eu * 1000:.1f} vs learned {U * s * 1000:.1f} W/K)")
        print(f"RESULT {label}.lower_rel_err={rel(learned_lower, el):.4f}  ({el * 1000:.1f} vs learned {learned_lower * 1000:.1f} W/K; "
              f"scale {dst._house_heat_loss_scale:.3f} ratio {dst._lower_floor_loss_ratio:.3f} samples {dst._house_heat_loss_samples}/{dst._lower_floor_loss_samples})")

    # --- 7. a pre-reseed snapshot restored onto the reseeded configuration ---
    snap = {"thermal_learning": copy.deepcopy(stored)}
    dst = coordinator(cfg_b, MemStore(stored))
    asyncio.run(dst._async_load_thermal_learning())
    # reseed fully applied in memory (multipliers back to 1.0), then restore
    dst._apply_house_heat_loss_scale(1.0)
    dst._apply_lower_floor_loss_ratio(1.0)
    dst._apply_learner_payloads(snap)
    p = dst._thermal_params
    eh = (p.upper_floor_heat_loss + p.lower_floor_heat_loss * dst._lower_floor_loss_ratio) * dst._house_heat_loss_scale
    el = p.lower_floor_heat_loss * dst._lower_floor_loss_ratio * dst._house_heat_loss_scale
    print(f"RESULT snapshot_restore_after_reseed.house_rel_err={rel(learned_house, eh):.4f}  ({eh * 1000:.1f} W/K)")
    print(f"RESULT snapshot_restore_after_reseed.lower_rel_err={rel(learned_lower, el):.4f}  ({el * 1000:.1f} W/K)")

    # single-zone: the options path is already a clean reseed
    cfg1 = house(two_zone=False, dhw=False)
    h1 = cfg1.get("house_heat_loss_coefficient") or ThermalParameters.from_config(cfg1).heat_loss_coefficient
    s1 = coordinator(cfg1)
    s1._apply_house_heat_loss_scale(s)
    s1._house_heat_loss_samples = 310
    asyncio.run(s1._async_save_thermal_learning())
    d1 = coordinator(dict(cfg1, house_heat_loss_coefficient=h1 * s), MemStore(s1._thermal_learning_store.data))
    asyncio.run(d1._async_load_thermal_learning())
    e1 = d1._thermal_params.heat_loss_coefficient * d1._house_heat_loss_scale
    print(f"RESULT options_reseed_single_zone.house_rel_err={rel(h1 * s, e1):.4f}  "
          f"(scale {d1._house_heat_loss_scale:.4f}, samples kept {d1._house_heat_loss_samples}, "
          f"phi {coord_mod.house_loss_confidence(d1._house_heat_loss_samples):.4f})")

    tf = (time.process_time() - c0) / max(time.thread_time() - t0, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=n/a(macOS)")


if __name__ == "__main__":
    main()
