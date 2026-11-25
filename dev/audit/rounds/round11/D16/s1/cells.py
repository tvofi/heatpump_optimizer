"""D16-s1 cells: every enumerator cell (D16.M1) and its value check (D16.M2).

Metric: per cell ``<site> | <state>`` of ``tools/audit/enumerate.py d16-writes --cells``,
the service calls that reached ``hass.services.async_call`` (attributed to the
enumerator site on the call's stack) and the ``log_held`` latches set, in the
step the state books, graded against D16.md's table row for that state; the
count of graded cells that fail, per rig.
Count key: the value and entity of each call the production seam delivered to
``services.async_call`` (never an input attribute), and ``held.written`` of
``pump_arbiter.state_for`` for "recorded as made".

Run (from the export root):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D16/s1/cells.py \
        [--perturb NAME] [--json OUT]
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (exact, counts):
    RESULT cells=532, examined=532, unattributed_calls=0, gate_cells=154,
    gate_cells_command_diff=2 (the two baseline cells a real solve refreshes),
    arbiter_value_rows_failing=4, clause_grid=50, clause_switch=5,
    cold_tank_charge=2, boost_indoor_between=2, baseline_switch_off=5,
    unavailable_recorded=5 (each exact). --no-gates skips the solve arm.
Machine: B11 container, Linux x86_64, $HOME/venv-ci python3. Counts are
contention-immune; the one wall number is provisional.

The oracle half (ORACLE, below) imports nothing from ``pump_arbiter`` and
calls no step selection of the package's: it reads index K of the plan the
harness built, by plain indexing. The production half is the real
``HeatPumpOptimizerCoordinator`` on ``coord_all_features`` (tests/golden.py)
with the pump's actuator slots added, driven through ``_apply_action`` (the
cycle's actuation), ``pump_arbiter.apply`` (the one-minute tick) and
``pump_arbiter.supply_tick`` (the step tick).

Perturbations (--perturb), each in memory:
  P1           pump_arbiter._step_index returns one step late (i-1): the
               oracle's K does not move and the value rows go red.
  P2           pump_arbiter.desired's house-only row lets the tank charge
               (space-only step writes Heating + DHW with the configured
               tank set-point): the row does not move and min-cold-tank /
               partial / full go red on every rig.
  P2doc        the docstring of pump_arbiter edited alone: no cell moves.
  dhw_gate     pump_arbiter.DHW_GATE_C = 10.0: D16-s1 finding on the cold tank
               moves to zero.
  boost_indoor desired() maps an indoor space boost to max_temperature: the
               indoor boost finding moves to zero.
  stale_on     the cycle's stale branch also writes the supply on: the
               baseline finding moves to zero.
  write_skips_unavailable  pump_arbiter._write returns before the call on an
               entity reading ``unavailable``: the unavailable finding moves to zero.
  freq_grid    FrequencyMap.recommend rounded to the entity's 1 Hz step: the
               frequency grid finding moves to zero.
  freq_step_half  (null control, a config change) the frequency entity states
               a 0.5 Hz step: every decile mid is on it, clause_grid reads 0.
  ha_skip_off  the service emulation does not skip unavailable entities
               (the stub's behaviour): the unavailable finding moves to zero
               (a harness-side null, it shows the count keys on HA's skip).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import asyncio
import json
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

sys.path[:0] = ["tests", "custom_components"]

from harness import FakeEntry, FakeHass, FakeServices, FakeState  # noqa: E402
from golden import coordinator_scenarios  # noqa: E402
from homeassistant.helpers import storage as _storage  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import heatpump_optimizer.coordinator as coord_mod  # noqa: E402
from heatpump_optimizer import (  # noqa: E402
    boost, heat_curve, inputs, log_latch, off_restore, pump_arbiter,
)
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer, OptimizationConfig, OptimizationResult,
)

PKG = "custom_components/heatpump_optimizer/"
ROOT = Path.cwd()
T0 = datetime(2026, 1, 12, 6, 0, tzinfo=timezone.utc)
N, K = 8, 4
TS = [T0 + timedelta(minutes=15 * i) for i in range(N)]
F, P = 1.0, 5.0          # coord_all_features' band: P >= 3f
HYST = 5.0               # the pump's own hot-water start hysteresis, K (sensor below)
DHW_CFG = 55.0
DISPLACE_ON, DISPLACE_OFF = 3.0, -4.0   # the plan's heat-curve displace, K
TANK = 48.0
STATES = ("idle", "min-cold-tank", "partial", "full", "dhw-only", "both",
          "boost-partial", "disinfection", "baseline", "restart", "upgrade",
          "unavailable", "observe", "off")
# The plan each state books at step K: (space kW, hot-water kW).
BOOK = {
    "idle": (0.0, 0.0), "min-cold-tank": (F, 0.0), "partial": ((F + P) / 2, 0.0),
    "full": (P, 0.0), "dhw-only": (0.0, 2 * F), "both": ((F + P) / 2, 2 * F),
}
for _s in ("baseline-on", "boost-partial", "disinfection", "baseline", "restart", "upgrade",
           "unavailable", "observe", "off"):
    BOOK[_s] = BOOK["partial"]

MODE_OPTS = {
    # The Tuya fork: a single duty in either direction.
    "fork": ["Heating", "DHW (Hot Water)", "Heating + DHW", "Cooling"],
    # The GCHV/Rotenso package: no single heating duty.
    "gchv": ["Off", "Cooling + DHW", "Heating + DHW"],
}
RIGS = {
    "fork-flow": ("fork", "flow"),
    "gchv-flow": ("gchv", "flow"),
    "fork-indoor": ("fork", "indoor"),
    "gchv-indoor": ("gchv", "indoor"),
    # fork-flow with the heat-curve entity's persistent kind and a smart_write
    # mixing valve: the holds of write_persistent and _command_valve_target.
    "fork-flow-pc": ("fork", "flow"),
}
RIG_EXTRA = {"fork-flow-pc": {"heat_curve_target_kind": "persistent", "mixing_valve_mode": "smart_write",
                              "mixing_valve_write_entity": "number.valve"}}
VALVE_K, VALVE_ELSE = 24.3, 22.0
FREQ_STEP = [1]  # the frequency entity's own step; --perturb freq_step_half sets 0.5 (null control)


# --------------------------------------------------------------------------
# The universe, and site attribution
# --------------------------------------------------------------------------

def universe() -> list[str]:
    out = subprocess.run([sys.executable, "tools/audit/enumerate.py", "d16-writes", "--cells"],
                         capture_output=True, text=True, check=True).stdout
    return [line for line in out.splitlines() if line.strip()]


def sites_of(cells: list[str]) -> list[tuple[str, str, int, str]]:
    seen = []
    for line in cells:
        head = line.split(" | ")[0]
        kind, loc, qual = head.split(" ")[:3]
        path, lineno = loc.rsplit(":", 1)
        item = (kind, path, int(lineno), qual)
        if item not in seen:
            seen.append(item)
    return seen


CELLS = universe()
SITES = sites_of(CELLS)
SITE_NAME = {(p, ln): f"{k} {p}:{ln} {q}" for k, p, ln, q in SITES}
BY_FUNC: dict[tuple[str, str], list[int]] = defaultdict(list)
for _k, _p, _ln, _q in SITES:
    BY_FUNC[(_p, _q.split(".")[-1])].append(_ln)
# A reference handed on uncalled (the enumerator's ``domain=?`` row): the call
# lands in the receiver's module, attributed to the site that handed it over.
REFERENCE_RECEIVERS = {PKG + "disinfection.py": (PKG + "coordinator.py", 3432)}


def _rel(filename: str) -> str | None:
    try:
        rel = Path(filename).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return None
    return rel if rel.startswith(PKG) else None


def attribute(kinds: tuple[str, ...]) -> tuple[str, int] | None:
    """The enumerator site on the current stack, innermost first."""
    f = sys._getframe(2)
    receiver = None
    while f is not None:
        rel = _rel(f.f_code.co_filename)
        if rel is not None:
            lines = BY_FUNC.get((rel, f.f_code.co_name))
            if lines:
                below = [ln for ln in lines if ln <= f.f_lineno] or lines
                ln = max(below)
                if any(k for k, p, l2, _ in SITES if p == rel and l2 == ln and k in kinds):
                    return rel, ln
            if receiver is None and rel in REFERENCE_RECEIVERS:
                receiver = REFERENCE_RECEIVERS[rel]
        f = f.f_back
    return receiver


# --------------------------------------------------------------------------
# Home Assistant's side of a write
# --------------------------------------------------------------------------

class Log:
    def __init__(self) -> None:
        self.calls: list[dict] = []
        self.holds: list[dict] = []
        self.now: datetime | None = None


LOG = Log()
HA_SKIPS_UNAVAILABLE = True


class EmuServices(FakeServices):
    """``FakeServices`` plus the device: a write the entity takes is what it
    then reads, and an unavailable entity is skipped as Home Assistant's
    entity service call skips it (``helpers/service.py``: an entity that is
    not ``available`` is left out of the call, which still returns)."""

    def __init__(self, hass) -> None:
        super().__init__()
        self._hass = hass

    async def async_call(self, domain, service, data=None, **kwargs):
        site = attribute(("write",))
        data = dict(data or {})
        ent = data.get("entity_id", data.get("topic"))
        st = self._hass.states.get(ent) if isinstance(ent, str) else None
        skipped = HA_SKIPS_UNAVAILABLE and st is not None and st.state == "unavailable"
        value = data.get("value", data.get("option", data.get("temperature", data.get("payload"))))
        LOG.calls.append({"site": site, "domain": domain, "service": service, "entity": ent,
                          "value": value, "t": LOG.now, "skipped": skipped})
        if st is not None and not skipped:
            if service == "turn_on":
                st.state = "on"
            elif service == "turn_off":
                st.state = "off"
            elif service in ("set_value", "select_option", "set_temperature"):
                st.state = str(value)
        return await super().async_call(domain, service, data, **kwargs)


_REAL_LOG_HELD = log_latch.log_held


def _log_held(owner, key, latched, *args, **kwargs):
    site = attribute(("hold",))
    out = _REAL_LOG_HELD(owner, key, latched, *args, **kwargs)
    LOG.holds.append({"site": site, "key": key, "latched": bool(latched), "t": LOG.now})
    return out


for _m in (coord_mod, heat_curve, inputs, off_restore, pump_arbiter):
    _m.log_held = _log_held


# --------------------------------------------------------------------------
# The reference plant, its pump, and the plan
# --------------------------------------------------------------------------

def config(rig: str, duty: str = "control") -> dict:
    transport, unit = RIGS[rig]
    cfg = dict(coordinator_scenarios()["coord_all_features"])
    cfg.update(
        pump_duty_mode=duty,
        heat_pump_mode_entity="select.hp_mode",
        dhw_setpoint_entity="number.hp_dhw",
        space_setpoint_entity="number.hp_space",
        space_setpoint_unit=unit,
        heat_pump_switch_entity="switch.hp",
        dhw_setpoint=DHW_CFG,
        dhw_temp_entity="sensor.tank",
        heat_pump_return_temp_entity="sensor.ret",
        dhw_hysteresis_entity="sensor.dhw_hyst",
        dhw_disinfection_switch_entity="switch.hp_disinfect",
        dhw_disinfection_mode="control",
        # The writers beside the arbiter, each on its own option: frequency
        # control, the space circulation pump, the ECL110 MQTT arms and the
        # heat-curve offset entity.
        compressor_freq_entity="number.hp_freq",
        freq_control_mode="control",
        space_circulation_pump_entity="switch.space_pump",
        ecl110_displace_set_topic="ecl110/displace/set",
        ecl110_command_topic="ecl110/command",
        heat_curve_displace_entity="number.curve_offset",
    )
    cfg.update(RIG_EXTRA.get(rig, {}))
    return cfg


def states(rig: str) -> dict:
    transport, unit = RIGS[rig]
    space = (FakeState("35", attributes={"min": 20, "max": 55, "step": 0.5})
             if unit == "flow" else
             FakeState("20.5", attributes={"min": 5, "max": 30, "step": 0.5}))
    return {
        "select.hp_mode": FakeState("Heating + DHW", attributes={"options": MODE_OPTS[transport]}),
        "number.hp_dhw": FakeState("50", attributes={"min": 10, "max": 65, "step": 1}),
        "number.hp_space": space,
        "switch.hp": FakeState("on"),
        "switch.hp_disinfect": FakeState("off"),
        "sensor.tank": FakeState(str(TANK), unit="°C"),
        "sensor.ret": FakeState("28", unit="°C"),
        "sensor.dhw_hyst": FakeState(str(HYST), unit="K"),
        "number.hp_freq": FakeState("40", attributes={"min": 20, "max": 90, "step": FREQ_STEP[0]}),
        "switch.space_pump": FakeState("off"),
        "number.curve_offset": (FakeState("0", attributes={"min": -10, "max": 10, "step": 1})
                                if "pc" not in rig else
                                FakeState("40", attributes={"min": 20, "max": 60, "step": 1})),
        "number.valve": FakeState("22", attributes={"min": 15, "max": 60, "step": 0.5}),
    }


def plan(space_k: float, dhw_k: float, *, last_on: bool = False) -> OptimizationResult:
    sp, dh = [0.0] * N, [0.0] * N
    sp[K], dh[K] = space_k, dhw_k
    if last_on:
        sp[N - 1] = space_k
    return OptimizationResult(
        power_schedule=sp, room_temp_trajectory=[20.5 + 0.1 * i for i in range(N)],
        slab_temp_trajectory=[21.0] * N, timestamps=list(TS), prices=[1.0] * N,
        predicted_cost=0.0, baseline_cost=0.0, predicted_savings=0.0, savings_percentage=0.0,
        optimal_setpoints=[20.0 + 0.25 * i for i in range(N)], status="ok",
        dhw_power_schedule=dh, duty_floor_kw=F,
        heat_pump_on_schedule=[(a > 0 or b > 0) for a, b in zip(sp, dh)],
        valve_target_schedule=[VALVE_K if i == K else VALVE_ELSE for i in range(N)],
        displace_schedule=[DISPLACE_ON if (a > 0 or b > 0) else DISPLACE_OFF for a, b in zip(sp, dh)],
        solve_band={"planned_min_kw": F, "planned_max_kw": P},
    )


_ENTRY_SEQ = [0]


def build(rig: str, duty: str = "control", hass=None, entry=None):
    if hass is None:
        hass = FakeHass(states(rig))
        hass.services = EmuServices(hass)
    if entry is None:
        _ENTRY_SEQ[0] += 1
        entry = FakeEntry(data=config(rig, duty), entry_id=f"d16s1_{_ENTRY_SEQ[0]}")
    c = coord_mod.HeatPumpOptimizerCoordinator(hass, entry)
    entry.runtime_data = c
    c._current_state.dhw_temperature = TANK
    for d in range(10):  # FREQ_MIN_SAMPLES and more in every decile of 20-90 Hz
        hz = 20.0 + (d + 0.5) * 7.0
        for _ in range(6):
            c._freq_map.observe(hz, hz * 0.06, 20.0, 90.0)
    asks = FREQ_ASKS.setdefault(id(c), [])
    real = c._freq_map.recommend

    def recommend(target_kw, hz_min, hz_max):
        asks.append((LOG.now, float(target_kw)))
        return real(target_kw, hz_min, hz_max)
    c._freq_map.recommend = recommend
    return c


FREQ_ASKS: dict[int, list] = {}


def at(t: datetime) -> None:
    LOG.now = t
    dt_util.freeze(t)


def solve(c, result: OptimizationResult, t: datetime, solved_at: datetime | None = None) -> None:
    """What a cycle's solve leaves: the plan, its age, the action cut at ``t``."""
    c._optimization_result = result
    c._last_optimization = solved_at or t
    action = HeatPumpOptimizer(c._thermal_model, OptimizationConfig()).get_current_action(result, t)
    boost.adopt_plan(c, action)


async def cycle(c, t: datetime) -> None:
    """The cycle's actuation tail: the overlay, then ``_apply_action``."""
    at(t)
    boost.apply(c, boost.BoostOverlay(max_power=P, max_temp=float(c._opt_config.max_temp),
                                      ecl_max=float(c._ecl110_displace_max)))
    if c._last_optimization == t:
        # smart_write: the solve's own tail, after a successful solve only.
        await c._command_valve_target()
    await c._apply_action()
    await c._command_frequency()
    await c._async_drive_pumps()


async def tick(c, t: datetime) -> None:
    """The one-minute arbiter tick and the step tick."""
    at(t)
    await pump_arbiter.apply(c, t)
    held = pump_arbiter.state_for(c)
    if held.supply is not None:
        await pump_arbiter.supply_tick(
            held, pump_arbiter.SupplyWiring(c.arbiter_inputs, boost.held_for(c), c._write_supply), t)


async def reload_unload(c) -> None:
    """``async_unload_entry``'s two writes: the off restore, then shutdown."""
    await off_restore.async_restore(c.hass, c.entry, c.effective_config, "unload")
    await c.async_shutdown()


# --------------------------------------------------------------------------
# Driving each state
# --------------------------------------------------------------------------

def _pre(c, res_prev) -> None:
    pass


async def drive(rig: str, state: str) -> dict:
    """Run the state; return the calls and holds inside step K (and the context)."""
    space_k, dhw_k = BOOK[state]
    at(TS[0])  # the coordinator is built (its frequency rate stamp included) on the plan's clock
    c = build(rig)
    t_prev, t_k = TS[K - 1] + timedelta(minutes=2), TS[K] + timedelta(minutes=2)
    extra: dict = {}
    if state == "min-cold-tank":
        c.hass.states.get("sensor.tank").state = "20"
        c._current_state.dhw_temperature = 20.0
    # step K-1: idle (the plan books nothing there)
    res = plan(space_k, dhw_k)
    at(t_prev)
    solve(c, res, t_prev)
    await cycle(c, t_prev)
    mark = len(LOG.calls), len(LOG.holds)
    if state in ("baseline", "baseline-on"):
        res = plan(space_k, dhw_k, last_on=state == "baseline-on")
        # the plan's last step is idle; the solves failed after T0 + 2 min
        t_last = TS[N - 1] + timedelta(minutes=2)
        # The last fresh solve actuated step N-1 (idle, or on for the null
        # arm); every solve after it failed, so the plan goes stale from there.
        solve(c, res, t_last)
        await cycle(c, t_last)
        mark = len(LOG.calls), len(LOG.holds)
        t_past = t_last + timedelta(minutes=100)  # past the plan, and past the stale limit
        if PRE_K[0] is not None:
            await PRE_K[0](c, t_past)
        await cycle(c, t_past)
        for m in (1, 2, 30):
            await tick(c, t_past + timedelta(minutes=m))
        extra["switch_reads"] = c.hass.states.get("switch.hp").state
        return _cut(c, mark, extra)
    if state == "boost-partial":
        at(t_k)
        boost.held_for(c).set(boost.CHANNEL_SPACE, True, t_k)
    if state == "disinfection":
        at(t_k)
        await c._legionella._drive_switch(True)
        extra["memo"] = c._legionella.disinfect.memo
    if state == "unavailable":
        saved = {e: c.hass.states.get(e).state for e in ("select.hp_mode", "number.hp_dhw", "number.hp_space")}
        for e in saved:
            c.hass.states.get(e).state = "unavailable"
    if state in ("observe", "off"):
        # The duty mode changed in the options: Home Assistant reloads the entry.
        solve(c, res, t_k)
        await cycle(c, t_k)   # control writes partial's row first
        at(t_k + timedelta(minutes=1))
        mark = len(LOG.calls), len(LOG.holds)
        await reload_unload(c)
        entry = FakeEntry(data=config(rig, state), entry_id=c.entry.entry_id)
        c = build(rig, hass=c.hass, entry=entry)
        t2 = t_k + timedelta(minutes=2)
        if PRE_K[0] is not None:
            await PRE_K[0](c, t2)
        solve(c, res, t2)
        await cycle(c, t2)
        for m in (3, 4):
            await tick(c, t_k + timedelta(minutes=m))
        extra["returned"] = {e: c.hass.states.get(e).state for e in ("select.hp_mode", "number.hp_dhw", "number.hp_space")}
        return _cut(c, mark, extra)
    if state in ("restart", "upgrade"):
        if state == "restart":
            solve(c, res, t_k)
            await cycle(c, t_k)
            await reload_unload(c)
            entry = FakeEntry(data=config(rig), entry_id=c.entry.entry_id)
        else:
            # A fresh entry whose stores the previous tag wrote at K-1 and K.
            _ENTRY_SEQ[0] += 1
            entry = FakeEntry(data=config(rig), entry_id=f"d16s1_{_ENTRY_SEQ[0]}")
            await upgrade_store(rig, entry.entry_id)
            hass = FakeHass(states(rig))
            hass.services = EmuServices(hass)
            for e, (st, _a) in UPGRADE["old_states"].items():
                hass.states.get(e).state = st
            c.hass = hass
        mark = len(LOG.calls), len(LOG.holds)
        c = build(rig, hass=c.hass, entry=entry)
        t2 = t_k + timedelta(minutes=5)
        if PRE_K[0] is not None:
            await PRE_K[0](c, t2)
        solve(c, res, t2)
        await cycle(c, t2)
        for m in (6, 7):
            await tick(c, t_k + timedelta(minutes=m))
        return _cut(c, mark, extra)
    if PRE_K[0] is not None:
        await PRE_K[0](c, t_k)
    solve(c, res, t_k)
    await cycle(c, t_k)
    if state == "unavailable":
        extra["recorded_while_unavailable"] = sorted(pump_arbiter.state_for(c).written)
        extra["skipped"] = [x for x in LOG.calls[mark[0]:] if x["skipped"]]
        at(t_k + timedelta(minutes=1))
        for e, v in saved.items():
            c.hass.states.get(e).state = v
    offs = (3, 4, 9, 12) if state == "both" else (3, 4)
    for m in offs:
        await tick(c, TS[K] + timedelta(minutes=m))
    return _cut(c, mark, extra)


async def upgrade_store(rig: str, entry_id: str) -> None:
    """The previous tag's arbiter writes this entry's stores: ``old_release.py``
    runs steps K-1 and K on ``git archive v10.0.2``, and this release loads
    what it saved."""
    tag = "v10.0.2"
    tmp = Path(tempfile.mkdtemp(prefix="d16s1_upgrade_"))
    arc = subprocess.run(["git", "archive", tag, "custom_components", "tests"],
                         capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(tmp)], input=arc, check=True)
    here = Path(__file__).resolve().parent
    rig_json = json.dumps({"config": config(rig), "states": {
        e: [s.state, s.attributes] for e, s in states(rig).items()}, "entry_id": entry_id,
        "ts": [t.isoformat() for t in TS], "K": K, "book": BOOK["partial"], "F": F, "P": P})
    out = subprocess.run([sys.executable, str(here / "old_release.py")], cwd=tmp, input=rig_json,
                         env={**os.environ, "PYTHONPATH": "tests/hastub"},
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"previous tag's run failed: {out.stderr[-3000:]}")
    payload = json.loads(out.stdout.strip().splitlines()[-1])
    UPGRADE["old_calls"] = payload["calls"]
    UPGRADE["old_states"] = payload["states"]
    for key, raw in payload["disk"].items():
        _storage._DISK[key] = raw
        _storage._VERSIONS[key] = payload["versions"].get(key, 1)


UPGRADE: dict = {}


def _cut(c, mark, extra) -> dict:
    extra["freq_asks"] = FREQ_ASKS.get(id(c), [])
    calls = LOG.calls[mark[0]:]
    holds = LOG.holds[mark[1]:]
    return {"calls": calls, "holds": holds, "written": dict(pump_arbiter.state_for(c).written),
            "extra": extra, "coord": c, "rig": RIG_NOW[0]}


RIG_NOW = [""]


# --------------------------------------------------------------------------
# ORACLE: D16.md's table, read off the plan by plain indexing
# --------------------------------------------------------------------------

def _kind(e: str | None) -> str:
    return {"select.hp_mode": "mode", "number.hp_dhw": "dhw", "number.hp_space": "space",
            "switch.hp": "supply", "switch.hp_disinfect": "disinfect", "number.hp_freq": "freq",
            "switch.space_pump": "circ", "number.curve_offset": "curve",
            "ecl110/displace/set": "mqtt_set", "ecl110/command": "mqtt_cmd", "number.valve": "valve"}.get(e or "", "other")


def _mode_key(option) -> str:
    o = str(option).lower()
    if "dhw" in o and "heat" in o:
        return "both"
    if "dhw" in o or "hot water" in o:
        return "dhw"
    if "heat" in o:
        return "space"
    return o


def _in_step(x, k=K) -> bool:
    return x["t"] is not None and TS[k] <= x["t"] < TS[k] + timedelta(minutes=15)


def _range_ok(x, st_attrs) -> bool:
    v = x["value"]
    if not isinstance(v, (int, float)):
        return True
    lo, hi, step = st_attrs.get("min"), st_attrs.get("max"), st_attrs.get("step", 1)
    on = abs(round(v / step) * step - v) < 1e-9
    return (lo is None or v >= lo) and (hi is None or v <= hi) and on


def grade(rig: str, state: str, run: dict, gate_value: float | None, levels: dict) -> list[str]:
    """Return the violated clauses of the state's row (empty: the row holds)."""
    transport, unit = RIGS[rig]
    calls = [x for x in run["calls"] if not x["skipped"]]
    c = run["coord"]
    bad: list[str] = []
    attrs = {e: c.hass.states.get(e).attributes
             for e in ("number.hp_dhw", "number.hp_space", "number.hp_freq", "number.curve_offset",
                       "number.valve")}
    for x in calls:
        if _kind(x["entity"]) in ("dhw", "space", "freq", "curve", "valve") and not _range_ok(x, attrs[x["entity"]]):
            bad.append(f"[grid] outside min/max/step: {x['entity']}={x['value']}")
    step = [x for x in calls if _in_step(x)]
    modes = [_mode_key(x["value"]) for x in step if _kind(x["entity"]) == "mode"]
    dhw = [x["value"] for x in step if _kind(x["entity"]) == "dhw"]
    space = [x["value"] for x in step if _kind(x["entity"]) == "space"]
    sup = [x["service"] for x in step if _kind(x["entity"]) == "supply"]
    tank = float(c.hass.states.get("sensor.tank").state)
    sp_k = BOOK[state][0]
    planned_room = plan(*BOOK[state]).optimal_setpoints[K]  # index K, plain
    # The device's state after the step's writes: what the pump now holds.
    mode_now = _mode_key(c.hass.states.get("select.hp_mode").state)
    dhw_now = float(c.hass.states.get("number.hp_dhw").state)
    space_now = float(c.hass.states.get("number.hp_space").state)

    def tank_asked() -> bool:
        return mode_now in ("dhw", "both") and dhw_now - HYST > tank

    if state == "idle":
        if modes:
            bad.append(f"mode written on idle: {modes}")
        if "turn_on" in sup:
            bad.append("supply switched on on idle")
    elif state in ("min-cold-tank", "partial", "full", "restart", "upgrade"):
        if tank_asked():
            bad.append(f"tank asked to charge: mode {mode_now}, tank set-point {dhw_now} "
                       f"- hysteresis {HYST} > tank {tank}")
        if unit == "indoor":
            # The device's reading after the step's writes: a write sent on an
            # earlier step that already holds the value is not re-sent.
            if space_now != planned_room:
                bad.append(f"indoor set-point {space_now} != optimal_setpoints[K] {planned_room}")
        else:
            if space and gate_value is not None and not space[-1] > gate_value:
                bad.append(f"water set-point {space[-1]} not above the do-not-heat value {gate_value}")
        if "turn_off" in sup:
            bad.append("supply switched off on a heating step")
    elif state == "dhw-only":
        if transport == "fork":
            if mode_now != "dhw":
                bad.append(f"mode {mode_now} where the pump offers hot water only")
        else:
            sv = float(c.hass.states.get("number.hp_space").state)
            no_heat = gate_value if unit == "flow" else attrs["number.hp_space"].get("min")
            if sv > no_heat + 1e-9:
                bad.append(f"space set-point {sv} calls for heat (no-heat value {no_heat})")
        if dhw_now != DHW_CFG:
            bad.append(f"tank set-point {dhw_now} != configured {DHW_CFG}")
    elif state == "both":
        first = modes[0] if modes else None
        want_first = "dhw" if transport == "fork" else "both"
        if first != want_first:
            bad.append(f"first mode in the step {first}, hot water first expected")
        if transport == "fork" and "space" not in modes:
            bad.append(f"house never asked inside the step: modes {modes}")
    elif state == "boost-partial":
        if unit == "flow":
            top = min(attrs["number.hp_space"]["max"], 55.0)
            if not space or space[-1] != top:
                bad.append(f"boost water set-point {space[-1] if space else None} != band top {top}")
        else:
            top = float(c._opt_config.max_temp)
            if space_now != top:
                bad.append(f"boost indoor set-point {space_now} != band top "
                           f"(max_temperature {top}); plan's step K booked {planned_room}")
    elif state == "disinfection":
        target = float(c._thermal_params.dhw_legionella_temp)
        if not dhw or dhw[-1] < target:
            bad.append(f"tank write {dhw[-1] if dhw else None} below the disinfection target {target}")
    elif state == "baseline":
        sw = run["extra"].get("switch_reads")
        if sw != "on":
            bad.append(f"[switch] supply switch reads {sw} past the plan: the pump is not handed back")
        if mode_now != "both":
            bad.append(f"mode {mode_now}, both circuits not allowed")
        if dhw_now != DHW_CFG:
            bad.append(f"tank set-point {dhw_now} != configured {DHW_CFG}")
    elif state == "unavailable":
        rec = run["extra"]["recorded_while_unavailable"]
        skipped = {_kind(x["entity"]) for x in run["extra"]["skipped"]}
        slot_of = {"mode": "mode", "dhw": "dhw_setpoint", "space": "space_setpoint"}
        false = sorted(s for s in skipped if slot_of.get(s) in rec)
        if false:
            bad.append(f"write recorded as made while Home Assistant skipped it: {false}")
        if tank_asked():
            bad.append("tank asked to charge once back")
        if unit == "indoor" and float(c.hass.states.get("number.hp_space").state) != planned_room:
            bad.append("partial's indoor set-point not restored once back")
    elif state in ("observe", "off"):
        # Every write after the reload is a write under that duty mode.
        # The reload is at TS[K] + 3 min; every pass after it runs under that
        # duty mode. The power switch is out of the row: "With any of the
        # three, the heat pump on/off switch ... is still switched by the
        # plan" (strings.json, pump_duty_mode).
        reload_t = TS[K] + timedelta(minutes=3)
        # Likewise the writers on options of their own (frequency mode, the
        # circulation pump, the ECL110 topics, the heat-curve entity): the
        # duty mode governs the three arbiter slots.
        after = [x for x in calls if x["t"] is not None and x["t"] > reload_t
                 and _kind(x["entity"]) in ("mode", "dhw", "space")]
        if after:
            bad.append(f"writes under duty mode {state}: {[(x['entity'], x['value']) for x in after]}")
        counts = defaultdict(int)
        for x in calls:
            if x["t"] is not None and x["t"] <= reload_t:
                counts[x["entity"]] += 1
        many = {e: n for e, n in counts.items() if n > 1 and _kind(e) in ("mode", "dhw", "space")}
        if many:
            bad.append(f"an entity returned more than once: {many}")
    bad += grade_aux(state, run, calls)
    return bad


#: States whose step K is actuated by a fresh plan's cycle, and what each books.
FRESH = ("idle", "min-cold-tank", "partial", "full", "dhw-only", "both", "boost-partial",
         "disinfection", "restart", "upgrade", "unavailable")


def grade_aux(state: str, run: dict, calls: list[dict]) -> list[str]:
    """The writers beside the arbiter, on their own oracle read off the plan:
    the frequency write's entity grid and the kW it was cut for, the ECL110 /
    heat-curve displace (``displace_schedule[K]``), the circulation pump."""
    bad: list[str] = []
    space_k, dhw_k = BOOK[state]
    booked = space_k > 0 or dhw_k > 0
    boosted = state == "boost-partial"
    res = plan(space_k, dhw_k)
    step = [x for x in calls if _in_step(x)]
    freq = [x for x in step if _kind(x["entity"]) == "freq"]
    asks = [a for a in run["extra"].get("freq_asks", []) if TS[K] <= a[0] < TS[K + 1]]
    if state in FRESH:
        if not booked and freq:
            bad.append(f"[freq] frequency written on an idle step: {[x['value'] for x in freq]}")
        want_kw = (P if boosted else space_k) + dhw_k
        for when, kw in asks:
            if abs(kw - want_kw) > 1e-6:
                bad.append(f"[freq] frequency cut for {kw} kW, the plan books {want_kw} kW")
        mset = [x["value"] for x in step if _kind(x["entity"]) == "mqtt_set"]
        want_d = 20 if boosted else int(res.displace_schedule[K])
        if mset and mset[-1] != str(want_d):
            bad.append(f"[mqtt] displace {mset[-1]} != plan displace {want_d}")
        mcmd = [json.loads(x["value"]) for x in step if _kind(x["entity"]) == "mqtt_cmd"]
        if mcmd and bool(mcmd[-1]["command"]["heat_pump_on"]) != booked:
            bad.append(f"[mqtt] legacy heat_pump_on {mcmd[-1]['command']['heat_pump_on']} != booked {booked}")
        valve = [x["value"] for x in step if _kind(x["entity"]) == "valve"]
        if "pc" in run.get("rig", "") and state not in ("restart", "upgrade", "unavailable"):
            want_v = 24.0  # valve_target_schedule[K] = 24.3, on the 0.5 step rounded down (a cap)
            if not valve or valve[-1] != want_v:
                bad.append(f"[valve] valve write {valve[-1] if valve else None} != plan's {want_v}")
        if space_k > 0:
            circ = run["coord"].hass.states.get("switch.space_pump").state
            if circ != "on":
                bad.append(f"[circ] space circulation pump {circ} on a heating step")
    if state == "baseline":
        late = [x for x in calls if _kind(x["entity"]) in ("freq", "mqtt_set", "mqtt_cmd", "curve")]
        if late:
            bad.append(f"[stale] plan-driven writes after the plan went stale: "
                       f"{[(x['entity'], x['value']) for x in late][:4]}")
    return bad


# --------------------------------------------------------------------------
# Perturbations
# --------------------------------------------------------------------------

def perturbation(name: str | None):
    stack = []
    if name == "P1":
        real = pump_arbiter._step_index

        def late(result, now):
            i = real(result, now)
            return None if i is None else max(i - 1, 0)
        stack.append(mock.patch.object(pump_arbiter, "_step_index", late))
        real_sd = pump_arbiter.step_duty

        def late_duty(result, now):
            return real_sd(result, now - timedelta(minutes=15))
        stack.append(mock.patch.object(pump_arbiter, "step_duty", late_duty))
        real_room = pump_arbiter._planned_room

        def late_room(result, now, attr="optimal_setpoints"):
            return real_room(result, now - timedelta(minutes=15), attr)
        stack.append(mock.patch.object(pump_arbiter, "_planned_room", late_room))
    elif name == "P2":
        real = pump_arbiter.desired

        def tank_too(coord, inp, duty, now):
            cmd = real(coord, inp, duty, now)
            if duty == "space":
                return replace(cmd, mode="HEATDHW", dhw_setpoint=DHW_CFG)
            return cmd
        stack.append(mock.patch.object(pump_arbiter, "desired", tank_too))
        stack.append(mock.patch.object(pump_arbiter, "__doc__", pump_arbiter.__doc__.replace(
            "space only     Heating, if offered", "space only     Heating + DHW      ")))
    elif name == "P2doc":
        stack.append(mock.patch.object(pump_arbiter, "__doc__", pump_arbiter.__doc__.replace(
            "space only     Heating, if offered", "space only     Heating + DHW      ")))
    elif name == "dhw_gate":
        stack.append(mock.patch.object(pump_arbiter, "DHW_GATE_C", 10.0))
    elif name == "boost_indoor":
        real = pump_arbiter.desired

        def top(coord, inp, duty, now):
            cmd = real(coord, inp, duty, now)
            if (not pump_arbiter._flow_unit(inp.config) and cmd.space_setpoint is not None
                    and boost.held_for(coord).active(boost.CHANNEL_SPACE, now)):
                return replace(cmd, space_setpoint=float(coord._opt_config.max_temp))
            return cmd
        stack.append(mock.patch.object(pump_arbiter, "desired", top))
    elif name == "write_skips_unavailable":
        real = pump_arbiter._write

        async def skip(coord, inp, slot, value, now, command=None):
            entity = pump_arbiter._slot_entity(inp.config, slot)
            st = inp.hass.states.get(entity) if entity else None
            if st is not None and st.state == "unavailable":
                return  # the one-line edit: an unavailable entity is no write, so no record
            return await real(coord, inp, slot, value, now, command)
        stack.append(mock.patch.object(pump_arbiter, "_write", skip))
    elif name == "freq_grid":
        from heatpump_optimizer import freq_control
        real = freq_control.FrequencyMap.recommend

        def on_grid(self, target_kw, hz_min, hz_max):
            hz = real(self, target_kw, hz_min, hz_max)
            return None if hz is None else float(round(hz))  # the entity's 1 Hz step
        stack.append(mock.patch.object(freq_control.FrequencyMap, "recommend", on_grid))
    elif name == "stale_on":
        real = coord_mod.HeatPumpOptimizerCoordinator._apply_action

        async def stale_on(self):
            await real(self)
            if self._mode in ("auto", "economy") and self._plan_is_stale():
                await self._write_supply(True)
        stack.append(mock.patch.object(coord_mod.HeatPumpOptimizerCoordinator, "_apply_action", stale_on))
    return stack


# --------------------------------------------------------------------------
# The holds on the solve and fetch path: does their latch gate a write?
# --------------------------------------------------------------------------

PRE_K: list = [None]


def _prices(c, t0):
    return [{"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
             "starts_at": (t0 + timedelta(hours=h)).isoformat(), "level": "NORMAL"} for h in range(48)]


def _weather(t0):
    return [{"datetime": (t0 + timedelta(hours=h)).isoformat(), "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
             "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0} for h in range(48)]


async def _timeout(*_a, **_k):
    raise coord_mod.ProcessWorkerTimeout("probe: the worker outran its reply deadline")


async def _hold_703(c, t):
    coord_mod._note_solve_failure(c, RuntimeError("probe"))


async def _hold_solve(c, t):
    """A real solve through ``async_run_optimization`` (3-4 s): it evaluates
    6457, 7234, 7250, 7312 and 2340 on its own path; the harness's plan is
    put back after it by the step-K ``solve`` that follows."""
    c._prices, c._weather_forecast = _prices(c, TS[0]), _weather(TS[0])
    c._solar_radiation_forecast = [max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)]
    await c.async_run_optimization()


async def _hold_7169(c, t):
    cfg = c._ctx._config
    object.__setattr__(c._ctx, "_config", replace(cfg, solar_location={"latitude": "north", "longitude": "x"}))
    try:
        c._solar_location()
    finally:
        object.__setattr__(c._ctx, "_config", cfg)


async def _hold_7185(c, t):
    with mock.patch.object(type(c), "_solar_forecast_source", lambda self: coord_mod.SOLAR_SOURCE_OPEN_METEO), \
            mock.patch.object(type(c), "_solar_location", lambda self: None):
        await c._fetch_solar_forecast()


async def _hold_7234(c, t):
    c._prices = []
    c._price_series(96, TS[0], 0)


async def _hold_7250(c, t):
    c._prices = _prices(c, TS[0] - timedelta(days=5))
    c._price_series(96, TS[0], 0)


async def _hold_7312(c, t):
    c._weather_forecast = []
    c._weather_series(96, TS[0], 0)


async def _hold_2148(c, t):
    with mock.patch.object(coord_mod, "_await_process", _timeout):
        try:
            await coord_mod._await_off_loop(c.hass, _probe_fn)
        except coord_mod.ProcessWorkerTimeout:
            pass


async def _hold_2153(c, t):
    async def ok(_hass, fn, *args):
        return fn(*args)
    with mock.patch.object(coord_mod, "_await_process", ok):
        await coord_mod._await_off_loop(c.hass, _probe_fn)


async def _hold_2322(c, t):
    with mock.patch.object(coord_mod, "_await_process", _timeout):
        try:
            await coord_mod._await_optimize(c.hass, None, None)
        except Exception:  # noqa: BLE001 - UpdateFailed: the cycle keeps the last plan
            pass


def _probe_fn():
    return None


GATE_HOOKS = {
    703: _hold_703, 2148: _hold_2148, 2153: _hold_2153, 2322: _hold_2322,
    7169: _hold_7169, 7185: _hold_7185, 7234: _hold_7234, 7250: _hold_7250, 7312: _hold_7312,
    6457: _hold_solve, 2340: _hold_solve,
}


def _sig(run):
    return [(x["entity"], x["service"], str(x["value"]) if _kind(x["entity"]) != "mqtt_cmd"
             else json.loads(x["value"])["command"]) for x in run["calls"]]


async def gate_arm(states_: tuple[str, ...]) -> dict:
    """Per coordinator hold site x state on fork-flow: the site's own function
    driven at step K (latched where it has a latched branch), then the step's
    commands compared with the same state run without it."""
    out = {}
    RIG_NOW[0] = "fork-flow"
    for state in states_:
        PRE_K[0] = None
        base = _sig(await drive("fork-flow", state))
        runs = {}
        for ln, hook in GATE_HOOKS.items():
            if hook not in runs:
                PRE_K[0] = hook
                mark = len(LOG.holds)
                try:
                    run = await drive("fork-flow", state)
                finally:
                    PRE_K[0] = None
                runs[hook] = (run, LOG.holds[mark:])
            run, holds = runs[hook]
            hit = [h for h in holds if h["site"] == (PKG + "coordinator.py", ln)]
            diff = sum(1 for a, b in zip(base, _sig(run)) if a != b) + abs(len(base) - len(_sig(run)))
            out[(ln, state)] = {"evaluated": len(hit), "latched": sum(h["latched"] for h in hit),
                                "command_diff": diff}
    return out


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

async def gate_of(rig: str) -> float | None:
    """The value a water set-point takes on a step that does not heat: the
    idle row's write, measured (the "do-not-heat value" of the table)."""
    run = await drive(rig, "idle-gate")
    return run


async def run_all(args) -> dict:
    out: dict = {"rigs": {}}
    for rig in RIGS:
        transport, unit = RIGS[rig]
        runs = {}
        for state in STATES:
            for k in list(_storage._DISK):
                if k.startswith("heatpump_optimizer_d16s1"):
                    pass
            RIG_NOW[0] = rig
            runs[state] = await drive(rig, state)
        # The do-not-heat value: what the idle-booked step K-1 wrote to the
        # space entity in the partial run (the step before K is idle).
        gate = None
        if unit == "flow":
            pre = [x for x in LOG.calls if _kind(x["entity"]) == "space"]
            idle_writes = [x["value"] for x in runs["partial"]["calls"]]
            c = runs["partial"]["coord"]
            gate = float(c.hass.states.get("number.hp_space").attributes["min"])
            gate = max(gate, 25.0)
        levels = {}
        rows = {}
        for state in STATES:
            rows[state] = grade(rig, state, runs[state], gate, levels)
        # Null control for the baseline row, never a cell: the plan went stale
        # while its last step had the supply on.
        RIG_NOW[0] = rig
        runs["baseline-on"] = await drive(rig, "baseline-on")
        rows["baseline-on"] = grade(rig, "baseline", runs["baseline-on"], gate, levels)
        if unit == "flow":
            seq = []
            for s in ("min-cold-tank", "partial", "full"):
                sv = [x["value"] for x in runs[s]["calls"] if _kind(x["entity"]) == "space" and _in_step(x)]
                seq.append(sv[-1] if sv else None)
            if None not in seq and not (seq[0] <= seq[1] <= seq[2]):
                rows["full"].append(f"water set-point falls as booked kW rises: {seq}")
            levels["water"] = seq
        out["rigs"][rig] = {"rows": rows, "levels": levels, "runs": runs}
    return out


def cell_table(out: dict) -> dict[str, dict]:
    """Every enumerator cell: what its site did in its state, on each rig."""
    table: dict[str, dict] = {}
    for line in CELLS:
        head, state = line.split(" | ")
        kind, loc = head.split(" ")[:2]
        path, ln = loc.rsplit(":", 1)
        key = (path, int(ln))
        per = {}
        for rig, data in out["rigs"].items():
            run = data["runs"][state]
            if kind == "write":
                hits = [x for x in run["calls"] if x["site"] == key]
                per[rig] = {"calls": len(hits),
                            "values": [(x["entity"], x["value"], x["skipped"]) for x in hits][:8],
                            "row_fail": data["rows"][state]}
            else:
                hits = [x for x in run["holds"] if x["site"] == key]
                per[rig] = {"evaluations": len(hits), "latched": sum(x["latched"] for x in hits),
                            "row_fail": data["rows"][state]}
        if kind == "hold" and (key[1], state) in out.get("gates", {}) and key[0].endswith("coordinator.py"):
            per["gate-arm"] = dict(out["gates"][(key[1], state)], row_fail=[])
            per["gate-arm"]["evaluations"] = per["gate-arm"]["evaluated"]
        table[line] = per
    return table


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb")
    ap.add_argument("--json")
    ap.add_argument("--no-gates", action="store_true", help="skip the solve/fetch hold arm (about a minute)")
    args = ap.parse_args()
    global HA_SKIPS_UNAVAILABLE
    if args.perturb == "ha_skip_off":
        HA_SKIPS_UNAVAILABLE = False
    if args.perturb == "freq_step_half":
        FREQ_STEP[0] = 0.5
    dt_util.DEFAULT_TIME_ZONE = timezone.utc
    stack = perturbation(args.perturb)
    for p in stack:
        p.start()
    w0, c0, t0 = time.perf_counter(), time.process_time(), time.thread_time()
    try:
        out = asyncio.run(run_all(args))
        out["gates"] = {} if args.no_gates else asyncio.run(gate_arm(STATES))
    finally:
        for p in reversed(stack):
            p.stop()
        dt_util.freeze(None)
    table = cell_table(out)
    unattributed = [x for x in LOG.calls if x["site"] is None]
    print(f"RESULT cells={len(CELLS)} count")
    print(f"RESULT examined={len(table)} count")
    print(f"RESULT unattributed_calls={len(unattributed)} count")
    for x in unattributed[:5]:
        print(f"  unattributed: {x['domain']}.{x['service']} {x['entity']} {x['value']}")
    fails_total = 0
    for rig, data in out["rigs"].items():
        for state in STATES:
            bad = data["rows"][state]
            fails_total += bool(bad)
            print(f"ROW {rig:12s} {state:14s} {'FAIL' if bad else 'ok'} {'; '.join(bad)}")
        bad = data["rows"]["baseline-on"]
        print(f"NULL {rig:12s} baseline-on    {'FAIL' if bad else 'ok'} {'; '.join(bad)}")
        print(f"LEVELS {rig} {data['levels']}")
    gates = out.get("gates", {})
    if gates:
        print(f"RESULT gate_cells={len(gates)} count (coordinator solve/fetch hold x state, fork-flow)")
        print(f"RESULT gate_cells_evaluated={sum(1 for v in gates.values() if v['evaluated'])} count")
        print(f"RESULT gate_cells_latched={sum(1 for v in gates.values() if v['latched'])} count")
        print(f"RESULT gate_cells_command_diff={sum(1 for v in gates.values() if v['command_diff'])} count "
              "(cells whose latch changed the state's commands)")
    fail_cells = sum(1 for per in table.values() if any(v["row_fail"] for v in per.values()))
    reached = sum(1 for line, per in table.items()
                  if any((v.get("calls") or v.get("evaluations")) for v in per.values()))
    print(f"RESULT failing_rows={fails_total} count (rig x state)")
    print(f"RESULT fail_cells={fail_cells} count (cells whose state row fails on some rig)")
    print(f"RESULT cells_with_site_activity={reached} count")
    value_states = ("idle", "min-cold-tank", "partial", "full", "dhw-only", "both", "boost-partial",
                    "disinfection", "restart", "upgrade")
    arb = sum(1 for rig, data in out["rigs"].items() for st in value_states
              if any(not b.startswith("[") for b in data["rows"][st]))
    print(f"RESULT arbiter_value_rows_failing={arb} rows (rig x value state, untagged arbiter clauses; "
          f"P1 and P2 raise it, P2doc leaves it)")
    for tag in ("grid", "freq", "mqtt", "circ", "stale", "switch", "valve"):
        n = sum(1 for rig, data in out["rigs"].items() for st, bad in data["rows"].items()
                if st in STATES and any(b.startswith(f"[{tag}]") for b in bad))
        print(f"RESULT clause_{tag}={n} rows (rig x state)")
    for name, rowkey in (("cold_tank_charge", "min-cold-tank"), ("boost_indoor_between", "boost-partial"),
                         ("baseline_switch_off", "baseline"), ("unavailable_recorded", "unavailable")):
        n = sum(1 for rig, data in out["rigs"].items()
                if any(not b.startswith(("[grid]", "[freq]", "[mqtt]", "[circ]", "[stale]", "[valve]"))
                       for b in data["rows"][rowkey]))
        print(f"RESULT {name}={n} rigs")
    wall = time.perf_counter() - w0
    tf = (time.process_time() - c0) / max(time.thread_time() - t0, 1e-9)
    print(f"RESULT wall_s={wall:.1f} s provisional")
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in Path('/proc/vmstat').read_text().splitlines() if l.startswith('pswpin')]
        print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")
    except OSError:
        print("RESULT swapins=0")
    if args.json:
        Path(args.json).write_text(json.dumps(table, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
