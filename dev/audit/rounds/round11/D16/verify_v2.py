"""D16 round-11 verifier, lens V2: independent measurements, one per finding.

Written by the D16 verifier; imports no finder harness. Each block builds its
own rig (tests/harness FakeHass + the real coordinator on coord_all_features)
and prints ``V2 <finding> <metric>=<value>``.

Run (worktree root): PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D16/verify_v2.py [ids...]
"""
from __future__ import annotations

import ast
import asyncio
import os
import re
import sys
from datetime import datetime, timedelta, timezone

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
sys.path[:0] = ["tests", "custom_components"]

from harness import FakeEntry, FakeHass, FakeServices, FakeState  # noqa: E402
from golden import coordinator_scenarios  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import heatpump_optimizer.coordinator as coord_mod  # noqa: E402
from heatpump_optimizer import boost, off_restore, pump_arbiter  # noqa: E402
from heatpump_optimizer.freq_control import FrequencyMap  # noqa: E402
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig, OptimizationResult  # noqa: E402

PKG = "custom_components/heatpump_optimizer/"
T0 = datetime(2026, 2, 3, 10, 0, tzinfo=timezone.utc)
N = 8
TS = [T0 + timedelta(minutes=15 * i) for i in range(N)]


class Svc(FakeServices):
    """Device emulation: a delivered write becomes the state; an unavailable
    entity is skipped (Home Assistant's entity service call)."""

    def __init__(self, hass):
        super().__init__()
        self.h = hass
        self.log = []

    async def async_call(self, domain, service, data=None, **kw):
        data = dict(data or {})
        ent = data.get("entity_id")
        st = self.h.states.get(ent) if isinstance(ent, str) else None
        skip = st is not None and st.state == "unavailable"
        val = data.get("value", data.get("option", data.get("temperature")))
        self.log.append((dt_util.now(), domain, service, ent, val, skip))
        if st is not None and not skip:
            if service == "turn_on":
                st.state = "on"
            elif service == "turn_off":
                st.state = "off"
            elif service in ("set_value", "select_option", "set_temperature"):
                st.state = str(val)
        return await super().async_call(domain, service, data, **kw)


def rig(opts, unit="flow", tank=50.0, mode_state="Heating + DHW", extra_cfg=None):
    cfg = dict(coordinator_scenarios()["coord_all_features"])
    cfg.update(pump_duty_mode="control", heat_pump_mode_entity="select.m", dhw_setpoint_entity="number.t",
               space_setpoint_entity="number.s", space_setpoint_unit=unit, heat_pump_switch_entity="switch.p",
               dhw_setpoint=50.0, dhw_temp_entity="sensor.tank", dhw_hysteresis_entity="sensor.h",
               heat_pump_return_temp_entity="sensor.r")
    cfg.update(extra_cfg or {})
    sp = (FakeState("35", attributes={"min": 20, "max": 55, "step": 1}) if unit == "flow"
          else FakeState("20", attributes={"min": 5, "max": 30, "step": 0.5}))
    hass = FakeHass({
        "select.m": FakeState(mode_state, attributes={"options": opts}),
        "number.t": FakeState("50", attributes={"min": 10, "max": 70, "step": 1}),
        "number.s": sp, "switch.p": FakeState("on"),
        "sensor.tank": FakeState(str(tank), unit="°C"), "sensor.h": FakeState("5", unit="K"),
        "sensor.r": FakeState("27", unit="°C"),
        "number.f": FakeState("40", attributes={"min": 20, "max": 90, "step": 1}),
    })
    hass.services = Svc(hass)
    entry = FakeEntry(data=cfg, entry_id=f"v2_{id(cfg)}")
    c = coord_mod.HeatPumpOptimizerCoordinator(hass, entry)
    entry.runtime_data = c
    c._current_state.dhw_temperature = tank
    return c


def plan(space, dhw, setp=None):
    return OptimizationResult(
        power_schedule=list(space), room_temp_trajectory=[20.5] * N, slab_temp_trajectory=[21.0] * N,
        timestamps=list(TS), prices=[1.0] * N, predicted_cost=0, baseline_cost=0, predicted_savings=0,
        savings_percentage=0, optimal_setpoints=list(setp or [20.0 + 0.2 * i for i in range(N)]), status="ok",
        dhw_power_schedule=list(dhw), duty_floor_kw=1.0,
        heat_pump_on_schedule=[(a > 0 or b > 0) for a, b in zip(space, dhw)],
        displace_schedule=[3.0 if (a > 0 or b > 0) else -4.0 for a, b in zip(space, dhw)],
        valve_target_schedule=[22.0] * N, solve_band={"planned_min_kw": 1.0, "planned_max_kw": 5.0})


def adopt(c, res, t):
    dt_util.freeze(t)
    c._optimization_result = res
    c._last_optimization = t
    boost.adopt_plan(c, HeatPumpOptimizer(c._thermal_model, OptimizationConfig()).get_current_action(res, t))


def written(c, ent):
    return [x for x in c.hass.services.log if x[3] == ent]


# ---------------------------------------------------------------- s1-01
def s1_01():
    """Share of FrequencyMap.recommend answers off a 1 Hz grid, over entity ranges and targets."""
    ranges = [(20, 90), (30, 90), (20, 100), (30, 120), (15, 120), (25, 85), (20, 110), (30, 110)]
    off = tot = 0
    per = {}
    for lo, hi in ranges:
        fm = FrequencyMap()
        span = hi - lo
        for d in range(10):
            hz = lo + (d + 0.5) * span / 10
            for _ in range(8):
                fm.observe(hz, hz * 0.05, float(lo), float(hi))
        o = t = 0
        for kw in [0.6 + 0.1 * i for i in range(50)]:
            r = fm.recommend(kw, float(lo), float(hi))
            if r is None:
                continue
            t += 1
            o += abs(r - round(r)) > 1e-9
        per[f"{lo}-{hi}"] = f"{o}/{t}"
        off += o
        tot += t
    print("V2 s1-01 per_range", per)
    print(f"V2 s1-01 off_grid_share={off / tot:.3f} ({off}/{tot})")


# ---------------------------------------------------------------- s1-02
async def s1_02():
    """GCHV (no Heating option): tank set-point written on a space-only step, per tank reading."""
    res = plan([0, 1, 1, 1, 0, 0, 0, 0], [0] * N)
    charge = []
    for tank in (20.0, 24.0, 26.0, 35.0):
        for opts, name in ((["Off", "Cooling + DHW", "Heating + DHW"], "gchv"),
                           (["Heating", "DHW (Hot Water)", "Heating + DHW"], "fork")):
            c = rig(opts, tank=tank)
            t = TS[1] + timedelta(minutes=3)
            adopt(c, res, t)
            await pump_arbiter.apply(c, t)
            await pump_arbiter.apply(c, t + timedelta(minutes=1))
            sp = float(c.hass.states.get("number.t").state)
            mode = c.hass.states.get("select.m").state
            charges = ("DHW" in mode) and (sp - 5.0 > tank)
            charge.append((name, tank, mode, sp, charges))
    print("V2 s1-02 rows", charge)
    print("V2 s1-02 gchv_tank_readings_charging=%d/4 fork=%d/4" % (
        sum(r[4] for r in charge if r[0] == "gchv"), sum(r[4] for r in charge if r[0] == "fork")))


# ---------------------------------------------------------------- s1-03
async def s1_03():
    res = plan([0, 3, 3, 3, 0, 0, 0, 0], [0] * N)
    out = {}
    for unit in ("indoor", "flow"):
        for boosted in (False, True):
            c = rig(["Heating", "DHW (Hot Water)", "Heating + DHW"], unit=unit)
            t = TS[1] + timedelta(minutes=3)
            adopt(c, res, t)
            if boosted:
                boost.held_for(c).set(boost.CHANNEL_SPACE, True, t)
                boost.apply(c, boost.BoostOverlay(max_power=5.0, max_temp=float(c._opt_config.max_temp),
                                                  ecl_max=float(c._ecl110_displace_max)))
            await pump_arbiter.apply(c, t)
            out[(unit, boosted)] = (c.hass.states.get("number.s").state, float(c._opt_config.max_temp),
                                    res.optimal_setpoints[1])
    print("V2 s1-03 (unit,boost)->(space_state,max_temp,plan_sp)", out)
    s = out[("indoor", True)]
    print(f"V2 s1-03 indoor_boost_gap_K={s[1] - float(s[0]):.2f}")


# ---------------------------------------------------------------- s1-04
async def s1_04():
    """Stale plan whose last actuated step was idle: minutes the power switch reads off afterwards."""
    out = {}
    for last_on in (False, True):
        sp = [2, 2, 2, 2, 2, 2, 2, 2 if last_on else 0]
        res = plan(sp, [0] * N)
        c = rig(["Heating", "DHW (Hot Water)", "Heating + DHW"])
        tl = TS[N - 1] + timedelta(minutes=2)
        adopt(c, res, tl)
        await c._apply_action()
        await pump_arbiter.apply(c, tl)
        off_min = 0
        for m in range(1, 241):
            t = tl + timedelta(minutes=m)
            dt_util.freeze(t)
            if m % 30 == 0:
                await c._apply_action()  # a cycle whose solve failed: the plan only ages
            await pump_arbiter.apply(c, t)
            held = pump_arbiter.state_for(c)
            if held.supply is not None:
                await pump_arbiter.supply_tick(held, pump_arbiter.SupplyWiring(c.arbiter_inputs, boost.held_for(c), c._write_supply), t)
            off_min += c.hass.states.get("switch.p").state == "off"
        out[last_on] = (off_min, c._plan_is_stale())
    print("V2 s1-04 last_on->(minutes off of 240, stale at end)", out)


# ---------------------------------------------------------------- s1-05
async def s1_05():
    res = plan([0, 3, 3, 3, 0, 0, 0, 0], [0] * N)
    out = {}
    for unavailable in (True, False):
        c = rig(["Heating", "DHW (Hot Water)", "Heating + DHW"], mode_state="DHW (Hot Water)")
        c.hass.states.get("switch.p").state = "off"
        t = TS[1] + timedelta(minutes=1)
        adopt(c, res, t)
        if unavailable:
            c.hass.states.get("select.m").state = "unavailable"
        await pump_arbiter.write_supply(c, "switch.p", True)
        held = pump_arbiter.state_for(c)
        w = [x for x in written(c, "select.m")]
        out[unavailable] = ("mode" in held.written, [(x[4], x[5]) for x in w])
    print("V2 s1-05 unavailable->(recorded, [(value,skipped)])", out)


# ---------------------------------------------------------------- s2-01
async def s2_01():
    """A cycle late in step k; at k+1 the arbiter ticks each minute: frequency and displace writes in k+1."""
    res = plan([0, 3, 5, 5, 0, 0, 0, 0], [0] * N)
    cfg = dict(compressor_freq_entity="number.f", freq_control_mode="control",
               ecl110_displace_set_topic="e/d/set", ecl110_command_topic="e/c")
    c = rig(["Heating", "DHW (Hot Water)", "Heating + DHW"], extra_cfg=cfg)
    for d in range(10):
        hz = 20 + (d + 0.5) * 7
        for _ in range(8):
            c._freq_map.observe(hz, hz * 0.06, 20.0, 90.0)
    t = TS[1] + timedelta(minutes=12)
    adopt(c, res, t)
    dt_util.freeze(t)
    await c._apply_action()
    await c._command_frequency()
    n0 = len(c.hass.services.log)
    for m in range(1, 18):  # through step 2 until the next cycle at +30
        tt = t + timedelta(minutes=m)
        dt_util.freeze(tt)
        await pump_arbiter.apply(c, tt)
        held = pump_arbiter.state_for(c)
        if held.supply is not None:
            await pump_arbiter.supply_tick(held, pump_arbiter.SupplyWiring(c.arbiter_inputs, boost.held_for(c), c._write_supply), tt)
    later = c.hass.services.log[n0:]
    f = [x for x in later if x[3] == "number.f"]
    mq = [x for x in later if x[1] == "mqtt"]
    sp = [x for x in later if x[3] == "number.s"]
    freq_k1 = c._freq_map.recommend(5.0 * 0.0 + 5.0, 20.0, 90.0)
    print(f"V2 s2-01 freq_in_force={c.hass.states.get('number.f').state} step2_own={freq_k1} "
          f"freq_writes_in_step2_before_cycle={len(f)} mqtt_writes={len(mq)} space_sp_writes={len(sp)}")


# ---------------------------------------------------------------- s2-02 / s3-04 / s3-02 (static order and callers)
def static():
    src = open(PKG + "coordinator.py").read()
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef) and n.name == "_async_update_data")
    calls = [(n.lineno, n.func.attr) for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
    first = {}
    for ln, name in sorted(calls):
        first.setdefault(name, ln)
    order = {k: first.get(k) for k in ("_update_current_state", "async_run_optimization", "_apply_action")}
    print("V2 s2-02 _async_update_data first-call lines", order)
    leg = open(PKG + "legionella.py").read()
    print("V2 s2-02 legionella reads self._action() at lines",
          [i + 1 for i, l in enumerate(leg.splitlines()) if "self._action()" in l])
    callers = []
    for f in sorted(os.listdir(PKG)):
        if f.endswith(".py"):
            for i, l in enumerate(open(PKG + f).read().splitlines()):
                if re.search(r"off_restore\.async_restore\(|async_mode_change\(", l) and "def " not in l:
                    callers.append(f"{f}:{i + 1}")
    print(f"V2 s3-04 callers_of_restore={len(callers)} {callers}")
    print("V2 s3-02 registered consumers", sorted(off_restore._CONSUMERS))


# ---------------------------------------------------------------- s2-03
async def s2_03():
    res = plan([0, 3, 0, 3, 0, 0, 0, 0], [0] * N)
    out = {}
    for moved in (True, False):
        c = rig(["Heating", "DHW (Hot Water)", "Heating + DHW"], mode_state="Heating")
        t = TS[1] + timedelta(minutes=2)
        adopt(c, res, t)
        await pump_arbiter.apply(c, t)
        rec = pump_arbiter.state_for(c).written.get("mode")
        c.hass.states.get("switch.p").state = "off"
        if moved:
            c.hass.states.get("select.m").state = "DHW (Hot Water)"
        t3 = TS[3] + timedelta(minutes=1)
        adopt(c, res, t3)
        await pump_arbiter.write_supply(c, "switch.p", True)
        out[moved] = (rec[0] if rec else None, c.hass.states.get("select.m").state)
    print("V2 s2-03 moved->(record, mode at switch-on)", out)


# ---------------------------------------------------------------- s3-01 / s3-03
async def s3_01():
    res = plan([0, 0, 0, 0, 0, 0, 0, 0], [0, 2, 2, 2, 0, 0, 0, 0])
    c = rig(["Heating", "DHW (Hot Water)", "Heating + DHW"], tank=40.0)
    t = TS[1] + timedelta(minutes=2)
    adopt(c, res, t)
    await pump_arbiter.apply(c, t)
    before = c.hass.states.get("select.m").state
    await c.async_set_mode("off", refresh=False)
    for m in range(1, 4):
        tt = t + timedelta(minutes=m)
        dt_util.freeze(tt)
        await pump_arbiter.apply(c, tt)
    print(f"V2 s3-01 mode_before_off={before!r} mode_after_off_3_ticks={c.hass.states.get('select.m').state!r} "
          f"(baseline 'Heating + DHW')")


async def s3_03():
    out = {}
    for disinf in (True, False):
        res = plan([0, 3, 3, 0, 0, 0, 0, 0], [0] * N)
        c = rig(["Heating", "DHW (Hot Water)", "Heating + DHW"],
                extra_cfg=dict(dhw_disinfection_switch_entity="switch.d", dhw_disinfection_mode="control"))
        c.hass.states._states["switch.d"] = FakeState("off") if hasattr(c.hass.states, "_states") else None
        t = TS[1] + timedelta(minutes=2)
        adopt(c, res, t)
        if disinf:
            c._legionella.disinfect.memo = True
        await pump_arbiter.apply(c, t)
        await pump_arbiter.release(c)
        out[disinf] = c.hass.states.get("number.t").state
    print("V2 s3-03 disinfecting->tank set-point after release (configured 50)", out)


async def s3_02():
    """Idle step switches the supply off; then Off, then unload: the switch state after each."""
    res = plan([3, 0, 0, 0, 0, 0, 0, 0], [0] * N)
    c = rig(["Heating", "DHW (Hot Water)", "Heating + DHW"])
    t = TS[1] + timedelta(minutes=2)
    adopt(c, res, t)
    await c._apply_action()
    s_idle = c.hass.states.get("switch.p").state
    await c.async_set_mode("off", refresh=False)
    for m in range(1, 4):
        dt_util.freeze(t + timedelta(minutes=m))
        await pump_arbiter.apply(c, t + timedelta(minutes=m))
    s_off = c.hass.states.get("switch.p").state
    await off_restore.async_restore(c.hass, c.entry, c.effective_config, "unload")
    await c.async_shutdown()
    print(f"V2 s3-02 switch after idle={s_idle} after Off+3 ticks={s_off} after unload={c.hass.states.get('switch.p').state}")


async def main(ids):
    blocks = {"s1-01": s1_01, "s1-02": s1_02, "s1-03": s1_03, "s1-04": s1_04, "s1-05": s1_05,
              "s2-01": s2_01, "static": static, "s2-03": s2_03, "s3-01": s3_01, "s3-03": s3_03, "s3-02": s3_02}
    for k in ids or blocks:
        try:
            r = blocks[k]()
            if asyncio.iscoroutine(r):
                await r
        except Exception as e:  # noqa: BLE001
            import traceback
            print(f"V2 {k} ERROR {type(e).__name__}: {e}")
            traceback.print_exc(limit=3)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
