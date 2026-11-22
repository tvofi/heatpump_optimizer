#!/usr/bin/env python3
# Metric: the curve learner's (bias, comfortable_days, resets) after one
#   HeatPumpOptimizerCoordinator._track_curve_comfort call, learner primed at comfortable_days=5, resets=0.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_ff56936f15fd4675.py
# Expected: margin_pos_bias_neg_baseline=(-1.0, 5, 0); margin_pos_bias_neg_mutant=(0.0, 0, 1)  (exact; null_moved=0)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g10, 4 vCPU Intel Xeon @ 2.30GHz, 16 GB.
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._track_curve_comfort
#   (coordinator.py:9273 `if margin <= 0.0 and self._curve_learner.bias < 0.0:`) -> curve_learning:CurveLearner.record_miss.
# Perturbation: mutant ff56936f15fd4675, `margin <= 0.0 and bias < 0.0` -> `or`, in memory (the method recompiled from its own
#   source and attached with mock.patch.object for the mutant arm only). Direction: a comfortable step (margin +0.5 K) with a learned bias -1 K resets it:
#   bias -1.0 -> 0.0, resets 0 -> 1, so a learned bias can never survive one update.
# Inputs: a live coordinator (tests/harness FakeHass/FakeEntry, curve_learning_enabled), the zone margin fixed through
#   coordinator.worst_zone_margin_k, freeze gates (_learning_frozen, learner_room_unread) held open.
# Null control: margin -0.3 with bias -1 (both operands true) and margin +0.5 with bias 0 (both false).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, types, logging, math, sys, textwrap, time
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

CLS = co.HeatPumpOptimizerCoordinator
_T0, _TT0 = time.process_time(), time.thread_time()


def mutant_of(name, old, new):
    """The method `name`, recompiled from its own source with `old` -> `new` (exactly once)."""
    src = textwrap.dedent(inspect.getsource(getattr(CLS, name)))
    assert src.count(old) == 1, f"anchor moved: {old!r}"
    ns = dict(co.__dict__)
    exec(compile(src.replace(old, new, 1), co.__file__, "exec"), ns)
    fn = ns[name]
    # Rebind to the LIVE module globals, so a mock.patch of a module name reaches both arms alike.
    live = types.FunctionType(fn.__code__, co.__dict__, fn.__name__, fn.__defaults__, fn.__closure__)
    live.__kwdefaults__ = fn.__kwdefaults__
    return live


@contextmanager
def arm(name, old, new, mutated):
    """Baseline arm (mutated False) or the mutant attached to the class for the block."""
    if not mutated:
        yield
        return
    with mock.patch.object(CLS, name, mutant_of(name, old, new)):
        yield


def make_coord(extra=None, states=None):
    cfg = {"tibber_token": "x", "weather_entity": "weather.home",
           "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor", **(extra or {})}
    st = {"sensor.indoor": FakeState("21.0", unit="°C"), "sensor.outdoor": FakeState("-5.0", unit="°C"), **(states or {})}
    return CLS(FakeHass(st), FakeEntry(data=cfg))


class LogCount(logging.Handler):
    """Counts records of the coordinator's logger matching a substring, by level."""
    def __init__(self, needle):
        super().__init__(logging.DEBUG)
        self.needle, self.hits = needle, []

    def emit(self, record):
        try:
            msg = record.getMessage()
        except Exception:  # noqa: BLE001 - a format error is itself a record
            msg = f"<format error> {record.msg}"
        if self.needle in msg or self.needle in str(record.msg):
            self.hits.append((record.levelname, msg))


@contextmanager
def counting(needle):
    lg = logging.getLogger(co.__name__)
    h, old = LogCount(needle), lg.level
    lg.addHandler(h); lg.setLevel(logging.DEBUG)
    try:
        yield h
    finally:
        lg.removeHandler(h); lg.setLevel(old)


def tail():
    cpu = time.process_time() - _T0
    print(f"RESULT probe_cpu_s={cpu:.2f} s provisional")
    tcpu = max(time.thread_time() - _TT0, 1e-9)
    print(f"RESULT thread_factor={cpu / tcpu:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
    except Exception:  # noqa: BLE001
        sw = "n/a"
    print(f"RESULT swapins={sw}")

NEW = "if margin <= 0.0 or self._curve_learner.bias < 0.0:"
CASES = {"margin_pos_bias_neg": (0.5, -1.0)}
NULLS = [(-0.3, -1.0), (0.5, 0.0)]
from datetime import datetime, timezone  # noqa: E402

NAME = "_track_curve_comfort"
OLD = "if margin <= 0.0 and self._curve_learner.bias < 0.0:"
NOW = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)


def drive(mutated, margin, bias):
    """One _track_curve_comfort call on a live coordinator; the zone margin is fixed via worst_zone_margin_k."""
    c = make_coord({"curve_learning_enabled": True})
    lr = c._curve_learner
    lr.bias, lr.comfortable_days, lr.resets = bias, 5, 0
    with arm(NAME, OLD, NEW, mutated), \
            mock.patch.object(co, "worst_zone_margin_k", lambda temps, floor: margin), \
            mock.patch.object(CLS, "_learning_frozen", lambda self, *a, **k: None), \
            mock.patch.object(co, "learner_room_unread", lambda cfg: None):
        c._curve_day = NOW.date().isoformat()
        c._track_curve_comfort(NOW)
    return (round(lr.bias, 6), lr.comfortable_days, lr.resets)


for label, (margin, bias) in CASES.items():
    b, m = drive(False, margin, bias), drive(True, margin, bias)
    print(f"RESULT {label}_baseline=(bias,comfortable_days,resets){b}")
    print(f"RESULT {label}_mutant=(bias,comfortable_days,resets){m}")
moved = sum(int(drive(False, mg, bs) != drive(True, mg, bs)) for mg, bs in NULLS)
print(f"RESULT null_moved={moved} count over {len(NULLS)} null inputs {NULLS}")
tail()
