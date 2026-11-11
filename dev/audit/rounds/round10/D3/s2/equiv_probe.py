#!/usr/bin/env python3
"""D3-s2 equivalence probe for the pre-screen survivors (D3.M4).

Metric: for each survivor mutant, the number of input cells over which the
mutated production function returns a different value from the baseline one
(0 = equivalent mutant, not a gap).  Count key: the production return value.

Command (repo root):
    PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python \
        dev/audit/rounds/round10/D3/s2/equiv_probe.py
Expected: M30_differs=3 of 32 cells (exact); M14_differs=1 of 2 traces (exact).
Baseline 17f1c55fad1b; machine tvofi macOS arm64, shared box B2.
Perturbation: --identity applies the mutant's *old* line as the "mutant";
every differs count must go to 0 (null control).
Mutation is applied in memory: the function's source is re-exec'd with the
one line replaced, nothing on disk changes.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, itertools, sys, textwrap, time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, ".")
IDENT = "--identity" in sys.argv

from custom_components.heatpump_optimizer import const, snapshots


def mutate(func, old, new, glb):
    src = textwrap.dedent(inspect.getsource(func))
    assert src.count(old) == 1, (func, old)
    src = src.replace(old, old if IDENT else new)
    ns = {}
    exec(compile(src, "<mut>", "exec"), glb, ns)
    return ns[func.__name__]


# M30: const.topology_layout_valid, `if key == TOPOLOGY_TWO_TANK_4WAY:` negated
base = const.topology_layout_valid
mut = mutate(base, "if key == TOPOLOGY_TWO_TANK_4WAY:",
             "if not (key == TOPOLOGY_TWO_TANK_4WAY):", vars(const))
keys = [const.TOPOLOGY_NO_VALVE, const.TOPOLOGY_SINGLE_TANK_VALVE,
        const.TOPOLOGY_TWO_TANK_4WAY, const.TOPOLOGY_VALVE_UPPER_DIRECT_SLAB]
cells = diff = 0
flips = []
for k, (tz, th, wp) in itertools.product(keys, itertools.product([0, 1], repeat=3)):
    a = base(k, two_zone=bool(tz), throttling=bool(th), wood_probe=bool(wp))
    b = mut(k, two_zone=bool(tz), throttling=bool(th), wood_probe=bool(wp))
    cells += 1
    if a != b:
        diff += 1
        flips.append((k, tz, th, wp, a, b))
for f in flips:
    print("  M30 flip", f)
print(f"RESULT M30_differs={diff} cells_of_{cells}")

# M14: snapshots.SnapshotRing.observe_bias, `if not healthy:` negated
SR = snapshots.SnapshotRing
mobs = mutate(SR.observe_bias, "if not healthy:", "if not (not healthy):",
              vars(snapshots))
T0 = datetime(2026, 1, 5, 12, tzinfo=timezone.utc)
traces = {"all_healthy": [True] * 6, "one_unhealthy": [True, True, False, True, True, True]}
d14 = 0
for name, health in traces.items():
    out = []
    for fn in (SR.observe_bias, mobs):
        r = SR()
        for i, h in enumerate(health):
            fn(r, T0 + timedelta(days=i), 0.9, h)
        out.append((r.alarmed, r.auto_rollback_justified))
    print(f"  M14 {name}: baseline={out[0]} mutant={out[1]}")
    d14 += out[0] != out[1]
print(f"RESULT M14_differs={d14} traces_of_{len(traces)}")
print(f"RESULT thread_factor={time.process_time()/max(time.thread_time(),1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
