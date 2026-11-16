# Review packet #3654
head: da36537f137ad9bb8a1cbc8c2fdc60bd7c81df8e
base: d4968fe08ba0b18f9d96f6ca308edf45f35ca469

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=133120878335 success
arch-score / arch-score id=133121651790 in_progress
arm id=133119437507 skipped
budget-raise-gate / budget-raise-gate id=133121651805 queued
cancel-superseded id=133119394235 in_progress
codeql id=133121654598 skipped
codeql / Analyze (actions) id=133120085561 success
codeql / Analyze (javascript-typescript) id=133120085465 success
codeql / Analyze (python) id=133120085512 success
governance id=133121654056 skipped
governance / env-matrix id=133120085623 in_progress
governance / instrument-self-tests id=133120085634 in_progress
governance / policy-docs id=133120085638 in_progress
governance / record id=133120086736 skipped
governance / wave-script id=133120085607 queued
hassfest id=133121653333 skipped
hassfest / hassfest id=133120085520 success
kernel-points id=133121654529 skipped
prelude id=133119393868 success
refresh id=133119394093 in_progress
tests id=133121653589 skipped
tests / briefs id=133120085649 in_progress
tests / closure-scope id=133120085808 queued
tests / mutation id=133120085527 success
tests / mutation-autofix id=133121275834 skipped
tests / mutation-pins id=133121274935 skipped
tests / nightly-status id=133120085588 failure
validate id=133121653590 skipped
validate / validate-hacs id=133120085483 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 133120085634: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
none

## carry_audit at the head
NOTE body item 806e1101: R11-PRE-TOOLCHAIN-PIN
NOTE body item 9833c393: R11-PRE-TOOLCHAIN-PIN
NOTE body item a00789b0: R11-PRE-TOOLCHAIN-PIN
NOTE body item f7b54cbd: R11-PRE-TOOLCHAIN-PIN
NOTE body item 766671f4: R11-PRE-TOOLCHAIN-PIN
NOTE body item 1eaf8e55: R11-PRE-TOOLCHAIN-PIN
NOTE body item 6fd3d308: R11-PRE-TOOLCHAIN-PIN
NOTE body item 3e0749c4: R11-PRE-TOOLCHAIN-PIN
NOTE body item 0feb43b0: R11-PRE-PARALLEL-PIPELINE: R11-PRE-PARALLEL-PIPELINE resolved on origin/handoff/audit-r10-roster
NOTE body item a62b1fec: R11-PRE-TOOLCHAIN-PIN
NOTE body item 695d23a5: R11-PRE-TOOLCHAIN-PIN
CARRY-AUDIT: 11 finding item(s): 11 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: FULL -- every test script runs, nothing is scoped out.
             no segment of this names a program this check knows
  ok         python3 -I tools/audit/seat/toolchain.py --self-test
             `tools/audit/seat/toolchain.py` is in the tree at this head
  ok         python3 -I tools/ci/gate.py --self-test
             `tools/ci/gate.py` is in the tree at this head
  ok         python3 tools/audit/seat/prune_refs.py --self-test
             `tools/audit/seat/prune_refs.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/beat_jobs.py --self-test
             `tools/audit/seat/beat_jobs.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r11_toolchain_mutants.py
             `dev/audit/harnesses/r11_toolchain_mutants.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs --budgets
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         python3 -I tools/ci/selftest_scope.py record --step toolchain --step ref-pruner
             `tools/ci/selftest_scope.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff 921214bf42 --workdir <dir>
             `tests/closure.py` is in the tree at this head
  ok         tools/ci/gate.py changes the gate itself
             `tools/ci/gate.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only
             `tests/env_drift.py` is in the tree at this head
  unverified git grep -n -E '\.\.origin/main|detach[^|]*origin/main|-B [^ ]+ origin/main|origin/main:\$?\{?(rel|tools)' -- tools/audit/seat tools/pr .claude/hooks ':!*selftest*' ':!*/instruments/*' ':!*/fixtures/*'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -ln "pr_args.sh" -- tools/audit/seat ':!*selftest*' ':!*.md'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -l "pr_tools_fresh" -- tools/audit/seat
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n -E 'fork_head\(|outside_is_mains' -- tools/audit/seat
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 16 resolved, 5 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: delta (later round over the reviewed head 7a2b2cdef2283bf3c2f07d70d9a380f9fce0b04e)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at 7a2b2cdef2283bf3c2f07d70d9a380f9fce0b04e
Fix review: blocked 7a2b2cdef2283bf3c2f07d70d9a380f9fce0b04e merge-conflict: head conflicts with origin/main in .github/workflows/governance.yml, tools/audit/seat/INSTRUMENTS.md, tools/audit/seat/beat_jobs.py, tools/audit/seat/instruments/beat_jobs.py.md

bus-nonce: 6e46a569100d5d70114fb4de057e6319

## Block
`git merge-tree --write-tree origin/main 7a2b2cdef2283bf3c2f07d70d9a380f9fce0b04e` (origin/main d4968fe08ba0b18f9d96f6ca308edf45f35ca469) exits 1 with content conflicts in four paths, none of them claim files: .github/workflows/governance.yml, tools/audit/seat/INSTRUMENTS.md, tools/audit/seat/beat_jobs.py, tools/audit/seat/instruments/beat_jobs.py.md. Main has moved 32 commits past the merge base 56ce2f695bcba5218444f52c04a5ed923a07d563; 6c87325160 (round_metrics self-test step + instrument entry) and b0051ab6df (beat scorecard row) touch the conflicting paths. No MERGE-CLAIM line was printed; the only ledger merge (tests/closures.json) resolved. By fix-review.md step 13 a conflict off the claim files is the author's: merge main, resolve, and re-dispatch review at the new head. The review of the diff itself was not carried further, since any resolution changes the head and voids a verdict here.

## Evidence
- ev/HEAD.txt: the head reviewed.
- ev/merge-tree.txt: the merge-tree output and exit code.
- ev/main-commits-on-conflicting-paths.txt: main commits since the merge base on the conflicting paths.
- ev/review-packet.md: review_packet.py render, REFUSE structure (head does not merge cleanly with origin/main); gate digest pending at render.
- CI was not waited on: the block is independent of CI state at this head.

## Delta diff: git diff 7a2b2cdef2283bf3c2f07d70d9a380f9fce0b04e da36537f137ad9bb8a1cbc8c2fdc60bd7c81df8e
diff --git a/.github/CODEOWNERS b/.github/CODEOWNERS
index ffd09f3fab..3927adb946 100644
--- a/.github/CODEOWNERS
+++ b/.github/CODEOWNERS
@@ -69,6 +69,10 @@
 # instruments R11-PRE-ROUND-METRICS builds.
 /tools/audit/seat/plant_recall.py         @tvofi
 /tools/audit/seat/finder_overlap.py       @tvofi
+# and its flow reads: lead_time, product_green (scorecard.py's A_gate and the
+# round lines), restore, runner seconds and tokens.
+/tools/audit/seat/round_metrics.py        @tvofi
+/tools/audit/seat/scorecard.py            @tvofi
 /dev/audit/harnesses/README.md            @tvofi
 /.github/CODEOWNERS                       @tvofi
 # The ratchet caps (`*_budgets.json`) carry no owner (decision 0013 as amended
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index 6c1012552b..a46806f70f 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -497,9 +497,9 @@ jobs:
         if: steps.scope.outputs.bottleneck-alert == 'true'
         run: python3 -I tools/audit/seat/bottleneck_check.py --self-test
 
-      # The convergence scorecard's ten report-only lines: each rule held to its
+      # The convergence scorecard's report-only lines: each rule held to its
       # null control over planted inputs, offline, and one mutant per predicate.
-      - name: Show the scorecard holding each of its ten lines to its null control
+      - name: Show the scorecard holding each of its lines to its null control
         id: scorecard
         if: steps.scope.outputs.scorecard == 'true'
         run: python3 -I tools/audit/seat/scorecard.py --self-test
@@ -513,6 +513,15 @@ jobs:
         if: steps.scope.outputs.toolchain == 'true'
         run: python3 -I tools/audit/seat/toolchain.py --self-test
 
+      # Decision 0018's flow reads per round and week (R11-PRE-ROUND-METRICS):
+      # lead_time from the roster-entry commit, product_green with the gate's
+      # check count, restore, runner seconds and tokens; an empty input reads
+      # unread, never a value, and one mutant per predicate is killed, offline.
+      - name: Show the round metrics reading unread on an empty input and each read on a planted one
+        id: round-metrics
+        if: steps.scope.outputs.round-metrics == 'true'
+        run: python3 -I tools/audit/seat/round_metrics.py --self-test
+
       # Decision 0018 section 5's two held-out checks (R11-PRE-ROUND-METRICS):
       # planted-defect recall's refusals and its count after the judge, and the
       # two-finder overlap estimate; each holds an empty input to unread, never
diff --git a/README.md b/README.md
index 50e59b8b14..30dab25208 100644
--- a/README.md
+++ b/README.md
@@ -563,7 +563,7 @@ every sensor is created on every install regardless of which group it is in.
 |---|---|---|---|
 | Optimization Mode | — | Current mode: auto, comfort, economy, boost or off | |
 | Heat Pump Action | — | What the plan is doing now: `off` (neither circuit runs), `hot_water` (only the tank heats), `eco`, `normal`, `pre_heat` or `boost`, `comfort` while comfort mode holds, `idle` before there is a plan to run or once it is empty, and `system_identification` while the step-response experiment drives the pump | |
-| Optimal Setpoint | °C | The setpoint the current plan step asks for | |
+| Optimal Setpoint | °C | The current plan step's heating power, written as a temperature: the coldest acceptable temperature at no heat, the warmest acceptable at full power, linear between. It is not the room temperature the plan aims for; the comfort settings are | Read Recommended Power for the power itself |
 | Recommended Power | kW | The electrical power the current plan step asks for | |
 | Cost Electricity Price (now) | CUR/kWh | The price the plan is being made against right now | |
 | Plan Narrative | — | The plan told in sentences, grouped by reason | Card headline |
@@ -1073,6 +1073,7 @@ Each clears itself once the cause is gone.
 - **A configured grid fee is negative** — almost always a sign slip. Correct it on **Transfer fees and contract**.
 - **The downstairs temperature is modelled, not measured** — two-zone planning without a lower-floor thermometer. Assign the *Lower floor temperature sensor* to remove it.
 - **Your comfort temperatures contradict each other** — the stored band cannot all be met at once, for example a target above the warmest acceptable temperature. Fix the band on **Comfort and temperatures**.
+- **The floor return sensor reads far warmer than any floor loop** — the floor return field reads more than 12 K above the room, almost always the heat pump's own return or a buffer-tank sensor. The reading is ignored and the slab is estimated as with no sensor; pick a sensor in the floor loop itself, after any buffer tank or mixing valve, or leave the field empty.
 - **Valve target above comfort** — the mixing-valve target is read as the room temperature the circuit holds, not a water temperature, and it is above the top of your comfort band. Nothing is changed (it can be deliberate, for example slab charging); if it is a flow temperature, set the room temperature or 0 on **Mixing valve**.
 - **The heat pump's hot water set-point is below the configured temperature** — the pump's own set-point stops it reaching the disinfection or minimum temperature. The notice's fix writes the needed value to the pump's entity.
 - **The space-heating set-point entity is not reporting** — the set-point entity is missing or unreadable. Check it, or clear the slot.
diff --git a/RELEASE_NOTES.md b/RELEASE_NOTES.md
index dad5c05f4e..189cd207a5 100644
--- a/RELEASE_NOTES.md
+++ b/RELEASE_NOTES.md
@@ -1,3 +1,23 @@
+## v10.0.2
+
+**Patch stamp: 12 merges since v10.0.1 (`git log --first-parent --merges --format=%h v10.0.1..HEAD | wc -l`): the card's "Apply this plan" now works when the published plan runs past the manual-plan window, and a floor-return reading far above the room no longer seeds the slab estimate; the rest is tooling and records.**
+
+### Action needed
+
+None: no step is asked of you. No option is added, no default changed, no entity renamed, and no store needs a migration. If a "floor return implausible" repair appears after the upgrade, it names the sensor to check (#3640, below).
+
+### #3649 "Apply this plan" applies the plan only up to the manual-plan window (R11-OUTSIDE-APPLY-PLAN-CEILING, issue #3636)
+
+"Apply this plan" failed whenever the published plan had a run starting 20 hours or more from now, because the card sent runs that start past the manual-plan window and the service refuses any such slot. The card now drops every run starting at or after now plus the published manual-plan window, less one plan step for clock skew between the browser and the server. A run that straddles the window is still sent whole, and a zoomed-in view does not change what is applied. Reported, with the suggested fix, by rasenschachmatt in issue #3636; thanks.
+
+### #3640 A floor-return reading far above the room no longer seeds the slab estimate (R11-OUTSIDE-SLAB-SEED-GUARD, issue #3616)
+
+A heat-pump return reading wired to the floor-return field, far above any floor loop, was believed as stored heat and the plan held none. A reading more than 12 K above the room, or one taken during a hot-water run or a defrost, is now refused and the slab follows the model's own estimate, as on an install with no floor-return sensor. A new repair, `floor_return_implausible`, names the sensor, its reading, the room and the bound, and clears on the next plausible cycle. The floor-return option text (en, de, sv) and the README say which sensor belongs there. Issue #3616's multi-zone request stays open.
+
+### Development process
+
+Developer tooling, CI, audit machinery and records only, no change to the integration: #3652 (self-test scope re-record, part 4), #3629 (self-test red on main), #3622 (plan render), #3642 (brief texts), #3638 (RCA latch clauses), #3646 (new audit dimensions), #3626 (rulings file), #3566 (nudge retirement), #3650 (delivery rows, autofix), #3634 (delivery rows, autofix).
+
 ## v10.0.1
 
 **Patch stamp: 20 merges since v10.0.0 (`git log --first-parent --merges --format=%h v10.0.0..HEAD | wc -l`): compressor starts are counted from the running signal's own on and off edges, so a short cycle between two refreshes is no longer missed, and the COP learner's power floor follows what the pump is metered drawing; the rest is tooling and records.**
diff --git a/VERSION b/VERSION
index 1532420512..7e2df97fe5 100644
--- a/VERSION
+++ b/VERSION
@@ -1 +1 @@
-10.0.1
+10.0.2
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index 6b0fddc4b0..f16081f02e 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -261,6 +261,7 @@ from .defrost import DefrostDerate, DefrostWindow, in_frost_band
 from . import duty_switch, early_cutoff, pump_arbiter, pump_signals, supply_hold
 from . import issues, setpoint_check
 from . import quiet_windows
+from . import slab_seed
 from . import price_tiles
 from . import whatif
 from .pump_mode import ModeCapability
@@ -6664,8 +6665,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         floor_return = reader.read(CONF_FLOOR_RETURN_TEMP_ENTITY)
         if floor_return.ok:
             self._floor_return_temp = floor_return.value
-            # The slab estimate advances from the reading and records it.
-            self._thermal_model.update_slab_from_return_temp(state, self._floor_return_temp)
+            slab_seed.seed(self._thermal_model, state, floor_return.value, self._pump_signals)
 
         # The lower zone's room temperature: only a real thermometer carries
         # information about it. The floor return is a WATER temperature,
@@ -6828,8 +6828,10 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         if buffer_reading.ok and (buffer_value := buffer_reading.value) is not None:
             await self._async_learn_buffer_cooling(buffer_value)
 
+        slab_sensed = slab_seed.judge(self._config_notices, self.hass, floor_return,
+                                      _ctx_of(self)._current_state.room_temperature, self._pump_signals)
         # The fabric model refined by how the interval went: last, on the full state.
-        seed = await self._async_learn_interval(prior, slab_unsensed=not floor_return.ok)
+        seed = await self._async_learn_interval(prior, slab_unsensed=not slab_sensed)
 
         state = replace(_ctx_of(self)._current_state)
         # Update ECL110 effective displace state (PID/PI lag approximation)
@@ -6841,10 +6843,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
 
         # Last resort: seed the slab, and the lower zone if nothing better
         # has been read, from the room temperature. Both guards are on the
-        # READING, not the entity being set: a stale sensor takes the same
-        # path as an absent one. The room+1 K seed runs only until the slab
-        # can be advanced (``_propagated_slab``); it used to freeze forever.
-        if not floor_return.ok:
+        # READING: a stale or refused one (slab_seed) takes the absent path.
+        # The room+1 K seed runs only until ``_propagated_slab`` advances it.
+        if not slab_sensed:
             if seed is not None:
                 state.slab_temperature = seed
                 self._slab_temp_initialized = True
diff --git a/custom_components/heatpump_optimizer/manifest.json b/custom_components/heatpump_optimizer/manifest.json
index e7c3535cd4..89038cdcf2 100644
--- a/custom_components/heatpump_optimizer/manifest.json
+++ b/custom_components/heatpump_optimizer/manifest.json
@@ -25,5 +25,5 @@
     "scipy>=1.10.0",
     "threadpoolctl>=3.5.0"
   ],
-  "version": "10.0.1"
+  "version": "10.0.2"
 }
diff --git a/custom_components/heatpump_optimizer/slab_seed.py b/custom_components/heatpump_optimizer/slab_seed.py
new file mode 100644
index 0000000000..8e20a7a368
--- /dev/null
+++ b/custom_components/heatpump_optimizer/slab_seed.py
@@ -0,0 +1,92 @@
+"""Whether a floor-return reading may seed the slab estimate (#3616).
+
+The floor-return field seeds the slab every cycle
+(``ThermalModel.update_slab_from_return_temp``), and a seed far above the
+room tells the planner that heat is already stored, so it plans none. That is
+what a heat-pump return on a buffer plant does when it is configured in that
+field: the plan held 0 kWh of space heating with the rooms below target.
+
+A refused reading is not replaced by a guess: the slab keeps the model's own
+estimate, which the coordinator advances exactly as it does with no sensor.
+Pure: no Home Assistant import; the coordinator passes the readings in.
+"""
+from __future__ import annotations
+
+from typing import Any, Final
+
+from .freq_control import defrost_interval
+
+#: The warmest a floor-loop return may read above the room air it heats, K.
+#: Floor-loop water runs 3-9 K above that air (the repository's working band,
+#: see the ``lower_floor_modelled`` repair text), and EN 1264's surface limits,
+#: 29 C in an occupied zone and 33 C in a bathroom over 20 and 24 C design
+#: rooms, both put the floor 9 K above its room. The 3 K over that is margin
+#: for a sensor on the manifold and a peripheral zone. A buffer or heat-pump
+#: return, which runs at the heating curve's flow temperature, clears it.
+SLAB_SEED_MAX_ABOVE_ROOM_K: Final = 12.0
+
+#: The issue raised while a reading is refused for its level, naming the sensor.
+ISSUE_FLOOR_RETURN_IMPLAUSIBLE: Final = "floor_return_implausible"
+
+REFUSED_ABOVE_ROOM: Final = "above_room"
+REFUSED_HOT_WATER: Final = "hot_water_run"
+REFUSED_DEFROST: Final = "defrost"
+
+
+def above_room(return_c: float, room_c: float) -> bool:
+    """Whether ``return_c`` is too far above ``room_c`` to be a floor loop."""
+    return return_c - room_c > SLAB_SEED_MAX_ABOVE_ROOM_K
+
+
+def hot_water_run(signals: Any) -> bool:
+    """Whether the pump's observed mode is hot water alone.
+
+    A return probe then reads tank water. Only an observed mode counts: the
+    unknown-mode fallback can do everything and so says nothing either way.
+    """
+    mode = signals.mode
+    return bool(signals.mode_observed and mode.dhw and not mode.space_heat)
+
+
+def refusal(return_c: float, room_c: float, signals: Any) -> str | None:
+    """Why ``return_c`` may not seed the slab now, or ``None`` when it may."""
+    if above_room(return_c, room_c):
+        return REFUSED_ABOVE_ROOM
+    if hot_water_run(signals):
+        return REFUSED_HOT_WATER
+    if defrost_interval(signals.defrosting):
+        return REFUSED_DEFROST
+    return None
+
+
+def seed(model: Any, state: Any, return_c: float | None, signals: Any) -> None:
+    """Advance ``state``'s slab from ``return_c`` unless the reading is refused.
+
+    Called before this cycle's pump signals are read, so ``signals`` are last
+    cycle's; :func:`judge` re-decides on this cycle's before the state publishes.
+    """
+    if return_c is not None and refusal(return_c, state.room_temperature, signals) is None:
+        model.update_slab_from_return_temp(state, return_c)
+
+
+def judge(notices: Any, hass: Any, reading: Any, room_c: float, signals: Any) -> bool:
+    """Whether this cycle's floor-return ``reading`` seeds the slab.
+
+    A refused reading leaves the slab to the model, as no sensor does. The
+    repair naming the sensor is raised while its level is refused and cleared
+    otherwise: judged on the level alone, since a hot-water run or a defrost
+    refuses a reading for that cycle only, which is the plant working, not a
+    wrong sensor.
+    """
+    value = reading.value if reading.ok else None
+    high = value is not None and above_room(value, room_c)
+    notices.report(
+        hass, ISSUE_FLOOR_RETURN_IMPLAUSIBLE, reading.entity_id if high else None,
+        {
+            "entity": str(reading.entity_id),
+            "reading": f"{value:.1f}",
+            "room": f"{room_c:.1f}",
+            "bound": f"{SLAB_SEED_MAX_ABOVE_ROOM_K:g}",
+        } if high else None,
+    )
+    return value is not None and refusal(value, room_c, signals) is None
diff --git a/custom_components/heatpump_optimizer/strings.json b/custom_components/heatpump_optimizer/strings.json
index c9179a9f5e..a0f688cfbe 100644
--- a/custom_components/heatpump_optimizer/strings.json
+++ b/custom_components/heatpump_optimizer/strings.json
@@ -223,7 +223,7 @@
           "solar_radiation_entity": "Optional. Sunshine in W/m² measured at your house. It tells the optimizer how much solar heat the house is getting right now, which it uses for the current state and for learning. Expected sun later in the day comes from the Solar irradiance source, not from this sensor.",
           "solar_forecast_source": "Where to get solar irradiance from. \"Weather entity\" uses your weather integration, which often does not publish irradiance at all. \"Open-Meteo\" fetches a free forecast for the location below; no account is needed.",
           "solar_location": "Coordinate used for the Open-Meteo irradiance forecast. Defaults to your Home Assistant home location. Only used when the source is Open-Meteo.",
-          "floor_return_temp_entity": "Optional. Water temperature coming back from the floor loops, used to gauge how much heat the slab is holding.",
+          "floor_return_temp_entity": "Optional. A sensor in the floor loop itself: the water coming back from the floor loops, after any buffer tank or mixing valve. It gauges how much heat the slab is holding. Do not use the heat pump's own return sensor: on a plant with a buffer tank it reads the heat pump's circuit, far warmer than the floor, and the plan would believe the slab is already full and plan no heating. A reading more than 12 K above the room is ignored and raises a repair notice. Leave empty if there is no sensor in the floor loop.",
           "lower_floor_temp_entity": "Optional, two-zone only. A real thermometer in the lower zone. Without one the lower floor is planned and plotted at whatever the main room sensor reads, so a downstairs that runs warmer or cooler than upstairs is invisible.",
           "dhw_temp_entity": "Optional but recommended. The real tank temperature. Also lets a manual hot water boost reset the anti-legionella timer.",
           "buffer_tank_temp_entity": "Optional. When set, the integration learns how fast the buffer tank loses heat instead of relying on the configured estimate.",
@@ -273,7 +273,7 @@
             "data_description": {
               "buffer_tank_temp_entity": "Optional. When set, the integration learns how fast the buffer tank loses heat instead of relying on the configured estimate.",
               "dhw_temp_entity": "Optional but recommended. The real tank temperature. Also lets a manual hot water boost reset the anti-legionella timer.",
-              "floor_return_temp_entity": "Optional. Water temperature coming back from the floor loops, used to gauge how much heat the slab is holding.",
+              "floor_return_temp_entity": "Optional. A sensor in the floor loop itself: the water coming back from the floor loops, after any buffer tank or mixing valve. It gauges how much heat the slab is holding. Do not use the heat pump's own return sensor: on a plant with a buffer tank it reads the heat pump's circuit, far warmer than the floor, and the plan would believe the slab is already full and plan no heating. A reading more than 12 K above the room is ignored and raises a repair notice. Leave empty if there is no sensor in the floor loop.",
               "heat_pump_defrost_entity": "Optional. On while the pump reverses to melt frost off the outdoor coil. The electricity bought during a defrost goes into the coil rather than into the house. Note that many pumps are only polled every few minutes, so short defrosts are missed entirely: this is a sample of defrost activity, not a stopwatch.",
               "heat_pump_fault_entity": "Optional. On while the pump is reporting a fault. Only whether there is a fault is used, never the code itself.",
               "heat_pump_mode_entity": "Optional. The pump's own mode selector - cooling, heating, hot water, or a combination of two. Read only, unless Pump duty control is set to Control. A pump in a cooling or hot-water-only mode cannot heat the house, and one in a heating-only mode cannot make hot water, so without this the plan can promise heat the pump is not currently able to deliver. Left empty, the optimizer assumes the pump can do everything.",
@@ -613,7 +613,7 @@
             "data_description": {
               "buffer_tank_temp_entity": "Optional. When set, the integration learns how fast the buffer tank loses heat instead of relying on the configured estimate.",
               "dhw_temp_entity": "Optional but recommended. The real tank temperature. Also lets a manual hot water boost reset the anti-legionella timer.",
-              "floor_return_temp_entity": "Optional. Water temperature coming back from the floor loops, used to gauge how much heat the slab is holding.",
+              "floor_return_temp_entity": "Optional. A sensor in the floor loop itself: the water coming back from the floor loops, after any buffer tank or mixing valve. It gauges how much heat the slab is holding. Do not use the heat pump's own return sensor: on a plant with a buffer tank it reads the heat pump's circuit, far warmer than the floor, and the plan would believe the slab is already full and plan no heating. A reading more than 12 K above the room is ignored and raises a repair notice. Leave empty if there is no sensor in the floor loop.",
               "heat_pump_switch_entity": "Optional. A switch used to turn the heat pump off during expensive hours.",
               "lower_floor_temp_entity": "Optional, two-zone only. A real thermometer in the lower zone. Without one the lower floor is planned and plotted at whatever the main room sensor reads, so a downstairs that runs warmer or cooler than upstairs is invisible."
             }
@@ -1866,6 +1866,10 @@
       "title": "A configured grid fee is negative",
       "description": "The grid fee layer contains a rate of {rate} {currency}/kWh (from the {source} input). A transfer fee is a charge, so a negative one is almost always a sign slip — and the plan is pricing every hour it applies to as subsidised, favouring exactly the hours the grid company charges for. Nothing is changed or capped: the plan keeps pricing with exactly the value configured. Correct the value on the \"Transfer fees and contract\" options page (or fix the fee sensor) and this notice clears on the next planning cycle."
     },
+    "floor_return_implausible": {
+      "title": "The floor return sensor reads far warmer than any floor loop",
+      "description": "{entity} reads {reading} °C with the room at {room} °C, more than {bound} K above it. Water returning from a floor loop runs a few kelvin above the room it heats, so this is almost always the heat pump's own return or a buffer-tank sensor configured in the floor return field. The integration estimates how much heat the floor slab holds from that field: a reading this warm made the plan believe the slab was already full, and plan little or no heating while the rooms were below target. Until this clears, the reading is ignored and the slab is estimated by the model, as it is with no sensor. Under the sensor options, pick a sensor in the floor loop itself, after any buffer tank or mixing valve, or leave the field empty; this notice clears on the next cycle once the reading is plausible."
+    },
     "lower_floor_modelled": {
       "title": "The downstairs temperature is modelled, not measured",
       "description": "Two-zone planning is on and no lower-floor thermometer is configured, so the lower zone starts from the main room sensor and is carried forward by the thermal model — the “Lower floor (modelled)” trace on the plan chart. That is how the zone has to be planned without a sensor, and it is not something the floor-return sensor can supply: return water runs 3–9 K above the room it heats, so it drives the slab estimate, which is what it is genuinely a proxy for. What a modelled zone cannot do is correct itself, so over a long cold spell it can drift from the real downstairs. Assigning “Lower floor temperature sensor” under the zone options closes that loop; this notice clears when you do."
diff --git a/custom_components/heatpump_optimizer/translations/de.json b/custom_components/heatpump_optimizer/translations/de.json
index b316299006..691dd9d300 100644
--- a/custom_components/heatpump_optimizer/translations/de.json
+++ b/custom_components/heatpump_optimizer/translations/de.json
@@ -223,7 +223,7 @@
           "solar_radiation_entity": "Optional. Sonneneinstrahlung in W/m², an deinem Haus gemessen. Sie sagt dem Optimierer, wie viel Solarwärme das Haus gerade erhält; er nutzt das für den aktuellen Zustand und für das Lernen. Die erwartete Sonne später am Tag stammt aus „Quelle der Sonneneinstrahlung“, nicht von diesem Sensor.",
           "solar_forecast_source": "Woher die Sonneneinstrahlung stammt. „Wetter-Entität“ nutzt deine Wetter-Integration, die Einstrahlung oft gar nicht bereitstellt. „Open-Meteo“ ruft eine kostenlose Vorhersage für den unten angegebenen Standort ab; ein Konto ist nicht nötig.",
           "solar_location": "Koordinaten für die Open-Meteo-Einstrahlungsvorhersage. Standardmäßig der Standort deines Zuhauses in Home Assistant. Wird nur verwendet, wenn die Quelle Open-Meteo ist.",
-          "floor_return_temp_entity": "Optional. Wassertemperatur im Rücklauf der Fußbodenheizkreise, dient zur Einschätzung, wie viel Wärme der Estrich speichert.",
+          "floor_return_temp_entity": "Optional. Ein Sensor im Fußbodenkreis selbst: das Wasser, das aus den Fußbodenkreisen zurückkommt, nach Pufferspeicher oder Mischventil. Damit wird geschätzt, wie viel Wärme der Estrich hält. Nicht den Rücklaufsensor der Wärmepumpe verwenden: Bei einer Anlage mit Pufferspeicher misst er den Kreis der Wärmepumpe, weit wärmer als der Boden, und der Plan hielte den Estrich für voll und plante keine Heizung. Ein Wert mehr als 12 K über dem Raum wird ignoriert und meldet einen Reparaturhinweis. Leer lassen, wenn es keinen Sensor im Fußbodenkreis gibt.",
           "lower_floor_temp_entity": "Optional, nur Zwei-Zonen. Ein echtes Thermometer in der unteren Zone. Ohne eines wird das Untergeschoss mit dem Wert des Hauptraumsensors geplant und dargestellt, sodass ein Erdgeschoss, das wärmer oder kälter ist als oben, unsichtbar bleibt.",
           "dhw_temp_entity": "Optional, aber empfohlen. Die tatsächliche Speichertemperatur. Ermöglicht außerdem, dass ein manueller Warmwasser-Boost den Legionellen-Timer zurücksetzt.",
           "buffer_tank_temp_entity": "Optional. Wenn gesetzt, lernt die Integration, wie schnell der Pufferspeicher Wärme verliert, statt sich auf die konfigurierte Schätzung zu verlassen.",
@@ -273,7 +273,7 @@
             "data_description": {
               "buffer_tank_temp_entity": "Optional. Wenn gesetzt, lernt die Integration, wie schnell der Pufferspeicher Wärme verliert, statt sich auf die konfigurierte Schätzung zu verlassen.",
               "dhw_temp_entity": "Optional, aber empfohlen. Die tatsächliche Speichertemperatur. Ermöglicht außerdem, dass ein manueller Warmwasser-Boost den Legionellen-Timer zurücksetzt.",
-              "floor_return_temp_entity": "Optional. Wassertemperatur im Rücklauf der Fußbodenheizkreise, dient zur Einschätzung, wie viel Wärme der Estrich speichert.",
+              "floor_return_temp_entity": "Optional. Ein Sensor im Fußbodenkreis selbst: das Wasser, das aus den Fußbodenkreisen zurückkommt, nach Pufferspeicher oder Mischventil. Damit wird geschätzt, wie viel Wärme der Estrich hält. Nicht den Rücklaufsensor der Wärmepumpe verwenden: Bei einer Anlage mit Pufferspeicher misst er den Kreis der Wärmepumpe, weit wärmer als der Boden, und der Plan hielte den Estrich für voll und plante keine Heizung. Ein Wert mehr als 12 K über dem Raum wird ignoriert und meldet einen Reparaturhinweis. Leer lassen, wenn es keinen Sensor im Fußbodenkreis gibt.",
               "heat_pump_defrost_entity": "Optional. Ein, solange die Pumpe den Kreislauf umkehrt, um Reif vom Außenregister zu schmelzen. Der während einer Abtauung eingekaufte Strom geht ins Register statt ins Haus. Beachte, dass viele Pumpen nur alle paar Minuten abgefragt werden, sodass kurze Abtauungen völlig übersehen werden: Dies ist eine Stichprobe der Abtauaktivität, keine Stoppuhr.",
               "heat_pump_fault_entity": "Optional. Ein, solange die Pumpe eine Störung meldet. Verwendet wird nur, ob eine Störung vorliegt, nie der Code selbst.",
               "heat_pump_mode_entity": "Optional. Die eigene Betriebsartwahl der Pumpe – Kühlen, Heizen, Warmwasser oder eine Kombination aus zwei. Nur lesend, es sei denn, die Steuerung der Pumpenaufgabe ist auf „Steuern“ gesetzt. Eine Pumpe im Kühl- oder reinen Warmwasserbetrieb kann das Haus nicht heizen, und eine im reinen Heizbetrieb kann kein Warmwasser bereiten; ohne diese Angabe kann der Plan also Wärme versprechen, die die Pumpe gerade nicht liefern kann. Bleibt das Feld leer, geht der Optimierer davon aus, dass die Pumpe alles kann.",
@@ -613,7 +613,7 @@
             "data_description": {
               "buffer_tank_temp_entity": "Optional. Wenn gesetzt, lernt die Integration, wie schnell der Pufferspeicher Wärme verliert, statt sich auf die konfigurierte Schätzung zu verlassen.",
               "dhw_temp_entity": "Optional, aber empfohlen. Die tatsächliche Speichertemperatur. Ermöglicht außerdem, dass ein manueller Warmwasser-Boost den Legionellen-Timer zurücksetzt.",
-              "floor_return_temp_entity": "Optional. Wassertemperatur, die aus den Fußbodenheizkreisen zurückkommt; dient zur Einschätzung, wie viel Wärme der Estrich speichert.",
+              "floor_return_temp_entity": "Optional. Ein Sensor im Fußbodenkreis selbst: das Wasser, das aus den Fußbodenkreisen zurückkommt, nach Pufferspeicher oder Mischventil. Damit wird geschätzt, wie viel Wärme der Estrich hält. Nicht den Rücklaufsensor der Wärmepumpe verwenden: Bei einer Anlage mit Pufferspeicher misst er den Kreis der Wärmepumpe, weit wärmer als der Boden, und der Plan hielte den Estrich für voll und plante keine Heizung. Ein Wert mehr als 12 K über dem Raum wird ignoriert und meldet einen Reparaturhinweis. Leer lassen, wenn es keinen Sensor im Fußbodenkreis gibt.",
               "heat_pump_switch_entity": "Optional. Ein Schalter, mit dem die Wärmepumpe in teuren Stunden ausgeschaltet wird.",
               "lower_floor_temp_entity": "Optional, nur bei zwei Zonen. Ein echtes Thermometer in der unteren Zone. Ohne eines wird das untere Geschoss mit dem Wert des Haupt-Raumsensors geplant und dargestellt, sodass ein Erdgeschoss, das wärmer oder kühler als das Obergeschoss ist, unsichtbar bleibt."
             }
@@ -1866,6 +1866,10 @@
       "title": "Ein konfiguriertes Netzentgelt ist negativ",
       "description": "Die Netzentgelt-Ebene enthält einen Satz von {rate} {currency}/kWh (aus der Eingabe {source}). Ein Übertragungsentgelt ist eine Gebühr, ein negativer Wert daher fast immer ein Vorzeichenfehler – und der Plan bepreist jede betroffene Stunde als subventioniert und bevorzugt genau die Stunden, für die der Netzbetreiber Gebühren verlangt. Es wird nichts geändert oder begrenzt: Der Plan rechnet weiter genau mit dem konfigurierten Wert. Korrigiere den Wert auf der Optionsseite \"Netzentgelte und Vertrag\" (oder repariere den Entgeltsensor), dann verschwindet dieser Hinweis im nächsten Planungszyklus."
     },
+    "floor_return_implausible": {
+      "title": "Der Fußboden-Rücklaufsensor misst weit wärmer als jeder Fußbodenkreis",
+      "description": "{entity} misst {reading} °C bei {room} °C im Raum, also mehr als {bound} K darüber. Das Rücklaufwasser eines Fußbodenkreises liegt nur wenige Kelvin über dem beheizten Raum; meist ist hier der Rücklauf der Wärmepumpe selbst oder ein Pufferspeichersensor im Feld für den Fußboden-Rücklauf eingetragen. Aus diesem Feld schätzt die Integration, wie viel Wärme der Estrich hält: Ein so warmer Wert ließ den Plan glauben, der Estrich sei schon voll, und er plante wenig oder keine Heizung, obwohl die Räume unter dem Ziel lagen. Bis dieser Hinweis verschwindet, wird der Wert ignoriert und der Estrich vom Modell geschätzt, wie ohne Sensor. Wähle in den Sensoroptionen einen Sensor im Fußbodenkreis selbst, nach Pufferspeicher oder Mischventil, oder lass das Feld leer; der Hinweis verschwindet im nächsten Zyklus, sobald der Wert plausibel ist."
+    },
     "lower_floor_modelled": {
       "title": "Die Temperatur im Untergeschoss wird modelliert, nicht gemessen",
       "description": "Die Zwei-Zonen-Planung ist aktiv und es ist kein Thermometer für das Untergeschoss konfiguriert, daher startet die untere Zone vom Hauptraumsensor und wird vom thermischen Modell fortgeschrieben – die Kurve „Lower floor (modelled)“ im Plandiagramm. So muss die Zone ohne Sensor geplant werden, und der Fußboden-Rücklaufsensor kann sie nicht ersetzen: Das Rücklaufwasser ist 3–9 K wärmer als der beheizte Raum und speist daher die Estrich-Schätzung, wofür es tatsächlich ein Stellvertreter ist. Eine modellierte Zone kann sich nicht selbst korrigieren und kann daher bei langer Kälte vom echten Untergeschoss abweichen. Weise in den Zonenoptionen den „Lower floor temperature sensor“ zu, um diese Lücke zu schließen; dann verschwindet dieser Hinweis."
diff --git a/custom_components/heatpump_optimizer/translations/en.json b/custom_components/heatpump_optimizer/translations/en.json
index c9179a9f5e..a0f688cfbe 100644
--- a/custom_components/heatpump_optimizer/translations/en.json
+++ b/custom_components/heatpump_optimizer/translations/en.json
@@ -223,7 +223,7 @@
           "solar_radiation_entity": "Optional. Sunshine in W/m² measured at your house. It tells the optimizer how much solar heat the house is getting right now, which it uses for the current state and for learning. Expected sun later in the day comes from the Solar irradiance source, not from this sensor.",
           "solar_forecast_source": "Where to get solar irradiance from. \"Weather entity\" uses your weather integration, which often does not publish irradiance at all. \"Open-Meteo\" fetches a free forecast for the location below; no account is needed.",
           "solar_location": "Coordinate used for the Open-Meteo irradiance forecast. Defaults to your Home Assistant home location. Only used when the source is Open-Meteo.",
-          "floor_return_temp_entity": "Optional. Water temperature coming back from the floor loops, used to gauge how much heat the slab is holding.",
+          "floor_return_temp_entity": "Optional. A sensor in the floor loop itself: the water coming back from the floor loops, after any buffer tank or mixing valve. It gauges how much heat the slab is holding. Do not use the heat pump's own return sensor: on a plant with a buffer tank it reads the heat pump's circuit, far warmer than the floor, and the plan would believe the slab is already full and plan no heating. A reading more than 12 K above the room is ignored and raises a repair notice. Leave empty if there is no sensor in the floor loop.",
           "lower_floor_temp_entity": "Optional, two-zone only. A real thermometer in the lower zone. Without one the lower floor is planned and plotted at whatever the main room sensor reads, so a downstairs that runs warmer or cooler than upstairs is invisible.",
           "dhw_temp_entity": "Optional but recommended. The real tank temperature. Also lets a manual hot water boost reset the anti-legionella timer.",
           "buffer_tank_temp_entity": "Optional. When set, the integration learns how fast the buffer tank loses heat instead of relying on the configured estimate.",
@@ -273,7 +273,7 @@
             "data_description": {
               "buffer_tank_temp_entity": "Optional. When set, the integration learns how fast the buffer tank loses heat instead of relying on the configured estimate.",
               "dhw_temp_entity": "Optional but recommended. The real tank temperature. Also lets a manual hot water boost reset the anti-legionella timer.",
-              "floor_return_temp_entity": "Optional. Water temperature coming back from the floor loops, used to gauge how much heat the slab is holding.",
+              "floor_return_temp_entity": "Optional. A sensor in the floor loop itself: the water coming back from the floor loops, after any buffer tank or mixing valve. It gauges how much heat the slab is holding. Do not use the heat pump's own return sensor: on a plant with a buffer tank it reads the heat pump's circuit, far warmer than the floor, and the plan would believe the slab is already full and plan no heating. A reading more than 12 K above the room is ignored and raises a repair notice. Leave empty if there is no sensor in the floor loop.",
               "heat_pump_defrost_entity": "Optional. On while the pump reverses to melt frost off the outdoor coil. The electricity bought during a defrost goes into the coil rather than into the house. Note that many pumps are only polled every few minutes, so short defrosts are missed entirely: this is a sample of defrost activity, not a stopwatch.",
               "heat_pump_fault_entity": "Optional. On while the pump is reporting a fault. Only whether there is a fault is used, never the code itself.",
               "heat_pump_mode_entity": "Optional. The pump's own mode selector - cooling, heating, hot water, or a combination of two. Read only, unless Pump duty control is set to Control. A pump in a cooling or hot-water-only mode cannot heat the house, and one in a heating-only mode cannot make hot water, so without this the plan can promise heat the pump is not currently able to deliver. Left empty, the optimizer assumes the pump can do everything.",
@@ -613,7 +613,7 @@
             "data_description": {
               "buffer_tank_temp_entity": "Optional. When set, the integration learns how fast the buffer tank loses heat instead of relying on the configured estimate.",
               "dhw_temp_entity": "Optional but recommended. The real tank temperature. Also lets a manual hot water boost reset the anti-legionella timer.",
-              "floor_return_temp_entity": "Optional. Water temperature coming back from the floor loops, used to gauge how much heat the slab is holding.",
+              "floor_return_temp_entity": "Optional. A sensor in the floor loop itself: the water coming back from the floor loops, after any buffer tank or mixing valve. It gauges how much heat the slab is holding. Do not use the heat pump's own return sensor: on a plant with a buffer tank it reads the heat pump's circuit, far warmer than the floor, and the plan would believe the slab is already full and plan no heating. A reading more than 12 K above the room is ignored and raises a repair notice. Leave empty if there is no sensor in the floor loop.",
               "heat_pump_switch_entity": "Optional. A switch used to turn the heat pump off during expensive hours.",
               "lower_floor_temp_entity": "Optional, two-zone only. A real thermometer in the lower zone. Without one the lower floor is planned and plotted at whatever the main room sensor reads, so a downstairs that runs warmer or cooler than upstairs is invisible."
             }
@@ -1866,6 +1866,10 @@
       "title": "A configured grid fee is negative",
       "description": "The grid fee layer contains a rate of {rate} {currency}/kWh (from the {source} input). A transfer fee is a charge, so a negative one is almost always a sign slip — and the plan is pricing every hour it applies to as subsidised, favouring exactly the hours the grid company charges for. Nothing is changed or capped: the plan keeps pricing with exactly the value configured. Correct the value on the \"Transfer fees and contract\" options page (or fix the fee sensor) and this notice clears on the next planning cycle."
     },
+    "floor_return_implausible": {
+      "title": "The floor return sensor reads far warmer than any floor loop",
+      "description": "{entity} reads {reading} °C with the room at {room} °C, more than {bound} K above it. Water returning from a floor loop runs a few kelvin above the room it heats, so this is almost always the heat pump's own return or a buffer-tank sensor configured in the floor return field. The integration estimates how much heat the floor slab holds from that field: a reading this warm made the plan believe the slab was already full, and plan little or no heating while the rooms were below target. Until this clears, the reading is ignored and the slab is estimated by the model, as it is with no sensor. Under the sensor options, pick a sensor in the floor loop itself, after any buffer tank or mixing valve, or leave the field empty; this notice clears on the next cycle once the reading is plausible."
+    },
     "lower_floor_modelled": {
       "title": "The downstairs temperature is modelled, not measured",
       "description": "Two-zone planning is on and no lower-floor thermometer is configured, so the lower zone starts from the main room sensor and is carried forward by the thermal model — the “Lower floor (modelled)” trace on the plan chart. That is how the zone has to be planned without a sensor, and it is not something the floor-return sensor can supply: return water runs 3–9 K above the room it heats, so it drives the slab estimate, which is what it is genuinely a proxy for. What a modelled zone cannot do is correct itself, so over a long cold spell it can drift from the real downstairs. Assigning “Lower floor temperature sensor” under the zone options closes that loop; this notice clears when you do."
diff --git a/custom_components/heatpump_optimizer/translations/sv.json b/custom_components/heatpump_optimizer/translations/sv.json
index 6b035c78dc..47b1ff7bce 100644
--- a/custom_components/heatpump_optimizer/translations/sv.json
+++ b/custom_components/heatpump_optimizer/translations/sv.json
@@ -223,7 +223,7 @@
           "solar_radiation_entity": "Valfritt. Solinstrålning i W/m² uppmätt vid ditt hus. Den talar om för optimeringen hur mycket solvärme huset får just nu, vilket används för aktuellt tillstånd och för inlärning. Väntad sol senare på dagen kommer från Källa för solinstrålning, inte från den här givaren.",
           "solar_forecast_source": "Var solinstrålningen ska hämtas ifrån. \"Väderentitet\" använder din väderintegration, som ofta inte publicerar solinstrålning alls. \"Open-Meteo\" hämtar en kostnadsfri prognos för platsen nedan; inget konto behövs.",
           "solar_location": "Koordinat som används för Open-Meteos solinstrålningsprognos. Utgår från Home Assistants hemposition. Används bara när källan är Open-Meteo.",
-          "floor_return_temp_entity": "Valfritt. Vattentemperaturen tillbaka från golvslingorna, används för att bedöma hur mycket värme plattan lagrar.",
+          "floor_return_temp_entity": "Valfri. En givare i själva golvslingan: vattnet som kommer tillbaka från golvslingorna, efter ackumulatortank eller shuntventil. Den används för att uppskatta hur mycket värme plattan håller. Använd inte värmepumpens egen returgivare: i en anläggning med ackumulatortank mäter den värmepumpens krets, långt varmare än golvet, och planen skulle tro att plattan redan är full och inte planera någon värme. Ett värde mer än 12 K över rummet ignoreras och ger ett reparationsmeddelande. Lämna tomt om det inte finns någon givare i golvslingan.",
           "lower_floor_temp_entity": "Valfritt, endast tvåzonsläge. En riktig givare på nedre plan. Utan en sådan planeras och ritas nedre plan efter vad rumsgivaren visar, så ett nedre plan som är varmare eller kallare än övre plan syns inte.",
           "dhw_temp_entity": "Valfritt men rekommenderas. Beredarens verkliga temperatur. Gör också att en manuell varmvattenkörning nollställer legionellatimern.",
           "buffer_tank_temp_entity": "Valfritt. När den anges lär sig integrationen hur snabbt buffertanken svalnar i stället för att förlita sig på det konfigurerade värdet.",
@@ -273,7 +273,7 @@
             "data_description": {
               "buffer_tank_temp_entity": "Valfritt. När den anges lär sig integrationen hur snabbt buffertanken svalnar i stället för att förlita sig på det konfigurerade värdet.",
               "dhw_temp_entity": "Valfritt men rekommenderas. Beredarens verkliga temperatur. Gör också att en manuell varmvattenkörning nollställer legionellatimern.",
-              "floor_return_temp_entity": "Valfritt. Vattentemperaturen tillbaka från golvslingorna, används för att bedöma hur mycket värme plattan lagrar.",
+              "floor_return_temp_entity": "Valfri. En givare i själva golvslingan: vattnet som kommer tillbaka från golvslingorna, efter ackumulatortank eller shuntventil. Den används för att uppskatta hur mycket värme plattan håller. Använd inte värmepumpens egen returgivare: i en anläggning med ackumulatortank mäter den värmepumpens krets, långt varmare än golvet, och planen skulle tro att plattan redan är full och inte planera någon värme. Ett värde mer än 12 K över rummet ignoreras och ger ett reparationsmeddelande. Lämna tomt om det inte finns någon givare i golvslingan.",
               "heat_pump_defrost_entity": "Valfritt. På medan pumpen vänder cykeln för att smälta bort frost från utomhusbatteriet. Elen som köps under en avfrostning går till batteriet i stället för in i huset. Tänk på att många pumpar bara avfrågas med några minuters mellanrum, så korta avfrostningar missas helt: det här är ett stickprov på avfrostning, inte ett tidtagarur.",
               "heat_pump_fault_entity": "Valfritt. På medan pumpen larmar om ett fel. Bara om det finns ett fel används, aldrig själva felkoden.",
               "heat_pump_mode_entity": "Valfritt. Pumpens eget lägesval - kyla, värme, varmvatten eller en kombination av två. Läses bara av, om inte Styrning av pumpens uppgift står på Styrning. En pump som står i kylläge eller enbart varmvatten kan inte värma huset, och en som står i enbart värmeläge kan inte göra varmvatten. Utan det här kan planen alltså lova värme som pumpen just då inte kan leverera. Lämnas fältet tomt antar optimeringen att pumpen klarar allt.",
@@ -613,7 +613,7 @@
             "data_description": {
               "buffer_tank_temp_entity": "Valfritt. När den anges lär sig integrationen hur snabbt buffertanken svalnar i stället för att förlita sig på det konfigurerade värdet.",
               "dhw_temp_entity": "Valfritt men rekommenderas. Beredarens verkliga temperatur. Gör också att en manuell varmvattenkörning nollställer legionellatimern.",
-              "floor_return_temp_entity": "Valfritt. Vattentemperaturen tillbaka från golvslingorna, används för att bedöma hur mycket värme plattan lagrar.",
+              "floor_return_temp_entity": "Valfri. En givare i själva golvslingan: vattnet som kommer tillbaka från golvslingorna, efter ackumulatortank eller shuntventil. Den används för att uppskatta hur mycket värme plattan håller. Använd inte värmepumpens egen returgivare: i en anläggning med ackumulatortank mäter den värmepumpens krets, långt varmare än golvet, och planen skulle tro att plattan redan är full och inte planera någon värme. Ett värde mer än 12 K över rummet ignoreras och ger ett reparationsmeddelande. Lämna tomt om det inte finns någon givare i golvslingan.",
               "heat_pump_switch_entity": "Valfritt. En strömbrytare som används för att stänga av värmepumpen under dyra timmar.",
               "lower_floor_temp_entity": "Valfritt, endast tvåzonsläge. En riktig givare på nedre plan. Utan en sådan planeras och ritas nedre plan efter vad rumsgivaren visar, så ett nedre plan som är varmare eller kallare än övre plan syns inte."
             }
@@ -1866,6 +1866,10 @@
       "title": "En konfigurerad nätavgift är negativ",
       "description": "Nätavgiftslagret innehåller en avgift på {rate} {currency}/kWh (från källan {source}). En överföringsavgift är en kostnad, så en negativ är nästan alltid ett teckenfel — och planen prissätter varje timme den gäller som subventionerad, och gynnar just de timmar nätbolaget tar betalt för. Ingenting ändras eller begränsas: planen fortsätter att prissätta med exakt det värde som konfigurerats. Rätta värdet på alternativsidan \"Överföringsavgifter och avtal\" (eller åtgärda avgiftssensorn) så försvinner meddelandet vid nästa planeringscykel."
     },
+    "floor_return_implausible": {
+      "title": "Returgivaren för golvvärmen visar långt varmare än någon golvslinga",
+      "description": "{entity} visar {reading} °C när rummet har {room} °C, mer än {bound} K över. Returvattnet från en golvslinga ligger bara några kelvin över rummet det värmer, så nästan alltid är det värmepumpens egen returgivare eller en ackumulatortanksgivare som angetts i fältet för golvvärmens retur. Ur det fältet uppskattar integrationen hur mycket värme plattan håller: ett så varmt värde fick planen att tro att plattan redan var full, och den planerade lite eller ingen värme fast rummen låg under målet. Tills meddelandet försvinner ignoreras värdet och plattan uppskattas av modellen, som utan givare. Välj under givaralternativen en givare i själva golvslingan, efter ackumulatortank eller shuntventil, eller lämna fältet tomt; meddelandet försvinner nästa cykel när värdet är rimligt."
+    },
     "lower_floor_modelled": {
       "title": "Temperaturen på nedre plan är modellerad, inte uppmätt",
       "description": "Tvåzonsplanering är på och ingen givare för nedre plan är konfigurerad, så nedre zonen utgår från rumsgivaren och räknas därefter fram av den termiska modellen — kurvan “Nedre plan (modellerad)” i plandiagrammet. Så måste zonen planeras utan givare, och det är inget returgivaren kan bidra med: returvattnet ligger 3–9 K över rummet det värmer, så det används till uppskattningen av plattan, vilket är det som det verkligen är ett mått på. Det en modellerad zon inte kan göra är att korrigera sig själv, så under en lång köldperiod kan den glida ifrån det verkliga nedre planet. Ange “Givare för temperaturen på nedre plan” under zonalternativen så sluts den kretsen; då försvinner meddelandet."
diff --git a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
index 936b5fbb8a..b6b049f42f 100644
--- a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
+++ b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
@@ -11,7 +11,7 @@
 
 const CARD_TAG = "heatpump-optimizer-card";
 const EDITOR_TAG = "heatpump-optimizer-card-editor";
-const CARD_VERSION = "10.0.1";
+const CARD_VERSION = "10.0.2";
 
 // Home Assistant's default --primary-color (#03a9f4) is 2.63:1 on a white
 // card — too light for text or for white label text on a filled button.
@@ -3063,6 +3063,13 @@ const AUTOPAN_INTERVAL_MS = 90;
 // service's expiry default is exactly the bug the published attribute prevents.
 const MANUAL_PLAN_WINDOW_FALLBACK_H = 20;
 
+// How far ahead of the server's clock the browser's may run before "Apply this
+// plan" sends a slot the service refuses: the card trims at its own `now` plus
+// the window, the service at the server's. One plan step, because runs start
+// on step boundaries: holding back a run that starts within the last step costs
+// at most one step's pin before the expiry, and tolerates a clock a step fast.
+const APPLY_CLOCK_SKEW_MS = PLAN_STEP_MS;
+
 // Range of the hot water minimum slider. The floor matches the options flow so
 // the two editors of the same setting agree. There is deliberately no margin
 // constant here: the *ceiling* is computed by the integration and published as
@@ -11570,13 +11577,17 @@ class ManualPlan {
 
   /** Pin the current arrangement for the manual-plan window.
    *
-   * Only the editable part of the horizon is sent: the past cannot be
-   * rescheduled, and pinning a slot that has already happened would be
-   * meaningless.
+   * Only the part of the horizon the window covers is sent: the past cannot
+   * be rescheduled, and `build_override` refuses any slot starting beyond now
+   * plus the window, so one run past it would fail the whole apply (#3636).
+   * The ceiling is the window alone (`applyEnd`), not `editCeiling`, which
+   * also carries the zoomed visible end; a run straddling it is sent whole,
+   * since the backend frees every step past the expiry itself.
    */
   apply() {
     if (!this.host.hass || !this.host.hass.callService) return;
-    const [lo] = this.bounds();
+    const lo = this.editFloor();
+    const hi = this.ceilingParts().applyEnd - APPLY_CLOCK_SKEW_MS;
     const runs = this.draft();
     const payload = {};
     for (const spec of this.laneSpecs()) {
@@ -11587,7 +11598,7 @@ class ManualPlan {
       // off for the rest of the day.
       if (!this.host.plan.forecastOf(spec.channel).length) continue;
       payload[`${spec.channel}_slots`] = (runs[spec.channel] || [])
-        .filter((r) => r.end > lo)
+        .filter((r) => r.end > lo && r.start < hi)
         .map((r) => ({
           start: new Date(Math.max(r.start, lo)).toISOString(),
           end: new Date(r.end).toISOString(),
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index a8d2eee1f1..eb5c2feced 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -283,7 +283,7 @@
   "source": "docs/architecture.md",
   "claim": "45 modules",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=93 measured=93",
+  "result": "documented=94 measured=94",
   "verdict": "true",
   "truth": ""
  },
@@ -292,7 +292,7 @@
   "source": "docs/architecture.md",
   "claim": "the module map is the package's module list",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "on disk=93, listed=93, missing=[], phantom=[]",
+  "result": "on disk=94, listed=94, missing=[], phantom=[]",
   "verdict": "true",
   "truth": "0 modules are absent from the map: "
  },
@@ -373,7 +373,7 @@
   "source": "manifest.json",
   "claim": "manifest version equals VERSION",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented='10.0.1' measured='10.0.1'",
+  "result": "documented='10.0.2' measured='10.0.2'",
   "verdict": "true",
   "truth": ""
  },
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index 648027e2af..2637058615 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -35,8 +35,8 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C29 | `docs/architecture.md:module map` | config_flow.py -- Setup flow plus 24 option pages behind two menus | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=24 measured=24 | **true** |  |
 | C30 | `docs/configuration.md` | every documented Default (97 rows) is the default the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 97 compared, mismatches=[] | **true** |  |
 | C31 | `docs/configuration.md` | every documented Range (104 rows) is the NumberSelector min/max the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 104 compared, mismatches=[] | **true** |  |
-| C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=93 measured=93 | **true** |  |
-| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=93, listed=93, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
+| C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=94 measured=94 | **true** |  |
+| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=94, listed=94, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
 | C34 | `docs/architecture.md:The Home Assistant boundary` | the boundary sentence's count of modules importing `homeassistant` at module level | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=33 measured=33 | **true** |  |
 | C35 | `docs/architecture.md:The Home Assistant boundary` | the named modules are the complete set of module-level importers | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | named=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], measured=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], unnamed=[] | **true** | unnamed module-level importers:  |
 | C36 | `docs/architecture.md:The Home Assistant boundary` | everything outside the named set is free of homeassistant, so each module can be driven with no Home Assistant running | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 0 modules outside the named set import homeassistant at module level | **true** | modules outside the named set import homeassistant at module level and cannot be imported without it:  |
@@ -45,7 +45,7 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C39 | `docs/architecture.md:module map` | sensor.py -- 62 sensors | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=62 measured=62 | **true** |  |
 | C40 | `docs/architecture.md:module map` | switch.py -- the comment names every switch the platform constructs | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Away', 'Block DHW', 'Block Space Heating', 'Boost Space Heating', 'DHW Boost', 'Optimizer Active'], the platform constructs ['Away', 'Block DHW', 'Block Space Heating', 'Boost Space Heating', 'DHW Boost', 'Optimizer Active'] | **true** |  |
 | C41 | `docs/architecture.md:module map` | binary_sensor.py -- the comment names every binary sensor the platform constructs | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Away Mode', 'External Heat Source', 'Input Problem', 'Mold Floor Breach', 'Open Window Detected', 'Wood Cheaper Than Heat Pump'], the platform constructs ['Away Mode', 'External Heat Source', 'Input Problem', 'Mold Floor Breach', 'Open Window Detected', 'Wood Cheaper Than Heat Pump'] | **true** |  |
-| C42 | `manifest.json` | manifest version equals VERSION | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='10.0.1' measured='10.0.1' | **true** |  |
+| C42 | `manifest.json` | manifest version equals VERSION | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='10.0.2' measured='10.0.2' | **true** |  |
 | C43 | `hacs.json` | hacs.json requires Home Assistant 2025.2.0 | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='2025.2.0' measured='2025.2.0' | **true** |  |
 | C44 | `README.md badge` | Home Assistant 2025.2.0+ badge matches hacs.json | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='2025.2.0' measured='2025.2.0' | **true** |  |
 | C45 | `README.md Requirements` | Home Assistant 2025.2.0 or newer | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='2025.2.0' measured='2025.2.0' | **true** |  |
diff --git a/dev/audit/rounds/round4/D6/claims.py b/dev/audit/rounds/round4/D6/claims.py
index ed03be4075..090b5d503b 100644
--- a/dev/audit/rounds/round4/D6/claims.py
+++ b/dev/audit/rounds/round4/D6/claims.py
@@ -91,7 +91,7 @@ against a document that is CORRECT.
                                          Range row on the expert thermal-model
                                          table; 101 with R10-USER-DOCS-FINAL's
                                          per-field rows on the options pages)
-    RESULT arch_modules_on_disk=93       (92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 85 until R10-WHY-NOW-WIDGET's slot_drivers.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
+    RESULT arch_modules_on_disk=94       (93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 85 until R10-WHY-NOW-WIDGET's slot_drivers.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
                                          66 until R9 F2.5's batchmath.py;
                                          65 until #1588's pump_arbiter.py; 64
                                          until #1408's store.py;
@@ -117,7 +117,7 @@ against a document that is CORRECT.
                                          bytes of, so nothing compared these
                                          numbers to a run between 2026-09-17
                                          and then)
-    RESULT arch_map_listed=93            (92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
+    RESULT arch_map_listed=94            (93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
                                          66 until R9 F2.5's batchmath.py;
                                          was 45; 11 were missing; 66 with
                                          #1588's pump_arbiter.py added to
diff --git a/dev/programme/delivery/3640.md b/dev/programme/delivery/3640.md
new file mode 100644
index 0000000000..0dca79fd39
--- /dev/null
+++ b/dev/programme/delivery/3640.md
@@ -0,0 +1 @@
+- [#3640](https://github.com/tvofi/heatpump_optimizer/pull/3640) — **open**, R11-OUTSIDE-SLAB-SEED-GUARD: r11 outside slab seed guard (R11-OUTSIDE-SLAB-SEED-GUARD)
diff --git a/dev/programme/delivery/3644.md b/dev/programme/delivery/3644.md
new file mode 100644
index 0000000000..b2a44aeae8
--- /dev/null
+++ b/dev/programme/delivery/3644.md
@@ -0,0 +1 @@
+- [#3644](https://github.com/tvofi/heatpump_optimizer/pull/3644) — **open**, R11-PRE-ROUND-METRICS: r11 pre round metrics (R11-PRE-ROUND-METRICS)
diff --git a/dev/programme/delivery/3649.md b/dev/programme/delivery/3649.md
new file mode 100644
index 0000000000..ba9ef185f7
--- /dev/null
+++ b/dev/programme/delivery/3649.md
@@ -0,0 +1 @@
+- [#3649](https://github.com/tvofi/heatpump_optimizer/pull/3649) — **open**, R11-OUTSIDE-APPLY-PLAN-CEILING: apply plan only up to the manual-plan window (R11-OUTSIDE-APPLY-PLAN-CEILING)
diff --git a/dev/programme/delivery/3652.md b/dev/programme/delivery/3652.md
new file mode 100644
index 0000000000..c296b5cbaa
--- /dev/null
+++ b/dev/programme/delivery/3652.md
@@ -0,0 +1 @@
+- [#3652](https://github.com/tvofi/heatpump_optimizer/pull/3652) — **open**, R11-HOTFIX-MAIN-SELFTEST-SCOPE-4: re-record the self-test scope table for main's red (R11-HOTFIX-MAIN-SELFTEST-SCOPE-4)
diff --git a/docs/architecture.md b/docs/architecture.md
index ab9956a76a..e69e659580 100644
--- a/docs/architecture.md
+++ b/docs/architecture.md
@@ -5,7 +5,7 @@ integration does rather than how it is built, start with
 [how-it-works.md](how-it-works.md).
 
 The shape is a thin Home Assistant layer wrapped around a much larger core that
-knows nothing about Home Assistant: 93 modules, of which 33 import the
+knows nothing about Home Assistant: 94 modules, of which 33 import the
 `homeassistant` package at module level, one more touches it inside a single
 function, and the rest take numbers in and give numbers back. The glue reads
 entity states, writes actuators and persists learned state. Keeping those two
@@ -183,6 +183,7 @@ custom_components/heatpump_optimizer/
 ├── presets.py            # Building archetypes to thermal parameters
 ├── external_heat.py      # Wood-furnace detection with hysteresis and decay
 ├── setpoint_check.py     # Disinfection set-point consistency: configured vs live
+├── slab_seed.py          # Whether a floor-return reading may seed the slab estimate
 │
 │   # The pump's own account of itself
 ├── pump_mode.py          # Operating-mode vocabulary: can it heat, can it make
@@ -279,7 +280,7 @@ custom_components/heatpump_optimizer/
 
 ## The Home Assistant boundary
 
-33 of the 93 modules import `homeassistant` at module level: `__init__`,
+33 of the 94 modules import `homeassistant` at module level: `__init__`,
 `config_flow`, `coordinator`, `open_meteo`, `frontend`, the six entity
 platforms `sensor`, `binary_sensor`, `button`, `climate`, `switch`, `datetime`,
 and the supporting modules `accuracy`, `away`, `boost`, `currency`, `debugger`, `defrost`,
@@ -288,7 +289,7 @@ and the supporting modules `accuracy`, `away`, `boost`, `currency`, `debugger`,
 reaches for `homeassistant.util.dt` inside a function, as the fallback when no
 clock function was injected.
 
-The other 59 modules are deliberately free of it, so each can be driven
+The other 60 modules are deliberately free of it, so each can be driven
 directly by `tests/features.py` with no Home Assistant running. That matters
 because the failure mode of this integration is a *plausible* plan: a detector
 that never fires, or a watchdog that lets a flatline through, produces output
diff --git a/tests/card.mjs b/tests/card.mjs
index 77765a6838..4fdf7cdbd7 100644
--- a/tests/card.mjs
+++ b/tests/card.mjs
@@ -2116,6 +2116,122 @@ const editable = () => {
     JSON.stringify(iso));
 }
 
+// #3636: a published plan reaching past the manual-plan window made "Apply this
+// plan" fail every time, because `build_override` refuses a slot starting
+// beyond now plus the window. The card trimmed at the edit floor only, so it
+// sent runs the editor itself would not let the user touch. The captured plan
+// is extended to 48 h past its first step with runs before, across, just
+// inside and past the ceiling: the published window (`applyEnd`), not the
+// zoomed visible end `editCeiling` also carries.
+{
+  const STEP = 15 * 60000;
+  const ceiling = FROZEN + 20 * HOUR;
+  const at = (h) => ceiling + h * HOUR;
+  // The forecast's `t` is local wall time with no offset, as the sensor
+  // publishes it, so extended steps are written the same way.
+  const local = (ms) => {
+    const d = new Date(ms);
+    const p = (n) => String(n).padStart(2, "0");
+    return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}` +
+      `T${p(d.getHours())}:${p(d.getMinutes())}:00`;
+  };
+  // [start, end) in hours from the ceiling, per channel.
+  const runs = {
+    dhw_power: [[-4, -3], [-2, 0.5], [1, 2], [4, 6]],
+    // Starts one step short of the ceiling: inside it on this clock, but past
+    // the server's on a browser clock a step ahead -- the skew allowance.
+    space_power: [[-4, -3], [-0.25, 1], [4, 6]],
+  };
+  const extended = (windowHours, seeded = runs) => {
+    const st = JSON.parse(JSON.stringify(slotStates));
+    const first = Date.parse(plan.dhw_plan.forecast[0].t);
+    for (const [id, field] of [[DEFAULT_DHW, "dhw_power"],
+                               [DEFAULT_SPACE, "space_power"]]) {
+      if (windowHours !== undefined) {
+        st[id].attributes.manual_plan_window_hours = windowHours;
+      }
+      const fc = st[id].attributes.forecast;
+      const last = fc[fc.length - 1];
+      for (let t = Date.parse(last.t) + STEP; t < first + 48 * HOUR; t += STEP) {
+        fc.push({ ...last, t: local(t) });
+      }
+      for (const f of fc) {
+        const t = Date.parse(f.t);
+        if (t < at(-4.5)) continue;
+        f[field] = seeded[field].some(([a, b]) => t >= at(a) && t < at(b)) ? 3 : 0;
+      }
+    }
+    return st;
+  };
+  const applied = (states, geom) => {
+    const c = build(states, { what_if: true });
+    c._hass = mkHass(states);
+    c._onCardClick({});
+    if (geom) c.geomAt = () => geom;
+    called = null;
+    c.manual.apply();
+    return { card: c, data: (called && called.data) || {} };
+  };
+  const { card, data } = applied(extended());
+  const drafted = [...card.manual.draft().dhw, ...card.manual.draft().space];
+  check("the extended plan drafts runs at and past the window (#3636)",
+    drafted.some((r) => r.start >= ceiling), JSON.stringify(drafted));
+  // Only the seeded tail: the captured plan's own earlier runs are untouched.
+  const span = (slots) => (slots || [])
+    .filter((sl) => Date.parse(sl.start) >= at(-4.5))
+    .map((sl) => [Date.parse(sl.start), Date.parse(sl.end)].map(
+      (ms) => (ms - ceiling) / HOUR));
+  check("no slot sent starts at or after the manual-plan window (#3636)",
+    [...(data.dhw_slots || []), ...(data.space_slots || [])]
+      .every((sl) => Date.parse(sl.start) < ceiling),
+    JSON.stringify(data));
+  check("a run straddling the window is sent whole, later ones dropped (#3636)",
+    JSON.stringify(span(data.dhw_slots)) === JSON.stringify([[-4, -3], [-2, 0.5]]),
+    JSON.stringify(span(data.dhw_slots)));
+  check("a run starting within one step of the window is held back for clock skew (#3636)",
+    JSON.stringify(span(data.space_slots)) === JSON.stringify([[-4, -3]]),
+    JSON.stringify(span(data.space_slots)));
+  // The ceiling is the window, not the zoomed view: zoomed in so the visible
+  // end falls 3 h before the window, `editCeiling` would drop the run that
+  // straddles the window and the one before it. Design choice: what is applied
+  // does not depend on the zoom.
+  const zoomed = applied(extended(), { windowStart: 0, windowEnd: at(-3) });
+  check("a zoomed-in view does not change the applied runs (#3636)",
+    zoomed.card.manual.editCeiling() <= at(-3) &&
+      JSON.stringify(span(zoomed.data.dhw_slots)) ===
+        JSON.stringify([[-4, -3], [-2, 0.5]]),
+    JSON.stringify({ editCeiling: (zoomed.card.manual.editCeiling() - ceiling) / HOUR,
+                     dhw: span(zoomed.data.dhw_slots) }));
+  // The skew allowance is one step, not more: a run starting two steps
+  // before the window is inside the server's acceptance and is sent.
+  const twoSteps = applied(extended(undefined, {
+    dhw_power: [],
+    space_power: [[-4, -3], [-0.5, 1]],
+  })).data;
+  check("a run starting two steps before the window is sent (#3636)",
+    JSON.stringify(span(twoSteps.space_slots)) ===
+      JSON.stringify([[-4, -3], [-0.5, 1]]),
+    JSON.stringify(span(twoSteps.space_slots)));
+
+  // Null control: the captured plan ends inside the window, so the payload
+  // must be byte-identical to the one a window too wide to bind produces.
+  check("the captured plan ends inside the window (#3636)",
+    drag.manual.planEnd() < ceiling - STEP,
+    new Date(drag.manual.planEnd()).toISOString());
+  const inside = applied(slotStates).data;
+  const unbound = (() => {
+    const st = JSON.parse(JSON.stringify(slotStates));
+    for (const id of [DEFAULT_DHW, DEFAULT_SPACE]) {
+      st[id].attributes.manual_plan_window_hours = 1000;
+    }
+    return applied(st).data;
+  })();
+  check("a plan wholly inside the window sends the same payload (#3636)",
+    (inside.dhw_slots || []).length > 0 &&
+      JSON.stringify(inside) === JSON.stringify(unbound),
+    JSON.stringify({ inside, unbound }));
+}
+
 // Prices are shown in the user's currency, not the author's.
 {
   const saved = drag._hass;
diff --git a/tests/closures.json b/tests/closures.json
index 35c3fc9420..b6b5fc9f18 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -265,6 +265,7 @@
    "custom_components/heatpump_optimizer/services.yaml",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
+   "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
    "custom_components/heatpump_optimizer/store.py",
@@ -431,6 +432,7 @@
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
+   "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
    "custom_components/heatpump_optimizer/store.py",
@@ -538,6 +540,7 @@
    "custom_components/heatpump_optimizer/running_signal.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
+   "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
    "custom_components/heatpump_optimizer/store.py",
@@ -643,6 +646,7 @@
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
+   "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
    "custom_components/heatpump_optimizer/store.py",
@@ -762,6 +766,7 @@
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
+   "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
    "custom_components/heatpump_optimizer/store.py",
@@ -893,6 +898,7 @@
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
+   "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
    "custom_components/heatpump_optimizer/store.py",
@@ -1021,6 +1027,7 @@
    "custom_components/heatpump_optimizer/running_signal.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
+   "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
    "custom_components/heatpump_optimizer/store.py",
@@ -1162,6 +1169,7 @@
    "custom_components/heatpump_optimizer/services.yaml",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
+   "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
    "custom_components/heatpump_optimizer/store.py",
@@ -1299,6 +1307,7 @@
    "custom_components/heatpump_optimizer/services.yaml",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
+   "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
    "custom_components/heatpump_optimizer/store.py",
@@ -1628,6 +1637,7 @@
    "custom_components/heatpump_optimizer/services.yaml",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
+   "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
    "custom_components/heatpump_optimizer/store.py",
@@ -2153,6 +2163,7 @@
    "custom_components/heatpump_optimizer/services.yaml",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
+   "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
    "custom_components/heatpump_optimizer/store.py",
@@ -2348,6 +2359,7 @@
    "custom_components/heatpump_optimizer/services.yaml",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
+   "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
    "custom_components/heatpump_optimizer/store.py",
@@ -2504,6 +2516,7 @@
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
+   "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
    "custom_components/heatpump_optimizer/store.py",
@@ -2655,6 +2668,7 @@
    "custom_components/heatpump_optimizer/services.yaml",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
+   "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
    "custom_components/heatpump_optimizer/store.py",
@@ -2833,6 +2847,7 @@
    "custom_components/heatpump_optimizer/running_signal.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
+   "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
    "custom_components/heatpump_optimizer/store.py",
@@ -3017,6 +3032,7 @@
    "custom_components/heatpump_optimizer/services.yaml",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
+   "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
    "custom_components/heatpump_optimizer/store.py",
@@ -3408,6 +3424,7 @@
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
+   "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
    "custom_components/heatpump_optimizer/store.py",
@@ -3576,6 +3593,7 @@
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
+   "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
    "custom_components/heatpump_optimizer/store.py",
@@ -3681,6 +3699,7 @@
    "custom_components/heatpump_optimizer/running_signal.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
+   "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
    "custom_components/heatpump_optimizer/store.py",
@@ -3845,6 +3864,7 @@
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
+   "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
    "custom_components/heatpump_optimizer/store.py",
@@ -3943,6 +3963,7 @@
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
+   "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
    "custom_components/heatpump_optimizer/store.py",
@@ -4066,6 +4087,7 @@
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
+   "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
    "custom_components/heatpump_optimizer/store.py",
@@ -4175,6 +4197,8 @@
    "tools/audit/seat/review_strength.py",
    "tools/audit/seat/roster_lib.py",
    "tools/audit/seat/roster_queue.py",
+   "tools/audit/seat/round_metrics.py",
+   "tools/audit/seat/round_metrics_selftest.py",
    "tools/audit/seat/scorecard.py",
    "tools/audit/seat/scorecard_selftest.py",
    "tools/audit/seat/seat_gen.py",
@@ -5292,7 +5316,7 @@
   },
   "tests/env_drift.py": {
    "rc": 0,
-   "seconds": 0.4
+   "seconds": 1.0
   },
   "tests/features.py": {
    "rc": 0,
@@ -5312,7 +5336,7 @@
   },
   "tests/guard_pins.py": {
    "rc": 0,
-   "seconds": 5.8
+   "seconds": 8.2
   },
   "tests/ha_contract.py": {
    "rc": 0,
@@ -5356,11 +5380,11 @@
   },
   "tests/structure.py": {
    "rc": 0,
-   "seconds": 17.9
+   "seconds": 21.1
   },
   "tests/typing_ruler.py": {
    "rc": 0,
-   "seconds": 20.8
+   "seconds": 30.8
   },
   "tests/validate.py": {
    "rc": 0,
diff --git a/tests/deployment_shape.py b/tests/deployment_shape.py
index a3acd70f57..f1e6575540 100644
--- a/tests/deployment_shape.py
+++ b/tests/deployment_shape.py
@@ -37,9 +37,9 @@ child from ``inspect.getfile``.
 
 COST OF THE SHAPE (#1218, round-5 D3-08). Materialising the shape copies the
 tracked package file by file (``_materialise``, below), and the gate's tracer
-records every read, so this lane's recorded closure is the package: all 112
+records every read, so this lane's recorded closure is the package: all 113
 files under ``custom_components/heatpump_optimizer/``, Python and non-Python
-alike (111 until R10-START-COUNTER-EDGES's ``running_signal.py``, 110 until
+alike (112 until #3616's ``slab_seed.py``, 111 until R10-START-COUNTER-EDGES's ``running_signal.py``, 110 until
 R10-ADVISOR-STEADY-START's ``whatif.py``, 109 until R10-DUTY-SWITCH-PLANNER-PRICE's
 ``duty_legs.py``, 108 until the supply-hold PR's ``supply_hold.py``, 107 until
 R10-DUTY-SWITCH-RESTART-LEARNING's ``duty_switch.py``, 78 until R9 F2.5's ``batchmath.py``, 79 until R9 UI-1's six brand
@@ -57,8 +57,9 @@ which drives the CI ratchet's archscore measurement and so opens the package
 the way this lane's recorder does. A diff touching any production file
 therefore selects this lane. That is a selection cost, not a
 duplicate-assertion one: the same
-recording finds 162 of the 528 script pairs (33 choose 2) sharing 0.80 or more
-of their production-module closure, all 162 among the 406 pairs whose two
+recording finds 163 of the 528 script pairs (33 choose 2) sharing 0.80 or more
+of their production-module closure (162 before #3616 re-recorded the closures
+that import the coordinator), all 163 among the 406 pairs whose two
 scripts each have a non-empty production closure (``tests/arch_score.py``,
 ``tests/ha_contract.py``, ``tests/layout.py`` and ``tests/md_tables.mjs`` have none;
 ``tests/harness_headers.py`` joined the comparable set, and ten pairs, when
diff --git a/tests/features.py b/tests/features.py
index 5b688a9204..f8a7f6c15a 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -92330,6 +92330,146 @@ R.check(
 )
 
 
+# --- #3616: an implausible slab seed is refused --------------------------------
+R.section("#3616: a floor-return reading far above the room does not seed the slab")
+
+# A heat-pump return on a buffer plant, configured in the floor-return field,
+# reads far warmer than any floor loop: the slab estimate followed it and the
+# plan held 0 kWh of space heating with the room below its comfort band.
+# Closed loop through the production coordinator and solver (the r9f12 rig):
+# room 19.6 C under a 22 C comfort target, 6 C outside, as the reporter's.
+from heatpump_optimizer import slab_seed as _ssg  # noqa: E402
+
+_ssg_start = datetime(2026, 11, 15, 6, 0, tzinfo=UTC)
+
+
+def _ssg_cycles(return_c, cycles=6, mode=None, defrost=None):
+    """Hourly cycles: (slab after each, planned space kWh, issues raised)."""
+    cfg = dict(_r9f12_seed_cfg, comfort_temperature=22.0)
+    live = {"sensor.indoor": ("19.6", "°C"), "sensor.outdoor": ("6.0", "°C")}
+    if return_c is not None:
+        cfg["floor_return_temp_entity"] = "sensor.ret"
+        live["sensor.ret"] = (str(return_c), "°C")
+    if mode is not None:
+        cfg["heat_pump_mode_entity"] = "select.mode"
+        live["select.mode"] = (mode, None)
+    if defrost is not None:
+        cfg["heat_pump_defrost_entity"] = "binary_sensor.defrost"
+        live["binary_sensor.defrost"] = (defrost, None)
+    hass = FakeHass()
+    # The notifier fires an event on a mode or defrost change; this rig's bus
+    # records nothing, so a sink stands in for it.
+    hass.bus.async_fire = lambda *_a, **_k: None
+    entry = _r9f12_entry(data=cfg, entry_id=f"ssg_{return_c}_{mode}_{defrost}")
+    seen = []
+    try:
+        for hour in range(cycles):
+            now = _ssg_start + timedelta(hours=hour)
+            _r9f12_dt.freeze(now)
+            for name, (value, unit) in live.items():
+                hass.states.set(name, FakeState(value, unit=unit) if unit else FakeState(value))
+            _r9f12_seed_prices(hass, now)
+            if hour == 0:
+                _r9f12_aio.run(_r9f12_integ.async_setup_entry(hass, entry))
+                coord = entry.runtime_data
+            _r9f12_aio.run(coord.async_refresh())
+            seen.append(coord._current_state.slab_temperature)
+        kwh = sum(float(p) for p in coord._optimization_result.power_schedule) * 0.25
+    finally:
+        _r9f12_dt.freeze(None)
+    return seen, kwh, {i[1]: i[2] for i in getattr(hass, "issues", [])}
+
+
+_ssg_warm = _ssg_cycles(38.0)
+_ssg_none = _ssg_cycles(None)
+_ssg_ok = _ssg_cycles(26.0)
+R.check(
+    "#3616: a 38 C heat-pump return in the floor-return field no longer plans "
+    "zero space heating for a room below its comfort band",
+    _ssg_warm[1] > 1.0,
+    f"planned {_ssg_warm[1]:.3f} kWh, slab {[round(s, 2) for s in _ssg_warm[0]]}",
+)
+R.check(
+    "and a refused reading leaves the slab to the model exactly as an install "
+    "with no floor-return sensor does",
+    _ssg_warm[0] == _ssg_none[0] and _ssg_warm[1] == _ssg_none[1],
+    f"refused {_ssg_warm[0]} {_ssg_warm[1]} / unconfigured {_ssg_none[0]} {_ssg_none[1]}",
+)
+R.check(
+    "and a repair issue names the sensor and the bound",
+    _ssg_warm[2].get(_ssg.ISSUE_FLOOR_RETURN_IMPLAUSIBLE, {}).get(
+        "translation_placeholders", {}).get("entity") == "sensor.ret"
+    and _ssg_warm[2][_ssg.ISSUE_FLOOR_RETURN_IMPLAUSIBLE][
+        "translation_placeholders"]["bound"] == "12",
+    f"{sorted(_ssg_warm[2])}",
+)
+# Null control: a plausible floor-loop reading (6.4 K above the room) still
+# seeds the slab unchanged, converging on the merge's return + 1 K fixed point,
+# raises nothing, and plans heat as before.
+R.check(
+    "null control: a plausible floor-loop return still seeds the slab, to the "
+    "return + 1 K fixed point, and raises no repair",
+    abs(_ssg_ok[0][-1] - 27.0) < 0.05 and _ssg_ok[0] != _ssg_none[0]
+    and _ssg.ISSUE_FLOOR_RETURN_IMPLAUSIBLE not in _ssg_ok[2],
+    f"slab {[round(s, 2) for s in _ssg_ok[0]]}, issues {sorted(_ssg_ok[2])}",
+)
+# A plausible reading during a hot-water run or a defrost is the pump's own
+# circuit water, not the floor's: it seeds nothing, and raises nothing.
+_ssg_dhw = _ssg_cycles(26.0, mode="DHW (Hot Water)")
+_ssg_dhw_none = _ssg_cycles(None, mode="DHW (Hot Water)")
+_ssg_frost = _ssg_cycles(26.0, defrost="on")
+_ssg_frost_none = _ssg_cycles(None, defrost="on")
+_ssg_both = _ssg_cycles(26.0, mode="Heating + DHW", defrost="off")
+R.check(
+    "a hot-water-only run does not seed the slab from the return",
+    _ssg_dhw[0] == _ssg_dhw_none[0]
+    and _ssg.ISSUE_FLOOR_RETURN_IMPLAUSIBLE not in _ssg_dhw[2],
+    f"{_ssg_dhw[0]} vs {_ssg_dhw_none[0]}",
+)
+R.check(
+    "nor does a defrost",
+    _ssg_frost[0] == _ssg_frost_none[0],
+    f"{_ssg_frost[0]} vs {_ssg_frost_none[0]}",
+)
+R.check(
+    "control: a heating mode with the defrost flag off seeds as with no signals",
+    _ssg_both[0] == _ssg_ok[0],
+    f"{_ssg_both[0]} vs {_ssg_ok[0]}",
+)
+# The bound at its edge, through the production predicate.
+R.check(
+    "the bound: 12 K above the room is a floor loop, anything warmer is not",
+    not _ssg.above_room(32.0, 20.0) and _ssg.above_room(32.1, 20.0)
+    and _ssg.SLAB_SEED_MAX_ABOVE_ROOM_K == 12.0,
+)
+# The option text states the bound the code applies, in every language.
+import json as _ssg_json  # noqa: E402
+from pathlib import Path as _ssg_Path  # noqa: E402
+
+_ssg_cc = _ssg_Path(_ssg.__file__).parent
+
+
+def _ssg_find(node):
+    """Every ``data_description`` text for the floor-return field, at any depth."""
+    if isinstance(node, dict):
+        text = (node.get("data_description") or {}).get("floor_return_temp_entity")
+        return ([text] if text else []) + [t for v in node.values() for t in _ssg_find(v)]
+    return []
+
+
+_ssg_texts = [
+    t for name in ("strings.json", "translations/en.json", "translations/de.json",
+                   "translations/sv.json")
+    for t in _ssg_find(_ssg_json.loads((_ssg_cc / name).read_text(encoding="utf-8")))
+]
+R.check(
+    "every floor-return option text names the bound the guard applies",
+    len(_ssg_texts) == 12
+    and all(f"{_ssg.SLAB_SEED_MAX_ABOVE_ROOM_K:g} K" in t for t in _ssg_texts),
+    f"{len(_ssg_texts)} texts",
+)
+
+
 
 # --- R10-START-COUNTER-EDGES: the start counter fed from running-signal edges ---
 # Part D of Bankaifan's outside pull request 3420, on the approved design
diff --git a/tests/golden/card_claimed_drift.txt b/tests/golden/card_claimed_drift.txt
index c2c3383491..8cf567f51b 100644
--- a/tests/golden/card_claimed_drift.txt
+++ b/tests/golden/card_claimed_drift.txt
@@ -19,9 +19,9 @@
 #
 # The state names are the ones `node tests/card_drift.mjs --list` prints.
 #
-# claims-for: 10.0.1
+# claims-for: 10.0.2
 #
-# v10.0.1: Compressor starts counted from running-signal edges; COP learner draw floor. The stamp empties the list; the
+# v10.0.2: card applies a plan only up to the manual-plan window; implausible floor-return readings no longer seed the slab. The stamp empties the list; the
 # next branch restates its own footprint, claims included.
 #
 
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index 7c3e125ce9..b4a0d77201 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -62,9 +62,9 @@
 # about one release's diff, it does not expire with the stamp and is not part
 # of the inherited-claims comparison.
 #
-# claims-for: 10.0.1
+# claims-for: 10.0.2
 #
-# v10.0.1: Compressor starts counted from running-signal edges; COP learner draw floor. The stamp empties the list; the
+# v10.0.2: card applies a plan only up to the manual-plan window; implausible floor-return readings no longer seed the slab. The stamp empties the list; the
 # next branch restates its own footprint, claims included.
 #
 # may-drift: flat_prices -- #1208 polish-every-candidate, owner ruling #1208 comment 208bed25
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._update_current_state.GUARD_OFF.8398778f.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._update_current_state.GUARD_OFF.8398778f.json
new file mode 100644
index 0000000000..b389f77e16
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._update_current_state.GUARD_OFF.8398778f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._update_current_state GUARD_OFF 8398778f",
+  "killed_by": "tests/features.py",
+  "old": "        if not slab_sensed:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=13."
+}
diff --git a/tests/mutation_ledger/killed_by/slab_seed.py/above_room.CMP_BOUND.adc09d49.json b/tests/mutation_ledger/killed_by/slab_seed.py/above_room.CMP_BOUND.adc09d49.json
new file mode 100644
index 0000000000..c45a2a4346
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/slab_seed.py/above_room.CMP_BOUND.adc09d49.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/slab_seed.py:above_room CMP_BOUND adc09d49",
+  "killed_by": "tests/features.py",
+  "old": "    return return_c - room_c > SLAB_SEED_MAX_ABOVE_ROOM_K",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return return_c - room_c >= SLAB_SEED_MAX_ABOVE_ROOM_K`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/slab_seed.py/above_room.RETURN_DEL.adc09d49.json b/tests/mutation_ledger/killed_by/slab_seed.py/above_room.RETURN_DEL.adc09d49.json
new file mode 100644
index 0000000000..e87b86f36f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/slab_seed.py/above_room.RETURN_DEL.adc09d49.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/slab_seed.py:above_room RETURN_DEL adc09d49",
+  "killed_by": "tests/features.py",
+  "old": "    return return_c - room_c > SLAB_SEED_MAX_ABOVE_ROOM_K",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/slab_seed.py/hot_water_run.RETURN_DEL.fd09c812.json b/tests/mutation_ledger/killed_by/slab_seed.py/hot_water_run.RETURN_DEL.fd09c812.json
new file mode 100644
index 0000000000..d2b6403c41
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/slab_seed.py/hot_water_run.RETURN_DEL.fd09c812.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/slab_seed.py:hot_water_run RETURN_DEL fd09c812",
+  "killed_by": "tests/features.py",
+  "old": "    return bool(signals.mode_observed and mode.dhw and not mode.space_heat)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/slab_seed.py/judge.BOOLOP.72bb8e63.json b/tests/mutation_ledger/killed_by/slab_seed.py/judge.BOOLOP.72bb8e63.json
new file mode 100644
index 0000000000..50d260e1b0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/slab_seed.py/judge.BOOLOP.72bb8e63.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/slab_seed.py:judge BOOLOP 72bb8e63",
+  "killed_by": "tests/solar_alignment.py",
+  "old": "    high = value is not None and above_room(value, room_c)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`high = value is not None or above_room(value, room_c)`) took tests/solar_alignment.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/slab_seed.py/judge.BOOLOP.84552d11.json b/tests/mutation_ledger/killed_by/slab_seed.py/judge.BOOLOP.84552d11.json
new file mode 100644
index 0000000000..d69760494f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/slab_seed.py/judge.BOOLOP.84552d11.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/slab_seed.py:judge BOOLOP 84552d11",
+  "killed_by": "tests/solar_alignment.py",
+  "old": "    return value is not None and refusal(value, room_c, signals) is None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return value is not None or refusal(value, room_c, signals) is None`) took tests/solar_alignment.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/slab_seed.py/judge.RETURN_DEL.84552d11.json b/tests/mutation_ledger/killed_by/slab_seed.py/judge.RETURN_DEL.84552d11.json
new file mode 100644
index 0000000000..62da138f8b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/slab_seed.py/judge.RETURN_DEL.84552d11.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/slab_seed.py:judge RETURN_DEL 84552d11",
+  "killed_by": "tests/features.py",
+  "old": "    return value is not None and refusal(value, room_c, signals) is None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/slab_seed.py/refusal.GUARD_OFF.53661e5e.json b/tests/mutation_ledger/killed_by/slab_seed.py/refusal.GUARD_OFF.53661e5e.json
new file mode 100644
index 0000000000..2b27a83def
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/slab_seed.py/refusal.GUARD_OFF.53661e5e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/slab_seed.py:refusal GUARD_OFF 53661e5e",
+  "killed_by": "tests/features.py",
+  "old": "    if above_room(return_c, room_c):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/slab_seed.py/refusal.GUARD_OFF.5b119bcb.json b/tests/mutation_ledger/killed_by/slab_seed.py/refusal.GUARD_OFF.5b119bcb.json
new file mode 100644
index 0000000000..62f82be5ef
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/slab_seed.py/refusal.GUARD_OFF.5b119bcb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/slab_seed.py:refusal GUARD_OFF 5b119bcb",
+  "killed_by": "tests/features.py",
+  "old": "    if hot_water_run(signals):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/slab_seed.py/refusal.GUARD_OFF.bf3858a0.json b/tests/mutation_ledger/killed_by/slab_seed.py/refusal.GUARD_OFF.bf3858a0.json
new file mode 100644
index 0000000000..d8b1bf2d9c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/slab_seed.py/refusal.GUARD_OFF.bf3858a0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/slab_seed.py:refusal GUARD_OFF bf3858a0",
+  "killed_by": "tests/features.py",
+  "old": "    if defrost_interval(signals.defrosting):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/slab_seed.py/seed.BOOLOP.01a5b253.json b/tests/mutation_ledger/killed_by/slab_seed.py/seed.BOOLOP.01a5b253.json
new file mode 100644
index 0000000000..630546ff3f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/slab_seed.py/seed.BOOLOP.01a5b253.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/slab_seed.py:seed BOOLOP 01a5b253",
+  "killed_by": "tests/features.py",
+  "old": "    if return_c is not None and refusal(return_c, state.room_temperature, signals) is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if return_c is not None or refusal(return_c, state.room_temperature, signals) is None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/slab_seed.py/seed.GUARD_OFF.01a5b253.json b/tests/mutation_ledger/killed_by/slab_seed.py/seed.GUARD_OFF.01a5b253.json
new file mode 100644
index 0000000000..bc9b15574b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/slab_seed.py/seed.GUARD_OFF.01a5b253.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/slab_seed.py:seed GUARD_OFF 01a5b253",
+  "killed_by": "tests/features.py",
+  "old": "    if return_c is not None and refusal(return_c, state.room_temperature, signals) is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/survivor_triage/slab_seed.py/refusal.RETURN_DEL.da9e8e97.json b/tests/mutation_ledger/survivor_triage/slab_seed.py/refusal.RETURN_DEL.da9e8e97.json
new file mode 100644
index 0000000000..ddd8024ada
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/slab_seed.py/refusal.RETURN_DEL.da9e8e97.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/slab_seed.py:refusal RETURN_DEL da9e8e97",
+  "old": "    return None",
+  "reason": "Equivalent (RETURN_DEL, `return None` -> `pass`): the statement is the last one in refusal, after three `if` arms that each return, so deleting it lets the function fall off its own end and return None -- the same value, on every input, to every reader. Measured by the #3616 fixer's mutant drive (tools/audit/seat/mutant_run.py --diff over the diff's 27 drafted custom_components mutants) against the '# --- #3616: an implausible slab seed' block of tests/features.py, whose null control pins the None arm (a plausible floor-loop return still seeds the slab): SURVIVED alone, every other drafted mutant killed.",
+  "verdict": "equivalent"
+}
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index b331a364fe..9e37583b07 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -121,7 +121,8 @@ standing-seat liveness step keep the seats alive.
 - [`state_docs.py`](instruments/state_docs.py.md) — one call regenerates the four state docs (`plan_table.py`, `merge_throughput.py flow`, `resume_doc.py`, `handover_prompt.py`), commits exactly their outputs to the orphan ref `handoff/audit-r<N>-plan` at `handoff/round<N>/state/`, N the roster's round
 - [`plan_public.py`](instruments/plan_public.py.md) — stages the ongoing round's plan page from the newest state ref for the public site, refusing a page that would publish a host path or a tool's attribution
 - [`bottleneck_check.py`](instruments/bottleneck_check.py.md) — prints one `BOTTLENECK:` line per flow metric past the owner's threshold, with a suggested action the orchestrator decides on, and nothing when none is
-- [`scorecard.py`](instruments/scorecard.py.md) — ten report-only convergence lines (gate and run health, first-verdict yield, machinery blocks, train skips, hotfix share, size, escapes, detection delay, seat cost), each but the hotfix naming measure held to a null control, written daily to `S/beatd/scorecard.txt`
+- [`scorecard.py`](instruments/scorecard.py.md) — report-only convergence lines (gate and run health, first-verdict yield, machinery blocks, train skips, hotfix share, size, escapes, detection delay, seat cost, and round_metrics.py's reads over the open round), each but the hotfix naming measure held to a null control, written daily to `S/beatd/scorecard.txt`
+- [`round_metrics.py`](instruments/round_metrics.py.md) — decision 0018's flow reads per round and per week (merges by class, lead_time from the roster-entry commit per class, product_green with the gate's check count, restore, runner seconds and tokens per merge), unread on no input, and the producer of the scorecard's inputs
 - [`toolchain.py`](instruments/toolchain.py.md) — the stable tools ref `toolchain/stable`: `behind` counts what the ref holds over a checkout on the seat paths, `promote` moves it along main to the newest commit whose push run reads MACHINERY green, and prints `PROMOTE-HELD` when the newest three past it do not
 - [`plant_recall.py`](instruments/plant_recall.py.md) — plants a held-out seat's objective bugs into the baseline export before the finders, refusing an unsound plant list, and counts recall after the judge (found / planted, whole, per space and per kind), unread on no input
 - [`finder_overlap.py`](instruments/finder_overlap.py.md) — seats a twin finder on one scopes.json seat's universe and estimates the bugs there from the two seats' judged-real overlap, with both models, unread on no input
diff --git a/tools/audit/seat/beat_jobs.py b/tools/audit/seat/beat_jobs.py
index 8c6c5374c4..fe64a76a7c 100644
--- a/tools/audit/seat/beat_jobs.py
+++ b/tools/audit/seat/beat_jobs.py
@@ -135,10 +135,14 @@ ROWS (the job table's `interval_s` in brackets):
                      owner's thresholds, 2026-11-07); a held breach re-prints its
                      first line, so it is new once per trip. A line suggests; the
                      orchestrator decides. `bottleneck: UNREADABLE` on a non-zero rc.
-  scorecard [86400]  scorecard.py `report --dir S/scorecard --train-log <train_log>
+  scorecard [86400]  round_metrics.py `produce --dir S/scorecard --repo <checkout>
+                     --gh-repo <repo>` refreshes the inputs (one REST batch), then
+                     scorecard.py `report --dir S/scorecard --train-log <train_log>
                      [--sweep-record <sweep_record>]` into `S/beatd/scorecard.txt`
-                     (ten report-only lines, none a gate); the digest hears only
-                     `scorecard: UNREADABLE rc=<n>` when the instrument fails.
+                     (report-only lines, none a gate); the digest hears only
+                     `scorecard: UNREADABLE produce rc=<n>` (the report then does not
+                     run, so scorecard.txt keeps its last dated read) or
+                     `scorecard: UNREADABLE rc=<n>` when an instrument fails.
   toolchain-promote [600] toolchain.py `promote --repo <repo> --dir <checkout>`: moves the
                      stable tools ref `toolchain/stable` along main to the newest commit
                      whose push run reads MACHINERY green, and keeps the instrument's
@@ -146,6 +150,11 @@ ROWS (the job table's `interval_s` in brackets):
                      leaves the digest empty; `PROMOTE-HELD` (the newest three concluded
                      main runs past the ref machinery red or unread) is the row's line, and
                      a refusal or failed read is `toolchain-promote: rc=<n>: <why>`.
+  ci-attempt [1800]  one `gh api` read of ci.yml's newest 100 runs: `CI-ATTEMPT: run
+                     <id> at attempt >= CI_ATTEMPT_ALARM on <branch> (#<pr>)` per run
+                     re-attempted that often (R10-RCA-SWEEP-SETTLE-LOOP countermeasure
+                     B: 1089 bot re-attempts on 11-08 were seen about 16 h late); a
+                     run below it is silent; `ci-attempt: UNREADABLE gh rc=<n>`.
 No row runs `git checkout`, `reset`, `pull` or `merge`; main is read as
 `git -C <repo> cat-file -e origin/main:<path>`. No row touches a seat's alive
 file. Every row exits 0 once its lines are written: the digest is the signal,
@@ -169,7 +178,7 @@ from pathlib import Path
 
 ROWS = ("tick-digest", "owed-check", "roster-drain", "plan-beat", "gantt", "verdict-audit", "pulse",
         "cancel-sweep", "disk", "opener", "loop-cwd", "head-watch", "audit-dispatch", "outside-intake", "bottleneck",
-        "scorecard", "toolchain-promote", "darwin-selftest")
+        "scorecard", "ci-attempt", "toolchain-promote", "darwin-selftest")
 HOLD_STALE_S = 24 * 3600  # gap 6: a hold line never expired
 #: roster-drain starts no op past this many seconds into a pass; the rest wait for the next pass. At
 #: most half the row's timeout_s in beatd.jobs.json (the self-test pins it), so an op started just
@@ -698,10 +707,15 @@ def bottleneck(ctx: Ctx) -> None:
 
 
 def scorecard(ctx: Ctx) -> None:
-    """scorecard.py report into S/beatd/scorecard.txt; report-only, so the digest hears only of a failed run."""
-    got = ctx.need("scorecard", "train_log")
+    """round_metrics.py produce, then scorecard.py report into S/beatd/scorecard.txt; report-only,
+    so the digest hears only of a failed run."""
+    got = ctx.need("scorecard", "train_log", "repo")
     if got is None:
         return
+    rc, _, err = ctx.py("tools/audit/seat/round_metrics.py", "produce", "--dir", str(ctx.state / "scorecard"),
+                        "--repo", str(ctx.repo), "--gh-repo", got[1])
+    if rc != 0:
+        return write_job(ctx, "scorecard", [f"scorecard: UNREADABLE produce rc={rc}: {(err.strip().splitlines() or [''])[-1]}"])
     args = ["report", "--dir", str(ctx.state / "scorecard"), "--train-log", got[0], "--repo", str(ctx.repo)]
     if ctx.overlay.get("sweep_record"):
         args += ["--sweep-record", str(ctx.overlay["sweep_record"])]
@@ -726,6 +740,30 @@ def toolchain_promote(ctx: Ctx) -> None:
     write_job(ctx, "toolchain-promote", held)
 
 
+#: ci-attempt flags a run at this attempt or more; gate.py's ATTEMPT_CAP (45) is where the hooks stop.
+CI_ATTEMPT_ALARM = 20
+CI_RUN = re.compile(r"(\d+) (\d+) (\S+) ?([\d,]*)")
+
+
+def ci_attempt(ctx: Ctx) -> None:
+    """One line per ci.yml run at attempt CI_ATTEMPT_ALARM or more among the newest 100, named with its PR."""
+    got = ctx.need("ci-attempt", "repo")
+    if got is None:
+        return
+    rc, out, _ = ctx.run(["gh", "api", f"repos/{got[0]}/actions/workflows/ci.yml/runs?per_page=100", "--jq",
+                          '.workflow_runs[] | "\\(.id) \\(.run_attempt) \\(.head_branch) \\([.pull_requests[].number] | join(","))"'],
+                         ctx.repo, ctx.env)
+    if rc != 0:
+        return write_job(ctx, "ci-attempt", [f"ci-attempt: UNREADABLE gh rc={rc}"])
+    lines = []
+    for ln in out.splitlines():
+        m = CI_RUN.fullmatch(ln.strip())
+        if m and int(m[2]) >= CI_ATTEMPT_ALARM:
+            prs = " ".join(f"#{n}" for n in m[4].split(",") if n) or "no pull request"
+            lines.append(f"CI-ATTEMPT: run {m[1]} at attempt >= {CI_ATTEMPT_ALARM} on {m[3]} ({prs})")
+    write_job(ctx, "ci-attempt", lines)
+
+
 DARWIN_SEAT = "audit/seat/"
 DARWIN_LEASE_LABEL = "darwin-selftest"
 #: darwin-selftest starts no self-test past this many seconds into a pass and gives the heavy slot back;
@@ -804,7 +842,7 @@ def darwin_selftest(ctx: Ctx) -> None:
 RUN = {"tick-digest": tick_digest, "owed-check": owed_check, "roster-drain": roster_drain,
        "plan-beat": plan_beat, "gantt": gantt, "verdict-audit": verdict_audit, "pulse": pulse, "cancel-sweep": cancel_sweep, "disk": disk,
        "opener": opener, "loop-cwd": loop_cwd, "head-watch": head_watch, "audit-dispatch": audit_dispatch,
-       "outside-intake": outside_intake, "bottleneck": bottleneck, "scorecard": scorecard,
+       "outside-intake": outside_intake, "bottleneck": bottleneck, "scorecard": scorecard, "ci-attempt": ci_attempt,
        "toolchain-promote": toolchain_promote, "darwin-selftest": darwin_selftest}
 
 
diff --git a/tools/audit/seat/beat_jobs_selftest.py b/tools/audit/seat/beat_jobs_selftest.py
index 1e36ec7d8a..d434391980 100644
--- a/tools/audit/seat/beat_jobs_selftest.py
+++ b/tools/audit/seat/beat_jobs_selftest.py
@@ -489,7 +489,14 @@ def cases(bj) -> dict[str, bool]:
     res["plan-beat: state_docs is handed the overlay's train_log (null: none leaves the flag out)"] = (
         arg(sd, "--train-log") == str(c.state / "train.log") and sd0 and "--train-log" not in sd0)
 
-    # bottleneck
+    # bottleneck: the live merge-wait value survives the digest's norm() (the a7 row's "the digest
+    # line equals the live value"), driven by bottleneck_check's own line, never a copy of it
+    import bottleneck_check as bk
+    live = bk.judge(bk._fixture(merge_wait=(([{"pr": 1, "hours": 4.2}] * 3, 0), "")))
+    c, f = fresh(answers={"bottleneck_check.py": (0, "\n".join(live) + "\n", "")})
+    bj.bottleneck(c)
+    res["bottleneck: a merge-wait line keeps its live hours through the digest"] = (
+        len(live) == 1 and "merge-wait 4.2 hours median" in digest(c))
     c, f = fresh(answers={"bottleneck_check.py": (0, "", "")})
     bj.bottleneck(c)
     bc = next((x for x in f.calls if any(a.endswith("bottleneck_check.py") for a in x)), [])
@@ -538,6 +545,41 @@ def cases(bj) -> dict[str, bool]:
     bj.scorecard(c)
     res["scorecard: an overlay without train_log is UNREADABLE and runs nothing"] = (
         digest(c) == "scorecard: UNREADABLE overlay lacks train_log\n" and f.ran("scorecard.py") == 0)
+    c, f = fresh(answers={"scorecard.py": (0, sc_out, "")})
+    bj.scorecard(c)
+    pr = next((x for x in f.calls if any(a.endswith("round_metrics.py") for a in x)), [])
+    res["scorecard: the producer runs first, handed produce, the dir, the checkout and the overlay's repo"] = (
+        f.calls and f.calls[0] == pr and "produce" in pr and arg(pr, "--dir") == str(c.state / "scorecard")
+        and arg(pr, "--repo") == str(c.repo) and arg(pr, "--gh-repo") == "o/r")
+    c, f = fresh(answers={"round_metrics.py": (1, "", "Traceback\nApiError: 502\n"), "scorecard.py": (0, sc_out, "")})
+    bj.scorecard(c)
+    res["scorecard: a failed producer is UNREADABLE and the report does not run on stale inputs"] = (
+        digest(c) == "scorecard: UNREADABLE produce rc=1: ApiError: 502\n" and f.ran("scorecard.py") == 0
+        and not (c.state / "beatd" / "scorecard.txt").exists())
+
+    # ci-attempt: the #3287 window (dev/audit/rca/R10-RCA-SWEEP-SETTLE-LOOP.md: PR #3319's code run
+    # 42469369199 reached attempt 44 and its edit run 42469369682 alternated with it)
+    loop = "42469369199 44 fix/r10-x 3319\n42469369682 43 fix/r10-x 3319\n42469300000 1 main \n"
+    c, f = fresh(answers={"gh": (0, loop, "")})
+    bj.ci_attempt(c)
+    res["ci-attempt: the #3287 window fires once per looping run, naming it and its pull request"] = (
+        digest(c) == "CI-ATTEMPT: run 42469369199 at attempt >= 20 on fix/r10-x (#3319)\n"
+                     "CI-ATTEMPT: run 42469369682 at attempt >= 20 on fix/r10-x (#3319)\n"
+        and len(f.calls) == 1 and "repos/o/r/actions/workflows/ci.yml/runs?per_page=100" in f.calls[0])
+    c, _ = fresh(answers={"gh": (0, "1 1 main \n2 19 fix/y 7\n", "")})
+    bj.ci_attempt(c)
+    res["ci-attempt null: runs at attempt 1 and 19 are silent"] = not digest(c)
+    c, _ = fresh(answers={"gh": (0, "3 20 main \n", "")})
+    bj.ci_attempt(c)
+    res["ci-attempt: attempt 20 exactly fires; a run with no pull request says so"] = (
+        digest(c) == "CI-ATTEMPT: run 3 at attempt >= 20 on main (no pull request)\n")
+    c, _ = fresh(answers={"gh": (1, "", "boom")})
+    bj.ci_attempt(c)
+    res["ci-attempt: an unreadable API is UNREADABLE"] = digest(c) == "ci-attempt: UNREADABLE gh rc=1\n"
+    c, f = fresh(overlay={"train_log": "/x"}, answers={"gh": (0, loop, "")})
+    bj.ci_attempt(c)
+    res["ci-attempt: an overlay without repo is UNREADABLE and calls no API"] = (
+        digest(c) == "ci-attempt: UNREADABLE overlay lacks repo\n" and not f.calls)
 
     # toolchain-promote
     moved = "PROMOTE 2026-11-15T10:00:00Z aaaaaaaaaaaa -> bbbbbbbbbbbb run=7\n"
@@ -1221,6 +1263,15 @@ MUTANTS = {
     "bottleneck_unreadable_dropped": ('ln.startswith(("BOTTLENECK: ", "BOTTLENECK-UNREADABLE: "))',
                                       'ln.startswith(("BOTTLENECK: ",))',
                                       "bottleneck: each BOTTLENECK and BOTTLENECK-UNREADABLE line reaches the digest, nothing else"),
+    "ci_attempt_cmp": ("int(m[2]) >= CI_ATTEMPT_ALARM", "int(m[2]) > CI_ATTEMPT_ALARM",
+                       "ci-attempt: attempt 20 exactly fires; a run with no pull request says so"),
+    "ci_attempt_off": ("if m and int(m[2])", "if m and 0 * int(m[2])",
+                       "ci-attempt: the #3287 window fires once per looping run, naming it and its pull request"),
+    "ci_attempt_pr": ('or "no pull request"', 'and "no pull request"',
+                      "ci-attempt: the #3287 window fires once per looping run, naming it and its pull request"),
+    "scorecard_produce_rc": ('        return write_job(ctx, "scorecard", [f"scorecard: UNREADABLE produce rc=',
+                             '        pass  # write_job(ctx, "scorecard", [f"scorecard: UNREADABLE produce rc=',
+                             "scorecard: a failed producer is UNREADABLE and the report does not run on stale inputs"),
     "scorecard_rc_clean": ('    if rc != 0 or not out.strip():\n        return write_job(ctx, "scorecard"',
                            '    if not out.strip():\n        return write_job(ctx, "scorecard"',
                            "scorecard: a failed instrument is UNREADABLE, never written"),
diff --git a/tools/audit/seat/beatd.jobs.json b/tools/audit/seat/beatd.jobs.json
index 6c3a6237dc..11ae415e14 100644
--- a/tools/audit/seat/beatd.jobs.json
+++ b/tools/audit/seat/beatd.jobs.json
@@ -310,9 +310,31 @@
       ],
       "cwd": "orch",
       "interval_s": 86400,
-      "timeout_s": 600,
+      "timeout_s": 1800,
       "heartbeat_s": null,
-      "env_pass": [],
+      "env_pass": [
+        "GH_TOKEN"
+      ],
+      "class": null,
+      "kind": "periodic"
+    },
+    {
+      "name": "ci-attempt",
+      "argv": [
+        "python3",
+        "-I",
+        "tools/audit/seat/beat_jobs.py",
+        "ci-attempt",
+        "--state",
+        "$S"
+      ],
+      "cwd": "orch",
+      "interval_s": 1800,
+      "timeout_s": 120,
+      "heartbeat_s": null,
+      "env_pass": [
+        "GH_TOKEN"
+      ],
       "class": null,
       "kind": "periodic"
     },
diff --git a/tools/audit/seat/bottleneck_check.py b/tools/audit/seat/bottleneck_check.py
index 5a86348cb1..580ce4dc14 100644
--- a/tools/audit/seat/bottleneck_check.py
+++ b/tools/audit/seat/bottleneck_check.py
@@ -33,8 +33,15 @@ smallest sample that may trip it, so that one verdict or one merge never fires:
 
 --memory PATH (the beat row's form): a metric that stays past its threshold
 re-prints the line it first printed, verbatim, so the digest's fold sees no
-new line and the wake fires once per trip; a metric back inside its threshold
-is forgotten, and its next trip prints afresh. The memory is keyed by the
+new line and the wake fires once per trip -- unless its live value is more
+than a quarter worse (WORSE) than the value that first line printed: then the
+live line prints, so the digest never shows a stale value that hides a
+worsening metric (owner ruling 2026-11-13, card P8; the process convergence
+audit's row a7, where "merge-wait 2.1 h" re-printed while it stood at 4.2 h).
+The first line stays the reference, so a held breach prints the live line on
+every beat it is past WORSE, and its first line again once it is not. Lower
+is worse for yield and throughput, higher for the rest. A metric back inside
+its threshold is forgotten, and its next trip prints afresh. The memory is keyed by the
 line's kind and metric, so a breach after an UNREADABLE beat for the same
 metric (or the reverse) is a new trip and prints.
 
@@ -65,12 +72,35 @@ THRESHOLDS = {
     "block-class": (0.30, 5),
 }
 SKIP_BATCHES = 2
+#: A held breach prints its live line once its value is worse than the first printed one by more than this share.
+WORSE = 0.25
+LOWER_IS_WORSE = {"yield", "throughput"}
+
+
+class Line(str):
+    """A breach line carrying the value it printed (None on an UNREADABLE line)."""
+    value: float | None = None
+
+
+def _line(text: str, value: float) -> Line:
+    ln = Line(text)
+    ln.value = value
+    return ln
 
 
 def _unread(metric: str, why: str) -> str:
     return f"BOTTLENECK-UNREADABLE: {metric} -- {why}"
 
 
+def worse(metric: str, first: float | None, live: float | None) -> bool:
+    """Whether `live` is worse than `first` by more than WORSE, in the metric's own direction."""
+    if first is None or live is None:
+        return False
+    if metric in LOWER_IS_WORSE:
+        return live < first * (1 - WORSE)
+    return live > first * (1 + WORSE)
+
+
 def judge(m: dict) -> list[str]:
     """The breach lines for one metrics dict (`bottleneck_metrics`' shape)."""
     out: list[str] = []
@@ -82,9 +112,9 @@ def judge(m: dict) -> list[str]:
         merged, judged = v
         lim, n = THRESHOLDS["yield"]
         if judged >= n and merged / judged < lim:
-            out.append(f"BOTTLENECK: yield {merged / judged:.2f} ({merged}/{judged} first passes, 24 h) "
-                       f"vs {lim} -- read the blocked-class mix; brief its top class into the "
-                       "open fixers' briefs or a prepr check before dispatching more")
+            out.append(_line(f"BOTTLENECK: yield {merged / judged:.2f} ({merged}/{judged} first passes, 24 h) "
+                             f"vs {lim} -- read the blocked-class mix; brief its top class into the "
+                             "open fixers' briefs or a prepr check before dispatching more", merged / judged))
 
     v, why = m["batches"]
     if v is None:
@@ -96,10 +126,11 @@ def judge(m: dict) -> list[str]:
         lim, n = THRESHOLDS["skip-share"]
         if entries >= n and len(skips) / entries > lim:
             top, k = Counter(r for _, r in skips).most_common(1)[0]
-            out.append(f"BOTTLENECK: skip-share {len(skips) / entries:.0%} ({len(skips)}/{entries}, "
-                       f"batches {' '.join(b['tag'] for b in done)}) vs {lim:.0%} -- {k} of "
-                       f"{len(skips)} are '{top}': re-add a skipped head only once classify "
-                       "reads GREEN, and hold the next launch until the race it names settles")
+            out.append(_line(f"BOTTLENECK: skip-share {len(skips) / entries:.0%} ({len(skips)}/{entries}, "
+                             f"batches {' '.join(b['tag'] for b in done)}) vs {lim:.0%} -- {k} of "
+                             f"{len(skips)} are '{top}': re-add a skipped head only once classify "
+                             "reads GREEN, and hold the next launch until the race it names settles",
+                             len(skips) / entries))
 
     v, why = m["merge_wait"]
     if v is None:
@@ -111,10 +142,12 @@ def judge(m: dict) -> list[str]:
             med = statistics.median(r["hours"] for r in rows)
             if med > lim:
                 worst = max(rows, key=lambda r: r["hours"])
-                out.append(f"BOTTLENECK: merge-wait {med:.1f} h median ({len(rows)} PRs, 24 h; worst "
-                           f"#{worst['pr']} {worst['hours']:.1f} h) vs {lim:g} h -- the merge stage "
-                           "is the constraint: check the train is live and every verdicted head "
-                           "is queued before dispatching review or fix work")
+                # "hours", never "h": the digest's norm() reads "<n> h" as an age and blanks it,
+                # which would hide the live value this line exists to show.
+                out.append(_line(f"BOTTLENECK: merge-wait {med:.1f} hours median ({len(rows)} PRs, 24 h; worst "
+                                 f"#{worst['pr']} {worst['hours']:.1f} hours) vs {lim:g} hours -- the merge stage "
+                                 "is the constraint: check the train is live and every verdicted head "
+                                 "is queued before dispatching review or fix work", med))
 
     v, why = m["closed"]
     if v is None:
@@ -123,17 +156,17 @@ def judge(m: dict) -> list[str]:
         lim, _ = THRESHOLDS["throughput"]
         rate, want = round(v / 6.0, 6), round(lim * m["takt"], 6)
         if rate < want:
-            out.append(f"BOTTLENECK: throughput {rate:.2f}/h ({v} groups closed, 6 h) vs "
-                       f"{want:.2f}/h (0.7 x takt {m['takt']:g}) -- find the stage holding the "
-                       "work (merge-wait, skip-share, yield above) and drain it before "
-                       "dispatching new groups")
+            out.append(_line(f"BOTTLENECK: throughput {rate:.2f}/h ({v} groups closed, 6 h) vs "
+                             f"{want:.2f}/h (0.7 x takt {m['takt']:g}) -- find the stage holding the "
+                             "work (merge-wait, skip-share, yield above) and drain it before "
+                             "dispatching new groups", rate))
 
     v, why = m["wip"]
     if v is None:
         out.append(_unread("wip", why))
     elif len(v) >= m["wip_cap"]:
-        out.append(f"BOTTLENECK: wip {len(v)} in-progress vs cap {m['wip_cap']} -- dispatch no new "
-                   "group; move review and merge work first")
+        out.append(_line(f"BOTTLENECK: wip {len(v)} in-progress vs cap {m['wip_cap']} -- dispatch no new "
+                         "group; move review and merge work first", len(v)))
 
     v, why = m["classes"]
     if v is None:
@@ -144,9 +177,9 @@ def judge(m: dict) -> list[str]:
         if total >= n:
             top, k = v.most_common(1)[0]
             if k / total > lim:
-                out.append(f"BOTTLENECK: block-class {top or 'unclassed'} {k / total:.0%} ({k}/{total} "
-                           f"blocks, 24 h) vs {lim:.0%} -- a recurring class owes a root-cause seat "
-                           "(defect-root-cause.md) or a check that catches it before review")
+                out.append(_line(f"BOTTLENECK: block-class {top or 'unclassed'} {k / total:.0%} ({k}/{total} "
+                                 f"blocks, 24 h) vs {lim:.0%} -- a recurring class owes a root-cause seat "
+                                 "(defect-root-cause.md) or a check that catches it before review", k / total))
     return out
 
 
@@ -162,18 +195,27 @@ def state_of(line: str) -> str:
 
 
 def remembered(lines: list[str], memory: Path | None) -> list[str]:
-    """`lines` with each still-tripped state's FIRST line kept verbatim, and
-    the memory rewritten: tripped states only, so a recovery forgets."""
+    """`lines` with each still-tripped state's FIRST line kept verbatim unless
+    the live value is past WORSE of it, and the memory rewritten: tripped states
+    only, so a recovery forgets. A memory entry written before values were kept
+    (a bare line) has no value, so it is kept verbatim until the trip ends."""
     if memory is None:
         return lines
     try:
         old = json.loads(memory.read_text(encoding="utf-8"))
     except (OSError, ValueError):
         old = {}
-    now = {state_of(ln): old.get(state_of(ln), ln) for ln in lines}
+    now, out = {}, []
+    for ln in lines:
+        first = old.get(state_of(ln))
+        if isinstance(first, str):
+            first = {"line": first, "value": None}
+        live = {"line": str(ln), "value": getattr(ln, "value", None)}
+        now[state_of(ln)] = first = first or live
+        out.append(live["line"] if worse(metric_of(ln), first["value"], live["value"]) else first["line"])
     memory.parent.mkdir(parents=True, exist_ok=True)
     memory.write_text(json.dumps(now, indent=1, sort_keys=True) + "\n", encoding="utf-8")
-    return [now[state_of(ln)] for ln in lines]
+    return out
 
 
 def live_metrics(checkout: Path, roster_ref: str | None, train_log: Path | None,
@@ -283,9 +325,36 @@ def self_test(mutate: str | None = None) -> int:
     with tempfile.TemporaryDirectory() as d:
         mem = Path(d) / "mem.json"
         first = remembered(judge(_fixture(closed=(4, ""))), mem)
-        again = remembered(judge(_fixture(closed=(3, ""))), mem)
+        again = remembered(judge(_fixture(closed=(3.5, ""))), mem)
         check("memory: a still-tripped metric re-prints its first line verbatim",
               again == first and "4 groups" in first[0], (first, again))
+        live = remembered(judge(_fixture(closed=(2, ""))), mem)
+        check("memory: a held breach more than a quarter worse prints the live line",
+              live == judge(_fixture(closed=(2, ""))) and "2 groups" in live[0], live)
+        back = remembered(judge(_fixture(closed=(3.5, ""))), mem)
+        check("memory: the first line stays the reference; back inside the quarter it prints again",
+              back == first, back)
+        mem.unlink()
+        wait = lambda h: {"merge_wait": (([{"pr": 1, "hours": h}] * 3, 0), "")}
+        first = remembered(judge(_fixture(**wait(2.4))), mem)
+        edge = remembered(judge(_fixture(**wait(3.0))), mem)
+        check("memory: exactly a quarter worse is not past it (null control)", edge == first, edge)
+        past = remembered(judge(_fixture(**wait(3.1))), mem)
+        check("memory: higher is worse for merge-wait; past the quarter prints live",
+              past and "3.1 hours median" in past[0], past)
+        mem.unlink()
+        first = remembered(judge(_fixture(**wait(4.0))), mem)
+        better = remembered(judge(_fixture(**wait(2.5))), mem)
+        check("memory: an improving value is never printed as live", better == first, better)
+        mem.unlink()
+        remembered(judge(_fixture(**{"yield": ((5, 10), "")})), mem)
+        low = remembered(judge(_fixture(**{"yield": ((3, 10), "")})), mem)
+        check("memory: lower is worse for yield; past the quarter prints live",
+              low and low[0].startswith("BOTTLENECK: yield 0.30 "), low)
+        mem.write_text(json.dumps({"BOTTLENECK: throughput": "BOTTLENECK: throughput old line"}))
+        legacy = remembered(judge(_fixture(closed=(1, ""))), mem)
+        check("memory: a bare-line memory from before values were kept stays verbatim",
+              legacy == ["BOTTLENECK: throughput old line"], legacy)
         remembered(judge(_fixture()), mem)
         after = remembered(judge(_fixture(closed=(3, ""))), mem)
         check("memory: a recovery forgets; the next trip prints afresh",
@@ -334,6 +403,17 @@ MEMORY_MUTANTS = (
     ("memory-key-metric", 'return " ".join(line.split()[:2])', "return line.split()[1]"),
     ("memory-key-kind", 'return " ".join(line.split()[:2])', "return line.split()[0]"),
 )
+#: The live-value rule: `worse`'s comparisons and direction, and `remembered`'s reference.
+WORSE_MUTANTS = (
+    ("worse-up-cmp", "return live > first * (1 + WORSE)", "return live >= first * (1 + WORSE)"),
+    ("worse-up-dir", "return live > first * (1 + WORSE)", "return live > first * (1 - WORSE)"),
+    ("worse-down-dir", "return live < first * (1 - WORSE)", "return live > first * (1 + WORSE)"),
+    ("worse-direction-set", "if metric in LOWER_IS_WORSE:", "if False:"),
+)
+REMEMBER_MUTANTS = (
+    ("reference-moves", "now[state_of(ln)] = first = first or live", "now[state_of(ln)] = first = live"),
+    ("live-never", 'out.append(live["line"] if worse(', 'out.append(first["line"] if worse('),
+)
 
 
 def run_mutants() -> int:
@@ -344,7 +424,9 @@ def run_mutants() -> int:
     survived = []
     g = globals()
     for fn, name, frag, repl in ([("judge", *m) for m in MUTANTS]
-                                 + [("state_of", *m) for m in MEMORY_MUTANTS]):
+                                 + [("state_of", *m) for m in MEMORY_MUTANTS]
+                                 + [("worse", *m) for m in WORSE_MUTANTS]
+                                 + [("remembered", *m) for m in REMEMBER_MUTANTS]):
         original = g[fn]
         src = textwrap.dedent(inspect.getsource(original))
         if src.count(frag) != 1:
diff --git a/tools/audit/seat/instruments/beat_jobs.py.md b/tools/audit/seat/instruments/beat_jobs.py.md
index afe9f0fe59..4695f1699f 100644
--- a/tools/audit/seat/instruments/beat_jobs.py.md
+++ b/tools/audit/seat/instruments/beat_jobs.py.md
@@ -21,7 +21,7 @@
   `disk` (`worktree_gc.sh` under the floor), `opener` (one `open_driver.py
   --board` pass, its refusals and `STUCK` forwarded) `head-watch`
   (`HEAD-MOVED` events) and `audit-dispatch` (one `DISPATCH: planted-defect-audit
-  arm=<arm> cut=<span>` line per sustained `would-trip` of a guardrail arm, never twice while the arm stays tripped; a failed run's `UNREADABLE` clears on the next readable run) and `outside-intake` (`outside_intake.py list` from the overlay's `intake_since`, with a cursor under `state/`: its `OUTSIDE` lines) and `bottleneck` (`bottleneck_check.py` with the beat checkout, the overlay's `train_log`, the `plan_slots` cap and `--memory state/bottleneck.json`: its `BOTTLENECK:` and `BOTTLENECK-UNREADABLE:` lines, each new once per trip; a failed run is `bottleneck: UNREADABLE`). `toolchain-promote` (`toolchain.py promote` with the overlay's `repo` and the beat checkout: a promotion of `toolchain/stable` or nothing newer writes nothing, `PROMOTE-HELD` is its line, a refusal or failed read is `toolchain-promote: rc=<n>`; the last answer is kept in `S/beatd/toolchain.txt`). `darwin-selftest` (Darwin hosts only; one cycle per `origin/main` tip runs `prepr.sh --self-test` and the `--self-test` of every `tools/audit/seat` script `selftest_wiring.py` reports as self-testing and wired, with CI's plain `python3`; each pass holds a heavy slot of `tests/gate_lock.py` around a detached worktree it makes and removes, starts no self-test past `DARWIN_PASS_BUDGET_S` and resumes the same tip next pass, because one whole cycle outlasts the row's `timeout_s` on a Mac; a finished cycle writes one `darwin-selftest: RED <instrument> <first FAIL line>` per red, nothing when green; CI runs these on Linux only, so this finds a Darwin-only red after the merge and prevents none; the host's beat is the macOS leg, no paid runner). `plan-beat` hands the overlay's `train_log` to `state_docs.py --train-log`. Each writes only actionable lines to
+  arm=<arm> cut=<span>` line per sustained `would-trip` of a guardrail arm, never twice while the arm stays tripped; a failed run's `UNREADABLE` clears on the next readable run) and `outside-intake` (`outside_intake.py list` from the overlay's `intake_since`, with a cursor under `state/`: its `OUTSIDE` lines) and `bottleneck` (`bottleneck_check.py` with the beat checkout, the overlay's `train_log`, the `plan_slots` cap and `--memory state/bottleneck.json`: its `BOTTLENECK:` and `BOTTLENECK-UNREADABLE:` lines, each new once per trip; a failed run is `bottleneck: UNREADABLE`) and `scorecard` (`round_metrics.py produce`, then `scorecard.py report` into `S/beatd/scorecard.txt`; only a failure reaches the digest) and `ci-attempt` (one `gh api` read of ci.yml's newest 100 runs: a `CI-ATTEMPT: run <id> at attempt >= 20 on <branch> (#<pr>)` line per run re-attempted that often, R10-RCA-SWEEP-SETTLE-LOOP countermeasure B). `toolchain-promote` (`toolchain.py promote` with the overlay's `repo` and the beat checkout: a promotion of `toolchain/stable` or nothing newer writes nothing, `PROMOTE-HELD` is its line, a refusal or failed read is `toolchain-promote: rc=<n>`; the last answer is kept in `S/beatd/toolchain.txt`). `darwin-selftest` (Darwin hosts only; one cycle per `origin/main` tip runs `prepr.sh --self-test` and the `--self-test` of every `tools/audit/seat` script `selftest_wiring.py` reports as self-testing and wired, with CI's plain `python3`; each pass holds a heavy slot of `tests/gate_lock.py` around a detached worktree it makes and removes, starts no self-test past `DARWIN_PASS_BUDGET_S` and resumes the same tip next pass, because one whole cycle outlasts the row's `timeout_s` on a Mac; a finished cycle writes one `darwin-selftest: RED <instrument> <first FAIL line>` per red, nothing when green; CI runs these on Linux only, so this finds a Darwin-only red after the merge and prevents none; the host's beat is the macOS leg, no paid runner). `plan-beat` hands the overlay's `train_log` to `state_docs.py --train-log`. Each writes only actionable lines to
   `S/digest/jobs/<row>`; `fold` concatenates them into `S/digest/digest.txt`,
   diffs `new.txt` and `gone.txt`, and touches `new.stamp` only on a new line,
   so the orchestrator's one wake reads `new.stamp` and `events.txt`. A null
diff --git a/tools/audit/seat/instruments/bottleneck_check.py.md b/tools/audit/seat/instruments/bottleneck_check.py.md
index 602cb69bf4..0262a3d69e 100644
--- a/tools/audit/seat/instruments/bottleneck_check.py.md
+++ b/tools/audit/seat/instruments/bottleneck_check.py.md
@@ -17,7 +17,9 @@
   row runs it every 30 minutes with `--train-log` (the overlay's
   `train_log`), `--wip-cap` (`plan_slots`) and `--memory`, which re-prints a
   held breach's first line verbatim so the digest's wake fires once per trip
-  and again only after a recovery. `--self-test`: a null control, one planted
+  and again only after a recovery, except while the live value is more than a
+  quarter worse than the first line's (lower is worse for yield and
+  throughput): then the live line prints. `--self-test`: a null control, one planted
   case per rule, each rule's boundary and minimum sample, a running batch not
   read, the UNREADABLE arm per rule, the trip memory, and one mutant per rule
   predicate; the beat row's arms are mutated in
diff --git a/tools/audit/seat/instruments/round_metrics.py.md b/tools/audit/seat/instruments/round_metrics.py.md
new file mode 100644
index 0000000000..535ce54c64
--- /dev/null
+++ b/tools/audit/seat/instruments/round_metrics.py.md
@@ -0,0 +1,22 @@
+# `round_metrics.py`
+
+- `round_metrics.py` — decision 0018 section 2's flow reads per round and per
+  week, and the producer of `scorecard.py`'s inputs (R11-PRE-ROUND-METRICS;
+  the process convergence audit d5d7ff81, section 6 row a3). Its rules and
+  null control are the script's docstring; the commands are:
+  - **A round, or its weeks:**
+
+        python3 -I tools/audit/seat/round_metrics.py report --dir <state>/scorecard \
+          --repo <checkout> --round <N> [--weeks]
+
+    `--since ISO [--until ISO]` reads any other window. A round whose
+    opening tag `v<N-1>.0.0` does not exist prints `round <N> unread`.
+  - **The producer** (the beat's `scorecard` row runs it once a day before
+    `scorecard.py report`; `GH_TOKEN` passed):
+
+        python3 -I tools/audit/seat/round_metrics.py produce --dir <state>/scorecard \
+          --repo <checkout> --gh-repo <owner/name>
+
+  `--self-test`: an empty input prints every read unread; a planted case per
+  read in a throwaway repository and planted state dirs; one mutant per
+  predicate.
diff --git a/tools/audit/seat/instruments/scorecard.py.md b/tools/audit/seat/instruments/scorecard.py.md
index ee69987209..9436eeaec4 100644
--- a/tools/audit/seat/instruments/scorecard.py.md
+++ b/tools/audit/seat/instruments/scorecard.py.md
@@ -1,6 +1,6 @@
 # `scorecard.py`
 
-- `scorecard.py` — the convergence scorecard (R10-MACH-SCORECARD): ten
+- `scorecard.py` — the convergence scorecard (R10-MACH-SCORECARD):
   report-only lines, one per signal, the baseline from which thresholds can
   later be set. No line sets an exit code or holds a merge. It is read-only on
   every input and makes no GitHub call; an input it cannot read prints
@@ -26,11 +26,15 @@
   - `K` — `recycle` lines of the standing dispatch and triage seats in the
     day's sweep record.
 
+  - `R` — `round_metrics.py`'s reads over the open round (merges by class,
+    `lead_time` per class, `product_green` with the gate's check count,
+    `restore`, `runner_s`, `tokens`).
+
   Every line but `H` is held in `--self-test` to a null control (a case whose
-  right answer is the quiet one). Inputs sit under `<state>/scorecard/`
+  right answer is the quiet one). Inputs sit under `<state>/scorecard/`, written by `round_metrics.py produce`
   (`runs.json`, `jobs/jobs_<id>.json`, `verdicts.json`, `merges.tsv`,
   `roster.json`) beside the overlay's `train_log` and the optional
-  `sweep_record`. When: the beat's `scorecard` row runs `report --dir
+  `sweep_record`. When: the beat's `scorecard` row runs the producer, then `report --dir
   <state>/scorecard --train-log <train_log> --repo <checkout>` (plus
   `--sweep-record` when the overlay names one) once a day and writes the
   output to `S/beatd/scorecard.txt`; the digest hears only
diff --git a/tools/audit/seat/round_metrics.py b/tools/audit/seat/round_metrics.py
new file mode 100644
index 0000000000..e84b9723ff
--- /dev/null
+++ b/tools/audit/seat/round_metrics.py
@@ -0,0 +1,452 @@
+#!/usr/bin/env python3
+"""round_metrics.py -- decision 0018's flow reads per round and per week, and the scorecard's input producer.
+
+    python3 -I round_metrics.py report --dir D --repo R (--round N | --since ISO [--until ISO]) [--weeks]
+    python3 -I round_metrics.py produce --dir D --repo R --gh-repo OWNER/NAME [--roster-ref REF]
+    python3 -I round_metrics.py --self-test [--no-mutants] [--tests DIR]
+
+WHY (owner ruling 2026-11-13, cards P3 and P8; the round-10 process convergence
+audit d5d7ff81, section 6 row a3): the scorecard had no producer for its inputs,
+and the audit's per-round and per-week figures came from out-of-tree scratch
+scripts. `produce` refreshes D (the beat's `<state>/scorecard/`); `report` reads
+only D and, for windows and gate checks, the checkout's git.
+
+THE WINDOW of round N runs from tag v(N-1).0.0 to tag vN.0.0 (decision 0016, a
+major version is a closed round), or to now while vN.0.0 does not exist; a round
+whose opening tag is missing is unread. `--weeks` cuts it into 7-day spans from
+its start; the last may be shorter and says so.
+
+THE READS (0018 section 2; each prints `unread (<why>)`, never a number, when its
+input is absent, and a partial ledger is a NO-READ, never a partial value):
+  merges          first-parent merges of main in the window by machinery_ratchet's
+                  class (production, machinery, record).
+  lead_time       per class, hours from the commit that ADDED the group to a roster
+                  (`"group": "<G>"` first appearing in dev/programme/rosters/ or
+                  .claude/workflows/ at the roster ref, never a field anyone fills)
+                  to the group's latest merge of that class in the window; p50 and
+                  p90 by nearest rank over groups. A merge maps to a group by the
+                  roster's resume.pr, else by its branch (owner prefix and
+                  fix/|handoff/|hotfix/ dropped, upper-cased, a split part's -pN
+                  suffix dropped) naming a group. A merge naming no group, and a
+                  group entered after its merge (unknowable, fixer.md step 16), are
+                  counted beside, never in the term.
+  product_green   main's concluded (success or failure) `CI` push runs in the window
+                  whose `gate` job (latest attempt) succeeded; cancelled beside; a
+                  concluded run with no job listing makes it unread; beside it the
+                  check count `tools/ci/gate.py` REQUIRED["push"] holds at the
+                  window's first and last main commit.
+  restore         median hours from a main run whose gate failed after a green one
+                  to the next run whose gate succeeded, over red spells closed in
+                  the window; an open spell beside.
+  runner_s        job seconds (completed_at - started_at, every attempt) of every
+                  completed `CI` run created in the window, over the window's
+                  merges; one run with no job listing makes it unread.
+  tokens          0018's tokens_per_change: the ledger `tokens.tsv` (t, seat_class,
+                  tokens) summed over the window, over production merges; a seat
+                  class of SEAT_CLASSES with no row in the window makes it unread.
+
+INPUTS under D, written by `produce` (one REST batch: the CI run listing since the
+open round's start, and each completed run's job listing not yet cached, at most
+JOB_FETCH_MAX per pass):
+  runs.json       [{id, t, c, attempt}] main `CI` push runs (scorecard.py's A lines)
+  ci_runs.json    [{id, t, c, attempt}] every completed `CI` run
+  jobs/jobs_<id>.json  {"attempt", "jobs": [{name, conclusion, started_at, completed_at, run_attempt}]}
+  merges.tsv      sha, pr, ct, class, tokens, group, entered (scorecard.py's H line)
+  entries.json    {"tip", "entered": {group: epoch}} the roster-entry scan's cache
+  verdicts.json   review_strength.load's bus;  roster.json  the newest roster
+"""
+from __future__ import annotations
+
+import argparse
+import csv
+import io
+import json
+import math
+import re
+import subprocess
+import sys
+import tarfile
+import tempfile
+import time
+from datetime import datetime, timezone
+from pathlib import Path
+
+HERE = Path(__file__).resolve().parent
+CLASSES = ("production", "machinery", "record")
+SEAT_CLASSES = ("orchestrator", "local", "cloud")
+WEEK_S = 7 * 86400
+JOB_FETCH_MAX = 400
+MERGES_MIN = 200  # merges.tsv keeps at least the newest 200, so scorecard's last-50 windows read
+ROSTER_PATHS = ("dev/programme/rosters/", ".claude/workflows/")
+SUBJECT = re.compile(r"^Merge pull request #(\d+) from [^/\s]+/(\S+)")
+ADDED = re.compile(r'^\+\s*"group":\s*"([^"]+)"')
+TSV = ("sha", "pr", "ct", "class", "tokens", "group", "entered")
+
+
+def epoch(s: str) -> float:
+    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
+
+
+def iso(t: float) -> str:
+    return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
+
+
+def rank(xs: list[float], p: float) -> float:
+    """Nearest-rank percentile: the smallest value with at least p of the sample at or below it."""
+    s = sorted(xs)
+    return s[max(0, math.ceil(p * len(s)) - 1)]
+
+
+def git(repo: Path, *a: str) -> str:
+    return subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True, check=True).stdout
+
+
+def read_json(path: Path):
+    try:
+        return json.loads(path.read_text())
+    except (OSError, ValueError):
+        return None
+
+
+# ------------------------------------------------------------------ windows
+
+def tag_time(repo: Path, n: int) -> float | None:
+    out = git(repo, "for-each-ref", "--format=%(creatordate:unix)", f"refs/tags/v{n}.0.0").strip()
+    return float(out) if out else None
+
+
+def round_window(repo: Path, n: int, now: float) -> tuple[float, float, str] | None:
+    a, b = tag_time(repo, n - 1), tag_time(repo, n)
+    if a is None:
+        return None
+    return a, (b if b is not None else now), ("closed" if b is not None else "open")
+
+
+def open_round(repo: Path) -> int | None:
+    tags = [int(m[1]) for m in re.finditer(r"^v(\d+)\.0\.0$", git(repo, "tag", "-l", "v*.0.0"), re.M)]
+    return max(tags) + 1 if tags else None
+
+
+def weeks(a: float, b: float) -> list[tuple[float, float]]:
+    out, t = [], a
+    while t < b:
+        out.append((t, min(t + WEEK_S, b)))
+        t += WEEK_S
+    return out
+
+
+# ------------------------------------------------------------------ reads over D
+
+def load_merges(d: Path) -> list[dict] | None:
+    try:
+        text = (d / "merges.tsv").read_text()
+    except OSError:
+        return None
+    rows = list(csv.DictReader(io.StringIO(text), delimiter="\t"))
+    for r in rows:
+        r["ct"] = int(r["ct"])
+    return rows
+
+
+def gate_conclusions(d: Path) -> dict[int, str]:
+    """Run id -> the conclusion of its `gate` job at the run's latest listed attempt."""
+    out: dict[int, str] = {}
+    for f in sorted((d / "jobs").glob("jobs_*.json")) if (d / "jobs").is_dir() else []:
+        doc = read_json(f)
+        try:
+            gates = [j for j in doc["jobs"] if j["name"] == "gate"]
+            if gates:
+                out[int(f.stem.split("_")[1])] = max(gates, key=lambda j: j.get("run_attempt") or 0)["conclusion"]
+        except (TypeError, KeyError, IndexError, ValueError):
+            continue
+    return out
+
+
+def lead_lines(rows: list[dict] | None, a: float, b: float) -> list[str]:
+    if rows is None:
+        return ["lead_time unread (merges.tsv)"]
+    out = []
+    for cls in CLASSES:
+        w = sorted((r for r in rows if r["class"] == cls and a <= r["ct"] < b), key=lambda r: r["ct"])
+        latest = {r["group"]: r for r in w}
+        nogroup = sum(not r["group"] for r in w)
+        hrs = [(r["ct"] - int(r["entered"])) / 3600 for r in latest.values() if r["entered"]]
+        ahead = sum(1 for h in hrs if h < 0)
+        hrs = [h for h in hrs if h >= 0]
+        side = f"{nogroup} {cls} merges name no roster group; {ahead} groups entered after their merge"
+        if not hrs:
+            out.append(f"lead_time {cls} unread (no {cls} group with a roster entry merged in the window; {side})")
+        else:
+            out.append(f"lead_time {cls} p50 {rank(hrs, 0.5):.1f} h p90 {rank(hrs, 0.9):.1f} h "
+                       f"(n={len(hrs)} groups; {side})")
+    return out
+
+
+def green_lines(runs: list | None, gate: dict, a: float, b: float, checks: str) -> list[str]:
+    if runs is None:
+        return ["product_green unread (runs.json)", "restore unread (runs.json)"]
+    seq = sorted((r for r in runs if r["c"] in ("success", "failure")), key=lambda r: r["t"])
+    w = [r for r in seq if a <= epoch(r["t"]) < b]
+    cancelled = sum(r["c"] == "cancelled" and a <= epoch(r["t"]) < b for r in runs)
+    if not w:
+        return ["product_green unread (no concluded main CI push run in the window)",
+                "restore unread (no concluded main CI push run in the window)"]
+    blind = [r for r in seq if r["id"] not in gate and epoch(r["t"]) < b]
+    if any(a <= epoch(r["t"]) for r in blind):
+        why = f"{sum(a <= epoch(r['t']) for r in blind)} of {len(w)} concluded runs have no job listing"
+        return [f"product_green unread ({why}: a partial ledger is no read)", f"restore unread ({why})"]
+    ok = sum(gate.get(r["id"]) == "success" for r in w)
+    green = (f"product_green {ok}/{len(w)} = {100 * ok / len(w):.0f}% (concluded main CI push runs; "
+             f"cancelled {cancelled}; gate checks {checks})")
+    spells, start = [], None
+    for r in (r for r in seq if r["id"] in gate and epoch(r["t"]) < b):
+        if gate[r["id"]] != "success" and start is None:
+            start = epoch(r["t"])
+        elif gate[r["id"]] == "success" and start is not None:
+            if epoch(r["t"]) >= a:
+                spells.append((epoch(r["t"]) - start) / 3600)
+            start = None
+    tail = f"; open red spell since {iso(start)}" if start is not None else ""
+    if not spells:
+        return [green, f"restore no red spell closed in the window ({len(w)} concluded runs read{tail})"]
+    return [green, f"restore median {rank(spells, 0.5):.1f} h over {len(spells)} red spells closed in the window "
+                   f"(longest {max(spells):.1f} h{tail})"]
+
+
+def runner_line(d: Path, merges: list | None, a: float, b: float) -> str:
+    runs = read_json(d / "ci_runs.json")
+    if runs is None or merges is None:
+        return "runner_s unread (ci_runs.json or merges.tsv)"
+    w = [r for r in runs if a <= epoch(r["t"]) < b]
+    m = sum(a <= r["ct"] < b for r in merges)
+    if not w or not m:
+        return f"runner_s unread ({len(w)} completed CI runs and {m} merges in the window)"
+    sec, blind = 0.0, 0
+    for r in w:
+        doc = read_json(d / "jobs" / f"jobs_{r['id']}.json")
+        if not doc or doc.get("attempt") != r["attempt"]:
+            blind += 1
+            continue
+        for j in doc["jobs"]:
+            if j.get("started_at") and j.get("completed_at"):
+                sec += max(0.0, epoch(j["completed_at"]) - epoch(j["started_at"]))
+    if blind:
+        return f"runner_s unread ({blind} of {len(w)} CI runs have no job listing at their latest attempt)"
+    return f"runner_s {sec / m:.0f} per merge ({sec:.0f} job seconds of {len(w)} CI runs over {m} merges)"
+
+
+def token_line(d: Path, merges: list | None, a: float, b: float) -> str:
+    try:
+        rows = list(csv.DictReader(io.StringIO((d / "tokens.tsv").read_text()), delimiter="\t"))
+    except OSError:
+        return "tokens unread (no token ledger tokens.tsv; R11-PRE-TOKEN-LEDGER builds it)"
+    w = [r for r in rows if a <= epoch(r["t"]) < b]
+    missing = [c for c in SEAT_CLASSES if not any(r["seat_class"] == c for r in w)]
+    prod = sum(r["class"] == "production" and a <= r["ct"] < b for r in merges or [])
+    if missing or not prod:
+        return f"tokens unread (seat classes with no ledger row: {', '.join(missing) or 'none'}; production merges {prod})"
+    total = sum(int(r["tokens"]) for r in w)
+    return f"tokens {total / prod:.0f} per production merge (window total {total}; {prod} production merges)"
+
+
+def window_lines(d: Path, a: float, b: float, checks: str) -> list[str]:
+    merges = load_merges(d)
+    out = []
+    if merges is None:
+        out.append("merges unread (merges.tsv)")
+    else:
+        n = {c: sum(r["class"] == c and a <= r["ct"] < b for r in merges) for c in CLASSES}
+        out.append(f"merges {sum(n.values())}: " + ", ".join(f"{c} {n[c]}" for c in CLASSES))
+    out += lead_lines(merges, a, b)
+    out += green_lines(read_json(d / "runs.json"), gate_conclusions(d), a, b, checks)
+    out.append(runner_line(d, merges, a, b))
+    out.append(token_line(d, merges, a, b))
+    return out
+
+
+# ------------------------------------------------------------------ git reads
+
+def gate_checks_at(repo: Path, sha: str) -> int | None:
+    """len(REQUIRED["push"]) of tools/ci/gate.py at <sha>, run from an archive of tools/ci there."""
+    try:
+        blob = subprocess.run(["git", "archive", sha, "tools/ci"], cwd=repo, capture_output=True, check=True).stdout
+        with tempfile.TemporaryDirectory() as td:
+            with tarfile.open(fileobj=io.BytesIO(blob)) as tf:
+                tf.extractall(td, filter="data")
+            p = subprocess.run([sys.executable, "-I", "-c", "import sys; sys.path.insert(0, sys.argv[1]); "
+                                "import gate; print(len(gate.REQUIRED['push']))", f"{td}/tools/ci"],
+                               capture_output=True, text=True, timeout=60)
+        return int(p.stdout.strip()) if p.returncode == 0 else None
+    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, tarfile.TarError, ValueError, OSError):
+        return None
+
+
+def gate_checks(repo: Path | None, a: float, b: float) -> str:
+    if repo is None:
+        return "unread"
+    ends = []
+    for t in (a, b):
+        sha = git(repo, "rev-list", "-1", "--first-parent", f"--before={int(t)}", "origin/main").strip()
+        n = gate_checks_at(repo, sha) if sha else None
+        ends.append("unread" if n is None else str(n))
+    return f"{ends[0]} at the window's start, {ends[1]} at its end"
+
+
+def roster_entries(repo: Path, ref: str, cache: dict) -> dict:
+    """{"tip", "entered"}: each group's first-adding commit time at <ref>, scanned from the cached tip."""
+    tip = git(repo, "rev-parse", ref).strip()
+    entered = dict(cache.get("entered") or {})
+    old = cache.get("tip")
+    span = f"{old}..{tip}" if old and subprocess.run(["git", "merge-base", "--is-ancestor", old, tip],
+                                                       cwd=repo).returncode == 0 else tip
+    t = None
+    for ln in git(repo, "log", "--reverse", "-p", "-U0", "--no-renames", "--format=@@C %ct", span,
+                  "--", *ROSTER_PATHS).splitlines():
+        if ln.startswith("@@C "):
+            t = int(ln[4:])
+        elif (m := ADDED.match(ln)) and m[1] not in entered:
+            entered[m[1]] = t
+    return {"tip": tip, "entered": entered}
+
+
+def group_of(pr: int | None, branch: str, by_pr: dict, names: set) -> str:
+    if pr in by_pr:
+        return by_pr[pr]
+    k = re.sub(r"^(?:fix|handoff|hotfix)/", "", branch).upper()
+    for c in (k, re.sub(r"-P\d+$", "", k)):
+        if c in names:
+            return c
+    return ""
+
+
+def rosters_at(repo: Path, ref: str) -> list[dict]:
+    groups = []
+    for f in git(repo, "ls-tree", "-r", "--name-only", ref, "dev/programme/rosters/").split():
+        if re.search(r"wave-r\d+-groups\.json$", f):
+            try:
+                groups += [g for g in json.loads(git(repo, "show", f"{ref}:{f}")).get("groups", []) if isinstance(g, dict)]
+            except (ValueError, subprocess.CalledProcessError):
+                continue
+    return groups
+
+
+def merge_rows(repo: Path, since: float, old: list[dict], groups: list[dict], entered: dict) -> list[dict]:
+    sys.path.insert(0, str(HERE.parent))
+    import machinery_ratchet as mr
+    cached = {r["sha"]: r["class"] for r in old}
+    by_pr = {}
+    for g in groups:
+        p = (g.get("resume") or {}).get("pr")
+        if isinstance(p, int):
+            by_pr[p] = g["group"]
+    names = {g["group"] for g in groups if "group" in g}
+    rows = []
+    for i, ln in enumerate(git(repo, "log", "--first-parent", "--merges", "--format=%H%x09%P%x09%ct%x09%s",
+                                "origin/main").splitlines()):
+        sha, parents, ct, subj = ln.split("\t", 3)
+        if int(ct) < since and i >= MERGES_MIN:
+            break
+        m = SUBJECT.match(subj)
+        pr, branch = (int(m[1]), m[2]) if m else (None, "")
+        cls = cached.get(sha) or mr.diff_stats(str(repo), parents.split()[0], sha)["kind"]
+        grp = group_of(pr, branch, by_pr, names)
+        rows.append({"sha": sha, "pr": pr or "", "ct": int(ct), "class": cls, "tokens": branch, "group": grp,
+                     "entered": entered.get(grp) or ""})
+    return rows[::-1]
+
+
+def write(path: Path, text: str) -> None:
+    path.parent.mkdir(parents=True, exist_ok=True)
+    tmp = path.with_suffix(path.suffix + ".tmp")
+    tmp.write_text(text)
+    tmp.replace(path)
+
+
+def produce(d: Path, repo: Path, gh_repo: str, roster_ref: str | None, paginate=None) -> list[str]:
+    """Refresh every input under D; returns the notes it prints (jobs left for the next pass)."""
+    sys.path.insert(0, str(HERE))
+    sys.path.insert(0, str(HERE.parent.parent / "ci"))
+    import roster_lib
+    import review_strength
+    if paginate is None:
+        import ghapi
+        paginate = ghapi.paginate
+    n = open_round(repo)
+    since = tag_time(repo, n - 1) if n else None
+    if since is None:
+        raise SystemExit("round_metrics: no v*.0.0 tag, so no open round to read from")
+    ref = roster_lib.reader_ref(str(repo), roster_ref)
+    groups = rosters_at(repo, ref)
+    entries = roster_entries(repo, ref, read_json(d / "entries.json") or {})
+    write(d / "entries.json", json.dumps(entries, sort_keys=True))
+    rows = merge_rows(repo, since, load_merges(d) or [], groups, entries["entered"])
+    write(d / "merges.tsv", "\t".join(TSV) + "\n" + "".join("\t".join(str(r[k]) for k in TSV) + "\n" for r in rows))
+    write(d / "roster.json", json.dumps(roster_lib.show_roster(str(repo), ref)))
+    bus, _ = review_strength.load(repo, "origin")
+    write(d / "verdicts.json", json.dumps({"verdicts": [dict(pr=v["pr"], head=v["head"], kind=v["kind"], cls=v["cls"],
+                                                              t=v["t"].isoformat()) for v in bus]}))
+    return fetch_runs(d, gh_repo, since, paginate)
+
+
+def fetch_runs(d: Path, gh_repo: str, since: float, paginate) -> list[str]:
+    """runs.json, ci_runs.json and the job listings not yet cached at a run's latest attempt."""
+    listed = paginate(f"repos/{gh_repo}/actions/workflows/ci.yml/runs",
+                      {"created": f">={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(since))}", "status": "completed"})
+    ci = [{"id": r["id"], "t": r["created_at"], "c": r["conclusion"], "attempt": r["run_attempt"]} for r in listed]
+    main = [x for x, r in zip(ci, listed) if r["event"] == "push" and r["head_branch"] == "main"]
+    write(d / "ci_runs.json", json.dumps(ci))
+    write(d / "runs.json", json.dumps(main))
+    todo = [r for r in ci if (read_json(d / "jobs" / f"jobs_{r['id']}.json") or {}).get("attempt") != r["attempt"]]
+    keep = ("name", "conclusion", "started_at", "completed_at", "run_attempt")
+    for r in todo[:JOB_FETCH_MAX]:
+        jobs = paginate(f"repos/{gh_repo}/actions/runs/{r['id']}/jobs", {"filter": "all"})
+        write(d / "jobs" / f"jobs_{r['id']}.json",
+              json.dumps({"attempt": r["attempt"], "jobs": [{k: j.get(k) for k in keep} for j in jobs]}))
+    left = len(todo) - JOB_FETCH_MAX
+    return [f"round_metrics: {left} job listings left for the next pass"] if left > 0 else []
+
+
+def main(argv: list[str]) -> int:
+    if argv[:1] == ["--self-test"]:
+        import round_metrics_selftest
+        tests = Path(argv[argv.index("--tests") + 1]) if "--tests" in argv else HERE.parents[2] / "tests"
+        return round_metrics_selftest.run(Path(__file__), "--no-mutants" not in argv, tests)
+    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
+    ap.add_argument("cmd", choices=["report", "produce"])
+    ap.add_argument("--dir", required=True, type=Path)
+    ap.add_argument("--repo", required=True, type=Path)
+    ap.add_argument("--round", type=int)
+    ap.add_argument("--since")
+    ap.add_argument("--until")
+    ap.add_argument("--weeks", action="store_true")
+    ap.add_argument("--gh-repo")
+    ap.add_argument("--roster-ref")
+    a = ap.parse_args(argv)
+    if a.cmd == "produce":
+        if not a.gh_repo:
+            ap.error("produce needs --gh-repo")
+        print("\n".join(produce(a.dir, a.repo, a.gh_repo, a.roster_ref)))
+        return 0
+    now = time.time()
+    if a.round is not None:
+        w = round_window(a.repo, a.round, now)
+        if w is None:
+            print(f"round {a.round} unread (no tag v{a.round - 1}.0.0 opens it)")
+            return 0
+        start, end, state = w
+    elif a.since:
+        start, end = epoch(a.since), epoch(a.until) if a.until else now
+        state = "given"
+    else:
+        ap.error("report needs --round or --since")
+    spans = [(start, end)] + (weeks(start, end) if a.weeks else [])
+    for k, (s, e) in enumerate(spans):
+        name = "window" if k == 0 else f"week {k}" + (" (short)" if e - s < WEEK_S else "")
+        print(f"== {name} {iso(s)} .. {iso(e)} ({state})")
+        print("\n".join(window_lines(a.dir, s, e, gate_checks(a.repo, s, e))))
+    return 0
+
+
+if __name__ == "__main__":
+    sys.path.insert(0, str(HERE))
+    sys.exit(main(sys.argv[1:]))
diff --git a/tools/audit/seat/round_metrics_selftest.py b/tools/audit/seat/round_metrics_selftest.py
new file mode 100644
index 0000000000..dde6ec0e44
--- /dev/null
+++ b/tools/audit/seat/round_metrics_selftest.py
@@ -0,0 +1,275 @@
+"""Self-test of round_metrics.py: the empty-input null control, a planted case per read, and one mutant per predicate.
+
+Run through round_metrics.py's own test mode. Offline: planted state dirs, a throwaway git
+repository (tests/throwaway_git.py) for the roster-entry clock, the merge classes, the round
+windows and the gate check count, and a fake paginator for the producer's API half. The mutants
+edit a temp copy of round_metrics.py; a mutant that survives, or whose copy does not run, fails.
+"""
+from __future__ import annotations
+
+import importlib.util
+import json
+import subprocess
+import sys
+import tempfile
+from pathlib import Path
+
+T0 = 1_800_000_000  # 2027-01-15T08:00Z; every planted stamp is T0 plus hours
+H = 3600
+
+
+def load(path: Path):
+    spec = importlib.util.spec_from_file_location("round_metrics_under_test", path)
+    mod = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(mod)
+    return mod
+
+
+def at(m, hours: float) -> str:
+    return m.datetime.fromtimestamp(T0 + hours * H, m.timezone.utc).isoformat().replace("+00:00", "Z")
+
+
+def tsv(rows) -> str:
+    return "sha\tpr\tct\tclass\ttokens\tgroup\tentered\n" + "".join(
+        f"s{i}\t{i}\t{T0 + ct * H}\t{c}\tb\t{g}\t{'' if e is None else T0 + e * H}\n" for i, (ct, c, g, e) in enumerate(rows))
+
+
+def state(td: Path, merges=None, runs=None, jobs=None, ci=None, tokens=None) -> Path:
+    d = td / "sc"
+    (d / "jobs").mkdir(parents=True, exist_ok=True)
+    if merges is not None:
+        (d / "merges.tsv").write_text(tsv(merges))
+    if runs is not None:
+        (d / "runs.json").write_text(json.dumps(runs))
+    if ci is not None:
+        (d / "ci_runs.json").write_text(json.dumps(ci))
+    for rid, doc in (jobs or {}).items():
+        (d / "jobs" / f"jobs_{rid}.json").write_text(json.dumps(doc))
+    if tokens is not None:
+        (d / "tokens.tsv").write_text("t\tseat_class\ttokens\n" + "".join(f"{t}\t{c}\t{n}\n" for t, c, n in tokens))
+    return d
+
+
+def gate_doc(*concl, attempt=1):
+    """A job listing whose gate job concluded concl[k] at attempt k+1."""
+    return {"attempt": attempt, "jobs": [{"name": "gate", "conclusion": c, "run_attempt": k + 1,
+                                          "started_at": None, "completed_at": None} for k, c in enumerate(concl)]}
+
+
+def git_cases(m, tests: Path, r: dict) -> None:
+    sys.path.insert(0, str(tests))
+    from throwaway_git import throwaway_git_init
+    with tempfile.TemporaryDirectory() as td:
+        repo = Path(td) / "repo"
+        repo.mkdir()
+        env = throwaway_git_init(repo, "-q", "-b", "main")
+
+        def commit(when: int, files: dict, msg="c", merge_of=None):
+            for f, text in files.items():
+                (repo / f).parent.mkdir(parents=True, exist_ok=True)
+                (repo / f).write_text(text)
+            subprocess.run(["git", "add", "-A"], cwd=repo, env=env, check=True)
+            e = dict(env, GIT_COMMITTER_DATE=f"{when} +0000", GIT_AUTHOR_DATE=f"{when} +0000")
+            if merge_of:
+                subprocess.run(["git", "merge", "-q", "--no-ff", "-m", msg, merge_of], cwd=repo, env=e, check=True)
+            else:
+                subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", msg], cwd=repo, env=e, check=True)
+            return subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, env=env, capture_output=True, text=True).stdout.strip()
+
+        ros = "dev/programme/rosters/wave-r1-groups.json"
+        g = lambda *names: json.dumps({"groups": [{"group": n, "resume": {"pr": 7} if n == "G-PR" else {}} for n in names]},
+                                      indent=1)
+        commit(T0, {ros: g("G-A"), "tools/ci/gate.py": "REQUIRED = {'push': ('a', 'b')}\n"}, "base")
+        subprocess.run(["git", "tag", "v0.0.0"], cwd=repo, env=env, check=True)
+        commit(T0 + 2 * H, {ros: g("G-A", "G-B", "G-PR")}, "add G-B")
+        subprocess.run(["git", "tag", "v1.0.0"], cwd=repo, env=env, check=True)
+        commit(T0 + 3 * H, {ros: g("G-PR", "G-B", "G-A")}, "reorder: no group is added again")
+        subprocess.run(["git", "checkout", "-q", "-b", "fix/g-b-p2"], cwd=repo, env=env, check=True)
+        commit(T0 + 4 * H, {"custom_components/x.py": "x = 1\n"})
+        subprocess.run(["git", "checkout", "-q", "main"], cwd=repo, env=env, check=True)
+        commit(T0 + 5 * H, {}, "Merge pull request #5 from o/fix/g-b-p2", merge_of="fix/g-b-p2")
+        subprocess.run(["git", "checkout", "-q", "-b", "fix/other"], cwd=repo, env=env, check=True)
+        commit(T0 + 6 * H, {"tools/ci/gate.py": "REQUIRED = {'push': ('a', 'b', 'c')}\n"})
+        subprocess.run(["git", "checkout", "-q", "main"], cwd=repo, env=env, check=True)
+        commit(T0 + 7 * H, {}, "Merge pull request #7 from o/fix/other", merge_of="fix/other")
+        subprocess.run(["git", "update-ref", "refs/remotes/origin/main", "HEAD"], cwd=repo, env=env, check=True)
+
+        e = m.roster_entries(repo, "main", {})
+        r["roster clock: a group's entry is the commit that first added it, not a later reorder"] = \
+            e["entered"] == {"G-A": T0, "G-B": T0 + 2 * H, "G-PR": T0 + 2 * H}
+        e2 = m.roster_entries(repo, "main", {"tip": e["tip"], "entered": {"G-A": 1}})
+        r["roster clock: an incremental scan from the cached tip keeps the cache"] = e2["entered"] == {"G-A": 1}
+        groups = m.rosters_at(repo, "main")
+        rows = m.merge_rows(repo, T0, [], groups, e["entered"])
+        r["merges: classes by machinery_ratchet, a split part maps to its group, resume.pr wins"] = \
+            [(x["pr"], x["class"], x["group"], x["entered"]) for x in rows] == \
+            [(5, "production", "G-B", T0 + 2 * H), (7, "machinery", "G-PR", T0 + 2 * H)]
+        r["merges: a cached class is not re-derived"] = \
+            m.merge_rows(repo, T0, [{"sha": rows[0]["sha"], "class": "record"}], groups, {})[0]["class"] == "record"
+        w = m.round_window(repo, 2, T0 + 9 * H)
+        r["window: an open round runs from its opening tag to now"] = w == (float(T0 + 2 * H), float(T0 + 9 * H), "open")
+        r["window: a closed round runs from its opening tag to its own"] = \
+            m.round_window(repo, 1, T0 + 9 * H) == (float(T0), float(T0 + 2 * H), "closed")
+        r["window: a round with no opening tag is unread"] = m.round_window(repo, 5, T0) is None
+        r["window: the open round is one past the newest major tag"] = m.open_round(repo) == 2
+        r["gate checks: REQUIRED['push'] counted at the window's two ends"] = \
+            m.gate_checks(repo, T0 + H, T0 + 8 * H) == "2 at the window's start, 3 at its end"
+        r["gate checks: a commit without gate.py is unread"] = m.gate_checks_at(repo, "HEAD~9999") is None
+
+
+def cases(m, tests: Path) -> dict[str, bool]:
+    r: dict[str, bool] = {}
+    with tempfile.TemporaryDirectory() as td:
+        empty = m.window_lines(Path(td) / "none", T0, T0 + 100 * H, "unread")
+        r["null: an empty input directory prints every read unread"] = len(empty) == 6 and all(" unread (" in x for x in empty)
+        rows = [(10, "production", "A", 0), (20, "production", "A", 0), (30, "production", "B", 20), (40, "production", "C", 10),
+                (50, "production", "", None), (60, "production", "D", 70), (15, "machinery", "M", 5), (200, "production", "Z", 0)]
+        d = state(Path(td), merges=rows)
+        lt = m.lead_lines(m.load_merges(d), T0, T0 + 100 * H)
+        r["lead_time: the latest merge per group, p50 and p90 by nearest rank"] = \
+            lt[0].startswith("lead_time production p50 20.0 h p90 30.0 h (n=3 groups;")
+        r["lead_time: a merge naming no group and a group entered after its merge are beside"] = \
+            "1 production merges name no roster group; 1 groups entered after their merge" in lt[0]
+        r["lead_time: each class its own line; a class with none merged is unread"] = \
+            lt[1].startswith("lead_time machinery p50 10.0 h") and lt[2].startswith("lead_time record unread (")
+        r["merges: the window's merges by class"] = \
+            m.window_lines(d, T0, T0 + 100 * H, "x")[0] == "merges 7: production 6, machinery 1, record 0"
+        r["rank: nearest rank"] = m.rank([1, 2, 3, 4], 0.5) == 2 and m.rank([1, 2, 3, 4], 0.9) == 4 and m.rank([5], 0.9) == 5
+
+    with tempfile.TemporaryDirectory() as td:
+        runs = [{"id": i, "t": at(m, h), "c": c} for i, (h, c) in enumerate(
+            [(1, "success"), (2, "failure"), (3, "failure"), (5, "success"), (6, "cancelled"), (7, "failure"), (9, "success"),
+             (11, "failure")])] + [{"id": 8, "t": at(m, 8), "c": "failure"}]
+        jobs = {0: gate_doc("success"), 1: gate_doc("failure"), 2: gate_doc("failure", "success", attempt=2),
+                3: gate_doc("success"), 5: gate_doc("failure"), 6: gate_doc("success"), 7: gate_doc("failure"),
+                8: gate_doc("failure")}
+        d = state(Path(td), runs=runs, jobs=jobs)
+        g, rs = m.green_lines(m.read_json(d / "runs.json"), m.gate_conclusions(d), T0, T0 + 12 * H, "2 at x")
+        r["product_green: concluded runs whose gate (latest attempt) succeeded; cancelled beside"] = \
+            g == "product_green 4/8 = 50% (concluded main CI push runs; cancelled 1; gate checks 2 at x)"
+        r["product_green: a run failing outside its gate counts green (null)"] = \
+            m.green_lines([{"id": 1, "t": at(m, 1), "c": "failure"}], {1: "success"}, T0, T0 + 2 * H, "x")[0].startswith(
+                "product_green 1/1 = 100%")
+        r["restore: median over red spells closed in the window, an open spell beside"] = \
+            rs == f"restore median 1.0 h over 2 red spells closed in the window (longest 2.0 h; open red spell since {m.iso(T0 + 11 * H)})"
+        r["restore: a spell closed before the window is not counted"] = \
+            m.green_lines(runs, m.gate_conclusions(d), T0 + 6 * H, T0 + 10 * H, "x")[1].startswith("restore median 2.0 h over 1 red")
+        r["restore: no red spell is a read, not unread"] = \
+            m.green_lines(runs[:1], {0: "success"}, T0, T0 + 2 * H, "x")[1] == "restore no red spell closed in the window (1 concluded runs read)"
+        del jobs[3]
+        (d / "jobs" / "jobs_3.json").unlink()
+        g, rs = m.green_lines(runs, m.gate_conclusions(d), T0, T0 + 12 * H, "x")
+        r["product_green: a concluded run with no job listing makes it unread (a partial ledger)"] = \
+            g.startswith("product_green unread (1 of 8 concluded runs have no job listing") and rs.startswith("restore unread (")
+        r["product_green: a cancelled run with no listing does not blind it"] = \
+            m.green_lines(runs[:4], {0: "success", 1: "failure", 2: "success", 3: "success"}, T0, T0 + 12 * H, "x")[0].startswith(
+                "product_green 3/4")
+
+    with tempfile.TemporaryDirectory() as td:
+        job = lambda a, b: {"name": "j", "conclusion": "success", "started_at": at(m, a), "completed_at": at(m, b), "run_attempt": 1}
+        ci = [{"id": 1, "t": at(m, 1), "c": "success", "attempt": 1}, {"id": 2, "t": at(m, 2), "c": "failure", "attempt": 2},
+              {"id": 3, "t": at(m, 50), "c": "success", "attempt": 1}]
+        jobs = {1: {"attempt": 1, "jobs": [job(1, 1.5), job(1, 1), {"name": "s", "started_at": None, "completed_at": None}]},
+                2: {"attempt": 2, "jobs": [job(2, 2.25), job(3, 3.25)]}}
+        d = state(Path(td), merges=[(1, "machinery", "", None), (3, "production", "", None)], ci=ci, jobs=jobs,
+                  tokens=[(at(m, 1), "orchestrator", 100), (at(m, 2), "local", 50), (at(m, 3), "cloud", 50), (at(m, 60), "cloud", 9)])
+        merges = m.load_merges(d)
+        r["runner_s: job seconds of the window's CI runs over its merges"] = \
+            m.runner_line(d, merges, T0, T0 + 10 * H) == "runner_s 1800 per merge (3600 job seconds of 2 CI runs over 2 merges)"
+        jobs[2]["attempt"] = 1
+        (d / "jobs" / "jobs_2.json").write_text(json.dumps(jobs[2]))
+        r["runner_s: a run whose listing is of an older attempt makes it unread"] = \
+            m.runner_line(d, merges, T0, T0 + 10 * H).startswith("runner_s unread (1 of 2 CI runs")
+        r["tokens: the ledger over the window, over production merges"] = \
+            m.token_line(d, merges, T0, T0 + 10 * H) == "tokens 200 per production merge (window total 200; 1 production merges)"
+        r["tokens: a seat class with no row in the window makes it unread"] = \
+            m.token_line(d, merges, T0 + 2.5 * H, T0 + 10 * H) == \
+            "tokens unread (seat classes with no ledger row: orchestrator, local; production merges 1)"
+        r["weeks: 7-day spans from the start, the last short"] = \
+            m.weeks(T0, T0 + 10 * 86400) == [(T0, T0 + 7 * 86400), (T0 + 7 * 86400, T0 + 10 * 86400)]
+        r["group_of: resume.pr, then the branch, then the branch less a part suffix"] = \
+            (m.group_of(9, "fix/x", {9: "P"}, {"X"}), m.group_of(1, "handoff/x-p3", {}, {"X"}),
+             m.group_of(1, "fix/x-pr", {}, {"X"}), m.group_of(1, "hotfix/x", {}, {"X"})) == ("P", "X", "", "X")
+
+        calls = []
+
+        def fake(path, params):
+            calls.append(path)
+            if path.endswith("/runs"):
+                return [{"id": 11, "created_at": at(m, 1), "conclusion": "success", "run_attempt": 2, "event": "push", "head_branch": "main"},
+                        {"id": 12, "created_at": at(m, 2), "conclusion": "failure", "run_attempt": 1, "event": "pull_request", "head_branch": "x"}]
+            return [{"name": "gate", "conclusion": "success", "run_attempt": 2, "started_at": None, "completed_at": None, "id": 5}]
+        out = Path(td) / "fetched"
+        m.fetch_runs(out, "o/r", T0, fake)
+        r["producer: main push runs in runs.json, every run in ci_runs.json, each listing fetched"] = \
+            [x["id"] for x in m.read_json(out / "runs.json")] == [11] and len(m.read_json(out / "ci_runs.json")) == 2 \
+            and m.read_json(out / "jobs" / "jobs_11.json")["attempt"] == 2 and len(calls) == 3
+        calls.clear()
+        m.fetch_runs(out, "o/r", T0, fake)
+        r["producer: a listing cached at the run's latest attempt is not fetched again"] = len(calls) == 1
+    git_cases(m, tests, r)
+    return r
+
+
+#: (needle in round_metrics.py, replacement, the case that must fail). One per predicate.
+MUTANTS = {
+    "rank index": ("math.ceil(p * len(s)) - 1", "math.floor(p * len(s))", "rank: nearest rank"),
+    "lead latest per group": ('key=lambda r: r["ct"])', 'key=lambda r: -r["ct"])', "lead_time: the latest merge"),
+    "lead unknowable kept": ("hrs = [h for h in hrs if h >= 0]", "hrs = hrs", "lead_time: the latest merge"),
+    "lead class filter": ('if r["class"] == cls and a <= r["ct"] < b', 'if a <= r["ct"] < b', "lead_time: each class"),
+    "green concluded": ('if r["c"] in ("success", "failure")', 'if r["c"] != "x"', "product_green: concluded runs"),
+    "green gate": ('ok = sum(gate.get(r["id"]) == "success" for r in w)', 'ok = sum(r["c"] == "success" for r in w)',
+                   "product_green: a run failing outside"),
+    "green partial ledger": ("    if any(a <= epoch(r[\"t\"]) for r in blind):", "    if False:",
+                             "product_green: a concluded run with no job listing"),
+    "gate latest attempt": ('key=lambda j: j.get("run_attempt") or 0)', 'key=lambda j: -(j.get("run_attempt") or 0))',
+                            "product_green: concluded runs"),
+    "restore window": ("            if epoch(r[\"t\"]) >= a:\n", "            if True:\n", "restore: a spell closed before"),
+    "restore start kept": ('if gate[r["id"]] != "success" and start is None:', 'if gate[r["id"]] != "success":',
+                           "restore: median"),
+    "runner attempt": ('doc.get("attempt") != r["attempt"]', "False", "runner_s: a run whose listing is of an older"),
+    "runner window": ('w = [r for r in runs if a <= epoch(r["t"]) < b]', "w = list(runs)", "runner_s: job seconds"),
+    "tokens class": ("missing or not prod", "not prod", "tokens: a seat class"),
+    "tokens production": ('r["class"] == "production" and a <= r["ct"] < b', 'a <= r["ct"] < b', "tokens: the ledger"),
+    "roster first add": ("and m[1] not in entered", "", "roster clock: a group's entry"),
+    "roster incremental": ('span = f"{old}..{tip}" if old and', 'span = tip if old and', "roster clock: an incremental"),
+    "group part suffix": ('re.sub(r"-P\\d+$", "", k)', "k", "group_of:"),
+    "group by pr": ("    if pr in by_pr:\n        return by_pr[pr]\n", "", "merges: classes"),
+    "merge cached class": ("cached.get(sha) or ", "", "merges: a cached class"),
+    "producer main filter": ('r["event"] == "push" and r["head_branch"] == "main"', "True", "producer: main push runs"),
+    "producer cache": ('.get("attempt") != r["attempt"]]', ".get(\"attempt\") is not None or True]", "producer: a listing cached"),
+    "window open": ('(b if b is not None else now)', "now", "window: a closed round"),
+    "week span": ("min(t + WEEK_S, b)", "t + WEEK_S", "weeks:"),
+}
+
+
+def run(path: Path, mutants: bool, tests: Path) -> int:
+    bad: list[str] = []
+    for name, ok in cases(load(path), tests).items():
+        print(("ok   " if ok else "FAIL ") + name)
+        if not ok:
+            bad.append(name)
+    if mutants:
+        src = path.read_text()
+        here = Path(__file__).resolve()
+        for name, (old, new, case) in MUTANTS.items():
+            if src.count(old) != 1:
+                print(f"FAIL mutant {name}: needle found {src.count(old)} times")
+                bad.append(name)
+                continue
+            with tempfile.TemporaryDirectory() as td:
+                (Path(td) / path.name).write_text(src.replace(old, new))
+                (Path(td) / here.name).write_text(here.read_text())
+                p = subprocess.run([sys.executable, "-I", str(Path(td) / here.name), str(tests), str(path.parents[1])],
+                                   capture_output=True, text=True, timeout=300)
+            killed = p.returncode != 0 and any(ln.startswith("FAIL") and case in ln for ln in p.stdout.splitlines())
+            print(("ok   " if killed else "FAIL ") + f"mutant killed: {name} (by '{case}')")
+            if not killed:
+                bad.append("mutant " + name)
+    print("round_metrics self-test: " + ("FAIL " + "; ".join(bad) if bad else f"ok ({'with' if mutants else 'without'} mutants)"))
+    return 1 if bad else 0
+
+
+if __name__ == "__main__":  # a mutant copy runs its cases only: argv is the tests dir and tools/audit
+    sys.path.insert(0, sys.argv[2])
+    sys.exit(run(Path(__file__).with_name("round_metrics.py"), False, Path(sys.argv[1])))
diff --git a/tools/audit/seat/scorecard.py b/tools/audit/seat/scorecard.py
index 97b4b64f48..b085052570 100644
--- a/tools/audit/seat/scorecard.py
+++ b/tools/audit/seat/scorecard.py
@@ -1,17 +1,18 @@
 #!/usr/bin/env python3
-"""Convergence scorecard: ten report-only lines, one per signal, each with its null control.
+"""Convergence scorecard: report-only lines, one per signal, each with its null control.
 
     python3 -I scorecard.py report --dir D --train-log PATH [--repo DIR] [--sweep-record PATH]
     python3 -I scorecard.py --self-test [--no-mutants]
 
 Report-only (R10-MACH-SCORECARD): no line sets an exit code or holds a merge. It
 is the baseline from which thresholds can later be set. Read-only on every
-input and no GitHub call; the inputs are refreshed elsewhere and an input it
+input and no GitHub call; the inputs are refreshed by round_metrics.py and an input it
 cannot read prints `<line>  unread (<why>)`, never a guessed value.
 
-INPUTS, all under D (the beat's `<state>/scorecard/`) except the train log:
-  runs.json      [{id, t, c}] main `CI` push runs: id, UTC stamp, run conclusion
-  jobs/jobs_<id>.json   the run's job listing (`{"jobs": [{name, conclusion}]}`)
+INPUTS, all under D (the beat's `<state>/scorecard/`) except the train log,
+written by `round_metrics.py produce`:
+  runs.json      [{id, t, c, attempt}] main `CI` push runs: id, UTC stamp, run conclusion
+  jobs/jobs_<id>.json   the run's job listing, every attempt (`{"attempt", "jobs": [{name, conclusion, run_attempt, ...}]}`)
   verdicts.json  {"verdicts": [{pr, head, kind, cls, t}]} review verdicts
   merges.tsv     TSV with columns pr, ct, class, tokens (merge order by ct)
   roster.json    {"groups": [...]} the round's roster
@@ -20,7 +21,7 @@ INPUTS, all under D (the beat's `<state>/scorecard/`) except the train log:
 
 THE LINES (rule, then the null control the self-test holds it to):
   A_gate   share of the last 20 concluded (success or failure) main runs whose
-           job named `gate` concluded success; a run with no cached job listing
+           job named `gate` concluded success at its latest attempt; a run with no cached job listing
            is `unread`, reported and not guessed.
            NULL: a run whose only failed job is `governance / instrument-self-tests`
            counts green here and red in A_run.
@@ -58,6 +59,12 @@ THE LINES (rule, then the null control the self-test holds it to):
            in the day's sweep record.
            NULL: K is 0 with no recycle line.
 C and K are one row of the study's table and print on one line.
+  R        round_metrics.py's reads over the open round (R11-PRE-ROUND-METRICS):
+           merges by class, lead_time p50/p90 per class, product_green with the
+           gate's check count, restore (time to restore), runner_s and tokens.
+           Their rules and null controls are round_metrics.py's; its producer
+           (`round_metrics.py produce`) writes every input above but the train log.
+           NULL: an empty state dir prints every R line unread.
 """
 from __future__ import annotations
 
@@ -70,8 +77,12 @@ import json
 import re
 import subprocess
 import sys
+import time
 from pathlib import Path
 
+sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I drops the script's directory
+import round_metrics  # noqa: E402
+
 WINDOW_RUNS = 20
 WINDOW_PRS = 50
 WINDOW_MERGES = 50
@@ -217,8 +228,9 @@ def rd(path: Path):
         return None
 
 
-def report(d: Path, train_log: Path, repo: Path | None, record: Path | None, run=sh_out) -> list[str]:
+def report(d: Path, train_log: Path, repo: Path | None, record: Path | None, run=sh_out, now: float | None = None) -> list[str]:
     out: list[str] = []
+    now = time.time() if now is None else now
 
     def load(name):
         t = rd(d / name)
@@ -228,14 +240,7 @@ def report(d: Path, train_log: Path, repo: Path | None, record: Path | None, run
             return None
 
     runs = load("runs.json")
-    gate: dict = {}
-    for f in sorted((d / "jobs").glob("jobs_*.json")) if (d / "jobs").is_dir() else []:
-        try:
-            for j in json.loads(f.read_text()).get("jobs", []):
-                if j["name"] == "gate":
-                    gate[int(f.stem.split("_")[1])] = j["conclusion"]
-        except (ValueError, KeyError, IndexError):
-            continue
+    gate = round_metrics.gate_conclusions(d)
     out += line_a(runs, gate) if runs else ["A_gate  unread (runs.json)", "A_run   unread (runs.json)"]
     v = load("verdicts.json")
     ytxt = rd(d.parent / "study" / "work" / "yield.py")
@@ -253,7 +258,17 @@ def report(d: Path, train_log: Path, repo: Path | None, record: Path | None, run
     ro = load("roster.json")
     out.append(line_escapes(ro["groups"]) if ro else "E       unread (roster.json)")
     out.append(line_ck(runs, rd(record) if record else None))
-    return out
+    return out + line_round(d, repo, now)
+
+
+def line_round(d: Path, repo: Path | None, now: float) -> list[str]:
+    """round_metrics' reads over the open round: lead time per class, product_green, restore, runner and tokens."""
+    n = round_metrics.open_round(repo) if repo else None
+    w = round_metrics.round_window(repo, n, now) if n else None
+    if w is None:
+        return ["R       unread (no checkout, or no v*.0.0 tag opens a round)"]
+    head = f"R       round {n} {round_metrics.iso(w[0])} .. {round_metrics.iso(w[1])} ({w[2]})"
+    return [head] + ["R       " + ln for ln in round_metrics.window_lines(d, w[0], w[1], round_metrics.gate_checks(repo, w[0], w[1]))]
 
 
 def main(argv: list[str]) -> int:
diff --git a/tools/audit/seat/scorecard_selftest.py b/tools/audit/seat/scorecard_selftest.py
index 494fe70b3f..3320eb4785 100644
--- a/tools/audit/seat/scorecard_selftest.py
+++ b/tools/audit/seat/scorecard_selftest.py
@@ -143,12 +143,13 @@ def cases(sc) -> dict[str, bool]:
         (Path(td) / "sweep.txt").write_text("dispatch recycle\n")
         out = sc.report(d, Path(td) / "train.log", None, Path(td) / "sweep.txt")
         r["report: ten lines' worth over a planted state dir (S unread without a checkout)"] = \
-            len(out) == 9 and not any("unread (" in x for x in out if x[:2] != "S ") and out[0].startswith("A_gate  5/5")
+            len(out) == 10 and not any("unread (" in x for x in out if x[:2] not in ("S ", "R ")) and out[0].startswith("A_gate  5/5")
         r["report: A_gate reads the job named gate, not the last job listed"] = out[0].startswith("A_gate  5/5 read = 100%") and out[1].startswith("A_run   4/5")
-        r["report: K reads the sweep record it is given"] = "K 1 " in out[-1] and "K unread" not in out[-1]
+        r["report: K reads the sweep record it is given"] = "K 1 " in out[-2] and "K unread" not in out[-2]
+        r["report: without a checkout the round lines are one unread R line"] = out[-1].startswith("R       unread (")
         empty = sc.report(Path(td) / "none", Path(td) / "none.log", None, None)
         r["report: an empty state dir prints unread on every line, none a number"] = \
-            all("unread" in x for x in empty if not x.startswith("C, K")) and "C unread; K unread" in empty[-1]
+            all("unread" in x for x in empty if not x.startswith("C, K")) and "C unread; K unread" in empty[-2]
     return r
 
 
@@ -163,7 +164,6 @@ MUTANTS = {
     "M_first family inverted": ("in MACH for v in last", "not in MACH for v in last", "M_first planted"),
     "Y_rev first verdict kept": ("first.setdefault(v[\"pr\"], v)", "first[v[\"pr\"]] = v", "Y_rev first verdict"),
     "Y_rev ordered by t": ('sorted(verdicts, key=lambda v: v["t"])', "list(verdicts)", "Y_rev unordered"),
-    "A_gate job named gate": ('if j["name"] == "gate":', "if True:", "report: A_gate reads the job named gate"),
     "report passes the record": ("rd(record) if record else None", "None", "report: K reads"),
     "Y_train MERGED names": ('(BATCH|SKIP|PARK|MERGED|ADMIT|ALREADY)', '(BATCH|SKIP|PARK|ADMIT|ALREADY)', "Y_train named"),
     "S ratchet exit": ("json.loads(out) if rc == 0 else None", "json.loads(out)", "S: a ratchet that exits non-zero"),
@@ -205,6 +205,7 @@ def run(path: Path, mutants: bool = True) -> int:
             with tempfile.TemporaryDirectory() as td:
                 (Path(td) / path.name).write_text(src.replace(old, new))
                 (Path(td) / here.name).write_text(here.read_text())
+                (Path(td) / "round_metrics.py").write_text(path.with_name("round_metrics.py").read_text())
                 p = subprocess.run([sys.executable, "-I", str(Path(td) / here.name)], capture_output=True, text=True, timeout=120)
             killed = p.returncode != 0 and any(ln.startswith("FAIL") and case in ln for ln in p.stdout.splitlines())
             print(("ok   " if killed else "FAIL ") + f"mutant killed: {name} (by '{case}')")
diff --git a/tools/ci/selftest_closures.json b/tools/ci/selftest_closures.json
index 47ab440739..5051a48e90 100644
--- a/tools/ci/selftest_closures.json
+++ b/tools/ci/selftest_closures.json
@@ -235,6 +235,7 @@
     "tools/audit/seat/delivery_row.sh",
     "tools/audit/seat/failure_logs.sh",
     "tools/audit/seat/features_block.py",
+    "tools/audit/seat/finder_overlap.py",
     "tools/audit/seat/fixtures/beat_jobs/**",
     "tools/audit/seat/flow_metrics.py",
     "tools/audit/seat/gantt_drift.py",
@@ -263,6 +264,7 @@
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
+    "tools/audit/seat/plant_recall.py",
     "tools/audit/seat/policy_reread_check.py",
     "tools/audit/seat/postmerge.py",
     "tools/audit/seat/pr_args.sh",
@@ -295,6 +297,8 @@
     "tools/audit/seat/roster_lib.py",
     "tools/audit/seat/roster_queue.py",
     "tools/audit/seat/roster_sync.py",
+    "tools/audit/seat/round_metrics.py",
+    "tools/audit/seat/round_metrics_selftest.py",
     "tools/audit/seat/row_position.py",
     "tools/audit/seat/run_twins.py",
     "tools/audit/seat/scorecard.py",
@@ -3933,6 +3937,7 @@
     "tests/mutation_ledger/killed_by/quiet_windows.py",
     "tests/mutation_ledger/killed_by/repairs.py",
     "tests/mutation_ledger/killed_by/replay_doc.py",
+    "tests/mutation_ledger/killed_by/running_signal.py",
     "tests/mutation_ledger/killed_by/sensor.py",
     "tests/mutation_ledger/killed_by/services.py",
     "tests/mutation_ledger/killed_by/setpoint_check.py",
@@ -4181,6 +4186,7 @@
     "tools/audit/seat/delivery_row.sh",
     "tools/audit/seat/failure_logs.sh",
     "tools/audit/seat/features_block.py",
+    "tools/audit/seat/finder_overlap.py",
     "tools/audit/seat/flow_metrics.py",
     "tools/audit/seat/gantt_drift.py",
     "tools/audit/seat/gh_calls.py",
@@ -4207,6 +4213,7 @@
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
+    "tools/audit/seat/plant_recall.py",
     "tools/audit/seat/policy_reread_check.py",
     "tools/audit/seat/postmerge.py",
     "tools/audit/seat/pr_args.sh",
@@ -4232,6 +4239,8 @@
     "tools/audit/seat/roster_lib.py",
     "tools/audit/seat/roster_queue.py",
     "tools/audit/seat/roster_sync.py",
+    "tools/audit/seat/round_metrics.py",
+    "tools/audit/seat/round_metrics_selftest.py",
     "tools/audit/seat/run_twins.py",
     "tools/audit/seat/scorecard.py",
     "tools/audit/seat/scorecard_selftest.py",
@@ -4754,6 +4763,7 @@
     "tools/audit/seat/delivery_row.sh",
     "tools/audit/seat/failure_logs.sh",
     "tools/audit/seat/features_block.py",
+    "tools/audit/seat/finder_overlap.py",
     "tools/audit/seat/flow_metrics.py",
     "tools/audit/seat/gantt_drift.py",
     "tools/audit/seat/gh_calls.py",
@@ -4782,6 +4792,7 @@
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
+    "tools/audit/seat/plant_recall.py",
     "tools/audit/seat/policy_reread_check.py",
     "tools/audit/seat/postmerge.py",
     "tools/audit/seat/pr_args.sh",
@@ -4814,6 +4825,8 @@
     "tools/audit/seat/roster_lib.py",
     "tools/audit/seat/roster_queue.py",
     "tools/audit/seat/roster_sync.py",
+    "tools/audit/seat/round_metrics.py",
+    "tools/audit/seat/round_metrics_selftest.py",
     "tools/audit/seat/row_position.py",
     "tools/audit/seat/run_twins.py",
     "tools/audit/seat/scorecard.py",
@@ -5262,6 +5275,7 @@
     "tools/audit/seat/delivery_row.sh",
     "tools/audit/seat/failure_logs.sh",
     "tools/audit/seat/features_block.py",
+    "tools/audit/seat/finder_overlap.py",
     "tools/audit/seat/flow_metrics.py",
     "tools/audit/seat/gantt_drift.py",
     "tools/audit/seat/gh_calls.py",
@@ -5289,6 +5303,7 @@
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
+    "tools/audit/seat/plant_recall.py",
     "tools/audit/seat/policy_reread_check.py",
     "tools/audit/seat/postmerge.py",
     "tools/audit/seat/pr_args.sh",
@@ -5428,6 +5443,7 @@
     "tools/audit/archscore/planted/perturb/.gitattributes",
     "tools/audit/archscore/planted/redteam/.gitattributes",
     "tools/audit/round4/**",
+    "tools/audit/round4/**",
     "tools/audit/seat",
     "tools/ci/.gitattributes",
     "tools/coverage/.gitattributes",
@@ -5556,6 +5572,7 @@
     "tools/audit/seat/delivery_row.sh",
     "tools/audit/seat/failure_logs.sh",
     "tools/audit/seat/features_block.py",
+    "tools/audit/seat/finder_overlap.py",
     "tools/audit/seat/fixtures/**",
     "tools/audit/seat/flow_metrics.py",
     "tools/audit/seat/gantt_drift.py",
@@ -5584,6 +5601,7 @@
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
+    "tools/audit/seat/plant_recall.py",
     "tools/audit/seat/policy_reread_check.py",
     "tools/audit/seat/postmerge.py",
     "tools/audit/seat/pr_args.sh",
@@ -5910,6 +5928,7 @@
     "dev/governance/dimensions/**",
     "dev/governance/roles/**",
     "dev/programme/HANDOVER.md",
+    "dev/programme/RULINGS.md",
     "dev/programme/carries/carry-1922.json",
     "dev/programme/carries/carry-2065.json",
     "dev/programme/carries/carry-2066.json",
@@ -6000,6 +6019,7 @@
     ".claude/workflows/wave-3l-groups.json",
     ".claude/workflows/wave-x-groups.json",
     ".cursor/**",
+    ".cursor/**",
     ".github/.gitattributes",
     ".github/actions/.gitattributes",
     ".github/actions/nightly-ha/.gitattributes",
@@ -6016,6 +6036,7 @@
     "dev/archive/.gitattributes",
     "dev/archive/audits/.gitattributes",
     "dev/archive/carries/**",
+    "dev/archive/carries/**",
     "dev/archive/experiments/.gitattributes",
     "dev/archive/experiments/ledger-layout/.gitattributes",
     "dev/archive/handoff/.gitattributes",
@@ -6252,6 +6273,7 @@
     "dev/audit/rounds/round4/D9/reports/.gitattributes",
     "dev/audit/rounds/round4/ledger/.gitattributes",
     "dev/audit/rounds/round5-fix/**",
+    "dev/audit/rounds/round5-fix/**",
     "dev/audit/rounds/round5/.gitattributes",
     "dev/audit/rounds/round5/D0/.gitattributes",
     "dev/audit/rounds/round5/D0/seat-a/.gitattributes",
@@ -6273,9 +6295,12 @@
     "dev/audit/rounds/round5/D2/seat-a/.gitattributes",
     "dev/audit/rounds/round5/D2/seat-b/.gitattributes",
     "dev/audit/rounds/round5/D3/**",
+    "dev/audit/rounds/round5/D3/**",
     "dev/audit/rounds/round5/D4/.gitattributes",
     "dev/audit/rounds/round5/D4/seat-a/.gitattributes",
     "dev/audit/rounds/round5/D7/**",
+    "dev/audit/rounds/round5/D7/**",
+    "dev/audit/rounds/round5/D8/**",
     "dev/audit/rounds/round5/D8/**",
     "dev/audit/rounds/round5/D9/.gitattributes",
     "dev/audit/rounds/round5/D9/seat-b/.gitattributes",
@@ -6298,6 +6323,7 @@
     "dev/audit/rounds/round6/D8/.gitattributes",
     "dev/audit/rounds/round6/D9/.gitattributes",
     "dev/audit/rounds/round7-fix/**",
+    "dev/audit/rounds/round7-fix/**",
     "dev/audit/rounds/round7/.gitattributes",
     "dev/audit/rounds/round7/D0/.gitattributes",
     "dev/audit/rounds/round7/D1/.gitattributes",
@@ -6315,6 +6341,7 @@
     "dev/audit/rounds/round7/D8/.gitattributes",
     "dev/audit/rounds/round7/D9/.gitattributes",
     "dev/audit/rounds/round8-fix/**",
+    "dev/audit/rounds/round8-fix/**",
     "dev/audit/rounds/round8/.gitattributes",
     "dev/audit/rounds/round8/D0/.gitattributes",
     "dev/audit/rounds/round8/D0/s1_logs/.gitattributes",
@@ -6562,6 +6589,8 @@
   "post-merge-bookkeeping": {
    "run_sha": "7f9730626bce97831ee61c879e8b929c037930447bf2bd8c202bbac5e13ade99",
    "files": [
+    "dev/governance/roles/orchestrator.md",
+    "dev/governance/roles/standing-merge.md",
     "tests/layout.py",
     "tools/audit/seat/postmerge.py",
     "tools/audit/seat/record_beat.py",
@@ -6663,6 +6692,7 @@
     "tools/audit/seat/delivery_row.sh",
     "tools/audit/seat/failure_logs.sh",
     "tools/audit/seat/features_block.py",
+    "tools/audit/seat/finder_overlap.py",
     "tools/audit/seat/flow_metrics.py",
     "tools/audit/seat/gantt_drift.py",
     "tools/audit/seat/gh_calls.py",
@@ -6690,6 +6720,7 @@
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
+    "tools/audit/seat/plant_recall.py",
     "tools/audit/seat/policy_reread_check.py",
     "tools/audit/seat/postmerge.py",
     "tools/audit/seat/pr_args.sh",
@@ -6829,6 +6860,7 @@
     "tools/audit/archscore/planted/perturb/.gitattributes",
     "tools/audit/archscore/planted/redteam/.gitattributes",
     "tools/audit/round4/**",
+    "tools/audit/round4/**",
     "tools/audit/seat",
     "tools/audit/seat/.gitattributes",
     "tools/audit/seat/hooks/.gitattributes",
@@ -6932,6 +6964,7 @@
     "tools/audit/seat/gh_read.py",
     "tools/audit/seat/merge_train.py",
     "tools/audit/seat/mutant_run.py",
+    "tools/audit/seat/pr_args.sh",
     "tools/audit/seat/proof_watch.py",
     "tools/audit/seat/ref_privacy.py",
     "tools/audit/seat/review_packet.py",
@@ -7568,6 +7601,7 @@
     "tests/mutation_ledger/killed_by/quiet_windows.py",
     "tests/mutation_ledger/killed_by/repairs.py",
     "tests/mutation_ledger/killed_by/replay_doc.py",
+    "tests/mutation_ledger/killed_by/running_signal.py",
     "tests/mutation_ledger/killed_by/sensor.py",
     "tests/mutation_ledger/killed_by/services.py",
     "tests/mutation_ledger/killed_by/setpoint_check.py",
@@ -7772,6 +7806,7 @@
     ".gitattributes",
     "tests/throwaway_git.py",
     "tools/audit/seat/body_push.sh",
+    "tools/audit/seat/pr_args.sh",
     "tools/audit/seat/ref_privacy.py",
     "tools/audit/seat/tmp_paths.py",
     "tools/audit/seat/wt_sync.sh",
@@ -7801,6 +7836,7 @@
     "tools/audit/archscore/planted/perturb/.gitattributes",
     "tools/audit/archscore/planted/redteam/.gitattributes",
     "tools/audit/round4/**",
+    "tools/audit/round4/**",
     "tools/audit/seat",
     "tools/ci/.gitattributes",
     "tools/ci/fixtures/.gitattributes",
@@ -8303,6 +8339,29 @@
    "objects": false,
    "git": []
   },
+  "round-metrics": {
+   "run_sha": "c227d51175cbb33d863c1d66275c946b02feafc5af8c3e926505148191d2bcd4",
+   "files": [
+    "tests/throwaway_git.py",
+    "tools/audit/machinery_ratchet.py",
+    "tools/audit/seat/round_metrics.py",
+    "tools/audit/seat/round_metrics_selftest.py"
+   ],
+   "probes": [
+    ".",
+    "tests",
+    "tools",
+    "tools/audit"
+   ],
+   "dirs": [
+    "tests",
+    "tools/audit",
+    "tools/audit/seat"
+   ],
+   "index": false,
+   "objects": false,
+   "git": []
+  },
   "ruleset-cut-over-instrument": {
    "run_sha": "8eade8ef98320d326fd120c27f5825f3096030e499f8d8be5f51a2f9a91e073e",
    "files": [
@@ -8327,6 +8386,7 @@
   "scorecard": {
    "run_sha": "3215c0b1f85e68b18dde7d804fdeca68363603e0bf8bb708323038e2801941ac",
    "files": [
+    "tools/audit/seat/round_metrics.py",
     "tools/audit/seat/scorecard.py",
     "tools/audit/seat/scorecard_selftest.py"
    ],
@@ -8429,6 +8489,7 @@
     "dev/governance/roles/**",
     "dev/governance/rules/**",
     "dev/programme/HANDOVER.md",
+    "dev/programme/RULINGS.md",
     "dev/programme/carries/carry-1922.json",
     "dev/programme/carries/carry-2065.json",
     "dev/programme/carries/carry-2066.json",
@@ -8653,6 +8714,7 @@
     "tools/audit/seat/delivery_row.sh",
     "tools/audit/seat/failure_logs.sh",
     "tools/audit/seat/features_block.py",
+    "tools/audit/seat/finder_overlap.py",
     "tools/audit/seat/fixtures/beat_jobs/**",
     "tools/audit/seat/flow_metrics.py",
     "tools/audit/seat/gantt_drift.py",
@@ -8682,6 +8744,7 @@
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
+    "tools/audit/seat/plant_recall.py",
     "tools/audit/seat/policy_reread_check.py",
     "tools/audit/seat/postmerge.py",
     "tools/audit/seat/pr_args.sh",
@@ -8714,6 +8777,8 @@
     "tools/audit/seat/roster_lib.py",
     "tools/audit/seat/roster_queue.py",
     "tools/audit/seat/roster_sync.py",
+    "tools/audit/seat/round_metrics.py",
+    "tools/audit/seat/round_metrics_selftest.py",
     "tools/audit/seat/row_position.py",
     "tools/audit/seat/run_twins.py",
     "tools/audit/seat/scorecard.py",
@@ -9011,6 +9076,10 @@
     "dev/governance/roles/standing-merge.md",
     "dev/governance/roles/standing-roster.md",
     "dev/governance/roles/standing-tick.md",
+    "dev/governance/roles/standing.md",
+    "dev/governance/rules/delivery-status-tracking.md",
+    "dev/governance/rules/gate-scoping.md",
+    "dev/programme/RULINGS.md",
     "tools",
     "tools/audit",
     "tools/audit/seat",
@@ -9134,6 +9203,7 @@
     "tests/mutation_ledger/killed_by/quiet_windows.py/.gitattributes",
     "tests/mutation_ledger/killed_by/repairs.py/.gitattributes",
     "tests/mutation_ledger/killed_by/replay_doc.py/.gitattributes",
+    "tests/mutation_ledger/killed_by/running_signal.py/.gitattributes",
     "tests/mutation_ledger/killed_by/sensor.py/.gitattributes",
     "tests/mutation_ledger/killed_by/services.py/.gitattributes",
     "tests/mutation_ledger/killed_by/setpoint_check.py/.gitattributes",
@@ -9200,6 +9270,7 @@
     "tools/audit/archscore/planted/perturb/.gitattributes",
     "tools/audit/archscore/planted/redteam/.gitattributes",
     "tools/audit/round4/**",
+    "tools/audit/round4/**",
     "tools/audit/seat",
     "tools/ci/.gitattributes",
     "tools/ci/fixtures/.gitattributes",
@@ -9432,6 +9503,7 @@
     "tools/audit/seat/delivery_row.sh",
     "tools/audit/seat/failure_logs.sh",
     "tools/audit/seat/features_block.py",
+    "tools/audit/seat/finder_overlap.py",
     "tools/audit/seat/flow_metrics.py",
     "tools/audit/seat/gantt_drift.py",
     "tools/audit/seat/gh_calls.py",
@@ -9459,6 +9531,7 @@
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
+    "tools/audit/seat/plant_recall.py",
     "tools/audit/seat/policy_reread_check.py",
     "tools/audit/seat/postmerge.py",
     "tools/audit/seat/pr_args.sh",
@@ -9598,6 +9671,7 @@
     "tools/audit/archscore/planted/perturb/.gitattributes",
     "tools/audit/archscore/planted/redteam/.gitattributes",
     "tools/audit/round4/**",
+    "tools/audit/round4/**",
     "tools/audit/seat",
     "tools/ci/.gitattributes",
     "tools/coverage/.gitattributes",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
