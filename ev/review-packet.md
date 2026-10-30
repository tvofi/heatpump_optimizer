# Review packet #2976
head: ebbdcaa6792fcd5326a30b15fc733f94dada3512
base: 1148ee635e8278ebbb033b524d54001b2a89218c

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=123938539603 success
arch-score / arch-score id=123938275969 success
arm id=123938176031 skipped
budget-raise-gate / budget-raise-gate id=123938275886 success
cancel-superseded id=123938174449 success
codeql / Analyze (actions) id=123938275928 success
codeql / Analyze (javascript-typescript) id=123938275871 success
codeql / Analyze (python) id=123938275887 success
gate id=123950646509 success
governance / delivery-status id=123938276064 success
governance / delivery-status-publish id=123938277818 skipped
governance / env-matrix id=123938276094 success
governance / instrument-self-tests id=123938276126 success
governance / policy-docs id=123938276120 success
governance / record id=123938277837 skipped
governance / wave-script id=123938276125 success
hassfest / hassfest id=123938275883 success
kernel-points id=123938277492 skipped
pr-contract / pr-contract id=123950439663 success
prelude id=123938174174 success
refresh id=123938174396 success
tests / arch-instrument id=123938427657 success
tests / briefs id=123938275914 success
tests / browser id=123938427604 success
tests / ci-ratchet id=123946185131 skipped
tests / claims-autofix id=123945710458 skipped
tests / closure-scope id=123938276076 success
tests / closures id=123938427652 success
tests / closures-autofix id=123946185514 skipped
tests / coverage id=123938427803 success
tests / coverage-ratchet id=123942961131 success
tests / fast (3.14) id=123938427705 success
tests / graders-head-copy id=123942961212 success
tests / lane-proofs id=123945709145 success
tests / mutation id=123938276114 success
tests / mutation-autofix id=123938477403 skipped
tests / mutation-pins id=123938477827 skipped
tests / nightly-ha id=123938429454 skipped
tests / nightly-status id=123938276059 success
tests / replay id=123938429937 skipped
tests / typing id=123938427591 success
validate / validate-hacs id=123938275795 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item d8131e69: R10-ARCH-DOCS
NOTE body item 792f8c74: R10-UX-HEALTH
NOTE body item 4f772573: R10-UX-HEALTH
NOTE body item 6697dbdf: R10-COP-GATE
CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tools/audit/archscore/score.py --diff origin/main
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift bash tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         node tests/card_drift.mjs origin/main
             `tests/card_drift.mjs` is in the tree at this head
  ok         python3 tests/env_drift.py --claims-only origin/main
             `tests/env_drift.py` is in the tree at this head
  ok         node tests/card.mjs
             `tests/card.mjs` is in the tree at this head
  ok         tests/card.mjs
             `tests/card.mjs` is in the tree at this head
  ok         HPO_BROWSER_SCOPE=auto node tests/card_browser.mjs
             `tests/card_browser.mjs` is in the tree at this head
  ok         python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tools/audit/seat/r10_deeplink_mutants.py RV1_history_bracket_back_in_undriven_keydown RD8_insert_adjacent_html_built_href_driven_residual R4_entry_ignored R6_more_info_instead_of_nav R6b_pending_nav_plus_event
             `tools/audit/seat/r10_deeplink_mutants.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_demand_overbook.py nometer_half meter_half
             `dev/audit/harnesses/r10_demand_overbook.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_learner_eta.py --study "$X/dev/audit/rounds/round10/study-ident"
             `dev/audit/harnesses/r10_learner_eta.py` is in the tree at this head
  unverified git archive 4f2d513c9 dev/audit/rounds/round10/study-ident
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 13 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/translations/sv.json b/custom_components/heatpump_optimizer/translations/sv.json
index 02e7f7ffe..5b12d1aef 100644
--- a/custom_components/heatpump_optimizer/translations/sv.json
+++ b/custom_components/heatpump_optimizer/translations/sv.json
@@ -302,8 +302,8 @@
           "dhw_tank": "Varmvattenberedare",
           "wood_furnace": "Vedpanna",
           "wood_buffer_tank": "Vedpannans tank",
-          "wood_tank_top_entity": "Givare, toppen av vedtanken (valfri)",
-          "wood_tank_bottom_entity": "Givare, botten av vedtanken (valfri)",
+          "wood_tank_top_entity": "Vedtankens toppgivare (valfri)",
+          "wood_tank_bottom_entity": "Vedtankens bottengivare (valfri)",
           "building_structure": "Vad huset är byggt av",
           "building_era": "Ungefär när det byggdes",
           "building_foundation": "Grundläggning",
@@ -1081,8 +1081,8 @@
           "dhw_tank": "Varmvattenberedare",
           "wood_furnace": "Vedpanna",
           "wood_buffer_tank": "Vedpannans tank",
-          "wood_tank_top_entity": "Givare, toppen av vedtanken (valfri)",
-          "wood_tank_bottom_entity": "Givare, botten av vedtanken (valfri)",
+          "wood_tank_top_entity": "Vedtankens toppgivare (valfri)",
+          "wood_tank_bottom_entity": "Vedtankens bottengivare (valfri)",
           "building_structure": "Vad huset är byggt av",
           "building_era": "Ungefär när det byggdes",
           "building_foundation": "Grundläggning",
diff --git a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
index e45f282b6..8e8501dcf 100644
--- a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
+++ b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
@@ -106,21 +106,53 @@ const STRINGS = {
     "health.next_due": "Next solve due now",
     "health.steps": "{n} steps",
     "health.solve_time": "{s} s",
-    "health.input_indoor_temp_entity": "Indoor temperature",
-    "health.input_outdoor_temp_entity": "Outdoor temperature",
-    "health.input_dhw_temp_entity": "Hot-water tank",
-    "health.input_floor_return_temp_entity": "Floor loop return",
-    "health.input_lower_floor_temp_entity": "Lower floor",
-    "health.input_buffer_tank_temp_entity": "Buffer tank",
-    "health.input_solar_radiation_entity": "Solar radiation",
-    "health.input_pv_production_entity": "PV production",
-    "health.input_heat_pump_power_entity": "Heat pump power",
-    "health.input_heat_pump_energy_entity": "Heat pump energy",
-    "health.input_house_power_entity": "House power",
+    "health.input_away_presence_entity": "Away indicator",
+    "health.input_buffer_tank_temp_entity": "Buffer tank temperature sensor",
+    "health.input_compressor_freq_entity": "Compressor frequency entity",
+    "health.input_dhw_disinfection_switch_entity": "Pump's disinfection switch",
+    "health.input_dhw_inlet_entity": "Cold water inlet sensor",
+    "health.input_dhw_setpoint_entity": "Heat pump DHW set-point entity",
+    "health.input_dhw_temp_entity": "Hot water tank temperature sensor",
+    "health.input_external_heat_entity": "Stove or flue sensor",
+    "health.input_floor_return_temp_entity": "Floor heating return temperature sensor",
+    "health.input_flow_meter_entity": "Water flow sensor",
+    "health.input_grid_fee_entity": "Live fee sensor",
+    "health.input_heat_pump_backup_heater_entity": "Space backup heater",
+    "health.input_heat_pump_capacity_limited_entity": "Capacity limited (night mode)",
+    "health.input_heat_pump_defrost_entity": "Defrosting",
+    "health.input_heat_pump_dhw_booster_entity": "Hot water tank booster",
+    "health.input_heat_pump_energy_entity": "Heat pump energy meter",
+    "health.input_heat_pump_fault_entity": "Fault alarm",
+    "health.input_heat_pump_heat_energy_entity": "Heat pump heat energy meter",
+    "health.input_heat_pump_mode_entity": "Heat pump operating mode",
+    "health.input_heat_pump_online_entity": "Pump online",
+    "health.input_heat_pump_power_entity": "Heat pump power meter",
+    "health.input_heat_pump_return_temp_entity": "Return water temperature",
+    "health.input_heat_pump_supply_temp_entity": "Supply (flow) water temperature",
+    "health.input_heat_pump_switch_entity": "Heat pump on/off switch",
+    "health.input_heat_pump_thermal_power_entity": "Heat pump thermal power meter",
+    "health.input_holiday_calendar_entity": "Holiday-profile calendar",
+    "health.input_house_power_entity": "Whole-house power meter",
+    "health.input_indoor_humidity_entity": "Indoor humidity sensor",
+    "health.input_indoor_temp_entity": "Indoor temperature sensor",
+    "health.input_lower_floor_temp_entity": "Lower floor temperature sensor",
+    "health.input_mixing_valve_target_entity": "Valve target sensor",
+    "health.input_mixing_valve_write_entity": "Valve control entity",
+    "health.input_outdoor_temp_entity": "Outdoor temperature sensor",
+    "health.input_price_entity": "Price sensor (Nord Pool or similar)",
+    "health.input_pv_export_price_entity": "Export compensation entity",
+    "health.input_pv_production_entity": "Solar production sensor",
+    "health.input_solar_radiation_entity": "Solar radiation sensor",
+    "health.input_space_circulation_pump_entity": "Heating circulation pump switch",
+    "health.input_space_setpoint_entity": "Space-heating set-point entity",
+    "health.input_valve_outlet_temp_entity": "Temperature after the wood/heat-pump mixing valve",
+    "health.input_vvc_pump_entity": "Hot water circulation pump switch",
+    "health.input_weather_entity": "Weather forecast",
+    "health.input_wood_tank_bottom_entity": "Wood tank bottom sensor",
+    "health.input_wood_tank_top_entity": "Wood tank top sensor",
     "health.learn_savings": "Savings this month",
     "health.learn_savings_why": "Waiting for the first settled month",
     "health.learn_cop": "Heat pump COP",
-    "health.learn_cop_why": "Needs a power meter on the heat pump, then some running time",
     "health.learn_accuracy": "Prediction accuracy",
     "health.learn_accuracy_why": "Waiting for the first scored interval",
     "health.learn_score": "Optimization score",
@@ -149,12 +181,11 @@ const STRINGS = {
     "health.model_cop_low": "Below its own history",
     "health.model_cop_fine": "No sign of degradation.",
     "health.model_cop_alarm": "It delivers less heat per kWh than it used to; check filters, defrost and flow.",
-    "health.model_cop_young": "Not enough running history to watch yet.",
     "health.model_gains_peak": "People, cooking and appliances add up to {kw} kW around {hh}:00.",
     "health.support_title": "Something looks wrong?",
     "health.support_detail":
-      "Open the integration page and choose Download diagnostics in its menu: " +
-      "the file holds the last diagnosis, input states, the current plan and what the model has learned, " +
+      "Download diagnostics saves a file for a bug report: " +
+      "it holds the last diagnosis, input states, the current plan and what the model has learned, " +
       "with tokens, names, people, calendars and locations removed.",
     "health.act_diagnostics": "Download diagnostics",
     "health.check_price": "Price source connected",
@@ -162,9 +193,54 @@ const STRINGS = {
     "health.check_indoor": "Indoor temperature sensor",
     "health.check_control": "Heat pump control connected",
     "health.check_power": "Power meter on the heat pump: makes savings measured instead of modelled",
-    "health.check_insight": "Some insight sensors are off by default; turn them on in the integration's settings",
+    "health.check_insight": "Some insight sensors are off by default; Show lists this integration's entities, disabled ones included, where you can turn them on",
     "health.act_assign": "Assign",
     "health.act_show": "Show",
+    "health.input_other": "Input",
+    "health.learner_waiting": "Waiting: {why}.",
+    "health.learner_wait_colder": "it learns when it is cold enough outside",
+    "health.learner_wait_darker": "it learns in the dark hours",
+    "health.learner_wait_sunnier": "it learns in sunshine",
+    "health.learner_waiting_any": "Waiting for conditions it can learn in.",
+    "health.learner_counting": "Learning: {pct} % of the samples it needs.",
+    "health.learner_eta": "About {d} days until learned.",
+    "health.learner_settling": "Settling on its value: {pct} %.",
+    "health.learner_settling_any": "Settling on its value.",
+    "health.model_unobservable": "Not observable without a power meter.",
+    "health.cop_measured": "Measured {age} ago.",
+    "health.cop_reason_heat_metered": "Measured by the heat meter.",
+    "health.cop_reason_draw_follows_plan": "Read from the power draw, which follows the plan.",
+    "health.cop_reason_not_measurable": "Not measurable here: without a heat meter the power draw does not follow the plan closely enough to read efficiency from.",
+    "health.cop_reason_awaiting_draw_evidence": "Waiting to see whether the power draw follows the plan.",
+    "health.cop_reason_no_electric_meter": "Needs a power or energy meter on the heat pump.",
+    "health.cop_reason_no_measured_power": "Waiting for a power reading from the heat pump.",
+    "health.cop_reason_learners_frozen": "Learning is paused.",
+    "health.cop_reason_duty_floor": "The heat pump ran too little in the interval to judge.",
+    "health.cop_reason_frost_band": "Skipped in the frost band, where defrosting distorts the reading.",
+    "health.cop_reason_draw_distorted": "The power draw was distorted by something else in the interval.",
+    "health.cop_reason_tracking_gate": "The house did not follow the plan closely enough in the interval.",
+    "health.cop_reason_draw_off_ask": "The power draw departed from what the plan asked for.",
+    "health.cop_reason_blended_duty": "Space heating and hot water shared the interval, so neither can be judged.",
+    "health.cop_reason_modelled_cop": "Only a modelled efficiency was available, not a measured one.",
+    "health.cop_reason_observed_cop": "The measured efficiency was outside the plausible range.",
+    "health.cop_reason_span_open": "Waiting for the meter span to close.",
+    "health.cop_reason_unaligned_meters": "The heat and power meters were not read at the same moments.",
+    "health.cop_reason_counter_reset": "The heat meter's counter was reset.",
+    "health.cop_reason_counter_rollover": "The heat meter's counter rolled over.",
+    "health.cop_reason_counter_resolution": "The heat meter's counter is too coarse for the interval.",
+    "health.cop_reason_span_too_long": "The meter span ran too long to use.",
+    "health.metric_heat_loss": "How fast the house loses heat, in watts per degree of difference between inside and outside. Higher is a leakier house; with no samples it is the settings' estimate.",
+    "health.metric_solar": "How much of the sun's heat the windows let in, against the settings. Above 1 lets in more; with no samples it is the settings' value.",
+    "health.metric_lower": "The lower floor's heat loss as a share of the settings' estimate.",
+    "health.metric_tank": "How fast the hot-water tank cools when the pump is off, in °C per hour. Lower is better insulated.",
+    "health.metric_cop": "Whether the heat pump still delivers as much heat per kWh as it used to. A dash means it is not yet watched.",
+    "health.metric_gains": "Heat from people, cooking and appliances by hour of day, which the plan counts as free heating.",
+    "health.debug_title": "Debug collection",
+    "health.debug_off": "Off. When a bug report asks for one, Start records a week of cycles into the diagnostics file.",
+    "health.debug_active": "Collecting: {rows} records so far, about {days} days left.",
+    "health.debug_final": "Finished with {rows} records. Download diagnostics to keep them.",
+    "health.debug_confirm": "Starting again discards the finished collection. Download diagnostics first to keep it, then press Start again.",
+    "health.act_debug_start": "Start",
     // The sensor advisor page (#1269): the backend's ranking of which
     // UNCONFIGURED optional temperature sensors would tighten the thermal
     // model most. Every quantified row is an estimate and says so.
@@ -872,21 +948,53 @@ const STRINGS = {
     "health.next_due": "Nästa lösning är försenad",
     "health.steps": "{n} steg",
     "health.solve_time": "{s} s",
-    "health.input_indoor_temp_entity": "Inomhustemperatur",
-    "health.input_outdoor_temp_entity": "Utomhustemperatur",
-    "health.input_dhw_temp_entity": "Varmvattenberedare",
-    "health.input_floor_return_temp_entity": "Golvslingans retur",
-    "health.input_lower_floor_temp_entity": "Nedre våning",
-    "health.input_buffer_tank_temp_entity": "Buffertank",
-    "health.input_solar_radiation_entity": "Solinstrålning",
-    "health.input_pv_production_entity": "Solcellsproduktion",
-    "health.input_heat_pump_power_entity": "Värmepumpens effekt",
-    "health.input_heat_pump_energy_entity": "Värmepumpens energi",
-    "health.input_house_power_entity": "Husets effekt",
+    "health.input_away_presence_entity": "Indikator för bortavaro",
+    "health.input_buffer_tank_temp_entity": "Temperaturgivare för buffertank",
+    "health.input_compressor_freq_entity": "Entitet för kompressorfrekvens",
+    "health.input_dhw_disinfection_switch_entity": "Pumpens desinfektionsbrytare",
+    "health.input_dhw_inlet_entity": "Givare för inkommande kallvatten",
+    "health.input_dhw_setpoint_entity": "Värmepumpens börvärdesenhet för varmvatten",
+    "health.input_dhw_temp_entity": "Givare för varmvattenberedarens temperatur",
+    "health.input_external_heat_entity": "Givare för panna eller rökgas",
+    "health.input_floor_return_temp_entity": "Givare för golvvärmens returtemperatur",
+    "health.input_flow_meter_entity": "Givare för vattenflöde",
+    "health.input_grid_fee_entity": "Sensor för aktuell avgift",
+    "health.input_heat_pump_backup_heater_entity": "Elpatron för värme",
+    "health.input_heat_pump_capacity_limited_entity": "Begränsad effekt (nattläge)",
+    "health.input_heat_pump_defrost_entity": "Avfrostning",
+    "health.input_heat_pump_dhw_booster_entity": "Elpatron i varmvattenberedaren",
+    "health.input_heat_pump_energy_entity": "Energimätare för värmepumpen",
+    "health.input_heat_pump_fault_entity": "Felindikering",
+    "health.input_heat_pump_heat_energy_entity": "Värmemängdsmätare för värmepumpen",
+    "health.input_heat_pump_mode_entity": "Värmepumpens driftläge",
+    "health.input_heat_pump_online_entity": "Pumpen är uppkopplad",
+    "health.input_heat_pump_power_entity": "Effektmätare för värmepumpen",
+    "health.input_heat_pump_return_temp_entity": "Returtemperatur",
+    "health.input_heat_pump_supply_temp_entity": "Framledningstemperatur",
+    "health.input_heat_pump_switch_entity": "Strömbrytare för värmepumpen",
+    "health.input_heat_pump_thermal_power_entity": "Värmeeffektmätare för värmepumpen",
+    "health.input_holiday_calendar_entity": "Lovprofilkalender",
+    "health.input_house_power_entity": "Effektmätare för hela huset",
+    "health.input_indoor_humidity_entity": "Inomhusfuktsensor",
+    "health.input_indoor_temp_entity": "Inomhusgivare",
+    "health.input_lower_floor_temp_entity": "Givare för temperaturen på nedre plan",
+    "health.input_mixing_valve_target_entity": "Givare för ventilens börvärde",
+    "health.input_mixing_valve_write_entity": "Ventilens styrenhet",
+    "health.input_outdoor_temp_entity": "Utomhusgivare",
+    "health.input_price_entity": "Prissensor (Nord Pool eller liknande)",
+    "health.input_pv_export_price_entity": "Entitet för ersättning",
+    "health.input_pv_production_entity": "Sensor för solproduktion",
+    "health.input_solar_radiation_entity": "Solinstrålningsgivare",
+    "health.input_space_circulation_pump_entity": "Brytare för värmesystemets cirkulationspump",
+    "health.input_space_setpoint_entity": "Börvärdesenhet för rumsuppvärmning",
+    "health.input_valve_outlet_temp_entity": "Temperatur efter shunten mellan ved- och värmepumpstank",
+    "health.input_vvc_pump_entity": "Brytare för VVC-pump",
+    "health.input_weather_entity": "Väderprognos",
+    "health.input_wood_tank_bottom_entity": "Vedtankens bottengivare",
+    "health.input_wood_tank_top_entity": "Vedtankens toppgivare",
     "health.learn_savings": "Sparande den här månaden",
     "health.learn_savings_why": "Väntar på den första avslutade månaden",
     "health.learn_cop": "Värmepumpens COP",
-    "health.learn_cop_why": "Behöver en effektmätare på värmepumpen och en tids drift",
     "health.learn_accuracy": "Prognosträffsäkerhet",
     "health.learn_accuracy_why": "Väntar på det första bedömda intervallet",
     "health.learn_score": "Optimeringspoäng",
@@ -915,12 +1023,11 @@ const STRINGS = {
     "health.model_cop_low": "Under sin egen historik",
     "health.model_cop_fine": "Inga tecken på försämring.",
     "health.model_cop_alarm": "Den ger mindre värme per kWh än förut; kontrollera filter, avfrostning och flöde.",
-    "health.model_cop_young": "För kort drifthistorik för att bevaka än.",
     "health.model_gains_peak": "Människor, matlagning och apparater ger upp till {kw} kW runt {hh}:00.",
     "health.support_title": "Ser något fel ut?",
     "health.support_detail":
-      "Öppna integrationssidan och välj Ladda ner diagnostik i menyn: " +
-      "filen innehåller senaste diagnosen, indatas tillstånd, den aktuella planen och vad modellen har lärt sig, " +
+      "Ladda ner diagnostik sparar en fil för en felrapport: " +
+      "den innehåller senaste diagnosen, indatas tillstånd, den aktuella planen och vad modellen har lärt sig, " +
       "utan nycklar, namn, personer, kalendrar och platser.",
     "health.act_diagnostics": "Ladda ner diagnostik",
     "health.check_price": "Priskälla ansluten",
@@ -928,9 +1035,54 @@ const STRINGS = {
     "health.check_indoor": "Inomhusgivare",
     "health.check_control": "Värmepumpsstyrning ansluten",
     "health.check_power": "Effektmätare på värmepumpen: gör att sparandet mäts i stället för modelleras",
-    "health.check_insight": "Vissa insiktsgivare är avstängda som standard; slå på dem i integrationens inställningar",
+    "health.check_insight": "Vissa insiktsgivare är avstängda som standard; Visa listar integrationens entiteter, även de avstängda, där du kan slå på dem",
     "health.act_assign": "Tilldela",
     "health.act_show": "Visa",
+    "health.input_other": "Indata",
+    "health.learner_waiting": "Väntar: {why}.",
+    "health.learner_wait_colder": "den lär sig när det är tillräckligt kallt ute",
+    "health.learner_wait_darker": "den lär sig under mörka timmar",
+    "health.learner_wait_sunnier": "den lär sig i solsken",
+    "health.learner_waiting_any": "Väntar på förhållanden den kan lära sig i.",
+    "health.learner_counting": "Lär sig: {pct} % av mätningarna den behöver.",
+    "health.learner_eta": "Ungefär {d} dagar tills den är inlärd.",
+    "health.learner_settling": "Stabiliserar sitt värde: {pct} %.",
+    "health.learner_settling_any": "Stabiliserar sitt värde.",
+    "health.model_unobservable": "Går inte att observera utan effektmätare.",
+    "health.cop_measured": "Mätt för {age} sedan.",
+    "health.cop_reason_heat_metered": "Mätt med värmemängdsmätaren.",
+    "health.cop_reason_draw_follows_plan": "Avläst från effektuttaget, som följer planen.",
+    "health.cop_reason_not_measurable": "Går inte att mäta här: utan värmemängdsmätare följer effektuttaget inte planen tillräckligt nära för att verkningsgraden ska kunna avläsas.",
+    "health.cop_reason_awaiting_draw_evidence": "Väntar på att se om effektuttaget följer planen.",
+    "health.cop_reason_no_electric_meter": "Behöver en effekt- eller energimätare på värmepumpen.",
+    "health.cop_reason_no_measured_power": "Väntar på en effektavläsning från värmepumpen.",
+    "health.cop_reason_learners_frozen": "Inlärningen är pausad.",
+    "health.cop_reason_duty_floor": "Värmepumpen gick för lite under intervallet för att bedömas.",
+    "health.cop_reason_frost_band": "Hoppades över i frostbandet, där avfrostning stör avläsningen.",
+    "health.cop_reason_draw_distorted": "Effektuttaget stördes av något annat under intervallet.",
+    "health.cop_reason_tracking_gate": "Huset följde inte planen tillräckligt nära under intervallet.",
+    "health.cop_reason_draw_off_ask": "Effektuttaget avvek från det planen begärde.",
+    "health.cop_reason_blended_duty": "Rumsvärme och varmvatten delade intervallet, så inget av dem kan bedömas.",
+    "health.cop_reason_modelled_cop": "Bara en modellerad verkningsgrad fanns, ingen uppmätt.",
+    "health.cop_reason_observed_cop": "Den uppmätta verkningsgraden låg utanför rimligt intervall.",
+    "health.cop_reason_span_open": "Väntar på att mätarens intervall ska stängas.",
+    "health.cop_reason_unaligned_meters": "Värme- och effektmätarna lästes inte av vid samma tidpunkter.",
+    "health.cop_reason_counter_reset": "Värmemängdsmätarens räkneverk nollställdes.",
+    "health.cop_reason_counter_rollover": "Värmemängdsmätarens räkneverk slog runt.",
+    "health.cop_reason_counter_resolution": "Värmemängdsmätarens räkneverk är för grovt för intervallet.",
+    "health.cop_reason_span_too_long": "Mätarens intervall blev för långt för att användas.",
+    "health.metric_heat_loss": "Hur snabbt huset förlorar värme, i watt per grads skillnad mellan inne och ute. Högre är ett otätare hus; utan mätningar är det inställningarnas uppskattning.",
+    "health.metric_solar": "Hur mycket av solens värme fönstren släpper in, mot inställningarna. Över 1 släpper in mer; utan mätningar är det inställningarnas värde.",
+    "health.metric_lower": "Nedre våningens värmeförlust som andel av inställningarnas uppskattning.",
+    "health.metric_tank": "Hur snabbt varmvattentanken svalnar när pumpen står still, i °C per timme. Lägre är bättre isolerat.",
+    "health.metric_cop": "Om värmepumpen fortfarande ger lika mycket värme per kWh som förut. Ett streck betyder att den inte bevakas än.",
+    "health.metric_gains": "Värme från människor, matlagning och apparater per timme, som planen räknar som gratis uppvärmning.",
+    "health.debug_title": "Felsökningsinsamling",
+    "health.debug_off": "Av. När en felrapport ber om det spelar Starta in en vecka av cykler i diagnostikfilen.",
+    "health.debug_active": "Samlar in: {rows} poster hittills, ungefär {days} dagar kvar.",
+    "health.debug_final": "Klar med {rows} poster. Ladda ner diagnostik för att behålla dem.",
+    "health.debug_confirm": "En ny start kastar den avslutade insamlingen. Ladda ner diagnostik först för att behålla den och tryck sedan Starta igen.",
+    "health.act_debug_start": "Starta",
     "advisor.heading": "Givare som skulle skärpa modellen",
     "advisor.empty":
       "Alla valfria temperaturgivare på denna anläggning är redan konfigurerade.",
@@ -8711,16 +8863,17 @@ function scoreParts(plan) {
     const value = readNumber(attrs[key]);
     return { key, label: L(`score.label_${key}`), value,
       reason: value === null ? scoreReasonText(reasons[key]) : null,
-      drivers: key === "envelope" && value !== null
-        ? envelopeDrivers(attrs.envelope_drivers) : "" };
+      drivers: value !== null ? scoreDrivers(key, attrs[`${key}_drivers`]) : "" };
   });
 }
 
-/** What moves the house grade off 50 (#2816): each driver the coordinator
- * published with its signed whole points, or "typical" when none moves it a
- * point -- so every shown grade carries at least one reason. An unknown
- * code is skipped rather than shown raw. */
-function envelopeDrivers(drivers) {
+/** What moves a sub-score off 50 (#2816): each driver the coordinator
+ * published (`envelope_drivers`, `machine_drivers`) with its signed whole
+ * points, or "typical" when none moves it a point -- so every shown grade
+ * carries at least one reason. A part with no drivers published has none to
+ * show; an unknown code is skipped rather than shown raw. */
+function scoreDrivers(part, drivers) {
+  if (part !== "envelope" && !Array.isArray(drivers)) return "";
   const shown = (Array.isArray(drivers) ? drivers : [])
     .filter((d) => STRINGS.en[`score.driver_${d.code}`] !== undefined)
     .map((d) => ({ code: d.code, pts: Math.round(Number(d.points) || 0) }))
@@ -8861,7 +9014,9 @@ function headlineHtml(plan, cfg, scoreOpen) {
       title:
         L("headline.score_title") +
         (breakdown ? `\n${breakdown}` : "") +
-        (parts[0].drivers ? `\n${L("score.part_envelope")}` : "") +
+        // Every part's metric in plain words, beside its grade and reason or
+        // drivers above (the owner's hover spec).
+        parts.map((p) => `\n${L(`score.part_${p.key}`)}`).join("") +
         `\n${L("headline.score_click_hint")}`,
       label: L("headline.score"),
       value: `${Math.round(score)}/100`,
@@ -9019,7 +9174,8 @@ function restartRows(plan) {
   const rows = [];
   if (refit && finiteNum(refit.scale)) {
     rows.push(row("adopt_refit",
-      L("advisor.refit_title", { to: Number(refit.scale).toFixed(2), from: Number(attrs.current_scale).toFixed(2) }),
+      L("advisor.refit_title", { to: Number(refit.scale).toFixed(2),
+        from: readNumber(attrs.current_scale) === null ? "—" : readNumber(attrs.current_scale).toFixed(2) }),
       L("advisor.refit_detail", { days: Number(refit.settled_days).toFixed(1), pairs: refit.pairs })));
   } else if (refit) {
     rows.push(row("", L("advisor.refit_wait_title"),
@@ -9048,13 +9204,13 @@ function advisorRows(host) {
       };
     }),
     advisorRow(plan, "dhw", (to, attrs) => {
-      const from = Number(attrs.current_setpoint);
-      if (!Number.isFinite(to) || !Number.isFinite(from) || to === from) return null;
+      const from = readNumber(attrs.current_setpoint);
+      if (!Number.isFinite(to) || from === null || to === from) return null;
       const perDay = dhwCostPerDay(attrs.candidates, from) - dhwCostPerDay(attrs.candidates, to);
       // The money is interpolated off the sweep. The write is the recommended
       // setpoint the sensor publishes, never that interpolation.
-      const recommended = Number(attrs.recommended_setpoint);
-      const write = Number.isFinite(recommended) ? recommended : to;
+      const recommended = readNumber(attrs.recommended_setpoint);
+      const write = recommended !== null ? recommended : to;
       return {
         value: perDay > 0 ? perDay * DAYS_PER_MONTH : null,
         act: "apply_dhw", target: write,
@@ -9062,8 +9218,8 @@ function advisorRows(host) {
       };
     }),
     advisorRow(plan, "valve", (to, attrs) => {
-      const from = Number(attrs.configured_target);
-      if (!Number.isFinite(to) || !Number.isFinite(from) || Math.abs(to - from) < 0.5) return null;
+      const from = readNumber(attrs.configured_target);
+      if (!Number.isFinite(to) || from === null || Math.abs(to - from) < 0.5) return null;
       const target = Math.min(30, Math.max(0, Math.round(to * 2) / 2));
       return {
         value: null, target,
@@ -9156,9 +9312,17 @@ function advisorInboxHtml(host) {
     ${optIn}`;
 }
 
-/** Open the integration's settings through Home Assistant's own router. */
-function navigateTo(path) {
+/** The card's one way out: open `path` through Home Assistant's own router,
+ * or, given a file name, save `path` (an object URL) as that file. */
+function navigateTo(path, download) {
   try {
+    if (download) {
+      const a = document.createElement("a");
+      a.href = path;
+      a.download = download;
+      a.click();
+      return;
+    }
     globalThis.history.pushState(null, "", path);
     globalThis.dispatchEvent(new CustomEvent("location-changed"));
   } catch (_err) { /* no router: the row stays advice */ }
@@ -9198,14 +9362,32 @@ function haLink(kind, entryId, entityId) {
  * it is asked of the entity registry for the card's own plan sensor; a failed
  * lookup leaves it null and `haLink` links the whole integration. */
 async function openHaLink(host, kind, entityId) {
-  let entryId = null;
+  const path = haLink(kind, await configEntryId(host), entityId);
+  if (path) navigateTo(path);
+}
+
+/** This card's config entry id, asked of the entity registry for its own plan
+ * sensor, or null when the registry does not answer. */
+async function configEntryId(host) {
   try {
     const reg = await host.hass.callWS({ type: "config/entity_registry/get",
       entity_id: host.plan.resolveEntity("space") });
-    entryId = (reg && reg.config_entry_id) || null;
-  } catch (_err) { /* no registry answer: link the integration */ }
-  const path = haLink(kind, entryId, entityId);
-  if (path) navigateTo(path);
+    return (reg && reg.config_entry_id) || null;
+  } catch (_err) { return null; }
+}
+
+/** Save this entry's diagnostics through Home Assistant's authenticated
+ * per-entry endpoint (the file its own menu downloads). A refused or failed
+ * fetch, or no entry id, opens the entry's page, whose menu has the same. */
+async function downloadDiagnostics(host) {
+  const entryId = await configEntryId(host);
+  let url = null;
+  try {
+    const res = entryId ? await host.hass.fetchWithAuth(`/api/diagnostics/config_entry/${encodeURIComponent(entryId)}`) : null;
+    if (res && res.ok) url = URL.createObjectURL(await res.blob());
+  } catch (_err) { url = null; }
+  if (url) setTimeout(() => URL.revokeObjectURL(url), 60000);
+  navigateTo(url || haLink("options", entryId), url ? `heatpump_optimizer-${entryId}.json` : undefined);
 }
 
 // ---- The Health page (R9-UX-3) ---------------------------------------------
@@ -9270,9 +9452,24 @@ function healthPillHtml(plan) {
   return `<span data-health-pill="${n ? "stale" : "fresh"}" class="status-pill tone-${n ? "warn" : "ok"}">${esc(text)}</span>`;
 }
 
+/** An input's role label, from the card's one table: `health.input_<key>`
+ * exists for every entity field of the options flow, each equal to that
+ * field's options-flow label less its "(optional)" marker (tests/card.mjs
+ * holds the two equal). A key outside the table has no name here, so the
+ * caller says "Input" and shows the entity id; never a name derived from the
+ * key, which read as the user's own entity names beside it. */
 function healthInputLabel(key) {
   const k = `health.input_${key}`;
-  return L(k) === k ? String(key).replace(/_entity$/, "").replace(/_/g, " ") : L(k);
+  return STRINGS.en[k] !== undefined ? L(k) : null;
+}
+
+/** Whether a setup slot has an entity: from the topology the card reads, or
+ * from an input the Input Problem sensor ages. One predicate for the
+ * checklist and the model block. */
+function inputAssigned(plan, key) {
+  const topo = plan.attrRaw("setup_topology", null);
+  const ages = (inputProblemState(plan) || { attributes: {} }).attributes.input_ages_minutes || {};
+  return !!((topo && topo.slots) || []).find((s) => s.key === key && s.entity) || key in ages;
 }
 
 function healthRow(attrs, title, detail, pill) {
@@ -9286,24 +9483,28 @@ function healthInputsHtml(plan) {
   const a = st.attributes || {};
   const problems = Array.isArray(a.problems) ? a.problems : [];
   const bad = new Set(problems.map((p) => p.input));
+  const topo = plan.attrRaw("setup_topology", null);
+  const entityOf = (key) => ((((topo && topo.slots) || []).find((s) => s.key === key)) || {}).entity || "";
   const pill = (tone, text) => `<span class="status-pill tone-${tone}">${esc(text)}</span>`;
+  // A key the table does not name says "Input" and leads with its entity id.
+  const row = (key, entityId, tone, parts, word) => {
+    const label = healthInputLabel(key);
+    return healthRow(` data-health-input="${esc(key)}" data-tone="${tone}"`, label || L("health.input_other"),
+      [label ? "" : entityId, ...parts].filter(Boolean).join(" · "), pill(tone, word));
+  };
   const rows = problems.map((p) => {
     const word = p.problem === "stale" ? L("health.stale")
       : L(`health.p_${p.problem}`) === `health.p_${p.problem}` ? String(p.problem) : L(`health.p_${p.problem}`);
     const age = Number(p.age_minutes), limit = Number(p.max_age_minutes);
-    const detail = [p.entity_id,
+    return row(p.input, p.entity_id, "warn", [healthInputLabel(p.input) ? p.entity_id : "",
       Number.isFinite(age) && p.age_minutes !== null ? L("health.ago", { age: fmtMinutes(age) }) : L("health.no_age"),
-      Number.isFinite(limit) && p.max_age_minutes !== null ? L("health.limit", { limit: fmtMinutes(limit) }) : ""]
-      .filter(Boolean).join(" · ");
-    return healthRow(` data-health-input="${esc(p.input)}" data-tone="warn"`,
-      healthInputLabel(p.input), detail, pill("warn", word));
+      Number.isFinite(limit) && p.max_age_minutes !== null ? L("health.limit", { limit: fmtMinutes(limit) }) : ""], word);
   });
   for (const [key, age] of Object.entries(a.input_ages_minutes || {})) {
     if (bad.has(key)) continue;
-    rows.push(healthRow(` data-health-input="${esc(key)}" data-tone="ok"`, healthInputLabel(key),
-      L("health.ago", { age: fmtMinutes(Number(age)) }), pill("ok", L("health.fresh"))));
+    rows.push(row(key, entityOf(key), "ok", [L("health.ago", { age: fmtMinutes(Number(age)) })], L("health.fresh")));
   }
-  return rows.length ? `<h3 class="health-h">${esc(L("health.inputs"))}</h3>${rows.join("")}` : "";
+  return rows.length ? `<h3 class="health-h">${esc(L("health.inputs"))}</h3><div class="health-inputs">${rows.join("")}</div>` : "";
 }
 
 function healthPlanHtml(plan) {
@@ -9332,16 +9533,37 @@ function healthWaiting(st) {
   return st.state === "unavailable" || (st.state === "unknown" && !!(st.attributes || {}).waiting_for);
 }
 
+/** The model status sensor's attributes, or null while it has none to trust. */
+function healthModelAttrs(plan) {
+  const st = plan.statEntity(HEALTH_MODEL_SUFFIX);
+  return !st || st.state === "unavailable" || st.state === "unknown" ? null : st.attributes || {};
+}
+
+/** Why a waiting sensor waits, in words: the COP from the one COP reading
+ * both rows share, the score from its own sensor's code. */
+function healthWaitingWhy(plan, id) {
+  if (id === "cop") {
+    const cop = (healthModelAttrs(plan) || {}).cop;
+    return cop ? copState(cop).reason : scoreReasonText("cop_watch_learning");
+  }
+  if (id === "score") {
+    const st = plan.statEntity("_plan_optimization_score");
+    return scoreReasonText((((st && st.attributes) || {}).reasons || {}).overall);
+  }
+  return L(`health.learn_${id}_why`);
+}
+
 function healthLearningHtml(plan) {
   const rows = HEALTH_WAITING.filter(([, sfx]) => healthWaiting(plan.statEntity(sfx)))
-    .map(([id]) => healthRow("", L(`health.learn_${id}`), L(`health.learn_${id}_why`), ""));
+    .map(([id]) => healthRow("", L(`health.learn_${id}`), healthWaitingWhy(plan, id), ""));
   return rows.length ? `<div class="health-learning"><h3 class="health-h">${esc(L("health.learning"))}</h3>${rows.join("")}</div>` : "";
 }
 
-/** One learner row: what it is, its evidence in words, its value and a bar. */
+/** One learner row: what it is, its evidence in words, its value and a bar.
+ * Its hover says what the figure is (`health.metric_<id>`). */
 function healthModelRow(id, title, detail, value, share, tone) {
   const pct = Math.round(Math.max(0, Math.min(1, Number(share) || 0)) * 100);
-  return `<div class="health-row model-row" data-model-row="${id}" data-tone="${tone || "ok"}">` +
+  return `<div class="health-row model-row" data-model-row="${id}" data-tone="${tone || "ok"}" title="${esc(L(`health.metric_${id}`))}">` +
     `<span class="adv-text">${esc(title)}<span class="adv-sub">${esc(detail)}</span></span>` +
     `<span class="model-value">${esc(value)}</span>` +
     `<span class="model-bar" aria-hidden="true"><span style="width:${pct}%"></span></span></div>`;
@@ -9357,44 +9579,104 @@ function healthVersusSettings(what, factor) {
 }
 
 /** The 24 hourly internal-gains bars, in the accent colour, and the peak. */
-function healthGainsRow(gains) {
+function healthGainsRow(gains, learning) {
   const kw = gains.map((g) => Math.max(0, Number(g) || 0));
   const top = Math.max(...kw);
   const at = kw.indexOf(top);
   const bars = kw.map((g, h) => `<span class="gains-bar" title="${String(h).padStart(2, "0")}:00" ` +
     `style="height:${top > 0 ? Math.max(4, Math.round((g / top) * 100)) : 4}%"></span>`).join("");
-  return `<div class="health-row model-row" data-model-row="gains" data-tone="ok">` +
+  const peak = L("health.model_gains_peak", { kw: top.toFixed(1), hh: String(at).padStart(2, "0") });
+  return `<div class="health-row model-row" data-model-row="gains" data-tone="ok" title="${esc(L("health.metric_gains"))}">` +
     `<span class="adv-text">${esc(L("health.model_gains"))}<span class="adv-sub">` +
-    `${esc(L("health.model_gains_peak", { kw: top.toFixed(1), hh: String(at).padStart(2, "0") }))}</span></span>` +
+    `${esc(learning ? `${learning.text} ${peak}` : peak)}</span></span>` +
     `<span class="gains-strip" aria-hidden="true">${bars}</span></div>`;
 }
 
+/** One learner's phase (`learner_progress`, R10-LEARNER-ETA) in words, or
+ * null for "off". Only a counting learner has a day figure: a settling one
+ * has passed its count and has none to give. `undefined` when the backend
+ * published no phase, so the row keeps its sample count. */
+function learnerPhase(p) {
+  if (!p || typeof p !== "object") return undefined;
+  const pct = readNumber(p.progress) === null ? null : Math.round(readNumber(p.progress) * 100);
+  if (p.phase === "off") return null;
+  if (p.phase === "waiting") {
+    const why = `health.learner_wait_${p.waiting_for}`;
+    return { text: STRINGS.en[why] !== undefined ? L("health.learner_waiting", { why: L(why) })
+      : L("health.learner_waiting_any"), share: (pct || 0) / 100 };
+  }
+  if (p.phase === "counting") {
+    const eta = readNumber(p.eta_days);
+    return { text: [L("health.learner_counting", { pct: pct || 0 }),
+      eta === null ? "" : L("health.learner_eta", { d: Math.max(1, Math.round(eta)) })].filter(Boolean).join(" "),
+    share: (pct || 0) / 100 };
+  }
+  if (p.phase === "settling") {
+    return { text: pct === null ? L("health.learner_settling_any") : L("health.learner_settling", { pct }),
+      share: pct === null ? 1 : pct / 100 };
+  }
+  return undefined;
+}
+
+/** The heat pump's COP in one reading (`ModelStatusSensor`'s `cop`), for
+ * both Health sites that show it -- the model row and the learning row --
+ * so the two cannot disagree. In order: an alarm; an install the gate
+ * rules cannot observe its COP (`cop_observability`, R10-COP-GATE), even
+ * with buckets watched before that ruling; a watched COP; else a dash and
+ * the first reason published: the learner's last refusal, the gate's wait
+ * for draw evidence, or not enough data. An unknown code is not enough data,
+ * never the raw code. */
+function copState(cop) {
+  const c = cop || {};
+  const obs = c.cop_observability;
+  const words = (code) => (STRINGS.en[`health.cop_reason_${code}`] !== undefined ? L(`health.cop_reason_${code}`) : null);
+  const scale = readNumber(c.scale);
+  if (c.alarm) return { value: L("health.model_cop_low"), reason: L("health.model_cop_alarm"), tone: "warn", watched: true };
+  if (obs === "not_measurable" || obs === "no_electric_meter") {
+    return { value: "—", reason: words(obs), tone: "ok", watched: false };
+  }
+  if (readNumber(c.watched_buckets) > 0 && scale !== null) {
+    const source = obs === "heat_metered" || obs === "draw_follows_plan" ? words(obs) : "";
+    return { value: L("health.model_cop_normal", { v: scale.toFixed(2) }),
+      reason: [L("health.model_cop_fine"), source].filter(Boolean).join(" "), tone: "ok", watched: true };
+  }
+  return { value: "—", tone: "ok", watched: false,
+    reason: words(c.cop_refusal) || (obs === "awaiting_draw_evidence" && words(obs)) || scoreReasonText("cop_watch_learning") };
+}
+
 /** "What the model has learned" (R9-UX-7): the model status sensor's rows. */
 function healthModelHtml(plan) {
-  const st = plan.statEntity(HEALTH_MODEL_SUFFIX);
-  if (!st || st.state === "unavailable" || st.state === "unknown") return "";
-  const a = st.attributes || {};
+  const a = healthModelAttrs(plan);
+  if (!a) return "";
   const num = (v) => (v === null || v === undefined || v === "" ? NaN : Number(v));
+  const lp = a.learner_progress || {};
   const rows = [];
   const hl = a.heat_loss || {};
-  if (Number.isFinite(num(a.heat_loss_w_per_k))) {
-    rows.push(healthModelRow("heat_loss", L("health.model_heat_loss"),
-      hl.learned ? `${L("health.model_from", { n: hl.samples })} ${healthVersusSettings(L("health.model_house"), hl.scale)}`
-        : L("health.model_estimate"),
-      L("health.model_w_per_k", { v: Math.round(num(a.heat_loss_w_per_k)) }), hl.learned ? 1 : 0));
+  const house = learnerPhase(lp.house);
+  if (Number.isFinite(num(a.heat_loss_w_per_k)) && house !== null) {
+    // Without a power meter the house's scale cannot be told from what the
+    // pump delivers (R10-DEMAND-OVERBOOK), so it is not called learned.
+    const detail = !inputAssigned(plan, "heat_pump_power_entity") ? L("health.model_unobservable")
+      : hl.learned ? `${L("health.model_from", { n: hl.samples })} ${healthVersusSettings(L("health.model_house"), hl.scale)}`
+        : house ? house.text : L("health.model_estimate");
+    rows.push(healthModelRow("heat_loss", L("health.model_heat_loss"), detail,
+      L("health.model_w_per_k", { v: Math.round(num(a.heat_loss_w_per_k)) }), hl.learned ? 1 : house ? house.share : 0));
   }
   const sol = a.solar_aperture || {};
-  if (Number.isFinite(num(sol.scale))) {
+  const solar = learnerPhase(lp.solar);
+  if (Number.isFinite(num(sol.scale)) && solar !== null) {
     const n = num(sol.samples) || 0, need = num(sol.needed) || 0;
     rows.push(healthModelRow("solar", L("health.model_solar"),
-      need > 0 && n < need ? L("health.model_learning", { n, need }) : L("health.model_from", { n }),
-      L("health.model_window", { v: num(sol.scale).toFixed(2) }), need > 0 ? n / need : 1));
+      solar ? solar.text : need > 0 && n < need ? L("health.model_learning", { n, need }) : L("health.model_from", { n }),
+      L("health.model_window", { v: num(sol.scale).toFixed(2) }), solar ? solar.share : need > 0 ? n / need : 1));
   }
   const lf = a.lower_floor || {};
-  if (lf.learned && Number.isFinite(num(lf.ratio))) {
+  const lower = learnerPhase(lp.lower);
+  if ((lf.learned || lower) && Number.isFinite(num(lf.ratio))) {
     rows.push(healthModelRow("lower", L("health.model_lower"),
-      `${L("health.model_from", { n: lf.samples })} ${healthVersusSettings(L("health.model_lower_floor"), lf.ratio)}`,
-      L("health.model_share", { v: Math.round(num(lf.ratio) * 100) }), 1));
+      lf.learned ? `${L("health.model_from", { n: lf.samples })} ${healthVersusSettings(L("health.model_lower_floor"), lf.ratio)}`
+        : lower.text,
+      L("health.model_share", { v: Math.round(num(lf.ratio) * 100) }), lf.learned ? 1 : lower.share));
   }
   const tk = a.tank_cooling;
   if (tk && Number.isFinite(num(tk.rate_c_per_h))) {
@@ -9402,30 +9684,30 @@ function healthModelHtml(plan) {
       tk.learned ? L("health.model_from", { n: tk.samples }) : L("health.model_default"),
       L("health.model_per_hour", { v: num(tk.rate_c_per_h).toFixed(1) }), tk.learned ? 1 : 0));
   }
-  const cop = a.cop || {};
-  if (cop.alarm || Number.isFinite(num(cop.scale))) {
-    const watched = num(cop.watched_buckets) > 0;
-    rows.push(healthModelRow("cop", L("health.model_cop"),
-      cop.alarm ? L("health.model_cop_alarm") : watched ? L("health.model_cop_fine") : L("health.model_cop_young"),
-      cop.alarm ? L("health.model_cop_low") : L("health.model_cop_normal", { v: num(cop.scale).toFixed(2) }),
-      watched || cop.alarm ? 1 : 0, cop.alarm ? "warn" : "ok"));
+  const cop = a.cop;
+  if (cop && (cop.alarm || Number.isFinite(num(cop.scale)) || cop.cop_observability || cop.cop_refusal)) {
+    const s = copState(cop);
+    const at = Date.parse(cop.measured_cop_at);
+    const age = Number.isFinite(at) && at <= Date.now() ? L("health.cop_measured", { age: fmtMinutes((Date.now() - at) / 60000) }) : "";
+    rows.push(healthModelRow("cop", L("health.model_cop"), [s.reason, age].filter(Boolean).join(" "),
+      s.value, s.watched ? 1 : 0, s.tone));
+  }
+  const gains = learnerPhase(lp.gains);
+  if (Array.isArray(a.internal_gains_kw) && a.internal_gains_kw.length === 24 && gains !== null) {
+    rows.push(healthGainsRow(a.internal_gains_kw, gains && gains.share < 1 ? gains : null));
   }
-  if (Array.isArray(a.internal_gains_kw) && a.internal_gains_kw.length === 24) rows.push(healthGainsRow(a.internal_gains_kw));
   return rows.length ? `<div class="health-model"><h3 class="health-h">${esc(L("health.model"))}</h3>${rows.join("")}</div>` : "";
 }
 
 function healthChecklistHtml(plan) {
-  const topo = plan.attrRaw("setup_topology", null);
-  const ages = (inputProblemState(plan) || { attributes: {} }).attributes.input_ages_minutes || {};
-  const assigned = (key) => !!((topo && topo.slots) || []).find((s) => s.key === key && s.entity) || key in ages;
   const status = (plan.statEntity(HEALTH_STATUS_SUFFIX) || {}).attributes || {};
   const items = [
     ["price", Number(status.prices_available) > 0, ""],
     ["weather", Number(status.weather_forecast_available) > 0, ""],
-    ["indoor", assigned("indoor_temp_entity"), ""],
-    ["control", assigned("heat_pump_switch_entity"), ""],
-    ["power", assigned("heat_pump_power_entity"), "assign"],
-    ["insight", false, "settings"],
+    ["indoor", inputAssigned(plan, "indoor_temp_entity"), ""],
+    ["control", inputAssigned(plan, "heat_pump_switch_entity"), ""],
+    ["power", inputAssigned(plan, "heat_pump_power_entity"), "assign"],
+    ["insight", false, "show_entities"],
   ];
   return `<h3 class="health-h">${esc(L("health.checklist"))}</h3>` + items.map(([id, done, act]) =>
     `<div class="health-row" data-check="${id}" data-done="${done}"><span class="health-mark">${done ? "✓" : ""}</span>` +
@@ -9434,17 +9716,71 @@ function healthChecklistHtml(plan) {
       `${esc(L(act === "assign" ? "health.act_assign" : "health.act_show"))}</button>` : "") + `</div>`).join("");
 }
 
+const DEBUG_DAYS = 7; // debugger.py's collection window
+
+/** This entry's debug collection, from the `debug_collect` service's
+ * response (`{context, response: {debug: {<entry id>: status}}}`), or null:
+ * a status at any other level, or keyed by another entry, is not ours. */
+function debugStatusOf(res, entryId) {
+  const s = res && res.response && res.response.debug && res.response.debug[entryId];
+  return s && typeof s === "object" ? s : null;
+}
+
+/** Ask the backend for this entry's collection and redraw when it changed.
+ * The state is on no entity, only in the service's response (#2809). */
+async function healthDebugRefresh(host, action = "status") {
+  host._debugAt = Date.now();
+  const entryId = await configEntryId(host);
+  if (!entryId) return;
+  let res = null;
+  try {
+    res = await host.hass.callService("heatpump_optimizer", "debug_collect",
+      { action, entry_id: entryId }, undefined, false, true);
+  } catch (_err) { /* no answer: off */ }
+  const st = debugStatusOf(res, entryId);
+  if (JSON.stringify(st) === JSON.stringify(host._debug || null)) return;
+  host._debug = st;
+  host._render();
+}
+
+/** The collection row: active, finished, or off, and a Start that discards a
+ * finished collection only on a second press, after saying so (#2815). */
+function healthDebugHtml(host) {
+  if (Date.now() - (host._debugAt || 0) > 60000) healthDebugRefresh(host);
+  const st = host._debug || {};
+  const rows = Number(st.rows) || 0;
+  const start = Date.parse(st.started_at);
+  const days = Number.isFinite(start) ? Math.max(0, Math.ceil((start + DEBUG_DAYS * 864e5 - Date.now()) / 864e5)) : DEBUG_DAYS;
+  const state = st.active ? "active" : st.final ? "final" : "off";
+  const text = host._debugArmed && state === "final" ? L("health.debug_confirm")
+    : state === "active" ? L("health.debug_active", { rows, days })
+      : state === "final" ? L("health.debug_final", { rows }) : L("health.debug_off");
+  return `<div class="health-row health-debug" data-debug="${state}"><span class="adv-text">${esc(L("health.debug_title"))}` +
+    `<span class="adv-sub">${esc(text)}</span></span>` +
+    (state === "active" ? "" : `<button type="button" class="adv-act" data-act="debug_start">${esc(L("health.act_debug_start"))}</button>`) +
+    `</div>`;
+}
+
+// Scoped to the page that draws it, like RECEIPT_CSS: the card's shared style
+// block and every other page's markup stay as they were. The inputs span the
+// page in as many columns as fit (owner, item 2).
+const HEALTH_CSS = `.health-inputs {
+  display: grid; grid-template-columns: repeat(auto-fill, minmax(18em, 1fr)); gap: 0 12px;
+}`;
+
 function healthPageHtml(host) {
   const plan = host.plan;
-  return `<div class="setup-page health-page">
+  return `<style>${HEALTH_CSS}</style><div class="setup-page health-page">
     <div class="health-cols">
-      <div class="health-col">${healthInputsHtml(plan)}</div>
-      <div class="health-col">${healthPlanHtml(plan)}${healthLearningHtml(plan)}</div>
+      <div class="health-col">${healthPlanHtml(plan)}</div>
+      <div class="health-col">${healthLearningHtml(plan)}</div>
     </div>
+    ${healthInputsHtml(plan)}
     ${healthModelHtml(plan)}
     <div class="health-row health-support"><span class="adv-text">${esc(L("health.support_title"))}
       <span class="adv-sub">${esc(L("health.support_detail"))}</span></span>
       <button type="button" class="adv-act" data-act="diagnostics">${esc(L("health.act_diagnostics"))}</button></div>
+    ${healthDebugHtml(host)}
     ${healthChecklistHtml(plan)}
     <div class="setup-result" role="status"></div></div>`;
 }
@@ -9732,8 +10068,22 @@ function attachAdvisorInbox(host, root) {
       } else if (act === "open_options") {
         openHaLink(host, "options", null);
         return;
-      } else if (act === "settings" || act === "diagnostics") {
-        navigateTo(SETTINGS_PATH);
+      } else if (act === "show_entities") {
+        openHaLink(host, "entities", null);
+        return;
+      } else if (act === "diagnostics") {
+        await downloadDiagnostics(host);
+        return;
+      } else if (act === "debug_start") {
+        // A finished collection is discarded by a start: the first press only
+        // says so (#2815).
+        if ((host._debug || {}).final && Number(host._debug.rows) > 0 && !host._debugArmed) {
+          host._debugArmed = true;
+          host._render();
+          return;
+        }
+        host._debugArmed = false;
+        await healthDebugRefresh(host, "start");
         return;
       } else if (act === "apply_valve") {
         const to = Number(btn.dataset.target);
@@ -9799,10 +10149,13 @@ class ExpandedDialog {
 
   /** Remember where the user was before `root` is rebuilt: the body scrolls,
    * and a plan refresh on the coordinator's schedule must not jump it back
-   * to the top mid-edit. */
+   * to the top mid-edit. A body still showing another page than the one
+   * about to be drawn (a tab was just pressed, which zeroed the offset) has
+   * no position to carry: the new page opens at its top (R10-UX-HEALTH
+   * item 3, its first row drawn under the head at the old page's offset). */
   saveScroll(root) {
-    const openBody = root.querySelector("dialog.expanded .dlg-body");
-    this.scroll = openBody ? openBody.scrollTop : this.scroll || 0;
+    const [body, shown] = [".dlg-body", ".dlg-tab.active"].map((sel) => root.querySelector(`dialog.expanded ${sel}`));
+    if (body && (!shown || shown.dataset.page === this.activePage())) this.scroll = body.scrollTop;
   }
 
   /** Which page an expanded dialog opens on, decided once `anyData` is known
@@ -14116,6 +14469,7 @@ class HeatpumpOptimizerCard extends HTMLElement {
       // The Health page reads its own sensors, and its "ago" figures move
       // with the clock while it is open (R9-UX-3).
       healthSignature(this.plan, this.dialog.expanded && this.dialog.activePage() === "health" ? Date.now() : 0),
+      JSON.stringify([this._debug || null, !!this._debugArmed]),
       JSON.stringify(this.plan.attrRaw("wood_fuel", null)),
       this.plan.awaySignature(),
       // A dark-mode toggle redraws the whatif result colours (D4-s1-01)
diff --git a/dev/programme/delivery/2976.md b/dev/programme/delivery/2976.md
new file mode 100644
index 000000000..936fe1962
--- /dev/null
+++ b/dev/programme/delivery/2976.md
@@ -0,0 +1 @@
+- [#2976](https://github.com/tvofi/heatpump_optimizer/pull/2976) — **open**, R10-UX-HEALTH: the Health tab, from the owner's report of 2026-10-14 (R10-UX-HEALTH)
diff --git a/tests/card.mjs b/tests/card.mjs
index 99b6fa020..7519d6878 100644
--- a/tests/card.mjs
+++ b/tests/card.mjs
@@ -3937,6 +3937,26 @@ const restartStates = (patch = {}) => {
   await press(vhp.c, '[data-act="apply_valve"]');
   check("the valve target is clamped to 30 °C",
     vhp.calls[0] && vhp.calls[0][2].manual_setpoint === 30, JSON.stringify(vhp.calls));
+  // R10-SCORES' carry to R10-UX-HEALTH: an attribute the backend published as
+  // None is no reading, never a measured 0 (`Number(null)` is 0).
+  const nr = inboxStates();
+  nr[`${PFX}_dhw_setpoint_advisor`].attributes.recommended_setpoint = null;
+  const nrp = mkInbox(nr);
+  await press(nrp.c, '[data-act="apply_dhw"]');
+  check("a null recommended setpoint writes the advisor's state, never 0",
+    nrp.calls[0] && nrp.calls[0][2].dhw_setpoint === 48 && /55 → 48 °C/.test(nrp.html()), JSON.stringify(nrp.calls));
+  const nc = inboxStates();
+  nc[`${PFX}_dhw_setpoint_advisor`].attributes.current_setpoint = null;
+  check("a null current hot-water setpoint is no row, not a move from 0",
+    !/data-act="apply_dhw"/.test(mkInbox(nc).html()));
+  const nv = inboxStates();
+  nv[`${PFX}_valve_target_recommendation`].attributes.configured_target = null;
+  check("a null configured valve target is no row, not a move from 0",
+    !/data-act="apply_valve"/.test(mkInbox(nv).html()));
+  const ns = restartStates({ current_scale: null });
+  const nsRow = mkInbox(ns).html().split('class="adv-inbox-row').find((r) => /data-act="adopt_refit"/.test(r)) || "";
+  check("a null current scale reads as a dash in the refit row, not 0.00",
+    /—/.test(nsRow) && !/0\.00/.test(nsRow), nsRow.slice(0, 300));
 
   await press(c, '[data-act="assign"]');
   check("Assign sensor opens the setup picker for the gap's top slot",
@@ -11913,7 +11933,7 @@ check("without an indoor reading the corner now label is absent",
     ["price", "weather", "indoor", "control"].map((k) => `${k}=${(done(k) || [])[1]}`).join(" "));
   check("a missing power meter is recommended with an Assign action; insight sensors have a Show action",
     (done("power") || [])[1] === "false" && /data-act="assign" data-key="heat_pump_power_entity"/.test(page)
-    && /data-check="insight"[\s\S]*?data-act="settings"/.test(page));
+    && /data-check="insight"[\s\S]*?data-act="show_entities"/.test(page));
   check("the insight-sensor row carries no invented count", !/\d+ insight sensors/.test(page));
   const noPrice = healthStates();
   noPrice[`${PFX}_optimization_status`].attributes.prices_available = 0;
@@ -11928,7 +11948,7 @@ check("without an indoor reading the corner now label is absent",
   try {
     if (btn) await Promise.all((btn._listeners.click || []).map((f) => f({ stopPropagation() {}, detail: 1 })));
   } finally { ctx.history = NAV.history; }
-  check("pressing it opens /config/integrations/integration/heatpump_optimizer",
+  check("pressing it with no entry to fetch for opens /config/integrations/integration/heatpump_optimizer",
     hist.includes("/config/integrations/integration/heatpump_optimizer"), JSON.stringify(hist));
   const pw = mkHealth(healthStates());
   const assignBtn = pw.c.shadowRoot.querySelector('[data-check="power"] [data-act="assign"]');
@@ -11936,6 +11956,10 @@ check("without an indoor reading the corner now label is absent",
   check("Assign on the power meter opens the Setup picker for that slot",
     pw.c.dialog.page === "setup" && pw.c.setup.pickerKey === "heat_pump_power_entity",
     `${pw.c.dialog.page} ${pw.c.setup.pickerKey}`);
+  // P08 (carry 5): and draws it -- a press that only set the state would leave
+  // the Health page on screen until something else re-rendered.
+  check("Assign redraws the dialog on the Setup page",
+    /setup-page/.test(pw.html()) && !/health-page"/.test(pw.html()));
 
   const sig1 = c._signature();
   const s2 = healthStates();
@@ -11965,6 +11989,8 @@ check("without an indoor reading the corner now label is absent",
       internal_gains_kw: [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.4, 0.4, 0.3, 0.3, 0.3, 0.3,
         0.3, 0.3, 0.3, 0.3, 0.4, 0.5, 0.6, 0.5, 0.4, 0.3, 0.2, 0.2],
       ...over } };
+    // A power meter, so the house's heat loss is observable (R10-UX-HEALTH D).
+    s[DEFAULT_SPACE].attributes.setup_topology.slots[2].entity = "sensor.hp_power";
     return s;
   };
   const modelOf = (states, lang) => {
@@ -12094,6 +12120,249 @@ check("without an indoor reading the corner now label is absent",
     wordsFor(undefined, "unknown_unit") === "Unknown unit" && wordsFor("sv-SE", "unknown_unit") === "Okänd enhet",
     `${wordsFor(undefined, "unknown_unit")} / ${wordsFor("sv-SE", "unknown_unit")}`);
 
+  // R10-UX-HEALTH (owner report 2026-10-14). Item 1: every input row carries
+  // the integration's role label, from the card's one table, and that table
+  // equals the options flow's own labels in each language.
+  {
+    const lab = healthStates();
+    lab[BIN].attributes.input_ages_minutes = { wood_tank_top_entity: 3, heat_pump_supply_temp_entity: 2, mystery_entity: 5 };
+    lab[DEFAULT_SPACE].attributes.setup_topology.slots.push(
+      { key: "mystery_entity", label: "x", place: "heat_pump", entity: "sensor.my_thing", domains: ["sensor"] });
+    const rowText = (html, key) => (new RegExp(`data-health-input="${key}"[\\s\\S]*?</div>`).exec(pageOf(html)) || [""])[0];
+    const en = mkHealth(lab).html(), svh = mkHealth(lab, "sv-SE").html();
+    check("UX-HEALTH A: input rows carry the options flow's role labels in English",
+      /Wood tank top sensor/.test(rowText(en, "wood_tank_top_entity"))
+      && /Supply \(flow\) water temperature/.test(rowText(en, "heat_pump_supply_temp_entity"))
+      && !/wood tank top|heat pump supply temp/.test(pageOf(en)), rowText(en, "wood_tank_top_entity"));
+    check("UX-HEALTH A: and in Swedish, the wood pair from its owning page",
+      /Vedtankens toppgivare/.test(rowText(svh, "wood_tank_top_entity"))
+      && /Framledningstemperatur/.test(rowText(svh, "heat_pump_supply_temp_entity")), rowText(svh, "wood_tank_top_entity"));
+    check("UX-HEALTH A: a key the table does not name reads Input with its entity id, never a name from the key",
+      /Input<span class="adv-sub">sensor\.my_thing/.test(rowText(en, "mystery_entity")) && !/mystery/.test(rowText(en, "mystery_entity").replace(/data-health-input="mystery_entity"/, "")),
+      rowText(en, "mystery_entity"));
+    // The equality: one label per options-flow field per language, the
+    // owning page's (never the quick_setup / modbus_prefill shortcuts), and
+    // the card's label is it less the language's optional marker.
+    const SHORTCUT = new Set(["quick_setup", "modbus_prefill"]);
+    const STRIP = { en: [" (optional)"], sv: [" (valfri)", " (valfritt)"] };
+    const FILES = { en: "custom_components/heatpump_optimizer/strings.json",
+      sv: "custom_components/heatpump_optimizer/translations/sv.json" };
+    const tbl = fn("STRINGS");
+    for (const lang of ["en", "sv"]) {
+      const json = JSON.parse(fs.readFileSync(FILES[lang], "utf8"));
+      const fields = {};
+      const walk = (n, path) => {
+        if (!n || typeof n !== "object") return;
+        for (const [k, v] of Object.entries(n)) {
+          if (k === "data" && v && typeof v === "object") {
+            for (const [f, l] of Object.entries(v)) {
+              if (f.endsWith("_entity") && typeof l === "string") (fields[f] ||= []).push([path.concat(k), l]);
+            }
+          }
+          walk(v, path.concat(k));
+        }
+      };
+      walk(json.options, ["options"]);
+      walk(json.config, ["config"]);
+      const strip = (l) => STRIP[lang].reduce((t, m) => (t.endsWith(m) ? t.slice(0, -m.length) : t), l);
+      const twoLabels = Object.entries(fields).filter(([, occ]) => new Set(occ.map(([, l]) => l)).size > 1).map(([f]) => f);
+      check(`UX-HEALTH A: every options-flow entity field has one label in ${lang}`,
+        Object.keys(fields).length > 0 && twoLabels.length === 0, `two labels: ${twoLabels.join(", ")}`);
+      const owning = (occ) => (occ.find(([p]) => !p.some((x) => SHORTCUT.has(x))) || occ[0])[1];
+      const off = Object.entries(fields).filter(([f, occ]) => tbl[lang][`health.input_${f}`] !== strip(owning(occ)))
+        .map(([f, occ]) => `${f}: card "${tbl[lang][`health.input_${f}`]}" vs "${strip(owning(occ))}"`);
+      const extra = Object.keys(tbl[lang]).filter((k) => /^health\.input_.+_entity$/.test(k) && !(k.slice(13) in fields));
+      check(`UX-HEALTH A: the card's ${lang} input labels are the options flow's, marker stripped, and no others`,
+        off.length === 0 && extra.length === 0, `${off.join("; ")} | extra ${extra.join(",")}`);
+    }
+  }
+
+  // Item 5: what a learner's phase is (learner_progress), and one COP reading
+  // behind both rows that show it.
+  {
+    const metered = modelStates;
+    const unmetered = modelStates();
+    unmetered[DEFAULT_SPACE].attributes.setup_topology.slots[2].entity = null;
+    const lp = (house) => ({ heat_loss: { scale: 1.0, samples: 3, learned: false }, learner_progress: { house } });
+    const settling = rowOf(modelOf(metered(lp({ phase: "settling", progress: 0.5, eta_days: 12, samples: 40 }))), "heat_loss");
+    check("UX-HEALTH D: a settling learner shows its progress and never a day figure",
+      /Settling on its value: 50 %/.test(settling) && !/day/i.test(settling), settling);
+    const counting = rowOf(modelOf(metered(lp({ phase: "counting", progress: 0.25, eta_days: 12, samples: 5 }))), "heat_loss");
+    check("UX-HEALTH D: a counting learner shows its progress and the days until its gate",
+      /25 %/.test(counting) && /About 12 days until learned/.test(counting), counting);
+    const waiting = rowOf(modelOf(metered(lp({ phase: "waiting", progress: null, waiting_for: "colder", samples: 0 }))), "heat_loss");
+    check("UX-HEALTH D: a waiting learner says what it waits for in words",
+      /Waiting: it learns when it is cold enough outside/.test(waiting) && !/colder/.test(waiting), waiting);
+    check("UX-HEALTH D: a learner that is off has no row",
+      !/data-model-row="gains"/.test(modelOf(metered({ learner_progress: { gains: { phase: "off", samples: 0 } } }))));
+    const nometer = rowOf(modelOf(unmetered), "heat_loss");
+    check("UX-HEALTH D: with no power meter the heat loss is not called learned",
+      /Not observable without a power meter/.test(nometer) && !/Learned from/.test(nometer), nometer);
+    check("UX-HEALTH D: a metered install's learned heat loss still says learned (null control)",
+      /Learned from 21 samples/.test(rowOf(modelOf(metered()), "heat_loss")));
+    const sc = healthStates();
+    sc[`${PFX}_plan_optimization_score`].attributes.reasons.overall = "heat_loss_learning";
+    const scoreRow = pageOf(mkHealth(sc).html());
+    check("UX-HEALTH D: the waiting score says its own sensor's reason",
+      /Optimization score<span class="adv-sub">Still learning the house&#39;s heat loss\.|Optimization score<span class="adv-sub">Still learning the house's heat loss\./.test(scoreRow),
+      scoreRow.slice(scoreRow.indexOf("Optimization score"), scoreRow.indexOf("Optimization score") + 120));
+
+    // Carry 14: the score's hover explains every sub-score's metric, not
+    // only the house's, beside each grade and its reason.
+    const sh = healthStates();
+    sh[`${PFX}_plan_optimization_score`] = { state: "62", last_updated: "t1", attributes: {
+      envelope: 55, machine: null, operation: 70, reasons: { machine: "cop_watch_learning" }, envelope_drivers: [] } };
+    const hv = mkHealth(sh);
+    hv.c.dialog.page = "plan";
+    hv.c._render();
+    const hoverHtml = hv.html();
+    const partsMissing = ["envelope", "machine", "operation"].filter((k) =>
+      !hoverHtml.includes(fn("STRINGS").en[`score.part_${k}`].replace(/&/g, "&amp;").replace(/"/g, "&quot;").slice(0, 40)));
+    check("UX-HEALTH F: the score hover explains every sub-score's metric",
+      partsMissing.length === 0, `missing ${partsMissing.join(",")}`);
+    const copRow = (cop) => rowOf(modelOf(modelStates({ cop })), "cop");
+    const young = copRow({ scale: 1.0, watched_buckets: 0, alarm: false });
+    check("UX-HEALTH E: an unwatched COP is a dash with the reason, never Normal",
+      !/Normal/.test(young) && /—/.test(young) && /Not enough COP data yet/.test(young), young);
+    for (const obs of ["not_measurable", "no_electric_meter"]) {
+      const r = copRow({ scale: 1.0, watched_buckets: 3, alarm: false, cop_observability: obs });
+      check(`UX-HEALTH E: ${obs} reads as such even with watched buckets, never Normal`,
+        !/Normal/.test(r) && r.includes(fn("STRINGS").en[`health.cop_reason_${obs}`].replace(/'/g, "&#39;").slice(0, 30))
+        || (!/Normal/.test(r) && r.includes(fn("STRINGS").en[`health.cop_reason_${obs}`].slice(0, 30))), r);
+    }
+    const span = copRow({ scale: 1.0, watched_buckets: 0, cop_refusal: "span_open" });
+    check("UX-HEALTH E: a refusal reads in words, not as its code",
+      /Waiting for the meter span to close/.test(span) && !/span_open/.test(span), span);
+    const odd = copRow({ scale: 1.0, watched_buckets: 0, cop_refusal: "zz_new_code" });
+    check("UX-HEALTH E: an unknown refusal code reads as not enough data, never raw",
+      /Not enough COP data yet/.test(odd) && !/zz_new_code/.test(odd), odd);
+    const both = copRow({ scale: 1.0, watched_buckets: 0, cop_observability: "awaiting_draw_evidence", cop_refusal: "duty_floor" });
+    check("UX-HEALTH E: the learner's own refusal is said before the gate's wait for draw evidence",
+      /ran too little/.test(both) && !/Waiting to see whether/.test(both), both);
+    const awaiting = copRow({ scale: 1.0, watched_buckets: 0, cop_observability: "awaiting_draw_evidence" });
+    check("UX-HEALTH E: with no refusal the gate's wait for draw evidence is said",
+      /Waiting to see whether the power draw follows the plan/.test(awaiting), awaiting);
+    const aged = copRow({ scale: 0.97, watched_buckets: 2, measured_cop_at: new Date(FROZEN - 2 * 3600e3).toISOString() });
+    check("UX-HEALTH E: the latched COP shows its age", /Measured 2 h ago/.test(aged), aged);
+    check("UX-HEALTH E: a watched COP still reads Normal (null control)",
+      /Normal \(COP scale 0\.97\)/.test(copRow({ scale: 0.97, watched_buckets: 2, alarm: false })));
+    const hm = copRow({ scale: 1.02, watched_buckets: 3, cop_observability: "heat_metered", cop_refusal: "span_open" });
+    check("UX-HEALTH E: a heat-metered COP with an open span stays Normal and names its meter (carry 11)",
+      /Normal \(COP scale 1\.02\)/.test(hm) && /Measured by the heat meter/.test(hm), hm);
+    const nm = modelStates({ cop: { scale: 1.0, watched_buckets: 3, cop_observability: "not_measurable" } });
+    const nmPage = pageOf(mkHealth(nm).html());
+    const learnCop = (/Heat pump COP<span class="adv-sub">([^<]*)</.exec(nmPage) || [])[1] || "";
+    check("UX-HEALTH E: the learning row says the same COP reason as the model row",
+      /^Not measurable here/.test(learnCop) && !/Needs a power meter/.test(nmPage), learnCop);
+    // Every code the COP gate and the heat counter publish has words in both
+    // languages; the count is asserted non-zero so a grep miss cannot pass.
+    const pySrc = ["accuracy.py", "heat_energy.py"].map((f) => fs.readFileSync(`custom_components/heatpump_optimizer/${f}`, "utf8")).join("\n");
+    const copCodes = [...pySrc.matchAll(/^(?:COP_(?:HEAT|DRAW|NOT|NO_ELECTRIC)[A-Z_]*|COP_REFUSED_[A-Z_]+|SPAN_REFUSED_[A-Z_]+) = "(\w+)"/gm)].map((m) => m[1]);
+    for (const lang of ["en", "sv"]) {
+      const missing = copCodes.filter((c) => !fn("STRINGS")[lang][`health.cop_reason_${c}`]);
+      check(`UX-HEALTH E: every published COP code has its own ${lang} words`,
+        copCodes.length > 0 && missing.length === 0, `${copCodes.length} codes; missing ${missing.join(",")}`);
+    }
+  }
+
+  // Items 4 and 7, and #2809/#2815: Show lands on this entry's entities;
+  // Download diagnostics saves the entry's file through the authenticated
+  // endpoint and falls back to the entry page; the debug collection row.
+  {
+    const ENTRY_ID = "01HEALTHENTRY";
+    const callWS = async (m) => ({ entity_id: m.entity_id, config_entry_id: ENTRY_ID });
+    const pressAct = async (h, act) => {
+      const b = h.c.shadowRoot.querySelector(`[data-act="${act}"]`);
+      if (b) await Promise.all((b._listeners.click || []).map((f) => f({ stopPropagation() {}, detail: 1 })));
+      return !!b;
+    };
+    const tick = () => new Promise((r) => setTimeout(r, 0));
+    const went = [];
+    const savedNav = ctx.navigateTo;
+    ctx.navigateTo = (p, d) => went.push([p, d]);
+    try {
+      const sh = mkHealth(healthStates());
+      sh.c.hass = { ...sh.c.hass, callWS };
+      await pressAct(sh, "show_entities");
+      await tick();
+      check("UX-HEALTH G: Show opens this entry's entity table, disabled entities included",
+        went.some(([p]) => p === fn("haLink")("entities", ENTRY_ID)), JSON.stringify(went));
+      const savedURL = ctx.URL, savedTimeout = ctx.setTimeout;
+      ctx.URL = { createObjectURL: () => "blob:hpo-diag", revokeObjectURL() {} };
+      ctx.setTimeout = () => 0;
+      try {
+        for (const [status, ok] of [[200, true], [403, false]]) {
+          went.length = 0;
+          const fetched = [];
+          const dg = mkHealth(healthStates());
+          dg.c.hass = { ...dg.c.hass, callWS,
+            fetchWithAuth: async (path) => { fetched.push(path); return { ok, status, blob: async () => "{}" }; } };
+          await pressAct(dg, "diagnostics");
+          await tick();
+          check(`UX-HEALTH G: Download diagnostics fetches the entry's endpoint (${status})`,
+            fetched[0] === `/api/diagnostics/config_entry/${ENTRY_ID}`, JSON.stringify(fetched));
+          check(ok ? "UX-HEALTH G: a 200 saves the file through navigateTo's download mode"
+            : "UX-HEALTH G: a refused fetch falls back to the entry page",
+          ok ? went.length === 1 && went[0][0] === "blob:hpo-diag" && /\.json$/.test(went[0][1] || "")
+            : went.length === 1 && went[0][0] === fn("haLink")("options", ENTRY_ID) && !went[0][1], JSON.stringify(went));
+        }
+      } finally {
+        if (savedURL === undefined) delete ctx.URL; else ctx.URL = savedURL;
+        ctx.setTimeout = savedTimeout;
+      }
+    } finally { ctx.navigateTo = savedNav; }
+    // navigateTo's download mode clicks an anchor and pushes no route.
+    {
+      const savedDoc = ctx.document, savedHist = ctx.history;
+      const pushed = [], made = [];
+      ctx.document = { createElement: (t) => { const a = { tag: t, click() { a.clicked = true; } }; made.push(a); return a; } };
+      ctx.history = { pushState: (_a, _b, p) => pushed.push(p) };
+      try { fn("navigateTo")("blob:x", "f.json"); } finally { ctx.document = savedDoc; ctx.history = savedHist; }
+      check("UX-HEALTH G: navigateTo's download mode saves through an anchor and pushes no route",
+        made.length === 1 && made[0].href === "blob:x" && made[0].download === "f.json" && made[0].clicked && pushed.length === 0,
+        JSON.stringify({ made, pushed }));
+    }
+
+    const FINAL = { active: false, final: true, rows: 40, bytes: 9000, started_at: new Date(FROZEN - 864e5).toISOString() };
+    const debugPage = async (answer) => {
+      const calls = [];
+      const h = mkHealth(healthStates());
+      h.c.hass = { ...h.c.hass, callWS,
+        callService: async (...a) => { calls.push(a); return typeof answer === "function" ? answer(a) : answer; } };
+      h.c._debugAt = 0;
+      h.c._render();
+      for (let i = 0; i < 4; i++) await tick();
+      return { h, calls, state: () => (/data-debug="(\w+)"/.exec(h.html()) || [])[1] };
+    };
+    const fin = await debugPage({ context: { id: "c" }, response: { debug: { [ENTRY_ID]: FINAL } } });
+    check("UX-HEALTH H: the collection status is asked of debug_collect with a response, for this entry",
+      fin.calls.some((a) => a[1] === "debug_collect" && a[2].action === "status" && a[2].entry_id === ENTRY_ID && a[5] === true),
+      JSON.stringify(fin.calls));
+    check("UX-HEALTH H: a finished collection reads finished with its records",
+      fin.state() === "final" && /Finished with 40 records/.test(fin.h.html()), fin.state());
+    const before = fin.calls.length;
+    await pressAct(fin.h, "debug_start");
+    check("UX-HEALTH H: the first Start on a finished collection only says it would discard it",
+      fin.calls.length === before && /discards the finished collection/.test(fin.h.html()));
+    await pressAct(fin.h, "debug_start");
+    check("UX-HEALTH H: the second Start starts it",
+      fin.calls.slice(before).some((a) => a[1] === "debug_collect" && a[2].action === "start"), JSON.stringify(fin.calls.slice(before)));
+    for (const [what, answer] of [["flat at the top level", { final: true, rows: 40 }],
+      ["without the response wrapper", { debug: { [ENTRY_ID]: FINAL } }],
+      ["keyed by another entry", { context: {}, response: { debug: { OTHER: FINAL } } }]]) {
+      check(`UX-HEALTH H: a status ${what} reads off, never finished`, (await debugPage(answer)).state() === "off");
+    }
+    const act = await debugPage({ response: { debug: { [ENTRY_ID]: { ...FINAL, active: true, final: false } } } });
+    check("UX-HEALTH H: an active collection shows no Start",
+      act.state() === "active" && !/data-act="debug_start"/.test(act.h.html()));
+  }
+
+  // P08/P41: a place the Setup page names is labelled through placeLabel,
+  // and an id it has no label for stays as itself rather than going blank.
+  check("placeLabel names a known place and keeps an unknown id as itself",
+    fn("placeLabel")("wood_tank") === fn("STRINGS").en["places.wood_tank"] && fn("placeLabel")("garage_loop") === "garage_loop",
+    `${fn("placeLabel")("wood_tank")} / ${fn("placeLabel")("garage_loop")}`);
+
   // The other four tabs still render.
   for (const [page_, marker] of [["plan", /stat-row|tile/], ["setup", /setup-page/],
     ["savings", /savings/i], ["advisor", /advisor-page/]]) {
@@ -12183,15 +12452,13 @@ check("without an indoor reading the corner now label is absent",
 {
   const ENTRY = "01JDEEPLINKENTRY";
   const BARE = "/config/integrations/integration/heatpump_optimizer";
-  const PENDING = {
-    "health:settings": { group: "R10-UX-HEALTH", path: BARE },
-    "health:diagnostics": { group: "R10-UX-HEALTH", path: BARE },
-  };
+  const PENDING = {};
   const haLink = fn("haLink");
   const BIN = "binary_sensor.heat_pump_optimizer_input_problem";
   // Every `act` branch the card's source can dispatch, by name.
   const ACTS = ["assign", "apply_dhw", "apply_valve", "try_degree", "adopt_refit",
-    "restore_snapshot", "settings", "open_options", "dismiss_feedback", "diagnostics", "add", "remove"];
+    "restore_snapshot", "show_entities", "open_options", "dismiss_feedback", "diagnostics", "debug_start",
+    "add", "remove"];
   const srcActs = [...new Set([...cardSrc.matchAll(/\bact\s*===\s*"([a-z_]+)"/g)].map((m) => m[1])
     .concat([...cardSrc.matchAll(/data-act="([a-z_]+)"/g)].map((m) => m[1])))].sort();
   const sourceOnly = srcActs.filter((a) => !ACTS.includes(a));
@@ -12681,6 +12948,12 @@ check("without an indoor reading the corner now label is absent",
           { key: "outdoor_temp_entity", label: "Outdoor temperature",
             priced: false, reason: "weather_backed" }] };
       } },
+    // R10-UX-HEALTH H: the debug collection row finished (its Start arms a
+    // confirm) and off (its Start starts).
+    { name: "health+debug_final", page: "health", prep: (c) => {
+      c._debug = { active: false, final: true, rows: 40, bytes: 9000, started_at: null };
+      c._debugAt = Date.now(); c._render(); } },
+    { name: "health+debug_off", page: "health", prep: (c) => { c._debug = null; c._debugAt = Date.now(); c._render(); } },
     { name: "setup+picker", page: "setup", prep: (c) => press(c, ".setup-hit") },
     { name: "setup+layout", page: "setup", prep: (c) => press(c, ".layout-edit-toggle") },
     { name: "editor", make: () => {
diff --git a/tests/card_browser.mjs b/tests/card_browser.mjs
index bd3768261..958876ccb 100644
--- a/tests/card_browser.mjs
+++ b/tests/card_browser.mjs
@@ -513,6 +513,77 @@ function healthPageStates(st, now) {
   };
 }
 
+/** R10-UX-HEALTH items 2 and 3, measured at a phone's width and a desktop's,
+ * in both themes: the input rows span the page in a grid, and the Health
+ * page's first row is not drawn under the dialog's head -- on open, and
+ * again after a page switch from a scrolled page. "Under" is read by
+ * hit-testing the row's own top edge: whatever the browser paints there must
+ * be the row. */
+async function healthLayout({ browser, check, plan }) {
+  const FROZEN = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * HOUR;
+  const states = healthPageStates(pageStates(plan), FROZEN);
+  for (const theme of ["light", "dark"]) {
+    for (const width of [375, 1280]) {
+      const ctx = await browser.newContext({ viewport: { width, height: 800 }, deviceScaleFactor: 1,
+        colorScheme: theme, reducedMotion: "reduce" });
+      await ctx.clock.setFixedTime(FROZEN);
+      const page = await ctx.newPage();
+      try {
+        await page.goto("about:blank");
+        await page.addScriptTag({ path: CARD_SRC });
+        await page.evaluate(([themeCss, st, dark]) => {
+          const style = document.createElement("style");
+          style.textContent = `html{${themeCss};background:var(--primary-background-color)}` +
+            `body{margin:0;font-family:"Liberation Sans",Arial,sans-serif;color:var(--primary-text-color)}` +
+            `heatpump-optimizer-card{display:block}`;
+          document.head.appendChild(style);
+          const card = document.createElement("heatpump-optimizer-card");
+          document.body.appendChild(card);
+          card.setConfig({ type: "custom:heatpump-optimizer-card" });
+          card.hass = { states: st, language: "en", themes: { darkMode: dark } };
+          card._onCardClick({});
+          card.dialog.page = "health";
+          card._render();
+          window.__card = card;
+        }, [THEMES[theme], states, theme === "dark"]);
+        await page.waitForTimeout(150);
+        const measure = () => page.evaluate(() => {
+          const r = window.__card.shadowRoot;
+          const hp = r.querySelector("dialog[open] .health-page");
+          const first = hp && hp.querySelector(".health-row");
+          if (!first) return null;
+          const fr = first.getBoundingClientRect();
+          const hit = r.elementFromPoint(fr.left + fr.width / 2, fr.top + 2);
+          const grid = hp.querySelector(".health-inputs");
+          const rows = grid ? [...grid.querySelectorAll("[data-health-input]")].map((n) => n.getBoundingClientRect()) : [];
+          return { clear: !!hit && (hit === first || first.contains(hit)), hit: hit ? `${hit.tagName}.${hit.className}` : "none",
+            top: Math.round(fr.top), share: grid ? grid.getBoundingClientRect().width / hp.getBoundingClientRect().width : 0,
+            perLine: rows.filter((b) => Math.abs(b.top - (rows[0] || b).top) < 1).length };
+        });
+        const opened = await measure();
+        // Press the Plan tab, scroll its body, and press Health again: the
+        // route a user takes, through the tabs' own handler.
+        const tab = (id) => page.evaluate((id) => window.__card.shadowRoot.querySelector(`dialog[open] .dlg-tab[data-page="${id}"]`).click(), id);
+        await tab("plan");
+        await page.evaluate(() => { window.__card.shadowRoot.querySelector("dialog[open] .dlg-body").scrollTop = 400; });
+        await tab("health");
+        await page.waitForTimeout(150);
+        const back = await measure();
+        const tag = `${theme} ${width}px`;
+        check(`UX-HEALTH C: the Health page's first row is not under the dialog head on open (${tag})`,
+          !!opened && opened.clear, JSON.stringify(opened));
+        check(`UX-HEALTH C: nor after a switch back from a scrolled page (${tag})`, !!back && back.clear, JSON.stringify(back));
+        if (width >= 1280) {
+          check(`UX-HEALTH B: the input grid spans the page, several rows to a line (${tag})`,
+            !!opened && opened.share >= 0.9 && opened.perLine >= 2, JSON.stringify(opened));
+        }
+      } finally {
+        await ctx.close();
+      }
+    }
+  }
+}
+
 async function cardPages({ browser, check, plan, out }) {
   const FROZEN = Date.parse(plan.dhw_plan.forecast[0].t) + 6 * HOUR;
   const states = pageStates(plan);
@@ -2673,6 +2744,7 @@ try {
   // plan's and the chart has a past and a future. Written only under
   // HPO_PAGES_OUT; checked always.
   await cardPages({ browser, check, plan, out: process.env.HPO_PAGES_OUT });
+  await healthLayout({ browser, check, plan });
 
   // R9-UI-3 review (theme-contrast): Home Assistant reports
   // hass.themes.darkMode false for any theme without a dark mode, so a
diff --git a/tests/closures.json b/tests/closures.json
index 9828d4baf..097789898 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -580,11 +580,13 @@
    "custom_components/heatpump_optimizer/silent_mode.py",
    "custom_components/heatpump_optimizer/snapshots.py",
    "custom_components/heatpump_optimizer/store.py",
+   "custom_components/heatpump_optimizer/strings.json",
    "custom_components/heatpump_optimizer/sysid.py",
    "custom_components/heatpump_optimizer/tariff.py",
    "custom_components/heatpump_optimizer/thermal_model.py",
    "custom_components/heatpump_optimizer/topology.py",
    "custom_components/heatpump_optimizer/translations/en.json",
+   "custom_components/heatpump_optimizer/translations/sv.json",
    "custom_components/heatpump_optimizer/wear.py",
    "custom_components/heatpump_optimizer/wood_fuel.py",
    "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js",
@@ -3632,6 +3634,7 @@
    "tools/audit/seat/prune_refs.py",
    "tools/audit/seat/pulse.py",
    "tools/audit/seat/queue_pre_flight.py",
+   "tools/audit/seat/r10_deeplink_mutants.py",
    "tools/audit/seat/r10_ledger_mutants.py",
    "tools/audit/seat/r10_roster_ops_mutants.py",
    "tools/audit/seat/r10_roster_sync_mutants.py",
diff --git a/tests/entities.py b/tests/entities.py
index fec657d42..d268d8839 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -40112,4 +40112,71 @@ R.check(
 )
 
 
+# R10-UX-HEALTH arm A, the backend end: every key an InputReader read takes --
+# the keys the Input Problem sensor's `input_ages_minutes` and `problems`
+# publish, which the card labels from `health.input_<key>` -- is an entity
+# field of the options flow, so the card's table (held equal to strings.json
+# by tests/card.mjs) names every input the backend can report. The keys are
+# enumerated at the call sites: a `CONF_*` name, or a `for key in <tuple>`
+# over `CONF_*` names; any other argument is listed, so a read keyed some
+# third way refuses rather than going unseen.
+_UXH_PKG = Path("custom_components/heatpump_optimizer")
+_UXH_CONST = {
+    (n.target if isinstance(n, ast.AnnAssign) else n.targets[0]).id: n.value.value
+    for n in ast.parse((_UXH_PKG / "const.py").read_text()).body
+    if (isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)
+        or isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name))
+    and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str)
+}
+_UXH_READS = {"read", "read_state", "read_bool", "read_power_kw", "read_flow_kg_s"}
+_uxh_keys: set[str] = set()
+_uxh_odd: list[str] = []
+for _uxh_f in sorted(_UXH_PKG.glob("*.py")):
+    _uxh_tree = ast.parse(_uxh_f.read_text())
+    _uxh_tuples = {
+        n.targets[0].id: [e.id for e in n.value.elts if isinstance(e, ast.Name)]
+        for n in ast.walk(_uxh_tree)
+        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
+        and isinstance(n.value, ast.Tuple)
+    }
+    _uxh_loops = {
+        g.target.id: g.iter.id for g in ast.walk(_uxh_tree)
+        if isinstance(g, (ast.comprehension, ast.For)) and isinstance(g.target, ast.Name) and isinstance(g.iter, ast.Name)
+    }
+    for _uxh_c in ast.walk(_uxh_tree):
+        if not (isinstance(_uxh_c, ast.Call) and isinstance(_uxh_c.func, ast.Attribute)
+                and _uxh_c.func.attr in _UXH_READS and _uxh_c.args):
+            continue
+        _uxh_arg = _uxh_c.args[0]
+        # `const.CONF_X` is the name `CONF_X`; any other shape is listed.
+        _uxh_a = _uxh_arg.attr if isinstance(_uxh_arg, ast.Attribute) else getattr(_uxh_arg, "id", ast.dump(_uxh_arg))
+        # InputReader's own methods hand their `key` on, and a module's `read`
+        # handed the reader itself reads inside that module: both are
+        # enumerated at their own call sites.
+        if (_uxh_f.name == "inputs.py" and _uxh_a == "key") or _uxh_a == "reader":
+            continue
+        _uxh_names = [_uxh_a] if _uxh_a.startswith("CONF_") else _uxh_tuples.get(_uxh_loops.get(_uxh_a, ""), [])
+        if not _uxh_names or any(n not in _UXH_CONST for n in _uxh_names):
+            _uxh_odd.append(f"{_uxh_f.name}:{_uxh_c.lineno} {_uxh_a}")
+        _uxh_keys.update(_UXH_CONST[n] for n in _uxh_names if n in _UXH_CONST)
+_UXH_FIELDS: set[str] = set()
+
+
+def _uxh_walk(node: object) -> None:
+    if isinstance(node, dict):
+        for k, v in node.items():
+            if k == "data" and isinstance(v, dict):
+                _UXH_FIELDS.update(f for f in v if f.endswith("_entity"))
+            _uxh_walk(v)
+
+
+_uxh_walk(json.loads((_UXH_PKG / "strings.json").read_text())["options"])
+R.check(
+    "every InputReader key is an options-flow entity field, so the Health card has its label",
+    len(_uxh_keys) >= 20 and not _uxh_odd and _uxh_keys <= _UXH_FIELDS,
+    f"{len(_uxh_keys)} keys; not options fields: {sorted(_uxh_keys - _UXH_FIELDS)}; "
+    f"reads keyed some other way: {_uxh_odd}",
+)
+
+
 sys.exit(R.close("ENTITY CHECKS"))
diff --git a/tests/golden/card_claimed_drift.txt b/tests/golden/card_claimed_drift.txt
index 1f470c06e..cb6f35e23 100644
--- a/tests/golden/card_claimed_drift.txt
+++ b/tests/golden/card_claimed_drift.txt
@@ -781,3 +781,18 @@
 # parenthetical follow the fixture's own scores. The other 44 states were
 # rendered and stayed identical.
 score_open  # R10-HOUSE-GRADE (#2816): the House row's explanation rewritten and its driver line added
+
+# R10-UX-HEALTH (#2253, #2260, #2263, #2809, #2815; owner report 2026-10-14):
+# the Health page is re-laid and re-worded. Its plan and learning blocks move
+# above the inputs, which become their own grid under a page-scoped style
+# (HEALTH_CSS, so the card's shared stylesheet does not move); each input row
+# carries the options flow's role label; the COP rows read one copState; each
+# model row gains a hover naming its figure; the diagnostics copy and the
+# insight row's Show change; a debug collection row is added. health_page is
+# the one state that renders that page. score_open moves because the
+# headline score's hover now names every sub-score's metric in plain words,
+# not only the house's when it has drivers (the owner's hover spec, carry 14);
+# it is the state that renders the score with its hover. The other 43 states
+# were rendered and stayed identical.
+health_page  # R10-UX-HEALTH: the Health page's layout, labels, COP and learner rows, copy and debug row
+score_open  # R10-UX-HEALTH: the score hover names each sub-score's metric
diff --git a/tools/audit/seat/r10_deeplink_mutants.py b/tools/audit/seat/r10_deeplink_mutants.py
index 9704fe1d4..2aaa3b4b0 100644
--- a/tools/audit/seat/r10_deeplink_mutants.py
+++ b/tools/audit/seat/r10_deeplink_mutants.py
@@ -121,7 +121,9 @@ import sys
 CARD = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
 TEST = "tests/card.mjs"
 P = "/config/integrations/integration/heatpump_optimizer"
-NAV = '        navigateTo(SETTINGS_PATH);\n        return;\n      } else if (act === "apply_valve")'
+# A navigation in a pressed act branch: the Health page's Show, which R10-UX-HEALTH
+# converted from the bare `navigateTo(SETTINGS_PATH)` this anchor first named.
+NAV = '        openHaLink(host, "entities", null);\n        return;\n      } else if (act === "diagnostics")'
 DIAG = '<button type="button" class="adv-act" data-act="diagnostics">'
 LOOP = '  for (const btn of root.querySelectorAll(".adv-act")) {\n    btn.addEventListener("click", async (ev) => {'
 DISMISS = "        dismissFeedback();\n        host._render();\n        return;"
@@ -131,7 +133,7 @@ RUNTIME_MORE_INFO = '["hass", "more", "info"].join("-")'
 
 
 def after_nav(stmt):
-    return [(CARD, NAV, NAV.replace("navigateTo(SETTINGS_PATH);", "navigateTo(SETTINGS_PATH); " + stmt))]
+    return [(CARD, NAV, NAV.replace('openHaLink(host, "entities", null);', 'openHaLink(host, "entities", null); ' + stmt))]
 
 
 def attach(sel, stmt):
@@ -355,11 +357,11 @@ PLANTS = {
     "M5_openPicker_no_focus": card("    this.pickerFocus = !!viaKeyboard;", "    this.pickerFocus = false;"),
     "M6_convert_advisor_settings": card("        navigateTo(SETTINGS_PATH);", '        await openHaLink(host, "options");'),
     # Rounds 1-3 (review) and the fixer's variants.
-    "R4_entry_ignored": card("    entryId = (reg && reg.config_entry_id) || null;", "    entryId = null;"),
+    "R4_entry_ignored": card("    return (reg && reg.config_entry_id) || null;", "    return null;"),
     "R5_anchor_href": card(DIAG, f'<a href="{P}">open</a>' + DIAG),
-    "R6_more_info_instead_of_nav": card("        navigateTo(SETTINGS_PATH);", "        " + EVENT % '"hass-more-info"'),
-    "R6b_pending_nav_plus_event": card("        navigateTo(SETTINGS_PATH);",
-                                       "        navigateTo(SETTINGS_PATH); " + EVENT % RUNTIME_MORE_INFO),
+    "R6_more_info_instead_of_nav": card('        openHaLink(host, "entities", null);', "        " + EVENT % '"hass-more-info"'),
+    "R6b_pending_nav_plus_event": card('        openHaLink(host, "entities", null);',
+                                       '        openHaLink(host, "entities", null); ' + EVENT % RUNTIME_MORE_INFO),
     "R6c_assign_fires_event": card("        openSetupSlot(host, btn.dataset.key, ev);", "        " + EVENT % RUNTIME_MORE_INFO),
     "R7b_setAttribute_unresolved": attach("a.zz", f'a.setAttribute("href", "{P}");'),
     "R7c_setAttribute_runtime_name": attach(".zz", f'a.setAttribute(["hr", "ef"].join(""), "{P}");'),

