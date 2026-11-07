import sys, pickle, importlib
root = sys.argv[1]
sys.path[:0] = [root + "/tests/hastub", root + "/custom_components"]
import numpy as np
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from heatpump_optimizer import tariff as T
rng = np.random.default_rng(7)
out = {}
TZS = [ZoneInfo("Europe/Stockholm"), None]
starts = []
for tz in TZS:
    for d in [datetime(2026,3,28,20,0), datetime(2026,3,29,0,45), datetime(2026,10,24,21,0), datetime(2026,10,25,1,30), datetime(2026,1,14,7,13)]:
        starts.append(d.replace(tzinfo=tz) if tz else d)
# fold=1 starts
starts.append(datetime(2026,10,25,2,15,fold=1,tzinfo=ZoneInfo("Europe/Stockholm")))
for wm in (15, 30, 45, 60, 90):
    for dt in (0.25, 1/12, 1.0, 0.5):
        for off in (0, 1, 3, 7):
            for n in (0, 1, 5, 23, 96):
                h = rng.uniform(0, 6, n)
                out[("mw", wm, dt, off, n)] = T.metering_windows(h, wm, dt, off).tolist()
                hb = rng.uniform(0, 6, (3, n))
                out[("mwb", wm, dt, off, n)] = T._window_means_batch(hb, wm, dt, off).tolist()
                for opf in (0.0, 0.5):
                    ct = T.CapacityTariff(enabled=True, window_minutes=wm, price_per_kw=1.3,
                                          peak_hours=((7.0, 20.0),), offpeak_factor=opf)
                    for si, s in enumerate(starts):
                        nw = T.metering_windows(np.zeros(n), wm, dt, off).size
                        for k in (nw, max(nw - 2, 0), nw + 3):
                            f = T.window_factors(ct, s, k, dt)
                            out[("wf", wm, dt, off, n, opf, si, k)] = None if f is None else f.tolist()
                        out[("pwd", wm, si, nw)] = T.plan_window_days(nw, wm, s).tolist()
                        # peak charges with factors short, exact, long
                        if n and si % 3 == 0:
                            for k in (max(nw - 2, 0), nw, nw + 3):
                                f = T.window_factors(ct, s, k, dt)
                                for thr in (0.0, 2.0, 4.0):
                                    bill = T.PeakBilling(threshold_kw=thr, price_per_kw=1.3,
                                                         window_minutes=wm, dt_hours=dt,
                                                         offset_steps=off, window_factors=f) \
                                        if "window_factors" in T.PeakBilling.__dataclass_fields__ else None
                                    if bill is None: continue
                                    out[("pc", wm, dt, off, n, opf, si, k, thr)] = float(T.peak_cost(h, np.zeros(n), bill))
                                    out[("pcb", wm, dt, off, n, opf, si, k, thr)] = T.peak_cost_batch(hb, np.zeros(n), bill).tolist()
# PeakTracker round trips
for case in range(40):
    m = int(rng.integers(0, 9))
    peaks = rng.uniform(0, 9, m).round(3).tolist()
    days = [f"2026-10-{int(d):02d}" for d in rng.integers(1, 28, m)]
    if case % 4 == 0: days = days[:-1]
    if case % 5 == 0: peaks = peaks + ["x", None]
    tr = T.PeakTracker.from_dict({"month": "2026-10", "peaks": peaks, "peak_days": days})
    out[("pt", case)] = (tr.peaks, tr.peak_days, tr.to_dict() if hasattr(tr, "to_dict") else None)
pickle.dump(out, open(sys.argv[2], "wb"))
print("keys", len(out))
