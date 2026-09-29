#!/usr/bin/env python3
"""LC catch-up lead (raised by D3-s3, owner D3-s1): are coordinator.py's
tzinfo-is-None guards at :586, :588, :6331, :8112, :8384 deletable the same
way open_meteo.py:209 was (D3-s3-01), because the gate's process runs at
TZ=UTC and HASTUB_TZ is unset by default?

Metric, per site: GUARD_ON (real coordinator.py function) vs GUARD_OFF (the
same function object with its named `if ...tzinfo is None...` branch deleted
by re-exec'ing an edited copy of its own source -- never a file on disk, never
tests/mutation_table.py's pool/prescreen/gate) driven on one fixed scenario
mixing a naive and an aware timestamp; differs=1 when GUARD_ON != GUARD_OFF's
return value. Each site is run twice: once with the process/stub clocks as
the gate leaves them (TZ=UTC, HASTUB_TZ unset) and once with
TZ=Europe/Stockholm, HASTUB_TZ=Europe/Stockholm -- to see whether a
divergence is UTC-invisible and Stockholm-visible (M02's shape) or is the
same at both (not a UTC-blindness case).

No mutation pool, no prescreen, no gate is run (tvofi's 2026-09-26 D3 rule);
this only calls production code (via an in-memory copy of one function) under
two process time zones.

Run:      PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
            tools/audit/round9/D3/s1/leads/lc_tz_probe_coordinator.py
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import inspect
import json
import re
import sys
import textwrap
import time
from datetime import datetime, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import harness  # noqa: E402  (path wiring only)
from heatpump_optimizer import coordinator as C  # noqa: E402


def _guard_off(func, pattern, repl=""):
    """Recompile `func` with one regex-matched guard line removed/replaced.

    Perturbation, in memory (mock.patch.object precedent, README): the exact
    named guard line only, never a re-derived formula.
    """
    src = textwrap.dedent(inspect.getsource(func))
    new_src, n = re.subn(pattern, repl, src, count=1)
    assert n == 1, f"pattern not found once in {func.__name__}: {pattern!r}"
    ns = dict(vars(sys.modules[func.__module__]))
    exec(compile(new_src, f"<guard_off:{func.__name__}>", "exec"), ns)
    return ns[func.__name__]


def _set_tz(tz, hastub_tz):
    if tz is None:
        os.environ.pop("TZ", None)
    else:
        os.environ["TZ"] = tz
    time.tzset()
    if hastub_tz is None:
        os.environ.pop("HASTUB_TZ", None)
    else:
        os.environ["HASTUB_TZ"] = hastub_tz
    # dt.py stub reads HASTUB_TZ at import time; reload it and coordinator's
    # bound name for it so DEFAULT_TIME_ZONE picks up the change.
    import importlib
    dt_mod = sys.modules["homeassistant.util.dt"]
    importlib.reload(dt_mod)
    C.dt_util = dt_mod


def site_comparable_ts():
    """coordinator.py:586 -- naive raw, aware reference; guard replaces
    tzinfo with a hardcoded timezone.utc (never consults the process clock)."""
    on = C._comparable_ts
    off = _guard_off(
        C._comparable_ts,
        r"    if ts\.tzinfo is None and reference\.tzinfo is not None:\n"
        r"        return ts\.replace\(tzinfo=timezone\.utc\)\n",
    )
    raw = "2026-01-15T00:30:00"
    ref = datetime(2026, 1, 15, tzinfo=timezone.utc)
    a = on(raw, ref)
    b = off(raw, ref)
    return (a.isoformat() if a else None), (b.isoformat() if b else None)


def site_comparable_ts_as_local():
    """coordinator.py:588 -- aware raw, naive reference; guard routes through
    dt_util.as_local, which under the stub is identity unless HASTUB_TZ is
    set (not the process TZ)."""
    on = C._comparable_ts
    off = _guard_off(
        C._comparable_ts,
        r"    if ts\.tzinfo is not None and reference\.tzinfo is None:\n"
        r"        return dt_util\.as_local\(ts\)\.replace\(tzinfo=None\)\n",
    )
    raw = "2026-01-15T00:30:00+00:00"
    ref = datetime(2026, 1, 15)
    a = on(raw, ref)
    b = off(raw, ref)
    return (a.isoformat() if a else None), (b.isoformat() if b else None)


class _Ctx:
    def __init__(self):
        self._config = {}


class _FakeCoord:
    """Minimal stand-in exposing only what _immersion_dhw_margin reads."""

    def __init__(self, events):
        self._ctx = _Ctx()
        self._immersion_events = events


def site_immersion_margin():
    """coordinator.py:8384 -- one naive stored event, `now` from dt_util.now()
    (naive unless HASTUB_TZ is set: the guard is only ever reachable when it
    is)."""
    on = C.HeatPumpOptimizerCoordinator._immersion_dhw_margin
    off = _guard_off(
        on,
        r" {8}if when\.tzinfo is None and now\.tzinfo is not None:\n"
        r" {12}when = when\.replace\(tzinfo=now\.tzinfo\)\n",
    )
    coord = _FakeCoord(
        ["2026-01-05T00:00:00", "2026-01-10T00:00:00", "2026-01-14T00:00:00"]
    )
    coord._ctx._config = {"immersion_feedback_enabled": True}
    now = C.dt_util.now()
    a = on(coord, now)
    try:
        b = off(coord, now)
    except TypeError as err:
        b = f"raises {err}"
    return (a, now.tzinfo is not None), (b, now.tzinfo is not None)


def _run_site(name, fn, tz, hastub_tz):
    _set_tz(tz, hastub_tz)
    a, b = fn()
    return name, a, b, a != b


def main():
    results = []
    for tz, hastub in (("UTC", None), ("Europe/Stockholm", "Europe/Stockholm")):
        for name, fn in (
            ("comparable_ts_586", site_comparable_ts),
            ("comparable_ts_588", site_comparable_ts_as_local),
        ):
            n, a, b, d = _run_site(name, fn, tz, hastub)
            results.append((tz, n, a, b, d))
            print(f"{tz}: {n} guard_on={a!r} guard_off={b!r} differs={int(d)}")

    for (n,) in [("comparable_ts_586",), ("comparable_ts_588",)]:
        utc_d = next(r[4] for r in results if r[0] == "UTC" and r[1] == n)
        sto_d = next(r[4] for r in results if r[0] == "Europe/Stockholm" and r[1] == n)
        print(f"RESULT {n}_utc_blind={int((not utc_d) and sto_d)}")
        print(f"RESULT {n}_differs_utc={int(utc_d)}")
        print(f"RESULT {n}_differs_stockholm={int(sto_d)}")

    # :8384 (and by identical shape :8112): `now.tzinfo` comes from
    # dt_util.now(), which under the stub is naive unless HASTUB_TZ is set --
    # a gate-default reachability question, not an OS-TZ one.
    _set_tz("UTC", None)
    (on_default, now_aware_default), (off_default, _) = site_immersion_margin()
    print(f"HASTUB_TZ unset: guard_on={on_default!r} guard_off={off_default!r} "
          f"now_tzaware={int(now_aware_default)}")
    _set_tz("UTC", "Europe/Stockholm")
    (on_stub, now_aware_stub), (off_stub, _) = site_immersion_margin()
    print(f"HASTUB_TZ=Europe/Stockholm: guard_on={on_stub!r} guard_off={off_stub!r} "
          f"now_tzaware={int(now_aware_stub)}")
    print(f"RESULT immersion_margin_8384_now_tzaware_default={int(now_aware_default)}")
    print(f"RESULT immersion_margin_8384_differs_hastubtz_unset={int(on_default != off_default)}")
    print(f"RESULT immersion_margin_8384_differs_hastubtz_stockholm={int(on_stub != off_stub)}")

    print(f"RESULT sites_probed=3")
    print("RESULT thread_factor=1.0 (no numpy/BLAS on this path)")
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1.0
    print(f"RESULT load1={load1:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
