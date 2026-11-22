#!/usr/bin/env python3
# Metric: (a) the Hz value HeatPumpOptimizerCoordinator._command_frequency writes through number.set_value and
#   (b) the commanded Hz it records on the FrequencyWatchdog, plus (c) whether the watchdog trips after one write and
#   4 reported ticks at 45.08 Hz, for a number entity whose own range is [20.0, 50.06] Hz and a target above every
#   evidenced bucket's reach (FrequencyMap.recommend answers round(hz_max, 1) = 50.1).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g03/probes/probe_420bcb85.py
# EXPECTED RESULT written_baseline=50.1 ; written_mutant=50.1 (the write re-rounds: rounding is monotone, so the
#   clamp never changes the written value)
# EXPECTED RESULT commanded_baseline=50.06 ; commanded_mutant=50.1 Hz
# EXPECTED RESULT tripped_baseline=False ; tripped_mutant=True (45.08 Hz is 4.98 Hz from 50.06, 5.02 from 50.1; FREQ_DIVERGENCE_HZ=5)
# EXPECTED RESULT null_delta=0 count (entity range [20.0, 50.0]: recommend stays in range, arms identical)
# Key of the count: the service-call payload and the watchdog's own fields (production state).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g03 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._command_frequency,
#   line 10855 `target = float(np.clip(target, hz_min, hz_max))`; real freq_control.FrequencyMap and FrequencyWatchdog.
# Perturbation: key 420bcb8597761025 CLAMP_DROP -> `target = float((target))`, in memory. Direction: commanded 50.06 -> 50.1.
# Null control: an entity range on the 0.1 Hz grid, where the clamp is inert.
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

from custom_components.heatpump_optimizer import freq_control as fc  # noqa: E402

MUT = mutant(CLS._command_frequency, 10855, "        target = float(np.clip(target, hz_min, hz_max))",
             "        target = float((target))")


def drive(fn, hz_max):
    fmap = fc.FrequencyMap()
    fmap.buckets = {d: [0.05, fc.FREQ_MIN_SAMPLES] for d in range(10)}  # 0.05 kW/Hz: at most ~2.5 kW
    wd = fc.FrequencyWatchdog()
    writes = []

    async def call(domain, service, data, blocking=False):
        writes.append(data["value"])

    me = SimpleNamespace(
        _config=SimpleNamespace(compressor_freq_entity="number.freq"), _mode="auto",
        _freq_mode=lambda: co.FREQ_MODE_CONTROL, _freq_entity_reading=lambda: (None, 20.0, hz_max, "number"),
        _freq_map=fmap, _commanded_power=lambda: 9.0, _freq_last_write=None, _freq_watchdog=wd,
        hass=SimpleNamespace(services=SimpleNamespace(async_call=call)),
    )
    run(fn(me))
    for _ in range(4):
        wd.note_report(45.08)
    return (writes[0] if writes else None), wd.commanded, wd.tripped


for arm, fn in (("baseline", CLS._command_frequency), ("mutant", MUT)):
    w, c, t = drive(fn, 50.06)
    print(f"RESULT written_{arm}={w}")
    print(f"RESULT commanded_{arm}={c} Hz")
    print(f"RESULT tripped_{arm}={t}")
print(f"RESULT null_delta={int(drive(CLS._command_frequency, 50.0) != drive(MUT, 50.0))} count")
tail()
