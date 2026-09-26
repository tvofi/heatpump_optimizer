"""D10-s1-01 verify-v1: the options 'entities' page's save-and-close seam.

Metric: over two arms (options_token, options_indoor) driven through
HeatPumpOptimizerOptionsFlow.async_step_entities with after_save=close (the
_save -> async_create_entry path the finder's harness did not take), count
  dup_accepted = arms where a fresh HeatPumpOptimizerConfigFlow submitting the
                 entry's current identity answers is NOT aborted
                 "already_configured".
Count key: the abort reason the production ConfigFlow returns. The stub's
OptionsFlow.async_create_entry does not apply options; this harness applies the
returned data as entry.options, which is what real HA's OptionsFlowManager does
on a create_entry result.
Perturbation: --fix re-stamps entry.unique_id = config_flow.entry_identity(
{**data, **options}) after the options are applied. Expected: baseline 2, --fix 0.
Null control: arm control_close (page saved with after_save=close, no identity
key changed) counts 0 in both runs.

Run (repo root):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D10/verify-v1/uid_close_path.py [--fix]
Expected +-0 (counts). Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (evidence
tree 6f51db2c). Machine: 4-core Linux cloud container, shared with two verifier
seats. Root rule: cwd.
"""
from __future__ import annotations

import os

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
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


class _Resp:
    status = 200

    async def json(self):
        return {"data": {"viewer": {"name": "Home"}}}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class _Session:
    def post(self, *a, **k):
        return _Resp()


config_flow.async_get_clientsession = lambda hass, verify_ssl=True: _Session()
CREDS = {"name": "HPO", const.CONF_TIBBER_TOKEN: "tok-a",
         const.CONF_WEATHER_ENTITY: "weather.home"}
SENSORS = {const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_a",
           const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor_a"}


async def fresh(hass, answers):
    flow = config_flow.HeatPumpOptimizerConfigFlow()
    flow.hass = hass
    try:
        r = await flow.async_step_user({k: v for k, v in answers.items() if k in CREDS})
        if r.get("step_id") == "user_sensors":
            r = await flow.async_step_user_sensors(
                {k: v for k, v in answers.items() if k not in CREDS})
    except AbortFlow as err:
        r = {"type": "abort", "reason": err.reason}
    return flow, r


def ident(entry):
    eff = {**entry.data, **entry.options}
    return {k: eff[k] for k in (*CREDS, *SENSORS) if eff.get(k)}


async def arm(name):
    hass = FakeHass()
    original = {**CREDS, **SENSORS}
    flow, _ = await fresh(hass, original)
    entry = FakeEntry(data=dict(original), entry_id="E", unique_id=flow.unique_id)
    hass.config_entries.entries.append(entry)
    of = config_flow.HeatPumpOptimizerOptionsFlow(entry)
    of.hass = hass
    await of.async_step_entities(None)
    change = {"options_token": {const.CONF_TIBBER_TOKEN: "tok-b"},
              "options_indoor": {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor_new"},
              "control_close": {}}[name]
    answers = {**ident(entry), **change, const.CONF_AFTER_SAVE: const.AFTER_SAVE_CLOSE}
    answers.pop("name", None)
    res = await of.async_step_entities(answers)
    assert res.get("type") == "create_entry", res
    entry.options = dict(res["data"])  # what real HA's OptionsFlowManager applies
    if FIX:
        entry.unique_id = config_flow.entry_identity({**entry.data, **entry.options})
    for k, v in change.items():
        assert {**entry.data, **entry.options}.get(k) == v
    _, r = await fresh(hass, ident(entry))
    dup = not (r.get("type") == "abort" and r.get("reason") == "already_configured")
    print(f"arm={name:15s} after_save_path=create_entry fresh(current)->{r.get('type')}/"
          f"{r.get('reason') or r.get('step_id')} dup={int(dup)}")
    return int(dup), name == "control_close"


async def main():
    dup = ctrl = 0
    for name in ("control_close", "options_token", "options_indoor"):
        d, is_ctrl = await arm(name)
        if is_ctrl:
            ctrl += d
        else:
            dup += d
    print(f"MODE {'fix' if FIX else 'baseline'}")
    print(f"RESULT dup_accepted_close_path={dup} arms")
    print(f"RESULT control_close={ctrl} arms")


t0p, t0t = time.process_time(), time.thread_time()
asyncio.run(main())
dp, dt = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={dp / dt if dt else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
with open("/proc/vmstat") as fh:
    print("RESULT swapins=" + next(l.split()[1] for l in fh if l.startswith("pswpin")))
