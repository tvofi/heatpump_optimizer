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
import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Mapping

import numpy as np

from .payload import ContractComparison, SavingsMonth

_LOGGER = logging.getLogger(__name__)

#: Months kept before pruning. Two years covers a year-over-year comparison
#: with a margin, and keeps the store size bounded forever.
KEEP_MONTHS = 24

#: The lines a receipt's total adds up: what the month cost. Every other line
#: restates one of these -- ``space`` and ``dhw`` split the spot energy by
#: circuit, the ``reason:`` lines partition it by why, and the two
#: ``savings_`` lines compare it with a thermostat -- so adding any of them
#: counts the same money again (R9-UX-6).
BILLED_LINES = ("spot", "grid_fee", "capacity", "immersion", "wear")

#: The month's billed peak, kW, beside the capacity line it prices.
CAPACITY_PEAK_META = "capacity_peak_kw"


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


def _leaf(raw: Any) -> float:
    """One persisted amount as a finite float; raises on anything else."""
    if isinstance(raw, bool):
        raise TypeError("a bool is not an amount")
    value = float(raw)
    if not math.isfinite(value):
        raise ValueError("non-finite amount")
    return value


def _clean_month(value: Any) -> dict[str, Any] | None:
    """One persisted month with every leaf a finite number, or None to drop it.

    Structure alone let a hand-edited ``"12,5"`` load, and every refresh then
    raised in ``line()`` (#1518). The month is dropped whole, as the accuracy,
    price and wear loaders drop the entry a bad leaf sits in.
    """
    if not isinstance(value, dict):
        return None
    lines, meta = value.get("lines", {}), value.get("meta", {})
    if not isinstance(lines, dict) or not isinstance(meta, dict):
        return None
    try:
        return {
            "lines": {
                str(name): {"kwh": _leaf(e["kwh"]), "sek": _leaf(e["sek"])}
                for name, e in lines.items()
            },
            "meta": {
                str(name): {"sum": _leaf(e["sum"]), "count": int(_leaf(e["count"]))}
                for name, e in meta.items() if int(_leaf(e["count"])) >= 1  # the first fold writes 1
            },
        }
    except (TypeError, ValueError, KeyError, IndexError, OverflowError):
        return None


@dataclass
class MonthlyLedger:
    """``months[month]["lines"][name] = {"kwh": …, "sek": …}`` plus meta."""

    months: dict[str, dict[str, Any]] = field(default_factory=dict)

    def _month(self, key: str) -> dict[str, Any]:
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

    def book_capacity(self, month: str, peak_kw: float, price_per_kw: float) -> None:
        """Restate ``month``'s capacity charge from the peaks billed so far.

        Set, not added: the billed peak is a running figure the peak tracker
        restates, so the line follows it, and it keeps the last statement
        made before the tracker wipes the month's peaks at month change. The
        line is money, not energy (kWh 0), like the wear line.
        """
        if not month or not (math.isfinite(peak_kw) and math.isfinite(price_per_kw)):
            return
        data = self._month(month)
        data["lines"]["capacity"] = {"kwh": 0.0, "sek": float(peak_kw) * float(price_per_kw)}
        data["meta"][CAPACITY_PEAK_META] = {"sum": float(peak_kw), "count": 1}

    def observe_spot_and_settle_savings(
        self,
        when: datetime,
        spot: float,
        pending: dict[str, float | None],
        actual_kwh: float,
        dt: float,
    ) -> None:
        """Sample spot for the month mean, then book savings if baseline exists."""
        self.observe_meta_mean(when, "spot_price", spot)
        self.settle_interval_savings(when, pending, actual_kwh, spot, dt)

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

    def settle_interval_savings(
        self,
        when: datetime,
        pending: dict[str, float | None],
        actual_kwh: float,
        spot: float,
        dt: float,
    ) -> None:
        """Book savings from a settled interval's pending snapshot."""
        self.add_savings_settlement(
            when,
            baseline_kw=pending.get("baseline_kw"),
            actual_kwh=actual_kwh,
            spot=spot,
            dt=dt,
        )

    # -- reading ------------------------------------------------------------

    def line(self, month: str, name: str) -> dict[str, float]:
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

    def month_summary(self, month: str) -> dict[str, dict[str, float]]:
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

    def savings_months(self, now: datetime) -> list[SavingsMonth]:
        """Published rows: months that booked savings_baseline, oldest first."""
        open_key = month_key(now)
        factor = pro_rata_factor(now)
        rows: list[SavingsMonth] = []
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

    def as_dict(self) -> dict[str, Any]:
        return {"months": self.months}

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "MonthlyLedger":
        ledger = cls()
        if not isinstance(data, dict):
            return ledger
        months = data.get("months")
        if isinstance(months, dict):
            clean: dict[str, dict[str, Any]] = {}
            dropped = 0
            for key, value in months.items():
                month = _clean_month(value)
                if month is not None:
                    clean[str(key)] = month
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


def billed_total(lines: Mapping[str, Mapping[str, float]]) -> tuple[float, list[str]]:
    """(total SEK, the billed lines it adds) of a receipt's published lines."""
    basis = [name for name in BILLED_LINES if name in lines]
    return round(sum(float(lines[name]["sek"]) for name in basis), 2), basis


def restate_total(report: dict[str, Any]) -> dict[str, Any]:
    """A stored receipt with its total restated from its own lines.

    Receipts frozen before R9-UX-6 summed every line but the reasons; their
    lines are right, so the total is re-derived from them on load.
    """
    lines = report.get("lines")
    if not isinstance(lines, dict):
        return report
    total, basis = billed_total(lines)
    return {**report, "total_sek": total, "basis": basis}


def freeze_month_report(
    ledger: MonthlyLedger,
    month: str,
    *,
    compressor_starts: int,
    contract_comparison: ContractComparison,
) -> dict[str, Any]:
    """One month's itemised receipt, frozen at rollover (#40).

    Everything in it comes from the ledger's own lines -- the receipt is a
    PRESENTATION of the accounting, never a second accounting. The reason
    lines partition the spot line by construction, and the receipt states how
    well that held rather than assuming it.
    """
    lines = ledger.month_summary(month)
    reasons = {
        name.split(":", 1)[1]: entry
        for name, entry in lines.items()
        if name.startswith("reason:")
    }
    # Reconcile on the RAW ledger values, not the rounded publication ones:
    # with a full reason set the accumulated 2-decimal rounding alone can
    # exceed the tolerance and cry wolf on a perfectly partitioned month.
    raw = [ledger.line(month, name) for name in ledger.months.get(month, {}).get("lines", {})
           if name.startswith("reason:")]
    reason_kwh = sum(entry["kwh"] for entry in raw)
    reason_sek = sum(entry["sek"] for entry in raw)
    raw_spot = ledger.line(month, "spot")
    spot = lines.get("spot", {"kwh": 0.0, "sek": 0.0})
    billed = {name: entry for name, entry in lines.items() if not name.startswith("reason:")}
    total, basis = billed_total(billed)
    report: dict[str, Any] = {
        "month": month,
        "lines": billed,
        "reasons": reasons,
        "total_kwh": round(spot["kwh"] + lines.get("immersion", {}).get("kwh", 0.0), 3),
        "total_sek": total,
        "basis": basis,
        "compressor_starts": compressor_starts,
        "contract_comparison": contract_comparison,
        # The partition check, published instead of asserted: a receipt that
        # hides its own bookkeeping error is worse than one that admits it.
        # None, not False, for a month with no reason lines at all -- a
        # pre-T6 month never had a partition to break, and publishing
        # "failed" for it would make an upgrade look like the very bug the
        # flag exists to expose.
        "reasons_reconcile": (
            bool(
                abs(reason_kwh - raw_spot["kwh"]) <= 0.05
                and abs(reason_sek - raw_spot["sek"]) <= 0.05
            )
            if reasons
            else None
        ),
    }
    for key, name, digits in (("mean_spot_price", "spot_price", 4),
                              ("capacity_peak_kw", CAPACITY_PEAK_META, 2)):
        mean = ledger.meta_mean(month, name)
        if mean is not None:
            report[key] = round(mean, digits)
    return report


def roll_receipts(
    ledger: MonthlyLedger,
    reports: dict[str, dict[str, Any]],
    current: str,
    freeze: Callable[[str], dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], bool]:
    """#40: freeze a receipt for every ledger month before ``current``.

    Derived from the ledger itself rather than a "last month seen" marker:
    any ledger month strictly before the current one that has no frozen
    receipt yet gets one now. Self-healing across restarts and downtime
    spanning a month end -- and bounded, because the ledger prunes itself
    and each month freezes exactly once.

    Pure: it RETURNS the receipts to keep and whether a month closed, rather
    than writing into the mapping it is handed. ``_month_reports`` is the
    coordinator's, and a collaborator module mutating coordinator-held state
    is the hazard ``shared_inplace_writes`` prices (R9-EG-A4), so the caller
    adopts the returned mapping by rebinding its own slot. The copy is
    shallow on purpose: a receipt is frozen once and never edited in place.
    """
    closed = sorted(k for k in ledger.months if k < current and k not in reports)
    kept = dict(reports)
    for month in closed:
        # Defense in depth: MonthlyLedger.from_dict already quarantines
        # malformed months at load time, but a still-live month can in
        # principle be freezable-yet-broken. Never let one bad month wedge
        # every future cycle forever (#D1-01) -- skip it and mark it closed
        # with an empty receipt so the cycle completes and it is not retried.
        try:
            kept[month] = freeze(month)
        except Exception:  # noqa: BLE001 -- must never wedge the coordinator
            _LOGGER.warning(
                "Skipping malformed ledger month %s while freezing monthly "
                "receipts; recording an empty receipt instead",
                month,
                exc_info=True,
            )
            kept[month] = {"month": month, "lines": {}}
    # Receipts follow the ledger's retention; a receipt for a month the
    # ledger no longer holds cannot be reconciled anyway.
    for old in sorted(kept)[: max(0, len(kept) - KEEP_MONTHS)]:
        del kept[old]
    return kept, bool(closed)
