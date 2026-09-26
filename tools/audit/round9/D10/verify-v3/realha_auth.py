"""D10 verify-v3 (round 9), D10-s1-03 in REAL Home Assistant core 2026.2.3.

The entry is created by the real config flow (Tibber source; the token
validates against a stand-in session answering 200) and set up by the real
ConfigEntries; the coordinator's Tibber session is a counting stand-in whose
answer the arm sets. What is read is real HA's own end state.

Metrics (one line each):
  auth_as_transient  auth-refusal arms (setup 401, setup 403, steady 401) in
                     which real HA ends in the transient branch: at setup the
                     entry is SETUP_RETRY with a retry timer armed (not
                     SETUP_ERROR), on the steady cycle the coordinator has a
                     next poll scheduled (auth_failed would stop it);
  transient_ok       control arms (setup 500, setup connection error) in the
                     transient branch (SETUP_RETRY) -- should be 2 of 2;
  revoked_posts      Tibber POSTs with the refused token in the 40 s after the
                     first failure at setup (real retry backoff 5 s, 10 s, 20 s
                     ... runs in real time), summed over the two setup-auth arms;
  reauth_flows       reauth flows in progress per auth arm (the integration's
                     own _tibber_start_reauth), printed per arm.
Perturbation (--fix): HeatPumpOptimizerCoordinator._async_update_data wrapped
in memory so an UpdateFailed raised after _tibber_start_reauth fired is
re-raised as homeassistant.exceptions.ConfigEntryAuthFailed (the wrapper-level
fix). Expected: baseline auth_as_transient=3, transient_ok=2; --fix
auth_as_transient=0, transient_ok=2, revoked_posts drops to the first attempt
only (2: one per setup-auth arm). Exact (counts); revoked_posts is a wall-clock
window count, +-1 per arm.
Wall: ~3 min (real retry timers).

Run:  /home/claude/havenv/bin/python tools/audit/round9/D10/verify-v3/realha_auth.py [--fix]
      (from the repository root, WITHOUT tests/hastub on PYTHONPATH)
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence).
Machine: G2-V3 cloud container, 4 vCPU, CPython 3.14.0rc2, HA core 2026.2.3.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _realha as R  # noqa: E402

import asyncio  # noqa: E402
import logging  # noqa: E402
from datetime import timedelta  # noqa: E402

from homeassistant import config_entries  # noqa: E402
from homeassistant.exceptions import ConfigEntryAuthFailed  # noqa: E402
from homeassistant.helpers.update_coordinator import UpdateFailed  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

logging.basicConfig(level=logging.CRITICAL)
FIX = "--fix" in sys.argv
CLOCK = R.Clock()
WINDOW = float(os.environ.get("D10V3_WINDOW", "40"))

from custom_components.heatpump_optimizer import config_flow, const  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as coord_mod  # noqa: E402

Coord = coord_mod.HeatPumpOptimizerCoordinator
if FIX:
    _orig = Coord._async_update_data

    async def _update(self):
        try:
            return await _orig(self)
        except UpdateFailed as err:
            if self._tibber_reauth_started:
                raise ConfigEntryAuthFailed(str(err)) from err
            raise

    Coord._async_update_data = _update


def payload():
    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    rows = [{"total": 0.8 + 0.4 * ((i // 4) % 12) / 12.0,
             "startsAt": (now - timedelta(hours=1) + timedelta(minutes=15 * i)).isoformat(),
             "level": "NORMAL"} for i in range(4 * 49)]
    return {"data": {"viewer": {"name": "Home", "homes": [
        {"currentSubscription": {"priceInfo": {"today": rows, "tomorrow": []}}}]}}}


async def make_entry(hass, coord_session):
    config_flow.async_get_clientsession = lambda h, verify_ssl=True: R.Session(200, payload())
    coord_mod.async_get_clientsession = lambda h, verify_ssl=True: coord_session
    hass.states.async_set("weather.home", "sunny")
    hass.states.async_set("sensor.indoor", "21.0", {"unit_of_measurement": "°C", "device_class": "temperature"})
    mgr = hass.config_entries.flow
    r = await mgr.async_init(R.DOMAIN, context={"source": config_entries.SOURCE_USER})
    r = await mgr.async_configure(r["flow_id"], {
        "name": "HPO", const.CONF_TIBBER_TOKEN: "tok", const.CONF_WEATHER_ENTITY: "weather.home"})
    assert r.get("step_id") == "user_sensors", r
    r = await mgr.async_configure(r["flow_id"], {})
    for _ in range(6):
        if r["type"] in ("abort", "create_entry"):
            break
        r = await mgr.async_configure(r["flow_id"], {"next_step_id": "finish_now"} if r["type"] == "menu" else {})
    assert r["type"] == "create_entry", r
    await hass.async_block_till_done()
    return r["result"]


def reauth_flows(hass):
    return sum(1 for f in hass.config_entries.flow.async_progress_by_handler(R.DOMAIN)
               if f["context"].get("source") == config_entries.SOURCE_REAUTH)


async def setup_arm(answer):
    hass = await R.make_hass()
    sess = R.Session(answer) if not isinstance(answer, Exception) else R.Session(exc=answer)
    entry = await make_entry(hass, sess)
    first = sess.posts
    state0 = entry.state
    armed = entry._async_cancel_retry_setup is not None
    await asyncio.sleep(WINDOW)
    await hass.async_block_till_done()
    posts = sess.posts
    out = (state0, armed, entry.state, entry.reason, reauth_flows(hass), first, posts)
    await hass.async_stop(force=True)
    return out


async def steady_arm(answer):
    hass = await R.make_hass()
    sess = R.Session(200, payload())
    entry = await make_entry(hass, sess)
    assert entry.state is config_entries.ConfigEntryState.LOADED, (entry.state, entry.reason)
    await hass.async_block_till_done(wait_background_tasks=True)
    coord = entry.runtime_data
    sess.status, sess.payload = answer, None
    await coord.async_refresh()
    await hass.async_block_till_done()
    out = (coord.last_update_success, coord._unsub_refresh is not None, bool(coord._listeners),
           reauth_flows(hass), type(coord.last_exception).__name__)
    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_stop(force=True)
    return out


async def main():
    auth_transient = transient_ok = revoked = 0
    for name, is_auth, answer in (("setup_401", True, 401), ("setup_403", True, 403),
                                  ("setup_500", False, 500),
                                  ("setup_conn_error", False, OSError("unreachable"))):
        st0, armed, st1, reason, flows, first, posts = await setup_arm(answer)
        transient = st0 is config_entries.ConfigEntryState.SETUP_RETRY and armed
        if is_auth:
            auth_transient += int(transient)
            revoked += posts
        else:
            transient_ok += int(transient)
        print(f"arm={name:17s} state_after_setup={st0.name} retry_armed={armed} "
              f"state_after_{WINDOW:.0f}s={st1.name} reason={reason!r} reauth_flows={flows} "
              f"tibber_posts_first={first} tibber_posts_{WINDOW:.0f}s={posts}")
    ok, next_poll, listeners, flows, exc = await steady_arm(401)
    auth_transient += int(next_poll)
    print(f"arm=steady_401        last_update_success={ok} next_poll_scheduled={next_poll} "
          f"listeners={listeners} reauth_flows={flows} last_exception={exc}")
    print(f"MODE {'fix' if FIX else 'baseline'}  ha_version={R.HA_VERSION}")
    print(f"RESULT auth_as_transient={auth_transient} arms")
    print(f"RESULT transient_ok={transient_ok} arms")
    print(f"RESULT revoked_posts={revoked} posts (2 setup-auth arms, {WINDOW:.0f} s window each)")
    print("RESULT arms=5 count")


asyncio.run(main())
R.footer(CLOCK)
