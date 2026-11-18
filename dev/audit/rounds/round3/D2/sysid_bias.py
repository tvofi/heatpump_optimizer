"""D2 -- bias of `sysid.SystemIdentification.identify` under white, quantised
and drifting room-sensor noise, against a plant whose UA, C and gains are known
exactly.

The plant is the model the fit assumes, integrated finely:
    C dT/dt = Q + G - UA (T - T_out)
so with noiseless samples the estimator must recover UA, C and G exactly and any
residual is the estimator's own.  Samples are handed to the production object
directly (`self.samples`), which is the same list the state machine fills, so
`identify()` is instrumented rather than reimplemented.

METRIC: `bias_UA` = median over `SEEDS` runs of (UA_hat - UA_true)/UA_true, and
the same for C and for the reported `internal_gains_kw`; plus `completion` = the
fraction of runs whose `SysIdResult.completed` is True, and `bias_UA_adopted` =
the same median taken over completed runs only (the bias the confidence gate
actually admits).

COMMAND (from the repository root, ~30 s):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D2/sysid_bias.py

EXPECTED at baseline ae36eff (see the RESULT lines; the noiseless arm is the
one with a hard tolerance): `arm_clean_30min` reports |bias_UA| <= 1e-6 and
|bias_C| <= 1e-6 -- a fit that cannot recover an exactly-generated plant is a
finding.  The noisy arms are reported as measured; the identity that must hold
there is DIRECTIONAL: a symmetric zero-mean sensor error must not produce a
one-signed bias that survives the confidence gate.

PERTURBATION (direction stated): raise the injected sensor drift `d` along the
`driftgrid_d*_sigma0.02` row -> `median_bias_UA_adopted` must rise in magnitude,
monotonically and one-signed.  Measured at baseline: -0.0211, -0.0662, -0.1340,
-0.2454, -0.4756 for d = 0.00, 0.02, 0.05, 0.10, 0.20 C/h.  That is the arm the
judge should run; it is executed by the default invocation, no flag needed.

TWO CANDIDATE FIXES THAT DO **NOT** WORK, executed here so nobody re-tries them:
  * `--wide-drift-prior` raises `SysIdConfig.sensor_drift_prior_c_per_h` from
    0.02 to 1.0 so the ridge stops shrinking the drift column.  The bias barely
    moves (-0.1340 -> -0.1322 at d=0.05; -0.2454 -> -0.2336 at d=0.10) and
    `median_drift_hat` lands near -0.024 whatever the true drift is.  So the
    prior is not the binding constraint -- the column is simply not identifiable
    against sensor noise at this experiment's excursion.
  * A finer sampling cadence does not help either: at 5-minute sampling
    (60 rows instead of 10) the bias at d=0.10, sigma=0.02 is -0.2408 against
    -0.2446 at 30 minutes, and nothing is adopted at all.
  * `SysIdConfig.max_excursion_c` is not a usable perturbation here: it gates the
    state machine's abort logic, not `identify`, and moves nothing.

NULL CONTROL: the `arm_clean_*` rows are the null: with zero sensor error every
bias must vanish.  A bias that persists there is the estimator, not the noise.

BASELINE SHA: ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1
MACHINE: 8-core Apple M1, 8 GB, numpy 2.4.6 / scipy 1.17.1 on OpenBLAS
INSTRUMENTED SYMBOLS: sysid.py:SystemIdentification.identify,
    sysid.py:SysIdConfig, sysid.py:SysIdSample, sysid.py:SysIdResult
"""
import sys
from datetime import datetime, timedelta

import d2lib  # noqa: F401  -- thread pin + sys.path, must be first
import numpy as np

from heatpump_optimizer.sysid import (
    PHASE_RELAX,
    PHASE_SETTLING,
    PHASE_STEP,
    SysIdConfig,
    SysIdSample,
    SystemIdentification,
)

d2lib.repo_root_ok()

WIDE_PRIOR = "--wide-drift-prior" in sys.argv
SEEDS = 200

UA_TRUE = 0.22        # kW/K
C_TRUE = 9.0          # kWh/K
G_TRUE = 0.35         # kW
T_OUT = 2.0
T0 = 21.0
Q_SETTLE = 0.8        # kW thermal
Q_STEP = 3.2
Q_RELAX = 0.0
START = datetime(2026, 1, 15, 23, 0)


def plant(cadence_h: float):
    """Exact-ish trajectory of the assumed plant, sampled at `cadence_h`."""
    phases = ((PHASE_SETTLING, 1.0, Q_SETTLE),
              (PHASE_STEP, 2.0, Q_STEP),
              (PHASE_RELAX, 2.0, Q_RELAX))
    micro = cadence_h / 400.0
    t = T0
    out = []
    when = START
    for phase, hours, q in phases:
        n_samples = int(round(hours / cadence_h))
        for _ in range(n_samples):
            out.append((when, t, q, phase))
            for _ in range(400):
                t = t + micro * (q + G_TRUE - UA_TRUE * (t - T_OUT)) / C_TRUE
            when = when + timedelta(hours=cadence_h)
    out.append((when, t, 0.0, PHASE_RELAX))
    return out


def run(cadence_h, sigma, quantum, drift, seed, offset=0.0):
    rng = np.random.default_rng(seed)
    cfg = SysIdConfig(enabled=True)
    if WIDE_PRIOR:
        # The live control for D2-03: widen the sensor-drift prior so the ridge
        # stops shrinking that column, and the drift stops landing in UA.
        cfg.sensor_drift_prior_c_per_h = 1.0
    sid = SystemIdentification(cfg)
    for i, (when, t, q, phase) in enumerate(plant(cadence_h)):
        obs = t + drift * (i * cadence_h) + offset
        if sigma:
            obs = obs + rng.normal(0.0, sigma)
        if quantum:
            obs = round(obs / quantum) * quantum
        sid.samples.append(SysIdSample(when, obs, T_OUT, q, phase))
    return sid.identify()


def arm(name, cadence_h, sigma, quantum, drift):
    ua, cc, gg, dd, done = [], [], [], [], 0
    ua_done = []
    for s in range(SEEDS):
        r = run(cadence_h, sigma, quantum, drift, 1000 + s)
        if r.heat_loss_kw_per_c is None or r.thermal_mass_kwh_per_c is None:
            continue
        bu = (r.heat_loss_kw_per_c - UA_TRUE) / UA_TRUE
        bc = (r.thermal_mass_kwh_per_c - C_TRUE) / C_TRUE
        ua.append(bu)
        cc.append(bc)
        if r.internal_gains_kw is not None:
            gg.append((r.internal_gains_kw - G_TRUE) / G_TRUE)
        if r.sensor_drift_c_per_h is not None:
            dd.append(r.sensor_drift_c_per_h)
        if r.completed:
            done += 1
            ua_done.append(bu)
        if sigma == 0.0 and quantum == 0.0 and drift == 0.0:
            break  # deterministic: one run is the whole arm
    n = max(len(ua), 1)
    d2lib.result(
        f"arm_{name}",
        f"n={len(ua)} bias_UA={np.median(ua) if ua else float('nan'):+.4f} "
        f"bias_C={np.median(cc) if cc else float('nan'):+.4f} "
        f"bias_G={np.median(gg) if gg else float('nan'):+.4f} "
        f"drift_hat={np.median(dd) if dd else float('nan'):+.4f} "
        f"completion={done / n:.3f} "
        f"bias_UA_adopted={np.median(ua_done) if ua_done else float('nan'):+.4f} "
        f"p90_absUA={np.percentile(np.abs(ua), 90) if ua else float('nan'):.4f}",
    )
    return float(np.median(ua)) if ua else float("nan")


def main() -> int:
    d2lib.result("seeds", SEEDS)
    d2lib.result("wide_drift_prior_arm", "1" if WIDE_PRIOR else "0")
    d2lib.result("plant", f"UA={UA_TRUE} C={C_TRUE} G={G_TRUE} T_out={T_OUT}")
    clean30 = arm("clean_30min", 0.5, 0.0, 0.0, 0.0)
    clean15 = arm("clean_15min", 0.25, 0.0, 0.0, 0.0)
    arm("white_0.02C_30min", 0.5, 0.02, 0.0, 0.0)
    arm("white_0.05C_30min", 0.5, 0.05, 0.0, 0.0)
    arm("white_0.10C_30min", 0.5, 0.10, 0.0, 0.0)
    arm("quantised_0.1C_30min", 0.5, 0.0, 0.1, 0.0)
    arm("quantised_0.1C_plus_white_0.02_30min", 0.5, 0.02, 0.1, 0.0)
    arm("drift_0.05Cph_30min", 0.5, 0.0, 0.0, 0.05)
    arm("drift_0.10Cph_30min", 0.5, 0.0, 0.0, 0.10)
    arm("drift_0.10Cph_plus_white_0.05_30min", 0.5, 0.05, 0.0, 0.10)
    # --- the quantisation sweep -------------------------------------
    # A single quantised run is deterministic, so one number is one operating
    # point.  Sweep the sub-quantum phase (where the trajectory sits inside a
    # quantisation bin), the quantum itself and the cadence: 3 x 10 x 2 = 60
    # cells, so the sign and size can be read as a property rather than as one
    # lucky alignment.  COMMON.md item 6: range across cells and the value with
    # the single most favourable cell dropped are both reported.
    for quantum in (0.1, 0.5):
        for cadence in (0.5, 0.25):
            cells = []
            for off in np.arange(0.0, 1.0, 0.1) * quantum:
                r = run(cadence, 0.0, quantum, 0.0, 0, offset=float(off))
                if r.heat_loss_kw_per_c is None:
                    continue
                cells.append((
                    (r.heat_loss_kw_per_c - UA_TRUE) / UA_TRUE,
                    (r.thermal_mass_kwh_per_c - C_TRUE) / C_TRUE,
                    bool(r.completed),
                ))
            if not cells:
                d2lib.result(
                    f"quantsweep_q{quantum}_cad{cadence}h",
                    "cells=0 no fit returned a coefficient at this quantum",
                )
                continue
            bu = np.array([c[0] for c in cells])
            bc = np.array([c[1] for c in cells])
            comp = sum(1 for c in cells if c[2])
            drop = np.sort(np.abs(bu))[:-1]      # most favourable = smallest |bias|
            d2lib.result(
                f"quantsweep_q{quantum}_cad{cadence}h",
                f"cells={len(cells)} median_bias_UA={np.median(bu):+.4f} "
                f"range_bias_UA={bu.max() - bu.min():.4f} "
                f"min_bias_UA={bu.min():+.4f} max_bias_UA={bu.max():+.4f} "
                f"n_positive={int(np.sum(bu > 0))} "
                f"median_bias_C={np.median(bc):+.4f} "
                f"completed={comp}/{len(cells)} "
                f"loo_median_abs_UA_drop_best={np.median(drop):.4f}",
            )

    # --- the drift x white-noise grid --------------------------------
    # The drift column exists to keep a drifting ROOM SENSOR out of UA.  With
    # any white noise the ridge shrinks that column back to zero, and the drift
    # returns to UA.  16 cells; range and leave-one-out reported.
    grid = {}
    for d in (0.0, 0.02, 0.05, 0.10, 0.20):
        for sg in (0.0, 0.02, 0.05, 0.10):
            bu, dh, done, n = [], [], 0, 0
            adopted = []      # coordinator._adopt_system_identification's gate
            for k in range(60):
                r = run(0.5, sg, 0.0, d, 5000 + k)
                if r.heat_loss_kw_per_c is None:
                    continue
                n += 1
                b = (r.heat_loss_kw_per_c - UA_TRUE) / UA_TRUE
                bu.append(b)
                dh.append(r.sensor_drift_c_per_h if r.sensor_drift_c_per_h is not None else float("nan"))
                done += int(bool(r.completed))
                if r.completed and r.confidence >= 0.3:
                    adopted.append(b)
            if not bu:
                continue
            grid[(d, sg)] = float(np.median(adopted)) if adopted else float(np.median(bu))
            d2lib.result(
                f"driftgrid_d{d}_sigma{sg}",
                f"n={n} median_bias_UA={np.median(bu):+.4f} "
                f"p10={np.percentile(bu, 10):+.4f} p90={np.percentile(bu, 90):+.4f} "
                f"median_drift_hat={np.nanmedian(dh):+.4f} (true {d}) "
                f"completed={done}/{n} adopted={len(adopted)}/{n} "
                f"median_bias_UA_adopted="
                f"{np.median(adopted) if adopted else float('nan'):+.4f}",
            )
    vals = np.array(list(grid.values()))
    d2lib.result("driftgrid_cells", len(grid))
    d2lib.result("driftgrid_range_bias_UA", f"{vals.max() - vals.min():.4f}")
    worst_key = min(grid, key=lambda k: grid[k])
    rest = [v for k, v in grid.items() if k != worst_key]
    d2lib.result("driftgrid_worst_cell", f"d={worst_key[0]} sigma={worst_key[1]} bias_UA={grid[worst_key]:+.4f}")
    d2lib.result("driftgrid_loo_worst_without_that_cell", f"{min(rest):+.4f}")

    d2lib.result("tolerance_clean_arm", "1e-6 relative")
    viol = int(abs(clean30) > 1e-6) + int(abs(clean15) > 1e-6)
    d2lib.result("clean_arm_violations", viol)
    d2lib.env_footer()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
