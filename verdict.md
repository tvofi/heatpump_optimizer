Design review: approve 6ed233f99cf55aa538c47003b2a9f64d8959ebdb

Reviewed design/R11-OWNER-CARD-EXTERNAL-HEAT at 6ed233f99cf55aa538c47003b2a9f64d8959ebdb (round 1), from a detached worktree. Code read at the note's base origin/main 8ef450936a1786abf4bb9610dc3336da4e77e8de, which is current origin/main. Roster row read at dev/programme/rosters/wave-r11-groups.json:7141 (the owner's item and its added scope).

Checked with no point raised:
- Seam. statusPill (card.js:9758), statusPillHtml (:9786) and statusSignature (:9794) are the pill's one owner. inputProblemState (:10479) is the plan-id twin derivation the note generalises. ExternalHeatBinarySensor (binary_sensor.py:244) is read and not written. Its is_on is external_heat_active (coordinator.py:8088 = detector state.active), and the object id heat_pump_optimizer_external_heat_source comes from _pin_identity (entity.py:293), with the same prefix that PLAN_ID_DERIVE (card.js:3046) strips. No new write path.
- Shape. The external_heat key sits after stale and before heating, and the heating split has three variants. Both are what the roster row names. The docs/dashboard-card.md:75 row has to move with them because the doc names a pill the card stops drawing. Removing status.heating is safe: no reader outside statusPill exists at the base (the only other hits are dev/audit records). Keeping key "heating" keeps the data-status contract at tests/card.mjs:12256 and tests/card_browser.mjs:508.
- Sibling sites. I re-ran the section 4 greps at the base. The www/ directory holds one card file. L("status.*) appears only in statusPill. The twin derivations at :7104 and :7279 resolve plan ids and are not binary twins. "Heating now" appears in docs only at dashboard-card.md:75.
- Evidence plan. Checks (1) to (5) in tests/card.mjs fail at the base, because statusPill has no external_heat branch and only one heating text. The null arms move under the named perturbations. mkStates publishes no external-heat sensor (grep finds no external_heat in tests/card.mjs), so the existing arms are the "absent" control. tests/card_drift.mjs and tests/golden/card_claimed_drift.txt exist and are the right claim file. No solver golden moves.
- Sibling designs. No open design/* note claims statusPill. R11-OUTSIDE-ROOMS-3B touches the card only at reasons/whynow labels (:446, :923, :3510). R11-OWNER-EXTHEAT-OVERRIDE (in revise) changes binary_sensor.py and keeps the sensor's state as raw detection, so this note's choice to read is_on survives it. See the title carry below.
- Cost. One card file, one doc row and two test files fit S.

Routed:
- decision: owner. Roster row :7141 asks for "tests/features.py gets a check with a null control for each of the three variants". The note puts the three variant checks in tests/card.mjs (section 5), where tests/README.md puts card behaviour, and keeps only the backend half in tests/features.py. tests/features.py already spawns subprocesses (e.g. :28959), so a node-driven check is possible. The owner should confirm that card.mjs satisfies the ask. If not, the fixer adds a features.py arm that drives the card through node. That is not a design change.

Carries (for the fixer and fix review):
- The title must hold under the external-heat override that R11-OWNER-EXTHEAT-OVERRIDE proposes. While that override is effective, the sensor stays on but nothing is held back, so "Planned heating is held back ..." would be false. If the override lands first, condition the hold sentence on the sensor's effective-block attribute (suppressing_electric_dhw as that design redefines it) or drop it. Ordering between the two groups is decision: orchestrator. Carry: R11-OWNER-CARD-EXTERNAL-HEAT (item title-under-override)
- The features.py arm reads the card's suffix "by regex" (section 5). Give "_external_heat_source" a named const in card.js, as HEALTH_MODEL_SUFFIX is (:10476), so the regex has one anchor and the planBinaryTwin call reads the same value. Carry: R11-OWNER-CARD-EXTERNAL-HEAT (item suffix-const)
- The note's own carries stand as written: fading-window, title-truth and rig-absent.

Seat token count: not reported by this harness.
