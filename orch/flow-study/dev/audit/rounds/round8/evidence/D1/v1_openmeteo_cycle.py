"""D1 verifier v1 (round 8), own harness for D1-s3-01.

Metric (one line): of N valid-JSON Open-Meteo bodies whose `hourly` or
`minutely_15` member has the wrong shape, count those for which one full
coordinator refresh cycle (async_refresh -> _async_update_data, Open-Meteo
solar source selected, auto mode, real solve) ends with last_update_success
False; per failed cycle also record whether it actuated (_apply_action ran).
Side arm (refresh gate): after a failed cycle, an immediate second cycle
(inside OPEN_METEO_MIN_REFRESH_MINUTES=20) is run with the same hostile body:
does it succeed because async_refresh skips the fetch?
Null control: a well-formed body (expect 0 failures).
Perturbations (in-process, restored in finally):
  --perturb=finder : the finder's stated one-liner, _parse_block returns _EMPTY
                     when `block` is not a dict.
  --perturb=fence  : async_refresh wrapped so any exception from the parse
                     is swallowed (the docstring's "never raises").
Command (tree root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D1/v1_openmeteo_cycle.py [--perturb=finder|fence]
Baseline cdf82daa; 4-vCPU shared cloud container; counts are final.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import timedelta  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, "tools/audit/round8/D1")

from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from heatpump_optimizer import open_meteo as om  # noqa: E402
from v1_setback_race import config, states  # noqa: E402

PERTURB = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--perturb=")), "")


def healthy_block(var_extra=True):
    now = dt_util.utcnow().replace(minute=0, second=0, microsecond=0)
    times = [(now + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M") for h in range(48)]
    b = {"time": times, "shortwave_radiation": [float(max(0, 300 - abs(h % 24 - 12) * 40)) for h in range(48)]}
    if var_extra:
        b["relative_humidity_2m"] = [80.0] * 48
        b["snowfall"] = [0.0] * 48
    return b


HOSTILE = {
    "hourly_list": {"hourly": [1, 2, 3]},
    "hourly_str": {"hourly": "shortwave_radiation"},
    "hourly_int": {"hourly": 7},
    "hourly_time_int": {"hourly": {"time": 5, "shortwave_radiation": [1.0, 2.0]}},
    "minutely_list": {"minutely_15": [0, 1]},
    "hourly_values_str": {"hourly": {"time": ["2026-09-23T00:00", "2026-09-23T01:00"], "shortwave_radiation": "ab"}},
}


class Resp:
    def __init__(self, body):
        self.status, self.body = 200, body

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def json(self, content_type=None):
        return self.body


class Session:
    def __init__(self, body):
        self.body = body

    def get(self, url, params=None, timeout=None):
        b = dict(self.body)
        b.setdefault("hourly", healthy_block())
        b.setdefault("minutely_15", {})
        return Resp(b)


async def one(body):
    coord = cm.HeatPumpOptimizerCoordinator(
        FakeHass(states()),
        FakeEntry(data={**config(), const.CONF_SOLAR_FORECAST_SOURCE: const.SOLAR_SOURCE_OPEN_METEO,
                        const.CONF_SOLAR_LOCATION: {"latitude": 59.3, "longitude": 18.0}}))
    await coord._update_current_state()
    acts = {"n": 0}
    orig = coord._apply_action

    async def counted():
        acts["n"] += 1
        return await orig()
    coord._apply_action = counted
    om.async_get_clientsession = lambda hass: Session(body)
    await coord.async_refresh()
    failed = int(not coord.last_update_success)
    actuated = acts["n"]
    await coord.async_refresh()  # immediately again: inside the 20-minute gate
    second_failed = int(not coord.last_update_success)
    return failed, actuated, second_failed


async def main():
    orig_parse, orig_refresh = om._parse_block, om.OpenMeteoSolar.async_refresh
    orig_sess = om.async_get_clientsession
    if PERTURB == "finder":
        def guarded(block, variable, max_value=om._MAX_PLAUSIBLE_GHI):
            if not isinstance(block, dict):
                return om._EMPTY
            return orig_parse(block, variable, max_value)
        om._parse_block = guarded
    elif PERTURB == "fence":
        async def fenced(self, now, force=False):
            try:
                return await orig_refresh(self, now, force)
            except Exception:  # noqa: BLE001
                return self.available
        om.OpenMeteoSolar.async_refresh = fenced
    out = {"failed": 0, "failed_actuated": 0, "second_cycle_failed": 0}
    try:
        for name, body in HOSTILE.items():
            f, a, s = await one(body)
            print(f"  shape={name}: failed={f} actuated={a} second_cycle_failed={s}")
            out["failed"] += f
            out["failed_actuated"] += a if f else 0
            out["second_cycle_failed"] += s
        cf, ca, cs = await one({})
        print(f"  control: failed={cf} actuated={ca} second_cycle_failed={cs}")
        out["control_failed"] = cf + cs
    finally:
        om._parse_block, om.OpenMeteoSolar.async_refresh = orig_parse, orig_refresh
        om.async_get_clientsession = orig_sess
        cm._shutdown_process_pool()
    out["shapes"] = len(HOSTILE)
    return out


if __name__ == "__main__":
    pc0, tc0 = time.process_time(), time.thread_time()
    res = asyncio.run(main())
    for k, v in res.items():
        print(f"RESULT {k}={v} count")
    pc, tc = time.process_time() - pc0, time.thread_time() - tc0
    print(f"RESULT thread_factor={pc / tc if tc else float('nan'):.3f}")
    print(f"RESULT load1={open('/proc/loadavg').read().split()[0]}")
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')]
    print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")
    print(f"RESULT perturbed={PERTURB or 0}")
