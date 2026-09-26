"""V3 reach for D1-s1-04 (a timestamp written while the clock ran ahead) under real Home Assistant.

Metric: per seam, the first day index (1-day steps from real HA's corrected
dt_util.now()) at which the production consumer acts, when the stamp was WRITTEN
by the production producer itself (Cusum.update, SnapshotRing.take,
CurveLearner._step_down via record_day) at a clock AHEAD days fast, saved and
re-loaded through a real homeassistant Store (orjson). Count key: the production
consumer's return (release_if_starved True / due True / bias moved).

Command:  /root/venvha/bin/python tools/audit/round9/D1/verify-v3/D1-s1-04_realha.py [--ahead N]
Expected: --ahead 0 -> 4/8/2 (designed timeouts); --ahead 30 -> 33/37/31 if real HA
adds no guard (the finder's stub numbers).
Baseline 1936d5ca (+6f51db2c evidence); G1 cloud container; homeassistant 2026.2.3.
"""
import os
_H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D1-1_realha.py")
exec(compile(open(_H).read(), _H, "exec"))

import asyncio
import logging
from datetime import timedelta

logging.disable(logging.CRITICAL)
AHEAD = int(sys.argv[sys.argv.index("--ahead") + 1]) if "--ahead" in sys.argv else 30
CAP = 400


async def main():
    hass = await make_hass()
    from homeassistant.util import dt as dt_util
    from homeassistant.helpers.storage import Store
    from heatpump_optimizer.drift import Cusum
    from heatpump_optimizer.snapshots import SnapshotRing
    from heatpump_optimizer.curve_learning import CurveLearner, DAYS_PER_STEP
    from heatpump_optimizer.coordinator import VENT_CUSUM_STARVE_HOURS

    now0 = dt_util.now()
    fast = now0 + timedelta(days=AHEAD)
    c = Cusum(threshold=5.0, drift=0.1)
    c.update(fast, 6.0)                         # trips, last_fed = fast clock
    ring = SnapshotRing(); ring.take(fast, {}, {}, True)
    cl = CurveLearner(bias=-1.0)
    for d in range(DAYS_PER_STEP):              # a step lands on the fast clock
        cl.record_day(fast - timedelta(days=DAYS_PER_STEP - 1 - d), 5.0)
    st = Store(hass, 1, "v3_clock")
    await st.async_save({"c": c.as_dict(), "r": ring.as_dict(), "l": cl.as_dict()})
    data = await Store(hass, 1, "v3_clock").async_load()
    c2 = Cusum(threshold=5.0, drift=0.1); c2.load(data["c"])
    r2 = SnapshotRing.from_dict(data["r"])
    l2 = CurveLearner.from_dict(data["l"]); l2._last_day = ""
    before = l2.bias

    def first(pred):
        for d in range(CAP):
            if pred(now0 + timedelta(days=d)):
                return d
        return CAP
    cus = first(lambda n: c2.release_if_starved(n, VENT_CUSUM_STARVE_HOURS))
    snp = first(lambda n: r2.due(n))
    crv = first(lambda n: (l2.record_day(n, 5.0), l2.bias != before)[1])
    print(f"# ahead={AHEAD} tripped={c.tripped} starve_h={VENT_CUSUM_STARVE_HOURS} last_fed={data['c']['last_fed']}")
    print(f"RESULT cusum_release_day={cus} day_index")
    print(f"RESULT snapshot_due_day={snp} day_index")
    print(f"RESULT curve_step_day={crv} day_index")

asyncio.run(main())
tail()
os._exit(0)
