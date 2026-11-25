#!/usr/bin/env python3
# Metric: how many times HeatPumpOptimizer.optimize consults _safety_release_steps (repair rounds + the final check) on a
#   manual space plan that never converges (the stub tests/manual_plan.py:test_release_always_resolves uses: one more
#   forced-off step released per round), 24 x 1 h horizon, every step pinned off.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_68ef00f470ecea8d.py
# EXPECTED RESULT release_calls_baseline=4 count  (3 rounds, then the out-of-rounds check that abandons the pins)
# EXPECTED RESULT release_calls_mutant=7 count  (6 rounds + the final check: three extra full solves)
# EXPECTED RESULT moved=1 count
# EXPECTED RESULT released_baseline=24 / released_mutant=24 count  (both end by abandoning every pin: the check the suite
#   makes, `len(manual_released_space) == N`, holds in both arms)
# EXPECTED RESULT real_rounds_used: the rounds the REAL _safety_release_steps needs on the same all-off plan (reach; if
#   it is <= 3 the constant is unobservable on that input)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g19 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize, the manual-plan repair
#   loop `for _ in range(_SAFETY_REPAIR_ROUNDS)` (optimizer.py:4514; constant at optimizer.py:2385; also read at 5163).
# Perturbation: `_SAFETY_REPAIR_ROUNDS = 3` -> `_SAFETY_REPAIR_ROUNDS = 6` (CONST 68ef00f470ecea8d), applied in memory with
#   mock.patch.object on the module constant (read at loop entry). Direction: release_calls 4 -> 7.
# Null control: no pins (the repair loop is not entered): 0 release calls in both arms.
# Inputs tried: the never-converging stub; the real release rule on an all-off 24 h winter plan; no pins.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time, warnings
from pathlib import Path
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
_T0, _C0 = time.perf_counter(), (time.process_time(), time.thread_time())


def mutated(mod, owner, name, lineno, old, new):
    """`name` (a function of `owner`, a module or class) recompiled from its own source with line `lineno`
    replaced, `old` -> `new`; the anchor must match exactly. Line numbers are kept, so a traceback names the file line."""
    fn = owner.__dict__[name] if isinstance(owner, type) else getattr(owner, name)
    lines, start = inspect.getsourcelines(fn)
    i = lineno - start
    assert lines[i].rstrip("\n") == old, f"anchor moved: {lines[i]!r} != {old!r}"
    lines[i] = new + "\n"
    ns = dict(mod.__dict__)
    exec(compile("\n" * (start - 1) + textwrap.dedent("".join(lines)), mod.__file__, "exec"), ns)
    return ns[name]


def tail():
    pc, tc = time.process_time() - _C0[0], time.thread_time() - _C0[1]
    print(f"RESULT wall={time.perf_counter() - _T0:.2f} s (provisional)")
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        for ln in open("/proc/vmstat"):
            if ln.startswith("pswpin "):
                sw = int(ln.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={sw}")
import math  # noqa: E402
from datetime import datetime  # noqa: E402
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import optimizer as O  # noqa: E402
from custom_components.heatpump_optimizer.thermal_model import ThermalParameters, ThermalState, ThermalModel  # noqa: E402

N = 24
assert O._SAFETY_REPAIR_ROUNDS == 3
H = O.HeatPumpOptimizer
real_release = H._safety_release_steps


def solve(pins):
    opt = H(ThermalModel(ThermalParameters()), O.OptimizationConfig(
        horizon_hours=N, time_step_minutes=60, target_temp=21.0, min_temp=19.0, max_temp=23.0))
    pr = np.full(N, 2.0)
    pr[:6] = 0.5
    return opt.optimize(inputs=O.SolveInputs(
        state=ThermalState(room_temperature=20.0, slab_temperature=22.0, outdoor_temperature=-10.0),
        start_time=datetime(2026, 1, 15, 12, 0),
        forecast=O.ForecastSeries(prices=pr, outdoor_temps=np.full(N, -10.0)),
        limits=O.SolveLimits(space_pins=pins)))


def run(stub, pins, rounds):
    calls = []

    def spy(self, result, tmin, sp, dp):
        calls.append(1)
        if stub:
            if sp is None:
                return [], []
            free = [i for i in range(len(sp)) if not math.isnan(float(sp[i])) and float(sp[i]) < 0.5]
            return free[:1], []
        return real_release(self, result, tmin, sp, dp)

    with mock.patch.object(H, "_safety_release_steps", spy), mock.patch.object(O, "_SAFETY_REPAIR_ROUNDS", rounds):
        r = solve(None if pins is None else pins.copy())
    return len(calls), len(r.manual_released_space)


cb, rb = run(True, np.zeros(N), 3)
cm, rm = run(True, np.zeros(N), 6)
real_b, real_rel_b = run(False, np.zeros(N), 3)
real_m, real_rel_m = run(False, np.zeros(N), 6)
nb, _ = run(True, None, 3)
nm, _ = run(True, None, 6)
print(f"RESULT release_calls_baseline={cb} count")
print(f"RESULT release_calls_mutant={cm} count")
print(f"RESULT moved={int(cb != cm)} count")
print(f"RESULT released_baseline={rb} count")
print(f"RESULT released_mutant={rm} count")
print(f"RESULT real_release_calls_baseline={real_b} count")
print(f"RESULT real_release_calls_mutant={real_m} count")
print(f"RESULT real_released_baseline={real_rel_b} count")
print(f"RESULT real_released_mutant={real_rel_m} count")
print(f"RESULT null_release_calls={nb}/{nm} count")
tail()
