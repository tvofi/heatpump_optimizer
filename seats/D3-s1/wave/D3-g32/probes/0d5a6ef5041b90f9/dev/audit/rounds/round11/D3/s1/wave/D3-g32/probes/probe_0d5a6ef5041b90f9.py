#!/usr/bin/env python3
# Box D3-g32 (round 11, seat D3-s1), D3 step 4 probe for full-gate survivor 0d5a6ef5041b90f9.
# Metric: step power (kW electrical) _size_step_power returns, and its noiseless peak excursion.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_0d5a6ef5041b90f9.py   (from the repository root)
# EXPECTED: inputs_moved=7/24; features cell (6 kW, COP 3, 21 C, 2 C, ua 0.20 C 8.0 gains 0.3): baseline=4.353515625 mutant=4.3125; peak 0.6499 -> 0.6402 C under bound 0.65.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g32, 4 vCPU Intel Xeon @ 2.10GHz, venv-ci CPython 3.14.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification._size_step_power, line 1606.
# Perturbation: key 0d5a6ef5041b90f9 (GUARD_OFF) `if fits(q, bound):` -> `if False:`. Direction: the bisection never raises lo; the step is the coarse grid point, smaller; applied in memory (the function re-compiled from its own source with the one line swapped), never on disk.
# Null control: inputs where fits(q_max) already holds (both return max_power_kw).
# Counts are exact (no timing); thread_factor/load1/swapins are printed per the harness contract.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time
from pathlib import Path
from unittest import mock


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


def mutate(owner, name, old, new):
    """Re-compile ``owner.name`` from its own source with the one-line mutant applied (in memory)."""
    fn = getattr(owner, name)
    mod = sys.modules[fn.__module__]
    src = inspect.getsource(fn)  # the anchor carries the file's own indentation
    assert src.count(old) == 1, f"anchor moved: {old!r}"
    ns = dict(mod.__dict__)
    exec(compile(textwrap.dedent(src.replace(old, new, 1)), mod.__file__, "exec"), ns)
    return ns[name]


def tail():
    pc, tc = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        for line in open("/proc/vmstat"):
            if line.startswith("pswpin "):
                sw = int(line.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={sw}")

from custom_components.heatpump_optimizer import sysid

SID = sysid.SystemIdentification
HOUSES = {  # (ua kW/K, capacity kWh/K, gains kW, slab_mass, slab_transfer); the first is tests/features.py's D2-s4-02 cell
    "features_heavy": sysid.HousePlant(ua=0.20, capacity=8.0, gains=0.3),
    "light": sysid.HousePlant(ua=0.15, capacity=4.0, gains=0.2),
    "leaky": sysid.HousePlant(ua=0.35, capacity=8.0, gains=0.5),
    "slab": sysid.HousePlant(ua=0.20, capacity=6.0, gains=0.3, slab_mass=8.0, slab_transfer=0.5),
}
ARGS = [  # (max_power_kw, cop, baseline, outdoor)
    (6.0, 3.0, 21.0, 2.0), (3.0, 2.5, 20.0, -5.0), (8.0, 4.0, 21.5, 8.0), (1.5, 3.0, 21.0, 2.0),
    (4.0, 1.0, 20.0, 0.0), (2.0, 2.0, 22.0, 10.0),
]


def call(fn, max_power_kw, cop, baseline, outdoor, house):
    s = SID(sysid.SysIdConfig(enabled=True))
    try:
        r = fn(s, max_power_kw, cop, baseline, outdoor, house)
        return None if r is None else round(float(r), 9)
    except Exception as err:  # noqa: BLE001
        return f"raised {type(err).__name__}"


def scan(mut, args=ARGS, houses=HOUSES, show=6):
    moved, n, shown = 0, 0, 0
    for hname, house in houses.items():
        for a in args:
            b, m = call(SID._size_step_power, *a, house), call(mut, *a, house)
            n += 1
            if b != m:
                moved += 1
                if shown < show:
                    shown += 1
                    print(f"RESULT moved_{hname}_{a}: baseline={b} mutant={m}")
    return moved, n

mut = mutate(SID, "_size_step_power", "                    if fits(q, bound):", "                    if False:")
moved, n = scan(mut)
print(f"RESULT inputs_moved={moved}/{n} count")
b = call(SID._size_step_power, 6.0, 3.0, 21.0, 2.0, HOUSES["features_heavy"])
m = call(mut, 6.0, 3.0, 21.0, 2.0, HOUSES["features_heavy"])
print(f"RESULT features_cell_step_kw_baseline={b} mutant={m}")
pb, _ = sysid._predict_step_excursion_plant(HOUSES["features_heavy"], 21.0, 2.0, (b or 0) * 3.0, 2.0, 2.0)
pm_, _ = sysid._predict_step_excursion_plant(HOUSES["features_heavy"], 21.0, 2.0, (m or 0) * 3.0, 2.0, 2.0)
print(f"RESULT features_cell_peak_c_baseline={pb:.4f} mutant={pm_:.4f} bound={0.8 - 0.15}")
tail()
