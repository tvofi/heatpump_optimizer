"""D2.M3 terminal-credit: the objective's terminal cost against a re-simulated
continuation, every golden.

For each golden the plan's own end state E (the state the solve settles,
HeatPumpOptimizer._settle_horizon's optimized_end) is priced by the production
terminal-cost closure (HeatPumpOptimizer._terminal_cost) as T(E). E* is E with
every store the closure credits raised to its settlement cap
(HeatPumpOptimizer._settlement_caps), so T(E*) = 0. The continuation is the
same golden window solved again by the production optimizer from E and from E*.

Metric definitions (one line each):
  sign      : T(E) >= 0, T(E*) == 0, and dJ >= -0.05 when T(E) > 0
  r_C       = T(E) / dC   spend = predicted_cost of the continuation (currency)
  r_J       = T(E) / dJ   dJ = objective_value(E) - objective_value(E*) (the
              continuation's whole objective, comfort included)
A cell fails when the sign identity fails or |T(E) - dJ| > max(0.5*|dJ|, 0.1 currency).
Count key: T from the production closure, dC/dJ from production re-solves.

Run:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D2/s3/m3_terminal.py [--only NAME]
      --perturb-refill2 doubles optimizer._REFILL_PRICE_QUANTILE's price by
      patching optimizer._refill_price (x2): every r must go up.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine B6 (shared).
"""
import _common  # noqa: F401
from _common import footer, golden_names, solve_golden, np

import argparse
import copy


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--perturb-refill2", action="store_true")
    a = ap.parse_args()
    import golden  # noqa: F401
    from heatpump_optimizer import optimizer as om
    if a.perturb_refill2:
        orig = om._refill_price
        om._refill_price = lambda prices: 2.0 * orig(prices)

    names = [a.only] if a.only else golden_names()
    fails, rows, over_credit = 0, [], []
    for name in names:
        rec = solve_golden(name)
        opt, res = rec["opt"], rec["result"]
        h = rec["horizons"][-1][0]
        E = copy.copy(rec["settle"][-1][1])
        tc = opt._terminal_cost(h.prices, h.outdoor_temps, h.solar_gains, h.humidity)[0]

        def T(s):
            return float(tc(np.array([s.room_temperature]), np.array([s.slab_temperature]),
                            np.array([s.upper_floor_temperature]), np.array([s.lower_floor_temperature]),
                            np.array([s.buffer_tank_temperature])))
        caps = opt._settlement_caps(h.outdoor_temps, humidity=h.humidity)
        p = opt.model.params
        Es = copy.copy(E)
        Es.slab_temperature = max(E.slab_temperature, caps["slab"])
        if p.two_zone_enabled:
            Es.upper_floor_temperature = max(E.upper_floor_temperature, caps["room"])
            Es.lower_floor_temperature = max(E.lower_floor_temperature, caps["room"])
        else:
            Es.room_temperature = max(E.room_temperature, caps["room"])
        if p.buffer_is_store:
            Es.buffer_tank_temperature = max(E.buffer_tank_temperature, caps["buffer"])
        tE, tEs = T(E), T(Es)
        cE = solve_golden(name, state=copy.copy(E), keep=False)["result"]
        cEs = solve_golden(name, state=copy.copy(Es), keep=False)["result"]
        dC = cE.predicted_cost - cEs.predicted_cost
        dJ = cE.objective_value - cEs.objective_value
        sign_ok = tE >= 0 and abs(tEs) < 1e-12 and (tE <= 1e-9 or dJ >= -0.05)
        rC = tE / dC if abs(dC) > 1e-6 else float("nan")
        rJ = tE / dJ if abs(dJ) > 1e-6 else float("nan")
        bad = (not sign_ok) or abs(tE - dJ) > max(0.5 * abs(dJ), 0.1)
        fails += bad
        if tE > 0.05 and np.isfinite(rJ):
            rows.append((name, rJ, rC))
        over_credit.append(tE - dJ)
        print(f"CELL terminal-credit golden={name} T_E={tE:.4f} T_Estar={tEs:.2e} dC={dC:.4f} dJ={dJ:.4f} "
              f"r_C={rC:.3f} r_J={rJ:.3f} deficit_K slab={Es.slab_temperature - E.slab_temperature:.2f} "
              f"room={(Es.upper_floor_temperature - E.upper_floor_temperature) if p.two_zone_enabled else (Es.room_temperature - E.room_temperature):.2f} "
              f"buffer={Es.buffer_tank_temperature - E.buffer_tank_temperature:.2f} {'FAIL' if bad else 'OK'}", flush=True)
    print(f"RESULT terminal_failures={fails} count")
    print(f"RESULT cells={len(names)} count")
    print(f"RESULT over_credit_max={max(over_credit):.4f} currency")
    if rows:
        rj = np.array([r[1] for r in rows])
        print(f"RESULT r_J_median={np.median(rj):.3f} ratio")
        print(f"RESULT r_J_min={rj.min():.3f} ratio")
        print(f"RESULT r_J_max={rj.max():.3f} ratio")
        print(f"RESULT r_J_cells={len(rj)} count")
    footer()


if __name__ == "__main__":
    main()
