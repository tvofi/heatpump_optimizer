#!/usr/bin/env python3
# Metric: whether the payload HeatPumpOptimizerCoordinator._build_data_dict assembles carries the `manual_plan` key,
#   on a real coordinator (tests/harness.py FakeHass/FakeEntry, one input cycle) holding an active manual override
#   built by manual_plan.build_override (one 2 h DHW slot, expiring in 12 h), as async_apply_manual_plan stores it.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g03/probes/probe_ac6bedc7.py
# EXPECTED RESULT manual_plan_published_baseline=True ; manual_plan_published_mutant=False
# EXPECTED RESULT null_delta=0 count (no override: both arms omit the key)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g03 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._build_data_dict,
#   line 8265 `if manual_state is not None:`; consumers: the plan sensors read data["manual_plan"].
# Perturbation: key ac6bedc70bb82ff7 GUARD_OFF -> `if False:`, in memory. Direction: key present -> absent.
# Null control: the same coordinator with no override.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, sys, textwrap, time, types
from types import SimpleNamespace
from unittest import mock

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
sys.path.insert(0, str(ROOT))
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402

CLS = co.HeatPumpOptimizerCoordinator
_T0 = (time.process_time(), time.thread_time())


def mutant(fn, line, old, new):
    """`fn` recompiled from its own source with production line `line` replaced (in memory only)."""
    lines, start = inspect.getsourcelines(fn)
    i = line - start
    assert lines[i].rstrip("\n") == old, f"anchor moved: {lines[i]!r}"
    lines[i] = new + "\n"
    ns = dict(co.__dict__)
    exec(compile(textwrap.dedent("".join(lines)), co.__file__, "exec"), ns)
    f = ns[fn.__name__]
    # rebound onto the module's own globals, so a patch of a module name reaches both arms alike
    return types.FunctionType(f.__code__, co.__dict__, f.__name__, f.__defaults__, f.__closure__)


def run(coro):
    return asyncio.run(coro)


def tail():
    p, t = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={p / t if t > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
    except OSError:
        sw = -1
    print(f"RESULT swapins={sw} count")

from datetime import timedelta  # noqa: E402
sys.path.insert(0, str(ROOT / "tests"))
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from custom_components.heatpump_optimizer import const, manual_plan  # noqa: E402

MUT = mutant(CLS._build_data_dict, 8265, "        if manual_state is not None:", "        if False:")


def coordinator(with_override):
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    coord = CLS(hass, FakeEntry(data={const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
                                      const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor", const.CONF_DHW_TANK_VOLUME: 180.0}))
    run(coord._update_current_state())
    if with_override:
        now = dt_util.now()
        coord._manual_override = manual_plan.build_override(
            dhw_slots=[{"start": (now + timedelta(hours=1)).isoformat(), "end": (now + timedelta(hours=3)).isoformat()}],
            space_slots=None, expires_at=now + timedelta(hours=12), now=now)
    return coord


for arm, fn in (("baseline", CLS._build_data_dict), ("mutant", MUT)):
    print(f"RESULT manual_plan_published_{arm}={'manual_plan' in fn(coordinator(True))}")
c = coordinator(False)
print(f"RESULT null_delta={int(('manual_plan' in CLS._build_data_dict(c)) != ('manual_plan' in MUT(c)))} count")
tail()
