#!/usr/bin/env python3
"""R10-SAV-COMFORT part 3: the flat-price null through the settled month row.

WHY IT EXISTS. ``r10_sav_baseline.py null`` reads the month row's saving at a
flat price with the plant equal to the model; ``r10_sav_null_terms.py`` splits
its residual into comfort, COP timing and stored heat. The owner's ruling
(2026-11-04) settles stored heat in the month row, keeps the start-independent
thermostat, and reports the comfort-matched null beside it. This harness
replays the same closed loop and books every interval exactly as the
coordinator's pending snapshot does since that ruling: ``baseline_kw`` plus the
plan's ``SETTLEMENT_KEYS`` for the step (``get_current_action``),
through ``MonthlyLedger.observe_spot_and_settle_savings``.

Arms:

  vary   the ``winter_cold`` outdoor series: the comfort-matched saving reads
         the COP-timing term, which is real at a flat price and must not be 0.
  const  outdoor held at the window's mean, so timing is 0 by construction:
         the comfort-matched saving reads about 0 (``|pct| < 3.0``, the
         owner's bar), with stored heat settled at both ends.

Per arm it prints the row (saving, ``stored_heat_sek``, ``comfort_sek``), the
comfort-matched saving and percentage, and the same loop's row with the two
new readings withheld (the pre-ruling row) as the control.

    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_null_settled.py [vary|const ...]
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta

import numpy as np

sys.path.insert(0, "dev/audit/harnesses")
import r10_sav_baseline as h  # noqa: E402
from profiles import DT, prices, solve_inputs, weather  # noqa: E402
from heatpump_optimizer.ledger import SETTLEMENT_KEYS, MonthlyLedger  # noqa: E402
from heatpump_optimizer.thermal_model import WeatherSeries  # noqa: E402

BAR_PCT = 3.0


def run(const: bool, days: int = 2, replan: int = 4) -> tuple[dict, dict]:
    opt, model, _ = h._optimizer()
    total = int(days * 24 / DT)
    span = total + int(24 / DT) + 4

    def tile(a):
        a = np.asarray(a, dtype=float)
        return np.tile(a, int(np.ceil(span / len(a))))[:span]

    pr = tile(prices("flat", h.START))
    out, wind, rain, sol = (tile(a) for a in weather("winter_cold", h.START))
    if const:
        out = np.full_like(out, float(np.mean(out[:total])))
    hs = int(24 / DT)
    state = h._state(21.0, 22.0, float(out[0]))
    settled, unsettled = MonthlyLedger(), MonthlyLedger()
    plan = None
    for k in range(total):
        now = h.START + timedelta(hours=k * DT)
        if k % replan == 0:
            plan = opt.optimize(inputs=solve_inputs(
                initial_state=state, prices=pr[k:k + hs], outdoor_temps=out[k:k + hs],
                wind_speeds=wind[k:k + hs], precipitation=rain[k:k + hs],
                solar_radiation=sol[k:k + hs], start_time=now,
            ))
        action = opt.get_current_action(plan, now)
        power = float(plan.power_schedule[k % replan])
        pending = {key: action.get(key) for key in SETTLEMENT_KEYS}
        settled.observe_spot_and_settle_savings(now, float(pr[k]), pending, power * DT, DT)
        unsettled.observe_spot_and_settle_savings(
            now, float(pr[k]), {"baseline_kw": pending["baseline_kw"]}, power * DT, DT,
        )
        room, slab, up, lo, *_ = model.simulate_trajectory(
            initial_state=state, power_schedule=np.array([power]),
            weather=WeatherSeries(outdoor_temps=out[k:k + 1], wind_speeds=wind[k:k + 1],
                                  precipitation=rain[k:k + 1], solar_radiation=sol[k:k + 1]),
            dt_hours=DT,
        )
        state = h._state(float(room[-1]), float(slab[-1]), float(out[k]))
        state.upper_floor_temperature = float(up[-1])
        state.lower_floor_temperature = float(lo[-1])
    when = datetime(2026, 2, 1, 0, 0)
    return settled.savings_months(when)[0], unsettled.savings_months(when)[0]


def arm(name: str) -> bool:
    row, control = run(const=name == "const")
    matched = row["savings_sek"] - row["comfort_sek"]
    pct = 100.0 * matched / row["baseline_sek"] if row["baseline_sek"] else float("nan")
    print(f"{name}: control (no stored/comfort readings): baseline {control['baseline_sek']} "
          f"actual {control['actual_sek']} saved {control['savings_sek']} ({control['savings_pct']:.2f} %)")
    print(f"{name}: settled row: baseline {row['baseline_sek']} actual {row['actual_sek']} "
          f"saved {row['savings_sek']} ({row['savings_pct']:.2f} %) stored_heat_sek {row['stored_heat_sek']} "
          f"comfort_sek {row['comfort_sek']}")
    print(f"{name}: comfort-matched saving {matched:.2f} ({pct:+.2f} % of the settled baseline)")
    if name == "const":
        return abs(pct) < BAR_PCT
    return pct >= BAR_PCT


def main(argv: list[str]) -> int:
    names = argv or ["vary", "const"]
    failed = [n for n in names if not arm(n)]
    for n in names:
        print(f"{n}: {'DEFECT' if n in failed else 'SOUND'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
