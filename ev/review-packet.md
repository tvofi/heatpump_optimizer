# Review packet #3845
head: e82a26569c3d27015f74627c8e25bca42d89ce58
base: f269ecccb5f1dfd21eca03a3d5dcc43b3a145603

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=137110075897 success
arch-score / arch-score id=137107458027 success
budget-raise-gate / budget-raise-gate id=137107458110 success
cancel-superseded id=137106354055 skipped
codeql / Analyze (actions) id=137107458035 success
codeql / Analyze (javascript-typescript) id=137107458217 success
codeql / Analyze (python) id=137107458112 success
governance / env-matrix id=137107458103 success
governance / instrument-self-tests id=137107458102 success
governance / policy-docs id=137107458063 success
governance / record id=137107459516 skipped
governance / wave-script id=137107458133 success
hassfest / hassfest id=137107457969 success
kernel-points id=137107458829 skipped
prelude id=137106353189 success
refresh id=137106353386 success
tests / arch-instrument id=137109232345 in_progress
tests / briefs id=137107458087 success
tests / browser id=137109232295 success
tests / closure-scope id=137107458106 success
tests / closures id=137109232421 in_progress
tests / coverage id=137109232420 in_progress
tests / coverage-ratchet id=137118261680 success
tests / fast (3.14) id=137109232350 in_progress
tests / graders-head-copy id=137118262903 skipped
tests / mutation id=137107458109 failure
tests / mutation-autofix id=137108415427 skipped
tests / mutation-pins id=137108415257 skipped
tests / mutation-pins (1) id=137109204354 in_progress
tests / mutation-pins (2) id=137109204361 in_progress
tests / nightly-ha id=137109233682 skipped
tests / nightly-status id=137107458094 success
tests / replay id=137109232356 in_progress
tests / typing id=137109232338 success
validate / validate-hacs id=137107457965 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified - `config_flow.py` `validate_tibber_token` (`'cannot_connect'`);
             no segment of this names a program this check knows
  unverified - `coordinator.py` `_valve_write_problem` (the problem text);
             no segment of this names a program this check knows
  unverified - `debugger.py` `run_self_tests` (`outcome['error']`) and `_async_replay` (the reason string);
             no segment of this names a program this check knows
  unverified - `off_restore.py` `_restore_baseline` (`sent, err`);
             no segment of this names a program this check knows
  unverified - `optimizer.py` `_multi_start_minimize` (`last_error`, raised once every start fails);
             no segment of this names a program this check knows
  unverified - `process_worker.py` `_describe`, `_dump` and both of `run_worker`'s arms (the child's status payload, which the parent raises).
             no segment of this names a program this check knows
  unverified - `features.py`: "every raised exception key exists in strings.json and every translation", because the new key was missing from the census's `_ET_KEYS`;
             no segment of this names a program this check knows
  unverified - `entities.py`: the P6 G probe on `__qualname__`, and the N-log-flood reasoned list still counting both update arms;
             no segment of this names a program this check knows
  unverified - `arch_score_head.py`: `CYCLE_HUB_WRITERS`' stale `_apply_comfort_weight` row;
             no segment of this names a program this check knows
  unverified - `typing_ruler.py`: one `union-attr` on `ctx.publish_config`;
             no segment of this names a program this check knows
  unverified - `structure.py`: exit 2, two unrecorded gains.
             no segment of this names a program this check knows
  unverified - `structure.py`: `STRUCTURE RATCHET PASSED`;
             no segment of this names a program this check knows
  unverified - `typing_ruler.py`: `ALL 12 typing-ruler source checks PASSED`, with `HPO_TYPING_PYTHON=/opt/hpo/venv-ha/bin/python`, the pinned mypy 2.4.1;
             no segment of this names a program this check knows
  unverified - `arch_score_head.py`: `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED`;
             no segment of this names a program this check knows
  unverified - `doc_claims.py`: `ALL 443 checks PASSED`;
             no segment of this names a program this check knows
  unverified - `entities.py`: `ALL 2736 ENTITY CHECKS PASSED`;
             no segment of this names a program this check knows
  unverified - `features.py`: `ALL 6000 FEATURE CHECKS PASSED`.
             no segment of this names a program this check knows
  unverified MODE: SCOPED -- 28 script(s) run, 5 scoped out.
             no segment of this names a program this check knows
  unverified git archive dbdc1d95fef3 dev/audit/rounds/round11
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/<path>
             the path `$EXPORT/dev/audit/rounds/round11/<path>` is a template or an expansion, not a literal
  unverified git diff 29f755a5c6 7dd02c4135 -- custom_components
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=a8efe1d1c2a8 ./tests/run.sh
             `tests/run.sh` is in the tree at this head
  unverified PYTHONPATH=tests/hastub python3 tests/<script>.py
             the path `tests/<script>.py` is a template or an expansion, not a literal
  ok         python3 tests/structure.py --record
             `tests/structure.py` is in the tree at this head

FIGURES: 2 resolved, 22 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/away.py/clears_return_time.RETURN_DEL.05ea228a.json b/tests/mutation_ledger/killed_by/away.py/clears_return_time.RETURN_DEL.05ea228a.json
new file mode 100644
index 0000000000..d78b5e7562
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/away.py/clears_return_time.RETURN_DEL.05ea228a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/away.py:clears_return_time RETURN_DEL 05ea228a",
+  "killed_by": "tests/features.py",
+  "old": "    return not raw or str(raw).strip().lower() in (\"unknown\", \"unavailable\", \"\")",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/away.py/_parse_return_time.RETURN_DEL.17d5e3f1.json b/tests/mutation_ledger/killed_by/away.py/parse_return_time.RETURN_DEL.17d5e3f1.json
similarity index 75%
rename from tests/mutation_ledger/killed_by/away.py/_parse_return_time.RETURN_DEL.17d5e3f1.json
rename to tests/mutation_ledger/killed_by/away.py/parse_return_time.RETURN_DEL.17d5e3f1.json
index 1e453ff9e6..f8ff08a66d 100644
--- a/tests/mutation_ledger/killed_by/away.py/_parse_return_time.RETURN_DEL.17d5e3f1.json
+++ b/tests/mutation_ledger/killed_by/away.py/parse_return_time.RETURN_DEL.17d5e3f1.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/away.py:_parse_return_time RETURN_DEL 17d5e3f1",
+  "anchor": "custom_components/heatpump_optimizer/away.py:parse_return_time RETURN_DEL 17d5e3f1",
   "killed_by": "tests/features.py",
   "old": "    return stored_instant(value, dt_util.DEFAULT_TIME_ZONE)",
   "reason": "Recorded by `mutation_table.py --pin-killed` against db878b29fa301d44231ccec55a85a80d610e9b1e: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=16."
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.RETURN_DEL.35324698.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.RETURN_DEL.35324698.json
deleted file mode 100644
index e1d1c1d0fa..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.RETURN_DEL.35324698.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_first_refresh_light RETURN_DEL 35324698",
-  "killed_by": "tests/features.py",
-  "old": "            return self._build_data_dict()",
-  "reason": "Recorded by `mutation_table.py --drain` against e8c67e1d3df151a8f273443a5ac5f736fb543782: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_update_data.RETURN_DEL.3bda3d97.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_update_data.RETURN_DEL.3bda3d97.json
deleted file mode 100644
index 3fe0fdd542..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_update_data.RETURN_DEL.3bda3d97.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_update_data RETURN_DEL 3bda3d97",
-  "killed_by": "tests/features.py",
-  "old": "            return await _with_sensor_advisor(self, self._build_data_dict())",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 830f84ad7a25453248a7709f4dfd13769b2d9684: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capture_diagnosis_inputs.RETURN_DEL.440ee7e3.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capture_diagnosis_inputs.RETURN_DEL.440ee7e3.json
new file mode 100644
index 0000000000..ee780882cb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capture_diagnosis_inputs.RETURN_DEL.440ee7e3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._capture_diagnosis_inputs RETURN_DEL 440ee7e3",
+  "killed_by": "tests/features.py",
+  "old": "            return None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_lbfgsb_restart.RETURN_DEL.9f13e26c.json b/tests/mutation_ledger/killed_by/optimizer.py/_lbfgsb_restart.RETURN_DEL.9f13e26c.json
new file mode 100644
index 0000000000..e85e4e5c38
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_lbfgsb_restart.RETURN_DEL.9f13e26c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_lbfgsb_restart RETURN_DEL 9f13e26c",
+  "killed_by": "tests/features.py",
+  "old": "        return best",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/store.py/save_held.RETURN_DEL.80a0007e.json b/tests/mutation_ledger/killed_by/store.py/save_held.RETURN_DEL.80a0007e.json
new file mode 100644
index 0000000000..cc4ed99a32
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/store.py/save_held.RETURN_DEL.80a0007e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/store.py:save_held RETURN_DEL 80a0007e",
+  "killed_by": "tests/features.py",
+  "old": "    return True",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/survivor_triage/away.py/parse_return_time.GUARD_OFF.48f338a4.json b/tests/mutation_ledger/survivor_triage/away.py/parse_return_time.GUARD_OFF.48f338a4.json
new file mode 100644
index 0000000000..6d4cb54af6
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/away.py/parse_return_time.GUARD_OFF.48f338a4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/away.py:parse_return_time GUARD_OFF 48f338a4",
+  "old": "    if clears_return_time(raw):",
+  "reason": "Equivalent. With the guard off, a clearing value falls through to stored_instant(str(raw).strip(), zone), which returns None for every clearing spelling clears_return_time admits (None, '', 'unknown', 'unavailable', any case or padding), measured at the R11-SEAM-cycle-reporting head through heatpump_optimizer.drift.stored_instant; parse_return_time returns None either way. The set_away refusal calls clears_return_time itself, so the guard decides no refusal.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/coordinator.py/_stored_fuse_advisor.RETURN_DEL.d7923b87.json b/tests/mutation_ledger/survivor_triage/coordinator.py/_stored_fuse_advisor.RETURN_DEL.d7923b87.json
new file mode 100644
index 0000000000..2a2cb71e75
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/coordinator.py/_stored_fuse_advisor.RETURN_DEL.d7923b87.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_stored_fuse_advisor RETURN_DEL d7923b87",
+  "old": "        return None",
+  "reason": "Equivalent. The return is the last statement of the except arm, and nothing follows the try in _stored_fuse_advisor, so deleting it falls off the end of the coroutine, which returns None: the value the deleted line returned.",
+  "verdict": "equivalent"
+}


## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/away.py b/custom_components/heatpump_optimizer/away.py
index 621a595565..28f41b8590 100644
--- a/custom_components/heatpump_optimizer/away.py
+++ b/custom_components/heatpump_optimizer/away.py
@@ -20,7 +20,6 @@ a margin before the stated return, and the estimate itself is rounded up.
 """
 from __future__ import annotations
 
-import logging
 from collections.abc import Awaitable, Callable, Mapping
 from dataclasses import dataclass, replace
 from datetime import date, datetime, timedelta
@@ -35,7 +34,7 @@ from .drift import stored_instant
 from .entry_config import EntryConfig
 from .const import finite_float
 from .payload import AwayView
-from .store import QuarantiningStore, load_mapping
+from .store import QuarantiningStore, load_mapping, save_held
 
 from .const import (
     CONF_AWAY_DHW_MIN_TEMP,
@@ -50,7 +49,6 @@ from .const import (
     ECONOMY_ABSOLUTE_FLOOR,
 )
 
-_LOGGER = logging.getLogger(__name__)
 AWAY_STORE_VERSION = 1
 OMIT = object()
 
@@ -319,7 +317,7 @@ def migrate_helper_override(
         active = interpret_presence(
             presence_raw, presence_entity, presence_attributes
         ) is True
-    parsed = _parse_return_time(return_raw)
+    parsed = parse_return_time(return_raw)
     return {
         "active": active,
         "return_time": parsed.isoformat() if parsed else None,
@@ -420,7 +418,7 @@ def _override_payload(state: AwayState) -> dict[str, Any]:
 
 def apply_override_payload(state: AwayState, payload: dict[str, Any]) -> AwayState:
     """``state`` with the stored override in it; ``state`` itself is not written."""
-    parsed = _parse_return_time(payload.get("return_time"))
+    parsed = parse_return_time(payload.get("return_time"))
     return replace(state, override_active=bool(payload.get("active")),
                    override_return_iso=parsed.isoformat() if parsed else None,
                    migrated_helpers=bool(payload.get("migrated_helpers")))
@@ -434,10 +432,9 @@ def published_under(state: AwayState, view: Mapping[str, Any]) -> bool:
 
 async def persist_override(coord: _AwayCoord, state: AwayState) -> None:
     """Save ``state`` -- the coordinator's away state, passed in (#1739)."""
-    try:
-        await _away_store(coord).async_save(_override_payload(state))
-    except Exception as err:  # noqa: BLE001
-        _LOGGER.debug("Could not persist away override: %s", err)
+    await save_held(
+        coord, "away override", lambda: _away_store(coord).async_save(_override_payload(state)),
+    )
 
 
 async def restore_override(
@@ -455,7 +452,7 @@ async def restore_override(
     payload = empty_override()
     if raw is not None:
         payload["active"] = bool(raw.get("active"))
-        parsed = _parse_return_time(raw.get("return_time"))
+        parsed = parse_return_time(raw.get("return_time"))
         payload["return_time"] = parsed.isoformat() if parsed else None
         payload["migrated_helpers"] = bool(raw.get("migrated_helpers"))
     if not payload["migrated_helpers"]:
@@ -558,14 +555,14 @@ async def resolve(
     state.target_temperature = config.away_temperature
     state.dhw_min_temperature = config.away_dhw_min_temperature
 
-    return_time = _parse_return_time(return_raw)
+    return_time = parse_return_time(return_raw)
     if return_time is None and presence_attributes:
         # A calendar event carries its own end time, which is a better return
         # estimate than anything the user would type twice.
         for key in ("end_time", "end", "next_event_end"):
             candidate = presence_attributes.get(key)
             if candidate:
-                return_time = _parse_return_time(str(candidate))
+                return_time = parse_return_time(str(candidate))
                 if return_time is not None:
                     break
     if return_time is None:
@@ -575,10 +572,10 @@ async def resolve(
 
 
 def _holiday_span(attrs: Mapping[str, Any], now: datetime) -> tuple[date, date]:
-    start = _parse_return_time(
+    start = parse_return_time(
         str(attrs.get("start_time") or attrs.get("start") or "")
     )
-    end = _parse_return_time(str(attrs.get("end_time") or attrs.get("end") or ""))
+    end = parse_return_time(str(attrs.get("end_time") or attrs.get("end") or ""))
     if start is None:
         start = now
     if end is None:
@@ -619,12 +616,22 @@ def _holiday_days(state: Any, now: datetime) -> frozenset[date]:
     return frozenset(days)
 
 
-def _parse_return_time(raw: str | None) -> datetime | None:
-    if not raw:
+def clears_return_time(raw: Any) -> bool:
+    """Whether ``raw`` is the absent return time: empty, or an unknown state."""
+    return not raw or str(raw).strip().lower() in ("unknown", "unavailable", "")
+
+
+def parse_return_time(raw: str | None) -> datetime | None:
+    """The return instant ``raw`` names; ``None`` when it clears it or does not parse.
+
+    The one parser of a return time (ADR-008): the restore, the helper
+    entities, the coordinator, the datetime entity and the ``set_away``
+    service, which refuses a value that neither clears nor parses
+    (D10-s1-01) rather than storing it as the absent time.
+    """
+    if clears_return_time(raw):
         return None
     value = str(raw).strip()
-    if value.lower() in ("unknown", "unavailable", ""):
-        return None
     # A typed time has no offset (the card's datetime-local, a time typed
     # into the service form): it is the user's wall clock, so it loads in
     # their zone.
diff --git a/custom_components/heatpump_optimizer/boost.py b/custom_components/heatpump_optimizer/boost.py
index 7a54506a89..975b5a861c 100644
--- a/custom_components/heatpump_optimizer/boost.py
+++ b/custom_components/heatpump_optimizer/boost.py
@@ -17,7 +17,6 @@ applied to a copy of it, and the switches call in.
 from __future__ import annotations
 
 import asyncio
-import logging
 import math
 from collections.abc import Callable, Coroutine, Mapping
 from dataclasses import dataclass, field
@@ -25,7 +24,7 @@ from datetime import datetime, timedelta
 from typing import Any, Protocol
 from weakref import WeakKeyDictionary
 
-from .store import QuarantiningStore, load_mapping
+from .store import QuarantiningStore, load_mapping, save_held
 from homeassistant.util import dt as dt_util
 
 from . import away as away_mode
@@ -43,7 +42,6 @@ from .drift import stored_instant
 from .entity import has_hot_water
 from .payload import CurrentAction, REASON_BOOST, REASON_LEGIONELLA
 
-_LOGGER = logging.getLogger(__name__)
 BOOST_STORE_VERSION = 1
 BOOST_HOURS = 2
 #: A block is the opposite of a boost: the same two hours, the duty zeroed.
@@ -569,10 +567,9 @@ def _store_payload(held: BoostState) -> dict[str, Any]:
 
 
 async def persist(coord: _BoostCoord) -> None:
-    try:
-        await _store(coord).async_save(_store_payload(held_for(coord)))
-    except Exception as err:  # noqa: BLE001
-        _LOGGER.debug("Could not persist boost state: %s", err)
+    await save_held(
+        coord, "boost state", lambda: _store(coord).async_save(_store_payload(held_for(coord))),
+    )
 
 
 async def restore(coord: Any) -> None:
diff --git a/custom_components/heatpump_optimizer/config_flow.py b/custom_components/heatpump_optimizer/config_flow.py
index 24858c41b9..3cd68a211a 100644
--- a/custom_components/heatpump_optimizer/config_flow.py
+++ b/custom_components/heatpump_optimizer/config_flow.py
@@ -793,7 +793,7 @@ def _prefilled_values(marker: Any) -> list[Any]:
         try:
             values.append(default())
         except Exception:  # noqa: BLE001 - a broken default is not our business
-            pass
+            _LOGGER.debug("A field default raised; not prefilled", exc_info=True)
     return values
 
 
@@ -2531,6 +2531,7 @@ def _omit_unstored_computed(
         try:
             computed = row.default.of(saving, hass)
         except Exception:  # noqa: BLE001 - leave a value we cannot recompute
+            _LOGGER.debug("Computed default %s not recomputed; value kept", row.key, exc_info=True)
             continue
         if _same_setting(computed, cleaned[row.key]):
             del cleaned[row.key]
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index 4dbd33b29a..aea69c249e 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -90,7 +90,7 @@ from .payload import (
     SpacePlan,
     ThermalView,
 )
-from .store import LedgerStore, QuarantiningStore, admitted, load_mapping
+from .store import LedgerStore, QuarantiningStore, admitted, load_mapping, save_held
 from .entry_config import EntryConfig, factory_settings, undo_point, undone_settings
 from homeassistant.util import dt as dt_util
 
@@ -2646,6 +2646,14 @@ class CoordinatorContext:
         new = replace(self._current_state if state is None else state, **fields)
         coord._ctx = replace(self, _current_state=new)
 
+    def publish_config(self, coord: Any, /, **fields: Any) -> None:
+        """Publish ``fields`` on ``coord`` in a new optimization config, whole (ADR-003).
+
+        D7-s2-03: the target and comfort-weight writers edited the shared
+        config in place, so every context published since setup saw the edit.
+        """
+        coord._ctx = replace(self, _opt_config=replace(self._opt_config, **fields))
+
 
 @dataclass(frozen=True)
 class CoordinatorDiagnostics:
@@ -2685,6 +2693,7 @@ class CoordinatorDiagnostics:
             try:
                 summaries[name.lstrip("_")] = summary()
             except Exception:  # noqa: BLE001 -- diagnostics never breaks
+                _LOGGER.debug("%s summary unavailable", name, exc_info=True)
                 summaries[name.lstrip("_")] = "summary unavailable"
         return cls(
             tibber_outage_cycles=getattr(coord, "_tibber_outage_cycles", None),
@@ -3047,6 +3056,7 @@ async def _stored_fuse_advisor(
             stored["fuse_advisor_at"], dt_util.DEFAULT_TIME_ZONE
         )
     except Exception:  # noqa: BLE001
+        _LOGGER.debug("Stored fuse advice unreadable; not restored", exc_info=True)
         return None
 
 
@@ -3466,6 +3476,8 @@ def _tail_freeze(coord: Any) -> str | None:
 class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
     """Coordinator for Heat Pump Cost Optimizer."""
 
+    config_entry: HeatPumpOptimizerConfigEntry  # the typed entry (D10-s3-02)
+
     _config = _hub("_config")
     _thermal_params = _hub("_thermal_params")
     _current_state = _hub("_current_state")
@@ -4112,6 +4124,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             action=self._current_action,
             measured_power_kw=pump_arbiter.live_power_kw(self.hass, ctx._config),
             defrosting=self._pump_signals.defrosting,
+            opt_config=ctx._opt_config,
             draw=self._accuracy.draw,
             disinfecting=getattr(
                 getattr(self._legionella, "disinfect", None), "memo", None
@@ -4227,7 +4240,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
                     "violations": comfort_band.describe(found)
                 },
             )
-        ctx._opt_config.target_temp = temperature
+        CoordinatorContext.publish_config(_ctx_of(self), self, target_temp=temperature)
         self.hass.config_entries.async_update_entry(
             self.entry,
             options={**self.entry.options, CONF_TARGET_TEMP: temperature},
@@ -4742,14 +4755,13 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
 
     async def _async_save_thermal_learning(self) -> None:
         """Persist the learned buffer and building parameters."""
-        try:
+        async def save() -> None:
             # D1-s2-52: wait before the payload; one built in flight is stale.
             await self._thermal_learning_store.async_wait_for_read()
             await self._thermal_learning_store.async_save(
                 self._thermal_learning_payload()
             )
-        except Exception as err:
-            _LOGGER.debug("Could not persist learned thermal parameters: %s", err)
+        await save_held(self._thermal_learning_store, "learned thermal parameters", save)
 
     def _dhw_confidence_band(
         self, dhw_temp: list[float | None], dt_hours: float
@@ -6103,7 +6115,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
                 minutes=ctx._config.optimization_interval
             ))
 
-            return await _with_sensor_advisor(self, self._build_data_dict())
+            payload = await _with_sensor_advisor(self, self._build_data_dict())
+            log_held(self.entry, _UPDATE_FAILED, False)
+            return payload
         except (UpdateFailed, ConfigEntryAuthFailed):
             # #216 (D10-09): the raiser — the Tibber outage latch — already
             # logged this failure once, at the severity its state machine
@@ -6112,10 +6126,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             # day-long outage printed the same ERROR on every cycle.
             raise
         except Exception as err:
-            _LOGGER.error(
-                "Error updating Heat Pump Optimizer: %s", err, exc_info=True
-            )
-            _raise_update_failed("update_failed", f"Error updating data: {err}", err, error=str(err))
+            _fail_update_held(self, err)
         finally:
             self._refresh_task = None
     async def _async_first_refresh_light(self) -> Payload:
@@ -6151,7 +6162,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
                 "First refresh completed without a solve; the real solve "
                 "follows in the background"
             )
-            return self._build_data_dict()
+            payload = self._build_data_dict()
+            log_held(self.entry, _UPDATE_FAILED, False)
+            return payload
         except (UpdateFailed, ConfigEntryAuthFailed):
             # #216, same as _async_update_data's wrapper: this path also
             # runs _fetch_tibber_prices, whose latch has already logged the
@@ -6159,10 +6172,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             # one ERROR, not two.
             raise
         except Exception as err:
-            _LOGGER.error(
-                "Error updating Heat Pump Optimizer: %s", err, exc_info=True
-            )
-            _raise_update_failed("update_failed", f"Error updating data: {err}", err, error=str(err))
+            _fail_update_held(self, err)
 
     def _solve_hubs(
         self, n_steps: int, *, banded: bool, band: draw_range.SolveBand | None = None
@@ -7755,7 +7765,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         await _best_effort_cycle_step(
             lambda: pump_arbiter.apply(self), "Pump arbiter apply skipped: %s"
         )
-        await _best_effort_cycle_step(lambda: early_cutoff.arm(early_cutoff.state_for(self), self.arbiter_inputs, boost.held_for(self), _ctx_of(self)._opt_config, self.entry.async_on_unload), "Early cut-off arm skipped: %s")
+        await _best_effort_cycle_step(lambda: early_cutoff.arm(early_cutoff.state_for(self), self.arbiter_inputs, boost.held_for(self), self.entry.async_on_unload), "Early cut-off arm skipped: %s")
         if not self._current_action or self._mode == MODE_OFF:  # off writes nothing
             return
         if self._mode in (MODE_AUTO, MODE_ECONOMY) and self._plan_is_stale():
@@ -8255,11 +8265,10 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
 
     async def _async_save_price_model(self) -> None:
         store = self._price_model_store  # bound once: read twice below (D1-s2-52)
-        try:
+        async def save() -> None:
             await store.async_wait_for_read()
             await store.async_save(self._price_learner.store_payload())
-        except Exception as err:  # noqa: BLE001
-            _LOGGER.debug("Could not persist price model: %s", err)
+        await save_held(store, "price model", save)
 
     async def _async_load_ledger(self) -> None:
         """Restore the monthly ledger (T1), then the start counter on every exit.
@@ -8310,7 +8319,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         self._spawn(self._async_save_ledger())
 
     async def _async_save_ledger(self) -> None:
-        try:
+        async def save() -> None:
             await self._ledger_store.async_wait_for_read()  # D1-s2-52
             await self._ledger_store.async_save(
                 {
@@ -8330,8 +8339,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
                     ),
                 }
             )
-        except Exception as err:  # noqa: BLE001
-            _LOGGER.debug("Could not persist ledger: %s", err)
+        await save_held(self._ledger_store, "ledger", save)
 
     async def _async_load_accuracy(self) -> None:
         ctx = getattr(self, "_ctx", self)
@@ -8353,7 +8361,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         )
         self._apply_comfort_weight()
     async def _async_save_accuracy(self) -> None:
-        try:
+        async def save() -> None:
             await self._accuracy_store.async_wait_for_read()  # D1-s2-52
             await self._accuracy_store.async_save_if_changed(
                 {
@@ -8368,8 +8376,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
                     "mode": self._mode,
                 },
             )
-        except Exception as err:  # noqa: BLE001
-            _LOGGER.debug("Could not persist accuracy history: %s", err)
+        await save_held(self._accuracy_store, "accuracy history", save)
 
     async def _async_load_energy_totals(self) -> None:
         stored = await load_mapping(self._energy_store, "energy totals")
@@ -8392,7 +8399,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         )
 
     async def _async_save_energy_totals(self) -> None:
-        try:
+        async def save() -> None:
             await self._energy_store.async_wait_for_read()  # D1-s2-52
             await self._energy_store.async_save_if_changed(
                 {
@@ -8410,8 +8417,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
                     "last_tick": dt_util.now().isoformat(),
                 },
             )
-        except Exception as err:  # noqa: BLE001
-            _LOGGER.debug("Could not persist energy totals: %s", err)
+        await save_held(self._energy_store, "energy totals", save)
 
     def month_channel_totals(self, line: str) -> tuple[float, float] | None:
         """This month's (kWh, cost) for one accumulator channel.
@@ -8460,15 +8466,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         self._manual_override = override
 
     async def _async_save_manual_plan(self) -> None:
-        try:
-            payload = (
-                self._manual_override.to_dict()
-                if self._manual_override is not None
-                else {}
-            )
-            await self._manual_plan_store.async_save(payload)
-        except Exception as err:  # noqa: BLE001
-            _LOGGER.debug("Could not persist manual plan: %s", err)
+        override = self._manual_override
+        await save_held(self._manual_plan_store, "manual plan", lambda: self._manual_plan_store.async_save(
+            {} if override is None else override.to_dict()))
 
     def _horizon_step_starts(self, solve_now: datetime, n_steps: int) -> list[datetime]:
         """The instant each solved step begins, matching the optimizer's own."""
@@ -9213,6 +9213,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             # dipping under the floor the user actually configured is.
             floor_c = float(ctx._opt_config.get_temp_bounds(hour)[0])
         except Exception:  # noqa: BLE001 - evidence, never operations
+            _LOGGER.debug("Curve comfort not tracked this cycle", exc_info=True)
             return
         margin = worst_zone_margin_k((
             ctx._current_state.room_temperature,
@@ -9485,6 +9486,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             # a full month — a rough estimate, honestly labelled "~".
             monthly_kwh = monthly_kwh / max(1, now.day) * 30.0
         except Exception:  # noqa: BLE001 - the estimate is best-effort
+            _LOGGER.debug("Monthly COP-issue estimate unavailable; 0 kWh used", exc_info=True)
             monthly_kwh = 0.0
         mean_price = (
             float(np.mean([p.get("total", 0.0) for p in self._prices]))
@@ -9731,10 +9733,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             self._snapshot_ring = SnapshotRing.from_dict(stored)
 
     async def _async_save_snapshots(self) -> None:
-        try:
-            await self._snapshot_store.async_save(self._snapshot_ring.as_dict())
-        except Exception as err:  # noqa: BLE001
-            _LOGGER.debug("Could not persist learner snapshots: %s", err)
+        await save_held(self._snapshot_store, "learner snapshots", lambda: self._snapshot_store.async_save(self._snapshot_ring.as_dict()))
 
     def _baseline_house_load(self, n_steps: int) -> np.ndarray:
         """Whole-house load excluding the heat pump, per step, in kW."""
@@ -9820,7 +9819,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
 
     def _expire_away_override(self, now: datetime) -> tuple[bool, datetime | None]:
         """The override as of ``now``, written back when it lapsed; no await splits it."""
-        parsed = away_mode._parse_return_time(self._away_state.override_return_iso)
+        parsed = away_mode.parse_return_time(self._away_state.override_return_iso)
         active, ret = away_mode.expire_override(self._away_state.override_active, parsed, now)
         if active != self._away_state.override_active or ret != parsed:
             self._away_state = replace(self._away_state, override_active=active,
@@ -9871,9 +9870,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         on = active if active is not None else self._away_state.override_active
         iso = None if active is False else self._away_state.override_return_iso
         if active is not False and return_time is not away_mode.OMIT:
-            parsed = away_mode._parse_return_time(return_time)
+            parsed = away_mode.parse_return_time(return_time)
             iso = parsed.isoformat() if parsed else None
-        on, ret = away_mode.expire_override(on, away_mode._parse_return_time(iso), dt_util.now())
+        on, ret = away_mode.expire_override(on, away_mode.parse_return_time(iso), dt_util.now())
         self._away_state = replace(self._away_state, override_active=on,
                                    override_return_iso=ret.isoformat() if ret else None)
         await away_mode.persist_override(self, self._away_state)
@@ -10043,6 +10042,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
                         pending["when"], sample.outdoor_temp, self._thermal_model
                     )
                 except Exception:  # noqa: BLE001 - tag is best-effort
+                    _LOGGER.debug("COP residual tag skipped", exc_info=True)
                     sample.cop_residual = None
                 # D7-03/D7-05: skip the accuracy sample when ``indoor_frozen``
                 # above is set — open window, external heat, pump fault, or
@@ -10603,11 +10603,13 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         try:
             state = replace(ctx._current_state)
         except Exception:  # noqa: BLE001 - diagnosis is best-effort evidence
+            _LOGGER.debug("Diagnosis inputs not captured", exc_info=True)
             return None
         now = dt_util.now()
         try:
             planned_wind, _ = self._current_weather()
         except Exception:  # noqa: BLE001 - wind is optional evidence
+            _LOGGER.debug("Diagnosis wind not captured; recorded as 0", exc_info=True)
             planned_wind = 0.0
         return {
             "state": state,
@@ -10900,8 +10902,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         return self._comfort_learner.effective_weight
 
     def _apply_comfort_weight(self) -> None:
-        """Push the comfort weight into the configuration when the learner moves."""
-        getattr(self, "_ctx", self)._opt_config.comfort_weight = self._comfort_weight()
+        """Publish the comfort weight in a new configuration when the learner moves."""
+        CoordinatorContext.publish_config(_ctx_of(self), self, comfort_weight=self._comfort_weight())
     def record_setpoint_override(self, requested: float) -> None:
         """Note that the user overrode the plan's setpoint.
 
@@ -11354,6 +11356,23 @@ def _raise_auth_failed(key: str, message: str, **placeholders: str) -> NoReturn:
     )
 
 
+#: The latch key of an unexpected exception in the update cycle, held on the
+#: config entry (D1-s3-06): each setup retry builds a new coordinator whose
+#: shutdown forgets ``hass``'s latches, and the entry outlives both.
+_UPDATE_FAILED = "update_failed"
+
+
+def _fail_update_held(coord: Any, err: Exception) -> NoReturn:
+    """Fail the update on an unexpected ``err``, logged once per outage (D1-s3-06).
+
+    Both update paths logged ERROR with a traceback on every refresh of a
+    persisting failure, beside #216's latched UpdateFailed arm; now only when
+    it starts or its text changes (``log_held``), each path's success clears it.
+    """
+    log_held(coord.entry, _UPDATE_FAILED, True, "Error updating Heat Pump Optimizer: %s", err, exc_info=err)
+    _raise_update_failed("update_failed", f"Error updating data: {err}", err, error=str(err))
+
+
 def _raise_update_failed(
     key: str, message: str, cause: BaseException | None, **placeholders: str
 ) -> NoReturn:
diff --git a/custom_components/heatpump_optimizer/datetime.py b/custom_components/heatpump_optimizer/datetime.py
index cc2e072476..efeb5754fe 100644
--- a/custom_components/heatpump_optimizer/datetime.py
+++ b/custom_components/heatpump_optimizer/datetime.py
@@ -7,7 +7,7 @@ from homeassistant.components.datetime import DateTimeEntity
 from homeassistant.core import HomeAssistant
 from homeassistant.helpers.entity_platform import AddEntitiesCallback
 
-from .away import _parse_return_time
+from .away import parse_return_time
 from .coordinator import HeatPumpOptimizerConfigEntry, HeatPumpOptimizerCoordinator
 from .entity import HeatPumpOptimizerEntity, publish_then_refresh
 
@@ -41,7 +41,7 @@ class AwayReturnDateTime(HeatPumpOptimizerEntity, DateTimeEntity):
     def native_value(self) -> datetime | None:
         # The live override, not the payload's copy, which changes only after
         # the refresh the set call asks for has run its solve (v6.6.12).
-        return _parse_return_time(self.coordinator.away_state.override_return_iso)
+        return parse_return_time(self.coordinator.away_state.override_return_iso)
 
     async def async_set_value(self, value: datetime) -> None:
         await self.coordinator.async_set_away(return_time=value, refresh=False)
diff --git a/custom_components/heatpump_optimizer/debugger.py b/custom_components/heatpump_optimizer/debugger.py
index b09a76a66e..b072d5ca38 100644
--- a/custom_components/heatpump_optimizer/debugger.py
+++ b/custom_components/heatpump_optimizer/debugger.py
@@ -32,7 +32,6 @@ from __future__ import annotations
 import asyncio
 import inspect
 import json
-import logging
 import statistics
 import time
 from collections.abc import Callable, Coroutine
@@ -62,10 +61,9 @@ from .store import (
     load_mapping,
     off_domain,
     quarantines,
+    save_held,
 )
 
-_LOGGER = logging.getLogger(__name__)
-
 DEBUG_STORE_VERSION = 1
 BUNDLE_SCHEMA = "hpo-debug/1"
 COLLECT_SPAN = timedelta(days=7)
@@ -518,10 +516,9 @@ class DebugCollector:
                 "snapshots": list(self.snapshots), **tests}
 
     async def async_save(self) -> None:
-        try:
-            await self._store.async_save(self.as_dict())
-        except Exception as err:  # noqa: BLE001 - a lost save costs at most an hour of rows
-            _LOGGER.debug("Could not persist the debug collection: %s", err)
+        await save_held(
+            self._store, "the debug collection", lambda: self._store.async_save(self.as_dict()),
+        )  # a lost save costs at most an hour of rows
 
     def observe(self, coordinator: Any) -> None:
         """One listener call: time a solve's edges, record a newly published payload."""
diff --git a/custom_components/heatpump_optimizer/dhw_learning.py b/custom_components/heatpump_optimizer/dhw_learning.py
index c912d13db2..5dab7c9b2a 100644
--- a/custom_components/heatpump_optimizer/dhw_learning.py
+++ b/custom_components/heatpump_optimizer/dhw_learning.py
@@ -26,7 +26,7 @@ from typing import Any
 import numpy as np
 
 from homeassistant.core import HomeAssistant
-from .store import QuarantiningStore, load_mapping
+from .store import QuarantiningStore, load_mapping, save_held
 from homeassistant.util import dt as dt_util
 
 from .accuracy import utc_elapsed_seconds
@@ -361,15 +361,14 @@ class DhwProfileLearner:
 
     async def async_save_profile(self) -> None:
         """Persist learned DHW profile to Home Assistant storage."""
-        try:
+        async def save() -> None:
             await self.profile_store.async_save(
                 {
                     **self.payload(),
                     "updated_at": dt_util.now().isoformat(),
                 }
             )
-        except Exception as err:
-            _LOGGER.debug("Could not persist DHW profile: %s", err)
+        await save_held(self.profile_store, "DHW profile", save)
 
     async def async_load_draws(self) -> None:
         """Load the per-window draw statistics (#32)."""
@@ -378,11 +377,10 @@ class DhwProfileLearner:
             self.draw_stats = DrawStats.from_dict(stored)
 
     async def async_save_draws(self) -> None:
-        try:
+        async def save() -> None:
             await self.draws_store.async_save(self.draw_stats.as_dict())
             self.draws_dirty = False
-        except Exception as err:  # noqa: BLE001
-            _LOGGER.debug("Could not persist DHW draw statistics: %s", err)
+        await save_held(self.draws_store, "DHW draw statistics", save)
 
     def pattern_for(self, weekend: bool) -> list[float]:
         """The #18 blended pattern for one day type, volume-preserving.
diff --git a/custom_components/heatpump_optimizer/diagnosis.py b/custom_components/heatpump_optimizer/diagnosis.py
index 303cb23f98..0cd15dfa98 100644
--- a/custom_components/heatpump_optimizer/diagnosis.py
+++ b/custom_components/heatpump_optimizer/diagnosis.py
@@ -91,6 +91,7 @@ def attribute(
     try:
         baseline = _room_after(model, state, planned)
     except Exception:  # noqa: BLE001 - diagnosis must never break operations
+        _LOGGER.debug("Diagnosis baseline not simulated", exc_info=True)
         return None
 
     contributions: dict[str, float] = {}
@@ -112,6 +113,7 @@ def attribute(
         try:
             shifted = _room_after(model, state, swapped)
         except Exception:  # noqa: BLE001 - skip the swap, keep the rest
+            _LOGGER.debug("Diagnosis swap %s not simulated", key, exc_info=True)
             continue
         delta = shifted - baseline
         if abs(delta) >= 0.005:
diff --git a/custom_components/heatpump_optimizer/diagnostics.py b/custom_components/heatpump_optimizer/diagnostics.py
index c49354ec08..6131cef4ac 100644
--- a/custom_components/heatpump_optimizer/diagnostics.py
+++ b/custom_components/heatpump_optimizer/diagnostics.py
@@ -66,6 +66,7 @@ self-tests ran.
 """
 from __future__ import annotations
 
+import logging
 from collections.abc import Callable, Mapping
 from datetime import datetime
 from functools import reduce
@@ -90,6 +91,8 @@ from .coordinator import (
 )
 from .payload import LearningView
 
+_LOGGER = logging.getLogger(__name__)
+
 #: Keys whose values never leave the instance, at any depth: the Tibber
 #: credential, the location (``LOCATION_KEYS``), and the entry name, which is
 #: free text the user typed and
@@ -337,6 +340,7 @@ def _coordinator_snapshot(coord: HeatPumpOptimizerCoordinator) -> dict[str, Any]
     try:
         state: CoordinatorDiagnostics | None = coord.diagnostics_state()
     except Exception:  # noqa: BLE001 -- diagnostics never breaks
+        _LOGGER.debug("Diagnostics state unavailable", exc_info=True)
         state = None
     snap: dict[str, Any] = {
         "mode": getattr(coord, "mode", None),
@@ -367,6 +371,7 @@ def _never_breaks(view: Callable[[Any], Any], coord: Any) -> Any:
     try:
         return view(coord)
     except Exception:  # noqa: BLE001 -- diagnostics never breaks
+        _LOGGER.debug("Diagnostics view %s unavailable", view, exc_info=True)
         return "unavailable"
 
 
diff --git a/custom_components/heatpump_optimizer/duty_switch.py b/custom_components/heatpump_optimizer/duty_switch.py
index 9851bc3071..596b892281 100644
--- a/custom_components/heatpump_optimizer/duty_switch.py
+++ b/custom_components/heatpump_optimizer/duty_switch.py
@@ -57,7 +57,7 @@ from homeassistant.util import dt as dt_util
 from . import duty_legs, pump_mode, running_signal
 from .const import DOMAIN
 from .drift import stored_instant, utc_elapsed_seconds
-from .store import QuarantiningStore
+from .store import QuarantiningStore, save_held
 from .thermal_model import planned_draw_runs
 
 _LOGGER = logging.getLogger(__name__)
@@ -509,12 +509,10 @@ async def _load(rec: _Record) -> bool:
 
 
 async def _persist(rec: _Record) -> None:
-    try:
-        await rec.store.async_save(rec.learner.stored_record())
-    except Exception as err:  # noqa: BLE001 - still dirty: saved on the next pass
-        _LOGGER.debug("Could not persist the duty-switch record: %s", err)
-        return
-    rec.dirty = False
+    if await save_held(
+        rec.store, "the duty-switch record", lambda: rec.store.async_save(rec.learner.stored_record()),
+    ):
+        rec.dirty = False  # a failed save stays dirty: saved on the next pass
 
 
 def starts_attributes(coord: Any) -> dict[str, float]:
diff --git a/custom_components/heatpump_optimizer/early_cutoff.py b/custom_components/heatpump_optimizer/early_cutoff.py
index 39de3411b3..04af0a5683 100644
--- a/custom_components/heatpump_optimizer/early_cutoff.py
+++ b/custom_components/heatpump_optimizer/early_cutoff.py
@@ -132,7 +132,6 @@ class CutoffInputs:
 
     inputs: Callable[[], ArbiterInputs]
     boosts: BoostState
-    opt_config: Any
 
 
 #: Weak-keyed, so a value must not reach its key: ``wiring.inputs`` is the
@@ -150,7 +149,6 @@ async def arm(
     held: CutoffState,
     inputs: Callable[[], ArbiterInputs],
     boosts: BoostState,
-    opt_config: Any,
     on_unload: Callable[[Callable[[], None]], Any],
     now: datetime | None = None,
 ) -> None:
@@ -165,7 +163,7 @@ async def arm(
         # Once per record, listener or not: the wiring below reaches the
         # coordinator and has to be dropped with the entry.
         on_unload(lambda: detach(held))
-    held.wiring = CutoffInputs(inputs, boosts, opt_config)
+    held.wiring = CutoffInputs(inputs, boosts)
     inp = inputs()
     cfg = EntryConfig.from_mapping(inp.config)
     # In UTC: local wall-clock arithmetic is an hour off across a DST change.
@@ -242,10 +240,15 @@ def _plant_exempt(inp: ArbiterInputs) -> str | None:
     return tank_reason(inp)
 
 
-def threshold(inp: ArbiterInputs, opt_config: Any, now: datetime) -> float:
-    """The room temperature above which the pump is cut, in degC."""
+def threshold(inp: ArbiterInputs, now: datetime) -> float:
+    """The room temperature above which the pump is cut, in degC.
+
+    The comfort target is the configuration ``inp`` carries, read at this
+    reading: never one held since the arm, which a target or comfort-weight
+    change has since replaced (ADR-003).
+    """
     local = dt_util.as_local(now)
-    base = float(opt_config.get_comfort_temp(local.hour + local.minute / 60.0, when=local))
+    base = float(inp.opt_config.get_comfort_temp(local.hour + local.minute / 60.0, when=local))
     return max(base, *_planned_room(inp.plan, now)) + MARGIN_K
 
 
@@ -304,7 +307,7 @@ def on_room_event(held: CutoffState, wiring: CutoffInputs, event: Any) -> None:
         return
     if _exempt(inp, wiring.boosts, now) is not None:
         return
-    limit = threshold(inp, wiring.opt_config, now)
+    limit = threshold(inp, now)
     if room <= limit:
         return
     reason = _cycle_guard(inp, held, now)
diff --git a/custom_components/heatpump_optimizer/legionella.py b/custom_components/heatpump_optimizer/legionella.py
index f68744eec1..515ca86e07 100644
--- a/custom_components/heatpump_optimizer/legionella.py
+++ b/custom_components/heatpump_optimizer/legionella.py
@@ -21,7 +21,7 @@ from typing import Any, Callable
 
 from homeassistant.core import HomeAssistant
 from homeassistant.helpers import issue_registry as ir
-from .store import QuarantiningStore
+from .store import QuarantiningStore, save_held
 from homeassistant.util import dt as dt_util
 
 from .accuracy import utc_elapsed_seconds
@@ -257,10 +257,7 @@ class LegionellaGuard:
                 payload["last_attempt_peak"] = round(
                     float(self.attempt_peak), 2
                 )
-        try:
-            await self.store.async_save(payload)
-        except Exception as err:
-            _LOGGER.debug("Could not persist DHW legionella timestamp: %s", err)
+        await save_held(self.store, "DHW legionella timestamp", lambda: self.store.async_save(payload))
 
     async def async_track(self, dhw_temp: float) -> None:
         """Reset the anti-legionella timer whenever the tank actually gets hot.
diff --git a/custom_components/heatpump_optimizer/manifest.json b/custom_components/heatpump_optimizer/manifest.json
index 3d56cf917b..f4c1236e77 100644
--- a/custom_components/heatpump_optimizer/manifest.json
+++ b/custom_components/heatpump_optimizer/manifest.json
@@ -19,7 +19,7 @@
   "documentation": "https://github.com/tvofi/heatpump_optimizer",
   "iot_class": "cloud_polling",
   "issue_tracker": "https://github.com/tvofi/heatpump_optimizer/issues",
-  "quality_scale": "platinum",
+  "quality_scale": "gold",
   "requirements": [
     "numpy>=1.24.0",
     "scipy>=1.10.0",
diff --git a/custom_components/heatpump_optimizer/notifier.py b/custom_components/heatpump_optimizer/notifier.py
index 0c82538382..e83e4779bc 100644
--- a/custom_components/heatpump_optimizer/notifier.py
+++ b/custom_components/heatpump_optimizer/notifier.py
@@ -27,7 +27,6 @@ holds its clock and writes it through ``issues.set_issue``.
 """
 from __future__ import annotations
 
-import logging
 from collections.abc import Callable, Coroutine
 from datetime import datetime, timedelta
 from typing import Any, NamedTuple
@@ -39,9 +38,7 @@ from .const import CONF_FLOOR_RETURN_TEMP_ENTITY, DOMAIN
 from .payload import InputProblem, Payload
 from .issues import set_issue
 from .wood_fuel import saving_includes_wood
-from .store import QuarantiningStore, load_mapping
-
-_LOGGER = logging.getLogger(__name__)
+from .store import QuarantiningStore, load_mapping, save_held
 
 NOTIFIER_STORE_VERSION = 1
 EVENT_MONTHLY_RECEIPT = f"{DOMAIN}_monthly_receipt"
@@ -284,10 +281,9 @@ class Notifier:
             self._baseline = False
 
     async def _async_save(self) -> None:
-        try:
-            await self._store.async_save({"sent": dict(self._sent)})
-        except Exception as err:  # noqa: BLE001
-            _LOGGER.debug("Could not persist notifier state: %s", err)
+        await save_held(
+            self._store, "notifier state", lambda: self._store.async_save({"sent": dict(self._sent)}),
+        )
 
     def handle(self, data: Payload) -> None:
         """Fire what is new in ``data`` and forget what has cleared."""
diff --git a/custom_components/heatpump_optimizer/off_restore.py b/custom_components/heatpump_optimizer/off_restore.py
index be47b192b7..33dc689838 100644
--- a/custom_components/heatpump_optimizer/off_restore.py
+++ b/custom_components/heatpump_optimizer/off_restore.py
@@ -50,7 +50,7 @@ from homeassistant.core import HomeAssistant
 
 from .const import DOMAIN, MODE_OFF
 from .log_latch import log_held
-from .store import QuarantiningStore, load_mapping
+from .store import QuarantiningStore, load_mapping, save_held
 
 if TYPE_CHECKING:
     from .coordinator import HeatPumpOptimizerConfigEntry
@@ -147,10 +147,9 @@ async def _save(held: _Held) -> None:
     data: dict[str, Any] = {"armed": dict(held.armed)}
     if held.consumers:  # a neutral consumer's record keeps #3299's one key (I4)
         data["state"] = held.consumers
-    try:
-        await held.store.async_save(data)
-    except Exception as err:  # noqa: BLE001 - a store failure never blocks a write
-        _LOGGER.debug("Could not save the off-restore store: %s", err)
+    await save_held(
+        held.store, "the off-restore store", lambda: held.store.async_save(data),
+    )  # a store failure never blocks a write
 
 
 async def async_arm(
diff --git a/custom_components/heatpump_optimizer/optimizer.py b/custom_components/heatpump_optimizer/optimizer.py
index c54290f544..f3ba7ce4da 100644
--- a/custom_components/heatpump_optimizer/optimizer.py
+++ b/custom_components/heatpump_optimizer/optimizer.py
@@ -1862,6 +1862,7 @@ def _lbfgsb_restart(
             bounds, args, maxiter, memo,
         )
     except Exception:  # pragma: no cover - solver blow-up
+        _LOGGER.debug("L-BFGS-B restart failed; the start's own point kept", exc_info=True)
         return best
     score = float(objective(polished.x, *args))
     prior = float(objective(best.x, *args))
@@ -1940,6 +1941,7 @@ def _multi_start_minimize(
         try:
             score = float(memoized(guess, *args))
         except Exception:
+            _LOGGER.debug("Start candidate skipped: its objective raised", exc_info=True)
             continue
         if np.isfinite(score):
             scored.append((score, guess))
@@ -2947,7 +2949,7 @@ def _solver_status(
         if objective(result.x) <= objective(initial_guess):
             return "optimal"
     except Exception:  # pragma: no cover - defensive
-        pass
+        _LOGGER.debug("Solver status comparison raised", exc_info=True)
     return f"suboptimal ({result.message})"
 
 
diff --git a/custom_components/heatpump_optimizer/pump_arbiter.py b/custom_components/heatpump_optimizer/pump_arbiter.py
index 8fc1cc6845..0c0b79b3bf 100644
--- a/custom_components/heatpump_optimizer/pump_arbiter.py
+++ b/custom_components/heatpump_optimizer/pump_arbiter.py
@@ -201,7 +201,7 @@ from .payload import REASON_LEGIONELLA, CurrentAction
 from .plan_step import PLAN_STEP_HOURS, PLAN_STEP_MINUTES, plan_step_index, plan_step_start
 from .drift import utc_elapsed_seconds, utc_shift
 from .drift import stored_instant
-from .store import QuarantiningStore, load_mapping
+from .store import QuarantiningStore, load_mapping, save_held
 from .sysid import KIND_PROBE
 from .thermal_model import (
     configured_flow_heat_c,
@@ -428,6 +428,10 @@ class ArbiterInputs:
     #: means is ``freq_control.defrost_interval``'s, and ``None`` is no flag
     #: or no evidence.
     defrosting: bool | None = None
+    #: The live optimization config, read at each decision: a target or
+    #: comfort-weight change publishes a new one (ADR-003), so one held across
+    #: passes would judge on the old values. ``None`` only in a harness.
+    opt_config: Any = None
     #: The running-draw window each pass record is handed to
     #: (``draw_range.note_pass``); ``None`` keeps none.
     draw: Any = None
@@ -2267,10 +2271,7 @@ async def _persist(coord: Any) -> None:
         "written": {k: [v, at.isoformat()] for k, (v, at) in held.written.items()},
         "dropped": dict(held.dropped),
     }
-    try:
-        await _store(coord).async_save(payload)
-    except Exception as err:  # noqa: BLE001
-        _LOGGER.debug("Could not persist the pump duty record: %s", err)
+    await save_held(coord, "the pump duty record", lambda: _store(coord).async_save(payload))
 
 
 async def _load(coord: Any) -> None:
diff --git a/custom_components/heatpump_optimizer/quality_scale.yaml b/custom_components/heatpump_optimizer/quality_scale.yaml
index 75e5433c5e..b2d3de0d96 100644
--- a/custom_components/heatpump_optimizer/quality_scale.yaml
+++ b/custom_components/heatpump_optimizer/quality_scale.yaml
@@ -197,16 +197,17 @@ rules:
   async-dependency: done
   inject-websession: done
   strict-typing:
-    status: done
+    status: todo
     comment: >-
-      Both halves of the rule hold. The marker file: "you need to add a
-      py.typed file to your library", "There are no exceptions to this rule" —
-      py.typed is shipped (qs_py_typed_files=1). The warning: the custom typed
-      config entry "must be used throughout" — every entry parameter, return
-      and attribute annotation is typed with HeatPumpOptimizerConfigEntry, none
-      bare (qs_entry_param_bare=0; tests/doc_claims.py derives the census from
-      the code and reads this number, #1545). The
-      note this replaces — that the marker-file half "does not apply to a
-      custom integration" — is not in the rule text, so it was not the basis.
-      #1465, #1466 (round 7 D10-01/D10-02). #303 paid the pinned-ruler census.
-      #829.
+      One half of the rule does not hold. The integration's library "must be
+      typed as well, and ship a py.typed file", and hassfest asks the same of
+      every manifest requirement or a types- stub package for it:
+      threadpoolctl ships neither (optimizer.py resolves it by name for that
+      reason), so the row is todo and the manifest carries the tier
+      tests/entities.py derives from the rows (D10-s3-01). What holds: the
+      integration ships py.typed (qs_py_typed_files=1); every entry
+      parameter, return and attribute annotation is typed with
+      HeatPumpOptimizerConfigEntry, none bare (qs_entry_param_bare=0;
+      tests/doc_claims.py derives the census from the code and reads this
+      number, #1545), and so is the coordinator's config_entry (D10-s3-02).
+      #1465, #1466, #303, #829.
diff --git a/custom_components/heatpump_optimizer/room_record.py b/custom_components/heatpump_optimizer/room_record.py
index e2c3096311..ccb522e2aa 100644
--- a/custom_components/heatpump_optimizer/room_record.py
+++ b/custom_components/heatpump_optimizer/room_record.py
@@ -20,7 +20,7 @@ from homeassistant.core import HomeAssistant
 from .const import DOMAIN
 from .room_history import History, House, Period, identifiability_report, loaded, note, stored
 from .rooms import RoomReading
-from .store import QuarantiningStore
+from .store import QuarantiningStore, save_held
 
 __all__ = ["House", "async_flush", "async_note_cycle", "record_of", "report_of"]
 
@@ -69,12 +69,10 @@ async def _load(rec: _Record) -> None:
 
 
 async def _persist(rec: _Record) -> None:
-    try:
-        await rec.store.async_save(stored(rec.history))
-    except Exception as err:  # noqa: BLE001 - still unsaved: saved on the next pass
-        _LOGGER.debug("Could not persist the room history: %s", err)
-        return
-    rec.unsaved = 0
+    if await save_held(
+        rec.store, "the room history", lambda: rec.store.async_save(stored(rec.history)),
+    ):
+        rec.unsaved = 0  # a failed save stays unsaved: saved on the next pass
 
 
 async def async_note_cycle(coord: Any, now: datetime, readings: Sequence[RoomReading], house: House) -> None:
diff --git a/custom_components/heatpump_optimizer/services.py b/custom_components/heatpump_optimizer/services.py
index 22ec38828a..37b806263b 100644
--- a/custom_components/heatpump_optimizer/services.py
+++ b/custom_components/heatpump_optimizer/services.py
@@ -27,6 +27,7 @@ from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
 from homeassistant.helpers import config_validation as cv
 from homeassistant.util import dt as dt_util
 
+from . import away as away_mode
 from . import comfort_band
 from . import debugger
 from . import mixing_valve
@@ -633,7 +634,17 @@ async def handle_set_away(hass: HomeAssistant, call: ServiceCall) -> None:
     if "active" in call.data:
         kwargs["active"] = call.data["active"]
     if "return_time" in call.data:
-        kwargs["return_time"] = call.data["return_time"]
+        raw = call.data["return_time"]
+        # D10-s1-01: a value that neither clears nor parses was stored as
+        # the absent time, wiping a held return; refused before any write.
+        if not away_mode.clears_return_time(raw) and away_mode.parse_return_time(raw) is None:
+            raise ServiceValidationError(
+                f"Invalid return_time {raw!r}: not a date and time",
+                translation_domain=DOMAIN,
+                translation_key="away_invalid_return_time",
+                translation_placeholders={"return_time": str(raw)},
+            )
+        kwargs["return_time"] = raw
     for _entry_id, coord in _loaded_coordinators(hass):
         await coord.async_set_away(**kwargs)
 
diff --git a/custom_components/heatpump_optimizer/store.py b/custom_components/heatpump_optimizer/store.py
index adbd6d826d..6e2a36a61d 100644
--- a/custom_components/heatpump_optimizer/store.py
+++ b/custom_components/heatpump_optimizer/store.py
@@ -30,7 +30,7 @@ import hashlib
 import json
 import logging
 import math
-from collections.abc import Mapping, Sequence
+from collections.abc import Awaitable, Callable, Mapping, Sequence
 from datetime import date, datetime, timedelta, timezone, tzinfo
 from types import MappingProxyType
 from typing import Any, NamedTuple, TypeVar, cast
@@ -55,6 +55,7 @@ from .price_model import (
     QUARTER_FACTOR_MAX, QUARTER_FACTOR_MIN, RESIDUAL_VAR_MAX, SHAPE_MAX, SHAPE_MIN,
 )
 from .issues import create_issue
+from .log_latch import log_held
 
 _LOGGER = logging.getLogger(__name__)
 
@@ -721,6 +722,29 @@ async def load_mapping(store: Any, what: str) -> dict[str, Any] | None:
     return raw if isinstance(raw, dict) else None
 
 
+
+async def save_held(owner: Any, what: str, save: Callable[[], Awaitable[object]]) -> bool:
+    """Run ``save``; whether it landed. A failure is held per ``(owner, what)``.
+
+    D1-s3-05: every persist handler logged its failure at DEBUG, so a save that
+    failed on every pass, or a payload builder that raised, stopped the store
+    persisting with nothing above Home Assistant's default level. ``save``
+    builds its payload inside the call, so a builder bug is held with the
+    transport failures: an ERROR with its traceback when the outage starts,
+    DEBUG while it holds, ``Resolved`` on the first save that lands
+    (``log_held``). ``owner`` outlives the call, as ``log_held`` requires: the
+    kept store, or the coordinator where a store is built per call; a record
+    dataclass is unhashable and cannot key the latch.
+    """
+    key = "persist_" + what.replace(" ", "_")
+    try:
+        await save()
+    except Exception as err:  # noqa: BLE001 - a lost save never breaks its caller
+        log_held(owner, key, True, "Could not persist %s: %s", what, err, exc_info=err)
+        return False
+    log_held(owner, key, False)
+    return True
+
 class QuarantiningStore(Store[_StorePayload]):
     """A ``Store`` whose ``async_load`` scrubs poisoned numeric leaves.
 
diff --git a/custom_components/heatpump_optimizer/strings.json b/custom_components/heatpump_optimizer/strings.json
index 64e36d0449..f9ef6160c7 100644
--- a/custom_components/heatpump_optimizer/strings.json
+++ b/custom_components/heatpump_optimizer/strings.json
@@ -438,6 +438,9 @@
     "manual_plan_invalid_expires_at": {
       "message": "Invalid expires_at \"{expires_at}\": not an ISO 8601 datetime"
     },
+    "away_invalid_return_time": {
+      "message": "Invalid return_time \"{return_time}\": not a date and time"
+    },
     "manual_plan_invalid_slots": {
       "message": "{error}"
     },
diff --git a/custom_components/heatpump_optimizer/translations/de.json b/custom_components/heatpump_optimizer/translations/de.json
index d024d3c067..fbd27df90c 100644
--- a/custom_components/heatpump_optimizer/translations/de.json
+++ b/custom_components/heatpump_optimizer/translations/de.json
@@ -438,6 +438,9 @@
     "manual_plan_invalid_expires_at": {
       "message": "Ungültiger Wert für expires_at \"{expires_at}\": kein ISO-8601-Datum mit Uhrzeit"
     },
+    "away_invalid_return_time": {
+      "message": "Ungültiger Wert für return_time \"{return_time}\": kein Datum mit Uhrzeit"
+    },
     "manual_plan_invalid_slots": {
       "message": "{error}"
     },
diff --git a/custom_components/heatpump_optimizer/translations/en.json b/custom_components/heatpump_optimizer/translations/en.json
index 64e36d0449..f9ef6160c7 100644
--- a/custom_components/heatpump_optimizer/translations/en.json
+++ b/custom_components/heatpump_optimizer/translations/en.json
@@ -438,6 +438,9 @@
     "manual_plan_invalid_expires_at": {
       "message": "Invalid expires_at \"{expires_at}\": not an ISO 8601 datetime"
     },
+    "away_invalid_return_time": {
+      "message": "Invalid return_time \"{return_time}\": not a date and time"
+    },
     "manual_plan_invalid_slots": {
       "message": "{error}"
     },
diff --git a/custom_components/heatpump_optimizer/translations/sv.json b/custom_components/heatpump_optimizer/translations/sv.json
index 42c981d30b..f6623cc026 100644
--- a/custom_components/heatpump_optimizer/translations/sv.json
+++ b/custom_components/heatpump_optimizer/translations/sv.json
@@ -438,6 +438,9 @@
     "manual_plan_invalid_expires_at": {
       "message": "Ogiltigt expires_at \"{expires_at}\": inte en datumtid i ISO 8601-format"
     },
+    "away_invalid_return_time": {
+      "message": "Ogiltig return_time \"{return_time}\": inte ett datum med tid"
+    },
     "manual_plan_invalid_slots": {
       "message": "{error}"
     },
diff --git a/dev/programme/delivery/3845.md b/dev/programme/delivery/3845.md
new file mode 100644
index 0000000000..0949e41e33
--- /dev/null
+++ b/dev/programme/delivery/3845.md
@@ -0,0 +1 @@
+- [#3845](https://github.com/tvofi/heatpump_optimizer/pull/3845) — **open**, R11-SEAM-cycle-reporting: how a failure is reported (R11-SEAM-cycle-reporting)
diff --git a/tests/arch_score_head.py b/tests/arch_score_head.py
index df6a910f01..7dbb4c1709 100644
--- a/tests/arch_score_head.py
+++ b/tests/arch_score_head.py
@@ -45,11 +45,9 @@ R = Results("architecture score on today's tree (R9-EG-A1)")
 #: wherever in the cycle it sits -- #1887's round-1 review moved one into the
 #: pre-solve step, which the solve-only roots did not reach.
 _C = "coordinator:HeatPumpOptimizerCoordinator."
-CYCLE_HUB_WRITERS = {
-    _C + "_apply_comfort_weight": (
-        {"_opt_config.comfort_weight"},
-        "the quiet-period learner in the solve's tail moved the learned weight"),
-}
+#: Empty since R11-SEAM-cycle-reporting (ADR-003, D7-s2-03): the comfort weight,
+#: the one row this held, is published in a new context, which is no site.
+CYCLE_HUB_WRITERS: dict[str, tuple[set[str], str]] = {}
 LISTED = {(w, f) for w, (fields, _why) in CYCLE_HUB_WRITERS.items() for f in fields}
 #: The planted writes the controls add: one as async_run_optimization's first
 #: statement, one as the pre-solve step's last (#1887's round-1 probe).
diff --git a/tests/doc_claims.py b/tests/doc_claims.py
index 062b8ee5b5..c83dea9d25 100644
--- a/tests/doc_claims.py
+++ b/tests/doc_claims.py
@@ -1539,6 +1539,27 @@ def bare_entry_annotations(trees: dict[str, ast.Module] | None = None) -> list[s
     return hits
 
 
+def untyped_coordinators(trees: dict[str, ast.Module] | None = None) -> tuple[list[str], list[str]]:
+    """Each DataUpdateCoordinator subclass, and those whose body leaves ``config_entry`` untyped.
+
+    D10-s3-02: the strict-typing rule asks a coordinator that gets the entry to
+    annotate ``config_entry`` with the typed alias; the parameter census above
+    reads no class attribute the base class declares, so it missed this one.
+    """
+    seen: list[str] = []
+    hits: list[str] = []
+    for name, tree in (_PKG_TREES if trees is None else trees).items():
+        for node in ast.walk(tree):
+            if not isinstance(node, ast.ClassDef) or not any(
+                    "DataUpdateCoordinator" in ast.unparse(b) for b in node.bases):
+                continue
+            seen.append(f"{name}:{node.lineno} {node.name}")
+            if not any(isinstance(st, ast.AnnAssign) and ast.unparse(st.target) == "config_entry"
+                       and "HeatPumpOptimizerConfigEntry" in ast.unparse(st.annotation)
+                       for st in node.body):
+                hits.append(seen[-1])
+    return seen, hits
+
 _EXC_FAMILY = {
     "HomeAssistantError", "ServiceValidationError", "IntegrationError",
     "ConfigEntryError", "ConfigEntryNotReady", "ConfigEntryAuthFailed",
@@ -1665,6 +1686,16 @@ _TYPING_CLEAN = """
 def ok(entry: HeatPumpOptimizerConfigEntry, n: int, /, *a: str, k: ConfigEntryX = None) -> HeatPumpOptimizerConfigEntry: ...
 x: "HeatPumpOptimizerConfigEntry | None" = None
 """
+_COORD_TYPING = """
+class Bare(DataUpdateCoordinator[Payload]):
+    config_entry: ConfigEntry
+class Missing(update_coordinator.DataUpdateCoordinator):
+    other: HeatPumpOptimizerConfigEntry
+class Typed(DataUpdateCoordinator[Payload]):
+    config_entry: HeatPumpOptimizerConfigEntry
+class NotACoordinator:
+    pass
+"""
 _RAISE_BAD = """
 def _raise_helper(key, message, cause=None, **ph):
     raise UpdateFailed(message, translation_domain=DOMAIN, translation_key=key) from cause
@@ -1727,6 +1758,13 @@ def check_census_self_test() -> None:
     )
     clean = bare_entry_annotations(_fixture(_TYPING_CLEAN))
     R.check("the typing census passes the alias and look-alike names (null control)", clean == [], repr(clean))
+    seen, untyped = untyped_coordinators(_fixture(_COORD_TYPING))
+    R.check(
+        "the coordinator census finds each coordinator subclass and refuses a bare or missing "
+        "config_entry; the typed one and a non-coordinator class pass (null controls)",
+        (seen, untyped) == (["m.py:2 Bare", "m.py:4 Missing", "m.py:6 Typed"], ["m.py:2 Bare", "m.py:4 Missing"]),
+        f"got {seen} {untyped}",
+    )
     total, missing, keys = exception_raise_census(_fixture(_RAISE_BAD))
     R.check(
         "the exception census counts every site, refuses each untranslated one, and reads each key",
@@ -1756,6 +1794,13 @@ def check_quality_scale() -> None:
         claimed is not None and int(claimed.group(1)) == len(bare),
         f"claimed {claimed.group(1) if claimed else None}, census {len(bare)}: {bare}",
     )
+    seen, untyped = untyped_coordinators()
+    R.check(
+        "every DataUpdateCoordinator subclass annotates config_entry with the typed entry "
+        "(D10-s3-02), over a census that found at least one",
+        bool(seen) and not untyped,
+        f"seen {seen}, untyped {untyped}",
+    )
     # The census itself is held to exact results by check_census_self_test.
 
     status = _rule_block("exception-translations").split(":", 1)[1]
diff --git a/tests/dst_checks.py b/tests/dst_checks.py
index 8a4491abf6..a09254552c 100644
--- a/tests/dst_checks.py
+++ b/tests/dst_checks.py
@@ -2424,7 +2424,8 @@ def _ec_cut_at(arm_at, switch_since, reading_at):
     hass, inp = _ec_world(arm_at - timedelta(minutes=5), switch_since)
     cfg = SimpleNamespace(get_comfort_temp=lambda hour, when=None: 21.0)
     dt_util.freeze(arm_at)
-    asyncio.run(_ec.arm(held, lambda: inp, _EcBoost(), cfg, lambda _f: None, dt_util.now()))
+    inp = replace(inp, opt_config=cfg)
+    asyncio.run(_ec.arm(held, lambda: inp, _EcBoost(), lambda _f: None, dt_util.now()))
     dt_util.freeze(reading_at)
     _ec.on_room_event(held, held.wiring, SimpleNamespace(
         data={"new_state": FakeState("22.5", unit="°C")}))
diff --git a/tests/entities.py b/tests/entities.py
index d84b350dad..3d0d66a786 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -10910,7 +10910,7 @@ def _ss_instant(leaf) -> bool:
         _ss_manual._parse_dt(leaf, _SS_NOW)
         return True
     except _ss_manual.ManualPlanError:
-        return _away_mod._parse_return_time(leaf) is not None
+        return _away_mod.parse_return_time(leaf) is not None
 
 
 def _ss_absolute(value) -> bool:
@@ -42827,11 +42827,11 @@ _R10_LOG_ALLOWED_BY_REASON = {
         ("off_restore.py", "async_forget"): 1,
     },
     "one record per failed call, an event and not a held condition (the "
-    "sweep's actuation handlers, and an unexpected exception per failed update)": {
+    "sweep's actuation handlers; an unexpected exception in the update cycle is "
+    "held per entry since R11-SEAM-cycle-reporting, D1-s3-06)": {
         ("climate.py", "_async_publish_displace_from_current_action"): 1,
         ("heat_curve.py", "publish_ecl110_topics"): 2, ("coordinator.py", "_async_set_pump"): 1,
-        ("coordinator.py", "_command_frequency"): 1, ("coordinator.py", "_async_update_data"): 1,
-        ("coordinator.py", "_async_first_refresh_light"): 1, ("disinfection.py", "_write"): 2,
+        ("coordinator.py", "_command_frequency"): 1, ("disinfection.py", "_write"): 2,
         ("disinfection.py", "release"): 1, ("pump_arbiter.py", "_write"): 1,
         ("pump_arbiter.py", "switch_supply"): 1,
     },
diff --git a/tests/features.py b/tests/features.py
index 658969c8a4..30b165f6c9 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -2669,9 +2669,9 @@ if _r9f10b_clock_default:
     R.check(
         "a stored instant typed without an offset loads aware through the stub's zone "
         "(the away picker string, D1-s3-01)",
-        away_mode._parse_return_time("2026-03-04 12:30:00")
+        away_mode.parse_return_time("2026-03-04 12:30:00")
         == datetime(2026, 3, 4, 12, 30, tzinfo=timezone.utc),
-        repr(away_mode._parse_return_time("2026-03-04 12:30:00")),
+        repr(away_mode.parse_return_time("2026-03-04 12:30:00")),
     )
     R.check(
         "as_local is still the identity under the UTC default (every golden fixture "
@@ -41857,6 +41857,7 @@ _ET_KEYS = {
     "apply_schedule_comfort_band_violation": {"violations"},
     "apply_schedule_dhw_min_no_deadband": {"minimum", "setpoint", "ceiling"},
     "manual_plan_invalid_expires_at": {"expires_at"},
+    "away_invalid_return_time": {"return_time"},
     "manual_plan_invalid_slots": {"error"},
     "run_optimization_no_prices": {"entry_ids"},
     "run_optimization_solve_failed": {"entry_ids"},
@@ -42239,6 +42240,11 @@ _et_check(
     _et_call(_et_hass, "apply_manual_plan", {"expires_at": "not-a-datetime"}),
     "manual_plan_invalid_expires_at",
 )
+_et_check(
+    "set_away with an unparseable return_time raises a translatable error (D10-s1-01)",
+    _et_call(_et_hass, "set_away", {"active": True, "return_time": "18:00"}),
+    "away_invalid_return_time",
+)
 _et_check(
     "apply_manual_plan with an invalid slot raises a translatable error",
     _et_call(
@@ -50901,7 +50907,7 @@ R.check(
 
 # A SPACE-SEPARATED local time is what the frontend's picker posts, and it is
 # not an ISO instant: storing it verbatim would leave the store holding a
-# string `_parse_return_time` has to re-interpret on every read, and the
+# string `parse_return_time` has to re-interpret on every read, and the
 # expiry sweep three lines below would compare against None.
 _t1_away_str = _t1_coord()
 _t1_away_target = (dt_util.now() + timedelta(hours=3)).replace(microsecond=0)
@@ -50913,9 +50919,9 @@ R.check(
     _t1_away_str._away_state.override_active is True
     and _t1_away_stored is not None
     and _t1_away_stored != _t1_away_posted
-    and away_mode._parse_return_time(_t1_away_stored) is not None,
+    and away_mode.parse_return_time(_t1_away_stored) is not None,
     f"posted={_t1_away_posted!r} stored={_t1_away_stored!r} -- the stored form "
-    "must round-trip through _parse_return_time, which the posted one only does "
+    "must round-trip through parse_return_time, which the posted one only does "
     "by accident of the parser's tolerance",
 )
 
@@ -58405,7 +58411,7 @@ R.check(
 )
 
 
-# -- away's numbers (const.finite_float) and _parse_return_time ------------------
+# -- away's numbers (const.finite_float) and parse_return_time ------------------
 _g8_nums = {
     "None": _t6_as_float(None, 7.0),
     "int": _t6_as_float(3, 7.0),
@@ -58425,12 +58431,12 @@ R.check(
     "set the away target to 1 °C",
 )
 _g8_rt = {
-    "iso": _g8_away._parse_return_time("2026-07-12T18:00:00+00:00"),
-    "unknown": _g8_away._parse_return_time("unknown"),
-    "unavailable": _g8_away._parse_return_time("unavailable"),
-    "empty": _g8_away._parse_return_time(""),
-    "None": _g8_away._parse_return_time(None),
-    "rubbish": _g8_away._parse_return_time("next tuesday"),
+    "iso": _g8_away.parse_return_time("2026-07-12T18:00:00+00:00"),
+    "unknown": _g8_away.parse_return_time("unknown"),
+    "unavailable": _g8_away.parse_return_time("unavailable"),
+    "empty": _g8_away.parse_return_time(""),
+    "None": _g8_away.parse_return_time(None),
+    "rubbish": _g8_away.parse_return_time("next tuesday"),
 }
 R.check(
     "a return time parses, or reads as absent -- never as a raise",
@@ -64582,6 +64588,7 @@ class _PaCoord:
                 getattr(getattr(self, "_legionella", None), "disinfect", None),
                 "memo", None,
             ) is True,
+            opt_config=getattr(self, "opt", None),
         )
 
     async def async_set_mode(self, mode):
@@ -66889,7 +66896,7 @@ _SI_STHLM = _SiZone("Europe/Stockholm")
 _si_zone0 = dt_util.DEFAULT_TIME_ZONE
 dt_util.DEFAULT_TIME_ZONE = _SI_STHLM
 try:
-    _si_ret = away_mode._parse_return_time("2026-10-05T08:00")
+    _si_ret = away_mode.parse_return_time("2026-10-05T08:00")
     _si_until = boost_mod._parse_until(_SI_NAIVE)
     _si_c = _t2_coord()
     _si_key = f"heatpump_optimizer_{_si_c.entry.entry_id}_pump_duty"
@@ -80546,7 +80553,7 @@ class _EcCoord(_PaCoord):
 
     def arm(self, at=None):
         _pa_aio.run(_ec.arm(_ec.state_for(self), self.arbiter_inputs,
-                            _ec_boost_mod.held_for(self), self.opt, self.entry.async_on_unload, at))
+                            _ec_boost_mod.held_for(self), self.entry.async_on_unload, at))
 
     def room(self, value):
         ev = _PaNS(data={"new_state": FakeState(str(value), unit="°C")})
@@ -99143,4 +99150,449 @@ R.check(
     f"before={_rh_ul_before} after={_rh_ul_doc}",
 )
 
+# ---------------------------------------------------------------------------
+# R11-SEAM-cycle-reporting: how a failure is reported (D1-s3-05, D1-s3-06,
+# D1-s3-07, D10-s1-01, D7-s2-03 with ADR-003's stale holder, D10-s3-02 in
+# tests/doc_claims.py). Each arm drives the production symbol; its null
+# control is the healthy input.
+# ---------------------------------------------------------------------------
+import ast as _cr_ast  # noqa: E402
+import asyncio as _cr_aio  # noqa: E402
+import logging as _cr_logging  # noqa: E402
+import pathlib as _cr_path  # noqa: E402
+from dataclasses import replace as _cr_replace  # noqa: E402
+from types import SimpleNamespace as _CrNS  # noqa: E402
+
+from harness import FakeEntry as _CrEntry  # noqa: E402
+from homeassistant.exceptions import ServiceValidationError as _CrSVE  # noqa: E402
+from homeassistant.helpers.update_coordinator import UpdateFailed as _CrUF  # noqa: E402
+from heatpump_optimizer import coordinator as _cr_cm  # noqa: E402
+from heatpump_optimizer import diagnostics as _cr_diag  # noqa: E402
+from heatpump_optimizer import early_cutoff as _cr_ec  # noqa: E402
+from heatpump_optimizer import optimizer as _cr_opt  # noqa: E402
+from heatpump_optimizer import services as _cr_svc  # noqa: E402
+from heatpump_optimizer import store as _cr_store  # noqa: E402
+
+_CR_PKG = _cr_path.Path(_cr_cm.__file__).parent
+_CR_CFG = {"tibber_token": "x", "price_source": "tibber", "weather_entity": "weather.home",
+           "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"}
+
+
+class _CrLog(_cr_logging.Handler):
+    """Every record the package logs, as (level, message, carries a traceback)."""
+
+    def __init__(self):
+        super().__init__(_cr_logging.DEBUG)
+        self.rows = []
+
+    def emit(self, record):
+        self.rows.append((record.levelname, record.getMessage(), record.exc_info is not None))
+
+    def count(self, level, needle, *, traced=None):
+        return sum(1 for lv, msg, tb in self.rows
+                   if lv == level and needle in msg and (traced is None or tb == traced))
+
+    def above_debug(self):
+        return [r for r in self.rows if r[0] != "DEBUG"]
+
+
+def _cr_logged(fn):
+    log, logger = _CrLog(), _cr_logging.getLogger(_cr_cm.__name__.rsplit(".", 1)[0])
+    old = logger.level
+    logger.addHandler(log)
+    logger.setLevel(_cr_logging.DEBUG)
+    try:
+        fn()
+    finally:
+        logger.removeHandler(log)
+        logger.setLevel(old)
+    return log
+
+
+def _cr_coord():
+    return Coord(FakeHass(), _CrEntry(data=dict(_CR_CFG)))
+
+
+class _CrStore:
+    """A store whose save fails while ``fail`` is set; ``saved`` holds what landed."""
+
+    def __init__(self):
+        self.fail, self.saved = True, []
+
+    async def async_wait_for_read(self):
+        return None
+
+    async def async_save(self, data):
+        if self.fail:
+            raise OSError("disk full")
+        self.saved.append(data)
+
+
+# -- D1-s3-05: a persistently failing save is reported once per outage ------
+_cr_st, _cr_landed = _CrStore(), []
+
+
+def _cr_held_run():
+    for fail in (True, True, True, False, True):
+        _cr_st.fail = fail
+        _cr_landed.append(_cr_aio.run(_cr_store.save_held(
+            _cr_st, "probe store", lambda: _cr_st.async_save({"k": 1}))))
+
+
+_cr_held = _cr_logged(_cr_held_run)
+_cr_ok_st, _cr_ok_st.fail = _CrStore(), False
+_cr_ok = _cr_logged(lambda: _cr_aio.run(_cr_store.save_held(
+    _cr_ok_st, "probe store", lambda: _cr_ok_st.async_save({"k": 1}))))
+R.check(
+    "D1-s3-05: a save failing on three passes logs one ERROR with its traceback, DEBUG while it "
+    "holds, Resolved on the save that lands, and ERROR again when it recurs; it never raises; "
+    "null control, a save that lands logs nothing above DEBUG",
+    _cr_landed == [False, False, False, True, False]
+    and _cr_held.count("ERROR", "Could not persist probe store: disk full", traced=True) == 2
+    and _cr_held.count("DEBUG", "Still: Could not persist probe store") == 2
+    and _cr_held.count("INFO", "Resolved: persist probe store") == 1
+    and len(_cr_held.above_debug()) == 3 and _cr_ok.above_debug() == [] and _cr_ok_st.saved == [{"k": 1}],
+    f"landed={_cr_landed} rows={_cr_held.rows} ok={_cr_ok.rows}",
+)
+
+# A payload builder that raises is held like a failing save, not raised into the cycle.
+_cr_bug_st = _CrStore()
+_cr_bug_st.fail = False
+_cr_bug = _cr_logged(lambda: _cr_landed.append(_cr_aio.run(_cr_store.save_held(
+    _cr_bug_st, "probe payload", lambda: _cr_bug_st.async_save({"k": 1 / 0})))))
+R.check(
+    "D1-s3-05: a payload builder that raises is held as the store's failure (ERROR with its "
+    "traceback), not raised into the caller, and nothing is saved",
+    _cr_landed[-1] is False and _cr_bug_st.saved == []
+    and _cr_bug.count("ERROR", "Could not persist probe payload: division by zero", traced=True) == 1,
+    f"{_cr_bug.rows}",
+)
+
+# A production persist handler, driven with its store failing on every pass.
+_cr_led = _cr_coord()
+_cr_led._ledger_store = _CrStore()
+_cr_led_log = _cr_logged(lambda: [_cr_aio.run(_cr_led._async_save_ledger()) for _ in range(3)])
+_cr_led._ledger_store.fail = False
+_cr_led_ok = _cr_logged(lambda: _cr_aio.run(_cr_led._async_save_ledger()))
+R.check(
+    "D1-s3-05: the coordinator's ledger save failing on three cycles logs one ERROR (it was DEBUG "
+    "on every cycle), and the save that lands logs Resolved and stores the ledger",
+    _cr_led_log.count("ERROR", "Could not persist ledger", traced=True) == 1
+    and len(_cr_led_log.above_debug()) == 1
+    and _cr_led_ok.count("INFO", "Resolved: persist ledger") == 1
+    and len(_cr_led._ledger_store.saved) == 1 and "ledger" in _cr_led._ledger_store.saved[0],
+    f"fail={_cr_led_log.rows} ok={_cr_led_ok.rows}",
+)
+
+
+def _cr_save_sites():
+    """Each store save call in the package: (file, line, how a failure is reported).
+
+    ``held``: inside a callable handed to ``store.save_held``. ``propagates``: under no
+    broad handler, so a failure reaches the caller. ``swallowed``: under a broad handler
+    with neither, the shape D1-s3-05 found at every persist handler.
+    """
+    out = []
+    for path in sorted(_CR_PKG.glob("*.py")):
+        if path.name == "store.py":  # the store's own wrappers of the base class's save
+            continue
+        tree = _cr_ast.parse(path.read_text())
+        parents = {c: p for p in _cr_ast.walk(tree) for c in _cr_ast.iter_child_nodes(p)}
+        handed = set()  # the callables handed to save_held: lambdas, and local defs by name
+        for call in _cr_ast.walk(tree):
+            if isinstance(call, _cr_ast.Call) and getattr(call.func, "id", None) == "save_held":
+                arg = call.args[2]
+                handed.add(arg if isinstance(arg, _cr_ast.Lambda) else ("def", arg.id, parents[call]))
+        for call in _cr_ast.walk(tree):
+            fn = call.func if isinstance(call, _cr_ast.Call) else None
+            if not (isinstance(fn, _cr_ast.Attribute) and fn.attr in ("async_save", "async_save_if_changed")):
+                continue
+            if isinstance(fn.value, _cr_ast.Name) and fn.value.id == "self":  # a method's own wrapper
+                continue
+            how, node = "propagates", call
+            while node in parents:
+                node = parents[node]
+                if node in handed or (isinstance(node, _cr_ast.AsyncFunctionDef) and any(
+                        h[0] == "def" and h[1] == node.name for h in handed if isinstance(h, tuple))):
+                    how = "held"
+                    break
+                if isinstance(node, _cr_ast.Try) and any(
+                        h.type is None or _cr_ast.unparse(h.type) in ("Exception", "BaseException")
+                        for h in node.handlers):
+                    how = "swallowed"
+                    break
+            out.append((path.name, call.lineno, how))
+    return out
+
+
+_cr_sites = _cr_save_sites()
+_cr_by = {how: [s for s in _cr_sites if s[2] == how] for how in ("held", "propagates", "swallowed")}
+R.check(
+    "D1-s3-05 census: every store save in the package is held through save_held or propagates to "
+    "its caller, none swallowed under a broad handler; precondition, the census finds the 18 "
+    "persist handlers persist_seams.py enumerated at the merge base, each now held",
+    _cr_by["swallowed"] == [] and len(_cr_by["held"]) >= 18
+    and {f for f, _, _ in _cr_by["held"]} >= {
+        "away.py", "boost.py", "coordinator.py", "debugger.py", "dhw_learning.py", "duty_switch.py",
+        "legionella.py", "notifier.py", "off_restore.py", "pump_arbiter.py", "room_record.py"},
+    f"{_cr_by}",
+)
+
+# -- D1-s3-06: the update cycle's generic arm logs a persisting failure once ---
+_cr_up = _cr_coord()
+_cr_up_outcomes = []
+
+
+async def _cr_noop(*_a, **_k):
+    return None
+
+
+async def _cr_broken(*_a, **_k):
+    raise RuntimeError("sensor bus down")
+
+
+def _cr_update_run():
+    for first in (False, False, True):  # two cycles, then a setup-time refresh
+        _cr_up._skip_solve_once = first
+        try:
+            _cr_aio.run(_cr_up._async_update_data())
+            _cr_up_outcomes.append("ok")
+        except _CrUF as err:
+            _cr_up_outcomes.append(err.translation_key)
+
+
+for _cr_name in ("_fetch_tibber_prices", "_fetch_weather_forecast", "_fetch_solar_forecast",
+                 "_async_learn_price_shape"):
+    setattr(_cr_up, _cr_name, _cr_noop)
+_cr_up._update_current_state = _cr_broken
+
+
+def _cr_retry_run():
+    """Two cycles and a setup-time refresh, then a setup retry: a new coordinator, same entry."""
+    global _cr_up
+    _cr_update_run()
+    first = _cr_up
+    _cr_aio.run(first.async_shutdown())  # a failed setup shuts its coordinator down, forgetting hass's latches
+    _cr_up = Coord(first.hass, first.entry)
+    for _name in ("_fetch_tibber_prices", "_fetch_weather_forecast", "_fetch_solar_forecast",
+                  "_async_learn_price_shape"):
+        setattr(_cr_up, _name, _cr_noop)
+    _cr_up._update_current_state = _cr_broken
+    _cr_up._skip_solve_once = True
+    try:
+        _cr_aio.run(_cr_up._async_update_data())
+    except _CrUF as err:
+        _cr_up_outcomes.append(err.translation_key)
+
+
+_cr_up_log = _cr_logged(_cr_retry_run)
+_cr_up._update_current_state = _cr_noop
+_cr_up._build_data_dict = lambda: {"recovered": True}
+
+
+def _cr_recover_run():
+    _cr_up._skip_solve_once = True
+    _cr_up_outcomes.append(_cr_aio.run(_cr_up._async_update_data()))
+    _cr_up._update_current_state = _cr_broken
+    _cr_update_run()
+
+
+_cr_rec_log = _cr_logged(_cr_recover_run)
+R.check(
+    "D1-s3-06: an unexpected failure persisting over two cycles, a setup-time refresh and a setup "
+    "retry's new coordinator logs one ERROR with its traceback (it was ERROR on every cycle and "
+    "every retry), each a translated UpdateFailed; the "
+    "refresh that succeeds logs Resolved, and the recurrence is an ERROR again (null control: "
+    "the transition is still reported)",
+    _cr_up_outcomes[:4] == ["update_failed"] * 4
+    and _cr_up_log.count("ERROR", "Error updating Heat Pump Optimizer: sensor bus down", traced=True) == 1
+    and len(_cr_up_log.above_debug()) == 1
+    and _cr_up_outcomes[4] == {"recovered": True}
+    and _cr_rec_log.count("INFO", "Resolved: update failed") == 1
+    and _cr_rec_log.count("ERROR", "Error updating Heat Pump Optimizer: sensor bus down") == 1,
+    f"outcomes={_cr_up_outcomes} first={_cr_up_log.rows} recover={_cr_rec_log.rows}",
+)
+
+# -- D1-s3-07: a broad handler that swallows leaves a record ------------------
+_cr_best = _CrNS(x=[0.5])
+_cr_restart_log = _cr_logged(lambda: _cr_landed.append(_cr_opt._lbfgsb_restart(
+    _cr_best, lambda x, *a: (_ for _ in ()).throw(RuntimeError("objective blew up")),
+    [(0.0, 1.0)], (), 5, None)))
+_cr_sum_coord = _CrNS(_accuracy=_CrNS(summary=lambda: 1 / 0))
+_cr_sum_log = _cr_logged(lambda: _cr_landed.append(
+    _cr_cm.CoordinatorDiagnostics.of(_cr_sum_coord).learner_summaries))
+_cr_view_log = _cr_logged(lambda: _cr_landed.append(
+    _cr_diag._never_breaks(lambda c: 1 / 0, None)))
+R.check(
+    "D1-s3-07: the L-BFGS-B restart, a learner summary and a diagnostics view that raise keep "
+    "their fallbacks (the start's point, 'summary unavailable', 'unavailable') and now each "
+    "leave a DEBUG record carrying the traceback; nothing above DEBUG",
+    _cr_landed[-3] is _cr_best and _cr_landed[-2] == {"accuracy": "summary unavailable"}
+    and _cr_landed[-1] == "unavailable"
+    and all(log.count("DEBUG", "", traced=True) >= 1 and log.above_debug() == []
+            for log in (_cr_restart_log, _cr_sum_log, _cr_view_log)),
+    f"restart={_cr_restart_log.rows} summary={_cr_sum_log.rows} view={_cr_view_log.rows}",
+)
+
+# _capture_diagnosis_inputs: a state that cannot be copied is no evidence (None), a weather
+# read that raises records wind 0.0; each now leaves a DEBUG record.
+_cr_dx = _cr_coord()
+_cr_dx_state = _cr_dx._ctx._current_state
+_cr_dx._ctx = _cr_replace(_cr_dx._ctx, _current_state=object())
+_cr_dx_none_log = _cr_logged(lambda: _cr_landed.append(_cr_dx._capture_diagnosis_inputs()))
+_cr_dx._ctx = _cr_replace(_cr_dx._ctx, _current_state=_cr_dx_state)
+_cr_dx._current_weather = lambda: (_ for _ in ()).throw(RuntimeError("no weather"))
+_cr_dx_wind_log = _cr_logged(lambda: _cr_landed.append(_cr_dx._capture_diagnosis_inputs()))
+R.check(
+    "D1-s3-07: diagnosis inputs whose state cannot be copied are None, and a weather read that "
+    "raises records the plan's wind as 0.0; each leaves a DEBUG record with its traceback",
+    _cr_landed[-2] is None and isinstance(_cr_landed[-1], dict)
+    and _cr_landed[-1]["planned"]["wind_speed"] == 0.0
+    and _cr_dx_none_log.count("DEBUG", "Diagnosis inputs not captured", traced=True) == 1
+    and _cr_dx_wind_log.count("DEBUG", "Diagnosis wind not captured", traced=True) == 1,
+    f"none={_cr_landed[-2]!r} wind={_cr_landed[-1] if isinstance(_cr_landed[-1], str) else 'dict'} "
+    f"logs={_cr_dx_none_log.rows} {_cr_dx_wind_log.rows}",
+)
+
+# diagnosis.attribute: a baseline the model cannot simulate is no report (None), recorded.
+from heatpump_optimizer import diagnosis as _cr_dg  # noqa: E402
+
+
+def _cr_attribute():
+    try:
+        return _cr_dg.attribute(_CrNS(simulate_step=lambda *a, **k: 1 / 0), _cr_dx_state, {}, {}, 21.0)
+    except Exception as err:  # a mutant that runs on without its baseline fails the check
+        return repr(err)
+
+
+_cr_dg_log = _cr_logged(lambda: _cr_landed.append(_cr_attribute()))
+R.check(
+    "D1-s3-07 seam rule: a diagnosis whose baseline cannot be simulated is no report (None), and "
+    "leaves a DEBUG record with its traceback",
+    _cr_landed[-1] is None and _cr_dg_log.count("DEBUG", "Diagnosis baseline not simulated", traced=True) == 1,
+    f"{_cr_landed[-1]!r} {_cr_dg_log.rows}",
+)
+
+
+def _cr_silent(path, func):
+    """The broad handlers of ``func`` in ``path`` that neither raise nor call anything logging."""
+    tree = _cr_ast.parse((_CR_PKG / path).read_text())
+    fns = [n for n in _cr_ast.walk(tree) if isinstance(n, (_cr_ast.FunctionDef, _cr_ast.AsyncFunctionDef))
+           and n.name == func]
+    assert len(fns) == 1, (path, func, len(fns))
+    broad = [h for n in _cr_ast.walk(fns[0]) if isinstance(n, _cr_ast.Try) for h in n.handlers
+             if h.type is None or _cr_ast.unparse(h.type) in ("Exception", "BaseException")]
+    silent = [h.lineno for h in broad if not any(
+        isinstance(c, (_cr_ast.Raise,)) or (isinstance(c, _cr_ast.Call) and "_LOGGER" in _cr_ast.unparse(c.func))
+        for c in _cr_ast.walk(_cr_ast.Module(body=h.body, type_ignores=[])))]
+    return len(broad), silent
+
+
+_CR_SILENT_SEAMS = [  # D1-s3-07's seven, and the evidence fallbacks D1-s3-07's seam rule returns
+    ("coordinator.py", "_record_accuracy"), ("coordinator.py", "_capture_diagnosis_inputs"),
+    ("coordinator.py", "of"), ("diagnostics.py", "_coordinator_snapshot"),
+    ("diagnostics.py", "_never_breaks"), ("optimizer.py", "_lbfgsb_restart"),
+    ("coordinator.py", "_stored_fuse_advisor"), ("coordinator.py", "_track_curve_comfort"),
+    ("coordinator.py", "_raise_cop_issue"), ("optimizer.py", "_solver_status"),
+    ("config_flow.py", "_omit_unstored_computed"),
+    ("config_flow.py", "_prefilled_values"), ("diagnosis.py", "attribute"),
+]
+_cr_silent_found = {s: _cr_silent(*s) for s in _CR_SILENT_SEAMS}
+R.check(
+    "D1-s3-07 census: each named handler's function holds a broad handler (precondition: the seam "
+    "is where the census reads it) and none of them is silent",
+    all(n >= 1 and silent == [] for n, silent in _cr_silent_found.values()),
+    f"{_cr_silent_found}",
+)
+
+# -- D10-s1-01: set_away refuses a return time that neither clears nor parses --
+_CR_BAD_RETURNS = ["18:00", "tomorrow", "2026-13-01T10:00:00", "not a date", "25:99", " x "]
+_CR_GOOD_RETURNS = [None, "", "unknown", "unavailable", "2026-07-12T18:00:00+00:00", "2026-07-12 18:00"]
+
+
+class _CrAwayCoord:
+    def __init__(self):
+        self.calls = []
+
+    async def async_set_away(self, **kwargs):
+        self.calls.append(kwargs)
+
+
+_cr_away_coord = _CrAwayCoord()
+_cr_loaded = _cr_svc._loaded_coordinators
+_cr_svc._loaded_coordinators = lambda hass, target_entry=None: [("e1", _cr_away_coord)]
+_cr_refused = []
+try:
+    for _cr_raw in _CR_BAD_RETURNS + _CR_GOOD_RETURNS:
+        try:
+            _cr_aio.run(_cr_svc.handle_set_away(FakeHass(), _CrNS(data={"active": True, "return_time": _cr_raw})))
+        except _CrSVE as _cr_err:
+            _cr_refused.append((_cr_raw, _cr_err.translation_key, _cr_err.translation_placeholders))
+finally:
+    _cr_svc._loaded_coordinators = _cr_loaded
+R.check(
+    "D10-s1-01: set_away refuses each of six return times that neither clear nor parse with the "
+    "translated away_invalid_return_time, before any write; null control, the clearing values and "
+    "two parseable times reach the coordinator unchanged",
+    [r[0] for r in _cr_refused] == _CR_BAD_RETURNS
+    and all(k == "away_invalid_return_time" and p == {"return_time": str(raw)} for raw, k, p in _cr_refused)
+    and [c["return_time"] for c in _cr_away_coord.calls] == _CR_GOOD_RETURNS,
+    f"refused={_cr_refused} calls={_cr_away_coord.calls}",
+)
+
+# -- D7-s2-03 / ADR-003: a change publishes a new context; the held cutoff reads it --
+_cr_ctx = _cr_coord()
+_cr_old = _cr_ctx._ctx
+_cr_old_cfg = (_cr_old._opt_config.target_temp, _cr_old._opt_config.comfort_weight)
+_cr_aio.run(_cr_ctx.async_set_target_temperature(_cr_old_cfg[0] + 1.0))
+_cr_mid = _cr_ctx._ctx
+_cr_ctx._comfort_weight = lambda: _cr_old_cfg[1] + 2.0
+_cr_ctx._apply_comfort_weight()
+R.check(
+    "D7-s2-03: a target change and a comfort-weight change each publish a new context; a holder of "
+    "the old context keeps the values it was handed (it saw both edits through the shared config)",
+    (_cr_old._opt_config.target_temp, _cr_old._opt_config.comfort_weight) == _cr_old_cfg
+    and _cr_mid is not _cr_old and _cr_mid._opt_config.target_temp == _cr_old_cfg[0] + 1.0
+    and _cr_mid._opt_config.comfort_weight == _cr_old_cfg[1]
+    and _cr_ctx._ctx is not _cr_mid and _cr_ctx._ctx._opt_config.comfort_weight == _cr_old_cfg[1] + 2.0
+    and _cr_ctx._ctx._opt_config.target_temp == _cr_old_cfg[0] + 1.0,
+    f"old={_cr_old._opt_config.target_temp, _cr_old._opt_config.comfort_weight} "
+    f"mid={_cr_mid._opt_config.target_temp, _cr_mid._opt_config.comfort_weight} "
+    f"live={_cr_ctx._ctx._opt_config.target_temp, _cr_ctx._ctx._opt_config.comfort_weight}",
+)
+
+# ADR-003's stale-holder acceptance: the cutoff armed with the coordinator's own inputs,
+# then a published change, judges the next reading on the replaced configuration.
+_cr_held_ec = _cr_ec.CutoffState()
+_cr_now = datetime.now(timezone.utc)
+# A plan colder than any comfort target, so the target is what sets the threshold.
+_cr_ctx._optimization_result = _CrNS(timestamps=[_cr_now - timedelta(minutes=15), _cr_now + timedelta(minutes=15)],
+                                     room_temp_trajectory=[5.0, 5.0, 5.0])
+_cr_aio.run(_cr_ec.arm(_cr_held_ec, _cr_ctx.arbiter_inputs, None, lambda _f: None))
+
+
+def _cr_threshold():
+    """The held cutoff's threshold now; a mutant that drops the config fails the check below."""
+    try:
+        return _cr_ec.threshold(_cr_held_ec.wiring.inputs(), _cr_now)
+    except AttributeError as err:
+        return repr(err)
+
+
+_cr_before = _cr_threshold()
+_cr_cfg_now = _cr_ctx._ctx._opt_config
+_cr_ctx._ctx.publish_config(_cr_ctx, comfort_temp_day=_cr_cfg_now.comfort_temp_day + 3.0,
+                            comfort_temp_night=_cr_cfg_now.comfort_temp_night + 3.0)
+_cr_seen = _cr_held_ec.wiring.inputs().opt_config
+_cr_after = _cr_threshold()
+R.check(
+    "ADR-003 stale holder: after the cutoff is armed, a published configuration change is what the "
+    "held cutoff reads at the next reading (its threshold rises by the 3.0 K the comfort target "
+    "rose); null control, the threshold read before the change is the old target's",
+    _cr_seen is _cr_ctx._ctx._opt_config and _cr_seen is not _cr_cfg_now
+    and isinstance(_cr_before, float) and isinstance(_cr_after, float)
+    and abs((_cr_after - _cr_before) - 3.0) < 1e-9,
+    f"before={_cr_before} after={_cr_after} seen_is_live={_cr_seen is _cr_ctx._ctx._opt_config}",
+)
+
 sys.exit(R.close("FEATURE CHECKS"))
diff --git a/tests/mutation_ledger/killed_by/away.py/clears_return_time.RETURN_DEL.05ea228a.json b/tests/mutation_ledger/killed_by/away.py/clears_return_time.RETURN_DEL.05ea228a.json
new file mode 100644
index 0000000000..d78b5e7562
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/away.py/clears_return_time.RETURN_DEL.05ea228a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/away.py:clears_return_time RETURN_DEL 05ea228a",
+  "killed_by": "tests/features.py",
+  "old": "    return not raw or str(raw).strip().lower() in (\"unknown\", \"unavailable\", \"\")",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/away.py/_parse_return_time.RETURN_DEL.17d5e3f1.json b/tests/mutation_ledger/killed_by/away.py/parse_return_time.RETURN_DEL.17d5e3f1.json
similarity index 75%
rename from tests/mutation_ledger/killed_by/away.py/_parse_return_time.RETURN_DEL.17d5e3f1.json
rename to tests/mutation_ledger/killed_by/away.py/parse_return_time.RETURN_DEL.17d5e3f1.json
index 1e453ff9e6..f8ff08a66d 100644
--- a/tests/mutation_ledger/killed_by/away.py/_parse_return_time.RETURN_DEL.17d5e3f1.json
+++ b/tests/mutation_ledger/killed_by/away.py/parse_return_time.RETURN_DEL.17d5e3f1.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/away.py:_parse_return_time RETURN_DEL 17d5e3f1",
+  "anchor": "custom_components/heatpump_optimizer/away.py:parse_return_time RETURN_DEL 17d5e3f1",
   "killed_by": "tests/features.py",
   "old": "    return stored_instant(value, dt_util.DEFAULT_TIME_ZONE)",
   "reason": "Recorded by `mutation_table.py --pin-killed` against db878b29fa301d44231ccec55a85a80d610e9b1e: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=16."
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.RETURN_DEL.35324698.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.RETURN_DEL.35324698.json
deleted file mode 100644
index e1d1c1d0fa..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.RETURN_DEL.35324698.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_first_refresh_light RETURN_DEL 35324698",
-  "killed_by": "tests/features.py",
-  "old": "            return self._build_data_dict()",
-  "reason": "Recorded by `mutation_table.py --drain` against e8c67e1d3df151a8f273443a5ac5f736fb543782: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_update_data.RETURN_DEL.3bda3d97.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_update_data.RETURN_DEL.3bda3d97.json
deleted file mode 100644
index 3fe0fdd542..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_update_data.RETURN_DEL.3bda3d97.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_update_data RETURN_DEL 3bda3d97",
-  "killed_by": "tests/features.py",
-  "old": "            return await _with_sensor_advisor(self, self._build_data_dict())",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 830f84ad7a25453248a7709f4dfd13769b2d9684: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capture_diagnosis_inputs.RETURN_DEL.440ee7e3.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capture_diagnosis_inputs.RETURN_DEL.440ee7e3.json
new file mode 100644
index 0000000000..ee780882cb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._capture_diagnosis_inputs.RETURN_DEL.440ee7e3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._capture_diagnosis_inputs RETURN_DEL 440ee7e3",
+  "killed_by": "tests/features.py",
+  "old": "            return None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_lbfgsb_restart.RETURN_DEL.9f13e26c.json b/tests/mutation_ledger/killed_by/optimizer.py/_lbfgsb_restart.RETURN_DEL.9f13e26c.json
new file mode 100644
index 0000000000..e85e4e5c38
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_lbfgsb_restart.RETURN_DEL.9f13e26c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_lbfgsb_restart RETURN_DEL 9f13e26c",
+  "killed_by": "tests/features.py",
+  "old": "        return best",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/store.py/save_held.RETURN_DEL.80a0007e.json b/tests/mutation_ledger/killed_by/store.py/save_held.RETURN_DEL.80a0007e.json
new file mode 100644
index 0000000000..cc4ed99a32
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/store.py/save_held.RETURN_DEL.80a0007e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/store.py:save_held RETURN_DEL 80a0007e",
+  "killed_by": "tests/features.py",
+  "old": "    return True",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/survivor_triage/away.py/parse_return_time.GUARD_OFF.48f338a4.json b/tests/mutation_ledger/survivor_triage/away.py/parse_return_time.GUARD_OFF.48f338a4.json
new file mode 100644
index 0000000000..6d4cb54af6
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/away.py/parse_return_time.GUARD_OFF.48f338a4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/away.py:parse_return_time GUARD_OFF 48f338a4",
+  "old": "    if clears_return_time(raw):",
+  "reason": "Equivalent. With the guard off, a clearing value falls through to stored_instant(str(raw).strip(), zone), which returns None for every clearing spelling clears_return_time admits (None, '', 'unknown', 'unavailable', any case or padding), measured at the R11-SEAM-cycle-reporting head through heatpump_optimizer.drift.stored_instant; parse_return_time returns None either way. The set_away refusal calls clears_return_time itself, so the guard decides no refusal.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/coordinator.py/_stored_fuse_advisor.RETURN_DEL.d7923b87.json b/tests/mutation_ledger/survivor_triage/coordinator.py/_stored_fuse_advisor.RETURN_DEL.d7923b87.json
new file mode 100644
index 0000000000..2a2cb71e75
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/coordinator.py/_stored_fuse_advisor.RETURN_DEL.d7923b87.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_stored_fuse_advisor RETURN_DEL d7923b87",
+  "old": "        return None",
+  "reason": "Equivalent. The return is the last statement of the except arm, and nothing follows the try in _stored_fuse_advisor, so deleting it falls off the end of the coroutine, which returns None: the value the deleted line returned.",
+  "verdict": "equivalent"
+}
diff --git a/tests/seam_map.json b/tests/seam_map.json
index 3f77543780..5748a6f215 100644
--- a/tests/seam_map.json
+++ b/tests/seam_map.json
@@ -254,6 +254,7 @@
   "coordinator._warm_seeded": "core",
   "coordinator._watch_lift": "learning",
   "coordinator._with_sensor_advisor": "core",
+  "coordinator._fail_update_held": "core",
   "coordinator.model_restart_advice": "views",
   "describe_setup": "core",
   "device_info": "core",
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 05bea24c45..ff8a6efaa9 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17317,
+ "class_excess_loc": 17313,
  "const_modules_over_50": 3,
  "coordinator_attrs": 136,
  "coordinator_multiassigned_attrs": 104,
@@ -12,12 +12,12 @@
  "import_cycle_modules": 0,
  "in_function_copies": 11,
  "max_cc": 44,
- "max_class_loc": 7868,
+ "max_class_loc": 7860,
  "max_method_loc": 373,
  "methods_over_150": 14,
  "methods_over_200": 7,
  "name_kept_members": 38,
- "recorded_at": "8751943e17ef4d3ec699e7859ae829b4528d8ce7",
+ "recorded_at": "a8efe1d1c2a8f1e0b44cdf1046a0ea4ca2155a3b",
  "seam_cut_total": 413,
  "unloaded_package_imports": 14
 }
diff --git a/tools/pr/prepr.sh b/tools/pr/prepr.sh
index 013b57d8ca..b7baeea206 100755
--- a/tools/pr/prepr.sh
+++ b/tools/pr/prepr.sh
@@ -3352,7 +3352,7 @@ https://claude.ai/code/session_011aqzm4YL9jLhU4jLvbkLYE'; got=$(lpush)
   st $? 0 "6d predicts ADDED UNPINNED for a guard the diff adds with no pin"
   grep -q '^rc=0$' <<<"$got"
   st $? 0 "and an unpinned site warns, never refuses: mutation-autofix may pin it after the push"
-  got=$(predict_at pstale); grep -q 'PREDICT ledger .*STALE PIN custom_components/heatpump_optimizer/away.py:_parse_return_time' <<<"$got"
+  got=$(predict_at pstale); grep -q 'PREDICT ledger .*STALE PIN custom_components/heatpump_optimizer/away.py:_*parse_return_time' <<<"$got"
   st $? 0 "6d predicts STALE PIN for a pinned line the diff edits, and refuses on it (rc=1)"
   grep -q '^rc=1$' <<<"$got"
   st $? 0 "a stale pin refuses, unlike an unpinned site: mutation-autofix never drops a pin"

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
