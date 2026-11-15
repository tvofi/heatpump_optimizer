"""The house heat-loss scale's walk under each settling-tail policy, per press arm.

R10-OUTSIDE-LEARNER-ROBUSTNESS-P2's measurement, on tests/boost_drift_replay.py's
own replay: every arm forks from one shared pre-boost state; on each boost day a
space press at each window start, held ``minutes`` and cancelled (the whole
window expires instead), ``count`` presses one cycle apart. ``press`` arms drive
the true house with the boost for the share of each cycle the press held it;
``freeze`` arms run the same presses and tails with the house on the plan, the
freeze with no boost heat behind it.

A policy replaces ``BoostState.settle`` for the arm's run, except
``production``, which runs the tree's own (the ``slope6h`` tail since
R10-OUTSIDE-LEARNER-ROBUSTNESS-P3, owner ruling 2026-11-12):

- ``full``: the full tail from every boost's end, whatever its length;
- ``none``: no tail;
- ``slope6h``: ``12 h + 6 h * ln(boosted / 2 h)``, floor 1.5 h, on the boosted
  sum (the adopted formula, commit 7a76f66c8a);
- ``slope3h``: ``12 h + 3 h * ln(boosted / 2 h)``, floor 1.5 h, each press
  priced at no less than 10 minutes (commit 36f10fd3ba).

Each arm prints ``worst`` (the largest signed excursion of a later 03:00 daily
row from the one before the first boost day) and ``final``. Two verdicts:

- ``PRODUCTION`` reads EQUAL when every production arm's summary equals its
  twin's under the reference policy: ``slope6h`` when it is run, else
  ``full``. Its null control is the ``none`` policy: at least one press
  arm under ``none`` must differ from ``full``, or the comparison is blind
  (exit 1 either way it fails).
- ``BOUND`` per scaled press arm: ``|worst|`` no larger than
  ``press_120x1_full``'s (the brief's absolute acceptance). Printed, not exited
  on; the round-11 precondition a scaled formula must meet.

    PYTHONPATH=tests/hastub:tests:custom_components \\
        python3 dev/audit/harnesses/boost_press_tail_walk.py [--flat] [policy ...]

``--flat``: the flat-price null control. Every day's price is one constant,
so the plan has no price reason to move heat between hours, and the arms
differ only by the boost heat and the freeze. A tail policy's walk measured
against ``full`` under flat prices is the walk with no price-shaped plan
behind the freeze's sample selection.

Default policies ``production full none``. Every arm replays the cycles past
the shared prefix with a production solve each; it is a harness, not a gate
script.
"""
from __future__ import annotations

import math
import sys
from datetime import timedelta

import boost_drift_replay as bdr

from heatpump_optimizer.drift import utc_elapsed_seconds, utc_shift

boost_mod = bdr.boost_mod
LENGTHS = ((10, 1), (30, 1), (60, 1), (120, 1), (10, 4))
WINDOW = timedelta(hours=boost_mod.BOOST_HOURS)
FULL = boost_mod.SPACE_SETTLE_TAIL
FLOOR = timedelta(hours=1.5)


def _scaled(slope: timedelta):
    def tail(boosted):
        if boosted is None or boosted >= WINDOW:
            return FULL
        if boosted <= timedelta(0):
            return FLOOR
        return max(FLOOR, FULL + slope * math.log(boosted / WINDOW))
    return tail


def _settle_with(tail_of, press_min=timedelta(0)):
    """``BoostState.settle`` with the tail ``tail_of(boosted sum)``."""
    def settle(self, end, since):
        if since is None or self.space_boosted is None:
            self.space_boosted = None
        else:
            self.space_boosted += max(press_min, timedelta(seconds=utc_elapsed_seconds(end, since)))
        until = utc_shift(end, tail_of(self.space_boosted))
        held = self.space_settle_until
        if held is None or utc_elapsed_seconds(until, held) > 0:
            self.space_settle_until = until
    return settle


POLICIES = {
    "production": None,
    "full": _settle_with(lambda _b: FULL),
    "none": _settle_with(lambda _b: timedelta(0)),
    "slope6h": _settle_with(_scaled(FULL / 2)),
    "slope3h": _settle_with(_scaled(FULL / 4), press_min=timedelta(minutes=10)),
}


def walk(out: dict) -> tuple[float, float]:
    daily = out["daily"]
    pre = daily[bdr.BOOST_DAYS[0] - 1]
    later = [v / pre - 1.0 for d, v in sorted(daily.items()) if d >= bdr.BOOST_DAYS[0]]
    return max(later, key=abs, default=0.0), out["hh_final"] / pre - 1.0


def comparable(out: dict) -> dict:
    """The arm's summary without its name, which differs between any two arms."""
    return {k: ([s.as_dict() for s in v] if k in ("tagged", "untagged") else v)
            for k, v in out.items() if k != "arm"}


def run(policy: str) -> dict:
    arms = {f"{kind}_{m}x{c}_{policy}": f"{kind}:{m}:{c}"
            for m, c in LENGTHS for kind in ("press", "freeze")}
    production = boost_mod.BoostState.settle
    if POLICIES[policy] is not None:
        boost_mod.BoostState.settle = POLICIES[policy]
    try:
        return bdr.replay(arms)
    finally:
        boost_mod.BoostState.settle = production


def _flat_prices() -> None:
    days = bdr.day_arrays

    def flat(day_index: int):
        p, *rest = days(day_index)
        return (p * 0.0 + float(p.mean()), *rest)
    bdr.day_arrays = flat


def main() -> int:
    argv = sys.argv[1:]
    if "--flat" in argv:
        argv.remove("--flat")
        _flat_prices()
        print("PRICES: flat")
    policies = argv or ["production", "full", "none"]
    outs = bdr.replay({"null_no_boost": "none"})
    for policy in policies:
        outs.update(run(policy))
    for arm, out in outs.items():
        w = walk(out)
        print(f"WALK {arm}: worst {w[0]:+.4f}, final {w[1]:+.4f}, daily {out['daily']}")
    status = 0
    ref = "slope6h" if "slope6h" in policies else "full"
    if "production" in policies and ref in policies:
        pairs = [(a, a[: -len("production")] + ref) for a in outs if a.endswith("_production")]
        same = [comparable(outs[a]) == comparable(outs[b]) for a, b in pairs]
        print(f"PRODUCTION: {'EQUAL' if all(same) else 'DIFFERS'} to {ref} on "
              f"{sum(same)} of {len(pairs)} arms")
        status |= 0 if all(same) else 1
    if "none" in policies and "full" in policies:
        moved = [a for a in outs if a.startswith("press_") and a.endswith("_none")
                 and comparable(outs[a]) != comparable(outs[a[: -len("none")] + "full"])]
        print(f"NULL CONTROL: none differs from full on {len(moved)} press arm(s): "
              f"{'SEES' if moved else 'BLIND'}")
        status |= 0 if moved else 1
    whole = walk(outs["press_120x1_full"])[0] if "press_120x1_full" in outs else math.nan
    for arm in (a for a in outs if a.startswith("press_") and a.split("_")[-1] in ("slope6h", "slope3h")):
        w = walk(outs[arm])[0]
        print(f"BOUND {arm}: |{w:+.4f}| vs |{whole:+.4f}|: "
              f"{'PASS' if abs(w) <= abs(whole) else 'FAIL'}")
    return status


if __name__ == "__main__":
    sys.exit(main())
