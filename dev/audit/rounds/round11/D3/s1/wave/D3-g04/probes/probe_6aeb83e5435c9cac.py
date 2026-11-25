#!/usr/bin/env python3
# Metric: The published grid_fee_sek key of _contract_comparison() on a month whose ledger carries a 3.00 SEK grid-fee line (10 kWh, 12 SEK spot, mean spot 1.5).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_6aeb83e5435c9cac.py
# EXPECTED RESULT grid_fee_sek_baseline=3.0
# EXPECTED RESULT grid_fee_sek_mutant=absent
# EXPECTED RESULT keys_lost=1 count
# EXPECTED RESULT null_delta=0 count  (no grid-fee line: both arms omit the key)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g04 (4 vCPU Intel Xeon Processor @ 2.10GHz, 16 GB, venv-ci CPython, gate running beside it: load1 ~1).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._contract_comparison (coordinator.py:10428 `if fee_line["sek"]:`)
# Perturbation: `        if fee_line["sek"]:` -> `        if False:`. Direction: grid_fee_sek 3.0 -> absent (the contract comparison never carries the grid fee).
# Null control: a month with no grid-fee line (fee 0): both arms omit grid_fee_sek.
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

NAME, OLD, NEW = "_contract_comparison", 'if fee_line["sek"]:', "if False:"
b, m = both(NAME, OLD, NEW, cc)
print(f"RESULT baseline={b}")
print(f"RESULT mutant={m}")
print(f"RESULT grid_fee_sek_baseline={b.get('grid_fee_sek', 'absent')}")
print(f"RESULT grid_fee_sek_mutant={m.get('grid_fee_sek', 'absent')}")
print(f"RESULT keys_lost={len(set(b) - set(m))} count")
nb, nm = both(NAME, OLD, NEW, lambda: cc(fee=0.0))
print(f"RESULT null_delta={int(nb != nm)} count")
tail()
