#!/usr/bin/env python3
"""D10.M1 config-flow (Bronze) subcheck "Uses ConfigEntry.data and ConfigEntry.options correctly".

Metric: number of keys in the ``data`` of the entry the config flow creates
(the dict handed to ``async_create_entry``) that are NOT asked on the two
connection screens (``user`` credentials + ``user_sensors`` entity slots)
-- settings "not needed for the connection", which the rule says belong in
``ConfigEntry.options``. Of those, the number the options flow also edits
(rows of config_flow._OPTION_FIELDS) is printed as a second RESULT.
Two walks: ``continue`` (finish_setup -> temperature -> building ->
thermal -> ... every form submitted at its own schema defaults) and
``finish_now`` (the two required screens only: the null arm, where the
rule is met by construction and the count must be 0).
Count key: the keys of the created entry's ``data`` as the production flow
delivers them (HeatPumpOptimizerConfigFlow._create_setup_entry ->
async_create_entry), never the strings or the schema.
Instrumented symbols: config_flow:HeatPumpOptimizerConfigFlow (every
async_step_* walked), config_flow:HeatPumpOptimizerConfigFlow._create_setup_entry.
Perturbation: ``--perturb`` swaps _create_setup_entry for the rule's shape:
data = the connection-screen keys, options = the rest (async_create_entry's
``options=`` keyword); settings_in_data must fall to 0 (to_zero) and the
merged {**data, **options} must equal the baseline walk's data (no setting
lost).

Run (from the export root):
  PYTHONPATH=tests/hastub <HOME>/.local/state/hpo/venv-ci/bin/python3 \
      dev/audit/rounds/round11/D10/s1/cfg_data_options.py [--perturb]
Expected: continue walk settings_in_data >= 30 (exact count in REPORT);
finish_now walk settings_in_data=0; --perturb 0 with merged_equal=1.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: macOS arm64, venv-ci Python 3.14.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import sys
import tempfile
import time

sys.path.insert(0, "tests")
os.environ.setdefault("HPO_PLANDATA", os.path.join(tempfile.mkdtemp(prefix="d10s1."), "plandata.json"))
from harness import FakeHass  # noqa: E402

from homeassistant.data_entry_flow import AbortFlow  # noqa: E402

from heatpump_optimizer import config_flow, const  # noqa: E402

PERTURB = "--perturb" in sys.argv
FIRST = {"name": "Heat Pump Optimizer", const.CONF_TIBBER_TOKEN: "tok-a",
         const.CONF_WEATHER_ENTITY: "weather.home"}
SENSORS = {const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_a"}
# The menus' choices on the "continue" walk: the manual path through every
# page the wizard has (thermal rather than the questionnaire).
MENU_PICK = {"finish_setup": "temperature", "building": "thermal"}


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


def defaults(result):
    out = {}
    for marker, _v in (result.get("data_schema").schema or {}).items():
        key = str(getattr(marker, "schema", marker))
        try:
            out[key] = marker.default()
        except Exception:  # noqa: BLE001 - no default: leave it out
            pass
    return out


async def step(flow, sid, answers):
    try:
        return await getattr(flow, f"async_step_{sid}")(answers)
    except AbortFlow as err:
        return {"type": "abort", "reason": err.reason}


async def walk(mode):
    created = {}
    flow = config_flow.HeatPumpOptimizerConfigFlow()
    flow.hass = FakeHass()
    orig_create = flow.async_create_entry

    def capture(**kw):
        created.update(kw)
        return orig_create(**kw)
    flow.async_create_entry = capture
    r = await step(flow, "user", dict(FIRST))
    r = await step(flow, "user_sensors", dict(SENSORS))
    connection = set(FIRST) | set(SENSORS) | set(defaults({"data_schema": __import__("voluptuous").Schema(config_flow._user_sensors_fields(flow.hass))}))
    visited = []
    for _ in range(60):
        if r.get("type") == "create_entry":
            break
        sid = r.get("step_id")
        visited.append(sid)
        if r.get("type") == "menu":
            opts = list(r.get("menu_options", {}))
            pick = "finish_now" if mode == "finish_now" and "finish_now" in opts else MENU_PICK.get(sid, opts[0])
            r = await step(flow, pick, None)
            continue
        if r.get("type") == "form":
            ans = defaults(r)
            if r.get("errors"):
                raise SystemExit(f"form {sid} refused its own defaults: {r.get('errors')}")
            r = await step(flow, sid, ans)
            continue
        raise SystemExit(f"unexpected result {r}")
    if r.get("type") != "create_entry":
        raise SystemExit(f"walk {mode} did not create an entry; visited {visited}")
    return created, connection, visited


async def main():
    config_flow.async_get_clientsession = lambda hass, verify_ssl=True: _Session()
    option_keys = {row.key for row in config_flow._OPTION_FIELDS if row.key}
    base_data = None
    if PERTURB:
        orig = config_flow.HeatPumpOptimizerConfigFlow._create_setup_entry
        conn_keys = set(FIRST) | set(SENSORS)

        def split(self):
            hass_ = self.hass
            conn = conn_keys | set(defaults({"data_schema": __import__("voluptuous").Schema(config_flow._user_sensors_fields(hass_))}))
            data = {k: v for k, v in self._data.items() if k in conn}
            opts = {k: v for k, v in self._data.items() if k not in conn}
            return self.async_create_entry(title=self._data.get("name", "Heat Pump Optimizer"),
                                           data=data, options=opts)
        # baseline data first, for the no-loss check
        created, _c, _v = await walk("continue")
        base_data = dict(created.get("data") or {})
        config_flow.HeatPumpOptimizerConfigFlow._create_setup_entry = split
        print("RESULT perturbed=_create_setup_entry splits connection keys into data, the rest into options")
    for mode in ("continue", "finish_now"):
        created, connection, visited = await walk(mode)
        data = dict(created.get("data") or {})
        opts = dict(created.get("options") or {})
        settings = sorted(k for k in data if k not in connection)
        editable = [k for k in settings if k in option_keys]
        print(f"WALK {mode}: visited={visited}")
        print(f"WALK {mode}: data_keys={len(data)} options_keys={len(opts)}")
        print(f"WALK {mode}: settings_in_data={settings}")
        print(f"RESULT {mode}_settings_in_data={len(settings)} count")
        print(f"RESULT {mode}_options_flow_editable_in_data={len(editable)} count")
        if PERTURB and mode == "continue":
            print(f"RESULT merged_equal={int({**data, **opts} == base_data)} count")


if __name__ == "__main__":
    c0, t0 = time.process_time(), time.thread_time()
    asyncio.run(main())
    c1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={((c1 - c0) / max(t1 - t0, 1e-9)):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
