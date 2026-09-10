"""Firewood price and the cheaper-than-pump rule. Does not detect fires."""
from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from datetime import datetime, timedelta
from typing import Any

from .const import (
    CONF_DHW_WOOD_COIL_ENABLED,
    CONF_EXTERNAL_HEAT_ENABLED,
    CONF_EXTERNAL_HEAT_ENTITY,
    CONF_WOOD_FURNACE_EFFICIENCY,
    CONF_WOOD_FURNACE_ENABLED,
    CONF_WOOD_PACKING,
    CONF_WOOD_PRICE_SEK_M3,
    CONF_WOOD_TANK_BOTTOM_ENTITY,
    CONF_WOOD_TANK_TOP_ENTITY,
    CONF_WOOD_TYPE,
)

WOOD_KWH_M3 = {
    "birch": {"packed": 1900.0, "loose": 1140.0},
    "pine": {"packed": 1500.0, "loose": 900.0},
    "mixed": {"packed": 1700.0, "loose": 1020.0},
}
PUMP_HOUR_KW = 0.05


def _optional_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        if isinstance(value, str):
            return float(value)
    except (TypeError, ValueError):
        return None
    return None


def _force_float(value: object, default: float = 0.0) -> float:
    got = _optional_float(value)
    return default if got is None else got


def useful_kwh_m3(wood_type: str, packing: str, efficiency: float) -> float:
    return WOOD_KWH_M3[wood_type][packing] * float(efficiency) / 100.0


def liters_to_kwh(
    liters: float, wood_type: str, packing: str, efficiency: float
) -> float:
    return float(liters) / 1000.0 * useful_kwh_m3(wood_type, packing, efficiency)


def wood_sek_per_kwh(
    price_sek_m3: float, wood_type: str, packing: str, efficiency: float
) -> float:
    useful = liters_to_kwh(1000.0, wood_type, packing, efficiency)
    if useful <= 0.0:
        raise ValueError("useful_kwh_m3 must be positive")
    return float(price_sek_m3) / useful


def wood_furnace_inferred(config: dict[str, Any]) -> bool:
    if config.get(CONF_WOOD_TANK_TOP_ENTITY) or config.get(
        CONF_WOOD_TANK_BOTTOM_ENTITY
    ):
        return True
    if config.get(CONF_DHW_WOOD_COIL_ENABLED):
        return True
    if config.get(CONF_EXTERNAL_HEAT_ENABLED):
        return True
    if config.get(CONF_EXTERNAL_HEAT_ENTITY):
        return True
    return False


def wood_furnace_on(config: dict[str, Any]) -> bool:
    if CONF_WOOD_FURNACE_ENABLED in config:
        return bool(config[CONF_WOOD_FURNACE_ENABLED])
    return wood_furnace_inferred(config)


def wood_fuel_ready(config: dict[str, Any]) -> bool:
    if not wood_furnace_on(config):
        return False
    if not (
        config.get(CONF_WOOD_TANK_TOP_ENTITY)
        or config.get(CONF_WOOD_TANK_BOTTOM_ENTITY)
    ):
        return False
    if not (
        config.get(CONF_EXTERNAL_HEAT_ENABLED)
        or config.get(CONF_DHW_WOOD_COIL_ENABLED)
    ):
        return False
    if config.get(CONF_WOOD_TYPE) not in WOOD_KWH_M3:
        return False
    packing = config.get(CONF_WOOD_PACKING)
    if packing not in WOOD_KWH_M3["birch"]:
        return False
    try:
        price = float(config.get(CONF_WOOD_PRICE_SEK_M3) or 0.0)
        eff = float(config.get(CONF_WOOD_FURNACE_EFFICIENCY) or 0.0)
    except (TypeError, ValueError):
        return False
    return price > 0.0 and 10.0 <= eff <= 95.0


def cheaper_hour_count(
    wood_sek: float,
    prices: Sequence[object],
    cops: Sequence[object],
    space_kw: Sequence[object],
    dhw_kw: Sequence[object],
    threshold: float = PUMP_HOUR_KW,
) -> int:
    n = 0
    for price, cop, space, dhw in zip(prices, cops, space_kw, dhw_kw, strict=False):
        if max(_force_float(space), _force_float(dhw)) <= threshold:
            continue
        cop_f = _force_float(cop)
        if cop_f <= 0.0:
            continue
        if wood_sek < _force_float(price) / cop_f:
            n += 1
    return n


def _scan_wood_night(
    now: datetime,
    prices: Sequence[object],
    timestamps: Sequence[datetime],
    cops: Sequence[object],
    wood_sek: float,
    n: int,
) -> tuple[int | None, bool]:
    horizon_end = timestamps[0] + timedelta(hours=48)
    best_i: int | None = None
    best_margin = 0.0
    expensive_next = False
    for i in range(n):
        when = timestamps[i]
        if when < now or when >= horizon_end:
            continue
        cop = _force_float(cops[i] if i < len(cops) else 0.0)
        if cop <= 0.0:
            continue
        pump = _force_float(prices[i]) / cop
        margin = pump - float(wood_sek)
        hour = when.hour + when.minute / 60.0
        if (hour >= 18.0 or hour < 6.0) and margin > best_margin:
            best_margin = margin
            best_i = i
        if when.date() > now.date() and margin < -0.05:
            expensive_next = True
    return best_i, expensive_next


def night_advice(
    *,
    now: datetime,
    prices: Sequence[object],
    timestamps: Sequence[datetime],
    cops: Sequence[object],
    wood_sek: float,
    tank_soc: float,
) -> dict[str, Any]:
    """48 h light/skip advice. Advisory only — never lights the stove."""
    if wood_sek <= 0.0 or not prices or not timestamps:
        return {"action": "none", "text": "", "when": None, "reason": ""}
    cop_n = len(cops) if cops else len(prices)
    n = min(len(prices), len(timestamps), cop_n)
    if n <= 0:
        return {"action": "none", "text": "", "when": None, "reason": ""}
    best_i, expensive_next = _scan_wood_night(
        now, prices, timestamps, cops, wood_sek, n
    )
    if tank_soc < 0.4 and best_i is not None:
        stamp = timestamps[best_i]
        return {
            "action": "light",
            "text": f"light {stamp.strftime('%a %H:%M')}",
            "when": stamp.isoformat(),
            "reason": "cheap night and a low tank",
        }
    if tank_soc > 0.8 and expensive_next:
        nxt = now + timedelta(days=1)
        return {
            "action": "skip",
            "text": f"skip {nxt.strftime('%a')}",
            "when": nxt.date().isoformat(),
            "reason": "expensive next day and a full tank",
        }
    return {"action": "none", "text": "", "when": None, "reason": ""}


def wood_cheaper(
    wood_sek: float,
    prices: Sequence[object],
    cops: Sequence[object],
    space_kw: Sequence[object],
    dhw_kw: Sequence[object],
    threshold: float = PUMP_HOUR_KW,
) -> bool:
    return cheaper_hour_count(
        wood_sek, prices, cops, space_kw, dhw_kw, threshold
    ) > 0


def _iso(ts: object) -> str:
    return ts.isoformat() if hasattr(ts, "isoformat") else str(ts)


def _as_dt(raw: object, stamps: Sequence[datetime]) -> datetime | None:
    if raw is None:
        return None
    if isinstance(raw, datetime):
        ts = raw
    else:
        try:
            ts = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return None
    if not stamps:
        return ts
    ref = stamps[0]
    if ts.tzinfo is None and ref.tzinfo is not None:
        return ts.replace(tzinfo=ref.tzinfo)
    if ts.tzinfo is not None and ref.tzinfo is None:
        return ts.replace(tzinfo=None)
    return ts


def wood_slots_to_kw(
    slots: list[dict[str, Any]],
    timestamps: Sequence[datetime],
    dt_hours: float,
    wood_type: str,
    packing: str,
    efficiency: float,
) -> list[float]:
    """kW-thermal per step. liters<=0 or hours<=0 skipped (caller may refuse)."""
    n = len(timestamps)
    out = [0.0] * n
    step = timedelta(hours=float(dt_hours))
    for slot in slots:
        try:
            liters = float(slot.get("liters") or 0.0)
        except (TypeError, ValueError, AttributeError):
            continue
        start = _as_dt(slot.get("start") if isinstance(slot, dict) else None, timestamps)
        end = _as_dt(slot.get("end") if isinstance(slot, dict) else None, timestamps)
        if liters <= 0.0 or start is None or end is None or end <= start:
            continue
        hours = (end - start).total_seconds() / 3600.0
        if hours <= 0.0:
            continue
        rate = liters_to_kwh(liters, wood_type, packing, efficiency) / hours
        for i, ts in enumerate(timestamps):
            if ts < end and ts + step > start:
                out[i] += rate
    return out


def _wood_slots_error(slots: object, stamps: Sequence[datetime]) -> str | None:
    """``invalid_wood_slots`` or None. Empty list is allowed (no fires)."""
    if not isinstance(slots, list):
        return "invalid_wood_slots"
    for slot in slots:
        if not isinstance(slot, dict):
            return "invalid_wood_slots"
        try:
            liters = float(slot.get("liters") or 0.0)
        except (TypeError, ValueError):
            return "invalid_wood_slots"
        start = _as_dt(slot.get("start"), stamps)
        end = _as_dt(slot.get("end"), stamps)
        if liters <= 0.0 or start is None or end is None or end <= start:
            return "invalid_wood_slots"
    return None


def _wood_override_fuel(
    overrides: dict[str, Any], config: dict[str, Any]
) -> tuple[str, str, float, float] | None:
    """Type, packing, price, efficiency — or None when not computable."""
    wtype = overrides.get(CONF_WOOD_TYPE, config.get(CONF_WOOD_TYPE))
    packing = overrides.get(CONF_WOOD_PACKING, config.get(CONF_WOOD_PACKING))
    try:
        price = float(
            overrides[CONF_WOOD_PRICE_SEK_M3]
            if CONF_WOOD_PRICE_SEK_M3 in overrides
            else (config.get(CONF_WOOD_PRICE_SEK_M3) or 0.0)
        )
        eff = float(
            overrides[CONF_WOOD_FURNACE_EFFICIENCY]
            if CONF_WOOD_FURNACE_EFFICIENCY in overrides
            else (config.get(CONF_WOOD_FURNACE_EFFICIENCY) or 0.0)
        )
    except (TypeError, ValueError):
        return None
    if (
        wtype not in WOOD_KWH_M3
        or packing not in WOOD_KWH_M3["birch"]
        or price <= 0.0
        or not (10.0 <= eff <= 95.0)
    ):
        return None
    return wtype, packing, price, eff


def simulate_wood_slots(
    overrides: dict[str, Any],
    config: dict[str, Any],
    n_steps: int,
    dt_hours: float,
    anchor: datetime,
) -> tuple[str | None, list[float] | None, float]:
    """Shadow-only wood injection. Returns (error, kw_or_None, wood_sek)."""
    if "wood_slots" not in overrides:
        return None, None, 0.0
    slots = overrides.get("wood_slots")
    stamps = [
        anchor + timedelta(hours=i * dt_hours) for i in range(n_steps)
    ]
    err = _wood_slots_error(slots, stamps)
    if err:
        return err, None, 0.0
    fuel = _wood_override_fuel(overrides, config)
    if fuel is None:
        return "wood_fuel_not_ready", None, 0.0
    if not isinstance(slots, list):
        return "invalid_wood_slots", None, 0.0
    typed_slots = [slot for slot in slots if isinstance(slot, dict)]
    wtype, packing, price, eff = fuel
    kw = wood_slots_to_kw(typed_slots, stamps, dt_hours, wtype, packing, eff)
    wood_sek = price * sum(_force_float(slot.get("liters")) for slot in typed_slots) / 1000.0
    return None, kw, wood_sek


def detected_wood_slots(
    timestamps: Sequence[datetime], forecast_kw: Sequence[object]
) -> list[dict[str, Any]]:
    """Merge consecutive steps with ``forecast_kw > 0`` into detected slots."""
    if not timestamps:
        return []
    dt = None
    if len(timestamps) >= 2:
        try:
            dt = timestamps[1] - timestamps[0]
        except TypeError:
            dt = None
    out: list[dict[str, Any]] = []
    run_start = None
    n = min(len(timestamps), len(forecast_kw))
    for i in range(n):
        if _force_float(forecast_kw[i]) > 0.0:
            if run_start is None:
                run_start = i
        elif run_start is not None:
            out.append(
                {
                    "start": _iso(timestamps[run_start]),
                    "end": _iso(timestamps[i]),
                    "source": "detected",
                }
            )
            run_start = None
    if run_start is not None:
        last = timestamps[n - 1]
        end_ts = last + dt if dt is not None else last
        out.append(
            {
                "start": _iso(timestamps[run_start]),
                "end": _iso(end_ts),
                "source": "detected",
            }
        )
    return out


def _cops(outdoor: Iterable[object], cop_at: Callable[[float], object]) -> list[float]:
    out: list[float] = []
    for temp in outdoor:
        if temp is None:
            out.append(0.0)
            continue
        try:
            out.append(_force_float(cop_at(_force_float(temp))))
        except (TypeError, ValueError):
            out.append(0.0)
    return out


def build_wood_fuel_view(
    config: dict[str, Any],
    *,
    prices: list[float],
    outdoor: list[float],
    space_kw: list[float],
    dhw_kw: list[float],
    cop_at: Callable[[float], object],
    timestamps: Sequence[datetime],
    forecast_kw: list[float],
    suppressing: bool,
) -> dict[str, Any]:
    """Ready/cheaper/slots. cheaper is False when not ready."""
    wtype = config.get(CONF_WOOD_TYPE)
    packing = config.get(CONF_WOOD_PACKING)
    price = _optional_float(config.get(CONF_WOOD_PRICE_SEK_M3))
    eff = _optional_float(config.get(CONF_WOOD_FURNACE_EFFICIENCY))
    sek = None
    if (
        wtype in WOOD_KWH_M3
        and packing in WOOD_KWH_M3["birch"]
        and price is not None
        and price > 0.0
        and eff is not None
        and 10.0 <= eff <= 95.0
    ):
        try:
            sek = wood_sek_per_kwh(price, wtype, packing, eff)
        except (KeyError, ValueError):
            sek = None
    ready = wood_fuel_ready(config)
    count = 0
    cheaper = False
    if ready and sek is not None:
        cops = _cops(outdoor, cop_at)
        count = cheaper_hour_count(sek, prices, cops, space_kw, dhw_kw)
        cheaper = wood_cheaper(sek, prices, cops, space_kw, dhw_kw)
    slots = detected_wood_slots(timestamps, forecast_kw) if suppressing else []
    view = {
        "ready": ready,
        "cheaper": cheaper,
        "show_whatif": wood_furnace_on(config),
        "sek_per_kwh": sek,
        "type": wtype if wtype in WOOD_KWH_M3 else None,
        "packing": packing if packing in WOOD_KWH_M3["birch"] else None,
        "efficiency": eff,
        "price_sek_m3": price,
        "cheaper_hour_count": count,
        "slots": slots,
    }
    _attach_night_advice(view, config, prices, timestamps, outdoor, cop_at, sek)
    return view


def _attach_night_advice(
    view: dict[str, Any],
    config: dict[str, Any],
    prices: list[float],
    timestamps: Sequence[datetime],
    outdoor: list[float],
    cop_at: Callable[[float], object],
    sek: float | None,
) -> None:
    if not wood_furnace_on(config) or sek is None or not prices or not timestamps:
        return
    soc = _optional_float(config.get("wood_tank_soc"))
    if soc is None:
        soc = 0.5
    cops = _cops(outdoor, cop_at) if outdoor else [3.0] * len(prices)
    advice = night_advice(
        now=timestamps[0],
        prices=prices,
        timestamps=timestamps,
        cops=cops,
        wood_sek=sek,
        tank_soc=soc,
    )
    if advice.get("action") in {"light", "skip"}:
        view["night_advice"] = advice


def wood_fuel_from_coordinator(coord: Any, result: Any) -> dict[str, Any]:
    """Publish helper so the coordinator does not grow a method (#463)."""
    n = len(result.timestamps) if result is not None else 0
    det = coord._external_heat
    suppressing = bool(det.suppressing)
    if result is not None and suppressing:
        forecast_kw = det.forecast_free_heat(
            n,
            coord._opt_config.dt_hours,
            coord._thermal_params.two_tank_modelled,
        )
    else:
        forecast_kw = []
    return build_wood_fuel_view(
        coord._config,
        prices=list(result.prices) if result is not None else [],
        outdoor=list(result.outdoor_temps) if result is not None else [],
        space_kw=list(result.power_schedule) if result is not None else [],
        dhw_kw=(
            list(result.dhw_power_schedule or []) if result is not None else []
        ),
        cop_at=coord._thermal_model.compute_cop,
        timestamps=list(result.timestamps) if result is not None else [],
        forecast_kw=forecast_kw,
        suppressing=suppressing,
    )
