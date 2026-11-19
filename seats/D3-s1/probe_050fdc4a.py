#!/usr/bin/env python3
# Metric: number of holiday hot-water windows ThermalParameters.from_config stores (dhw_holiday_windows) for a
#   config whose holiday-windows option is unset (absent / "" / None); None means "fall back to ordinary windows".
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/probe_050fdc4a.py
# EXPECTED RESULT holiday_unset_baseline_{absent,empty,none}=None  (no holiday override)
# EXPECTED RESULT holiday_unset_mutant_{absent,empty,none}=[]  (an empty list is an override: no hot water on holidays)
# EXPECTED RESULT unset_forms_moved=3 count
# EXPECTED RESULT null_delta=0 count  (a configured spec "08:00-10:00": guard inert, identical windows)
# EXPECTED RESULT reach_unset_calls=3 count  (production from_config calls with the option unset)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-rem (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:_holiday_dhw_windows, line 169
#   `if not spec:`, called from ThermalParameters.from_config (thermal_model.py:1157); consumed at
#   dhw_planner.py:964 (getattr(params, "dhw_holiday_windows")) by _dhw_windows_at -> windows_for_day.
# Perturbation: key 050fdc4a20eba212, `    if not spec:` -> `    if False:` (GUARD_OFF), in memory: the function is
#   re-compiled from its own source and patched onto the module for the mutant arm. Direction: None -> [].
# Null control: a configured holiday spec, where the guard is false either way.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))
from custom_components.heatpump_optimizer import const, thermal_model as tm  # noqa: E402

src = textwrap.dedent(inspect.getsource(tm._holiday_dhw_windows))
assert src.count("    if not spec:") == 1, "anchor moved"
ns = dict(tm.__dict__)
exec(compile(src.replace("    if not spec:", "    if False:", 1), tm.__file__, "exec"), ns)
mut = ns["_holiday_dhw_windows"]

KEY = const.CONF_HOLIDAY_DHW_WINDOWS
forms = {"absent": {}, "empty": {KEY: ""}, "none": {KEY: None}}


def holiday(cfg, fn=None):
    if fn is None:
        return tm.ThermalParameters.from_config(cfg).dhw_holiday_windows
    with mock.patch.object(tm, "_holiday_dhw_windows", fn):
        return tm.ThermalParameters.from_config(cfg).dhw_holiday_windows


moved = 0
for name, cfg in forms.items():
    b, m = holiday(cfg), holiday(cfg, mut)
    print(f"RESULT holiday_unset_baseline_{name}={b!r}")
    print(f"RESULT holiday_unset_mutant_{name}={m!r}")
    moved += b != m
print(f"RESULT unset_forms_moved={moved} count")
cfg = {KEY: "08:00-10:00"}
print(f"RESULT null_delta={int(holiday(cfg) != holiday(cfg, mut))} count")
calls = []
real = tm._holiday_dhw_windows
with mock.patch.object(tm, "_holiday_dhw_windows", lambda c: (calls.append(c.get(KEY)), real(c))[1]):
    for cfg in forms.values():
        tm.ThermalParameters.from_config(cfg)
print(f"RESULT reach_unset_calls={sum(1 for v in calls if not v)} count")
