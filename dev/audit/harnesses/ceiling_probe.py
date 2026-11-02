"""R10-CEILING-PROBE harness: does the experiment's step reach a flow set-point
install, and can its draws teach the band top?

Four arms. The first two are the finder's harnesses (``probe_duty.py`` sha1
0d3fbd4541c8a1b7aa0a4ed6304ba55c1828dff5, ``probe_draw.py`` sha1
f4a4344c30aadf764929ec473d1ada2b11eb1e5f, carried on #2498), ported verbatim
in what they print. The other two are their companions, applying the tree's
own rule to the same inputs: the finder's duty arm reads ``_planned_duty``
and a code-object name, and its draw arm drives ``DrawRange.observe``
directly, which the fix rightly leaves alone, so both read flat at a head
that routes the experiment elsewhere.

  duty      the duty the arbiter serves while the experiment overrides the
            action (5.0 kW), against a plan action of 5.0 kW
  draw      what one probe run adds to the window's top, against 48 ceiling
            samples in the window
  level     the flow set-point one arbitration pass writes for an experiment
            action at 5.0, 1.5 and 0.0 kW on a 1-5 kW band (FLOW_HEAT_C 55)
  store     three default probe nights of a synthetic pump with a 3.0 kW
            maximum behind a configured 5.0 kW, through the production fold;
            the learned top and where the probe draws went

Synthetic inputs only. Run from a worktree root (any tree; an arm whose
symbols the tree lacks prints ``absent``):
  PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/ceiling_probe.py
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace as NS

from harness import FakeHass, FakeState
from heatpump_optimizer import draw_range as dr
from heatpump_optimizer import pump_arbiter as pa
from heatpump_optimizer import sysid
from heatpump_optimizer.entry_config import EntryConfig

NOW = datetime(2026, 10, 27, 1, 0, tzinfo=timezone.utc)


def duty_arm() -> None:
    plan = NS(timestamps=[NOW], power_schedule=[0.0], dhw_power_schedule=[0.0], optimal_setpoints=[20.0])

    def inp(action):
        return pa.ArbiterInputs(hass=None, config={}, mode="auto", plan=plan, plan_stale=False,
                                entry_released=False, state=None, thermal=None, params=None, action=action,
                                measured_power_kw=None, disinfecting=False)

    class C:
        pass

    coord = C()
    for label, action in (("sysid step 5.0 kW", {"mode": "system_identification", "power": 5.0}),
                          ("null: plan action  5.0 kW", {"mode": "auto", "power": 5.0})):
        print("duty:", label, "-> duty", repr(pa._planned_duty(coord, inp(action), NOW)),
              "| plan step_duty", repr(pa.step_duty(plan, NOW)))
    print("duty: flow target, duty None reads the plan/curve hold; duty 'space' reads plan power_schedule:",
          "sysid power is not an input to _flow_target:", "action" not in pa._flow_target.__code__.co_names
          and "action" not in pa._step_kw.__code__.co_names)


def draw_arm() -> None:
    cfg = sysid.SysIdConfig()
    interval_h = 30 / 60  # DEFAULT_OPTIMIZATION_INTERVAL
    per_run = int(cfg.step_hours / interval_h)

    def run(n_ceiling):
        d = dr.DrawRange()
        for _ in range(dr.WINDOW - n_ceiling):  # set-point install: sub-ceiling commands
            d.observe(1.5, 2.0, 1.0, 5.0, (35.0, 55.0))
        for _ in range(n_ceiling):  # probe: ceiling written, pump draws 3 kW
            d.observe(3.0, 5.0, 1.0, 5.0, (55.0, 55.0))
        return d.observed(), d.engaged, d.planned(1.0, 5.0)

    print("draw: samples per probe run", per_run, "| runs per", cfg.min_days_between_runs,
          "days: 1 | MIN_SAMPLES", dr.MIN_SAMPLES)
    print("draw: one probe   :", run(per_run))
    print("draw: null 48 ceil:", run(dr.MIN_SAMPLES))


class _Flow:
    """The arbiter's coordinator surface on a flow set-point install, band 1-5 kW."""

    def __init__(self, action):
        self.hass = FakeHass({
            "select.pump_mode": FakeState("Heating + DHW", attributes={
                "options": ["Heating", "DHW (Hot Water)", "Heating + DHW"]}),
            "number.dhw_set": FakeState("53", attributes={"min": 40, "max": 63}),
            "number.water_set": FakeState("53", attributes={"min": 25, "max": 63}),
        })
        self._config = EntryConfig.from_mapping({
            "pump_duty_mode": "control", "heat_pump_mode_entity": "select.pump_mode",
            "dhw_setpoint_entity": "number.dhw_set", "space_setpoint_entity": "number.water_set",
            "space_setpoint_unit": "flow",
        })
        self.action = action
        self.params = NS(dhw_setpoint=48.0, min_electrical_power=1.0, max_electrical_power=5.0)
        self.entry = NS(entry_id=f"cph{id(self)}")
        self._plan = NS(timestamps=[NOW], power_schedule=[5.0], dhw_power_schedule=[0.0],
                        optimal_setpoints=[21.0])

    def _plan_is_stale(self):
        return False

    @property
    def effective_config(self):
        return self._config

    @property
    def thermal_params(self):
        return self.params

    def arbiter_inputs(self):
        return pa.ArbiterInputs(
            hass=self.hass, config=self._config, mode="auto", plan=self._plan, plan_stale=False,
            entry_released=False, state=NS(outdoor_temperature=2.0, room_temperature=21.0),
            thermal=NS(params=self.params, curve_flow_temp=lambda _o: 34.2), params=self.params,
            action=self.action, measured_power_kw=None, disinfecting=False,
        )


def level_arm() -> None:
    for kw in (5.0, 1.5, 0.0):
        c = _Flow({"mode": "system_identification", "power": kw, "dhw_power": 0.0})
        asyncio.run(pa.apply(c, NOW + timedelta(minutes=1)))
        flow = [d.get("value") for dom, _s, d in c.hass.services.calls
                if dom == "number" and (d or {}).get("entity_id") == "number.water_set"]
        print(f"level: experiment {kw:.1f} kW (plan step 5.0 kW) -> flow written",
              flow[-1] if flow else None)


def store_arm() -> None:
    if not hasattr(dr.DrawRange, "learned_max_kw"):
        print("store: absent (no ceiling store in this tree)")
        return
    store = dr.DrawRange()
    ceil = NS(written_c=55.0, gate_c=25.0, ceiling_c=55.0)
    mid = NS(written_c=40.0, gate_c=25.0, ceiling_c=55.0)
    params = NS(min_electrical_power=1.0, max_electrical_power=5.0)
    house = sysid.HousePlant(ua=0.35, capacity=12.0, gains=0.3)
    for night in range(3):
        start = datetime(2026, 1, 10, 23, 0, tzinfo=timezone.utc) + timedelta(days=8 * night)
        s = sysid.SystemIdentification(sysid.SysIdConfig(enabled=True))
        if not s.arm(start, learner_samples=482, probe=store):
            print("store: night", night, "refused:", s.result.reason)
            return
        pending = None
        for k in range(9):
            now = start + timedelta(minutes=30 * k)
            override = s.step(now, 21.0, 2.0, 0.5, [0.5 + 0.03 * i for i in range(48)], 482, 5.0,
                              cop=3.0, plan_power_kw=1.5, house=house)
            if pending is not None:
                dr.fold(store, 3.0 if pending["cmd"] is ceil else 1.5, (pending["kw"], 0.0), params,
                        frozen=False, distorted=False, defrost=False, command=pending["cmd"],
                        experiment_s=pending["when"] if pending["sid"] else None)
            kw = 1.5 if override is None else override
            pending = {"sid": override is not None, "kw": kw, "when": now.timestamp(),
                       "cmd": ceil if kw >= 5.0 else mid}
    top = store.learned_max_kw(store.ceiling_since() or 0.0)
    print("store: probe samples", len(store.ceiling), "| learned top", top,
          "| window samples at the ceiling", sum(1 for d, _a in store.samples if d > 2.5),
          "| engaged", store.engaged)


if __name__ == "__main__":
    duty_arm()
    draw_arm()
    level_arm()
    store_arm()
