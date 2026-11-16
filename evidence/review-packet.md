# Review packet #3663
head: 54fd5072b6b165c4bd3eab3900e5009332132d6a
base: 367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arch-score / arch-score id=133439461099 in_progress
budget-raise-gate / budget-raise-gate id=133439461134 success
cancel-superseded id=133437451141 queued
codeql / Analyze (actions) id=133439461082 queued
codeql / Analyze (javascript-typescript) id=133439461202 queued
codeql / Analyze (python) id=133439461284 queued
governance / env-matrix id=133439460968 queued
governance / instrument-self-tests id=133439461001 queued
governance / policy-docs id=133439460975 queued
governance / record id=133439464409 skipped
governance / wave-script id=133439460916 queued
hassfest / hassfest id=133439460736 queued
kernel-points id=133439463664 skipped
prelude id=133437451130 queued
refresh id=133437451177 queued
tests / arch-instrument id=133441564015 queued
tests / briefs id=133439460996 success
tests / browser id=133441564490 queued
tests / closure-scope id=133439460967 success
tests / closures id=133441563982 queued
tests / coverage id=133441563874 queued
tests / fast (3.14) id=133441564063 queued
tests / mutation id=133439461262 success
tests / mutation-autofix id=133441833163 skipped
tests / mutation-pins id=133441831305 skipped
tests / nightly-ha id=133441566755 skipped
tests / nightly-status id=133439461026 queued
tests / replay id=133441566428 skipped
tests / typing id=133441563959 queued
validate / validate-hacs id=133439461214 queued

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 133439461001: queued has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: FULL -- every test script runs, nothing is scoped out.
             no segment of this names a program this check knows
  ok         python3 dev/audit/harnesses/vendor_text_census.py --counts
             `dev/audit/harnesses/vendor_text_census.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/vendor_text_census.py
             `dev/audit/harnesses/vendor_text_census.py` is in the tree at this head
  ok         python3 -I tools/audit/check_scopes.py --self-test --repo .
             `tools/audit/check_scopes.py` is in the tree at this head
  ok         node tools/policy/policy_lint_mutants.mjs
             `tools/policy/policy_lint_mutants.mjs` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs --self-test
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tests/closure.py
             `tests/closure.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/features.py
             `tests/features.py` is in the tree at this head
  ok         tests/golden.py
             `tests/golden.py` is in the tree at this head
  ok         tests/config_flow_steps.py
             `tests/config_flow_steps.py` is in the tree at this head
  ok         tests/deployment_shape.py
             `tests/deployment_shape.py` is in the tree at this head
  ok         tests/arch_score_head.py
             `tests/arch_score_head.py` is in the tree at this head
  ok         node tests/md_tables.mjs
             `tests/md_tables.mjs` is in the tree at this head
  ok         node tests/card.mjs
             `tests/card.mjs` is in the tree at this head
  ok         node tests/card_drift.mjs
             `tests/card_drift.mjs` is in the tree at this head
  ok         tests/plan_view.py
             `tests/plan_view.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only b3831ff64e
             `tests/env_drift.py` is in the tree at this head
  ok         tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tools/audit/text_ledger.py --self-test
             `tools/audit/text_ledger.py` is in the tree at this head
  ok         tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  ok         dev/audit/rounds/round4/D6/claims.py
             `dev/audit/rounds/round4/D6/claims.py` is in the tree at this head

FIGURES: 24 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (no verdict on verdict/<pr> names the reviewed head c00ad6ba0a26431fd07cfa89e30aa025063fb947, so there is no finding to confirm resolved)

## Three-dot diff
diff --git a/README.md b/README.md
index 30dab25208..4ca4c9066b 100644
--- a/README.md
+++ b/README.md
@@ -61,8 +61,9 @@ and a cool-only heat-curve correction are all estimated
 from your own house. Every learner is snapshotted weekly (the last eight are
 kept), and a drift watchdog can roll them back to the last healthy snapshot.
 
-**Knows what your electricity actually costs.** Tibber spot prices, time-of-use
-grid transfer fees, the monthly capacity (*effekt*) tariff and its billing clock,
+**Knows what your electricity actually costs.** Spot prices from Tibber or a
+price sensor, time-of-use grid transfer fees, the monthly capacity (*effekt*)
+tariff and its billing clock,
 PV self-consumption priced at what consuming actually costs you, and a learned
 diurnal price prior for the part of the horizon that has not been published yet.
 A live peak guard and a main-fuse headroom advisor act inside the metering window
@@ -128,7 +129,7 @@ or history. Monetary units follow your instance currency.
 ```mermaid
 flowchart LR
     subgraph inputs["Inputs"]
-        tibber["Tibber API<br/>hourly prices"]
+        tibber["Tibber API or a price sensor<br/>hourly prices"]
         weather["HA weather entity<br/>temperature, wind,<br/>rain, irradiance"]
         meteo["Open-Meteo<br/>optional irradiance"]
         ha["Your HA sensors<br/>temps, power, presence"]
@@ -150,7 +151,7 @@ flowchart LR
     subgraph out["Outputs"]
         ent["Entities<br/>sensors, binary sensors,<br/>buttons, switches,<br/>climate, datetime"]
         card["Dashboard card<br/>plan chart + editor"]
-        ctl["Heat pump switch /<br/>ECL110 displace /<br/>frequency advisor"]
+        ctl["Heat pump switch /<br/>heat-curve displace /<br/>frequency advisor"]
     end
 
     tibber --> pm
@@ -240,9 +241,9 @@ act on" — pricing and planning without actuating anything.
 | Control path | You provide | The optimizer writes |
 |---|---|---|
 | **On/off switch** | a `switch` that turns the heat pump on and off | may turn it off during expensive hours |
-| **ECL110 heat curve** | a Danfoss ECL110-compatible weather-compensated controller, reachable over MQTT | a heat-pump on/off decision and an integer parallel shift (*displace*) onto the controller's own heat curve |
-| **Heat-curve offset entity** | a controller whose volatile whole-curve offset is a `number` entity (for example a Luxtronik SHI heating offset) | the same displace as a temperature difference via `number.set_value`, bounded to ±3 K by default; 0 again when the optimizer is turned off or unloaded |
-| **Heat-curve stored parameter** | a controller with no volatile offset, whose stored curve setting is a `number` entity (kind *persistent*) | its value before the first write plus the displace, within ±3 K and at most 12 writes a day by default; that value written back when the optimizer is turned off or unloaded |
+| **Heat curve, over MQTT** | a weather-compensated controller that takes its curve offset over MQTT (for example a Danfoss ECL110 through an MQTT bridge) | a heat-pump on/off decision and an integer parallel shift (*displace*) onto the controller's own heat curve |
+| **Heat curve, offset entity** | a controller whose volatile whole-curve offset is a `number` entity (for example a Luxtronik SHI heating offset) | the same displace as a temperature difference via `number.set_value`, bounded to ±3 K by default; 0 again when the optimizer is turned off or unloaded |
+| **Heat curve, stored parameter** | a controller with no volatile offset, whose stored curve setting is a `number` entity (kind *persistent*) | its value before the first write plus the displace, within ±3 K and at most 12 writes a day by default; that value written back when the optimizer is turned off or unloaded |
 | **Compressor frequency** | the compressor frequency exposed as a `number` entity (typically from Modbus or ESPHome) | the recommended frequency via `number.set_value` — but only once you switch the mode to Control |
 
 The boundaries of each path — what it can reach and what it cannot — are
@@ -252,8 +253,9 @@ limitations that apply to the integration as a whole.
 Each path in full: [Switch and climate entity](#switches-climate-and-datetime-entities),
 [Inverter frequency: observe first, control if you say
 so](#inverter-frequency-observe-first-control-if-you-say-so),
-[ECL110 heat-curve control](#ecl110-heat-curve-control); the setup fields for
-all three live in [docs/configuration.md](./docs/configuration.md).
+[Heat-curve control](#heat-curve-control) (three ways: MQTT topics, an offset
+entity, a stored curve parameter); the setup fields for all three paths live
+in [docs/configuration.md](./docs/configuration.md).
 
 ## Known limitations
 
@@ -272,16 +274,17 @@ installing rather than discover it after:
   broadest path — any on/off `switch` will do, and the only one of the three
   that needs nothing from the pump's electronics — but any control finer than
   on-and-off needs one of the other paths.
-- **ECL110 control is MQTT-only; other controllers need an offset entity.** The
-  ECL110 path is for installs that have such a controller on MQTT, and
-  publishing goes through Home Assistant's own `mqtt.publish` service, "so the
-  MQTT integration has to be set up". The two command topics ship empty, so an
-  install without an ECL110 has nothing to clear on the options page. Without
-  MQTT, the displace reaches only a controller whose heat-curve offset is a
-  volatile `number` entity, 0 neutral; an absolute or stored curve parameter
-  is not supported in this version. Details in
-  [ECL110 heat-curve control](#ecl110-heat-curve-control) and
-  [docs/ecl110.md](./docs/ecl110.md).
+- **Heat-curve control needs MQTT or a `number` entity on your controller.**
+  Over MQTT, publishing goes through Home Assistant's own `mqtt.publish`
+  service, "so the MQTT integration has to be set up"; the two command topics
+  ship empty, so an install whose controller takes nothing over MQTT has
+  nothing to clear on the options page. Without MQTT, the displace reaches a
+  controller only through a `number` entity: a volatile offset, 0 neutral, or
+  a curve setting the controller stores, which wears its memory and is capped
+  at a few writes a day. An absolute curve point (an entity whose range
+  excludes 0) is refused as an offset. Details in
+  [Heat-curve control](#heat-curve-control) and
+  [docs/heat-curve.md](./docs/heat-curve.md).
 - **Frequency control needs a `number` entity and your explicit say-so.** The
   path exists only if the compressor frequency is exposed as a `number`
   entity (Modbus, ESPHome). The default Observe mode "learns and recommends
@@ -369,7 +372,7 @@ and every one of its entities and stops every command to the heat pump. Three
 things are left behind on purpose, because deleting them is your call:
 
 - **The heat pump keeps its last command.** The last setpoint the optimizer
-  wrote to your thermostat, or the last ECL110 displacement it published, stays
+  wrote to your thermostat, or the last heat-curve displacement it published over MQTT, stays
   in force until you set the pump's own controls back. Nothing else is restored on
   removal: a heat-curve entity is the one exception, written back when the
   integration unloads (0 for an offset, the value it held before the first
@@ -652,8 +655,8 @@ every sensor is created on every install regardless of which group it is in.
 |---|---|---|---|
 | Prediction Accuracy | °C | Mean indoor-temperature error, with the signed bias and the last diagnosis in attributes | Diagnostic; unavailable until an interval has been scored |
 | Learning Comfort Weight | — | The comfort weight in force, learned or configured | Diagnostic |
-| ECL110 Displace | °C | The parallel shift commanded to an ECL110 heat curve | Diagnostic; disabled by default unless an ECL110 MQTT topic is configured at setup; unavailable without one |
-| ECL110 Effective Displace | °C | The shift the controller has actually reached, after its own lag | Diagnostic; disabled by default unless an ECL110 MQTT topic is configured at setup; unavailable without one |
+| Heat-Curve Displace | °C | The parallel shift commanded to the controller's heat curve, over MQTT or to the heat-curve entity | Diagnostic; disabled by default unless a heat-curve MQTT topic or entity is configured at setup; unavailable without one |
+| Heat-Curve Effective Displace | °C | The shift the controller has actually reached, after its own lag | Diagnostic; disabled by default unless a heat-curve MQTT topic or entity is configured at setup; unavailable without one |
 | Valve Target Recommendation | °C | What to set a manual mixing valve to, and why | Diagnostic; disabled by default and unavailable until a throttling mixing-valve mode is configured (manual, smart read or smart write) — a valve-less install gets neither a hidden sensor nor one stuck at unknown |
 | Sensor-Gap Advisor | CUR | Estimated extra cost per month, in your currency, from the highest-value empty sensor slot | Diagnostic; outdoor, house meter, DHW probe |
 | Wood-Burn Night Advisor | — | 48 h light/skip advice when the wood furnace is on | Diagnostic; disabled by default; advisory only — never lights the stove |
@@ -662,7 +665,8 @@ every sensor is created on every install regardless of which group it is in.
 Disabled by default: Buffer Tank Temperature, Compressor Frequency
 Advisor, Compressor Starts, Cost Contract Comparison, Cost Monthly Peak Power,
 Cost Power Headroom, DHW Heavy Day Demand, DHW Mixed Water, DHW Temperature,
-ECL110 Displace, ECL110 Effective Displace, Floor Heating Return Temperature,
+Floor Heating Return Temperature, Heat-Curve Displace, Heat-Curve Effective
+Displace,
 Lower Floor Temperature, Measured Power, Slab Temperature (Estimated), Solar
 Surplus Forecast, Upper Floor Temperature, Valve Target Recommendation,
 Wood-Burn Night Advisor and Wood Cheaper Than Heat Pump.
@@ -849,7 +853,7 @@ hard-coded to the entity ids the examples assume.
 sequenceDiagram
     autonumber
     participant C as Coordinator
-    participant P as Prices (Tibber + learned prior)
+    participant P as Prices (Tibber or a price sensor, + learned prior)
     participant W as Weather entity (HA)
     participant S as Your sensors
     participant M as Thermal model
@@ -868,7 +872,7 @@ sequenceDiagram
     O->>O: solve: minimize cost + comfort penalty<br/>subject to comfort floor, tank limits,<br/>legionella clock, fuse and peak caps
     O-->>C: space + DHW slot plan
     C->>C: apply manual-plan pins,<br/>safety releases pinned-off slots
-    C->>E: publish plan sensors, switch the heat pump,<br/>ECL110 displace / frequency advice
+    C->>E: publish plan sensors, switch the heat pump,<br/>heat-curve displace / frequency advice
     Note over C: between plans the peak guard folds power-meter events<br/>and flips a flag (2 agree to engage, 2 to clear).<br/>It never solves — the next solve only reads the flag
     Note over M: afterwards: compare prediction against reality,<br/>nudge the learned parameters
 ```
@@ -1082,16 +1086,30 @@ Each clears itself once the cause is gone.
 - **Silent windows are not enforced** — the capacity-limited slot is not a switch the integration can hold. Assign the pump's own night-mode switch, or remove the silent windows.
 - **The heat pump cannot hold the hot water minimum** — You named a *Hot water start hysteresis* entity, and the hot water minimum sits above the temperature the pump starts a charge at (its hot water target less that hysteresis). The plan places no charge the pump would not start, so it shows the tank falling under the minimum before each charge. Lower the minimum to the start temperature or less, raise the hot water set-point, or reduce the hysteresis on the pump.
 
-## ECL110 heat-curve control
+## Heat-curve control
 
-The integration can drive a Danfoss ECL110-compatible controller over MQTT,
-publishing a heat-pump on/off decision and an integer parallel shift (*displace*)
-onto the controller's own heat curve. The ECL110 settings live only
-on the **Heat curve control** options page, not in initial setup, and
-both ECL110 sensors are disabled by default. The MQTT topics ship empty;
-nothing is published or subscribed until you set a topic, so an install without
-an ECL110 never touches the topics at all. Topics, payloads, options and the
-PI/PID lag handling are documented in [docs/ecl110.md](./docs/ecl110.md).
+<a id="ecl110-heat-curve-control"></a>
+
+The integration can shift a weather-compensated controller's own heat curve:
+up in cheap hours, down in expensive ones, as an integer parallel shift
+(*displace*). It reaches the controller one of three ways:
+
+- **Over MQTT**, to a controller that takes its offset there — for example a
+  Danfoss ECL110 through the strutsfarm/ecl110 bridge — with a heat-pump
+  on/off decision beside the displace;
+- **to an offset entity**, a volatile whole-curve offset Home Assistant
+  exposes as a `number` (for example a Luxtronik SHI heating offset), written
+  back to 0 when the optimizer is turned off or unloaded;
+- **to a stored curve parameter**, a `number` the controller keeps in memory,
+  displaced from its own value at most a few times a day and written back on
+  off.
+
+The settings live only on the **Heat curve control** options page, not in
+initial setup, and both heat-curve sensors are disabled by default. The MQTT
+topics ship empty; nothing is published or subscribed until you set a topic,
+so an install whose controller takes nothing over MQTT never touches the
+topics at all. The three ways, their options, payloads and the PI/PID lag
+handling are documented in [docs/heat-curve.md](./docs/heat-curve.md).
 
 ## Project status
 
@@ -1155,7 +1173,7 @@ before installing; it applies with full force.
 | [docs/dashboard-card.md](./docs/dashboard-card.md) | The card: options, interactions, editing limits |
 | [docs/automations.md](./docs/automations.md) | Complete automation examples using only the entities and services the integration creates |
 | [docs/architecture.md](./docs/architecture.md) | Module map and how a plan is made, for anyone reading or changing the code |
-| [docs/ecl110.md](./docs/ecl110.md) | ECL110 MQTT control |
+| [docs/heat-curve.md](./docs/heat-curve.md) | Heat-curve control, three ways: MQTT topics (for example a Danfoss ECL110), an offset entity, a stored curve parameter |
 | [DISCLAIMER.md](./DISCLAIMER.md) | The full disclaimer |
 
 ## Disclaimer
diff --git a/custom_components/heatpump_optimizer/strings.json b/custom_components/heatpump_optimizer/strings.json
index a0f688cfbe..4bc15c7641 100644
--- a/custom_components/heatpump_optimizer/strings.json
+++ b/custom_components/heatpump_optimizer/strings.json
@@ -593,12 +593,12 @@
               "indoor_temp_entity": "Optional. The actual room temperature. Without it the optimizer trusts its own model, which drifts over time.",
               "outdoor_temp_entity": "Optional. A local outdoor thermometer is more accurate than the forecast for the current hour.",
               "space_setpoint_entity": "Optional. A number, helper or climate entity that is the pump's space-heating set-point. With Pump duty control at Control the optimizer writes it on every plan step, as Pump duty control describes, and turning Optimizer active off writes back the value it read before its first write. With Pump duty control at Off or Observe it is only read, to notice when it cannot be read.",
-              "space_setpoint_unit": "Indoor temperature is correct for a room or thermostat set-point. Flow temperature is for a controller whose set-point is a water temperature it holds its supply at. Return temperature is for a controller that takes the set-point as its return-water target (assumed for a Luxtronik through its Smart Home Interface); it is written like a flow set-point, with the rated hold, the weather curve and the 25 °C gate moved 5 K down to return terms. A version before this option reads Return temperature as Indoor temperature: switch it back to Flow temperature before downgrading. Pointing an indoor target at a flow entity would command roughly 21 °C to something expecting 35–45 °C and badly underheat the house. The unit is a declaration: the optimizer never infers it from the entity, and only the heat-pump pre-fill suggests one. With Pump duty control at Control the optimizer writes the plan's room temperature (Indoor temperature) or water temperature (Flow temperature, Return temperature) to this entity.",
+              "space_setpoint_unit": "Indoor temperature is correct for a room or thermostat set-point. Flow temperature is for a controller whose set-point is a water temperature it holds its supply at. Return temperature is for a controller that takes the set-point as its return-water target (a Luxtronik through its Smart Home Interface, for example, is assumed to be one); it is written like a flow set-point, with the rated hold, the weather curve and the 25 °C gate moved 5 K down to return terms. A version before this option reads Return temperature as Indoor temperature: switch it back to Flow temperature before downgrading. Pointing an indoor target at a flow entity would command roughly 21 °C to something expecting 35–45 °C and badly underheat the house. The unit is a declaration: the optimizer never infers it from the entity, and only the heat-pump pre-fill suggests one. With Pump duty control at Control the optimizer writes the plan's room temperature (Indoor temperature) or water temperature (Flow temperature, Return temperature) to this entity.",
               "flow_min_lift_k": "With Pump duty control at Control, the water set-point written at the plan's lowest power is the measured inlet water plus this: heat-pump return, buffer tank, floor return or valve outlet, and for a Return temperature entity the first three only. 5 K suits a controller that holds its supply at the set-point. A controller that takes the number as its return-water target is assumed to run its compressor harder the further the target sits above the return, so it likely wants less; 1–2 K is a starting point to check against the compressor's measured frequency and power, not a measured value.",
               "flow_heat_c": "The water set-point written at full planned power, and the highest one written while the plan is in charge. 55 °C suits a supply target. For a Return temperature entity choose it above the highest return you see in normal heating plus the lift, and no higher than the controller accepts; on a low-temperature floor heating 35–40 °C may be a starting point to check against measurements. Below 30 °C is not offered: the gate that means off is 25 °C for a flow target and 20 °C for a return target. A space boost or Boost mode writes the set-point entity's own maximum (up to 70 °C) on every step instead; a value other than 55 °C set here caps that too, so set one on a low-temperature floor heating.",
-              "space_setpoint_power_feedback": "On by default. Acts only with Pump duty control at Control, a Flow or Return temperature unit and a heat-pump power sensor; otherwise nothing changes. After a 5-minute start hold, the water set-point is nudged down while the measured draw is above the planned level and up while it is below, and held while it is within 10 %, instead of following the rising inlet water. Off writes the inlet plus the lift. Requirements on the controller: its heating hysteresis at most the lift (Luxtronik: 0.5 K), or a stopped compressor is not started; its minimum return target below the heating-season return; its integration polling it at least every 10 minutes, and restoring its heating mode after a controller restart, since a Luxtronik Smart Home Interface drops every set value after 600 s without access; and no second tool writing the same registers (a Luxtronik then silently discards writes).",
-              "space_setpoint_low_limit_entity": "Optional. A temperature sensor that reports the lowest value the controller accepts for the set-point entity above (a Luxtronik through ha-luxtronik-shi: \"Temperature: return target minimum\", input 10104). With it, Follow the planned power never sends a value below it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes.",
-              "space_setpoint_high_limit_entity": "Optional. A temperature sensor that reports the highest value the controller accepts for the set-point entity above (a Luxtronik through ha-luxtronik-shi: \"Temperature: return limit\", input 10103). With it, Follow the planned power never sends a value above it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes."
+              "space_setpoint_power_feedback": "On by default. Acts only with Pump duty control at Control, a Flow or Return temperature unit and a heat-pump power sensor; otherwise nothing changes. After a 5-minute start hold, the water set-point is nudged down while the measured draw is above the planned level and up while it is below, and held while it is within 10 %, instead of following the rising inlet water. Off writes the inlet plus the lift. Requirements on the controller: its heating hysteresis at most the lift (0.5 K on a Luxtronik, for example), or a stopped compressor is not started; its minimum return target below the heating-season return; its integration polling it at least every 10 minutes, and restoring its heating mode after a controller restart, since a controller can drop what was set when it goes unread (a Luxtronik Smart Home Interface, for one, drops every set value after 600 s without access); and no second tool writing the same registers (a Luxtronik, for one, then silently discards writes).",
+              "space_setpoint_low_limit_entity": "Optional. A temperature sensor that reports the lowest value the controller accepts for the set-point entity above (for example a Luxtronik through ha-luxtronik-shi: \"Temperature: return target minimum\", input 10104). With it, Follow the planned power never sends a value below it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes.",
+              "space_setpoint_high_limit_entity": "Optional. A temperature sensor that reports the highest value the controller accepts for the set-point entity above (for example a Luxtronik through ha-luxtronik-shi: \"Temperature: return limit\", input 10103). With it, Follow the planned power never sends a value above it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes."
             }
           },
           "plant": {
@@ -941,7 +941,7 @@
       },
       "heat_curve": {
         "title": "Heat curve control",
-        "description": "Shifts the heat curve up in cheap hours and down in expensive ones, through a Danfoss ECL110 over MQTT, a number entity that offsets your controller's curve, or both. Leave the topics and the entity empty if you have neither.",
+        "description": "Shifts your controller's heat curve up in cheap hours and down in expensive ones, three ways: over MQTT topics, to a controller that takes its offset there (a Danfoss ECL110 through an MQTT bridge, for example); to a number entity that offsets the curve; or to a curve setting the controller stores. The topics and the entity can be used together. Leave them all empty if your controller has none of these.",
         "data": {
           "ecl110_displace_set_topic": "Offset command topic",
           "ecl110_command_topic": "Legacy JSON command topic",
@@ -960,7 +960,7 @@
           "after_save": "After saving"
         },
         "data_description": {
-          "ecl110_displace_set_topic": "MQTT topic the parallel heat-curve offset is published to. Nothing is published while this and the legacy command topic below are empty: leave them empty if you do not have a Danfoss ECL110.",
+          "ecl110_displace_set_topic": "MQTT topic the parallel heat-curve offset is published to. Nothing is published while this and the legacy command topic below are empty: leave them empty if your controller does not take its offset over MQTT (a Danfoss ECL110 through an MQTT bridge is one that does).",
           "ecl110_command_topic": "Only needed for older setups that expect a JSON payload instead.",
           "ecl110_state_topic": "MQTT topic the controller reports its current state on.",
           "ecl110_mqtt_qos": "0 is fine for almost everyone.",
@@ -970,8 +970,8 @@
           "ecl110_pid_time_constant_hours": "Roughly how long the controller takes to act on a new offset. Used so the optimizer does not ask for changes faster than the system can follow.",
           "heat_curve_displace_entity": "A number entity that shifts your controller's heat curve. Kind offset: a whole-curve offset, 0 meaning no shift, that the controller forgets on a restart (for example a Luxtronik SHI heating offset); turning the optimizer off, or unloading it, writes 0. Kind persistent: a curve setting the controller stores; turning the optimizer off, or unloading it, writes back the value it held before the first write.",
           "heat_curve_target_kind": "Offset: a temperature difference, 0 neutral, not stored by the controller. Prefer it wherever your controller has one. Persistent: a curve setting the controller stores, displaced from its own value and written back on off; every write wears the controller's memory, so writes are limited per day.",
-          "heat_curve_offset_band_k": "The offset written to the entity stays within this many kelvin either way. 3 K is an estimate between a +1 to +2 step SG-Ready boost and Luxtronik's own ±5 K correction.",
-          "heat_curve_persistent_band_k": "The stored setting is moved at most this many kelvin either way from the value it held before the first write. 3 K is an estimate between a +1 to +2 step SG-Ready boost and Luxtronik's own ±5 K correction.",
+          "heat_curve_offset_band_k": "The offset written to the entity stays within this many kelvin either way. 3 K is an estimate between a +1 to +2 step SG-Ready boost and the ±5 K user correction one controller offers (Luxtronik's).",
+          "heat_curve_persistent_band_k": "The stored setting is moved at most this many kelvin either way from the value it held before the first write. 3 K is an estimate between a +1 to +2 step SG-Ready boost and the ±5 K user correction one controller offers (Luxtronik's).",
           "heat_curve_persistent_writes_per_day": "Writes in one local day, the write back on off included; one is always kept for it. 12 (six shift-and-return episodes) stays under the one documented manufacturer quota found (Daikin, 7000 a year); the margin below it is an estimate. 0 or 1 writes nothing. Above 19 exceeds that quota.",
           "heat_curve_persistent_min_dwell_minutes": "After a write, the next waits at least this long. 60 minutes is about three response times of a radiator system (a forum estimate); a slow floor may want 2 to 3 hours.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
@@ -1274,7 +1274,7 @@
         "data_description": {
           "heat_pump_mode_entity": "Optional. The pump's own mode selector - cooling, heating, hot water, or a combination of two. Read only, unless Pump duty control is set to Control. A pump in a cooling or hot-water-only mode cannot heat the house, and one in a heating-only mode cannot make hot water, so without this the plan can promise heat the pump is not currently able to deliver. Left empty, the optimizer assumes the pump can do everything.",
           "pump_duty_mode": "Off (the default) never writes the pump's operating mode or set-points. Observe writes none either and keeps a 24-hour ledger, in the diagnostics, of the duty each plan step asked for against what the pump did (from the power entity, the mode and the tank temperature). With any of the three, the heat pump on/off switch, if you have set one, is still switched by the plan. Control writes the operating mode above (hot water only on hot-water-only steps, heating only on space-heating-only steps, unchanged on idle steps; on a step that plans both, hot water only for the hot-water share of the step and then heating, a share under 5 minutes going to the other duty; Heating + DHW while a boost or an anti-legionella cycle calls for both, and whenever the plan is not in charge), the hot water set-point entity (the hot water set-point configured on the hot water page, or the anti-legionella temperature during a cycle) and the space set-point entity (for a flow set-point, a target that follows the planned power — the heating flow (55 °C, or the Heating flow ceiling) at full power, toward 5 °C (or the Minimum lift above the inlet water) above the first fresh reading of the heat-pump return, buffer tank, floor return or valve outlet (35 °C when none is configured) at the modulation floor — on steps that heat the house, 25 °C on steps that do not (20 °C for a Return temperature set-point, or the entity's own minimum if that is higher), and 35 °C or the weather curve, whichever is higher, when the plan is not in charge; for an indoor one, the planned room temperature). Where the mode offers no single-duty option, as on the GCHV Modbus package, the other duty's set-point is lowered instead: the hot water one to 30 °C, a flow set-point to the same 25 °C (20 °C for Return temperature), an indoor one to 5 °C, each never below the entity's own minimum. A hot-water-only stretch is capped at 90 minutes (30 below -10 °C outdoors), unless the room is already at its planned temperature. Where Capacity limited (night mode) is a switch and silent windows are scheduled, Control also holds that switch on inside a silent window and off outside one. While Optimizer active is on, any change to those entities the optimizer did not make is written back at once; turn Optimizer active off to change the pump by hand. A value the pump does not hold raises a warning and is sent again every 5 minutes.",
-          "space_hysteresis_entity": "Optional. A sensor or number holding the pump's own heating start hysteresis as a temperature difference in K (°C reads the same, °F is scaled; 0 to 20 K): its controller starts heating only once the target sits that far above the water. On a flow or return set-point the lift written above the measured water at the lowest planned level is then never smaller than it, so a planned heating step is one the pump starts. A controller that publishes only the start threshold itself (a Luxtronik's Demand border, input 10107) needs a template sensor of the return target minus that threshold. Left empty or unreadable, the configured lift stands.",
+          "space_hysteresis_entity": "Optional. A sensor or number holding the pump's own heating start hysteresis as a temperature difference in K (°C reads the same, °F is scaled; 0 to 20 K): its controller starts heating only once the target sits that far above the water. On a flow or return set-point the lift written above the measured water at the lowest planned level is then never smaller than it, so a planned heating step is one the pump starts. A controller that publishes only the start threshold itself (a Luxtronik's Demand border, input 10107, for example) needs a template sensor of the return target minus that threshold. Left empty or unreadable, the configured lift stands.",
           "dhw_hysteresis_entity": "Optional. A sensor or number holding the pump's own hot water start hysteresis as a temperature difference in K (°C reads the same, °F is scaled; 0 to 20 K): the pump starts a charge only once the tank is below the hot water target minus this. The plan then places no charge on a tank warmer than that (a charge planned for the current step is kept, as it may already be running; a disinfection charge is judged against the disinfection temperature), and the duty ledger marks an idle hot water step on such a tank not-startable instead of idle-instead. A hot water minimum above that start temperature cannot be held by the pump and raises a warning. Left empty, unreadable or 0, every planned charge is taken to start.",
           "heat_pump_defrost_entity": "Optional. On while the pump reverses to melt frost off the outdoor coil. The electricity bought during a defrost goes into the coil rather than into the house. Note that many pumps are only polled every few minutes, so short defrosts are missed entirely: this is a sample of defrost activity, not a stopwatch.",
           "heat_pump_online_entity": "Optional, and strongly recommended for a cloud-connected pump. On while the pump is actually reachable. A cloud integration can keep republishing its last known readings while the pump itself has dropped off the network, which leaves every other sensor looking perfectly fresh; this is the one signal that says otherwise. On a local (LAN) connection the sensors go unavailable by themselves and this adds little.",
@@ -1407,7 +1407,7 @@
         },
         "data_description": {
           "dso_product": "A dated Sweden-only table. Selecting a product writes transfer-fee rules and peak-tariff fields you can still edit, switches the transfer fee to Time-of-use rules and turns the peak tariff on. Verify against your bill: a product keeps writing its values after its end date. A product the table does not know writes nothing.",
-          "grid_fee_mode": "The fee your grid company adds per kWh transferred. Tibber's price does not include it, so with it configured the plan finally sees the whole marginal price. \"Time-of-use rules\" uses the schedule below; \"Live sensor\" follows an entity.",
+          "grid_fee_mode": "The fee your grid company adds per kWh transferred. Tibber's price does not include it, and a price sensor includes it only if you added it there yourself, so with it configured the plan sees the whole marginal price. \"Time-of-use rules\" uses the schedule below; \"Live sensor\" follows an entity.",
           "grid_fee_fixed": "A flat fee added in every hour, on top of the time-of-use rules or the live sensor's value. It only applies when Grid transfer fee is Time-of-use rules or Live sensor; with None it is ignored. Take it from your grid invoice.",
           "grid_fee_rules": "One rule per line, for example \"Nov-Mar Mon-Fri 06:00-22:00 = 0.25\". Month, weekday and time parts are each optional; overlapping rules add together, which matches a base fee plus a high-load surcharge. A comma between digits is a decimal separator, so \"0,25\" reads as 0.25 and never splits a rule.",
           "grid_fee_entity": "A sensor reporting the current fee in {currency}/kWh, for grids with dynamic fees. Its value is added to every planned hour.",
@@ -1519,7 +1519,7 @@
       },
       "modbus_prefill": {
         "title": "Pre-fill from a heat pump device",
-        "description": "For a Rotenso Windmi or another GCHV-built heat pump, read through the tuya_heat_pump project's Modbus package or through the pump's own Home Assistant device. Pick the device, or leave it empty and name the package's entity prefix, and submit: the next form suggests values read from the pump - the hot water set-points and schedule, the anti-legionella days, the night mode schedule, the pump's maximum electrical power (from its unit capacity), whether the pump steers on water temperature, and the pump's own sensors for sensor slots that are still empty. Edit or clear any of them; only what you keep is saved, and a field you clear is left as it was. Nothing about the house or its heating system can be read this way.\n\nEntities read: {found}. Backup heater type register: {backup_heater_type} - any value but 7 means the pump has electric heat of its own, which the heater slots on Heat pump telemetry are there to watch.\n\nRoles read from an entity's NAME rather than from a published definition - the page cannot verify those, so check each before saving: {name_matched}. Roles read from published definitions, by source: {matched_sources}.",
+        "description": "Reads only what this page has a mapping for: a GCHV-built heat pump (a Rotenso Windmi, for example) through the tuya_heat_pump project's Modbus package, or a heat pump's own Home Assistant device, through its integration's published definitions where one is mapped here and otherwise by its entities' names. Pick the device, or leave it empty and name the package's entity prefix, and submit: the next form suggests values read from the pump - the hot water set-points and schedule, the anti-legionella days, the night mode schedule, the pump's maximum electrical power (from its unit capacity), whether the pump steers on water temperature, and the pump's own sensors for sensor slots that are still empty. Edit or clear any of them; only what you keep is saved, and a field you clear is left as it was. Nothing about the house or its heating system can be read this way.\n\nEntities read: {found}. Backup heater type register: {backup_heater_type} - any value but 7 means the pump has electric heat of its own, which the heater slots on Heat pump telemetry are there to watch.\n\nRoles read from an entity's NAME rather than from a published definition - the page cannot verify those, so check each before saving: {name_matched}. Roles read from published definitions, by source: {matched_sources}.",
         "data": {
           "prefill_device": "Heat pump device (optional)",
           "modbus_prefill_prefix": "Modbus package entity prefix",
@@ -1988,10 +1988,10 @@
         "name": "DHW Temperature"
       },
       "ecl110_displace": {
-        "name": "ECL110 Displace"
+        "name": "Heat-Curve Displace"
       },
       "ecl110_effective_displace": {
-        "name": "ECL110 Effective Displace"
+        "name": "Heat-Curve Effective Displace"
       },
       "floor_heating_return_temperature": {
         "name": "Floor Heating Return Temperature"
@@ -2382,15 +2382,15 @@
           "description": "Heat loss multiplier when raining. 1.15 means 15% more heat loss in rain of 2 mm/h or more (wet building envelope effect); lighter rain scales it down in proportion, and 0.1 mm/h or less applies none of it."
         },
         "ecl110_pid_time_constant_hours": {
-          "name": "ECL110 PI/PID Time Constant",
-          "description": "Time constant (hours) for the ECL110 PI/PID response approximation. Lower values react faster, higher values are smoother."
+          "name": "Heat-Curve Controller Time Constant",
+          "description": "Time constant (hours) for the heat-curve controller's PI/PID response approximation. Lower values react faster, higher values are smoother."
         },
         "ecl110_displace_min": {
-          "name": "ECL110 displace minimum",
+          "name": "Heat-curve displace minimum",
           "description": "Lowest parallel shift the optimizer may command, in °C."
         },
         "ecl110_displace_max": {
-          "name": "ECL110 displace maximum",
+          "name": "Heat-curve displace maximum",
           "description": "Highest parallel shift the optimizer may command, in °C."
         },
         "quiet_silent_windows": {
diff --git a/custom_components/heatpump_optimizer/translations/de.json b/custom_components/heatpump_optimizer/translations/de.json
index 691dd9d300..c701511a65 100644
--- a/custom_components/heatpump_optimizer/translations/de.json
+++ b/custom_components/heatpump_optimizer/translations/de.json
@@ -539,7 +539,7 @@
           "learning_features": "Erweiterte Lernfunktionen",
           "grid_connection": "Sicherung und Spitzenwächter",
           "grid_fees": "Netzentgelte und Vertrag",
-          "heat_curve": "Heizkurvensteuerung (ECL110)",
+          "heat_curve": "Heizkurvensteuerung",
           "factory_reset": "Auf Werkseinstellungen zurücksetzen"
         }
       },
@@ -593,12 +593,12 @@
               "indoor_temp_entity": "Optional. Die tatsächliche Raumtemperatur. Ohne sie vertraut der Optimierer seinem eigenen Modell, das mit der Zeit abdriftet.",
               "outdoor_temp_entity": "Optional. Ein lokales Außenthermometer ist für die aktuelle Stunde genauer als die Vorhersage.",
               "space_setpoint_entity": "Optional. Eine Zahl, ein Helfer oder eine Climate-Entität, die der Sollwert der Raumheizung der Pumpe ist. Steht die Steuerung der Pumpenfunktion auf Steuern, schreibt der Optimierer sie in jedem Planschritt, wie die Steuerung der Pumpenfunktion beschreibt, und das Ausschalten von Optimierer aktiv schreibt den Wert zurück, den die Entität vor dem ersten Schreiben zeigte. Bei Aus oder Beobachten wird sie nur gelesen, um zu bemerken, wenn sie nicht gelesen werden kann.",
-              "space_setpoint_unit": "Innentemperatur ist richtig für einen Raum- oder Thermostat-Sollwert. Vorlauftemperatur gilt für einen Regler, dessen Sollwert eine Wassertemperatur ist, auf der er seinen Vorlauf hält. Rücklauftemperatur gilt für einen Regler, der den Sollwert als Ziel für das Rücklaufwasser nimmt (angenommen für eine Luxtronik über ihre Smart-Home-Schnittstelle); er wird wie ein Vorlauf-Sollwert geschrieben, wobei der Nennhaltewert, die Wetterkurve und die 25-°C-Schwelle um 5 K nach unten in Rücklaufwerte verschoben werden. Eine Version vor dieser Option liest Rücklauftemperatur als Innentemperatur: Stelle vor einem Downgrade wieder auf Vorlauftemperatur um. Würde ein Innentemperaturziel auf eine Vorlauf-Entität zeigen, würden etwa 21 °C an ein Gerät gesendet, das 35–45 °C erwartet, und das Haus würde stark unterheizt. Die Einheit ist eine Angabe: Der Optimizer leitet sie nie aus der Entität ab, nur das Vorausfüllen aus einem Wärmepumpengerät schlägt eine vor. Bei „Steuerung der Pumpenfunktion“ auf „Steuern“ schreibt der Optimizer die Raumtemperatur (Innentemperatur) bzw. die Wassertemperatur (Vorlauftemperatur, Rücklauftemperatur) des Plans in diese Entität.",
+              "space_setpoint_unit": "Innentemperatur ist richtig für einen Raum- oder Thermostat-Sollwert. Vorlauftemperatur gilt für einen Regler, dessen Sollwert eine Wassertemperatur ist, auf der er seinen Vorlauf hält. Rücklauftemperatur gilt für einen Regler, der den Sollwert als Ziel für das Rücklaufwasser nimmt (angenommen zum Beispiel für eine Luxtronik über ihre Smart-Home-Schnittstelle); er wird wie ein Vorlauf-Sollwert geschrieben, wobei der Nennhaltewert, die Wetterkurve und die 25-°C-Schwelle um 5 K nach unten in Rücklaufwerte verschoben werden. Eine Version vor dieser Option liest Rücklauftemperatur als Innentemperatur: Stelle vor einem Downgrade wieder auf Vorlauftemperatur um. Würde ein Innentemperaturziel auf eine Vorlauf-Entität zeigen, würden etwa 21 °C an ein Gerät gesendet, das 35–45 °C erwartet, und das Haus würde stark unterheizt. Die Einheit ist eine Angabe: Der Optimizer leitet sie nie aus der Entität ab, nur das Vorausfüllen aus einem Wärmepumpengerät schlägt eine vor. Bei „Steuerung der Pumpenfunktion“ auf „Steuern“ schreibt der Optimizer die Raumtemperatur (Innentemperatur) bzw. die Wassertemperatur (Vorlauftemperatur, Rücklauftemperatur) des Plans in diese Entität.",
               "flow_min_lift_k": "Mit Steuerung der Pumpenfunktion auf Steuern ist der bei der niedrigsten Planleistung geschriebene Wasser-Sollwert das gemessene Eingangswasser plus dieser Wert: Wärmepumpen-Rücklauf, Pufferspeicher, Fußbodenrücklauf oder Ventilauslass, und bei einer Entität mit Rücklauftemperatur nur die ersten drei. 5 K passt zu einem Regler, der seinen Vorlauf auf dem Sollwert hält. Von einem Regler, der die Zahl als Ziel für das Rücklaufwasser nimmt, wird angenommen, dass er seinen Verdichter umso stärker laufen lässt, je weiter das Ziel über dem Rücklauf liegt, er will also wahrscheinlich weniger; 1–2 K ist ein Ausgangspunkt, der an der gemessenen Frequenz und Leistung des Verdichters zu prüfen ist, kein gemessener Wert.",
               "flow_heat_c": "Der bei voller Planleistung geschriebene Wasser-Sollwert und der höchste, der geschrieben wird, solange der Plan die Führung hat. 55 °C passt zu einem Vorlaufziel. Wähle ihn bei einer Entität mit Rücklauftemperatur über dem höchsten Rücklauf, den du im normalen Heizbetrieb siehst, plus dem Hub, und nicht höher, als der Regler annimmt; bei einer Niedertemperatur-Fußbodenheizung können 35–40 °C ein Ausgangspunkt sein, der an Messungen zu prüfen ist. Unter 30 °C wird nicht angeboten: Die Schwelle, die aus bedeutet, liegt bei 25 °C für ein Vorlaufziel und bei 20 °C für ein Rücklaufziel. Ein Raumheizungs-Boost oder der Boost-Modus schreibt stattdessen in jedem Schritt das eigene Maximum der Sollwert-Entität (höchstens 70 °C); ein anderer Wert als 55 °C begrenzt auch das, also stelle bei einer Niedertemperatur-Fußbodenheizung einen ein.",
-              "space_setpoint_power_feedback": "Standardmäßig an. Wirkt nur mit Wärmepumpen-Betriebssteuerung auf Steuern, einer Einheit Vorlauf- oder Rücklauftemperatur und einem Leistungssensor der Wärmepumpe; sonst ändert sich nichts. Nach 5 Minuten Starthaltezeit wird der Wasser-Sollwert gesenkt, solange die gemessene Aufnahme über der geplanten Leistung liegt, angehoben, solange sie darunter liegt, und innerhalb von 10 % gehalten, statt dem steigenden Eingangswasser zu folgen. Aus schreibt das Eingangswasser plus den Hub. Anforderungen an den Regler: seine Heizungshysterese höchstens der Hub (Luxtronik: 0,5 K), sonst startet ein stehender Verdichter nicht; sein minimales Rücklaufziel unter dem Rücklauf der Heizperiode; seine Integration fragt ihn mindestens alle 10 Minuten ab und stellt nach einem Reglerneustart die Heizbetriebsart wieder her, denn eine Luxtronik Smart Home Interface verwirft nach 600 s ohne Zugriff alle gesetzten Werte; und kein zweites Werkzeug schreibt dieselben Register (eine Luxtronik verwirft Schreibvorgänge dann stillschweigend).",
-              "space_setpoint_low_limit_entity": "Optional. Ein Temperatursensor, der den niedrigsten Wert meldet, den der Regler für die Sollwert-Entität oben annimmt (eine Luxtronik über ha-luxtronik-shi: \"Temperature: return target minimum\", Eingang 10104). Damit sendet Geplanter Leistung über die gemessene Aufnahme folgen nie einen Wert darunter, statt die Grenze erst zu finden, wenn der Regler einen Schreibwert kappt. Nur von dieser Option verwendet; leer ändert sich nichts.",
-              "space_setpoint_high_limit_entity": "Optional. Ein Temperatursensor, der den höchsten Wert meldet, den der Regler für die Sollwert-Entität oben annimmt (eine Luxtronik über ha-luxtronik-shi: \"Temperature: return limit\", Eingang 10103). Damit sendet Geplanter Leistung über die gemessene Aufnahme folgen nie einen Wert darüber, statt die Grenze erst zu finden, wenn der Regler einen Schreibwert kappt. Nur von dieser Option verwendet; leer ändert sich nichts."
+              "space_setpoint_power_feedback": "Standardmäßig an. Wirkt nur mit Wärmepumpen-Betriebssteuerung auf Steuern, einer Einheit Vorlauf- oder Rücklauftemperatur und einem Leistungssensor der Wärmepumpe; sonst ändert sich nichts. Nach 5 Minuten Starthaltezeit wird der Wasser-Sollwert gesenkt, solange die gemessene Aufnahme über der geplanten Leistung liegt, angehoben, solange sie darunter liegt, und innerhalb von 10 % gehalten, statt dem steigenden Eingangswasser zu folgen. Aus schreibt das Eingangswasser plus den Hub. Anforderungen an den Regler: seine Heizungshysterese höchstens der Hub (bei einer Luxtronik zum Beispiel 0,5 K), sonst startet ein stehender Verdichter nicht; sein minimales Rücklaufziel unter dem Rücklauf der Heizperiode; seine Integration fragt ihn mindestens alle 10 Minuten ab und stellt nach einem Reglerneustart die Heizbetriebsart wieder her, denn ein Regler kann Gesetztes verwerfen, wenn er nicht abgefragt wird (eine Luxtronik Smart Home Interface etwa verwirft nach 600 s ohne Zugriff alle gesetzten Werte); und kein zweites Werkzeug schreibt dieselben Register (eine Luxtronik etwa verwirft Schreibvorgänge dann stillschweigend).",
+              "space_setpoint_low_limit_entity": "Optional. Ein Temperatursensor, der den niedrigsten Wert meldet, den der Regler für die Sollwert-Entität oben annimmt (zum Beispiel eine Luxtronik über ha-luxtronik-shi: \"Temperature: return target minimum\", Eingang 10104). Damit sendet Geplanter Leistung über die gemessene Aufnahme folgen nie einen Wert darunter, statt die Grenze erst zu finden, wenn der Regler einen Schreibwert kappt. Nur von dieser Option verwendet; leer ändert sich nichts.",
+              "space_setpoint_high_limit_entity": "Optional. Ein Temperatursensor, der den höchsten Wert meldet, den der Regler für die Sollwert-Entität oben annimmt (zum Beispiel eine Luxtronik über ha-luxtronik-shi: \"Temperature: return limit\", Eingang 10103). Damit sendet Geplanter Leistung über die gemessene Aufnahme folgen nie einen Wert darüber, statt die Grenze erst zu finden, wenn der Regler einen Schreibwert kappt. Nur von dieser Option verwendet; leer ändert sich nichts."
             }
           },
           "plant": {
@@ -940,8 +940,8 @@
         }
       },
       "heat_curve": {
-        "title": "Heizkurvensteuerung (ECL110)",
-        "description": "Für Danfoss-ECL110-Regler, die über MQTT angesteuert werden. Der Optimierer verschiebt die Heizkurve in günstigen Stunden nach oben und in teuren nach unten. Lass diese Felder leer, wenn du keinen solchen Regler hast.",
+        "title": "Heizkurvensteuerung",
+        "description": "Verschiebt die Heizkurve deines Reglers in günstigen Stunden nach oben und in teuren nach unten, auf drei Wegen: über MQTT-Topics an einen Regler, der seine Verschiebung dort annimmt (zum Beispiel ein Danfoss ECL110 über eine MQTT-Brücke); an eine Zahlenentität, die die Kurve verschiebt; oder an eine Kurveneinstellung, die der Regler speichert. Topics und Entität lassen sich zusammen nutzen. Lass alles leer, wenn dein Regler nichts davon bietet.",
         "data": {
           "ecl110_displace_set_topic": "Topic für Verschiebungsbefehl",
           "ecl110_command_topic": "Topic für Legacy-JSON-Befehl",
@@ -960,7 +960,7 @@
           "after_save": "Nach dem Speichern"
         },
         "data_description": {
-          "ecl110_displace_set_topic": "MQTT-Topic, auf das die Parallelverschiebung der Heizkurve veröffentlicht wird. Solange dieses und das Legacy-Befehls-Topic unten leer sind, wird nichts veröffentlicht: Lass beide leer, wenn du keinen Danfoss ECL110 hast.",
+          "ecl110_displace_set_topic": "MQTT-Topic, auf das die Parallelverschiebung der Heizkurve veröffentlicht wird. Solange dieses und das Legacy-Befehls-Topic unten leer sind, wird nichts veröffentlicht: Lass beide leer, wenn dein Regler seine Verschiebung nicht über MQTT annimmt (ein Danfoss ECL110 über eine MQTT-Brücke tut das).",
           "ecl110_command_topic": "Nur für ältere Installationen nötig, die stattdessen eine JSON-Nutzlast erwarten.",
           "ecl110_state_topic": "MQTT-Topic, auf dem der Regler seinen aktuellen Zustand meldet.",
           "ecl110_mqtt_qos": "0 genügt für fast alle.",
@@ -970,8 +970,8 @@
           "ecl110_pid_time_constant_hours": "Ungefähr, wie lange der Regler braucht, um auf eine neue Verschiebung zu reagieren. Damit fordert der Optimierer keine schnelleren Änderungen an, als das System umsetzen kann.",
           "heat_curve_displace_entity": "Eine Zahlenentität, die die Heizkurve deines Reglers verschiebt. Typ Verschiebung: eine Verschiebung der ganzen Kurve, bei der 0 keine Verschiebung bedeutet und die der Regler bei einem Neustart vergisst (zum Beispiel eine Luxtronik-SHI-Heizverschiebung); Ausschalten oder Entladen des Optimierers schreibt 0. Typ beständig: eine Kurveneinstellung, die der Regler speichert; Ausschalten oder Entladen des Optimierers schreibt den Wert zurück, den sie vor dem ersten Schreiben hatte.",
           "heat_curve_target_kind": "Verschiebung: eine Temperaturdifferenz, 0 neutral, vom Regler nicht gespeichert. Nimm sie, wo immer dein Regler eine hat. Beständig: eine Kurveneinstellung, die der Regler speichert, von ihrem eigenen Wert verschoben und beim Ausschalten zurückgeschrieben; jeder Schreibvorgang nutzt den Speicher des Reglers ab, daher sind die Schreibvorgänge pro Tag begrenzt.",
-          "heat_curve_offset_band_k": "Der auf die Entität geschriebene Offset bleibt in beide Richtungen innerhalb so vieler Kelvin. 3 K ist eine Schätzung zwischen einer SG-Ready-Anhebung um +1 bis +2 Stufen und Luxtroniks eigener Korrektur von ±5 K.",
-          "heat_curve_persistent_band_k": "Die gespeicherte Einstellung wird höchstens so viele Kelvin in jede Richtung von dem Wert verschoben, den sie vor dem ersten Schreiben hatte. 3 K ist eine Schätzung zwischen einer SG-Ready-Anhebung um +1 bis +2 Stufen und Luxtroniks eigener Korrektur von ±5 K.",
+          "heat_curve_offset_band_k": "Der auf die Entität geschriebene Offset bleibt in beide Richtungen innerhalb so vieler Kelvin. 3 K ist eine Schätzung zwischen einer SG-Ready-Anhebung um +1 bis +2 Stufen und der Benutzerkorrektur von ±5 K, die ein Regler bietet (der von Luxtronik).",
+          "heat_curve_persistent_band_k": "Die gespeicherte Einstellung wird höchstens so viele Kelvin in jede Richtung von dem Wert verschoben, den sie vor dem ersten Schreiben hatte. 3 K ist eine Schätzung zwischen einer SG-Ready-Anhebung um +1 bis +2 Stufen und der Benutzerkorrektur von ±5 K, die ein Regler bietet (der von Luxtronik).",
           "heat_curve_persistent_writes_per_day": "Schreibvorgänge an einem lokalen Tag, das Zurückschreiben beim Ausschalten eingeschlossen; einer wird dafür immer zurückgehalten. 12 (sechs Verschiebungen mit Rückkehr) liegt unter dem einzigen dokumentierten Herstellerkontingent, das gefunden wurde (Daikin, 7000 pro Jahr); der Abstand darunter ist eine Schätzung. 0 oder 1 schreibt nichts. Über 19 überschreitet dieses Kontingent.",
           "heat_curve_persistent_min_dwell_minutes": "Nach einem Schreibvorgang wartet der nächste mindestens so lange. 60 Minuten sind etwa drei Reaktionszeiten einer Heizkörperanlage (eine Schätzung aus einem Forum); eine träge Fußbodenheizung braucht eher 2 bis 3 Stunden.",
           "after_save": "Das Speichern wirkt sofort; hier wählst du, wohin der Dialog als Nächstes führt."
@@ -1274,7 +1274,7 @@
         "data_description": {
           "heat_pump_mode_entity": "Optional. Die eigene Modusauswahl der Wärmepumpe – Kühlen, Heizen, Warmwasser oder eine Kombination aus zwei. Nur lesend, außer die Steuerung der Pumpenfunktion steht auf Steuern. Eine Wärmepumpe im Kühl- oder reinen Warmwassermodus kann das Haus nicht heizen, und eine im reinen Heizmodus kann kein Warmwasser bereiten; ohne diese Angabe kann der Plan Wärme versprechen, die die Wärmepumpe gerade nicht liefern kann. Bleibt sie leer, geht der Optimierer davon aus, dass die Wärmepumpe alles kann.",
           "pump_duty_mode": "Aus (Standard) schreibt nie den Betriebsmodus oder die Sollwerte der Wärmepumpe. Beobachten schreibt ebenfalls nichts und führt in den Diagnosedaten ein 24-Stunden-Protokoll darüber, welche Funktion jeder Planschritt angefordert hat und was die Wärmepumpe getan hat (aus der Leistungsentität, dem Modus und der Speichertemperatur). Bei jeder der drei Einstellungen wird der Ein/Aus-Schalter der Wärmepumpe, falls du einen eingerichtet hast, weiterhin vom Plan geschaltet. Steuern schreibt den oben gewählten Betriebsmodus (nur Warmwasser bei reinen Warmwasserschritten, nur Heizen bei reinen Raumheizungsschritten, unverändert bei Leerlaufschritten; bei einem Schritt, der beides plant, nur Warmwasser für den Warmwasseranteil des Schritts und danach Heizen, wobei ein Anteil unter 5 Minuten der anderen Funktion zugeschlagen wird; Heizen + Warmwasser, solange ein Boost oder ein Anti-Legionellen-Zyklus beides verlangt, und immer dann, wenn der Plan nicht die Führung hat), die Entität für den Warmwasser-Sollwert (der auf der Warmwasserseite konfigurierte Warmwasser-Sollwert oder während eines Zyklus die Anti-Legionellen-Temperatur) und die Entität für den Raumheizungs-Sollwert (bei einem Vorlauf-Sollwert ein Ziel, das der geplanten Leistung folgt – die Heizungsvorlauftemperatur (55 °C, oder Obergrenze der Heizungsvorlauftemperatur) bei voller Leistung, in Richtung 5 °C (oder Mindesthub über dem Eingangswasser) über dem ersten aktuellen Wert von Wärmepumpen-Rücklauf, Pufferspeicher, Fußbodenrücklauf oder Ventilauslass (35 °C, wenn keiner konfiguriert ist) an der Modulationsuntergrenze – bei Schritten, die das Haus heizen, 25 °C bei Schritten, die es nicht tun (20 °C bei einem Rücklauftemperatur-Sollwert oder das eigene Minimum der Entität, falls höher), und 35 °C oder die Wetterkurve, je nachdem, was höher ist, wenn der Plan nicht die Führung hat; bei einem Raum-Sollwert die geplante Raumtemperatur). Wo der Modus keine Einzelfunktion anbietet, etwa beim GCHV-Modbus-Paket, wird stattdessen der Sollwert der anderen Funktion gesenkt: der für Warmwasser auf 30 °C, ein Vorlauf-Sollwert auf dieselben 25 °C (20 °C bei Rücklauftemperatur), ein Raum-Sollwert auf 5 °C, jeweils nie unter das eigene Minimum der Entität. Ein reiner Warmwasserabschnitt ist auf 90 Minuten begrenzt (30 unter -10 °C Außentemperatur), außer der Raum hat bereits seine geplante Temperatur. Wo Leistung begrenzt (Nachtmodus) ein Schalter ist und Ruhefenster geplant sind, hält Steuern diesen Schalter außerdem innerhalb eines Ruhefensters an und außerhalb aus. Solange Optimierer aktiv eingeschaltet ist, wird jede Änderung an diesen Entitäten, die der Optimierer nicht vorgenommen hat, sofort zurückgeschrieben; schalte Optimierer aktiv aus, um die Wärmepumpe von Hand zu ändern. Ein Wert, den die Wärmepumpe nicht übernimmt, löst eine Warnung aus und wird alle 5 Minuten erneut gesendet.",
-          "space_hysteresis_entity": "Optional. Ein Sensor oder eine Zahl mit der eigenen Starthysterese der Pumpe fürs Heizen als Temperaturdifferenz in K (°C gilt unverändert, °F wird umgerechnet; 0 bis 20 K): Ihre Regelung beginnt erst zu heizen, wenn das Ziel so weit über dem Wasser liegt. Bei einem Vorlauf- oder Rücklauf-Sollwert ist die Anhebung über dem gemessenen Wasser auf der niedrigsten geplanten Stufe dann nie kleiner, sodass ein geplanter Heizschritt auch wirklich von der Pumpe gestartet wird. Eine Regelung, die nur die Startschwelle selbst veröffentlicht (bei einer Luxtronik der Bedarfsgrenzwert, Eingang 10107), braucht einen Template-Sensor aus Rücklaufziel minus dieser Schwelle. Bleibt sie leer oder unlesbar, gilt die konfigurierte Anhebung.",
+          "space_hysteresis_entity": "Optional. Ein Sensor oder eine Zahl mit der eigenen Starthysterese der Pumpe fürs Heizen als Temperaturdifferenz in K (°C gilt unverändert, °F wird umgerechnet; 0 bis 20 K): Ihre Regelung beginnt erst zu heizen, wenn das Ziel so weit über dem Wasser liegt. Bei einem Vorlauf- oder Rücklauf-Sollwert ist die Anhebung über dem gemessenen Wasser auf der niedrigsten geplanten Stufe dann nie kleiner, sodass ein geplanter Heizschritt auch wirklich von der Pumpe gestartet wird. Eine Regelung, die nur die Startschwelle selbst veröffentlicht (zum Beispiel bei einer Luxtronik der Bedarfsgrenzwert, Eingang 10107), braucht einen Template-Sensor aus Rücklaufziel minus dieser Schwelle. Bleibt sie leer oder unlesbar, gilt die konfigurierte Anhebung.",
           "dhw_hysteresis_entity": "Optional. Ein Sensor oder eine Zahl mit der eigenen Starthysterese der Pumpe für Warmwasser als Temperaturdifferenz in K (°C gilt unverändert, °F wird umgerechnet; 0 bis 20 K): Die Pumpe startet eine Ladung erst, wenn der Speicher unter dem Warmwasser-Sollwert minus diesem Wert liegt. Der Plan setzt dann keine Ladung auf einen wärmeren Speicher (eine für den aktuellen Schritt geplante Ladung bleibt, da sie schon laufen kann; eine Desinfektionsladung wird an der Desinfektionstemperatur gemessen), und das Funktionsprotokoll markiert einen Warmwasser-Leerlaufschritt auf so einem Speicher als not-startable statt idle-instead. Ein Warmwasser-Minimum über dieser Starttemperatur kann die Pumpe nicht halten und löst eine Warnung aus. Bleibt sie leer, unlesbar oder 0, gilt jede geplante Ladung als startend.",
           "heat_pump_defrost_entity": "Optional. Ein, solange die Wärmepumpe den Kreislauf umkehrt, um Frost vom Außenwärmetauscher zu schmelzen. Der während einer Abtauung bezogene Strom geht in den Wärmetauscher statt ins Haus. Beachte, dass viele Wärmepumpen nur alle paar Minuten abgefragt werden, kurze Abtauvorgänge also komplett übersehen werden: Dies ist eine Stichprobe der Abtauaktivität, keine Stoppuhr.",
           "heat_pump_online_entity": "Optional und bei einer cloudverbundenen Wärmepumpe dringend empfohlen. Ein, solange die Wärmepumpe tatsächlich erreichbar ist. Eine Cloud-Integration kann ihre letzten bekannten Werte weiter veröffentlichen, obwohl die Wärmepumpe selbst vom Netzwerk getrennt ist, sodass alle anderen Sensoren völlig aktuell aussehen; dies ist das einzige Signal, das etwas anderes sagt. Bei einer lokalen Verbindung (LAN) werden die Sensoren von selbst nicht verfügbar, und dies bringt wenig.",
@@ -1407,7 +1407,7 @@
         },
         "data_description": {
           "dso_product": "Eine datierte Tabelle nur für Schweden. Die Auswahl eines Produkts schreibt Netzentgeltregeln und Felder für den Spitzentarif, die du weiterhin bearbeiten kannst, stellt das Netzentgelt auf „Zeitabhängige Regeln“ und schaltet den Spitzentarif ein. Prüfe sie anhand deiner Rechnung: Ein Produkt schreibt seine Werte auch nach seinem Enddatum weiter. Ein Produkt, das die Tabelle nicht kennt, schreibt nichts.",
-          "grid_fee_mode": "Das Entgelt, das dein Netzbetreiber pro übertragener kWh aufschlägt. Der Tibber-Preis enthält es nicht, sodass der Plan mit dieser Konfiguration endlich den gesamten Grenzpreis sieht. „Zeitabhängige Regeln“ verwendet den Zeitplan unten; „Live-Sensor“ folgt einer Entität.",
+          "grid_fee_mode": "Das Entgelt, das dein Netzbetreiber pro übertragener kWh aufschlägt. Der Tibber-Preis enthält es nicht, und ein Preissensor nur, wenn du es dort selbst eingerechnet hast, sodass der Plan mit dieser Konfiguration den gesamten Grenzpreis sieht. „Zeitabhängige Regeln“ verwendet den Zeitplan unten; „Live-Sensor“ folgt einer Entität.",
           "grid_fee_fixed": "Ein pauschales Entgelt, das in jeder Stunde zusätzlich zu den zeitabhängigen Regeln oder dem Wert des Live-Sensors aufgeschlagen wird. Es gilt nur, wenn Netzentgelt auf „Zeitabhängige Regeln“ oder „Live-Sensor“ steht; bei „Keine“ wird es ignoriert. Entnimm es deiner Netzrechnung.",
           "grid_fee_rules": "Eine Regel pro Zeile, zum Beispiel „Nov-Mar Mon-Fri 06:00-22:00 = 0.25“. Monats-, Wochentags- und Zeitteil sind jeweils optional; überlappende Regeln addieren sich, was einem Grundentgelt plus einem Hochlastzuschlag entspricht. Ein Komma zwischen Ziffern ist ein Dezimaltrenner, „0,25“ wird also als 0.25 gelesen und trennt nie eine Regel.",
           "grid_fee_entity": "Ein Sensor, der das aktuelle Entgelt in {currency}/kWh meldet, für Netze mit dynamischen Entgelten. Sein Wert wird zu jeder geplanten Stunde addiert.",
@@ -1519,7 +1519,7 @@
       },
       "modbus_prefill": {
         "title": "Aus einem Wärmepumpengerät vorbefüllen",
-        "description": "Für eine Rotenso Windmi oder eine andere von GCHV gebaute Wärmepumpe, die über das Modbus-Paket des Projekts tuya_heat_pump oder über das eigene Home-Assistant-Gerät der Pumpe ausgelesen wird. Wähle das Gerät, oder lass es leer und nenne den Entitäts-Präfix des Pakets, und sende ab: Das nächste Formular schlägt Werte vor, die aus der Pumpe gelesen wurden – die Warmwasser-Sollwerte und den Zeitplan, die Legionellentage, den Nachtmodus-Zeitplan, die maximale elektrische Leistung der Pumpe (aus ihrer Gerätekapazität), ob die Pumpe nach Wassertemperatur regelt, und die eigenen Sensoren der Pumpe für noch leere Sensorplätze. Bearbeite oder leere beliebige davon; nur was du behältst, wird gespeichert, und ein geleertes Feld bleibt, wie es war. Nichts über das Haus oder sein Heizsystem lässt sich auf diese Weise auslesen.\n\nGelesene Entitäten: {found}. Register für den Typ des Zuheizers: {backup_heater_type} – jeder Wert außer 7 bedeutet, dass die Pumpe eine eigene elektrische Heizung hat, die von den Heizer-Plätzen bei der Wärmepumpen-Telemetrie überwacht werden soll.\n\nRollen, die aus dem NAMEN einer Entität statt aus einer veröffentlichten Definition gelesen wurden – die Seite kann diese nicht prüfen, prüfe daher jede vor dem Speichern: {name_matched}. Rollen aus veröffentlichten Definitionen, nach Quelle: {matched_sources}.",
+        "description": "Liest nur, wofür diese Seite eine Zuordnung hat: eine von GCHV gebaute Wärmepumpe (zum Beispiel eine Rotenso Windmi) über das Modbus-Paket des Projekts tuya_heat_pump, oder das eigene Home-Assistant-Gerät einer Wärmepumpe, über die veröffentlichten Definitionen seiner Integration, wo hier eine zugeordnet ist, sonst über die Namen seiner Entitäten. Wähle das Gerät, oder lass es leer und nenne den Entitäts-Präfix des Pakets, und sende ab: Das nächste Formular schlägt Werte vor, die aus der Pumpe gelesen wurden – die Warmwasser-Sollwerte und den Zeitplan, die Legionellentage, den Nachtmodus-Zeitplan, die maximale elektrische Leistung der Pumpe (aus ihrer Gerätekapazität), ob die Pumpe nach Wassertemperatur regelt, und die eigenen Sensoren der Pumpe für noch leere Sensorplätze. Bearbeite oder leere beliebige davon; nur was du behältst, wird gespeichert, und ein geleertes Feld bleibt, wie es war. Nichts über das Haus oder sein Heizsystem lässt sich auf diese Weise auslesen.\n\nGelesene Entitäten: {found}. Register für den Typ des Zuheizers: {backup_heater_type} – jeder Wert außer 7 bedeutet, dass die Pumpe eine eigene elektrische Heizung hat, die von den Heizer-Plätzen bei der Wärmepumpen-Telemetrie überwacht werden soll.\n\nRollen, die aus dem NAMEN einer Entität statt aus einer veröffentlichten Definition gelesen wurden – die Seite kann diese nicht prüfen, prüfe daher jede vor dem Speichern: {name_matched}. Rollen aus veröffentlichten Definitionen, nach Quelle: {matched_sources}.",
         "data": {
           "prefill_device": "Wärmepumpen-Gerät (optional)",
           "modbus_prefill_prefix": "Entitäts-Präfix des Modbus-Pakets",
@@ -1988,10 +1988,10 @@
         "name": "Warmwassertemperatur"
       },
       "ecl110_displace": {
-        "name": "ECL110 Parallelverschiebung"
+        "name": "Heizkurven-Parallelverschiebung"
       },
       "ecl110_effective_displace": {
-        "name": "ECL110 Effektive Parallelverschiebung"
+        "name": "Heizkurven-Parallelverschiebung effektiv"
       },
       "floor_heating_return_temperature": {
         "name": "Rücklauftemperatur Fußbodenheizung"
@@ -2382,15 +2382,15 @@
           "description": "Multiplikator des Wärmeverlusts bei Regen. 1,15 bedeutet 15 % mehr Wärmeverlust bei Regen ab 2 mm/h (Effekt der nassen Gebäudehülle); schwächerer Regen verringert ihn anteilig, bei 0,1 mm/h oder weniger wirkt er gar nicht."
         },
         "ecl110_pid_time_constant_hours": {
-          "name": "ECL110 PI/PID-Zeitkonstante",
-          "description": "Zeitkonstante (Stunden) für die Näherung des PI/PID-Verhaltens des ECL110. Niedrigere Werte reagieren schneller, höhere sind gleichmäßiger."
+          "name": "PI/PID-Zeitkonstante des Heizkurvenreglers",
+          "description": "Zeitkonstante (Stunden) für die Näherung des PI/PID-Verhaltens des Heizkurvenreglers. Niedrigere Werte reagieren schneller, höhere sind gleichmäßiger."
         },
         "ecl110_displace_min": {
-          "name": "ECL110 Verschiebung Minimum",
+          "name": "Heizkurvenverschiebung Minimum",
           "description": "Niedrigste Parallelverschiebung, die der Optimierer vorgeben darf, in °C."
         },
         "ecl110_displace_max": {
-          "name": "ECL110 Verschiebung Maximum",
+          "name": "Heizkurvenverschiebung Maximum",
           "description": "Höchste Parallelverschiebung, die der Optimierer vorgeben darf, in °C."
         },
         "quiet_silent_windows": {
diff --git a/custom_components/heatpump_optimizer/translations/en.json b/custom_components/heatpump_optimizer/translations/en.json
index a0f688cfbe..4bc15c7641 100644
--- a/custom_components/heatpump_optimizer/translations/en.json
+++ b/custom_components/heatpump_optimizer/translations/en.json
@@ -593,12 +593,12 @@
               "indoor_temp_entity": "Optional. The actual room temperature. Without it the optimizer trusts its own model, which drifts over time.",
               "outdoor_temp_entity": "Optional. A local outdoor thermometer is more accurate than the forecast for the current hour.",
               "space_setpoint_entity": "Optional. A number, helper or climate entity that is the pump's space-heating set-point. With Pump duty control at Control the optimizer writes it on every plan step, as Pump duty control describes, and turning Optimizer active off writes back the value it read before its first write. With Pump duty control at Off or Observe it is only read, to notice when it cannot be read.",
-              "space_setpoint_unit": "Indoor temperature is correct for a room or thermostat set-point. Flow temperature is for a controller whose set-point is a water temperature it holds its supply at. Return temperature is for a controller that takes the set-point as its return-water target (assumed for a Luxtronik through its Smart Home Interface); it is written like a flow set-point, with the rated hold, the weather curve and the 25 °C gate moved 5 K down to return terms. A version before this option reads Return temperature as Indoor temperature: switch it back to Flow temperature before downgrading. Pointing an indoor target at a flow entity would command roughly 21 °C to something expecting 35–45 °C and badly underheat the house. The unit is a declaration: the optimizer never infers it from the entity, and only the heat-pump pre-fill suggests one. With Pump duty control at Control the optimizer writes the plan's room temperature (Indoor temperature) or water temperature (Flow temperature, Return temperature) to this entity.",
+              "space_setpoint_unit": "Indoor temperature is correct for a room or thermostat set-point. Flow temperature is for a controller whose set-point is a water temperature it holds its supply at. Return temperature is for a controller that takes the set-point as its return-water target (a Luxtronik through its Smart Home Interface, for example, is assumed to be one); it is written like a flow set-point, with the rated hold, the weather curve and the 25 °C gate moved 5 K down to return terms. A version before this option reads Return temperature as Indoor temperature: switch it back to Flow temperature before downgrading. Pointing an indoor target at a flow entity would command roughly 21 °C to something expecting 35–45 °C and badly underheat the house. The unit is a declaration: the optimizer never infers it from the entity, and only the heat-pump pre-fill suggests one. With Pump duty control at Control the optimizer writes the plan's room temperature (Indoor temperature) or water temperature (Flow temperature, Return temperature) to this entity.",
               "flow_min_lift_k": "With Pump duty control at Control, the water set-point written at the plan's lowest power is the measured inlet water plus this: heat-pump return, buffer tank, floor return or valve outlet, and for a Return temperature entity the first three only. 5 K suits a controller that holds its supply at the set-point. A controller that takes the number as its return-water target is assumed to run its compressor harder the further the target sits above the return, so it likely wants less; 1–2 K is a starting point to check against the compressor's measured frequency and power, not a measured value.",
               "flow_heat_c": "The water set-point written at full planned power, and the highest one written while the plan is in charge. 55 °C suits a supply target. For a Return temperature entity choose it above the highest return you see in normal heating plus the lift, and no higher than the controller accepts; on a low-temperature floor heating 35–40 °C may be a starting point to check against measurements. Below 30 °C is not offered: the gate that means off is 25 °C for a flow target and 20 °C for a return target. A space boost or Boost mode writes the set-point entity's own maximum (up to 70 °C) on every step instead; a value other than 55 °C set here caps that too, so set one on a low-temperature floor heating.",
-              "space_setpoint_power_feedback": "On by default. Acts only with Pump duty control at Control, a Flow or Return temperature unit and a heat-pump power sensor; otherwise nothing changes. After a 5-minute start hold, the water set-point is nudged down while the measured draw is above the planned level and up while it is below, and held while it is within 10 %, instead of following the rising inlet water. Off writes the inlet plus the lift. Requirements on the controller: its heating hysteresis at most the lift (Luxtronik: 0.5 K), or a stopped compressor is not started; its minimum return target below the heating-season return; its integration polling it at least every 10 minutes, and restoring its heating mode after a controller restart, since a Luxtronik Smart Home Interface drops every set value after 600 s without access; and no second tool writing the same registers (a Luxtronik then silently discards writes).",
-              "space_setpoint_low_limit_entity": "Optional. A temperature sensor that reports the lowest value the controller accepts for the set-point entity above (a Luxtronik through ha-luxtronik-shi: \"Temperature: return target minimum\", input 10104). With it, Follow the planned power never sends a value below it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes.",
-              "space_setpoint_high_limit_entity": "Optional. A temperature sensor that reports the highest value the controller accepts for the set-point entity above (a Luxtronik through ha-luxtronik-shi: \"Temperature: return limit\", input 10103). With it, Follow the planned power never sends a value above it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes."
+              "space_setpoint_power_feedback": "On by default. Acts only with Pump duty control at Control, a Flow or Return temperature unit and a heat-pump power sensor; otherwise nothing changes. After a 5-minute start hold, the water set-point is nudged down while the measured draw is above the planned level and up while it is below, and held while it is within 10 %, instead of following the rising inlet water. Off writes the inlet plus the lift. Requirements on the controller: its heating hysteresis at most the lift (0.5 K on a Luxtronik, for example), or a stopped compressor is not started; its minimum return target below the heating-season return; its integration polling it at least every 10 minutes, and restoring its heating mode after a controller restart, since a controller can drop what was set when it goes unread (a Luxtronik Smart Home Interface, for one, drops every set value after 600 s without access); and no second tool writing the same registers (a Luxtronik, for one, then silently discards writes).",
+              "space_setpoint_low_limit_entity": "Optional. A temperature sensor that reports the lowest value the controller accepts for the set-point entity above (for example a Luxtronik through ha-luxtronik-shi: \"Temperature: return target minimum\", input 10104). With it, Follow the planned power never sends a value below it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes.",
+              "space_setpoint_high_limit_entity": "Optional. A temperature sensor that reports the highest value the controller accepts for the set-point entity above (for example a Luxtronik through ha-luxtronik-shi: \"Temperature: return limit\", input 10103). With it, Follow the planned power never sends a value above it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes."
             }
           },
           "plant": {
@@ -941,7 +941,7 @@
       },
       "heat_curve": {
         "title": "Heat curve control",
-        "description": "Shifts the heat curve up in cheap hours and down in expensive ones, through a Danfoss ECL110 over MQTT, a number entity that offsets your controller's curve, or both. Leave the topics and the entity empty if you have neither.",
+        "description": "Shifts your controller's heat curve up in cheap hours and down in expensive ones, three ways: over MQTT topics, to a controller that takes its offset there (a Danfoss ECL110 through an MQTT bridge, for example); to a number entity that offsets the curve; or to a curve setting the controller stores. The topics and the entity can be used together. Leave them all empty if your controller has none of these.",
         "data": {
           "ecl110_displace_set_topic": "Offset command topic",
           "ecl110_command_topic": "Legacy JSON command topic",
@@ -960,7 +960,7 @@
           "after_save": "After saving"
         },
         "data_description": {
-          "ecl110_displace_set_topic": "MQTT topic the parallel heat-curve offset is published to. Nothing is published while this and the legacy command topic below are empty: leave them empty if you do not have a Danfoss ECL110.",
+          "ecl110_displace_set_topic": "MQTT topic the parallel heat-curve offset is published to. Nothing is published while this and the legacy command topic below are empty: leave them empty if your controller does not take its offset over MQTT (a Danfoss ECL110 through an MQTT bridge is one that does).",
           "ecl110_command_topic": "Only needed for older setups that expect a JSON payload instead.",
           "ecl110_state_topic": "MQTT topic the controller reports its current state on.",
           "ecl110_mqtt_qos": "0 is fine for almost everyone.",
@@ -970,8 +970,8 @@
           "ecl110_pid_time_constant_hours": "Roughly how long the controller takes to act on a new offset. Used so the optimizer does not ask for changes faster than the system can follow.",
           "heat_curve_displace_entity": "A number entity that shifts your controller's heat curve. Kind offset: a whole-curve offset, 0 meaning no shift, that the controller forgets on a restart (for example a Luxtronik SHI heating offset); turning the optimizer off, or unloading it, writes 0. Kind persistent: a curve setting the controller stores; turning the optimizer off, or unloading it, writes back the value it held before the first write.",
           "heat_curve_target_kind": "Offset: a temperature difference, 0 neutral, not stored by the controller. Prefer it wherever your controller has one. Persistent: a curve setting the controller stores, displaced from its own value and written back on off; every write wears the controller's memory, so writes are limited per day.",
-          "heat_curve_offset_band_k": "The offset written to the entity stays within this many kelvin either way. 3 K is an estimate between a +1 to +2 step SG-Ready boost and Luxtronik's own ±5 K correction.",
-          "heat_curve_persistent_band_k": "The stored setting is moved at most this many kelvin either way from the value it held before the first write. 3 K is an estimate between a +1 to +2 step SG-Ready boost and Luxtronik's own ±5 K correction.",
+          "heat_curve_offset_band_k": "The offset written to the entity stays within this many kelvin either way. 3 K is an estimate between a +1 to +2 step SG-Ready boost and the ±5 K user correction one controller offers (Luxtronik's).",
+          "heat_curve_persistent_band_k": "The stored setting is moved at most this many kelvin either way from the value it held before the first write. 3 K is an estimate between a +1 to +2 step SG-Ready boost and the ±5 K user correction one controller offers (Luxtronik's).",
           "heat_curve_persistent_writes_per_day": "Writes in one local day, the write back on off included; one is always kept for it. 12 (six shift-and-return episodes) stays under the one documented manufacturer quota found (Daikin, 7000 a year); the margin below it is an estimate. 0 or 1 writes nothing. Above 19 exceeds that quota.",
           "heat_curve_persistent_min_dwell_minutes": "After a write, the next waits at least this long. 60 minutes is about three response times of a radiator system (a forum estimate); a slow floor may want 2 to 3 hours.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
@@ -1274,7 +1274,7 @@
         "data_description": {
           "heat_pump_mode_entity": "Optional. The pump's own mode selector - cooling, heating, hot water, or a combination of two. Read only, unless Pump duty control is set to Control. A pump in a cooling or hot-water-only mode cannot heat the house, and one in a heating-only mode cannot make hot water, so without this the plan can promise heat the pump is not currently able to deliver. Left empty, the optimizer assumes the pump can do everything.",
           "pump_duty_mode": "Off (the default) never writes the pump's operating mode or set-points. Observe writes none either and keeps a 24-hour ledger, in the diagnostics, of the duty each plan step asked for against what the pump did (from the power entity, the mode and the tank temperature). With any of the three, the heat pump on/off switch, if you have set one, is still switched by the plan. Control writes the operating mode above (hot water only on hot-water-only steps, heating only on space-heating-only steps, unchanged on idle steps; on a step that plans both, hot water only for the hot-water share of the step and then heating, a share under 5 minutes going to the other duty; Heating + DHW while a boost or an anti-legionella cycle calls for both, and whenever the plan is not in charge), the hot water set-point entity (the hot water set-point configured on the hot water page, or the anti-legionella temperature during a cycle) and the space set-point entity (for a flow set-point, a target that follows the planned power — the heating flow (55 °C, or the Heating flow ceiling) at full power, toward 5 °C (or the Minimum lift above the inlet water) above the first fresh reading of the heat-pump return, buffer tank, floor return or valve outlet (35 °C when none is configured) at the modulation floor — on steps that heat the house, 25 °C on steps that do not (20 °C for a Return temperature set-point, or the entity's own minimum if that is higher), and 35 °C or the weather curve, whichever is higher, when the plan is not in charge; for an indoor one, the planned room temperature). Where the mode offers no single-duty option, as on the GCHV Modbus package, the other duty's set-point is lowered instead: the hot water one to 30 °C, a flow set-point to the same 25 °C (20 °C for Return temperature), an indoor one to 5 °C, each never below the entity's own minimum. A hot-water-only stretch is capped at 90 minutes (30 below -10 °C outdoors), unless the room is already at its planned temperature. Where Capacity limited (night mode) is a switch and silent windows are scheduled, Control also holds that switch on inside a silent window and off outside one. While Optimizer active is on, any change to those entities the optimizer did not make is written back at once; turn Optimizer active off to change the pump by hand. A value the pump does not hold raises a warning and is sent again every 5 minutes.",
-          "space_hysteresis_entity": "Optional. A sensor or number holding the pump's own heating start hysteresis as a temperature difference in K (°C reads the same, °F is scaled; 0 to 20 K): its controller starts heating only once the target sits that far above the water. On a flow or return set-point the lift written above the measured water at the lowest planned level is then never smaller than it, so a planned heating step is one the pump starts. A controller that publishes only the start threshold itself (a Luxtronik's Demand border, input 10107) needs a template sensor of the return target minus that threshold. Left empty or unreadable, the configured lift stands.",
+          "space_hysteresis_entity": "Optional. A sensor or number holding the pump's own heating start hysteresis as a temperature difference in K (°C reads the same, °F is scaled; 0 to 20 K): its controller starts heating only once the target sits that far above the water. On a flow or return set-point the lift written above the measured water at the lowest planned level is then never smaller than it, so a planned heating step is one the pump starts. A controller that publishes only the start threshold itself (a Luxtronik's Demand border, input 10107, for example) needs a template sensor of the return target minus that threshold. Left empty or unreadable, the configured lift stands.",
           "dhw_hysteresis_entity": "Optional. A sensor or number holding the pump's own hot water start hysteresis as a temperature difference in K (°C reads the same, °F is scaled; 0 to 20 K): the pump starts a charge only once the tank is below the hot water target minus this. The plan then places no charge on a tank warmer than that (a charge planned for the current step is kept, as it may already be running; a disinfection charge is judged against the disinfection temperature), and the duty ledger marks an idle hot water step on such a tank not-startable instead of idle-instead. A hot water minimum above that start temperature cannot be held by the pump and raises a warning. Left empty, unreadable or 0, every planned charge is taken to start.",
           "heat_pump_defrost_entity": "Optional. On while the pump reverses to melt frost off the outdoor coil. The electricity bought during a defrost goes into the coil rather than into the house. Note that many pumps are only polled every few minutes, so short defrosts are missed entirely: this is a sample of defrost activity, not a stopwatch.",
           "heat_pump_online_entity": "Optional, and strongly recommended for a cloud-connected pump. On while the pump is actually reachable. A cloud integration can keep republishing its last known readings while the pump itself has dropped off the network, which leaves every other sensor looking perfectly fresh; this is the one signal that says otherwise. On a local (LAN) connection the sensors go unavailable by themselves and this adds little.",
@@ -1407,7 +1407,7 @@
         },
         "data_description": {
           "dso_product": "A dated Sweden-only table. Selecting a product writes transfer-fee rules and peak-tariff fields you can still edit, switches the transfer fee to Time-of-use rules and turns the peak tariff on. Verify against your bill: a product keeps writing its values after its end date. A product the table does not know writes nothing.",
-          "grid_fee_mode": "The fee your grid company adds per kWh transferred. Tibber's price does not include it, so with it configured the plan finally sees the whole marginal price. \"Time-of-use rules\" uses the schedule below; \"Live sensor\" follows an entity.",
+          "grid_fee_mode": "The fee your grid company adds per kWh transferred. Tibber's price does not include it, and a price sensor includes it only if you added it there yourself, so with it configured the plan sees the whole marginal price. \"Time-of-use rules\" uses the schedule below; \"Live sensor\" follows an entity.",
           "grid_fee_fixed": "A flat fee added in every hour, on top of the time-of-use rules or the live sensor's value. It only applies when Grid transfer fee is Time-of-use rules or Live sensor; with None it is ignored. Take it from your grid invoice.",
           "grid_fee_rules": "One rule per line, for example \"Nov-Mar Mon-Fri 06:00-22:00 = 0.25\". Month, weekday and time parts are each optional; overlapping rules add together, which matches a base fee plus a high-load surcharge. A comma between digits is a decimal separator, so \"0,25\" reads as 0.25 and never splits a rule.",
           "grid_fee_entity": "A sensor reporting the current fee in {currency}/kWh, for grids with dynamic fees. Its value is added to every planned hour.",
@@ -1519,7 +1519,7 @@
       },
       "modbus_prefill": {
         "title": "Pre-fill from a heat pump device",
-        "description": "For a Rotenso Windmi or another GCHV-built heat pump, read through the tuya_heat_pump project's Modbus package or through the pump's own Home Assistant device. Pick the device, or leave it empty and name the package's entity prefix, and submit: the next form suggests values read from the pump - the hot water set-points and schedule, the anti-legionella days, the night mode schedule, the pump's maximum electrical power (from its unit capacity), whether the pump steers on water temperature, and the pump's own sensors for sensor slots that are still empty. Edit or clear any of them; only what you keep is saved, and a field you clear is left as it was. Nothing about the house or its heating system can be read this way.\n\nEntities read: {found}. Backup heater type register: {backup_heater_type} - any value but 7 means the pump has electric heat of its own, which the heater slots on Heat pump telemetry are there to watch.\n\nRoles read from an entity's NAME rather than from a published definition - the page cannot verify those, so check each before saving: {name_matched}. Roles read from published definitions, by source: {matched_sources}.",
+        "description": "Reads only what this page has a mapping for: a GCHV-built heat pump (a Rotenso Windmi, for example) through the tuya_heat_pump project's Modbus package, or a heat pump's own Home Assistant device, through its integration's published definitions where one is mapped here and otherwise by its entities' names. Pick the device, or leave it empty and name the package's entity prefix, and submit: the next form suggests values read from the pump - the hot water set-points and schedule, the anti-legionella days, the night mode schedule, the pump's maximum electrical power (from its unit capacity), whether the pump steers on water temperature, and the pump's own sensors for sensor slots that are still empty. Edit or clear any of them; only what you keep is saved, and a field you clear is left as it was. Nothing about the house or its heating system can be read this way.\n\nEntities read: {found}. Backup heater type register: {backup_heater_type} - any value but 7 means the pump has electric heat of its own, which the heater slots on Heat pump telemetry are there to watch.\n\nRoles read from an entity's NAME rather than from a published definition - the page cannot verify those, so check each before saving: {name_matched}. Roles read from published definitions, by source: {matched_sources}.",
         "data": {
           "prefill_device": "Heat pump device (optional)",
           "modbus_prefill_prefix": "Modbus package entity prefix",
@@ -1988,10 +1988,10 @@
         "name": "DHW Temperature"
       },
       "ecl110_displace": {
-        "name": "ECL110 Displace"
+        "name": "Heat-Curve Displace"
       },
       "ecl110_effective_displace": {
-        "name": "ECL110 Effective Displace"
+        "name": "Heat-Curve Effective Displace"
       },
       "floor_heating_return_temperature": {
         "name": "Floor Heating Return Temperature"
@@ -2382,15 +2382,15 @@
           "description": "Heat loss multiplier when raining. 1.15 means 15% more heat loss in rain of 2 mm/h or more (wet building envelope effect); lighter rain scales it down in proportion, and 0.1 mm/h or less applies none of it."
         },
         "ecl110_pid_time_constant_hours": {
-          "name": "ECL110 PI/PID Time Constant",
-          "description": "Time constant (hours) for the ECL110 PI/PID response approximation. Lower values react faster, higher values are smoother."
+          "name": "Heat-Curve Controller Time Constant",
+          "description": "Time constant (hours) for the heat-curve controller's PI/PID response approximation. Lower values react faster, higher values are smoother."
         },
         "ecl110_displace_min": {
-          "name": "ECL110 displace minimum",
+          "name": "Heat-curve displace minimum",
           "description": "Lowest parallel shift the optimizer may command, in °C."
         },
         "ecl110_displace_max": {
-          "name": "ECL110 displace maximum",
+          "name": "Heat-curve displace maximum",
           "description": "Highest parallel shift the optimizer may command, in °C."
         },
         "quiet_silent_windows": {
diff --git a/custom_components/heatpump_optimizer/translations/sv.json b/custom_components/heatpump_optimizer/translations/sv.json
index 47b1ff7bce..4cd820ad7e 100644
--- a/custom_components/heatpump_optimizer/translations/sv.json
+++ b/custom_components/heatpump_optimizer/translations/sv.json
@@ -593,12 +593,12 @@
               "indoor_temp_entity": "Valfritt. Den verkliga rumstemperaturen. Utan den litar optimeringen på sin egen modell, som glider med tiden.",
               "outdoor_temp_entity": "Valfritt. En egen utegivare är mer exakt än prognosen för den aktuella timmen.",
               "space_setpoint_entity": "Valfritt. En number-, helper- eller climate-enhet som är pumpens börvärde för rumsuppvärmning. Med Styrning av pumpens uppgift satt till Styrning skriver optimeraren det vid varje plansteg, som Styrning av pumpens uppgift beskriver, och när Optimeraren aktiv stängs av skrivs värdet tillbaka som enheten visade före den första skrivningen. Med Av eller Observera läses det bara, för att märka när det inte går att läsa.",
-              "space_setpoint_unit": "Inomhustemperatur är rätt för ett rums- eller termostatbörvärde. Framledningstemperatur är för en styrenhet vars börvärde är en vattentemperatur som den håller framledningen på. Returtemperatur är för en styrenhet som tar börvärdet som mål för returvattnet (antaget för en Luxtronik via dess Smart Home Interface); den skrivs som ett framledningsbörvärde, med det nominella hållvärdet, värmekurvan och grinden på 25 °C flyttade 5 K ned till returnivå. En version från före det här valet läser Returtemperatur som Inomhustemperatur: byt tillbaka till Framledningstemperatur innan du nedgraderar. Att peka ett inomhusmål mot en framledningsentitet skulle kommendera ungefär 21 °C till något som förväntar sig 35–45 °C och undervärma huset kraftigt. Enheten är en deklaration: optimeraren härleder den aldrig från entiteten, och bara förifyllningen från en värmepumpsenhet föreslår en. Med Styrning av pumpens uppgift på Styrning skriver optimeraren planens rumstemperatur (Inomhustemperatur) eller vattentemperatur (Framledningstemperatur, Returtemperatur) till den här entiteten.",
+              "space_setpoint_unit": "Inomhustemperatur är rätt för ett rums- eller termostatbörvärde. Framledningstemperatur är för en styrenhet vars börvärde är en vattentemperatur som den håller framledningen på. Returtemperatur är för en styrenhet som tar börvärdet som mål för returvattnet (antaget till exempel för en Luxtronik via dess Smart Home Interface); den skrivs som ett framledningsbörvärde, med det nominella hållvärdet, värmekurvan och grinden på 25 °C flyttade 5 K ned till returnivå. En version från före det här valet läser Returtemperatur som Inomhustemperatur: byt tillbaka till Framledningstemperatur innan du nedgraderar. Att peka ett inomhusmål mot en framledningsentitet skulle kommendera ungefär 21 °C till något som förväntar sig 35–45 °C och undervärma huset kraftigt. Enheten är en deklaration: optimeraren härleder den aldrig från entiteten, och bara förifyllningen från en värmepumpsenhet föreslår en. Med Styrning av pumpens uppgift på Styrning skriver optimeraren planens rumstemperatur (Inomhustemperatur) eller vattentemperatur (Framledningstemperatur, Returtemperatur) till den här entiteten.",
               "flow_min_lift_k": "Med Styrning av pumpens uppgift på Styrning skrivs vattenbörvärdet vid planens lägsta effekt som det uppmätta inkommande vattnet plus detta: värmepumpens retur, bufferttank, golvretur eller ventilens utlopp, och för en entitet med Returtemperatur bara de tre första. 5 K passar en styrenhet som håller sin framledning på börvärdet. En styrenhet som tar börvärdet som mål för returvattnet antas köra kompressorn hårdare ju högre målet ligger över returen och vill troligen ha mindre; 1–2 K är en startpunkt att kontrollera mot kompressorns uppmätta frekvens och effekt, inte ett uppmätt värde.",
               "flow_heat_c": "Vattenbörvärdet som skrivs vid full planerad effekt, och det högsta som skrivs medan planen styr. 55 °C passar ett framledningsmål. För en entitet med Returtemperatur väljs det över den högsta retur du ser vid normal uppvärmning plus höjningen, och inte högre än styrenheten accepterar; för en lågtemperatur-golvvärme kan 35–40 °C vara en startpunkt att kontrollera mot mätningar. Under 30 °C erbjuds inte: grinden som betyder av är 25 °C för ett framledningsmål och 20 °C för ett returmål. En rumsvärmeboost eller Boost-läget skriver i stället börvärdesentitetens eget maximum (högst 70 °C) vid varje steg; ett annat värde än 55 °C här begränsar även det, så ange ett för en lågtemperatur-golvvärme.",
-              "space_setpoint_power_feedback": "På som standard. Verkar bara med Styrning av pumpens uppgift på Styrning, enheten Framlednings- eller Returtemperatur och en effektgivare för värmepumpen; annars ändras ingenting. Efter 5 minuters starthållning sänks vattenbörvärdet medan den uppmätta förbrukningen ligger över planerad nivå, höjs medan den ligger under och hålls inom 10 %, i stället för att följa det stigande inkommande vattnet. Av skriver inkommande vatten plus höjningen. Krav på styrenheten: dess värmehysteres högst höjningen (Luxtronik: 0,5 K), annars startas inte en stoppad kompressor; dess lägsta returmål under returen under eldningssäsongen; dess integration läser den minst var 10:e minut och återställer värmeläget efter en omstart av styrenheten, eftersom ett Luxtronik Smart Home Interface släpper alla satta värden efter 600 s utan åtkomst; och inget annat verktyg skriver samma register (en Luxtronik kastar då skrivningar tyst).",
-              "space_setpoint_low_limit_entity": "Valfri. En temperaturgivare som rapporterar det lägsta värde styrenheten tar emot för börvärdesentiteten ovan (en Luxtronik via ha-luxtronik-shi: \"Temperature: return target minimum\", ingång 10104). Med den skickar Följ planerad effekt efter uppmätt förbrukning aldrig ett värde under det, i stället för att hitta gränsen först när styrenheten kapar en skrivning. Används bara av det alternativet; lämnas den tom ändras ingenting.",
-              "space_setpoint_high_limit_entity": "Valfri. En temperaturgivare som rapporterar det högsta värde styrenheten tar emot för börvärdesentiteten ovan (en Luxtronik via ha-luxtronik-shi: \"Temperature: return limit\", ingång 10103). Med den skickar Följ planerad effekt efter uppmätt förbrukning aldrig ett värde över det, i stället för att hitta gränsen först när styrenheten kapar en skrivning. Används bara av det alternativet; lämnas den tom ändras ingenting."
+              "space_setpoint_power_feedback": "På som standard. Verkar bara med Styrning av pumpens uppgift på Styrning, enheten Framlednings- eller Returtemperatur och en effektgivare för värmepumpen; annars ändras ingenting. Efter 5 minuters starthållning sänks vattenbörvärdet medan den uppmätta förbrukningen ligger över planerad nivå, höjs medan den ligger under och hålls inom 10 %, i stället för att följa det stigande inkommande vattnet. Av skriver inkommande vatten plus höjningen. Krav på styrenheten: dess värmehysteres högst höjningen (0,5 K på till exempel en Luxtronik), annars startas inte en stoppad kompressor; dess lägsta returmål under returen under eldningssäsongen; dess integration läser den minst var 10:e minut och återställer värmeläget efter en omstart av styrenheten, eftersom en styrenhet kan släppa det som satts när den inte läses (ett Luxtronik Smart Home Interface till exempel släpper alla satta värden efter 600 s utan åtkomst); och inget annat verktyg skriver samma register (en Luxtronik till exempel kastar då skrivningar tyst).",
+              "space_setpoint_low_limit_entity": "Valfri. En temperaturgivare som rapporterar det lägsta värde styrenheten tar emot för börvärdesentiteten ovan (till exempel en Luxtronik via ha-luxtronik-shi: \"Temperature: return target minimum\", ingång 10104). Med den skickar Följ planerad effekt efter uppmätt förbrukning aldrig ett värde under det, i stället för att hitta gränsen först när styrenheten kapar en skrivning. Används bara av det alternativet; lämnas den tom ändras ingenting.",
+              "space_setpoint_high_limit_entity": "Valfri. En temperaturgivare som rapporterar det högsta värde styrenheten tar emot för börvärdesentiteten ovan (till exempel en Luxtronik via ha-luxtronik-shi: \"Temperature: return limit\", ingång 10103). Med den skickar Följ planerad effekt efter uppmätt förbrukning aldrig ett värde över det, i stället för att hitta gränsen först när styrenheten kapar en skrivning. Används bara av det alternativet; lämnas den tom ändras ingenting."
             }
           },
           "plant": {
@@ -941,7 +941,7 @@
       },
       "heat_curve": {
         "title": "Värmekurvestyrning",
-        "description": "Förskjuter värmekurvan uppåt under billiga timmar och nedåt under dyra, via en Danfoss ECL110 över MQTT, en nummerentitet som förskjuter styrningens kurva, eller båda. Lämna ämnena och entiteten tomma om du inte har någon av dem.",
+        "description": "Förskjuter styrningens värmekurva uppåt under billiga timmar och nedåt under dyra, på tre sätt: via MQTT-topics till en styrning som tar emot sin förskjutning där (till exempel en Danfoss ECL110 via en MQTT-brygga); till en nummerentitet som förskjuter kurvan; eller till en kurvinställning som styrningen lagrar. Topics och entitet kan användas tillsammans. Lämna allt tomt om styrningen inte har något av detta.",
         "data": {
           "ecl110_displace_set_topic": "Topic för förskjutningskommando",
           "ecl110_command_topic": "Äldre JSON-kommandotopic",
@@ -960,7 +960,7 @@
           "after_save": "Efter sparande"
         },
         "data_description": {
-          "ecl110_displace_set_topic": "MQTT-topic dit parallellförskjutningen av värmekurvan publiceras. Inget publiceras så länge detta fält och den äldre kommandotopicen nedan är tomma: lämna dem tomma om du inte har en Danfoss ECL110.",
+          "ecl110_displace_set_topic": "MQTT-topic dit parallellförskjutningen av värmekurvan publiceras. Inget publiceras så länge detta fält och den äldre kommandotopicen nedan är tomma: lämna dem tomma om styrningen inte tar emot sin förskjutning över MQTT (en Danfoss ECL110 via en MQTT-brygga gör det).",
           "ecl110_command_topic": "Behövs bara för äldre installationer som förväntar sig JSON i stället.",
           "ecl110_state_topic": "MQTT-topic där regulatorn rapporterar sitt tillstånd.",
           "ecl110_mqtt_qos": "0 räcker för de allra flesta.",
@@ -970,8 +970,8 @@
           "ecl110_pid_time_constant_hours": "Ungefär hur lång tid regulatorn behöver för att verkställa en ny förskjutning. Används så att optimeringen inte begär snabbare ändringar än systemet hinner följa.",
           "heat_curve_displace_entity": "En nummerentitet som förskjuter styrningens värmekurva. Typen förskjutning: en förskjutning av hela kurvan, där 0 betyder ingen förskjutning, som styrningen glömmer vid en omstart (till exempel en Luxtronik SHI-värmeförskjutning); när optimeraren stängs av eller avlastas skrivs 0. Typen beständig: en kurvinställning som styrningen lagrar; när optimeraren stängs av eller avlastas skrivs värdet tillbaka som den hade före den första skrivningen.",
           "heat_curve_target_kind": "Förskjutning: en temperaturskillnad, 0 neutral, lagras inte av styrningen. Välj den där styrningen har en. Beständig: en kurvinställning som styrningen lagrar, förskjuten från sitt eget värde och återställd vid avstängning; varje skrivning sliter på styrningens minne, så skrivningarna begränsas per dygn.",
-          "heat_curve_offset_band_k": "Förskjutningen som skrivs till entiteten håller sig inom så här många kelvin åt båda hållen. 3 K är en uppskattning mellan en SG-Ready-höjning på +1 till +2 steg och Luxtronik egen korrigering på ±5 K.",
-          "heat_curve_persistent_band_k": "Den lagrade inställningen flyttas högst så här många kelvin åt båda hållen från värdet den hade före den första skrivningen. 3 K är en uppskattning mellan en SG-Ready-höjning på +1 till +2 steg och Luxtronik egen korrigering på ±5 K.",
+          "heat_curve_offset_band_k": "Förskjutningen som skrivs till entiteten håller sig inom så här många kelvin åt båda hållen. 3 K är en uppskattning mellan en SG-Ready-höjning på +1 till +2 steg och den användarkorrigering på ±5 K som en styrning erbjuder (Luxtroniks).",
+          "heat_curve_persistent_band_k": "Den lagrade inställningen flyttas högst så här många kelvin åt båda hållen från värdet den hade före den första skrivningen. 3 K är en uppskattning mellan en SG-Ready-höjning på +1 till +2 steg och den användarkorrigering på ±5 K som en styrning erbjuder (Luxtroniks).",
           "heat_curve_persistent_writes_per_day": "Skrivningar under ett lokalt dygn, återställningen vid avstängning inräknad; en hålls alltid kvar för den. 12 (sex förskjutningar med återgång) ligger under den enda dokumenterade tillverkarkvot som hittats (Daikin, 7000 per år); marginalen under den är en uppskattning. 0 eller 1 skriver ingenting. Över 19 överskrider kvoten.",
           "heat_curve_persistent_min_dwell_minutes": "Efter en skrivning väntar nästa minst så här länge. 60 minuter är ungefär tre svarstider för ett radiatorsystem (en uppskattning från ett forum); ett trögt golv kan behöva 2 till 3 timmar.",
           "after_save": "Sparandet slår igenom direkt; detta val avgör vart dialogen går näst."
@@ -1274,7 +1274,7 @@
         "data_description": {
           "heat_pump_mode_entity": "Valfritt. Pumpens eget lägesval - kyla, värme, varmvatten eller en kombination av två. Läses bara av, om inte Styrning av pumpens uppgift står på Styrning. En pump som står i kylläge eller enbart varmvatten kan inte värma huset, och en som står i enbart värmeläge kan inte göra varmvatten. Utan det här kan planen alltså lova värme som pumpen just då inte kan leverera. Lämnas fältet tomt antar optimeringen att pumpen klarar allt.",
           "pump_duty_mode": "Av (standard) skriver aldrig pumpens driftläge eller börvärden. Observera skriver inte heller något och för en 24-timmarslogg, i diagnostiken, över vilken uppgift varje planerat steg bad om och vad pumpen gjorde (från effektentiteten, driftläget och tanktemperaturen). Med något av de tre styrs strömbrytaren för värmepumpen, om du har ställt in en, ändå av planen. Styrning skriver driftläget ovan (bara varmvatten på steg med bara varmvatten, bara värme på steg med bara rumsvärme, oförändrat på vilande steg; på ett steg som planerar båda bara varmvatten under stegets varmvattendel och sedan värme, där en andel under 5 minuter går till den andra uppgiften; Värme + varmvatten medan en boost eller en legionellacykel kräver båda, och närhelst planen inte styr), varmvattnets börvärdesentitet (varmvattnets börvärde från varmvattensidan, eller legionellatemperaturen under en cykel) och rumsvärmens börvärdesentitet (för ett framledningsbörvärde ett mål som följer den planerade effekten — värmeframledningen (55 °C, eller Högsta framledning vid värme) vid full effekt, mot 5 °C (eller Minsta höjning över inkommande vatten) över den första färska avläsningen av värmepumpens retur, ackumulatortanken, golvreturen eller ventilens utlopp (35 °C när ingen är inställd) vid moduleringsgolvet — på steg som värmer huset, 25 °C på steg som inte gör det (20 °C för ett Returtemperatur-börvärde, eller entitetens eget minimum om det är högre), och 35 °C eller värmekurvan, det som är högst, när planen inte styr; för ett inomhusbörvärde den planerade rumstemperaturen). Där driftläget saknar ett läge för bara en uppgift, som i GCHV Modbus-paketet, sänks i stället den andra uppgiftens börvärde: varmvattnets till 30 °C, ett framledningsbörvärde till samma 25 °C (20 °C för Returtemperatur), ett inomhusbörvärde till 5 °C, aldrig under entitetens eget minimum. En sträcka med bara varmvatten begränsas till 90 minuter (30 under -10 °C ute), om inte rummet redan har sin planerade temperatur. Där Begränsad effekt (nattläge) är en brytare och tysta tidsfönster är schemalagda håller Styrning också den brytaren på inom ett tyst fönster och av utanför ett. Medan Optimeraren aktiv är på skrivs varje ändring av entiteterna som optimeraren inte gjorde tillbaka direkt; stäng av Optimeraren aktiv för att ändra pumpen för hand. Ett värde som pumpen inte behåller ger en varning och skickas igen var 5:e minut.",
-          "space_hysteresis_entity": "Valfritt. En sensor eller ett tal med pumpens egen starthysteres för uppvärmning som temperaturskillnad i K (°C läses likadant, °F räknas om; 0 till 20 K): dess styrning börjar värma först när målet ligger så mycket över vattnet. För ett framlednings- eller returbörvärde blir lyftet över det uppmätta vattnet på den lägsta planerade nivån då aldrig mindre, så ett planerat värmesteg är ett som pumpen startar. En styrning som bara publicerar själva startgränsen (en Luxtroniks Demand border, ingång 10107) behöver en mallsensor av returmålet minus den gränsen. Lämnas fältet tomt eller oläsbart gäller det konfigurerade lyftet.",
+          "space_hysteresis_entity": "Valfritt. En sensor eller ett tal med pumpens egen starthysteres för uppvärmning som temperaturskillnad i K (°C läses likadant, °F räknas om; 0 till 20 K): dess styrning börjar värma först när målet ligger så mycket över vattnet. För ett framlednings- eller returbörvärde blir lyftet över det uppmätta vattnet på den lägsta planerade nivån då aldrig mindre, så ett planerat värmesteg är ett som pumpen startar. En styrning som bara publicerar själva startgränsen (till exempel en Luxtroniks Demand border, ingång 10107) behöver en mallsensor av returmålet minus den gränsen. Lämnas fältet tomt eller oläsbart gäller det konfigurerade lyftet.",
           "dhw_hysteresis_entity": "Valfritt. En sensor eller ett tal med pumpens egen starthysteres för varmvatten som temperaturskillnad i K (°C läses likadant, °F räknas om; 0 till 20 K): pumpen startar en laddning först när tanken ligger under varmvattenbörvärdet minus detta. Planen lägger då ingen laddning på en varmare tank (en laddning som planerats för det aktuella steget behålls, eftersom den kan redan pågå; en desinfektionsladdning bedöms mot desinfektionstemperaturen), och pumploggen märker ett vilande varmvattensteg på en sådan tank not-startable i stället för idle-instead. Ett varmvattenminimum över den starttemperaturen kan pumpen inte hålla och ger en varning. Lämnas fältet tomt, oläsbart eller 0 antas varje planerad laddning starta.",
           "heat_pump_defrost_entity": "Valfritt. På medan pumpen vänder cykeln för att smälta bort frost från utomhusbatteriet. Elen som köps under en avfrostning går till batteriet i stället för in i huset. Tänk på att många pumpar bara avfrågas med några minuters mellanrum, så korta avfrostningar missas helt: det här är ett stickprov på avfrostning, inte ett tidtagarur.",
           "heat_pump_online_entity": "Valfritt, men varmt rekommenderat för en molnansluten pump. På medan pumpen faktiskt går att nå. En molnintegration kan fortsätta publicera sina senast kända värden medan pumpen själv har tappat nätverket, vilket får alla andra givare att se alldeles färska ut. Det här är den enda signal som avslöjar det. Vid lokal anslutning (LAN) blir givarna otillgängliga av sig själva och fältet tillför då lite.",
@@ -1406,7 +1406,7 @@
           "dso_product": "Svensk nättariff (skriver fälten nedan)"
         },
         "data_description": {
-          "grid_fee_mode": "Avgiften ditt elnätsbolag lägger på varje överförd kWh. Tibbers pris innehåller den inte, så med den inställd ser planen äntligen hela marginalpriset. \"Tidsregler\" använder schemat nedan; \"Sensor\" följer en entitet.",
+          "grid_fee_mode": "Avgiften ditt elnätsbolag lägger på varje överförd kWh. Tibbers pris innehåller den inte, och en prissensor bara om du själv lagt in den där, så med den inställd ser planen hela marginalpriset. \"Tidsregler\" använder schemat nedan; \"Sensor\" följer en entitet.",
           "grid_fee_fixed": "En fast avgift som läggs på varje timme, utöver tidsreglerna eller livesensorns värde. Den gäller bara när Elnätets överföringsavgift är Tidsregler eller Sensor; med Ingen ignoreras den. Ta den från din elnätsfaktura.",
           "grid_fee_rules": "En regel per rad, till exempel \"Nov-Mar Mån-Fre 06:00-22:00 = 0.25\". Månads-, veckodags- och tidsdelarna är valfria var för sig; överlappande regler adderas, vilket motsvarar grundavgift plus höglastpåslag. Ett komma mellan siffror är en decimalseparator, så \"0,25\" läses som 0,25 och delar aldrig en regel.",
           "grid_fee_entity": "En sensor som anger aktuell avgift i {currency}/kWh, för nät med dynamiska avgifter. Värdet läggs på varje planerad timme.",
@@ -1519,7 +1519,7 @@
       },
       "modbus_prefill": {
         "title": "Förifyll från en värmepumpsenhet",
-        "description": "För en Rotenso Windmi eller en annan GCHV-byggd värmepump, som läses via tuya_heat_pump-projektets Modbus-paket eller via pumpens egen Home Assistant-enhet. Välj enheten, eller lämna tomt och ange paketets entitetsprefix, och skicka: nästa formulär föreslår värden som lästs från pumpen - varmvattnets börvärden och schema, dagarna för legionellaskydd, nattlägets schema, pumpens maximala eleffekt (ur dess enhetskapacitet), om pumpen styr på vattentemperatur, och pumpens egna givare för givarfält som fortfarande är tomma. Ändra eller töm vilket som helst av dem; bara det du behåller sparas, och ett fält du tömmer lämnas som det var. Inget om huset eller dess värmesystem går att läsa ut på det här sättet.\n\nLästa entiteter: {found}. Registret för tillsatsvärmens typ: {backup_heater_type} - allt utom 7 betyder att pumpen har egen elvärme, och det är den som elpatronfälten under Värmepumps telemetri finns till för att bevaka.\n\nRoller lästa ur en entitets NAMN i stället för ur en publicerad definition - sidan kan inte verifiera dem, så kontrollera var och en innan du sparar: {name_matched}. Roller lästa ur publicerade definitioner, per källa: {matched_sources}.",
+        "description": "Läser bara det som sidan har en mappning för: en GCHV-byggd värmepump (till exempel en Rotenso Windmi) via tuya_heat_pump-projektets Modbus-paket, eller en värmepumps egen Home Assistant-enhet, via dess integrations publicerade definitioner där en är mappad här och annars via entiteternas namn. Välj enheten, eller lämna tomt och ange paketets entitetsprefix, och skicka: nästa formulär föreslår värden som lästs från pumpen - varmvattnets börvärden och schema, dagarna för legionellaskydd, nattlägets schema, pumpens maximala eleffekt (ur dess enhetskapacitet), om pumpen styr på vattentemperatur, och pumpens egna givare för givarfält som fortfarande är tomma. Ändra eller töm vilket som helst av dem; bara det du behåller sparas, och ett fält du tömmer lämnas som det var. Inget om huset eller dess värmesystem går att läsa ut på det här sättet.\n\nLästa entiteter: {found}. Registret för tillsatsvärmens typ: {backup_heater_type} - allt utom 7 betyder att pumpen har egen elvärme, och det är den som elpatronfälten under Värmepumps telemetri finns till för att bevaka.\n\nRoller lästa ur en entitets NAMN i stället för ur en publicerad definition - sidan kan inte verifiera dem, så kontrollera var och en innan du sparar: {name_matched}. Roller lästa ur publicerade definitioner, per källa: {matched_sources}.",
         "data": {
           "prefill_device": "Värmepumpens enhet (valfritt)",
           "modbus_prefill_prefix": "Modbus-paketets entitetsprefix",
@@ -1988,10 +1988,10 @@
         "name": "Varmvattentemperatur"
       },
       "ecl110_displace": {
-        "name": "ECL110-förskjutning"
+        "name": "Värmekurvans förskjutning"
       },
       "ecl110_effective_displace": {
-        "name": "ECL110 effektiv förskjutning"
+        "name": "Värmekurvans effektiva förskjutning"
       },
       "floor_heating_return_temperature": {
         "name": "Golvvärmens returtemperatur"
@@ -2382,15 +2382,15 @@
           "description": "Multiplikator för värmeförlusten när det regnar. 1,15 betyder 15 % större värmeförlust vid regn på 2 mm/h eller mer (effekten av ett blött klimatskal); lättare regn skalar ned den i proportion, och vid 0,1 mm/h eller mindre tillämpas den inte alls."
         },
         "ecl110_pid_time_constant_hours": {
-          "name": "ECL110 PI/PID-tidskonstant",
-          "description": "Tidskonstant (timmar) för approximationen av ECL110:s PI/PID-svar. Lägre värden reagerar snabbare, högre värden ger jämnare gång."
+          "name": "Värmekurvestyrningens PI/PID-tidskonstant",
+          "description": "Tidskonstant (timmar) för approximationen av värmekurvestyrningens PI/PID-svar. Lägre värden reagerar snabbare, högre värden ger jämnare gång."
         },
         "ecl110_displace_min": {
-          "name": "ECL110 minsta parallellförskjutning",
+          "name": "Värmekurvans minsta parallellförskjutning",
           "description": "Den lägsta parallellförskjutning optimeringen får begära, i °C."
         },
         "ecl110_displace_max": {
-          "name": "ECL110 största parallellförskjutning",
+          "name": "Värmekurvans största parallellförskjutning",
           "description": "Den högsta parallellförskjutning optimeringen får begära, i °C."
         },
         "quiet_silent_windows": {
diff --git a/dev/audit/config/scopes.json b/dev/audit/config/scopes.json
index 6aa17cb651..0c79236437 100644
--- a/dev/audit/config/scopes.json
+++ b/dev/audit/config/scopes.json
@@ -311,7 +311,7 @@
   "mode": "cells",
   "universe": [
    "README.md",
-   "docs/{CONTRIBUTING,architecture,automations,configuration,dashboard-card,ecl110,how-it-works,setup}.md",
+   "docs/{CONTRIBUTING,architecture,automations,configuration,dashboard-card,ecl110,heat-curve,how-it-works,setup}.md",
    "custom_components/heatpump_optimizer/*.py",
    "custom_components/heatpump_optimizer/www/*.js",
    "tools/**.{py,sh,js,mjs}",
@@ -486,7 +486,7 @@
    "docs/index.html",
    "docs/site/*.css",
    "tools/site/build_docs.mjs",
-   "docs/{CONTRIBUTING,architecture,automations,configuration,dashboard-card,ecl110,how-it-works,setup}.md",
+   "docs/{CONTRIBUTING,architecture,automations,configuration,dashboard-card,ecl110,heat-curve,how-it-works,setup}.md",
    "custom_components/heatpump_optimizer/{services.yaml,strings.json,manifest.json}",
    "hacs.json",
    "blueprints/**",
@@ -543,7 +543,7 @@
       "docs/index.html",
       "docs/site/*.css",
       "tools/site/build_docs.mjs",
-      "docs/{architecture,automations,configuration,dashboard-card,ecl110,how-it-works,setup}.md"
+      "docs/{architecture,automations,configuration,dashboard-card,ecl110,heat-curve,how-it-works,setup}.md"
      ],
      "steps": [
       "M1",
diff --git a/dev/audit/harnesses/vendor_text_census.py b/dev/audit/harnesses/vendor_text_census.py
new file mode 100644
index 0000000000..7654e5b189
--- /dev/null
+++ b/dev/audit/harnesses/vendor_text_census.py
@@ -0,0 +1,114 @@
+#!/usr/bin/env python3
+"""Every vendor, model or integration name in the user-facing text.
+
+    python3 dev/audit/harnesses/vendor_text_census.py [--root DIR] [--counts]
+
+The user-facing surface is `README.md`, `docs/` (less `docs/design/`, the
+dated design notes, and the figure generators under `docs/img/`), the
+integration's `strings.json` and `translations/*.json` (values only, each
+reported at its key path), the card's `www/*.js` and `services.yaml`. Each
+line or JSON value is matched against `BRANDS`, case-insensitively, as a
+whole word: a name glued to `_` or a letter (`ecl110_displace_set_topic`, an
+option key or entity id) is an identifier, not prose, and is not a hit.
+
+One line per hit: `path:locator<TAB>brand<TAB>excerpt`. `--counts` prints
+only `brand<TAB>count` lines and a `total<TAB>N` line. Exit 0 always: this is an
+enumerator whose output a seat rules hit by hit (an example of a generic
+shape, a real restriction, or a leftover), not a gate.
+
+`BRANDS` was built from every capitalised token of the same surface, read
+by hand at main b3831ff64e; a name it lacks is a hit this census misses, so
+a new vendor named in the text joins the list in the same change.
+
+Perturbation: add the word `Thermia` to any README line and `--counts`
+prints `thermia 1` and a total one higher.
+"""
+from __future__ import annotations
+
+import json
+import re
+import subprocess
+import sys
+from pathlib import Path
+
+BRANDS = (
+    "Luxtronik", "Danfoss", "ECL110", "ECL", "Tibber", "Nord Pool",
+    "ENTSO-E", "Open-Meteo", "Met.no", "Daikin", "NIBE", "Novelan",
+    "Alpha Innotec", "Stiebel Eltron", "Stiebel", "Vaillant", "Panasonic",
+    "Mitsubishi", "Thermia", "Viessmann", "Bosch", "Homey", "Rotenso",
+    "Windmi", "GCHV", "Tuya", "Vattenfall", "Ellevio", "Shelly", "Tado",
+    "ESPHome", "Modbus", "Zigbee", "ApexCharts", "Bouni", "EKMBDXA",
+    "S1256PC", "LWDV", "GWF", "Kamstrup", "Smart Home Interface", "SHI",
+)
+_PATTERN = re.compile(
+    r"(?<![\w])("
+    + "|".join(re.escape(b).replace(r"\ ", r"[ -]?") for b in sorted(BRANDS, key=len, reverse=True))
+    + r")s?(?![\w])",
+    re.IGNORECASE,
+)
+_CANON = {b.lower().replace(" ", ""): b for b in BRANDS}
+
+
+def _canon(word: str) -> str:
+    return _CANON.get(re.sub(r"[ -]", "", word.lower()), _CANON.get(word.lower(), word))
+
+
+def _surface(root: Path) -> list[str]:
+    files = subprocess.run(
+        ["git", "-C", str(root), "ls-files", "README.md", "docs",
+         "custom_components/heatpump_optimizer/strings.json",
+         "custom_components/heatpump_optimizer/translations",
+         "custom_components/heatpump_optimizer/www",
+         "custom_components/heatpump_optimizer/services.yaml"],
+        check=True, capture_output=True, text=True,
+    ).stdout.split()
+    return [
+        f for f in files
+        if not f.startswith(("docs/design/", "docs/img/"))
+        and f.endswith((".md", ".json", ".js", ".yaml", ".html"))
+    ]
+
+
+def _json_values(obj, path: str):
+    if isinstance(obj, dict):
+        for key, value in obj.items():
+            yield from _json_values(value, f"{path}.{key}" if path else key)
+    elif isinstance(obj, list):
+        for i, value in enumerate(obj):
+            yield from _json_values(value, f"{path}[{i}]")
+    elif isinstance(obj, str):
+        yield path, obj
+
+
+def census(root: Path):
+    for rel in _surface(root):
+        text = (root / rel).read_text(encoding="utf-8")
+        if rel.endswith(".json"):
+            units = _json_values(json.loads(text), "")
+        else:
+            units = ((str(n), line) for n, line in enumerate(text.splitlines(), 1))
+        for locator, unit in units:
+            for match in _PATTERN.finditer(unit):
+                start = max(0, match.start() - 60)
+                excerpt = unit[start:match.end() + 60].replace("\n", " ").replace("\t", " ")
+                yield rel, locator, _canon(match.group(1)), excerpt.strip()
+
+
+def main(argv: list[str]) -> int:
+    root = Path(argv[argv.index("--root") + 1]) if "--root" in argv else Path.cwd()
+    hits = list(census(root))
+    if "--counts" in argv:
+        counts: dict[str, int] = {}
+        for _, _, brand, _ in hits:
+            counts[brand] = counts.get(brand, 0) + 1
+        for brand, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
+            print(f"{brand}\t{n}")
+        print(f"total\t{len(hits)}")
+        return 0
+    for rel, locator, brand, excerpt in hits:
+        print(f"{rel}:{locator}\t{brand}\t{excerpt}")
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index eb5c2feced..c5f2d68bc2 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -49,7 +49,7 @@
   "source": "README.md:Entities",
   "claim": "Twenty entities are disabled by default, and these are they (#1335)",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Contract Comparison', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Temperature', 'ECL110 Displace', 'ECL110 Effective Displace', 'Floor Heating Return Temperature', 'Lower Floor Temperature', 'Measured Power', 'Slab Temperature (Estimated)', 'Solar Surplus Forecast', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood Cheaper Than Heat Pump', 'Wood-Burn Night Advisor'] measured=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Contract Comparison', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Temperature', 'ECL110 Displace', 'ECL110 Effective Displace', 'Floor Heating Return Temperature', 'Lower Floor Temperature', 'Measured Power', 'Slab Temperature (Estimated)', 'Solar Surplus Forecast', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood Cheaper Than Heat Pump', 'Wood-Burn Night Advisor']",
+  "result": "documented=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Contract Comparison', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Temperature', 'Floor Heating Return Temperature', 'Heat-Curve Displace', 'Heat-Curve Effective Displace', 'Lower Floor Temperature', 'Measured Power', 'Slab Temperature (Estimated)', 'Solar Surplus Forecast', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood Cheaper Than Heat Pump', 'Wood-Burn Night Advisor'] measured=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Contract Comparison', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Temperature', 'Floor Heating Return Temperature', 'Heat-Curve Displace', 'Heat-Curve Effective Displace', 'Lower Floor Temperature', 'Measured Power', 'Slab Temperature (Estimated)', 'Solar Surplus Forecast', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood Cheaper Than Heat Pump', 'Wood-Burn Night Advisor']",
   "verdict": "true",
   "truth": ""
  },
@@ -67,7 +67,7 @@
   "source": "README.md:### Sensors",
   "claim": "the sensor table names exactly the sensors the platform constructs",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Baseline', 'Cost Contract Comparison', 'Cost Electricity Price (now)', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'Cost Predicted', 'DHW Cost (lifetime)', 'DHW Energy (lifetime)', 'DHW Heating Cost (next 24 h)', 'DHW Heating Schedule', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Setpoint Advisor', 'DHW Temperature', 'ECL110 Displace', 'ECL110 Effective Displace', 'Floor Heating Return Temperature', 'Heat Pump Action', 'Indoor Temperature (Optimizer)', 'Indoor Temperature (Predicted)', 'Last Optimization', 'Learning Comfort Weight', 'Learning Estimated COP', 'Learning Model Status', 'Learning Observed COP', 'Lifetime Space Heating Cost', 'Lifetime Space Heating Energy', 'Lifetime Total Energy', 'Lifetime Total Heating Cost', 'Lower Floor Temperature', 'Measured Power', 'Model Restart Advisor', 'Next Optimization', 'Optimal Setpoint', 'Optimization Mode', 'Optimization Schedule', 'Optimization Schedule Steps', 'Optimization Status', 'Outdoor Temperature (Optimizer)', 'Plan DHW Heating (next 24 h)', 'Plan Monthly Savings', 'Plan Narrative', 'Plan Optimization Score', 'Plan Predicted Savings', 'Plan Savings Percentage', 'Plan Space Heating (next 24 h)', 'Prediction Accuracy', 'Predictive Optimization Insight', 'Recommended Power', 'Sensor-Gap Advisor', 'Slab Temperature (Estimated)', 'Solar Heat Gain', 'Solar Irradiance', 'Solar Surplus Forecast', 'Thermal Battery Charge', 'Thermal Battery Energy', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood-Burn Night Advisor'] measured=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Baseline', 'Cost Contract Comparison', 'Cost Electricity Price (now)', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'Cost Predicted', 'DHW Cost (lifetime)', 'DHW Energy (lifetime)', 'DHW Heating Cost (next 24 h)', 'DHW Heating Schedule', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Setpoint Advisor', 'DHW Temperature', 'ECL110 Displace', 'ECL110 Effective Displace', 'Floor Heating Return Temperature', 'Heat Pump Action', 'Indoor Temperature (Optimizer)', 'Indoor Temperature (Predicted)', 'Last Optimization', 'Learning Comfort Weight', 'Learning Estimated COP', 'Learning Model Status', 'Learning Observed COP', 'Lifetime Space Heating Cost', 'Lifetime Space Heating Energy', 'Lifetime Total Energy', 'Lifetime Total Heating Cost', 'Lower Floor Temperature', 'Measured Power', 'Model Restart Advisor', 'Next Optimization', 'Optimal Setpoint', 'Optimization Mode', 'Optimization Schedule', 'Optimization Schedule Steps', 'Optimization Status', 'Outdoor Temperature (Optimizer)', 'Plan DHW Heating (next 24 h)', 'Plan Monthly Savings', 'Plan Narrative', 'Plan Optimization Score', 'Plan Predicted Savings', 'Plan Savings Percentage', 'Plan Space Heating (next 24 h)', 'Prediction Accuracy', 'Predictive Optimization Insight', 'Recommended Power', 'Sensor-Gap Advisor', 'Slab Temperature (Estimated)', 'Solar Heat Gain', 'Solar Irradiance', 'Solar Surplus Forecast', 'Thermal Battery Charge', 'Thermal Battery Energy', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood-Burn Night Advisor']",
+  "result": "documented=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Baseline', 'Cost Contract Comparison', 'Cost Electricity Price (now)', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'Cost Predicted', 'DHW Cost (lifetime)', 'DHW Energy (lifetime)', 'DHW Heating Cost (next 24 h)', 'DHW Heating Schedule', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Setpoint Advisor', 'DHW Temperature', 'Floor Heating Return Temperature', 'Heat Pump Action', 'Heat-Curve Displace', 'Heat-Curve Effective Displace', 'Indoor Temperature (Optimizer)', 'Indoor Temperature (Predicted)', 'Last Optimization', 'Learning Comfort Weight', 'Learning Estimated COP', 'Learning Model Status', 'Learning Observed COP', 'Lifetime Space Heating Cost', 'Lifetime Space Heating Energy', 'Lifetime Total Energy', 'Lifetime Total Heating Cost', 'Lower Floor Temperature', 'Measured Power', 'Model Restart Advisor', 'Next Optimization', 'Optimal Setpoint', 'Optimization Mode', 'Optimization Schedule', 'Optimization Schedule Steps', 'Optimization Status', 'Outdoor Temperature (Optimizer)', 'Plan DHW Heating (next 24 h)', 'Plan Monthly Savings', 'Plan Narrative', 'Plan Optimization Score', 'Plan Predicted Savings', 'Plan Savings Percentage', 'Plan Space Heating (next 24 h)', 'Prediction Accuracy', 'Predictive Optimization Insight', 'Recommended Power', 'Sensor-Gap Advisor', 'Slab Temperature (Estimated)', 'Solar Heat Gain', 'Solar Irradiance', 'Solar Surplus Forecast', 'Thermal Battery Charge', 'Thermal Battery Energy', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood-Burn Night Advisor'] measured=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Baseline', 'Cost Contract Comparison', 'Cost Electricity Price (now)', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'Cost Predicted', 'DHW Cost (lifetime)', 'DHW Energy (lifetime)', 'DHW Heating Cost (next 24 h)', 'DHW Heating Schedule', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Setpoint Advisor', 'DHW Temperature', 'Floor Heating Return Temperature', 'Heat Pump Action', 'Heat-Curve Displace', 'Heat-Curve Effective Displace', 'Indoor Temperature (Optimizer)', 'Indoor Temperature (Predicted)', 'Last Optimization', 'Learning Comfort Weight', 'Learning Estimated COP', 'Learning Model Status', 'Learning Observed COP', 'Lifetime Space Heating Cost', 'Lifetime Space Heating Energy', 'Lifetime Total Energy', 'Lifetime Total Heating Cost', 'Lower Floor Temperature', 'Measured Power', 'Model Restart Advisor', 'Next Optimization', 'Optimal Setpoint', 'Optimization Mode', 'Optimization Schedule', 'Optimization Schedule Steps', 'Optimization Status', 'Outdoor Temperature (Optimizer)', 'Plan DHW Heating (next 24 h)', 'Plan Monthly Savings', 'Plan Narrative', 'Plan Optimization Score', 'Plan Predicted Savings', 'Plan Savings Percentage', 'Plan Space Heating (next 24 h)', 'Prediction Accuracy', 'Predictive Optimization Insight', 'Recommended Power', 'Sensor-Gap Advisor', 'Slab Temperature (Estimated)', 'Solar Heat Gain', 'Solar Irradiance', 'Solar Surplus Forecast', 'Thermal Battery Charge', 'Thermal Battery Energy', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood-Burn Night Advisor']",
   "verdict": "true",
   "truth": ""
  },
@@ -724,7 +724,7 @@
   "source": "docs/ecl110.md",
   "claim": "both ECL110 sensors are disabled by default and diagnostic",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "[('ECL110 Displace', False, 'diagnostic'), ('ECL110 Effective Displace', False, 'diagnostic')]",
+  "result": "[('Heat-Curve Displace', False, 'diagnostic'), ('Heat-Curve Effective Displace', False, 'diagnostic')]",
   "verdict": "true",
   "truth": ""
  },
@@ -965,9 +965,9 @@
  {
   "id": "C108",
   "source": "README.md + docs/*.md",
-  "claim": "every relative link resolves (92 links)",
+  "claim": "every relative link resolves (97 links)",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "92 links, broken=[], of which removed-by-the-export=[]",
+  "result": "97 links, broken=[], of which removed-by-the-export=[]",
   "verdict": "true",
   "truth": ""
  },
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index 2637058615..4617af6acb 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -9,9 +9,9 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C3 | `README.md:### Binary Sensors` | Binary Sensors (6 total) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=6 measured=6 | **true** |  |
 | C4 | `README.md:### Buttons` | Buttons (6 total) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=6 measured=6 | **true** |  |
 | C5 | `docs/architecture.md:mermaid` | 82 entities / 62 sensors / 6 binary sensors / 6 buttons / 6 switches / 1 climate / 1 datetime | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=(82, 62, 6, 6, 6, 1, 1) measured=(82, 62, 6, 6, 6, 1, 1) | **true** |  |
-| C6 | `README.md:Entities` | Twenty entities are disabled by default, and these are they (#1335) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Contract Comparison', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Temperature', 'ECL110 Displace', 'ECL110 Effective Displace', 'Floor Heating Return Temperature', 'Lower Floor Temperature', 'Measured Power', 'Slab Temperature (Estimated)', 'Solar Surplus Forecast', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood Cheaper Than Heat Pump', 'Wood-Burn Night Advisor'] measured=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Contract Comparison', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Temperature', 'ECL110 Displace', 'ECL110 Effective Displace', 'Floor Heating Return Temperature', 'Lower Floor Temperature', 'Measured Power', 'Slab Temperature (Estimated)', 'Solar Surplus Forecast', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood Cheaper Than Heat Pump', 'Wood-Burn Night Advisor'] | **true** |  |
+| C6 | `README.md:Entities` | Twenty entities are disabled by default, and these are they (#1335) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Contract Comparison', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Temperature', 'Floor Heating Return Temperature', 'Heat-Curve Displace', 'Heat-Curve Effective Displace', 'Lower Floor Temperature', 'Measured Power', 'Slab Temperature (Estimated)', 'Solar Surplus Forecast', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood Cheaper Than Heat Pump', 'Wood-Burn Night Advisor'] measured=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Contract Comparison', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Temperature', 'Floor Heating Return Temperature', 'Heat-Curve Displace', 'Heat-Curve Effective Displace', 'Lower Floor Temperature', 'Measured Power', 'Slab Temperature (Estimated)', 'Solar Surplus Forecast', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood Cheaper Than Heat Pump', 'Wood-Burn Night Advisor'] | **true** |  |
 | C7 | `README.md:Entities` | exactly twenty entities are disabled by default (#1335) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=20 measured=20 | **true** |  |
-| C8 | `README.md:### Sensors` | the sensor table names exactly the sensors the platform constructs | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Baseline', 'Cost Contract Comparison', 'Cost Electricity Price (now)', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'Cost Predicted', 'DHW Cost (lifetime)', 'DHW Energy (lifetime)', 'DHW Heating Cost (next 24 h)', 'DHW Heating Schedule', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Setpoint Advisor', 'DHW Temperature', 'ECL110 Displace', 'ECL110 Effective Displace', 'Floor Heating Return Temperature', 'Heat Pump Action', 'Indoor Temperature (Optimizer)', 'Indoor Temperature (Predicted)', 'Last Optimization', 'Learning Comfort Weight', 'Learning Estimated COP', 'Learning Model Status', 'Learning Observed COP', 'Lifetime Space Heating Cost', 'Lifetime Space Heating Energy', 'Lifetime Total Energy', 'Lifetime Total Heating Cost', 'Lower Floor Temperature', 'Measured Power', 'Model Restart Advisor', 'Next Optimization', 'Optimal Setpoint', 'Optimization Mode', 'Optimization Schedule', 'Optimization Schedule Steps', 'Optimization Status', 'Outdoor Temperature (Optimizer)', 'Plan DHW Heating (next 24 h)', 'Plan Monthly Savings', 'Plan Narrative', 'Plan Optimization Score', 'Plan Predicted Savings', 'Plan Savings Percentage', 'Plan Space Heating (next 24 h)', 'Prediction Accuracy', 'Predictive Optimization Insight', 'Recommended Power', 'Sensor-Gap Advisor', 'Slab Temperature (Estimated)', 'Solar Heat Gain', 'Solar Irradiance', 'Solar Surplus Forecast', 'Thermal Battery Charge', 'Thermal Battery Energy', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood-Burn Night Advisor'] measured=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Baseline', 'Cost Contract Comparison', 'Cost Electricity Price (now)', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'Cost Predicted', 'DHW Cost (lifetime)', 'DHW Energy (lifetime)', 'DHW Heating Cost (next 24 h)', 'DHW Heating Schedule', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Setpoint Advisor', 'DHW Temperature', 'ECL110 Displace', 'ECL110 Effective Displace', 'Floor Heating Return Temperature', 'Heat Pump Action', 'Indoor Temperature (Optimizer)', 'Indoor Temperature (Predicted)', 'Last Optimization', 'Learning Comfort Weight', 'Learning Estimated COP', 'Learning Model Status', 'Learning Observed COP', 'Lifetime Space Heating Cost', 'Lifetime Space Heating Energy', 'Lifetime Total Energy', 'Lifetime Total Heating Cost', 'Lower Floor Temperature', 'Measured Power', 'Model Restart Advisor', 'Next Optimization', 'Optimal Setpoint', 'Optimization Mode', 'Optimization Schedule', 'Optimization Schedule Steps', 'Optimization Status', 'Outdoor Temperature (Optimizer)', 'Plan DHW Heating (next 24 h)', 'Plan Monthly Savings', 'Plan Narrative', 'Plan Optimization Score', 'Plan Predicted Savings', 'Plan Savings Percentage', 'Plan Space Heating (next 24 h)', 'Prediction Accuracy', 'Predictive Optimization Insight', 'Recommended Power', 'Sensor-Gap Advisor', 'Slab Temperature (Estimated)', 'Solar Heat Gain', 'Solar Irradiance', 'Solar Surplus Forecast', 'Thermal Battery Charge', 'Thermal Battery Energy', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood-Burn Night Advisor'] | **true** |  |
+| C8 | `README.md:### Sensors` | the sensor table names exactly the sensors the platform constructs | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Baseline', 'Cost Contract Comparison', 'Cost Electricity Price (now)', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'Cost Predicted', 'DHW Cost (lifetime)', 'DHW Energy (lifetime)', 'DHW Heating Cost (next 24 h)', 'DHW Heating Schedule', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Setpoint Advisor', 'DHW Temperature', 'Floor Heating Return Temperature', 'Heat Pump Action', 'Heat-Curve Displace', 'Heat-Curve Effective Displace', 'Indoor Temperature (Optimizer)', 'Indoor Temperature (Predicted)', 'Last Optimization', 'Learning Comfort Weight', 'Learning Estimated COP', 'Learning Model Status', 'Learning Observed COP', 'Lifetime Space Heating Cost', 'Lifetime Space Heating Energy', 'Lifetime Total Energy', 'Lifetime Total Heating Cost', 'Lower Floor Temperature', 'Measured Power', 'Model Restart Advisor', 'Next Optimization', 'Optimal Setpoint', 'Optimization Mode', 'Optimization Schedule', 'Optimization Schedule Steps', 'Optimization Status', 'Outdoor Temperature (Optimizer)', 'Plan DHW Heating (next 24 h)', 'Plan Monthly Savings', 'Plan Narrative', 'Plan Optimization Score', 'Plan Predicted Savings', 'Plan Savings Percentage', 'Plan Space Heating (next 24 h)', 'Prediction Accuracy', 'Predictive Optimization Insight', 'Recommended Power', 'Sensor-Gap Advisor', 'Slab Temperature (Estimated)', 'Solar Heat Gain', 'Solar Irradiance', 'Solar Surplus Forecast', 'Thermal Battery Charge', 'Thermal Battery Energy', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood-Burn Night Advisor'] measured=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Baseline', 'Cost Contract Comparison', 'Cost Electricity Price (now)', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'Cost Predicted', 'DHW Cost (lifetime)', 'DHW Energy (lifetime)', 'DHW Heating Cost (next 24 h)', 'DHW Heating Schedule', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Setpoint Advisor', 'DHW Temperature', 'Floor Heating Return Temperature', 'Heat Pump Action', 'Heat-Curve Displace', 'Heat-Curve Effective Displace', 'Indoor Temperature (Optimizer)', 'Indoor Temperature (Predicted)', 'Last Optimization', 'Learning Comfort Weight', 'Learning Estimated COP', 'Learning Model Status', 'Learning Observed COP', 'Lifetime Space Heating Cost', 'Lifetime Space Heating Energy', 'Lifetime Total Energy', 'Lifetime Total Heating Cost', 'Lower Floor Temperature', 'Measured Power', 'Model Restart Advisor', 'Next Optimization', 'Optimal Setpoint', 'Optimization Mode', 'Optimization Schedule', 'Optimization Schedule Steps', 'Optimization Status', 'Outdoor Temperature (Optimizer)', 'Plan DHW Heating (next 24 h)', 'Plan Monthly Savings', 'Plan Narrative', 'Plan Optimization Score', 'Plan Predicted Savings', 'Plan Savings Percentage', 'Plan Space Heating (next 24 h)', 'Prediction Accuracy', 'Predictive Optimization Insight', 'Recommended Power', 'Sensor-Gap Advisor', 'Slab Temperature (Estimated)', 'Solar Heat Gain', 'Solar Irradiance', 'Solar Surplus Forecast', 'Thermal Battery Charge', 'Thermal Battery Energy', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood-Burn Night Advisor'] | **true** |  |
 | C9 | `README.md:### Sensors` | every sensor row's Unit column is the unit the entity publishes (CUR = the instance currency) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 62 rows checked, mismatches=[] | **true** |  |
 | C10 | `README.md:### Sensors` | every row whose Notes begin `Diagnostic` is EntityCategory.DIAGNOSTIC, and no other row is | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | mismatches=[] | **true** |  |
 | C11 | `README.md:### Sensors` | every row whose Notes say `disabled by default` has entity_registry_enabled_default False, and no other row does | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | mismatches=[] | **true** |  |
@@ -84,7 +84,7 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C78 | `docs/ecl110.md` | the weather anticipation bias applies over the first eight hours | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=True measured=True | **true** |  |
 | C79 | `docs/ecl110.md` | the published displace is rounded to a whole number | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=True measured=True | **true** |  |
 | C80 | `docs/ecl110.md` | comfort commands +4 °C or your maximum if lower; boost your maximum; off your minimum | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=True measured=True | **true** |  |
-| C81 | `docs/ecl110.md` | both ECL110 sensors are disabled by default and diagnostic | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | [('ECL110 Displace', False, 'diagnostic'), ('ECL110 Effective Displace', False, 'diagnostic')] | **true** |  |
+| C81 | `docs/ecl110.md` | both ECL110 sensors are disabled by default and diagnostic | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | [('Heat-Curve Displace', False, 'diagnostic'), ('Heat-Curve Effective Displace', False, 'diagnostic')] | **true** |  |
 | C82 | `README.md:Removal` | every entry keeps its learners and ledgers in twelve files under .storage/, named | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['accuracy', 'away', 'boost', 'dhw_draws', 'dhw_legionella', 'dhw_profile', 'energy', 'ledger', 'manual_plan', 'price_model', 'snapshots', 'thermal_learning'] measured=['accuracy', 'away', 'boost', 'dhw_draws', 'dhw_legionella', 'dhw_profile', 'energy', 'ledger', 'manual_plan', 'price_model', 'snapshots', 'thermal_learning'] | **true** |  |
 | C83 | `README.md:Removal` | the count in that sentence is twelve | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=12 measured=12 | **true** |  |
 | C84 | `README.md:Removal` | the registered Lovelace resource is /heatpump_optimizer_static/heatpump-optimizer-card.js | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='/heatpump_optimizer_static/heatpump-optimizer-card.js' measured='/heatpump_optimizer_static/heatpump-optimizer-card.js' | **true** |  |
@@ -111,7 +111,7 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C105 | `docs/automations.md` | the Power Headroom sensor appears once anything bounds the house -- a main fuse OR a capacity tariff -- and a tariff-only install reads 0.0 kW with limit_source='capacity tariff with no peak reference yet' until the month's first metering window closes; with neither it stays unavailable | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | no fuse + capacity tariff enabled -> {'available': True, 'limit_kw': 0.0, 'headroom_kw': 0.0, 'baseline_source': 'planned power only (no meter)', 'limit_source': 'capacity tariff with no peak reference yet'}; fuse only -> available=True; neither -> available=False | **true** |  |
 | C106 | `docs/automations.md` | Power Headroom is min(main fuse, capacity threshold) - current house draw, clamped at zero, in kW | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | fuse 20 A 3-phase -> limit_kw=13.8, headroom_kw=13.8, limit_source='main fuse' | **true** |  |
 | C107 | `README.md + docs/*.md + the card` | every entity id quoted in the documentation is an entity the platforms construct | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 9 distinct ids cited, not constructed=[] | **true** |  |
-| C108 | `README.md + docs/*.md` | every relative link resolves (92 links) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 92 links, broken=[], of which removed-by-the-export=[] | **true** |  |
+| C108 | `README.md + docs/*.md` | every relative link resolves (97 links) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 97 links, broken=[], of which removed-by-the-export=[] | **true** |  |
 | C109 | `README.md + docs/how-it-works.md` | the links to docs/audit-2026-08.md, docs/audit-2026-09.md and docs/backlog.md resolve | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | finder_wall in tools/audit/prepare_baseline.sh removes docs/audit-*.md, dev/archive/audits/audit-*.md and dev/archive/backlog.md; this tree cannot answer | **unverifiable** | not checkable in the export -- finder_wall removes docs/audit-*.md, dev/archive/audits/audit-*.md and dev/archive/backlog.md |
 | C110 | `README.md + docs/*.md` | every image the documentation embeds exists (21 images) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 21 images, missing=[] | **true** |  |
 | C111 | `README.md + docs/*.md` | every external link answers 200 to a HEAD request (21 links) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py --links` | not run: pass --links | **unverifiable** | re-run with --links |
diff --git a/dev/programme/delivery/3663.md b/dev/programme/delivery/3663.md
new file mode 100644
index 0000000000..d733c8f57e
--- /dev/null
+++ b/dev/programme/delivery/3663.md
@@ -0,0 +1 @@
+- [#3663](https://github.com/tvofi/heatpump_optimizer/pull/3663) — **open**, R11-OWNER-GENERIC-CONTROL-TEXT: r11 owner generic control text (R11-OWNER-GENERIC-CONTROL-TEXT)
diff --git a/docs/architecture.md b/docs/architecture.md
index e69e659580..f057a9dc1b 100644
--- a/docs/architecture.md
+++ b/docs/architecture.md
@@ -178,7 +178,7 @@ custom_components/heatpump_optimizer/
 ├── snapshots.py          # Weekly learner snapshots and the rollback alarm
 ├── learner_progress.py   # Each thermal learner's phase, progress and wait; a day count only to a counting gate
 ├── comfort_learning.py   # Revealed-preference comfort-weight tuning
-├── curve_learning.py     # Standing cool-only bias on the ECL110 heat curve
+├── curve_learning.py     # Standing cool-only bias on the heat-curve displace
 ├── sysid.py              # Active step-response identification
 ├── presets.py            # Building archetypes to thermal parameters
 ├── external_heat.py      # Wood-furnace detection with hysteresis and decay
@@ -200,8 +200,8 @@ custom_components/heatpump_optimizer/
 │                         #   estimate is what the solve prices that switch by
 │                         #   and what orders the legs of a both step the
 │                         #   arbiter serves
-├── heat_curve.py         # The heat-curve displace's outputs: the ECL110 MQTT
-│                         #   topics and an offset number entity
+├── heat_curve.py         # The heat-curve displace's outputs: the MQTT topics
+│                         #   and a number entity, kind offset or persistent
 ├── off_restore.py        # The one owner of the off and unload restore: what
 │                         #   a writer restores when the optimizer lets go
 ├── early_cutoff.py       # Switches a space-heating pump off inside the
diff --git a/docs/automations.md b/docs/automations.md
index 4e39024783..95b39f5962 100644
--- a/docs/automations.md
+++ b/docs/automations.md
@@ -1,6 +1,6 @@
 # Automations
 
-Without a heat pump on/off switch — and without the ECL110 or
+Without a heat pump on/off switch — and without the heat-curve or
 frequency-control paths — the optimizer's plan is published on sensors for
 your own automations to act on ([configuration.md](configuration.md) says
 exactly that where the trade-off is made). The examples below are complete and
diff --git a/docs/configuration.md b/docs/configuration.md
index ae9cef0a84..ba148fd0c3 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -85,7 +85,7 @@ Every picker on this second screen is optional; skip any you do not have. Withou
 |---|---|---|
 | Indoor temperature sensor | none | The real room temperature. Without it the optimizer trusts its own model, which drifts over time — this is the sensor worth finding first. |
 | Outdoor temperature sensor | none | A local thermometer beats the forecast for the current hour. |
-| Heat pump on/off switch | none | A `switch` the optimizer may turn off during expensive hours. In *auto* and *economy* mode it is never switched off less than 10 minutes after it came on, nor on less than 10 minutes after it went off, and a run the plan would end within 10 minutes is not started unless the step heats the tank and the tank needs heat now (below its minimum, or a disinfection hold); a held switch is retried every minute and changes once its 10 minutes have passed. The age is the switch's own, whoever switched it; after a Home Assistant restart it counts from the restart. A boost, the other modes and the measurement experiment are not held. Without it — and without the ECL110 or frequency-control paths — the plan is published on sensors for your own automations to act on ([worked examples](automations.md)). |
+| Heat pump on/off switch | none | A `switch` the optimizer may turn off during expensive hours. In *auto* and *economy* mode it is never switched off less than 10 minutes after it came on, nor on less than 10 minutes after it went off, and a run the plan would end within 10 minutes is not started unless the step heats the tank and the tank needs heat now (below its minimum, or a disinfection hold); a held switch is retried every minute and changes once its 10 minutes have passed. The age is the switch's own, whoever switched it; after a Home Assistant restart it counts from the restart. A boost, the other modes and the measurement experiment are not held. Without it — and without the heat-curve or frequency-control paths — the plan is published on sensors for your own automations to act on ([worked examples](automations.md)). |
 | Solar radiation sensor | none | Irradiance in W/m², the sun on the house now, which the learners read. The plan's later steps take the sun from the weather forecast; the sensor's reading stands in for the whole horizon only when no forecast is available. |
 | Solar irradiance source | Weather entity | `Weather entity` reads irradiance from your weather integration, which often does not publish any. `Open-Meteo` fetches a free forecast for the location below; no account needed. |
 | Solar irradiance location | your Home Assistant home location | The coordinate Open-Meteo is asked about. Only used when the source is Open-Meteo. |
@@ -98,12 +98,12 @@ Every picker on this second screen is optional; skip any you do not have. Withou
 | Pump online | none | Strongly recommended for a cloud-connected pump. On while the pump is actually reachable, which a stale cloud republish cannot tell you on its own. |
 | Fault alarm | none | On while the pump is reporting a fault. Only whether there is a fault is used, never the code itself. |
 
-The heat-curve settings (the Danfoss ECL110 MQTT topics and the offset entity)
-are not asked during setup. Questions only owners of such a controller can
-answer do not belong on everyone's first screen, so they
-live on their own options page, where both MQTT topics ship empty and nothing
-is published or subscribed until a topic is set (see [ecl110.md](ecl110.md));
-an install without an ECL110 never touches the topics.
+The heat-curve settings (the MQTT topics and the entity, for the three ways
+in [heat-curve.md](heat-curve.md)) are not asked during setup. Questions only
+owners of such a controller can answer do not belong on everyone's first
+screen, so they live on their own options page, where both MQTT topics ship
+empty and nothing is published or subscribed until a topic is set; an install
+whose controller takes nothing over MQTT never touches the topics.
 
 ### 3 · The finish menu — Finish setup now?
 
@@ -627,8 +627,8 @@ are on **Power and solar sensors**; mode / defrost / online / fault are on
 | Minimum lift above the inlet water (`flow_min_lift_k`) | 5 K | 0.5–15 K, 0.5 steps | Shown when the unit above is *Flow* or *Return temperature*. The heating value at the plan's lowest power is the measured inlet water plus this (see [Pump duty control](#pump-duty-control)). |
 | Heating flow ceiling (`flow_heat_c`) | 55 °C | 30–70 °C, 0.5 steps | Shown when the unit above is *Flow* or *Return temperature*. The heating value at full planned power, and the highest heating value written while the plan is in charge. A space boost or Boost mode writes the set-point entity's own maximum instead (up to 70 °C), capped by a value here other than 55 °C. A stored value at or below the 25 °C gate is read as 55 °C. |
 | Follow the planned power on the measured draw (`space_setpoint_power_feedback`) | On | on / off | Shown when the unit above is *Flow* or *Return temperature*; acts only when a heat-pump power sensor is configured too. Closes the heating value on the measured draw (see [Pump duty control](#pump-duty-control)). Off writes the inlet plus the lift. |
-| Controller's minimum set-point sensor (`space_setpoint_low_limit_entity`) | none | a temperature sensor | Shown when the unit above is *Flow* or *Return temperature*. Optional: the lowest value the controller accepts for the set-point entity (a Luxtronik through ha-luxtronik-shi: “Temperature: return target minimum”, input 10104). *Follow the planned power* then never sends a value below it (see [Pump duty control](#pump-duty-control)). Empty changes nothing. |
-| Controller's maximum set-point sensor (`space_setpoint_high_limit_entity`) | none | a temperature sensor | Shown when the unit above is *Flow* or *Return temperature*. Optional: the highest value the controller accepts (a Luxtronik: “Temperature: return limit”, input 10103). *Follow the planned power* then never sends a value above it. Empty changes nothing. |
+| Controller's minimum set-point sensor (`space_setpoint_low_limit_entity`) | none | a temperature sensor | Shown when the unit above is *Flow* or *Return temperature*. Optional: the lowest value the controller accepts for the set-point entity (for example a Luxtronik through ha-luxtronik-shi: “Temperature: return target minimum”, input 10104). *Follow the planned power* then never sends a value below it (see [Pump duty control](#pump-duty-control)). Empty changes nothing. |
+| Controller's maximum set-point sensor (`space_setpoint_high_limit_entity`) | none | a temperature sensor | Shown when the unit above is *Flow* or *Return temperature*. Optional: the highest value the controller accepts (for example a Luxtronik: “Temperature: return limit”, input 10103). *Follow the planned power* then never sends a value above it. Empty changes nothing. |
 
 ### Power and solar sensors
 
@@ -716,8 +716,8 @@ writes, at every 15-minute plan step:
   fields appear once that unit is saved). Those defaults suit a controller
   that holds its **supply** at the set-point.
 - **For a *Return temperature* entity** — a controller that takes the
-  number as its **return-water** target, as a Luxtronik (alpha innotec,
-  Novelan) through its Smart Home Interface is assumed to — everything above
+  number as its **return-water** target, as, for example, a Luxtronik
+  (alpha innotec, Novelan) through its Smart Home Interface is assumed to — everything above
   applies, with these differences:
   - The values derived from a supply temperature — the 35 °C hold, the
     weather curve and the 25 °C gate — are written 5 K lower (the rated
@@ -747,12 +747,12 @@ writes, at every 15-minute plan step:
     level; check it against the measured frequency and power. Choose the
     ceiling above the highest return you see in normal heating plus the
     lift (otherwise a heating step writes a target below the return, and
-    such a controller presumably stops), and no higher than the controller accepts: a Luxtronik
+    such a controller presumably stops), and no higher than the controller accepts: a Luxtronik, for example,
     clamps the target to its own minimum return target and return limit, so a ceiling above the
     limit is written but not followed. A controller that starts heating only once the target sits
     its hysteresis above the return is not started by a smaller lift;
     it only keeps a running compressor near its minimum. That hysteresis is a setting of the
-    controller, not a fixed 2 K: a Luxtronik accepts 0.5 K at the least, and the start threshold in
+    controller, not a fixed 2 K: a Luxtronik, for example, accepts 0.5 K at the least, and the start threshold in
     effect (the return target less the hysteresis) is input 10107 of its Smart Home Interface, which
     ha-luxtronik-shi publishes as its *Demand border* sensor
     ([the contributor's answers](https://github.com/tvofi/heatpump_optimizer/pull/3372#issuecomment-6756915104)).
@@ -762,8 +762,8 @@ writes, at every 15-minute plan step:
     frequency and power.
   - The integration that exposes the controller must poll it at least
     every 10 minutes and restore its heating mode after a controller
-    restart: a Luxtronik Smart Home Interface drops every value set through
-    it after 600 s without access and after each restart. Any access
+    restart, since a controller can drop what was set through it: a Luxtronik
+    Smart Home Interface, for one, drops every value set through it after 600 s without access and after each restart. Any access
     re-arms those 600 s, a read as much as a write, so polling alone keeps
     a written value; ha-luxtronik-shi polls every 30 s by default and
     offers 10–300 s, and restores what it wrote after a controller restart
@@ -771,7 +771,7 @@ writes, at every 15-minute plan step:
     ([the contributor's answers](https://github.com/tvofi/heatpump_optimizer/pull/3372#issuecomment-6756915104)). A reverted
     set-point is noticed and written again; a reverted heating mode is not
     visible to this integration. No second tool may write the same
-    registers: a Luxtronik then silently discards writes (error 816).
+    registers: a Luxtronik, for one, then silently discards writes (error 816).
   - Downgrading: a version before this option reads *Return temperature* as
     *Indoor temperature* and writes the planned room temperature to the
     entity. Switch the unit back to *Flow temperature* before downgrading.
@@ -793,12 +793,12 @@ writes, at every 15-minute plan step:
   unchanged and start the loop over. Where the controller cuts a written
   value to its own limits, that cut is taken as the run's limit and no
   repair is raised. Preconditions on the controller:
-  - its heating hysteresis is at most the lift (Luxtronik: 0.5 K, its
-    minimum), or the first write of a run does not start a stopped
+  - its heating hysteresis is at most the lift (on a Luxtronik, for
+    example, 0.5 K, its minimum), or the first write of a run does not start a stopped
     compressor — the same limitation as without the loop;
   - its minimum return target sits below the return during the heating
     season, or the loop cannot wind the compressor down past it. A
-    Luxtronik cuts the set-point to its minimum return target (input 10104
+    Luxtronik, for example, cuts the set-point to its minimum return target (input 10104
     of its Smart Home Interface, parameter 979) and its return limit (input
     10103, parameter 87), both of which ha-luxtronik-shi publishes as
     sensors ([the contributor's answers](https://github.com/tvofi/heatpump_optimizer/pull/3372#issuecomment-6756915104)).
@@ -1187,12 +1187,14 @@ reads SEK, that is a label, not a constraint.
 
 ### Heat curve control
 
-For Danfoss ECL110 controllers driven over MQTT, or any controller whose
-heat-curve offset Home Assistant exposes as a `number`. The topics have no
-shipped default: each is exactly what you store, an empty or absent topic
-leaves that arm off, and nothing is published or subscribed until a topic
-is set — an install without an ECL110 never touches these topics. See
-[ecl110.md](ecl110.md) for the full picture.
+For a weather-compensated controller whose heat curve the optimizer shifts,
+three ways: over MQTT topics (a Danfoss ECL110 through an MQTT bridge, for
+example), to a volatile offset `number` entity, or to a stored curve
+parameter. The topics have no shipped default: each is exactly what you
+store, an empty or absent topic leaves that arm off, and nothing is published
+or subscribed until a topic is set — an install whose controller takes
+nothing over MQTT never touches these topics. See
+[heat-curve.md](heat-curve.md) for the full picture.
 
 | Setting | Default | Range | What it means |
 |---|---|---|---|
@@ -1205,10 +1207,10 @@ is set — an install without an ECL110 never touches these topics. See
 | Largest upward offset | 20 °C | 0–30, 0.5 steps | How far it may be shifted up when storing cheap heat. |
 | Controller response time | 1.5 h | 0.25–6.0, 0.25 steps | Roughly how long the controller takes to act on a new offset, so the optimizer does not ask for changes faster than the system can follow. |
 | Heat-curve offset entity | *(empty)* | a `number` or `input_number` | The same offset written to an entity instead of, or as well as, MQTT. Kind offset: a whole-curve offset, 0 neutral, that the controller forgets on a restart; turning the optimizer off, or unloading it, writes 0; refused when its own range excludes 0. Kind persistent: a curve setting the controller stores; off and unload write back the value it held before the first write; refused when it reads no value or one outside its own range. Refused when it is an entity the optimizer already writes. |
-| What the entity is | Offset | Offset, Persistent | Offset: a temperature difference, not stored by the controller; prefer it where the controller has one. Persistent: a stored curve setting, displaced from its own value with a daily write cap; see [ecl110.md](ecl110.md#kind-persistent-a-stored-curve-parameter). |
-| Largest offset written to the entity | 3 K | 0.5–5, 0.5 steps | The entity's offset stays within this many kelvin either way, whatever the MQTT range allows. 3 K is an estimate; see [ecl110.md](ecl110.md#without-mqtt-a-number-entity). |
+| What the entity is | Offset | Offset, Persistent | Offset: a temperature difference, not stored by the controller; prefer it where the controller has one. Persistent: a stored curve setting, displaced from its own value with a daily write cap; see [heat-curve.md](heat-curve.md#kind-persistent-a-stored-curve-parameter). |
+| Largest offset written to the entity | 3 K | 0.5–5, 0.5 steps | The entity's offset stays within this many kelvin either way, whatever the MQTT range allows. 3 K is an estimate; see [heat-curve.md](heat-curve.md#without-mqtt-a-number-entity). |
 | Largest displacement of a stored parameter | 3 K | 0.5–5, 0.5 steps | Kind persistent only: the stored setting stays within this many kelvin of its value before the first write. 3 K is an estimate. |
-| Most writes a day to a stored parameter | 12 | 0–48 | Kind persistent only: writes in one local day, the write back on off included, one always kept for it; 0 or 1 writes nothing. 12 rests partly on forum figures and estimates; see [ecl110.md](ecl110.md#kind-persistent-a-stored-curve-parameter). |
+| Most writes a day to a stored parameter | 12 | 0–48 | Kind persistent only: writes in one local day, the write back on off included, one always kept for it; 0 or 1 writes nothing. 12 rests partly on forum figures and estimates; see [heat-curve.md](heat-curve.md#kind-persistent-a-stored-curve-parameter). |
 | Least time between writes to a stored parameter | 60 min | 15–360, 15 steps | Kind persistent only: after a write, the next waits at least this long. 60 min is an estimate of three radiator response times. |
 
 ### Reset to factory defaults
@@ -1226,8 +1228,8 @@ changes, and closing the dialog cancels.
   the optimizer stays connected to the house: every assigned entity, the zone
   and emitter topology (the two-zone switch is written as the settings in force
   imply it), the hot-water tank, valve and wood-furnace layout, the price and
-  solar-forecast sources and the Tibber token, the plant diagram, the ECL110
-  MQTT wiring, the pre-fill device and the main fuse.
+  solar-forecast sources and the Tibber token, the plant diagram, the
+  heat-curve MQTT wiring, the pre-fill device and the main fuse.
 - **Learned values**: every learner starts again from the settings: the heat
   loss scale and lower-floor ratio, the comfort weight, COP, buffer and hot
   water cooling, the hot water profile and draws, defrost, the heat curve, the
@@ -1386,7 +1388,7 @@ would otherwise divide by zero inside the model:
   `dhw_legionella_interval_days` (0.01–60).
 - **Weather:** `wind_sensitivity_factor` (0–1),
   `rain_heat_loss_multiplier` (1–2).
-- **ECL110:** `ecl110_pid_time_constant_hours` (0.01–24),
+- **Heat curve:** `ecl110_pid_time_constant_hours` (0.01–24),
   `ecl110_displace_min` (−30–0), `ecl110_displace_max` (0–30).
 
 **`simulate_plan`** prices a hypothetical comfort choice against the current
@@ -1496,4 +1498,4 @@ file under `.storage/` that holds the rows.
 - [../README.md#removal](../README.md#removal) — removing the integration: what deleting the entry does, and what it leaves behind
 - [how-it-works.md](how-it-works.md) — the mechanisms behind these settings
 - [dashboard-card.md](dashboard-card.md) — the card, its own configuration keys, and the Setup tab
-- [ecl110.md](ecl110.md) — the heat-curve path in full: the Danfoss ECL110 over MQTT, and an offset `number` entity
+- [heat-curve.md](heat-curve.md) — heat-curve control in full, all three ways: MQTT topics (a Danfoss ECL110, for example), an offset `number` entity, and a stored curve parameter
diff --git a/docs/ecl110.md b/docs/ecl110.md
index 86bec52334..785f1a1361 100644
--- a/docs/ecl110.md
+++ b/docs/ecl110.md
@@ -1,326 +1,7 @@
-# Danfoss ECL110 control over MQTT
+# Moved: heat-curve control
 
-Some heat pumps are driven by a separate weather-compensated controller rather
-than by a switch. The Danfoss ECL110 is the common one here: it runs its own
-heat curve, and the standard way to bias that curve is the manual *displace*
-value — a parallel shift of the whole curve, in degrees.
-
-This page is for installs that have such a controller on MQTT, or a controller
-whose heat-curve offset Home Assistant exposes as a `number` entity
-([Without MQTT](#without-mqtt-a-number-entity)). Everything else in the
-integration works without either.
-
-## What the integration sends
-
-Each optimization produces two outputs for the controller:
-
-- `heat_pump_on` — whether supply should be enabled. A step is ON when the
-  power the plan books for it, space plus hot water together, is above 0.1 kW.
-  A step below the pump's modulation floor is the plan duty-cycling within that
-  step: the plan has already priced that energy as delivered, so supply is
-  enabled and the pump's own thermostat does the cycling. Half the modulation
-  floor answers a different question — whether a *measured* draw means the
-  compressor ran — and is not what this flag uses.
-- `displace_value` — the parallel shift, in °C, that corresponds to the planned
-  power for that step.
-
-The displace schedule is derived from the power schedule, not chosen
-separately: planned power is normalised against the pump's min and max, mapped
-onto the configured displace range, given a weather anticipation bias over the
-first eight hours (wind and rain push it up, expected sun pulls it down), and
-nudged up slightly below 0 °C outdoors. The result is then passed through the
-same first-order lag the controller itself is assumed to have, so the optimizer
-never asks for a change faster than the loop can follow.
-
-Before publishing, the coordinator adds the learned heat-curve bias if curve
-learning is enabled (it may only cool an over-hot curve, never heat, and is
-clamped well inside your configured range), clamps the result to your
-configured range, and rounds to a whole number — the ECL110 takes integers.
-
-The fixed modes do not plan a displace at all: comfort commands +4 °C (or your
-maximum, if that is lower), boost commands your maximum, off your minimum.
-
-The live peak guard can override any of them mid-window: while it is
-suppressing, it publishes the plan's displace minus 2 °C, and re-publishes the
-plan's own value when it releases.
-
-## Topics and payloads
-
-The preferred path is a plain number on the direct set topic:
-
-- `ecl110_displace_set_topic` (no default: empty leaves this arm off)
-
-```text
-4
-```
-
-For a setup that expects JSON, the same command is also published to the
-legacy topic when it is configured:
-
-- `ecl110_command_topic` (no default: empty leaves this arm off)
-
-```json
-{
-  "source": "heatpump_optimizer",
-  "reason": "scheduled_update",
-  "timestamp": "2026-01-01T12:00:00+00:00",
-  "command": {
-    "type": "ecl110_control",
-    "heat_pump_on": true,
-    "displace": 4
-  },
-  "context": {
-    "price": 1.23,
-    "mode": "pre_heat",
-    "pre_heat_urgency": 0.6
-  }
-}
-```
-
-The status topic is subscribed to, not written. Both shapes are accepted: a
-bare number, or a JSON object carrying `displace` (or `command.displace`) and
-optionally `effective_displace`, which overrides the modelled value below.
-
-Publishing goes through Home Assistant's own `mqtt.publish` service, so the
-MQTT integration has to be set up. The topics have no shipped
-default: each one is exactly what you stored, an empty or absent topic leaves
-that arm off, and nothing is published or subscribed until a topic is set —
-so an install without an ECL110 never touches these topics at all.
-
-## Options
-
-All eleven settings live on the options page **Heat curve control**, under
-*Advanced settings*: the eight below, and the three of the
-[offset entity](#without-mqtt-a-number-entity). They are not asked during
-initial setup, because only owners of such a controller can answer them; installs that never open the
-page run no ECL110 surface at all — the topic options below suggest empty and
-a topic only exists once you store one.
-
-| Option | Default | What it is |
-|---|---|---|
-| `ecl110_displace_set_topic` | *(empty)* | Topic the offset is published to, as a plain number |
-| `ecl110_command_topic` | *(empty)* | Legacy JSON command topic |
-| `ecl110_state_topic` | *(empty)* | Topic the controller reports its state on |
-| `ecl110_mqtt_qos` | 1 | MQTT quality of service, 0–2 |
-| `ecl110_mqtt_retain` | off | Retain the last offset on the broker |
-| `ecl110_displace_min` | −20 °C | Largest downward shift allowed, −30 to 0 |
-| `ecl110_displace_max` | +20 °C | Largest upward shift allowed, 0 to +30 |
-| `ecl110_pid_time_constant_hours` | 1.5 h | Roughly how long the controller takes to act on a new offset, 0.25–6 |
-
-The min and max are worth setting to what your curve can actually tolerate.
-They bound both the plan and every override, including the peak guard's.
-
-## Sensors
-
-Two sensors report the ECL110 path. Both follow the MQTT topics and the offset
-entity: with none stored they are **unavailable and disabled by default**, and on an install
-whose topics were configured at setup they are enabled. Both are
-**diagnostic**, so they sit with the other advisories on the device page. On an
-install that adds the topics later, enable them from the integration's device
-page.
-
-| Sensor | Unit | What it shows |
-|---|---|---|
-| ECL110 Displace | °C | The displace the current plan step asks for, falling back to the last value commanded or reported |
-| ECL110 Effective Displace | °C | The modelled shift the controller has actually reached; its attributes carry the legacy command topic and the status topic |
-
-## PI/PID dynamics
-
-The ECL110 does not jump to a new offset. Its manual documents PI-style loop
-dynamics, so a commanded shift arrives gradually, and treating the command as
-if it took effect instantly would make the thermal model expect heat that has
-not been delivered yet.
-
-The integration models this as a first-order lag with the time constant you
-configure: each interval, the effective displace moves a fraction
-`interval / time constant` of the remaining distance toward the command, and
-the result is clamped to the same min/max range. That modelled value is what
-**ECL110 Effective Displace** publishes, and it is replaced by the controller's
-own figure whenever a status payload reports `effective_displace`.
-
-The lag is applied twice on purpose: the optimizer smooths its planned displace
-schedule with it, so the plan only asks for shifts the controller can follow,
-and the coordinator then tracks what the controller has reached, so the model
-prices the heat that has actually arrived rather than the heat requested.
-
-## Without MQTT: a number entity
-
-The same displace can be written to a Home Assistant `number` (or
-`input_number`) that offsets your controller's heat curve, instead of or as
-well as the MQTT topics. Set **Heat-curve offset entity** on the same page.
-Every source of the displace reaches it unchanged: the plan, the fixed modes,
-boost, the peak guard and the learned curve bias. With curve learning on, an
-entity-only install now moves the real pump, where with no topic it moved
-nothing.
-
-**What the entity must be (kind *offset*).**
-A whole-curve offset whose neutral value is 0, which the controller forgets on
-its own restart. Not an absolute curve point, and not a parameter the
-controller stores in its non-volatile memory: those are kind *persistent*
-([below](#kind-persistent-a-stored-curve-parameter)), with its own write budget.
-Prefer *offset* wherever your controller has such an entity. The
-integration cannot tell a volatile entity from a stored one; your choice of
-entity and kind is the declaration. It does check one thing: an entity whose own range
-excludes 0 (for example 20 to 70) is refused at save, and again at every write,
-because it is a curve point, not an offset. An absolute entity that declares a
-range including 0 passes that check, so pick the offset entity deliberately.
-An entity the optimizer already writes for something else (a set-point, the
-valve, the compressor frequency or the mode) is refused too.
-
-**What is written.** The displace integer, the one the MQTT topics carry, as a
-temperature difference in the entity's own unit: kelvin, °C or no unit as is,
-°F times 9/5; any other unit is refused. It is bounded to
-±**Largest offset written to the entity** (default 3 K, 0.5 to 5 K) and to the
-entity's own range; where the entity's range is the narrower one, the value
-saturates and a warning is logged once. The 3 K default and its 5 K ceiling
-come from a web survey of controller documentation (handoff-body/r10-ghc-research
-52f5a442, "Recommended defaults"): ±5 K is the user heating correction a
-Luxtronik controller offers *[documented, a third-party app's docs]*, and 3 K is
-an *[estimate]* between that and the +1 to +2 offset steps an SG-Ready boost
-uses on NIBE *[documented]*. No source states a generic value.
-
-**How often.** Nothing is written while the entity already reads the target
-(within half its step). Each write is recorded: a reading that still differs
-within 90 s proves nothing; after that one more write is sent, and if the
-entity still does not hold it a warning is logged and that value is not sent
-again until the target changes or the reading matches. More than
-2 × 1440 / *optimization interval* writes in 24 hours (96 at the default 30
-minutes) is treated as a loop bug: refused and logged. An entity that is
-missing, unavailable, of another domain or unit, or whose service call
-fails, is not written and the failure is logged once; the MQTT topics are
-published first and are never affected by it. A stale plan is not a reason
-for silence: the peak guard and a mode change publish without checking the
-plan's age, as they do over MQTT.
-
-**Turning it off.** Switching the optimizer to off writes 0 to the entity,
-and so does unloading the integration (a reload after an options change, a
-disable, or Home Assistant stopping), so the curve is back where the
-controller had it. Only a value the optimizer wrote is restored; an install
-that never wrote leaves the entity alone. The MQTT topics get the same:
-once the optimizer has published to them, off and unload publish displace 0
-to each configured topic, retained when retain is on. While off, nothing
-else is written.
-A write the optimizer made before a crash is restored at the next start's
-first off or unload. When Home Assistant is stopping, the controller's own
-integration may already be gone; the 0 is then attempted, the failure logged,
-and the restore kept for the next off or unload. The MQTT topics are not
-written on off.
-
-**Example: a Luxtronik controller with the SHI interface** (alpha innotec,
-Novelan and others). python-luxtronik (Bouni/python-luxtronik at
-`02afea84bd5bf3ee87445de6f2a42b8029983169`) describes the SHI holding
-`heating_offset` as an offset applied to the current return-temperature
-set-point, volatile, and in effect only while the SHI heating mode is
-`offset`; the `luxtronik_shi` integration exposes it as a number in K, −20 to
-20, step 0.5. Measured by one user on one installation (an alpha innotec
-LWDV 91-1/3, 2026-11-07):
-+2 K raised the return target from 27.7 °C to 29.7 °C at that operating point,
-and the same user reports +1 K giving exactly +1 K at another outdoor
-temperature, so on that installation it behaves as a parallel shift. The optimizer does not own the heating mode: after a controller
-restart the mode can fall back to off, the offset reads back as written, and it
-has no effect, which the integration cannot detect. Check the mode after a
-controller restart. The heating-curve parameters themselves (the end point,
-and the setting the controller calls *Parallelverschiebung*) are stored
-parameters: kind *persistent*, not this kind.
-
-## Kind persistent: a stored curve parameter
-
-For a controller with no volatile offset, set **What the entity is** to
-*Persistent* and name the curve setting the controller stores (a foot point,
-a parallel shift, an end point). The options page then shows three more
-settings. Every write lands in the controller's non-volatile memory, which
-wears, so this kind writes far less often than kind *offset*. Prefer kind
-*offset* wherever your controller has a volatile register: on a Luxtronik,
-python-luxtronik's README states that parameter writes go to the controller's
-NAND memory while the SHI offset registers are volatile *[documented]*.
-
-**The baseline.** Before its first write the optimizer reads the entity and
-records that value, with the entity it was read from, in its own store. That
-recorded value is the baseline: every write is the baseline plus the displace,
-as a difference in the entity's unit (°F times 9/5), in whole steps of the
-entity, never more than **Largest displacement of a stored parameter** away
-from the baseline (default 3 K, 0.5 to 5 K) and never outside the entity's own
-range. A restart keeps the baseline, so a value the optimizer wrote is never
-mistaken for yours. The entity must read a value inside its own range when you
-save the page, and at every write; otherwise nothing is written.
-
-**Your own change wins.** If the entity, after a write and its 90 s grace,
-reads neither what the optimizer wrote nor what it read before that write, the
-change is yours: the baseline moves by the same amount, logged once, and the
-optimizer keeps displacing from there. A change that would move the baseline
-outside the entity's own range moves it to that range's edge instead, so the
-write back on off is always a value the entity accepts; the optimizer then
-displaces from that edge, which can write over part of your change. A reading still at the value before the
-write is a write that did not land: it is sent once more, and if it still
-does not land a warning is logged and that value is not sent again until the
-target changes.
-
-**How often.** Nothing is written while the entity already reads the target.
-After a write, the next waits at least **Least time between writes to a stored
-parameter** (default 60 min, 15 min to 6 h), counted on the wall clock so it
-holds across a restart. Writes in one local day, the write back on off
-included, are capped at **Most writes a day to a stored parameter** (default
-12, 0 to 48), and one is always kept back for that write back: a displace that
-would leave none is refused, logged once a day. 0 writes nothing at all, and
-neither does 1: its one write is the one kept back. The
-offset kind's 24-hour loop guard does not apply to this kind; the daily cap
-replaces it.
-
-**Turning it off.** Switching the optimizer off, and every unload (a reload
-after an options change, a disable, Home Assistant stopping), writes the
-baseline back to the entity it was read from, even if you have since named
-another entity or cleared it; the new entity is only read and written after
-that. A write back that fails is logged, kept, and tried again at the next off
-or unload. Removing the integration writes nothing: if a baseline is still
-owed then, a warning names the entity and the value to set by hand.
-
-**Where the defaults come from.** A web survey of controller documentation
-(handoff-body/r10-ghc-research 52f5a442, BODY.md, "Recommended defaults";
-*[documented]*, *[forum]*, *[estimate]* and *[snippet only]* mark the evidence)
-found no manufacturer endurance figure for a generic curve parameter, so these
-rest partly on forum posts and estimates; lower them if your controller's maker
-documents a quota.
-
-- Band, 3 K: Luxtronik's own user heating correction is ±5 K (Homey Luxtronik
-  app *[documented, third party]*), so 5 K is the maximum; NIBE's SG-Ready
-  boost uses +1 to +2 offset steps (NIBE S1256PC manual, p. 44
-  *[documented]*, the step-to-kelvin size *[estimate]*); 3 K between them is an
-  *[estimate]*.
-- Writes a day, 12: the only manufacturer write quota found is Daikin's 7000
-  control commands a year, about 19 a day (Daikin EKMBDXA design guide, quoted
-  on a forum *[forum]*, and the budulinek Daikin-P1P2 gateway's docs
-  *[documented]*); 12 a day for 15 years is 66 % of a 100 000-cycle SLC NAND
-  cell (Micron datasheet *[documented]*); choosing 12 rather than 19 rests on
-  wear levelling *[estimate]*. That is six shift-and-return episodes a day.
-  48 is above Daikin's quota. A NIBE figure of one million writes per
-  position *[forum, snippet only]* and ioBroker write counts *[forum, snippet
-  only]* could not be verified; nothing was found for Vaillant, Stiebel
-  Eltron, Mitsubishi or Panasonic.
-- Dwell, 60 min: about three response times of a radiator system, which warms
-  in 10 to 20 minutes (enpal.de *[forum]*); SG-Ready's 10-minute minimum
-  (gridx.ai *[documented, secondary]*) is below the 15-minute floor; a floor
-  heating system responds in 2 to 3 hours (GWF Stuttgart sheet *[forum]*), so
-  the range reaches 6 h.
-
-**A stored curve parameter is rarely a parallel shift.** Kind *persistent*
-writes the baseline plus the displace, which moves the water target by the
-displace only if the parameter shifts the whole curve. Many controllers' curve
-settings are not shifts. On a Luxtronik (controller firmware V3.92.3, from one
-outside contributor's static analysis of its heating-curve function, checked
-against the targets that contributor's controller reported *[third party]*) the
-two curve parameters are the end point E and the *Parallelverschiebung* F,
-5 to 35 °C, and the target at outdoor temperature T is
-
-    F + (E − 20) × (F − T) / (20 − (T − F) / 2)
-
-before the circuit's minimum and maximum clamp it (the return target for the
-heating circuit, the flow target for a mixing circuit). F is the outdoor
-temperature at which the target equals the outdoor temperature, and moving it
-changes the slope too: it is neither a parallel shift nor a foot point the
-curve turns about. With E = 30, raising F from 22 to 23 °C raises the target
-by 1.15 K at −10 °C, 1.25 K at 6 °C and 1.35 K at 15 °C, so a displace d
-written to F moves the return target by more than d, by an amount that varies
-with the outdoor temperature. On a Luxtronik, use kind *offset* on the SHI
-heating offset, which is the parallel shift (above); kind *persistent* on F
-over-shifts. Whether another controller's stored setting is a true parallel
-shift was not measured here.
+This page is now [Heat-curve control](heat-curve.md). The Danfoss ECL110 over
+MQTT is one of the three ways described there:
+[Over MQTT: topics and payloads](heat-curve.md#over-mqtt-topics-and-payloads).
+The other two are an [offset entity](heat-curve.md#without-mqtt-a-number-entity)
+and a [stored curve parameter](heat-curve.md#kind-persistent-a-stored-curve-parameter).
diff --git a/docs/heat-curve.md b/docs/heat-curve.md
new file mode 100644
index 0000000000..8a3b595b87
--- /dev/null
+++ b/docs/heat-curve.md
@@ -0,0 +1,346 @@
+# Heat-curve control
+
+Many heat pumps are driven by a weather-compensated controller that runs its
+own heat curve, rather than by a switch. The optimizer can bias that curve:
+in cheap hours it shifts the curve up, in expensive ones down. The shift is a
+*displace* — a parallel shift of the whole curve, in degrees.
+
+It reaches your controller in one of three ways. Use the one your controller
+offers; which way, and which entity, is your declaration, because the
+integration does not detect what kind of controller it is talking to:
+
+| Way | Your controller | Details |
+|---|---|---|
+| MQTT topics | takes its curve offset as a number (or a JSON command) on an MQTT topic — for example a Danfoss ECL110 through the [strutsfarm/ecl110](https://github.com/strutsfarm/ecl110) bridge, the controller this way was first built for | [Over MQTT: topics and payloads](#over-mqtt-topics-and-payloads) |
+| An offset entity (kind *offset*) | exposes a volatile whole-curve offset as a Home Assistant `number` entity, 0 neutral — for example a Luxtronik's SHI heating offset | [Without MQTT: a number entity](#without-mqtt-a-number-entity) |
+| A stored curve parameter (kind *persistent*) | has no volatile offset, only a curve setting it stores, exposed as a `number` entity | [Kind persistent: a stored curve parameter](#kind-persistent-a-stored-curve-parameter) |
+
+The MQTT topics and an entity can be used together. Everything else in the
+integration works without any of the three.
+
+## What the integration sends
+
+Each optimization produces two outputs for the controller:
+
+- `heat_pump_on` — whether supply should be enabled. A step is ON when the
+  power the plan books for it, space plus hot water together, is above 0.1 kW.
+  A step below the pump's modulation floor is the plan duty-cycling within that
+  step: the plan has already priced that energy as delivered, so supply is
+  enabled and the pump's own thermostat does the cycling. Half the modulation
+  floor answers a different question — whether a *measured* draw means the
+  compressor ran — and is not what this flag uses.
+- `displace_value` — the parallel shift, in °C, that corresponds to the planned
+  power for that step.
+
+The displace schedule is derived from the power schedule, not chosen
+separately: planned power is normalised against the pump's min and max, mapped
+onto the configured displace range, given a weather anticipation bias over the
+first eight hours (wind and rain push it up, expected sun pulls it down), and
+nudged up slightly below 0 °C outdoors. The result is then passed through the
+same first-order lag the controller itself is assumed to have, so the optimizer
+never asks for a change faster than the loop can follow.
+
+Before publishing, the coordinator adds the learned heat-curve bias if curve
+learning is enabled (it may only cool an over-hot curve, never heat, and is
+clamped well inside your configured range), clamps the result to your
+configured range, and rounds to a whole number. The rounding applies to every
+way, not only the controller that needs it: the ECL110, the first controller
+this was built for, takes integers.
+
+The fixed modes do not plan a displace at all: comfort commands +4 °C (or your
+maximum, if that is lower), boost commands your maximum, off your minimum.
+
+The live peak guard can override any of them mid-window: while it is
+suppressing, it publishes the plan's displace minus 2 °C, and re-publishes the
+plan's own value when it releases.
+
+## Over MQTT: topics and payloads
+
+This way is for a controller that takes its curve offset over MQTT. A Danfoss
+ECL110 does, through the strutsfarm/ecl110 bridge; any controller listening
+for a plain number on a topic can use the first topic below.
+
+The preferred path is a plain number on the direct set topic:
+
+- `ecl110_displace_set_topic` (no default: empty leaves this arm off)
+
+```text
+4
+```
+
+For a setup that expects JSON, the same command is also published to the
+legacy topic when it is configured:
+
+- `ecl110_command_topic` (no default: empty leaves this arm off)
+
+```json
+{
+  "source": "heatpump_optimizer",
+  "reason": "scheduled_update",
+  "timestamp": "2026-01-01T12:00:00+00:00",
+  "command": {
+    "type": "ecl110_control",
+    "heat_pump_on": true,
+    "displace": 4
+  },
+  "context": {
+    "price": 1.23,
+    "mode": "pre_heat",
+    "pre_heat_urgency": 0.6
+  }
+}
+```
+
+The status topic is subscribed to, not written. Both shapes are accepted: a
+bare number, or a JSON object carrying `displace` (or `command.displace`) and
+optionally `effective_displace`, which overrides the modelled value below.
+
+Publishing goes through Home Assistant's own `mqtt.publish` service, so the
+MQTT integration has to be set up. The topics have no shipped
+default: each one is exactly what you stored, an empty or absent topic leaves
+that arm off, and nothing is published or subscribed until a topic is set —
+so an install whose controller takes nothing over MQTT never touches these
+topics at all.
+
+## Options
+
+All eleven settings live on the options page **Heat curve control**, under
+*Advanced settings*: the eight below, and the three of the
+[offset entity](#without-mqtt-a-number-entity). They are not asked during
+initial setup, because only owners of such a controller can answer them; installs that never open the
+page run no heat-curve surface at all — the topic options below suggest empty and
+a topic only exists once you store one.
+
+The `ecl110_` prefix on the option keys is historical, from when MQTT to an
+ECL110 was the only way. The topics, quality of service and retain apply to
+MQTT alone; the displace range and the response time apply to every way.
+
+| Option | Default | What it is |
+|---|---|---|
+| `ecl110_displace_set_topic` | *(empty)* | Topic the offset is published to, as a plain number |
+| `ecl110_command_topic` | *(empty)* | Legacy JSON command topic |
+| `ecl110_state_topic` | *(empty)* | Topic the controller reports its state on |
+| `ecl110_mqtt_qos` | 1 | MQTT quality of service, 0–2 |
+| `ecl110_mqtt_retain` | off | Retain the last offset on the broker |
+| `ecl110_displace_min` | −20 °C | Largest downward shift allowed, −30 to 0 |
+| `ecl110_displace_max` | +20 °C | Largest upward shift allowed, 0 to +30 |
+| `ecl110_pid_time_constant_hours` | 1.5 h | Roughly how long the controller takes to act on a new offset, 0.25–6 |
+
+The min and max are worth setting to what your curve can actually tolerate.
+They bound both the plan and every override, including the peak guard's.
+
+## Sensors
+
+Two sensors report the displace, whichever way it goes out. Both follow the
+MQTT topics and the entity: with none stored they are **unavailable and disabled by default**, and on an install
+whose topics were configured at setup they are enabled. Both are
+**diagnostic**, so they sit with the other advisories on the device page. On an
+install that adds the topics later, enable them from the integration's device
+page.
+
+| Sensor | Unit | What it shows |
+|---|---|---|
+| Heat-Curve Displace | °C | The displace the current plan step asks for, falling back to the last value commanded or reported |
+| Heat-Curve Effective Displace | °C | The modelled shift the controller has actually reached; its attributes carry the legacy command topic and the status topic |
+
+## PI/PID dynamics
+
+A weather-compensated controller does not jump to a new offset. The ECL110's
+manual, for one, documents PI-style loop dynamics, and the integration assumes
+the same of every controller: a commanded shift arrives gradually, and treating
+the command as if it took effect instantly would make the thermal model expect
+heat that has not been delivered yet.
+
+The integration models this as a first-order lag with the time constant you
+configure: each interval, the effective displace moves a fraction
+`interval / time constant` of the remaining distance toward the command, and
+the result is clamped to the same min/max range. That modelled value is what
+**Heat-Curve Effective Displace** publishes, and it is replaced by the controller's
+own figure whenever a status payload reports `effective_displace`.
+
+The lag is applied twice on purpose: the optimizer smooths its planned displace
+schedule with it, so the plan only asks for shifts the controller can follow,
+and the coordinator then tracks what the controller has reached, so the model
+prices the heat that has actually arrived rather than the heat requested.
+
+## Without MQTT: a number entity
+
+The same displace can be written to a Home Assistant `number` (or
+`input_number`) that offsets your controller's heat curve, instead of or as
+well as the MQTT topics. Set **Heat-curve offset entity** on the same page.
+Every source of the displace reaches it unchanged: the plan, the fixed modes,
+boost, the peak guard and the learned curve bias. With curve learning on, an
+entity-only install now moves the real pump, where with no topic it moved
+nothing.
+
+**What the entity must be (kind *offset*).**
+A whole-curve offset whose neutral value is 0, which the controller forgets on
+its own restart. Not an absolute curve point, and not a parameter the
+controller stores in its non-volatile memory: those are kind *persistent*
+([below](#kind-persistent-a-stored-curve-parameter)), with its own write budget.
+Prefer *offset* wherever your controller has such an entity. The
+integration cannot tell a volatile entity from a stored one; your choice of
+entity and kind is the declaration. It does check one thing: an entity whose own range
+excludes 0 (for example 20 to 70) is refused at save, and again at every write,
+because it is a curve point, not an offset. An absolute entity that declares a
+range including 0 passes that check, so pick the offset entity deliberately.
+An entity the optimizer already writes for something else (a set-point, the
+valve, the compressor frequency or the mode) is refused too.
+
+**What is written.** The displace integer, the one the MQTT topics carry, as a
+temperature difference in the entity's own unit: kelvin, °C or no unit as is,
+°F times 9/5; any other unit is refused. It is bounded to
+±**Largest offset written to the entity** (default 3 K, 0.5 to 5 K) and to the
+entity's own range; where the entity's range is the narrower one, the value
+saturates and a warning is logged once. The 3 K default and its 5 K ceiling
+come from a web survey of controller documentation (handoff-body/r10-ghc-research
+52f5a442, "Recommended defaults"): ±5 K is the user heating correction a
+Luxtronik controller offers *[documented, a third-party app's docs]*, and 3 K is
+an *[estimate]* between that and the +1 to +2 offset steps an SG-Ready boost
+uses on NIBE *[documented]*. No source states a generic value.
+
+**How often.** Nothing is written while the entity already reads the target
+(within half its step). Each write is recorded: a reading that still differs
+within 90 s proves nothing; after that one more write is sent, and if the
+entity still does not hold it a warning is logged and that value is not sent
+again until the target changes or the reading matches. More than
+2 × 1440 / *optimization interval* writes in 24 hours (96 at the default 30
+minutes) is treated as a loop bug: refused and logged. An entity that is
+missing, unavailable, of another domain or unit, or whose service call
+fails, is not written and the failure is logged once; the MQTT topics are
+published first and are never affected by it. A stale plan is not a reason
+for silence: the peak guard and a mode change publish without checking the
+plan's age, as they do over MQTT.
+
+**Turning it off.** Switching the optimizer to off writes 0 to the entity,
+and so does unloading the integration (a reload after an options change, a
+disable, or Home Assistant stopping), so the curve is back where the
+controller had it. Only a value the optimizer wrote is restored; an install
+that never wrote leaves the entity alone. The MQTT topics get the same:
+once the optimizer has published to them, off and unload publish displace 0
+to each configured topic, retained when retain is on. While off, nothing
+else is written.
+A write the optimizer made before a crash is restored at the next start's
+first off or unload. When Home Assistant is stopping, the controller's own
+integration may already be gone; the 0 is then attempted, the failure logged,
+and the restore kept for the next off or unload. The MQTT topics are not
+written on off.
+
+**Example: a Luxtronik controller with the SHI interface** (alpha innotec,
+Novelan and others). python-luxtronik (Bouni/python-luxtronik at
+`02afea84bd5bf3ee87445de6f2a42b8029983169`) describes the SHI holding
+`heating_offset` as an offset applied to the current return-temperature
+set-point, volatile, and in effect only while the SHI heating mode is
+`offset`; the `luxtronik_shi` integration exposes it as a number in K, −20 to
+20, step 0.5. Measured by one user on one installation (an alpha innotec
+LWDV 91-1/3, 2026-11-07):
++2 K raised the return target from 27.7 °C to 29.7 °C at that operating point,
+and the same user reports +1 K giving exactly +1 K at another outdoor
+temperature, so on that installation it behaves as a parallel shift. The optimizer does not own the heating mode: after a controller
+restart the mode can fall back to off, the offset reads back as written, and it
+has no effect, which the integration cannot detect. Check the mode after a
+controller restart. The heating-curve parameters themselves (the end point,
+and the setting the controller calls *Parallelverschiebung*) are stored
+parameters: kind *persistent*, not this kind.
+
+## Kind persistent: a stored curve parameter
+
+For a controller with no volatile offset, set **What the entity is** to
+*Persistent* and name the curve setting the controller stores (a foot point,
+a parallel shift, an end point). The options page then shows three more
+settings. Every write lands in the controller's non-volatile memory, which
+wears, so this kind writes far less often than kind *offset*. Prefer kind
+*offset* wherever your controller has a volatile register: on a Luxtronik,
+python-luxtronik's README states that parameter writes go to the controller's
+NAND memory while the SHI offset registers are volatile *[documented]*.
+
+**The baseline.** Before its first write the optimizer reads the entity and
+records that value, with the entity it was read from, in its own store. That
+recorded value is the baseline: every write is the baseline plus the displace,
+as a difference in the entity's unit (°F times 9/5), in whole steps of the
+entity, never more than **Largest displacement of a stored parameter** away
+from the baseline (default 3 K, 0.5 to 5 K) and never outside the entity's own
+range. A restart keeps the baseline, so a value the optimizer wrote is never
+mistaken for yours. The entity must read a value inside its own range when you
+save the page, and at every write; otherwise nothing is written.
+
+**Your own change wins.** If the entity, after a write and its 90 s grace,
+reads neither what the optimizer wrote nor what it read before that write, the
+change is yours: the baseline moves by the same amount, logged once, and the
+optimizer keeps displacing from there. A change that would move the baseline
+outside the entity's own range moves it to that range's edge instead, so the
+write back on off is always a value the entity accepts; the optimizer then
+displaces from that edge, which can write over part of your change. A reading still at the value before the
+write is a write that did not land: it is sent once more, and if it still
+does not land a warning is logged and that value is not sent again until the
+target changes.
+
+**How often.** Nothing is written while the entity already reads the target.
+After a write, the next waits at least **Least time between writes to a stored
+parameter** (default 60 min, 15 min to 6 h), counted on the wall clock so it
+holds across a restart. Writes in one local day, the write back on off
+included, are capped at **Most writes a day to a stored parameter** (default
+12, 0 to 48), and one is always kept back for that write back: a displace that
+would leave none is refused, logged once a day. 0 writes nothing at all, and
+neither does 1: its one write is the one kept back. The
+offset kind's 24-hour loop guard does not apply to this kind; the daily cap
+replaces it.
+
+**Turning it off.** Switching the optimizer off, and every unload (a reload
+after an options change, a disable, Home Assistant stopping), writes the
+baseline back to the entity it was read from, even if you have since named
+another entity or cleared it; the new entity is only read and written after
+that. A write back that fails is logged, kept, and tried again at the next off
+or unload. Removing the integration writes nothing: if a baseline is still
+owed then, a warning names the entity and the value to set by hand.
+
+**Where the defaults come from.** A web survey of controller documentation
+(handoff-body/r10-ghc-research 52f5a442, BODY.md, "Recommended defaults";
+*[documented]*, *[forum]*, *[estimate]* and *[snippet only]* mark the evidence)
+found no manufacturer endurance figure for a generic curve parameter, so these
+rest partly on forum posts and estimates; lower them if your controller's maker
+documents a quota.
+
+- Band, 3 K: Luxtronik's own user heating correction is ±5 K (Homey Luxtronik
+  app *[documented, third party]*), so 5 K is the maximum; NIBE's SG-Ready
+  boost uses +1 to +2 offset steps (NIBE S1256PC manual, p. 44
+  *[documented]*, the step-to-kelvin size *[estimate]*); 3 K between them is an
+  *[estimate]*.
+- Writes a day, 12: the only manufacturer write quota found is Daikin's 7000
+  control commands a year, about 19 a day (Daikin EKMBDXA design guide, quoted
+  on a forum *[forum]*, and the budulinek Daikin-P1P2 gateway's docs
+  *[documented]*); 12 a day for 15 years is 66 % of a 100 000-cycle SLC NAND
+  cell (Micron datasheet *[documented]*); choosing 12 rather than 19 rests on
+  wear levelling *[estimate]*. That is six shift-and-return episodes a day.
+  48 is above Daikin's quota. A NIBE figure of one million writes per
+  position *[forum, snippet only]* and ioBroker write counts *[forum, snippet
+  only]* could not be verified; nothing was found for Vaillant, Stiebel
+  Eltron, Mitsubishi or Panasonic.
+- Dwell, 60 min: about three response times of a radiator system, which warms
+  in 10 to 20 minutes (enpal.de *[forum]*); SG-Ready's 10-minute minimum
+  (gridx.ai *[documented, secondary]*) is below the 15-minute floor; a floor
+  heating system responds in 2 to 3 hours (GWF Stuttgart sheet *[forum]*), so
+  the range reaches 6 h.
+
+**A stored curve parameter is rarely a parallel shift.** Kind *persistent*
+writes the baseline plus the displace, which moves the water target by the
+displace only if the parameter shifts the whole curve. Many controllers' curve
+settings are not shifts. On a Luxtronik (controller firmware V3.92.3, from one
+outside contributor's static analysis of its heating-curve function, checked
+against the targets that contributor's controller reported *[third party]*) the
+two curve parameters are the end point E and the *Parallelverschiebung* F,
+5 to 35 °C, and the target at outdoor temperature T is
+
+    F + (E − 20) × (F − T) / (20 − (T − F) / 2)
+
+before the circuit's minimum and maximum clamp it (the return target for the
+heating circuit, the flow target for a mixing circuit). F is the outdoor
+temperature at which the target equals the outdoor temperature, and moving it
+changes the slope too: it is neither a parallel shift nor a foot point the
+curve turns about. With E = 30, raising F from 22 to 23 °C raises the target
+by 1.15 K at −10 °C, 1.25 K at 6 °C and 1.35 K at 15 °C, so a displace d
+written to F moves the return target by more than d, by an amount that varies
+with the outdoor temperature. On a Luxtronik, use kind *offset* on the SHI
+heating offset, which is the parallel shift (above); kind *persistent* on F
+over-shifts. Whether another controller's stored setting is a true parallel
+shift was not measured here.
diff --git a/docs/how-it-works.md b/docs/how-it-works.md
index 797a51c760..301d24e663 100644
--- a/docs/how-it-works.md
+++ b/docs/how-it-works.md
@@ -55,7 +55,7 @@ survivable — a wrong guess about hour 20 is corrected forty times before hour
 sequenceDiagram
     autonumber
     participant C as Coordinator
-    participant P as Prices (Tibber + learned prior)
+    participant P as Prices (Tibber or a price sensor, + learned prior)
     participant W as Weather entity (HA)
     participant S as Your sensors
     participant M as Thermal model
@@ -74,7 +74,7 @@ sequenceDiagram
     O->>O: solve: hot water first (LP + repair),<br/>then space heating around it,<br/>then one co-optimization pass
     O-->>C: space + DHW slot plan
     C->>C: apply manual-plan pins (≤20 h),<br/>safety releases pinned-off slots
-    C->>E: publish plan sensors, switch heat pump,<br/>ECL110 displace / frequency advice
+    C->>E: publish plan sensors, switch heat pump,<br/>heat-curve displace / frequency advice
     Note over C: between plans the peak guard folds power-meter events<br/>and flips a flag (2 agree engage / 2 clear).<br/>It never solves — the next solve only reads the flag
     Note over M: afterwards: compare prediction vs reality,<br/>nudge learned parameters
 ```
@@ -736,7 +736,8 @@ zero confidence.
 
 Added per kWh moved through the grid, and increasingly by time of day: several
 Swedish grid companies charge roughly 25 öre/kWh more on winter weekdays 06–22.
-Tibber's price does not include it. Configure it on the Grid costs page — as
+Tibber's price does not include it, and a price sensor includes it only if you
+added it there yourself. Configure it on the Grid costs page — as
 time-of-use rules like `Nov-Mar Mon-Fri 06:00-22:00 = 0.25`, as a flat figure,
 or as a live sensor — and every planned hour is priced at spot *plus* fee, which
 moves load to nights and weekends in winter even when spot alone would not. The
@@ -1440,5 +1441,5 @@ does raising your minimum temperature. Both work.
 - [architecture.md](architecture.md) — module layout and the internal data flow.
 - [dashboard-card.md](dashboard-card.md) — the card, its options, the plan
   editor and the Setup page.
-- [ecl110.md](ecl110.md) — the optional ECL110 MQTT control path.
+- [heat-curve.md](heat-curve.md) — the optional heat-curve control path, three ways: MQTT topics (for example a Danfoss ECL110), an offset entity, a stored curve parameter.
 - [the archive](../dev/archive/backlog.md) — the delivered archive and the open findings.
diff --git a/docs/img/readme/mermaid-how-the-pieces-fit-dark.png b/docs/img/readme/mermaid-how-the-pieces-fit-dark.png
index 58eb532a73..affcf605c6 100644
Binary files a/docs/img/readme/mermaid-how-the-pieces-fit-dark.png and b/docs/img/readme/mermaid-how-the-pieces-fit-dark.png differ
diff --git a/docs/img/readme/mermaid-how-the-pieces-fit.png b/docs/img/readme/mermaid-how-the-pieces-fit.png
index 0bd6e40dc4..cbba858ad9 100644
Binary files a/docs/img/readme/mermaid-how-the-pieces-fit.png and b/docs/img/readme/mermaid-how-the-pieces-fit.png differ
diff --git a/docs/img/readme/mermaid-one-interval-dark.png b/docs/img/readme/mermaid-one-interval-dark.png
index 3a29fe44f3..7d62805d7d 100644
Binary files a/docs/img/readme/mermaid-one-interval-dark.png and b/docs/img/readme/mermaid-one-interval-dark.png differ
diff --git a/docs/img/readme/mermaid-one-interval.png b/docs/img/readme/mermaid-one-interval.png
index be729a5172..d69985147c 100644
Binary files a/docs/img/readme/mermaid-one-interval.png and b/docs/img/readme/mermaid-one-interval.png differ
diff --git a/docs/img/readme/mermaid-setup-flow-dark.png b/docs/img/readme/mermaid-setup-flow-dark.png
index 0b1b423a82..6d09b243bd 100644
Binary files a/docs/img/readme/mermaid-setup-flow-dark.png and b/docs/img/readme/mermaid-setup-flow-dark.png differ
diff --git a/docs/img/readme/mermaid-setup-flow.png b/docs/img/readme/mermaid-setup-flow.png
index 8942fd6532..06f46e4b6d 100644
Binary files a/docs/img/readme/mermaid-setup-flow.png and b/docs/img/readme/mermaid-setup-flow.png differ
diff --git a/docs/img/readme/mermaid_figures.json b/docs/img/readme/mermaid_figures.json
index 15eda0aa8d..2163081bba 100644
--- a/docs/img/readme/mermaid_figures.json
+++ b/docs/img/readme/mermaid_figures.json
@@ -1,28 +1,28 @@
 {
  "generator": "docs/img/readme/render_mermaid.mjs",
- "mermaid": "12.2.0",
+ "mermaid": "12.3.0",
  "source": "README.md",
  "figures": [
   {
    "png": "docs/img/readme/mermaid-how-the-pieces-fit.png",
    "png_dark": "docs/img/readme/mermaid-how-the-pieces-fit-dark.png",
-   "block_sha256": "6ba9cc1e027334c1a7c602a43ea25a455915adba2a0df4899fa54fc0f3ca88ac",
-   "png_sha256": "eb8cdfed82662cbd8b9648613429ef291eac4ffd3dcc8be3baea9cfa7f8eefc2",
-   "png_dark_sha256": "01ce3b59e9f686c2137979c042dcd1b0941c155d0de91fab5544f4d7c78ead9f"
+   "block_sha256": "5cec01a40765b96e51f85a4cd8e65a223162c034c58701cc43acb088668dac57",
+   "png_sha256": "20b98c412361363d5fd1a5dd172f60630f5de432351d3168db0740ad52afb1f6",
+   "png_dark_sha256": "aa93a61d222e40baff87f1fad1bbdb16b252db64c729156f5b73bfb2e040f2c4"
   },
   {
    "png": "docs/img/readme/mermaid-setup-flow.png",
    "png_dark": "docs/img/readme/mermaid-setup-flow-dark.png",
    "block_sha256": "e14dda04c9aa932ef2255be95c1220aacb2475423f59db71972a7d84d51e0e64",
-   "png_sha256": "c73d2f2ef5abb6a37d3ad77c88014afe4597ab7528a1ea63e61379b65dfc9910",
-   "png_dark_sha256": "5db63c422a7f59702ba53a18b5bf4810cb6d022ed3851546ae4778e6e71f0320"
+   "png_sha256": "57b03429cdbed126c15494b4a1515517447730685f9a418ac03fee39a47b43b4",
+   "png_dark_sha256": "3fd4a950793a122073d89662333d1dfb016a7317bbad47077ece1a0041e482d5"
   },
   {
    "png": "docs/img/readme/mermaid-one-interval.png",
    "png_dark": "docs/img/readme/mermaid-one-interval-dark.png",
-   "block_sha256": "bb15e14e25b60cfea3092931d189455da33c117b2fb86f50be0c3ed56287b30c",
-   "png_sha256": "07d112b5c02d8b89feee1aa36f1b4d0c6b27618ee0bbdbbab1d3f4b81dac4a80",
-   "png_dark_sha256": "aba7cb5fe671636c480c0b8de9d36afed3d33b72f224a0fa9fb0297e5738bdb7"
+   "block_sha256": "a9e8fdb9d6f7956aff52a9a123766d95cdbdce1764536b2edf050447f088429a",
+   "png_sha256": "5efa80ae8c2358b86510bc67f9b1d3f3603a8c5a1adf9b8ad3bafa53afd10b84",
+   "png_dark_sha256": "e3cefd8a1dbd3b885586cc07b3444a9b2180ec778c8853a6636233bde308537e"
   }
  ]
 }
diff --git a/docs/index.html b/docs/index.html
index 5ef7433080..e3d2d8b420 100644
--- a/docs/index.html
+++ b/docs/index.html
@@ -251,7 +251,7 @@ pre.yaml .k { color: var(--accent) } pre.yaml .c { color: var(--ink-2) }
 .cp .pp > div { padding: 14px 18px 2px 0; display: grid; gap: 4px; align-content: start }
 .cp .pp > div + div { padding-left: 18px; border-left: 1px solid var(--line) }
 .cp .pp .one { grid-column: 1 / -1 }
-.cp:has(#cp1:checked) .p1, .cp:has(#cp2:checked) .p2, .cp:has(#cp3:checked) .p3, .cp:has(#cp0:checked) .p0 { display: grid }
+.cp:has(#cp1:checked) .p1, .cp:has(#cp2:checked) .p2, .cp:has(#cp4:checked) .p4, .cp:has(#cp5:checked) .p5, .cp:has(#cp3:checked) .p3, .cp:has(#cp0:checked) .p0 { display: grid }
 @supports not selector(:has(*)) { .cp .pp { display: grid; margin-top: 8px } }
 @media (max-width: 640px) { .cp .pp { grid-template-columns: 1fr } .cp .pp > div + div { padding-left: 0; border-left: 0; border-top: 1px solid var(--line) } }
 /* each answer's own name, shown only where every answer shows at once */
@@ -414,7 +414,7 @@ footer a { padding-block: 9px }
       </div></li>
       <li class="st" data-step="4"><div class="in">
         <h3 data-copy><span class="n" aria-hidden="true">4</span>Act</h3>
-        <p class="q" data-src="README.md#how-it-works">Publish plan sensors, switch the heat pump, ECL110 displace / frequency advice</p>
+        <p class="q" data-src="README.md#how-it-works">Publish plan sensors, switch the heat pump, heat-curve displace / frequency advice</p>
         <p data-src="README.md#known-limitations">The plan is re-solved once per optimization interval — 30 minutes by default — and holds until the next solve.</p>
       </div></li>
       <li class="st" data-step="5"><div class="in">
@@ -484,7 +484,7 @@ footer a { padding-block: 9px }
       <p>The heat-loss scale, tank cooling rates, the COP curve and its defrost derate, the solar aperture, internal gains, how the loss splits between floors, your hot-water draw statistics, your revealed comfort preference, and a cool-only heat-curve correction are all estimated from your own house. Every learner is snapshotted weekly (the last eight are kept), and a drift watchdog can roll them back to the last healthy snapshot.</p></article>
     <article class="feat" data-src="README.md#what-it-does"><span class="ic" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L4 14h7l-1 8 9-12h-7z"/></svg></span>
       <h3 data-feature>Knows what your electricity actually costs.</h3>
-      <p>Tibber spot prices, time-of-use grid transfer fees, the monthly capacity (effekt) tariff and its billing clock, PV self-consumption priced at what consuming actually costs you, and a learned diurnal price prior for the part of the horizon that has not been published yet. A live peak guard and a main-fuse headroom advisor act inside the metering window the plan never saw, and a contract comparison settles the month three ways so you can see what your tariff choice is worth.</p></article>
+      <p>Spot prices from Tibber or a price sensor, time-of-use grid transfer fees, the monthly capacity (effekt) tariff and its billing clock, PV self-consumption priced at what consuming actually costs you, and a learned diurnal price prior for the part of the horizon that has not been published yet. A live peak guard and a main-fuse headroom advisor act inside the metering window the plan never saw, and a contract comparison settles the month three ways so you can see what your tariff choice is worth.</p></article>
     <article class="feat" data-src="README.md#what-it-does"><span class="ic" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4v6a4 4 0 0 0 4 4h8a4 4 0 0 1 4 4v2"/><circle cx="4" cy="4" r="1.5"/><circle cx="20" cy="20" r="1.5"/></svg></span>
       <h3 data-feature>Handles real plumbing.</h3>
       <p>A mixing valve is what lets a buffer tank store anything, so it is modelled explicitly. A wood furnace tank is a store of its own, drawn wood-first while it is usable, with an optional hot-water inlet coil. Your hydronic layout is picked from a catalog of drawn arrangements rather than described in prose, and circulation pumps — the hot-water loop and the space pump — are scheduled instead of left running.</p></article>
@@ -517,14 +517,18 @@ footer a { padding-block: 9px }
     <fieldset><legend><span class="eyebrow">Control path</span><span data-copy>How is your heat pump controlled?</span></legend>
       <div class="opts">
         <label><input type="radio" name="cp" id="cp1" checked>On/off switch</label>
-        <label><input type="radio" name="cp" id="cp2">ECL110 heat curve</label>
+        <label><input type="radio" name="cp" id="cp2">Heat curve, over MQTT</label>
+        <label><input type="radio" name="cp" id="cp4">Heat curve, offset entity</label>
+        <label><input type="radio" name="cp" id="cp5">Heat curve, stored parameter</label>
         <label><input type="radio" name="cp" id="cp3">Compressor frequency</label>
         <label data-copy><input type="radio" name="cp" id="cp0">None of these</label>
       </div>
     </fieldset>
     <div aria-live="polite">
       <div class="pp p1"><h3 class="pph">On/off switch</h3><div><span class="eyebrow">You provide</span><p>a switch that turns the heat pump on and off</p></div><div><span class="eyebrow">The optimizer writes</span><p>may turn it off during expensive hours</p></div></div>
-      <div class="pp p2"><h3 class="pph">ECL110 heat curve</h3><div><span class="eyebrow">You provide</span><p>a Danfoss ECL110-compatible weather-compensated controller, reachable over MQTT</p></div><div><span class="eyebrow">The optimizer writes</span><p>a heat-pump on/off decision and an integer parallel shift (displace) onto the controller's own heat curve</p></div></div>
+      <div class="pp p2"><h3 class="pph">Heat curve, over MQTT</h3><div><span class="eyebrow">You provide</span><p>a weather-compensated controller that takes its curve offset over MQTT (for example a Danfoss ECL110 through an MQTT bridge)</p></div><div><span class="eyebrow">The optimizer writes</span><p>a heat-pump on/off decision and an integer parallel shift (displace) onto the controller's own heat curve</p></div></div>
+      <div class="pp p4"><h3 class="pph">Heat curve, offset entity</h3><div><span class="eyebrow">You provide</span><p>a controller whose volatile whole-curve offset is a number entity (for example a Luxtronik SHI heating offset)</p></div><div><span class="eyebrow">The optimizer writes</span><p>the same displace as a temperature difference via number.set_value, bounded to ±3 K by default; 0 again when the optimizer is turned off or unloaded</p></div></div>
+      <div class="pp p5"><h3 class="pph">Heat curve, stored parameter</h3><div><span class="eyebrow">You provide</span><p>a controller with no volatile offset, whose stored curve setting is a number entity (kind persistent)</p></div><div><span class="eyebrow">The optimizer writes</span><p>its value before the first write plus the displace, within ±3 K and at most 12 writes a day by default; that value written back when the optimizer is turned off or unloaded</p></div></div>
       <div class="pp p3"><h3 class="pph">Compressor frequency</h3><div><span class="eyebrow">You provide</span><p>the compressor frequency exposed as a number entity (typically from Modbus or ESPHome)</p></div><div><span class="eyebrow">The optimizer writes</span><p>the recommended frequency via number.set_value — but only once you switch the mode to Control</p></div></div>
       <div class="pp p0"><h3 class="pph" data-copy>None of these</h3><div class="one"><span class="eyebrow" data-copy>With none of them</span><p>Each path is optional, the three are independent of each other, and with none of them configured “the plan is published on sensors for your own automations to act on”</p></div></div>
     </div>
@@ -597,7 +601,7 @@ footer a { padding-block: 9px }
     <a class="doc" data-doc="docs/dashboard-card.md" href="dashboard-card.html"><b>docs/dashboard-card.md</b><span>The card: options, interactions, editing limits</span></a>
     <a class="doc" data-doc="docs/automations.md" href="automations.html"><b>docs/automations.md</b><span>Complete automation examples using only the entities and services the integration creates</span></a>
     <a class="doc" data-doc="docs/architecture.md" href="architecture.html"><b>docs/architecture.md</b><span>Module map and how a plan is made, for anyone reading or changing the code</span></a>
-    <a class="doc" data-doc="docs/ecl110.md" href="ecl110.html"><b>docs/ecl110.md</b><span>ECL110 MQTT control</span></a>
+    <a class="doc" data-doc="docs/heat-curve.md" href="heat-curve.html"><b>docs/heat-curve.md</b><span>Heat-curve control, three ways: MQTT topics (for example a Danfoss ECL110), an offset entity, a stored curve parameter</span></a>
     <a class="doc" data-doc="DISCLAIMER.md" href="disclaimer.html"><b>DISCLAIMER.md</b><span>The full disclaimer</span></a>
   </div>
 </section>
diff --git a/docs/setup.md b/docs/setup.md
index e20f2ae860..2ed884cb33 100644
--- a/docs/setup.md
+++ b/docs/setup.md
@@ -42,6 +42,15 @@ Have two things to hand:
 Everything else — indoor and outdoor thermometers, tank probes, a power
 meter — is optional and can be pointed at later from the options pages.
 
+So is how the optimizer acts on the heat pump. The on/off switch is a picker on
+[Screen 2](#screen-2--optional-sensors); heat-curve control and compressor
+frequency control are not asked during setup and are set later from the
+options pages. Heat-curve control shifts your controller's own heat curve one
+of three ways: over MQTT topics (a Danfoss ECL110 through an MQTT bridge, for
+example), to an offset `number` entity, or to a curve setting the controller
+stores — see [heat-curve.md](heat-curve.md). With none of these, the plan is
+published on sensors for your own automations to act on.
+
 ## Adding the integration
 
 **Settings → Devices & services → Add integration → Heat Pump Cost
diff --git a/tests/closure.py b/tests/closure.py
index 8eeaaadb0e..8b08f21a49 100644
--- a/tests/closure.py
+++ b/tests/closure.py
@@ -698,6 +698,7 @@ INERT_EXCEPT = (
     # dependency, not inert prose, whatever directory it lives in.
     "docs/dashboard-card.md",
     "docs/ecl110.md",
+    "docs/heat-curve.md",
     "docs/how-it-works.md",
     "docs/setup.md",
     # R10-OUTSIDE-CONTRIBUTOR-CYCLE: the contributor guide is a reader doc
diff --git a/tests/closures.json b/tests/closures.json
index e29b8ded09..568361ac9c 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -1334,6 +1334,7 @@
    "docs/configuration.md",
    "docs/dashboard-card.md",
    "docs/ecl110.md",
+   "docs/heat-curve.md",
    "docs/how-it-works.md",
    "docs/img/brand/coffee.svg",
    "docs/img/card/advisor-dark.png",
@@ -3297,6 +3298,7 @@
    "docs/configuration.md",
    "docs/dashboard-card.md",
    "docs/ecl110.md",
+   "docs/heat-curve.md",
    "docs/how-it-works.md",
    "docs/setup.md",
    "hacs.json",
@@ -3480,7 +3482,7 @@
    "docs/automations.md",
    "docs/configuration.md",
    "docs/dashboard-card.md",
-   "docs/ecl110.md",
+   "docs/heat-curve.md",
    "docs/how-it-works.md",
    "docs/setup.md",
    "tests/md_tables.mjs",
@@ -4541,6 +4543,7 @@
    "dev/audit/harnesses/ux5_idle_codes.py",
    "dev/audit/harnesses/ux5_idle_codes_sites.py",
    "dev/audit/harnesses/ux9_flow_unit_guard.py",
+   "dev/audit/harnesses/vendor_text_census.py",
    "dev/audit/rounds/round10/D0/leads/tail_floor_own_bounds.py",
    "dev/audit/rounds/round10/D0/s1/race.py",
    "dev/audit/rounds/round10/D0/s2/ftol_race.py",
diff --git a/tests/doc_claims.py b/tests/doc_claims.py
index 9b94ebbad1..5adb22d18d 100644
--- a/tests/doc_claims.py
+++ b/tests/doc_claims.py
@@ -2804,6 +2804,8 @@ def check_product_page() -> None:
 # building nothing. The pages are then scanned for a third-party request.
 
 SITE_BUILD = ROOT / "tools" / "site" / "build_docs.mjs"
+# Old document path -> its new one; both addresses must resolve (build_docs.mjs's MOVED is the site half).
+MOVED_PAGES = {"docs/ecl110.md": "docs/heat-curve.md"}
 SITE_CHART = ROOT / "tools" / "site" / "day_chart.mjs"
 _BUILD_CACHE: dict[str, dict] = {}
 
@@ -2816,7 +2818,7 @@ def docs_build(root: pathlib.Path = ROOT) -> dict:
     key = str(root)
     if key in _BUILD_CACHE:
         return _BUILD_CACHE[key]
-    res: dict = {"rc": None, "fails": [], "stats": "", "pages": {}, "html": {}}
+    res: dict = {"rc": None, "fails": [], "stats": "", "pages": {}, "html": {}, "moved": {}}
     if not SITE_BUILD.is_file():
         res["fails"] = [f"{str(SITE_BUILD).removeprefix(str(ROOT) + os.sep)} does not exist"]
     else:
@@ -2839,6 +2841,8 @@ def docs_build(root: pathlib.Path = ROOT) -> dict:
                 if man.is_file():
                     res["pages"] = {b["src"]: b["out"] for b in json.loads(man.read_text())["built"]}
                     res["html"] = {b["out"]: (out / b["out"]).read_text() for b in json.loads(man.read_text())["built"]}
+                    res["moved"] = {m["src"]: (m["to"], (out / m["out"]).read_text())
+                                    for m in json.loads(man.read_text()).get("moved", [])}
     _BUILD_CACHE[key] = res
     return res
 
@@ -2873,6 +2877,14 @@ def check_docs_subpages() -> None:
     rows = {os.path.normpath(r) for r in re.findall(r"^\|\s*\[[^\]]+\]\(([^)#]+\.md)\)", _site_sections(README).get("documentation", ""), flags=re.M)}
     missing = sorted((rows | {"README.md"}) - set(b["pages"]))
     R.check("every README Documentation row is a built page", not missing, ", ".join(missing))
+    # A renamed page keeps its old address (R11-OWNER-GENERIC-CONTROL-TEXT): on GitHub the old file stays as a
+    # pointer to the new one, and on the site the build writes the old page name as a redirect to the new page.
+    for old, new in MOVED_PAGES.items():
+        to, page = b["moved"].get(old, ("", ""))
+        stub = (ROOT / old).read_text() if (ROOT / old).is_file() else ""
+        R.check(f"{old} still resolves: a pointer to {new} in the tree, a redirect to its page on the site",
+                to == b["pages"].get(new) and f'url={to}"' in page and f"]({os.path.basename(new)})" in stub,
+                f"site redirect to {to or 'nothing'}; the in-tree file links {new}: {f']({os.path.basename(new)})' in stub}")
     bad = [f"{n}: {m}" for n, h in sorted(b["html"].items()) for _, m in subpage_findings(h)]
     R.check("no built page requests anything from a third party", bool(b["html"]) and not bad,
             "; ".join(bad[:4]) + (f" (+{len(bad) - 4})" if len(bad) > 4 else "") or "no page built")
@@ -3272,7 +3284,7 @@ def check_image_dimensions() -> None:
 WIRING_DOCS = ("docs/architecture.md", "README.md", "dev/README.md")
 # The user pages R10-USER-DOCS-FINAL drafts and R10-USER-DOCS-VERIFY re-checks. README.md is in both sets.
 USER_PAGES = ("README.md", "docs/setup.md", "docs/configuration.md", "docs/how-it-works.md", "docs/automations.md",
-              "docs/dashboard-card.md", "docs/ecl110.md")
+              "docs/dashboard-card.md", "docs/heat-curve.md")
 _COMMENT = re.compile(r"<!--.*?-->", re.S)
 # (e) reads every reader doc that draws a mermaid block, plus the onboarding.
 MERMAID_STYLE_DOCS = ("README.md", "docs/architecture.md", "docs/how-it-works.md", "docs/configuration.md",
diff --git a/tests/entities.py b/tests/entities.py
index e9966d5b8e..4ff0b9c8a0 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -6655,9 +6655,9 @@ R.check(
 # Two the audit brief flagged and this PR deliberately leaves alone, pinned so
 # a future "consistency" pass does not add a device class to either.
 R.check(
-    "ECL110 Displace stays bare: it is a parallel shift, not a temperature",
-    getattr(by_name["ECL110 Displace"], "_attr_device_class", None) is None
-    and by_name["ECL110 Displace"]._attr_native_unit_of_measurement == "°C",
+    "Heat-Curve Displace stays bare: it is a parallel shift, not a temperature",
+    getattr(by_name["Heat-Curve Displace"], "_attr_device_class", None) is None
+    and by_name["Heat-Curve Displace"]._attr_native_unit_of_measurement == "°C",
     "a TEMPERATURE device class would have HA convert a delta as an absolute",
 )
 R.check(
diff --git a/tests/layout.json b/tests/layout.json
index 0746b077df..82045892b2 100644
--- a/tests/layout.json
+++ b/tests/layout.json
@@ -29,7 +29,7 @@
    "name": "docs",
    "why": "product documentation, read by users; the page URLs stay stable for users and HACS",
    "globs": [
-    "docs/{setup,configuration,automations,dashboard-card,ecl110,how-it-works,architecture,CONTRIBUTING}.md",
+    "docs/{setup,configuration,automations,dashboard-card,ecl110,heat-curve,how-it-works,architecture,CONTRIBUTING}.md",
     "docs/img/brand/*",
     "docs/img/card/*",
     "docs/img/model/*",
diff --git a/tests/md_tables.mjs b/tests/md_tables.mjs
index c1de466a1b..7e64a1fc0c 100644
--- a/tests/md_tables.mjs
+++ b/tests/md_tables.mjs
@@ -3,7 +3,7 @@
 // (dev/audit/rounds/round9/D5/s1/md_tables.mjs, evidence commit 79aa98ec).
 //
 // Metric (one line, unchanged from the finder): source lines in README.md +
-// docs/{architecture,automations,configuration,dashboard-card,ecl110,
+// docs/{architecture,automations,configuration,dashboard-card,heat-curve,
 // how-it-works,setup}.md that render in the wrong block -- (a) prose lines
 // (not starting with "|") rendered as table rows ("swallowed"), plus (b)
 // pipe-table rows rendered as paragraph text with raw pipes ("orphaned")
@@ -38,7 +38,7 @@ const md = new MarkdownIt('commonmark').enable('table')
 const FILES = [
   'README.md',
   ...['architecture', 'automations', 'configuration', 'dashboard-card',
-    'ecl110', 'how-it-works', 'setup'].map((n) => `docs/${n}.md`),
+    'heat-curve', 'how-it-works', 'setup'].map((n) => `docs/${n}.md`),
 ]
 
 export function analyse(text) {
diff --git a/tools/site/build_docs.mjs b/tools/site/build_docs.mjs
index 0fbd7f1e42..f38826355f 100644
--- a/tools/site/build_docs.mjs
+++ b/tools/site/build_docs.mjs
@@ -35,6 +35,9 @@ const BLOB = 'https://github.com/tvofi/heatpump_optimizer/blob/main/'
 const TREEURL = 'https://github.com/tvofi/heatpump_optimizer/tree/main/'
 // Rows of the README Documentation table the site links to GitHub instead of rendering, each with its reason.
 const EXCLUDE = {}
+// Documents that moved: the old page name keeps resolving, as a redirect to the new page with the fragment kept, so a
+// link to the old address still lands (docs/ecl110.md became docs/heat-curve.md; the old file stays as a pointer).
+const MOVED = { 'docs/ecl110.md': 'docs/heat-curve.md' }
 const errors = []
 const stats = { pages: 0, pageLinks: 0, anchors: 0, githubLinks: 0, images: 0, badges: 0, external: 0, mermaid: 0 }
 
@@ -244,8 +247,25 @@ ${mermaidJs(r.mermaid)}
   fs.writeFileSync(path.join(OUT, r.out), page)
 })
 stats.pages = rendered.length
+stats.redirects = 0
+const redirects = []
+for (const [from, to] of Object.entries(MOVED)) {
+  const target = PUBLISHED.get(to), old = outName(from)
+  // A tree without the old file has nothing to redirect (tests/doc_claims.py pins that this one keeps it).
+  if (!TREE.has(from)) continue
+  if (!target) { errors.push(`MOVED names ${to}, which is not a built page`); continue }
+  if ([...PUBLISHED.values()].includes(old)) { errors.push(`MOVED ${from}: ${old} is also a built page`); continue }
+  fs.writeFileSync(path.join(OUT, old), `<!doctype html>
+<html lang="en"><head><meta charset="utf-8"><title>Moved</title>
+<meta http-equiv="refresh" content="0; url=${esc(target)}"><link rel="canonical" href="${esc(target)}">
+<script>location.replace(${JSON.stringify(target)} + location.hash)</script></head>
+<body><p>This page moved to <a href="${esc(target)}">${esc(target)}</a>.</p></body></html>
+`)
+  redirects.push({ src: from, out: old, to: target })
+  stats.redirects++
+}
 if (!rendered.length) errors.push('ANCHOR: zero pages built')
-fs.writeFileSync(path.join(OUT, 'docs-manifest.json'), JSON.stringify({ built: rendered.map((r) => ({ src: r.src, out: r.out, mermaid: r.mermaid })), excluded: EXCLUDE }, null, 1))
+fs.writeFileSync(path.join(OUT, 'docs-manifest.json'), JSON.stringify({ built: rendered.map((r) => ({ src: r.src, out: r.out, mermaid: r.mermaid })), excluded: EXCLUDE, moved: redirects }, null, 1))
 console.log(Object.entries(stats).map(([k, v]) => `${k} ${v}`).join(', '))
 console.log(`built ${rendered.length} page(s): ${rendered.map((r) => r.out).join(', ')}; excluded ${Object.keys(EXCLUDE).join(', ') || 'none'}`)
 for (const e of errors) console.log('FAIL', e)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
