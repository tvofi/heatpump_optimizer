# Review packet #3015
head: b7c376a3228f1c0b9a794c5f6cc5f71a29fdae4f
base: 18b788ac20af17ecfe83c552420926fbcb05290b

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124402003106 neutral
arch-score / arch-score id=124401864406 success
arm id=124401743741 skipped
budget-raise-gate / budget-raise-gate id=124401864388 success
cancel-superseded id=124401742752 success
codeql / Analyze (actions) id=124401863887 success
codeql / Analyze (javascript-typescript) id=124401863912 success
codeql / Analyze (python) id=124401864020 in_progress
governance / delivery-status id=124401864240 success
governance / delivery-status-publish id=124401865150 skipped
governance / env-matrix id=124401864174 success
governance / instrument-self-tests id=124401864129 in_progress
governance / policy-docs id=124401864268 success
governance / record id=124401865089 skipped
governance / wave-script id=124401864290 success
hassfest / hassfest id=124401863855 success
kernel-points id=124401865111 skipped
prelude id=124401742962 success
refresh id=124401742931 success
tests / arch-instrument id=124401985235 success
tests / briefs id=124401864045 success
tests / browser id=124401985111 success
tests / closure-scope id=124401864000 success
tests / closures id=124401985201 in_progress
tests / coverage id=124401985220 in_progress
tests / fast (3.14) id=124401985184 in_progress
tests / mutation id=124401864077 in_progress
tests / nightly-ha id=124401986242 skipped
tests / nightly-status id=124401863974 success
tests / replay id=124401985145 success
tests / typing id=124401985133 success
validate / validate-hacs id=124401863875 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 7c4444b2: dismissed:cosmetic until the first solve, and resolving in setup would start the process worker there
NOTE body item 60966b4c: dismissed:landed in-tree, in the census header in tests/features.py
NOTE body item da82aad9: dismissed:R10-HOTFIX-AWAY-SETBACK merged as #3013 (18b788ac2); merge-tree against main is clean; the semantic overlap in away.py is the reviewer's to check
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         tests/features.py
             `tests/features.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/features.py
             `tests/features.py` is in the tree at this head
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/structure.py --record
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         tests/stress.py
             `tests/stress.py` is in the tree at this head

FIGURES: 9 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.BOOLOP.aa838ac4.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.BOOLOP.aa838ac4.json
new file mode 100644
index 000000000..4f7292845
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.BOOLOP.aa838ac4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_first_refresh_light BOOLOP aa838ac4",
+  "killed_by": "tests/features.py",
+  "old": "        if handover is not None and away_mode.published_under(self._away_state, handover):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if handover is not None or away_mode.published_under(self._away_state, handover):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.GUARD_OFF.026f6cc7.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.GUARD_OFF.026f6cc7.json
deleted file mode 100644
index 970d2673a..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.GUARD_OFF.026f6cc7.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_first_refresh_light GUARD_OFF 026f6cc7",
-  "killed_by": "tests/features.py",
-  "old": "        if handover is not None:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.GUARD_OFF.aa838ac4.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.GUARD_OFF.aa838ac4.json
new file mode 100644
index 000000000..5db7fd88d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.GUARD_OFF.aa838ac4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_first_refresh_light GUARD_OFF aa838ac4",
+  "killed_by": "tests/features.py",
+  "old": "        if handover is not None and away_mode.published_under(self._away_state, handover):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/away.py b/custom_components/heatpump_optimizer/away.py
index d66951e6e..8374c5823 100644
--- a/custom_components/heatpump_optimizer/away.py
+++ b/custom_components/heatpump_optimizer/away.py
@@ -373,6 +373,12 @@ def apply_override_payload(state: AwayState, payload: dict[str, Any]) -> AwaySta
                    migrated_helpers=bool(payload.get("migrated_helpers")))
 
 
+def published_under(state: AwayState, view: Mapping[str, Any]) -> bool:
+    """Whether ``view``, a published payload, was built under ``state``'s override."""
+    return (bool(view.get("away_override_active")) == state.override_active
+            and view.get("away_override_return_time") == state.override_return_iso)
+
+
 async def persist_override(coord: _AwayCoord, state: AwayState) -> None:
     """Save ``state`` -- the coordinator's away state, passed in (#1739)."""
     try:
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index bd7a38ab2..c34106942 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -5833,23 +5833,20 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
     async def _async_first_refresh_light(self) -> Payload:
         """The setup-time refresh: publish something valid without solving.
 
-        Runs at most once per setup, when ``async_setup_entry`` set
-        ``_skip_solve_once``. Two cases:
-
-        * After an in-process reload the unload handler passed the previous
-          plan through ``_reload_handover``; ages are recomputed, with no
-          fetches at all — an options save must not wait on Tibber. The
-          background refresh scheduled at the end of setup replaces it with
-          a freshly solved plan within the first cycle.
-        * On a genuinely fresh start there is nothing to hand over, so the
-          cheap reads run — live sensor state, prices, weather — and the
-          payload is built without a plan. Only the solve and its dependents
-          (actuation, accuracy pairing, drift heartbeat) are skipped: none
-          of them makes sense before a plan exists.
+        Runs once per setup, when ``async_setup_entry`` set ``_skip_solve_once``,
+        after the session restore; the background refresh setup schedules solves.
+
+        * After an in-process reload, the plan the unload handler passed through
+          ``_reload_handover``, its ages recomputed and nothing fetched (an options
+          save must not wait on Tibber) -- unless it was published under another
+          away override than the restored one: the reload cancelled that solve.
+        * Otherwise the cheap reads run (sensors, prices, weather) and the payload
+          is built without a plan, so the solve's dependents (actuation, accuracy
+          pairing, drift heartbeat) wait for the background refresh.
         """
-        handover = self._reload_handover
-        self._reload_handover = None
-        if handover is not None:
+        handover, self._reload_handover = self._reload_handover, None
+        await boost.session_restored(self)
+        if handover is not None and away_mode.published_under(self._away_state, handover):
             _LOGGER.debug(
                 "First refresh republishes the pre-reload plan; the real "
                 "solve follows in the background"
@@ -9598,6 +9595,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
 
     async def _resolve_away(self) -> None:
         """Work out whether the house is empty, and when it must be warm again."""
+        await boost.session_restored(self)  # read after the stored override lands, as writers do (L3)
         ctx = getattr(self, "_ctx", self)
         config = away_mode.config_from_mapping(ctx._config)
         now = dt_util.now()
diff --git a/dev/programme/delivery/3015.md b/dev/programme/delivery/3015.md
new file mode 100644
index 000000000..06fa98d1c
--- /dev/null
+++ b/dev/programme/delivery/3015.md
@@ -0,0 +1 @@
+- [#3015](https://github.com/tvofi/heatpump_optimizer/pull/3015) — **open**, HOTFIX R10-HOTFIX-AWAY-LIVE: the away override survives an entry reload and the restore (R10-HOTFIX-AWAY-LIVE)
diff --git a/tests/features.py b/tests/features.py
index d8b045083..d348d25d0 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -13210,7 +13210,9 @@ for _race_name, (_race_load, _race_cmd, _race_read, _race_want) in _RACES.items(
 # are a subset. Preconditions: every store built is read at startup, every
 # read has a previous run's payload to land, and the loads assign something.
 # Null control: the same race with every store's fence (async_wait_for_read)
-# removed must differ, or the window reaches no writer and the census is blind.
+# and the session-restore gate the setup refresh awaits (boost.session_restored,
+# R10-HOTFIX-AWAY-LIVE) removed must differ, or the window reaches no writer
+# and the census is blind.
 import logging as _src_logging  # noqa: E402
 import weakref as _src_weakref  # noqa: E402
 from unittest import mock as _src_mock  # noqa: E402
@@ -13382,7 +13384,8 @@ with _src_mock.patch.object(_src_dt, "now", lambda *a, **k: _src_clock[0]), \
         _src_differ["fenced"][_src_key] = [
             k for k in _src_assigned if _src_raced[k] != _src_serial[k]]
     _src_differ = {"fenced": {k: v for k, v in _src_differ["fenced"].items() if v}}
-    with _src_mock.patch.object(_src_store.QuarantiningStore, "async_wait_for_read", _src_no_fence):
+    with _src_mock.patch.object(_src_store.QuarantiningStore, "async_wait_for_read", _src_no_fence), \
+            _src_mock.patch.object(_src_boost, "session_restored", _src_no_fence):
         _src_raced = _src_snapshot(_src_restart(_src_disk_then, race=True))
         _src_unfenced_serial = _src_snapshot(_src_restart(_src_disk_then, race=False))
     _src_differ["unfenced"] = [
@@ -71955,6 +71958,104 @@ R.check(
 )
 
 
+# R10-HOTFIX-AWAY-LIVE (tvofi, 2026-10-30): the away override was on disk and
+# not in the plan. Each path that carries it, through the production coordinator:
+# a resolve that runs before the restore lands, and a reload whose handover was
+# published before the switch's own solve could (an options save cancels it).
+_al_disk: dict = {}
+
+
+async def _al_load(store, what):
+    return dict(_al_disk) if "away" in what else None
+
+
+async def _al_save(coord, state):
+    _al_disk.update(away_mode._override_payload(state))
+
+
+async def _al_noop(*args, **kwargs):
+    return None
+
+
+def _al_coord(hass, **kwargs):
+    """A coordinator over the restore-only hass, its setup reads stubbed out."""
+    coord = Coord(hass, _LsEntry(data={
+        "tibber_token": "x", "weather_entity": "weather.home", "away_temperature": 15.0}), **kwargs)
+    for name in ("_update_current_state", "_fetch_tibber_prices", "_fetch_weather_forecast",
+                 "_fetch_solar_forecast", "_async_learn_price_shape"):
+        setattr(coord, name, _al_noop)
+    return coord
+
+
+def _al_bands(coord):
+    """The comfort day band and floor the solve plans with, and away_active."""
+    cfg = coord._solve_hubs(8, banded=True)[0]
+    return cfg.comfort_temp_day, cfg.min_temp, coord._away_state.active
+
+
+async def _al_reload(switch):
+    """The last publish, the switch or not, a reload: the first publish and solve."""
+    _al_disk.clear()
+    _al_disk.update(away_mode.empty_override(), migrated_helpers=True)
+    hass = _LsRestoreHass()
+    old = _al_coord(hass)
+    await hass.restores[0]
+    published = old._build_data_dict()
+    published["last_optimization"] = dt_util.now() - timedelta(minutes=14)
+    if switch:
+        await old.async_set_away(active=True, return_time=(
+            dt_util.now() + timedelta(hours=24)).isoformat(), refresh=False)
+    new = _al_coord(hass, skip_first_solve=True, reload_handover=published)
+    first = await new._async_update_data()
+    await new._resolve_away()
+    return (first is published, first.get("away_override_active"), _al_bands(new),
+            new._opt_config.comfort_temp_day)
+
+
+async def _al_resolve_first(return_in_h):
+    """A stored override, and a resolve before the restore's task has run a step."""
+    _al_disk.clear()
+    _al_disk.update(active=True, migrated_helpers=True, return_time=(
+        dt_util.now() + timedelta(hours=return_in_h)).isoformat())
+    coord = _al_coord(_LsRestoreHass())
+    await coord._resolve_away()
+    return _al_bands(coord), coord._away_state.override_active
+
+
+_al_saved = (away_mode.load_mapping, away_mode.persist_override)
+away_mode.load_mapping, away_mode.persist_override = _al_load, _al_save
+try:
+    _al_on, _al_off = _ls_aio.run(_al_reload(True)), _ls_aio.run(_al_reload(False))
+    _al_first, _al_lapsed = _ls_aio.run(_al_resolve_first(24.0)), _ls_aio.run(_al_resolve_first(-1.0))
+finally:
+    away_mode.load_mapping, away_mode.persist_override = _al_saved
+R.check(
+    "R10-HOTFIX-AWAY-LIVE a reload after the away switch, before its solve "
+    "published, drops the home handover: the first publish carries the restored "
+    "override and the first solve plans the away band",
+    not _al_on[0] and _al_on[1] is True and _al_on[2][0] == 15.0 and _al_on[2][2] is True,
+    str(_al_on),
+)
+R.check(
+    "R10-HOTFIX-AWAY-LIVE null control: with the store inactive the handover is "
+    "republished and the solve keeps the configured band",
+    _al_off[0] and not _al_off[1] and _al_off[2][0] == _al_off[3] and _al_off[2][2] is False,
+    str(_al_off),
+)
+R.check(
+    "R10-HOTFIX-AWAY-LIVE a resolve run before the session restore lands waits "
+    "for it, and plans the stored override's away band",
+    _al_first[0][0] == 15.0 and _al_first[0][2] is True and _al_first[1] is True,
+    str(_al_first),
+)
+R.check(
+    "R10-HOTFIX-AWAY-LIVE a stored override whose return has passed still "
+    "expires at the resolve: home band, override off",
+    _al_lapsed[0][2] is False and _al_lapsed[1] is False and _al_lapsed[0][0] != 15.0,
+    str(_al_lapsed),
+)
+
+
 class _LsPlanStore:
     """A manual-plan store whose load is held on an event; its read future
     is registered on the load's first step, as ``QuarantiningStore`` does."""
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.BOOLOP.aa838ac4.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.BOOLOP.aa838ac4.json
new file mode 100644
index 000000000..4f7292845
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.BOOLOP.aa838ac4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_first_refresh_light BOOLOP aa838ac4",
+  "killed_by": "tests/features.py",
+  "old": "        if handover is not None and away_mode.published_under(self._away_state, handover):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if handover is not None or away_mode.published_under(self._away_state, handover):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.GUARD_OFF.026f6cc7.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.GUARD_OFF.026f6cc7.json
deleted file mode 100644
index 970d2673a..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.GUARD_OFF.026f6cc7.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_first_refresh_light GUARD_OFF 026f6cc7",
-  "killed_by": "tests/features.py",
-  "old": "        if handover is not None:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.GUARD_OFF.aa838ac4.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.GUARD_OFF.aa838ac4.json
new file mode 100644
index 000000000..5db7fd88d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.GUARD_OFF.aa838ac4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_first_refresh_light GUARD_OFF aa838ac4",
+  "killed_by": "tests/features.py",
+  "old": "        if handover is not None and away_mode.published_under(self._away_state, handover):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 061d4aef7..dfdc1677a 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17659,
+ "class_excess_loc": 17657,
  "const_modules_over_50": 3,
  "coordinator_attrs": 142,
  "coordinator_multiassigned_attrs": 109,
@@ -11,11 +11,11 @@
  "functions_cc_over_25": 8,
  "import_cycle_modules": 0,
  "max_cc": 44,
- "max_class_loc": 8063,
+ "max_class_loc": 8061,
  "max_method_loc": 373,
  "methods_over_150": 15,
  "methods_over_200": 8,
  "name_kept_members": 38,
- "recorded_at": "88c6ad5bbec69bfe157e04597a74d0c9c3e4775c",
+ "recorded_at": "5d4e0bcfb88413ddf9ca7f0884c36bbec9235447",
  "seam_cut_total": 422
 }

