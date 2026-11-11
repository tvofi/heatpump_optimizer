"""P1 sweep probe: _current_spot_price reads the list head for startless Tibber rows.

Feeds 96 quarter rows with no startsAt through the real _fetch_tibber_prices,
then asks _current_spot_price at a clock 12:00 local-UTC. The quarter that
covers 12:00 is row 48; the seam returns row 0's price.
RESULT spot_wrong=1 (bug present) / 0 under --perturb (rows without a parseable
startsAt refused at prices_from_tibber_payload, the finding's own fix shape).
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-P1/probe_spot_head.py [--perturb]
"""
import asyncio, sys
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
from harness import FakeHass, FakeEntry
from heatpump_optimizer import coordinator as C, price_model as PM
from homeassistant.helpers.update_coordinator import UpdateFailed

if "--perturb" in sys.argv:
    _o = PM.prices_from_tibber_payload
    def _s(d):
        out = _o(d)
        if isinstance(out, list):
            ok = []
            for r in out:
                try: datetime.fromisoformat(str(r["starts_at"])); ok.append(r)
                except ValueError: pass
            out = ok or "no usable rows"
        return out
    PM.prices_from_tibber_payload = _s

class R:
    status = 200
    def __init__(s, b): s.b = b
    async def __aenter__(s): return s
    async def __aexit__(s, *a): return False
    async def json(s): return s.b
class S:
    def __init__(s, b): s.b = b
    def post(s, *a, **k): return R(s.b)

mid = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
rows = [{"total": 1.0 + i / 100, "level": "NORMAL"} for i in range(96)]
body = {"data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": {"today": rows, "tomorrow": []}}}]}}}
c = C.HeatPumpOptimizerCoordinator(FakeHass({}), FakeEntry(data={"tibber_token": "x",
    "weather_entity": "weather.home", "indoor_temp_entity": "sensor.i", "outdoor_temp_entity": "sensor.o"}))
C.async_get_clientsession = lambda h: S(body)
async def go():
    try: await c._fetch_tibber_prices()
    except UpdateFailed: pass
asyncio.run(go())
noon = mid + timedelta(hours=12)
C.dt_util.now = lambda *a, **k: noon
got = c._current_spot_price() if c._prices else None
print(f"# admitted={len(c._prices)} spot_at_noon={got} true={rows[48]['total']}")
print(f"RESULT spot_wrong={int(got is not None and abs(got - rows[48]['total']) > 1e-9)} count")
