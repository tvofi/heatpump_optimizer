#!/usr/bin/env python3
# Metric: whether DhwPlanner._dhw_legionella_due places the elastic anti-legionella cycle (due flag, 0/1) on a 24 h horizon whose only price under the ceiling is a prior-estimated (unpublished) step.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g16/probes/probe_35d61c87783ebe66.py
# EXPECTED RESULT cycle_placed_baseline=0 count (baseline waits: the one cheap step is estimated)
# EXPECTED RESULT cycle_placed_mutant=1 count (mutant books the cycle at step 20, an estimated price)
# EXPECTED RESULT mutant_step_price_known=0
# EXPECTED RESULT null_inputs_moved=0 of 3
# Tolerance: exact (counts, verdicts and float64 prices are deterministic on one numpy build).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
# Machine: box D3-g16 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, /opt/hpo/venv-ci CPython).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._dhw_legionella_due (custom_components/heatpump_optimizer/dhw_planner.py:680 `if known is not None:`).
# Perturbation: mutant 35d61c87783ebe66, `if known is not None:` -> `if False:`, applied in memory: the method is re-compiled from
#   its own source with the one line replaced and called beside the untouched baseline method on the same input.
#   Direction: cycles placed up (0 -> 1): every step is treated as a published price.
# Reach: production: optimizer.py passes the per-step price_known mask to DhwPlanner (optimizer.py:4373) whenever the horizon runs past the published day-ahead prices.
# Null control: an all-known mask, the None mask of a fresh optimizer and a horizon whose cheap step is published: the guard cannot matter, 0 moved.
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

MUT = mutant_method("_dhw_legionella_due", "if known is not None:", "if False:")
from types import SimpleNamespace  # noqa: E402
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402
from custom_components.heatpump_optimizer.optimizer import OptimizationConfig  # noqa: E402

N = 24


def legionella(known, prices, *, tank=55.0, p_run=3.0, volume=200.0, ceiling=1.0, off=None, fn=None):
    """(due, hour, step, ready_temps) from DhwPlanner._dhw_legionella_due inside the elastic window (130 h since
    the last cycle: past the 5-day minimum, before the 7-day deadline, so the hard-deadline branch is not taken)."""
    p = ThermalParameters(dhw_enabled=True, dhw_legionella_enabled=True, dhw_elastic_legionella_enabled=True,
                          dhw_legionella_price_ceiling=ceiling, dhw_tank_volume=volume)
    planner = DhwPlanner(ThermalModel(p), OptimizationConfig(horizon_hours=N, time_step_minutes=60), None, known)
    h = SimpleNamespace(initial_state=ThermalState(dhw_temperature=tank, dhw_hours_since_legionella=130.0),
                        n_steps=N, dt=1.0, outdoor_temps=np.full(N, 5.0), humidity=None)
    ready = np.zeros(N)
    due, hour, step = (fn or DhwPlanner._dhw_legionella_due)(
        planner, h, params=p, hours_mod=np.arange(N, dtype=float), draw_rates=np.zeros(N),
        ready_temps=ready, p_dhw_run=p_run, dhw_prices=np.asarray(prices, dtype=float), off_steps=off)
    return due, hour, step, ready.tobytes()

prices = np.full(N, 2.0)
prices[20] = 0.1                                  # the one price under the ceiling (1.0) is in the estimated half
part_known = np.array([True] * 12 + [False] * 12)  # day-ahead published for 12 h, the rest from the prior
b = legionella(part_known, prices)
m = legionella(part_known, prices, fn=MUT)
print(f"# headline: baseline (due, hour, step)={b[:3]} mutant={m[:3]}")
print(f"RESULT cycle_placed_baseline={int(b[0])} count")
print(f"RESULT cycle_placed_mutant={int(m[0])} count")
print(f"RESULT mutant_step_price_known={int(bool(part_known[m[2]])) if m[2] is not None else 'none'}")
inputs = {
    "all_known": np.ones(N, dtype=bool),
    "known_None_fresh_optimizer": None,
    "cheap_step_in_known_half": None,
}
moved = []
for name, known in inputs.items():
    pr = prices
    if name == "cheap_step_in_known_half":
        known, pr = part_known, np.where(np.arange(N) == 5, 0.1, 2.0)
    bb, mm = legionella(known, pr), legionella(known, pr, fn=MUT)
    print(f"# input {name}: baseline={bb[:3]} mutant={mm[:3]}")
    if bb != mm:
        moved.append(name)
print(f"RESULT null_inputs_moved={len(moved)} of {len(inputs)} ({','.join(moved) or '-'})")
footer()
