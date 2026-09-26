"""V3 reach for D1-s1-01 (tz-naive persisted timestamp) under real Home Assistant.

Metric: (a) naive_written = count of timestamp leaves the three production
producers (SnapshotRing.take, CurveLearner.record_day->_step_down,
ComfortLearner.record_override) write under real HA's dt_util.now(), of 3;
(b) store_keeps_naive = 1 if a naive ISO leaf survives a real
homeassistant.helpers.storage.Store save/load round trip unchanged;
(c) consumer_raises = raising calls of SnapshotRing.due / CurveLearner._step_down /
ComfortLearner._decay over 21 real-clock days after loading a naive leaf (of 63);
(d) extra_seam_raises = raising calls of coordinator._update_snow_memory with a
naive stored snow_accum_last (a seam OUTSIDE the finding's seam_rule), of 21.
Count key: exceptions out of the production call.

Command:  /root/venvha/bin/python tools/audit/round9/D1/verify-v3/D1-s1-01_realha.py [--aware]
Expected: naive_written=0, store_keeps_naive=1, consumer_raises=63, extra_seam_raises=21;
          --aware (perturbation: leaf written aware): consumer_raises=0, extra_seam_raises=0.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence 6f51db2c);
machine: G1 cloud container, 4 vCPU, Python 3.14.0rc2, homeassistant 2026.2.3.
"""
import os
_H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D1-1_realha.py")
exec(compile(open(_H).read(), _H, "exec"))

import asyncio
import logging
from datetime import timedelta
from types import SimpleNamespace

import numpy as np

logging.disable(logging.CRITICAL)
AWARE = "--aware" in sys.argv


async def main():
    hass = await make_hass()
    from homeassistant.util import dt as dt_util
    from homeassistant.helpers.storage import Store
    from heatpump_optimizer.snapshots import SnapshotRing
    from heatpump_optimizer.curve_learning import CurveLearner, DAYS_PER_STEP
    from heatpump_optimizer.comfort_learning import ComfortLearner, OverrideEvent
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    from heatpump_optimizer.const import CONF_SNOW_ROOF_FACTOR_ENABLED

    now0 = dt_util.now()
    # (a) producers under the real clock
    ring = SnapshotRing(); ring.take(now0, {}, {}, True)
    cl = CurveLearner()
    for d in range(DAYS_PER_STEP + 1):
        cl.record_day(now0 + timedelta(days=d), 5.0)
    co = ComfortLearner(configured_weight=1.0, learned_weight=1.0)
    co.record_override(OverrideEvent(when=now0, delta_c=1.0, indoor_temp=20.0, planned_setpoint=21.0))
    stamps = [ring.as_dict()["snapshots"][-1]["taken_at"], cl._last_step_at, co.as_dict()["last_update"]]
    from datetime import datetime
    naive_written = sum(datetime.fromisoformat(s).tzinfo is None for s in stamps)

    # (b) the real Store keeps whatever string it is given
    past = (now0 - timedelta(days=30))
    leaf = past.isoformat() if AWARE else past.replace(tzinfo=None).isoformat()
    st = Store(hass, 1, "v3_naive_probe")
    await st.async_save({"t": leaf})
    loaded = await Store(hass, 1, "v3_naive_probe").async_load()
    store_keeps = int(loaded["t"] == leaf and ("+" not in leaf[19:]) == (not AWARE))

    # (c) consumers over 21 real-clock days
    raises = 0
    ring = SnapshotRing.from_dict({"snapshots": [{"taken_at": leaf, "learners": {}, "accuracy": {}}]})
    cl = CurveLearner.from_dict({"last_step_at": leaf, "comfortable_days": 0})
    co = ComfortLearner.from_dict({"configured_weight": 1.0, "last_update": leaf}, 1.0)
    for d in range(21):
        now = now0 + timedelta(days=d)
        for fn in (lambda: ring.due(now), lambda: cl._step_down(now), lambda: co._decay(now)):
            try:
                fn()
            except TypeError:
                raises += 1
    # (d) a sibling seam the seam_rule does not list
    extra = 0
    for d in range(21):
        fake = SimpleNamespace(_config={CONF_SNOW_ROOF_FACTOR_ENABLED: True},
                               _snow_accum_last=datetime.fromisoformat(leaf),
                               _snow_accum_cm=0.0, _last_heavy_snow=None)
        try:
            HeatPumpOptimizerCoordinator._update_snow_memory(fake, now0 + timedelta(days=d), np.array([0.1]))
        except TypeError:
            extra += 1
    print(f"# arm={'aware' if AWARE else 'naive'} stamps={stamps}")
    print(f"RESULT naive_written={naive_written} count_of_3")
    print(f"RESULT store_keeps_naive={store_keeps} flag")
    print(f"RESULT consumer_raises={raises} count_of_63")
    print(f"RESULT extra_seam_raises={extra} count_of_21")

asyncio.run(main())
tail()
os._exit(0)
