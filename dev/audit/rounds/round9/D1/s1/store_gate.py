"""D1-s1 lifecycle harness (D1.M1) for store.py's read gate on a real asyncio loop
with a real ThreadPoolExecutor-backed load: QuarantiningStore.async_load /
async_wait_for_read under a normal read, a read cancelled mid-flight (unload during
startup), a read whose backend raises, and two overlapping reads.

Metric (one line): number of the 4 scenarios in which a writer awaiting
async_wait_for_read (1) hangs past 2 s or (2) lands its write before the read.
Count key: timeouts of the production await, and write/read ordering observed.

Command:  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python tools/audit/round9/D1/s1/store_gate.py [--nofinally]
  default       expected: hung=0 misordered=0 (exact)
  --nofinally   perturbation: the read future is resolved only on success (the
                finally dropped) -> hung=2 (cancel and raise scenarios), direction up
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B4 cloud container.
The executor thread's CPU is deliberate (sleep only); thread_factor printed as residual.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import cast

sys.path.insert(0, "custom_components")
_p0, _t0 = time.process_time(), time.thread_time()
from homeassistant.helpers import storage as hs  # noqa: E402
from heatpump_optimizer import store as store_mod  # noqa: E402
from heatpump_optimizer.store import QuarantiningStore, _sanitize  # noqa: E402

NOFINALLY = "--nofinally" in sys.argv
EX = ThreadPoolExecutor(2)
events = []
MODE = {"v": "ok"}


async def slow_backend_load(self):
    await asyncio.get_running_loop().run_in_executor(EX, time.sleep, 0.2)
    if MODE["v"] == "raise":
        raise OSError("disk")
    events.append("read")
    return {"x": 1.0}


async def nofinally_load(self):
    self._reading = reading = asyncio.get_running_loop().create_future()
    out = cast(dict, _sanitize(await hs.Store.async_load(self)))
    reading.set_result(None)
    return out


async def scenario(kind):
    events.clear()
    MODE["v"] = "raise" if kind == "raise" else "ok"
    st = QuarantiningStore(None, 1, f"gate_{kind}")
    loads = [asyncio.ensure_future(st.async_load())]
    if kind == "overlap":
        await asyncio.sleep(0.05)
        loads.append(asyncio.ensure_future(st.async_load()))
    await asyncio.sleep(0.05)
    if kind == "cancel":
        loads[0].cancel()

    async def writer():
        await st.async_wait_for_read()
        events.append("write")
    hung = 0
    try:
        await asyncio.wait_for(writer(), 2.0)
    except asyncio.TimeoutError:
        hung = 1
    for f in loads:
        try:
            await f
        except BaseException:
            pass
    mis = 0
    if kind in ("ok", "overlap") and "write" in events and "read" in events:
        mis = int(events.index("write") < events.index("read"))
    return hung, mis


async def main():
    tot_h = tot_m = 0
    for kind in ("ok", "cancel", "raise", "overlap"):
        h, m = await scenario(kind)
        print(f"# {kind}: hung={h} misordered={m}")
        tot_h += h
        tot_m += m
    return tot_h, tot_m


hs.Store.async_load = slow_backend_load
if NOFINALLY:
    QuarantiningStore.async_load = nofinally_load
h, m = asyncio.run(main())
print(f"RESULT hung={h} count")
print(f"RESULT misordered={m} count")
p, t = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={p / t if t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins={sw}")
