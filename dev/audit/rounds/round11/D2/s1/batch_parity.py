#!/usr/bin/env python3
"""D2.M1 batch-parity: scalar simulate_trajectory against simulate_trajectory_batch, bit for bit.

Metric: per input level, the count of trajectory elements (room, slab, upper, lower,
buffer, wood, refused over every row and step) where the batch twin differs from the
scalar path by any bit; plus the largest absolute difference in K (or kW for refused).
Count key: the arrays the production seams return (ThermalModel.simulate_trajectory per
row vs ThermalModel.simulate_trajectory_batch), never an input attribute.

Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D2/s1/batch_parity.py [--fix-lift]
  --fix-lift  perturbation of D2-s1-01: ThermalModel.flow_lift_factor swapped in memory for
              the Carnot ratio the batch twin uses (carnot_flow / carnot_ref); every single-zone
              valve arm and the dhw[combi], wood and coil arms go to zero.
  --fix-emitter  perturbation of D2-s1-02: mixing_valve.emitter_delivery swapped in memory for
              max(0, ua*(mix-zone)) (its own docstring's "never negative"); with --fix-lift the
              remaining two-zone valve mismatches (valve 2z, pv 2z-valve) go to zero.
Expected at baseline: mismatches on every level whose config throttles a valve
(valve, dhw[combi], wood, coil, external_heat[valve arm], pv[valve arm]) -- tolerance exact;
0 on space_only.  Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B4 (4 vCPU container).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import numpy as np  # noqa: E402
from unittest import mock  # noqa: E402
from contextlib import ExitStack  # noqa: E402
from heatpump_optimizer import mixing_valve  # noqa: E402
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalState, WeatherSeries)

N, B = 96, 6


def emitter_fixed(*, mix_temp, zone_temp, ua):
    return max(0.0, ua * (mix_temp - zone_temp))


def lift_fixed(self, outdoor_temp, flow_temp):
    """The batch twin's own Carnot ratio (thermal_model.py _batch_cop), scalar."""
    ref = self.params.cop_flow_reference_temp
    if not flow_temp > ref:
        return 1.0
    t_ratio = min(max(outdoor_temp, self.params.cop_reference_temp - (1.0 - 0.3) / 0.025),
                  self.params.cop_reference_temp)
    t_out = t_ratio + 273.15
    carnot_flow = (flow_temp + 273.15) / max(flow_temp + 273.15 - t_out, 1.0)
    carnot_ref = (ref + 273.15) / max(ref + 273.15 - t_out, 1.0)
    if carnot_ref <= 1e-9:
        return 1.0
    return max(0.25, carnot_flow / carnot_ref)


VALVE = {"mixing_valve_mode": "manual", "buffer_tank_volume": 750.0, "buffer_max_temperature": 70.0}
WOOD = dict(VALVE, wood_tank_top_entity="sensor.wood_top", wood_tank_volume=500.0)


def arms():
    """(level, label, params kwargs, attribute overrides, state overrides, weather extras)."""
    out = []
    for tz in (False, True):
        z = "2z" if tz else "1z"
        out.append(("space_only", z, dict(two_zone=tz), {}, {}, {}))
        out.append(("space_only", z + "-flowcurve-partload", dict(
            two_zone=tz, flow_curve_cop_enabled=True, heat_pump_max_power=3.0,
            heat_pump_cop_partload_derate=0.15), {}, {}, {}))
        out.append(("space_only", z + "-stiff", dict(two_zone=tz), {"slab_thermal_mass": 0.05,
                    "room_thermal_mass": 0.05, "upper_floor_thermal_mass": 0.05}, {}, {}))
        out.append(("valve", z, dict(two_zone=tz, **VALVE), {}, {"buffer_tank_temperature": 45.0}, {"valve_targets": True}))
        out.append(("dhw", z + "-combi", dict(two_zone=tz, dhw=True, **VALVE), {"dhw_combi_tank_enabled": True},
                    {"buffer_tank_temperature": 50.0}, {"buffer_exo": True}))
        out.append(("dhw", z + "-sep", dict(two_zone=tz, dhw=True), {}, {}, {}))
        out.append(("external_heat", z, dict(two_zone=tz), {}, {}, {"ext": True}))
        out.append(("external_heat", z + "-valve", dict(two_zone=tz, **VALVE), {}, {"buffer_tank_temperature": 45.0}, {"ext": True}))
        out.append(("pv", z, dict(two_zone=tz), {}, {}, {"sun": True}))
        out.append(("pv", z + "-valve", dict(two_zone=tz, **VALVE), {}, {"buffer_tank_temperature": 45.0}, {"sun": True}))
    out.append(("valve", "2z-direct-slab", dict(two_zone=True, topology_layout="valve_upper_direct_slab", **VALVE), {},
                {"buffer_tank_temperature": 55.0}, {}))
    out.append(("wood", "2z", dict(two_zone=True, **WOOD), {}, {"buffer_tank_temperature": 40.0, "wood_tank_temperature": 60.0}, {"ext": True}))
    out.append(("wood", "2z-noburn", dict(two_zone=True, **WOOD), {}, {"buffer_tank_temperature": 40.0, "wood_tank_temperature": 70.0}, {}))
    out.append(("coil", "2z", dict(two_zone=True, dhw=True, dhw_wood_coil_enabled=True, **WOOD), {},
                {"buffer_tank_temperature": 40.0, "wood_tank_temperature": 60.0}, {"ext": True}))
    return out


def run_arm(params_kw, attrs, st_over, extras, seed):
    rng = np.random.default_rng(seed)
    p = C.house_params(**params_kw)
    for k, v in attrs.items():
        setattr(p, k, v)
    m = ThermalModel(p)
    st = ThermalState(room_temperature=20.5, slab_temperature=23.0, upper_floor_temperature=20.5,
                      lower_floor_temperature=21.0, buffer_tank_temperature=40.0)
    for k, v in st_over.items():
        setattr(st, k, v)
    out = rng.uniform(-12, 8, N)
    w = WeatherSeries(
        outdoor_temps=out, wind_speeds=rng.uniform(0, 9, N), precipitation=rng.uniform(0, 2, N),
        solar_radiation=(rng.uniform(0, 700, N) if extras.get("sun") else np.zeros(N)),
        humidity=rng.uniform(40, 99, N),
        external_heat_kw=(np.linspace(8, 0, N) if extras.get("ext") else None),
        buffer_exo_kw=(rng.uniform(-3, 4, N) if extras.get("buffer_exo") else None))
    P = rng.uniform(0, p.max_electrical_power, (B, N))
    P[:, ::7] = 0.0
    vt = rng.uniform(19, 26, N) if extras.get("valve_targets") else None
    batch = m.simulate_trajectory_batch(st, P, w, dt_hours=0.25, valve_targets=vt, start_hour=3.0)
    mism, worst = 0, 0.0
    keys = ("room", "slab", "upper", "lower", "buffer", "refused", "wood")
    for b in range(B):
        sc = m.simulate_trajectory(st, P[b], w, dt_hours=0.25, valve_targets=vt, start_hour=3.0)
        for k, s_arr in zip(keys, sc):
            b_arr = batch[k]
            if s_arr is None and b_arr is None:
                continue
            s_arr = np.asarray(s_arr, float)
            bb = np.asarray(b_arr[b], float)
            diff = s_arr != bb
            mism += int(diff.sum())
            if diff.any():
                worst = max(worst, float(np.nanmax(np.abs(s_arr - bb))))
    return mism, worst


def main():
    fix = "--fix-lift" in sys.argv
    fix_e = "--fix-emitter" in sys.argv
    per_level = {}
    with ExitStack() as stack:
        if fix:
            stack.enter_context(mock.patch.object(ThermalModel, "flow_lift_factor", lift_fixed))
        if fix_e:
            stack.enter_context(mock.patch.object(mixing_valve, "emitter_delivery", emitter_fixed))
        for i, (level, label, pk, at, so, ex) in enumerate(arms()):
            m, wv = run_arm(pk, at, so, ex, 1000 + i)
            print(f"arm {level:14s} {label:16s} mismatched_elements={m:6d} max_abs_diff={wv:.6g}")
            agg = per_level.setdefault(level, [0, 0.0])
            agg[0] += m
            agg[1] = max(agg[1], wv)
            if "valve" in level + label or level in ("dhw", "wood", "coil"):
                key = "1z" if label.startswith("1z") else "2z"
                per_level.setdefault("_zone_" + key, [0, 0.0])[0] += m
    tot = 0
    for level in ("space_only", "dhw", "valve", "wood", "coil", "external_heat", "pv"):
        m, wv = per_level[level]
        tot += m
        C.result(f"batch_parity_mismatch[{level}]", m, "elements")
        C.result(f"batch_parity_maxdiff[{level}]", f"{wv:.6g}", "K")
    C.result("batch_parity_mismatch_total", tot, "elements")
    C.result("batch_parity_mismatch_1z_valve_arms", per_level["_zone_1z"][0], "elements")
    C.result("batch_parity_mismatch_2z_valve_arms", per_level["_zone_2z"][0], "elements")
    C.result("perturbation_fix_lift", int(fix))
    C.result("perturbation_fix_emitter", int(fix_e))
    C.trailer()


if __name__ == "__main__":
    main()
