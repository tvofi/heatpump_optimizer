#!/usr/bin/env python3
"""D9-s2 payload bytes: JSON bytes of the published data dict and of every entity's attributes, per cycle and per day.

METRIC (D9.md "Payload bytes"): per real coordinator cycle
(``HeatPumpOptimizerCoordinator._async_update_data``), the compact-JSON byte length of
(a) ``coordinator.data`` (what ``_build_data_dict`` builds plus the cycle's additions) and
(b) each entity's ``extra_state_attributes`` (climate: plus its state attributes), split by
the class's ``_unrecorded_attributes`` into recorded / unrecorded. Per day at the
shortest interval (10 min, 144 cycles): recorded bytes of every entity whose recorded
attribute set changed since the previous cycle (each such change is one new recorder
``state_attributes`` row, deduplicated by content as the recorder does). B6 budgets: one
entity's recorded attributes <= 16,384 B (the recorder's own cap); all recorded attribute
bytes <= 5 MB/day. Count key: the bytes the production property returns, encoded compactly
(orjson-equivalent separators; datetimes ISO; non-finite as null).

RUN:   HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D9/s2/payload.py \
         --fixture owner --cycles 160 [--perturb NAME] [--json OUT]
EXPECTED: printed per run; finding blocks quote values with tolerance (bytes are exact
for a fixed driver; the plan content depends on the solver, +-5 %).
BASELINE: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. MACHINE: printed.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import collections
import hashlib
import json
import math
import platform
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _drive  # noqa: E402

RECORDER_ATTR_CAP = 16384  # homeassistant/components/recorder/db_schema.py MAX_STATE_ATTRS_BYTES
DAY_BUDGET = 5_000_000


def _clean(o):
    if isinstance(o, float):
        return o if math.isfinite(o) else None
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, set, frozenset)):
        return [_clean(v) for v in o]
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    if isinstance(o, timedelta):
        return o.total_seconds()
    try:
        import numpy as np
        if isinstance(o, np.generic):
            return _clean(o.item())
        if isinstance(o, np.ndarray):
            return _clean(o.tolist())
    except ImportError:
        pass
    if hasattr(o, "value") and type(o).__module__.startswith(("enum", "homeassistant")):
        return _clean(o.value)
    return o


def jbytes(o) -> int:
    return len(json.dumps(_clean(o), separators=(",", ":"), ensure_ascii=False,
                          default=str).encode())


def unrecorded(ent) -> frozenset:
    return frozenset(getattr(type(ent), "_unrecorded_attributes", frozenset()) or ()) | \
        frozenset(getattr(type(ent), "_entity_component_unrecorded_attributes", frozenset()) or ())


def attrs_of(ent) -> dict:
    a = dict(getattr(ent, "extra_state_attributes", None) or {})
    if type(ent).__module__.endswith(".climate"):
        for name, prop in (("current_temperature", "current_temperature"),
                           ("temperature", "target_temperature"), ("hvac_action", "hvac_action")):
            try:
                a.setdefault(name, getattr(ent, prop))
            except Exception:  # noqa: BLE001
                pass
    return a


PERTURB = {}


def _p_record_plan_forecast(_):
    # sensor.py:_PlanSensorBase._unrecorded_attributes drops "forecast" -> recorded bytes go UP.
    from heatpump_optimizer import sensor
    sensor._PlanSensorBase._unrecorded_attributes = sensor._PlanSensorBase._unrecorded_attributes - {"forecast"}


PERTURB["record_plan_forecast"] = _p_record_plan_forecast


def run(args) -> dict:
    if args.perturb:
        PERTURB[args.perturb](None)
    drv = _drive.Driver(args.fixture, step_minutes=args.step_minutes)
    per_entity: dict[str, dict] = {}
    data_bytes: list[int] = []
    rec_cycle: list[int] = []
    unrec_cycle: list[int] = []
    new_rows_bytes: list[int] = []
    changed_bytes: list[int] = []
    prev_rec: dict[str, str] = {}
    seen_hash: set[str] = set()
    top_keys = collections.Counter()
    for c in range(1, args.cycles + 1):
        data = drv.cycle()
        if c <= args.warmup:
            continue
        data_bytes.append(jbytes(data))
        for k, v in (data or {}).items():
            top_keys[k] = max(top_keys[k], jbytes(v))
        r_tot = u_tot = new_b = chg_b = 0
        for ent in drv.entities:
            key = f"{type(ent).__name__}:{getattr(ent, '_attr_unique_id', '')}"
            try:
                a = attrs_of(ent)
            except Exception as err:  # noqa: BLE001
                drv.errors.append(f"{key}: {err}")
                continue
            un = unrecorded(ent)
            rec = {k: v for k, v in a.items() if k not in un}
            unr = {k: v for k, v in a.items() if k in un}
            rb, ub = jbytes(rec), jbytes(unr)
            r_tot += rb; u_tot += ub
            blob = json.dumps(_clean(rec), separators=(",", ":"), sort_keys=True, default=str)
            if prev_rec.get(key) != blob:
                chg_b += rb
                h = hashlib.sha1(blob.encode()).hexdigest()
                if h not in seen_hash:
                    seen_hash.add(h); new_b += rb
            prev_rec[key] = blob
            pe = per_entity.setdefault(key, {"file": type(ent).__module__.rsplit(".", 1)[-1] + ".py",
                                             "rec_max": 0, "unrec_max": 0, "changes": 0,
                                             "rec_keys": {}, "n": 0})
            pe["rec_max"] = max(pe["rec_max"], rb)
            pe["unrec_max"] = max(pe["unrec_max"], ub)
            pe["n"] += 1
            for k, v in rec.items():
                pe["rec_keys"][k] = max(pe["rec_keys"].get(k, 0), jbytes(v))
        rec_cycle.append(r_tot); unrec_cycle.append(u_tot)
        new_rows_bytes.append(new_b); changed_bytes.append(chg_b)
    drv.close()
    n = len(rec_cycle)
    return {"fixture": args.fixture, "cycles": args.cycles, "warmup": args.warmup,
            "perturb": args.perturb, "n_errors": getattr(drv, "n_errors", len(drv.errors)), "errors": drv.errors[:4],
            "entities": len(drv.entities), "measured": n,
            "data_bytes_max": max(data_bytes), "data_bytes_mean": sum(data_bytes) / n,
            "data_top_keys": top_keys.most_common(12),
            "rec_cycle_mean": sum(rec_cycle) / n, "unrec_cycle_mean": sum(unrec_cycle) / n,
            "changed_per_day": sum(changed_bytes) / n * _drive.CYCLES_PER_DAY,
            "newrows_per_day": sum(new_rows_bytes) / n * _drive.CYCLES_PER_DAY,
            "per_entity": per_entity}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", default="owner", choices=sorted(_drive.FIXTURES))
    ap.add_argument("--cycles", type=int, default=160)
    ap.add_argument("--warmup", type=int, default=16)
    ap.add_argument("--perturb", default=None, choices=[None, *PERTURB])
    ap.add_argument("--step-minutes", type=int, default=None,
                    help="time-warp arm: clock step between cycles; per-day figures stay per 144 cycles")
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    t0 = time.time()
    out = run(args)
    if args.json:
        Path(args.json).write_text(json.dumps(out))
    print(f"# machine {platform.platform()} py{platform.python_version()}")
    print(f"# fixture={out['fixture']} cycles={out['cycles']} warmup={out['warmup']} measured={out['measured']} "
          f"entities={out['entities']} perturb={out['perturb']} errors={out['n_errors']} {out['errors'][:2]}")
    print(f"RESULT data_dict_bytes_max={out['data_bytes_max']} B")
    print(f"RESULT data_dict_bytes_mean={out['data_bytes_mean']:.0f} B")
    for k, v in out["data_top_keys"]:
        print(f"#   data[{k}] max {v} B")
    print(f"RESULT attrs_recorded_per_cycle={out['rec_cycle_mean']:.0f} B")
    print(f"RESULT attrs_unrecorded_per_cycle={out['unrec_cycle_mean']:.0f} B")
    print(f"RESULT recorded_changed_per_day={out['changed_per_day']:.0f} B (B6 budget {DAY_BUDGET})")
    print(f"RESULT recorded_newrows_per_day={out['newrows_per_day']:.0f} B (recorder dedup by content)")
    worst = sorted(out["per_entity"].items(), key=lambda kv: -kv[1]["rec_max"])
    over = [k for k, v in worst if v["rec_max"] > RECORDER_ATTR_CAP]
    print(f"RESULT entities_over_16384={len(over)} count {over}")
    for k, v in worst[:15]:
        topk = sorted(v["rec_keys"].items(), key=lambda kv: -kv[1])[:4]
        print(f"RESULT entity_recorded_max[{k}]={v['rec_max']} B unrec_max={v['unrec_max']} file={v['file']} top={topk}")
    files = collections.Counter()
    for k, v in out["per_entity"].items():
        files[v["file"]] += v["rec_max"]
    for f, b in files.most_common():
        print(f"RESULT file_recorded_max_sum[{f}]={b} B")
    print(f"RESULT wall_s={time.time() - t0:.0f} s (provisional)")
    print(f"RESULT thread_factor={time.process_time() / max(1e-9, time.thread_time()):.3f}")
    print(f"RESULT load1={_drive.load1()}")
    print(f"RESULT swapins={_drive.swapins()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
