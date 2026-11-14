# Review packet #3564
head: d6a7b00bba95068c5236805aa0a740b792d0d954
base: c987209cc7a891e0e4066d4ad8dc5cf55357c5ae

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=132311319749 success
arch-score / arch-score id=132309879499 success
arm id=132307572822 skipped
budget-raise-gate / budget-raise-gate id=132309879837 success
cancel-superseded id=132307574114 success
codeql id=132309179012 skipped
codeql / Analyze (actions) id=132309879485 success
codeql / Analyze (javascript-typescript) id=132309879464 success
codeql / Analyze (python) id=132309879427 success
gate id=132311468783 in_progress
governance id=132309179903 skipped
governance / delivery-status id=132309879817 success
governance / delivery-status-publish id=132309881208 skipped
governance / env-matrix id=132309879777 success
governance / instrument-self-tests id=132309879823 in_progress
governance / policy-docs id=132309879605 success
governance / record id=132309881344 skipped
governance / wave-script id=132309879692 success
hassfest id=132309179049 skipped
hassfest / hassfest id=132309879419 success
kernel-points id=132309881041 skipped
pr-contract id=132311470557 skipped
prelude id=132307573895 success
refresh id=132307574062 success
tests id=132309179020 skipped
tests / arch-instrument id=132310365219 in_progress
tests / briefs id=132309879564 success
tests / browser id=132310365290 queued
tests / closure-scope id=132309879647 success
tests / closures id=132310365391 queued
tests / coverage id=132310365318 queued
tests / fast (3.14) id=132310365551 queued
tests / mutation id=132309879613 success
tests / mutation-autofix id=132310947824 skipped
tests / mutation-pins id=132310948020 skipped
tests / nightly-ha id=132310366857 skipped
tests / nightly-status id=132309879657 failure
tests / replay id=132310366316 skipped
tests / typing id=132310365270 queued
validate id=132309180399 skipped
validate / validate-hacs id=132309879473 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 132309879823: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
none

## carry_audit at the head
NOTE body item 2de47db2: R11-INTAKE-R10-RESIDUE
NOTE body item 9ae2be30: R11-INTAKE-R10-RESIDUE
NOTE body item 55051373: R11-INTAKE-R10-RESIDUE
NOTE body item 4ab03548: R11-INTAKE-R10-RESIDUE
NOTE body item af528396: R11-INTAKE-R10-RESIDUE
NOTE body item 31878861: R11-INTAKE-R10-RESIDUE
NOTE body item 734b6d33: R11-INTAKE-R10-RESIDUE
NOTE body item 452440fb: R11-INTAKE-R10-RESIDUE
NOTE body item 86aa4096: R11-INTAKE-R10-RESIDUE
NOTE body item a64a0285: R11-INTAKE-R10-RESIDUE
NOTE body item b30f48ba: R11-INTAKE-R10-RESIDUE
NOTE body item 6f36db0c: R11-INTAKE-R10-RESIDUE
NOTE body item bb5336e8: R11-INTAKE-R10-RESIDUE
CARRY-AUDIT: 13 finding item(s): 13 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 dev/audit/rounds/round10/D6/flow_claims.py enumerate | tail -4
             `dev/audit/rounds/round10/D6/flow_claims.py` is in the tree at this head
  ok         python3 dev/audit/rounds/round10/D6/flow_claims.py distinct | tail -1
             `dev/audit/rounds/round10/D6/flow_claims.py` is in the tree at this head
  unverified python3 -c "import json; print(json.load(open('dev/audit/rounds/round10/D6/flow-claims.json'))['verdicts'])"
             python3 runs an inline script rather than a file
  unverified git diff --stat origin/main...HEAD -- custom_components/heatpump_optimizer/strings.json custom_components/heatpump_optimizer/translations/
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         GOLDEN_MODE=drift python3 tests/golden.py
             `tests/golden.py` is in the tree at this head
  ok         node tests/card.mjs
             `tests/card.mjs` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  unverified git merge-tree --write-tree origin/main HEAD
             `git merge-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 6 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: delta (later round over the reviewed head 9a524d703f3a25325c71f1fe888a35ab53147189)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at 9a524d703f3a25325c71f1fe888a35ab53147189
Fix review: blocked 9a524d703f3a25325c71f1fe888a35ab53147189 ci-red: the gate is red at this head on tests / fast (3.14), whose failing features.py check fails identically at main 50373173; the delta itself is clean

bus-nonce: d82428ee2068935c8dab85be3b59d4e4

## Block

- `merge_train.py classify` returns RED at this head (`red: gate`). The red job is `tests / fast (3.14)`, which is in the owed-reds set. The failing script is `tests/features.py`: one check fails, "a charge-start dip that recovers is learned as neither a draw nor usage, and a draw that does not recover keeps what main booked". It fails identically at main 50373173, and this PR changes no `.py` file that the check reads. The red is inherited from main, not caused by this PR, and the review of the delta is otherwise complete with nothing open against it (Evidence). A red CI never carries, so I cannot return `merge` over it. Once main's failure is fixed and the gate is green at a head whose delta is only that main merge, `review_carry.py` should carry this review. The PR body's `## Red checks` answers `tests / fast (3.14)` for the earlier head 67ab6ad0 (doc_claims). The red at this head has a different cause, and it is main's.

Round 2 (a delta round over the reviewed head 8c9dc2697a74ebb036f4dddb8557edd57664d8bd, which had a merge verdict). The review packet's scope line reads `delta`. The delta is `git diff 8c9dc269 9a524d70`. The branch's own commits in it are 59bb0506 (the pin repoint) and 67ab6ad0 (the delivery row). The rest is four merges of main: 5d890b3e, 0d29eb62, 6ebbd4e5 and 9a524d70. I measured head 9a524d703f3a25325c71f1fe888a35ab53147189, and the PR body's `## Head` names the same SHA. Role contracts: `git diff $(git merge-base origin/main HEAD)..origin/main -- dev/governance/roles/` is empty, so the contract is current.

## Findings

- Still open from round 1: a conflict with #3561 (a02783d4, not yet on main). `git merge-tree --write-tree a02783d4 <head>` still exits 1 with content conflicts in strings.json, en.json, sv.json and de.json (ev/merge_tree_3561.txt). It is the same adjacent-line edit that round 1 measured and resolved by keeping both lines. Carry: dismissed: a hand resolution the orchestrator makes at the second merge, both sides kept; measured in round 1
- Still open from round 1: translations are not pinned. The written-slot arm reads only strings.json. The delta does not change this. Carry: R11-INTAKE-R10-RESIDUE
- Still open from round 1: the written-slot set (`pump_arbiter._entities`) is narrower than the set of entities that are written. `heat_pump_switch_entity` and `dhw_disinfection_switch_entity` are not covered. The delta does not change this. Carry: R11-INTAKE-R10-RESIDUE
- Still open from round 1: two record rows cite strings.json `menu_options` rather than the code that builds the menu. The delta does not change this. Carry: R11-INTAKE-R10-RESIDUE
- Still open from round 1: the `pump_duty_mode` text says "toward 5 °C (or the Minimum lift…)", but this is a temperature difference and should be in K. It predates the branch. Carry: R11-INTAKE-R10-RESIDUE
- Main added two hysteresis data_description texts. They raise the claim set to 372, and flow-claims.json has no row for them, because its record is judged at merge base 154dbb4c. The body says so. They are main's reviewed text, not this PR's. Carry: R11-INTAKE-R10-RESIDUE
- Main's own red: tests/features.py fails "a charge-start dip that recovers is learned as neither a draw nor usage…" at main 50373173 and at this head alike. Its driver seeds the clock from `dt_util.now()` (tests/features.py:62334), so a wall-clock (weekday) dependence is the likely cause; unconfirmed. This turns every scoped `fast` lane that runs features.py red until it is fixed on main. Carry: R11-INTAKE-R10-RESIDUE

## Evidence

- RESULT prior finding 1 (main-merge break): resolved. 59bb0506 repoints the single pin to `duty_legs.SPLIT_MIN_MINUTES`, adds the import, and changes nothing else (`git show 59bb0506`: tests/doc_claims.py, +2/-2). At the head, which contains current origin/main 50373173, `python3 tests/doc_claims.py` prints `ALL 354 checks PASSED` with rc 0 (ev/doc_claims_head.txt).
- RESULT mutation on the repoint: setting `SPLIT_MIN_MINUTES = 6.0` in duty_legs.py at the head gives `FAIL every quoted figure in the flow help (19 pins) is its constant's value  [options.step.entities_pump.data_description.pump_duty_mode: quotes 5, the code holds 6.0]`, rc 1 (ev/mutant_split_min.txt). The mutant is killed. I restored the file and the worktree is clean.
- RESULT main-conflict resolution, read back per parent: `git show --remerge-diff 6ebbd4e5` shows conflicts in strings.json, en.json, sv.json and de.json only (ev/remerge_diff_6ebbd4e56a.txt). In each, the branch's `pump_duty_mode` is kept, main's base copy of that key is dropped, and main's `space_hysteresis_entity` and `dhw_hysteresis_entity` lines are kept. 5d890b3e, 0d29eb62 and 9a524d70 have no textual conflict; tests/closures.json went through LEDGER-MERGE and was resolved. I ran a key-level three-way check (base, parent 1, parent 2, result) on all four catalogues for each of the four merges. It found `wrong=[]` and `both-sides-changed=[]` in every case (ev/merge_resolution_per_parent.txt). The body's resolution account matches.
- RESULT patch identity: the sorted +/- lines of `git diff 154dbb4c 8c9dc269 -- custom_components` and of `git diff origin/main 9a524d70 -- custom_components` are identical. The production patch is the one already reviewed. Beyond custom_components, the net diff differs only by dev/programme/delivery/3564.md (+1) and by tests/closures.json, where main already carries the harness_headers move and only the `flow_claims.py` entry remains. No production code delta, so no widening (fix-review.md step 12).
- RESULT body figures at the head (ev/head_figures.txt), all matching the body:
  - Flow strings: 1078 per catalogue.
  - Distinct claim set: 372.
  - Verdicts: {'true': 286, 'false': 27, 'stale': 12, 'unverifiable': 4, 'no-claim': 40}.
  - `numstat origin/main HEAD`: 56/56 for strings, de and en, and 55/55 for sv.
  - `numstat 59bb0506 HEAD`: 8/0 per file.
- tests/structure.py: STRUCTURE RATCHET PASSED (ev/structure_head.txt). tests/entities.py: `ALL 2711 ENTITY CHECKS PASSED`, rc 0; this matches the body (ev/entities_head_full.txt).
- Merge with origin/main 50373173: `git merge-tree --write-tree origin/main <head>` exits 0 and writes one tree (ev/merge_tree_main.txt).
- VERSION, the manifest version, RELEASE_NOTES.md and both claim files are untouched: `git diff --stat origin/main HEAD` is empty for all of them.
- RESULT red-check answer (step 11): `tests / fast (3.14)` is in the owed-reds set (ev/owed_reds.txt). It was red at the earlier head 67ab6ad0. The body's `## Red checks` names it and gives the cause (the moved constant). It names a cheaper detector, a local doc_claims.py run after a main merge (17 s), with its standing cost, and records that no new countermeasure is proposed. That trigger is answered. The body also answers `pr-contract`, which is outside the owed set and needed no answer.
- Not re-derived: the scoped-gate figures (`MODE: SCOPED -- 11 script(s) run, 22 scoped out`) and the per-script counts the body quotes for features.py, config_flow_steps.py and harness_headers.py. These are heavy runs; I cite CI's runs.
- CI at this head: I polled `merge_train.py classify` from 00:44 UTC; it returned WAIT (`pending: gate`) until about 01:18. It then returned `RED 9a524d70… pending: none red: gate`, rc 1 (ev/classify_poll.txt). The review packet I rendered at about 01:16 shows `tests / fast (3.14)` id=132266515694 as failure. The job log ends `1 TEST SCRIPT(S) FAILED`, and its tail does not name the script. I re-ran the scoped scripts at the head. `env_drift --claims-only`, `closure.py selftest`, `config_flow_steps.py` (586), `layout.py`, `deployment_shape.py` and `plan_view.py` all exit 0. `env_drift --all` prints NO UNCLAIMED DRIFT and NO STALE FIXTURE (56 scenarios), rc 0 (ev/env_drift_all_head.txt). The log shows card.mjs and harness_headers.py passing. `tests/features.py` exits 1 with `1 of 5571 FEATURE CHECKS FAILED`, on the check "a charge-start dip that recovers is learned as neither a draw nor usage…" (ev/features_head.txt:5500).
- RESULT inherited-red check: at main 50373173 (the PR's base), `tests/features.py` prints the identical FAIL line and `1 of 5571 FEATURE CHECKS FAILED`, rc 1 (ev/features_main_50373173.txt; ev/features_fail_head_vs_main.txt). Between main and the head, the only `.py` files that differ are dev/audit/rounds/round10/D6/flow_claims.py and tests/doc_claims.py. The failing check's driver seeds its clock from `dt_util.now()` (tests/features.py:62334), and it fails on both trees on 2026-11-14, a Saturday. A wall-clock dependence is a plausible cause, but I did not isolate it.

## Delta diff: git diff 9a524d703f3a25325c71f1fe888a35ab53147189 d6a7b00bba95068c5236805aa0a740b792d0d954
diff --git a/RELEASE_NOTES.md b/RELEASE_NOTES.md
index 9f16af6fe3..3bb0dfe9d3 100644
--- a/RELEASE_NOTES.md
+++ b/RELEASE_NOTES.md
@@ -1,3 +1,27 @@
+## v7.1.16
+
+**Patch stamp: 13 merges since v7.1.15 (`git log --first-parent --merges --format=%h v7.1.15..HEAD | wc -l`): the hot-water and heating plans can take the pump's own start condition, the planner prices a hot-water to heating switch that stops the compressor, and the savings reference no longer books heat the pump could not deliver; the rest is tooling.**
+
+### #3531 The pump's start condition is an optional input per duty (R10-OUTSIDE-DHW-START-HYSTERESIS)
+
+With the new optional hot-water and heating hysteresis entities set, the plan no longer starts a charge on a tank at or above the pump's own start temperature, and buys back what the hot-water minimum still needs at steps where a charge can start. If the hot-water minimum is above that start temperature, a repair notice (`dhw_minimum_above_start`) says so. The heating flow floor never uses a lift below the heating hysteresis. Installs that leave the options unset plan as before. Based on outside pull request 3440 by Bankaifan.
+
+### #3526 The planner prices a duty switch that stops the compressor (R10-DUTY-SWITCH-PLANNER-PRICE)
+
+A switch between hot water and heating that the learner reports as stopping the compressor now carries a cost in the plan, including the running time the stop takes, and the planner tries one hot-water placement that avoids it. Built on the finding and table of outside pull request 3420 by Bankaifan.
+
+### #3511 The savings reference holds only a state the pump could deliver (R10-SAV-VALUATION-RESIDUE)
+
+The reference thermostat's held room state is now the highest temperature the reference step can hold within the pump's and the mixing valve's limits, so the reference no longer draws stored heat that nobody paid for. A reference that can hold the target is unchanged.
+
+### Developer tooling, CI and audit machinery only
+
+#3557, #3546, #3558, #3499, #3520, #3539, #3549.
+
+### Record only
+
+#3559 (delivery rows, autofix), #3555, #3554 (roster).
+
 ## v7.1.15
 
 **Patch stamp: 16 merges since v7.1.14 (`git log --first-parent --merges --format=%h v7.1.14..HEAD | wc -l`): the supply switch now keeps its minimum run and pause, the mixing-valve target is labelled as a room temperature, boosts keep the learners clean while their heat settles, and the dashboard card folds its detail sections; the rest is tooling.**
diff --git a/VERSION b/VERSION
index 6329380f96..682452864e 100644
--- a/VERSION
+++ b/VERSION
@@ -1 +1 @@
-7.1.15
+7.1.16
diff --git a/custom_components/heatpump_optimizer/manifest.json b/custom_components/heatpump_optimizer/manifest.json
index 0a11baa27b..b839ba97e5 100644
--- a/custom_components/heatpump_optimizer/manifest.json
+++ b/custom_components/heatpump_optimizer/manifest.json
@@ -25,5 +25,5 @@
     "scipy>=1.10.0",
     "threadpoolctl>=3.5.0"
   ],
-  "version": "7.1.15"
+  "version": "7.1.16"
 }
diff --git a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
index c586c82225..8b635dab94 100644
--- a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
+++ b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
@@ -11,7 +11,7 @@
 
 const CARD_TAG = "heatpump-optimizer-card";
 const EDITOR_TAG = "heatpump-optimizer-card-editor";
-const CARD_VERSION = "7.1.15";
+const CARD_VERSION = "7.1.16";
 
 // Home Assistant's default --primary-color (#03a9f4) is 2.63:1 on a white
 // card — too light for text or for white label text on a filled button.
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index e3d6e2186d..1cba7a8c8c 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -373,7 +373,7 @@
   "source": "manifest.json",
   "claim": "manifest version equals VERSION",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented='7.1.15' measured='7.1.15'",
+  "result": "documented='7.1.16' measured='7.1.16'",
   "verdict": "true",
   "truth": ""
  },
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index e4521e8162..85ee2484d6 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -45,7 +45,7 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C39 | `docs/architecture.md:module map` | sensor.py -- 62 sensors | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=62 measured=62 | **true** |  |
 | C40 | `docs/architecture.md:module map` | switch.py -- the comment names every switch the platform constructs | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Away', 'Block DHW', 'Block Space Heating', 'Boost Space Heating', 'DHW Boost', 'Optimizer Active'], the platform constructs ['Away', 'Block DHW', 'Block Space Heating', 'Boost Space Heating', 'DHW Boost', 'Optimizer Active'] | **true** |  |
 | C41 | `docs/architecture.md:module map` | binary_sensor.py -- the comment names every binary sensor the platform constructs | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Away Mode', 'External Heat Source', 'Input Problem', 'Mold Floor Breach', 'Open Window Detected', 'Wood Cheaper Than Heat Pump'], the platform constructs ['Away Mode', 'External Heat Source', 'Input Problem', 'Mold Floor Breach', 'Open Window Detected', 'Wood Cheaper Than Heat Pump'] | **true** |  |
-| C42 | `manifest.json` | manifest version equals VERSION | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='7.1.15' measured='7.1.15' | **true** |  |
+| C42 | `manifest.json` | manifest version equals VERSION | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='7.1.16' measured='7.1.16' | **true** |  |
 | C43 | `hacs.json` | hacs.json requires Home Assistant 2025.2.0 | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='2025.2.0' measured='2025.2.0' | **true** |  |
 | C44 | `README.md badge` | Home Assistant 2025.2.0+ badge matches hacs.json | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='2025.2.0' measured='2025.2.0' | **true** |  |
 | C45 | `README.md Requirements` | Home Assistant 2025.2.0 or newer | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='2025.2.0' measured='2025.2.0' | **true** |  |
diff --git a/dev/programme/delivery/3572.md b/dev/programme/delivery/3572.md
new file mode 100644
index 0000000000..6356094349
--- /dev/null
+++ b/dev/programme/delivery/3572.md
@@ -0,0 +1 @@
+- [#3572](https://github.com/tvofi/heatpump_optimizer/pull/3572) — **open**, R10-DIMENSIONS-FULL-COVERAGE: r10 dimensions full coverage (R10-DIMENSIONS-FULL-COVERAGE)
diff --git a/dev/programme/delivery/3578.md b/dev/programme/delivery/3578.md
new file mode 100644
index 0000000000..74f5e0da84
--- /dev/null
+++ b/dev/programme/delivery/3578.md
@@ -0,0 +1 @@
+- [#3578](https://github.com/tvofi/heatpump_optimizer/pull/3578) — **open**, R10-HOTFIX-FEATURES-WEEKEND-CLOCK: pin the charge-settle check's clock to a weekday (R10-HOTFIX-FEATURES-WEEKEND-CLOCK)
diff --git a/tests/features.py b/tests/features.py
index a663d02b74..01a0f60761 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -62331,7 +62331,9 @@ def _chg_seq(temps, charged=True, start_hm=(8, 0), heated_at=(1,), saturday=Fals
     learner.async_save_draws = _save_draws
     module = _sys.modules[type(learner).__module__]
     real_dt = module.dt_util
-    start = dt_util.now().replace(hour=start_hm[0], minute=start_hm[1], second=0)
+    # Monday 2026-11-09, never today: the weekday booking must not depend on the day the suite runs.
+    start = dt_util.now().replace(
+        year=2026, month=11, day=9, hour=start_hm[0], minute=start_hm[1], second=0)
     if saturday:
         start += timedelta(days=(5 - start.weekday()) % 7)
     clock = [start]
diff --git a/tests/golden/card_claimed_drift.txt b/tests/golden/card_claimed_drift.txt
index 4c50cb6178..4e3b2fb18e 100644
--- a/tests/golden/card_claimed_drift.txt
+++ b/tests/golden/card_claimed_drift.txt
@@ -19,9 +19,9 @@
 #
 # The state names are the ones `node tests/card_drift.mjs --list` prints.
 #
-# claims-for: 7.1.15
+# claims-for: 7.1.16
 #
-# v7.1.15: Supply minimum run and pause, valve target label, boost settling, card folds. The stamp empties the list; the
+# v7.1.16: Pump start condition input, duty-switch pricing, savings reference fix. The stamp empties the list; the
 # next branch restates its own footprint, claims included.
 #
 
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index a107b76be2..8b6433462b 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -62,12 +62,11 @@
 # about one release's diff, it does not expire with the stamp and is not part
 # of the inherited-claims comparison.
 #
-# claims-for: 7.1.15
+# claims-for: 7.1.16
 #
-# v7.1.15: Supply minimum run and pause, valve target label, boost settling, card folds. The stamp empties the list; the
+# v7.1.16: Pump start condition input, duty-switch pricing, savings reference fix. The stamp empties the list; the
 # next branch restates its own footprint, claims included.
 #
-config_flow # R10-OUTSIDE-DHW-START-HYSTERESIS: the entities_pump page gains the two start-hysteresis pickers (space_hysteresis_entity, dhw_hysteresis_entity), so the plain render, the seeded render and the seed each gain those two keys; every leaf that moves is "present on one side only" and ADDED at this head. Float-free and compared exactly, so re-recorded in the committed file (golden.py --record --only config_flow). No plan reads the options unset: the other 55 fixtures are byte-identical to the merge base (env_drift.py --all, one environment), which is the null.
 # may-drift: flat_prices -- #1208 polish-every-candidate, owner ruling #1208 comment 208bed25
 # (option (a)): the move's margin is inside the noise band (objective rel
 # -1.2171e-03, deterministic on one box), so which runner sees it move is the
diff --git a/tools/policy/check-wave-script.mjs b/tools/policy/check-wave-script.mjs
index be218608f5..806c32b394 100644
--- a/tools/policy/check-wave-script.mjs
+++ b/tools/policy/check-wave-script.mjs
@@ -69,6 +69,14 @@ let pass = 0, fail = 0
 // This is exactly how the control run for the verdict grammar died.
 const J = (x) => JSON.stringify(x ?? null) ?? 'undefined'
 const t = (n, c, d = '') => { c ? (pass++, console.log('  ok   ' + n)) : (fail++, console.log('  FAIL ' + n + ' ' + d)) }
+// THE ONE SWITCH, READ FROM UNPINNED DATA. `wave-script` grades a pull request
+// with the BASE's copy of this file (decision 0013), so this file lands first and
+// must pass over the tree before the driver that carries the denominator (carryOf,
+// seatCarry, denominatorGaps) and over the tree after it. The switch is whether
+// the finder report schema's coverage rows require an enumerator -- a data file
+// the same pull request that lands the driver changes, never the driver's own text.
+// When it is on, the driver MUST export all three and every denominator test runs.
+const DENOM = (JSON.parse(fs.readFileSync(at('dev/audit/config/finding.schema.json'), 'utf8')).properties?.coverage?.items?.required ?? []).includes('enumerator')
 // A block that throws reports as a failure, never as a truncated run. Every
 // grouped assertion below runs inside it: without that the first unexpected
 // throw ends the process and the remaining assertions are silently unreported,
@@ -805,10 +813,10 @@ await block('the finder report schema', async () => {
   const re = (k) => new RegExp(F.properties?.[k]?.pattern ?? '$^')
   const idRe = re('id'), scopeRe = re('scope')
   const ownerRe = new RegExp(S.properties?.leads?.items?.properties?.owner_seat?.pattern ?? '$^')
-  t('scope admits a scopes.json seat id and refuses a bare dimension (D1-s3 yes, D1 no)', scopeRe.test('D1-s3') && scopeRe.test('D14-s5') && !scopeRe.test('D1') && !scopeRe.test('D16-s1'), String(scopeRe))
+  t('scope admits a scopes.json seat id and refuses a bare dimension (D1-s3 yes, D1 no)', scopeRe.test('D1-s3') && scopeRe.test('D14-s5') && !scopeRe.test('D1') && !scopeRe.test('D18-s1') && (!DENOM || scopeRe.test('D17-s1')), String(scopeRe))
   t('a finding numbered under its seat is an id the schema admits (D13-s1-01, D1-s3-51)', idRe.test('D13-s1-01') && idRe.test('D1-s3-51'), String(idRe))
   t("a lead's owner_seat admits a seat id or unknown, and refuses a bare dimension, a file, or anything else (null control)",
-    ownerRe.test('D1-s3') && ownerRe.test('D14-s5') && ownerRe.test('unknown') && !ownerRe.test('D1') && !ownerRe.test('D16-s1') && !ownerRe.test('boost.py') && !ownerRe.test('') && !ownerRe.test('D1-s3 '), String(ownerRe))
+    ownerRe.test('D1-s3') && ownerRe.test('D14-s5') && ownerRe.test('unknown') && !ownerRe.test('D1') && !ownerRe.test('D18-s1') && (!DENOM || ownerRe.test('D17-s1')) &&!ownerRe.test('boost.py') && !ownerRe.test('') && !ownerRe.test('D1-s3 '), String(ownerRe))
   // A design choice, said so: the guess is refused unless it is a class the
   // ledger HAS, so a class the judge adds is added to bugclasses.json and to
   // this enum in one pull request -- this check fails until both carry it.
@@ -951,7 +959,9 @@ await block('the scoped round driver', async () => {
   if (!blk) return
   t('the dispatch block draws on no randomness and no clock', !/Math\.random|Date\b|performance\.now|crypto/.test(blk[0]), 'found one')
   t('and no planSeats: seats come from the scopes, not a rotation over the ledger', !/planSeats/.test(rd), 'audit-find.js still names planSeats')
-  const D = new Function(`${blk[0]}\nreturn { CADENCE, EVERY_DIM_ROUNDS, activeIn, seatsFromScopes, BOXES, CHROMIUM, boxGaps }`)()
+  const D = new Function(`${blk[0]}\nreturn { CADENCE, EVERY_DIM_ROUNDS, activeIn, seatsFromScopes, BOXES, CHROMIUM, boxGaps, carryOf: typeof carryOf === 'function' ? carryOf : undefined, seatCarry: typeof seatCarry === 'function' ? seatCarry : undefined, denominatorGaps: typeof denominatorGaps === 'function' ? denominatorGaps : undefined }`)()
+  t('a schema that requires a denominator has a driver that enforces one (carryOf, seatCarry, denominatorGaps in the DISPATCH block)',
+    !DENOM || [D.carryOf, D.seatCarry, D.denominatorGaps].every((f) => typeof f === 'function'), `schema requires an enumerator; exported: ${['carryOf', 'seatCarry', 'denominatorGaps'].filter((k) => typeof D[k] === 'function')}`)
   // The seat ids and boxes below are read off the committed scopes and the
   // DISPATCH block, never named here: a re-cut of either (round 10 gave every
   // dimension three seats) must not turn a control into a test of old names.
@@ -962,8 +972,12 @@ await block('the scoped round driver', async () => {
   // nor a multiple of three, `on6` is a multiple of six.
   const free = Array.from({ length: 60 }, (_, i) => i + 10).filter((r) => !every.includes(r))
   const off = free.find((r) => r % 2 !== 0 && r % 3 !== 0), on6 = free.find((r) => r % 6 === 0)
-  t(`...and the cadence is otherwise read from the round number (D11 and D5 off at ${off}, both on at ${on6}, D0 on at ${off})`,
-    !!off && !!on6 && !D.activeIn(off, 'D11') && D.activeIn(on6, 'D11') && D.activeIn(on6, 'D5') && !D.activeIn(off, 'D5') && D.activeIn(off, 'D0'), 'the cadence is not derived from the round')
+  // D11 and D13 are held to the driver's own table, not to a number here: the
+  // cadence a tree declares is the cadence it must run (tvofi 2026-11-13 made it
+  // every round, in the pull request that lands the denominator).
+  t(`...and the cadence is otherwise read from the round number (D5 off at ${off}, on at ${on6}; D0 on at ${off}; D11 and D13 follow their CADENCE entry)`,
+    !!off && !!on6 && !D.activeIn(off, 'D5') && D.activeIn(on6, 'D5') && D.activeIn(off, 'D0')
+      && ['D11', 'D13'].every((d) => D.activeIn(off, d) === (D.CADENCE[d] === 1) && D.activeIn(on6, d)), 'the cadence is not derived from the round')
   const ids = L.dims.flatMap((d) => D.seatsFromScopes(scopes, d).map((s) => s.id))
   const fileSeats = Object.entries(scopes).filter(([k]) => !k.startsWith('_')).flatMap(([d, x]) => Object.keys(x.seats).map((k) => `${d}-${k}`))
   t('one seat per scopes.json seat, id <dim>-s<n>, nothing added or dropped', J(ids) === J(fileSeats), `${ids.length} vs ${fileSeats.length}`)
@@ -1005,19 +1019,26 @@ await block('the scoped round driver', async () => {
   // export (or another seat's tree) is visible in its prompt.
   const isoDims = new Set(L.isolated)
   const PREP = { exportDir: '/x', worktrees: Object.fromEntries(fileSeats.filter((id) => isoDims.has(id.split('-')[0])).map((id) => [id, `/w/${id}`])), python: 'py', rotation_ok: true, scopes_ok: true, scopes_rc: 0, scopes_out: 'ok' }
+  // A closed denominator for a seat: one row per step it owns, every carried item answered examined.
+  const closed = (id, args) => {
+    const seat = D.seatsFromScopes(args.scopes, id.split('-')[0]).find((x) => x.id === id)
+    if (!seat) return []
+    const carry = D.seatCarry ? D.seatCarry(args.rotation, args.round, seat) : []
+    return seat.steps.map((m) => ({ step: `${seat.dim}.${m}`, depth: 'deep', enumerator: 'stub-enumerator', universe: 1, examined: 1, not_reached: [], redispatched: carry.filter((c) => c.step === m).map((c) => ({ item: c.id, state: 'examined' })), evidence: 'stub' }))
+  }
   const drive = async (args, { prep = {}, report = () => ({}), nullSeats = [], leadsOut = {}, gather } = {}) => {
     const calls = []
     const agent = async (prompt, o) => {
       calls.push({ label: o.label, prompt, schema: o.schema })
       if (o.label === 'prepare') return { ...PREP, ...prep }
       if (o.label === 'gather' && gather) return gather(prompt)
-      if (o.label === 'gather') return { reports: Object.fromEntries(fileSeats.map((id) => [id, { dimension: id.split('-')[0], report_path: `/r/${id}`, coverage: [], unfinished: [], findings: [], non_findings: [], harnesses: [], leads: [], ...report(id) }])), absent_boxes: [] }
+      if (o.label === 'gather') return { reports: Object.fromEntries(fileSeats.map((id) => [id, { dimension: id.split('-')[0], report_path: `/r/${id}`, coverage: closed(id, args), unfinished: [], findings: [], non_findings: [], harnesses: [], leads: [], ...report(id) }])), absent_boxes: [] }
       if (o.label === 'leads') return { report_path: '/r/leads', findings: [], non_findings: [], harnesses: [], converted: [], closed: [], ...leadsOut }
       if (nullSeats.includes(o.label)) return null
       if (o.label === 'intake') return { branch: 'b', registered: [], rejected: [] }
       if (o.label === 'quiet') return { quiet_path: '/q', d3_confirmed: [] }
       if (o.label.startsWith('collect-')) return { branch: 'b', commit: 'c' }
-      return { dimension: o.label.split('-')[0], report_path: `/r/${o.label}`, coverage: [], unfinished: [], findings: [], non_findings: [], harnesses: [], leads: [], ...report(o.label) }
+      return { dimension: o.label.split('-')[0], report_path: `/r/${o.label}`, coverage: closed(o.label, args), unfinished: [], findings: [], non_findings: [], harnesses: [], leads: [], ...report(o.label) }
     }
     const fn = new Function('agent', 'log', 'phase', 'pipeline', 'args', `return (async () => { ${rbody} })()`)
     let out, error = ''
@@ -1068,7 +1089,7 @@ await block('the scoped round driver', async () => {
   const seatBoxes = Object.keys(D.BOXES).filter((b) => D.BOXES[b].heavy.length + D.BOXES[b].light.length)
   t(`from "intake" gathers once per box, each prompt naming its own box (${seatBoxes.length} boxes)`,
     gathers.length === seatBoxes.length && seatBoxes.every((b) => gathers.filter((c) => c.prompt.includes(`reports-${b}.json`)).length === 1), J(gathers.map((c) => (/reports-(B\d+)\.json/.exec(c.prompt) ?? [])[1])))
-  const rep = (id) => ({ dimension: id.split('-')[0], report_path: `/r/${id}`, coverage: [], unfinished: [], findings: [], non_findings: [], harnesses: [], leads: [] })
+  const rep = (id) => ({ dimension: id.split('-')[0], report_path: `/r/${id}`, coverage: closed(id, base), unfinished: [], findings: [], non_findings: [], harnesses: [], leads: [] })
   const boxIn = (prompt) => (/reports-(B\d+)\.json/.exec(prompt) ?? [])[1]
   const own = (b) => Object.fromEntries([...D.BOXES[b].heavy, ...D.BOXES[b].light].map((id) => [id, rep(id)]))
   const cutBox = bx
@@ -1100,7 +1121,7 @@ await block('the scoped round driver', async () => {
   t(`an unknown box is refused (${noBox})`, !D.BOXES[noBox] && /is not one of/.test((await drive({ ...base, box: noBox })).error), `${noBox} accepted`)
   const both = await drive({ ...base, box: 'B1', from: 'intake' })
   t('box and from "intake" together are refused before Prepare', /exclusive/.test(both.error) && both.labels.length === 0, both.error || J(both.labels))
-  // Round `off` runs neither D5, D6, D11 nor D13 (cadence 2 and 3): a box
+  // Round `off` runs neither D5 nor D6 (cadence 2; D11 and D13 run every round): a box
   // holding both active and inactive seats carries only the active ones, and
   // the placement check is taken over the active seats.
   const mixed = Object.keys(D.BOXES).find((b) => { const ss = [...D.BOXES[b].heavy, ...D.BOXES[b].light].map((s) => D.activeIn(off, s.split('-')[0])); return ss.includes(true) && ss.includes(false) })
@@ -1205,6 +1226,82 @@ await block('the scoped round driver', async () => {
     /handoff\/audit-r9-find-<box>/.test(glp) && !/handoff\/audit-r9-find-<box>/.test(lp), glp.slice(-400))
   t('and the round\'s ledger entry names every active dimension, one step list per seat',
     Object.keys(r9.out?.rotation_round ?? {}).length === L.dims.length && r9.out.rotation_round.D1.seats.length === Object.keys(scopes.D1.seats).length, J(Object.keys(r9.out?.rotation_round ?? {})))
+
+  // The denominator (COMMON.md; tvofi 2026-11-13): a report names what its steps
+  // range over, how much it examined and what it left, and what the round before
+  // left is the first work of this one. Each refusal has its null control here.
+  if (!DENOM) console.log("  skip   the denominator block: the schema's coverage rows require no enumerator at this tree")
+  else await block('the denominator', async () => {
+    const seat = { dim: 'D1', steps: ['M1', 'M2'] }
+    const row = (m, o = {}) => ({ step: `D1.${m}`, enumerator: 'e', universe: 2, examined: 2, not_reached: [], redispatched: [], evidence: 'x', ...o })
+    const ok = { coverage: [row('M1'), row('M2')] }
+    const gaps = (rep, carry = []) => D.denominatorGaps(seat, rep, carry)
+    const refuses = (name, rep, re, carry = []) => { const g = gaps(rep, carry); t(`denominatorGaps refuses ${name}`, g.length > 0 && g.some((x) => re.test(x)), J(g)) }
+    t('denominatorGaps passes a closed report, one row per step (null control)', J(gaps(ok)) === J([]), J(gaps(ok)))
+    refuses('a step with no row', { coverage: [row('M1')] }, /M2/)
+    refuses('two rows for one step', { coverage: [row('M1'), row('M1'), row('M2')] }, /M1/)
+    refuses('an empty enumerator', { coverage: [row('M1', { enumerator: ' ' }), row('M2')] }, /M1/)
+    refuses('examined above universe', { coverage: [row('M1', { examined: 3 }), row('M2')] }, /M1/)
+    refuses('a non-integer universe', { coverage: [row('M1', { universe: 1.5, examined: 1 }), row('M2')] }, /M1/)
+    refuses('examined below universe with nothing listed not reached', { coverage: [row('M1', { examined: 1 }), row('M2')] }, /M1/)
+    refuses('examined equal to universe with a not_reached list', { coverage: [row('M1', { not_reached: ['a'] }), row('M2')] }, /M1/)
+    refuses('an absent coverage', {}, /M1/)
+    const c1 = { id: 'C1', step: 'M1', item: 'x', age: 1, overdue: false }
+    const withAns = (state) => ({ coverage: [row('M1', state ? { universe: 2, examined: state === 'examined' ? 2 : 1, not_reached: state === 'examined' ? [] : ['x'], redispatched: [{ item: 'C1', state }] } : {}), row('M2')] })
+    refuses('a carried item left unanswered', ok, /C1/, [c1])
+    t('...and passes it answered examined, or answered not_reached when not overdue and the counts close (null control)', J(gaps(withAns('examined'), [c1])) === J([]) && J(gaps(withAns('not_reached'), [c1])) === J([]), J([gaps(withAns('examined'), [c1]), gaps(withAns('not_reached'), [c1])]))
+    refuses('an overdue carried item answered not_reached', withAns('not_reached'), /C1/, [{ ...c1, overdue: true }])
+    t('...and passes the same overdue item answered examined (null control)', J(gaps(withAns('examined'), [{ ...c1, overdue: true }])) === J([]), J(gaps(withAns('examined'), [{ ...c1, overdue: true }])))
+
+    const led = { D1: { steps: ['M1', 'M2', 'M3'], rounds: {
+      9: { coverage: { M3: { enumerator: 'e', universe: 3, examined: 1, not_reached: ['a', 'b'] } } },
+      10: { coverage: { M1: 'spot', M2: 'deep', M3: { enumerator: 'e', universe: 3, examined: 2, not_reached: ['a'] } }, unfinished: [{ step: 'D1.M2', what: 'left' }] } } } }
+    const co = D.carryOf(led, 11, 'D1')
+    t('carryOf at round 11 reads round 10: the whole step for M1, "a" aged 2 for M3, the unfinished entry for M2; nothing for deep M2, "b" not carried',
+      co.length === 3 && co.filter((c) => c.step === 'M1').length === 1 && /whole step/.test(co.find((c) => c.step === 'M1')?.item ?? '') && co.find((c) => c.step === 'M3')?.item === 'a' && co.find((c) => c.step === 'M3')?.age === 2
+      && co.filter((c) => c.step === 'M2').length === 1 && co.find((c) => c.step === 'M2')?.item === 'unfinished: left' && !co.some((c) => c.item === 'b'), J(co))
+    const co10 = D.carryOf(led, 10, 'D1')
+    t('...at round 10 it reads round 9 only: a and b, each aged 1', co10.length === 2 && co10.every((c) => c.step === 'M3' && c.age === 1) && J(co10.map((c) => c.item)) === J(['a', 'b']), J(co10))
+    t('...and a dimension with no earlier round carries nothing (null control)', J(D.carryOf(led, 9, 'D1')) === J([]) && J(D.carryOf(led, 11, 'D2')) === J([]), J(D.carryOf(led, 9, 'D1')))
+
+    const sc = D.seatCarry(led, 11, { dim: 'D1', steps: ['M3', 'M2'] })
+    t('seatCarry numbers C1.. in order and keeps only the seat\'s steps', J(sc.map((c) => [c.id, c.step])) === J([['C1', 'M3'], ['C2', 'M2']]) && J(D.seatCarry(led, 11, { dim: 'D1', steps: ['M1'] }).map((c) => c.id)) === J(['C1']), J(sc))
+    const ov = (rotate) => D.seatCarry({ D1: { ...led.D1, ...(rotate ? { rotate } : {}) } }, 11, { dim: 'D1', steps: ['M3'] })[0].overdue
+    t('seatCarry marks the age-2 item overdue at bound 3, not at bound 4, not with no rotate', ov({ M3: { bound: 3 } }) === true && ov({ M3: { bound: 4 } }) === false && ov(undefined) === false, J([ov({ M3: { bound: 3 } }), ov({ M3: { bound: 4 } }), ov(undefined)]))
+
+    // Driven: the real committed scopes and ledger at round 11.
+    const b11 = { ...base, round: 11 }
+    const empty = await drive(b11, { report: (l) => (l === 'D1-s1' ? { coverage: [] } : {}) })
+    t('a seat whose report carries no denominator is dispatched twice, ends missing, and intake does not run',
+      empty.labels.filter((l) => l === 'D1-s1').length === 2 && J(empty.out?.missing) === J(['D1-s1']) && !empty.labels.includes('intake'), J({ n: empty.labels.filter((l) => l === 'D1-s1').length, missing: empty.out?.missing, error: empty.error }))
+    const full11 = await drive(b11)
+    t('...and with the default stub every seat reports and intake runs (null control)', full11.error === '' && J(full11.out?.missing) === J([]) && full11.labels.includes('intake') && full11.labels.filter((l) => l === 'D1-s1').length === 1, J({ error: full11.error, missing: full11.out?.missing }))
+
+    const fp = (l) => full11.calls.find((c) => c.label === l)?.prompt ?? ''
+    t('a seat with carry (D4-s1, whose round-10 M1 was "spot") is told FIRST WORK with its C ids', fp('D4-s1').includes('FIRST WORK') && fp('D4-s1').includes('C1') && !fp('D4-s1').includes('handed your steps nothing not reached'), fp('D4-s1').slice(-400))
+    const none = await drive({ ...b11, rotation: { ...ledger, D4: { ...ledger.D4, rounds: {} } } })
+    const np = (l) => none.calls.find((c) => c.label === l)?.prompt ?? ''
+    const d4 = none.labels.filter((l) => /^D4-s\d+$/.test(l))
+    t('a dimension with no earlier round is told it was handed nothing, and no FIRST WORK (null control)', d4.length > 0 && d4.every((l) => np(l).includes('handed your steps nothing not reached') && !np(l).includes('FIRST WORK')), J(d4))
+
+    // The ledger entry is the sum over the seats that own the step.
+    const owners = (d, m) => D.seatsFromScopes(scopes, d).filter((x) => x.steps.includes(m)).map((x) => x.id)
+    const [sd, sm] = L.dims.filter((d) => scopes[d]).flatMap((d) => scopes[d].steps.map((m) => [d, m])).sort((a, b) => owners(b[0], b[1]).length - owners(a[0], a[1]).length)[0]
+    const led11 = full11.out?.rotation_round?.[sd]?.coverage?.[sm]
+    const k = owners(sd, sm).length
+    t(`the round's ledger coverage is exactly {enumerator, universe, examined, not_reached}, summed over the ${k} seat(s) owning ${sd}.${sm}`,
+      J(Object.keys(led11 ?? {}).sort()) === J(['enumerator', 'examined', 'not_reached', 'universe']) && led11.universe === k && led11.examined === k && J(led11.not_reached) === J([]), J(led11))
+    const s41 = D.seatsFromScopes(scopes, 'D4').find((x) => x.id === 'D4-s1')
+    const carry41 = D.seatCarry(ledger, 11, s41)
+    const m41 = carry41[0]?.step
+    const answered = await drive(b11, { report: (l) => (l !== 'D4-s1' ? {} : { coverage: closed('D4-s1', b11).map((r) => (r.step !== `D4.${m41}` ? r : { ...r, examined: 0, universe: 1, not_reached: ['z'], redispatched: [...r.redispatched.filter((x) => x.item !== 'C1'), { item: 'C1', state: 'not_reached' }] })) }) })
+    const nr = answered.out?.rotation_round?.D4?.coverage?.[m41]?.not_reached ?? []
+    t('a carried item answered not_reached stays in the ledger under its original words, beside the seat\'s own not_reached',
+      !!m41 && carry41[0].overdue === false && nr.includes('z') && nr.includes(carry41[0].item), J({ m41, nr, item: carry41[0]?.item, error: answered.error, missing: answered.out?.missing }))
+    t('...and the default run keeps neither (null control)', !(full11.out?.rotation_round?.D4?.coverage?.[m41]?.not_reached ?? []).includes('z') && !(full11.out?.rotation_round?.D4?.coverage?.[m41]?.not_reached ?? []).includes(carry41[0]?.item), J(full11.out?.rotation_round?.D4?.coverage?.[m41]))
+
+    t('the cadence: D11, D13, D16 and D17 run at round 11, D5 does not', D.activeIn(11, 'D11') && D.activeIn(11, 'D13') && D.activeIn(11, 'D16') && D.activeIn(11, 'D17') && !D.activeIn(11, 'D5'), J(['D11', 'D13', 'D16', 'D17', 'D5'].map((d) => [d, D.activeIn(11, d)])))
+  })
 })
 
 // THE ROUND-9 VERIFY DRIVER, ADMITTED BEFORE IT LANDS -- R1a's route for the

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
