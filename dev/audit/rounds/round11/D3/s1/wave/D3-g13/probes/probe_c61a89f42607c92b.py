#!/usr/bin/env python3
# Metric: the (temperature, humidity) bucket one measured defrost duty folds into through DefrostDerate.observe_duty
#   at outdoor 40.0 C (TEMP_EDGES[-1]) and the coldest bucket's resulting factor, baseline vs mutant.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_c61a89f42607c92b.py
# EXPECTED RESULT bucket_temp_at_top_edge baseline=5 mutant=0
# EXPECTED RESULT direct_inputs_moved=2 of 20 (temp:40.0,hum:101.0)  (only a value exactly on the top edge moves)
# EXPECTED RESULT observe_duty_40C_bucket baseline=(5, 0) mutant=(0, 0)
# EXPECTED RESULT cold_bucket_factor baseline=0.784729 mutant=0.92494  (ten 40 C zero duties dilute the -30..-5 C bucket)
# EXPECTED RESULT null_delta=0 count
# Count key: DefrostDerate.duty_counts (which bucket the production fold incremented) and factor() at the cold centre.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g13 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.defrost:_bucket_index
#   (line 169 `    return len(edges) - 2 if value >= edges[-1] else 0`), reached by DefrostDerate._bucket <- observe_duty
#   <- coordinator._settle_defrost (coordinator.py:9981, every temperature once the defrost flag is legible).
# Perturbation: mutant c61a89f42607c92b, `>=` -> `>`, in memory (function recompiled from its own source and patched
#   onto the module with mock.patch.object). Direction: a 40.0 C (or 101 % RH) sample moves from the top bucket to 0.
# Null control: a 20 C sample (inside the edges: line 169 is not reached), same bucket both arms.
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


def mutated(module, func, old, new, name=None):
    """``func`` recompiled from its own source with the one mutant line swapped (anchor must occur once)."""
    src = textwrap.dedent(inspect.getsource(func))
    o, n = old.strip(), new.strip()
    assert src.count(o) == 1, f"anchor moved: {o!r}"
    ns = dict(module.__dict__)
    exec(compile(src.replace(o, n, 1), module.__file__, "exec"), ns)
    return ns[name or func.__name__]


def footer():
    pc, tc = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        swp = [l for l in open("/proc/vmstat") if l.startswith("pswpin ")]
        print(f"RESULT swapins={swp[0].split()[1] if swp else 0}")
    except OSError:
        print("RESULT swapins=n/a")
from custom_components.heatpump_optimizer import defrost  # noqa: E402

OLD = "return len(edges) - 2 if value >= edges[-1] else 0"
NEW = "return len(edges) - 2 if value > edges[-1] else 0"
MUT = mutated(defrost, defrost._bucket_index, OLD, NEW)
TE, HE = defrost.TEMP_EDGES, defrost.HUMIDITY_EDGES
inputs = [TE[-1], HE[-1], TE[0], -31.0, 41.0, float("inf"), float("-inf"), float("nan"), 39.999999, 3.0]
moved = []
for v in inputs:
    for nm, edges in (("temp", TE), ("hum", HE)):
        b, m = defrost._bucket_index(v, edges), MUT(v, edges)
        if b != m:
            moved.append(f"{nm}:{v}")
print(f"RESULT bucket_temp_at_top_edge baseline={defrost._bucket_index(TE[-1], TE)} mutant={MUT(TE[-1], TE)}")
print(f"RESULT direct_inputs_moved={len(moved)} of {2 * len(inputs)} ({','.join(moved)})")


def duty_bucket(fn, outdoor, humidity):
    """The (t, h) bucket one measured duty lands in, through DefrostDerate.observe_duty (the production fold)."""
    d = defrost.DefrostDerate()
    with mock.patch.object(defrost, "_bucket_index", fn):
        d.observe_duty(outdoor, humidity, 0.0, events=0)
    return [(t, h) for t in range(len(TE) - 1) for h in range(len(HE) - 1) if d.duty_counts[t][h]][0]


b, m = duty_bucket(defrost._bucket_index, 40.0, 50.0), duty_bucket(MUT, 40.0, 50.0)
print(f"RESULT observe_duty_40C_bucket baseline={b} mutant={m}")
print(f"RESULT observe_duty_40C_moved={int(b != m)} count")
# The consequence on the coldest bucket's learned factor: ten zero-duty 40.0 C settlements on top of a bucket that
# had measured a 0.2 duty at -10 C (twelve samples).
def cold_factor(fn):
    d = defrost.DefrostDerate()
    for _ in range(12):
        d.observe_duty(-10.0, 50.0, 0.2, events=1)
    with mock.patch.object(defrost, "_bucket_index", fn):
        for _ in range(10):
            d.observe_duty(40.0, 50.0, 0.0, events=0)
    return round(d.factor(-17.5, 35.0), 6)


print(f"RESULT cold_bucket_factor baseline={cold_factor(defrost._bucket_index)} mutant={cold_factor(MUT)}")
b, m = duty_bucket(defrost._bucket_index, 20.0, 50.0), duty_bucket(MUT, 20.0, 50.0)
print(f"RESULT null_delta={int(b != m)} count  (20 C: inside the edges, line 169 never runs)")
# Reach: _settle_defrost (coordinator.py:9981) folds observe_duty at ANY outdoor temperature once the flag is legible;
# observe() (inferred) only inside the frost band [FROST_BAND_MIN_C, FROST_BAND_MAX_C), where 40.0 never arrives.
print(f"RESULT frost_band={defrost.FROST_BAND_MIN_C}..{defrost.FROST_BAND_MAX_C} C")
footer()
