#!/usr/bin/env python3
"""D3-s2 round 9, step D3.M4: for each pre-screen survivor, does the mutant behave differently at all?

Metric: per mutant id, the number of probe inputs (of N) on which the production symbol's output
  under the one-line mutant differs from the unmutated original (`diverge=<k>/<N>`), over (a) the
  domain the integration can reach (config-flow ranges, a stored payload's own shape) and, where
  the mutant is only reachable outside it, (b) the out-of-domain probe as the positive control.
  k=0 over (a) means an equivalent mutant (a non-finding); k>0 with no suite driver red is a gap.
Command:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D3/s2/witness.py [M01 ...]
Expected: per-mutant RESULT lines as recorded in REPORT.md (counts, exact).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B2 (4-CPU Linux container).
Instrumented symbols: named per probe below (module:symbol), loaded twice by mutload.pair():
  the real module, and the same source with pool.json's mutant line applied in memory.
Perturbation: the mutant line itself (mutant vs original arm); removing it sends diverge to 0.
Key: the value the production symbol returns / the state it leaves, never an input attribute.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mutload  # noqa: E402
import numpy as np  # noqa: E402

PROBES = {}


def probe(fn):
    PROBES[fn.__name__.upper()] = fn
    return fn


def _same(a, b) -> bool:
    try:
        return bool(np.array_equal(np.asarray(a, dtype=object), np.asarray(b, dtype=object)))
    except Exception:  # noqa: BLE001
        return a == b


@probe
def m01():
    """optimizer:classify_space_steps with n_steps == 0 (the guarded case)."""
    o, m, _ = mutload.pair("M01")
    rng = np.random.default_rng(1)
    n = 0
    for k in range(50):
        L = int(rng.integers(0, 8))
        args = (rng.random(L), rng.random(L) if k % 2 else np.array([]), rng.random(L) + 20,
                rng.random(L) + 19, rng.random(L), None, 0)
        n += not _same(o.classify_space_steps(*args), m.classify_space_steps(*args))
    return {"diverge_in_domain": (n, 50)}


def _opt(module, buffer_max):
    import golden
    spec = golden.make(two_zone=True, dhw=False, config_overrides={
        "mixing_valve_mode": "manual", "buffer_tank_volume": 750.0,
        "buffer_max_temperature": buffer_max})
    real = spec["optimizer"]
    return module.HeatPumpOptimizer(real.model, real.config)


@probe
def m02():
    """optimizer:HeatPumpOptimizer._buffer_charge_ceiling; config flow bounds buffer_max_temperature 40..90."""
    o, m, _ = mutload.pair("M02")
    ind, outd = 0, 0
    grid_in = [(bm, t) for bm in range(40, 91, 5) for t in (-25.0, -10.0, 0.0, 10.0)]
    for bm, t in grid_in:
        ind += not _same(_opt(o, bm)._buffer_charge_ceiling(t), _opt(m, bm)._buffer_charge_ceiling(t))
    grid_out = [(bm, t) for bm in (25, 30) for t in (-25.0, -10.0, 0.0, 10.0)]
    vals = []
    for bm, t in grid_out:
        a, b = _opt(o, bm)._buffer_charge_ceiling(t), _opt(m, bm)._buffer_charge_ceiling(t)
        outd += not _same(a, b)
        vals.append((bm, t, round(a, 2), round(b, 2)))
    return {"diverge_in_domain": (ind, len(grid_in)), "diverge_out_of_domain": (outd, len(grid_out)),
            "_out": vals}


_SOLVED = {}


def _solved(two_zone=False, dhw=False, state_overrides=None):
    key = (two_zone, dhw, tuple(sorted((state_overrides or {}).items())))
    if key not in _SOLVED:
        import golden
        spec = golden.make(two_zone=two_zone, dhw=dhw, state_overrides=state_overrides)
        opt = spec["optimizer"]
        res = opt.optimize(spec["state"], spec["prices"], spec["outdoor"], spec["wind"],
                           spec["rain"], spec["solar"], golden.START)
        _SOLVED[key] = (spec, opt, res)
    return _SOLVED[key]


@probe
def m03():
    """optimizer:HeatPumpOptimizer._safety_release_steps, single zone (the BOOLOP's only new arm):
    a solved plan, random forced-off pin blocks, comfort floors swept so breaches exist."""
    o, m, _ = mutload.pair("M03")
    rng = np.random.default_rng(3)
    n_div, n, nonempty = 0, 0, 0
    for st in ({}, {"upper_floor_temperature": 15.0}, {"upper_floor_temperature": 30.0}):
        spec, real, res = _solved(False, False, st)
        steps = len(res.power_schedule)
        a, b = o.HeatPumpOptimizer(real.model, real.config), m.HeatPumpOptimizer(real.model, real.config)
        for k in range(20):
            pins = np.full(steps, np.nan)
            s0 = int(rng.integers(0, steps - 8))
            pins[s0:s0 + int(rng.integers(2, 8))] = 0.0
            floor = np.full(steps, float(np.min(res.room_temp_trajectory)) + rng.uniform(-0.2, 0.6))
            n += 1
            ra = a._safety_release_steps(res, floor, pins, None)
            nonempty += bool(ra[0])
            n_div += not _same(ra, b._safety_release_steps(res, floor, pins, None))
    return {"diverge_in_domain": (n_div, n), "releasing_probes": (nonempty, n)}


@probe
def m04():
    """optimizer:cycling_penalty_batch; config flow bounds compressor_cycling_cost to 0..10 and the
    electrical rating to > 0. Out-of-domain control: a negative cost or a zero rating."""
    o, m, _ = mutload.pair("M04")
    rng = np.random.default_rng(4)
    ind = n_in = 0
    for cost in (0.0, 0.05, 0.5, 2.0, 10.0):
        for pm in (0.5, 3.0, 8.0):
            for cols in (1, 2, 96):
                mat = rng.random((4, cols)) * pm
                n_in += 1
                ind += not np.array_equal(o.cycling_penalty_batch(mat, cost, pm),
                                          m.cycling_penalty_batch(mat, cost, pm))
    outd = n_out = 0
    with np.errstate(all="ignore"):
        for cost, pm in ((-0.5, 3.0), (0.5, 0.0), (0.5, -1.0)):
            mat = rng.random((4, 96))
            n_out += 1
            outd += not np.array_equal(o.cycling_penalty_batch(mat, cost, pm),
                                       m.cycling_penalty_batch(mat, cost, pm), equal_nan=True)
    return {"diverge_in_domain": (ind, n_in), "diverge_out_of_domain": (outd, n_out)}


@probe
def m08():
    """thermal_model:ThermalModel.simulate_dhw_step (value and _step_dhw_floor_injected) on steps
    that hit the inlet floor; the planner's steps are 5..60 min. Control: dt_hours = 0."""
    o, m, _ = mutload.pair("M08")
    import golden
    params = golden.make(dhw=True)["optimizer"].model.params
    a, b = o.ThermalModel(params), m.ThermalModel(params)
    ind = n_in = floor_hits = 0
    for dt in (5 / 60, 0.25, 0.5, 1.0):
        for t0 in (5.0, 8.0, 10.0, 12.0, 40.0):
            for hr in (7.0, 19.0):
                va = a.simulate_dhw_step(t0, 0.0, hr, ambient_temp=15.0, dt_hours=dt, draw_power=20.0)
                vb = b.simulate_dhw_step(t0, 0.0, hr, ambient_temp=15.0, dt_hours=dt, draw_power=20.0)
                n_in += 1
                floor_hits += a._step_dhw_floor_injected > 0
                ind += not (va == vb and a._step_dhw_floor_injected == b._step_dhw_floor_injected)
    outd = 0
    try:
        va = a.simulate_dhw_step(8.0, 0.0, 7.0, ambient_temp=15.0, dt_hours=0.0, draw_power=20.0)
        vb = b.simulate_dhw_step(8.0, 0.0, 7.0, ambient_temp=15.0, dt_hours=0.0, draw_power=20.0)
        outd = int(not (va == vb and a._step_dhw_floor_injected == b._step_dhw_floor_injected))
    except ZeroDivisionError:
        outd = 1
    return {"diverge_in_domain": (ind, n_in), "floor_hit_probes": (floor_hits, n_in),
            "diverge_out_of_domain": (outd, 1)}


@probe
def m11():
    """tariff:PeakTracker._close_window retention (del ranked[max(2k, 6):] -> del ranked[2k:]):
    two weeks of hourly samples, per window compare billed_peak_kw and threshold_kw (what the
    optimizer and the bill read) and the persisted as_dict()['peaks'] (what the store keeps)."""
    o, m, _ = mutload.pair("M11")
    from datetime import datetime, timedelta
    rng = np.random.default_rng(11)
    billed = n = stored = 0
    for k in (1, 2, 3, 4, 5):
        for dd in (True, False):
            ta = o.CapacityTariff(enabled=True, price_per_kw=50.0, peaks_averaged=k, distinct_days=dd)
            tb = m.CapacityTariff(enabled=True, price_per_kw=50.0, peaks_averaged=k, distinct_days=dd)
            pa, pb = o.PeakTracker(), m.PeakTracker()
            t = datetime(2026, 1, 3, 0, 0)
            for h in range(24 * 14):
                kw = float(rng.gamma(2.0, 1.5))
                for q in range(4):
                    when = t + timedelta(minutes=15 * q)
                    pa.observe(when, kw, ta)
                    pb.observe(when, kw, tb)
                t += timedelta(hours=1)
                n += 1
                billed += not (pa.billed_peak_kw(ta) == pb.billed_peak_kw(tb)
                               and pa.threshold_kw(ta) == pb.threshold_kw(tb))
                stored += pa.as_dict()["peaks"] != pb.as_dict()["peaks"]
    return {"diverge_billed_or_threshold": (billed, n), "diverge_persisted_peaks": (stored, n)}


@probe
def m19():
    """price_model:extend_price_series when the published prices already cover the horizon
    (known_count >= n_steps, the guarded case), with no model and with a default model."""
    o, m, _ = mutload.pair("M19")
    from datetime import datetime, timedelta, timezone
    rng = np.random.default_rng(19)
    n_div = n = 0
    for model in (None, o.PriceShapeModel()):
        for _ in range(40):
            n_steps = int(rng.integers(0, 97))
            known = list(rng.random(n_steps + int(rng.integers(0, 20))) * 3 - 0.2)
            t0 = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=int(rng.integers(0, 400)))
            starts = [t0 + timedelta(minutes=15 * i) for i in range(n_steps)]
            a = o.extend_price_series(list(known), n_steps, starts, model)
            b = m.extend_price_series(list(known), n_steps, starts, model)
            n += 1
            n_div += not all(np.array_equal(x, y) for x, y in zip(a, b))
    return {"diverge_in_domain": (n_div, n)}


def _sid_samples(mod, rng, c=6.0, ua=0.12, g=0.5, noise=0.02):
    from datetime import datetime, timedelta, timezone
    out, temp, tout = [], 20.7, 0.0
    when = datetime(2026, 2, 10, 0, 0, tzinfo=timezone.utc)
    for phase, power, steps in ((mod.PHASE_STEP, 3.0, 12), (mod.PHASE_RELAX, 0.0, 19)):
        for _ in range(steps):
            out.append(mod.SysIdSample(when, temp + rng.normal(0, noise), tout, power, phase))
            temp += (1.0 / 6.0) * (power + g - ua * (temp - tout)) / c
            when += timedelta(minutes=10)
    return out


@probe
def m24():
    """sysid:SystemIdentification.identify with thermal_mass_prior over the config flow's
    RANGE_HOUSE_THERMAL_MASS (0.5..80 kWh/K, the coordinator passes room_thermal_mass);
    control: priors below the 0.1 floor."""
    o, m, _ = mutload.pair("M24")
    ind = n_in = done = 0
    for prior in (0.5, 1.0, 3.0, 6.0, 10.0, 40.0, 80.0):
        for seed in range(6):
            nz = (0.02, 0.05)[seed % 2]
            ra = o.SystemIdentification(o.SysIdConfig(enabled=True, thermal_mass_prior=prior, gains_prior_kw=0.4))
            rb = m.SystemIdentification(m.SysIdConfig(enabled=True, thermal_mass_prior=prior, gains_prior_kw=0.4))
            ra.samples = _sid_samples(o, np.random.default_rng(seed), noise=nz)
            rb.samples = _sid_samples(m, np.random.default_rng(seed), noise=nz)
            a, b = ra.identify(), rb.identify()
            n_in += 1
            done += bool(a.completed)
            ind += repr(a) != repr(b)
    outd = n_out = 0
    for prior in (0.05, 0.01):
        ra = o.SystemIdentification(o.SysIdConfig(enabled=True, thermal_mass_prior=prior, gains_prior_kw=0.4))
        rb = m.SystemIdentification(m.SysIdConfig(enabled=True, thermal_mass_prior=prior, gains_prior_kw=0.4))
        ra.samples = _sid_samples(o, np.random.default_rng(0), noise=0.05)
        rb.samples = _sid_samples(m, np.random.default_rng(0), noise=0.05)
        n_out += 1
        outd += repr(ra.identify()) != repr(rb.identify())
    return {"diverge_in_domain": (ind, n_in), "completed_fits": (done, n_in),
            "diverge_out_of_domain": (outd, n_out)}


M31_CORRUPT = [{"bias_k": "nan", "samples": 4}, {"bias_k": "inf", "samples": 4},
               {"bias_k": "-inf", "samples": 12}, {"bias_k": 3.0, "samples": -2},
               {"bias_k": -6.0, "samples": -1}, {"bias_k": float("nan"), "samples": 40}]


def _m31_cop(model, params, learner):
    """What the plan prices: ThermalModel.compute_cop on a direct plant whose curve bias the
    coordinator pushes from the restored learner (coordinator.py: params.flow_curve_bias)."""
    params.flow_curve_bias = learner.bias_k
    return float(model.compute_cop(-10.0))


@probe
def m31():
    """flow_lift:FlowCurveBias.from_dict, the store-boundary guard `not isfinite(bias) or
    samples < 0 -> inert`. In-domain: well-formed payloads (finite bias, samples >= 0) must not
    diverge. The guarded domain: corrupt payloads a Store can hand back (a 'nan'/'inf' string
    parses through float(); a negative count). Downstream: the COP the plan prices at -10 C,
    and the bias after one ordinary fold (observe(45, 40))."""
    o, m, _ = mutload.pair("M31")
    import copy
    import golden
    from heatpump_optimizer import thermal_model as tm
    rng = np.random.default_rng(31)
    ind = n_in = 0
    for _ in range(60):
        d = {"bias_k": float(rng.uniform(-40, 40)), "samples": int(rng.integers(0, 50))}
        a, b = o.FlowCurveBias.from_dict(dict(d)), m.FlowCurveBias.from_dict(dict(d))
        n_in += 1
        ind += (a.bias_k, a.samples) != (b.bias_k, b.samples)
    base = golden.make(dhw=False)["optimizer"].model.params
    params = copy.deepcopy(base)
    params.flow_curve_cop, params.cop_flow_carnot = True, False
    params.flow_curve_indoor_target = 21.0
    model = tm.ThermalModel(params)
    inert_cop = _m31_cop(model, params, o.FlowCurveBias())
    non_inert = cop_moved = nonfinite_after_fold = fold_raised = 0
    detail = []
    for d in M31_CORRUPT:
        a, b = o.FlowCurveBias.from_dict(dict(d)), m.FlowCurveBias.from_dict(dict(d))
        non_inert += (b.bias_k, b.samples) != (0.0, 0)
        restored = ((a.bias_k, a.samples), (b.bias_k, b.samples))
        ca, cb = _m31_cop(model, params, a), _m31_cop(model, params, b)
        cop_moved += ca != cb
        try:
            b.observe(45.0, 40.0)
            after = b.bias_k
        except ZeroDivisionError as err:
            after = f"raised {type(err).__name__}"
            fold_raised += 1
        nonfinite_after_fold += isinstance(after, float) and not np.isfinite(after)
        detail.append((d, restored[0], restored[1], round(ca, 4), round(cb, 4),
                       after))
    return {"diverge_in_domain": (ind, n_in),
            "corrupt_payloads_restored_non_inert": (non_inert, len(M31_CORRUPT)),
            "corrupt_payloads_moving_priced_cop": (cop_moved, len(M31_CORRUPT)),
            "corrupt_payloads_nonfinite_bias_after_one_fold": (nonfinite_after_fold, len(M31_CORRUPT)),
            "corrupt_payloads_fold_raises": (fold_raised, len(M31_CORRUPT)),
            "_detail (payload, orig, mutant, cop_orig, cop_mut, mutant_bias_after_fold)": detail,
            "_inert_cop": inert_cop}


@probe
def s05():
    """tariff:PeakTracker.from_dict's `not isfinite(window_factor) -> 1.0` guard. Corrupt stored
    window_factor ('nan'/'inf'/'-inf', parsed by float()); then the open window closes on the next
    month-internal window change. Metric: billed_peak_kw / threshold_kw after the close."""
    o, m, _ = mutload.pair("S05")
    from datetime import datetime
    ind = n_in = bad = n_bad = 0
    detail = []
    base = {"month": "2026-01", "peaks": [4.0, 3.5, 3.0], "peak_days": ["2026-01-02", "2026-01-03", "2026-01-04"],
            "window_key": "2026-01-10T07:00:00|60", "window_sum": 10.0, "window_samples": 4}
    for wf in (1.0, 0.5, 0.0, 0.25):
        d = dict(base, window_factor=wf)
        ta, tb = o.CapacityTariff(enabled=True, price_per_kw=50.0), m.CapacityTariff(enabled=True, price_per_kw=50.0)
        a, b = o.PeakTracker.from_dict(dict(d)), m.PeakTracker.from_dict(dict(d))
        a.observe(datetime(2026, 1, 10, 9, 0), 1.0, ta)
        b.observe(datetime(2026, 1, 10, 9, 0), 1.0, tb)
        n_in += 1
        ind += (a.billed_peak_kw(ta), a.threshold_kw(ta)) != (b.billed_peak_kw(tb), b.threshold_kw(tb))
    for wf in ("nan", "inf", "-inf"):
        d = dict(base, window_factor=wf)
        ta, tb = o.CapacityTariff(enabled=True, price_per_kw=50.0), m.CapacityTariff(enabled=True, price_per_kw=50.0)
        a, b = o.PeakTracker.from_dict(dict(d)), m.PeakTracker.from_dict(dict(d))
        a.observe(datetime(2026, 1, 10, 9, 0), 1.0, ta)
        b.observe(datetime(2026, 1, 10, 9, 0), 1.0, tb)
        va, vb = (a.billed_peak_kw(ta), a.threshold_kw(ta)), (b.billed_peak_kw(tb), b.threshold_kw(tb))
        n_bad += 1
        bad += (not all(np.isfinite(vb))) or va != vb
        detail.append((wf, va, vb))
    return {"diverge_in_domain": (ind, n_in), "corrupt_payloads_diverging": (bad, n_bad), "_detail": detail}


@probe
def s17():
    """price_model:PriceShapeModel.from_dict's non-finite shape-bin gate (#922 in its comment).
    A stored shape with one 'nan' bin; metric: guessed prices extend_price_series produces for
    the horizon past the published prices, orig vs mutant, and how many hours price at 0.0."""
    o, m, _ = mutload.pair("S17")
    from datetime import datetime, timedelta, timezone
    rng = np.random.default_rng(17)
    good = [[float(v) for v in 0.7 + 0.6 * rng.random(24)] for _ in range(2)]
    ind = n_in = 0
    for _ in range(10):
        shapes = [[float(v) for v in 0.7 + 0.6 * rng.random(24)] for _ in range(2)]
        d = {"shapes": shapes, "days": [30, 12]}
        n_in += 1
        ind += o.PriceShapeModel.from_dict(dict(d)).shapes != m.PriceShapeModel.from_dict(dict(d)).shapes
    t0 = datetime(2026, 1, 12, 0, 0, tzinfo=timezone.utc)
    starts = [t0 + timedelta(minutes=15 * i) for i in range(192)]
    known = [1.0] * 96
    detail = []
    zero_a = zero_b = 0
    for bad_hour in (3, 13, 18):
        shapes = [list(s) for s in good]
        shapes[0][bad_hour] = "nan"
        shapes[1][bad_hour] = "nan"
        d = {"shapes": shapes, "days": [30, 12]}
        ma, mb = o.PriceShapeModel.from_dict(dict(d)), m.PriceShapeModel.from_dict(dict(d))
        pa, _, _ = o.extend_price_series(list(known), 192, starts, ma)
        pb, _, _ = m.extend_price_series(list(known), 192, starts, mb)
        za, zb = int(np.sum(pa[96:] == 0.0)), int(np.sum(pb[96:] == 0.0))
        zero_a += za
        zero_b += zb
        detail.append((bad_hour, za, zb, bool(np.all(np.isfinite(pb)))))
    return {"diverge_in_domain": (ind, n_in), "zero_priced_guessed_steps_orig": (zero_a, 3 * 96),
            "zero_priced_guessed_steps_mutant": (zero_b, 3 * 96), "_detail (bad hour, zeros orig, zeros mut, mut finite)": detail}


def _price_run(o, m, d, n_known=96, n=192):
    from datetime import datetime, timedelta, timezone
    t0 = datetime(2026, 1, 12, 0, 0, tzinfo=timezone.utc)
    starts = [t0 + timedelta(minutes=15 * i) for i in range(n)]
    ma, mb = o.PriceShapeModel.from_dict(dict(d)), m.PriceShapeModel.from_dict(dict(d))
    ra = o.extend_price_series([1.0] * n_known, n, starts, ma)
    rb = m.extend_price_series([1.0] * n_known, n, starts, mb)
    return ra, rb


@probe
def s18():
    """price_model:PriceShapeModel.from_dict's non-finite quarter-factor gate ('Same gate as the
    shapes above (#922)'). One stored 'nan' quarter factor; metric: guessed steps priced 0.0."""
    o, m, _ = mutload.pair("S18")
    rng = np.random.default_rng(18)
    ind = n_in = 0
    for _ in range(10):
        q = [[float(v) for v in 0.8 + 0.4 * rng.random(96)] for _ in range(2)]
        d = {"shapes": [[1.0] * 24, [1.0] * 24], "days": [30, 12], "quarter_factors": q, "quarter_days": [20, 8]}
        (pa, _, sa), (pb, _, sb) = _price_run(o, m, d)
        n_in += 1
        ind += not (np.array_equal(pa, pb) and np.array_equal(sa, sb))
    zero_a = zero_b = 0
    for bad in (13, 55, 77):
        q = [[1.0] * 96 for _ in range(2)]
        q[0][bad] = "nan"
        q[1][bad] = "nan"
        d = {"shapes": [[1.0] * 24, [1.0] * 24], "days": [30, 12], "quarter_factors": q, "quarter_days": [20, 8]}
        (pa, _, _), (pb, _, _) = _price_run(o, m, d)
        zero_a += int(np.sum(pa[96:] == 0.0))
        zero_b += int(np.sum(pb[96:] == 0.0))
    return {"diverge_in_domain": (ind, n_in), "zero_priced_guessed_steps_orig": (zero_a, 3 * 96),
            "zero_priced_guessed_steps_mutant": (zero_b, 3 * 96)}


@probe
def s19():
    """price_model:PriceShapeModel.from_dict's residual_var clamp max(0.0, float(v)). A stored
    'nan' variance; metric: non-finite entries in the sigma extend_price_series hands the
    optimizer (price_sigma). Negative variances are the in-domain-equivalent arm (sigma() floors
    var <= 0 itself), so the guard's only load is the non-finite one."""
    o, m, _ = mutload.pair("S19")
    rng = np.random.default_rng(19)
    ind = n_in = 0
    for _ in range(10):
        var = [[float(v) for v in rng.random(24) * 0.1 - (0.05 if _ % 2 else 0.0)] for _ in range(2)]
        d = {"shapes": [[1.0] * 24, [1.0] * 24], "days": [30, 12], "residual_var": var}
        (pa, _, sa), (pb, _, sb) = _price_run(o, m, d)
        n_in += 1
        ind += not (np.array_equal(pa, pb) and np.array_equal(sa, sb))
    nf_a = nf_b = 0
    for bad in (2, 12, 20):
        var = [[0.02] * 24 for _ in range(2)]
        var[0][bad] = "nan"
        var[1][bad] = "nan"
        d = {"shapes": [[1.0] * 24, [1.0] * 24], "days": [30, 12], "residual_var": var}
        (_, _, sa), (_, _, sb) = _price_run(o, m, d)
        nf_a += int(np.sum(~np.isfinite(sa)))
        nf_b += int(np.sum(~np.isfinite(sb)))
    # The round trip a restart makes: a learned model -> as_dict -> from_dict -> sigma.
    learned = o.PriceShapeModel(days=[30, 12])
    learned.residual_var = [[0.01 + 0.002 * h for h in range(24)] for _ in range(2)]
    stored = learned.as_dict()
    (_, _, sa), (_, _, sb) = _price_run(o, m, stored)
    rt_a, rt_b = int(np.sum(sa[96:] > 0)), int(np.sum(sb[96:] > 0))
    return {"diverge_in_domain": (ind, n_in),
            "restart_round_trip_nonzero_sigma_steps_orig": (rt_a, 96),
            "restart_round_trip_nonzero_sigma_steps_mutant": (rt_b, 96),
            "nonfinite_sigma_steps_orig": (nf_a, 3 * 192),
            "nonfinite_sigma_steps_mutant": (nf_b, 3 * 192)}


def main() -> int:
    want = [a.upper() for a in sys.argv[1:]] or list(PROBES)
    for k in want:
        res = PROBES[k]()
        for name, v in res.items():
            if name.startswith("_"):
                print(f"  {k} {name[1:]}: {v}")
            else:
                print(f"RESULT {k}_{name}={v[0]}/{v[1]} probes")
    pt, tt = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={pt / tt if tt else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    for line in Path("/proc/vmstat").read_text().splitlines():
        if line.startswith("pswpin "):
            sw = int(line.split()[1])
    print(f"RESULT swapins={sw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
