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

import calendar
import logging
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np

_LOGGER = logging.getLogger(__name__)

#: Months kept before pruning. Two years covers a year-over-year comparison
#: with a margin, and keeps the store size bounded forever.
KEEP_MONTHS = 24


def month_key(when: datetime) -> str:
    return when.strftime("%Y-%m")


def pro_rata_factor(now: datetime) -> float:
    """Calendar days in this month over max(1, day-of-month)."""
    days = calendar.monthrange(now.year, now.month)[1]
    return days / max(1, now.day)


def savings_pct(baseline_sek: float, savings_sek: float) -> float | None:
    """Same clip as optimizer._savings_percentage, but None when the baseline is ~0.

    The optimizer helper returns 0.0 in that case; the published row must omit
    the percentage instead of claiming 0 %.
    """
    if baseline_sek <= 0.01:
        return None
    return float(np.clip(savings_sek / baseline_sek * 100.0, -100.0, 100.0))


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

    def add_savings_settlement(
        self,
        when: datetime,
        *,
        baseline_kw: float | None,
        actual_kwh: float,
        spot: float,
        dt: float,
    ) -> None:
        """Book the two savings lines, or neither.

        ``baseline_kw is None`` means no plan covered the interval — skip.
        A finite 0.0 kW is a real thermostat-off step and must book.
        ``actual_kwh`` is already energy (spot + immersion), not kW.
        """
        if baseline_kw is None:
            return
        if not (
            np.isfinite(baseline_kw)
            and np.isfinite(actual_kwh)
            and np.isfinite(spot)
            and np.isfinite(dt)
        ):
            return
        base_kwh = float(baseline_kw) * float(dt)
        self.add(
            when, "savings_baseline", kwh=base_kwh, sek=base_kwh * float(spot)
        )
        self.add(
            when,
            "savings_actual",
            kwh=float(actual_kwh),
            sek=float(actual_kwh) * float(spot),
        )

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
        lines = data.get("lines")
        if not isinstance(lines, dict):
            return {}
        return {
            name: {
                "kwh": round(float(entry.get("kwh", 0.0)), 3),
                "sek": round(float(entry.get("sek", 0.0)), 2),
            }
            for name, entry in lines.items()
            if isinstance(entry, dict)
        }

    def savings_months(self, now: datetime) -> list[dict]:
        """Published rows: months that booked savings_baseline, oldest first."""
        open_key = month_key(now)
        factor = pro_rata_factor(now)
        rows: list[dict] = []
        for key in sorted(self.months):
            lines = self.months[key].get("lines") or {}
            if "savings_baseline" not in lines:
                continue
            baseline_sek = float(self.line(key, "savings_baseline")["sek"])
            actual_sek = float(self.line(key, "savings_actual")["sek"])
            estimated = key == open_key
            if estimated:
                baseline_sek *= factor
                actual_sek *= factor
            savings_sek = baseline_sek - actual_sek
            rows.append(
                {
                    "month": key,
                    "baseline_sek": round(baseline_sek, 2),
                    "actual_sek": round(actual_sek, 2),
                    "savings_sek": round(savings_sek, 2),
                    "savings_pct": savings_pct(baseline_sek, savings_sek),
                    "estimated": estimated,
                }
            )
        return rows

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
            clean: dict[str, dict] = {}
            dropped = 0
            for key, value in months.items():
                if (
                    isinstance(value, dict)
                    and isinstance(value.get("lines", {}), dict)
                    and isinstance(value.get("meta", {}), dict)
                ):
                    clean[str(key)] = {
                        "lines": value.get("lines", {}),
                        "meta": value.get("meta", {}),
                    }
                else:
                    dropped += 1
            if dropped:
                _LOGGER.warning(
                    "Quarantined %d malformed ledger month(s) on load; "
                    "the rest of the ledger was kept",
                    dropped,
                )
            ledger.months = clean
            ledger._prune()
        return ledger
