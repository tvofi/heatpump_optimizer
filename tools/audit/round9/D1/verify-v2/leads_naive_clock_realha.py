"""V2 (independent) for D1-s1-52: the hastub clock versus Home Assistant 2026.2.3's real util/dt.

Metric: of 8 cells (4 production stored-timestamp seams, none of them the finder's, x a stored
stamp written aware or naive), count cells whose raise/no-raise verdict under tests/hastub's
default clock (no HASTUB_TZ, not frozen) differs from the verdict under the REAL
homeassistant/util/dt.py of HA 2026.2.3 (loaded from the extracted wheel; its now, utcnow,
as_utc, as_local and parse_datetime swapped into the stub module object, DEFAULT_TIME_ZONE = its
own default UTC). Seams: boost.restore (stored boost 'until' vs now), drift.Cusum.load +
release_if_starved (stored last_fed), manual_plan.ManualOverride.from_dict + is_expired (stored
expires_at), legionella.LegionellaGuard.hours_since (stored last_cycle via parse_datetime).
Count key: whether the production seam raises (TypeError), read from the call itself.
Also printed: whether each clock's now() is tz-aware.
Command: LEADS_HA_ROOT=<root> PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/verify-v2/leads_naive_clock_realha.py
Expected: stub_now_aware=0, real_now_aware=1; divergent=4 of 8 (exact; boost 2 cells [inverted],
drift 2 cells [its loader normalises a naive stamp to UTC, so both stored forms raise on the naive
stub now and neither on the real one], manual_plan and legionella 0: they coerce awareness /
route through as_utc).
Perturbation: HASTUB_TZ=UTC (the stub's aware mode) -> divergent=0.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio
import importlib.util
import resource
import sys
import time
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import leads_realha  # noqa: E402

T0 = (time.process_time(), time.thread_time())
sys.path.append(os.path.join(leads_realha.root(), "deps"))  # ciso8601, aiozoneinfo only
spec = importlib.util.spec_from_file_location("realha_dt", leads_realha.real_module_path("util/dt.py"))
real_dt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(real_dt)

from homeassistant.util import dt as dt_util  # noqa: E402  (the stub)
from homeassistant.helpers import storage  # noqa: E402
from harness import FakeHass, FakeEntry  # noqa: E402
from heatpump_optimizer import boost, const  # noqa: E402
from heatpump_optimizer.drift import Cusum  # noqa: E402
from heatpump_optimizer.manual_plan import ManualOverride  # noqa: E402
from heatpump_optimizer.legionella import LegionellaGuard  # noqa: E402

dt_util.freeze(None)
STUB_FUNCS = {k: getattr(dt_util, k) for k in ("now", "utcnow", "as_utc", "as_local", "parse_datetime")}
BASE = datetime.now(timezone.utc).replace(microsecond=0)


def stamp(delta_h, aware):
    t = BASE + timedelta(hours=delta_h)
    return t.isoformat() if aware else t.replace(tzinfo=None).isoformat()


class _Coord:  # weak-referenceable, as boost.held_for's WeakKeyDictionary needs
    def __init__(self):
        self.hass, self.entry = FakeHass(), FakeEntry(data={})


def s_boost(aware):
    coord = _Coord()
    storage._DISK[f"{const.DOMAIN}_{coord.entry.entry_id}_boost"] = (
        '{"space": {"until": "%s"}}' % stamp(2, aware))
    asyncio.run(boost.restore(coord))


def s_drift(aware):
    c = Cusum(threshold=1.0, drift=0.0)
    c.load({"stat": 2.0, "tripped": True, "last_fed": stamp(-30, aware)})
    c.release_if_starved(dt_util.now(), 6.0)


def s_manual(aware):
    ov = ManualOverride.from_dict({"expires_at": stamp(2, aware), "space_slots": [], "dhw_slots": None})
    ov.is_expired(dt_util.now())


def s_legionella(aware):
    ns = SimpleNamespace(last_cycle=dt_util.parse_datetime(stamp(-30, aware)), attempt=None)
    LegionellaGuard.hours_since(ns)


SEAMS = {"boost.restore": s_boost, "drift.release_if_starved": s_drift,
         "manual_plan.is_expired": s_manual, "legionella.hours_since": s_legionella}


def verdicts():
    out = {}
    for name, fn in SEAMS.items():
        for aware in (True, False):
            try:
                fn(aware)
                out[(name, aware)] = 0
            except TypeError:
                out[(name, aware)] = 1
    return out


def use(funcs):
    for k, f in funcs.items():
        setattr(dt_util, k, f)


use(STUB_FUNCS)
stub_aware = int(dt_util.now().tzinfo is not None)
sv = verdicts()
use({k: getattr(real_dt, k) for k in STUB_FUNCS})
real_aware = int(dt_util.now().tzinfo is not None)
rv = verdicts()
use(STUB_FUNCS)
div = 0
for k in sv:
    d = sv[k] != rv[k]
    div += d
    print(f"RESULT cell_{k[0]}_{'aware' if k[1] else 'naive'}: stub_raises={sv[k]} real_raises={rv[k]} divergent={int(d)}")
print(f"RESULT stub_now_aware={stub_aware} real_now_aware={real_aware} real_default_tz={real_dt.DEFAULT_TIME_ZONE}")
print(f"RESULT divergent={div} of_{len(sv)}")
pc, tc = time.process_time() - T0[0], time.thread_time() - T0[1]
print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_majflt}")
