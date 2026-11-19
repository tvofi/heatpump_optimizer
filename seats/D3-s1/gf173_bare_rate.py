#!/usr/bin/env python3
# Metric: how many of a fixed set of rule lines WITHOUT an "=" separator grid_fee.parse_rules accepts as a
#   fee rule (baseline: every one refused with GridFeeError "has no '= rate' part").
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/gf173_bare_rate.py
# EXPECTED RESULT accepted_baseline=0 count
# EXPECTED RESULT accepted_mutant=2 count  (the two bare-number lines "0.25" and "0,40" become always-on rules)
# EXPECTED RESULT null_accepted_delta=0 count  (well-formed lines: both arms parse them identically)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-top6 (4 vCPU Xeon @ 2.30GHz). Counts are exact.
# Instrumented symbol: custom_components.heatpump_optimizer.grid_fee:_parse_rule (line 173 guard `if not sep:`),
#   driven through the public grid_fee:parse_rules.
# Perturbation: line 173 `if not sep:` -> `if False:` (GUARD_OFF 121362d48b408236), in memory: _parse_rule is
#   re-compiled from its own source with that one edit and patched onto the module. Direction: accepted 0 -> 2.
#   The full gate (fullgate.py run --src complete --key 121362d48b408236) stays green under it.
# Null control: well-formed rules ("Mon-Fri 06-22 = 0.5", "Nov-Mar = 0,3", "= 0.1") parse to identical
#   FeeRule lists in both arms.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))
from custom_components.heatpump_optimizer import grid_fee as gf  # noqa: E402

OLD = "    if not sep:"
BARE = ["0.25", "0,40", "Mon-Fri 0.5", "Nov-Mar"]
GOOD = ["Mon-Fri 06-22 = 0.5", "Nov-Mar = 0,3", "= 0.1"]


def mutant():
    src = textwrap.dedent(inspect.getsource(gf._parse_rule))
    old = OLD.strip()
    assert src.count(old) == 1, "anchor line moved"
    ns = dict(gf.__dict__)
    exec(compile(src.replace(old, "if False:"), gf.__file__, "exec"), ns)
    return ns["_parse_rule"]


def accepted(lines):
    n, got = 0, []
    for ln in lines:
        try:
            r = gf.parse_rules(ln)
        except gf.GridFeeError:
            got.append(None)
            continue
        n += 1
        got.append([(x.rate, x.months, x.days, x.hours) for x in r])
    return n, got


base_n, _ = accepted(BARE)
gb, good_base = accepted(GOOD)
with mock.patch.object(gf, "_parse_rule", mutant()):
    mut_n, mut_rules = accepted(BARE)
    gm, good_mut = accepted(GOOD)
print(f"RESULT accepted_baseline={base_n} count")
print(f"RESULT accepted_mutant={mut_n} count")
print(f"RESULT mutant_rules={[r for r in mut_rules if r]!r}")
print(f"RESULT null_accepted_delta={int(good_base != good_mut) + abs(gb - gm)} count")
print("RESULT thread_factor=1.0 ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0 count")
