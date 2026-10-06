"""Model Predictive Control optimizer for heat pump cost minimization.

Plans the heat pump's power schedule over the forecast horizon (24 h by
default, 15-minute steps) against forecast prices and weather, re-solved every
update interval with only the first step ever acted on.

**How the solve is structured.** Hot water is a deferrable on/off load, so it
is planned first by a linear program plus a cheapest-first repair against the
real tank simulation (`dhw_planner.DhwPlanner`); a gradient solver would
smear it into an unrealizable trickle. Space heating is then optimized around
the fixed DHW blocks by multi-start L-BFGS-B, and one co-optimization pass
re-plans hot water against the solved space profile where the two competed
for the compressor.

**What the space objective actually minimizes:**

    grid_cost(P_space + P_dhw)        piecewise in PV surplus, × price_weight
    + comfort terms                   pull-to-target, floor/ceiling penalties
    + (cycling + capacity tariff)     × price_weight
    + terminal cost                   value of heat stored at the horizon end

Every term but the comfort penalties is in currency. There used to be one more
— a `0.01 · Σ ΔP²` smoothness regulariser — and it was removed in v3.9.0
because it was priced in invented units and cost real money: about 5 % of the
two-zone winter bill, at no reduction in compressor starts. Discouraging
chatter is `cycling_cost`'s job, and that is denominated in currency per
start-stop cycle, so the trade against electricity is one the user can read.

subject to 0 ≤ P_space[k] ≤ P_max − P_dhw[k] (the pump can be off; values
below its modulation floor read as duty cycling within the step) and the
thermal dynamics of the configured model. Comfort bounds are soft penalties,
not constraints — a hard band could make a cold morning infeasible.

Weather anticipation is emergent rather than a separate term: the trajectory
simulation applies forecast solar gain and wind/rain loss factors at each
step, so heating before a sunny spell or coasting into a windy evening prices
itself.
"""
from __future__ import annotations

import importlib
import logging
import math
import time as _time_mod
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Any, Callable, Iterable

import numpy as np
from scipy.optimize import minimize

from . import mixing_valve, pv
from .const import (
    CONF_COMFORT_TEMP_DAY,
    CONF_COMFORT_TEMP_DAY_WEEKEND,
    CONF_COMFORT_TEMP_NIGHT,
    CONF_COMFORT_TEMP_NIGHT_WEEKEND,
    CONF_COMFORT_WEIGHT,
    CONF_DAY_END_HOUR,
    CONF_DAY_END_HOUR_WEEKEND,
    CONF_DAY_START_HOUR,
    CONF_DAY_START_HOUR_WEEKEND,
    CONF_HOLIDAY_COMFORT_DAY,
    CONF_HOLIDAY_COMFORT_NIGHT,
    CONF_HOLIDAY_DAY_END_HOUR,
    CONF_HOLIDAY_DAY_START_HOUR,
    CONF_MAX_TEMP,
    CONF_MIN_TEMP,
    CONF_PRICE_WEIGHT,
    CONF_TARGET_TEMP,
    DEFAULT_COMFORT_TEMP_DAY,
    DEFAULT_COMFORT_TEMP_NIGHT,
    DEFAULT_COMFORT_WEIGHT,
    DEFAULT_CYCLING_COST,
    DEFAULT_DAY_END_HOUR,
    DEFAULT_DAY_START_HOUR,
    DEFAULT_MAX_TEMP,
    DEFAULT_MIN_TEMP,
    DEFAULT_PRICE_RISK_LAMBDA,
    DEFAULT_PRICE_WEIGHT,
    DEFAULT_TARGET_TEMP,
    DHW_COOLING_REFERENCE_AMBIENT_TEMP,
    WOOD_TANK_MAX_TEMP,
)
from .batchmath import row_sums
from .dhw_planner import DhwPlanner
from .manual_plan import _pin_is_free
from .payload import CurrentAction
from .thermal_model import (
    TANK_ROOM_AMBIENT_TEMP,
    MIN_RUNNING_DRAW_KW,
    ThermalModel,
    ThermalParameters,
    ThermalState,
    WeatherSeries,
    _mean_humidity,
    _step_humidity,
    planned_draw_runs,
    planned_draws_run,
    weather_or_calm,
    wood_share,
)
from .tariff import (
    CapacityTariff,
    metering_windows,
    peak_cost,
    peak_cost_batch,
    peak_cost_smooth,
    plan_window_days,
    realised_peak,
    window_factors,
)
from .dhw_schedule import format_resolved_day_spec

_LOGGER = logging.getLogger(__name__)


def _padded_nonneg(values: Any, n_steps: int) -> np.ndarray:
    """A per-step series clipped at zero and fitted to the horizon: cut to
    ``n_steps``, or padded with zeros when the forecast is shorter."""
    head = np.clip(np.asarray(values, dtype=float), 0.0, None)[:n_steps]
    return np.pad(head, (0, n_steps - head.size))


def _padded_mask(mask: Any, n_steps: int) -> np.ndarray | None:
    """A per-step boolean mask fitted to the horizon, or ``None`` when empty.

    ``None`` when the input is ``None`` or marks no step at all, so a caller
    gating on it ("an off window in force") reads the absence of the window
    rather than an all-False array (#1910). Cut to ``n_steps`` like the
    series above; a short mask pads False — steps the caller never named
    are not in any window.
    """
    if mask is None:
        return None
    head = np.asarray(mask, dtype=bool)[:n_steps]
    head = np.pad(head, (0, n_steps - head.size))
    return head if bool(np.any(head)) else None


def _space_breach_due(
    power_caps_extra: np.ndarray | None,
    space_blocked: bool,
    off_steps: np.ndarray | None,
    n_steps: int,
) -> bool:
    """Whether the plan must publish the space floor-breach figure (#1910).

    True for an external cap, a blocked mode channel, or a quiet Off
    window: all three are the same question — how far below its floor did
    a bound the plan accepted push the house.
    """
    return (
        power_caps_extra is not None
        or space_blocked
        or _padded_mask(off_steps, n_steps) is not None
    )


def _publish_quiet_actions(
    result: OptimizationResult,
    quiet_actions: np.ndarray | None,
    n_steps: int,
) -> None:
    """The resolved per-step quiet action onto ``predictive_info`` (#1910).

    One int per step (0 none, 1 silent, 2 off), published only when a
    window was in force — absent entirely otherwise, which keeps every
    other install's payload byte-identical.
    """
    if quiet_actions is None:
        return
    result.predictive_info["quiet_actions"] = [
        int(a) for a in np.asarray(quiet_actions)[:n_steps]
    ]


def _holiday_flags_for(
    step_datetimes: list[datetime], holiday_dates: frozenset[date]
) -> np.ndarray | None:
    if not holiday_dates:
        return None
    return np.array(
        [False] + [d.date() in holiday_dates for d in step_datetimes]
    )


def _dhw_step_weekdays(
    params: ThermalParameters,
    step_datetimes: list[datetime],
    dt: float,
) -> np.ndarray | None:
    """The weekday array weekly DHW windows and per-day overrides need.

    ``None`` when neither is configured -- the flat, no-override install
    every entry was before either feature -- so nothing downstream pays for
    it. The array carries n+1 entries: entry i is the weekday of the step
    BEFORE step i (the pre-horizon step for i=0), entry i+1 the weekday of
    step i itself -- the two lookups the window-start edge test needs,
    without re-deriving datetimes inside the builder.
    """
    if (
        params.dhw_weekly_windows is None
        and params.dhw_day_windows is None
    ):
        return None
    return np.array(
        [(step_datetimes[0] - timedelta(hours=dt)).weekday()]
        + [d.weekday() for d in step_datetimes]
    )


def _dhw_resolved_publish(params: ThermalParameters) -> dict[str, Any]:
    """The resolved day-aware spec for ``predictive_info``, or nothing.

    #1260: present ONLY when a per-day override is in force, so the payload
    is byte-for-byte what it was before the feature otherwise and the card
    keeps reading the configured spec. Holiday windows stay out -- they
    resolve by date, this grammar by weekday, and the card's band reads the
    weekday schedule today too.
    """
    if not params.dhw_day_windows:
        return {}
    return {
        "dhw_windows_resolved": format_resolved_day_spec(
            params.dhw_weekly_windows,
            params.dhw_windows,
            params.dhw_day_windows,
        )
    }


def _utc_step_starts(
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


def _baseline_power_list(baseline_power: np.ndarray | None) -> list[float]:
    if baseline_power is None:
        return []
    return [float(v) for v in np.asarray(baseline_power, dtype=float)]


# The comfort penalty on breaching the user's minimum temperature is quadratic,
# which means its gradient vanishes as the violation approaches zero: a 0.05 C
# breach costs almost nothing while the electricity it saves is worth real
# money, so the solver settles just under the bound. Adding a small linear term
# gives the penalty a non-zero slope at the boundary, which is the standard
# exact penalty construction and pins the trajectory to the floor instead of
# just below it. Tuned to the smallest value that removes the residual
# violations across the validation scenarios; larger values buy nothing and
# start holding a wasteful margin above the floor.
_COMFORT_FLOOR_L1 = 2.0

# Strength of the pull towards the comfort *target*, as distinct from the
# penalty for breaching the user's *bounds*. Halved in v3.9.0 after measuring
# what the old strength cost: on the winter scenario the plan spent 28.55 SEK
# instead of 23.28 -- 18 % of the bill -- buying an average 0.32 K of warmth
# above what the band required, while never coming near the floor. Below half
# the saving plateaus (23.28 at every lower value tested), so this is the point
# where the money stops improving and a real preference for the setpoint is
# still expressed. The two-zone figure is half again because that branch
# averages two zones rather than summing them.
_COMFORT_PULL_SINGLE_ZONE = 0.025
_COMFORT_PULL_TWO_ZONE = 0.0125

# Every candidate the seam is handed is refined; the refined count is derived
# from the candidate list itself, not from a separate constant. A fixed cut
# used to sit here (_MULTI_START_SOLVES = 4) and, per the comment R1-D0-02
# then carried, "every candidate is now refined" -- an invariant a later fix
# in the same class silently broke: #1295's warm start hands a FIFTH candidate
# on every production cycle, and the cut discarded the worst-scoring
# structural seed (R6 D0-02, #1378, measured at 80/80 cells). The extra
# refinement is one short L-BFGS-B run of a lead that converges almost
# immediately, and the stress gate's per-scenario budgets police the runtime,
# exactly as they did for the 2->4 raise.

# The low-energy bang-bang seed (R1-D0-01): the historical candidates all
# anchored to the same TOTAL energy (the baseline's), and on
# arbitrage-structured prices all three refined into one basin -- measured
# by the audit at a 0.52-0.55 energy-fraction cluster, leaving strictly
# cheaper comfort-feasible plans unfound (1.1-1.6 % net on adversarial
# shapes, with a different step-0 action so MPC re-planning does not mask
# it). This seed buys only the cheapest ~35 % of that energy: a genuinely
# different basin the solver can climb out of cheaply when comfort wants
# more, but which wins outright when pre-heating less is the better plan.
_LOW_ENERGY_START_FRACTION = 0.35

# The deep low-energy bang-bang seed (round 7 D0-01, #1447). The seed above
# brackets the two-store shape; on the default two-zone winter cell it does
# not bracket the OPTIMUM, which sits below both anchors: measured, the
# objective's best point is at 0.20x the baseline energy (77.543533 against
# production's 77.884228, 0.4374 % of the shipped objective, 1.060 SEK/day),
# and the 0.35x seed is not merely unhelpful there -- refined it lands at
# 79.12, a worse basin than the shipped plan, and the smooth/baseline/1.0x
# seeds all refine into the ~77.88 basin. Pre-heating less and buying the
# shortfall later is cheaper because the day's price curve is steeper than
# the stores' round-trip loss. Under-heating is a priced decision, not a
# comfort one: the anchor is climbed out of at no comfort cost (0.0
# degree-steps of floor violation on both arms of the harness), and at flat
# prices the same seed stops beating production (gap 0.0000 %), which is the
# null control separating a price gap from a comfort or cycling artefact.
# The 0.20 fraction is the ladder's measured winner, not a fitted value: the
# 0.10 anchor does not beat it on the cell the harness drives.
#
# TWO-ZONE ONLY, and the reach is the point. The anchor is appended in
# `_optimize_space_only` only under `two_zone_enabled`, because the
# single-zone plan is the state the solve certificate's recorded claims are
# calibrated on and this seed moves it to a different local optimum on some
# runners and not others: measured, the certificate's own grid reads
# `one|shoulder|winter_cold`'s ladder gap at 0.73 % here and closed on CI's
# runner, which is a claim that can be neither kept nor withdrawn. Restricting
# the reach leaves every single-zone solve byte-identical, so those claims keep
# their calibration, and the finding's own fix scope asks for the two-zone
# path. The two-zone cell carries the same portability limit and states it
# where it is measured -- see `_CERT_BARS` in tests/optimality.py.
_DEEP_LOW_ENERGY_START_FRACTION = 0.20

# Resolved by name, not imported: threadpoolctl publishes no py.typed and no
# stub distribution exists, so a static import is an `import-untyped` error
# with no annotation that reaches it -- while the try/except below already
# says this dependency is optional and looked up at runtime.
try:  # pragma: no cover - present via the manifest requirement
    _threadpool_limits: Any = importlib.import_module(
        "threadpoolctl"
    ).threadpool_limits
except (ImportError, AttributeError):  # bare test imports without the requirement
    _threadpool_limits = None


def _scoped_minimize(*args: Any, **kwargs: Any) -> Any:
    """``minimize`` with BLAS threads pinned to one for the call's duration.

    The arrays here are 96 steps, far below any threshold where BLAS
    parallelism repays its synchronisation, and the unscoped pool sized to
    the machine's core count spent ~21% of solve CPU spinning (issue #88) --
    CPU a Raspberry-Pi-class host running all of Home Assistant does not
    have. Scoped to the call and never process-wide, because other
    components share this interpreter; a bare environment-variable set would
    be both process-wide and too late (numpy is long since imported).
    Identical results by construction: no operation at these sizes is
    threaded, which is precisely why the threads were pure overhead.
    """
    if _threadpool_limits is None:
        return minimize(*args, **kwargs)
    with _threadpool_limits(limits=1):
        return minimize(*args, **kwargs)


def _batch_fd_gradient(
    batch_objective: Callable[..., Any],
    args: tuple[Any, ...],
    x0: np.ndarray,
    f0: float | None,
    eps: float,
    bounds: list[tuple[float, float]],
) -> np.ndarray:
    """The gradient scipy would estimate itself -- computed as ONE batch.

    Replicates, exactly, what ``approx_derivative`` does for L-BFGS-B with
    ``jac=None`` and the ``eps`` option: a 2-point forward difference with
    the absolute step ``eps``, adjusted one-sided at the bounds by
    scipy's own rule (flip the step when it fits; otherwise take the full
    distance to the roomier side), and the division ``((x0+h)-x0)`` on
    the same footing. Byte-identical to scipy's estimate wherever the
    batched objective's rows are byte-identical to the scalar one --
    which is the batched simulation's contract (issue #97).

    The 97 perturbed schedules are evaluated by ONE call to
    ``batch_objective``: the simulation, which is nearly the whole cost,
    runs vectorized across the batch instead of 97 times sequentially.

    A FIXED variable (``lb == ub``) is the one place this deliberately
    departs from scipy (D9-01): there the one-sided rule leaves a zero step
    and scipy's own divided difference is 0/0 = NaN. That NaN is not a
    derivative, it is an artefact of dividing by a step the bounds forbade,
    and the true derivative of a variable that cannot move is 0.0 -- which
    is what this returns. It matters because scipy survives its own NaN
    only by accident (its first Fortran evaluation lands one ULP off the
    pin, x=4.44e-16 against a (0, 0) bound, turning 0/0 into -0.0), while a
    NaN arriving in a SUPPLIED jac kills L-BFGS-B in the first line search
    at status 2, nit 0. Free variables are untouched: their entries are
    still bit-for-bit scipy's, asserted per variable by
    ``tests/features.py::_grad_parity``.

    ``f0=None`` puts ``x0`` itself at the head of the batch as row 0 and
    differences against that row, so a caller that needs ``f(x0)`` as well
    reads it from the same batch instead of the scalar objective
    (``_fused_value_and_gradient``, R9 D9-s1-02).
    """
    h, free = _fd_steps(x0, eps, bounds)
    lead = 1 if f0 is None else 0
    f = batch_objective(_fd_rows(x0, h, lead), *args)
    if f0 is None:
        f0 = float(f[0])
    return _fd_divide(f[lead:], f0, x0, h, free)


def _fd_steps(
    x0: np.ndarray, eps: float, bounds: list[tuple[float, float]],
) -> tuple[np.ndarray, np.ndarray]:
    """scipy's 2-point steps for ``x0`` under ``bounds``, and which are free."""
    n = x0.size
    lb = np.array([b[0] for b in bounds], dtype=float)
    ub = np.array([b[1] for b in bounds], dtype=float)
    free = lb < ub
    h = np.full(n, eps, dtype=float)
    # scipy's zero-step fallback, replicated (issue #97): when x0 + eps
    # lands on the same float -- a zero-range bound, which the with-DHW
    # solve produces for space heating inside a full DHW block -- scipy
    # falls back to a relative step of sqrt(machine eps). Without this
    # the difference is 0/0 NaN and the iterate path diverges.
    sign_x0 = (x0 >= 0).astype(float) * 2 - 1
    dx_probe = (x0 + h) - x0
    h = np.where(
        dx_probe == 0,
        np.finfo(np.float64).eps ** 0.5 * sign_x0 * np.maximum(1.0, np.abs(x0)),
        h,
    )
    lower_dist = x0 - lb
    upper_dist = ub - x0
    x = x0 + h
    violated = (x < lb) | (x > ub)
    fitting = np.abs(h) <= np.maximum(lower_dist, upper_dist)
    h[violated & fitting] *= -1
    forward = (upper_dist >= lower_dist) & ~fitting
    h[forward] = upper_dist[forward]
    backward = (upper_dist < lower_dist) & ~fitting
    h[backward] = -lower_dist[backward]
    return h, free


def _fd_rows(x0: np.ndarray, h: np.ndarray, lead: int) -> np.ndarray:
    """``lead`` copies of ``x0``, then ``x0`` with each variable stepped by ``h``."""
    n = x0.size
    rows = np.tile(x0, (lead + n, 1))
    rows[lead + np.arange(n), np.arange(n)] = x0 + h
    return rows


def _fd_divide(
    f: np.ndarray, f0: float, x0: np.ndarray, h: np.ndarray, free: np.ndarray,
) -> np.ndarray:
    """The divided differences of the stepped rows' values against ``f0``."""
    dx = (x0 + h) - x0
    # ``where=free`` leaves the fixed entries at the 0.0 they start as and
    # never performs their division, so no 0/0 is computed and no invalid-
    # value warning is raised. On an all-free bound set this is elementwise
    # the same IEEE division as before, bit for bit.
    grad = np.zeros(x0.size, dtype=float)
    np.divide(f - f0, dx, out=grad, where=free)
    return grad


def _fused_value_and_gradient(
    batch_objective: Callable[..., Any],
    bounds: list[tuple[float, float]],
    fd_eps: float,
) -> Callable[..., tuple[float, np.ndarray]]:
    """An L-BFGS-B ``fun`` for ``jac=True``: ``f(x)`` and its gradient, one batch.

    L-BFGS-B asks for the value and the gradient at every point it visits.
    Taking the value from the scalar objective cost ~19-26x a batched row,
    9-19 % of the solve (R9 D9-s1-02); here it is one extra row, ``x``
    itself, at the head of the gradient's batch. The batched rows are
    bitwise the scalar objective (the batched simulation's contract, #97),
    so the value, the gradient and the iterate path are the ones the scalar
    value produced.
    """
    def value_and_gradient(x: np.ndarray, *a: Any) -> tuple[float, np.ndarray]:
        _gil_yield()
        values: list[float] = []

        def centred(rows: np.ndarray, *b: Any) -> Any:
            out = batch_objective(rows, *b)
            values.append(float(out[0]))
            return out

        grad = _batch_fd_gradient(centred, a, x, None, fd_eps, bounds)
        return values[-1], grad

    return value_and_gradient


def _bounds_supported_by_batch(bounds: list[tuple[float, float]]) -> bool:
    """Whether the batched jac may serve a solve with these bounds.

    The batched finite-difference gradient (``_batch_fd_gradient``) is a
    vectorized replica of scipy's own 2-point ``approx_derivative``. Where it
    serves a solve, it is bitwise-identical to scipy's estimate on every jac
    evaluation -- verified directly at uniform, per-step-capped and
    DHW-pinned-headroom bounds, and end-to-end by the schedule race in
    ``tests/optimality.py``. Serving those shapes is the point of D9-01: any
    DHW block pins the space bounds unevenly, so the old uniform-bounds-only
    gate left the fast path unreachable for real users (38 of 39 DHW-enabled
    golden scenarios; the default two-zone DHW solve was 941,472
    simulate_step calls, x40 the batched cost).

    A zero-range entry (``lo == hi``) used to be carved out here, and that
    carve-out was the whole of D9-01: ONE such bound anywhere in the vector
    put the WHOLE solve back on scipy's scalar finite differences, at 9,220
    simulate-step equivalents per gradient against 293 batched -- 31.5x, and
    2.7 M simulate_step calls for a solve that costs 81 k. It is not an
    exotic shape: a single-phase 16 A fuse guard caps a default 5 kW pump
    below its own 4.0 kW hot-water run power, so space heating inside a DHW
    block gets (0, 0); so do fuse-minus-house-load, the monthly fuse
    advisor's shadow solve, and a one-slot manual plan (23 forced-off steps).

    The carve-out existed because at such a variable the one-sided rule takes
    a zero step and the divided difference is 0/0 = NaN, and a NaN in a
    SUPPLIED jac kills L-BFGS-B in its first line search (status 2, nit 0)
    where scipy's own estimator survives on an accident -- its first Fortran
    evaluation lands one ULP off the pin (x=4.44e-16 against a (0, 0) bound),
    turning 0/0 into -0.0. The answer is to remove the NaN rather than the
    fast path: ``_batch_fd_gradient`` now returns an exact 0.0 at a fixed
    variable, which is that variable's true derivative, and the solve
    converges to the same point the scalar path reached (executed on the
    fuse-guard shape: fev_per_jev 96.0 -> 1.00).

    ``lo > hi`` and non-finite bounds are still refused: L-BFGS-B could not
    solve those on any path. This function stays the single, documented gate,
    so any bound class that ever proves impossible to serve has exactly one
    place to be carved out and explained.
    """
    if not bounds:
        return False
    for lo, hi in bounds:
        if not (np.isfinite(lo) and np.isfinite(hi)):
            return False
        if lo > hi:
            return False
    return True


#: Adopt the restart only when it beats the prior by a real relative drop.
#: L-BFGS-B's own ``ftol`` is 1e-6. Keeping every ``score < prior`` tick
#: re-planned 15 of 51 stress scenarios and left the work check under its
#: 40-of-51 floor. 1e-4 still moved different golden fixtures on Linux
#: 3.13 vs 3.14, so a claim list cannot be true on both. 2e-2 sat above
#: the largest Darwin golden keep -- and, it turned out, above every real
#: improvement the restart finds on the gate's own populations: the polish
#: was computed and thrown away whole, up to 1.17% of the objective and
#: 6% of a day's bill (round 5 D0-01, #1207). 2e-5 sits in the widest
#: measured quiet band of the polished-improvement distribution (every
#: restart's polished score, hooked at ``_scoped_minimize``, over the 50
#: golden solves at this merge base): the distribution is empty from
#: 4.83e-6 to 3.67e-5 -- 2e-5's nearest neighbours are 4.1x below it and
#: 1.8x above -- so no fixture's adoption decision can flip on
#: last-decimal drift the way 1e-4's did. It keeps every gap the round-5
#: finding counted (smallest: 1.34e-4, worst: 1.17e-2) and stays 20x
#: over the 1e-6 ftol tick the features pin refuses. No new seed.
#: (Landed by the owner directive of 2026-09-20, #1207 comment c1329fe /
#: database id 5750296026, via #1208's scoped may-drift path.)
_LBFGSB_RESTART_KEEP_REL = 2e-5


def _lbfgsb_restart(
    best: Any,
    objective: Callable[..., float],
    bounds: list[tuple[float, float]],
    args: tuple[Any, ...],
    maxiter: int,
    batch_objective: Callable[..., Any] | None,
    fd_eps: float,
) -> Any:
    """Restart L-BFGS-B from its own returned point. No new seed (#826)."""
    _time_mod.sleep(0.002)
    fun: Callable[..., Any] = objective
    jac: bool | None = None
    if batch_objective is not None and _bounds_supported_by_batch(bounds):
        fun, jac = _fused_value_and_gradient(batch_objective, bounds, fd_eps), True
    try:
        polished = _scoped_minimize(
            fun,
            np.asarray(best.x, dtype=float),
            args=args,
            jac=jac,
            method="L-BFGS-B",
            bounds=bounds,
            options={"maxiter": maxiter, "ftol": 1e-6, "eps": 1e-4},
        )
    except Exception:  # pragma: no cover - solver blow-up
        return best
    score = float(objective(polished.x, *args))
    prior = float(objective(best.x, *args))
    scale = max(abs(prior), 1e-12)
    if np.isfinite(score) and (prior - score) > _LBFGSB_RESTART_KEEP_REL * scale:
        return polished
    return best


def _gil_yield() -> None:
    """Release the GIL for one scheduler tick, from INSIDE a solve.

    A single L-BFGS-B run is tens of milliseconds of contiguous Python (each
    objective evaluation simulates the horizon, each batched gradient runs one
    vectorized batch), so it holds the GIL even on an executor thread and
    starves a co-located event loop. The between-run ``sleep``s cannot bound
    that hold: they sit *between* runs, and the gap is set by the longest
    run, not by what happens between runs (round 6 D9-01). A zero-length
    sleep drops and re-acquires the GIL with no measurable delay, which is
    exactly the yield a loop's 1 ms heartbeat needs, and it changes no
    number. Inert on the shipped path, where the solve runs in a separate
    interpreter, but that path does not need the yield.
    """
    _time_mod.sleep(0)


def _multi_start_minimize(
    objective: Callable[..., float],
    candidates: list[np.ndarray],
    bounds: list[tuple[float, float]],
    args: tuple[Any, ...] = (),
    maxiter: int = 300,
    batch_objective: Callable[..., Any] | None = None,
    fd_eps: float = 1e-4,
    move_starts: Callable[[list[np.ndarray], int], list[np.ndarray]] = (
        lambda candidates, maxiter: candidates
    ),
) -> Any:
    """Run L-BFGS-B from several starting points and keep the best result.

    The space heating objective is not convex: the comfort penalty is only
    active on one side of the temperature band, and the price signal creates
    several distinct "charge here, coast there" patterns that are each locally
    optimal. A gradient method started from a single guess can therefore stop
    at a schedule that random perturbation can beat, which is exactly what the
    two-zone case showed.

    Rather than pay for a full solve from every candidate at full cost, the
    candidates are first scored on the objective directly, which is cheap, and
    every candidate is then refined (the fixed refinement cut was removed --
    see the note beside the seed constants above). Scoring only ranks the
    candidates; the cross-candidate minimum below is what ships.

    The one-entry memo (#288) holds the last scalar value computed at an
    ``x``, so scoring a point scipy last evaluated re-evaluates nothing on
    the unbatched path. ``args`` is fixed for this call, so the key is ``x``
    alone.
    """
    # A caller's continuation moves its starts under this call's own
    # iteration budget, so a cut budget reaches it too (R9-F2.1).
    candidates = move_starts(list(candidates), maxiter)
    _raw_objective = objective
    _memo_key = None
    _memo_val = None

    def memoized(x: np.ndarray, *a: Any) -> float:
        nonlocal _memo_key, _memo_val
        _gil_yield()
        key = np.asarray(x, dtype=float).tobytes()
        if key != _memo_key:
            _memo_key = key
            _memo_val = float(_raw_objective(x, *a))
        return _memo_val

    scored = []
    for guess in candidates:
        try:
            score = float(memoized(guess, *args))
        except Exception:
            continue
        if np.isfinite(score):
            scored.append((score, guess))
    if not scored:
        raise ValueError("no usable starting point")
    scored.sort(key=lambda item: item[0])

    best = None
    best_score = np.inf
    last_error: Exception | None = None
    for solve_index, (_, guess) in enumerate(scored):
        if solve_index:
            # Timing only, between consecutive starts: each L-BFGS-B run is
            # Python-heavy and holds the GIL even from an executor thread,
            # so on the weak hardware Home Assistant usually runs on a long
            # solve starves the event loop and the whole instance reads as
            # frozen. A short sleep releases the GIL so the loop keeps
            # breathing. No effect on any numerical result.
            _time_mod.sleep(0.002)
        try:
            fun: Callable[..., Any] = memoized
            jac: bool | None = None
            # The batched jac (#97, widened by D9-01) serves NON-UNIFORM
            # bounds, which is where the cost actually is: DHW is on by
            # default, and any DHW block or per-step power cap pins the space
            # bounds unevenly, so the old uniform-bounds-only gate left 38 of
            # 39 DHW-enabled golden scenarios on the scalar scipy-FD path --
            # the batched gradient effectively never reached real users
            # (winter_two_zone_dhw: 941,472 simulate_step per solve, x40).
            #
            # ``_batch_fd_gradient`` replicates scipy's own 2-point
            # ``approx_derivative`` (abs_step=eps, the exact settings
            # L-BFGS-B passes) PER VARIABLE, including the one-sided bounds
            # rule and the zero-step fallback, so where it serves a solve the
            # iterate path does not move: asserted per-variable by
            # tests/features.py::_grad_parity (uniform, capped and
            # DHW-pinned-headroom bounds) and raced end-to-end by
            # tests/optimality.py on DHW-enabled solves. A FIXED variable
            # (lb == ub) is served too, since D9-01: it gets an exact 0.0
            # rather than scipy's 0/0 NaN, which is the only entry that ever
            # differs and the only one whose value the bounds already decide.
            # It used to disqualify the whole vector, which is what put a
            # fuse-guarded install on the scalar path at 31.5x. The CI drift
            # gate on Linux is the final arbiter.
            can_batch = _bounds_supported_by_batch(bounds)
            if batch_objective is not None and can_batch:
                # The batched-FD jac (#97): scipy calls the gradient at
                # every trial point, so a supplied jac removes 96/97 of
                # ALL evaluations, not just of the gradient's own. It
                # reproduces scipy's own 2-point estimate to the bit --
                # same eps, same bounds rule -- so on bounds with no fixed
                # variable the iterate path, and therefore the plan, does
                # not move. The value rides in the same batch (R9
                # D9-s1-02), so L-BFGS-B makes no scalar evaluation.
                fun = _fused_value_and_gradient(batch_objective, bounds, fd_eps)
                jac = True
            res = _scoped_minimize(
                fun,
                guess,
                args=args,
                jac=jac,
                method="L-BFGS-B",
                bounds=bounds,
                options={"maxiter": maxiter, "ftol": 1e-6, "eps": 1e-4},
            )
        except Exception as err:  # pragma: no cover - solver blow-up
            last_error = err
            continue
        # Polish EVERY solved candidate, here inside the loop (#1208, round
        # 5 D0-02; owner override 2026-09-20, comment eb3540c1: the
        # unbounded form). The restart used to run once, on the raw-best
        # result after the loop, so a candidate whose own polish would have
        # dropped below that result never got one: measured on the round-5
        # grid, production shipped up to 1.40% above the best its own code
        # reaches from the same candidates. The cross-candidate minimum below
        # is what ships.
        #
        # The restart stops on its own convergence, not on the budget handed
        # in here. Round 7 D9-02 (#1463) measured the polish at 0.4-0.6 of a
        # main run and ~35% of the solve, refuting the "one short L-BFGS-B
        # run per candidate" this comment used to claim, and priced every cut
        # of it -- a maxiter cap, a cap at the main run's own nit, polishing
        # only the best-scoring candidates, a looser polish ftol -- each of
        # which moves the shipped plan. The cost is what the 1.40% is bought
        # with; the stress gate's per-scenario CPU budgets police it.
        res = _lbfgsb_restart(
            res, memoized, bounds, args, maxiter, batch_objective, fd_eps,
        )
        score = float(memoized(res.x, *args))
        if np.isfinite(score) and score < best_score:
            best, best_score = res, score
    if best is None:
        raise last_error or ValueError("all starting points failed")
    return best


#: Below this horizon-mean price (SEK/kWh) the smooth guess's normalisation
#: is meaningless: a negative mean flips its sign — the cheapest (most
#: negative) steps clip to the LOW floor and the guess starts inverted — and
#: a near-zero mean divides by ~1e-6 and saturates the clip into bang-bang
#: at arbitrary steps. Real Nordic spring days do average below zero.
PRICE_MEAN_GUESS_EPS = 1e-3


def _price_guess_weights(prices: np.ndarray) -> np.ndarray:
    """Per-step initial-guess weight in [0.2, 1.0], high where cheap.

    On any meaningfully positive horizon mean this is the historical smooth
    mean-normalised guess, arithmetic untouched so every normal solve starts
    from bit-identical floats. Otherwise the same [0.2, 1.0] band is filled
    by price rank — relative ordering is all the guess exists to encode, and
    ranks keep it under any sign or scale. Shift-by-min would not: it warps
    the relative spacing the clip band then quantises.
    """
    if float(np.mean(prices)) > PRICE_MEAN_GUESS_EPS:
        smooth: np.ndarray = np.clip(1.5 - prices / (np.mean(prices) + 1e-6), 0.2, 1.0)
        return smooth
    ranks = np.argsort(np.argsort(prices)).astype(float)
    return 1.0 - 0.8 * ranks / float(max(len(prices) - 1, 1))


def _cap_tighten_starts(
    prev: np.ndarray,
    power_caps: np.ndarray,
    prices: np.ndarray,
    dt: float,
    p_max: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Starting points for a buffer-cap re-solve (#234)."""
    clipped = np.minimum(np.asarray(prev, dtype=float), power_caps)
    energy = float(np.sum(clipped) * dt)
    bang_bang = np.minimum(
        _price_ranked_start(prices, energy, p_max, dt), power_caps
    )
    return clipped, bang_bang


def _better_objective(
    left: OptimizationResult, right: OptimizationResult
) -> OptimizationResult:
    """The plan with the lower finite objective; ties keep ``left``."""
    lo = float(left.objective_value)
    ro = float(right.objective_value)
    if np.isfinite(ro) and (not np.isfinite(lo) or ro < lo - 1e-9):
        return right
    return left


def _price_ranked_start(
    prices: np.ndarray, energy_kwh: float, p_max: float, dt: float
) -> np.ndarray:
    """A bang-bang schedule that buys the cheapest steps first.

    This is the shape a cost-minimal plan takes when comfort is not binding,
    and it is structurally very different from the smooth price-weighted guess,
    which is what makes it useful as a second starting point.
    """
    schedule = np.zeros_like(prices, dtype=float)
    if energy_kwh <= 0 or p_max <= 0 or dt <= 0:
        return schedule
    remaining = float(energy_kwh)
    for idx in np.argsort(prices):
        if remaining <= 0:
            break
        take = min(p_max, remaining / dt)
        schedule[idx] = take
        remaining -= take * dt
    return schedule


def _savings_percentage(savings: float, baseline_cost: float) -> float:
    """Savings as a percentage of the baseline, clamped to a sensible range.

    A baseline at or near zero (a warm day where a thermostat would barely run)
    would otherwise turn rounding noise into a huge percentage.
    """
    if baseline_cost <= 0.01:
        return 0.0
    return float(np.clip(savings / baseline_cost * 100.0, -100.0, 100.0))


# ---------------------------------------------------------------------------
# Compressor cycling and capacity tariff
# ---------------------------------------------------------------------------


# Below this a pump's modulation band is too narrow to grade a step by: a
# fixed-speed pump (min == max power) is either off or at its one power.
_MIN_MODULATION_BAND_KW = 0.1


def _power_fraction(power: float, params: ThermalParameters) -> float:
    """Where a planned power sits in the pump's modulation band, in [0, 1].

    The one normalisation the setpoint, displace and action sites share. Four
    inline copies floored a zero band at 0.1 kW, which on a fixed-speed pump
    read a full-power step as 0 and an idle one as -60, and the published one
    did not clip (R9 D12-s2-03). With no band to grade, a step is graded
    against the pump's one running power instead.
    """
    p_min = params.min_electrical_power
    p_max = params.max_electrical_power
    if p_max - p_min >= _MIN_MODULATION_BAND_KW:
        low, band = p_min, p_max - p_min
    elif p_max > 0:
        low, band = 0.0, p_max
    else:
        return 0.0
    return float(min(1.0, max(0.0, (power - low) / band)))


def count_compressor_starts(
    power: np.ndarray, threshold: float = MIN_RUNNING_DRAW_KW
) -> int:
    """Number of off→on transitions in a schedule.

    Measurement first: the backlog note for this feature was explicit that a
    cycling penalty should only be paid for if realistic plans actually
    chatter. This is what the validation harness reports, and it is published
    on the result so the question stays answerable after the fact.

    The default is the plan's own running rule (``MIN_RUNNING_DRAW_KW``, and
    ``planned_draws_run`` is the same comparison), so the count this publishes
    and the on schedule beside it on the same result cannot disagree about
    which steps ran (R9 D12-s2-01).
    """
    running = np.asarray(power, dtype=float) > threshold
    if running.size == 0:
        return 0
    starts = int(running[0])
    starts += int(np.sum(running[1:] & ~running[:-1]))
    return starts


#: numpy's pairwise-summation block: a reduction longer than this is split in
#: two (at a multiple of 8) and each half summed on its own.


def cycling_penalty(
    power: np.ndarray, cost_per_cycle: float, p_max: float
) -> float:
    """Smooth stand-in for a per-start cost.

    ``sum |ΔP|`` over the schedule counts total power swing. One complete
    start-stop cycle at full power contributes ``2·p_max``, so dividing by that
    expresses the L1 term in units of whole cycles and makes ``cost_per_cycle``
    mean what its name says. The one-row case of ``cycling_penalty_batch``.
    """
    return float(cycling_penalty_batch(
        np.asarray(power, dtype=float)[None, :], cost_per_cycle, p_max
    )[0])


def cycling_penalty_batch(
    power_matrix: np.ndarray, cost_per_cycle: float, p_max: float
) -> np.ndarray:
    """``cycling_penalty`` for a [B, n] batch of plans, one entry per row (#948).

    The swings are elementwise and ``row_sums`` reduces them in numpy's own
    order, so each row is the scalar penalty bit for bit on every backend
    without a per-row interpreter loop (RC-sw1).
    """
    shape = np.shape(power_matrix)
    if cost_per_cycle <= 0 or p_max <= 0 or shape[1] < 2:
        return np.zeros(shape[0])
    swing = row_sums(np.abs(np.diff(np.asarray(power_matrix, dtype=float), axis=1)))
    return cost_per_cycle * swing / (2.0 * p_max)


# ---------------------------------------------------------------------------
# Plan reason codes (item 16)
# ---------------------------------------------------------------------------

REASON_COMFORT_FLOOR = "comfort_floor"
REASON_CHEAP_PRICE = "cheap_price"
REASON_PREHEAT_WEATHER = "preheat_weather"
#: The neutral fall-through: a step that is none of the specific cases below,
#: which is to say an ordinary slot holding the house at target. Until v5.1.7
#: these steps were tagged ``preheat_weather`` — the same code as the genuine
#: high-heat-loss branch — so the card told a user that a mid-price hour on a
#: mild afternoon was "Pre-heating before colder weather". A reason code that
#: doubles as a default is a reason code that cannot be trusted, and this one
#: was read as evidence that the optimizer was chasing weather it had not been
#: shown.
REASON_SCHEDULED = "scheduled"
REASON_TERMINAL_VALUE = "terminal_value"
REASON_SOLAR_SURPLUS = "solar_surplus"
REASON_DHW_WINDOW = "dhw_window"
REASON_DHW_READY = "dhw_ready"
REASON_DHW_PREHEAT = "dhw_preheat"
REASON_LEGIONELLA = "legionella"
REASON_IDLE = "idle"
#: Why an idle step is idle, when the solved plan shows it (R9-UX-5). One
#: code, the most specific that applies: a hard limit, then a named wait,
#: then the price, then coasting. ``idle`` remains the fall-through.
REASON_IDLE_OTHER = "idle_other_channel"
REASON_IDLE_FUSE = "idle_fuse"
REASON_IDLE_SOLAR = "idle_solar"
REASON_IDLE_DEARER = "idle_dearer"
REASON_IDLE_COASTING = "idle_coasting"
_IDLE_REASONS = frozenset({
    REASON_IDLE, REASON_IDLE_OTHER, REASON_IDLE_FUSE, REASON_IDLE_SOLAR,
    REASON_IDLE_DEARER, REASON_IDLE_COASTING,
})


def _above_floor(i: int, level: np.ndarray | None, floor: np.ndarray | None) -> bool:
    """The step's temperature is clear of the floor the plan was holding.

    ``level`` is a trajectory with the initial state at index 0, so step ``i``
    reads index ``i + 1``, the same index the heating classifier uses.
    """
    if level is None or floor is None or i >= len(floor) or len(level) == 0:
        return False
    j = i + 1 if i + 1 < len(level) else len(level) - 1
    return float(level[j]) > float(floor[i]) + 0.15


def _dearer_than_used(
    i: int, power: np.ndarray, prices: np.ndarray | None, threshold: float,
) -> bool:
    """This idle step costs more than every hour the channel actually ran."""
    if prices is None or i >= len(prices) or len(power) == 0:
        return False
    n = min(len(power), len(prices))
    used = np.asarray(prices[:n], dtype=float)[np.asarray(power[:n], dtype=float) > threshold]
    return bool(used.size) and float(prices[i]) > float(np.max(used))


def _waiting_for_solar(
    i: int, power: np.ndarray, surplus: np.ndarray | None, threshold: float,
) -> bool:
    """Surplus arrives before this channel's next run, and not at this step."""
    if surplus is None or i >= len(surplus) or float(surplus[i]) > 1e-6:
        return False
    nxt = i + 1
    while nxt < len(power) and float(power[nxt]) <= threshold:
        if nxt < len(surplus) and float(surplus[nxt]) > 1e-6:
            return True
        nxt += 1
    return False


def idle_reason(
    i: int,
    power: np.ndarray,
    prices: np.ndarray | None,
    level: np.ndarray | None,
    floor: np.ndarray | None,
    surplus: np.ndarray | None,
    other: np.ndarray | None,
    caps: np.ndarray | None,
    threshold: float,
) -> str:
    """The exact idle sub-code for step ``i``, or ``idle`` when none applies.

    Ranked. The other channel drawing, and a fuse cap that leaves no
    electrical room, are limits the plan did not choose. Waiting for solar
    and a price above every hour that ran are choices. Coasting is what is
    left when the temperature is simply above the floor.
    """
    if other is not None and i < len(other) and float(other[i]) > threshold:
        return REASON_IDLE_OTHER
    if caps is not None and i < len(caps) and float(caps[i]) <= threshold:
        return REASON_IDLE_FUSE
    if _waiting_for_solar(i, power, surplus, threshold):
        return REASON_IDLE_SOLAR
    if _dearer_than_used(i, power, prices, threshold):
        return REASON_IDLE_DEARER
    if _above_floor(i, level, floor):
        return REASON_IDLE_COASTING
    return REASON_IDLE


def classify_space_steps(
    power: np.ndarray,
    prices: np.ndarray,
    room_temps: np.ndarray,
    temp_min_bounds: np.ndarray,
    heat_loss_factors: np.ndarray,
    surplus: np.ndarray | None,
    n_steps: int,
    threshold: float = 0.05,
    *,
    other: np.ndarray | None = None,
    caps: np.ndarray | None = None,
) -> list[str]:
    """Why each space-heating step is where it is.

    The plan sensors published *which* slots were chosen but never *why*. A
    slot could be cheapest-price, comfort-floor, weather pre-heat, terminal
    value, solar self-consumption or simply scheduled, and nothing
    distinguished them — so an unexpected slot was indistinguishable from a
    bug. That makes the optimizer
    hard to trust and hard to support, and it makes bug reports much weaker
    than they could be.

    The classification is a post-hoc reading of the solved plan rather than
    something the solver emits, because the objective is a single scalar and
    there is no point in the LP at which one term "wins". Ranked, so the most
    specific explanation is the one reported.
    """
    reasons: list[str] = []
    if n_steps == 0:
        return reasons
    cheap_cut = float(np.percentile(prices, 35)) if len(prices) else 0.0
    for i in range(n_steps):
        if power[i] <= threshold:
            reasons.append(idle_reason(
                i, power, prices, room_temps, temp_min_bounds, surplus,
                other, caps, threshold,
            ))
            continue
        # Closest to a hard requirement wins: at or below the comfort floor,
        # the plan has no choice.
        room = room_temps[i + 1] if i + 1 < len(room_temps) else room_temps[-1]
        if room <= temp_min_bounds[i] + 0.15:
            reasons.append(REASON_COMFORT_FLOOR)
            continue
        if surplus is not None and i < len(surplus) and surplus[i] > 1e-6:
            reasons.append(REASON_SOLAR_SURPLUS)
            continue
        if i >= n_steps - max(1, int(0.08 * n_steps)):
            reasons.append(REASON_TERMINAL_VALUE)
            continue
        if i < len(heat_loss_factors) and heat_loss_factors[i] > 1.1:
            reasons.append(REASON_PREHEAT_WEATHER)
            continue
        if prices[i] <= cheap_cut:
            reasons.append(REASON_CHEAP_PRICE)
            continue
        # Nothing more specific applies: an ordinary step keeping the house at
        # target. `preheat_weather` is reserved for the heat-loss branch above,
        # which is the only one that has actually looked at the weather.
        reasons.append(REASON_SCHEDULED)
    return reasons


def classify_dhw_steps(
    power: np.ndarray,
    in_window: np.ndarray,
    ready_temps: np.ndarray,
    legionella_step: int | None,
    n_steps: int,
    threshold: float = 0.05,
    *,
    prices: np.ndarray | None = None,
    tank: np.ndarray | None = None,
    floors: np.ndarray | None = None,
    other: np.ndarray | None = None,
    caps: np.ndarray | None = None,
    surplus: np.ndarray | None = None,
) -> list[str]:
    """Why each hot-water step is where it is.

    Idle steps take the same sub-codes as space heating. Callers that do not
    pass prices, the tank, the floor, the other channel, the fuse cap or the
    surplus get ``idle``, which is what a hot-water path with none of those
    in hand used to publish as an empty explanation.
    """
    reasons: list[str] = []
    for i in range(n_steps):
        if power[i] <= threshold:
            reasons.append(idle_reason(
                i, power, prices, tank, floors, surplus, other, caps, threshold,
            ))
            continue
        if legionella_step is not None and i == legionella_step:
            reasons.append(REASON_LEGIONELLA)
            continue
        if i < len(ready_temps) and ready_temps[i] > 0:
            reasons.append(REASON_DHW_READY)
            continue
        if i < len(in_window) and in_window[i]:
            reasons.append(REASON_DHW_WINDOW)
            continue
        reasons.append(REASON_DHW_PREHEAT)
    return reasons


# ---------------------------------------------------------------------------
# Manual plan override (pinning when the pump runs)
# ---------------------------------------------------------------------------
#
# A user who hand-arranges their day pins individual steps on or off. The pin
# arrays are floats — NaN means "leave it to the optimizer", 0 forces the step
# off, 1 forces it on — so a whole channel is a single array the solver bounds
# can be built from directly. See ``manual_plan.py`` for how they are produced.

#: A step ran because the manual plan said so, not because the optimizer chose
#: it. Kept distinct from the automatic reasons so a pinned slot is never
#: mistaken for the solver's own decision.
REASON_MANUAL = "manual_plan"

#: A step is empty because the heat pump's *operating mode* cannot serve that
#: channel at all — a unit in ``heat`` makes no hot water, a unit in ``DHW`` or
#: ``cool`` heats no rooms. Deliberately distinct from ``idle``: idle means the
#: optimizer chose not to run, and a user reading "not heating" against a
#: comfort floor the plan is missing would look for a bug in the optimizer
#: instead of at the mode selector on the pump. See ``pump_mode.py``.
REASON_PUMP_MODE = "pump_mode"

#: How many times a manual plan may be repaired before its forced-off slots are
#: abandoned entirely. Each round costs a full solve, so this trades run time
#: against how precisely an unsafe plan can be salvaged.
_SAFETY_REPAIR_ROUNDS = 3

#: Reasons a pinned-on step keeps rather than being relabelled manual: they are
#: hard requirements it would have run for regardless of the pin.
_MANUAL_KEEP_REASONS = frozenset(
    {REASON_IDLE, REASON_COMFORT_FLOOR, REASON_LEGIONELLA}
)


def _apply_pins_to_bounds(
    bounds: list[tuple[float, float]],
    pins: np.ndarray | None,
    min_on_power: float,
) -> list[tuple[float, float]]:
    """Rewrite per-step solver bounds so pinned steps run or stay off.

    A forced-off step is clamped shut. A forced-on step has its *lower* bound
    raised to ``min_on_power`` so L-BFGS-B must actually run it, while its upper
    bound is left alone — the user pinned *when* the pump runs, not *how hard*,
    so the magnitude is still the optimizer's to choose. The lower bound is
    clamped to the existing upper bound because that upper bound can legitimately
    be zero (the other channel has taken all the capacity), and a lower bound
    above the upper bound makes the solve diverge.
    """
    if pins is None:
        return bounds
    out = list(bounds)
    for i in range(min(len(out), len(pins))):
        pin = float(pins[i])
        if _pin_is_free(pin):
            continue
        _low, high = out[i]
        if pin >= 0.5:
            out[i] = (min(min_on_power, high), high)
        else:
            out[i] = (0.0, 0.0)
    return out


def _mark_blocked_reasons(reasons: list[str], blocked: bool) -> list[str]:
    """Relabel a mode-blocked channel's empty steps from ``idle``.

    Only the empty ones, and only a channel the mode actually blocked. A
    blocked channel should be empty everywhere — the suppression is enforced
    at the bounds and, for hot water, again as a hard zeroing — so anything
    still carrying power here is a bug, and painting it ``pump_mode`` would
    hide the bug behind a plausible label. Leaving it as whatever the
    classifier said keeps the contradiction visible.
    """
    if not blocked:
        return reasons
    return [
        REASON_PUMP_MODE if reason in _IDLE_REASONS else reason
        for reason in reasons
    ]


def _dhw_reason_list(
    h: _Horizon,
    space_power: np.ndarray,
    dhw_power: np.ndarray | None,
    dhw_temps: np.ndarray | None,
    in_window: np.ndarray | None,
    ready: np.ndarray | None,
    legionella_step: int | None,
    floors: np.ndarray | None,
    surplus: np.ndarray | None,
) -> list[str]:
    """Hot-water reasons for a result, including when the caller has no windows.

    The shared builder used to store an empty list and let only the DHW path
    fill it, so any result that carried hot-water power without that second
    assignment published no reason at all. Idle steps still get the sub-codes
    when the caller has no demand windows to pass.
    """
    if dhw_power is None:
        return []
    n = h.n_steps
    window = in_window if in_window is not None else np.zeros(n, dtype=bool)
    ready_arr = ready if ready is not None else np.zeros(n)
    return _mark_blocked_reasons(
        _mark_manual_reasons(
            classify_dhw_steps(
                dhw_power, window, ready_arr, legionella_step, n,
                prices=h.prices, tank=dhw_temps, floors=floors,
                other=space_power, caps=h.power_caps_extra, surplus=surplus,
            ),
            h.dhw_pins,
        ),
        h.dhw_blocked,
    )


def _mark_manual_reasons(
    reasons: list[str], pins: np.ndarray | None
) -> list[str]:
    """Relabel steps the manual plan forced on, unless a hard reason applies.

    A forced-on step that would have run anyway — because it is at the comfort
    floor or is the legionella cycle — keeps that more specific reason; every
    other running forced-on step is attributed to the manual plan.
    """
    if pins is None:
        return reasons
    out = list(reasons)
    for i in range(min(len(out), len(pins))):
        pin = float(pins[i])
        if _pin_is_free(pin) or pin < 0.5:
            continue
        if out[i] not in _MANUAL_KEEP_REASONS:
            out[i] = REASON_MANUAL
    return out


@dataclass
class OptimizationResult:
    """Result of the MPC optimization."""

    power_schedule: list[float]  # kW electrical per time step (space heating)
    room_temp_trajectory: list[float]  # °C predicted avg room temp
    slab_temp_trajectory: list[float]  # °C predicted slab temp
    timestamps: list[datetime]  # timestamp for each step
    prices: list[float]  # electricity price per step
    predicted_cost: float  # total cost in currency units
    baseline_cost: float  # cost with constant-temp strategy
    predicted_savings: float  # savings vs baseline
    savings_percentage: float  # -100..100, not a fraction; see _savings_percentage
    optimal_setpoints: list[float]  # recommended setpoints per step
    status: str  # optimization status
    solve_time_ms: float = 0.0
    # Cost of restoring heat the plan left unstored at the end of the horizon.
    # Excluded from predicted_cost (which is what will actually be spent in the
    # window) but charged against the savings so borrowed heat is not counted
    # as a saving.
    deferred_energy_cost: float = 0.0

    # Outdoor temperature actually used for each step, so consumers can plot
    # the plan against the weather it was made for.
    outdoor_temps: list[float] = field(default_factory=list)

    # ECL110-oriented control outputs
    displace_schedule: list[float] = field(default_factory=list)
    heat_pump_on_schedule: list[bool] = field(default_factory=list)

    # The planned buffer-tank temperature, one entry per step boundary. Empty
    # without a mixing valve, where the tank is a hydraulic separator and its
    # temperature is not a decision. It is the only view anyone -- a sensor, the
    # card, a test -- has of whether the plan intends to store anything.
    buffer_temp_trajectory: list[float] = field(default_factory=list)
    # The valve target the plan wants at each step, fully resolved. Non-empty
    # only in smart_write mode when a hold schedule beat the fixed target on
    # the objective: low between charging and the price peak so the tank keeps
    # its heat, back to the working target through the peak. The actuator
    # writes the current step's entry each cycle.
    valve_target_schedule: list[float] = field(default_factory=list)
    # The planned wood-tank temperature, one entry per step boundary. Empty
    # unless the two-tank topology is modelled (issue #40) — mirrors
    # buffer_temp_trajectory as the only external view of the wood store.
    wood_temp_trajectory: list[float] = field(default_factory=list)
    # The achieved objective value of this plan, for candidate comparison --
    # two solves under different valve schedules are two controls priced by
    # the same physics, so the smaller wins. NaN when a solve failed.
    objective_value: float = float("nan")
    # Two-zone trajectories
    upper_temp_trajectory: list[float] = field(default_factory=list)
    lower_temp_trajectory: list[float] = field(default_factory=list)
    solar_gain_trajectory: list[float] = field(default_factory=list)
    upper_setpoints: list[float] = field(default_factory=list)
    lower_setpoints: list[float] = field(default_factory=list)

    # DHW optimization results
    dhw_power_schedule: list[float] = field(default_factory=list)
    # Thermostat-baseline electrical kW per step (space + DHW). Settlement
    # reads the current step; must be a pickle-safe list for the process route.
    baseline_power_schedule: list[float] = field(default_factory=list)
    dhw_temp_trajectory: list[float] = field(default_factory=list)
    dhw_heating_cost: float = 0.0

    # Predictive insights
    predictive_info: dict[str, Any] = field(default_factory=dict)

    # --- Plan reason codes (item 16) -----------------------------------
    #: Per-step explanation of why the plan does what it does.
    space_reasons: list[str] = field(default_factory=list)
    dhw_reasons: list[str] = field(default_factory=list)

    # --- Price provenance (item 7) -------------------------------------
    #: True where the price came from the published market data, False where
    #: it came from the learned diurnal prior. A plan that looks identical
    #: whether or not it rests on real prices cannot be audited.
    price_known: list[bool] = field(default_factory=list)

    # --- Capacity tariff and cycling (items 8, 10) ---------------------
    #: Peak the plan would set, in kW at the house connection.
    projected_peak_kw: float = 0.0
    #: Cost of that peak above what the month has already committed to.
    peak_cost: float = 0.0
    #: Off→on transitions in the space heating schedule.
    compressor_starts: int = 0

    # --- PV self-consumption (item 9) ----------------------------------
    #: Forecast surplus (production minus baseline load) per step, kW.
    pv_surplus: list[float] = field(default_factory=list)
    #: Heat pump energy served from surplus rather than imported, kWh.
    pv_self_consumed_kwh: float = 0.0

    # --- Manual plan override ------------------------------------------
    #: True when a manual plan pinned any step in this solve.
    manual_pins_active: bool = False
    #: Steps whose forced-off pin had to be released for safety (comfort floor,
    #: tank minimum or legionella), so the UI can show where the plan yielded.
    manual_released_space: list[int] = field(default_factory=list)
    manual_released_dhw: list[int] = field(default_factory=list)

    # --- Heat pump operating mode (v5.3.0) ------------------------------
    #: True when the pump's observed mode made this channel unplannable for
    #: the whole horizon. Unlike a manual pin these are never released for
    #: safety: releasing them would put back power the hardware refuses to
    #: draw, so the plan would report heat that cannot arrive. The channel's
    #: floor is left unmet and *visible* instead.
    #:
    #: Also mirrored into ``predictive_info`` when true, because that is the
    #: dict the coordinator actually publishes; a field only the solver could
    #: see would make "the plan is empty and nothing says why" a supported
    #: outcome. Only when true, so a plan with no mode entity carries no new
    #: keys at all.
    mode_blocked_space: bool = False
    mode_blocked_dhw: bool = False


@dataclass
class OptimizationConfig:
    """Configuration for the optimizer."""

    # Temperature constraints
    target_temp: float = 21.0
    min_temp: float = 19.0
    max_temp: float = 23.0
    comfort_temp_day: float = 21.0
    comfort_temp_night: float = 19.5
    day_start_hour: int = 7
    day_end_hour: int = 22
    comfort_temp_day_weekend: float | None = None
    comfort_temp_night_weekend: float | None = None
    day_start_hour_weekend: int | None = None
    day_end_hour_weekend: int | None = None
    holiday_comfort_day: float | None = None
    holiday_comfort_night: float | None = None
    holiday_day_start_hour: int | None = None
    holiday_day_end_hour: int | None = None
    holiday_dates: frozenset[date] = field(default_factory=frozenset)

    # Optimization parameters
    horizon_hours: float = 24.0
    time_step_minutes: float = 15.0
    price_weight: float = 1.0
    comfort_weight: float = 5.0

    # --- Compressor cycling (item 10) ---------------------------------
    # Every compressor start has real costs: oil dilution and wear, the loss
    # while the system re-establishes steady state, and on some units a
    # defrost penalty. Nothing in either optimizer path used to stop a plan
    # from chattering between steps.
    #
    # Modelled as a smooth L1 term on the step-to-step power difference rather
    # than a true minimum-runtime constraint. The L1 keeps the problem
    # continuous and cheap; a minimum-runtime constraint would make it a MILP,
    # which is not affordable inside a 30-second Home Assistant update on the
    # hardware this usually runs on.
    #: Currency cost attributed to one full start-stop cycle.
    #: Mirrors ``const.DEFAULT_CYCLING_COST`` rather than restating it, so the
    #: objective a harness builds directly is the objective that ships. The two
    #: had silently drifted apart once before, which meant the tests were
    #: measuring a slightly different optimizer from the integration.
    cycling_cost: float = DEFAULT_CYCLING_COST

    # --- Capacity tariff (item 8) --------------------------------------
    #: Currency per kW of new monthly peak, already divided by the number of
    #: peaks the DSO averages. Zero disables the term entirely.
    peak_price_per_kw: float = 0.0
    #: The level above which a new peak would raise the bill, in kW.
    peak_threshold_kw: float = 0.0
    #: Metering window of the tariff, in minutes.
    peak_window_minutes: int = 60
    #: How many of the month's highest peaks the DSO averages for the bill.
    peak_count: int = 3
    #: The averaged peaks fall on different days (#1512): a plan day
    #: contributes its highest window only.
    peak_distinct_days: bool = True
    #: Whole-house load excluding the heat pump, per step, in kW.
    baseline_load_kw: Any = None

    # --- PV self-consumption (item 9) -----------------------------------
    #: What an exported kWh earns, in the currency of the import price. With
    #: forecast surplus available, consumption up to it is priced at this
    #: rather than at the import price; see `_energy_cost_fn` below.
    pv_export_price: float = 0.0

    # --- Effekttariff masks (#13) --------------------------------------
    #: Months the capacity tariff applies in at all; empty = every month.
    peak_months: Any = frozenset()
    #: Peak-hour windows (dhw_schedule ``Window`` tuples); empty = always.
    peak_hours: Any = ()
    #: Weekends bill as off-peak when set.
    peak_weekdays_only: bool = False
    #: What an off-peak window's kW counts at; 1.0 = the flat model.
    peak_offpeak_factor: float = 1.0

    # --- Risk-adjusted unknown-horizon pricing (#34) --------------------
    #: Premium multiplier on the prior's per-step dispersion. Zero prices
    #: prior-filled steps at the mean, exactly as before.
    price_risk_lambda: float = DEFAULT_PRICE_RISK_LAMBDA

    @property
    def n_steps(self) -> int:
        """Number of optimization steps."""
        return int(self.horizon_hours * 60 / self.time_step_minutes)

    @property
    def dt_hours(self) -> float:
        """Time step in hours."""
        return self.time_step_minutes / 60.0

    @classmethod
    def from_mapping(cls, config: dict[str, Any]) -> "OptimizationConfig":
        """Build from an entry mapping so the coordinator stays a caller."""

        def _opt_float(key: str) -> float | None:
            raw = config.get(key)
            if raw is None or raw == "":
                return None
            try:
                return float(raw)
            except (TypeError, ValueError):
                return None

        def _opt_int(key: str) -> int | None:
            raw = config.get(key)
            if raw is None or raw == "":
                return None
            try:
                return int(raw)
            except (TypeError, ValueError):
                return None

        return cls(
            target_temp=config.get(CONF_TARGET_TEMP, DEFAULT_TARGET_TEMP),
            min_temp=config.get(CONF_MIN_TEMP, DEFAULT_MIN_TEMP),
            max_temp=config.get(CONF_MAX_TEMP, DEFAULT_MAX_TEMP),
            comfort_temp_day=config.get(
                CONF_COMFORT_TEMP_DAY, DEFAULT_COMFORT_TEMP_DAY
            ),
            comfort_temp_night=config.get(
                CONF_COMFORT_TEMP_NIGHT, DEFAULT_COMFORT_TEMP_NIGHT
            ),
            day_start_hour=int(
                config.get(CONF_DAY_START_HOUR, DEFAULT_DAY_START_HOUR)
            ),
            day_end_hour=int(config.get(CONF_DAY_END_HOUR, DEFAULT_DAY_END_HOUR)),
            comfort_temp_day_weekend=_opt_float(CONF_COMFORT_TEMP_DAY_WEEKEND),
            comfort_temp_night_weekend=_opt_float(CONF_COMFORT_TEMP_NIGHT_WEEKEND),
            day_start_hour_weekend=_opt_int(CONF_DAY_START_HOUR_WEEKEND),
            day_end_hour_weekend=_opt_int(CONF_DAY_END_HOUR_WEEKEND),
            holiday_comfort_day=_opt_float(CONF_HOLIDAY_COMFORT_DAY),
            holiday_comfort_night=_opt_float(CONF_HOLIDAY_COMFORT_NIGHT),
            holiday_day_start_hour=_opt_int(CONF_HOLIDAY_DAY_START_HOUR),
            holiday_day_end_hour=_opt_int(CONF_HOLIDAY_DAY_END_HOUR),
            price_weight=config.get(CONF_PRICE_WEIGHT, DEFAULT_PRICE_WEIGHT),
            comfort_weight=config.get(CONF_COMFORT_WEIGHT, DEFAULT_COMFORT_WEIGHT),
        )

    def _comfort_pair(
        self, when: datetime | None
    ) -> tuple[float, float, int, int]:
        day = self.comfort_temp_day
        night = self.comfort_temp_night
        start = self.day_start_hour
        end = self.day_end_hour
        if when is not None and when.date() in self.holiday_dates:
            if self.holiday_comfort_day is not None:
                day = self.holiday_comfort_day
            if self.holiday_comfort_night is not None:
                night = self.holiday_comfort_night
            if self.holiday_day_start_hour is not None:
                start = self.holiday_day_start_hour
            if self.holiday_day_end_hour is not None:
                end = self.holiday_day_end_hour
            return day, night, start, end
        if when is not None and when.weekday() >= 5:
            if self.comfort_temp_day_weekend is not None:
                day = self.comfort_temp_day_weekend
            if self.comfort_temp_night_weekend is not None:
                night = self.comfort_temp_night_weekend
            if self.day_start_hour_weekend is not None:
                start = self.day_start_hour_weekend
            if self.day_end_hour_weekend is not None:
                end = self.day_end_hour_weekend
        return day, night, start, end

    def get_comfort_temp(
        self, hour: float, when: datetime | None = None
    ) -> float:
        """Get comfort temperature for a given hour of day."""
        day, night, start, end = self._comfort_pair(when)
        if start <= hour < end:
            return day
        return night

    def get_temp_bounds(
        self, hour: float, when: datetime | None = None
    ) -> tuple[float, float]:
        """Get temperature bounds for a given hour."""
        _day, _night, start, end = self._comfort_pair(when)
        if start <= hour < end:
            return (self.min_temp, self.max_temp)
        return (self.min_temp - 0.5, self.max_temp)

    def baseline_load_array(self, n_steps: int) -> np.ndarray:
        """Per-step whole-house baseline load, padded or truncated to fit."""
        if self.baseline_load_kw is None:
            return np.zeros(n_steps, dtype=float)
        values = np.asarray(self.baseline_load_kw, dtype=float).ravel()
        if values.size == 0:
            return np.zeros(n_steps, dtype=float)
        if values.size >= n_steps:
            return values[:n_steps]
        return np.concatenate(
            [values, np.full(n_steps - values.size, float(values[-1]))]
        )


def _solver_status(
    result: Any, objective: Callable[..., float], initial_guess: np.ndarray
) -> str:
    """Classify a SciPy result, tolerating benign line-search aborts.

    L-BFGS-B reports ABNORMAL_TERMINATION_IN_LNSRCH whenever the line search
    cannot make further progress. On a flat price curve the cost surface is
    genuinely degenerate along the arbitrage direction, so this fires routinely
    even though the returned point is perfectly good. Surfacing that to the
    user as "suboptimal" is misleading, so only call it suboptimal when the
    solver actually failed to improve on the starting point.
    """
    if result.success:
        return "optimal"
    try:
        if objective(result.x) <= objective(initial_guess):
            return "optimal"
    except Exception:  # pragma: no cover - defensive
        pass
    return f"suboptimal ({result.message})"


@dataclass(frozen=True)
class _Horizon:
    """Everything about one solve that both optimization paths need.

    These eighteen values were previously threaded through two near-identical
    eighteen-parameter signatures. Collecting them removes that duplication,
    but the real benefit is that adding a new per-solve input is now a single
    edit instead of four (two signatures, two call sites) — which is exactly
    the kind of divergence that let the two objectives drift apart before.

    Frozen because nothing downstream should be rewriting the horizon it was
    handed; a path that wants a variation makes its own.
    """

    initial_state: ThermalState
    prices: np.ndarray
    outdoor_temps: np.ndarray
    wind_speeds: np.ndarray
    precipitation: np.ndarray
    solar_radiation: np.ndarray
    start_time: datetime
    n_steps: int
    dt: float
    #: Per-step comfort target and the bounds either side of it.
    comfort_targets: np.ndarray
    temp_min_bounds: np.ndarray
    temp_max_bounds: np.ndarray
    #: Hour-of-day per step, for the DHW draw pattern and demand windows.
    step_hours: np.ndarray
    #: Solar gain in kW, and the wind/rain multiplier on heat loss, per step.
    solar_gains: np.ndarray
    heat_loss_factors: np.ndarray
    #: Output of ``_analyze_forecast_trajectory``.
    forecast: dict[str, Any]
    #: ``time.monotonic()`` at the start of the solve, for the timing report.
    t_start: float
    #: Optional per-step manual pins, one array per channel, or ``None`` when
    #: that channel is fully automatic. Encoding: NaN free, 0 off, 1 on.
    space_pins: np.ndarray | None = None
    dhw_pins: np.ndarray | None = None
    #: Weekday lookup for weekly DHW windows (#3), n+1 entries (entry i is
    #: the weekday of the step before step i), or None on a flat spec.
    step_weekdays: np.ndarray | None = None
    #: Parallel to ``step_weekdays``: True when that step's date is a
    #: holiday-profile day. None when no holiday calendar is on.
    holiday_flags: np.ndarray | None = None
    #: Optional per-step ceiling on space-heating power, kW. The pin encoding
    #: can force a step on or off but cannot say "at most this much", which is
    #: what the buffer tank's hard temperature cap needs: the tighten-and-
    #: re-solve loop in ``optimize`` lowers entries here at steps that charged
    #: a full tank. ``None`` means the nameplate maximum everywhere.
    power_caps: np.ndarray | None = None
    #: Optional per-step *total electrical* ceiling, kW — the fuse guard and
    #: shadow solves (item 3). ``power_caps`` above bounds space heating
    #: alone; this one bounds space **plus** hot water, so the DHW planner
    #: and ``solve_space`` both have to respect it. Already clipped to ≥ 0
    #: and padded to ``n_steps``. ``None`` means uncapped.
    power_caps_extra: np.ndarray | None = None
    #: Optional per-step forecast of free thermal input, kW — a wood furnace
    #: burn (item 28). Both objectives and the savings baseline simulate with
    #: it, so the plan defers electric heat the furnace is already providing
    #: and the reference thermostat is granted the same free heat rather than
    #: booking it as savings. ``None`` means none.
    external_heat_kw: np.ndarray | None = None
    #: Optional per-step mixing-valve target schedule, fully resolved. Only
    #: the objectives simulate with it — the savings baseline is a thermostat
    #: and a thermostat does not schedule a valve. ``None`` means the static
    #: configured target, which is byte-for-byte the previous behaviour.
    valve_targets: np.ndarray | None = None
    #: Optional forecast relative humidity per step (#21), for the defrost
    #: derate; NaN marks unknown steps. ``None`` falls back to the single
    #: ambient value, which is byte-for-byte the previous behaviour.
    humidity: np.ndarray | None = None
    #: The observed operating mode has made a channel undeliverable for the
    #: whole horizon (v5.3.0). Carried rather than derived so the reason
    #: codes can say *why* a channel is empty; the actual suppression is
    #: already in ``power_caps`` (space) and the DHW forced-off mask.
    space_blocked: bool = False
    dhw_blocked: bool = False
    #: #1910 (SW-1): steps inside a quiet Off window — no space heat and no
    #: hot-water charge there (decision D1). Space rides a deliberate,
    #: unfloored zero entry in the caps array; hot water enters the planner's
    #: forced-off door, the same one manual pins and a blocked mode use, so
    #: the energy those steps would have carried is re-bought in the steps
    #: that remain (pre-heating) rather than deleted. ``None`` is
    #: byte-for-byte the previous behaviour.
    off_steps: np.ndarray | None = None
    #: #1910: the resolved quiet-window action per step (0 none, 1 silent,
    #: 2 off), carried for publication only — the caps and the mask above
    #: are what the solve itself reads. ``None`` when no window is in force.
    quiet_actions: np.ndarray | None = None
    #: Extra L-BFGS-B starting points for a cap-tightened re-solve (#234).
    #: Prepended ahead of the usual candidates so the solver can escape the
    #: kink at a lowered ceiling instead of re-descending onto it.
    extra_starts: tuple[np.ndarray, ...] | None = None

    @property
    def timestamps(self) -> list[datetime]:
        return _utc_step_starts(self.start_time, self.n_steps, timedelta(hours=self.dt))



@dataclass(frozen=True, kw_only=True)
class ForecastSeries:
    """The per-step series one solve plans against, each named (#1736).

    Most are same-shape float arrays, so the positional signature they used
    to travel in would have taken a transposition silently. ``None`` keeps
    each one's neutral default: no wind, rain, sun, surplus, free heat or
    price dispersion, every price published, the ambient humidity.
    """

    prices: np.ndarray
    outdoor_temps: np.ndarray
    wind_speeds: np.ndarray | None = None
    precipitation: np.ndarray | None = None
    solar_radiation: np.ndarray | None = None
    price_known: np.ndarray | None = None
    pv_surplus: np.ndarray | None = None
    price_sigma: np.ndarray | None = None
    humidity: np.ndarray | None = None
    external_heat_kw: np.ndarray | None = None


@dataclass(frozen=True, kw_only=True)
class SolveLimits:
    """What bounds one solve beyond its configuration: the manual pins, the
    electrical ceiling, the comfort floor's two adjustments and the pump's
    blocked channels. The defaults bound nothing."""

    space_pins: np.ndarray | None = None
    dhw_pins: np.ndarray | None = None
    power_caps_extra: np.ndarray | None = None
    min_temp_margins: np.ndarray | None = None
    min_temp_floors: np.ndarray | None = None
    space_blocked: bool = False
    dhw_blocked: bool = False
    off_steps: np.ndarray | None = None
    quiet_actions: np.ndarray | None = None


@dataclass(frozen=True, kw_only=True)
class SolveInputs:
    """Everything ``HeatPumpOptimizer.optimize`` plans from besides its own
    model and configuration, built once per solve and never written."""

    state: ThermalState
    forecast: ForecastSeries
    start_time: datetime | None = None
    limits: SolveLimits = field(default_factory=SolveLimits)


def hold_demand_kw(
    params: ThermalParameters,
    target: float,
    out_mean: float,
    solar_mean: float = 0.0,
) -> float:
    """Net thermal power the house needs to hold target, kW, never negative.

    Deliberately NOT shared with ``slab_settlement_cap``, which computes a
    similar-looking number for a different question and must keep doing so.
    That one sizes how hot the slab has to run, so in two-zone mode it uses
    the lower zone's loss and gains alone — the slab feeds only the lower
    zone. This one asks how fast the buffer tank drains, and the tank sits
    upstream of the mixing valve feeding both zones, so it is whole-house.
    Collapsing the two would either inflate the slab ceiling by the upper
    zone's demand or understate the tank's drain rate; they are two laws that
    happen to rhyme, not one law written twice.

    ``solar_mean`` is likewise opt-in rather than always-on. The slab ceiling
    deliberately ignores solar (a worst case within the horizon); the
    survival term must not, because free gain genuinely displaces the demand
    the stored heat is waiting for, and omitting it credits storage on a
    sunny summer day.

    Zero means the house does not need bought heat at all at this weather —
    gains alone hold the target — which is a real and common summer state,
    not a degenerate one. Callers must handle it rather than dividing by it.
    """
    if params.two_zone_enabled:
        u_eff = params.upper_floor_heat_loss + params.lower_floor_heat_loss_learned
    else:
        u_eff = params.heat_loss_coefficient
    # D2-s2-01: the learned leakage scale the dynamics apply to both zones.
    u_eff *= params.house_heat_loss_scale
    return max(
        0.0,
        u_eff * (target - out_mean)
        - params.internal_gains
        - max(0.0, float(solar_mean)),
    )


def stored_heat_survival(
    ua: float, cap: float, demand: float, ambient: float = DHW_COOLING_REFERENCE_AMBIENT_TEMP
) -> float:
    """Fraction of tank heat left at the horizon end the next window can use.

    The terminal cost credits a full tank as heat the next window does not
    have to buy. That is only true if the next window *spends* it. A tank
    loses to ambient at ``UA`` whether or not anyone draws on it, so heat put
    in against a demand that will not arrive for days is largely gone before
    it is wanted — and crediting it at face value is what had the optimizer
    buying space heat in July, when the house was coasting six degrees clear
    of its comfort floor and the credit was the only term with a gradient.

    A mixed tank drained steadily at ``demand`` empties in
    ``C (cap - ambient) / demand`` hours, so the average kWh in it is spent at
    half that. Decaying over that time with the tank's own time constant
    ``tau = C / UA`` cancels ``C`` entirely:

        survival = exp(-UA (cap - ambient) / (2 demand))

    which is ``exp(-half the drain time / tau)`` — how many time constants
    pass before the heat is used. It depends only on the weather and the
    hardware, never on the end temperature the solver is choosing, so the
    terminal cost stays linear in that end temperature and the gradient keeps
    pointing the same way; making the discount itself a function of the
    decision variable would give the term a second-order kink for no physical
    gain.

    Winter is untouched by construction: at a 750 L tank's learned UA and a
    house drawing ~4.7 kW the discount is under 3%. It only bites when the
    demand it is divided by collapses, which is exactly the case it exists
    for.

    ``UA`` is the *learned* standby loss (``buffer_cooling_rate``, fitted by
    the coordinator from observed cooling and clamped to this tank's
    insulation bounds), so a well-insulated accumulator is discounted far
    less than a bare cylinder — the discount is this tank's physics, not a
    tuning constant.
    """
    if ua <= 0.0:
        return 1.0
    span = cap - ambient
    if span <= 0.0:
        # Nothing usable stored above ambient; the credit is zero anyway.
        return 1.0
    if demand <= 0.0:
        # No demand at all: the hold time is unbounded and every stored kWh
        # leaks away before it is ever spent.
        return 0.0
    # Capped before exp() so a near-zero demand underflows to 0.0 cleanly
    # rather than raising.
    return float(math.exp(-min(0.5 * ua * span / demand, 700.0)))


def slab_settlement_cap(
    params: ThermalParameters, target: float, out_mean: float
) -> float:
    """The slab temperature above which stored heat is worth nothing.

    The slab has to run above the room to push heat into it, so its useful
    ceiling is the temperature that *sustains* the target at the weather in
    front of it, not the target itself. Above that the extra degrees buy
    nothing the plan can spend, so settling them up would credit a plan for
    being pointlessly hot.

    Module level, and public, because the settlement is no longer its only
    reader: the virtual battery view reports the slab's usable capacity and
    state of charge, and used a `comfort_max + 6` magic offset to do it —
    a fixed 29.0 °C against this function's weather-dependent 24.5-28.5,
    overstating usable capacity by around a quarter and understating the
    charge in it by the same. One formula, both readers.

    Bounded above by the plant: the slab is fed by store water that
    ``buffer_max_temp`` caps, so it cannot stand above that however weak
    the coupling. Without the bound the term grows without limit as
    ``slab_heat_transfer`` falls — roughly 195 °C at ``presets.derive``'s
    own floor — crediting heat no slab can physically hold. The bound
    rides existing configuration rather than a constant, so a future
    ceiling change moves it (issue #87).
    """
    if params.two_zone_enabled:
        # The slab feeds ONLY the lower zone (`q_slab_to_lower` in the
        # dynamics; the upper zone is radiator-fed), so its ceiling is
        # sized from the lower zone's demand alone — the learned loss,
        # because every consumer of the dynamics goes through it — and
        # the lower zone's share of the internal gains. Sizing it from
        # the whole house inflated the cap by the upper zone's demand
        # and over-valued hot-slab end states by exactly that much.
        q_demand = max(
            0.0,
            params.lower_floor_heat_loss_learned * params.house_heat_loss_scale
            * (target - out_mean)
            - params.internal_gains * (1.0 - params.upper_floor_area_ratio),
        )
    else:
        # D2-s2-01: the learned leakage scale, as the dynamics apply it; a
        # cap sized on the nameplate loss does not sustain the target.
        u_eff = params.heat_loss_coefficient * params.house_heat_loss_scale
        q_demand = max(0.0, u_eff * (target - out_mean) - params.internal_gains)
    return min(
        target + q_demand / params.slab_heat_transfer_floored,
        params.buffer_max_temp,
    )


def _terminal_row_cost(
    refill_price: float,
    cop_end: float,
    cop_buffer: float,
    stores: tuple[tuple[float, str, float, float], ...],
) -> tuple[Callable[[Iterable[float]], float], tuple[tuple[float, str, float], ...]]:
    """The terminal cost of ONE plan, from its end-of-horizon temperatures.

    Returns the shared per-plan accumulation and the per-store term
    specification (``mass * survival`` folded, with the store's name and
    cap) the caller builds that plan's terms from. The terms are exact IEEE
    arithmetic -- ``coef * max(0.0, cap - end)``, two multiplies and a
    subtraction -- so the scalar closure may build them in Python and the
    batch twin elementwise across its rows with the same bits. The
    ACCUMULATION is the shared function, run once per plan by both twins
    (#948): sharing it is what keeps the objective and the batched
    objective it serves from differing by a single floating-point
    operation -- including builtin ``sum``'s compensated (Neumaier)
    summation on CPython 3.12+, which no vectorized accumulation
    reproduces and which is exactly the ulp that diverged this branch's
    jac races on CI's 3.14 runner while every 3.11 seat stayed green
    (3.11's ``sum`` is plain accumulation). The terms moving out of the
    per-plan function is R9 F2.5 (RC-rca2): the per-row loop this replaces
    built a name-keyed dict and walked the stores in Python per row, which
    the round-9 recompute RCA measured at 2-3 % of every solve and the S5
    sweep could not see because it keyed the loop to this builder, which
    runs once.
    """
    terms = tuple(
        (mass * survival, name, cap) for mass, name, cap, survival in stores
    )
    is_buffer = tuple(name == "buffer" for _, name, _ in terms)

    def row_cost(term_values: Iterable[float]) -> float:
        # The buffer's deficit converts at its own (flow-derated) COP;
        # everything else at the plain curve. Split only when the two
        # actually differ, so every unthrottled configuration keeps the
        # single-sum arithmetic -- and therefore the solver's descent
        # path -- bit for bit.
        if cop_buffer != cop_end:
            deficit = 0.0
            buffer_deficit = 0.0
            for buffered, term in zip(is_buffer, term_values):
                if buffered:
                    buffer_deficit += term
                else:
                    deficit += term
            return refill_price * (
                deficit / max(cop_end, 1e-6)
                + buffer_deficit / max(cop_buffer, 1e-6)
            )
        deficit = sum(term_values)
        return refill_price * deficit / max(cop_end, 1e-6)

    return row_cost, terms


class HeatPumpOptimizer:
    """MPC-based heat pump cost optimizer with predictive weather anticipation and DHW."""

    #: The two-zone floor's linear price, as a fraction of its own: 1.0, but
    #: 0.5 for the continuation ``_optimize_space_only`` runs on its first
    #: start -- see there.
    _floor_l1_scale = 1.0

    def __init__(
        self,
        thermal_model: ThermalModel,
        config: OptimizationConfig,
    ) -> None:
        """Initialize the optimizer."""
        self.model = thermal_model
        self.config = config
        # Populated per solve by ``optimize``; kept as attributes so the two
        # solve paths can reach them without threading five more parameters
        # through their already long signatures.
        self._price_known: np.ndarray | None = None
        self._pv_surplus: np.ndarray | None = None
        # The requirement the last DHW build returned, for the safety-release
        # loop: the tank temperature the plan must keep the DHW trajectory
        # above. Assigned at each build, so the last build of a solve wins.
        self._dhw_requirement: np.ndarray | None = None
        #: The solve's starting buffer temperature; floors the settlement
        #: value cap so pre-stored heat cannot be drained for free.
        self._initial_buffer_temp: float | None = None

    # ------------------------------------------------------------------
    # Shared cost terms
    # ------------------------------------------------------------------

    def _anticipatory_weights(
        self,
        n_steps: int,
        dt: float,
        solar_gains: np.ndarray,
        heat_loss_factors: np.ndarray,
    ) -> np.ndarray:
        """Warm-start shaping for the *initial guess* only.

        A cheap forecast-aware nudge: start the solver lower where sun is
        coming and higher where the weather is about to turn, so L-BFGS-B
        begins near the shape of the answer.

        These weights used to scale the comfort-violation penalty as well,
        which discounted a real breach of the user's minimum temperature
        because the sun might come out later. That is backwards — if the sun
        does arrive, the simulated trajectory is not cold and no penalty arises
        anyway, so the discount could only ever buy under-heating.
        """
        weights = np.ones(n_steps)
        lookahead = int(8 / dt)
        for i in range(n_steps):
            end = min(i + lookahead, n_steps)
            if end <= i:
                continue
            future_solar = np.mean(solar_gains[i:end])
            if future_solar > 0.5:  # > 0.5 kW solar gain is significant
                weights[i] *= max(0.6, 1.0 - future_solar * 0.3)
            future_loss = np.mean(heat_loss_factors[i:end])
            if future_loss > 1.1:
                weights[i] *= min(1.5, future_loss)
        return weights

    def _comfort_terms(
        self,
        room_temps: np.ndarray,
        upper_temps: np.ndarray,
        lower_temps: np.ndarray,
        comfort_targets: np.ndarray,
        temp_min_bounds: np.ndarray,
        temp_max_bounds: np.ndarray,
        comfort_band: np.ndarray,
    ) -> tuple[float, float]:
        """The comfort penalty and the pull-to-target cost.

        Returns them separately because they mean different things: the first
        is the price of breaching the user's bounds, the second is a mild
        preference for sitting near the target inside them.

        Two-zone overshoot and pull are *averaged* over the zones rather than
        summed. Summing made a two-zone house behave as if ``comfort_weight``
        were set twice as high as configured, so it hugged the setpoint and gave
        up most of the available savings. The floor's linear price is not
        averaged: each zone's kelvin under ``min_temp`` pays the full
        ``_COMFORT_FLOOR_L1``, as a single-zone room's does. Averaged, it paid
        half, and the solver bought the breach back where prices paid for it
        (R9 D2-s2-81). The quadratic undershoot stays averaged: priced in full
        too, it left more of the stock two-zone plans under the floor than the
        linear term alone, measured on the goldens.

        **The pull is deliberately weak.** The user states a *band*, and the
        band is what the plan owes them; the target is a preference inside it.
        At twice the current strength the pull was quietly expensive: measured
        on the winter scenario it cost 28.55 SEK against 23.28 -- 18 % of the
        bill -- to hold the house 0.32 K warmer on average while never
        approaching the floor. Nobody asked for that trade, and
        ``comfort_weight`` is the knob for anyone who wants it back.
        """
        penalty, comfort_cost = self._comfort_terms_batch(
            np.asarray(room_temps, dtype=float)[None, :],
            np.asarray(upper_temps, dtype=float)[None, :],
            np.asarray(lower_temps, dtype=float)[None, :],
            comfort_targets, temp_min_bounds, temp_max_bounds, comfort_band,
        )
        return float(penalty[0]), float(comfort_cost[0])

    def _comfort_terms_batch(
        self,
        room_temps: np.ndarray,
        upper_temps: np.ndarray,
        lower_temps: np.ndarray,
        comfort_targets: np.ndarray,
        temp_min_bounds: np.ndarray,
        temp_max_bounds: np.ndarray,
        comfort_band: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """``_comfort_terms`` for a [B, n+1] trajectory batch, one entry per row.

        Every per-element operation is elementwise across the batch and every
        sum is ``row_sums`` (batchmath), so a row is the one-row call ``_comfort_terms``
        makes, bit for bit, on every numpy backend and in either memory
        order. The per-row loop this replaced (#948) held the same contract
        by re-running the scalar body B times, which cost 13-32 % of a solve
        (R9 D9-s1-01). See ``_comfort_terms`` for what the two terms mean and
        why the pull is deliberately weak.
        """
        weight = self.config.comfort_weight

        if self.model.params.two_zone_enabled:
            upper_t = upper_temps[:, 1:]
            lower_t = lower_temps[:, 1:]

            undershoot_u = np.maximum(0, temp_min_bounds - upper_t)
            overshoot_u = np.maximum(0, upper_t - temp_max_bounds)
            undershoot_l = np.maximum(0, temp_min_bounds - lower_t)
            overshoot_l = np.maximum(0, lower_t - temp_max_bounds)

            penalty = 0.5 * weight * (
                row_sums(undershoot_u ** 2) * 10.0
                + row_sums(overshoot_u ** 2) * 5.0
                + row_sums(undershoot_l ** 2) * 10.0
                + row_sums(overshoot_l ** 2) * 5.0
            ) + weight * (
                row_sums(undershoot_u) + row_sums(undershoot_l)
            ) * (_COMFORT_FLOOR_L1 * self._floor_l1_scale)

            comfort_dev_u = upper_t - comfort_targets
            comfort_dev_l = lower_t - comfort_targets
            comfort_cost = _COMFORT_PULL_TWO_ZONE * weight * (
                row_sums((comfort_dev_u / comfort_band) ** 2)
                + row_sums((comfort_dev_l / comfort_band) ** 2)
            )
            return penalty, comfort_cost

        room_t = room_temps[:, 1:]
        undershoot = np.maximum(0, temp_min_bounds - room_t)
        overshoot = np.maximum(0, room_t - temp_max_bounds)

        penalty = weight * (
            row_sums(undershoot ** 2) * 10.0
            + row_sums(overshoot ** 2) * 5.0
            + row_sums(undershoot) * _COMFORT_FLOOR_L1
        )
        deviation = room_t - comfort_targets
        comfort_cost = (
            _COMFORT_PULL_SINGLE_ZONE
            * weight
            * row_sums((deviation / comfort_band) ** 2)
        )
        return penalty, comfort_cost

    def _cost_terms_batch(
        self,
        traj: dict[str, np.ndarray],
        grid_power: np.ndarray,
        *,
        energy_cost_of: Callable[[np.ndarray], Any],
        cycling_batch: Callable[[np.ndarray], np.ndarray],
        capacity_batch: Callable[[np.ndarray], np.ndarray],
        terminal_cost_batch: Callable[[dict[str, np.ndarray]], np.ndarray],
        comfort_targets: np.ndarray,
        temp_min_bounds: np.ndarray,
        temp_max_bounds: np.ndarray,
        comfort_band: np.ndarray,
    ) -> np.ndarray:
        """The batched objective's cost half: every term, once per batch (#948).

        ``objective_batch``'s two twins vectorized the simulation (#97) and
        then re-computed these terms in a Python loop over the B rows; here
        each term is one reduction over the whole batch, in the scalar
        objective's own addition order, so every row equals ``objective``
        on the same schedule bit for bit -- pinned on the production
        closures by tests/features.py (#948 section).

        ``grid_power`` is what the grid sees per row -- the space schedule
        alone on the space-only path, space plus the DHW plan on the DHW
        path -- because the energy, cycling and capacity terms are
        properties of the combined draw, while the comfort and terminal
        terms read ``traj``, which the space schedule alone produces.
        """
        weight = self.config.price_weight
        penalty, comfort_cost = self._comfort_terms_batch(
            traj["room"], traj["upper"], traj["lower"],
            comfort_targets, temp_min_bounds, temp_max_bounds, comfort_band,
        )
        # ``np.asarray`` on the sum is a no-op view: it types the value
        # without touching a bit of it.
        return np.asarray(
            energy_cost_of(grid_power) * weight
            + penalty
            + comfort_cost
            + (cycling_batch(grid_power) + capacity_batch(grid_power)) * weight
            + terminal_cost_batch(traj)
        )

    def _buffer_survival(
        self,
        outdoor_temps: np.ndarray,
        solar_gains: np.ndarray | None,
        cap: float | None,
    ) -> float:
        """The buffer tank's terminal-credit discount for this horizon.

        Returns 1.0 — today's behaviour exactly — whenever the tank is not a
        store, so the no-valve and small-tank paths stay byte-for-byte
        identical. ``solar_gains`` is optional so a caller without a forecast
        degrades to the no-solar answer (a smaller discount) rather than
        crashing; that is the conservative direction.
        """
        params = self.model.params
        if not params.buffer_is_store or cap is None:
            return 1.0
        solar_mean = (
            float(np.mean(solar_gains))
            if solar_gains is not None and len(solar_gains)
            else 0.0
        )
        demand = hold_demand_kw(
            params,
            self.config.target_temp,
            float(np.mean(outdoor_temps)),
            solar_mean,
        )
        return stored_heat_survival(
            params.buffer_tank_heat_loss_coefficient, float(cap), demand
        )

    def _terminal_cost(
        self,
        prices: np.ndarray,
        outdoor_temps: np.ndarray,
        solar_gains: np.ndarray | None = None,
        humidity: np.ndarray | None = None,
    ) -> tuple[Callable[..., float], Callable[[dict[str, np.ndarray]], np.ndarray]]:
        """Price the heat the plan leaves unstored at the end of the horizon.

        Nothing beyond the horizon is scored, so without this the optimizer
        always dumps the last couple of hours: it coasts the house down because
        the resulting cold never appears in the objective. That both breaches
        the comfort floor at the tail of the plan and reports a saving that was
        really borrowed heat.

        Returns the scalar closure and, beside it, its batch twin (#948):
        both run ONE shared per-plan function — the accumulation at the
        heart of the scalar closure — so neither the per-store constants,
        nor their order, nor a single floating-point operation can drift
        between the objective and the batched objective it serves. The
        per-plan construction is not a style choice: the store
        accumulation is a REDUCTION whose scalar form is Python's builtin
        ``sum``, which on CPython 3.12+ is Neumaier-compensated — a
        different float, by design, from the plain left-to-right
        accumulation a vectorized twin would compute, on exactly the ulp
        the solver's iterate path amplifies (round 7 of this branch: the
        race diverged on CI's 3.14 runner and on no 3.11 seat, because
        3.11's ``sum`` is plain accumulation). See ``_terminal_row_cost``
        and ``_terminal_cost_batch`` for the two sides of that contract.

        The shortfall is priced against the same reference the savings
        settle-up uses — the 25th-percentile price and the mean-outdoor COP,
        exactly as ``_deferred_energy_cost`` prices it — so the plan and the
        reported savings agree. Scaled by ``price_weight`` because the energy
        term is: an unscaled terminal cost at a non-default weight changes the
        exchange rate between buying heat now and buying it back later, which
        re-creates the tail-dumping this term exists to prevent.

        Each store's deficit converts at that store's own marginal COP
        (v4.0.5, ``ThermalModel.marginal_cop``). The building mass refills at
        the plain curve, but the buffer tank charges at the flow-derated COP
        of its settlement temperature — the same physics the simulation
        applies while charging it. Pricing the tank's terminal kWh at the
        plain curve paid back less per kWh than storing it cost, so the
        solver only stored when the price spread also covered a COP gap the
        physics never charged: systematic under-charging.
        """
        caps = self._settlement_caps(outdoor_temps, humidity=humidity)
        refill_price = (
            float(np.percentile(prices, 25)) * self.config.price_weight
        )
        # How much of what the tank holds the next window actually gets to
        # spend. Every building store settles at 1.0: their cap IS the comfort
        # target, so heat credited there is heat serving the objective
        # directly, not speculative storage waiting for a demand that may not
        # come. Only the tank is an intermediate store, and only the tank can
        # be charged with no comfort consequence at all.
        buffer_survival = self._buffer_survival(
            outdoor_temps, solar_gains, caps.get("buffer")
        )
        out_mean = float(np.mean(outdoor_temps))
        hum_mean = _mean_humidity(humidity)
        cop_end = self.model.compute_cop(out_mean, humidity=hum_mean)
        # Equal to `cop_end` bit for bit whenever no valve throttles (the
        # `cop_flow_carnot` gate) or the cap sits at the flow reference; the
        # branch below keeps those paths on the historical arithmetic.
        cop_buffer = self.model.marginal_cop(
            out_mean, "buffer", store_temp=caps["buffer"], humidity=hum_mean
        )
        params = self.model.params

        stores: tuple[tuple[float, str, float, float], ...]
        if params.two_zone_enabled:
            stores = (
                (params.upper_floor_thermal_mass, "upper", caps["room"], 1.0),
                (params.lower_floor_thermal_mass, "lower", caps["room"], 1.0),
                (params.slab_thermal_mass, "slab", caps["slab"], 1.0),
            )
            if params.buffer_is_store:
                # Only with a valve, and only a tank big enough to matter.
                # Without a valve the tank cannot be charged, so adding it
                # here would put a constant in the objective -- it would not
                # change which plan wins, but it would move every reported
                # number for no reason. A tiny tank (item 27) holds less than
                # one step of heat, and crediting it has the solver planning
                # around noise.
                stores = stores + (
                    (
                        params.buffer_tank_thermal_mass,
                        "buffer",
                        caps["buffer"],
                        buffer_survival,
                    ),
                )
        else:
            stores = (
                (params.room_thermal_mass, "room", caps["room"], 1.0),
                (params.slab_thermal_mass, "slab", caps["slab"], 1.0),
            )

        row_cost, term_spec = _terminal_row_cost(
            refill_price, cop_end, cop_buffer, stores
        )

        def cost(
            room_temps: np.ndarray,
            slab_temps: np.ndarray,
            upper_temps: np.ndarray,
            lower_temps: np.ndarray,
            buffer_temps: np.ndarray | None = None,
        ) -> float:
            ends = {
                "room": float(room_temps[-1]),
                "slab": float(slab_temps[-1]),
                "upper": float(upper_temps[-1]),
                "lower": float(lower_temps[-1]),
                # A tank left cold is heat that has to be bought back, exactly
                # like a cold slab. Leaving it out is what made charging look
                # like pure cost with no benefit, so no starting point could
                # ever descend towards storing anything.
                "buffer": (
                    float(buffer_temps[-1]) if buffer_temps is not None else 0.0
                ),
            }
            # The store terms in store order: the same two multiplies and
            # one subtraction per store the batch twin computes
            # elementwise, so both twins feed the shared accumulation the
            # same floats to the bit (see _terminal_row_cost).
            return row_cost([
                coef * max(0.0, cap - ends[name])
                for coef, name, cap in term_spec
            ])

        return cost, self._terminal_cost_batch(row_cost, term_spec)

    @staticmethod
    def _terminal_cost_batch(
        row_cost: Callable[[Iterable[float]], float],
        term_spec: tuple[tuple[float, str, float], ...],
    ) -> Callable[[dict[str, np.ndarray]], np.ndarray]:
        """The terminal-cost closure's batch twin, per row of a batch (#948).

        ``row_cost`` IS the scalar closure's accumulation — the one
        function both twins run, per row — so the twin cannot diverge from
        the scalar closure by configuration or by arithmetic. The per-row
        loop that remains is the contract, not a leftover: the store
        accumulation's scalar form is Python's builtin ``sum``,
        Neumaier-compensated on CPython 3.12+, and a vectorized
        accumulation computed plain left-to-right adds — the twin this
        method had before #948 round 7 — differed from it by 1-2 ulp on
        CI's 3.14 runner at interior iterates (every other term
        bit-identical, trajectories bit-identical), which was enough to
        re-plan the solve from step 35 on. That is the ``fixer.md``
        step-15 rule applied one level up: a reduction whose scalar form
        is a Python builtin is not elementwise end to end, however few
        terms it has — parity forbids removing this loop, and R9 F2.5
        (RC-rca2) does not: what it removes is the per-row Python around
        the sum. The store terms are computed elementwise over the whole
        batch (exact IEEE arithmetic, the same bits the scalar closure's
        list comprehension produces — see ``_terminal_row_cost``) and
        converted with one ``tolist``, instead of a name-keyed ends dict
        and a per-store walk in Python per row; the round-9 recompute RCA
        measured that loop at 2-3 % of every solve. What remains per row
        is the builtin sum over at most four floats — the recorded
        partial, priced in the F2.5 pull request. ``np.where(d > 0.0, d,
        0.0)`` is Python's ``max(0.0, d)`` exactly, NaN included (the
        comparison is False, so 0.0 wins, as it does in ``max``).
        ``simulate_trajectory_batch`` always fills ``buffer``, so the
        scalar closure's ``buffer_temps=None`` arm has no counterpart
        here.
        """

        def cost_batch(traj: dict[str, np.ndarray]) -> np.ndarray:
            n_rows = traj["room"].shape[0]
            terms = np.stack([
                coef * np.where(
                    (d := cap - traj[name][:, -1]) > 0.0, d, 0.0
                )
                for coef, name, cap in term_spec
            ], axis=1)
            rows = terms.tolist()
            out = np.empty(n_rows)
            for b in range(n_rows):
                out[b] = row_cost(rows[b])
            return out
        return cost_batch

    def _zone_setpoints(
        self, power: np.ndarray
    ) -> tuple[list[float], list[float]]:
        """Per-zone setpoints implied by a power schedule.

        Empty in single-zone mode, where there is only one setpoint series.
        """
        if not self.model.params.two_zone_enabled:
            return [], []

        span = self.config.max_temp - self.config.min_temp

        upper: list[float] = []
        lower: list[float] = []
        for value in power:
            p_norm = _power_fraction(value, self.model.params)
            upper.append(round(float(self.config.min_temp + p_norm * span), 1))
            lower.append(
                round(float(self.config.min_temp + p_norm * (span + 1.0)), 1)
            )
        return upper, lower

    def _build_result(
        self,
        h: _Horizon,
        *,
        space_power: np.ndarray,
        trajectories: tuple[Any, ...],
        status: str,
        predicted_cost: float,
        baseline_cost: float,
        savings: float,
        deferred_cost: float,
        dhw_power: np.ndarray | None = None,
        dhw_temps: np.ndarray | None = None,
        dhw_cost: float = 0.0,
        baseline_power: np.ndarray | None = None,
        buffer_temps: np.ndarray | None = None,
        wood_temps: np.ndarray | None = None,
        predictive_info: dict[str, Any] | None = None,
        objective_value: float = float("nan"),
        dhw_in_window: np.ndarray | None = None,
        dhw_ready: np.ndarray | None = None,
        dhw_legionella_step: int | None = None,
        dhw_floors: np.ndarray | None = None,
    ) -> OptimizationResult:
        """Assemble the result both solve paths return.

        Roughly thirty field assignments that were previously written out twice
        and had already begun to diverge — the DHW path was carrying fields the
        space-only path had quietly stopped setting. Anything genuinely
        specific to hot water arrives through the optional arguments.
        """
        import time

        room_temps, slab_temps, upper_temps, lower_temps = trajectories
        total_power = (
            space_power if dhw_power is None else space_power + dhw_power
        )
        # Only the start-time-independent baseline array is wanted here; the
        # previous ``_grid_terms(h.n_steps, h.dt)`` call built offset-0
        # cycling/capacity closures just to discard them, and read as if the
        # published grid figures were folded without the anchor. They are
        # not: ``_grid_report`` below gets ``h.start_time``.
        baseline_load = self.config.baseline_load_array(h.n_steps)
        grid = self._grid_report(total_power, baseline_load, h.dt, h.start_time)
        upper_setpoints, lower_setpoints = self._zone_setpoints(space_power)
        two_zone = self.model.params.two_zone_enabled

        return OptimizationResult(
            power_schedule=space_power.tolist(),
            room_temp_trajectory=room_temps.tolist(),
            slab_temp_trajectory=slab_temps.tolist(),
            buffer_temp_trajectory=(
                [float(v) for v in buffer_temps]
                if buffer_temps is not None
                and mixing_valve.is_throttling(self.model.params.mixing_valve_mode)
                else []
            ),
            valve_target_schedule=(
                [float(v) for v in h.valve_targets]
                if h.valve_targets is not None
                else []
            ),
            wood_temp_trajectory=(
                [float(v) for v in wood_temps]
                if wood_temps is not None
                and self.model.params.two_tank_modelled
                else []
            ),
            objective_value=objective_value,
            timestamps=h.timestamps,
            prices=h.prices.tolist(),
            outdoor_temps=h.outdoor_temps.tolist(),
            predicted_cost=predicted_cost,
            baseline_cost=baseline_cost,
            predicted_savings=savings,
            savings_percentage=_savings_percentage(savings, baseline_cost),
            deferred_energy_cost=deferred_cost,
            optimal_setpoints=self._power_to_setpoints(
                space_power, room_temps[:-1], h.outdoor_temps
            ),
            status=status,
            solve_time_ms=(time.monotonic() - h.t_start) * 1000,
            displace_schedule=self._power_to_displace_schedule(
                space_power, h.outdoor_temps, h.forecast
            ),
            heat_pump_on_schedule=self._power_to_heat_pump_schedule(
                space_power, dhw_power
            ),
            upper_temp_trajectory=upper_temps.tolist(),
            lower_temp_trajectory=lower_temps.tolist(),
            solar_gain_trajectory=[
                self.model.compute_solar_gain(sr) for sr in h.solar_radiation
            ],
            upper_setpoints=upper_setpoints,
            lower_setpoints=lower_setpoints,
            dhw_power_schedule=(
                dhw_power.tolist() if dhw_power is not None else []
            ),
            baseline_power_schedule=_baseline_power_list(baseline_power),
            dhw_temp_trajectory=(
                dhw_temps.tolist() if dhw_temps is not None else []
            ),
            dhw_heating_cost=dhw_cost,
            space_reasons=_mark_blocked_reasons(
                _mark_manual_reasons(
                    classify_space_steps(
                        space_power,
                        h.prices,
                        upper_temps if two_zone else room_temps,
                        h.temp_min_bounds,
                        h.heat_loss_factors,
                        self._pv_surplus,
                        h.n_steps,
                        other=dhw_power,
                        caps=h.power_caps_extra,
                    ),
                    h.space_pins,
                ),
                h.space_blocked,
            ),
            dhw_reasons=_dhw_reason_list(
                h, space_power, dhw_power, dhw_temps, dhw_in_window, dhw_ready,
                dhw_legionella_step, dhw_floors, self._pv_surplus,
            ),
            price_known=self._price_known_list(h.n_steps),
            projected_peak_kw=grid["peak_kw"],
            peak_cost=grid["peak_cost"],
            compressor_starts=grid["starts"],
            pv_surplus=self._pv_surplus_list(h.n_steps),
            pv_self_consumed_kwh=self._pv_self_consumed(total_power, h.dt),
            predictive_info=predictive_info or {},
        )

    def _co_optimize(
        self,
        h: _Horizon,
        *,
        space_power: np.ndarray,
        dhw_power: np.ndarray,
        status: str,
        best_score: float,
        solve_space: Callable[..., Any],
        p_max: float,
        planner: DhwPlanner,
    ) -> tuple[np.ndarray, np.ndarray, str]:
        """Re-plan hot water against the space heating it competes with.

        The first DHW plan is made in ignorance of space heating, so it fills
        the cheapest hours to the compressor ceiling and pushes space heating
        into dearer ones. Now that the space profile is known, that contention
        can be priced and the tank re-planned around it.

        The second plan is adopted **only if it scores better on the same
        objective**, so this pass can never make the plan worse — which is what
        makes a single extra iteration safe rather than something that needs to
        run to convergence. The wood-tank coil (#400) re-plans here against
        the solved space heating's wood trajectory; no compressor pin required.
        """
        try:
            headroom = np.maximum(0.0, p_max - dhw_power)
            # Where space heating sits hard against the ceiling hot water left
            # it, it wanted more power than it could have; its unconstrained
            # demand there is at least the full compressor.
            pinned = (dhw_power > 1e-6) & (space_power >= headroom - 1e-3)
            wood_temps = planner._dhw_coil_wood_forecast(h, space_power, dhw_power)
            coil_replan = False
            if wood_temps is not None:
                hours = np.asarray(h.step_hours, dtype=float) % 24.0
                raw = self.model.dhw_draw_rates(hours)
                credited = planner._dhw_planner_draws(raw, wood_temps)
                coil_replan = not np.allclose(credited, raw, atol=1e-9)
            if not bool(np.any(pinned)) and not coil_replan:
                return space_power, dhw_power, status

            replanned_plan, self._dhw_requirement = planner._build_dhw_requirements(
                h,
                p_max=p_max,
                space_demand=np.where(pinned, p_max, space_power),
                p_run_cap=(
                    float(np.min(h.power_caps_extra))
                    if h.power_caps_extra is not None
                    else None
                ),
                # The first build's block (#1747): a replan without it plans
                # hot water the mode cannot make, and masks the breach.
                blocked=h.dhw_blocked,
                off_steps=h.off_steps,
                wood_temps=wood_temps,
            )
            replanned = replanned_plan.schedule
            if np.allclose(replanned, dhw_power, atol=1e-4):
                return space_power, dhw_power, status

            candidate_space, candidate_status, score = solve_space(
                replanned, space_power
            )
            if score < best_score - 1e-9:
                return candidate_space, replanned, candidate_status
        except Exception as err:  # pragma: no cover - defensive
            _LOGGER.debug("DHW/space co-optimization pass skipped: %s", err)

        return space_power, dhw_power, status

    def _energy_cost_fn(
        self, prices: np.ndarray, dt: float
    ) -> Callable[[np.ndarray], Any]:
        """Closure pricing a total electrical draw against the grid, exactly.

        Piecewise in each step's PV surplus: energy up to it displaces an
        export and costs the export compensation, everything beyond it is
        imported at the market price. An earlier formulation substituted the
        export price for the *whole* step whenever any surplus existed, so
        0.05 kW of winter sun made 6 kW of grid import look nearly free and
        the plan piled into steps with trivial surplus.

        Written inline (not as a `pv` helper) because this runs inside the
        objective, thousands of times per solve. One closure prices a 1-D
        schedule (returning a float) and a whole [B, n] batch at once
        (returning one price per row, #948). The elementwise half runs over
        the whole batch; the two SUMS per row still run through ``np.sum``
        on that row's own contiguous 1-D view -- the scalar expression --
        because a batched ``axis=`` reduce may reassociate each row's sum
        on some backends (see ``_comfort_terms_batch``), and each row must
        be bit-for-bit the scalar price of that row.
        """
        surplus = self._pv_surplus
        if surplus is None or not np.any(surplus[: len(prices)] > 1e-6):
            def grid_only_cost(total_power: np.ndarray) -> Any:
                if np.ndim(total_power) == 1:
                    return float(np.sum(prices * total_power) * dt)
                return np.array([
                    float(np.sum(prices * total_power[b]) * dt)
                    for b in range(total_power.shape[0])
                ])

            return grid_only_cost

        surplus = surplus[: len(prices)]
        margin = pv.import_margin(prices, self.config.pv_export_price)

        def energy_cost(total_power: np.ndarray) -> Any:
            if np.ndim(total_power) == 1:
                covered = margin * np.minimum(total_power, surplus)
                return float(
                    (np.sum(prices * total_power) - np.sum(covered)) * dt
                )
            return np.array([
                (
                    np.sum(prices * total_power[b])
                    - np.sum(margin * np.minimum(total_power[b], surplus))
                )
                * dt
                for b in range(total_power.shape[0])
            ])

        return energy_cost

    def _window_offset_steps(self, start_time: datetime | None, dt: float) -> int:
        """Steps until the DSO's next metering-window boundary.

        The plan rarely starts on one, and folding windows from step 0 splits
        a burst across two billed windows; see ``metering_windows``.
        """
        if start_time is None:
            return 0
        window = max(1, int(self.config.peak_window_minutes))
        phase = (start_time.hour * 60 + start_time.minute) % window
        if phase == 0:
            return 0
        return max(0, int(round((window - phase) / max(dt * 60.0, 1e-6))))

    def _grid_terms(
        self, n_steps: int, dt: float, start_time: datetime | None = None
    ) -> tuple[
        Callable[[np.ndarray], float],
        Callable[[np.ndarray], float],
        np.ndarray,
        Callable[[np.ndarray], np.ndarray],
        Callable[[np.ndarray], np.ndarray],
    ]:
        """Closures for the cycling and capacity-tariff penalties.

        Both are shared between the space-only and DHW paths. Keeping them in
        one place is not just tidiness: the previous divergence between the two
        objectives meant that simply enabling hot water changed the space
        heating objective, which is a class of bug worth designing out.

        Each scalar closure comes with its batch twin (#948), the same
        penalty over a [B, n] matrix of plans with one entry per row. The
        twins close over exactly the arguments the scalar closures close
        over -- one tariff, one offset, one factor walk -- so a twin cannot
        diverge from its scalar by configuration.
        """
        cfg = self.config
        p_max = self.model.params.max_electrical_power
        baseline = cfg.baseline_load_array(n_steps)
        offset_steps = self._window_offset_steps(start_time, dt)
        factors = self._peak_window_factors(n_steps, dt, start_time, offset_steps)
        day_kwargs = self._peak_day_kwargs(n_steps, dt, start_time, offset_steps)

        def cycling(power: np.ndarray) -> float:
            return cycling_penalty(power, cfg.cycling_cost, p_max)

        def cycling_batch(power_matrix: np.ndarray) -> np.ndarray:
            return cycling_penalty_batch(power_matrix, cfg.cycling_cost, p_max)

        # The argument list the capacity term prices a plan on, shared by
        # the scalar closure and its batch twin so the two can never
        # disagree about the tariff they are pricing. The term the SOLVER
        # minimizes is the smooth surrogate (#232/#1210): on a plateau of
        # more than peak_count tied windows a hard top-k has no
        # finite-difference gradient in any direction the bounds allow, so
        # the solver would be blind on exactly the bang-bang plan the
        # tariff exists to discourage. peak_cost_smooth's value is a
        # bounded under-approximation there; every billed or published
        # figure goes through the exact peak_cost instead (see
        # _grid_report and OptimizationResult.peak_cost).
        peak_args = (
            baseline,
            cfg.peak_threshold_kw,
            cfg.peak_price_per_kw,
            cfg.peak_window_minutes,
            dt,
            cfg.peak_count,
            offset_steps,
        )

        def capacity(total_power: np.ndarray) -> float:
            return peak_cost_smooth(
                total_power, *peak_args, window_factors=factors, **day_kwargs
            )

        def capacity_batch(total_power_matrix: np.ndarray) -> np.ndarray:
            return peak_cost_batch(
                total_power_matrix, *peak_args, window_factors=factors,
                **day_kwargs,
            )

        return cycling, capacity, baseline, cycling_batch, capacity_batch

    def _peak_window_factors(
        self,
        n_steps: int,
        dt: float,
        start_time: datetime | None,
        offset_steps: int,
    ) -> np.ndarray | None:
        """Per-window billing factors for the #13 masks, or None unmasked.

        Composed from the same ``CapacityTariff.sample_factor`` the realised
        tracker uses. That alone never settled which *instant* each window is
        sampled at, which is where they actually diverged (#777); the agreement
        rests on ``window_factors`` walking the windows in UTC, the same rule
        ``_utc_step_starts`` applies to the step grid this power array is
        indexed on.
        """
        cfg = self.config
        mask = CapacityTariff(
            enabled=True,
            window_minutes=cfg.peak_window_minutes,
            months=frozenset(cfg.peak_months or ()),
            peak_hours=tuple(cfg.peak_hours or ()),
            weekdays_only=bool(cfg.peak_weekdays_only),
            offpeak_factor=float(cfg.peak_offpeak_factor),
        )
        n_windows = metering_windows(
            np.zeros(n_steps), cfg.peak_window_minutes, dt, offset_steps
        ).size
        return window_factors(mask, start_time, n_windows, dt)

    def _peak_day_kwargs(
        self,
        n_steps: int,
        dt: float,
        start_time: datetime | None,
        offset_steps: int,
    ) -> dict[str, Any]:
        """The distinct-days rule and each plan window's day, for peak_cost.

        Dated by ``plan_window_days``, which walks the windows exactly as
        ``window_factors`` does, so a window's day and its billing factor
        are read at the same real instant (#1512).
        """
        cfg = self.config
        n_windows = metering_windows(
            np.zeros(n_steps), cfg.peak_window_minutes, dt, offset_steps
        ).size
        days = (
            None if start_time is None
            else plan_window_days(n_windows, cfg.peak_window_minutes, start_time)
        )
        return {
            "window_days": days,
            "distinct_days": bool(cfg.peak_distinct_days),
        }

    # ------------------------------------------------------------------
    # Predictive weather analysis
    # ------------------------------------------------------------------

    def _analyze_forecast_trajectory(
        self,
        solar_radiation: np.ndarray,
        wind_speeds: np.ndarray,
        precipitation: np.ndarray,
        outdoor_temps: np.ndarray,
        dt_hours: float,
    ) -> dict[str, Any]:
        """Summarise the forecast into a few scalar anticipation signals.

        The real anticipation lives in the trajectory simulation, which
        applies forecast solar gain and wind/rain loss factors step by step;
        these scalars only shape the solver's *initial guess* and give the
        log a one-line summary of what the horizon looks like.
        """
        n = len(solar_radiation)
        if n == 0:
            return {
                "future_solar_energy_kwh": 0.0,
                "solar_peak_indices": [],
                "pre_heat_urgency": 0.5,
                "solar_reduction_factor": 1.0,
                "wind_anticipation_factor": 1.0,
                "rain_anticipation_factor": 1.0,
            }

        # --- Solar analysis ---
        # Compute total solar gain over the horizon
        solar_gains_kw = np.array([
            self.model.compute_solar_gain(sr) for sr in solar_radiation
        ])
        total_solar_energy = float(np.sum(solar_gains_kw) * dt_hours)  # kWh

        # Find peak solar periods (>200 W/m² is significant)
        solar_peak_mask = solar_radiation > 200.0
        solar_peak_indices = np.where(solar_peak_mask)[0].tolist()

        # Solar energy in the FUTURE (next 6-24 hours)
        # Weight more heavily the solar coming in the next 6-12 hours
        n_6h = min(int(6 / dt_hours), n)
        n_12h = min(int(12 / dt_hours), n)
        future_solar_6_12h = float(np.sum(solar_gains_kw[n_6h:n_12h]) * dt_hours)

        # If lots of solar is coming in 6-12h, reduce current heating
        # The slab has enough thermal mass to coast through to solar period
        typical_heat_loss = (  # the learned scale too, as the dynamics (D2-s2-01)
            self.model.params.heat_loss_coefficient
            * self.model.params.house_heat_loss_scale
            * (self.config.target_temp - np.mean(outdoor_temps))
        )
        if typical_heat_loss > 0:
            solar_fraction = min(future_solar_6_12h / max(typical_heat_loss * 6, 0.1), 1.0)
        else:
            solar_fraction = 0.0

        # Solar reduction factor: 1.0 = no reduction, 0.5 = reduce heating by 50%
        # Only reduce slab pre-heating, not immediate comfort heating
        solar_reduction = 1.0 - 0.4 * solar_fraction  # max 40% reduction

        # --- Wind analysis ---
        # Look at future wind speeds and compute anticipated heat loss increase
        wind_weights = np.exp(-np.arange(n) * dt_hours / 12.0)  # decay over 12h
        wind_weights /= wind_weights.sum()
        avg_future_wind = float(np.sum(wind_speeds * wind_weights))
        wind_anticipation = 1.0 + self.model.params.wind_sensitivity * avg_future_wind

        # --- Rain analysis ---
        # Upcoming rain increases heat loss
        rain_weights = np.exp(-np.arange(n) * dt_hours / 12.0)
        rain_weights /= rain_weights.sum()
        avg_future_precip = float(np.sum(precipitation * rain_weights))
        rain_anticipation = 1.0
        if avg_future_precip > 0.1:
            rain_intensity = min(avg_future_precip / 2.0, 1.0)
            rain_anticipation = 1.0 + (
                self.model.params.rain_heat_loss_multiplier - 1.0
            ) * rain_intensity

        # --- Pre-heat urgency ---
        # High if bad weather (wind + rain) is coming AND cheap electricity now
        # Low if sunny weather is coming (solar will help)
        pre_heat_urgency = min(1.0, max(0.0,
            (wind_anticipation - 1.0) * 3.0 +
            (rain_anticipation - 1.0) * 5.0 -
            (1.0 - solar_reduction) * 2.0
        ))

        return {
            "future_solar_energy_kwh": total_solar_energy,
            "solar_peak_indices": solar_peak_indices,
            "pre_heat_urgency": pre_heat_urgency,
            "solar_reduction_factor": solar_reduction,
            "wind_anticipation_factor": wind_anticipation,
            "rain_anticipation_factor": rain_anticipation,
            "avg_future_wind_ms": avg_future_wind,
            "avg_future_precip_mmh": avg_future_precip,
            "future_solar_6_12h_kwh": future_solar_6_12h,
        }

    # ------------------------------------------------------------------
    # Main optimization
    # ------------------------------------------------------------------

    def optimize(self, *, inputs: SolveInputs) -> OptimizationResult:
        """Run the MPC optimization with predictive weather anticipation.

        This is the CORE of true MPC: the optimizer uses the FULL 24-hour
        forecast trajectory (solar, wind, rain, temperature) to make decisions
        about CURRENT actions. It doesn't just react to current conditions.

        Key anticipatory behaviors:
        - Reduces pre-heating before forecasted sunny periods
        - Increases pre-heating before forecasted windy/rainy periods
        - Coordinates DHW heating with space heating and electricity prices

        The forecast's ``prices`` are the raw import prices. Where its
        ``pv_surplus`` forecasts spare production, the objectives price
        consumption piecewise — the surplus-covered energy at
        ``config.pv_export_price``, the rest at the import price — so a step
        with trivial sun is not repriced wholesale. ``price_known`` marks which
        steps rest on published market data rather than on the learned
        diurnal prior.

        The limits' ``space_blocked`` / ``dhw_blocked`` say that the heat
        pump's *observed operating mode* cannot serve that channel at all — a
        unit in ``heat`` makes no hot water, a unit in ``DHW`` or ``cool``
        heats no rooms. They are not a preference and not a manual pin: the
        pin-safety loop below releases forced-off pins when a floor would be
        breached, and doing that here would put back power the hardware
        refuses to draw. So a blocked channel stays blocked, its floor is left
        unmet, and the reason codes say ``pump_mode`` rather than ``idle`` so
        the shortfall is visible instead of looking like the optimizer
        declining to run. Both default to False, which is byte-for-byte the
        previous behaviour.
        """
        import time

        t_start = time.monotonic()
        initial_state, start_time = inputs.state, inputs.start_time
        series, limits = inputs.forecast, inputs.limits
        prices, outdoor_temps = series.prices, series.outdoor_temps
        wind_speeds, precipitation = series.wind_speeds, series.precipitation
        solar_radiation, humidity = series.solar_radiation, series.humidity
        price_known, pv_surplus = series.price_known, series.pv_surplus
        price_sigma, external_heat_kw = series.price_sigma, series.external_heat_kw
        space_pins, dhw_pins = limits.space_pins, limits.dhw_pins
        power_caps_extra = limits.power_caps_extra
        min_temp_margins, min_temp_floors = limits.min_temp_margins, limits.min_temp_floors
        space_blocked, dhw_blocked = limits.space_blocked, limits.dhw_blocked
        off_steps, quiet_actions = limits.off_steps, limits.quiet_actions

        n_steps = min(len(prices), len(outdoor_temps), self.config.n_steps)
        dt = self.config.dt_hours

        wind_speeds, precipitation, solar_radiation = weather_or_calm(
            n_steps, wind_speeds, precipitation, solar_radiation
        )
        if price_known is None:
            price_known = np.ones(n_steps, dtype=bool)
        if pv_surplus is None:
            pv_surplus = np.zeros(n_steps)

        if start_time is None:
            start_time = datetime.now()

        # Truncate arrays to n_steps
        prices = prices[:n_steps]
        outdoor_temps = outdoor_temps[:n_steps]
        wind_speeds = wind_speeds[:n_steps]
        precipitation = precipitation[:n_steps]
        solar_radiation = solar_radiation[:n_steps]
        prices = self._stash_price_horizon(
            initial_state, n_steps, price_known, price_sigma, prices, pv_surplus
        )
        # One hot-water planner per solve, from this solve's inputs (#1743).
        planner = DhwPlanner(
            self.model, self.config, self._pv_surplus, self._price_known
        )

        # Forecast humidity (#21), normalised to horizon length; short
        # series pad with NaN, which the model reads as "unknown, use the
        # ambient value" — never as 0 % humidity. An all-NaN series is the
        # same as none at all, and dropping it keeps the objective's inner
        # loop free of per-step lookups that can only fall back.
        if humidity is not None:
            hum = np.asarray(humidity, dtype=float)
            if hum.size < n_steps:
                hum = np.concatenate(
                    [hum, np.full(n_steps - hum.size, np.nan)]
                )
            humidity = hum[:n_steps]
            if not np.any(np.isfinite(humidity)):
                humidity = None

        # Free-heat forecast, normalised to horizon length like the arrays
        # above. All-zero is the same as none at all, and is treated so.
        if external_heat_kw is not None:
            external_heat_kw = _padded_nonneg(external_heat_kw, n_steps)
            if not np.any(external_heat_kw > 0.0):
                external_heat_kw = None

        # --- Analyze forecast trajectory for predictive signals ---
        forecast_analysis = self._analyze_forecast_trajectory(
            solar_radiation, wind_speeds, precipitation, outdoor_temps, dt
        )

        _LOGGER.debug(
            "Predictive analysis: solar_reduction=%.2f, wind_factor=%.2f, "
            "rain_factor=%.2f, pre_heat_urgency=%.2f, future_solar=%.1f kWh",
            forecast_analysis["solar_reduction_factor"],
            forecast_analysis["wind_anticipation_factor"],
            forecast_analysis["rain_anticipation_factor"],
            forecast_analysis["pre_heat_urgency"],
            forecast_analysis["future_solar_energy_kwh"],
        )

        dhw_enabled = self.model.params.dhw_enabled

        # Hour of day at each step. Computed once: the comfort target, both
        # temperature bounds and the DHW draw pattern all key off it, and it
        # was previously rebuilt from scratch for each of the four.
        step_datetimes = _utc_step_starts(start_time, n_steps, timedelta(hours=dt))
        step_hours = np.array([
            d.hour + d.minute / 60.0 for d in step_datetimes
        ])
        # Weekday per step, for weekly DHW windows (#3) and the per-weekday
        # overrides (#1260); the helper returns None unless either is
        # configured, so the flat no-override install pays nothing.
        step_weekdays = _dhw_step_weekdays(
            self.model.params, step_datetimes, dt
        )
        holiday_flags = _holiday_flags_for(
            step_datetimes, self.config.holiday_dates
        )

        comfort_targets, temp_min_bounds, temp_max_bounds = (
            self._build_comfort_bounds(
                step_hours, n_steps, min_temp_margins, min_temp_floors,
                step_datetimes,
            )
        )

        # Per-step solar gain, and the wind/rain multiplier on heat loss. Both
        # use the *forecast* at each future step rather than current
        # conditions, which is what makes the control anticipatory.
        solar_gains_per_step = np.array([
            self.model.compute_solar_gain(sr) for sr in solar_radiation
        ])
        base_loss = max(self.model.params.heat_loss_coefficient, 0.001)
        forecast_heat_loss_factors = np.array([
            self.model.effective_heat_loss_coefficient(
                self.model.params.heat_loss_coefficient,
                wind_speeds[i],
                precipitation[i],
            )
            / base_loss
            for i in range(n_steps)
        ])

        # --- Manual plan pins ------------------------------------------
        # Normalise both channels to writable float arrays of horizon length so
        # the safety-release loop below can relax individual steps in place. A
        # channel left ``None`` stays fully automatic and costs nothing.
        space_pins = self._normalise_pins(space_pins, n_steps)
        dhw_pins = self._normalise_pins(dhw_pins, n_steps)
        self._dhw_requirement = None
        released_space: set[int] = set()
        released_dhw: set[int] = set()

        throttling, power_caps, caps_extra_arr = self._build_space_power_caps(
            n_steps, power_caps_extra, space_blocked, off_steps
        )

        # Per-step valve target schedule, set by the hold-candidate pass below
        # and read by every solve and re-simulation through the closure.
        valve_targets: np.ndarray | None = None

        # Solve, then check the solved trajectory against the hard safety lines,
        # release any forced-off pin that would breach one, and solve again.
        # The comfort and tank floors are *soft* penalties in the objective, so
        # clamping a step off does not actually protect the house or tank — only
        # re-solving with the offending pin freed does.
        def _solve(
            extra_starts: tuple[np.ndarray, ...] | None = None,
        ) -> OptimizationResult:
            horizon = _Horizon(
                initial_state=initial_state,
                prices=prices,
                outdoor_temps=outdoor_temps,
                wind_speeds=wind_speeds,
                precipitation=precipitation,
                solar_radiation=solar_radiation,
                start_time=start_time,
                n_steps=n_steps,
                dt=dt,
                comfort_targets=comfort_targets,
                temp_min_bounds=temp_min_bounds,
                temp_max_bounds=temp_max_bounds,
                step_hours=step_hours,
                step_weekdays=step_weekdays,
                holiday_flags=holiday_flags,
                solar_gains=solar_gains_per_step,
                heat_loss_factors=forecast_heat_loss_factors,
                forecast=forecast_analysis,
                t_start=t_start,
                space_pins=space_pins,
                dhw_pins=dhw_pins,
                power_caps=power_caps,
                power_caps_extra=caps_extra_arr,
                external_heat_kw=external_heat_kw,
                valve_targets=valve_targets,
                humidity=humidity,
                space_blocked=space_blocked,
                dhw_blocked=dhw_blocked,
                off_steps=off_steps,
                extra_starts=extra_starts,
            )
            if dhw_enabled:
                return self._optimize_with_dhw(horizon, planner)
            return self._optimize_space_only(horizon)

        # #1295: the plan the caller hands in -- the coordinator seeds it from
        # the last shipped plan -- is one extra candidate on the FIRST solve
        # only; ``_warm_start_starts`` says why later solves get none.
        result = _solve(self._warm_start_starts(n_steps))

        # A blocked channel is withheld from the release loop entirely. Its
        # floor IS breached — that is the whole point, and the plan reports it
        # — so the loop would dutifully free every forced-off pin on that
        # channel, re-solve to the identical (still blocked) schedule, and
        # then report those slots as "released for safety". None of that is
        # true, and the user would be told the optimizer overrode their
        # manual plan when it did nothing of the kind.
        release_space = None if space_blocked else space_pins
        release_dhw = None if dhw_blocked else dhw_pins

        if release_space is not None or release_dhw is not None:
            # Every release must be followed by a re-solve: releasing a pin and
            # then returning the plan that was built *with* it would hand back a
            # schedule already known to be unsafe, while reporting the step as
            # released. Bounded so a physically infeasible plan cannot spin.
            for _ in range(_SAFETY_REPAIR_ROUNDS):
                rel_s, rel_d = self._safety_release_steps(
                    result, temp_min_bounds, release_space, release_dhw
                )
                if not rel_s and not rel_d:
                    break
                # PER CHANNEL, because the two are independent: a caller may
                # pin space and leave hot water unpinned, which
                # tests/manual_plan.py does -- an earlier form of this
                # narrowing asserted both existed and that test failed on it.
                # `rel_s` is empty whenever `release_space` is None, so the
                # guard changes nothing it runs; it is what lets the writes
                # below be checked rather than suppressed. Two decision
                # points, the raise the owner granted on 2026-09-11.
                if space_pins is not None:
                    for i in rel_s:
                        space_pins[i] = float("nan")
                        released_space.add(i)
                if dhw_pins is not None:
                    for i in rel_d:
                        dhw_pins[i] = float("nan")
                        released_dhw.add(i)
                result = _solve()
            else:
                # Out of repair rounds. If anything is still breaching, abandon
                # the forced-off pins wholesale rather than return a plan that
                # leaves the house or the tank below its limit: the user asked
                # for timing, not for the heating to be unsafe.
                rel_s, rel_d = self._safety_release_steps(
                    result, temp_min_bounds, release_space, release_dhw
                )
                if rel_s or rel_d:
                    # Only the channel that is actually breaching is abandoned.
                    # Discarding the other one as well would throw away an
                    # arrangement that was never unsafe -- letting the pump heat
                    # in exactly the expensive hours the user excluded -- and
                    # then report those slots as released for safety, which
                    # would not be true.
                    for name, pins, released, breaching in (
                        ("space", release_space, released_space, bool(rel_s)),
                        ("hot water", release_dhw, released_dhw, bool(rel_d)),
                    ):
                        if pins is None or not breaching:
                            continue
                        for i in range(len(pins)):
                            value = float(pins[i])
                            if not _pin_is_free(value) and value < 0.5:
                                pins[i] = float("nan")
                                released.add(i)
                        _LOGGER.warning(
                            "Manual %s plan could not be made safe in %d "
                            "rounds; releasing every forced-off slot on that "
                            "channel and planning it freely",
                            name,
                            _SAFETY_REPAIR_ROUNDS,
                        )
                    result = _solve()

        # --- The hold candidate: can a commanded valve wait for the peak? ---
        #
        # A fixed-curve valve starts feeding the house the moment the tank is
        # warmer than the curve, so storage mostly shifts the hours right
        # after charging (measured in v3.10.0 at roughly a fifth of the
        # analytical value). A valve the optimizer can *command* does not have
        # to: lower the curve to the comfort floor between charging and the
        # price peak and the tank holds its heat for when it is worth most.
        #
        # The schedule is a derived candidate, not a rule: it is guessed from
        # the structure of the solved plan, re-solved in full, and adopted
        # only if it beats the fixed target on the same objective -- exactly
        # `_co_optimize`'s discipline, and what makes a heuristic safe here.
        # At flat prices no candidate is even proposed, which is the null
        # control. Gated on smart_write (no other mode can actuate it), on
        # the tank being a real store, and away from manual pins -- the
        # pin-safety loop above has already finished, and a hand-pinned day
        # is not the day to get clever with the valve.
        if (
            self.model.params.mixing_valve_mode == mixing_valve.MODE_SMART_WRITE
            and self.model.params.buffer_is_store
            and space_pins is None
            and dhw_pins is None
            and np.isfinite(result.objective_value)
        ):
            schedule = self._derive_hold_schedule(
                np.asarray(result.power_schedule), prices, temp_min_bounds
            )
            if schedule is not None:
                fixed_objective = result.objective_value
                valve_targets = schedule
                candidate = _solve()
                if (
                    np.isfinite(candidate.objective_value)
                    and candidate.objective_value < fixed_objective - 1e-9
                ):
                    result = candidate
                    _LOGGER.debug(
                        "Valve hold schedule adopted: objective %.3f -> %.3f",
                        fixed_objective,
                        candidate.objective_value,
                    )
                else:
                    valve_targets = None

        if power_caps is not None and throttling:
            result = self._repair_throttled_buffer_caps(
                WeatherSeries(
                    outdoor_temps=outdoor_temps,
                    wind_speeds=wind_speeds,
                    precipitation=precipitation,
                    solar_radiation=solar_radiation,
                    humidity=humidity,
                    external_heat_kw=external_heat_kw,
                ),
                initial_state, result, power_caps, dt,
                prices, step_hours, valve_targets, _solve,
            )

        result.manual_pins_active = space_pins is not None or dhw_pins is not None
        result.manual_released_space = sorted(released_space)
        result.manual_released_dhw = sorted(released_dhw)
        result.mode_blocked_space = bool(space_blocked)
        result.mode_blocked_dhw = bool(dhw_blocked)

        existing_info = result.predictive_info if result.predictive_info else {}
        result.predictive_info = {**forecast_analysis, **existing_info}

        self._publish_breach_reports(
            result, power_caps_extra, space_blocked, dhw_blocked, n_steps,
            temp_min_bounds, off_steps, quiet_actions,
        )
        return result

    def _warm_start_starts(self, n_steps: int) -> tuple[np.ndarray, ...] | None:
        """The caller's previous plan as one extra candidate (#1295).

        The optimizer keeps no memory of its own solves, so this is an input:
        ``_prev_shipped_plan`` is set by the caller that knows the previous
        plan -- in production ``coordinator._warm_seeded``, which rebuilds this
        optimizer every solve and so is the only seat that can carry the plan
        across an MPC cycle. L-BFGS-B is then restarted from that point, a lead
        no structural seed reproduces. It is the previous plan on its own
        clock: the caller hands it at offset 0, not shifted by the steps
        elapsed since it was made. It is a *candidate*, not a warm start
        that bypasses the multi-start -- ``_multi_start_minimize`` scores it
        against every structural seed and keeps the cheapest, so a stale or
        wrong-shaped plan can lose, never win.

        It rides on the FIRST solve of a call only: the pin-release loop and
        the cap-tighten repair correct a plan the caller already changed, not
        fresh re-plans, so an extra candidate there would buy solves and no
        plan.

        A different step count means the caller is planning a different
        horizon (the coordinator's own horizon is fixed, but a service call or
        a test need not match it), and a plan of the wrong width is dropped
        rather than clipped or padded into a plausible-looking guess.
        """
        prev = getattr(self, "_prev_shipped_plan", None)
        if prev is None or len(prev) != n_steps:
            return None
        return (np.asarray(prev, dtype=float),)

    def _stash_price_horizon(
        self,
        initial_state: ThermalState,
        n_steps: int,
        price_known: np.ndarray,
        price_sigma: np.ndarray | None,
        prices: np.ndarray,
        pv_surplus: np.ndarray,
    ) -> np.ndarray:
        """Pad known-mask and surplus, stash the buffer seed, risk-adjust prices."""
        price_known = np.asarray(price_known, dtype=bool)[:n_steps]
        pv_surplus = np.asarray(pv_surplus, dtype=float)[:n_steps]
        if price_known.size < n_steps:
            price_known = np.concatenate(
                [price_known, np.zeros(n_steps - price_known.size, dtype=bool)]
            )
        if pv_surplus.size < n_steps:
            pv_surplus = np.concatenate(
                [pv_surplus, np.zeros(n_steps - pv_surplus.size)]
            )

        self._price_known = price_known
        self._initial_buffer_temp = (
            float(initial_state.buffer_tank_temperature)
            if self.model.params.buffer_is_store
            and initial_state.buffer_tank_temperature is not None
            else None
        )
        self._pv_surplus = pv_surplus

        # Risk-adjusted pricing on the unpublished horizon (#34). The prior
        # fills unknown steps with its mean, so the optimizer treats a
        # guessed trough as bankable; the error is asymmetric — a trough
        # that fails to appear forces buying at a peak, while charging
        # slightly early costs only standby loss. Deferral into guessed
        # steps therefore pays λ·sigma on top of the mean; known steps carry
        # sigma 0 by construction and λ defaults to 0, which skips this
        # entirely and leaves the array untouched.
        if price_sigma is not None and self.config.price_risk_lambda > 0.0:
            risk = self.config.price_risk_lambda * _padded_nonneg(price_sigma, n_steps)
            risk = np.where(price_known, 0.0, risk)
            if np.any(risk > 0.0):
                prices = np.asarray(prices, dtype=float) + risk
        return prices

    def _build_comfort_bounds(
        self,
        step_hours: np.ndarray,
        n_steps: int,
        min_temp_margins: np.ndarray | None,
        min_temp_floors: np.ndarray | None,
        step_times: list[datetime] | None = None,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """The per-step comfort target and the band the solve must stay in."""
        times = list(step_times) if step_times is not None else []
        comfort_targets = np.array(
            [
                self.config.get_comfort_temp(
                    hour, when=times[i] if i < len(times) else None
                )
                for i, hour in enumerate(step_hours)
            ]
        )
        bounds = [
            self.config.get_temp_bounds(
                hour, when=times[i] if i < len(times) else None
            )
            for i, hour in enumerate(step_hours)
        ]
        temp_min_bounds = np.array([low for low, _ in bounds])
        temp_max_bounds = np.array([high for _, high in bounds])

        # T5 (#16 #54): the comfort floor's two adjustments, both optional
        # and both applied HERE — the single site where the bounds are
        # built — so every consumer (objectives, safety releases, pin
        # repair) sees the same effective floor. ``min_temp_margins`` is a
        # per-step raise (the model's own expected error at that lead);
        # ``min_temp_floors`` an absolute per-step floor (the mold guard).
        # None for both is byte-for-byte the previous bounds.
        if min_temp_margins is not None or min_temp_floors is not None:
            if min_temp_margins is not None:
                temp_min_bounds = temp_min_bounds + _padded_nonneg(min_temp_margins, n_steps)
            if min_temp_floors is not None:
                f = np.asarray(min_temp_floors, dtype=float)
                if f.size < n_steps:
                    f = np.concatenate(
                        [f, np.full(n_steps - f.size, -np.inf)]
                    )
                temp_min_bounds = np.maximum(temp_min_bounds, f[:n_steps])
            # Whatever raised the floor, the band never squeezes shut: a
            # floor at or above the ceiling makes the solve infeasible and
            # the comfort penalty unbounded.
            temp_min_bounds = np.minimum(
                temp_min_bounds, temp_max_bounds - 0.5
            )
        return comfort_targets, temp_min_bounds, temp_max_bounds

    def _build_space_power_caps(
        self,
        n_steps: int,
        power_caps_extra: np.ndarray | None,
        space_blocked: bool,
        off_steps: np.ndarray | None = None,
    ) -> tuple[bool, np.ndarray | None, np.ndarray | None]:
        """The per-step space-power ceiling, and whether the valve throttles."""
        # Per-step ceiling on space power, lowered by the buffer-cap loop
        # below (valve installs) and by external per-step caps (T2's fuse
        # guard and shadow solves). It exists only when a valve can charge
        # the tank OR extra caps were supplied, so every no-valve, no-cap
        # install stays byte-for-byte identical.
        throttling = mixing_valve.is_throttling(
            self.model.params.mixing_valve_mode
        )
        power_caps: np.ndarray | None = None
        caps_extra_arr: np.ndarray | None = None
        if throttling or power_caps_extra is not None or space_blocked:
            power_caps = np.full(
                n_steps, self.model.params.max_electrical_power
            )
        if space_blocked:
            # The mode gate rides the space-heating ceiling rather than being
            # a mechanism of its own: ``power_caps`` is already the one place
            # that bounds space power on both solve paths, it composes with
            # the fuse guard and the buffer cap by minimum, and — unlike a
            # pin — nothing in this function can relax it.
            power_caps = np.zeros(n_steps, dtype=float)
        off_mask = _padded_mask(off_steps, n_steps)
        if off_mask is not None:
            # #1910 (D1): a quiet Off window's space half rides the SAME
            # array, as a deliberate zero at exactly its own steps. The zero
            # is not floored — refusing to plan is the point of the window —
            # and it survives the elementwise minimum below because the
            # extra caps are clipped to >= 0.
            if power_caps is None:
                power_caps = np.full(
                    n_steps, self.model.params.max_electrical_power
                )
            power_caps = np.where(off_mask, 0.0, power_caps)
        if power_caps_extra is not None:
            # The branch above ran for this same condition, so the ceiling
            # exists; the minimum below is against a real array.
            assert power_caps is not None
            extra = np.clip(
                np.asarray(power_caps_extra, dtype=float), 0.0, None
            )
            if extra.size < n_steps:
                extra = np.concatenate(
                    [
                        extra,
                        np.full(
                            n_steps - extra.size,
                            self.model.params.max_electrical_power,
                        ),
                    ]
                )
            caps_extra_arr = extra[:n_steps]
            power_caps = np.minimum(power_caps, caps_extra_arr)
        return throttling, power_caps, caps_extra_arr

    def _publish_breach_reports(
        self,
        result: OptimizationResult,
        power_caps_extra: np.ndarray | None,
        space_blocked: bool,
        dhw_blocked: bool,
        n_steps: int,
        temp_min_bounds: np.ndarray,
        off_steps: np.ndarray | None = None,
        quiet_actions: np.ndarray | None = None,
    ) -> None:
        """Publish the cap and mode-block breach figures onto ``result``.

        Runs once, after the solve, so nothing here is in a per-solve hot
        loop. Each key is added only when its cap or block is actually in
        force, which is what leaves an ordinary install — and every golden
        fixture — with byte-identical ``predictive_info``. A quiet Off
        window (#1910) reports through the same space figure — its floor
        shortfall is the price the plan knowingly paid for the window — and
        carries the resolved per-step quiet actions beside it, for the plan
        sensor to draw.
        """
        if _space_breach_due(
            power_caps_extra, space_blocked, off_steps, n_steps
        ):
            trajectory = np.asarray(
                result.upper_temp_trajectory
                if self.model.params.two_zone_enabled
                and result.upper_temp_trajectory
                else result.room_temp_trajectory,
                dtype=float,
            )
            # Trajectories carry n+1 entries with index 0 the *initial*
            # state — the same convention the objectives use (`room_t[1:]`
            # vs bounds). Judging the starting temperature against the cap
            # would blame the fuse for the weather; dropping the last step
            # would miss a breach at the horizon's edge.
            planned = trajectory[1:] if trajectory.size > n_steps else trajectory
            steps = min(planned.size, temp_min_bounds.size)
            breach = 0.0
            if steps > 0:
                breach = float(
                    np.max(
                        np.clip(
                            temp_min_bounds[:steps] - planned[:steps],
                            0.0,
                            None,
                        )
                    )
                )
            result.predictive_info["power_cap_breach_c"] = round(breach, 3)

        # v5.3.0: the mode block, published rather than merely recorded.
        # Added only when a channel is actually blocked, so an install with
        # no mode entity — every golden fixture, and the overwhelming
        # majority of installs — sees byte-identical predictive_info.
        if space_blocked:
            result.predictive_info["mode_blocked_space"] = True
        if dhw_blocked:
            result.predictive_info["mode_blocked_dhw"] = True
            # The DHW analogue of ``power_cap_breach_c``, which is space-only:
            # without it a hot-water block leaves no number anywhere saying
            # how badly the tank fell short, and "the tank went cold and the
            # plan never said so" is the same failure the space figure exists
            # to prevent. Worst shortfall against the tank's own per-step
            # requirement, in °C; zero when the tank coasted through anyway.
            requirement = self._dhw_requirement
            dhw_trajectory = result.dhw_temp_trajectory
            shortfall = 0.0
            if requirement is not None and dhw_trajectory:
                req = np.asarray(requirement, dtype=float)
                planned = np.asarray(dhw_trajectory, dtype=float)
                # Same convention as the space trajectory: index 0 is the
                # initial tank temperature, not a planned one.
                planned = planned[1:] if planned.size > req.size else planned
                steps = min(planned.size, req.size)
                if steps > 0:
                    shortfall = float(
                        np.max(np.clip(req[:steps] - planned[:steps], 0.0, None))
                    )
            result.predictive_info["dhw_floor_breach_c"] = round(shortfall, 3)

        _publish_quiet_actions(result, quiet_actions, n_steps)

    def _solve_space(
        self,
        dhw_plan: np.ndarray,
        warm_start: np.ndarray | None,
        h: _Horizon,
        p_max: float,
        n_steps: int,
        dt: float,
        prices: np.ndarray,
        init_base: np.ndarray,
        objective: Callable[..., float],
        objective_batch: Callable[..., np.ndarray],
    ) -> tuple[np.ndarray, str, float]:
        """Optimize space heating around a fixed DHW schedule."""
        # The heat pump serves one circuit at a time, so a DHW block eats
        # into the capacity available for space heating during that step.
        headroom = np.maximum(0.0, p_max - dhw_plan)
        if h.power_caps is not None:
            headroom = np.minimum(headroom, h.power_caps)
        if h.power_caps_extra is not None:
            # power_caps bounds space heating alone, so during a DHW block
            # space + DHW could still exceed an external *total* cap. The
            # fuse guard's whole promise is that total draw stays under
            # the limit, so subtract the block from the cap here too.
            headroom = np.minimum(
                headroom,
                np.maximum(0.0, h.power_caps_extra - dhw_plan),
            )
        guess = init_base if warm_start is None else warm_start
        guess = np.minimum(np.clip(guess, 0.0, p_max), headroom)
        bounds = [(0.0, float(headroom[i])) for i in range(n_steps)]
        # Manual space pins apply here just as in the DHW-free path. Forcing
        # a step on raises its lower bound, but only as far as the headroom
        # the DHW block left it — a slot the user pinned for both channels
        # cannot demand more than the compressor has.
        bounds = _apply_pins_to_bounds(
            bounds, h.space_pins, self._pin_on_power(p_max)
        )
        guess = self._seed_pinned_guess(guess, bounds)
        # A warm start is a genuinely good lead, so keep it first; the
        # extra structural candidates only matter on the initial solve.
        # The low-energy seed rides along for the same R1-D0-01 reason as
        # in the space-only path: without it every candidate anchors to
        # the same total energy and arbitrage days refine into one basin.
        starts = [guess]
        if h.extra_starts:
            starts = list(h.extra_starts) + starts
        if warm_start is None:
            energy = float(np.sum(np.minimum(init_base, headroom)) * dt)
            starts.append(
                np.minimum(
                    _price_ranked_start(prices, energy, p_max, dt), headroom
                )
            )
            starts.append(headroom * 0.5)
            starts.append(
                np.minimum(
                    _price_ranked_start(
                        prices,
                        energy * _LOW_ENERGY_START_FRACTION,
                        p_max,
                        dt,
                    ),
                    headroom,
                )
            )
        try:
            res = _multi_start_minimize(
                objective, starts, bounds, args=(dhw_plan,), maxiter=300,
                batch_objective=objective_batch,
            )
            power = np.clip(res.x, 0.0, headroom)
            return (
                power,
                _solver_status(
                    res, lambda x: objective(x, dhw_plan), guess
                ),
                float(objective(power, dhw_plan)),
            )
        except Exception as e:
            _LOGGER.error("Space heating optimization (with DHW) failed: %s", e)
            return (
                guess,
                f"failed ({e})",
                float(objective(guess, dhw_plan)),
            )

    @staticmethod
    def _normalise_pins(
        pins: np.ndarray | None, n_steps: int
    ) -> np.ndarray | None:
        """Copy pins to a float array of horizon length, or pass ``None`` on.

        A copy because the safety-release loop frees individual steps in place
        and must not mutate the caller's array; padded or truncated to the
        horizon so a stale-length override cannot misalign the schedule.
        """
        if pins is None:
            return None
        arr = np.full(n_steps, float("nan"), dtype=float)
        src = np.asarray(pins, dtype=float)
        take = min(n_steps, src.size)
        arr[:take] = src[:take]
        return arr

    def _derive_hold_schedule(
        self,
        power: np.ndarray,
        prices: np.ndarray,
        temp_min_bounds: np.ndarray,
    ) -> np.ndarray | None:
        """A candidate valve-target schedule: hold between charging and peak.

        Fully resolved -- every entry a real temperature. Default steps carry
        the working target (the configured static target, else the comfort
        ceiling); hold steps carry the per-step comfort floor, which is the
        lowest target the solve is allowed to plan for anyway, so a hold can
        never ask for a house the objective would not accept.

        Hold steps are the ones after charging has begun and before the last
        expensive block ends, that are neither charging nor expensive
        themselves: the stretch where a fixed-curve valve bleeds the tank into
        the house at mid prices. ``None`` -- no candidate at all -- when there
        is nothing to arbitrage: no charging, no expensive block, or a price
        spread too flat to name one. That refusal is the null control; the
        caller adopts a candidate only if it beats the fixed target on the
        same objective, so this function only has to be plausible, not right.
        """
        n = len(power)
        if n == 0 or len(prices) != n:
            return None
        # p85 rather than p75 for the peak. A real day is often a long flat
        # plateau with a short tall spike -- sixteen expensive steps in
        # ninety-six -- and at p75 the threshold lands *on* the plateau: the
        # whole day reads as expensive, the spread test then sees p75 == p25
        # and refuses a schedule on exactly the profile that most wants one.
        p25, p40, p85 = np.percentile(prices, [25, 40, 85])
        # Flat prices: nothing to arbitrage, so no candidate. The margin is
        # deliberately generous -- a 5 % spread cannot pay for a hold.
        if p85 <= p25 * 1.05:
            return None
        p_max = self.model.params.max_electrical_power
        expensive = prices >= p85
        charging = (power > 0.5 * p_max) & (prices <= p40)
        if not bool(expensive.any()) or not bool(charging.any()):
            return None

        after_charge = np.zeros(n, dtype=bool)
        seen = False
        for i in range(n):
            seen = seen or bool(charging[i])
            after_charge[i] = seen
        before_peak = np.zeros(n, dtype=bool)
        seen = False
        for i in reversed(range(n)):
            seen = seen or bool(expensive[i])
            before_peak[i] = seen

        hold = after_charge & before_peak & ~charging & ~expensive
        if not bool(hold.any()):
            return None

        params = self.model.params
        default_target = params.mixing_valve_target or params.comfort_ceiling
        targets = np.full(n, float(default_target))
        floors = np.asarray(temp_min_bounds, dtype=float)
        targets[hold] = floors[hold]
        return targets

    def _tighten_buffer_caps(
        self,
        weather: WeatherSeries,
        initial_state: ThermalState,
        result: OptimizationResult,
        power_caps: np.ndarray,
        dt: float,
        *,
        valve_targets: np.ndarray | None = None,
        start_hour: float | None = None,
    ) -> bool:
        """Lower per-step power ceilings where the plan charged a full tank.

        Re-simulates the returned space schedule and reads the heat the
        buffer cap refused at each step. A refusing step gets its ceiling cut
        to the power whose heat the tank could actually take, converted at
        that step's own COP (the flow temperature is the cap itself, since
        that is where the tank sits when it refuses). Mutates ``power_caps``
        in place, exactly as the pin-release loop mutates the pins, and
        returns whether anything changed so the caller knows to re-solve.
        """
        outdoor_temps = weather.outdoor_temps
        humidity = weather.humidity
        schedule = np.asarray(result.power_schedule, dtype=float)
        _, _, _, _, _, refused, _ = self.model.simulate_trajectory(
            initial_state=initial_state,
            power_schedule=schedule,
            weather=weather,
            dt_hours=dt,
            valve_targets=valve_targets,
            # The refusal check must simulate the same physics the
            # objective did — with #53's profile active, flat internal
            # gains would judge the caps on a trajectory the solve does
            # not believe.
            start_hour=start_hour,
        )
        if refused is None:
            return False
        changed = False
        for i in np.nonzero(refused > 1e-9)[0]:
            # The shared marginal-COP helper (v4.0.5): this loop was the one
            # optimizer site already converting at the dynamics' flow-derated
            # convention, and the terminal/deferred valuations now draw from
            # the same code path so the three cannot drift apart again.
            cop_i = self.model.marginal_cop(
                float(outdoor_temps[i]),
                "buffer",
                store_temp=self.model.params.buffer_max_temp,
                humidity=_step_humidity(humidity, int(i)),
            )
            allowed = float(schedule[i]) - float(refused[i]) / max(cop_i, 1e-6)
            # Slightly under, or float noise re-trips the same step and burns
            # a repair round confirming it.
            new_cap = max(0.0, allowed) * 0.999
            if new_cap < float(power_caps[i]) - 1e-9:
                power_caps[i] = new_cap
                changed = True
        if changed:
            _LOGGER.debug(
                "Buffer cap tightened %d step(s); re-solving",
                int(np.count_nonzero(refused > 1e-9)),
            )
        return changed

    def _repair_throttled_buffer_caps(
        self,
        weather: WeatherSeries,
        initial_state: ThermalState,
        result: OptimizationResult,
        power_caps: np.ndarray,
        dt: float,
        prices: np.ndarray,
        step_hours: np.ndarray,
        valve_targets: np.ndarray | None,
        solve: Callable[..., OptimizationResult],
    ) -> OptimizationResult:
        """Re-solve after lowering ceilings where the tank clamp refused heat."""
        p_max = self.model.params.max_electrical_power
        for _ in range(_SAFETY_REPAIR_ROUNDS):
            if not self._tighten_buffer_caps(
                weather, initial_state, result, power_caps, dt,
                valve_targets=valve_targets,
                start_hour=float(step_hours[0]),
            ):
                break
            extras = _cap_tighten_starts(
                np.asarray(result.power_schedule, dtype=float),
                power_caps,
                prices,
                dt,
                p_max,
            )
            # Extra seeds can only add basins now that every candidate is
            # refined (no refinement cut to displace them). Run both arms
            # anyway; seeds may only win.
            result = _better_objective(solve(), solve(extras))
        return result

    def _safety_release_steps(
        self,
        result: OptimizationResult,
        temp_min_bounds: np.ndarray,
        space_pins: np.ndarray | None,
        dhw_pins: np.ndarray | None,
    ) -> tuple[list[int], list[int]]:
        """Which forced-off steps must be released so safety is not breached.

        Reads the solved trajectories against the same hard lines the plan
        classifiers use — the comfort floor for space heating, and the DHW
        requirement (which already folds in the usable minimum, the idle floor
        and any due legionella cycle) for hot water.

        Every step is checked, not just the forced-off ones: an off-block's
        deficit surfaces *later*, at free steps — typically in the demand
        window just after the override expires — and checking only the pinned
        steps let exactly those breaches through with nothing releasing
        anything. A breach is attributed to the nearest preceding forced-off
        step, and the whole contiguous off-block it belongs to is released,
        because a tank or slab that is already cold needs the run-up freed,
        not just the final step. A breach with no forced-off step before it
        has nothing to release and is left to the ordinary penalties — that is
        genuine infeasibility, not the pins' doing.
        """

        def _preceding_off(pins: np.ndarray, i: int) -> int | None:
            j = i
            while j >= 0:
                pin = float(pins[j]) if j < len(pins) else float("nan")
                if not _pin_is_free(pin) and pin < 0.5:
                    return j
                j -= 1
            return None

        release_space: list[int] = []
        if space_pins is not None:
            two_zone = self.model.params.two_zone_enabled
            room = (
                result.upper_temp_trajectory
                if two_zone and result.upper_temp_trajectory
                else result.room_temp_trajectory
            )
            for i in range(len(result.power_schedule)):
                temp = room[i + 1] if i + 1 < len(room) else room[-1]
                floor = (
                    temp_min_bounds[i]
                    if i < len(temp_min_bounds)
                    else temp_min_bounds[-1]
                )
                pin = float(space_pins[i]) if i < len(space_pins) else float("nan")
                pinned_off = not _pin_is_free(pin) and pin < 0.5
                # At a forced-off step, sitting *at* the floor already means
                # the pin is what is holding the house there. At a free step
                # the solver legitimately rides the floor, so only a clear
                # violation beyond its tolerance counts.
                if pinned_off:
                    breach = temp <= floor + 0.15
                else:
                    breach = temp < floor - 0.25
                if not breach:
                    continue
                j = _preceding_off(space_pins, i)
                if j is not None:
                    release_space.append(j)

        release_dhw: list[int] = []
        if dhw_pins is not None and self._dhw_requirement is not None:
            traj = result.dhw_temp_trajectory
            req = self._dhw_requirement
            for i in range(min(len(result.dhw_power_schedule), len(req))):
                temp = traj[i + 1] if traj and i + 1 < len(traj) else 0.0
                if temp >= float(req[i]) - 0.5:
                    continue
                j = _preceding_off(dhw_pins, i)
                if j is not None:
                    release_dhw.append(j)

        return (
            self._expand_off_blocks(space_pins, release_space),
            self._expand_off_blocks(dhw_pins, release_dhw),
        )

    @staticmethod
    def _expand_off_blocks(
        pins: np.ndarray | None, breaches: list[int]
    ) -> list[int]:
        """Grow each breach back over its contiguous forced-off run."""
        if pins is None or not breaches:
            return []
        out: set[int] = set()
        for i in breaches:
            j = i
            while j >= 0 and not _pin_is_free(float(pins[j])) and float(pins[j]) < 0.5:
                out.add(j)
                j -= 1
        return sorted(out)

    def _pin_on_power(self, upper: float) -> float:
        """Lower bound for a forced-on step: the pump's minimum running power.

        Kept a touch above the classifier's idle threshold so a pinned-on step
        is unambiguously "running", but never above the capacity actually
        available, which the bounds helper clamps to.
        """
        floor = max(float(self.model.params.min_electrical_power), 0.1)
        return min(floor, upper)

    @staticmethod
    def _seed_pinned_guess(
        guess: np.ndarray, bounds: list[tuple[float, float]]
    ) -> np.ndarray:
        """Clamp a starting guess inside the (possibly pinned) bounds."""
        out = np.array(guess, dtype=float)
        for i in range(min(len(out), len(bounds))):
            low, high = bounds[i]
            out[i] = min(max(out[i], low), high)
        return out

    def _solve_objectives(self, h: _Horizon) -> tuple[
        Callable[..., Any],
        Callable[..., float],
        Callable[..., np.ndarray],
        Callable[..., Any],
    ]:
        """Both solve paths' trajectory, objective, batch twin and price (#1743).

        The DHW path passes its fixed plan as ``dhw_plan_power``; with
        ``None`` the arithmetic is the space-only path's, operand for operand.
        """
        initial_state, prices, dt, comfort_targets = (
            h.initial_state, h.prices, h.dt, h.comfort_targets
        )
        outdoor_temps, wind_speeds, precipitation, solar_radiation = (
            h.outdoor_temps, h.wind_speeds, h.precipitation, h.solar_radiation
        )
        weather = WeatherSeries.from_horizon(h)
        temp_min_bounds, temp_max_bounds = h.temp_min_bounds, h.temp_max_bounds

        # How far the user is willing to let the house drift below target. The
        # pull-to-target term is normalised by this, so widening the allowed
        # band actually buys cheaper operation instead of being overwhelmed by
        # a fixed quadratic penalty.
        comfort_band = np.maximum(comfort_targets - temp_min_bounds, 1.0)
        terminal_cost, terminal_cost_batch = self._terminal_cost(
            prices, outdoor_temps, h.solar_gains, h.humidity
        )
        cycling, capacity, _, cycling_batch, capacity_batch = (
            self._grid_terms(h.n_steps, dt, h.start_time)
        )
        energy_cost_of = self._energy_cost_fn(prices, dt)

        def _space_traj(power_schedule: np.ndarray) -> Any:
            return self.model.simulate_trajectory(
                initial_state=initial_state,
                power_schedule=power_schedule,
                weather=weather,
                dt_hours=dt,
                valve_targets=h.valve_targets,
                start_hour=float(h.step_hours[0]),
            )

        def objective(
            space_power: np.ndarray,
            dhw_plan_power: np.ndarray | None = None,
        ) -> float:
            """Compute the total cost with predictive weather anticipation."""
            room_temps, slab_temps, upper_temps, lower_temps, buffer_temps, _, _ = (
                _space_traj(space_power)
            )

            # The compressor is one machine: the grid sees the *combined*
            # draw, so the energy cost, the PV surplus it may consume, the
            # cycling term and the house peak are all properties of the sum,
            # not of space heating alone.
            combined = (
                space_power if dhw_plan_power is None
                else space_power + dhw_plan_power
            )

            # Electricity cost, piecewise in PV surplus. ``float()`` is
            # identity on the 1-D branch's return and states it.
            energy_cost = (
                float(energy_cost_of(combined)) * self.config.price_weight
            )

            penalty, comfort_cost = self._comfort_terms(
                room_temps, upper_temps, lower_temps,
                comfort_targets, temp_min_bounds, temp_max_bounds, comfort_band,
            )

            # --- Weather anticipation is the simulation's job ----------------
            # ``simulate_trajectory`` already applies the solar gain and the
            # wind/rain heat loss factors to the real physics, so the predicted
            # trajectory itself tells the optimizer that heating just before a
            # sunny spell is wasted and that coasting into a windy evening is
            # expensive. Two extra objective terms used to re-state the same
            # thing in invented currency: a penalty for heating before sun, and
            # a *negative* cost that paid the plan to burn electricity before
            # bad weather. Both double-counted, and the second existed only on
            # the space-only path and not on the DHW one, so simply enabling
            # hot water changed the space heating objective. Removing them made
            # the shoulder season 4-6% cheaper at identical comfort.

            return (
                energy_cost + penalty + comfort_cost
                # Currency terms scale with price_weight as the energy cost
                # does, or a non-default weight silently re-prices starts and
                # peaks relative to the electricity they trade against.
                + (cycling(combined) + capacity(combined))
                * self.config.price_weight
                + terminal_cost(
                    room_temps,
                    slab_temps,
                    upper_temps,
                    lower_temps,
                    buffer_temps,
                )
            )

        def objective_batch(
            space_matrix: np.ndarray,
            dhw_plan_power: np.ndarray | None = None,
        ) -> np.ndarray:
            """The same objective, for B schedules at once (issue #97).

            One batched simulation replaces B scalar ones, and the cost
            terms run as one reduction per term over the whole batch
            through ``_cost_terms_batch`` (#948) -- they used to run as B
            scalar calls each, which cost a third of the solve's wall
            (round 4, D9-05). Row for row bit-identical to ``objective``,
            asserted by test, because a divergence here would move plans
            silently.
            """
            traj = self.model.simulate_trajectory_batch(
                initial_state=initial_state,
                power_matrix=space_matrix,
                weather=weather,
                dt_hours=dt,
                valve_targets=h.valve_targets,
                start_hour=float(h.step_hours[0]),
            )
            # The grid sees the combined draw: space plus the fixed DHW plan.
            grid_power = (
                space_matrix if dhw_plan_power is None
                else space_matrix + dhw_plan_power
            )
            return self._cost_terms_batch(
                traj, grid_power,
                energy_cost_of=energy_cost_of,
                cycling_batch=cycling_batch,
                capacity_batch=capacity_batch,
                terminal_cost_batch=terminal_cost_batch,
                comfort_targets=comfort_targets,
                temp_min_bounds=temp_min_bounds,
                temp_max_bounds=temp_max_bounds,
                comfort_band=comfort_band,
            )

        return _space_traj, objective, objective_batch, energy_cost_of

    def _optimize_space_only(self, h: _Horizon) -> OptimizationResult:
        """Optimize space heating only (no DHW)."""
        import time

        # Unpacked rather than accessed through ``h`` throughout: the body is
        # dense numpy, and ``h.prices * h.dt`` forty times over reads far worse
        # than the equations it is meant to express.
        initial_state, prices, dt, n_steps = (
            h.initial_state, h.prices, h.dt, h.n_steps
        )
        outdoor_temps, wind_speeds = h.outdoor_temps, h.wind_speeds
        precipitation, solar_radiation = h.precipitation, h.solar_radiation
        weather = WeatherSeries.from_horizon(h)
        comfort_targets = h.comfort_targets
        solar_gains_per_step = h.solar_gains
        forecast_heat_loss_factors = h.heat_loss_factors
        forecast_analysis, t_start = h.forecast, h.t_start

        p_min = self.model.params.min_electrical_power
        p_max = self.model.params.max_electrical_power

        anticipatory_weights = self._anticipatory_weights(
            n_steps, dt, solar_gains_per_step, forecast_heat_loss_factors
        )
        _space_traj, objective, objective_batch, energy_cost_of = (
            self._solve_objectives(h)
        )

        # Initial guess: smart initialization considering forecasts
        initial_power = p_max * _price_guess_weights(prices)

        # Apply predictive adjustments to initial guess
        for i in range(n_steps):
            # Reduce power before solar periods
            initial_power[i] *= anticipatory_weights[i]

        initial_power = np.clip(initial_power, p_min, p_max)
        # A heat pump can be off. min_electrical_power is the lowest it can
        # modulate to while running, not a floor it must burn every step, so
        # allow 0 and read sub-minimum values as duty cycling within the step.
        if h.power_caps is not None:
            bounds = [
                (0.0, float(min(p_max, h.power_caps[i]))) for i in range(n_steps)
            ]
        else:
            bounds = [(0.0, p_max)] * n_steps
        # A manual plan pins individual steps on or off. Forcing on raises the
        # lower bound to the pump's minimum running power so the step must run
        # without fixing how hard; the initial guess is nudged into the pinned
        # band so the solver starts feasible.
        bounds = _apply_pins_to_bounds(bounds, h.space_pins, self._pin_on_power(p_max))
        initial_power = self._seed_pinned_guess(initial_power, bounds)

        # Multiple starting points: the smooth price-weighted guess above, a
        # bang-bang schedule that buys the cheapest steps first, a flat
        # schedule, and the low-energy bang-bang seeds (R1-D0-01 and R7-D0-01
        # -- see the two fractions' comments for why the same-energy
        # candidates all refine into one basin on arbitrage prices, and why
        # 0.35x alone does not bracket the optimum's energy). See
        # _multi_start_minimize for why one guess is not enough.
        # Computed once and reused below for the savings reference; the same
        # simulation also makes a good solver start.
        baseline_power, baseline_end = self._compute_baseline_power(
            weather, initial_state, dt, comfort_targets,
        )
        baseline_energy = float(np.sum(baseline_power) * dt)
        starts = [
            initial_power,
            _price_ranked_start(prices, baseline_energy, p_max, dt),
            np.clip(baseline_power, 0.0, p_max),
            _price_ranked_start(
                prices,
                baseline_energy * _LOW_ENERGY_START_FRACTION,
                p_max,
                dt,
            ),
        ]
        if self.model.params.two_zone_enabled:
            # The deep low-energy anchor, two-zone only -- see its own
            # comment for why the reach is deliberately this narrow.
            starts.append(
                _price_ranked_start(
                    prices,
                    baseline_energy * _DEEP_LOW_ENERGY_START_FRACTION,
                    p_max,
                    dt,
                )
            )
        def move_starts(
            cands: list[np.ndarray], maxiter: int
        ) -> list[np.ndarray]:
            """Continuation for a two-zone solve's first start (R9-F2.1).

            Each zone pays the full linear floor price, and a descent that
            crosses the floor from the smooth guess can bend away from a
            basin the half price reaches: the backtest's 750 L storage house
            shipped a plan its own objective scores 0.83 worse. So the guess
            is refined at the half price first; what ships is still decided
            by the true objective, against every other start. One plain
            L-BFGS-B run inside the multi-start's own budget: it moves a
            start, it is not one.
            """
            if not self.model.params.two_zone_enabled:
                return cands
            first = len(h.extra_starts or ())
            self._floor_l1_scale = 0.5
            try:
                cands[first] = np.asarray(_scoped_minimize(
                    objective, cands[first], method="L-BFGS-B", bounds=bounds,
                    jac=(lambda x: _batch_fd_gradient(
                        objective_batch, (), x, float(objective(x)), 1e-4,
                        bounds,
                    )) if _bounds_supported_by_batch(bounds) else None,
                    options={"maxiter": maxiter, "ftol": 1e-6, "eps": 1e-4},
                ).x, dtype=float)
            finally:
                self._floor_l1_scale = 1.0
            return cands

        if h.extra_starts:
            starts = list(h.extra_starts) + starts

        try:
            result = _multi_start_minimize(
                objective, starts, bounds, maxiter=200,
                batch_objective=objective_batch, move_starts=move_starts,
            )
            optimal_power = result.x
            status = _solver_status(result, objective, initial_power)
        except Exception as e:
            _LOGGER.error("Optimization failed: %s", e)
            optimal_power = initial_power
            status = f"failed ({e})"

        # Simulate with optimal schedule
        (
            room_temps,
            slab_temps,
            upper_temps,
            lower_temps,
            buffer_temps,
            _,
            wood_temps,
        ) = _space_traj(optimal_power)
        # The achieved objective, for candidate comparison across valve
        # schedules. One extra evaluation, robust on the failure path too.
        achieved_objective = float(objective(optimal_power))

        baseline_cost = float(energy_cost_of(baseline_power))
        predicted_cost = float(energy_cost_of(optimal_power))

        optimized_end = self._replay_end_state(
            initial_state, optimal_power, outdoor_temps, wind_speeds,
            precipitation, solar_radiation, dt,
            external_heat_kw=h.external_heat_kw,
            valve_targets=h.valve_targets, humidity=h.humidity,
        )
        deferred_cost = self._deferred_energy_cost(
            baseline_end, optimized_end, prices, outdoor_temps,
            caps=self._settlement_caps(outdoor_temps, humidity=h.humidity),
            humidity=h.humidity,
        )
        savings = baseline_cost - predicted_cost - deferred_cost

        t_elapsed = (time.monotonic() - t_start) * 1000
        _LOGGER.info(
            "Optimization completed in %.0fms: cost=%.2f, baseline=%.2f, "
            "savings=%.1f%%, solar_reduction=%.2f, wind_factor=%.2f",
            t_elapsed, predicted_cost, baseline_cost,
            _savings_percentage(savings, baseline_cost),
            forecast_analysis["solar_reduction_factor"],
            forecast_analysis["wind_anticipation_factor"],
        )

        return self._build_result(
            h,
            space_power=optimal_power,
            trajectories=(room_temps, slab_temps, upper_temps, lower_temps),
            buffer_temps=buffer_temps,
            wood_temps=wood_temps,
            objective_value=achieved_objective,
            status=status,
            predicted_cost=predicted_cost,
            baseline_cost=baseline_cost,
            savings=savings,
            deferred_cost=deferred_cost,
            baseline_power=baseline_power,
        )

    # ------------------------------------------------------------------
    # Reporting helpers shared by both solve paths
    # ------------------------------------------------------------------

    def _grid_report(
        self,
        total_power: np.ndarray,
        baseline_load: np.ndarray,
        dt: float,
        start_time: datetime | None = None,
    ) -> dict[str, Any]:
        """Peak and cycling figures for the solved plan."""
        cfg = self.config
        offset_steps = self._window_offset_steps(start_time, dt)
        n = len(np.asarray(total_power))
        factors = self._peak_window_factors(n, dt, start_time, offset_steps)
        if factors is None:
            peak_kw = realised_peak(
                total_power,
                baseline_load,
                cfg.peak_window_minutes,
                dt,
                offset_steps,
            )
        else:
            # Billed-equivalent projection when the #13 masks are active:
            # this figure is published beside the billed-equivalent threshold
            # and the peak cost, and a physical 8 kW above a half-rate 4 kW
            # threshold with zero cost read as three mutually contradictory
            # numbers. Unmasked, this is the physical window max, as always.
            house = np.asarray(total_power, dtype=float) + np.asarray(
                baseline_load, dtype=float
            )
            windows = metering_windows(
                house, cfg.peak_window_minutes, dt, offset_steps
            )
            f = factors[: windows.size]
            if f.size < windows.size:
                f = np.concatenate([f, np.ones(windows.size - f.size)])
            peak_kw = float(np.max(windows * f)) if windows.size else 0.0
        return {
            "peak_kw": round(peak_kw, 3),
            "peak_cost": round(
                peak_cost(
                    total_power,
                    baseline_load,
                    cfg.peak_threshold_kw,
                    cfg.peak_price_per_kw,
                    cfg.peak_window_minutes,
                    dt,
                    cfg.peak_count,
                    offset_steps,
                    window_factors=self._peak_window_factors(
                        len(np.asarray(total_power)), dt, start_time,
                        offset_steps,
                    ),
                    **self._peak_day_kwargs(n, dt, start_time, offset_steps),
                ),
                3,
            ),
            "starts": count_compressor_starts(total_power),
        }

    def _price_known_list(self, n_steps: int) -> list[bool]:
        if self._price_known is None:
            return [True] * n_steps
        return [bool(v) for v in self._price_known[:n_steps]]

    def _pv_surplus_list(self, n_steps: int) -> list[float]:
        if self._pv_surplus is None:
            return []
        if not np.any(self._pv_surplus > 1e-6):
            return []
        return [round(float(v), 3) for v in self._pv_surplus[:n_steps]]

    def _pv_self_consumed(self, power: np.ndarray, dt: float) -> float:
        """Heat pump energy that lands inside forecast surplus, kWh."""
        if self._pv_surplus is None or not np.any(self._pv_surplus > 1e-6):
            return 0.0
        n = min(len(power), len(self._pv_surplus))
        served = np.minimum(
            np.asarray(power[:n], dtype=float), self._pv_surplus[:n]
        )
        return round(float(np.sum(served) * dt), 3)

    def _optimize_with_dhw(
        self, h: _Horizon, planner: DhwPlanner
    ) -> OptimizationResult:
        """Optimize coordinated space heating + DHW heating.

        Decision variables: [P_space[0..n-1], P_dhw[0..n-1]]
        The heat pump can allocate power to space OR DHW, with total
        constrained by max capacity.
        """
        import time
        # See ``_optimize_space_only`` for why the context is unpacked.
        initial_state, prices, dt, n_steps = (
            h.initial_state, h.prices, h.dt, h.n_steps
        )
        outdoor_temps, wind_speeds = h.outdoor_temps, h.wind_speeds
        precipitation, solar_radiation = h.precipitation, h.solar_radiation
        weather = WeatherSeries.from_horizon(h)
        comfort_targets = h.comfort_targets
        step_hours, solar_gains_per_step = h.step_hours, h.solar_gains
        forecast_heat_loss_factors = h.heat_loss_factors
        start_time, t_start = h.start_time, h.t_start

        p_min = self.model.params.min_electrical_power
        p_max = self.model.params.max_electrical_power
        dhw_min_temp = self.model.params.dhw_min_temp
        dhw_setpoint = self.model.params.dhw_setpoint

        start_hour = start_time.hour + start_time.minute / 60.0

        anticipatory_weights = self._anticipatory_weights(
            n_steps, dt, solar_gains_per_step, forecast_heat_loss_factors
        )

        # ----------------------------------------------------------------
        # DHW demand model
        # ----------------------------------------------------------------
        # The DHW requirement is expressed as a per-step temperature floor
        # rather than a target trajectory. Inside a configured demand window
        # hot water must be available; outside it there is no requirement, so
        # the only reason to run the pump is to be ready for the *next* window
        # — and the energy-cost term then decides *when* that happens.
        dhw_plan, self._dhw_requirement = planner._build_dhw_requirements(
            h,
            p_max=p_max,
            # The DHW block honours an external ceiling through this scalar,
            # the horizon's minimum — the same conservative, never-over-the-
            # line approximation the fuse guard's cap already makes here. A
            # quiet silent window's cap therefore bounds every DHW block the
            # same way (#1910); its OFF steps are per-step, below, through
            # the forced-off door where the energy is re-bought elsewhere.
            p_run_cap=(
                float(np.min(h.power_caps_extra))
                if h.power_caps_extra is not None
                else None
            ),
            blocked=h.dhw_blocked,
            off_steps=h.off_steps,
            wood_temps=planner._dhw_coil_wood_forecast(h),
        )

        dhw_floor_temps = dhw_plan.floor_temps
        dhw_ready_temps = dhw_plan.ready_temps
        dhw_draw_rates = dhw_plan.draw_rates
        in_demand_window = dhw_plan.in_window
        optimal_dhw = dhw_plan.schedule

        # Kept for reporting/back-compat: which hours the learned profile still
        # considers high-usage (restricted to the configured windows).
        usage_intensity = np.array([
            self.model.dhw_usage_intensity(h) for h in step_hours
        ])
        high_usage_mask = in_demand_window & (
            usage_intensity >= max(1.0, float(np.percentile(usage_intensity, 70)))
        )

        # DHW is a deferrable, effectively on/off load, so it is scheduled by
        # the min-cost planner above rather than by the gradient solver (which
        # would smear it into an unrealizable trickle). Space heating is then
        # optimized *around* the fixed DHW blocks: the pump's remaining
        # capacity during a DHW block is what bounds space heating power.
        #
        # That decomposition is only exact when the two loads do not compete
        # for the compressor. They do: both want the cheapest hours. So the
        # split is iterated below, re-planning DHW against the space-heating
        # profile it actually has to share the pump with.

        # ``_solve_objectives`` builds the objective both paths share.
        _, objective, objective_batch, energy_cost_of = (
            self._solve_objectives(h)
        )

        # Initial guess: space heating inversely proportional to price.
        init_base = p_max * 0.6 * _price_guess_weights(prices)
        for i in range(n_steps):
            init_base[i] *= anticipatory_weights[i]
        init_base = np.clip(init_base, p_min * 0.5, p_max * 0.8)

        def solve_space(
            dhw_plan: np.ndarray, warm_start: np.ndarray | None
        ) -> tuple[np.ndarray, str, float]:
            return self._solve_space(
                dhw_plan,
                warm_start,
                h,
                p_max,
                n_steps,
                dt,
                prices,
                init_base,
                objective,
                objective_batch,
            )

        # The seam between the DHW LP stage above and the gradient space
        # stage below. Timing only: yield the GIL for a moment so the event
        # loop schedules pending work before the heaviest part of the solve
        # begins (see _multi_start_minimize). No effect on any result.
        time.sleep(0.002)

        optimal_space, status, best_score = solve_space(optimal_dhw, None)
        optimal_space, optimal_dhw, status = self._co_optimize(
            h,
            space_power=optimal_space,
            dhw_power=optimal_dhw,
            status=status,
            best_score=best_score,
            solve_space=solve_space,
            p_max=p_max,
            planner=planner,
        )

        # Simulate with optimal schedule
        published_end: list[ThermalState] = []
        (
            room_temps,
            slab_temps,
            upper_temps,
            lower_temps,
            dhw_temps,
            buffer_temps,
            wood_temps,
        ) = self.model.simulate_trajectory_with_dhw(
            initial_state=initial_state,
            space_power_schedule=optimal_space,
            dhw_power_schedule=optimal_dhw,
            weather=WeatherSeries.from_horizon(h),
            start_hour=start_hour,
            dt_hours=dt,
            dhw_draw_rates=dhw_draw_rates,
            valve_targets=h.valve_targets,
            end_state=published_end,
        )
        # The achieved objective, for candidate comparison across valve
        # schedules.
        achieved_objective = float(objective(optimal_space, optimal_dhw))

        # Baseline cost; its house owns the plan's refill coil and draws.
        baseline_power, baseline_end = self._compute_baseline_power(
            weather, initial_state, dt, comfort_targets,
            coil_draws=dhw_draw_rates, coil_dhw_temp=dhw_setpoint,
        )
        baseline_dhw, baseline_cost, predicted_cost, dhw_cost = (
            planner._baseline_dhw_economics(
                initial_state, outdoor_temps, n_steps, dhw_setpoint,
                energy_cost_of, baseline_power, optimal_space, optimal_dhw, h.humidity,
            )
        )

        # Settle up the heat the optimized plan left unstored at the horizon end.
        # The baseline reference ends with a tank at setpoint, so compare against
        # that rather than against the optimized tank's own starting point.
        # The plan's end is its published trajectory's last state; a space-only
        # replay skipped the coil's wood debit (R9 D2-s2-03).
        baseline_end.dhw_temperature = dhw_setpoint
        optimized_end = published_end[0]
        # The tank only has to satisfy the requirement in force at the end of
        # the horizon. Outside a demand window that is the idle minimum, so a
        # cold tank at midnight is not treated as borrowed heat.
        deferred_cost = self._deferred_energy_cost(
            baseline_end, optimized_end, prices, outdoor_temps, include_dhw=True,
            caps=self._settlement_caps(
                outdoor_temps, dhw_cap=float(dhw_floor_temps[-1]), humidity=h.humidity
            ),
            humidity=h.humidity,
        )
        savings = baseline_cost - predicted_cost - deferred_cost

        t_elapsed = (time.monotonic() - t_start) * 1000

        dhw_active_steps = int(np.sum(optimal_dhw > 0.1))
        _LOGGER.info(
            "DHW+Space optimization completed in %.0fms: cost=%.2f (DHW=%.2f in "
            "%d steps), baseline=%.2f, savings=%.1f%%, windows=%s",
            t_elapsed, predicted_cost, dhw_cost, dhw_active_steps, baseline_cost,
            _savings_percentage(savings, baseline_cost),
            dhw_plan.windows_text or "always",
        )

        result = self._build_result(
            h,
            space_power=optimal_space,
            trajectories=(room_temps, slab_temps, upper_temps, lower_temps),
            buffer_temps=buffer_temps,
            wood_temps=wood_temps,
            objective_value=achieved_objective,
            status=status,
            predicted_cost=predicted_cost,
            baseline_cost=baseline_cost,
            savings=savings,
            deferred_cost=deferred_cost,
            baseline_power=baseline_power + baseline_dhw,
            dhw_power=optimal_dhw,
            dhw_temps=dhw_temps,
            dhw_cost=dhw_cost,
            dhw_in_window=in_demand_window,
            dhw_ready=dhw_ready_temps,
            dhw_legionella_step=dhw_plan.legionella_step,
            dhw_floors=dhw_floor_temps,
            predictive_info={
                "dhw_peak_usage_hours": [
                    int(step_hours[idx]) % 24
                    for idx in np.where(high_usage_mask)[0][:24].tolist()
                ],
                "dhw_preheat_lead_hours": round(dhw_plan.max_lead_hours, 2),
                "dhw_min_temperature": float(dhw_min_temp),
                "dhw_target_temperature": float(dhw_setpoint),
                "dhw_usage_intensity_now": float(usage_intensity[0]) if len(usage_intensity) else 1.0,
                "dhw_windows": dhw_plan.windows_text,
                **_dhw_resolved_publish(self.model.params),
                "dhw_in_demand_window": bool(in_demand_window[0]) if n_steps else False,
                "dhw_next_window_in_hours": dhw_plan.next_window_in_hours,
                "dhw_required_temperature_now": (
                    float(max(dhw_floor_temps[0], dhw_ready_temps[0]))
                    if n_steps
                    else float(dhw_min_temp)
                ),
                "dhw_idle_min_temperature": float(
                    self.model.params.dhw_idle_min_temp
                ),
                "dhw_legionella_due": dhw_plan.legionella_due,
                "dhw_legionella_step_hour": dhw_plan.legionella_hour,
                "dhw_planned_heating_hours": [
                    round(float(step_hours[idx]), 2)
                    for idx in np.where(optimal_dhw > 0.1)[0][:48].tolist()
                ],
                # Hours of planned heating that happen ahead of a demand
                # window rather than inside it — the visible sign that the
                # tank is being charged when electricity is cheap.
                "dhw_preheat_hours": round(
                    float(np.sum((optimal_dhw > 0.1) & ~in_demand_window) * dt), 2
                ),
                "dhw_cooling_rate": round(
                    float(self.model.params.dhw_cooling_rate), 3
                ),
                "dhw_hold_hours": round(float(self.model.dhw_hold_hours()), 1),
            },
        )
        return result

    def _settlement_caps(
        self, outdoor_temps: np.ndarray, dhw_cap: float | None = None,
        humidity: np.ndarray | None = None,
    ) -> dict[str, float]:
        """Temperatures above which stored heat is worth nothing.

        Heat carried past the horizon is only an asset up to the point where it
        is actually needed. A house sitting at 25 °C in July because the sun
        heated it is not holding 4 °C of useful charge, and settling that up
        would charge the optimizer for failing to be as overheated as the
        reference. Cap every store at what the comfort target and the hot water
        requirement genuinely call for.
        """
        p = self.model.params
        target = self.config.target_temp
        out_mean = float(np.mean(outdoor_temps))
        slab_cap = slab_settlement_cap(p, target, out_mean)
        caps = {"room": target, "slab": slab_cap}
        # The buffer tank needs its own ceiling, and it is much higher than the
        # slab's.
        #
        # The cap exists to stop *passive* overheating being counted as charge:
        # a house at 25 C in July is not holding useful heat. That reasoning does
        # not transfer to a tank. A tank only gets hot because the pump
        # deliberately heated it, and the valve stops it overheating anything, so
        # every degree in it is heat that will genuinely be used.
        #
        # Sharing the slab's cap made the tank invisible as a store: with a slab
        # ceiling near 28 C, charging a tank from 45 C to 70 C was credited with
        # 0.0 kWh of the 21.8 kWh actually stored. Charging was pure cost with no
        # modelled benefit, which is why every starting point descended to the
        # same no-storage plan.
        if p.buffer_is_store:
            # Valued up to the ceiling the plan can actually charge to, not
            # the raw safety rating. The rating is where the simulation's
            # clamp and the cap-refusal loop stop the tank — but reaching it
            # requires the pump to out-run the house's standing draw and the
            # tank's own loss at an ever-worsening flow-derated COP, and in
            # cold weather a real pump cannot. Settling the full distance to
            # 70 °C charged every plan for failing to hold a temperature no
            # plan could reach, an asymmetry the room cap (the target, not
            # the comfort ceiling) never had.
            ceiling = self._buffer_charge_ceiling(out_mean, _mean_humidity(humidity))
            # Heat ALREADY in the tank above the charging ceiling is real:
            # it was paid for, and draining it displaces bought electricity
            # at the derated COP. Capping the value at the ceiling alone let
            # a plan drain a pre-charged tank (a mild evening's 60 °C before
            # a cold snap) to the ceiling with zero settlement — re-creating
            # the tail-dumping this term exists to prevent, in exactly the
            # regime storage matters most (v4.0.5 review). The floor at the
            # solve's initial temperature keeps the deficit direction
            # honest too: no plan can charge past the ceiling, so the
            # unavoidable decay from a hot start prices every candidate
            # identically and only the drained difference separates them.
            initial = self._initial_buffer_temp
            if initial is not None:
                ceiling = min(
                    float(p.buffer_max_temp), max(ceiling, float(initial))
                )
            caps["buffer"] = ceiling
        else:
            # Without a valve the tank cannot be charged at all, and below the
            # store threshold (item 27) it holds too little to matter, so its
            # cap cannot change any decision. Left alone so these paths stay
            # byte-for-byte identical.
            caps["buffer"] = slab_cap
        if p.two_tank_modelled:
            # The wood tank is a genuine store too (issue #40): a burn's heat
            # still in it at the horizon end displaces bought heat exactly as
            # the buffer's does. Report-only and symmetric, like every
            # settlement figure -- the objective's terminal cost deliberately
            # excludes it (nobody refills it with electricity, so crediting
            # it there would create a hoarding incentive with no refill cost).
            caps["wood"] = WOOD_TANK_MAX_TEMP
        if dhw_cap is not None:
            caps["dhw"] = dhw_cap
        return caps

    def _buffer_charge_ceiling(
        self, out_mean: float, humidity: float | None = None
    ) -> float:
        """The tank temperature the pump can still charge past, °C.

        The bound the solve actually operates under. The simulation's clamp
        sits at ``buffer_max_temp``, but the tank only rises while the pump's
        thermal output at the tank's own flow temperature exceeds the house's
        standing draw plus the tank's standby loss — and the flow-derated COP
        falls as the tank warms, so in cold weather that balance closes below
        the rating and no schedule can push further. Bisection on the net
        charge rate, which is monotone decreasing in tank temperature; the
        answer is the rating whenever the pump still out-runs the drains
        there (every mild-weather case, where this changes nothing).
        """
        p = self.model.params
        hi = float(p.buffer_max_temp)
        # Below the flow reference no derate applies and the tank is just the
        # hydronic loop; heat down there is always chargeable.
        lo = max(20.0, float(p.cop_flow_reference_temp))
        if hi <= lo:
            return hi
        target = self.config.target_temp
        if p.two_zone_enabled:
            u_house = p.upper_floor_heat_loss + p.lower_floor_heat_loss_learned
        else:
            u_house = p.heat_loss_coefficient
        # The learned leakage scale rides along: the dynamics and the battery
        # view both apply it, and a learned-leaky house that omitted it here
        # got an optimistic ceiling — the one direction this bound must not
        # err (v4.0.5 review).
        u_house *= p.house_heat_loss_scale
        # What the valve keeps feeding the house while the tank charges: the
        # standing demand at the comfort target, the same steady-state frame
        # as the settlement caps themselves.
        q_house = max(0.0, u_house * (target - out_mean) - p.internal_gains)
        ua_tank = p.buffer_tank_heat_loss_coefficient
        p_max = p.max_electrical_power

        def net(temp: float) -> float:
            cop = self.model.marginal_cop(
                out_mean, "buffer", store_temp=temp, humidity=humidity
            )
            return p_max * cop - q_house - ua_tank * max(0.0, temp - TANK_ROOM_AMBIENT_TEMP)

        if net(hi) > 0.0:
            return hi
        if net(lo) <= 0.0:
            return lo
        for _ in range(32):
            mid = 0.5 * (lo + hi)
            if net(mid) > 0.0:
                lo = mid
            else:
                hi = mid
        return lo

    def _deferred_energy_cost(
        self,
        baseline_end: ThermalState,
        optimized_end: ThermalState,
        prices: np.ndarray,
        outdoor_temps: np.ndarray,
        include_dhw: bool = False,
        caps: dict[str, float] | None = None,
        humidity: np.ndarray | None = None,
    ) -> float:
        """Cost of restoring the heat the optimized plan left unstored.

        Nothing beyond the horizon is penalised, so the optimizer will happily
        coast the house (and tank) down as the window closes. That heat is
        borrowed, not saved, and counting it as a saving is what makes the
        savings figure drift upwards. Value the difference at the price the
        heat would actually be bought back at, which is the cheapest part of the
        upcoming window rather than the average.

        Symmetric: a surplus is credited exactly as a deficit is charged. It
        used to be one-sided, on the reasoning that the reference is a
        thermostat rather than a competing plan -- but that argument forbids
        charging just as much as it forbids crediting, and what it produced was
        a savings figure that understated itself precisely when the plan chose
        to end the window warm. Measured across ten scenarios, three ended with
        more useful heat than the thermostat baseline and were given nothing for
        it: shoulder by 2.29 SEK on a reported 27.64 (8 %), flat prices by 3.52
        on 14.85 (24 %), and flat prices with no mixing valve at all by 6.06 on
        9.84 -- a 62 % understatement, and nothing to do with storage. It is the
        building's own mass ending warmer than a thermostat would have left it.

        What makes the credit safe is ``caps``: every store is already limited
        to the temperature above which its heat is of no further use, so this
        cannot pay out for a house that merely overheated in the sun.

        Note this figure is reported, not optimised -- it reaches
        ``predicted_savings`` and the sensors, and never the objective, which
        prices its own end state through ``_terminal_cost``. Changing it makes
        the number honest; it does not change a single plan.
        """
        stored_gap = self._stored_thermal_energy(
            baseline_end, include_dhw, caps
        ) - self._stored_thermal_energy(optimized_end, include_dhw, caps)

        out_mean = float(np.mean(outdoor_temps))
        hum_mean = _mean_humidity(humidity)
        cop = max(self.model.compute_cop(out_mean, humidity=hum_mean), 1e-3)
        # Heat is topped up when it is cheap, so settle at a low percentile
        # rather than the mean; using the mean would over-charge the optimizer
        # for heat it would obviously buy back in a cheap hour. The same
        # percentile prices a credit, where it errs the other way and is the
        # conservative choice: heat already in store displaces whatever the next
        # window would have paid, which is the average and not the cheap tail.
        refill_price = float(np.percentile(prices, 25))
        electrical = stored_gap / cop

        # v4.0.5: the tank shares of the gap re-price at their own marginal
        # COP — the buffer refills at the flow-derated COP of its settlement
        # temperature, the DHW tank at `compute_cop_dhw` — because that is
        # what the simulation would actually charge to put the heat back.
        # Pricing them at the plain space curve made a cold tank cheap to
        # refill and a warm one rich to credit, so the reported savings
        # overstated themselves exactly when the plan ended with a cold tank.
        # Written as corrections on the plain-COP total rather than a clean
        # per-store split so every store still priced at the plain curve —
        # and every configuration where the tank COPs collapse to it —
        # keeps the historical arithmetic bit for bit.
        p = self.model.params
        caps = caps or {}

        def _capped(value: float, cap_key: str) -> float:
            cap = caps.get(cap_key)
            return min(value, cap) if cap is not None else value

        if p.two_zone_enabled:
            cop_buffer = max(
                self.model.marginal_cop(
                    out_mean, "buffer", store_temp=caps.get("buffer"),
                    humidity=hum_mean,
                ),
                1e-3,
            )
            if cop_buffer != cop:
                buffer_gap = p.buffer_tank_thermal_mass * (
                    _capped(baseline_end.buffer_tank_temperature, "buffer")
                    - _capped(optimized_end.buffer_tank_temperature, "buffer")
                )
                electrical += buffer_gap / cop_buffer - buffer_gap / cop
        if include_dhw:
            dhw_cap = caps.get("dhw")
            cop_dhw = max(
                self.model.marginal_cop(
                    out_mean,
                    "dhw",
                    store_temp=(
                        dhw_cap if dhw_cap is not None else p.dhw_setpoint
                    ),
                    humidity=hum_mean,
                ),
                1e-3,
            )
            if cop_dhw != cop:
                dhw_gap = p.dhw_tank_thermal_mass * (
                    _capped(baseline_end.dhw_temperature, "dhw")
                    - _capped(optimized_end.dhw_temperature, "dhw")
                )
                electrical += dhw_gap / cop_dhw - dhw_gap / cop
        return float(electrical * refill_price)

    def _compute_baseline_power(
        self,
        weather: WeatherSeries,
        initial_state: ThermalState,
        dt: float,
        comfort_targets: np.ndarray | None = None,
        coil_draws: np.ndarray | None = None,
        coil_dhw_temp: float = 0.0,
    ) -> tuple[np.ndarray, ThermalState]:
        """Simulate a conventional thermostat following the comfort schedule.

        This is the reference the reported savings are measured against, so it
        has to behave like a real thermostat in the same physics as the
        optimized schedule. Anything it wastes is reported to the user as a
        saving, so the controller is built from the model's own steady state
        rather than from a heuristic.

        The thermostat tracks the same per-step comfort targets the plan is
        held to. Holding the flat ``target_temp`` around the clock instead
        made the reference heat to the *day* temperature all night, and a
        configured night setback was then booked as optimizer savings — value
        any ordinary programmable thermostat delivers.

        Heat is delivered to the slab and only reaches the room on the
        following step, so power is set by a cascade: the slab is driven to the
        temperature that sustains the setpoint, with a proportional term that
        pulls the room back if it has drifted.

        Returns the power schedule and the final state, the latter so the
        caller can account for the thermal energy left stored at the end of the
        horizon. ``coil_draws`` (the hot-water path's raw draws) runs the
        wood-tank refill coil on that state each step, from a tank at
        ``coil_dhw_temp``, as the plan's own trajectory does.
        """
        outdoor_temps = weather.outdoor_temps
        wind_speeds = weather.wind_speeds
        precipitation = weather.precipitation
        solar_radiation = weather.solar_radiation
        external_heat_kw = weather.external_heat_kw
        humidity = weather.humidity
        # The thermostat runs the same heat-loss physics as the plan, so its
        # weather is the horizon's: the series the loss multiplies are
        # required here, never the record's None default. Both callers hand
        # it a horizon's series (tests build them concrete).
        assert wind_speeds is not None and precipitation is not None
        assert solar_radiation is not None
        n_steps = len(outdoor_temps)
        p = self.model.params
        if not p.dhw_coil_active:
            coil_draws = None

        baseline_power = np.zeros(n_steps)
        state = initial_state

        for i in range(n_steps):
            target = (
                float(comfort_targets[i])
                if comfort_targets is not None and i < len(comfort_targets)
                else self.config.target_temp
            )
            if p.two_zone_enabled:
                required_thermal = self._baseline_thermal_demand_two_zone(
                    state, target, outdoor_temps[i], wind_speeds[i],
                    precipitation[i], solar_radiation[i], dt,
                )
            else:
                required_thermal = self._baseline_thermal_demand_single(
                    state, target, outdoor_temps[i], wind_speeds[i],
                    precipitation[i], solar_radiation[i], dt,
                )

            # A thermostat's house receives a furnace burn too, and its
            # sensor sees the warmth: the reference backs off by the free
            # heat, or the burn would be booked as optimizer savings.
            ext_i = (
                float(external_heat_kw[i])
                if external_heat_kw is not None and i < len(external_heat_kw)
                else 0.0
            )
            if (
                p.two_tank_modelled
                and state.wood_tank_temperature is not None
            ):
                # With the wood tank modelled, the 4-way valve covers part
                # of the draw from the wood side; the reference backs its
                # electric demand off by that share, computed with the SAME
                # wood_share law the plan's physics uses so the two cannot
                # drift. Subtracting ext_i afterwards as well is deliberate
                # double counting in the conservative direction: the
                # baseline can only get cheaper, so reported savings are
                # understated, never inflated.
                u_up = self.model.effective_heat_loss_coefficient(
                    p.upper_floor_heat_loss, wind_speeds[i], precipitation[i]
                )
                u_lo = self.model.effective_heat_loss_coefficient(
                    p.lower_floor_heat_loss_learned,
                    wind_speeds[i] * 0.5, precipitation[i] * 0.5,
                )
                design_power = p.max_electrical_power * p.cop_nominal_floored
                flow_set = mixing_valve.flow_setpoint(
                    target_temp=p.mixing_valve_target or p.comfort_ceiling,
                    outdoor_temp=float(outdoor_temps[i]),
                    heat_loss_coefficient=u_up + u_lo,
                    emitter_ua=design_power / p.emitter_design_delta_t_floored,
                )
                w_i = wood_share(
                    state.wood_tank_temperature,
                    state.buffer_tank_temperature,
                    flow_set,
                    min(
                        state.upper_floor_temperature, state.slab_temperature
                    ),
                )
                required_thermal *= 1.0 - w_i
            required_thermal = max(0.0, required_thermal - ext_i)

            hum_i = _step_humidity(humidity, i)
            cop = self.model.compute_cop(outdoor_temps[i], humidity=hum_i)
            # No lower clamp to ``min_electrical_power``: a pump that cannot
            # modulate that low cycles on and off, and over a step the average
            # power is what determines energy use. Forcing the baseline up to
            # the minimum modulation power made it burn a constant
            # min_electrical_power * 24 h per day even when the house needed no heat at
            # all, which inflated both the baseline and the savings.
            power = float(
                np.clip(required_thermal / cop, 0.0, p.max_electrical_power)
            )
            baseline_power[i] = power

            state = self.model.simulate_step(
                state, power, outdoor_temps[i],
                wind_speeds[i], precipitation[i], solar_radiation[i], dt,
                external_heat_kw=ext_i, humidity=hum_i,
            )
            if coil_draws is not None:
                self.model.apply_dhw_coil(
                    state, float(coil_draws[i]), coil_dhw_temp, dt
                )

        return baseline_power, state

    def _baseline_thermal_demand_single(
        self,
        state: ThermalState,
        target: float,
        outdoor_temp: float,
        wind_speed: float,
        precipitation: float,
        solar_radiation: float,
        dt: float,
    ) -> float:
        """Thermal power a thermostat needs this step in the single-zone model."""
        p = self.model.params
        k_slab = p.slab_heat_transfer_floored

        u_eff = self.model.effective_heat_loss_coefficient(
            p.heat_loss_coefficient, wind_speed, precipitation
        )
        q_solar = self.model.compute_solar_gain(solar_radiation)

        # Thermal power the room needs to sit at the setpoint.
        q_demand = u_eff * (target - outdoor_temp) - p.internal_gains - q_solar
        # Slab temperature that delivers exactly that, plus a pull-back term
        # if the room has drifted away from the setpoint.
        slab_target = (
            target
            + max(0.0, q_demand) / k_slab
            + 2.0 * (target - state.room_temperature)
        )

        q_slab_to_room = k_slab * (state.slab_temperature - state.room_temperature)
        # Replace what the slab gives up to the room, and move the slab to
        # where it needs to be.
        return q_slab_to_room + p.slab_thermal_mass * (
            slab_target - state.slab_temperature
        ) / dt

    def _baseline_thermal_demand_two_zone(
        self,
        state: ThermalState,
        target: float,
        outdoor_temp: float,
        wind_speed: float,
        precipitation: float,
        solar_radiation: float,
        dt: float,
    ) -> float:
        """Thermal power a thermostat needs this step in the two-zone model.

        The upper floor is fed directly by radiators while the lower floor is
        fed through the slab, and the split between them is fixed by
        ``radiator_power_fraction``. One control cannot hold both zones exactly,
        which is also true of the real system being modelled, so the demand of
        the two zones is summed the way an outdoor-reset curve on a single
        mixing valve would.
        """
        p = self.model.params
        k_slab = p.slab_heat_transfer_floored

        u_upper = self.model.effective_heat_loss_coefficient(
            p.upper_floor_heat_loss, wind_speed, precipitation
        )
        u_lower = self.model.effective_heat_loss_coefficient(
            p.lower_floor_heat_loss_learned, wind_speed * 0.5, precipitation * 0.5
        )
        q_solar_upper, q_solar_lower = self.model.solar_gain_per_zone(solar_radiation)
        area_ratio = p.upper_floor_area_ratio
        q_int_upper = p.internal_gains * area_ratio
        q_int_lower = p.internal_gains * (1.0 - area_ratio)

        t_upper = state.upper_floor_temperature
        t_lower = state.lower_floor_temperature
        q_inter = p.inter_zone_transfer * (t_lower - t_upper)

        # Radiators reach the upper floor within the step, so its demand is
        # met directly, including the pull-back on any drift.
        q_upper = (
            u_upper * (target - outdoor_temp)
            - q_solar_upper
            - q_int_upper
            - q_inter
            + p.upper_floor_thermal_mass * (target - t_upper) / dt
        )
        q_upper = max(0.0, q_upper)

        # The lower floor is heated through the slab, so drive the slab to the
        # temperature that sustains it and charge it over this step.
        q_lower = (
            u_lower * (target - outdoor_temp) - q_solar_lower - q_int_lower + q_inter
        )
        slab_target = (
            target + max(0.0, q_lower) / k_slab + 2.0 * (target - t_lower)
        )
        q_slab_to_lower = k_slab * (state.slab_temperature - t_lower)
        q_floor = q_slab_to_lower + p.slab_thermal_mass * (
            slab_target - state.slab_temperature
        ) / dt
        q_floor = max(0.0, q_floor)

        # The heat pump makes one water temperature and the split between
        # radiators and floor is fixed, so total output is sized to total
        # demand the way an outdoor-reset curve does. The zones then settle at
        # slightly different temperatures, which is what the real system does
        # too, and inter-zone transfer pulls them back together.
        thermal = q_upper + q_floor

        # Replace what the buffer tank leaks so it does not sag over the day.
        thermal += p.buffer_tank_heat_loss_coefficient * max(
            0.0, state.buffer_tank_temperature - TANK_ROOM_AMBIENT_TEMP
        )
        return thermal

    def _stored_thermal_energy(
        self,
        state: ThermalState,
        include_dhw: bool = False,
        caps: dict[str, float] | None = None,
    ) -> float:
        """Thermal energy stored in the building mass (and optionally the tank).

        Used to settle up at the end of the horizon. The optimizer is free to
        run the house and tank down towards the end of the window because
        nothing past the horizon is penalised, and without this correction that
        borrowed heat is reported as a saving even though it has to be paid back
        in the next window.

        ``caps`` limits each store to the temperature above which the heat is of
        no further use, so that passive overheating is not mistaken for charge.
        """
        p = self.model.params
        caps = caps or {}

        def _t(value: float, cap_key: str) -> float:
            cap = caps.get(cap_key)
            return min(value, cap) if cap is not None else value

        if p.two_zone_enabled:
            stored = (
                p.slab_thermal_mass * _t(state.slab_temperature, "slab")
                + p.upper_floor_thermal_mass
                * _t(state.upper_floor_temperature, "room")
                + p.lower_floor_thermal_mass
                * _t(state.lower_floor_temperature, "room")
                + p.buffer_tank_thermal_mass
                * _t(state.buffer_tank_temperature, "buffer")
            )
            if (
                p.two_tank_modelled
                and state.wood_tank_temperature is not None
            ):
                # Symmetric with the buffer: heat still in the wood tank at
                # the horizon end is heat the next window does not buy.
                stored += p.wood_tank_thermal_mass * _t(
                    state.wood_tank_temperature, "wood"
                )
        else:
            stored = (
                p.slab_thermal_mass * _t(state.slab_temperature, "slab")
                + p.room_thermal_mass * _t(state.room_temperature, "room")
            )
        if include_dhw:
            stored += p.dhw_tank_thermal_mass * _t(state.dhw_temperature, "dhw")
        return float(stored)

    def _replay_end_state(
        self,
        initial_state: ThermalState,
        power_schedule: np.ndarray,
        outdoor_temps: np.ndarray,
        wind_speeds: np.ndarray,
        precipitation: np.ndarray,
        solar_radiation: np.ndarray,
        dt: float,
        external_heat_kw: np.ndarray | None = None,
        valve_targets: np.ndarray | None = None,
        humidity: np.ndarray | None = None,
    ) -> ThermalState:
        """Final state after running a power schedule through the model.

        The optimizer's own trajectories only carry the room and slab, so a
        state rebuilt from them silently falls back to defaults for the zone and
        buffer temperatures. Replaying the schedule keeps every part of the
        state consistent with the model in both single and two-zone mode.
        """
        state = initial_state
        for i in range(len(power_schedule)):
            state = self.model.simulate_step(
                state, float(power_schedule[i]), outdoor_temps[i],
                wind_speeds[i], precipitation[i], solar_radiation[i], dt,
                external_heat_kw=(
                    float(external_heat_kw[i])
                    if external_heat_kw is not None
                    else 0.0
                ),
                valve_target=(
                    float(valve_targets[i])
                    if valve_targets is not None
                    else None
                ),
                humidity=_step_humidity(humidity, i),
            )
        return state

    def _power_to_setpoints(
        self,
        power_schedule: np.ndarray,
        room_temps: np.ndarray,
        outdoor_temps: np.ndarray,
    ) -> list[float]:
        """Convert power schedule to equivalent temperature setpoints."""
        setpoints: list[float] = []
        for power, _room_t in zip(power_schedule, room_temps):
            p_norm = _power_fraction(power, self.model.params)
            displacement = p_norm * (self.config.max_temp - self.config.min_temp)
            setpoint = self.config.min_temp + displacement
            setpoints.append(round(float(setpoint), 1))

        return setpoints

    def _power_to_displace_schedule(
        self,
        power_schedule: np.ndarray,
        outdoor_temps: np.ndarray,
        forecast_analysis: dict[str, Any] | None = None,
    ) -> list[float]:
        """Map optimized power to ECL110 displace values with PID-aware smoothing."""
        p = self.model.params
        d_min = p.ecl110_displace_min
        d_max = p.ecl110_displace_max

        solar_reduction = (forecast_analysis or {}).get("solar_reduction_factor", 1.0)
        wind_factor = (forecast_analysis or {}).get("wind_anticipation_factor", 1.0)
        rain_factor = (forecast_analysis or {}).get("rain_anticipation_factor", 1.0)

        displacement_bias = (
            (wind_factor - 1.0) * 3.0
            + (rain_factor - 1.0) * 4.0
            - (1.0 - solar_reduction) * 5.0
        )

        raw_displace: list[float] = []
        for i, power in enumerate(power_schedule):
            p_norm = _power_fraction(power, p)
            displace = d_min + p_norm * (d_max - d_min)

            if i < int(max(1, 8 / self.config.dt_hours)):
                displace += displacement_bias

            out_t = outdoor_temps[i] if i < len(outdoor_temps) else outdoor_temps[-1]
            if out_t < 0:
                displace += min(2.0, abs(out_t) * 0.08)

            raw_displace.append(float(np.clip(displace, d_min, d_max)))

        tau = p.ecl110_pid_tau_hours
        alpha = float(np.clip(self.config.dt_hours / tau, 0.0, 1.0))
        effective = 0.0
        filtered: list[float] = []
        for cmd in raw_displace:
            effective = effective + alpha * (cmd - effective)
            filtered.append(round(float(np.clip(effective, d_min, d_max)), 1))

        return filtered

    def _power_to_heat_pump_schedule(
        self,
        space_power_schedule: np.ndarray,
        dhw_power_schedule: np.ndarray | None = None,
    ) -> list[bool]:
        """ON/OFF supply-enable decisions: ON when the step books heat.

        The plan's own running rule, owned by ``planned_draws_run``. This used
        to decide at half the pump's minimum electrical power -- the threshold
        a METER reading needs, which ``on_threshold_kw`` still owns -- and on a
        fixed-speed pump that is half the rating, so the switch path switched
        off steps whose heat the same plan's trajectory, cost and published
        savings booked as delivered (R9 D12-s2-01, #1644 P2). A step below the
        modulation floor is duty cycling within the step, which is what the
        solve's own bounds say: the pump is commanded on for it and its own
        thermostat cycles it, while the objective prices the chatter.
        """
        return planned_draws_run(space_power_schedule, dhw_power_schedule)

    def _idle_action(self) -> CurrentAction:
        """The do-nothing action: shared by the empty-plan branch and the
        pre-horizon clamp so the two fallbacks cannot drift apart."""
        return {
            "power": self.model.params.min_electrical_power,
            "setpoint": self.config.target_temp,
            "mode": "idle",
            "price": 0.0,
            "heat_pump_on": False,
            "displace_value": 0.0,
            "space_reason": None,
            "dhw_reason": None,
        }

    def get_current_action(
        self, result: OptimizationResult, current_time: datetime
    ) -> CurrentAction:
        """Get the current recommended action from the optimization result."""
        if not result.timestamps:
            return self._idle_action()

        # Instants, not wall clocks (R9 D14-s4-01): Home Assistant hands every
        # datetime in one ZoneInfo, and CPython subtracts and compares two that
        # share a tzinfo as naive wall time, so across a DST transition a
        # 15-minute step read as 75 and the autumn fold matched the wrong step.
        now_s = current_time.timestamp()
        starts = [ts.timestamp() for ts in result.timestamps]
        if now_s < starts[0]:
            # A pre-horizon clock (NTP step back, restored stale plan) would
            # fall through the loop below to the LAST step — the 24h-ahead
            # slot where terminal-value charging lives. Clamp to step 0 only
            # while the gap is within one step length; beyond that the plan
            # says nothing about now, so idle like the empty-plan branch.
            step_s = starts[1] - starts[0] if len(starts) > 1 else 900.0
            if starts[0] - now_s > step_s:
                return self._idle_action()
            i = 0
        else:
            # Find the current time step
            for i, start_s in enumerate(starts):
                if i + 1 < len(starts):
                    if start_s <= now_s < starts[i + 1]:
                        break
                else:
                    i = len(result.timestamps) - 1
                    break

        power = result.power_schedule[i]
        setpoint = result.optimal_setpoints[i]
        price = result.prices[i]
        displace_value = (
            result.displace_schedule[i]
            if result.displace_schedule and i < len(result.displace_schedule)
            else 0.0
        )
        # The schedule is the authority; the fallback is the same owner on the
        # same two circuits, for a result built without the field. Both read
        # the plan's own running rule, never the meter's threshold, so a step
        # this action declares off is a step the plan booked no heat for
        # (R9 D12-s2-01).
        dhw_power_at_i = (
            result.dhw_power_schedule[i]
            if result.dhw_power_schedule and i < len(result.dhw_power_schedule)
            else 0.0
        )
        heat_pump_on = (
            result.heat_pump_on_schedule[i]
            if result.heat_pump_on_schedule and i < len(result.heat_pump_on_schedule)
            else planned_draw_runs(power, dhw_power_at_i)
        )

        p_norm = _power_fraction(power, self.model.params)

        # The band is the SPACE circuit's, but "off" means the pump is off
        # (#1499): a space step below the band's first rung still runs, and
        # a step where only DHW books a draw is hot_water.
        space_on = planned_draw_runs(power)
        if not heat_pump_on:
            mode = "off"
        elif not space_on:
            mode = "hot_water"
        elif p_norm < 0.4:
            mode = "eco"
        elif p_norm < 0.7:
            mode = "normal"
        elif p_norm < 0.9:
            mode = "pre_heat"
        else:
            mode = "boost"

        action: CurrentAction = {
            "power": round(power, 2),
            "setpoint": setpoint,
            "mode": mode,
            "price": round(price, 4),
            "power_normalized": round(p_norm, 2),
            "heat_pump_on": bool(heat_pump_on),
            "displace_value": float(displace_value),
            # T6: the reason codes for THIS step ride with the action, so
            # the settlement can tag every booked SEK with why the plan
            # wanted that draw. This method already owns the one search for
            # the step covering now; re-deriving the index at settle time
            # would be a second chance to disagree about which step ran.
            "space_reason": (
                result.space_reasons[i]
                if result.space_reasons and i < len(result.space_reasons)
                else None
            ),
            "dhw_reason": (
                result.dhw_reasons[i]
                if result.dhw_reasons and i < len(result.dhw_reasons)
                else None
            ),
        }

        # The valve target for *this* step, when a hold schedule is in force.
        # It rides with the rest of the current action rather than being
        # re-derived by the actuator: this method already owns the one search
        # for the step covering now, and a second copy of that search is a
        # second chance to disagree about which step is current.
        if result.valve_target_schedule and i < len(result.valve_target_schedule):
            action["valve_target"] = round(
                float(result.valve_target_schedule[i]), 1
            )

        # Add zone-specific setpoints if available
        if result.upper_setpoints and i < len(result.upper_setpoints):
            action["upper_setpoint"] = result.upper_setpoints[i]
        if result.lower_setpoints and i < len(result.lower_setpoints):
            action["lower_setpoint"] = result.lower_setpoints[i]

        # Add solar gain info
        if result.solar_gain_trajectory and i < len(result.solar_gain_trajectory):
            action["solar_gain_kw"] = round(result.solar_gain_trajectory[i], 3)

        # Add DHW info
        if result.dhw_power_schedule and i < len(result.dhw_power_schedule):
            dhw_power = result.dhw_power_schedule[i]
            action["dhw_power"] = round(dhw_power, 2)
            action["dhw_heating_active"] = dhw_power > 0.1
        if result.baseline_power_schedule and i < len(result.baseline_power_schedule):
            action["baseline_kw"] = float(result.baseline_power_schedule[i])
        if result.dhw_temp_trajectory and i < len(result.dhw_temp_trajectory):
            action["dhw_temperature"] = round(result.dhw_temp_trajectory[i], 1)
        if result.predictive_info.get("dhw_target_temperature") is not None:
            action["dhw_target_temperature"] = result.predictive_info.get(
                "dhw_target_temperature"
            )

        # Add predictive info
        if result.predictive_info:
            action["solar_reduction_factor"] = round(
                result.predictive_info.get("solar_reduction_factor", 1.0), 2
            )
            action["wind_anticipation_factor"] = round(
                result.predictive_info.get("wind_anticipation_factor", 1.0), 2
            )
            action["pre_heat_urgency"] = round(
                result.predictive_info.get("pre_heat_urgency", 0.0), 2
            )

        return action


def optimize_in_process(
    optimizer: "HeatPumpOptimizer", inputs: SolveInputs
) -> OptimizationResult:
    """Picklable ``optimize`` entry for the worker process; lambdas are not.

    ``subprocess.Popen`` (via ``process_worker.py``) has to pickle the
    callable. The coordinator's three executor lambdas could not cross
    that boundary (#199 #290).
    """
    return optimizer.optimize(inputs=inputs)