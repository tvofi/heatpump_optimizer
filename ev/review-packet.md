# Review packet #3048
head: e5cbb1a9aa2099efd7d9237ef1069d2f81996047
base: 7539d1675d7fc8b5020f90b395f4bb0c3485d5b3

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124607020312 neutral
arch-score / arch-score id=124606796289 success
arm id=124606678753 skipped
budget-raise-gate / budget-raise-gate id=124606796214 success
cancel-superseded id=124606688343 success
codeql / Analyze (actions) id=124606796218 success
codeql / Analyze (javascript-typescript) id=124606796227 success
codeql / Analyze (python) id=124606796256 in_progress
governance / delivery-status id=124606796391 success
governance / delivery-status-publish id=124606797880 skipped
governance / env-matrix id=124606796221 in_progress
governance / instrument-self-tests id=124606796195 in_progress
governance / policy-docs id=124606796235 success
governance / record id=124606797287 skipped
governance / wave-script id=124606796303 success
hassfest / hassfest id=124606796039 success
kernel-points id=124606796743 skipped
prelude id=124606688589 in_progress
refresh id=124606688502 success
tests / arch-instrument id=124606921175 success
tests / briefs id=124606796276 success
tests / browser id=124606921160 in_progress
tests / closure-scope id=124606796228 success
tests / closures id=124606921367 in_progress
tests / coverage id=124606921183 in_progress
tests / fast (3.14) id=124606921176 in_progress
tests / mutation id=124606796208 success
tests / mutation-autofix id=124606936039 skipped
tests / mutation-pins id=124606935576 skipped
tests / nightly-ha id=124606922202 skipped
tests / nightly-status id=124606796185 success
tests / replay id=124606922791 skipped
tests / typing id=124606921088 success
validate / validate-hacs id=124606796117 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE stale tree: 7539d1675d7fc8b5020f90b395f4bb0c3485d5b3 lacks origin/main 9a9659c4f4577c419683b1646d86ee6ebfb772be; roster read at origin/main
NOTE body item 5017455b: R10-USER-DOCS-VERIFY: R10-USER-DOCS-VERIFY resolved on origin/handoff/audit-r10-roster
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tests/doc_claims.py --surfaces | awk -F'\t' 'NF==6{print $1}' | sort | uniq -c
             `tests/doc_claims.py` is in the tree at this head
  ok         python3 tests/doc_claims.py --surfaces >/dev/null; echo $?
             `tests/doc_claims.py` is in the tree at this head
  ok         node tests/md_tables.mjs
             `tests/md_tables.mjs` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         tests/plan_view.py
             `tests/plan_view.py` is in the tree at this head
  ok         node tests/card_drift.mjs
             `tests/card_drift.mjs` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         dev/audit/rounds/round4/D6/claims.py
             `dev/audit/rounds/round4/D6/claims.py` is in the tree at this head
  ok         dev/audit/rounds/round4/D7/sysid_estimator_frontier.py
             `dev/audit/rounds/round4/D7/sysid_estimator_frontier.py` is in the tree at this head
  ok         tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only <merge base>
             `tests/env_drift.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 15 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/README.md b/README.md
index 2b2412ad5..6b2136258 100644
--- a/README.md
+++ b/README.md
@@ -113,7 +113,7 @@ optional mould guard watches surface humidity. Safety — tank minimums, the
 legionella clock, the comfort floor — releases pinned slots it cannot honour and
 tells you which.
 
-**Fits your Home Assistant.** Since v5.0.0 entity names are translated (English
+**Fits your Home Assistant.** Entity names are translated (English
 and Swedish) and follow your Home Assistant language, without touching entity ids
 or history. Monetary units follow your instance currency.
 
@@ -306,8 +306,8 @@ installing rather than discover it after:
   refuses to arm the experiment on such a house and names the reason in the
   log, rather than running a night of excitation whose result the fit's
   guards would silently discard. A house whose floor coupling is fast enough
-  passes the same gate, and there a two-state estimator now exists behind
-  it (#942): a grey-box fit of the heat-loss coefficient and the slab mode's
+  passes the same gate, and there a two-state estimator sits behind
+  it: a grey-box fit of the heat-loss coefficient and the slab mode's
   own time constant — never the slab-mass/coupling split, which no window
   length can identify — carrying the ported intercept ridge and further
   gated on the window's own residual noise staying under ~0.02 °C, refusing
@@ -457,9 +457,7 @@ which end with a working entry. **Quick setup (recommended)** asks one page of
 questions about the house, reads the heat pump's entities automatically and
 returns to this menu; **Continue setup** walks the wizard screens below;
 **Finish setup now** goes straight to the review with shipped defaults you
-refine later in Options. Quick
-setup arrived in v6.6.5 — an install set up on an earlier version never saw
-the menu, and its entries are complete all the same.
+refine later in Options.
 
 **4 · Temperatures.** Your target (21 °C), the band you allow around it, and the
 comfort temperatures for day (21 °C) and night (19.5 °C) with the hours the day
@@ -535,11 +533,11 @@ its configuration or its first evidence, and saying which — so nothing appears
 and disappears under your dashboards. Twenty entities (nineteen sensors and
 the wood binary sensor) are disabled by default because the ordinary install
 cannot light them: optional probes and meters, the capacity tariff, PV, the
-wood furnace, niche hardware, and the one compatibility duplicate (#1669).
-They can be enabled from the entity registry,
+wood furnace, niche hardware, and the one compatibility duplicate (Upper Floor
+Temperature). They can be enabled from the entity registry,
 and an entity enabled later starts collecting from that moment.
 
-Since v5.0.0 the display names are translated (English and Swedish) and follow
+The display names are translated (English and Swedish) and follow
 your Home Assistant language; the tables below show the English names. Entity ids
 and history are unaffected by the language.
 
@@ -590,7 +588,7 @@ every sensor is created on every install regardless of which group it is in.
 | Plan Monthly Savings | CUR | Estimated savings for the open month, with the settled and in-progress months in attributes | Unavailable until at least one month row exists |
 | Cost Contract Comparison | CUR/kWh | How far below the month's flat-consumer average the shifting landed; the three settled totals — hourly spot, monthly-average spot, fixed price — ride in attributes | Diagnostic; disabled by default; needs a configured contract comparison |
 | Lifetime Space Heating Cost | CUR | Accumulating cost | |
-| DHW Cost (lifetime) | CUR | Accumulating cost | Renamed from Hot Water Cost by #174; existing installs keep their entity id |
+| DHW Cost (lifetime) | CUR | Accumulating cost | |
 | Lifetime Total Heating Cost | CUR | Accumulating cost | |
 
 #### The temperatures the optimizer works in
@@ -616,7 +614,7 @@ every sensor is created on every install regardless of which group it is in.
 | Learning Observed COP | — | Efficiency from measurement rather than the nameplate curve | Needs measured power |
 | Measured Power | kW | Real electrical draw, with the commanded power alongside | Disabled by default; unavailable until a power or energy entity is configured |
 | Lifetime Space Heating Energy | kWh | Accumulating, for the Energy dashboard | |
-| DHW Energy (lifetime) | kWh | Accumulating, for the Energy dashboard | Renamed from Hot Water Energy by #174; existing installs keep their entity id |
+| DHW Energy (lifetime) | kWh | Accumulating, for the Energy dashboard | |
 | Lifetime Total Energy | kWh | Accumulating, for the Energy dashboard | |
 | Cost Monthly Peak Power | kW | The peak the capacity tariff is billed on, and the headroom left | Disabled by default; unavailable unless the capacity tariff is enabled |
 | Cost Power Headroom | kW | What the house can draw right now without new cost — a number an EV charger's dynamic limit can follow | Disabled by default; unavailable until a main fuse or capacity tariff bounds the house |
@@ -627,7 +625,7 @@ every sensor is created on every install regardless of which group it is in.
 
 | Sensor | Unit | What it tells you | Notes |
 |---|---|---|---|
-| Solar Irradiance | W/m² | The irradiance the plan uses, with the forecast horizon in attributes | Absorbed the former Solar Radiation sensor in v5.0.0 |
+| Solar Irradiance | W/m² | The irradiance the plan uses, with the forecast horizon in attributes | |
 | Solar Heat Gain | kW | Passive solar gain through the windows right now | |
 | Solar Surplus Forecast | kWh | Forecast PV surplus the heat pump could absorb | Disabled by default; unavailable unless PV is enabled |
 | Thermal Battery Charge | % | State of charge of house and tanks against the comfort band | Unavailable when no store is sensed at all; `components[].measured` and `modelled_components` say which stores are estimated |
@@ -638,7 +636,7 @@ every sensor is created on every install regardless of which group it is in.
 | Sensor | Unit | What it tells you | Notes |
 |---|---|---|---|
 | DHW Setpoint Advisor | °C | The cheapest hot-water setpoint that still covers your heavy days | Diagnostic; unavailable until there is a recommendation |
-| DHW Mixed Water | L | Litres of 40 °C water the tank holds now, with shower minutes alongside | Disabled by default unless the tank thermometer is configured at setup; unavailable without it; renamed from Mixed Hot Water by #174 |
+| DHW Mixed Water | L | Litres of 40 °C water the tank holds now, with shower minutes alongside | Disabled by default unless the tank thermometer is configured at setup; unavailable without it |
 | DHW Heavy Day Demand | kWh | The learned 90th-percentile draw per demand window | Diagnostic; disabled by default; needs weeks of data |
 
 #### How well it is doing, and what it has learned
@@ -662,10 +660,10 @@ Lower Floor Temperature, Measured Power, Slab Temperature (Estimated), Solar
 Surplus Forecast, Upper Floor Temperature, Valve Target Recommendation,
 Wood-Burn Night Advisor and Wood Cheaper Than Heat Pump.
 
-Since #1335 that list is every entity the ordinary install cannot light — the
+That list is every entity the ordinary install cannot light — the
 machinery advisories, the optional probes and meters, the capacity tariff, PV
-and the wood furnace — not only the six niche-hardware sensors it used to be.
-It also carries the one compatibility duplicate (#1669): Upper Floor
+and the wood furnace.
+It also carries the one compatibility duplicate: Upper Floor
 Temperature republishes Indoor Temperature, so it ships off even though the
 ordinary install can produce its number.
 That list assumes hot water itself is configured. Without a hot water tank
@@ -698,6 +696,17 @@ Heating Schedule, DHW Setpoint Advisor and Plan DHW Heating (next 24 h).
 
 ### Switches, climate and datetime entities
 
+| Entity | Platform | What it does |
+|---|---|---|
+| Optimizer Active | switch | Turns the optimizer on and off |
+| Away | switch | Turns the away setback on and off |
+| Away Expected Return | datetime | When you expect to be back; the recovery heat is bought before it |
+| DHW Boost | switch | Maximum hot water heat for two hours |
+| Boost Space Heating | switch | Maximum space heat for two hours |
+| Block DHW | switch | Holds hot water heating at zero for two hours |
+| Block Space Heating | switch | Holds space heating at zero for two hours |
+| Heat Pump Optimizer | climate | A virtual thermostat for your comfort target |
+
 **Optimizer Active** turns the optimizer on and off. Turning it on only acts from
 *off* — it never clobbers a comfort or economy mode you selected deliberately.
 
@@ -1024,11 +1033,43 @@ attribute says which entity and why (e.g. `sensor.tank: stale (last report 600
 min)`). Then press **Prediction Accuracy Diagnose Last Interval** and read the attribution on
 **Prediction Accuracy**.
 
+### Repair notices
+
+Some problems are raised as notices under **Settings → System → Repairs**.
+Each clears itself once the cause is gone.
+
+- **Heat pump efficiency has dropped** — the pump delivers noticeably less heat per kWh than it did under the same conditions, with the monthly cost. Check the filter, the refrigerant and defrost.
+- **Learned model is drifting** — predictions have been off for several days. Check that the sensors read sensibly; the `restore_learned_snapshot` service rolls the learners back to the last healthy weekly snapshot.
+- **Learned model was restored from a snapshot** — the drift above happened while every input looked healthy, so the learners were rolled back automatically. Nothing is required.
+- **Frequency control stood down** — the compressor frequency kept diverging from the commanded value, so frequency control fell back to observe. Check the entity, then switch the frequency mode to observe, save, and back to control.
+- **Optimization keeps failing; the plan is going stale** — several solves in a row failed. Once the plan is a few intervals old the pump is handed back to its own heating curve. Look for a lost price or weather connection, or a solver error in the log.
+- **Planning fell back to the slow in-process solver** — the separate solver process could not be used, so Home Assistant may feel briefly unresponsive on each solve. Attach the reported cause and the log to a bug report.
+- **Floor return temperature sensor is not reporting** — the slab temperature is carried forward from the plan's prediction until the sensor reads again. Check the entity, or clear the slot.
+- **Heat pump operating mode entity is not reporting** — the plan stops being held to the last mode it read. Check the entity, or clear the slot.
+- **The pump's disinfection switch may still be on** — a disinfection switch the optimizer turned on cannot be read any more. Check the pump and turn the switch off by hand.
+- **The pump's disinfection switch could not be set** — Home Assistant refused the write. It is retried on every update; check the entity, or set the switch mode back to observe.
+- **Hot water disinfection is overdue: the heat pump's mode blocks it** — the pump reports a mode that makes no hot water, so the cycle cannot be scheduled. Change the pump's mode.
+- **Hot water has not been disinfected for N days** — no cycle has been confirmed at temperature within the interval. An immersion heater for the last few degrees, or a disinfection temperature the system can hold, is the usual answer.
+- **Hot water is not reaching the disinfection temperature** — the cycle ran and the tank fell short. Same remedies as above; the cycle is retried about a day later.
+- **The disinfection cycle cannot be verified** — no tank temperature sensor confirms the cycle. Assign the *Hot water tank temperature sensor* to a real probe.
+- **Disinfection goes above your hot water charge limit** — the disinfection temperature is above the charge limit. That is allowed; the notice says so, so the one hot day per interval is no surprise.
+- **The price feed and Home Assistant name different currencies** — costs are published in the feed's currency. Set Home Assistant's currency to match, or choose a price sensor in it.
+- **A price entity reports a unit the optimizer cannot read** — the number is used as published. Choose a sensor that prices per kWh, MWh or Wh in a currency or its hundredth.
+- **A configured grid fee looks 100× too large** — almost always öre or cents entered where whole currency was meant. Correct it on **Transfer fees and contract**.
+- **A configured grid fee is negative** — almost always a sign slip. Correct it on **Transfer fees and contract**.
+- **The downstairs temperature is modelled, not measured** — two-zone planning without a lower-floor thermometer. Assign the *Lower floor temperature sensor* to remove it.
+- **Your comfort temperatures contradict each other** — the stored band cannot all be met at once, for example a target above the warmest acceptable temperature. Fix the band on **Comfort and temperatures**.
+- **The heat pump's hot water set-point is below the configured temperature** — the pump's own set-point stops it reaching the disinfection or minimum temperature. The notice's fix writes the needed value to the pump's entity.
+- **The space-heating set-point entity is not reporting** — the set-point entity is missing or unreadable. Check it, or clear the slot.
+- **The heat pump does not hold a setting the optimizer wrote** — the pump reads back something else after two writes. To change the pump by hand, turn **Optimizer Active** off first.
+- **Stored learning could not be read** — stored data from another version could not be read, so that part of what was learned starts again from defaults. The integration keeps running.
+- **Silent windows are not enforced** — the capacity-limited slot is not a switch the integration can hold. Assign the pump's own night-mode switch, or remove the silent windows.
+
 ## ECL110 heat-curve control
 
 The integration can drive a Danfoss ECL110-compatible controller over MQTT,
 publishing a heat-pump on/off decision and an integer parallel shift (*displace*)
-onto the controller's own heat curve. Since v4.1.0 the ECL110 settings live only
+onto the controller's own heat curve. The ECL110 settings live only
 on the **Heat curve control (ECL110)** options page, not in initial setup, and
 both ECL110 sensors are disabled by default. The MQTT topics ship empty;
 nothing is published or subscribed until you set a topic, so an install without
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index b6df29eea..d8cc47111 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -263,18 +263,18 @@
  {
   "id": "C30",
   "source": "docs/configuration.md",
-  "claim": "every documented Default (89 rows) is the default the rendered options page actually carries",
+  "claim": "every documented Default (92 rows) is the default the rendered options page actually carries",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "89 compared, mismatches=[]",
+  "result": "92 compared, mismatches=[]",
   "verdict": "true",
   "truth": ""
  },
  {
   "id": "C31",
   "source": "docs/configuration.md",
-  "claim": "every documented Range (92 rows) is the NumberSelector min/max the rendered options page actually carries",
+  "claim": "every documented Range (101 rows) is the NumberSelector min/max the rendered options page actually carries",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "92 compared, mismatches=[]",
+  "result": "101 compared, mismatches=[]",
   "verdict": "true",
   "truth": ""
  },
@@ -965,9 +965,9 @@
  {
   "id": "C108",
   "source": "README.md + docs/*.md",
-  "claim": "every relative link resolves (83 links)",
+  "claim": "every relative link resolves (85 links)",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "83 links, broken=[], of which removed-by-the-export=[]",
+  "result": "85 links, broken=[], of which removed-by-the-export=[]",
   "verdict": "true",
   "truth": ""
  },
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index 1e353093f..9ec94de0a 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -33,8 +33,8 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C27 | `docs/configuration.md` | There are 23 pages | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=23 measured=23 | **true** |  |
 | C28 | `docs/configuration.md` | eight on the first menu and fifteen more behind Advanced settings | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=(8, 15) measured=(8, 15) | **true** |  |
 | C29 | `docs/architecture.md:module map` | config_flow.py -- Setup flow plus 23 option pages behind two menus | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=23 measured=23 | **true** |  |
-| C30 | `docs/configuration.md` | every documented Default (89 rows) is the default the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 89 compared, mismatches=[] | **true** |  |
-| C31 | `docs/configuration.md` | every documented Range (92 rows) is the NumberSelector min/max the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 92 compared, mismatches=[] | **true** |  |
+| C30 | `docs/configuration.md` | every documented Default (92 rows) is the default the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 92 compared, mismatches=[] | **true** |  |
+| C31 | `docs/configuration.md` | every documented Range (101 rows) is the NumberSelector min/max the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 101 compared, mismatches=[] | **true** |  |
 | C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=84 measured=84 | **true** |  |
 | C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=84, listed=84, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
 | C34 | `docs/architecture.md:The Home Assistant boundary` | the boundary sentence's count of modules importing `homeassistant` at module level | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=28 measured=28 | **true** |  |
@@ -111,7 +111,7 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C105 | `docs/automations.md` | the Power Headroom sensor appears once anything bounds the house -- a main fuse OR a capacity tariff -- and a tariff-only install reads 0.0 kW with limit_source='capacity tariff with no peak reference yet' until the month's first metering window closes; with neither it stays unavailable | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | no fuse + capacity tariff enabled -> {'available': True, 'limit_kw': 0.0, 'headroom_kw': 0.0, 'baseline_source': 'planned power only (no meter)', 'limit_source': 'capacity tariff with no peak reference yet'}; fuse only -> available=True; neither -> available=False | **true** |  |
 | C106 | `docs/automations.md` | Power Headroom is min(main fuse, capacity threshold) - current house draw, clamped at zero, in kW | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | fuse 20 A 3-phase -> limit_kw=13.8, headroom_kw=13.8, limit_source='main fuse' | **true** |  |
 | C107 | `README.md + docs/*.md + the card` | every entity id quoted in the documentation is an entity the platforms construct | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 9 distinct ids cited, not constructed=[] | **true** |  |
-| C108 | `README.md + docs/*.md` | every relative link resolves (83 links) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 83 links, broken=[], of which removed-by-the-export=[] | **true** |  |
+| C108 | `README.md + docs/*.md` | every relative link resolves (85 links) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 85 links, broken=[], of which removed-by-the-export=[] | **true** |  |
 | C109 | `README.md + docs/how-it-works.md` | the links to docs/audit-2026-08.md, docs/audit-2026-09.md and docs/backlog.md resolve | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | finder_wall in tools/audit/prepare_baseline.sh removes docs/audit-*.md, dev/archive/audits/audit-*.md and dev/archive/backlog.md; this tree cannot answer | **unverifiable** | not checkable in the export -- finder_wall removes docs/audit-*.md, dev/archive/audits/audit-*.md and dev/archive/backlog.md |
 | C110 | `README.md + docs/*.md` | every image the documentation embeds exists (21 images) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 21 images, missing=[] | **true** |  |
 | C111 | `README.md + docs/*.md` | every external link answers 200 to a HEAD request (19 links) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py --links` | not run: pass --links | **unverifiable** | re-run with --links |
diff --git a/dev/audit/rounds/round4/D6/claims.py b/dev/audit/rounds/round4/D6/claims.py
index 7626132ba..a5cef8fd7 100644
--- a/dev/audit/rounds/round4/D6/claims.py
+++ b/dev/audit/rounds/round4/D6/claims.py
@@ -51,7 +51,7 @@ against a document that is CORRECT.
     RESULT claims_false=0
     RESULT claims_stale=0
     RESULT claims_unverifiable=2    (1 with --links; the checker runs the default)
-    RESULT config_defaults_compared=89   (76 until #937's rows landed; 82
+    RESULT config_defaults_compared=92   (76 until #937's rows landed; 82
                                          until #1067's solver half documented
                                          the flow-curve lift option's default;
                                          83 until #1067's silent-mode half
@@ -70,8 +70,11 @@ against a document that is CORRECT.
                                          fields document no defaults; 89 with
                                          #1495's mold-floor breach warning
                                          margin, a NumberSelector Default row
-                                         on the Comfort and temperatures table)
-    RESULT config_ranges_compared=92     (76 until #937's rows landed; 86
+                                         on the Comfort and temperatures table;
+                                         92 with R10-USER-DOCS-FINAL, which
+                                         gives every options field a row of
+                                         its own under its page)
+    RESULT config_ranges_compared=101    (76 until #937's rows landed; 86
                                          until #1067's silent-mode half
                                          documented the derate's range; 87
                                          until its frequency half documented
@@ -81,7 +84,8 @@ against a document that is CORRECT.
                                          only one this re-record adds; 92 with
                                          R10-COP-PARTLOAD's part-load derate
                                          Range row on the expert thermal-model
-                                         table)
+                                         table; 101 with R10-USER-DOCS-FINAL's
+                                         per-field rows on the options pages)
     RESULT arch_modules_on_disk=84       (83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
                                          66 until R9 F2.5's batchmath.py;
                                          65 until #1588's pump_arbiter.py; 64
diff --git a/dev/programme/delivery/3048.md b/dev/programme/delivery/3048.md
new file mode 100644
index 000000000..1c5b8cea4
--- /dev/null
+++ b/dev/programme/delivery/3048.md
@@ -0,0 +1 @@
+- [#3048](https://github.com/tvofi/heatpump_optimizer/pull/3048) — **open**, R10-USER-DOCS-FINAL: user docs final (R10-USER-DOCS-FINAL)
diff --git a/docs/configuration.md b/docs/configuration.md
index 8fd441ab2..40b177519 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -63,7 +63,7 @@ install with no entry yet has it off, so this never fires on first setup.)
 Every route ends on the same read-only review screen, and confirming there is
 what actually creates the entry.
 
-### 1 · Basics
+### 1 · Basics — Heat Pump Optimizer Setup
 
 Where the prices, the forecast and your own measurements come from. The token
 is checked against Tibber before the flow continues, and a network failure is
@@ -72,9 +72,9 @@ reported as a connection problem rather than as a bad token.
 | Setting | Default | What it means |
 |---|---|---|
 | Name for this integration | Heat Pump Optimizer | Shown in front of every entity this integration creates. |
-| Price source | Tibber | Where hourly electricity prices come from: Tibber (needs the token below) or a price sensor entity you already have. |
+| Electricity price source | Tibber | Where hourly electricity prices come from: Tibber (needs the token below) or a price sensor entity you already have. |
 | Tibber API token | — (**required with the Tibber source**) | Reads your hourly electricity prices. Create one at developer.tibber.com. The field still shows when the price source is a price entity — not needed then, so leave it empty. |
-| Price entity | — (**required with the price-entity source**) | A `sensor` publishing the current electricity price, read instead of Tibber. |
+| Price sensor (Nord Pool or similar) | — (**required with the price-entity source**) | A `sensor` publishing the current electricity price, read instead of Tibber. |
 | Weather forecast | — (**required**) | A `weather` entity supplying outdoor temperature, wind and rain for the next 24 hours. The optimizer plans ahead, so a forecast is not optional. |
 
 ### 2 · Optional sensors
@@ -93,23 +93,74 @@ Every picker on this second screen is optional; skip any you do not have. Withou
 | Lower floor temperature sensor | none | Two-zone houses only. Without it the lower zone is modelled from the main room sensor and labelled as modelled on the plan chart; a repair notice says so. |
 | Hot water tank temperature sensor | none | Recommended. Lets a manual hot-water boost reset the anti-legionella timer, and unlocks the learned draw quantiles. Without one, a disinfection cycle the plan commands resets the countdown but is recorded as an *attempt* rather than a verified cycle, and a note in Repairs says the cycle cannot be verified. |
 | Buffer tank temperature sensor | none | When set, the tank's cooling rate is learned instead of assumed. |
-| Heat pump operating mode | none | The pump's own mode selector — cooling, heating, hot water, or a combination of two. Read only unless **Pump duty control** is set to Control. Left empty, the optimizer assumes the pump can do everything, exactly as before. |
+| Heat pump operating mode | none | The pump's own mode selector — cooling, heating, hot water, or a combination of two. Read only unless **Pump duty control** is set to Control. Left empty, the optimizer assumes the pump can do everything. |
 | Defrosting | none | On while the pump reverses to melt frost off the outdoor coil. A sample of defrost activity, not a stopwatch — many pumps are only polled every few minutes. |
 | Pump online | none | Strongly recommended for a cloud-connected pump. On while the pump is actually reachable, which a stale cloud republish cannot tell you on its own. |
 | Fault alarm | none | On while the pump is reporting a fault. Only whether there is a fault is used, never the code itself. |
 
-The Danfoss ECL110 MQTT fields were asked here until v4.1.0. Eight questions
+The Danfoss ECL110 MQTT settings are not asked during setup. Eight questions
 only ECL110 owners can answer do not belong on everyone's first screen, so they
-now live on their own options page — where both MQTT topics ship empty and
-nothing is published or subscribed until a topic is set (see
-[ecl110.md](ecl110.md)); an install without an ECL110 never touches the
-topics.
+live on their own options page, where both MQTT topics ship empty and nothing
+is published or subscribed until a topic is set (see [ecl110.md](ecl110.md));
+an install without an ECL110 never touches the topics.
 
-### 3 · The finish menu
+### 3 · The finish menu — Finish setup now?
 
 After the optional sensors the flow asks **Finish setup now?** with three answers, drawn in the diagram above: **Quick setup (recommended)**, **Continue setup** and **Finish setup now**. Quick setup and its pre-fill return to this menu; Continue setup runs the screens numbered 4 to 7 below; Finish setup now goes to the review. Nothing else on this menu has fields of its own.
 
-### 4 · Temperatures
+### The Quick setup screen
+
+**Quick setup (recommended)** asks the whole house on one page: five yes/no
+questions, the two wood-tank probes, and the six building questions from
+[Describe your building](#describe-your-building). What each answer means is
+in [setup.md](setup.md#quick-setup-recommended).
+
+| Setting | Default | What it means |
+|---|---|---|
+| Two-zone house | off | Two separately heated floors, balanced against each other. |
+| Buffer tank | off | A tank between the pump and the heating circuits large enough to store heat (recorded as 500 L). |
+| Hot water tank | on | The pump keeps a domestic hot water tank. Off removes hot water from the plan. |
+| Wood furnace | off | A wood furnace heats the same water loop. |
+| Wood buffer tank | off | A second tank the wood furnace heats. |
+| Wood tank top sensor (optional) | none | With the bottom sensor, says how much a fire has left. |
+| Wood tank bottom sensor (optional) | none | See the top sensor. Both are needed for the remaining-energy estimate. |
+| What the house is built from | Timber frame on a concrete slab | As on [Describe your building](#describe-your-building). |
+| Roughly when it was built | 1980–2005 | As above. |
+| Foundation | Slab on ground | As above. |
+| Heated floor area | 140 m² | As above. |
+| Upper floor heating | Radiators | As above. |
+| Lower floor heating | Floor heating | As above. |
+
+### The Pre-fill from a heat pump device screen
+
+After Quick setup, and on the full path when the offer is switched on, this
+screen reads the heat pump's own entities. The first submit names the device;
+the second shows what its entities suggest, as ordinary fields you can edit or
+clear. Nothing is written until that second submit, and leaving the device
+empty skips the screen. Where each suggestion comes from is listed under
+[Pre-fill from a heat pump device](#pre-fill-from-a-heat-pump-device).
+
+| Setting | Default | What it means |
+|---|---|---|
+| Heat pump device | none | The pump's device. Leave it empty to skip. |
+| Highest tank temperature to charge to | read from the device | The pump's own hot water setpoint. |
+| Anti-legionella temperature | read from the device | The pump's anti-legionella setpoint. |
+| Hot water temperature you need | read from the device | The pump's economy hot water setpoint. |
+| When you need hot water | read from the device | The pump's hot water schedule. Keeping it turns hot water planning on. |
+| Anti-legionella interval | read from the device | The pump's anti-legionella schedule. |
+| Pump's own night-mode schedule | read from the device | When the pump limits itself to its quiet mode. |
+| Heat pump max power (kW) | read from the device | The unit's capacity divided by the nominal COP. |
+| What that set-point entity expects | read from the device | Flow temperature when the pump runs on water temperature control. |
+| What the control entity expects | read from the device | The same, for a mixing valve, only where the two-zone model is configured. |
+| Outdoor temperature sensor | read from the device | Suggested only while the slot is empty. |
+| Hot water tank temperature sensor | read from the device | Suggested only while the slot is empty. |
+| Supply (flow) water temperature | read from the device | Suggested only while the slot is empty. |
+| Return water temperature | read from the device | Suggested only while the slot is empty. |
+| Actual frequency sensor (recommended for control) | read from the device | Suggested only while the slot is empty. |
+| Capacity limited (night mode) | read from the device | Suggested only while the slot is empty. |
+| After saving | Menu | The options page's own navigation control, shown on this form too; setup continues to the finish menu whatever it says. |
+
+### 4 · Temperature Settings
 
 The gap between your target and your minimum is what makes savings possible:
 the wider it is, the further the house may coast through an expensive hour.
@@ -133,7 +184,9 @@ end). The same checks run on the options page later.
 
 ### 5 · Your building — two ways to answer
 
-**Describe my building (recommended).** Six questions with answers a homeowner
+#### Describe your building
+
+**Describe my building (recommended)** opens this screen. Six questions with answers a homeowner
 knows, from which the thermal masses, the heat-loss coefficient and the slab
 parameters are derived. These are starting values; the self-learning model
 corrects them from how the house actually behaves, so they need not be exact.
@@ -147,6 +200,8 @@ corrects them from how the house actually behaves, so they need not be exact.
 | Upper floor heating | Radiators | Radiators · Floor heating | Radiators respond in minutes, floor heating in hours. This sets how far ahead heat can usefully be shifted. |
 | Lower floor heating | Floor heating | Radiators · Floor heating | A heated slab is a large store that gets actively charged, which makes pre-heating both more valuable and more necessary. |
 
+#### Your heat pump
+
 Then three numbers off the heat pump's nameplate:
 
 | Setting | Default | Range | What it means |
@@ -161,8 +216,10 @@ on, and a fresh install should not be given a two-zone model it did not ask
 for. If your house does have two independently modelled floors, turn it on
 afterwards on **Advanced settings → Thermal model (expert)**.
 
-**Enter thermal values directly** is for someone holding a real energy
-declaration. It asks the model's own numbers:
+#### Thermal Model & Optimization
+
+**Enter thermal values directly** opens this screen. It is for someone holding a real energy
+declaration, and asks the model's own numbers:
 
 | Setting | Default | Range | What it means |
 |---|---|---|---|
@@ -178,10 +235,13 @@ declaration. It asks the model's own numbers:
 | How hard to chase low prices | 1.0 | 0.1–10, 0.1 steps | Higher moves more heating into cheap hours, at the cost of more temperature swing. |
 | How strictly to hold the temperature | 5.0 | 0.1–20, 0.1 steps | The counterweight. Around 5 lets the house drift freely inside your allowed range; 10 keeps it noticeably closer to target; 20 or more behaves like an ordinary thermostat. |
 
-followed by the two-zone and solar page:
+#### Two-Zone & Solar Configuration
+
+The direct path continues on the two-zone and solar screen:
 
 | Setting | Default | Range | What it means |
 |---|---|---|---|
+| The house has two zones (two floors heated separately) | unticked | on/off | On: the two-zone model runs and the zone fields below apply. Off: the house is modelled as one zone whatever the fields say. An untouched screen answers no. |
 | Upper floor thermal mass | 3.0 kWh/°C | 0.25–60 | Heat stored in the upper zone. Usually much lower than a heated slab, so the zone reacts faster. |
 | Lower floor thermal mass | 8.0 kWh/°C | 0.25–60 | Heat stored in the lower zone. |
 | Upper floor heat loss | 0.08 kW/°C | 0.001–1.0 | The upper zone's own loss coefficient. |
@@ -194,11 +254,11 @@ followed by the two-zone and solar page:
 | Solar orientation factor | 0.7 | 0.0–1.0 | How well the glazing faces the sun over a day. 1.0 suits mostly south-facing windows. |
 | How much sunlight the windows let through | 0.7 | 0.1–1.0 | The glazing's solar heat gain coefficient. About 0.6 for modern triple glazing. |
 
-Filling in any of the upper mass, lower mass, inter-zone transfer or radiator
-share is what turns the two-zone model on. That is why this page is skipped on
-the questionnaire path.
+The tick box at the top decides the two-zone model; the zone fields only apply
+while it is on. The questionnaire path skips this screen, so a fresh install
+is single-zone until you turn two-zone on.
 
-### 6 · Hot water
+### 6 · Hot water — Domestic Hot Water (DHW) Configuration
 
 Tell the optimizer when you actually need hot water. It then guarantees a
 usable tank temperature during those periods and heats in the cheapest hours
@@ -207,6 +267,7 @@ the saving comes from.
 
 | Setting | Default | Range | What it means |
 |---|---|---|---|
+| The house has a hot water tank | unticked, or your Quick setup answer | on/off | On: hot water is planned and the tank charged. Leave it off unless the heat pump really heats a tank; the other fields only apply while it is on. |
 | Hot water tank size | 200 L | 50–1500, 10 steps | A larger tank stores more cheap electricity and can skip more expensive hours. |
 | Highest tank temperature to charge to | 55 °C | 40–65 | An upper limit on charging, not a target. The tank is only filled this high when storing extra cheap heat pays. |
 | Hot water temperature you need | 45 °C | 35–55 | Guaranteed inside the time frames below. Must be at least 5 °C below the charge limit, or the plan sits in permanent slight violation. |
@@ -215,7 +276,7 @@ the saving comes from.
 | Only guarantee hot water at set times | on | on/off | Off keeps the tank hot around the clock, which costs noticeably more. |
 | When you need hot water | `06:00-08:30, 17:00-22:00` | 24-hour times, comma separated | The tank is heated in the cheapest hours before each period. Each period must be at least 15 minutes — one planning step; a shorter one can fall between two steps and never take effect. Leave empty to let the integration learn your habits from actual usage. |
 | Let the tank cool to | 20 °C | 10–55 | How cold the tank may get between periods. The default is roughly room temperature — nothing is spent at all. |
-| Run an anti-legionella cycle | on | on/off | Because the tank now spends long stretches cool, it is periodically heated hot enough to kill legionella. Strongly recommended. |
+| Run an anti-legionella cycle | on | on/off | Because the tank spends long stretches cool, it is periodically heated hot enough to kill legionella. Strongly recommended. |
 | Anti-legionella temperature | 60 °C | 55–70 | The usual recommendation is 60 °C. Check what applies where you live. This applies only while a cycle is running: if it is above the charge limit above, the tank goes above that limit for the cycle and at no other time. |
 | Anti-legionella interval | 7 days | 1–30 | Placed in the cheapest hour before each deadline. |
 
@@ -224,17 +285,32 @@ Per-weekday windows are an options-page feature (see
 single field takes the same grammar, including day selectors such as
 `weekdays 06:00-08:30, weekend 08:00-09:30`.
 
-### 7 · Weather sensitivity
+### 7 · Weather Sensitivity Parameters
 
 | Setting | Default | Range | What it means |
 |---|---|---|---|
 | Wind sensitivity | 0.03 | 0.0–0.5, 0.01 steps | Extra heat loss per m/s of wind — 0.03 means 3 % more loss per m/s. Raise it if the house noticeably cools on windy days. |
 | Rain sensitivity | 1.15 | 1.0–1.5, 0.01 steps | Loss multiplier while it is raining. 1.0 means rain makes no difference. |
 
-Saving this page moves to the read-only review screen — confirming there is
+Saving this page moves to the review screen.
+
+### The review screen — Your system, as configured
+
+Every route ends here: a read-only picture of what you described, the zones,
+the tanks and every sensor slot with what is assigned to it. Confirming it is
 what creates the entry. All 82 entities appear at once and the first plan is
 solved within one optimization interval.
 
+### Reauthenticate Tibber
+
+When Tibber refuses the stored token, Home Assistant asks you to
+re-authenticate the integration under **Settings → Devices & services**, which
+opens this screen. Enter a valid token and price updates resume.
+
+| Setting | Default | What it means |
+|---|---|---|
+| Tibber API token | none | A new token from developer.tibber.com. |
+
 ---
 
 ## Changing settings later
@@ -288,23 +364,30 @@ slots are shown as empty on purpose — the point is to reveal what is missing.
 
 ### Comfort and temperatures
 
-The seven weekday fields are exactly those from setup step 2 — the target,
-minimum and maximum, the two comfort temperatures and the two day hours —
-with the same defaults, ranges and cross-checks. The weekend and holiday
-schedules live here too, and each of their fields starts as a copy of the
-weekday value it mirrors; leave every one at that default and weekends and
-holidays simply follow the weekday plan.
+The seven weekday fields are those of the
+[Temperature Settings](#4--temperature-settings) screen, with the same
+defaults, ranges and cross-checks. The weekend and holiday schedules live here
+too, and each of their fields starts as a copy of the weekday value it mirrors;
+leave every one at that default and weekends and holidays simply follow the
+weekday plan.
 
 | Setting | Default | Range | What it means |
 |---|---|---|---|
+| Target indoor temperature | 21.0 °C | 15–28, 0.5 steps | What you actually want. The optimizer aims here and only drifts to avoid expensive hours. |
+| Coldest acceptable temperature | 19.0 °C | 14–25 | The coldest the plan will take the house. Priced, not fenced, but firm at any real price. |
+| Warmest acceptable temperature | 23.0 °C | 18–28 | A limit on pre-heating during cheap hours, never a target. |
+| Daytime comfort temperature | 21.0 °C | 16–26 | Preferred temperature during waking hours. |
+| Night-time comfort temperature | 19.5 °C | 15–24 | Preferred temperature overnight. |
+| Day starts at | 07 | 00–23 | Hour the daytime temperature takes over. |
+| Day ends at | 22 | 01–24 | Hour the night temperature takes over. |
 | Weekend daytime comfort | weekday daytime value | 16–26, 0.5 steps | Preferred temperature during weekend waking hours. |
 | Weekend night-time comfort | weekday night-time value | 15–24, 0.5 steps | Preferred temperature overnight on Saturday and Sunday. |
-| Weekend day starts at | weekday start (07) | 00–23 | Hour the weekend daytime temperature takes over. |
-| Weekend day ends at | weekday end (22) | 01–24 | Hour the weekend night temperature takes over. 24 keeps the daytime temperature until midnight. |
+| Weekend day starts at | the weekday start | 00–23 | Hour the weekend daytime temperature takes over. |
+| Weekend day ends at | the weekday end | 01–24 | Hour the weekend night temperature takes over. 24 keeps the daytime temperature until midnight. |
 | Holiday daytime comfort | weekday daytime value | 16–26, 0.5 steps | Daytime comfort on days the holiday-profile calendar is on. Away setback still wins if away is active. |
 | Holiday night-time comfort | weekday night-time value | 15–24, 0.5 steps | Overnight comfort on holiday-calendar days. |
-| Holiday day starts at | weekday start (07) | 00–23 | Hour the holiday daytime temperature takes over. |
-| Holiday day ends at | weekday end (22) | 01–24 | Hour the holiday night temperature takes over. |
+| Holiday day starts at | the weekday start | 00–23 | Hour the holiday daytime temperature takes over. |
+| Holiday day ends at | the weekday end | 01–24 | Hour the holiday night temperature takes over. |
 
 Four mold-guard fields complete the page:
 
@@ -327,7 +410,13 @@ advanced pages.
 | When you need hot water | `06:00-08:30, 17:00-22:00` | 24-hour times, comma separated | The tank is heated in the cheapest hours before each period. Each period must be at least 15 minutes. Leave empty to let the integration learn your habits from actual usage. |
 | Holiday hot-water windows | empty | same grammar | Used on days the holiday calendar is on, instead of weekday/weekend. Leave empty to keep the ordinary schedule. |
 | Customize by weekday | off | on/off | Reveals seven fields, one per weekday, below the ordinary ones. |
-| Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday | empty | 24-hour times, comma separated | Hot-water times for that weekday only. Leave empty to inherit. |
+| Monday | empty | 24-hour times, comma separated | Hot-water times for Mondays only. Leave empty to inherit. |
+| Tuesday | empty | 24-hour times, comma separated | Hot-water times for Tuesdays only. Leave empty to inherit. |
+| Wednesday | empty | 24-hour times, comma separated | Hot-water times for Wednesdays only. Leave empty to inherit. |
+| Thursday | empty | 24-hour times, comma separated | Hot-water times for Thursdays only. Leave empty to inherit. |
+| Friday | empty | 24-hour times, comma separated | Hot-water times for Fridays only. Leave empty to inherit. |
+| Saturday | empty | 24-hour times, comma separated | Hot-water times for Saturdays only. Leave empty to inherit. |
+| Sunday | empty | 24-hour times, comma separated | Hot-water times for Sundays only. Leave empty to inherit. |
 
 **Per-weekday windows, and how the layers stack.** One schedule rarely fits
 a week with early workdays, a late Saturday and a Sunday that starts at
@@ -336,7 +425,7 @@ noon. You can already type day selectors into the ordinary field
 the form version — switch it on, save, reopen the page, and seven fields
 appear, each holding one weekday's times in the same comma-separated
 format (`12:00-24:00` for "nothing until noon"). An empty field does not
-mean "no hot water that day"; it means *inherit*, exactly as before.
+mean "no hot water that day"; it means *inherit*.
 
 ![The Hot water options page with the Customize by weekday switch on: the ordinary windows field above, then seven weekday fields, Monday and Saturday filled, the rest empty to inherit](img/card/options-hot-water-by-day.png)
 
@@ -376,7 +465,7 @@ The temperatures the schedule holds the tank to:
 | Let the tank cool to | 20 °C | 10–55 | How cold the tank may get between periods. The default is roughly room temperature — nothing is spent at all. |
 | Highest tank temperature to charge to | 55 °C | 40–65 | An upper limit on charging, not a target. The tank is only filled this high when storing extra cheap heat pays. |
 | Heat pump DHW set-point entity | none | `number` / `input_number` / `climate` | Optional. The pump's own DHW set-point, used to notice when it cannot be read and, with **Pump duty control** at Control, written with the hot water set-point above. |
-| Run an anti-legionella cycle | on | on/off | Because the tank now spends long stretches cool, it is periodically heated hot enough to kill legionella. Strongly recommended. |
+| Run an anti-legionella cycle | on | on/off | Because the tank spends long stretches cool, it is periodically heated hot enough to kill legionella. Strongly recommended. |
 | Anti-legionella temperature | 60 °C | 55–70 | The usual recommendation is 60 °C. Check what applies where you live. |
 | Anti-legionella interval | 7 days | 1–30 | Placed in the cheapest hour before each deadline. |
 
@@ -412,7 +501,7 @@ are on their own advanced pages.
 | My grid bill has a capacity charge | off | on/off | Adds the monthly power-peak fee to the objective, so flattening peaks is worth actual money. |
 | Capacity charge per kW per month | 45 | 0–500 | Take it from your grid invoice; it varies a lot between companies. |
 | Number of peak hours averaged | 3 | 1–10 | Most Swedish tariffs average the three highest hours of the month. |
-| Measurement window | 1 hour | 15 minutes / 1 hour | Swedish DSOs move to 15-minute settlement through 2026–27. Pick 15 when your bill averages the highest 15-minute windows; 60 keeps the older hourly clock. Hourly prices are smeared evenly across the four quarters — a 15-minute sauna spike is billed in full only when the window is 15. |
+| Measurement window | hourly | 15 minutes / 1 hour | Swedish DSOs move to 15-minute settlement through 2026–27. Pick 15 when your bill averages the highest 15-minute windows; 60 keeps the older hourly clock. Hourly prices are smeared evenly across the four quarters — a 15-minute sauna spike is billed in full only when the window is 15. |
 | Months the capacity tariff applies | empty | e.g. `Nov-Mar` | Empty means every month. Outside these months a peak contributes nothing, and the plan knows it. |
 | Peak hours | empty | e.g. `07:00-19:00` | Empty means every hour counts in full. Outside these hours a peak counts at the factor below. |
 | Weekends are off-peak | off | on/off | Many tariffs only bill weekday peaks. |
@@ -432,6 +521,15 @@ device page and on the card, not here.
 | Temperature while away | 16.0 °C | 5–21, 0.5 steps | Low enough to save, high enough to protect the house and its plumbing. |
 | Hot water minimum while away | 20.0 °C | 10–55 | The anti-legionella cycle still runs, timed to finish before you get back. |
 
+### Quick setup
+
+The one-page house questions of [the Quick setup screen](#the-quick-setup-screen),
+pre-filled with this entry's own recorded answers. Change an answer and submit,
+and the thermal model is re-derived from the questionnaire; submit without
+changing anything and nothing is written. The device pre-fill is not offered
+here: an existing entry's sensor slots are already answered, and that read
+stays on [Pre-fill from a heat pump device](#pre-fill-from-a-heat-pump-device).
+
 ### Pre-fill from a heat pump device
 
 The pump keeps several of the answers the other pages ask for, and this page
@@ -504,14 +602,18 @@ are on **Power and solar sensors**; mode / defrost / online / fault are on
 | Setting | Default | Range | What it means |
 |---|---|---|---|
 | Electricity price source | Tibber | Tibber / Price entity | Tibber uses the API token. Entity reads a Home Assistant price sensor (Nord Pool, ENTSO-E, similar) with `raw_today` / `raw_tomorrow`. |
-| Tibber API token | from setup | required when source is Tibber | Re-validated against Tibber whenever you change it. Not required for an entity source. |
+| Tibber API token | — (the setup value) | required when source is Tibber | Re-validated against Tibber whenever you change it. Not required for an entity source. |
 | Price sensor | none | a price sensor | Required when the source is an entity. Typical attributes are `raw_today` and `raw_tomorrow`. |
 | VAT multiplier | 1.0 | 0–2, 0.01 steps | Applied to entity-sourced prices as value × VAT + surcharge. 1.0 leaves the values unchanged; Tibber prices are used as delivered. |
 | Surcharge per kWh | 0 | 0–2, 0.01 steps | Added on top after the multiplier, in the same currency as your prices. 0 leaves the values unchanged. |
-| Weather forecast | from setup | required | The forecast source. |
-| Indoor / outdoor temperature | from setup | temperature sensors | See setup step 1. |
-| Hot water tank, buffer tank, floor return, lower floor sensors | from setup | temperature sensors | See setup step 1. |
-| Heat pump on/off switch | from setup | a `switch` | See setup step 1. |
+| Weather forecast | — (the setup value) | required | The forecast source. |
+| Indoor temperature sensor | the setup value | a temperature sensor | As on [Optional sensors](#2--optional-sensors). Clearing it leaves the plan on its own model. |
+| Outdoor temperature sensor | the setup value | a temperature sensor | As on Optional sensors. |
+| Hot water tank temperature sensor | the setup value | a temperature sensor | As on Optional sensors. |
+| Buffer tank temperature sensor | the setup value | a temperature sensor | As on Optional sensors. |
+| Floor heating return temperature sensor | the setup value | a temperature sensor | As on Optional sensors. |
+| Lower floor temperature sensor | the setup value | a temperature sensor | As on Optional sensors. Two-zone houses only. |
+| Heat pump on/off switch | the setup value | a `switch` | As on Optional sensors. |
 | Space-heating set-point entity | none | `number` / `input_number` / `climate` | Optional. Used to notice when the entity cannot be read. Written only with **Pump duty control** at Control, and then with the plan's own number (see below), never a recommended optimum. |
 | What that set-point entity expects | Indoor temperature | Indoor temperature / Flow temperature | A declaration, not a write. Pointing an indoor target at a flow entity would command roughly 21 °C to something expecting 35–45 °C. |
 
@@ -519,8 +621,10 @@ are on **Power and solar sensors**; mode / defrost / online / fault are on
 
 | Setting | Default | Range | What it means |
 |---|---|---|---|
-| Solar radiation sensor, source, location | from setup | — | See setup step 1. |
-| Heat pump power meter | none | a `power` sensor | Actual electrical draw. With it, efficiency becomes measurable, predicted cost gets a real counterpart, and a wood fire is detected reliably. Several sensors stay unavailable without it. |
+| Solar radiation sensor | the setup value | an irradiance sensor | As on [Optional sensors](#2--optional-sensors). |
+| Solar irradiance source | Weather entity | Weather entity / Open-Meteo | As on Optional sensors. |
+| Solar irradiance location | your Home Assistant home location | a coordinate | As on Optional sensors. Only used with Open-Meteo. |
+| Heat pump power meter | none | a `power` sensor | Actual electrical draw. A figure the pump estimates for itself is read the same way as a meter, so prefer a real one ([why](how-it-works.md#the-house-heat-loss-coefficient)). With it, efficiency becomes measurable, predicted cost gets a real counterpart, and a wood fire is detected reliably. Several sensors stay unavailable without it. |
 | Heat pump thermal power meter | none | a `power` sensor in W or kW | The heat the pump delivers, from a heat meter. Published as `measured_heat_output_kw` on the Recommended Power sensor. With the power meter, COP is measured (heat over electricity) rather than inferred from the commanded draw, and the efficiency scale is judged at the supply temperature the pump actually ran at when a supply sensor is mapped, so it stops absorbing weather-driven lift as wear. The house heat-loss and lower-floor learners replay the measured heat for a space-heating interval, and the capacity curve takes it at every load as a floor (it may raise a bucket; only near-nameplate intervals count towards capping). When set it replaces the water flow sensor's estimate, also in a cycle where its own reading is unusable, and an unusable reading pauses the learners that read it. |
 | Heat pump energy meter | none | an `energy` sensor | A cumulative kWh meter is more accurate than adding up power readings, which misses short runs. |
 | Heat pump heat energy meter | none | an `energy` sensor in Wh, kWh or MWh | A cumulative kWh meter of the heat the pump delivers. It is read over each span of about an hour, so short compressor runs count, and when set it is used instead of the thermal power meter and the water flow sensor. With the energy meter on the same read instants, efficiency is measured as heat over electricity for the span; the house heat-loss learner replays the heat that was delivered. A span whose counter went backwards (a meter reset), jumped past the pump's nameplate, or whose counter resolution is too coarse for the heat expected in it is not learned from. A meter that also counts hot water is split by the operating mode entity, by the time the pump spent in each mode; without that entity, or in a combined mode, the split falls back to the plan's, and an hour that heated the tank is not read as space heating. |
@@ -648,8 +752,8 @@ writes, at every 15-minute plan step:
   is still there is written back like any other difference.
 - **Its own mode is not a pump limit.** A mode the optimizer wrote does not
   stop the next plan from heating the house or making hot water, even when the
-  pump has not shown it yet or after a restart; one set by anybody else still
-  does, as before.
+  pump has not shown it yet or after a restart; one set by anybody else
+  does.
 
 **Observe** writes nothing. In *Observe* and *Control* the optimizer keeps a
 ledger of the last 24 hours: per 15-minute step, the duty the plan wanted
@@ -725,15 +829,22 @@ turning the preset on.
 
 ### Thermal model (expert)
 
-The seven raw single-zone numbers, otherwise only asked at setup. **A field
+The raw single-zone numbers, otherwise only asked at setup. **A field
 left empty keeps its current value and is never saved.** Buffer tank size
 lives on *Heating system and heat storage*; window area and the glazing
 coefficient live on *Building type and emitters*; the two-zone switch and
 the per-floor numbers live on **Two-zone model**.
 
-The seven fields are those from the expert setup page above, with the same
-ranges: house thermal mass, heat-loss coefficient, slab mass, slab-to-room
-transfer, nominal COP, max power, min power.
+| Setting | Default | Range | What it means |
+|---|---|---|---|
+| House thermal mass | the setup value | 0.5–80 kWh/°C | Heat stored per degree by the room air, furnishings and light fabric. |
+| Heat loss coefficient | the setup value | 0.01–1.0 kW/°C | Heat lost per degree of indoor-outdoor difference. |
+| Slab floor thermal mass | the setup value | 0.1–60 kWh/°C | Heat stored per degree by the slab or the radiator circuit. |
+| Slab-to-room heat transfer | the setup value | 0.02–5.0 kW/°C | How fast that store gives its heat to the room. |
+| Heat pump nominal COP | the setup value | 1.5–6.0 | Units of heat per unit of electricity under normal conditions. |
+| Heat pump max power | the setup value | 1–20 kW | Electrical input at full output. |
+| Heat pump min power | the setup value | 0–10 kW | The lowest input the pump can hold without cycling. |
+| Heat pump COP loss at max power | the setup value | 0–0.5 | The share of efficiency lost at max power rather than min power. See [the setup screen](#thermal-model--optimization) for the limit the page enforces. |
 
 **Changing a derived value turns the derivation off.** These fields are what
 *Building type and emitters* works out from the questionnaire. If that switch
@@ -754,12 +865,14 @@ warning; every other field keeps its normal limits.
 | Setting | Default | Range | What it means |
 |---|---|---|---|
 | Two-zone model | Automatic | Automatic · On · Off | *Automatic* means two-zone as soon as any zone value has ever been saved — which can only ever turn it on. **Off is the only way back to single-zone**, because values written during setup live where the options flow cannot erase them. *On* forces two-zone using the values below or their defaults. |
-| Upper / lower floor thermal mass | 3.0 / 8.0 kWh/°C | 0.25–60 | Heat stored in each zone. |
-| Upper / lower floor heat loss | 0.08 / 0.07 kW/°C | 0.001–1.0 | Each zone's own loss coefficient. |
+| Upper floor thermal mass | the setup value | 0.25–60 kWh/°C | Heat stored in the upper zone. |
+| Lower floor thermal mass | the setup value | 0.25–60 kWh/°C | Heat stored in the lower zone. |
+| Upper floor heat loss | the setup value | 0.001–1.0 kW/°C | The upper zone's own loss coefficient. |
+| Lower floor heat loss | the setup value | 0.001–1.0 kW/°C | The lower zone's own loss coefficient. |
 | Inter-zone heat transfer (kW/°C) | see setup | kW/°C | How fast heat moves between the two floors. |
 | Share of heat going to radiators | see setup | 0–1 | Share of heat delivered through radiators rather than the slab. |
-| Upper floor area ratio | see setup | 0.1–0.9 | Used to split solar gain. |
-| Solar orientation factor | 0.7 | 0.0–1.0 | How well the glazing faces the sun over a day. |
+| Upper floor area ratio | see setup | 0.1–0.9 | Splits the solar gain between the floors. |
+| Solar orientation factor | the setup value | 0.0–1.0 | How well the glazing faces the sun over a day. |
 
 ### Hot water tank and inlet
 
@@ -821,6 +934,7 @@ opt-in learners are on **Advanced learning features**.
 | Allow this much extra age | 1.0 | 0.5–10.0, 0.5 steps | Raise it if sensors that deliberately report rarely are being flagged. |
 | Learn my comfort preference from overrides | off | on/off | Every temperature override says the plan went too far one way. This adjusts the comfort weight from that, shows the result on its own sensor, and has a reset button. |
 | Allow a one-off measurement experiment | off | on/off | Lets the optimizer run a small deliberate heating step on a mild, cheap night to measure your house directly instead of inferring it over weeks. Kept too small to notice, and stopped if the temperature drifts. |
+| Collect a week of debug data | off | on/off | Records one small row per optimization cycle and one full snapshot a day for seven days, then stops by itself. Download diagnostics then carries the week for a bug report. The `debug_collect` service and the Learning Finalize Debug Collection button drive the same collection. |
 | Estimate prices past the published horizon | on | on/off | Tomorrow's prices arrive around 13:00. Until then this uses your learned daily price shape instead of a flat repeat, and the plan marks which hours are estimated. |
 
 ### Advanced learning features
diff --git a/docs/dashboard-card.md b/docs/dashboard-card.md
index e6552d388..f98c37ecb 100644
--- a/docs/dashboard-card.md
+++ b/docs/dashboard-card.md
@@ -105,8 +105,8 @@ figures come from `docs/img/card/make_card_figures.mjs` and the schematics furth
 down from `tests/setup_qa_render.mjs`, both run against a plan
 `tests/plan_view.py` solved. The two photographs further down — the weekly
 band and the Advisor page — are the shipped card itself, rendered in a
-headless browser against the same solved plan. Nothing here is a picture of
-how the card used to look.
+headless browser against the same solved plan. Every picture here is the card
+this release ships.
 
 ### The two kinds of dashed line
 
@@ -183,9 +183,9 @@ The card finds those sensors from the plan sensor it has already resolved: it
 takes that entity id's prefix and appends `_plan_predicted_savings`,
 `_plan_savings_percentage`, `_plan_optimization_score` and `_plan_narrative`. If you have
 renamed one individually, it falls back to scanning for any `sensor` whose id
-ends in the suffix it wants. An install upgraded across the #1227 key rename
-keeps its old registry ids, so the card tries each renamed sensor's pre-#1227
-suffix after the current one. The savings figure is labelled with the unit the
+ends in the suffix it wants. An install that kept older registry ids for these
+sensors is covered too: the card tries each sensor's older suffix after the
+current one. The savings figure is labelled with the unit the
 savings sensor itself declares — nothing here converts, so a `currency:` in the
 card config does not relabel it.
 
@@ -201,10 +201,10 @@ it costs the chart no axis width. Hovering gives its value in W/m².
 Hovering a planned slot shows why it was chosen: cheapest hours, holding the
 minimum temperature, pre-heating before colder weather, using solar surplus, the
 anti-legionella cycle, and so on — or simply keeping the house at target, which
-is what an ordinary slot says now that it no longer borrows the weather
-pre-heat label. Without this an unexpected slot is indistinguishable from a
+is what an ordinary slot says; it never borrows the weather pre-heat label. Without this an unexpected slot is indistinguishable from a
 bug.
 
+<!-- [target: R10-ARCH-SHAPES-CLASSIFIER] -->
 ### Why a step is idle
 
 <picture>
@@ -268,7 +268,7 @@ yourself and yours wins in every language.
 Prices are labelled with the first currency the card can find:
 
 1. `currency:` in the card config.
-2. The `currency` attribute the plan sensors publish (v4.1.0 and later).
+2. The `currency` attribute the plan sensors publish.
 3. Home Assistant's own configured currency.
 4. `SEK`, as a last resort.
 
@@ -332,9 +332,9 @@ A plain vertical scroll is deliberately left alone. The card sits in a dashboard
 people scroll, and a chart that swallowed the wheel would trap the page the
 moment the pointer crossed it.
 
-It is **forward-only over the plan**. There is no history of what the plan used
-to say to scroll back into: both plan sensors keep their `forecast` attribute
-out of the recorder, so nothing stores what the plan used to say. The window
+It is **forward-only over the plan**. There is no history of past plans to
+scroll back into: both plan sensors keep their `forecast` attribute out of the
+recorder, so nothing stores what an earlier plan said. The window
 therefore stays between now and the end of the plan, and zooming out stops at
 the plan's real extent rather than at the configured plot width — past the
 optimizer's horizon there is empty chart, not more plan. The reset button
@@ -365,7 +365,7 @@ rather than the whole span. If the recorder answers nothing — it is off, or
 the past was never recorded — the card says so in a notice above the chart
 and snaps the window back to now rather than show a past it has no evidence
 for. Panning back needs the recorder's history API, so a frontend without it
-keeps the forward-only pan exactly as before.
+keeps the forward-only pan.
 
 Zooming changes the axis the lanes are drawn against, not just their appearance,
 so dragging a slot keeps hitting the time under the pointer at any zoom level.
@@ -435,7 +435,7 @@ add a slot", or a slot's own start and end times. Tab to one and:
 Dragging has no keyboard form; add and remove cover the same edits in more
 steps. Every edit redraws the chart, which destroys the element that had focus,
 so focus is deliberately moved to the lane the edit happened in — the acted-on
-slot either no longer exists or has a new index — rather than being dropped
+slot either is gone or has a new index — rather than being dropped
 back at the top of the document. Escape puts it back on the slot the menu was
 opened from.
 
@@ -461,7 +461,7 @@ rather than silently.
 
 Each hot water window carries a day selector — *Every day*, *Weekdays* or
 *Weekend* — so a household whose mornings differ can say so from the card, in
-the grammar the integration's weekly windows use (v6.2.5). A schedule typed in
+the grammar the integration's weekly windows use. A schedule typed in
 the options flow with specific days (`Tu-Fr 06:00-08:00`) shows that day list
 as the row's own choice and is saved back unchanged. The editor pre-fills from
 the configured schedule the plan sensors publish as `dhw_windows_spec`, not
@@ -661,6 +661,7 @@ When every optional temperature sensor is already configured, that part of the
 page says exactly that; the integration publishes no ranking at all, and no
 empty table is drawn.
 
+<!-- [target: R10-UX-HEALTH] -->
 ## The health page
 
 The **Health** tab answers "is the plan running on good data?" in one screen,
@@ -942,12 +943,12 @@ series:                                  # optional, initial per-series visibili
 |----------------|---------|--------------------------------|-------------|
 | `type`         | string  | —                              | Must be `custom:heatpump-optimizer-card`. |
 | `title`        | string  | localized                      | Card header text. Left out, it is the built-in default for the frontend language (`Heat pump plan`, `Värmepumpsplan`). An explicit empty string renders no header text. |
-| `space_entity` | string  | auto-detected                  | Entity id of the space-heating plan sensor (its `forecast` attribute supplies `price`, `outdoor`, `space_power`, `room`, `upper`, `lower`). |
-| `dhw_entity`   | string  | auto-detected                  | Entity id of the DHW plan sensor (its `forecast` attribute supplies `dhw_power`, `dhw_temp`, the `dhw_temp_lo`/`dhw_temp_hi` expected-error band, and `price`/`outdoor` fallbacks). |
-| `solar_entity` | string  | auto-detected                  | Entity id of the solar irradiance sensor (its `forecast` attribute supplies `ghi`). |
+| `space_entity` | string  | `sensor.heat_pump_optimizer_plan_space_heating`, else auto-detected | Entity id of the space-heating plan sensor (its `forecast` attribute supplies `price`, `outdoor`, `space_power`, `room`, `upper`, `lower`). |
+| `dhw_entity`   | string  | `sensor.heat_pump_optimizer_plan_dhw_heating`, else auto-detected | Entity id of the DHW plan sensor (its `forecast` attribute supplies `dhw_power`, `dhw_temp`, the `dhw_temp_lo`/`dhw_temp_hi` expected-error band, and `price`/`outdoor` fallbacks). |
+| `solar_entity` | string  | `sensor.heat_pump_optimizer_solar_irradiance`, else auto-detected | Entity id of the solar irradiance sensor (its `forecast` attribute supplies `ghi`). |
 | `hours`        | number  | `24`                           | How many hours forward to plot. Must be from `1` to `168`: the visual editor's box steps whole hours from that same floor, and a YAML value below or above the range is refused rather than plotted. |
 | `what_if`      | boolean | `true`                         | Show the slot lanes and schedule editor in the enlarged view. Editing is local to the card; only the Simulate, Save and Apply buttons reach Home Assistant. |
-| `currency`     | string  | plan sensor's, else HA's, else `SEK` | Unit shown on the price axis and cost figures. The card first uses the currency the integration publishes on the plan sensors (v4.1.0+), then Home Assistant's configured currency, then `SEK`. Only override this if your price feed disagrees with all of them. It relabels rather than converts, and it does not relabel a savings figure: the headline and the savings page keep the unit their own sensor declares. |
+| `currency`     | string  | plan sensor's, else HA's, else `SEK` | Unit shown on the price axis and cost figures. The card first uses the currency the integration publishes on the plan sensors, then Home Assistant's configured currency, then `SEK`. Only override this if your price feed disagrees with all of them. It relabels rather than converts, and it does not relabel a savings figure: the headline and the savings page keep the unit their own sensor declares. |
 | `show_stats`   | boolean | `true`                         | Show the headline row (projected savings, optimization score, plan narrative) under the card header. It hides itself, entirely, when the backend publishes none of those sensors. |
 | `series`       | map     | all `true`                     | Initial visibility per series key. Keys: `price`, `dhw_slots`, `space_slots`, `actioned`, `quiet_silent`, `quiet_off`, `outdoor`, `dhw_temp`, `house_temp`, `solar`. |
 
@@ -981,9 +982,9 @@ reloads. The key is the space and hot-water entity ids the config carries (the
 defaults, when you have not set them) plus the card's `title` and `hours` — its
 config identity, not just its data sources — so a 24-hour card on a wall panel
 and a 48-hour card of the same sensors elsewhere keep their own toggles instead
-of overwriting each other. Cards saved before v4.2.0 used a key of the
-entity ids alone; that key is still read once as a fallback, so an upgrade does
-not silently reset every toggle. Writes always go to the new key.
+of overwriting each other. A card whose toggles were saved under a key of the
+entity ids alone has that key read once as a fallback, so its toggles are kept.
+Writes always go to the full key.
 
 The `series` option only sets the *initial* visibility the first time the card
 is shown.
diff --git a/docs/ecl110.md b/docs/ecl110.md
index da1e1c49d..eeea97148 100644
--- a/docs/ecl110.md
+++ b/docs/ecl110.md
@@ -89,8 +89,8 @@ that stored the previous default strings keep publishing to them.
 ## Options
 
 All eight settings live on the options page **Heat curve control (ECL110)**,
-under *Advanced settings*. Since v4.1.0 they no longer appear during initial
-setup, because only ECL110 owners can answer them; installs that never open the
+under *Advanced settings*. They are not asked during initial setup, because
+only ECL110 owners can answer them; installs that never open the
 page run no ECL110 surface at all — the topic options below suggest empty and
 a topic only exists once you store one.
 
diff --git a/docs/how-it-works.md b/docs/how-it-works.md
index a87af50d5..2f65b750b 100644
--- a/docs/how-it-works.md
+++ b/docs/how-it-works.md
@@ -142,20 +142,19 @@ nothing and the electricity saved is worth real money. The linear term gives
 the penalty a non-zero slope at the boundary and pins the trajectory to the
 floor instead.
 
-**The pull toward the target is deliberately weak.** It was halved in v3.9.0
-after measuring what the old strength cost: on the winter scenario the plan
-spent 28.55 SEK instead of 23.28 — 18% of the bill — buying an average 0.32 K
-of extra warmth while never coming near the floor. Below half the saving
-plateaus, so the current value is where the money stops improving and a real
-preference is still expressed.
+**The pull toward the target is deliberately weak.** Twice the strength, on the
+winter scenario, makes the plan spend 28.55 SEK instead of 23.28 — 18% of the
+bill — buying an average 0.32 K of extra warmth while never coming near the
+floor. Below the chosen strength the saving plateaus, so it sits where the
+money stops improving and a real preference is still expressed.
 
 **Money terms scale with `price_weight` together.** If the energy cost scaled
 and the cycling and capacity terms did not, a non-default price weight would
 silently re-price compressor starts and grid peaks against the electricity they
 trade off.
 
-**One term was removed.** Until v3.9.0 the objective carried a `0.01 · Σ ΔP²`
-smoothness regulariser, priced in invented units and costing about 5% of the
+**There is no smoothness term.** A `0.01 · Σ ΔP²` smoothness regulariser
+would be priced in invented units, and measured, it costs about 5% of the
 two-zone winter bill for no reduction in compressor starts. Discouraging
 chatter is the cycling cost's job, and that is denominated in currency per
 start-stop cycle.
@@ -348,24 +347,15 @@ whole plan rests on.
 
 ### Knowing the lower floor rather than guessing it
 
-Two-zone mode plans against two room temperatures, but historically only the
-upper one had a sensor. The lower zone was inferred from the floor return water
-as `T_return + 0.5 °C` — a *water* temperature standing in for an *air*
-temperature. A floor loop returns at roughly 24–30 °C while the room it serves
-sits near 21, so the model believed the lower floor was several degrees warmer
-than it was. Judged against the same comfort band as the upper floor, the zone
-read as permanently overshooting and the optimizer under-heated the one room it
-could not see. Worse, the slab was derived from the *same* sensor as
-`T_return + 1 °C`, so slab-minus-room was always exactly 0.5 K whatever the
-sensor read — pinning the main heat path into the lower zone at a constant.
-
-That estimate is gone (v5.1.7). It was also what the plan chart drew as the
-house temperature: a 27.5 °C floor return put a "house" trace at 28.0 °C on the
-chart while the measured zone sat at 22.1, which reads as the optimizer cooking
-the house to a temperature no plan ever chose. The floor return keeps the job it
-is genuinely a proxy for — the slab estimate above — and the lower zone now
-starts from the room sensor and is carried forward by the model's own dynamics.
-That is open-loop: nothing corrects it, so it can drift from the real downstairs
+Two-zone mode plans against two room temperatures, and often only the upper
+one has a sensor. The floor return water is not used for the lower zone: a
+floor loop returns at roughly 24–30 °C while the room it serves sits near 21,
+so a *water* temperature standing in for an *air* temperature would make the
+lower floor read several degrees too warm, permanently overshooting its comfort
+band, and the optimizer would under-heat the one room it cannot see. The floor
+return keeps the job it is genuinely a proxy for — the slab estimate above —
+and the lower zone starts from the room sensor and is carried forward by the
+model's own dynamics. That is open-loop: nothing corrects it, so it can drift from the real downstairs
 over a long cold spell, and a repair notice says so rather than letting a
 modelled number pass for a measured one. The chart labels the trace
 "Lower floor (modelled)" until a thermometer is assigned.
@@ -425,7 +415,7 @@ its ceiling, so the *building* charges first — and building storage is free,
 because the heat sits at room temperature. Only then does the valve throttle and
 the tank take the surplus, which is stored hot and does cost efficiency.
 Building first, tank second, is the cheap order. The cost of that choice is that
-the valve no longer prevents the house overheating — the optimizer's comfort
+the valve does not prevent the house overheating — the optimizer's comfort
 limits do.
 
 **Storing hot is not free.** A heat pump loses efficiency the hotter it must
@@ -579,9 +569,8 @@ does not shrink because the tank happens to be cold.
 
 With the scaled draw, the inlet floor underneath is a genuine no-op safety
 bound, and any heat it does have to fabricate is booked rather than silently
-created. The default inlet reference is 10.0 °C — the value the two previously
-hard-coded cold-water temperatures used, so every existing install's ready
-targets sit exactly where they did.
+created. The default inlet reference is 10.0 °C; set *Cold water inlet
+temperature* on **Hot water tank and inlet** if you have measured yours.
 
 ### Self-learning tank cooling
 
@@ -648,8 +637,8 @@ Everything here is inert until configured or until evidence exists:
 - **Heavy-day targets** (opt-in): the integration learns how much hot water each
   frame actually draws — whole occurrences, weekdays and weekends separately —
   and readies the tank for the 90th-percentile day of *that* frame rather than
-  the average. The blend ramps with evidence, so a fresh install answers exactly
-  as before and one early outlier cannot yank the target. It needs *configured*
+  the average. The blend ramps with evidence, so a fresh install answers with
+  the average and one early outlier cannot yank the target. It needs *configured*
   frames: with learned-profile frames there is no stable frame to attach
   statistics to. Watch **DHW Heavy Day Demand** (disabled by default; it needs
   weeks of data).
@@ -720,11 +709,11 @@ the same as "no sun".
 ### Past the published horizon
 
 Nord Pool and Tibber publish tomorrow's prices around 13:00, so before then a
-large part of the horizon has no data. That gap used to be filled by repeating
-the last known price — and a flat tail has no trough, so the optimizer could not
-see a cheap period ahead worth waiting for and systematically under-deferred
-load in the morning, precisely when deferral is most valuable. It also fed the
-terminal cost a price that was entirely fictitious.
+large part of the horizon has no data. Repeating the last known price there
+would give a flat tail with no trough, so the optimizer could not see a cheap
+period ahead worth waiting for and would under-defer load in the morning,
+precisely when deferral is most valuable, and the terminal cost would be fed a
+fictitious price.
 
 Instead, a normalised daily price *shape* is learned from the prices actually
 seen, split weekday/weekend (the morning peak is later and shallower at the
@@ -891,9 +880,9 @@ model simulates two tanks side by side: a burn charges the *wood* tank, the
 4-way valve draws wood-first while the wood side can meet the flow temperature
 and shifts to the heat-pump tank as it depletes, and the blend law is the same
 one the outlet sensor measures, so model and measurement cannot disagree. The
-point of the split is that a fire can no longer make the heat pump's modelled
-efficiency look worse — the old single-tank abstraction charged the modelled COP
-for water the pump never made — and can no longer eat the buffer's
+point of the split is that a fire cannot make the heat pump's modelled
+efficiency look worse — a single-tank model would charge the modelled COP
+for water the pump never made — and cannot eat the buffer's
 safe-temperature headroom, so the plan keeps charging cheap hours right through
 a burn. Heat still in the wood tank at day's end counts in the savings
 settlement and the thermal-battery view, up to 95 °C. Without the probe, or if
@@ -962,7 +951,7 @@ the learners paused. It is on by default, because it protects everything else
 and costs nothing. Learning also freezes while an external heat source is active
 and while the open-window detector is tripped.
 
-**The heat pump's own signals (v5.3.0).** Four optional slots read the pump
+**The heat pump's own signals.** Four optional slots read the pump
 itself: operating mode, defrosting, online status and fault alarm. Three of
 them freeze the learners, and they freeze on a *value* rather than on a missing
 reading, which is a different shape from everything above:
@@ -1030,6 +1019,28 @@ day biases it up, so a lower envelope would be systematically wrong. It uses a
 slow symmetric average instead, with a per-interval rate limit and a residual
 cutoff so a single anomaly cannot move the model far.
 
+**What it replays.** The heat an interval put into the house comes from the
+best evidence the install has. With a heat meter — a heat energy meter or a
+thermal power meter — it is the heat the pump delivered. Without one, a heat pump
+power meter gives the measured electrical draw, turned into heat through the
+modelled COP; without that, it is the power the plan commanded. Gaining better
+evidence (adding a power meter, or a heat meter's first measured interval)
+discards the evidence gathered on the weaker one.
+
+**An estimated power reading.** The integration cannot tell a revenue meter
+from a power figure the heat pump computes for itself: both are read as the
+measured draw. If yours is an estimate and it reads high, the house looks
+leakier by about the same factor, and the plan buys heat it does not need.
+Prefer a real meter, and reset the learners after changing the slot.
+
+**Starting again.** The **Learning Reset Heat Loss** button and the
+`reset_heat_loss_learners` service return the learned scale and the lower
+floor loss ratio to 1.0, so the plan uses the heat loss values in the settings
+and learning starts again from there. Changing the indoor or the lower floor
+temperature sensor resets the learner fitted on it the same way, because
+evidence fitted against one sensor says nothing about another.
+
+<!-- [target: R10-COP-GATE, R10-COP-PARTLOAD] -->
 ### COP, and the tracking-error gate
 
 With a power meter, COP becomes observable instead of derived from a nameplate
@@ -1046,7 +1057,7 @@ twice. Without a defrost sensor there is no way to tell which intervals those
 are, so the exclusion has to cover the whole 0–5 °C frosting band — which in a
 Swedish shoulder season is a large share of all heating hours, leaving the one
 multiplier every priced plan runs through blind in the conditions it spends most
-of its life in. With a defrost flag configured (v5.3.0) the exclusion narrows to
+of its life in. With a defrost flag configured the exclusion narrows to
 the intervals that **actually contained a defrost**, and the rest of the band
 teaches `cop_scale` normally. The attribution stays disjoint, just at a far
 finer grain.
@@ -1066,7 +1077,7 @@ Two caveats are worth stating plainly:
   number of defrosts actually witnessed per bucket alongside the duty, so a
   coarse estimate can be recognised as one.
 * **Without a flag** the derate falls back to inferring the shortfall from the
-  commanded-versus-measured power ratio, exactly as before v5.3.0. That
+  commanded-versus-measured power ratio. That
   estimator cannot see a defrost at all — during one the compressor draws
   roughly normal power while delivering almost no heat, which reads as a
   perfectly performing unit — and its error is biased optimistic, because the
@@ -1103,6 +1114,7 @@ by itself makes 1.0 the only fixed point and drags a perfectly-confirmed model
 back toward "trust the nameplate". The same vetted sample feeds the compressor
 health watch and the capacity envelope, so both inherit every filter for free.
 
+<!-- [target: R10-CEILING-PROBE] -->
 ### Active system identification
 
 Optional, and the fastest way to a good model. On a mild, cheap night the
@@ -1142,8 +1154,8 @@ handing the collinear intercept the noise.
 
 Guards on the result: fitted gains outside −0.5 to 2.0 kW mean the "constant"
 was a drifting contaminant (sun through a window, a door left open), and the
-triple is **rejected rather than clipped** — a clipped intercept no longer
-satisfies the regression it came from, so the other coefficients would carry its
+triple is **rejected rather than clipped** — a clipped intercept would not
+satisfy the regression it came from, so the other coefficients would carry its
 bias. Time constant must land in 0.1–200 h and the loss coefficient in
 0.01–5 kW/°C. Confidence comes from the fit's R², tempered by sample count and
 by the achieved temperature excursion, because R² cannot see that a flat fit
@@ -1236,9 +1248,8 @@ anti-legionella cycle, and so on — in the plan sensor attributes and in the
 card's tooltip. Without it, an unexpected slot is indistinguishable from a
 bug, which makes the optimizer hard to trust and bug reports much weaker than
 they could be. A step that is none of those is `scheduled`, "keeping the
-house at target": until v5.1.7 the fall-through was `preheat_weather`, so an
-ordinary mid-price hour claimed to be anticipating weather nobody had
-forecast. Everything below is built on those codes:
+house at target", so an ordinary mid-price hour never claims to be
+anticipating weather nobody has forecast. Everything below is built on those codes:
 
 | Where to look | What it explains |
 |---|---|
diff --git a/docs/setup.md b/docs/setup.md
index 9488a4150..0d22cbfe7 100644
--- a/docs/setup.md
+++ b/docs/setup.md
@@ -2,9 +2,8 @@
 
 Every screen Home Assistant shows when you add the Heat Pump Cost Optimizer,
 in the order you meet it, with a picture of each. Quick setup — the
-recommended route since v6.6.5 — collapses the original eleven-page wizard to
-one page of questions plus an automatic read of the heat pump's own entities;
-the full wizard is still there one menu entry later, and everything either
+recommended route — asks one page of questions plus an automatic read of the
+heat pump's own entities; the full wizard is one menu entry later, and everything either
 path sets can be refined afterwards in Options.
 
 This page is the journey. For what every field *means* — defaults, ranges,
@@ -126,7 +125,7 @@ with three answers:
 
 Two things worth knowing about this menu:
 
-- **It belongs to adding a new entry — and, since #1258, to changing one.**
+- **It belongs to adding a new entry, and Quick setup also to changing one.**
   The menu itself appears only while setting the integration up, but the
   Quick setup questions are also reachable afterwards: open the integration
   and choose **Configure**, where **Quick setup** is the last entry on the
@@ -136,10 +135,8 @@ Two things worth knowing about this menu:
   submit without changing anything and nothing is written. The device
   pre-fill is not offered there, because an existing entry's entity slots
   are already answered — that read stays on the **Pre-fill from a heat
-  pump device** page. **Reconfigure** still reopens only the first
+  pump device** page. **Reconfigure** reopens only the first
   screen and saves back onto the same entry.
-- **Quick setup arrived in v6.6.5.** An install set up on an earlier version
-  never saw the menu; its entries are complete all the same.
 
 ## Quick setup (recommended)
 
diff --git a/tests/doc_claims.py b/tests/doc_claims.py
index 377f2edf2..0b2f95cff 100644
--- a/tests/doc_claims.py
+++ b/tests/doc_claims.py
@@ -1957,7 +1957,11 @@ def entity_census(extra: dict) -> list[dict]:
             out.append({
                 "platform": str(plat),
                 "name": names.get(str(plat), {}).get(key, {}).get("name", f"<{plat}:{key}>"),
-                "enabled": getattr(e, "entity_registry_enabled_default", True),
+                # The stub has no entity_registry_enabled_default property, so a class declaring only
+                # _attr_entity_registry_enabled_default read as enabled here; upstream's property returns that
+                # attribute. Same two-path rule as tests/entities.py registry_default.
+                "enabled": bool(getattr(e, "entity_registry_enabled_default",
+                                        getattr(e, "_attr_entity_registry_enabled_default", True))),
                 "options": set(getattr(e, "_attr_options", None) or ()) - {"unknown"},
             })
     return out
@@ -3019,6 +3023,10 @@ def check_image_dimensions() -> None:
 # R10-ARCH-DOCS's end-of-round check, not this one.
 
 WIRING_DOCS = ("docs/architecture.md", "README.md", "dev/README.md")
+# The user pages R10-USER-DOCS-FINAL drafts and R10-USER-DOCS-VERIFY re-checks. README.md is in both sets.
+USER_PAGES = ("README.md", "docs/setup.md", "docs/configuration.md", "docs/how-it-works.md", "docs/automations.md",
+              "docs/dashboard-card.md", "docs/ecl110.md")
+_COMMENT = re.compile(r"<!--.*?-->", re.S)
 # (e) reads every reader doc that draws a mermaid block, plus the onboarding.
 MERMAID_STYLE_DOCS = ("README.md", "docs/architecture.md", "docs/how-it-works.md", "docs/configuration.md",
                       "docs/setup.md", "dev/README.md")
@@ -3038,9 +3046,21 @@ def roster_stages(path: pathlib.Path = ROSTER) -> dict[str, str] | None:
     return {g["group"]: (g.get("resume") or {}).get("stage", "") for g in json.loads(path.read_text())["groups"]}
 
 
+def _in_comment(text: str, pos: int) -> bool:
+    """Whether `pos` lies inside an HTML comment. A marker wrapped in one is a user-doc marker, R10-USER-DOCS-VERIFY's
+    to resolve; a bare one is a wiring marker, R10-ARCH-DOCS's (design/R10-USER-DOCS-FINAL section 3: the wrapper is
+    the tag)."""
+    return any(m.start() < pos < m.end() for m in _COMMENT.finditer(text))
+
+
+def _wiring(text: str) -> list[re.Match]:
+    """The well-formed wiring markers in `text`: a user-doc marker excuses no wiring finding (udf-user-marker-path-mask)."""
+    return [m for m in _MARKER.finditer(text) if not _in_comment(text, m.start())]
+
+
 def _groups(text: str, kind: str = "target") -> list[str]:
-    """The roster groups every well-formed marker of `kind` in `text` names."""
-    return [g for m in _MARKER.finditer(text) if m.group(1) == kind for g in m.group(2).split(", ")]
+    """The roster groups every well-formed wiring marker of `kind` in `text` names."""
+    return [g for m in _wiring(text) if m.group(1) == kind for g in m.group(2).split(", ")]
 
 
 def _units(text: str) -> list[tuple[str, list[str]]]:
@@ -3149,9 +3169,9 @@ def doc_wiring_findings(docs: dict[str, str], tree: set[str], roster, style_docs
                 out.append(f"{name}: a retired-by marker names one group and no owner step: {m.group(0)!r}")
             else:
                 groups += [(name, g.group(1), x) for x in g.group(2).split(", ")]
-        # (a) every backticked repository path resolves, or its unit carries a marker
+        # (a) every backticked repository path resolves, or its unit carries a wiring marker
         for unit, covered in _units(text):
-            marked = covered or bool(_MARKER.search(unit))
+            marked = covered or bool(_wiring(unit))
             for span in re.findall(r"`([^`\n]+)`", unit):
                 for tok in span.split():
                     tok = re.sub(r":\d+(?:-\d+)?$", "", tok)
@@ -3180,7 +3200,7 @@ def doc_wiring_findings(docs: dict[str, str], tree: set[str], roster, style_docs
             out += [f"{name}: [{kind}: {g}] names no group in the roster" for name, kind, g in groups if g not in stages]
             # (c) report-only: resolving is R10-ARCH-DOCS's end-of-round predicate
             notes += [f"{r['doc']}:{r['line']}: {r['marker']} names only done groups; R10-ARCH-DOCS resolves it"
-                      for r in marker_census(docs, stages) if r["due"]]
+                      for r in marker_census(docs, stages) if r["due"] and r["scope"] == "wiring"]
     # (e) no hex colour and no init directive inside a mermaid block
     for name, text in {**(style_docs or {}), **docs}.items():
         for info, body in _FENCE.findall(text):
@@ -3195,17 +3215,37 @@ def doc_wiring_findings(docs: dict[str, str], tree: set[str], roster, style_docs
 def marker_census(docs: dict[str, str], stages: dict[str, str]) -> list[dict]:
     """Every marker in the documents, in order, with each named group's roster stage (`absent` when the roster has
     no such group). `due`: every group it names is done, so the marker is unresolved (R10-ARCH-DOCS-WIRING item 2).
-    A marker quoted in inline code is the grammar being described, not a marker."""
+    `scope`: `user` for a marker inside an HTML comment, else `wiring` (`_in_comment`). A marker quoted in inline code
+    is the grammar being described, not a marker."""
     rows = []
     for name, text in docs.items():
         bare = re.sub(r"`[^`\n]+`", lambda m: " " * len(m.group(0)), text)
         for m in _MARKER.finditer(bare):
             st = {g: stages.get(g, "absent") for g in m.group(2).split(", ")}
             rows.append({"doc": name, "line": bare.count("\n", 0, m.start()) + 1, "marker": m.group(0),
-                         "stages": st, "due": all(v == "done" for v in st.values())})
+                         "stages": st, "due": all(v == "done" for v in st.values()),
+                         "scope": "user" if _in_comment(bare, m.start()) else "wiring"})
     return rows
 
 
+def marker_docs(root: pathlib.Path = ROOT) -> dict[str, str]:
+    """The one dict the marker census reads: the wiring documents and the user pages, keyed by path, so README.md,
+    which is both, is read once and its markers counted once."""
+    return {p: (root / p).read_text() for p in dict.fromkeys(WIRING_DOCS + USER_PAGES) if (root / p).is_file()}
+
+
+def marker_placement_findings(rows: list[dict]) -> list[str]:
+    """A marker on the wrong page for its scope: a bare one on a user-only page renders as text, and a wrapped one
+    on a wiring-only page has no owner there. A user marker naming no roster group is refused as a wiring one is."""
+    out = [f"{r['doc']}:{r['line']}: bare marker {r['marker']} on a user page renders; wrap it in <!-- -->"
+           for r in rows if r["scope"] == "wiring" and r["doc"] in USER_PAGES and r["doc"] not in WIRING_DOCS]
+    out += [f"{r['doc']}:{r['line']}: user-doc marker {r['marker']} on a wiring page; leave it bare"
+            for r in rows if r["scope"] == "user" and r["doc"] in WIRING_DOCS and r["doc"] not in USER_PAGES]
+    out += [f"{r['doc']}:{r['line']}: {r['marker']} names no group in the roster" for r in rows
+            if r["scope"] == "user" and "absent" in r["stages"].values()]
+    return out
+
+
 # (f)-(i): what the architecture page and the onboarding name beyond a path -- a command's arguments, a module's
 # symbols, a workflow job, a ledger kind, a diagram node -- each resolved in the artifact that defines it (fixer.md
 # step 11), never in a list kept here. Read from these two only: README.md names the user's own files
@@ -3531,6 +3571,13 @@ def check_doc_wiring() -> None:
             repr((got, gn, calls)))
     got, _ = doc_wiring_findings({"d.md": base}, t, lambda: None)
     R.check("a marker with no roster file to resolve it is a finding", any("no roster" in g for g in got), repr(got))
+    # udf-user-marker-path-mask: a user-doc marker on a README unit excuses no missing path there; a wiring one does.
+    user = "# T\n\n- `docs/gone.md` documents it <!-- [target: R10-A] -->\n"
+    got, gn = doc_wiring_findings({"README.md": user}, t, ro)
+    R.check("red fixture: a user-doc marker beside a missing path leaves the path a finding, and adds no due note",
+            any("`docs/gone.md` is not in the tree" in g for g in got) and not gn, repr((got, gn)))
+    got, _ = doc_wiring_findings({"README.md": user.replace("<!-- [target: R10-A] -->", "[target: R10-A]")}, t, ro)
+    R.check("null control: the same unit with a bare wiring marker excuses the path", not got, repr(got))
 
 
 def _read_tracked(tree: set[str]):
@@ -3595,13 +3642,27 @@ def check_named_elements() -> None:
 
 def check_marker_census() -> None:
     R.section("target-marker resolver: every marker with its group's roster stage (R10-ARCH-DOCS-WIRING item 2)")
-    docs = {p: (ROOT / p).read_text() for p in WIRING_DOCS if (ROOT / p).is_file()}
+    docs = marker_docs()
     stages = roster_stages()
     rows = marker_census(docs, stages or {})
-    R.check("the resolver reads every marker arm W reads (anchor)",
-            len(rows) == sum(len(_MARKER.findall(re.sub(r"`[^`\n]+`", "", t))) for t in docs.values()) > 0, str(len(rows)))
-    print(f"       ({sum(r['due'] for r in rows)} of {len(rows)} marker(s) name only done groups: "
-          "python3 tests/doc_claims.py --markers lists them)")
+    R.check("the resolver reads every marker in the wiring documents and the user pages, README.md once (anchor)",
+            len(rows) == sum(len(_MARKER.findall(re.sub(r"`[^`\n]+`", "", t))) for t in docs.values()) > 0
+            and set(docs) == set(WIRING_DOCS) | set(USER_PAGES), str(len(rows)))
+    wiring = [r for r in rows if r["scope"] == "wiring"]
+    print(f"       ({sum(r['due'] for r in wiring)} of {len(wiring)} wiring marker(s) name only done groups: "
+          "python3 tests/doc_claims.py --markers lists them; "
+          f"{len(rows) - len(wiring)} user-doc marker(s): --markers --user)")
+    bad = marker_placement_findings(rows) if stages is not None else []
+    R.check("every marker sits on a page of its scope and names a roster group", not bad, "; ".join(bad[:4]))
+    readme = "# T\n\n- `a.py` lands [target: R10-A]\n\n| Row | Cell <!-- [target: R10-B] --> |\n"
+    tagged = marker_census({"README.md": readme}, {"R10-A": "not-started", "R10-B": "done"})
+    R.check("null control: a README with one wiring and one wrapped marker gives one row of each scope",
+            [r["scope"] for r in tagged] == ["wiring", "user"], repr(tagged))
+    for page, doc, key in (("docs/setup.md", "# T\n\nA screen. [target: R10-A]\n", "renders"),
+                           ("docs/architecture.md", "# T\n\nA module. <!-- [target: R10-A] -->\n", "wiring page")):
+        got = marker_placement_findings(marker_census({page: doc}, {"R10-A": "not-started"}))
+        R.check(f"red fixture: {'a bare' if key == 'renders' else 'a wrapped'} marker in {page} is misplaced",
+                any(key in g for g in got), repr(got))
     stub = {"R10-A": "not-started", "R10-B": "done"}
     doc = "# T\n\n- `a.py` lands [target: R10-A]\n- quoted: `[target: R10-B]`\n"
     null = marker_census({"d.md": doc}, stub)
@@ -3615,17 +3676,26 @@ def check_marker_census() -> None:
 
 
 def print_marker_census(argv: list[str]) -> int:
-    """`--markers [--roster FILE]`: every marker, its groups' stages, and what each due one still leaves unresolved.
-    Exit 1 while any marker is due. FILE defaults to this tree's roster; the live one is on handoff/audit-r10-roster."""
+    """`--markers [--roster FILE]`: every wiring marker, its groups' stages, and what each due one still leaves
+    unresolved; exit 1 while any is due. `--markers --user`: only the comment-wrapped user-doc markers, ending
+    `N user-doc marker(s), M due`; exit 1 while N > 0 (R10-USER-DOCS-VERIFY's end condition is `0 ..., 0 due`).
+    FILE defaults to this tree's roster; the live one is on handoff/audit-r10-roster."""
     roster = pathlib.Path(argv[argv.index("--roster") + 1]) if "--roster" in argv else ROSTER
     stages = roster_stages(roster)
     if stages is None:
         print(f"no roster at {roster}")
         return 2
+    if "--user" in argv:
+        rows = [r for r in marker_census(marker_docs(), stages) if r["scope"] == "user"]
+        for r in rows:
+            print(f"{'DUE ' if r['due'] else '    '}{r['doc']}:{r['line']} {r['marker']} "
+                  + ", ".join(f"{g}={v}" for g, v in r["stages"].items()))
+        print(f"{len(rows)} user-doc marker(s), {sum(r['due'] for r in rows)} due")
+        return 1 if rows else 0
     docs = {p: (ROOT / p).read_text() for p in WIRING_DOCS if (ROOT / p).is_file()}
     tree = _tracked()
     _, pending, _ = named_element_findings(docs, tree, _read_tracked(tree))
-    rows = marker_census(docs, stages)
+    rows = [r for r in marker_census(docs, stages) if r["scope"] == "wiring"]
     for r in rows:
         print(f"{'DUE ' if r['due'] else '    '}{r['doc']}:{r['line']} {r['marker']} "
               + ", ".join(f"{g}={v}" for g, v in r["stages"].items()))
@@ -3854,6 +3924,466 @@ def check_readme_marketplace() -> None:
             not [g for g in readme_figure_findings(edited, regen, sha_of) if "its text differs" in g])
 
 
+# ---------------------------------------------------------------------------
+# R10-USER-DOCS-FINAL: every user-facing surface the tree exposes, and the one place in the user docs that describes
+# it (its home). The page map, the enumeration rule and the claim-check method are the group's design note,
+# dev/programme/designs/R10-USER-DOCS-FINAL.md; R10-USER-DOCS-VERIFY reruns `--surfaces --against` and
+# `--markers --user` at its own base. Each class's source is read from the tree, never from a list kept here.
+# ---------------------------------------------------------------------------
+
+# One class's home: (page, the heading its home sits under, or None for the whole page).
+_HOMES = {
+    "entity": ("README.md", "## Entities"),
+    "service": ("docs/configuration.md", "## Services"),
+    "setup_step": ("docs/setup.md", None),
+    "setup_field": ("docs/configuration.md", "## Initial setup"),
+    "option_page": ("docs/configuration.md", "## Changing settings later"),
+    "option": ("docs/configuration.md", "## Changing settings later"),
+    "blueprint": ("docs/automations.md", "## Blueprints"),
+    "event": ("docs/automations.md", "## Events"),
+    "card_view": ("docs/dashboard-card.md", None),
+    "card_option": ("docs/dashboard-card.md", "## Configuration options"),
+    "repair": ("README.md", "## Troubleshooting"),
+}
+# (class, id) -> why the surface needs no home of its own. Two or more words each; an id no longer enumerated is red.
+SURFACE_EXEMPT = {
+    ("option", "building_preset[questionnaire]"): "a block the questionnaire builds at render time; its fields are "
+    "the Describe your building questions, whose home is the setup screen of that name",
+}
+_NONE = "<none>"
+_COMPUTED = "<computed>"
+
+
+def _under(text: str, heading: str | None) -> str:
+    """The text below the first heading whose line starts with `heading`, up to the next heading at its level or
+    above; the whole text outside fences when `heading` is None. Fenced blocks are dropped first, so a `#` comment
+    in a YAML example is not a heading."""
+    lines = _FENCE.sub("", text).splitlines()
+    if heading is None:
+        return "\n".join(lines)
+    level, out = heading.split()[0].count("#"), None
+    for line in lines:
+        h = re.match(r"(#+)\s", line)
+        if out is not None:
+            if h and len(h.group(1)) <= level:
+                break
+            out.append(line)
+        elif h and len(h.group(1)) == level and line.startswith(heading):
+            out = []
+    return "\n".join(out or [])
+
+
+def _table_rows(text: str) -> list[tuple[str, list[str], list[str]]]:
+    """(nearest heading above, header cells, body cells) for every GFM table row, read after HTML comments are
+    stripped, so a marker at the end of a last cell is never part of a cell (design section 3, Placement)."""
+    rows, hdr, head = [], None, ""
+    for line in _COMMENT.sub("", text).splitlines():
+        h = re.match(r"#+\s+(.*)", line)
+        if h:
+            head, hdr = h.group(1).strip(), None
+        elif line.lstrip().startswith("|"):
+            cells = [c.strip() for c in line.strip().strip("|").split("|")]
+            if hdr is None:
+                hdr = cells
+            elif not set(line.strip()) <= set("|-: "):
+                rows.append((head, hdr, cells))
+        else:
+            hdr = None
+    return rows
+
+
+def _plain(s: str) -> str:
+    """A label as a reader compares it: `_label`, then only letters, digits and single spaces."""
+    return " ".join(re.sub(r"[^a-z0-9]+", " ", _label(s)).split())
+
+
+def _js_literal(src: str) -> object:
+    src = src.strip().rstrip(",")
+    return json.loads(src) if re.fullmatch(r'"[^"]*"|-?\d+(?:\.\d+)?|true|false|null', src) else _COMPUTED
+
+
+def surface_sources(services: dict | None = None) -> list[dict]:
+    """Every surface the tree exposes: (class, id, label, value). `value` is the shipped default where the class has
+    one -- a literal, `_COMPUTED` for one derived at run time, `_NONE` for none -- and is otherwise ignored.
+    `services` replaces the parsed services.yaml (the coverage arm's red fixture plants one there)."""
+    import asyncio
+
+    import yaml
+
+    from harness import FakeHass
+    from heatpump_optimizer import config_flow, const
+
+    out: list[dict] = []
+
+    def add(cls: str, id_: str, label: str, value: object = _NONE, under: str = "") -> None:
+        out.append({"class": cls, "id": id_, "label": label, "value": value, "under": under})
+
+    for e in entity_census({const.CONF_DHW_TANK_VOLUME: 200.0}):
+        add("entity", f"{e['platform']}.{e['name']}", e["name"], "enabled" if e["enabled"] else "disabled")
+    if services is None:
+        services = yaml.safe_load((PKG / "services.yaml").read_text())
+    for name, spec in services.items():
+        add("service", name, (spec or {}).get("name", name))
+
+    def fields(step: dict) -> dict[str, str]:
+        got = dict(step.get("data", {}))
+        for sec in step.get("sections", {}).values():
+            got.update(sec.get("data", {}))
+        return got
+
+    async def rendered(step: str) -> dict[str, object]:
+        flow = config_flow.HeatPumpOptimizerConfigFlow()
+        flow.hass = FakeHass()
+        form = await getattr(flow, f"async_step_{step}")(None)
+        found: dict[str, object] = {}
+        stack = [form.get("data_schema")]
+        while stack:
+            sch = stack.pop()
+            for k, v in (getattr(sch, "schema", None) or {}).items():
+                if hasattr(v, "schema") and not isinstance(getattr(v, "schema"), (str, dict)):
+                    stack.append(v.schema)
+                    continue
+                d = k.default() if callable(getattr(k, "default", None)) else None
+                found[str(getattr(k, "schema", k))] = _NONE if d is None else (d if isinstance(
+                    d, (bool, int, float, str)) else _COMPUTED)
+        return found
+
+    for step, spec in _EN_STRINGS["config"]["step"].items():
+        add("setup_step", step, spec.get("title", step))
+        defaults = asyncio.run(rendered(step))
+        for key, label in fields(spec).items():
+            add("setup_field", f"{step}.{key}", label, defaults.get(key, _NONE), spec.get("title", step))
+    titles, _ = options_field_pages()
+    for page in config_flow._OPTION_PAGES:
+        add("option_page", page.step, titles.get(page.step, page.label))
+    opt_steps = _EN_STRINGS["options"]["step"]
+    for f in config_flow._OPTION_FIELDS:
+        d = f.default
+        value = d if isinstance(d, (bool, int, float, str)) and not isinstance(d, config_flow._Rule) else _COMPUTED
+        add("option", f.key or f"{f.step}[{f.group}]", fields(opt_steps.get(f.step, {})).get(f.key, ""), value,
+            titles.get(f.step, f.step))
+    for p in sorted(BLUEPRINTS_DIR.glob("*.yaml")):
+        add("blueprint", p.name, (re.search(r"^\s*name:\s*(.+)$", p.read_text(), re.M) or [None, p.stem])[1].strip())
+    for m in re.finditer(r'^EVENT_\w+ = f"\{DOMAIN\}_(\w+)"', (PKG / "notifier.py").read_text(), re.M):
+        add("event", f"{const.DOMAIN}_{m.group(1)}", m.group(1).replace("_", " "))
+    card = CARD.read_text()
+    for view in ["compact", *dict.fromkeys(re.findall(r'\btab\("(\w+)"', card))]:
+        add("card_view", view, view)
+    block = re.search(r"^const DEFAULTS = \{\n(.*?)^\};", card, re.M | re.S)
+    defaults = {m.group(1): _js_literal(m.group(2))
+                for m in re.finditer(r"^\s+(\w+):\s*(.+?)\s*$", block.group(1) if block else "", re.M)}
+    for key in sorted(set(defaults) | set(re.findall(r"\bconfig\.([a-z_]\w*)", card))):
+        add("card_option", key, key, defaults.get(key, _NONE))
+    for key, issue in json.loads((PKG / "strings.json").read_text())["issues"].items():
+        add("repair", key, issue.get("title", key))
+    return out
+
+
+def _selector_labels(value: str) -> set[str]:
+    return {opts["options"][value] for opts in _EN_STRINGS.get("selector", {}).values()
+            if isinstance(opts, dict) and value in opts.get("options", {})}
+
+
+def default_agrees(value: object, cell: str) -> bool:
+    """A Default cell states the shipped default: the number, the on/off, the choice, or "none" for an empty one. A
+    computed default, or a field with none, needs a non-empty cell naming no number (design section 4, item 1)."""
+    cell = _COMMENT.sub("", cell).strip()
+    flat = re.sub(r"[`*]", "", cell).replace("\u2212", "-").lower()
+    flat = re.sub(r"(?<=\d)[ \u00a0\u202f](?=\d{3}\b)", "", flat)
+    if not flat:
+        return False
+    if value in (_COMPUTED, _NONE):
+        return not re.search(r"\d", flat)
+    if isinstance(value, bool):
+        words = r"on|enabled|yes|true" if value else r"off|disabled|no|false"
+        return bool(re.match(rf"(?:{words})\b", flat))
+    if isinstance(value, (int, float)):
+        m = re.search(r"-?\d+(?:[.,]\d+)?", flat)
+        return m is not None and abs(float(m.group(0).replace(",", ".")) - float(value)) < 1e-9
+    if value == "":
+        return bool(re.match(r"\(?(?:none|empty|not set|\u2014|-)(?:\W|$)", flat))
+    wanted = {value.lower(), value.lower().replace("_", " ")} | {s.lower() for s in _selector_labels(value)}
+    return any(w in flat for w in wanted)
+
+
+def _bold_leads(text: str) -> list[str]:
+    return [m.group(1) for m in re.finditer(r"^(?:[-*]\s+)?\*\*([^*\n]+?)\*\*", _COMMENT.sub("", text), re.M)]
+
+
+def _home(row: dict, pages: dict[str, str]) -> tuple[bool, str]:
+    """(found, why not) for one surface: its home shape is on its home page, and a default the class carries
+    agrees with the home's Default cell."""
+    cls, id_, label = row["class"], row["id"], row["label"]
+    page, heading = _HOMES[cls]
+    body = _under(pages.get(page, ""), heading)
+    if cls in ("option", "setup_field", "card_option", "entity", "event"):
+        want = (_label(label) if cls in ("option", "setup_field") else
+                f"`{id_}`" if cls in ("card_option", "event") else label)
+        for head, hdr, cells in _table_rows(body):
+            first = _label(cells[0]) if cls in ("option", "setup_field") else cells[0].strip("* ")
+            if cls == "event" and want in cells[0] or first == want:
+                # an option's row sits under its page's heading; a setup field's under a heading naming its screen
+                if cls == "option" and _plain(head) != _plain(row["under"]) or (
+                        cls == "setup_field" and f" {_plain(row['under'])} " not in f" {_plain(head)} "):
+                    continue
+                if cls == "entity":
+                    off = "disabled by default" in " ".join(cells).lower()
+                    return (off == (row["value"] == "disabled"),
+                            "" if off == (row["value"] == "disabled") else "the row's disabled-by-default disagrees")
+                if cls == "event":
+                    return True, ""
+                col = next((i for i, h in enumerate(hdr) if h.strip().lower() == "default"), None)
+                if col is None or col >= len(cells):
+                    return False, "its row has no Default cell"
+                return (default_agrees(row["value"], cells[col]),
+                        "" if default_agrees(row["value"], cells[col]) else f"Default cell {cells[col]!r}")
+        return False, "no table row names it"
+    if cls == "service":
+        para = _service_paragraphs(_COMMENT.sub("", body))
+        summary = {c[0] for _, _, c in _table_rows(_under(pages.get("README.md", ""), "## Services"))}
+        if id_ not in para:
+            return False, "no **`name`** paragraph under docs/configuration.md ## Services"
+        return (f"`{id_}`" in summary, "" if f"`{id_}`" in summary else "no row in README.md ## Services")
+    if cls in ("setup_step", "option_page", "card_view"):
+        heads = [re.sub(r"^#+\s+", "", l) for l in body.splitlines() if re.match(r"#{2,4}\s", l)]
+        if cls == "setup_step":
+            heads += [re.sub(r"^#+\s+", "", l) for l in _under(pages.get("docs/configuration.md", ""),
+                                                                 "## Initial setup").splitlines()
+                      if re.match(r"#{2,4}\s", l)]
+            hit = any(f" {_plain(label)} " in f" {_plain(h)} " for h in heads)
+        elif cls == "option_page":
+            hit = any(re.match(r"### ", l) and _plain(l[4:]) == _plain(label) for l in body.splitlines())
+        else:
+            want = {"plan": "reading the chart", "compact": "the card at a glance"}.get(id_, f"the {id_} page")
+            hit = any(_plain(h) == want for h in heads)
+        return hit, "" if hit else "no heading names it"
+    if cls == "blueprint":
+        hit = bool(re.search(r"^\s*[-*]\s.*\(https://raw\.githubusercontent\.com/\S+/blueprints/automation/"
+                             + re.escape(id_) + r"\)", _COMMENT.sub("", body), re.M))
+        return hit, "" if hit else "no bullet links its raw URL"
+    parts = [_plain(p) for p in re.split(r"\{\w+\}", label)]
+    pattern = r" \S+ ".join(re.escape(p) for p in parts if p)
+    hit = any(re.fullmatch(pattern, _plain(b)) for b in _bold_leads(body))
+    return hit, "" if hit else "no bold lead names its title"
+
+
+def _user_pages(root: pathlib.Path = ROOT) -> dict[str, str]:
+    return {p: (root / p).read_text() for p in USER_PAGES if (root / p).is_file()}
+
+
+def _shown(cls: str, value: object) -> str:
+    if cls == "entity":
+        return str(value)
+    if cls not in ("option", "setup_field", "card_option"):
+        return "-"
+    return value if value in (_COMPUTED, _NONE) else json.dumps(value, ensure_ascii=False)
+
+
+def surface_rows(pages: dict[str, str] | None = None, sources: list[dict] | None = None) -> list[dict]:
+    """One row per surface, sorted by its key `(class, id)`: the label, the home page, whether the home is there
+    (`home`, 0 or 1, with `why` when it is not), the default as `--surfaces` prints it, and the exemption reason."""
+    pages = _user_pages() if pages is None else pages
+    rows = []
+    for src in surface_sources() if sources is None else sources:
+        found, why = _home(src, pages)
+        rows.append({**src, "page": _HOMES[src["class"]][0], "home": int(found), "why": why,
+                     "default": _shown(src["class"], src["value"]),
+                     "exempt": SURFACE_EXEMPT.get((src["class"], src["id"]))})
+    return sorted(rows, key=lambda r: (r["class"], r["id"]))
+
+
+def surface_findings(rows: list[dict], exempt: dict[tuple[str, str], str] = SURFACE_EXEMPT) -> list[str]:
+    """What the coverage arm refuses: a duplicate key, a non-exempt surface with no home, an exemption whose
+    reason is under two words, and an exemption naming a key no longer enumerated."""
+    keys = [(r["class"], r["id"]) for r in rows]
+    out = [f"duplicate surface key {k}" for k, n in collections.Counter(keys).items() if n > 1]
+    out += [f"{r['class']} {r['id']!r} ({r['label']}): no home on {r['page']}: {r['why']}"
+            for r in rows if not r["home"] and (r["class"], r["id"]) not in exempt]
+    out += [f"exemption {k} gives a reason of under two words" for k, why in exempt.items()
+            if len(why.split()) < 2]
+    out += [f"exemption {k} names no enumerated surface" for k in exempt if k not in set(keys)]
+    return out
+
+
+def surface_tsv(rows: list[dict]) -> list[str]:
+    return ["\t".join((r["class"], r["id"], r["label"], r["page"], str(r["home"]), r["default"])) for r in rows]
+
+
+_DELTA_FIELDS = ("label", "home-page", "home-found", "default")
+
+
+def _parse_tsv(lines: list[str]) -> dict[tuple[str, str], dict[str, str]]:
+    out = {}
+    for line in lines:
+        cells = line.rstrip("\n").split("\t")
+        if len(cells) == 6:
+            out[(cells[0], cells[1])] = dict(zip(_DELTA_FIELDS, cells[2:]))
+    return out
+
+
+def surface_delta(old: list[str], new: list[str]) -> list[str]:
+    """The keyed delta between two `--surfaces` outputs: LANDED (keys only in `new`), REMOVED (keys only in
+    `old`) and CHANGED (keys in both whose label, home or default differs, naming each field old -> new). A relabel,
+    a lost home or a changed default is a CHANGED line, never a removal plus an addition."""
+    a, b = _parse_tsv(old), _parse_tsv(new)
+    landed = [f"  {c}\t{i}\t{b[(c, i)]['label']}" for c, i in sorted(set(b) - set(a))]
+    removed = [f"  {c}\t{i}\t{a[(c, i)]['label']}" for c, i in sorted(set(a) - set(b))]
+    changed = []
+    for k in sorted(set(a) & set(b)):
+        diff = [f"{f}: {a[k][f]!r} -> {b[k][f]!r}" for f in _DELTA_FIELDS if a[k][f] != b[k][f]]
+        if diff:
+            changed.append(f"  {k[0]}\t{k[1]}\t" + "; ".join(diff))
+    return ([f"LANDED ({len(landed)})", *landed, f"REMOVED ({len(removed)})", *removed,
+             f"CHANGED ({len(changed)})", *changed])
+
+
+def print_surfaces(argv: list[str]) -> int:
+    """`--surfaces`: one sorted line per surface, `class id label home-page home-found default`, tab-separated;
+    exit 1 while a non-exempt surface has no home. `--surfaces --against FILE`: the keyed delta from an earlier
+    `--surfaces` output (FILE) to this tree; exit 1 while any of its three sections is non-empty. Run each with cwd
+    at its own worktree's root: tests/harness.py puts the relative package first on sys.path."""
+    rows = surface_rows()
+    if "--against" in argv:
+        path = pathlib.Path(argv[argv.index("--against") + 1])
+        if not path.is_file():
+            print(f"no --surfaces output at {path}")
+            return 2
+        delta = surface_delta(path.read_text().splitlines(), surface_tsv(rows))
+        print("\n".join(delta))
+        return 1 if any(not line.endswith("(0)") for line in delta if not line.startswith("  ")) else 0
+    print("\n".join(surface_tsv(rows)))
+    bad = surface_findings(rows)
+    for b in bad:
+        print(f"# {b}", file=sys.stderr)
+    return 1 if bad else 0
+
+
+def check_surface_coverage() -> None:
+    R.section("every user-facing surface has its home in the user docs, default included (R10-USER-DOCS-FINAL)")
+    sources = surface_sources()
+    rows = surface_rows(sources=sources)
+    classes = collections.Counter(r["class"] for r in rows)
+    R.check("every surface class enumerates from the tree (anchor)", set(classes) == set(_HOMES),
+            ", ".join(f"{c}={classes.get(c, 0)}" for c in _HOMES))
+    bad = surface_findings(rows)
+    R.check("every surface has its home, or a reasoned exemption that still names one",
+            not bad, "; ".join(bad[:4]) + (f" (+{len(bad) - 4})" if len(bad) > 4 else ""))
+    print(f"       ({len(rows)} surface(s), {sum(r['home'] for r in rows)} homed, {len(SURFACE_EXEMPT)} exempt: "
+          "python3 tests/doc_claims.py --surfaces lists them)")
+    import yaml
+
+    planted = surface_sources(services={**yaml.safe_load((PKG / "services.yaml").read_text()),
+                                        "probe_undocumented": {"name": "Probe"}})
+    got = surface_findings(surface_rows(sources=planted))
+    R.check("red fixture: a service planted in services.yaml with no home is the one finding",
+            len(got) == len(bad) + 1 and any("'probe_undocumented'" in g for g in got), repr(got[:3]))
+    pages = _user_pages()
+    opt = next(r for r in rows if r["class"] == "option" and isinstance(r["value"], float) and r["home"])
+    hdr = next(h for _, h, c in _table_rows(_under(pages["docs/configuration.md"], "## Changing settings later"))
+               if _label(c[0]) == _label(opt["label"]))
+    col = [h.lower() for h in hdr].index("default")
+    lines = pages["docs/configuration.md"].splitlines()
+    i = next(n for n, l in enumerate(lines) if l.startswith("|") and _label(l.strip("|").split("|")[0]) ==
+             _label(opt["label"]))
+    cells = lines[i].strip().strip("|").split("|")
+    cells[col] = " 9999 "
+    moved = {**pages, "docs/configuration.md": "\n".join(lines[:i] + ["|" + "|".join(cells) + "|"] + lines[i + 1:])}
+    got = surface_findings(surface_rows(pages=moved, sources=sources))
+    R.check(f"red fixture: a Default cell that disagrees with the shipped default ({opt['id']}) is a finding",
+            any(f"'{opt['id']}'" in g and "Default cell" in g for g in got), repr(got[:3]))
+    stale = {**SURFACE_EXEMPT, ("service", "gone_service"): "removed from the tree"}
+    R.check("red fixture: an exemption naming a surface no longer enumerated is a finding",
+            any("gone_service" in g for g in surface_findings(rows, stale)))
+    R.check("red fixture: a one-word exemption reason is a finding",
+            any("under two words" in g for g in surface_findings(rows, {**SURFACE_EXEMPT, ("x", "y"): "internal"})))
+    a = surface_tsv(rows)
+    flip = [l.rsplit("\t", 1)[0] + "\t" + json.dumps(9999.0) if l.startswith(f"option\t{opt['id']}\t") else l
+            for l in a]
+    R.check("null control: the delta of a surface list against itself is three empty sections",
+            surface_delta(a, a) == ["LANDED (0)", "REMOVED (0)", "CHANGED (0)"], repr(surface_delta(a, a)))
+    d = surface_delta(a, flip)
+    R.check("red fixture: a changed default is exactly one CHANGED line, nothing LANDED or REMOVED",
+            d[:2] == ["LANDED (0)", "REMOVED (0)"] and d[2] == "CHANGED (1)" and len(d) == 4
+            and "default:" in d[3], repr(d))
+    d = surface_delta(a[1:], a[:-1])
+    R.check("red fixture: an added key is LANDED and a dropped key is REMOVED",
+            d[0] == "LANDED (1)" and a[0].split("\t")[1] in d[1] and d[2] == "REMOVED (1)"
+            and a[-1].split("\t")[1] in d[3], repr(d))
+
+
+# The stateless arm (design section 4, item 2): the user pages state how the integration works, never how it came to
+# work that way -- RELEASE_NOTES.md is where the history lives. Every phrase has word boundaries: a bare `used to`
+# matches "Refused together" (carry udf-used-to-boundary). The bare word "now" is not in the lexicon: its hits are
+# "right now" and a UI label ("Finish setup now"), not history.
+_HISTORY = re.compile(r"(?i:\bnew in\b|\bsince (?:v\d|version\b|#\d)|\bpreviously\b|\bno longer\b|\bused to\b"
+                      r"|\buntil v\d|\bas before\b|\brenamed from\b|\bround \d)|\bv\d+\.\d+|(?<![\w&])#\d{3,}\b"
+                      r"|\bR\d+-")
+# `used to` in its purpose sense ("is used to size the tank", "Used to ..."), which states what a thing does now.
+_PURPOSE = re.compile(r"(?:^|[.!?|]\s*|,\s*|\b(?:is|are|only|also)\s+)$", re.I)
+# (page, fragment, reason): a literal use of a lexicon phrase. Each fragment must match exactly once on its page.
+STATELESS_EXEMPT: tuple[tuple[str, str, str], ...] = ()
+
+
+def _blank(m: re.Match) -> str:
+    return re.sub(r"[^\n]", " ", m.group(0))
+
+
+def stateless_text(text: str) -> str:
+    """The prose a reader reads as a statement: fences, inline code, HTML comments and link targets blanked, line
+    breaks kept so a hit keeps its line number."""
+    text = _FENCE.sub(_blank, text)
+    text = _COMMENT.sub(_blank, text)
+    text = re.sub(r"`[^`\n]+`", _blank, text)
+    text = re.sub(r"(?<=\])\([^)\s]*(?:\s+\"[^\"]*\")?\)", _blank, text)
+    return re.sub(r"<[^>\n]+>", _blank, text)
+
+
+def stateless_findings(pages: dict[str, str], exempt=STATELESS_EXEMPT) -> list[str]:
+    """`page:line: phrase | context` for every history phrase outside an exemption, plus every exemption that does
+    not match exactly once."""
+    out = []
+    spans: dict[str, list[tuple[int, int]]] = {}
+    for page, fragment, _why in exempt:
+        text = stateless_text(pages.get(page, ""))
+        at = [m.start() for m in re.finditer(re.escape(fragment), text)]
+        if len(at) != 1:
+            out.append(f"exemption {page}: {fragment!r} matches {len(at)} times, not once")
+        spans.setdefault(page, []).extend((a, a + len(fragment)) for a in at)
+    for page, raw in pages.items():
+        text = stateless_text(raw)
+        for m in _HISTORY.finditer(text):
+            if m.group(0).lower() == "used to" and _PURPOSE.search(text[:m.start()]):
+                continue
+            if any(a <= m.start() < b for a, b in spans.get(page, ())):
+                continue
+            line = text.count("\n", 0, m.start()) + 1
+            ctx = text.splitlines()[line - 1].strip()
+            out.append(f"{page}:{line}: {m.group(0)!r} | {ctx[:90]}")
+    return out
+
+
+def check_stateless() -> None:
+    R.section("the user pages describe the integration as it is, with no change history (R10-USER-DOCS-FINAL)")
+    pages = _user_pages()
+    R.check("the seven user pages are there (anchor)", len(pages) == len(USER_PAGES),
+            ", ".join(sorted(set(USER_PAGES) - set(pages))))
+    bad = stateless_findings(pages)
+    R.check("no user page carries a history phrase outside a reasoned exemption",
+            not bad, "; ".join(bad[:4]) + (f" (+{len(bad) - 4})" if len(bad) > 4 else ""))
+    for plant in ("This mode is new in v9.", "The card previously showed the price."):
+        got = stateless_findings({"probe.md": f"# T\n\n{plant}\n"})
+        R.check(f"red fixture: {plant!r} is a finding", len(got) >= 1, repr(got))
+    R.check("null control: \"previous day\", a purpose-sense \"is used to\", \"Refused together\", a code span and "
+            "a link anchor are not findings",
+            not stateless_findings({"probe.md": "# T\n\nThe previous day's cost. The sensor is used to size the tank."
+                                                " Refused together. Run `v9.1 previously`. See [x](#1234-x).\n"}))
+    R.check("red fixture: a history-sense \"used to\" is a finding",
+            len(stateless_findings({"probe.md": "# T\n\nThe card used to draw the price.\n"})) == 1)
+    R.check("red fixture: an exemption that matches no fragment is a finding",
+            any("matches 0 times" in g for g in stateless_findings(pages, (("README.md", "no such words", "a b"),))))
+
+
+
 def main() -> int:
     check_figures()
     check_product_page()
@@ -3894,8 +4424,11 @@ def main() -> int:
     check_card_figures()
     check_coffee_button()
     check_readme_marketplace()
+    check_surface_coverage()
+    check_stateless()
     return R.close("checks")
 
 
 if __name__ == "__main__":
-    raise SystemExit(print_marker_census(sys.argv) if "--markers" in sys.argv else main())
+    raise SystemExit(print_marker_census(sys.argv) if "--markers" in sys.argv
+                     else print_surfaces(sys.argv) if "--surfaces" in sys.argv else main())

