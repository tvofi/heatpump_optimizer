"""The heat an unmetered install can read off its water flow (#2016).

Thermal output is flow x c_p x (supply - return). It is the stand-in for the
signals an install does not have: a power entity or a frequency entity or
sensor each outrank it (:func:`~.thermal_model.probe_install`), so the
estimate exists only where no other signal does, and an install without the
flow key reads exactly what it read before.

Kept free of Home Assistant imports so it can be unit-tested directly, like
``flow_lift``.
"""
from __future__ import annotations

from typing import Any

from . import const
from .flow_lift import read_water_temps
from .thermal_model import probe_install


def thermal_output_kw(
    flow_kg_s: float | None,
    supply_c: float | None,
    return_c: float | None,
) -> float | None:
    """Heat handed to the water in kW, or ``None`` with any input missing.

    A supply no warmer than the return is no output: the pump is idle, or
    the probes are crossed, and a negative kW is not a measurement.
    """
    if flow_kg_s is None or supply_c is None or return_c is None:
        return None
    drop = supply_c - return_c
    return (
        None
        if drop <= 0.0
        else flow_kg_s * const.WATER_CP_KJ_PER_KG_K * drop
    )


def read_heat_output_kw(reader: Any, config: Any) -> float | None:
    """This cycle's thermal output, or ``None`` when it is not to be used.

    ``None`` when the flow key is unset, when a power or frequency signal
    exists, or when the flow, supply or return cannot be read.
    """
    cfg = config or {}
    cap = probe_install(cfg)
    if (
        not cfg.get(const.CONF_FLOW_METER_ENTITY)
        or cap.measured_power
        or cap.frequency
    ):
        return None
    flow = reader.read_flow_kg_s(const.CONF_FLOW_METER_ENTITY)
    supply, returned = read_water_temps(reader)
    return thermal_output_kw(
        flow.value if flow.ok else None, supply, returned
    )
