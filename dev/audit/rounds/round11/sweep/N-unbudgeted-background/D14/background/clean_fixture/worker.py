"""Null-control fixture: one background solve, behind an in-flight guard."""


async def _await_optimize(hass, opt, inputs):  # infrastructure: excluded
    return await hass.async_add_executor_job(opt.solve, inputs)


class Coord:
    def __init__(self):
        self._whatif_task = None

    async def async_whatif(self, overrides):
        if self._whatif_task is not None and not self._whatif_task.done():
            return None
        return await _await_optimize(self.hass, self.opt, overrides)
