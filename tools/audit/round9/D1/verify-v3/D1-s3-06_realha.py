"""V3 reach for D1-s3-06 (FrequencyMap admits an unbounded ratio or out-of-range decile) under real HA.

Metric (a) store seam: a trained map (400 folds of 0.04 kW/Hz, 20-100 Hz) saved through
the production QuarantiningStore on a real hass, with ONE bucket ratio set to 1e308
(or a decile key "-2" at 5.0 kW/Hz), re-loaded (real orjson) and FrequencyMap.from_dict;
then 96 truthful folds at the recommended frequency: store_stuck = 1 if recommend()
still delivers < 50 % of a 3 kW target. (b) live seam, outside the finding's
seam_rule: the same trained map folds ONE power reading that a real homeassistant
State (sensor.hp_power = "500", unit kW) delivers through inputs.InputReader.read
(CONF_POWER_ENTITY), at 22 Hz (the lowest decile), via FrequencyMap.observe -- the coordinator's own fold
path; live_folds_to_recover = truthful folds until recommend() delivers >= 50 %
again (cap 2000). Count key: the frequency recommend() returns.

Command:  /root/venvha/bin/python tools/audit/round9/D1/verify-v3/D1-s3-06_realha.py
Control: the same map with no corruption and no glitch (healthy_stuck=0).
Baseline 1936d5ca (+6f51db2c evidence); G1 cloud container; homeassistant 2026.2.3.
"""
import os
_H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D1-1_realha.py")
exec(compile(open(_H).read(), _H, "exec"))

import asyncio
import json
import logging

import numpy as np

logging.disable(logging.CRITICAL)
HZ_MIN, HZ_MAX, K, TARGET = 20.0, 100.0, 0.04, 3.0


async def main():
    hass = await make_hass()
    from heatpump_optimizer.freq_control import FrequencyMap
    from heatpump_optimizer.store import QuarantiningStore
    from heatpump_optimizer.inputs import InputReader
    from heatpump_optimizer.const import CONF_POWER_ENTITY, CONF_STALENESS_ENABLED

    def trained():
        m = FrequencyMap()
        for hz in np.linspace(22, 99, 400):
            m.observe(float(hz), K * float(hz), HZ_MIN, HZ_MAX)
        return m

    def delivered(m):
        rec = m.recommend(TARGET, HZ_MIN, HZ_MAX)
        hz = HZ_MAX if rec is None else float(np.clip(rec, HZ_MIN, HZ_MAX))
        return hz, K * hz

    def stuck_after(m, folds):
        for _ in range(folds):
            hz, _ = delivered(m)
            m.observe(hz, K * hz, HZ_MIN, HZ_MAX)
        return int(delivered(m)[1] < 0.5 * TARGET)

    healthy = stuck_after(trained(), 96)
    store_stuck = 0
    for i, mut in enumerate(("huge_ratio", "neg_key")):
        p = trained().as_dict()
        if mut == "huge_ratio":
            p[sorted(p, key=int)[0]][0] = 1e308
        else:
            p["-2"] = [5.0, 50]
        st = QuarantiningStore(hass, 1, f"v3_freq_{i}")
        await st.async_save({"freq_map": p})
        back = await QuarantiningStore(hass, 1, f"v3_freq_{i}").async_load()
        store_stuck += stuck_after(FrequencyMap.from_dict(back["freq_map"]), 96)
    hass.states.async_set("sensor.hp_power", "500", {"unit_of_measurement": "kW"})
    r = InputReader(hass, {CONF_POWER_ENTITY: "sensor.hp_power", CONF_STALENESS_ENABLED: False},
                    enabled=False).read(CONF_POWER_ENTITY)
    m = trained()
    m.observe(22.0, float(r.value), HZ_MIN, HZ_MAX)
    folds = 0
    while delivered(m)[1] < 0.5 * TARGET and folds < 2000:
        hz, _ = delivered(m)
        m.observe(hz, K * hz, HZ_MIN, HZ_MAX)
        folds += 1
    print(f"# reader_ok={r.ok} delivered_kw={r.value}")
    print(f"RESULT healthy_stuck={healthy} flag")
    print(f"RESULT store_stuck={store_stuck} count_of_2")
    print(f"RESULT live_folds_to_recover={folds} folds")

asyncio.run(main())
tail()
os._exit(0)
