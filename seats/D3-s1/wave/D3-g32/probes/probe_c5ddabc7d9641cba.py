#!/usr/bin/env python3
# Box D3-g32 (round 11, seat D3-s1), D3 step 4 probe for full-gate survivor c5ddabc7d9641cba.
# Metric: step power _size_step_power returns for cop below 0.1.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_c5ddabc7d9641cba.py   (from the repository root)
# EXPECTED: low_cop_inputs_moved=68/384 (only at max_power 160 kW); null_cop_ge_0.1_moved=0/24; production_cop_min=1.050.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g32, 4 vCPU Intel Xeon @ 2.10GHz, venv-ci CPython 3.14.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification._size_step_power, line 1573.
# Perturbation: key c5ddabc7d9641cba (CLAMP_DROP) `cop = max(cop, 0.1)` -> `cop = (cop)`; applied in memory (the function re-compiled from its own source with the one line swapped), never on disk.
# Null control: cop >= 0.1, where the floor is inert.
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

mut = mutate(SID, "_size_step_power", "        cop = max(cop, 0.1)", "        cop = (cop)")
low = [(p, c, 21.0, o) for p in (3.0, 6.0, 12.0, 40.0, 80.0, 160.0) for c in (0.0, 0.05, 0.09, -1.0) for o in (2.0, 12.0, 16.0, 18.0)]
for a in low[48:54]:
    print(f"RESULT sample_{a}: baseline={call(SID._size_step_power, *a, HOUSES['light'])} mutant={call(mut, *a, HOUSES['light'])}")
moved, n = scan(mut, args=low)
print(f"RESULT low_cop_inputs_moved={moved}/{n} count")
nm, nn = scan(mut, show=0)
print(f"RESULT null_cop_ge_0.1_moved={nm}/{nn} count")
# reach: the coordinator's only call passes cop = ThermalModel.compute_cop(outdoor), whose COP law floors at 1.0
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
tm_ = ThermalModel(ThermalParameters())
cops = [float(tm_.compute_cop(float(t))) for t in range(-40, 41)]
print(f"RESULT production_cop_min={min(cops):.3f} over outdoor -40..40 C  (the floor removed only acts below 0.1)")
tail()
