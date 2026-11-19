"""D8-s1 M1/M2 matrix: every entity of the five owned platforms, every cell, two cycles.

Metric: per violation class, the count of (cell, entity) pairs breaking a Home
Assistant publication rule or the D8.M2 per-entity contract, keyed on the value
the production entity property returns (native_value / is_on / hvac_mode and
extra_state_attributes) after a real `_async_update_data` cycle.

Command (from the export root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D8/s1/matrix.py [--dump]
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine: orchestrator's macOS box (B4).
Expected: the RESULT counts printed at baseline, exact (deterministic: frozen clock, no network).
Instrumented symbols: heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_update_data
and each platform's async_setup_entry (sensor, binary_sensor, button, climate, switch).

Violation classes (one RESULT each):
  raise          a property raised
  numeric        unit or state_class set (or numeric device class) and the state is not a number
  timestamp      device_class timestamp and the state is not a tz-aware datetime
  enum           device_class enum and the state is not in options
  unit           unit does not belong to the device_class
  serial         state or attributes not plain-JSON (numpy scalar, NaN/inf, foreign object)
  state_len      a string state over 255 characters (HA writes "unknown" instead)
  attr_bytes     recorded attributes over 16384 bytes of JSON (the recorder drops them)
  unknown_src    available, state None, while the payload key the entity is named for is non-None
  stale          state identical in cycles A and B while its payload key changed
--dump writes every row to $TMPDIR/d8s1-matrix-*/rows.json.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import math
import sys
import tempfile
import time
from collections import Counter, defaultdict
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402
import numpy as np  # noqa: E402

UNITS = {
    "temperature": {"°C", "°F", "K"},
    "power": {"W", "kW", "MW", "mW", "GW", "TW", "BTU/h"},
    "energy": {"Wh", "kWh", "MWh", "GWh", "J", "kJ", "MJ", "GJ", "cal", "kcal", "Mcal", "Gcal", "mWh", "TWh"},
    "irradiance": {"W/m²", "BTU/(h⋅ft²)"},
    "battery": {"%"},
    "frequency": {"Hz", "kHz", "MHz", "GHz"},
    "volume_storage": {"L", "mL", "m³", "ft³", "gal", "fl. oz.", "CCF"},
    "energy_storage": {"Wh", "kWh", "MWh", "GWh", "J", "kJ", "MJ", "GJ", "cal", "kcal", "Mcal", "Gcal", "mWh", "TWh"},
    "timestamp": {None},
    "enum": {None},
}
NON_NUMERIC = {"enum", "timestamp"}


def plain(v, path, bad):
    if v is None or isinstance(v, (str, bool)):
        return
    if isinstance(v, np.generic):
        bad.append(f"{path}:numpy {type(v).__name__}")
    elif isinstance(v, int):
        return
    elif isinstance(v, float):
        if not math.isfinite(v):
            bad.append(f"{path}:{v}")
    elif isinstance(v, dict):
        for k, x in v.items():
            if not isinstance(k, (str, int, float, bool)):
                bad.append(f"{path}:key {type(k).__name__}")
            plain(x, f"{path}.{k}", bad)
    elif isinstance(v, (list, tuple, set, frozenset)):
        for i, x in enumerate(v):
            plain(x, f"{path}[{i}]", bad)
    elif isinstance(v, (datetime, date)):
        return
    else:
        bad.append(f"{path}:{type(v).__name__}")


def source(row, data):
    """(present, value) of the payload key the entity is named for."""
    e = row["entity"]
    path = getattr(e, "_payload_path", None) or ((row["key"],) if row["key"] else ())
    node = data or {}
    for k in path:
        if not isinstance(node, dict) or k not in node:
            return False, None
        node = node[k]
    return bool(path), node


def is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def check_cycle(cell, cyc, rows, data, hits):
    for r in rows:
        ent = f"{cell}|{r['platform']}.{r['cls']}"
        if r["state_err"] or r["attrs_err"]:
            hits["raise"].append(f"{ent}|{r['state_err'] or r['attrs_err']}")
        if r["platform"] != "sensor":
            continue
        st, dc, sc, unit = r["state"], r["device_class"], r["state_class"], r["unit"]
        if st is not None:
            numeric = (unit is not None or sc is not None or (dc is not None and dc not in NON_NUMERIC))
            if numeric and not is_number(st):
                try:
                    float(st)
                except (TypeError, ValueError):
                    hits["numeric"].append(f"{ent}|{st!r}")
            if dc == "timestamp" and not (isinstance(st, datetime) and st.tzinfo is not None):
                hits["timestamp"].append(f"{ent}|{st!r}")
            if dc == "enum" and r["options"] and st not in r["options"]:
                hits["enum"].append(f"{ent}|{st!r}")
            if isinstance(st, str) and len(st) > 255:
                hits["state_len"].append(f"{ent}|{len(st)}")
        if dc in UNITS and unit not in UNITS[dc] and not (dc == "monetary"):
            hits["unit"].append(f"{ent}|{dc}|{unit}")
        bad = []
        plain(st, "state", bad)
        plain(r["attrs"], "attrs", bad)
        if bad:
            hits["serial"].append(f"{ent}|{bad[:3]}")
        if isinstance(r["attrs"], dict):
            skip = getattr(r["entity"], "_unrecorded_attributes", frozenset())
            rec = {k: v for k, v in r["attrs"].items() if k not in skip}
            size = len(json.dumps(rec, default=str))
            if size > 16384:
                hits["attr_bytes"].append(f"{ent}|{size}")
        present, val = source(r, data)
        if r["available"] and st is None and present and val is not None:
            hits["unknown_src"].append(f"{ent}|cycle{cyc}|src={str(val)[:60]}")


def main():
    t0, th0 = time.process_time(), time.thread_time()
    hits = defaultdict(list)
    all_rows = {}
    cells = rig.cells()
    if "--list" in sys.argv:
        # The M2 enumerator: one line per (cell, entity) pair, entities from the
        # real async_setup_entry of the five platforms, no cycle run.
        for cell, cfg in cells.items():
            hass, entry, _coord = rig.build(cfg)
            for pname, e in rig.entities(hass, entry):
                print(f"{cell} {pname}.{type(e).__name__}")
            rig.dt_util.freeze(None)
        return
    n_pairs = 0
    errs = []
    static = []
    for cell, cfg in cells.items():
        coord, ents, cycles = rig.run_cell(cfg)
        for i, (err, data, rows) in enumerate(cycles):
            if err:
                errs.append(f"{cell}|cycle{i}|{err}")
            check_cycle(cell, i, rows, data, hits)
        (ea, da, ra), (eb, db, rb) = cycles
        for a, b in zip(ra, rb):
            n_pairs += 1
            if a["platform"] != "sensor" or a["state"] is None:
                continue
            if a["state"] == b["state"] and a["available"] and b["available"]:
                pa, va = source(a, da)
                pb, vb = source(b, db)
                moved = pa and pb and va != vb
                static.append(f"{cell}|{a['cls']}|key={a['key']}|src_moved={moved}")
                if moved:
                    hits["stale"].append(f"{cell}|sensor.{a['cls']}|{a['state']!r}|{str(va)[:40]}->{str(vb)[:40]}")
        all_rows[cell] = [[{k: (v if k != "entity" else None) for k, v in r.items()} for r in rows]
                          for _, _, rows in cycles]
    if "--dump" in sys.argv:
        d = tempfile.mkdtemp(prefix="d8s1-matrix-")
        with open(os.path.join(d, "rows.json"), "w") as fh:
            json.dump({"rows": all_rows, "hits": hits, "static": static, "errs": errs}, fh, default=str, indent=1)
        print("dump", d)
    if "-v" in sys.argv:
        for k, v in hits.items():
            for line in v:
                print(f"  {k}: {line}")
        for line in errs:
            print(f"  cycle_error: {line}")
        for line in static:
            print(f"  STATIC {line}")
    print(f"RESULT cells={len(cells)} count")
    print(f"RESULT entity_cell_pairs={n_pairs} count")
    print(f"RESULT cycle_errors={len(errs)} count")
    for k in ("raise", "numeric", "timestamp", "enum", "unit", "serial", "state_len", "attr_bytes", "unknown_src", "stale"):
        print(f"RESULT {k}={len(hits[k])} count")
    print(f"RESULT static_sensor_pairs={len(static)} count")
    ptime = time.process_time() - t0
    try:
        tcpu = time.thread_time() - th0
        print(f"RESULT thread_factor={ptime / max(tcpu, 1e-9):.3f}")
    except Exception:
        pass
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
