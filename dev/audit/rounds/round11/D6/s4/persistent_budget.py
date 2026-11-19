#!/usr/bin/env python3
"""D6-s4: plan writes the persistent heat-curve arm sends in one local day, per budget.

Metric: number of `heat_curve._send` calls `heat_curve._write_persistent_target` makes in
one local day when the plan asks for a new target every 61 min (dwell 60 min), for a
`heat_curve_persistent_writes_per_day` budget B; plus `total_with_restore` = that + 1 (the
off/unload restore, which off_restore writes unbudgeted and heat_curve counts to the day).
Count key: the production seam's own send calls, never the config value.

The text under test (translations/sv.json, options.step.heat_curve.data_description.
heat_curve_persistent_writes_per_day): "en hålls alltid kvar för den [återställningen]"
and "0 eller 1 skriver ingenting" -- i.e. plan writes <= max(B-1, 0) and B=1 sends 0.

Run:   PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D6/s4/persistent_budget.py
       ... --perturb   (in memory: `writes_today(state, now) + 1 > budget` -> `+ 2 > budget`,
                        the kept-back write the text states; plan_writes_B1 goes to 0)
Expected at baseline 92d38ecb: plan_writes_B0=0, plan_writes_B1=1, plan_writes_B2=2,
plan_writes_B12=12 (exact; counts). With --perturb: 0, 0, 1, 11.
Machine: B13 finder box (linux x86_64), counts are load-immune.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, sys, textwrap, time
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, ".")
from custom_components.heatpump_optimizer import heat_curve as hc  # noqa: E402

PERTURB = "--perturb" in sys.argv
if PERTURB:
    src = textwrap.dedent(inspect.getsource(hc._write_persistent_target))
    old = "writes_today(state, now) + 1 > budget"
    assert src.count(old) == 1, "perturbation site moved"
    # Defined in the module's own namespace, so the harness's patches reach it.
    exec(compile(src.replace(old, "writes_today(state, now) + 2 > budget"), hc.__file__, "exec"), vars(hc))


def day_of_writes(budget):
    clock = [datetime(2026, 1, 14, 0, 30, tzinfo=timezone.utc)]
    sends = []

    async def fake_send(hass, entry, entity_id, target):
        sends.append((clock[0], target))
        return True

    async def fake_true(*a, **k):
        return True

    async def fake_none(*a, **k):
        return None

    cfg = SimpleNamespace(heat_curve_displace_entity="number.curve_parallel_shift",
                          heat_curve_persistent_min_dwell_minutes=60,
                          heat_curve_persistent_writes_per_day=budget)
    state = {"entity_id": cfg.heat_curve_displace_entity}
    fake_dt = SimpleNamespace(utcnow=lambda: clock[0], as_local=lambda t: t,
                              parse_datetime=hc.dt_util.parse_datetime)
    with mock.patch.object(hc, "_send", fake_send), \
         mock.patch.object(hc, "setpoint_step", lambda h, e: 1.0), \
         mock.patch.object(hc, "log_held", lambda *a, **k: False), \
         mock.patch.object(hc, "dt_util", fake_dt), \
         mock.patch.object(hc.off_restore, "async_arm", fake_true), \
         mock.patch.object(hc.off_restore, "async_save_state", fake_none):
        reading = 40.0
        for i in range(22):  # 00:30 .. 21:51, one local (UTC) day
            target = 41.0 if i % 2 == 0 else 40.0
            asyncio.run(hc._write_persistent_target(None, object(), cfg, state, reading, target, "ours"))
            reading = sends[-1][1] if sends else reading
            clock[0] += timedelta(minutes=61)
    return len([s for s in sends if s[0].date() == datetime(2026, 1, 14).date()])


t0p, t0t = time.process_time(), time.thread_time()
for b in (0, 1, 2, 12):
    n = day_of_writes(b)
    print(f"RESULT plan_writes_B{b}={n} count")
    print(f"RESULT total_with_restore_B{b}={n + 1 if n else 0} count")
    print(f"RESULT over_text_B{b}={max(0, n - max(b - 1, 0))} count")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins={sw}")
