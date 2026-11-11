"""Verifier V2 for D1-s3-01/02. Metrics: (a) pull_prices verdict and row count on an
HTTP-200 payload with empty today/tomorrow (Tibber post patched); (b) rows admitted
with starts_at=='' from 96 startless rows; (c) for (a), _current_spot_price after
the wipe (0.0 = silent zero price).
Command: PYTHONPATH=tests/hastub:custom_components python3 dev/audit/rounds/round10/D1/v_s3_tibber_own.py"""
import asyncio
from types import SimpleNamespace
from heatpump_optimizer import price_model as pm, coordinator as cm
def home(today, tomorrow): return {"data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": {"today": today, "tomorrow": tomorrow}}}]}}}
async def post(*a, **k): return 200, CUR[0]
pm._tibber_post = post
CUR = [home([], [])]
v, rows = asyncio.run(pm.pull_prices(None, {pm.CONF_PRICE_SOURCE: "tibber", pm.CONF_TIBBER_TOKEN: "x"} if hasattr(pm, "CONF_TIBBER_TOKEN") else {}))
print(f"RESULT empty_payload_verdict={v} rows={len(rows) if isinstance(rows, list) else rows}")
print(f"RESULT spot_after_wipe={cm.HeatPumpOptimizerCoordinator._current_spot_price(SimpleNamespace(_prices=[]))}")
CUR[0] = home([{"total": 1.0 + i / 100, "level": "NORMAL"} for i in range(96)], [])
r = pm.prices_from_tibber_payload(CUR[0])
print(f"RESULT startless_admitted={sum(1 for x in r if x['starts_at'] == '')} of 96")
