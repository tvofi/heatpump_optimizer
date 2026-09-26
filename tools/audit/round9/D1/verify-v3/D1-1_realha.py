"""Shared bootstrap for verifier V3's real-Home-Assistant reach harnesses (unit D1-1).

Not a harness itself: each D1-s*_realha.py loads it with runpy/importlib.
Runs under the genuine ``homeassistant`` package (2026.2.3 in /root/venvha),
WITHOUT tests/hastub on the path:

    /root/venvha/bin/python tools/audit/round9/D1/verify-v3/<id>_realha.py

Environment shim, disclosed: Python 3.14 removed ``typing.ByteString``, which
mashumaro (pulled in by webrtc_models <- homeassistant.core_config) still
reads; ``typing.ByteString = bytes`` is set before any HA import. It touches no
production code path.
"""
import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")

import sys
import tempfile
import time
import typing

typing.ByteString = bytes  # py3.14 shim for mashumaro; see header

sys.path[:] = [p for p in sys.path if "hastub" not in p]
if "custom_components" not in sys.path:
    sys.path.insert(0, "custom_components")

_P0, _T0 = time.process_time(), time.thread_time()


def ha_version() -> str:
    from homeassistant.const import __version__
    return __version__


async def make_hass(tz: str = "Europe/Stockholm"):
    from homeassistant.core import HomeAssistant
    root = tempfile.mkdtemp(prefix="v3realha-", dir=os.environ.get("TMPDIR"))
    hass = HomeAssistant(root)
    await hass.config.async_set_time_zone(tz)
    from homeassistant.helpers import frame
    frame.async_setup(hass)  # bootstrap does this; hass.async_create_task's thread check needs it
    import threading
    hass.loop_thread_id = threading.get_ident()  # what hass.async_run/async_start set
    from homeassistant import loader
    loader.async_setup(hass)
    return hass


def make_entry(data: dict, entry_id: str = "v3_entry"):
    from types import MappingProxyType
    from homeassistant.config_entries import ConfigEntry
    return ConfigEntry(
        data=data, discovery_keys=MappingProxyType({}), domain="heatpump_optimizer",
        entry_id=entry_id, minor_version=1, options={}, source="user",
        subentries_data=None, title="HPO", unique_id=None, version=1,
    )


def tail(extra_cpu: float = 0.0) -> None:
    p, t = time.process_time() - _P0, time.thread_time() - _T0
    if extra_cpu:
        print(f"RESULT deliberate_thread_cpu={extra_cpu:.3f} s")
    print(f"RESULT thread_factor={(p - extra_cpu) / t if t else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except Exception:  # noqa: BLE001
        sw = "na"
    print(f"RESULT swapins={sw}")
    print(f"# homeassistant {ha_version()}")
