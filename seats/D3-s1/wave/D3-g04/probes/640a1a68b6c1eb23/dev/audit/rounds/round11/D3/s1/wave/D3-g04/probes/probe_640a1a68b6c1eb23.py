#!/usr/bin/env python3
# Metric: _entity_state(entity_id)'s outcome for an unset entity (None, the EntryConfig default of away_presence_entity, and '') under two states registries: the suite's FakeStates (dict.get) and a registry that follows Home Assistant's StateMachine.get contract (`_states_data.get(entity_id) or _states_data.get(entity_id.lower())`, written out below; Home Assistant itself is not installed in venv-ci).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_640a1a68b6c1eb23.py
# EXPECTED RESULT fake_states_differing=0 count (None, '')
# EXPECTED RESULT ha_contract_baseline=(None, {}) for None
# EXPECTED RESULT ha_contract_mutant=raises AttributeError for None
# EXPECTED RESULT ha_contract_differing=1 count
# EXPECTED RESULT null_delta=0 count (a present entity 'binary_sensor.home' = 'on': both arms, both registries)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g04 (4 vCPU Intel Xeon Processor @ 2.10GHz, 16 GB, venv-ci CPython, gate running beside it: load1 ~1).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._entity_state (coordinator.py:9846 `if not entity_id:`), the call site _resolve_away (coordinator.py:9875) with away_presence_entity unset
# Perturbation: `if not entity_id:` -> `if False:`. Direction: None reaches hass.states.get; the suite's stub answers None (no change), a registry that lower()s the id raises.
# Null control: a configured, present presence entity: identical on both arms.
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

NAME, OLD, NEW = "_entity_state", "if not entity_id:", "if False:"


class HaContractStates:
    """Home Assistant's StateMachine.get, as the contract a real hass.states honours (core.py)."""

    def __init__(self, mapping):
        self._states_data = dict(mapping)

    def get(self, entity_id):
        return self._states_data.get(entity_id) or self._states_data.get(entity_id.lower())


present = {"binary_sensor.home": FakeState("on")}


def es(eid, ha):
    c = coord(present)
    if ha:
        c.hass.states = HaContractStates(present)
    return c._entity_state(eid)


fake_diff = sum(int(x[0] != x[1]) for x in (both(NAME, OLD, NEW, lambda e=e: es(e, False)) for e in (None, "")))
hb, hm = both(NAME, OLD, NEW, lambda: es(None, True))
ha_diff = sum(int(x[0] != x[1]) for x in (both(NAME, OLD, NEW, lambda e=e: es(e, True)) for e in (None, "")))
print(f"RESULT default_presence_entity={coord()._ctx._config.away_presence_entity!r}")
print(f"RESULT fake_states_differing={fake_diff} count")
print(f"RESULT ha_contract_baseline={hb} for None")
print(f"RESULT ha_contract_mutant={hm} for None")
print(f"RESULT ha_contract_differing={ha_diff} count")
nd = sum(int(x[0][0] != x[1][0]) for x in (both(NAME, OLD, NEW, lambda h=h: es("binary_sensor.home", h)) for h in (False, True)))
print(f"RESULT null_delta={nd} count")
tail()
