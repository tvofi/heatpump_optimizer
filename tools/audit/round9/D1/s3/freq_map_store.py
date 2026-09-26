"""D1-s3 M2: a corrupt frequency-map bucket survives FrequencyMap.from_dict and
pins the compressor recommendation for days.

from_dict refuses non-finite and non-positive ratios but bounds neither the
ratio from above nor the bucket key to [0, FREQ_DECILES). A bucket whose ratio
is huge (or whose key sits below decile 0 with a large ratio) predicts any
target at the lowest frequency, so recommend() answers hz_min (after the
coordinator's clip) for every target.

Metric: of N seeded mutants of a healthy persisted map, the number whose
recommendation for a 3 kW target is still under-delivering (plant kW at the
clipped recommended Hz < 50 % of target) after 96 truthful folds (one day of
15-min cycles) through FrequencyMap.observe at that frequency.
Count key: the frequency production's recommend() returns, clipped as
coordinator._command_frequency clips it; the plant kW is 0.04 kW/Hz * Hz.

Run:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/freq_map_store.py [--n 200] [--seed 9] [--perturb]
  --perturb  in-memory fix: from_dict also drops a key outside [0, FREQ_DECILES)
             and a ratio above 1.0 kW/Hz (expect 0).
Expected (default, seed 9, n 200): stuck_after_day=10 (exact, deterministic; huge_ratio 3, neg_key 7); healthy=0.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: box B5 (cloud container, linux).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import copy
import json
import random
import time
from collections import Counter
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
from heatpump_optimizer import freq_control  # noqa: E402
from heatpump_optimizer.freq_control import FrequencyMap, FREQ_DECILES  # noqa: E402


def _arg(name, default):
    return type(default)(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default

N = _arg("--n", 200)
SEED = _arg("--seed", 9)
PERTURB = "--perturb" in sys.argv
HZ_MIN, HZ_MAX, K = 20.0, 100.0, 0.04
TARGET = 3.0
_c0, _t0 = time.process_time(), time.thread_time()


def _healthy():
    m = FrequencyMap()
    for hz in np.linspace(22, 99, 400):
        m.observe(float(hz), K * float(hz), HZ_MIN, HZ_MAX)
    return json.loads(json.dumps(m.as_dict()))


def _mutate(p, rng):
    p = copy.deepcopy(p)
    op = rng.choice(["huge_ratio", "key_shift", "neg_key", "nan", "str", "delete", "swap", "count_neg", "wrap"])
    key = rng.choice(list(p))
    if op == "huge_ratio":
        p[key][0] = rng.choice([1e308, 1e6, 50.0])
    elif op == "key_shift":
        p[str(int(key) + rng.choice([10, 47]))] = p.pop(key)
    elif op == "neg_key":
        p[str(-rng.randint(1, 3))] = [rng.choice([0.04, 5.0]), 50]
    elif op == "nan":
        p[key][0] = float("nan")
    elif op == "str":
        p[key] = "garbage"
    elif op == "delete":
        p.pop(key)
    elif op == "swap":
        p[key] = [p[key][1], p[key][0]]
    elif op == "count_neg":
        p[key][1] = -1
    elif op == "wrap":
        p[key] = {"v": p[key]}
    return p, op


def _stuck(payload):
    m = FrequencyMap.from_dict(json.loads(json.dumps(payload)))
    hz = None
    for _ in range(96):
        rec = m.recommend(TARGET, HZ_MIN, HZ_MAX)
        hz = HZ_MAX if rec is None else float(np.clip(rec, HZ_MIN, HZ_MAX))
        m.observe(hz, K * hz, HZ_MIN, HZ_MAX)
    rec = m.recommend(TARGET, HZ_MIN, HZ_MAX)
    hz = HZ_MAX if rec is None else float(np.clip(rec, HZ_MIN, HZ_MAX))
    return K * hz < 0.5 * TARGET, hz


_orig = FrequencyMap.from_dict.__func__


def _from_dict_fixed(cls, data):
    m = _orig(cls, data)
    m.buckets = {k: v for k, v in m.buckets.items() if 0 <= k < FREQ_DECILES and v[0] <= 1.0}
    return m


def main():
    rng = random.Random(SEED)
    h = _healthy()
    healthy_stuck, healthy_hz = _stuck(h)
    stuck, by_op = 0, Counter()
    for _ in range(N):
        m, op = _mutate(h, rng)
        s, _hz = _stuck(m)
        if s:
            stuck += 1
            by_op[op] += 1
    return healthy_stuck, healthy_hz, stuck, by_op

if PERTURB:
    with mock.patch.object(FrequencyMap, "from_dict", classmethod(_from_dict_fixed)):
        hs, hhz, stuck, by_op = main()
else:
    hs, hhz, stuck, by_op = main()
print(f"arm={'perturb' if PERTURB else 'default'} healthy_recommend_hz={hhz:.1f} stuck_by_op={dict(by_op)}")
print(f"RESULT healthy_stuck={int(hs)} count")
print(f"RESULT stuck_after_day={stuck} count_of_{N}")
cpu, thr = time.process_time() - _c0, time.thread_time() - _t0
print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = 'na'
print(f"RESULT swapins={sw}")
