#!/usr/bin/env python3
"""R10-DRAW-MAP-EVIDENCE part B: the power-response sweep, measured on synthetic plants.

    PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/draw_map_sweep.py [ARM ...]

Three arms (all by default), each printing ``RESULT`` lines. Synthetic inputs
only. An arm whose symbols the tree lacks prints ``absent``.

``comfort`` (design figure P8, review note r12). The 60 building presets
(``presets.STRUCTURES`` x ``ERAS`` x ``FOUNDATIONS``, 140 m2, one zone) on a
1.0-4.0 kW band at COP 3.0, baseline 21 degC, at -5 and +10 degC outdoor: how
many admit 5, 4, 3 and 2 levels of half an hour inside 0.8 K, with every
level at the band top as the upper bound and three lower bounds: each level
at its ``commanded`` kW; ``stop``, each level at its commanded kW for its
first quarter hour and none after (a set-point the inlet reaches stops the
compressor); ``zero``, no heat at all. Then ``production``: the same counts
from ``sysid.sweep_level_count``. Null: ``relax=0`` drops the relax phase,
and every count rises.

``yield`` (design figure P9). Five levels in the sweep's order, 30 minutes
each, one arbiter pass a minute through the production ``_arbitrate`` on a
flow set-point install whose inlet starts at 32, 37 or 42 degC and drifts up
0 to 0.2 K/min whatever the pump does, the entity stepping 0.5 or 1 K. Per
drift, over the six cases: the most distinct set-points one level wrote, and
per case how many levels kept at least 10 minutes running (the set-point
above the inlet). Each twice: the action naming the sweep kind, and
(``remap``, the null) the same action naming no kind, which every tree maps
on the inlet of each pass.

``night``. One sweep night through the production experiment (armed as the
sweep's button arms it), the arbiter and ``draw_range.fold`` on a pump whose
draw is 0.4 kW + 0.25 kW/K of lift, capped at a 3.2 kW top under a configured
4.0 kW: the levels held, the yield report, the published cost bound against
the metered energy and the meter's own integral, where the draws went
(window, idle, ceiling store and its sources), the band-top sample beside
its row's steady mean (r17), and compressor starts against the same night
under the plan at one level (r2).
"""
from __future__ import annotations

import asyncio
import itertools
import sys
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace as NS

from harness import FakeEntry, FakeHass, FakeState
from heatpump_optimizer import draw_range as dr
from heatpump_optimizer import presets
from heatpump_optimizer import pump_arbiter as pa
from heatpump_optimizer import sysid
from heatpump_optimizer.entry_config import EntryConfig
from heatpump_optimizer.thermal_model import ThermalParameters

FRACTIONS = (0.0, 0.5, 0.25, 1.0, 0.75)
LOW_KW, HIGH_KW, COP, BASE_C, BOUND_K = 1.0, 4.0, 3.0, 21.0, 0.8
T0 = datetime(2026, 1, 12, 23, 0, tzinfo=timezone.utc)
SET, INLET, POWER = "number.water_set", "sensor.return", "sensor.power"
#: The synthetic pump: kW at zero lift, kW per K of lift, and its real top.
OFFSET_KW, GAIN_KW_PER_K, TOP_KW = 0.4, 0.25, 3.2


def _houses():
    gains = ThermalParameters().internal_gains
    for s, e, f in itertools.product(presets.STRUCTURES, presets.ERAS, presets.FOUNDATIONS):
        d = presets.derive(presets.BuildingPreset(structure=s, era=e, foundation=f))
        yield sysid.HousePlant(ua=d["house_heat_loss_coefficient"], capacity=d["house_thermal_mass"],
                               gains=gains, slab_mass=d["slab_thermal_mass"],
                               slab_transfer=d["slab_heat_transfer"])


def _peak(house, outdoor, schedule):
    model = sysid._sizing_model(house.ua, house.capacity, house.gains, house.slab_mass, house.slab_transfer)
    state, peak = sysid._held_state(model, BASE_C, outdoor), 0.0
    for q, remaining in schedule:
        while remaining > 1e-12:
            dt = min(0.25, remaining)
            state = sysid._valve_drive(model, state, q, outdoor, dt)
            peak = max(peak, abs(state.upper_floor_temperature - BASE_C))
            remaining -= dt
    return peak


def _lower(kind, k):
    kws = [(LOW_KW + f * (HIGH_KW - LOW_KW)) * COP for f in FRACTIONS[:k]]
    if kind == "commanded":
        return [(q, 0.5) for q in kws]
    if kind == "stop":
        return [pair for q in kws for pair in ((q, 0.25), (0.0, 0.25))]
    return [(0.0, 0.5)] * k


def comfort_arm() -> None:
    for relax in (2.0, 0.0):
        for outdoor in (-5.0, 10.0):
            for kind in ("commanded", "stop", "zero"):
                fits = {k: 0 for k in (5, 4, 3, 2)}
                for house in _houses():
                    for k in (5, 4, 3, 2):
                        upper = [(HIGH_KW * COP, 0.5)] * k + [(0.0, relax)]
                        if max(_peak(house, outdoor, upper),
                               _peak(house, outdoor, _lower(kind, k) + [(0.0, relax)])) <= BOUND_K:
                            for j in fits:
                                fits[j] += j <= k
                            break
                print(f"RESULT comfort relax={relax:.0f} outdoor={outdoor:+.0f} lower={kind} "
                      + " ".join(f"k{k}={n}/60" for k, n in fits.items()))
    if not hasattr(sysid, "sweep_level_count"):
        print("RESULT comfort production absent")
        return
    for outdoor in (-5.0, 10.0):
        fits = {k: 0 for k in (5, 4, 3, 2)}
        for house in _houses():
            k = sysid.sweep_level_count(house, None, BASE_C, outdoor, HIGH_KW * COP,
                                        sysid.SysIdConfig(), len(FRACTIONS))
            for j in fits:
                fits[j] += k is not None and j <= k
        print(f"RESULT comfort production outdoor={outdoor:+.0f} "
              + " ".join(f"k{k}={n}/60" for k, n in fits.items()))


class _Flow:
    """The arbiter's coordinator surface: a flow set-point install with a
    return sensor and a power meter, band 1.0-4.0 kW, ceiling 55 degC."""

    def __init__(self, inlet_c, step=0.5):
        self.hass = FakeHass({
            SET: FakeState("35", attributes={"min": 25, "max": 63, "step": step}),
            INLET: FakeState(f"{inlet_c:.2f}", unit="°C"),
        })
        self._config = EntryConfig.from_mapping({
            "pump_duty_mode": "control", "space_setpoint_entity": SET, "space_setpoint_unit": "flow",
            "heat_pump_return_temp_entity": INLET, "heat_pump_power_entity": POWER,
        })
        self.action = {"mode": "eco", "power": 2.0}
        self.params = NS(dhw_setpoint=48.0, dhw_max_temp=48.0, min_electrical_power=LOW_KW,
                         max_electrical_power=HIGH_KW)
        self.plan = NS(timestamps=[T0 + timedelta(minutes=15 * i) for i in range(48)],
                       power_schedule=[2.0] * 48, dhw_power_schedule=[0.0] * 48,
                       optimal_setpoints=[21.0] * 48)
        self.entry = FakeEntry(entry_id=f"dms{id(self)}")
        self.draw = dr.DrawRange()
        self.power = None

    def _plan_is_stale(self):
        return False

    def arbiter_inputs(self):
        kw = dict(
            hass=self.hass, config=self._config, mode="auto", plan=self.plan, plan_stale=False,
            entry_released=False, state=NS(outdoor_temperature=2.0, room_temperature=21.0),
            thermal=NS(params=self.params, curve_flow_temp=lambda _o: 34.2), params=self.params,
            action=self.action, measured_power_kw=self.power, disinfecting=False,
        )
        if "draw" in pa.ArbiterInputs.__dataclass_fields__:
            kw["draw"] = self.draw
        return pa.ArbiterInputs(**kw)


class _Pump:
    """The synthetic pump behind ``_Flow``: it runs while the register sits
    above the inlet, drawing ``OFFSET_KW + GAIN_KW_PER_K x lift`` up to
    ``TOP_KW``; the inlet starts at ``inlet_c`` and rises ``drift`` K a minute."""

    def __init__(self, coord, inlet_c, drift):
        self.coord, self.inlet, self.drift = coord, inlet_c, drift
        self.held = pa.state_for(coord)
        self.held.loaded = True
        self.register, self.seen, self.starts, self.running = 35.0, 0, 0, False
        self.kwh = 0.0

    def kw(self):
        lift = self.register - self.inlet
        return min(OFFSET_KW + GAIN_KW_PER_K * lift, TOP_KW) if lift > 0.0 else 0.05

    def minute(self, now):
        """One arbiter pass at ``now``, then a minute of plant; the write sent, if any."""
        c = self.coord
        c.power = round(self.kw(), 3)
        c.hass.states.get(INLET).state = f"{self.inlet:.2f}"
        asyncio.run(pa._arbitrate(c, self.held, c.arbiter_inputs(), "control", now))
        sent = [float(d["value"]) for _dom, _s, d in c.hass.services.calls[self.seen:]
                if (d or {}).get("entity_id") == SET]
        self.seen = len(c.hass.services.calls)
        if sent:
            self.register = sent[-1]
            c.hass.states.get(SET).state = f"{self.register}"
        runs = self.register > self.inlet
        self.starts += runs and not self.running
        self.running = runs
        self.kwh += self.kw() / 60.0
        self.inlet += self.drift
        return self.register


def _yield_case(inlet_c, drift, step, kind):
    coord = _Flow(inlet_c, step)
    pump = _Pump(coord, inlet_c, drift)
    per_level, kept = [], 0
    for i, f in enumerate(FRACTIONS):
        coord.action = {"mode": "system_identification", "power": LOW_KW + f * (HIGH_KW - LOW_KW), **kind}
        registers, ran = set(), 0
        for m in range(30):
            registers.add(pump.minute(T0 + timedelta(minutes=30 * i + m)))
            ran += pump.running
        per_level.append(len(registers))
        kept += ran >= 10
    return per_level, kept


def yield_arm() -> None:
    for label, kind in (("sweep", {"kind": "power_sweep"}), ("remap", {})):
        for drift in (0.0, 0.05, 0.1, 0.2):
            cases = [_yield_case(inlet_c, drift, step, kind)
                     for inlet_c, step in itertools.product((32.0, 37.0, 42.0), (0.5, 1.0))]
            print(f"RESULT yield {label} drift={drift} cases={len(cases)} "
                  f"most_setpoints_in_a_level={max(max(p) for p, _ in cases)} "
                  f"levels_10min={sorted(k for _, k in cases)}")


def _night(sweep: bool):
    """One night on the synthetic pump: the experiment's steps and folds as
    the coordinator pairs them (an interval's own mode, split and command,
    folded a cycle later). ``sweep`` False runs the plan at 2.0 kW."""
    coord = _Flow(30.0)
    pump = _Pump(coord, 30.0, 0.02)
    s = sysid.SystemIdentification(sysid.SysIdConfig(enabled=True))
    house = sysid.HousePlant(ua=0.35, capacity=12.0, gains=0.3)
    if sweep:
        levels = tuple((dr.sweep_rows_at(coord.draw, kw), kw) for kw in sysid.sweep_levels_kw(LOW_KW, HIGH_KW))
        assert s.arm(T0, learner_samples=482, probe=coord.draw, sweep=levels), s.result.reason
    armed = s.result.reason
    pending, meter, ceiling_rows = None, 0.0, []
    for k in range(10):
        now = T0 + timedelta(minutes=30 * k)
        if pending is not None:
            before = len(coord.draw.ceiling)
            dr.fold(coord.draw, round(pump.kw(), 3), (pending["kw"], 0.0), coord.params, frozen=False,
                    distorted=False, defrost=False, command=pending["cmd"],
                    experiment_s=pending["when"] if pending["sid"] else None)
            if len(coord.draw.ceiling) > before:
                ceiling_rows.append((round(pump.kw(), 3), pending["when"]))
        override = s.step(now, 21.0, 2.0, 0.5, [0.5] * 96, 482, HIGH_KW, cop=COP, plan_power_kw=2.0,
                          house=house, sweep_band_k=pa.sweep_band_k(coord)) if sweep else None
        coord.action = ({"mode": "eco", "power": 2.0} if override is None else
                        {"mode": "system_identification", "kind": s.kind, "power": override})
        in_run = override is not None
        for m in range(30):
            kwh = pump.kwh
            pump.minute(now + timedelta(minutes=m))
            meter += (pump.kwh - kwh) if in_run else 0.0
        pending = {"sid": in_run, "kw": 2.0 if override is None else override, "when": now.timestamp(),
                   "cmd": pa._flow_command(coord.arbiter_inputs(), pump.held)}
    return NS(coord=coord, pump=pump, sysid=s, armed=armed, meter=meter, ceiling_rows=ceiling_rows)


def night_arm() -> None:
    if not hasattr(sysid, "KIND_SWEEP"):
        print("RESULT night absent")
        return
    n, plan = _night(True), _night(False)
    d, y = n.coord.draw, dr.sweep_yield(n.coord.draw)
    print("RESULT night armed:", n.armed)
    print("RESULT night outcome:", n.sysid.result.reason)
    for lv in y["levels"]:
        print(f"RESULT night level fraction={lv['fraction']} held_c={lv['held_c']} "
              f"steady_min={lv['steady_minutes']} drawn_mean_kw={lv['drawn_mean_kw']} "
              f"inlet_mean_c={lv['inlet_mean_c']}")
    bound = len(y["levels"]) * 0.5 * HIGH_KW
    print(f"RESULT night cost bound_kwh={bound:.1f} metered_kwh={y['metered_kwh']} "
          f"meter_integral_kwh={n.meter:.3f}")
    sources = [c[2] for c in d.ceiling]
    print(f"RESULT night routing window={len(d.samples)} idle={len(d.idle)} ceiling={len(d.ceiling)} "
          f"sources={sorted(set(sources))} probe_since={d.probe_since()} "
          f"plan_night_window={len(plan.coord.draw.samples)}")
    top = [r for r in d.map.rows if r[15] == "sweep" and r[6] == HIGH_KW]
    print(f"RESULT night r17 ceiling_sample_kw={[kw for kw, _ in n.ceiling_rows]} "
          f"row_drawn_mean_kw={[r[13] for r in top]} (the store takes the interval's closing meter reading)")
    print(f"RESULT night starts sweep={n.pump.starts} plan_at_one_level={plan.pump.starts}")
    print(f"RESULT night held_floor_after={n.pump.held.sweep_floor_c}")


ARMS = {"comfort": comfort_arm, "yield": yield_arm, "night": night_arm}

if __name__ == "__main__":
    for name in sys.argv[1:] or ARMS:
        ARMS[name]()
