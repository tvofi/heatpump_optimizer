"""D1 verifier v1 (round 8), own harness for D1-s1-01.

Metric (one line): of the thermal-parameter writes that the production write
path (coordinator.async_update_thermal_params, what handle_set_thermal_params
calls after validation) makes while async_run_optimization is parked on its
solve await, count the written fields whose LIVE value (ctx._thermal_params)
and PUBLISHED value (coordinator.data) differ from the written value once the
refresh cycle has returned; away mode inactive.

Method, deliberately different from the finder's: no wall-clock race. The
interleave is injected deterministically at the one await the solve parks on
(coordinator._await_process), which is exactly where the real event loop may
run a service call. FakeHass (inline executor) is fine here because nothing is
measured about the executor boundary; the order of loop events is forced.
Arms:
  race     write lands inside the solve await              (expected 2 / 2)
  control  same write after the cycle returned (null)      (expected 0 / 0)
  late     write lands inside the solve await of a cycle, then a SECOND full
           cycle runs: does the next solve see the reverted value?  (2)
--perturb: a fix-shaped edit, applied in-process and restored in finally:
  away.restore_setback restores a field only when its live value still equals
  the value the setback left there (compare-and-swap). race must go to 0.
Command (tree root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D1/v1_setback_race.py [--perturb]
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; 4-vCPU shared cloud container.
Counts are final; no timing is reported.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import timedelta  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import away as away_mod  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402

PERTURB = "--perturb" in sys.argv
WANT = {"dhw_min_temperature": 37.0, "dhw_idle_min_temperature": 29.0}
LIVE = {"dhw_min_temperature": "dhw_min_temp",
        "dhw_idle_min_temperature": "dhw_idle_min_temp"}


def states():
    now = dt_util.now()
    mid = now.replace(hour=0, minute=0, second=0, microsecond=0)
    rows = [{"start": (mid + timedelta(hours=h)).isoformat(),
             "end": (mid + timedelta(hours=h + 1)).isoformat(),
             "value": round(0.5 + 0.4 * ((h * 5) % 11) / 11.0, 4)} for h in range(48)]
    return {
        "sensor.indoor": FakeState("21.0", last_updated=now),
        "sensor.outdoor": FakeState("-5.0", last_updated=now),
        "sensor.price": FakeState("0.7", last_updated=now,
                                  attributes={"raw_today": rows[:24], "raw_tomorrow": rows[24:]}),
    }


def config():
    return {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
            const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
            const.CONF_PRICE_SOURCE: const.PRICE_SOURCE_ENTITY,
            const.CONF_PRICE_ENTITY: "sensor.price",
            const.CONF_DHW_TANK_VOLUME: 200.0}


def mismatches(coord):
    p = coord._ctx._thermal_params
    live = sum(1 for k, a in LIVE.items() if getattr(p, a) != WANT[k])
    pub = sum(1 for k in LIVE if (coord.data or {}).get(k) != WANT[k])
    return live, pub


async def arm(kind):
    coord = cm.HeatPumpOptimizerCoordinator(FakeHass(states()), FakeEntry(data=config()))
    await coord._update_current_state()
    assert not coord._away_state.active
    injected = {"n": 0, "during_solve": 0}
    orig = cm._await_process

    async def wrapped(hass, fn, *args):
        if kind in ("race", "late") and coord._optimization_running and injected["n"] == 0:
            injected["n"] += 1
            injected["during_solve"] = int(coord._optimization_running)
            await coord.async_update_thermal_params(dict(WANT))
        return await orig(hass, fn, *args)

    solves = []
    orig_solve_snapshot = coord._solve_snapshot

    def snap():
        s = orig_solve_snapshot()
        solves.append((s[1].model.params.dhw_min_temp, s[1].model.params.dhw_idle_min_temp))
        return s

    coord._solve_snapshot = snap
    cm._await_process = wrapped
    try:
        await coord.async_refresh()
        if kind == "control":
            await coord.async_update_thermal_params(dict(WANT))
            await coord.async_refresh()
        if kind == "late":
            await coord.async_refresh()
    finally:
        cm._await_process = orig
    live, pub = mismatches(coord)
    p = coord._ctx._thermal_params
    print(f"  arm={kind} injected={injected['n']} in_solve={injected['during_solve']} "
          f"ok={coord.last_update_success} live=({p.dhw_min_temp},{p.dhw_idle_min_temp}) "
          f"pub=({coord.data.get('dhw_min_temperature')},{coord.data.get('dhw_idle_min_temperature')}) "
          f"solve_inputs={solves}")
    next_solve_reverted = None
    if kind == "late" and len(solves) >= 2:
        next_solve_reverted = sum(1 for v, w in zip(solves[-1], WANT.values()) if v != w)
    return live, pub, injected["during_solve"], next_solve_reverted


def cas_restore(original, opt_config, thermal_params, _applied={}):
    # compare-and-swap: only undo what the setback itself left in place
    for obj, names in ((opt_config, ("target_temp", "min_temp", "comfort_temp_day", "comfort_temp_night")),
                       (thermal_params, ("dhw_min_temp", "dhw_idle_min_temp"))):
        for n in names:
            if getattr(obj, n) == _applied.get(n, original[n]):
                setattr(obj, n, original[n])


async def main():
    orig_apply, orig_restore = away_mod.apply_setback, away_mod.restore_setback
    applied = {}

    def rec_apply(state, oc, tp):
        o = orig_apply(state, oc, tp)
        applied.clear()
        applied.update(target_temp=oc.target_temp, min_temp=oc.min_temp,
                       comfort_temp_day=oc.comfort_temp_day, comfort_temp_night=oc.comfort_temp_night,
                       dhw_min_temp=tp.dhw_min_temp, dhw_idle_min_temp=tp.dhw_idle_min_temp)
        return o

    if PERTURB:
        cm.away_mode.apply_setback = rec_apply
        cm.away_mode.restore_setback = lambda o, oc, tp: cas_restore(o, oc, tp, applied)
    out = {}
    try:
        for kind in ("race", "control", "late"):
            live, pub, ins, nxt = await arm(kind)
            out[f"{kind}_reverted_live"] = live
            out[f"{kind}_reverted_published"] = pub
            out[f"{kind}_in_solve_at_write"] = ins
            if nxt is not None:
                out["late_next_solve_inputs_reverted"] = nxt
    finally:
        cm.away_mode.apply_setback = orig_apply
        cm.away_mode.restore_setback = orig_restore
        cm._shutdown_process_pool()
    return out


if __name__ == "__main__":
    pc0, tc0 = time.process_time(), time.thread_time()
    res = asyncio.run(main())
    for k, v in res.items():
        print(f"RESULT {k}={v} count")
    pc, tc = time.process_time() - pc0, time.thread_time() - tc0
    print(f"RESULT thread_factor={pc / tc if tc else float('nan'):.3f}")
    print(f"RESULT load1={open('/proc/loadavg').read().split()[0]}")
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')]
    print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")
    print(f"RESULT perturbed={int(PERTURB)}")
