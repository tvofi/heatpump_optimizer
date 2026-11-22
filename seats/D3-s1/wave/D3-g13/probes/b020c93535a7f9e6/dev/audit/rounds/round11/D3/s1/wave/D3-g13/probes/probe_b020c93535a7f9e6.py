#!/usr/bin/env python3
# Metric: count of inputs (10 window sequences + a fresh window peeked with 5 stamp shapes) on which
#   DefrostWindow.peek returns a different DefrostObservation baseline vs mutant.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_b020c93535a7f9e6.py
# EXPECTED RESULT inputs_moved=0 of 15 ()  (with _opened None, _elapsed(now, None) hits None.tzinfo -> AttributeError
#   -> None, and the next line returns the same empty DefrostObservation())
# Count key: the (duty, events, observed, seconds) peek() returns.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g13 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.defrost:DefrostWindow.peek (line 795 `        if self._opened is None:`).
# Perturbation: mutant b020c93535a7f9e6, guard -> `if False:`, in memory (peek recompiled, called unbound).
#   Direction if not equivalent: a fresh window would answer something other than the empty observation.
# Null control: the sequences with _opened set, which the guard never touches.
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
OLD = "if self._opened is None:"
NEW = "if False:"
MUT = mutated(defrost, W.peek, OLD, NEW)
moved = []
for name, (seq, at) in SEQS.items():
    b, m = drive(seq, at), drive(seq, at, MUT)
    if b != m:
        moved.append(name)
# fresh window (the only state where _opened is None), peeked with every stamp shape
fresh = {"aware": s(0), "naive": s(0, N0), "none": None, "int": 5, "str": "x"}
for name, now in fresh.items():
    w = W()
    b = W.peek(w, now)
    try:
        m = MUT(w, now)
        m = (m.duty, m.events, m.observed, m.seconds)
    except Exception as exc:  # noqa: BLE001
        m = f"raises {type(exc).__name__}"
    b = (b.duty, b.events, b.observed, b.seconds)
    print(f"RESULT fresh_{name}: baseline={b} mutant={m}")
    if b != m:
        moved.append(f"fresh_{name}")
print(f"RESULT inputs_moved={len(moved)} of {len(SEQS) + len(fresh)} ({','.join(moved)})")
footer()
