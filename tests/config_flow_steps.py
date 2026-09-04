"""The config flows, walked end to end with real validation (#194).

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

Tranche 2 (this file's second half) drives the other two flows:

* the fifteen-step OPTIONS flow (``init``/``advanced`` menus,
  ``setup_overview``, ``entities``, ``comfort``, ``hot_water``,
  ``building``, ``thermal_model``, ``tuning``, ``heat_curve``,
  ``building_preset``, ``grid``, ``solar_pv``, ``away``, ``learning``):
  every page submitted through the handler that really runs, its save
  persisted through ``async_update_entry`` (``AFTER_SAVE_MENU``, the
  stay-in-the-dialog default) or merged into one ``create_entry``
  (``AFTER_SAVE_CLOSE``), the after-save return routed to the menu the
  page came from, every per-page validation error, and the
  clearing-an-entity-selector-None write-backs -- including that the
  entities page nulls only its own roster (the PV/away/external-heat
  wipe this handler once shipped).
* the RECONFIGURE flow end to end through the real
  ``validate_tibber_token``: ``tests/entities.py`` drives it with the
  verdict stubbed to accept-anything, so the refused-token and
  unreachable branches, and the whole round trip against scripted HTTP,
  had never run.

``--self-check`` is the mutation-proof mode (tests/README.md): it breaks
the duplicate guard, the token probe, the options grid month validation,
the reconfigure guard's own-identity exemption and the grid page's
peak-hours grammar in-memory, one at a time, and fails unless the checks
that are supposed to catch each breakage really fail.  Normal mode must
pass on an unmodified tree; the self-check must fail on the broken one.

Expected (tolerance 0): every RESULT line reads full coverage --
``flow_checks_covered=<checks>`` with no failures, every step
``happy=P/P error_branches=P/P``, ``options_steps_covered=15/15``,
``reauth_round_trips=1``, ``reconfigure_round_trips=1``,
``duplicate_aborts=1``.  Baseline measured: 87645f8, re-verified
identical at 6d83f0b (tranche 1; ``config_flow.py`` byte-identical
between the two), extended at 9ab836e (tranche 2, the merge base, whose
``config_flow.py`` carries the #307 reconfigure flow), MacBookAir10,1;
every number here is a count, immune to box load.
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

# Valid answers for the fifteen options pages, at the shape each handler
# reads. One dict per page: a page probe overrides one field and submits
# an otherwise-valid page, the same discipline as the initial-flow walks.
COMFORT_PAGE_ANSWERS = {
    **TEMPERATURE_ANSWERS,
    const.CONF_MOLD_GUARD_ENABLED: True,
    const.CONF_THERMAL_BRIDGE_FRSI: 0.7,
    const.CONF_INDOOR_HUMIDITY_ENTITY: "sensor.living_humidity",
}
TUNING_ANSWERS = {
    const.CONF_PRICE_WEIGHT: 2.0,
    const.CONF_COMFORT_WEIGHT: 8.0,
    const.CONF_OPTIMIZATION_INTERVAL: 45,
    const.CONF_CYCLING_COST: 0.35,
    const.CONF_PRICE_RISK_LAMBDA: 0.4,
    const.CONF_CONFIDENCE_MARGINS_ENABLED: True,
    const.CONF_COMPRESSOR_REPLACEMENT_COST: 25000,
    const.CONF_COMPRESSOR_RATED_STARTS: 300000,
    const.CONF_WEAR_AUTOTUNE_ENABLED: True,
    const.CONF_PRICE_TILES_ENABLED: True,
}
# The peak-hours field is validated and consumed through ONE grammar. The
# options page checks it with ``is_valid_spec`` (config_flow.py:2658), bound
# from ``.dhw_schedule`` and not from ``grid_fee``; that function is
# ``parse_windows`` succeeding, which is exactly the predicate the
# coordinator's ``_tariff_hours`` applies to the stored value. So the
# documented form "07:00-19:00" both saves and takes effect.
#
# #327 reported the opposite -- the page validating this field with the
# grid-fee RULES grammar, leaving every non-empty value unsavable or
# silently ignored. Driven end to end through ``async_step_grid`` and back
# through ``_tariff_hours``, that did not reproduce in either direction, at
# the reported 9ab836e or at main; the issue is closed as not-reproducing.
# The likely misread is the module import of ``grid_fee`` sitting three
# lines above the ``.dhw_schedule`` one.
#
# The agreement is now pinned rather than assumed. Neither check keyed on
# the answers below would notice the validator being repointed at
# ``grid_fee.is_valid_spec``: this happy page carries the default empty
# spec, and the error probe uses "garbage", which no grammar accepts. The
# documented-form check in ``options_error_branches`` is the one that dies,
# and it is what #327's false report bought.
GRID_ANSWERS = {
    const.CONF_PEAK_TARIFF_ENABLED: True,
    const.CONF_PEAK_TARIFF_PRICE: 60.0,
    const.CONF_PEAK_TARIFF_COUNT: 3,
    const.CONF_PEAK_TARIFF_WINDOW: "60",
    const.CONF_PEAK_TARIFF_MONTHS: "nov-feb",
    const.CONF_PEAK_TARIFF_HOURS: "",
    const.CONF_PEAK_TARIFF_WEEKDAYS_ONLY: False,
    const.CONF_PEAK_TARIFF_OFFPEAK_FACTOR: 0.5,
    const.CONF_MAIN_FUSE_A: 16,
    const.CONF_MAIN_FUSE_PHASES: 3,
    const.CONF_FUSE_GUARD_ENABLED: True,
    const.CONF_PEAK_GUARD_ENABLED: True,
    const.CONF_PEAK_GUARD_MARGIN_KW: 1.0,
    const.CONF_GRID_FEE_MODE: config_flow.grid_fee.MODE_RULES,
    const.CONF_GRID_FEE_FIXED: 0.15,
    const.CONF_GRID_FEE_RULES: "06:00-08:00 = 0.5",
    const.CONF_CONTRACT_FIXED_PRICE: 0.9,
}
BUILDING_PAGE_ANSWERS = {
    const.CONF_MIXING_VALVE_MODE: config_flow.mixing_valve.MODE_NONE,
    const.CONF_MIXING_VALVE_TARGET: 0.0,
    const.CONF_MIXING_VALVE_WRITE_TARGET_KIND: config_flow.mixing_valve.WRITE_TARGET_INDOOR,
    const.CONF_BUFFER_TANK_VOLUME: 250.0,
    const.CONF_BUFFER_MAX_TEMP: 70.0,
    const.CONF_WOOD_TANK_VOLUME: 600.0,
    const.CONF_DHW_WOOD_COIL_ENABLED: True,
}
SOLAR_ANSWERS = {
    const.CONF_PV_ENABLED: True,
    const.CONF_PV_PEAK_KW: 8.5,
    const.CONF_PV_EFFICIENCY: 0.9,
    const.CONF_PV_EXPORT_PRICE: 0.45,
    const.CONF_PV_EXPORT_PRICE_ENTITY: "sensor.export_price",
}
AWAY_ANSWERS = {
    const.CONF_AWAY_ENABLED: True,
    const.CONF_AWAY_PRESENCE_ENTITY: "person.home",
    const.CONF_AWAY_TEMPERATURE: 17.0,
    const.CONF_AWAY_DHW_MIN_TEMP: 45.0,
}
LEARNING_ANSWERS = {
    const.CONF_STALENESS_ENABLED: True,
    const.CONF_STALENESS_SCALE: 2.0,
    const.CONF_EXTERNAL_HEAT_ENABLED: True,
    const.CONF_EXTERNAL_HEAT_ENTITY: "binary_sensor.stove",
    const.CONF_EXTERNAL_HEAT_MIN_RISE: 0.6,
    const.CONF_EXTERNAL_HEAT_DECAY_MINUTES: 45,
    const.CONF_COMFORT_LEARNING_ENABLED: True,
    const.CONF_SYSID_ENABLED: True,
    const.CONF_PRICE_PRIOR_ENABLED: True,
    const.CONF_OUTAGE_RECOVERY_ENABLED: True,
    const.CONF_OPEN_WINDOW_RELAX_ENABLED: True,
    const.CONF_IMMERSION_FEEDBACK_ENABLED: True,
    const.CONF_PRECIP_TYPE_ENABLED: True,
    const.CONF_SNOW_ROOF_FACTOR_ENABLED: True,
    const.CONF_CAPACITY_CURVE_ENABLED: True,
    const.CONF_SOLAR_APERTURE_LEARNING_ENABLED: True,
    const.CONF_INTERNAL_GAINS_LEARNING_ENABLED: True,
    const.CONF_CURVE_LEARNING_ENABLED: True,
}
HEAT_CURVE_ANSWERS = {
    const.CONF_ECL110_DISPLACE_SET_TOPIC: "ecl/set",
    const.CONF_ECL110_COMMAND_TOPIC: "ecl/cmd",
    const.CONF_ECL110_STATE_TOPIC: "ecl/state",
    const.CONF_ECL110_QOS: 1,
    const.CONF_ECL110_RETAIN: True,
    const.CONF_ECL110_DISPLACE_MIN: -10.0,
    const.CONF_ECL110_DISPLACE_MAX: 10.0,
    const.CONF_ECL110_PID_TIME_CONSTANT: 1.5,
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
        # Tranche 2 (#194): the fifteen options-flow steps. Each row is one
        # of HeatPumpOptimizerOptionsFlow's step methods; the opt_ prefix
        # keeps them apart from the initial-flow steps of the same name.
        options_steps = (
            "opt_init",
            "opt_advanced",
            "opt_setup_overview",
            "opt_entities",
            "opt_comfort",
            "opt_hot_water",
            "opt_building",
            "opt_thermal_model",
            "opt_tuning",
            "opt_heat_curve",
            "opt_building_preset",
            "opt_grid",
            "opt_solar_pv",
            "opt_away",
            "opt_learning",
        )
        covered = 0
        for step in options_steps:
            row = self.rows.get(step, {"happy": [], "error": [], "happy_ok": 0, "error_ok": 0})
            happy = f"{row['happy_ok']}/{len(row['happy'])}"
            errors = f"{row['error_ok']}/{len(row['error'])}"
            print(f"RESULT step_{step} happy={happy} error_branches={errors}")
            if row["happy"]:
                covered += 1
        print(f"RESULT options_steps_covered={covered}/15 pages")
        row = self.rows.get("reconfigure", {"happy": [], "error": [], "happy_ok": 0, "error_ok": 0})
        print(
            f"RESULT step_reconfigure happy={row['happy_ok']}/{len(row['happy'])} "
            f"error_branches={row['error_ok']}/{len(row['error'])}"
        )
        print(f"RESULT reauth_round_trips={self.rows.get('_reauth', 0)}")
        print(f"RESULT reconfigure_round_trips={self.rows.get('_reconfigure', 0)}")
        print(f"RESULT options_close_round_trips={self.rows.get('_options_close', 0)}")
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


def shows_menu(result, step_id):
    """The result is an options-flow menu for this step."""
    return result.get("type") == "menu" and result.get("step_id") == step_id


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
# Tranche 2 (#194): the options flow. Its entry is a real one -- walked
# through the questionnaire path above, then handed to
# ``async_get_options_flow`` the way the flow manager does. Every page is
# submitted through the handler that really runs, and every save is
# asserted against the entry's options afterwards.
# ---------------------------------------------------------------------------
BASE_ENTRY_DATA: dict = {}
BASE_UNIQUE_ID: str | None = None


async def seed_base_entry():
    """Walk the initial flow once and keep its entry (idempotent)."""
    global BASE_ENTRY_DATA, BASE_UNIQUE_ID
    if not BASE_ENTRY_DATA:
        BASE_ENTRY_DATA, BASE_UNIQUE_ID = await options_entry_data()


async def options_entry_data():
    """The entry data of an existing install, from a real walk (not a fixture)."""
    real = install_session(config_flow, FakeSession([TIBBER_VIEWER_OK]))
    try:
        flow = fresh_flow()
        await submit(
            flow,
            "user",
            {**FIRST_SCREEN, const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor_a"},
        )
        await submit(flow, "temperature", TEMPERATURE_ANSWERS)
        await submit(flow, "building_describe", QUESTIONNAIRE_ANSWERS)
        await submit(flow, "building_extras", EXTRAS_ANSWERS)
        await submit(flow, "dhw", DHW_ANSWERS)
        result = await submit(flow, "weather_sensitivity", WEATHER_ANSWERS)
    finally:
        config_flow.async_get_clientsession = real
    assert result.get("type") == "create_entry", str(result)[:200]
    return dict(result["data"]), flow.unique_id


def fresh_options(pre_options=None, entry_id="opts-1"):
    """A fresh options flow over a fresh entry seeded as the walk left it."""
    hass = FakeHass()
    entry = FakeEntry(
        data=dict(BASE_ENTRY_DATA),
        options=dict(pre_options or {}),
        entry_id=entry_id,
        unique_id=BASE_UNIQUE_ID,
    )
    hass.config_entries.entries.append(entry)
    flow = config_flow.HeatPumpOptimizerConfigFlow.async_get_options_flow(entry)
    flow.hass = hass
    return flow, entry, hass


async def options_menus():
    R.section("options: the two menus")
    flow, entry, _ = fresh_options()
    top = await flow.async_step_init(None)
    check(
        "opt_init",
        "happy",
        "the top menu offers the revisited pages plus Advanced, in order",
        shows_menu(top, "init")
        and list(top.get("menu_options", {}))
        == ["setup_overview", "comfort", "hot_water", "tuning", "grid", "away", "advanced"],
        str(list(top.get("menu_options", {}))),
    )
    advanced = await flow.async_step_advanced(None)
    check(
        "opt_advanced",
        "happy",
        "the advanced menu lists the set-once pages, in order",
        shows_menu(advanced, "advanced")
        and list(advanced.get("menu_options", {}))
        == [
            "entities",
            "building",
            "building_preset",
            "thermal_model",
            "solar_pv",
            "learning",
            "heat_curve",
        ],
        str(list(advanced.get("menu_options", {}))),
    )


async def options_walk():
    """One dialog, six top pages: show each form, submit it, stay in the dialog."""
    R.section("options walk: six top pages, every save through async_update_entry")
    flow, entry, hass = fresh_options()

    # setup_overview is read-only: a picture of the system, saving nothing.
    form = await flow.async_step_setup_overview(None)
    check(
        "opt_setup_overview",
        "happy",
        "the setup overview renders the configured system as text",
        shows(form, "setup_overview")
        and bool(form.get("description_placeholders", {}).get("setup_summary")),
        str(form.get("description_placeholders", {}))[:120],
    )
    result = await submit(flow, "setup_overview", {})
    check(
        "opt_setup_overview",
        "happy",
        "leaving the overview returns to the menu and saves nothing",
        shows_menu(result, "init") and not entry.options and not hass.config_entries.updated,
        f"options={sorted(entry.options)} updated={hass.config_entries.updated}",
    )

    # comfort: a valid band, a humidity sensor, then the menu again.
    await flow.async_step_comfort(None)
    result = await submit(flow, "comfort", COMFORT_PAGE_ANSWERS)
    check(
        "opt_comfort",
        "happy",
        "a valid comfort page saves and returns to the top menu",
        shows_menu(result, "init")
        and entry.options.get(const.CONF_TARGET_TEMP) == 21.0
        and entry.options.get(const.CONF_INDOOR_HUMIDITY_ENTITY) == "sensor.living_humidity"
        and hass.config_entries.updated == ["opts-1"],
        f"{result.get('type')}/{result.get('step_id')} "
        f"options={sorted(entry.options)[:6]}",
    )

    # hot_water: the same page the initial flow has, with its warning.
    warnings: list[str] = []

    class Capture(logging.Handler):
        def emit(self, record):
            warnings.append(record.getMessage().lower())

    logger = logging.getLogger("heatpump_optimizer.config_flow")
    logger.addHandler(Capture())
    try:
        await flow.async_step_hot_water(None)
        result = await submit(flow, "hot_water", DHW_ANSWERS)
    finally:
        logger.removeHandler(Capture())
    check(
        "opt_hot_water",
        "happy",
        "a valid hot-water page saves and warns about the legionella pair",
        shows_menu(result, "init")
        and entry.options.get(const.CONF_DHW_SETPOINT) == 52.0
        and any("legionella" in w for w in warnings),
        f"{result.get('type')}/{result.get('step_id')} warned={warnings[:1]}",
    )
    check(
        "opt_hot_water",
        "happy",
        "this page's cleared entity slots are written back as None",
        entry.options.get(const.CONF_DHW_INLET_ENTITY) is None
        and entry.options.get(const.CONF_VVC_PUMP_ENTITY) is None
        and entry.options.get(const.CONF_SPACE_PUMP_ENTITY) is None,
        str(
            {
                k: entry.options.get(k)
                for k in (
                    const.CONF_DHW_INLET_ENTITY,
                    const.CONF_VVC_PUMP_ENTITY,
                    const.CONF_SPACE_PUMP_ENTITY,
                )
            }
        ),
    )

    # tuning: the objective weights.
    await flow.async_step_tuning(None)
    result = await submit(flow, "tuning", TUNING_ANSWERS)
    check(
        "opt_tuning",
        "happy",
        "the tuning page saves and returns to the top menu",
        shows_menu(result, "init") and entry.options.get(const.CONF_PRICE_WEIGHT) == 2.0,
        f"{result.get('type')}/{result.get('step_id')} "
        f"price_weight={entry.options.get(const.CONF_PRICE_WEIGHT)}",
    )

    # grid: the fee and tariff page, with its string->int window conversion.
    await flow.async_step_grid(None)
    result = await submit(flow, "grid", GRID_ANSWERS)
    check(
        "opt_grid",
        "happy",
        "the grid page saves, converting the window dropdown to minutes",
        shows_menu(result, "init")
        and entry.options.get(const.CONF_PEAK_TARIFF_WINDOW) == 60
        and entry.options.get(const.CONF_PEAK_TARIFF_MONTHS) == "nov-feb"
        and entry.options.get(const.CONF_GRID_FEE_ENTITY) is None,
        f"window={entry.options.get(const.CONF_PEAK_TARIFF_WINDOW)!r} "
        f"months={entry.options.get(const.CONF_PEAK_TARIFF_MONTHS)!r}",
    )

    # away: the last top page.
    await flow.async_step_away(None)
    result = await submit(flow, "away", AWAY_ANSWERS)
    check(
        "opt_away",
        "happy",
        "the away page saves, clearing its own empty entity slots",
        shows_menu(result, "init")
        and entry.options.get(const.CONF_AWAY_TEMPERATURE) == 17.0
        and entry.options.get(const.CONF_AWAY_RETURN_ENTITY) is None,
        f"{result.get('type')}/{result.get('step_id')} "
        f"return={entry.options.get(const.CONF_AWAY_RETURN_ENTITY)!r}",
    )

    # Six pages in, one entry: the saves must have accumulated, not replaced.
    from_every_page = [
        key
        for key in (
            const.CONF_TARGET_TEMP,
            const.CONF_DHW_SETPOINT,
            const.CONF_PRICE_WEIGHT,
            const.CONF_PEAK_TARIFF_WINDOW,
            const.CONF_AWAY_TEMPERATURE,
        )
        if key not in entry.options
    ]
    check(
        "opt_init",
        "happy",
        "five saved pages accumulate on the entry, not replace each other",
        not from_every_page and len(hass.config_entries.updated) == 5,
        f"missing {from_every_page} updated={len(hass.config_entries.updated)}",
    )

    # The other after-save choice: close the dialog. One create_entry whose
    # data is this page merged into everything saved before it, and the
    # after-save choice itself never persists.
    result = await submit(
        flow,
        "tuning",
        {**TUNING_ANSWERS, const.CONF_PRICE_WEIGHT: 3.0, const.CONF_AFTER_SAVE: const.AFTER_SAVE_CLOSE},
    )
    close_data = result.get("data", {})
    round_trip_done = (
        result.get("type") == "create_entry"
        and close_data.get(const.CONF_PRICE_WEIGHT) == 3.0
        and close_data.get(const.CONF_TARGET_TEMP) == 21.0
        and close_data.get(const.CONF_AWAY_TEMPERATURE) == 17.0
        and close_data.get(const.CONF_PEAK_TARIFF_WINDOW) == 60
        and const.CONF_AFTER_SAVE not in close_data
    )
    check(
        "opt_tuning",
        "happy",
        "'close' merges this page into every page saved before it",
        round_trip_done,
        f"{result.get('type')} keys={len(close_data)} "
        f"after_save_persisted={const.CONF_AFTER_SAVE in close_data}",
    )
    LEDGER.rows["_options_close"] = int(round_trip_done)


async def options_advanced_pages():
    """The seven advanced pages, each on its own entry (they seed their own)."""
    R.section("options: the advanced pages")

    # entities: the token verdicts, the clearing, and the roster scope.
    real = install_session(config_flow, FakeSession([TIBBER_VIEWER_OK]))
    refused = fresh_options()
    config_flow.async_get_clientsession = lambda hass, verify_ssl=True: FakeSession([(401, None)])
    result = await submit(
        refused[0],
        "entities",
        {const.CONF_TIBBER_TOKEN: "tok-wrong", const.CONF_WEATHER_ENTITY: "weather.home"},
    )
    check(
        "opt_entities",
        "error",
        "a changed but refused token re-shows the entities page as invalid_tibber_token",
        shows(result, "entities")
        and result.get("errors", {}).get(const.CONF_TIBBER_TOKEN) == "invalid_tibber_token"
        and not refused[1].options,
        str(result.get("errors")),
    )
    unreachable = fresh_options()
    config_flow.async_get_clientsession = lambda hass, verify_ssl=True: FakeSession(
        [OSError("router rebooting")]
    )
    result = await submit(
        unreachable[0],
        "entities",
        {const.CONF_TIBBER_TOKEN: "tok-wrong", const.CONF_WEATHER_ENTITY: "weather.home"},
    )
    check(
        "opt_entities",
        "error",
        "an unreachable Tibber is cannot_connect on the entities page too",
        shows(result, "entities")
        and result.get("errors", {}).get(const.CONF_TIBBER_TOKEN) == "cannot_connect"
        and not unreachable[1].options,
        str(result.get("errors")),
    )

    # An UNCHANGED token skips the probe entirely (the session counts zero
    # POSTs); cleared slots stick as None; and the entities this page does
    # not render -- the PV, away and external-heat slots -- survive the save.
    quiet_session = FakeSession([TIBBER_VIEWER_OK])
    config_flow.async_get_clientsession = lambda hass, verify_ssl=True: quiet_session
    flow, entry, _ = fresh_options(
        pre_options={
            const.CONF_PV_PRODUCTION_ENTITY: "sensor.pv",
            const.CONF_AWAY_PRESENCE_ENTITY: "person.home",
            const.CONF_EXTERNAL_HEAT_ENTITY: "binary_sensor.stove",
        }
    )
    await flow.async_step_entities(None)
    result = await submit(
        flow,
        "entities",
        {
            const.CONF_TIBBER_TOKEN: BASE_ENTRY_DATA[const.CONF_TIBBER_TOKEN],
            const.CONF_WEATHER_ENTITY: "weather.home",
        },
    )
    check(
        "opt_entities",
        "happy",
        "an unchanged token skips the probe and cleared slots stick as None",
        shows_menu(result, "advanced")
        and entry.options.get(const.CONF_INDOOR_TEMP_ENTITY) is None
        and entry.options.get(const.CONF_HEAT_PUMP_SWITCH_ENTITY) is None
        and quiet_session.posts == 0,
        f"indoor={entry.options.get(const.CONF_INDOOR_TEMP_ENTITY)!r} "
        f"posts={quiet_session.posts}",
    )
    check(
        "opt_entities",
        "happy",
        "other pages' entities survive an entities-page save",
        entry.options.get(const.CONF_PV_PRODUCTION_ENTITY) == "sensor.pv"
        and entry.options.get(const.CONF_AWAY_PRESENCE_ENTITY) == "person.home"
        and entry.options.get(const.CONF_EXTERNAL_HEAT_ENTITY) == "binary_sensor.stove",
        str(
            {
                k: entry.options.get(k)
                for k in (
                    const.CONF_PV_PRODUCTION_ENTITY,
                    const.CONF_AWAY_PRESENCE_ENTITY,
                    const.CONF_EXTERNAL_HEAT_ENTITY,
                )
            }
        ),
    )

    # A changed token that validates saves through.
    rotated_session = FakeSession([TIBBER_VIEWER_OK])
    config_flow.async_get_clientsession = lambda hass, verify_ssl=True: rotated_session
    flow, entry, _ = fresh_options()
    await flow.async_step_entities(None)
    result = await submit(
        flow,
        "entities",
        {const.CONF_TIBBER_TOKEN: "tok-rotated", const.CONF_WEATHER_ENTITY: "weather.home"},
    )
    check(
        "opt_entities",
        "happy",
        "a changed token that validates is written to the options",
        shows_menu(result, "advanced")
        and entry.options.get(const.CONF_TIBBER_TOKEN) == "tok-rotated"
        and rotated_session.posts == 1,
        f"token={entry.options.get(const.CONF_TIBBER_TOKEN)!r} "
        f"posts={rotated_session.posts}",
    )
    config_flow.async_get_clientsession = real

    # building: the plumbing page, clearable entities, and one validated
    # field (#398) -- see below.
    flow, entry, _ = fresh_options()
    await flow.async_step_building(None)
    result = await submit(flow, "building", BUILDING_PAGE_ANSWERS)
    check(
        "opt_building",
        "happy",
        "the building page saves to the advanced menu, clearing its entity slots",
        shows_menu(result, "advanced")
        and entry.options.get(const.CONF_BUFFER_TANK_VOLUME) == 250.0
        and entry.options.get(const.CONF_MIXING_VALVE_TARGET_ENTITY) is None
        and entry.options.get(const.CONF_WOOD_TANK_TOP_ENTITY) is None
        and entry.options.get(const.CONF_VALVE_OUTLET_TEMP_ENTITY) is None,
        f"valve={entry.options.get(const.CONF_MIXING_VALVE_TARGET_ENTITY)!r} "
        f"wood_top={entry.options.get(const.CONF_WOOD_TANK_TOP_ENTITY)!r}",
    )
    check(
        "opt_building",
        "happy",
        "the 'indoor' write-target kind round-trips through the page (#398)",
        entry.options.get(const.CONF_MIXING_VALVE_WRITE_TARGET_KIND)
        == config_flow.mixing_valve.WRITE_TARGET_INDOOR,
        str(entry.options.get(const.CONF_MIXING_VALVE_WRITE_TARGET_KIND)),
    )

    # 'flow' needs the two-zone model, whose absence is what the owner's
    # entry has by default here -- catch it rather than saving it silently.
    flow, entry, _ = fresh_options()
    await flow.async_step_building(None)
    result = await submit(
        flow,
        "building",
        {
            **BUILDING_PAGE_ANSWERS,
            const.CONF_MIXING_VALVE_WRITE_TARGET_KIND: (
                config_flow.mixing_valve.WRITE_TARGET_FLOW
            ),
        },
    )
    check(
        "opt_building",
        "error",
        "'flow' without the two-zone model is refused, not saved (#398)",
        shows(result, "building")
        and result.get("errors", {}).get(
            const.CONF_MIXING_VALVE_WRITE_TARGET_KIND
        )
        == "flow_target_needs_two_zone"
        and not entry.options,
        f"errors={result.get('errors')} options={sorted(entry.options)}",
    )

    # With the two-zone model present, the same choice saves.
    flow, entry, _ = fresh_options(
        pre_options={const.CONF_UPPER_FLOOR_THERMAL_MASS: 4.0}
    )
    await flow.async_step_building(None)
    result = await submit(
        flow,
        "building",
        {
            **BUILDING_PAGE_ANSWERS,
            const.CONF_MIXING_VALVE_WRITE_TARGET_KIND: (
                config_flow.mixing_valve.WRITE_TARGET_FLOW
            ),
        },
    )
    check(
        "opt_building",
        "happy",
        "'flow' with the two-zone model configured saves cleanly (#398)",
        shows_menu(result, "advanced")
        and entry.options.get(const.CONF_MIXING_VALVE_WRITE_TARGET_KIND)
        == config_flow.mixing_valve.WRITE_TARGET_FLOW,
        f"options={entry.options.get(const.CONF_MIXING_VALVE_WRITE_TARGET_KIND)!r}",
    )

    # thermal_model: the presence-hazard page. A no-op save keeps the
    # questionnaire armed; editing a derived number disarms it.
    stored_mass = BASE_ENTRY_DATA[const.CONF_HOUSE_THERMAL_MASS]
    flow, entry, _ = fresh_options()
    await flow.async_step_thermal_model(None)
    result = await submit(
        flow,
        "thermal_model",
        {
            const.CONF_HOUSE_THERMAL_MASS: stored_mass,
            const.CONF_HEAT_PUMP_MAX_POWER: 5.0,
            const.CONF_HEAT_PUMP_MIN_POWER: 1.0,
        },
    )
    check(
        "opt_thermal_model",
        "happy",
        "re-submitting the derived values as they are keeps the preset armed",
        shows_menu(result, "advanced")
        and const.CONF_BUILDING_PRESET_ENABLED not in entry.options,
        f"preset={entry.options.get(const.CONF_BUILDING_PRESET_ENABLED)!r}",
    )
    flow, entry, _ = fresh_options()
    await flow.async_step_thermal_model(None)
    result = await submit(
        flow, "thermal_model", {const.CONF_HOUSE_THERMAL_MASS: stored_mass + 2.0}
    )
    check(
        "opt_thermal_model",
        "happy",
        "editing a derived number disarms the questionnaire",
        shows_menu(result, "advanced")
        and entry.options.get(const.CONF_BUILDING_PRESET_ENABLED) is False
        and entry.options.get(const.CONF_HOUSE_THERMAL_MASS) == stored_mass + 2.0,
        f"preset={entry.options.get(const.CONF_BUILDING_PRESET_ENABLED)!r}",
    )

    # building_preset: the questionnaire, options-side. Enabling it derives
    # physics from the answers; disabling it leaves the numbers alone.
    flow, entry, _ = fresh_options()
    await flow.async_step_building_preset(None)
    result = await submit(
        flow,
        "building_preset",
        {
            **QUESTIONNAIRE_ANSWERS,
            const.CONF_HEATED_AREA: 160.0,
            const.CONF_WINDOW_AREA: 12.0,
            const.CONF_BUILDING_PRESET_ENABLED: True,
        },
    )
    check(
        "opt_building_preset",
        "happy",
        "enabling the preset derives physics from the answers",
        shows_menu(result, "advanced")
        and entry.options.get(const.CONF_BUILDING_PRESET_ENABLED) is True
        and const.CONF_HOUSE_THERMAL_MASS in entry.options
        and entry.options[const.CONF_HOUSE_THERMAL_MASS] != stored_mass,
        f"derived={entry.options.get(const.CONF_HOUSE_THERMAL_MASS)!r} "
        f"stored={stored_mass!r}",
    )
    flow, entry, _ = fresh_options()
    await flow.async_step_building_preset(None)
    result = await submit(
        flow,
        "building_preset",
        {**QUESTIONNAIRE_ANSWERS, const.CONF_BUILDING_PRESET_ENABLED: False},
    )
    check(
        "opt_building_preset",
        "happy",
        "a disabled preset saves the answers without deriving physics",
        shows_menu(result, "advanced")
        and entry.options.get(const.CONF_BUILDING_PRESET_ENABLED) is False
        and const.CONF_HOUSE_THERMAL_MASS not in entry.options,
        f"mass={entry.options.get(const.CONF_HOUSE_THERMAL_MASS)!r}",
    )

    # solar_pv, learning, heat_curve: plain pages, each clearing its own.
    flow, entry, _ = fresh_options()
    await flow.async_step_solar_pv(None)
    result = await submit(flow, "solar_pv", SOLAR_ANSWERS)
    check(
        "opt_solar_pv",
        "happy",
        "the solar page saves, clearing an absent production entity",
        shows_menu(result, "advanced")
        and entry.options.get(const.CONF_PV_PEAK_KW) == 8.5
        and entry.options.get(const.CONF_PV_PRODUCTION_ENTITY) is None
        and entry.options.get(const.CONF_PV_EXPORT_PRICE_ENTITY) == "sensor.export_price",
        f"production={entry.options.get(const.CONF_PV_PRODUCTION_ENTITY)!r}",
    )
    flow, entry, _ = fresh_options()
    await flow.async_step_learning(None)
    result = await submit(flow, "learning", LEARNING_ANSWERS)
    check(
        "opt_learning",
        "happy",
        "the learning page saves with its watchdogs and its own entity slot",
        shows_menu(result, "advanced")
        and entry.options.get(const.CONF_EXTERNAL_HEAT_ENTITY) == "binary_sensor.stove"
        and entry.options.get(const.CONF_SYSID_ENABLED) is True,
        f"external={entry.options.get(const.CONF_EXTERNAL_HEAT_ENTITY)!r}",
    )
    flow, entry, _ = fresh_options()
    await flow.async_step_heat_curve(None)
    result = await submit(flow, "heat_curve", HEAT_CURVE_ANSWERS)
    check(
        "opt_heat_curve",
        "happy",
        "the heat curve page saves its MQTT wiring",
        shows_menu(result, "advanced")
        and entry.options.get(const.CONF_ECL110_COMMAND_TOPIC) == "ecl/cmd"
        and entry.options.get(const.CONF_ECL110_PID_TIME_CONSTANT) == 1.5,
        str({k: entry.options.get(k) for k in HEAT_CURVE_ANSWERS}),
    )


async def options_error_branches():
    """Every per-page validation error, each on a fresh flow that must not save."""
    R.section("options: every page's validation errors")

    # comfort: the comfort band, one rule at a time, exact error dicts.
    flow, entry, _ = fresh_options()
    result = await submit(
        flow,
        "comfort",
        {
            **COMFORT_PAGE_ANSWERS,
            const.CONF_MIN_TEMP: 21.5,
            const.CONF_COMFORT_TEMP_DAY: 22.0,
            const.CONF_COMFORT_TEMP_NIGHT: 21.5,
        },
    )
    check(
        "opt_comfort",
        "error",
        "an inverted comfort band re-shows the page with min_above_target",
        shows(result, "comfort")
        and result.get("errors") == {const.CONF_MIN_TEMP: "min_above_target"},
        str(result.get("errors")),
    )
    check(
        "opt_comfort",
        "error",
        "and stores nothing",
        not entry.options,
        str(sorted(entry.options)),
    )

    # hot_water: the window grammar and the deadband, through the options page.
    flow, entry, _ = fresh_options()
    result = await submit(
        flow, "hot_water", {**DHW_ANSWERS, const.CONF_DHW_WINDOWS: "garbage"}
    )
    check(
        "opt_hot_water",
        "error",
        "an unparseable window spec is invalid_dhw_windows on this page too",
        shows(result, "hot_water")
        and result.get("errors", {}).get(const.CONF_DHW_WINDOWS) == "invalid_dhw_windows",
        str(result.get("errors")),
    )
    flow, entry, _ = fresh_options()
    result = await submit(
        flow,
        "hot_water",
        {**DHW_ANSWERS, const.CONF_DHW_SETPOINT: 48.0, const.CONF_DHW_MIN_TEMP: 46.0},
    )
    check(
        "opt_hot_water",
        "error",
        "a minimum with no deadband below the setpoint is dhw_min_too_close here too",
        shows(result, "hot_water")
        and result.get("errors", {}).get(const.CONF_DHW_MIN_TEMP) == "dhw_min_too_close"
        and not entry.options,
        str(result.get("errors")),
    )

    # thermal_model: the power pair, whole and half (the effective-pair rule).
    flow, entry, _ = fresh_options()
    result = await submit(
        flow,
        "thermal_model",
        {const.CONF_HEAT_PUMP_MAX_POWER: 4.0, const.CONF_HEAT_PUMP_MIN_POWER: 8.0},
    )
    check(
        "opt_thermal_model",
        "error",
        "an inverted power pair is min_power_above_max on the thermal page",
        shows(result, "thermal_model")
        and result.get("errors") == {const.CONF_HEAT_PUMP_MIN_POWER: "min_power_above_max"},
        str(result.get("errors")),
    )
    flow, entry, _ = fresh_options()
    result = await submit(flow, "thermal_model", {const.CONF_HEAT_PUMP_MIN_POWER: 6.0})
    check(
        "opt_thermal_model",
        "error",
        "a submitted floor above the STORED ceiling is caught too",
        shows(result, "thermal_model")
        and result.get("errors") == {const.CONF_HEAT_PUMP_MIN_POWER: "min_power_above_max"}
        and not entry.options,
        str(result.get("errors")),
    )

    # grid: three validators, each pinned on its own field.
    probes = [
        (
            "an unparseable month mask on the grid page is invalid_peak_months",
            {const.CONF_PEAK_TARIFF_MONTHS: "garbage"},
            const.CONF_PEAK_TARIFF_MONTHS,
            "invalid_peak_months",
        ),
        (
            "an unparseable hours mask on the grid page is invalid_peak_hours",
            {const.CONF_PEAK_TARIFF_HOURS: "garbage"},
            const.CONF_PEAK_TARIFF_HOURS,
            "invalid_peak_hours",
        ),
        (
            "an unparseable fee rule is invalid_grid_fee_rules",
            {const.CONF_GRID_FEE_RULES: "garbage"},
            const.CONF_GRID_FEE_RULES,
            "invalid_grid_fee_rules",
        ),
        (
            "a negative fee rate is grid_fee_rules_negative",
            {const.CONF_GRID_FEE_RULES: "06:00-08:00 = -1"},
            const.CONF_GRID_FEE_RULES,
            "grid_fee_rules_negative",
        ),
    ]
    for name, override, field, expected in probes:
        flow, entry, _ = fresh_options()
        result = await submit(flow, "grid", {**GRID_ANSWERS, **override})
        check(
            "opt_grid",
            "error",
            name,
            shows(result, "grid")
            and result.get("errors") == {field: expected}
            and not entry.options,
            f"got {result.get('errors')}, want {{{field!r}: {expected!r}}}",
        )

    # grid: the documented peak-hours form, saved through the page and then
    # READ BACK through the coordinator (#327, see the note above
    # GRID_ANSWERS). Asserting "the page showed no error" would not be
    # enough -- the failure this pins is a validator that accepts a string
    # the coordinator then cannot parse, which is silent at the form and
    # only shows up as an every-hour-peak fallback hours later. So the
    # check carries all the way to the mask ``_tariff_hours`` returns.
    #
    # The coordinator is imported here rather than at module scope: this
    # driver is about the flow, and pulling the coordinator in at import
    # time would make every run pay for it.
    from heatpump_optimizer.coordinator import (  # noqa: PLC0415
        HeatPumpOptimizerCoordinator,
    )

    flow, entry, _ = fresh_options()
    result = await submit(
        flow,
        "grid",
        {**GRID_ANSWERS, const.CONF_PEAK_TARIFF_HOURS: "07:00-19:00"},
    )
    stored = entry.options.get(const.CONF_PEAK_TARIFF_HOURS)
    coordinator = HeatPumpOptimizerCoordinator(
        FakeHass(),
        FakeEntry(data={**BASE_ENTRY_DATA, const.CONF_PEAK_TARIFF_HOURS: stored}),
    )
    mask = coordinator._tariff_hours()
    check(
        "opt_grid",
        "happy",
        "the documented peak-hours form saves and reaches the coordinator's mask",
        shows_menu(result, "init")
        and not result.get("errors")
        and stored == "07:00-19:00"
        and mask == ((7.0, 19.0),),
        f"errors={result.get('errors')} stored={stored!r} "
        f"_tariff_hours()={mask!r}, want ((7.0, 19.0),)",
    )


# ---------------------------------------------------------------------------
# Tranche 2 (#194): the reconfigure flow, end to end through the real
# validate_tibber_token. tests/entities.py drives this flow with the verdict
# stubbed to accept-anything; the branches below (a refused token
# mid-reconfigure, an unreachable Tibber, the whole round trip against
# scripted HTTP) had never run against the production verdict logic.
# ---------------------------------------------------------------------------
RC_ENTRY_DATA = {
    config_flow.CONF_NAME: "Annex pump",
    const.CONF_TIBBER_TOKEN: "stale-token",
    const.CONF_WEATHER_ENTITY: "weather.home",
    const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_a",
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.annex_indoor",
    const.CONF_TARGET_TEMP: 21.5,  # a second-screen setting the first screen never asks
}
RC_SAME = {
    config_flow.CONF_NAME: "Annex pump",
    const.CONF_TIBBER_TOKEN: "stale-token",
    const.CONF_WEATHER_ENTITY: "weather.home",
    const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_a",
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.annex_indoor",
}
RC_OTHER_PLANT = {
    **FIRST_SCREEN,
    const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_b",
}


def rc_setup():
    """A reconfigure flow as the 2024.6 manager starts one: two plants, entry A."""
    hass = FakeHass()
    entry = FakeEntry(
        data=dict(RC_ENTRY_DATA),
        entry_id="plant_a",
        unique_id=config_flow.entry_identity(RC_ENTRY_DATA),
    )
    other = FakeEntry(
        data=dict(RC_OTHER_PLANT),
        entry_id="plant_b",
        unique_id=config_flow.entry_identity(RC_OTHER_PLANT),
    )
    hass.config_entries.entries += [entry, other]
    flow = config_flow.HeatPumpOptimizerConfigFlow()
    flow.hass = hass
    flow.context = {"source": "reconfigure", "entry_id": "plant_a"}
    return flow, entry, other, hass


def rc_suggested(result):
    """The suggested values the reopened first screen carries, by field."""
    schema = result.get("data_schema")
    if schema is None:
        return {}
    return {
        str(getattr(key, "schema", key)): (getattr(key, "description", None) or {}).get(
            "suggested_value"
        )
        for key in schema.schema
    }


async def reconfigure_flow():
    R.section("reconfigure: the first screen reopened over the entry it changes")
    real = install_session(config_flow, FakeSession([TIBBER_VIEWER_OK]))

    # The entry point: the manager calls async_step_reconfigure with the
    # entry's own data; the step reopens the first screen prefilled from it.
    flow, entry, _, _ = rc_setup()
    result = await flow.async_step_reconfigure(None)
    suggested = rc_suggested(result)
    check(
        "reconfigure",
        "happy",
        "reconfigure reopens the first screen, prefilled with this entry's answers",
        shows(result, "user")
        and suggested.get(config_flow.CONF_NAME) == "Annex pump"
        and suggested.get(const.CONF_TIBBER_TOKEN) == "stale-token"
        and suggested.get(const.CONF_INDOOR_TEMP_ENTITY) == "sensor.annex_indoor",
        f"{result.get('type')}/{result.get('step_id')} suggested={suggested}",
    )

    # 401 mid-reconfigure: the token is refused, the entry is untouched.
    config_flow.async_get_clientsession = lambda hass, verify_ssl=True: FakeSession([(401, None)])
    flow, entry, _, hass = rc_setup()
    result = await submit(flow, "reconfigure", RC_SAME)
    check(
        "reconfigure",
        "error",
        "a refused token mid-reconfigure shows invalid_tibber_token, changing nothing",
        shows(result, "user")
        and result.get("errors", {}).get(const.CONF_TIBBER_TOKEN) == "invalid_tibber_token"
        and entry.data == dict(RC_ENTRY_DATA)
        and not hass.config_entries.updated,
        f"{result.get('errors')} updated={hass.config_entries.updated}",
    )
    config_flow.async_get_clientsession = lambda hass, verify_ssl=True: FakeSession(
        [OSError("router rebooting")]
    )
    flow, entry, _, hass = rc_setup()
    result = await submit(flow, "reconfigure", RC_SAME)
    check(
        "reconfigure",
        "error",
        "an unreachable Tibber is cannot_connect mid-reconfigure too",
        shows(result, "user")
        and result.get("errors", {}).get(const.CONF_TIBBER_TOKEN) == "cannot_connect"
        and not hass.config_entries.updated,
        str(result.get("errors")),
    )

    # Re-submitting this entry's OWN identity is the case the plain duplicate
    # guard would get wrong: the registry finds THIS entry, and the guard's
    # own-identity exemption is what lets the reconfigure proceed.
    config_flow.async_get_clientsession = lambda hass, verify_ssl=True: FakeSession(
        [TIBBER_VIEWER_OK]
    )
    flow, entry, _, hass = rc_setup()
    result = await submit(flow, "reconfigure", RC_SAME)
    round_trip_done = (
        result == {"type": "abort", "reason": "reconfigure_successful"}
        and entry.data[const.CONF_TARGET_TEMP] == 21.5
        and entry.data[const.CONF_TIBBER_TOKEN] == "stale-token"
        and hass.config_entries.reloaded == ["plant_a"]
        and entry.unique_id == config_flow.entry_identity(RC_ENTRY_DATA)
    )
    check(
        "reconfigure",
        "happy",
        "re-submitting this entry's own identity reconfigures it instead of aborting",
        round_trip_done,
        f"{result} reloaded={hass.config_entries.reloaded}",
    )

    # A rotated token: a new identity no other entry holds, written through
    # with the rest of the entry's data intact.
    flow, entry, _, hass = rc_setup()
    result = await submit(flow, "reconfigure", {**RC_SAME, const.CONF_TIBBER_TOKEN: "tok-fresh"})
    check(
        "reconfigure",
        "happy",
        "a rotated token is written through and the entry keeps its other settings",
        result == {"type": "abort", "reason": "reconfigure_successful"}
        and entry.data[const.CONF_TIBBER_TOKEN] == "tok-fresh"
        and entry.data[const.CONF_TARGET_TEMP] == 21.5
        and hass.config_entries.reloaded == ["plant_a"]
        and entry.unique_id
        == config_flow.entry_identity({**RC_ENTRY_DATA, const.CONF_TIBBER_TOKEN: "tok-fresh"}),
        f"{result} token={entry.data.get(const.CONF_TIBBER_TOKEN)} "
        f"reloaded={hass.config_entries.reloaded}",
    )

    # Changed identity: the picks now name the OTHER entry's plant. The
    # guard runs (this is not this entry's identity) and must refuse.
    flow, entry, _, hass = rc_setup()
    result = await submit(flow, "reconfigure", RC_OTHER_PLANT)
    check(
        "reconfigure",
        "error",
        "reconfiguring into another entry's plant is refused",
        result == {"type": "abort", "reason": "already_configured"}
        and entry.data == dict(RC_ENTRY_DATA)
        and not hass.config_entries.reloaded,
        f"{result} data_unchanged={entry.data == dict(RC_ENTRY_DATA)}",
    )

    # A cleared slot: the user stopped using this sensor, and the update
    # drops it instead of silently keeping the old entity.
    flow, entry, _, _ = rc_setup()
    cleared = {k: v for k, v in RC_SAME.items() if k != const.CONF_INDOOR_TEMP_ENTITY}
    result = await submit(flow, "reconfigure", cleared)
    check(
        "reconfigure",
        "happy",
        "a slot the user cleared is dropped, not silently kept",
        result == {"type": "abort", "reason": "reconfigure_successful"}
        and const.CONF_INDOOR_TEMP_ENTITY not in entry.data,
        f"{result} indoor={entry.data.get(const.CONF_INDOOR_TEMP_ENTITY)!r}",
    )

    LEDGER.rows["_reconfigure"] = int(round_trip_done)
    config_flow.async_get_clientsession = real


# ---------------------------------------------------------------------------
# --self-check: break production in memory, one behaviour at a time, and
# require the checks that guard each behaviour to fail. A check that cannot
# fail pins nothing (tests/README.md).
# ---------------------------------------------------------------------------
async def self_check():
    print("\n=== self-check: each mutation must break its named check ===")
    # The base-entry walk passes through the dhw warning; sink it so the
    # mutation verdicts stay readable.
    sink = logging.Handler()
    sink.emit = lambda record: None
    logging.getLogger().addHandler(sink)
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

    # Mutation 3: the options grid page's month-mask validation is a no-op.
    real_months = config_flow._valid_months_spec
    config_flow._valid_months_spec = lambda spec: True
    try:
        await seed_base_entry()
        flow, entry, _ = fresh_options()
        result = await submit(
            flow, "grid", {**GRID_ANSWERS, const.CONF_PEAK_TARIFF_MONTHS: "garbage"}
        )
        caught = (
            result.get("errors", {}).get(const.CONF_PEAK_TARIFF_MONTHS)
            != "invalid_peak_months"
        )
        outcomes.append(
            (
                "grid months validation no-op",
                caught,
                "an unparseable month mask on the grid page is invalid_peak_months",
                str(result.get("errors")),
            )
        )
    finally:
        config_flow._valid_months_spec = real_months

    # Mutation 4: the reconfigure guard runs on the entry's OWN identity --
    # the exemption removed. The wrapper runs the REAL guard against the
    # REAL identity before delegating, which is exactly what deleting the
    # ``self._reconfigure_entry is None or ...`` condition does to the
    # reconfigure path (the production-edit proof is in the PR body).
    real_user = config_flow.HeatPumpOptimizerConfigFlow.async_step_user

    async def guard_before_exemption(self, user_input=None):
        if user_input is not None and self._reconfigure_entry is not None:
            await self.async_set_unique_id(config_flow.entry_identity(user_input))
            self._abort_if_unique_id_configured()
        return await real_user(self, user_input)

    config_flow.HeatPumpOptimizerConfigFlow.async_step_user = guard_before_exemption
    try:
        real = install_session(config_flow, FakeSession([TIBBER_VIEWER_OK]))
        flow, _, _, _ = rc_setup()
        result = await submit(flow, "reconfigure", RC_SAME)
        caught = result != {"type": "abort", "reason": "reconfigure_successful"}
        outcomes.append(
            (
                "reconfigure guard runs on own identity",
                caught,
                "re-submitting this entry's own identity reconfigures it instead of aborting",
                str(result)[:120],
            )
        )
        config_flow.async_get_clientsession = real
    finally:
        config_flow.HeatPumpOptimizerConfigFlow.async_step_user = real_user

    # Mutation 5: the peak-hours field validated with the fee-RULES grammar
    # instead of the window one -- the defect #327 reported, which did not
    # reproduce (see the note above GRID_ANSWERS). Nothing in this driver
    # caught this before the documented-form check existed: the happy page
    # submits the empty default and the error probe submits "garbage", and
    # both are verdict-identical under either grammar.
    real_hours = config_flow.is_valid_spec
    config_flow.is_valid_spec = config_flow.grid_fee.is_valid_spec
    try:
        await seed_base_entry()
        flow, entry, _ = fresh_options()
        result = await submit(
            flow,
            "grid",
            {**GRID_ANSWERS, const.CONF_PEAK_TARIFF_HOURS: "07:00-19:00"},
        )
        stored = entry.options.get(const.CONF_PEAK_TARIFF_HOURS)
        caught = not (shows_menu(result, "init") and stored == "07:00-19:00")
        outcomes.append(
            (
                "peak hours validated with the fee-rules grammar (#327)",
                caught,
                "the documented peak-hours form saves and reaches the coordinator's mask",
                f"errors={result.get('errors')} stored={stored!r}",
            )
        )
    finally:
        config_flow.is_valid_spec = real_hours

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
    print("\nall five mutations caught by their named checks")
    return 0


async def main() -> int:
    if "--self-check" in sys.argv:
        return await self_check()

    # A sink for the one WARNING the dhw branch provokes, so the ledger's
    # output stays readable.
    sink = logging.Handler()
    sink.emit = lambda record: None
    logging.getLogger().addHandler(sink)

    await seed_base_entry()
    await duplicate_and_null_control()
    await user_error_branches()
    await walk_questionnaire()
    await walk_expert()
    await temperature_error_branches()
    await reauth_round_trip()
    await options_menus()
    await options_walk()
    await options_advanced_pages()
    await options_error_branches()
    await reconfigure_flow()

    print()
    LEDGER.print_result_lines()
    return R.close("checks")


sys.exit(asyncio.run(main()))
