# Review packet #3911
head: bff0cd0fc16fe2eaedbfa1d351776c8838ada6c3
base: 1d3077736d4a7ced6ec15d9aec29f6bcf40fbae8

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=139885321149 success
arch-score / arch-score id=139898566572 success
arm id=139883137591 skipped
budget-raise-gate / budget-raise-gate id=139898566501 success
cancel-superseded id=139897135336 success
codeql id=139898569370 skipped
codeql / Analyze (actions) id=139884304299 success
codeql / Analyze (javascript-typescript) id=139884304109 success
codeql / Analyze (python) id=139884304080 success
gate id=139899841634 failure
governance id=139898569144 skipped
governance / env-matrix id=139884304531 success
governance / instrument-self-tests id=139884303836 success
governance / policy-docs id=139884304014 success
governance / record id=139884306915 skipped
governance / wave-script id=139884304001 success
hassfest id=139898568906 skipped
hassfest / hassfest id=139884304034 success
kernel-points id=139898569074 skipped
pr-contract id=139899843261 skipped
prelude id=139897135033 success
refresh id=139897135434 success
sweep-self id=139901173771 skipped
tests id=139898569580 skipped
tests / arch-instrument id=139886820882 success
tests / briefs id=139884303867 success
tests / browser id=139886820930 success
tests / claims-autofix id=139895351106 skipped
tests / closure-scope id=139884304274 success
tests / closures id=139886821173 success
tests / closures-autofix id=139901231153 skipped
tests / coverage id=139886820757 in_progress
tests / fast (3.14) id=139886820771 success
tests / mutation id=139884303833 success
tests / mutation-autofix id=139886877017 skipped
tests / mutation-pins id=139886877066 skipped
tests / nightly-ha id=139886823613 skipped
tests / nightly-status id=139884303993 failure
tests / replay id=139886824122 skipped
tests / typing id=139886820906 success
validate id=139898569044 skipped
validate / validate-hacs id=139884303840 success

## Refusals
none

## Advisories
required-wait: required context `gate` reads concluded failure at bff0cd0fc16fe2eaedbfa1d351776c8838ada6c3 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub:custom_components:tests python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py
             `dev/audit/rounds/round4/D6/claims.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/rounds/round4/D9/h7_memory_gate.py
             `dev/audit/rounds/round4/D9/h7_memory_gate.py` is in the tree at this head
  ok         python3 tests/comment_ratchet.py
             `tests/comment_ratchet.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/deployment_shape.py
             `tests/deployment_shape.py` is in the tree at this head
  ok         node tests/md_tables.mjs
             `tests/md_tables.mjs` is in the tree at this head
  ok         python3 tests/closure.py select --diff <merge-base>
             `tests/closure.py` is in the tree at this head
  unverified git grep -cE "[0-9]+ until "
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tools/pr/app_approve.sh
             `tools/pr/app_approve.sh` is in the tree at this head
  ok         tools/audit/seat/record_beat.py
             `tools/audit/seat/record_beat.py` is in the tree at this head

FIGURES: 12 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (no verdict on verdict/<pr> names the reviewed head bff0cd0fc16fe2eaedbfa1d351776c8838ada6c3, so there is no finding to confirm resolved)

## Three-dot diff
diff --git a/dev/audit/rounds/round3/D5/option_doc_coverage.py b/dev/audit/rounds/round3/D5/option_doc_coverage.py
index 156e408ff3..85360afb32 100644
--- a/dev/audit/rounds/round3/D5/option_doc_coverage.py
+++ b/dev/audit/rounds/round3/D5/option_doc_coverage.py
@@ -24,90 +24,21 @@ RUN (from the repository root, no cd):
 
 Set D5_ROOT=<dir> to point the document side at a copy of the tree.
 
-EXPECTED on this tree (ae36eff printed option_fields_rendered=174 and
-    wood_economics_doc_lines=0; both moved on main before this check;
-    option_fields_undocumented moved 7 -> 0 when #937's reference rows
-    named the last seven fields -- three schedule hours, the three
-    external-heat detection fields, and the split Surcharge per kWh row.
-    #1067 moved the two rendered counts 180 -> 183 and 213 -> 216: three
-    new optional entities_pump pickers -- the space backup heater, the DHW
-    tank booster and the capacity-limited flag. `option_fields_undocumented`
-    stayed 0 because docs/configuration.md gained a row for each in the same
-    commit; had it not, this harness would have printed 3.
-    #1067's learner half then moved them again, 183 -> 185 and 216 -> 218:
-    two more optional entities_pump pickers, the pump's own supply (flow)
-    and return water temperatures. `option_fields_undocumented` stayed 0 for
-    the same reason and under the same condition -- each has a row in
-    docs/configuration.md's Heat pump telemetry table. #1067's solver half
-    moved them once more, 185 -> 186 and 218 -> 219: one boolean on the
-    building page, the flow-curve lift, with its row in docs/configuration.md's
-    heating-system table in the same commit. #1067's silent-mode half moved
-    them again, 186 -> 188 and 219 -> 221: the pump's silent-mode window and
-    the power it keeps, on the fuse-and-peak-guards page, each with its row
-    in docs/configuration.md's Fuse and peak guards table in the same
-    commit. #1067's disinfection half (W1067-G5a) moved them again, 188 -> 189
-    and 221 -> 222: the pump's disinfection switch on the hot water tank page,
-    with its row in docs/configuration.md's Hot water tank and inlet table in
-    the same commit. #1067's frequency half (W1067-G6) moved them again,
-    189 -> 191 and 222 -> 224: the compressor's lowest and highest frequency,
-    on the power and solar sensors page, each with its row in
-    docs/configuration.md's Power and solar sensors table in the same commit.
-    #1067's pre-fill page (W1067-G7) moved them once more, 191 -> 192 and
-    224 -> 225: the Modbus package entity prefix, the one field that page
-    renders unsubmitted, with its row in docs/configuration.md's Pre-fill
-    from a Modbus heat pump table in the same commit. #1067's disinfection
-    control half (W1067-G5b) moved them once more, 192 -> 193 and 225 -> 226:
-    the disinfection switch mode (observe/control), on the hot water tank
-    page, with its row in docs/configuration.md's Hot water tank and inlet
-    table in the same commit. #1067's post-wave follow-on (W1067-POST1) moved
-    them once more, 193 -> 194 and 226 -> 227: the offer switch on the
-    pre-fill page, with its row in docs/configuration.md's Pre-fill from a
-    Modbus heat pump table in the same commit -- the offer page the initial
-    flow shows renders whole fields, never this switch, so it adds nothing
-    here. #1260 moved them once more, 194 -> 195 and 227 -> 228: the
-    by-day toggle on the hot-water page, with its row in
-    docs/configuration.md's Hot water table in the same commit; the seven
-    per-day fields stay hidden while the toggle is off, so they add
-    nothing to this count on an unconfigured render. #1512 moved them once
-    more, 195 -> 196 and 228 -> 229: the peaks-on-different-days toggle on
-    the grid peak tariff page, with its row in docs/configuration.md's Grid
-    peak tariff table in the same commit. #1495 moved them once more,
-    196 -> 197 and 229 -> 230: the mold-floor breach warning margin, on the
-    comfort page's mold group, with its row in docs/configuration.md's
-    Comfort and temperatures table in the same commit. #1588 moved them once
-    more, 197 -> 198 and 230 -> 231: the pump-duty control mode select on
-    the entities_pump page, with its row in docs/configuration.md in the
-    same commit. #1939 moved them once more, 198 -> 199 and 231 -> 232:
-    the debug-collection toggle on the learning page, with its row in
-    docs/configuration.md in the same commit. #2016 moved them once more,
-    199 -> 200 and 232 -> 233: the water flow sensor on the entities_metering
-    page, with its row in docs/configuration.md in the same commit. #1955
-    fold (e) moved them once more, 200 -> 201 and 233 -> 234: the thermal
-    power meter on the entities_metering page, with its row in
-    docs/configuration.md in the same commit. #2261 moved them once more,
-    201 -> 202 and 234 -> 235: the heat energy meter on the
-    entities_metering page, with its row in docs/configuration.md in the
-    same commit. R10-COP-PARTLOAD moved them once more, 202 -> 203 and
-    235 -> 236: the part-load derate number on the thermal model page, with
-    its row in docs/configuration.md in the same commit. R10-WOOD-NOTIFY
-    moved them once more, 203 -> 204 and 236 -> 237: the wood lighting lead
-    time on the wood page, with its row in docs/configuration.md in the same
-    commit. R10-HOTFIX-COP-UNMEASURED moved them once more, 204 -> 207 and
-    237 -> 240: the power and thermal power meter source selects and the
-    hot-water coverage switch on the entities_metering page, with their rows
-    in docs/configuration.md in the same commit. R10-MIN-POWER-FLOOR moved
-    them once more, 207 -> 208 and 240 -> 241: the compressor modulation
-    select on the thermal model page, with its row in docs/configuration.md
-    in the same commit. R10-COMBI-TANK (#3225) moved them 211 -> 216 and
-    244 -> 250: the building page's combi section (one section key, five
-    fields), each with its row. This block is an
-    ASSERTION `tests/harness_headers.py` executes the script against, and it
-    is reached by a shell-out the closure recorder cannot see, so it does not
-    go red on a pull request: it is re-measured in the commit that changes
-    what the script prints, or main's forced-full run finds it):
-    RESULT option_fields_rendered=220 count   (219 until R11-OUTSIDE-ROOMS-P2's room lift toggle; 218 until R11-OUTSIDE-ROOMS-P1's room list; 216 until the two start-hysteresis pickers; 211 until R10-COMBI-TANK's five combi fields; 208 until R10-GENERIC-HEAT-CURVE's three heat_curve fields)
+EXPECTED on this tree. This block is an ASSERTION `tests/harness_headers.py`
+    executes the script against, and it is reached by a shell-out the
+    closure recorder cannot see, so it does not go red on a pull request: it
+    is re-measured in the commit that changes what the script prints, or
+    main's forced-full run finds it. The run also prints
+    option_fields_rendered and option_schema_keys_rendered, derived from the
+    option flow on every run; this header pins neither (FG-1, 2026-11-26):
+    each moved with every option-adding pull request, two such branches
+    re-recorded it each from its own tree, and git merged the two lines as
+    text. A page that fails to render is pinned as
+    option_pages_unrendered=0, and a render that reads no field fails
+    wood_economics_fields_rendered=4. The history of each line is in
+    `git log -L` on this header, not in it:
+    RESULT option_pages_unrendered=0 count
     RESULT option_fields_undocumented=0 count
-    RESULT option_schema_keys_rendered=254 count   (253 until R11-OUTSIDE-ROOMS-P2's room lift toggle; 252 until R11-OUTSIDE-ROOMS-P1's room list; 250 until the two start-hysteresis pickers; 244 until R10-COMBI-TANK; 241 until R10-GENERIC-HEAT-CURVE)
     RESULT wood_economics_fields_rendered=4 count
     RESULT wood_economics_doc_lines=8 count      (tolerance: exact;
     moved 6 -> 8 by #1645/F8.1: the Services section's `simulate_plan`
@@ -282,6 +213,7 @@ def main():
 
     print()
     print(f"RESULT option_pages_rendered={pages_ok} count")
+    print(f"RESULT option_pages_unrendered={len(cf._OPTION_PAGES) - pages_ok} count")
     print(f"RESULT option_schema_keys_rendered={len(rendered)} count")
     print(f"RESULT option_section_or_unlabelled_keys={sectionish} count")
     print(f"RESULT option_fields_rendered={len(rendered) - sectionish} count")
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index fa507417de..950a92049d 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -281,9 +281,9 @@
  {
   "id": "C32",
   "source": "docs/architecture.md",
-  "claim": "45 modules",
+  "claim": "fewer than half of the modules import the `homeassistant` package at module level",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=105 measured=105",
+  "result": "sentence present=True, the module-level importers are fewer than half the package=True",
   "verdict": "true",
   "truth": ""
  },
@@ -292,16 +292,16 @@
   "source": "docs/architecture.md",
   "claim": "the module map is the package's module list",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "on disk=105, listed=105, missing=[], phantom=[]",
+  "result": "missing=[], phantom=[]",
   "verdict": "true",
   "truth": "0 modules are absent from the map: "
  },
  {
   "id": "C34",
   "source": "docs/architecture.md:The Home Assistant boundary",
-  "claim": "the boundary sentence's count of modules importing `homeassistant` at module level",
+  "claim": "the boundary sentence names each module once, and only modules on disk",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=36 measured=36",
+  "result": "named twice=[], not on disk=[]",
   "verdict": "true",
   "truth": ""
  },
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index df07808ef0..e1ed21bac6 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -35,9 +35,9 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C29 | `docs/architecture.md:module map` | config_flow.py -- Setup flow plus 25 option pages behind two menus | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=25 measured=25 | **true** |  |
 | C30 | `docs/configuration.md` | every documented Default (97 rows) is the default the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 97 compared, mismatches=[] | **true** |  |
 | C31 | `docs/configuration.md` | every documented Range (104 rows) is the NumberSelector min/max the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 104 compared, mismatches=[] | **true** |  |
-| C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=105 measured=105 | **true** |  |
-| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=105, listed=105, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
-| C34 | `docs/architecture.md:The Home Assistant boundary` | the boundary sentence's count of modules importing `homeassistant` at module level | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=36 measured=36 | **true** |  |
+| C32 | `docs/architecture.md` | fewer than half of the modules import the `homeassistant` package at module level | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | sentence present=True, the module-level importers are fewer than half the package=True | **true** |  |
+| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
+| C34 | `docs/architecture.md:The Home Assistant boundary` | the boundary sentence names each module once, and only modules on disk | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | named twice=[], not on disk=[] | **true** |  |
 | C35 | `docs/architecture.md:The Home Assistant boundary` | the named modules are the complete set of module-level importers | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | named=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'circulation.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'number_restore.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], measured=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'circulation.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'number_restore.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], unnamed=[] | **true** | unnamed module-level importers:  |
 | C36 | `docs/architecture.md:The Home Assistant boundary` | everything outside the named set is free of homeassistant, so each module can be driven with no Home Assistant running | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 0 modules outside the named set import homeassistant at module level | **true** | modules outside the named set import homeassistant at module level and cannot be imported without it:  |
 | C37 | `docs/architecture.md:module map` | __init__.py -- the 15 services | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=15 measured=15 | **true** |  |
diff --git a/dev/audit/rounds/round4/D6/claims.py b/dev/audit/rounds/round4/D6/claims.py
index 832e339552..7e9e13eb81 100644
--- a/dev/audit/rounds/round4/D6/claims.py
+++ b/dev/audit/rounds/round4/D6/claims.py
@@ -51,99 +51,20 @@ against a document that is CORRECT.
     RESULT claims_false=0
     RESULT claims_stale=0
     RESULT claims_unverifiable=2    (1 with --links; the checker runs the default)
-    RESULT config_defaults_compared=97   (94 until R10-COMBI-TANK's combi rows on
-                                         the building table; 93 until R10-GENERIC-HEAT-CURVE's offset rows; 76 until #937's rows landed; 82
-                                         until #1067's solver half documented
-                                         the flow-curve lift option's default;
-                                         83 until #1067's silent-mode half
-                                         documented the derate's default; 84
-                                         until its frequency half documented
-                                         the two compressor Hz bounds, 86 as
-                                         further rows of that chain landed
-                                         unrecorded, 87 with the pre-fill
-                                         page's "Offer this pre-fill at
-                                         setup" -- a Boolean Default row and
-                                         the only one the diff between the
-                                         frequency merge and this re-record
-                                         adds; 88 with #1260's "Customize by
-                                         weekday" toggle -- an on/off Default
-                                         row whose seven hidden per-day
-                                         fields document no defaults; 89 with
-                                         #1495's mold-floor breach warning
-                                         margin, a NumberSelector Default row
-                                         on the Comfort and temperatures table;
-                                         92 with R10-USER-DOCS-FINAL, which
-                                         gives every options field a row of
-                                         its own under its page; 93 with
-                                         R10-FACTORY-RESET's "What to reset",
-                                         a select Default row on the Reset to
-                                         factory defaults table)
-    RESULT config_ranges_compared=104    (102 until R10-COMBI-TANK's effectiveness
-                                         and potable-volume Range rows; 101 until R10-GENERIC-HEAT-CURVE's band row; 76 until #937's rows landed; 86
-                                         until #1067's silent-mode half
-                                         documented the derate's range; 87
-                                         until its frequency half documented
-                                         the two compressor Hz bounds; 90 with
-                                         #1495's same mold-floor breach warning
-                                         margin, whose 0-5 °C Range row is the
-                                         only one this re-record adds; 92 with
-                                         R10-COP-PARTLOAD's part-load derate
-                                         Range row on the expert thermal-model
-                                         table; 101 with R10-USER-DOCS-FINAL's
-                                         per-field rows on the options pages)
-    RESULT arch_modules_on_disk=105      (104 until the merge joining R11-OUTSIDE-3848's dhw_start.py and R11-OUTSIDE-ROOMS-3B's comfort_floor.py, 103 until either; 102 until R11-OWNER-FLOWCAP's flow_limit.py; 101 until R11-SEAM-cycle-solve's solve_gate.py; 99 until R11-SEAM-actuation-release's duty_ledger.py and number_restore.py; 98 until R11-SEAM-actuation-release's circulation.py; 96 until R11-OUTSIDE-ROOMS-P3's room_history.py and room_record.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 85 until R10-WHY-NOW-WIDGET's slot_drivers.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
-                                         66 until R9 F2.5's batchmath.py;
-                                         65 until #1588's pump_arbiter.py; 64
-                                         until #1408's store.py;
-                                         architecture.md said 45; 56 until
-                                         #1067's learner half added
-                                         flow_lift.py, 57 until its
-                                         silent-mode half added silent_mode.py,
-                                         58 until its disinfection half added
-                                         disinfection.py, 59 until its
-                                         pre-fill half added
-                                         modbus_prefill.py and
-                                         device_prefill.py, 61 until
-                                         name_match.py, 62 until
-                                         prefill_offer.py, each of which the
-                                         module map
-                                         and the opening counts gained in the
-                                         same commit -- this header is an
-                                         ASSERTION tests/harness_headers.py
-                                         executes on every pull request, which
-                                         is true again only since #1148: the
-                                         marker sits at byte 5224 of a file
-                                         the discovery read its first 4000
-                                         bytes of, so nothing compared these
-                                         numbers to a run between 2026-09-17
-                                         and then)
-    RESULT arch_map_listed=105           (104 until the merge joining R11-OUTSIDE-3848's dhw_start.py and R11-OUTSIDE-ROOMS-3B's comfort_floor.py, 103 until either; 102 until R11-OWNER-FLOWCAP's flow_limit.py; 101 until R11-SEAM-cycle-solve's solve_gate.py; 99 until R11-SEAM-actuation-release's duty_ledger.py and number_restore.py; 98 until R11-SEAM-actuation-release's circulation.py; 96 until R11-OUTSIDE-ROOMS-P3's room_history.py and room_record.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
-                                         66 until R9 F2.5's batchmath.py;
-                                         was 45; 11 were missing; 66 with
-                                         #1588's pump_arbiter.py added to
-                                         architecture.md's module map)
-    RESULT arch_map_missing=0            (was 11)
-    RESULT ha_module_level_importers=36  (35 until R11-SEAM-actuation-release's number_restore.py; 34 until its circulation.py; 33 until R11-OUTSIDE-ROOMS-P3's room_record.py; 32 until R10-START-COUNTER-EDGES's running_signal.py; 31 until the supply-hold PR's supply_hold.py; 30 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 28 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 27 until the live-fix wave's early_cutoff.py imports
-                                         homeassistant.core at module level;
-                                         26 until R9-DBG-1's debugger.py imports
-                                         homeassistant.core at module level;
-                                         25 until R9-UX-4's notifier.py; was 21; 22 until #1588's
-                                         pump_arbiter.py imports
-                                         homeassistant.helpers.event at
-                                         module level; #1299's defrost
-                                         normalisation imports
-                                         homeassistant.util.dt at module
-                                         level, and architecture.md moved
-                                         with the census in the same
-                                         commit; 24 since round 9's F3.1:
-                                         away.py reads a typed return time
-                                         in homeassistant.util.dt's zone;
-                                         25 since round 9's F1.6:
-                                         accuracy.py reads
-                                         homeassistant.util.dt's
-                                         DEFAULT_TIME_ZONE for the
-                                         stored-instant rule's zone
-                                         argument)
+    RESULT config_defaults_compared=97
+    RESULT config_ranges_compared=104
+    RESULT arch_map_missing=0
+    RESULT arch_map_phantom=0
+    RESULT ha_importers_unnamed=0
+
+    The run also prints arch_modules_on_disk, arch_map_listed and
+    ha_module_level_importers, derived from the package on every run; this
+    header pins none of them (FG-1, 2026-11-26). Each moved with every
+    module-adding pull request, two such branches re-recorded it each from its
+    own tree, and git merged the two lines as text. What those counts guarded
+    is pinned as the three zeros above, and a derivation that read nothing
+    turns C32, C33 or C35 false, which claims_false=0 refuses. The history of
+    each line is in `git log -L` on this header, not in it.
 
 INSTRUMENTED SYMBOLS (driven, not read):
     heatpump_optimizer.{sensor,binary_sensor,button,climate,switch,datetime}
@@ -792,18 +713,6 @@ claim("C31", "docs/configuration.md",
 _disk = sorted(p.name for p in PKG.glob("*.py"))
 _map = re.search(r"## The module map\n\n```text\n(.*?)\n```", DOCS["architecture.md"], re.S).group(1)
 _listed = sorted(set(re.findall(r"([a-z_0-9]+\.py)", _map)))
-eq("C32", "docs/architecture.md", "45 modules", CMD,
-   int(re.search(r"(\d+) modules, of which", DOCS["architecture.md"]).group(1)),
-   len(_disk),
-   "the package holds {m} Python modules")
-claim("C33", "docs/architecture.md",
-      "the module map is the package's module list", CMD,
-      f"on disk={len(_disk)}, listed={len(_listed)}, "
-      f"missing={sorted(set(_disk) - set(_listed))}, "
-      f"phantom={sorted(set(_listed) - set(_disk))}",
-      "true" if set(_disk) == set(_listed) else "false",
-      f"{len(set(_disk) - set(_listed))} modules are absent from the map: "
-      + ", ".join(sorted(set(_disk) - set(_listed))))
 
 
 def _toplevel(body):
@@ -830,27 +739,46 @@ for _p in sorted(PKG.glob("*.py")):
             _hit |= bool(_n.module) and _n.module.split(".")[0] == "homeassistant"
     if _hit:
         _ha_importers.append(_p.name)
-# #939 re-truthed the boundary sentence ("Exactly ten modules import ..." ->
-# "21 of the 56 modules import ..."), so C34 reads the count the document
-# now states instead of the carried 10 the old sentence spelled out, and
-# C35's named set ends at the list's own full stop -- the `inputs` sentence
-# that follows is a different claim (the one function-level toucher), and
-# sweeping it in counts 22 names against 21 importers. The METRIC is
-# unchanged: the set of modules that import homeassistant at module level.
-_doc_n = re.search(
-    r"(\d+) of the (\d+) modules\s+import `homeassistant` at module level",
-    DOCS["architecture.md"])
+# FG-1 (2026-11-26) took the module counts out of architecture.md: they
+# moved with every module-adding pull request and merged as text into a
+# number neither branch derived. C32 reads the opening sentence's share
+# ("fewer than half of the modules"), C33 the map, C34 the boundary list's
+# own names, and no result carries a count. C35's named set ends at the
+# list's own full stop -- the `inputs` sentence that follows is a different
+# claim (the one function-level toucher). The METRIC is unchanged: the set
+# of modules that import homeassistant at module level.
 _doc_span = re.search(
-    r"\d+ of the \d+ modules\s+import `homeassistant` at module level:\s+(.*?)\.",
+    r"These modules\s+import `homeassistant` at module level:\s+(.*?)\.",
     DOCS["architecture.md"], re.S)
-_doc_named = sorted(
-    {f"{n}.py" for n in re.findall(r"`([a-z_]+)`", _doc_span.group(1))}
-)
-eq("C34", "docs/architecture.md:The Home Assistant boundary",
-   "the boundary sentence's count of modules importing `homeassistant` at "
-   "module level", CMD,
-   int(_doc_n.group(1)) if _doc_n else -1, len(_ha_importers),
-   "{m} modules import homeassistant at module level")
+_bound_names = re.findall(r"`([a-z_]+)`", _doc_span.group(1)) if _doc_span else []
+_doc_named = sorted({f"{n}.py" for n in _bound_names})
+_ha_minority = bool(_ha_importers) and 2 * len(_ha_importers) < len(_disk)
+_open_says = bool(re.search(
+    r"fewer than half of the modules import the\s+`homeassistant` package at "
+    r"module level", DOCS["architecture.md"]))
+claim("C32", "docs/architecture.md",
+      "fewer than half of the modules import the `homeassistant` package at "
+      "module level", CMD,
+      f"sentence present={_open_says}, the module-level importers are fewer "
+      f"than half the package={_ha_minority}",
+      "true" if _open_says and _ha_minority else "false",
+      "" if _ha_minority else "the module-level importers are not a minority "
+      "of the package's modules")
+claim("C33", "docs/architecture.md",
+      "the module map is the package's module list", CMD,
+      f"missing={sorted(set(_disk) - set(_listed))}, "
+      f"phantom={sorted(set(_listed) - set(_disk))}",
+      "true" if _disk and set(_disk) == set(_listed) else "false",
+      f"{len(set(_disk) - set(_listed))} modules are absent from the map: "
+      + ", ".join(sorted(set(_disk) - set(_listed))))
+_doc_dups = sorted({n for n in _bound_names if _bound_names.count(n) > 1})
+_doc_off_disk = sorted(set(_doc_named) - set(_disk))
+claim("C34", "docs/architecture.md:The Home Assistant boundary",
+      "the boundary sentence names each module once, and only modules on disk",
+      CMD, f"named twice={_doc_dups}, not on disk={_doc_off_disk}",
+      "true" if _bound_names and not _doc_dups and not _doc_off_disk else "false",
+      "" if not _doc_dups and not _doc_off_disk
+      else "the boundary list repeats or invents module names")
 claim("C35", "docs/architecture.md:The Home Assistant boundary",
       "the named modules are the complete set of module-level importers",
       CMD, f"named={_doc_named}, measured={_ha_importers}, "
@@ -1449,6 +1377,8 @@ print(f"RESULT claims_unverifiable={counts['unverifiable']} claims")
 print(f"RESULT arch_modules_on_disk={len(_disk)} modules")
 print(f"RESULT arch_map_listed={len(_listed)} modules")
 print(f"RESULT arch_map_missing={len(set(_disk) - set(_listed))} modules")
+print(f"RESULT arch_map_phantom={len(set(_listed) - set(_disk))} modules")
+print(f"RESULT ha_importers_unnamed={len(set(_ha_importers) - set(_doc_named))} modules")
 print(f"RESULT ha_module_level_importers={len(_ha_importers)} modules")
 print(f"RESULT config_defaults_compared={_def_n} rows")
 print(f"RESULT config_ranges_compared={_rng_n} rows")
diff --git a/dev/audit/rounds/round4/D9/h7_memory_gate.py b/dev/audit/rounds/round4/D9/h7_memory_gate.py
index 004a6925ea..1614da75b7 100644
--- a/dev/audit/rounds/round4/D9/h7_memory_gate.py
+++ b/dev/audit/rounds/round4/D9/h7_memory_gate.py
@@ -60,7 +60,7 @@ live-header: this header is maintained against the tree; harness_headers.py exec
 FINAL RESULT (exact; #1005 review follow-up -- the marker above puts
 this harness in tests/harness_headers.py's executed set, which compares
 these lines to the run):
-    RESULT scenarios_recorded=54             (51 until R9 F10.2 added three summer valve plants)
+    RESULT scenarios_recorded=54
     RESULT memory_budget_factor=1.5
     RESULT detection_target=2
     RESULT min_attrib_rss_multiple_required_to_fail=1.5
@@ -69,7 +69,7 @@ these lines to the run):
     RESULT min_traced_multiple_required_to_fail=1.5
     RESULT max_traced_multiple_required_to_fail=1.5
     RESULT scenarios_where_2x_traced_fails=54
-    RESULT scenarios_memory_probed=54        (6 until D9-s3-01: the gate probes every recorded row)
+    RESULT scenarios_memory_probed=54
     RESULT scenarios_never_memory_probed=0
     RESULT attrib_leader_label=typical_slab/winter   (unchanged by R9 F2.5: the review restored the table's memory caps to the base's -- the container's raises were a recording-environment artifact -- keeping only the fields the record measured lower; typical_slab/winter's own rss_attrib_mb is one of those, 16.7 -> 13.7, which moves the failing multiple below)
     RESULT attrib_fail_threshold_mb=20.55       (25.05 at the base; 20.55 at R9 F2.5, 1.5 x the leader's kept-lower 13.7 MiB cap)
diff --git a/dev/programme/delivery/3911.md b/dev/programme/delivery/3911.md
new file mode 100644
index 0000000000..3da4786c9c
--- /dev/null
+++ b/dev/programme/delivery/3911.md
@@ -0,0 +1 @@
+- [#3911](https://github.com/tvofi/heatpump_optimizer/pull/3911) — **open**, test(flow): derive the module and pair counts, carry none in prose (FG-1) (r11-flow-fg1)
diff --git a/docs/architecture.md b/docs/architecture.md
index 35ec85c49c..3266164cc1 100644
--- a/docs/architecture.md
+++ b/docs/architecture.md
@@ -5,7 +5,7 @@ integration does rather than how it is built, start with
 [how-it-works.md](how-it-works.md).
 
 The shape is a thin Home Assistant layer wrapped around a much larger core that
-knows nothing about Home Assistant: 105 modules, of which 36 import the
+knows nothing about Home Assistant: fewer than half of the modules import the
 `homeassistant` package at module level, one more touches it inside a single
 function, and the rest take numbers in and give numbers back. The glue reads
 entity states, writes actuators and persists learned state. Keeping those two
@@ -299,7 +299,7 @@ custom_components/heatpump_optimizer/
 
 ## The Home Assistant boundary
 
-36 of the 105 modules import `homeassistant` at module level: `__init__`,
+These modules import `homeassistant` at module level: `__init__`,
 `config_flow`, `coordinator`, `open_meteo`, `frontend`, the six entity
 platforms `sensor`, `binary_sensor`, `button`, `climate`, `switch`, `datetime`,
 and the supporting modules `accuracy`, `away`, `boost`, `circulation`, `currency`, `debugger`, `defrost`,
@@ -308,7 +308,7 @@ and the supporting modules `accuracy`, `away`, `boost`, `circulation`, `currency
 reaches for `homeassistant.util.dt` inside a function, as the fallback when no
 clock function was injected.
 
-The other 68 modules are deliberately free of it, so each can be driven
+Every other module is deliberately free of it, so each can be driven
 directly by `tests/features.py` with no Home Assistant running. That matters
 because the failure mode of this integration is a *plausible* plan: a detector
 that never fires, or a watchdog that lets a flatline through, produces output
diff --git a/tests/deployment_shape.py b/tests/deployment_shape.py
index b1706cb3cd..2e6b6c7102 100644
--- a/tests/deployment_shape.py
+++ b/tests/deployment_shape.py
@@ -37,103 +37,27 @@ child from ``inspect.getfile``.
 
 COST OF THE SHAPE (#1218, round-5 D3-08). Materialising the shape copies the
 tracked package file by file (``_materialise``, below), and the gate's tracer
-records every read, so this lane's recorded closure is the package: all 124
-files under ``custom_components/heatpump_optimizer/``, Python and non-Python
-alike (123 until the merge joining #3848's ``dhw_start.py`` and R11-OUTSIDE-ROOMS-3B's ``comfort_floor.py``, 122 until either, 121 until R11-OWNER-FLOWCAP's ``flow_limit.py``, 120 until R11-SEAM-cycle-solve's ``solve_gate.py``, 118 until R11-SEAM-actuation-release's ``duty_ledger.py`` and ``number_restore.py``, 117 until its ``circulation.py``, 115 until R11-OUTSIDE-ROOMS-P3's ``room_history.py`` and ``room_record.py``, 114 until R11-OUTSIDE-ROOMS-P1's ``rooms.py``, 113 until R11-OUTSIDE-HONEST-STARTS-RUNS's ``runs.py``, 112 until #3616's ``slab_seed.py``, 111 until R10-START-COUNTER-EDGES's ``running_signal.py``, 110 until
-R10-ADVISOR-STEADY-START's ``whatif.py``, 109 until R10-DUTY-SWITCH-PLANNER-PRICE's
-``duty_legs.py``, 108 until the supply-hold PR's ``supply_hold.py``, 107 until
-R10-DUTY-SWITCH-RESTART-LEARNING's ``duty_switch.py``, 78 until R9 F2.5's ``batchmath.py``, 79 until R9 UI-1's six brand
-images, 85 until R9 EG-B5's ``dhw_planner.py``, 86 until R9-EG-B3a's
-``payload.py``, 87 until R9-UX-4's ``notifier.py``, 88 until R9-SW-1's
-``quiet_windows.py``, 89 until R9-DBG-1's ``debugger.py``, 90 until
-R9-EG-B11's ``entry_config.py``, 91 until R9-UX-9's ``flow_meter.py``, 92
-until the live power clamp's ``draw_range.py``, 93 until the live-fix wave's
-``early_cutoff.py``, 94 until R10-FAHRENHEIT's ``issues.py``, 95 until
-R10-N-log-flood's ``log_latch.py``, 96 until R10-PUMP-MODEL's ``plan_step.py``, 97 until R10-DIAG-REPLAY's ``replay_doc.py``, 98 until R10-ADVISOR's ``price_tiles.py``, 99 until R10-LEARNER-ETA's ``learner_progress.py``, 100 until R10-HEAT-METER's ``heat_energy.py``, 101 until R10-ADVISOR-WHATIF's ``plan_slots.py``, 102 until R10-GRADE-DRIVERS's ``driving_grade.py``, 103 until R10-WHY-NOW-WIDGET's ``slot_drivers.py``, 104 until R10-I18N-DE's ``translations/de.json``, 105 until R10-GENERIC-HEAT-CURVE's ``heat_curve.py`` and ``off_restore.py``) -- one of the three closures in ``tests/closures.json`` that reach
-every production file; the second is ``tests/arch_score_head.py``'s
-(R9-EG-A1), which measures today's tree with the architecture score and so
-must read all of it, and the third is ``tests/entities.py``'s (round 9),
-which drives the CI ratchet's archscore measurement and so opens the package
-the way this lane's recorder does. A diff touching any production file
-therefore selects this lane. That is a selection cost, not a
-duplicate-assertion one: the same
-recording finds 190 of the 561 script pairs (34 choose 2) sharing 0.80 or more
-of their production-module closure (186 on #3863's branch and 182 on
-main before the merge joining them, main's R11-SEAM-entity-service services.yaml
-having taken config_flow_steps.py's pairs with debug_collect.py and wood_advisor.py
-under 0.80, 184 on main and 180 on that branch before it landed; on the #3863
-branch, 184 on each side before the merge joining
-R11-OWNER-FLOWCAP's flow_limit.py and #3848's dhw_start.py (R11-OUTSIDE-ROOMS-3B's comfort_floor.py on that branch), which put
-card_drift.mjs and wood_advisor.py each with features.py at the 0.80 floor; 182
-before flow_limit.py on main and dhw_start.py on its branch (comfort_floor.py on rooms-3b's) each lifted
-env_drift.py/manual_plan.py and golden.py/manual_plan.py to 0.80; 169 of 528 before R11-SEAM-tests's
-cycle_lane.py, whose closure opens the whole package, and 180 on its branch
-before the merge bringing R11-SEAM-actuation-release's three production
-modules; 167 before both; 164 on each side before the merge joining
-R11-OUTSIDE-ROOMS-P1's rooms.py, read by every closure that imports the
-coordinator, the input reader, the config flow or the sensor platform, and
-R11-OUTSIDE-HONEST-STARTS-RUNS's recordings, which joined
-config_flow_steps.py/debug_collect.py at 0.80; 162 before #3616 re-recorded the
-closures that import the coordinator), all 190 among the 435 pairs whose two
-scripts each have a non-empty production closure (``tests/arch_score.py``,
-``tests/ha_contract.py``, ``tests/layout.py`` and ``tests/md_tables.mjs`` have none;
-``tests/harness_headers.py`` joined the comparable set, and ten pairs, when
-R9 F10.3's strace instrument recorded its round-harness children's imports;
-doc_claims.py/manual_plan.py left it, 0.81 to 0.79, when R9 F10.4's I5 arms
-added icons.json and services.yaml to doc_claims.py's closure; #1935's
-tests/boost_drift_replay.py joined, adding 6 pairs at >= 0.80;
-``tests/debug_collect.py`` joined when the debug-collector pin driver was
-recorded, adding 7 pairs at >= 0.80; the live-fix wave's early_cutoff.py,
-R9-UX-9's flow_meter.py and the live power clamp's draw_range.py, each read
-by every full-coverage closure, lifted the census from 120 to 123 pairs at
-the 0.80 floor; round 9's CI ratchet then grew entities.py's closure past
-doc_claims.py's and harness_headers.py's, moving the count from 123 to 122
-and putting entities.py itself in the full-coverage set; R10-ARCH-SHAPES's
-pins (#2819) grew guard_pins.py's closure to coordinator.py and sensor.py,
-adding its 9 pairs at >= 0.80 and moving the count from 122 to 131;
-R10-WOOD-NOTIFY's wood_advisor.py closure gained binary_sensor.py, lifting
-its pairs with finite_boundary.py, structure.py and typing_ruler.py from
-0.798 to 0.81 and the count from 131 to 134; R10-GRADE-DRIVERS's
-driving_grade.py re-recorded every closure that imports the coordinator,
-putting block_duty.py and boost_drift_replay.py each with finite_boundary.py
-and structure.py, plan_view.py with both, and card.mjs with features.py at
-the 0.80 floor, and the count from 134 to 141; the bot's closure re-record
-then added driving_grade.py to typing_ruler.py's closure, which had been
-recorded without it, putting block_duty.py, boost_drift_replay.py and
-plan_view.py each with typing_ruler.py at the 0.80 floor, and the count from
-141 to 144; R10-WHY-NOW-WIDGET's slot_drivers.py, imported by optimizer.py,
-joined the 27 closures that measure the optimizer, and the count from 144
-to 145; R10-I18N-DE's ``translations/de.json``, read by every closure that
-reads the catalogues, moved card.mjs with config_flow_steps.py from 0.800 to
-0.802 and left the count at 145; R10-GENERIC-HEAT-CURVE's heat_curve.py and
-off_restore.py, read by every closure that imports the coordinator, moved it
-from 145 to 146; R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py, read by every
-closure that imports the arbiter, the sensor platform or the store, from 146 to 148; the supply-hold PR's
-supply_hold.py, read by every closure that imports the coordinator, from 148 to 154;
-R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py, read by every closure that
-imports the optimizer or the arbiter, left it at 154: measured alone on the
-148 recording it moves the same count to 154, the pairs it lifts being ones
-supply_hold.py lifts too; R10-ADVISOR-STEADY-START's whatif.py, read by every
-closure that imports the coordinator, left it at 154 too;
-R10-OUTSIDE-DHW-START-HYSTERESIS's block_duty.py check that the coordinator's
-input read puts the pump's start hysteresis on the state builds a coordinator,
-which grew that script's closure from 74 to 91 production files (75 to 92
-beside whatif.py): nine pairs joined at the 0.80 floor and one left, the
-count from 154 to 162; #3616's re-record moved it to 163, and
-R11-OUTSIDE-HONEST-STARTS-RUNS's recordings, which add runs.py, to 164; 184 on main after R11-OUTSIDE-ROOMS-3B's comfort_floor.py, and 190 on the merge joining that main to #3848's branch, re-derived from the merged closures).
-Eighteen of the pairs sit at exactly 1.00 -- arch_score_head.py/deployment_shape.py,
-arch_score_head.py/entities.py and deployment_shape.py/entities.py
-(98 shared production files each), doc_claims.py/harness_headers.py
-(88), structure.py/typing_ruler.py, finite_boundary.py/structure.py and
-finite_boundary.py/typing_ruler.py (80 each), plan_view.py/solar_alignment.py,
-boost_drift_replay.py/plan_view.py and boost_drift_replay.py/solar_alignment.py
-(62 each), the optimality.py/validate.py/edge.py/backtest.py four (22, six
-pairs), golden.py/env_drift.py (94), card.mjs/card_drift.mjs (61) -- and which
-mutants each script actually kills
-was never measured, so nothing here says those runs are redundant either:
-the pre-screen stops at the first killer, and where a narrower closure here
-or a merged script for an exactly-equal pair would pay is recorded rather
-than attempted (#1218).
+records every read, so this lane's recorded closure is the package: every file
+under ``custom_components/heatpump_optimizer/``, Python and non-Python alike --
+one of the three closures in ``tests/closures.json`` that reach every
+production file; the second is ``tests/arch_score_head.py``'s (R9-EG-A1),
+which measures today's tree with the architecture score and so must read all
+of it, and the third is ``tests/entities.py``'s (round 9), which drives the CI
+ratchet's archscore measurement and so opens the package the way this lane's
+recorder does. A diff touching any production file therefore selects this
+lane. That is a selection cost, not a duplicate-assertion one: the same
+recording pairs scripts sharing 0.80 or more of their production-module
+closure, among the pairs whose two scripts each have a non-empty production
+closure (``tests/arch_score.py``, ``tests/ha_contract.py``, ``tests/layout.py``
+and ``tests/md_tables.mjs`` have none), and some pairs share exactly the same
+production files. ``tests/entities.py``'s #1218 block derives and prints every
+one of those numbers and the exactly-equal pairs; this note carries none of
+them, because each moves with any recording that adds a production module and
+two branches merging their counts as text left a number neither tree derives
+(FG-1). Which mutants each script actually kills was never measured, so
+nothing here says those runs are redundant either: the pre-screen stops at the
+first killer, and where a narrower closure here or a merged script for an
+exactly-equal pair would pay is recorded rather than attempted (#1218).
 
     python tests/deployment_shape.py
 """
diff --git a/tests/doc_claims.py b/tests/doc_claims.py
index 7d7706239b..9acbb6a9f3 100644
--- a/tests/doc_claims.py
+++ b/tests/doc_claims.py
@@ -1277,6 +1277,23 @@ _PROSE_COUNT_SHAPES: tuple[tuple[str, re.Pattern[str], tuple[tuple[str, str], ..
      (("n", "modules"),)),
 )
 
+# FG-1 (2026-11-26): the shapes whose count the reader corpus must NOT state.
+# A module count moved with every module-adding pull request. Two branches
+# each re-derived it, and git merged their sentences as text into a number
+# neither derived. tests/entities.py's #939 block and claims.py derive and
+# print the counts. The shapes stay above, so a module count written back is
+# still claimed and compared, and is refused besides.
+_ABSENT_COUNT_SHAPES = frozenset({
+    "the Home-Assistant-free module count",
+    "the module-level importer count",
+    "the opening module total and its importer count",
+    "the module total",
+})
+_ABSENT_QUANTITIES = frozenset({
+    template for name, _pattern, quantities in _PROSE_COUNT_SHAPES
+    if name in _ABSENT_COUNT_SHAPES for _group, template in quantities
+})
+
 
 def _imports_homeassistant(node: ast.AST) -> bool:
     """Is this statement an import of the ``homeassistant`` package?"""
@@ -1388,7 +1405,7 @@ def prose_count_scan(
                         )
     unread = [
         name for index, (name, _pattern, _quantities) in enumerate(_PROSE_COUNT_SHAPES)
-        if not seen[index]
+        if not seen[index] and name not in _ABSENT_COUNT_SHAPES
     ]
     return rows, unread
 
@@ -1412,6 +1429,7 @@ def check_prose_tree_counts() -> None:
     tree_wide = ("modules", "modules_importing_homeassistant",
                  "modules_free_of_homeassistant", "services",
                  "options_pages", "editable_options_pages")
+    print("  derived: " + ", ".join(f"{key}={facts[key]}" for key in tree_wide))
     R.check(
         "every tree-wide quantity a count shape names measured positive "
         "(anchor: a measurement that read nothing cannot pass a census)",
@@ -1436,6 +1454,25 @@ def check_prose_tree_counts() -> None:
         not unread,
         f"no occurrence of: {unread}",
     )
+    carried = [row for row in claims if row[2] in _ABSENT_QUANTITIES]
+    R.check(
+        "the reader corpus states no module count; entities.py and claims.py "
+        "derive and print it (FG-1)",
+        bool(_ABSENT_QUANTITIES) and not carried,
+        "; ".join(f"{document}:{line} {quantity}={stated}"
+                  for document, line, quantity, stated, _measured in carried),
+    )
+    # Null control: a module count planted in a reader document is read by its
+    # shape and refused, true or not -- the refusal is keyed on the shape, so
+    # a count that happens to equal the tree still lands red.
+    planted, _ = prose_count_census(
+        {"probe.md": f"The package holds {facts['modules']} modules."}, facts)
+    R.check(
+        "a true module count planted in a reader document is refused "
+        "(null control)",
+        [row[2] for row in planted if row[2] in _ABSENT_QUANTITIES] == ["modules"],
+        repr(planted),
+    )
     wrong = [row for row in claims if row[4] != row[3]]
     R.check(
         "every count of a tree-measurable set the reader corpus states is "
@@ -1479,12 +1516,13 @@ def check_prose_tree_counts() -> None:
         repr(named),
     )
     # Null control: deleting a reader document refuses the shapes only it
-    # states. The arm cannot go green by reading less.
+    # states. The arm cannot go green by reading less. README.md is the one
+    # document stating the editable-page and named-field shapes.
     _, lost = prose_count_census(
-        {name: text for name, text in CORPUS.items() if name != "architecture.md"}, facts
+        {name: text for name, text in CORPUS.items() if name != "README.md"}, facts
     )
     R.check(
-        "deleting architecture.md refuses the module shapes only it states "
+        "deleting README.md refuses the shapes only it states "
         "(null control: failure-closed, not silent)",
         bool(lost),
         f"unread after the deletion: {lost}",
diff --git a/tests/entities.py b/tests/entities.py
index f3d2a59eae..33e8a874c7 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -1178,15 +1178,27 @@ _arch_anywhere = sorted(
     if any(_arch_ha_import(n) for n in ast.walk(ast.parse(p.read_text())))
 )
 
-_arch_open = _re.search(r"(\d+) modules, of which\s+(\d+) import", _arch)
-R.check(
-    "architecture.md's opening counts name the package it describes",
+# FG-1 (2026-11-26): the prose states no module count. A count here moved
+# with every module-adding pull request. Two such branches each re-derived
+# it, and git merged their sentences as text. The counts are derived and
+# printed here instead, and doc_claims.py refuses a module count anywhere in
+# the reader corpus.
+print(
+    f"  derived: package modules={len(_arch_disk)}, importing homeassistant "
+    f"at module level={len(_arch_modlevel)}, touching it anywhere="
+    f"{len(_arch_anywhere)}, free of it={len(_arch_disk) - len(_arch_anywhere)}"
+)
+_arch_open = _re.search(
+    r"fewer than half of the modules import the\s+`homeassistant` package at "
+    r"module level", _arch)
+R.check(
+    "architecture.md's opening share of homeassistant importers is the tree's",
     _arch_open is not None
-    and int(_arch_open.group(1)) == len(_arch_disk)
-    and int(_arch_open.group(2)) == len(_arch_modlevel),
-    f"architecture.md says {_arch_open.groups() if _arch_open else '?'}; the "
-    f"package holds {len(_arch_disk)} modules, {len(_arch_modlevel)} of them "
-    f"importing homeassistant at module level",
+    and 0 < len(_arch_modlevel)
+    and 2 * len(_arch_modlevel) < len(_arch_disk),
+    f"opening sentence found={_arch_open is not None}; the package holds "
+    f"{len(_arch_disk)} modules, {len(_arch_modlevel)} of them importing "
+    f"homeassistant at module level",
 )
 
 _arch_map = _re.search(r"## The module map\n+```text\n(.*?)\n```", _arch, _re.S)
@@ -1206,22 +1218,20 @@ R.check(
 # follows is about a different claim (the one function-level toucher, pinned
 # below), and sweeping it in would make 22 names out of 21 importers.
 _arch_bound = _re.search(
-    r"(\d+) of the (\d+) modules\s+import `homeassistant` at module level:\s+(.*?)\.",
+    r"These modules\s+import `homeassistant` at module level:\s+(.*?)\.",
     _arch, _re.S,
 )
 _arch_named = (
-    sorted(set(_re.findall(r"`([a-z_]+)`", _arch_bound.group(3))))
+    sorted(set(_re.findall(r"`([a-z_]+)`", _arch_bound.group(1))))
     if _arch_bound is not None
     else []
 )
 R.check(
     "architecture.md's HA boundary names exactly the module-level importers",
     _arch_bound is not None
-    and int(_arch_bound.group(1)) == len(_arch_modlevel)
-    and int(_arch_bound.group(2)) == len(_arch_disk)
+    and bool(_arch_modlevel)
     and _arch_named == _arch_modlevel,
-    f"documented {_arch_bound.group(1) if _arch_bound else '?'} of "
-    f"{_arch_bound.group(2) if _arch_bound else '?'}, named {_arch_named}; "
+    f"named {len(_arch_named)}: {_arch_named}; "
     f"the AST walk finds {len(_arch_modlevel)}: {_arch_modlevel}",
 )
 
@@ -1237,16 +1247,18 @@ R.check(
     f"{_arch_touchers}",
 )
 
-_arch_free = _re.search(
-    r"The other (\d+) modules are deliberately free", _arch
-)
+_arch_free = _re.search(r"Every other module is deliberately free", _arch)
 R.check(
-    "architecture.md's HA-free count is the tree's",
+    "architecture.md's HA-free remainder is the tree's: every module but the "
+    "named importers and the one toucher",
     _arch_free is not None
-    and int(_arch_free.group(1)) == len(_arch_disk) - len(_arch_anywhere),
-    f"architecture.md says {_arch_free.group(1) if _arch_free else '?'}; "
-    f"{len(_arch_disk)} modules less {len(_arch_anywhere)} that touch "
-    f"homeassistant anywhere leaves {len(_arch_disk) - len(_arch_anywhere)}",
+    and len(_arch_disk) - len(_arch_anywhere)
+    == len(_arch_disk) - len(_arch_modlevel) - 1 > 0,
+    f"sentence found={_arch_free is not None}; {len(_arch_disk)} modules less "
+    f"{len(_arch_anywhere)} that touch homeassistant anywhere leaves "
+    f"{len(_arch_disk) - len(_arch_anywhere)}, against "
+    f"{len(_arch_disk) - len(_arch_modlevel) - 1} outside the named set and "
+    "the toucher",
 )
 
 _arch_pages = _re.search(
@@ -18162,12 +18174,12 @@ R.check(
 # #1218 (D3-08): the deployment-shape lane's measured closure is the whole
 # tracked package -- it materialises the package file by file, and the
 # gate's tracer records every read -- so every diff touching any production
-# file selects the lane. The same recording pairs 53 of the 276 scripts at
-# 0.80 or more of shared production-module closure. The numbers are
-# re-derived here exactly as dev/audit/rounds/round5/D3/resource_r5.py derived
-# them (Jaccard over the closure files under
-# custom_components/heatpump_optimizer/, empty sets skipped), and the lane's
-# docstring records them as this repository's selection-cost note. A
+# file selects the lane. The same recording pairs scripts at 0.80 or more of
+# shared production-module closure. The numbers are derived here exactly as
+# dev/audit/rounds/round5/D3/resource_r5.py derived them (Jaccard over the
+# closure files under custom_components/heatpump_optimizer/, empty sets
+# skipped) and printed below; the lane's docstring is this repository's
+# selection-cost note and names this block as their source. A
 # SELECTION cost only: which mutants each script kills was never measured
 # (the pre-screen stops at the first killer), so nothing claims two
 # overlapping scripts are redundant.
@@ -18230,25 +18242,39 @@ R.check(
     f"it={_D308_SELECTED} -- this is the cost the note beside the lane "
     "records",
 )
-# The note carries the derived numbers, so a re-record that moves them fails
-# HERE instead of leaving stale prose behind. The text is whitespace-
-# normalised first so a future re-wrap of the paragraph cannot flip these.
+# The numbers are derived and printed HERE, never carried in the note
+# (FG-1, 2026-11-26). The pair count is a threshold function of the whole
+# recording, so it does not add across a merge. Two branches each re-derived
+# it, and git merged the two sentences as text. The merged tree derived a
+# third number (#3838, #3866, #3870). The note names the cost and this block;
+# a count written back into it is refused. The text is whitespace-normalised
+# first so a re-wrap of the paragraph cannot flip these.
+_D308_SAME = sorted(
+    (_a, _b, _n) for _jac, _a, _b, _n in _D308_PAIRS if _jac == 1.0)
+print(
+    f"  derived (#1218): the lane reaches all {len(_D308_PROD)} production "
+    f"files; {len(_D308_PAIRS)} of the {_D308_TOTAL} script pairs share >= 0.80 "
+    f"of their production closure, among {_D308_COMPARABLE} comparable pairs; "
+    f"{len(_D308_SAME)} at exactly 1.00: "
+    + ", ".join(f"{_a}/{_b} ({_n})" for _a, _b, _n in _D308_SAME)
+)
 _D308_DS_TEXT = " ".join((_closure.ROOT / _D308_DS).read_text().split())
+_D308_CARRIED = _re.findall(
+    r"\ball \d+ files\b|\b\d+ of the \d+ script pairs\b|\b\d+ pairs\b"
+    r"|\b\d+ until\b|\b\d+ shared production files\b",
+    _D308_DS_TEXT,
+)
 R.check(
-    "and the lane's docstring records those measured numbers as the "
-    "selection-cost note (#1218)",
+    "and the lane's docstring is the selection-cost note, naming this block "
+    "as the source of its numbers and carrying none of them (#1218, FG-1)",
     all(_s in _D308_DS_TEXT for _s in (
-        "D3-08", "#1218", "selection cost",
-        f"all {len(_D308_PROD)} files",
-        f"{len(_D308_PAIRS)} of the {_D308_TOTAL}",
-        f"{_D308_COMPARABLE} pairs",
+        "D3-08", "#1218", "selection cost", "tests/entities.py",
     ))
-    and all(_e in _D308_DS_TEXT for _e in _D308_EMPTY),
-    "the note cites numbers this tree derives: "
-    f"{len(_D308_PROD)} production files; {len(_D308_PAIRS)} of "
-    f"{_D308_TOTAL} pairs at >= 0.80; {_D308_COMPARABLE} pairs comparable; "
-    f"no production closure in {_D308_EMPTY}; missing markers -> "
-    f"{[s for s in ('D3-08', '#1218', 'selection cost', 'all %d files' % len(_D308_PROD), '%d of the %d' % (len(_D308_PAIRS), _D308_TOTAL), '%d pairs' % _D308_COMPARABLE) if s not in _D308_DS_TEXT]}",
+    and all(_e in _D308_DS_TEXT for _e in _D308_EMPTY)
+    and not _D308_CARRIED,
+    "missing markers -> "
+    f"{[s for s in ('D3-08', '#1218', 'selection cost', 'tests/entities.py') if s not in _D308_DS_TEXT]}; "
+    f"no production closure in {_D308_EMPTY}; hand-kept counts -> {_D308_CARRIED}",
 )
 # The predicate itself, on synthetic closures built from real production
 # names: equal sets count, disjoint and below-boundary do not, an exactly
diff --git a/tools/audit/prose_counts_census.py b/tools/audit/prose_counts_census.py
index 87ddffa9cc..802266a2b8 100644
--- a/tools/audit/prose_counts_census.py
+++ b/tools/audit/prose_counts_census.py
@@ -5,7 +5,7 @@
     ... --rows   # each unread row with its line, not only the per-noun totals
 
 The rule that enumerates the stale-prose-count class's seams. `tests/doc_claims`
-`check_prose_tree_counts` reads eleven count SHAPES over the reader corpus and
+`check_prose_tree_counts` reads the count SHAPES over the reader corpus and
 compares each to a measurement the tree derives; this command enumerates every
 `<number> <plural noun>` the corpus states, subtracts the spans those shapes
 claimed, and prints what is left against a disposition. A noun with no entry is

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
