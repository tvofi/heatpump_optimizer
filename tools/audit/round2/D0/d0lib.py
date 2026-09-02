"""Shared capture-and-race library for the round-2 D0 (price optimality) harnesses.

Not a harness: it prints no RESULT lines and is only imported by the scripts
beside it. Every script that imports it runs from the repository root with
PYTHONPATH=tests/hastub.

What it provides
  * the thread pin (before numpy), copied from tests/stress.py
  * ``Recorder``: a context manager that monkeypatches
    ``heatpump_optimizer.optimizer:_multi_start_minimize`` to record every
    call's objective, candidates, bounds, args, maxiter, batch objective and
    L-BFGS-B result, and ``HeatPumpOptimizer._optimize_space_only`` /
    ``_optimize_with_dhw`` to stash the ``_Horizon`` each solve ran on. The
    production path is otherwise untouched: the wrapper calls the real
    function and returns its result unchanged.
  * counters on ``ThermalModel.simulate_trajectory`` and
    ``simulate_trajectory_batch`` (function-evaluation counts, the
    contention-immune evidence)
  * ``lbfgsb``: the production L-BFGS-B call (same jac path, same options)
    re-issued from an arbitrary start with an arbitrary budget, so a
    challenger differs from production ONLY in what the harness changes
  * ``feasibility``: per-step comfort floor/ceiling violation of a space
    schedule on the recorded horizon, for the parity check
  * ``build_cell``: a scenario from tests/golden.py:make plus the profile
    grid in tests/profiles.py
"""
from __future__ import annotations

import os

for _threads in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_threads, "1")

import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402

from heatpump_optimizer import optimizer as opt_mod  # noqa: E402
from heatpump_optimizer import thermal_model as tm_mod  # noqa: E402
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer,
    OptimizationConfig,
    _batch_fd_gradient,
    _bounds_supported_by_batch,
    _scoped_minimize,
)
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel,
    ThermalParameters,
    ThermalState,
)
from profiles import DT, house, prices, weather  # noqa: E402

PRICE_PROFILES = (
    "winter_typical", "winter_extreme", "summer_typical", "summer_negative",
    "shoulder", "winter_narrow", "winter_moderate", "flat",
)
WEATHER_PROFILES = (
    "winter_cold", "winter_mild", "summer_warm", "summer_cool", "shoulder",
)
START = datetime(2026, 1, 15, 0, 0)


# ---------------------------------------------------------------------------
# Machine-condition footer every harness prints
# ---------------------------------------------------------------------------

def load1() -> float:
    try:
        return float(os.getloadavg()[0])
    except (AttributeError, OSError):
        return -1.0


def swapins() -> int:
    """Swap-ins since boot (macOS: vm.swapusage has no count; report 0)."""
    try:
        import resource

        return int(resource.getrusage(resource.RUSAGE_SELF).ru_nswap)
    except Exception:
        return 0


class CpuClock:
    """process vs thread CPU over a region, for RESULT thread_factor."""

    def __init__(self) -> None:
        self.process = 0.0
        self.thread = 0.0
        self._p0 = 0.0
        self._t0 = 0.0

    def __enter__(self):
        self._p0 = time.process_time()
        self._t0 = time.thread_time()
        return self

    def __exit__(self, *exc):
        self.process += time.process_time() - self._p0
        self.thread += time.thread_time() - self._t0

    @property
    def factor(self) -> float:
        return self.process / self.thread if self.thread > 1e-9 else 1.0


def footer(clock: CpuClock | None = None) -> None:
    factor = clock.factor if clock is not None else 1.0
    print(f"RESULT thread_factor={factor:.3f} ratio")
    print(f"RESULT load1={load1():.2f} load")
    print(f"RESULT swapins={swapins()} count")


# ---------------------------------------------------------------------------
# Scenario builder
# ---------------------------------------------------------------------------

@dataclass
class Cell:
    name: str
    optimizer: HeatPumpOptimizer
    model: ThermalModel
    state: ThermalState
    prices: np.ndarray
    outdoor: np.ndarray
    wind: np.ndarray
    rain: np.ndarray
    solar: np.ndarray
    two_zone: bool
    dhw: bool
    hours: int
    price_profile: str
    weather_profile: str

    def solve(self, **kw):
        return self.optimizer.optimize(
            self.state, self.prices, self.outdoor, self.wind, self.rain,
            self.solar, START, **kw,
        )


def _fit(arr, need):
    arr = np.asarray(arr, dtype=float)
    if len(arr) >= need:
        return arr[:need]
    reps = int(np.ceil(need / len(arr)))
    return np.tile(arr, reps)[:need]


def build_cell(
    price_profile: str = "winter_typical",
    weather_profile: str = "winter_cold",
    two_zone: bool = False,
    dhw: bool = True,
    hours: int = 24,
    config_overrides: dict | None = None,
    opt_overrides: dict | None = None,
    param_overrides: dict | None = None,
    state_overrides: dict | None = None,
) -> Cell:
    """tests/golden.py:make, inlined so the profile grid can be swept.

    Same house, same state, same tiling of a horizon longer than a day.
    """
    cfg = house(two_zone=two_zone, dhw=dhw)
    cfg.update(config_overrides or {})
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = dhw
    for key, value in (param_overrides or {}).items():
        setattr(params, key, value)
    opt_cfg = OptimizationConfig(
        horizon_hours=hours,
        time_step_minutes=15,
        target_temp=cfg["target_temperature"],
        min_temp=cfg["min_temperature"],
        max_temp=cfg["max_temperature"],
    )
    for key, value in (opt_overrides or {}).items():
        setattr(opt_cfg, key, value)
    price_series = prices(price_profile, START)
    outdoor, wind, rain, solar = weather(weather_profile, START)
    need = int(hours / DT)
    state = ThermalState(
        room_temperature=21.0,
        slab_temperature=22.0,
        outdoor_temperature=float(outdoor[0]),
        upper_floor_temperature=21.0,
        lower_floor_temperature=21.0,
        dhw_temperature=50.0,
        dhw_hours_since_legionella=20.0,
        buffer_tank_temperature=40.0,
    )
    for key, value in (state_overrides or {}).items():
        setattr(state, key, value)
    model = ThermalModel(params)
    name = (
        f"{price_profile}/{weather_profile}/"
        f"{'tz' if two_zone else 'sz'}/{'dhw' if dhw else 'nodhw'}/{hours}h"
    )
    return Cell(
        name=name,
        optimizer=HeatPumpOptimizer(model, opt_cfg),
        model=model,
        state=state,
        prices=_fit(price_series, need),
        outdoor=_fit(outdoor, need),
        wind=_fit(wind, need),
        rain=_fit(rain, need),
        solar=_fit(solar, need),
        two_zone=two_zone,
        dhw=dhw,
        hours=hours,
        price_profile=price_profile,
        weather_profile=weather_profile,
    )


# ---------------------------------------------------------------------------
# The capture
# ---------------------------------------------------------------------------

@dataclass
class Call:
    """One recorded ``_multi_start_minimize`` call."""

    index: int
    objective: object
    candidates: list
    bounds: list
    args: tuple
    maxiter: int
    batch_objective: object
    fd_eps: float
    result: object
    candidate_scores: list = field(default_factory=list)
    refined: list = field(default_factory=list)
    result_score: float = float("nan")
    horizon: object = None
    n_objective_calls: int = 0
    n_batch_calls: int = 0
    n_batch_rows: int = 0
    cpu_s: float = 0.0

    @property
    def n(self) -> int:
        return len(self.bounds)

    def score(self, x) -> float:
        return float(self.objective(np.asarray(x, dtype=float), *self.args))


class Recorder:
    """Record every multi-start call of the solves run inside the block."""

    def __init__(self) -> None:
        self.calls: list[Call] = []
        self.horizons: list = []
        self.sim_calls = 0
        self.sim_batch_calls = 0
        self.sim_batch_rows = 0
        self._patches = []

    # -- counters on the model -------------------------------------------
    def _wrap_sim(self, real):
        rec = self

        def wrapped(model_self, *a, **kw):
            rec.sim_calls += 1
            return real(model_self, *a, **kw)

        return wrapped

    def _wrap_sim_batch(self, real):
        rec = self

        def wrapped(model_self, initial_state, power_matrix, *a, **kw):
            rec.sim_batch_calls += 1
            rec.sim_batch_rows += int(np.asarray(power_matrix).shape[0])
            return real(model_self, initial_state, power_matrix, *a, **kw)

        return wrapped

    def __enter__(self):
        rec = self
        real_ms = opt_mod._multi_start_minimize

        def recording_ms(objective, candidates, bounds, args=(), maxiter=300,
                         batch_objective=None, fd_eps=1e-4):
            counts = {"obj": 0, "batch": 0, "rows": 0}

            def counted_objective(x, *a):
                counts["obj"] += 1
                return objective(x, *a)

            counted_batch = None
            if batch_objective is not None:
                def counted_batch(m, *a):
                    counts["batch"] += 1
                    counts["rows"] += int(np.asarray(m).shape[0])
                    return batch_objective(m, *a)

            scores = []
            for guess in candidates:
                try:
                    scores.append(float(objective(guess, *args)))
                except Exception:
                    scores.append(float("nan"))
            order = sorted(
                [i for i, s in enumerate(scores) if np.isfinite(s)],
                key=lambda i: scores[i],
            )
            t0 = time.process_time()
            res = real_ms(
                counted_objective, candidates, bounds, args=args,
                maxiter=maxiter, batch_objective=counted_batch, fd_eps=fd_eps,
            )
            cpu = time.process_time() - t0
            call = Call(
                index=len(rec.calls),
                objective=objective,
                candidates=[np.array(c, dtype=float) for c in candidates],
                bounds=list(bounds),
                args=tuple(args),
                maxiter=maxiter,
                batch_objective=batch_objective,
                fd_eps=fd_eps,
                result=res,
                candidate_scores=scores,
                refined=order[: opt_mod._MULTI_START_SOLVES],
                result_score=float(objective(res.x, *args)),
                horizon=rec.horizons[-1] if rec.horizons else None,
                n_objective_calls=counts["obj"],
                n_batch_calls=counts["batch"],
                n_batch_rows=counts["rows"],
                cpu_s=cpu,
            )
            rec.calls.append(call)
            return res

        real_space = HeatPumpOptimizer._optimize_space_only
        real_dhw = HeatPumpOptimizer._optimize_with_dhw

        def rec_space(opt_self, h):
            rec.horizons.append(h)
            return real_space(opt_self, h)

        def rec_dhw(opt_self, h):
            rec.horizons.append(h)
            return real_dhw(opt_self, h)

        self._patches = [
            mock.patch.object(opt_mod, "_multi_start_minimize", recording_ms),
            mock.patch.object(HeatPumpOptimizer, "_optimize_space_only", rec_space),
            mock.patch.object(HeatPumpOptimizer, "_optimize_with_dhw", rec_dhw),
            mock.patch.object(
                ThermalModel, "simulate_trajectory",
                self._wrap_sim(ThermalModel.simulate_trajectory),
            ),
            mock.patch.object(
                ThermalModel, "simulate_trajectory_batch",
                self._wrap_sim_batch(ThermalModel.simulate_trajectory_batch),
            ),
        ]
        for p in self._patches:
            p.start()
        return self

    def __exit__(self, *exc):
        for p in reversed(self._patches):
            p.stop()
        self._patches = []
        return False

    def adopted_call(self, result) -> Call | None:
        """The recorded call whose L-BFGS-B ``x`` became the plan."""
        plan = np.asarray(result.power_schedule, dtype=float)
        best = None
        best_err = np.inf
        for call in self.calls:
            x = np.asarray(call.result.x, dtype=float)
            if x.shape != plan.shape:
                continue
            lo = np.array([b[0] for b in call.bounds])
            hi = np.array([b[1] for b in call.bounds])
            err = float(np.max(np.abs(np.clip(x, lo, hi) - plan)))
            if err < best_err:
                best, best_err = call, err
        return best if best_err < 1e-9 else None


# ---------------------------------------------------------------------------
# Re-issuing production's L-BFGS-B call
# ---------------------------------------------------------------------------

def make_jac(call: Call, eps: float | None = None, use_batch: bool = True):
    """The jac production would build for this call (None on the scalar path)."""
    eps = call.fd_eps if eps is None else eps
    if not use_batch or call.batch_objective is None:
        return None
    if not _bounds_supported_by_batch(call.bounds):
        return None

    def jac(x, *a):
        return _batch_fd_gradient(
            call.batch_objective, a, x, float(call.objective(x, *a)), eps,
            call.bounds,
        )

    return jac


def lbfgsb(
    call: Call,
    x0: np.ndarray,
    maxiter: int | None = None,
    ftol: float = 1e-6,
    eps: float = 1e-4,
    use_batch: bool = True,
    maxfun: int | None = None,
):
    """Production's ``_scoped_minimize`` call from ``x0`` with these options.

    Defaults reproduce production exactly (options dict verbatim), so a
    challenger differs only in what the caller overrides.
    """
    options = {
        "maxiter": call.maxiter if maxiter is None else maxiter,
        "ftol": ftol,
        "eps": eps,
    }
    if maxfun is not None:
        options["maxfun"] = maxfun
    lo = np.array([b[0] for b in call.bounds])
    hi = np.array([b[1] for b in call.bounds])
    x0 = np.clip(np.asarray(x0, dtype=float), lo, hi)
    return _scoped_minimize(
        call.objective,
        x0,
        args=call.args,
        jac=make_jac(call, eps=eps, use_batch=use_batch),
        method="L-BFGS-B",
        bounds=call.bounds,
        options=options,
    )


def clip_to_bounds(call: Call, x: np.ndarray) -> np.ndarray:
    lo = np.array([b[0] for b in call.bounds])
    hi = np.array([b[1] for b in call.bounds])
    return np.clip(np.asarray(x, dtype=float), lo, hi)


# ---------------------------------------------------------------------------
# Feasibility parity
# ---------------------------------------------------------------------------

def trajectories(cell: Cell, call: Call, x: np.ndarray):
    h = call.horizon
    return cell.model.simulate_trajectory(
        initial_state=h.initial_state,
        power_schedule=np.asarray(x, dtype=float),
        outdoor_temps=h.outdoor_temps,
        wind_speeds=h.wind_speeds,
        precipitation=h.precipitation,
        solar_radiation=h.solar_radiation,
        dt_hours=h.dt,
        external_heat_kw=h.external_heat_kw,
        valve_targets=h.valve_targets,
        humidity=h.humidity,
        start_hour=float(h.step_hours[0]),
    )


def feasibility(cell: Cell, call: Call, x: np.ndarray) -> dict:
    """Comfort floor/ceiling violation of a space schedule, in degree-steps.

    The same series ``_comfort_terms`` scores: room[1:] single-zone, the
    two floors [1:] two-zone, against the horizon's per-step bounds.
    """
    h = call.horizon
    room, slab, upper, lower = trajectories(cell, call, x)
    lo, hi = h.temp_min_bounds, h.temp_max_bounds
    if cell.model.params.two_zone_enabled:
        series = (upper[1:], lower[1:])
    else:
        series = (room[1:],)
    under = sum(float(np.sum(np.maximum(0.0, lo - s))) for s in series)
    over = sum(float(np.sum(np.maximum(0.0, s - hi))) for s in series)
    worst = max(float(np.max(np.maximum(0.0, lo - s))) for s in series)
    tmin = min(float(np.min(s)) for s in series)
    return {"under": under, "over": over, "worst_under": worst, "min_temp": tmin}


def energy_cost(call: Call, x: np.ndarray) -> float:
    """Plain energy cost of the COMBINED draw at the horizon's prices, SEK."""
    h = call.horizon
    total = np.asarray(x, dtype=float)
    if call.args:
        total = total + np.asarray(call.args[0], dtype=float)
    return float(np.sum(h.prices * total) * h.dt)


# ---------------------------------------------------------------------------
# Structured challenger seeds
# ---------------------------------------------------------------------------

def bang_bang(call: Call, energy_kwh: float) -> np.ndarray:
    """Cheapest steps first, up to each step's upper bound."""
    h = call.horizon
    hi = np.array([b[1] for b in call.bounds])
    lo = np.array([b[0] for b in call.bounds])
    schedule = lo.copy()
    remaining = float(energy_kwh) - float(np.sum(lo) * h.dt)
    for idx in np.argsort(h.prices):
        if remaining <= 0:
            break
        take = min(hi[idx] - lo[idx], remaining / h.dt)
        schedule[idx] += take
        remaining -= take * h.dt
    return schedule


def seeds(
    call: Call, extra: list[np.ndarray] | None = None,
    bang_fracs: tuple = (0.6, 0.8, 1.0, 1.2, 1.5),
) -> dict[str, np.ndarray]:
    """Structured starting points beyond production's three."""
    h = call.horizon
    x_prod = clip_to_bounds(call, call.result.x)
    e_prod = float(np.sum(x_prod) * h.dt)
    out = {}
    for frac in bang_fracs:
        out[f"bang{frac:.1f}"] = bang_bang(call, e_prod * frac)
    hi = np.array([b[1] for b in call.bounds])
    lo = np.array([b[0] for b in call.bounds])
    out["zero"] = lo.copy()
    out["half"] = clip_to_bounds(call, 0.5 * (lo + hi))
    for k, c in enumerate(call.candidates):
        out[f"prod_cand{k}"] = clip_to_bounds(call, c)
    for k, c in enumerate(extra or []):
        out[f"extra{k}"] = clip_to_bounds(call, c)
    return out


# ---------------------------------------------------------------------------
# The race
# ---------------------------------------------------------------------------

@dataclass
class Arm:
    name: str
    x: np.ndarray
    score: float
    nit: int
    nfev: int
    message: str
    feas: dict
    energy: float
    pg: float = float("nan")


def projected_gradient(call: Call, x: np.ndarray, eps: float | None = None) -> float:
    """max |projected gradient| at x -- scipy's own PGTOL quantity.

    The gradient is production's batched 2-point estimate (or scipy's scalar
    one where the batch is not served); a component is zeroed where the
    variable sits at a bound and the gradient points out of the box.
    """
    x = clip_to_bounds(call, x)
    jac = make_jac(call, eps=eps)
    if jac is None:
        from scipy.optimize._numdiff import approx_derivative

        lo = np.array([b[0] for b in call.bounds])
        hi = np.array([b[1] for b in call.bounds])
        g = approx_derivative(
            lambda v: call.objective(v, *call.args), x, method="2-point",
            abs_step=call.fd_eps if eps is None else eps, bounds=(lo, hi),
        )
    else:
        g = jac(x, *call.args)
    lo = np.array([b[0] for b in call.bounds])
    hi = np.array([b[1] for b in call.bounds])
    at_lo = (x <= lo + 1e-12) & (g > 0)
    at_hi = (x >= hi - 1e-12) & (g < 0)
    g = np.where(at_lo | at_hi, 0.0, g)
    return float(np.max(np.abs(g)))


def run_arm(cell: Cell, call: Call, name: str, x0, **opts) -> Arm:
    res = lbfgsb(call, x0, **opts)
    x = clip_to_bounds(call, res.x)
    return Arm(
        name=name, x=x, score=call.score(x), nit=int(res.nit),
        nfev=int(res.nfev), message=str(res.message),
        feas=feasibility(cell, call, x), energy=energy_cost(call, x),
    )


def production_arm(cell: Cell, call: Call) -> Arm:
    x = clip_to_bounds(call, call.result.x)
    return Arm(
        name="production", x=x, score=call.score(x), nit=int(call.result.nit),
        nfev=int(call.result.nfev), message=str(call.result.message),
        feas=feasibility(cell, call, x), energy=energy_cost(call, x),
        pg=projected_gradient(call, x),
    )


def race(
    cell: Cell,
    call: Call,
    *,
    budget_maxiter: int = 3000,
    budget_ftol: float = 1e-12,
    random_starts: int = 6,
    seed: int = 0,
    extra_seeds: list | None = None,
    include: tuple = ("third", "restart", "budget", "seeds", "random", "eps", "polish"),
    bang_fracs: tuple = (0.6, 0.8, 1.0, 1.2, 1.5),
) -> dict:
    """Race challengers against production on the exact recorded objective.

    Every arm solves with production's L-BFGS-B call (same jac path, same
    bounds, same args); the arms differ only in start and budget:

      third   the candidate production scored and discarded, refined at
              production's budget (what _MULTI_START_SOLVES=3 would do)
      restart production's own answer, re-submitted to the SAME L-BFGS-B
              call (same maxiter, ftol, eps): a fresh curvature memory and
              nothing else. Improvement here means the FACTR stop fired on a
              stalled iteration, not at a stationary point
      budget  production's own answer, continued with maxiter/ftol relaxed
      seeds   structured bang-bang seeds at production's budget
      random  uniform-random starts inside the bounds, production's budget
      eps     production's answer continued with a different FD step
      polish  the best arm so far, continued at the relaxed budget
    """
    rng = np.random.default_rng(seed)
    arms: list[Arm] = [production_arm(cell, call)]
    prod = arms[0]

    if "third" in include:
        for k in range(len(call.candidates)):
            if k in call.refined:
                continue
            arms.append(run_arm(cell, call, f"third_cand{k}", call.candidates[k]))
    if "restart" in include:
        arms.append(run_arm(cell, call, "restart_same", prod.x))
    if "budget" in include:
        arms.append(run_arm(
            cell, call, "budget_warm", prod.x,
            maxiter=budget_maxiter, ftol=budget_ftol,
        ))
    if "seeds" in include:
        for name, x0 in seeds(call, extra_seeds, bang_fracs).items():
            if name.startswith("prod_cand"):
                continue
            arms.append(run_arm(cell, call, f"seed_{name}", x0))
    if "random" in include:
        lo = np.array([b[0] for b in call.bounds])
        hi = np.array([b[1] for b in call.bounds])
        for k in range(random_starts):
            x0 = lo + rng.random(call.n) * (hi - lo)
            arms.append(run_arm(cell, call, f"random{k}", x0))
    if "eps" in include:
        for eps in (1e-3, 1e-5):
            arms.append(run_arm(
                cell, call, f"eps{eps:g}_warm", prod.x,
                maxiter=budget_maxiter, ftol=budget_ftol, eps=eps,
            ))
    if "polish" in include:
        best = min(arms, key=lambda a: a.score)
        if best is not prod:
            arms.append(run_arm(
                cell, call, f"polish[{best.name}]", best.x,
                maxiter=budget_maxiter, ftol=budget_ftol,
            ))
    return {"production": prod, "arms": arms}


def parity_ok(prod: Arm, arm: Arm, tol: float = 1e-6) -> bool:
    """Comfort feasibility no worse than production's."""
    return (
        arm.feas["under"] <= prod.feas["under"] + tol
        and arm.feas["over"] <= prod.feas["over"] + tol
    )


def summarize(cell: Cell, call: Call, raced: dict, verbose: bool = True) -> dict:
    prod = raced["production"]
    feasible = [a for a in raced["arms"] if a is not prod and parity_ok(prod, a)]
    any_arm = [a for a in raced["arms"] if a is not prod]
    best_feas = min(feasible, key=lambda a: a.score) if feasible else None
    best_any = min(any_arm, key=lambda a: a.score) if any_arm else None
    bill = max(abs(prod.energy), 1e-9)
    by_name = {a.name: a for a in raced["arms"]}
    restart = by_name.get("restart_same")
    budget = by_name.get("budget_warm")
    out = {
        "cell": cell.name,
        "prod_score": prod.score,
        "prod_energy": prod.energy,
        "prod_nit": prod.nit,
        "prod_nfev": prod.nfev,
        "prod_msg": prod.message,
        "prod_pg": prod.pg,
        "prod_under": prod.feas["under"],
        "gap_restart": 0.0 if restart is None else prod.score - restart.score,
        "gap_budget": 0.0 if budget is None else prod.score - budget.score,
        "best_feasible": None if best_feas is None else best_feas.name,
        "gap_feasible": 0.0 if best_feas is None else prod.score - best_feas.score,
        "gap_feasible_pct": 0.0 if best_feas is None else 100.0 * (prod.score - best_feas.score) / max(abs(prod.score), 1e-9),
        "energy_gap_feasible": 0.0 if best_feas is None else prod.energy - best_feas.energy,
        "energy_gap_feasible_pct_bill": 0.0 if best_feas is None else 100.0 * (prod.energy - best_feas.energy) / bill,
        "best_any": None if best_any is None else best_any.name,
        "gap_any": 0.0 if best_any is None else prod.score - best_any.score,
        "step0_prod": float(prod.x[0]),
        "step0_best": None if best_feas is None else float(best_feas.x[0]),
    }
    if verbose:
        print(f"  {cell.name}: prod obj {prod.score:.4f} energy {prod.energy:.2f} nit {prod.nit} nfev {prod.nfev} pg {prod.pg:.3g} [{prod.message}] under {prod.feas['under']:.4f}")
        for a in sorted(raced["arms"], key=lambda a: a.score):
            if a is prod:
                continue
            flag = "ok " if parity_ok(prod, a) else "INF"
            print(f"     {flag} {a.name:<22} obj {a.score:10.4f} d={prod.score - a.score:+9.4f} energy {a.energy:8.2f} under {a.feas['under']:.4f} over {a.feas['over']:.4f} nit {a.nit:4d} nfev {a.nfev:5d}")
    return out


# ---------------------------------------------------------------------------
# An "improved" solver, patched in through the same seam, for the closed loop
# ---------------------------------------------------------------------------

class ImprovedSolver:
    """Production's multi-start plus the cheap fixes the race pointed at.

    Patched in through ``optimizer:_multi_start_minimize`` (the seam
    tests/optimality.py uses). Per call:
      1. production's own result (its 2 refined candidates, untouched);
      2. the discarded third candidate, refined;
      3. bang-bang seeds at ``fracs`` of the production answer's energy,
         refined at production's budget;
      4. the best of those re-submitted once to the same call (restart).
    The winner on the same objective is returned. Everything else in the
    solve -- bounds, args, jac path, options -- is production's.
    """

    def __init__(self, fracs=(0.6, 0.8), restart: bool = True, third: bool = True):
        self.fracs = fracs
        self.restart = restart
        self.third = third
        self.calls = 0
        self.improved_calls = 0
        self.total_gain = 0.0
        self.horizons: list = []
        self._patches = []

    def __enter__(self):
        me = self
        real_ms = opt_mod._multi_start_minimize
        real_space = HeatPumpOptimizer._optimize_space_only
        real_dhw = HeatPumpOptimizer._optimize_with_dhw

        def stash_space(opt_self, h):
            me.horizons.append(h)
            return real_space(opt_self, h)

        def stash_dhw(opt_self, h):
            me.horizons.append(h)
            return real_dhw(opt_self, h)

        def improved(objective, candidates, bounds, args=(), maxiter=300,
                     batch_objective=None, fd_eps=1e-4):
            me.calls += 1
            res = real_ms(objective, candidates, bounds, args=args,
                          maxiter=maxiter, batch_objective=batch_objective,
                          fd_eps=fd_eps)
            best, best_score = res, float(objective(res.x, *args))
            prod_score = best_score
            h = me.horizons[-1]
            lo = np.array([b[0] for b in bounds])
            hi = np.array([b[1] for b in bounds])
            x_prod = np.clip(res.x, lo, hi)
            e_prod = float(np.sum(x_prod) * h.dt)
            starts: list[np.ndarray] = []
            if me.third:
                scored = []
                for c in candidates:
                    try:
                        s = float(objective(c, *args))
                    except Exception:
                        s = float("nan")
                    scored.append(s)
                order = sorted([i for i, s in enumerate(scored) if np.isfinite(s)],
                               key=lambda i: scored[i])
                for i in order[opt_mod._MULTI_START_SOLVES:]:
                    starts.append(np.asarray(candidates[i], dtype=float))
            for frac in me.fracs:
                sched = lo.copy()
                remaining = e_prod * frac - float(np.sum(lo) * h.dt)
                for idx in np.argsort(h.prices):
                    if remaining <= 0:
                        break
                    take = min(hi[idx] - lo[idx], remaining / h.dt)
                    sched[idx] += take
                    remaining -= take * h.dt
                starts.append(sched)
            for x0 in starts:
                try:
                    r = real_ms(objective, [x0], bounds, args=args, maxiter=maxiter,
                                batch_objective=batch_objective, fd_eps=fd_eps)
                except Exception:
                    continue
                s = float(objective(r.x, *args))
                if np.isfinite(s) and s < best_score:
                    best, best_score = r, s
            if me.restart:
                try:
                    r = real_ms(objective, [best.x], bounds, args=args, maxiter=maxiter,
                                batch_objective=batch_objective, fd_eps=fd_eps)
                    s = float(objective(r.x, *args))
                    if np.isfinite(s) and s < best_score:
                        best, best_score = r, s
                except Exception:
                    pass
            if best_score < prod_score - 1e-9:
                me.improved_calls += 1
                me.total_gain += prod_score - best_score
            return best

        self._patches = [
            mock.patch.object(opt_mod, "_multi_start_minimize", improved),
            mock.patch.object(HeatPumpOptimizer, "_optimize_space_only", stash_space),
            mock.patch.object(HeatPumpOptimizer, "_optimize_with_dhw", stash_dhw),
        ]
        for p in self._patches:
            p.start()
        return self

    def __exit__(self, *exc):
        for p in reversed(self._patches):
            p.stop()
        return False
