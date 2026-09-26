#!/usr/bin/env python3
"""V3 (round 9) D1-s5-02 reach on REAL Home Assistant: the finder's seeded store
mutants (tools/audit/round9/D1/s5/store_domain_fuzz.py, same seed and N, its own
mutate() and cycles) are each written to disk by the genuine
homeassistant.helpers.storage.Store and read back through production
QuarantiningStore.async_load before PriceShapeModel.from_dict / PeakTracker.from_dict.

Metric (one line): mutants of N per store whose loaded state makes the next cycle
deliver an out-of-domain value with no WARNING (the finder's silent_invalid), when
every payload takes the real persistence round trip first.
Command:  PYTHONPATH=. /root/venvha/bin/python -W ignore tools/audit/round9/D1/verify-v3/D1-s5-02_realha_store.py --n 300 --seed 9 [--perturb]
  --perturb: the finder's domain-gated loaders; silent_invalid must go to 0.
Environment shim: typing.ByteString aliased to bytes before importing HA (CPython
3.14.0rc2 removed it; mashumaro in HA 2026.2.3 needs it). Not a product change.
Expected: measured, exact (seeded).  Baseline SHA 1936d5ca (evidence tree).  HA 2026.2.3.
Machine: cloud 4-core box, CPython 3.14.0rc2 (V3 sub-seat for G1).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import typing  # noqa: E402
if not hasattr(typing, "ByteString"):
    typing.ByteString = bytes

import asyncio  # noqa: E402
import importlib.util  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
from unittest import mock  # noqa: E402

sys.path.insert(0, ".")
t_proc0, t_thr0 = time.process_time(), time.thread_time()

from homeassistant.core import HomeAssistant  # noqa: E402
from homeassistant.helpers.storage import Store  # noqa: E402
import homeassistant.const as hac  # noqa: E402
from custom_components.heatpump_optimizer.store import QuarantiningStore  # noqa: E402

assert "tests/hastub" not in " ".join(sys.path)
spec = importlib.util.spec_from_file_location("sdf", "tools/audit/round9/D1/s5/store_domain_fuzz.py")
F = importlib.util.module_from_spec(spec)
spec.loader.exec_module(F)
pm, tf = F.pm, F.tf
PERTURB = "--perturb" in sys.argv

loop = asyncio.new_event_loop()
threading.Thread(target=loop.run_forever, daemon=True).start()


async def _mk():
    return HomeAssistant(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))


hass = asyncio.run_coroutine_threadsafe(_mk(), loop).result()
_n = [0]
STATS = {"load_none": 0, "changed_by_boundary": 0}


async def _rt(data):
    _n[0] += 1
    key = f"hpo_v3_rt_{_n[0]}"
    await Store(hass, 1, key).async_save({"p": data})
    got = await QuarantiningStore(hass, 1, key).async_load()
    return got


def roundtrip(data):
    got = asyncio.run_coroutine_threadsafe(_rt(data), loop).result()
    if got is None:
        STATS["load_none"] += 1
        return None
    out = got.get("p")
    if out != data:
        STATS["changed_by_boundary"] += 1
    return out


def wrap(orig):
    def _f(cls, data):
        return orig(cls, roundtrip(data))
    return classmethod(_f)


pm_base = F._gated_pm_from_dict if PERTURB else F._orig_pm_from_dict
pt_base = F._gated_pt_from_dict if PERTURB else F._orig_pt_from_dict
with mock.patch.object(pm.PriceShapeModel, "from_dict", wrap(pm_base)), \
     mock.patch.object(tf.PeakTracker, "from_dict", wrap(pt_base)):
    a = F.fuzz("price_model", F.healthy_price_model(), F.price_cycle)
    b = F.fuzz("peak_tracker", F.healthy_peak_tracker(), F.peak_cycle)
print(f"HA {hac.__version__} perturb={PERTURB} N={F.N} seed={F.SEED} boundary_stats={STATS}")
for name, c in (("price_model", a), ("peak_tracker", b)):
    print(f"RESULT realha_{name}_silent_invalid={c['silent_invalid']} mutants (of {F.N})")
    print(f"RESULT realha_{name}_next_still_invalid={c['next_still_invalid']} mutants")
    print(f"RESULT realha_{name}_crash={c['crash']} mutants")
    print(f"RESULT realha_{name}_control_invalid={c['control_invalid']} payloads (of 1)")
asyncio.run_coroutine_threadsafe(hass.async_stop(force=True), loop).result()
pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f} (the event-loop thread does the file I/O; see deliberate_thread note)")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=" + next((ln.split()[1] for ln in open("/proc/vmstat") if ln.startswith("pswpin")), "unknown"))
