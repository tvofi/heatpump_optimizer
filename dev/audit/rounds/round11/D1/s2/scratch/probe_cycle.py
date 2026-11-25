import os, sys, time, asyncio, logging
for _t in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")
sys.path[:0] = ["tests", "tests/hastub", "custom_components"]
from harness import FakeHass, FakeEntry, FakeState
from heatpump_optimizer import const
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
logging.basicConfig(level=logging.WARNING)
hass = FakeHass()
hass.states.set("sensor.indoor", FakeState("21.4"))
hass.states.set("sensor.outdoor", FakeState("-3.0"))
cfg = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor", const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor", const.CONF_DHW_TANK_VOLUME: 180.0}
coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))
from datetime import timedelta
from homeassistant.util import dt as dtu
async def _prices():
    s0 = dtu.now().replace(minute=0, second=0, microsecond=0)
    coord._prices = [{"total": round(0.6 + 0.5*(h%12)/12, 4), "starts_at": (s0+timedelta(hours=h)).isoformat(), "level":"NORMAL"} for h in range(-2, 36)]
coord._fetch_tibber_prices = _prices
for i in range(3):
    t=time.process_time(); w=time.time()
    try:
        d = asyncio.run(coord._async_update_data())
        print("ok", i, type(d), len(d) if d else None, "cpu", time.process_time()-t, "wall", time.time()-w)
    except Exception as e:
        print("EXC", i, type(e).__name__, e, "cpu", time.process_time()-t)
print("last_update_success", getattr(coord, "last_update_success", None))
print(sorted(d)[:200]); print(d.get("plan_stale"), d.get("current_action"))
