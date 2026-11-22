#!/usr/bin/env python3
# Metric: hours and shape of the learned DHW windows over 10 patterns (contiguous runs, wrap past midnight, alternating hours, plateaus, single peaks, non-normalised).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_9b890e4f1fdfcd41.py
# EXPECTED RESULT window_hours_baseline=12.0 h
# EXPECTED RESULT window_hours_mutant=12.0 h
# EXPECTED RESULT inputs_moved=0 of 10
# Tolerance: exact (counts, verdicts and float64 prices are deterministic on one numpy build).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
# Machine: box D3-g16 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, /opt/hpo/venv-ci CPython).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._effective_dhw_windows (custom_components/heatpump_optimizer/dhw_planner.py:556 `if hour == prev + 1:`).
# Perturbation: mutant 9b890e4f1fdfcd41, `if hour == prev + 1:` -> `if False:`, applied in memory: the method is re-compiled from
#   its own source with the one line replaced and called beside the untouched baseline method on the same input.
#   Direction: none found: one-hour windows are merged back by dhw_schedule._normalize (start <= last_end), which parse_windows(format_windows(...)) applies.
# Reach: production learned windows.
# Null control: the grid itself.
# Count key: the value the production method returns (never an input attribute).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time
from pathlib import Path


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
_T0 = (time.process_time(), time.thread_time())
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import dhw_planner  # noqa: E402
from custom_components.heatpump_optimizer.dhw_planner import DhwPlanner  # noqa: E402


def mutant_method(name, old, new):
    """DhwPlanner.<name> re-compiled from its own source with the one mutated line, in memory."""
    src = textwrap.dedent(inspect.getsource(getattr(DhwPlanner, name)))
    assert src.count(old) == 1, f"anchor line moved: {old!r}"
    ns = dict(dhw_planner.__dict__)
    exec(compile(src.replace(old, new, 1), dhw_planner.__file__, "exec"), ns)
    return ns[name]


def footer():
    pc, tc = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as f:
            sw = next((l.split()[1] for l in f if l.startswith("pswpin ")), "0")
    except OSError:
        sw = "0"
    print(f"RESULT swapins={sw}")

from custom_components.heatpump_optimizer.thermal_model import DHW_HOURLY_DRAW_PATTERN  # noqa: E402
OLD = "if hour == prev + 1:"
NEW = "if False:"
INPUTS = [
    ("default_profile", list(DHW_HOURLY_DRAW_PATTERN)),
    ("flat_1.0", [1.0] * 24),
    ("flat_0.5_unnormalised", [0.5] * 24),
    ("mean1_shoulder_1.1", [0.518] * 11 + [1.1] * 3 + [1.5] * 10),
    ("plateau_1.0_peak_2.0", [1.0] * 20 + [2.0] * 4),
    ("alternating_2.0_0.2", [2.0, 0.2] * 12),
    ("single_peak_mean1", [0.2] * 23 + [24 - 0.2 * 23]),
    ("all_just_below_1", [1.0 - 1e-12] * 24),
    ("mean1_plateau_1.25", [0.5] * 8 + [1.25] * 16),
    ("wrap_22_to_2_mean1", [2.4] * 2 + [0.6] * 20 + [2.4] * 2),
]
MAIN = 5  # index into INPUTS of the headline input
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, DHW_HOURLY_DRAW_PATTERN  # noqa: E402

MUT = mutant_method("_effective_dhw_windows", OLD, NEW)


def windows(pattern, fn=None):
    """The (windows, learned) pair the planner plans against: schedule on, no windows entered, learned pattern."""
    p = ThermalParameters(dhw_enabled=True, dhw_schedule_enabled=True, dhw_windows=[],
                          dhw_hourly_draw_pattern=[float(x) for x in pattern])
    planner = DhwPlanner(ThermalModel(p), None)
    try:
        return (fn or DhwPlanner._effective_dhw_windows)(planner)
    except Exception as err:  # the mutant arm may raise
        return f"raises {type(err).__name__}"


def window_hours(res):
    return float(sum(e - s for s, e in res[0])) if isinstance(res, tuple) else float("nan")


moved = []
for name, pat in INPUTS:
    b, m = windows(pat), windows(pat, MUT)
    print(f"# input {name}: baseline={b} mutant={m}")
    if b != m:
        moved.append(name)
name, pat = INPUTS[MAIN]
b, m = windows(pat), windows(pat, MUT)
print(f"RESULT window_hours_baseline={window_hours(b)} h")
print(f"RESULT window_hours_mutant={window_hours(m)} h")
print(f"RESULT mutant_raises={int(isinstance(m, str))}")
nb, nm = windows(DHW_HOURLY_DRAW_PATTERN), windows(DHW_HOURLY_DRAW_PATTERN, MUT)
print(f"RESULT null_delta_hours={abs(window_hours(nm) - window_hours(nb)) if not isinstance(nm, str) else 'raises'} h")
print(f"RESULT inputs_moved={len(moved)} of {len(INPUTS)} ({','.join(moved) or '-'})")
footer()
