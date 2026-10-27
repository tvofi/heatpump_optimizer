#!/usr/bin/env python3
"""R10-SAV-COMFORT (#2492, carries 2 and 4): the month row's volume and timing terms.

WHY IT EXISTS. The D15 triage of the owner's diagnostics bundle found the
open month negative by volume, not by price timing: the booked thermostat is
a modelled kWh, the actual a metered one, and the plan's model under-read the
meter 1.56x. Pricing both sides at one price left the negative month whole.
The owner's specification (2026-10-24) is a thermostat at the power levels the
pump recorded, priced over the same profile, so that at one flat price the
timing term is 0 and only the volume difference may remain.

This harness settles a synthetic install through the production path
(``MonthlyLedger.observe_spot_and_settle_savings``, with the pending snapshot
the coordinator builds: ``baseline_kw``, ``power`` and ``grid_fee``) and reads
the row ``savings_months`` publishes, then splits it from
``ledger.months[<month>].lines``:

  volume  the mean price times the calibrated thermostat's kWh less the
          metered kWh (``meter_calibration``; 1 where the tree has none)
  timing  the row's saving less the volume term

The install: 96 one-hour intervals; the plan heats 2.0 kW on the even hours
(the cheap ones of the varying profile) and idles on the odd; the thermostat draws 1.0 kW flat (the plan's
modelled volume); the meter reads ``FACTOR`` times the plan's model. No bundle
data: every figure is the synthetic install's.

Arms:

  flat  one price: the saving must read about 0 (the thermostat's modelled
        volume is the plan's), SOUND below 0.01 per kWh metered; the modelled
        basis reads the model's under-read as a loss.
  vary  the cheap/dear profile: the timing term must survive, SOUND above 0.
  gap   the same varying month with the meter equal to the model: the row
        must be what the modelled basis books (prints both).

    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_volume.py [flat|vary|gap ...]
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta

from heatpump_optimizer.ledger import MonthlyLedger

FACTOR = 1.56
HOURS = 96
START = datetime(2026, 10, 1, 0, 0)
NOW = datetime(2026, 11, 2, 0, 0)


def month(prices: list[float], factor: float) -> tuple[dict, MonthlyLedger]:
    led = MonthlyLedger()
    for h in range(HOURS):
        plan_kw = 0.0 if h % 2 else 2.0
        led.observe_spot_and_settle_savings(
            START + timedelta(hours=h), prices[h],
            {"baseline_kw": 1.0, "power": plan_kw, "grid_fee": 0.2},
            factor * plan_kw, 1.0,
        )
        # The bill's energy lines, as the coordinator books them beside.
        led.add(START + timedelta(hours=h), "spot", kwh=factor * plan_kw, sek=factor * plan_kw * prices[h])
        led.add(START + timedelta(hours=h), "grid_fee", kwh=factor * plan_kw, sek=factor * plan_kw * 0.2)
    return led.savings_months(NOW)[0], led


def terms(row: dict, led: MonthlyLedger, prices: list[float]) -> tuple[float, float]:
    key = row["month"]
    cal = getattr(led, "meter_calibration", lambda _k: None)(key)
    base_kwh = led.line(key, "savings_baseline")["kwh"] * (1.0 if cal is None else cal)
    act_kwh = led.line(key, "savings_actual")["kwh"]
    mean = sum(p + 0.2 for p in prices) / len(prices)
    volume = mean * (base_kwh - act_kwh)
    return volume, row["savings_sek"] - volume


def report(arm: str, prices: list[float], factor: float) -> tuple[dict, float, float]:
    row, led = month(prices, factor)
    volume, timing = terms(row, led, prices)
    print(f"{arm}: row {row}")
    print(f"{arm}: volume {volume:+.2f}  timing {timing:+.2f}  "
          f"metered {led.line(row['month'], 'savings_actual')['kwh']:.1f} kWh")
    return row, volume, timing


def main(arms: list[str]) -> int:
    flat, vary = [1.0] * HOURS, [1.5 if h % 2 else 0.5 for h in range(HOURS)]
    for arm in arms:
        if arm == "flat":
            row, _v, timing = report(arm, flat, FACTOR)
            per_kwh = abs(row["savings_sek"]) / (FACTOR * 2.0 * HOURS)
            verdict = "SOUND" if per_kwh < 0.01 and abs(timing) < 0.01 else "DEFECT"
            print(f"flat: {verdict}: |saving| {per_kwh:.4f} per metered kWh at one price")
        elif arm == "vary":
            _row, _v, timing = report(arm, vary, FACTOR)
            print(f"vary: {'SOUND' if timing > 0.0 else 'DEFECT'}: the timing term {timing:+.2f}")
        elif arm == "gap":
            report(arm, vary, 1.0)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["flat", "vary", "gap"]))
