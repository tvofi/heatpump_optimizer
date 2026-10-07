"""Reviewer's plants against the behavioural check_fork at the round-2 head."""
import asyncio, sys
import boost_drift_replay as b
orig = b.cycle
PLANT = sys.argv[1]
def planted(st, i, surface):
    c = st["coord"]
    if PLANT == "channel100" and surface == "channel" and i == 100:
        asyncio.run(b.boost_mod.set_channel(c, b.boost_mod.CHANNEL_SPACE, True, refresh=False))
    if PLANT == "comfort30" and surface == "mode" and i == 30:
        asyncio.run(c.async_set_mode("comfort", refresh=False))
    if PLANT == "dhw200" and surface == "channel" and i == 200:
        asyncio.run(b.boost_mod.set_channel(c, b.boost_mod.CHANNEL_DHW, True, refresh=False))
    if PLANT == "channel253" and surface == "channel" and i == 253:
        asyncio.run(b.boost_mod.set_channel(c, b.boost_mod.CHANNEL_SPACE, True, refresh=False))
    if PLANT == "param253" and surface == "mode" and i == 253:
        c._thermal_model.params.heat_pump_max_power = 5.0  # outside the trace
    orig(st, i, surface)
b.cycle = planted
b.check_fork()
print("RESULT plant", PLANT, "check_fork rc", b.R.close("FORK"))
