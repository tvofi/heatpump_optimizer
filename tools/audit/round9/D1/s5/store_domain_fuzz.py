#!/usr/bin/env python3
"""D1-s5 (round 9, D1.M2): store-corruption fuzz of the two persisted learners
whose loaders live in this seat's files: price_model.PriceShapeModel.from_dict
and tariff.PeakTracker.from_dict.

Metric (one line): of N seeded mutants of a healthy payload per store, the
number whose loaded state makes the next cycle DELIVER a value outside the
domain that learner's own update path can ever produce, with no WARNING logged.

Count key (the value the production seam delivers, not the mutant's fields):
  price_model - the tail of production `price_model.extend_price_series`
                (the planning price of every unpublished step) and its sigma:
                invalid when any tail price is <= 0 or non-finite, or > 1000x
                the known mean, or sigma is non-finite. An honest model cannot
                deliver those: observe_day clips every bin to [0.2, 3] and
                renormalises, so every bin is > 0 and bounded.
  peak_tracker - production `PeakTracker.threshold_kw` / `billed_peak_kw`
                after the cycle folds real samples: invalid when either is
                negative or NaN. An honest tracker cannot: observe() drops
                every negative sample and window factors are in [0, 1].
"next" counts the invalid mutants still invalid after one more cycle (the
price model folds one healthy day with observe_day; the tracker closes one
more window) - the brief's "the next cycle does not repeat the failure".
"crash" counts mutants whose load or cycle raised.

Command:
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s5/store_domain_fuzz.py [--perturb] [--n 300] [--seed 9]
  --perturb applies, in memory, the domain gate the update path already
  enforces (price shapes/quarters clipped to their observe_* ranges and
  renormalised, negative day counts reset to 0; negative peaks dropped and a
  window whose sample count/factor is outside the update path's domain reset):
  both silent_invalid counts go to 0.

Expected (baseline, --n 300 --seed 9): RESULT price_model_silent_invalid=11
(next_still_invalid=9), peak_tracker_silent_invalid=8 (next_still_invalid=2),
exact (seeded); crash=0 for both. With --perturb: 0 and 0.
Seeds 1,2,3,4,5,9 (six cells): price_model 8,10,8,9,13,11 (range 8-13, 8 with
the largest dropped); peak_tracker 2,5,3,0,5,8 (range 0-8).
Null control: the healthy payload itself (mutation "none") delivers 0 invalid.
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: cloud container
(box B5, Linux x86_64), Python 3.14 venv. Counts are contention-immune.
Root rule: imports from the working directory (run from the export root).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import copy
import logging
import math
import random
import sys
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from unittest import mock

sys.path.insert(0, ".")
sys.path.insert(0, "tests")

_p0, _t0 = time.process_time(), time.thread_time()

import numpy as np  # noqa: E402

from custom_components.heatpump_optimizer import price_model as pm  # noqa: E402
from custom_components.heatpump_optimizer import tariff as tf  # noqa: E402

PERTURB = "--perturb" in sys.argv


def _arg(name, default):
    if name in sys.argv:
        return type(default)(sys.argv[sys.argv.index(name) + 1])
    return default


N = _arg("--n", 300)
SEED = _arg("--seed", 9)


class _Count(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING)
        self.n = 0

    def emit(self, record):
        self.n += 1


LOG = _Count()
logging.getLogger("custom_components.heatpump_optimizer").addHandler(LOG)
logging.getLogger("custom_components.heatpump_optimizer").setLevel(logging.DEBUG)

# ---------------------------------------------------------------- healthy payloads

UTC = timezone.utc
DAY0 = datetime(2026, 1, 5, tzinfo=UTC)  # a Monday


def _day_prices(i, rng):
    base = 1.0 + 0.3 * math.sin(i)
    shape = [0.6] * 6 + [1.4] * 3 + [1.0] * 8 + [1.6] * 4 + [0.8] * 3
    return [base * s * (1.0 + 0.05 * rng.random()) for s in shape]


def healthy_price_model():
    rng = random.Random(1)
    m = pm.PriceShapeModel()
    for i in range(14):
        when = DAY0 + timedelta(days=i)
        hourly = _day_prices(i, rng)
        m.observe_day(when, hourly)
        m.observe_day_quarters(when, [h * f for h in hourly for f in (0.9, 1.0, 1.0, 1.1)])
    return m.as_dict()


def healthy_peak_tracker():
    t = tf.PeakTracker()
    tariff = tf.CapacityTariff(enabled=True, price_per_kw=50.0)
    start = datetime(2026, 1, 3, tzinfo=UTC)
    for h in range(0, 72, 1):
        for q in range(4):
            t.observe(start + timedelta(hours=h, minutes=15 * q), 2.0 + (h % 7) * 0.5, tariff)
    return t.as_dict()


# ---------------------------------------------------------------- mutants

HOSTILE = (
    lambda v, r: float("nan"), lambda v, r: float("inf"), lambda v, r: float("-inf"),
    lambda v, r: -abs(v) if isinstance(v, (int, float)) and not isinstance(v, bool) and v else -5,
    lambda v, r: 1e300, lambda v, r: 10 ** 30, lambda v, r: 0, lambda v, r: -10 ** 9,
    lambda v, r: "abc", lambda v, r: None, lambda v, r: [], lambda v, r: {}, lambda v, r: True,
    lambda v, r: [v], lambda v, r: str(v),
)


def _paths(obj, prefix=()):
    yield prefix
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _paths(v, prefix + (k,))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _paths(v, prefix + (i,))


def _get(obj, path):
    for p in path:
        obj = obj[p]
    return obj


def _set(obj, path, value):
    if not path:
        return value
    parent = _get(obj, path[:-1])
    parent[path[-1]] = value
    return obj


def mutate(payload, rng):
    p = copy.deepcopy(payload)
    kind = rng.choice(("value", "value", "value", "delkey", "truncate", "nest", "whole"))
    paths = [x for x in _paths(p) if x]
    if kind == "whole":
        return rng.choice(("garbage", [p], None, 42, {})), "whole"
    path = rng.choice(paths)
    target = _get(p, path)
    if kind == "delkey":
        top = path[:1]
        del p[top[0]]
        return p, f"del {top[0]}"
    if kind == "truncate" and isinstance(target, list) and target:
        _set(p, path, target[: rng.randrange(len(target))])
        return p, f"truncate {path}"
    if kind == "nest":
        _set(p, path, {"x": target})
        return p, f"nest {path}"
    fn = rng.randrange(len(HOSTILE))
    # A value mutation hits one leaf, or every leaf of a list (a whole row).
    if isinstance(target, list) and target and rng.random() < 0.5:
        _set(p, path, [HOSTILE[fn](v, rng) for v in target])
        return p, f"row{fn} {path}"
    _set(p, path, HOSTILE[fn](target, rng))
    return p, f"val{fn} {path}"


# ---------------------------------------------------------------- cycles

WHEN = DAY0 + timedelta(days=16, hours=10)  # a Wednesday, mid-morning


def _price_invalid(model):
    n = 48
    starts = [WHEN + timedelta(hours=i) for i in range(n)]
    known = [1.0 + 0.1 * (i % 3) for i in range(12)]
    prices, mask, sigma = pm.extend_price_series(known, n, starts, model)
    tail = prices[~mask]
    ref = float(np.mean(known))
    bad = (not np.all(np.isfinite(tail)) or np.any(tail <= 0.0)
           or np.any(tail > 1000.0 * ref) or not np.all(np.isfinite(sigma)))
    return bool(bad)


def price_cycle(payload):
    model = pm.PriceShapeModel.from_dict(payload)
    first = _price_invalid(model)
    rng = random.Random(2)
    model.observe_day(WHEN.replace(hour=0), _day_prices(3, rng))
    return first, _price_invalid(model)


TARIFF = tf.CapacityTariff(enabled=True, price_per_kw=50.0)


def _peak_invalid(t):
    th = t.threshold_kw(TARIFF)
    billed = t.billed_peak_kw(TARIFF)
    return bool(math.isnan(th) or th < 0.0 or math.isnan(billed) or billed < 0.0)


def peak_cycle(payload):
    t = tf.PeakTracker.from_dict(payload)
    now = datetime(2026, 1, 6, 12, 0, tzinfo=UTC)  # same month as the payload
    # The open window's key in the healthy payload is 2026-01-05T23:00; one
    # new sample closes it (the restart-then-first-cycle path).
    t.observe(now, 3.0, TARIFF)
    first = _peak_invalid(t)
    t.observe(now + timedelta(hours=1), 3.0, TARIFF)
    return first, _peak_invalid(t)


# ---------------------------------------------------------------- perturbation

_orig_pm_from_dict = pm.PriceShapeModel.from_dict.__func__
_orig_pt_from_dict = tf.PeakTracker.from_dict.__func__


def _gated_pm_from_dict(cls, data):
    m = _orig_pm_from_dict(cls, data)
    m.shapes = [list(np.clip(s, pm.SHAPE_MIN, pm.SHAPE_MAX) / max(np.mean(np.clip(s, pm.SHAPE_MIN, pm.SHAPE_MAX)), 1e-6)) for s in m.shapes]
    m.quarter_factors = [list(np.clip(s, pm.QUARTER_FACTOR_MIN, pm.QUARTER_FACTOR_MAX)) for s in m.quarter_factors]
    m.days = [max(0, d) for d in m.days]
    m.quarter_days = [max(0, d) for d in m.quarter_days]
    m.residual_var = [[v if math.isfinite(v) else 0.0 for v in s] for s in m.residual_var]
    return m


def _gated_pt_from_dict(cls, data):
    t = _orig_pt_from_dict(cls, data)
    keep = [(p, d) for p, d in zip(t.peaks, t.peak_days) if p >= 0.0]
    t.peaks = [p for p, _ in keep]
    t.peak_days = [d for _, d in keep]
    if t._window_samples < 0 or t._window_sum < 0 or not 0.0 <= t._window_factor <= 1.0 \
            or t._window_wsum < 0 or t._window_weight < 0:
        t._window_key, t._window_sum, t._window_samples = "", 0.0, 0
        t._window_factor, t._window_wsum, t._window_weight = 1.0, 0.0, 0.0
    return t


# ---------------------------------------------------------------- run


def fuzz(name, healthy, cycle):
    rng = random.Random(SEED)
    out = Counter()
    examples = []
    LOG.n = 0
    f, s = cycle(copy.deepcopy(healthy))
    out["control_invalid"] = int(f or LOG.n > 0)
    for i in range(N):
        payload, label = mutate(healthy, rng)
        LOG.n = 0
        try:
            first, second = cycle(payload)
        except Exception as err:  # noqa: BLE001 - a crash is a result here
            out["crash"] += 1
            examples.append(f"CRASH {label}: {err!r}")
            continue
        if first and LOG.n == 0:
            out["silent_invalid"] += 1
            out["next_still_invalid"] += int(second)
            examples.append(f"silent {label} (next cycle still invalid: {second})")
        elif first:
            out["logged_invalid"] += 1
        elif LOG.n:
            out["logged_quarantined"] += 1
        else:
            out["ok"] += 1
    print(f"-- {name}: {dict(out)}")
    for e in examples:
        print(f"   {e}")
    return out


def _swapins():
    try:
        with open("/proc/vmstat") as f:
            for line in f:
                if line.startswith("pswpin"):
                    return int(line.split()[1])
    except OSError:
        pass
    return -1


if __name__ == "__main__":
    print(f"arm: {'PERTURBED (domain gate in the loaders)' if PERTURB else 'baseline'}; N={N} seed={SEED}")
    hp, ht = healthy_price_model(), healthy_peak_tracker()
    if PERTURB:
        with mock.patch.object(pm.PriceShapeModel, "from_dict", classmethod(_gated_pm_from_dict)), \
             mock.patch.object(tf.PeakTracker, "from_dict", classmethod(_gated_pt_from_dict)):
            a = fuzz("price_model", hp, price_cycle)
            b = fuzz("peak_tracker", ht, peak_cycle)
    else:
        a = fuzz("price_model", hp, price_cycle)
        b = fuzz("peak_tracker", ht, peak_cycle)
    for name, c in (("price_model", a), ("peak_tracker", b)):
        print(f"RESULT {name}_silent_invalid={c['silent_invalid']} mutants (of {N})")
        print(f"RESULT {name}_next_still_invalid={c['next_still_invalid']} mutants")
        print(f"RESULT {name}_crash={c['crash']} mutants")
        print(f"RESULT {name}_control_invalid={c['control_invalid']} payloads (of 1)")
    p, t = time.process_time() - _p0, time.thread_time() - _t0
    print(f"RESULT thread_factor={p / t if t > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={_swapins()}")
