"""The house, published as a virtual battery.

The building fabric plus the buffer and DHW tanks together form real energy
storage. The integration modelled it internally and never exposed it, so from
the outside a heat pump looks like an opaque load rather than the flexible
asset it is.

Two payoffs from publishing the abstraction:

1. Other Home Assistant energy automations can reason about the heat pump
   alongside a real battery, instead of treating it as a black box.
2. It is the precondition for flexibility market participation (FCR-D, mFRR via
   an aggregator), where thermal storage can earn money for capacity the user
   already owns.

**State of charge is defined against the comfort band**, not against absolute
zero. Energy stored above the minimum acceptable temperature is what is
actually available; the rest is not dischargeable without making the house
uncomfortable, so counting it would overstate the asset.

**Round-trip efficiency is where the COP and the standing losses show up.**
Charging is done at COP > 1, which makes the "efficiency" exceed 100% if
measured naively in electrical terms — so it is reported in thermal terms,
where standing loss is the only round-trip cost and the number means what a
battery person expects it to mean.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from .const import WOOD_TANK_MAX_TEMP

_LOGGER = logging.getLogger(__name__)


@dataclass
class StorageComponent:
    """One thermal store, expressed in battery terms."""

    name: str
    #: kWh/°C
    capacity_kwh_per_c: float
    temperature: float
    min_temperature: float
    max_temperature: float
    #: kW/°C, used for the standing loss and hence the round-trip efficiency.
    loss_kw_per_c: float = 0.0
    ambient_temperature: float = 20.0

    @property
    def usable_capacity_kwh(self) -> float:
        """Energy the store can hold between its comfort floor and its ceiling."""
        span = max(0.0, self.max_temperature - self.min_temperature)
        return self.capacity_kwh_per_c * span

    @property
    def stored_kwh(self) -> float:
        """Energy currently available above the floor. Never negative."""
        above = max(0.0, self.temperature - self.min_temperature)
        return self.capacity_kwh_per_c * above

    @property
    def soc(self) -> float:
        """State of charge, 0-1, against the usable span."""
        usable = self.usable_capacity_kwh
        if usable <= 1e-9:
            return 0.0
        return min(1.0, self.stored_kwh / usable)

    @property
    def standing_loss_kw(self) -> float:
        return max(
            0.0, self.loss_kw_per_c * (self.temperature - self.ambient_temperature)
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "temperature": round(self.temperature, 2),
            "stored_kwh": round(self.stored_kwh, 3),
            "usable_capacity_kwh": round(self.usable_capacity_kwh, 3),
            "soc_percent": round(self.soc * 100.0, 1),
            "standing_loss_kw": round(self.standing_loss_kw, 4),
        }


@dataclass
class VirtualBattery:
    """Aggregate view of every thermal store in the system."""

    components: list[StorageComponent]
    #: Electrical charge rate limit, kW. The compressor sets this.
    charge_power_kw: float = 0.0
    #: COP at current conditions, needed to convert electrical to thermal.
    cop: float = 3.0

    @property
    def stored_kwh(self) -> float:
        return sum(c.stored_kwh for c in self.components)

    @property
    def usable_capacity_kwh(self) -> float:
        return sum(c.usable_capacity_kwh for c in self.components)

    @property
    def soc(self) -> float:
        usable = self.usable_capacity_kwh
        if usable <= 1e-9:
            return 0.0
        return min(1.0, self.stored_kwh / usable)

    @property
    def charge_rate_kw(self) -> float:
        """Thermal charge rate: what the compressor can actually put in."""
        return self.charge_power_kw * max(self.cop, 0.1)

    @property
    def discharge_rate_kw(self) -> float:
        """Rate at which stored heat leaves usefully.

        The house discharges by *not heating* — the standing loss is the
        discharge. Unlike a real battery there is no way to discharge faster on
        demand, which is a genuine limitation of the analogy and is reported
        rather than papered over.
        """
        return sum(c.standing_loss_kw for c in self.components)

    @property
    def hours_of_autonomy(self) -> float | None:
        """How long the stored heat lasts at the current discharge rate."""
        rate = self.discharge_rate_kw
        if rate <= 1e-6:
            return None
        return self.stored_kwh / rate

    def round_trip_efficiency(self, hold_hours: float = 6.0) -> float:
        """Fraction of stored thermal energy still there after ``hold_hours``.

        Thermal, not electrical: charging happens at COP > 1, so an electrical
        round-trip figure would exceed 100% and mean nothing to anyone reading
        it as a battery specification.
        """
        stored = self.stored_kwh
        if stored <= 1e-9:
            return 0.0
        lost = self.discharge_rate_kw * hold_hours
        return max(0.0, min(1.0, (stored - lost) / stored))

    def as_dict(self) -> dict[str, Any]:
        autonomy = self.hours_of_autonomy
        return {
            "stored_energy_kwh": round(self.stored_kwh, 2),
            "usable_capacity_kwh": round(self.usable_capacity_kwh, 2),
            "state_of_charge_percent": round(self.soc * 100.0, 1),
            "charge_rate_kw": round(self.charge_rate_kw, 2),
            "charge_power_electrical_kw": round(self.charge_power_kw, 2),
            "discharge_rate_kw": round(self.discharge_rate_kw, 3),
            "hours_of_autonomy": (
                round(autonomy, 2) if autonomy is not None else None
            ),
            "round_trip_efficiency_6h": round(
                self.round_trip_efficiency(6.0) * 100.0, 1
            ),
            "components": [c.as_dict() for c in self.components],
        }


#: Which entry of the coordinator's ``reading_ok`` map backs each store's
#: temperature. The slab is integrated from the floor return rather than
#: sensed, so it is measured exactly while that sensor reads -- the same rule
#: the Slab Temperature sensor is gated on. The wood tank has no entry: it is
#: in the view at all only when a wood-tank temperature was sensed (issue
#: #40), so its presence already is its measurement.
COMPONENT_READINGS: dict[str, str] = {
    "house": "upper_floor_temperature",
    "upper_floor": "upper_floor_temperature",
    "lower_floor": "lower_floor_temperature",
    "slab": "slab_temperature",
    "dhw_tank": "dhw_temperature",
    "buffer_tank": "buffer_tank_temperature",
}


def label_measured(view: dict[str, Any], reading_ok: Any) -> dict[str, Any]:
    """Say which of the battery's stores stand on a thermometer.

    Every component temperature comes out of ``ThermalState``, and a field
    there is overwritten only when its entity read OK -- so on an install
    with no probes the whole view is assembled from constructor defaults
    (55/40/22/21 °C) and published as a ``BATTERY`` percentage and an
    ``ENERGY_STORAGE`` kWh, both ``MEASUREMENT``, which is a long-term
    statistics series of a number nothing measured (#282).

    The figures themselves are left exactly as they were. The view is a
    model and the model is the point; dropping a component would change the
    state-of-charge denominator for every partly-probed install, silently
    rescaling a recorded series, which is a worse defect than the one being
    fixed. What is added is the disclosure the numbers never carried: per
    component, and as two lists an entity can gate on.
    """
    flags = reading_ok or {}
    modelled: list[str] = []
    measured: list[str] = []
    for component in view.get("components") or []:
        key = COMPONENT_READINGS.get(component.get("name"))
        ok = bool(flags.get(key)) if key else True
        component["measured"] = ok
        (measured if ok else modelled).append(component.get("name"))
    view["measured_components"] = measured
    view["modelled_components"] = modelled
    return view


def build(
    params: Any,
    state: Any,
    *,
    comfort_min: float,
    comfort_max: float,
    dhw_min: float,
    dhw_max: float,
    cop: float,
    slab_max: float | None = None,
) -> VirtualBattery:
    """Assemble the battery view from the thermal model's parameters and state.

    ``slab_max`` is the slab's useful ceiling — the optimizer's own settlement
    cap. Optional so the view still assembles without one, in which case it
    falls back to the comfort ceiling; every caller in the integration passes
    it.
    """
    components: list[StorageComponent] = []

    # The view reports the same house the dynamics simulate, so every loss
    # figure carries the learned corrections: the overall scale on both
    # zones, and the learned split on the lower one (whose docstring says
    # every consumer of the dynamics must go through it). Raw configured
    # values here showed autonomy figures for a house the model itself no
    # longer believes in. Both default to 1.0, so a fresh install is
    # unchanged.
    loss_scale = params.house_heat_loss_scale
    if params.two_zone_enabled:
        components.append(
            StorageComponent(
                name="upper_floor",
                capacity_kwh_per_c=params.upper_floor_thermal_mass,
                temperature=state.upper_floor_temperature,
                min_temperature=comfort_min,
                max_temperature=comfort_max,
                loss_kw_per_c=params.upper_floor_heat_loss * loss_scale,
                ambient_temperature=state.outdoor_temperature,
            )
        )
        components.append(
            StorageComponent(
                name="lower_floor",
                capacity_kwh_per_c=params.lower_floor_thermal_mass,
                temperature=state.lower_floor_temperature,
                min_temperature=comfort_min,
                max_temperature=comfort_max,
                loss_kw_per_c=params.lower_floor_heat_loss_learned * loss_scale,
                ambient_temperature=state.outdoor_temperature,
            )
        )
    else:
        components.append(
            StorageComponent(
                name="house",
                capacity_kwh_per_c=params.room_thermal_mass,
                temperature=state.room_temperature,
                min_temperature=comfort_min,
                max_temperature=comfort_max,
                loss_kw_per_c=params.heat_loss_coefficient * loss_scale,
                ambient_temperature=state.outdoor_temperature,
            )
        )

    components.append(
        StorageComponent(
            name="slab",
            capacity_kwh_per_c=params.slab_thermal_mass,
            temperature=state.slab_temperature,
            # The slab is only useful down to the room temperature it feeds.
            min_temperature=comfort_min,
            # The optimizer's own settlement cap: the slab temperature above
            # which stored heat is worth nothing, sized from the demand the
            # weather in front of the house actually creates. This was
            # `comfort_max + 6.0` — the last magic offset left over from the
            # v4.0.6 sweep that took `comfort + 20` off the buffer tank. A
            # fixed 29.0 °C at the default ceiling is not the same number as
            # the settlement cap in ANY direction: on the default parameters
            # it is too high (cap 27.4 °C at −15 outdoor), and on a radiator
            # install, where the emitter is weak and the loop must run hot to
            # sustain the target, it is far too low (cap 48.3 °C). The view is
            # report-only, so nothing the optimizer does changes; what changes
            # is that the two numbers now come from one formula.
            #
            # Clamped to the plant's own ceiling, and only here. The cap is
            # `target + demand / slab_heat_transfer`, unbounded above as that
            # coefficient falls: at the `set_thermal_parameters` schema's
            # minimum of 0.01 kW/°C it reaches 531 °C, which would publish
            # 2560 kWh of "usable capacity" for a floor loop. No water-side
            # store in this system can exceed the tank's rated ceiling, so
            # that is the bound. It changes no objective — the optimizer
            # settles against the unclamped cap exactly as before, and that
            # unboundedness is a real edge case still open against the
            # optimizer itself.
            max_temperature=(
                comfort_max + 6.0
                if slab_max is None
                else min(float(slab_max), float(params.buffer_max_temp))
            ),
            loss_kw_per_c=0.0,
            ambient_temperature=state.room_temperature,
        )
    )

    if params.dhw_enabled and state.dhw_temperature is not None:
        components.append(
            StorageComponent(
                name="dhw_tank",
                capacity_kwh_per_c=params.dhw_tank_thermal_mass,
                temperature=state.dhw_temperature,
                min_temperature=dhw_min,
                max_temperature=dhw_max,
                loss_kw_per_c=params.dhw_tank_heat_loss_coefficient,
                ambient_temperature=20.0,
            )
        )

    if state.buffer_tank_temperature is not None:
        components.append(
            StorageComponent(
                name="buffer_tank",
                capacity_kwh_per_c=params.buffer_tank_thermal_mass,
                temperature=state.buffer_tank_temperature,
                min_temperature=comfort_min,
                # The tank's real ceiling — the same `buffer_max_temp` the
                # simulation clamps at and the settlement caps read — not a
                # `comfort + 20` magic offset. That offset (43 °C at the
                # default ceiling) published 100 % state of charge for a tank
                # barely half full: a 40 °C tank read 88.5 % against a 70 °C
                # rating's ~43 %. Report-only, so the physical rating applies
                # unconditionally; the wood tank one component down already
                # shares its cap constant with the optimizer the same way.
                max_temperature=params.buffer_max_temp,
                loss_kw_per_c=params.buffer_tank_heat_loss_coefficient,
                ambient_temperature=20.0,
            )
        )

    if (
        params.two_tank_modelled
        and state.wood_tank_temperature is not None
    ):
        # The wood tank is a real store when the two-tank topology is
        # modelled (issue #40): heat a burn left in it displaces bought
        # heat like any other component. Report-only, like the whole view.
        components.append(
            StorageComponent(
                name="wood_tank",
                capacity_kwh_per_c=params.wood_tank_thermal_mass,
                temperature=state.wood_tank_temperature,
                min_temperature=comfort_min,
                max_temperature=WOOD_TANK_MAX_TEMP,
                loss_kw_per_c=params.wood_tank_heat_loss_coefficient,
                ambient_temperature=20.0,
            )
        )

    return VirtualBattery(
        components=components,
        charge_power_kw=params.max_electrical_power,
        cop=cop,
    )
