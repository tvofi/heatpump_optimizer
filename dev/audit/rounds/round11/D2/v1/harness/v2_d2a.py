"""D2-v1 V2 independent harness (box V5) for D2-s1-01/-02/-51, D2-s2-01/-02/-03.

Run from the planted-export copy root:
  PYTHONPATH=tests/hastub python3 $HOME/vout/D2-v1/harness/v2_d2a.py
"""
import asyncio
import math
import os
import sys
import time
from unittest import mock

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
sys.path.insert(0, os.path.expanduser("~/vout/D17-v1/harness"))
import myrig  # noqa: E402  (path setup + own coordinator rig)
from heatpump_optimizer import const, defrost, mixing_valve, presets  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402
from heatpump_optimizer.entry_config import EntryConfig  # noqa: E402

c0, t0 = time.process_time(), time.thread_time()

# ---- lift: my own Carnot ratio  C(T)=(T+273.15)/(T-To); physical factor C(flow)/C(ref) (<1 above ref)
p = ThermalParameters()
m = ThermalModel(p)
ref = p.cop_flow_reference_temp
over1 = n = 0
worst = 0.0
for of in range(-25, 16):
    for ff in range(int(ref) + 1, 71):
        f = m.flow_lift_factor(float(of), float(ff))
        n += 1
        over1 += f > 1.0 + 1e-12
        worst = max(worst, f)
c = lambda T, To: (T + 273.15) / max(T - To, 1.0)  # noqa: E731
print(f"RESULT lift ref={ref} grid flow {int(ref)+1}..70 x outdoor -25..15: factor>1 in {over1} of {n}; max {worst:.4f}")
print(f"RESULT lift at outdoor 0, flow 60: production {m.flow_lift_factor(0.0, 60.0):.4f}; own Carnot ratio C(60)/C(ref) {c(60, 0) / c(ref, 0):.4f}")

# ---- reach: count flow_lift_factor calls >1 during a real coordinator solve with a DHW tank
orig = ThermalModel.flow_lift_factor
calls = {"n": 0, "over": 0}


def rec(self, o, fl):
    r = orig(self, o, fl)
    calls["n"] += 1
    calls["over"] += r > 1.0 + 1e-12
    return r


async def solve_reach():
    myrig.freeze()
    with mock.patch.object(ThermalModel, "flow_lift_factor", rec):
        hass, entry, cd = await myrig.setup(myrig.base_data(**{const.CONF_DHW_TANK_VOLUME: 200.0}))
        await myrig.solve(cd)
asyncio.run(solve_reach())
print(f"RESULT lift_reach real coordinator solve (DHW 200 l, default plant): calls={calls['n']} factor>1={calls['over']}")

# ---- emitter_delivery sign
neg = tot = 0
for mix in range(15, 61, 5):
    for zone in range(15, 26):
        d = mixing_valve.emitter_delivery(mix_temp=float(mix), zone_temp=float(zone), ua=0.2)
        tot += 1
        neg += d < 0
print(f"RESULT emitter grid mix 15..60 x zone 15..25 ua 0.2: negative deliveries {neg} of {tot}; "
      f"e.g. mix 15 zone 22 -> {mixing_valve.emitter_delivery(mix_temp=15.0, zone_temp=22.0, ua=0.2):+.3f} kW")

# ---- defrost derate
for d in (0.0, 0.05, 0.1, 0.2, 0.3):
    print(f"RESULT defrost duty={d}: derate_from_duty={defrost.derate_from_duty(d):.3f} ; capacity-loss law 1-1.5*d={max(0.55, 1 - 1.5 * d):.3f}")

# ---- presets era order (own cells: every structure x foundation x area 100/200, both emitters)
inv = cells = 0
ratios = []
for st in presets.STRUCTURES if hasattr(presets, "STRUCTURES") else (presets.STRUCTURE_TIMBER_SLAB,):
    for fd in presets.FOUNDATIONS if hasattr(presets, "FOUNDATIONS") else (presets.FOUNDATION_NONE,):
        for area in (100.0, 200.0):
            for emi in presets.EMITTERS:
                vals = []
                for era in presets.ERAS:
                    bp = presets.BuildingPreset(structure=st, era=era, foundation=fd, heated_area_m2=area,
                                                upper_emitter=emi, lower_emitter=emi)
                    vals.append(presets.derive(bp)[const.CONF_HOUSE_HEAT_LOSS_COEFFICIENT])
                cells += 1
                le, p05 = vals[presets.ERAS.index(presets.ERA_LOW_ENERGY)], vals[presets.ERAS.index(presets.ERA_POST_2005)]
                inv += le >= p05
                ratios.append(le / p05)
print(f"RESULT presets low_energy loss >= post_2005 loss in {inv} of {cells} cells; ratio {min(ratios):.3f}..{max(ratios):.3f}")

# ---- clamp per declared modulation
for mode in ("on_off", "modulating", "auto"):
    ec = EntryConfig.from_mapping({const.CONF_COMPRESSOR_MODULATION: mode})
    print(f"RESULT clamp compressor_modulation={mode}: clamp_planned_levels={getattr(ec, 'clamp_planned_levels', 'n/a')}")

pc, tc = time.process_time() - c0, time.thread_time() - t0
print(f"RESULT thread_factor={pc / tc if tc else 1:.3f} load1={os.getloadavg()[0]:.2f}")
