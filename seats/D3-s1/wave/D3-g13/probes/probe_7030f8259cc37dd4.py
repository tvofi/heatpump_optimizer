#!/usr/bin/env python3
# Metric: count of DefrostWindow observe/close sequences (10) plus direct _accrue calls (delta 0.0, -0.0, -5, 1e-9, 7)
#   whose peek()/close() observation or accumulated seconds differ between baseline and mutant.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_7030f8259cc37dd4.py
# EXPECTED RESULT sequences_moved=0 of 15 ()  (delta == 0 adds 0.0 to a float: equivalent; -0.0 >= 0 adds -0.0,
#   which leaves a positive or zero accumulator bit-identical)
# Count key: the (duty, events, observed, seconds) DefrostObservation peek/close return, and _seconds_on itself.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g13 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.defrost:DefrostWindow._accrue
#   (line 746 `            if delta is not None and delta > 0:`).
# Perturbation: mutant 7030f8259cc37dd4, `delta > 0` -> `delta >= 0`, in memory (_accrue recompiled from its own source
#   onto a subclass). Direction if it were not equivalent: seconds_on up at delta == 0 (it is not: += 0.0).
# Null control: the baseline arm against itself (sequences are deterministic); nothing to move.
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
OLD = "if delta is not None and delta > 0:"
NEW = "if delta is not None and delta >= 0:"
MUT = mutated(defrost, W._accrue, OLD, NEW)


class WM(W):
    pass


WM._accrue = MUT
moved = []
# every sequence, peeked and closed, in aware UTC, naive and mixed stamps
for name, (seq, at) in SEQS.items():
    b, m = drive(seq, at), drive(seq, at, cls=WM)
    bc, mc = drive(seq, at, peek_fn=W.close), drive(seq, at, peek_fn=WM.close, cls=WM)
    print(f"RESULT {name}: baseline={b}/{bc} mutant={m}/{mc}")
    if b != m or bc != mc:
        moved.append(name)
# direct: delta exactly 0.0, -0.0, negative, nan-free; the exact float accumulated
for d0 in (0.0, -0.0, -5.0, 1e-9, 7.0):
    wb, wm = W(), WM()
    for w in (wb, wm):
        w._state, w._since, w._seconds_on = True, T0, 3.0
        w._accrue(T0 + timedelta(seconds=d0))
    same = (wb._seconds_on == wm._seconds_on) and (str(wb._seconds_on) == str(wm._seconds_on))
    print(f"RESULT direct_delta={d0}: baseline_seconds_on={wb._seconds_on!r} mutant={wm._seconds_on!r} same={int(same)}")
    if not same:
        moved.append(f"direct{d0}")
print(f"RESULT sequences_moved={len(moved)} of {len(SEQS) + 5} ({','.join(moved)})")
footer()
