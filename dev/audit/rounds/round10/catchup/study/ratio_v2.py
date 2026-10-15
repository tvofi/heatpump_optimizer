"""Catch-up verifier V2 for D-1 / D-2 / D-3 (lower-floor learned ratio seams).

Independent of the finder's reparam_sites.py: a SYNTHETIC two-zone house
(tests/profiles.py:house(two_zone=True), learned ratio r and scale s chosen
here, no install data), and independent oracles:

  D-1  oracle = the production ThermalModel's own dynamics: with every store at
       one temperature, no sun, no gains, no wind and no power, the total heat
       leaving the house is -(sum C_i dT_i)/dt over a 1e-4 h step. Metric:
       _space_demand_kw / dynamics_loss - 1.
  D-2  an END-TO-END production experiment: SystemIdentification armed on the
       declared plant (which carries the learned ratio r), stepped through
       sysid.step on a continuous ThermalModel plant whose true scale is
       s_true (and whose ratio equals the declared r), then
       adoption_decision -> the effective UA the coordinator would hold after a
       full-weight adoption, (U + L r) * decision.scale, against the plant's
       true effective UA (U + L r) * s_true. Metric: adopted / truth - 1, at
       r and at r = 1 (null); the claim predicts +(U+Lr)/(U+L)-1 at r.
  D-3  options-edit paths through the production store round trip
       (_async_save_thermal_learning -> new coordinator on the edited entry
       -> _async_load_thermal_learning): metric = lower-zone effective loss
       after reload / before - 1, for (a) an edit that touches no nameplate
       (null), (b) a lower-nameplate edit to the learned lower value L*r
       with the upper untouched.

Command (tree root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/catchup/study/ratio_v2.py [--ratio 1.6] [--scale 1.3]
Expected: D-1 at r=1.6: -(L(r-1))/(U+Lr) = -0.2093 (U=.10, L=.09); at r=1: 0.
    D-2 at r: equal to the r=1 arm within the fit noise if the fit and the
    adoption share the (U+L) basis; +0.2093*... if the claim holds.
    D-3 (a) 0; (b) lower effective moves by ~r-1 if the ratio double-applies.
Baseline SHA: d749c986d (production byte-identical to 17f1c55fa / a77faf30d).
Machine: macOS arm64, venv Python 3.14. No timing figure.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import asyncio  # noqa: E402
import copy  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from dataclasses import replace  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass  # noqa: E402
from profiles import house  # noqa: E402

from heatpump_optimizer import sysid  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.sysid import HousePlant, SysIdConfig, SystemIdentification  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402


class MemStore:
    def __init__(self, data=None):
        self.data = copy.deepcopy(data)

    async def async_load(self):
        return copy.deepcopy(self.data)

    async def async_save(self, data):
        self.data = copy.deepcopy(data)

    async def async_wait_for_read(self):
        return None


def cfg_two_zone():
    c = house(two_zone=True, dhw=False, buffer_tank_volume=0.0)
    c["lower_floor_temp_entity"] = "sensor.synthetic_lower"
    return c


def coord(cfg, store=None):
    c = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
    c._thermal_learning_store = store or MemStore({})
    return c


def dynamics_loss_kw(params, t_in, t_out):
    """Heat leaving the house per the model's own dynamics (all stores at t_in)."""
    p = replace(params, internal_gains=0.0, wind_sensitivity=0.0)
    m = ThermalModel(p)
    st = ThermalState(room_temperature=t_in, slab_temperature=t_in, outdoor_temperature=t_out,
                      upper_floor_temperature=t_in, lower_floor_temperature=t_in,
                      buffer_tank_temperature=t_in)
    dt = 1e-4
    nx = m.simulate_step(st, 0.0, t_out, dt_hours=dt)
    de = (p.upper_floor_thermal_mass * (nx.upper_floor_temperature - t_in)
          + p.lower_floor_thermal_mass * (nx.lower_floor_temperature - t_in)
          + p.slab_thermal_mass * (nx.slab_temperature - t_in))
    return -de / dt


def d1(r, s):
    cfg = cfg_two_zone()
    c = coord(cfg)
    c._apply_house_heat_loss_scale(s)
    c._apply_lower_floor_loss_ratio(r)
    c._current_state = ThermalState(room_temperature=21.0, outdoor_temperature=-5.0)
    sd = c._space_demand_kw()
    oracle = dynamics_loss_kw(c._thermal_params, 21.0, -5.0)
    return sd, oracle


def d2(r, s_true, seed_name="d2"):
    """One production experiment night on the synthetic two-zone house."""
    night = datetime(2026, 1, 15, 23, 0, tzinfo=timezone.utc)
    cfg = cfg_two_zone()
    declared = ThermalParameters.from_config(cfg)
    declared.wind_sensitivity = 0.0
    declared.lower_floor_loss_ratio = r
    declared.dhw_enabled = False
    plant = ThermalModel(replace(declared, house_heat_loss_scale=s_true))
    cop = plant.compute_cop(0.0)
    true_eff = (declared.upper_floor_heat_loss + declared.lower_floor_heat_loss * r) * s_true
    hold = max(true_eff * 21.0 - declared.internal_gains, 0.1) / cop
    st = ThermalState(room_temperature=21.0, upper_floor_temperature=21.0, lower_floor_temperature=21.0,
                      slab_temperature=24.0, outdoor_temperature=0.0, buffer_tank_temperature=35.0)
    for _ in range(2400):
        st = plant.simulate_step(st, electrical_power=hold, outdoor_temp=0.0)
    sid = SystemIdentification(SysIdConfig(enabled=True, min_days_between_runs=0.0))
    armed = sid.arm(night, plant=declared)
    if not armed:
        return None, sid.result.reason, true_eff
    when = night
    while sid.active:
        reading = st.upper_floor_temperature
        override = sid.step(
            now=when, room_temp=reading, outdoor_temp=0.0, price=0.1,
            price_horizon=np.full(48, 1.0), learner_samples=0,
            max_power_kw=declared.max_electrical_power, cop=cop, plan_power_kw=hold,
            house=HousePlant(ua=declared.heat_loss_coefficient * declared.house_heat_loss_scale,
                             capacity=declared.room_thermal_mass, gains=declared.internal_gains,
                             slab_mass=declared.slab_thermal_mass, slab_transfer=declared.slab_heat_transfer),
        )
        el = hold if override is None else float(override)
        for _ in range(15):
            st = plant.simulate_step(st, electrical_power=el, outdoor_temp=0.0, dt_hours=1.0 / 60)
        when += timedelta(minutes=15)
    dec = sysid.adoption_decision(sid.result, declared, sid.config)
    adopted_eff = (declared.upper_floor_heat_loss + declared.lower_floor_heat_loss * r) * dec.scale
    return dec, sid.result, true_eff, adopted_eff


def d3(r, s, edit):
    cfg = cfg_two_zone()
    U, L = cfg["upper_floor_heat_loss"], cfg["lower_floor_heat_loss"]
    src = coord(cfg)
    src._apply_house_heat_loss_scale(s)
    src._apply_lower_floor_loss_ratio(r)
    src._house_heat_loss_samples, src._lower_floor_loss_samples = 400, 200
    asyncio.run(src._async_save_thermal_learning())
    before_lower = L * r * s
    before_upper = U * s
    if edit == "no_nameplate":
        new = dict(cfg, target_temperature=cfg["target_temperature"] + 0.5)
    elif edit == "lower_to_learned_split":
        new = dict(cfg, lower_floor_heat_loss=L * r)
    else:
        raise ValueError(edit)
    dst = coord(new, MemStore(src._thermal_learning_store.data))
    asyncio.run(dst._async_load_thermal_learning())
    p = dst._thermal_params
    lo = p.lower_floor_heat_loss * dst._lower_floor_loss_ratio * dst._house_heat_loss_scale
    up = p.upper_floor_heat_loss * dst._house_heat_loss_scale
    return lo / before_lower - 1.0, up / before_upper - 1.0, (lo + up) / (before_lower + before_upper) - 1.0, \
        dst._house_heat_loss_scale, dst._lower_floor_loss_ratio


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ratio", type=float, default=1.6)
    ap.add_argument("--scale", type=float, default=1.3)
    a = ap.parse_args()
    c0, t0 = time.process_time(), time.thread_time()
    for r in (a.ratio, 1.0):
        sd, orc = d1(r, a.scale)
        print(f"RESULT D1.r{r:.3f}.space_demand_vs_dynamics={sd / orc - 1.0:+.4f}  ({sd:.3f} vs {orc:.3f} kW)")
    for r in (a.ratio, 1.0):
        out = d2(r, a.scale)
        if out[0] is None:
            print(f"RESULT D2.r{r:.3f}.not_armed reason={out[1]!r}")
            continue
        dec, res, true_eff, adopted = out
        print(f"RESULT D2.r{r:.3f}.adopted_eff_vs_truth={adopted / true_eff - 1.0:+.4f}  "
              f"(admit {dec.admit} reason {dec.reason!r}; scale {dec.scale:.4f} vs true {a.scale}; "
              f"fit heat_loss_kw_per_c {res.heat_loss_kw_per_c if res.heat_loss_kw_per_c is None else round(res.heat_loss_kw_per_c * 1000, 1)} W/K; "
              f"true effective {true_eff * 1000:.1f} W/K)")
    for r in (a.ratio, 1.0):
        for edit in ("no_nameplate", "lower_to_learned_split"):
            lo, up, tot, sc, rr = d3(r, a.scale, edit)
            print(f"RESULT D3.r{r:.3f}.{edit}.lower_rel={lo:+.4f} upper_rel={up:+.4f} total_rel={tot:+.4f} "
                  f"(scale {sc:.3f} ratio {rr:.3f})")
    tf = (time.process_time() - c0) / max(time.thread_time() - t0, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")


if __name__ == "__main__":
    main()
