"""Inverter frequency: observe first, actuate only when told to (T7 #61).

Most heat pumps modulate on a compressor frequency the house never sees.
When a Modbus or ESPHome integration exposes that frequency as a ``number``
entity, two stages become possible, and the order is the whole design:

* **Observe** (the default whenever the entity is configured): learn a
  kW-per-Hz map — the envelope pattern again, per-decile buckets of the
  entity's own range — and publish what frequency the current plan's power
  WOULD ask for. No actuation of any kind. The map is evidence for the
  user's go/no-go, not a controller.
* **Control** (explicit opt-in, per install): write the recommendation via
  ``number.set_value``, rate-limited, clamped to the entity's own min/max,
  and watched — a reported frequency that diverges from the commanded one
  for three consecutive ticks means the hardware is not actually listening
  (wrong register, a pump in a protective mode, a write path that silently
  drops), and the only safe answer is to stand down to observe and say so.

The map deliberately does NOT feed the optimizer: applying a part-load COP
factor in observe mode would change plans with no actuation to realise
them, and even in control mode the plan stays power-denominated — control
only translates the plan's commanded kW into the Hz that delivers it.

Kept free of Home Assistant imports so it can be unit-tested directly.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

#: The two stages. Anything unrecognised in config reads as observe.
FREQ_MODE_OBSERVE = "observe"
FREQ_MODE_CONTROL = "control"

#: Buckets across the entity's own [min, max] range.
FREQ_DECILES = 10
#: Weeks-scale EWMA once a bucket is seeded; plain mean before that.
FREQ_EWMA_ALPHA = 0.1
FREQ_MIN_SAMPLES = 5
#: Reported vs commanded divergence that counts as a strike, Hz.
FREQ_DIVERGENCE_HZ = 5.0
#: Consecutive strikes before control stands down to observe.
FREQ_WATCHDOG_TICKS = 3
#: At most one write per this many seconds (1 per 5 minutes).
FREQ_WRITE_MIN_INTERVAL_S = 300.0
#: Re-writing the same value is noise on the wire.
FREQ_WRITE_EPSILON_HZ = 1.0


@dataclass
class FrequencyMap:
    """kW per Hz over frequency deciles — the envelope pattern again.

    ``buckets[decile] = [kw_per_hz_ewma, count]``. Ratios rather than
    absolute kW so a bucket's answer scales with the frequency asked
    about. Buckets are keyed by decile INDEX of whatever range was in
    force when the sample folded — reconfiguring the entity's min/max
    re-labels old ratios onto different frequencies, so the map after a
    range change is approximately right at best and re-learns within
    days (slow EWMA, mean-until-N). A per-decile ratio also carries a
    small within-bucket bias (samples at a bucket's edge are priced at
    its mid), bounded by one decile's width and self-correcting under
    control's own feedback.
    """

    buckets: dict[int, list] = field(default_factory=dict)

    def observe(
        self, hz: float, kw: float, hz_min: float, hz_max: float
    ) -> None:
        """Fold one (frequency, electrical kW) reading into its bucket."""
        span = float(hz_max) - float(hz_min)
        if span <= 0 or not np.isfinite(hz) or not np.isfinite(kw):
            return
        # A stopped compressor teaches nothing about kW per Hz, and a
        # reading outside the entity's own range is a wiring problem.
        if hz < max(1.0, float(hz_min)) or hz > float(hz_max) * 1.05:
            return
        if kw <= 0.05:
            return
        decile = int(np.clip((hz - hz_min) / span * FREQ_DECILES, 0, FREQ_DECILES - 1))
        ratio = float(kw) / float(hz)
        entry = self.buckets.setdefault(decile, [ratio, 0])
        count = int(entry[1])
        if count < FREQ_MIN_SAMPLES:
            # Plain mean while young — the COP baseline's own lesson: an
            # EWMA seeded from a single outlier distorts the bucket for
            # its first dozens of folds.
            entry[0] = (float(entry[0]) * count + ratio) / (count + 1)
        else:
            entry[0] = (
                (1.0 - FREQ_EWMA_ALPHA) * float(entry[0])
                + FREQ_EWMA_ALPHA * ratio
            )
        entry[1] = count + 1

    def _evidenced(self, hz_min: float, hz_max: float) -> list[tuple[float, float]]:
        """(mid_hz, predicted_kw) per bucket with enough samples, ascending."""
        span = float(hz_max) - float(hz_min)
        if span <= 0:
            return []
        out = []
        for decile, entry in sorted(self.buckets.items()):
            if int(entry[1]) < FREQ_MIN_SAMPLES:
                continue
            mid = float(hz_min) + (decile + 0.5) * span / FREQ_DECILES
            out.append((mid, float(entry[0]) * mid))
        return out

    def recommend(
        self, target_kw: float, hz_min: float, hz_max: float
    ) -> float | None:
        """The lowest evidenced frequency that delivers the target power.

        Lowest on purpose — an inverter runs most efficiently slow. Above
        every evidenced bucket's reach the answer is the highest evidenced
        frequency (run flat out); with no evidence, or nothing to deliver,
        there is no answer, and None must never be turned into a write.
        """
        if not np.isfinite(target_kw) or target_kw <= 0.05:
            return None
        candidates = self._evidenced(hz_min, hz_max)
        if not candidates:
            return None
        for mid, predicted in candidates:
            if predicted >= target_kw:
                return round(mid, 1)
        # Above every evidenced bucket's reach: TRUE flat out — the
        # entity's own maximum, not the highest evidenced mid. This both
        # delivers what can be delivered and generates the high-frequency
        # evidence the map is missing; answering from evidence alone would
        # be the #17 ratchet again — control only revisits frequencies it
        # already knows, so no higher decile could ever earn its samples
        # and capacity would freeze at whatever observation happened to see.
        return round(float(hz_max), 1)

    def evidence_exhausted(
        self, target_kw: float, hz_min: float, hz_max: float
    ) -> bool:
        """True when the target exceeds every evidenced bucket's reach.

        Published so "running flat out on faith" is visible: the flat-out
        answer above is deliberate, but the user watching the advisor
        deserves to know when the map is extrapolating rather than
        answering from evidence.
        """
        if not np.isfinite(target_kw) or target_kw <= 0.05:
            return False
        candidates = self._evidenced(hz_min, hz_max)
        return bool(candidates) and all(
            predicted < target_kw for _, predicted in candidates
        )

    def summary(self, hz_min: float, hz_max: float) -> dict:
        """The map as published: per-bucket mid-Hz, ratio and count."""
        span = float(hz_max) - float(hz_min)
        out = {}
        for decile, entry in sorted(self.buckets.items()):
            mid = (
                float(hz_min) + (decile + 0.5) * span / FREQ_DECILES
                if span > 0
                else 0.0
            )
            out[str(decile)] = {
                "mid_hz": round(mid, 1),
                "kw_per_hz": round(float(entry[0]), 4),
                "samples": int(entry[1]),
            }
        return out

    # -- persistence --------------------------------------------------------

    def as_dict(self) -> dict:
        return {
            str(decile): [round(float(entry[0]), 5), int(entry[1])]
            for decile, entry in self.buckets.items()
        }

    @classmethod
    def from_dict(cls, data: dict | None) -> "FrequencyMap":
        fmap = cls()
        if not isinstance(data, dict):
            return fmap
        for key, entry in data.items():
            try:
                ratio = float(entry[0])
                count = int(entry[1])
            except (TypeError, ValueError, OverflowError, IndexError, KeyError):
                continue
            if not np.isfinite(ratio) or ratio <= 0 or count < 0:
                continue
            try:
                fmap.buckets[int(key)] = [ratio, count]
            except (TypeError, ValueError, OverflowError):
                continue
        return fmap


@dataclass
class FrequencyWatchdog:
    """Reported-vs-commanded divergence counter for the control stage.

    Three CONSECUTIVE divergent ticks trip it; a single convergent report
    clears the streak — transient lag during a ramp must not stand the
    controller down. The tick right after a new command is a grace tick
    (the register may not have ramped or re-polled yet), and ticks where
    the plan is not actually asking for the compressor are no evidence at
    all: an idle pump reading 0 Hz, or one pausing for a defrost, is an
    operating point at rest, not a write path that stopped listening.
    """

    commanded: float | None = None
    strikes: int = 0
    tripped: bool = False
    grace: bool = False

    def note_command(self, hz: float) -> None:
        self.commanded = float(hz)
        self.grace = True

    def note_report(self, reported: float | None, active: bool = True) -> bool:
        """Fold one reported frequency; True when this tick trips it.

        ``active`` is the caller's judgement that the divergence question
        is even meaningful this tick — the plan is asking for power AND
        the reading is in the compressor's running range. Inactive ticks
        clear the streak rather than pausing it: strikes must be
        CONSECUTIVE evidence, and an idle gap breaks consecutiveness.
        """
        if self.tripped or self.commanded is None:
            return False
        if not active:
            self.strikes = 0
            return False
        if reported is None or not np.isfinite(reported):
            # No reading is not divergence evidence; it is a stale input,
            # and the staleness watchdog owns that story.
            return False
        if self.grace:
            # The first report after a command: the pump is entitled to
            # still be ramping (or the register to a stale poll).
            self.grace = False
            return False
        if abs(float(reported) - self.commanded) <= FREQ_DIVERGENCE_HZ:
            self.strikes = 0
            return False
        self.strikes += 1
        if self.strikes >= FREQ_WATCHDOG_TICKS:
            self.tripped = True
            return True
        return False

    def reset(self) -> None:
        self.commanded = None
        self.strikes = 0
        self.tripped = False
        self.grace = False
