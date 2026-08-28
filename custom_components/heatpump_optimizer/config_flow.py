"""Config flow for Heat Pump Cost Optimizer integration."""
from __future__ import annotations

import logging
from typing import Any, Final

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.translation import async_get_translations

from .const import (
    DOMAIN,
    CONFIG_ENTRY_VERSION,
    CONF_TIBBER_TOKEN,
    CONF_WEATHER_ENTITY,
    CONF_INDOOR_TEMP_ENTITY,
    CONF_OUTDOOR_TEMP_ENTITY,
    CONF_HEAT_PUMP_SWITCH_ENTITY,
    CONF_HEAT_PUMP_MODE_ENTITY,
    CONF_HEAT_PUMP_DEFROST_ENTITY,
    CONF_HEAT_PUMP_ONLINE_ENTITY,
    CONF_HEAT_PUMP_FAULT_ENTITY,
    CONF_SOLAR_RADIATION_ENTITY,
    CONF_SOLAR_FORECAST_SOURCE,
    CONF_SOLAR_LOCATION,
    DEFAULT_SOLAR_FORECAST_SOURCE,
    SOLAR_SOURCES,
    CONF_FLOOR_RETURN_TEMP_ENTITY,
    CONF_BUFFER_MAX_TEMP,
    CONF_LOWER_FLOOR_TEMP_ENTITY,
    CONF_MIXING_VALVE_MODE,
    CONF_MIXING_VALVE_TARGET,
    CONF_MIXING_VALVE_TARGET_ENTITY,
    CONF_MIXING_VALVE_WRITE_ENTITY,
    DEFAULT_BUFFER_MAX_TEMP,
    DEFAULT_MIXING_VALVE_TARGET,
    CONF_BUFFER_TANK_TEMP_ENTITY,
    CONF_DHW_TEMP_ENTITY,
    CONF_ECL110_COMMAND_TOPIC,
    CONF_ECL110_DISPLACE_SET_TOPIC,
    CONF_ECL110_STATE_TOPIC,
    CONF_ECL110_QOS,
    CONF_ECL110_RETAIN,
    CONF_ECL110_DISPLACE_MIN,
    CONF_ECL110_DISPLACE_MAX,
    CONF_ECL110_PID_TIME_CONSTANT,
    CONF_TARGET_TEMP,
    CONF_MIN_TEMP,
    CONF_MAX_TEMP,
    CONF_COMFORT_TEMP_DAY,
    CONF_COMFORT_TEMP_NIGHT,
    CONF_DAY_START_HOUR,
    CONF_DAY_END_HOUR,
    CONF_HOUSE_THERMAL_MASS,
    CONF_HOUSE_HEAT_LOSS_COEFFICIENT,
    CONF_SLAB_THERMAL_MASS,
    CONF_SLAB_HEAT_TRANSFER,
    CONF_HEAT_PUMP_COP_NOMINAL,
    CONF_HEAT_PUMP_MAX_POWER,
    CONF_HEAT_PUMP_MIN_POWER,
    CONF_UPPER_FLOOR_THERMAL_MASS,
    CONF_LOWER_FLOOR_THERMAL_MASS,
    CONF_UPPER_FLOOR_HEAT_LOSS,
    CONF_LOWER_FLOOR_HEAT_LOSS,
    CONF_INTER_ZONE_TRANSFER,
    CONF_RADIATOR_POWER_FRACTION,
    CONF_UPPER_FLOOR_AREA_RATIO,
    CONF_BUFFER_TANK_VOLUME,
    CONF_WINDOW_AREA,
    CONF_SOLAR_ORIENTATION_FACTOR,
    CONF_SOLAR_HEAT_GAIN_COEFF,
    CONF_DHW_TANK_VOLUME,
    CONF_DHW_SETPOINT,
    CONF_DHW_MIN_TEMP,
    CONF_DHW_DAILY_CONSUMPTION,
    CONF_DHW_COOLING_RATE,
    CONF_DHW_SCHEDULE_ENABLED,
    CONF_DHW_WINDOWS,
    CONF_DHW_IDLE_MIN_TEMP,
    CONF_DHW_LEGIONELLA_ENABLED,
    CONF_DHW_LEGIONELLA_TEMP,
    CONF_DHW_LEGIONELLA_INTERVAL_DAYS,
    CONF_DHW_INLET_TEMP,
    DEFAULT_DHW_INLET_TEMP,
    CONF_DHW_INLET_SEASONAL_AMPLITUDE,
    DEFAULT_DHW_INLET_SEASONAL_AMPLITUDE,
    CONF_DHW_INLET_ENTITY,
    CONF_GREYWATER_RECOVERY,
    DEFAULT_GREYWATER_RECOVERY,
    CONF_DHW_QUANTILE_TARGETS_ENABLED,
    DEFAULT_DHW_QUANTILE_TARGETS_ENABLED,
    CONF_DHW_FREE_DISINFECTION_ENABLED,
    DEFAULT_DHW_FREE_DISINFECTION_ENABLED,
    CONF_DHW_ELASTIC_LEGIONELLA_ENABLED,
    DEFAULT_DHW_ELASTIC_LEGIONELLA_ENABLED,
    CONF_DHW_LEGIONELLA_MIN_INTERVAL_DAYS,
    DEFAULT_DHW_LEGIONELLA_MIN_INTERVAL_DAYS,
    CONF_SHOWER_FLOW_LPM,
    DEFAULT_SHOWER_FLOW_LPM,
    CONF_VVC_PUMP_ENTITY,
    CONF_VVC_LEAD_MINUTES,
    DEFAULT_VVC_LEAD_MINUTES,
    CONF_SPACE_PUMP_ENTITY,
    CONF_WIND_SENSITIVITY,
    CONF_RAIN_HEAT_LOSS_MULTIPLIER,
    CONF_OPTIMIZATION_INTERVAL,
    CONF_PRICE_WEIGHT,
    CONF_COMFORT_WEIGHT,
    DEFAULT_TARGET_TEMP,
    DEFAULT_MIN_TEMP,
    DEFAULT_MAX_TEMP,
    DEFAULT_COMFORT_TEMP_DAY,
    DEFAULT_COMFORT_TEMP_NIGHT,
    DEFAULT_DAY_START_HOUR,
    DEFAULT_DAY_END_HOUR,
    DEFAULT_HOUSE_THERMAL_MASS,
    DEFAULT_HOUSE_HEAT_LOSS_COEFFICIENT,
    DEFAULT_SLAB_THERMAL_MASS,
    DEFAULT_SLAB_HEAT_TRANSFER,
    DEFAULT_HEAT_PUMP_COP_NOMINAL,
    DEFAULT_HEAT_PUMP_MAX_POWER,
    DEFAULT_HEAT_PUMP_MIN_POWER,
    DEFAULT_UPPER_FLOOR_THERMAL_MASS,
    DEFAULT_LOWER_FLOOR_THERMAL_MASS,
    DEFAULT_UPPER_FLOOR_HEAT_LOSS,
    DEFAULT_LOWER_FLOOR_HEAT_LOSS,
    DEFAULT_INTER_ZONE_TRANSFER,
    DEFAULT_RADIATOR_POWER_FRACTION,
    DEFAULT_UPPER_FLOOR_AREA_RATIO,
    DEFAULT_BUFFER_TANK_VOLUME,
    DEFAULT_WINDOW_AREA,
    DEFAULT_SOLAR_ORIENTATION_FACTOR,
    DEFAULT_SOLAR_HEAT_GAIN_COEFF,
    DEFAULT_DHW_TANK_VOLUME,
    DEFAULT_DHW_SETPOINT,
    DEFAULT_DHW_MIN_TEMP,
    DHW_MIN_TEMP_SETPOINT_MARGIN,
    DEFAULT_DHW_DAILY_CONSUMPTION,
    DEFAULT_DHW_COOLING_RATE,
    DEFAULT_DHW_SCHEDULE_ENABLED,
    DEFAULT_DHW_WINDOWS,
    DEFAULT_DHW_IDLE_MIN_TEMP,
    DEFAULT_DHW_LEGIONELLA_ENABLED,
    DEFAULT_DHW_LEGIONELLA_TEMP,
    DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS,
    DEFAULT_ECL110_COMMAND_TOPIC,
    DEFAULT_ECL110_DISPLACE_SET_TOPIC,
    DEFAULT_ECL110_STATE_TOPIC,
    DEFAULT_ECL110_QOS,
    DEFAULT_ECL110_RETAIN,
    DEFAULT_ECL110_DISPLACE_MIN,
    DEFAULT_ECL110_DISPLACE_MAX,
    DEFAULT_ECL110_PID_TIME_CONSTANT,
    DEFAULT_WIND_SENSITIVITY,
    DEFAULT_RAIN_HEAT_LOSS_MULTIPLIER,
    DEFAULT_OPTIMIZATION_INTERVAL,
    DEFAULT_PRICE_WEIGHT,
    DEFAULT_COMFORT_WEIGHT,
    # Added in v2.8.0
    CONF_POWER_ENTITY,
    CONF_ENERGY_ENTITY,
    CONF_HOUSE_POWER_ENTITY,
    CONF_STALENESS_ENABLED,
    CONF_STALENESS_SCALE,
    DEFAULT_STALENESS_ENABLED,
    DEFAULT_STALENESS_SCALE,
    STALENESS_SCALE_MIN,
    STALENESS_SCALE_MAX,
    CONF_EXTERNAL_HEAT_ENABLED,
    CONF_EXTERNAL_HEAT_ENTITY,
    CONF_EXTERNAL_HEAT_MIN_RISE,
    CONF_EXTERNAL_HEAT_DECAY_MINUTES,
    DEFAULT_EXTERNAL_HEAT_ENABLED,
    DEFAULT_EXTERNAL_HEAT_MIN_RISE,
    DEFAULT_EXTERNAL_HEAT_DECAY_MINUTES,
    CONF_VALVE_OUTLET_TEMP_ENTITY,
    CONF_WOOD_TANK_TOP_ENTITY,
    CONF_WOOD_TANK_BOTTOM_ENTITY,
    CONF_WOOD_TANK_VOLUME,
    DEFAULT_WOOD_TANK_VOLUME,
    CONF_DHW_WOOD_COIL_ENABLED,
    DEFAULT_DHW_WOOD_COIL_ENABLED,
    CONF_PRICE_PRIOR_ENABLED,
    DEFAULT_PRICE_PRIOR_ENABLED,
    CONF_PEAK_TARIFF_ENABLED,
    CONF_PEAK_TARIFF_PRICE,
    CONF_PEAK_TARIFF_COUNT,
    CONF_PEAK_TARIFF_WINDOW,
    DEFAULT_PEAK_TARIFF_ENABLED,
    DEFAULT_PEAK_TARIFF_PRICE,
    DEFAULT_PEAK_TARIFF_COUNT,
    DEFAULT_PEAK_TARIFF_WINDOW,
    CONF_CYCLING_COST,
    DEFAULT_CYCLING_COST,
    CONF_GRID_FEE_MODE,
    DEFAULT_GRID_FEE_MODE,
    CONF_GRID_FEE_RULES,
    DEFAULT_GRID_FEE_RULES,
    CONF_GRID_FEE_ENTITY,
    CONF_GRID_FEE_FIXED,
    DEFAULT_GRID_FEE_FIXED,
    CONF_PEAK_TARIFF_MONTHS,
    DEFAULT_PEAK_TARIFF_MONTHS,
    CONF_PEAK_TARIFF_HOURS,
    DEFAULT_PEAK_TARIFF_HOURS,
    CONF_PEAK_TARIFF_WEEKDAYS_ONLY,
    DEFAULT_PEAK_TARIFF_WEEKDAYS_ONLY,
    CONF_PEAK_TARIFF_OFFPEAK_FACTOR,
    DEFAULT_PEAK_TARIFF_OFFPEAK_FACTOR,
    CONF_PRICE_RISK_LAMBDA,
    DEFAULT_PRICE_RISK_LAMBDA,
    CONF_CONTRACT_FIXED_PRICE,
    DEFAULT_CONTRACT_FIXED_PRICE,
    CONF_MAIN_FUSE_A,
    DEFAULT_MAIN_FUSE_A,
    CONF_MAIN_FUSE_PHASES,
    DEFAULT_MAIN_FUSE_PHASES,
    CONF_FUSE_GUARD_ENABLED,
    DEFAULT_FUSE_GUARD_ENABLED,
    CONF_PEAK_GUARD_ENABLED,
    DEFAULT_PEAK_GUARD_ENABLED,
    CONF_PEAK_GUARD_MARGIN_KW,
    DEFAULT_PEAK_GUARD_MARGIN_KW,
    CONF_OUTAGE_RECOVERY_ENABLED,
    DEFAULT_OUTAGE_RECOVERY_ENABLED,
    CONF_OPEN_WINDOW_RELAX_ENABLED,
    DEFAULT_OPEN_WINDOW_RELAX_ENABLED,
    CONF_IMMERSION_FEEDBACK_ENABLED,
    DEFAULT_IMMERSION_FEEDBACK_ENABLED,
    CONF_PRECIP_TYPE_ENABLED,
    DEFAULT_PRECIP_TYPE_ENABLED,
    CONF_SNOW_ROOF_FACTOR_ENABLED,
    DEFAULT_SNOW_ROOF_FACTOR_ENABLED,
    CONF_CAPACITY_CURVE_ENABLED,
    DEFAULT_CAPACITY_CURVE_ENABLED,
    CONF_SOLAR_APERTURE_LEARNING_ENABLED,
    DEFAULT_SOLAR_APERTURE_LEARNING_ENABLED,
    CONF_INTERNAL_GAINS_LEARNING_ENABLED,
    DEFAULT_INTERNAL_GAINS_LEARNING_ENABLED,
    CONF_CURVE_LEARNING_ENABLED,
    DEFAULT_CURVE_LEARNING_ENABLED,
    CONF_CONFIDENCE_MARGINS_ENABLED,
    DEFAULT_CONFIDENCE_MARGINS_ENABLED,
    CONF_COMPRESSOR_REPLACEMENT_COST,
    DEFAULT_COMPRESSOR_REPLACEMENT_COST,
    CONF_COMPRESSOR_RATED_STARTS,
    DEFAULT_COMPRESSOR_RATED_STARTS,
    CONF_WEAR_AUTOTUNE_ENABLED,
    DEFAULT_WEAR_AUTOTUNE_ENABLED,
    CONF_PRICE_TILES_ENABLED,
    DEFAULT_PRICE_TILES_ENABLED,
    CONF_COMPRESSOR_FREQ_ENTITY,
    CONF_COMPRESSOR_FREQ_SENSOR,
    CONF_FREQ_CONTROL_MODE,
    DEFAULT_FREQ_CONTROL_MODE,
    CONF_MOLD_GUARD_ENABLED,
    DEFAULT_MOLD_GUARD_ENABLED,
    CONF_INDOOR_HUMIDITY_ENTITY,
    CONF_THERMAL_BRIDGE_FRSI,
    DEFAULT_THERMAL_BRIDGE_FRSI,
    CONF_PV_ENABLED,
    CONF_PV_PEAK_KW,
    CONF_PV_EFFICIENCY,
    CONF_PV_EXPORT_PRICE,
    CONF_PV_EXPORT_PRICE_ENTITY,
    CONF_PV_PRODUCTION_ENTITY,
    DEFAULT_PV_ENABLED,
    DEFAULT_PV_PEAK_KW,
    DEFAULT_PV_EFFICIENCY,
    DEFAULT_PV_EXPORT_PRICE,
    CONF_AWAY_ENABLED,
    CONF_AWAY_PRESENCE_ENTITY,
    CONF_AWAY_RETURN_ENTITY,
    CONF_AWAY_TEMPERATURE,
    CONF_AWAY_DHW_MIN_TEMP,
    DEFAULT_AWAY_ENABLED,
    DEFAULT_AWAY_TEMPERATURE,
    DEFAULT_AWAY_DHW_MIN_TEMP,
    CONF_SYSID_ENABLED,
    DEFAULT_SYSID_ENABLED,
    CONF_COMFORT_LEARNING_ENABLED,
    DEFAULT_COMFORT_LEARNING_ENABLED,
    CONF_TWO_ZONE_MODE,
    TWO_ZONE_MODES,
    TWO_ZONE_MODE_AUTO,
    CONF_BUILDING_PRESET_ENABLED,
    CONF_BUILDING_STRUCTURE,
    CONF_BUILDING_ERA,
    CONF_BUILDING_FOUNDATION,
    CONF_HEATED_AREA,
    CONF_UPPER_EMITTER,
    CONF_LOWER_EMITTER,
    DEFAULT_BUILDING_PRESET_ENABLED,
    DEFAULT_HEATED_AREA,
)
from . import comfort_band, grid_fee, mixing_valve, presets, topology
from .dhw_schedule import is_valid_spec
from .freq_control import FREQ_MODE_CONTROL, FREQ_MODE_OBSERVE

_LOGGER = logging.getLogger(__name__)

TIBBER_API_URL = "https://api.tibber.com/v1-beta/gql"


async def validate_tibber_token(hass: HomeAssistant, token: str) -> str:
    """Check the Tibber API token: "ok", "invalid_auth" or "cannot_connect".

    The distinction matters at 03:00 with the router rebooting: a network
    failure must not tell the user their token is wrong — retyping a
    correct token fixes nothing, and the message sends them to the wrong
    place. Only Tibber's own verdict (an errors payload, or 401/403) may
    say "invalid"; everything else is a connectivity answer.
    """
    query = '{ "query": "{ viewer { name } }" }'
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    try:
        # Home Assistant's shared session — never closed here. A private
        # ClientSession per validation attempt leaked its connection pool.
        session = async_get_clientsession(hass)
        async with session.post(
            TIBBER_API_URL, data=query, headers=headers,
            timeout=aiohttp.ClientTimeout(total=10),
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                return "ok" if "errors" not in data else "invalid_auth"
            if resp.status in (401, 403):
                return "invalid_auth"
            return "cannot_connect"
    except Exception:
        return "cannot_connect"


def _number(
    minimum: float,
    maximum: float,
    step: float,
    unit: str | None = None,
    *,
    slider: bool = False,
) -> selector.NumberSelector:
    """A numeric field.

    The nested ``NumberSelector(NumberSelectorConfig(...))`` construction
    appeared eighty-two times in this file; collapsing it makes each field one
    readable line, so a form reads as a list of settings rather than as a wall
    of constructor calls.
    """
    config: dict[str, Any] = {
        "min": minimum,
        "max": maximum,
        "step": step,
        "mode": (
            selector.NumberSelectorMode.SLIDER
            if slider
            else selector.NumberSelectorMode.BOX
        ),
    }
    if unit is not None:
        config["unit_of_measurement"] = unit
    return selector.NumberSelector(selector.NumberSelectorConfig(**config))


# --- Nominal bounds for the thermal model ----------------------------------
#
# These are the ranges the expert page and the initial setup flow accept for
# the parameters ``presets.derive`` writes. They were originally guessed
# around one 140 m² house with floor heating, and the guess was narrower than
# the physics: ``derive`` scales everything by heated area, so the same
# archetype at 40 m² or 400 m² lands far outside a range chosen for the
# middle. A radiator-only house derives a ``slab_thermal_mass`` — the emitter
# loop's few litres of water and steel — of about 0.002 kWh/°C per m², i.e.
# 0.1 to 0.8 for any ordinary house, against a field that used to start at 1.
#
# So each pair below covers what ``derive`` can emit for a *plausible*
# building — 40 to 400 m² of heated area, every structure, era, foundation,
# emitter pair and zone split — with modest headroom, and no more. The
# extremes the questionnaire still allows (a 20 m² cabin, a 1000 m² block)
# are not covered here on purpose: a range wide enough for those would stop
# catching a mistyped number, and a stored value outside its field's range
# is admitted anyway by ``_fit_stored_values`` above, which relaxes only the
# one field that holds it. ``tests/entities.py`` pins both halves.
#
# kWh/°C. 0.72 is a 40 m² timber house on a crawlspace; 62.5 a 400 m² masonry
# house with a heated basement. Only the *fast* store — air, furnishings and
# light fabric — lives here; heavy floors are in the slab mass below.
RANGE_HOUSE_THERMAL_MASS: Final = (0.5, 80.0)
# kW/°C. 0.0140 is a 40 m² low-energy house (14 W/K), 0.7316 a 400 m²
# pre-1960 one with a heated basement. The ceiling is unchanged.
RANGE_HOUSE_HEAT_LOSS: Final = (0.01, 1.0)
# kWh/°C. 0.1 is the radiator loop of a small house, and it is where three
# things meet: ``derive`` floors its radiator-loop mass there, the whole
# 20–1000 m² sweep bottoms out there exactly, and ``ThermalParameters.clamp``
# raises anything below it to ``THERMAL_MASS_FLOOR`` anyway. A lower field
# minimum would only buy a window in which the page stores a number the model
# silently overrides. 53.0 is a 400 m² masonry house's heated slab.
RANGE_SLAB_THERMAL_MASS: Final = (0.1, 60.0)
# kW/°C. ``derive`` floors this at 0.05; a 400 m² floor circuit reaches 4.0.
# The ceiling is unchanged.
RANGE_SLAB_HEAT_TRANSFER: Final = (0.02, 5.0)
# kWh/°C per zone. ``derive`` floors both at 0.5; the heaviest zone of a
# 400 m² masonry house with a heated basement is 58.45. The two zones share
# one range because either can be the heavy one, depending on the emitters.
RANGE_ZONE_THERMAL_MASS: Final = (0.25, 60.0)
# kW/°C per zone. A tenth of a 40 m² low-energy house is 0.0014; nine tenths
# of a 400 m² pre-1960 one with a basement is 0.6584. A single zone cannot
# lose more than the whole house, so the ceiling matches RANGE_HOUSE_HEAT_LOSS.
RANGE_ZONE_HEAT_LOSS: Final = (0.001, 1.0)


# Shown on the expert page while the questionnaire is armed. English here
# is the fallback; the translated text lives beside the page's own strings.
# Shown on the expert page while the questionnaire is armed. Home Assistant
# validates strings.json against a fixed schema, and a step may only carry
# title/description/data/data_description/menu_options/submit/sections -- a
# free-standing sentence under the step is rejected by hassfest. A
# description *placeholder* is substituted verbatim by the frontend, so the
# text has to be chosen here, by language, rather than looked up.
PRESET_WARNING: Final = {
    "en": "Deriving from the building type is switched on, so saving Building type and emitters recalculates the house thermal mass, heat loss, slab mass and slab transfer below (and the two-zone values) from the questionnaire, overwriting whatever is here. Changing any of those fields to a different value switches the derivation off, so your value stays; simply saving this page again does not.",
    "sv": "Härledning från hustypen är påslagen, så när sidan Hustyp och värmesystem sparas räknas husets värmekapacitet, värmeförlust, plattans termiska massa och värmeöverföring nedan (samt tvåzonsvärdena) om från formuläret och skriver över det som står här. Ändrar du något av de fälten till ett annat värde stängs härledningen av, så att ditt värde blir kvar; att bara spara sidan igen gör det inte.",
}

# Everything ``presets.derive`` writes into the entry, in the order the
# expert page shows them. The last six only exist in two-zone mode.
# ``tests/entities.py`` checks this against ``derive`` itself, so a new
# derived parameter cannot quietly fall off the list.
DERIVED_THERMAL_KEYS: Final = (
    CONF_HOUSE_THERMAL_MASS,
    CONF_HOUSE_HEAT_LOSS_COEFFICIENT,
    CONF_SLAB_THERMAL_MASS,
    CONF_SLAB_HEAT_TRANSFER,
    CONF_UPPER_FLOOR_THERMAL_MASS,
    CONF_LOWER_FLOOR_THERMAL_MASS,
    CONF_UPPER_FLOOR_HEAT_LOSS,
    CONF_LOWER_FLOOR_HEAT_LOSS,
    CONF_UPPER_FLOOR_AREA_RATIO,
    CONF_RADIATOR_POWER_FRACTION,
)


# The error a page reports on a field whose stored value sits outside that
# field's nominal range. Raised when the form is *shown*, not when it is
# submitted: the value is already on disk, so the user has to be told before
# they press anything — and the whole point of a nominal range is that
# leaving it is worth noticing.
ERROR_STORED_VALUE_OUT_OF_RANGE: Final = "stored_value_out_of_range"


def _prefilled_values(marker: Any) -> list[Any]:
    """What the frontend will put in this field before the user touches it.

    Both mechanisms count. ``description={"suggested_value": x}`` pre-fills
    the box without defaulting the key, and ``default=x`` pre-fills it *and*
    substitutes itself when the key is absent from the submission. Either way
    the value comes back on submit and is validated by this field's own
    selector — so either way, a stored value the selector rejects makes the
    page impossible to save.
    """
    values: list[Any] = []
    description = getattr(marker, "description", None)
    if isinstance(description, dict) and "suggested_value" in description:
        values.append(description["suggested_value"])
    default = getattr(marker, "default", None)
    # A marker without a default carries voluptuous' UNDEFINED sentinel here,
    # which is not callable; only a real default is.
    if callable(default):
        try:
            values.append(default())
        except Exception:  # noqa: BLE001 - a broken default is not our business
            pass
    return values


def _widen_to_fit(
    number: selector.NumberSelector, values: list[Any]
) -> selector.NumberSelector | None:
    """The same field with bounds stretched to admit ``values``, or None.

    Returns None when nothing needs to move, so an untouched page keeps the
    very selector object it declared.
    """
    config = dict(number.config)
    low = config.get("min")
    high = config.get("max")
    if low is None and high is None:
        return None
    fitted_low, fitted_high = low, high
    for value in values:
        try:
            number_value = float(value)
        except (TypeError, ValueError):
            continue
        if number_value != number_value or number_value in (
            float("inf"),
            float("-inf"),
        ):
            continue
        if fitted_low is not None and number_value < fitted_low:
            fitted_low = number_value
        if fitted_high is not None and number_value > fitted_high:
            fitted_high = number_value
    if fitted_low == low and fitted_high == high:
        return None
    if fitted_low is not None:
        config["min"] = fitted_low
    if fitted_high is not None:
        config["max"] = fitted_high
    return selector.NumberSelector(selector.NumberSelectorConfig(**config))


def _fit_stored_values(schema: Any) -> tuple[Any, list[str]]:
    """Schema with every numeric field widened to admit what it displays.

    A bounded numeric field is validated on submit against its own min/max,
    and the frontend submits the whole form — including the fields nobody
    touched. So a *stored* value outside a field's range does not merely look
    odd: it makes the entire page un-submittable, silently, because
    voluptuous rejects the submission before any handler sees it and the
    dialog just re-renders. The user experiences a Submit button that does
    nothing.

    That is not hypothetical: ``presets.derive`` scales the thermal
    parameters by heated area and knows nothing about the bounds the expert
    page happens to declare, and a radiator-only house legitimately derives a
    ``slab_thermal_mass`` an order of magnitude below what that field used to
    accept.

    So whenever a value is already on disk, the field that displays it
    relaxes far enough to display it — and no further. Every other field
    keeps its nominal bounds, which is what makes them worth having. The
    caller gets back the list of fields that had to relax, so it can say so.
    """
    if schema is None or not hasattr(schema, "schema"):
        return schema, []
    fitted: dict[Any, Any] = {}
    widened: list[str] = []
    for marker, value in schema.schema.items():
        if isinstance(value, selector.NumberSelector):
            replacement = _widen_to_fit(value, _prefilled_values(marker))
            if replacement is not None:
                value = replacement
                widened.append(str(getattr(marker, "schema", marker)))
        fitted[marker] = value
    if not widened:
        return schema, []
    return vol.Schema(fitted), widened


class _StoredValuesAlwaysFit:
    """Mixin: a page can never be blocked by a value already on disk.

    Applied to both flows rather than to one page, because the hazard is
    structural — any bounded numeric field fed from stored configuration can
    reach it, and the stored value need not have come from this integration's
    own forms (``apply_schedule`` and the climate entity both write config
    keys straight into the entry's options, with their own wider limits).

    The widening is deliberately paired with an error on the same field. A
    form that silently accepts an implausible number teaches the user
    nothing, and the failure this exists to end was invisible: the page
    simply did not save. Whatever else happens, the user must be told which
    field is odd and why.
    """

    @callback
    def async_show_form(self, **kwargs: Any) -> FlowResult:
        """Show a form, first making sure it can be submitted at all."""
        fitted, widened = _fit_stored_values(kwargs.get("data_schema"))
        if widened:
            kwargs["data_schema"] = fitted
            errors = dict(kwargs.get("errors") or {})
            for field in widened:
                # A real validation error on the same field wins: it is about
                # what the user just typed, which is more urgent than a value
                # that has been sitting on disk for months.
                errors.setdefault(field, ERROR_STORED_VALUE_OUT_OF_RANGE)
            kwargs["errors"] = errors
        return super().async_show_form(**kwargs)


def _effective(
    candidate: dict[str, Any], current: dict[str, Any], key: str, default: Any
) -> float:
    """The value a save would leave in force for one field.

    Cross-field rules must judge the *pair that would be stored*, not just
    the submitted form: the options pages save partial pages over existing
    data, so a form that only carries one half of a pair can still create a
    contradiction with the stored other half.
    """
    return float(candidate.get(key, current.get(key, default)))


def _band_errors(
    candidate: dict[str, Any], current: dict[str, Any]
) -> dict[str, str]:
    """Comfort-band contradictions no single selector can catch.

    Each violation lands on the field a user would naturally correct. The
    optimizer treats these bounds as soft penalties, so an inverted band is
    not rejected downstream — the plan just sits in permanent violation,
    which is the same undiagnosable failure mode the DHW deadband check
    exists for.

    The rules themselves live in ``comfort_band`` (v5.1.7), because this form
    stopped being the only way into these fields: the ``apply_schedule``
    service writes ``comfort_temp_day`` and the climate entity's slider writes
    ``target_temperature``, and both used to reach the config entry without
    passing anything like this check. One rule set, three callers.
    """
    return comfort_band.errors(candidate, current)


def _power_errors(
    candidate: dict[str, Any], current: dict[str, Any]
) -> dict[str, str]:
    """A modulation floor above the ceiling inverts the solver's power bounds."""
    if _effective(
        candidate, current, CONF_HEAT_PUMP_MIN_POWER, DEFAULT_HEAT_PUMP_MIN_POWER
    ) > _effective(
        candidate, current, CONF_HEAT_PUMP_MAX_POWER, DEFAULT_HEAT_PUMP_MAX_POWER
    ):
        return {CONF_HEAT_PUMP_MIN_POWER: "min_power_above_max"}
    return {}


def _dhw_min_too_close(candidate: dict[str, Any], current: dict[str, Any]) -> bool:
    """Whether the effective DHW minimum leaves no deadband below the setpoint.

    The apply_schedule service and the card already enforce this margin; a form
    that lets the same pair through would store the one configuration the
    solver cannot express — the tank limits are soft penalties, so an
    impossible minimum is not rejected downstream, the plan just sits in
    permanent slight violation.
    """
    setpoint = candidate.get(
        CONF_DHW_SETPOINT, current.get(CONF_DHW_SETPOINT, DEFAULT_DHW_SETPOINT)
    )
    minimum = candidate.get(
        CONF_DHW_MIN_TEMP, current.get(CONF_DHW_MIN_TEMP, DEFAULT_DHW_MIN_TEMP)
    )
    return float(minimum) > float(setpoint) - DHW_MIN_TEMP_SETPOINT_MARGIN


def _valid_months_spec(spec: Any) -> bool:
    """Whether a #13 month-mask spec parses; empty means every month."""
    text = str(spec or "").strip()
    if not text:
        return True
    try:
        for chunk in text.replace(";", ",").split(","):
            if chunk.strip():
                grid_fee.parse_month_range(chunk)
    except grid_fee.GridFeeError:
        return False
    return True


def _entity_of(
    domain: str | list[str], device_class: str | None = None
) -> selector.EntitySelector:
    """An entity picker, optionally narrowed to a device class.

    The filter is expressed under ``filter`` rather than as top-level
    ``domain``/``device_class`` keys. Those top-level keys are the legacy form:
    Home Assistant still accepts them, but the frontend reads only ``filter``
    when it decides which entities match and which helper types the picker may
    offer to create. With the legacy form the "create helper" shortcut cannot
    resolve a single helper domain, and submits the creation without a name —
    which surfaces to the user as "required key not provided @ data['name']".
    """
    entity_filter: dict[str, Any] = {
        "domain": [domain] if isinstance(domain, str) else list(domain)
    }
    if device_class is not None:
        entity_filter["device_class"] = [device_class]
    return selector.EntitySelector(
        selector.EntitySelectorConfig(filter=[entity_filter])
    )


def _select(options: list[str], translation_key: str) -> selector.SelectSelector:
    """A dropdown of fixed options with a translation key for its labels."""
    return selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=options,
            translation_key=translation_key,
            mode=selector.SelectSelectorMode.DROPDOWN,
        )
    )


def _freq_mode_selector() -> selector.SelectSelector:
    """Observe or control (T7 #61).

    An explicit two-option select rather than a boolean, because the
    words matter: "control" is the moment actuation begins, and the user
    should read that word, not flip an anonymous toggle.
    """
    return selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=[FREQ_MODE_OBSERVE, FREQ_MODE_CONTROL],
            translation_key="freq_control_mode",
            mode=selector.SelectSelectorMode.DROPDOWN,
        )
    )


def _solar_source_selector() -> selector.SelectSelector:
    """Where irradiance comes from.

    Kept as an explicit choice rather than "use Open-Meteo when no sensor
    exists": silently calling an external API on a user's behalf is not a
    decision an integration should make for them.
    """
    return selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=list(SOLAR_SOURCES),
            translation_key="solar_forecast_source",
            mode=selector.SelectSelectorMode.DROPDOWN,
        )
    )


def _solar_location_selector() -> selector.LocationSelector:
    """Map picker for the irradiance coordinate."""
    return selector.LocationSelector(selector.LocationSelectorConfig(radius=False))


def _default_location(hass: HomeAssistant, current: dict[str, Any]) -> dict[str, float]:
    """Pre-fill the map with the configured point, else the HA home location."""
    existing = current.get(CONF_SOLAR_LOCATION)
    if isinstance(existing, dict) and "latitude" in existing:
        return existing
    return {
        "latitude": hass.config.latitude,
        "longitude": hass.config.longitude,
    }


def _questionnaire_fields(current: dict[str, Any]) -> dict[Any, Any]:
    """The building questionnaire, shared by initial setup and options.

    One field list, two flows: the initial ``building_describe`` step and the
    options ``building_preset`` page must ask the identical questions, or the
    two paths would derive different physics for the same answers. Anything
    either page adds around these (the enable flag, the structural extras)
    stays that page's own.
    """
    return {
        vol.Optional(
            CONF_BUILDING_STRUCTURE,
            default=current.get(
                CONF_BUILDING_STRUCTURE, presets.STRUCTURE_TIMBER_SLAB
            ),
        ): _select(list(presets.STRUCTURES), "building_structure"),
        vol.Optional(
            CONF_BUILDING_ERA,
            default=current.get(CONF_BUILDING_ERA, presets.ERA_1980_2005),
        ): _select(list(presets.ERAS), "building_era"),
        vol.Optional(
            CONF_BUILDING_FOUNDATION,
            default=current.get(
                CONF_BUILDING_FOUNDATION, presets.FOUNDATION_NONE
            ),
        ): _select(list(presets.FOUNDATIONS), "building_foundation"),
        vol.Optional(
            CONF_HEATED_AREA,
            default=current.get(CONF_HEATED_AREA, DEFAULT_HEATED_AREA),
        ): _number(20, 1000, 5, "m²"),
        vol.Optional(
            CONF_UPPER_EMITTER,
            default=current.get(CONF_UPPER_EMITTER, presets.EMITTER_RADIATORS),
        ): _select(list(presets.EMITTERS), "emitter"),
        vol.Optional(
            CONF_LOWER_EMITTER,
            default=current.get(CONF_LOWER_EMITTER, presets.EMITTER_FLOOR),
        ): _select(list(presets.EMITTERS), "emitter"),
    }


def _derive_preset(answers: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    """Turn questionnaire answers into thermal-parameter starting values.

    ``two_zone`` follows the same presence rule the rest of the integration
    uses — a fresh setup has no zone keys, so the questionnaire derives a
    single-zone model and never writes the keys whose presence would flip
    two-zone on.
    """
    preset = presets.BuildingPreset(
        structure=answers.get(CONF_BUILDING_STRUCTURE, ""),
        era=answers.get(CONF_BUILDING_ERA, ""),
        foundation=answers.get(CONF_BUILDING_FOUNDATION, ""),
        heated_area_m2=float(answers.get(CONF_HEATED_AREA, DEFAULT_HEATED_AREA)),
        upper_emitter=answers.get(CONF_UPPER_EMITTER, ""),
        lower_emitter=answers.get(CONF_LOWER_EMITTER, ""),
        upper_area_ratio=float(
            current.get(CONF_UPPER_FLOOR_AREA_RATIO, DEFAULT_UPPER_FLOOR_AREA_RATIO)
        ),
        two_zone=bool(current.get(CONF_UPPER_FLOOR_THERMAL_MASS)),
    )
    derived = presets.derive(preset)
    # The derived response time is informational; it is not a thermal
    # parameter and would be rejected by the model.
    derived.pop("heating_response_hours", None)
    return derived


async def _translated_text(
    hass: HomeAssistant, flow_type: str, path: str, fallback: str
) -> str:
    """One translated sentence for a description placeholder.

    Placeholder *values* are substituted verbatim by the frontend, so a
    sentence composed here would ship in English whatever the user's
    language is. The catalogue is read the same way ``_translated_menu``
    reads it, and the English text stays in code as the fallback for the
    moment the lookup fails.
    """
    try:
        translations = await async_get_translations(
            hass, hass.config.language, flow_type, {DOMAIN}
        )
    except Exception:  # noqa: BLE001 - a form must never fail to render
        _LOGGER.debug("Could not load %s translations", flow_type, exc_info=True)
        return fallback
    return translations.get(f"component.{DOMAIN}.{flow_type}.{path}") or fallback


async def _translated_menu(
    hass: HomeAssistant, flow_type: str, step_id: str, labels: dict[str, str]
) -> dict[str, str]:
    """Menu entries as explicit ``step id -> label`` pairs.

    Passing plain step ids instead would leave the frontend to translate
    them, and it renders an empty row when that lookup comes back empty,
    which shows up as a menu of unreadable blank lines. Supplying the label
    ourselves means the menu is always legible; the translation is still
    used whenever it resolves.
    """
    labels = dict(labels)
    try:
        translations = await async_get_translations(
            hass, hass.config.language, flow_type, {DOMAIN}
        )
    except Exception:  # noqa: BLE001 - a menu must never fail to render
        _LOGGER.debug("Could not load %s menu translations", flow_type, exc_info=True)
        return labels

    prefix = f"component.{DOMAIN}.{flow_type}.step.{step_id}.menu_options."
    for entry in labels:
        translated = translations.get(f"{prefix}{entry}")
        if translated:
            labels[entry] = translated
    return labels


class HeatPumpOptimizerConfigFlow(
    _StoredValuesAlwaysFit, config_entries.ConfigFlow, domain=DOMAIN
):
    """Handle a config flow for Heat Pump Optimizer."""

    VERSION = CONFIG_ENTRY_VERSION

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step — API credentials and entity selection."""
        errors: dict[str, str] = {}

        if user_input is not None:
            verdict = await validate_tibber_token(
                self.hass, user_input[CONF_TIBBER_TOKEN]
            )
            if verdict == "invalid_auth":
                errors[CONF_TIBBER_TOKEN] = "invalid_tibber_token"
            elif verdict != "ok":
                errors[CONF_TIBBER_TOKEN] = "cannot_connect"
            else:
                self._data.update(user_input)
                return await self.async_step_temperature()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default="Heat Pump Optimizer"): str,
                    vol.Required(CONF_TIBBER_TOKEN): str,
                    vol.Required(CONF_WEATHER_ENTITY): _entity_of("weather"),
                    vol.Optional(CONF_INDOOR_TEMP_ENTITY): _entity_of("sensor", "temperature"),
                    vol.Optional(CONF_OUTDOOR_TEMP_ENTITY): _entity_of("sensor", "temperature"),
                    vol.Optional(CONF_HEAT_PUMP_SWITCH_ENTITY): _entity_of("switch"),
                    vol.Optional(CONF_SOLAR_RADIATION_ENTITY): _entity_of("sensor"),
                    vol.Optional(
                        CONF_SOLAR_FORECAST_SOURCE,
                        default=DEFAULT_SOLAR_FORECAST_SOURCE,
                    ): _solar_source_selector(),
                    vol.Optional(
                        CONF_SOLAR_LOCATION,
                        default=_default_location(self.hass, {}),
                    ): _solar_location_selector(),
                    vol.Optional(CONF_FLOOR_RETURN_TEMP_ENTITY): _entity_of("sensor", "temperature"),
                    vol.Optional(CONF_LOWER_FLOOR_TEMP_ENTITY): _entity_of("sensor", "temperature"),
                    vol.Optional(CONF_DHW_TEMP_ENTITY): _entity_of("sensor", "temperature"),
                    vol.Optional(
                        CONF_BUFFER_TANK_TEMP_ENTITY
                    ): _entity_of("sensor", "temperature"),
                    # v5.3.0: what the pump reports about itself. Read only —
                    # the optimizer never writes the mode — and every one of
                    # them optional, so an install that leaves all four empty
                    # behaves exactly as it did before they existed.
                    vol.Optional(CONF_HEAT_PUMP_MODE_ENTITY): _entity_of(
                        list(topology.ASSIGNABLE_KEYS[CONF_HEAT_PUMP_MODE_ENTITY])
                    ),
                    vol.Optional(CONF_HEAT_PUMP_DEFROST_ENTITY): _entity_of(
                        list(topology.ASSIGNABLE_KEYS[CONF_HEAT_PUMP_DEFROST_ENTITY])
                    ),
                    vol.Optional(CONF_HEAT_PUMP_ONLINE_ENTITY): _entity_of(
                        list(topology.ASSIGNABLE_KEYS[CONF_HEAT_PUMP_ONLINE_ENTITY])
                    ),
                    vol.Optional(CONF_HEAT_PUMP_FAULT_ENTITY): _entity_of(
                        list(topology.ASSIGNABLE_KEYS[CONF_HEAT_PUMP_FAULT_ENTITY])
                    ),
                    # The Danfoss ECL110 MQTT fields lived here until v4.1.0.
                    # Eight fields only ECL110 owners can answer do not belong
                    # on everyone's first screen; the options page "Heat curve
                    # control (ECL110)" owns them, and every reader falls back
                    # to the same defaults when the keys are absent.
                }
            ),
            errors=errors,
            description_placeholders={
                "tibber_info": "Get your token from https://developer.tibber.com",
            },
        )

    async def async_step_temperature(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle temperature configuration step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = _band_errors(user_input, self._data)
            if not errors:
                self._data.update(user_input)
                return await self.async_step_building()

        return self.async_show_form(
            step_id="temperature",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_TARGET_TEMP, default=DEFAULT_TARGET_TEMP
                    ): _number(15, 28, 0.5, "°C", slider=True),
                    vol.Required(
                        CONF_MIN_TEMP, default=DEFAULT_MIN_TEMP
                    ): _number(14, 25, 0.5, "°C", slider=True),
                    vol.Required(
                        CONF_MAX_TEMP, default=DEFAULT_MAX_TEMP
                    ): _number(18, 28, 0.5, "°C", slider=True),
                    vol.Required(
                        CONF_COMFORT_TEMP_DAY, default=DEFAULT_COMFORT_TEMP_DAY
                    ): _number(16, 26, 0.5, "°C", slider=True),
                    vol.Required(
                        CONF_COMFORT_TEMP_NIGHT, default=DEFAULT_COMFORT_TEMP_NIGHT
                    ): _number(15, 24, 0.5, "°C", slider=True),
                    vol.Required(
                        CONF_DAY_START_HOUR, default=DEFAULT_DAY_START_HOUR
                    ): _number(0, 12, 1, slider=True),
                    vol.Required(
                        CONF_DAY_END_HOUR, default=DEFAULT_DAY_END_HOUR
                    ): _number(18, 23, 1, slider=True),
                }
            ),
        )

    async def async_step_building(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Choose how the thermal model gets its starting values.

        The raw ``thermal`` page asks for kWh/°C, which nobody knows; the
        questionnaire asks what the house is made of and derives the physics
        (presets.py). Both paths exist because both users exist — someone
        holding a real energy declaration should not be forced through an
        approximation of it.
        """
        return self.async_show_menu(
            step_id="building",
            menu_options=await _translated_menu(
                self.hass,
                "config",
                "building",
                {
                    "building_describe": "Describe my building (recommended)",
                    "thermal": "Enter thermal values directly",
                },
            ),
        )

    async def async_step_building_describe(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """The questionnaire path: answerable questions instead of kWh/°C.

        Stores the answers themselves (so the options page shows them back),
        marks the preset enabled, and writes the derived physics where the
        ``thermal`` step would have written hand-typed numbers. The ``zones``
        step is skipped entirely: its voluptuous defaults would write the
        two-zone presence keys on every fresh install, which is exactly the
        one-specific-house prior presets.py exists to end.
        """
        if user_input is not None:
            self._data.update(user_input)
            self._data[CONF_BUILDING_PRESET_ENABLED] = True
            self._data.update(_derive_preset(user_input, self._data))
            return await self.async_step_building_extras()

        return self.async_show_form(
            step_id="building_describe",
            data_schema=vol.Schema(_questionnaire_fields(self._data)),
        )

    async def async_step_building_extras(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """What the questionnaire cannot derive: the heat pump itself.

        Three numbers off the nameplate. Everything else the skipped
        ``thermal``/``zones`` pages asked (weights, interval, window and
        solar factors) has a shipped default every reader falls back to,
        and lives in the options pages for anyone who needs it.
        """
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = _power_errors(user_input, self._data)
            if not errors:
                self._data.update(user_input)
                return await self.async_step_dhw()

        return self.async_show_form(
            step_id="building_extras",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HEAT_PUMP_COP_NOMINAL,
                        default=DEFAULT_HEAT_PUMP_COP_NOMINAL,
                    ): _number(1.5, 6.0, 0.1),
                    vol.Required(
                        CONF_HEAT_PUMP_MAX_POWER, default=DEFAULT_HEAT_PUMP_MAX_POWER
                    ): _number(1, 20, 0.5, "kW"),
                    vol.Required(
                        CONF_HEAT_PUMP_MIN_POWER, default=DEFAULT_HEAT_PUMP_MIN_POWER
                    ): _number(0, 10, 0.5, "kW"),
                }
            ),
        )

    async def async_step_thermal(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle thermal model configuration step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = _power_errors(user_input, self._data)
            if not errors:
                self._data.update(user_input)
                return await self.async_step_zones()

        return self.async_show_form(
            step_id="thermal",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOUSE_THERMAL_MASS, default=DEFAULT_HOUSE_THERMAL_MASS
                    ): _number(*RANGE_HOUSE_THERMAL_MASS, 0.5, "kWh/°C"),
                    vol.Required(
                        CONF_HOUSE_HEAT_LOSS_COEFFICIENT,
                        default=DEFAULT_HOUSE_HEAT_LOSS_COEFFICIENT,
                    ): _number(*RANGE_HOUSE_HEAT_LOSS, 0.01, "kW/°C"),
                    vol.Required(
                        CONF_SLAB_THERMAL_MASS, default=DEFAULT_SLAB_THERMAL_MASS
                    ): _number(*RANGE_SLAB_THERMAL_MASS, 0.5, "kWh/°C"),
                    vol.Required(
                        CONF_SLAB_HEAT_TRANSFER, default=DEFAULT_SLAB_HEAT_TRANSFER
                    ): _number(*RANGE_SLAB_HEAT_TRANSFER, 0.1, "kW/°C"),
                    vol.Required(
                        CONF_HEAT_PUMP_COP_NOMINAL,
                        default=DEFAULT_HEAT_PUMP_COP_NOMINAL,
                    ): _number(1.5, 6.0, 0.1),
                    vol.Required(
                        CONF_HEAT_PUMP_MAX_POWER, default=DEFAULT_HEAT_PUMP_MAX_POWER
                    ): _number(1, 20, 0.5, "kW"),
                    vol.Required(
                        CONF_HEAT_PUMP_MIN_POWER, default=DEFAULT_HEAT_PUMP_MIN_POWER
                    ): _number(0, 10, 0.5, "kW"),
                    vol.Required(
                        CONF_OPTIMIZATION_INTERVAL,
                        default=DEFAULT_OPTIMIZATION_INTERVAL,
                    ): _number(10, 120, 5, "min", slider=True),
                    vol.Required(
                        CONF_PRICE_WEIGHT, default=DEFAULT_PRICE_WEIGHT
                    ): _number(0.1, 10, 0.1),
                    vol.Required(
                        CONF_COMFORT_WEIGHT, default=DEFAULT_COMFORT_WEIGHT
                    ): _number(0.1, 20, 0.1),
                }
            ),
        )

    async def async_step_zones(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle two-zone and solar configuration (optional step)."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_dhw()

        return self.async_show_form(
            step_id="zones",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_UPPER_FLOOR_THERMAL_MASS,
                        default=DEFAULT_UPPER_FLOOR_THERMAL_MASS,
                    ): _number(*RANGE_ZONE_THERMAL_MASS, 0.5, "kWh/°C"),
                    vol.Optional(
                        CONF_LOWER_FLOOR_THERMAL_MASS,
                        default=DEFAULT_LOWER_FLOOR_THERMAL_MASS,
                    ): _number(*RANGE_ZONE_THERMAL_MASS, 0.5, "kWh/°C"),
                    vol.Optional(
                        CONF_UPPER_FLOOR_HEAT_LOSS,
                        default=DEFAULT_UPPER_FLOOR_HEAT_LOSS,
                    ): _number(*RANGE_ZONE_HEAT_LOSS, 0.01, "kW/°C"),
                    vol.Optional(
                        CONF_LOWER_FLOOR_HEAT_LOSS,
                        default=DEFAULT_LOWER_FLOOR_HEAT_LOSS,
                    ): _number(*RANGE_ZONE_HEAT_LOSS, 0.01, "kW/°C"),
                    vol.Optional(
                        CONF_INTER_ZONE_TRANSFER,
                        default=DEFAULT_INTER_ZONE_TRANSFER,
                    ): _number(0.0, 3.0, 0.1, "kW/°C"),
                    vol.Optional(
                        CONF_RADIATOR_POWER_FRACTION,
                        default=DEFAULT_RADIATOR_POWER_FRACTION,
                    ): _number(0.0, 1.0, 0.05, slider=True),
                    vol.Optional(
                        CONF_UPPER_FLOOR_AREA_RATIO,
                        default=DEFAULT_UPPER_FLOOR_AREA_RATIO,
                    ): _number(0.1, 0.9, 0.05, slider=True),
                    vol.Optional(
                        CONF_BUFFER_TANK_VOLUME,
                        default=DEFAULT_BUFFER_TANK_VOLUME,
                    ): _number(10, 1500, 5, "L"),
                    vol.Optional(
                        CONF_WINDOW_AREA, default=DEFAULT_WINDOW_AREA
                    ): _number(0, 50, 0.5, "m²"),
                    vol.Optional(
                        CONF_SOLAR_ORIENTATION_FACTOR,
                        default=DEFAULT_SOLAR_ORIENTATION_FACTOR,
                    ): _number(0.0, 1.0, 0.05, slider=True),
                    vol.Optional(
                        CONF_SOLAR_HEAT_GAIN_COEFF,
                        default=DEFAULT_SOLAR_HEAT_GAIN_COEFF,
                    ): _number(0.1, 1.0, 0.05, slider=True),
                }
            ),
        )

    async def async_step_dhw(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle DHW (Domestic Hot Water) configuration step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if not is_valid_spec(user_input.get(CONF_DHW_WINDOWS, "")):
                errors[CONF_DHW_WINDOWS] = "invalid_dhw_windows"
            elif _dhw_min_too_close(user_input, self._data):
                errors[CONF_DHW_MIN_TEMP] = "dhw_min_too_close"
            else:
                self._data.update(user_input)
                return await self.async_step_weather_sensitivity()

        return self.async_show_form(
            step_id="dhw",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_DHW_TANK_VOLUME,
                        default=DEFAULT_DHW_TANK_VOLUME,
                    ): _number(50, 1500, 10, "L"),
                    vol.Optional(
                        CONF_DHW_SETPOINT,
                        default=DEFAULT_DHW_SETPOINT,
                    ): _number(40, 65, 1, "°C", slider=True),
                    vol.Optional(
                        CONF_DHW_MIN_TEMP,
                        default=DEFAULT_DHW_MIN_TEMP,
                    ): _number(35, 55, 1, "°C", slider=True),
                    vol.Optional(
                        CONF_DHW_DAILY_CONSUMPTION,
                        default=DEFAULT_DHW_DAILY_CONSUMPTION,
                    ): _number(50, 1500, 10, "L/day"),
                    vol.Optional(
                        CONF_DHW_COOLING_RATE,
                        default=DEFAULT_DHW_COOLING_RATE,
                    ): _number(0.05, 3.0, 0.05, "°C/h"),
                    vol.Optional(
                        CONF_DHW_SCHEDULE_ENABLED,
                        default=DEFAULT_DHW_SCHEDULE_ENABLED,
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_DHW_WINDOWS,
                        default=DEFAULT_DHW_WINDOWS,
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        )
                    ),
                    vol.Optional(
                        CONF_DHW_IDLE_MIN_TEMP,
                        default=DEFAULT_DHW_IDLE_MIN_TEMP,
                    ): _number(10, 55, 1, "°C", slider=True),
                    vol.Optional(
                        CONF_DHW_LEGIONELLA_ENABLED,
                        default=DEFAULT_DHW_LEGIONELLA_ENABLED,
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_DHW_LEGIONELLA_TEMP,
                        default=DEFAULT_DHW_LEGIONELLA_TEMP,
                    ): _number(55, 70, 1, "°C", slider=True),
                    vol.Optional(
                        CONF_DHW_LEGIONELLA_INTERVAL_DAYS,
                        default=DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS,
                    ): _number(1, 30, 1, "days", slider=True),
                }
            ),
        )

    async def async_step_weather_sensitivity(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle weather sensitivity configuration step."""
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(
                title=self._data.get(CONF_NAME, "Heat Pump Optimizer"),
                data=self._data,
            )

        return self.async_show_form(
            step_id="weather_sensitivity",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_WIND_SENSITIVITY,
                        default=DEFAULT_WIND_SENSITIVITY,
                    ): _number(0.0, 0.5, 0.01),
                    vol.Optional(
                        CONF_RAIN_HEAT_LOSS_MULTIPLIER,
                        default=DEFAULT_RAIN_HEAT_LOSS_MULTIPLIER,
                    ): _number(1.0, 1.5, 0.01),
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> HeatPumpOptimizerOptionsFlow:
        """Get the options flow for this handler."""
        return HeatPumpOptimizerOptionsFlow(config_entry)


class HeatPumpOptimizerOptionsFlow(_StoredValuesAlwaysFit, config_entries.OptionsFlow):
    """Handle options flow for Heat Pump Optimizer.

    The options are split into a menu of focused pages rather than one very
    long form, so that changing a single setting does not mean scrolling past
    forty unrelated fields.
    """

    # Entity fields on the "Sensors and entities" page. A cleared selector is
    # simply absent from ``user_input``, and because options are merged on top
    # of the original setup data, an absent key would silently restore the old
    # entity. These are written back explicitly as ``None`` so clearing them
    # sticks — but only for the fields this page actually renders: nulling the
    # whole roster wiped the PV, away and external-heat entities configured on
    # their own pages every time this one was saved.
    _ENTITIES_PAGE_KEYS = (
        CONF_INDOOR_TEMP_ENTITY,
        CONF_OUTDOOR_TEMP_ENTITY,
        CONF_HEAT_PUMP_SWITCH_ENTITY,
        CONF_SOLAR_RADIATION_ENTITY,
        CONF_FLOOR_RETURN_TEMP_ENTITY,
        CONF_LOWER_FLOOR_TEMP_ENTITY,
        CONF_DHW_TEMP_ENTITY,
        CONF_BUFFER_TANK_TEMP_ENTITY,
        CONF_POWER_ENTITY,
        CONF_ENERGY_ENTITY,
        CONF_HOUSE_POWER_ENTITY,
        CONF_COMPRESSOR_FREQ_ENTITY,
        CONF_COMPRESSOR_FREQ_SENSOR,
        CONF_HEAT_PUMP_MODE_ENTITY,
        CONF_HEAT_PUMP_DEFROST_ENTITY,
        CONF_HEAT_PUMP_ONLINE_ENTITY,
        CONF_HEAT_PUMP_FAULT_ENTITY,
    )

    # Every clearable entity across all pages; the solar, away, learning and
    # building pages clear their own members in their own handlers.
    _OPTIONAL_ENTITY_KEYS = _ENTITIES_PAGE_KEYS + (
        CONF_EXTERNAL_HEAT_ENTITY,
        CONF_VALVE_OUTLET_TEMP_ENTITY,
        CONF_WOOD_TANK_TOP_ENTITY,
        CONF_WOOD_TANK_BOTTOM_ENTITY,
        CONF_MIXING_VALVE_TARGET_ENTITY,
        CONF_MIXING_VALVE_WRITE_ENTITY,
        CONF_PV_PRODUCTION_ENTITY,
        CONF_PV_EXPORT_PRICE_ENTITY,
        CONF_AWAY_PRESENCE_ENTITY,
        CONF_AWAY_RETURN_ENTITY,
        CONF_GRID_FEE_ENTITY,
        CONF_DHW_INLET_ENTITY,
        CONF_VVC_PUMP_ENTITY,
        CONF_SPACE_PUMP_ENTITY,
        CONF_INDOOR_HUMIDITY_ENTITY,
    )

    # Fallback labels for the menus, used when the frontend has no translation
    # to show. This stays the flat roster of every *leaf* page — the golden
    # capture and the entity tests walk it expecting each entry to render a
    # form — while the two tuples below decide where each page appears. The
    # synthetic ``advanced`` menu entry is deliberately not a member: it opens
    # the second menu, not a form.
    _MENU_LABELS = {
        "setup_overview": "Your system, as configured",
        "entities": "Sensors and entities",
        "comfort": "Comfort and temperatures",
        "hot_water": "Hot water",
        "building": "Heating system and heat storage",
        "building_preset": "Building type and emitters",
        "thermal_model": "Thermal model (expert)",
        "tuning": "Savings vs comfort",
        "grid": "Grid costs",
        "solar_pv": "Solar panels",
        "away": "Away and holiday mode",
        "learning": "Self-learning and diagnostics",
        "heat_curve": "Heat curve control (ECL110)",
    }

    # The pages a household actually revisits. Everything else moves behind
    # one extra click so the first menu reads as questions a user has, not as
    # a map of the integration's internals. ``section()`` was considered and
    # rejected for this: the pinned minimum HA version predates it and the
    # golden capture walks schemas one level deep, so grouped fields would
    # silently fall out of the fingerprint — a submenu works everywhere.
    _TOP_MENU = ("setup_overview", "comfort", "hot_water", "tuning", "grid", "away")

    # Set-once configuration: sensors, building physics, actuation plumbing.
    _ADVANCED_MENU = (
        "entities",
        "building",
        "building_preset",
        "thermal_model",
        "solar_pv",
        "learning",
        "heat_curve",
    )

    _ADVANCED_LABEL = "Advanced settings"

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        # Assigning to ``self.config_entry`` goes through a property setter that
        # Home Assistant deprecated in 2024.11 and removed in 2025.12, which makes
        # the options flow raise and the frontend report a 500 error. Keep our own
        # reference instead so the flow works on every supported version.
        self._entry = config_entry

    @property
    def _current(self) -> dict[str, Any]:
        """Effective configuration: setup data with saved options applied."""
        return {**self._entry.data, **self._entry.options}

    def _save(self, user_input: dict[str, Any]) -> FlowResult:
        """Persist one page without discarding settings from the other pages."""
        return self.async_create_entry(
            title="", data={**self._entry.options, **user_input}
        )

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Show the top-level options menu."""
        labels = {step: self._MENU_LABELS[step] for step in self._TOP_MENU}
        labels["advanced"] = self._ADVANCED_LABEL
        return self.async_show_menu(
            step_id="init",
            menu_options=await _translated_menu(self.hass, "options", "init", labels),
        )

    async def async_step_advanced(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Show the advanced submenu of set-once pages."""
        labels = {step: self._MENU_LABELS[step] for step in self._ADVANCED_MENU}
        return self.async_show_menu(
            step_id="advanced",
            menu_options=await _translated_menu(
                self.hass, "options", "advanced", labels
            ),
        )

    async def async_step_setup_overview(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Item 32: a read-only picture of the configured system.

        Rendered from the same ``describe_setup`` the card's setup page uses,
        so the two can never disagree about what the system looks like. Empty
        sensor slots are shown as empty on purpose — the point is to reveal
        what is missing, and a diagram that silently omits an unconfigured
        sensor looks complete. Click-to-assign is deliberately deferred: a
        config flow renders a voluptuous schema, and a genuinely interactive
        drawing means a custom panel. This page is the staging the item
        recommends.
        """
        if user_input is not None:
            return await self.async_step_init()
        setup = topology.describe_setup(self._current)
        return self.async_show_form(
            step_id="setup_overview",
            data_schema=vol.Schema({}),
            description_placeholders={
                "setup_summary": topology.render_text_summary(setup)
            },
        )

    async def async_step_entities(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Change which Home Assistant entities the optimizer reads."""
        errors: dict[str, str] = {}
        current = self._current

        if user_input is not None:
            token = user_input.get(CONF_TIBBER_TOKEN)
            if token and token != current.get(CONF_TIBBER_TOKEN):
                verdict = await validate_tibber_token(self.hass, token)
                if verdict == "invalid_auth":
                    errors[CONF_TIBBER_TOKEN] = "invalid_tibber_token"
                elif verdict != "ok":
                    errors[CONF_TIBBER_TOKEN] = "cannot_connect"
            if not errors:
                cleaned = dict(user_input)
                for key in self._ENTITIES_PAGE_KEYS:
                    if not cleaned.get(key):
                        cleaned[key] = None
                return self._save(cleaned)
            current = {**current, **user_input}

        def _entity(key: str) -> Any:
            """Optional key that keeps the currently configured entity as default."""
            existing = current.get(key)
            if existing:
                return vol.Optional(key, default=existing)
            return vol.Optional(key)

        return self.async_show_form(
            step_id="entities",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_TIBBER_TOKEN,
                        default=current.get(CONF_TIBBER_TOKEN, ""),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD
                        )
                    ),
                    vol.Required(
                        CONF_WEATHER_ENTITY,
                        default=current.get(CONF_WEATHER_ENTITY, ""),
                    ): _entity_of("weather"),
                    _entity(CONF_INDOOR_TEMP_ENTITY): _entity_of("sensor", "temperature"),
                    _entity(CONF_OUTDOOR_TEMP_ENTITY): _entity_of("sensor", "temperature"),
                    _entity(CONF_SOLAR_RADIATION_ENTITY): _entity_of("sensor"),
                    vol.Optional(
                        CONF_SOLAR_FORECAST_SOURCE,
                        default=current.get(
                            CONF_SOLAR_FORECAST_SOURCE,
                            DEFAULT_SOLAR_FORECAST_SOURCE,
                        ),
                    ): _solar_source_selector(),
                    vol.Optional(
                        CONF_SOLAR_LOCATION,
                        default=_default_location(self.hass, current),
                    ): _solar_location_selector(),
                    _entity(CONF_DHW_TEMP_ENTITY): _entity_of("sensor", "temperature"),
                    _entity(CONF_BUFFER_TANK_TEMP_ENTITY): _entity_of("sensor", "temperature"),
                    _entity(CONF_FLOOR_RETURN_TEMP_ENTITY): _entity_of("sensor", "temperature"),
                    _entity(CONF_LOWER_FLOOR_TEMP_ENTITY): _entity_of("sensor", "temperature"),
                    _entity(CONF_HEAT_PUMP_SWITCH_ENTITY): _entity_of("switch"),
                    # Measured electrical draw. Optional, and everything that
                    # uses it degrades cleanly without it — but with it, COP
                    # becomes observable, predicted cost gets a realised
                    # counterpart, and the external-heat detector gets its
                    # cleanest signal.
                    _entity(CONF_POWER_ENTITY): _entity_of("sensor", "power"),
                    _entity(CONF_ENERGY_ENTITY): _entity_of("sensor", "energy"),
                    # Whole-house load. The capacity tariff is metered at the
                    # connection point, not at the heat pump, so without this
                    # the peak model only sees part of the picture.
                    _entity(CONF_HOUSE_POWER_ENTITY): _entity_of("sensor", "power"),
                    # T7 #61: the compressor frequency number entity, and
                    # which stage runs. Observe (the default) learns and
                    # recommends but never writes; control is the explicit
                    # per-install opt-in AFTER the user has validated the
                    # entity against their real hardware.
                    _entity(CONF_COMPRESSOR_FREQ_ENTITY): _entity_of("number"),
                    # The ACTUAL frequency, when the number above is a
                    # setpoint register that merely echoes what was
                    # written: feedback read from an echo can never
                    # diverge, so without this the watchdog is decorative
                    # and the map learns against a frozen setpoint.
                    _entity(CONF_COMPRESSOR_FREQ_SENSOR): _entity_of(
                        "sensor", "frequency"
                    ),
                    vol.Optional(
                        CONF_FREQ_CONTROL_MODE,
                        default=current.get(
                            CONF_FREQ_CONTROL_MODE, DEFAULT_FREQ_CONTROL_MODE
                        ),
                    ): _freq_mode_selector(),
                    # v5.3.0: the pump's own account of itself. The domains
                    # come from the topology slot table, so the picker here,
                    # the card's picker and the assign_entity service cannot
                    # offer three different answers about what fits a slot.
                    _entity(CONF_HEAT_PUMP_MODE_ENTITY): _entity_of(
                        list(topology.ASSIGNABLE_KEYS[CONF_HEAT_PUMP_MODE_ENTITY])
                    ),
                    _entity(CONF_HEAT_PUMP_DEFROST_ENTITY): _entity_of(
                        list(topology.ASSIGNABLE_KEYS[CONF_HEAT_PUMP_DEFROST_ENTITY])
                    ),
                    _entity(CONF_HEAT_PUMP_ONLINE_ENTITY): _entity_of(
                        list(topology.ASSIGNABLE_KEYS[CONF_HEAT_PUMP_ONLINE_ENTITY])
                    ),
                    _entity(CONF_HEAT_PUMP_FAULT_ENTITY): _entity_of(
                        list(topology.ASSIGNABLE_KEYS[CONF_HEAT_PUMP_FAULT_ENTITY])
                    ),
                }
            ),
        )

    async def async_step_comfort(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """How warm the house should be, and when."""
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = _band_errors(user_input, self._current)
            if not errors:
                cleaned = dict(user_input)
                # This page's clearable entity (T5 #54): an absent selector is
                # written back as None so clearing genuinely clears.
                if not cleaned.get(CONF_INDOOR_HUMIDITY_ENTITY):
                    cleaned[CONF_INDOOR_HUMIDITY_ENTITY] = None
                return self._save(cleaned)

        current = self._current
        if user_input is not None:
            # Re-render the rejected form with what was typed, not with the
            # stored values the user was in the middle of changing.
            current = {**current, **user_input}

        def _entity_default(key: str) -> Any:
            existing = current.get(key)
            if existing:
                return vol.Optional(key, default=existing)
            return vol.Optional(key)
        return self.async_show_form(
            step_id="comfort",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_TARGET_TEMP,
                        default=current.get(CONF_TARGET_TEMP, DEFAULT_TARGET_TEMP),
                    ): _number(15, 28, 0.5, "°C", slider=True),
                    vol.Required(
                        CONF_MIN_TEMP,
                        default=current.get(CONF_MIN_TEMP, DEFAULT_MIN_TEMP),
                    ): _number(14, 25, 0.5, "°C", slider=True),
                    vol.Required(
                        CONF_MAX_TEMP,
                        default=current.get(CONF_MAX_TEMP, DEFAULT_MAX_TEMP),
                    ): _number(18, 28, 0.5, "°C", slider=True),
                    vol.Required(
                        CONF_COMFORT_TEMP_DAY,
                        default=current.get(
                            CONF_COMFORT_TEMP_DAY, DEFAULT_COMFORT_TEMP_DAY
                        ),
                    ): _number(16, 26, 0.5, "°C", slider=True),
                    vol.Required(
                        CONF_COMFORT_TEMP_NIGHT,
                        default=current.get(
                            CONF_COMFORT_TEMP_NIGHT, DEFAULT_COMFORT_TEMP_NIGHT
                        ),
                    ): _number(15, 24, 0.5, "°C", slider=True),
                    vol.Required(
                        CONF_DAY_START_HOUR,
                        default=current.get(
                            CONF_DAY_START_HOUR, DEFAULT_DAY_START_HOUR
                        ),
                    ): _number(0, 12, 1, slider=True),
                    vol.Required(
                        CONF_DAY_END_HOUR,
                        default=current.get(CONF_DAY_END_HOUR, DEFAULT_DAY_END_HOUR),
                    ): _number(18, 23, 1, slider=True),
                    # T5 #54: the mold guard is comfort in the oldest sense
                    # — a floor the house must not coast below. Double-
                    # gated: the flag AND a live indoor humidity sensor.
                    vol.Optional(
                        CONF_MOLD_GUARD_ENABLED,
                        default=current.get(
                            CONF_MOLD_GUARD_ENABLED, DEFAULT_MOLD_GUARD_ENABLED
                        ),
                    ): bool,
                    _entity_default(
                        CONF_INDOOR_HUMIDITY_ENTITY
                    ): _entity_of("sensor", "humidity"),
                    vol.Optional(
                        CONF_THERMAL_BRIDGE_FRSI,
                        default=current.get(
                            CONF_THERMAL_BRIDGE_FRSI, DEFAULT_THERMAL_BRIDGE_FRSI
                        ),
                    ): _number(0.3, 0.98, 0.01),
                }
            ),
        )

    async def async_step_hot_water(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """When hot water is needed and how hot it has to be."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if not is_valid_spec(user_input.get(CONF_DHW_WINDOWS, "")):
                errors[CONF_DHW_WINDOWS] = "invalid_dhw_windows"
            elif _dhw_min_too_close(user_input, self._current):
                errors[CONF_DHW_MIN_TEMP] = "dhw_min_too_close"
            else:
                cleaned = dict(user_input)
                # This page's clearable entities (T3): an absent selector is
                # written back as None so clearing genuinely clears. The
                # presence rule ignores None-valued keys, so this can never
                # phantom-enable hot water.
                for key in (
                    CONF_DHW_INLET_ENTITY,
                    CONF_VVC_PUMP_ENTITY,
                    CONF_SPACE_PUMP_ENTITY,
                ):
                    if not cleaned.get(key):
                        cleaned[key] = None
                return self._save(cleaned)

        current = self._current
        if user_input is not None:
            current = {**current, **user_input}

        def _entity_default(key: str) -> Any:
            existing = current.get(key)
            if existing:
                return vol.Optional(key, default=existing)
            return vol.Optional(key)

        return self.async_show_form(
            step_id="hot_water",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_DHW_SCHEDULE_ENABLED,
                        default=current.get(
                            CONF_DHW_SCHEDULE_ENABLED, DEFAULT_DHW_SCHEDULE_ENABLED
                        ),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_DHW_WINDOWS,
                        default=current.get(CONF_DHW_WINDOWS, DEFAULT_DHW_WINDOWS),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        )
                    ),
                    vol.Optional(
                        CONF_DHW_MIN_TEMP,
                        default=current.get(CONF_DHW_MIN_TEMP, DEFAULT_DHW_MIN_TEMP),
                    ): _number(35, 55, 1, "°C", slider=True),
                    vol.Optional(
                        CONF_DHW_IDLE_MIN_TEMP,
                        default=current.get(
                            CONF_DHW_IDLE_MIN_TEMP, DEFAULT_DHW_IDLE_MIN_TEMP
                        ),
                    ): _number(10, 55, 1, "°C", slider=True),
                    vol.Optional(
                        CONF_DHW_SETPOINT,
                        default=current.get(CONF_DHW_SETPOINT, DEFAULT_DHW_SETPOINT),
                    ): _number(40, 65, 1, "°C", slider=True),
                    vol.Optional(
                        CONF_DHW_TANK_VOLUME,
                        default=current.get(
                            CONF_DHW_TANK_VOLUME, DEFAULT_DHW_TANK_VOLUME
                        ),
                    ): _number(50, 1500, 10, "L"),
                    vol.Optional(
                        CONF_DHW_DAILY_CONSUMPTION,
                        default=current.get(
                            CONF_DHW_DAILY_CONSUMPTION, DEFAULT_DHW_DAILY_CONSUMPTION
                        ),
                    ): _number(50, 1500, 10, "L/day"),
                    vol.Optional(
                        CONF_DHW_COOLING_RATE,
                        default=current.get(
                            CONF_DHW_COOLING_RATE, DEFAULT_DHW_COOLING_RATE
                        ),
                    ): _number(0.05, 3.0, 0.05, "°C/h"),
                    vol.Optional(
                        CONF_DHW_LEGIONELLA_ENABLED,
                        default=current.get(
                            CONF_DHW_LEGIONELLA_ENABLED,
                            DEFAULT_DHW_LEGIONELLA_ENABLED,
                        ),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_DHW_LEGIONELLA_TEMP,
                        default=current.get(
                            CONF_DHW_LEGIONELLA_TEMP, DEFAULT_DHW_LEGIONELLA_TEMP
                        ),
                    ): _number(55, 70, 1, "°C", slider=True),
                    vol.Optional(
                        CONF_DHW_LEGIONELLA_INTERVAL_DAYS,
                        default=current.get(
                            CONF_DHW_LEGIONELLA_INTERVAL_DAYS,
                            DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS,
                        ),
                    ): _number(1, 30, 1, "days", slider=True),
                    # --- v4.0.0 T3 -------------------------------------
                    vol.Optional(
                        CONF_DHW_INLET_TEMP,
                        default=current.get(
                            CONF_DHW_INLET_TEMP, DEFAULT_DHW_INLET_TEMP
                        ),
                    ): _number(2, 25, 0.5, "°C"),
                    vol.Optional(
                        CONF_DHW_INLET_SEASONAL_AMPLITUDE,
                        default=current.get(
                            CONF_DHW_INLET_SEASONAL_AMPLITUDE,
                            DEFAULT_DHW_INLET_SEASONAL_AMPLITUDE,
                        ),
                    ): _number(0, 8, 0.5, "°C"),
                    _entity_default(CONF_DHW_INLET_ENTITY): _entity_of(
                        "sensor", "temperature"
                    ),
                    vol.Optional(
                        CONF_GREYWATER_RECOVERY,
                        default=current.get(
                            CONF_GREYWATER_RECOVERY, DEFAULT_GREYWATER_RECOVERY
                        ),
                    ): _number(0, 0.9, 0.05, None, slider=True),
                    vol.Optional(
                        CONF_DHW_QUANTILE_TARGETS_ENABLED,
                        default=current.get(
                            CONF_DHW_QUANTILE_TARGETS_ENABLED,
                            DEFAULT_DHW_QUANTILE_TARGETS_ENABLED,
                        ),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_DHW_FREE_DISINFECTION_ENABLED,
                        default=current.get(
                            CONF_DHW_FREE_DISINFECTION_ENABLED,
                            DEFAULT_DHW_FREE_DISINFECTION_ENABLED,
                        ),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_DHW_ELASTIC_LEGIONELLA_ENABLED,
                        default=current.get(
                            CONF_DHW_ELASTIC_LEGIONELLA_ENABLED,
                            DEFAULT_DHW_ELASTIC_LEGIONELLA_ENABLED,
                        ),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_DHW_LEGIONELLA_MIN_INTERVAL_DAYS,
                        default=current.get(
                            CONF_DHW_LEGIONELLA_MIN_INTERVAL_DAYS,
                            DEFAULT_DHW_LEGIONELLA_MIN_INTERVAL_DAYS,
                        ),
                    ): _number(1, 14, 1, "days", slider=True),
                    vol.Optional(
                        CONF_SHOWER_FLOW_LPM,
                        default=current.get(
                            CONF_SHOWER_FLOW_LPM, DEFAULT_SHOWER_FLOW_LPM
                        ),
                    ): _number(4, 20, 0.5, "L/min"),
                    _entity_default(CONF_VVC_PUMP_ENTITY): _entity_of(
                        ["switch", "input_boolean"]
                    ),
                    vol.Optional(
                        CONF_VVC_LEAD_MINUTES,
                        default=current.get(
                            CONF_VVC_LEAD_MINUTES, DEFAULT_VVC_LEAD_MINUTES
                        ),
                    ): _number(0, 120, 5, "min", slider=True),
                    _entity_default(CONF_SPACE_PUMP_ENTITY): _entity_of(
                        ["switch", "input_boolean"]
                    ),
                }
            ),
        )

    async def async_step_building(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """The heating system's plumbing: valve, tanks, and the heat split.

        One page for everything between the heat sources and the emitters —
        the mixing valve, the buffer tank as a store, and the wood-furnace
        tank with its probes. These used to be spread across three pages
        (building, mixing valve, and the wood block on the learning page),
        which meant describing one physical system in three places.
        The purely structural properties (windows, wind and rain) live on
        *Building type and emitters* instead.
        """
        if user_input is not None:
            cleaned = dict(user_input)
            # This page's own clearable entities: an absent selector must be
            # written back as None or clearing it silently restores the old
            # entity.
            for key in (
                CONF_MIXING_VALVE_TARGET_ENTITY,
                CONF_MIXING_VALVE_WRITE_ENTITY,
                CONF_VALVE_OUTLET_TEMP_ENTITY,
                CONF_WOOD_TANK_TOP_ENTITY,
                CONF_WOOD_TANK_BOTTOM_ENTITY,
            ):
                if not cleaned.get(key):
                    cleaned[key] = None
            return self._save(cleaned)

        current = self._current

        def _entity(key: str) -> Any:
            """Optional key that keeps the currently configured entity as default."""
            existing = current.get(key)
            if existing:
                return vol.Optional(key, default=existing)
            return vol.Optional(key)

        return self.async_show_form(
            step_id="building",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_MIXING_VALVE_MODE,
                        default=current.get(
                            CONF_MIXING_VALVE_MODE, mixing_valve.MODE_NONE
                        ),
                    ): _select(
                        list(mixing_valve.SELECTABLE_MODES), "mixing_valve_mode"
                    ),
                    # 0 means "use the top of the comfort band", which is also
                    # what a dumb valve is recommended to be set to.
                    vol.Optional(
                        CONF_MIXING_VALVE_TARGET,
                        default=current.get(
                            CONF_MIXING_VALVE_TARGET, DEFAULT_MIXING_VALVE_TARGET
                        ),
                    ): _number(0, 30, 0.5, "°C"),
                    _entity(CONF_MIXING_VALVE_TARGET_ENTITY): _entity_of(
                        "sensor", "temperature"
                    ),
                    # The actuation path for smart_write: the number or
                    # climate entity the valve's own controller exposes.
                    _entity(CONF_MIXING_VALVE_WRITE_ENTITY): _entity_of(
                        ["number", "input_number", "climate"]
                    ),
                    vol.Optional(
                        CONF_BUFFER_TANK_VOLUME,
                        default=current.get(
                            CONF_BUFFER_TANK_VOLUME, DEFAULT_BUFFER_TANK_VOLUME
                        ),
                    ): _number(10, 1500, 5, "L"),
                    vol.Optional(
                        CONF_BUFFER_MAX_TEMP,
                        default=current.get(
                            CONF_BUFFER_MAX_TEMP, DEFAULT_BUFFER_MAX_TEMP
                        ),
                    ): _number(40, 90, 1, "°C", slider=True),
                    # The radiator share is deliberately NOT here even though
                    # the old building page carried it: it is one of the four
                    # two-zone *presence* keys, and this page's voluptuous
                    # defaults write every field on any save — which would
                    # flip a legacy single-zone entry to two-zone the first
                    # time someone configured a valve. It lives on the
                    # thermal_model page, whose fields are presence-safe.
                    # Wood-furnace topology: the valve outlet is the sensor
                    # that turns the boolean fire into a continuous
                    # displacement; the tank pair bounds how long the fire
                    # can back it. The detector itself stays on the learning
                    # page; this is the plumbing it observes.
                    _entity(CONF_VALVE_OUTLET_TEMP_ENTITY): _entity_of(
                        ["sensor"]
                    ),
                    _entity(CONF_WOOD_TANK_TOP_ENTITY): _entity_of(["sensor"]),
                    _entity(CONF_WOOD_TANK_BOTTOM_ENTITY): _entity_of(
                        ["sensor"]
                    ),
                    vol.Optional(
                        CONF_WOOD_TANK_VOLUME,
                        default=current.get(
                            CONF_WOOD_TANK_VOLUME, DEFAULT_WOOD_TANK_VOLUME
                        ),
                    ): _number(50, 3000, 50, "L", slider=True),
                    # How the DHW tank is plumbed to the wood tank. Only bites
                    # with the two-tank model, which is why it sits beside the
                    # tank it depends on (v3.15.1).
                    vol.Optional(
                        CONF_DHW_WOOD_COIL_ENABLED,
                        default=current.get(
                            CONF_DHW_WOOD_COIL_ENABLED,
                            DEFAULT_DHW_WOOD_COIL_ENABLED,
                        ),
                    ): bool,
                }
            ),
        )

    async def async_step_thermal_model(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """The raw numeric thermal model, previously settable only at setup.

        A wrong ``heat_pump_max_power`` or zone split could until now only be
        fixed by deleting the integration and starting over — losing every
        learned parameter with it. This page surfaces those numbers.

        The presence hazard: ``two_zone_enabled`` and ``dhw_enabled`` are not
        flags but *inferences* from whether their keys exist at all
        (``ThermalParameters.from_config``), so a ``vol.Optional`` with a
        default would write that default on any untouched save and silently
        flip a legacy single-zone entry to two-zone. Fields with a stored
        value therefore only *suggest* it back — writing the same value again
        is a no-op — and fields without one render empty; an empty box is
        omitted from ``user_input`` and never saved.
        """
        errors: dict[str, str] = {}
        if user_input is not None:
            # Judged against the *effective* pair: this page saves partial
            # input over stored data, so a submitted floor can contradict a
            # stored ceiling without both being on the form.
            errors = _power_errors(user_input, self._current)
            if not errors:
                saved = dict(user_input)
                stored = self._current
                if any(
                    key in saved and saved[key] != stored.get(key)
                    for key in DERIVED_THERMAL_KEYS
                ):
                    # Editing a derived number here has to mean it. Left
                    # armed, the questionnaire would overwrite this value the
                    # next time that page was saved, and the user would be
                    # back to a number they did not choose with no idea why.
                    #
                    # It has to be a *changed* value, not merely a present
                    # one. ``user_input`` is what the browser posted, and the
                    # browser posts every pre-filled field back — which is
                    # the whole premise of this page's suggested values — so
                    # presence alone is true on a no-op Submit, and testing
                    # it disarmed the questionnaire for every user who had
                    # ever opened this page and pressed the button.
                    saved[CONF_BUILDING_PRESET_ENABLED] = False
                return self._save(saved)

        current = self._current
        if user_input is not None:
            current = {**current, **user_input}

        def _numeric(key: str) -> Any:
            """Optional key that suggests the stored value without defaulting it."""
            if key in current:
                return vol.Optional(
                    key, description={"suggested_value": current[key]}
                )
            return vol.Optional(key)

        # Home Assistant cannot grey a field out — a selector carries no
        # read-only flag, and the schema the browser receives has nowhere to
        # put one — so say in words what the form cannot show.
        preset_warning = ""
        if current.get(
            CONF_BUILDING_PRESET_ENABLED, DEFAULT_BUILDING_PRESET_ENABLED
        ):
            lang = (self.hass.config.language or "en").split("-")[0]
            preset_warning = PRESET_WARNING.get(lang, PRESET_WARNING["en"])

        return self.async_show_form(
            step_id="thermal_model",
            errors=errors,
            description_placeholders={"preset_warning": preset_warning},
            data_schema=vol.Schema(
                {
                    _numeric(CONF_HOUSE_THERMAL_MASS): _number(
                        *RANGE_HOUSE_THERMAL_MASS, 0.5, "kWh/°C"
                    ),
                    _numeric(CONF_HOUSE_HEAT_LOSS_COEFFICIENT): _number(
                        *RANGE_HOUSE_HEAT_LOSS, 0.01, "kW/°C"
                    ),
                    _numeric(CONF_SLAB_THERMAL_MASS): _number(
                        *RANGE_SLAB_THERMAL_MASS, 0.5, "kWh/°C"
                    ),
                    _numeric(CONF_SLAB_HEAT_TRANSFER): _number(
                        *RANGE_SLAB_HEAT_TRANSFER, 0.1, "kW/°C"
                    ),
                    _numeric(CONF_HEAT_PUMP_COP_NOMINAL): _number(1.5, 6.0, 0.1),
                    _numeric(CONF_HEAT_PUMP_MAX_POWER): _number(1, 20, 0.5, "kW"),
                    _numeric(CONF_HEAT_PUMP_MIN_POWER): _number(0, 10, 0.5, "kW"),
                    # The explicit two-zone switch. Presence of the zone keys
                    # below can only ever turn the model on — the initial flow
                    # writes them into entry.data, where this page cannot
                    # erase them — so turning it *off* needs a real override.
                    # Suggested, not defaulted, like every field here: an
                    # untouched save must write nothing.
                    vol.Optional(
                        CONF_TWO_ZONE_MODE,
                        description={
                            "suggested_value": current.get(
                                CONF_TWO_ZONE_MODE, TWO_ZONE_MODE_AUTO
                            )
                        },
                    ): _select(list(TWO_ZONE_MODES), "two_zone_mode"),
                    _numeric(CONF_UPPER_FLOOR_THERMAL_MASS): _number(
                        *RANGE_ZONE_THERMAL_MASS, 0.5, "kWh/°C"
                    ),
                    _numeric(CONF_LOWER_FLOOR_THERMAL_MASS): _number(
                        *RANGE_ZONE_THERMAL_MASS, 0.5, "kWh/°C"
                    ),
                    _numeric(CONF_UPPER_FLOOR_HEAT_LOSS): _number(
                        *RANGE_ZONE_HEAT_LOSS, 0.01, "kW/°C"
                    ),
                    _numeric(CONF_LOWER_FLOOR_HEAT_LOSS): _number(
                        *RANGE_ZONE_HEAT_LOSS, 0.01, "kW/°C"
                    ),
                    _numeric(CONF_INTER_ZONE_TRANSFER): _number(
                        0.0, 3.0, 0.1, "kW/°C"
                    ),
                    _numeric(CONF_RADIATOR_POWER_FRACTION): _number(
                        0.0, 1.0, 0.05, slider=True
                    ),
                    _numeric(CONF_UPPER_FLOOR_AREA_RATIO): _number(
                        0.1, 0.9, 0.05, slider=True
                    ),
                    _numeric(CONF_SOLAR_ORIENTATION_FACTOR): _number(
                        0.0, 1.0, 0.05, slider=True
                    ),
                }
            ),
        )

    async def async_step_tuning(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Balance between saving money and holding the setpoint."""
        if user_input is not None:
            return self._save(user_input)

        current = self._current
        return self.async_show_form(
            step_id="tuning",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_PRICE_WEIGHT,
                        default=current.get(CONF_PRICE_WEIGHT, DEFAULT_PRICE_WEIGHT),
                    ): _number(0.1, 10, 0.1),
                    vol.Required(
                        CONF_COMFORT_WEIGHT,
                        default=current.get(
                            CONF_COMFORT_WEIGHT, DEFAULT_COMFORT_WEIGHT
                        ),
                    ): _number(0.1, 20, 0.1),
                    vol.Required(
                        CONF_OPTIMIZATION_INTERVAL,
                        default=current.get(
                            CONF_OPTIMIZATION_INTERVAL, DEFAULT_OPTIMIZATION_INTERVAL
                        ),
                    ): _number(10, 120, 5, "min", slider=True),
                    # An objective knob in SEK per start, so it lives with the
                    # other objective weights rather than under grid fees
                    # (moved here in v4.0.0; the key is unchanged).
                    vol.Optional(
                        CONF_CYCLING_COST,
                        default=current.get(CONF_CYCLING_COST, DEFAULT_CYCLING_COST),
                    ): _number(0, 10, 0.05),
                    # Risk premium on the prior-guessed part of the horizon
                    # (#34). Zero prices guessed steps at the prior's mean,
                    # exactly as before.
                    vol.Optional(
                        CONF_PRICE_RISK_LAMBDA,
                        default=current.get(
                            CONF_PRICE_RISK_LAMBDA, DEFAULT_PRICE_RISK_LAMBDA
                        ),
                    ): _number(0.0, 2.0, 0.05),
                    # T5 #16: an objective-shaping knob like the weights
                    # above — the floor rises by the model's own expected
                    # error, so a promise made 12 hours out carries the
                    # uncertainty a 12-hour promise has earned.
                    vol.Optional(
                        CONF_CONFIDENCE_MARGINS_ENABLED,
                        default=current.get(
                            CONF_CONFIDENCE_MARGINS_ENABLED,
                            DEFAULT_CONFIDENCE_MARGINS_ENABLED,
                        ),
                    ): bool,
                    # T6 #55: the wear pricing behind the start counter.
                    # Replacement cost 0 keeps the counter pure observation.
                    vol.Optional(
                        CONF_COMPRESSOR_REPLACEMENT_COST,
                        default=current.get(
                            CONF_COMPRESSOR_REPLACEMENT_COST,
                            DEFAULT_COMPRESSOR_REPLACEMENT_COST,
                        ),
                    ): _number(0, 100000, 100),
                    vol.Optional(
                        CONF_COMPRESSOR_RATED_STARTS,
                        default=current.get(
                            CONF_COMPRESSOR_RATED_STARTS,
                            DEFAULT_COMPRESSOR_RATED_STARTS,
                        ),
                    ): _number(1000, 1000000, 1000),
                    # The one T6 switch that changes plans: the realised
                    # wear price floors the cycling cost above.
                    vol.Optional(
                        CONF_WEAR_AUTOTUNE_ENABLED,
                        default=current.get(
                            CONF_WEAR_AUTOTUNE_ENABLED,
                            DEFAULT_WEAR_AUTOTUNE_ENABLED,
                        ),
                    ): bool,
                    # T6 #39: three extra rate-limited solves per cycle of
                    # the tile set — real CPU, so opt-in.
                    vol.Optional(
                        CONF_PRICE_TILES_ENABLED,
                        default=current.get(
                            CONF_PRICE_TILES_ENABLED,
                            DEFAULT_PRICE_TILES_ENABLED,
                        ),
                    ): bool,
                }
            ),
        )

    async def async_step_heat_curve(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Danfoss ECL110 heat-curve offset control over MQTT."""
        if user_input is not None:
            return self._save(user_input)

        current = self._current
        return self.async_show_form(
            step_id="heat_curve",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_ECL110_DISPLACE_SET_TOPIC,
                        default=current.get(
                            CONF_ECL110_DISPLACE_SET_TOPIC,
                            DEFAULT_ECL110_DISPLACE_SET_TOPIC,
                        ),
                    ): str,
                    vol.Optional(
                        CONF_ECL110_COMMAND_TOPIC,
                        default=current.get(
                            CONF_ECL110_COMMAND_TOPIC, DEFAULT_ECL110_COMMAND_TOPIC
                        ),
                    ): str,
                    vol.Optional(
                        CONF_ECL110_STATE_TOPIC,
                        default=current.get(
                            CONF_ECL110_STATE_TOPIC, DEFAULT_ECL110_STATE_TOPIC
                        ),
                    ): str,
                    vol.Optional(
                        CONF_ECL110_QOS,
                        default=current.get(CONF_ECL110_QOS, DEFAULT_ECL110_QOS),
                    ): _number(0, 2, 1, slider=True),
                    vol.Optional(
                        CONF_ECL110_RETAIN,
                        default=current.get(CONF_ECL110_RETAIN, DEFAULT_ECL110_RETAIN),
                    ): bool,
                    vol.Optional(
                        CONF_ECL110_DISPLACE_MIN,
                        default=current.get(
                            CONF_ECL110_DISPLACE_MIN, DEFAULT_ECL110_DISPLACE_MIN
                        ),
                    ): _number(-30, 0, 0.5, "°C"),
                    vol.Optional(
                        CONF_ECL110_DISPLACE_MAX,
                        default=current.get(
                            CONF_ECL110_DISPLACE_MAX, DEFAULT_ECL110_DISPLACE_MAX
                        ),
                    ): _number(0, 30, 0.5, "°C"),
                    vol.Optional(
                        CONF_ECL110_PID_TIME_CONSTANT,
                        default=current.get(
                            CONF_ECL110_PID_TIME_CONSTANT,
                            DEFAULT_ECL110_PID_TIME_CONSTANT,
                        ),
                    ): _number(0.25, 6.0, 0.25, "h"),
                }
            ),
        )

    # ------------------------------------------------------------------
    # Option pages added in v2.8.0
    # ------------------------------------------------------------------

    async def async_step_building_preset(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Describe the building in terms a homeowner can actually answer.

        The numeric thermal page asks for kWh/°C, which nobody knows. This page
        asks what the house is made of, roughly when it was built and what the
        heat comes out of, then derives the physics. Enabling it overwrites the
        numeric values on the *House and heating system* page, which stays
        available for anyone with a real energy declaration.
        """
        current = self._current
        if user_input is not None:
            saved = dict(user_input)
            if saved.get(CONF_BUILDING_PRESET_ENABLED):
                saved.update(_derive_preset(saved, current))
            return self._save(saved)

        return self.async_show_form(
            step_id="building_preset",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_BUILDING_PRESET_ENABLED,
                        default=current.get(
                            CONF_BUILDING_PRESET_ENABLED,
                            DEFAULT_BUILDING_PRESET_ENABLED,
                        ),
                    ): bool,
                    # The questionnaire itself is shared with the initial
                    # flow's building_describe step — one field list, so the
                    # two paths can never ask different questions.
                    **_questionnaire_fields(current),
                    # Structural properties of the building itself, beside
                    # the questions that describe it. None of these are
                    # derived by the preset, so a hand-set value survives
                    # enabling it.
                    vol.Optional(
                        CONF_WINDOW_AREA,
                        default=current.get(CONF_WINDOW_AREA, DEFAULT_WINDOW_AREA),
                    ): _number(0, 50, 0.5, "m²"),
                    vol.Optional(
                        CONF_SOLAR_HEAT_GAIN_COEFF,
                        default=current.get(
                            CONF_SOLAR_HEAT_GAIN_COEFF,
                            DEFAULT_SOLAR_HEAT_GAIN_COEFF,
                        ),
                    ): _number(0.1, 1.0, 0.05, slider=True),
                    vol.Optional(
                        CONF_WIND_SENSITIVITY,
                        default=current.get(
                            CONF_WIND_SENSITIVITY, DEFAULT_WIND_SENSITIVITY
                        ),
                    ): _number(0.0, 0.5, 0.01),
                    vol.Optional(
                        CONF_RAIN_HEAT_LOSS_MULTIPLIER,
                        default=current.get(
                            CONF_RAIN_HEAT_LOSS_MULTIPLIER,
                            DEFAULT_RAIN_HEAT_LOSS_MULTIPLIER,
                        ),
                    ): _number(1.0, 1.5, 0.01),
                }
            ),
        )

    async def async_step_grid(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """What the DSO charges: capacity tariff, transfer fees, contracts."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if not grid_fee.is_valid_spec(
                user_input.get(CONF_GRID_FEE_RULES, "")
            ):
                errors[CONF_GRID_FEE_RULES] = "invalid_grid_fee_rules"
            if not _valid_months_spec(
                user_input.get(CONF_PEAK_TARIFF_MONTHS, "")
            ):
                errors[CONF_PEAK_TARIFF_MONTHS] = "invalid_peak_months"
            if not is_valid_spec(user_input.get(CONF_PEAK_TARIFF_HOURS, "")):
                errors[CONF_PEAK_TARIFF_HOURS] = "invalid_peak_hours"
            if not errors:
                cleaned = dict(user_input)
                # The dropdown speaks strings; everything downstream treats
                # the window as a number of minutes. Convert once, here, so
                # the stored value has the type the rest of the integration
                # expects.
                window = cleaned.get(CONF_PEAK_TARIFF_WINDOW)
                if window is not None:
                    try:
                        cleaned[CONF_PEAK_TARIFF_WINDOW] = int(window)
                    except (TypeError, ValueError):
                        cleaned[CONF_PEAK_TARIFF_WINDOW] = (
                            DEFAULT_PEAK_TARIFF_WINDOW
                        )
                if not cleaned.get(CONF_GRID_FEE_ENTITY):
                    cleaned[CONF_GRID_FEE_ENTITY] = None
                return self._save(cleaned)

        current = self._current
        if user_input is not None:
            current = {**current, **user_input}
            # A cleared entity selector is simply absent from the submission,
            # so on the error re-render the merge above would resurrect the
            # stored value — and fixing the unrelated error would then
            # silently re-save the entity the user cleared.
            if not user_input.get(CONF_GRID_FEE_ENTITY):
                current.pop(CONF_GRID_FEE_ENTITY, None)

        def _entity(key: str) -> Any:
            existing = current.get(key)
            if existing:
                return vol.Optional(key, default=existing)
            return vol.Optional(key)

        return self.async_show_form(
            step_id="grid",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_PEAK_TARIFF_ENABLED,
                        default=current.get(
                            CONF_PEAK_TARIFF_ENABLED, DEFAULT_PEAK_TARIFF_ENABLED
                        ),
                    ): bool,
                    vol.Optional(
                        CONF_PEAK_TARIFF_PRICE,
                        default=current.get(
                            CONF_PEAK_TARIFF_PRICE, DEFAULT_PEAK_TARIFF_PRICE
                        ),
                    ): _number(0, 500, 1),
                    vol.Optional(
                        CONF_PEAK_TARIFF_COUNT,
                        default=current.get(
                            CONF_PEAK_TARIFF_COUNT, DEFAULT_PEAK_TARIFF_COUNT
                        ),
                    ): _number(1, 10, 1, slider=True),
                    vol.Optional(
                        CONF_PEAK_TARIFF_WINDOW,
                        # The selector's options are strings, so the default
                        # must be one too. An int default is returned verbatim
                        # when the field is left untouched, and SelectSelector
                        # rejects it with "expected str" — which made the
                        # already-selected option the one that could not be
                        # submitted.
                        default=str(
                            current.get(
                                CONF_PEAK_TARIFF_WINDOW, DEFAULT_PEAK_TARIFF_WINDOW
                            )
                        ),
                    ): _select(["15", "60"], "peak_window"),
                    # The #13 masks: which hours a peak actually bills in.
                    # Empty means every hour at full rate — the flat model.
                    vol.Optional(
                        CONF_PEAK_TARIFF_MONTHS,
                        default=current.get(
                            CONF_PEAK_TARIFF_MONTHS, DEFAULT_PEAK_TARIFF_MONTHS
                        ),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        )
                    ),
                    vol.Optional(
                        CONF_PEAK_TARIFF_HOURS,
                        default=current.get(
                            CONF_PEAK_TARIFF_HOURS, DEFAULT_PEAK_TARIFF_HOURS
                        ),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        )
                    ),
                    vol.Optional(
                        CONF_PEAK_TARIFF_WEEKDAYS_ONLY,
                        default=current.get(
                            CONF_PEAK_TARIFF_WEEKDAYS_ONLY,
                            DEFAULT_PEAK_TARIFF_WEEKDAYS_ONLY,
                        ),
                    ): bool,
                    vol.Optional(
                        CONF_PEAK_TARIFF_OFFPEAK_FACTOR,
                        default=current.get(
                            CONF_PEAK_TARIFF_OFFPEAK_FACTOR,
                            DEFAULT_PEAK_TARIFF_OFFPEAK_FACTOR,
                        ),
                    ): _number(0.0, 1.0, 0.05, slider=True),
                    # The main fuse and its guards (T2). 0 A means
                    # unconfigured: advisor, guard and headroom all dormant.
                    vol.Optional(
                        CONF_MAIN_FUSE_A,
                        default=current.get(
                            CONF_MAIN_FUSE_A, DEFAULT_MAIN_FUSE_A
                        ),
                    ): _number(0, 125, 1, "A"),
                    vol.Optional(
                        CONF_MAIN_FUSE_PHASES,
                        default=current.get(
                            CONF_MAIN_FUSE_PHASES, DEFAULT_MAIN_FUSE_PHASES
                        ),
                    ): _number(1, 3, 1, slider=True),
                    vol.Optional(
                        CONF_FUSE_GUARD_ENABLED,
                        default=current.get(
                            CONF_FUSE_GUARD_ENABLED, DEFAULT_FUSE_GUARD_ENABLED
                        ),
                    ): bool,
                    vol.Optional(
                        CONF_PEAK_GUARD_ENABLED,
                        default=current.get(
                            CONF_PEAK_GUARD_ENABLED, DEFAULT_PEAK_GUARD_ENABLED
                        ),
                    ): bool,
                    vol.Optional(
                        CONF_PEAK_GUARD_MARGIN_KW,
                        default=current.get(
                            CONF_PEAK_GUARD_MARGIN_KW,
                            DEFAULT_PEAK_GUARD_MARGIN_KW,
                        ),
                    ): _number(0.0, 3.0, 0.1, "kW", slider=True),
                    # The ToU fee layer (#1).
                    vol.Optional(
                        CONF_GRID_FEE_MODE,
                        default=current.get(
                            CONF_GRID_FEE_MODE, DEFAULT_GRID_FEE_MODE
                        ),
                    ): _select(list(grid_fee.MODES), "grid_fee_mode"),
                    vol.Optional(
                        CONF_GRID_FEE_FIXED,
                        default=current.get(
                            CONF_GRID_FEE_FIXED, DEFAULT_GRID_FEE_FIXED
                        ),
                    ): _number(0, 5, 0.01),
                    vol.Optional(
                        CONF_GRID_FEE_RULES,
                        default=current.get(
                            CONF_GRID_FEE_RULES, DEFAULT_GRID_FEE_RULES
                        ),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                            multiline=True,
                        )
                    ),
                    _entity(CONF_GRID_FEE_ENTITY): _entity_of("sensor"),
                    # The contract shadow settlement's fixed column (#23).
                    vol.Optional(
                        CONF_CONTRACT_FIXED_PRICE,
                        default=current.get(
                            CONF_CONTRACT_FIXED_PRICE,
                            DEFAULT_CONTRACT_FIXED_PRICE,
                        ),
                    ): _number(0, 10, 0.01),
                }
            ),
        )

    async def async_step_solar_pv(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Photovoltaic array and export economics."""
        if user_input is not None:
            cleaned = dict(user_input)
            for key in (CONF_PV_PRODUCTION_ENTITY, CONF_PV_EXPORT_PRICE_ENTITY):
                if not cleaned.get(key):
                    cleaned[key] = None
            return self._save(cleaned)

        current = self._current

        def _entity(key: str) -> Any:
            existing = current.get(key)
            if existing:
                return vol.Optional(key, default=existing)
            return vol.Optional(key)

        return self.async_show_form(
            step_id="solar_pv",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_PV_ENABLED,
                        default=current.get(CONF_PV_ENABLED, DEFAULT_PV_ENABLED),
                    ): bool,
                    vol.Optional(
                        CONF_PV_PEAK_KW,
                        default=current.get(CONF_PV_PEAK_KW, DEFAULT_PV_PEAK_KW),
                    ): _number(0, 100, 0.1, "kWp"),
                    vol.Optional(
                        CONF_PV_EFFICIENCY,
                        default=current.get(
                            CONF_PV_EFFICIENCY, DEFAULT_PV_EFFICIENCY
                        ),
                    ): _number(0.3, 1.0, 0.01, slider=True),
                    vol.Optional(
                        CONF_PV_EXPORT_PRICE,
                        default=current.get(
                            CONF_PV_EXPORT_PRICE, DEFAULT_PV_EXPORT_PRICE
                        ),
                    ): _number(0, 10, 0.01),
                    _entity(CONF_PV_EXPORT_PRICE_ENTITY): _entity_of("sensor"),
                    _entity(CONF_PV_PRODUCTION_ENTITY): _entity_of("sensor", "power"),
                }
            ),
        )

    async def async_step_away(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Deep setback while the house is empty, with timed recovery."""
        if user_input is not None:
            cleaned = dict(user_input)
            for key in (CONF_AWAY_PRESENCE_ENTITY, CONF_AWAY_RETURN_ENTITY):
                if not cleaned.get(key):
                    cleaned[key] = None
            return self._save(cleaned)

        current = self._current

        def _entity(key: str) -> Any:
            existing = current.get(key)
            if existing:
                return vol.Optional(key, default=existing)
            return vol.Optional(key)

        return self.async_show_form(
            step_id="away",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_AWAY_ENABLED,
                        default=current.get(CONF_AWAY_ENABLED, DEFAULT_AWAY_ENABLED),
                    ): bool,
                    _entity(CONF_AWAY_PRESENCE_ENTITY): _entity_of([ "input_boolean", "person", "device_tracker", "calendar", "binary_sensor", ]),
                    _entity(CONF_AWAY_RETURN_ENTITY): _entity_of(["input_datetime", "sensor"]),
                    vol.Optional(
                        CONF_AWAY_TEMPERATURE,
                        default=current.get(
                            CONF_AWAY_TEMPERATURE, DEFAULT_AWAY_TEMPERATURE
                        ),
                    ): _number(5, 21, 0.5, "°C", slider=True),
                    vol.Optional(
                        CONF_AWAY_DHW_MIN_TEMP,
                        default=current.get(
                            CONF_AWAY_DHW_MIN_TEMP, DEFAULT_AWAY_DHW_MIN_TEMP
                        ),
                    ): _number(10, 55, 1, "°C", slider=True),
                }
            ),
        )

    async def async_step_learning(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Watchdogs and the opt-in learning features."""
        if user_input is not None:
            cleaned = dict(user_input)
            for key in (CONF_EXTERNAL_HEAT_ENTITY,):
                if not cleaned.get(key):
                    cleaned[key] = None
            return self._save(cleaned)

        current = self._current

        def _entity(key: str) -> Any:
            existing = current.get(key)
            if existing:
                return vol.Optional(key, default=existing)
            return vol.Optional(key)

        return self.async_show_form(
            step_id="learning",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_STALENESS_ENABLED,
                        default=current.get(
                            CONF_STALENESS_ENABLED, DEFAULT_STALENESS_ENABLED
                        ),
                    ): bool,
                    vol.Optional(
                        CONF_STALENESS_SCALE,
                        default=current.get(
                            CONF_STALENESS_SCALE, DEFAULT_STALENESS_SCALE
                        ),
                    ): _number(STALENESS_SCALE_MIN, STALENESS_SCALE_MAX, 0.5, slider=True),
                    vol.Optional(
                        CONF_EXTERNAL_HEAT_ENABLED,
                        default=current.get(
                            CONF_EXTERNAL_HEAT_ENABLED,
                            DEFAULT_EXTERNAL_HEAT_ENABLED,
                        ),
                    ): bool,
                    _entity(CONF_EXTERNAL_HEAT_ENTITY): _entity_of(["binary_sensor", "switch", "input_boolean", "sensor"]),
                    vol.Optional(
                        CONF_EXTERNAL_HEAT_MIN_RISE,
                        default=current.get(
                            CONF_EXTERNAL_HEAT_MIN_RISE,
                            DEFAULT_EXTERNAL_HEAT_MIN_RISE,
                        ),
                    ): _number(0.5, 10, 0.1, "°C/h"),
                    vol.Optional(
                        CONF_EXTERNAL_HEAT_DECAY_MINUTES,
                        default=current.get(
                            CONF_EXTERNAL_HEAT_DECAY_MINUTES,
                            DEFAULT_EXTERNAL_HEAT_DECAY_MINUTES,
                        ),
                    ): _number(15, 360, 15, "min", slider=True),
                    vol.Optional(
                        CONF_COMFORT_LEARNING_ENABLED,
                        default=current.get(
                            CONF_COMFORT_LEARNING_ENABLED,
                            DEFAULT_COMFORT_LEARNING_ENABLED,
                        ),
                    ): bool,
                    vol.Optional(
                        CONF_SYSID_ENABLED,
                        default=current.get(
                            CONF_SYSID_ENABLED, DEFAULT_SYSID_ENABLED
                        ),
                    ): bool,
                    # A learned model toggle, so it belongs with the other
                    # learners rather than under grid fees (moved here in
                    # v4.0.0; the key is unchanged).
                    vol.Optional(
                        CONF_PRICE_PRIOR_ENABLED,
                        default=current.get(
                            CONF_PRICE_PRIOR_ENABLED, DEFAULT_PRICE_PRIOR_ENABLED
                        ),
                    ): bool,
                    # Post-outage staggered recovery (#22, T2): a diagnostic
                    # behaviour, so it lives with the other watchdogs.
                    vol.Optional(
                        CONF_OUTAGE_RECOVERY_ENABLED,
                        default=current.get(
                            CONF_OUTAGE_RECOVERY_ENABLED,
                            DEFAULT_OUTAGE_RECOVERY_ENABLED,
                        ),
                    ): bool,
                    # T4a: only the plan-affecting halves are gated — the
                    # detectors themselves ship on, because a freeze only
                    # stops learning and never moves a plan.
                    vol.Optional(
                        CONF_OPEN_WINDOW_RELAX_ENABLED,
                        default=current.get(
                            CONF_OPEN_WINDOW_RELAX_ENABLED,
                            DEFAULT_OPEN_WINDOW_RELAX_ENABLED,
                        ),
                    ): bool,
                    vol.Optional(
                        CONF_IMMERSION_FEEDBACK_ENABLED,
                        default=current.get(
                            CONF_IMMERSION_FEEDBACK_ENABLED,
                            DEFAULT_IMMERSION_FEEDBACK_ENABLED,
                        ),
                    ): bool,
                    # T4b: every one of these moves real physics or real
                    # heat, so learning AND application sit behind the
                    # same flag — a half-armed learner that suddenly
                    # applies weeks of unreviewed evidence is worse than
                    # an off one.
                    vol.Optional(
                        CONF_PRECIP_TYPE_ENABLED,
                        default=current.get(
                            CONF_PRECIP_TYPE_ENABLED,
                            DEFAULT_PRECIP_TYPE_ENABLED,
                        ),
                    ): bool,
                    vol.Optional(
                        CONF_SNOW_ROOF_FACTOR_ENABLED,
                        default=current.get(
                            CONF_SNOW_ROOF_FACTOR_ENABLED,
                            DEFAULT_SNOW_ROOF_FACTOR_ENABLED,
                        ),
                    ): bool,
                    vol.Optional(
                        CONF_CAPACITY_CURVE_ENABLED,
                        default=current.get(
                            CONF_CAPACITY_CURVE_ENABLED,
                            DEFAULT_CAPACITY_CURVE_ENABLED,
                        ),
                    ): bool,
                    vol.Optional(
                        CONF_SOLAR_APERTURE_LEARNING_ENABLED,
                        default=current.get(
                            CONF_SOLAR_APERTURE_LEARNING_ENABLED,
                            DEFAULT_SOLAR_APERTURE_LEARNING_ENABLED,
                        ),
                    ): bool,
                    vol.Optional(
                        CONF_INTERNAL_GAINS_LEARNING_ENABLED,
                        default=current.get(
                            CONF_INTERNAL_GAINS_LEARNING_ENABLED,
                            DEFAULT_INTERNAL_GAINS_LEARNING_ENABLED,
                        ),
                    ): bool,
                    vol.Optional(
                        CONF_CURVE_LEARNING_ENABLED,
                        default=current.get(
                            CONF_CURVE_LEARNING_ENABLED,
                            DEFAULT_CURVE_LEARNING_ENABLED,
                        ),
                    ): bool,
                }
            ),
        )
