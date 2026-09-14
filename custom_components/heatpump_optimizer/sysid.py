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
from typing import Any, Callable

import numpy as np

from .const import DEFAULT_SLAB_HEAT_TRANSFER, DEFAULT_SLAB_THERMAL_MASS
from .thermal_model import ThermalModel, ThermalParameters, ThermalState

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
) -> tuple[float, float]:
    """Peak and final |T − baseline| over a first-order step then relax.

    Each phase is one exponential with constant Q, so the extrema are at
    the phase endpoints (heating then cooling is monotonic in each).

    Kept as the one-state control. Production sizing uses
    :func:`_predict_step_excursion_plant` — heat lands in the slab
    (:meth:`ThermalModel.simulate_step`), so this over-predicts the
    room's move and undersizes the experiment (#779).
    """
    if ua <= 1e-9 or capacity <= 1e-9:
        return float("inf"), float("inf")
    tau = capacity / ua

    def _end(temp: float, q: float, hours: float) -> float:
        t_ss = outdoor + (q + gains) / ua
        return float(t_ss + (temp - t_ss) * np.exp(-hours / tau))

    after_step = _end(baseline, step_thermal_kw, step_hours)
    after_relax = _end(after_step, 0.0, relax_hours)
    peak = max(abs(after_step - baseline), abs(after_relax - baseline))
    return peak, abs(after_relax - baseline)


def _sizing_model(
    ua: float,
    capacity: float,
    gains: float,
    slab_thermal_mass: float | None = None,
    slab_heat_transfer: float | None = None,
) -> ThermalModel:
    """Single-zone plant whose UA / room mass / gains match the sizer inputs.

    ``house_heat_loss_scale`` stays 1.0: the caller already folds the
    learned scale into ``ua``. The slab pair is the configured house's own
    (``None`` falls back to the ``ThermalParameters`` defaults): sizing on
    any other slab predicts a different building than the one the step
    heats — the shipped presets carry (0.24, 0.24) to (23.0, 2.0) against
    the defaults (5.0, 0.8), which breached ``max_excursion_c`` on the
    light end (#943). The identified UA remains a room-only lumped figure;
    the sizer does not pretend otherwise.
    """
    if slab_thermal_mass is None:
        slab_thermal_mass = DEFAULT_SLAB_THERMAL_MASS
    if slab_heat_transfer is None:
        slab_heat_transfer = DEFAULT_SLAB_HEAT_TRANSFER
    return ThermalModel(
        ThermalParameters(
            heat_loss_coefficient=ua,
            house_heat_loss_scale=1.0,
            room_thermal_mass=capacity,
            internal_gains=gains,
            slab_thermal_mass=slab_thermal_mass,
            slab_heat_transfer=slab_heat_transfer,
            two_zone_enabled=False,
        )
    )


def _predict_step_excursion_plant(
    ua: float,
    capacity: float,
    gains: float,
    baseline: float,
    outdoor: float,
    step_thermal_kw: float,
    step_hours: float,
    relax_hours: float,
    dt_hours: float = 0.25,
    model: ThermalModel | None = None,
    slab_thermal_mass: float | None = None,
    slab_heat_transfer: float | None = None,
) -> tuple[float, float]:
    """Peak and final |T − baseline| on the two-state plant the model simulates.

    Heat enters the slab. The room moves only through ``slab_heat_transfer``.
    The one-state exponential treats the same Q as landing in the room, so
    it cannot size this experiment (#779).
    """
    if ua <= 1e-9 or capacity <= 1e-9:
        return float("inf"), float("inf")
    if model is None:
        model = _sizing_model(
            ua, capacity, gains, slab_thermal_mass, slab_heat_transfer
        )
    k_slab = max(model.params.slab_heat_transfer, 1e-9)
    q_hold = ua * (baseline - outdoor) - gains
    state = ThermalState(
        room_temperature=baseline,
        slab_temperature=baseline + q_hold / k_slab,
        outdoor_temperature=outdoor,
    )
    peak = 0.0
    remaining = step_hours
    while remaining > 1e-12:
        dt = min(dt_hours, remaining)
        state = model.simulate_step(
            state,
            electrical_power=0.0,
            outdoor_temp=outdoor,
            dt_hours=dt,
            external_heat_kw=step_thermal_kw,
        )
        peak = max(peak, abs(state.room_temperature - baseline))
        remaining -= dt
    remaining = relax_hours
    while remaining > 1e-12:
        dt = min(dt_hours, remaining)
        state = model.simulate_step(
            state,
            electrical_power=0.0,
            outdoor_temp=outdoor,
            dt_hours=dt,
            external_heat_kw=0.0,
        )
        peak = max(peak, abs(state.room_temperature - baseline))
        remaining -= dt
    return peak, abs(state.room_temperature - baseline)


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
    #: The slab-room fast mode's time constant as RE-DERIVED by the
    #: two-state fitted arm, hours; ``None`` on every one-state result.
    #: The ratified hybrid (#942, 2026-09-14) fits UA and tau_fast only —
    #: the C_s/k_s split rides a tau-preserving ridge no window length
    #: removes — so this is computed from the FITTED room capacity against
    #: the CONFIG slab pair, and the pair itself is never adopted. An
    #: adopted change to a slab-mode parameter is a config-class change
    #: (#996): the claim-grammar treatment is the owner's decision,
    #: recorded on #996 (comment 5663831849), and until it lands the
    #: published tau is diagnostic, not an adopted value.
    slab_mode_tau_hours: float | None = None
    reason: str = ""

    def as_dict(self) -> dict[str, Any]:
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
            "slab_mode_tau_hours": (
                round(self.slab_mode_tau_hours, 4)
                if self.slab_mode_tau_hours is not None
                else None
            ),
            "reason": self.reason,
        }


#: How many time constants of the slab-room fast mode the protocol's own
#: SHORTEST phase must hold before the plant looks single-state to the fit
#: (3 tau is the conventional 95 % settling band). A DESIGN constant, like
#: DEFAULT_MAX_EXCURSION_C: it prices the model class, not a tuning knob.
FAST_MODE_SETTLE_TAUS = 3.0

#: Width of the intercept ridge ported to the two-state slab fit, kW — the
#: D2-01 instrument's regularization (the one-state fit pulls its intercept
#: toward ``gains_prior_kw``), expressed in the nonlinear form as ONE
#: pseudo-observation ``(G − gains_prior_kw) / width`` appended to the
#: residual vector. The sysid-estimator wave's pre-study (#942, comment
#: 5656402482) measured this port on the nightly 5 h window: UA bias
#: p5/p95 −91/+112 % unridged at 0.01 °C noise against −6.7/+4.2 % ported
#: on light_new — the comfort bound keeps ΔT within ~2 % of its mean, so UA
#: and G are collinear and the unridged fit hands the intercept's noise to
#: both. A DESIGN constant like the prior it ports: it prices the prior's
#: own uncertainty (±0.1 kW on a 0.3 kW prior), not a tuning knob.
SLAB_INTERCEPT_PRIOR_SD_KW = 0.1

#: The noise gate on the two-state fitted arm (#942's wave, act 2): the
#: fit's own residual scatter on the arm window, °C, above which the
#: fitted values are refused by name instead of adopted. The ratified
#: hybrid (owner decision on #942, 2026-09-14, comment 5659441129) prices
#: fitted adoption at "residual noise <= ~0.02 °C": the pre-study's
#: frontier measured the same gate-passing cell inside the ±10 % UA bar at
#: σ=0.01–0.02 room noise and PAST it at σ=0.05, so the gate must separate
#: those noise regimes, not pin the exact σ. The measured dof-adjusted
#: scatter of a σ=0.02 window (n≈21) lands 0.017–0.027 and a σ=0.05 window
#: 0.033–0.066, so 0.03 sits between the distributions with margin on both
#: sides — a gate at exactly 0.02 would refuse half the windows the
#: ratification priced as adoptable, and the "~" is that slack. A DESIGN
#: constant: it prices the fitted arm's noise ceiling, not a tuning knob.
MAX_FIT_RESIDUAL_SCATTER_C = 0.03


def slab_mode_tau_fast(c_r: float, c_s: float, k_s: float) -> float:
    """The slab-room fast mode's time constant, hours.

    One expression for the quantity the #991 gate, the two-state fit's
    published result and the tests all consume: the gate computes it from
    the CONFIG plant at arm time, the fitted arm re-derives it from the
    FITTED room capacity against the config slab pair. Zero when the
    constants are unset — the gate refuses that plant separately.
    """
    if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9):
        return 0.0
    return c_r * c_s / ((c_r + c_s) * k_s)


def slab_mode_identifiability(
    params: ThermalParameters, config: SysIdConfig
) -> tuple[bool, str]:
    """Whether the one-state fit can see this plant at all (#942).

    The plant the optimizer simulates is two-state: heat lands in the slab
    and the room sees only ``k_s·(T_s − T_r)``. ``identify()`` fits ONE
    state to it, which is honest exactly when the slab-room fast mode is
    quick against the protocol's own phases. The fit pools settle, step and
    relax rows, and every phase boundary re-excites the fast mode, so a
    mode that cannot settle within the SHORTEST phase is still visibly
    two-state everywhere the fit looks — the relax rows carry slab
    discharge that a one-state model can only explain with a negative UA,
    which is what the sign guards have been refusing, silently, on every
    preset this integration ships (tau_fast = C_r·C_s/((C_r+C_s)·k_s) is
    0.9–3.7 h against a shortest phase of 1 h). The gate names that at arm
    time and at adoption instead of letting the night burn and the guards
    stay mute; a plant whose slab coupling is fast enough (or a protocol
    with phases long enough — the deferred two-state estimator's wave)
    passes the same gate and adopts.
    """
    c_r = float(params.room_thermal_mass)
    c_s = float(params.slab_thermal_mass)
    k_s = float(params.slab_heat_transfer)
    window = config.settle_hours + config.step_hours + config.relax_hours
    settle_band = min(config.settle_hours, config.step_hours, config.relax_hours)
    if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9) or not settle_band > 1e-9:
        return False, (
            "slab constants not configured; the one-state fit cannot be "
            "interpreted on this plant"
        )
    tau_fast = slab_mode_tau_fast(c_r, c_s, k_s)
    if FAST_MODE_SETTLE_TAUS * tau_fast <= settle_band:
        return True, "ok"
    return False, (
        "slab mode too slow for the excitation window: tau_fast="
        f"{tau_fast:.2f} h needs {FAST_MODE_SETTLE_TAUS * tau_fast:.1f} h to "
        f"settle, but the shortest phase of the {window:.1f} h window is "
        f"{settle_band:.1f} h"
    )


def _simulate_slab_path(
    ua: float,
    room_cap: float,
    gains: float,
    slab_mass: float,
    slab_transfer: float,
    first_room_c: float,
    outdoor_c: np.ndarray,
    thermal_kw: np.ndarray,
    dt_hours: np.ndarray,
) -> np.ndarray:
    """Roll a candidate two-state plant over the recorded thermal power.

    The candidate is the production ``ThermalModel`` itself — the same
    object the optimizer simulates — with UA, room capacity and free heat
    free and the slab pair trusted from configuration. The slab's initial
    temperature is its steady offset under the candidate's own heat
    balance (the house held temperature before the experiment), and the
    room starts at the first recorded reading. Returns the predicted room
    series, one entry per recorded sample.
    """
    model = ThermalModel(
        ThermalParameters(
            heat_loss_coefficient=ua,
            house_heat_loss_scale=1.0,
            room_thermal_mass=room_cap,
            internal_gains=gains,
            slab_thermal_mass=slab_mass,
            slab_heat_transfer=slab_transfer,
            two_zone_enabled=False,
            wind_sensitivity=0.0,
        )
    )
    k_slab = max(slab_transfer, 1e-9)
    state = ThermalState(
        room_temperature=first_room_c,
        slab_temperature=first_room_c
        + (ua * (first_room_c - float(outdoor_c[0])) - gains) / k_slab,
        outdoor_temperature=float(outdoor_c[0]),
    )
    rooms = [state.room_temperature]
    for q, out, dt in zip(thermal_kw, outdoor_c, dt_hours):
        state = model.simulate_step(
            state,
            electrical_power=0.0,
            outdoor_temp=float(out),
            dt_hours=float(dt),
            external_heat_kw=float(q),
        )
        rooms.append(state.room_temperature)
    return np.asarray(rooms)


def _lm_solve(
    residual: Callable[[np.ndarray], np.ndarray],
    x0: np.ndarray,
    max_iter: int = 60,
) -> tuple[np.ndarray, float]:
    """Levenberg–Marquardt on a least-squares residual, in plain numpy.

    The integration runs on Home Assistant installs that do not ship
    scipy, so the two-state fit solves its own small (three-parameter)
    problem: forward-difference Jacobian, diagonal Marquardt damping,
    projection of the linear parameter into its loose band. Returns the
    best point found and its cost; convergence quality is pinned by the
    ensemble test, not by this function's iteration count.
    """
    x = np.asarray(x0, dtype=float).copy()
    value = residual(x)
    cost = float(value @ value)
    damping = 1e-2
    for _ in range(max_iter):
        jac = np.empty((value.size, x.size))
        for i in range(x.size):
            step = 1e-6 * max(abs(float(x[i])), 1.0)
            bumped = x.copy()
            bumped[i] += step
            jac[:, i] = (residual(bumped) - value) / step
        gram = jac.T @ jac
        gradient = jac.T @ value
        accepted = False
        for _attempt in range(10):
            try:
                delta = np.linalg.solve(
                    gram + damping * np.diag(np.diag(gram) + 1e-12), -gradient
                )
            except np.linalg.LinAlgError:
                damping *= 10.0
                continue
            candidate = x + delta
            candidate[2] = float(np.clip(candidate[2], -5.0, 10.0))
            next_value = residual(candidate)
            next_cost = float(next_value @ next_value)
            if np.isfinite(next_cost) and next_cost < cost:
                x, value, cost = candidate, next_value, next_cost
                damping = max(damping * 0.3, 1e-12)
                accepted = True
                break
            damping *= 10.0
        if not accepted or float(np.max(np.abs(delta))) < 1e-10:
            break
    return x, cost


def _slab_series(
    usable: list[SysIdSample],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray] | None:
    """The recorded series the two-state rollout needs, or None.

    ``None`` means fewer than five usable intervals — the one-state fit's
    own floor, so both fits refuse the same starvation.
    """
    rooms = np.asarray([s.room_temp for s in usable], dtype=float)
    outdoors = np.asarray([s.outdoor_temp for s in usable], dtype=float)
    powers = np.asarray([s.power_kw for s in usable], dtype=float)
    dts = np.asarray(
        [
            (b.when - a.when).total_seconds() / 3600.0
            for a, b in zip(usable, usable[1:])
        ],
        dtype=float,
    )
    if len(dts) < 5:
        return None
    return rooms, outdoors, powers, dts


def _slab_refusal(
    ua: float, room_cap: float, gains_kw: float, slab_mass: float
) -> SysIdResult | None:
    """The outcome guards the two-state fit shares with the one-state fit.

    Same bands, same reason strings as :meth:`SystemIdentification.identify`
    — the adoption surface must not move because the model class did.
    Returns the refusal, or ``None`` when the triple is acceptable (with
    the gains CLIPPED into their band, exactly as identify() clips).
    """
    if ua <= 1e-6 or room_cap <= 1e-6:
        return SysIdResult(completed=False, reason="fit gave implausible signs")
    if not (-0.5 <= gains_kw <= 2.0):
        return SysIdResult(
            completed=False, reason="fitted gains outside plausible bounds"
        )
    tau = (room_cap + slab_mass) / ua
    if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0):
        return SysIdResult(
            completed=False, reason="fitted parameters outside plausible bounds"
        )
    return None


def _slab_confidence(rooms: np.ndarray, error: np.ndarray) -> float:
    """Confidence for the two-state fit, mirroring identify()'s ingredients.

    R² of the room series, tempered by sample count, by the achieved
    excursion against the design allowance, and by the residual SNR — the
    nonlinear form's stand-in for the one-state noise gate until the wave
    rebuilds that program (a noisy window is discounted, not refused).
    """
    ss_res = float(np.sum(np.square(error)))
    tail = rooms[1:]
    ss_tot = float(np.sum(np.square(tail - np.mean(tail))))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-9 else 0.0
    confidence = float(np.clip(r2, 0.0, 1.0)) * min(1.0, len(error) / 12.0)
    excursion = float(np.max(rooms) - np.min(rooms))
    confidence *= float(np.clip(excursion / DEFAULT_MAX_EXCURSION_C, 0.3, 1.0))
    signal = float(np.percentile(rooms, 90) - np.percentile(rooms, 10))
    noise = float(np.sqrt(ss_res / max(len(error), 1)))
    snr = signal / max(noise, 1e-9)
    return confidence * float(np.clip((snr - 1.0) / 3.0, 0.0, 1.0))


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
        #: Slab pair (C_s, k_s) and initial-guess room pair (UA, C_r) from
        #: the plant declared at arm time, recorded ONLY when the #991
        #: identifiability gate passed on it. ``_finish`` routes the
        #: experiment to the two-state slab fit exactly when the pair is
        #: present, so the gate's refusals stay in front of the fit and a
        #: harness that declares no plant keeps the one-state regression.
        self._slab_pair: tuple[float, float] | None = None
        self._slab_prior: tuple[float, float] | None = None
        #: Whether the finished experiment's result came from
        #: :meth:`identify_slab` — the routing pin the wave's test reads.
        self._slab_fit_used: bool = False

    # -- control ------------------------------------------------------------

    @property
    def active(self) -> bool:
        return self.phase in (PHASE_ARMED, PHASE_SETTLING, PHASE_STEP, PHASE_RELAX)

    def arm(self, now: datetime, plant: ThermalParameters | None = None) -> bool:
        """Arm an experiment, to start when conditions allow.

        ``plant`` is the house the experiment would run on, when the caller
        knows it. #942's identifiability gate then refuses to arm on a plant
        whose slab mode is too slow for the excitation window — naming the
        reason into the result, so it is published — instead of burning the
        night to have the fit's guards refuse it silently. Callers that do
        not declare a plant (a harness driving a synthetic one) are not
        gated; production always declares it.
        """
        if not self.config.enabled:
            _LOGGER.info("System identification is disabled in the configuration")
            return False
        if self.active:
            return False
        self._slab_pair = None
        self._slab_prior = None
        self._slab_fit_used = False
        if plant is not None:
            identifiable, why = slab_mode_identifiability(plant, self.config)
            if not identifiable:
                _LOGGER.info("System identification not armed: %s", why)
                self.result = SysIdResult(completed=False, reason=why)
                return False
            # The gate passed: the experiment this plant runs may be fitted
            # in the two-state form, seeded from the plant's own figures.
            self._slab_pair = (
                float(plant.slab_thermal_mass),
                float(plant.slab_heat_transfer),
            )
            self._slab_prior = (
                float(plant.heat_loss_coefficient)
                * float(plant.house_heat_loss_scale),
                float(plant.room_thermal_mass),
            )
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
        slab_thermal_mass: float | None = None,
        slab_heat_transfer: float | None = None,
    ) -> float | None:
        """Largest electrical step whose predicted excursion fits the bound."""
        cfg = self.config
        cop = max(cop, 0.1)
        q_max = max_power_kw * cop
        # 0.01 kW thermal: the C=8 UA=0.35 kW/K needle is ~0.05 kW wide.
        # Binary search: each trial is a two-state rollout, not a closed form.
        lo = 0.0
        hi = q_max
        best: float | None = None
        plant = _sizing_model(ua, capacity, gains, slab_thermal_mass, slab_heat_transfer)
        peak_max, final_max = _predict_step_excursion_plant(
            ua,
            capacity,
            gains,
            baseline,
            outdoor_temp,
            q_max,
            cfg.step_hours,
            cfg.relax_hours,
            model=plant,
        )
        if peak_max <= cfg.max_excursion_c and final_max <= cfg.max_excursion_c:
            return max_power_kw
        while hi - lo > 0.01:
            q = (lo + hi) / 2.0
            peak, final = _predict_step_excursion_plant(
                ua,
                capacity,
                gains,
                baseline,
                outdoor_temp,
                q,
                cfg.step_hours,
                cfg.relax_hours,
                model=plant,
            )
            if peak <= cfg.max_excursion_c and final <= cfg.max_excursion_c:
                best = q / cop
                lo = q
            else:
                hi = q
        if best is not None:
            one_peak, _ = _predict_step_excursion(
                baseline,
                outdoor_temp,
                ua,
                capacity,
                gains,
                best * cop,
                cfg.step_hours,
                cfg.relax_hours,
            )
            _LOGGER.debug(
                "System identification sizer: two-state step %.2f kW; "
                "one-state exponential predicted %.2f K",
                best,
                one_peak,
            )
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
        house_slab_mass: float | None = None,
        house_slab_transfer: float | None = None,
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
                house_slab_mass,
                house_slab_transfer,
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
        house_slab_mass: float | None = None,
        house_slab_transfer: float | None = None,
    ) -> float | None:
        """Advance the experiment; returns a power override, or ``None``.

        ``None`` means "the optimizer's plan stands". A number overrides it for
        this interval, which is how the step is actually injected. The returned
        value is electrical power, because that is what the rest of the
        integration speaks; ``cop`` converts it to the thermal quantity the fit
        needs.

        The ``house_*`` figures are the coordinator's configured thermal
        parameters, the learned scale already folded into ``house_ua``. The
        sizer builds its plant from them, so a caller that omits the slab
        pair sizes on the ``ThermalParameters`` defaults instead of on the
        house it heats (#943).
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
                house_slab_mass,
                house_slab_transfer,
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
        # #942's wave: an experiment the arm-time gate admitted on a declared
        # plant is fitted in the two-state form (with the ported intercept
        # ridge); everything else — a harness that declared no plant — keeps
        # the one-state regression. The gate's refusals never reach here.
        if self._slab_pair is not None:
            self.result = self.identify_slab()
        else:
            self._slab_fit_used = False
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
        It is solved over settle, step and relax: settle is a known-input
        hour the step used to throw away; relax carries UA (no input to
        confound it); the step carries C.

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

        # R3-D2-03: the drift ridge shrinks d to ~0 at 0.02 °C of noise,
        # below a typical sensor's quantisation, and the ΔT column then
        # carries the ramp into UA. Rate residuals of that biased house
        # look clean. The tell is a settle long enough to have a
        # (Q+G)/ΔT instantaneous UA, disagreeing with the fit. A
        # two-row settle (the existing noise-free unbiasedness plant)
        # is skipped — that window never had the comparison.
        if (
            drift_c_per_h is not None
            and abs(drift_c_per_h) < self.config.sensor_drift_prior_c_per_h
            and gains_kw is not None
        ):
            settle = [s for s in usable if s.phase == PHASE_SETTLING]
            if len(settle) >= 3:
                last = settle[-1]
                den = last.room_temp - last.outdoor_temp
                if abs(den) > 1e-6:
                    ua_ss = (last.power_kw + gains_kw) / den
                    if ua_ss > 0.0 and abs(ua_ss - ua) / ua > 0.10:
                        return SysIdResult(
                            completed=False,
                            reason="sensor drift collapsed into heat-loss",
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

    def identify_slab(self) -> SysIdResult:
        """Fit the two-state plant the optimizer simulates (#942's wave).

        This is the fit that runs where the arm-time identifiability gate
        passed on a declared plant (see :meth:`_finish`): a candidate
        ``ThermalModel`` is rolled forward over the recorded thermal power
        (:func:`_simulate_slab_path`) and UA, the room capacity and the
        free heat are fitted by simulation-error least squares, with the
        slab pair TRUSTED from the declared plant — the ratified arm
        (#942 comment 5659441129: config-trusted today; the C_s/k_s split
        is structurally unidentifiable and is not this act's work).

        The D2-01 intercept ridge, ported: the comfort bound keeps the
        excursion — and so ΔT — within ~2 % of its mean, which leaves UA
        and G collinear; the unridged two-state fit is noise-wrecked at
        any σ (pre-study, comment 5656402482: −91/+112 % UA-bias p5/p95
        at σ=0.01 on the nightly window). ONE pseudo-observation
        ``(G − gains_prior_kw) / SLAB_INTERCEPT_PRIOR_SD_KW`` appended to
        the residual vector holds the intercept to its configured prior
        and lands the band at single digits (−6.7/+4.2 % ported).

        Deliberately absent, until the wave rebuilds them for the
        nonlinear form: the one-state program's D2-01 errors-in-variables
        correction, D2-07 drift column and R3-D2-03 settle cross-check.
        The outcome guards and the confidence ingredients mirror
        :meth:`identify` (R², sample count, achieved excursion, residual
        SNR) so the adoption surface — completed, confidence ≥ 0.3 and
        the #991 gate — is the same surface; and the wave's act 2 adds the
        ratified residual-scatter gate on top: a window whose own noise
        exceeds ``MAX_FIT_RESIDUAL_SCATTER_C`` is refused by name rather
        than discounted, because past that ceiling the same cell degrades
        outside the ±10 % bar the blend exists to beat.

        Reports the lumped equivalents a one-state consumer expects: UA
        (room-side), total capacity ``C_r + C_s`` and its time constant;
        no sensor-drift figure exists in this form. The slab mode's own
        time constant re-derives from the fitted capacity against the
        config pair and is published as ``slab_mode_tau_hours`` — the
        quantity the #996 config-class decision prices, never an adopted
        constant.
        """
        self._slab_fit_used = True
        if self._slab_pair is None or self._slab_prior is None:
            # Called without an arm-time plant (a harness replaying samples
            # directly): the one-state regression is what the pre-wave tree
            # ran on that path, and it stays what runs there.
            self._slab_fit_used = False
            return self.identify()
        usable = [
            s
            for s in self.samples
            if s.phase in (PHASE_SETTLING, PHASE_STEP, PHASE_RELAX)
        ]
        if len(usable) < 6:
            return SysIdResult(completed=False, reason="not enough samples")
        series = _slab_series(usable)
        if series is None:
            return SysIdResult(
                completed=False, reason="not enough usable intervals"
            )
        rooms, outdoors, powers, dts = series
        if bool(np.any((dts <= 1e-3) | (dts > 2.0))):
            # A cadence gap breaks the rollout's state chain; the one-state
            # regression tolerates gaps by skipping the interval, so the
            # experiment falls back to it rather than being discarded.
            self._slab_fit_used = False
            return self.identify()
        slab_mass, slab_transfer = self._slab_pair
        ua0, cr0 = self._slab_prior
        prior_g = self.config.gains_prior_kw

        def residual(x: np.ndarray) -> np.ndarray:
            predicted = _simulate_slab_path(
                float(np.exp(x[0])),
                float(np.exp(x[1])),
                float(x[2]),
                slab_mass,
                slab_transfer,
                float(rooms[0]),
                outdoors[:-1],
                powers[:-1],
                dts,
            )
            # The ported ridge itself: one pseudo-observation on G, weighed
            # against the whole room series through its width. Deleting
            # this append is the mutation the ensemble test flips on.
            return np.append(
                predicted[1:] - rooms[1:],
                (float(x[2]) - prior_g) / SLAB_INTERCEPT_PRIOR_SD_KW,
            )

        # Multi-start over the room-capacity decade: the cost surface has a
        # competing local minimum along C_r (measured while porting: a 3x
        # seed parked at −61 % UA noise-free where the true basin sits at
        # 0), and the declared plant's figures seed only one point of it.
        best_x: np.ndarray | None = None
        best_cost = float("inf")
        for mult in (1.0 / 3.0, 1.0, 3.0):
            x0 = np.array(
                [
                    np.log(max(ua0, 1e-3)),
                    np.log(max(cr0 * mult, 1e-2)),
                    prior_g,
                ]
            )
            x, cost = _lm_solve(residual, x0)
            if cost < best_cost:
                best_x, best_cost = x, cost
        if best_x is None or not bool(np.all(np.isfinite(best_x))):
            return SysIdResult(completed=False, reason="fit failed")
        return self._slab_outcome(
            best_x, rooms, outdoors, powers, dts, slab_mass, slab_transfer
        )

    def _slab_outcome(
        self,
        best_x: np.ndarray,
        rooms: np.ndarray,
        outdoors: np.ndarray,
        powers: np.ndarray,
        dts: np.ndarray,
        slab_mass: float,
        slab_transfer: float,
    ) -> SysIdResult:
        """Guard and package the converged two-state fit (the wave's act 2).

        Two things happen between the solver and the result, and both are
        the ratified hybrid's (#942, comment 5659441129) adoption
        preconditions rather than tuning: the residual-scatter noise gate,
        and the tau_fast re-derivation.
        """
        ua = float(np.exp(best_x[0]))
        room_cap = float(np.exp(best_x[1]))
        gains_kw = float(best_x[2])
        refusal = _slab_refusal(ua, room_cap, gains_kw, slab_mass)
        if refusal is not None:
            return refusal
        gains_kw = float(np.clip(gains_kw, 0.0, 2.0))
        capacity = room_cap + slab_mass
        predicted = _simulate_slab_path(
            ua,
            room_cap,
            gains_kw,
            slab_mass,
            slab_transfer,
            float(rooms[0]),
            outdoors[:-1],
            powers[:-1],
            dts,
        )
        error = predicted[1:] - rooms[1:]
        # The noise gate: the fitted values are adoptable only where the
        # window's own residual scatter clears the ratified ceiling — the
        # pre-study's frontier measured this same cell PAST the +-10 % UA
        # bar at sigma 0.05, so a window that noisy is refused BY NAME
        # instead of adopted at whatever confidence the SNR term leaves.
        # The scatter is dof-adjusted (three fitted parameters) so it
        # estimates the sensor noise rather than the fit's degrees of
        # freedom.
        n_error = int(error.size)
        scatter = float(
            np.sqrt(np.sum(np.square(error)) / max(n_error - 3, 1))
        )
        if scatter > MAX_FIT_RESIDUAL_SCATTER_C:
            return SysIdResult(
                completed=False,
                reason=(
                    f"residual scatter {scatter:.3f} C exceeds the "
                    f"{MAX_FIT_RESIDUAL_SCATTER_C:.2f} C noise gate for "
                    "fitted adoption; config-trusted"
                ),
            )
        # tau_fast re-derives from the fit. The split itself is never
        # adopted — see SysIdResult.slab_mode_tau_hours and the #996
        # decision it points at.
        return SysIdResult(
            completed=True,
            time_constant_hours=capacity / ua,
            heat_loss_kw_per_c=ua,
            thermal_mass_kwh_per_c=capacity,
            internal_gains_kw=gains_kw,
            sensor_drift_c_per_h=None,
            slab_mode_tau_hours=slab_mode_tau_fast(
                room_cap, slab_mass, slab_transfer
            ),
            confidence=_slab_confidence(rooms, error),
            reason="ok",
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "active": self.active,
            "samples": len(self.samples),
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "result": self.result.as_dict(),
        }
