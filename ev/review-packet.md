# Review packet #3671
head: 17c9dd0672322c18c03a0cd6781310d6596a6327
base: 6f422812d5d8b918beace0283419c153f6df66ce

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
cancel-superseded id=133428430329 queued
prelude id=133428430209 queued
refresh id=133428429813 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
FIGURES: 0 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3671.md b/dev/programme/delivery/3671.md
new file mode 100644
index 0000000000..f5a21720f0
--- /dev/null
+++ b/dev/programme/delivery/3671.md
@@ -0,0 +1 @@
+- [#3671](https://github.com/tvofi/heatpump_optimizer/pull/3671) — **open**, R11-HOTFIX-MAIN-SELFTEST-DRIFT: re-record the self-test read table (R11-HOTFIX-MAIN-SELFTEST-DRIFT)
diff --git a/tools/ci/selftest_closures.json b/tools/ci/selftest_closures.json
index 2a07bf3bd8..3c0f43d262 100644
--- a/tools/ci/selftest_closures.json
+++ b/tools/ci/selftest_closures.json
@@ -196,6 +196,7 @@
     "tools/audit/archscore/weights.sha256",
     "tools/audit/carry_audit.py",
     "tools/audit/check_scopes.py",
+    "tools/audit/enumerate.py",
     "tools/audit/fold_ledger.py",
     "tools/audit/judge_batch.py",
     "tools/audit/machinery_ratchet.py",
@@ -263,6 +264,7 @@
     "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
+    "tools/audit/seat/plan_phases.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
     "tools/audit/seat/plant_recall.py",
@@ -2823,6 +2825,7 @@
    "run_sha": "8e2afa7d1084b7223a39f0ef593e419b78e3a724781a06ccb99196801427962a",
    "files": [
     "dev/governance/config/machinery_budgets.json",
+    "dev/governance/config/machinery_target_budgets.json",
     "dev/governance/config/policy_budgets.json",
     "tests/ci_budgets.json",
     "tests/coverage_budgets.json",
@@ -3825,6 +3828,7 @@
     "dev/governance/config",
     "dev/governance/decisions",
     "dev/governance/dimensions",
+    "dev/governance/dimensions/criteria",
     "dev/governance/roles",
     "dev/governance/rules",
     "dev/programme",
@@ -3835,6 +3839,7 @@
     "dev/programme/round10",
     "dev/programme/round10/rechain",
     "dev/programme/round10/state",
+    "dev/programme/round11",
     "dev/programme/round9",
     "dev/programme/round9/state",
     "dev/programme/triage",
@@ -3943,6 +3948,7 @@
     "tests/mutation_ledger/killed_by/services.py",
     "tests/mutation_ledger/killed_by/setpoint_check.py",
     "tests/mutation_ledger/killed_by/silent_mode.py",
+    "tests/mutation_ledger/killed_by/slab_seed.py",
     "tests/mutation_ledger/killed_by/slot_drivers.py",
     "tests/mutation_ledger/killed_by/snapshots.py",
     "tests/mutation_ledger/killed_by/store.py",
@@ -3985,6 +3991,7 @@
     "tests/mutation_ledger/survivor_triage/quiet_windows.py",
     "tests/mutation_ledger/survivor_triage/repairs.py",
     "tests/mutation_ledger/survivor_triage/sensor.py",
+    "tests/mutation_ledger/survivor_triage/slab_seed.py",
     "tests/mutation_ledger/survivor_triage/slot_drivers.py",
     "tests/mutation_ledger/survivor_triage/store.py",
     "tests/mutation_ledger/survivor_triage/sysid.py",
@@ -4160,6 +4167,7 @@
     "tools/audit/archscore/gate.py",
     "tools/audit/carry_audit.py",
     "tools/audit/check_scopes.py",
+    "tools/audit/enumerate.py",
     "tools/audit/fold_ledger.py",
     "tools/audit/machinery_ratchet.py",
     "tools/audit/merge_fastpath.py",
@@ -4213,6 +4221,7 @@
     "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
+    "tools/audit/seat/plan_phases.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
     "tools/audit/seat/plant_recall.py",
@@ -4526,6 +4535,7 @@
   "gantt-and-verdict-audit": {
    "run_sha": "16bbc5a7a78f977e26aabe9f3756fcab21ffc79c4ad03ac92f57d5a1fbfdc634",
    "files": [
+    "tests/throwaway_git.py",
     "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/roster_lib.py",
     "tools/audit/seat/sweep_gantt.py",
@@ -4534,11 +4544,16 @@
    ],
    "probes": [
     ".",
+    "config",
+    "objects",
+    "refs",
+    "tests",
     "tools",
     "tools/audit",
     "tools/audit/seat"
    ],
    "dirs": [
+    "tests",
     "tools/audit/seat"
    ],
    "index": false,
@@ -4801,6 +4816,7 @@
     "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
+    "tools/audit/seat/plan_phases.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
     "tools/audit/seat/plant_recall.py",
@@ -5076,6 +5092,7 @@
     "tools/audit/seat/review_packet.py",
     "tools/audit/seat/roster_lib.py",
     "tools/audit/seat/seat_gen.py",
+    "tools/audit/seat/topic_grammar.py",
     "tools/ci/gate.py",
     "tools/ci/ghapi.py",
     "tools/ci/prelude.py",
@@ -5249,6 +5266,7 @@
     "tools/audit/archscore/vector.py",
     "tools/audit/carry_audit.py",
     "tools/audit/check_scopes.py",
+    "tools/audit/enumerate.py",
     "tools/audit/fold_ledger.py",
     "tools/audit/judge_batch.py",
     "tools/audit/machinery_ratchet.py",
@@ -5313,6 +5331,7 @@
     "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
+    "tools/audit/seat/plan_phases.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
     "tools/audit/seat/plant_recall.py",
@@ -5348,6 +5367,8 @@
     "tools/audit/seat/roster_lib.py",
     "tools/audit/seat/roster_queue.py",
     "tools/audit/seat/roster_sync.py",
+    "tools/audit/seat/round_metrics.py",
+    "tools/audit/seat/round_metrics_selftest.py",
     "tools/audit/seat/row_position.py",
     "tools/audit/seat/run_twins.py",
     "tools/audit/seat/scorecard.py",
@@ -5487,11 +5508,13 @@
     "tests/layout.json",
     "tests/layout.py",
     "tests/throwaway_git.py",
+    "tools/audit/machinery_ratchet.py",
     "tools/audit/seat/ci_priority.py",
     "tools/audit/seat/gh_read.py",
     "tools/audit/seat/ledger.py",
     "tools/audit/seat/merge_train.py",
     "tools/audit/seat/orchestrator_tick.py",
+    "tools/audit/seat/owed_unactioned.py",
     "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/pr_cap.py",
     "tools/audit/seat/proof_watch.py",
@@ -5501,9 +5524,11 @@
     "tools/ci/gate.py",
     "tools/ci/ghapi.py",
     "tools/ci/prelude.py",
+    "tools/plan/replan.py",
     "tools/policy/budget_raise_gate.py",
     "tools/policy/fixtures/required-contexts.json",
-    "tools/pr/app_approve.sh"
+    "tools/pr/app_approve.sh",
+    "tools/release/stamp.py"
    ],
    "probes": [
     ".",
@@ -5518,14 +5543,17 @@
     "tools/audit/carry_audit.py",
     "tools/audit/seat",
     "tools/ci",
+    "tools/plan",
     "tools/policy",
-    "tools/policy/policy_lint.mjs"
+    "tools/policy/policy_lint.mjs",
+    "tools/release"
    ],
    "dirs": [
     ".github/workflows",
     "tests",
     "tools/audit/seat",
-    "tools/ci"
+    "tools/ci",
+    "tools/release"
    ],
    "index": true,
    "objects": true,
@@ -5545,6 +5573,7 @@
     "tools/audit/archscore/**",
     "tools/audit/carry_audit.py",
     "tools/audit/check_scopes.py",
+    "tools/audit/enumerate.py",
     "tools/audit/fold_ledger.py",
     "tools/audit/judge_batch.py",
     "tools/audit/machinery_ratchet.py",
@@ -5613,6 +5642,7 @@
     "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
+    "tools/audit/seat/plan_phases.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
     "tools/audit/seat/plant_recall.py",
@@ -5648,6 +5678,8 @@
     "tools/audit/seat/roster_lib.py",
     "tools/audit/seat/roster_queue.py",
     "tools/audit/seat/roster_sync.py",
+    "tools/audit/seat/round_metrics.py",
+    "tools/audit/seat/round_metrics_selftest.py",
     "tools/audit/seat/row_position.py",
     "tools/audit/seat/run_twins.py",
     "tools/audit/seat/scorecard.py",
@@ -5795,12 +5827,20 @@
    "files": [
     "tests/layout.py",
     "tests/throwaway_git.py",
+    "tools/audit/carry_audit.py",
     "tools/audit/merge_throughput.py",
     "tools/audit/seat/bottleneck_check.py",
     "tools/audit/seat/plan_page.py",
+    "tools/audit/seat/plan_phases.py",
+    "tools/audit/seat/plan_public.py",
     "tools/audit/seat/pr_cap.py",
+    "tools/audit/seat/ref_privacy.py",
     "tools/audit/seat/review_strength.py",
+    "tools/audit/seat/roster_edit.py",
     "tools/audit/seat/roster_lib.py",
+    "tools/audit/seat/roster_sync.py",
+    "tools/audit/seat/state_docs.py",
+    "tools/audit/seat/topic_grammar.py",
     "tools/plan/durations.json",
     "tools/plan/replan.py",
     "tools/policy/budget_raise_gate.py",
@@ -5935,6 +5975,7 @@
     "dev/audit/**",
     "dev/governance/config/corpus_excluded.json",
     "dev/governance/config/machinery_budgets.json",
+    "dev/governance/config/machinery_target_budgets.json",
     "dev/governance/config/outside_contributors.json",
     "dev/governance/config/policy_budgets.json",
     "dev/governance/config/policy_known_bad.json",
@@ -5952,6 +5993,7 @@
     "dev/programme/register/audit-2026-09.md",
     "dev/programme/rosters/**",
     "dev/programme/round10/**",
+    "dev/programme/round11/phases.json",
     "dev/programme/round9/**",
     "dev/programme/triage/**",
     "docs/**",
@@ -6506,6 +6548,7 @@
     "dev/programme/round10/.gitattributes",
     "dev/programme/round10/rechain/.gitattributes",
     "dev/programme/round10/state/.gitattributes",
+    "dev/programme/round11/.gitattributes",
     "dev/programme/round9/.gitattributes",
     "dev/programme/round9/state/.gitattributes",
     "dev/programme/triage/.gitattributes",
@@ -6669,6 +6712,7 @@
     "tools/audit/archscore/vector.py",
     "tools/audit/carry_audit.py",
     "tools/audit/check_scopes.py",
+    "tools/audit/enumerate.py",
     "tools/audit/fold_ledger.py",
     "tools/audit/judge_batch.py",
     "tools/audit/machinery_ratchet.py",
@@ -6733,6 +6777,7 @@
     "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
+    "tools/audit/seat/plan_phases.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
     "tools/audit/seat/plant_recall.py",
@@ -6768,6 +6813,8 @@
     "tools/audit/seat/roster_lib.py",
     "tools/audit/seat/roster_queue.py",
     "tools/audit/seat/roster_sync.py",
+    "tools/audit/seat/round_metrics.py",
+    "tools/audit/seat/round_metrics_selftest.py",
     "tools/audit/seat/row_position.py",
     "tools/audit/seat/run_twins.py",
     "tools/audit/seat/scorecard.py",
@@ -6984,6 +7031,7 @@
     "tools/audit/seat/ref_privacy.py",
     "tools/audit/seat/review_packet.py",
     "tools/audit/seat/roster_lib.py",
+    "tools/audit/seat/topic_grammar.py",
     "tools/audit/worktree_gc.sh",
     "tools/merge/ledger_merge.py",
     "tools/policy/brief_lint.mjs",
@@ -7503,6 +7551,7 @@
     "dev/governance/config",
     "dev/governance/decisions",
     "dev/governance/dimensions",
+    "dev/governance/dimensions/criteria",
     "dev/governance/roles",
     "dev/governance/rules",
     "dev/programme",
@@ -7513,6 +7562,7 @@
     "dev/programme/round10",
     "dev/programme/round10/rechain",
     "dev/programme/round10/state",
+    "dev/programme/round11",
     "dev/programme/round9",
     "dev/programme/round9/state",
     "dev/programme/triage",
@@ -7621,6 +7671,7 @@
     "tests/mutation_ledger/killed_by/services.py",
     "tests/mutation_ledger/killed_by/setpoint_check.py",
     "tests/mutation_ledger/killed_by/silent_mode.py",
+    "tests/mutation_ledger/killed_by/slab_seed.py",
     "tests/mutation_ledger/killed_by/slot_drivers.py",
     "tests/mutation_ledger/killed_by/snapshots.py",
     "tests/mutation_ledger/killed_by/store.py",
@@ -7663,6 +7714,7 @@
     "tests/mutation_ledger/survivor_triage/quiet_windows.py",
     "tests/mutation_ledger/survivor_triage/repairs.py",
     "tests/mutation_ledger/survivor_triage/sensor.py",
+    "tests/mutation_ledger/survivor_triage/slab_seed.py",
     "tests/mutation_ledger/survivor_triage/slot_drivers.py",
     "tests/mutation_ledger/survivor_triage/store.py",
     "tests/mutation_ledger/survivor_triage/sysid.py",
@@ -8115,6 +8167,7 @@
     "tools/audit/seat/ref_privacy.py",
     "tools/audit/seat/review_packet.py",
     "tools/audit/seat/roster_lib.py",
+    "tools/audit/seat/topic_grammar.py",
     "tools/policy/brief_lint.mjs",
     "tools/policy/counts.mjs",
     "tools/policy/dependabot_contract.mjs",
@@ -8493,6 +8546,7 @@
     "dev/audit/**",
     "dev/governance/config/corpus_excluded.json",
     "dev/governance/config/machinery_budgets.json",
+    "dev/governance/config/machinery_target_budgets.json",
     "dev/governance/config/outside_contributors.json",
     "dev/governance/config/policy_budgets.json",
     "dev/governance/config/policy_known_bad.json",
@@ -8511,6 +8565,7 @@
     "dev/programme/register/audit-2026-09.md",
     "dev/programme/rosters/**",
     "dev/programme/round10/**",
+    "dev/programme/round11/phases.json",
     "dev/programme/round9/**",
     "dev/programme/triage/**",
     "docs/**",
@@ -8670,10 +8725,12 @@
     "tests/mutation_ledger/killed_by/quiet_windows.py",
     "tests/mutation_ledger/killed_by/repairs.py",
     "tests/mutation_ledger/killed_by/replay_doc.py",
+    "tests/mutation_ledger/killed_by/running_signal.py",
     "tests/mutation_ledger/killed_by/sensor.py",
     "tests/mutation_ledger/killed_by/services.py",
     "tests/mutation_ledger/killed_by/setpoint_check.py",
     "tests/mutation_ledger/killed_by/silent_mode.py",
+    "tests/mutation_ledger/killed_by/slab_seed.py",
     "tests/mutation_ledger/killed_by/slot_drivers.py",
     "tests/mutation_ledger/killed_by/snapshots.py",
     "tests/mutation_ledger/killed_by/store.py",
@@ -8715,6 +8772,7 @@
     "tests/mutation_ledger/survivor_triage/quiet_windows.py",
     "tests/mutation_ledger/survivor_triage/repairs.py",
     "tests/mutation_ledger/survivor_triage/sensor.py",
+    "tests/mutation_ledger/survivor_triage/slab_seed.py",
     "tests/mutation_ledger/survivor_triage/slot_drivers.py",
     "tests/mutation_ledger/survivor_triage/store.py",
     "tests/mutation_ledger/survivor_triage/sysid.py",
@@ -8819,6 +8877,7 @@
     "tools/audit/archscore/weights.sha256",
     "tools/audit/carry_audit.py",
     "tools/audit/check_scopes.py",
+    "tools/audit/enumerate.py",
     "tools/audit/fold_ledger.py",
     "tools/audit/judge_batch.py",
     "tools/audit/machinery_ratchet.py",
@@ -8887,6 +8946,7 @@
     "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
+    "tools/audit/seat/plan_phases.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
     "tools/audit/seat/plant_recall.py",
@@ -9103,6 +9163,7 @@
     "tools/audit/seat/bottleneck_check.py",
     "tools/audit/seat/handover_prompt.py",
     "tools/audit/seat/plan_page.py",
+    "tools/audit/seat/plan_phases.py",
     "tools/audit/seat/plan_table.py",
     "tools/audit/seat/pr_cap.py",
     "tools/audit/seat/ref_privacy.py",
@@ -9353,6 +9414,7 @@
     "tests/mutation_ledger/killed_by/services.py/.gitattributes",
     "tests/mutation_ledger/killed_by/setpoint_check.py/.gitattributes",
     "tests/mutation_ledger/killed_by/silent_mode.py/.gitattributes",
+    "tests/mutation_ledger/killed_by/slab_seed.py/.gitattributes",
     "tests/mutation_ledger/killed_by/slot_drivers.py/.gitattributes",
     "tests/mutation_ledger/killed_by/snapshots.py/.gitattributes",
     "tests/mutation_ledger/killed_by/store.py/.gitattributes",
@@ -9395,6 +9457,7 @@
     "tests/mutation_ledger/survivor_triage/quiet_windows.py/.gitattributes",
     "tests/mutation_ledger/survivor_triage/repairs.py/.gitattributes",
     "tests/mutation_ledger/survivor_triage/sensor.py/.gitattributes",
+    "tests/mutation_ledger/survivor_triage/slab_seed.py/.gitattributes",
     "tests/mutation_ledger/survivor_triage/slot_drivers.py/.gitattributes",
     "tests/mutation_ledger/survivor_triage/store.py/.gitattributes",
     "tests/mutation_ledger/survivor_triage/sysid.py/.gitattributes",
@@ -9578,6 +9641,7 @@
     "tools/audit/archscore/vector.py",
     "tools/audit/carry_audit.py",
     "tools/audit/check_scopes.py",
+    "tools/audit/enumerate.py",
     "tools/audit/fold_ledger.py",
     "tools/audit/judge_batch.py",
     "tools/audit/machinery_ratchet.py",
@@ -9642,6 +9706,7 @@
     "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
+    "tools/audit/seat/plan_phases.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
     "tools/audit/seat/plant_recall.py",
@@ -9677,6 +9742,8 @@
     "tools/audit/seat/roster_lib.py",
     "tools/audit/seat/roster_queue.py",
     "tools/audit/seat/roster_sync.py",
+    "tools/audit/seat/round_metrics.py",
+    "tools/audit/seat/round_metrics_selftest.py",
     "tools/audit/seat/row_position.py",
     "tools/audit/seat/run_twins.py",
     "tools/audit/seat/scorecard.py",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
