"""D1-s3 M6: Tibber price-response ingress under malformed payloads.

Metric (two RESULTs, key = the coordinator's own state after the real fetch):
  empty_ok_wipes   : 1 when a Tibber 200 response with empty today/tomorrow
                     makes HeatPumpOptimizerCoordinator._fetch_tibber_prices
                     replace a 96-row good price list with 0 rows and return
                     success (no UpdateFailed); 0 otherwise.
  startless_rows   : rows the real fetch admits into coordinator._prices whose
                     starts_at cannot be parsed (96-row payload, startsAt absent),
                     and misplaced_steps = horizon steps _known_prices_for fills
                     from a row other than the one whose quarter it is.
Command: PYTHONPATH=tests/hastub ~/hpo-seats/r9fix-lanerunner/bin/python3 \
         dev/audit/rounds/round10/D1/s3/tibber_ingress.py [--perturb]
Expected (baseline): empty_ok_wipes=1, startless_rows=96, misplaced_steps>0 (exact).
--perturb wraps price_model.prices_from_tibber_payload so an empty result or a row
whose startsAt fails datetime.fromisoformat is refused: all three go to 0.
Baseline 17f1c55fad1b, machine: macOS arm64 seat box (counts, contention-immune).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, sys, time
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
from harness import FakeHass, FakeEntry  # noqa: E402
from heatpump_optimizer import coordinator as C, price_model as PM  # noqa: E402
from homeassistant.helpers.update_coordinator import UpdateFailed  # noqa: E402

PERTURB = "--perturb" in sys.argv
if PERTURB:
    _orig = PM.prices_from_tibber_payload
    def _strict(data):
        out = _orig(data)
        if isinstance(out, list):
            ok = []
            for r in out:
                try:
                    datetime.fromisoformat(str(r["starts_at"])); ok.append(r)
                except ValueError:
                    pass
            out = ok or "Tibber returned no usable price rows"
        return out
    PM.prices_from_tibber_payload = _strict

class _Resp:
    def __init__(self, body): self.status, self._b = 200, body
    async def __aenter__(self): return self
    async def __aexit__(self, *a): return False
    async def json(self): return self._b
class _Sess:
    def __init__(self, body): self.body = body
    def post(self, *a, **k): return _Resp(self.body)

def payload(today, tomorrow):
    return {"data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": {
        "current": None, "today": today, "tomorrow": tomorrow}}}]}}}

def coord():
    cfg = {"tibber_token": "x", "weather_entity": "weather.home",
           "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"}
    return C.HeatPumpOptimizerCoordinator(FakeHass({}), FakeEntry(data=cfg))

midnight = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
good = [{"total": 1.0 + i / 100, "startsAt": (midnight + timedelta(minutes=15 * i)).isoformat(),
         "level": "NORMAL"} for i in range(96)]

async def fetch(c, body):
    C.async_get_clientsession = lambda hass: _Sess(body)
    try:
        await c._fetch_tibber_prices(); return "ok"
    except UpdateFailed:
        return "failed"

async def main():
    c = coord()
    r1 = await fetch(c, payload(good, []))
    before = len(c._prices)
    r2 = await fetch(c, payload([], []))
    after = len(c._prices)
    wipes = int(r1 == "ok" and before == 96 and r2 == "ok" and after == 0)
    print(f"# good fetch={r1} rows={before}; empty fetch={r2} rows={after}")
    print(f"RESULT empty_ok_wipes={wipes} count")

    c2 = coord()
    startless = [{"total": g["total"], "level": "NORMAL"} for g in good]
    r3 = await fetch(c2, payload(startless, []))
    bad = sum(1 for e in c2._prices if C._comparable_ts(e.get("starts_at"), midnight) is None)
    steps = [midnight + timedelta(minutes=15 * k) for k in range(96)]
    known = c2._known_prices_for(steps) if c2._prices else []
    mis = sum(1 for k, v in enumerate(known) if abs(v - good[k]["total"]) > 1e-9)
    print(f"# startless fetch={r3} admitted={len(c2._prices)} known_steps={len(known)}")
    print(f"RESULT startless_rows={bad} count")
    print(f"RESULT misplaced_steps={mis} count")

t0p, t0t = time.process_time(), time.thread_time()
asyncio.run(main())
tf = (time.process_time() - t0p) / max(time.thread_time() - t0t, 1e-9)
print(f"RESULT thread_factor={tf:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
