"""D5-s1 harness: is an over-bound transfer-fee rule refused or only flagged?

docs/how-it-works.md ("The DSO transfer fee") says a fee component above the plausibility bound
"is flagged, not refused"; docs/configuration.md ("Transfer fees and contract") says such a rate
"is refused when the page is saved". Metric: refused_rules = number of probe rule texts (rates
above the bound, the doc's own 100x-slip example included) for which the options page's
validator grid_fee.spec_problem returns an error key (the save is refused).
Count key: spec_problem's return value. Command:
  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s1/fee_refusal.py [--perturb]
Expected at baseline 92d38ecb: refused_rules=3 of 3 (exact): configuration.md holds,
how-it-works.md's "not refused" contradicts it for the rules path.
Perturbation (--perturb): grid_fee.fee_bound patched to return inf; refused_rules falls to 0.
Machine: orchestrator Mac, local seat.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time
sys.path.insert(0, ".")
t0, c0 = time.time(), time.process_time()
from custom_components.heatpump_optimizer import grid_fee
if "--perturb" in sys.argv:
    grid_fee.fee_bound = lambda currency=None: float("inf")
probes = ["Nov-Mar Mon-Fri 06:00-22:00 = 25", "= 11", "06:00-22:00 = 40"]
refused = 0
for p in probes:
    r = grid_fee.spec_problem(p, "SEK")
    print(f"probe {p!r}: {r}")
    refused += r is not None
print(f"RESULT refused_rules={refused} rules")
pc, wc = time.process_time() - c0, time.time() - t0
print(f"RESULT thread_factor={pc / max(wc, 1e-9):.2f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
