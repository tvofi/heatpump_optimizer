# == REVIEWER-REPRO upstream debouncer trailing refresh (2025.2.0 debounce.py, verbatim)
import asyncio as _rv_aio
_rv_src = open("/Users/timmalmstrom/hpo-seats/r11/rev-3738-28977/ha/debounce.py").read()
_rv_src = _rv_src.replace("from homeassistant.core import HassJob, HomeAssistant, callback", "")
class _RvJob:
    def __init__(self, target, name=None, **kw):
        self.target = target
    def __repr__(self): return "job"
_rv_ns = {"HassJob": _RvJob, "HomeAssistant": object, "callback": (lambda f: f), "__name__": "rv_debounce"}
exec(compile(_rv_src, "upstream-debounce.py", "exec"), _rv_ns)
_RvDebouncer = _rv_ns["Debouncer"]

def _rv_task(loop, coro, name=None, eager_start=True):
    return _rv_aio.Task(coro, loop=loop, name=name, eager_start=eager_start)

async def _rv_run(origin, write):
    _hass, _entry, coord = _r9f13_make(f"rv_{origin}_{write}")
    loop = _rv_aio.get_running_loop()
    coord.hass.loop = loop
    coord.hass.async_create_task = lambda coro, name=None, eager_start=True: _rv_task(loop, coro, name, eager_start)
    coord.hass.async_create_background_task = lambda coro, name=None, eager_start=True: _rv_task(loop, coro, name, eager_start)
    coord.hass.async_run_hass_job = lambda job, *a, background=False: _rv_task(loop, job.target(*a))
    import logging as _rv_log
    coord._debounced_refresh = _RvDebouncer(coord.hass, _rv_log.getLogger("rv"), cooldown=0.05, immediate=True, function=coord.async_refresh)
    async def _solve():
        return None
    coord.async_run_optimization = _solve
    real_state = coord._update_current_state
    cycles, order = [], []
    async def _state_with_write():
        cycles.append(1); n = len(cycles); order.append(f"s{n}")
        await _rv_aio.sleep(0)
        await real_state()
        if write and n == 1:
            await coord.async_request_refresh()  # a user write mid-refresh, not solving
    coord._update_current_state = _state_with_write
    real_build = coord._build_data_dict
    def _built(*a, **k):
        order.append(f"e{len(cycles)}")
        return real_build(*a, **k)
    coord._build_data_dict = _built
    if origin == "debounced":
        await coord.async_request_refresh()
    else:
        await coord.async_refresh()
    for _ in range(40):
        await _rv_aio.sleep(0.02)
    return len(cycles), " ".join(order)

for _o in ("debounced", "direct"):
    for _w in (True, False):
        _r = _rv_aio.run(_rv_run(_o, _w))
        print(f"RV origin={_o} write={_w} cycles={_r[0]} order={_r[1]}")
        R.check(f"RV {_o} write={_w}: cycles", _r[0] == (2 if _w else 1), f"{_r}")
