#!/usr/bin/env python3
"""D15-s1 M4: a capacity-envelope bucket the fold writes is dropped by its own loader.

Metric (one line): buckets of ``_capacity_envelope`` after a save/load round trip
(``_thermal_learning_payload`` -> ``_load_t4b_learners`` on a fresh coordinator), against
the buckets the fold wrote; ``lost`` = written - reloaded.
Count key: len(coordinator._capacity_envelope) as the production loader leaves it, never
the stored document's own fields.

Command (export root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D15/s1/capacity_envelope.py \
        [--bundle B] [--nameplate] [--loader-accepts-zero]
Expected at the baseline: fold_written=1, reloaded=0, lost=1 (exact) for a measured
    heat_kw at partial load; bundle arm (owner's 2026-11-16 download): bundle_stored=1,
    bundle_zero_count=1, bundle_reloaded=0.
Perturbations: --nameplate (commanded power at nameplate, so the fold counts the sample)
    -> lost 1 -> 0 (to_zero); --loader-accepts-zero (coordinator._learned_pair accepts a
    count of 0, the one-line loader edit) -> lost 1 -> 0 and bundle_reloaded 0 -> 1.
Null control: --nameplate, the arm where the fold writes count 1 and the loader keeps it.
Baseline SHA: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: macOS arm64, CI venv 3.14.
Instrumented symbols: coordinator:HeatPumpOptimizerCoordinator._fold_capacity_envelope,
    coordinator:HeatPumpOptimizerCoordinator._thermal_learning_payload,
    coordinator:HeatPumpOptimizerCoordinator._load_t4b_learners, coordinator:_learned_pair.
Seam rule: grep -nE "setdefault\\([^)]*\\[[^]]*, *0\\]\\)" custom_components/heatpump_optimizer/*.py
    (each fold seeding a [value, 0] pair) against the loader its store key reaches.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path.cwd()
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components", ROOT / "tools" / "replay"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import numpy as np  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer import store as S  # noqa: E402

CFG = {"tibber_token": "x", "weather_entity": "weather.home", "indoor_temp_entity": "sensor.indoor",
       "outdoor_temp_entity": "sensor.outdoor", "capacity_curve_enabled": True}


def coordinator():
    return coord_mod.HeatPumpOptimizerCoordinator(FakeHass({}), FakeEntry(data=dict(CFG)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", type=Path)
    ap.add_argument("--nameplate", action="store_true")
    ap.add_argument("--loader-accepts-zero", action="store_true")
    a = ap.parse_args()
    c0, t0 = time.process_time(), time.thread_time()
    original_pair = coord_mod._learned_pair
    if a.loader_accepts_zero:
        def accepts_zero(entry):
            value, count = float(entry[0]), coord_mod._storable_sample_count(entry[1])
            if not (np.isfinite(value) and value > 0 and count >= 0):
                raise ValueError("not a fold")
            return [value, count]
        coord_mod._learned_pair = accepts_zero
    try:
        c = coordinator()
        c._measured_power = 1.5
        p_max = float(c._thermal_params.max_electrical_power)
        if a.nameplate:
            c._commanded_power = lambda: p_max
        else:
            c._commanded_power = lambda: 0.4 * p_max
        c._fold_capacity_envelope(3.0, heat_kw=4.2)
        written = len(c._capacity_envelope)
        written_zero = sum(1 for v in c._capacity_envelope.values() if int(v[1]) == 0)
        payload = json.loads(json.dumps(c._thermal_learning_payload()))
        fresh = coordinator()
        fresh._load_t4b_learners(payload)
        reloaded = len(fresh._capacity_envelope)
        print(f"RESULT fold_written={written} unit=buckets")
        print(f"RESULT fold_written_count_zero={written_zero} unit=buckets")
        print(f"RESULT reloaded={reloaded} unit=buckets")
        print(f"RESULT lost={written - reloaded} unit=buckets")
        print(f"RESULT store_off_domain={len(S.off_domain('x_thermal_learning', payload))} unit=fields")
        if a.bundle:
            doc = json.loads(a.bundle.read_text())
            data = doc.get("data") if isinstance(doc.get("data"), dict) else doc
            bundle = data.get("debug", data)
            tl = next((v for k, v in (bundle.get("stores") or {}).items() if S.store_name(k) == "thermal_learning"), {})
            env = tl.get("capacity_envelope") or {}
            b = coordinator()
            b._load_t4b_learners(tl)
            print(f"RESULT bundle_stored={len(env)} unit=buckets")
            print(f"RESULT bundle_zero_count={sum(1 for v in env.values() if isinstance(v, list) and len(v) > 1 and v[1] == 0)} unit=buckets")
            print(f"RESULT bundle_reloaded={len(b._capacity_envelope)} unit=buckets")
            snaps = next((v for k, v in (bundle.get("stores") or {}).items() if S.store_name(k) == "snapshots"), {})
            zs = sum(1 for s in snaps.get("snapshots") or []
                     for v in (((s.get("learners") or {}).get("thermal_learning") or {}).get("capacity_envelope") or {}).values()
                     if isinstance(v, list) and len(v) > 1 and v[1] == 0)
            print(f"RESULT bundle_snapshot_zero_count_buckets={zs} unit=buckets")
    finally:
        coord_mod._learned_pair = original_pair
    tc = time.thread_time() - t0
    print(f"RESULT thread_factor={((time.process_time() - c0) / tc) if tc > 0 else 1.0:.3f} unit=ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} unit=load")
    try:
        out = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
        sw = int(next(l for l in out.splitlines() if l.startswith("Swapins")).split(":")[1].strip(" ."))
    except Exception:  # noqa: BLE001
        sw = -1
    print(f"RESULT swapins={sw} unit=count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
