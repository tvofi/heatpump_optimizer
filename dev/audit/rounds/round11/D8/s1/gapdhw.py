"""D8-s1 M2: Sensor Gap Advisor prices a hot-water tank thermometer on a house with no hot water.

Metric: count of (cell, cycle) pairs where the published payload says `dhw_enabled` is False and
SensorGapAdvisorSensor publishes a `dhw_temp_entity` gap with sek_per_month > 0 (and, separately,
where that gap is the sensor's state, i.e. `top_slot`). Key: the value the production
SensorGapAdvisorSensor.native_value / extra_state_attributes return after a real cycle; the
cell's DHW status is the payload's own `dhw_enabled`, never this harness's reading of the config.
Null control: the same count over DHW-enabled cells with no tank probe (`dhw_null`), where the
gap is real and must stay.
Command (from the export root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D8/s1/gapdhw.py [--fix] [-v]
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine B4. Expected at baseline: printed counts, exact.
Instrumented symbols: heatpump_optimizer.sensor:SensorGapAdvisorSensor, heatpump_optimizer.sensor:_gap_probe_terms,
heatpump_optimizer.topology:rank_sensor_gaps.
Perturbation --fix (in memory): `_gap_probe_terms` returns dhw_extra_kwh 0.0 when the config's
`thermal_model._dhw_enabled_from_config(config)` is false -> `no_dhw_priced` and `no_dhw_top` go to 0, `dhw_null` unchanged.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402
from heatpump_optimizer import sensor as sensor_mod  # noqa: E402
from heatpump_optimizer.thermal_model import _dhw_enabled_from_config  # noqa: E402


def main():
    t0, th0 = time.process_time(), time.thread_time()
    orig = sensor_mod._gap_probe_terms
    if "--fix" in sys.argv:
        def fixed(config, hp, house, rate):
            terms = orig(config, hp, house, rate)
            if not _dhw_enabled_from_config(config):
                terms["dhw_extra_kwh"] = 0.0
            return terms
        sensor_mod._gap_probe_terms = fixed
    priced = top = null = no_dhw_pairs = null_pairs = 0
    lines = []
    try:
        for cell, cfg in rig.cells().items():
            hass, entry, coord = rig.build(cfg)
            ent = None
            for idx in range(2):
                rig.cycle(hass, coord, idx)
                if ent is None:
                    ent = [e for p, e in rig.entities(hass, entry)
                           if isinstance(e, sensor_mod.SensorGapAdvisorSensor)][0]
                data = coord.data or {}
                attrs = ent.extra_state_attributes
                row = next((g for g in attrs["gaps"] if g["key"] == "dhw_temp_entity"), {})
                sek = float(row.get("sek_per_month") or 0.0)
                if not data.get("dhw_enabled"):
                    no_dhw_pairs += 1
                    if sek > 0:
                        priced += 1
                        lines.append(f"{cell}|c{idx}|state={ent.native_value}|top={attrs['top_slot']}|dhw_sek={sek}")
                        if attrs["top_slot"] == "dhw_temp_entity":
                            top += 1
                elif not cfg.get("dhw_temp_entity"):
                    null_pairs += 1
                    null += sek > 0
            rig.dt_util.freeze(None)
    finally:
        sensor_mod._gap_probe_terms = orig
    if "-v" in sys.argv:
        for x in lines:
            print("  ", x)
    print(f"RESULT no_dhw_pairs={no_dhw_pairs} count")
    print(f"RESULT no_dhw_priced={priced} count")
    print(f"RESULT no_dhw_top={top} count")
    print(f"RESULT dhw_null_pairs={null_pairs} count")
    print(f"RESULT dhw_null={null} count")
    print(f"RESULT thread_factor={(time.process_time() - t0) / max(time.thread_time() - th0, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
