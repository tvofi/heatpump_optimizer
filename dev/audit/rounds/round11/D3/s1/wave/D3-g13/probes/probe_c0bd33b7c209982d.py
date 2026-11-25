#!/usr/bin/env python3
# Metric: max |DefrostDerate factor (mutant) - factor (baseline)| over every probe temperature/humidity pair (each centre,
#   +-1e-9 around it, its negation, +-100, 0, +-inf, nan) on six fully learned learners, plus the (i, u) tuple
#   _interp_position returns on the same values.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_c0bd33b7c209982d.py
# EXPECTED RESULT at_first_centre baseline=(0, 0.0) mutant=(0, 0.0)  (the loop's first cell gives u=(c0-c0)/span=0.0)
# EXPECTED RESULT interp_tuple_moves=0 of 76 count
# EXPECTED RESULT factor_max_abs_delta=0.0
# Count key: the float DefrostDerate._factor_uncached returns (what factor() memoizes and every plan's COP multiplies by).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g13 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.defrost:_interp_position (line 181 `    if value <= centers[0]:`).
# Perturbation: mutant c0bd33b7c209982d, `<=` -> `<`, in memory (function recompiled from its own source and patched
#   onto the module). Direction if not equivalent: the factor at exactly the first centre would change.
# Null control: values away from centers[0], which the comparison cannot touch.
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
import random  # noqa: E402
from custom_components.heatpump_optimizer import defrost  # noqa: E402

TC, HC = defrost.TEMP_CENTERS, defrost.HUMIDITY_CENTERS


def learned(seed):
    """A learner with every bucket measured and inferred to distinct values (no uniform-surroundings shortcut)."""
    rng = random.Random(seed)
    d = defrost.DefrostDerate()
    for t in range(len(defrost.TEMP_EDGES) - 1):
        for h in range(len(defrost.HUMIDITY_EDGES) - 1):
            d.duty[t][h] = rng.uniform(0.0, 0.3)
            d.duty_counts[t][h] = rng.choice((1, 5, 12, 40))
            d.factors[t][h] = rng.uniform(0.55, 1.0)
            d.counts[t][h] = rng.choice((0, 3, 20))
    return d


def probe_values():
    """Every centre, the span ends, values a hair either side of each centre, and non-finite inputs."""
    vals = set()
    for c in TC + HC:
        vals |= {c, c - 1e-9, c + 1e-9, -c}
    vals |= {-100.0, 100.0, 0.0, float("inf"), float("-inf"), float("nan")}
    return sorted(vals, key=lambda v: (v != v, v))


def factor_delta(fn, seeds=range(6)):
    """max |factor_mutant - factor_baseline| over every (t, h) pair of probe_values and every learner."""
    worst, pairs, tuple_moves = 0.0, 0, 0
    vals = probe_values()
    for seed in seeds:
        d = learned(seed)
        for t in vals:
            for h in vals + [None]:
                hh = h if h is not None else HC[0]
                b = d._factor_uncached(float(t), float(hh))
                with mock.patch.object(defrost, "_interp_position", fn):
                    m = d._factor_uncached(float(t), float(hh))
                pairs += 1
                if b != m and not (b != b and m != m):
                    worst = max(worst, abs(m - b) if (m == m and b == b) else float("inf"))
    for v in vals:
        for cs in (TC, HC):
            b, m = defrost._interp_position(v, cs), fn(v, cs)
            if b != m and not (b[1] != b[1] and m[1] != m[1] and b[0] == m[0]):
                tuple_moves += 1
    return worst, pairs, tuple_moves
OLD = "if value <= centers[0]:"
NEW = "if value < centers[0]:"
MUT = mutated(defrost, defrost._interp_position, OLD, NEW)
print(f"RESULT at_first_centre baseline={defrost._interp_position(TC[0], TC)} mutant={MUT(TC[0], TC)}")
worst, pairs, tmoves = factor_delta(MUT)
print(f"RESULT interp_tuple_moves={tmoves} of {2 * len(probe_values())} count")
print(f"RESULT factor_max_abs_delta={worst} over {pairs} (t,h) pairs x 6 learners")
footer()
