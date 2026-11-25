#!/usr/bin/env python3
# Metric: count of inputs on which any of the seven arrays DhwPlanner._dhw_window_floors returns differs, over 600 inputs including learned stats with count 0, negative counts, p90 0/negative/1e300/NaN/inf and unparseable entries.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_e19cdb6bf198d1e7.py
# EXPECTED RESULT inputs_tried=600 count
# EXPECTED RESULT stats_branch_live=1
# EXPECTED RESULT outputs_differing=0 count
# Tolerance: exact (counts, verdicts and float64 prices are deterministic on one numpy build).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
# Machine: box D3-g16 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, /opt/hpo/venv-ci CPython).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._dhw_window_floors (custom_components/heatpump_optimizer/dhw_planner.py:1034 `if p90 is not None and np.isfinite(p90) and count > 0:`).
# Perturbation: mutant e19cdb6bf198d1e7, `if p90 is not None and np.isfinite(p90) and count > 0:` -> `if p90 is not None and np.isfinite(p90) and count >= 0:`, applied in memory: the method is re-compiled from
#   its own source with the one line replaced and called beside the untouched baseline method on the same input.
#   Direction: none found: at count 0 the blend weight w = 0 and (1 - 0) * e + 0 * max(0, p90) == e for every finite p90.
# Reach: production ready-temperature computation.
# Null control: the grid itself; liveness: count 8 at p90 0 moves the ready temps against no stats.
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

OLD = "if p90 is not None and np.isfinite(p90) and count > 0:"
NEW = "if p90 is not None and np.isfinite(p90) and count >= 0:"
MUT = mutant_method("_dhw_window_floors", OLD, NEW)
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import OptimizationConfig  # noqa: E402
from custom_components.heatpump_optimizer.dhw_schedule import parse_windows  # noqa: E402
from custom_components.heatpump_optimizer.dhw_draws import labels_for  # noqa: E402


def floors(spec, dt, n, stats=None, start=0.0, fn=None):
    """All seven arrays DhwPlanner._dhw_window_floors returns, as bytes (the store as its capacity)."""
    p = ThermalParameters(dhw_enabled=True, dhw_schedule_enabled=True, dhw_windows=parse_windows(spec))
    if stats is not None:
        p.dhw_window_ready_energy = stats
    planner = DhwPlanner(ThermalModel(p), OptimizationConfig(horizon_hours=24, time_step_minutes=int(dt * 60)))
    out = (fn or DhwPlanner._dhw_window_floors)(planner, p, p.dhw_windows, start + np.arange(n) * dt, None, dt, n, None)
    return (out[0].capacity_kwh_per_c,) + tuple(np.asarray(a, dtype=float).tobytes() for a in out[1:])


def grid():
    specs = ("06:00-08:30, 17:00-22:00", "00:00-24:00", "23:00-23:15", "05:45-06:00", "21:00-03:00")
    def stat_sets(spec):
        """Learned per-window ready-energy stats keyed by the planner's own window labels."""
        labels = labels_for(parse_windows(spec))
        return {
            "none": None,
            "count0": {lab: [3.0, 0] for lab in labels},
            "count_neg": {lab: [3.0, -2] for lab in labels},
            "count3": {lab: [3.0, 3] for lab in labels},
            "count8_p90_0": {lab: [0.0, 8] for lab in labels},
            "count0_p90_0": {lab: [0.0, 0] for lab in labels},
            "count0_negp90": {lab: [-4.0, 0] for lab in labels},
            "count0_huge_p90": {lab: [1e300, 0] for lab in labels},
            "nan_inf_p90": {lab: [float("nan") if i % 2 == 0 else float("inf"), 2] for i, lab in enumerate(labels)},
            "unparseable": {lab: ["x", "y"] for lab in labels},
        }
    for spec in specs:
        for dt, n in ((0.25, 96), (1.0, 24), (0.25, 1), (1.0, 3)):
            for start in (0.0, 5.75, 22.0):
                for sname, st in stat_sets(spec).items():
                    yield (spec, dt, n, start, sname, st)

tried = moved = 0
for spec, dt, n, start, sname, st in grid():
    tried += 1
    if floors(spec, dt, n, st, start) != floors(spec, dt, n, st, start, fn=MUT):
        moved += 1
        print(f"# moved: {spec} dt={dt} n={n} start={start} stats={sname}")
print(f"RESULT inputs_tried={tried} count")
live = floors("06:00-08:30, 17:00-22:00", 1.0, 24, {"06:00-08:30": [0.0, 8]}) != floors("06:00-08:30, 17:00-22:00", 1.0, 24)
print(f"RESULT stats_branch_live={int(live)}  (count 8 at p90 0 moves the ready temps against no stats: the blend is reached)")
print(f"RESULT outputs_differing={moved} count")
footer()
