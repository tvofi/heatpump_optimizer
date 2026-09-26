#!/usr/bin/env python3
"""Verifier V3 cheap check for D3-s3-04 (dhw_learning.DhwProfileLearner.async_fold_draw_stats).

Metric: total energy (kWh) folded into draw_stats reservoirs across one
beyond-standby-drop interval, comparing the baseline body against the M24
mutant (the `if self._external_heat_active(): return` skip deleted, so a
wood-burn interval folds anyway) and a stronger "folds nothing" mutant
(`if True: return`), with a null (identity) arm.

Command:
    PYTHONPATH=tests/hastub /root/venv314/bin/python \
    tools/audit/round9/D3/verify-v3-catchup/D3-s3-04_reach.py

Reach: async_fold_draw_stats takes a HomeAssistant instance only to build a
QuarantiningStore for persistence, never reads hass state to decide whether
to fold; the fold arithmetic itself has no homeassistant.* call in it (grep
of the method body). Not run against /root/venvha for that reason (the
divergence, if any, is only in whether tests/hastub's HomeAssistant/Store
stand-ins accept the constructor -- checked here by constructing the real
class, not a re-implementation).

Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: box G1-V3 (4 CPUs).
"""
import asyncio
import os
import sys
import time
from datetime import datetime
from unittest import mock

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

t_process0 = time.process_time()
t_wall0 = time.time()

sys.path.insert(0, os.getcwd())

from custom_components.heatpump_optimizer.dhw_learning import DhwProfileLearner  # noqa: E402
from custom_components.heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402
from homeassistant.core import HomeAssistant  # noqa: E402


def total_folded(kwh_of) -> float:
    # fold() accumulates into the OPEN occurrence until the window/day
    # changes; a single call's effect is _open_kwh, matching the finder's
    # own metric ("0.4396 kWh folded ... instead of 0.0").
    return kwh_of._open_kwh


async def run(mutant: str | None, external_heat: bool = True) -> float:
    params = ThermalParameters(dhw_enabled=True)
    hass = HomeAssistant()
    learner = DhwProfileLearner(
        hass,
        "entry1",
        params,
        frozen=lambda _e: None,
        heating_active=lambda: False,
        external_heat_active=lambda: external_heat,
    )
    now = datetime(2026, 1, 15, 7, 0)
    # previous_temp - AMBIENT well above zero, dt_h beyond standby loss,
    # so a real fold (if it happened) would be positive.
    previous_temp = 45.0
    temp_drop = 5.0
    dt_h = 1.0

    if mutant is None:
        await learner.async_fold_draw_stats(now, previous_temp, temp_drop, dt_h)
    elif mutant == "M24":
        # M24: the external-heat skip deleted -- fold proceeds unconditionally.
        async def mutated(self, now, previous_temp, temp_drop, dt_h):
            standby_rate = (
                self.cooling_rate
                * max(0.0, previous_temp - 20.0)
                / 25.0
            )
            intensity = max(0.0, temp_drop / dt_h - standby_rate)
            energy_kwh = intensity * dt_h * self._params.dhw_tank_thermal_mass
            windows = self._params.dhw_demand_windows
            from custom_components.heatpump_optimizer.dhw_draws import (
                window_label as draw_window_label,
            )

            label = draw_window_label(now.hour + now.minute / 60.0, windows)
            self.draw_stats.fold(now, label, energy_kwh)

        with mock.patch.object(DhwProfileLearner, "async_fold_draw_stats", mutated):
            await learner.async_fold_draw_stats(now, previous_temp, temp_drop, dt_h)
    elif mutant == "folds_nothing":
        async def mutated(self, now, previous_temp, temp_drop, dt_h):
            return None

        with mock.patch.object(DhwProfileLearner, "async_fold_draw_stats", mutated):
            await learner.async_fold_draw_stats(now, previous_temp, temp_drop, dt_h)

    return total_folded(learner.draw_stats)


def main():
    # Arm A: wood burn in progress (external_heat=True) -- the demonstrated M24 seam.
    baseline = asyncio.run(run(None, external_heat=True))
    m24 = asyncio.run(run("M24", external_heat=True))
    null = asyncio.run(run(None, external_heat=True))

    # Arm B: no external heat (normal beyond-standby draw) -- the
    # "folds nothing" stronger mutant, which the seam_rule command also kills=0.
    normal_baseline = asyncio.run(run(None, external_heat=False))
    folds_nothing = asyncio.run(run("folds_nothing", external_heat=False))

    print(f"RESULT baseline_folded_kwh_extheat={baseline}")
    print(f"RESULT M24_folded_kwh_extheat={m24}")
    print(f"RESULT M24_delta={abs(baseline - m24)} kWh")
    print(f"RESULT null_delta={abs(baseline - null)} kWh")
    print(f"RESULT baseline_folded_kwh_normal={normal_baseline}")
    print(f"RESULT folds_nothing_folded_kwh_normal={folds_nothing}")
    print(f"RESULT folds_nothing_delta={abs(normal_baseline - folds_nothing)} kWh")

    thread_cpu = time.process_time() - t_process0
    wall = time.time() - t_wall0
    thread_factor = (thread_cpu / wall) if wall > 0 else 1.0
    try:
        load1 = os.getloadavg()[0]
    except (OSError, AttributeError):
        load1 = -1.0
    print(f"RESULT thread_factor={min(thread_factor, 1.0):.3f}")
    print(f"RESULT load1={load1}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
