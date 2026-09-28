"""C2: _record_manual_release writes the solve's safety releases into
whatever self._manual_override is AFTER the solve await, with no identity
check against the override _manual_pins read BEFORE it.

Real coordinator, real solve, held on an asyncio.Event.
  O1 = space forced OFF for the whole manual window (at -5 C outdoor the
       solver must release pinned steps for safety)
  O2 = space forced ON 1 h, 2-3 h ahead (a different override)
probe: A = async_run_optimization() with O1 in force, held; inside the
       window the apply_manual_plan path (coord.async_apply_manual_plan(O2):
       adopt, persist, request_refresh) runs; release A.
null1: same, no swap -> O1's own releases.
null2: O2 solved on its own -> O2's true releases.
Observed: the override object each released list lands on, the plan
sensor's manual-plan state (_manual_plan_state), the persisted store payload,
and whether any solve ever ran against O2's pins.
"""
import asyncio
from datetime import timedelta

import rig
from heatpump_optimizer import manual_plan

PINS_SEEN = []


def overrides(now):
    o1 = manual_plan.build_override(dhw_slots=None, space_slots=[], expires_at=now + timedelta(hours=10), now=now)
    o2 = manual_plan.build_override(
        dhw_slots=None,
        space_slots=[{"start": (now + timedelta(hours=2)).isoformat(), "end": (now + timedelta(hours=3)).isoformat()}],
        expires_at=now + timedelta(hours=10), now=now)
    return o1, o2


def tag(c, o1, o2):
    real = c._manual_pins

    def spy(solve_now, n):
        o = c._manual_override
        PINS_SEEN.append("O1" if o is o1 else "O2" if o is o2 else repr(o))
        return real(solve_now, n)

    c._manual_pins = spy


def state(c, o1, o2):
    s = c._manual_plan_state() or {}
    return {"sensor.space_slots_n": len(s.get("space_slots") or []), "sensor.released_space_n": len(s.get("released_space") or [])}


async def arm(name):
    c = rig.make(f"c2_{name}")
    now = rig.dt_util.now()
    o1, o2 = overrides(now)
    PINS_SEEN.clear()
    tag(c, o1, o2)
    saved = []
    real_save = c._manual_plan_store.async_save

    async def save_spy(payload):
        saved.append(payload)
        return await real_save(payload)

    c._manual_plan_store.async_save = save_spy
    if name == "null2/O2-alone":
        c._manual_override = o2
        r = await c.async_run_optimization()
    else:
        c._manual_override = o1
        rig.GATE.arm()
        a = asyncio.get_running_loop().create_task(c.async_run_optimization())
        await asyncio.wait_for(rig.GATE.entered.wait(), 60)
        if name == "probe/swap-to-O2":
            await c.async_apply_manual_plan(o2)
        rig.GATE.release.set()
        r = await a
        rig.GATE.disarm()
    cur = c._manual_override
    res = c._optimization_result
    # One more save, as the next persist of the override would do.
    await c._async_save_manual_plan()
    return {
        "arm": name,
        "solve": r,
        "solves ran against": list(PINS_SEEN),
        "current override": "O1" if cur is o1 else "O2" if cur is o2 else cur,
        "result.manual_released_space (n)": len(res.manual_released_space),
        "O1.released_space (n)": len(o1.released_space),
        "O2.released_space (n)": len(o2.released_space),
        "O2.released idx[:6]": [r["step"] for r in o2.released_space][:6],
        "O2 pin value at those idx": _pinvals(c, o2, now),
        "published plan kW at O2's ON steps": _on_steps_power(c, o2, now),
        **state(c, o1, o2),
    }


def _on_steps_power(c, o2, now):
    starts = c._horizon_step_starts(rig.cmod._solve_anchor(now), c._opt_config.n_steps)
    pins = o2.channel_pins("space", starts) or []
    ps = list(c._optimization_result.power_schedule)
    return [round(float(ps[i]), 2) for i, p in enumerate(pins) if p == 1.0 and i < len(ps)]


def _pinvals(c, o2, now):
    starts = c._horizon_step_starts(rig.cmod._solve_anchor(now), c._opt_config.n_steps)
    pins = o2.channel_pins("space", starts) or []
    return [pins[r["step"]] if r["step"] < len(pins) else "-" for r in o2.released_space][:6]


async def main():
    rows = [await arm("probe/swap-to-O2"), await arm("null1/no-swap"), await arm("null2/O2-alone")]
    keys = [k for k in rows[0] if k != "arm"]
    w = 26
    print("field".ljust(40) + "".join(r["arm"].ljust(w) for r in rows))
    for k in keys:
        print(k.ljust(40) + "".join(str(r[k]).ljust(w) for r in rows))


asyncio.run(main())
