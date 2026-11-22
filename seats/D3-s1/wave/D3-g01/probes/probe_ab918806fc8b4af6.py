#!/usr/bin/env python3
# Metric: ledger lines HeatPumpOptimizerCoordinator._accumulate_energy books for ONE settled 0.25 h interval in which the
#   pump drew 0 kW (energy == 0, price 1.5, spot 1.0), on a live coordinator's MonthlyLedger; plus the energy total.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_ab918806fc8b4af6.py
# EXPECTED RESULT zero_energy_lines_baseline=0 count [] ; zero_energy_lines_mutant=3 count ['dhw', 'space', 'spot'] (0 kWh, 0 SEK each)
# EXPECTED RESULT zero_energy_total_kwh_delta=0.0  (the energy and cost sums are unchanged)
# EXPECTED RESULT null_delta=0 count  (a 2 kW interval: energy > 0, both arms book the same four lines)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g01 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._accumulate_energy
#   line 10331 (`if energy <= 0:`; energy = max(0.0, actual * elapsed_hours) at 10315, so energy < 0 never occurs),
#   live coordinator, _schedule_ledger_save counted instead of scheduled.
# Perturbation: key ab918806fc8b4af6, `if energy <= 0:` -> `if False:` (GUARD_OFF), in memory (method recompiled from source).
#   Direction: a zero-energy interval books no ledger line -> books zero-valued dhw/space/spot lines.
# Null control: an interval with energy > 0 (2 kW for 0.25 h).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, logging, sys, textwrap, time
logging.disable(logging.CRITICAL)
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

_T0 = (time.process_time(), time.thread_time())


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
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
sys.path.insert(0, str(ROOT / "tests"))
from harness import FakeEntry, FakeHass  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402

CFG = {"tibber_token": "x", "weather_entity": "weather.home",
       "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"}


def coord(states=None, **extra):
    return co.HeatPumpOptimizerCoordinator(FakeHass(dict(states or {})), FakeEntry(data={**CFG, **extra}))


def recompile(cls, name, old, new):
    """The method `name` of `cls` with its single line `old` replaced by `new`, compiled in the module namespace."""
    src = textwrap.dedent(inspect.getsource(getattr(cls, name)))
    assert src.count(old) == 1, f"anchor {old!r} moved"
    ns = dict(co.__dict__)
    exec(compile(src.replace(old, new, 1), co.__file__, "exec"), ns)
    return ns[name]


def tail():
    p, t = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={p / t if t > 0 else 1.0:.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = next(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin "))
    except (OSError, StopIteration):
        sw = 0
    print(f"RESULT swapins={sw} count")


CLS = co.HeatPumpOptimizerCoordinator
WHEN = co.dt_util.now().replace(day=15, hour=12, minute=0, second=0, microsecond=0)


def drive(fn, actual_kw, pending_extra=None):
    """One settled 0.25 h interval through _accumulate_energy; returns (ledger lines booked, saves scheduled, totals)."""
    c = coord()
    saves = []
    c._schedule_ledger_save = lambda: saves.append(1)
    pending = {"when": WHEN, "price": 1.5, "spot_price": 1.0, "power": 0.0, "dhw_power": 0.0,
               "space_reason": "cheap", "dhw_reason": "idle", **(pending_extra or {})}
    fn(c, SimpleNamespace(actual_power_kw=actual_kw), 0.25, pending)
    month = c._ledger.as_dict()["months"] if hasattr(c._ledger, "as_dict") else c._ledger.months
    lines = sorted(k for m in (month.values() if isinstance(month, dict) else month) for k in m.get("lines", {}))
    return lines, len(saves), round(c._energy_totals["total_energy_kwh"], 6)


MUT = recompile(CLS, "_accumulate_energy", "if energy <= 0:", "if False:")
for name, kw in (("zero_energy", 0.0), ("no_meter_zero_plan", None)):
    b, m = drive(CLS._accumulate_energy, kw), drive(MUT, kw)
    print(f"RESULT {name}_lines_baseline={len(b[0])} count {b[0]}")
    print(f"RESULT {name}_lines_mutant={len(m[0])} count {m[0]}")
    print(f"RESULT {name}_total_kwh_delta={m[2] - b[2]}")
    print(f"RESULT {name}_saves baseline={b[1]} mutant={m[1]}")
print(f"RESULT inputs no-price zero-energy: baseline={drive(CLS._accumulate_energy, 0.0, {'price': None})} mutant={drive(MUT, 0.0, {'price': None})}")
print(f"RESULT null_delta={int(drive(CLS._accumulate_energy, 2.0) != drive(MUT, 2.0))} count")
tail()
