#!/usr/bin/env python3
"""R10-DRAW-MAP-EVIDENCE part A: the set-point-to-draw map fitted from the steady-run map rows.

The rows are ``draw_range.MapRows``'s, built here the way production builds
them: one ``draw_range.PassRecord`` a minute through ``MapRows.take_pass``,
committed by ``MapRows.commit_runs``, stored by ``DrawRange.as_dict`` and read
back by ``DrawRange.from_dict`` before the fit. The fit is least squares of a
row's drawn mean on its lift, written set-point less inlet mean:
``drawn = offset_kw + gain_kw_per_k * lift``.

    PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/draw_map_rows.py --synthetic
    PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/draw_map_rows.py --bundle BUNDLE.json

``--synthetic`` prints four ``RESULT`` lines on a planted plant (gain 0.3
kW/K, offset 0.4 kW, inlets 30 to 40 °C, five held set-points each):

* ``open_loop``: the rows of held set-points recover the planted gain and
  offset;
* ``shuffled`` (null): the same rows with their set-points permuted fall to a
  flat fit -- the recovery is the rows' pairing, not the fit;
* ``closed_loop`` (null): rows whose set-point a loop moved while the draw sat
  on the plan's level give a slope far from the planted one -- why the origin
  column must separate them;
* ``store``: the stored bytes of the rows at ``MAP_ROWS`` (compact JSON, as
  Home Assistant's store writes), and those bytes times the 48 saves a day
  of the default cycle (the accuracy store saves every cycle).

``--bundle`` reads a diagnostics download (``data.debug.stores``, the
accuracy store's ``draw`` record) and prints its rows by origin, the fit on
the open-loop ones (``fit=none`` under three distinct set-points), and the
accuracy store's own compact bytes. A bundle from before the rows reads
``rows=0``. Counts only: no row is printed.
"""
from __future__ import annotations

import json
import random
import sys
from datetime import datetime, timedelta, timezone

from heatpump_optimizer import draw_range as dr

#: Origins whose write no loop moved against the draw: the map's evidence.
OPEN_LOOP = ("plan", "fit", "probe", "boost")
GAIN, OFFSET = 0.3, 0.4
T0 = datetime(2026, 1, 12, 0, 0, tzinfo=timezone.utc)
SAVES_PER_DAY = 48


def fit(rows: list[tuple]) -> tuple[float, float, int] | None:
    """``(gain, offset, distinct set-points)`` or ``None`` under three."""
    pts = [(r[2] - r[10], r[13]) for r in rows if r[10] is not None and r[13] is not None]
    if len({r[2] for r in rows}) < 3 or len(pts) < 3:
        return None
    n = len(pts)
    mx, my = sum(x for x, _ in pts) / n, sum(y for _, y in pts) / n
    sxx = sum((x - mx) ** 2 for x, _ in pts)
    if sxx <= 0.0:
        return None
    gain = sum((x - mx) * (y - my) for x, y in pts) / sxx
    return gain, my - gain * mx, len({r[2] for r in rows})


def _runs(closed_loop: bool, seed: int = 3) -> dr.DrawRange:
    rng = random.Random(seed)
    draw = dr.DrawRange()
    minute = 0
    for inlet0 in (30.0, 32.5, 35.0, 37.5, 40.0):
        for lift in (1.0, 2.0, 3.0, 4.5, 6.0):
            level = OFFSET + GAIN * lift
            # A closed loop holds the plan's draw and walks the set-point,
            # held for 6-minute stretches the run rule can keep.
            walk = [round(inlet0 + 3.0 + rng.uniform(-2.0, 2.0), 1) for _ in range(4)]
            for m in range(24 if closed_loop else 20):
                inlet = inlet0 + 0.02 * m
                if closed_loop:
                    written, origin = walk[m // 6], "feedback"
                    drawn = 1.3 + rng.uniform(-0.03, 0.03)
                else:
                    written, origin = inlet0 + lift, "plan"
                    drawn = OFFSET + GAIN * (written - inlet) + rng.uniform(-0.03, 0.03)
                draw.map.take_pass(dr.PassRecord(
                    T0 + timedelta(minutes=minute), written, 25.0, 45.0, inlet0 + 0.5, level,
                    0.5, 4.0, 45.0, inlet, drawn, 4.0, "space", "heat", False, origin))
                minute += 1
            draw.map.take_pass(None)
            minute += 5
    draw.map.commit_runs(True)
    return dr.DrawRange.from_dict(json.loads(json.dumps(draw.as_dict())))


def _line(label: str, rows: list[tuple]) -> str:
    got = fit(rows)
    if got is None:
        return f"RESULT {label} rows={len(rows)} fit=none"
    gain, offset, distinct = got
    return f"RESULT {label} rows={len(rows)} distinct_c={distinct} gain_kw_per_k={gain:.3f} offset_kw={offset:.3f}"


def synthetic() -> None:
    rows = list(_runs(False).map.rows)
    print(_line("open_loop", rows) + f" planted_gain={GAIN} planted_offset={OFFSET}")
    written = [r[2] for r in rows]
    random.Random(5).shuffle(written)
    print(_line("shuffled", [(r[0], r[1], w) + r[3:] for r, w in zip(rows, written)]))
    print(_line("closed_loop", list(_runs(True).map.rows)))
    full = dr.DrawRange()
    template = rows[0]
    full.map.rows.extend((template[0] + 30 * i,) + template[1:] for i in range(dr.MAP_ROWS))
    empty = json.dumps(dr.DrawRange().as_dict(), separators=(",", ":"))
    capped = json.dumps(full.as_dict(), separators=(",", ":"))
    added = len(capped) - len(empty)
    print(f"RESULT store rows={len(full.map.rows)} draw_record_bytes_empty={len(empty)} "
          f"draw_record_bytes_capped={len(capped)} added_bytes={added} added_bytes_per_day={added * SAVES_PER_DAY}")


def bundle(path: str) -> None:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    stores = (((data.get("data") or {}).get("debug") or {}).get("stores")) or {}
    acc = next((v for k, v in stores.items() if k.endswith("_accuracy") and isinstance(v, dict)), None)
    if acc is None:
        print("RESULT bundle accuracy_store=absent")
        return
    draw = dr.DrawRange.from_dict((acc.get("accuracy") or {}).get("draw") or {})
    rows = list(draw.map.rows)
    origins: dict[str, int] = {}
    for r in rows:
        origins[r[15]] = origins.get(r[15], 0) + 1
    size = len(json.dumps(acc, separators=(",", ":")))
    print(f"RESULT bundle accuracy_store_bytes={size} bytes_per_day={size * SAVES_PER_DAY} "
          f"origins={dict(sorted(origins.items()))}")
    print(_line("bundle_open_loop", [r for r in rows if r[15] in OPEN_LOOP]))


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--synthetic"]:
        synthetic()
    elif args[:1] == ["--bundle"] and len(args) == 2:
        bundle(args[1])
    else:
        print(__doc__)
        sys.exit(2)
