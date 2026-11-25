#!/usr/bin/env python3
# Metric: count of inputs on which DefrostWindow._elapsed (and the ten window sequences that call it) answer
#   differently baseline vs mutant: production-shaped stamps (datetime aware/naive/mixed/None) vs fabricated stamps.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_5941c09a9face079.py
# EXPECTED RESULT production_shaped_moved=0 of 19 ()  (timedelta.total_seconds() is always a float: `and`->`or`
#   changes nothing for a float)
# EXPECTED RESULT fabricated_moved=3 of 3  (bool True -> None vs 1.0; Decimal 5 -> None vs 5.0; str "5" -> None vs 5.0)
# Count key: the value _elapsed returns (seconds or None) and the DefrostObservation the window returns.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g13 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.defrost:DefrostWindow._elapsed
#   (line 739 `        if isinstance(raw, (int, float)) and not isinstance(raw, bool):`).
# Perturbation: mutant 5941c09a9face079, `and` -> `or`, in memory (staticmethod recompiled from its own source onto a
#   subclass). Direction: a non-float total_seconds() result is accepted instead of declined.
# Reach: every caller (observe/_accrue/peek/close, coordinator dt_util.now() and state-change times) passes datetimes,
#   whose difference is a timedelta: the separating inputs exist only as fabricated objects.
# Null control: the production-shaped arm, which must not move.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time
from pathlib import Path
from unittest import mock


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
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
_T0 = (time.process_time(), time.thread_time())


def mutated(module, func, old, new, name=None):
    """``func`` recompiled from its own source with the one mutant line swapped (anchor must occur once)."""
    src = textwrap.dedent(inspect.getsource(func))
    o, n = old.strip(), new.strip()
    assert src.count(o) == 1, f"anchor moved: {o!r}"
    ns = dict(module.__dict__)
    exec(compile(src.replace(o, n, 1), module.__file__, "exec"), ns)
    return ns[name or func.__name__]


def footer():
    pc, tc = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        swp = [l for l in open("/proc/vmstat") if l.startswith("pswpin ")]
        print(f"RESULT swapins={swp[0].split()[1] if swp else 0}")
    except OSError:
        print("RESULT swapins=n/a")
from datetime import datetime, timedelta, timezone  # noqa: E402
from custom_components.heatpump_optimizer import defrost  # noqa: E402

W = defrost.DefrostWindow
T0 = datetime(2026, 1, 15, 6, 0, tzinfo=timezone.utc)
N0 = datetime(2026, 1, 15, 6, 0)


def s(sec, base=T0):
    return base + timedelta(seconds=sec)


# (name, [(op, seconds, flag)], peek/close at seconds); op "o" observe, "c" close
SEQS = {
    "on_then_peek": ([("o", 0, True)], 600),
    "off_on_peek": ([("o", 0, False), ("o", 300, True)], 900),
    "on_off_peek": ([("o", 0, True), ("o", 300, False)], 900),
    "repeat_same_stamp": ([("o", 0, True), ("o", 0, True), ("o", 300, True), ("o", 300, True)], 300),
    "zero_length": ([("o", 0, True)], 0),
    "backwards_clock": ([("o", 600, True), ("o", 300, True)], 200),
    "dark_then_on": ([("o", 0, None), ("o", 120, True)], 600),
    "carried_level_after_close": ([("o", 0, True), ("c", 1800, None)], 2400),
    "carried_level_reobserved": ([("o", 0, True), ("c", 1800, None), ("o", 1800, True)], 2400),
    "none_observed": ([], 600),
}


def drive(seq, peek_at, peek_fn=None, cls=W):
    w = cls()
    for op, sec, flag in seq:
        if op == "o":
            w.observe(s(sec), flag)
        else:
            w.close(s(sec))
    ob = (peek_fn or cls.peek)(w, s(peek_at))
    return (round(ob.duty, 12), ob.events, ob.observed, ob.seconds)
OLD = "if isinstance(raw, (int, float)) and not isinstance(raw, bool):"
NEW = "if isinstance(raw, (int, float)) or not isinstance(raw, bool):"
MUT = staticmethod(mutated(defrost, W._elapsed, OLD, NEW))


class WM(W):
    pass


WM._elapsed = MUT
from decimal import Decimal  # noqa: E402


def _eq(a, b):
    return a == b or (a != a and b != b)


moved = []
# 1) every production-shaped stamp: aware UTC, aware non-UTC, naive, mixed, DST edge, None
tz2 = timezone(timedelta(hours=2))
pairs = {
    "aware_utc": (s(600), s(0)), "aware_tz2": (s(600).astimezone(tz2), s(0)), "naive": (s(600, N0), s(0, N0)),
    "mixed": (s(600), s(0, N0)), "equal": (s(0), s(0)), "negative": (s(0), s(600)), "none_then": (s(0), None),
    "none_now": (None, s(0)), "micro": (s(0.000001), s(0)),
}
for name, (a, b_) in pairs.items():
    rb, rm = W._elapsed(a, b_), WM._elapsed(a, b_)
    print(f"RESULT stamp_{name}: baseline={rb!r} mutant={rm!r}")
    if not _eq(rb, rm):
        moved.append(name)
# 2) the full window sequences through the mutated helper
for name, (seq, at) in SEQS.items():
    if drive(seq, at) != drive(seq, at, cls=WM):
        moved.append(name)
print(f"RESULT production_shaped_moved={len(moved)} of {len(pairs) + len(SEQS)} ({','.join(moved)})")


# 3) fabricated stamps: objects whose difference's total_seconds() is not a float (no production caller passes one)
class _Delta:
    def __init__(self, v):
        self.v = v

    def total_seconds(self):
        return self.v


class _Stamp:
    tzinfo = timezone.utc

    def __init__(self, v):
        self.v = v

    def __sub__(self, other):
        return _Delta(self.v)


fab = {"bool_True": True, "decimal_5": Decimal("5"), "str_5": "5"}
fab_moved = []
for name, v in fab.items():
    rb = W._elapsed(_Stamp(v), _Stamp(0))
    try:
        rm = WM._elapsed(_Stamp(v), _Stamp(0))
    except Exception as exc:  # noqa: BLE001
        rm = f"raises {type(exc).__name__}"
    print(f"RESULT fabricated_{name}: baseline={rb!r} mutant={rm!r}")
    if not _eq(rb, rm):
        fab_moved.append(name)
print(f"RESULT fabricated_moved={len(fab_moved)} of {len(fab)} ({','.join(fab_moved)})")
footer()
