"""D2-s4 (round 9, D2.M5): the sysid adoption gate against the UA bias it admits.

Metric: over draws of the production step experiment (SystemIdentification.arm/step
-> _finish -> identify_slab) on a two-state preset plant, the share of fits that
sysid.adoption_decision ADMITS whose fitted UA is off the true UA by more than the
gate's own +-10 % bar (UA_ADOPTION_HALFWIDTH_BAR), per noise cell. A 95 % interval
gate should hold that share at or under ~5 %. Count key: the UA the production
fit delivers (SysIdResult.heat_loss_kw_per_c) against the plant's true UA, and the
admit flag the production gate returns -- never an input attribute.

Command (from the export root):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/s4/gate_bias.py [--seeds N] [--cells a,b] [--perturb drift_col]

Cells: noise kind x preset x cadence. Noise kinds: white (sigma degC), quant (0.1 degC
rounding + 0.005 white), drift (linear sensor ramp degC/h + 0.005 white), gains
(true free heat differs from the configured prior by +dG kW, 0.005 white).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: box B6 (4 CPU cloud container).
Expected: see REPORT.md in this directory (counts are exact per seed set; tolerance exact).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
import argparse
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "custom_components")
sys.path.insert(0, "tests")
import numpy as np  # noqa: E402

from heatpump_optimizer import presets, sysid as S  # noqa: E402
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState,
)
from profiles import house  # noqa: E402
from stress import BUILDINGS  # noqa: E402

NOW = datetime(2026, 1, 15, 23, 0, tzinfo=timezone.utc)
COP = 3.0
MAX_KW = 3.5
SEED0 = 20260926


def plant(name):
    cfg = house(two_zone=False, dhw=False)
    d = presets.derive(BUILDINGS[name])
    d.pop("heating_response_hours", None)
    cfg.update(d)
    p = ThermalParameters.from_config(cfg)
    p.two_zone_enabled = False
    return p


def drive(params, seed, kind, level, dt_h, max_kw=MAX_KW):
    """Run the production state machine on the true plant; returns (sid, result, ua_true)."""
    rng = np.random.default_rng(seed)
    ua_true = params.heat_loss_coefficient * params.house_heat_loss_scale
    prior_g = float(params.internal_gains)
    true_g = prior_g + (level if kind == "gains" else 0.0)
    truth = ThermalParameters(**{**params.__dict__})
    truth.internal_gains = true_g
    model = ThermalModel(truth)
    sid = S.SystemIdentification(S.SysIdConfig(
        enabled=True, min_days_between_runs=0.0,
        gains_prior_kw=prior_g, thermal_mass_prior=float(params.room_thermal_mass)))
    assert sid.arm(NOW, plant=params)
    outdoor = 0.0
    ks = max(float(params.slab_heat_transfer), 1e-9)
    hold = max(ua_true * (21.0 - outdoor) - true_g, 0.0)
    state = ThermalState(room_temperature=21.0, slab_temperature=21.0 + hold / ks,
                         outdoor_temperature=outdoor)
    prices = np.full(48, 1.0)
    when = NOW
    t = 0.0
    for _ in range(int(5.0 / dt_h) + 4):
        white = 0.005 if kind in ("quant", "drift", "gains") else level
        reading = state.room_temperature + rng.normal(0.0, white)
        if kind == "drift":
            reading += level * t
        if kind == "quant":
            reading = round(reading / level) * level
        override = sid.step(
            now=when, room_temp=reading, outdoor_temp=outdoor, price=0.1,
            price_horizon=prices, learner_samples=0, max_power_kw=max_kw, cop=COP,
            plan_power_kw=hold / COP, house_ua=ua_true,
            house_capacity=float(params.room_thermal_mass), house_gains=prior_g,
            house_slab_mass=float(params.slab_thermal_mass),
            house_slab_transfer=float(params.slab_heat_transfer))
        if not sid.active:
            break
        elec = hold / COP if override is None else float(override)
        state = model.simulate_step(state, electrical_power=0.0, outdoor_temp=outdoor,
                                    dt_hours=dt_h, external_heat_kw=elec * COP)
        when += timedelta(hours=dt_h)
        t += dt_h
    return sid, sid.result, ua_true


CELLS = {
    "white001": ("white", 0.01), "white002": ("white", 0.02), "white005": ("white", 0.05),
    "quant01": ("quant", 0.1), "quant005": ("quant", 0.05),
    "drift002": ("drift", 0.02), "drift005": ("drift", 0.05), "drift010": ("drift", 0.10),
    "gains+02": ("gains", 0.2), "gains+04": ("gains", 0.4), "gains-02": ("gains", -0.2),
    "null": ("white", 0.0),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=12)
    ap.add_argument("--cells", default=",".join(CELLS))
    ap.add_argument("--presets", default="light_new,typical_slab,heavy_old")
    ap.add_argument("--dt", type=float, default=0.5)
    ap.add_argument("--perturb", default="")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    t0p, t0t = time.process_time(), time.thread_time()
    for cell in a.cells.split(","):
        kind, level = CELLS[cell]
        for pname in a.presets.split(","):
            p = plant(pname)
            n = done = admit = admit_bad = 0
            biases, adm_b, adm_w, reasons = [], [], [], {}
            for k in range(a.seeds if level else 1):
                sid, res, ua = drive(p, SEED0 + k, kind, level, a.dt)
                n += 1
                if not res.completed:
                    reasons[res.reason[:30]] = reasons.get(res.reason[:30], 0) + 1
                    continue
                done += 1
                b = (res.heat_loss_kw_per_c - ua) / ua
                biases.append(b)
                dec = S.adoption_decision(res, p, sid.config)
                if dec.admit:
                    admit += 1
                    adm_b.append(b)
                    # the blended scale's error when the learner stood at the truth
                    adm_w.append(dec.weight * b)
                    if a.verbose:
                        print(f"#   admit seed={k} bias={b*100:+.2f}% weight={dec.weight:.3f} "
                              f"hw_profile={res.ua_profile_halfwidth:.4f} hw_prior={res.ua_prior_halfwidth:.4f}")
                    if abs(b) > float(np.expm1(S.UA_ADOPTION_HALFWIDTH_BAR)):
                        admit_bad += 1
                else:
                    reasons[dec.reason[:30]] = reasons.get(dec.reason[:30], 0) + 1
            tag = f"{cell}_{pname}_dt{a.dt}"
            print(f"RESULT {tag}_n={n} count")
            print(f"RESULT {tag}_admitted={admit} count")
            print(f"RESULT {tag}_admitted_over_bar={admit_bad} count")
            if adm_b:
                print(f"RESULT {tag}_admitted_bias_median={np.median(adm_b)*100:+.2f} %")
                print(f"RESULT {tag}_admitted_absbias_max={np.max(np.abs(adm_b))*100:.2f} %")
                print(f"RESULT {tag}_adopted_scale_abserr_max={np.max(np.abs(adm_w))*100:.2f} %")
            if biases:
                print(f"RESULT {tag}_completed_bias_median={np.median(biases)*100:+.2f} %")
            print(f"# {tag} refusals {reasons}", flush=True)
    pc, tc = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "na"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
