# == REVIEWER-REPRO upstream debouncer trailing refresh
import asyncio as _rv_aio, types as _rv_types, sys as _rv_sys
from homeassistant.util import dt as _rv_dt
_rv_src = open("/tmp/claude-0/ha/unpacked/homeassistant/helpers/debounce.py").read()
_rv_src = _rv_src.replace("from homeassistant.core import HassJob, HomeAssistant, callback", "")
class _RvJob:
    def __init__(self, target, name=None, **kw):
        self.target = target
    def __repr__(self): return "job"
_rv_ns = {"HassJob": _RvJob, "HomeAssistant": object, "callback": (lambda f: f), "__name__": "rv_debounce"}
exec(compile(_rv_src, "upstream-debounce.py", "exec"), _rv_ns)
_RvDebouncer = _rv_ns["Debouncer"]

def _rv_eager(loop, coro, name=None):
    return _rv_aio.Task(coro, loop=loop, name=name, eager_start=True)

async def _rv_run(origin, write_phase):
    _hass, _entry, coord = _r9f13_make(f"rv_{origin}_{write_phase}")
    loop = _rv_aio.get_running_loop()
    coord.hass.loop = loop
    coord.hass.async_create_task = lambda coro, name=None, eager_start=True: _rv_eager(loop, coro, name)
    coord.hass.async_create_background_task = lambda coro, name=None, eager_start=True: _rv_eager(loop, coro, name)
    coord.hass.async_run_hass_job = lambda job, *a, background=False: _rv_eager(loop, job.target(*a))
    refreshes = []
    real_refresh = coord.async_refresh
    async def _counted():
        refreshes.append(1)
        await real_refresh()
    import logging as _rv_log
    coord._debounced_refresh = _RvDebouncer(coord.hass, _rv_log.getLogger("rv"), cooldown=0.05, immediate=True, function=_counted)
    async def _solve():
        return None
    coord.async_run_optimization = _solve
    real_state = coord._update_current_state
    wrote = []
    async def _state_with_write():
        await real_state()
        if not wrote:
            wrote.append(1)
            await coord.async_request_refresh()  # a user write mid-refresh, not solving
    coord._update_current_state = _state_with_write
    if origin == "debounced":
        await coord.async_request_refresh()
    else:
        await coord.async_refresh()
    for _ in range(40):
        await _rv_aio.sleep(0.02)
    return len(refreshes), len(wrote)

for _o in ("debounced", "direct"):
    _r = _rv_aio.run(_rv_run(_o, "fetch"))
    print(f"RV origin={_o} debouncer_refreshes={_r[0]} writes={_r[1]}")
    R.check(f"RV {_o}: the write mid-refresh is followed by one more refresh", (_r[0] if _o=='debounced' else _r[0]+1) == 2, f"{_r}")
