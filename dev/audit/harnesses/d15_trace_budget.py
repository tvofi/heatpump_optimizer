#!/usr/bin/env python3
"""R10-DRAW-MAP-EVIDENCE part F: the minute trace's bytes, and the debug store's writes.

``--bundle B`` (a whole "Download diagnostics" file) prices a full 168 h
download at indent 2, as ``debugger.download_bytes`` writes it, against
``INLINE_CAP_BYTES`` less ``DOWNLOAD_HEADROOM_BYTES``: the bundle's own
sections with ``cycle_rows`` scaled to 168 h and the snapshots to seven; the
trace encoded by the collector's own functions (``dbg_bundle_gen.trace_blocks``)
from the replay half's minutes, its 24 h block repeated for seven days; the
arbiter's pass record bounded by ``ARBITER_COLUMNS`` copies of the densest
input columns (no release publishes one yet); part A's map rows as column
strings of synthetic values. Prints byte counts only, never a value.

``--writes`` drives a ``DebugCollector`` through a synthetic week (a cycle
every 30 min, a trace sample every minute over ``--columns`` inputs, each
changing in ``--change`` of its minutes) and prints the bytes its hourly saves
write per day, with the debug option on and off; ``--columns 0`` is the ring
without a trace.

    PYTHONPATH=tests/hastub:tests:custom_components:tools/replay \\
        python3 -I dev/audit/harnesses/d15_trace_budget.py --bundle B
    PYTHONPATH=tests/hastub:tests:custom_components:tools/replay \\
        python3 dev/audit/harnesses/d15_trace_budget.py --writes

``--replay-null B`` (a ``dbg_bundle_gen.py`` bundle) is the trace's null control:
the agreement offenders over ``debug_replay.offender_window`` from the replay
half and from ``debug_replay.trace_document`` must be equal, and the
perturbation (the hot-water column held at ``PERTURB_DHW_C``) must move them.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import random
import sys
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for _p in ("tests/hastub", "tests", "custom_components", "tools/replay"):
    if str(ROOT / _p) not in sys.path:
        sys.path.insert(0, str(ROOT / _p))

from heatpump_optimizer import debugger  # noqa: E402

ARBITER_COLUMNS = 13  # the design's pass-record fields (part A)
MAP_ROWS, MAP_FIELDS = 1008, 17
COLUMNS = 27  # the owner bundle's mapped inputs (design P3)
PERTURB_DHW_C = "20"


def _indent(section: str, value: object) -> int:
    return len(json.dumps({"data": {"debug": {section: value}}}, indent=2).encode())


def budget(path: Path) -> None:
    import dbg_bundle_gen
    doc = json.loads(path.read_bytes())
    dbg = doc["data"]["debug"]
    rep = dbg["replay"]
    span = dbg["manifest"]["span_hours"]
    parts = {k: _indent(k, v) for k, v in dbg.items() if k not in ("replay", "trace", "lifecycle")}
    parts["cycle_rows"] = round(parts["cycle_rows"] * 168.0 / span)
    snaps = dbg["payload_snapshots"]
    full_snaps = round(parts["payload_snapshots"] * 7 / len(snaps))
    thin_snaps = round(parts["payload_snapshots"] * 2 / len(snaps))
    start = datetime.fromisoformat(rep["window"]["start"]).astimezone(timezone.utc)
    day = {**rep, "window": {"start": start.isoformat(),
                             "end": (start + timedelta(days=1)).isoformat()}}
    blocks = dbg_bundle_gen.trace_blocks(day)
    cols = {k: v for b in blocks for k, v in b["cols"].items()}
    densest = sorted(cols.values(), key=len, reverse=True)[:ARBITER_COLUMNS]
    one = {"start": blocks[0]["start"], "n": sum(b["n"] for b in blocks), "gap": blocks[0]["gap"],
           "cols": {**cols, **{f"arbiter/{i}": text for i, text in enumerate(densest)}}}
    trace_inputs = _indent("trace", [{**one, "cols": cols}] * 7)
    trace = _indent("trace", [one] * 7)
    random.seed(3106)
    rows = [[29563210 + 7 * i, 24, 41.5, 25.0, 55.0, 38.2, 1.38, 0.5, 4.0, 55.0,
             round(random.uniform(30, 42), 1), 0.6, -2.3, round(random.uniform(0.5, 4), 2),
             0.18, "s", "s"] for i in range(MAP_ROWS)]
    columnar = {f"c{j}": ",".join(str(r[j]) for r in rows) for j in range(MAP_FIELDS)}
    map_bytes = (_indent("stores", {"x": {"accuracy": {"draw": {"map": columnar}}}})
                 - _indent("stores", {"x": {"accuracy": {"draw": {}}}}))
    allowed = debugger.INLINE_CAP_BYTES - debugger.DOWNLOAD_HEADROOM_BYTES
    replay_24h = _indent("replay", rep)
    base = sum(parts.values()) - parts["payload_snapshots"]
    for label, snap in (("all 7 snapshots", full_snaps), ("snapshots thinned to 2", thin_snaps)):
        need = base + snap + trace + map_bytes
        print(f"RESULT {label}: non_replay={need} left_for_replay={allowed - need} "
              f"replay_24h={replay_24h} fits={allowed - need >= replay_24h} unit=byte")
    print(f"RESULT trace_columns_inputs={len(cols)} unit=count")
    print(f"RESULT trace_day_inputs={trace_inputs // 7} trace_week_inputs={trace_inputs} unit=byte")
    print(f"RESULT trace_week_with_arbiter_bound={trace} unit=byte")
    print(f"RESULT map_rows_columnar={map_bytes} unit=byte")


class _Coord:
    integration_version = "synthetic"
    optimization_running = False
    solve_failures = 0
    prices = ()

    def __init__(self) -> None:
        self.accuracy = types.SimpleNamespace(samples=[])
        self.data = None

    def async_add_listener(self, _listener):
        return lambda: None


def writes(enabled: bool, columns: int = COLUMNS, change: float = 0.3) -> list[int]:
    """Bytes the debug store's saves write on each of seven synthetic days."""
    from harness import FakeEntry, FakeHass
    from homeassistant.helpers import storage
    from homeassistant.util import dt as dt_util
    from heatpump_optimizer.const import CONF_DEBUG_COLLECT
    storage._DISK.clear()
    entities = {f"col_{i}_entity": f"sensor.col_{i}" for i in range(columns)}
    hass = FakeHass()
    entry = FakeEntry(entry_id="w", data=entities, options={CONF_DEBUG_COLLECT: enabled})
    coord = _Coord()
    written = [0] * 7
    t0 = datetime(2026, 1, 12, tzinfo=timezone.utc)
    now = {"t": t0}
    saves = []
    entry.async_create_background_task = lambda _h, coro, name=None: saves.append(coro)

    async def drive() -> None:
        await debugger.async_setup_debugger(hass, entry, coord)
        collector = debugger.collector_for(coord)
        rng = random.Random(1939)
        for minute in range(7 * 1440):
            at = t0 + timedelta(minutes=minute)
            now["t"] = at
            dt_util.freeze(at)
            for i in range(columns):
                if rng.random() < change:
                    hass.states.set(f"sensor.col_{i}", types.SimpleNamespace(
                        state=f"{20 + rng.random() * 5:.3f}"))
            if collector is not None:
                if minute % 30 == 0:
                    coord.data = {"mode": "auto", "current_action": {"power": 1.0},
                                  "indoor_temperature": 21.0, "learners_frozen": False,
                                  "input_health": "ok"}
                    collector.observe(coord)
                collector.sample(at, {})
            while saves:
                before = dict(storage._DISK)
                await saves.pop(0)
                for key, text in storage._DISK.items():
                    if text is not before.get(key):
                        written[minute // 1440] += len(text.encode())
        dt_util.freeze(None)

    asyncio.run(drive())
    return written


def replay_null(path: Path) -> None:
    import copy
    import debug_ingest
    import debug_replay
    bundle = debug_ingest.load_bundle(path)

    def offenders(doc: dict) -> list:
        verdict = debug_replay.run_seeded(debug_replay.offender_window(doc))
        return (verdict.get("results") or {}).get("agreement") or []

    half = offenders(bundle["replay"])
    traced = offenders(debug_replay.trace_document(bundle))
    moved = copy.deepcopy(bundle)
    for block in moved["trace"]:
        block["cols"]["dhw_temp_entity"] = ",".join([PERTURB_DHW_C] + [""] * (block["n"] - 1))
    perturbed = offenders(debug_replay.trace_document(moved))
    print(f"RESULT offenders_replay_half={len(half)} offenders_trace={len(traced)} "
          f"equal={half == traced} unit=count")
    print(f"RESULT offenders_perturbed={len(perturbed)} moved={perturbed != traced} unit=count")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", type=Path)
    ap.add_argument("--writes", action="store_true")
    ap.add_argument("--replay-null", type=Path)
    ap.add_argument("--columns", type=int, default=COLUMNS)
    ap.add_argument("--change", type=float, default=0.3, help="share of minutes a column changes")
    a = ap.parse_args()
    if a.bundle:
        budget(a.bundle)
    if a.replay_null:
        replay_null(a.replay_null)
    if a.writes:
        for enabled in (True, False):
            per_day = writes(enabled, a.columns, a.change)
            print(f"RESULT option_{'on' if enabled else 'off'} store_bytes_written_per_day="
                  f"{per_day} unit=byte")
    return 0


if __name__ == "__main__":
    sys.exit(main())
