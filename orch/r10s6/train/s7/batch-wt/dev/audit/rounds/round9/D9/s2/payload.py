#!/usr/bin/env python3
"""D9-s2 (round 9, D9.M1) -- published payload bytes versus the recorder
exclusion set.

METRIC: per real cycle (HeatPumpOptimizerCoordinator._async_update_data over
tests/replay/synthetic-dhw-only.json, 48 cycles = one day), for every entity
the six platforms publish (tests/replay.py:sweep reads each one's state and
extra_state_attributes as async_write_ha_state would): the compact JSON bytes
of its attributes split into RECORDED (keys not in the entity class's
_unrecorded_attributes) and UNRECORDED; and "recorder attribute bytes per day"
= the sum, over cycles where an entity's recorded attributes differ from its
previous cycle's (the recorder writes a new state_attributes row only then),
of that recorded JSON size. Also the JSON bytes of coordinator.data
(_build_data_dict) per cycle. HA's component-level exclusions
(_entity_component_unrecorded_attributes, absent from tests/hastub) are NOT
subtracted: numbers are an upper bound by those keys.
Count key: bytes of the attributes the production entities return.
COMMAND (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D9/s2/payload.py
PERTURBATION: --exclude KEY (in memory: add KEY to the _unrecorded_attributes
  of every entity class that publishes it) -> recorded_attr_bytes_per_day DOWN
  by that key's share; e.g. --exclude dhw_plan_forecast.
EXPECTED (baseline 1936d5ca): bytes exact (+-0.5 %) for a deterministic replay.
MACHINE: round-9 box B5 (Linux container, Intel Xeon @ 2.80GHz, 4 vCPU, 16 GB, numpy 2.4.6/scipy 1.17.1,
  Python 3.14.0rc2). Root rule: os.getcwd().
"""
from __future__ import annotations

import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import argparse
import collections
import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / "tools" / "audit" / "round9" / "D9" / "s2"))
import _rig  # noqa: E402


def jbytes(obj) -> int:
    return len(json.dumps(obj, default=str, separators=(",", ":"),
                          ensure_ascii=False).encode())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exclude", action="append", default=[])
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args()
    data_bytes: list[int] = []

    def after(probe, coord, data):
        data_bytes.append(jbytes(data))

    _rig.PROBE.after_cycle.append(after)
    _rig.install()
    p0, t0 = time.process_time(), time.thread_time()
    out = _rig.run(1)
    pc, tc = time.process_time() - p0, time.thread_time() - t0
    cycles = _rig.PROBE.cycles
    ents = cycles[-1]["entities"]
    unrec = {}
    for e in ents:
        eid = getattr(e, "entity_id", None) or getattr(e, "_attr_unique_id", repr(e))
        unrec[eid] = set(getattr(type(e), "_unrecorded_attributes", frozenset())) | set(args.exclude)
    prev: dict[str, str] = {}
    per_ent = collections.Counter()
    per_key = collections.Counter()
    rec_cycle, unrec_cycle, writes = [], [], 0
    for c in cycles:
        r_tot = u_tot = 0
        for r in c.get("records", []):
            attrs = r["attributes"] or {}
            ex = unrec.get(r["entity_id"], set())
            rec = {k: v for k, v in attrs.items() if k not in ex}
            un = {k: v for k, v in attrs.items() if k in ex}
            rb, ub = jbytes(rec), jbytes(un)
            r_tot += rb
            u_tot += ub
            key = json.dumps(rec, default=str, sort_keys=True)
            if prev.get(r["entity_id"]) != key:
                writes += 1
                per_ent[r["entity_id"]] += rb
                for k, v in rec.items():
                    per_key[f"{r['entity_id']}.{k}"] += jbytes({k: v})
            prev[r["entity_id"]] = key
        rec_cycle.append(r_tot)
        unrec_cycle.append(u_tot)
    n = len(cycles)
    day = sum(per_ent.values())
    print(f"cycles={n} entities={len(ents)} counts={out['counts']}")
    for eid, b in per_ent.most_common(args.top):
        print(f"#  entity {eid}: {b} B/day recorded attributes")
    for k, b in per_key.most_common(args.top):
        print(f"#  key {k}: {b} B/day")
    print(f"RESULT cycles={n} count")
    print(f"RESULT entities={len(ents)} count")
    print(f"RESULT data_dict_bytes_per_cycle={sum(data_bytes) / len(data_bytes):.0f} bytes")
    print(f"RESULT attrs_recorded_bytes_per_cycle={sum(rec_cycle) / n:.0f} bytes")
    print(f"RESULT attrs_unrecorded_bytes_per_cycle={sum(unrec_cycle) / n:.0f} bytes")
    print(f"RESULT recorded_attr_rows_per_day={writes} count")
    print(f"RESULT recorded_attr_bytes_per_day={day} bytes")
    top_eid, top_b = per_ent.most_common(1)[0]
    print(f"RESULT top_entity_share_of_recorded_per_day={top_b / day:.4f} ratio ({top_eid})")
    for k, b in per_key.most_common(5):
        print(f"RESULT key.{k}={b} bytes_per_day")
    _rig.tail(pc / tc if tc else float("nan"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
