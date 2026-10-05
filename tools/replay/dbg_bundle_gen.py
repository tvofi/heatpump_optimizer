#!/usr/bin/env python3
"""Generate a synthetic-week ``hpo-debug/1`` debugger bundle.

Promoted from the R9-DBG-0 prototype at ``eae236d66``. Drives
``tests/replay.py:run_fixture`` over the committed DHW-only fixture repeated
day by day, records a slim per-cycle row plus one payload snapshot per day,
and harvests every ``heatpump_optimizer_*`` store document from the HA-stub
disk.

    PYTHONPATH=tests/hastub:tests python3 tools/replay/dbg_bundle_gen.py --days 7 --out DIR
    PYTHONPATH=tests/hastub:tests python3 tools/replay/dbg_bundle_gen.py --days 1 --out DIR
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
import time
from datetime import timedelta
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components", HERE):
    s = str(_p)
    if s not in sys.path:
        sys.path.insert(0, s)

import debug_ingest  # noqa: E402

SCHEMA = debug_ingest.SCHEMA
FIXTURE = ROOT / "tests" / "replay" / "synthetic-dhw-only.json"
GENERATOR = "tools/replay/dbg_bundle_gen.py"


def _shift(iso: str | None, days: int) -> str | None:
    if iso is None:
        return None
    from datetime import datetime
    return (datetime.fromisoformat(iso) + timedelta(days=days)).isoformat()


def extend_fixture(days: int) -> dict:
    """Repeat the recorded day ``days`` times, shifting stamps by whole days."""
    fixture = json.loads(FIXTURE.read_text())
    start = fixture["window"]["start"]
    out_states: dict[str, list] = {}
    for entity, rows in fixture["states"].items():
        extended: list = []
        for day in range(days):
            for updated, state, attrs, reported in rows:
                extended.append([
                    _shift(updated, day), state, attrs, _shift(reported, day)])
        out_states[entity] = extended
    fixture["states"] = out_states
    fixture["window"] = {
        "start": start,
        "end": _shift(fixture["window"]["end"], days - 1),
    }
    return fixture


def build_bundle(days: int, drop: set[str] | None = None) -> dict:
    drop = drop or set()
    fixture = extend_fixture(days)
    import replay
    from homeassistant.util import dt as dt_util
    from heatpump_optimizer import coordinator as cm

    rows: list[dict] = []
    payload_snapshots: list[dict] = []
    seen: dict[str, object] = {}
    real_tick = cm.HeatPumpOptimizerCoordinator._async_update_data

    async def recording_tick(self):
        began = time.perf_counter()
        data = await real_tick(self)
        seen["coord"] = self
        wall_ms = round((time.perf_counter() - began) * 1000.0, 1)
        sample = None
        acc = getattr(self, "_accuracy", None)
        if acc is not None and acc.samples:
            s = acc.samples[-1]
            sample = {
                "predicted_power_kw": s.predicted_power_kw,
                "actual_power_kw": s.actual_power_kw,
                "predicted_temp": s.predicted_temp,
                "actual_temp": s.actual_temp,
                "outdoor_temp": s.outdoor_temp,
            }
        action = data.get("current_action") or {}
        row = {
            "t": dt_util.now().isoformat(),
            "mode": data.get("mode"),
            "action_mode": action.get("mode"),
            "action_kw": action.get("power"),
            "heat_pump_on": action.get("heat_pump_on"),
            "solve_wall_ms": wall_ms,
            "payload_solve_time_ms": data.get("solve_time_ms"),
            "solve_failures": getattr(self, "_solve_failures", None),
            "prices_rows": len(getattr(self, "_prices", ()) or ()),
            "weather_stale_h": data.get("weather_forecast_stale_hours"),
            "indoor_temp": data.get("indoor_temperature"),
            "outdoor_temp": data.get("outdoor_temperature"),
            "dhw_temp": data.get("dhw_temperature"),
            "accuracy_sample": sample,
        }
        for key in drop:
            row.pop(key, None)
        rows.append(row)
        if len(rows) % 48 == 1:
            payload_snapshots.append({"cycle": len(rows) - 1, "data": data})
        return data

    import tempfile
    cm.HeatPumpOptimizerCoordinator._async_update_data = recording_tick
    try:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "week-fixture.json"
            path.write_text(json.dumps(fixture))
            verdict = replay.run_fixture(path, None, None)
    finally:
        cm.HeatPumpOptimizerCoordinator._async_update_data = real_tick

    from homeassistant.helpers import storage as stub_storage
    stores: dict[str, dict] = {}
    save_counts: dict[str, int] = {}
    for key, document in sorted(stub_storage._DISK.items()):
        if not key.startswith("heatpump_optimizer"):
            continue
        stores[key] = json.loads(document)
        save_counts[key] = stub_storage.SAVE_COUNTS.get(key, 0)

    diagnostics_view = None
    coord = seen.get("coord")
    if coord is not None:
        from heatpump_optimizer import diagnostics as diag_mod
        diagnostics_view = diag_mod._coordinator_snapshot(coord)

    version = (ROOT / "VERSION").read_text().strip()
    return {
        "schema": SCHEMA,
        "manifest": {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "generator": GENERATOR,
            "integration_version": version,
            "days": days,
            "cycles": len(rows),
            "replay_verdict": verdict,
            "dropped_slim_fields": sorted(drop),
        },
        "replay": fixture,
        "cycle_rows": rows,
        "payload_snapshots": payload_snapshots,
        "stores": stores,
        "store_save_counts": save_counts,
        "diagnostics": diagnostics_view,
    }


def gate_checks() -> list[tuple[str, bool, str]]:
    one = extend_fixture(1)
    two = extend_fixture(2)
    entity = next(iter(one["states"]))
    return [
        ("debug generator: schema id is hpo-debug/1",
         SCHEMA == "hpo-debug/1", SCHEMA),
        ("debug generator: extend_fixture(1) keeps the committed window",
         one["window"] == json.loads(FIXTURE.read_text())["window"],
         str(one["window"])),
        ("debug generator: extend_fixture(2) doubles state rows and shifts end",
         len(two["states"][entity]) == 2 * len(one["states"][entity])
         and two["window"]["end"] != one["window"]["end"],
         f"n1={len(one['states'][entity])} n2={len(two['states'][entity])}"),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--out", default="/tmp/hpo-debug-bundle")
    parser.add_argument("--slim-fields", default="",
                        help="comma list of slim-row fields to drop")
    args = parser.parse_args(argv)
    drop = {s.strip() for s in args.slim_fields.split(",") if s.strip()}
    bundle = build_bundle(args.days, drop)

    from datetime import datetime as _dt

    def _default(obj: object) -> object:
        if isinstance(obj, _dt):
            return obj.isoformat()
        raise TypeError(f"unserialisable: {type(obj).__name__}")

    def _dumps(node: object) -> str:
        return json.dumps(node, default=_default)

    raw = _dumps(bundle).encode()
    packed = gzip.compress(raw, 6)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "bundle.json").write_bytes(raw)
    (out_dir / "bundle.json.gz").write_bytes(packed)
    rows = bundle["cycle_rows"]
    row_bytes = len(_dumps(rows).encode())
    print(f"RESULT bundle_schema={SCHEMA} unit=identifier")
    print(f"RESULT cycles={len(rows)} unit=count")
    print(f"RESULT stores={len(bundle['stores'])} unit=count")
    print(f"RESULT raw_bytes={len(raw)} unit=byte")
    print(f"RESULT gz_bytes={len(packed)} unit=byte")
    print(f"RESULT cycle_row_bytes={row_bytes} unit=byte")
    print(f"RESULT mean_row_bytes={row_bytes // max(len(rows), 1)} unit=byte")
    print("RESULT thread_factor=1.0 unit=ratio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
