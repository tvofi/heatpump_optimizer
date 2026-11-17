#!/usr/bin/env python3
"""D15-s1 M4: store.DOMAINS declares less than the writers write, and one reader drops on it.

Metric (one line): (a) debug-ring rows the debug store's loader (debugger._kept) keeps out of
the rows debugger.cycle_row writes, one per accuracy sample the bundle's accuracy store holds
(each sample restored through AccuracyTracker.from_dict, as a restart restores it); (b)
store.off_domain field count over documents a released writer wrote and whose own loader
reads them intact.
Count key: len(debugger._kept(...)) -- what the production loader keeps -- and
store.off_domain's list length; never a bundle field rewritten by this harness.
Counts and DOMAINS names only: no bundle value is printed. Never commit a bundle.

Command (export root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D15/s1/domains_drift.py \
        [--bundle B] [--synthetic S] [--declare]
``--synthetic`` omitted: tools/replay/dbg_bundle_gen.py --days 7 is run into a temp dir.
Expected at the baseline:
    unit arm: sample_none_cost_admitted=0 (a sample the coordinator writes when no price covered
        the interval, #2229, is outside DOMAINS), its row kept 0/1;
    synthetic: store_samples_unpriced=192/192, written_rows_kept=0/192, off_domain[accuracy]=192;
    real (owner's 2026-11-16 download): store_samples_unpriced=0/192, written_rows_kept=192/192,
        cycle_rows_kept=662/662 (every interval priced: the null control), off_domain[off_restore]=1
        with off_restore_loader_keeps=2/2, off_domain[snapshots]=101 (legacy learner keys).
Perturbation: --declare (DOMAINS, in memory: accuracy samples' predicted_cost nullable as
    actual_cost already is; off_restore's armed entry also declared as the mapping its writer
    stores) -> synthetic written_rows_kept 0 -> 192 (up), unit arm 0 -> 1, real
    off_domain[off_restore] 1 -> 0 (to_zero).
Null control: the real bundle, every interval priced: its rows kept in full with or without --declare.
Note: dbg_bundle_gen.py's own cycle_rows are not debugger.cycle_row's (they carry None fields
    cycle_row omits), so the rows arm writes its rows through cycle_row rather than reading those.
Baseline SHA: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: macOS arm64, CI venv 3.14.
Instrumented symbols: debugger:_kept, debugger:cycle_row, accuracy:AccuracyTracker.from_dict,
    accuracy:AccuracySample.as_dict, store:admitted, store:off_domain, off_restore:_entry_of.
Seam rule: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D15/s1/store_replay.py --bundle B
    (off_domain per store over a production-written bundle; each nonzero row is a seam).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components", ROOT / "tools" / "replay"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import debug_ingest  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import debugger, off_restore  # noqa: E402
from heatpump_optimizer import store as S  # noqa: E402
from heatpump_optimizer.accuracy import AccuracySample, AccuracyTracker  # noqa: E402


def declare() -> None:
    S.DOMAINS["accuracy"]["accuracy/samples/#/predicted_cost"] = S.Domain("real", null=True)
    S.DOMAINS["off_restore"]["armed/*/entity_id"] = S.Domain("text")
    S.DOMAINS["off_restore"]["armed/*/value"] = S.Domain("real")


def unit_arm() -> None:
    sample = AccuracySample(when=datetime(2026, 1, 15, 12, tzinfo=timezone.utc), predicted_power_kw=1.0,
                            actual_power_kw=1.1, predicted_temp=20.0, actual_temp=20.1,
                            predicted_cost=None, actual_cost=None, outdoor_temp=-3.0).as_dict()
    ok = S.admitted("accuracy", {"accuracy": {"samples": [sample]}})
    row = {"t": sample["t"], "accuracy_sample": sample, "version": "x"}
    kept = debugger._kept({"rows": [row]}, "rows", {"t"})
    print(f"RESULT sample_none_cost_admitted={int(ok)} unit=bool")
    print(f"RESULT unit_row_kept={len(kept)}/1 unit=rows")


def written_rows(bundle: dict) -> tuple[int, int, int]:
    """(unpriced samples, rows written, rows the debug loader keeps): one debugger.cycle_row per
    sample the bundle's accuracy store holds, restored through the production loader."""
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    acc = next((v for k, v in (bundle.get("stores") or {}).items() if S.store_name(k) == "accuracy"), {})
    tracker = AccuracyTracker.from_dict(acc.get("accuracy", acc))
    coord = HeatPumpOptimizerCoordinator(FakeHass({}), FakeEntry(data={
        "tibber_token": "x", "weather_entity": "weather.home", "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor"}))
    coord.integration_version = "harness"
    rows = []
    for sample in list(tracker.samples):
        coord._accuracy.samples.clear()
        coord._accuracy.samples.append(sample)
        rows.append(debugger.cycle_row(coord, {"mode": "auto"}, sample.when, 1.0))
    unpriced = sum(1 for s in tracker.samples if s.predicted_cost is None)
    return unpriced, len(rows), len(debugger._kept({"rows": rows}, "rows", {"t"}))


def bundle_arm(tag: str, path: Path) -> None:
    bundle = debug_ingest.load_bundle(path)
    unpriced, written, kept_w = written_rows(bundle)
    print(f"RESULT {tag}_store_samples_unpriced={unpriced}/{written} unit=samples")
    print(f"RESULT {tag}_written_rows_kept={kept_w}/{written} unit=rows")
    if tag == "real":
        rows = bundle.get("cycle_rows") or []
        print(f"RESULT {tag}_cycle_rows_kept={len(debugger._kept({'rows': rows}, 'rows', {'t'}))}/{len(rows)} unit=rows")
    stores = {S.store_name(k): (k, v) for k, v in (bundle.get("stores") or {}).items() if S.store_name(k)}
    for name in sorted(stores):
        key, doc = stores[name]
        off = S.off_domain(key, doc)
        if off:
            print(f"RESULT {tag}_off_domain[{name}]={len(off)} unit=fields")
    if "off_restore" in stores:
        armed = (stores["off_restore"][1] or {}).get("armed") or {}
        kept_armed = sum(1 for v in armed.values() if off_restore._entry_of(v) == v)
        print(f"RESULT {tag}_off_restore_loader_keeps={kept_armed}/{len(armed)} unit=entries")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", type=Path)
    ap.add_argument("--synthetic", type=Path)
    ap.add_argument("--declare", action="store_true")
    a = ap.parse_args()
    c0, t0 = time.process_time(), time.thread_time()
    if a.declare:
        declare()
    unit_arm()
    synth = a.synthetic
    if synth is None:
        out = Path(tempfile.mkdtemp())
        subprocess.run([sys.executable, str(ROOT / "tools/replay/dbg_bundle_gen.py"), "--days", "7", "--out", str(out)],
                       check=True, capture_output=True, env=dict(os.environ, PYTHONPATH="tests/hastub:tests"))
        synth = out / "bundle.json"
    bundle_arm("synthetic", synth)
    if a.bundle:
        bundle_arm("real", a.bundle)
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
