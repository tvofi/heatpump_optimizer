import asyncio, sys
exec(open("tests/_ux4_review_block.py").read().split("_ux4 = _ux4_aio.run")[0])
async def probe():
    rig = _Ux4Rig("probe_flicker"); await rig.load()
    a = await rig.feed(_ux4_released(space=(3, 4)))
    b = await rig.feed(_ux4_released(space=()))          # same override, this solve released nothing
    c = await rig.feed(_ux4_released(space=(5,)))        # same override, released again
    print("RESULT manual_flicker_same_override fires=", [len(a), len(b), len(c)])
    rig = _Ux4Rig("probe_osc"); await rig.load()
    seq = [_ux4_cold(18.9), _ux4_cold(19.1), _ux4_cold(18.9), _ux4_cold(19.1), _ux4_cold(18.9)]
    print("RESULT comfort_oscillation fires=", [len(await rig.feed(p)) for p in seq])
    # restart with a far-future expiry under the real store, default clock
    rig = _Ux4Rig("probe_restart"); await rig.load()
    p = _ux4_released(expires="2099-01-01T00:00:00+00:00")
    first = await rig.feed(p)
    r2 = _Ux4Rig("probe_restart"); await r2.load()
    print("RESULT restart_far_future_expiry fires=", [len(first), len(await r2.feed(p))])
asyncio.run(probe())
