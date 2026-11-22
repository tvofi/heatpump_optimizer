#!/usr/bin/env python3
# Metric: DhwPlanner._dhw_legionella_due's (due, step) at a legionella interval of exactly 0 days, baseline vs mutant,
#   and the smallest interval each production write path accepts (config/options flow selector, the
#   set_parameters service schema).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_79ba0b9f6b3cf22d.py
# EXPECTED RESULT interval0_baseline=(False, None)  interval0_mutant=(True, 1)  (the separating input)
# EXPECTED RESULT null_moved=0 count  (intervals 0.01, 1, 7, 30 days: interval_hours > 0 in both arms)
# EXPECTED RESULT reach_flow_min_days=1  reach_service_min_days=0.01  (both refuse 0)
# EXPECTED RESULT reach_service_accepts_0=0 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g15 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._dhw_legionella_due, line 596
#   `and interval_hours > 0`.
# Perturbation: key 79ba0b9f6b3cf22d (CMP_BOUND) -> `and interval_hours >= 0`, in memory (method recompiled,
#   mock.patch.object). Direction: at interval 0 the baseline schedules no cycle, the mutant reads the cycle as
#   overdue and places one; no production path stores an interval of 0.
# Null control: every positive interval, identical in both arms.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _lg_common as c  # noqa: E402

fn = c.mutant("_dhw_legionella_due", "and interval_hours > 0", "and interval_hours >= 0")
h = c.horizon(n=96, hours_since=20.0)
p0 = c.params(dhw_legionella_interval_days=0.0)
b, m = c.due(p0, h), c.due(p0, h, fn=fn)
print(f"RESULT interval0_baseline={b[:3:2] if isinstance(b, tuple) else b}")
print(f"RESULT interval0_mutant={m[:3:2] if isinstance(m, tuple) else m}")
nm = 0
for days in (0.01, 1.0, 7.0, 30.0):
    for hs in (0.0, 20.0, 150.0, 1000.0):
        p = c.params(dhw_legionella_interval_days=days)
        hh = c.horizon(n=96, hours_since=hs)
        nm += c.differs(c.due(p, hh), c.due(p, hh, fn=fn))
print(f"RESULT null_moved={nm} count")
# Reach: the two write paths.
from custom_components.heatpump_optimizer import config_flow, services  # noqa: E402
from custom_components.heatpump_optimizer.const import CONF_DHW_LEGIONELLA_INTERVAL_DAYS  # noqa: E402
src = Path(config_flow.__file__).read_text()
line = next(l for l in src.splitlines() if "CONF_DHW_LEGIONELLA_INTERVAL_DAYS, DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS, _number(" in l)
print(f"RESULT reach_flow_min_days={line.split('_number(')[1].split(',')[0].strip()}")
v = services._positive(60)
acc0 = 0
try:
    v(0.0)
    acc0 = 1
except Exception:
    pass
lo = None
for x in (0.001, 0.005, 0.01, 0.02):
    try:
        v(x)
        lo = x
        break
    except Exception:
        continue
print(f"RESULT reach_service_min_days={lo}")
print(f"RESULT reach_service_accepts_0={acc0} count")
c.footer()
