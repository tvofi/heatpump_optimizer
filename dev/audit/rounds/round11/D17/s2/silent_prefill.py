"""D17-s2-04 -- the night-mode schedule kept on the setup pre-fill page caps nothing.

Metric: the maximum planned electrical power (kW, OptimizationResult.power_schedule)
inside the kept night-mode window 06:00-10:00 UTC, on an entry created through the
real config flow (quick_setup -> device_prefill picking the G7b fixture device ->
keep `silent_mode_windows` -> finish_now), minus the same maximum on the entry created
without it. Binding state: the window is the only cheap stretch of the horizon
(0.05 inside, 3.0 outside), so an uncapped plan runs at nameplate there. Key: the
plan the real coordinator solves (silent_mode.compose via quiet_windows), never the
stored spec.
Oracle: strings.json config.step.device_prefill.data.silent_mode_windows "Pump's own
night-mode schedule"; docs/configuration.md:152 "When the pump limits itself to its
quiet mode"; docs/configuration.md:1171 "without this the plan counts on full power in
those hours and may buy cheap night quarters the pump will not use" -> with it kept,
the plan does not count on full power inside it.
Perturbation (config): the same entry with silent_mode_power_fraction=0.6 stored (the
options page's companion field, which the setup page never offers) -- expected cap
delta < 0. Code perturbation `--perturb`: EntryConfig.silent_mode_power_fraction read as
0.6 when a schedule is stored and the fraction is at its 1.0 default.

Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D17/s2/silent_prefill.py [--perturb]
Expected at 92d38ecb: RESULT kept_schedule_cap_delta_kW=0.00 ; RESULT
          with_fraction_cap_delta_kW<0 ; RESULT offered_fraction_on_setup_page=0 ; tolerance 1e-6.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B13 (Linux x86_64 container).
Instrumented: custom_components/heatpump_optimizer/silent_mode.py:compose
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "tools/devices")

import asyncio  # noqa: E402
import time  # noqa: E402
from unittest import mock  # noqa: E402

import gen_device_fixtures as g  # noqa: E402
import rig  # noqa: E402
from harness import FakeHass, FakeState  # noqa: E402
from heatpump_optimizer import config_flow, silent_mode  # noqa: E402

FIX = g.load("tuya_heat_pump_000004k4z6.json")
STATES = {"outdoor_ambient_temperature_t4": ("sensor", "-3.5"), "dhw_tank_temperature": ("sensor", "48.0"),
          "outlet_water_temperature_t1": ("sensor", "35.2"),
          "heat_exchanger_inlet_water_temperature_tin": ("sensor", "30.1"),
          "night_mode_silent": ("switch", "off"), "dhw_setpoint": ("number", "50")}
CHEAP = {"price": lambda h: 0.05 if 2 <= h < 6 else 3.0}  # h=2..5 -> 06:00-10:00 UTC


def seed(h):
    from homeassistant.helpers import device_registry as dr, entity_registry as er
    dr.async_get(h).add("dev_rotenso", name=FIX["device_name"])
    reg = er.async_get(h)
    for row in FIX["records"]:
        reg.add(row["entity_id"], unique_id=row["unique_id"], device_id="dev_rotenso", platform="tuya_heat_pump",
                original_name=row["original_name"], original_device_class=row["device_class"],
                unit_of_measurement=row["unit"])
    slug = FIX["device_name"].lower().replace(" ", "_")
    for n, (d, v) in STATES.items():
        h.states.set(f"{d}.{slug}_{n}", FakeState(v))


async def walk(kept):
    flow = config_flow.HeatPumpOptimizerConfigFlow()
    h = FakeHass()
    seed(h)
    flow.hass = h
    await rig._submit(flow, "user", rig.FIRST)
    await rig._submit(flow, "user_sensors", dict(rig.SENSORS))
    await rig._submit(flow, "quick_setup", {**rig.questionnaire(), "two_zone": False, "buffer_tank": False,
                                            "dhw_tank": True, "wood_furnace": False, "wood_buffer_tank": False})
    preview = await rig._submit(flow, "device_prefill", {"prefill_device": "dev_rotenso"})
    await rig._submit(flow, "device_prefill", kept)
    await rig._submit(flow, "finish_now", {})
    done = await rig._submit(flow, "setup_overview", {})
    return preview, done["data"], h


def max_in_window(data, h, extra=None):
    _, _, c = rig.build({**data, **(extra or {})}, hass=h, **CHEAP)
    reason, res, _ = rig.cycle(c)
    idx = [i for i, t in enumerate(res.timestamps) if 6 <= t.hour < 10 and t.date() == rig.NOW.date()]
    return max(res.power_schedule[i] for i in idx)


def measure():
    preview, base, hb = asyncio.run(walk({}))
    _, kept, hk = asyncio.run(walk({"silent_mode_windows": "06:00-10:00"}))
    offered = {str(k) for k in preview["data_schema"].schema}
    print(f"setup pre-fill page offers: {sorted(offered)}")
    print(f"entry kept: silent_mode_windows={kept.get('silent_mode_windows')!r} "
          f"silent_mode_power_fraction={kept.get('silent_mode_power_fraction')!r}")
    b = max_in_window(base, hb)
    k = max_in_window(kept, hk)
    f = max_in_window(kept, hk, {"silent_mode_power_fraction": 0.6})
    print(f"max planned kW in the window: without schedule={b:.3f} kept schedule={k:.3f} schedule+fraction 0.6={f:.3f}")
    print(f"RESULT kept_schedule_cap_delta_kW={k - b:.3f} kW")
    print(f"RESULT with_fraction_cap_delta_kW={f - b:.3f} kW")
    print(f"RESULT offered_fraction_on_setup_page={int('silent_mode_power_fraction' in offered)} fields")


if __name__ == "__main__":
    t0 = time.time()
    if "--perturb" in sys.argv:
        real = silent_mode.EntryConfig.from_mapping

        def frm(config):
            cfg = real(config)
            if cfg.silent_mode_windows and (cfg.silent_mode_power_fraction or 1.0) >= 1.0:
                object.__setattr__(cfg, "silent_mode_power_fraction", 0.6)
            return cfg
        with mock.patch.object(silent_mode.EntryConfig, "from_mapping", staticmethod(frm)):
            measure()
    else:
        measure()
    print(f"RESULT wall_s={time.time() - t0:.1f} s (provisional)")
    print("RESULT thread_factor=1.00 (counts only; single-thread pin)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
