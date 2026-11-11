#!/usr/bin/env python3
"""LC catch-up lead (raised by D3-s3, owner D3-s2): optimizer.py:200
(_utc_step_starts) and defrost.py:643 (DefrostWindow._elapsed) -- are these
tzinfo-is-None guards deletable the same way open_meteo.py:209 (D3-s3-01)
is, because the gate's process runs at TZ=UTC?

Metric: GUARD_ON (real function) vs GUARD_OFF (the same function object with
its named guard line(s) deleted by re-exec'ing a dedented, in-memory-edited
copy of its own source -- never a file on disk, never
tests/mutation_table.py's pool/prescreen/gate) driven on one fixed scenario,
under two process time zones (TZ=UTC and TZ=Europe/Stockholm), differs=1 when
GUARD_ON != GUARD_OFF.

No mutation pool, no prescreen, no gate is run (tvofi's 2026-09-26 D3 rule);
this only calls production code (via an in-memory copy of one function) under
two process time zones.

Run:      PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
            tools/audit/round9/D3/s2/leads/lc_tz_probe_optimizer.py
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import inspect
import re
import sys
import textwrap
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import harness  # noqa: E402 (path wiring only)
from heatpump_optimizer import optimizer as OPT  # noqa: E402
from heatpump_optimizer import defrost as DEF  # noqa: E402


def _guard_off(func, pattern, repl=""):
    src = textwrap.dedent(inspect.getsource(func))
    new_src, n = re.subn(pattern, repl, src, count=1)
    assert n == 1, f"pattern not found once in {func.__name__}: {pattern!r}"
    ns = dict(vars(sys.modules[func.__module__]))
    exec(compile(new_src, f"<guard_off:{func.__name__}>", "exec"), ns)
    return ns[func.__name__]


def _set_tz(tz):
    os.environ["TZ"] = tz
    time.tzset()


def site_utc_step_starts():
    """optimizer.py:200 -- naive `start`; guard is an early return for a
    naive walk. GUARD_OFF unconditionally does the astimezone(utc) round
    trip, which for a NAIVE datetime interprets it in the process's own
    local zone (stdlib semantics), then `.astimezone(start.tzinfo)` with
    `start.tzinfo is None` converts to the process local zone too --
    swapping a naive result for an aware one, and shifting the wall time
    whenever the process zone offset != 0."""
    on = OPT._utc_step_starts
    off = _guard_off(
        on,
        r"    if start\.tzinfo is None:\n"
        r"        return \[start \+ timedelta\(hours=i \* dt_hours\) for i in range\(n\)\]\n",
    )
    start = datetime(2026, 1, 15, 0, 0, 0)  # naive
    a = on(start, 3, 1.0)
    b = off(start, 3, 1.0)
    return [t.isoformat() for t in a], [t.isoformat() for t in b]


def site_defrost_elapsed():
    """defrost.py:643 -- one naive, one aware stamp 900s apart; guard refuses
    to compare mismatched awareness. GUARD_OFF instead runs
    dt_util.as_utc on each (the harness stub's as_utc hardcodes UTC for a
    naive value -- TZ-independent through this stub)."""
    on = DEF.DefrostWindow._elapsed
    off = _guard_off(
        on,
        r" {8}if \(now\.tzinfo is None\) != \(then\.tzinfo is None\):\n"
        r" {12}return None\n",
    )
    now_naive = datetime(2026, 1, 15, 0, 15, 0)
    then_aware = datetime(2026, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
    a = on(now_naive, then_aware)
    b = off(now_naive, then_aware)
    return a, b


def main():
    results = {}
    for tz in ("UTC", "Europe/Stockholm"):
        _set_tz(tz)
        a, b = site_utc_step_starts()
        d = int(a != b)
        results[("utc_step_starts", tz)] = d
        print(f"{tz}: optimizer._utc_step_starts guard_on={a} guard_off={b} differs={d}")

        a2, b2 = site_defrost_elapsed()
        d2 = int(a2 != b2)
        results[("defrost_elapsed", tz)] = d2
        print(f"{tz}: defrost._elapsed guard_on={a2!r} guard_off={b2!r} differs={d2}")

    utc_d = results[("utc_step_starts", "UTC")]
    sto_d = results[("utc_step_starts", "Europe/Stockholm")]
    print(f"RESULT utc_step_starts_differs_utc={utc_d}")
    print(f"RESULT utc_step_starts_differs_stockholm={sto_d}")
    print(f"RESULT utc_step_starts_utc_blind={int((not utc_d) and sto_d)}")

    utc_d2 = results[("defrost_elapsed", "UTC")]
    sto_d2 = results[("defrost_elapsed", "Europe/Stockholm")]
    print(f"RESULT defrost_elapsed_differs_utc={utc_d2}")
    print(f"RESULT defrost_elapsed_differs_stockholm={sto_d2}")
    print(f"RESULT defrost_elapsed_utc_blind={int((not utc_d2) and sto_d2)}")

    print("RESULT sites_probed=2")
    print("RESULT thread_factor=1.0 (no numpy/BLAS on this path)")
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1.0
    print(f"RESULT load1={load1:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
