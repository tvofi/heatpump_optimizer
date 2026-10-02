from __future__ import annotations
from .payload import Payload


def published_but_rejected(data: Payload) -> object:
    # producer: coordinator._insight_view sets insight.compressor_starts.wear_price_per_start
    a = (data.get("insight") or {}).get("compressor_starts", {}).get("wear_price_per_start")
    # producer: disinfection.DisinfectionSwitch.view(), spread into _dhw_view
    b = data.get("dhw_disinfection_switch")
    # producer: _build_plan_views sets space_plan["valve_target_schedule"]
    return (a, b)


def unpublished_but_accepted(data: Payload) -> object:
    # no producer sets insight.wear_price_per_start
    a = (data.get("insight") or {}).get("wear_price_per_start")
    # no producer sets a top-level valve_target_schedule
    b = data.get("valve_target_schedule")
    return (a, b)


def subscript_reads(data: Payload) -> object:
    a = data["dhw_disinfection_switch"]  # published, undeclared
    b = data["insight"]["compressor_starts"]["wear_price_per_start"]  # published, undeclared
    c = data["insight"]["wear_price_per_start"]  # declared, never published
    d = data["valve_target_schedule"]  # declared, never published top-level
    e: float = data.get("horizon_hourz", 24.0)  # unknown key via get, value used typed
    f = data.get("horizon_hourz")  # unknown key via get, value unused
    return (a, b, c, d, e, f)
