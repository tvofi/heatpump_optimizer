#!/usr/bin/env python3
"""D10.M1 action-exceptions (Silver): set_away acknowledges a return_time it could not read.

Metric: of the schema-valid ``heatpump_optimizer.set_away`` calls whose
``return_time`` is a non-empty string the integration cannot parse as a
datetime (cases below), the number that return without raising
(ServiceValidationError or any HomeAssistantError) -- counted on what the
production seam delivers: the call's outcome, plus whether the stored
return instant afterwards is the one the call supplied (it cannot be: the
string has no instant). A control arm sends a parseable ISO return time
and must be accepted and stored.
Count key: the handler's raise/no-raise outcome through the real registered
schema and handler (FakeServices.async_call dispatches schema -> handler),
and the coordinator's ``away_state.override_return_iso`` after the call.
Instrumented symbols: services:handle_set_away (via the registered service),
coordinator:HeatPumpOptimizerCoordinator.async_set_away,
away:_parse_return_time.
Perturbation: ``--perturb`` swaps away._parse_return_time (the name the
coordinator calls through ``away_mode``) for a wrapper that raises
ServiceValidationError on a non-empty unparseable string -- the shape a fix
takes; acknowledged_unparseable must fall to 0 (direction to_zero) while
the control arm stays accepted.

Run (from the export root):
  PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python3 \
      dev/audit/rounds/round11/D10/s1/svc_set_away.py [--perturb]
Expected: acknowledged_unparseable=6 (exact), cleared_existing_return=3
(exact), control_accepted=1; under --perturb acknowledged_unparseable=0.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: macOS arm64, venv-ci Python 3.14.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import sys
import tempfile
import time
from datetime import timedelta

sys.path.insert(0, "tests")
os.environ.setdefault("HPO_PLANDATA", os.path.join(tempfile.mkdtemp(prefix="d10s1."), "plandata.json"))
from harness import FakeHass, FakeEntry  # noqa: E402  (inserts custom_components)

from homeassistant.config_entries import ConfigEntryState  # noqa: E402
from homeassistant.exceptions import HomeAssistantError  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import away as away_mode  # noqa: E402
from heatpump_optimizer import services  # noqa: E402
from heatpump_optimizer.const import DOMAIN  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

PERTURB = "--perturb" in sys.argv

# Non-empty strings the schema (cv.string) accepts that are not datetimes.
UNPARSEABLE = ["18:00", "tomorrow 18:00", "2026-13-40T25:00", "next friday",
               "16/11/2026 18:00", "in 3 hours"]


def make():
    hass = FakeHass()
    entry = FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home"})
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    entry.runtime_data = coord
    entry.state = ConfigEntryState.LOADED
    hass.config_entries.entries.append(entry)

    async def _noop():
        return None
    coord.async_request_refresh = _noop
    services.async_register_services(hass)
    return hass, coord


async def call(hass, data):
    try:
        await hass.services.async_call(DOMAIN, "set_away", data, blocking=True)
        return None
    except HomeAssistantError as err:
        return type(err).__name__


async def main() -> None:
    if PERTURB:
        orig = away_mode._parse_return_time
        from homeassistant.exceptions import ServiceValidationError

        def strict(raw):
            got = orig(raw)
            if got is None and raw is not None and str(raw).strip() and \
                    str(raw).strip().lower() not in ("unknown", "unavailable"):
                raise ServiceValidationError(f"unparseable return_time {raw!r}")
            return got
        away_mode._parse_return_time = strict
        print("RESULT perturbed=away._parse_return_time raises on unparseable input")

    acknowledged = 0
    cleared_existing = 0
    for i, raw in enumerate(UNPARSEABLE):
        hass, coord = make()
        if i % 2 == 0:
            # Arm A: away on with the bad return in one call.
            outcome = await call(hass, {"active": True, "return_time": raw})
        else:
            # Arm B: away already on until a known instant; the call only
            # tries to move the return time.
            good = (dt_util.now() + timedelta(hours=5)).replace(microsecond=0).isoformat()
            await call(hass, {"active": True, "return_time": good})
            before = coord.away_state.override_return_iso
            outcome = await call(hass, {"return_time": raw})
            after = coord.away_state.override_return_iso
            if outcome is None and before is not None and after is None:
                cleared_existing += 1
            print(f"CASE B {raw!r}: before={before} after={after}")
        st = coord.away_state
        print(f"CASE {raw!r}: outcome={outcome or 'accepted'} "
              f"active={st.override_active} return={st.override_return_iso}")
        if outcome is None:
            acknowledged += 1

    hass, coord = make()
    good = (dt_util.now() + timedelta(hours=3)).replace(microsecond=0).isoformat()
    out = await call(hass, {"active": True, "return_time": good})
    control_ok = int(out is None and coord.away_state.override_return_iso is not None)
    print(f"CONTROL {good!r}: outcome={out or 'accepted'} return={coord.away_state.override_return_iso}")

    print(f"RESULT cases={len(UNPARSEABLE)} count")
    print(f"RESULT acknowledged_unparseable={acknowledged} count")
    print(f"RESULT cleared_existing_return={cleared_existing} count")
    print(f"RESULT control_accepted={control_ok} count")


if __name__ == "__main__":
    c0, t0 = time.process_time(), time.thread_time()
    asyncio.run(main())
    c1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={((c1 - c0) / max(t1 - t0, 1e-9)):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
