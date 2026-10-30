# Review packet #3016
head: 7c6416aa24e3bb0e38a159ff92b83dcf3d6c5089
base: a6e4a5afe37b5371bb4eb7bfc6c67032b70222be

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=124353465944 neutral
arch-score / arch-score id=124353199434 success
arm id=124353073744 skipped
budget-raise-gate / budget-raise-gate id=124353199180 success
cancel-superseded id=124353028155 success
codeql / Analyze (actions) id=124353199395 success
codeql / Analyze (javascript-typescript) id=124353199524 success
codeql / Analyze (python) id=124353199423 in_progress
governance / delivery-status id=124353199530 success
governance / delivery-status-publish id=124353200939 skipped
governance / env-matrix id=124353199408 in_progress
governance / instrument-self-tests id=124353199438 in_progress
governance / policy-docs id=124353199986 success
governance / record id=124353201618 skipped
governance / wave-script id=124353199503 success
hassfest / hassfest id=124353199369 success
kernel-points id=124353200948 skipped
prelude id=124353028242 success
refresh id=124353027821 success
tests / arch-instrument id=124353379074 in_progress
tests / briefs id=124353199345 success
tests / browser id=124353379160 in_progress
tests / closure-scope id=124353199309 success
tests / closures id=124353379266 in_progress
tests / coverage id=124353379126 in_progress
tests / fast (3.14) id=124353379098 in_progress
tests / mutation id=124353199381 failure
tests / mutation-autofix id=124353813842 failure
tests / mutation-pins (1) id=124353460096 success
tests / mutation-pins (2) id=124353460069 success
tests / mutation-pins (3) id=124353460184 success
tests / mutation-pins (4) id=124353460205 success
tests / nightly-ha (2025.2.0) id=124353379157 success
tests / nightly-ha (stable) id=124353379077 success
tests / nightly-status id=124353199283 success
tests / replay id=124353379130 success
tests / typing id=124353379165 success
validate / validate-hacs id=124353199157 success

## Refusals
red-unanswered: concluded red check `tests / mutation` is not named in ## Red checks
red-unanswered: concluded red check `tests / mutation-autofix` is not named in ## Red checks

## Advisories
none

## carry_audit at the head
NOTE body item e0c7f213: dismissed:environment change belongs to the orchestrator, not this fix
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 -I tools/audit/archscore/gate.py --base c098261d4f44 --head 95eebb247775
             `tools/audit/archscore/gate.py` is in the tree at this head
  ok         tests/features.py
             `tests/features.py` is in the tree at this head
  ok         dev/audit/rounds/round9/D12/leads/l2_wood_currency.py
             `dev/audit/rounds/round9/D12/leads/l2_wood_currency.py` is in the tree at this head
  ok         GOLDEN_MODE=drift python3 tests/golden.py
             `tests/golden.py` is in the tree at this head
  ok         python3 tests/env_drift.py --claims-only c098261d4f44
             `tests/env_drift.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff c098261d4f44
             `tests/closure.py` is in the tree at this head

FIGURES: 9 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.configured_quiet_windows.RETURN_DEL.7edb83fa.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.configured_quiet_windows.RETURN_DEL.7edb83fa.json
deleted file mode 100644
index 4fb4b78cd..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.configured_quiet_windows.RETURN_DEL.7edb83fa.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.configured_quiet_windows RETURN_DEL 7edb83fa",
-  "killed_by": "tests/finite_boundary.py",
-  "old": "        return out",
-  "reason": "Recorded by hand (<seat-scratch>/r9-sw-1-resume/drive2.py, the R9-EG-B1 count-relative route: this Mac's tests/features.py is red at main on R9-F2.1 P3, so red baselines are kept) against 04805baaaa7eb85ef9c33fbe20b89e086f70a551: RETURN_DEL (`pass`) took tests/finite_boundary.py from failed=0 to failed=1; the comment-only null control did not raise it, newly failing time-budget checks are not counted, and a +1 was confirmed by re-run."
-}
diff --git a/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.CMP_BOUND.b0150e87.json b/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.CMP_BOUND.b0150e87.json
deleted file mode 100644
index aa537ebf1..000000000
--- a/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.CMP_BOUND.b0150e87.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/wood_fuel.py:cheaper_hour_count CMP_BOUND b0150e87",
-  "killed_by": "tests/guard_pins.py",
-  "old": "        if wood_sek < finite_float(price, 0.0) / cop_f:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if wood_sek <= finite_float(price, 0.0) / cop_f:`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.GUARD_OFF.245ce17b.json b/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.GUARD_OFF.245ce17b.json
deleted file mode 100644
index 3a212a949..000000000
--- a/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.GUARD_OFF.245ce17b.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/wood_fuel.py:cheaper_hour_count GUARD_OFF 245ce17b",
-  "killed_by": "tests/wood_advisor.py",
-  "old": "        if cop_f <= 0.0:",
-  "reason": "Recorded by `mutation_table.py --drain` against aca6ea4567034a05e64edcfd8355d42a8079427d: GUARD_OFF (`if False:`) took tests/wood_advisor.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.GUARD_OFF.75e29480.json b/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.GUARD_OFF.75e29480.json
deleted file mode 100644
index 884330977..000000000
--- a/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.GUARD_OFF.75e29480.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/wood_fuel.py:cheaper_hour_count GUARD_OFF 75e29480",
-  "killed_by": "tests/features.py",
-  "old": "        if not on:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.GUARD_OFF.b0150e87.json b/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.GUARD_OFF.b0150e87.json
deleted file mode 100644
index 258543765..000000000
--- a/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.GUARD_OFF.b0150e87.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/wood_fuel.py:cheaper_hour_count GUARD_OFF b0150e87",
-  "killed_by": "tests/wood_advisor.py",
-  "old": "        if wood_sek < finite_float(price, 0.0) / cop_f:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/wood_advisor.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.RETURN_DEL.608287c2.json b/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.RETURN_DEL.608287c2.json
deleted file mode 100644
index c8cf3372c..000000000
--- a/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.RETURN_DEL.608287c2.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/wood_fuel.py:cheaper_hour_count RETURN_DEL 608287c2",
-  "killed_by": "tests/guard_pins.py",
-  "old": "    return n",
-  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/wood_fuel.py/wood_cheaper.CMP_BOUND.5f837d78.json b/tests/mutation_ledger/killed_by/wood_fuel.py/wood_cheaper.CMP_BOUND.5f837d78.json
deleted file mode 100644
index e048de679..000000000
--- a/tests/mutation_ledger/killed_by/wood_fuel.py/wood_cheaper.CMP_BOUND.5f837d78.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/wood_fuel.py:wood_cheaper CMP_BOUND 5f837d78",
-  "killed_by": "tests/features.py",
-  "old": "    return cheaper_hour_count(wood_sek, prices, cops, runs) > 0",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return cheaper_hour_count(wood_sek, prices, cops, runs) >= 0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}


## Three-dot diff
diff --git a/README.md b/README.md
index 4d291dcb2..6c3f2aec7 100644
--- a/README.md
+++ b/README.md
@@ -796,6 +796,7 @@ from Settings → Automations & Scenes → Blueprints → Import Blueprint:
 - [Economy mode through the evening price peak](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/main/blueprints/automation/economy_mode_on_price_peak.yaml) — switches the optimizer's mode when the current electricity price crosses your expensive threshold, and back when it falls.
 - [Notify when a manual plan takes over](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/main/blueprints/automation/notify_on_manual_plan.yaml) — raises a persistent notification while an `apply_manual_plan` override pins the heating slots.
 - [Notifications](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/main/blueprints/automation/notifications.yaml) — sends the optimizer's documented events (monthly receipt, comfort at risk, stale input, stale plan, released manual plan) to a notify target, with quiet hours.
+- [Notify when wood beats the heat pump today](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/main/blueprints/automation/notify_wood_cheaper_window.yaml) — a morning phone notification naming today's cheaper-than-pump windows and when to light the furnace, with an optional follow-up after a replan; silent on a day with none.
 
 Each blueprint takes the sensor and thresholds as inputs, so nothing is
 hard-coded to the entity ids the examples assume.
diff --git a/blueprints/automation/notify_wood_cheaper_window.yaml b/blueprints/automation/notify_wood_cheaper_window.yaml
new file mode 100644
index 000000000..3e46c6d11
--- /dev/null
+++ b/blueprints/automation/notify_wood_cheaper_window.yaml
@@ -0,0 +1,120 @@
+blueprint:
+  name: Heat Pump Optimizer - notify when wood beats the heat pump today
+  description: >-
+    Send a phone notification on a day when the plan expects firewood to be
+    cheaper than the heat pump: the cheaper windows and when to light the
+    furnace so it is warm as the first window opens, both in local time. The
+    Wood Cheaper Than Heat Pump sensor carries today's windows in its
+    cheaper_windows attribute and the lighting window in lighting_start and
+    lighting_end; the lead time is the "Light the furnace this long before a
+    cheaper window" option on the wood page. One notification at the send
+    time, and optionally a follow-up later the same day when a replan brings
+    a window that was not there before. A day with no cheaper window sends
+    nothing.
+  domain: automation
+  author: tvofi
+  source_url: https://raw.githubusercontent.com/tvofi/heatpump_optimizer/main/blueprints/automation/notify_wood_cheaper_window.yaml
+  input:
+    wood_sensor:
+      name: Wood Cheaper Than Heat Pump sensor
+      description: >-
+        The optimizer's wood comparison sensor. It is disabled by default;
+        enable it under the integration's entities once the wood furnace is
+        set up. Entity ids are fixed at `binary_sensor.heat_pump_optimizer_*`
+        regardless of the entry name.
+      default: binary_sensor.heat_pump_optimizer_wood_cheaper
+      selector:
+        entity:
+          domain: binary_sensor
+    notify_device:
+      name: Phone
+      description: >-
+        The Home Assistant companion app device that receives the
+        notification, through its notify.mobile_app_* action.
+      selector:
+        device:
+          integration: mobile_app
+    send_time:
+      name: Send time
+      description: >-
+        When the day's notification is sent. Early morning, so the windows
+        are known before the day starts.
+      default: "06:00:00"
+      selector:
+        time: {}
+    notify_on_replan:
+      name: Follow up after a replan
+      description: >-
+        Later the same day, send one more notification when a replan brings a
+        cheaper window that is not yet open and was not in the plan before.
+      default: true
+      selector:
+        boolean: {}
+    title_template:
+      name: Title
+      description: >-
+        The notification title. A template; windows_text,
+        lighting_start_text and lighting_end_text hold the local times.
+      default: "Wood beats the heat pump today"
+      selector:
+        text: {}
+    message_template:
+      name: Message
+      description: >-
+        The notification text. A template; windows_text lists today's
+        cheaper windows, lighting_start_text and lighting_end_text bound the
+        recommended lighting window, all as HH:MM local time.
+      default: >-
+        Firewood is cheaper than the heat pump {{ windows_text }}. Light the
+        furnace between {{ lighting_start_text }} and {{ lighting_end_text }}.
+      selector:
+        text:
+          multiline: true
+mode: single
+max_exceeded: silent
+variables:
+  wood_sensor: !input wood_sensor
+  notify_device: !input notify_device
+  send_time: !input send_time
+  notify_on_replan: !input notify_on_replan
+  windows: "{{ state_attr(wood_sensor, 'cheaper_windows') or [] }}"
+  windows_text: >-
+    {% set ns = namespace(parts=[]) %}{% for w in windows %}{% set ns.parts =
+    ns.parts + [as_timestamp(w.start) | timestamp_custom('%H:%M') ~ '–' ~
+    as_timestamp(w.end) | timestamp_custom('%H:%M')] %}{% endfor %}{{
+    ns.parts | join(', ') }}
+  lighting_start_text: >-
+    {% set t = state_attr(wood_sensor, 'lighting_start') %}{{
+    as_timestamp(t) | timestamp_custom('%H:%M') if t else '' }}
+  lighting_end_text: >-
+    {% set t = state_attr(wood_sensor, 'lighting_end') %}{{
+    as_timestamp(t) | timestamp_custom('%H:%M') if t else '' }}
+trigger:
+  - platform: time
+    at: !input send_time
+    id: daily
+  - platform: state
+    entity_id: !input wood_sensor
+    attribute: cheaper_windows
+    id: replan
+condition:
+  - "{{ windows | count > 0 }}"
+  - "{{ state_attr(wood_sensor, 'lighting_start') is not none }}"
+  - condition: or
+    conditions:
+      - "{{ trigger.id == 'daily' }}"
+      - condition: and
+        conditions:
+          - "{{ notify_on_replan }}"
+          - "{{ now() >= today_at(send_time) }}"
+          - >-
+            {% set old = (trigger.from_state.attributes.get('cheaper_windows')
+            or []) if trigger.from_state else [] %}{% set ns =
+            namespace(new=false) %}{% for w in windows %}{% if w not in old
+            and as_timestamp(w.start) > as_timestamp(now()) %}{% set ns.new =
+            true %}{% endif %}{% endfor %}{{ ns.new }}
+action:
+  - action: notify.mobile_app_{{ device_attr(notify_device, 'name') | slugify }}
+    data:
+      title: !input title_template
+      message: !input message_template
diff --git a/custom_components/heatpump_optimizer/binary_sensor.py b/custom_components/heatpump_optimizer/binary_sensor.py
index dacc1d081..eea76f87a 100644
--- a/custom_components/heatpump_optimizer/binary_sensor.py
+++ b/custom_components/heatpump_optimizer/binary_sensor.py
@@ -333,5 +333,8 @@ class WoodCheaperBinarySensor(_OptimizerBinarySensorBase):
         return {
             "sek_per_kwh": fuel.get("sek_per_kwh"),
             "cheaper_hour_count": fuel.get("cheaper_hour_count"),
+            "cheaper_windows": fuel.get("cheaper_windows") or [],
+            "lighting_start": fuel.get("lighting_start"),
+            "lighting_end": fuel.get("lighting_end"),
         }
 
diff --git a/custom_components/heatpump_optimizer/config_flow.py b/custom_components/heatpump_optimizer/config_flow.py
index 048e4ee1c..f05ec6884 100644
--- a/custom_components/heatpump_optimizer/config_flow.py
+++ b/custom_components/heatpump_optimizer/config_flow.py
@@ -264,6 +264,8 @@ from .const import (
     DEFAULT_WOOD_TYPE,
     DEFAULT_WOOD_PACKING,
     DEFAULT_WOOD_FURNACE_EFFICIENCY,
+    CONF_WOOD_LIGHTING_LEAD_MINUTES,
+    DEFAULT_WOOD_LIGHTING_LEAD_MINUTES,
     WOOD_TYPES,
     WOOD_PACKINGS,
     CONF_PRICE_PRIOR_ENABLED,
@@ -1690,6 +1692,7 @@ _OPTION_FIELDS: Final[tuple[_F, ...]] = (
     _F("building", CONF_WOOD_PACKING, DEFAULT_WOOD_PACKING, _select(list(WOOD_PACKINGS), 'wood_packing'), when=wood_furnace_on, group="wood"),
     _F("building", CONF_WOOD_PRICE_SEK_M3, _SUGGESTED, _ByHass(lambda hass: _money(10000, 10, hass, "/m³")), when=wood_furnace_on, group="wood"),
     _F("building", CONF_WOOD_FURNACE_EFFICIENCY, DEFAULT_WOOD_FURNACE_EFFICIENCY, _number(10, 95, 1, '%', slider=True), when=wood_furnace_on, group="wood"),
+    _F("building", CONF_WOOD_LIGHTING_LEAD_MINUTES, DEFAULT_WOOD_LIGHTING_LEAD_MINUTES, _number(0, 240, 15, 'min', slider=True), when=wood_furnace_on, group="wood"),
     _F("building", CONF_SPACE_PUMP_ENTITY, _STORED, _entity_of(['switch', 'input_boolean']), group="circulation"),
     # -- thermal_model
     _F("thermal_model", CONF_HOUSE_THERMAL_MASS, _SUGGESTED, _number(*RANGE_HOUSE_THERMAL_MASS, 0.5, 'kWh/°C')),
diff --git a/custom_components/heatpump_optimizer/const.py b/custom_components/heatpump_optimizer/const.py
index 7302a27d4..a74a5a946 100644
--- a/custom_components/heatpump_optimizer/const.py
+++ b/custom_components/heatpump_optimizer/const.py
@@ -340,6 +340,10 @@ CONF_WOOD_FURNACE_EFFICIENCY: Final = "wood_furnace_efficiency"
 DEFAULT_WOOD_TYPE: Final = "mixed"
 DEFAULT_WOOD_PACKING: Final = "packed"
 DEFAULT_WOOD_FURNACE_EFFICIENCY: Final = 75.0
+# How long before a cheaper-than-pump window the furnace should be lit, so
+# the boiler is past its warm-up and charging the tank as the window opens.
+CONF_WOOD_LIGHTING_LEAD_MINUTES: Final = "wood_lighting_lead_minutes"
+DEFAULT_WOOD_LIGHTING_LEAD_MINUTES: Final = 60.0
 WOOD_TYPES: Final = ("birch", "pine", "mixed")
 WOOD_PACKINGS: Final = ("packed", "loose")
 
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index 88ac5122a..9301c866a 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -7856,8 +7856,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         return format_windows(params.dhw_windows)
 
     def configured_quiet_windows(self) -> dict[str, str]:
-        out = quiet_windows.configured_specs(getattr(self, "_ctx", self)._config, getattr(getattr(getattr(self, "hass", None), "states", None), "get", None))
-        return out
+        return quiet_windows.configured_specs(getattr(self, "_ctx", self)._config, getattr(getattr(getattr(self, "hass", None), "states", None), "get", None))
 
     def describe_setup(self) -> dict[str, Any]:
         """The configured topology, for every picture of the system.
@@ -7969,6 +7968,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             thermal_model=self._thermal_model,
             current_state=ctx._current_state,
             result=result,
+            local_tz=dt_util.DEFAULT_TIME_ZONE,
         )
         # Only surface the manual-plan key while an override is actually active,
         # so a plan-free solve (the golden fixtures included) is byte-for-byte
diff --git a/custom_components/heatpump_optimizer/entry_config.py b/custom_components/heatpump_optimizer/entry_config.py
index 7a0c9806c..aa24e56c2 100644
--- a/custom_components/heatpump_optimizer/entry_config.py
+++ b/custom_components/heatpump_optimizer/entry_config.py
@@ -186,6 +186,7 @@ class EntryConfig(Mapping[str, Any]):
     target_temperature: float = _key(const.DEFAULT_TARGET_TEMP, finite_float)
     thermal_bridge_frsi: float = _key(const.DEFAULT_THERMAL_BRIDGE_FRSI, finite_float)
     vvc_lead_minutes: float = _key(const.DEFAULT_VVC_LEAD_MINUTES, finite_float)
+    wood_lighting_lead_minutes: float = _key(const.DEFAULT_WOOD_LIGHTING_LEAD_MINUTES, finite_float)
     wood_tank_volume: float = _key(const.DEFAULT_WOOD_TANK_VOLUME, finite_float)
 
     # A fraction this version cannot read caps nothing: None, not the default.
diff --git a/custom_components/heatpump_optimizer/payload.py b/custom_components/heatpump_optimizer/payload.py
index ff71705b9..eae89d29f 100644
--- a/custom_components/heatpump_optimizer/payload.py
+++ b/custom_components/heatpump_optimizer/payload.py
@@ -443,6 +443,11 @@ class WoodSlot(TypedDict, total=False):
     source: str
 
 
+class WoodWindow(TypedDict):
+    start: str
+    end: str
+
+
 class WoodFuel(TypedDict, total=False):
     ready: bool
     cheaper: bool
@@ -455,6 +460,9 @@ class WoodFuel(TypedDict, total=False):
     cheaper_hour_count: int
     slots: list[WoodSlot]
     night_advice: NightAdvice
+    cheaper_windows: list[WoodWindow]
+    lighting_start: str
+    lighting_end: str
 
 
 class Accuracy(TypedDict, total=False):
diff --git a/custom_components/heatpump_optimizer/strings.json b/custom_components/heatpump_optimizer/strings.json
index 67ef0dc61..a956f568d 100644
--- a/custom_components/heatpump_optimizer/strings.json
+++ b/custom_components/heatpump_optimizer/strings.json
@@ -810,6 +810,7 @@
               "external_heat_min_rise": "Temperature rise that counts as evidence",
               "valve_outlet_temp_entity": "Temperature after the wood/heat-pump mixing valve (optional)",
               "wood_furnace_efficiency": "Furnace efficiency",
+              "wood_lighting_lead_minutes": "Light the furnace this long before a cheaper window",
               "wood_furnace_enabled": "Wood furnace",
               "wood_packing": "Packing",
               "wood_price_sek_m3": "Price per cubic metre",
@@ -826,6 +827,7 @@
               "external_heat_min_rise": "Raise this if normal operation triggers it. Missing a fire costs one unnecessary heating cycle; wrongly assuming one can leave you without hot water.",
               "valve_outlet_temp_entity": "Temperature of the blended flow leaving the valve that mixes wood and heat-pump water. With the tank sensors it tells the plan how much of the heating a fire is covering right now, so electric heat can stand down by that much instead of all-or-nothing.",
               "wood_furnace_efficiency": "Share of the wood's energy that reaches the tank, percent.",
+              "wood_lighting_lead_minutes": "How long before a window where wood beats the heat pump to light the furnace, so it is past its warm-up and charging the tank as the window opens. Sets the lighting window on the Wood Cheaper Than Heat Pump sensor.",
               "wood_furnace_enabled": "Off hides the wood probes, detection and fuel price; stored values are kept. A lone 500 L tank volume does not turn this on.",
               "wood_packing": "Packed is stacked (travad); loose is dumped (stjälpt) and billed at 0.60 of packed.",
               "wood_price_sek_m3": "What you pay per billed cubic metre. Empty keeps the cheaper-than-pump sensor unavailable — there is no silent default.",
diff --git a/custom_components/heatpump_optimizer/translations/en.json b/custom_components/heatpump_optimizer/translations/en.json
index 950f65ad6..daa2898e2 100644
--- a/custom_components/heatpump_optimizer/translations/en.json
+++ b/custom_components/heatpump_optimizer/translations/en.json
@@ -810,6 +810,7 @@
               "external_heat_min_rise": "Temperature rise that counts as evidence",
               "valve_outlet_temp_entity": "Temperature after the wood/heat-pump mixing valve (optional)",
               "wood_furnace_efficiency": "Furnace efficiency",
+              "wood_lighting_lead_minutes": "Light the furnace this long before a cheaper window",
               "wood_furnace_enabled": "Wood furnace",
               "wood_packing": "Packing",
               "wood_price_sek_m3": "Price per cubic metre",
@@ -826,6 +827,7 @@
               "external_heat_min_rise": "Raise this if normal operation triggers it. Missing a fire costs one unnecessary heating cycle; wrongly assuming one can leave you without hot water.",
               "valve_outlet_temp_entity": "Temperature of the blended flow leaving the valve that mixes wood and heat-pump water. With the tank sensors it tells the plan how much of the heating a fire is covering right now, so electric heat can stand down by that much instead of all-or-nothing.",
               "wood_furnace_efficiency": "Share of the wood's energy that reaches the tank, percent.",
+              "wood_lighting_lead_minutes": "How long before a window where wood beats the heat pump to light the furnace, so it is past its warm-up and charging the tank as the window opens. Sets the lighting window on the Wood Cheaper Than Heat Pump sensor.",
               "wood_furnace_enabled": "Off hides the wood probes, detection and fuel price; stored values are kept. A lone 500 L tank volume does not turn this on.",
               "wood_packing": "Packed is stacked (travad); loose is dumped (stjälpt) and billed at 0.60 of packed.",
               "wood_price_sek_m3": "What you pay per billed cubic metre. Empty keeps the cheaper-than-pump sensor unavailable — there is no silent default.",
diff --git a/custom_components/heatpump_optimizer/translations/sv.json b/custom_components/heatpump_optimizer/translations/sv.json
index d9f0a22eb..3fdac5f2e 100644
--- a/custom_components/heatpump_optimizer/translations/sv.json
+++ b/custom_components/heatpump_optimizer/translations/sv.json
@@ -810,6 +810,7 @@
               "external_heat_min_rise": "Temperaturökning som räknas som bevis",
               "valve_outlet_temp_entity": "Temperatur efter shunten mellan ved- och värmepumpstank (valfri)",
               "wood_furnace_efficiency": "Pannverkningsgrad",
+              "wood_lighting_lead_minutes": "Tänd pannan så här länge före ett billigare fönster",
               "wood_furnace_enabled": "Vedpanna",
               "wood_packing": "Packning",
               "wood_price_sek_m3": "Pris per kubikmeter",
@@ -826,6 +827,7 @@
               "external_heat_min_rise": "Höj om normal drift utlöser den. Att missa en brasa kostar en onödig uppvärmningscykel; att felaktigt anta en kan lämna dig utan varmvatten.",
               "valve_outlet_temp_entity": "Temperaturen på det blandade flödet som lämnar ventilen som blandar ved- och värmepumpsvatten. Tillsammans med tankgivarna talar den om hur stor del av uppvärmningen en brasa täcker just nu, så att elvärmen kan stå tillbaka lika mycket i stället för allt eller inget.",
               "wood_furnace_efficiency": "Andel av vedens energi som når tanken, i procent.",
+              "wood_lighting_lead_minutes": "Hur långt innan ett fönster där ved är billigare än värmepumpen pannan ska tändas, så att den är förbi uppeldningen och laddar tanken när fönstret börjar. Styr tändfönstret på sensorn Ved billigare än värmepump.",
               "wood_furnace_enabled": "Av döljer vedgivare, detektering och bränslepris; sparade värden ligger kvar. En ensam volym på 500 L slår inte på detta.",
               "wood_packing": "Tvad (travad) eller stjälpt. Stjälpt räknas som 0,60 av tvad.",
               "wood_price_sek_m3": "Vad du betalar per fakturerad kubikmeter. Tomt fält gör givaren Ved billigare än värmepump otillgänglig — det finns inget tyst förval.",
diff --git a/custom_components/heatpump_optimizer/wood_fuel.py b/custom_components/heatpump_optimizer/wood_fuel.py
index 445bd775c..7e8acdd15 100644
--- a/custom_components/heatpump_optimizer/wood_fuel.py
+++ b/custom_components/heatpump_optimizer/wood_fuel.py
@@ -2,7 +2,7 @@
 from __future__ import annotations
 
 from collections.abc import Callable, Iterable, Mapping, Sequence
-from datetime import datetime, timedelta
+from datetime import datetime, timedelta, tzinfo
 from typing import Any
 
 from .drift import utc_elapsed_seconds
@@ -12,16 +12,18 @@ from .const import (
     CONF_EXTERNAL_HEAT_ENTITY,
     CONF_WOOD_FURNACE_EFFICIENCY,
     CONF_WOOD_FURNACE_ENABLED,
+    CONF_WOOD_LIGHTING_LEAD_MINUTES,
     CONF_WOOD_PACKING,
     CONF_WOOD_PRICE_SEK_M3,
     CONF_WOOD_TANK_BOTTOM_ENTITY,
     CONF_WOOD_TANK_TOP_ENTITY,
     CONF_WOOD_TYPE,
     DEFAULT_MIN_TEMP,
+    DEFAULT_WOOD_LIGHTING_LEAD_MINUTES,
     WOOD_TANK_MAX_TEMP,
 )
 from .const import finite_float
-from .payload import NightAdvice, WoodFuel, WoodSlot
+from .payload import NightAdvice, WoodFuel, WoodSlot, WoodWindow
 
 WOOD_KWH_M3 = {
     "birch": {"packed": 1900.0, "loose": 1140.0},
@@ -115,27 +117,80 @@ def wood_fuel_ready(config: Mapping[str, Any]) -> bool:
     return price > 0.0 and 10.0 <= eff <= 95.0
 
 
-def cheaper_hour_count(
+def cheaper_steps(
     wood_sek: float,
     prices: Sequence[object],
     cops: Sequence[object],
     runs: Sequence[bool],
-) -> int:
-    """Steps the plan runs the pump at whose heat costs more than wood's.
+) -> list[bool]:
+    """Per step: the plan runs the pump and its heat costs more than wood's.
 
     ``runs`` is the plan's own on schedule (``heat_pump_on_schedule``): a
     step it calls off buys no pump heat for wood to undercut (D8-s1-01).
+    A step with no usable COP is never cheaper.
     """
-    n = 0
+    out: list[bool] = []
     for price, cop, on in zip(prices, cops, runs, strict=False):
-        if not on:
-            continue
         cop_f = finite_float(cop, 0.0)
-        if cop_f <= 0.0:
+        out.append(
+            bool(on)
+            and cop_f > 0.0
+            and wood_sek < finite_float(price, 0.0) / cop_f
+        )
+    return out
+
+
+def cheaper_hour_count(
+    wood_sek: float,
+    prices: Sequence[object],
+    cops: Sequence[object],
+    runs: Sequence[bool],
+) -> int:
+    """Steps the plan runs the pump at whose heat costs more than wood's."""
+    return sum(cheaper_steps(wood_sek, prices, cops, runs))
+
+
+def cheaper_windows(
+    timestamps: Sequence[datetime],
+    cheaper: Sequence[bool],
+    local_tz: tzinfo | None,
+) -> list[tuple[datetime, datetime]]:
+    """Today's contiguous runs of ``cheaper`` steps as (start, end).
+
+    Today is the local calendar day of the plan's first step; a run crossing
+    midnight ends there. A step's end is the next step's start, so a plan of
+    one step has no measurable step and yields none.
+    """
+    if len(timestamps) < 2:
+        return []
+
+    def day(ts: datetime) -> object:
+        return (ts.astimezone(local_tz) if local_tz is not None else ts).date()
+
+    today = day(timestamps[0])
+    step = timestamps[1] - timestamps[0]
+    out: list[tuple[datetime, datetime]] = []
+    for ts, cheap in zip(timestamps, cheaper, strict=False):
+        if day(ts) != today:
+            break
+        if not cheap:
             continue
-        if wood_sek < finite_float(price, 0.0) / cop_f:
-            n += 1
-    return n
+        if out and out[-1][1] == ts:
+            out[-1] = (out[-1][0], ts + step)
+        else:
+            out.append((ts, ts + step))
+    return out
+
+
+def lighting_window(
+    first_start: datetime, now: datetime, lead_minutes: float
+) -> tuple[datetime, datetime]:
+    """When to light so the furnace is up to temperature as the window opens.
+
+    Opens ``lead_minutes`` before the window and closes at its start; never
+    opens before ``now``, so a window already open means "light now".
+    """
+    return max(first_start - timedelta(minutes=lead_minutes), now), first_start
 
 
 def _scan_wood_night(
@@ -206,15 +261,6 @@ def night_advice(
     return {"action": "none", "text": "", "when": None, "reason": ""}
 
 
-def wood_cheaper(
-    wood_sek: float,
-    prices: Sequence[object],
-    cops: Sequence[object],
-    runs: Sequence[bool],
-) -> bool:
-    return cheaper_hour_count(wood_sek, prices, cops, runs) > 0
-
-
 def _iso(ts: object) -> str:
     return ts.isoformat() if hasattr(ts, "isoformat") else str(ts)
 
@@ -409,11 +455,17 @@ def build_wood_fuel_view(
     cop_at: Callable[[float], object],
     timestamps: Sequence[datetime],
     forecast_kw: list[float],
-    suppressing: bool,
     wood_tank_temperature: float | None = None,
     comfort_min: float | None = None,
+    local_tz: tzinfo | None = None,
 ) -> WoodFuel:
-    """Ready/cheaper/slots. cheaper is False when not ready."""
+    """Ready/cheaper/slots. cheaper is False when not ready.
+
+    ``forecast_kw`` is the detector's free-heat forecast, empty while it is
+    not suppressing, so detected slots exist only while it suppresses.
+    ``cheaper_windows`` and the lighting window are present only while
+    today has a cheaper window, so a view without one is unchanged.
+    """
     wtype = config.get(CONF_WOOD_TYPE)
     packing = config.get(CONF_WOOD_PACKING)
     price = finite_float(config.get(CONF_WOOD_PRICE_SEK_M3))
@@ -433,12 +485,14 @@ def build_wood_fuel_view(
             sek = None
     ready = wood_fuel_ready(config)
     count = 0
-    cheaper = False
+    cheap: list[bool] = []
     if ready and sek is not None:
         cops = _cops(outdoor, cop_at)
         count = cheaper_hour_count(sek, prices, cops, runs)
-        cheaper = wood_cheaper(sek, prices, cops, runs)
-    slots = detected_wood_slots(timestamps, forecast_kw) if suppressing else []
+        if count:
+            cheap = cheaper_steps(sek, prices, cops, runs)
+    cheaper = count > 0
+    slots = detected_wood_slots(timestamps, forecast_kw)
     view: WoodFuel = {
         "ready": ready,
         "cheaper": cheaper,
@@ -451,6 +505,7 @@ def build_wood_fuel_view(
         "cheaper_hour_count": count,
         "slots": slots,
     }
+    _attach_windows(view, config, timestamps, cheap, local_tz)
     _attach_night_advice(
         view,
         config,
@@ -465,6 +520,36 @@ def build_wood_fuel_view(
     return view
 
 
+def _attach_windows(
+    view: WoodFuel,
+    config: Mapping[str, Any],
+    timestamps: Sequence[datetime],
+    cheap: Sequence[bool],
+    local_tz: tzinfo | None,
+) -> None:
+    runs = cheaper_windows(timestamps, cheap, local_tz)
+    if not runs:
+        return
+
+    def iso(ts: datetime) -> str:
+        return (ts.astimezone(local_tz) if local_tz is not None else ts).isoformat()
+
+    windows: list[WoodWindow] = [
+        {"start": iso(start), "end": iso(end)} for start, end in runs
+    ]
+    lead = max(
+        0.0,
+        finite_float(
+            config.get(CONF_WOOD_LIGHTING_LEAD_MINUTES),
+            DEFAULT_WOOD_LIGHTING_LEAD_MINUTES,
+        ),
+    )
+    light_start, light_end = lighting_window(runs[0][0], timestamps[0], lead)
+    view["cheaper_windows"] = windows
+    view["lighting_start"] = iso(light_start)
+    view["lighting_end"] = iso(light_end)
+
+
 def _attach_night_advice(
     view: WoodFuel,
     config: Mapping[str, Any],
@@ -504,6 +589,7 @@ def wood_fuel_from_parts(
     thermal_model: Any,
     current_state: Any,
     result: Any,
+    local_tz: tzinfo | None = None,
 ) -> WoodFuel:
     """The published wood-fuel view from the coordinator's parts (#1739).
 
@@ -513,8 +599,7 @@ def wood_fuel_from_parts(
     """
     n = len(result.timestamps) if result is not None else 0
     det = external_heat
-    suppressing = bool(det.suppressing)
-    if result is not None and suppressing:
+    if result is not None and det.suppressing:
         forecast_kw = det.forecast_free_heat(
             n,
             opt_config.dt_hours,
@@ -532,7 +617,7 @@ def wood_fuel_from_parts(
         cop_at=thermal_model.compute_cop,
         timestamps=list(result.timestamps) if result is not None else [],
         forecast_kw=forecast_kw,
-        suppressing=suppressing,
         wood_tank_temperature=getattr(current_state, "wood_tank_temperature", None),
         comfort_min=getattr(opt_config, "min_temp", None),
+        local_tz=local_tz,
     )
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index 884f80777..eafbf2df4 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -965,9 +965,9 @@
  {
   "id": "C108",
   "source": "README.md + docs/*.md",
-  "claim": "every relative link resolves (84 links)",
+  "claim": "every relative link resolves (85 links)",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "84 links, broken=[], of which removed-by-the-export=[]",
+  "result": "85 links, broken=[], of which removed-by-the-export=[]",
   "verdict": "true",
   "truth": ""
  },
@@ -992,7 +992,7 @@
  {
   "id": "C111",
   "source": "README.md + docs/*.md",
-  "claim": "every external link answers 200 to a HEAD request (19 links)",
+  "claim": "every external link answers 200 to a HEAD request (20 links)",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py --links",
   "result": "not run: pass --links",
   "verdict": "unverifiable",
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index 4dd228422..7910edc99 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -111,10 +111,10 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C105 | `docs/automations.md` | the Power Headroom sensor appears once anything bounds the house -- a main fuse OR a capacity tariff -- and a tariff-only install reads 0.0 kW with limit_source='capacity tariff with no peak reference yet' until the month's first metering window closes; with neither it stays unavailable | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | no fuse + capacity tariff enabled -> {'available': True, 'limit_kw': 0.0, 'headroom_kw': 0.0, 'baseline_source': 'planned power only (no meter)', 'limit_source': 'capacity tariff with no peak reference yet'}; fuse only -> available=True; neither -> available=False | **true** |  |
 | C106 | `docs/automations.md` | Power Headroom is min(main fuse, capacity threshold) - current house draw, clamped at zero, in kW | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | fuse 20 A 3-phase -> limit_kw=13.8, headroom_kw=13.8, limit_source='main fuse' | **true** |  |
 | C107 | `README.md + docs/*.md + the card` | every entity id quoted in the documentation is an entity the platforms construct | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 9 distinct ids cited, not constructed=[] | **true** |  |
-| C108 | `README.md + docs/*.md` | every relative link resolves (84 links) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 84 links, broken=[], of which removed-by-the-export=[] | **true** |  |
+| C108 | `README.md + docs/*.md` | every relative link resolves (85 links) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 85 links, broken=[], of which removed-by-the-export=[] | **true** |  |
 | C109 | `README.md + docs/how-it-works.md` | the links to docs/audit-2026-08.md, docs/audit-2026-09.md and docs/backlog.md resolve | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | finder_wall in tools/audit/prepare_baseline.sh removes docs/audit-*.md, dev/archive/audits/audit-*.md and dev/archive/backlog.md; this tree cannot answer | **unverifiable** | not checkable in the export -- finder_wall removes docs/audit-*.md, dev/archive/audits/audit-*.md and dev/archive/backlog.md |
 | C110 | `README.md + docs/*.md` | every image the documentation embeds exists (22 images) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 22 images, missing=[] | **true** |  |
-| C111 | `README.md + docs/*.md` | every external link answers 200 to a HEAD request (19 links) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py --links` | not run: pass --links | **unverifiable** | re-run with --links |
+| C111 | `README.md + docs/*.md` | every external link answers 200 to a HEAD request (20 links) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py --links` | not run: pass --links | **unverifiable** | re-run with --links |
 | C112 | `strings.json + translations/*.json` | every translation file carries exactly the keys strings.json declares | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | languages=['en', 'sv'], missing={'en': 0, 'sv': 0}, extra={'en': 0, 'sv': 0} | **true** |  |
 | C113 | `README.md` | entity names are translated into English and Swedish | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['en', 'sv'] measured=['en', 'sv'] | **true** |  |
 | C114 | `README.md` | every entity's display name comes from the translation files | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | untranslated=[] | **true** |  |
diff --git a/dev/audit/rounds/round9/D12/leads/l2_wood_currency.py b/dev/audit/rounds/round9/D12/leads/l2_wood_currency.py
index 4d43f10bf..0b74f1dae 100644
--- a/dev/audit/rounds/round9/D12/leads/l2_wood_currency.py
+++ b/dev/audit/rounds/round9/D12/leads/l2_wood_currency.py
@@ -56,7 +56,7 @@ def count(prices, wood_price):
     view = wood_fuel.build_wood_fuel_view(
         {**CFG, const.CONF_WOOD_PRICE_SEK_M3: wood_price}, prices=prices, outdoor=outdoor,
         space_kw=space, dhw_kw=dhw, cop_at=lambda t: 2.5 + 0.05 * t, timestamps=stamps,
-        forecast_kw=[], suppressing=False)
+        forecast_kw=[])
     return view["cheaper_hour_count"], view
 
 
diff --git a/dev/programme/delivery/3016.md b/dev/programme/delivery/3016.md
new file mode 100644
index 000000000..40ded8e47
--- /dev/null
+++ b/dev/programme/delivery/3016.md
@@ -0,0 +1 @@
+- [#3016](https://github.com/tvofi/heatpump_optimizer/pull/3016) — **open**, R10-WOOD-NOTIFY: blueprint notifies when wood beats the heat pump, with a recommended lighting window (R10-WOOD-NOTIFY)
diff --git a/docs/automations.md b/docs/automations.md
index 4dd7bc2f7..5e7f253f6 100644
--- a/docs/automations.md
+++ b/docs/automations.md
@@ -179,3 +179,4 @@ Blueprints → Import Blueprint:
 - [Economy mode through the evening price peak](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/main/blueprints/automation/economy_mode_on_price_peak.yaml) — from the second example above.
 - [Notify when a manual plan takes over](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/main/blueprints/automation/notify_on_manual_plan.yaml) — from the third example above.
 - [Notifications](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/main/blueprints/automation/notifications.yaml) — sends the five events above to a notify target, one switch per event, with quiet hours that the comfort alert passes through.
+- [Notify when wood beats the heat pump today](https://raw.githubusercontent.com/tvofi/heatpump_optimizer/main/blueprints/automation/notify_wood_cheaper_window.yaml) — one phone notification on a day the plan expects firewood to be cheaper than the heat pump, naming the cheaper windows (the Wood Cheaper Than Heat Pump sensor's `cheaper_windows` attribute) and when to light the furnace (`lighting_start` to `lighting_end`, opened by the wood page's lead time before the first window), with an optional follow-up when a replan brings a new window. Silent on a day with none.
diff --git a/docs/configuration.md b/docs/configuration.md
index bba7b039c..bafe04ef0 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -699,6 +699,7 @@ catalog below keys off.
 | Packing | Packed (stacked) | Packed (stacked) · Loose (dumped) | Packed is stacked (travad); loose is dumped (stjälpt) and billed at 0.60 of packed. |
 | Price per cubic metre | none | 0–10 000, 10 steps | What you pay per billed cubic metre. **Empty keeps the cheaper-than-pump sensor unavailable — there is no silent default.** |
 | Furnace efficiency | 75 % | 10–95 | Share of the wood's energy that reaches the tank. |
+| Light the furnace this long before a cheaper window | 60 min | 0–240, 15 steps | How far ahead of today's first cheaper window the recommended lighting window opens: a batch boiler spends roughly half an hour to an hour going from kindling to a full burn with its water hot enough for the load valve to charge the tank. The window closes as the cheaper window opens, and never opens before now. |
 | Heating circulation pump switch | none | `switch` / `input_boolean` | Paused only in slots that are provably idle and warm — it always runs when heat is planned, when it is freezing outside, or when any room is near its comfort floor. |
 
 The four fuel-price fields and the external-heat detection group render only
@@ -707,6 +708,12 @@ while **Wood furnace** is on. The
 on, a wood-tank probe is set, external-heat detection or the DHW wood coil
 is on, type and packing are set, the billed price is greater than 0, and
 efficiency is between 10 and 95. A usable wood tank alone is not enough.
+While it is available it also carries today's cheaper windows — each run of
+planned heat-pump steps whose heat costs more than wood's, as `start` and
+`end` in the `cheaper_windows` attribute — and the recommended lighting
+window ahead of the first of them in `lighting_start` and `lighting_end`.
+Both are empty on a day with no cheaper window. The
+[wood notification blueprint](automations.md#blueprints) sends them to a phone.
 
 ### Building type and emitters
 
diff --git a/tests/closure.py b/tests/closure.py
index bba004d32..3d882c594 100644
--- a/tests/closure.py
+++ b/tests/closure.py
@@ -691,6 +691,7 @@ INERT_EXCEPT = (
     "blueprints/automation/charge_ev_from_grid_headroom.yaml",
     "blueprints/automation/economy_mode_on_price_peak.yaml",
     "blueprints/automation/notify_on_manual_plan.yaml",
+    "blueprints/automation/notify_wood_cheaper_window.yaml",
     "blueprints/automation/notifications.yaml",
     ".gitignore",
     # #995, the .gitignore story one lane later: the live-header harness check
diff --git a/tests/closures.json b/tests/closures.json
index ceb95f3f0..5ff90e4ea 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -1103,6 +1103,7 @@
    "blueprints/automation/economy_mode_on_price_peak.yaml",
    "blueprints/automation/notifications.yaml",
    "blueprints/automation/notify_on_manual_plan.yaml",
+   "blueprints/automation/notify_wood_cheaper_window.yaml",
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
    "custom_components/heatpump_optimizer/away.py",
@@ -3668,11 +3669,13 @@
    "tests/validate.py"
   ],
   "tests/wood_advisor.py": [
+   "blueprints/automation/notify_wood_cheaper_window.yaml",
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
+   "custom_components/heatpump_optimizer/binary_sensor.py",
    "custom_components/heatpump_optimizer/boost.py",
    "custom_components/heatpump_optimizer/comfort_band.py",
    "custom_components/heatpump_optimizer/comfort_learning.py",
@@ -3738,6 +3741,7 @@
    "tests/harness.py",
    "tests/hastub/homeassistant/__init__.py",
    "tests/hastub/homeassistant/components/__init__.py",
+   "tests/hastub/homeassistant/components/binary_sensor.py",
    "tests/hastub/homeassistant/components/mqtt.py",
    "tests/hastub/homeassistant/components/repairs.py",
    "tests/hastub/homeassistant/components/sensor.py",
diff --git a/tests/entities.py b/tests/entities.py
index 1260ef106..9a68f14b5 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -6900,9 +6900,16 @@ R.check(
     _wf_ready_entity.available is True,
 )
 R.check(
-    "cheaper attributes are sek_per_kwh and cheaper_hour_count",
+    "cheaper attributes are sek_per_kwh, cheaper_hour_count and the "
+    "windows, empty while the view carries none",
     _wf_ready_entity.extra_state_attributes
-    == {"sek_per_kwh": 0.6, "cheaper_hour_count": 1},
+    == {
+        "sek_per_kwh": 0.6,
+        "cheaper_hour_count": 1,
+        "cheaper_windows": [],
+        "lighting_start": None,
+        "lighting_end": None,
+    },
 )
 
 # Mold Floor Breach (#1495). The floor is the one the solve enforces -- the
@@ -12501,7 +12508,8 @@ _PUBLISHED_ATTRS: dict[str, frozenset[str]] = {
     }),
     "VentilationBinarySensor": frozenset({"evidence"}),
     "WoodCheaperBinarySensor": frozenset({
-        "cheaper_hour_count", "sek_per_kwh"
+        "cheaper_hour_count", "cheaper_windows", "lighting_end",
+        "lighting_start", "sek_per_kwh"
     }),
     "WoodBurnAdvisorSensor": frozenset({"action", "reason", "when"}),
 }
diff --git a/tests/features.py b/tests/features.py
index d82394cf4..954663c20 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -42241,7 +42241,6 @@ from heatpump_optimizer.wood_fuel import (
     cheaper_hour_count as _wf_count,
     liters_to_kwh as _wf_liters,
     useful_kwh_m3 as _wf_useful,
-    wood_cheaper as _wf_cheaper,
     wood_fuel_ready as _wf_ready,
     wood_furnace_inferred as _wf_inferred,
     wood_furnace_on as _wf_on,
@@ -42300,11 +42299,11 @@ _wf_no_price = dict(_wf_cfg, wood_price_sek_m3=0.0)
 R.check("price 0 is not ready", not _wf_ready(_wf_no_price))
 R.check(
     "idle plan is not cheaper",
-    not _wf_cheaper(1.0, [2.0], [3.0], [False]),
+    _wf_count(1.0, [2.0], [3.0], [False]) == 0,
 )
 R.check(
     "one hour the plan runs the pump, and wood is cheaper, is on",
-    _wf_cheaper(1.0, [4.0], [2.0], [True]),
+    _wf_count(1.0, [4.0], [2.0], [True]) > 0,
 )
 R.check(
     "that hour counts",
@@ -42409,7 +42408,6 @@ _wf_not_ready = _wf_view(
     cop_at=lambda _t: 2.0,
     timestamps=[],
     forecast_kw=[],
-    suppressing=False,
 )
 R.check(
     "data wood_fuel cheaper is false when not ready",
@@ -42515,7 +42513,6 @@ _wf_soc_kwargs = dict(
     cop_at=lambda _t: 3.0,
     timestamps=_wf_stamps,
     forecast_kw=[],
-    suppressing=False,
 )
 _wf_light_view = _wf_view(
     _wf_cfg,
@@ -42567,7 +42564,6 @@ _wf_skip_view = _wf_view(
     cop_at=lambda _t: 3.0,
     timestamps=_wf_stamps,
     forecast_kw=[],
-    suppressing=False,
     wood_tank_temperature=87.4,
     comfort_min=19.0,
 )
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index b7341d300..a12392fce 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -58,6 +58,7 @@
 #
 # v7.1.0: Round-10 merge train: claim-carry barrier, train admission, COP gate and part-load, Health tab, Marketplace. The stamp empties the list; the
 # next branch restates its own footprint, claims included.
+config_flow # r10-wood-notify: the wood_lighting_lead_minutes option joins the seeded wood group; one key added, no value moved
 #
 # may-drift: flat_prices -- #1208 polish-every-candidate, owner ruling #1208 comment 208bed25
 # (option (a)): the move's margin is inside the noise band (objective rel
diff --git a/tests/golden/config_flow.json b/tests/golden/config_flow.json
index 49f528857..7309e0d95 100644
--- a/tests/golden/config_flow.json
+++ b/tests/golden/config_flow.json
@@ -1371,6 +1371,18 @@
       "required": "Optional",
       "selector": "type"
      },
+     "wood_lighting_lead_minutes": {
+      "config": {
+       "max": "240",
+       "min": "0",
+       "mode": "'slider'",
+       "step": "15",
+       "unit_of_measurement": "'min'"
+      },
+      "default": "60.0",
+      "required": "Optional",
+      "selector": "NumberSelector"
+     },
      "wood_packing": {
       "config": {
        "mode": "'dropdown'",
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.configured_quiet_windows.RETURN_DEL.7edb83fa.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.configured_quiet_windows.RETURN_DEL.7edb83fa.json
deleted file mode 100644
index 4fb4b78cd..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.configured_quiet_windows.RETURN_DEL.7edb83fa.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.configured_quiet_windows RETURN_DEL 7edb83fa",
-  "killed_by": "tests/finite_boundary.py",
-  "old": "        return out",
-  "reason": "Recorded by hand (<seat-scratch>/r9-sw-1-resume/drive2.py, the R9-EG-B1 count-relative route: this Mac's tests/features.py is red at main on R9-F2.1 P3, so red baselines are kept) against 04805baaaa7eb85ef9c33fbe20b89e086f70a551: RETURN_DEL (`pass`) took tests/finite_boundary.py from failed=0 to failed=1; the comment-only null control did not raise it, newly failing time-budget checks are not counted, and a +1 was confirmed by re-run."
-}
diff --git a/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.CMP_BOUND.b0150e87.json b/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.CMP_BOUND.b0150e87.json
deleted file mode 100644
index aa537ebf1..000000000
--- a/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.CMP_BOUND.b0150e87.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/wood_fuel.py:cheaper_hour_count CMP_BOUND b0150e87",
-  "killed_by": "tests/guard_pins.py",
-  "old": "        if wood_sek < finite_float(price, 0.0) / cop_f:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if wood_sek <= finite_float(price, 0.0) / cop_f:`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.GUARD_OFF.245ce17b.json b/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.GUARD_OFF.245ce17b.json
deleted file mode 100644
index 3a212a949..000000000
--- a/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.GUARD_OFF.245ce17b.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/wood_fuel.py:cheaper_hour_count GUARD_OFF 245ce17b",
-  "killed_by": "tests/wood_advisor.py",
-  "old": "        if cop_f <= 0.0:",
-  "reason": "Recorded by `mutation_table.py --drain` against aca6ea4567034a05e64edcfd8355d42a8079427d: GUARD_OFF (`if False:`) took tests/wood_advisor.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.GUARD_OFF.75e29480.json b/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.GUARD_OFF.75e29480.json
deleted file mode 100644
index 884330977..000000000
--- a/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.GUARD_OFF.75e29480.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/wood_fuel.py:cheaper_hour_count GUARD_OFF 75e29480",
-  "killed_by": "tests/features.py",
-  "old": "        if not on:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.GUARD_OFF.b0150e87.json b/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.GUARD_OFF.b0150e87.json
deleted file mode 100644
index 258543765..000000000
--- a/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.GUARD_OFF.b0150e87.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/wood_fuel.py:cheaper_hour_count GUARD_OFF b0150e87",
-  "killed_by": "tests/wood_advisor.py",
-  "old": "        if wood_sek < finite_float(price, 0.0) / cop_f:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/wood_advisor.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.RETURN_DEL.608287c2.json b/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.RETURN_DEL.608287c2.json
deleted file mode 100644
index c8cf3372c..000000000
--- a/tests/mutation_ledger/killed_by/wood_fuel.py/cheaper_hour_count.RETURN_DEL.608287c2.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/wood_fuel.py:cheaper_hour_count RETURN_DEL 608287c2",
-  "killed_by": "tests/guard_pins.py",
-  "old": "    return n",
-  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/wood_fuel.py/wood_cheaper.CMP_BOUND.5f837d78.json b/tests/mutation_ledger/killed_by/wood_fuel.py/wood_cheaper.CMP_BOUND.5f837d78.json
deleted file mode 100644
index e048de679..000000000
--- a/tests/mutation_ledger/killed_by/wood_fuel.py/wood_cheaper.CMP_BOUND.5f837d78.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/wood_fuel.py:wood_cheaper CMP_BOUND 5f837d78",
-  "killed_by": "tests/features.py",
-  "old": "    return cheaper_hour_count(wood_sek, prices, cops, runs) > 0",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return cheaper_hour_count(wood_sek, prices, cops, runs) >= 0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/wood_advisor.py b/tests/wood_advisor.py
index 4c311c702..681ebb30a 100644
--- a/tests/wood_advisor.py
+++ b/tests/wood_advisor.py
@@ -155,4 +155,309 @@ R.check(
     "a guard that skipped every hour would hide the real comparison",
 )
 
+R.section("Today's cheaper windows and the lighting window")
+
+# Driven through the production view builder. A ready config at 1275 SEK/m3
+# of mixed packed wood at 75 % burns at 1275 / (1700 * 0.75) = 1.0 SEK/kWh;
+# with a flat COP of 3 the pump's heat costs price / 3, so wood is cheaper
+# exactly on the steps priced above 3.0.
+from datetime import datetime as _dt, timedelta as _td, timezone as _tz
+
+from heatpump_optimizer import binary_sensor as _bs
+from heatpump_optimizer.wood_fuel import build_wood_fuel_view
+
+_WOOD_READY = {
+    "wood_tank_top_entity": "sensor.wood_tank_top",
+    "external_heat_detection_enabled": True,
+    "wood_type": "mixed",
+    "wood_packing": "packed",
+    "wood_price_sek_m3": 1275.0,
+    "wood_furnace_efficiency": 75.0,
+}
+_DAY0 = _dt(2026, 1, 15, 0, 0, tzinfo=_tz.utc)
+# 30 hourly steps: today and the first six hours of tomorrow.
+_STAMPS = [_DAY0 + _td(hours=i) for i in range(30)]
+
+
+def _wood_view(cheap_steps, off_steps=(), config=None):
+    n = len(_STAMPS)
+    return build_wood_fuel_view(
+        _WOOD_READY if config is None else config,
+        prices=[4.0 if i in cheap_steps else 1.0 for i in range(n)],
+        outdoor=[0.0] * n,
+        runs=[i not in off_steps for i in range(n)],
+        cop_at=lambda _t: 3.0,
+        timestamps=_STAMPS,
+        forecast_kw=[],
+        local_tz=_tz.utc,
+    )
+
+
+def _at(hour, minute=0):
+    return (_DAY0 + _td(hours=hour, minutes=minute)).isoformat()
+
+
+def _lighting(view):
+    return view.get("lighting_start"), view.get("lighting_end")
+
+
+# Two cheaper runs today (06-08 and 17-20), a cheaper step at 12 while the
+# pump is planned off, and a cheaper step tomorrow at 02.
+_two = _wood_view({6, 7, 12, 17, 18, 19, 26}, off_steps={12})
+R.check(
+    "a day with two cheaper runs gives two windows, each contiguous run once",
+    _two.get("cheaper_windows")
+    == [
+        {"start": _at(6), "end": _at(8)},
+        {"start": _at(17), "end": _at(20)},
+    ],
+    repr(_two.get("cheaper_windows")),
+)
+R.check(
+    "the lighting window opens the default 60 min before the first window "
+    "and closes at its start",
+    _lighting(_two) == (_at(5), _at(6)),
+    repr(_lighting(_two)),
+)
+_lead90 = _wood_view({6, 7}, config={**_WOOD_READY, "wood_lighting_lead_minutes": 90})
+R.check(
+    "the lead time is the configured option",
+    _lighting(_lead90) == (_at(4, 30), _at(6)),
+    repr(_lighting(_lead90)),
+)
+_now_open = _wood_view({0, 1})
+R.check(
+    "a window open at the plan's first step lights now, never in the past",
+    _lighting(_now_open) == (_at(0), _at(0)),
+    repr(_lighting(_now_open)),
+)
+_off_day = _wood_view({12}, off_steps={12})
+R.check(
+    "a cheaper step while the pump is planned off is not a window",
+    _off_day.get("cheaper_windows", []) == [] and _lighting(_off_day) == (None, None),
+    repr(_off_day.get("cheaper_windows")),
+)
+_tomorrow = _wood_view({26})
+R.check(
+    "a cheaper step tomorrow is counted but is not one of today's windows",
+    _tomorrow.get("cheaper_windows", []) == []
+    and _tomorrow.get("cheaper_hour_count") == 1,
+    repr(_tomorrow.get("cheaper_windows")),
+)
+_CET = _tz(_td(hours=1))
+_local = build_wood_fuel_view(
+    _WOOD_READY,
+    prices=[4.0 if i in (22, 23) else 1.0 for i in range(30)],
+    outdoor=[0.0] * 30,
+    runs=[True] * 30,
+    cop_at=lambda _t: 3.0,
+    timestamps=_STAMPS,
+    forecast_kw=[],
+    local_tz=_CET,
+)
+R.check(
+    "today is the local day: at UTC+1 the 23:00 UTC step is tomorrow, and the "
+    "window is published in local time",
+    _local.get("cheaper_windows")
+    == [{"start": "2026-01-15T23:00:00+01:00", "end": "2026-01-16T00:00:00+01:00"}],
+    repr(_local.get("cheaper_windows")),
+)
+_never = _wood_view(set())
+R.check(
+    "null control: a day wood never beats the pump gives no windows and no "
+    "lighting window",
+    _never.get("cheaper_windows", []) == []
+    and _lighting(_never) == (None, None)
+    and _never.get("cheaper_hour_count") == 0,
+    repr(_never),
+)
+_attrs = _bs.WoodCheaperBinarySensor(
+    FakeCoordinator({"wood_fuel": _two}), ENTRY
+).extra_state_attributes
+R.check(
+    "the wood sensor publishes the windows and the lighting window as attributes",
+    _attrs.get("cheaper_windows") == _two["cheaper_windows"]
+    and (_attrs.get("lighting_start"), _attrs.get("lighting_end"))
+    == (_at(5), _at(6)),
+    repr(_attrs),
+)
+_null_attrs = _bs.WoodCheaperBinarySensor(
+    FakeCoordinator({"wood_fuel": _never}), ENTRY
+).extra_state_attributes
+R.check(
+    "and with no window it publishes an empty list and no lighting window",
+    _null_attrs.get("cheaper_windows") == []
+    and (_null_attrs.get("lighting_start"), _null_attrs.get("lighting_end"))
+    == (None, None),
+    repr(_null_attrs),
+)
+
+R.section("The wood-window notification blueprint")
+
+# Read as Home Assistant reads it: ``!input`` is a reference to a declared
+# input. Every declared input is used and every reference is declared, so an
+# input renamed on one side only is refused.
+import pathlib as _pl
+
+import yaml as _yaml
+
+_BP_NAME = "notify_wood_cheaper_window.yaml"
+_BP_TEXT = (
+    _pl.Path(__file__).resolve().parent.parent / "blueprints" / "automation" / _BP_NAME
+).read_text()
+
+
+class _Input(str):
+    pass
+
+
+class _BpLoader(_yaml.SafeLoader):
+    pass
+
+
+_BpLoader.add_constructor(
+    "!input", lambda loader, node: _Input(loader.construct_scalar(node))
+)
+_BP = _yaml.load(_BP_TEXT, Loader=_BpLoader)
+
+
+def _refs(node):
+    if isinstance(node, _Input):
+        yield str(node)
+    elif isinstance(node, dict):
+        for v in node.values():
+            yield from _refs(v)
+    elif isinstance(node, list):
+        for v in node:
+            yield from _refs(v)
+
+
+_bp_inputs = set(_BP["blueprint"]["input"])
+_used = set(_refs({k: v for k, v in _BP.items() if k != "blueprint"}))
+R.check(
+    "every declared blueprint input is referenced, and every reference declared",
+    bool(_bp_inputs) and _bp_inputs == _used,
+    f"declared-only {sorted(_bp_inputs - _used)}, undeclared {sorted(_used - _bp_inputs)}",
+)
+R.check(
+    "the blueprint names its own import URL and its author, as its siblings do",
+    _BP["blueprint"]["source_url"].endswith("/blueprints/automation/" + _BP_NAME)
+    and _BP["blueprint"]["author"] == "tvofi",
+    repr((_BP["blueprint"].get("source_url"), _BP["blueprint"].get("author"))),
+)
+R.check(
+    "it listens to the wood sensor's window attribute and a daily time",
+    {(t.get("platform"), t.get("attribute")) for t in _BP["trigger"]}
+    == {("time", None), ("state", "cheaper_windows")},
+    repr(_BP["trigger"]),
+)
+
+# The templates, rendered against the production sensor's attributes. CI's
+# fast lane installs no jinja2 (tests/requirements-ci.txt), so this arm runs
+# where it is installed: the HA helpers below are the few the blueprint calls,
+# shaped as Home Assistant's are, with local time fixed at UTC.
+try:
+    from jinja2.nativetypes import NativeEnvironment as _Env
+except ImportError:
+    _Env = None
+R.section(
+    "The blueprint's templates against a fixture state"
+    + ("" if _Env is not None else " -- NOT RENDERED: jinja2 is not installed")
+)
+if _Env is not None:
+
+    def _ts(value):
+        if isinstance(value, (int, float)):
+            return float(value)
+        return _dt.fromisoformat(str(value)).timestamp()
+
+    def _render(template, ctx):
+        env = _Env()
+        env.filters["timestamp_custom"] = lambda ts, fmt: _dt.fromtimestamp(
+            ts, _tz.utc
+        ).strftime(fmt)
+        env.filters["slugify"] = lambda s: "_".join(str(s).lower().split())
+        env.globals.update(
+            as_timestamp=_ts,
+            state_attr=lambda eid, attr: ctx["_attrs"].get(attr),
+            now=lambda: ctx["_now"],
+            today_at=lambda hms: ctx["_now"].replace(
+                hour=int(hms[:2]), minute=int(hms[3:5]), second=0
+            ),
+            device_attr=lambda dev, attr: "Pixel 8",
+        )
+        if not isinstance(template, str):
+            return template
+        return env.from_string(template).render(
+            **{k: v for k, v in ctx.items() if not k.startswith("_")}
+        )
+
+    def _run(attrs, now, trigger):
+        defaults = {
+            k: v.get("default") for k, v in _BP["blueprint"]["input"].items()
+        }
+        defaults["notify_device"] = "device-1"
+        ctx = {"_attrs": attrs, "_now": now, "trigger": trigger}
+        for name, tpl in _BP["variables"].items():
+            ctx[name] = _render(
+                defaults[str(tpl)] if isinstance(tpl, _Input) else tpl, ctx
+            )
+
+        def cond(c):
+            if isinstance(c, str):
+                return _render(c, ctx) is True
+            parts = [cond(x) for x in c["conditions"]]
+            return any(parts) if c["condition"] == "or" else all(parts)
+
+        sent = all(cond(c) for c in _BP["condition"])
+        action = _BP["action"][0]
+        return sent, {
+            "action": _render(action["action"], ctx),
+            "title": _render(defaults[str(action["data"]["title"])], ctx),
+            "message": _render(defaults[str(action["data"]["message"])], ctx),
+        }
+
+    class _State:
+        def __init__(self, attrs):
+            self.attributes = attrs
+
+    _daily = {"id": "daily"}
+    _sent, _note = _run(_attrs, _DAY0.replace(hour=6), _daily)
+    R.check(
+        "on a day with two windows the daily send fires and names both windows "
+        "and the lighting window in local time",
+        _sent
+        and "06:00–08:00, 17:00–20:00" in _note["message"]
+        and "between 05:00 and 06:00" in _note["message"]
+        and _note["action"] == "notify.mobile_app_pixel_8",
+        repr((_sent, _note)),
+    )
+    _sent_null, _ = _run(_null_attrs, _DAY0.replace(hour=6), _daily)
+    R.check(
+        "null control: on a day with no cheaper window it stays silent",
+        _sent_null is False,
+        repr(_sent_null),
+    )
+    _first_only = {**_attrs, "cheaper_windows": _attrs["cheaper_windows"][:1]}
+    _replan = {
+        "id": "replan",
+        "from_state": _State(_first_only),
+        "to_state": _State(_attrs),
+    }
+    _sent_new, _ = _run(_attrs, _DAY0.replace(hour=10), _replan)
+    R.check(
+        "a replan that brings a new upcoming window after the send time follows up",
+        _sent_new is True,
+        repr(_sent_new),
+    )
+    _same = {**_replan, "from_state": _State(_attrs)}
+    _sent_same, _ = _run(_attrs, _DAY0.replace(hour=10), _same)
+    _sent_early, _ = _run(_attrs, _DAY0.replace(hour=5), _replan)
+    R.check(
+        "and one whose windows did not change, or that lands before the send "
+        "time, does not",
+        _sent_same is False and _sent_early is False,
+        repr((_sent_same, _sent_early)),
+    )
+
 sys.exit(R.close("wood-advisor checks"))

