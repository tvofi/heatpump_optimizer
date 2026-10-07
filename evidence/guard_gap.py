"""Does check_fork notice a surface that acts BEFORE the first boosting cycle?
Plant: the channel arm enters a space boost at cycle 100 (day 2), outside
boosting_at. Stub solver (fork_equiv.stub_optimize)."""
import asyncio, sys
sys.argv = ["x", "stub"]
import fork_equiv as fe
from heatpump_optimizer.optimizer import HeatPumpOptimizer
HeatPumpOptimizer.optimize = fe.stub_optimize
b = fe.head
orig = b.cycle
def planted(st, i, surface):
    if surface == "channel" and i == 100:
        asyncio.run(b.boost_mod.set_channel(st["coord"], b.boost_mod.CHANNEL_SPACE, True, refresh=False))
    orig(st, i, surface)
b.cycle = planted
b.check_fork(); print("RESULT check_fork rc", b.R.close("FORK"))
arms = {"channel_boost": "channel"}
sh = b.replay(arms); un = b.replay(arms, fork=0)
d = fe.diff_fields(sh["channel_boost"], un["channel_boost"])
print("RESULT planted pre-fork surface action: shared vs unshared", "EQUAL" if not d else "DIFFERENT " + ",".join(d))
