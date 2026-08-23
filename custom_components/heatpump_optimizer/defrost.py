"""Learned capacity and efficiency derate in the frosting band.

The COP model is a clean monotonic function of outdoor temperature. Real
air-to-water units are not: between roughly 0 and +5 °C in humid air, frost
accumulates on the evaporator and the unit must periodically reverse to clear
it. Capacity and efficiency both fall, and the loss is largest exactly where
the Swedish shoulder season lives — and exactly where the optimizer is most
aggressive about coasting on stored heat.

The failure mode is quiet. Plans made in that band under-deliver, and the
shortfall surfaces as a comfort miss rather than as an obvious fault.

**The derate is learned, not tabulated.** A datasheet curve would be wrong for
most units, and the between-unit spread is larger than the effect being
modelled. What is learned is a multiplicative factor per (temperature,
humidity) bucket, from the same predicted-versus-actual signal the closed-loop
accuracy reporting collects. With no evidence, the factor is exactly 1.0 and
this module changes nothing.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

_LOGGER = logging.getLogger(__name__)

# Bucket edges in °C. The frosting band is resolved finely and everything
# outside it coarsely, because that is where the physics actually varies.
TEMP_EDGES: tuple[float, ...] = (-30.0, -5.0, 0.0, 2.0, 5.0, 8.0, 40.0)
# Humidity split. Frost needs moisture; dry cold air barely frosts at all.
HUMIDITY_EDGES: tuple[float, ...] = (0.0, 70.0, 101.0)

# The band whose under-delivery is attributed to frost. Two learners watch the
# same commanded-versus-measured signal — the global COP scale and this derate —
# and if both fold in the same interval, one shortfall is corrected twice and
# plans in the band overshoot the compensation. So the attribution is disjoint:
# inside the band the shortfall belongs to frost and only this module learns
# from it; outside, frost is physically implausible and only the COP scale does.
FROST_BAND_MIN_C = 0.0
FROST_BAND_MAX_C = 5.0


def in_frost_band(outdoor_temp: float) -> bool:
    """Whether under-delivery at this outdoor temperature reads as frost."""
    return FROST_BAND_MIN_C <= float(outdoor_temp) < FROST_BAND_MAX_C

# Derate is bounded. A unit that appears to deliver less than half or more than
# its rated output is telling us about a broken sensor, not about frost.
DERATE_MIN = 0.55
DERATE_MAX = 1.05
# Slow, because each sample is a single noisy interval.
DERATE_ALPHA = 0.05
# Until a bucket has this many samples the derate is blended towards 1.0, so a
# first observation cannot swing a plan.
DERATE_CONFIDENCE_SAMPLES = 12


def _bucket_index(value: float, edges: tuple[float, ...]) -> int:
    for i in range(len(edges) - 1):
        if edges[i] <= value < edges[i + 1]:
            return i
    return len(edges) - 2 if value >= edges[-1] else 0


@dataclass
class DefrostDerate:
    """Per-bucket multiplicative COP/capacity derate, learned online."""

    #: ``factors[temp_bucket][humidity_bucket]``
    factors: list[list[float]] = field(
        default_factory=lambda: [
            [1.0 for _ in range(len(HUMIDITY_EDGES) - 1)]
            for _ in range(len(TEMP_EDGES) - 1)
        ]
    )
    counts: list[list[int]] = field(
        default_factory=lambda: [
            [0 for _ in range(len(HUMIDITY_EDGES) - 1)]
            for _ in range(len(TEMP_EDGES) - 1)
        ]
    )

    # -- lookup -------------------------------------------------------------

    def factor(self, outdoor_temp: float, humidity: float | None = None) -> float:
        """Derate for these conditions, blended towards 1.0 while uncertain."""
        t = _bucket_index(float(outdoor_temp), TEMP_EDGES)
        h = _bucket_index(
            float(humidity) if humidity is not None else 60.0, HUMIDITY_EDGES
        )
        raw = self.factors[t][h]
        n = self.counts[t][h]
        if n <= 0:
            return 1.0
        # Linear ramp of trust. A derate the size of the effect being measured
        # should not be applied on the strength of one observation.
        trust = min(1.0, n / DERATE_CONFIDENCE_SAMPLES)
        return 1.0 + (raw - 1.0) * trust

    def samples(self, outdoor_temp: float, humidity: float | None = None) -> int:
        t = _bucket_index(float(outdoor_temp), TEMP_EDGES)
        h = _bucket_index(
            float(humidity) if humidity is not None else 60.0, HUMIDITY_EDGES
        )
        return self.counts[t][h]

    # -- learning -----------------------------------------------------------

    def observe(
        self,
        outdoor_temp: float,
        humidity: float | None,
        delivered_ratio: float,
    ) -> None:
        """Fold in one observation.

        ``delivered_ratio`` is realised thermal output over predicted thermal
        output for the interval: below 1.0 means the unit under-delivered.
        """
        if delivered_ratio <= 0 or delivered_ratio > 3.0:
            return
        t = _bucket_index(float(outdoor_temp), TEMP_EDGES)
        h = _bucket_index(
            float(humidity) if humidity is not None else 60.0, HUMIDITY_EDGES
        )
        target = min(max(float(delivered_ratio), DERATE_MIN), DERATE_MAX)
        current = self.factors[t][h]
        self.factors[t][h] = (1.0 - DERATE_ALPHA) * current + DERATE_ALPHA * target
        self.counts[t][h] += 1

    # -- persistence --------------------------------------------------------

    def as_dict(self) -> dict:
        return {"factors": self.factors, "counts": self.counts}

    @classmethod
    def from_dict(cls, data: dict | None) -> "DefrostDerate":
        instance = cls()
        if not isinstance(data, dict):
            return instance
        factors = data.get("factors")
        counts = data.get("counts")
        n_t = len(TEMP_EDGES) - 1
        n_h = len(HUMIDITY_EDGES) - 1
        if (
            isinstance(factors, list)
            and len(factors) == n_t
            and all(isinstance(row, list) and len(row) == n_h for row in factors)
        ):
            instance.factors = [[float(v) for v in row] for row in factors]
        if (
            isinstance(counts, list)
            and len(counts) == n_t
            and all(isinstance(row, list) and len(row) == n_h for row in counts)
        ):
            instance.counts = [[int(v) for v in row] for row in counts]
        return instance

    def summary(self) -> list[dict]:
        """Human-readable view for the diagnostics attributes."""
        out = []
        for t in range(len(TEMP_EDGES) - 1):
            for h in range(len(HUMIDITY_EDGES) - 1):
                if self.counts[t][h] <= 0:
                    continue
                out.append(
                    {
                        "outdoor_range": [TEMP_EDGES[t], TEMP_EDGES[t + 1]],
                        "humidity_range": [
                            HUMIDITY_EDGES[h],
                            HUMIDITY_EDGES[h + 1],
                        ],
                        "derate": round(self.factors[t][h], 3),
                        "samples": self.counts[t][h],
                    }
                )
        return out

    @property
    def total_samples(self) -> int:
        return sum(sum(row) for row in self.counts)
