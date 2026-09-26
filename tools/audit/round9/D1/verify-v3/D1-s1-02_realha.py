"""V3 reach for D1-s1-02 (non-numeric snapshot temperature_bias) under real Home Assistant.

Metric: of 4 non-numeric bias leaves ("0.3", "garbage", [0.3], {"v":0.3}) saved and
re-loaded through the production QuarantiningStore (a real homeassistant Store
subclass, real orjson), the count for which SnapshotRing.from_dict(...).best_restore()
raises; plus producer_nonnumeric = 1 if AccuracyTracker.summary()'s
temperature_bias (the only producer of the leaf) is anything but float/None.
Count key: exceptions out of best_restore.

Command:  /root/venvha/bin/python tools/audit/round9/D1/verify-v3/D1-s1-02_realha.py [--control]
Expected: restore_raises=4, producer_nonnumeric=0; --control (numeric 0.3 leaf): restore_raises=0.
Baseline 1936d5ca (+6f51db2c evidence); G1 cloud container; homeassistant 2026.2.3.
"""
import os
_H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D1-1_realha.py")
exec(compile(open(_H).read(), _H, "exec"))

import asyncio
import logging

logging.disable(logging.CRITICAL)
CONTROL = "--control" in sys.argv


async def main():
    hass = await make_hass()
    from homeassistant.util import dt as dt_util
    from heatpump_optimizer.store import QuarantiningStore
    from heatpump_optimizer.snapshots import SnapshotRing
    from heatpump_optimizer.accuracy import AccuracyTracker

    variants = [0.3] if CONTROL else ["0.3", "garbage", [0.3], {"v": 0.3}]
    raises = 0
    for i, bias in enumerate(variants):
        snap = {"taken_at": dt_util.now().isoformat(), "healthy": True, "alarmed_at_capture": False,
                "accuracy": {"temperature_bias": bias}, "learners": {}}
        st = QuarantiningStore(hass, 1, f"v3_snap_{i}")
        await st.async_save({"snapshots": [snap]})
        data = await QuarantiningStore(hass, 1, f"v3_snap_{i}").async_load()
        ring = SnapshotRing.from_dict(data)
        try:
            ring.best_restore()
        except Exception:  # noqa: BLE001
            raises += 1
    b = AccuracyTracker().summary().get("temperature_bias")
    producer_bad = int(not (b is None or isinstance(b, float)))
    print(f"# arm={'control' if CONTROL else 'default'} variants={len(variants)}")
    print(f"RESULT restore_raises={raises} count_of_{len(variants)}")
    print(f"RESULT producer_nonnumeric={producer_bad} flag")

asyncio.run(main())
tail()
os._exit(0)
