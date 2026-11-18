"""N-solve-recompute seam probe (round 11, SW2).

Usage: PYTHONPATH=tests/hastub python3 probe.py TRIGGER [--perturb]
TRIGGER in: diagnose | force_button | boost_dhw | block_space | refresh (null)
            | away (power control: an input-changing trigger)

At one frozen instant after three warm cycles, a plain refresh solves the
plan (reference), then TRIGGER runs.  Every _multi_start_minimize entry the
trigger causes is recorded with its result vector.  The trigger is a
recompute when it enters the solver at least once and every solve it buys
reproduces a reference solve (|dx|max <= TOL): work whose result was
already in hand.  rc=1 then; rc=0 when it solves nothing or solves
something new.  'refresh' (a second identical refresh) is the null arm of
the comparator and is rc=1 by construction -- it shows a repeated
solve on unchanged inputs IS reproduced exactly; 'away' must give rc=0.
"""
import asyncio
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
sys.path.insert(0, os.path.join(REPO, "dev/audit/rounds/round11/D9/s1"))
sys.path.insert(0, REPO)
import d9s1lib as L  # noqa: E402

# Solver jitter between two solves of identical inputs measured 6.04e-4 on a
# 6 kW-scale vector (warm start); an input change (away) moved it by 6.
TOL = 1e-2


async def run(trigger, perturb=False):
    from heatpump_optimizer import boost
    from heatpump_optimizer import optimizer as om
    from homeassistant.util import dt as dtu
    from profiles import house

    loop = asyncio.get_running_loop()
    pool = ThreadPoolExecutor(max_workers=2)
    hass = L.make_loop_hass(loop, pool)
    dtu.freeze(L.CYCLE_NOW)
    coord = L.make_coordinator(hass, dict(house(two_zone=True, dhw=True)),
                               entry_id=f"snr_{trigger}")
    tags: list = []
    undo = L.inline_worker(tags)
    xs: list = []
    real = om._multi_start_minimize

    def hook(*a, **k):
        res = real(*a, **k)
        x = getattr(res, "x", None)
        if x is None and isinstance(res, tuple):
            x = getattr(res[0], "x", res[0])
        xs.append(np.asarray(x, dtype=float).ravel().copy())
        return res

    om._multi_start_minimize = hook
    try:
        for i in range(3):
            now = L.CYCLE_NOW + timedelta(minutes=30 * i)
            dtu.freeze(now)
            L.feed(coord, now)
            coord.data = await coord._async_update_data()
        now = L.CYCLE_NOW + timedelta(minutes=67)
        dtu.freeze(now)
        L.feed(coord, now)
        async def cycle():
            # Home Assistant's debouncer runs every request as one cycle --
            # at once outside its cooldown, at the cooldown's end inside it;
            # the stub's frozen clock would hold the second one forever.
            coord.data = await coord._async_update_data()
        coord.async_request_refresh = cycle
        n0 = len(xs)
        await cycle()
        ref = xs[n0:]
        n1 = len(xs)
        if perturb:
            # One-line re-introduction in reverse (D9-s1-01's perturbation):
            # the request publishes the payload without running the cycle.
            async def publish_only():
                coord.data = coord._build_data_dict()
                coord.async_update_listeners()
            coord.async_request_refresh = publish_only
        inner = None
        if trigger == "diagnose":
            await coord.async_diagnose_interval()
        elif trigger == "force_button":  # button.py ForceOptimizationButton.async_press
            await coord.async_run_optimization()
            inner = len(xs)
            await coord.async_request_refresh()
        elif trigger == "boost_dhw":  # switch.py TimedDutySwitch._press -> publish_then_refresh
            await boost.set_channel(coord, boost.CHANNEL_DHW, True, refresh=False)
            await coord.async_request_refresh()
        elif trigger == "block_space":
            await boost.set_block(coord, boost.CHANNEL_SPACE, True, refresh=False)
            await coord.async_request_refresh()
        elif trigger == "refresh":
            await coord.async_request_refresh()
        elif trigger == "away":
            await coord.async_set_away(active=True, refresh=False)
            await coord.async_request_refresh()
        else:
            raise SystemExit(f"unknown trigger {trigger}")
        got = xs[n1:]
    finally:
        om._multi_start_minimize = real
        undo()
        pool.shutdown()

    def dup(x):
        return any(r.shape == x.shape and float(np.max(np.abs(r - x), initial=0.0)) <= TOL for r in ref)

    def dist(x):
        d = [float(np.max(np.abs(r - x), initial=0.0)) for r in ref if r.shape == x.shape]
        return min(d) if d else float("inf")

    print("RESULT dist_to_reference=" + ",".join(f"{dist(x):.3g}" for x in got))
    print("RESULT ref_scale=" + ",".join(f"{float(np.max(np.abs(r))):.3g}" for r in ref))
    if inner is not None:
        # The press's own first solve is the reference for its refresh: the
        # refresh's solves are the ones the press need not have bought.
        own, rest = xs[n1:inner], xs[inner:]
        inner_dups = sum(any(r.shape == x.shape and float(np.max(np.abs(r - x), initial=0.0)) <= TOL
                             for r in own) for x in rest)
        print(f"RESULT press_first_solves={len(own)} refresh_solves={len(rest)} refresh_reproduces_press={inner_dups}")
        got = rest
    dups = sum(dup(x) for x in got) if inner is None else inner_dups
    print(f"RESULT trigger={trigger} reference_solves={len(ref)} trigger_solves={len(got)} reproduced={dups}")
    recompute = len(got) > 0 and dups == len(got)
    print(f"RESULT recompute={int(recompute)}")
    return 1 if recompute else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(run(sys.argv[1], "--perturb" in sys.argv[2:])))
