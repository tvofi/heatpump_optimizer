"""D15.M6: re-run the accuracy monitor over a bundle's accuracy store.

Rebuilds AccuracyTracker from the bundle's stored samples, computes the
production temperature_bias/temperature_mae per calendar day (cumulative
window as the tracker would hold it at day end), folds each day into
SnapshotRing.observe_bias and compares the latch with the recorded one.
Perturbation: --offset C adds C degrees to every actual_temp (bias -C).
Prints counts only (no bundle values beyond aggregates).
"""
import argparse, json, sys
from datetime import datetime
from custom_components.heatpump_optimizer.accuracy import AccuracyTracker
from custom_components.heatpump_optimizer.snapshots import SnapshotRing

ap = argparse.ArgumentParser()
ap.add_argument("--bundle", required=True)
ap.add_argument("--offset", type=float, default=0.0)
a = ap.parse_args()
doc = json.load(open(a.bundle))
dbg = doc.get("data", doc).get("debug", doc.get("debug", doc))
st = dbg["stores"]
acc = next(v for k, v in st.items() if k.endswith("_accuracy"))["accuracy"]
snap = next((v for k, v in st.items() if k.endswith("_snapshots")), {})
samples = [dict(s) for s in acc["samples"]]
for s in samples:
    if a.offset and s.get("actual_temp") is not None:
        s["actual_temp"] += a.offset
days = sorted({s["t"][:10] for s in samples})
ring = SnapshotRing()
for day in days:
    upto = [s for s in samples if s["t"][:10] <= day]
    tr = AccuracyTracker.from_dict({"samples": upto})
    now = datetime.fromisoformat(max(s["t"] for s in upto))
    b, m = tr.temperature_bias(), tr.temperature_mae()
    ring.observe_bias(now, b, True)
    print(f"day={day} n={len(tr.samples)} bias={b} mae={m} bias_days={ring._bias_days} alarmed={ring.alarmed}")
full = AccuracyTracker.from_dict({"samples": samples})
print(f"window bias={full.temperature_bias()} mae={full.temperature_mae()} samples={len(full.samples)}")
print(f"recorded alarmed={snap.get('alarmed')} bias_days={snap.get('bias_days')}")
print(f"RERUN alarmed={ring.alarmed} agree={ring.alarmed == bool(snap.get('alarmed'))}")
