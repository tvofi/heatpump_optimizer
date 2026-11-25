#!/usr/bin/env python3
# Metric: DefrostWindow.peek(now).duty (and events, any_defrost) on an interval whose defrost flag is still ON at the
#   peek, over nine observe/close sequences; headline: flag ON carried over a close at 1800 s, re-observed ON at 1800 s (the per-cycle level read), peek at 2400 s.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/probes/probe_8297234e122897ff.py
# EXPECTED RESULT duty_baseline=1.0          (the pump has defrosted the whole 600 s of the open interval)
# EXPECTED RESULT duty_mutant=0.0            (the open on-period is dropped from the peek)
# EXPECTED RESULT observed_baseline=1 mutant=1
# EXPECTED RESULT any_defrost_baseline=1 mutant=0  (coordinator.py:5345-5347 then stops refusing the COP fold)
# EXPECTED RESULT null_delta=0 count         (flag switched off before the peek: same answer both arms)
# Count key: the DefrostObservation peek() returns (what coordinator._learn_measured_cop reads at coordinator.py:5345).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g13 (4 vCPU Intel Xeon @ 2.30GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.defrost:DefrostWindow.peek
#   (line 802 `        if self._state and self._since is not None:`).
# Perturbation: mutant 8297234e122897ff, that guard -> `if False:`, applied in memory (peek recompiled from its own
#   source, called unbound for the mutant arm). Direction: peek duty down to the closed part only.
# Null control: sequences whose flag is off at the peek (on_off_peek, never-on): identical in both arms.
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
OLD = "if self._state and self._since is not None:"
NEW = "if False:"
MUT = mutated(defrost, defrost.DefrostWindow.peek, OLD, NEW)
moved = []
for name, (seq, at) in SEQS.items():
    b, m = drive(seq, at), drive(seq, at, MUT)
    print(f"RESULT {name}: baseline={b} mutant={m}")
    if b != m:
        moved.append(name)
b = drive(*SEQS["carried_level_reobserved"])
m = drive(*SEQS["carried_level_reobserved"], peek_fn=MUT)
print(f"RESULT duty_baseline={b[0]}")
print(f"RESULT duty_mutant={m[0]}")
print(f"RESULT observed_baseline={int(b[2])} mutant={int(m[2])}")
print(f"RESULT any_defrost_baseline={int(b[1] > 0 or b[0] > 0)} mutant={int(m[1] > 0 or m[0] > 0)}")
print(f"RESULT sequences_moved={len(moved)} of {len(SEQS)} ({','.join(moved)})")
# Null control: a window whose flag closed before the peek (on_off_peek) and one never on: unchanged.
print(f"RESULT null_delta={int(drive(*SEQS['on_off_peek']) != drive(*SEQS['on_off_peek'], peek_fn=MUT))} count")
footer()
