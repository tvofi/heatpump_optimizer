#!/usr/bin/env python3
# D3-g12 step-4 probe for full-gate survivor 4403a4c7bec83d8f (audit round 11, seat D3-s1).
# Metric: state-machine lookups _price_entity_state makes with a falsy entity id for a config with no price entity (the API-price install), and whether the lookup raises under Home Assistant core's lookup shape (`get(id) or get(id.lower())`, modelled here: no homeassistant package is installed).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g12/probes/probe_4403a4c7bec83d8f.py
# Expected: falsy_lookups_baseline=0, falsy_lookups_mutant=1; ha_shape_raises_baseline=0, ha_shape_raises_mutant=1; return value None in both arms on the suite's FakeStates (exact: counts and values, no tolerance)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g12 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:_price_entity_state, line 3417
# Perturbation: key 4403a4c7bec83d8f GUARD_OFF, `if not entity_id:` -> `if False:`, in memory. Direction: 0 -> 1 falsy lookups; a None id reaches `None.lower()` under core's shape.
# Null control: a configured price entity id, where the guard is false either way: identical lookups and state.
# Count key: the value the production symbol returns or stores (never an input attribute).
# Runs from the repository root, writes nothing; the mutant lives only in memory.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, logging, sys, textwrap, time
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

_P0, _T0 = time.process_time(), time.thread_time()


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


def mutated(obj, module, old, new):
    """``obj`` (a function, or a method/classmethod read off its class) re-compiled
    from its own source with the one-line mutant applied, in ``module``'s namespace."""
    raw = obj.__func__ if hasattr(obj, "__func__") else obj
    full = inspect.getsource(raw)
    cut = len(full) - len(full.lstrip(" "))  # the def's own indent, which dedent strips
    src = textwrap.dedent(full)
    old, new = old[cut:], new[cut:]
    assert src.count(old) == 1, f"anchor moved: {old!r}"
    ns = dict(module.__dict__)
    exec(compile(src.replace(old, new, 1), module.__file__, "exec"), ns)
    return ns[raw.__name__]


class _Count(logging.Handler):
    def __init__(self, needle):
        super().__init__(logging.DEBUG)
        self.needle, self.n = needle, 0

    def emit(self, record):
        if self.needle in record.getMessage():
            self.n += 1


def logged(logger_name, needle, fn):
    """How many records containing ``needle`` ``fn()`` logs on ``logger_name``."""
    lg = logging.getLogger(logger_name)
    h = _Count(needle)
    lg.addHandler(h)
    old = lg.level
    lg.setLevel(logging.DEBUG)
    try:
        fn()
    finally:
        lg.removeHandler(h)
        lg.setLevel(old)
    return h.n

from custom_components.heatpump_optimizer import coordinator as c
OLD = "    if not entity_id:"
mut = mutated(c._price_entity_state, c, OLD, "    if False:")


class Recording:
    """The suite's FakeStates shape (dict.get), counting lookups by a falsy id."""
    def __init__(self, states):
        self._s, self.falsy = dict(states), 0

    def get(self, entity_id):
        self.falsy += not entity_id
        return self._s.get(entity_id)


class CoreShape(Recording):
    """Home Assistant core's StateMachine.get shape: exact id, then the lower-cased id."""
    def get(self, entity_id):
        self.falsy += not entity_id
        return self._s.get(entity_id) or self._s.get(entity_id.lower())


def run(fn, states_cls, cfg):
    hass = SimpleNamespace(states=states_cls({"sensor.price": "STATE"}))
    try:
        value, raised = fn(hass, cfg), 0
    except Exception as err:  # noqa: BLE001 -- the count is the point
        value, raised = type(err).__name__, 1
    return value, hass.states.falsy, raised


for label, cfg in (("unset", {}), ("configured", {"price_entity": "sensor.price"})):
    for arm, fn in (("baseline", c._price_entity_state), ("mutant", mut)):
        v, n, _ = run(fn, Recording, cfg)
        _, _, r = run(fn, CoreShape, cfg)
        print(f"RESULT {label}_value_{arm}={v!r}")
        print(f"RESULT {label}_falsy_lookups_{arm}={n} count")
        print(f"RESULT {label}_ha_shape_raises_{arm}={r} count")


def _swapins():
    try:
        for line in open("/proc/vmstat"):
            if line.startswith("pswpin "):
                return int(line.split()[1])
    except OSError:
        pass
    return 0


_p, _t = time.process_time() - _P0, time.thread_time() - _T0
print(f"RESULT thread_factor={(_p / _t) if _t > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={_swapins()}")
