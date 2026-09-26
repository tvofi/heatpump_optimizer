"""V3 reach for D1-s2-03 (a sample count past 2**64 in thermal_learning) under real Home Assistant.

Metric: a thermal_learning store file whose cop_baseline["4"][1] is the JSON number
LEAF (default 1e20) is written to the real .storage directory; the REAL coordinator
loads it through its QuarantiningStore (real homeassistant Store, real orjson) with
_async_load_thermal_learning, then _learning_view() -- the per-cycle consumer --
is called 3 times: view_raises = raising calls of 3. Then the production saver
_async_save_thermal_learning runs and the file is re-read: file_still_corrupt=1
if the corrupt leaf survives the save (the store is never overwritten).
producer_max_count = largest count the production folder
(_observe_cop_baseline path: entry[1]) reaches after 500 folds, for scale.
Count key: exceptions out of _learning_view; the leaf read back from disk.

Command:  /root/venvha/bin/python tools/audit/round9/D1/verify-v3/D1-s2-03_realha.py [--leaf 1e20|1e18|100]
Expected: --leaf 1e20 -> view_raises=3, file_still_corrupt=1; --leaf 1e18 (< 2**63) -> view_raises=0.
Baseline 1936d5ca (+6f51db2c evidence); G1 cloud container; homeassistant 2026.2.3.
"""
import os
_H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D1-1_realha.py")
exec(compile(open(_H).read(), _H, "exec"))

import asyncio
import json
import logging

logging.disable(logging.CRITICAL)
LEAF = sys.argv[sys.argv.index("--leaf") + 1] if "--leaf" in sys.argv else "1e20"


async def main():
    hass = await make_hass()
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    from heatpump_optimizer.const import DOMAIN
    entry = make_entry({"indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"},
                       entry_id="v3big")
    key = f"{DOMAIN}_v3big_thermal_learning"
    path = os.path.join(hass.config.path(".storage"), key)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # A post-v5.7.0 store carries house_heat_loss_anchor; without it the loader's own
    # anchor-adoption save rewrites the file before cop_baseline is parsed.
    probe = HeatPumpOptimizerCoordinator(hass, make_entry(dict(entry.data), entry_id="v3probe"))
    anchor = json.dumps(probe._thermal_learning_payload().get("house_heat_loss_anchor"))
    raw = ('{"version": 1, "minor_version": 1, "key": "%s", "data": {"house_heat_loss_anchor": %s, '
           '"cop_baseline": {"4": [3.1, %s]}}}' % (key, anchor, LEAF))
    open(path, "w").write(raw)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    await asyncio.sleep(0.2)
    await coord._async_load_thermal_learning()
    loaded = coord._cop_baseline.get((4, False))
    raises = 0
    for _ in range(3):
        try:
            coord._learning_view()
        except Exception:  # noqa: BLE001
            raises += 1
    await coord._async_save_thermal_learning()
    await asyncio.sleep(0.2)
    disk = json.load(open(path))
    print("# disk_keys", sorted(disk["data"].keys())[:12], "cop_baseline=", disk["data"].get("cop_baseline"))
    back = disk["data"].get("cop_baseline", {}).get("4")
    still = int(back is not None and float(back[1]) >= 2 ** 63)
    print(f"# leaf={LEAF} loaded_entry={loaded} type={type(loaded[1]).__name__ if loaded else None} on_disk_after_save={back}")
    print(f"RESULT view_raises={raises} count_of_3")
    print(f"RESULT file_still_corrupt={still} flag")

asyncio.run(main())
tail()
os._exit(0)
