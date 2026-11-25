#!/usr/bin/env python3
# Metric: what _seed_pinned_guess returns for a guess longer than its bounds; and how many real solve calls pass a guess whose length differs from the bounds.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g23/probes/probe_f25414a9d4e32d19.py
# EXPECTED RESULT direct_long_guess_baseline=[1.0,2.0,5.0]
# EXPECTED RESULT direct_long_guess_mutant=IndexError
# EXPECTED RESULT null_equal_length_delta=0
# EXPECTED RESULT reach_length_mismatch_calls=0 of 14 (over 7 solves)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g23 cloud (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux),
#   run from a scratch baseline worktree while the box's full gate ran (counts exact; no timing is claimed).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._seed_pinned_guess, line 5292 (loop bound).
# Perturbation: key f25414a9d4e32d19, optimizer.py:5292 `for i in range(min(len(out), len(bounds))):` -> `for i in range((len(out))):`, applied in memory
#   (_g23_common.mutated re-compiles HeatPumpOptimizer._seed_pinned_guess with the one line replaced and patches the class);
#   direction: a long guess goes from an unclamped tail to IndexError.
# Null control: guess as long as the bounds: both arms identical.
# Writes nothing. Helpers: _g23_common.py beside this file.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import _g23_common as c  # noqa: E402
NAN = c.NAN
MUT = ('_seed_pinned_guess', 'for i in range(min(len(out), len(bounds))):', 'for i in range((len(out))):')
import numpy as np
res = {}
for arm in ("baseline", "mutant"):
    with (c.mutated(*MUT) if arm == "mutant" else c.contextlib.nullcontext()):
        out = []
        for g, bnd in (([5.0, 5.0, 5.0], [(0.0, 1.0), (0.0, 2.0)]), ([5.0, -1.0], [(0.0, 1.0), (0.5, 2.0)])):
            try:
                out.append([float(x) for x in c.OPT._seed_pinned_guess(np.array(g), bnd)])
            except Exception as exc:
                out.append(type(exc).__name__)
        res[arm] = out
print(f"RESULT direct_long_guess_baseline={c.fmt(res['baseline'][0])}")
print(f"RESULT direct_long_guess_mutant={c.fmt(res['mutant'][0])}")
print(f"RESULT null_equal_length_delta={int(res['baseline'][1] != res['mutant'][1])}")
with c.Spy("_seed_pinned_guess", lambda g, bnd: len(g) != len(bnd)) as spy:
    n = c.reach_solves()
print(f"RESULT reach_length_mismatch_calls={spy.hits} of {spy.calls} (over {n} solves)")
c.tail()
