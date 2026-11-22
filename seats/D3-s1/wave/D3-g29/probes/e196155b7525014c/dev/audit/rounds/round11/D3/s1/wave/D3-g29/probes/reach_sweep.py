#!/usr/bin/env python3
# Metric: production reach of the D3-g29 mutated symbols -- over every scenario of tests/golden.py:SCENARIOS
#   (the golden plan matrix, solved through HeatPumpOptimizer.optimize), the count of calls whose arguments
#   sit in the region where a box D3-g29 mutant can differ from the baseline (see each probe's header).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/reach_sweep.py [symbol]
# EXPECTED RESULT reach_<symbol>_calls=<n> count and one reach_<symbol>_<region>=<n> count per region (exact counts).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g29 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbols: custom_components.heatpump_optimizer.optimizer:_solver_status, _terminal_row_cost
#   (and the row_cost it returns), classify_space_steps, classify_dhw_steps, stored_heat_survival -- each
#   wrapped by mock.patch.object with a recording spy that calls the real function unchanged.
# Perturbation: none here (the spies are transparent); each probe_<key>.py applies its own one-line mutant.
# Imported by the probes (load_reach) so each probe prints the reach of its own symbol.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import math, sys
from pathlib import Path
from unittest import mock


def repo_root(start):
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
for p in (str(ROOT), str(ROOT / "tests"), str(ROOT / "custom_components")):
    if p not in sys.path:
        sys.path.insert(0, p)
import numpy as np  # noqa: E402
# tests/golden.py imports the package as `heatpump_optimizer` (custom_components on sys.path): spy on that module.
from heatpump_optimizer import optimizer as opt  # noqa: E402
from heatpump_optimizer.thermal_model import CHANNEL_ACTIVE_KW  # noqa: E402


def sweep(symbols=None, scenarios=None):
    """Solve every golden scenario once with spies on; return {symbol: {region: count}}."""
    import golden  # noqa: E402  (tests/golden.py, __main__-guarded)
    rec = {s: {} for s in ("solver_status", "terminal_row_cost", "classify_space_steps",
                           "classify_dhw_steps", "stored_heat_survival")}

    def bump(sym, region, n=1):
        rec[sym][region] = rec[sym].get(region, 0) + n

    r_status, r_trc = opt._solver_status, opt._terminal_row_cost
    r_space, r_dhw, r_shs = opt.classify_space_steps, opt.classify_dhw_steps, opt.stored_heat_survival

    def s_status(result, objective, x0):
        bump("solver_status", "calls")
        if result.success:
            bump("solver_status", "success")
            try:
                if not objective(result.x) <= objective(x0):
                    bump("solver_status", "success_but_worse_than_x0")
            except Exception:
                bump("solver_status", "success_objective_raises")
        return r_status(result, objective, x0)

    def s_trc(refill_price, cop_end, cop_buffer, stores, refill=None):
        bump("terminal_row_cost", "calls")
        bump("terminal_row_cost", "split_branch" if cop_buffer != cop_end else "single_branch")
        bump("terminal_row_cost", "refill_set" if refill is not None else "refill_none")
        if not cop_end > 1e-6:
            bump("terminal_row_cost", "cop_end_le_1e-6")
        if not cop_buffer > 1e-6:
            bump("terminal_row_cost", "cop_buffer_le_1e-6")
        rec["terminal_row_cost"]["min_cop_end"] = min(rec["terminal_row_cost"].get("min_cop_end", math.inf), float(cop_end))
        rec["terminal_row_cost"]["min_cop_buffer"] = min(rec["terminal_row_cost"].get("min_cop_buffer", math.inf), float(cop_buffer))
        return r_trc(refill_price, cop_end, cop_buffer, stores, refill)

    def s_space(power, prices, room_temps, temp_min_bounds, heat_loss_factors, surplus, n_steps,
                threshold=CHANNEL_ACTIVE_KW, *, other=None, caps=None):
        bump("classify_space_steps", "calls")
        if n_steps == 0:
            bump("classify_space_steps", "n_steps_zero")
        if threshold != CHANNEL_ACTIVE_KW:
            bump("classify_space_steps", "nondefault_threshold")
        pw, _ = opt._heating_draws(power, other)
        for i in range(n_steps):
            if pw[i] == threshold:
                bump("classify_space_steps", "power_eq_threshold")
            if pw[i] <= threshold:
                continue
            bump("classify_space_steps", "active_steps")
            if i + 1 == len(room_temps):
                bump("classify_space_steps", "room_index_at_len")
            room = room_temps[i + 1] if i + 1 < len(room_temps) else room_temps[-1]
            if room == temp_min_bounds[i] + 0.15:
                bump("classify_space_steps", "room_eq_floor_plus_015")
            if surplus is not None and i < len(surplus) and surplus[i] == 1e-6:
                bump("classify_space_steps", "surplus_eq_1e-6")
            if i < len(heat_loss_factors) and heat_loss_factors[i] == 1.1:
                bump("classify_space_steps", "hlf_eq_1.1")
        return r_space(power, prices, room_temps, temp_min_bounds, heat_loss_factors, surplus, n_steps,
                       threshold, other=other, caps=caps)

    def s_dhw(power, in_window, ready_temps, legionella_step, n_steps, threshold=CHANNEL_ACTIVE_KW, idle=None):
        bump("classify_dhw_steps", "calls")
        if threshold != CHANNEL_ACTIVE_KW:
            bump("classify_dhw_steps", "nondefault_threshold")
        pw, _ = opt._heating_draws(power, (idle or opt.IdleContext()).other)
        bump("classify_dhw_steps", "power_eq_threshold", int(np.sum(np.asarray(pw[:n_steps]) == threshold)))
        return r_dhw(power, in_window, ready_temps, legionella_step, n_steps, threshold, idle)

    def s_shs(ua, cap, demand, ambient=opt.DHW_COOLING_REFERENCE_AMBIENT_TEMP):
        bump("stored_heat_survival", "calls")
        if ua > 0.0:
            span = cap - ambient
            if span < 0.0:
                bump("stored_heat_survival", "span_negative")
            if span == 0.0:
                bump("stored_heat_survival", "span_zero")
                if demand <= 0.0:
                    bump("stored_heat_survival", "span_zero_demand_le0")
            if span > 0.0 and demand > 0.0 and 0.5 * ua * span / demand > 700.0:
                bump("stored_heat_survival", "exponent_over_700")
        return r_shs(ua, cap, demand, ambient)

    names = list(scenarios or golden.SCENARIOS)
    with mock.patch.object(opt, "_solver_status", s_status), \
            mock.patch.object(opt, "_terminal_row_cost", s_trc), \
            mock.patch.object(opt, "classify_space_steps", s_space), \
            mock.patch.object(opt, "classify_dhw_steps", s_dhw), \
            mock.patch.object(opt, "stored_heat_survival", s_shs):
        for name in names:
            golden.capture(name, golden.SCENARIOS[name])
    rec["_scenarios"] = len(names)
    return {k: v for k, v in rec.items() if symbols is None or k in symbols or k == "_scenarios"}


def print_reach(rec):
    n = rec.get("_scenarios", 0)
    print(f"RESULT reach_scenarios={n} count")
    for sym, regions in rec.items():
        if sym.startswith("_"):
            continue
        for region, v in sorted(regions.items()):
            print(f"RESULT reach_{sym}_{region}={v}")


if __name__ == "__main__":
    print_reach(sweep(set(sys.argv[1:]) or None))
