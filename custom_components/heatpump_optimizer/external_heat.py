"""Detect an external heat source feeding the tanks, and how confident we are.

Typically a wood furnace tied into the same buffer. Burning electricity to heat
water that is already being heated for free is the single most expensive
mistake the optimizer can make, and nothing else in the integration stops it.

Everything here is inferred from sensors that already exist; no new hardware is
required. Three signals are used:

* the DHW or buffer tank warming while the compressor is not running,
* the tank warming faster than the compressor could possibly manage, which
  catches the case where the heat pump happens to be running too,
* an explicit user-provided entity (a flue thermostat, a stove switch), which
  overrides the inference entirely — anyone who has one will trust it more than
  a heuristic, and rightly so.

**The costs are asymmetric, so the detector is deliberately reluctant.**
Wrongly believing a fire is lit means skipping a cheap-hours charge and either
paying peak prices later or running out of hot water. Wrongly missing one costs
a single unnecessary charge. So activation needs several consecutive
confirmations, while release is quicker, and a decay window keeps the state from
flapping as a fire dies down.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime

from .const import (
    EXTERNAL_HEAT_FORECAST_MAX_HOURS,
    WATER_SPECIFIC_HEAT,
    WOOD_TANK_MIN_MARGIN,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class ExternalHeatConfig:
    """Tuning for the detector. Defaults are conservative on purpose."""

    enabled: bool = False
    #: Minimum rise, in °C/h, that counts as "something is heating this tank".
    #: Below this, sensor quantisation and thermosiphon drift dominate.
    min_rise_c_per_h: float = 1.5
    #: A rise this many times faster than the heat pump could deliver is
    #: evidence even while the pump is running.
    capacity_margin: float = 1.6
    #: Consecutive confirming samples before the state turns on. Two intervals
    #: of agreement rules out a single defrost cycle or a sensor spike.
    confirm_samples: int = 2
    #: Consecutive non-confirming samples before it turns off.
    release_samples: int = 2
    #: After release, how long the state keeps fading rather than clearing.
    #: A fire dies down gradually, and re-planning a full charge the instant
    #: the flames drop is exactly the wrong move.
    decay_minutes: float = 90.0
    #: Below this the compressor counts as off.
    idle_power_kw: float = 0.2
    #: Samples further apart than this say nothing about a rate of change.
    #: Sized from the update interval by the caller: with a fixed 1.0 h window
    #: and a 60-minute interval, every sample pair was rejected and the
    #: detector was permanently blind while appearing configured.
    max_sample_hours: float = 1.0
    min_sample_hours: float = 0.05
    #: Volume of the wood-side tank, liters, for bounding how much free heat
    #: a fire can still back (item 28).
    wood_tank_volume_l: float = 500.0


@dataclass
class ExternalHeatObservation:
    """One sampling of the quantities the detector reasons over."""

    now: datetime
    dhw_temp: float | None = None
    buffer_temp: float | None = None
    #: What the optimizer asked the pump to draw, kW electrical.
    commanded_power_kw: float = 0.0
    #: What the pump actually drew, kW electrical, when a meter exists.
    measured_power_kw: float | None = None
    #: Fastest rise the heat pump itself could produce in each tank, °C/h.
    dhw_max_rise_c_per_h: float | None = None
    buffer_max_rise_c_per_h: float | None = None
    #: An explicit user entity: ``True``/``False`` when one is configured.
    override: bool | None = None
    #: Wood-furnace topology sensors (item 28), each ``None`` when the entity
    #: is unconfigured or its reading is stale — a stalled hot sensor would
    #: look like an indefinite free fire, so staleness maps to absence.
    outlet_temp: float | None = None
    wood_top: float | None = None
    wood_bottom: float | None = None
    #: The heat-pump tank temperature, the cold side of the mix.
    hp_tank_temp: float | None = None
    #: Current space-heating demand, kW thermal, for scaling the displacement
    #: into an absolute free-heat figure.
    space_demand_kw: float | None = None


@dataclass
class ExternalHeatState:
    """What the detector currently believes, and why."""

    active: bool = False
    #: Between 0 and 1. Full while confirmed, decaying after release.
    confidence: float = 0.0
    fading: bool = False
    source: str = "none"
    evidence: list[str] = field(default_factory=list)
    since: datetime | None = None
    last_active: datetime | None = None
    #: Observed rise rates, published so a user can check the reasoning.
    dhw_rise_c_per_h: float | None = None
    buffer_rise_c_per_h: float | None = None
    #: How much of the space-heating load the furnace currently covers, 0-1.
    #: A separate field from ``confidence`` on purpose: confidence means "how
    #: recently", this means "how much", and the two must not be conflated.
    displacement: float = 0.0
    #: The displacement scaled to kW thermal, when demand is known.
    free_heat_kw: float = 0.0
    #: Sensible energy left in the wood tank above the useful floor, kWh.
    #: ``None`` when the tank pair is not sensed.
    wood_energy_kwh: float | None = None

    def as_dict(self) -> dict:
        return {
            "active": self.active,
            "confidence": round(self.confidence, 2),
            "fading": self.fading,
            "source": self.source,
            "evidence": list(self.evidence),
            "since": self.since.isoformat() if self.since else None,
            "dhw_rise_c_per_h": (
                round(self.dhw_rise_c_per_h, 2)
                if self.dhw_rise_c_per_h is not None
                else None
            ),
            "buffer_rise_c_per_h": (
                round(self.buffer_rise_c_per_h, 2)
                if self.buffer_rise_c_per_h is not None
                else None
            ),
        } | self._displacement_dict()

    def _displacement_dict(self) -> dict:
        """The item-28 fields, present only when the topology produces them.

        Conditional so that a configuration without the wood-furnace sensors
        publishes exactly the dictionary it always did — the golden captures
        of the coordinator's data hold every existing install to that.
        """
        out: dict = {}
        if self.displacement > 0.0 or self.free_heat_kw > 0.0:
            out["displacement"] = round(self.displacement, 2)
            out["free_heat_kw"] = round(self.free_heat_kw, 2)
        if self.wood_energy_kwh is not None:
            out["wood_energy_kwh"] = round(self.wood_energy_kwh, 1)
        return out


class ExternalHeatDetector:
    """Hysteretic detector with a decay tail."""

    def __init__(self, config: ExternalHeatConfig | None = None) -> None:
        self.config = config or ExternalHeatConfig()
        self.state = ExternalHeatState()
        self._confirmations = 0
        self._releases = 0
        self._prev_dhw: tuple[datetime, float] | None = None
        self._prev_buffer: tuple[datetime, float] | None = None

    # -- helpers ------------------------------------------------------------

    def _rate(
        self,
        previous: tuple[datetime, float] | None,
        now: datetime,
        value: float | None,
    ) -> tuple[float | None, tuple[datetime, float] | None]:
        """Rise rate in °C/h, and the sample to remember for next time."""
        if value is None:
            return None, previous
        sample = (now, float(value))
        if previous is None:
            return None, sample
        dt_h = (now - previous[0]).total_seconds() / 3600.0
        cfg = self.config
        if dt_h < cfg.min_sample_hours or dt_h > cfg.max_sample_hours:
            return None, sample
        return (float(value) - previous[1]) / dt_h, sample

    def _pump_idle(self, obs: ExternalHeatObservation) -> bool:
        """Whether the compressor is off.

        The measured draw is used when available precisely because the
        commanded value is the assumption that breaks here: a heat pump running
        on its own internal logic, or a plan that has already been overridden,
        makes "commanded" say nothing about reality.
        """
        if obs.measured_power_kw is not None:
            return obs.measured_power_kw <= self.config.idle_power_kw
        return obs.commanded_power_kw <= self.config.idle_power_kw

    # -- main entry point ---------------------------------------------------

    def update(self, obs: ExternalHeatObservation) -> ExternalHeatState:
        """Fold one observation in and return the resulting state."""
        state = self._update_activation(obs)
        self._update_displacement(obs)
        return state

    def _update_activation(
        self, obs: ExternalHeatObservation
    ) -> ExternalHeatState:
        """The boolean question: is something else heating the tanks?"""
        cfg = self.config
        state = self.state

        dhw_rate, self._prev_dhw = self._rate(
            self._prev_dhw, obs.now, obs.dhw_temp
        )
        buffer_rate, self._prev_buffer = self._rate(
            self._prev_buffer, obs.now, obs.buffer_temp
        )
        state.dhw_rise_c_per_h = dhw_rate
        state.buffer_rise_c_per_h = buffer_rate

        if not cfg.enabled:
            self._reset()
            return self.state

        # An explicit entity is authoritative and skips the hysteresis: the
        # user's own sensor is not a guess that needs corroborating.
        if obs.override is not None:
            if obs.override:
                self._activate(obs.now, "entity", ["user entity reports active"])
            else:
                self._deactivate(obs.now, source="entity")
            return self.state

        evidence = self._collect_evidence(obs, dhw_rate, buffer_rate)

        if evidence:
            self._confirmations += 1
            self._releases = 0
            if self._confirmations >= cfg.confirm_samples or state.active:
                self._activate(obs.now, "inferred", evidence)
                return self.state
            # Not yet confirmed: report the partial evidence without acting on
            # it, so a user can see the detector thinking.
            state.evidence = evidence
            state.source = "pending"
            return self.state

        self._releases += 1
        self._confirmations = 0
        if state.active and self._releases >= cfg.release_samples:
            self._deactivate(obs.now, source="inferred")
        elif not state.active:
            self._decay(obs.now)
        return self.state

    def _collect_evidence(
        self,
        obs: ExternalHeatObservation,
        dhw_rate: float | None,
        buffer_rate: float | None,
    ) -> list[str]:
        cfg = self.config
        evidence: list[str] = []
        idle = self._pump_idle(obs)

        for name, rate, ceiling in (
            ("DHW tank", dhw_rate, obs.dhw_max_rise_c_per_h),
            ("buffer tank", buffer_rate, obs.buffer_max_rise_c_per_h),
        ):
            if rate is None or rate < cfg.min_rise_c_per_h:
                continue
            if idle:
                evidence.append(
                    f"{name} rising {rate:.1f} °C/h with the compressor off"
                )
                continue
            if ceiling is not None and ceiling > 0:
                if rate > ceiling * cfg.capacity_margin:
                    evidence.append(
                        f"{name} rising {rate:.1f} °C/h, beyond the "
                        f"{ceiling:.1f} °C/h the heat pump can deliver"
                    )
        return evidence

    # -- displacement (item 28) --------------------------------------------

    def _update_displacement(self, obs: ExternalHeatObservation) -> None:
        """How much of the space load the furnace covers right now.

        The valve outlet is the only sensor that measures what the house
        actually receives; with the two tank temperatures either side of the
        mix it identifies the mixing fraction directly:
        ``f = (T_outlet − T_hp) / (T_wood − T_hp)``.

        Deliberately reluctant, like everything else here: the displacement
        is zero unless a fire is active or fading (lighting one is human
        behaviour and is never predicted), zero when any needed sensor is
        missing or stale, zero when the wood side is too close to the pump
        side to identify the mix, and zero once the measured wood tank can no
        longer back it.
        """
        state = self.state

        # Sensible energy left in the wood tank, when the pair is sensed.
        # The useful floor is the pump-tank side: below that the valve has
        # no reason to prefer wood water. Published even while no fire is
        # active, because "how much is left from the last one" is exactly
        # what a user checks before deciding whether to light another.
        state.wood_energy_kwh = None
        if obs.wood_top is not None and obs.hp_tank_temp is not None:
            useful_floor = obs.hp_tank_temp + WOOD_TANK_MIN_MARGIN
            if obs.wood_bottom is not None:
                mean_temp = (obs.wood_top + obs.wood_bottom) / 2.0
            else:
                # A single top probe over-reads a stratified tank; assume a
                # modestly colder bulk rather than believing the top.
                mean_temp = obs.wood_top - 5.0
            state.wood_energy_kwh = (
                max(0.0, mean_temp - useful_floor)
                * self.config.wood_tank_volume_l
                * WATER_SPECIFIC_HEAT
            )

        state.displacement = 0.0
        state.free_heat_kw = 0.0
        if not (state.active or state.fading):
            return
        if (
            obs.outlet_temp is None
            or obs.hp_tank_temp is None
            or obs.wood_top is None
        ):
            return
        denom = obs.wood_top - obs.hp_tank_temp
        if denom < WOOD_TANK_MIN_MARGIN:
            return
        if state.wood_energy_kwh is not None and state.wood_energy_kwh <= 0.0:
            return
        fraction = (obs.outlet_temp - obs.hp_tank_temp) / denom
        state.displacement = min(1.0, max(0.0, fraction))
        if obs.space_demand_kw is not None:
            state.free_heat_kw = state.displacement * max(
                0.0, obs.space_demand_kw
            )

    def forecast_free_heat(self, n_steps: int, dt_hours: float) -> list[float]:
        """Per-step free-heat forecast for the optimizer, kW.

        Three independent bounds, each of which alone can zero it, because
        the failure is asymmetric — a wrongly promised burn is a cold house
        in winter, hours long:

        * a hard horizon of ``EXTERNAL_HEAT_FORECAST_MAX_HOURS``, whatever
          the detector's own decay says (the DHW suppression's pattern);
        * a linear fade to zero across that horizon, so the tail never
          carries full weight;
        * when the wood tank pair is sensed, the cumulative promise never
          exceeds the energy the tank measurably holds.
        """
        out = [0.0] * n_steps
        rate = self.state.free_heat_kw
        if rate <= 0.0 or n_steps <= 0 or dt_hours <= 0.0:
            return out
        horizon_steps = min(
            n_steps, int(EXTERNAL_HEAT_FORECAST_MAX_HOURS / dt_hours)
        )
        budget = (
            self.state.wood_energy_kwh
            if self.state.wood_energy_kwh is not None
            else float("inf")
        )
        for i in range(horizon_steps):
            fade = 1.0 - i / max(horizon_steps, 1)
            step_kw = rate * fade
            step_kwh = step_kw * dt_hours
            if step_kwh > budget:
                step_kw = max(0.0, budget / dt_hours)
                step_kwh = step_kw * dt_hours
            out[i] = step_kw
            budget -= step_kwh
            if budget <= 0.0:
                break
        return out

    # -- state transitions --------------------------------------------------

    def _activate(self, now: datetime, source: str, evidence: list[str]) -> None:
        state = self.state
        if not state.active:
            state.since = now
            _LOGGER.info(
                "External heat source detected (%s): %s", source, "; ".join(evidence)
            )
        state.active = True
        state.fading = False
        state.confidence = 1.0
        state.source = source
        state.evidence = evidence
        state.last_active = now

    def _deactivate(self, now: datetime, source: str) -> None:
        state = self.state
        if state.active:
            _LOGGER.info("External heat source no longer detected (%s)", source)
            state.last_active = now
        state.active = False
        state.source = source
        state.evidence = []
        state.since = None
        self._decay(now)

    def _decay(self, now: datetime) -> None:
        """Fade confidence after release rather than dropping it cleanly."""
        state = self.state
        cfg = self.config
        if state.last_active is None or cfg.decay_minutes <= 0:
            state.confidence = 0.0
            state.fading = False
            return
        elapsed = (now - state.last_active).total_seconds() / 60.0
        remaining = max(0.0, 1.0 - elapsed / cfg.decay_minutes)
        state.confidence = remaining
        state.fading = remaining > 0.0

    def _reset(self) -> None:
        self.state.active = False
        self.state.confidence = 0.0
        self.state.fading = False
        self.state.source = "disabled"
        self.state.evidence = []
        self.state.since = None
        self.state.displacement = 0.0
        self.state.free_heat_kw = 0.0
        self._confirmations = 0
        self._releases = 0

    # -- consumers ----------------------------------------------------------

    @property
    def suppressing(self) -> bool:
        """Whether the optimizer should hold off on electric heating.

        True while active and for the whole decay window afterwards. Coming
        back immediately when the fire dies would re-plan a full charge at
        whatever the price happens to be, which is the behaviour the decay
        exists to prevent.
        """
        return self.state.active or self.state.fading
