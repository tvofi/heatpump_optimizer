"""Catch-up verifier arch-b, V2 for D7-s4-81: does REAL Home Assistant's Store hand Notifier a non-mapping
payload from a hand-edited .storage file, and does async_setup_notifier then raise?

Metric: setup_raises = number of on-disk payloads (written as HA's own storage envelope
{"version":1,"minor_version":1,"key":K,"data":D} under <tmp>/.storage/K) for which
notifier.async_setup_notifier raises, using a real homeassistant.core.HomeAssistant (no FakeHass).
Arms: D in {"x", [1], {"sent": "x"} (mapping control), {"sent": {"a": "b"}} (healthy control),
truncated JSON (parse error control), version 9 envelope (downgrade control)}.
Null control: the two mapping arms and the parse-error arm must read 0.
Perturbation (--perturb): Notifier.async_load is rebound in memory to route through
store.load_mapping (the P2 shape); setup_raises must fall to 0.

    ~/.local/state/hpo/venv-ha/bin/python dev/audit/rounds/round10/catchup/arch-b/v2_s4_notifier_realha.py [--perturb]

Expected at baseline 9061fbd3d (HA 2026.9 venv): setup_raises=2 (the "x" and [1] arms); --perturb 0.
Machine: seat macOS box; counts only. Writes only under a tempfile.mkdtemp root.
"""
import asyncio
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "custom_components"))
PERTURB = "--perturb" in sys.argv

from homeassistant.core import HomeAssistant  # noqa: E402

try:  # the HA venv carries no scipy; the solver is imported (store closure) but never run here
    import scipy.optimize  # noqa: F401
except ImportError:
    import importlib.abc
    import importlib.machinery
    import types as _t

    class _Stub(importlib.abc.MetaPathFinder, importlib.abc.Loader):
        def find_spec(self, name, path, target=None):
            if name == "scipy" or name.startswith("scipy."):
                return importlib.machinery.ModuleSpec(name, self, is_package=True)
            return None

        def create_module(self, spec):
            m = _t.ModuleType(spec.name)
            m.__path__ = []
            m.__getattr__ = lambda n: (lambda *a, **k: None)
            return m

        def exec_module(self, module):
            pass

    sys.meta_path.insert(0, _Stub())

from heatpump_optimizer import notifier, store  # noqa: E402

if PERTURB:
    async def _load(self):
        raw = await store.load_mapping(self._store, "notifier state")
        sent = raw.get("sent") if raw else None
        if isinstance(sent, dict):
            self._sent = {k: v for k, v in sent.items() if isinstance(k, str) and isinstance(v, str)}
            self._baseline = False
    notifier.Notifier.async_load = _load


class Entry:
    entry_id = "E1"

    def async_create_background_task(self, hass, coro, name=None):
        coro.close()

    def async_on_unload(self, f):
        pass


class Coord:
    data = None

    def async_add_listener(self, cb):
        return lambda: None


ARMS = [("str", "x"), ("list", [1]), ("map_bad_sent", {"sent": "x"}),
        ("healthy", {"sent": {"a": "b"}}), ("truncated", None), ("newer_version", {"sent": {}})]


async def one(label, data):
    tmp = tempfile.mkdtemp(prefix="archb-ha-")
    hass = HomeAssistant(tmp)
    key = f"{notifier.DOMAIN}_E1_notifier"
    sd = Path(tmp) / ".storage"
    sd.mkdir()
    if label == "truncated":
        (sd / key).write_text('{"version": 1, "minor_version": 1, "key": "' + key + '", "data": {"se')
    else:
        ver = 9 if label == "newer_version" else notifier.NOTIFIER_STORE_VERSION
        (sd / key).write_text(json.dumps({"version": ver, "minor_version": 1, "key": key, "data": data}))
    try:
        await notifier.async_setup_notifier(hass, Entry(), Coord())
        out = "ok"
    except Exception as e:  # noqa: BLE001
        out = f"RAISES {type(e).__name__}: {e}"
    await hass.async_stop(force=True)
    return out


async def main():
    raises = 0
    for label, data in ARMS:
        out = await one(label, data)
        print(f"ARM {label}: {out}")
        if out != "ok" and label in ("str", "list"):
            raises += 1
        elif out != "ok":
            print(f"RESULT control_{label}_raised=1")
    print(f"RESULT setup_raises={raises} count")


asyncio.run(main())
