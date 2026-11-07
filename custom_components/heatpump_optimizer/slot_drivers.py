"""Why the plan does what it does at one step, as signed weights (R10-WHY-NOW-WIDGET).

``classify_space_steps`` names one ranked reason per step; this module says
how much each of five inputs pushed that step towards running or idling.
Each push is read from the solve's own inputs at the step, in [-1, 1],
positive meaning run, and the five are normalised into signed percents of
one push whose magnitudes sum to 100. They are read after the solve and
never written back, so the plan cannot move.

Pure numpy and no Home Assistant import: the optimizer calls
``space_drivers`` once per result, and ``get_current_action`` reads step
``i``'s entry through ``why_now_at`` at the index it already found.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from .optimizer import OptimizationConfig, OptimizationResult, _Horizon
    from .payload import CurrentAction, WhyNow, WhyNowDriver

#: The five drivers, in the order a tie in weight is listed.
DRIVER_CODES = ("price_rank", "comfort_floor", "mold_guard", "away", "forecast")
#: The forecast window: the eight hours ``_anticipatory_weights`` looks ahead.
FORECAST_LOOKAHEAD_H = 8.0
#: One outdoor degree's share of a full forecast push: a 10 °C swing between
#: now and the coming window's mean saturates it.
FORECAST_OUTDOOR_SCALE_C = 10.0
#: The narrowest half-band a comfort push is scaled by, °C, so a band
#: squeezed to its 0.5 °C minimum cannot turn a hundredth of a degree into
#: a full push.
MIN_HALF_BAND_C = 0.5
#: A weight whose magnitude is under this many percent points neither way.
NEUTRAL_BELOW_PCT = 0.5


def away_floor_drops(
    config: OptimizationConfig, step_hours: np.ndarray, times: list[datetime],
    away_floor_drop_c: float | None,
) -> np.ndarray | None:
    """Per step, the floor the away setback and the holiday profile took off.

    The setback arrives as one figure (``SolveLimits.away_floor_drop_c``).
    The holiday calendar reaches the solve through ``get_temp_bounds``, which
    keys the day/night split on the holiday profile's hours; its drop is that
    floor against the one the same instant has on a working day. None when
    neither applies.
    """
    hol = config.holiday_dates
    on_holiday = [bool(hol) and t.date() in hol for t in times]
    if away_floor_drop_c is None and not any(on_holiday):
        return None
    regular = replace(config, holiday_dates=frozenset())
    return np.array([
        max(0.0, float(away_floor_drop_c or 0.0)) + (
            max(0.0, regular.get_temp_bounds(hour, when=t)[0]
                - config.get_temp_bounds(hour, when=t)[0])
            if held else 0.0
        )
        for hour, t, held in zip(step_hours, times, on_holiday)
    ])


def _price_push(prices: np.ndarray) -> np.ndarray:
    """1 - 2r, r the step's rank in the horizon (ties share the middle)."""
    n = prices.size
    if n < 2:
        return np.zeros(n)
    less = (prices[None, :] < prices[:, None]).sum(axis=1)
    equal = (prices[None, :] == prices[:, None]).sum(axis=1)
    rank = (less + 0.5 * (equal - 1)) / (n - 1)
    return 1.0 - 2.0 * rank


def _forecast_push(h: _Horizon, p_max_kw: float) -> np.ndarray:
    """Weather now against the coming window's mean: run ahead of the cold,
    the wind and rain, idle ahead of the sun."""
    n = h.n_steps
    span = max(1, int(FORECAST_LOOKAHEAD_H / h.dt))
    out = np.asarray(h.outdoor_temps[:n], dtype=float)
    hlf = np.asarray(h.heat_loss_factors[:n], dtype=float)
    sun = np.asarray(h.solar_gains[:n], dtype=float)
    push = np.zeros(n)
    for i in range(n):
        end = min(i + span, n)
        push[i] = (
            (out[i] - out[i:end].mean()) / FORECAST_OUTDOOR_SCALE_C
            + (hlf[i:end].mean() - hlf[i])
            - (sun[i:end].mean() - sun[i]) / max(p_max_kw, 1.0)
        )
    return np.clip(push, -1.0, 1.0)


def space_drivers(
    h: _Horizon, room_temps: np.ndarray, p_max_kw: float,
) -> dict[str, list[float]]:
    """Code -> one signed weight per step, percent of that step's push."""
    n = h.n_steps
    room = np.asarray(room_temps[:n], dtype=float)
    ceiling = np.asarray(h.temp_max_bounds[:n], dtype=float)
    floor = np.asarray(
        h.comfort_floors if h.comfort_floors is not None else h.temp_min_bounds,
        dtype=float,
    )[:n]
    half = np.maximum((ceiling - floor) / 2.0, MIN_HALF_BAND_C)
    mold = (
        np.nan_to_num(np.asarray(h.mold_floors, dtype=float)[:n], nan=-1e9, neginf=-1e9)
        if h.mold_floors is not None else floor
    )
    drops = h.away_floor_drops[:n] if h.away_floor_drops is not None else np.zeros(n)
    push = np.vstack([
        _price_push(np.asarray(h.prices[:n], dtype=float)),
        np.clip((floor + half - room) / half, -1.0, 1.0),
        np.clip((mold - floor) / half, 0.0, 1.0),
        -np.clip(drops / half, 0.0, 1.0),
        _forecast_push(h, p_max_kw),
    ])
    total = np.abs(push).sum(axis=0)
    weights = np.divide(
        100.0 * push, total, out=np.zeros_like(push), where=total > 0
    )
    return {
        code: [round(float(w), 1) + 0.0 for w in row]  # + 0.0: no -0.0
        for code, row in zip(DRIVER_CODES, weights)
    }


def _direction(weight: float) -> str:
    if abs(weight) < NEUTRAL_BELOW_PCT:
        return "neutral"
    return "run" if weight > 0 else "idle"


def step_reasons(result: OptimizationResult, i: int) -> CurrentAction:
    """Step ``i``'s reason codes, then its why-now drivers when it has any:
    every per-step explanation the current action carries."""
    out: CurrentAction = {
        "space_reason": result.space_reasons[i] if i < len(result.space_reasons) else None,
        "dhw_reason": result.dhw_reasons[i] if i < len(result.dhw_reasons) else None,
    }
    if (why_now := why_now_at(result, i)) is not None:
        out["why_now"] = why_now
    return out


def why_now_at(result: OptimizationResult, i: int) -> WhyNow | None:
    """Step ``i``'s drivers, largest first; None where the plan has none,
    ``i`` is past them, or the step's price is unknown."""
    drivers: dict[str, list[Any]] = result.space_drivers
    if not drivers or any(i >= len(v) for v in drivers.values()):
        return None
    if i >= len(result.prices) or not np.isfinite(result.prices[i]):
        return None
    if result.price_known and (i >= len(result.price_known) or not result.price_known[i]):
        return None
    rows: list[WhyNowDriver] = [
        {"code": code, "direction": _direction(w), "weight": w}
        for code in DRIVER_CODES
        if code in drivers
        for w in (float(drivers[code][i]),)
    ]
    rows.sort(key=lambda d: -abs(d["weight"]))
    return {"t": result.timestamps[i].isoformat(), "drivers": rows}
