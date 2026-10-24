"""D2 -- the money identities the optimizer's own published figures must satisfy,
re-derived from the plan it published, on every golden scenario.

METRIC (four identities, each a max absolute residual in currency units over
the 49 scenarios of `tests/golden.py:SCENARIOS`, re-solved live -- no committed
fixture is read, so the may-drift set cannot contaminate this):
  A  predicted_cost      == energy_cost(space + dhw)      [piecewise in PV]
  B  predicted_savings   == baseline_cost - predicted_cost - deferred_energy_cost
  C  savings_percentage  == clip(savings / baseline_cost * 100, -100, 100)
  D  dhw_heating_cost    == predicted_cost - energy_cost(space alone)
`energy_cost` is re-implemented here from the contract in
`HeatPumpOptimizer._energy_cost_fn`'s docstring -- sum(price*power)*dt, less
`pv.import_margin * min(power, surplus)` per step -- NOT by calling the
production closure, so the identity has an independent left-hand side.

COMMAND (from the repository root, ~7 min at load 12):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D2/cost_identity.py
    # one scenario only:
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D2/cost_identity.py winter_single_dhw

EXPECTED at baseline ae36eff: all four residuals <= 1e-9 currency units
(`max_resid_A..D`), `scenarios=49`, `violations=0`.  Tolerance 1e-9: these are
sums of at most 192 products of order 1, so double-precision round-off is
~1e-13; 1e-9 is four orders of slack.

PERTURBATION (direction stated): multiply the price array the identity is
re-derived from by 1.01 -> `max_resid_A` must rise to ~1% of the cost (about
1e-2, i.e. seven orders above tolerance).  Run as the `--perturb` arm here so a
verifier can see the harness is live rather than vacuously green.

HARNESS GAP ALREADY PAID FOR (do not repeat it): the published
`pv_surplus` attribute is `_pv_surplus_list`'s 3-decimal rounding of the array
the objective actually priced.  Re-deriving identity A from that copy produces a
residual of 5.087e-04 on `shoulder` and 2.469e-05 on `summer_dhw_only` that is
entirely the rounding, not the arithmetic.  This harness rebuilds the array from
`golden.pv_surplus_for` instead.

NULL CONTROL: the `flat_prices` and `valve_storage_flat_prices` scenarios are in
the matrix and are reported separately; a cost/savings identity must hold there
too, and identity B's residual at flat prices is the arm in which any
savings-accounting artefact must vanish.

BASELINE SHA: ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1
MACHINE: 8-core Apple M1, 8 GB, numpy 2.4.6 / scipy 1.17.1 on OpenBLAS
INSTRUMENTED SYMBOLS: optimizer.py:HeatPumpOptimizer.optimize,
    :_energy_cost_fn, :_baseline_dhw_economics, :_savings_percentage,
    :_build_result   (driven through tests/golden.py:capture)
"""
import sys

import d2lib  # noqa: F401  -- thread pin + sys.path, must be first
import numpy as np

import golden
from heatpump_optimizer import pv

# `capture` rounds every stored value to 6 decimals (golden.PRECISION), which
# is coarser than the identities being tested.  Raise it for this process only;
# nothing is written back to tests/golden/.
golden.PRECISION = 15

d2lib.repo_root_ok()

PERTURB = "--perturb" in sys.argv
ONLY = [a for a in sys.argv[1:] if not a.startswith("-")]


def energy_cost(prices, power, dt, surplus, export_price):
    """Independent re-implementation of `_energy_cost_fn`'s contract."""
    prices = np.asarray(prices, dtype=float)
    power = np.asarray(power, dtype=float)
    base = float(np.sum(prices * power) * dt)
    if surplus is None:
        return base
    s = np.asarray(surplus, dtype=float)[: len(prices)]
    if not np.any(s > 1e-6):
        return base
    margin = pv.import_margin(prices, export_price)
    covered = np.minimum(power, s)
    return float((np.sum(prices * power) - np.sum(margin * covered)) * dt)


def main() -> int:
    names = ONLY or list(golden.SCENARIOS)
    resid = {"A": [], "B": [], "C": [], "D": []}
    worst = {"A": ("", 0.0), "B": ("", 0.0), "C": ("", 0.0), "D": ("", 0.0)}
    flat_rows = {}
    n_done = 0
    for name in names:
        spec = golden.SCENARIOS[name]
        built = golden.make(**spec)
        opt = built["optimizer"]
        dt = opt.config.dt_hours
        payload = golden.capture(name, spec)
        # `capture` re-builds its own optimizer; read back the horizon the
        # published payload was produced with.
        prices = np.asarray(payload["prices"], dtype=float)
        if PERTURB:
            prices = prices * 1.01
        space = np.asarray(payload["power_schedule"], dtype=float)
        dhw = np.asarray(payload["dhw_power_schedule"], dtype=float)
        if dhw.size == 0:
            dhw = np.zeros_like(space)
        # NOT payload["pv_surplus"]: `_pv_surplus_list` rounds the published
        # attribute to 3 decimals while the objective prices the unrounded
        # array, and re-deriving from the rounded copy manufactures a residual
        # of ~5e-4 on the two PV scenarios.  Rebuild the array `capture` fed in.
        surplus = (
            golden.pv_surplus_for(len(prices), built["solar"])
            if name in golden.PV_SCENARIOS
            else None
        )
        export_price = opt.config.pv_export_price
        total = space + dhw

        c_total = energy_cost(prices, total, dt, surplus, export_price)
        c_space = energy_cost(prices, space, dt, surplus, export_price)

        a = abs(c_total - payload["predicted_cost"])
        b = abs(
            (payload["baseline_cost"]
             - payload["predicted_cost"]
             - payload["deferred_energy_cost"])
            - payload["predicted_savings"]
        )
        bc = payload["baseline_cost"]
        want_pct = (
            0.0
            if bc <= 0.01
            else float(np.clip(payload["predicted_savings"] / bc * 100.0, -100.0, 100.0))
        )
        c = abs(want_pct - payload["savings_percentage"])
        d = abs((c_total - c_space) - payload["dhw_heating_cost"])

        for key, val in (("A", a), ("B", b), ("C", c), ("D", d)):
            resid[key].append(val)
            if val > worst[key][1]:
                worst[key] = (name, val)
        if "flat" in name:
            flat_rows[name] = (a, b, c, d)
        n_done += 1
        print(f"# {name}: A={a:.3e} B={b:.3e} C={c:.3e} D={d:.3e}", flush=True)

    d2lib.result("scenarios", n_done)
    d2lib.result("perturb_arm", "1" if PERTURB else "0")
    tol = 1e-9
    viol = 0
    for key in "ABCD":
        m = max(resid[key]) if resid[key] else 0.0
        d2lib.result(f"max_resid_{key}", f"{m:.6e}", "currency")
        d2lib.result(f"worst_scenario_{key}", worst[key][0] or "none")
        viol += sum(1 for v in resid[key] if v > tol)
    d2lib.result("tolerance", f"{tol:.0e}", "currency")
    d2lib.result("violations", viol)
    for name, (a, b, c, dd) in flat_rows.items():
        d2lib.result(
            f"null_control_{name}", f"A={a:.3e} B={b:.3e} C={c:.3e} D={dd:.3e}"
        )
    d2lib.env_footer()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
