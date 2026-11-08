# Review packet #3300
head: 21fdd06b99ebb71e58d37e431aeeec8ccd928764
base: 48af0864a43052a43e9125fa31c2822bac99165d

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=128608559272 neutral
arch-score / arch-score id=128608418340 success
arm id=128608292961 skipped
budget-raise-gate / budget-raise-gate id=128608418451 success
cancel-superseded id=128608292716 success
codeql id=128608419038 skipped
codeql / Analyze (actions) id=128608394878 success
codeql / Analyze (javascript-typescript) id=128608394856 success
codeql / Analyze (python) id=128608394887 in_progress
gate id=128608585703 failure
governance id=128608418901 skipped
governance / delivery-status id=128608394924 success
governance / delivery-status-publish id=128608395792 skipped
governance / env-matrix id=128608394761 in_progress
governance / instrument-self-tests id=128608394931 in_progress
governance / policy-docs id=128608394864 success
governance / record id=128608396134 skipped
governance / wave-script id=128608394888 success
hassfest id=128608419526 skipped
hassfest / hassfest id=128608394793 success
kernel-points id=128608419329 skipped
pr-contract id=128608586632 skipped
prelude id=128608292964 success
refresh id=128608292889 success
tests id=128608419279 skipped
tests / arch-instrument id=128608511070 success
tests / briefs id=128608394895 success
tests / browser id=128608511074 success
tests / closure-scope id=128608395000 success
tests / closures id=128608511123 in_progress
tests / coverage id=128608511119 in_progress
tests / fast (3.14) id=128608511098 in_progress
tests / mutation id=128608394877 in_progress
tests / nightly-ha id=128608512375 skipped
tests / nightly-status id=128608394925 success
tests / replay id=128608511079 in_progress
tests / typing id=128608511072 success
validate id=128608419030 skipped
validate / validate-hacs id=128608394787 success

## Refusals
required-red: required context `gate` concluded failure at 21fdd06b99ebb71e58d37e431aeeec8ccd928764

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/features.py
             `tests/features.py` is in the tree at this head
  ok         PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  ok         tools/audit/seat/mutant_run.py --diff origin/main...HEAD
             `tools/audit/seat/mutant_run.py` is in the tree at this head

FIGURES: 4 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_track_states.RETURN_DEL.da09b9a2.json b/tests/mutation_ledger/killed_by/coordinator.py/_track_states.RETURN_DEL.da09b9a2.json
new file mode 100644
index 000000000..fbbeaa8e4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_track_states.RETURN_DEL.da09b9a2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_track_states RETURN_DEL da09b9a2",
+  "killed_by": "tests/features.py",
+  "old": "    return async_track_state_change_event(hass, entity_ids, callback(lambda event: action(event)))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReader._begin.GUARD_OFF.c5567f15.json b/tests/mutation_ledger/killed_by/inputs.py/InputReader._begin.GUARD_OFF.c5567f15.json
new file mode 100644
index 000000000..69817334c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/InputReader._begin.GUARD_OFF.c5567f15.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReader._begin GUARD_OFF c5567f15",
+  "killed_by": "tests/features.py",
+  "old": "        if not has_value(state):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=15."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReader._begin.GUARD_OFF.d3150a8e.json b/tests/mutation_ledger/killed_by/inputs.py/InputReader._begin.GUARD_OFF.d3150a8e.json
deleted file mode 100644
index f9f4f8853..000000000
--- a/tests/mutation_ledger/killed_by/inputs.py/InputReader._begin.GUARD_OFF.d3150a8e.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReader._begin GUARD_OFF d3150a8e",
-  "killed_by": "tests/structure.py",
-  "old": "        if raw is None or str(raw).lower() in _INVALID_STATES:",
-  "reason": "Recorded by `mutation_table.py --drain` against aca6ea4567034a05e64edcfd8355d42a8079427d: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._drop.GUARD_OFF.7bdf1e66.json b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._drop.GUARD_OFF.7bdf1e66.json
new file mode 100644
index 000000000..b8940b6d9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._drop.GUARD_OFF.7bdf1e66.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReturnWatch._drop GUARD_OFF 7bdf1e66",
+  "killed_by": "tests/features.py",
+  "old": "        if unsub is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._on_event.BOOLOP.c43e9ddb.json b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._on_event.BOOLOP.c43e9ddb.json
new file mode 100644
index 000000000..5a9164031
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._on_event.BOOLOP.c43e9ddb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReturnWatch._on_event BOOLOP c43e9ddb",
+  "killed_by": "tests/features.py",
+  "old": "        if reread is not None and self.clock() - reread < self.spacing_s:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if reread is not None or self.clock() - reread < self.spacing_s:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._on_event.CMP_BOUND.c43e9ddb.json b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._on_event.CMP_BOUND.c43e9ddb.json
new file mode 100644
index 000000000..ea8461555
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._on_event.CMP_BOUND.c43e9ddb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReturnWatch._on_event CMP_BOUND c43e9ddb",
+  "killed_by": "tests/features.py",
+  "old": "        if reread is not None and self.clock() - reread < self.spacing_s:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if reread is not None and self.clock() - reread <= self.spacing_s:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._on_event.GUARD_OFF.c43e9ddb.json b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._on_event.GUARD_OFF.c43e9ddb.json
new file mode 100644
index 000000000..82062e88b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._on_event.GUARD_OFF.c43e9ddb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReturnWatch._on_event GUARD_OFF c43e9ddb",
+  "killed_by": "tests/features.py",
+  "old": "        if reread is not None and self.clock() - reread < self.spacing_s:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.BOOLOP.7ca77e31.json b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.BOOLOP.7ca77e31.json
new file mode 100644
index 000000000..7ad67bec4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.BOOLOP.7ca77e31.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReturnWatch.arm BOOLOP 7ca77e31",
+  "killed_by": "tests/features.py",
+  "old": "            if reading.entity_id and reading.problem in RETURN_WATCHED_PROBLEMS",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if reading.entity_id or reading.problem in RETURN_WATCHED_PROBLEMS`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.GUARD_OFF.21834646.json b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.GUARD_OFF.21834646.json
new file mode 100644
index 000000000..0d93bec74
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.GUARD_OFF.21834646.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReturnWatch.arm GUARD_OFF 21834646",
+  "killed_by": "tests/features.py",
+  "old": "        if wanted:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.GUARD_OFF.6f7a9fe0.json b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.GUARD_OFF.6f7a9fe0.json
new file mode 100644
index 000000000..fa280a035
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.GUARD_OFF.6f7a9fe0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReturnWatch.arm GUARD_OFF 6f7a9fe0",
+  "killed_by": "tests/features.py",
+  "old": "        if self.released:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.GUARD_OFF.ecb87ca6.json b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.GUARD_OFF.ecb87ca6.json
new file mode 100644
index 000000000..1409d6c4c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.GUARD_OFF.ecb87ca6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReturnWatch.arm GUARD_OFF ecb87ca6",
+  "killed_by": "tests/features.py",
+  "old": "        if wanted == self._entities:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/has_value.BOOLOP.1f655796.json b/tests/mutation_ledger/killed_by/inputs.py/has_value.BOOLOP.1f655796.json
new file mode 100644
index 000000000..6b7be9575
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/has_value.BOOLOP.1f655796.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:has_value BOOLOP 1f655796",
+  "killed_by": "tests/features.py",
+  "old": "    return raw is not None and str(raw).lower() not in _INVALID_STATES",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return raw is not None or str(raw).lower() not in _INVALID_STATES`) took tests/features.py from rc=0 failed=0 to rc=1 failed=18."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/has_value.RETURN_DEL.1f655796.json b/tests/mutation_ledger/killed_by/inputs.py/has_value.RETURN_DEL.1f655796.json
new file mode 100644
index 000000000..09a8b5381
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/has_value.RETURN_DEL.1f655796.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:has_value RETURN_DEL 1f655796",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    return raw is not None and str(raw).lower() not in _INVALID_STATES",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=3."
+}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index abb9b8115..66456fc5b 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -202,6 +202,7 @@ from .inputs import (
     InputHealth,
     InputReader,
     InputReading,
+    InputReturnWatch,
     age_of,
     normalize_price_per_kwh,
     parse_bool,
@@ -630,6 +631,17 @@ def _peak_tariff_hours(spec: str) -> tuple[Any, ...]:
 _FENCED_CAUSES: set[tuple[str, str]] = set()
 
 
+def _track_states(
+    hass: HomeAssistant, entity_ids: list[str], action: Callable[[Any], None]
+) -> Callable[[], None]:
+    """``async_track_state_change_event`` for a plain callable, run on the loop.
+
+    The tracker ``InputReturnWatch`` is handed, so ``inputs`` imports no
+    Home Assistant; ``@callback`` keeps the action off the executor.
+    """
+    return async_track_state_change_event(hass, entity_ids, callback(lambda event: action(event)))
+
+
 async def _best_effort_cycle_step(step: Callable[[], Any], message: str) -> None:
     """Run one best-effort cycle step, logging -- never raising -- its fault.
 
@@ -3606,6 +3618,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             self, self._spawn, self._adopt_away_override, config, self._entity_state
         )
         away_mode.watch_away_inputs(hass, entry, config, self.async_request_refresh)
+        self._input_returns = InputReturnWatch(functools.partial(_track_states, hass), lambda:
+            hass.async_create_task(self.async_request_refresh()), 60.0 * config.optimization_interval)
 
     @callback
     def _release_registrations(self) -> None:
@@ -3621,6 +3635,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         # #1755 r1: a released entry drops its worker-fallback latch, so a removed
         # entry cannot hold the shared repair issue or leak a key after it is gone.
         _clear_worker_fallback(self.hass, self.entry.entry_id)
+        self._input_returns.release()
         for name in ("_unsub_ecl110_state", "_unsub_peak_guard", "_unsub_defrost"):
             unsub = getattr(self, name, None)
             setattr(self, name, None)
@@ -4034,7 +4049,6 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             "dhw_cost": 0.0,
             "total_cost": 0.0,
         }
-        self._last_energy_sample: datetime | None = None
         #: The date the lifetime accumulators started, restored from the
         #: energy store; set on first publish when the store has none.
         self._energy_totals_since: str | None = None
@@ -6674,14 +6688,12 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         # ``prior`` is the state the interval started from (the slab seed).
         prior = ctx._current_state
         state = replace(prior)
-        # Indoor temperature
         indoor = reader.read(CONF_INDOOR_TEMP_ENTITY)
         if indoor.ok:
             state.room_temperature = indoor.value
             # For two-zone: indoor sensor is typically upper floor
             state.upper_floor_temperature = indoor.value
 
-        # Outdoor temperature
         outdoor = reader.read(CONF_OUTDOOR_TEMP_ENTITY)
         if outdoor.ok:
             state.outdoor_temperature = outdoor.value
@@ -6693,7 +6705,6 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             # None (no forecast) keeps the default: the honest horizon.
             state.outdoor_temperature = forecast_outdoor
 
-        # Floor heating return temperature sensor
         floor_return = reader.read(CONF_FLOOR_RETURN_TEMP_ENTITY)
         if floor_return.ok:
             self._floor_return_temp = floor_return.value
@@ -6836,6 +6847,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         # The health snapshot has to be complete before any learner runs, since
         # each one consults it to decide whether to freeze.
         self._input_health = reader.health
+        self._input_returns.arm(reader.health)
         self._learner_freeze_reason = None
 
         # The defrost derate's humidity bucket is resolved from this, so it has
diff --git a/custom_components/heatpump_optimizer/inputs.py b/custom_components/heatpump_optimizer/inputs.py
index 4973c108d..05e746733 100644
--- a/custom_components/heatpump_optimizer/inputs.py
+++ b/custom_components/heatpump_optimizer/inputs.py
@@ -38,6 +38,7 @@ from __future__ import annotations
 
 import logging
 import math
+import time
 from dataclasses import dataclass, field
 from datetime import datetime, timedelta
 from collections.abc import Callable, Collection
@@ -906,8 +907,7 @@ class InputReader:
             reading.problem = "missing_entity"
             return reading, None
 
-        raw = getattr(state, "state", None)
-        if raw is None or str(raw).lower() in _INVALID_STATES:
+        if not has_value(state):
             reading.problem = "unavailable"
             return reading, None
 
@@ -1107,6 +1107,108 @@ class InputReader:
         return reading
 
 
+def has_value(state: Any) -> bool:
+    """Whether ``state`` carries a value at all, before any guard judges it."""
+    raw = getattr(state, "state", None) if state is not None else None
+    return raw is not None and str(raw).lower() not in _INVALID_STATES
+
+
+#: The problems a state event can show have cleared: the entity was not in the
+#: state machine, or held no value. Age, plausibility and units are judged by
+#: the re-read, never by the event.
+RETURN_WATCHED_PROBLEMS: frozenset[str] = frozenset({"missing_entity", "unavailable"})
+
+
+class InputReturnWatch:
+    """Ask for a re-read as soon as an input the last read could not use returns.
+
+    A configured entity absent at one read -- an MQTT entity discovery has not
+    re-created yet when this integration starts or reloads -- otherwise stayed
+    ``missing_entity`` until the next scheduled update, one
+    ``optimization_interval`` later, with every learner frozen and the planner
+    steering from the value pinned before it. The watch reads nothing itself:
+    ``request`` asks the owner for a refresh, so the returned value passes
+    every guard a scheduled read applies, and one they reject keeps the
+    learners frozen.
+
+    Its edges are injected, as the reader's clock is: ``track(entity_ids,
+    action)`` subscribes ``action`` to those entities' state changes and
+    returns the unsubscribe; ``request()`` asks for a refresh. So this module
+    imports no Home Assistant and holds no reference to its owner.
+
+    A request can be dropped: Home Assistant's debouncer discards a call while
+    a cycle is in flight. So a return stays pending until a read has run after
+    it (``arm`` is that read's snapshot), and only a re-read that ran starts the
+    ``spacing_s`` hold. A second return before that read asks again; one inside
+    ``spacing_s`` of a re-read asks for nothing, which bounds a sensor flapping
+    between ``unavailable`` and a value at one extra update per interval.
+    """
+
+    def __init__(
+        self,
+        track: Callable[[list[str], Callable[[Any], None]], Callable[[], None]],
+        request: Callable[[], Any],
+        spacing_s: float,
+        clock: Callable[[], float] = time.monotonic,
+    ) -> None:
+        self.track = track
+        self.request = request
+        self.spacing_s = float(spacing_s)
+        self.clock = clock
+        self.released = False
+        self._entities: frozenset[str] = frozenset()
+        self._unsub: Callable[[], None] | None = None
+        self._pending: set[str] = set()
+        self._reread_at: dict[str, float] = {}
+
+    def arm(self, health: InputHealth) -> None:
+        """Take a read's snapshot: settle what it re-read, watch what it lacked."""
+        if self.released:
+            return
+        now = self.clock()
+        for entity_id in self._pending:
+            self._reread_at[entity_id] = now
+        self._pending.clear()
+        wanted = frozenset(
+            reading.entity_id
+            for reading in health.readings.values()
+            if reading.entity_id and reading.problem in RETURN_WATCHED_PROBLEMS
+        )
+        if wanted == self._entities:
+            return
+        self._drop()
+        self._entities = wanted
+        if wanted:
+            self._unsub = self.track(sorted(wanted), self._on_event)
+
+    def _on_event(self, event: Any) -> None:
+        data = getattr(event, "data", {})
+        entity_id = data.get("entity_id")
+        if (
+            self.released
+            or entity_id not in self._entities
+            or not has_value(data.get("new_state"))
+        ):
+            return
+        reread = self._reread_at.get(entity_id)
+        if reread is not None and self.clock() - reread < self.spacing_s:
+            return
+        self._pending.add(entity_id)
+        self.request()
+
+    def _drop(self) -> None:
+        unsub, self._unsub = self._unsub, None
+        if unsub is not None:
+            unsub()
+
+    def release(self) -> None:
+        """Drop the listener for good; a later ``arm`` registers nothing (#236)."""
+        self.released = True
+        self._drop()
+        self._entities = frozenset()
+        self._pending.clear()
+
+
 def health_summary(stale_keys: Collection[str], missing_keys: Collection[str]) -> str:
     """One-line description from the two sets, so the wording has one owner.
 
diff --git a/dev/programme/delivery/3300.md b/dev/programme/delivery/3300.md
new file mode 100644
index 000000000..e4ad219fc
--- /dev/null
+++ b/dev/programme/delivery/3300.md
@@ -0,0 +1 @@
+- [#3300](https://github.com/tvofi/heatpump_optimizer/pull/3300) — **open**, R10-INPUT-REAPPEAR: input reappear (R10-INPUT-REAPPEAR)
diff --git a/tests/features.py b/tests/features.py
index 3b7d7df65..b873eda93 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -30519,6 +30519,351 @@ R.check(
 )
 
 
+R.section("A configured input that returns is re-read at once, not one interval later")
+
+# A live install's indoor sensor is a Zigbee2MQTT entity. After a restart or a
+# reload of this integration the first read ran before MQTT discovery had
+# re-created it, so the reading was `missing_entity` and every learner froze;
+# nothing read it again until the next scheduled update, one
+# `optimization_interval` (15 min there) later, although the entity was back
+# within seconds. `InputReturnWatch` asks for the coordinator's debounced
+# refresh as soon as an input the last read found absent or valueless reports
+# a value. The re-read goes through the real `_update_current_state` here, so
+# every guard a scheduled read applies applies to the returned value too.
+import gc as _ir_gc  # noqa: E402
+import weakref as _ir_weakref  # noqa: E402
+
+_IR_SPACING_S = 15 * 60.0
+
+
+def _ir_event(entity_id, state):
+    return type("Ev", (), {"data": {
+        "entity_id": entity_id, "old_state": None, "new_state": state}})()
+
+
+def _ir_fire(hass, entity_id, state):
+    for ids, action in list(getattr(hass, "state_listeners", [])):
+        if entity_id in ids:
+            action(_ir_event(entity_id, state))
+
+
+def _ir_rig(indoor=None, *, stub_refresh=True):
+    """A coordinator whose first read finds ``indoor`` (absent when None).
+
+    ``stub_refresh`` replaces the refresh with the cycle's input half (the
+    real read, every real guard); without it the real debounced
+    ``async_request_refresh`` is what a return reaches.
+    """
+    import homeassistant.util.dt as _ir_dt
+
+    states = {"sensor.outdoor": FakeState("-8.0", unit="°C", last_updated=_LF_T0)}
+    if indoor is not None:
+        states["sensor.indoor"] = indoor
+    hass = _FakeHass(states)
+    coord = Coord(hass, _FakeEntry(data={
+        "tibber_token": "x",
+        "weather_entity": "weather.home",
+        "indoor_temp_entity": "sensor.indoor",
+        "outdoor_temp_entity": "sensor.outdoor",
+        "optimization_interval": 15,
+    }))
+    coord._current_weather = lambda: (0.0, 0.0)
+    # Captured from here on: the construction's own loaders are not the watch.
+    tasks = []
+    hass.async_create_task = lambda coro, *a, **k: tasks.append(coro)
+    refreshes = []
+
+    async def _refresh():
+        refreshes.append(1)
+        await coord._update_current_state()
+
+    if stub_refresh:
+        coord.async_request_refresh = _refresh
+    clock = [1000.0]
+    # getattr: at a tree without the watch the checks below fail, not crash.
+    watch = getattr(coord, "_input_returns", None)
+    if watch is not None:
+        watch.clock = lambda: clock[0]
+    real = (_ir_dt.now, _ir_dt.utcnow)
+
+    def run(coro):
+        _ir_dt.now = _ir_dt.utcnow = lambda: _LF_T0
+        try:
+            _asyncio.run(coro)
+        finally:
+            _ir_dt.now, _ir_dt.utcnow = real
+
+    run(coord._update_current_state())
+
+    def run_tasks():
+        while tasks:
+            run(tasks.pop(0))
+
+    return coord, hass, tasks, refreshes, clock, run_tasks, run
+
+
+def _ir_watched(hass):
+    return sorted(
+        e for ids, _a in getattr(hass, "state_listeners", []) for e in ids)
+
+
+def _ir_indoor(coord):
+    return coord._input_health.readings["indoor_temp_entity"]
+
+
+_ir_c, _ir_h, _ir_tasks, _ir_refreshes, _ir_clock, _ir_run, _ir_do = _ir_rig()
+R.check(
+    "precondition: an indoor entity absent at the first read is missing_entity "
+    "and freezes the learners",
+    _ir_indoor(_ir_c).problem == "missing_entity"
+    and _ir_c._learning_frozen("indoor_temp_entity")
+    == "missing_entity:indoor_temp_entity",
+    f"got {_ir_c._learning_frozen('indoor_temp_entity')!r}",
+)
+R.check(
+    "the read that found it absent watches exactly that entity",
+    _ir_watched(_ir_h) == ["sensor.indoor"],
+    f"watched {_ir_watched(_ir_h)}",
+)
+# HA writes an `unavailable` placeholder for a registry entity whose
+# integration has not loaded; that is not a return.
+_ir_fire(_ir_h, "sensor.indoor", FakeState("unavailable", last_updated=_LF_T0))
+R.check(
+    "an entity that reappears without a value asks for nothing",
+    not _ir_tasks,
+    f"{len(_ir_tasks)} refreshes requested",
+)
+_ir_back = FakeState("21.3", unit="°C", last_updated=_LF_T0)
+_ir_h.states.set("sensor.indoor", _ir_back)
+_ir_fire(_ir_h, "sensor.indoor", _ir_back)
+R.check(
+    "the entity reporting a value asks for one refresh at once",
+    len(_ir_tasks) == 1,
+    f"{len(_ir_tasks)} refreshes requested",
+)
+_ir_run()
+R.check(
+    "that refresh re-reads it: the input is ok, the learners unfreeze, the "
+    "planner's room temperature is the reading",
+    _ir_refreshes == [1]
+    and _ir_indoor(_ir_c).ok
+    and _ir_c._learning_frozen("indoor_temp_entity") is None
+    and _ir_c._current_state.room_temperature == 21.3,
+    f"refreshes {_ir_refreshes}, "
+    f"frozen {_ir_c._learning_frozen('indoor_temp_entity')!r}, "
+    f"room {_ir_c._current_state.room_temperature}",
+)
+R.check(
+    "and with nothing absent any more nothing is watched",
+    _ir_watched(_ir_h) == [],
+    f"watched {_ir_watched(_ir_h)}",
+)
+
+# A flapping sensor: absent again at the next scheduled read, back within the
+# same interval. The hold runs from the re-read (at clock 1000.0), one
+# interval long, so one extra refresh per entity per interval, not one per flap.
+_ir_h.states._states.pop("sensor.indoor")
+_ir_do(_ir_c._update_current_state())
+_ir_clock[0] = 1000.0 + _IR_SPACING_S - 1.0
+_ir_fire(_ir_h, "sensor.indoor", _ir_back)
+R.check(
+    "a return one second short of an interval after the re-read asks for nothing",
+    not _ir_tasks and _ir_watched(_ir_h) == ["sensor.indoor"],
+    f"{len(_ir_tasks)} requested, watched {_ir_watched(_ir_h)}",
+)
+_ir_clock[0] = 1000.0 + _IR_SPACING_S
+_ir_fire(_ir_h, "sensor.indoor", _ir_back)
+R.check(
+    "a return exactly one interval after the re-read asks again",
+    len(_ir_tasks) == 1,
+    f"{len(_ir_tasks)} refreshes requested",
+)
+_ir_tasks.clear()
+
+# A return while a cycle is in flight. Home Assistant's debouncer discards a
+# call while it is executing; the real `async_request_refresh` meets the stub's
+# copy of that branch here. A request that never became a read must not start
+# the hold, or the next return would wait a whole interval.
+_ir_f, _ir_fh, _ir_ft, _ir_fr, _ir_fc, _ir_frun, _ir_fdo = _ir_rig(stub_refresh=False)
+_ir_fh.states.set("sensor.indoor", _ir_back)
+_ir_f._debounced_refresh._executing = True
+_ir_fire(_ir_fh, "sensor.indoor", _ir_back)
+_ir_asked = len(_ir_ft)
+_ir_frun()
+R.check(
+    "precondition: a return during an in-flight cycle is asked for and "
+    "dropped by the debouncer, so nothing was re-read",
+    _ir_asked == 1 and _ir_f.refresh_requests == 1
+    and _ir_indoor(_ir_f).problem == "missing_entity",
+    f"asked {_ir_asked}, requests {_ir_f.refresh_requests}, "
+    f"indoor {_ir_indoor(_ir_f).problem}",
+)
+_ir_f._debounced_refresh._executing = False
+_ir_fc[0] += 60.0
+_ir_fire(_ir_fh, "sensor.indoor", _ir_back)
+R.check(
+    "the next report after a dropped request asks again",
+    len(_ir_ft) == 1,
+    f"{len(_ir_ft)} refreshes requested",
+)
+for _ir_coro in _ir_ft:
+    _ir_coro.close()
+_ir_ft.clear()
+# The in-flight cycle read its inputs before the return arrived, so it cannot
+# settle it; the first read that runs after the return does (here the next
+# one), and that read starts the hold.
+_ir_fdo(_ir_f._update_current_state())
+_ir_fh.states._states.pop("sensor.indoor")
+_ir_fdo(_ir_f._update_current_state())
+_ir_fc[0] += 60.0
+_ir_fire(_ir_fh, "sensor.indoor", _ir_back)
+R.check(
+    "a read after the return settles it: the next return inside the hold "
+    "asks for nothing",
+    not _ir_ft,
+    f"{len(_ir_ft)} refreshes requested",
+)
+
+# The guards still decide. A value twelve hours old comes back: the re-read
+# runs, rejects it as stale, and the learners stay frozen.
+_ir_s, _ir_sh, _ir_st, _ir_sr, _ir_sc, _ir_srun, _ = _ir_rig()
+_ir_old = FakeState("21.0", unit="°C", last_updated=_LF_T0 - timedelta(hours=12))
+_ir_sh.states.set("sensor.indoor", _ir_old)
+_ir_fire(_ir_sh, "sensor.indoor", _ir_old)
+_ir_srun()
+R.check(
+    "a returned value the guards reject is re-read and keeps the learners "
+    "frozen",
+    _ir_sr == [1]
+    and _ir_s._learning_frozen("indoor_temp_entity") == "stale:indoor_temp_entity",
+    f"refreshes {_ir_sr}, got {_ir_s._learning_frozen('indoor_temp_entity')!r}",
+)
+
+# `unavailable` is watched as `missing_entity` is: an entity HA holds, with no
+# value, that then reports one.
+_ir_u, _ir_uh, _ir_ut, _ir_ur, _ir_uc, _ir_urun, _ = _ir_rig(
+    FakeState("unavailable", unit="°C", last_updated=_LF_T0))
+_ir_uh.states.set("sensor.indoor", _ir_back)
+_ir_fire(_ir_uh, "sensor.indoor", _ir_back)
+_ir_urun()
+R.check(
+    "an input read as unavailable is watched and re-read when it reports a value",
+    _ir_watched(_ir_uh) == [] and _ir_ur == [1] and _ir_indoor(_ir_u).ok,
+    f"refreshes {_ir_ur}, indoor {_ir_indoor(_ir_u).problem}",
+)
+
+# Released with the entry (#236): the listener goes, and no later read re-arms.
+_ir_r, _ir_rh, _ir_rt, _ir_rr, _ir_rc, _ir_rrun, _ir_rdo = _ir_rig()
+_ir_r._release_registrations()
+_ir_released = _ir_watched(_ir_rh)
+_ir_rdo(_ir_r._update_current_state())
+R.check(
+    "releasing the entry drops the watch, and a read after it registers none",
+    _ir_released == [] and _ir_watched(_ir_rh) == [],
+    f"after release {_ir_released}, after a later read {_ir_watched(_ir_rh)}",
+)
+# And nothing the watch holds keeps the coordinator alive: a module-level
+# table keyed by the coordinator, whose value held its bound refresh, pinned
+# every coordinator for the life of the process -- one per reload and per
+# ConfigEntryNotReady retry.
+_ir_ref = _ir_weakref.ref(_ir_r)
+del _ir_r, _ir_rh, _ir_rt, _ir_rr, _ir_rc, _ir_rrun, _ir_rdo
+_ir_gc.collect()
+R.check(
+    "a released coordinator is collected",
+    _ir_ref() is None,
+    f"{len(_ir_gc.get_referrers(_ir_ref()))} referrers" if _ir_ref() else "",
+)
+
+# NULL CONTROL: a healthy install carries no listener at all, so the watch
+# cannot be what every healthy read pays for.
+_ir_n, _ir_nh, _ir_nt, *_ = _ir_rig(
+    FakeState("21.0", unit="°C", last_updated=_LF_T0))
+R.check(
+    "null control: a read with every configured input usable watches nothing",
+    _ir_indoor(_ir_n).ok and _ir_watched(_ir_nh) == [] and not _ir_nt,
+    f"watched {_ir_watched(_ir_nh)}",
+)
+# A design choice, pinned: only absence and no-value are watched. A sensor
+# reporting a word (or a fault code, or a unit the reader cannot convert) is
+# present and reporting, and a stale one re-reported unchanged fires no state
+# change at all; an event vouches for nothing the re-read could accept, so
+# watching either would buy one extra update per interval while it stays so.
+_ir_w, _ir_wh, *_ = _ir_rig(FakeState("warm", unit="°C", last_updated=_LF_T0))
+R.check(
+    "a present input with an unusable value (not_numeric) is not watched",
+    _ir_indoor(_ir_w).problem == "not_numeric" and _ir_watched(_ir_wh) == [],
+    f"watched {_ir_watched(_ir_wh)}",
+)
+_ir_o, _ir_oh, *_ = _ir_rig(
+    FakeState("21.0", unit="°C", last_updated=_LF_T0 - timedelta(hours=12)))
+R.check(
+    "a stale input is not watched",
+    _ir_indoor(_ir_o).problem == "stale" and _ir_watched(_ir_oh) == [],
+    f"watched {_ir_watched(_ir_oh)}",
+)
+
+# The watch itself, driven with a fake clock and a counting tracker, so the
+# bookkeeping a whole-coordinator read cannot see is pinned too.
+from heatpump_optimizer.inputs import (  # noqa: E402
+    InputHealth as _IrHealth,
+    InputReading as _IrReading,
+    InputReturnWatch as _IrWatch,
+)
+
+
+def _ir_unit():
+    log = {"track": [], "unsub": 0, "req": 0, "t": 0.0, "cb": None}
+
+    def track(ids, cb):
+        log["track"].append(list(ids))
+        log["cb"] = cb
+
+        def unsub():
+            log["unsub"] += 1
+        return unsub
+
+    def request():
+        log["req"] += 1
+
+    w = _IrWatch(track, request, _IR_SPACING_S, clock=lambda: log["t"])
+    return w, log
+
+
+def _ir_health(*ids):
+    h = _IrHealth()
+    for i in ids:
+        h.record(_IrReading(key=i, entity_id=i, problem="missing_entity"))
+    return h
+
+
+_ir_w1, _ir_l1 = _ir_unit()
+_ir_w1.arm(_ir_health("sensor.a"))
+_ir_w1.arm(_ir_health("sensor.a"))
+R.check(
+    "an unchanged watched set neither re-registers nor drops the listener",
+    _ir_l1["track"] == [["sensor.a"]] and _ir_l1["unsub"] == 0,
+    f"{_ir_l1['track']} unsub {_ir_l1['unsub']}",
+)
+
+# The re-read stamp is the arm that follows the request, not a later arm.
+_ir_w2, _ir_l2 = _ir_unit()
+_ir_w2.arm(_ir_health("sensor.a"))
+_ir_l2["t"] = 10.0
+_ir_l2["cb"](_ir_event("sensor.a", FakeState("1.0")))
+_ir_l2["t"] = 20.0
+_ir_w2.arm(_ir_health("sensor.a"))  # stamps the re-read at t=20
+_ir_l2["t"] = 5000.0
+_ir_w2.arm(_ir_health("sensor.a"))  # nothing pending: must not restamp
+_ir_l2["t"] = 20.0 + _IR_SPACING_S
+_ir_l2["cb"](_ir_event("sensor.a", FakeState("1.0")))
+R.check(
+    "a settled request is stamped once; a later arm does not push the spacing out",
+    _ir_l2["req"] == 2,
+    f"requests {_ir_l2['req']}",
+)
+
+
 # ===========================================================================
 # v5.1.7 — an ordinary slot stops calling itself weather pre-heating
 # ===========================================================================
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_track_states.RETURN_DEL.da09b9a2.json b/tests/mutation_ledger/killed_by/coordinator.py/_track_states.RETURN_DEL.da09b9a2.json
new file mode 100644
index 000000000..fbbeaa8e4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_track_states.RETURN_DEL.da09b9a2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_track_states RETURN_DEL da09b9a2",
+  "killed_by": "tests/features.py",
+  "old": "    return async_track_state_change_event(hass, entity_ids, callback(lambda event: action(event)))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReader._begin.GUARD_OFF.c5567f15.json b/tests/mutation_ledger/killed_by/inputs.py/InputReader._begin.GUARD_OFF.c5567f15.json
new file mode 100644
index 000000000..69817334c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/InputReader._begin.GUARD_OFF.c5567f15.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReader._begin GUARD_OFF c5567f15",
+  "killed_by": "tests/features.py",
+  "old": "        if not has_value(state):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=15."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReader._begin.GUARD_OFF.d3150a8e.json b/tests/mutation_ledger/killed_by/inputs.py/InputReader._begin.GUARD_OFF.d3150a8e.json
deleted file mode 100644
index f9f4f8853..000000000
--- a/tests/mutation_ledger/killed_by/inputs.py/InputReader._begin.GUARD_OFF.d3150a8e.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReader._begin GUARD_OFF d3150a8e",
-  "killed_by": "tests/structure.py",
-  "old": "        if raw is None or str(raw).lower() in _INVALID_STATES:",
-  "reason": "Recorded by `mutation_table.py --drain` against aca6ea4567034a05e64edcfd8355d42a8079427d: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._drop.GUARD_OFF.7bdf1e66.json b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._drop.GUARD_OFF.7bdf1e66.json
new file mode 100644
index 000000000..b8940b6d9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._drop.GUARD_OFF.7bdf1e66.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReturnWatch._drop GUARD_OFF 7bdf1e66",
+  "killed_by": "tests/features.py",
+  "old": "        if unsub is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._on_event.BOOLOP.c43e9ddb.json b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._on_event.BOOLOP.c43e9ddb.json
new file mode 100644
index 000000000..5a9164031
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._on_event.BOOLOP.c43e9ddb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReturnWatch._on_event BOOLOP c43e9ddb",
+  "killed_by": "tests/features.py",
+  "old": "        if reread is not None and self.clock() - reread < self.spacing_s:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if reread is not None or self.clock() - reread < self.spacing_s:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._on_event.CMP_BOUND.c43e9ddb.json b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._on_event.CMP_BOUND.c43e9ddb.json
new file mode 100644
index 000000000..ea8461555
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._on_event.CMP_BOUND.c43e9ddb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReturnWatch._on_event CMP_BOUND c43e9ddb",
+  "killed_by": "tests/features.py",
+  "old": "        if reread is not None and self.clock() - reread < self.spacing_s:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if reread is not None and self.clock() - reread <= self.spacing_s:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._on_event.GUARD_OFF.c43e9ddb.json b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._on_event.GUARD_OFF.c43e9ddb.json
new file mode 100644
index 000000000..82062e88b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch._on_event.GUARD_OFF.c43e9ddb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReturnWatch._on_event GUARD_OFF c43e9ddb",
+  "killed_by": "tests/features.py",
+  "old": "        if reread is not None and self.clock() - reread < self.spacing_s:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.BOOLOP.7ca77e31.json b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.BOOLOP.7ca77e31.json
new file mode 100644
index 000000000..7ad67bec4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.BOOLOP.7ca77e31.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReturnWatch.arm BOOLOP 7ca77e31",
+  "killed_by": "tests/features.py",
+  "old": "            if reading.entity_id and reading.problem in RETURN_WATCHED_PROBLEMS",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if reading.entity_id or reading.problem in RETURN_WATCHED_PROBLEMS`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.GUARD_OFF.21834646.json b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.GUARD_OFF.21834646.json
new file mode 100644
index 000000000..0d93bec74
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.GUARD_OFF.21834646.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReturnWatch.arm GUARD_OFF 21834646",
+  "killed_by": "tests/features.py",
+  "old": "        if wanted:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.GUARD_OFF.6f7a9fe0.json b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.GUARD_OFF.6f7a9fe0.json
new file mode 100644
index 000000000..fa280a035
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.GUARD_OFF.6f7a9fe0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReturnWatch.arm GUARD_OFF 6f7a9fe0",
+  "killed_by": "tests/features.py",
+  "old": "        if self.released:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.GUARD_OFF.ecb87ca6.json b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.GUARD_OFF.ecb87ca6.json
new file mode 100644
index 000000000..1409d6c4c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/InputReturnWatch.arm.GUARD_OFF.ecb87ca6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReturnWatch.arm GUARD_OFF ecb87ca6",
+  "killed_by": "tests/features.py",
+  "old": "        if wanted == self._entities:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/has_value.BOOLOP.1f655796.json b/tests/mutation_ledger/killed_by/inputs.py/has_value.BOOLOP.1f655796.json
new file mode 100644
index 000000000..6b7be9575
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/has_value.BOOLOP.1f655796.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:has_value BOOLOP 1f655796",
+  "killed_by": "tests/features.py",
+  "old": "    return raw is not None and str(raw).lower() not in _INVALID_STATES",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return raw is not None or str(raw).lower() not in _INVALID_STATES`) took tests/features.py from rc=0 failed=0 to rc=1 failed=18."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/has_value.RETURN_DEL.1f655796.json b/tests/mutation_ledger/killed_by/inputs.py/has_value.RETURN_DEL.1f655796.json
new file mode 100644
index 000000000..09a8b5381
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/has_value.RETURN_DEL.1f655796.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:has_value RETURN_DEL 1f655796",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    return raw is not None and str(raw).lower() not in _INVALID_STATES",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=3."
+}

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
