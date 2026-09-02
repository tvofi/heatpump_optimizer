"""The initial config flow, walked end to end with real validation (#194).

    PYTHONPATH=tests/hastub python tests/config_flow_steps.py
    PYTHONPATH=tests/hastub python tests/config_flow_steps.py --self-check

What this catches that nothing else in the suite does (issue #194, tranche
1): the nine-step initial flow had its screens fingerprinted by
``tests/golden.py`` and its first three steps probed one at a time by
``tests/entities.py`` (user, temperature, building_describe -- the token
verdict stubbed to "ok" wherever it mattered), but no test ever submitted
an answer past the questionnaire: ``building_extras``, ``thermal``,
``zones``, ``dhw`` and ``weather_sensitivity`` were never submitted to
anywhere in the suite, no initial flow was ever walked to
``create_entry``, and the token verdict branches (``invalid_tibber_token``,
``cannot_connect``) were never asserted through the flow at all.  A step
whose handler stopped calling the next one, a validator that stopped
firing, the accumulated ``_data`` losing a page's answers on the way to
``create_entry`` -- all of it would have shipped green.

This driver walks both paths through the flow, questionnaire and expert,

    user -> temperature -> building (menu)
      -> building_describe -> building_extras -> dhw -> weather_sensitivity
      -> thermal -> zones -> dhw -> weather_sensitivity
    -> create_entry

asserting at every hop the next step_id and the data accumulated so far,
then probes each step's INVALID inputs through the validation code that
really runs (``comfort_band.errors``, ``_power_errors``, the DHW window
grammar), and drives the two credential behaviours end to end -- the
duplicate-entry abort and the reauth round trip -- through the fake Tibber
session seam the round-2 D10-B harness used: the REAL
``validate_tibber_token`` runs to its verdict against scripted HTTP
responses, so the branches pinned are the production ones, not a stub's.

``--self-check`` is the mutation-proof mode (tests/README.md): it breaks
the duplicate guard and the token probe in-memory, one at a time, and
fails unless the checks that are supposed to catch each breakage really
fail.  Normal mode must pass on an unmodified tree; the self-check must
fail on the broken one.

Expected (tolerance 0): every RESULT line reads full coverage --
``flow_checks_covered=<checks>`` with no failures, every step
``happy=P/P error_branches=P/P``, ``reauth_round_trips=1``,
``duplicate_aborts=1``.  Baseline measured: 87645f8, re-verified
identical at 6d83f0b (the merge base; ``config_flow.py`` is byte-identical
between the two), MacBookAir10,1; every number here is a count, immune to
box load.
"""
from __future__ import annotations

import os

# The thread pin, before anything that could import numpy. Copied from
# tests/stress.py; without it a threaded BLAS inflates process CPU time by
# the thread factor, and the audit harness contract measures that ratio.
for _var in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_var, "1")

import asyncio  # noqa: E402
import logging  # noqa: E402
import sys  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "custom_components",
    ),
)

import voluptuous as vol  # noqa: E402

from harness import FakeEntry, FakeHass, Results  # noqa: E402

from heatpump_optimizer import config_flow, const  # noqa: E402
from heatpump_optimizer.presets import (  # noqa: E402
    EMITTER_FLOOR,
    EMITTER_RADIATORS,
    ERA_1980_2005,
    FOUNDATION_NONE,
    STRUCTURE_TIMBER_SLAB,
)
from homeassistant.data_entry_flow import AbortFlow  # noqa: E402

R = Results("Initial config flow, walked end to end")

# The first-screen answers both walks start from. Three required fields and
# one identity-bearing optional one, so the duplicate section has a real
# plant identity to collide on.
FIRST_SCREEN = {
    "name": "Heat Pump Optimizer",
    const.CONF_TIBBER_TOKEN: "tok-a",
    const.CONF_WEATHER_ENTITY: "weather.home",
    const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_a",
}

# Valid answers for every form step, at the defaults the forms themselves
# pre-fill. One dict per step so a probe can override a single field and
# still submit an otherwise-valid page.
TEMPERATURE_ANSWERS = {
    const.CONF_TARGET_TEMP: 21.0,
    const.CONF_MIN_TEMP: 19.0,
    const.CONF_MAX_TEMP: 23.0,
    const.CONF_COMFORT_TEMP_DAY: 21.0,
    const.CONF_COMFORT_TEMP_NIGHT: 19.5,
    const.CONF_DAY_START_HOUR: 7,
    const.CONF_DAY_END_HOUR: 22,
}
QUESTIONNAIRE_ANSWERS = {
    const.CONF_BUILDING_STRUCTURE: STRUCTURE_TIMBER_SLAB,
    const.CONF_BUILDING_ERA: ERA_1980_2005,
    const.CONF_BUILDING_FOUNDATION: FOUNDATION_NONE,
    const.CONF_HEATED_AREA: 140.0,
    const.CONF_UPPER_EMITTER: EMITTER_RADIATORS,
    const.CONF_LOWER_EMITTER: EMITTER_FLOOR,
}
EXTRAS_ANSWERS = {
    const.CONF_HEAT_PUMP_COP_NOMINAL: 3.5,
    const.CONF_HEAT_PUMP_MAX_POWER: 5.0,
    const.CONF_HEAT_PUMP_MIN_POWER: 1.0,
}
THERMAL_ANSWERS = {
    const.CONF_HOUSE_THERMAL_MASS: 10.0,
    const.CONF_HOUSE_HEAT_LOSS_COEFFICIENT: 0.15,
    const.CONF_SLAB_THERMAL_MASS: 5.0,
    const.CONF_SLAB_HEAT_TRANSFER: 0.8,
    const.CONF_HEAT_PUMP_COP_NOMINAL: 3.5,
    const.CONF_HEAT_PUMP_MAX_POWER: 5.0,
    const.CONF_HEAT_PUMP_MIN_POWER: 1.0,
    const.CONF_OPTIMIZATION_INTERVAL: 30,
    const.CONF_PRICE_WEIGHT: 1.0,
    const.CONF_COMFORT_WEIGHT: 5.0,
}
ZONES_ANSWERS = {
    const.CONF_UPPER_FLOOR_THERMAL_MASS: 4.0,
    const.CONF_LOWER_FLOOR_THERMAL_MASS: 3.0,
    const.CONF_INTER_ZONE_TRANSFER: 0.1,
}
# The legionella pair is deliberately a warning case: 60 °C cycle over a
# 52 °C charge limit is legitimate and must PROCEED, with the warning in
# the log -- that is a real branch of the dhw handler, counted in the
# ledger like the errors beside it.
DHW_ANSWERS = {
    const.CONF_DHW_TANK_VOLUME: 200.0,
    const.CONF_DHW_SETPOINT: 52.0,
    const.CONF_DHW_MIN_TEMP: 42.0,
    const.CONF_DHW_DAILY_CONSUMPTION: 200.0,
    const.CONF_DHW_COOLING_RATE: 0.2,
    const.CONF_DHW_SCHEDULE_ENABLED: True,
    const.CONF_DHW_WINDOWS: "weekdays 06:00-08:30",
    const.CONF_DHW_IDLE_MIN_TEMP: 20.0,
    const.CONF_DHW_LEGIONELLA_ENABLED: True,
    const.CONF_DHW_LEGIONELLA_TEMP: 60.0,
    const.CONF_DHW_LEGIONELLA_INTERVAL_DAYS: 14,
}
WEATHER_ANSWERS = {
    const.CONF_WIND_SENSITIVITY: 0.03,
    const.CONF_RAIN_HEAT_LOSS_MULTIPLIER: 1.15,
}


# ---------------------------------------------------------------------------
# The Tibber session seam: the real validate_tibber_token, scripted HTTP.
# Same shape as tools/audit/round2/D10/B/harness.py, so what this pins is
# the production verdict logic (401/403 vs errors payload vs connect
# failure), not a stub's.
# ---------------------------------------------------------------------------
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


class FakeSession:
    """A script of responses, one consumed per POST.

    An entry that is an Exception is raised (connect failure); anything
    else is returned as (status, json payload). When the script runs out,
    the last entry repeats -- an ok-responder for the happy walks, so they
    never depend on how many polls a page does.
    """

    def __init__(self, script):
        self._script = list(script)
        self.posts = 0

    def post(self, *args, **kwargs):
        self.posts += 1
        index = min(self.posts - 1, len(self._script) - 1)
        entry = self._script[index]
        if isinstance(entry, Exception):
            raise entry
        status, payload = entry
        return FakeResponse(status, payload)


TIBBER_VIEWER_OK = (200, {"data": {"viewer": {"name": "Home"}}})


def install_session(module, session):
    """Point a production module's async_get_clientsession at the fake."""
    real = getattr(module, "async_get_clientsession")
    module.async_get_clientsession = lambda hass, verify_ssl=True: session
    return real


def fresh_flow(hass=None, data=None):
    """A new initial flow on a new hass, optionally pre-seeded with data."""
    flow = config_flow.HeatPumpOptimizerConfigFlow()
    flow.hass = hass or FakeHass()
    if data:
        flow._data.update(data)
    return flow


async def submit(flow, step, answers):
    """Run one step with answers; an AbortFlow comes back as HA renders it.

    There is no flow manager in the stub, so the exception the real manager
    converts into an abort result is caught here instead -- exactly what
    tools/audit/round2/D10/B/harness.py and tests/entities.py do.
    """
    try:
        return await getattr(flow, f"async_step_{step}")(dict(answers))
    except AbortFlow as err:
        return {"type": "abort", "reason": err.reason}


# ---------------------------------------------------------------------------
# The coverage ledger: one row per step, happy checks and error branches.
# ---------------------------------------------------------------------------
class Ledger:
    def __init__(self):
        self.rows = {}

    def record(self, step, kind, name, ok):
        row = self.rows.setdefault(
            step, {"happy": [], "error": [], "happy_ok": 0, "error_ok": 0}
        )
        row[kind].append(name)
        row[f"{kind}_ok"] += int(bool(ok))

    def print_result_lines(self):
        steps = {k: v for k, v in self.rows.items() if not k.startswith("_")}
        total_ok = sum(r["happy_ok"] + r["error_ok"] for r in steps.values())
        total = sum(len(r["happy"]) + len(r["error"]) for r in steps.values())
        print(f"RESULT flow_checks_covered={total_ok}/{total} checks")
        for step in (
            "user",
            "temperature",
            "building",
            "building_describe",
            "building_extras",
            "thermal",
            "zones",
            "dhw",
            "weather_sensitivity",
            "reauth_confirm",
        ):
            row = steps.get(step)
            row = self.rows.get(step, {"happy": [], "error": [], "happy_ok": 0, "error_ok": 0})
            happy = f"{row['happy_ok']}/{len(row['happy'])}"
            errors = f"{row['error_ok']}/{len(row['error'])}"
            print(f"RESULT step_{step} happy={happy} error_branches={errors}")
        print(f"RESULT reauth_round_trips={self.rows.get('_reauth', 0)}")
        print(f"RESULT duplicate_aborts={self.rows.get('_dup', 0)}")


LEDGER = Ledger()


def check(step, kind, name, condition, detail=""):
    """One ledgered check: recorded per step, and pass/fail for the suite."""
    LEDGER.record(step, kind, name, condition)
    return R.check(name, condition, detail)


def shows(result, step_id):
    """The result is a form for this step (or a menu, for menu steps)."""
    if result.get("type") == "menu":
        return step_id == "building"
    return result.get("type") == "form" and result.get("step_id") == step_id


# ---------------------------------------------------------------------------
# user: the credential screen. Token verdicts through the real validate.
# ---------------------------------------------------------------------------
async def user_error_branches():
    R.section("user: refused and unreachable tokens, required fields")
    real = install_session(config_flow, FakeSession([TIBBER_VIEWER_OK]))

    # invalid_auth: Tibber answers 401. The user must be told the TOKEN is
    # wrong, on the same screen, with nothing stored.
    refused = fresh_flow()
    config_flow.async_get_clientsession = lambda hass, verify_ssl=True: FakeSession(
        [(401, None)]
    )
    result = await submit(refused, "user", FIRST_SCREEN)
    check(
        "user",
        "error",
        "a 401 re-shows the first screen with invalid_tibber_token",
        shows(result, "user")
        and result.get("errors", {}).get(const.CONF_TIBBER_TOKEN)
        == "invalid_tibber_token",
        str(result.get("errors")),
    )
    check(
        "user",
        "error",
        "a refused token stores nothing",
        not refused._data,
        str(sorted(refused._data)),
    )

    # cannot_connect: the POST raises. A network failure must NOT call the
    # token invalid -- that message sends the user to retype a correct
    # token and fixes nothing.
    unreachable = fresh_flow()
    config_flow.async_get_clientsession = lambda hass, verify_ssl=True: FakeSession(
        [OSError("router rebooting")]
    )
    result = await submit(unreachable, "user", FIRST_SCREEN)
    check(
        "user",
        "error",
        "a connect failure shows cannot_connect, not invalid_tibber_token",
        shows(result, "user")
        and result.get("errors", {}).get(const.CONF_TIBBER_TOKEN)
        == "cannot_connect",
        str(result.get("errors")),
    )

    # The errors payload Tibber answers a bad token with, on HTTP 200.
    errors_payload = fresh_flow()
    config_flow.async_get_clientsession = lambda hass, verify_ssl=True: FakeSession(
        [(200, {"errors": [{"message": "bad token"}]})]
    )
    result = await submit(errors_payload, "user", FIRST_SCREEN)
    check(
        "user",
        "error",
        "an errors payload on HTTP 200 is an invalid token too",
        shows(result, "user")
        and result.get("errors", {}).get(const.CONF_TIBBER_TOKEN)
        == "invalid_tibber_token",
        str(result.get("errors")),
    )

    # The declared schema refuses a first screen with no token / no weather
    # entity at all: the entity pickers are optional, the identity fields
    # are not. In Home Assistant voluptuous runs this before the handler.
    form = await fresh_flow().async_step_user(None)
    try:
        form["data_schema"]({"name": "x", "weather_entity": "weather.home"})
        rejected = False
    except vol.Invalid:
        rejected = True
    try:
        form["data_schema"]({"name": "x", "tibber_token": "t"})
        weather_rejected = False
    except vol.Invalid:
        weather_rejected = True
    check(
        "user",
        "error",
        "the first-screen schema requires the token and the weather entity",
        rejected and weather_rejected,
        f"token={rejected} weather={weather_rejected}",
    )

    config_flow.async_get_clientsession = real


# ---------------------------------------------------------------------------
# duplicate: same plant twice aborts, a second pump proceeds (null control).
# ---------------------------------------------------------------------------
async def duplicate_and_null_control():
    R.section("user: the same plant twice, a second pump once")
    real = install_session(config_flow, FakeSession([TIBBER_VIEWER_OK]))
    hass = FakeHass()

    first = fresh_flow(hass)
    result = await submit(first, "user", FIRST_SCREEN)
    check(
        "user",
        "happy",
        "a valid first screen proceeds to the temperature step",
        shows(result, "temperature"),
        str(result)[:120],
    )
    check(
        "user",
        "happy",
        "and carries the plant identity as the flow's unique id",
        bool(first.unique_id),
        repr(first.unique_id),
    )

    # What the flow manager does when that flow finishes: an entry holding
    # the flow's unique id.
    hass.config_entries.entries.append(
        FakeEntry(data=dict(FIRST_SCREEN), entry_id="first", unique_id=first.unique_id)
    )
    duplicate = await submit(fresh_flow(hass), "user", FIRST_SCREEN)
    dup_aborted = duplicate == {"type": "abort", "reason": "already_configured"}
    check(
        "user",
        "error",
        "the same answers a second time abort as already_configured",
        dup_aborted,
        str(duplicate)[:120],
    )

    # Null control: one different entity slot is a different plant -- a
    # second heat pump must go through.
    distinct = await submit(
        fresh_flow(hass),
        "user",
        {**FIRST_SCREEN, const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_b"},
    )
    check(
        "user",
        "happy",
        "a second heat pump on the same account proceeds (null control)",
        shows(distinct, "temperature"),
        str(distinct)[:120],
    )

    LEDGER.rows["_dup"] = int(dup_aborted)
    config_flow.async_get_clientsession = real


# ---------------------------------------------------------------------------
# The questionnaire walk: building_describe -> building_extras.
# ---------------------------------------------------------------------------
async def walk_questionnaire():
    R.section("walk 1 (questionnaire): user through create_entry")
    real = install_session(config_flow, FakeSession([TIBBER_VIEWER_OK]))
    flow = fresh_flow()

    result = await submit(flow, "user", FIRST_SCREEN)
    check(
        "temperature",
        "happy",
        "the accepted first screen lands on temperature",
        shows(result, "temperature")
        and flow._data.get(const.CONF_TIBBER_TOKEN) == "tok-a"
        and flow._data.get(const.CONF_WEATHER_ENTITY) == "weather.home",
        str(result.get("step_id")),
    )

    result = await submit(flow, "temperature", TEMPERATURE_ANSWERS)
    check(
        "building",
        "happy",
        "a valid comfort band opens the building menu",
        result.get("type") == "menu"
        and result.get("step_id") == "building"
        and set(result.get("menu_options", {})) == {"building_describe", "thermal"},
        str(result)[:120],
    )
    check(
        "temperature",
        "happy",
        "the band answers are accumulated",
        flow._data.get(const.CONF_TARGET_TEMP) == 21.0
        and flow._data.get(const.CONF_DAY_START_HOUR) == 7,
        str({k: flow._data.get(k) for k in TEMPERATURE_ANSWERS}),
    )

    result = await submit(flow, "building_describe", QUESTIONNAIRE_ANSWERS)
    check(
        "building_describe",
        "happy",
        "the questionnaire proceeds to the heat pump extras",
        shows(result, "building_extras"),
        str(result.get("step_id")),
    )
    derived_present = [
        key
        for key in (
            const.CONF_HOUSE_THERMAL_MASS,
            const.CONF_HOUSE_HEAT_LOSS_COEFFICIENT,
            const.CONF_SLAB_THERMAL_MASS,
            const.CONF_SLAB_HEAT_TRANSFER,
        )
        if key in flow._data
    ]
    check(
        "building_describe",
        "happy",
        "the answers are stored and the physics derived from them",
        flow._data.get(const.CONF_BUILDING_PRESET_ENABLED) is True
        and len(derived_present) == 4,
        f"derived {derived_present}",
    )
    check(
        "building_describe",
        "happy",
        "a fresh questionnaire derives a single-zone model (no zone keys)",
        const.CONF_UPPER_FLOOR_THERMAL_MASS not in flow._data
        and const.CONF_LOWER_FLOOR_THERMAL_MASS not in flow._data,
        str(
            [
                k
                for k in (const.CONF_UPPER_FLOOR_THERMAL_MASS, const.CONF_LOWER_FLOOR_THERMAL_MASS)
                if k in flow._data
            ]
        ),
    )

    result = await submit(flow, "building_extras", EXTRAS_ANSWERS)
    check(
        "building_extras",
        "happy",
        "the nameplate numbers proceed to hot water",
        shows(result, "dhw"),
        str(result.get("step_id")),
    )

    # The dhw step's three errors and one warning, each on its own flow
    # seeded exactly as the walk had it, each still standing on dhw.
    seeded = lambda: fresh_flow(data={**FIRST_SCREEN, **TEMPERATURE_ANSWERS, **QUESTIONNAIRE_ANSWERS, **EXTRAS_ANSWERS, **derived_into(flow)})  # noqa: E731

    bad_spec = await submit(seeded(), "dhw", {**DHW_ANSWERS, const.CONF_DHW_WINDOWS: "garbage"})
    check(
        "dhw",
        "error",
        "an unparseable window spec is invalid_dhw_windows",
        shows(bad_spec, "dhw")
        and bad_spec.get("errors", {}).get(const.CONF_DHW_WINDOWS)
        == "invalid_dhw_windows",
        str(bad_spec.get("errors")),
    )
    too_short = await submit(
        seeded(), "dhw", {**DHW_ANSWERS, const.CONF_DHW_WINDOWS: "06:05-06:10"}
    )
    check(
        "dhw",
        "error",
        "a window shorter than one planning step is dhw_window_too_short",
        shows(too_short, "dhw")
        and too_short.get("errors", {}).get(const.CONF_DHW_WINDOWS)
        == "dhw_window_too_short",
        str(too_short.get("errors")),
    )
    too_close = await submit(
        seeded(),
        "dhw",
        {**DHW_ANSWERS, const.CONF_DHW_SETPOINT: 48.0, const.CONF_DHW_MIN_TEMP: 46.0},
    )
    check(
        "dhw",
        "error",
        "a minimum with no deadband below the setpoint is dhw_min_too_close",
        shows(too_close, "dhw")
        and too_close.get("errors", {}).get(const.CONF_DHW_MIN_TEMP)
        == "dhw_min_too_close",
        str(too_close.get("errors")),
    )

    # The legionella pair is a WARNING: 60 over 52 proceeds, and says so.
    warnings: list[str] = []

    class Capture(logging.Handler):
        def emit(self, record):
            warnings.append(record.getMessage().lower())

    logger = logging.getLogger("heatpump_optimizer.config_flow")
    logger.addHandler(Capture())
    try:
        result = await submit(flow, "dhw", DHW_ANSWERS)
    finally:
        logger.removeHandler(Capture())
    check(
        "dhw",
        "happy",
        "a valid hot-water page proceeds to weather sensitivity",
        shows(result, "weather_sensitivity"),
        str(result.get("step_id")),
    )
    check(
        "dhw",
        "error",
        "a legionella cycle above the charge limit proceeds with a warning",
        any("legionella" in w for w in warnings) and flow._data.get(const.CONF_DHW_SETPOINT) == 52.0,
        str(warnings[:1]),
    )

    result = await submit(flow, "weather_sensitivity", WEATHER_ANSWERS)
    entry_data = result.get("data", {})
    from_every_page = [
        key
        for key in (
            const.CONF_TIBBER_TOKEN,
            const.CONF_TARGET_TEMP,
            const.CONF_BUILDING_ERA,
            const.CONF_HOUSE_THERMAL_MASS,
            const.CONF_HEAT_PUMP_COP_NOMINAL,
            const.CONF_DHW_TANK_VOLUME,
            const.CONF_WIND_SENSITIVITY,
        )
        if key not in entry_data
    ]
    check(
        "weather_sensitivity",
        "happy",
        "the last page creates the entry under the chosen name",
        result.get("type") == "create_entry"
        and result.get("title") == "Heat Pump Optimizer",
        f"{result.get('type')} {result.get('title')!r}",
    )
    check(
        "weather_sensitivity",
        "happy",
        "the entry carries one answer from every page it walked",
        result.get("type") == "create_entry" and not from_every_page,
        f"missing {from_every_page}",
    )

    config_flow.async_get_clientsession = real


def derived_into(flow):
    """The keys the questionnaire's derivation wrote into this flow."""
    return {key: flow._data[key] for key in config_flow.DERIVED_THERMAL_KEYS if key in flow._data}


# ---------------------------------------------------------------------------
# The expert walk: thermal -> zones. Its own flow, its own error probes.
# ---------------------------------------------------------------------------
async def walk_expert():
    R.section("walk 2 (expert): thermal values and zones")
    real = install_session(config_flow, FakeSession([TIBBER_VIEWER_OK]))

    seeded = lambda: fresh_flow(  # noqa: E731
        data={**FIRST_SCREEN, **TEMPERATURE_ANSWERS}
    )

    # building_extras never runs on this path; its error is probed on a
    # flow seeded the way the questionnaire walk would have left it.
    extras_seeded = lambda: fresh_flow(  # noqa: E731
        data={**FIRST_SCREEN, **TEMPERATURE_ANSWERS, **QUESTIONNAIRE_ANSWERS}
    )
    inverted = await submit(
        extras_seeded(),
        "building_extras",
        {**EXTRAS_ANSWERS, const.CONF_HEAT_PUMP_MAX_POWER: 3.0, const.CONF_HEAT_PUMP_MIN_POWER: 6.0},
    )
    check(
        "building_extras",
        "error",
        "a modulation floor above the ceiling is min_power_above_max",
        shows(inverted, "building_extras")
        and inverted.get("errors", {}).get(const.CONF_HEAT_PUMP_MIN_POWER)
        == "min_power_above_max",
        str(inverted.get("errors")),
    )

    inverted = await submit(
        seeded(), "thermal", {**THERMAL_ANSWERS, const.CONF_HEAT_PUMP_MAX_POWER: 4.0, const.CONF_HEAT_PUMP_MIN_POWER: 8.0}
    )
    check(
        "thermal",
        "error",
        "the thermal page refuses the same inverted power pair",
        shows(inverted, "thermal")
        and inverted.get("errors", {}).get(const.CONF_HEAT_PUMP_MIN_POWER)
        == "min_power_above_max",
        str(inverted.get("errors")),
    )

    flow = seeded()
    result = await submit(flow, "thermal", THERMAL_ANSWERS)
    check(
        "thermal",
        "happy",
        "hand-typed thermal values proceed to the optional zones page",
        shows(result, "zones"),
        str(result.get("step_id")),
    )

    result = await submit(flow, "zones", ZONES_ANSWERS)
    check(
        "zones",
        "happy",
        "zone answers proceed to hot water",
        shows(result, "dhw"),
        str(result.get("step_id")),
    )
    check(
        "zones",
        "happy",
        "and the zone keys are accumulated",
        flow._data.get(const.CONF_UPPER_FLOOR_THERMAL_MASS) == 4.0,
        str(flow._data.get(const.CONF_UPPER_FLOOR_THERMAL_MASS)),
    )

    result = await submit(flow, "dhw", {**DHW_ANSWERS, const.CONF_DHW_LEGIONELLA_ENABLED: False})
    check(
        "dhw",
        "happy",
        "hot water without a legionella cycle proceeds too",
        shows(result, "weather_sensitivity"),
        str(result.get("step_id")),
    )
    result = await submit(flow, "weather_sensitivity", WEATHER_ANSWERS)
    check(
        "weather_sensitivity",
        "happy",
        "the expert path creates its entry with the thermal values",
        result.get("type") == "create_entry"
        and result.get("data", {}).get(const.CONF_HOUSE_THERMAL_MASS) == 10.0
        and result.get("data", {}).get(const.CONF_INTER_ZONE_TRANSFER) == 0.1,
        f"{result.get('type')} "
        f"{result.get('data', {}).get(const.CONF_HOUSE_THERMAL_MASS)}",
    )

    config_flow.async_get_clientsession = real


# ---------------------------------------------------------------------------
# temperature: every comfort-band contradiction, one field at a time.
# ---------------------------------------------------------------------------
async def temperature_error_branches():
    R.section("temperature: every comfort-band contradiction")
    # Each probe overrides fields so exactly ONE rule fires; the assertion
    # is on the whole errors dict, so a probe that also trips a second rule
    # fails here rather than quietly counting itself covered.
    probes = [
        (
            "min_above_target",
            {const.CONF_MIN_TEMP: 21.5, const.CONF_COMFORT_TEMP_DAY: 22.0, const.CONF_COMFORT_TEMP_NIGHT: 21.5},
            {const.CONF_MIN_TEMP: "min_above_target"},
        ),
        (
            "max_below_target",
            {const.CONF_MAX_TEMP: 20.5, const.CONF_COMFORT_TEMP_DAY: 20.0},
            {const.CONF_MAX_TEMP: "max_below_target"},
        ),
        (
            "night_above_day",
            {const.CONF_COMFORT_TEMP_NIGHT: 22.0},
            {const.CONF_COMFORT_TEMP_NIGHT: "night_above_day"},
        ),
        (
            "day_window_empty",
            {const.CONF_DAY_START_HOUR: 22},
            {const.CONF_DAY_END_HOUR: "day_window_empty"},
        ),
        (
            "comfort_outside_band (day)",
            {const.CONF_COMFORT_TEMP_DAY: 23.5},
            {const.CONF_COMFORT_TEMP_DAY: "comfort_outside_band"},
        ),
        (
            "comfort_outside_band (night)",
            {const.CONF_COMFORT_TEMP_NIGHT: 18.0},
            {const.CONF_COMFORT_TEMP_NIGHT: "comfort_outside_band"},
        ),
    ]
    for name, override, expected in probes:
        flow = fresh_flow(data={**FIRST_SCREEN})
        result = await submit(
            flow, "temperature", {**TEMPERATURE_ANSWERS, **override}
        )
        check(
            "temperature",
            "error",
            f"comfort band: {name} re-shows the page with exactly that error",
            shows(result, "temperature") and result.get("errors") == expected,
            f"got {result.get('errors')}, want {expected}",
        )
        check(
            "temperature",
            "error",
            f"comfort band: {name} stores nothing",
            const.CONF_TARGET_TEMP not in flow._data,
            str(sorted(flow._data)),
        )


# ---------------------------------------------------------------------------
# reauth: refused entry point, refused confirm, unreachable, then fixed.
# ---------------------------------------------------------------------------
async def reauth_round_trip():
    R.section("reauth: refused, unreachable, then fixed")
    hass = FakeHass()
    entry = FakeEntry(
        data={
            const.CONF_TIBBER_TOKEN: "stale-token",
            const.CONF_WEATHER_ENTITY: "weather.home",
        },
        entry_id="reauth-1",
    )
    hass.config_entries.entries.append(entry)
    flow = config_flow.HeatPumpOptimizerConfigFlow()
    flow.hass = hass
    # What the flow manager stamps on a reauth flow: the entry it repairs.
    flow.context = {"entry_id": "reauth-1"}

    result = await flow.async_step_reauth(entry.data)
    check(
        "reauth_confirm",
        "happy",
        "the reauth flow opens on a one-field confirm form",
        result.get("type") == "form"
        and result.get("step_id") == "reauth_confirm",
        f"{result.get('type')}/{result.get('step_id')}",
    )

    real = install_session(
        config_flow,
        FakeSession([(401, None), OSError("router rebooting"), TIBBER_VIEWER_OK]),
    )
    refused = await flow.async_step_reauth_confirm(
        {const.CONF_TIBBER_TOKEN: "stale-token"}
    )
    check(
        "reauth_confirm",
        "error",
        "the refused old token is invalid_tibber_token, not a network error",
        shows(refused, "reauth_confirm")
        and refused.get("errors", {}).get(const.CONF_TIBBER_TOKEN)
        == "invalid_tibber_token",
        str(refused.get("errors")),
    )
    unreachable = await flow.async_step_reauth_confirm(
        {const.CONF_TIBBER_TOKEN: "anything"}
    )
    check(
        "reauth_confirm",
        "error",
        "an unreachable Tibber is cannot_connect on the confirm form too",
        shows(unreachable, "reauth_confirm")
        and unreachable.get("errors", {}).get(const.CONF_TIBBER_TOKEN)
        == "cannot_connect",
        str(unreachable.get("errors")),
    )

    fixed = await flow.async_step_reauth_confirm(
        {const.CONF_TIBBER_TOKEN: "brand-new-token"}
    )
    round_trip_done = (
        fixed == {"type": "abort", "reason": "reauth_successful"}
        and entry.data[const.CONF_TIBBER_TOKEN] == "brand-new-token"
        and hass.config_entries.reloaded == ["reauth-1"]
    )
    check(
        "reauth_confirm",
        "happy",
        "a new token is written through, the entry reloads, reauth_successful",
        round_trip_done,
        f"{fixed} token={entry.data[const.CONF_TIBBER_TOKEN]} "
        f"reloaded={hass.config_entries.reloaded}",
    )
    LEDGER.rows["_reauth"] = int(round_trip_done)
    config_flow.async_get_clientsession = real


# ---------------------------------------------------------------------------
# --self-check: break production in memory, one behaviour at a time, and
# require the checks that guard each behaviour to fail. A check that cannot
# fail pins nothing (tests/README.md).
# ---------------------------------------------------------------------------
async def self_check():
    print("\n=== self-check: each mutation must break its named check ===")
    outcomes = []

    # Mutation 1: the duplicate guard is a no-op.
    real_guard = config_flow.HeatPumpOptimizerConfigFlow._abort_if_unique_id_configured
    config_flow.HeatPumpOptimizerConfigFlow._abort_if_unique_id_configured = (
        lambda self, *a, **k: None
    )
    try:
        real = install_session(config_flow, FakeSession([TIBBER_VIEWER_OK]))
        hass = FakeHass()
        first = fresh_flow(hass)
        await submit(first, "user", FIRST_SCREEN)
        hass.config_entries.entries.append(
            FakeEntry(data=dict(FIRST_SCREEN), entry_id="first", unique_id=first.unique_id)
        )
        duplicate = await submit(fresh_flow(hass), "user", FIRST_SCREEN)
        caught = duplicate != {"type": "abort", "reason": "already_configured"}
        outcomes.append(
            (
                "duplicate guard no-op",
                caught,
                "the same answers a second time abort as already_configured",
                str(duplicate)[:120],
            )
        )
        config_flow.async_get_clientsession = real
    finally:
        config_flow.HeatPumpOptimizerConfigFlow._abort_if_unique_id_configured = real_guard

    # Mutation 2: the token probe always says ok.
    real_validate = config_flow.validate_tibber_token

    async def always_ok(hass, token):
        return "ok"

    config_flow.validate_tibber_token = always_ok
    try:
        real = install_session(config_flow, FakeSession([(401, None)]))
        refused = fresh_flow()
        result = await submit(refused, "user", FIRST_SCREEN)
        caught = result.get("errors", {}).get(const.CONF_TIBBER_TOKEN) != "invalid_tibber_token"
        outcomes.append(
            (
                "token probe always ok",
                caught,
                "a 401 re-shows the first screen with invalid_tibber_token",
                str(result.get("errors")),
            )
        )
        config_flow.async_get_clientsession = real
    finally:
        config_flow.validate_tibber_token = real_validate

    ok = True
    for mutation, caught, check_name, detail in outcomes:
        print(
            f"  {'caught' if caught else 'MISSED'}  {mutation}"
            f"  ->  check {check_name!r}"
            + ("" if caught else f"  [{detail}]")
        )
        ok = ok and caught
    if not ok:
        print("\na mutation survived: a check that cannot fail pins nothing")
        return 1
    print("\nboth mutations caught by their named checks")
    return 0


async def main() -> int:
    if "--self-check" in sys.argv:
        return await self_check()

    # A sink for the one WARNING the dhw branch provokes, so the ledger's
    # output stays readable.
    sink = logging.Handler()
    sink.emit = lambda record: None
    logging.getLogger().addHandler(sink)

    await duplicate_and_null_control()
    await user_error_branches()
    await walk_questionnaire()
    await walk_expert()
    await temperature_error_branches()
    await reauth_round_trip()

    print()
    LEDGER.print_result_lines()
    return R.close("checks")


sys.exit(asyncio.run(main()))
