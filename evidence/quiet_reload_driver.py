"""Reviewer-built driver (r9c-rev-2025), not the finder's: a quiet-only
set_thermal_parameters call, then the update listener, then a coordinator
rebuilt from the entry as the reload would build it. Prints RESULT lines.
Usage: python3 quiet_reload_driver.py <repo root>"""
import asyncio, sys, pathlib
from datetime import datetime, UTC
root = pathlib.Path(sys.argv[1]).resolve()
for p in ("tests/hastub", "tests", "custom_components"):
    sys.path.insert(0, str(root / p))
from harness import FakeHass, FakeEntry  # noqa
from heatpump_optimizer import const, quiet_windows
import heatpump_optimizer as integration
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as C

CALL = {"quiet_off_windows": "09:00-09:30", "silent_mode_power_fraction": 0.8}
if len(sys.argv) > 2 and sys.argv[2] == "null":
    CALL = {}

def view(coord):
    cfg = coord._ctx._config if hasattr(coord, "_ctx") else coord._config
    q = quiet_windows.compose(None, cfg, None, datetime(2026, 1, 5, 0, 0, tzinfo=UTC), 96, 0.25, 6.0)
    off = 0 if q.off_steps is None else int(q.off_steps.sum())
    return coord.configured_quiet_windows().get("quiet_off_windows_spec"), off, cfg.get("silent_mode_power_fraction")

async def main():
    hass = FakeHass()
    entry = FakeEntry(data={const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
                            const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor"})
    hass.config_entries.entries.append(entry)
    coord = C(hass, entry)
    entry.runtime_data = coord
    async def noop(): return None
    coord.async_request_refresh = noop
    try:
        await coord.async_update_thermal_params(dict(CALL))
        err = None
    except Exception as e:  # noqa
        err = f"{type(e).__name__}: {e}"
    print(f"RESULT call_error={err}")
    print(f"RESULT options_off={entry.options.get('quiet_off_windows')!r}")
    live = view(coord)
    print(f"RESULT live_spec={live[0]!r} live_off_steps={live[1]} live_fraction={live[2]!r}")
    await integration.async_update_options(hass, entry)
    print(f"RESULT reloaded={len(hass.config_entries.reloaded)}")
    hass2 = FakeHass()
    coord2 = C(hass2, entry)
    after = view(coord2)
    print(f"RESULT rebuilt_spec={after[0]!r} rebuilt_off_steps={after[1]} rebuilt_fraction={after[2]!r}")

asyncio.run(main())
