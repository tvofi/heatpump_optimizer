import sys, asyncio; sys.path.insert(0, sys.argv[1])
import myrig
async def main():
    myrig.freeze()
    hass, entry, c = await myrig.setup(myrig.base_data())
    d = await myrig.solve(c)
    print(type(d), sorted(d.keys())[:400] if isinstance(d, dict) else d)
    for k in ("two_zone_enabled","last_optimization","current_price","schedule"):
        v=d.get(k); print(k, type(v), str(v)[:300])
asyncio.run(main())
