#!/usr/bin/env python3
# Metric: rows of DefrostDerate.summary() carrying a measured-duty block ("duty"/"events"/"duty_samples") on a learner
#   whose only evidence is one INFERRED observation (duty_counts all 0), baseline vs mutant.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_24d9995ccee4252e.py
# EXPECTED RESULT rows_with_duty_baseline=0 count
# EXPECTED RESULT rows_with_duty_mutant=1 count  (the inferred-only row gains duty=0.0 events=0 duty_samples=0)
# EXPECTED RESULT null_delta_rows=0 count        (a bucket with a counted duty reports it in both arms)
# Count key: the rows summary() returns (what coordinator.py:8002 publishes as diagnostics "defrost_buckets").
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g13 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.defrost:DefrostDerate.summary
#   (line 642 `                if self.duty_counts[t][h] > 0:`).
# Perturbation: mutant 24d9995ccee4252e, `> 0` -> `>= 0`, applied in memory (method recompiled from its own source
#   and called unbound for the mutant arm). Direction: rows_with_duty 0 -> 1 on an inferred-only bucket.
# Null control: a bucket with one counted duty sample (observe_duty): its row carries the duty block in both arms.
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

OLD = "if self.duty_counts[t][h] > 0:"
NEW = "if self.duty_counts[t][h] >= 0:"
MUT = mutated(defrost, defrost.DefrostDerate.summary, OLD, NEW)


def rows_with_duty(learner, fn=None):
    rows = (fn or defrost.DefrostDerate.summary)(learner)
    return sum(1 for r in rows if "duty" in r), len(rows), rows


# Case: one INFERRED observation (no defrost flag: the pre-v5.3.0 estimator), zero measured duty samples.
d = defrost.DefrostDerate()
d.observe(3.0, 85.0, 0.8)
b_duty, b_rows, b = rows_with_duty(d)
m_duty, m_rows, m = rows_with_duty(d, MUT)
print(f"RESULT rows_total_baseline={b_rows} count")
print(f"RESULT rows_with_duty_baseline={b_duty} count")
print(f"RESULT rows_with_duty_mutant={m_duty} count")
print(f"RESULT mutant_row_fields={sorted(set(m[0]) - set(b[0]))}")
print(f"RESULT mutant_row_duty={m[0].get('duty')} events={m[0].get('events')} duty_samples={m[0].get('duty_samples')}")
# Null control: a bucket with a counted duty reports its duty in both arms.
n = defrost.DefrostDerate()
n.observe_duty(3.0, 85.0, 0.1, events=1)
nb, _, _ = rows_with_duty(n)
nm, _, _ = rows_with_duty(n, MUT)
print(f"RESULT null_delta_rows={nm - nb} count")
# Empty learner: no rows in either arm (source None skips the row before line 642).
e = defrost.DefrostDerate()
print(f"RESULT empty_rows_baseline={len(e.summary())} mutant={len(MUT(e))} count")
footer()
