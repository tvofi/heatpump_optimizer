"""D1.M3: a price list that stops updating -- the last entry is published and booked as "now" forever.

Metric: over cycles at T0+{5,8,30,50} h, with a price list whose last hourly entry
starts at T0+3 h (so nothing covers now), the count of cycles whose published
`current_price` (coordinator._build_data_dict, via _current_spot_price) is a
finite number, and the count whose settlement pending prediction
(_pending_prediction["price"], what the ledger books) is a finite number.
Key: the values the production seams delivered.
Control: cycles at T0+0 and T0+2 h, where an entry covers now (counted separately).
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D1/s2/stale_price.py [--perturb]
--perturb: in memory, _current_spot_price returns NaN once now is past the last
entry's start + 1 h (a last entry covers one slot, not forever); expected 4 -> 0.
Baseline 17f1c55fad1b; machine Apple-silicon macOS (box B4).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, math, sys, time
from datetime import timedelta, datetime, timezone
sys.path.insert(0, os.path.dirname(__file__))
_a = list(sys.argv); sys.argv = [sys.argv[0], "0", "__none__"]
import store_fuzz as F  # noqa: E402
sys.argv = _a
from harness import FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as cm  # noqa: E402

T0 = datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc)
LAST = T0 + timedelta(hours=3)

if "--perturb" in sys.argv:
    _orig = cm.HeatPumpOptimizerCoordinator._current_spot_price
    def _bounded(self):
        if dt_util.now() >= LAST + timedelta(hours=1):
            return float("nan")
        return _orig(self)
    cm.HeatPumpOptimizerCoordinator._current_spot_price = _bounded


def fin(v):
    return isinstance(v, (int, float)) and math.isfinite(v)


async def main():
    t0 = time.process_time(); tt0 = time.thread_time()
    dt_util.freeze(T0)
    h, c = F.build(); await F.drain(c)
    prices = [{"total": round(1.0 + 0.1 * k, 2), "starts_at": (T0 + timedelta(hours=k)).isoformat(),
               "level": "NORMAL"} for k in range(-2, 4)]
    async def fp():
        c._prices = list(prices)
    c._fetch_tibber_prices = fp
    covered = uncovered_pub = uncovered_book = n_unc = 0
    for hrs in (0, 2, 5, 8, 30, 50):
        t = T0 + timedelta(hours=hrs); dt_util.freeze(t)
        h.states.set("sensor.indoor", FakeState("21.4", last_updated=t, last_reported=t))
        h.states.set("sensor.outdoor", FakeState("-3.0", last_updated=t, last_reported=t))
        err = await F.cycle(c)
        data = c._build_data_dict()
        pub = data.get("current_price")
        book = (c._pending_prediction or {}).get("price")
        print(f"  t+{hrs}h err={err} current_price={pub} booked={book}")
        if t < LAST + timedelta(hours=1):
            covered += fin(pub)
        else:
            n_unc += 1
            uncovered_pub += fin(pub)
            uncovered_book += fin(book)
    dt_util.freeze(None)
    print(f"RESULT uncovered_cycles={n_unc} count")
    print(f"RESULT uncovered_current_price_published={uncovered_pub} count")
    print(f"RESULT uncovered_price_booked={uncovered_book} count")
    print(f"RESULT control_covered_published={covered} count")
    tf = (time.process_time() - t0) / max(1e-9, time.thread_time() - tt0)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")

asyncio.run(main())
