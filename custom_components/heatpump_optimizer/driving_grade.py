"""The Driving grade (#65) and the drivers that move it (#2816).

The grade replays each priced day's energy against that day's flat
time-mean spot price: buying ``FULL_SAVING`` below flat scores 100, at or
above flat scores 0, folded over days by ``SCORE_ALPHA``. Its drivers split
the day's saving against the flat replay exactly in two -- the energy bought
below the day's running mean as it was bought (``tally``), and the rest --
each weighed against the day's own mean, and fold with the grade's own EMA,
so they sum to it (``REFERENCE``: flat buying scores 0).

The coordinator owns the day book and the grade; the drivers ride this
module's per-coordinator side table (``held``), persisted beside the grade.
Only ``held`` sees the coordinator; the rest take the book or the drivers.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any
from weakref import WeakKeyDictionary

import numpy as np

from .const import SCORE_ALPHA, finite_float

#: The drivers a day's saving splits into, in display order.
CODES = ("cheap_hours", "dear_hours")
#: Buying this fraction below the day's flat price scores 100.
FULL_SAVING = 0.2
#: The grade the drivers move from: buying flat at the day's mean price.
REFERENCE = 0.0

_DRIVERS_BY_OWNER: WeakKeyDictionary[Any, dict[str, float]] = WeakKeyDictionary()


def _add(book: dict[str, Any], key: str, value: float) -> None:
    book[key] = finite_float(book.get(key), 0.0) + value


def held(owner: Any) -> dict[str, float]:
    """``owner``'s drivers, folded with its grade (empty until a day folds)."""
    return _DRIVERS_BY_OWNER.setdefault(owner, {})


def tally(day: Mapping[str, Any], kwh: float, sek: float, spot: float, hours: float) -> dict[str, Any]:
    """The day book with one priced interval booked in it, as a new book.

    The kWh and the SEK paid for them (SIGNED: a paid negative-price hour
    lowers the day's mean paid price), the time-weighted spot price, and --
    for an interval bought below the day's running mean, ``spot_sum /
    spot_h`` with this interval already in it -- the cheap side's share.
    """
    book = dict(day)
    if np.isfinite(sek):
        _add(book, "kwh", max(0.0, kwh))
        _add(book, "sek", sek)
    if np.isfinite(spot) and hours > 0:
        _add(book, "spot_sum", spot * hours)
        _add(book, "spot_h", hours)
        if np.isfinite(sek) and spot < book["spot_sum"] / book["spot_h"]:
            _add(book, "kwh_lo", max(0.0, kwh))
            _add(book, "sek_lo", sek)
    return book


def book_keys(day: Mapping[str, Any]) -> tuple[str, ...]:
    """The cheap side's day-book keys a stored ``day`` carries (absent: none booked)."""
    return tuple(key for key in ("kwh_lo", "sek_lo") if key in day)


def day_drivers(book: Mapping[str, Any], mean_spot: float, sample: float) -> dict[str, float]:
    """One priced day's ``sample`` split into its signed drivers, summing to it.

    ``cheap_hours`` pushes the grade up, ``dear_hours`` down; a clipped
    sample scales both, and one of 0 leaves both at 0.
    """
    kwh, sek = finite_float(book.get("kwh"), 0.0), finite_float(book.get("sek"), 0.0)
    kwh_lo, sek_lo = finite_float(book.get("kwh_lo"), 0.0), finite_float(book.get("sek_lo"), 0.0)
    saved = {
        "cheap_hours": mean_spot * kwh_lo - sek_lo,
        "dear_hours": mean_spot * (kwh - kwh_lo) - (sek - sek_lo),
    }
    total = sum(saved.values())
    scale = sample / total if sample > 0.0 and total > 0.0 else 0.0
    return {code: value * scale for code, value in saved.items()}


def fold(drivers: dict[str, float], grade: float | None, book: Mapping[str, Any], mean_spot: float) -> float:
    """Fold one priced day into ``grade`` (None seeds it) and ``drivers``; the new grade."""
    paid_mean = finite_float(book.get("sek"), 0.0) / finite_float(book.get("kwh"), 0.0)
    saved_fraction = 1.0 - paid_mean / mean_spot
    sample = float(np.clip(saved_fraction / FULL_SAVING, 0.0, 1.0)) * 100.0
    day = day_drivers(book, mean_spot, sample)
    if grade is not None:
        sample = (1.0 - SCORE_ALPHA) * grade + SCORE_ALPHA * sample
        day = {
            code: (1.0 - SCORE_ALPHA) * finite_float(drivers.get(code), 0.0) + SCORE_ALPHA * value
            for code, value in day.items()
        }
    drivers.clear()
    drivers.update(day)
    return sample


def published(drivers: Mapping[str, float], grade: float | None) -> list[dict[str, Any]]:
    """The published drivers of ``grade``: none without one.

    What the held drivers do not account for -- a grade folded before they
    were kept -- is ``earlier_days``, decaying with the EMA.
    """
    if grade is None:
        return []
    shown = [{"code": code, "points": finite_float(drivers.get(code), 0.0)} for code in CODES]
    rest = grade - REFERENCE - sum(d["points"] for d in shown)
    return [*shown, {"code": "earlier_days", "points": rest}]


def restore(drivers: dict[str, float], stored: Any, admitted: Callable[[Any], bool]) -> None:
    """Adopt into ``drivers`` what ``as_stored`` wrote, when the store ``admitted`` it."""
    if isinstance(stored, Mapping) and admitted(stored):
        drivers.clear()
        drivers.update({code: float(stored[code]) for code in CODES if code in stored})


def as_stored(drivers: Mapping[str, float], grade: float | None) -> dict[str, float]:
    """The drivers to persist beside ``grade``: none without one."""
    return dict(drivers) if grade is not None else {}
