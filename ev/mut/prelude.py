def _solve_record_now(coord):
    """The record a solve started now would plan with (#1736): what the
    solve's tail -- the fuse advisor, the price tiles -- is handed."""
    from homeassistant.util import dt as _rec_dt
    from heatpump_optimizer.plan_step import plan_step_start

    now = _rec_dt.now()
    return coord._solve_record(plan_step_start(now), coord._forecast_arrays(now))
import asyncio as _asyncio
from harness import FakeEntry as _FakeEntry, FakeHass as _FakeHass
from homeassistant.util import dt as dt_util
class _SolveHass(_FakeHass):
    """Real tasks, a recording service registry, and a holdable executor.

    ``spawn_real`` is off while the coordinator is constructed, so the ten
    fire-and-forget store loads `__init__` spawns are closed rather than run:
    the simulated disk is class-level and shared across this whole file, and a
    timestamp some earlier case wrote is not an input these checks want.
    """

    spawn_real = False

    def __init__(self, states=None) -> None:
        super().__init__(states)
        self.state_listeners = []
        self.entered = None
        self.release = None

    def async_create_task(self, coro, name=None, eager_start=None):
        if not self.spawn_real:
            coro.close()
            return None
        try:
            loop = _asyncio.get_running_loop()
        except RuntimeError:
            coro.close()
            return None
        return loop.create_task(coro)

    async def async_add_executor_job(self, func, *args):
        if self.entered is not None:
            self.entered.set()
        if self.release is not None:
            await self.release.wait()
        return func(*args)
def _solve_coord() -> Coord:
    """A coordinator with prices and forecasts, ready to solve.

    The horizon is anchored on the real clock rather than a fixed day, so the
    published prices are the ones `_forecast_arrays` picks up and the solve
    genuinely runs -- a horizon in the past yields "no_prices" and the
    executor is never reached at all.
    """
    hass = _SolveHass(
        {
            "sensor.indoor": FakeState("21.0", unit="°C"),
            "sensor.outdoor": FakeState("-5.0", unit="°C"),
        }
    )
    coord = Coord(
        hass,
        _FakeEntry(
            data={
                "tibber_token": "x",
                "weather_entity": "weather.home",
                "heat_pump_switch_entity": "switch.heat_pump",
                "indoor_temp_entity": "sensor.indoor",
                "outdoor_temp_entity": "sensor.outdoor",
                # R5-D12-01: the cycle's two MQTT actuations are part of
                # what the #237 guards must let through and then stop, so
                # this solve coordinator carries a CONFIGURED ECL110
                # surface -- unconfigured, the fix on this branch removes
                # the publishes and the null control's 3-call arm would
                # pin nothing about the guards.
                "ecl110_displace_set_topic": "ecl_solve/set",
                "ecl110_command_topic": "ecl_solve/command",
            }
        ),
    )
    hass.spawn_real = True
    coord._skip_solve_once = False
    _t0 = dt_util.now().replace(minute=0, second=0, microsecond=0) - timedelta(
        hours=1
    )
    coord._prices = [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (_t0 + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]
    coord._weather_forecast = [
        {
            "datetime": (_t0 + timedelta(hours=h)).isoformat(),
            "temperature": -5.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [0.0] * 48

    async def _noop():
        return None

    for _name in (
        "_update_current_state",
        "_fetch_tibber_prices",
        "_fetch_weather_forecast",
        "_fetch_solar_forecast",
        "_async_learn_price_shape",
    ):
        setattr(coord, _name, _noop)
    return coord
import heatpump_optimizer.coordinator as _st_cmod  # noqa: E402
from heatpump_optimizer import whatif as _st_whatif  # noqa: E402
from homeassistant.util import dt as _st_dt  # noqa: E402
class _StSeams:
    """Both await seams of ``coordinator``, counted; the pair's seam can be
    made to raise, and the process worker to be unavailable."""

    def __init__(self, pair_error=None, worker_error=None):
        self.optimize, self.off_loop, self.built = [], [], []
        self._pair_error, self._worker_error = pair_error, worker_error
        self._real = (_st_cmod._await_optimize, _st_cmod._await_off_loop,
                      _st_cmod._await_process, _st_cmod._warm_seeded,
                      _st_cmod.SolveRecord.optimizer)

    def __enter__(self):
        real_opt, real_off, real_proc, real_seed, real_rec = self._real

        async def _opt(hass, optimizer, inputs):
            self.optimize.append((optimizer, inputs))
            return await real_opt(hass, optimizer, inputs)

        async def _off(hass, fn, *args):
            if fn is _st_cmod.optimize_in_process:
                self.off_loop.append(args)
                if self._pair_error is not None:
                    raise self._pair_error
            return await real_off(hass, fn, *args)

        async def _proc(hass, fn, *args):
            if self._worker_error is not None:
                raise self._worker_error
            return await real_proc(hass, fn, *args)

        def _seed(coord, optimizer):
            self.built.append(optimizer)
            return real_seed(coord, optimizer)

        def _rec(record):
            made = real_rec(record)
            self.built.append(made)
            return made

        _st_cmod._await_optimize, _st_cmod._await_off_loop = _opt, _off
        _st_cmod._await_process, _st_cmod._warm_seeded = _proc, _seed
        _st_cmod.SolveRecord.optimizer = _rec
        return self

    def __exit__(self, *exc):
        (_st_cmod._await_optimize, _st_cmod._await_off_loop, _st_cmod._await_process,
         _st_cmod._warm_seeded, _st_cmod.SolveRecord.optimizer) = self._real

    def counts(self):
        return len(self.optimize), len(self.off_loop)
async def _st_coord(start=None, extra=None):
    """A solved coordinator whose live house starts at ``start``."""
    coord = _solve_coord()
    if extra:
        with_config(coord, extra)
    if start is not None:
        live = getattr(coord, "_ctx", coord)._current_state
        live.room_temperature = live.upper_floor_temperature = live.lower_floor_temperature = start[0]
        live.slab_temperature = start[1]
    coord._fuse_advisor_at = _st_dt.now()  # the seeding solve runs no advisor
    await coord.async_run_optimization()
    return coord
