#!/usr/bin/env python3
"""V2 (D1-2) own harness for D1-s5-02: finite out-of-domain learner-store fields, exhaustive
single-field corruptions routed through store.QuarantiningStore.async_load (the production
boundary, which scrubs only non-finite leaves) into PriceShapeModel.from_dict / PeakTracker.from_dict.

Metric P (price model): of the enumerated single-field corruptions of a model trained on 28 days,
  count whose extend_price_series tail (48 h, 12 h known) differs from the healthy twin's tail by
  more than 2x at any guessed step (or is <= 0 / non-finite), with no WARNING logged;
  and the same count after 1 and after 14 further observed days (observe_day + observe_day_quarters).
Metric K (peak tracker; base months with 3 days and with 1 day of real peaks): of the enumerated corruptions, count whose threshold_kw or billed_peak_kw
  is negative or > 1000 kW at load (before any observe), after one in-window observe() (the next cycle), and after 3 closed
  real windows of 5 kW on 3 days.
Null: the unmutated payload through the same path: 0 in both.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/u2_store_domain.py
Expected (exact, deterministic): see RESULT lines.
Baseline SHA 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, copy, logging, math, sys, time
from datetime import datetime, timedelta, timezone
sys.path[:0] = [".", "tests", "tests/hastub"]
p0, t0 = time.process_time(), time.thread_time()
import numpy as np  # noqa: E402
from homeassistant.helpers import storage as S  # noqa: E402
from custom_components.heatpump_optimizer import price_model as PM  # noqa: E402
from custom_components.heatpump_optimizer import tariff as TF  # noqa: E402
from custom_components.heatpump_optimizer.store import QuarantiningStore  # noqa: E402


class Warn(logging.Handler):
    n = 0

    def emit(self, r):
        if r.levelno >= logging.WARNING:
            Warn.n += 1


logging.getLogger("custom_components.heatpump_optimizer").addHandler(Warn())
D0 = datetime(2026, 1, 5, 0, 0, tzinfo=timezone.utc)


def day_prices(d):
    return [0.4 + 0.5 * math.sin(math.pi * (h - 5) / 14) ** 2 + 0.02 * ((d * 7 + h) % 5) for h in range(24)]


def train(m, start, days):
    for d in range(days):
        day = start + timedelta(days=d)
        hp = day_prices(d)
        m.observe_day(day, hp)
        m.observe_day_quarters(day, [p * (1.0 + 0.05 * (q - 1.5)) for p in hp for q in range(4)])


async def boundary(payload, key):
    await S.Store(None, 1, key).async_save(payload)
    return await QuarantiningStore(None, 1, key).async_load()


def tail(m, now):
    times = [now + timedelta(minutes=15 * i) for i in range(192)]
    known = [0.4 + 0.3 * math.sin(i / 10.0) ** 2 for i in range(48)]
    pr, mask, sig = PM.extend_price_series(known, 192, times, m)
    return pr[~mask], sig[~mask], float(np.mean(known))


def bad_tail(pr, sig, ref, mean):
    if not (np.all(np.isfinite(pr)) and np.all(np.isfinite(sig))):
        return True
    if np.any(pr <= 0) or np.any(pr > 1000 * mean):
        return True
    return bool(np.any((pr > 2 * ref) | (pr < ref / 2)))


async def price_arm():
    healthy = PM.PriceShapeModel()
    train(healthy, D0, 28)
    base = healthy.as_dict()
    now = D0 + timedelta(days=28, hours=12)
    muts = []
    for p in range(2):
        for h in (3, 17):
            for v in (0.0, -1.0, 50.0, 1e300):
                muts.append(("shapes", p, h, v))
        for q in (12, 70):
            for v in (0.0, -1.0, 1e300):
                muts.append(("quarter_factors", p, q, v))
        for v in (-5, 10 ** 9):
            muts.append(("days", p, None, v))
        muts.append(("residual_var", p, 17, 1e300))
    ref_now = tail(healthy, now)[0]
    h1 = copy.deepcopy(healthy); train(h1, now, 1)
    ref1 = tail(h1, now + timedelta(days=1))[0]
    h14 = copy.deepcopy(healthy); train(h14, now, 14)
    ref14 = tail(h14, now + timedelta(days=14))[0]
    counts = {"load": 0, "silent": 0, "after1": 0, "after14": 0}
    per = {}
    for k, (field, p, i, v) in enumerate(muts):
        pl = copy.deepcopy(base)
        if i is None:
            pl[field][p] = v
        else:
            pl[field][p][i] = v
        w0 = Warn.n
        m = PM.PriceShapeModel.from_dict(await boundary(pl, f"u2p{k}"))
        warned = Warn.n > w0
        pr, sg, mean = tail(m, now)
        b0 = bad_tail(pr, sg, ref_now, mean)
        m1 = copy.deepcopy(m); train(m1, now, 1)
        pr1, sg1, _ = tail(m1, now + timedelta(days=1))
        m14 = copy.deepcopy(m); train(m14, now, 14)
        pr14, sg14, _ = tail(m14, now + timedelta(days=14))
        b1 = bad_tail(pr1, sg1, ref1, mean); b14 = bad_tail(pr14, sg14, ref14, mean)
        counts["load"] += b0; counts["silent"] += b0 and not warned
        counts["after1"] += b1; counts["after14"] += b14
        tag = f"{field}={v!r}"
        per.setdefault(tag, [0, 0, 0]); per[tag][0] += b0; per[tag][1] += b1; per[tag][2] += b14
    print(f"RESULT price.cases={len(muts)} count")
    print(f"RESULT price.bad_tail_on_load={counts['load']} count")
    print(f"RESULT price.bad_tail_on_load_silent={counts['silent']} count")
    print(f"RESULT price.bad_tail_after_1_day={counts['after1']} count")
    print(f"RESULT price.bad_tail_after_14_days={counts['after14']} count")
    for tag, (a, b, c) in per.items():
        print(f"RESULT price.by.{tag}=load:{a},d1:{b},d14:{c} count")
    m = PM.PriceShapeModel.from_dict(await boundary(copy.deepcopy(base), "u2pnull"))
    pr, sg, mean = tail(m, now)
    print(f"RESULT price.null_bad_tail={int(bad_tail(pr, sg, ref_now, mean))} count")


async def peak_arm(ndays):
    tariff = TF.CapacityTariff(enabled=True, price_per_kw=50.0, peaks_averaged=3)
    tr = TF.PeakTracker()
    t = datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc)
    for d in range(ndays):
        for mnt in range(0, 61, 15):
            tr.observe(t + timedelta(days=d, hours=18, minutes=mnt), 4.0 + d, tariff, dt_hours=0.25)
    base = tr.as_dict()
    muts = []
    for i in range(len(base["peaks"])):
        for v in (-5.0, -1e300, 1e300):
            muts.append(("peaks", i, v))
    for f, vals in (("window_sum", (1e300, -1e300)), ("window_samples", (-10, 10 ** 12)),
                    ("window_factor", (-1.0, 1e300)), ("window_wsum", (1e300, -1e300)),
                    ("window_weight", (-1.0,))):
        for v in vals:
            muts.append((f, None, v))
    now = t + timedelta(days=3, hours=18, minutes=5)
    bad0 = bad3 = silent = badload = 0
    per = {}
    for k, (f, i, v) in enumerate(muts):
        pl = copy.deepcopy(base)
        if i is None:
            pl[f] = v
        else:
            pl[f][i] = v
        w0 = Warn.n
        x = TF.PeakTracker.from_dict(await boundary(pl, f"u2k{ndays}_{k}"))
        warned = Warn.n > w0

        def bad(y):
            vals = (y.threshold_kw(tariff), y.billed_peak_kw(tariff))
            return any((not math.isfinite(z)) or z < 0 or z > 1000 for z in vals)
        bl = bad(x); badload += bl
        per.setdefault(f"{f}={v!r}", [0, 0, 0]); per[f"{f}={v!r}"][2] += bl
        x.observe(now, 3.0, tariff, dt_hours=0.25)
        x.observe(now + timedelta(minutes=60), 3.0, tariff, dt_hours=0.25)  # closes the open window
        b0 = bad(x)
        for d in range(4, 7):
            for mnt in range(0, 61, 15):
                x.observe(t + timedelta(days=d, hours=18, minutes=mnt), 5.0, tariff, dt_hours=0.25)
        b3 = bad(x)
        bad0 += b0; bad3 += b3; silent += b0 and not warned
        tag = f"{f}={v!r}"
        per[tag][0] += b0; per[tag][1] += b3
    print(f"RESULT peak{ndays}d.cases={len(muts)} count")
    print(f"RESULT peak{ndays}d.bad_published_next_cycle={bad0} count")
    print(f"RESULT peak{ndays}d.bad_published_next_cycle_silent={silent} count")
    print(f"RESULT peak{ndays}d.bad_after_3_real_windows={bad3} count")
    print(f"RESULT peak{ndays}d.bad_published_at_load={badload} count")
    for tag, (a, b, c) in per.items():
        print(f"RESULT peak{ndays}d.by.{tag}=load:{c},next:{a},after3:{b} count")
    x = TF.PeakTracker.from_dict(await boundary(copy.deepcopy(base), f"u2knull{ndays}"))
    x.observe(now, 3.0, tariff, dt_hours=0.25)
    z = (x.threshold_kw(tariff), x.billed_peak_kw(tariff))
    print(f"RESULT peak{ndays}d.null_bad={int(any(v < 0 or v > 1000 or not math.isfinite(v) for v in z))} count")


asyncio.run(price_arm())
asyncio.run(peak_arm(3))
asyncio.run(peak_arm(1))
p1, t1 = time.process_time(), time.thread_time()
print(f"RESULT thread_factor={(p1 - p0) / max(t1 - t0, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
except Exception:  # noqa: BLE001
    sw = "na"
print(f"RESULT swapins={sw}")
