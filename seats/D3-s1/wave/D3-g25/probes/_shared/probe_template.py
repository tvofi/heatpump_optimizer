#!/usr/bin/env python3
# Probe for D3 u1 full-gate key @KEY@ (box D3-g25, seat D3-s1, round 11).
# Metric: @METRIC@ of HeatPumpOptimizer.get_current_action's returned action on one hand-built
#   OptimizationResult (or "raised:<exception>" when the call raises), baseline arm vs mutant arm.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g25/probes/probe_@KEY@.py
# Expected: RESULT moved=1 count on the first (distinguishing) input, direction @DIR@;
#   RESULT null_moved=0 count on the input marked [null]. Exact (no tolerance: string/bool/key outcomes).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g25 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB),
#   provisional; nothing here is a timing.
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer.get_current_action
#   (optimizer.py:@LINE@ `@OLDTXT@`).
# Perturbation: line @LINE@ -> `@NEWTXT@` (mutant @KEY@), applied in memory only: the method is
#   recompiled from its own source with that one line replaced and patched onto the class for the
#   mutant arm (mock.patch.object); the tree on disk is never edited.
# Count key: the value the production seam delivers (the action dict get_current_action returns).
# Null control: the input marked [null], where the mutated comparison evaluates the same in both arms.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest import mock


def repo_root(start):
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
_c0, _t0 = time.process_time(), time.thread_time()
from custom_components.heatpump_optimizer import optimizer  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer, OptimizationConfig, OptimizationResult)
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402

SPEC = @SPEC@
KIND = "@KIND@"
METRIC = "@METRIC@"


def mutant_method():
    src = textwrap.dedent(inspect.getsource(HeatPumpOptimizer.get_current_action))
    old, new = SPEC["old"].strip(), SPEC["new"].strip()
    assert src.count(old) == 1, f"anchor line not found exactly once (tree not at baseline?): {old!r}"
    ns = dict(optimizer.__dict__)
    exec(compile(src.replace(old, new, 1), optimizer.__file__, "exec"), ns)
    return ns["get_current_action"]


T0 = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)


def plan(n, powers=None, **extra):
    p = list(powers) if powers is not None else [2.0] * n
    r = OptimizationResult(
        power_schedule=p, room_temp_trajectory=[21.0] * (n + 1), slab_temp_trajectory=[22.0] * (n + 1),
        timestamps=[T0 + timedelta(minutes=15 * k) for k in range(n)], prices=[1.0] * n,
        predicted_cost=1.0, baseline_cost=1.0, predicted_savings=0.0, savings_percentage=0.0,
        optimal_setpoints=[21.0 + 0.1 * k for k in range(n)], status="optimal")
    for k, v in extra.items():
        setattr(r, k, v)
    return r


def scenario(a):
    """(result, now) for one input of this key's kind."""
    if KIND == "prehorizon":
        return plan(a["n"]), T0 - timedelta(seconds=a["skew_s"])
    if KIND == "short":
        r = plan(4)
        setattr(r, a["field"], [0.5] * 2)
        return r, T0 + timedelta(minutes=15 * a["at"])
    if KIND == "power":
        return plan(4, [a["p"]] * 4, heat_pump_on_schedule=[True] * 4), T0 + timedelta(minutes=15)
    if KIND == "dhw":
        return plan(4, dhw_power_schedule=[a["d"]] * 4), T0 + timedelta(minutes=15)
    if KIND == "target":
        info = {} if a["t"] is None else {"dhw_target_temperature": a["t"]}
        return plan(4, predictive_info=info), T0 + timedelta(minutes=15)
    raise ValueError(KIND)


def outcome(opt, a):
    r, now = scenario(a)
    try:
        act = opt.get_current_action(r, now)
    except Exception as exc:  # the number names it
        return f"raised:{type(exc).__name__}"
    if METRIC == "outcome":
        key = a.get("key")
        if key is not None:
            return f"{key}={act[key]!r}" if key in act else f"{key}=absent"
        return f"mode={act['mode']},power={act['power']},setpoint={act['setpoint']}"
    return repr(act.get(METRIC, "absent"))


def optimizer_instance():
    # A modulating pump with a 0.5..3.0 kW band, so the p_norm boundaries 0.4/0.7/0.9 are exact floats
    # ((1.5-0.5)/2.5 == 0.4, (2.25-0.5)/2.5 == 0.7, (2.75-0.5)/2.5 == 0.9).
    return HeatPumpOptimizer(ThermalModel(ThermalParameters(min_electrical_power=0.5, max_electrical_power=3.0)),
                             OptimizationConfig())


opt = optimizer_instance()
mut = mutant_method()
moved_any = 0
for idx, (label, a) in enumerate(SPEC["inputs"]):
    b = outcome(opt, a)
    with mock.patch.object(HeatPumpOptimizer, "get_current_action", mut):
        m = outcome(optimizer_instance(), a)
    mv = int(b != m)
    print(f"INPUT {idx}: {label}: baseline {b} | mutant {m} | moved {mv}")
    if idx == 0:
        print(f"RESULT baseline_value={b}")
        print(f"RESULT mutant_value={m}")
        print(f"RESULT moved={mv} count")
    if "[null]" in label:
        print(f"RESULT null_moved={mv} count")
    moved_any |= mv
print(f"RESULT inputs_tried={len(SPEC['inputs'])} count")
print(f"RESULT moved_any={moved_any} count")
_pc, _tc = time.process_time() - _c0, time.thread_time() - _t0
print(f"RESULT thread_factor={_pc / _tc if _tc > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _sw = sum(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
except OSError:
    _sw = -1
print(f"RESULT swapins={_sw} count")
