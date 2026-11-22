"""R11-OWNER-MODE-LEGS (#3859): mode legs served by the arbiter over invented days.

    PYTHONPATH=tests/hastub:custom_components:tests \\
        python3 dev/audit/harnesses/mode_legs.py --synthetic --seed S [--hours H] [--heat N] [--dhw M]

No finder harness exists (owner report); this one is the design's
(design/R11-OWNER-MODE-LEGS 0e59437a, "Harness"). Synthetic only: no bundle is
read, and the ``--history`` mode the design names for the owner's bundle is
not built here, the bundle being private and its output never pushed.

A plan of 15-minute steps is drawn from the seed: heating on most steps, hot
water in blocks, and both steps whose hot-water share is a whole number of
minutes, so a pass each minute meets every planned leg end exactly. Every 30
minutes a re-solve, at a second offset the seed draws (never on a step
boundary), redraws the hot water of the step being served and the next one;
its pass runs at that second, the cycle's, and ``duty_switch.planner_fields``
reads the leg the pump is in, as a solve does. ``pump_arbiter.apply`` runs at
every minute and every re-solve second, and the pump echoes each mode write.

Printed, one ``RESULT`` line each:

* ``h2d_per_hour``: Heating to DHW mode writes per hour.
* ``legs_under_10_<cause>``: closed mode legs under 10 minutes, by cause:
  ``resolve`` (the leg starts or ends at a re-solve second), ``plan`` (both
  ends on a whole minute, as planned legs do here), ``other``.
* ``lease_expiries``: writes of Heating + DHW, the baseline row a hot-water
  lease expiry falls back to (the only baseline here: no boost, no block).
* ``space_priced_minus_delivered_kwh``: heating the plans in force price, at
  the step's combined level for the heating minutes ``duty_legs.plan_legs``
  gives under the run's rule (a both step's legs as the arbiter latched them
  at its first pass), less the heating minutes the pump served at that level:
  what the execution checks moved after the plan priced it.
* ``tank_unpriced_kwh``: hot-water minutes served beyond the plans' own split
  with no minimum (``--heat 0 --dhw 0``), at the step's level.

On a tree without the minimum legs (the merge base) only the counts print:
they are the null's reference. Null control: ``--heat 0 --dhw 0`` turns
both checks off; its counts must equal the merge base's, its
``legs_under_10_resolve`` must be above 0 (the generator reaches the case) and
both kWh figures must read 0.
"""
from __future__ import annotations

import argparse
import asyncio
import random
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from harness import FakeEntry, FakeHass, FakeState
from homeassistant.util import dt as dt_util

from heatpump_optimizer import duty_legs, duty_switch, pump_arbiter, pump_mode, running_signal
from heatpump_optimizer.entry_config import EntryConfig

T0 = datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc)
OPTIONS = ("Heating", "DHW (Hot Water)", "Heating + DHW")
STEP_S = 900
#: The tree has the minimum legs. On the merge base the counts still print, the kWh figures do not.
BUILT = hasattr(duty_legs, "plan_legs")


class Pump:
    """The arbiter's coordinator surface: a mode select, a running signal, a plan."""

    def __init__(self, heat: float, dhw: float, plan: SimpleNamespace) -> None:
        self.hass = FakeHass({
            "select.pump_mode": FakeState("Heating + DHW", attributes={"options": list(OPTIONS)}),
            "sensor.freq": FakeState("40"),
        })
        self._config = {"pump_duty_mode": "control", "heat_pump_mode_entity": "select.pump_mode",
                        "compressor_freq_sensor": "sensor.freq",
                        "mode_leg_heat_min_minutes": heat, "mode_leg_dhw_min_minutes": dhw}
        self.plan = plan
        self.params = SimpleNamespace(dhw_setpoint=48.0, dhw_max_temp=60.0, dhw_cycle_temp=None,
                                      min_electrical_power=1.0, max_electrical_power=5.0)
        self.entry = FakeEntry(entry_id=f"ml{id(self)}")
        self.attached = False

    def arbiter_inputs(self) -> pump_arbiter.ArbiterInputs:
        if not self.attached:
            running_signal.attach(running_signal.signal_for(self), *running_signal.source(
                self.hass, EntryConfig.from_mapping(self._config), lambda: self.params, lambda kw: False))
            self.attached = True
        return pump_arbiter.ArbiterInputs(
            hass=self.hass, config=self._config, mode="auto", plan=self.plan, plan_stale=False,
            entry_released=False, state=SimpleNamespace(outdoor_temperature=2.0, room_temperature=20.0,
                                                        dhw_temperature=45.0),
            thermal=SimpleNamespace(params=self.params), params=self.params, action={"heat_pump_on": True},
            measured_power_kw=None, disinfecting=False, defrosting=None)


def _step(rng: random.Random, dhw_block: bool) -> tuple[float, float]:
    """One step's (space kW, hot-water kW); a both step's hot-water share is whole minutes."""
    space = rng.uniform(0.8, 3.0) if rng.random() < 0.75 else 0.0
    if not dhw_block:
        return space, 0.0
    if space == 0.0 or rng.random() < 0.4:
        return 0.0, rng.uniform(1.0, 3.0)
    minutes = rng.randint(5, 10)
    return space, space * minutes / (15 - minutes)


def _plan(levels: list[tuple[float, float]]) -> SimpleNamespace:
    return SimpleNamespace(timestamps=[T0 + timedelta(seconds=STEP_S * i) for i in range(len(levels))],
                           power_schedule=[s for s, _d in levels], dhw_power_schedule=[d for _s, d in levels],
                           optimal_setpoints=[21.0] * len(levels))


def run(seed: int, hours: int, heat: float, dhw: float) -> dict[str, float]:
    """The seed's plan at 00:00, a re-solve every 30 minutes, driven through the arbiter."""
    rng = random.Random(seed)
    n = hours * 4
    levels = [_step(rng, rng.random() < 0.3) for _ in range(n)]
    plans = {0: _plan(levels)}
    for at in range(0, n * STEP_S - 2 * STEP_S, 1800):
        at += rng.randint(30, STEP_S - 30)
        levels = list(levels)
        for j in (at // STEP_S, at // STEP_S + 1):
            levels[j] = _step(rng, rng.random() < 0.5)
        plans[at] = _plan(levels)
    return _drive(Pump(heat, dhw, plans[0]), plans, n, heat, dhw)


def _drive(pump: Pump, plans: dict[int, SimpleNamespace], n: int, heat: float, dhw: float) -> dict[str, float]:
    writes: list[tuple[int, str]] = []
    served: list[tuple[int, str, SimpleNamespace, duty_legs.Legs, duty_legs.Legs]] = []
    latched: dict[datetime, SimpleNamespace] = {}
    rec = duty_switch.record_for(pump)
    rec.loaded = True
    cfg = EntryConfig.from_mapping(pump._config)
    rule = duty_legs.LegRule("dhw", None, heat, dhw) if BUILT else None

    async def go() -> None:
        for s in sorted(set(range(0, n * STEP_S, 60)) | set(plans)):
            now = T0 + timedelta(seconds=s)
            dt_util.freeze(now)
            if s in plans:
                pump.plan = plans[s]
                if BUILT:
                    duty_switch.planner_fields(pump, cfg)
            await pump_arbiter.apply(pump, now)
            mode = pump_arbiter.state_for(pump).written.get("mode")
            if mode and (not writes or writes[-1][1] != mode[0]):
                writes.append((s, mode[0]))
                pump.hass.states.set("select.pump_mode", FakeState(
                    next(o for o in OPTIONS if pump_mode.resolve(o) == mode[0]), attributes={"options": list(OPTIONS)}))
            if not BUILT:
                served.append((s, writes[-1][1] if writes else "", pump.plan, (), ()))
                continue
            i, plan = s // STEP_S, pump.plan
            if pump_arbiter.step_duty(plan, now) == "both" and rec.order is not None \
                    and rec.order[0] == plan.timestamps[i]:
                plan = latched.setdefault(rec.order[0], plan)  # the plan the both step's legs were latched on
            legs = duty_legs.plan_legs(plan.power_schedule, plan.dhw_power_schedule, rule=rule)[i]
            bare = duty_legs.plan_legs(plan.power_schedule, plan.dhw_power_schedule)[i]
            served.append((s, writes[-1][1] if writes else "", plan, legs, bare))
    try:
        asyncio.run(go())
    finally:
        dt_util.freeze(None)
    return _figures(writes, served, set(plans) - {0}, n)


def _figures(writes: list[tuple[int, str]],
             served: list[tuple[int, str, SimpleNamespace, duty_legs.Legs, duty_legs.Legs]],
             resolve_s: set[int], n: int) -> dict[str, float]:
    out: dict[str, float] = {"h2d_per_hour": 0.0, "legs_under_10_resolve": 0, "legs_under_10_plan": 0,
                             "legs_under_10_other": 0, "lease_expiries": 0}
    for (s0, m0), (s1, m1) in zip(writes, writes[1:]):
        out["h2d_per_hour"] += (m0, m1) == (pump_mode.MODE_HEAT, pump_mode.MODE_DHW)
        out["lease_expiries"] += m1 == pump_mode.MODE_HEAT_DHW
        if s1 - s0 < 600:
            cause = "resolve" if s0 in resolve_s or s1 in resolve_s else "plan" if s0 % 60 == s1 % 60 == 0 else "other"
            out[f"legs_under_10_{cause}"] += 1
    out["h2d_per_hour"] /= n / 4
    if not BUILT:
        return out
    priced = delivered = unpriced = 0.0
    for (s, mode, plan, legs, bare), nxt in zip(served, [*served[1:], (n * STEP_S, "", None, (), ())]):
        i = s // STEP_S
        level = plan.power_schedule[i] + plan.dhw_power_schedule[i]
        span_min = (nxt[0] - s) / 60.0
        minute = (s % STEP_S) / 60.0
        priced += level * span_min / 60.0 * (_at(legs, minute) == "space")
        delivered += level * span_min / 60.0 * (mode == pump_mode.MODE_HEAT)
        unpriced += level * span_min / 60.0 * (mode == pump_mode.MODE_DHW and _at(bare, minute) != "dhw"
                                               and plan.dhw_power_schedule[i] > 0)
    out["space_priced_minus_delivered_kwh"] = round(priced - delivered, 3)
    out["tank_unpriced_kwh"] = round(unpriced, 3)
    return out


def _at(legs: duty_legs.Legs, minute: float) -> str:
    """The leg served at ``minute`` into its step, compared as the arbiter compares (``timedelta``)."""
    return legs[0][0] if timedelta(minutes=minute) < timedelta(minutes=legs[0][1]) else legs[-1][0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", action="store_true", required=True)
    ap.add_argument("--seed", type=int, default=3859)
    ap.add_argument("--hours", type=int, default=48)
    ap.add_argument("--heat", type=float, default=10.0)
    ap.add_argument("--dhw", type=float, default=10.0)
    args = ap.parse_args()
    for key, value in run(args.seed, args.hours, args.heat, args.dhw).items():
        print(f"RESULT {key}={value}")


if __name__ == "__main__":
    main()
