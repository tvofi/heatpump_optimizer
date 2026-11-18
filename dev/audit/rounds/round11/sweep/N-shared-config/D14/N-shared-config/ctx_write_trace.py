"""N-shared-config dynamic arm (round 11): which production lines write INTO an object that a
published CoordinatorContext holds as a member, after it was published.

The static arm (ctx_inplace_seams.py) sees an edit only when it can name the member. A hub
object also travels as a parameter (`params`, `state`, `cfg`) or through `ThermalModel.params`,
where no AST rule can type it. This arm types it at runtime: `__setattr__` of OptimizationConfig,
ThermalParameters and ThermalState is wrapped, and a write is a SEAM when the instance is (or
was) a member of a context the coordinator published. Each seam is attributed to the first
package frame on the stack. Driven on the D1-s2 rig (real loop, spawned store loads, real
cycle with the memoised solve): construction, 4 full cycles 15 min apart, then the service
writers async_update_thermal_params, async_set_target_temperature, _apply_comfort_weight,
async_set_mode (comfort, auto), and one more cycle.

Run (repo root): PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/N-shared-config/ctx_write_trace.py
     --perturb   async_set_target_temperature publishes replace(ctx, _opt_config=replace(..)) instead:
                 its seam leaves the list (the finding's fix, in memory)
     --plant     one extra in-place write on a published member in the drive
                 (`coord._ctx._thermal_params.<first float field> += 0.0`): the seams rise by one
Null control: a published member written only through replace() (the --perturb arm for that line).
"""
from __future__ import annotations

import asyncio
import contextlib
import dataclasses
import os
import sys
import traceback
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT / "dev/audit/rounds/round11/D1/s2"))
import d1s2_lib as L  # noqa: E402
from heatpump_optimizer import optimizer as opt_mod, thermal_model as tm_mod  # noqa: E402

PKG = str(ROOT / "custom_components" / "heatpump_optimizer")
CLASSES = [opt_mod.OptimizationConfig, tm_mod.ThermalParameters, tm_mod.ThermalState]
PUBLISHED: dict[int, str] = {}   # id(member object) -> member name
KEEP: list = []                  # keep published members alive so ids stay unique
SEAMS: dict[tuple, int] = {}
STEP = {"name": "construct"}


def note_ctx(coord):
    ctx = getattr(coord, "_ctx", None)
    if ctx is None:
        return
    for m in ("_opt_config", "_thermal_params", "_current_state"):
        obj = getattr(ctx, m, None)
        if obj is not None and id(obj) not in PUBLISHED:
            PUBLISHED[id(obj)] = m
            KEEP.append(obj)


def hook(cls):
    orig = cls.__setattr__

    def __setattr__(self, name, value):
        if id(self) in PUBLISHED and not name.startswith("__"):
            frame = None
            for fs in reversed(traceback.extract_stack()[:-1]):
                if fs.filename.startswith(PKG) and not fs.filename.endswith("dataclasses.py"):
                    frame = fs
                    break
            where = (os.path.relpath(frame.filename, ROOT), frame.lineno, frame.name) if frame else ("?", 0, "?")
            key = (*where, PUBLISHED[id(self)], name)
            SEAMS[key] = SEAMS.get(key, 0) + 1
            STEP.setdefault("by_step", {}).setdefault(key, set()).add(STEP["name"])
        orig(self, name, value)

    cls.__setattr__ = __setattr__


async def drive(perturb: bool, plant: bool):
    hass = L.SchedHass(L.base_states())
    coord = L.HeatPumpOptimizerCoordinator(hass, L.FakeEntry(data=L.base_config({"comfort_learning_enabled": True})))
    L.price_stub(coord)
    coord.async_request_refresh = lambda: asyncio.sleep(0)
    if perturb:
        async def set_target(self, temperature):
            ctx = self._ctx
            self._ctx = dataclasses.replace(ctx, _opt_config=dataclasses.replace(ctx._opt_config, target_temp=temperature))
        coord.async_set_target_temperature = set_target.__get__(coord)
    note_ctx(coord)
    await L.drain(hass)

    async def step(name, coro_or_fn):
        STEP["name"] = name
        note_ctx(coord)
        try:
            out = coro_or_fn()
            if hasattr(out, "__await__"):
                await out
        except Exception as err:  # noqa: BLE001
            print(f"# step {name} raised {type(err).__name__}: {str(err)[:100]}")
        await L.drain(hass)
        note_ctx(coord)

    for i in range(4):
        now = L.T0 + timedelta(minutes=15 * i)
        L.dtu.freeze(now)
        for k, v in L.base_states().items():
            hass.states.set(k, L.FakeState(v.state, last_updated=now, last_reported=now))
        await step(f"cycle{i}", coord._async_update_data)
    await step("update_thermal_params", lambda: coord.async_update_thermal_params({"house_heat_loss_coefficient": 0.2}))
    await step("set_target", lambda: coord.async_set_target_temperature(22.0))

    def bump_weight():
        coord._comfort_learner.learned_weight = coord._comfort_learner.configured_weight * 1.5
        coord._apply_comfort_weight()
    await step("comfort_weight", bump_weight)
    await step("set_mode_comfort", lambda: coord.async_set_mode("comfort"))
    await step("set_mode_auto", lambda: coord.async_set_mode("auto"))
    if plant:
        def planted():
            p = coord._ctx._thermal_params
            f = next(f.name for f in dataclasses.fields(p) if isinstance(getattr(p, f.name), float))
            setattr(p, f, getattr(p, f) + 0.0)  # planted: an in-place write into a published member
        await step("plant", planted)
    now = L.T0 + timedelta(minutes=75)
    L.dtu.freeze(now)
    await step("cycle4", coord._async_update_data)
    with contextlib.suppress(Exception):
        await coord.async_shutdown()
    await L.drain(hass, 5)


def main() -> int:
    perturb, plant = "--perturb" in sys.argv, "--plant" in sys.argv
    for c in CLASSES:
        hook(c)
    with contextlib.ExitStack() as st:
        for p in L.patches():
            st.enter_context(p)
        asyncio.run(drive(perturb, plant))
    by = STEP.get("by_step", {})
    for (f, ln, fn, m, field), n in sorted(SEAMS.items()):
        print(f"SEAM {f}:{ln} {fn} {m}.{field} writes={n} steps={','.join(sorted(by[(f, ln, fn, m, field)]))}")
    sites = {(f, ln) for (f, ln, *_ ) in SEAMS}
    print(f"RESULT published_member_write_sites={len(sites)} fields={len(SEAMS)} published_members={len(PUBLISHED)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
