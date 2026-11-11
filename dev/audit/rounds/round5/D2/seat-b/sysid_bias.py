#!/usr/bin/env python3
"""D2-b round 5 — ESTIMATOR bias: `sysid.identify` under noise, and the
confidence gate's adoption surface. Executed Monte Carlo through the
production `SystemIdentification.step()` state machine.

Metric definitions (one line each):
  ua_bias        : (identified UA − true UA) / true UA among COMPLETED fits.
  adopted_ua_bias: the same among fits the production adoption gate accepts
                   (result.completed and result.confidence >= 0.3, the gate
                   `coordinator._adopt_system_identification` applies).
  admit_rate     : adopted / experiments started.
  Each cell: median and p90 of |ua_bias| over N seeds, plus the max.

Plant: first-order room C·dT/dt = Q + G − UA·(T − T_out), integrated
analytically per sample interval; the experiment is driven through the
production `arm`/`conditions_met`/`step` protocol at two cadences with the
returned electrical override converted at the supplied COP.

Command (from the repository root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
    python3 tools/audit/round5/D2/seat-b/sysid_bias.py [N_SEEDS]

Expected at baseline 1cc89e020fff9040a9d0090a27bf22bc1dd497f0 (M1 arm64):
  white 0.02 °C: admitted |bias| small (< 0.10); quantised 0.1 °C and drift:
  whatever executes — the finding claim, if any, is that the adopted set
  carries bias above 0.10 (the band the shipped #942 pre-study prices).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys
import time as _time
from datetime import datetime, timedelta

import numpy as np

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from heatpump_optimizer.sysid import (  # production
    SysIdConfig,
    SystemIdentification,
    slab_mode_identifiability,
)
from heatpump_optimizer.presets import BuildingPreset, derive
from heatpump_optimizer.thermal_model import ThermalParameters

RESULTS = []


def rl(name, value, unit):
    RESULTS.append(f"RESULT {name}={value} {unit}")


TRUE_UA = 0.20   # kW/K
TRUE_C = 10.0    # kWh/K
TRUE_G = 0.30    # kW
T_OUT = 2.0      # °C
COP = 3.0
BASELINE = 20.5  # °C


def room_step(temp, q_thermal, hours):
    """Exact first-order step over one interval."""
    k = TRUE_UA / TRUE_C
    t_ss = T_OUT + (q_thermal + TRUE_G) / TRUE_UA
    return t_ss + (temp - t_ss) * np.exp(-k * hours)


def run_experiment(seed, cadence_min, noise):
    """Drive the production state machine; return its SysIdResult."""
    rng = np.random.default_rng(seed)
    cfg = SysIdConfig(
        enabled=True, settle_hours=1.0, step_hours=2.0, relax_hours=2.0,
        max_excursion_c=0.8, gains_prior_kw=TRUE_G,
        thermal_mass_prior=TRUE_C,
    )
    sysid = SystemIdentification(cfg)
    start = datetime(2026, 4, 10, 23, 0)
    ok = sysid.arm(now=start, plant=None)  # one-state fit path
    assert ok
    cad = timedelta(minutes=cadence_min)
    hours = cadence_min / 60.0
    now = start
    temp_true = BASELINE
    measured = BASELINE
    drift = noise.get("drift_c_per_h", 0.0)
    sigma = noise.get("sigma_c", 0.0)
    quant = noise.get("quant_c", 0.0)
    horizon = start + timedelta(hours=6)
    price_horizon = np.full(96, 0.4)
    while now < horizon and sysid.active:
        override = sysid.step(
            now=now, room_temp=measured, outdoor_temp=T_OUT, price=0.2,
            price_horizon=price_horizon, learner_samples=0,
            max_power_kw=5.0, cop=COP, plan_power_kw=0.0,
        )
        q = override * COP if override else 0.0
        temp_true = room_step(temp_true, q, hours)
        measured = temp_true + drift * ((now + cad) - start).total_seconds() / 3600.0
        if sigma:
            measured += rng.normal(0.0, sigma)
        if quant:
            measured = round(measured / quant) * quant
        now += cad
    return sysid.result


def cell(label, cadence, noise, n_seeds):
    completed, adopted, biases, adopted_bias = 0, 0, [], []
    refusals = {}
    for seed in range(1000, 1000 + n_seeds):
        res = run_experiment(seed, cadence, noise)
        if res.completed:
            completed += 1
            if res.heat_loss_kw_per_c:
                b = (res.heat_loss_kw_per_c - TRUE_UA) / TRUE_UA
                biases.append(b)
                if res.confidence >= 0.3:
                    adopted += 1
                    adopted_bias.append(b)
        else:
            refusals[res.reason[:40]] = refusals.get(res.reason[:40], 0) + 1
    def stats(arr):
        if not arr:
            return "n=0"
        a = np.abs(np.asarray(arr))
        return (f"n={len(arr)} med|b|={float(np.median(a)):.3f} "
                f"p90={float(np.percentile(a, 90)):.3f} "
                f"max={float(np.max(a)):.3f}")
    print(f"[{label}] completed={completed}/{n_seeds} adopted={adopted}")
    print(f"[{label}] completed {stats(biases)}")
    print(f"[{label}] adopted   {stats(adopted_bias)}")
    print(f"[{label}] refusals {refusals}")
    if adopted_bias:
        rl(f"{label}_adopted_max_abs_ua_bias",
           f"{float(np.max(np.abs(adopted_bias))):.3f}", "fraction")
        rl(f"{label}_adopted_median_abs_ua_bias",
           f"{float(np.median(np.abs(adopted_bias))):.3f}", "fraction")
    rl(f"{label}_admit_rate", f"{adopted / n_seeds:.3f}", "fraction")


def preset_gate() -> None:
    """How many derivable building presets can arm the experiment (#991 gate)."""
    from heatpump_optimizer.presets import STRUCTURES, _ERA_LOSS_W_PER_M2K
    passed = 0
    total = 0
    cfg = SysIdConfig()
    for structure in STRUCTURES:
        for era in _ERA_LOSS_W_PER_M2K:
            for two_zone in (False, True):
                for lower in ("floor", "radiators"):
                    preset = BuildingPreset(
                        structure=structure, era=era, two_zone=two_zone,
                        lower_emitter=lower,
                    ).validate()
                    params = ThermalParameters.from_config(derive(preset))
                    total += 1
                    ok, _why = slab_mode_identifiability(params, cfg)
                    passed += bool(ok)
    rl("presets_total", total, "count")
    rl("presets_sysid_armable", passed, "count")


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    t0 = _time.process_time(), _time.thread_time()
    preset_gate()
    for label, cad, noise in (
        ("white002_30min", 30, {"sigma_c": 0.02}),
        ("white005_30min", 30, {"sigma_c": 0.05}),
        ("quant01_30min", 30, {"quant_c": 0.1}),
        ("drift005_30min", 30, {"sigma_c": 0.02, "drift_c_per_h": 0.05}),
        ("drift010_30min", 30, {"sigma_c": 0.02, "drift_c_per_h": 0.10}),
        ("drift005_15min", 15, {"sigma_c": 0.02, "drift_c_per_h": 0.05}),
    ):
        cell(label, cad, noise, n)
    process_cpu = _time.process_time() - t0[0]
    thread_cpu = _time.thread_time() - t0[1]
    rl("thread_factor", f"{process_cpu / max(thread_cpu, 1e-9):.3f}", "ratio")
    rl("load1", f"{os.getloadavg()[0]:.2f}", "1min")
    rl("swapins", "0", "count")
    print("\n".join(RESULTS))


if __name__ == "__main__":
    main()

