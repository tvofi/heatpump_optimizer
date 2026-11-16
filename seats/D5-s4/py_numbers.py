#!/usr/bin/env python3
"""D5-s4 M4 (C7): executed check of numbers Python comments in the seat's cells cite, against the
production constants they sit on (imported, never read from another comment).
Metric: cited-number checks that fail.  Count key: the imported module attribute's value.
Run:  PYTHONPATH=tests/hastub /root/venv-ci/bin/python3 dev/audit/rounds/round11/D5/s4/py_numbers.py [--perturb]
  --perturb sets pump_arbiter.FEEDBACK_STOP_MARGIN_K = 0.3 in memory: failed goes up by 1.
Expected at 92d38ecb: RESULT checks=11, failed=0 (exact). Machine: box B11. No timing.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time
sys.path.insert(0, ".")
from scipy import stats
from custom_components.heatpump_optimizer import (const, ledger, modbus_prefill, open_meteo, optimizer,  # noqa: E402
                                                 pump_arbiter, quick_setup, slab_seed, store, sysid, tariff)

if "--perturb" in sys.argv:
    pump_arbiter.FEEDBACK_STOP_MARGIN_K = 0.3
C = [
    ("_DAY_BITS: Monday bit 7 .. Sunday bit 1, bit 0 no day", modbus_prefill._DAY_BITS == sum(1 << b for b in range(1, 8))),
    ("_MAX_PLAUSIBLE_GHI ~39 above the 1361 W/m2 solar constant", abs(open_meteo._MAX_PLAUSIBLE_GHI - 1361 - 39) < 1),
    ("_COMFORT_PULL two-zone is half the single-zone", optimizer._COMFORT_PULL_TWO_ZONE * 2 == optimizer._COMFORT_PULL_SINGLE_ZONE),
    ("FEEDBACK_STOP_MARGIN_K is two 0.1 K steps", abs(pump_arbiter.FEEDBACK_STOP_MARGIN_K - 0.2) < 1e-12),
    ("ECHO_GRACE_S past the 8 s window and 1 s debounce", pump_arbiter.ECHO_GRACE_S > 8 + 1),
    ("QUICK_SETUP_BUFFER_VOLUME above BUFFER_STORE_MIN_VOLUME (100 L)", const.BUFFER_STORE_MIN_VOLUME == 100 and quick_setup.QUICK_SETUP_BUFFER_VOLUME > 100),
    ("SLAB_SEED 9 K (29-20, 33-24) plus 3 K margin", slab_seed.SLAB_SEED_MAX_ABOVE_ROOM_K == (29 - 20) + 3 == (33 - 24) + 3),
    ("store.ABSURD above an epoch in ms (1.8e12)", store.ABSURD > time.time() * 1000 and time.time() * 1000 < 1.9e12),
    ("_PROFILE_CHI2_95 is the 95 % chi-square(1) quantile", abs(sysid._PROFILE_CHI2_95 - stats.chi2.ppf(0.95, 1)) < 1e-6),
    ("_Z_975 is the 97.5 % normal quantile", abs(sysid._Z_975 - stats.norm.ppf(0.975)) < 1e-12),
    ("tariff window default 60 min (hourly)", tariff.CapacityTariff.__dataclass_fields__["window_minutes"].default == 60
     if hasattr(tariff, "CapacityTariff") else None),
]
failed = 0
for what, ok in C:
    print(("ok   " if ok else "FAIL ") + what)
    failed += not ok
print(f"RESULT checks={len(C)} count")
print(f"RESULT failed={failed} count")
print(f"RESULT thread_factor={time.process_time() / max(time.thread_time(), 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=" + next((l.split()[1] for l in open('/proc/vmstat') if l.startswith('pswpin')), 'na'))
