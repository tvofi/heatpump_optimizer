# Review packet #3873
head: 73797a573acd73668d17d0fc965d33a4b287ad8b
base: e3cb5c019b464a770cc7c6fe2fbc858ed29debf7

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=137363035748 skipped
cancel-superseded id=137363652499 queued
prelude id=137363652242 queued
refresh id=137363652410 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git show 819aa2e354b4:dev/audit/rounds/round11/PLAN/prototypes.py
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified python3 $EXPORT/dev/audit/rounds/round11/PLAN/prototypes.py --only reach
             the path `$EXPORT/dev/audit/rounds/round11/PLAN/prototypes.py` is a template or an expansion, not a literal
  ok         python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         python3 tests/guard_pins.py
             `tests/guard_pins.py` is in the tree at this head

FIGURES: 5 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/boost.py/_mode_live.RETURN_DEL.c34d5103.json b/tests/mutation_ledger/killed_by/boost.py/_mode_live.RETURN_DEL.c34d5103.json
deleted file mode 100644
index 39afaf7213..0000000000
--- a/tests/mutation_ledger/killed_by/boost.py/_mode_live.RETURN_DEL.c34d5103.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/boost.py:_mode_live RETURN_DEL c34d5103",
-  "killed_by": "tests/features.py",
-  "old": "    return getattr(coord, \"mode\", None) == MODE_BOOST",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/boost.py/_restore_settle.CMP_BOUND.81c29603.json b/tests/mutation_ledger/killed_by/boost.py/_restore_settle.CMP_BOUND.81c29603.json
deleted file mode 100644
index 8758b08603..0000000000
--- a/tests/mutation_ledger/killed_by/boost.py/_restore_settle.CMP_BOUND.81c29603.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/boost.py:_restore_settle CMP_BOUND 81c29603",
-  "killed_by": "tests/features.py",
-  "old": "                              and not isinstance(hours, bool) and 0.0 <= hours < math.inf else None)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`and not isinstance(hours, bool) and 0.0 < hours < math.inf else None)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 2 sites under this anchor was killed."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._effective_cycling_cost.GUARD_OFF.9ee6aedb.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._effective_cycling_cost.GUARD_OFF.9ee6aedb.json
deleted file mode 100644
index 3c96d1053b..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._effective_cycling_cost.GUARD_OFF.9ee6aedb.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._effective_cycling_cost GUARD_OFF 9ee6aedb",
-  "killed_by": "tests/features.py",
-  "old": "        if ctx._config.wear_autotune_enabled:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 0c25836e5a847d39f7a023e9f567ac2525741ebe: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._floor_widening.BOOLOP.3e0e5f0c.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._floor_widening.BOOLOP.3e0e5f0c.json
deleted file mode 100644
index b2d6578415..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._floor_widening.BOOLOP.3e0e5f0c.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._floor_widening BOOLOP 3e0e5f0c",
-  "killed_by": "tests/entities.py",
-  "old": "        relax = self._vent_cusum.tripped and ctx._config.open_window_relax_enabled",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 0c25836e5a847d39f7a023e9f567ac2525741ebe: BOOLOP (`relax = self._vent_cusum.tripped or ctx._config.open_window_relax_enabled`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.diagnostics_state.RETURN_DEL.700af26e.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.diagnostics_state.RETURN_DEL.700af26e.json
deleted file mode 100644
index 55c198c71a..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.diagnostics_state.RETURN_DEL.700af26e.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.diagnostics_state RETURN_DEL 700af26e",
-  "killed_by": "tests/entities.py",
-  "old": "        return CoordinatorDiagnostics.of(self)",
-  "reason": "R9-EG-B6 (#1739) made this delegate the view's one reader. Re-measured on a detached worktree at be777f2f: driving tests/entities.py fails 2 of 2159 entity checks (`the learner summaries are present`; `the coordinator snapshot carries the live counter values, not None placeholders`), against the unmutated worktree's 0 failed."
-}


## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/boost.py b/custom_components/heatpump_optimizer/boost.py
index 7a54506a89..cf0b929f95 100644
--- a/custom_components/heatpump_optimizer/boost.py
+++ b/custom_components/heatpump_optimizer/boost.py
@@ -143,9 +143,11 @@ class BoostState:
     #: baseline is gone after a restart, but the slab heat is not, so every
     #: replay after the first one would fold it.
     space_settle_until: datetime | None = None
-    #: When the space overlay, and the global boost mode, went live; ``None``
-    #: unseen (a mode restored as boost), which makes ``space_boosted`` unknown.
+    #: When the space overlay went live; ``None`` unseen.
     space_since: datetime | None = None
+    #: When the global boost mode went live, ``None`` while it is not: the one
+    #: answer to "is the mode live" (ADR-005). A mode restored as boost reads
+    #: its restore, and its unseen start makes ``space_boosted`` unknown.
     mode_since: datetime | None = None
 
     #: The boosted time, over both surfaces, that ended since the learners
@@ -198,11 +200,17 @@ class BoostState:
                 and CHANNEL_SPACE not in self.until and self.mode_since is None):
             self.space_settle_until, self.space_boosted = None, timedelta(0)
 
-    def note_mode(self, live: bool, now: datetime) -> None:
-        """The global boost mode was entered (``live``) or left: leaving starts its tail."""
+    def note_mode(self, live: bool, now: datetime, *, seen: bool = True) -> None:
+        """The global boost mode was entered (``live``) or left: leaving starts its tail.
+
+        An entry not ``seen`` is a restart restoring the mode: its start, and so
+        the boosted sum, is unknown.
+        """
         if live:
             self._clear_spent(now)
             self.mode_since = now
+            if not seen:
+                self.space_boosted = None
         else:
             self.settle(now, self.mode_since)
             self.mode_since = None
@@ -357,8 +365,8 @@ def space_boost_active(coord: Any, now: datetime | None = None) -> bool:
 
 
 def _mode_live(coord: Any) -> bool:
-    """Is the global boost mode selected?"""
-    return getattr(coord, "mode", None) == MODE_BOOST
+    """Is the global boost mode selected? Read from what ``note_mode_change`` was told."""
+    return held_for(coord).mode_since is not None
 
 
 def space_learning_frozen(coord: Any, now: datetime | None = None) -> bool:
@@ -425,14 +433,14 @@ def note_mode_change(coord: Any, old: str | None, new: str, now: datetime | None
 
     The mode surface diverges the replayed plant state exactly as the
     channel overlay does -- same actuation, same mechanism -- so it owes
-    the same tail, for the time the mode ran.
+    the same tail, for the time the mode ran. ``old`` ``None`` is a restart
+    restoring ``new``, whose start nobody saw (ADR-005).
     """
     if (old == MODE_BOOST) != (new == MODE_BOOST):
-        held_for(coord).note_mode(new == MODE_BOOST, now or dt_util.now())
+        held_for(coord).note_mode(new == MODE_BOOST, now or dt_util.now(), seen=old is not None)
         if old == MODE_BOOST:
             _schedule_persist(coord)
 
-
 def overlay(
     action: CurrentAction,
     held: BoostState,
@@ -614,8 +622,10 @@ def _restore_settle(held: BoostState, raw: Mapping[str, Any], now: datetime) ->
         held.space_settle_until = until
         # Unreadable boosted time reads as a start nobody saw: unknown.
         hours = tail.get("boosted_h")
+        # A restored boost mode's unknown sum stays unknown, whichever restore ran first.
         held.space_boosted = (timedelta(hours=hours) if isinstance(hours, (int, float))
-                              and not isinstance(hours, bool) and 0.0 <= hours < math.inf else None)
+                              and not isinstance(hours, bool) and 0.0 <= hours < math.inf
+                              and held.space_boosted is not None else None)
     space = raw.get(CHANNEL_SPACE)
     since = _parse_until(space.get("since")) if isinstance(space, Mapping) else None
     if since is not None and CHANNEL_SPACE in held.until:
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index 4dbd33b29a..37b333f9eb 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -2660,6 +2660,7 @@ class CoordinatorDiagnostics:
     tibber_outage_cycles: int | None = None
     tibber_reauth_started: bool | None = None
     solve_failures: int | None = None
+    mode: str | None = None
     cop_scale: float | None = None
     cop_samples: int | None = None
     house_heat_loss_scale: float | None = None
@@ -2668,8 +2669,8 @@ class CoordinatorDiagnostics:
     LEARNERS = ("_accuracy", "_comfort_learner", "_curve_learner", "_price_model")
 
     @classmethod
-    def of(cls, coord: Any) -> "CoordinatorDiagnostics":
-        """Read ``coord``'s live counters and learner summaries into a view.
+    def of(cls, coord: Any, mode: str | None = None) -> "CoordinatorDiagnostics":
+        """Read ``coord``'s live counters and learner summaries, with the ``mode`` it hands, into a view.
 
         Lives beside the fields it fills, so a member diagnostics needs and
         a field here go stale together, not apart. A learner whose
@@ -2690,6 +2691,7 @@ class CoordinatorDiagnostics:
             tibber_outage_cycles=getattr(coord, "_tibber_outage_cycles", None),
             tibber_reauth_started=getattr(coord, "_tibber_reauth_started", None),
             solve_failures=getattr(coord, "_solve_failures", None),
+            mode=mode,
             cop_scale=getattr(coord, "_cop_scale", None),
             cop_samples=getattr(coord, "_cop_samples", None),
             house_heat_loss_scale=getattr(coord, "_house_heat_loss_scale", None),
@@ -4121,7 +4123,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
 
     def diagnostics_state(self) -> CoordinatorDiagnostics:
         """What diagnostics may read about this instance, as one view (#1739)."""
-        return CoordinatorDiagnostics.of(self)
+        return CoordinatorDiagnostics.of(self, self.mode)
 
     async def _async_setup_ecl110_state_subscription(self) -> None:
         """Subscribe to ECL110 MQTT state updates if MQTT integration is available."""
@@ -6233,8 +6235,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
     def _floor_widening(self) -> tuple[float, ...]:
         """Economy's wider band, then #26's (gated) open-window relax: while
         a window is detected open, holding the comfort floor heats the street."""
-        ctx = getattr(self, "_ctx", self)
-        relax = self._vent_cusum.tripped and ctx._config.open_window_relax_enabled
+        relax = self._vent_cusum.tripped and _ctx_of(self)._config.open_window_relax_enabled
         return tuple(by for on, by in (
             (self._mode == MODE_ECONOMY, ECONOMY_MIN_TEMP_WIDENING),
             (relax, OPEN_WINDOW_RELAX_C),
@@ -8334,7 +8335,6 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             _LOGGER.debug("Could not persist ledger: %s", err)
 
     async def _async_load_accuracy(self) -> None:
-        ctx = getattr(self, "_ctx", self)
         stored = await load_mapping(self._accuracy_store, "accuracy history")
         if stored is None:
             return
@@ -8347,9 +8347,10 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         stored_mode = stored.get("mode")
         if isinstance(stored_mode, str) and stored_mode in OPERATION_MODES:
             self._mode = stored_mode
+            boost.note_mode_change(self, None, stored_mode)  # ADR-005: boost is told a restored mode
         self._comfort_learner = ComfortLearner.from_dict(
             stored.get("comfort"),
-            ctx._config.comfort_weight,
+            _ctx_of(self)._config.comfort_weight,
         )
         self._apply_comfort_weight()
     async def _async_save_accuracy(self) -> None:
@@ -10429,9 +10430,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         the replacement fields. With the flag off this is exactly the
         configured value.
         """
-        ctx = getattr(self, "_ctx", self)
         cost = self.effective_config.compressor_cycling_cost
-        if ctx._config.wear_autotune_enabled:
+        if _ctx_of(self)._config.wear_autotune_enabled:
             cost = max(cost, self._wear_price())
         return cost
     def _book_starts(self, starts: list[datetime]) -> None:
diff --git a/custom_components/heatpump_optimizer/diagnostics.py b/custom_components/heatpump_optimizer/diagnostics.py
index c49354ec08..c3a1b8681e 100644
--- a/custom_components/heatpump_optimizer/diagnostics.py
+++ b/custom_components/heatpump_optimizer/diagnostics.py
@@ -339,7 +339,7 @@ def _coordinator_snapshot(coord: HeatPumpOptimizerCoordinator) -> dict[str, Any]
     except Exception:  # noqa: BLE001 -- diagnostics never breaks
         state = None
     snap: dict[str, Any] = {
-        "mode": getattr(coord, "mode", None),
+        "mode": state.mode if state else None,
         "tibber_outage_cycles": state.tibber_outage_cycles if state else None,
         "tibber_reauth_started": state.tibber_reauth_started if state else None,
         "weather_stale_hours": coord.weather_stale_hours()
diff --git a/dev/programme/delivery/3873.md b/dev/programme/delivery/3873.md
new file mode 100644
index 0000000000..c42cd9529c
--- /dev/null
+++ b/dev/programme/delivery/3873.md
@@ -0,0 +1 @@
+- [#3873](https://github.com/tvofi/heatpump_optimizer/pull/3873) — **open**, R11-ARCH-cycle-surface: boost and diagnostics read the mode from boost state and the diagnostics view, not the coordinator (ADR-005 parts 1 and 2) (R11-ARCH-cycle-surface)
diff --git a/tests/debug_collect.py b/tests/debug_collect.py
index fed82dca7b..95795df664 100644
--- a/tests/debug_collect.py
+++ b/tests/debug_collect.py
@@ -836,6 +836,7 @@ from homeassistant.helpers import entity_registry as er  # noqa: E402
 from heatpump_optimizer import const as const_mod  # noqa: E402
 from heatpump_optimizer import replay_doc  # noqa: E402
 from heatpump_optimizer.const import PRICE_SOURCE_ENTITY  # noqa: E402
+from heatpump_optimizer.coordinator import CoordinatorDiagnostics  # noqa: E402
 
 _export_spec = importlib.util.spec_from_file_location(
     "hpo_export_under_test", Path("tools/replay/export.py"))
@@ -1538,7 +1539,8 @@ async def _planted_download(value_pass=True):
     (Path(folder) / ".storage" / debugger.store_keys("rp")["accuracy"]).write_text(
         json.dumps({"version": 1, "data": {"note": _leak_text("store"),
                                            "lat": float(EXACT[0])}}))
-    coord.mode = _leak_text("mode")
+    # Diagnostics reads the mode from the published view (ADR-005), so the plant goes there.
+    coord.diagnostics_state = lambda: CoordinatorDiagnostics(mode=_leak_text("mode"))
     coord.data = {"insight": {"last_diagnosis": _leak_text("diagnosis")},
                   "problem_messages": [_leak_text("input")],
                   "current_action": _leak_text("plan"),
diff --git a/tests/features.py b/tests/features.py
index fa4336c904..ac893443a3 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -85603,6 +85603,40 @@ R.check(
     f"{_bt_cc_in} {_bt_cc_held}",
 )
 
+# ADR-005: boost answers "is the global boost mode live" from what it was told,
+# so a restart that restores the boost mode tells it. Restarted in boost: live,
+# and leaving owes the unseen start's full tail. Null control: a restart in auto.
+_bt_rs_seen = {}
+for _bt_rs_mode in (boost_mod.MODE_BOOST, _fb_const.MODE_AUTO):
+    _bt_rs_entry = FakeEntry(data=dict(_T1_DATA), entry_id=f"bt_rs_{_bt_rs_mode}")
+    _bt_asyncio.run(Coord(FakeHass(), _bt_rs_entry).async_set_mode(_bt_rs_mode, refresh=False))
+    _bt_rs = Coord(FakeHass(), _bt_rs_entry)
+    _bt_asyncio.run(_bt_rs._async_load_accuracy())
+    _bt_rs_live = boost_mod.space_boost_active(_bt_rs, NOW)
+    _bt_asyncio.run(_bt_rs.async_set_mode(_fb_const.MODE_AUTO, refresh=False))
+    _bt_rs_held = boost_mod.held_for(_bt_rs)
+    _bt_rs_seen[_bt_rs_mode] = (_bt_rs_live, _bt_rs_held.space_boosted, _bt_rs_held.space_settle_until is None)
+R.check(
+    "a restart restoring the boost mode reads it live, and leaving it owes the unseen start's tail",
+    _bt_rs_seen == {boost_mod.MODE_BOOST: (True, None, False), _fb_const.MODE_AUTO: (False, timedelta(0), True)},
+    f"{_bt_rs_seen}",
+)
+# The unseen sum stays unknown whichever restore runs first: a persisted tail
+# restored after the mode does not replace it. Null control: no mode restored.
+_bt_ro = {}
+for _bt_ro_mode in (boost_mod.MODE_BOOST, _fb_const.MODE_AUTO):
+    _bt_ro_coord = _BtCoord()
+    boost_mod.note_mode_change(_bt_ro_coord, None, _bt_ro_mode, NOW)
+    _bt_ro_held = boost_mod.held_for(_bt_ro_coord)
+    boost_mod._restore_settle(_bt_ro_held, {"space_settle": {
+        "until": (NOW + timedelta(hours=1)).isoformat(), "boosted_h": 0.5}}, NOW)
+    _bt_ro[_bt_ro_mode] = (_bt_ro_held.mode_since, _bt_ro_held.space_boosted)
+R.check(
+    "a persisted tail restored after the boost mode keeps its boosted sum unknown",
+    _bt_ro == {boost_mod.MODE_BOOST: (NOW, None), _fb_const.MODE_AUTO: (None, timedelta(hours=0.5))},
+    f"{_bt_ro}",
+)
+
 
 # A hot-water charge inside a counter span (the dwell saw it): the cycle has no
 # space interval, yet the span stays clean where the counter is declared to see
@@ -92713,9 +92747,11 @@ R.check(
     f"{_p3_none} {_p3_live} {_p3_cancel} {_p3_press}",
 )
 class _P3Coord:
-    mode = "auto"
+    pass
 _p3_c = _P3Coord()
-_p3_mode = type("C", (), {"mode": boost_mod.MODE_BOOST})()
+_p3_mode = _P3Coord()
+# Boost reads the mode it was told (ADR-005), not an attribute of the coordinator.
+boost_mod.note_mode_change(_p3_mode, "auto", boost_mod.MODE_BOOST, NOW)
 # Both hold a running tail, so only the global mode can make the end unknown.
 boost_mod.held_for(_p3_c).space_settle_until = NOW + _p3_td(hours=5)
 boost_mod.held_for(_p3_mode).space_settle_until = NOW + _p3_td(hours=5)
diff --git a/tests/mutation_ledger/killed_by/boost.py/_mode_live.RETURN_DEL.c34d5103.json b/tests/mutation_ledger/killed_by/boost.py/_mode_live.RETURN_DEL.c34d5103.json
deleted file mode 100644
index 39afaf7213..0000000000
--- a/tests/mutation_ledger/killed_by/boost.py/_mode_live.RETURN_DEL.c34d5103.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/boost.py:_mode_live RETURN_DEL c34d5103",
-  "killed_by": "tests/features.py",
-  "old": "    return getattr(coord, \"mode\", None) == MODE_BOOST",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/boost.py/_restore_settle.CMP_BOUND.81c29603.json b/tests/mutation_ledger/killed_by/boost.py/_restore_settle.CMP_BOUND.81c29603.json
deleted file mode 100644
index 8758b08603..0000000000
--- a/tests/mutation_ledger/killed_by/boost.py/_restore_settle.CMP_BOUND.81c29603.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/boost.py:_restore_settle CMP_BOUND 81c29603",
-  "killed_by": "tests/features.py",
-  "old": "                              and not isinstance(hours, bool) and 0.0 <= hours < math.inf else None)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`and not isinstance(hours, bool) and 0.0 < hours < math.inf else None)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 2 sites under this anchor was killed."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._effective_cycling_cost.GUARD_OFF.9ee6aedb.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._effective_cycling_cost.GUARD_OFF.9ee6aedb.json
deleted file mode 100644
index 3c96d1053b..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._effective_cycling_cost.GUARD_OFF.9ee6aedb.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._effective_cycling_cost GUARD_OFF 9ee6aedb",
-  "killed_by": "tests/features.py",
-  "old": "        if ctx._config.wear_autotune_enabled:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 0c25836e5a847d39f7a023e9f567ac2525741ebe: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._floor_widening.BOOLOP.3e0e5f0c.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._floor_widening.BOOLOP.3e0e5f0c.json
deleted file mode 100644
index b2d6578415..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._floor_widening.BOOLOP.3e0e5f0c.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._floor_widening BOOLOP 3e0e5f0c",
-  "killed_by": "tests/entities.py",
-  "old": "        relax = self._vent_cusum.tripped and ctx._config.open_window_relax_enabled",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 0c25836e5a847d39f7a023e9f567ac2525741ebe: BOOLOP (`relax = self._vent_cusum.tripped or ctx._config.open_window_relax_enabled`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.diagnostics_state.RETURN_DEL.700af26e.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.diagnostics_state.RETURN_DEL.700af26e.json
deleted file mode 100644
index 55c198c71a..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.diagnostics_state.RETURN_DEL.700af26e.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.diagnostics_state RETURN_DEL 700af26e",
-  "killed_by": "tests/entities.py",
-  "old": "        return CoordinatorDiagnostics.of(self)",
-  "reason": "R9-EG-B6 (#1739) made this delegate the view's one reader. Re-measured on a detached worktree at be777f2f: driving tests/entities.py fails 2 of 2159 entity checks (`the learner summaries are present`; `the coordinator snapshot carries the live counter values, not None placeholders`), against the unmutated worktree's 0 failed."
-}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 87b424eaa0..c0a561d8c0 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17317,
+ "class_excess_loc": 17315,
  "const_modules_over_50": 4,
  "coordinator_attrs": 136,
  "coordinator_multiassigned_attrs": 104,
@@ -12,13 +12,13 @@
  "import_cycle_modules": 0,
  "in_function_copies": 11,
  "max_cc": 44,
- "max_class_loc": 7868,
+ "max_class_loc": 7866,
  "max_method_loc": 373,
  "methods_over_150": 14,
  "methods_over_200": 7,
  "module_excess_loc": 21779,
  "name_kept_members": 38,
- "recorded_at": "4ebd430fbff9a7b19582ca530a817f34abbafa16",
+ "recorded_at": "1207ee13b0e439a4acefccabace691785af2ebad",
  "seam_cut_total": 413,
  "unloaded_package_imports": 14
 }

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
