#!/usr/bin/env python3
"""R10-SOLVER (#2240, class P4): does a winner-only tight polish pay in money?

Written by the R10-SOLVER fixer to price the one tolerance change the
owner's #1293 refusal did not already measure. #1293 refused tightening
every L-BFGS-B stop (ftol 1e-6 -> 1e-9) because the better objective lost
money on the backtest's shoulder cell and cost 2.4x thread CPU; D0-s2-01's
own closed loop (``dev/audit/rounds/round10/D0/s2/mpc_mask.py --arm ftol``)
read the same at 1e-10. The narrower candidate is one more
``_lbfgsb_restart`` of the multi-start's WINNER at a tight ftol, adopted
only past ``_LBFGSB_RESTART_KEEP_REL`` -- a fraction of the work, and the
plan moves only where the polish finds a real drop.

Arms, interleaved per cell:
  prod    -- the tree as it stands;
  winner  -- every ``optimizer:_multi_start_minimize`` call's result polished
             once more by ``optimizer:_lbfgsb_restart`` with its
             ``_scoped_minimize`` stop at ``--ftol`` (default 1e-9).

Metrics per cell: the one-shot shipped objective of the first solve (the
captured ``_multi_start_minimize`` objective at the shipped x; ``dJ_pct`` =
(prod - winner)/|prod|, positive = the polish found descent), and the
realised one-day closed-loop cost (``tests/rolling.py:run_rolling``, exec'd up
to its test body, REPLAN 2 h, plant_error 1.0, as mpc_mask.py drives it):
``money_pct`` = (prod - winner)/prod, positive = winner cheaper. Comfort is
printed beside it (min room, degree-steps below 17 C). Null control: the
flat-price cells, where no price shape exists for the polish to trade.

Run from a worktree root, at the base and at the head:

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_solver_winner_polish.py \\
        [--ftol 1e-9] [--cells winter_typical:winter_cold:1:1,...]

Every figure is a count or a cost from the deterministic solve on the
machine that runs it; thread_factor and load1 are printed so a reader can
see the BLAS pin held. No wall time is evidence.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import sys
import time
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402

from heatpump_optimizer import optimizer as OM  # noqa: E402

_SRC = open("tests/rolling.py").read().split('R.section("Stability over three days")')[0]
_G = {"__name__": "rolling_cut"}
exec(compile(_SRC, "tests/rolling.py", "exec"), _G)
run_rolling = _G["run_rolling"]

ap = argparse.ArgumentParser()
ap.add_argument("--ftol", type=float, default=1e-9)
ap.add_argument("--cells", default=(
    "winter_typical:winter_cold:1:1,winter_narrow:winter_cold:1:1,"
    "winter_moderate:winter_cold:1:1,winter_extreme:winter_mild:1:1,"
    "winter_typical:winter_mild:1:0,shoulder:winter_cold:0:0,"
    "flat:winter_cold:1:1,flat:winter_mild:1:0"))
A = ap.parse_args()

REAL_MS = OM._multi_start_minimize
REAL_SM = OM._scoped_minimize
STAT = {"polish": 0, "adopted": 0, "polish_nfev": 0}


def _tight(*a, **kw):
    kw["options"] = dict(kw["options"], ftol=A.ftol)
    res = REAL_SM(*a, **kw)
    STAT["polish_nfev"] += int(getattr(res, "nfev", 0))
    return res


def winner(objective, candidates, bounds, args=(), maxiter=300,
           batch_objective=None, fd_eps=1e-4, **kw):
    best = REAL_MS(objective, candidates, bounds, args, maxiter,
                   batch_objective, fd_eps, **kw)
    memo = OM._memoized_value_and_gradient(batch_objective, bounds, fd_eps, {})
    with mock.patch.object(OM, "_scoped_minimize", _tight):
        out = OM._lbfgsb_restart(best, objective, bounds, args, maxiter, memo)
    STAT["polish"] += 1
    STAT["adopted"] += out is not best
    return out


def one_shot(fn, tz, dh, pp, wp):
    """The first solve's shipped objective under ``fn``: run_rolling's day 1."""
    first = {}

    def cap(objective, candidates, bounds, args=(), maxiter=300, **kw):
        res = fn(objective, candidates, bounds, args, maxiter, **kw)
        if "J" not in first:
            first["J"] = float(objective(np.asarray(res.x, float), *args))
        return res

    with mock.patch.object(OM, "_multi_start_minimize", cap):
        hist = run_rolling(days=1, dhw=dh, two_zone=tz, plant_error=1.0,
                           price_profile=pp, weather_profile=wp)["history"]
    room = hist["room"]
    return (first.get("J", float("nan")), float(hist["cost"].sum()),
            float(room.min()), float(np.maximum(0, 17.0 - room).sum()))


t0p, t0t = time.process_time(), time.thread_time()
money, dj = [], []
for cell in A.cells.split(","):
    pp, wp, tz, dh = cell.split(":")
    tz, dh = bool(int(tz)), bool(int(dh))
    before = dict(STAT)
    jp, cp, mp, bp = one_shot(REAL_MS, tz, dh, pp, wp)
    jw, cw, mw, bw = one_shot(winner, tz, dh, pp, wp)
    g = (cp - cw) / cp
    d = (jp - jw) / abs(jp)
    money.append((pp, g))
    dj.append((pp, d))
    print(f"RESULT cell[{cell}] dJ_pct={100 * d:.4f} money_pct={100 * g:.4f} "
          f"J prod={jp:.4f} winner={jw:.4f} SEK prod={cp:.3f} winner={cw:.3f} "
          f"minroom prod={mp:.2f} winner={mw:.2f} below17 prod={bp:.3f} "
          f"winner={bw:.3f} polish={STAT['polish'] - before['polish']} "
          f"adopted={STAT['adopted'] - before['adopted']} "
          f"polish_nfev={STAT['polish_nfev'] - before['polish_nfev']}", flush=True)
nf = [g for p, g in money if p != "flat"]
fl = [g for p, g in money if p == "flat"]
print(f"RESULT money_pct_nonflat_mean={100 * np.mean(nf):.4f} "
      f"worse_cells={sum(g < 0 for g in nf)}/{len(nf)}")
if fl:
    print(f"RESULT money_pct_flat_mean={100 * np.mean(fl):.4f} (null)")
print(f"RESULT dJ_pct_mean={100 * np.mean([d for _, d in dj]):.4f}")
print(f"RESULT polish={STAT['polish']} adopted={STAT['adopted']} "
      f"polish_nfev={STAT['polish_nfev']}")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
