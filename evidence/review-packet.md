# Review packet #3378
head: 07ad9ae34ab5903bb2c103a2828fc71910b30a7e
base: 2f6d699e504d6dc0bb6040d99c21c5b015a290e4

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=129348536948 neutral
arch-score / arch-score id=129357778098 success
budget-raise-gate / budget-raise-gate id=129357781465 success
cancel-superseded id=129357777017 success
codeql id=129357779757 skipped
codeql / Analyze (actions) id=129357853250 success
codeql / Analyze (javascript-typescript) id=129357771838 success
codeql / Analyze (python) id=129357768868 in_progress
gate id=129358448270 failure
governance id=129357780383 skipped
governance / delivery-status id=129357768694 success
governance / delivery-status-publish id=129357771210 skipped
governance / env-matrix id=129357768847 success
governance / instrument-self-tests id=129357768713 success
governance / policy-docs id=129357772526 success
governance / record id=129357770777 skipped
governance / wave-script id=129357768707 success
hassfest id=129357780196 skipped
hassfest / hassfest id=129357826164 success
kernel-points id=129357779953 skipped
pr-contract id=129358450920 skipped
pr-contract / pr-contract id=129352210364 failure
prelude id=129357780506 success
refresh id=129357776669 success
tests id=129357779824 skipped
tests / arch-instrument id=129357769525 success
tests / briefs id=129357768594 success
tests / browser id=129357769413 success
tests / ci-ratchet id=129372189635 skipped
tests / claims-autofix id=129371715010 skipped
tests / closure-scope id=129357834065 success
tests / closures id=129357769567 success
tests / closures-autofix id=129368780124 skipped
tests / coverage id=129357769740 success
tests / coverage-ratchet id=129372185978 success
tests / fast (3.14) id=129357769982 success
tests / graders-head-copy id=129372185999 success
tests / lane-proofs id=129372185965 success
tests / mutation id=129357816891 success
tests / mutation-autofix id=129357772256 skipped
tests / mutation-pins id=129357771601 skipped
tests / nightly-ha id=129357772524 skipped
tests / nightly-status id=129357850804 success
tests / replay id=129357773056 skipped
tests / typing id=129357769557 success
validate id=129357779585 skipped
validate / validate-hacs id=129357854953 success

## Refusals
red-unanswered: concluded red check `pr-contract / pr-contract` is not named in ## Red checks
required-red: required context `gate` concluded failure at 07ad9ae34ab5903bb2c103a2828fc71910b30a7e

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py
             `dev/audit/rounds/round4/D6/claims.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub node tests/card.mjs
             `tests/card.mjs` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         tests/golden.py
             `tests/golden.py` is in the tree at this head
  ok         tests/env_drift.py --all
             `tests/env_drift.py` is in the tree at this head
  ok         tests/card.mjs
             `tests/card.mjs` is in the tree at this head
  ok         tests/card_drift.mjs
             `tests/card_drift.mjs` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 8 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/translations/de.json b/custom_components/heatpump_optimizer/translations/de.json
index 8a6871b79..a2bc7dfb2 100644
--- a/custom_components/heatpump_optimizer/translations/de.json
+++ b/custom_components/heatpump_optimizer/translations/de.json
@@ -581,13 +581,17 @@
               "indoor_temp_entity": "Innentemperatursensor",
               "outdoor_temp_entity": "Außentemperatursensor",
               "space_setpoint_entity": "Sollwert-Entität der Raumheizung (optional)",
-              "space_setpoint_unit": "Was diese Sollwert-Entität erwartet"
+              "space_setpoint_unit": "Was diese Sollwert-Entität erwartet",
+              "flow_min_lift_k": "Mindesthub über dem Eingangswasser (K)",
+              "flow_heat_c": "Obergrenze der Heizungsvorlauftemperatur (°C)"
             },
             "data_description": {
               "indoor_temp_entity": "Optional. Die tatsächliche Raumtemperatur. Ohne sie vertraut der Optimierer seinem eigenen Modell, das mit der Zeit abdriftet.",
               "outdoor_temp_entity": "Optional. Ein lokales Außenthermometer ist für die aktuelle Stunde genauer als die Vorhersage.",
               "space_setpoint_entity": "Optional. Eine Zahl, ein Helfer oder eine Climate-Entität, die der Sollwert der Raumheizung der Pumpe ist. Dient nur dazu zu bemerken, wenn die Entität nicht gelesen werden kann. Der Optimierer schreibt nie einen empfohlenen Raumheizungs-Sollwert.",
-              "space_setpoint_unit": "Innentemperatur ist richtig für einen Raum- oder Thermostat-Sollwert. Vorlauftemperatur gilt für einen Regler, dessen Sollwert eine Wassertemperatur ist. Würde ein Innentemperaturziel auf eine Vorlauf-Entität zeigen, würden etwa 21 °C an ein Gerät gesendet, das 35–45 °C erwartet, und das Haus würde stark unterheizt. Die Einheit ist eine Angabe: Diese Integration empfiehlt nie einen Raumheizungs-Sollwert."
+              "space_setpoint_unit": "Innentemperatur ist richtig für einen Raum- oder Thermostat-Sollwert. Vorlauftemperatur gilt für einen Regler, dessen Sollwert eine Wassertemperatur ist, auf der er seinen Vorlauf hält. Rücklauftemperatur gilt für einen Regler, der den Sollwert als Ziel für das Rücklaufwasser nimmt (angenommen für eine Luxtronik über ihre Smart-Home-Schnittstelle); er wird wie ein Vorlauf-Sollwert geschrieben, wobei der Nennhaltewert, die Wetterkurve und die 25-°C-Schwelle um 5 K nach unten in Rücklaufwerte verschoben werden. Eine Version vor dieser Option liest Rücklauftemperatur als Innentemperatur: Stelle vor einem Downgrade wieder auf Vorlauftemperatur um. Würde ein Innentemperaturziel auf eine Vorlauf-Entität zeigen, würden etwa 21 °C an ein Gerät gesendet, das 35–45 °C erwartet, und das Haus würde stark unterheizt. Die Einheit ist eine Angabe: Diese Integration empfiehlt nie einen Raumheizungs-Sollwert.",
+              "flow_min_lift_k": "Mit Steuerung der Pumpenfunktion auf Steuern ist der bei der niedrigsten Planleistung geschriebene Wasser-Sollwert das gemessene Eingangswasser plus dieser Wert: Wärmepumpen-Rücklauf, Pufferspeicher, Fußbodenrücklauf oder Ventilauslass, und bei einer Entität mit Rücklauftemperatur nur die ersten drei. 5 K passt zu einem Regler, der seinen Vorlauf auf dem Sollwert hält. Von einem Regler, der die Zahl als Ziel für das Rücklaufwasser nimmt, wird angenommen, dass er seinen Verdichter umso stärker laufen lässt, je weiter das Ziel über dem Rücklauf liegt, er will also wahrscheinlich weniger; 1–2 K ist ein Ausgangspunkt, der an der gemessenen Frequenz und Leistung des Verdichters zu prüfen ist, kein gemessener Wert.",
+              "flow_heat_c": "Der bei voller Planleistung geschriebene Wasser-Sollwert und der höchste, der geschrieben wird, solange der Plan die Führung hat. 55 °C passt zu einem Vorlaufziel. Wähle ihn bei einer Entität mit Rücklauftemperatur über dem höchsten Rücklauf, den du im normalen Heizbetrieb siehst, plus dem Hub, und nicht höher, als der Regler annimmt; bei einer Niedertemperatur-Fußbodenheizung können 35–40 °C ein Ausgangspunkt sein, der an Messungen zu prüfen ist. Unter 30 °C wird nicht angeboten: Die Schwelle, die aus bedeutet, liegt bei 25 °C für ein Vorlaufziel und bei 20 °C für ein Rücklaufziel."
             }
           },
           "plant": {
@@ -1225,7 +1229,7 @@
         },
         "data_description": {
           "heat_pump_mode_entity": "Optional. Die eigene Modusauswahl der Wärmepumpe – Kühlen, Heizen, Warmwasser oder eine Kombination aus zwei. Nur lesend, außer die Steuerung der Pumpenfunktion steht auf Steuern. Eine Wärmepumpe im Kühl- oder reinen Warmwassermodus kann das Haus nicht heizen, und eine im reinen Heizmodus kann kein Warmwasser bereiten; ohne diese Angabe kann der Plan Wärme versprechen, die die Wärmepumpe gerade nicht liefern kann. Bleibt sie leer, geht der Optimierer davon aus, dass die Wärmepumpe alles kann.",
-          "pump_duty_mode": "Aus (Standard) schreibt nie auf die Wärmepumpe. Beobachten schreibt nichts und führt in den Diagnosedaten ein 24-Stunden-Protokoll darüber, welche Funktion jeder Planschritt angefordert hat und was die Wärmepumpe getan hat (aus der Leistungsentität, dem Modus und der Speichertemperatur). Steuern schreibt den oben gewählten Betriebsmodus (nur Warmwasser bei reinen Warmwasserschritten, nur Heizen bei reinen Raumheizungsschritten, Heizen + Warmwasser, wenn beides geplant ist oder ein Desinfektionszyklus läuft, unverändert bei Leerlaufschritten), die Entität für den Warmwasser-Sollwert (der auf der Warmwasserseite konfigurierte Warmwasser-Sollwert) und die Entität für den Raumheizungs-Sollwert (bei einem Vorlauf-Sollwert ein Ziel, das der geplanten Leistung folgt – die Heizungsvorlauftemperatur (55 °C, oder flow_heat_c) bei voller Leistung, in Richtung 5 °C über dem ersten aktuellen Wert von Wärmepumpen-Rücklauf, Pufferspeicher, Fußbodenrücklauf oder Ventilauslass (35 °C, wenn keiner konfiguriert ist) an der Modulationsuntergrenze – oder das Maximum der Entität bei Schritten, die das Haus heizen, ihr Minimum bei Schritten, die es nicht tun, und 35 °C oder die Wetterkurve, wenn der Plan nicht die Führung hat; bei einem Raum-Sollwert die geplante Raumtemperatur). Wo der Modus keine Einzelfunktion anbietet, etwa beim GCHV-Modbus-Paket, wird stattdessen der Sollwert der anderen Funktion auf sein Minimum gesenkt. Ein reiner Warmwasserabschnitt ist auf 90 Minuten begrenzt (30 unter -10 °C Außentemperatur), außer der Raum hat bereits seine geplante Temperatur. Solange Optimierer aktiv eingeschaltet ist, wird jede Änderung an diesen Entitäten, die der Optimierer nicht vorgenommen hat, sofort zurückgeschrieben; schalte Optimierer aktiv aus, um die Wärmepumpe von Hand zu ändern. Ein Wert, den die Wärmepumpe nicht übernimmt, löst eine Warnung aus und wird alle 5 Minuten erneut gesendet.",
+          "pump_duty_mode": "Aus (Standard) schreibt nie auf die Wärmepumpe. Beobachten schreibt nichts und führt in den Diagnosedaten ein 24-Stunden-Protokoll darüber, welche Funktion jeder Planschritt angefordert hat und was die Wärmepumpe getan hat (aus der Leistungsentität, dem Modus und der Speichertemperatur). Steuern schreibt den oben gewählten Betriebsmodus (nur Warmwasser bei reinen Warmwasserschritten, nur Heizen bei reinen Raumheizungsschritten, Heizen + Warmwasser, wenn beides geplant ist oder ein Desinfektionszyklus läuft, unverändert bei Leerlaufschritten), die Entität für den Warmwasser-Sollwert (der auf der Warmwasserseite konfigurierte Warmwasser-Sollwert) und die Entität für den Raumheizungs-Sollwert (bei einem Vorlauf-Sollwert ein Ziel, das der geplanten Leistung folgt – die Heizungsvorlauftemperatur (55 °C, oder flow_heat_c) bei voller Leistung, in Richtung 5 °C (oder flow_min_lift_k) über dem ersten aktuellen Wert von Wärmepumpen-Rücklauf, Pufferspeicher, Fußbodenrücklauf oder Ventilauslass (35 °C, wenn keiner konfiguriert ist) an der Modulationsuntergrenze – oder das Maximum der Entität bei Schritten, die das Haus heizen, ihr Minimum bei Schritten, die es nicht tun, und 35 °C oder die Wetterkurve, wenn der Plan nicht die Führung hat; bei einem Raum-Sollwert die geplante Raumtemperatur). Wo der Modus keine Einzelfunktion anbietet, etwa beim GCHV-Modbus-Paket, wird stattdessen der Sollwert der anderen Funktion auf sein Minimum gesenkt. Ein reiner Warmwasserabschnitt ist auf 90 Minuten begrenzt (30 unter -10 °C Außentemperatur), außer der Raum hat bereits seine geplante Temperatur. Solange Optimierer aktiv eingeschaltet ist, wird jede Änderung an diesen Entitäten, die der Optimierer nicht vorgenommen hat, sofort zurückgeschrieben; schalte Optimierer aktiv aus, um die Wärmepumpe von Hand zu ändern. Ein Wert, den die Wärmepumpe nicht übernimmt, löst eine Warnung aus und wird alle 5 Minuten erneut gesendet.",
           "heat_pump_defrost_entity": "Optional. Ein, solange die Wärmepumpe den Kreislauf umkehrt, um Frost vom Außenwärmetauscher zu schmelzen. Der während einer Abtauung bezogene Strom geht in den Wärmetauscher statt ins Haus. Beachte, dass viele Wärmepumpen nur alle paar Minuten abgefragt werden, kurze Abtauvorgänge also komplett übersehen werden: Dies ist eine Stichprobe der Abtauaktivität, keine Stoppuhr.",
           "heat_pump_online_entity": "Optional und bei einer cloudverbundenen Wärmepumpe dringend empfohlen. Ein, solange die Wärmepumpe tatsächlich erreichbar ist. Eine Cloud-Integration kann ihre letzten bekannten Werte weiter veröffentlichen, obwohl die Wärmepumpe selbst vom Netzwerk getrennt ist, sodass alle anderen Sensoren völlig aktuell aussehen; dies ist das einzige Signal, das etwas anderes sagt. Bei einer lokalen Verbindung (LAN) werden die Sensoren von selbst nicht verfügbar, und dies bringt wenig.",
           "heat_pump_fault_entity": "Optional. Ein, solange die Wärmepumpe eine Störung meldet. Verwendet wird nur, ob eine Störung vorliegt, nie der Code selbst.",
@@ -1686,7 +1690,8 @@
     "space_setpoint_unit": {
       "options": {
         "indoor": "Innentemperatur",
-        "flow": "Vorlauftemperatur"
+        "flow": "Vorlauftemperatur",
+        "return": "Rücklauftemperatur"
       }
     },
     "pump_duty_mode": {
diff --git a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
index 55849121d..49fd8394e 100644
--- a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
+++ b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
@@ -2034,6 +2034,8 @@ const STRINGS = {
     "savings.col_pct": "%",
     "savings.estimated": "geschätzt",
     "savings.old_basis": "alte Basis",
+    "savings.below_meter_floor": "keine Einsparung angegeben",
+    "savings.meter_floor_note": "Für einen Monat, dessen Referenz weniger als die Hälfte der vom Zähler erfassten Energie verbraucht hat, wird keine Einsparung angegeben: Eine so niedrige Referenz ist ein Fehler, keine Einsparung.",
     "savings.wood_note": "Die Einsparung enthält Wärme aus Holz. Die Kosten für das Brennholz sind nicht berücksichtigt.",
     "savings.empty": "Noch keine abgeschlossenen Einsparungsmonate.",
     "receipt.closed": "{month} · abgeschlossen",
diff --git a/dev/programme/delivery/3378.md b/dev/programme/delivery/3378.md
new file mode 100644
index 000000000..b0207855b
--- /dev/null
+++ b/dev/programme/delivery/3378.md
@@ -0,0 +1 @@
+- [#3378](https://github.com/tvofi/heatpump_optimizer/pull/3378) — **open**, hotfix(i18n): German strings for the keys #3372 and #3360 added (main red tests/fast) (R10-HOTFIX-MAIN-FAST-1109)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
