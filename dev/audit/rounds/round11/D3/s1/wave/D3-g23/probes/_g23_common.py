"""Shared plumbing for box D3-g23's probes (audit round 11, D3-s1). Not a harness on its own.

Each probe_<key>.py imports this module (it sits beside them) to: pin BLAS threads before numpy,
locate the export root, re-compile one HeatPumpOptimizer method with a one-line mutant in memory
(the gate's tree is never edited), build the manual-plan optimizer bundle tests/manual_plan.py uses,
and print the contract's trailing RESULT lines (thread_factor, load1, swapins).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import contextlib, inspect, sys, textwrap, time
from datetime import datetime
from pathlib import Path
from unittest import mock

BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"


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
os.chdir(ROOT)
for _p in (str(ROOT / "tests" / "hastub"), str(ROOT / "tests"), str(ROOT / "custom_components"), str(ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np  # noqa: E402
from heatpump_optimizer import optimizer as om  # noqa: E402

OPT = om.HeatPumpOptimizer
_T0_PROC, _T0_THREAD = time.process_time(), time.thread_time()


def mutant_method(name, old, new):
    """HeatPumpOptimizer.<name> re-compiled with the single line `old` replaced by `new` (stripped match)."""
    raw = OPT.__dict__[name]
    fn = raw.__func__ if isinstance(raw, staticmethod) else raw
    src = textwrap.dedent(inspect.getsource(fn))
    lines = src.split("\n")
    hits = [i for i, l in enumerate(lines) if l.strip() == old.strip()]
    assert len(hits) == 1, f"anchor for {name} matched {len(hits)} lines: {old!r}"
    i = hits[0]
    indent = lines[i][: len(lines[i]) - len(lines[i].lstrip())]
    lines[i] = indent + new.strip()
    ns = dict(om.__dict__)
    exec(compile("\n".join(lines), om.__file__, "exec"), ns)
    obj = ns[name]
    return obj  # already a staticmethod object when the source carries the decorator


@contextlib.contextmanager
def mutated(name, old, new):
    with mock.patch.object(OPT, name, mutant_method(name, old, new)):
        yield


# ---- the manual-plan bundle, as tests/manual_plan.py:_build_optimizer builds it -------------
START = datetime(2026, 1, 15, 0, 0)
N = 96


def build(price_profile, weather_profile, dhw=True, **state_over):
    from profiles import house, prices, weather
    from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
    cfg = house()
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = dhw
    opt = om.OptimizationConfig(horizon_hours=24, time_step_minutes=15, target_temp=cfg["target_temperature"],
                                min_temp=cfg["min_temperature"], max_temp=cfg["max_temperature"])
    p = prices(price_profile, START)
    outdoor, wind, rain, solar = weather(weather_profile, START)
    base = dict(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=float(outdoor[0]),
                upper_floor_temperature=21.0, lower_floor_temperature=21.0, dhw_temperature=50.0,
                dhw_hours_since_legionella=20.0, buffer_tank_temperature=40.0)
    base.update(state_over)
    return OPT(ThermalModel(params), opt), ThermalState(**base), p, outdoor, wind, rain, solar


def solve(bundle, **kw):
    from profiles import solve_inputs
    o, state, p, outdoor, wind, rain, solar = bundle
    return o.optimize(inputs=solve_inputs(initial_state=state, prices=p, outdoor_temps=outdoor, wind_speeds=wind,
                                          precipitation=rain, solar_radiation=solar, start_time=START, **kw))


def plan_signature(res):
    """What a manual-plan solve delivers to the user: released steps and the two schedules (rounded)."""
    return (sorted(res.manual_released_space), sorted(res.manual_released_dhw),
            tuple(round(float(x), 6) for x in res.power_schedule),
            tuple(round(float(x), 6) for x in (res.dhw_power_schedule or [])))


def tail():
    proc, thr = time.process_time() - _T0_PROC, time.thread_time() - _T0_THREAD
    print(f"RESULT thread_factor={proc / thr if thr > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = "n/a"
    try:
        for line in open("/proc/vmstat"):
            if line.startswith("pswpin "):
                sw = line.split()[1]
    except OSError:
        pass
    print(f"RESULT swapins={sw}")


# ---- a direct call of HeatPumpOptimizer._safety_release_steps on a hand-built solved result --
from types import SimpleNamespace  # noqa: E402

NAN = float("nan")


def release_direct(room, floors, space_pins=None, dhw_traj=None, dhw_req=None, dhw_pins=None, n=None):
    """(release_space, release_dhw) the class's current _safety_release_steps returns, or the exception name.

    room[i+1] is the room temperature after step i (result.sensor_trajectory), floors[i] the comfort
    floor at step i, dhw_traj[i+1] the tank after step i, dhw_req[i] the DHW requirement.
    """
    n = len(room) - 1 if n is None else n
    result = SimpleNamespace(
        power_schedule=[0.0] * n,
        sensor_trajectory=lambda two_zone: list(room),
        dhw_power_schedule=[0.0] * (n if dhw_traj is None else len(dhw_traj) - 1),
        dhw_temp_trajectory=list(dhw_traj) if dhw_traj is not None else [],
    )
    me = SimpleNamespace(model=SimpleNamespace(params=SimpleNamespace(two_zone_enabled=False)),
                         _dhw_requirement=None if dhw_req is None else np.asarray(dhw_req, dtype=float),
                         _expand_off_blocks=OPT._expand_off_blocks)
    sp = None if space_pins is None else np.asarray(space_pins, dtype=float)
    dp = None if dhw_pins is None else np.asarray(dhw_pins, dtype=float)
    try:
        return OPT._safety_release_steps(me, result, np.asarray(floors, dtype=float), sp, dp)
    except Exception as exc:  # the mutant's failure is the number
        return type(exc).__name__


def pins(n, *blocks):
    a = np.full(n, NAN)
    for s, e, v in blocks:
        a[s:e] = v
    return a


def fmt(x):
    return str(x).replace(" ", "")


def result_diff(a, b, tol=1e-9):
    """Names of the OptimizationResult fields whose values differ between two solves (numbers to tol)."""
    out = []
    va, vb = vars(a), vars(b)
    for k in sorted(set(va) | set(vb)):
        if k == "solve_time_ms":  # wall time, not plan content
            continue
        x, y = va.get(k), vb.get(k)
        try:
            ax, ay = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
            if ax.shape != ay.shape or not np.allclose(ax, ay, atol=tol, rtol=0, equal_nan=True):
                out.append(k)
            continue
        except (TypeError, ValueError):
            pass
        if repr(x) != repr(y):
            out.append(k)
    return out


class Spy:
    """Wrap one HeatPumpOptimizer method and record a predicate of every call's arguments."""

    def __init__(self, name, probe):
        self.name, self.probe, self.calls, self.hits = name, probe, 0, 0

    def __enter__(self):
        inner = OPT.__dict__[self.name]
        fn = inner.__func__ if isinstance(inner, staticmethod) else inner
        spy = self

        def wrapper(*a, **kw):
            spy.calls += 1
            if spy.probe(*a, **kw):
                spy.hits += 1
            return fn(*a, **kw)

        self._patch = mock.patch.object(OPT, self.name, staticmethod(wrapper) if isinstance(inner, staticmethod) else wrapper)
        self._patch.__enter__()
        return self

    def __exit__(self, *exc):
        return self._patch.__exit__(*exc)


# The manual-plan scenarios a reach count runs: tests/manual_plan.py's safety-release cases and the
# distinguishing ones this box found (winter_extreme, cold start, short off blocks), pins of length N.
REACH_SCENARIOS = [
    (("winter_typical", "winter_cold", {}), {"space_pins": ((0, N, 0.0),)}),
    (("summer_typical", "summer_warm", {"room_temperature": 23.0, "dhw_temperature": 54.0}), {"space_pins": ((0, N, 0.0),)}),
    (("winter_typical", "winter_cold", {"dhw_temperature": 40.0}), {"dhw_pins": ((0, N, 0.0),)}),
    (("winter_typical", "winter_cold", {"dhw_hours_since_legionella": 200.0}), {"dhw_pins": ((0, N, 0.0),)}),
    (("winter_extreme", "winter_cold", {"room_temperature": 16.9, "slab_temperature": 16.9}), {"space_pins": ((0, 1, 0.0),)}),
    (("winter_extreme", "winter_cold", {"room_temperature": 17.0, "slab_temperature": 17.0}),
     {"space_pins": ((0, 2, 0.0), (2, 3, 1.0)), "dhw_pins": ((0, 8, 0.0),)}),
    (("winter_typical", "winter_cold", {}), {}),
]


def reach_solves():
    """Run every REACH_SCENARIOS solve; returns the number of solves."""
    for (pp, wp, st), pinspec in REACH_SCENARIOS:
        b = build(pp, wp, **st)
        kw = {k: pins(N, *v) for k, v in pinspec.items()}
        solve(b, **kw)
    return len(REACH_SCENARIOS)
