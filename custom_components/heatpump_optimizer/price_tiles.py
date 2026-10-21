"""The price tiles (#39) and the horizon they are published over (#2257).

A tile answers one fixed what-if after a scheduled solve: a degree cooler, a
degree warmer, power capped at 75 %. The coordinator runs the shadow solve;
everything else -- the perturbation, which figure of the answer a tile reads,
and the averaging -- is here, pure.

THE DEGREE TILES PRICE A DEGREE HELD. A degree is the whole comfort schedule
moved by one kelvin, because that schedule, not ``target_temp``, is what the
plan heats to; moving ``target_temp`` alone moved only the settlement caps and
the terminal value, so the tile priced a side effect. And the figure is the
thermostat baseline's, which starts held at its own target: the plan's own
spend from the live house is a one-off coast (a degree cooler) or heat-up (a
degree warmer), which the monthly scaling multiplies by every horizon in the
month. ``dev/audit/harnesses/r10_advisor_degree.py`` measures both, and the
null: at a flat price and a constant outdoor temperature, where the plan has
no timing to buy, its closed-loop cost per degree it delivers is the held
figure up to the loop's own settlement error.

THE HORIZON. One solve prices one day of weather and prices, so a tile is
published as the mean of its daily means over the last ``HORIZON_DAYS`` local
days: one unusual day moves it by a thirtieth. The days are kept on the tile
and persisted with the ledger, so a restart does not start the mean over.

The tiles live in a per-coordinator side table (``boost.py``'s discipline),
so the coordinator class does not hold state it never computes with.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import date, datetime, timedelta
from typing import Any, TypedDict, cast
from weakref import WeakKeyDictionary

from .payload import PriceTile

#: The owner's horizon (#2257 item 6): "a 30-day rolling average".
HORIZON_DAYS = 30

#: Hours in the month a what-if is scaled to: 30.4 days, the mean month.
MONTH_HOURS = 30.4 * 24.0

#: The tiles, in rotation order.
TILE_NAMES = ("target_minus_1", "target_plus_1", "power_cap_75")


class TileDay(TypedDict):
    """One local day of a tile's samples: their sum and how many."""

    day: str
    sum: float
    count: int


#: Each coordinator's tiles by name: the overrides, the per-day book, the
#: comfort consequence of the latest answer and its stamp.
_BOOKS: WeakKeyDictionary[Any, dict[str, dict[str, Any]]] = WeakKeyDictionary()


def book(owner: Any) -> dict[str, dict[str, Any]]:
    """``owner``'s tiles by name, as the ledger store persists them; the
    functions below take the book, never its owner."""
    return _BOOKS.setdefault(owner, {})


def per_month(delta: float, horizon_hours: float) -> float:
    """A cost difference over a solve's horizon, scaled to a month."""
    return delta * MONTH_HOURS / horizon_hours


def specs(config: Any, max_kw: float) -> list[tuple[str, dict[str, float]]]:
    """#39's fixed perturbation set, from the configuration ONE solve planned with.

    Fixed on purpose: tiles answer the same three questions every day, so
    their drift means the situation changed, not the question. The degree
    tiles move what the record's plan was solved with -- during an away
    setback the configured target would make "one degree lower" a raise
    against the setback plan, and the published trade would carry the wrong
    sign.
    """
    # Every comfort level the schedule has set: the target, day and night,
    # and the weekend and holiday overrides that replace them on their days.
    levels = {
        "target_temp": config.target_temp, "comfort_temp_day": config.comfort_temp_day,
        "comfort_temp_night": config.comfort_temp_night,
        "comfort_temp_day_weekend": config.comfort_temp_day_weekend,
        "comfort_temp_night_weekend": config.comfort_temp_night_weekend,
        "holiday_comfort_day": config.holiday_comfort_day,
        "holiday_comfort_night": config.holiday_comfort_night,
    }

    def degree(step: float) -> dict[str, float]:
        return {key: round(float(v) + step, 1) for key, v in levels.items() if v is not None}

    return list(zip(TILE_NAMES, (
        degree(-1.0), degree(1.0), {"power_cap_kw": round(0.75 * max_kw, 2)})))


def monthly_figure(overrides: Mapping[str, float], answer: Mapping[str, Any]) -> float | None:
    """The monthly figure a tile averages: a degree held, or the plan under a cap."""
    key = "monthly_cost_delta" if "power_cap_kw" in overrides else "monthly_held_cost_delta"
    value = answer.get(key)
    return float(value) if isinstance(value, (int, float)) else None


def _within(days: list[TileDay], today: date) -> list[TileDay]:
    """The days inside the horizon ending ``today``; a day ahead of it is dropped."""
    oldest = (today - timedelta(days=HORIZON_DAYS - 1)).isoformat()
    return [d for d in days if oldest <= d["day"] <= today.isoformat()]


def fold(days: list[TileDay], today: date, value: float) -> list[TileDay]:
    """``days`` with ``value`` added to today's sum, and the horizon applied."""
    key = today.isoformat()
    kept = [d for d in _within(days, today) if d["day"] != key]
    current = next((d for d in days if d["day"] == key), None)
    total, count = (current["sum"], current["count"]) if current else (0.0, 0)
    return [*kept, {"day": key, "sum": total + value, "count": count + 1}]


def record(
    tiles: dict[str, dict[str, Any]], name: str, overrides: dict[str, float],
    answer: Mapping[str, Any], now: datetime,
) -> None:
    """Fold one what-if answer into tile ``name``; an answer without the
    figure the tile reads changes nothing."""
    value = monthly_figure(overrides, answer)
    if value is None:
        return
    tiles[name] = {
        "overrides": overrides,
        "days": fold(list(tiles.get(name, {}).get("days", [])), now.date(), value),
        "min_room_temperature": answer.get("min_room_temperature"),
        "computed_at": now.isoformat(timespec="seconds"),
    }


def published(tiles: Mapping[str, Mapping[str, Any]], today: date) -> dict[str, PriceTile]:
    """Each tile as the sensor publishes it: the horizon mean as its monthly
    figure, how many days that mean covers, and no per-day book."""
    out: dict[str, PriceTile] = {}
    for name, tile in tiles.items():
        days = _within(list(tile.get("days") or []), today)
        if not days:
            continue
        mean = sum(d["sum"] / d["count"] for d in days) / len(days)
        view = {k: v for k, v in tile.items() if k != "days"}
        out[name] = cast(PriceTile, {**view, "monthly_cost_delta": round(mean, 2), "horizon_days": len(days)})
    return out


def _aware(stamp: Any) -> bool:
    try:
        return datetime.fromisoformat(stamp).tzinfo is not None
    except (TypeError, ValueError):
        return False


def restore(out: dict[str, dict[str, Any]], raw: Any, admit: Callable[[str, Any], bool]) -> None:
    """Load the ledger store's tiles into the book ``out``, each field and
    each day admitted on its own, so one bad day costs that day and not the
    tile's other twenty-nine."""
    out.clear()
    if not isinstance(raw, Mapping):
        return
    for name, tile in raw.items():
        if not isinstance(tile, Mapping) or not isinstance(tile.get("days"), list):
            continue
        days = [d for d in tile["days"] if isinstance(d, dict) and admit(name, {"days": [d]})]
        kept = {k: v for k, v in tile.items() if k != "days" and admit(name, {k: v})}
        if not _aware(kept.get("computed_at")):
            kept.pop("computed_at", None)  # a naive stamp is no instant (F3.1)
        if days:
            out[str(name)] = {**kept, "days": days}
