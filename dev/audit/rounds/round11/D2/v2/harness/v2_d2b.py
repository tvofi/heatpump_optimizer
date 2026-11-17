"""D2-v2 V2 independent harness (box V5) for D2-s3-01..09 (function level + own coordinator reach).

Run from the planted-export copy root:
  HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 $HOME/vout/D2-v2/harness/v2_d2b.py
"""
import asyncio
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from zoneinfo import ZoneInfo

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
sys.path.insert(0, os.path.expanduser("~/vout/D17-v1/harness"))
import myrig  # noqa: E402
import numpy as np  # noqa: E402
from harness import FakeState  # noqa: E402
from heatpump_optimizer import const, grid_fee, inputs, ledger, price_model, tariff  # noqa: E402

c0, t0 = time.process_time(), time.thread_time()
SE = ZoneInfo("Europe/Stockholm")


def R(*a):
    print("RESULT", *a)


# ---- s3-02: minor units
bad = 0
for unit, val, want in (("öre/kWh", 150.0, 1.50), ("c/kWh", 25.0, 0.25), ("cent/kWh", 25.0, 0.25),
                        ("p/kWh", 30.0, 0.30), ("öre/MWh", 150000.0, 1.50), ("SEK/kWh", 1.5, 1.5),
                        ("EUR/MWh", 80.0, 0.08), ("kr/kWh", 1.2, 1.2)):
    got = inputs.normalize_price_per_kwh(val, unit)
    ok = got is not None and abs(got - want) < 1e-9
    bad += not ok
    R(f"s3-02 {val} {unit} -> {got} (want {want}) {'ok' if ok else 'WRONG'}")
R(f"s3-02 wrong={bad} of 8 (5 minor, 3 major)")

# ---- s3-03: tibber today + tomorrow
day0 = datetime(2026, 2, 3, 0, 0, tzinfo=SE)
rows = lambda d: [{"total": 1.0 + 0.01 * q, "startsAt": (d + timedelta(minutes=15 * q)).isoformat(), "level": "NORMAL"} for q in range(96)]  # noqa
payload = {"data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": {"today": rows(day0), "tomorrow": rows(day0 + timedelta(days=1))}}}]}}}
out = price_model.prices_from_tibber_payload(payload)
R(f"s3-03 tibber rows in=192 out={len(out) if isinstance(out, list) else out!r}; tomorrow rows kept={sum(1 for r in out if str(r['starts_at'])[:10] == '2026-02-04') if isinstance(out, list) else 'n/a'}")

# ---- s3-04: grid-fee weekday
rules = grid_fee.parse_rules("= 0.05, Mon-Fri 07:00-21:00 = 0.30, Sat-Sun = 0.12")
wrong = 0
per_day = {}
mon = datetime(2026, 2, 2, 0, 0, tzinfo=SE)
for q in range(7 * 96):
    t = mon + timedelta(minutes=15 * q)
    applies = [r.applies(t) for r in rules]
    # my own expectation from calendar weekday names
    wk = t.weekday() < 5
    hr = t.hour + t.minute / 60
    exp_rules = [True, wk and 7 <= hr < 21, not wk]
    if applies != exp_rules:
        wrong += 1
        per_day[t.strftime("%a")] = per_day.get(t.strftime("%a"), 0) + 1
R(f"s3-04 rule-applies mismatches {wrong} of 672 quarter steps; by day {per_day}; parse_day_range('Mon-Fri')={sorted(grid_fee.parse_day_range('Mon-Fri'))}")

# ---- s3-05: _one_per_day keeps per-day max?
ranked = [(4.0, "2026-02-03"), (1.0, "2026-02-03"), (3.0, "2026-02-04"), (0.5, "2026-02-04"), (2.0, "")]
kept = tariff._one_per_day(ranked)
R(f"s3-05 _one_per_day({ranked}) -> {sorted(kept)} ; documented per-day highest -> [(2.0,''),(3.0,'2026-02-04'),(4.0,'2026-02-03')]")

# ---- s3-06: _exact_topk_sum
ex = np.array([0.1, 5.0, 0.2, 3.0, 0.0, 4.0])
R(f"s3-06 _exact_topk_sum({ex.tolist()}, 3) = {tariff._exact_topk_sum(ex, 3)} ; k largest = {float(np.sort(ex)[-3:].sum())}")

# ---- s3-07: month hours across DST (my own: real elapsed hours in the zone)
for y, mth in ((2026, 3), (2026, 10), (2026, 1)):
    a = datetime(y, mth, 1, tzinfo=SE)
    b = datetime(y + (mth == 12), mth % 12 + 1, 1, tzinfo=SE)
    real = (b.astimezone(timezone.utc) - a.astimezone(timezone.utc)).total_seconds() / 3600
    mh = ledger.month_hours(datetime(y, mth, 15, tzinfo=SE))
    meta = {ledger.SETTLED_HOURS_META: {"sum": real, "count": 10_000}, ledger.SPOT_PRICE_META: {"count": 1}}
    cf = ledger.coverage_factor(meta, datetime(y, mth, 28, 12, tzinfo=SE))
    R(f"s3-07 {y}-{mth:02d}: month_hours={mh} real={real} coverage_factor(full settle)={cf:.6f}")

# ---- s3-08: ChargeSettle take-back, one-sample vs multi-sample charge
from heatpump_optimizer.dhw_learning import ChargeSettle  # noqa: E402


def run_settle(seq):
    cs = ChargeSettle()
    tot = 0.0
    for heated, settling, drop in seq:
        taken, _ = cs.advance(heated, settling, [None, drop])
        tot += taken
    return tot


short = [(True, False, 4.0), (False, False, -4.0), (False, False, 0.0)]
long_ = [(True, False, 4.0), (True, False, -2.0), (True, False, -2.0), (True, False, -1.0), (False, False, 0.0)]
R(f"s3-08 ChargeSettle dip taken back: one-sample charge {run_settle(short):.2f} K of 4; four-sample charge {run_settle(long_):.2f} K of 4")

# ---- s3-09: DrawRange ceiling store at the floor
from heatpump_optimizer import draw_range  # noqa: E402
try:
    dr = draw_range.DrawRange()
    cmd = SimpleNamespace(written_c=55.0, ceiling_c=55.0)
    acc = dr.takes_ceiling(1.5, cmd)
    for i in range(14):
        dr.observe_ceiling(1.5, 1_000_000.0 + 900 * i)
    R(f"s3-09 takes_ceiling(1.5 kW at ceiling)={acc}; idle_kw={dr.above_idle_kw()}; learned_max_kw after 14 floor samples={dr.learned_max_kw(1_000_000.0 + 900 * 14)}")
except Exception as e:  # noqa: BLE001
    R(f"s3-09 ERROR {type(e).__name__}: {e}")


# ---- s3-01: own coordinator with a 10-hour price feed (tail guessed) and lambda 0 vs 1
async def risk():
    res = {}
    for lam in (0.0, 1.0):
        myrig.freeze()
        hass = myrig.make_hass(indoor=20.5, outdoor=-6.0)
        hass.states.set("sensor.spot", FakeState("1.0", attributes={"raw_today": myrig.prices(1.0, hours=10)}))
        hass, entry, c = await myrig.setup(myrig.base_data(**{const.CONF_PRICE_RISK_LAMBDA: lam}), hass=hass)
        d = await myrig.solve(c)
        r = c._optimization_result
        s = d["schedule"]
        pub_cost = sum(float(x["power"]) * float(x["price"]) * 0.25 for x in s)
        res[lam] = (d.get("predicted_cost"), d.get("baseline_cost"), d.get("predicted_savings"), pub_cost,
                    [float(x["price"]) for x in s])
    p0, p1 = res[0.0][4], res[1.0][4]
    dp = max(abs(a - b) for a, b in zip(p0, p1))
    for lam, v in res.items():
        R(f"s3-01 lambda={lam}: predicted_cost={v[0]} baseline_cost={v[1]} savings={v[2]} sum(power*published price*dt)={v[3]:.4f}")
    R(f"s3-01 max |published step price(lambda 1) - published step price(lambda 0)| = {dp:.4f} (raw feed identical)")
asyncio.run(risk())


# ---- s3-02 reach: entity priced in öre/kWh through the real coordinator
async def minor_reach():
    for unit, base in (("SEK/kWh", 1.0), ("öre/kWh", 100.0)):
        myrig.freeze()
        hass = myrig.make_hass()
        hass.states.set("sensor.spot", FakeState(str(base), attributes={"raw_today": myrig.prices(base), "unit_of_measurement": unit}))
        hass, entry, c = await myrig.setup(myrig.base_data(), hass=hass)
        d = await myrig.solve(c)
        R(f"s3-02 reach unit={unit} feed {base}: published current_price={d.get('current_price')} first step={d['schedule'][0]['price']}")
asyncio.run(minor_reach())

pc, tc = time.process_time() - c0, time.thread_time() - t0
R(f"thread_factor={pc / tc if tc else 1:.3f} load1={os.getloadavg()[0]:.2f}")
