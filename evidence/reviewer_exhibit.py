#!/usr/bin/env python3
"""REVIEWER'S OWN instrument (not the finder's, not the fixer's).

Attacks the rule the fix asks to be attacked first: "a channel the plan was
running keeps its reason at ANY meter magnitude" (ledger.explain_metered).

    python3 reviewer_exhibit.py --worktree <path>

One meter, two circuits. The plan runs SPACE at 1.0 kW (reason cheap_price)
and draws NOTHING on DHW (reason idle) -- the classification which the fix
itself says must book untagged. The meter samples the WHOLE unit at 3.0 kW
for 1.0 h. _accumulate_energy apportions the unit's energy by the PLAN's
split (dhw_share = planned_dhw / planned_total = 0), so the whole 3.0 kWh is
handed to explain_metered as the SPACE share and books cheap_price. A draw on
a channel whose reason says the plan drew nothing is labelled with another
channel's plan reason: the same phenomenon as #2256, one seam on.

Prints the reason lines at whichever tree it is pointed at.
"""
from __future__ import annotations
import argparse, os, sys
from datetime import datetime, timezone
from pathlib import Path

UTC = timezone.utc
WHEN = datetime(2026, 3, 28, 12, 0, tzinfo=UTC)
METER = {"sensor.indoor": ("21.0", "°C"), "sensor.outdoor": ("-5.0", "°C")}
CONFIG = {"tibber_token": "x", "weather_entity": "weather.home",
          "indoor_temp_entity": "sensor.indoor",
          "outdoor_temp_entity": "sensor.outdoor"}


def _import(worktree: Path):
    os.chdir(worktree)
    for p in (worktree / "tests", worktree / "tests" / "hastub",
              worktree / "custom_components"):
        sys.path.insert(0, str(p))
    from harness import FakeEntry, FakeHass, FakeState
    from heatpump_optimizer.accuracy import AccuracySample
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    loaded = Path(sys.modules[HeatPumpOptimizerCoordinator.__module__].__file__).resolve()
    if worktree not in loaded.parents:
        raise SystemExit(f"asked for {worktree}, imported {loaded}")
    return FakeEntry, FakeHass, FakeState, AccuracySample, HeatPumpOptimizerCoordinator


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worktree", required=True, type=Path)
    w = ap.parse_args().worktree.resolve()
    FakeEntry, FakeHass, FakeState, AccuracySample, Coord = _import(w)
    states = {k: FakeState(v, unit=u) for k, (v, u) in METER.items()}
    c = Coord(FakeHass(dict(states)), FakeEntry(data=dict(CONFIG)))
    c._thermal_params.dhw_enabled = True
    c._accumulate_energy(
        AccuracySample(when=WHEN, actual_power_kw=3.0),
        1.0,
        {"price": 2.0, "spot_price": 2.0, "grid_fee": 0.0,
         "space_power": 1.0, "dhw_power": 0.0,
         "space_reason": "cheap_price", "dhw_reason": "idle", "when": WHEN},
    )
    m = "2026-03"
    names = ["spot", "space", "dhw", "reason:cheap_price", "reason:idle",
             "reason:untagged"]
    print("PLAN  space 1.0 kW (cheap_price)  dhw 0.0 kW (idle)   "
          "METER 3.0 kW for 1.0 h")
    for n in names:
        try:
            print(f"  {n:<22} {round(c._ledger.line(m, n)['kwh'], 6)} kWh")
        except KeyError:
            print(f"  {n:<22} (no line)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
