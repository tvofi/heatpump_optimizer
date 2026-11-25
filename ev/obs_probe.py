import asyncio, sys
sys.path.insert(0, "custom_components"); sys.path.insert(0, "tests/hastub")
from heatpump_optimizer import legionella as L
g = L.LegionellaGuard.__new__(L.LegionellaGuard)
called = []
async def _track(t): called.append(("track", t))
async def _cycle(t): called.append(("cycle", t))
class _D:
    def observe(self, r): pass
class _O:
    def check(self, *a): pass
g.async_track = _track; g.async_track_cycle = _cycle
g.disinfect = _D(); g.off_step = _O(); g._params = lambda: None; g._config = None
g.check_ceiling = lambda: None; g.check_overdue = lambda: None; g.hours_since = lambda: 1.0
asyncio.run(g.async_observe(55.0, None))
print("async_observe ran follower:", ("cycle", 55.0) in called, called)
