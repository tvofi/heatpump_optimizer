"""Shared bootstrap for the D10 verify-v3 real-Home-Assistant harnesses.

Not a harness: imported by realha_*.py in this directory. Environment shims
only, never a production change:
  * mashumaro (a real-HA dependency) calls issubclass(x, typing.ByteString),
    which CPython 3.14 removed; a stand-in ABC is registered before HA imports.
  * numpy/scipy/threadpoolctl are linked from the CI venv
    ($HPO_NP_SITE, default /home/claude/venv/lib/python3.14/site-packages)
    into a private temp dir on sys.path (the HA venv has none).
  * custom_components/ is symlinked into a temp HA config dir, so HA's own
    loader imports the integration as custom_components.heatpump_optimizer.
  * the manifest's 'http' dependency is marked loaded and hass.http is a
    stand-in whose static-path registration is a no-op (the card's files).
Everything else -- FlowManager, OptionsFlowManager, ConfigEntries setup and
retry, DataUpdateCoordinator, Debouncer, service calls, entity platforms,
translations -- is the real homeassistant 2026.2.3 package.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import abc
import sys
import tempfile
import time
import typing

assert "hastub" not in os.environ.get("PYTHONPATH", ""), "run WITHOUT tests/hastub"
assert "hastub" not in "".join(sys.path), "run WITHOUT tests/hastub"
if not hasattr(typing, "ByteString"):
    class _ByteString(abc.ABC):
        pass
    for _t in (bytes, bytearray, memoryview):
        _ByteString.register(_t)
    typing.ByteString = _ByteString

REPO = os.getcwd()
TMP = tempfile.mkdtemp(prefix="d10v3_")
_np_site = os.environ.get("HPO_NP_SITE", "/home/claude/venv/lib/python3.14/site-packages")
_np_dir = os.path.join(TMP, "np")
os.makedirs(_np_dir)
for _n in os.listdir(_np_site):
    if _n.split("-")[0].split(".")[0] in ("numpy", "scipy", "threadpoolctl"):
        os.symlink(os.path.join(_np_site, _n), os.path.join(_np_dir, _n))
sys.path.insert(0, _np_dir)
CONFIG_DIR = os.path.join(TMP, "config")
os.makedirs(CONFIG_DIR)
os.symlink(os.path.join(REPO, "custom_components"), os.path.join(CONFIG_DIR, "custom_components"))
sys.path.insert(0, CONFIG_DIR)
# the integration's solve runs in a spawned process worker, which inherits
# the environment, not sys.path
os.environ["PYTHONPATH"] = os.pathsep.join([_np_dir, CONFIG_DIR])

import homeassistant  # noqa: E402
from homeassistant import config_entries, core, loader  # noqa: E402
from homeassistant.const import __version__ as HA_VERSION  # noqa: E402,F401
from homeassistant.helpers import device_registry as dr  # noqa: E402
from homeassistant.helpers import entity_registry as er  # noqa: E402
from homeassistant.helpers import issue_registry as ir  # noqa: E402

assert "hastub" not in homeassistant.__file__, homeassistant.__file__
DOMAIN = "heatpump_optimizer"


class _Http:
    async def async_register_static_paths(self, *a, **k):
        return None

    def register_static_path(self, *a, **k):
        return None


async def make_hass():
    cfg = tempfile.mkdtemp(prefix="cfg_", dir=TMP)  # fresh .storage per hass
    os.symlink(os.path.join(REPO, "custom_components"), os.path.join(cfg, "custom_components"))
    hass = core.HomeAssistant(cfg)
    hass.config.skip_pip = True
    await hass.config.async_set_time_zone("Europe/Stockholm")
    loader.async_setup(hass)
    await dr.async_load(hass)
    await er.async_load(hass)
    await ir.async_load(hass)
    hass.config_entries = config_entries.ConfigEntries(hass, {})
    await hass.config_entries.async_initialize()
    hass.set_state(core.CoreState.running)
    hass.config.components.add("http")
    hass.http = _Http()
    return hass


class Resp:
    def __init__(self, status, payload=None):
        self.status = status
        self._payload = payload if payload is not None else {"data": {"viewer": {"name": "Home"}}}

    async def json(self, *a, **k):
        return self._payload

    async def text(self):
        return ""

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class Session:
    """aiohttp-session stand-in: every POST answers `status` (counted)."""

    def __init__(self, status=200, payload=None, exc=None):
        self.status, self.payload, self.exc, self.posts = status, payload, exc, 0

    def post(self, *a, **k):
        self.posts += 1
        if self.exc is not None:
            raise self.exc
        return Resp(self.status, self.payload)


class Clock:
    def __init__(self):
        self.p, self.t = time.process_time(), time.thread_time()


def footer(clock):
    pc, tc = time.process_time() - clock.p, time.thread_time() - clock.t
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
    except Exception:  # noqa: BLE001
        sw = "na"
    print(f"RESULT swapins={sw}")
