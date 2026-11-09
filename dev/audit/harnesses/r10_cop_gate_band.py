#!/usr/bin/env python3
"""R10-COP-GATE-E (#3106): drawn power against the flow set-point between the duty gate and the ceiling.

Reads every recorded replay fixture under ``tests/replay/`` (format: each
``states[entity]`` a list of ``[last_changed, state, attrs, last_updated]``)
whose ``entry.options`` name a flow set-point and a power entity. A
set-point step counts when it lies strictly inside the band,
``pump_arbiter.FLOW_GATE_C + draw_range.GATE_TOLERANCE_K`` to the configured
ceiling (``thermal_model.configured_flow_heat_c`` on the entry's options) less ``draw_range.CEILING_TOLERANCE_K``,
and the mode entity reads space heat alone (``pump_mode.resolve`` is
``MODE_HEAT``) for the whole step: a combined or hot-water mode's draw is
not the space set-point's. Its draw is the last power reading inside the
step (the settled one), and a step with no reading is not counted.

Per fixture one ``RESULT`` line: ``steps`` (counted), ``distinct_c``
(distinct set-points among them) and, where ``distinct_c >= 3``, the fitted
``gain_kw_per_k`` (least squares) and ``max_resid_kw`` (the largest departure
from that line: linear where it is within the readings' own spread). Fewer
than three distinct set-points fit no line and its curvature: ``fit=none``.

    PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r10_cop_gate_band.py [--synthetic] [FIXTURE.json ...]

Each ``FIXTURE.json`` named is read beside the committed ones (an owner's
recording in the same format, kept out of the tree).

Null control: ``--synthetic`` adds a fixture made here, four in-band steps
drawing exactly ``0.1 kW/K`` above the gate, through the same pairing; it
must read ``distinct_c=4 gain_kw_per_k=0.1 max_resid_kw=0.0``, so a fixture
reading ``fit=none`` lacks the data rather than the instrument a fit.
"""
from __future__ import annotations

import glob
import json
import sys
from datetime import datetime, timedelta, timezone


def steps(data: dict) -> list[tuple[float, float]]:
    from heatpump_optimizer import draw_range, pump_arbiter, pump_mode
    from heatpump_optimizer.thermal_model import configured_flow_heat_c

    opts = data.get("entry", {}).get("options", {})
    sp_id, pw_id = opts.get("space_setpoint_entity"), opts.get("heat_pump_power_entity")
    mode_id = opts.get("heat_pump_mode_entity")
    if not sp_id or not pw_id or opts.get("space_setpoint_unit", "flow") != "flow":
        return []
    states = data["states"]
    lo = pump_arbiter.FLOW_GATE_C + draw_range.GATE_TOLERANCE_K
    hi = configured_flow_heat_c(opts) - draw_range.CEILING_TOLERANCE_K
    at = lambda row: datetime.fromisoformat(row[0])  # noqa: E731
    sps = [(at(r), float(r[1])) for r in states.get(sp_id, []) if _num(r[1])]
    pws = [(at(r), float(r[1])) for r in states.get(pw_id, []) if _num(r[1])]
    modes = [(at(r), pump_mode.resolve(r[1])) for r in states.get(mode_id, [])] if mode_id else []
    out = []
    for i, (start, sp) in enumerate(sps):
        end = sps[i + 1][0] if i + 1 < len(sps) else datetime.max.replace(tzinfo=timezone.utc)
        if not lo < sp < hi:
            continue
        held = [m for t, m in modes if t <= start][-1:] + [m for t, m in modes if start < t < end]
        if held != [pump_mode.MODE_HEAT] * len(held) or not held:
            continue
        inside = [kw for t, kw in pws if start <= t < end]
        if inside:
            out.append((sp, inside[-1]))
    return out


def _num(s: object) -> bool:
    try:
        float(s)  # type: ignore[arg-type]
        return True
    except (TypeError, ValueError):
        return False


def fit(points: list[tuple[float, float]]) -> str:
    xs = sorted({sp for sp, _ in points})
    if len(xs) < 3:
        return f"steps={len(points)} distinct_c={len(xs)} fit=none"
    n = len(points)
    mx = sum(p[0] for p in points) / n
    my = sum(p[1] for p in points) / n
    gain = sum((x - mx) * (y - my) for x, y in points) / sum((x - mx) ** 2 for x, _ in points)
    resid = max(abs(y - (my + gain * (x - mx))) for x, y in points)
    return f"steps={n} distinct_c={len(xs)} gain_kw_per_k={round(gain, 6)} max_resid_kw={round(resid, 6)}"


def synthetic() -> dict:
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    sp = [[(t0 + timedelta(hours=i)).isoformat(), str(c), None, None] for i, c in enumerate((30.0, 35.0, 40.0, 45.0))]
    pw = [[(t0 + timedelta(hours=i, minutes=20)).isoformat(), str(round(0.1 * (c - 25.0), 6)), None, None]
          for i, c in enumerate((30.0, 35.0, 40.0, 45.0))]
    return {"entry": {"options": {"space_setpoint_entity": "number.sp", "heat_pump_power_entity": "sensor.p",
                                  "heat_pump_mode_entity": "select.m", "space_setpoint_unit": "flow"}},
            "states": {"number.sp": sp, "sensor.p": pw, "select.m": [[t0.isoformat(), "Heating", None, None]]}}


def main() -> None:
    named = [a for a in sys.argv[1:] if not a.startswith("--")]
    fixtures = {path: json.load(open(path)) for path in sorted(glob.glob("tests/replay/*.json")) + named}
    if "--synthetic" in sys.argv[1:]:
        fixtures["synthetic-linear"] = synthetic()
    for name, data in fixtures.items():
        print(f"RESULT {name} {fit(steps(data))}")


if __name__ == "__main__":
    main()
