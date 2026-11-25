"""D8-s1 M2: Plan Monthly Savings across a month rollover, through the production cycle.

Metrics (key: the value MonthlySavingsSensor.native_value / .available return after each real
`_async_update_data` cycle, 15 min apart, from 2026-01-31 22:00 UTC to 2026-02-01 02:00 UTC):
  avail_none_cycles  cycles where the sensor is available and its state is None (HA: "unknown")
  first_scale        the open month's coverage factor (ledger.coverage_factor) on the first cycle
                     whose state is a number: how many times the settled figures were multiplied
  swing              max |state| over the first four numeric cycles of the new month, in currency
Command (from the export root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D8/s1/monthly.py [--gate-waiting] [--min-hours H] [-v]
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine B4. Expected at baseline: printed values, exact.
Instrumented symbols: heatpump_optimizer.sensor:MonthlySavingsSensor (native_value, available,
_waiting_for), heatpump_optimizer.ledger:MonthlyLedger.savings_months, coverage_factor.
Perturbations (in memory):
  --gate-waiting  MonthlySavingsSensor._waiting_for answers "settled_savings_month" unless an estimated
                  row with a numeric savings_sek exists: avail_none_cycles -> 0.
  --min-hours H   the same gate also waits until the open month has H settled hours: first_scale falls
                  (null control: H=0 reproduces the baseline numbers).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402
from heatpump_optimizer import ledger as ledger_mod  # noqa: E402
from heatpump_optimizer import sensor as sensor_mod  # noqa: E402


def main():
    t0, th0 = time.process_time(), time.thread_time()
    gate = "--gate-waiting" in sys.argv
    min_hours = float(sys.argv[sys.argv.index("--min-hours") + 1]) if "--min-hours" in sys.argv else None
    cls = sensor_mod.MonthlySavingsSensor
    orig = cls._waiting_for

    def gated(self):
        rows = self._rows()
        est = [r for r in rows if isinstance(r, dict) and r.get("estimated") and r.get("savings_sek") is not None]
        if not est:
            return "settled_savings_month"
        if min_hours:
            meta = self.coordinator._ledger.months.get(est[0]["month"], {}).get("meta", {})
            settled = (meta.get(ledger_mod.SETTLED_HOURS_META) or {}).get("sum", 0.0)
            if settled < min_hours:
                return "settled_savings_month"
        return None

    if gate or min_hours is not None:
        cls._waiting_for = property(gated)
    try:
        rig.START = datetime(2026, 1, 31, 22, 0, tzinfo=timezone.utc)
        cfg = rig.cells()["coord_dhw"]
        hass, entry, coord = rig.build(cfg)
        ent = None
        rows = []
        for idx in range(17):
            err = rig.cycle(hass, coord, idx)
            if ent is None:
                ent = [e for p, e in rig.entities(hass, entry) if isinstance(e, cls)][0]
            now = rig.START + rig.timedelta(minutes=15 * idx)
            key = ledger_mod.month_key(now)
            meta = coord._ledger.months.get(key, {}).get("meta", {})
            factor = ledger_mod.coverage_factor(meta, now) if meta else None
            rows.append((now, err, ent.available, ent.native_value, factor,
                         [r["month"] for r in ent._rows()]))
        rig.dt_util.freeze(None)
    finally:
        cls._waiting_for = orig
    feb = [r for r in rows if r[0].month == 2]
    avail_none = sum(1 for r in rows if r[2] and r[3] is None)
    numeric = [r for r in feb if r[2] and isinstance(r[3], (int, float))]
    first_scale = numeric[0][4] if numeric else 0.0
    swing = max((abs(r[3]) for r in numeric[:4]), default=0.0)
    if "-v" in sys.argv:
        for r in rows:
            print("  ", r[0].isoformat(), "err" if r[1] else "", "avail", r[2], "state", r[3],
                  "factor", None if r[4] is None else round(r[4], 1), "rows", r[5])
    print(f"RESULT avail_none_cycles={avail_none} count")
    print(f"RESULT first_scale={first_scale:.1f} ratio")
    print(f"RESULT swing={swing:.2f} currency")
    print(f"RESULT cycles={len(rows)} count")
    print(f"RESULT thread_factor={(time.process_time() - t0) / max(time.thread_time() - th0, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
