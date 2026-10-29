Fix review: merge cf9341725978140fd3129de026577a68a85eac72

bus-nonce: 2b1971434de36bf05b09c51986e49ab0

## Round

Round 3 of the fix review for #2915 (R10-CONFIGFLOW-C, arms C and C2). Round 2 was blocked class-open at f74f6cbb2 on reauth_confirm's tibber_token. Head measured: cf9341725978140fd3129de026577a68a85eac72. It equals the PR head the body names.

## Block

none

## Findings

- Follow-up, owed after the merge: the finder's harness wizard_widgets.py (sha1 66b390554c0aa54c8960eacb532b04ff827ca8cf) still exists only at commit 3930b421a, not in the tree and not in the group's roster entry on origin/main (dev/programme/rosters/wave-r10-groups.json mentions no wizard_widgets). It is a follow-up that still has to land under dev/audit/rounds/round10/D7/arch2-s5/ with arm D (fix-review.md step 9; fixer.md 18). Its domain also stops at 64 fields and leaves out reauth, which this PR's census covers (66). Carry: R10-CONFIGFLOW-PAGES

## Evidence

- Class closed (step 6). The census domain is every async_step_* of HeatPumpOptimizerConfigFlow: 18 steps, minus the declared NON_FORM_SETUP_STEPS (building, finish_setup, reconfigure). reauth and reauth_confirm are in the domain and render _prefill_row(CONF_TIBBER_TOKEN).widget. I scanned the class (lines 2340-3037) and the module helpers it calls for direct widget construction. The CONF keys still built directly are the six questionnaire keys, CONF_NAME and CONF_DHW_ENABLED, plus non-CONF keys (the quick-setup toggles, prefill_device, two_zone). None of them has an _OPTION_FIELDS row, so no registry-backed setting spells its own widget in setup or reauth. _tibber_token_selector is deleted, so the registry row is the only place that builds the PASSWORD selector.
- Main's config_flow.py change was kept. Main's 58e2d6953 (arm B) folded _options_suggested_numeric and _suggested_entity into _suggested_optional. At the head, _suggested_optional is defined at config_flow.py:893 and used in _field_marker (:1812) and on both wood probes (:1214-1215), with the value side _prefill_row(K).widget. The three-dot diff against main reverts none of arm B. The later automatic merge of main 9071062b0 (ad321ca30, then cf9341725) has the resolution delta ev/resolution_delta.txt: b8ea97aef..head equals 0b17333c2..9071062b0 except for the structure_budgets class_excess_loc ledger line, which is 17875->17870 here against main's 17991->17986. That is the ledger driver carrying main's -5.
- Mutation proof at this head (ev/mutants.txt, my own mutants, each restored afterwards; the worktree is clean). The unmutated baseline is ALL 534 checks PASSED, rc 0.
  - M1, reauth_confirm back to its own PASSWORD TextSelector: killed, 2 spelled twice [reauth, reauth_confirm].
  - M2, the user step's tibber own widget: killed.
  - M3, building_extras COP own _number: killed.
  - M4, quick_setup wood probe own _entity_of: killed.
  - M5, reauth_confirm with no form: killed, 4 checks fail, including census reach unrendered=[reauth, reauth_confirm] and registry-backed fields=64.
  - From M5's 64, the unmutated census reaches 66, which matches the >=66 floor.
- Finder's harness at both ends (ev/finder_harness.txt, copied from 3930b421a, sha1 66b39055..., into a git archive of each tree).
  - Base 9071062b0: spelled_twice=44, other_spelled_twice=20, bump disagree=2.
  - Head: spelled_twice=0, other_spelled_twice=0, bump disagree=0, golden_equal=1.
  - Every body figure for the harness re-derives.
- Merge (step 13): git merge-tree --write-tree origin/main head exits 0 with no conflict (ev/merge_tree.txt).
- Release files and claims (steps 4, 5): VERSION, RELEASE_NOTES.md, the manifest and both claim files are untouched three-dot (0 paths). env_drift --claims-only 9071062b0 reads ok. The three-dot diffstat is 4 files, 195+/218-, which matches the body.
- Metrics (step 14). structure.py at the head reads class_excess_loc=17870 <= 17870, STRUCTURE RATCHET PASSED. The body's 17875 was taken at b8ea97aef, before main's -5 merged, so it is stale for this head, not wrong. archscore --diff origin/main reads dS +0.5850 IMPROVES, literal_clone_copies 185 -> 123, matching the body. The movement comes from deleting the duplicated widget literals.
- Forward-carry (step 10): the arm D items (unused_boundary_imports, literal_clone_copies, device_registry) are present in the R10-CONFIGFLOW-PAGES roster entry on origin/main.
- CI (step 11, ev/ci_state.txt): no check run on this head has concluded failure. tests / coverage, codeql / Analyze (python), governance / instrument-self-tests and one prelude run were still in progress when read, so there is no red check to answer yet.
- Local runs used Python 3.11 with the pinned voluptuous/numpy/scipy from tests/requirements-ci.txt (not hash-installed, because the lock targets 3.14) and PYTHONPATH=tests/hastub.
