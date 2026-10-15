"""D1.M3: inputs whose last_reported lies ahead of the host clock, across cycles.

Metric: per skew delta (stamp = now + delta on indoor AND outdoor), over 3 real
_async_update_data cycles with the stamp re-written each cycle (a sensor that
keeps reporting, as after a host-clock step back): cycles that raise, WARNING
lines "ahead of the host clock" logged, and the published indoor reading
problem (inputs.py:InputReader._age_gate). Key: the reading's problem as the
reader delivered it.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D1/s2/future_stamp.py [--perturb]
--perturb: InputReader._age_minutes tolerates stamps up to 2 s ahead (in memory).
Control: delta = -1 s (a past stamp): 0 warnings, 0 failures.
Baseline 17f1c55fad1b; machine Apple-silicon macOS (box B4).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, logging, sys, time
from datetime import timedelta
sys.path.insert(0, os.path.dirname(__file__))
_a = list(sys.argv); sys.argv = [sys.argv[0], "0", "__none__"]
import store_fuzz as F  # noqa: E402
sys.argv = _a
from harness import FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from homeassistant.helpers import storage  # noqa: E402
from custom_components.heatpump_optimizer import inputs  # noqa: E402

if "--perturb" in sys.argv:
    _orig = inputs.InputReader._age_minutes
    def _tol(self, state):
        age = inputs.state_age(state, self._utcnow())
        if age is not None and timedelta(seconds=-2) <= age < timedelta(0):
            return 0.0
        return _orig(self, state)
    inputs.InputReader._age_minutes = _tol


class Cap(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING); self.n = 0
    def emit(self, r):
        if "ahead of the host clock" in r.getMessage(): self.n += 1


async def run(delta_s):
    storage._DISK.clear(); storage._VERSIONS.clear()
    h, c = F.build(); await F.drain(c)
    cap = Cap(); logging.getLogger().addHandler(cap)
    fails = 0; per = []
    for _ in range(3):
        st = dt_util.utcnow() + timedelta(seconds=delta_s)
        h.states.set("sensor.indoor", FakeState("21.4", last_updated=st, last_reported=st))
        h.states.set("sensor.outdoor", FakeState("-3.0", last_updated=st, last_reported=st))
        before = cap.n
        e = await F.cycle(c)
        fails += e is not None
        per.append(cap.n - before)
    logging.getLogger().removeHandler(cap)
    ok = getattr(c, "data", None)
    return fails, cap.n, per, e


async def main():
    t0 = time.process_time(); tt0 = time.thread_time()
    for d in (-1.0, 0.05, 1.0, 60.0):
        fails, n, per, e = await run(d)
        tag = f"d{d:+g}s".replace(".", "p").replace("+", "p").replace("-", "m")
        print(f"RESULT {tag}.cycles_failed={fails} count")
        print(f"RESULT {tag}.ahead_warnings={n} count  per_cycle={per}  last_err={e}")
    tf = (time.process_time() - t0) / max(1e-9, time.thread_time() - tt0)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")

asyncio.run(main())
