#!/usr/bin/env python3
# Metric: count of (mode, step count, entity value, rule list) cases, of 36 tried, on which
#   GridFeeSchedule.fee_vector returns a different vector (or raises) under the mutant; plus how many of those
#   cases the one production caller (coordinator.py:7272, gated on `schedule.active`) can deliver.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_ee2d5a67d9d3a7f9.py
# EXPECTED RESULT cases_tried=36 count
# EXPECTED RESULT differing_cases=4 count            (entity mode with zero steps, all four value/rule pairs: IndexError on step_starts[0])
# EXPECTED RESULT differing_mode_none_cases=0 count   (current_fee returns 0.0 in mode none: zeros either way)
# EXPECTED RESULT production_deliverable_differing=0 count  (mode none is never `active`; the caller passes n_steps > 0)
# EXPECTED RESULT mode_none_active=0 count
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g18 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: heatpump_optimizer.grid_fee:GridFeeSchedule.fee_vector, line 329
#   `if self.mode == MODE_NONE or n == 0:`; production caller coordinator.py:7599 via _fee_series (7272).
# Perturbation: mutant ee2d5a67d9d3a7f9, the guard -> `if False:`, applied in memory (the method is recompiled from
#   its own source and patched onto the class for the mutant arm). Direction: only n == 0 in entity mode moves
#   (zeros(0) -> IndexError); mode none falls through to current_fee, which returns 0.0 per step.
# Inputs: mode in {none, rules, entity} x n in {0, 1, 96} x entity value in {None, 0.4} x rules in {[], [Nov-Mar
#   Mon-Fri 06-22 = 0.5, = 0.1]}; fixed 0.2 for rules/entity, 0.3 with stale rules for none.
# Null control: the baseline against itself (0 by construction); the production-deliverable count applies the
#   caller's own gate (schedule.active and n_steps > 0) to the differing cases.
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
from datetime import datetime, timedelta, timezone  # noqa: E402
from unittest import mock  # noqa: E402

import numpy as np  # noqa: E402

from heatpump_optimizer import grid_fee as gf  # noqa: E402

OLD = "if self.mode == MODE_NONE or n == 0:"
SRC = textwrap.dedent(inspect.getsource(gf.GridFeeSchedule.fee_vector))
assert SRC.count(OLD) == 1, "anchor line moved"
NS = dict(gf.__dict__)
exec(compile(SRC.replace(OLD, "if False:", 1), gf.__file__, "exec"), NS)
MUT = NS["fee_vector"]
RULES = gf.parse_rules("Nov-Mar Mon-Fri 06:00-22:00 = 0.5\n= 0.1")
START = datetime(2026, 1, 12, 0, 0, tzinfo=timezone.utc)


def out(sched, steps, ev, mutant):
    ctx = mock.patch.object(gf.GridFeeSchedule, "fee_vector", MUT) if mutant else mock.MagicMock()
    try:
        with ctx:
            v = sched.fee_vector(steps, ev)
        return ("ok", np.asarray(v).dtype.str, tuple(np.round(np.asarray(v, dtype=float), 12)))
    except Exception as err:  # the mutant's failure mode is part of the compared value
        return ("raise", type(err).__name__)


cases = diff = diff_none = deliverable = 0
for mode in (gf.MODE_NONE, gf.MODE_RULES, gf.MODE_ENTITY):
    for n in (0, 1, 96):
        steps = [START + timedelta(minutes=15 * i) for i in range(n)]
        for ev in (None, 0.4):
            for rules in ([], RULES):
                sched = gf.GridFeeSchedule(mode=mode, fixed=0.3 if mode == gf.MODE_NONE else 0.2, rules=list(rules))
                cases += 1
                if out(sched, steps, ev, False) != out(sched, steps, ev, True):
                    diff += 1
                    diff_none += mode == gf.MODE_NONE
                    deliverable += bool(sched.active and n > 0)
none_active = int(gf.GridFeeSchedule(mode=gf.MODE_NONE, fixed=0.3, rules=list(RULES)).active)
print(f"RESULT cases_tried={cases} count")
print(f"RESULT differing_cases={diff} count")
print(f"RESULT differing_mode_none_cases={diff_none} count")
print(f"RESULT production_deliverable_differing={deliverable} count")
print(f"RESULT mode_none_active={none_active} count")

import resource as _resource  # noqa: E402
import time as _time  # noqa: E402

print(f"RESULT thread_factor={_time.process_time() / max(_time.thread_time(), 1e-9):.3f} ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={_resource.getrusage(_resource.RUSAGE_SELF).ru_nswap} count")
