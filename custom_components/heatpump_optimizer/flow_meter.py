"""The heat the pump delivers, read off a thermal meter or the water flow.

Two sources, one answer (:func:`read_heat_output_kw`). A thermal power entity
(#1955 fold e) is the direct reading and wins whenever it is configured,
whatever else the install has; the flow meter is not consulted then, even in
a cycle the thermal reading is unusable, so a learner never mixes the two.
Without one, thermal output is flow x c_p x (supply - return) (#2016): the
stand-in for the signals an install does not have, so a power entity or a
frequency entity or sensor each outrank it
(:func:`~.thermal_model.probe_install`). An install with neither key reads
exactly what it read before.

Kept free of Home Assistant imports so it can be unit-tested directly, like
``flow_lift``.
"""
from __future__ import annotations

from typing import Any

from . import const
from .flow_lift import read_water_temps
from .thermal_model import UNMETERED_POWER_FREEZE, probe_install


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


def read_heat_output_kw(
    reader: Any,
    config: Any,
    temps: tuple[float | None, float | None] | None = None,
) -> float | None:
    """This cycle's thermal output, or ``None`` when it is not to be used.

    A configured thermal entity answers alone: its reading in kW, ``None``
    when unusable or negative. Otherwise the flow meter: ``temps`` is the
    cycle's (supply, return) when already read, so the two slots are not
    read twice. ``None`` when the flow key is unset, when a power or
    frequency signal exists, or when the flow, supply or return cannot be
    read.
    """
    cfg = config or {}
    cap = probe_install(cfg)
    if cap.measured_heat:
        heat = reader.read_power_kw(const.CONF_THERMAL_POWER_ENTITY)
        kw = heat.value if heat.ok else None
        return kw if kw is not None and kw >= 0.0 else None
    if (
        not cfg.get(const.CONF_FLOW_METER_ENTITY)
        or cap.measured_power
        or cap.frequency
    ):
        return None
    flow = reader.read_flow_kg_s(const.CONF_FLOW_METER_ENTITY)
    supply, returned = temps or read_water_temps(reader)
    return thermal_output_kw(
        flow.value if flow.ok else None, supply, returned
    )


def replay_freeze(
    frozen: str | None, config: Any, heat_kw: float | None
) -> str | None:
    """An interval learner's freeze, lifted where a thermal meter measured it.

    For the two learners that replay the interval (the house heat-loss scale
    and the lower floor's ratio). The unmetered-power freeze (#1955 c)
    exists because the replay would
    otherwise credit commanded kilowatts the pump never delivered; an
    interval whose delivered heat a thermal entity measured (``heat_kw``,
    the replay's own figure) replays that heat instead, so the reason is
    gone. Every other reason stands, and so does this one for an interval
    without a measurement or an install whose figure is the flow meter's.
    """
    lifted = (
        frozen == UNMETERED_POWER_FREEZE
        and heat_kw is not None
        and probe_install(config).measured_heat
    )
    return None if lifted else frozen


def cop_evidence(
    modelled_cop: float,
    commanded_kw: float,
    electrical_kw: float,
    heat_kw: float | None,
    cop_scale: float,
) -> tuple[float, float]:
    """``(observed COP, cop_scale target)`` for one interval.

    With ``heat_kw`` measured the COP is observed outright, heat over
    electricity, and the target is the current scale times its ratio to
    ``modelled_cop``. Without it the delivered heat is assumed to be what the
    plan intended, ``commanded_kw`` at ``modelled_cop``, which is the
    v4.0.5 inference and its float order, kept bit for bit.
    """
    if heat_kw is None:
        observed = modelled_cop * commanded_kw / electrical_kw
        return observed, cop_scale * commanded_kw / electrical_kw
    observed = heat_kw / electrical_kw
    return observed, cop_scale * observed / modelled_cop


def space_reference_cop(
    model: Any, outdoor_c: float, heat_kw: float | None, supply_c: float | None
) -> float:
    """The space COP an interval's evidence is judged against.

    A measured COP (``heat_kw``) carries the lift of the supply the machine
    ran at, so it is judged at that supply: the one COP law at a known water
    temperature, which :meth:`~.thermal_model.ThermalModel.compute_cop_dhw`
    is. The scale then learns what is left once lift is accounted for, and no
    longer walks with the weather on a direct plant (``flow_lift``). Without
    a measured COP, or without a fresh supply, the plan's own price, as
    before: the commanded inference already carries the lift in the draw
    (``_cop_reference_curve``'s #1067 note).
    """
    if heat_kw is None or supply_c is None:
        return float(model.compute_cop(outdoor_c))
    return float(model.compute_cop_dhw(outdoor_c, supply_c))


def observe_water(bias: Any, reader: Any, config: Any) -> None:
    """Fold this cycle's supply, return and flow into the flow-bias holder."""
    temps = read_water_temps(reader)
    bias.observe_temps(
        *temps, heat_output_kw=read_heat_output_kw(reader, config, temps)
    )
