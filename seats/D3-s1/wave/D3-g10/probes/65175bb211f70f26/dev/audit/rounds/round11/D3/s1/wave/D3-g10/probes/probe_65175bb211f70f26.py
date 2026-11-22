#!/usr/bin/env python3
# Metric: INFO records "No settled interval to diagnose yet" the coordinator logger emits, the returned report and
#   the refresh count, for one HeatPumpOptimizerCoordinator.async_diagnose_interval call whose worker returns None.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_65175bb211f70f26.py
# Expected: none_baseline=(1, None, 1); none_mutant=(0, None, 1); null_moved=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g10, 4 vCPU Intel Xeon @ 2.30GHz, 16 GB.
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator.async_diagnose_interval
#   (coordinator.py:10678 `if report is None:`).
# Perturbation: mutant 65175bb211f70f26, the guard -> `if False:`, in memory (the coroutine recompiled from its own
#   source, attached with mock.patch.object for the mutant arm only). Direction: infos 1 -> 0; the return value,
#   the stored diagnosis (real _store_diagnosis) and the refresh are unchanged.
# Inputs: live coordinator (tests/harness FakeHass/FakeEntry); coordinator._await_process patched to return the
#   worker's answer (None: no settled interval) without a process pool; async_request_refresh counted.
# Null control: the worker returns a report object (store patched to a recorder in both arms): neither arm logs.
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


NAME, OLD, NEW = "async_diagnose_interval", "if report is None:", "if False:"


def drive(mutated, report):
    c = make_coord()
    refreshes = []

    async def fake_await(hass, fn, *args):
        return report

    async def refresh():
        refreshes.append(1)

    patches = [mock.patch.object(co, "_await_process", fake_await), mock.patch.object(c, "async_request_refresh", refresh)]
    if report is not None:
        patches.append(mock.patch.object(co, "_store_diagnosis", lambda coord, rep: None))
    with arm(NAME, OLD, NEW, mutated), counting("No settled interval") as lg:
        for p in patches:
            p.start()
        try:
            out = asyncio.run(c.async_diagnose_interval())
        finally:
            for p in patches:
                p.stop()
    return sum(1 for lv, _ in lg.hits if lv == "INFO"), out, len(refreshes)


b, m = drive(False, None), drive(True, None)
print(f"RESULT none_baseline=(infos,report,refreshes){b}")
print(f"RESULT none_mutant=(infos,report,refreshes){m}")
rep = SimpleNamespace(verdict="ok")
print(f"RESULT null_moved={int(drive(False, rep) != drive(True, rep))} count (worker returns a report)")
tail()
