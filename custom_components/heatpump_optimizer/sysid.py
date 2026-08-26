"""Active system identification: run an experiment instead of waiting.

Every learner in the integration is passive. Each waits for the house to happen
to do something informative, which is why parameters take weeks to converge and
why the guard thresholds have to be so conservative: normal operation provides
poor excitation, so most observations are ambiguous and get rejected.

Standard practice in process control is to stop waiting and run an experiment.
A deliberate step change gives clean excitation, and the time constant and loss
coefficient fall out in days rather than weeks.

Three constraints shape the design:

**Comfort is a hard constraint on the experiment, not a cost term.** The step
has to be small enough that the occupants do not notice, which directly bounds
how much information can be extracted. That is the trade, and it is not
negotiable — a learning feature that makes the house cold has failed even if
the identification is excellent.

**It must be gated.** Mild outdoor temperature, cheap electricity, night hours,
and explicit user opt-in. Running a step test into a -15 °C evening at peak
tariff would be both expensive and uncomfortable.

**It must be abortable, and must not repeat on a converged house.** Both are
handled here rather than left to the caller.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

import numpy as np

_LOGGER = logging.getLogger(__name__)

PHASE_IDLE = "idle"
PHASE_ARMED = "armed"
PHASE_SETTLING = "settling"
PHASE_STEP = "step"
PHASE_RELAX = "relax"
PHASE_DONE = "done"
PHASE_ABORTED = "aborted"


@dataclass
class SysIdConfig:
    """Gating conditions and step size."""

    enabled: bool = False
    #: Outdoor temperature band in which a step is both safe and informative.
    #: Too cold and the step risks comfort; too mild and ΔT is too small for
    #: the loss coefficient to be identifiable.
    min_outdoor_temp: float = -5.0
    max_outdoor_temp: float = 10.0
    #: Only run when the price is in the cheapest fraction of the horizon.
    max_price_percentile: float = 30.0
    #: Night window, when nobody is moving between rooms opening doors.
    start_hour: int = 23
    end_hour: int = 5
    #: How far the room is allowed to drift during the step, in °C. This is the
    #: comfort constraint, and it is what bounds the achievable accuracy.
    max_excursion_c: float = 0.8
    #: Duration of each phase in hours.
    settle_hours: float = 1.0
    step_hours: float = 2.0
    relax_hours: float = 2.0
    #: Prior for the intercept, from the configuration: the comfort-bounded
    #: excursion (max_excursion_c) keeps the ΔT column nearly constant, so
    #: the intercept is weakly identified from data alone and pure least
    #: squares either rejects noisy nights wholesale or adopts a
    #: selection-biased UA. The fit ridges the intercept toward
    #: gains_prior_kw / thermal_mass_prior instead of toward nothing.
    gains_prior_kw: float = 0.3
    thermal_mass_prior: float = 10.0
    #: Do not repeat on a house that has already converged.
    min_days_between_runs: float = 30.0
    converged_samples: int = 200


@dataclass
class SysIdSample:
    """One observation during an experiment.

    ``power_kw`` is *thermal* output, not electrical draw. The fit below
    regresses the room's energy balance, in which the input is heat delivered
    into the building; using electrical draw instead would scale both
    identified parameters by the COP, and the error would look entirely
    plausible because the ratio between them — the time constant — stays
    correct.
    """

    when: datetime
    room_temp: float
    outdoor_temp: float
    power_kw: float
    phase: str


@dataclass
class SysIdResult:
    """What an experiment identified."""

    completed: bool = False
    #: Time constant of the room, hours.
    time_constant_hours: float | None = None
    #: Heat loss coefficient, kW/°C.
    heat_loss_kw_per_c: float | None = None
    #: Effective thermal capacity, kWh/°C.
    thermal_mass_kwh_per_c: float | None = None
    #: Constant free heat during the experiment (occupancy, appliances,
    #: residual solar), kW. ``None`` when the fit had to run without the
    #: intercept column that identifies it.
    internal_gains_kw: float | None = None
    #: 0-1; how much the result should be trusted as a prior.
    confidence: float = 0.0
    reason: str = ""

    def as_dict(self) -> dict:
        return {
            "completed": self.completed,
            "time_constant_hours": (
                round(self.time_constant_hours, 2)
                if self.time_constant_hours is not None
                else None
            ),
            "heat_loss_kw_per_c": (
                round(self.heat_loss_kw_per_c, 4)
                if self.heat_loss_kw_per_c is not None
                else None
            ),
            "thermal_mass_kwh_per_c": (
                round(self.thermal_mass_kwh_per_c, 2)
                if self.thermal_mass_kwh_per_c is not None
                else None
            ),
            "internal_gains_kw": (
                round(self.internal_gains_kw, 3)
                if self.internal_gains_kw is not None
                else None
            ),
            "confidence": round(self.confidence, 2),
            "reason": self.reason,
        }


class SystemIdentification:
    """State machine driving a step-response experiment."""

    def __init__(self, config: SysIdConfig | None = None) -> None:
        self.config = config or SysIdConfig()
        self.phase: str = PHASE_IDLE
        self.phase_started: datetime | None = None
        self.samples: list[SysIdSample] = []
        self.last_run: datetime | None = None
        self.result: SysIdResult = SysIdResult()
        self._baseline_temp: float | None = None
        self._step_power: float = 0.0

    # -- control ------------------------------------------------------------

    @property
    def active(self) -> bool:
        return self.phase in (PHASE_ARMED, PHASE_SETTLING, PHASE_STEP, PHASE_RELAX)

    def arm(self, now: datetime) -> bool:
        """Arm an experiment, to start when conditions allow."""
        if not self.config.enabled:
            _LOGGER.info("System identification is disabled in the configuration")
            return False
        if self.active:
            return False
        if self.last_run is not None:
            days = (now - self.last_run).total_seconds() / 86400.0
            if days < self.config.min_days_between_runs:
                _LOGGER.info(
                    "System identification ran %.1f days ago; waiting for the "
                    "%.0f day minimum",
                    days,
                    self.config.min_days_between_runs,
                )
                return False
        self.phase = PHASE_ARMED
        self.phase_started = now
        self.samples = []
        return True

    def abort(self, reason: str) -> None:
        if not self.active:
            return
        _LOGGER.info("Aborting system identification: %s", reason)
        self.phase = PHASE_ABORTED
        self.result = SysIdResult(completed=False, reason=reason)

    # -- gating -------------------------------------------------------------

    def conditions_met(
        self,
        now: datetime,
        outdoor_temp: float,
        price: float,
        price_horizon: np.ndarray,
        learner_samples: int,
    ) -> tuple[bool, str]:
        """Whether an armed experiment may start right now."""
        cfg = self.config
        if learner_samples >= cfg.converged_samples:
            return False, "house already converged"
        if not (cfg.min_outdoor_temp <= outdoor_temp <= cfg.max_outdoor_temp):
            return False, "outdoor temperature outside the safe band"

        hour = now.hour
        if cfg.start_hour <= cfg.end_hour:
            in_window = cfg.start_hour <= hour < cfg.end_hour
        else:
            # The window wraps midnight, which is the normal case.
            in_window = hour >= cfg.start_hour or hour < cfg.end_hour
        if not in_window:
            return False, "outside the night window"

        if price_horizon is not None and len(price_horizon):
            cutoff = float(np.percentile(price_horizon, cfg.max_price_percentile))
            if price > cutoff:
                return False, "electricity is not cheap enough"
        return True, "ready"

    # -- execution ----------------------------------------------------------

    def step(
        self,
        now: datetime,
        room_temp: float,
        outdoor_temp: float,
        price: float,
        price_horizon: np.ndarray,
        learner_samples: int,
        max_power_kw: float,
        cop: float = 1.0,
    ) -> float | None:
        """Advance the experiment; returns a power override, or ``None``.

        ``None`` means "the optimizer's plan stands". A number overrides it for
        this interval, which is how the step is actually injected. The returned
        value is electrical power, because that is what the rest of the
        integration speaks; ``cop`` converts it to the thermal quantity the fit
        needs.
        """
        cfg = self.config
        if not self.active:
            return None

        if self.phase == PHASE_ARMED:
            ok, reason = self.conditions_met(
                now, outdoor_temp, price, price_horizon, learner_samples
            )
            if not ok:
                if "converged" in reason:
                    self.phase = PHASE_IDLE
                    self.result = SysIdResult(completed=False, reason=reason)
                return None
            _LOGGER.info("Starting system identification: %s", reason)
            self.phase = PHASE_SETTLING
            self.phase_started = now
            self._baseline_temp = room_temp

        elapsed = (
            (now - self.phase_started).total_seconds() / 3600.0
            if self.phase_started
            else 0.0
        )
        self.samples.append(
            SysIdSample(now, room_temp, outdoor_temp, 0.0, self.phase)
        )

        # Comfort is a hard constraint: abandon the experiment rather than
        # trade a degree of comfort for a better fit.
        if self._baseline_temp is not None:
            if abs(room_temp - self._baseline_temp) > cfg.max_excursion_c:
                self.abort("room temperature drifted beyond the allowed excursion")
                return None

        if self.phase == PHASE_SETTLING:
            # Hold steady so the step starts from a known, quiet state.
            if elapsed >= cfg.settle_hours:
                self.phase = PHASE_STEP
                self.phase_started = now
                self._step_power = max_power_kw * 0.6
                _LOGGER.debug(
                    "System identification step: injecting %.2f kW",
                    self._step_power,
                )
            return None

        if self.phase == PHASE_STEP:
            self.samples[-1].power_kw = self._step_power * max(cop, 0.1)
            if elapsed >= cfg.step_hours:
                self.phase = PHASE_RELAX
                self.phase_started = now
            return self._step_power

        if self.phase == PHASE_RELAX:
            if elapsed >= cfg.relax_hours:
                self._finish(now)
            return 0.0

        return None

    def _finish(self, now: datetime) -> None:
        self.phase = PHASE_DONE
        self.last_run = now
        self.result = self.identify()
        if self.result.completed:
            _LOGGER.info(
                "System identification complete: tau=%.2f h, UA=%.4f kW/°C, "
                "C=%.2f kWh/°C (confidence %.2f)",
                self.result.time_constant_hours or 0.0,
                self.result.heat_loss_kw_per_c or 0.0,
                self.result.thermal_mass_kwh_per_c or 0.0,
                self.result.confidence,
            )

    # -- fitting ------------------------------------------------------------

    def identify(self) -> SysIdResult:
        """Fit a first-order model to the recorded step response.

        During the experiment the room obeys

            C·dT/dt = Q + G - UA·(T - T_out)

        with G the constant free heat (occupancy, appliances, residual
        solar). Regressing dT/dt on (T - T_out), Q and a constant gives
        UA/C, 1/C and G/C directly, which is a plain least-squares problem.
        It is solved over both the step and the relaxation phases because
        the relaxation carries the cleanest information about UA (no input
        to confound it) while the step carries the information about C.

        The intercept column is not decoration. Relax-phase samples carry
        ``power_kw = 0`` while the gains keep heating the room, so a fit
        without it pushed G into the other two coefficients and biased both
        UA and C — the exact parameters the experiment exists to pin. When
        the data cannot support three columns (rank < 3) the fit degrades
        to the historical two-column form rather than failing outright,
        and reports no gains figure.
        """
        usable = [
            s for s in self.samples if s.phase in (PHASE_STEP, PHASE_RELAX)
        ]
        if len(usable) < 6:
            return SysIdResult(completed=False, reason="not enough samples")

        rows = []
        targets = []
        for previous, current in zip(usable, usable[1:]):
            dt_h = (current.when - previous.when).total_seconds() / 3600.0
            if dt_h <= 1e-3 or dt_h > 2.0:
                continue
            rate = (current.room_temp - previous.room_temp) / dt_h
            delta = previous.room_temp - previous.outdoor_temp
            rows.append([-delta, previous.power_kw, 1.0])
            targets.append(rate)

        if len(rows) < 5:
            return SysIdResult(completed=False, reason="not enough usable intervals")

        a = np.asarray(rows, dtype=float)
        b = np.asarray(targets, dtype=float)
        gains_kw: float | None = None
        # The comfort constraint bounds the room's excursion, which keeps the
        # ΔT column nearly constant — near-collinear with the intercept — so
        # with realistic sensor noise the unregularized three-column fit is
        # ill-conditioned: it either fails the outcome guards on almost every
        # night (the feature silently dead) or the survivors carry a
        # selection-biased UA (v4.0.5 review, measured ~+34%). A ridge pulls
        # the intercept toward the CONFIGURED gains — a genuine prior, not
        # zero — with weight equal to a quarter of the samples, so a night
        # with real information still moves it and a noisy one cannot run.
        prior_icpt = self.config.gains_prior_kw / max(
            self.config.thermal_mass_prior, 0.1
        )
        # Bayesian weighting, calibrated by the data's own residual noise: a
        # first unregularized pass measures the scatter s, and the prior
        # then enters as ONE pseudo-observation whose uncertainty is a
        # generous ±0.5 kW on the gains. Clean data (s → 0) out-weighs the
        # prior and recovers the truth exactly; a noisy night leans on the
        # prior instead of handing the collinear intercept the noise.
        prior_sd = 0.5 / max(self.config.thermal_mass_prior, 0.1)
        try:
            pass1, _res1, rank1, _ = np.linalg.lstsq(a, b, rcond=None)
            resid = b - a @ pass1
            dof = max(len(rows) - 3, 1)
            s_noise = float(np.sqrt(np.sum(resid**2) / dof))
        except np.linalg.LinAlgError:
            return SysIdResult(completed=False, reason="fit failed")
        data_w = 1.0 / max(s_noise, 1e-9)
        prior_w = 1.0 / prior_sd
        a_fit = np.vstack(
            [a * data_w, prior_w * np.array([[0.0, 0.0, 1.0]])]
        )
        b_fit = np.concatenate([b * data_w, [prior_w * prior_icpt]])
        try:
            solution, residuals, rank, _ = np.linalg.lstsq(
                a_fit, b_fit, rcond=None
            )
            if rank < 3:
                # The constant cannot be separated (e.g. ΔT barely moved, so
                # the delta column is itself nearly constant). Fall back to
                # the two-column fit rather than discarding the experiment.
                a = a[:, :2]
                solution, residuals, rank, _ = np.linalg.lstsq(a, b, rcond=None)
                a_fit, b_fit = a, b
                if rank < 2:
                    # Both regressors moved together, so they cannot be
                    # separated. This is exactly the ambiguity the experiment
                    # exists to break: the step was too small or too short.
                    return SysIdResult(
                        completed=False,
                        reason="step gave insufficient excitation",
                    )
        except np.linalg.LinAlgError:
            return SysIdResult(completed=False, reason="fit failed")

        ua_over_c, one_over_c = float(solution[0]), float(solution[1])
        if one_over_c <= 1e-6 or ua_over_c <= 1e-6:
            return SysIdResult(completed=False, reason="fit gave implausible signs")

        capacity = 1.0 / one_over_c
        ua = ua_over_c * capacity
        tau = 1.0 / ua_over_c
        if solution.shape[0] == 3:
            gains_kw = float(solution[2]) * capacity
            # Sanity bound: a hair of negative gains is regression noise and
            # clips to zero; far outside the band means the "constant" was a
            # drifting contaminant (sun through a window, a door), and a fit
            # whose intercept is absorbing an unmodelled input has no claim
            # on the other two coefficients either.
            if not (-0.5 <= gains_kw <= 2.0):
                # Rejecting, not clipping: a triple whose intercept was
                # clipped no longer satisfies the regression it came from,
                # so UA and C would carry the unclipped intercept's bias.
                return SysIdResult(
                    completed=False,
                    reason="fitted gains outside plausible bounds",
                )
            gains_kw = float(np.clip(gains_kw, 0.0, 2.0))

        # Confidence from how well the fit explains the data, tempered by how
        # much data there was.
        predicted = a @ solution
        ss_res = float(np.sum((b - predicted) ** 2))
        ss_tot = float(np.sum((b - np.mean(b)) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-9 else 0.0
        confidence = float(np.clip(r2, 0.0, 1.0)) * min(1.0, len(rows) / 20.0)
        # The intercept's identifiability scales with how far ΔT actually
        # moved; R² cannot see that (a flat fit explains flat data well), so
        # the blend weight is tempered by the achieved excursion directly.
        deltas = -a[:, 0]
        excursion = float(np.max(deltas) - np.min(deltas)) if len(deltas) else 0.0
        confidence *= float(np.clip(excursion / 2.0, 0.3, 1.0))

        if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0):
            return SysIdResult(
                completed=False, reason="fitted parameters outside plausible bounds"
            )

        return SysIdResult(
            completed=True,
            time_constant_hours=tau,
            heat_loss_kw_per_c=ua,
            thermal_mass_kwh_per_c=capacity,
            internal_gains_kw=gains_kw,
            confidence=confidence,
            reason="ok",
        )

    def as_dict(self) -> dict:
        return {
            "phase": self.phase,
            "active": self.active,
            "samples": len(self.samples),
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "result": self.result.as_dict(),
        }
