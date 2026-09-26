#!/usr/bin/env python3
"""V2 (D1-2) own harness for D1-s4-01 and D1-s4-03: defrost duty corruption driven through
the production persistence boundary (store.QuarantiningStore.async_load) before
DefrostDerate.from_dict, exhaustively (every duty cell x every bad scalar), not by random draw.

Metric (D1-s4-01): of 12 cells x K bad scalars single-cell duty corruptions of a healthy v2
  payload, saved through the stub Store (json round-trip) and loaded through QuarantiningStore,
  count whose delivered DefrostDerate.factor at the corrupted bucket's centre differs from the
  healthy-loaded twin's by > 0.01 after F healthy zero-duty folds per bucket (F = 24, 200).
  Count key: the value factor() delivers, not the stored cell.
Metric (D1-s4-03): of the same corruptions, count loaded with migrated=True and the measured
  buckets discarded (duty_counts reset to 0 where the healthy twin has 20).
Arms: 'boundary' (QuarantiningStore, the production path at coordinator.py _async_load_accuracy
  and the snapshot restore) and 'bypass' (from_dict on the raw payload, as the finder drove it).
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/u2_defrost_boundary.py
Expected (exact, deterministic): boundary wrong_200=36 pinned_min_200=36 nonfinite=0 migrated=72 discarded=864;
  bypass wrong_200=84 nonfinite=48 migrated=24; folds_to_recover 1e308=6779 1e300=6604 2**70=509 50.0=85 (+-0).
Baseline SHA 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, copy, math, sys, time
sys.path.insert(0, "tests/hastub"); sys.path.insert(0, ".")
p0, t0 = time.process_time(), time.thread_time()
from homeassistant.helpers import storage as S  # noqa: E402
from custom_components.heatpump_optimizer import defrost as D  # noqa: E402
from custom_components.heatpump_optimizer.store import QuarantiningStore  # noqa: E402

NT, NH = len(D.TEMP_EDGES) - 1, len(D.HUMIDITY_EDGES) - 1
BAD = [("nan_str", "nan"), ("inf_str", "inf"), ("nan_float", float("nan")), ("inf_float", float("inf")),
       ("1e308_str", "1e308"), ("1e300", 1e300), ("2**70", 2 ** 70), ("50.0", 50.0), ("1.5", 1.5),
       ("-0.5", -0.5), ("-1e300", -1e300), ("abc", "abc"), ("None", None)]


def healthy():
    return {"version": 2,
            "factors": [[0.9] * NH for _ in range(NT)], "counts": [[20] * NH for _ in range(NT)],
            "duty": [[0.1] * NH for _ in range(NT)], "duty_counts": [[20] * NH for _ in range(NT)],
            "duty_events": [[3] * NH for _ in range(NT)]}


async def through_boundary(payload, key):
    await S.Store(None, 1, key).async_save({"defrost": payload})
    stored = await QuarantiningStore(None, 1, key).async_load()
    return D.DefrostDerate.from_dict(stored.get("defrost"))


def fold(inst, n):
    for _ in range(n):
        for tc in D.TEMP_CENTERS:
            for hc in D.HUMIDITY_CENTERS:
                inst.observe_duty(tc, hc, 0.0, 0)


async def main():
    ref = D.DefrostDerate.from_dict(healthy())
    ref24 = copy.deepcopy(ref); fold(ref24, 24)
    ref200 = copy.deepcopy(ref); fold(ref200, 200)
    out = {}
    for arm in ("boundary", "bypass"):
        wrong24 = wrong200 = pinned_min200 = pinned_max200 = nonfinite = migrated = discarded = 0
        per = {}
        k = 0
        for name, bad in BAD:
            for t in range(NT):
                for h in range(NH):
                    p = healthy(); p["duty"][t][h] = bad; k += 1
                    if arm == "boundary":
                        inst = await through_boundary(p, f"u2_{k}")
                    else:
                        try:
                            inst = D.DefrostDerate.from_dict(p)
                        except Exception:  # noqa: BLE001
                            continue
                    migrated += int(inst.migrated)
                    discarded += sum(1 for r in inst.duty_counts for c in r if c == 0)
                    nonfinite += sum(1 for r in inst.duty for v in r if not math.isfinite(v))
                    tc, hc = D.TEMP_CENTERS[t], D.HUMIDITY_CENTERS[h]
                    i24 = copy.deepcopy(inst); fold(i24, 24)
                    i200 = copy.deepcopy(inst); fold(i200, 200)
                    w24 = abs(i24.factor(tc, hc) - ref24.factor(tc, hc)) > 0.01
                    w200 = abs(i200.factor(tc, hc) - ref200.factor(tc, hc)) > 0.01
                    wrong24 += w24; wrong200 += w200
                    pinned_min200 += abs(i200.factor(tc, hc) - D.DERATE_MIN) < 1e-9
                    pinned_max200 += w200 and abs(i200.factor(tc, hc) - D.DERATE_MAX) < 1e-9
                    per.setdefault(name, [0, 0])
                    per[name][0] += w24; per[name][1] += w200
        print(f"RESULT {arm}.cases={k} count")
        print(f"RESULT {arm}.wrong_factor_after_24_folds={wrong24} count")
        print(f"RESULT {arm}.wrong_factor_after_200_folds={wrong200} count")
        print(f"RESULT {arm}.pinned_derate_min_after_200={pinned_min200} count")
        print(f"RESULT {arm}.pinned_derate_max_wrong_after_200={pinned_max200} count")
        print(f"RESULT {arm}.nonfinite_cells_loaded={nonfinite} count")
        print(f"RESULT {arm}.migrated={migrated} count")
        print(f"RESULT {arm}.measured_buckets_discarded={discarded} count")
        for name, (a, b) in per.items():
            print(f"RESULT {arm}.by_scalar.{name}=w24:{a},w200:{b} count")
    # folds-to-recover for finite out-of-range duty (single bucket), cap 20000.
    # Positive: fold zero duty until factor is within 0.01 of 1.0 (the healthy target).
    # Negative: fold a real duty of 0.2 until factor is within 0.01 of derate_from_duty(0.2);
    # a negative cell shows 1.0 (no derate) until then.
    for name, bad in (("1e308", 1e308), ("1e300", 1e300), ("2**70", float(2 ** 70)), ("50.0", 50.0),
                      ("-0.5", -0.5), ("-1e300", -1e300)):
        p = healthy(); p["duty"][0][0] = bad
        inst = await through_boundary(p, f"u2_rec_{name}")
        tc, hc = D.TEMP_CENTERS[0], D.HUMIDITY_CENTERS[0]
        d = 0.0 if bad > 0 else 0.2
        target = D.derate_from_duty(d)
        n = 0
        while n < 20000 and abs(inst.factor(tc, hc) - target) > 0.01:
            inst.observe_duty(tc, hc, d, 0); n += 1
        print(f"RESULT folds_to_recover.{name}={n} folds (fold duty {d}, target factor {target:.3f})")
    p1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={(p1 - p0) / max(t1 - t0, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except Exception:  # noqa: BLE001
        sw = "na"
    print(f"RESULT swapins={sw}")

asyncio.run(main())
