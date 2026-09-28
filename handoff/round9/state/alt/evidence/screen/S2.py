"""S2: the fuse advisor and the price tile borrow async_simulate inside a
snapshot/restore of (_last_simulation, _simulation_cache). Does a USER
simulate (the simulate_plan action / card what-if) that overlaps the borrow
window get (a) rate-limited, or (b) have its answer and its limiter slot
erased by the unconditional restore?

Real coordinator, real solves (in-process). Only the borrowed simulate's
_await_optimize is held on an asyncio.Event; the user's is not. A
contextvar tags which caller issued each solve.

Setup per arm: cycle 1 (plan + borrowers run once, ungated) -> user U0
(target_temp 20.0) seeds the card cache -> clock moves on (the limiter stamp
is backdated 10 s, i.e. U0 was 10 s ago).
Cycle 2 = async_run_optimization with ONE borrower due (tile or fuse).
  probe(a): user U1 (target 22.0) lands immediately inside the held window
  probe(b): the window is held 3.2 s of real time (a slow Pi-class solve),
            then U1 lands, finishes inside the window; window released; then
            U2 (target 22.5) is issued immediately (<3 s after U1)
  null    : cycle 2 completes first (no overlap), then U1, then U2 immediately
"""
import asyncio
import contextvars
import time
from datetime import timedelta

import rig
from heatpump_optimizer import coordinator as cmod
from heatpump_optimizer.optimizer import optimize_in_process

WHO = contextvars.ContextVar("who", default="plan_or_user")
HOLD = {"label": None, "entered": None, "release": None}


async def _await_opt(hass, optimizer, state, *pos, **kw):
    if HOLD["label"] is not None and WHO.get() == HOLD["label"]:
        HOLD["entered"].set()
        await HOLD["release"].wait()
    return optimize_in_process(optimizer, state, pos, kw)


cmod._await_optimize = _await_opt


def tag(coord, name, label):
    real = getattr(coord, name)

    async def w(*a, **k):
        tok = WHO.set(label)
        try:
            return await real(*a, **k)
        finally:
            WHO.reset(tok)

    setattr(coord, name, w)


def ov(ans):
    if not isinstance(ans, dict):
        return ans
    return (ans.get("overrides") or {}).get("target_temp"), bool(ans.get("rate_limited")), ans.get("error")


async def setup(borrower):
    c = rig.make(f"s2_{borrower}", extra={"price_tiles_enabled": True, "main_fuse_amperes": 20, "main_fuse_phases": 3})
    tag(c, "_maybe_refresh_price_tile", "tile")
    tag(c, "_maybe_run_fuse_advisor", "fuse")
    HOLD["label"] = None
    assert await c.async_run_optimization() is None
    c._last_simulation = None
    u0 = await c.async_simulate({"target_temp": 20.0})
    c._last_simulation = c._last_simulation - timedelta(seconds=10)
    u0_stamp = c._last_simulation
    # Make exactly one borrower due in cycle 2.
    if borrower == "tile":
        c._fuse_advisor_at = rig.dt_util.now()  # fuse not due
    else:
        c._config["price_tiles_enabled"] = False
        c._fuse_advisor_at = rig.dt_util.now() - timedelta(days=8)
    return c, u0, u0_stamp


async def arm(borrower, kind):
    c, u0, u0_stamp = await setup(borrower)
    out = {"arm": f"{kind}/{borrower}", "U0": ov(u0)}
    if kind == "null":
        HOLD["label"] = None
        await c.async_run_optimization()
        u1 = await c.async_simulate({"target_temp": 22.0})
        u1_stamp = c._last_simulation
        out["U1"] = ov(u1)
        out["cache_after_window"] = ov(c._simulation_cache)
        out["stamp_is_U0s"] = c._last_simulation == u0_stamp
        out["U2 issued, s after U1 stamp"] = round((rig.dt_util.now() - u1_stamp).total_seconds(), 2)
        u2 = await c.async_simulate({"target_temp": 22.5})
        out["U2(<3s after U1)"] = ov(u2)
        return out
    HOLD.update(label=borrower, entered=asyncio.Event(), release=asyncio.Event())
    task = asyncio.get_running_loop().create_task(c.async_run_optimization())
    await asyncio.wait_for(HOLD["entered"].wait(), 60)
    if kind == "probe(b)":
        await asyncio.sleep(3.2)
    t = time.time()
    u1 = await c.async_simulate({"target_temp": 22.0})
    u1_stamp = c._last_simulation
    out["U1"] = ov(u1)
    out["cache_inside_window"] = ov(c._simulation_cache)
    HOLD["release"].set()
    await task
    HOLD["label"] = None
    out["cache_after_window"] = ov(c._simulation_cache)
    out["stamp_is_U0s"] = c._last_simulation == u0_stamp
    out["U2 issued, s after U1 stamp"] = round((rig.dt_util.now() - u1_stamp).total_seconds(), 2)
    u2 = await c.async_simulate({"target_temp": 22.5})
    out["U2(<3s after U1)"] = ov(u2)
    return out


async def main():
    # wall time of one borrowed simulate here, for the window width
    c, _, _ = await setup("tile")
    t = time.time()
    await c._maybe_refresh_price_tile()
    print(f"one tile simulate on this box: {time.time() - t:.2f} s  (limiter SIMULATE_MIN_INTERVAL_SECONDS={cmod.SIMULATE_MIN_INTERVAL_SECONDS})")
    print("cells are (overrides.target_temp, rate_limited, error)\n")
    rows = []
    for b in ("tile", "fuse"):
        for k in ("probe(a)", "probe(b)", "null"):
            rows.append(await arm(b, k))
    keys = ["U0", "U1", "cache_inside_window", "cache_after_window", "stamp_is_U0s", "U2 issued, s after U1 stamp", "U2(<3s after U1)"]
    w = 24
    print("field".ljust(22) + "".join(r["arm"].ljust(w) for r in rows))
    for k in keys:
        print(k.ljust(22) + "".join(str(r.get(k, "-")).ljust(w) for r in rows))




asyncio.run(main())
