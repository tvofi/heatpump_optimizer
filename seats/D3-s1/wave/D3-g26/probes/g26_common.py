"""Shared plumbing for box D3-g26's step-4 probes (round 11, seat D3-s1).

Not a harness on its own: every probe_<key>.py imports it, and each carries its
own header (metric, command, expected, baseline, machine, instrumented symbol,
perturbation). It provides
  * the thread pin (before numpy),
  * mutant(owner, name, old, new): the production function/method recompiled
    from its OWN source with exactly one line swapped (the anchor must occur
    once), compiled with ``from __future__ import annotations`` as the module is,
    returned for ``mock.patch.object`` -- the mutant is applied in memory only,
    never on disk,
  * the manual-plan bundle builders of tests/manual_plan.py (reused, not copied),
  * trailer(): RESULT thread_factor / load1 / swapins.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import __future__
import inspect
import sys
import textwrap
import time
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
for _p in (str(ROOT / "custom_components"), str(ROOT / "tests"), str(ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

_T0 = (time.process_time(), time.thread_time())


def mutant(owner, name, old, new, nth=None):
    """``owner.name`` recompiled with the one line whose stripped text is ``old``
    replaced by ``new`` (same indentation). Module-level functions and methods. When the
    anchor text occurs more than once, ``nth`` (0-based) names which occurrence the mutant is."""
    fn = inspect.unwrap(getattr(owner, name))
    mod = sys.modules[fn.__module__]
    src = textwrap.dedent(inspect.getsource(fn))
    lines = src.split("\n")
    hits = [i for i, ln in enumerate(lines) if ln.strip() == old.strip()]
    if nth is None:
        assert len(hits) == 1, f"anchor {old!r} found {len(hits)} times in {name}"
        nth = 0
    i = hits[nth]
    indent = lines[i][: len(lines[i]) - len(lines[i].lstrip())]
    lines[i] = indent + new.strip()
    ns = dict(mod.__dict__)
    code = compile("\n".join(lines), mod.__file__, "exec",
                   flags=__future__.annotations.compiler_flag, dont_inherit=True)
    exec(code, ns)
    return ns[fn.__name__]


def trailer():
    pc, tc = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    swap = "n/a"
    try:
        for ln in Path("/proc/vmstat").read_text().splitlines():
            if ln.startswith("pswpin "):
                swap = ln.split()[1]
    except OSError:
        pass
    print(f"RESULT swapins={swap}")


def manual_plan_module():
    """tests/manual_plan.py imported as a module: its _build_optimizer, _solve, N."""
    import importlib
    os.environ.setdefault("PYTHONPATH", "tests/hastub")
    return importlib.import_module("manual_plan")


class SolveCounter:
    """Counts the optimizer's top-level channel solves on one instance."""

    def __init__(self, opt):
        self.n = 0
        for attr in ("_optimize_with_dhw", "_optimize_space_only"):
            bound = getattr(opt, attr)

            def wrap(*a, _b=bound, **k):
                self.n += 1
                return _b(*a, **k)

            setattr(opt, attr, wrap)


def coordinator_cycle_reach(spies, manual_plan=True):
    """Run real coordinator refresh cycles (HeatPumpOptimizerCoordinator._async_update_data) with the solve
    kept in-process, under ``spies`` -- a list of (owner, attr, replacement) patched for the cycle -- so a spy
    records what production hands the instrumented symbol. Two configs (house power entity absent / present,
    2.5 kW), each with and without an active manual plan (space 01:00-03:00, DHW 02:00-03:00, 6 h expiry).
    Inputs mirror tests/config_flow_steps.py:_noop_hass. Returns the number of solves run."""
    import asyncio
    from datetime import timedelta
    from unittest import mock
    from harness import FakeEntry, FakeHass, FakeState
    from homeassistant.util import dt as dt_util
    from heatpump_optimizer import const, coordinator as CO, manual_plan as MP
    solves = []

    async def inline(hass, optimizer, inputs):
        solves.append(1)
        return CO.optimize_in_process(optimizer, inputs)

    now = dt_util.now()
    start = now.replace(minute=0, second=0, microsecond=0)
    base = {"name": "Home", const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY, const.CONF_PRICE_ENTITY: "sensor.prices",
            const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor", const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor"}
    for extra in ({}, {const.CONF_HOUSE_POWER_ENTITY: "sensor.house"}):
        for plan in ((False, True) if manual_plan else (False,)):
            hass = FakeHass()
            hass.states.set("sensor.prices", FakeState("0.5", attributes={"raw_today": [
                {"start": (start + timedelta(hours=h)).isoformat(), "value": round(0.5 + 0.1 * (h % 4), 3)}
                for h in range(48)]}))
            hass.states.set("sensor.indoor", FakeState("21.0", unit="°C"))
            hass.states.set("sensor.outdoor", FakeState("2.0", unit="°C"))
            hass.states.set("sensor.house", FakeState("2500", unit="W"))
            coord = CO.HeatPumpOptimizerCoordinator(hass, FakeEntry(data={**base, **extra}))
            if plan:
                slot = lambda a, b: {"start": (start + timedelta(hours=a)).isoformat(),  # noqa: E731
                                     "end": (start + timedelta(hours=b)).isoformat()}
                coord._manual_override = MP.build_override(
                    space_slots=[slot(1, 3)], dhw_slots=[slot(2, 3)], expires_at=now + timedelta(hours=6), now=now)
            with mock.patch.object(CO, "_await_optimize", inline):
                ctx = [mock.patch.object(o, a, r) for o, a, r in spies]
                for c in ctx:
                    c.start()
                try:
                    asyncio.run(coord._async_update_data())
                finally:
                    for c in ctx:
                        c.stop()
    return len(solves)
