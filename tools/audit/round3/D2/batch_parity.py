"""D2 -- scalar `simulate_trajectory` versus vectorized
`simulate_trajectory_batch`: the bitwise-parity contract the batch docstring
states ("Bitwise parity is the contract. Every row must equal what the scalar
path produces for the same schedule, to the last bit").

METRIC: per (topology x feature) cell, `max_ulp` = the largest absolute
difference, in units of the last place of the scalar value, between the scalar
trajectory and the corresponding batch row, over every store
(room/slab/upper/lower/buffer/wood) and every step; and `max_abs` the same
difference in kelvin.  Bitwise parity means max_ulp == 0 in every cell.

COMMAND (from the repository root, ~40 s):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D2/batch_parity.py

EXPECTED at baseline ae36eff: `cells=22`, `cells_not_bit_identical=<n>` and
`max_abs_kelvin` over all cells.  Tolerance for "bit identical" is exactly 0.0;
the contract admits no slack.  Any non-zero cell is reported by name with the
store and step at which it first diverges.

PERTURBATION (direction stated): in
`thermal_model.py:simulate_trajectory_batch`, change the single-zone branch's
`T_room = T_room + dT_room * dt` to `T_room = T_room + dt * dT_room` ->
`max_ulp` for the single-zone cells must become non-zero (re-association is
exactly what the docstring forbids).  Not applied here: this harness does not
edit production.  The live control instead is `--scramble`, which adds 1e-9 kW to
step N/2 of the BATCH input only and requires `max_ulp_all_cells` to leave zero
(measured: >=1 ulp in every cell); a harness that still reports 0 there is
comparing an array with itself and is measuring nothing.

BASELINE SHA: ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1
MACHINE: 8-core Apple M1, 8 GB, numpy 2.4.6 / scipy 1.17.1 on OpenBLAS
INSTRUMENTED SYMBOLS: thermal_model.py:ThermalModel.simulate_trajectory,
    :ThermalModel.simulate_trajectory_batch, :ThermalModel.simulate_step
"""
import sys

import d2lib  # noqa: F401  -- thread pin + sys.path, must be first
import numpy as np

from profiles import house
from heatpump_optimizer.defrost import DefrostDerate
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

d2lib.repo_root_ok()

SCRAMBLE = "--scramble" in sys.argv
N = 24          # steps
DT = 0.25       # hours
RNG = np.random.default_rng(20260910)


def params_for(cfg_over, param_over=None, two_zone=False):
    cfg = house(two_zone=two_zone, dhw=False)
    cfg.update(cfg_over or {})
    p = ThermalParameters.from_config(cfg)
    for k, v in (param_over or {}).items():
        setattr(p, k, v)
    return p


def base_state(**over):
    st = ThermalState(
        room_temperature=21.0,
        slab_temperature=22.3,
        outdoor_temperature=-4.0,
        upper_floor_temperature=21.7,   # deliberately != room: the classic
        lower_floor_temperature=20.4,   # single-zone seeding parity bug
        dhw_temperature=50.0,
        dhw_hours_since_legionella=20.0,
        buffer_tank_temperature=41.0,
    )
    for k, v in over.items():
        setattr(st, k, v)
    return st


def ulps(a, b):
    """Difference between a and b in units of the last place of a."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    step = np.nextafter(np.abs(a), np.inf) - np.abs(a)
    step = np.where(step > 0, step, np.finfo(float).tiny)
    return np.abs(a - b) / step


CELLS = []


def cell(name, **kw):
    CELLS.append((name, kw))


# --- the sweep -------------------------------------------------------------
derate = DefrostDerate()
hum = np.full(N, 85.0)
hum[3] = np.nan          # #21's unknown-step marker
hum[7] = 40.0
ext = np.zeros(N)
ext[5:9] = 3.0
sol = np.linspace(0.0, 320.0, N)
wind = np.linspace(0.0, 9.0, N)
rain = np.where(np.arange(N) % 5 == 0, 1.7, 0.0)
gains_profile = list(np.linspace(0.2, 1.8, 24))

valve_cfg = {
    "mixing_valve_mode": "manual",
    "buffer_tank_volume": 750.0,
    "buffer_max_temperature": 70.0,
}
wood_cfg = dict(valve_cfg, **{
    "wood_tank_top_entity": "sensor.wood_top",
    "wood_tank_volume": 500.0,
})

cell("single_plain", two_zone=False)
cell("single_weather", two_zone=False, wind=wind, rain=rain, sol=sol)
cell("single_external_heat", two_zone=False, ext=ext)
cell("single_derate_humidity", two_zone=False, derate=True, hum=hum)
cell("single_gains_profile", two_zone=False, gains=True, start_hour=5.5)
cell("single_all", two_zone=False, wind=wind, rain=rain, sol=sol, ext=ext,
     derate=True, hum=hum, gains=True, start_hour=5.5)
# Force the Euler stability subdivision: tiny masses against a big coupling.
cell("single_substeps", two_zone=False,
     param_over={"room_thermal_mass": 0.35, "slab_thermal_mass": 0.4,
                 "slab_heat_transfer": 3.0, "heat_loss_coefficient": 1.2})
cell("two_zone_plain", two_zone=True)
cell("two_zone_weather", two_zone=True, wind=wind, rain=rain, sol=sol)
cell("two_zone_external_heat", two_zone=True, ext=ext)
cell("two_zone_derate_humidity", two_zone=True, derate=True, hum=hum)
cell("two_zone_gains_profile", two_zone=True, gains=True, start_hour=5.5)
cell("two_zone_substeps", two_zone=True,
     param_over={"upper_floor_thermal_mass": 0.4, "lower_floor_thermal_mass": 0.5,
                 "slab_thermal_mass": 0.5, "slab_heat_transfer": 3.0,
                 "inter_zone_transfer": 2.0})
cell("valve_manual", two_zone=True, cfg=valve_cfg, buffer0=32.0)
cell("valve_targets", two_zone=True, cfg=valve_cfg, buffer0=32.0,
     valve_targets=np.linspace(20.0, 23.0, N))
cell("valve_weather_sol", two_zone=True, cfg=valve_cfg, buffer0=32.0,
     wind=wind, rain=rain, sol=sol)
cell("valve_external_heat", two_zone=True, cfg=valve_cfg, buffer0=32.0, ext=ext)
cell("valve_hot_tank", two_zone=True, cfg=valve_cfg, buffer0=68.0)
cell("valve_slab_direct", two_zone=True,
     cfg=dict(valve_cfg, **{"topology_layout": "valve_upper_direct_slab"}),
     buffer0=45.0)
cell("wood_two_tank", two_zone=True, cfg=wood_cfg, buffer0=32.0, wood0=72.0)
cell("wood_two_tank_cold", two_zone=True, cfg=wood_cfg, buffer0=32.0, wood0=25.0)
cell("wood_two_tank_ext", two_zone=True, cfg=wood_cfg, buffer0=32.0, wood0=72.0,
     ext=ext)


def run_cell(kw):
    p = params_for(kw.get("cfg"), kw.get("param_over"), two_zone=kw["two_zone"])
    if kw.get("derate"):
        p.defrost_derate = derate
    else:
        p.defrost_derate = None
    if kw.get("gains"):
        p.internal_gains_profile = gains_profile
    m = ThermalModel(p)
    st = base_state()
    if "buffer0" in kw:
        st.buffer_tank_temperature = kw["buffer0"]
    if "wood0" in kw:
        st.wood_tank_temperature = kw["wood0"]

    power = np.round(RNG.uniform(0.0, p.max_electrical_power, N), 6)
    batch_power = power
    if SCRAMBLE:
        # Inject a known divergence into the BATCH input only: the metric must
        # move off zero, which is what shows the comparison is live rather than
        # comparing an array with itself.
        batch_power = power.copy()
        batch_power[N // 2] += 1e-9

    common = dict(
        outdoor_temps=np.linspace(-12.0, 6.0, N),
        wind_speeds=kw.get("wind"),
        precipitation=kw.get("rain"),
        solar_radiation=kw.get("sol"),
        dt_hours=DT,
        external_heat_kw=kw.get("ext"),
        valve_targets=kw.get("valve_targets"),
        humidity=kw.get("hum") if kw.get("derate") else None,
        start_hour=kw.get("start_hour"),
    )
    scal = m.simulate_trajectory(st, power, **common)
    bat = m.simulate_trajectory_batch(st, batch_power[None, :], **common)
    names = ("room", "slab", "upper", "lower", "buffer")
    worst_ulp, worst_abs, where = 0.0, 0.0, ""
    for idx, nm in enumerate(names):
        s = np.asarray(scal[idx], dtype=float)
        b = np.asarray(bat[nm], dtype=float)[0]
        u = ulps(s, b)
        a = np.abs(s - b)
        if u.max() > worst_ulp:
            worst_ulp = float(u.max())
            where = f"{nm}@step{int(np.argmax(u))}"
        worst_abs = max(worst_abs, float(a.max()))
    if scal[6] is not None and bat["wood"] is not None:
        s = np.asarray(scal[6], dtype=float)
        b = np.asarray(bat["wood"], dtype=float)[0]
        u = ulps(s, b)
        if u.max() > worst_ulp:
            worst_ulp = float(u.max())
            where = f"wood@step{int(np.argmax(u))}"
        worst_abs = max(worst_abs, float(np.abs(s - b).max()))
    # The refused-heat ledger is part of the contract too.
    ref_s = np.asarray(scal[5], dtype=float)
    ref_b = np.asarray(bat["refused"], dtype=float)[0]
    ref_abs = float(np.abs(ref_s - ref_b).max())
    return worst_ulp, worst_abs, where, ref_abs


def main() -> int:
    bad = []
    worst_all_ulp, worst_all_abs, worst_ref = 0.0, 0.0, 0.0
    for name, kw in CELLS:
        u, a, where, ref = run_cell(kw)
        worst_all_ulp = max(worst_all_ulp, u)
        worst_all_abs = max(worst_all_abs, a)
        worst_ref = max(worst_ref, ref)
        flag = "BIT-IDENTICAL" if u == 0.0 and ref == 0.0 else "DIVERGES"
        if flag == "DIVERGES":
            bad.append((name, u, a, where, ref))
        d2lib.result(
            f"cell_{name}",
            f"{flag} max_ulp={u:g} max_abs={a:.3e}K first={where or '-'} "
            f"refused_max_abs={ref:.3e}",
        )
    d2lib.result("cells", len(CELLS))
    d2lib.result("cells_not_bit_identical", len(bad))
    d2lib.result("max_ulp_all_cells", f"{worst_all_ulp:g}", "ulp")
    d2lib.result("max_abs_kelvin", f"{worst_all_abs:.6e}", "K")
    d2lib.result("max_abs_refused", f"{worst_ref:.6e}", "kW")
    d2lib.result("tolerance", "0.0 ulp (docstring: bitwise parity is the contract)")
    d2lib.result("scramble_arm", "1" if SCRAMBLE else "0")
    for name, u, a, where, ref in bad:
        d2lib.result(f"diverging_{name}", f"ulp={u:g} abs={a:.3e}K at={where}")
    d2lib.env_footer()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
