"""Verifier D1#2 V2 for D1-s3-06. Metric: integration ERROR records carrying exc_info over 5
consecutive _async_update_data calls whose body raises a persistent RuntimeError (once-per-outage
would be 1). Null: the body raises UpdateFailed (latch path) -> 0. Unbound call on a namespace self."""
import asyncio, logging
from types import SimpleNamespace
from heatpump_optimizer import coordinator as c
from homeassistant.helpers.update_coordinator import UpdateFailed
class H(logging.Handler):
    def __init__(s): super().__init__(); s.recs=[]
    def emit(s, r): s.recs.append(r)
h=H(); lg=logging.getLogger(c.__name__); lg.addHandler(h); lg.setLevel(logging.DEBUG)
async def run(exc):
    async def boom(): raise exc
    me=SimpleNamespace(_skip_solve_once=False, _refresh_task=None, _update_current_state=boom)
    n=0
    for _ in range(5):
        h.recs.clear()
        try: await c.HeatPumpOptimizerCoordinator._async_update_data(me)
        except UpdateFailed: pass
        n+=sum(1 for r in h.recs if r.levelno>=logging.ERROR and r.exc_info)
    return n
print("V2 06 error_tracebacks_over_5_failures=", asyncio.run(run(RuntimeError("stuck"))))
print("V2 06 null_updatefailed=", asyncio.run(run(UpdateFailed("x"))))
