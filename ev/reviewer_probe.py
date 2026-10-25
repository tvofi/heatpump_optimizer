#!/usr/bin/env python3
"""Fix-review probe for PR #2832 (reviewer-built, not the finder's or fixer's).

Closed loop with a different pump ceiling (58.5 C) and different ages/intervals
than the fixer's harness, plus unit-level guard probes. Run from a worktree root:
PYTHONPATH=tests/hastub:tests:custom_components python3 <this> [section ...]
"""
from __future__ import annotations
import asyncio, sys
from datetime import timedelta, timezone
sys.path[:0] = ["tests", "custom_components"]
import numpy as np
from golden import START, make
from harness import FakeHass
from homeassistant.util import dt as dt_util
from profiles import solve_inputs
from heatpump_optimizer.disinfection import DisinfectionSwitch
from heatpump_optimizer.legionella import LegionellaGuard
from heatpump_optimizer.payload import REASON_LEGIONELLA

T0 = START.replace(tzinfo=timezone.utc)


def guard_for(params, config, action, hass=None):
    hass = hass or FakeHass()
    g = LegionellaGuard(hass, "probe", params, config, action=lambda: action,
                        disinfect=DisinfectionSwitch({}, lambda *a, **k: None, lambda e: None),
                        dhw_blocked=lambda: False)
    async def _ns():
        return None
    g.async_save = _ns
    return g, hass


def issues(hass):
    return {i[1]: (i[2].get("translation_placeholders") or {}) for i in getattr(hass, "issues", [])}


def loop(tag, age_days, interval, ceiling, days, enabled=True, probe=True):
    built = make(config_overrides={"dhw_setpoint": 50.0} if enabled else {"dhw_setpoint": 50.0, "dhw_legionella_enabled": False})
    opt = built["optimizer"]; params = opt.model.params
    params.dhw_legionella_interval_days = interval
    cfg = {"dhw_temp_entity": "sensor.tank"} if probe else {}
    action = {"dhw_reason": "idle"}
    g, hass = guard_for(params, cfg, action)
    g.last_cycle = T0 - timedelta(days=age_days)
    tank = 47.0; n = len(built["prices"]); reasons = []; traj = np.zeros(1)
    first_cmd = None; cmd = 0; attempts = []; la = None; max_tank = tank; max_plan = -1e9
    sinces = []; ever = set()
    for i in range(days * 96):
        now = T0 + i * timedelta(minutes=15); dt_util.freeze(now)
        if i % 2 == 0:
            st = built["state"]; st.dhw_temperature = tank
            s = g.hours_since(); sinces.append(None if s is None else round(s, 3))
            st.dhw_hours_since_legionella = s
            sh = i % n
            res = opt.optimize(inputs=solve_inputs(initial_state=st,
                prices=np.roll(built["prices"], -sh), outdoor_temps=np.roll(built["outdoor"], -sh),
                wind_speeds=np.roll(built["wind"], -sh), precipitation=np.roll(built["rain"], -sh),
                solar_radiation=np.roll(built["solar"], -sh), start_time=START + i * timedelta(minutes=15)))
            reasons = list(res.dhw_reasons or []); traj = np.asarray(res.dhw_temp_trajectory, dtype=float)
            max_plan = max(max_plan, float(np.nanmax(traj)))
        k = i % 2
        action["dhw_reason"] = reasons[k] if k < len(reasons) else "idle"
        if action["dhw_reason"] == REASON_LEGIONELLA:
            cmd += 1; first_cmd = first_cmd if first_cmd is not None else i * 0.25
        asyncio.run(g.async_observe(tank if probe else None, None))
        if g.attempt is not None and g.attempt != la:
            attempts.append(round(i * 0.25, 2)); la = g.attempt
        ever |= set(issues(hass))
        d = float(traj[k + 1] - traj[k]) if k + 1 < traj.size else 0.0
        tank = min(ceiling, tank + d) if d > 0 else tank + d
        max_tank = max(max_tank, tank)
    standing = issues(hass); dt_util.freeze(None)
    top = float(params.dhw_max_temp)
    out = dict(commanded_steps=cmd, first_commanded_h=first_cmd, attempts=attempts,
               completed=(g.last_cycle > T0), max_tank=round(max_tank, 2), max_plan=round(max_plan, 2),
               dhw_max_temp=top, plan_exceeds_ceiling=max_plan > top + 1e-6,
               notices_ever=sorted(ever), notices_standing=standing,
               since_hash=hash(tuple(sinces)))
    for k2, v in out.items():
        print(f"RESULT loop:{tag} {k2} {v}")


async def units():
    from heatpump_optimizer.thermal_model import ThermalParameters
    def P(interval=7.0, enabled=True):
        p = ThermalParameters(); p.dhw_enabled = True; p.dhw_legionella_enabled = enabled
        p.dhw_legionella_interval_days = interval; return p
    base_now = T0
    # (2) below-target peak leaves cycle due; null reaches target
    for free in (False, True):
        for label, temp, steps in (("below", 58.9 if not free else 59.4, 12), ("reach", 60.0, 12),
                                   ("reach_short_hold", 60.0, 1)):
            p = P(); g, h = guard_for(p, {"dhw_temp_entity": "s", "dhw_free_disinfection_enabled": free}, {"dhw_reason": "idle"})
            g.last_cycle = base_now - timedelta(days=10); before = g.last_cycle
            for j in range(steps):
                dt_util.freeze(base_now + j * timedelta(minutes=15))
                await g.async_observe(temp, None)
            print(f"RESULT unit:peak free={free} {label} completed={g.last_cycle != before} hours_since={round(g.hours_since(),2)}")
    # sensor gap: None readings never credit
    p = P(); g, h = guard_for(p, {"dhw_temp_entity": "s"}, {"dhw_reason": REASON_LEGIONELLA})
    g.last_cycle = base_now - timedelta(days=10); before = g.last_cycle
    for j in range(8):
        dt_util.freeze(base_now + j * timedelta(minutes=15)); await g.async_observe(None, None)
    print(f"RESULT unit:sensor_gap completed={g.last_cycle != before}")
    # (3) overdue notice loud vs healthy, user interval respected
    for label, interval, age in (("overdue_7d", 7.0, 66), ("healthy_7d", 7.0, 2), ("user14_age10", 14.0, 10),
                                 ("user14_age15", 14.0, 15), ("edge_7d_exact", 7.0, 7)):
        p = P(interval); g, h = guard_for(p, {"dhw_temp_entity": "s"}, {"dhw_reason": "idle"})
        dt_util.freeze(base_now); g.last_cycle = base_now - timedelta(days=age)
        await g.async_observe(45.0, None)
        print(f"RESULT unit:notice {label} overdue={issues(h).get('dhw_legionella_overdue')}")
    # disabled: no notices, hours_since
    p = P(enabled=False); g, h = guard_for(p, {"dhw_temp_entity": "s"}, {"dhw_reason": REASON_LEGIONELLA})
    dt_util.freeze(base_now); g.last_cycle = base_now - timedelta(days=66)
    hs = await g.async_observe(45.0, None)
    print(f"RESULT unit:disabled issues={sorted(issues(h))} hours_since={hs} attempt={g.attempt}")
    # retry spacing with short user interval and with no probe
    for label, interval, cfg in (("probe_7d", 7.0, {"dhw_temp_entity": "s"}), ("probe_0.5d", 0.5, {"dhw_temp_entity": "s"}),
                                 ("noprobe_7d", 7.0, {})):
        p = P(interval); g, h = guard_for(p, cfg, {"dhw_reason": "idle"})
        g.last_cycle = base_now - timedelta(days=66); g.attempt = base_now
        vals = []
        for hrs in (0, 6, 12, 24, 48):
            dt_util.freeze(base_now + timedelta(hours=hrs)); vals.append((hrs, g.due_in_hours()))
        print(f"RESULT unit:retry {label} due_in={vals}")
    # cap: recent completion then attempt -> not due sooner than interval
    p = P(7.0); g, h = guard_for(p, {"dhw_temp_entity": "s"}, {"dhw_reason": "idle"})
    g.last_cycle = base_now - timedelta(days=2); g.attempt = base_now - timedelta(hours=1)
    dt_util.freeze(base_now); print(f"RESULT unit:cap recent_completion due_in={g.due_in_hours()}")
    dt_util.freeze(None)

if __name__ == "__main__":
    secs = sys.argv[1:] or ["units", "loop"]
    if "units" in secs:
        asyncio.run(units())
    if "loop" in secs:
        loop("overdue_short585", 66, 7.0, 58.5, 4)
        loop("null_notdue", 2, 7.0, 58.5, 2)
        loop("user14_overdue", 30, 14.0, 58.5, 3)
        loop("noprobe_overdue", 66, 7.0, 58.5, 3, probe=False)
        loop("disabled", 66, 7.0, 58.5, 2, enabled=False)
