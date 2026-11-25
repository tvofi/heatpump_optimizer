#!/usr/bin/env python3
# Metric: OptimizationConfig._comfort_pair(when) -> (day C, night C, start h, end h), and how many of the 24 hourly
#   get_comfort_temp(hour, when) values move, on four dates of one config carrying weekday comfort 21/19.5 07-22,
#   weekend overrides 22/20 09-23 and holiday overrides 20/17 08-20 with holidays {Wed 2026-01-14, Sat 2026-01-17}:
#   the weekday holiday, the weekend holiday, a plain Saturday (2026-01-24) and a plain Wednesday (2026-01-21, null).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_e4affa9b9b540588.py
# EXPECTED RESULT holiday_wed unchanged; holiday_sat (20.0,17.0,8,20) -> (22.0,20.0,9,23) (the weekend overrides overwrite the holiday on a weekend holiday): hours_moved_holiday_sat=23 count (hour 08 reads 20.0 holiday-day vs 20.0 weekend-night: the one hour that coincides)
# EXPECTED RESULT null_hours_moved=0 count  (plain Wednesday: no override applies in either arm); tolerance exact
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g26 cloud (4 vCPU Intel Xeon @ 2.30GHz, 16 GB), venv-ci CPython; run while a GATE_JOBS=1 gate ran (counts exact, no timing reported).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:OptimizationConfig._comfort_pair line 2788
#   `return day, night, start, end` (the holiday branch return), read by get_comfort_temp / get_temp_bounds for every step of the plan.
# Perturbation: `return day, night, start, end` -> `pass` applied in memory (the method recompiled from its own source, patched onto the
#   class for the mutant arm only).
import sys
from datetime import date, datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g26_common as g  # noqa: E402  (thread pin first)
from unittest import mock  # noqa: E402
from heatpump_optimizer import optimizer as O  # noqa: E402
C = O.OptimizationConfig
MUT = g.mutant(C, "_comfort_pair", "return day, night, start, end", "pass", nth=0)  # line 2788: the holiday branch's return (the first of two)
cfg = C(comfort_temp_day=21.0, comfort_temp_night=19.5, day_start_hour=7, day_end_hour=22,
        comfort_temp_day_weekend=22.0, comfort_temp_night_weekend=20.0, day_start_hour_weekend=9, day_end_hour_weekend=23,
        holiday_comfort_day=20.0, holiday_comfort_night=17.0, holiday_day_start_hour=8, holiday_day_end_hour=20,
        holiday_dates=frozenset({date(2026, 1, 14), date(2026, 1, 17)}))
DATES = {"holiday_wed": date(2026, 1, 14), "holiday_sat": date(2026, 1, 17), "plain_sat": date(2026, 1, 24), "plain_wed": date(2026, 1, 21)}


def arm(mutated):
    out = {}
    with mock.patch.object(C, "_comfort_pair", MUT if mutated else C._comfort_pair):
        for name, d in DATES.items():
            when = datetime(d.year, d.month, d.day, 12, tzinfo=timezone.utc)
            out[name] = (cfg._comfort_pair(when), [cfg.get_comfort_temp(float(h), when) for h in range(24)])
    return out


b, m = arm(False), arm(True)
moved = 0
for name in DATES:
    print(f"RESULT pair_{name}_baseline={b[name][0]}")
    print(f"RESULT pair_{name}_mutant={m[name][0]}")
    hm = sum(1 for x, y in zip(b[name][1], m[name][1]) if x != y)
    if name != "plain_wed":
        moved += hm
    print(f"RESULT hours_moved_{name}={hm} count")
print(f"RESULT hours_moved_total={moved} count")
print(f"RESULT null_hours_moved={sum(1 for x, y in zip(b['plain_wed'][1], m['plain_wed'][1]) if x != y)} count")
g.trailer()
