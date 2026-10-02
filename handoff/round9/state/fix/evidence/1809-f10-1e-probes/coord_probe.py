"""Four coordinator elapsed/rate-limit sites under a real autumn fold."""

import asyncio
import math
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, "tests")
import numpy as np
from harness import FakeEntry, FakeHass, FakeState
from homeassistant.util import dt as dt_util
from heatpump_optimizer import const
from heatpump_optimizer.freq_control import FREQ_MIN_SAMPLES
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as C

S = ZoneInfo("Europe/Stockholm")
LAST = datetime(2026, 10, 25, 2, 55, tzinfo=S)  # 00:55Z
NOW = datetime(2026, 10, 25, 2, 55, tzinfo=S, fold=1)  # 01:55Z
LAST2 = datetime(2026, 10, 25, 2, 55, tzinfo=S)  # 00:55Z
NOW2 = datetime(
    2026, 10, 25, 2, 5, tzinfo=S, fold=1
)  # 01:05Z -> true 10 min, wall -50 min


def coord(hass=None, **cfg):
    base = {
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
    }
    return C(hass or FakeHass(), FakeEntry(data={**base, **cfg}))


# 1. snow memory
dt_util.freeze(NOW)
c = coord(**{const.CONF_SNOW_ROOF_FACTOR_ENABLED: True})
c._snow_accum_last, c._snow_accum_cm = LAST, 10.0
c._update_snow_memory(NOW, np.zeros(4))
print(
    f"1 snow_accum  observed={c._snow_accum_cm:.6f} expected={10 * math.exp(-1 / 24):.6f}"
)

# 2. async_simulate limiter (no plan -> returns no_plan if the limiter is NOT taken)
dt_util.freeze(NOW)
c = coord()
c._last_simulation = LAST
r = asyncio.run(c.async_simulate({}, limited=True))
print(
    f"2 simulate    observed_rate_limited={r.get('rate_limited')!r} (result={r}) expected_rate_limited=False"
)

# 3. _on_power_event spacing fold
dt_util.freeze(NOW2)
c = coord(
    peak_guard_enabled=True,
    house_power_entity="sensor.house_power",
    main_fuse_amperes=16.0,
    main_fuse_phases=1,
    **{const.CONF_PEAK_TARIFF_ENABLED: True},
)
seen = []
c._peak_tracker.observe = lambda *a, **k: seen.append(k.get("dt_hours", "n/a"))
c._guard_last_fold = LAST2
fuse_only = c._capacity_tariff().enabled
ev = type("E", (), {"data": {"new_state": FakeState("6500", unit="W")}})()
c._on_power_event(ev)
print(
    f"3 spacing     tariff.enabled={fuse_only} observe_calls={seen} "
    f"_guard_last_fold_updated={c._guard_last_fold.timestamp() == NOW2.timestamp()}"
)
print(f"3 spacing     expected dt_h={1 / 6:.6f}")

# 4. _command_frequency limiter
dt_util.freeze(NOW)
hass = FakeHass()
hass.states.set("number.freq", FakeState("45", attributes={"min": 20.0, "max": 120.0}))
c = coord(hass, compressor_freq_entity="number.freq", freq_control_mode="control")
c._measured_power = 2.0
c._current_action = {"power": 1.5, "dhw_power": 0.5}
for _ in range(FREQ_MIN_SAMPLES + 1):
    c._freq_map.observe(45.0, 2.0, 20.0, 120.0)
c._freq_last_write = LAST
asyncio.run(c._command_frequency())
print(
    f"4 freq        observed_service_calls={len(hass.services.calls)} "
    f"expected_service_calls=1 last_write_updated={c._freq_last_write.timestamp() == NOW.timestamp()}"
)
