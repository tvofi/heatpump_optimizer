# Review packet #2915
head: 196a75a9f32d87445f48a266ea37a961bfa1089a
base: 6493ea3625900f8361011e0c8f2a3c66885ce7b1

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=123186560483 neutral
arch-score / arch-score id=123185550239 success
arm id=123184809280 skipped
budget-raise-gate / budget-raise-gate id=123185550303 success
cancel-superseded id=123188189881 success
codeql / Analyze (actions) id=123185550288 success
codeql / Analyze (javascript-typescript) id=123185550407 success
codeql / Analyze (python) id=123185550354 in_progress
governance / delivery-status id=123185550095 failure
governance / delivery-status-publish id=123185552223 skipped
governance / env-matrix id=123185550022 success
governance / instrument-self-tests id=123185550027 in_progress
governance / policy-docs id=123185550171 success
governance / record id=123185552751 skipped
governance / wave-script id=123185550172 success
hassfest / hassfest id=123185550146 success
kernel-points id=123185552355 skipped
prelude id=123188190330 in_progress
refresh id=123188189569 success
tests / arch-instrument id=123186485284 success
tests / briefs id=123185550091 success
tests / browser id=123186485206 success
tests / claims-autofix id=123191367123 skipped
tests / closure-scope id=123185550360 success
tests / closures id=123186485214 in_progress
tests / coverage id=123186485096 in_progress
tests / fast (3.14) id=123186485126 success
tests / mutation id=123185550149 success
tests / mutation-autofix id=123186270993 skipped
tests / mutation-pins id=123186270979 skipped
tests / nightly-ha id=123186486798 skipped
tests / nightly-status id=123185550152 success
tests / replay id=123186486564 skipped
tests / typing id=123186485172 success
validate / validate-hacs id=123185549970 success

## Refusals
red-unanswered: concluded red check `governance / delivery-status` is not named in ## Red checks

## Advisories
none

## carry_audit at the head
NOTE stale tree: 6493ea3625900f8361011e0c8f2a3c66885ce7b1 lacks origin/main 077dee8567ebebc4bac7481c54276348d5bceab3; roster read at origin/main
NOTE body item c3498e8d: R10-CONFIGFLOW-PAGES
NOTE body item 4bc1c15e: R10-CONFIGFLOW-PAGES
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git archive
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round10/D7/arch2-s5/wizard_widgets.py [--all | --bump heat_pump_cop_nominal]
             the path `$EXPORT/dev/audit/rounds/round10/D7/arch2-s5/wizard_widgets.py` is a template or an expansion, not a literal
  ok         python3 tests/closure.py select --diff b0b2d7697 --workdir $D
             `tests/closure.py` is in the tree at this head
  ok         tests/config_flow_steps.py
             `tests/config_flow_steps.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff b0b2d7697
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py --base origin/main
             `tools/pr/ci_predict.py` is in the tree at this head
  unverified git diff --stat b0b2d7697...HEAD
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git diff --name-only b0b2d7697...HEAD -- <those five> | wc -l
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 5 resolved, 4 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/config_flow.py b/custom_components/heatpump_optimizer/config_flow.py
index bc51e5feb..384a2b4a3 100644
--- a/custom_components/heatpump_optimizer/config_flow.py
+++ b/custom_components/heatpump_optimizer/config_flow.py
@@ -1023,13 +1023,6 @@ def _valid_months_spec(spec: Any) -> bool:
     return True
 
 
-def _tibber_token_selector() -> selector.TextSelector:
-    """The masked token widget shared by setup, reauth and options."""
-    return selector.TextSelector(
-        selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
-    )
-
-
 def _entity_of(
     domain: str | list[str], device_class: str | None = None
 ) -> selector.EntitySelector:
@@ -1225,10 +1218,10 @@ def _quick_setup_schema(
     return vol.Schema(
         {
             **question_fields,
-            _suggested_entity(CONF_WOOD_TANK_TOP_ENTITY, current): _entity_of(["sensor"]),
+            _suggested_entity(CONF_WOOD_TANK_TOP_ENTITY, current): _prefill_row(CONF_WOOD_TANK_TOP_ENTITY).widget,
             _suggested_entity(
                 CONF_WOOD_TANK_BOTTOM_ENTITY, current
-            ): _entity_of(["sensor"]),
+            ): _prefill_row(CONF_WOOD_TANK_BOTTOM_ENTITY).widget,
             **_questionnaire_fields(current),
         }
     )
@@ -1268,10 +1261,10 @@ def _user_credentials_fields() -> dict[Any, Any]:
         vol.Required(CONF_NAME, default="Heat Pump Optimizer"): str,
         vol.Optional(
             CONF_PRICE_SOURCE, default=DEFAULT_PRICE_SOURCE
-        ): _select(list(PRICE_SOURCES), "price_source"),
-        vol.Optional(CONF_TIBBER_TOKEN, default=""): _tibber_token_selector(),
-        vol.Optional(CONF_PRICE_ENTITY): _entity_of("sensor"),
-        vol.Required(CONF_WEATHER_ENTITY): _entity_of("weather"),
+        ): _prefill_row(CONF_PRICE_SOURCE).widget,
+        vol.Optional(CONF_TIBBER_TOKEN, default=""): _prefill_row(CONF_TIBBER_TOKEN).widget,
+        vol.Optional(CONF_PRICE_ENTITY): _prefill_row(CONF_PRICE_ENTITY).widget,
+        vol.Required(CONF_WEATHER_ENTITY): _prefill_row(CONF_WEATHER_ENTITY).widget,
     }
 
 
@@ -1308,36 +1301,28 @@ def _user_sensors_fields(hass: HomeAssistant) -> dict[Any, Any]:
     ``_user_sensors_sections`` is what the setup page renders (#824).
     """
     return {
-        vol.Optional(CONF_INDOOR_TEMP_ENTITY): _entity_of("sensor", "temperature"),
-        vol.Optional(CONF_OUTDOOR_TEMP_ENTITY): _entity_of("sensor", "temperature"),
-        vol.Optional(CONF_HEAT_PUMP_SWITCH_ENTITY): _entity_of("switch"),
-        vol.Optional(CONF_SOLAR_RADIATION_ENTITY): _entity_of("sensor"),
+        vol.Optional(CONF_INDOOR_TEMP_ENTITY): _prefill_row(CONF_INDOOR_TEMP_ENTITY).widget,
+        vol.Optional(CONF_OUTDOOR_TEMP_ENTITY): _prefill_row(CONF_OUTDOOR_TEMP_ENTITY).widget,
+        vol.Optional(CONF_HEAT_PUMP_SWITCH_ENTITY): _prefill_row(CONF_HEAT_PUMP_SWITCH_ENTITY).widget,
+        vol.Optional(CONF_SOLAR_RADIATION_ENTITY): _prefill_row(CONF_SOLAR_RADIATION_ENTITY).widget,
         vol.Optional(
             CONF_SOLAR_FORECAST_SOURCE,
             default=DEFAULT_SOLAR_FORECAST_SOURCE,
-        ): _solar_source_selector(),
+        ): _prefill_row(CONF_SOLAR_FORECAST_SOURCE).widget,
         vol.Optional(
             CONF_SOLAR_LOCATION,
             default=_default_location(hass, {}),
-        ): _solar_location_selector(),
-        vol.Optional(CONF_FLOOR_RETURN_TEMP_ENTITY): _entity_of("sensor", "temperature"),
-        vol.Optional(CONF_LOWER_FLOOR_TEMP_ENTITY): _entity_of("sensor", "temperature"),
-        vol.Optional(CONF_DHW_TEMP_ENTITY): _entity_of("sensor", "temperature"),
+        ): _prefill_row(CONF_SOLAR_LOCATION).widget,
+        vol.Optional(CONF_FLOOR_RETURN_TEMP_ENTITY): _prefill_row(CONF_FLOOR_RETURN_TEMP_ENTITY).widget,
+        vol.Optional(CONF_LOWER_FLOOR_TEMP_ENTITY): _prefill_row(CONF_LOWER_FLOOR_TEMP_ENTITY).widget,
+        vol.Optional(CONF_DHW_TEMP_ENTITY): _prefill_row(CONF_DHW_TEMP_ENTITY).widget,
         vol.Optional(
             CONF_BUFFER_TANK_TEMP_ENTITY
-        ): _entity_of("sensor", "temperature"),
-        vol.Optional(CONF_HEAT_PUMP_MODE_ENTITY): _entity_of(
-            list(topology.ASSIGNABLE_KEYS[CONF_HEAT_PUMP_MODE_ENTITY])
-        ),
-        vol.Optional(CONF_HEAT_PUMP_DEFROST_ENTITY): _entity_of(
-            list(topology.ASSIGNABLE_KEYS[CONF_HEAT_PUMP_DEFROST_ENTITY])
-        ),
-        vol.Optional(CONF_HEAT_PUMP_ONLINE_ENTITY): _entity_of(
-            list(topology.ASSIGNABLE_KEYS[CONF_HEAT_PUMP_ONLINE_ENTITY])
-        ),
-        vol.Optional(CONF_HEAT_PUMP_FAULT_ENTITY): _entity_of(
-            list(topology.ASSIGNABLE_KEYS[CONF_HEAT_PUMP_FAULT_ENTITY])
-        ),
+        ): _prefill_row(CONF_BUFFER_TANK_TEMP_ENTITY).widget,
+        vol.Optional(CONF_HEAT_PUMP_MODE_ENTITY): _prefill_row(CONF_HEAT_PUMP_MODE_ENTITY).widget,
+        vol.Optional(CONF_HEAT_PUMP_DEFROST_ENTITY): _prefill_row(CONF_HEAT_PUMP_DEFROST_ENTITY).widget,
+        vol.Optional(CONF_HEAT_PUMP_ONLINE_ENTITY): _prefill_row(CONF_HEAT_PUMP_ONLINE_ENTITY).widget,
+        vol.Optional(CONF_HEAT_PUMP_FAULT_ENTITY): _prefill_row(CONF_HEAT_PUMP_FAULT_ENTITY).widget,
     }
 
 
@@ -1560,7 +1545,7 @@ _OPTION_PAGES: Final[tuple[_P, ...]] = (
 _OPTION_FIELDS: Final[tuple[_F, ...]] = (
     # -- entities
     _F("entities", CONF_PRICE_SOURCE, DEFAULT_PRICE_SOURCE, _select(list(PRICE_SOURCES), "price_source"), group="credentials"),
-    _F("entities", CONF_TIBBER_TOKEN, '', _tibber_token_selector(), required=False, group="credentials"),
+    _F("entities", CONF_TIBBER_TOKEN, '', selector.TextSelector(selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)), required=False, group="credentials"),
     _F("entities", CONF_PRICE_ENTITY, _STORED, _entity_of('sensor'), group="credentials"),
     _F("entities", CONF_PRICE_VAT, DEFAULT_PRICE_VAT, _number(0.0, 2.0, 0.01), group="credentials"),
     _F("entities", CONF_PRICE_SURCHARGE, DEFAULT_PRICE_SURCHARGE, _number(0.0, 2.0, 0.01), group="credentials"),
@@ -1937,6 +1922,33 @@ def _prefill_row(key: str) -> _F:
     return next(row for row in _OPTION_FIELDS if row.key == key)
 
 
+def _wizard_fields(
+    marker: Callable[..., Any], defaults: Mapping[str, Any]
+) -> dict[Any, Any]:
+    """Setup-wizard fields, each rendered by its options-registry widget.
+
+    A setting's selector -- bounds, step, unit, slider -- is declared once, on
+    its ``_OPTION_FIELDS`` row. The wizard asks the same question earlier and
+    with its own default and marker, so it takes the widget from that row
+    rather than spelling a second one: the two flows cannot then offer a
+    different range for one setting, which is the disagreement
+    ``_StoredValuesAlwaysFit`` would otherwise be left to paper over.
+    """
+    return {
+        marker(key, default=default): _prefill_row(key).widget
+        for key, default in defaults.items()
+    }
+
+
+#: The heat pump's nameplate, asked on both wizard paths (``building_extras``
+#: after the questionnaire, ``thermal`` on the expert path).
+_NAMEPLATE_DEFAULTS: Final = {
+    CONF_HEAT_PUMP_COP_NOMINAL: DEFAULT_HEAT_PUMP_COP_NOMINAL,
+    CONF_HEAT_PUMP_MAX_POWER: DEFAULT_HEAT_PUMP_MAX_POWER,
+    CONF_HEAT_PUMP_MIN_POWER: DEFAULT_HEAT_PUMP_MIN_POWER,
+}
+
+
 def _prefill_fits(key: str, value: Any) -> bool:
     """A suggestion its own field would accept: a number inside its range.
 
@@ -2648,37 +2660,18 @@ class HeatPumpOptimizerConfigFlow(
             step_id="temperature",
             errors=errors,
             data_schema=vol.Schema(
-                {
-                    vol.Required(
-                        CONF_TARGET_TEMP, default=DEFAULT_TARGET_TEMP
-                    ): _number(15, 28, 0.5, "°C", slider=True),
-                    vol.Required(
-                        CONF_MIN_TEMP, default=DEFAULT_MIN_TEMP
-                    ): _number(14, 25, 0.5, "°C", slider=True),
-                    vol.Required(
-                        CONF_MAX_TEMP, default=DEFAULT_MAX_TEMP
-                    ): _number(18, 28, 0.5, "°C", slider=True),
-                    vol.Required(
-                        CONF_COMFORT_TEMP_DAY, default=DEFAULT_COMFORT_TEMP_DAY
-                    ): _number(
-                        COMFORT_TEMP_DAY_SELECTOR_MIN,
-                        COMFORT_TEMP_DAY_SELECTOR_MAX,
-                        0.5, "°C", slider=True,
-                    ),
-                    vol.Required(
-                        CONF_COMFORT_TEMP_NIGHT, default=DEFAULT_COMFORT_TEMP_NIGHT
-                    ): _number(
-                        COMFORT_TEMP_NIGHT_SELECTOR_MIN,
-                        COMFORT_TEMP_NIGHT_SELECTOR_MAX,
-                        0.5, "°C", slider=True,
-                    ),
-                    vol.Required(
-                        CONF_DAY_START_HOUR, default=DEFAULT_DAY_START_HOUR
-                    ): _number(0, 23, 1, slider=True),
-                    vol.Required(
-                        CONF_DAY_END_HOUR, default=DEFAULT_DAY_END_HOUR
-                    ): _number(1, 24, 1, slider=True),
-                }
+                _wizard_fields(
+                    vol.Required,
+                    {
+                        CONF_TARGET_TEMP: DEFAULT_TARGET_TEMP,
+                        CONF_MIN_TEMP: DEFAULT_MIN_TEMP,
+                        CONF_MAX_TEMP: DEFAULT_MAX_TEMP,
+                        CONF_COMFORT_TEMP_DAY: DEFAULT_COMFORT_TEMP_DAY,
+                        CONF_COMFORT_TEMP_NIGHT: DEFAULT_COMFORT_TEMP_NIGHT,
+                        CONF_DAY_START_HOUR: DEFAULT_DAY_START_HOUR,
+                        CONF_DAY_END_HOUR: DEFAULT_DAY_END_HOUR,
+                    },
+                )
             ),
         )
 
@@ -2749,20 +2742,7 @@ class HeatPumpOptimizerConfigFlow(
         return self.async_show_form(
             step_id="building_extras",
             errors=errors,
-            data_schema=vol.Schema(
-                {
-                    vol.Required(
-                        CONF_HEAT_PUMP_COP_NOMINAL,
-                        default=DEFAULT_HEAT_PUMP_COP_NOMINAL,
-                    ): _number(1.5, 6.0, 0.1),
-                    vol.Required(
-                        CONF_HEAT_PUMP_MAX_POWER, default=DEFAULT_HEAT_PUMP_MAX_POWER
-                    ): _number(1, 20, 0.5, "kW"),
-                    vol.Required(
-                        CONF_HEAT_PUMP_MIN_POWER, default=DEFAULT_HEAT_PUMP_MIN_POWER
-                    ): _number(0, 10, 0.5, "kW"),
-                }
-            ),
+            data_schema=vol.Schema(_wizard_fields(vol.Required, _NAMEPLATE_DEFAULTS)),
         )
 
     async def async_step_thermal(
@@ -2780,41 +2760,19 @@ class HeatPumpOptimizerConfigFlow(
             step_id="thermal",
             errors=errors,
             data_schema=vol.Schema(
-                {
-                    vol.Required(
-                        CONF_HOUSE_THERMAL_MASS, default=DEFAULT_HOUSE_THERMAL_MASS
-                    ): _number(*RANGE_HOUSE_THERMAL_MASS, 0.5, "kWh/°C"),
-                    vol.Required(
-                        CONF_HOUSE_HEAT_LOSS_COEFFICIENT,
-                        default=DEFAULT_HOUSE_HEAT_LOSS_COEFFICIENT,
-                    ): _number(*RANGE_HOUSE_HEAT_LOSS, 0.01, "kW/°C"),
-                    vol.Required(
-                        CONF_SLAB_THERMAL_MASS, default=DEFAULT_SLAB_THERMAL_MASS
-                    ): _number(*RANGE_SLAB_THERMAL_MASS, 0.5, "kWh/°C"),
-                    vol.Required(
-                        CONF_SLAB_HEAT_TRANSFER, default=DEFAULT_SLAB_HEAT_TRANSFER
-                    ): _number(*RANGE_SLAB_HEAT_TRANSFER, 0.1, "kW/°C"),
-                    vol.Required(
-                        CONF_HEAT_PUMP_COP_NOMINAL,
-                        default=DEFAULT_HEAT_PUMP_COP_NOMINAL,
-                    ): _number(1.5, 6.0, 0.1),
-                    vol.Required(
-                        CONF_HEAT_PUMP_MAX_POWER, default=DEFAULT_HEAT_PUMP_MAX_POWER
-                    ): _number(1, 20, 0.5, "kW"),
-                    vol.Required(
-                        CONF_HEAT_PUMP_MIN_POWER, default=DEFAULT_HEAT_PUMP_MIN_POWER
-                    ): _number(0, 10, 0.5, "kW"),
-                    vol.Required(
-                        CONF_OPTIMIZATION_INTERVAL,
-                        default=DEFAULT_OPTIMIZATION_INTERVAL,
-                    ): _number(10, 120, 5, "min", slider=True),
-                    vol.Required(
-                        CONF_PRICE_WEIGHT, default=DEFAULT_PRICE_WEIGHT
-                    ): _number(0.1, 10, 0.1),
-                    vol.Required(
-                        CONF_COMFORT_WEIGHT, default=DEFAULT_COMFORT_WEIGHT
-                    ): _number(0.1, 20, 0.1),
-                }
+                _wizard_fields(
+                    vol.Required,
+                    {
+                        CONF_HOUSE_THERMAL_MASS: DEFAULT_HOUSE_THERMAL_MASS,
+                        CONF_HOUSE_HEAT_LOSS_COEFFICIENT: DEFAULT_HOUSE_HEAT_LOSS_COEFFICIENT,
+                        CONF_SLAB_THERMAL_MASS: DEFAULT_SLAB_THERMAL_MASS,
+                        CONF_SLAB_HEAT_TRANSFER: DEFAULT_SLAB_HEAT_TRANSFER,
+                        **_NAMEPLATE_DEFAULTS,
+                        CONF_OPTIMIZATION_INTERVAL: DEFAULT_OPTIMIZATION_INTERVAL,
+                        CONF_PRICE_WEIGHT: DEFAULT_PRICE_WEIGHT,
+                        CONF_COMFORT_WEIGHT: DEFAULT_COMFORT_WEIGHT,
+                    },
+                )
             ),
         )
 
@@ -2855,49 +2813,22 @@ class HeatPumpOptimizerConfigFlow(
                             "suggested_value": mode == TWO_ZONE_MODE_ON
                         },
                     ): selector.BooleanSelector(),
-                    vol.Optional(
-                        CONF_UPPER_FLOOR_THERMAL_MASS,
-                        default=DEFAULT_UPPER_FLOOR_THERMAL_MASS,
-                    ): _number(*RANGE_ZONE_THERMAL_MASS, 0.5, "kWh/°C"),
-                    vol.Optional(
-                        CONF_LOWER_FLOOR_THERMAL_MASS,
-                        default=DEFAULT_LOWER_FLOOR_THERMAL_MASS,
-                    ): _number(*RANGE_ZONE_THERMAL_MASS, 0.5, "kWh/°C"),
-                    vol.Optional(
-                        CONF_UPPER_FLOOR_HEAT_LOSS,
-                        default=DEFAULT_UPPER_FLOOR_HEAT_LOSS,
-                    ): _number(*RANGE_ZONE_HEAT_LOSS, 0.01, "kW/°C"),
-                    vol.Optional(
-                        CONF_LOWER_FLOOR_HEAT_LOSS,
-                        default=DEFAULT_LOWER_FLOOR_HEAT_LOSS,
-                    ): _number(*RANGE_ZONE_HEAT_LOSS, 0.01, "kW/°C"),
-                    vol.Optional(
-                        CONF_INTER_ZONE_TRANSFER,
-                        default=DEFAULT_INTER_ZONE_TRANSFER,
-                    ): _number(POSITIVE_PARAM_FLOOR, 3.0, 0.1, "kW/°C"),
-                    vol.Optional(
-                        CONF_RADIATOR_POWER_FRACTION,
-                        default=DEFAULT_RADIATOR_POWER_FRACTION,
-                    ): _number(0.0, 1.0, 0.05, slider=True),
-                    vol.Optional(
-                        CONF_UPPER_FLOOR_AREA_RATIO,
-                        default=DEFAULT_UPPER_FLOOR_AREA_RATIO,
-                    ): _number(0.1, 0.9, 0.05, slider=True),
-                    vol.Optional(
-                        CONF_BUFFER_TANK_VOLUME,
-                        default=DEFAULT_BUFFER_TANK_VOLUME,
-                    ): _number(10, 1500, 5, "L"),
-                    vol.Optional(
-                        CONF_WINDOW_AREA, default=DEFAULT_WINDOW_AREA
-                    ): _number(POSITIVE_PARAM_FLOOR, 50, 0.5, "m²"),
-                    vol.Optional(
-                        CONF_SOLAR_ORIENTATION_FACTOR,
-                        default=DEFAULT_SOLAR_ORIENTATION_FACTOR,
-                    ): _number(0.0, 1.0, 0.05, slider=True),
-                    vol.Optional(
-                        CONF_SOLAR_HEAT_GAIN_COEFF,
-                        default=DEFAULT_SOLAR_HEAT_GAIN_COEFF,
-                    ): _number(0.1, 1.0, 0.05, slider=True),
+                    **_wizard_fields(
+                        vol.Optional,
+                        {
+                            CONF_UPPER_FLOOR_THERMAL_MASS: DEFAULT_UPPER_FLOOR_THERMAL_MASS,
+                            CONF_LOWER_FLOOR_THERMAL_MASS: DEFAULT_LOWER_FLOOR_THERMAL_MASS,
+                            CONF_UPPER_FLOOR_HEAT_LOSS: DEFAULT_UPPER_FLOOR_HEAT_LOSS,
+                            CONF_LOWER_FLOOR_HEAT_LOSS: DEFAULT_LOWER_FLOOR_HEAT_LOSS,
+                            CONF_INTER_ZONE_TRANSFER: DEFAULT_INTER_ZONE_TRANSFER,
+                            CONF_RADIATOR_POWER_FRACTION: DEFAULT_RADIATOR_POWER_FRACTION,
+                            CONF_UPPER_FLOOR_AREA_RATIO: DEFAULT_UPPER_FLOOR_AREA_RATIO,
+                            CONF_BUFFER_TANK_VOLUME: DEFAULT_BUFFER_TANK_VOLUME,
+                            CONF_WINDOW_AREA: DEFAULT_WINDOW_AREA,
+                            CONF_SOLAR_ORIENTATION_FACTOR: DEFAULT_SOLAR_ORIENTATION_FACTOR,
+                            CONF_SOLAR_HEAT_GAIN_COEFF: DEFAULT_SOLAR_HEAT_GAIN_COEFF,
+                        },
+                    ),
                 }
             ),
         )
@@ -2955,54 +2886,22 @@ class HeatPumpOptimizerConfigFlow(
                             )
                         },
                     ): selector.BooleanSelector(),
-                    vol.Optional(
-                        CONF_DHW_TANK_VOLUME,
-                        default=DEFAULT_DHW_TANK_VOLUME,
-                    ): _number(50, 1500, 10, "L"),
-                    vol.Optional(
-                        CONF_DHW_SETPOINT,
-                        default=DEFAULT_DHW_SETPOINT,
-                    ): _number(40, 65, 1, "°C", slider=True),
-                    vol.Optional(
-                        CONF_DHW_MIN_TEMP,
-                        default=DEFAULT_DHW_MIN_TEMP,
-                    ): _number(35, 55, 1, "°C", slider=True),
-                    vol.Optional(
-                        CONF_DHW_DAILY_CONSUMPTION,
-                        default=DEFAULT_DHW_DAILY_CONSUMPTION,
-                    ): _number(50, 1500, 10, "L/day"),
-                    vol.Optional(
-                        CONF_DHW_COOLING_RATE,
-                        default=DEFAULT_DHW_COOLING_RATE,
-                    ): _number(0.05, 3.0, 0.05, "°C/h"),
-                    vol.Optional(
-                        CONF_DHW_SCHEDULE_ENABLED,
-                        default=DEFAULT_DHW_SCHEDULE_ENABLED,
-                    ): selector.BooleanSelector(),
-                    vol.Optional(
-                        CONF_DHW_WINDOWS,
-                        default=DEFAULT_DHW_WINDOWS,
-                    ): selector.TextSelector(
-                        selector.TextSelectorConfig(
-                            type=selector.TextSelectorType.TEXT,
-                        )
+                    **_wizard_fields(
+                        vol.Optional,
+                        {
+                            CONF_DHW_TANK_VOLUME: DEFAULT_DHW_TANK_VOLUME,
+                            CONF_DHW_SETPOINT: DEFAULT_DHW_SETPOINT,
+                            CONF_DHW_MIN_TEMP: DEFAULT_DHW_MIN_TEMP,
+                            CONF_DHW_DAILY_CONSUMPTION: DEFAULT_DHW_DAILY_CONSUMPTION,
+                            CONF_DHW_COOLING_RATE: DEFAULT_DHW_COOLING_RATE,
+                            CONF_DHW_SCHEDULE_ENABLED: DEFAULT_DHW_SCHEDULE_ENABLED,
+                            CONF_DHW_WINDOWS: DEFAULT_DHW_WINDOWS,
+                            CONF_DHW_IDLE_MIN_TEMP: DEFAULT_DHW_IDLE_MIN_TEMP,
+                            CONF_DHW_LEGIONELLA_ENABLED: DEFAULT_DHW_LEGIONELLA_ENABLED,
+                            CONF_DHW_LEGIONELLA_TEMP: DEFAULT_DHW_LEGIONELLA_TEMP,
+                            CONF_DHW_LEGIONELLA_INTERVAL_DAYS: DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS,
+                        },
                     ),
-                    vol.Optional(
-                        CONF_DHW_IDLE_MIN_TEMP,
-                        default=DEFAULT_DHW_IDLE_MIN_TEMP,
-                    ): _number(10, 55, 1, "°C", slider=True),
-                    vol.Optional(
-                        CONF_DHW_LEGIONELLA_ENABLED,
-                        default=DEFAULT_DHW_LEGIONELLA_ENABLED,
-                    ): selector.BooleanSelector(),
-                    vol.Optional(
-                        CONF_DHW_LEGIONELLA_TEMP,
-                        default=DEFAULT_DHW_LEGIONELLA_TEMP,
-                    ): _number(55, 70, 1, "°C", slider=True),
-                    vol.Optional(
-                        CONF_DHW_LEGIONELLA_INTERVAL_DAYS,
-                        default=DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS,
-                    ): _number(1, 30, 1, "days", slider=True),
                 }
             ),
         )
@@ -3018,16 +2917,13 @@ class HeatPumpOptimizerConfigFlow(
         return self.async_show_form(
             step_id="weather_sensitivity",
             data_schema=vol.Schema(
-                {
-                    vol.Optional(
-                        CONF_WIND_SENSITIVITY,
-                        default=DEFAULT_WIND_SENSITIVITY,
-                    ): _number(0.0, 0.5, 0.01),
-                    vol.Optional(
-                        CONF_RAIN_HEAT_LOSS_MULTIPLIER,
-                        default=DEFAULT_RAIN_HEAT_LOSS_MULTIPLIER,
-                    ): _number(1.0, 1.5, 0.01),
-                }
+                _wizard_fields(
+                    vol.Optional,
+                    {
+                        CONF_WIND_SENSITIVITY: DEFAULT_WIND_SENSITIVITY,
+                        CONF_RAIN_HEAT_LOSS_MULTIPLIER: DEFAULT_RAIN_HEAT_LOSS_MULTIPLIER,
+                    },
+                )
             ),
         )
 
@@ -3094,7 +2990,7 @@ class HeatPumpOptimizerConfigFlow(
         return self.async_show_form(
             step_id="reauth_confirm",
             data_schema=vol.Schema(
-                {vol.Required(CONF_TIBBER_TOKEN): _tibber_token_selector()}
+                {vol.Required(CONF_TIBBER_TOKEN): _prefill_row(CONF_TIBBER_TOKEN).widget}
             ),
             errors=errors,
         )
diff --git a/dev/programme/delivery/2915.md b/dev/programme/delivery/2915.md
new file mode 100644
index 000000000..50df39242
--- /dev/null
+++ b/dev/programme/delivery/2915.md
@@ -0,0 +1 @@
+- [#2915](https://github.com/tvofi/heatpump_optimizer/pull/2915) — **open**, fix(config-flow): R10-CONFIGFLOW-PAGES arms C and C2 (ARCH2-s5-F1)
diff --git a/tests/config_flow_steps.py b/tests/config_flow_steps.py
index 3dba5f309..716f4a76d 100644
--- a/tests/config_flow_steps.py
+++ b/tests/config_flow_steps.py
@@ -7327,6 +7327,85 @@ async def r9_f5_text_and_menu_findings():
     )
 
 
+# ---------------------------------------------------------------------------
+# R10-CONFIGFLOW-PAGES arm C/C2 (ARCH2-s5-F1, #2238): one setting, one widget.
+# Every setup-flow field whose key has an ``_OPTION_FIELDS`` row renders that
+# row's widget OBJECT, so the two flows cannot offer two ranges for one setting.
+# ---------------------------------------------------------------------------
+#: The flow's steps that render no form when entered bare: two menus, and
+#: ``reconfigure``, which needs a sourced entry and then hands its form to
+#: ``user`` (covered there). Every other ``async_step_*`` is driven, so a new
+#: step joins the census without being listed (reauth was once outside a list).
+NON_FORM_SETUP_STEPS = frozenset({"building", "finish_setup", "reconfigure"})
+
+
+def _schema_leaves(schema):
+    """(marker, widget) for every field, a ``section()``'s fields included."""
+    for marker, value in schema.schema.items():
+        inner = getattr(value, "schema", None)
+        if isinstance(inner, vol.Schema):
+            yield from _schema_leaves(inner)
+        else:
+            yield marker, value
+
+
+async def setup_widgets_are_the_registry_rows():
+    """Each setup field with a registry row delivers that row's widget (``is``)."""
+    R.section("setup flow: every field with an options row renders that row's widget")
+    steps = sorted(
+        name[len("async_step_"):]
+        for name in dir(config_flow.HeatPumpOptimizerConfigFlow)
+        if name.startswith("async_step_")
+    )
+    in_registry, twice, unrendered = 0, [], []
+    for step in steps:
+        flow = config_flow.HeatPumpOptimizerConfigFlow()
+        flow.hass = FakeHass()
+        try:
+            schema = (await getattr(flow, f"async_step_{step}")()).get("data_schema")
+        except Exception as err:  # noqa: BLE001 -- a step that cannot render is reported
+            schema = None
+            if step not in NON_FORM_SETUP_STEPS:
+                unrendered.append(f"{step}:{type(err).__name__}")
+        if schema is None:
+            if step not in NON_FORM_SETUP_STEPS and not any(
+                u.startswith(f"{step}:") for u in unrendered
+            ):
+                unrendered.append(f"{step}:no form")
+            continue
+        for marker, widget in _schema_leaves(schema):
+            key = str(marker)
+            rows = [row for row in config_flow._OPTION_FIELDS if row.key == key]
+            if not rows:
+                continue
+            in_registry += 1
+            if not any(widget is row.widget for row in rows):
+                twice.append(f"{step}:{key}")
+    # The census asserts its own reach: a page that stopped rendering would
+    # pass the identity check vacuously.
+    check(
+        "temperature",
+        "happy",
+        "the setup-widget census renders every step but the declared non-form ones",
+        not unrendered and NON_FORM_SETUP_STEPS <= set(steps),
+        f"unrendered={unrendered} steps={len(steps)}",
+    )
+    check(
+        "temperature",
+        "happy",
+        "the setup-widget census reaches every registry-backed setup field",
+        in_registry >= 66,
+        f"registry-backed setup fields={in_registry}",
+    )
+    check(
+        "temperature",
+        "happy",
+        "no setup field spells a second widget for a setting the options registry declares",
+        not twice,
+        f"{len(twice)} spelled twice: {twice[:12]}",
+    )
+
+
 async def main() -> int:
     if "--self-check" in sys.argv:
         return await self_check()
@@ -7372,6 +7451,7 @@ async def main() -> int:
     await config_flow_device_prefill_offer()
     await device_prefill_preview_texts()
     await r9_f5_text_and_menu_findings()
+    await setup_widgets_are_the_registry_rows()
 
     print()
     LEDGER.print_result_lines()
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index d4fd0a0cb..9a399fcc8 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 18037,
+ "class_excess_loc": 17921,
  "const_modules_over_50": 3,
  "coordinator_attrs": 142,
  "coordinator_multiassigned_attrs": 109,
@@ -16,6 +16,6 @@
  "methods_over_150": 16,
  "methods_over_200": 9,
  "name_kept_members": 38,
- "recorded_at": "6eb552157b63d1e98a9653250789d9fe0027b5bc",
+ "recorded_at": "6d86acc909f7fc465e5736771daf8fa45c1373a4",
  "seam_cut_total": 423
 }

