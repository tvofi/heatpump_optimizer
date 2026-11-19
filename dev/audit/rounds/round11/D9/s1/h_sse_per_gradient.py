"""D9-s1 sse_per_gradient: simulate-step-equivalents per gradient evaluation.

Metric (D9.md): SSE = scalar ThermalModel.simulate_step calls + rows of
ThermalModel.simulate_trajectory_batch, both hooked by monkeypatching the
production symbols; per gradient = SSE inside an L-BFGS-B run
(optimizer._scoped_minimize) / that run's batched gradients
(optimizer._batch_fd_gradient calls), and SSE inside a
_multi_start_minimize call / its njev. Counts are keyed on the rows the
production seam is handed (power_matrix.shape[0]), never on bounds shape.

Also splits a solve's SSE by caller path (C3: the DHW planning loops) --
_dhw_build / _co_optimize / _avoid_priced_switches / _commit_runs /
_relaxed_plans -- and reports each DHW-loop path's rows per gradient.

Command (from the export root):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
        dev/audit/rounds/round11/D9/s1/h_sse_per_gradient.py

Perturbation: --horizon 12 (n 96 -> 48): rows/gradient must go DOWN 97 -> 49;
and optimizer._bounds_supported_by_batch forced False (one-line edit, the
scalar-FD path): SSE per gradient must go UP to ~n*(n+1)/... (scipy FD,
n+1 scalar trajectories of n steps -> ~9,300).

Expected: rows per batched gradient = n_free + 1 exactly (97 at n=96), every
scenario, 0 scalar-jac runs. Counts exact; CPU figures provisional.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B1 container.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d9s1lib as L  # noqa: E402

DUTY = dict(cycling_cost=2.0, duty_switch_stop_probability=(0.5, 0.5),
            duty_switch_off_seconds=(300.0, 300.0))

# name -> (make_solve kind, config overrides, params overrides, price, weather)
CELLS = {
    "two_zone_dhw": ("two_zone_dhw", {}, {}, "winter_typical", "winter_cold"),
    "single_zone": ("single_zone", {}, {}, "winter_typical", "winter_cold"),
    "single_zone_dhw": ("single_zone_dhw", {}, {}, "winter_typical", "winter_cold"),
    "dhw_cap_zero_range": ("dhw_cap_zero_range", {}, {}, "winter_typical", "winter_cold"),
    "manual_pin": ("manual_pin", {}, {}, "winter_typical", "winter_cold"),
    # DHW planning loops (C3): _co_optimize re-plans when space is pinned
    # under a DHW block (a 3 kW pump); priced switches add the second relaxed
    # multi-start and the _commit_runs re-solves; _avoid_priced_switches is
    # reached at its switch_weight gate under DUTY.
    "dhw_coopt_small_pump": ("two_zone_dhw", {}, {"max_electrical_power": 3.0},
                             "winter_typical", "winter_cold"),
    "dhw_duty_two_zone": ("two_zone_dhw", DUTY, {}, "winter_typical", "winter_cold"),
    "dhw_duty_small_pump": ("two_zone_dhw", DUTY, {"max_electrical_power": 3.0},
                            "winter_typical", "winter_cold"),
    "dhw_duty_shoulder": ("single_zone_dhw", DUTY, {}, "shoulder", "shoulder"),
}

DHW_PATH_KEYS = ("_co_optimize", "_avoid_priced_switches", "_dhw_build",
                 "_dhw_coil_wood_forecast", "_commit_runs")


def run_cell(name, horizon, scalar=False):
    from heatpump_optimizer import optimizer as om
    kind, cfg, par, price, wx = CELLS[name]
    opt, inp, n = L.make_solve(kind, horizon_hours=horizon, price=price, wx=wx)
    for k, v in cfg.items():
        setattr(opt.config, k, v)
    for k, v in par.items():
        setattr(opt.model.params, k, v)
    real_gate = om._bounds_supported_by_batch
    if scalar:
        om._bounds_supported_by_batch = lambda bounds: False
    reached = {"avoid_gate": 0}
    real_sw = om.duty_legs.switch_weight

    def sw(*a, **k):
        reached["avoid_gate"] += 1
        return real_sw(*a, **k)

    om.duty_legs.switch_weight = sw
    c = L.Counters().install()
    t0 = time.process_time()
    try:
        res = opt.optimize(inputs=inp)
    finally:
        cpu = time.process_time() - t0
        c.uninstall()
        om._bounds_supported_by_batch = real_gate
        om.duty_legs.switch_weight = real_sw
    tag = f"{name}.h{horizon}" + (".scalar" if scalar else "")
    batched = [r for r in c.runs if r["jac"]]
    scalar_runs = [r for r in c.runs if not r["jac"]]
    run_sse = sum(r["sse"] for r in batched)
    L.result(f"{tag}.n_steps", n, "steps")
    L.result(f"{tag}.status", str(res.status).replace(" ", "_"), "enum")
    L.result(f"{tag}.sse_total", c.sse, "sse")
    L.result(f"{tag}.batched_gradients", c.fd_grads, "count")
    L.result(f"{tag}.rows_per_batched_gradient",
             (run_sse / c.fd_grads) if c.fd_grads else 0.0, "sse/gradient")
    L.result(f"{tag}.scalar_jac_runs", len(scalar_runs), "count")
    if scalar_runs:
        nj = sum(r["njev"] for r in scalar_runs)
        L.result(f"{tag}.scalar_sse_per_gradient",
                 sum(r["sse"] for r in scalar_runs) / max(1, nj), "sse/gradient")
    msm_sse = sum(m["sse"] for m in c.msm)
    msm_nj = sum(m["njev"] for m in c.msm)
    L.result(f"{tag}.msm_calls", len(c.msm), "count")
    L.result(f"{tag}.msm_sse_per_njev", msm_sse / max(1, msm_nj), "sse/gradient")
    L.result(f"{tag}.sse_outside_runs_share", (c.sse - sum(r["sse"] for r in c.runs)) / max(1, c.sse), "1")
    # caller-path split (C3)
    for key in DHW_PATH_KEYS + ("_relaxed_plans",):
        sse = sum(v for p, v in c.by_path.items() if key in p.split(">"))
        L.result(f"{tag}.path.{key}.sse", sse, "sse")
        runs = [r for r in batched if key in r["path"].split(">")]
        g = sum(r["njev"] for r in runs)
        if runs:
            L.result(f"{tag}.path.{key}.sse_per_njev", sum(r["sse"] for r in runs) / max(1, g),
                     "sse/gradient")
    L.result(f"{tag}.avoid_priced_switches_gate_reached", reached["avoid_gate"], "count")
    L.result(f"{tag}.solve_cpu_s", cpu, "s")
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizon", type=int, default=24)
    ap.add_argument("--cells", default=",".join(CELLS))
    ap.add_argument("--scalar", action="store_true",
                    help="perturbation: _bounds_supported_by_batch -> False")
    a = ap.parse_args()
    clock = L.Clock()
    swap0 = L.swapins()
    for name in a.cells.split(","):
        run_cell(name, a.horizon, a.scalar)
    L.result("reference_solve_cpu_ms", L.ref_ms(), "ms")
    L.tail(clock, swap0=swap0)


if __name__ == "__main__":
    main()
