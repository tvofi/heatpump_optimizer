#!/usr/bin/env python3
"""R10-SAV-REASONS: what a settled cost is attributed to (#2256).

The owner's report (savings items 3 and 4): "Not heating" was the costliest
attribution category, and boost costs landed in "untagged". Two measurements
read the seam this group owns — reason tagging at booking and at
classification — and they are run the same way against either end of the fix:

    python3 dev/audit/harnesses/sav_reasons_booking.py --worktree <path>

1. BOOKING. The plan commanded nothing at the step (space 0, DHW 0, reason
   ``idle``) and the meter read 0.4 kW over the hour. The print is the
   interval's ledger lines. Before the fix the whole draw books
   ``reason:idle``; after it, ``reason:untagged`` (outside the plan) carries
   it and ``reason:idle`` is empty.
2. CLASSIFICATION. A space-channel boost is laid over a plan step the plan
   had idle. The print is the running action's ``power`` and its two reason
   fields. Before the fix the boosted channel keeps ``idle``; after it, the
   boosted channel reads ``boost`` and the untouched channel keeps ``idle``.

It reads the tree it is pointed at by putting that worktree's ``tests``,
``tests/hastub`` and ``custom_components`` first on ``sys.path``, so the two
ends are measured with their own modules. Pure measurement: it always exits 0
and asserts nothing, so a red is read off the printed lines, not a traceback.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

UTC = timezone.utc
WHEN = datetime(2026, 3, 28, 12, 0, tzinfo=UTC)
METER = {
    "sensor.indoor": ("21.0", "°C"),
    "sensor.outdoor": ("-5.0", "°C"),
}
CONFIG = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
}


def _import(worktree: Path):
    """The worktree's own modules, ahead of whatever this process imported.

    ``tests/harness.py`` prepends the RELATIVE ``tests`` and
    ``custom_components`` on import, which resolve against the process cwd —
    run from another checkout's root, that silently measures the other tree
    (measured: a head run reproduced the baseline's lines). Chdir first, so
    both its insertions and this function's absolute ones name ``worktree``,
    and refuse loudly if the tree actually loaded is not the one asked for.
    """
    os.chdir(worktree)
    for path in (worktree / "tests", worktree / "tests" / "hastub",
                 worktree / "custom_components"):
        sys.path.insert(0, str(path))
    from harness import FakeEntry, FakeHass, FakeState
    from heatpump_optimizer import boost
    from heatpump_optimizer.accuracy import AccuracySample
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    loaded = Path(sys.modules[HeatPumpOptimizerCoordinator.__module__].__file__).resolve()
    if worktree not in loaded.parents:
        raise SystemExit(f"asked for {worktree}, imported {loaded}")
    return FakeEntry, FakeHass, FakeState, boost, AccuracySample, HeatPumpOptimizerCoordinator


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worktree", required=True, type=Path)
    args = parser.parse_args()
    worktree = args.worktree.resolve()

    FakeEntry, FakeHass, FakeState, boost, AccuracySample, Coord = _import(worktree)
    states = {k: FakeState(v, unit=u) for k, (v, u) in METER.items()}

    def coord():
        c = Coord(FakeHass(dict(states)), FakeEntry(data=dict(CONFIG)))
        c._thermal_params.dhw_enabled = True
        return c

    # 1. booking: a plan that commanded nothing, a meter that drew.
    c = coord()
    c._accumulate_energy(
        AccuracySample(when=WHEN, actual_power_kw=0.4),
        1.0,
        {
            "price": 2.0, "spot_price": 1.5, "grid_fee": 0.0,
            "space_power": 0.0, "dhw_power": 0.0,
            "space_reason": "idle", "dhw_reason": "idle",
            "when": WHEN,
        },
    )
    month = "2026-03"
    lines = {
        name: round(c._ledger.line(month, name)["kwh"], 6)
        for name in ("spot", "reason:idle", "reason:untagged")
    }
    print("BOOKING plan commanded 0.0 kW, meter read 0.4 kW for 1 h")
    for name, kwh in lines.items():
        print(f"  {name:<18} {kwh} kWh")

    # 2. classification: a space boost over an idle plan step.
    c = coord()
    base = {
        "power": 0.0, "dhw_power": 0.0, "heat_pump_on": False, "mode": "off",
        "space_reason": "idle", "dhw_reason": "idle",
    }
    boost.adopt_plan(c, dict(base))
    boost.held_for(c).set(boost.CHANNEL_SPACE, True, datetime.now(UTC))
    boost.apply(
        c, boost.BoostOverlay(max_power=9.0, max_temp=24.0, ecl_max=4.0)
    )
    action = c._current_action
    print("CLASSIFICATION space boost over a plan-idle step")
    for key in ("power", "space_reason", "dhw_reason", "boost_space"):
        print(f"  {key:<14} {action.get(key)!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
