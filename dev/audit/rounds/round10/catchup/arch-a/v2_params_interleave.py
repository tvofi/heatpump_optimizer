#!/usr/bin/env python3
"""arch-a V2 (round 10 catch-up verify, D7-s1-82): a second task observes the thermal parameters
while set_thermal_parameters is suspended in a store write that really yields.

Independent of the finder's probe: no spy replaces the coordinator's save; the Store stub's
async_save is made to yield (asyncio.sleep(0) x 3, as the real HA Store does through
async_add_executor_job), and a concurrent reader task samples the hub, the live model and a
solve's private copy (coordinator._solve_hubs, the real solve entry) on every loop turn.

Metric: mixed_snapshots -- reader samples whose requested fields are neither all at the
          pre-call value nor all at the post-call value (a torn view another task can act on);
        unclamped_hub -- samples of the hub with room_thermal_mass < THERMAL_MASS_FLOOR;
        unclamped_solve -- samples of _solve_hubs' params copy with room_thermal_mass < floor;
        yielded -- 1 when the call was suspended at least once (0 = the arm measured nothing).
Count key: one sample per reader loop turn while the call task is pending.
Command:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/catchup/arch-a/v2_params_interleave.py [--null]
          run from the root of the tree under test.
Null control: --null requests every field at the value it already holds: mixed and unclamped
          must read 0 on every tree.
Perturbation: the tree. Expected (baseline 9061fbd3d / d749c986d, darwin): main mixed>0,
          unclamped_hub>0, unclamped_solve=0 (replace() re-clamps the solve copy);
          + P1_thermal_params_single_owner.patch: 0, 0, 0.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.helpers import storage  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.thermal_model import THERMAL_MASS_FLOOR  # noqa: E402

_real_save = storage.Store.async_save


async def _yielding_save(self, data):
    for _ in range(3):
        await asyncio.sleep(0)
    await _real_save(self, data)


storage.Store.async_save = _yielding_save

FIELDS = ("heat_loss_coefficient", "room_thermal_mass", "dhw_legionella_temp",
          "dhw_idle_min_temp", "ecl110_displace_min")


def main(argv: list[str]) -> int:
    null = "--null" in argv
    t_cpu, t_thr = time.process_time(), time.thread_time()
    coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data={
        "tibber_token": "x", "weather_entity": "weather.home", "dhw_tank_volume": 200.0}))
    p = coord._thermal_params
    if null:
        req = {"house_heat_loss_coefficient": p.heat_loss_coefficient,
               "house_thermal_mass": p.room_thermal_mass,
               "dhw_legionella_temperature": p.dhw_legionella_temp,
               "dhw_idle_min_temperature": p.dhw_idle_min_temp,
               "ecl110_displace_min": p.ecl110_displace_min}
    else:
        req = {"house_heat_loss_coefficient": 0.31, "house_thermal_mass": 1e-6,
               "dhw_legionella_temperature": 63.5, "dhw_idle_min_temperature": 41.5,
               "ecl110_displace_min": -4.25}
    pre = {f: getattr(p, f) for f in FIELDS}
    samples: list[tuple[dict, dict, float | None]] = []
    solve_err: list[str] = []

    async def reader(task: asyncio.Task) -> None:
        while not task.done():
            hub = coord._thermal_params
            model = coord._thermal_model.params
            solve_mass = None
            try:
                _o, sp, _s = coord._solve_hubs(96, banded=False)
                solve_mass = float(sp.room_thermal_mass)
            except Exception as err:  # the solve prep may need more state than a bare coordinator
                if not solve_err:
                    solve_err.append(f"{type(err).__name__}: {err}"[:120])
            samples.append(({f: getattr(hub, f) for f in FIELDS},
                            {f: getattr(model, f) for f in FIELDS}, solve_mass))
            await asyncio.sleep(0)

    async def run() -> None:
        task = asyncio.ensure_future(coord.async_update_thermal_params(req))
        await asyncio.gather(task, reader(task))

    asyncio.run(run())
    post = {f: getattr(coord._thermal_params, f) for f in FIELDS}
    changed = [f for f in FIELDS if pre[f] != post[f]]

    def mixed(view: dict) -> bool:
        if not changed:
            return False
        return (any(view[f] != pre[f] for f in changed)
                and any(view[f] != post[f] for f in changed))

    mixed_n = sum(mixed(h) or mixed(m) for h, m, _ in samples)
    unc_hub = sum(h["room_thermal_mass"] < THERMAL_MASS_FLOOR for h, _m, _ in samples)
    solve_vals = [s for _h, _m, s in samples if s is not None]
    unc_solve = sum(s < THERMAL_MASS_FLOOR for s in solve_vals)
    print(f"RESULT yielded={int(len(samples) > 1)} count samples={len(samples)}")
    print(f"RESULT mixed_snapshots={mixed_n} count (changed fields {len(changed)})")
    print(f"RESULT unclamped_hub={unc_hub} count")
    print(f"RESULT unclamped_solve={unc_solve} count (solve samples {len(solve_vals)}"
          f"{'; ' + solve_err[0] if solve_err else ''})")
    cpu, thr = time.process_time() - t_cpu, time.thread_time() - t_thr
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
