#!/usr/bin/env python3
"""Round-2 D10-B harness: eight quality-scale rules, stub-run on the baseline.

Rules measured (tools/audit/round2/D10/rules.json ids):

    unique-config-entry     duplicate config-flow submission aborts
    config-entry-unloading  setup->unload->reload leaves nothing behind,
                            coordinator shutdown chain calls super()
    entity-unavailable      failed update flips entities unavailable;
                            removed data keys yield unknown, not stale values
    log-when-unavailable    N=5 failed Tibber polls then 1 recovery: ERROR
                            records during the outage (expect 1), INFO at
                            recovery (expect 1)
    reauthentication-flow   401 during update starts the reauth flow once;
                            async_step_reauth/reauth_confirm walk a token fix
    diagnostics             not a platform; payload keys; token redacted
    test-before-configure   the user step probes the Tibber token and shows
                            invalid_tibber_token / cannot_connect on failure
    appropriate-polling     DataUpdateCoordinator update_interval as built

Run from the export root:

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
    .venv/bin/python tools/audit/round2/D10/B/harness.py

(Any python 3.11+ works; the venv is the audit box's.) It never cds and
writes nothing. Expected values (tolerance 0 -- counts):

    duplicate_flow_aborted            1
    distinct_flow_proceeds            1   (null control: second pump passes)
    user_step_error_on_invalid_auth   1
    user_step_error_on_cannot_connect 1
    reauth_flow_started_after_401s    1   (and stays 1 on a second 401)
    reauth_confirm_fixes_entry        1
    platforms_forwarded_on_unload     5
    coordinator_super_shutdown_called 1
    unload_leak_count                 0
    handover_leak_after_reload        0
    sensors_total                     roster size (65-ish)
    sensors_unavailable_after_failure == sensors_total
    stale_publishers_after_key_removal 0
    error_logs_during_5_failed_polls  1   <-- expected by the rule; baseline
                                             measures more (finding D10-B1)
    info_logs_at_recovery             1
    outage_cycles_after_5_polls       5   <-- baseline doubles it (finding)
    diagnostics_in_platform_list      0
    diagnostics_top_level_key_count   4
    token_leak_occurrences            0
    update_interval_default_seconds   1800
    update_interval_configured_seconds 900

Baseline: b39fc6f01f4caee9d3ef17bce5f0b4561392fdb9. Machine: MacBookAir10,1
8 cores (shared during fan-out; all numbers are counts, immune to load).

Instrumented symbols: heatpump_optimizer.config_flow:HeatPumpOptimizerConfigFlow
.async_step_user / .async_step_reauth / .async_step_reauth_confirm,
config_flow:validate_tibber_token, coordinator:HeatPumpOptimizerCoordinator
.__init__ / ._async_update_data / ._fetch_tibber_prices / ._tibber_start_reauth
/ .async_shutdown, heatpump_optimizer:async_setup_entry / .async_unload_entry,
sensor:async_setup_entry, diagnostics:async_get_config_entry_diagnostics.
The Tibber HTTP seam is driven by replacing async_get_clientsession in the
config_flow and coordinator module namespaces with a scriptable fake session
(the stub raises RuntimeError, i.e. "no session"), so the real fetch and
validation code runs to its verdict.

Perturbations (one production line each; dry-run on a /tmp copy):
    delete `self._abort_if_unique_id_configured()` (config_flow.py:1002)
        -> duplicate_flow_aborted 1 -> 0
    change validate_tibber_token's `return "cannot_connect"` on 401/403
       to `return "ok"` (config_flow.py:355)
        -> user_step_error_on_invalid_auth 1 -> 0
    delete `entry.async_start_reauth(self.hass)` (coordinator.py:5510)
        -> reauth_flow_started_after_401s 1 -> 0
    delete `self._tibber_reauth_started = True` (coordinator.py:5509)
        -> reauth_flow_started_after_401s 1 -> 2 (two 401 polls)
    delete `await super().async_shutdown()` (coordinator.py:5015)
        -> coordinator_super_shutdown_called 1 -> 0
    change the `_LOGGER.error("Error updating Heat Pump Optimizer: ...")`
       at coordinator.py:4460 to `_LOGGER.debug`
        -> error_logs_during_5_failed_polls 6 -> 1 (finding D10-B1, down)
    move `_tibber_fetch_failed`'s `raise UpdateFailed(reason)` out of
       _fetch_tibber_prices's try/except (re-raise without re-entering)
        -> outage_cycles_after_5_polls 10 -> 5 (finding D10-B1, down)
    add Platform.DIAGNOSTICS to PLATFORM_LIST (__init__.py:85)
        -> diagnostics_in_platform_list 0 -> 1 (and the import fails)
    drop CONF_TIBBER_TOKEN from TO_REDACT (diagnostics.py:21)
        -> token_leak_occurrences 0 -> 1
    change DEFAULT_OPTIMIZATION_INTERVAL 30 -> 15 (const.py:1074)
        -> update_interval_default_seconds 1800 -> 900
"""

from __future__ import annotations

import os

# The thread pin, before anything that could import numpy (the coordinator
# does). Copied from tests/stress.py; without it a threaded BLAS inflates
# process CPU time by the thread factor.
for _var in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_var, "1")

import asyncio  # noqa: E402
import json  # noqa: E402
import logging  # noqa: E402
import resource  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import timedelta  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, ha_setup_entry, ha_unload_entry  # noqa: E402

import heatpump_optimizer as integ  # noqa: E402
from heatpump_optimizer import config_flow, const, coordinator as coord_mod  # noqa: E402
from heatpump_optimizer import diagnostics, sensor  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from homeassistant.helpers import update_coordinator as uc  # noqa: E402

DOMAIN = const.DOMAIN
DATA = {
    const.CONF_TIBBER_TOKEN: "SECRET-TOKEN-d10b",
    const.CONF_WEATHER_ENTITY: "weather.home",
    const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_a",
}


def result(name: str, value, unit: str = "count") -> None:
    print(f"RESULT {name}={value} {unit}")


# --------------------------------------------------------------------------
# Fake HTTP seam: async_get_clientsession replacement + scripted responses.
# --------------------------------------------------------------------------
class FakeResponse:
    def __init__(self, status: int, payload: dict | None = None) -> None:
        self.status = status
        self._payload = payload

    async def json(self):
        return self._payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class FakeSession:
    """A one-shot script of responses; each post() consumes the next entry.

    An entry that is an Exception is raised (connect failure), anything else
    is returned as the response status with an optional JSON payload.
    """

    def __init__(self, script) -> None:
        self._script = list(script)
        self.posts = 0

    def post(self, *args, **kwargs):
        self.posts += 1
        entry = self._script.pop(0)
        if isinstance(entry, Exception):
            raise entry
        status, payload = entry
        return FakeResponse(status, payload)

    async def close(self):
        return None


def install_session(module, session: FakeSession):
    """Point a production module's async_get_clientsession at the fake."""
    real = getattr(module, "async_get_clientsession")
    module.async_get_clientsession = lambda hass, verify_ssl=True: session
    return real


TIBBER_OK = {
    "data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": {
        "today": [{"total": 0.42, "startsAt": "2026-09-02T00:00:00Z",
                   "level": "NORMAL"}],
        "tomorrow": [],
    }}}]}}
}


# --------------------------------------------------------------------------
# appropriate-polling: capture the update_interval super().__init__) receives.
# --------------------------------------------------------------------------
_INIT_KWARGS: dict = {}
_orig_duc_init = uc.DataUpdateCoordinator.__init__


def _spy_init(self, *args, **kwargs):
    _INIT_KWARGS.clear()
    _INIT_KWARGS.update(kwargs)
    _orig_duc_init(self, *args, **kwargs)


uc.DataUpdateCoordinator.__init__ = _spy_init


def make_coordinator(hass=None, extra_config=None) -> HeatPumpOptimizerCoordinator:
    entry = FakeEntry(data={**DATA, **(extra_config or {})})
    return HeatPumpOptimizerCoordinator(hass or FakeHass(), entry)


# --------------------------------------------------------------------------
# unique-config-entry + test-before-configure (real validate, fake session).
# --------------------------------------------------------------------------
async def run_step(flow, step, answers):
    try:
        return await getattr(flow, step)(dict(answers))
    except Exception as err:  # noqa: BLE001 - AbortFlow, as the manager would
        reason = getattr(err, "reason", None)
        if reason is None:
            raise
        return {"type": "abort", "reason": reason}


def flow_with(hass):
    handler = config_flow.HeatPumpOptimizerConfigFlow()
    handler.hass = hass
    return handler


async def measure_user_step() -> tuple[int, int, int, int]:
    first_screen = {
        "name": "Heat Pump Optimizer",
        const.CONF_TIBBER_TOKEN: "tok-a",
        const.CONF_WEATHER_ENTITY: "weather.home",
        const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_a",
    }
    # The same real validate_tibber_token answers every poll: one 200 (the
    # first, accepted flow), then a 401 and a connect failure for the
    # failure-branch runs.
    session = FakeSession(
        [(200, TIBBER_OK), (200, TIBBER_OK), (200, TIBBER_OK),
         (401, None), OSError("router rebooting")]
    )
    real = install_session(config_flow, session)
    try:
        hass = FakeHass()
        first = flow_with(hass)
        first_result = await run_step(first, "async_step_user", first_screen)
        # What the flow manager does when the first flow finishes: an entry
        # holding the flow's unique id.
        existing = FakeEntry(data=dict(first_screen))
        existing.entry_id = "d10b_existing"
        existing.unique_id = getattr(first, "unique_id", None)
        hass.config_entries.entries.append(existing)

        duplicate = await run_step(flow_with(hass), "async_step_user", first_screen)
        duplicate_aborted = int(
            first_result.get("type") == "form"
            and duplicate.get("type") == "abort"
            and duplicate.get("reason") == "already_configured"
        )
        other = await run_step(
            flow_with(hass),
            "async_step_user",
            {**first_screen, const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_b"},
        )
        distinct_proceeds = int(
            other.get("type") == "form" and other.get("step_id") == "temperature"
        )

        # Failure branches of the same user step, real validate code.
        invalid = flow_with(FakeHass())
        invalid_result = await run_step(invalid, "async_step_user", first_screen)
        invalid_shown = int(
            invalid_result.get("type") == "form"
            and invalid_result.get("step_id") == "user"
            and invalid_result.get("errors", {}).get(const.CONF_TIBBER_TOKEN)
            == "invalid_tibber_token"
        )
        connect = flow_with(FakeHass())
        connect_result = await run_step(connect, "async_step_user", first_screen)
        connect_shown = int(
            connect_result.get("type") == "form"
            and connect_result.get("step_id") == "user"
            and connect_result.get("errors", {}).get(const.CONF_TIBBER_TOKEN)
            == "cannot_connect"
        )
    finally:
        config_flow.async_get_clientsession = real
    return duplicate_aborted, distinct_proceeds, invalid_shown, connect_shown


# --------------------------------------------------------------------------
# reauthentication-flow: 401 during the update + the confirm steps.
# --------------------------------------------------------------------------
class ReauthEntry(FakeEntry):
    """FakeEntry plus the reauth-start hook HA's ConfigEntry carries."""

    def __init__(self, *a, **k) -> None:
        super().__init__(*a, **k)
        self.reauth_calls = 0
        self.reloads = 0

    def async_start_reauth(self, hass):
        self.reauth_calls += 1
        return True

    async def async_reload(self, entry_id):
        self.reloads += 1
        return True


async def _no_fetch_side(*_a, **_k):
    return None


def _no_side(*_a, **_k):
    # Production calls these WITHOUT await (they are sync methods).
    return None


def make_update_coordinator(entry: ReauthEntry):
    coord = HeatPumpOptimizerCoordinator(FakeHass(), entry)
    # Mirror what HA 2024.6's DataUpdateCoordinator.__init__ does by
    # inference (self.config_entry = config_entries.current_entry.get()):
    # the coordinator itself never passes config_entry to super().__init__,
    # so the attribute only exists via that inference.
    coord.config_entry = entry
    # Keep the cycle about the fetch: everything after it is patched out.
    for name in (
        "_update_current_state", "_fetch_weather_forecast",
        "_fetch_solar_forecast", "_async_learn_price_shape",
        "_apply_action", "_command_frequency", "_async_drive_pumps",
        "_async_save_accuracy", "_async_save_energy_totals",
        "_async_watch_learning_drift",
    ):
        setattr(coord, name, _no_fetch_side)
    for name in ("_record_accuracy", "_track_realised_peak"):
        setattr(coord, name, _no_side)
    coord._mode = const.MODE_OFF
    return coord


async def _drive_polls(coord, session_script) -> None:
    session = FakeSession(session_script)
    real = install_session(coord_mod, session)
    try:
        await coord._async_update_data()
    except Exception:  # noqa: BLE001 - UpdateFailed is the expected outcome
        pass
    finally:
        coord_mod.async_get_clientsession = real


async def measure_reauth() -> tuple[int, int, int, int]:
    entry = ReauthEntry(data=dict(DATA), entry_id="d10b_reauth")
    hass = FakeHass()
    hass.config_entries.entries.append(entry)
    coord = make_update_coordinator(entry)

    # Two 401 polls: the flow must start once, not twice.
    await _drive_polls(coord, [(401, None), (401, None)])
    started = entry.reauth_calls

    # Without the config_entry link (what the bare stub gives), nothing starts.
    entry2 = ReauthEntry(data=dict(DATA), entry_id="d10b_reauth_nolink")
    coord2 = make_update_coordinator(entry2)
    del coord2.config_entry
    await _drive_polls(coord2, [(401, None)])
    unlinked = entry2.reauth_calls

    # The reauth entry point resolves the entry, then the confirm step with
    # a good token: entry updated, reload, abort.
    session = FakeSession([(200, TIBBER_OK)])
    real = install_session(config_flow, session)
    try:
        flow = flow_with(hass)
        await run_step(flow, "async_step_reauth", {})
        fixed = await flow.async_step_reauth_confirm(
            {const.CONF_TIBBER_TOKEN: "brand-new-token"}
        )
    finally:
        config_flow.async_get_clientsession = real
    fixed_ok = int(
        fixed.get("type") == "abort"
        and fixed.get("reason") == "reauth_successful"
        and entry.data[const.CONF_TIBBER_TOKEN] == "brand-new-token"
        and entry.entry_id in hass.config_entries.reloaded
    )
    # The reauth steps themselves exist as flow handlers.
    steps_present = sum(
        hasattr(config_flow.HeatPumpOptimizerConfigFlow, name)
        for name in ("async_step_reauth", "async_step_reauth_confirm")
    )
    return started, unlinked, fixed_ok, steps_present


# --------------------------------------------------------------------------
# config-entry-unloading: setup -> unload -> reload, count survivors.
# --------------------------------------------------------------------------
async def measure_unload() -> dict:
    hass = FakeHass()
    entry = FakeEntry(data=dict(DATA), entry_id="d10b_unload")
    forwarded: list = []
    real_unload_platforms = hass.config_entries.async_unload_platforms

    async def record_unload_platforms(entry_, platforms):
        forwarded.append(list(platforms))
        return await real_unload_platforms(entry_, platforms)

    hass.config_entries.async_unload_platforms = record_unload_platforms

    ok_setup = await ha_setup_entry(integ, hass, entry)
    coord = entry.runtime_data
    coord.data = {"mode": "auto", "current_price": 0.5}  # exercise handover
    ok_unload = await ha_unload_entry(integ, hass, entry)

    pending_tasks = len([t for t in coord._background_tasks if getattr(t, "done", lambda: False)() is False and t is not None])
    unsub_left = sum(
        getattr(coord, name) is not None
        for name in ("_unsub_timer", "_unsub_ecl110_state", "_unsub_peak_guard", "_unsub_defrost")
    )
    on_unload_left = len(getattr(entry, "_on_unload", []))
    leak = pending_tasks + unsub_left + on_unload_left

    handover_after_unload = len(integ._plan_handovers(hass))
    ok_reload = await ha_setup_entry(integ, hass, entry)
    handover_after_reload = len(integ._plan_handovers(hass))
    new_coordinator = int(entry.runtime_data is not coord)

    return {
        "setup_ok": int(ok_setup),
        "unload_ok": int(ok_unload),
        "platforms_forwarded": len(forwarded[0]) if forwarded else 0,
        "super_shutdown": int(getattr(coord, "base_shutdown_called", False)),
        "leak": leak,
        "handover_after_unload": handover_after_unload,
        "reload_ok": int(ok_reload),
        "handover_after_reload": handover_after_reload,
        "new_coordinator": new_coordinator,
    }


# --------------------------------------------------------------------------
# entity-unavailable: the real sensor roster over a real coordinator.
# --------------------------------------------------------------------------
# A representative published payload: every key here is one a sensor is
# named for (the removal test pops them one at a time).
PUBLISHED = {
    "mode": "auto",
    "optimization_status": "optimal",
    "predicted_savings": 12.5,
    "savings_percentage": 8.3,
    "predicted_cost": 141.2,
    "baseline_cost": 153.7,
    "current_price": 0.42,
    "current_setpoint": 21.0,
    "current_power": 2.5,
    "measured_cop": 3.1,
    "indoor_temperature": 21.3,
    "outdoor_temperature": 3.4,
    "solar_irradiance": 120.0,
    "next_optimization": "2026-09-02T12:30:00+00:00",
    "last_optimization": "2026-09-02T12:00:00+00:00",
    "measured_power": 2.4,
    "reading_ok": {
        "indoor_temp_entity": True,
        "outdoor_temp_entity": True,
    },
    "current_action": {"power": 2.5, "setpoint": 21.0, "mode": "auto"},
}


async def sensor_roster(coord):
    hass = FakeHass()
    entry = FakeEntry(data=dict(DATA), entry_id="d10b_entities")
    entry.runtime_data = coord
    added: list = []
    await sensor.async_setup_entry(hass, entry, added.extend)
    return added


def native_of(entity):
    try:
        return entity.native_value
    except Exception:  # noqa: BLE001 - a roster member that cannot read
        return "<raises>"


async def measure_entities() -> dict:
    coord = make_coordinator()
    roster = await sensor_roster(coord)

    # 1. Failed coordinator update: every sensor goes unavailable.
    coord.data = dict(PUBLISHED)
    coord.last_update_success = True
    before_unavailable = sum(not e.available for e in roster)
    coord.last_update_success = False  # what the base class does on UpdateFailed
    after_unavailable = sum(not e.available for e in roster)

    # 2. Partial-missing: pop each key, the sensor named for it must go
    #    unknown (None), not keep publishing the old value. A candidate that
    #    publishes None with data entirely empty reads some OTHER fresh key
    #    (e.g. current_action) -- a mapping artefact of this metric, not a
    #    stale publish -- so it is verified against the empty payload.
    coord.last_update_success = True
    stale = []
    for key, value in list(PUBLISHED.items()):
        if key == "reading_ok":
            continue
        coord.data = {k: v for k, v in PUBLISHED.items() if k != key}
        for e in roster:
            if getattr(e, "_key", None) != key:
                continue
            now = native_of(e)
            if now == value and now is not None:
                coord.data = {}
                still = native_of(e)
                coord.data = {k: v for k, v in PUBLISHED.items() if k != key}
                if still is not None:
                    stale.append(f"{type(e).__name__}:{key}")
    coord.data = {}

    # 3. No data at all: which sensors still publish something?
    publishing_when_empty = [
        f"{type(e).__name__}={native_of(e)!r}"
        for e in roster
        if native_of(e) is not None
    ]
    return {
        "total": len(roster),
        "unavailable_before": before_unavailable,
        "unavailable_after_failure": after_unavailable,
        "stale_count": len(stale),
        "stale_list": stale,
        "publishing_when_empty": publishing_when_empty,
    }


# --------------------------------------------------------------------------
# log-when-unavailable: 5 failed polls, then 1 recovery, count records.
# --------------------------------------------------------------------------
class Capture(logging.Handler):
    def __init__(self) -> None:
        super().__init__(level=logging.DEBUG)
        self.records: list[tuple[int, str]] = []

    def emit(self, record: logging.LogRecord) -> None:
        if "heatpump_optimizer" in record.name:
            self.records.append((record.levelno, record.getMessage()))


async def measure_outage_logs() -> dict:
    entry = ReauthEntry(data=dict(DATA), entry_id="d10b_logs")
    coord = make_update_coordinator(entry)

    capture = Capture()
    root = logging.getLogger()
    root.addHandler(capture)
    root.setLevel(logging.DEBUG)
    try:
        for _ in range(5):
            await _drive_polls(coord, [(500, None)])
        outage_errors = [m for lvl, m in capture.records if lvl >= logging.ERROR]
        outage_all = list(capture.records)
        # Read the latch BEFORE the recovery poll resets it.
        cycles = getattr(coord, "_tibber_outage_cycles", None)
        capture.records.clear()
        await _drive_polls(coord, [(200, TIBBER_OK)])
        recovery = list(capture.records)
    finally:
        root.removeHandler(capture)

    recovered_msg = next(
        (m for lvl, m in recovery if "recovered" in m), ""
    )
    return {
        "error_count_outage": len(outage_errors),
        "error_samples": outage_errors[:3],
        "total_records_outage": len(outage_all),
        "info_count_recovery": sum(
            1 for lvl, _ in recovery if lvl == logging.INFO
        ),
        "error_count_recovery": sum(
            1 for lvl, _ in recovery if lvl >= logging.ERROR
        ),
        "outage_cycles": cycles,
        "recovered_msg": recovered_msg,
    }


# --------------------------------------------------------------------------
# diagnostics: platform list, payload keys, redaction.
# --------------------------------------------------------------------------
async def measure_diagnostics() -> dict:
    in_platforms = sum(
        1 for p in integ.PLATFORM_LIST if "diagnostics" in str(getattr(p, "value", p))
    )
    entry = FakeEntry(
        data={
            **DATA,
            const.CONF_INDOOR_TEMP_ENTITY: "sensor.room",
            "optimization_interval": 30,
        },
        options={"comfort_weight": 1.5},
        entry_id="d10b_diag",
    )
    hass = FakeHass()
    coord = make_coordinator(hass)
    coord.data = {"current_price": 0.42}
    entry.runtime_data = coord
    payload = await diagnostics.async_get_config_entry_diagnostics(hass, entry)
    dumped = json.dumps(payload, default=str)
    leak = dumped.count(DATA[const.CONF_TIBBER_TOKEN])
    sensitive = [k for k in entry.data if "token" in k]
    return {
        "in_platforms": in_platforms,
        "keys": sorted(payload.keys()),
        "token_leak": leak,
        "to_redact": len(diagnostics.TO_REDACT),
        "sensitive_candidates": len(sensitive),
    }


# --------------------------------------------------------------------------
async def main() -> None:
    # A sink handler on the root logger for the whole run: without one the
    # lastResort handler prints every ERROR the reauth/ooutage sections
    # provoke, burying the RESULT lines. measure_outage_logs attaches its
    # own counting handler.
    sink = logging.Handler()
    sink.emit = lambda record: None
    logging.getLogger().addHandler(sink)
    process_start, thread_start = time.process_time(), time.thread_time()

    # appropriate-polling (construction under the spy installed above)
    make_coordinator()
    default_interval = _INIT_KWARGS.get("update_interval")
    make_coordinator(extra_config={const.CONF_OPTIMIZATION_INTERVAL: 15})
    configured_interval = _INIT_KWARGS.get("update_interval")
    result(
        "update_interval_default_seconds",
        int(default_interval.total_seconds()) if default_interval else -1,
        "s",
    )
    result(
        "update_interval_configured_seconds",
        int(configured_interval.total_seconds()) if configured_interval else -1,
        "s",
    )

    dup, distinct, invalid, connect = await measure_user_step()
    result("duplicate_flow_aborted", dup, "bool")
    result("distinct_flow_proceeds", distinct, "bool")
    result("user_step_error_on_invalid_auth", invalid, "bool")
    result("user_step_error_on_cannot_connect", connect, "bool")

    started, unlinked, fixed_ok, steps = await measure_reauth()
    result("reauth_flow_started_after_two_401s", started)
    result("reauth_started_without_entry_link", unlinked)
    result("reauth_confirm_fixes_entry", fixed_ok, "bool")
    result("reauth_steps_present", steps)

    unload = await measure_unload()
    for name in ("setup_ok", "unload_ok", "platforms_forwarded",
                 "super_shutdown", "leak", "handover_after_unload",
                 "reload_ok", "handover_after_reload", "new_coordinator"):
        result(f"unload_{name}", unload[name])

    entities = await measure_entities()
    result("sensors_total", entities["total"])
    result("sensors_unavailable_before_failure", entities["unavailable_before"])
    result("sensors_unavailable_after_failure", entities["unavailable_after_failure"])
    result("stale_publishers_after_key_removal", entities["stale_count"])
    print(f"note stale_list={entities['stale_list']}")
    print(f"note publishing_when_empty={entities['publishing_when_empty']}")

    logs = await measure_outage_logs()
    result("error_logs_during_5_failed_polls", logs["error_count_outage"])
    result("total_log_records_during_outage", logs["total_records_outage"])
    result("info_logs_at_recovery", logs["info_count_recovery"])
    result("error_logs_at_recovery", logs["error_count_recovery"])
    result("outage_cycles_after_5_polls", logs["outage_cycles"])
    print(f"note error_samples={logs['error_samples']}")
    print(f"note recovered_msg={logs['recovered_msg']!r}")

    diag = await measure_diagnostics()
    result("diagnostics_in_platform_list", diag["in_platforms"])
    result("diagnostics_top_level_keys", "+".join(diag["keys"]))
    result("diagnostics_top_level_key_count", len(diag["keys"]))
    result("token_leak_occurrences", diag["token_leak"])
    result("redacted_field_count", diag["to_redact"])
    result("sensitive_candidate_count", diag["sensitive_candidates"])

    process_cpu = time.process_time() - process_start
    thread_cpu = time.thread_time() - thread_start
    result("thread_factor", f"{process_cpu / thread_cpu:.3f}" if thread_cpu else "nan", "ratio")
    result("load1", f"{os.getloadavg()[0]:.2f}", "load")
    result("swapins", resource.getrusage(resource.RUSAGE_SELF).ru_nswap, "count")


if __name__ == "__main__":
    asyncio.run(main())
