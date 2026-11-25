#!/usr/bin/env python3
# Metric: total kWh over the items HeatPumpOptimizerCoordinator._narrative_view publishes ("narrative" payload key,
#   coordinator.py:10721) for one fixed 4-step plan, per OptimizationConfig.time_step_minutes; key = the payload items.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g08/probes/probe_7398de952c9d1510.py
# Expected: time step 15 and 1 min: moved 0 (null: the clamp is inactive at >= 1); 0.5 min: baseline 0.2 kWh,
#   mutant 0.1 kWh; 0 min: baseline 0.2 kWh, mutant 0.0 kWh. Exact (deterministic).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g08 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._narrative_view
#   (coordinator.py:10603 `dt_hours = max(..._opt_config.time_step_minutes, 1.0) / 60.0`).
# Perturbation: mutant 7398de952c9d1510 (CLAMP_DROP) drops the max(.., 1.0) floor, compiled in memory from the
#   method's source; direction: below a 1-minute step the published kWh/cost/hours shrink with the step.
# Reach: production never sets time_step_minutes off OptimizationConfig's 15.0 default (optimizer.py:2667 is the only
#   assignment in custom_components/), so the moving inputs (< 1 min) reach the line only by a direct construction.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path.cwd()))
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402

CLS = co.HeatPumpOptimizerCoordinator
OLD = 'dt_hours = max(getattr(self, "_ctx", self)._opt_config.time_step_minutes, 1.0) / 60.0'
NEW = 'dt_hours = (getattr(self, "_ctx", self)._opt_config.time_step_minutes) / 60.0'


def mutant(fn):
    src = textwrap.dedent(inspect.getsource(fn))
    assert src.count(OLD) == 1, "anchor line moved"
    ns = dict(co.__dict__)
    exec(compile(src.replace(OLD, NEW, 1), co.__file__, "exec"), ns)
    return ns[fn.__name__]


MUT = mutant(CLS._narrative_view)
RESULT_PLAN = SimpleNamespace(
    timestamps=["t0", "t1", "t2", "t3"], prices=[1.0, 2.0, 1.0, 2.0],
    power_schedule=[3.0, 3.0, 0.0, 0.0], space_reasons=["cheap_hour", "cheap_hour", "", ""],
    dhw_power_schedule=[0.0, 0.0, 6.0, 0.0], dhw_reasons=["", "", "dhw_reheat", ""],
)


def total_kwh(fn, step):
    me = SimpleNamespace(_optimization_result=RESULT_PLAN, _opt_config=SimpleNamespace(time_step_minutes=step),
                         hass=SimpleNamespace(config=SimpleNamespace(language="en")), currency="SEK")
    out = fn(me)
    return round(sum(float(i.get("kwh", 0.0)) for i in out["items"]), 6), len(out["lines"])


moved = 0
for step in (15.0, 1.0, 0.5, 0.0):
    b, m = total_kwh(CLS._narrative_view, step), total_kwh(MUT, step)
    moved += int(b != m)
    print(f"RESULT step={step}_baseline=kwh {b[0]} lines {b[1]}")
    print(f"RESULT step={step}_mutant=kwh {m[0]} lines {m[1]}")
print(f"RESULT steps_moved={moved} count of 4")
