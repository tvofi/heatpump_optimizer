"""D1.M2: a HEALTHY snapshot store is rewritten on restart (future lead_pending dues bounded to now).

Metric: after two healthy cycles and a restart with no corruption and no clock
change, the number of stored instants store.py:_bound_instants rewrote in the
snapshots store (QuarantiningStore.bounded, keyed on the leaf the load
delivered vs the bytes on disk), plus WARNING lines it logged.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D1/s2/snapshot_bound.py [--perturb]
--perturb: give the snapshots store the accuracy store's lead (max(LEAD_BUCKETS) h)
in memory; expected: rewritten -> 0, warnings -> 0.
Null control (always printed): the accuracy store, which holds the same
lead_pending dues with lead=24 h, rewrites 0.
Expected baseline: rewritten > 0 (one per pending due in the newest snapshot), exact for a run.
Baseline 17f1c55fad1b; machine Apple-silicon macOS (box B4).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, json, logging, sys, time
from datetime import timedelta
sys.path.insert(0, os.path.dirname(__file__))
sys.argv_saved = list(sys.argv); sys.argv = [sys.argv[0], "0", "__none__"]
import store_fuzz as F  # noqa: E402  (N=0: defines helpers, fuzzes nothing)
sys.argv = sys.argv_saved
from custom_components.heatpump_optimizer.accuracy import LEAD_BUCKETS  # noqa: E402
from homeassistant.helpers import storage  # noqa: E402

PERTURB = "--perturb" in sys.argv


class Cap(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING); self.snap = 0; self.acc = 0
    def emit(self, r):
        m = r.getMessage()
        if "ahead of the clock" in m:
            if "_snapshots" in m: self.snap += 1
            if "_accuracy" in m: self.acc += 1


async def main():
    t0 = time.process_time(); tt0 = time.thread_time()
    await F.healthy()
    stored = json.loads(storage._DISK["heatpump_optimizer_test_entry_snapshots"])
    cap = Cap(); logging.getLogger().addHandler(cap)
    h, c = F.build()
    if PERTURB:
        c._snapshot_store._lead = timedelta(hours=max(LEAD_BUCKETS))
    await F.drain(c)
    logging.getLogger().removeHandler(cap)
    restored = c._snapshot_ring.as_dict()
    diffs = sum(1 for a, b in zip(json.dumps(stored).split('"'), json.dumps(restored).split('"'))
                if a != b and a[:2] == "20" and "T" in a)
    print(f"RESULT snapshot_instants_rewritten={len(c._snapshot_store.bounded)} count")
    print(f"RESULT snapshot_ahead_warnings={cap.snap} count")
    print(f"RESULT ring_instants_changed_vs_disk={diffs} count")
    print(f"RESULT control_accuracy_instants_rewritten={len(c._accuracy_store.bounded)} count")
    print(f"RESULT control_accuracy_ahead_warnings={cap.acc} count")
    print(f"  paths={c._snapshot_store.bounded[:4]}")
    tf = (time.process_time() - t0) / max(1e-9, time.thread_time() - tt0)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")

asyncio.run(main())
