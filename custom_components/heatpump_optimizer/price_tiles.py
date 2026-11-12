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

THE CAP TILE PRICES THE PLAN IN STEADY STATE (#2257). Both plans, the live
configuration's and the capped one, are solved again from a start held at
each one's own schedule (``SolveInputs.held_start``), and each one's spend
plus the heat it left unstored (``deferred_energy_cost``) is differenced:
the fuse advisor reads the same figure, and so does the what-if panel for a
change that moves no comfort target. The held start holds the rooms and
the slab, not a tank: a hot-water ask's figure moves with the measured tank
and turns sign with the hour
(``dev/audit/harnesses/r10_advisor_steady_seams.py``, arm ``pair``), which
docs/dashboard-card.md says. From the measured house the settled
figure still moved with where the house started, and a cap, which can only
cost, read as a saving on some starts; unsettled, a cap that left the house
colder at the horizon's end read as one too.

A SCHEDULE CHANGE IS AN ESTIMATE, NOT TWO PLANS (#2257). Two plans solved
from held starts read a comfort or day-window change against its own sign
(``dev/audit/harnesses/r10_advisor_steady_carrier.py``), so the panel's
figure for one is ``schedule_figure``: the energy a thermostat holding each
schedule draws over the average day of the week ahead, at the day's average
weather and average price.
It excludes the optimiser's load shifting, on both sides. The degree tiles
keep the held figure, the same thermostat priced at each hour's own price.
``dev/audit/harnesses/r10_advisor_residue.py whatif`` measures the figures.

THE HORIZON. One solve prices one day of weather and prices, so a tile is
published as the mean of its daily means over the last ``HORIZON_DAYS`` local
days: one unusual day moves it by a thirtieth. The days are kept on the tile
and persisted with the ledger, so a restart does not start the mean over.

THE CAP TILE'S CLOCK (#2257). Its refresh is three solves where a degree
tile's is one, and on every third scheduled solve that put a recorded day's
cycle half again over its CPU budget (``tests/replay.py``, ``cycle_cost``).
The steady figure starts from held rooms, so it moves with the horizon's
prices and weather and not with the house: the tile is refreshed at most
every ``STEADY_REFRESH_HOURS``, and between refreshes its turn in the
rotation solves nothing and the tile stands as last recorded. The clock
starts at a coordinator's first cap turn, which solves nothing either: one
refresh in a timed cycle of that recorded day is by itself over the budget,
and a start is when a host has least CPU to spare.

The tiles live in a per-coordinator side table (``boost.py``'s discipline),
so the coordinator class does not hold state it never computes with.
"""
from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from datetime import date, datetime, timedelta
from typing import Any, TypedDict, cast
from weakref import WeakKeyDictionary

from .const import finite_float
from .payload import PriceTile

#: The owner's horizon (#2257 item 6): "a 30-day rolling average".
HORIZON_DAYS = 30

#: Hours in the month a what-if is scaled to: 30.4 days, the mean month.
MONTH_HOURS = 30.4 * 24.0

#: A schedule ask's steady figure once more, at the what-if plan's own average
#: purchase price. Present, None where that price is unusable, exactly when
#: the steady figure is the schedule estimate; absent when it is the pair's.
SHIFTED_KEY = "monthly_steady_cost_delta_shifted"

#: The least time between two refreshes of a tile that reads the steady
#: figure: four samples of the sliding price horizon in a tile's day, where
#: the rotation took one every third solve.
STEADY_REFRESH_HOURS = 6.0

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


#: Each coordinator's rotation position; not persisted.
_CURSORS: WeakKeyDictionary[Any, int] = WeakKeyDictionary()


#: When each coordinator's steady tile last took its turn, or first came up
#: for one; not persisted, so a restart waits one clock before a refresh.
_STEADY_TAKEN: WeakKeyDictionary[Any, datetime] = WeakKeyDictionary()


def take(
    owner: Any, specs: list[tuple[str, dict[str, float]]], now: datetime,
) -> tuple[str, dict[str, float]] | None:
    """``owner``'s next spec, or None on the turn of a steady tile still inside
    its clock, which its first turn starts. The rotation moves before the
    solve, so a failing or cancelled spec cannot block the others: it is
    retried on the next pass, the steady one at its next clock, since the
    clock counts turns taken and not answers. A turn stamped ahead of ``now``
    has no age (#775) and is taken."""
    cursor = _CURSORS.get(owner, 0)
    _CURSORS[owner] = cursor + 1
    name, overrides = specs[cursor % len(specs)]
    if "power_cap_kw" in overrides:
        taken = _STEADY_TAKEN.setdefault(owner, now)
        if 0.0 <= (now - taken).total_seconds() < STEADY_REFRESH_HOURS * 3600.0:
            return None
        _STEADY_TAKEN[owner] = now
    return name, overrides


def per_month(delta: float, horizon_hours: float) -> float:
    """A cost difference over a solve's horizon, scaled to a month."""
    return delta * MONTH_HOURS / horizon_hours


def monthly_deltas(
    live: Any, sim: Any, extra: float, horizon_hours: float, steady: tuple[Any, Any] | None = None,
) -> dict[str, float]:
    """A what-if's monthly figures against the plan it shadows.

    ``live`` and ``sim`` are the two solves' results, ``extra`` the what-if's
    spend outside its solve (wood). The plan's spend; the same choice held from
    a steady start, the thermostats' (the degree tiles'); and the plan's spend
    with the heat each plan left unstored bought back. Only the first carries
    the whole one-off coast or heat-up. ``steady`` is the same pair solved
    again from held starts, live side first: with it the answer carries the
    steady figure, settled the same way (the panel's, the cap tile's and the
    fuse advisor's); without it the key is absent, never a fallback.
    """
    spend = sim.predicted_cost + extra - live.predicted_cost
    held = {} if steady is None else {"monthly_steady_cost_delta": round(per_month(
        steady[1].predicted_cost + steady[1].deferred_energy_cost + extra
        - steady[0].predicted_cost - steady[0].deferred_energy_cost, horizon_hours), 2)}
    return {
        **held,
        "monthly_cost_delta": round(per_month(spend, horizon_hours), 2),
        "monthly_held_cost_delta": round(per_month(sim.baseline_cost - live.baseline_cost, horizon_hours), 2),
        "monthly_settled_cost_delta": round(per_month(
            spend + sim.deferred_energy_cost - live.deferred_energy_cost, horizon_hours), 2),
    }


def realised_price(result: Any, dt_hours: float) -> float:
    """What one plan pays per kWh on average: its spend over its energy; nan for a plan that buys none."""
    kwh = (float(sum(result.power_schedule)) + float(sum(result.dhw_power_schedule or ()))) * dt_hours
    return float(result.predicted_cost) / kwh if kwh > 0.0 else math.nan


def schedule_figure(
    live_kwh: float, sim_kwh: float, mean_price: float, extra: float, horizon_hours: float,
    shifted_price: float = math.nan,
) -> dict[str, float | None]:
    """A schedule change's steady figure: an estimate, not a plan's money (#2257).

    ``live_kwh`` and ``sim_kwh`` are what a thermostat holding each schedule
    draws over a day of the day's average weather
    (``HeatPumpOptimizer.reference_day``); their difference is priced at
    ``mean_price``, the average of the horizon's prices, and ``extra`` is the
    what-if's spend outside its solve (wood). It excludes the optimiser's
    load shifting on both sides. An energy that is not finite gives no key,
    never another figure.

    The optimiser buys that energy below the mean, so the same difference is
    priced once more at ``shifted_price``, the what-if plan's own average
    purchase price (``realised_price``), under ``SHIFTED_KEY``: the card shows
    the two as a range. On a day of price peaks the mean-price figure is two
    to three times the other
    (``dev/audit/harnesses/r10_advisor_steady_bracket.py``). A price that is
    not finite and positive gives None there: the key itself says the figure
    is this estimate and not the pair's.
    """
    def month(price: float) -> float:
        return round(per_month((sim_kwh - live_kwh) * price * horizon_hours / 24.0 + extra, horizon_hours), 2)

    if not math.isfinite((sim_kwh - live_kwh) * mean_price):
        return {}
    priced = math.isfinite(shifted_price) and shifted_price > 0.0
    return {"monthly_steady_cost_delta": month(mean_price), SHIFTED_KEY: month(shifted_price) if priced else None}


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
    """The monthly figure a tile averages: a degree held, or the plan under a cap in steady state."""
    key = "monthly_steady_cost_delta" if "power_cap_kw" in overrides else "monthly_held_cost_delta"
    return finite_float(answer.get(key))


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
