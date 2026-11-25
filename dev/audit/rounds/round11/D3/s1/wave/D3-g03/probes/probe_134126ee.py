#!/usr/bin/env python3
# Metric: the operation score (EMA, prior 40.0) HeatPumpOptimizerCoordinator._close_score_day leaves after closing
#   a day book of exactly 0.2 kWh bought at 0.8x the day's mean spot over 2 priced hours (the `<`/`<=` tie).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g03/probes/probe_134126ee.py
# EXPECTED RESULT score_tie_baseline=43.0 (the day is scored) ; score_tie_mutant=40.0 (skipped, score unmoved)
# EXPECTED RESULT null_delta=0 count (0.1999 kWh and 0.2001 kWh, either side of the tie: arms agree)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g03 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._close_score_day,
#   line 10561 `if kwh < 0.2 or hours < 1.0:`; real driving_grade.fold.
# Perturbation: key 134126ee4914191f CMP_BOUND -> `if kwh <= 0.2 or hours < 1.0:`, in memory. Direction: scored -> skipped.
# Null control: kWh either side of 0.2.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, sys, textwrap, time, types
from types import SimpleNamespace
from unittest import mock

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
sys.path.insert(0, str(ROOT))
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402

CLS = co.HeatPumpOptimizerCoordinator
_T0 = (time.process_time(), time.thread_time())


def mutant(fn, line, old, new):
    """`fn` recompiled from its own source with production line `line` replaced (in memory only)."""
    lines, start = inspect.getsourcelines(fn)
    i = line - start
    assert lines[i].rstrip("\n") == old, f"anchor moved: {lines[i]!r}"
    lines[i] = new + "\n"
    ns = dict(co.__dict__)
    exec(compile(textwrap.dedent("".join(lines)), co.__file__, "exec"), ns)
    f = ns[fn.__name__]
    # rebound onto the module's own globals, so a patch of a module name reaches both arms alike
    return types.FunctionType(f.__code__, co.__dict__, f.__name__, f.__defaults__, f.__closure__)


def run(coro):
    return asyncio.run(coro)


def tail():
    p, t = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={p / t if t > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
    except OSError:
        sw = -1
    print(f"RESULT swapins={sw} count")

class Me:
    """A bare owner (hashable: driving_grade keys its drivers by owner)."""


def close(fn, book, prior=40.0):
    me = Me()
    me._score_day, me._operation_score, me.saves = dict(book), prior, 0
    me._schedule_ledger_save = lambda: setattr(me, "saves", me.saves + 1)
    fn(me)
    return (None if me._operation_score is None else round(me._operation_score, 6)), me._score_day
MUT = mutant(CLS._close_score_day, 10561, "        if kwh < 0.2 or hours < 1.0:", "        if kwh <= 0.2 or hours < 1.0:")


def book(kwh):
    return {"day": "2026-01-10", "kwh": kwh, "sek": kwh * 0.8, "spot_sum": 2.0, "spot_h": 2.0}


print(f"RESULT score_tie_baseline={close(CLS._close_score_day, book(0.2))[0]}")
print(f"RESULT score_tie_mutant={close(MUT, book(0.2))[0]}")
print(f"RESULT null_delta={sum(int(close(CLS._close_score_day, book(k)) != close(MUT, book(k))) for k in (0.1999, 0.2001))} count")
tail()
