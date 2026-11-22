#!/usr/bin/env python3
# Metric: Count of ledger inputs on which _contract_comparison() differs between `kwh > 0` and `kwh >= 0` in its cheapest-contract guard. The arms differ only at kwh == 0, where costs holds hourly_spot alone (both other contracts need kwh > 0), so len(costs) > 1 is false on both.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_9789e0e7faa1b53a.py
# EXPECTED RESULT differing_inputs=0 count over 8 inputs (kwh 0 with/without spot cost, mean, fixed price, fee; kwh -1; kwh nan; kwh 1e-12)
# EXPECTED RESULT null_delta=0 count (kwh 10, mean and fixed: both arms carry cheapest)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g04 (4 vCPU Intel Xeon Processor @ 2.10GHz, 16 GB, venv-ci CPython, gate running beside it: load1 ~1).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._contract_comparison (coordinator.py:10445 `if kwh > 0 and len(costs) > 1:`)
# Perturbation: `kwh > 0` -> `kwh >= 0`. Direction: none on any input: at kwh == 0 the costs dict has one entry.
# Null control: kwh 10 with a mean and a fixed price: both arms publish cheapest.
# Run from the repository root; the mutant is applied in memory (the method recompiled from its own
# source with the one line replaced, patched onto the class for the mutant arm only).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import asyncio, inspect, sys, textwrap, time
from pathlib import Path
from unittest import mock

# The repository root is the working directory (the harness contract): the probe imports
# production from there, so a gate mutating the tree it is stored in never leaks into it.
ROOT = Path.cwd()
assert (ROOT / "custom_components" / "heatpump_optimizer" / "manifest.json").is_file(), "run from the repository root"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
_T0, _C0 = time.thread_time(), time.process_time()
from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402
C = co.HeatPumpOptimizerCoordinator


def mutant(name, old, new):
    """The method recompiled from its own source with the one-line mutant applied."""
    src = textwrap.dedent(inspect.getsource(getattr(C, name)))
    old, new = old.strip(), new.strip()
    assert src.count(old) == 1, f"anchor moved: {old!r}"
    ns = dict(co.__dict__)
    exec(compile(src.replace(old, new, 1), co.__file__, "exec"), ns)
    return ns[name]


BASE_CFG = {"tibber_token": "x", "weather_entity": "weather.home",
            "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"}


def coord(states=None, **extra):
    return C(FakeHass(dict(states or {})), FakeEntry(data={**BASE_CFG, **extra}))


def both(name, old, new, fn):
    """fn() on the baseline and under the mutant; an exception is the value (its type name)."""
    def run():
        try:
            return fn()
        except Exception as err:  # noqa: BLE001 - a raise is an observable outcome
            return f"raises {type(err).__name__}"
    base = run()
    with mock.patch.object(C, name, mutant(name, old, new)):
        mut = run()
    return base, mut


def tail():
    thread = time.thread_time() - _T0
    proc = time.process_time() - _C0
    print(f"RESULT thread_factor={proc / thread if thread > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        swap = [l for l in open("/proc/vmstat") if l.startswith("pswpin ")][0].split()[1]
    except Exception:  # noqa: BLE001
        swap = "na"
    print(f"RESULT swapins={swap}")

def cc(kwh=10.0, sek=12.0, fee=3.0, mean=1.5, fixed=None):
    """_contract_comparison() over a ledger with this month's spot line, grid-fee line and spot mean."""
    c = coord(**({"contract_fixed_price": fixed} if fixed is not None else {}))
    now = co.dt_util.now()
    if kwh or sek:
        c._ledger.add(now, "spot", kwh=kwh, sek=sek)
    if fee:
        c._ledger.add(now, "grid_fee", kwh=kwh, sek=fee)
    if mean is not None:
        c._ledger.observe_meta_mean(now, "spot_price", mean)
    return c._contract_comparison()

NAME, OLD, NEW = "_contract_comparison", "if kwh > 0 and len(costs) > 1:", "if kwh >= 0 and len(costs) > 1:"
inputs = [dict(kwh=0.0, sek=0.0, fixed=1.0), dict(kwh=0.0, sek=5.0, fixed=1.0), dict(kwh=0.0, sek=0.0, mean=1.0, fixed=2.0),
          dict(kwh=0.0, sek=-3.0, mean=0.5, fixed=0.7, fee=0.0), dict(kwh=-1.0, sek=1.0, fixed=1.0),
          dict(kwh=float("nan"), sek=1.0, fixed=1.0), dict(kwh=1e-12, sek=0.0, fixed=1.0), dict(kwh=0.0, sek=0.0, mean=None)]
diff = 0
for a in inputs:
    b, m = both(NAME, OLD, NEW, lambda a=a: cc(**a))
    d = int(repr(b) != repr(m))
    diff += d
    print(f"RESULT input {a}: differs={d}")
print(f"RESULT differing_inputs={diff} count")
nb, nm = both(NAME, OLD, NEW, lambda: cc(mean=1.0, fixed=1.4))
print(f"RESULT null_delta={int(nb != nm)} count")
tail()
