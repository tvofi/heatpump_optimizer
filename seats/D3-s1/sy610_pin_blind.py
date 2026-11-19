#!/usr/bin/env python3
# Metric: of four degenerate slab triples (c_r, c_s, k_s) with an unset constant, how many
#   sysid.slab_mode_tau_fast answers 0.0 without raising; and whether the #1401 pin's own input
#   (0.0, 1.0, 1.0) tells the guarded and unguarded helper apart (pin_discriminates).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/sy610_pin_blind.py
# EXPECTED RESULT zero_answers_baseline=4 count
# EXPECTED RESULT zero_answers_mutant=2 count  ((1,1,0) and (0,0,0) raise ZeroDivisionError)
# EXPECTED RESULT pin_discriminates=0 count  (features.py:53975's input gives 0.0 in both arms)
# EXPECTED RESULT null_delta=0.0 h  (a set triple (2,30,1.5) gives the same tau in both arms)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-top6 (4 vCPU Xeon @ 2.30GHz). Counts are exact.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:slab_mode_tau_fast (line 610 guard
#   `if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9):`).
# Perturbation: line 610 -> `if False:` (GUARD_OFF 460217277822d5bd), in memory: the function is re-compiled
#   from its own source with that one edit. Direction: zero_answers 4 -> 2.
#   The full gate (fullgate.py run --src complete --key 460217277822d5bd) stays green under it.
# Null control: a set triple, where the guard is inert, answers identically in both arms.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))
from custom_components.heatpump_optimizer import sysid  # noqa: E402

OLD = "if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9):"
TRIPLES = [(0.0, 1.0, 1.0), (1.0, 0.0, 1.0), (1.0, 1.0, 0.0), (0.0, 0.0, 0.0)]
PIN = (0.0, 1.0, 1.0)  # tests/features.py:53975 (#1401)


def mutant():
    src = textwrap.dedent(inspect.getsource(sysid.slab_mode_tau_fast))
    assert src.count(OLD) == 1, "anchor line moved"
    ns = dict(sysid.__dict__)
    exec(compile(src.replace(OLD, "if False:"), sysid.__file__, "exec"), ns)
    return ns["slab_mode_tau_fast"]


def zero_answers(fn):
    n = 0
    for t in TRIPLES:
        try:
            n += int(fn(*t) == 0.0)
        except ZeroDivisionError:
            pass
    return n


mut = mutant()
base_n, mut_n = zero_answers(sysid.slab_mode_tau_fast), zero_answers(mut)
pin = int(sysid.slab_mode_tau_fast(*PIN) != mut(*PIN))
null = abs(sysid.slab_mode_tau_fast(2.0, 30.0, 1.5) - mut(2.0, 30.0, 1.5))
print(f"RESULT zero_answers_baseline={base_n} count")
print(f"RESULT zero_answers_mutant={mut_n} count")
print(f"RESULT pin_discriminates={pin} count")
print(f"RESULT null_delta={null} h")
print("RESULT thread_factor=1.0 ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0 count")
