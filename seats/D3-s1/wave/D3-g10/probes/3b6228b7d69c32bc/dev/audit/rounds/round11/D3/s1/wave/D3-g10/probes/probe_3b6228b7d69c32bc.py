#!/usr/bin/env python3
# Metric: the displacement (K, integer) HeatPumpOptimizerCoordinator.async_publish_ecl110_command hands
#   heat_curve.publish (the MQTT / entity write) and stores as _ecl110_current_displace, for one call.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes/probe_3b6228b7d69c32bc.py
# Expected: at_min_plus_bias_baseline=(-20, -20.0); at_min_plus_bias_mutant=(-24, -24.0) (exact);
#   over_max_baseline=(20, 20.0); over_max_mutant=(25, 25.0); null_moved=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g10, 4 vCPU Intel Xeon @ 2.30GHz, 16 GB.
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator.async_publish_ecl110_command
#   (coordinator.py:7693 `np.clip(displace_value, self._ecl110_displace_min, self._ecl110_displace_max)`).
# Perturbation: mutant 3b6228b7d69c32bc, the clip dropped (`(displace_value)`), in memory (the coroutine recompiled from
#   its own source, attached with mock.patch.object for the mutant arm only). Direction: a command at the configured
#   floor plus the learned curve bias leaves the range: -20 -> -24 K published.
# Reach: the action at the floor is production's own (coordinator.py:4104 sets displace_value to _ecl110_displace_min);
#   curve_learning_enabled adds CurveLearner.bias, bounded to [BIAS_MIN=-4.0, 0] (coordinator.py:7689-7690), before the
#   clip. The over-max case is a direct call (upstream producers stay within the range); it shows the bound both ways.
# Inputs: live coordinator (tests/harness FakeHass/FakeEntry), default range [-20, 20]; heat_curve.publish captured.
# Null control: in-range commands (2.0 K; 0.0 K with bias -1.0): the clip is the identity, the arms agree.
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

CASES = {"at_min_plus_bias": (-20.0, -4.0), "over_max": (25.0,)}
NULLS = [(2.0,), (0.0, -1.0)]
import custom_components.heatpump_optimizer.heat_curve as hc  # noqa: E402

NAME = "async_publish_ecl110_command"
OLD = "np.clip(displace_value, self._ecl110_displace_min, self._ecl110_displace_max)"
NEW = "(displace_value)"


def drive(mutated, value, bias=None):
    """One publish: (displace_int handed to heat_curve.publish, the coordinator's _ecl110_current_displace)."""
    c = make_coord({"curve_learning_enabled": bias is not None})
    if bias is not None:
        c._curve_learner.bias = bias
    sent = []

    async def publish(hass, entry, config, displace_int, legacy_payload, *, mode_off=False):
        sent.append(displace_int)

    with arm(NAME, OLD, NEW, mutated), mock.patch.object(co.heat_curve, "publish", publish):
        asyncio.run(c.async_publish_ecl110_command(value, True))
    return sent[-1], c._ecl110_current_displace


c0 = make_coord()
print(f"RESULT range=[{c0._ecl110_displace_min}, {c0._ecl110_displace_max}] K (the configured clamp, defaults)")
for label, args in CASES.items():
    b, m = drive(False, *args), drive(True, *args)
    print(f"RESULT {label}_baseline=(sent,current){b}")
    print(f"RESULT {label}_mutant=(sent,current){m}")
moved = sum(int(drive(False, *a) != drive(True, *a)) for a in NULLS)
print(f"RESULT null_moved={moved} count over {len(NULLS)} in-range inputs {NULLS}")
tail()
