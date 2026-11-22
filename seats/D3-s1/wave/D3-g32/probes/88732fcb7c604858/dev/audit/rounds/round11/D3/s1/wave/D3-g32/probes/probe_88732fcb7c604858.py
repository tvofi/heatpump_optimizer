#!/usr/bin/env python3
# Box D3-g32 (round 11, seat D3-s1), D3 step 4 probe for full-gate survivor 88732fcb7c604858.
# Metric: slab_mode_one_state_identifiability verdict (one-state fit allowed) across tau_fast on the default 1 h shortest phase.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/probes/probe_88732fcb7c604858.py   (from the repository root)
# EXPECTED: verdicts_moved=4 (tau_fast 0.200-0.333 h: True -> False); null_delta=0.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g32, 4 vCPU Intel Xeon @ 2.10GHz, venv-ci CPython 3.14.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:slab_mode_one_state_identifiability (reads FAST_MODE_SETTLE_TAUS, line 549, at line 683).
# Perturbation: key 88732fcb7c604858 (CONST) `FAST_MODE_SETTLE_TAUS = 3.0` -> `6.0`, in memory by mock.patch.object. Direction: admitted -> refused for tau_fast in (1/6, 1/3] h; applied in memory (the function re-compiled from its own source with the one line swapped), never on disk.
# Null control: an unconfigured slab (c_s = 0), refused before the constant is read.
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

cfg = sysid.SysIdConfig()  # settle 1 h, step 2 h, relax 2 h: shortest phase 1 h
moved, rows = 0, []
# tau_fast = c_r*c_s/((c_r+c_s)*k_s); c_r = c_s = 1 gives tau_fast = 0.5/k_s
for k_s in (0.4, 1.0, 1.5, 1.6, 2.0, 2.5, 3.0, 3.1, 4.0, 6.0):
    b = sysid.slab_mode_one_state_identifiability(1.0, 1.0, k_s, cfg)
    with mock.patch.object(sysid, "FAST_MODE_SETTLE_TAUS", 6.0):
        m = sysid.slab_mode_one_state_identifiability(1.0, 1.0, k_s, cfg)
    tau = sysid.slab_mode_tau_fast(1.0, 1.0, k_s)
    print(f"RESULT tau_fast_{tau:.3f}h_baseline_ok={b[0]} mutant_ok={m[0]}")
    moved += b[0] != m[0]
print(f"RESULT verdicts_moved={moved} count  (tau_fast in (1/6, 1/3] h)")
b = sysid.slab_mode_one_state_identifiability(1.0, 1.0, 2.0, cfg)
with mock.patch.object(sysid, "FAST_MODE_SETTLE_TAUS", 6.0):
    m = sysid.slab_mode_one_state_identifiability(1.0, 1.0, 2.0, cfg)
print(f"RESULT tau_0.25h_baseline={b!r}")
print(f"RESULT tau_0.25h_mutant={m!r}")
# null control: an unconfigured slab, refused before the constant is read
b = sysid.slab_mode_one_state_identifiability(1.0, 0.0, 2.0, cfg)
with mock.patch.object(sysid, "FAST_MODE_SETTLE_TAUS", 6.0):
    m = sysid.slab_mode_one_state_identifiability(1.0, 0.0, 2.0, cfg)
print(f"RESULT null_delta={int(b != m)} count")
tail()
