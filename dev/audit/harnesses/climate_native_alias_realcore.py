#!/usr/bin/env python3
"""Read the climate entity's published temperatures on a real Home Assistant core.

WHY IT EXISTS. Home Assistant 2026.11 serves the climate temperatures under
the native names and logs, at class creation, every class still defining the
old ones; the supported floor (2025.2.0) reads only the old ones. The
pre-native alias in ``HeatPumpOptimizerEntity`` (R10-OUTSIDE-CLIMATE-NATIVE-TEMP)
must leave what the entity publishes unchanged on both and silence that log on
the newer. ``tests/finite_boundary.py`` drives stub bases; this reads the real
``ClimateEntity`` of whichever core the interpreter has installed.

It prints one JSON line: the core version, the temperature attributes the
entity publishes (``capability_attributes`` and ``state_attributes``) under
the metric and the US-customary unit system for a measured indoor reading and
a NaN one, and every log line naming a deprecated member. Compare the line
for two trees under one core; byte-identical attributes and the deprecation
lines are the measurement.

    uv venv -p 3.13 v2502 && VIRTUAL_ENV=v2502 uv pip install homeassistant==2025.2.0 numpy scipy
    uv venv -p 3.14 v2611 && VIRTUAL_ENV=v2611 uv pip install homeassistant==2026.11.1 numpy scipy paho-mqtt
    git archive <rev> custom_components | tar -x -C <dir>
    (cd /tmp && v2611/bin/python -I <repo>/dev/audit/harnesses/climate_native_alias_realcore.py <dir>/custom_components)
"""
import json
import logging
import math
import sys
import types

sys.path.insert(0, sys.argv[1])
lines: list[str] = []


class _Capture(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        lines.append(record.getMessage())


logging.getLogger().addHandler(_Capture())
logging.getLogger().setLevel(logging.WARNING)

import homeassistant.const as hc  # noqa: E402
from homeassistant.util.unit_system import METRIC_SYSTEM, US_CUSTOMARY_SYSTEM  # noqa: E402

from heatpump_optimizer import climate  # noqa: E402

KEYS = ("current_temperature", "temperature", "min_temp", "max_temp", "target_temp_step")
out: dict[str, object] = {"core": hc.__version__}
for indoor in (20.5, float("nan")):
    for units in (METRIC_SYSTEM, US_CUSTOMARY_SYSTEM):
        ent = object.__new__(climate.HeatPumpOptimizerClimate)
        ent.coordinator = types.SimpleNamespace(
            data={"reading_ok": {"upper_floor_temperature": True}, "indoor_temperature": indoor},
            last_update_success=True, target_temperature=21.0, mode="optimizer")
        ent.hass = types.SimpleNamespace(config=types.SimpleNamespace(units=units))
        try:
            attrs = {**ent.capability_attributes, **ent.state_attributes}
            read: object = {k: attrs[k] for k in KEYS if k in attrs}
        except Exception as exc:  # the measured breakage is a reading, not a crash
            read = f"{type(exc).__name__}: {exc}"
        out[f"{'nan' if math.isnan(indoor) else indoor} {units._name}"] = read
out["deprecation_lines"] = [line for line in lines if "provides the deprecated" in line]
print(json.dumps(out, sort_keys=True, default=str))
