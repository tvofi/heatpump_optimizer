"""D2-s2 harness (non-finding): grid-fee windows on the two DST days.

Metric: number of 15-min steps of a local day that grid_fee.GridFeeSchedule
.fee_vector charges the "Mon-Fri 06:00-22:00" surcharge on, over the step grid
coordinator._utc_step_starts builds (true answer 64 on every weekday: 16 local
hours, whatever the day's length), plus the day's total step count.
Command: OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub python3 tools/audit/round8/D2/s2_fee_dst.py
Expected: alldays fee_steps=64 on the 23 h, 25 h and a 24 h day (16 real local hours);
night_wrap 28 / 36 / 32 (7, 9, 8 real hours between 22:00 and 06:00). Exact counts.
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU cloud container.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time
from datetime import datetime
from zoneinfo import ZoneInfo
sys.path.insert(0, ".")
import numpy as np
from custom_components.heatpump_optimizer.coordinator import _utc_step_starts
from custom_components.heatpump_optimizer.grid_fee import GridFeeSchedule

t0p, t0t = time.process_time(), time.thread_time()
TZ = ZoneInfo("Europe/Stockholm")
for rules, tag in (("06:00-22:00 = 0.25", "alldays"), ("22:00-06:00 = 0.10", "night_wrap")):
    sched = GridFeeSchedule.from_config({"grid_fee_mode": "rules", "grid_fee_rules": rules,
                                         "grid_fee_fixed": 0.0})
    for day in ((2026, 3, 29), (2026, 10, 25), (2026, 1, 14)):
        mid = datetime(*day, tzinfo=TZ)
        nxt = datetime(day[0], day[1], day[2] + 1, tzinfo=TZ)
        n = int((nxt.timestamp() - mid.timestamp()) // 900)
        starts = _utc_step_starts(mid, n)
        fee = sched.fee_vector(starts)
        print(f"RESULT {tag}_{day[1]:02d}{day[2]:02d}_steps={n} count")
        print(f"RESULT {tag}_{day[1]:02d}{day[2]:02d}_fee_steps={int(np.sum(fee > 0))} count")
pc_, tc_ = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc_ / max(tc_, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=" + [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1])
