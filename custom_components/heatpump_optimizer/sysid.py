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

#: The comfort allowance a default install gives the experiment, and the
#: reference the confidence scores the achieved excursion against.
#:
#: It is a DESIGN constant on purpose. Scoring the achieved excursion against
#: the *configured* bound (v6.3.3) made the confidence fall when the bound was
#: widened: the same finished experiment, having gathered strictly more
#: information, scored less because its allowance was larger. That inverted
#: the whole point of the factor and shut the gate on every install that lifts
#: the bound (D7-01's own positive control went from 4 of 8 admitted to 0 of
#: 8). Against a fixed reference the factor is monotone in the excursion the
#: room actually made, which is what identifiability depends on.
DEFAULT_MAX_EXCURSION_C = 0.8


def _predict_step_excursion(
    baseline: float,
    outdoor: float,
    ua: float,
    capacity: float,
    gains: float,
    step_thermal_kw: float,
    step_hours: float,
    relax_hours: float,
    dt_h: float = 0.05,
) -> tuple[float, float]:
    """Peak and final |T − baseline| over a first-order step then relax."""
    if ua <= 1e-9 or capacity <= 1e-9:
        return float("inf"), float("inf")
    tau = capacity / ua
    peak = 0.0
    temp = baseline

    def _advance(duration: float, q: float) -> None:
        nonlocal peak, temp
        t_ss = outdoor + (q + gains) / ua
        steps = max(int(duration / dt_h), 1)
        h = duration / steps
        for _ in range(steps):
            temp = t_ss + (temp - t_ss) * np.exp(-h / tau)
            peak = max(peak, abs(temp - baseline))

    _advance(step_hours, step_thermal_kw)
    _advance(relax_hours, 0.0)
    return peak, abs(temp - baseline)


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
    max_excursion_c: float = DEFAULT_MAX_EXCURSION_C
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
    #: Prior width for the room sensor's own drift, °C/h. The drift column
    #: is identifiable from a clean window and hopeless from a short noisy
    #: one, so it gets the same treatment as the intercept: one
    #: pseudo-observation at ZERO, weighed against the data's own residual
    #: scatter. A clean night reports the drift it can see; a 0.10 °C-noise
    #: night at the 30-minute cadence has seven rows and no business
    #: inventing one, and shrinks back to the undrifted fit. 0.02 °C/h is
    #: 0.08 °C over the whole window, a tenth of the comfort allowance --
    #: measured against the alternatives (0.05, 0.1, 0.2) it holds the
    #: completion rate the release already had while more than halving the
    #: adopted UA error at every noise level.
    sensor_drift_prior_c_per_h: float = 0.02
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
    #: Linear drift of the ROOM SENSOR over the experiment, °C/h, estimated
    #: as a nuisance parameter alongside the house. ``None`` when the fit had
    #: to run without the column that identifies it. A sensor ageing at
    #: 0.10 °C/h is invisible to any noise statistic built on second
    #: differences — a straight line has none — and lands squarely in UA.
    sensor_drift_c_per_h: float | None = None
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

    def _size_step_power(
        self,
        max_power_kw: float,
        cop: float,
        baseline: float,
        outdoor_temp: float,
        ua: float,
        capacity: float,
        gains: float,
    ) -> float | None:
        """Largest electrical step whose predicted excursion fits the bound."""
        cfg = self.config
        cop = max(cop, 0.1)
        best: float | None = None
        for i in range(1, 41):
            power = max_power_kw * i / 40.0
            peak, final = _predict_step_excursion(
                baseline,
                outdoor_temp,
                ua,
                capacity,
                gains,
                power * cop,
                cfg.step_hours,
                cfg.relax_hours,
            )
            if peak <= cfg.max_excursion_c and final <= cfg.max_excursion_c:
                best = power
        return best

    def _over_excursion(self, room_temp: float) -> bool:
        base = self._baseline_temp
        return (
            base is not None
            and abs(room_temp - base) > self.config.max_excursion_c
        )

    def _begin_step_phase(
        self,
        now: datetime,
        outdoor_temp: float,
        max_power_kw: float,
        cop: float,
        house_ua: float | None,
        house_capacity: float | None,
        house_gains: float | None,
    ) -> bool:
        """Enter PHASE_STEP with a comfort-bounded injection. False if none fits."""
        self.phase = PHASE_STEP
        self.phase_started = now
        if (
            house_ua is not None
            and house_capacity is not None
            and house_gains is not None
            and house_ua > 1e-6
            and house_capacity > 1e-6
            and self._baseline_temp is not None
        ):
            sized = self._size_step_power(
                max_power_kw,
                cop,
                self._baseline_temp,
                outdoor_temp,
                house_ua,
                house_capacity,
                house_gains,
            )
            if sized is None:
                self.abort("no step fits within the comfort bound")
                return False
            self._step_power = sized
        else:
            self._step_power = max_power_kw * 0.3
        _LOGGER.debug(
            "System identification step: injecting %.2f kW",
            self._step_power,
        )
        return True

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
        plan_power_kw: float = 0.0,
        house_ua: float | None = None,
        house_capacity: float | None = None,
        house_gains: float | None = None,
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
        thermal_cop = max(cop, 0.1)
        if self.phase == PHASE_SETTLING:
            # D2-08 / #325: the plan keeps running during settle; record what
            # was actually delivered, not zero, before the rows enter identify().
            self.samples[-1].power_kw = max(plan_power_kw, 0.0) * thermal_cop
            if self._over_excursion(room_temp):
                self.abort("room temperature drifted beyond the allowed excursion")
                return None
            if elapsed >= cfg.settle_hours and not self._begin_step_phase(
                now,
                outdoor_temp,
                max_power_kw,
                cop,
                house_ua,
                house_capacity,
                house_gains,
            ):
                return None
            return None

        if self._over_excursion(room_temp):
            self.abort("room temperature drifted beyond the allowed excursion")
            return None

        if self.phase == PHASE_STEP:
            self.samples[-1].power_kw = self._step_power * thermal_cop
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
            s
            for s in self.samples
            if s.phase in (PHASE_SETTLING, PHASE_STEP, PHASE_RELAX)
        ]
        if len(usable) < 6:
            return SysIdResult(completed=False, reason="not enough samples")

        rows = []
        targets = []
        row_dts = []
        t_zero = usable[0].when
        for previous, current in zip(usable, usable[1:]):
            dt_h = (current.when - previous.when).total_seconds() / 3600.0
            if dt_h <= 1e-3 or dt_h > 2.0:
                continue
            rate = (current.room_temp - previous.room_temp) / dt_h
            delta = previous.room_temp - previous.outdoor_temp
            since = (previous.when - t_zero).total_seconds() / 3600.0
            # D2-07: the fourth column is elapsed time, and it is there to
            # catch a drifting ROOM SENSOR. A sensor ageing at d °C/h adds
            # d·t to every reading, which enters the regression twice — the
            # rate gains a constant d, the ΔT column gains a ramp d·t — and
            # the identity
            #     rate = -(UA/C)·Δ + Q/C + (G/C + d) + (UA/C)·d·t
            # shows the ramp has nowhere to go in a three-column fit but
            # into UA. Estimating d as a nuisance parameter costs one degree
            # of freedom and leaves UA alone. On an undrifting sensor the
            # column fits zero, so this is inert where there is nothing to
            # correct.
            rows.append([-delta, previous.power_kw, 1.0, since])
            targets.append(rate)
            row_dts.append(dt_h)

        if len(rows) < 5:
            return SysIdResult(completed=False, reason="not enough usable intervals")

        a = np.asarray(rows, dtype=float)
        b = np.asarray(targets, dtype=float)
        dts = np.asarray(row_dts, dtype=float)
        # Centre the drift column: uncentred it is strongly correlated with
        # the intercept, and the ΔT/intercept pair is already the collinear
        # one this fit has to survive. The centring is undone in the
        # coefficient algebra below.
        t_mean = float(np.mean(a[:, 3]))
        a[:, 3] -= t_mean
        gains_kw: float | None = None
        drift_c_per_h: float | None = None
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
        n_cols = a.shape[1]
        try:
            pass1, _res1, rank1, _ = np.linalg.lstsq(a, b, rcond=None)
            resid = b - a @ pass1
            dof = max(len(rows) - n_cols, 1)
            s_noise = float(np.sqrt(np.sum(resid**2) / dof))
        except np.linalg.LinAlgError:
            return SysIdResult(completed=False, reason="fit failed")
        # --- D2-01: errors-in-variables correction -------------------------
        # ``T_prev`` sits on BOTH sides of the regression -- in the rate
        # (divided by dt) and in the delta column -- so sensor noise covaries
        # the two and biases the UA/C slope UPWARD (the audit measured +44 %
        # at 0.05 °C noise, +108 % at 0.10 °C, and biased fits cleared the
        # 0.3 adoption gate). The noise variance is estimated from the room
        # series itself and the KNOWN bias terms are subtracted from the
        # normal equations: the delta column's own noise deflates X'X by
        # n*sigma^2, and the rate/regressor noise covariance shifts X'y by
        # sigma^2 * sum(1/dt). Clean data estimates sigma^2 ~ 0 and the
        # correction vanishes; a window whose noise exceeds a third of the
        # delta column's spread is refused outright -- there is no honest
        # fit to be had there.
        #
        # sigma^2 from second differences WITHIN a phase only: the step->
        # relax transition is a genuine kink in the signal (power drops to
        # zero), and one boundary second difference would swamp a whole
        # night of sensor noise.
        #
        # D2-07: the plant's OWN curvature is removed first. A second
        # difference of a smooth exponential is h^2*T'', not zero, and
        # within a phase Q is constant so T'' = -(UA/C)*T' -- a quantity the
        # first pass already estimated. Left in, that curvature is read as
        # sensor noise: it triggered the errors-in-variables correction on
        # perfectly clean data (measured: the noise-free UA null moved from
        # +0.0000 to -0.0002) and, on a house whose response is genuinely
        # curved, it is what the refusal gate would fire on.
        k_hat = max(float(pass1[0]), 0.0)
        sigma2 = 0.0
        d2_all = []
        for i in range(1, len(usable) - 1):
            if usable[i - 1].phase == usable[i].phase == usable[i + 1].phase:
                h_prev = (
                    usable[i].when - usable[i - 1].when
                ).total_seconds() / 3600.0
                if h_prev <= 1e-6:
                    continue
                curvature = (
                    -k_hat
                    * h_prev
                    * (usable[i + 1].room_temp - usable[i - 1].room_temp)
                    / 2.0
                )
                d2_all.append(
                    usable[i + 1].room_temp
                    - 2.0 * usable[i].room_temp
                    + usable[i - 1].room_temp
                    - curvature
                )
        if len(d2_all) >= 3:
            sigma2 = float(
                np.sum(np.square(d2_all)) / (6.0 * len(d2_all))
            )
        n_rows = float(len(rows))
        x1_spread2 = float(np.var(a[:, 0])) * n_rows / max(n_rows - 1.0, 1.0)
        if sigma2 > 0.0 and sigma2 > x1_spread2 / 9.0:
            return SysIdResult(
                completed=False,
                reason="sensor noise dominates the excursion",
            )
        # --- end correction; solve via normal equations ---------------------
        # Column equilibration before the normal-equation solve: the columns
        # live at wildly different scales (delta ~20, power ~10, constant 1,
        # elapsed hours ~2), and an explicit Gram of that is needlessly
        # ill-conditioned in float64. Normalising each column by its own
        # norm keeps the solve honest; the correction and prior terms are
        # applied in the SAME scaled units.
        #
        # D2-07: the data weight is GONE from this solve, because it only
        # ever entered as a ratio against the prior's weight and cancels.
        # v6.3.3 carried it explicitly as 1/max(s_noise, 1e-3) — and that
        # floor is a bug with teeth: on a clean night s_noise is ~1e-15, the
        # floor caps the data's weight at 1e3, and the prior it was supposed
        # to out-weigh instead takes about a fifth of the near-collinear
        # intercept direction. Measured on the audit's own null control, a
        # noise-free window's UA went from +0.0000 to -1.58 %. Carrying the
        # RATIO s_noise/prior_sd restores the documented intent — clean data
        # out-weighs the prior and recovers the truth exactly — with no
        # floor and no 1e9 to make the solve singular.
        col_scale = np.maximum(
            np.sqrt(np.mean(np.square(a), axis=0)), 1e-12
        )
        a_s = a / col_scale
        gram = a_s.T @ a_s
        rhs = a_s.T @ b
        if sigma2 > 0.0:
            gram[0, 0] -= n_rows * sigma2 / (col_scale[0] ** 2)
            rhs[0] -= sigma2 * float(np.sum(1.0 / dts)) / col_scale[0]
        # The prior enters as its own pseudo-observation, exactly as the
        # stacked row did -- same algebra, normal-equation form, weighed
        # against the data through prior_rel = prior_w / data_w.
        #
        # D2-07: the right-hand side term had one factor of col_scale[2] too
        # many, which is not a scaling nicety -- it made the prior pull the
        # intercept toward prior_icpt/col_scale[2], i.e. toward ZERO gains,
        # the exact thing the comment above says it exists not to do. On the
        # D7-01 harness's first-order positive control that alone moved the
        # identified UA from -8.06 % to -16.21 %.
        prior_rel = s_noise / prior_sd
        gram[2, 2] += (prior_rel / col_scale[2]) ** 2
        rhs[2] += (prior_rel / col_scale[2]) * prior_rel * prior_icpt
        # The drift column's own shrinkage prior, mean zero. Its coefficient
        # is (UA/C)·d, so the width in coefficient units is the configured
        # drift width times the slope the first pass already found (clamped
        # to the plausible time-constant band, because a wild first pass must
        # shrink the drift harder, never less).
        k_prior = float(np.clip(k_hat, 1.0 / 200.0, 1.0 / 0.1))
        drift_sd = k_prior * max(
            self.config.sensor_drift_prior_c_per_h, 1e-6
        )
        drift_rel = s_noise / drift_sd
        gram[3, 3] += (drift_rel / col_scale[3]) ** 2
        try:
            solution = np.linalg.solve(gram, rhs)
            rank = n_cols
        except np.linalg.LinAlgError:
            solution = None
        if solution is not None:
            # Undo the column scaling on the coefficients.
            solution = solution / col_scale
        if solution is None or not np.all(np.isfinite(solution)) or rank < n_cols:
            # The constant cannot be separated (e.g. ΔT barely moved, so
            # the delta column is itself nearly constant). Fall back to
            # the two-column fit rather than discarding the experiment.
            a = a[:, :2]
            try:
                solution, residuals, rank, _ = np.linalg.lstsq(
                    a, b, rcond=None
                )
            except np.linalg.LinAlgError:
                return SysIdResult(completed=False, reason="fit failed")
            if rank < 2:
                # Both regressors moved together, so they cannot be
                # separated. This is exactly the ambiguity the experiment
                # exists to break: the step was too small or too short.
                return SysIdResult(
                    completed=False,
                    reason="step gave insufficient excitation",
                )
            gains_kw = None
            drift_c_per_h = None

        ua_over_c, one_over_c = float(solution[0]), float(solution[1])
        if one_over_c <= 1e-6 or ua_over_c <= 1e-6:
            return SysIdResult(completed=False, reason="fit gave implausible signs")

        capacity = 1.0 / one_over_c
        ua = ua_over_c * capacity
        tau = 1.0 / ua_over_c
        if solution.shape[0] >= 4:
            # rate carries (UA/C)·d on the centred elapsed column, so the
            # sensor's drift falls straight out of the ratio.
            drift_c_per_h = float(solution[3]) / ua_over_c
        if solution.shape[0] >= 3:
            # The intercept holds G/C + d·(1 + (UA/C)·t̄) once the elapsed
            # column is centred at t̄; the free heat is what is left of it
            # after the sensor's own drift is taken back out.
            gains_over_c = float(solution[2])
            if drift_c_per_h is not None:
                gains_over_c -= drift_c_per_h * (1.0 + ua_over_c * t_mean)
            gains_kw = gains_over_c * capacity
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
        confidence = float(np.clip(r2, 0.0, 1.0)) * min(1.0, len(rows) / 12.0)
        # The intercept's identifiability scales with how far ΔT actually
        # moved; R² cannot see that (a flat fit explains flat data well), so
        # the blend weight is tempered by the achieved excursion directly.
        # D7-02: normalised by the default comfort allowance, not by a
        # literal 2 °C — the comfort constraint caps the excursion at
        # max_excursion_c (0.8 by default), so the old /2 divisor held every
        # legal experiment at or below 0.4 here, and together with the /20
        # row cap it kept the default protocol's confidence under the 0.3
        # adoption gate on every install: the experiment could never be
        # adopted at all (inert on target houses). Against the design
        # reference, a protocol-maximal excursion earns 1.0 — and, unlike
        # the configured bound v6.3.3 divided by, it stays monotone: an
        # install that widens its allowance cannot score lower for the same
        # room movement (see DEFAULT_MAX_EXCURSION_C).
        #
        # D2-07: measured on the room's REAL movement. A drifting sensor
        # inflates the ΔT range with its own ramp, and crediting that as
        # identifiability is how a 0.10 °C/h drift came to be adopted at
        # confidence 1.000.
        deltas = -a[:, 0]
        if drift_c_per_h is not None and a.shape[1] >= 4:
            deltas = deltas - drift_c_per_h * a[:, 3]
        excursion = float(np.max(deltas) - np.min(deltas)) if len(deltas) else 0.0
        confidence *= float(np.clip(
            excursion / DEFAULT_MAX_EXCURSION_C, 0.3, 1.0
        ))
        # D2-01's gate half: a fit is only as trustworthy as its residual
        # noise is small against the signal it claims to explain. The rate
        # signal here is the spread of the target column; the audit showed
        # biased fits sailing through a pure-R² gate because a noisy window
        # can still look self-consistent. SNR ≥ 4 earns full weight; SNR ≤ 1
        # earns none (the EIV-corrected estimator keeps such windows honest,
        # but they still carry little information).
        signal_spread = float(np.percentile(b, 90) - np.percentile(b, 10))
        snr = signal_spread / max(s_noise, 1e-9)
        confidence *= float(np.clip((snr - 1.0) / 3.0, 0.0, 1.0))

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
            sensor_drift_c_per_h=drift_c_per_h,
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
