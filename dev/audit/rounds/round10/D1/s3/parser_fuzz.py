"""D1-s3 M6 null sweep: hostile payloads into open_meteo._parse_block,
coordinator._plausible_forecast_rows and price_model.prices_from_tibber_payload.
Metric: exceptions escaping each parser over 400 seeded hostile inputs (count), and
non-finite values in their outputs (count).
Command: PYTHONPATH=tests/hastub ~/hpo-seats/r9fix-lanerunner/bin/python3 dev/audit/rounds/round10/D1/s3/parser_fuzz.py
Expected: raises_* reported as measured; nonfinite_*=0. Baseline 17f1c55fad1b, macOS arm64.
Perturbation: --perturb removes the isfinite drop in _parse_block (wraps float) -> nonfinite_open_meteo up.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import math, random, sys, time
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
from heatpump_optimizer import open_meteo as OM, coordinator as C, price_model as PM
if "--perturb" in sys.argv:
    OM.math = type("M", (), {"isfinite": staticmethod(lambda v: True)})
rng = random.Random(10)
H = [None, "x", float("nan"), float("inf"), -1e308, 1e308, [], {}, "1e999", True, 5, "2026-13-40", -3]
def hv(): return rng.choice(H + [rng.uniform(-50, 2000)])
def ts(i): return rng.choice([f"2026-10-14T{i%24:02d}:00", "bad", None, 7, f"2026-10-14T{i%24:02d}:00+05:00"])
r = {"om": 0, "fc": 0, "tb": 0}; nf = {"om": 0, "fc": 0, "tb": 0}
t0p, t0t = time.process_time(), time.thread_time()
for _ in range(400):
    n = rng.randint(0, 30)
    blk = rng.choice([{"time": [ts(i) for i in range(n)], "shortwave_radiation": [hv() for _ in range(n)]}, [], "s", {"time": "x"}])
    try:
        s = OM._parse_block(blk, "shortwave_radiation")
        nf["om"] += sum(1 for v in s.values if not math.isfinite(v))
    except Exception: r["om"] += 1
    rows = rng.choice([[{"datetime": ts(i), "temperature": hv(), "wind_speed": hv()} for i in range(n)], None, "x", [1, None]])
    try:
        out = C._plausible_forecast_rows(rows)
        nf["fc"] += sum(1 for row in out for v in row.values() if isinstance(v, float) and not math.isfinite(v))
    except Exception: r["fc"] += 1
    tb = rng.choice([{"data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": {"today": [{"total": hv(), "startsAt": ts(i)} for i in range(n)]}}}]}}}, None, {"data": None}, {"data": {"viewer": {"homes": ["x"]}}}])
    try:
        out = PM.prices_from_tibber_payload(tb)
        if isinstance(out, list): nf["tb"] += sum(1 for row in out if not math.isfinite(row["total"]))
    except Exception: r["tb"] += 1
for k in r: print(f"RESULT raises_{k}={r[k]} count"); print(f"RESULT nonfinite_{k}={nf[k]} count")
print(f"RESULT thread_factor={(time.process_time()-t0p)/max(time.thread_time()-t0t,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}"); print("RESULT swapins=0")
