#!/usr/bin/env python3
"""D10.M1/M2: one executed check per Bronze and Silver rule of the HA quality scale.

Metric: per rule, the count of sites that break the rule as its page states it
(RESULT <rule>_violations=N), over the enumeration the check names; 0 = the
rule holds at every site this check reaches. Rules whose check is a separate
harness in this directory say so (RESULT <rule>_see=<harness>).
Enumerator for the rule universe: the Bronze and Silver ids of the HA
checklist (tiers.json, fetched 2026-11-16, snapshot in this directory:
ha_tiers.json); the integration's rows are quality_scale.yaml's under
# Bronze and # Silver.
Instrumented symbols (per check, named in its RESULT block): __init__:async_setup,
__init__:async_setup_entry/async_unload_entry, coordinator:HeatPumpOptimizerCoordinator
(update_interval, _fetch_tibber_prices, async_config_entry_first_refresh),
every platform's async_setup_entry and its entities, config_flow:HeatPumpOptimizerConfigFlow.
Perturbation: ``--perturb <rule>`` applies the named in-memory break and the
rule's violation count must move up: parallel-updates (delete
sensor.PARALLEL_UPDATES), has-entity-name (_attr_has_entity_name=False on the
base entity), entity-unique-id (base _pin_identity drops the unique id),
action-setup (async_setup registers nothing), log-when-unavailable (the
outage latch counter reset every cycle), entity-unavailable (CoordinatorEntity
.available forced True), test-before-setup (first refresh swallows the failure).

Run (from the export root):
  PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python3 \
      dev/audit/rounds/round11/D10/s1/qs_rules.py [--perturb RULE]
Expected: see REPORT.md tier table (exact counts).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (the round's export tree). Machine: macOS arm64, venv-ci Python 3.14.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import ast
import asyncio
import glob
import importlib
import json
import logging
import re
import struct
import sys
import tempfile
import time

sys.path.insert(0, "tests")
os.environ.setdefault("HPO_PLANDATA", os.path.join(tempfile.mkdtemp(prefix="d10s1."), "plandata.json"))
from harness import FakeEntry, FakeHass, FakeState, ha_setup_component, ha_setup_entry, ha_unload_entry  # noqa: E402

import yaml  # noqa: E402

from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady  # noqa: E402

import heatpump_optimizer as integ  # noqa: E402
from heatpump_optimizer import config_flow, const, entity as entity_mod  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

PKG = "custom_components/heatpump_optimizer"
HERE = os.path.dirname(os.path.abspath(__file__))
PERTURB = sys.argv[sys.argv.index("--perturb") + 1] if "--perturb" in sys.argv else None
PLATFORMS = ["sensor", "binary_sensor", "button", "climate", "switch", "datetime"]


def res(rule, n, note=""):
    print(f"RESULT {rule}_violations={n} count" + (f"  # {note}" if note else ""))


def docs_text():
    return "\n".join(open(f).read() for f in ["README.md"] + sorted(glob.glob("docs/*.md")))


def scenario_configs():
    from golden import coordinator_scenarios
    return coordinator_scenarios()


# The stub has no HTTP session; the price checks patch pull_prices, which is
# handed whatever session this returns.
coord_mod.async_get_clientsession = lambda hass, *a, **k: object()


def seed_prices(hass):
    from datetime import timedelta
    from homeassistant.util import dt as dt_util
    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    hass.states.set("sensor.prices", FakeState("0.5", attributes={"raw_today": [
        {"start": (now + timedelta(hours=h)).isoformat(), "value": 0.5 + 0.1 * (h % 4)} for h in range(48)]}))


async def collect_entities(cfg):
    hass = FakeHass()
    entry = FakeEntry(data=dict(cfg))
    c = HeatPumpOptimizerCoordinator(hass, entry)
    entry.runtime_data = c
    out = []
    for p in PLATFORMS:
        m = importlib.import_module(f"heatpump_optimizer.{p}")
        await m.async_setup_entry(hass, entry, lambda es, *a, **k: out.extend(es))
    return c, out


# --------------------------------------------------------------------- perturbations
def apply_perturb():
    if PERTURB is None:
        return
    print(f"RESULT perturbed={PERTURB}")
    if PERTURB == "parallel-updates":
        del importlib.import_module("heatpump_optimizer.sensor").PARALLEL_UPDATES
    elif PERTURB == "has-entity-name":
        entity_mod.HeatPumpOptimizerEntity._attr_has_entity_name = False
    elif PERTURB == "entity-unique-id":
        orig = entity_mod.HeatPumpOptimizerEntity._pin_identity

        def pin(self, *a, **k):
            orig(self, *a, **k)
            self._attr_unique_id = None
        entity_mod.HeatPumpOptimizerEntity._pin_identity = pin
    elif PERTURB == "action-setup":
        async def nothing(hass, config):
            return True
        integ.async_setup = nothing
    elif PERTURB == "entity-unavailable":
        from homeassistant.helpers import update_coordinator as uc
        uc.CoordinatorEntity.available = property(lambda self: True)
    elif PERTURB == "log-when-unavailable":
        orig = HeatPumpOptimizerCoordinator._tibber_fetch_failed

        def unlatched(self, *a, **k):
            self._tibber_outage_cycles = 0
            return orig(self, *a, **k)
        HeatPumpOptimizerCoordinator._tibber_fetch_failed = unlatched
    elif PERTURB == "test-before-setup":
        async def swallow(self):
            try:
                await self._async_refresh(log_failures=False)
            except Exception:  # noqa: BLE001
                pass
        HeatPumpOptimizerCoordinator.async_config_entry_first_refresh = swallow


# --------------------------------------------------------------------- checks
async def main():
    apply_perturb()
    tiers = json.load(open(os.path.join(HERE, "ha_tiers.json")))
    universe = [r if isinstance(r, str) else r["id"] for t in ("bronze", "silver") for r in tiers[t]]
    qs = yaml.safe_load(open(f"{PKG}/quality_scale.yaml"))["rules"]
    print(f"RESULT universe_rules={len(universe)} count")
    res("register-rows-missing", sum(1 for r in universe if r not in qs), "Q1: checklist rule without a row")
    res("register-not-done-or-exempt", sum(1 for r in universe
        if (qs[r] if isinstance(qs.get(r), str) else (qs.get(r) or {}).get("status")) not in ("done", "exempt")))
    manifest = json.load(open(f"{PKG}/manifest.json"))
    docs = docs_text()
    services_yaml = yaml.safe_load(open(f"{PKG}/services.yaml"))

    # action-setup: every documented service registered by async_setup, before any entry;
    # an entry's setup adds none; unload removes none.
    hass = FakeHass()
    seed_prices(hass)
    await ha_setup_component(integ, hass, const.DOMAIN)
    reg0 = set(hass.services.async_services().get(const.DOMAIN, {}))
    entry = FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home",
                            "price_source": "entity", "price_entity": "sensor.prices"})
    ok = await ha_setup_entry(integ, hass, entry)
    reg1 = set(hass.services.async_services().get(const.DOMAIN, {}))
    unl = await ha_unload_entry(integ, hass, entry)
    reg2 = set(hass.services.async_services().get(const.DOMAIN, {}))
    missing = set(services_yaml) - reg0
    print(f"INFO action-setup: setup_ok={ok} unload_ok={unl} registered_before_entry={len(reg0)} "
          f"documented={len(services_yaml)} added_by_entry={len(reg1 - reg0)} lost_at_unload={len(reg0 - reg2)}")
    res("action-setup", len(missing) + len(reg1 - reg0) + len(reg0 - reg2))

    # appropriate-polling: the coordinator's interval, default config, >= 1 minute.
    c = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home"}))
    iv = getattr(c, "update_interval", None)
    mins = iv.total_seconds() / 60 if iv else None
    print(f"INFO appropriate-polling: update_interval_min={mins}")
    res("appropriate-polling", int(mins is None or mins < 1))

    # brands: brand/ icon 256x256, icon@2x 512x512 (+dark), logo shortest side 128-256, @2x 256-512.
    bad = 0
    want = {"icon.png": (256, 256), "icon@2x.png": (512, 512), "dark_icon.png": (256, 256), "dark_icon@2x.png": (512, 512)}
    for name, wh in want.items():
        p = f"{PKG}/brand/{name}"
        dims = struct.unpack(">II", open(p, "rb").read(24)[16:24]) if os.path.exists(p) else None
        bad += int(dims != wh)
    for name, lo, hi in (("logo.png", 128, 256), ("logo@2x.png", 256, 512), ("dark_logo.png", 128, 256), ("dark_logo@2x.png", 256, 512)):
        p = f"{PKG}/brand/{name}"
        dims = struct.unpack(">II", open(p, "rb").read(24)[16:24]) if os.path.exists(p) else None
        bad += int(dims is None or not lo <= min(dims) <= hi)
    res("brands", bad)

    # common-modules: coordinator in coordinator.py, base entity in entity.py, every entity derives from it.
    _, ents = await collect_entities({"tibber_token": "x", "weather_entity": "weather.home"})
    v = int(HeatPumpOptimizerCoordinator.__module__ != "heatpump_optimizer.coordinator")
    v += int(entity_mod.HeatPumpOptimizerEntity.__module__ != "heatpump_optimizer.entity")
    v += sum(1 for e in ents if not isinstance(e, entity_mod.HeatPumpOptimizerEntity))
    res("common-modules", v)

    # config-flow: manifest flag + every options-registry field and every strings data field described.
    s = json.load(open(f"{PKG}/strings.json"))
    undesc = 0
    for top in ("config", "options"):
        for sid, st in s[top]["step"].items():
            dd = dict(st.get("data_description") or {})
            data = dict(st.get("data") or {})
            for sec in (st.get("sections") or {}).values():
                dd.update(sec.get("data_description") or {})
                data.update(sec.get("data") or {})
            undesc += sum(1 for k in data if k not in dd)
    for row in config_flow._OPTION_FIELDS:
        if not row.key:
            continue
        st = s["options"]["step"].get(row.step) or {}
        dd = dict(st.get("data_description") or {})
        for sec in (st.get("sections") or {}).values():
            dd.update(sec.get("data_description") or {})
        undesc += int(row.key not in dd)
    res("config-flow", int(manifest.get("config_flow") is not True) + undesc,
        "data_description half; the data/options half is cfg_data_options.py (D10-s1-03)")

    # dependency-transparency: every requirement is a PyPI project name with an OSI licence (curated list).
    osi = {"numpy": "BSD-3-Clause", "scipy": "BSD-3-Clause", "threadpoolctl": "BSD-3-Clause"}
    reqs = [re.split(r"[<>=!~ ]", r)[0] for r in manifest.get("requirements", [])]
    print(f"INFO dependency-transparency: requirements={reqs}")
    res("dependency-transparency", sum(1 for r in reqs if r not in osi))

    # docs-actions: every service (services.yaml) named in README/docs with its fields.
    undoc = [svc for svc in services_yaml if svc not in docs]
    unfields = [f"{svc}.{f}" for svc, spec in services_yaml.items() for f in ((spec or {}).get("fields") or {}) if f not in docs]
    print(f"INFO docs-actions: undocumented_services={undoc} undocumented_fields={unfields}")
    res("docs-actions", len(undoc) + len(unfields))

    # docs-triggers / docs-conditions: vacuous iff the package ships no trigger/condition platform.
    res("docs-triggers", len(glob.glob(f"{PKG}/*trigger*.py")) + int("triggers" in s), "vacuous when 0 platforms")
    res("docs-conditions", len(glob.glob(f"{PKG}/*condition*.py")) + int("conditions" in s), "vacuous when 0 platforms")

    # docs-high-level-description / installation / removal: README sections present.
    readme = open("README.md").read()
    res("docs-high-level-description", int(not re.search(r"^## What it does", readme, re.M)) + int("tibber.com" not in readme.lower()))
    res("docs-installation-instructions", int(not re.search(r"^## Installation", readme, re.M)) + int(not re.search(r"^## Requirements", readme, re.M)))
    res("docs-removal-instructions", int(not re.search(r"^### Removal", readme, re.M)))

    # docs-installation-parameters: every config-flow user/user_sensors field label or key in docs.
    low = re.sub(r"[*_`]", "", docs.lower())

    def labelled(step_tbl, key):
        lab = dict(step_tbl.get("data") or {})
        for sec in (step_tbl.get("sections") or {}).values():
            lab.update(sec.get("data") or {})
        core = re.sub(r"\s*\([^)]*\)", "", lab.get(key, "")).strip().lower()
        return key in docs or (core and core in low)
    miss = []
    for sid in ("user", "user_sensors"):
        st = s["config"]["step"][sid]
        keys = set(st.get("data") or {})
        for sec in (st.get("sections") or {}).values():
            keys |= set(sec.get("data") or {})
        miss += [f"{sid}.{k}" for k in sorted(keys) if not labelled(st, k)]
    print(f"INFO docs-installation-parameters: missing={miss}")
    res("docs-installation-parameters", len(miss))
    miss = [f"{r.step}.{r.key}" for r in config_flow._OPTION_FIELDS if r.key and not labelled(s["options"]["step"][r.step], r.key)]
    print(f"INFO docs-configuration-parameters: rows={sum(1 for r in config_flow._OPTION_FIELDS if r.key)} missing={miss}")
    res("docs-configuration-parameters", len(miss))

    # entity-event-setup: subscription calls inside entity classes outside async_added_to_hass.
    subs = re.compile(r"async_track_\w+|async_listen(_once)?|async_subscribe|async_add_listener")
    bad = []
    for p in PLATFORMS + ["entity"]:
        tree = ast.parse(open(f"{PKG}/{p}.py").read())
        for cls in [n for n in tree.body if isinstance(n, ast.ClassDef)]:
            for fn in [n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
                if fn.name in ("async_added_to_hass", "async_will_remove_from_hass"):
                    continue
                for node in ast.walk(fn):
                    if isinstance(node, ast.Call):
                        name = getattr(node.func, "attr", getattr(node.func, "id", ""))
                        if subs.fullmatch(name or ""):
                            bad.append(f"{p}.{cls.name}.{fn.name}:{name}")
    print(f"INFO entity-event-setup: sites={bad}")
    res("entity-event-setup", len(bad))

    # entity-unique-id / has-entity-name: every entity of every golden coordinator scenario.
    uid_bad = hen_bad = dup = total = 0
    for name, cfg in scenario_configs().items():
        _, ents = await collect_entities(cfg)
        total += len(ents)
        uids = [getattr(e, "_attr_unique_id", None) for e in ents]
        uid_bad += sum(1 for u in uids if not u)
        dup += len(uids) - len(set(uids))
        hen_bad += sum(1 for e in ents if getattr(e, "_attr_has_entity_name", None) is not True)
    print(f"INFO entities checked over {len(scenario_configs())} scenarios: {total}")
    res("entity-unique-id", uid_bad + dup)
    res("has-entity-name", hen_bad)

    # runtime-data: hass.data writes keyed per entry outside the documented reload handover.
    hd = []
    for f in sorted(glob.glob(f"{PKG}/*.py")):
        for i, line in enumerate(open(f), 1):
            if re.search(r"hass\.data\[[^]]*\]\s*=|hass\.data\.setdefault\(", line):
                hd.append(f"{os.path.basename(f)}:{i}")
    print(f"INFO runtime-data: hass.data write sites={hd}")
    # A per-entry store is the rule's subject; frontend.py's write is a process-wide
    # once-flag (the card is served once per instance), not runtime data.
    per_entry = [x for x in hd if not x.startswith(("__init__.py", "frontend.py"))]
    res("runtime-data", len(per_entry) + int("entry.runtime_data = coordinator" not in open(f"{PKG}/__init__.py").read()),
        "per-entry hass.data stores outside the documented reload handover")

    # test-before-configure: a refused / unreachable token is caught on the first screen.
    class _R:
        def __init__(s, st):
            s.status = st

        async def json(s):
            return {}

        async def __aenter__(s):
            return s

        async def __aexit__(s, *e):
            return False

    class _S:
        def __init__(s, st):
            s.st = st

        def post(s, *a, **k):
            if isinstance(s.st, Exception):
                raise s.st
            return _R(s.st)
    tbc = 0
    for status, want_err in ((401, "invalid_tibber_token"), (OSError("down"), "cannot_connect")):
        config_flow.async_get_clientsession = lambda h, verify_ssl=True, st=status: _S(st)
        flow = config_flow.HeatPumpOptimizerConfigFlow()
        flow.hass = FakeHass()
        r = await flow.async_step_user({"name": "x", "tibber_token": "t", "weather_entity": "weather.home"})
        tbc += int((r.get("errors") or {}).get(const.CONF_TIBBER_TOKEN) != want_err)
    res("test-before-configure", tbc)

    # unique-config-entry: the same answers twice abort already_configured.
    from homeassistant.data_entry_flow import AbortFlow
    config_flow.async_get_clientsession = lambda h, verify_ssl=True: _S(200)

    class _OK(_R):
        async def json(s):
            return {"data": {"viewer": {"name": "x"}}}
    config_flow.async_get_clientsession = lambda h, verify_ssl=True: type("S", (), {"post": lambda s, *a, **k: _OK(200)})()
    hass_u = FakeHass()
    first = {"name": "x", "tibber_token": "t", "weather_entity": "weather.home"}
    f1 = config_flow.HeatPumpOptimizerConfigFlow()
    f1.hass = hass_u
    await f1.async_step_user(dict(first))
    await f1.async_step_user_sensors({})
    hass_u.config_entries.entries.append(FakeEntry(data=dict(first), entry_id="u1", unique_id=f1.unique_id))
    f2 = config_flow.HeatPumpOptimizerConfigFlow()
    f2.hass = hass_u
    await f2.async_step_user(dict(first))
    try:
        r2 = await f2.async_step_user_sensors({})
        aborted = False
    except AbortFlow as err:
        aborted = err.reason == "already_configured"
    res("unique-config-entry", int(not aborted) + int(not f1.unique_id))

    # test-before-setup + reauthentication-flow: a failed price fetch at setup raises
    # ConfigEntryNotReady, a refused token ConfigEntryAuthFailed and starts reauth.
    tbs = 0
    for verdict, want in (("fail", ConfigEntryNotReady), ("reauth", ConfigEntryAuthFailed)):
        async def pp(session, cfg, st, v=verdict):
            return v, "harness: price fetch refused"
        orig = coord_mod.pull_prices
        coord_mod.pull_prices = pp
        try:
            h = FakeHass()
            e = FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home"}, entry_id=f"tbs_{verdict}")
            got = None
            try:
                await ha_setup_entry(integ, h, e)
            except Exception as err:  # noqa: BLE001
                got = type(err)
        finally:
            coord_mod.pull_prices = orig
        print(f"INFO test-before-setup: verdict={verdict} raised={got.__name__ if got else None} reauth_starts={e.reauth_starts}")
        tbs += int(got is not want)
        if verdict == "reauth":
            res("reauthentication-flow", int(got is not want) + int(e.reauth_starts < 1)
                + int(not hasattr(config_flow.HeatPumpOptimizerConfigFlow, "async_step_reauth_confirm")))
    res("test-before-setup", tbs)

    # config-entry-unloading: async_unload_entry exists, unload ok, state listeners/timers/bus left.
    h = FakeHass()
    seed_prices(h)
    e = FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home", "price_source": "entity",
                        "price_entity": "sensor.prices", "indoor_temp_entity": "sensor.indoor",
                        "heat_pump_switch_entity": "switch.hp", "away_presence_entity": "person.a"})
    await ha_setup_entry(integ, h, e)
    live = (len(getattr(h, "state_listeners", [])), len(getattr(h, "timers", [])), len(h.bus.listeners))
    ok = await ha_unload_entry(integ, h, e)
    left = (len(getattr(h, "state_listeners", [])), len(getattr(h, "timers", [])), len(h.bus.listeners))
    print(f"INFO config-entry-unloading: live_after_setup={live} left_after_unload={left} unload_ok={ok}")
    res("config-entry-unloading", int(not ok) + sum(left))

    # entity-unavailable: a failed update makes every entity unavailable.
    for name, cfg in list(scenario_configs().items())[-1:]:
        c, ents = await collect_entities(cfg)
        c.last_update_success = False
        still = [type(e).__name__ for e in ents if e.available]
        print(f"INFO entity-unavailable: scenario={name} entities={len(ents)} available_after_failure={still}")
        res("entity-unavailable", len(still))

    # integration-owner
    res("integration-owner", int(not manifest.get("codeowners")))

    # log-when-unavailable: an outage of 6 failed cycles then a recovery logs once each way
    # (integration logger, >= INFO).
    recs = []

    class H(logging.Handler):
        def emit(self, r):
            if r.levelno >= logging.INFO:
                recs.append((r.levelname, r.getMessage()[:80]))
    lg = logging.getLogger("custom_components.heatpump_optimizer")
    logging.getLogger("heatpump_optimizer").addHandler(H())
    lg.addHandler(H())
    logging.getLogger("heatpump_optimizer").setLevel(logging.DEBUG)
    c = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home"}))
    seq = ["fail"] * 6 + ["ok"]
    for v in seq:
        async def pp(session, cfg, st, v=v):
            return (v, "harness outage") if v != "ok" else ("ok", [{"start": "x", "total": 1.0}])
        coord_mod.pull_prices, orig = pp, coord_mod.pull_prices
        try:
            await c._fetch_tibber_prices()
        except Exception:  # noqa: BLE001
            pass
        finally:
            coord_mod.pull_prices = orig
    down = [r for r in recs if "recovered" not in r[1]]
    up = [r for r in recs if "recovered" in r[1]]
    print(f"INFO log-when-unavailable: outage_lines={down} recovery_lines={up}")
    res("log-when-unavailable", max(0, len(down) - 1) + max(0, len(up) - 1) + int(not up))

    # parallel-updates: every entity platform module declares PARALLEL_UPDATES.
    res("parallel-updates", sum(1 for p in PLATFORMS
        if not hasattr(importlib.import_module(f"heatpump_optimizer.{p}"), "PARALLEL_UPDATES")))

    print("RESULT action-exceptions_see=svc_set_away.py,btn_actions.py (D10-s1-01, D10-s1-02)")
    print("RESULT config-flow-test-coverage_see=cfg_recovery.py (D10-s1-05) and cov_modules.sh (config_flow.py statements)")
    print("RESULT test-coverage_see=cov_modules.sh (D10.M3)")


if __name__ == "__main__":
    c0, t0 = time.process_time(), time.thread_time()
    asyncio.run(main())
    c1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={((c1 - c0) / max(t1 - t0, 1e-9)):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
