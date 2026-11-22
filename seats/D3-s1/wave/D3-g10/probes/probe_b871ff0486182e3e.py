#!/usr/bin/env python3
# Metric: the roof-snow accumulator (cm) and the solar-damping verdict HeatPumpOptimizerCoordinator._update_snow_memory
#   returns for one call after a gap since the last call, at a constant snowfall rate.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_b871ff0486182e3e.py
# Expected: gap12h_rate0.2_baseline=(1.2, False); gap12h_rate0.2_mutant=(2.4, True) (exact to 1e-6); null_moved=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g10, 4 vCPU Intel Xeon @ 2.30GHz, 16 GB.
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._update_snow_memory
#   (coordinator.py:7549 `self._snow_accum_cm += rate_now * min(dt_true, 6.0)`).
# Perturbation: mutant b871ff0486182e3e, `min(dt_true, 6.0)` -> `(dt_true)`, in memory (method recompiled from its own
#   source, attached with mock.patch.object for the mutant arm only). Direction: after a 12 h outage one 0.2 cm/h
#   sample books 2.4 cm instead of 1.2 cm, crossing SNOW_HEAVY_CM (2.0): the roof is declared snowed over and solar
#   is damped for SNOW_ROOF_DAYS (False -> True). The code comment states the bound's purpose: "a long outage
#   cannot book a blizzard from one rate sample".
# Inputs: live coordinator (tests/harness FakeHass/FakeEntry) with snow_roof_factor_enabled; accumulator 0, the last
#   call 12 h before NOW, snowfall rate 0.2 cm/h.
# Null control: gaps at or under the 6 h bound (3 h and exactly 6 h), where min() is the identity.
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

OLD = "self._snow_accum_cm += rate_now * min(dt_true, 6.0)"
NEW = "self._snow_accum_cm += rate_now * (dt_true)"
CASES = {"gap12h_rate0.2": (0.0, 12.0, 0.2)}
NULLS = [(0.0, 3.0, 0.2), (0.0, 6.0, 0.2)]
from datetime import datetime, timedelta, timezone  # noqa: E402
import numpy as np  # noqa: E402

NAME = "_update_snow_memory"
NOW = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)


def drive(mutated, accum, gap_h, rate):
    """One _update_snow_memory call: (accumulator cm, solar damped?)."""
    c = make_coord({"snow_roof_factor_enabled": True})
    c._snow_accum_cm, c._snow_accum_last, c._last_heavy_snow = accum, NOW - timedelta(hours=gap_h), None
    with arm(NAME, OLD, NEW, mutated):
        damped = c._update_snow_memory(NOW, np.array([rate] * 48, dtype=float))
    return round(c._snow_accum_cm, 6), bool(damped)


for label, args in CASES.items():
    b, m = drive(False, *args), drive(True, *args)
    print(f"RESULT {label}_baseline=(accum_cm,damped){b}")
    print(f"RESULT {label}_mutant=(accum_cm,damped){m}")
moved = sum(int(drive(False, *a) != drive(True, *a)) for a in NULLS)
print(f"RESULT null_moved={moved} count over {len(NULLS)} null inputs (accum, gap_h, rate) {NULLS}")
print(f"RESULT inputs_tried={len(CASES) + len(NULLS)} count")
tail()
