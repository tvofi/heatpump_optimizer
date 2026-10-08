"""The heat an unmetered install can read off its water flow (#2016).

Thermal output is flow x c_p x (supply - return). It is the stand-in for the
signals an install does not have: a power entity or a frequency entity or
sensor each outrank it (:func:`flow_is_signal`), so the estimate exists only
where no other signal does, and an install without the flow key reads
exactly what it read before. Where it exists, the interval learners replay
it (:func:`learner_power_kw`, :func:`replay_heat_kw`).

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


def flow_is_signal(config: Any) -> bool:
    """The flow meter is this install's heat signal.

    Its key holds an entity and no power or frequency signal outranks it,
    by the one install probe (#1955).
    """
    cfg = config or {}
    cap = probe_install(cfg)
    return bool(cfg.get(const.CONF_FLOW_METER_ENTITY)) and not (
        cap.measured_power or cap.frequency
    )


def learner_power_kw(
    heat_kw: float | None,
    params: Any,
    commanded_kw: float,
    dhw_share: float,
    signals: Any,
) -> float | None:
    """The electrical kW an interval learner replays where the meter is the signal.

    ``0.0``: the metered heat enters the replay as heat
    (:func:`replay_heat_kw`), so no electrical power and no COP stand between
    the meter and the heat-loss fit, which no longer leans on the COP curve
    or on the pump tracking its plan. ``None`` is no sample: no reading this
    interval (stale, negative, an unknown unit or crossed probes -- the
    stale power meter's rule, never the commanded guess), or heat the meter
    cannot tell from hot water: a planned hot-water share, or an observed
    mode that heats no rooms. A two-tank plant keeps ``commanded_kw``.
    """
    if params.two_tank_modelled:
        return commanded_kw
    if (
        heat_kw is None
        or dhw_share > 0.0
        or (signals.mode_observed and not signals.space_heat)
    ):
        return None
    return 0.0


def replay_heat_kw(heat_kw: float | None, params: Any) -> float:
    """The metered heat an interval learner's replay is fed, kW.

    The step's free-heat input joins the hydronic mix exactly like the
    pump's own heat, which is what the meter read. On a two-tank plant that
    input charges the wood tank instead, so there the step has no route for
    the pump's metered heat and it is not fed. ``0.0`` wherever the flow
    meter is not the signal: ``heat_kw`` is ``None`` there
    (:func:`read_heat_output_kw`).
    """
    return 0.0 if heat_kw is None or params.two_tank_modelled else heat_kw


def read_heat_output_kw(
    reader: Any,
    config: Any,
    temps: tuple[float | None, float | None] | None = None,
) -> float | None:
    """This cycle's thermal output, or ``None`` when it is not to be used.

    ``temps`` is the cycle's (supply, return) when already read, so the
    two slots are not read twice. ``None`` when the flow key is unset, when a power or frequency signal
    exists, or when the flow, supply or return cannot be read.
    """
    if not flow_is_signal(config):
        return None
    flow = reader.read_flow_kg_s(const.CONF_FLOW_METER_ENTITY)
    supply, returned = temps or read_water_temps(reader)
    return thermal_output_kw(
        flow.value if flow.ok else None, supply, returned
    )


def observe_water(bias: Any, reader: Any, config: Any) -> None:
    """Fold this cycle's supply, return and flow into the flow-bias holder."""
    temps = read_water_temps(reader)
    bias.observe_temps(*temps)
    bias.heat_output_kw = read_heat_output_kw(reader, config, temps)
