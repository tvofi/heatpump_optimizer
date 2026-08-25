"""A month-keyed ledger of settled energy money (T1 infrastructure).

Nothing in the integration bucketed anything by calendar month before this:
the cost accumulators are lifetime totals, and the capacity tracker keeps
only the current month's peaks. Every bill is monthly, so the gap kept three
features unbuildable — the contract-type shadow settlement (#23), the grid
fee accounting (#1), and eventually the itemised monthly report (#40, T6).

The shape is deliberately dumb: per month, named lines each carrying kWh and
SEK, plus a small meta block for running month-level statistics (today: the
running mean of the spot price, which the månadsspot contract settles on).
T6 adds per-reason lines beside these; the schema does not change for that,
which is the point of naming lines with strings.

Kept free of Home Assistant imports so it can be unit-tested directly. The
coordinator owns the Store; this owns the arithmetic.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

import numpy as np

#: Months kept before pruning. Two years covers a year-over-year comparison
#: with a margin, and keeps the store size bounded forever.
KEEP_MONTHS = 24


def month_key(when: datetime) -> str:
    return when.strftime("%Y-%m")


@dataclass
class MonthlyLedger:
    """``months[month]["lines"][name] = {"kwh": …, "sek": …}`` plus meta."""

    months: dict[str, dict] = field(default_factory=dict)

    def _month(self, key: str) -> dict:
        month = self.months.get(key)
        if month is None:
            month = {"lines": {}, "meta": {}}
            self.months[key] = month
            self._prune()
        return month

    def _prune(self) -> None:
        extra = sorted(self.months)[: max(0, len(self.months) - KEEP_MONTHS)]
        for key in extra:
            del self.months[key]

    # -- writing ------------------------------------------------------------

    def add(self, when: datetime, line: str, *, kwh: float, sek: float) -> None:
        """Accumulate one settled amount onto a named line."""
        if not (np.isfinite(kwh) and np.isfinite(sek)):
            return
        lines = self._month(month_key(when))["lines"]
        entry = lines.setdefault(line, {"kwh": 0.0, "sek": 0.0})
        entry["kwh"] = float(entry["kwh"]) + float(kwh)
        entry["sek"] = float(entry["sek"]) + float(sek)

    def observe_meta_mean(self, when: datetime, name: str, value: float) -> None:
        """Fold one sample into a running month-level mean (sum and count)."""
        if not np.isfinite(value):
            return
        meta = self._month(month_key(when))["meta"]
        entry = meta.setdefault(name, {"sum": 0.0, "count": 0})
        entry["sum"] = float(entry["sum"]) + float(value)
        entry["count"] = int(entry["count"]) + 1

    # -- reading ------------------------------------------------------------

    def line(self, month: str, name: str) -> dict:
        """One line's totals, zeros when nothing was booked."""
        entry = self.months.get(month, {}).get("lines", {}).get(name)
        if not isinstance(entry, dict):
            return {"kwh": 0.0, "sek": 0.0}
        return {
            "kwh": float(entry.get("kwh", 0.0)),
            "sek": float(entry.get("sek", 0.0)),
        }

    def meta_mean(self, month: str, name: str) -> float | None:
        entry = self.months.get(month, {}).get("meta", {}).get(name)
        if not isinstance(entry, dict) or not entry.get("count"):
            return None
        return float(entry["sum"]) / int(entry["count"])

    def month_summary(self, month: str) -> dict:
        """Every line of one month, rounded for publication."""
        data = self.months.get(month)
        if not isinstance(data, dict):
            return {}
        return {
            name: {
                "kwh": round(float(entry.get("kwh", 0.0)), 3),
                "sek": round(float(entry.get("sek", 0.0)), 2),
            }
            for name, entry in data.get("lines", {}).items()
            if isinstance(entry, dict)
        }

    # -- persistence --------------------------------------------------------

    def as_dict(self) -> dict:
        return {"months": self.months}

    @classmethod
    def from_dict(cls, data: dict | None) -> "MonthlyLedger":
        ledger = cls()
        if not isinstance(data, dict):
            return ledger
        months = data.get("months")
        if isinstance(months, dict):
            ledger.months = {
                str(key): value
                for key, value in months.items()
                if isinstance(value, dict)
            }
            ledger._prune()
        return ledger
