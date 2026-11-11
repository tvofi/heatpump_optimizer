#!/usr/bin/env python3
"""R10-COP-GATE (#2262): COP observability on an install without a heat meter.

Companion to the finder's ``dev/audit/rounds/round10/study-ident/owner_rows.py``
(fixer.md step 3): that harness reads the gate pass shares, which this fix
leaves alone; this one applies the tree's own rule to the same inputs and reads
what the fix changes.

Two arms, both through the production symbols:

  * ``owner`` (needs the PRIVATE bundle path; derived ratios only): the
    accuracy store's metered rows feed ``draw_range.DrawRange`` as the
    finder's harness does (``is_running_space``, the owner's configured
    range), ``follows_ask`` judges that window, and
    ``accuracy.MeasuredCop.judge_ratio`` replays each row past the duty
    floor against it. ``folds_within_tolerance`` is the count of rows that
    fold within ``COP_ASK_TOLERANCE`` of the ask while the window says the
    draw does not follow it (the defect: nonzero at the base, 0 at the head).
  * ``synthetic`` (no bundle): a 14 kW / 1.0 kW install whose draw is 2.2 kW
    whatever it is asked (``selfset``, a flow set-point's shape), and its null
    control whose draw is 1.3 x the ask (``follows``); 12 intervals asked
    2.1 kW drawn 2.2 kW (inside the tolerance) through the coordinator's
    ``_learn_measured_cop``. ``selfset`` folds 12 at the base, 0 at the head;
    ``follows`` folds 12 at both ends.

``observability`` is ``accuracy.cop_observability`` on the arm's meters, or
``absent`` where the tree has no such state (the base).

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_cop_gate.py [BUNDLE.json]

Perturbation: ``--slope-follow`` replaces the owner's draws with 1.3 x the ask;
``follows_ask`` must turn True and ``folds_within_tolerance`` must stay 0
(nothing departs), while the folds count rises (direction: up).
Null control: the ``follows`` synthetic arm folds every interval at both ends.
"""
from __future__ import annotations

import argparse
import json
import sys

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

from heatpump_optimizer import accuracy, draw_range  # noqa: E402
from heatpump_optimizer.accuracy import COP_ASK_TOLERANCE, MeasuredCop  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

CFG = {
    "tibber_token": "x", "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
    "heat_pump_power_entity": "sensor.pump_power",
    "heat_pump_max_power": 14.0, "heat_pump_min_power": 1.0,
}
STATES = {
    "sensor.indoor": FakeState("21.0", unit="°C"),
    "sensor.outdoor": FakeState("8.0", unit="°C"),
    "sensor.pump_power": FakeState("2200", unit="W"),
}


def observability(electric: bool, heat: bool, follows: bool | None) -> str:
    rule = getattr(accuracy, "cop_observability", None)
    return "absent" if rule is None else rule(electric=electric, measured_heat=heat, follows=follows)


def synthetic(shape: str) -> tuple[int, str | None, str]:
    coord = HeatPumpOptimizerCoordinator(FakeHass(dict(STATES)), FakeEntry(data=dict(CFG)))
    window = draw_range.DrawRange()
    for i in range(96):
        ask = (1.2, 1.6, 2.0, 2.4)[i % 4]
        window.observe(2.2 if shape == "selfset" else 1.3 * ask, ask, 1.0, 14.0)
    coord._accuracy.draw = window
    coord._cop_ratio_ewma = 1.0
    for _ in range(12):
        coord._current_action = {"power": 2.1, "dhw_power": 0.0}
        coord._measured_power = 2.2
        coord._current_state.outdoor_temperature = 8.0
        coord._learn_measured_cop(coord._accuracy.draw)
    return coord._cop_samples, coord._measured_cop.refusal, observability(True, False, draw_range.follows_ask(window))


def owner(path: str, slope_follow: bool) -> None:
    data = json.load(open(path))["data"]
    cfg = dict(data["config"])
    stores = data["debug"]["stores"]
    rows = []
    for s in stores[next(k for k in stores if k.endswith("_accuracy"))]["accuracy"]["samples"]:
        ask, drawn = s.get("predicted_power_kw"), s.get("actual_power_kw")
        if ask is None or drawn is None:
            continue
        rows.append((float(ask), 1.3 * float(ask) if slope_follow else float(drawn)))
    p = ThermalParameters.from_config(cfg)
    window = draw_range.DrawRange()
    for ask, drawn in rows:
        if draw_range.is_running_space(drawn, ask, 0.0, frozen=False, distorted=False, defrost=False):
            window.observe(drawn, ask, p.min_electrical_power, p.max_electrical_power)
    follows = draw_range.follows_ask(window)
    folds = within = 0
    ewma = 1.0
    for ask, drawn in rows:
        if ask <= 0.0 or MeasuredCop.judge_floor(ask, drawn, p) is not None:
            continue
        ratio = drawn / max(ask, 1e-6)
        prev, ewma = ewma, 0.9 * ewma + 0.1 * ratio
        if MeasuredCop.judge_ratio(ratio, prev, ask, p, window) is None:
            folds += 1
            within += int(abs(ratio - 1.0) <= COP_ASK_TOLERANCE)
    heat = bool(cfg.get("heat_pump_heat_energy_entity") or cfg.get("heat_pump_thermal_power_entity"))
    print(f"RESULT owner.rows={len(rows)} running_pairs={len(window.samples)} follows_ask={follows}")
    print(f"RESULT owner.folds={folds} folds_within_tolerance={within}")
    print(f"RESULT owner.heat_metered={heat} observability={observability(bool(cfg.get('heat_pump_power_entity')), heat, follows)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle", nargs="?")
    ap.add_argument("--slope-follow", action="store_true")
    a = ap.parse_args()
    for shape in ("selfset", "follows"):
        n, why, obs = synthetic(shape)
        print(f"RESULT synthetic.{shape}.folded={n}/12 refusal={why} observability={obs}")
    if a.bundle:
        owner(a.bundle, a.slope_follow)


if __name__ == "__main__":
    main()
