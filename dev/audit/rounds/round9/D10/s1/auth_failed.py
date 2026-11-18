"""D10-s1 test-before-setup / reauthentication-flow: how a refused token surfaces.

Metric: over five Tibber-response arms, count
  auth_as_transient = arms whose Tibber answer is an authentication refusal
                      (HTTP 401/403) where the exception the production code
                      delivers to Home Assistant is NOT auth-class
                      (ConfigEntryAuthFailed, or an exception named so) -- i.e.
                      it arrives as ConfigEntryNotReady / UpdateFailed, which HA
                      treats as transient and retries.
  transient_ok      = control arms (HTTP 500, connection error) delivered as
                      ConfigEntryNotReady / UpdateFailed (should stay 2 of 2).
Count key: the class of the exception escaping heatpump_optimizer.async_setup_entry
(setup arms) or HeatPumpOptimizerCoordinator._fetch_tibber_prices (the steady
cycle arm), classified by class name; not an input attribute.

Arms: setup_401, setup_403, steady_401 (auth refusals); control setup_500,
setup_conn_error.

Perturbation: --fix wraps HeatPumpOptimizerCoordinator._fetch_tibber_prices
so that, when the fetch fails after _tibber_start_reauth fired, it raises a
ConfigEntryAuthFailed (defined here as an IntegrationError subclass, because
tests/hastub has no such class -- the stub gap is recorded in the report) and
the harness's first refresh re-raises it as upstream's
async_config_entry_first_refresh does. Expected: baseline auth_as_transient=3,
--fix auth_as_transient=0; transient_ok=2 in both.

Run (from the export root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D10/s1/auth_failed.py [--fix]
Expected +- 0 (counts). Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1,
machine: audit box B1 (Linux container). Root rule: cwd (sys.path 'tests').
"""
from __future__ import annotations

import os

for _var in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_var, "1")

import asyncio  # noqa: E402
import logging  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
import heatpump_optimizer as integration  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as coordinator_module  # noqa: E402
from homeassistant import exceptions as ha_exc  # noqa: E402
from homeassistant.helpers import update_coordinator as uc  # noqa: E402

logging.disable(logging.CRITICAL)
FIX = "--fix" in sys.argv

AuthFailed = getattr(ha_exc, "ConfigEntryAuthFailed", None)
STUB_HAS_AUTH_FAILED = AuthFailed is not None
if AuthFailed is None:
    class ConfigEntryAuthFailed(ha_exc.IntegrationError):
        """Upstream: homeassistant.exceptions.ConfigEntryAuthFailed."""

    AuthFailed = ConfigEntryAuthFailed

if FIX:
    Coord = coordinator_module.HeatPumpOptimizerCoordinator
    _orig_fetch = Coord._fetch_tibber_prices

    async def _fetch(self):
        try:
            await _orig_fetch(self)
        except uc.UpdateFailed as err:
            if self._tibber_reauth_started:
                raise AuthFailed(str(err)) from err
            raise

    Coord._fetch_tibber_prices = _fetch
    def _auth_in_chain(err):
        # The fix's second line: the update wrappers (_async_update_data,
        # _async_first_refresh_light) pass ConfigEntryAuthFailed through
        # instead of re-wrapping it in UpdateFailed; modelled by walking the
        # cause chain rather than editing the wrappers on disk.
        seen = 0
        while err is not None and seen < 8:
            if isinstance(err, AuthFailed):
                return err
            err = err.__cause__ or err.__context__
            seen += 1
        return None

    async def _first(self):
        # Upstream's first refresh re-raises ConfigEntryAuthFailed as-is.
        try:
            self.data = await self._async_update_data()
            self.last_update_success = True
        except Exception as err:  # noqa: BLE001
            auth = _auth_in_chain(err)
            if auth is not None:
                raise auth
            self.last_exception = err
            self.last_update_success = False
            raise ha_exc.ConfigEntryNotReady() from err

    uc.DataUpdateCoordinator.async_config_entry_first_refresh = _first


class Resp:
    def __init__(self, status):
        self.status = status

    async def json(self):
        return None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class Session:
    def __init__(self, answer):
        self.answer = answer
        self.posts = 0

    def post(self, *a, **k):
        self.posts += 1
        if isinstance(self.answer, Exception):
            raise self.answer
        return Resp(self.answer)


def make(answer):
    session = Session(answer)
    coordinator_module.async_get_clientsession = lambda hass, verify_ssl=True: session
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.0"))
    entry = FakeEntry(data={
        const.CONF_TIBBER_TOKEN: "revoked",
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    })
    entry.reauth_started = 0

    def start_reauth(hass_):
        entry.reauth_started += 1

    entry.async_start_reauth = start_reauth
    return hass, entry, session


def classify(exc):
    if exc is None:
        return "none"
    name = type(exc).__name__
    return "auth" if name == "ConfigEntryAuthFailed" else f"transient:{name}"


async def setup_arm(answer):
    hass, entry, session = make(answer)
    try:
        await integration.async_setup_entry(hass, entry)
        exc = None
    except Exception as err:  # noqa: BLE001 - the delivered class is the metric
        exc = err
    return classify(exc), entry.reauth_started, session.posts


async def steady_arm(answer):
    hass, entry, session = make(answer)
    coord = coordinator_module.HeatPumpOptimizerCoordinator(hass, entry)
    try:
        await coord._fetch_tibber_prices()
        exc = None
    except Exception as err:  # noqa: BLE001
        exc = err
    return classify(exc), entry.reauth_started, session.posts


async def main():
    arms = [
        ("setup_401", True, setup_arm, 401),
        ("setup_403", True, setup_arm, 403),
        ("steady_401", True, steady_arm, 401),
        ("setup_500", False, setup_arm, 500),
        ("setup_conn_error", False, setup_arm, OSError("unreachable")),
    ]
    auth_transient = transient_ok = 0
    for name, is_auth, fn, answer in arms:
        cls, reauth, posts = await fn(answer)
        if is_auth and cls != "auth":
            auth_transient += 1
        if not is_auth and cls.startswith("transient"):
            transient_ok += 1
        print(f"arm={name:17s} delivered={cls:36s} reauth_flows_started={reauth} tibber_posts={posts}")
    print(f"MODE {'fix' if FIX else 'baseline'}  stub_has_ConfigEntryAuthFailed={STUB_HAS_AUTH_FAILED}")
    print(f"RESULT auth_as_transient={auth_transient} arms")
    print(f"RESULT transient_ok={transient_ok} arms")
    print(f"RESULT arms={len(arms)} count")


t0p, t0t = time.process_time(), time.thread_time()
asyncio.run(main())
dp, dt = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={dp / dt if dt else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    with open("/proc/vmstat") as fh:
        print("RESULT swapins=" + next(l.split()[1] for l in fh if l.startswith("pswpin")))
except (OSError, StopIteration):
    print("RESULT swapins=unknown")
