"""V2 (independent) harness for D1-s2-03.

Metric (one line): per stored sample-count value N at cop_baseline["4"][1] and
capacity_envelope["0"][1], whether production HeatPumpOptimizerCoordinator.
_learning_view() raises after the store payload (orjson round trip) is loaded
by production _async_load_thermal_learning; count of raising (seam, N) pairs,
N (JSON literal) in {1000, 2**63-1, 2**64-1, 1e19, 1.9e19, 1e20, 1e308}; plus whether
orjson can re-save the loaded state (the stuck-store half).
Count key: exceptions out of _learning_view; orjson.dumps exceptions on the
production save payload builder's int(v[1]).
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/u1_huge_count.py
Expected: raising pairs = the literals whose int() >= 2**64 (1.9e19, 1e20, 1e308: 3 per seam = 6 of 14),
  resave_refused for the same; 1000 / 2**63-1 / 2**64-1 / 1e19 give 0 (+-0).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")
import asyncio, sys, time, logging
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
_p0, _t0 = time.process_time(), time.thread_time()
logging.disable(logging.CRITICAL)
import orjson
from harness import FakeEntry, FakeHass, FakeState  # noqa
from heatpump_optimizer import const  # noqa
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa

VALUES = ["1000", str(2**63 - 1), str(2**64 - 1), "1e19", "1.9e19", "1e20", "1e308"]


def coord():
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.0"))
    hass.states.set("sensor.outdoor", FakeState("0.0"))
    return HeatPumpOptimizerCoordinator(hass, FakeEntry(data={
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor", const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor"}))


def trial(seam, n):
    c = coord()
    cop = n if seam == "cop_baseline" else "50"
    env = n if seam == "capacity_envelope" else "50"
    text = '{"cop_baseline": {"4": [3.0, %s]}, "capacity_envelope": {"0": [4.0, %s]}}' % (cop, env)
    raw = orjson.loads(text)  # HA's Store reads with orjson; the literal is the stored JSON number
    asyncio.run(c._thermal_learning_store.async_save(raw))
    asyncio.run(c._async_load_thermal_learning())
    try:
        c._learning_view()
        rv = 0
    except Exception:  # noqa: BLE001
        rv = 1
    try:
        orjson.dumps({k: int(v[1]) for k, v in (c._cop_baseline | {("e", k2): v2 for k2, v2 in c._capacity_envelope.items()}).items()} and
                     [int(v[1]) for v in list(c._cop_baseline.values()) + list(c._capacity_envelope.values())])
        rs = 0
    except Exception:  # noqa: BLE001
        rs = 1
    return rv, rs


tot = 0
for seam in ("cop_baseline", "capacity_envelope"):
    for n in VALUES:
        rv, rs = trial(seam, n)
        tot += rv
        print(f"RESULT {seam}_N{n}_view_raises={rv} resave_refused={rs}")
print(f"RESULT raising_pairs={tot} count_of_{2 * len(VALUES)}")
p, t = time.process_time() - _p0, time.thread_time() - _t0
print(f"RESULT thread_factor={p / t if t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    print("RESULT swapins=" + [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1])
except Exception:
    print("RESULT swapins=na")
