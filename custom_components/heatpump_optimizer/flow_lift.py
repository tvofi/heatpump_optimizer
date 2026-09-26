"""How far the real supply water sits from the model's own curve (#1067).

``ThermalModel.compute_cop`` has always taken a ``flow_temp``, and the only
value ever passed to it is the buffer tank's temperature, gated on
``cop_flow_carnot`` -- which is on only while a mixing valve throttles. On a
direct plant, a monoblock feeding the emitters with no buffer and no valve,
that term is therefore never applied at all. The efficiency learner then
attributes the entire commanded-versus-measured ratio to ``cop_scale``
whatever lift the machine was actually working at, so the one multiplier every
plan's cost runs through walks with the weather: cold weather asks the curve
for hotter water, the machine returns a lower COP for a physical reason the
model was not told about, and ``cop_scale`` absorbs it as if the pump had
degraded.

What this module measures is the difference between the two things that can be
known: the supply temperature the plant actually ran at, and the supply
temperature this model's OWN weather-compensation curve implies for the same
outdoor temperature. Their difference is a bias in kelvin -- an installer
offset, a curve set steeper or flatter than the model's, a fixed-setpoint
plant that ignores weather altogether -- and it is exactly what has to be known
before a lift can be applied to a horizon.

Deliberately not a controller and deliberately not priced. This half of #1067
learns the bias and reports it; applying it to what the solver prices is
W1067-G3's, behind its own flag. The two halves must agree about what "the
curve" is, which is why :func:`curve_supply_temp` exists and is the only place
in the integration that answers that question.

Kept free of Home Assistant imports so it can be unit-tested directly, like
``freq_control`` and ``pump_signals``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .const import (
    CONF_HEAT_PUMP_RETURN_TEMP_ENTITY,
    CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY,
)

#: Weeks-scale EWMA once the bias is seeded. The same alpha the kW-per-Hz map
#: uses, for the same reason: a curve offset is a property of the
#: installation, so a single odd interval must not move it far.
FLOW_BIAS_ALPHA = 0.1
#: Plain mean until this many samples, then the EWMA. The COP baseline's
#: lesson, repeated in ``freq_control.FrequencyMap``: an EWMA seeded from one
#: outlier distorts its own estimate for dozens of folds afterwards.
FLOW_BIAS_MIN_SAMPLES = 5
#: How far BELOW the curve the bias may travel, in kelvin.
#:
#: A plant running under the model's curve is one whose emitters need less
#: than the model thinks; past 15 K under it the supply would be colder than
#: the room it heats, which is a probe in the wrong pipe rather than a curve.
#: The clamp bounds the ESTIMATE, not the sample.
FLOW_BIAS_CLAMP_K = 15.0
#: The hottest supply a direct heat-pump plant runs at, degC, and therefore
#: how far ABOVE the curve the bias may travel: up to this supply, measured
#: against the curve of the sample it was learned from (D2-s2-02).
#:
#: The upper bound used to be the same 15 K, argued against a curve asking
#: 35 C. The model's own curve (``curve_supply_temp``, an emitter UA backed
#: out of the nameplate at a 15 K design spread) asks 22-28 C of the default
#: houses, so a plant at 40/45/50 C sat 17-27 K above it, pinned the bias at
#: the clamp and was priced at a supply it never ran: COP overstated up to
#: 37 %. Sized against the supply itself, the bound holds every real plant,
#: and the readings no plant produces -- degF adopted raw, a flue or DHW
#: probe in the supply slot -- are refused as samples instead of absorbed.
FLOW_SUPPLY_MAX_C = 75.0


def read_water_temps(reader: Any) -> tuple[float | None, float | None]:
    """This cycle's (supply, return) water temperatures in degC, or ``None``.

    The sibling of ``pump_signals.read_electric_heat``, and read with the
    generic :meth:`~.inputs.InputReader.read` for the same reason every other
    plant temperature is: it applies the entity's own unit (#961, so a US
    instance reporting degF is converted rather than adopted at face value)
    and the horizon in ``INPUT_MAX_AGE_MINUTES``, and it records both slots in
    this cycle's ``InputHealth`` with their entity id and problem. A slot
    nobody can read is therefore visible in the diagnostics; it just does not
    act, which is ``pump_signals``' rule and applies here unchanged.
    """
    supply = reader.read(CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY)
    returned = reader.read(CONF_HEAT_PUMP_RETURN_TEMP_ENTITY)
    return (
        supply.value if supply.ok else None,
        returned.value if returned.ok else None,
    )


def curve_supply_temp(
    model: Any, outdoor_temp: float, indoor_target: float
) -> float | None:
    """The supply temperature this model's weather curve implies, in degC.

    THE one answer to "what is the curve", for both halves of #1067. The bias
    below is learned as a residual against whatever this returns, and W1067-G3
    must apply the lift against exactly the same curve -- a second expression
    of it, however faithful on the day it was written, is a bias learned
    against one curve and spent against another.

    It is ``ThermalModel.flow_target_for_indoor``, reused rather than
    re-derived: that is already the conversion ``_simulate_step_two_zone``
    bounds a dumb valve's delivery with, and it follows the learned heat-loss
    scale, so the curve tracks the house the model has learned rather than the
    one it was configured with.

    ``None`` for an unusable input rather than a number: a non-finite outdoor
    temperature must produce no sample, not a sample the clamp then absorbs.
    """
    if not np.isfinite(outdoor_temp) or not np.isfinite(indoor_target):
        return None
    curve = float(model.flow_target_for_indoor(indoor_target, outdoor_temp))
    return curve if np.isfinite(curve) else None


@dataclass
class FlowCurveBias:
    """The learned supply-vs-curve offset, and this cycle's two readings.

    Inert with zero evidence: ``bias_k`` is exactly 0.0 at zero samples, so an
    install that never maps the supply slot gets a bias that changes nothing,
    and every arithmetic downstream of it is the arithmetic that ran before
    this existed.

    The two readings ride here rather than on the coordinator because they are
    this feature's inputs and belong beside the thing they feed, and because
    holding them in one place is what lets the fold be a single module-level
    predicate. They are deliberately NOT persisted -- see :meth:`as_dict`.
    """

    #: Measured supply minus curve supply, kelvin, from
    #: -:data:`FLOW_BIAS_CLAMP_K` up to :data:`FLOW_SUPPLY_MAX_C` less the
    #: curve. Positive means the plant runs HOTTER than the model's curve
    #: asks for, which costs COP.
    bias_k: float = 0.0
    #: How many residuals have been folded. Zero is the inert state.
    samples: int = 0
    #: This cycle's supply reading in degC, or ``None`` when the slot is
    #: unconfigured, unreadable or past its horizon. ``None`` acts on nothing,
    #: exactly as an absent pump flag does (``pump_signals``).
    last_supply_c: float | None = None
    #: This cycle's return reading, same rules. Held for the diagnostics and
    #: for W1067-G3; nothing in this group's fold reads it, because the bias
    #: is a property of the SUPPLY side against the supply curve.
    last_return_c: float | None = None

    def observe_temps(
        self, supply: float | None, return_temp: float | None
    ) -> None:
        """Record this cycle's two readings, or clear them.

        Called every cycle, with ``None`` for a slot that was unconfigured,
        unavailable or stale. Clearing rather than keeping is the whole point:
        a supply temperature from forty minutes ago describes a different
        operating point, and "there is a fresh supply reading" is the gate the
        bias fold is taken on.
        """
        self.last_supply_c = (
            float(supply)
            if supply is not None and np.isfinite(supply)
            else None
        )
        self.last_return_c = (
            float(return_temp)
            if return_temp is not None and np.isfinite(return_temp)
            else None
        )

    def observe(self, measured_supply: float, curve_supply: float) -> None:
        """Fold one (measured, curve) pair into the bias."""
        if not np.isfinite(measured_supply) or not np.isfinite(curve_supply):
            return
        if measured_supply > FLOW_SUPPLY_MAX_C:
            return
        residual = float(measured_supply) - float(curve_supply)
        if self.samples < FLOW_BIAS_MIN_SAMPLES:
            blended = (self.bias_k * self.samples + residual) / (
                self.samples + 1
            )
        else:
            blended = (
                1.0 - FLOW_BIAS_ALPHA
            ) * self.bias_k + FLOW_BIAS_ALPHA * residual
        self.bias_k = float(
            np.clip(
                blended,
                -FLOW_BIAS_CLAMP_K,
                max(FLOW_SUPPLY_MAX_C - float(curve_supply), 0.0),
            )
        )
        self.samples += 1

    # -- persistence --------------------------------------------------------

    def as_dict(self) -> dict[str, Any]:
        """The learned state only.

        The two readings are absent on purpose. They are one cycle's
        measurement of water that has since cooled, and restoring one hours
        later would hand the bias fold a "fresh" supply temperature
        that is nothing of the kind -- the exact failure the horizons in
        ``INPUT_MAX_AGE_MINUTES`` exist to prevent.
        """
        return {
            "bias_k": round(float(self.bias_k), 4),
            "samples": int(self.samples),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "FlowCurveBias":
        """Parse a stored dict; anything unusable restores to inert."""
        learner = cls()
        if not isinstance(data, dict):
            return learner
        try:
            bias = float(data.get("bias_k", 0.0))
            samples = int(data.get("samples", 0))
        except (TypeError, ValueError, OverflowError):
            return learner
        if not np.isfinite(bias) or samples < 0:
            return learner
        # Zero samples is the inert state, whatever the stored bias says: a
        # bias with no evidence behind it is exactly 0.0 (the class
        # docstring's promise, and what W1067-G3 is told it may rely on).
        if samples == 0:
            return learner
        # Re-clamped on load rather than trusted: a store written by a build
        # with a wider clamp, or simply corrupt, must not reintroduce a bias
        # this version would never have learned. No heating curve asks for
        # water below 0 degC, so none learns a bias past the supply ceiling.
        learner.bias_k = float(
            np.clip(bias, -FLOW_BIAS_CLAMP_K, FLOW_SUPPLY_MAX_C)
        )
        learner.samples = samples
        return learner
