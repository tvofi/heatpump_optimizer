"""Judge's own D10-16 mode-specificity driver.

Replicates the B-harness seam from first principles: real
HeatPumpOptimizerCoordinator._async_update_data driven through a fake
clientsession, per failure mode: 5 failed polls + 1 recovery.
Counts ERROR-level records from heatpump_optimizer loggers during the 5
failed polls, the tibber latch value before recovery, and the recovery INFO.
Run from the export root:
  PYTHONPATH=tests/hastub python /tmp/hpo-d10-judge/judge_d10_16_modes.py
"""
import asyncio
import logging
import os
import sys

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import aiohttp  # noqa: E402
import harness as hh            # tests/harness.py: FakeHass/FakeEntry  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

DATA = {
    const.CONF_TIBBER_TOKEN: "SECRET-TOKEN-judge",
    const.CONF_WEATHER_ENTITY: "weather.home",
    const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_a",
}
TIBBER_OK = {
    "data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": {
        "today": [{"total": 0.42, "startsAt": "2026-09-02T00:00:00Z",
                   "level": "NORMAL"}],
        "tomorrow": [],
    }}}]}}
}


class Resp:
    def __init__(self, status, payload=None):
        self.status = status
        self._p = payload

    async def json(self):
        return self._p

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False


class Sess:
    def __init__(self, script):
        self._s = list(script)

    def post(self, *a, **k):
        e = self._s.pop(0)
        if isinstance(e, Exception):
            raise e
        return Resp(*e)

    async def close(self):
        return None


async def _noop(*a, **k):
    return None


def _nosync(*a, **k):
    return None


class Entry(hh.FakeEntry):
    def async_start_reauth(self, hass):
        self.reauth_calls = getattr(self, "reauth_calls", 0) + 1
        return True

    async def async_reload(self, entry_id):
        return True


def make():
    entry = Entry(data=dict(DATA))
    c = HeatPumpOptimizerCoordinator(hh.FakeHass(), entry)
    c.config_entry = entry
    for n in ("_update_current_state", "_fetch_weather_forecast",
              "_fetch_solar_forecast", "_async_learn_price_shape",
              "_apply_action", "_command_frequency", "_async_drive_pumps",
              "_async_save_accuracy", "_async_save_energy_totals",
              "_async_watch_learning_drift"):
        setattr(c, n, _noop)
    for n in ("_record_accuracy", "_track_realised_peak"):
        setattr(c, n, _nosync)
    c._mode = const.MODE_OFF
    return c


class Cap(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.recs = []

    def emit(self, r):
        if "heatpump_optimizer" in r.name:
            self.recs.append((r.levelno, r.getMessage()))


async def poll(c, script):
    real = coord_mod.async_get_clientsession
    coord_mod.async_get_clientsession = lambda hass, **k: Sess(script)
    try:
        await c._async_update_data()
    except Exception:
        pass
    finally:
        coord_mod.async_get_clientsession = real


async def run_mode(name, fail_entry):
    c = make()
    cap = Cap()
    root = logging.getLogger()
    root.addHandler(cap)
    root.setLevel(logging.DEBUG)
    try:
        for _ in range(5):
            await poll(c, [fail_entry])
        errs = [m for lvl, m in cap.recs if lvl >= logging.ERROR]
        cycles = getattr(c, "_tibber_outage_cycles", None)
        cap.recs.clear()
        await poll(c, [(200, TIBBER_OK)])
        rec = list(cap.recs)
    finally:
        root.removeHandler(cap)
    info = [m for lvl, m in rec if lvl == logging.INFO and "recovered" in m]
    print(f"RESULT mode={name} error_records_during_5_polls={len(errs)} "
          f"outage_cycles_after_5_polls={cycles} "
          f"recovery_msg={info[0] if info else '<none>'!r}")


async def main():
    await run_mode("http_500(in-try)", (500, None))
    await run_mode("connect_failure(except-clienterror)",
                   aiohttp.ClientConnectionError("refused"))
    await run_mode("http_401(in-try)", (401, None))
    await run_mode("graphql_errors(in-try)",
                   (200, {"errors": [{"message": "bad token"}]}))
    await run_mode("no_homes(in-try)", (200, {"data": {"viewer": {"homes": []}}}))

asyncio.run(main())
