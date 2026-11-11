"""D12 v1 -- what the DHW boost switch changes on an install with NO hot-water tank.

Metric (v1, one line): over a grid of no-DHW installs (zones 1/2 x outdoor
-10/0/+8 C, one switch-actuated pump, a peak-priced current hour), the number of
cells in which a cycle run after switch:BoostDhwSwitch.async_turn_on differs
from the same cell's no-boost cycle in any of: (a) the direction of the
heat-pump switch service call, (b) a published data-dict key whose name contains
"dhw", (c) coordinator._commanded_power(). Each channel is also counted
separately. Key: service calls FakeServices recorded and the dict
_async_update_data returned, diffed per cell.

Differs from the finder's s1_phantom_boost.py: a different cell grid
(zones x outdoor temperature instead of zones x wood x pv), the coordinator is
constructed bare (no ha_setup_entry, no switch platform setup), the switch
entity is constructed directly, and the key is a boost-on vs boost-off DIFF
(physical actuation plus every published dhw key), not the absolute dhw_power.

Null control: the same diff between two no-boost cycles on fresh coordinators
(expected 0 cells on every channel).
Perturbation (--fix-arm): the finder's one-line fix in boost.apply (drop the DHW
channel when params.dhw_enabled is False), applied in memory, restored in
finally -> every channel to_zero.

Command (from tree root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D12/v1_boost_effects.py [--fix-arm]
Expected at baseline cdf82daa: RESULT cells_changed=6 of 6 (exact).
Machine: 4-vCPU cloud Linux container (audit round 8 fan-out), seat D12-v1.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import inspect
import itertools
import math
import sys
import textwrap
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import boost as boost_mod  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as cmod  # noqa: E402
from heatpump_optimizer.optimizer import optimize_in_process  # noqa: E402
from heatpump_optimizer.switch import BoostDhwSwitch  # noqa: E402

NOW = datetime(2026, 1, 14, 17, 7, tzinfo=timezone.utc)


def cfg(zones):
    c = {
        "name": "Home",
        const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
        const.CONF_PRICE_ENTITY: "sensor.prices",
        const.CONF_WEATHER_ENTITY: "weather.home",
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
        const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.hp",
        const.CONF_DHW_ENABLED: False,
        const.CONF_TWO_ZONE_MODE: "on" if zones == 2 else "off",
    }
    if zones == 2:
        c.update({"upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 8.0})
    return c


def hass_for(t_out):
    start = NOW.replace(minute=0)
    hass = FakeHass({
        "sensor.prices": FakeState("1.3", attributes={"raw_today": [
            {"start": (start + timedelta(hours=h)).isoformat(),
             "value": 1.3 if h < 3 else 0.3} for h in range(48)]}),
        "sensor.indoor": FakeState("21.5", unit="°C"),
        "sensor.outdoor": FakeState(str(t_out), unit="°C"),
        "switch.hp": FakeState("on"),
    })

    async def forecasts(call):
        return {call.data["entity_id"]: {"forecast": [
            {"datetime": (start + timedelta(hours=h)).isoformat(),
             "temperature": float(t_out), "wind_speed": 3.0,
             "precipitation": 0.0, "humidity": 85.0} for h in range(48)]}}
    hass.services.async_register("weather", "get_forecasts", forecasts)
    return hass


async def cycle(zones, t_out, boost_on):
    hass = hass_for(t_out)
    entry = FakeEntry(data=cfg(zones))
    coord = cmod.HeatPumpOptimizerCoordinator(hass, entry)
    coord.async_request_refresh = _noop  # the switch asks for a refresh; we run the cycle ourselves
    if boost_on:
        await BoostDhwSwitch(coord, entry).async_turn_on()
    data = await coord._async_update_data()
    sw = [s for d, s, p in hass.services.calls
          if (p or {}).get("entity_id") == "switch.hp" and s in ("turn_on", "turn_off")]
    out = {
        "switch": sw[-1] if sw else None,
        "dhw_keys": {k: data[k] for k in data if "dhw" in k.lower()},
        "commanded": float(coord._commanded_power() or 0.0),
        "dhw_enabled": coord._thermal_params.dhw_enabled,
    }
    try:
        await coord.async_shutdown()
    except Exception:  # noqa: BLE001
        pass
    boost_mod._STATES.pop(coord, None)
    return out


async def _noop(*a, **k):
    return None


def _eq(a, b):
    if isinstance(a, float) and isinstance(b, float):
        return (math.isnan(a) and math.isnan(b)) or abs(a - b) < 1e-9
    return a == b


def diff(a, b):
    keys = sorted(k for k in set(a["dhw_keys"]) | set(b["dhw_keys"])
                  if not _eq(a["dhw_keys"].get(k), b["dhw_keys"].get(k)))
    return {
        "switch": a["switch"] != b["switch"],
        "dhw_keys": keys,
        "commanded": abs(a["commanded"] - b["commanded"]) > 1e-6,
        "commanded_delta": b["commanded"] - a["commanded"],
    }


def patch_fix():
    src = textwrap.dedent(inspect.getsource(boost_mod.apply))
    needle = "held.expire(now)\n"
    assert needle in src
    src = src.replace(needle, needle + "    if not coord._thermal_model.params.dhw_enabled: held.until.pop(CHANNEL_DHW, None)\n", 1)
    ns = {}
    exec(compile(src, boost_mod.__file__, "exec"), boost_mod.__dict__, ns)
    orig = boost_mod.apply
    boost_mod.apply = ns["apply"]
    return orig


def main():
    fix = "--fix-arm" in sys.argv
    real_solve, real_now = cmod._await_optimize, dt_util.now

    async def inline(hass, optimizer, state, *a, **k):
        return optimize_in_process(optimizer, state, a, k)
    cmod._await_optimize = inline
    dt_util.now = lambda *a, **k: NOW
    orig = patch_fix() if fix else None
    t0p, t0t = time.process_time(), time.thread_time()
    cells = 0
    tally = {"any": 0, "switch": 0, "dhw_keys": 0, "commanded": 0}
    null = {"any": 0, "switch": 0, "dhw_keys": 0, "commanded": 0}
    try:
        for zones, t_out in itertools.product((1, 2), (-10, 0, 8)):
            cells += 1
            base = asyncio.run(cycle(zones, t_out, False))
            base2 = asyncio.run(cycle(zones, t_out, False))
            on = asyncio.run(cycle(zones, t_out, True))
            assert base["dhw_enabled"] is False
            d, n = diff(base, on), diff(base, base2)
            for tgt, dd in ((tally, d), (null, n)):
                hit = {"switch": dd["switch"], "dhw_keys": bool(dd["dhw_keys"]),
                       "commanded": dd["commanded"]}
                for k, v in hit.items():
                    tgt[k] += int(v)
                tgt["any"] += int(any(hit.values()))
            print(f"  z{zones} t_out={t_out:+d}  switch {base['switch']}->{on['switch']}  "
                  f"commanded {base['commanded']:.2f}->{on['commanded']:.2f} kW  "
                  f"dhw keys changed={d['dhw_keys']}  | null diff: switch={n['switch']} "
                  f"keys={n['dhw_keys']} commanded={n['commanded']}")
    finally:
        cmod._await_optimize, dt_util.now = real_solve, real_now
        if orig is not None:
            boost_mod.apply = orig
    pc, tc = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT arm={'fix' if fix else 'baseline'}")
    print(f"RESULT cells_changed={tally['any']} of {cells}")
    print(f"RESULT cells_switch_flipped={tally['switch']} of {cells}")
    print(f"RESULT cells_dhw_keys_changed={tally['dhw_keys']} of {cells}")
    print(f"RESULT cells_commanded_changed={tally['commanded']} of {cells}")
    print(f"RESULT null_cells_changed={null['any']} of {cells}")
    print(f"RESULT thread_factor={pc / tc if tc else float('nan'):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    with open("/proc/vmstat") as fh:
        sw = [l for l in fh if l.startswith("pswpin")]
    print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")


if __name__ == "__main__":
    main()
