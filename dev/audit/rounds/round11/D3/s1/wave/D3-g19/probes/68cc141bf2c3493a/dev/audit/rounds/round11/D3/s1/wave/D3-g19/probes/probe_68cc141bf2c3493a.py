#!/usr/bin/env python3
# Metric: the SOURCE label grid_fee.min_component returns in entity mode when the entity value ties the fixed
#   component exactly (fixed=-0.20, entity=-0.20); baseline label 'fixed'.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g19/probes/probe_68cc141bf2c3493a.py
# EXPECTED RESULT label_baseline=fixed
# EXPECTED RESULT label_mutant=entity
# EXPECTED RESULT label_changed=1 count
# EXPECTED RESULT value_delta=0.0
# EXPECTED RESULT null_label_delta=0 count  (entity strictly below, strictly above, None)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g19 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.grid_fee:min_component (line 388
#   `        and float(entity_value) < lowest`), whose label names the negative-fee source to the user.
# Perturbation: `< lowest` -> `<= lowest` (CMP_BOUND 68cc141bf2c3493a), applied in memory (function recompiled from its own
#   source, patched onto the module for the mutant arm only). Direction: label 'fixed' -> 'entity' on a tie.
# Null control: entity -0.5 (both 'entity'), entity 0.1 (both 'fixed'), entity None (both 'fixed').
# Inputs tried: tie -0.20/-0.20; tie at 0.0/0.0 (fixed 0, entity 0); the three null inputs.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time, warnings
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
_T0, _C0 = time.perf_counter(), (time.process_time(), time.thread_time())


def mutated(mod, owner, name, lineno, old, new):
    """`name` (a function of `owner`, a module or class) recompiled from its own source with line `lineno`
    replaced, `old` -> `new`; the anchor must match exactly. Line numbers are kept, so a traceback names the file line."""
    fn = owner.__dict__[name] if isinstance(owner, type) else getattr(owner, name)
    lines, start = inspect.getsourcelines(fn)
    i = lineno - start
    assert lines[i].rstrip("\n") == old, f"anchor moved: {lines[i]!r} != {old!r}"
    lines[i] = new + "\n"
    ns = dict(mod.__dict__)
    exec(compile("\n" * (start - 1) + textwrap.dedent("".join(lines)), mod.__file__, "exec"), ns)
    return ns[name]


def tail():
    pc, tc = time.process_time() - _C0[0], time.thread_time() - _C0[1]
    print(f"RESULT wall={time.perf_counter() - _T0:.2f} s (provisional)")
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        for ln in open("/proc/vmstat"):
            if ln.startswith("pswpin "):
                sw = int(ln.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={sw}")
from custom_components.heatpump_optimizer import grid_fee as gf  # noqa: E402

FN = "min_component"
mut = mutated(gf, gf, FN, 388, "        and float(entity_value) < lowest", "        and float(entity_value) <= lowest")
base = getattr(gf, FN)
s = gf.GridFeeSchedule(mode=gf.MODE_ENTITY, fixed=-0.20)
z = gf.GridFeeSchedule(mode=gf.MODE_ENTITY, fixed=0.0)
b, m = base(s, -0.20), mut(s, -0.20)
bz, mz = base(z, 0.0), mut(z, 0.0)
null = sum(int(base(s, v) != mut(s, v)) for v in (-0.5, 0.1, None))
print(f"RESULT label_baseline={b[1]}")
print(f"RESULT label_mutant={m[1]}")
print(f"RESULT label_changed={int(b[1] != m[1])} count")
print(f"RESULT value_delta={abs(b[0] - m[0])}")
print(f"RESULT zero_tie_label={bz[1]}->{mz[1]}")
print(f"RESULT null_label_delta={null} count")
tail()
