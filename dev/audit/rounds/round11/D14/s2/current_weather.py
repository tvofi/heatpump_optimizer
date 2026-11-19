"""N-no-expiry seam (D14-s2, round 11): _current_weather books forecast entry 0 as "now" at any age.

Metric: over a weather-fetch outage of H = 1..72 h after the last good fetch
(hourly rows, 48 of them, row i's wind = 10 + i m/s so every row is
distinguishable), the number of hours at which
``HeatPumpOptimizerCoordinator._current_weather()`` returns a wind that is not
the wind of the row covering now (or returns one when no row covers now, past
the 48 h horizon). Key: the wind the production method returns, compared with
the row ``coordinator._covering_index`` (the class's own end-bounded helper)
picks over the same rows at the same instant.

Also read: the diagnosis record's booked ``planned.wind_speed``
(``_capture_diagnosis_inputs``) at H = 30, and the fixed sibling
``coordinator.forecast_outdoor_now`` over the same rows (null control: its
mismatch count is 0, since #2229 bounded it, and it returns None past the
horizon).

Perturbation: ``--perturb covering`` swaps ``_current_weather`` in memory for
the same body indexed by ``_covering_index`` (what forecast_outdoor_now
does) -> mismatch count 72 -> 0.

Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/s2/current_weather.py [--perturb covering]
Expected at 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (box B7, linux), exact:
  RESULT wind_mismatch_hours=72 (of 72), RESULT outdoor_sibling_mismatch_hours=0,
  RESULT booked_planned_wind_h30=10.0 (the covering row's is 40.0), RESULT h0_match=1;
  under --perturb covering: wind_mismatch_hours=0.
"""
import os

for _threads in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_threads, "1")

import argparse
import sys
import time
from datetime import timedelta

sys.path.insert(0, "tests")
import harness  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as cmod  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

ROWS = 48


def _rows(fetched_at):
    return [
        {
            "datetime": (fetched_at + timedelta(hours=i)).isoformat(),
            "temperature": -5.0 + i * 0.1,
            "wind_speed": 10.0 + i,
            "precipitation": 0.0,
        }
        for i in range(ROWS)
    ]


def _covering_wind(rows, now):
    starts = [cmod._comparable_ts(r["datetime"], now) for r in rows]
    i = cmod._covering_index(starts, now, timedelta(hours=1))
    return None if i is None else rows[i]["wind_speed"]


def _covering_current_weather(self):
    # The perturbation: the same body, indexed by the class's helper.
    if self._weather_forecast:
        now = dt_util.now()
        w = _covering_wind(self._weather_forecast, now)
        return (0.0 if w is None else max(0.0, float(w)), 0.0)
    return 0.0, 0.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", choices=("none", "covering"), default="none")
    a = ap.parse_args()
    if a.perturb == "covering":
        HeatPumpOptimizerCoordinator._current_weather = _covering_current_weather
    t0, c0 = time.thread_time(), time.process_time()
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.0"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    coord = HeatPumpOptimizerCoordinator(
        hass,
        FakeEntry(data={const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor", const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor"}),
    )
    mismatch = sibling_mismatch = 0
    h0 = None
    booked_h30 = None
    for h in range(0, 73):
        now = dt_util.now()
        # Half an hour into the hour, so no instant sits on a row boundary.
        rows = _rows(now - timedelta(hours=h, minutes=30))
        coord._weather_forecast = rows
        got = coord._current_weather()[0]
        want = _covering_wind(rows, now)
        ok = (got == want) if want is not None else (got == 0.0)
        out = cmod.forecast_outdoor_now(rows, now)
        starts = [cmod._comparable_ts(r["datetime"], now) for r in rows]
        idx = cmod._covering_index(starts, now, timedelta(hours=1))
        out_want = None if idx is None else rows[idx]["temperature"]
        if h == 0:
            h0 = int(ok)
        else:
            mismatch += int(not ok)
            sibling_mismatch += int(out != out_want)
        if h == 30:
            try:
                d = coord._capture_diagnosis_inputs()
                booked_h30 = None if d is None else d["planned"]["wind_speed"]
            except Exception as err:  # noqa: BLE001
                booked_h30 = f"error:{err!r}"
            print(f"# h=30 covering-row wind {want}, _current_weather {got}")
    print(f"RESULT h0_match={h0}")
    print(f"RESULT wind_mismatch_hours={mismatch} hours (of 72)")
    print(f"RESULT outdoor_sibling_mismatch_hours={sibling_mismatch} hours (of 72)")
    print(f"RESULT booked_planned_wind_h30={booked_h30} m/s")
    tf = (time.process_time() - c0) / max(time.thread_time() - t0, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as f:
            print("RESULT swapins=" + next(l.split()[1] for l in f if l.startswith("pswpin")))
    except OSError:
        print("RESULT swapins=unknown")
    return 0


if __name__ == "__main__":
    sys.exit(main())
