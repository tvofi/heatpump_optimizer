"""D16-s2 shared rig: the real coordinator on the reference plant, a plan the harness books,
a device that takes every write, and a minute clock that drives the production cycle and ticks.

Not a harness on its own (no RESULT lines); timing.py and effect.py import it.
Run from the export root with PYTHONPATH=tests/hastub. Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.

The oracle half (``Plan``, ``oracle_*``) imports nothing from pump_arbiter and calls no step
selection of the package's: the step covering a minute is found here by plain arithmetic on the
plan's own ``timestamps`` and read by plain indexing.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import sys
import tempfile
from dataclasses import replace
from datetime import datetime, timedelta, timezone

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.environ.get("D16_ROOT") or os.path.abspath(os.path.join(_HERE, *[".."] * 6))
sys.path.insert(0, os.path.join(_ROOT, "tests"))
sys.path.insert(0, os.path.join(_ROOT, "custom_components"))
# Private store root: the storage stub writes under the cwd's .storage otherwise.
os.environ.setdefault("HPO_PLANDATA", tempfile.mkdtemp(prefix="d16s2-"))

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import golden  # noqa: E402
from heatpump_optimizer import boost, pump_arbiter  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.optimizer import OptimizationResult  # noqa: E402

UTC = timezone.utc
T0 = datetime(2026, 1, 12, 6, 0, tzinfo=UTC)  # a step-grid instant
STEP = timedelta(minutes=15)

ENT = {
    "switch": "switch.hp_power",
    "mode": "select.hp_mode",
    "dhw": "number.hp_dhw_set",
    "flow": "number.hp_flow_set",
    "freq": "number.hp_freq",
    "space_pump": "switch.space_pump",
    "curve": "number.curve_offset",
}
TOPIC = "ecl110/displace/set"
TUYA_OPTIONS = ["Heating", "DHW (Hot Water)", "Heating + DHW", "Cooling", "Cooling + DHW"]


def config(**extra):
    """``coord_all_features`` with the actuators wired (D16: you run the reference plant)."""
    cfg = dict(golden.coordinator_scenarios()["coord_all_features"])
    cfg.update({
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        "dhw_temp_entity": "sensor.tank",
        "heat_pump_power_entity": "sensor.hp_power",
        "heat_pump_return_temp_entity": "sensor.hp_return",
        "heat_pump_switch_entity": ENT["switch"],
        "heat_pump_mode_entity": ENT["mode"],
        "dhw_setpoint_entity": ENT["dhw"],
        "space_setpoint_entity": ENT["flow"],
        "space_setpoint_unit": "flow",
        "pump_duty_mode": "control",
        "dhw_setpoint": 50.0,
        "dhw_min_temperature": 40.0,
        "space_circulation_pump_entity": ENT["space_pump"],
        "ecl110_displace_set_topic": TOPIC,
        "heat_curve_displace_entity": ENT["curve"],
        "compressor_freq_entity": ENT["freq"],
        "freq_control_mode": "control",
    })
    cfg.update(extra)
    return {k: v for k, v in cfg.items() if v is not None}


def states(now, **over):
    s = {
        "sensor.indoor": FakeState("20.5", unit="°C", last_updated=now),
        "sensor.outdoor": FakeState("-2.0", unit="°C", last_updated=now),
        "sensor.tank": FakeState("44.0", unit="°C", last_updated=now),
        "sensor.hp_power": FakeState("0.0", unit="kW", last_updated=now),
        "sensor.hp_return": FakeState("30.0", unit="°C", last_updated=now),
        ENT["switch"]: FakeState("off", last_updated=now - timedelta(hours=2)),
        ENT["mode"]: FakeState("Heating + DHW", attributes={"options": list(TUYA_OPTIONS)},
                               last_updated=now - timedelta(hours=2)),
        ENT["dhw"]: FakeState("50", attributes={"min": 30, "max": 65, "step": 1},
                              last_updated=now - timedelta(hours=2)),
        ENT["flow"]: FakeState("35", attributes={"min": 20, "max": 60, "step": 1},
                               last_updated=now - timedelta(hours=2)),
        ENT["freq"]: FakeState("0", attributes={"min": 20, "max": 90, "step": 1},
                               last_updated=now - timedelta(hours=2)),
        ENT["space_pump"]: FakeState("off", last_updated=now - timedelta(hours=2)),
        ENT["curve"]: FakeState("0", unit="K", attributes={"min": -10, "max": 10, "step": 1},
                                last_updated=now - timedelta(hours=2)),
    }
    s.update(over)
    return s


class Device:
    """Takes every service call the way the entity would: the state moves, stamped now."""

    def __init__(self, hass):
        self.hass = hass
        self.log = []  # (instant, domain, service, data)
        for dom, svcs in {
            "switch": ("turn_on", "turn_off"), "homeassistant": ("turn_on", "turn_off"),
            "select": ("select_option",), "number": ("set_value",),
            "input_number": ("set_value",), "mqtt": ("publish",), "climate": ("set_temperature",),
        }.items():
            for svc in svcs:
                hass.services.async_register(dom, svc, self._handler(dom, svc))

    def _handler(self, dom, svc):
        async def _h(call):
            now = dt_util.now()
            data = dict(call.data)
            self.log.append((now, dom, svc, data))
            ent = data.get("entity_id")
            if dom == "mqtt":
                return
            st = self.hass.states.get(ent) if ent else None
            if st is None:
                return
            old = st.state
            if svc in ("turn_on", "turn_off"):
                st.state = "on" if svc == "turn_on" else "off"
            elif svc == "select_option":
                st.state = data["option"]
            elif svc == "set_value":
                st.state = str(data["value"])
            if st.state != old:
                st.last_changed = now
            st.last_updated = st.last_reported = now
        return _h


def plan(rows, start=T0, floor=None, setpoints=None, dhw_reasons=None):
    """A solve result the harness books: ``rows`` is [(space_kw, dhw_kw)] per 15-min step."""
    n = len(rows)
    space = [float(r[0]) for r in rows]
    dhw = [float(r[1]) for r in rows]
    stamps = [start + STEP * i for i in range(n)]
    sp = list(setpoints) if setpoints is not None else [21.0] * n
    return OptimizationResult(
        power_schedule=space, room_temp_trajectory=[20.8] * n, slab_temp_trajectory=[21.0] * n,
        timestamps=stamps, prices=[1.0] * n, predicted_cost=0.0, baseline_cost=0.0,
        predicted_savings=0.0, savings_percentage=0.0, optimal_setpoints=sp, status="optimal",
        dhw_power_schedule=dhw,
        heat_pump_on_schedule=[(s > 0.0 or d > 0.0) for s, d in zip(space, dhw)],
        displace_schedule=[round(6.0 * s / max(max(space), 1e-9)) if s > 0 else -2.0 for s in space],
        duty_floor_kw=floor,
        **({"dhw_reasons": list(dhw_reasons)} if dhw_reasons is not None else {}),
    )


def oracle_index(result, now):
    """Plain arithmetic on the plan's own stamps: the k whose [t_k, t_k + 15 min) holds now."""
    t = result.timestamps
    for k in range(len(t)):
        if t[k] <= now < t[k] + STEP:
            return k
    return None


class Sim:
    """One coordinator, one device, one frozen clock."""

    _ids = iter(range(10**6))

    def __init__(self, cfg=None, st=None, now=T0, seed_freq=True, hass=None, entry=None):
        dt_util.freeze(now)
        self.now = now
        if hass is None:
            self.hass = FakeHass(st if st is not None else states(now))
            self.dev = Device(self.hass)
        else:  # a reload: the same Home Assistant, state machine and store
            self.hass, self.dev = hass, hass._d16_device
        self.hass._d16_device = self.dev
        # One store key per simulated install: the storage stub outlives FakeHass.
        self.entry = entry or FakeEntry(data=cfg or config(), entry_id=f"d16s2_{next(Sim._ids)}_{os.getpid()}")
        self.coord = HeatPumpOptimizerCoordinator(self.hass, self.entry)
        self.coord._mode = "auto"
        if seed_freq:
            fm = self.coord._freq_map
            for hz in range(24, 90, 7):
                for _ in range(12):
                    fm.observe(float(hz), 0.05 * hz, 20.0, 90.0)

    def at(self, now):
        self.now = now
        dt_util.freeze(now)

    def run(self, coro):
        return asyncio.run(coro)

    def adopt(self, result):
        """The solve's adoption lines (coordinator.async_run_optimization), on the harness's plan."""
        c = self.coord
        c._optimization_result = result
        c._last_optimization = dt_util.now()
        boost.adopt_plan(c, _action(c, result))

    async def _cycle_writes(self):
        """The cycle's write tail in production order (``_async_update_data``)."""
        c = self.coord
        ctx = c._ctx
        boost.apply(c, boost.BoostOverlay(
            max_power=float(c._thermal_model.params.max_electrical_power),
            max_temp=float(ctx._opt_config.max_temp), ecl_max=float(c._ecl110_displace_max)))
        await c._apply_action()
        await c._command_frequency()
        await c._async_drive_pumps()

    def cycle(self, result=None, write_delay_s=0):
        """A solve cut at ``now``; its writes land ``write_delay_s`` later (a slow tail).

        Production order (``_async_update_data``): the input read first (``_update_current_state``,
        which also drives the disinfection switch), the solve's adoption, the valve write the solve
        ends with, then the write tail."""
        self.run(self.coord._update_current_state())
        if result is not None:
            self.adopt(result)
            self.run(self.coord._command_valve_target())
        if write_delay_s:
            self.at(self.now + timedelta(seconds=write_delay_s))
        self.run(self._cycle_writes())

    def tick(self):
        """The two one-minute intervals production arms: the arbiter's and the supply's."""
        c = self.coord
        self.run(pump_arbiter.apply(c, dt_util.now()))
        held = pump_arbiter.state_for(c)
        if held.supply is not None:
            wiring = pump_arbiter.SupplyWiring(c.arbiter_inputs, boost.held_for(c), c._write_supply)
            self.run(pump_arbiter.supply_tick(held, wiring, dt_util.now()))

    def value(self, key):
        st = self.hass.states.get(ENT[key])
        return None if st is None else st.state

    def mqtt_payload(self):
        sent = [d for (_t, dom, _s, d) in self.dev.log if dom == "mqtt" and d.get("topic") == TOPIC]
        return None if not sent else sent[-1]["payload"]


def _action(coord, result):
    """``solve_optimizer.get_current_action(result, now)``, the solve's own cut of the action."""
    from heatpump_optimizer.optimizer import HeatPumpOptimizer
    from heatpump_optimizer.thermal_model import ThermalModel
    ctx = coord._ctx
    opt = HeatPumpOptimizer(ThermalModel(ctx._thermal_params), ctx._opt_config)
    return opt.get_current_action(result, dt_util.now())


# ---------------------------------------------------------------------------
# Site attribution: which enumerator line a service call or a log_held came from
# ---------------------------------------------------------------------------
import ast as _ast  # noqa: E402
import subprocess as _sp  # noqa: E402
import sys as _sys  # noqa: E402
from collections import Counter as _Counter  # noqa: E402

PKG_DIR = os.path.join(_ROOT, "custom_components", "heatpump_optimizer")


def enumerator_cells():
    """``python3 tools/audit/enumerate.py d16-writes --cells``, run from the export root."""
    out = _sp.run([_sys.executable, "-I", os.path.join(_ROOT, "tools/audit/enumerate.py"), "d16-writes", "--cells",
                   "--repo", _ROOT], capture_output=True, text=True, check=True).stdout
    return [l for l in out.splitlines() if l.strip()]


def site_lines():
    """{(file basename, line): site text} for every enumerator site."""
    sites = {}
    for cell in enumerator_cells():
        site = cell.split(" | ")[0]
        loc = site.split()[1]
        f, ln = loc.rsplit(":", 1)
        sites[(os.path.basename(f), int(ln))] = site
    return sites


class Attribution:
    """Counts each service call and each log_held by the enumerator site it came from."""

    MODULES = ("coordinator", "heat_curve", "inputs", "off_restore", "pump_arbiter", "disinfection",
               "early_cutoff", "boost", "legionella", "supply_hold")

    def __init__(self):
        self.sites = site_lines()
        self.calls = _Counter()
        self.holds = _Counter()
        self.holds_active = _Counter()
        self.unmatched = _Counter()
        self._patched = []

    def _site_of(self, frame):
        f = frame
        while f is not None:
            fn = f.f_code.co_filename
            if fn.startswith(PKG_DIR):
                base = os.path.basename(fn)
                ln = f.f_lineno
                for d in range(0, 4):
                    if (base, ln - d) in self.sites:
                        return self.sites[(base, ln - d)]
                return f"unmatched {base}:{ln}"
            f = f.f_back
        return None

    def install(self, hass):
        import importlib
        orig = hass.services.async_call
        att = self

        async def async_call(domain, service, data=None, **kw):
            site = att._site_of(_sys._getframe(1))
            if site:
                (att.unmatched if site.startswith("unmatched") else att.calls)[site] += 1
            return await orig(domain, service, data, **kw)

        hass.services.async_call = async_call
        for name in self.MODULES:
            mod = importlib.import_module(f"heatpump_optimizer.{name}")
            if getattr(mod, "log_held", None) is None or (mod, "log_held") in self._patched:
                continue
            real = mod.log_held

            def wrapped(*a, _real=real, **k):
                site = att._site_of(_sys._getframe(1))
                active = a[2] if len(a) > 2 else k.get("active")
                if site:
                    (att.unmatched if site.startswith("unmatched") else att.holds)[site] += 1
                    if active:
                        att.holds_active[site] += 1
                return _real(*a, **k)

            mod.log_held = wrapped
            self._patched.append((mod, "log_held", real))
        return self

    def uninstall(self):
        for mod, name, real in self._patched:
            setattr(mod, name, real)
        self._patched = []
