"""D3-s1 (D3.M4): are get_current_action's per-key length guards live?

Metric: of the `if result.X and i < len(result.X)` guards in
optimizer.py:HeatPumpOptimizer.get_current_action, how many change the
returned action (or raise) when `and` is flipped to `or`, on a plan whose
optional schedules are SHORTER than power_schedule and `now` is in the last
step. Count key: the guard line whose in-memory mutant's output differs from
the unmutated method's output on the same plan.
Command:
  PYTHONPATH=tests/hastub python dev/audit/rounds/round10/D3/s1/action_guards.py [--equal]
Expected: RESULT live_guards=12 count (exact); RESULT guards=12 count.
Perturbation: --equal gives every optional schedule power_schedule's length
-> live_guards drops to 0 (the guards matter only for a short schedule).
Baseline 17f1c55fad1b; machine: owner's 8-core Mac (Darwin 25.6). Count, no timing.
The mutation is in memory (the method re-compiled from its source and
patched onto the class); nothing on disk changes.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, re, sys, textwrap, time
from unittest import mock
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "custom_components")
import heatpump_optimizer.optimizer as opt  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402

PATH = opt.__file__
SRC = open(PATH).read()
GUARD = re.compile(r"if result\.(\w+) and i < len\(result\.\1\)")
EQUAL = "--equal" in sys.argv
N = 4


def plan(mod):
    t0 = datetime(2026, 1, 15, 12, tzinfo=timezone.utc)
    short = N if EQUAL else 2
    r = mod.OptimizationResult(
        power_schedule=[1.0] * N, room_temp_trajectory=[21.0] * N,
        slab_temp_trajectory=[22.0] * N,
        timestamps=[t0 + timedelta(minutes=15 * k) for k in range(N)],
        prices=[1.0] * N, predicted_cost=0.0, baseline_cost=0.0,
        predicted_savings=0.0, savings_percentage=0.0,
        optimal_setpoints=[21.0] * N, status="optimal")
    for name in ("displace_schedule", "dhw_power_schedule", "baseline_power_schedule",
                 "valve_target_schedule", "upper_setpoints", "lower_setpoints",
                 "solar_gain_trajectory", "dhw_temp_trajectory"):
        setattr(r, name, [0.5] * short)
    r.heat_pump_on_schedule = [True] * short
    r.space_reasons = ["r"] * short
    r.dhw_reasons = ["r"] * short
    return r, r.timestamps[-1] + timedelta(minutes=1)


def action(mod):
    o = mod.HeatPumpOptimizer(ThermalModel(ThermalParameters()), mod.OptimizationConfig())
    r, now = plan(mod)
    try:
        return repr(sorted(o.get_current_action(r, now).items()))
    except Exception as exc:  # noqa: BLE001 - a raise IS the observed difference
        return "RAISE " + type(exc).__name__


def mutant_method(lineno):
    """get_current_action re-compiled from source with one guard flipped, in
    the module's own globals, then patched onto the class (mock.patch.object)."""
    fn = opt.HeatPumpOptimizer.get_current_action
    first = fn.__code__.co_firstlineno
    src = inspect.getsource(fn).split("\n")
    k = lineno - first
    src[k] = src[k].replace(" and i < len(", " or i < len(", 1)
    ns = {}
    code = compile("\n" * (first - 1) + textwrap.dedent("\n".join(src)), PATH, "exec")
    exec(code, opt.__dict__, ns)
    return ns["get_current_action"]


base = action(opt)
guards = [i + 1 for i, ln in enumerate(SRC.split("\n")) if GUARD.search(ln)
          and i + 1 > SRC[:SRC.index("def get_current_action")].count("\n")
          and i + 1 < SRC[:SRC.index("def optimize_in_process")].count("\n")]
live = 0
for ln in guards:
    with mock.patch.object(opt.HeatPumpOptimizer, "get_current_action", mutant_method(ln)):
        out = action(opt)
    diff = out != base
    live += diff
    print("GUARD optimizer.py:%d %s -> %s" % (ln, GUARD.search(SRC.split("\n")[ln - 1]).group(1),
                                              "DIFFERS (" + out[:40] + ")" if diff else "same"))
print("RESULT guards=%d count" % len(guards))
print("RESULT live_guards=%d count" % live)
print("RESULT thread_factor=%.3f" % (time.process_time() / max(time.thread_time(), 1e-9)))
print("RESULT load1=%.2f" % os.getloadavg()[0])
print("RESULT swapins=0")
