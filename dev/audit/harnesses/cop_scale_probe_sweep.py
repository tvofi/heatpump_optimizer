#!/usr/bin/env python3
"""The COP scale's heat-ask probe over its domain (R11-OUTSIDE-SELF-SETTING-PUMP, #3662).

Written by the #3662 fixers (the repair seat's ``sweep.py``, then the round-3
design's build), not by a finder: fix review 1 blocked the pull request on a
class, a self-setting pump whose draw swings on its own, and a class is
answered over its domain. Drives ``cop_duty_floor.py``'s ``run`` (the real
coordinator's ``_learn_measured_cop`` under flat 1.5 kW asks on a 4 kW
nameplate, open loop) over two kinds of row, 672 intervals each:

  * ``selfset`` -- a pump drawing ``kw`` x (1 + amp sin(2 pi t / per + phase))
    +-3 % whatever is asked: 1.6, 2.2 and 3.0 kW; periods of 2 to 240 cycles
    (2, 3 and 4 are the length of the probe's own pairs); amplitudes +-15,
    30 and 40 %; seeds 1-5; four phases; and 2.2 kW +-30 % from a persisted
    scale of 0.5 and 0.7. The right verdict is does_not_follow and the right
    scale the configured 1.000; ``follows`` is the defect.
  * ``heatled`` -- a heat-led pump whose true scale ``kw`` (0.45 to 1.3)
    swings +-``amp`` over ``per`` cycles (the weather moving its COP), its
    meter +-``noise``; from 1.0 and from a persisted 0.5. The right verdict
    is follows; ``does_not_follow`` is the defect.

Run it from a worktree root, at each end, then summarize:

    PYTHONPATH=tests/hastub:custom_components:tests \
        python3 dev/audit/harnesses/cop_scale_probe_sweep.py [NPROC] [--null] > OUT
    python3 dev/audit/harnesses/cop_scale_probe_sweep.py --sum OUT

Each line: ``SWEEP kind kw amp per seed phase scale0 noise verdict scale
lowest highest probes band`` (the last four as ``cop_duty_floor.run``'s
``stats``; ``-`` at a tree that has no probe). ``--null`` is null control 1 of
the round-3 design note: the dither's amplitude forced to zero, under which no
row of either kind may latch follows. ``--sum`` counts, per kind and starting
scale, the rows with the wrong verdict, the pending ones by cell, the latched
self-setting rows off the configured scale, the widest band and the most
probes any row started. A tree before the probe prints ``-`` for a verdict
and counts as wrong only what it latched.
"""
from __future__ import annotations

import contextlib
import io
import math
import sys
from collections import Counter
from multiprocessing import Pool

ARGS = sys.argv[1:]
sys.argv = sys.argv[:1]
sys.path.insert(0, "dev/audit/harnesses")

N = 672
NULL = False


def _worker(null: bool) -> None:
    """A pool worker's start: it does not inherit the parent's arguments
    under every start method, so the null control is handed to it."""
    global NULL
    NULL = null


def jobs() -> list[tuple]:
    out: list[tuple] = []
    for kw in (1.6, 2.2, 3.0):
        for per in (2, 3, 4, 8, 16, 32, 48, 64, 80, 96, 120, 144, 240):
            for amp in (0.15, 0.3, 0.4):
                for seed in range(1, 6):
                    for phase in (0.0, math.pi / 2, math.pi, 3 * math.pi / 2):
                        out.append(("selfset", kw, amp, per, seed, phase, None, 0))
    for s0 in (0.5, 0.7):
        for per in (48, 64, 96):
            for seed in range(1, 6):
                out.append(("selfset", 2.2, 0.3, per, seed, math.pi, s0, 0))
    for true in (0.45, 0.6, 0.68, 0.8, 1.3):
        for amp, per in ((0, 1), (0.15, 64), (0.3, 96), (0.3, 48)):
            for noise in (0.0, 0.05, 0.1):
                for seed in range(1, 4):
                    for s0 in (None, 0.5):
                        out.append(("heatled", true, amp, per, seed, 0.0, s0, noise))
    return out


def one(job: tuple) -> str:
    import cop_duty_floor as h

    kind, kw, amp, per, seed, phase, s0, noise = job
    if NULL:
        dither = sys.modules[h.HeatPumpOptimizerCoordinator.__module__.rsplit(".", 1)[0] + ".accuracy"].ScaleDither
        dither.levels = staticmethod(lambda base: (base, base))
    kwargs: dict = {} if s0 is None else {"scale0": s0}
    if kind == "selfset":
        pairs = h.swing(N, kw, [(amp, per)], seed, phase)
    else:
        pairs = h.flat(N, seed=seed)
        kwargs.update(true=lambda t: kw * (1 + amp * math.sin(2 * math.pi * t / per + phase)), noise=noise, noise_seed=seed)
    st: dict = {}
    with contextlib.redirect_stdout(io.StringIO()):
        got = h.run(pairs, p_max=4.0, stats=st, **kwargs)
    return " ".join(str(x) for x in ("SWEEP", *job, st["verdict"], got.split()[1], st["lowest"], st["highest"], st["probes"], st["band"]))


def summarize(path: str) -> None:
    rows = [line.split() for line in open(path) if line.startswith("SWEEP")]
    total, wrong, pending, off = Counter(), Counter(), Counter(), Counter()
    band, probes, shown = 0.0, 0, []
    for _tag, kind, kw, amp, per, _seed, _phase, s0, noise, verdict, scale, _lo, _hi, started, reach in rows:
        key = f"{kind} scale0={s0}"
        total[key] += 1
        bad = verdict == ("follows" if kind == "selfset" else "does_not_follow")
        wrong[key] += bad
        if bad and len(shown) < 12:
            shown.append(" ".join((kind, kw, amp, per, _seed, s0, noise, verdict, scale)))
        if verdict == "pending":
            pending[f"{kind} kw={kw} amp={amp} per={per} scale0={s0} noise={noise}"] += 1
        off[key] += kind == "selfset" and verdict == "does_not_follow" and scale != "1.000"
        band = max(band, 0.0 if reach == "-" else float(reach))
        probes = max(probes, 0 if started == "-" else int(started))
    for key in sorted(total):
        print(f"RESULT {key.replace(' ', '_')}: wrong={wrong[key]}/{total[key]} latched_off_configured={off[key]}")
    print(f"RESULT pending_rows={sum(pending.values())}/{len(rows)} widest_band={band:.3f} most_probes={probes}")
    for cell in sorted(pending):
        print(f"  pending {pending[cell]} of its seeds and phases: {cell}")
    for line in shown:
        print(f"  wrong: {line}")


if __name__ == "__main__":
    if "--sum" in ARGS:
        for name in ARGS[ARGS.index("--sum") + 1:]:
            summarize(name)
    else:
        nproc = next((int(a) for a in ARGS if a.isdigit()), 4)
        with Pool(nproc, initializer=_worker, initargs=("--null" in ARGS,)) as pool:
            for line in pool.imap(one, jobs(), chunksize=4):
                print(line, flush=True)
