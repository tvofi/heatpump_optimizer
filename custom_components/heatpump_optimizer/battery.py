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


def build(
    params: Any,
    state: Any,
    *,
    comfort_min: float,
    comfort_max: float,
    dhw_min: float,
    dhw_max: float,
    cop: float,
) -> VirtualBattery:
    """Assemble the battery view from the thermal model's parameters and state."""
    components: list[StorageComponent] = []

    if params.two_zone_enabled:
        components.append(
            StorageComponent(
                name="upper_floor",
                capacity_kwh_per_c=params.upper_floor_thermal_mass,
                temperature=state.upper_floor_temperature,
                min_temperature=comfort_min,
                max_temperature=comfort_max,
                loss_kw_per_c=params.upper_floor_heat_loss,
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
                loss_kw_per_c=params.lower_floor_heat_loss,
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
                loss_kw_per_c=params.heat_loss_coefficient,
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
            max_temperature=comfort_max + 6.0,
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
                max_temperature=comfort_max + 20.0,
                loss_kw_per_c=params.buffer_tank_heat_loss_coefficient,
                ambient_temperature=20.0,
            )
        )

    return VirtualBattery(
        components=components,
        charge_power_kw=params.max_electrical_power,
        cop=cop,
    )
