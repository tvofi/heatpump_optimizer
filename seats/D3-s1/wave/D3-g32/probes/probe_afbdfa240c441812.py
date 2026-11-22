#!/usr/bin/env python3
# Box D3-g32 (round 11, seat D3-s1), D3 step 4 probe for full-gate survivor afbdfa240c441812.
# Metric: step power _size_step_power returns at the fits() peak tie.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_afbdfa240c441812.py   (from the repository root)
# EXPECTED: real_inputs_moved=0/360; stub_peak_tie (predictor stubbed to (0.8, 0.7)) baseline=6.0 mutant=None; stub_null_below baseline=6.0 mutant=6.0.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g32, 4 vCPU Intel Xeon @ 2.10GHz, venv-ci CPython 3.14.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification._size_step_power.fits, line 1593.
# Perturbation: key afbdfa240c441812 (CMP_BOUND) `peak <= bound` -> `peak < bound`; applied in memory (the function re-compiled from its own source with the one line swapped), never on disk.
# Null control: the predictor stubbed 0.01 C under the bound.
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

OLD, NEW = "            return peak <= bound and final <= bound", "            return peak < bound and final <= bound"
mut = mutate(SID, "_size_step_power", OLD, NEW)
gen_args = [(p, c, b, o) for p in (1.5, 3.0, 4.5, 6.0, 9.0) for c in (2.0, 3.0, 3.7) for b in (20.0, 21.0) for o in (-5.0, 2.0, 8.0)]
moved, n = scan(mut, args=gen_args)
print(f"RESULT real_inputs_moved={moved}/{n} count")
# the tie, which no rollout of a real house was found to produce: the predictor stubbed to return (bound, bound - 0.1)
def run_tie(fn, peak_off, final_off):
    bound = 0.8  # the full bound, tried after the noise-headroom bound 0.65 fails
    stub = lambda *a, **k: (bound + peak_off, bound + final_off)
    with mock.patch.dict(fn.__globals__, {"_predict_step_excursion_plant": stub}):
        return call(fn, 6.0, 3.0, 21.0, 2.0, HOUSES["features_heavy"])
print(f"RESULT stub_peak_tie_baseline={run_tie(SID._size_step_power, 0.0, -0.1)} mutant={run_tie(mut, 0.0, -0.1)}")
print(f"RESULT stub_null_below_baseline={run_tie(SID._size_step_power, -0.01, -0.1)} mutant={run_tie(mut, -0.01, -0.1)}")
tail()
