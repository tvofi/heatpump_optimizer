#!/usr/bin/env python3
"""V3 (round 9) D1-s4-01 / D1-s4-03 reach on REAL Home Assistant: a defrost store
file on disk, read by production QuarantiningStore over the genuine
homeassistant.helpers.storage.Store, then DefrostDerate.from_dict, then 200
healthy zero-duty folds of the corrupted bucket.

Metric (one line): per on-disk duty-cell spelling, the bucket's factor after 200
zero-duty folds (healthy reaches 1.0; 0.55 = pinned at DERATE_MIN), whether the
loaded duty cell is outside [0,1]/non-finite, and whether the instance is flagged
migrated (the D1-s4-03 label).
Command:  PYTHONPATH=. /root/venvha/bin/python tools/audit/round9/D1/verify-v3/D1-s4-01_realha_store.py [--perturb]
  --perturb: DefrostDerate.from_dict wrapped to clip duty to [0,1] (non-finite->0);
  every stuck row must go to 0.
Environment shim: typing.ByteString is aliased to bytes before importing HA
(mashumaro in HA 2026.2.3 needs it; CPython 3.14.0rc2 removed it). Not a product change.
Expected: measured, exact.  Baseline SHA 1936d5ca (evidence tree).  HA 2026.2.3.
Machine: cloud 4-core box, CPython 3.14.0rc2 (V3 sub-seat for G1).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import typing  # noqa: E402
if not hasattr(typing, "ByteString"):
    typing.ByteString = bytes  # environment shim, see header

import asyncio  # noqa: E402
import json  # noqa: E402
import logging  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402

sys.path.insert(0, ".")
t_proc0, t_thr0 = time.process_time(), time.thread_time()

from homeassistant.core import HomeAssistant  # noqa: E402
import homeassistant.const as hac  # noqa: E402
from custom_components.heatpump_optimizer import defrost as D  # noqa: E402
from custom_components.heatpump_optimizer.store import QuarantiningStore  # noqa: E402

assert "tests/hastub" not in " ".join(sys.path), "must run on real HA"
PERTURB = "--perturb" in sys.argv
if PERTURB:
    _orig = D.DefrostDerate.from_dict.__func__

    def _san(cls, data):
        inst = _orig(cls, data)
        inst.duty = [[min(1.0, max(0.0, v)) if math.isfinite(v) else 0.0 for v in r] for r in inst.duty]
        return inst
    D.DefrostDerate.from_dict = classmethod(_san)

NT, NH = len(D.TEMP_EDGES) - 1, len(D.HUMIDITY_EDGES) - 1
T, H = 2, 1
TC, HC = D.TEMP_CENTERS[T], D.HUMIDITY_CENTERS[H]


def healthy():
    return {
        "version": 2,
        "factors": [[0.9] * NH for _ in range(NT)],
        "counts": [[15] * NH for _ in range(NT)],
        "duty": [[0.05] * NH for _ in range(NT)],
        "duty_counts": [[20] * NH for _ in range(NT)],
        "duty_events": [[3] * NH for _ in range(NT)],
    }


# (label, raw JSON text of the cell): what a file on disk can hold.
CELLS = [("healthy_0.05", "0.05"), ('str_"nan"', '"nan"'), ('str_"inf"', '"inf"'),
         ('str_"NaN"', '"NaN"'), ("literal_NaN", "NaN"), ("1.5", "1.5"), ("-0.3", "-0.3"),
         ("50.0", "50.0"), ("1e300", "1e300"), ('str_"1e308"', '"1e308"'),
         ('str_"abc"', '"abc"'), ("null", "null"), ("2^70_int", str(2 ** 70))]

LOGS = []


class _H(logging.Handler):
    def emit(self, r):
        LOGS.append(r)


logging.getLogger().addHandler(_H(level=logging.WARNING))


async def one(hass, label, raw):
    key = "hpo_v3_" + "".join(c for c in label if c.isalnum())
    body = json.dumps({"version": 1, "minor_version": 1, "key": key,
                       "data": {"defrost": healthy()}})
    token = '"__CELL__"'
    doc = json.loads(body)
    doc["data"]["defrost"]["duty"][T][H] = "__CELL__"
    text = json.dumps(doc).replace(token, raw)
    path = hass.config.path(".storage", key)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(text)
    before = len(LOGS)
    store = QuarantiningStore(hass, 1, key)
    try:
        stored = await store.async_load()
    except Exception as err:  # noqa: BLE001
        return label, f"load_raised:{type(err).__name__}", None, None, None, len(LOGS) - before
    if not isinstance(stored, dict):
        inst = D.DefrostDerate.from_dict(None)
        loaded = "store_returned_" + type(stored).__name__
    else:
        inst = D.DefrostDerate.from_dict(stored.get("defrost"))
        loaded = repr(stored["defrost"]["duty"][T][H]) if isinstance(stored.get("defrost"), dict) else "?"
    cell = inst.duty[T][H]
    bad = (not math.isfinite(cell)) or cell < 0 or cell > 1
    for _ in range(200):
        inst.observe_duty(TC, HC, 0.0, 0)
        inst.observe(TC, HC, 1.0)
    return label, loaded, bad, round(inst.factor(TC, HC), 4), inst.migrated, len(LOGS) - before


async def main():
    d = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"))
    hass = HomeAssistant(d)
    rows = []
    for label, raw in CELLS:
        rows.append(await one(hass, label, raw))
    await hass.async_stop(force=True)
    return rows


rows = asyncio.run(main())
print(f"HA {hac.__version__} perturb={PERTURB}")
stuck = pinned = mig = 0
for label, loaded, bad, fac, migr, nlog in rows:
    print(f"  {label:14s} store_delivered={loaded!s:22s} cell_out_of_domain={bad} "
          f"factor_after_200_zero_folds={fac} migrated={migr} warnings={nlog}")
    if bad:
        stuck += 1
        if fac is not None and abs(fac - D.DERATE_MIN) < 1e-9:
            pinned += 1
    if migr:
        mig += 1
print(f"RESULT realha_cells={len(rows)} count")
print(f"RESULT realha_stuck_out_of_domain={stuck} count")
print(f"RESULT realha_pinned_at_derate_min={pinned} count")
print(f"RESULT realha_flagged_migrated={mig} count")
pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=" + next((ln.split()[1] for ln in open("/proc/vmstat") if ln.startswith("pswpin")), "unknown"))
