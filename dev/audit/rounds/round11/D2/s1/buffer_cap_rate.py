#!/usr/bin/env python3
"""D2.M1 buffer-cap-rate: the buffer cap clamps a rate, never a state -- per hydronic layout.

For every layout of the `layout` population axis (const.py TOPOLOGY_*), the parameters are
built with that layout stored, and two arms run through ThermalModel.simulate_step (scalar)
and ThermalModel.simulate_trajectory_batch (one row), dt 0.25 h and 1 h, pump at max:
  above  the tank starts 5 K ABOVE buffer_max_temp (the wood tank 5 K above 95 C): the step
         may only discharge it at its physical rate. A state clamp shows as the tank landing
         ON the cap (or below the physical discharge bound) from above.
  cross  the tank starts 0.5 K below the cap: the step must land exactly on the cap and book
         the excess on _step_buffer_refused, sum C*dT + refused*dt equal to the unclamped rise.
Metric: count of (layout, arm, dt, path) cases breaking either rule; plus the resolved layout.
Count key: the buffer/wood temperature the production step returns and its refused ledger.
The DHW store (thermal_model.store_step) is run through the same two arms against its rating.

Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D2/s1/buffer_cap_rate.py
Perturbation (judge): replace the charging-direction clamp in _simulate_step_two_zone with a
state clamp (new_buf = min(new_buf, cap)) -> the `above` count goes up from 0.
Expected at baseline: 0 violations (tolerance 1e-9 K / 1e-9 kWh).
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B4.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import numpy as np  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import thermal_model as TM  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalState, WeatherSeries  # noqa: E402

LAYOUTS = sorted(v for k, v in vars(const).items() if k.startswith("TOPOLOGY_") and isinstance(v, str)
                 and k not in ("TOPOLOGY_LAYOUT",))
BASE = {"mixing_valve_mode": "manual", "buffer_tank_volume": 300.0, "buffer_max_temperature": 60.0}


def params_for(layout):
    over = dict(BASE, topology_layout=layout)
    if layout == const.TOPOLOGY_NO_VALVE:
        over["mixing_valve_mode"] = "none"
    if layout == const.TOPOLOGY_TWO_TANK_4WAY:
        over.update(wood_tank_top_entity="sensor.wood_top", wood_tank_volume=300.0)
    return C.house_params(two_zone=True, **over)


def one(m, st, dt, batch):
    w = WeatherSeries(outdoor_temps=np.array([0.0]), wind_speeds=np.zeros(1), precipitation=np.zeros(1),
                      solar_radiation=np.zeros(1), humidity=None, external_heat_kw=np.array([10.0]))
    P = m.params.max_electrical_power
    if batch:
        r = m.simulate_trajectory_batch(st, np.array([[P]]), w, dt_hours=dt)
        wood = None if r["wood"] is None else float(r["wood"][0, 1])
        return float(r["buffer"][0, 1]), wood, float(r["refused"][0, 0])
    s = m.simulate_step(st, P, 0.0, dt_hours=dt, external_heat_kw=10.0)
    return s.buffer_tank_temperature, s.wood_tank_temperature, m._step_buffer_refused


def main():
    viol, cases, rows = 0, 0, []
    for layout in LAYOUTS:
        p = params_for(layout)
        m = ThermalModel(p)
        resolved = p.topology_layout
        thr = TM.mixing_valve.is_throttling(p.mixing_valve_mode)
        cap = p.buffer_max_temp
        cbuf = TM._buffer_capacity(p)
        ua = TM._valve_ua(p) if thr else 0.0
        for dt in (0.25, 1.0):
            for batch in (False, True):
                wood0 = TM.WOOD_TANK_MAX_TEMP + 5.0 if p.two_tank_modelled else None
                st = ThermalState(room_temperature=20.0, slab_temperature=22.0, upper_floor_temperature=20.0,
                                  lower_floor_temperature=20.0, buffer_tank_temperature=cap + 5.0,
                                  wood_tank_temperature=wood0)
                b, wd, ref = one(m, st, dt, batch)
                cases += 1
                # physical discharge bound: every emitter wide open on the tank, plus its loss
                max_dis = (ua * (cap + 5.0 - 20.0) + p.buffer_tank_heat_loss_coefficient * (cap + 5.0 - 20.0)) / cbuf * dt
                snapped = thr and (b < cap + 5.0 - max_dis - 1e-9 or b > cap + 5.0 + 1e-9)
                wood_snapped = wd is not None and wd < wood0 - (p.wood_tank_heat_loss_coefficient * (wood0 - 20)
                                                                + ua * (wood0 - 20)) / p.wood_tank_thermal_mass * dt - 1e-9
                if snapped or wood_snapped:
                    viol += 1
                rows.append(f"{layout:24s}->{resolved:24s} above dt={dt} {'batch ' if batch else 'scalar'} "
                            f"buf {cap + 5.0:.2f}->{b:.4f} wood {wood0}->{wd} {'VIOLATION' if snapped or wood_snapped else 'ok'}")
                # cross arm
                st = ThermalState(room_temperature=20.0, slab_temperature=22.0, upper_floor_temperature=20.0,
                                  lower_floor_temperature=20.0, buffer_tank_temperature=cap - 0.5,
                                  wood_tank_temperature=(60.0 if p.two_tank_modelled else None))
                b, wd, ref = one(m, st, dt, batch)
                cases += 1
                bad = thr and (b > cap + 1e-9)
                if thr and abs(b - cap) < 1e-9:
                    # the unclamped rise is what the refused ledger plus the realised rise add to
                    bad = bad or ref <= 0.0
                if bad:
                    viol += 1
                rows.append(f"{layout:24s}->{resolved:24s} cross dt={dt} {'batch ' if batch else 'scalar'} "
                            f"buf {cap - 0.5:.2f}->{b:.4f} refused={ref:.4g}kW {'VIOLATION' if bad else 'ok'}")
    # the DHW store against its rating, both arms
    p = C.house_params(dhw=True)
    store = p.dhw_store
    for dt in (0.25, 1.0):
        t0 = store.rating_max_temp + 5.0
        new, refused, inj, draw = TM.store_step(store, t0, 6.0, 0.0, 20.0, dt)
        cases += 1
        if new < t0 - store.ua_kw_per_c * (t0 - 20.0) / store.capacity_kwh_per_c * dt - 1e-9 or new > t0 + 1e-9:
            viol += 1
        rows.append(f"dhw_store above dt={dt} {t0:.2f}->{new:.4f} refused={refused:.4g}")
        t0 = store.rating_max_temp - 0.1
        new, refused, inj, draw = TM.store_step(store, t0, 12.0, 0.0, 20.0, dt)
        cases += 1
        lhs = store.capacity_kwh_per_c * (new - t0) + refused * dt
        rhs = (12.0 - store.ua_kw_per_c * (t0 - 20.0)) * dt
        if new > store.rating_max_temp + 1e-9 or abs(lhs - rhs) > 1e-9:
            viol += 1
        rows.append(f"dhw_store cross dt={dt} {t0:.2f}->{new:.4f} refused={refused:.4g} balance={lhs - rhs:.2e}")
    for r in rows:
        print(r)
    C.result("layouts", len(LAYOUTS))
    C.result("cases", cases)
    C.result("cap_as_state_violations", viol, "cases")
    C.trailer()


if __name__ == "__main__":
    main()
