"""r10-live-plan-energy probe: rebuild the owner's two-zone solve through the production path."""
import sys, math
from dataclasses import replace
from datetime import datetime
import numpy as np
WT = sys.argv[1]
sys.path[:0] = [f"{WT}/tests/hastub", f"{WT}/custom_components", f"{WT}/tests"]
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from profiles import solve_inputs
from heatpump_optimizer import const as C
SZ = {"two_zone_mode": C.TWO_ZONE_MODE_OFF}

START = datetime(2026, 10, 30, 18, 45)
N = 96
hours = np.array([(START.hour + START.minute / 60 + i * 0.25) % 24 for i in range(N)])
# SE3 late-October shape, SEK/kWh incl. grid fee + tax (~2.3 avg, matching 152.84/66.71)
spot = np.interp(hours, [0, 3, 5, 7, 9, 12, 15, 17, 19, 21, 23, 24],
                 [0.45, 0.35, 0.40, 1.30, 1.50, 0.90, 0.85, 1.40, 1.80, 1.10, 0.60, 0.45])
PRICE = spot + 1.15
OUT = 6.0 + 2.0 * np.cos((hours - 14) / 24 * 2 * np.pi)   # 4..8 °C, median 6

CFG = {
    "target_temperature": 18.0, "comfort_temp_day": 19.5, "comfort_temp_night": 18.5,
    "min_temperature": 18.0, "max_temperature": 21.0, "comfort_weight": 2.0,
    "two_zone_mode": C.TWO_ZONE_MODE_ON, "upper_floor_area_ratio": 0.5, "inter_zone_heat_transfer": 0.5,
    "house_heat_loss_coefficient": 0.4, "lower_floor_heat_loss": 0.2, "upper_floor_heat_loss": 0.13,
    "lower_floor_thermal_mass": 1.0, "upper_floor_thermal_mass": 1.26,
    "slab_thermal_mass": 1.0, "slab_heat_transfer": 1.5,
}
SETUP = {"house_heat_loss_coefficient": 0.15, "lower_floor_heat_loss": 0.07, "upper_floor_heat_loss": 0.08,
         "lower_floor_thermal_mass": 5.0, "upper_floor_thermal_mass": 3.0,
         "slab_thermal_mass": 2.0, "slab_heat_transfer": 0.8}
LEARNED = {"house_heat_loss_scale": 1.2356, "lower_floor_loss_ratio": 1.943}

def solve(cfg, learned, room=22.0, lower=None, slab=None, price=PRICE, out=OUT, margins=None):
    opt_cfg = OptimizationConfig.from_mapping(cfg)
    p = ThermalParameters.from_config(cfg)
    p = replace(p, **learned)        # coordinator _publish_params path
    m = ThermalModel(p)
    lower = room - 1.0 if lower is None else lower
    st = ThermalState(room_temperature=room, outdoor_temperature=float(out[0]),
                      upper_floor_temperature=room, lower_floor_temperature=lower,
                      slab_temperature=lower + 1.0 if slab is None else slab)
    r = HeatPumpOptimizer(m, opt_cfg).optimize(inputs=solve_inputs(
        initial_state=st, prices=price, outdoor_temps=out, start_time=START,
        min_temp_margins=margins))
    pw = np.asarray(r.power_schedule, float)
    on = pw > 1e-3
    slots = int(np.sum(on[1:] & ~on[:-1]) + on[0])
    def tr(name):
        v = getattr(r, name, None)
        return np.asarray(v, float) if v is not None and len(v) else None
    ua = (p.upper_floor_heat_loss + p.lower_floor_heat_loss_learned) * p.house_heat_loss_scale if p.two_zone_enabled \
        else p.heat_loss_coefficient * p.house_heat_loss_scale
    return dict(kwh=float(pw.sum() * 0.25), cost=float(r.predicted_cost), slots=slots, on=int(on.sum()),
                ua=ua, two=p.two_zone_enabled, reason=(getattr(r,"predictive_info",None) or {}).get("space_reason"),
                room=tr("room_temp_trajectory"), up=tr("upper_temp_trajectory"),
                lo=tr("lower_temp_trajectory"), slab=tr("slab_temp_trajectory"), pw=pw,
                maxkw=p.max_electrical_power, cop=float(np.mean([m.compute_cop(float(t)) for t in out])), status=getattr(r, "status", None))

def fmt(x):
    return "-" if x is None else f"{x.min():.1f}/{np.median(x):.1f}/{x.max():.1f}"

ARMS = [
    ("1 as configured, indoor 22", lambda: solve(CFG, LEARNED, 22.0)),
    ("2 indoor 20", lambda: solve(CFG, LEARNED, 20.0)),
    ("3 setup heat-loss/mass values + learned", lambda: solve({**CFG, **SETUP}, LEARNED, 22.0)),
    ("3b setup values, learning reset", lambda: solve({**CFG, **SETUP}, {}, 22.0)),
    ("4 configured, no learned scale/ratio", lambda: solve(CFG, {}, 22.0)),
    ("4b single-zone UA=0.4, no scale", lambda: solve({**CFG, **SZ}, {}, 22.0)),
    ("5 single-zone UA=0.4 x1.2356", lambda: solve({**CFG, **SZ}, {"house_heat_loss_scale": 1.2356}, 22.0)),
    ("5b single-zone UA=0.6409 (learned effective)", lambda: solve({**CFG, **SZ, "house_heat_loss_coefficient": 0.6409}, {}, 22.0)),
    ("6a margins at cap 0.8 (on, worst)", lambda: solve(CFG, LEARNED, 22.0, margins=np.full(N, 0.8))),
    ("6 margins off (=1)", lambda: solve(CFG, LEARNED, 22.0)),
    ("7 null: flat price", lambda: solve(CFG, LEARNED, 22.0, price=np.full(N, float(PRICE.mean())))),
    ("7b flat price, flat 6 °C", lambda: solve(CFG, LEARNED, 22.0, price=np.full(N, float(PRICE.mean())), out=np.full(N, 6.0))),
    ("s1 scale only (ratio 1)", lambda: solve(CFG, {"house_heat_loss_scale": 1.2356}, 22.0)),
    ("s2 ratio only (scale 1)", lambda: solve(CFG, {"lower_floor_loss_ratio": 1.943}, 22.0)),
    ("s3 outdoor 3 °C mean", lambda: solve(CFG, LEARNED, 22.0, out=OUT - 3.0)),
    ("s4 outdoor 9 °C mean", lambda: solve(CFG, LEARNED, 22.0, out=OUT + 3.0)),
    ("x cold lower floor 18, slab 18", lambda: solve(CFG, LEARNED, 22.0, lower=18.0, slab=18.0)),
]
if __name__ == "__main__":
    print(f"{'arm':<46}{'kWh':>7}{'cost':>8}{'slots':>6}{'on':>4}{'UA':>7}  reason  room  upper  lower  slab (min/med/max)")
    for name, f in ARMS:
        d = f()
        print(f"{name:<46}{d['kwh']:7.2f}{d['cost']:8.2f}{d['slots']:6d}{d['on']:4d}{d['ua']:7.3f}  {d['reason']}  "
              f"{fmt(d['room'])}  {fmt(d['up'])}  {fmt(d['lo'])}  {fmt(d['slab'])}  cop~{d['cop']:.2f} two={d['two']}")
