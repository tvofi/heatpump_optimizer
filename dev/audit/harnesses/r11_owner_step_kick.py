"""R11-OWNER-STEP-KICK (#3860): the first heating write after a hot-water leg, classified and replayed.

    PYTHONPATH=tests/hastub:custom_components:tests \\
        python3 dev/audit/harnesses/r11_owner_step_kick.py --synthetic [--seed S] [--n N] [--perturb K]

The design's harness (design/R11-OWNER-STEP-KICK 09fecb1b, section 4), its
replay core only. Leg R reads a bundle's own series of swap passes (inlet
rungs, lift, ceiling, planned level and band, the recorded first write); a
diagnostics download carries no such series (``pump_arbiter.diagnostics_view``
holds the step ledger, not the per-pass writes or inlets), so the bundle arm
is not built here and the replay runs over invented swap passes. Leg S, the
post-merge soak, is the owner's.

Each swap pass is drawn from the seed: the pump-loop return after the leg
(44-58 °C), the space inlet remembered before it (22-35 °C), a buffer rung
present on a third of the installs, a planned level inside a 1.5-5.5 kW band
and the ceiling ``FLOW_HEAT_C``. Its write is recomputed through the
arbiter's own ``_flow_target`` (``thermal_model.modulation_floor_flow_c`` ->
``flow_setpoint_for_level``), once with no settle ("before", main's write)
and once with the swap's settle ("after", ``flow_anchor.settled_inlet_c``).

Kick classes, of one pass's write: ``hot-inlet`` (at least the ceiling less
0.5 K, the return within the lift of the ceiling), ``other`` (at least that,
the return cool), ``none`` (the rest). An "after" pass whose level maps to
the ceiling from the space loop's own water as well is ``band-top`` (the
design's invariant I5: a level at the band top writes the ceiling), not a
kick; the pass criterion is ``after_hot-inlet=0``.

Printed: the class counts before and after over the passes inside the
settle span (``in_window``), ``i1_violations`` (after above before, every
pass) and ``i2_violations`` (a pass 300 s or more after the swap whose write
moved). ``--perturb K`` is the classifier's control: the first K
``none`` passes of "before" have their write raised to the ceiling and their
return set within the lift, and ``hot-inlet`` before must rise by exactly K.
"""
from __future__ import annotations

import argparse
import random
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from harness import FakeHass, FakeState

from heatpump_optimizer import flow_anchor, pump_arbiter
from heatpump_optimizer.const import CONF_BUFFER_TANK_TEMP_ENTITY, CONF_HEAT_PUMP_RETURN_TEMP_ENTITY
from heatpump_optimizer.thermal_model import FLOW_MIN_LIFT_K

T0 = datetime(2026, 1, 10, 6, 0, tzinfo=timezone.utc)
CEILING_C = pump_arbiter.FLOW_HEAT_C


def _inp(return_c: float | None, buffer_c: float | None, kw: float) -> SimpleNamespace:
    config = {"space_setpoint_entity": "number.flow", "space_setpoint_unit": "flow"}
    states = {"number.flow": FakeState("40", attributes={"min": 20, "max": 70})}
    if return_c is not None:
        config[CONF_HEAT_PUMP_RETURN_TEMP_ENTITY] = "sensor.ret"
        states["sensor.ret"] = FakeState(str(return_c), unit="°C")
    if buffer_c is not None:
        config[CONF_BUFFER_TANK_TEMP_ENTITY] = "sensor.buf"
        states["sensor.buf"] = FakeState(str(buffer_c), unit="°C")
    return SimpleNamespace(
        config=config, hass=FakeHass(states),
        state=SimpleNamespace(outdoor_temperature=0.0, buffer_tank_temperature=40.0, floor_return_temperature=None),
        thermal=SimpleNamespace(params=None), params=SimpleNamespace(min_electrical_power=1.5, max_electrical_power=5.5),
        plan=SimpleNamespace(timestamps=[T0], power_schedule=[kw]), action=None, measured_power_kw=None)


def classify(write_c: float, return_c: float) -> str:
    if write_c < CEILING_C - 0.5:
        return "none"
    return "hot-inlet" if return_c + FLOW_MIN_LIFT_K >= CEILING_C else "other"


def run(seed: int, n: int, perturb: int) -> dict[str, int]:
    rng = random.Random(seed)
    out = {f"{leg}_{c}": 0 for leg in ("before", "after") for c in ("hot-inlet", "other", "none")}
    out["after_band-top"] = 0
    out.update(i1_violations=0, i2_violations=0, passes=n, in_window=0, perturbed=0)
    for _ in range(n):
        return_c, space_c = rng.uniform(44.0, 58.0), rng.uniform(22.0, 35.0)
        buffer_c = rng.uniform(25.0, 40.0) if rng.random() < 1 / 3 else None
        kw, dt_s = rng.uniform(1.5, 5.5), rng.choice((0, 60, 120, 299, 300, 600))
        at = T0 + timedelta(seconds=dt_s)
        settle = flow_anchor.Settle(T0, space_c if rng.random() < 0.8 else None)
        before = pump_arbiter._flow_target(_inp(return_c, buffer_c, kw), "space", at)
        after = pump_arbiter._flow_target(_inp(return_c, buffer_c, kw), "space", at, settle=settle)
        out["i1_violations"] += after > before
        if dt_s >= 300:
            out["i2_violations"] += after != before
            continue
        out["in_window"] += 1
        cls_before = classify(before, return_c)
        if cls_before == "none" and out["perturbed"] < perturb:
            out["perturbed"] += 1
            cls_before = classify(CEILING_C, CEILING_C - FLOW_MIN_LIFT_K + 0.1)
        out[f"before_{cls_before}"] += 1
        cls_after = classify(after, return_c)
        if cls_after == "hot-inlet":
            # The level's own map from the space loop's water: at the band top it is the ceiling (I5).
            water = pump_arbiter._flow_target(_inp(settle.space_inlet_c, buffer_c, kw), "space", at)
            cls_after = "hot-inlet" if water < CEILING_C - 0.5 else "band-top"
        out[f"after_{cls_after}"] += 1
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", action="store_true", required=True)
    ap.add_argument("--seed", type=int, default=3860)
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--perturb", type=int, default=0)
    args = ap.parse_args()
    for key, value in run(args.seed, args.n, args.perturb).items():
        print(f"RESULT {key}={value}")


if __name__ == "__main__":
    main()
