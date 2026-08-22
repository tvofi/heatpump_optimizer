"""Learn ``comfort_weight`` from what the user actually does.

``comfort_weight`` sets the exchange rate between money and degrees in the
objective. It is the most consequential number in the configuration and the
least knowable: it has no intuitive units, and nobody can reason about what 5.0
means.

But users reveal the answer constantly. Every manual override is the user
saying the plan went too far in one direction:

* overriding *upward* during an expensive coast means comfort was worth more
  than the plan assumed — ``comfort_weight`` is too low;
* never overriding while paying for a very flat temperature profile suggests it
  is too high, and money is being spent on comfort nobody asked for.

This deletes the hardest configuration question in the integration and replaces
it with something users already do without being asked.

**Overrides are noisy.** A party, an illness, an open window — plenty of them
have nothing to do with the plan. So evidence has to be consistent before the
value moves, the step is small, and the accumulated evidence decays so that a
year-old preference does not pin the model. The learned value is published and
resettable, because an invisible self-adjusting objective would be alarming.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np

_LOGGER = logging.getLogger(__name__)

# Bounds on the learned value. Outside these the optimizer either ignores price
# entirely or ignores comfort entirely, and neither is a preference anyone
# actually holds.
COMFORT_WEIGHT_MIN = 1.0
COMFORT_WEIGHT_MAX = 40.0

# How fast the value moves per unit of net evidence. Deliberately small: this
# is a preference, not a measurement, and a wrong step is felt directly.
LEARNING_RATE = 0.06
# Evidence below this magnitude is treated as noise and ignored.
EVIDENCE_THRESHOLD = 2.0
# Per-day decay, so old behaviour fades rather than accumulating forever.
EVIDENCE_HALF_LIFE_DAYS = 21.0
# An override smaller than this is a rounding artefact, not an opinion.
MIN_OVERRIDE_DELTA = 0.3
# Below this fraction of the comfort band, a "flat profile" is not evidence of
# over-weighting; the house may simply have had no opportunity to coast.
FLAT_PROFILE_BAND_FRACTION = 0.25


@dataclass
class OverrideEvent:
    """One recorded manual setpoint override, with the context that explains it."""

    when: datetime
    #: Positive when the user asked for more heat than the plan wanted.
    delta_c: float
    indoor_temp: float
    #: What the plan's setpoint was at that moment.
    planned_setpoint: float
    #: Price at the time, relative to the horizon mean. Above 1 means the plan
    #: was coasting through an expensive period, which is the informative case.
    relative_price: float = 1.0

    def evidence(self) -> float:
        """Signed evidence contribution.

        Weighted by relative price because an override during a *cheap* hour
        says almost nothing: the plan should have been heating anyway, so the
        override is more likely about something else entirely.
        """
        if abs(self.delta_c) < MIN_OVERRIDE_DELTA:
            return 0.0
        weight = float(np.clip(self.relative_price, 0.5, 2.5))
        return float(np.sign(self.delta_c)) * min(abs(self.delta_c), 3.0) * weight


@dataclass
class ComfortLearner:
    """Accumulates override evidence and nudges ``comfort_weight``."""

    configured_weight: float = 5.0
    learned_weight: float = 5.0
    evidence: float = 0.0
    overrides: int = 0
    last_update: datetime | None = None
    history: list[dict] = field(default_factory=list)

    # -- evidence -----------------------------------------------------------

    def _decay(self, now: datetime) -> None:
        if self.last_update is None:
            self.last_update = now
            return
        days = (now - self.last_update).total_seconds() / 86400.0
        if days <= 0:
            return
        self.evidence *= 0.5 ** (days / EVIDENCE_HALF_LIFE_DAYS)
        self.last_update = now

    def record_override(self, event: OverrideEvent) -> None:
        """Fold a manual override into the accumulated evidence."""
        self._decay(event.when)
        contribution = event.evidence()
        if contribution == 0.0:
            return
        self.evidence += contribution
        self.overrides += 1
        self.history.append(
            {
                "t": event.when.isoformat(),
                "delta_c": round(event.delta_c, 2),
                "indoor_temp": round(event.indoor_temp, 2),
                "planned_setpoint": round(event.planned_setpoint, 2),
                "relative_price": round(event.relative_price, 2),
            }
        )
        del self.history[:-40]
        self._maybe_adjust(event.when)

    def record_quiet_period(
        self,
        now: datetime,
        temperature_span: float,
        comfort_band: float,
        days: float = 1.0,
    ) -> None:
        """Note a stretch with no overrides and a very flat temperature.

        This is the other half of the signal, and it is the half that lets the
        weight come *down*. Without it the learner could only ever ratchet
        upward, since only discomfort produces an override.
        """
        if comfort_band <= 0 or days <= 0:
            return
        if temperature_span > comfort_band * FLAT_PROFILE_BAND_FRACTION:
            return
        self._decay(now)
        # Weak negative evidence: paying to hold a flat profile that nobody
        # ever complained about suggests comfort is over-weighted. Kept much
        # smaller than an override so a fortnight of quiet cannot outweigh a
        # single clear complaint.
        self.evidence -= 0.35 * min(days, 7.0)
        self._maybe_adjust(now)

    # -- adjustment ---------------------------------------------------------

    def _maybe_adjust(self, now: datetime) -> None:
        if abs(self.evidence) < EVIDENCE_THRESHOLD:
            return
        direction = float(np.sign(self.evidence))
        step = LEARNING_RATE * min(abs(self.evidence), 6.0)
        updated = self.learned_weight * (1.0 + direction * step)
        self.learned_weight = float(
            np.clip(updated, COMFORT_WEIGHT_MIN, COMFORT_WEIGHT_MAX)
        )
        # Consume the evidence that produced the move, so the same complaints
        # cannot be spent twice.
        self.evidence -= direction * EVIDENCE_THRESHOLD
        self.last_update = now
        _LOGGER.info(
            "Adjusted learned comfort weight to %.2f (configured %.2f) from "
            "%d recorded overrides",
            self.learned_weight,
            self.configured_weight,
            self.overrides,
        )

    def reset(self) -> None:
        """Return to the configured value and forget the evidence."""
        self.learned_weight = self.configured_weight
        self.evidence = 0.0
        self.overrides = 0
        self.history = []

    def set_configured(self, weight: float) -> None:
        """A new configured value supersedes anything learned against the old."""
        if abs(weight - self.configured_weight) < 1e-9:
            return
        self.configured_weight = float(weight)
        self.reset()

    # -- reporting / persistence -------------------------------------------

    @property
    def effective_weight(self) -> float:
        return float(
            np.clip(self.learned_weight, COMFORT_WEIGHT_MIN, COMFORT_WEIGHT_MAX)
        )

    def summary(self) -> dict:
        return {
            "configured": round(self.configured_weight, 2),
            "learned": round(self.learned_weight, 2),
            "evidence": round(self.evidence, 2),
            "overrides": self.overrides,
            "recent_overrides": self.history[-10:],
        }

    def as_dict(self) -> dict:
        return {
            "configured_weight": self.configured_weight,
            "learned_weight": self.learned_weight,
            "evidence": self.evidence,
            "overrides": self.overrides,
            "last_update": (
                self.last_update.isoformat() if self.last_update else None
            ),
            "history": self.history[-40:],
        }

    @classmethod
    def from_dict(cls, data: dict | None, configured_weight: float) -> "ComfortLearner":
        learner = cls(
            configured_weight=configured_weight, learned_weight=configured_weight
        )
        if not isinstance(data, dict):
            return learner
        stored_configured = data.get("configured_weight")
        try:
            stored_configured = float(stored_configured)
        except (TypeError, ValueError):
            stored_configured = None
        # If the user has since changed the configured weight, everything
        # learned against the old one is about a different question.
        if stored_configured is None or abs(stored_configured - configured_weight) > 1e-6:
            return learner
        try:
            learner.learned_weight = float(data.get("learned_weight", configured_weight))
            learner.evidence = float(data.get("evidence", 0.0))
            learner.overrides = int(data.get("overrides", 0))
        except (TypeError, ValueError):
            return cls(
                configured_weight=configured_weight, learned_weight=configured_weight
            )
        raw_time = data.get("last_update")
        if isinstance(raw_time, str):
            try:
                learner.last_update = datetime.fromisoformat(raw_time)
            except ValueError:
                learner.last_update = None
        history = data.get("history")
        if isinstance(history, list):
            learner.history = [h for h in history if isinstance(h, dict)][-40:]
        return learner
