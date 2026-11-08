"""R10-PARTLOAD-RESIDUE: the solver CPU the residue of #3182 left measure-first.

    PYTHONPATH=tests/hastub:custom_components:tests \\
        taskset -c 0 python3 dev/audit/harnesses/r10_partload_residue.py relaxed|buffer N|refill

Synthetic throughout; every time is ``time.process_time`` of one process
pinned to one core, so a Raspberry-Pi-class figure is this figure times the
stated per-core ratio (the pull-request body derives it). The budget a solve
is held against is the shortest optimisation interval the options flow
accepts (``config_flow``'s ``CONF_OPTIMIZATION_INTERVAL`` slider minimum,
10 min); the default interval is 30 min.

``relaxed``: the relaxed duty-cycle pass (``optimizer._relaxed_starts``) on
R10-SETPOINT-BOOST's 16 installs, spread and flat price days, at ``d = 0``
and at the central plant's derate (``r10_partload_pricing.solve``). Two arms
per cell: production, and the pass removed (``_relaxed_starts`` as
identity, ``r10_setpoint_boost.solve``'s own perturbation). Printed: the
seconds spent inside ``_relaxed_starts`` and how many relaxed L-BFGS-B runs
it started, and the whole solve's seconds at both arms. Null control: the
cells whose levels do not ship clamped must start 0 relaxed runs; the
harness exits 1 otherwise.

``buffer N``: the live buffer store's solve cost, one lever at a time:
``r10_buffer_store.solve``'s owner shape (750 L behind a manual valve, slab,
seeded hourly prices, outdoor -15..8 degC) at 750 L and at no buffer, each
on the seeded spread days and on a flat day (the null: no cheap window to
store for). Printed per arm: p50 and worst ``process_time`` over N solves.

``refill``: #3182's carry 2 at a stated refill rate. ``_terminal_cost`` and
``deferred_energy_cost`` value heat at a COP with no draw, so under a derate
their secant error is the figure times ``P_r / heat_per_cop_kw(P_r) - 1``
(``r10_partload_pricing.py``'s rule, which prints it only at the floor, 0,
and at max power). The rate stated here is the plan's own: ``P_r``, the
energy-weighted mean of the published total draw (space plus hot water)
over its running steps, ``sum(P^2) / sum(P)``, the draw at which the plan
bought its mean kWh. Same cells and solves as ``r10_partload_pricing.py``
(``pp.solve``, ``pp.terminal_figure``). Printed per cell and as maxima: the
terminal and deferred errors at ``P_r``, beside the plan's hot-water cost
and its ``predicted_cost``. Null control: at ``d = 0`` both errors must read
exactly 0; the harness exits 1 otherwise.
"""
from __future__ import annotations

import sys
import time

import numpy as np

sys.path.insert(0, "dev/audit/harnesses")

import r10_buffer_store as bs  # noqa: E402
import r10_cop_partload as cp  # noqa: E402
import r10_partload_pricing as pp  # noqa: E402
import r10_setpoint_boost as sb  # noqa: E402
from heatpump_optimizer import optimizer as opt_mod  # noqa: E402
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel,
    ThermalParameters,
    heat_per_cop_kw,
)

BUDGET_S = 10 * 60.0


def central_derate() -> float:
    model = ThermalModel(ThermalParameters(
        min_electrical_power=cp.P_MIN, max_electrical_power=cp.P_MAX))
    eta = cp.calibrate(cp.CENTRAL, model.compute_cop(cp.OUTDOOR_C))
    return round(1.0 - cp.plant_cop(cp.P_MAX, *cp.CENTRAL, eta)[0]
                 / cp.plant_cop(cp.P_MIN, *cp.CENTRAL, eta)[0], 3)


def timed_solve(cell, prices, derate: float, relaxed: bool) -> tuple[float, float, int]:
    """(solve s, seconds inside the relaxed pass, relaxed runs started)."""
    kept = opt_mod._relaxed_starts
    seen = {"s": 0.0, "runs": 0}

    def wrapped(opt, objective, objective_batch, bounds, first, args, cands, maxiter):
        if not relaxed:
            return cands
        t = time.process_time()
        out = kept(opt, objective, objective_batch, bounds, first, args, cands, maxiter)
        seen["s"] += time.process_time() - t
        seen["runs"] += len(out) - len(cands)
        return out

    opt_mod._relaxed_starts = wrapped
    try:
        t = time.process_time()
        pp.solve(cell, prices, derate)
        return time.process_time() - t, seen["s"], seen["runs"]
    finally:
        opt_mod._relaxed_starts = kept


def relaxed() -> int:
    derate = central_derate()
    print(f"central plant derate {derate}; budget {BUDGET_S:.0f} s")
    null_bad = 0
    clamped_solves: list[float] = []
    clamped_pass: list[float] = []
    for tag, prices in (("spread", sb.SPREAD), ("flat", sb.FLAT)):
        for cell in sb.CELLS:
            for d in (0.0, derate):
                on, inside, runs = timed_solve(cell, prices, d, True)
                off, _, _ = timed_solve(cell, prices, d, False)
                clamped = cell[3]
                print(f"  {tag} {cell} d={d} clamped {clamped} relaxed_runs {runs}"
                      f" relaxed_pass_s {inside:.3f} solve_s {on:.3f}"
                      f" pass_removed_solve_s {off:.3f} delta_s {on - off:+.3f}")
                if clamped:
                    clamped_solves.append(on)
                    clamped_pass.append(inside)
                elif runs != 0:
                    null_bad += 1
    a, b = np.array(clamped_solves), np.array(clamped_pass)
    print(f"clamped solves {a.size}: solve_s p50 {np.median(a):.3f} max {a.max():.3f};"
          f" relaxed_pass_s p50 {np.median(b):.3f} max {b.max():.3f};"
          f" worst solve share of budget {a.max() / BUDGET_S:.5f}")
    print(f"null (unclamped) cells with a relaxed run {null_bad}")
    return 1 if null_bad else 0


def buffer(n: int) -> int:
    for buffer_l in (750.0, 0.0):
        for kind in ("spread", "flat"):
            rng = np.random.default_rng(2500)
            times = []
            for _ in range(n):
                hourly = rng.uniform(0.4, 3.0, size=24)
                prices = np.repeat(hourly, 4) if kind == "spread" else bs.FLAT
                outdoor = float(rng.uniform(-15.0, 8.0))
                t = time.process_time()
                bs.solve(buffer_l, prices, outdoor)
                times.append(time.process_time() - t)
            a = np.array(times)
            print(f"buffer {buffer_l:.0f} L {kind}: n {n} p50_s {np.median(a):.3f}"
                  f" max_s {a.max():.3f} worst share of budget {a.max() / BUDGET_S:.5f}")
    return 0


def refill() -> int:
    derate = central_derate()
    print(f"central plant derate {derate}")
    null_bad = failures = 0
    for tag, prices in (("spread", sb.SPREAD), ("flat", sb.FLAT)):
        for d in (0.0, derate):
            rows = []
            for cell in sb.CELLS:
                try:
                    opt, res = pp.solve(cell, prices, d)
                except Exception as err:  # counted, never dropped
                    failures += 1
                    print(f"  {tag} {cell} d={d} failed: {err!r}")
                    continue
                params = opt.model.params
                pr = np.asarray(res.prices, float)
                space = np.asarray(res.power_schedule, float)
                dhw = np.asarray(res.dhw_power_schedule or [0.0] * len(pr), float)
                total = space + dhw
                run = total[total > 0.0]
                p_r = float((run * run).sum() / run.sum()) if run.size else 0.0
                k_r = p_r / heat_per_cop_kw(params, p_r) - 1.0 if p_r > 0.0 else 0.0
                term = pp.terminal_figure(opt, res)
                defer = float(res.deferred_energy_cost)
                dhw_cost = float((pr * dhw).sum() * pp.DT_H)
                pred = float(res.predicted_cost)
                rows.append((term * k_r, abs(defer) * k_r, dhw_cost, pred,
                             term * k_r / pred if pred > 0 else 0.0))
                print(f"  {tag} {cell} d={d} P_r {p_r:.3f} k_r {k_r:.5f}"
                      f" | terminal {term:.4f} at-P_r {term * k_r:.6f}"
                      f" | deferred {defer:.4f} at-P_r {abs(defer) * k_r:.6f}"
                      f" | dhw cost {dhw_cost:.4f} | predicted {pred:.4f}")
                if d == 0.0 and (term * k_r != 0.0 or defer * k_r != 0.0):
                    null_bad += 1
            if rows:
                a = np.array(rows, float)
                print(f"{tag} d={d}: cells {len(rows)} terminal-at-P_r max {a[:, 0].max():.6f}"
                      f" deferred-at-P_r max {a[:, 1].max():.6f}"
                      f" (dhw cost max {a[:, 2].max():.4f}, predicted max {a[:, 3].max():.4f})"
                      f" terminal-at-P_r / predicted max {a[:, 4].max():.5f}")
    print(f"null rows not zero {null_bad}")
    print(f"failures {failures}")
    return 1 if null_bad or failures else 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["refill"]:
        return refill()
    if argv[:1] == ["relaxed"]:
        return relaxed()
    if argv[:1] == ["buffer"]:
        return buffer(int(argv[1]))
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
