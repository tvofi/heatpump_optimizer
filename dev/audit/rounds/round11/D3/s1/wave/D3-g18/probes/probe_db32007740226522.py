#!/usr/bin/env python3
# Metric: count of rule lines, of 15 tried, on which grid_fee._parse_rule returns a different FeeRule (or raises a
#   different error) under the mutant; plus the number of empty tokens body.split()+strip() yields over them.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_db32007740226522.py
# EXPECTED RESULT lines_tried=15 count
# EXPECTED RESULT differing_lines=0 count       (equivalent: str.split() never yields a token strip() empties)
# EXPECTED RESULT empty_tokens_seen=0 count
# EXPECTED RESULT positive_control_differing=6 count  (split(" ") instead of split(): the guard then matters)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g18 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: heatpump_optimizer.grid_fee:_parse_rule, line 187 `if not token:` (reached from parse_rules,
#   GridFeeSchedule.from_config, spec_problem and apply_catalog).
# Perturbation: mutant db32007740226522, `if not token:` -> `if False:`, applied in memory (the function is
#   recompiled from its own source and patched onto the module for the mutant arm). Expected direction: none.
# Inputs: ordinary rules, empty body, doubled spaces, tabs, NBSP, EM SPACE, \x1c-\x1f separators, a trailing
#   newline, a rule that is only whitespace before '=', and three malformed lines (the error text is compared).
# Null control: the baseline against itself (0 by construction). Positive control: both arms re-tokenised with
#   body.split(" "), which does yield empty tokens; there the guard's absence turns 6 lines into errors.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))
import inspect  # noqa: E402
import textwrap  # noqa: E402
from unittest import mock  # noqa: E402

from heatpump_optimizer import grid_fee as gf  # noqa: E402

OLD = "        if not token:"
SRC = textwrap.dedent(inspect.getsource(gf._parse_rule))
assert SRC.count("if not token:") == 1, "anchor line moved"


def compiled(src):
    ns = dict(gf.__dict__)
    exec(compile(src, gf.__file__, "exec"), ns)
    return ns["_parse_rule"]


MUT = compiled(SRC.replace("if not token:", "if False:", 1))
SPLIT = 'body.split()'
assert SRC.count(SPLIT) == 1
POS_BASE = compiled(SRC.replace(SPLIT, 'body.split(" ")', 1))
POS_MUT = compiled(SRC.replace(SPLIT, 'body.split(" ")', 1).replace("if not token:", "if False:", 1))
LINES = [
    "Nov-Mar Mon-Fri 06:00-22:00 = 0.5", "= 0.1", "  = 0.1", "Nov-Mar  Mon-Fri   06:00-22:00 = 0,5",
    "Nov-Mar\tMon-Fri\t06:00-22:00 = 0.5", "Nov-Mar Mon-Fri = 0.5", "Jul Sat = 0.2",
    "Jul\x1cSat\x1d06:00-07:00\x1e= 0.2", "Jul\x1f= 0.2", "Jul Sat 06:00-07:00 \n= 0.2", " \t   = 0.3",
    "Nov-Mar Mon-Fri", "Foo = 1", "Jul Jul = 1",
    "06:00-07:00 08:00-09:00 = 1",
]


def call(fn, line):
    try:
        return ("ok", fn(line))
    except gf.GridFeeError as err:
        return ("err", str(err))


def differing(base_fn, mut_fn):
    return sum(1 for line in LINES if call(base_fn, line) != call(mut_fn, line))


empty = 0
for line in LINES:
    body = line.rpartition("=")[0]
    empty += sum(1 for tok in body.split() if not tok.strip())
print(f"RESULT lines_tried={len(LINES)} count")
print(f"RESULT differing_lines={differing(gf._parse_rule, MUT)} count")
print(f"RESULT empty_tokens_seen={empty} count")
print(f"RESULT positive_control_differing={differing(POS_BASE, POS_MUT)} count")

import resource as _resource  # noqa: E402
import time as _time  # noqa: E402

print(f"RESULT thread_factor={_time.process_time() / max(_time.thread_time(), 1e-9):.3f} ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={_resource.getrusage(_resource.RUSAGE_SELF).ru_nswap} count")
