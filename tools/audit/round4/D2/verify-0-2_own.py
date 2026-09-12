"""Verifier 2 of panel D2-0, round 4 — my own measurements (not the finder's).

Written refute-first: every metric here is my own definition, chosen to be
independent of the finder's harness code path where that is possible.

EXACT COMMAND (from this tree's root):
    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D2/verify-0-2_own.py

BASELINE SHA measured: 0855277 (branch head claude/13-dimension-audit-920935;
finder measured 7dd68dd). MACHINE: 8-core Apple M1, shared box, load1 quoted.
All numbers are closed-form float identities or counts; no timings.

Sections (one per finding, prefix v2_<finding>_):
  D2-01  unit-of-defect ratio _smooth_topk_sum/(k*peak); analytic break;
         jitter attack (ties broken within and outside the 1e-3 band);
         realistic-threshold attack; flat-vs-spiky objective preference.
  D2-02  sample_factor walked by hand over a week (no window_factors);
         mask_active under perturbed offpeak factor.
  D2-03  sup-jump over a dense wood-temp grid at two flow_set values;
         fraction of the 2 degC band with a large jump; batched trajectory.
  D2-04  closed-form reconstruction of compute_cop(-21,70); my own grid at
         0.5 degC spacing; drop-the-70-row and drop-the--25-column LOO;
         inversion check; DHW at the default setpoint.
  D2-05  parse_rules on comma specs directly; dead-code probe.
"""
from __future__ import annotations

import math
import os
import sys

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "tools", "audit", "round4", "D2"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "tests", "hastub"))
sys.path.insert(0, os.path.join(ROOT, "custom_components"))

from datetime import datetime, timedelta, timezone  # noqa: E402

import numpy as np  # noqa: E402  (after the pin, deliberately)

from _d2common import Cpu, footer, result  # noqa: E402
import harness  # noqa: E402,F401
from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import grid_fee, tariff  # noqa: E402
from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
)
from heatpump_optimizer import thermal_model as tm  # noqa: E402
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState,
)

CPU = Cpu()


def R(name, value, unit=""):
    result(name, value, unit)


# ===========================================================================
# D2-01 — my metric: overstatement of the SMOOTH SUM ITSELF against k*peak,
# plus robustness attacks on the tie condition.
# ===========================================================================
K, TAU = 3, tariff._PEAK_SMOOTH_TAU
rng = np.random.default_rng(20260912)


def smooth_unit(n: int, excess: float, jitter: float = 0.0) -> float:
    x = np.full(n, excess) + (rng.uniform(-jitter, jitter, n) if jitter else 0.0)
    return tariff._smooth_topk_sum(x, K, TAU) / (K * float(np.max(x)))


R("v2_d201_smooth_over_12kw_96w", smooth_unit(96, 12.0), "ratio")
R("v2_d201_smooth_over_9kw_96w", smooth_unit(96, 9.0), "ratio")
R("v2_d201_smooth_over_6kw_96w", smooth_unit(96, 6.0), "ratio")
# analytic break: root offset 0.05*peak*ln((n-k)/k) == 1.0 (bracket half-width)
R("v2_d201_break_analytic_n96", 1.0 / (TAU * math.log((96 - K) / K)), "kW")
R("v2_d201_break_analytic_n24", 1.0 / (TAU * math.log((24 - K) / K)), "kW")

# jitter attack: ties within the 1e-3 band survive; and even jitter 4x the
# band still leaves >k windows within the band of the max (uniform jitter),
# so the branch is entered and the overstatement persists
R("v2_d201_jitter_5e4_ratio", smooth_unit(96, 12.0, 5e-4), "ratio")
jit = np.full(96, 12.0) + rng.uniform(-2e-3, 2e-3, 96)
with CPU:
    got_jit = tariff.peak_cost(jit, np.zeros(96), 0.0, 27.083333333, 15,
                               0.25, peaks_averaged=K)
R("v2_d201_jitter_2e3_ratio",
  got_jit / (27.083333333 * float(np.sum(np.sort(jit)[-K:]))), "ratio")

# realistic-threshold attack: early-month threshold 3 kW, flat 12 kW house
house = np.full(96, 12.0)
with CPU:
    charged = tariff.peak_cost(house, np.zeros(96), 3.0, 81.25 / 3.0, 15,
                               0.25, peaks_averaged=3)
R("v2_d201_threshold3kw_12kw_house_ratio",
  charged / ((81.25 / 3.0) * 3.0 * 9.0), "ratio")

# objective preference: identical billed top-k (3 x 12 kW), different term
flat = np.full(96, 12.0)
spiky = np.full(96, 0.0)
spiky[:3] = 12.0
with CPU:
    term_flat = tariff.peak_cost(flat, np.zeros(96), 0.0, 81.25 / 3.0, 15,
                                 0.25, peaks_averaged=3)
    term_spiky = tariff.peak_cost(spiky, np.zeros(96), 0.0, 81.25 / 3.0, 15,
                                  0.25, peaks_averaged=3)
R("v2_d201_term_flat_sek", term_flat, "SEK")
R("v2_d201_term_spiky_sek", term_spiky, "SEK")
R("v2_d201_spiky_cheaper_by", term_spiky - term_flat, "SEK")

# ===========================================================================
# D2-02 — my metric: walk sample_factor by hand over one tariff week
# ===========================================================================
ELL = "ellevio_villa_effekt_2026"
cfg = dict(grid_fee.apply_catalog(ELL))
co = HeatPumpOptimizerCoordinator(FakeHass({}), FakeEntry(data=cfg))
with CPU:
    t = co._capacity_tariff()
R("v2_d202_offpeak_factor_from_catalog", float(t.offpeak_factor), "factor")
R("v2_d202_mask_active", int(tariff.mask_active(t)), "bool")

jan4 = datetime(2026, 1, 5, 0, 0, tzinfo=timezone.utc)  # a Monday
with CPU:
    factors = [t.sample_factor(jan4 + timedelta(minutes=15 * i))
               for i in range(7 * 24 * 4)]
R("v2_d202_samplefactor_lt1_over_week",
  int(sum(1 for f in factors if f < 1.0)), "count")
R("v2_d202_samplefactor_sat_0000",
  float(t.sample_factor(datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc))),
  "factor")
R("v2_d202_samplefactor_wed_1200",
  float(t.sample_factor(datetime(2026, 1, 7, 12, 0, tzinfo=timezone.utc))),
  "factor")
# the month mask does bite (the null control, my own walk over July)
with CPU:
    july = [t.sample_factor(datetime(2026, 7, 6) + timedelta(hours=i))
            for i in range(7 * 24)]
R("v2_d202_july_unique", str(sorted(set(july))))
# and the same walk with the one-line fix (offpeak factor 0.0) lights up
t2 = tariff.CapacityTariff(enabled=True, price_per_kw=81.25, peaks_averaged=3,
                           window_minutes=15, months=t.months,
                           peak_hours=t.peak_hours,
                           weekdays_only=t.weekdays_only, offpeak_factor=0.0)
with CPU:
    factors2 = [t2.sample_factor(jan4 + timedelta(minutes=15 * i))
                for i in range(7 * 24 * 4)]
R("v2_d202_perturbed_samplefactor_lt1", int(sum(1 for f in factors2 if f < 1.0)),
  "count")

# ===========================================================================
# D2-03 — my metric: sup of the jump over a dense wood-temp grid, at two
# curve temperatures; and the fraction of the 2 degC band that jumps > 0.5
# ===========================================================================
def sup_jump(flow_set: float, floor: float = 21.0, eps: float = 1e-9) -> float:
    wood = np.linspace(flow_set - tm.WOOD_TANK_MIN_MARGIN, flow_set, 4001)
    below = [tm.wood_share(float(w), flow_set - eps, flow_set, floor)
             for w in wood]
    above = [tm.wood_share(float(w), flow_set + eps, flow_set, floor)
             for w in wood]
    return float(np.max(np.abs(np.array(below) - np.array(above))))


R("v2_d203_sup_jump_flow26c6", sup_jump(26.6), "fraction")
R("v2_d203_sup_jump_flow40", sup_jump(40.0), "fraction")
R("v2_d203_sup_jump_flow55", sup_jump(55.0), "fraction")

wood_band = np.linspace(26.6 - 2.0, 26.6, 2001)
with CPU:
    band_jumps = np.array([
        abs(tm.wood_share(float(w), 26.6 - 1e-9, 26.6, 21.0)
            - tm.wood_share(float(w), 26.6 + 1e-9, 26.6, 21.0))
        for w in wood_band])
R("v2_d203_band_frac_jump_gt_0.5",
  float(np.mean(band_jumps > 0.5)), "fraction")
R("v2_d203_band_frac_jump_gt_0.1",
  float(np.mean(band_jumps > 0.1)), "fraction")

# through the batched trajectory (the path the optimizer actually drives),
# at SEVERAL outdoor temperatures (curve temperatures from the production
# valve symbol): bisect the wood-tank start so the valve law reads it 0.25
# degC below the curve, then bisect the step-0 electrical power onto the
# buffer-crossing and take the wood tank's step-1 enthalpy change on both
# sides of a ~1-ulp power gap.
from heatpump_optimizer import mixing_valve  # noqa: E402

PARAMS = ThermalParameters(two_zone_enabled=True, mixing_valve_mode="manual",
                           wood_tank_configured=True)
MODEL = ThermalModel(PARAMS)

_u_up = MODEL.effective_heat_loss_coefficient(PARAMS.upper_floor_heat_loss)
_u_lo = MODEL.effective_heat_loss_coefficient(
    PARAMS.lower_floor_heat_loss_learned)
_design = PARAMS.max_electrical_power * max(PARAMS.cop_nominal, 1.0)


def curve_at(out: float) -> float:
    return float(mixing_valve.flow_setpoint(
        target_temp=(PARAMS.mixing_valve_target or PARAMS.comfort_ceiling),
        outdoor_temp=out,
        heat_loss_coefficient=_u_up + _u_lo,
        emitter_ua=_design / max(PARAMS.emitter_design_delta_t, 1.0),
    ))


def traj_at(out: float, p0: float, wood0: float):
    curve = curve_at(out)
    st = ThermalState(room_temperature=21.0, slab_temperature=23.0,
                      outdoor_temperature=out, upper_floor_temperature=21.0,
                      lower_floor_temperature=21.0,
                      buffer_tank_temperature=curve - 3.0,
                      wood_tank_temperature=wood0)
    with CPU:
        _r, _s, _u, _l, buf, _ref, wood = MODEL.simulate_trajectory(
            st, np.array([p0, 0.0]), np.full(2, out), dt_hours=0.25)
    return (float(buf[1]), float(wood[1]),
            PARAMS.wood_tank_thermal_mass * float(wood[2] - wood[1]))


for _out in (-5.0, -10.0, -15.0, -20.0, -25.0):
    _curve = curve_at(_out)

    def _traj(p0, w0, _out=_out):
        return traj_at(_out, p0, w0)

    wlo, whi = _curve - 4.0, _curve + 8.0
    for _ in range(80):
        mid = 0.5 * (wlo + whi)
        if _traj(0.18, mid)[1] > _curve - 0.25:
            whi = mid
        else:
            wlo = mid
    WOOD0 = 0.5 * (wlo + whi)
    lo, hi = 0.0, float(PARAMS.max_electrical_power)
    for _ in range(52):
        mid = 0.5 * (lo + hi)
        if _traj(mid, WOOD0)[0] > _curve:
            hi = mid
        else:
            lo = mid
    _b = _traj(lo, WOOD0)
    _a = _traj(hi, WOOD0)
    tag = f"{_out:g}"
    R(f"v2_d203_traj_out{_out:g}_curve_c", _curve, "degC")
    R(f"v2_d203_traj_out{_out:g}_power_gap_kw", hi - lo, "kW")
    R(f"v2_d203_traj_out{_out:g}_wood_jump_kwh", _b[2] - _a[2], "kWh")

# ===========================================================================
# D2-04 — closed-form reconstruction + my own grid + LOO variants
# ===========================================================================
P = ThermalParameters.from_config({"mixing_valve_mode": "manual",
                                   "two_zone_enabled": True})
M = ThermalModel(P)
# closed form at outdoor -21, flow 70: 3.5 * 0.3 * carnot_ratio
t_out = -21.0 + 273.15
cf = (70.0 + 273.15) / max(70.0 + 273.15 - t_out, 1.0)
cr = (35.0 + 273.15) / max(35.0 + 273.15 - t_out, 1.0)
R("v2_d204_closedform_m21_f70", 3.5 * 0.3 * max(0.25, cf / cr), "cop")
R("v2_d204_compute_cop_m21_f70", M.compute_cop(-21.0, flow_temp=70.0), "cop")

# my own grid, 0.5 degC spacing over the same envelope
OUT = np.arange(-25.0, 15.001, 0.5)
FLW = np.arange(35.0, 70.001, 0.5)
with CPU:
    G = np.array([[M.compute_cop(float(o), flow_temp=float(f)) for o in OUT]
                  for f in FLW])
R("v2_d204_mygrid_cells", int(G.size), "count")
R("v2_d204_mygrid_min_cop", float(G.min()), "cop")
R("v2_d204_mygrid_cells_below_unity", int(np.sum(G < 1.0)), "count")
R("v2_d204_mygrid_frac_below_unity", float(np.mean(G < 1.0)), "fraction")
# LOO: drop the flow-70 row entirely / drop the outdoor -25 column
R("v2_d204_loo_drop_flow70",
  int(np.sum(G[:-1, :] < 1.0)), "count")
R("v2_d204_loo_drop_out_m25",
  int(np.sum(G[:, 1:] < 1.0)), "count")
R("v2_d204_loo_drop_both",
  int(np.sum(G[:-1, 1:] < 1.0)), "count")
# the inversion, closed-form check at the two ends
R("v2_d204_cop_m30_f70", M.compute_cop(-30.0, flow_temp=70.0), "cop")
R("v2_d204_cop_m21_f70_again", M.compute_cop(-21.0, flow_temp=70.0), "cop")
R("v2_d204_inverts_fall_with_warming",
  int(M.compute_cop(-30.0, flow_temp=70.0)
      > M.compute_cop(-21.0, flow_temp=70.0)), "bool")
# DHW at the DEFAULT setpoint (55) -- the load-bearing reachable number
with CPU:
    dhw = np.array([M.compute_cop_dhw(float(o), 55.0) for o in OUT])
R("v2_d204_dhw55_min", float(dhw.min()), "cop")
R("v2_d204_dhw55_cells_below_unity", int(np.sum(dhw < 1.0)), "count")
R("v2_d204_dhw55_outdoor_at_min", float(OUT[int(np.argmin(dhw))]), "degC")
# null: valve off -> the floor holds
M0 = ThermalModel(ThermalParameters.from_config({"mixing_valve_mode": "none"}))
with CPU:
    G0 = np.array([[M0.compute_cop(float(o), flow_temp=float(f)) for o in OUT]
                   for f in FLW])
R("v2_d204_null_carnot_off_min", float(G0.min()), "cop")

# ===========================================================================
# D2-05 — parse_rules on comma specs, directly
# ===========================================================================
COMMA_SPECS = ["= 0,45", "Nov-Mar 06:00-22:00 = 0,27", "maj = 0,20",
               "Mon-Fri 07:00-19:00 = 1,05", "lor 00:00-24:00 = 0,09",
               "= 0,18; Nov-Mar Mon-Fri 06:00-22:00 = 0,27"]
ok = 0
with CPU:
    for s in COMMA_SPECS:
        try:
            grid_fee.parse_rules(s)
            ok += 1
        except grid_fee.GridFeeError:
            pass
R("v2_d205_comma_specs_parsed", ok, f"of {len(COMMA_SPECS)}")
with CPU:
    dotted = 0
    for s in COMMA_SPECS:
        try:
            grid_fee.parse_rules(s.replace(",", ".").replace(";", ","))
            dotted += 1
        except grid_fee.GridFeeError:
            pass
R("v2_d205_dotted_specs_parsed", dotted, f"of {len(COMMA_SPECS)}")
# the dead conversion, exercised on its own
with CPU:
    rr = grid_fee._parse_rule("lor 00:00-24:00 = 0,09")
R("v2_d205_parse_rule_unit_comma_rate", float(rr.rate), "SEK/kWh")

footer(CPU, "[v]erify-0-2_own")
