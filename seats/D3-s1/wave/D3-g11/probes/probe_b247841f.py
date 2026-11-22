#!/usr/bin/env python3
# Metric: the open-loop plan value coordinator._open_loop_plan_value returns (a trajectory entry, or None) for a plan
#   whose first step starts exactly at `now` (the `<` / `<=` tie), plus every other input class searched.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_b247841f.py
# Expected: every production-shaped input agrees (moved_valid=0 count); only a malformed plan with a DUPLICATED head
#   timestamp moves (dup_head baseline 51.0 -> mutant 50.0), which no plan producer emits.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g11 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:_open_loop_plan_value (line 2539,
#   `    if now_s < starts[0]:`).
# Perturbation: mutant b247841f5466162d, `now_s < starts[0]` -> `now_s <= starts[0]`, in memory (recompiled from its own
#   source in the module namespace). Direction: none on valid plans (equivalent-candidate): at the tie the baseline's
#   _covering_index returns 0 and the mutant's head branch returns trajectory[0] (0 <= 900 s).
# Null control: now 1 s and 600 s before the head, mid-plan, past the end: both arms agree by construction.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from pathlib import Path

ROOT = Path.cwd()  # run from the repository root (harness contract)
assert (ROOT / "custom_components/heatpump_optimizer/manifest.json").is_file(), "run from the repository root"
sys.path.insert(0, str(ROOT))
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402


def mutate(fn, old, new, name=None):
    """Recompile fn's own source with the one-line mutant, in the module namespace (in memory)."""
    src = textwrap.dedent(inspect.getsource(fn))
    assert src.count(old) == 1, f"anchor moved: {old!r}"
    ns = dict(co.__dict__)
    exec(compile(src.replace(old, new, 1), co.__file__, "exec"), ns)
    return ns[name or fn.__name__]


def tail_results(t0_cpu, t0_thr):
    import time
    pc, tc = time.process_time() - t0_cpu, time.thread_time() - t0_thr
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        for ln in open("/proc/vmstat"):
            if ln.startswith("pswpin "):
                sw = int(ln.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={sw} count")

import time
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

T0 = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
MUT = mutate(co._open_loop_plan_value, "if now_s < starts[0]:", "if now_s <= starts[0]:")


def plan(n, dup=False):
    ts = [T0 + timedelta(minutes=15 * i) for i in range(n)]
    if dup:
        ts = [T0] + ts
    return SimpleNamespace(timestamps=ts, slab_temp_trajectory=[50.0 + i for i in range(len(ts))])


t0, t1 = time.process_time(), time.thread_time()
cases = {
    "tie_96_steps": (plan(96), T0),
    "tie_1_step": (plan(1), T0),
    "tie_2_steps": (plan(2), T0),
    "tie_plus_1us": (plan(96), T0 + timedelta(microseconds=1)),
    "tie_minus_1us": (plan(96), T0 - timedelta(microseconds=1)),
    "before_600s": (plan(96), T0 - timedelta(seconds=600)),
    "before_901s": (plan(96), T0 - timedelta(seconds=901)),
    "mid": (plan(96), T0 + timedelta(hours=3)),
    "past_end": (plan(4), T0 + timedelta(hours=3)),
}
moved = 0
for name, (p, now) in cases.items():
    b = co._open_loop_plan_value(p, "slab_temp_trajectory", now)
    m = MUT(p, "slab_temp_trajectory", now)
    moved += int(b != m)
    print(f"RESULT {name}_baseline={b} mutant={m}")
print(f"RESULT moved_valid={moved} count")
p = plan(4, dup=True)
print(f"RESULT dup_head_baseline={co._open_loop_plan_value(p, 'slab_temp_trajectory', T0)} "
      f"mutant={MUT(p, 'slab_temp_trajectory', T0)}  (malformed plan, not a production state)")
tail_results(t0, t1)
