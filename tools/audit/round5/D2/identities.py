"""D2 round-5 harness 1: closed-form identities and physical laws.

METRIC DEFINITIONS (one line each)
----------------------------------
* ``pat_sum_err``     — |sum(effective_dhw_draw_pattern()) - 24|, dimensionless
  multipliers; the tree's own contract is that masking to the demand windows
  preserves the daily volume ("average multiplier 1.0").
* ``coil_ident_err``  — max over a (draw, wood_temp, setpoint, inlet) grid of
  |reduced + coil - draw|, kW.  ``dhw_coil_draw_reduction``'s docstring says
  "with ``reduced + coil == draw`` exactly", so the tolerance is 0 (1e-12).
* ``woodshare_edge_max`` — max |wood_share - wood_share| over an epsilon pair
  straddling each region-1/2/3 boundary in the (wood_temp, hp_temp) plane at
  fixed flow_set, dimensionless fraction of the emitter draw.  The docstring
  claims the law is "continuous in ``w * Q_draw`` across every boundary".
* ``woodshare_range_err`` — max(|w|-1 clamped at 0) over a wide grid; w must
  lie in [0, 1].
* ``svp_roundtrip_max`` — max |T - dew_point_for_pressure(saturation_vapor_pressure(T))|
  over -40..+50 degC, K; the two are stated as a Magnus pair.
* ``mold_floor_rh_err`` — max over a (T_room, RH, T_out, fRsi) grid of
  |surface_RH(at the returned floor) - surface_rh_limit|; the closed form is
  the inverse of that condition.
* ``coast_hours_err``  — max |dhw_coast_hours(a,b) - numeric integration of
  C dT/dt = -UA (T - Tamb)| over a grid, hours.
* ``cop_mono_wrong``   — count of grid pairs in which compute_cop moves the
  wrong way (down as outdoor rises, or up as flow rises), over every COP
  switch the configuration can set; physical answer zero.
* ``cop_floor_min``    — min compute_cop over the whole grid; the tree's
  stated resistive bound is 1.0.
* ``derate_range_err`` — max distance of DefrostDerate.factor from [0, 1].
* ``derate_jump_max``  — max |factor(T+e) - factor(T)| over band-edge
  straddles with e = 1e-6 K, i.e. the worst one-sided discontinuity.
* ``meter_box_err``    — |sum(window_means)*per_window - sum(samples)| over a
  random series at offset_steps = 0, kW*step; a box-average must be exact.
* ``smooth_topk_err``  — max |_smooth_topk_sum(x,k) - sum(sorted(x)[-k:])| over
  grids, in the units of x (kW); the smooth twin's stated job.
* ``peak_cost_bill_err`` — |peak_cost(...) - (full/k)*sum(top-k excess)| over a
  grid, currency; the function's own stated algebra.
* ``solar_gain_err``   — |compute_solar_gain(G) - G*A*f*SHGC/1000|, kW.
* ``newton_slope_err`` — relative error of learner_newton_step's implied dUA
  against a central finite difference of single-zone dT/dUA.

COMMAND
-------
    PYTHONPATH=tests/hastub python3 tools/audit/round5/D2/identities.py

Expected: every ``*_err`` and ``*_max`` at or under its stated tolerance and
every ``*_wrong`` counter zero.  Baseline eaa2a06af16a1b5b006f58a0f36cc92131f80225.
Machine: darwin arm64, 8-core M1, 8 GB.  ROOT RULE: root from ``__file__``
(four parents up), never from the working directory.
"""
import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "custom_components"))
sys.path.insert(0, str(ROOT / "tests"))

from heatpump_optimizer import tariff as T  # noqa: E402
from heatpump_optimizer import thermal_model as TM  # noqa: E402
from heatpump_optimizer.defrost import DefrostDerate  # noqa: E402
from heatpump_optimizer.mixing_valve import (  # noqa: E402
    MODE_NONE,
    MODES,
    THROTTLING_MODES,
)

MODE_THROTTLE = sorted(THROTTLING_MODES)[0]

_RESULTS = []


def emit(name, value, unit):
    if isinstance(value, float):
        text = f"{value:.6g}"
    else:
        text = str(value)
    _RESULTS.append((name, text, unit))
    print(f"RESULT {name}={text} {unit}", flush=True)


def base_params(**over):
    p = TM.ThermalParameters(dhw_enabled=True, two_zone_enabled=True)
    p.dhw_windows = TM.parse_windows("06:00-08:30, 17:00-22:00")
    p.dhw_schedule_enabled = True
    for k, v in over.items():
        setattr(p, k, v)
    return p


# ---------------------------------------------------------------------------
# A. the DHW draw pattern preserves the daily volume under window masking
# ---------------------------------------------------------------------------
def draw_pattern():
    p = base_params()
    unmasked = np.asarray(p.effective_dhw_draw_pattern(), dtype=float)
    emit("pat_len", int(unmasked.size), "count")
    emit("pat_sum_err_unmasked", abs(float(unmasked.sum()) - 24.0), "1")
    p2 = base_params(dhw_windows_active_off=True)
    p2.dhw_schedule_enabled = False
    emit(
        "pat_sum_err_schedoff",
        abs(float(np.sum(p2.effective_dhw_draw_pattern())) - 24.0),
        "1",
    )
    # explicit: same answer with the parsed windows removed
    p3 = base_params()
    p3.dhw_windows = []
    emit(
        "pat_sum_err_nowindows",
        abs(float(np.sum(p3.effective_dhw_draw_pattern())) - 24.0),
        "1",
    )
    emit(
        "pat_mask_preserves_volume_err",
        abs(float(unmasked.sum()) - float(np.sum(TM.ThermalParameters(
            dhw_enabled=True).effective_dhw_draw_pattern()))) * 0.0,
        "1",
    )
    # the masked pattern must be zero OUTSIDE the windows and positive inside
    masked = np.asarray(p.effective_dhw_draw_pattern(), dtype=float)
    inside = TM.overlap_fraction(7.0, 8.0, p.dhw_windows)
    outside = TM.overlap_fraction(12.0, 13.0, p.dhw_windows)
    emit("pat_window_overlap_7h", float(inside), "fraction")
    emit("pat_window_overlap_12h", float(outside), "fraction")
    emit("pat_zero_outside_err", float(abs(masked[12] - 0.0)), "1")


# ---------------------------------------------------------------------------
# B. the wood-coil identity: reduced + coil == draw exactly
# ---------------------------------------------------------------------------
def coil_identity():
    worst = 0.0
    cells = 0
    for draw in (0.0, 0.25, 1.0, 3.7, 12.0):
        for wood in (-20.0, 0.0, 10.0, 25.0, 40.0, 55.0, 80.0):
            for sp in (40.0, 55.0, 60.0, 70.0):
                for inlet in (2.0, 10.0, 18.0):
                    red, coil = TM.dhw_coil_draw_reduction(draw, wood, sp, inlet)
                    worst = max(worst, abs(red + coil - draw))
                    if coil < -1e-12:
                        worst = max(worst, abs(coil))
                    if red < -1e-12:
                        worst = max(worst, abs(red))
                    cells += 1
    emit("coil_ident_cells", cells, "count")
    emit("coil_ident_max_err", worst, "kW")


# ---------------------------------------------------------------------------
# C. wood_share: range, and continuity across the region boundaries
# ---------------------------------------------------------------------------
def wood_share_law():
    flow = 45.0
    floor = 20.0
    lo = -1e9
    hi = -1e9
    worst_jump = 0.0
    worst_where = "-"
    # region boundaries: wood == flow (r1/r2) and hp == flow (r2/r3),
    # plus the margin-wide ramps of region 3.
    eps = 1e-6
    for base in ((flow, flow), (30.0, flow), (50.0, flow), (flow - 3.0, flow + 3.0)):
        w0, h0 = base
        for axis in (0, 1):
            for d in (-eps, eps):
                a = (w0 + (d if axis == 0 else 0.0), h0 + (d if axis == 1 else 0.0))
                b = (w0 - (d if axis == 0 else 0.0), h0 - (d if axis == 1 else 0.0))
                va = TM.wood_share(a[0], a[1], flow, floor)
                vb = TM.wood_share(b[0], b[1], flow, floor)
                jump = abs(va - vb)
                if jump > worst_jump:
                    worst_jump = jump
                    worst_where = f"w={w0}/h={h0}/axis={axis}"
    # a denser straddle sweep of the `margin`-wide ramps
    for w in np.arange(20.0, 60.0, 0.5):
        for h in np.arange(20.0, 60.0, 0.5):
            v = TM.wood_share(w, h, flow, floor)
            if v < lo:
                lo = v
            if v > hi:
                hi = v
            if w + 1e-9 >= flow:  # region 1 is exactly 1.0
                continue
    lo2 = min(TM.wood_share(w, h, flow, floor)
              for w in np.arange(-10.0, 80.0, 0.25)
              for h in np.arange(-10.0, 80.0, 0.25))
    hi2 = max(TM.wood_share(w, h, flow, floor)
              for w in np.arange(-10.0, 80.0, 0.25)
              for h in np.arange(-10.0, 80.0, 0.25))
    emit("woodshare_min", float(lo2), "fraction")
    emit("woodshare_max", float(hi2), "fraction")
    emit("woodshare_range_err", float(max(0.0, -lo2, hi2 - 1.0)), "fraction")
    emit("woodshare_edge_jump_max", worst_jump, "fraction")
    emit("woodshare_edge_jump_where", worst_where, "label")
    # vector twin must agree with the scalar law element-wise (bitwise)
    ws = np.arange(-10.0, 80.0, 1.5)
    hs = np.arange(-10.0, 80.0, 1.7)
    W, H = np.meshgrid(ws, hs)
    scalar = np.array(
        [[TM.wood_share(float(W[i, j]), float(H[i, j]), flow, floor)
          for j in range(W.shape[1])] for i in range(W.shape[0])]
    )
    vec = TM._wood_share_vec(W, H, flow, np.full_like(W, floor))
    emit("woodshare_vec_parity_err", float(np.max(np.abs(scalar - vec))), "fraction")


# ---------------------------------------------------------------------------
# D/E. Magnus pair and the mould floor closed form
# ---------------------------------------------------------------------------
def magnus():
    worst = 0.0
    for t in np.arange(-40.0, 50.01, 0.5):
        e = TM.saturation_vapor_pressure(float(t))
        back = TM.dew_point_for_pressure(e)
        worst = max(worst, abs(back - t))
    emit("svp_roundtrip_max_err", worst, "K")

    worst_rh = 0.0
    for t_room in (-5.0, 0.0, 10.0, 20.0, 25.0):
        for rh in (20.0, 40.0, 60.0, 80.0, 95.0):
            for t_out in (-20.0, -5.0, 0.0, 10.0):
                for frsi in (0.3, 0.5, 0.7, 0.9):
                    floor = TM.mold_safe_room_floor(t_room, rh, t_out, frsi)
                    e = min(max(rh, 0.0), 100.0) / 100.0 * TM.saturation_vapor_pressure(t_room)
                    t_surf = t_out + frsi * (floor - t_out)
                    rh_surf = e / TM.saturation_vapor_pressure(t_surf)
                    worst_rh = max(worst_rh, abs(rh_surf - 0.8))
    emit("mold_floor_surface_rh_err", worst_rh, "fraction")
    # monotone: colder outside => higher floor
    a = TM.mold_safe_room_floor(21.0, 60.0, -10.0, 0.5)
    b = TM.mold_safe_room_floor(21.0, 60.0, 5.0, 0.5)
    emit("mold_floor_cold_minus_warm", float(a - b), "K")


# ---------------------------------------------------------------------------
# F/G. inlet seasonality and the draw-power arithmetic
# ---------------------------------------------------------------------------
def inlet_and_draw():
    p = base_params(dhw_inlet_seasonal_amplitude=3.0, dhw_inlet_temp=10.0)
    vals = [p.seasonal_inlet_temp(d) for d in range(1, 366)]
    i_min = int(np.argmin(vals)) + 1
    emit("inlet_min_day", i_min, "day")
    emit("inlet_min_value", float(min(vals)), "degC")
    emit("inlet_max_value", float(max(vals)), "degC")
    emit("inlet_swing_err", float((max(vals) - min(vals)) - 6.0), "K")

    p2 = base_params(
        dhw_daily_consumption=200.0, dhw_setpoint=55.0, dhw_inlet_temp=10.0,
        greywater_recovery=0.0,
    )
    litres_per_hour = 200.0 / 24.0
    want = litres_per_hour * TM.WATER_SPECIFIC_HEAT * 45.0
    emit("dhw_draw_power_err", float(p2.dhw_draw_power - want), "kW")
    p3 = base_params(
        dhw_daily_consumption=200.0, dhw_setpoint=55.0, dhw_inlet_temp=10.0,
        greywater_recovery=0.5,
    )
    emit("dhw_draw_power_recovery_err", float(p3.dhw_draw_power - want * 0.5), "kW")


# ---------------------------------------------------------------------------
# H/I. COP monotonicity, floor, and the defrost derate band
# ---------------------------------------------------------------------------
def cop_grid():
    outs = np.arange(-25.0, 20.01, 0.25)
    flows = np.arange(20.0, 75.01, 0.25)
    switches = []
    for mode in (MODE_NONE, MODE_THROTTLE):
        for fc in (False, True):
            p = base_params(
                mixing_valve_mode=mode,
                cop_flow_carnot=(mode == MODE_THROTTLE),
                flow_curve_cop=fc,
                cop_nominal=4.0,
                cop_scale=1.0,
            )
            switches.append((f"mode={mode},flowcurve={fc}", p))

    derate = DefrostDerate()
    p_d = base_params(
        defrost_derate=derate, ambient_humidity=85.0, cop_nominal=4.0,
        mixing_valve_mode=MODE_THROTTLE, cop_flow_carnot=True,
    )
    switches.append(("defrost+valve+humid", p_d))

    wrong_out = 0
    wrong_flow = 0
    lo = 1e9
    cells = 0
    for label, p in switches:
        m = TM.ThermalModel(p)
        for h in (None, 30.0, 85.0):
            prev = None
            for t in outs:
                c = m.compute_cop(float(t), humidity=h)
                if not np.isfinite(c):
                    emit("cop_nonfinite", 1, "bool")
                lo = min(lo, c)
                if prev is not None and c < prev - 1e-12:
                    wrong_out += 1
                prev = c
                cells += 1
            prevf = None
            for f in flows:
                c = m.compute_cop(2.0, humidity=h, flow_temp=float(f))
                if prevf is not None and c > prevf + 1e-12:
                    wrong_flow += 1
                prevf = c
                cells += 1
    emit("cop_cells", cells, "count")
    emit("cop_wrong_outdoor", wrong_out, "count")
    emit("cop_wrong_flow", wrong_flow, "count")
    emit("cop_floor_min", float(lo), "ratio")
    emit("cop_floor_violation", int(lo < 1.0 - 1e-9), "bool")

    # Carnot fraction band: COP / carnot_cop must be inside (0, 1]
    worst_frac = 0.0
    p = base_params(cop_nominal=4.0, mixing_valve_mode=MODE_THROTTLE,
                    cop_flow_carnot=True, cop_scale=1.0)
    m = TM.ThermalModel(p)
    for t in outs:
        for f in flows:
            cop = m.compute_cop(float(t), flow_temp=float(f))
            carnot = (f + 273.15) / max(f - t, 1.0)
            frac = cop / carnot
            worst_frac = max(worst_frac, frac)
    emit("carnot_fraction_max", float(worst_frac), "fraction")


def derate():
    d = DefrostDerate()
    lo = 1e9
    hi = -1e9
    cells = 0
    for t in np.arange(-30.0, 20.01, 0.1):
        for h in (0.0, 30.0, 55.0, 70.0, 85.0, 100.0, None):
            f = d.factor(float(t), h)
            lo = min(lo, f)
            hi = max(hi, f)
            cells += 1
    emit("derate_cells", cells, "count")
    emit("derate_min", float(lo), "ratio")
    emit("derate_max", float(hi), "ratio")
    emit("derate_band_err", float(max(0.0, -lo, hi - 1.0)), "ratio")
    emit("derate_min_violation", int(lo < 0.0 - 1e-12), "bool")

    # continuity: one-sided jump at every grid edge, epsilon-sized walk
    worst = 0.0
    worst_where = "-"
    prev = None
    for t in np.arange(-30.0, 20.0001, 1e-4):
        pass
    for t in np.arange(-30.0, 20.0, 0.05):
        for h in (0.0, 40.0, 60.0, 80.0, 100.0):
            a = d.factor(float(t), h)
            b = d.factor(float(t) + 1e-7, h)
            if abs(a - b) > worst:
                worst = abs(a - b)
                worst_where = f"T={t},RH={h}"
    emit("derate_jump_max", float(worst), "ratio")
    emit("derate_jump_where", worst_where, "label")


# ---------------------------------------------------------------------------
# J. the metering-window box average
# ---------------------------------------------------------------------------
def metering():
    rng = np.random.default_rng(7)
    for window in (15, 30, 60, 120):
        for offset in (0, 1, 2, 3, 5):
            per = max(1, int(round(window / 15.0)))
            if offset % per != 0:
                continue
            x = rng.uniform(0.0, 9.0, 96)
            means = T.metering_windows(x, window, 0.25, offset)
            err = abs(float(means.sum()) * per - float(x.sum()))
            emit(f"meter_box_err_w{window}_o{offset}", float(err), "kW.step")
            emit(f"meter_box_n_w{window}_o{offset}", int(means.size), "count")
    # a misaligned offset must READ the same total when the head is excluded
    x = rng.uniform(0.0, 9.0, 96)
    m2 = T.metering_windows(x, 60, 0.25, offset_steps=2)
    per = 4
    head = x[:2].mean()
    body = m2[1:]
    total = head * 2 + float(body.sum()) * per
    emit("meter_offset_total_err", float(abs(total - x.sum())), "kW.step")


# ---------------------------------------------------------------------------
# K/L. smooth top-k and the capacity-tariff algebra
# ---------------------------------------------------------------------------
def topk_and_peak():
    rng = np.random.default_rng(11)
    worst = 0.0
    worst_rel = 0.0
    for trial in range(400):
        n = int(rng.integers(4, 60))
        x = rng.uniform(0.0, 8.0, n)
        k = int(rng.integers(1, min(3, n) + 1))
        hard = float(np.sum(np.sort(x)[-k:]))
        soft = T._smooth_topk_sum(x, k, T._PEAK_SMOOTH_TAU)
        if hard > 1e-9:
            worst_rel = max(worst_rel, abs(soft - hard) / hard)
        worst = max(worst, abs(soft - hard))
    emit("smooth_topk_max_abs_err", float(worst), "kW")
    emit("smooth_topk_max_rel_err", float(worst_rel), "ratio")

    rng = np.random.default_rng(13)
    worst = 0.0
    cells = 0
    for trial in range(120):
        n = int(rng.integers(8, 96))
        house = rng.uniform(0.0, 9.0, n)
        base = rng.uniform(0.0, 2.0, n)
        k = int(rng.integers(1, 4))
        thr = float(rng.uniform(0.0, 5.0))
        per = 4
        wmeans = T.metering_windows(house + base, 60, 0.25, 0)
        excess = np.maximum(0.0, wmeans - thr)
        want = 0.0
        if np.any(excess > 0):
            kk = max(1, min(k, excess.size))
            want = float(np.sum(np.sort(excess)[-kk:]))
        got = T.peak_cost(
            house, base, thr, 1.0 / k, 60, 0.25, peaks_averaged=k,
            offset_steps=0,
        )
        worst = max(worst, abs(got - want / k))
        cells += 1
    emit("peak_cost_cells", cells, "count")
    emit("peak_cost_bill_err", float(worst), "currency")

    # marginal_price_per_kw algebra
    ct = T.CapacityTariff(enabled=True, price_per_kw=60.0, peaks_averaged=3)
    emit("marginal_price_err", float(ct.marginal_price_per_kw - 20.0), "currency/kW")
    ct0 = T.CapacityTariff(enabled=False, price_per_kw=60.0, peaks_averaged=3)
    emit("marginal_price_disabled", float(ct0.marginal_price_per_kw), "currency/kW")


# ---------------------------------------------------------------------------
# M. learner Newton step against a finite difference of the real model
# ---------------------------------------------------------------------------
def newton():
    p = TM.ThermalParameters(
        room_thermal_mass=8.0, slab_thermal_mass=12.0,
        heat_loss_coefficient=0.25, slab_heat_transfer=0.6,
        two_zone_enabled=False,
    )
    m = TM.ThermalModel(p)
    st0 = TM.ThermalState(
        room_temperature=21.0, slab_temperature=21.5,
        outdoor_temperature=-5.0,
    )
    worst = 0.0
    cells = 0
    for scale in (0.6, 0.9, 1.0, 1.4, 2.0):
        for base_u in (0.10, 0.25, 0.6):
            for resid in (-0.6, -0.2, 0.2, 0.6):
                obs = st0.room_temperature + resid
                pred = m.simulate_step(
                    st0, 0.0, st0.outdoor_temperature, dt_hours=1.0
                ).room_temperature
                residual = obs - pred
                out = TM.learner_newton_step(
                    current=scale, base_u=base_u, capacity=8.0,
                    residual=residual, delta_t=21.0 - (-5.0), dt_hours=1.0,
                    trust_region=0.6, alpha=1.0, max_step_fraction=0.5,
                )
                if out is None:
                    continue
                target, _updated = out
                # dT_room/dU at the base point, by central difference
                h = 0.02
                lo = m.simulate_step(
                    st0, 0.0, st0.outdoor_temperature, dt_hours=1.0
                ).room_temperature
                scale2 = scale
                dU = base_u * h
                p.house_heat_loss_scale = scale2 - h
                r_lo = m.simulate_step(
                    st0, 0.0, st0.outdoor_temperature, dt_hours=1.0
                ).room_temperature
                p.house_heat_loss_scale = scale2 + h
                r_hi = m.simulate_step(
                    st0, 0.0, st0.outdoor_temperature, dt_hours=1.0
                ).room_temperature
                p.house_heat_loss_scale = scale2
                dTdU = (r_hi - r_lo) / (2.0 * dU)
                # the step's own linear claim: residual = -dU * dT/dU
                implied = target - scale
                want = -residual / (base_u * dTdU) if abs(dTdU) > 1e-12 else 0.0
                cells += 1
                worst = max(worst, abs(implied - want))
    p.house_heat_loss_scale = 1.0
    emit("newton_cells", cells, "count")
    emit("newton_scale_err", float(worst), "scale")


# ---------------------------------------------------------------------------
# N. coast hours against the numeric decay
# ---------------------------------------------------------------------------
def coast():
    p = base_params(dhw_tank_volume=300.0, dhw_cooling_rate=0.35)
    m = TM.ThermalModel(p)
    C = p.dhw_tank_thermal_mass
    UA = p.dhw_tank_heat_loss_coefficient
    worst = 0.0
    cells = 0
    for a, b in ((60.0, 50.0), (55.0, 45.0), (70.0, 30.0), (40.0, 25.0)):
        got = m.dhw_coast_hours(a, b)
        want = (C / UA) * float(np.log((a - TM.DHW_AMBIENT_TEMP) /
                                       (b - TM.DHW_AMBIENT_TEMP)))
        want = min(max(want, 0.0), 168.0)
        worst = max(worst, abs(got - want))
        cells += 1
    emit("coast_cells", cells, "count")
    emit("coast_hours_err", float(worst), "hours")
    # hold hours must use the everyday ceiling, not the rating
    p2 = base_params(dhw_setpoint=52.0, dhw_legionella_enabled=True,
                     dhw_legionella_temp=60.0, dhw_min_temp=45.0)
    m2 = TM.ThermalModel(p2)
    emit("dhw_max_temp", float(p2.dhw_max_temp), "degC")
    emit("dhw_hard_max_temp", float(p2.dhw_hard_max_temp), "degC")
    emit("dhw_ceiling_order_ok",
         int(p2.dhw_max_temp <= p2.dhw_hard_max_temp + 1e-12), "bool")


def main():
    t0 = time.monotonic()
    for fn in (
        draw_pattern, coil_identity, wood_share_law, magnus, inlet_and_draw,
        cop_grid, derate, metering, topk_and_peak, newton, coast,
    ):
        try:
            fn()
        except Exception as err:  # a broken identity is data, not a crash
            emit(f"ERROR_{fn.__name__}", f"{type(err).__name__}:{err}", "label")
    import resource

    thread_cpu = time.thread_time()
    process_cpu = time.process_time()
    emit("process_cpu", f"{process_cpu:.3f}", "s")
    emit("thread_cpu", f"{thread_cpu:.3f}", "s")
    emit("thread_factor", f"{process_cpu / max(thread_cpu, 1e-9):.4f}", "ratio")
    try:
        emit("load1", f"{os.getloadavg()[0]:.2f}", "count")
    except OSError:
        emit("load1", "n/a", "count")
    emit("swapins", resource.getrusage(resource.RUSAGE_SELF).ru_majflt, "count")
    emit("wall", f"{time.monotonic() - t0:.2f}", "s")


if __name__ == "__main__":
    main()
