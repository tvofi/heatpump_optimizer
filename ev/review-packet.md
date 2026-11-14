# Review packet #3580
head: ec9645014c773759edfbf632829c7cbef272ba33
base: 513a07dfdc0daf09a054826974dbb64bfea9de27

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=132318711827 skipped
cancel-superseded id=132318714918 queued
prelude id=132318714675 queued
refresh id=132318714911 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 4d485f3d: R11-INTAKE-R10-RESIDUE
NOTE body item c07c1278: R11-INTAKE-R10-RESIDUE
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: SCOPED -- 23 script(s) run, 10 scoped out.
             no segment of this names a program this check knows
  ok         PYTHONPATH=tests/hastub:tests:custom_components python3 tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/env_drift.py --all e23124ff6e45bac1d48b4a775dad555a37965355
             `tests/env_drift.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/env_drift.py --all origin/main
             `tests/env_drift.py` is in the tree at this head
  unverified git grep -n -i -E "lowers the (heating )?target by|headroom sensor dormant|correct itself against|in front of every|spot cost only|measured delivery|first settled month|Heizziel um|värmemålet med|utrymmessensorn vilande|Reserve inaktiv|vorangestellt|Visas framför" -- ':!dev/' ':!tests/golden' ':!*.png'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 7 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/away.py b/custom_components/heatpump_optimizer/away.py
index 9fad06b00d..375ced98bb 100644
--- a/custom_components/heatpump_optimizer/away.py
+++ b/custom_components/heatpump_optimizer/away.py
@@ -1,8 +1,8 @@
 """Away / holiday mode with deadline-driven recovery.
 
 A week away is the single largest saving a heating system can offer: a deep
-setback plus hot water suppressed entirely, except for a legionella cycle timed
-to complete before return.
+setback plus hot water held only at its away minimum; the legionella cycle
+keeps its usual interval.
 
 What makes this more than an ``input_number`` is the **return time**. Knowing
 when the house must be comfortable again lets the optimizer buy the recovery
@@ -73,11 +73,6 @@ class AwayConfig:
     #: Setback targets while away.
     away_temperature: float = 16.0
     away_dhw_min_temperature: float = 20.0
-    #: Whether to keep the anti-legionella cycle running while away. Kept on by
-    #: default: a tank sitting lukewarm for a week is exactly the condition the
-    #: cycle exists for, and it is much cheaper to run it in a chosen cheap
-    #: hour than to arrive home to an overdue one.
-    legionella_before_return: bool = True
 
 
 @dataclass
diff --git a/custom_components/heatpump_optimizer/strings.json b/custom_components/heatpump_optimizer/strings.json
index 5b5bba0267..62eeb54f32 100644
--- a/custom_components/heatpump_optimizer/strings.json
+++ b/custom_components/heatpump_optimizer/strings.json
@@ -12,7 +12,7 @@
           "weather_entity": "Weather forecast"
         },
         "data_description": {
-          "name": "Shown in front of every sensor this integration creates.",
+          "name": "The title of this entry under Devices & services. Entity names use the fixed device name, Heat Pump Optimizer.",
           "price_source": "Tibber uses your API token. Entity reads a Home Assistant price sensor such as Nord Pool.",
           "tibber_token": "Used to read your hourly electricity prices. Create one at developer.tibber.com. Leave as-is unless it has changed. Not required when the price source is an entity.",
           "price_entity": "Required when the price source is an entity. Typical attributes are raw_today and raw_tomorrow.",
@@ -593,7 +593,7 @@
               "indoor_temp_entity": "Optional. The actual room temperature. Without it the optimizer trusts its own model, which drifts over time.",
               "outdoor_temp_entity": "Optional. A local outdoor thermometer is more accurate than the forecast for the current hour.",
               "space_setpoint_entity": "Optional. A number, helper or climate entity that is the pump's space-heating set-point. Used only to notice when the entity cannot be read. The optimizer never writes a recommended space set-point.",
-              "space_setpoint_unit": "Indoor temperature is correct for a room or thermostat set-point. Flow temperature is for a controller whose set-point is a water temperature it holds its supply at. Return temperature is for a controller that takes the set-point as its return-water target (assumed for a Luxtronik through its Smart Home Interface); it is written like a flow set-point, with the rated hold, the weather curve and the 25 °C gate moved 5 K down to return terms. A version before this option reads Return temperature as Indoor temperature: switch it back to Flow temperature before downgrading. Pointing an indoor target at a flow entity would command roughly 21 °C to something expecting 35–45 °C and badly underheat the house. The unit is a declaration: this integration never recommends a space set-point.",
+              "space_setpoint_unit": "Indoor temperature is correct for a room or thermostat set-point. Flow temperature is for a controller whose set-point is a water temperature it holds its supply at. Return temperature is for a controller that takes the set-point as its return-water target (assumed for a Luxtronik through its Smart Home Interface); it is written like a flow set-point, with the rated hold, the weather curve and the 25 °C gate moved 5 K down to return terms. A version before this option reads Return temperature as Indoor temperature: switch it back to Flow temperature before downgrading. Pointing an indoor target at a flow entity would command roughly 21 °C to something expecting 35–45 °C and badly underheat the house. The unit is a declaration: the optimizer never infers it from the entity, and only the heat-pump pre-fill suggests one.",
               "flow_min_lift_k": "With Pump duty control at Control, the water set-point written at the plan's lowest power is the measured inlet water plus this: heat-pump return, buffer tank, floor return or valve outlet, and for a Return temperature entity the first three only. 5 K suits a controller that holds its supply at the set-point. A controller that takes the number as its return-water target is assumed to run its compressor harder the further the target sits above the return, so it likely wants less; 1–2 K is a starting point to check against the compressor's measured frequency and power, not a measured value.",
               "flow_heat_c": "The water set-point written at full planned power, and the highest one written while the plan is in charge. 55 °C suits a supply target. For a Return temperature entity choose it above the highest return you see in normal heating plus the lift, and no higher than the controller accepts; on a low-temperature floor heating 35–40 °C may be a starting point to check against measurements. Below 30 °C is not offered: the gate that means off is 25 °C for a flow target and 20 °C for a return target.",
               "space_setpoint_power_feedback": "On by default. Acts only with Pump duty control at Control, a Flow or Return temperature unit and a heat-pump power sensor; otherwise nothing changes. After a 5-minute start hold, the water set-point is nudged down while the measured draw is above the planned level and up while it is below, and held while it is within 10 %, instead of following the rising inlet water. Off writes the inlet plus the lift. Requirements on the controller: its heating hysteresis at most the lift (Luxtronik: 0.5 K), or a stopped compressor is not started; its minimum return target below the heating-season return; its integration polling it at least every 10 minutes, and restoring its heating mode after a controller restart, since a Luxtronik Smart Home Interface drops every set value after 600 s without access; and no second tool writing the same registers (a Luxtronik then silently discards writes).",
@@ -1106,7 +1106,7 @@
           "pv_export_price_entity": "Use this instead if your compensation follows the spot price.",
           "pv_enabled": "Lets the plan run the heat pump on your own surplus instead of selling it for less than bought power costs.",
           "pv_peak_kw": "The array's rated peak output. Used to scale the production forecast.",
-          "pv_production_entity": "Optional. A live production sensor lets the forecast correct itself against what the roof actually delivers.",
+          "pv_production_entity": "Optional. A live production sensor replaces the forecast's current step with what the roof delivers now, capped at the installed capacity; later steps stay modelled.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
         }
       },
@@ -1123,7 +1123,7 @@
         "data_description": {
           "away_presence_entity": "A person, device tracker, calendar, or occupancy sensor. The Plan-page toggle wins until it is turned off. A person being 'not home' still means away when the toggle is off.",
           "holiday_calendar_entity": "When this calendar is on, holiday comfort and holiday hot-water windows replace the weekday/weekend pair for that day. Away setback still wins if away is active.",
-          "away_dhw_min_temperature": "The anti-legionella cycle still runs, and is timed to finish before you get back.",
+          "away_dhw_min_temperature": "The anti-legionella cycle still runs on its usual interval; it is not timed to your return.",
           "away_temperature": "The hold temperature while away. Low enough to save, high enough to protect the house and its plumbing.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
         }
@@ -1348,7 +1348,7 @@
               "dhw_disinfection_mode": "Observe reads the switch and never writes it. Control turns it on when an anti-legionella cycle starts and off when that cycle ends, but never turns it on while the pump's mode makes no hot water. It only turns off a switch it turned on itself: a switch that was already on when the cycle began is left alone. One limit: if you turn the switch on by hand while a cycle the optimizer started is running, it is turned off when that cycle ends, because the two cannot be told apart. Control needs the switch above.",
               "dhw_disinfection_switch_entity": "A switch or helper that starts the heat pump's own anti-legionella program. In observe mode its state is only read and shown on the hot water sensor's attributes; in control mode the integration turns it on when a disinfection cycle starts and off when that cycle ends.",
               "dhw_elastic_legionella_enabled": "Allow the anti-legionella cycle to run a day or two early when electricity is unusually cheap, instead of always waiting for its deadline. The deadline is still always honoured.",
-              "dhw_free_disinfection_enabled": "If a wood boiler, solar coil or immersion heater already gets the tank to the anti-legionella temperature and holds it there, count that as a completed cycle instead of running another one.",
+              "dhw_free_disinfection_enabled": "A wood boiler, solar coil or immersion heater that gets the tank to the anti-legionella temperature is counted as a completed cycle either way. Off, it counts at once; on, only after the tank has held that temperature for 20 minutes, so a short peak credits nothing.",
               "dhw_legionella_min_interval_days": "Never run anti-legionella cycles closer together than this, even on very cheap days.",
               "dhw_quantile_targets_enabled": "Learn how much hot water each time frame actually uses on a heavy day, and make the tank ready for that instead of for the average day. Needs a tank temperature sensor, configured hot water time frames, and a couple of weeks of evidence."
             }
@@ -1364,7 +1364,7 @@
           "after_save": "After saving"
         },
         "data_description": {
-          "vvc_pump_entity": "A switch controlling the hot water circulation (VVC) loop pump. When set, the pump only runs during your hot water time frames, plus the lead time below.",
+          "vvc_pump_entity": "A switch controlling the hot water circulation (VVC) loop pump. When set, the pump only runs during your hot water time frames, plus the lead time below. With hot water off or no time frames, it is left on.",
           "vvc_lead_minutes": "How long before a hot water time frame the circulation pump starts, so the loop is already hot when the time frame opens.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
         }
@@ -1383,7 +1383,7 @@
           "after_save": "After saving"
         },
         "data_description": {
-          "main_fuse_amperes": "The house's main fuse in amperes, from your grid contract. 0 leaves it unconfigured, which keeps the fuse advisor, the fuse guard and the headroom sensor dormant — there is no safe default to guess, and a wrong one would cap a bigger house.",
+          "main_fuse_amperes": "The house's main fuse in amperes, from your grid contract. 0 leaves it unconfigured, which keeps the fuse advisor and the fuse guard dormant, and leaves the headroom sensor following the capacity-tariff peak alone, unavailable without a capacity tariff — there is no safe default to guess, and a wrong one would cap a bigger house.",
           "main_fuse_phases": "Nearly every Swedish house is 3-phase.",
           "fuse_guard_enabled": "Caps the heat pump's planned power at what the fuse leaves after the rest of the house. If a cap would make the comfort floor unreachable, the plan says so on its sensors instead of silently going cold.",
           "peak_guard_enabled": "Watches the power meter live and, when the current metering window is projected to set a new billed peak, holds back electric hot water and nudges the heat curve down for the rest of that window. Needs a power meter; a cold tank or a breached comfort floor always wins over the guard.",
@@ -1434,7 +1434,7 @@
               "snow_roof_factor_enabled": "Assume less sun after heavy snowfall"
             },
             "data_description": {
-              "open_window_relax_enabled": "The open-window detector always pauses learning — that part is free and always on. This additionally lowers the heating target by 1 °C while a window appears to be open, so the heat pump stops paying to heat the garden. Off by default because it moves real heat: a wrongly flagged window means a slightly cooler house.",
+              "open_window_relax_enabled": "The open-window detector always pauses learning — that part is free and always on. This additionally lowers the coldest indoor temperature the plan accepts by 1 °C, never below 15 °C, while a window appears to be open, so the heat pump stops paying to heat the garden. Off by default because it moves real heat: a wrongly flagged window means a slightly cooler house.",
               "outage_recovery_enabled": "After an outage everything restarts at once — cold house, cold tank, the whole neighbourhood — which is exactly when a new monthly capacity peak gets set. With this on, a long gap in updates opens a two-hour recovery window where the capacity charge is taken seriously from the first kW and hot water queues 45 minutes behind space heating, unless the tank is genuinely low.",
               "precip_type_enabled": "Rain soaks the building envelope and increases heat loss; snow does not. Without this, a snowy forecast is treated as rain and the plan buys heat for a wet wall that stays dry. Needs the Open-Meteo connection for the snow data.",
               "snow_roof_factor_enabled": "For two days after heavy snowfall, the modelled solar gain is halved — snow on roof glazing and low winter panes blocks the sun the plan was counting on. Deliberately crude: a factor and a holding period, not a melt model."
diff --git a/custom_components/heatpump_optimizer/translations/de.json b/custom_components/heatpump_optimizer/translations/de.json
index dfba34dc50..13be79f936 100644
--- a/custom_components/heatpump_optimizer/translations/de.json
+++ b/custom_components/heatpump_optimizer/translations/de.json
@@ -12,7 +12,7 @@
           "weather_entity": "Wettervorhersage"
         },
         "data_description": {
-          "name": "Wird jedem Sensor vorangestellt, den diese Integration erstellt.",
+          "name": "Der Titel dieses Eintrags unter Geräte & Dienste. Entitätsnamen verwenden den festen Gerätenamen Heat Pump Optimizer.",
           "price_source": "Tibber verwendet dein API-Token. Entität liest einen Preissensor aus Home Assistant, z. B. Nord Pool.",
           "tibber_token": "Wird verwendet, um deine stündlichen Strompreise abzufragen. Erstelle eines unter developer.tibber.com. Unverändert lassen, solange es sich nicht geändert hat. Nicht erforderlich, wenn die Preisquelle eine Entität ist.",
           "price_entity": "Erforderlich, wenn die Preisquelle eine Entität ist. Typische Attribute sind raw_today und raw_tomorrow.",
@@ -593,7 +593,7 @@
               "indoor_temp_entity": "Optional. Die tatsächliche Raumtemperatur. Ohne sie vertraut der Optimierer seinem eigenen Modell, das mit der Zeit abdriftet.",
               "outdoor_temp_entity": "Optional. Ein lokales Außenthermometer ist für die aktuelle Stunde genauer als die Vorhersage.",
               "space_setpoint_entity": "Optional. Eine Zahl, ein Helfer oder eine Climate-Entität, die der Sollwert der Raumheizung der Pumpe ist. Dient nur dazu zu bemerken, wenn die Entität nicht gelesen werden kann. Der Optimierer schreibt nie einen empfohlenen Raumheizungs-Sollwert.",
-              "space_setpoint_unit": "Innentemperatur ist richtig für einen Raum- oder Thermostat-Sollwert. Vorlauftemperatur gilt für einen Regler, dessen Sollwert eine Wassertemperatur ist, auf der er seinen Vorlauf hält. Rücklauftemperatur gilt für einen Regler, der den Sollwert als Ziel für das Rücklaufwasser nimmt (angenommen für eine Luxtronik über ihre Smart-Home-Schnittstelle); er wird wie ein Vorlauf-Sollwert geschrieben, wobei der Nennhaltewert, die Wetterkurve und die 25-°C-Schwelle um 5 K nach unten in Rücklaufwerte verschoben werden. Eine Version vor dieser Option liest Rücklauftemperatur als Innentemperatur: Stelle vor einem Downgrade wieder auf Vorlauftemperatur um. Würde ein Innentemperaturziel auf eine Vorlauf-Entität zeigen, würden etwa 21 °C an ein Gerät gesendet, das 35–45 °C erwartet, und das Haus würde stark unterheizt. Die Einheit ist eine Angabe: Diese Integration empfiehlt nie einen Raumheizungs-Sollwert.",
+              "space_setpoint_unit": "Innentemperatur ist richtig für einen Raum- oder Thermostat-Sollwert. Vorlauftemperatur gilt für einen Regler, dessen Sollwert eine Wassertemperatur ist, auf der er seinen Vorlauf hält. Rücklauftemperatur gilt für einen Regler, der den Sollwert als Ziel für das Rücklaufwasser nimmt (angenommen für eine Luxtronik über ihre Smart-Home-Schnittstelle); er wird wie ein Vorlauf-Sollwert geschrieben, wobei der Nennhaltewert, die Wetterkurve und die 25-°C-Schwelle um 5 K nach unten in Rücklaufwerte verschoben werden. Eine Version vor dieser Option liest Rücklauftemperatur als Innentemperatur: Stelle vor einem Downgrade wieder auf Vorlauftemperatur um. Würde ein Innentemperaturziel auf eine Vorlauf-Entität zeigen, würden etwa 21 °C an ein Gerät gesendet, das 35–45 °C erwartet, und das Haus würde stark unterheizt. Die Einheit ist eine Angabe: Der Optimizer leitet sie nie aus der Entität ab, nur das Vorausfüllen aus einem Wärmepumpengerät schlägt eine vor.",
               "flow_min_lift_k": "Mit Steuerung der Pumpenfunktion auf Steuern ist der bei der niedrigsten Planleistung geschriebene Wasser-Sollwert das gemessene Eingangswasser plus dieser Wert: Wärmepumpen-Rücklauf, Pufferspeicher, Fußbodenrücklauf oder Ventilauslass, und bei einer Entität mit Rücklauftemperatur nur die ersten drei. 5 K passt zu einem Regler, der seinen Vorlauf auf dem Sollwert hält. Von einem Regler, der die Zahl als Ziel für das Rücklaufwasser nimmt, wird angenommen, dass er seinen Verdichter umso stärker laufen lässt, je weiter das Ziel über dem Rücklauf liegt, er will also wahrscheinlich weniger; 1–2 K ist ein Ausgangspunkt, der an der gemessenen Frequenz und Leistung des Verdichters zu prüfen ist, kein gemessener Wert.",
               "flow_heat_c": "Der bei voller Planleistung geschriebene Wasser-Sollwert und der höchste, der geschrieben wird, solange der Plan die Führung hat. 55 °C passt zu einem Vorlaufziel. Wähle ihn bei einer Entität mit Rücklauftemperatur über dem höchsten Rücklauf, den du im normalen Heizbetrieb siehst, plus dem Hub, und nicht höher, als der Regler annimmt; bei einer Niedertemperatur-Fußbodenheizung können 35–40 °C ein Ausgangspunkt sein, der an Messungen zu prüfen ist. Unter 30 °C wird nicht angeboten: Die Schwelle, die aus bedeutet, liegt bei 25 °C für ein Vorlaufziel und bei 20 °C für ein Rücklaufziel.",
               "space_setpoint_power_feedback": "Standardmäßig an. Wirkt nur mit Wärmepumpen-Betriebssteuerung auf Steuern, einer Einheit Vorlauf- oder Rücklauftemperatur und einem Leistungssensor der Wärmepumpe; sonst ändert sich nichts. Nach 5 Minuten Starthaltezeit wird der Wasser-Sollwert gesenkt, solange die gemessene Aufnahme über der geplanten Leistung liegt, angehoben, solange sie darunter liegt, und innerhalb von 10 % gehalten, statt dem steigenden Eingangswasser zu folgen. Aus schreibt das Eingangswasser plus den Hub. Anforderungen an den Regler: seine Heizungshysterese höchstens der Hub (Luxtronik: 0,5 K), sonst startet ein stehender Verdichter nicht; sein minimales Rücklaufziel unter dem Rücklauf der Heizperiode; seine Integration fragt ihn mindestens alle 10 Minuten ab und stellt nach einem Reglerneustart die Heizbetriebsart wieder her, denn eine Luxtronik Smart Home Interface verwirft nach 600 s ohne Zugriff alle gesetzten Werte; und kein zweites Werkzeug schreibt dieselben Register (eine Luxtronik verwirft Schreibvorgänge dann stillschweigend).",
@@ -1012,7 +1012,7 @@
               "building_preset_enabled": "Thermische Werte aus dem Gebäudetyp ableiten"
             },
             "data_description": {
-              "building_preset_enabled": "Wenn aktiviert, werden die Werte für thermische Masse, Wärmeverlust und Heizflächen auf der Seite „Thermisches Modell (Experte)“ bei jedem Speichern dieser Seite überschrieben."
+              "building_preset_enabled": "Wenn aktiviert, werden die Werte für thermische Masse, Wärmeverlust und Heizflächen auf der Seite „Thermisches Modell (Experten)“ bei jedem Speichern dieser Seite überschrieben."
             }
           },
           "climate": {
@@ -1033,7 +1033,7 @@
         }
       },
       "thermal_model": {
-        "title": "Thermisches Modell (Experte)",
+        "title": "Thermisches Modell (Experten)",
         "description": "Die Rohwerte hinter dem thermischen Modell, die sonst nur bei der Einrichtung abgefragt werden. Ein leer gelassenes Feld behält seinen aktuellen Wert und wird nie gespeichert, ein Haus mit einer Zone bleibt also ein Haus mit einer Zone – und durch Ausfüllen der Felder für zwei Zonen schaltet eine bestehende Installation das Zwei-Zonen-Modell ein.\n\n{preset_warning}",
         "data": {
           "house_thermal_mass": "Thermische Masse des Hauses (kWh/°C)",
@@ -1061,7 +1061,7 @@
         }
       },
       "grid": {
-        "title": "Netz-Spitzentarif",
+        "title": "Lastspitzentarif des Netzes",
         "description": "Kosten, die nicht einfach der Preis pro kWh sind. Viele schwedische Netzbetreiber berechnen zusätzlich eine monatliche Leistungsgebühr auf Basis deiner höchsten Stunden – Warmwasser und Heizung in dieselbe günstige Stunde zu legen kann dann mehr kosten, als es spart.",
         "data": {
           "peak_tariff_enabled": "Meine Netzrechnung enthält eine Leistungsgebühr",
@@ -1089,7 +1089,7 @@
         }
       },
       "solar_pv": {
-        "title": "Solaranlage",
+        "title": "Solarmodule",
         "description": "Wenn du Solarstrom erzeugst, ist es besser, Warmwasser oder den Pufferspeicher mit Überschuss zu beheizen, als ihn zum Vergütungssatz einzuspeisen. Teile dem Optimierer mit, wie deine Anlage aussieht, und er bewertet jede Stunde mit den tatsächlichen Kosten des Verbrauchs.",
         "data": {
           "pv_enabled": "Ich habe eine Solaranlage",
@@ -1106,7 +1106,7 @@
           "pv_export_price_entity": "Verwende stattdessen diese, wenn deine Vergütung dem Spotpreis folgt.",
           "pv_enabled": "Lässt den Plan die Wärmepumpe mit deinem eigenen Überschuss betreiben, statt ihn für weniger zu verkaufen, als Netzstrom kostet.",
           "pv_peak_kw": "Die Nennspitzenleistung der Anlage. Dient zur Skalierung der Erzeugungsprognose.",
-          "pv_production_entity": "Optional. Ein Live-Erzeugungssensor lässt die Prognose sich anhand dessen korrigieren, was das Dach tatsächlich liefert.",
+          "pv_production_entity": "Optional. Ein Live-Erzeugungssensor ersetzt den aktuellen Schritt der Prognose durch das, was das Dach gerade liefert, begrenzt auf die installierte Leistung; spätere Schritte bleiben modelliert.",
           "after_save": "Das Speichern wirkt sofort; hier wählst du, wohin der Dialog als Nächstes führt."
         }
       },
@@ -1123,7 +1123,7 @@
         "data_description": {
           "away_presence_entity": "Eine Person, ein Gerätetracker, ein Kalender oder ein Anwesenheitssensor. Der Schalter auf der Plan-Seite hat Vorrang, bis er ausgeschaltet wird. Eine Person, die „nicht zu Hause“ ist, bedeutet bei ausgeschaltetem Schalter weiterhin Abwesenheit.",
           "holiday_calendar_entity": "Wenn dieser Kalender eingeschaltet ist, ersetzen die Feiertags-Komfort- und Feiertags-Warmwasserfenster für diesen Tag das Paar aus Werktag und Wochenende. Die Abwesenheitsabsenkung hat weiterhin Vorrang, wenn Abwesenheit aktiv ist.",
-          "away_dhw_min_temperature": "Der Anti-Legionellen-Zyklus läuft weiterhin und wird so getimt, dass er vor deiner Rückkehr abgeschlossen ist.",
+          "away_dhw_min_temperature": "Der Anti-Legionellen-Zyklus läuft weiterhin in seinem üblichen Intervall; er wird nicht auf deine Rückkehr abgestimmt.",
           "away_temperature": "Die Haltetemperatur während der Abwesenheit. Niedrig genug zum Sparen, hoch genug, um das Haus und seine Leitungen zu schützen.",
           "after_save": "Das Speichern wirkt sofort; hier wählst du, wohin der Dialog als Nächstes führt."
         }
@@ -1348,7 +1348,7 @@
               "dhw_disinfection_mode": "Beobachten liest den Schalter und schreibt ihn nie. Steuern schaltet ihn ein, wenn eine Legionellenschaltung startet, und aus, wenn sie endet, schaltet ihn aber nie ein, solange der Modus der Pumpe kein Warmwasser erzeugt. Es wird nur ein Schalter ausgeschaltet, den die Integration selbst eingeschaltet hat: Ein Schalter, der bei Beginn des Zyklus schon eingeschaltet war, bleibt unberührt. Eine Einschränkung: Wenn du den Schalter von Hand einschaltest, während ein vom Optimierer gestarteter Zyklus läuft, wird er am Ende dieses Zyklus ausgeschaltet, weil sich beides nicht unterscheiden lässt. Steuern benötigt den obigen Schalter.",
               "dhw_disinfection_switch_entity": "Ein Schalter oder Helfer, der das eigene Legionellenprogramm der Wärmepumpe startet. Im Beobachtungsmodus wird sein Zustand nur gelesen und in den Attributen des Warmwasser-Sensors angezeigt; im Steuerungsmodus schaltet die Integration ihn ein, wenn ein Desinfektionszyklus startet, und aus, wenn er endet.",
               "dhw_elastic_legionella_enabled": "Erlaubt der Legionellenschaltung, ein bis zwei Tage früher zu laufen, wenn Strom ungewöhnlich günstig ist, statt immer bis zur Frist zu warten. Die Frist wird weiterhin immer eingehalten.",
-              "dhw_free_disinfection_enabled": "Wenn ein Holzkessel, eine Solarspirale oder ein Heizstab den Speicher bereits auf die Legionellentemperatur bringt und dort hält, wird das als abgeschlossener Zyklus gezählt, statt einen weiteren auszuführen.",
+              "dhw_free_disinfection_enabled": "Bringt ein Holzkessel, eine Solarspirale oder ein Heizstab den Speicher auf die Legionellentemperatur, wird das in jedem Fall als abgeschlossener Zyklus gezählt. Aus: sofort; ein: erst nachdem der Speicher diese Temperatur 20 Minuten gehalten hat, sodass eine kurze Spitze nichts anrechnet.",
               "dhw_legionella_min_interval_days": "Legionellenschaltungen laufen nie in kürzerem Abstand als diesem, auch nicht an sehr günstigen Tagen.",
               "dhw_quantile_targets_enabled": "Lernt, wie viel Warmwasser jeder Zeitraum an einem Tag mit hohem Verbrauch tatsächlich nutzt, und bereitet den Speicher darauf vor statt auf den Durchschnittstag. Benötigt einen Speichertemperatursensor, konfigurierte Warmwasser-Zeitfenster und einige Wochen an Daten."
             }
@@ -1364,7 +1364,7 @@
           "after_save": "Nach dem Speichern"
         },
         "data_description": {
-          "vvc_pump_entity": "Ein Schalter, der die Pumpe der Warmwasser-Zirkulation (VVC) steuert. Wenn gesetzt, läuft die Pumpe nur in deinen Warmwasser-Zeitfenstern plus der unten genannten Vorlaufzeit.",
+          "vvc_pump_entity": "Ein Schalter, der die Pumpe der Warmwasser-Zirkulation (VVC) steuert. Wenn gesetzt, läuft die Pumpe nur in deinen Warmwasser-Zeitfenstern plus der unten genannten Vorlaufzeit. Ist Warmwasser aus oder gibt es keine Zeitfenster, bleibt sie an.",
           "vvc_lead_minutes": "Wie lange vor einem Warmwasser-Zeitfenster die Zirkulationspumpe startet, damit die Leitung bei Beginn des Zeitfensters schon heiß ist.",
           "after_save": "Das Speichern wirkt sofort; hier legst du fest, wohin der Dialog als Nächstes führt."
         }
@@ -1383,7 +1383,7 @@
           "after_save": "Nach dem Speichern"
         },
         "data_description": {
-          "main_fuse_amperes": "Die Hauptsicherung des Hauses in Ampere, laut Netzanschlussvertrag. 0 lässt sie unkonfiguriert, wodurch der Sicherungsberater, der Sicherungswächter und der Sensor für die Reserve inaktiv bleiben – es gibt keinen sicheren Standardwert zum Raten, und ein falscher würde ein größeres Haus begrenzen.",
+          "main_fuse_amperes": "Die Hauptsicherung des Hauses in Ampere, laut Netzanschlussvertrag. 0 lässt sie unkonfiguriert, wodurch der Sicherungsberater und der Sicherungswächter inaktiv bleiben und der Sensor für die Reserve allein der Spitze des Lastspitzentarifs folgt, ohne Lastspitzentarif nicht verfügbar – es gibt keinen sicheren Standardwert zum Raten, und ein falscher würde ein größeres Haus begrenzen.",
           "main_fuse_phases": "Fast jedes schwedische Haus hat 3 Phasen.",
           "fuse_guard_enabled": "Begrenzt die geplante Leistung der Wärmepumpe auf das, was die Sicherung nach dem restlichen Haus noch übrig lässt. Wenn eine Begrenzung die Komfortuntergrenze unerreichbar machen würde, meldet der Plan das auf seinen Sensoren, statt stillschweigend kalt zu werden.",
           "peak_guard_enabled": "Überwacht den Stromzähler live und hält, wenn für das laufende Messfenster voraussichtlich eine neue abgerechnete Spitze entsteht, elektrisches Warmwasser zurück und senkt die Heizkurve für den Rest dieses Fensters leicht ab. Benötigt einen Stromzähler; ein kalter Speicher oder eine verletzte Komfortuntergrenze haben immer Vorrang vor dem Wächter.",
@@ -1434,7 +1434,7 @@
               "snow_roof_factor_enabled": "Nach starkem Schneefall weniger Sonne annehmen"
             },
             "data_description": {
-              "open_window_relax_enabled": "Die Erkennung offener Fenster pausiert das Lernen immer – das ist kostenlos und stets aktiv. Zusätzlich senkt diese Option das Heizziel um 1 °C, solange ein Fenster offen zu sein scheint, damit die Wärmepumpe nicht dafür zahlt, den Garten zu heizen. Standardmäßig aus, weil sie echte Wärme verschiebt: Ein fälschlich erkanntes Fenster bedeutet ein etwas kühleres Haus.",
+              "open_window_relax_enabled": "Die Erkennung offener Fenster pausiert das Lernen immer – das ist kostenlos und stets aktiv. Zusätzlich senkt diese Option die niedrigste Raumtemperatur, die der Plan zulässt, um 1 °C, nie unter 15 °C, solange ein Fenster offen zu sein scheint, damit die Wärmepumpe nicht dafür zahlt, den Garten zu heizen. Standardmäßig aus, weil sie echte Wärme verschiebt: Ein fälschlich erkanntes Fenster bedeutet ein etwas kühleres Haus.",
               "outage_recovery_enabled": "Nach einem Ausfall läuft alles gleichzeitig wieder an – kaltes Haus, kalter Speicher, die ganze Nachbarschaft – und genau dann entsteht eine neue monatliche Leistungsspitze. Ist dies aktiviert, öffnet eine lange Lücke bei den Aktualisierungen ein zweistündiges Wiederanlauffenster, in dem der Leistungspreis vom ersten kW an ernst genommen wird und Warmwasser 45 Minuten hinter der Raumheizung ansteht, außer der Speicher ist wirklich knapp.",
               "precip_type_enabled": "Regen durchfeuchtet die Gebäudehülle und erhöht den Wärmeverlust; Schnee nicht. Ohne diese Option wird eine Schneeprognose wie Regen behandelt, und der Plan kauft Wärme für eine nasse Wand, die trocken bleibt. Benötigt die Open-Meteo-Verbindung für die Schneedaten.",
               "snow_roof_factor_enabled": "Für zwei Tage nach starkem Schneefall wird der modellierte solare Wärmeeintrag halbiert – Schnee auf Dachfenstern und tiefen Winterscheiben blockiert die Sonne, mit der der Plan gerechnet hat. Bewusst grob: ein Faktor und eine Haltedauer, kein Schmelzmodell."
@@ -1518,7 +1518,7 @@
         }
       },
       "modbus_prefill": {
-        "title": "Aus einem Wärmepumpen-Gerät vorbefüllen",
+        "title": "Aus einem Wärmepumpengerät vorbefüllen",
         "description": "Für eine Rotenso Windmi oder eine andere von GCHV gebaute Wärmepumpe, die über das Modbus-Paket des Projekts tuya_heat_pump ausgelesen wird. Nenne den Entitäts-Präfix des Pakets und sende ab: Das nächste Formular schlägt Werte vor, die aus den eigenen Registern der Pumpe gelesen wurden – die Warmwasser-Sollwerte und den Zeitplan, die Legionellentage, den Nachtmodus-Zeitplan, ob die Pumpe nach Wassertemperatur regelt, und die eigenen Sensoren der Pumpe für noch leere Sensorplätze. Bearbeite oder leere beliebige davon; nur was du behältst, wird gespeichert, und ein geleertes Feld bleibt, wie es war. Nichts über das Haus oder sein Heizsystem lässt sich auf diese Weise auslesen.\n\nGelesene Entitäten: {found}. Register für den Typ des Zuheizers: {backup_heater_type} – jeder Wert außer 7 bedeutet, dass die Pumpe eine eigene elektrische Heizung hat, die von den Heizer-Plätzen bei der Wärmepumpen-Telemetrie überwacht werden soll.\n\nRollen, die aus dem NAMEN einer Entität statt aus einer veröffentlichten Definition gelesen wurden – die Seite kann diese nicht prüfen, prüfe daher jede vor dem Speichern: {name_matched}. Rollen aus veröffentlichten Definitionen, nach Quelle: {matched_sources}.",
         "data": {
           "prefill_device": "Wärmepumpen-Gerät (optional)",
diff --git a/custom_components/heatpump_optimizer/translations/en.json b/custom_components/heatpump_optimizer/translations/en.json
index 5b5bba0267..62eeb54f32 100644
--- a/custom_components/heatpump_optimizer/translations/en.json
+++ b/custom_components/heatpump_optimizer/translations/en.json
@@ -12,7 +12,7 @@
           "weather_entity": "Weather forecast"
         },
         "data_description": {
-          "name": "Shown in front of every sensor this integration creates.",
+          "name": "The title of this entry under Devices & services. Entity names use the fixed device name, Heat Pump Optimizer.",
           "price_source": "Tibber uses your API token. Entity reads a Home Assistant price sensor such as Nord Pool.",
           "tibber_token": "Used to read your hourly electricity prices. Create one at developer.tibber.com. Leave as-is unless it has changed. Not required when the price source is an entity.",
           "price_entity": "Required when the price source is an entity. Typical attributes are raw_today and raw_tomorrow.",
@@ -593,7 +593,7 @@
               "indoor_temp_entity": "Optional. The actual room temperature. Without it the optimizer trusts its own model, which drifts over time.",
               "outdoor_temp_entity": "Optional. A local outdoor thermometer is more accurate than the forecast for the current hour.",
               "space_setpoint_entity": "Optional. A number, helper or climate entity that is the pump's space-heating set-point. Used only to notice when the entity cannot be read. The optimizer never writes a recommended space set-point.",
-              "space_setpoint_unit": "Indoor temperature is correct for a room or thermostat set-point. Flow temperature is for a controller whose set-point is a water temperature it holds its supply at. Return temperature is for a controller that takes the set-point as its return-water target (assumed for a Luxtronik through its Smart Home Interface); it is written like a flow set-point, with the rated hold, the weather curve and the 25 °C gate moved 5 K down to return terms. A version before this option reads Return temperature as Indoor temperature: switch it back to Flow temperature before downgrading. Pointing an indoor target at a flow entity would command roughly 21 °C to something expecting 35–45 °C and badly underheat the house. The unit is a declaration: this integration never recommends a space set-point.",
+              "space_setpoint_unit": "Indoor temperature is correct for a room or thermostat set-point. Flow temperature is for a controller whose set-point is a water temperature it holds its supply at. Return temperature is for a controller that takes the set-point as its return-water target (assumed for a Luxtronik through its Smart Home Interface); it is written like a flow set-point, with the rated hold, the weather curve and the 25 °C gate moved 5 K down to return terms. A version before this option reads Return temperature as Indoor temperature: switch it back to Flow temperature before downgrading. Pointing an indoor target at a flow entity would command roughly 21 °C to something expecting 35–45 °C and badly underheat the house. The unit is a declaration: the optimizer never infers it from the entity, and only the heat-pump pre-fill suggests one.",
               "flow_min_lift_k": "With Pump duty control at Control, the water set-point written at the plan's lowest power is the measured inlet water plus this: heat-pump return, buffer tank, floor return or valve outlet, and for a Return temperature entity the first three only. 5 K suits a controller that holds its supply at the set-point. A controller that takes the number as its return-water target is assumed to run its compressor harder the further the target sits above the return, so it likely wants less; 1–2 K is a starting point to check against the compressor's measured frequency and power, not a measured value.",
               "flow_heat_c": "The water set-point written at full planned power, and the highest one written while the plan is in charge. 55 °C suits a supply target. For a Return temperature entity choose it above the highest return you see in normal heating plus the lift, and no higher than the controller accepts; on a low-temperature floor heating 35–40 °C may be a starting point to check against measurements. Below 30 °C is not offered: the gate that means off is 25 °C for a flow target and 20 °C for a return target.",
               "space_setpoint_power_feedback": "On by default. Acts only with Pump duty control at Control, a Flow or Return temperature unit and a heat-pump power sensor; otherwise nothing changes. After a 5-minute start hold, the water set-point is nudged down while the measured draw is above the planned level and up while it is below, and held while it is within 10 %, instead of following the rising inlet water. Off writes the inlet plus the lift. Requirements on the controller: its heating hysteresis at most the lift (Luxtronik: 0.5 K), or a stopped compressor is not started; its minimum return target below the heating-season return; its integration polling it at least every 10 minutes, and restoring its heating mode after a controller restart, since a Luxtronik Smart Home Interface drops every set value after 600 s without access; and no second tool writing the same registers (a Luxtronik then silently discards writes).",
@@ -1106,7 +1106,7 @@
           "pv_export_price_entity": "Use this instead if your compensation follows the spot price.",
           "pv_enabled": "Lets the plan run the heat pump on your own surplus instead of selling it for less than bought power costs.",
           "pv_peak_kw": "The array's rated peak output. Used to scale the production forecast.",
-          "pv_production_entity": "Optional. A live production sensor lets the forecast correct itself against what the roof actually delivers.",
+          "pv_production_entity": "Optional. A live production sensor replaces the forecast's current step with what the roof delivers now, capped at the installed capacity; later steps stay modelled.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
         }
       },
@@ -1123,7 +1123,7 @@
         "data_description": {
           "away_presence_entity": "A person, device tracker, calendar, or occupancy sensor. The Plan-page toggle wins until it is turned off. A person being 'not home' still means away when the toggle is off.",
           "holiday_calendar_entity": "When this calendar is on, holiday comfort and holiday hot-water windows replace the weekday/weekend pair for that day. Away setback still wins if away is active.",
-          "away_dhw_min_temperature": "The anti-legionella cycle still runs, and is timed to finish before you get back.",
+          "away_dhw_min_temperature": "The anti-legionella cycle still runs on its usual interval; it is not timed to your return.",
           "away_temperature": "The hold temperature while away. Low enough to save, high enough to protect the house and its plumbing.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
         }
@@ -1348,7 +1348,7 @@
               "dhw_disinfection_mode": "Observe reads the switch and never writes it. Control turns it on when an anti-legionella cycle starts and off when that cycle ends, but never turns it on while the pump's mode makes no hot water. It only turns off a switch it turned on itself: a switch that was already on when the cycle began is left alone. One limit: if you turn the switch on by hand while a cycle the optimizer started is running, it is turned off when that cycle ends, because the two cannot be told apart. Control needs the switch above.",
               "dhw_disinfection_switch_entity": "A switch or helper that starts the heat pump's own anti-legionella program. In observe mode its state is only read and shown on the hot water sensor's attributes; in control mode the integration turns it on when a disinfection cycle starts and off when that cycle ends.",
               "dhw_elastic_legionella_enabled": "Allow the anti-legionella cycle to run a day or two early when electricity is unusually cheap, instead of always waiting for its deadline. The deadline is still always honoured.",
-              "dhw_free_disinfection_enabled": "If a wood boiler, solar coil or immersion heater already gets the tank to the anti-legionella temperature and holds it there, count that as a completed cycle instead of running another one.",
+              "dhw_free_disinfection_enabled": "A wood boiler, solar coil or immersion heater that gets the tank to the anti-legionella temperature is counted as a completed cycle either way. Off, it counts at once; on, only after the tank has held that temperature for 20 minutes, so a short peak credits nothing.",
               "dhw_legionella_min_interval_days": "Never run anti-legionella cycles closer together than this, even on very cheap days.",
               "dhw_quantile_targets_enabled": "Learn how much hot water each time frame actually uses on a heavy day, and make the tank ready for that instead of for the average day. Needs a tank temperature sensor, configured hot water time frames, and a couple of weeks of evidence."
             }
@@ -1364,7 +1364,7 @@
           "after_save": "After saving"
         },
         "data_description": {
-          "vvc_pump_entity": "A switch controlling the hot water circulation (VVC) loop pump. When set, the pump only runs during your hot water time frames, plus the lead time below.",
+          "vvc_pump_entity": "A switch controlling the hot water circulation (VVC) loop pump. When set, the pump only runs during your hot water time frames, plus the lead time below. With hot water off or no time frames, it is left on.",
           "vvc_lead_minutes": "How long before a hot water time frame the circulation pump starts, so the loop is already hot when the time frame opens.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
         }
@@ -1383,7 +1383,7 @@
           "after_save": "After saving"
         },
         "data_description": {
-          "main_fuse_amperes": "The house's main fuse in amperes, from your grid contract. 0 leaves it unconfigured, which keeps the fuse advisor, the fuse guard and the headroom sensor dormant — there is no safe default to guess, and a wrong one would cap a bigger house.",
+          "main_fuse_amperes": "The house's main fuse in amperes, from your grid contract. 0 leaves it unconfigured, which keeps the fuse advisor and the fuse guard dormant, and leaves the headroom sensor following the capacity-tariff peak alone, unavailable without a capacity tariff — there is no safe default to guess, and a wrong one would cap a bigger house.",
           "main_fuse_phases": "Nearly every Swedish house is 3-phase.",
           "fuse_guard_enabled": "Caps the heat pump's planned power at what the fuse leaves after the rest of the house. If a cap would make the comfort floor unreachable, the plan says so on its sensors instead of silently going cold.",
           "peak_guard_enabled": "Watches the power meter live and, when the current metering window is projected to set a new billed peak, holds back electric hot water and nudges the heat curve down for the rest of that window. Needs a power meter; a cold tank or a breached comfort floor always wins over the guard.",
@@ -1434,7 +1434,7 @@
               "snow_roof_factor_enabled": "Assume less sun after heavy snowfall"
             },
             "data_description": {
-              "open_window_relax_enabled": "The open-window detector always pauses learning — that part is free and always on. This additionally lowers the heating target by 1 °C while a window appears to be open, so the heat pump stops paying to heat the garden. Off by default because it moves real heat: a wrongly flagged window means a slightly cooler house.",
+              "open_window_relax_enabled": "The open-window detector always pauses learning — that part is free and always on. This additionally lowers the coldest indoor temperature the plan accepts by 1 °C, never below 15 °C, while a window appears to be open, so the heat pump stops paying to heat the garden. Off by default because it moves real heat: a wrongly flagged window means a slightly cooler house.",
               "outage_recovery_enabled": "After an outage everything restarts at once — cold house, cold tank, the whole neighbourhood — which is exactly when a new monthly capacity peak gets set. With this on, a long gap in updates opens a two-hour recovery window where the capacity charge is taken seriously from the first kW and hot water queues 45 minutes behind space heating, unless the tank is genuinely low.",
               "precip_type_enabled": "Rain soaks the building envelope and increases heat loss; snow does not. Without this, a snowy forecast is treated as rain and the plan buys heat for a wet wall that stays dry. Needs the Open-Meteo connection for the snow data.",
               "snow_roof_factor_enabled": "For two days after heavy snowfall, the modelled solar gain is halved — snow on roof glazing and low winter panes blocks the sun the plan was counting on. Deliberately crude: a factor and a holding period, not a melt model."
diff --git a/custom_components/heatpump_optimizer/translations/sv.json b/custom_components/heatpump_optimizer/translations/sv.json
index ae8c426623..4932421778 100644
--- a/custom_components/heatpump_optimizer/translations/sv.json
+++ b/custom_components/heatpump_optimizer/translations/sv.json
@@ -12,7 +12,7 @@
           "price_entity": "Prissensor (Nord Pool eller liknande)"
         },
         "data_description": {
-          "name": "Visas framför alla sensorer som integrationen skapar.",
+          "name": "Titeln på den här posten under Enheter och tjänster. Entiteternas namn använder det fasta enhetsnamnet Heat Pump Optimizer.",
           "tibber_token": "Används för att läsa dina timpriser på el. Skapa en på developer.tibber.com. Lämna som den är om den inte har ändrats. Krävs inte när priskällan är en entitet.",
           "weather_entity": "Härifrån hämtas prognos för utomhustemperatur, vind och regn. Optimeringen planerar 24 timmar framåt och kräver därför en prognos.",
           "price_source": "Tibber använder din API-token. Entitet läser en Home Assistant-prissensor, till exempel Nord Pool.",
@@ -593,7 +593,7 @@
               "indoor_temp_entity": "Valfritt. Den verkliga rumstemperaturen. Utan den litar optimeringen på sin egen modell, som glider med tiden.",
               "outdoor_temp_entity": "Valfritt. En egen utegivare är mer exakt än prognosen för den aktuella timmen.",
               "space_setpoint_entity": "Valfritt. En number-, helper- eller climate-enhet som är pumpens börvärde för rumsuppvärmning. Används bara för att märka när enheten inte går att läsa. Optimeringen skriver aldrig ett rekommenderat rumsuppvärmningsbörvärde.",
-              "space_setpoint_unit": "Inomhustemperatur är rätt för ett rums- eller termostatbörvärde. Framledningstemperatur är för en styrenhet vars börvärde är en vattentemperatur som den håller framledningen på. Returtemperatur är för en styrenhet som tar börvärdet som mål för returvattnet (antaget för en Luxtronik via dess Smart Home Interface); den skrivs som ett framledningsbörvärde, med det nominella hållvärdet, värmekurvan och grinden på 25 °C flyttade 5 K ned till returnivå. En version från före det här valet läser Returtemperatur som Inomhustemperatur: byt tillbaka till Framledningstemperatur innan du nedgraderar. Att peka ett inomhusmål mot en framledningsenhet skulle kommendera ungefär 21 °C till något som förväntar sig 35–45 °C och undervärma huset kraftigt. Enheten är en deklaration: den här integrationen rekommenderar aldrig ett rumsuppvärmningsbörvärde.",
+              "space_setpoint_unit": "Inomhustemperatur är rätt för ett rums- eller termostatbörvärde. Framledningstemperatur är för en styrenhet vars börvärde är en vattentemperatur som den håller framledningen på. Returtemperatur är för en styrenhet som tar börvärdet som mål för returvattnet (antaget för en Luxtronik via dess Smart Home Interface); den skrivs som ett framledningsbörvärde, med det nominella hållvärdet, värmekurvan och grinden på 25 °C flyttade 5 K ned till returnivå. En version från före det här valet läser Returtemperatur som Inomhustemperatur: byt tillbaka till Framledningstemperatur innan du nedgraderar. Att peka ett inomhusmål mot en framledningsenhet skulle kommendera ungefär 21 °C till något som förväntar sig 35–45 °C och undervärma huset kraftigt. Enheten är en deklaration: optimeraren härleder den aldrig från enheten, och bara förifyllningen från en värmepumpsenhet föreslår en.",
               "flow_min_lift_k": "Med Styrning av pumpens uppgift på Styrning skrivs vattenbörvärdet vid planens lägsta effekt som det uppmätta inkommande vattnet plus detta: värmepumpens retur, bufferttank, golvretur eller ventilens utlopp, och för en entitet med Returtemperatur bara de tre första. 5 K passar en styrenhet som håller sin framledning på börvärdet. En styrenhet som tar börvärdet som mål för returvattnet antas köra kompressorn hårdare ju högre målet ligger över returen och vill troligen ha mindre; 1–2 K är en startpunkt att kontrollera mot kompressorns uppmätta frekvens och effekt, inte ett uppmätt värde.",
               "flow_heat_c": "Vattenbörvärdet som skrivs vid full planerad effekt, och det högsta som skrivs medan planen styr. 55 °C passar ett framledningsmål. För en entitet med Returtemperatur väljs det över den högsta retur du ser vid normal uppvärmning plus höjningen, och inte högre än styrenheten accepterar; för en lågtemperatur-golvvärme kan 35–40 °C vara en startpunkt att kontrollera mot mätningar. Under 30 °C erbjuds inte: grinden som betyder av är 25 °C för ett framledningsmål och 20 °C för ett returmål.",
               "space_setpoint_power_feedback": "På som standard. Verkar bara med Styrning av pumpens uppgift på Styrning, enheten Framlednings- eller Returtemperatur och en effektgivare för värmepumpen; annars ändras ingenting. Efter 5 minuters starthållning sänks vattenbörvärdet medan den uppmätta förbrukningen ligger över planerad nivå, höjs medan den ligger under och hålls inom 10 %, i stället för att följa det stigande inkommande vattnet. Av skriver inkommande vatten plus höjningen. Krav på styrenheten: dess värmehysteres högst höjningen (Luxtronik: 0,5 K), annars startas inte en stoppad kompressor; dess lägsta returmål under returen under eldningssäsongen; dess integration läser den minst var 10:e minut och återställer värmeläget efter en omstart av styrenheten, eftersom ett Luxtronik Smart Home Interface släpper alla satta värden efter 600 s utan åtkomst; och inget annat verktyg skriver samma register (en Luxtronik kastar då skrivningar tyst).",
@@ -1106,7 +1106,7 @@
           "pv_export_price_entity": "Använd denna i stället om din ersättning följer spotpriset.",
           "pv_enabled": "Låter planen köra värmepumpen på ditt eget överskott i stället för att sälja det för mindre än vad köpt el kostar.",
           "pv_peak_kw": "Anläggningens installerade toppeffekt. Används för att skala produktionsprognosen.",
-          "pv_production_entity": "Valfritt. En sensor med faktisk produktion låter prognosen rätta sig efter vad taket verkligen levererar.",
+          "pv_production_entity": "Valfritt. En sensor med faktisk produktion ersätter prognosens aktuella steg med vad taket levererar just nu, högst den installerade effekten; senare steg förblir modellerade.",
           "after_save": "Sparandet slår igenom direkt; detta val avgör vart dialogen går näst."
         }
       },
@@ -1122,7 +1122,7 @@
         },
         "data_description": {
           "away_presence_entity": "En person, enhetsspårare, kalender eller närvarosensor. Plan-sidans brytare vinner tills den slås av. Att en person är 'inte hemma' betyder fortfarande bortavaro när brytaren är av.",
-          "away_dhw_min_temperature": "Legionellacykeln körs fortfarande, och tidsätts så att den hinner bli klar innan du är tillbaka.",
+          "away_dhw_min_temperature": "Legionellacykeln körs fortfarande med sitt vanliga intervall; den tidsätts inte efter din hemkomst.",
           "away_temperature": "Temperaturen som hålls under bortavaron. Låg nog att spara, hög nog att skydda hus och rör.",
           "after_save": "Sparandet slår igenom direkt; detta val avgör vart dialogen går näst.",
           "holiday_calendar_entity": "När den här kalendern är på ersätter lovets komfort och varmvattenfönster vardag/helg för den dagen. Bortasänkning vinner om bortaläget är aktivt."
@@ -1348,7 +1348,7 @@
               "dhw_disinfection_mode": "Observera läser brytaren och skriver aldrig till den. Styra slår på den när en legionellacykel börjar och av den när cykeln är slut, men slår aldrig på den medan pumpens driftläge inte gör varmvatten. Den slår bara av en brytare som den själv slog på: en brytare som redan var på när cykeln började lämnas i fred. En begränsning: om du slår på brytaren för hand medan en cykel som optimeraren startade pågår, slås den av när cykeln är slut, eftersom de två inte går att skilja åt. Styra kräver brytaren ovan.",
               "dhw_disinfection_switch_entity": "En brytare eller hjälpare som startar värmepumpens eget legionellaprogram. I läget observera läses bara dess tillstånd och visas bland varmvattensensorns attribut; i läget styra slår integrationen på den när en desinfektionscykel börjar och av den när cykeln är slut.",
               "dhw_elastic_legionella_enabled": "Låt legionellacykeln köras en dag eller två tidigare när elen är ovanligt billig, i stället för att alltid vänta till sista dagen. Sista dagen hålls alltid.",
-              "dhw_free_disinfection_enabled": "Om en vedpanna, solslinga eller elpatron redan får tanken till legionellatemperatur och håller den där, räkna det som en genomförd cykel i stället för att köra en till.",
+              "dhw_free_disinfection_enabled": "En vedpanna, solslinga eller elpatron som får tanken till legionellatemperatur räknas som en genomförd cykel i båda lägena. Av: direkt; på: först när tanken har hållit den temperaturen i 20 minuter, så en kort topp räknas inte.",
               "dhw_legionella_min_interval_days": "Kör aldrig legionellacykler tätare än så här, även på mycket billiga dagar.",
               "dhw_quantile_targets_enabled": "Lär in hur mycket varmvatten varje tidsfönster faktiskt använder en tung dag, och gör tanken redo för det i stället för för genomsnittsdagen. Kräver tanktemperaturgivare, konfigurerade varmvattenfönster och ett par veckors underlag."
             }
@@ -1364,7 +1364,7 @@
           "after_save": "Efter sparande"
         },
         "data_description": {
-          "vvc_pump_entity": "En brytare som styr VVC-pumpen. Om satt körs pumpen bara under dina varmvattenfönster, plus förvarmningstiden nedan.",
+          "vvc_pump_entity": "En brytare som styr VVC-pumpen. Om satt körs pumpen bara under dina varmvattenfönster, plus förvarmningstiden nedan. Med varmvattnet avslaget eller utan fönster lämnas den på.",
           "vvc_lead_minutes": "Hur långt före ett varmvattenfönster cirkulationspumpen startar, så att slingan redan är varm när fönstret öppnar.",
           "after_save": "Sparandet slår igenom direkt; detta val avgör vart dialogen går näst."
         }
@@ -1383,7 +1383,7 @@
           "after_save": "Efter sparande"
         },
         "data_description": {
-          "main_fuse_amperes": "Husets huvudsäkring i ampere, från ditt nätavtal. 0 lämnar den oinställd, vilket håller säkringsrådgivaren, säkringsvakten och utrymmessensorn vilande — det finns inget säkert standardvärde att gissa, och ett felaktigt skulle strypa ett större hus.",
+          "main_fuse_amperes": "Husets huvudsäkring i ampere, från ditt nätavtal. 0 lämnar den oinställd, vilket håller säkringsrådgivaren och säkringsvakten vilande medan utrymmessensorn bara följer effekttariffens topp, otillgänglig utan effekttariff — det finns inget säkert standardvärde att gissa, och ett felaktigt skulle strypa ett större hus.",
           "main_fuse_phases": "Nästan alla svenska hus har 3 faser.",
           "fuse_guard_enabled": "Begränsar värmepumpens planerade effekt till vad säkringen lämnar efter resten av huset. Om en begränsning skulle göra komfortgolvet onåbart säger planen det på sina sensorer i stället för att tyst bli kall.",
           "peak_guard_enabled": "Bevakar effektmätaren live och håller tillbaka eldrivet varmvatten samt sänker värmekurvan resten av mätfönstret när fönstret beräknas sätta en ny fakturerad topp. Kräver en effektmätare; en kall tank eller ett brutet komfortgolv vinner alltid över vakten.",
@@ -1434,7 +1434,7 @@
               "snow_roof_factor_enabled": "Räkna med mindre sol efter kraftigt snöfall"
             },
             "data_description": {
-              "open_window_relax_enabled": "Fönsterdetektorn pausar alltid inlärningen — den delen är gratis och alltid på. Detta sänker dessutom värmemålet med 1 °C medan ett fönster verkar stå öppet, så att värmepumpen slutar betala för att värma trädgården. Av som standard eftersom det flyttar riktig värme: ett felaktigt flaggat fönster betyder ett något svalare hus.",
+              "open_window_relax_enabled": "Fönsterdetektorn pausar alltid inlärningen — den delen är gratis och alltid på. Detta sänker dessutom den lägsta inomhustemperatur som planen godtar med 1 °C, aldrig under 15 °C, medan ett fönster verkar stå öppet, så att värmepumpen slutar betala för att värma trädgården. Av som standard eftersom det flyttar riktig värme: ett felaktigt flaggat fönster betyder ett något svalare hus.",
               "outage_recovery_enabled": "Efter ett avbrott startar allt samtidigt — kallt hus, kall tank, hela grannskapet — vilket är exakt när en ny månadstopp sätts. Med detta på öppnar ett långt uppehåll i uppdateringarna ett tvåtimmarsfönster där effektavgiften tas på allvar från första kW och varmvattnet köar 45 minuter bakom husvärmen, om inte tanken är riktigt låg.",
               "precip_type_enabled": "Regn blöter ner klimatskalet och ökar värmeförlusten; snö gör det inte. Utan detta behandlas en snöig prognos som regn och planen köper värme för en våt vägg som förblir torr. Kräver Open-Meteo-anslutningen för snödata.",
               "snow_roof_factor_enabled": "I två dygn efter kraftigt snöfall halveras den modellerade solvinsten — snö på takfönster och låga vinterrutor blockerar solen planen räknade med. Medvetet grovt: en faktor och en hålltid, ingen smältmodell."
diff --git a/dev/programme/delivery/3580.md b/dev/programme/delivery/3580.md
new file mode 100644
index 0000000000..afa5d6d8a8
--- /dev/null
+++ b/dev/programme/delivery/3580.md
@@ -0,0 +1 @@
+- [#3580](https://github.com/tvofi/heatpump_optimizer/pull/3580) — **open**, R10-DOCS-STRINGS-RESIDUE (part 2): r10 docs strings residue p2 (R10-DOCS-STRINGS-RESIDUE)
diff --git a/docs/configuration.md b/docs/configuration.md
index d8ded8775a..ec884636ea 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -71,7 +71,7 @@ reported as a connection problem rather than as a bad token.
 
 | Setting | Default | What it means |
 |---|---|---|
-| Name for this integration | Heat Pump Optimizer | Shown in front of every entity this integration creates. |
+| Name for this integration | Heat Pump Optimizer | The title of this entry under Devices & services. Entity names use the fixed device name, Heat Pump Optimizer. |
 | Electricity price source | Tibber | Where hourly electricity prices come from: Tibber (needs the token below) or a price sensor entity you already have. |
 | Tibber API token | — (**required with the Tibber source**) | Reads your hourly electricity prices. Create one at developer.tibber.com. The field still shows when the price source is a price entity — not needed then, so leave it empty. |
 | Price sensor (Nord Pool or similar) | — (**required with the price-entity source**) | A `sensor` publishing the current electricity price, read instead of Tibber. |
@@ -527,7 +527,7 @@ device page and on the card, not here.
 | Away indicator | none | `person`, `device_tracker`, `calendar`, `binary_sensor` | Polarity is handled for you: a person being *not home* still means away when the Plan-page toggle is off. |
 | Holiday-profile calendar | none | a `calendar` | When this calendar is on, holiday comfort and holiday hot-water windows replace the weekday/weekend pair for that day. Away setback still wins if away is active. |
 | Temperature while away | 16.0 °C | 5–21, 0.5 steps | Low enough to save, high enough to protect the house and its plumbing. With the mold guard on, the mold-safe temperature outranks it and can hold the room near the comfort target in a humid house, so away then saves little space-heating energy ([Away and the mold guard](how-it-works.md#away-and-holiday-mode)). |
-| Hot water minimum while away | 20.0 °C | 10–55 | The anti-legionella cycle still runs, timed to finish before you get back. |
+| Hot water minimum while away | 20.0 °C | 10–55 | The anti-legionella cycle still runs on its usual interval; it is not timed to your return. |
 
 ### Quick setup
 
@@ -1060,7 +1060,7 @@ Tank size, daily draw, inlet water and the disinfection extras. The first-menu
 | Cold water inlet sensor | none | a temperature sensor | When set, its live reading replaces the model above. |
 | Greywater heat recovery effectiveness | 0.0 | 0–0.9, 0.05 steps | The fraction of drain heat a drain-water recovery unit returns. 0 means none installed. |
 | Learn heavy-day hot water targets | off | on/off | Makes the tank ready for a heavy day rather than an average one. Needs a tank sensor, configured time frames, and a couple of weeks of evidence. |
-| Credit disinfection from any heat source | off | on/off | If a wood boiler, solar coil or immersion heater already got the tank hot enough and held it there, count that as a completed cycle. |
+| Credit disinfection from any heat source | off | on/off | A wood boiler, solar coil or immersion heater that gets the tank to the anti-legionella temperature counts as a completed cycle either way. Off, it counts the moment the tank is within 1 °C of that temperature; on, only after the tank has spent 20 minutes within 0.5 °C of it, so a short peak credits nothing. |
 | Let the anti-legionella cycle pick a cheap day | off | on/off | Allows the cycle to run a day or two early when electricity is unusually cheap. The deadline is still always honoured. |
 | Earliest anti-legionella re-run | 5 days | 1–14 | A floor on how close together cycles may run, however cheap the day. |
 | Pump's disinfection switch | none | `switch` / `input_boolean` | A switch or helper that starts the heat pump's own anti-legionella program. Its state is read on every update and published on the hot water sensor's attributes as `dhw_disinfection_switch`; the attribute is absent while no switch is set. |
@@ -1074,7 +1074,7 @@ The DHW loop pump. The heating-circuit circulation pump lives on
 
 | Setting | Default | Range | What it means |
 |---|---|---|---|
-| Hot water circulation pump switch | none | `switch` / `input_boolean` | When set, the circulation loop pump runs only during your hot water time frames plus the lead time below. |
+| Hot water circulation pump switch | none | `switch` / `input_boolean` | When set, the circulation loop pump runs only during your hot water time frames plus the lead time below. With hot water off or no time frames, it is left on. |
 | Start circulation before a time frame | 20 min | 0–120, 5 steps | So the loop is already hot when the time frame opens. |
 
 ### Solar panels
@@ -1090,7 +1090,7 @@ what consuming actually costs you.
 | Overall system efficiency | 0.80 | 0.3–1.0, 0.01 steps | Everything between sunlight and the meter: inverter losses, panel temperature, dirt, orientation. |
 | Export compensation per kWh | 0.0 | 0–10, 0.01 steps | What you are paid for an exported kWh. While you have surplus, that is what an extra kWh of heating really costs. |
 | Export compensation entity | none | a sensor | Use this instead if your compensation follows the spot price. |
-| Solar production sensor | none | a `power` sensor | Lets the forecast correct itself against what the roof actually delivers. |
+| Solar production sensor | none | a `power` sensor | Replaces the forecast's current step with what the roof delivers now, capped at the installed capacity; later steps stay modelled. |
 
 ### Self-learning and diagnostics
 
@@ -1113,7 +1113,7 @@ opt-in learners are on **Advanced learning features**.
 | Setting | Default | Range | What it means |
 |---|---|---|---|
 | Staggered recovery after a power cut | off | on/off | After an outage everything restarts at once, which is exactly when a new monthly peak gets set. This opens a two-hour recovery window where hot water queues 45 minutes behind space heating unless the tank is genuinely low. A restart that finds the last saved heartbeat ahead of the clock (the clock was set back, so the gap cannot be known) counts as an outage too. |
-| Ease heating while a window is open | off | on/off | The detector always pauses learning; this additionally lowers the target by 1 °C while a window appears open. Off by default because it moves real heat. |
+| Ease heating while a window is open | off | on/off | The detector always pauses learning; this additionally lowers the coldest temperature the plan accepts by 1 °C, never below 15 °C, while a window appears open. Off by default because it moves real heat. |
 | Plan around immersion heater use | off | on/off | Repeated immersion use raises the hot-water planning margin so the heat pump gets there first. It also declares the immersion element: when the power meter reads more than the compressor's nameplate can draw, the excess books as its own ledger line. With this off and neither pump heater flag on, nothing books as resistive heat, because the meter alone cannot tell an element from a compressor over its configured nameplate. |
 | Tell snow from rain in the forecast | off | on/off | Rain soaks the envelope and raises heat loss; snow does not. Needs the Open-Meteo connection. |
 | Assume less sun after heavy snowfall | off | on/off | Halves modelled solar gain for two days after heavy snowfall. Deliberately crude. |
@@ -1126,7 +1126,7 @@ opt-in learners are on **Advanced learning features**.
 
 | Setting | Default | Range | What it means |
 |---|---|---|---|
-| Main fuse size | 0 A | 0–125 | From your grid contract. **0 means unconfigured**, which keeps the fuse advisor, the fuse guard and the headroom sensor dormant — there is no safe default to guess. |
+| Main fuse size | 0 A | 0–125 | From your grid contract. **0 means unconfigured**, which keeps the fuse advisor and the fuse guard dormant; the headroom sensor then follows the capacity-tariff peak alone and is unavailable without a capacity tariff — there is no safe default to guess. |
 | Phases | 3 | 1–3 | Nearly every Swedish house is 3-phase. |
 | Keep the plan under the main fuse | off | on/off | Caps planned power at what the fuse leaves after the rest of the house. If a cap would make the comfort floor unreachable, the plan says so instead of silently going cold. |
 | Live peak guard | off | on/off | Watches the power meter and, when the current metering window is projected to set a new billed peak, holds back electric hot water and nudges the heat curve down for the rest of that window. Needs a power meter. |
diff --git a/docs/dashboard-card.md b/docs/dashboard-card.md
index 4e1bb4d63c..43544808cb 100644
--- a/docs/dashboard-card.md
+++ b/docs/dashboard-card.md
@@ -575,8 +575,9 @@ capacity charge at the month's billed peak, the kWh a resistive heater drew
 beyond what the compressor can (the pump's own tank booster or backup heater
 while its flag is on, or an immersion heater you have declared), and
 compressor wear in starts. The total adds those lines and nothing else; a
-note under it says which lines it covers and that the savings figure
-compares spot cost only. Wear reads "not priced" until you set a
+note under it says which lines it covers and what the savings figure
+compares: the plan and the thermostat baseline are both priced at spot
+plus the per-kWh grid fee. Wear reads "not priced" until you set a
 compressor replacement cost. Beside it, **Where the money went** splits the
 spot line by the plan's reason for each kWh, largest first; the bars add up
 to the spot line. Every receipt the integration keeps (24 months) is on the
@@ -697,8 +698,8 @@ configured, the way it did before:
 - **Each ranked row carries its spread and an *estimated* badge.** The spread
   is in degrees the model's predictions can move — one unit, comparable
   between sensors. The line under the heading names what drove the replay:
-  your install's measured delivery where there is history, configured
-  defaults otherwise.
+  the mean electrical power your heat pump has measured where there is
+  history, half its configured maximum otherwise.
 - **A sensor the estimate cannot price is listed below the ranked rows, with
   its reason** — the outdoor probe whose job the weather entity already does,
   the floor-return probe that feeds a state estimate rather than a learned
@@ -724,7 +725,7 @@ on the Health page names which. The pill appears once that sensor has a state.
 
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="img/card/health-dark.png">
-  <img alt="The Health tab: a Plan column solved 12 minutes ago with the next solve, its 96 steps and the solve time, and a Still learning column with savings waiting for the first settled month; an Inputs row with a stale outdoor temperature sensor (its age and its limit) and fresh indoor and hot-water sensors; a What the model has learned block whose rows each carry a value, their evidence in words and a bar: house heat loss 142 W/K, not observable without a power meter, solar gain at a window scale of 1.15 and still learning, hot-water tank cooling at 0.9 °C per hour, heat pump efficiency normal at a COP scale of 0.97, and a 24-bar internal-gains strip peaking around 18:00; a Something looks wrong? row with a Download diagnostics button, a Debug collection row with a Start button, and the six-item first-plan checklist, three ticked, with Assign on the power meter and Show on the insight sensors" src="img/card/health-light.png">
+  <img alt="The Health tab: a Plan column solved 12 minutes ago with the next solve, its 96 steps and the solve time, and a Still learning column with savings waiting for the first month with a booked saving; an Inputs row with a stale outdoor temperature sensor (its age and its limit) and fresh indoor and hot-water sensors; a What the model has learned block whose rows each carry a value, their evidence in words and a bar: house heat loss 142 W/K, not observable without a power meter, solar gain at a window scale of 1.15 and still learning, hot-water tank cooling at 0.9 °C per hour, heat pump efficiency normal at a COP scale of 0.97, and a 24-bar internal-gains strip peaking around 18:00; a Something looks wrong? row with a Download diagnostics button, a Debug collection row with a Start button, and the six-item first-plan checklist, three ticked, with Assign on the power meter and Show on the insight sensors" src="img/card/health-light.png">
 </picture>
 
 *Everything here is read from the integration's sensors; the card computes no
@@ -735,8 +736,8 @@ figure of its own.* The page shows, top to bottom:
   solve took (the Optimization Status sensor's `solve_time_ms`). Its pill reads
   **Stale** once the plan is past the limit the header's own status pill uses.
   **Still learning** lists the sensors that are enabled by default and wait
-  for evidence, each with its reason in words: savings (the first settled
-  month), heat pump COP (a power meter, then some running time), prediction
+  for evidence, each with its reason in words: savings (the first month with a
+  booked saving), heat pump COP (a power meter, then some running time), prediction
   accuracy (the first scored interval) and the optimization score (the first
   scored day). Home Assistant hides an unavailable entity's attributes, so the
   card cannot read the sensor's own `waiting_for` code and the reason is keyed
diff --git a/docs/how-it-works.md b/docs/how-it-works.md
index ccbb2bb9c7..b838ba71af 100644
--- a/docs/how-it-works.md
+++ b/docs/how-it-works.md
@@ -617,9 +617,10 @@ redundant cycle.
 
 Two opt-in refinements:
 
-- **Free disinfection**: if another heat source holds the tank at the
-  disinfection temperature *long enough*, that counts as a completed cycle. It
-  is hold-verified, so a momentary blip at 60 °C credits nothing.
+- **Hold-verified disinfection**: any heat source already resets the timer;
+  with *Credit disinfection from any heat source* on, it does so only once the
+  tank has held the disinfection temperature for 20 minutes, so a momentary
+  blip at 60 °C credits nothing.
 - **A price-aware cycle**: inside its interval the cycle may run a day or two
   early (no sooner than a configurable minimum, default 5 days) when a known
   price beats what a typical remaining day is expected to bottom out at. The
@@ -646,7 +647,8 @@ Everything here is inert until configured or until evidence exists:
   Advisor** reports the cheapest setpoint that still covers your learned heavy
   days — read-only, the decision stays yours.
 - **Circulation pumps** (opt-in): a VVC loop pump runs only around your demand
-  frames, with a lead (default 20 minutes) so the loop is hot when they open.
+  frames, with a lead (default 20 minutes) so the loop is hot when they open;
+  with hot water off or no frames it is left on.
   The space circulation pump pauses only in provably idle, warm slots, and is
   forced on whenever heat is planned, the heat curve is being driven, any room
   is near its comfort floor, or it is freezing outside.
@@ -921,7 +923,7 @@ that cannot save them anything should not be able to cost them anything.
 
 A week away is the largest single saving a heating system can offer: a deep
 setback plus hot water held only at its away minimum (20 °C unless you change
-it), except for a legionella cycle timed to complete before you return.
+it), while the legionella cycle keeps its usual interval.
 
 What makes this more than a manual setpoint is the **return time**. Knowing when
 the house must be comfortable again lets the recovery heat be bought in the
diff --git a/docs/setup.md b/docs/setup.md
index ebd69f7217..03cd658ae1 100644
--- a/docs/setup.md
+++ b/docs/setup.md
@@ -88,7 +88,7 @@ answers of the whole flow.*
 
 | Setting | What it asks |
 |---|---|
-| Name for this integration | Shown in front of every entity the integration creates. |
+| Name for this integration | The title of this entry under Devices & services. Entity names use the fixed device name, Heat Pump Optimizer. |
 | Electricity price source | `Tibber` uses your API token; `Price entity (Nord Pool or similar)` reads a Home Assistant price sensor. |
 | Tibber API token | Required only when the source is Tibber. Checked against Tibber before the flow continues — a network failure is reported as a connection problem, not as a bad token. |
 | Price sensor (Nord Pool or similar) | Required only when the source is an entity. |
diff --git a/tests/doc_claims.py b/tests/doc_claims.py
index 8641c21162..6a677b7f93 100644
--- a/tests/doc_claims.py
+++ b/tests/doc_claims.py
@@ -4664,6 +4664,164 @@ def check_power_feedback_claims() -> None:
             all(fact in (pa._clamp_cut.__doc__ or "") for fact in (comment_id, "10104", "10103")))
 
 
+# ---------------------------------------------------------------------------
+# R10-DOCS-STRINGS-RESIDUE carries 5 to 13: reader sentences and option texts
+# that described behaviour the code does not have. Each arm takes its fact
+# from the producing code, refuses the old wording in the reader corpus and in
+# all four string files, and requires the corrected sentence to state the fact.
+# ---------------------------------------------------------------------------
+_STRING_FILES = {
+    name: json.loads((PKG / rel).read_text())
+    for name, rel in (("strings.json", "strings.json"), ("en.json", "translations/en.json"),
+                      ("de.json", "translations/de.json"), ("sv.json", "translations/sv.json"))
+}
+
+#: (carry, the old wording in any language) -- the sentences these carries corrected.
+_RESIDUE_REFUSED = (
+    ("Carry 5", r"lowers the (?:heating )?target by|Heizziel um|värmemålet med"),
+    ("Carry 6", r"headroom sensor dormant|Reserve inaktiv|utrymmessensorn vilande"),
+    ("Carry 7", r"correct itself against|Prognose sich anhand|rätta sig efter"),
+    ("Carry 8", r"in front of every (?:entity|sensor)|vorangestellt|Visas framför"),
+    ("Carry 9", r"compares spot cost only"),
+    ("Carry 10", r"measured delivery"),
+    ("Carry 11", r"first settled month"),
+)
+
+
+def _string_leaves(tree: object):
+    if isinstance(tree, dict):
+        for value in tree.values():
+            yield from _string_leaves(value)
+    elif isinstance(tree, str):
+        yield tree
+
+
+def residue_hits(corpus: dict[str, str], string_files: dict[str, dict]) -> dict[str, list[str]]:
+    """Every refused wording still present, by carry: the document or string file it is in."""
+    texts = {**{k: " ".join(v.split()) for k, v in corpus.items()},
+             **{k: "\n".join(_string_leaves(v)) for k, v in string_files.items()}}
+    return {carry: hits for carry, pattern in _RESIDUE_REFUSED
+            if (hits := [name for name, text in texts.items() if re.search(pattern, text)])}
+
+
+def menu_title_mismatches(strings: dict) -> tuple[int, list[str]]:
+    """Every options-menu entry whose target step has a title: (pairs compared, the pairs whose names differ).
+
+    Design choice: the options flow only. Its menu entries name the page they open; the config flow's are
+    actions ("Continue setup", "Describe my building (recommended)") and legitimately differ from the title."""
+    pairs, bad = 0, []
+    for flow in ("options",):
+        steps = strings.get(flow, {}).get("step", {})
+        for body in steps.values():
+            for key, label in (body.get("menu_options") or {}).items():
+                title = steps.get(key, {}).get("title")
+                if title is None:
+                    continue
+                pairs += 1
+                if title != label:
+                    bad.append(f"{flow}.step.{key}: menu {label!r}, title {title!r}")
+    return pairs, bad
+
+
+def check_docs_strings_residue() -> None:
+    R.section("reader text against the code that produces it (R10-DOCS-STRINGS-RESIDUE carries 5 to 13)")
+    import inspect
+    import types
+    from heatpump_optimizer import away, const, coordinator, entry_config, ledger, topology
+
+    flat = {k: " ".join(v.split()) for k, v in DOCS.items()}
+    cfg, en = flat.get("configuration.md", ""), _STRING_FILES["en.json"]
+    opts = en["options"]["step"]
+    hits = residue_hits(CORPUS, _STRING_FILES)
+    R.check("no reader doc or string file keeps a corrected sentence's old wording", not hits, repr(hits))
+
+    # Carry 5: the open-window relax widens the floor and leaves the target.
+    relax, floor = const.OPEN_WINDOW_RELAX_C, const.ECONOMY_ABSOLUTE_FLOOR
+    fields = dict.fromkeys(away._OPT_FIELDS, None) | {"target_temp": 21.0, "min_temp": 20.0}
+    thermal = types.SimpleNamespace(**dict.fromkeys(away._DHW_FIELDS, 45.0))
+    banded, _ = away.solve_bands(types.SimpleNamespace(**fields), thermal, None, (relax,))
+    R.check("solve_bands lowers min_temp by OPEN_WINDOW_RELAX_C and leaves target_temp",
+            banded["min_temp"] == 20.0 - relax and banded["target_temp"] == 21.0, repr(banded))
+    low, _ = away.solve_bands(types.SimpleNamespace(**(fields | {"min_temp": floor})), thermal, None, (relax,))
+    R.check("solve_bands never takes min_temp below ECONOMY_ABSOLUTE_FLOOR", low["min_temp"] == floor, repr(low))
+    phrase = f"by {relax:g} °C, never below {floor:g} °C"
+    R.check(f"configuration.md's open-window row says the coldest accepted temperature drops {phrase}",
+            f"lowers the coldest temperature the plan accepts {phrase}" in cfg)
+    R.check(f"the open-window option text says {phrase}",
+            phrase in opts["learning_features"]["sections"]["weather"]["data_description"]["open_window_relax_enabled"])
+
+    # Carry 6: fuse 0 is no fuse, so the headroom follows the capacity-tariff peak alone.
+    def fuse(amps: int) -> float | None:
+        cfg_ = types.SimpleNamespace(main_fuse_amperes=amps, main_fuse_phases=3)
+        cfg_.fuse_kw_at = lambda a: entry_config.EntryConfig.fuse_kw_at(cfg_, a)
+        return entry_config.EntryConfig.fuse_kw(cfg_)
+
+    R.check("EntryConfig.fuse_kw answers None at main fuse 0, and a capacity at 16 A (control)",
+            fuse(0) is None and fuse(16) is not None, repr((fuse(0), fuse(16))))
+    R.check("configuration.md's main-fuse row says the headroom sensor follows the capacity-tariff peak",
+            "the headroom sensor then follows the capacity-tariff peak alone" in cfg)
+    R.check("the main-fuse option text says the headroom sensor follows the capacity-tariff peak",
+            "headroom sensor following the capacity-tariff peak alone"
+            in opts["grid_connection"]["data_description"]["main_fuse_amperes"])
+
+    # Carry 7: the measured production replaces step 0 only.
+    pv = re.search(r"production\[0\] = min\(self\._pv_production, config\.peak_kw\)",
+                   inspect.getsource(coordinator))
+    R.check("the coordinator replaces production[0] alone, capped at peak_kw (anchor)", pv is not None)
+    for where, text in (("configuration.md", cfg),
+                        ("the PV sensor option text", opts["solar_pv"]["data_description"]["pv_production_entity"])):
+        R.check(f"{where} says only the current step is replaced, capped at the installed capacity",
+                "current step" in text and "capped at the installed capacity" in text)
+
+    # Carry 8: every entity is named from the device, whose name is a literal.
+    device = re.search(r'DeviceInfo\(\s*identifiers=.*?name="([^"]+)"', inspect.getsource(coordinator), re.S)
+    R.check("the coordinator's DeviceInfo names the device by a literal (anchor)", device is not None)
+    name = device.group(1) if device else "<none>"
+    for where, text in (("setup.md", flat.get("setup.md", "")), ("configuration.md", cfg),
+                        ("the name option text", en["config"]["step"]["user"]["data_description"]["name"])):
+        R.check(f"{where} says entities use the fixed device name {name!r}",
+                f"fixed device name, {name}" in text)
+
+    # Carry 9: both sides of the saving are priced at spot plus the per-kWh fee.
+    R.check("observe_spot_and_settle_savings prices the settlement at spot + fee_per_kwh (anchor)",
+            "spot=spot + fee_per_kwh" in inspect.getsource(ledger.MonthlyLedger.observe_spot_and_settle_savings))
+    card = flat.get("dashboard-card.md", "")
+    R.check("dashboard-card.md says both sides are priced at spot plus the per-kWh grid fee",
+            "both priced at spot plus the per-kWh grid fee" in card)
+
+    # Carry 10: the replay's power is the measured mean, else a fraction of the maximum.
+    half = {0.5: "half"}.get(topology._ADVISOR_DUTY_FRACTION)
+    R.check("_ADVISOR_DUTY_FRACTION is a fraction the page can name", half is not None,
+            repr(topology._ADVISOR_DUTY_FRACTION))
+    R.check("dashboard-card.md names the measured mean power, else the configured maximum's fraction",
+            f"mean electrical power your heat pump has measured where there is history, {half} its configured maximum"
+            in card)
+
+    # Carry 11: the Health picture's alt text names the booked-saving wait.
+    R.check("dashboard-card.md's Health picture waits for the first month with a booked saving",
+            "savings waiting for the first month with a booked saving" in card)
+
+    # Carry 13: one options page, one name per language.
+    for fname, strings in _STRING_FILES.items():
+        pairs, bad = menu_title_mismatches(strings)
+        R.check(f"{fname}: every options-menu entry names its page by the page's title ({pairs} pairs)",
+                pairs > 0 and not bad, "; ".join(bad))
+
+    # Null controls: each old wording, put back, fires; a renamed page title fires.
+    for carry, old in (
+        ("Carry 5", "this additionally lowers the target by 1 °C"), ("Carry 6", "the headroom sensor dormant"),
+        ("Carry 7", "Lets the forecast correct itself against what the roof"),
+        ("Carry 8", "Shown in front of every entity"), ("Carry 9", "the savings figure compares spot cost only"),
+        ("Carry 10", "your install's measured delivery"), ("Carry 11", "waiting for the first settled month"),
+    ):
+        R.check(f"{carry}: the old wording, put back, is refused (null control)",
+                carry in residue_hits({"setup.md": old}, {}))
+    renamed = json.loads(json.dumps(_STRING_FILES["de.json"]))
+    renamed["options"]["step"]["grid"]["title"] = "Netz-Spitzentarif"
+    R.check("a de grid page titled apart from its menu entry is refused (null control)",
+            bool(menu_title_mismatches(renamed)[1]))
+
+
 def check_stateless() -> None:
     R.section("the user pages describe the integration as it is, with no change history (R10-USER-DOCS-FINAL)")
     pages = _user_pages()
@@ -4756,6 +4914,7 @@ def main() -> int:
     check_readme_marketplace()
     check_surface_coverage()
     check_power_feedback_claims()
+    check_docs_strings_residue()
     check_stateless()
     return R.close("checks")
 

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
