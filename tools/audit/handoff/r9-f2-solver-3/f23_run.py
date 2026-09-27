import sys, inspect; sys.path.insert(0,"tests"); sys.path.insert(0,"custom_components")
import numpy as np
from harness import Results
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
R = Results("f23")
# -- R9-F2.3: the plant model's coupled Euler guard, coil debit and inlet ------
# Round 9, fix F2.3 (#1671 N-euler-coupled; #1644 P2; #1645 I5). Each arm
# drives the production symbol and reads the value it returns.
import importlib.util as _f23_ilu  # noqa: E402

from heatpump_optimizer import const as _f23_const  # noqa: E402
from heatpump_optimizer import mixing_valve as _f23_mv  # noqa: E402
from heatpump_optimizer import thermal_model as _f23_tm  # noqa: E402
from heatpump_optimizer.optimizer import HeatPumpOptimizer as _F23Opt  # noqa: E402

# D2-s1-01: every configuration below is accepted by the config flow's own
# ranges. The first two are the finder's named single-zone points; the third
# the two-zone grid point with the finder's worst per-substep radius (1.3958
# at the merge base); the last two a throttled valve regulating off a hot
# 750 L tank, where only the emitter conductance takes a row past 1: the
# radiators' in the upper zone's (loss and coupling 0.8 kW/K against a
# 0.25 kWh/K zone, 1.27 with the circuit), the floor's in the slab's (0.1
# against 0.1 kWh/K, 0.8 with the circuit). The
# property is the maximum principle a passive RC network obeys: a zero-input
# day from stores at 21 (slab 25, tank 30 or 60) against a 0 degC outdoor
# stays inside [0, hottest store], and the production step's own sub-step
# matrix -- finite differences of the step at the production h -- has no
# negative entry and a spectral radius at or under 1. (Not a row sum: a
# regulating valve draws the tank at the curve, so the tank's row leans on
# the zones with no diagonal to match, and sums past 1 while stable.)
_F23_EULER_CASES = (
    ("single-zone C=0.5 k=5", {
        "house_thermal_mass": 0.5, "house_heat_loss_coefficient": 0.2,
        "slab_thermal_mass": 0.5, "slab_heat_transfer": 5.0,
        "two_zone_mode": "off"}),
    ("single-zone C=1.0 k=5", {
        "house_thermal_mass": 1.0, "house_heat_loss_coefficient": 0.2,
        "slab_thermal_mass": 1.0, "slab_heat_transfer": 5.0,
        "two_zone_mode": "off"}),
    ("two-zone Cu=0.25 Cl=1.55 Cs=0.843 k=5", {
        "upper_floor_thermal_mass": 0.25, "lower_floor_thermal_mass": 1.55,
        "upper_floor_heat_loss": 1.0, "lower_floor_heat_loss": 1.0,
        "slab_thermal_mass": 0.843, "slab_heat_transfer": 5.0,
        "inter_zone_transfer": 0.01, "two_zone_mode": "on"}),
    ("two-zone valved, radiator row", {
        "upper_floor_thermal_mass": 0.25, "upper_floor_heat_loss": 0.3,
        "two_zone_mode": "on", "mixing_valve_mode": "manual",
        "buffer_tank_volume": 750.0}),
    ("two-zone valved, floor row", {
        "slab_thermal_mass": 0.1, "slab_heat_transfer": 0.1,
        "two_zone_mode": "on", "mixing_valve_mode": "manual",
        "buffer_tank_volume": 750.0}),
)
_F23_STORES = ("upper_floor_temperature", "lower_floor_temperature",
               "slab_temperature", "buffer_tank_temperature")


def _f23_model(cfg):
    p = ThermalParameters.from_config(cfg)
    p.internal_gains = 0.0
    p.internal_gains_profile = None
    return ThermalModel(p)


def _f23_start(m):
    return ThermalState(
        room_temperature=21.0, slab_temperature=25.0,
        upper_floor_temperature=21.0, lower_floor_temperature=21.0,
        buffer_tank_temperature=(
            60.0 if _f23_mv.is_throttling(m.params.mixing_valve_mode) else 30.0
        ),
        outdoor_temperature=0.0,
    )


def _f23_step_matrix(m, n_sub=None):
    """The production sub-step's Jacobian over the stores it integrates."""
    p = m.params
    h = 0.25 / (n_sub or m._stability_substeps(0.0, 0.0, 0.25))
    if p.two_zone_enabled:
        fields = _F23_STORES if _f23_mv.is_throttling(p.mixing_valve_mode) \
            else _F23_STORES[:3]

        def step(s):
            return m._simulate_step_two_zone(s, 0.0, 0.0, 0.0, 0.0, 0.0, h, 0.0)
    else:
        fields = ("room_temperature", "slab_temperature")

        def step(s):
            return m._simulate_step_single(s, 0.0, 0.0, 0.0, 0.0, 0.0, h, 0.0)
    f0 = step(_f23_start(m))
    eps = 1e-4
    jac = np.zeros((len(fields), len(fields)))
    for j, fj in enumerate(fields):
        s = _f23_start(m)
        setattr(s, fj, getattr(s, fj) + eps)
        f1 = step(s)
        for i, fi in enumerate(fields):
            jac[i, j] = (getattr(f1, fi) - getattr(f0, fi)) / eps
    return jac


for _f23_label, _f23_cfg in _F23_EULER_CASES:
    _f23_m = _f23_model(_f23_cfg)
    _f23_s0 = _f23_start(_f23_m)
    _f23_r = _f23_m.simulate_trajectory(
        _f23_s0, np.zeros(96), np.zeros(96), dt_hours=0.25)
    _f23_all = np.concatenate([np.asarray(a, dtype=float) for a in _f23_r[:5]])
    _f23_exc = (
        float(max(np.max(_f23_all) - _f23_s0.buffer_tank_temperature,
                  -np.min(_f23_all), 0.0))
        if np.all(np.isfinite(_f23_all)) else float("inf")
    )
    R.check(
        f"R9-F2.3 D2-s1-01 ({_f23_label}): a zero-input day stays inside the "
        "passive envelope [T_out, hottest store]",
        _f23_exc <= 1e-9,
        f"left the envelope by {_f23_exc:.4g} K at "
        f"n_sub={_f23_m._stability_substeps(0.0, 0.0, 0.25)}",
    )
    _f23_j = _f23_step_matrix(_f23_m)
    _f23_rho = float(np.max(np.abs(np.linalg.eigvals(_f23_j))))
    R.check(
        f"R9-F2.3 D2-s1-01 ({_f23_label}): the sub-step matrix is monotone -- "
        "no negative entry -- with spectral radius at or under 1",
        float(np.min(_f23_j)) >= -1e-6 and _f23_rho <= 1.0 + 1e-6,
        f"min entry {float(np.min(_f23_j)):.4f}, spectral radius "
        f"{_f23_rho:.4f}",
    )
# Null arm: the shipped defaults, single and two-zone, still never subdivide.
R.check(
    "R9-F2.3 D2-s1-01 (null arm): the shipped defaults keep n_sub == 1",
    ThermalModel(ThermalParameters())._stability_substeps(0.0, 0.0, 0.25) == 1
    and ThermalModel(ThermalParameters(two_zone_enabled=True))
    ._stability_substeps(0.0, 0.0, 0.25) == 1
    and _f23_model({"two_zone_mode": "on", "mixing_valve_mode": "manual",
                    "buffer_tank_volume": 750.0})
    ._stability_substeps(0.0, 0.0, 0.25) == 1,
)
# The count reads the step's own clamps: a design delta-T under 1 K, a COP
# under 1 and an empty buffer are integrated as 1 K, 1 and 0.04 kWh/K, so the
# count is the tightest monotone one there too (one sub-step fewer has a
# negative entry), and an empty buffer is counted, not divided by.
_F23_V = {"upper_floor_thermal_mass": 0.25, "upper_floor_heat_loss": 0.3,
          "two_zone_mode": "on", "mixing_valve_mode": "manual",
          "buffer_tank_volume": 750.0}
for _f23_label, _f23_cfg, _f23_set, _f23_tight in (
    ("design delta-T 0.5 K", _F23_V, {"emitter_design_delta_t": 0.5}, True),
    ("COP 0.5, delta-T 0.5 K", _F23_V,
     {"emitter_design_delta_t": 0.5, "cop_nominal": 0.5}, True),
    ("empty buffer", {"two_zone_mode": "on", "mixing_valve_mode": "manual",
                      "buffer_tank_volume": 0.0}, {}, False),
):
    _f23_m = _f23_model(_f23_cfg)
    for _f23_k, _f23_v in _f23_set.items():
        setattr(_f23_m.params, _f23_k, _f23_v)
    try:
        _f23_n = _f23_m._stability_substeps(0.0, 0.0, 0.25)
        _f23_j = _f23_step_matrix(_f23_m)
        _f23_jm = _f23_step_matrix(_f23_m, _f23_n - 1) if _f23_tight else None
        _f23_err = ""
    except (ArithmeticError, ValueError) as _f23_e:
        _f23_n, _f23_j, _f23_jm, _f23_err = 0, None, None, repr(_f23_e)
    R.check(
        f"R9-F2.3 D2-s1-01 ({_f23_label}): the count is the step's own "
        "stiffness -- monotone at n_sub"
        + (", and one sub-step fewer is not" if _f23_tight else ""),
        _f23_j is not None and float(np.min(_f23_j)) >= -1e-6
        and float(np.max(np.abs(np.linalg.eigvals(_f23_j)))) <= 1.0 + 1e-6
        and (not _f23_tight or (_f23_n > 1 and float(np.min(_f23_jm)) < -1e-6)),
        _f23_err or f"n_sub={_f23_n}, min entry {float(np.min(_f23_j)):.4f}"
        + (f", at n_sub-1 {float(np.min(_f23_jm)):.4f}" if _f23_tight else ""),
    )

# D2-s1-02: across the coil, the heat the wood tank loses equals the heat the
# DHW tank is spared, at every DHW tank temperature -- the finder's metric,
# C_w*(wood_off - wood_on) - [C_dhw*(dhw_on - dhw_off) - booked floor
# injection], from two production runs identical but for the coil. Below the
# 40 degC mixed-use temperature the step debits only the scaled draw, which is
# where the residual lived (0.405991 kWh per step at the merge base).
_f23_coil_base = dict(
    two_zone_enabled=True, mixing_valve_mode=_f23_mv.MODE_MANUAL,
    buffer_tank_volume=200.0, wood_tank_configured=True, wood_tank_volume=500.0,
    dhw_enabled=True, dhw_tank_volume=200.0, dhw_setpoint=55.0,
)
_f23_on = ThermalModel(ThermalParameters(**_f23_coil_base, dhw_wood_coil_enabled=True))
_f23_off = ThermalModel(ThermalParameters(**_f23_coil_base, dhw_wood_coil_enabled=False))


def _f23_coil_residual(dhw0, wood0):
    out = []
    for m in (_f23_on, _f23_off):
        s = ThermalState(
            room_temperature=21.0, slab_temperature=24.0,
            upper_floor_temperature=21.0, lower_floor_temperature=21.0,
            buffer_tank_temperature=40.0, dhw_temperature=dhw0,
            wood_tank_temperature=wood0,
        )
        r = m.simulate_trajectory_with_dhw(
            s, np.zeros(1), np.zeros(1), np.zeros(1), start_hour=7.0,
            dt_hours=0.25, dhw_draw_rates=np.full(1, 2.0))
        out.append((r[4][-1], r[6][-1], m._step_dhw_floor_injected * 0.25))
    (d_on, w_on, f_on), (d_off, w_off, f_off) = out
    c_w = _f23_on.params.wood_tank_thermal_mass
    c_d = _f23_on.params.dhw_tank_thermal_mass
    wood_out = c_w * (w_off - w_on)
    return wood_out - (c_d * (d_on - d_off) - (f_on - f_off)), wood_out


_f23_cells = [(d, w, *_f23_coil_residual(d, w))
              for d in (12.0, 20.0, 30.0, 35.0, 39.0, 45.0, 55.0)
              for w in (30.0, 70.0, 90.0)]
_f23_worst = max(_f23_cells, key=lambda c: abs(c[2]))
R.check(
    "R9-F2.3 D2-s1-02: the coil takes from the wood tank exactly the heat it "
    "spares the DHW tank, below the mixed-use temperature as above it",
    abs(_f23_worst[2]) <= 1e-9,
    f"residual {_f23_worst[2]:.6f} kWh at dhw0={_f23_worst[0]} "
    f"wood0={_f23_worst[1]}",
)
R.check(
    "R9-F2.3 D2-s1-02 (control): the coil genuinely draws on the wood tank in "
    "every cell, so the identity above is not an empty zero",
    all(c[3] > 1e-6 for c in _f23_cells),
    f"coil heat per cell {[round(c[3], 6) for c in _f23_cells]}",
)
_f23_scale = getattr(_f23_tm, "dhw_draw_scale", None)
R.check(
    "R9-F2.3 D2-s1-02: the tank debit, the coil's wood debit and the planner's "
    "capacity clamp read one draw-scale rule",
    _f23_scale is not None
    and _f23_scale(30.0, 10.0) == 20.0 / 30.0
    and _f23_scale(40.0, 10.0) == 1.0
    and _f23_scale(5.0, 10.0) == 0.0,
)
_f23_mix = _f23_tm.DHW_MIXED_USE_TEMP
try:
    _f23_edge = [_f23_scale(_f23_mix + 5.0, _f23_mix),
                 _f23_scale(_f23_mix, _f23_mix),
                 _f23_scale(_f23_mix + 5.0, _f23_mix + 2.0)]
except (ArithmeticError, TypeError) as _f23_e:
    _f23_edge = [repr(_f23_e)]
R.check(
    "R9-F2.3 D2-s1-02: an inlet at or above the mixed-use temperature scales "
    "the draw to 1 above it and 0 at it, never past [0, 1]",
    _f23_edge == [1.0, 0.0, 1.0],
    f"got {_f23_edge}",
)
_f23_nowood = ThermalState(room_temperature=21.0, slab_temperature=21.0,
                           dhw_temperature=45.0, outdoor_temperature=0.0)
try:
    _f23_nw = (ThermalModel(ThermalParameters()).apply_dhw_coil(
        _f23_nowood, 1.5, 45.0, 0.25), _f23_nowood.wood_tank_temperature)
except (ArithmeticError, TypeError) as _f23_e:
    _f23_nw = (repr(_f23_e), None)
R.check(
    "R9-F2.3 D2-s1-02: with no wood tank the coil passes the draw through "
    "untouched",
    _f23_nw == (1.5, None),
    f"got {_f23_nw}",
)

# D2-s2-03: the hot-water path settles up the end state its own published
# trajectory ends on -- the coil's wood debit included -- and its thermostat
# reference owns the same coil. The golden wood_coil scenario, solved once,
# with the settle-up's two ends read where they are consumed.
from golden import make as _f23_make, START as _F23_START  # noqa: E402
from golden import SCENARIOS as _F23_SCENARIOS  # noqa: E402

_f23_spec = dict(_F23_SCENARIOS["wood_coil"])
_f23_built = _f23_make(**_f23_spec)
_f23_opt = _f23_built["optimizer"]
_f23_seen: dict = {}
_f23_real_def = _F23Opt._deferred_energy_cost
_f23_real_base = _F23Opt._compute_baseline_power


def _f23_def(self, baseline_end, optimized_end, *a, **k):
    _f23_seen["ends"] = (baseline_end, optimized_end)
    return _f23_real_def(self, baseline_end, optimized_end, *a, **k)


def _f23_base(self, *a, **k):
    _f23_seen["base_call"] = (a, dict(k))
    return _f23_real_base(self, *a, **k)


_F23Opt._deferred_energy_cost = _f23_def
_F23Opt._compute_baseline_power = _f23_base
try:
    _f23_res = _f23_opt.optimize(
        _f23_built["state"], _f23_built["prices"], _f23_built["outdoor"],
        _f23_built["wind"], _f23_built["rain"], _f23_built["solar"],
        _F23_START, external_heat_kw=np.zeros(len(_f23_built["prices"])),
    )
finally:
    _F23Opt._deferred_energy_cost = _f23_real_def
    _F23Opt._compute_baseline_power = _f23_real_base
_f23_bend, _f23_oend = _f23_seen["ends"]
_f23_pub = {
    "wood_tank_temperature": _f23_res.wood_temp_trajectory,
    "buffer_tank_temperature": _f23_res.buffer_temp_trajectory,
    "upper_floor_temperature": _f23_res.upper_temp_trajectory,
    "lower_floor_temperature": _f23_res.lower_temp_trajectory,
    "slab_temperature": _f23_res.slab_temp_trajectory,
    "dhw_temperature": _f23_res.dhw_temp_trajectory,
}
_f23_gaps = {
    k: abs(float(getattr(_f23_oend, k)) - float(v[-1]))
    for k, v in _f23_pub.items()
}
R.check(
    "R9-F2.3 D2-s2-03: the hot-water settle-up's plan end is the published "
    "trajectory's last state, store for store",
    _f23_opt.model.params.dhw_coil_active and max(_f23_gaps.values()) <= 1e-9,
    f"end gaps (K): {({k: round(v, 6) for k, v in _f23_gaps.items()})}",
)
# The reference's no-coil twin: the same call, the coil's draws withheld.
_f23_ba, _f23_bk = _f23_seen["base_call"]
_f23_bk_full = dict(_f23_bk)
_f23_bk.pop("coil_draws", None)
_, _f23_bend_nocoil = _f23_real_base(_f23_opt, *_f23_ba, **_f23_bk)
R.check(
    "R9-F2.3 D2-s2-03: the thermostat reference's wood tank ends lower than "
    "its no-coil twin -- it owns the coil the plan owns",
    float(_f23_bend.wood_tank_temperature)
    < float(_f23_bend_nocoil.wood_tank_temperature) - 1e-6,
    f"reference wood end {float(_f23_bend.wood_tank_temperature):.6f} vs "
    f"no-coil {float(_f23_bend_nocoil.wood_tank_temperature):.6f}",
)
# ... and only while the coil is on: switched off, the draws change nothing.
_f23_opt.model.params.dhw_wood_coil_enabled = False
try:
    _, _f23_bend_off = _f23_real_base(_f23_opt, *_f23_ba, **_f23_bk_full)
finally:
    _f23_opt.model.params.dhw_wood_coil_enabled = True
R.check(
    "R9-F2.3 D2-s2-03: with the coil switched off, the reference's draws "
    "leave its wood tank as its no-coil twin's",
    np.any(np.asarray(_f23_bk_full.get("coil_draws", [])) > 0)
    and float(_f23_bend_off.wood_tank_temperature)
    == float(_f23_bend_nocoil.wood_tank_temperature),
    f"off {float(_f23_bend_off.wood_tank_temperature):.6f} vs no-coil "
    f"{float(_f23_bend_nocoil.wood_tank_temperature):.6f}",
)

# D7-s1-71 / D5-s2-03: the cold-water inlet default is defined once. The
# finder's rule, in memory: move const.DEFAULT_DHW_INLET_TEMP, load a fresh
# copy of thermal_model.py against it, and read what each site delivers; a
# site holding its own 10.0 stays behind. The retired constant's comment
# claimed a coupling the draw does not have, so it is gone rather than kept.
_f23_moved = 12.5
_f23_saved = _f23_const.DEFAULT_DHW_INLET_TEMP
_f23_const.DEFAULT_DHW_INLET_TEMP = _f23_moved
try:
    _f23_spec_tm = _f23_ilu.spec_from_file_location(
        "heatpump_optimizer._f23_thermal_model", _f23_tm.__file__)
    _f23_fresh = _f23_ilu.module_from_spec(_f23_spec_tm)
    sys.modules[_f23_spec_tm.name] = _f23_fresh
    _f23_spec_tm.loader.exec_module(_f23_fresh)
    _f23_sites = {
        "ThermalParameters()": _f23_fresh.ThermalParameters().dhw_inlet_temp,
        "ThermalParameters.from_config({})":
            _f23_fresh.ThermalParameters.from_config({}).dhw_inlet_temp,
        "dhw_coil_draw_reduction's inlet default": inspect.signature(
            _f23_fresh.dhw_coil_draw_reduction
        ).parameters["inlet_temp"].default,
    }
finally:
    _f23_const.DEFAULT_DHW_INLET_TEMP = _f23_saved
    sys.modules.pop("heatpump_optimizer._f23_thermal_model", None)
R.check(
    "R9-F2.3 D7-s1-71: every site resolving the cold-water inlet default "
    "follows DEFAULT_DHW_INLET_TEMP when it moves",
    all(v == _f23_moved for v in _f23_sites.values()),
    f"{_f23_sites}",
)
R.check(
    "R9-F2.3 D5-s2-03: no second cold-water constant claims to be the draw "
    "model's cold end",
    not hasattr(_f23_const, "DHW_COLD_WATER_TEMP"),
)



sys.exit(R.close("F23"))
