"""D2.M3 predicted-cost-sum on the risk-priced path: what the published money
figures carry when price_risk_lambda > 0.

Metric definitions (one line each), keyed on the OptimizationResult fields the
coordinator publishes (predicted_cost, baseline_cost, predicted_savings, prices):
  spend_premium    = result.predicted_cost - sum(raw input price * planned draw * dt)
  baseline_premium = result.baseline_cost  - sum(raw input price * baseline draw * dt)
  savings_inflation= baseline_premium - spend_premium (what the published saving gains from
                     prices nobody pays, before the settlement term)
  price_dev        = max |result.prices - raw input prices| (the per-step price the
                     schedule attribute publishes)
Grid: lambda in {0 (null control), 0.5, 1.0, 2.0 (config max)} on the price_risk golden
(sigma 0.5 on the 45 % guessed tail), and lambda 1.0 on winter_single_dhw and
horizon_48h with the same sigma rule.
Run:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D2/s3/m3_risk.py
Expected: every figure 0 at lambda 0; savings_inflation ~12.5 currency at lambda 1 on price_risk.
Perturbation: optimizer.HeatPumpOptimizer._stash_price_horizon returning the raw prices
(the risk premium kept out of the published figures) takes every figure to_zero.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine B6 (shared).
"""
import _common  # noqa: F401
from _common import footer, solve_golden, np

import argparse
import golden

ap = argparse.ArgumentParser()
ap.add_argument("--perturb-raw", action="store_true")
a = ap.parse_args()
from heatpump_optimizer import optimizer as om  # noqa: E402

if a.perturb_raw:
    # Keep the risk premium in the solve only: price the published figures raw.
    _orig = om.HeatPumpOptimizer._build_result

    def _br(self, h, **kw):
        raw = self._raw_prices_for_report
        P = kw["space_power"] + (kw.get("dhw_power") if kw.get("dhw_power") is not None else 0.0)
        bl = kw.get("baseline_power")
        f = self._energy_cost_fn(raw, h.dt)
        kw["predicted_cost"] = float(f(P))
        if bl is not None:
            kw["baseline_cost"] = float(f(bl))
        kw["savings"] = kw["baseline_cost"] - kw["predicted_cost"] - kw["deferred_cost"]
        out = _orig(self, h, **kw)
        out.prices = list(map(float, raw))
        return out
    om.HeatPumpOptimizer._build_result = _br
    _orig_stash = om.HeatPumpOptimizer._stash_price_horizon

    def _stash(self, initial_state, n_steps, price_known, price_sigma, prices, pv_surplus):
        self._raw_prices_for_report = np.asarray(prices, dtype=float)[:n_steps]
        return _orig_stash(self, initial_state, n_steps, price_known, price_sigma, prices, pv_surplus)
    om.HeatPumpOptimizer._stash_price_horizon = _stash

worst = 0.0
cells = []
for name, lam in [("price_risk", 0.0), ("price_risk", 0.5), ("price_risk", 1.0), ("price_risk", 2.0),
                  ("winter_single_dhw", 1.0), ("horizon_48h", 1.0)]:
    def patch(o, lam=lam):
        o.config.price_risk_lambda = lam
    if name != "price_risk":
        golden.RISK_SCENARIOS.add(name)
    try:
        rec = solve_golden(name, opt_patch=patch, keep=False)
    finally:
        if name != "price_risk":
            golden.RISK_SCENARIOS.discard(name)
    r, opt, inp = rec["result"], rec["opt"], rec["inputs"]
    n = len(r.power_schedule)
    dt = opt.config.dt_hours
    raw = np.asarray(inp.forecast.prices, dtype=float)[:n]
    P = np.asarray(r.power_schedule) + (np.asarray(r.dhw_power_schedule) if r.dhw_power_schedule else 0.0)
    bl = np.asarray(r.baseline_power_schedule)
    sp = r.predicted_cost - float(np.sum(raw * P) * dt)
    bp = r.baseline_cost - float(np.sum(raw * bl) * dt)
    pdv = float(np.max(np.abs(np.asarray(r.prices) - raw)))
    infl = bp - sp
    if lam > 0:
        cells.append(infl)
    worst = max(worst, abs(infl))
    print(f"CELL risk golden={name} lambda={lam} spend_premium={sp:.4f} baseline_premium={bp:.4f} "
          f"savings_inflation={infl:.4f} published_savings={r.predicted_savings:.4f} "
          f"published_baseline={r.baseline_cost:.4f} price_dev={pdv:.3f}", flush=True)
print(f"RESULT savings_inflation_max={worst:.4f} currency")
print(f"RESULT savings_inflation_lambda1_price_risk={cells[1]:.4f} currency")
footer()
