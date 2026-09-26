"""D10-s1 unique-config-entry: does an entry's unique id follow its identity?

Metric: over five arms, each of which first sets up entry E through the real
config flow (user -> user_sensors, unique id taken from the flow) and then
changes E through one production write path, count
  dup_accepted  = arms where a FRESH setup flow submitting E's *current*
                  identity answers (token + identity entity slots, as E's
                  effective config data|options now holds them) is NOT
                  aborted "already_configured" -- a second entry for the plant
                  E already runs;
  stale_refused = arms where a fresh setup submitting E's *original* answers
                  (which no entry now holds) IS aborted "already_configured".
Count key: the flow result the production ConfigFlow returns (abort reason),
never an input attribute. entry.unique_id is only read, to print.

Arms: control_none (no change), reconfigure (async_step_reconfigure, rewrites
the unique id -- the seam that is right), reauth (async_step_reauth_confirm,
new token), options_token (options 'entities' page, new token),
options_indoor (options 'entities' page, new indoor sensor).

Perturbation: --fix wraps hass.config_entries.async_update_entry so every
write re-stamps unique_id = config_flow.entry_identity({**data, **options})
(what a one-line fix at each seam would do). Expected: baseline
dup_accepted=3, stale_refused=3; --fix dup_accepted=0, stale_refused=0.
Null control: control_none and reconfigure count 0 in both runs.

Run (from the export root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D10/s1/unique_id_drift.py [--fix]
Expected +- 0 (counts). Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1,
machine: audit box B1 (Linux container). Root rule: cwd (sys.path 'tests').
"""
from __future__ import annotations

import os

for _var in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_var, "1")

import asyncio  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import config_flow, const  # noqa: E402
from homeassistant.data_entry_flow import AbortFlow  # noqa: E402

FIX = "--fix" in sys.argv


class FakeResponse:
    def __init__(self, status, payload=None):
        self.status = status
        self._payload = payload

    async def json(self):
        return self._payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class OkSession:
    def post(self, *a, **k):
        return FakeResponse(200, {"data": {"viewer": {"name": "Home"}}})


config_flow.async_get_clientsession = lambda hass, verify_ssl=True: OkSession()

CREDS = {"name": "Heat Pump Optimizer", const.CONF_TIBBER_TOKEN: "tok-a",
         const.CONF_WEATHER_ENTITY: "weather.home"}
SENSORS = {const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_a",
           const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor_a"}
FIRST = frozenset(CREDS)


async def submit(flow, step, answers):
    try:
        return await getattr(flow, f"async_step_{step}")(dict(answers))
    except AbortFlow as err:
        return {"type": "abort", "reason": err.reason}


async def fresh_setup(hass, answers):
    flow = config_flow.HeatPumpOptimizerConfigFlow()
    flow.hass = hass
    creds = {k: v for k, v in answers.items() if k in FIRST}
    sensors = {k: v for k, v in answers.items() if k not in FIRST}
    res = await submit(flow, "user", creds)
    if res.get("type") == "form" and res.get("step_id") == "user_sensors":
        res = await submit(flow, "user_sensors", sensors)
    return flow, res


def is_dup_abort(res):
    return res.get("type") == "abort" and res.get("reason") == "already_configured"


def identity_answers(entry):
    eff = {**entry.data, **entry.options}
    keys = set(FIRST) | set(SENSORS)
    return {k: eff[k] for k in keys if eff.get(k)}


async def run_arm(arm):
    hass = FakeHass()
    if FIX:
        real = hass.config_entries.async_update_entry

        def restamp(entry, options=None, **kw):
            real(entry, options=options, **kw)
            entry.unique_id = config_flow.entry_identity({**entry.data, **entry.options})
            hass.config_entries.updated.append("restamp")

        hass.config_entries.async_update_entry = restamp
    original = {**CREDS, **SENSORS}
    flow, res = await fresh_setup(hass, original)
    assert flow.unique_id, res
    entry = FakeEntry(data=dict(original), entry_id="E", unique_id=flow.unique_id)
    hass.config_entries.entries.append(entry)
    if arm == "reconfigure":
        rf = config_flow.HeatPumpOptimizerConfigFlow()
        rf.hass = hass
        rf.context = {"source": "reconfigure", "entry_id": "E"}
        r1 = await submit(rf, "reconfigure", {**CREDS, const.CONF_TIBBER_TOKEN: "tok-b"})
        r2 = await submit(rf, "user_sensors", SENSORS)
        assert r2.get("reason") == "reconfigure_successful", (r1, r2)
    elif arm == "reauth":
        ra = config_flow.HeatPumpOptimizerConfigFlow()
        ra.hass = hass
        ra.context = {"source": "reauth", "entry_id": "E"}
        await ra.async_step_reauth(entry.data)
        r = await ra.async_step_reauth_confirm({const.CONF_TIBBER_TOKEN: "tok-b"})
        assert r.get("reason") == "reauth_successful", r
    elif arm in ("options_token", "options_indoor"):
        of = config_flow.HeatPumpOptimizerOptionsFlow(entry)
        of.hass = hass
        page = await of.async_step_entities(None)
        assert page.get("step_id") == "entities", page
        change = ({const.CONF_TIBBER_TOKEN: "tok-b"} if arm == "options_token"
                  else {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor_new"})
        answers = {**identity_answers(entry), **change}
        answers.pop("name", None)
        r = await of.async_step_entities(answers)
        eff = {**entry.data, **entry.options}
        k, v = next(iter(change.items()))
        assert eff.get(k) == v, (arm, r, entry.options)
    now_answers = identity_answers(entry)
    _, now_res = await fresh_setup(hass, now_answers)
    _, old_res = await fresh_setup(hass, original)
    changed = now_answers != {k: v for k, v in original.items() if v}
    dup = not is_dup_abort(now_res)
    stale = changed and is_dup_abort(old_res)
    print(f"arm={arm:15s} changed={changed!s:5s} fresh(current)->{now_res.get('type')}/"
          f"{now_res.get('reason') or now_res.get('step_id')}  fresh(original)->"
          f"{old_res.get('type')}/{old_res.get('reason') or old_res.get('step_id')}  "
          f"uid_follows={entry.unique_id == config_flow.entry_identity({**entry.data, **entry.options})}")
    return int(dup), int(stale)


async def main():
    arms = ["control_none", "reconfigure", "reauth", "options_token", "options_indoor"]
    dup = stale = 0
    for arm in arms:
        d, s = await run_arm(arm)
        dup += d
        stale += s
    print(f"MODE {'fix' if FIX else 'baseline'}")
    print(f"RESULT dup_accepted={dup} arms")
    print(f"RESULT stale_refused={stale} arms")
    print(f"RESULT arms={len(arms)} count")


t0p, t0t = time.process_time(), time.thread_time()
asyncio.run(main())
dp, dt = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={dp / dt if dt else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    with open("/proc/vmstat") as fh:
        print("RESULT swapins=" + next(l.split()[1] for l in fh if l.startswith("pswpin")))
except (OSError, StopIteration):
    print("RESULT swapins=unknown")
