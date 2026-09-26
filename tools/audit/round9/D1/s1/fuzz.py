"""D1-s1 store-corruption fuzzer (D1.M2) over the persisted payloads whose loaders
live in D1-s1's cells: ledger, accuracy, comfort, curve, wear, drift (Cusum),
snapshots, dhw profile (+ its snapshot-restore twin apply_payload).

Metric (one line): per store, of N seeded mutants of a healthy payload saved and
re-read through the real QuarantiningStore, how many make the loader or a
consumer op raise in cycle 1, and how many of those raise again in cycle 2
(permanent); plus mutants whose published outputs carry a non-finite number.
Count key: exceptions raised by production calls on the object the production
loader delivered.

Command:  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python tools/audit/round9/D1/s1/fuzz.py [--n 250] [--seed 9] [--fix-snap] [--fix-ts] [--stub-json]
  expected (seed 9, n 250, exact): see the RESULT lines in REPORT.md.
  --fix-ts   perturbation for D1-s1-01: seam modules' datetime.fromisoformat
             treats naive as UTC -> the naive-timestamp signatures go to 0.
  --fix-snap perturbation for D1-s1-02: best_restore's bias read coerced through
             a guarded float() (np.isfinite on a str/list raises) -> the
             snapshots.best_restore signatures go to 0.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B4 cloud container.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import copy
import json
import logging
import math
import random
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
_p0, _t0 = time.process_time(), time.thread_time()

import numpy as np  # noqa: E402
from harness import FakeHass  # noqa: E402
from heatpump_optimizer import comfort_learning, curve_learning, snapshots as snap_mod  # noqa: E402
from heatpump_optimizer.accuracy import AccuracySample, AccuracyTracker, delivered_ratio  # noqa: E402
from heatpump_optimizer.comfort_learning import ComfortLearner, OverrideEvent  # noqa: E402
from heatpump_optimizer.curve_learning import CurveLearner  # noqa: E402
from heatpump_optimizer.dhw_learning import DhwProfileLearner  # noqa: E402
from heatpump_optimizer.drift import Cusum  # noqa: E402
from heatpump_optimizer.ledger import MonthlyLedger  # noqa: E402
from heatpump_optimizer.snapshots import SnapshotRing  # noqa: E402
from heatpump_optimizer.store import QuarantiningStore  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402
from heatpump_optimizer.wear import StartCounter  # noqa: E402

args = sys.argv[1:]
N = int(args[args.index("--n") + 1]) if "--n" in args else 250
SEED = int(args[args.index("--seed") + 1]) if "--seed" in args else 9
FIX_TS, FIX_SNAP = "--fix-ts" in args, "--fix-snap" in args
STUB_JSON = "--stub-json" in args
NOW = datetime(2026, 1, 20, 12, 0, tzinfo=timezone.utc)

# count log lines emitted by the loaders (one-log-line requirement)
class _Count(logging.Handler):
    n = 0
    def emit(self, record):
        if record.levelno >= logging.WARNING:
            _Count.n += 1
logging.getLogger("custom_components").addHandler(_Count())
logging.getLogger("heatpump_optimizer").addHandler(_Count())
logging.getLogger("heatpump_optimizer").setLevel(logging.WARNING)
logging.getLogger("heatpump_optimizer").propagate = False


# ---------------------------------------------------------------- healthy
def healthy_payloads():
    led = MonthlyLedger()
    for d in range(40):
        w = NOW - timedelta(days=d)
        led.add_savings_settlement(w, baseline_kw=2.0, actual_kwh=1.5, spot=1.1, dt=0.5)
        led.observe_meta_mean(w, "spot_price", 1.1)
    acc = AccuracyTracker()
    for i in range(30):
        w = NOW - timedelta(minutes=30 * i)
        acc.record(AccuracySample(when=w, predicted_power_kw=1.2, actual_power_kw=1.3,
                                  predicted_temp=21.0, actual_temp=21.2, predicted_cost=0.4,
                                  actual_cost=0.45, outdoor_temp=-3.0, humidity=80.0,
                                  cop_residual=0.1))
        acc.note_lead_prediction(w + timedelta(hours=3), 3.0, 21.1)
    acc.score_lead_predictions(NOW, 21.0, window_hours=24)
    for i in range(5):
        acc.note_lead_prediction(NOW + timedelta(hours=i + 1), float([1, 3, 6, 12, 24][i]), 21.0)
    com = ComfortLearner(configured_weight=5.0, learned_weight=5.0)
    for i in range(3):
        com.record_override(OverrideEvent(when=NOW - timedelta(days=5 - i), delta_c=1.0,
                                          indoor_temp=20.5, planned_setpoint=20.0, relative_price=1.5))
    cur = CurveLearner(bias=-1.0, comfortable_days=1, resets=1, _last_day="2026-01-18",
                       _last_step_at=(NOW - timedelta(days=9)).isoformat())
    wear = StartCounter(running=False, lifetime=120, months={"2025-12": 60, "2026-01": 60})
    cus = Cusum(threshold=5.0, drift=0.1)
    for i in range(12):
        cus.update(NOW - timedelta(hours=12 - i), 1.0)
    ring = SnapshotRing()
    for k in range(3):
        ring.take(NOW - timedelta(days=21 - 7 * k),
                  {"comfort": com.as_dict(), "curve": cur.as_dict()}, acc.summary(), True)
    ring.observe_bias(NOW - timedelta(days=1), 0.7, True)
    dhw = {"hourly_profile": [1.0 + 0.3 * math.sin(h / 3) for h in range(24)],
           "cooling_rate": 0.8, "cooling_samples": 12,
           "profile_weekday": [1.0] * 24, "profile_weekend": [1.1] * 12 + [0.9] * 12,
           "profile_weekday_samples": 5, "profile_weekend_samples": 2,
           "updated_at": NOW.isoformat()}
    return {"ledger": led.as_dict(), "accuracy": acc.as_dict(), "comfort": com.as_dict(),
            "curve": cur.as_dict(), "wear": wear.as_dict(), "cusum": cus.as_dict(),
            "snapshots": ring.as_dict(), "dhw_profile": dhw}


# ---------------------------------------------------------------- mutation
def paths(node, prefix=()):
    yield prefix
    if isinstance(node, dict):
        for k, v in node.items():
            yield from paths(v, prefix + (k,))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from paths(v, prefix + (i,))


def get(node, path):
    for p in path:
        node = node[p]
    return node


def put(root, path, value):
    if not path:
        return value
    get(root, path[:-1])[path[-1]] = value
    return root


def naive(s):
    try:
        v = datetime.fromisoformat(s)
    except (TypeError, ValueError):
        return s
    return v.replace(tzinfo=None).isoformat() if v.tzinfo else s


OPS = ["type_str", "type_list", "type_dict", "type_bool", "type_none", "missing", "nan",
       "inf", "ninf", "nan_str", "negative", "huge", "hugeint", "nest_list", "nest_dict",
       "truncate", "str_for_container", "naive_ts", "numeric_str"]


def mutate(rng, payload):
    root = copy.deepcopy(payload)
    tags = []
    for _ in range(rng.choice((1, 1, 2, 3))):
        ps = list(paths(root))
        path = rng.choice(ps)
        op = rng.choice(OPS)
        try:
            cur = get(root, path)
        except (KeyError, IndexError, TypeError):
            continue
        if op == "naive_ts":
            ts = [p for p in ps if isinstance(_safe_get(root, p), str) and "T" in _safe_get(root, p)
                  and _safe_get(root, p)[:2] == "20"]
            if not ts:
                continue
            path = rng.choice(ts)
            root = put(root, path, naive(get(root, path)))
        elif op == "missing":
            if not path:
                continue
            parent = get(root, path[:-1])
            if isinstance(parent, dict):
                del parent[path[-1]]
            else:
                del parent[path[-1]]
        elif op == "truncate":
            if isinstance(cur, list):
                root = put(root, path, cur[: rng.randrange(0, max(1, len(cur)))])
            elif isinstance(cur, dict):
                keys = list(cur)[: rng.randrange(0, max(1, len(cur)))]
                root = put(root, path, {k: cur[k] for k in keys})
            elif isinstance(cur, str):
                root = put(root, path, cur[: len(cur) // 2])
            else:
                continue
        else:
            val = {
                "type_str": lambda c: "garbage", "type_list": lambda c: [c], "type_dict": lambda c: {"x": c},
                "type_bool": lambda c: True, "type_none": lambda c: None, "nan": lambda c: float("nan"),
                "inf": lambda c: float("inf"), "ninf": lambda c: float("-inf"), "nan_str": lambda c: "NaN",
                "negative": lambda c: -abs(c) if isinstance(c, (int, float)) and not isinstance(c, bool) else -1,
                "huge": lambda c: 1e308, "hugeint": lambda c: 10 ** 400,
                "nest_list": lambda c: [[c]], "nest_dict": lambda c: {"a": {"b": c}},
                "str_for_container": lambda c: "{}" if isinstance(c, (dict, list)) else "12,5",
                "numeric_str": lambda c: str(c) if isinstance(c, (int, float)) else "3.5",
            }[op](cur)
            root = put(root, path, val)
        tags.append(f"{op}@{'/'.join(map(str, path))}")
    return root, tags


def _safe_get(root, p):
    try:
        return get(root, p)
    except Exception:
        return None


# ---------------------------------------------------------------- drive
def finite_tree(v):
    if isinstance(v, float):
        return math.isfinite(v)
    if isinstance(v, dict):
        return all(finite_tree(x) for x in v.values())
    if isinstance(v, (list, tuple)):
        return all(finite_tree(x) for x in v)
    return True


class _HaJson:
    """Home Assistant's own Store codec: orjson (NaN/inf written as null, a
    >64-bit int refused on save, an out-of-range literal refused on load).
    Default; --stub-json keeps tests/hastub's stdlib json, which decodes
    10**400 to an exact int that real HA can never hand a loader."""
    import orjson as _o
    @classmethod
    def dumps(cls, d):
        return cls._o.dumps(d, option=cls._o.OPT_NON_STR_KEYS).decode()
    @classmethod
    def loads(cls, s):
        return cls._o.loads(s)


def store_roundtrip(payload):
    st = QuarantiningStore(FakeHass(), 1, f"d1s1_fuzz_{id(payload)}")
    asyncio.run(st.async_save(payload))
    return asyncio.run(st.async_load())


def drive(name, data, cycle, obj):
    """One cycle of consumer ops on the loaded object; returns (obj, outputs)."""
    now = NOW + timedelta(days=cycle)
    outs = []
    ops = []
    if name == "ledger":
        o = obj or MonthlyLedger.from_dict(data)
        ops = [("add", lambda: o.add_savings_settlement(now, baseline_kw=2.0, actual_kwh=1.5, spot=1.1, dt=0.5)),
               ("observe_meta_mean", lambda: o.observe_meta_mean(now, "spot_price", 1.2)),
               ("savings_months", lambda: outs.append(o.savings_months(now))),
               ("month_summary", lambda: outs.append([o.month_summary(k) for k in list(o.months)])),
               ("meta_mean", lambda: outs.append([o.meta_mean(k, "spot_price") for k in list(o.months)])),
               ("line", lambda: outs.append([o.line(k, "savings_actual") for k in list(o.months)]))]
    elif name == "accuracy":
        o = obj or AccuracyTracker.from_dict(data)
        ops = [("summary", lambda: outs.append(o.summary())), ("trust", lambda: outs.append(o.trust())),
               ("sigma", lambda: outs.append([o.sigma(h) for h in (1, 3, 6, 12, 24)])),
               ("has_lead_history", o.has_lead_history),
               ("delivered_ratio", lambda: outs.append([delivered_ratio(s) for s in o.samples])),
               ("note_lead", lambda: o.note_lead_prediction(now + timedelta(hours=3), 3.0, 21.0)),
               ("score_lead", lambda: o.score_lead_predictions(now, 21.0))]
    elif name == "comfort":
        o = obj or ComfortLearner.from_dict(data, 5.0)
        ops = [("record_override", lambda: o.record_override(OverrideEvent(
                    when=now, delta_c=1.0, indoor_temp=20.5, planned_setpoint=20.0, relative_price=1.5))),
               ("record_quiet_period", lambda: o.record_quiet_period(now, 0.1, 2.0, days=1.0)),
               ("effective_weight", lambda: outs.append(o.effective_weight)),
               ("summary", lambda: outs.append(o.summary()))]
    elif name == "curve":
        o = obj or CurveLearner.from_dict(data)
        ops = [("record_day", lambda: o.record_day(now, 1.0)),
               ("summary", lambda: outs.append(o.summary()))]
    elif name == "wear":
        o = obj or StartCounter.from_dict(data)
        ops = [("observe", lambda: [o.observe(now + timedelta(minutes=m), kw, 0.3, False)
                                    for m, kw in enumerate((0.0, 1.0, 1.0, 0.0, 0.0))]),
               ("month_count", lambda: outs.append(o.month_count("2026-01")))]
    elif name == "cusum":
        o = obj
        if o is None:
            o = Cusum(threshold=5.0, drift=0.1)
            o.load(data)
        ops = [("update", lambda: o.update(now, 0.5)),
               ("release_if_starved", lambda: o.release_if_starved(now, 72.0)),
               ("stat", lambda: outs.append(o.stat))]
    elif name == "snapshots":
        o = obj or SnapshotRing.from_dict(data)
        ops = [("due", lambda: o.due(now)), ("observe_bias", lambda: o.observe_bias(now, 0.1, True)),
               ("best_restore", o.best_restore),
               ("take", lambda: o.take(now, {"comfort": {}}, {"temperature_bias": 0.1}, True))]
    elif name == "dhw_profile":
        o = obj
        if o is None:
            o = DhwProfileLearner(FakeHass(), "fz", ThermalParameters(), frozen=lambda *a: None,
                                  heating_active=lambda: False, external_heat_active=lambda: False)
            asyncio.run(o.profile_store.async_save(data))
            asyncio.run(o.async_load_profile())
        ops = [("pattern_for", lambda: outs.append([o.pattern_for(False), o.pattern_for(True)])),
               ("payload", lambda: outs.append(o.payload())),
               # the #42 restore path hands a snapshot's dhw_profile to apply_payload
               ("apply_payload", lambda: o.apply_payload(data if isinstance(data, dict) else {}))]
    if hasattr(o, "as_dict"):
        # as_dict output must also survive the real Store's JSON write
        ops.append(("as_dict", lambda: outs.append(json.loads(json.dumps(o.as_dict())))))
    raised = []
    for op, fn in ops:
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            raised.append((op, type(e).__name__, str(e)[:80]))
    return o, outs, raised


class _AwareDatetime(datetime):
    @classmethod
    def fromisoformat(cls, s):
        v = datetime.fromisoformat(s)
        return v if v.tzinfo is not None else v.replace(tzinfo=timezone.utc)


def _best_restore_fixed(self):
    orig_isf = snap_mod.np.isfinite
    def safe_isfinite(x):
        try:
            return orig_isf(float(x))
        except (TypeError, ValueError, OverflowError):
            return False
    with mock.patch.object(snap_mod.np, "isfinite", safe_isfinite):
        return _orig_best_restore(self)


_orig_best_restore = SnapshotRing.best_restore


def main():
    rng = random.Random(SEED)
    healthy = healthy_payloads()
    stats = {}
    sigs = defaultdict(Counter)
    examples = {}
    # healthy control first
    for name, payload in healthy.items():
        data = store_roundtrip(payload)
        _, outs, raised = drive(name, data, 0, None)
        assert not raised, (name, raised)
        assert finite_tree(outs), name
    for name, payload in healthy.items():
        s = Counter()
        for i in range(N):
            mutant, tags = mutate(rng, payload)
            try:
                data = store_roundtrip(mutant)
            except Exception as e:  # stub refuses to serialise (e.g. never)
                s["unserialisable"] += 1
                continue
            s["mutants"] += 1
            logs0 = _Count.n
            try:
                obj, outs, raised = drive(name, data, 0, None)
            except Exception as e:  # loader itself raised
                s["loader_raise"] += 1
                sig = (name, "LOADER", type(e).__name__)
                sigs[name][sig] += 1
                examples.setdefault(sig, (tags, str(e)[:80]))
                continue
            logs = _Count.n - logs0
            if raised:
                s["cycle1_raise"] += 1
                _, _, raised2 = drive(name, data, 1, obj)
                if {r[0] for r in raised} & {r[0] for r in raised2}:
                    s["cycle2_repeat"] += 1
                for op, et, msg in raised:
                    sig = (name, op, et)
                    sigs[name][sig] += 1
                    examples.setdefault(sig, (tags, msg))
            if not finite_tree(outs):
                s["nonfinite_output"] += 1
                examples.setdefault((name, "NONFINITE", ""), (tags, ""))
            if logs > 1:
                s["multi_log"] += 1
        stats[name] = s
    return stats, sigs, examples


if FIX_TS:
    ctx = [mock.patch.object(m, "datetime", _AwareDatetime) for m in (comfort_learning, curve_learning, snap_mod)]
else:
    ctx = []
if not STUB_JSON:
    import homeassistant.helpers.storage as _hs
    ctx.append(mock.patch.object(_hs, "json", _HaJson))
if FIX_SNAP:
    ctx.append(mock.patch.object(SnapshotRing, "best_restore", _best_restore_fixed))
for c in ctx:
    c.start()
stats, sigs, examples = main()
for c in ctx:
    c.stop()
print(f"# seed={SEED} n={N} fix_ts={FIX_TS} fix_snap={FIX_SNAP} stub_json={STUB_JSON}")
tot = Counter()
for name, s in stats.items():
    for k in ("unserialisable", "mutants", "loader_raise", "cycle1_raise", "cycle2_repeat", "nonfinite_output", "multi_log"):
        print(f"RESULT {name}.{k}={s.get(k, 0)} count")
        tot[k] += s.get(k, 0)
for k, v in tot.items():
    print(f"RESULT total.{k}={v} count")
for name, c in sigs.items():
    for sig, n in c.most_common():
        tags, msg = examples[sig]
        print(f"SIG {'|'.join(sig)} n={n} e.g. {tags} :: {msg}")
for sig, (tags, _) in examples.items():
    if sig[1] == "NONFINITE":
        print(f"NONFINITE {sig[0]} e.g. {tags}")
p, t = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={p / t if t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins={sw}")
