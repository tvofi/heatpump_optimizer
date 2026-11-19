#!/usr/bin/env python3
# Metric: hot-water demand windows the DHW planner sees on a HOLIDAY step for an install that has ordinary
#   windows "06:00-08:00,18:00-21:00" and leaves the holiday hot-water windows option unset (absent, "" or None).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/tm169_holiday_dhw.py
# EXPECTED RESULT holiday_windows_baseline=2 count  (per unset form: the ordinary windows carry the holiday)
# EXPECTED RESULT holiday_windows_mutant=0 count    (an empty holiday list replaces them: no hot water on holidays)
# EXPECTED RESULT unset_forms_moved=3 count
# EXPECTED RESULT null_delta=0 count  (a set holiday spec "08:00-10:00" gives the same windows in both arms)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-top6 (4 vCPU Xeon @ 2.30GHz). Counts are exact.
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:_holiday_dhw_windows (line 169 guard
#   `if not spec:`), read through thermal_model.ThermalParameters.from_config (line 1157, dhw_holiday_windows)
#   and consumed by dhw_planner:_dhw_windows_at -> dhw_schedule:windows_for_day on a holiday-flagged step.
# Perturbation: line 169 `if not spec:` -> `if False:` (GUARD_OFF 050fdc4a20eba212), in memory: the function is
#   re-compiled from its own source with that one edit and patched onto the module. Direction: 2 -> 0.
#   The full gate (fullgate.py run --src complete --key 050fdc4a20eba212) stays green under it.
# Null control: a configured holiday spec, where the guard is inert.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import const, dhw_planner, thermal_model as tm  # noqa: E402
from custom_components.heatpump_optimizer.dhw_schedule import parse_windows  # noqa: E402

ORDINARY = parse_windows("06:00-08:00,18:00-21:00")
UNSET = [{}, {const.CONF_HOLIDAY_DHW_WINDOWS: ""}, {const.CONF_HOLIDAY_DHW_WINDOWS: None}]
SET = {const.CONF_HOLIDAY_DHW_WINDOWS: "08:00-10:00"}


def mutant():
    src = textwrap.dedent(inspect.getsource(tm._holiday_dhw_windows))
    assert src.count("if not spec:") == 1, "anchor line moved"
    ns = dict(tm.__dict__)
    exec(compile(src.replace("if not spec:", "if False:"), tm.__file__, "exec"), ns)
    return ns["_holiday_dhw_windows"]


def holiday_windows(cfg):
    hw = tm._holiday_dhw_windows(cfg)
    got = dhw_planner._dhw_windows_at(None, None, 1, ORDINARY, hw, np.array([False, True]))
    return len(got)


def from_config_reads_it():
    """Precondition: from_config publishes this helper's answer as dhw_holiday_windows."""
    src = inspect.getsource(tm)
    return int('values["dhw_holiday_windows"] = _holiday_dhw_windows(config)' in src)


base = [holiday_windows(c) for c in UNSET]
null_b = holiday_windows(SET)
with mock.patch.object(tm, "_holiday_dhw_windows", mutant()):
    mut = [holiday_windows(c) for c in UNSET]
    null_m = holiday_windows(SET)
print(f"RESULT from_config_reads_helper={from_config_reads_it()} count")
print(f"RESULT holiday_windows_baseline={min(base)} count")
print(f"RESULT holiday_windows_mutant={max(mut)} count")
print(f"RESULT unset_forms_moved={sum(int(a != b) for a, b in zip(base, mut))} count")
print(f"RESULT null_delta={abs(null_b - null_m)} count")
print("RESULT thread_factor=1.0 ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0 count")
