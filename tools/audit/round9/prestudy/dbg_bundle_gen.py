#!/usr/bin/env python3
"""R9-DBG-0 pre-study prototype: generate a synthetic-week debugger bundle.

Metric definition: the shape and byte size of one week (``--days``, default 7)
of debugger collection from a live-install-shaped source, produced by driving
the real coordinator cycle (``tests/replay.py:run_fixture``) over the
committed synthetic fixture repeated day by day, recording a slim per-cycle
row plus one full payload snapshot per day, and harvesting every
``heatpump_optimizer_*`` store document from the HA-stub storage disk.

Run command (from the repository root):

    PYTHONPATH=tests/hastub:tests ~/.local/state/hpo/venv-ci/bin/python \
        tools/audit/round9/prestudy/dbg_bundle_gen.py --days 7 \
        --out /tmp/r9-dbg-0/bundle

Expected: ``RESULT bundle_schema=hpo-debug/1``, ``RESULT cycles=<48*days>``,
``RESULT raw_bytes`` within 3x of the committed synthetic fixture's size times
days (the slim rows dominate, not the payload snapshots), and a written
``bundle.json`` plus ``bundle.json.gz``. Baseline: the seat worktree head of
``handoff/r9-dbg-0``. Machine: the seat's Mac, venv-ci wheels (numpy 2.4.6,
scipy 1.17.1) -- a size measurement, contention-immune.

Perturbation (canon): ``--days 1`` must produce roughly 1/7 the cycle rows and
one payload snapshot; ``--slim-fields -price_rows`` must shrink row bytes.
The bundle consumes only code that exists at the baseline: ``run_fixture``,
the coordinator's own ``_async_update_data``, ``diagnostics``
``_coordinator_snapshot``, and the HA-stub ``Store`` disk. It adds no
production code.
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

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "tests" / "hastub"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))

SCHEMA = "hpo-debug/1"
FIXTURE = ROOT / "tests" / "replay" / "synthetic-dhw-only.json"


def extend_fixture(days: int) -> dict:
    """Repeat the recorded day ``days`` times, shifting stamps by whole days.

    The synthetic fixture records one January day; the D9-s2 rig already
    repeats it in-process. Here the repetition is materialised so the bundle
    carries a real ``hpo-replay/1`` document for a whole week.
    """
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


def _shift(iso: str, days: int) -> str:
    from datetime import datetime
    t = datetime.fromisoformat(iso)
    return (t + timedelta(days=days)).isoformat()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--out", default="/tmp/r9-dbg-0/bundle")
    parser.add_argument("--slim-fields", default="",
                        help="comma list of slim-row fields to drop (perturbation arm)")
    args = parser.parse_args(argv)
    drop = {s.strip() for s in args.slim_fields.split(",") if s.strip()}

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    extended_path = out_dir / "week-fixture.json"
    fixture = extend_fixture(args.days)
    extended_path.write_text(json.dumps(fixture))

    # -- record the cycles by wrapping the production tick, in memory only ----
    import replay  # tests/replay.py; imports stress first, which pins BLAS
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
        if len(rows) % 48 == 1:  # one full payload snapshot per day
            payload_snapshots.append({"cycle": len(rows) - 1, "data": data})
        return data

    cm.HeatPumpOptimizerCoordinator._async_update_data = recording_tick
    try:
        verdict = replay.run_fixture(extended_path, None, None)
    finally:
        cm.HeatPumpOptimizerCoordinator._async_update_data = real_tick

    # -- harvest the stores from the HA-stub disk -----------------------------
    from homeassistant.helpers import storage as stub_storage
    stores: dict[str, dict] = {}
    save_counts: dict[str, int] = {}
    for key, document in sorted(stub_storage._DISK.items()):
        if not key.startswith("heatpump_optimizer"):
            continue
        stores[key] = json.loads(document)
        save_counts[key] = stub_storage.SAVE_COUNTS.get(key, 0)

    # -- the existing diagnostics snapshot, reused verbatim -------------------
    diagnostics_view = None
    coord = seen.get("coord")
    if coord is not None:
        from heatpump_optimizer import diagnostics as diag_mod
        diagnostics_view = diag_mod._coordinator_snapshot(coord)

    version = (ROOT / "VERSION").read_text().strip()
    bundle = {
        "schema": SCHEMA,
        "manifest": {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "generator": "tools/audit/round9/prestudy/dbg_bundle_gen.py",
            "integration_version": version,
            "days": args.days,
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
    # ``last_optimization`` and friends carry datetimes; the wire form is ISO
    # strings, exactly what a store round-trip would leave behind.
    from datetime import datetime as _dt

    def _default(obj: object) -> object:
        if isinstance(obj, _dt):
            return obj.isoformat()
        raise TypeError(f"unserialisable: {type(obj).__name__}")

    def _dumps(node: object) -> str:
        return json.dumps(node, default=_default)

    raw = _dumps(bundle).encode()
    packed = gzip.compress(raw, 6)
    (out_dir / "bundle.json").write_bytes(raw)
    (out_dir / "bundle.json.gz").write_bytes(packed)

    row_bytes = len(_dumps(rows).encode())
    snap_bytes = len(_dumps(payload_snapshots).encode())
    store_bytes = len(_dumps(stores).encode())
    replay_bytes = len(_dumps(fixture).encode())
    print(f"RESULT bundle_schema={SCHEMA} unit=identifier")
    print(f"RESULT cycles={len(rows)} unit=count")
    print(f"RESULT stores={len(stores)} unit=count")
    print(f"RESULT raw_bytes={len(raw)} unit=byte")
    print(f"RESULT gz_bytes={len(packed)} unit=byte")
    print(f"RESULT cycle_row_bytes={row_bytes} unit=byte")
    print(f"RESULT payload_snapshot_bytes={snap_bytes} unit=byte")
    print(f"RESULT store_bytes={store_bytes} unit=byte")
    print(f"RESULT replay_fixture_bytes={replay_bytes} unit=byte")
    print(f"RESULT mean_row_bytes={row_bytes // max(len(rows), 1)} unit=byte")
    print(f"RESULT diagnostics_bytes={len(_dumps(diagnostics_view).encode())} unit=byte")
    print(f"RESULT thread_factor=1.0 unit=ratio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
