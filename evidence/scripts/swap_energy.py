"""Reviewer's driver (my own, not the fixer's): owner's nameplates (finder probe CFG), store written by
the production coordinator with indoor=sensor.t6, lower=sensor.floor_old, scale 1.2356 / ratio 1.943,
n=400; reload under an options variant; feed the reloaded learners into the finder's solve()."""
import asyncio, sys, os
WT = os.path.abspath(sys.argv[1])
sys.argv = [sys.argv[0], WT]
sys.path[:0] = [os.path.dirname(__file__)]
import probe  # finder's harness, adds WT paths
from harness import FakeEntry, FakeHass
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord

class Store:
    def __init__(s): s.saved=None; s.saves=0
    async def async_save(s,d): s.saved=d; s.saves+=1
    async def async_load(s): return s.saved
    async def async_wait_for_read(s): return None

BASE = dict(probe.CFG, indoor_temp_entity="sensor.t6", lower_floor_temp_entity="sensor.floor_old",
            outdoor_temp_entity="sensor.out")
def mk(cfg, st):
    c = Coord(FakeHass({}), FakeEntry(data=cfg)); c._thermal_learning_store = st; return c
def written(legacy=False):
    st = Store(); c = mk(BASE, st)
    c._apply_house_heat_loss_scale(1.2356); c._apply_lower_floor_loss_ratio(1.943)
    c._house_heat_loss_samples = c._lower_floor_loss_samples = 400
    asyncio.run(c._async_save_thermal_learning())
    if legacy: st.saved.pop("heat_loss_zone_entities", None)
    st.saves = 0
    return st
def reload(cfg, legacy=False):
    st = written(legacy); c = mk(cfg, st)
    asyncio.run(c._async_load_thermal_learning())
    return c, st
ARMS = [
  ("unchanged", BASE),
  ("finder swap: indoor=bthome, lower=t6", dict(BASE, indoor_temp_entity="sensor.bthome", lower_floor_temp_entity="sensor.t6")),
  ("indoor only", dict(BASE, indoor_temp_entity="sensor.bthome")),
  ("lower only", dict(BASE, lower_floor_temp_entity="sensor.t6")),
  ("null: outdoor sensor", dict(BASE, outdoor_temp_entity="sensor.out2")),
  ("null: comfort_weight", dict(BASE, comfort_weight=3.0)),
  ("lower removed", {k:v for k,v in BASE.items() if k!="lower_floor_temp_entity"}),
]
if __name__ == "__main__":
    for legacy in (False, True):
        for name, cfg in ARMS:
            c, st = reload(cfg, legacy)
            s, r = c._house_heat_loss_scale, c._lower_floor_loss_ratio
            d = probe.solve(probe.CFG, {"house_heat_loss_scale": s, "lower_floor_loss_ratio": r}, 22.0)
            tag = "legacy-store " if legacy else ""
            print(f"RESULT {tag}{name:<38} scale={s:.4f} ratio={r:.4f} n=({c._house_heat_loss_samples},{c._lower_floor_loss_samples}) saves={st.saves} plan_kWh={d['kwh']:.2f} UA={d['ua']:.3f}")
