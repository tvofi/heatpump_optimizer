#!/usr/bin/env python3
# Metric: over five HeatPumpOptimizerCoordinator._update_current_state cycles on a two-tank install whose wood probes
#   read healthy, healthy, unavailable, unavailable, healthy: the count of wood-tank WARNING and two-tank INFO
#   records the coordinator logger emits, logging format errors among them, and the published
#   wood_tank_temperature per cycle.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_8ab42c4ab9755537.py
# Expected: (warnings,infos,format_errors) (1, 2, 0) -> (1, 4, 1); temps identical; null_moved=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g10, 4 vCPU Intel Xeon @ 2.30GHz, 16 GB.
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._update_current_state
#   (coordinator.py:6747 `if wood_mean is None and had:` / 6752 `elif wood_mean is not None and not had:`).
# Perturbation: mutant 8ab42c4ab9755537, line 6752 `and` -> `or`, in memory (the coroutine recompiled from its own source and attached
#   with mock.patch.object for the mutant arm only). Direction: the activation INFO repeats on a held healthy cycle and a second stale cycle formats %.1f with None: infos 2 -> 4, format errors 0 -> 1.
# Inputs: live coordinator (tests/harness FakeHass/FakeEntry) configured with wood_tank_top/bottom entities;
#   ThermalParameters.two_tank_modelled forced True by a PropertyMock (topology_layout == TOPOLOGY_TWO_TANK_4WAY in
#   production); the probe states are rewritten between cycles; asyncio.run per cycle.
# Null control: a single healthy first read (both arms log the activation INFO alike); temps_moved also reports
#   whether the published temperature moved (it must not: the guards only choose a log line).
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

OLD = "elif wood_mean is not None and not had:"
NEW = "elif wood_mean is not None or not had:"
NULL = ("60.0",)
from custom_components.heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

NAME = "_update_current_state"
WOOD = {"wood_tank_top_entity": "sensor.wood_top", "wood_tank_bottom_entity": "sensor.wood_bottom"}
# The wood probe per cycle: healthy, healthy, unavailable, unavailable, healthy.
SEQ = ("60.0", "60.0", "unavailable", "unavailable", "58.0")


def drive(mutated, seq=SEQ):
    """Five _update_current_state cycles; (warnings, infos, format errors, wood temperature per cycle)."""
    c = make_coord(WOOD, {"sensor.wood_top": FakeState("60.0", unit="°C"),
                          "sensor.wood_bottom": FakeState("50.0", unit="°C")})
    temps = []
    with arm(NAME, OLD, NEW, mutated), \
            mock.patch.object(ThermalParameters, "two_tank_modelled", new_callable=mock.PropertyMock, return_value=True), \
            counting("ood tank") as wood_log, counting("Two-tank model active") as two_log:
        for v in seq:
            for eid in ("sensor.wood_top", "sensor.wood_bottom"):
                c.hass.states.set(eid, FakeState(v, unit="°C"))
            asyncio.run(c._update_current_state())
            t = c._current_state.wood_tank_temperature
            temps.append(None if t is None else round(t, 3))
    hits = wood_log.hits + [h for h in two_log.hits if h not in wood_log.hits]
    warn = sum(1 for lv, _ in hits if lv == "WARNING")
    info = sum(1 for lv, _ in hits if lv == "INFO")
    fmt = sum(1 for _, msg in hits if msg.startswith("<format error>"))
    return warn, info, fmt, tuple(temps)


b, m = drive(False), drive(True)
print(f"RESULT wood_logs_baseline=(warnings,infos,format_errors,temps){b}")
print(f"RESULT wood_logs_mutant=(warnings,infos,format_errors,temps){m}")
print(f"RESULT temps_moved={int(b[3] != m[3])} count")
print(f"RESULT null_moved={int(drive(False, NULL) != drive(True, NULL))} count (null input {NULL})")
tail()
