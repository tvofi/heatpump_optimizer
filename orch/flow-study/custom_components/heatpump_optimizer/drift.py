"""One CUSUM primitive for every drift detector in the program (v4.0.0 T4).

Three places need "this signal has been consistently off for a while":
the open-window detector (#26, °C residuals over minutes-to-hours), the
compressor-health watch (#12, relative COP shortfall over weeks) and the
snapshot insurance's bias test (#42, days). Each hand-rolls badly — a
threshold on a single sample false-alarms on noise, a plain mean forgets
the recent past. CUSUM is the standard answer: accumulate the evidence
beyond a per-sample allowance, trip on the accumulated total, and a noisy
but centred signal accumulates nothing.

The primitive is deliberately tiny and fully serialisable; the users
choose thresholds in their own units and own their consequences (freeze,
repair issue, rollback). Symmetry with ``external_heat.py``'s detector
pattern: evidence strings, explicit release, nothing actuates from here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone, tzinfo
from typing import Any

import numpy as np

#: The statistic is capped at this multiple of the threshold. Without a
#: cap, every sample of a long-lived condition keeps accumulating, and the
#: release lag grows with how long the condition lasted — an 8-hour open
#: window would freeze learning for two extra days after it closed.
STAT_CAP_FACTOR = 1.5
#: The tracked reference's prior variance per coefficient (per unit
#: residual variance, so the prior weighs as one sample: the first few
#: samples are a plain least-squares fit); forgetting may inflate each
#: variance back to it and no further -- without the cap, days with a
#: regressor held still wind its slope's variance up until a single
#: sample can swing it.
REFERENCE_PRIOR_COV = 1.0


def _as_utc(value: datetime) -> datetime:
    """Home Assistant's ``as_utc`` rule: naive is UTC, aware is converted."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def utc_elapsed_seconds(newer: datetime, older: datetime) -> float:
    """Seconds between two stamps as instants (round-9 D14-s4-01, P7).

    Two aware stamps that share Home Assistant's one ZoneInfo object subtract
    as wall clock in CPython, an hour off across a DST transition; converting
    both to UTC first measures the instants. A naive pair keeps its wall
    difference, which is what the identity-zone test clock means by it.
    """
    return (_as_utc(newer) - _as_utc(older)).total_seconds()


def utc_step_starts(
    start: datetime, n: int, step: timedelta, offset: int = 0
) -> list[datetime]:
    """The start of steps ``offset`` .. ``offset + n - 1``, walked in UTC.

    The one horizon clock: the optimizer's horizon, the coordinator's
    forecast and price grids, and the silent-mode schedule all read it
    (#1741), so no two of them can label one step differently. Adding a
    wall-clock step invents the spring DST gap and stretches the autumn
    overlap into a 75-minute step; walking the count in UTC keeps every label
    a real instant, converted back to ``start``'s zone. A naive ``start``
    keeps the wall-clock walk, so unzoned fixtures stay byte-identical.
    """
    tz = start.tzinfo
    if tz is None:
        return [start + step * (offset + i) for i in range(n)]
    base = start.astimezone(timezone.utc)
    return [(base + step * (offset + i)).astimezone(tz) for i in range(n)]


def stored_instant(
    raw: Any, naive_zone: tzinfo | None = timezone.utc
) -> datetime | None:
    """The stored-instant rule: a persisted instant loads aware, or not at all.

    Every consumer diffs a loaded instant against an aware ``now``, so a naive
    one raised ``TypeError`` on every cycle until something rewrote the leaf
    (round 9, D1-s1-01, D1-s3-01). A naive instant is read in ``naive_zone``:
    Home Assistant's configured zone where the loader can see it (the clock
    that reads the value back is in that zone, and a typed time is the user's
    wall clock), UTC in a pure loader that cannot (``Cusum``'s legacy rule).
    Anything that does not parse is ``None``. The zone is all this decides;
    how far ahead a stored instant may lie is the store boundary's.
    """
    if isinstance(raw, datetime):
        when = raw
    elif isinstance(raw, str) and raw.strip():
        try:
            when = datetime.fromisoformat(raw.strip())
        except ValueError:
            return None
    else:
        return None
    return when if when.tzinfo is not None else when.replace(tzinfo=naive_zone)


@dataclass
class Cusum:
    """A one-sided CUSUM with a drift allowance and hysteresis release.

    ``update`` folds one residual; the statistic accumulates
    ``side·residual − drift`` clipped at zero, trips at ``threshold`` and
    releases when it falls back under ``release`` (default: a quarter of
    the threshold, so a detector does not chatter at the trip line). With
    ``reference_hours`` set it folds the departure from the signal's own
    tracked level instead, for a signal whose zero is not its normal.
    """

    #: Accumulated evidence at which the detector trips.
    threshold: float
    #: Per-sample allowance: ordinary noise must accumulate nothing.
    drift: float
    #: +1 watches positive residuals, -1 negative.
    side: int = 1
    #: Release level; None means threshold / 4.
    release: float | None = None
    stat: float = 0.0
    tripped: bool = False
    #: Human-readable trail, newest last, capped.
    evidence: list[str] = field(default_factory=list)
    #: When the detector was last fed a residual. A tripped detector that
    #: stops being fed (the signal that drives it vanished) must not stay
    #: latched forever — see ``release_if_starved``.
    last_fed: datetime | None = None
    #: Per-sample cap on the departure folded, so no single glitch can trip
    #: the detector alone. None: no cap.
    clip: float | None = None
    #: Hours over which the reference tracks what the signal normally
    #: reads. None: the reference is zero, for a signal centred by
    #: construction. Set, the statistic folds the departure from
    #: ``level + sum(slope_i * regressor_i)``, fitted by least squares that
    #: forget over this time constant: a bias the signal carries for days
    #: -- one that also scales with a regressor -- accumulates nothing, and
    #: only a change does.
    reference_hours: float | None = None
    #: The tracked ``[level, *slopes]`` (None until the first sample seeds
    #: it) and its covariance, row-major.
    reference: list[float] | None = None
    reference_cov: list[float] | None = None

    def update(
        self, when: datetime, residual: float, regressors: tuple[float, ...] = ()
    ) -> bool:
        """Fold one residual in; True when ``tripped`` changed.

        ``regressors`` are what a bias of the signal may scale with; only a
        tracked reference reads them.
        """
        if not (np.isfinite(residual) and all(np.isfinite(x) for x in regressors)):
            return False
        departure = self._departure(when, float(residual), regressors)
        self.last_fed = when
        signed = departure * (1 if self.side >= 0 else -1)
        self.stat = min(
            max(0.0, self.stat + signed - self.drift),
            self.threshold * STAT_CAP_FACTOR,
        )
        release_at = (
            self.release if self.release is not None else self.threshold / 4.0
        )
        if not self.tripped and self.stat >= self.threshold:
            self.tripped = True
            self._note(
                when,
                f"accumulated {self.stat:.2f} over threshold "
                f"{self.threshold:.2f}; tripped",
            )
            return True
        if self.tripped and self.stat <= release_at:
            self.tripped = False
            self._note(when, f"decayed to {self.stat:.2f}; released")
            return True
        return False

    def _departure(
        self, when: datetime, value: float, regressors: tuple[float, ...]
    ) -> float:
        """``value`` less the reference, clipped; the reference then moves.

        The departure is taken against the reference BEFORE this sample
        moves it, so a change shows in full on the sample that carries it.
        The first sample (or the first after the regressors change in
        number) seeds the level, clipped, with no slopes; each later one is
        a recursive least-squares step on the clipped departure, forgetting
        over the elapsed time, so a glitch drags the fit no further than it
        may push the statistic.
        """
        if self.reference_hours is None:
            return self._clipped(value)
        u = np.array((1.0, *(float(x) for x in regressors)))
        k = u.size
        if (
            self.reference is None or self.reference_cov is None
            or len(self.reference) != k or len(self.reference_cov) != k * k
        ):
            self.reference = [self._clipped(value)] + [0.0] * (k - 1)
            self.reference_cov = (np.eye(k) * REFERENCE_PRIOR_COV).ravel().tolist()
            return 0.0
        theta = np.array(self.reference)
        cov = np.array(self.reference_cov).reshape(k, k)
        departure = self._clipped(value - float(theta @ u))
        gap_h = (
            max(0.0, utc_elapsed_seconds(when, self.last_fed) / 3600.0)
            if self.last_fed is not None
            else 0.0
        )
        # Forget, then hold each coefficient's variance at the prior's: a
        # regressor that sits still (no sun for weeks) inflates only its own
        # slope's, never the forgetting the others need. D P D, D diagonal,
        # stays positive definite.
        cov = cov * float(np.exp(gap_h / self.reference_hours))
        shrink = np.sqrt(np.minimum(1.0, REFERENCE_PRIOR_COV / np.diag(cov)))
        cov = cov * np.outer(shrink, shrink)
        cov_u = cov @ u
        gain = cov_u / (1.0 + float(u @ cov_u))
        theta = theta + gain * departure
        cov = cov - np.outer(gain, cov_u)
        self.reference = theta.tolist()
        self.reference_cov = ((cov + cov.T) / 2.0).ravel().tolist()
        return departure

    def _clipped(self, value: float) -> float:
        if self.clip is None:
            return value
        return min(max(value, -self.clip), self.clip)

    def release_if_starved(self, now: datetime, max_gap_hours: float) -> bool:
        """Force-release a tripped detector nothing has fed for too long.

        The feed path can dry up while the latch holds — the open-window
        detector is fed from heat-loss residuals, which stop entirely in
        mild weather (indoor−outdoor below the learning threshold). With
        no residuals the condition that tripped it can no longer be
        observed either way, and staying latched would freeze every
        learner indefinitely. Returns True when it released.
        """
        if not self.tripped:
            return False
        if self.last_fed is None:
            # Unknown feed history (a pre-cap payload): start the clock
            # now rather than releasing on a guess.
            self.last_fed = now
            return False
        if utc_elapsed_seconds(now, self.last_fed) < max_gap_hours * 3600.0:
            return False
        self.tripped = False
        self.stat = 0.0
        self._note(
            now,
            f"no residuals for {max_gap_hours:.0f} h; released as stale",
        )
        return True

    def _note(self, when: datetime, text: str) -> None:
        self.evidence.append(f"{when.isoformat(timespec='seconds')}: {text}")
        del self.evidence[:-6]

    def as_dict(self) -> dict[str, Any]:
        data = {
            "stat": round(self.stat, 4),
            "tripped": self.tripped,
            "evidence": list(self.evidence),
            "last_fed": (
                self.last_fed.isoformat() if self.last_fed is not None else None
            ),
        }
        if self.reference_hours is not None:
            # Only a tracked detector persists a fit: the zero-referenced
            # one's payload is the same as before the reference existed.
            data["reference"] = (
                [round(v, 6) for v in self.reference]
                if self.reference is not None else None
            )
            data["reference_cov"] = (
                [round(v, 9) for v in self.reference_cov]
                if self.reference_cov is not None else None
            )
        return data

    def load(self, data: dict[str, Any] | None) -> None:
        """Restore state; thresholds stay code-owned, never persisted."""
        if not isinstance(data, dict):
            return
        try:
            self.stat = min(max(0.0, float(data.get("stat", 0.0))), self.threshold * STAT_CAP_FACTOR)
        except (TypeError, ValueError, OverflowError):
            self.stat = 0.0
        # `is True`, not truthiness: a corrupt payload ("tripped": "yes")
        # must load as a quiet detector, not a latched one.
        self.tripped = data.get("tripped") is True
        raw = data.get("evidence")
        if isinstance(raw, list):
            self.evidence = [str(e) for e in raw[-6:]]
        raw_fed = data.get("last_fed")
        if isinstance(raw_fed, str):
            self.last_fed = stored_instant(raw_fed)
        # A missing or corrupt reference re-seeds at the next sample: a
        # payload from before it existed loads exactly like a fresh one.
        ref = _finite_floats(data.get("reference"))
        cov = _finite_floats(data.get("reference_cov"))
        if (
            ref and cov and len(cov) == len(ref) ** 2
            and all(abs(v) <= REFERENCE_PRIOR_COV for v in cov)
            and _positive_definite(cov, len(ref))
        ):
            self.reference, self.reference_cov = ref, cov
        else:
            self.reference, self.reference_cov = None, None


def _finite_floats(raw: Any) -> list[float] | None:
    """``raw`` as a list of finite floats, or None (a bool is not a number)."""
    if not isinstance(raw, list):
        return None
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in raw):
        return None
    vals = [float(v) for v in raw]
    return vals if all(np.isfinite(v) for v in vals) else None


def _positive_definite(flat: list[float], k: int) -> bool:
    """Whether ``flat`` is a symmetric positive-definite k x k matrix."""
    m = np.array(flat).reshape(k, k)
    if not np.allclose(m, m.T):
        return False
    try:
        np.linalg.cholesky(m)
    except np.linalg.LinAlgError:
        return False
    return True
