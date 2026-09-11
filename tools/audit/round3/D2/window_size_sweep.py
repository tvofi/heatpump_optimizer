"""D2/#777 -- THE FIXER'S instrument, not the finder's. Disclosed as such.

`dst_window_factors.py` beside this file is the finder's harness and is what
`fix-review.md` step 2 means by "the finder's harness".  This one exists because
the #777 fix has a boundary the finder's harness does not sweep: `window_minutes`
larger than an hour.  A reviewer attacking the fix at other configurations
(`fix-review.md` step 6) reaches that boundary immediately, and the honest answer
is a measurement rather than an argument, so it is committed rather than quoted.

METRIC: `live_tracker_mismatch_<day>_<wm>min` = the number of horizon windows i
where `window_factors(mask, midnight, n, dt)[i]` differs from the factor
PRODUCTION ITSELF ASSIGNED that window -- `PeakTracker.observe` driven over
`optimizer._utc_step_starts` instants, then `tracker._window_factor` read back.
`pre777` re-creates the old production expression (`slot0 + timedelta(...)`)
inline, as a DIAGNOSTIC only; nothing here asserts against it.

COMMAND (from the repository root, < 5 s):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D2/window_size_sweep.py

WHAT IT SHOWS, and why the >60 rows are not a regression.  For every window that
DIVIDES the hour -- 15, 30, 60 -- the fix takes the mismatch to 0 on both 2026
Stockholm transitions.  Above an hour it does not, and cannot: the power array
`window_factors` labels is bucketed by STEP INDEX (`optimizer.metering_windows`),
so bucket i holds `window` minutes of REAL time, while `tariff._window_slot`
deliberately keeps a window longer than an hour WALL-anchored, which lets the
autumn fold's repeated hour stretch one metered window to three real hours.
Those are two different partitions of the day and no per-window label reconciles
two partitions.  The reference this script reads is therefore NOT authoritative
above 60 minutes -- it answers "which wall window does this instant fall in",
which is a different question from "which bucket of the power array is this".
Read the >60 rows as the size of that pre-existing partition mismatch, never as
a verdict on the walk.

NULL CONTROL: `control`, 2026-10-18 -- an ordinary Sunday one week before the
fold, same masks, same horizon.  Every cell is 0 at both ends and at every
window size, so a non-zero row anywhere is about the transition and not about
this script.

POPULATION: no shipped install reaches a window above an hour.  All four rows of
`grid_fee.py`'s product catalog set `peak_tariff_window_minutes` to 15, and the
options selector offers `['15', '60']`; both are printed below rather than
asserted here, so a later edit that adds 90 shows up in this output.

BASELINE: da43c9da5fddfc0ded0f538edae4a41311cc4b01 (the #777 merge base).
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import d2lib  # noqa: F401  -- thread pin + sys.path, must be first

from heatpump_optimizer.optimizer import _utc_step_starts
from heatpump_optimizer.tariff import (
    CapacityTariff,
    PeakTracker,
    _window_slot,
    window_factors,
)

d2lib.repo_root_ok()

STHLM = ZoneInfo("Europe/Stockholm")
DAYS = (
    ("autumn", datetime(2026, 10, 25, tzinfo=STHLM)),   # 25-hour day
    ("spring", datetime(2026, 3, 29, tzinfo=STHLM)),    # 23-hour day
    ("control", datetime(2026, 10, 18, tzinfo=STHLM)),  # ordinary Sunday
)
# 15/30/60 divide the hour; 90/120 do not, and are the boundary this exists for.
WINDOWS = (15, 30, 60, 90, 120)
MASK = dict(peak_hours=((7.0, 20.0),), offpeak_factor=0.0)


def metered(tariff: CapacityTariff, slot0: datetime, n: int) -> list[float]:
    """The factor production assigns each window, over real UTC-walked instants."""
    tracker = PeakTracker()
    out = []
    for when in _utc_step_starts(slot0, n, tariff.window_minutes / 60.0):
        tracker.observe(when, 1.0, tariff)
        out.append(tracker._window_factor)
    return out


def main() -> int:
    for label, day in DAYS:
        for wm in WINDOWS:
            t = CapacityTariff(
                enabled=True, price_per_kw=60.0, window_minutes=wm, **MASK
            )
            n = int(round(24 * 60 / wm))
            slot0 = _window_slot(day, wm)
            post = list(window_factors(t, day, n, wm / 60.0))
            # The PRE-#777 production expression, reproduced inline as a
            # diagnostic. Nothing asserts against it; it is here so the two
            # ends are one command instead of a checkout.
            pre = [t.sample_factor(slot0 + timedelta(minutes=wm * i)) for i in range(n)]
            ref = metered(t, slot0, n)
            d2lib.result(
                f"live_tracker_mismatch_{label}_{wm}min",
                f"pre777={sum(1 for i in range(n) if pre[i] != ref[i])} "
                f"post777={sum(1 for i in range(n) if post[i] != ref[i])} "
                f"of_{n}_windows",
            )

    # The population, printed rather than asserted, so a later edit shows here
    # instead of silently widening what "no shipped install reaches it" covers.
    # Both probes print how many rows/lines they actually found, because a probe
    # that swallows its own miss prints a confident zero: the first draft of this
    # one reported `not_a_list_of_rows` and a bare import line, and both read
    # exactly like a real answer.
    from heatpump_optimizer import config_flow
    from heatpump_optimizer.grid_fee import SWEDEN_CATALOG

    rows = [
        row for row in SWEDEN_CATALOG.values()
        if isinstance(row, dict) and "peak_tariff_window_minutes" in row
    ]
    d2lib.result(
        "catalog_window_minutes",
        f"{sorted({row['peak_tariff_window_minutes'] for row in rows})} "
        f"from_{len(rows)}_of_{len(SWEDEN_CATALOG)}_catalog_rows",
    )
    lines = [
        ln.strip()
        for ln in open(config_flow.__file__, encoding="utf-8").read().splitlines()
        if "CONF_PEAK_TARIFF_WINDOW" in ln and "_select(" in ln
    ]
    d2lib.result(
        "options_selector_choices",
        f"{len(lines)}_matching_line(s): "
        + (lines[0][lines[0].find("_select(") :] if lines else "NONE_FOUND"),
    )

    d2lib.env_footer()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
