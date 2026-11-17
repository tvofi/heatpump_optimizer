# Review packet #3707
head: 49e0e0c270a9ae4d8e734df3bb338faf1e9593cf
base: 8f39313a44a4baec18b239ba925f6e164eb26bd2

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=134023916728 success
arch-score / arch-score id=134025139556 success
arm id=134023515952 skipped
budget-raise-gate / budget-raise-gate id=134025139234 success
cancel-superseded id=134024791379 success
codeql id=134025141778 skipped
codeql / Analyze (actions) id=134023819005 success
codeql / Analyze (javascript-typescript) id=134023819094 success
codeql / Analyze (python) id=134023819190 success
gate id=134025881927 failure
governance id=134025141229 skipped
governance / env-matrix id=134023819323 in_progress
governance / instrument-self-tests id=134023819204 in_progress
governance / policy-docs id=134023819032 success
governance / record id=134023821852 skipped
governance / wave-script id=134023819108 success
hassfest id=134025141028 skipped
hassfest / hassfest id=134023819126 success
kernel-points id=134025141160 skipped
pr-contract id=134025883842 skipped
prelude id=134024790863 success
refresh id=134024791299 success
sweep-self id=134026306149 skipped
tests id=134025141723 skipped
tests / arch-instrument id=134024247190 in_progress
tests / briefs id=134023819211 success
tests / browser id=134024247110 in_progress
tests / closure-scope id=134023819384 success
tests / closures id=134024247173 in_progress
tests / coverage id=134024247241 in_progress
tests / fast (3.14) id=134024247224 in_progress
tests / mutation id=134023819270 success
tests / mutation-autofix id=134024330295 skipped
tests / mutation-pins id=134024330098 skipped
tests / nightly-ha id=134024250024 skipped
tests / nightly-status id=134023819340 failure
tests / replay id=134024249573 skipped
tests / typing id=134024247219 success
validate id=134025142544 skipped
validate / validate-hacs id=134023818982 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 134023819204: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
required-wait: required context `gate` reads concluded failure at 49e0e0c270a9ae4d8e734df3bb338faf1e9593cf in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

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
diff --git a/dev/programme/delivery/3707.md b/dev/programme/delivery/3707.md
new file mode 100644
index 0000000000..bf91f00a10
--- /dev/null
+++ b/dev/programme/delivery/3707.md
@@ -0,0 +1 @@
+- [#3707](https://github.com/tvofi/heatpump_optimizer/pull/3707) — **open**, R11-HOTFIX-MAIN-SELFTEST-DRIFT: re-record the self-test table from main run 44048908427 (R11-HOTFIX-MAIN-SELFTEST-DRIFT)
diff --git a/tools/ci/selftest_closures.json b/tools/ci/selftest_closures.json
index c5f72db9ce..28b2a1c0fe 100644
--- a/tools/ci/selftest_closures.json
+++ b/tools/ci/selftest_closures.json
@@ -128,6 +128,7 @@
     "tools/audit/prepare_baseline.sh",
     "tools/audit/repo_root.sh",
     "tools/audit/seat/a1_dispatch_arms.sh",
+    "tools/audit/seat/ancestry_calls.sh",
     "tools/audit/seat/autofix_statuses.sh",
     "tools/audit/seat/bare_array.py",
     "tools/audit/seat/body_patch.sh",
@@ -211,6 +212,7 @@
     "tools/audit/repo_root.sh",
     "tools/audit/round4/**",
     "tools/audit/seat/a1_dispatch_arms.sh",
+    "tools/audit/seat/ancestry_calls.sh",
     "tools/audit/seat/autofix_statuses.sh",
     "tools/audit/seat/bare_array.py",
     "tools/audit/seat/beat_jobs.py",
@@ -313,6 +315,7 @@
     "tools/audit/seat/seat_gen_selftest.py",
     "tools/audit/seat/seat_venv.sh",
     "tools/audit/seat/selftest_wiring.py",
+    "tools/audit/seat/shell_hazard.py",
     "tools/audit/seat/shims/**",
     "tools/audit/seat/state_docs.py",
     "tools/audit/seat/survivor_list.py",
@@ -3354,6 +3357,7 @@
   "dependency-graph-census": {
    "run_sha": "2fc275964d5628cecf27226ec91672f83abf35c8fd29a39db34fe589e240479d",
    "files": [
+    ".github/ISSUE_TEMPLATE/**",
     ".github/actions/nightly-ha/action.yml",
     ".github/dependabot.yml",
     ".github/workflows/**",
@@ -3378,6 +3382,7 @@
     ".cursor",
     ".cursor/rules",
     ".github",
+    ".github/ISSUE_TEMPLATE",
     ".github/actions",
     ".github/actions/nightly-ha",
     ".github/workflows",
@@ -3954,6 +3959,7 @@
     "tests/mutation_ledger/killed_by/quiet_windows.py",
     "tests/mutation_ledger/killed_by/repairs.py",
     "tests/mutation_ledger/killed_by/replay_doc.py",
+    "tests/mutation_ledger/killed_by/rooms.py",
     "tests/mutation_ledger/killed_by/running_signal.py",
     "tests/mutation_ledger/killed_by/runs.py",
     "tests/mutation_ledger/killed_by/sensor.py",
@@ -4002,6 +4008,7 @@
     "tests/mutation_ledger/survivor_triage/pump_mode.py",
     "tests/mutation_ledger/survivor_triage/quiet_windows.py",
     "tests/mutation_ledger/survivor_triage/repairs.py",
+    "tests/mutation_ledger/survivor_triage/rooms.py",
     "tests/mutation_ledger/survivor_triage/runs.py",
     "tests/mutation_ledger/survivor_triage/sensor.py",
     "tests/mutation_ledger/survivor_triage/slab_seed.py",
@@ -4279,6 +4286,7 @@
     "tools/audit/seat/seat_gen_selftest.py",
     "tools/audit/seat/seat_venv.sh",
     "tools/audit/seat/selftest_wiring.py",
+    "tools/audit/seat/shell_hazard.py",
     "tools/audit/seat/state_docs.py",
     "tools/audit/seat/survivor_list.py",
     "tools/audit/seat/sweep_driver.py",
@@ -4783,6 +4791,7 @@
     "tests/typing_budgets.json",
     "tools/audit/seat/INSTRUMENTS.md",
     "tools/audit/seat/a1_dispatch_arms.sh",
+    "tools/audit/seat/ancestry_calls.sh",
     "tools/audit/seat/autofix_statuses.sh",
     "tools/audit/seat/bare_array.py",
     "tools/audit/seat/beat_jobs.py",
@@ -4885,6 +4894,7 @@
     "tools/audit/seat/seat_gen_selftest.py",
     "tools/audit/seat/seat_venv.sh",
     "tools/audit/seat/selftest_wiring.py",
+    "tools/audit/seat/shell_hazard.py",
     "tools/audit/seat/shims/**",
     "tools/audit/seat/state_docs.py",
     "tools/audit/seat/survivor_list.py",
@@ -5127,43 +5137,209 @@
     "tests/layout.py",
     "tests/run.sh",
     "tests/throwaway_git.py",
+    "tools/audit/archscore/__init__.py",
+    "tools/audit/archscore/calibrate.py",
+    "tools/audit/archscore/counters.py",
+    "tools/audit/archscore/gate.py",
+    "tools/audit/archscore/metrics/**",
+    "tools/audit/archscore/planted/**",
+    "tools/audit/archscore/score.py",
+    "tools/audit/archscore/vector.py",
     "tools/audit/carry_audit.py",
+    "tools/audit/check_scopes.py",
+    "tools/audit/enumerate.py",
+    "tools/audit/fold_ledger.py",
+    "tools/audit/judge_batch.py",
+    "tools/audit/machinery_ratchet.py",
     "tools/audit/merge_fastpath.py",
+    "tools/audit/merge_throughput.py",
+    "tools/audit/product_reads.py",
+    "tools/audit/prose_counts_census.py",
+    "tools/audit/repo_root.py",
+    "tools/audit/round4/**",
+    "tools/audit/seat/bare_array.py",
+    "tools/audit/seat/beat_jobs.py",
+    "tools/audit/seat/beat_jobs_selftest.py",
+    "tools/audit/seat/beatd.py",
+    "tools/audit/seat/bottleneck_check.py",
+    "tools/audit/seat/carry_fold.py",
+    "tools/audit/seat/ci_critpath.py",
     "tools/audit/seat/ci_pause.py",
     "tools/audit/seat/ci_priority.py",
+    "tools/audit/seat/ci_probe.py",
+    "tools/audit/seat/closeout.py",
+    "tools/audit/seat/cloud_dispatch.py",
+    "tools/audit/seat/daemonize.py",
+    "tools/audit/seat/features_block.py",
+    "tools/audit/seat/finder_overlap.py",
+    "tools/audit/seat/flow_metrics.py",
+    "tools/audit/seat/gantt_drift.py",
+    "tools/audit/seat/gh_calls.py",
     "tools/audit/seat/gh_read.py",
+    "tools/audit/seat/gh_read_run.py",
+    "tools/audit/seat/handover_prompt.py",
+    "tools/audit/seat/hooks/**",
+    "tools/audit/seat/hooks_setup.py",
     "tools/audit/seat/ledger.py",
+    "tools/audit/seat/loop_ledger.py",
     "tools/audit/seat/merge_pr.sh",
     "tools/audit/seat/merge_train.py",
+    "tools/audit/seat/moved_paths.py",
+    "tools/audit/seat/mutant_run.py",
+    "tools/audit/seat/offline_spy.py",
+    "tools/audit/seat/open_driver.py",
+    "tools/audit/seat/open_driver_selftest.py",
     "tools/audit/seat/orchestrator_tick.py",
+    "tools/audit/seat/outside_intake.py",
+    "tools/audit/seat/outside_intake_selftest.py",
+    "tools/audit/seat/owed_unactioned.py",
+    "tools/audit/seat/owed_watch.py",
+    "tools/audit/seat/plan_audit.py",
+    "tools/audit/seat/plan_page.py",
+    "tools/audit/seat/plan_phases.py",
+    "tools/audit/seat/plan_public.py",
+    "tools/audit/seat/plan_table.py",
+    "tools/audit/seat/plant_recall.py",
+    "tools/audit/seat/policy_reread_check.py",
+    "tools/audit/seat/postmerge.py",
     "tools/audit/seat/pr_args.sh",
+    "tools/audit/seat/pr_cap.py",
+    "tools/audit/seat/probe_bridge.py",
     "tools/audit/seat/proof_watch.py",
+    "tools/audit/seat/prune_refs.py",
+    "tools/audit/seat/pulse.py",
     "tools/audit/seat/queue_pre_flight.py",
+    "tools/audit/seat/r10_bash_kill_hook_drive.py",
+    "tools/audit/seat/r10_deeplink_mutants.py",
+    "tools/audit/seat/r10_disinfection_setpoint_mutants.py",
+    "tools/audit/seat/r10_ledger_mutants.py",
+    "tools/audit/seat/r10_mandate_guard_mutants.py",
+    "tools/audit/seat/r10_roster_ops_mutants.py",
+    "tools/audit/seat/r10_roster_sync_mutants.py",
+    "tools/audit/seat/r10_stamp_round_mutants.py",
+    "tools/audit/seat/record_beat.py",
     "tools/audit/seat/record_row.py",
     "tools/audit/seat/ref_privacy.py",
     "tools/audit/seat/remerge_main.sh",
+    "tools/audit/seat/remerge_main_selftest.py",
+    "tools/audit/seat/replay_draws.py",
+    "tools/audit/seat/resume_doc.py",
+    "tools/audit/seat/review_carry.py",
     "tools/audit/seat/review_packet.py",
+    "tools/audit/seat/review_strength.py",
+    "tools/audit/seat/roster_edit.py",
     "tools/audit/seat/roster_lib.py",
+    "tools/audit/seat/roster_queue.py",
+    "tools/audit/seat/roster_sync.py",
+    "tools/audit/seat/round_metrics.py",
+    "tools/audit/seat/round_metrics_selftest.py",
+    "tools/audit/seat/row_position.py",
+    "tools/audit/seat/run_twins.py",
+    "tools/audit/seat/scorecard.py",
+    "tools/audit/seat/scorecard_selftest.py",
     "tools/audit/seat/seat_gen.py",
+    "tools/audit/seat/seat_gen_selftest.py",
+    "tools/audit/seat/selftest_wiring.py",
+    "tools/audit/seat/shell_hazard.py",
+    "tools/audit/seat/state_docs.py",
+    "tools/audit/seat/survivor_list.py",
+    "tools/audit/seat/sweep_driver.py",
+    "tools/audit/seat/sweep_driver_selftest.py",
+    "tools/audit/seat/sweep_gantt.py",
+    "tools/audit/seat/sweep_render.py",
+    "tools/audit/seat/tmp_paths.py",
+    "tools/audit/seat/toolchain.py",
+    "tools/audit/seat/toolchain_selftest.py",
     "tools/audit/seat/topic_grammar.py",
+    "tools/audit/seat/verdict_audit.py",
+    "tools/audit/seat/verify_eight.py",
+    "tools/audit/text_ledger.py",
+    "tools/ci/alert_list.py",
+    "tools/ci/codescan_wait.py",
     "tools/ci/gate.py",
     "tools/ci/ghapi.py",
     "tools/ci/prelude.py",
+    "tools/ci/ruleset_cutover.py",
+    "tools/ci/selftest_scope.py",
+    "tools/ci/sweep.py",
+    "tools/ci/sweep_selftest.py",
+    "tools/coverage/partition.py",
+    "tools/devices/**",
+    "tools/merge/ledger_merge.py",
+    "tools/plan/replan.py",
+    "tools/plan/size_durations.py",
+    "tools/policy/agreement_py.py",
     "tools/policy/budget_raise_gate.py",
     "tools/policy/fixtures/required-contexts.json",
     "tools/policy/policy_lint.mjs",
+    "tools/policy/record-predicate/row_files_replay.py",
+    "tools/policy/role_pack.py",
     "tools/pr/app_approve.sh",
+    "tools/pr/cancel_superseded.py",
+    "tools/pr/ci_predict.py",
+    "tools/pr/codeql_scope.py",
+    "tools/pr/dependabot_merge.py",
+    "tools/pr/depgraph.py",
+    "tools/pr/figure_block.py",
+    "tools/pr/gate_priority.py",
+    "tools/pr/gh_comment.py",
+    "tools/pr/head_note.py",
+    "tools/pr/local_alerts.py",
+    "tools/pr/merge_main_bot.py",
     "tools/pr/outside.py",
-    "tools/release/stamp.py"
+    "tools/release/stamp.py",
+    "tools/replay/**"
    ],
    "probes": [],
    "dirs": [
     ".",
     "tests",
+    "tools",
     "tools/audit",
+    "tools/audit/archscore",
+    "tools/audit/archscore/calibration",
+    "tools/audit/archscore/metrics",
+    "tools/audit/archscore/planted",
+    "tools/audit/archscore/planted/perturb",
+    "tools/audit/archscore/planted/redteam",
+    "tools/audit/round4",
+    "tools/audit/round4/D11",
     "tools/audit/seat",
+    "tools/audit/seat/beatd_shims",
+    "tools/audit/seat/fixtures",
+    "tools/audit/seat/fixtures/beat_jobs",
+    "tools/audit/seat/fixtures/ci_critpath",
+    "tools/audit/seat/hooks",
+    "tools/audit/seat/instruments",
+    "tools/audit/seat/shims",
     "tools/ci",
-    "tools/release"
+    "tools/ci/fixtures",
+    "tools/ci/fixtures/ruleset",
+    "tools/coverage",
+    "tools/devices",
+    "tools/merge",
+    "tools/plan",
+    "tools/policy",
+    "tools/policy/fixtures",
+    "tools/policy/fixtures/figures",
+    "tools/policy/fixtures/policy-loop",
+    "tools/policy/fixtures/policy-rot",
+    "tools/policy/fixtures/policy-rot/hooks",
+    "tools/policy/fixtures/policy-rot/prepr",
+    "tools/policy/fixtures/policy-rot/prepr/raise",
+    "tools/policy/fixtures/policy-rot/prepr/raise/recorded",
+    "tools/policy/fixtures/policy-rot/prepr/upstream",
+    "tools/policy/fixtures/red-ancestry",
+    "tools/policy/fixtures/red-ancestry/bare",
+    "tools/policy/fixtures/red-ancestry/green",
+    "tools/policy/fixtures/red-ancestry/red",
+    "tools/policy/fixtures/roster-probe",
+    "tools/policy/record-predicate",
+    "tools/policy/vendor",
+    "tools/pr",
+    "tools/release",
+    "tools/replay",
+    "tools/site"
    ],
    "index": false,
    "objects": true,
@@ -5333,6 +5509,7 @@
     "tools/audit/repo_root.sh",
     "tools/audit/round4/**",
     "tools/audit/seat/a1_dispatch_arms.sh",
+    "tools/audit/seat/ancestry_calls.sh",
     "tools/audit/seat/autofix_statuses.sh",
     "tools/audit/seat/bare_array.py",
     "tools/audit/seat/beat_jobs.py",
@@ -5432,6 +5609,7 @@
     "tools/audit/seat/seat_gen_selftest.py",
     "tools/audit/seat/seat_venv.sh",
     "tools/audit/seat/selftest_wiring.py",
+    "tools/audit/seat/shell_hazard.py",
     "tools/audit/seat/state_docs.py",
     "tools/audit/seat/survivor_list.py",
     "tools/audit/seat/sweep_driver.py",
@@ -5533,7 +5711,6 @@
     "tools/audit/archscore/planted/perturb/.gitattributes",
     "tools/audit/archscore/planted/redteam/.gitattributes",
     "tools/audit/round4/**",
-    "tools/audit/round4/**",
     "tools/audit/seat",
     "tools/ci/.gitattributes",
     "tools/coverage/.gitattributes",
@@ -5645,6 +5822,7 @@
     "tools/audit/round4/**",
     "tools/audit/seat/INSTRUMENTS.md",
     "tools/audit/seat/a1_dispatch_arms.sh",
+    "tools/audit/seat/ancestry_calls.sh",
     "tools/audit/seat/autofix_statuses.sh",
     "tools/audit/seat/bare_array.py",
     "tools/audit/seat/beat_jobs.py",
@@ -5747,6 +5925,7 @@
     "tools/audit/seat/seat_gen_selftest.py",
     "tools/audit/seat/seat_venv.sh",
     "tools/audit/seat/selftest_wiring.py",
+    "tools/audit/seat/shell_hazard.py",
     "tools/audit/seat/shims/**",
     "tools/audit/seat/state_docs.py",
     "tools/audit/seat/survivor_list.py",
@@ -6016,6 +6195,7 @@
     ".gitignore",
     "AGENTS.md",
     "CLAUDE.md",
+    "CODE_OF_CONDUCT.md",
     "DISCLAIMER.md",
     "LICENSE",
     "NOTICE",
@@ -6137,8 +6317,8 @@
     ".claude/workflows/wave-3l-groups.json",
     ".claude/workflows/wave-x-groups.json",
     ".cursor/**",
-    ".cursor/**",
     ".github/.gitattributes",
+    ".github/ISSUE_TEMPLATE/.gitattributes",
     ".github/actions/.gitattributes",
     ".github/actions/nightly-ha/.gitattributes",
     ".mailmap",
@@ -6154,7 +6334,6 @@
     "dev/archive/.gitattributes",
     "dev/archive/audits/.gitattributes",
     "dev/archive/carries/**",
-    "dev/archive/carries/**",
     "dev/archive/experiments/.gitattributes",
     "dev/archive/experiments/ledger-layout/.gitattributes",
     "dev/archive/handoff/.gitattributes",
@@ -6394,7 +6573,6 @@
     "dev/audit/rounds/round4/D9/reports/.gitattributes",
     "dev/audit/rounds/round4/ledger/.gitattributes",
     "dev/audit/rounds/round5-fix/**",
-    "dev/audit/rounds/round5-fix/**",
     "dev/audit/rounds/round5/.gitattributes",
     "dev/audit/rounds/round5/D0/.gitattributes",
     "dev/audit/rounds/round5/D0/seat-a/.gitattributes",
@@ -6416,12 +6594,9 @@
     "dev/audit/rounds/round5/D2/seat-a/.gitattributes",
     "dev/audit/rounds/round5/D2/seat-b/.gitattributes",
     "dev/audit/rounds/round5/D3/**",
-    "dev/audit/rounds/round5/D3/**",
     "dev/audit/rounds/round5/D4/.gitattributes",
     "dev/audit/rounds/round5/D4/seat-a/.gitattributes",
     "dev/audit/rounds/round5/D7/**",
-    "dev/audit/rounds/round5/D7/**",
-    "dev/audit/rounds/round5/D8/**",
     "dev/audit/rounds/round5/D8/**",
     "dev/audit/rounds/round5/D9/.gitattributes",
     "dev/audit/rounds/round5/D9/seat-b/.gitattributes",
@@ -6444,7 +6619,6 @@
     "dev/audit/rounds/round6/D8/.gitattributes",
     "dev/audit/rounds/round6/D9/.gitattributes",
     "dev/audit/rounds/round7-fix/**",
-    "dev/audit/rounds/round7-fix/**",
     "dev/audit/rounds/round7/.gitattributes",
     "dev/audit/rounds/round7/D0/.gitattributes",
     "dev/audit/rounds/round7/D1/.gitattributes",
@@ -6462,7 +6636,6 @@
     "dev/audit/rounds/round7/D8/.gitattributes",
     "dev/audit/rounds/round7/D9/.gitattributes",
     "dev/audit/rounds/round8-fix/**",
-    "dev/audit/rounds/round8-fix/**",
     "dev/audit/rounds/round8/.gitattributes",
     "dev/audit/rounds/round8/D0/.gitattributes",
     "dev/audit/rounds/round8/D0/s1_logs/.gitattributes",
@@ -6793,6 +6966,7 @@
     "tools/audit/repo_root.sh",
     "tools/audit/round4/**",
     "tools/audit/seat/a1_dispatch_arms.sh",
+    "tools/audit/seat/ancestry_calls.sh",
     "tools/audit/seat/autofix_statuses.sh",
     "tools/audit/seat/bare_array.py",
     "tools/audit/seat/beat_jobs.py",
@@ -6892,6 +7066,7 @@
     "tools/audit/seat/seat_gen_selftest.py",
     "tools/audit/seat/seat_venv.sh",
     "tools/audit/seat/selftest_wiring.py",
+    "tools/audit/seat/shell_hazard.py",
     "tools/audit/seat/state_docs.py",
     "tools/audit/seat/survivor_list.py",
     "tools/audit/seat/sweep_driver.py",
@@ -6993,7 +7168,6 @@
     "tools/audit/archscore/planted/perturb/.gitattributes",
     "tools/audit/archscore/planted/redteam/.gitattributes",
     "tools/audit/round4/**",
-    "tools/audit/round4/**",
     "tools/audit/seat",
     "tools/audit/seat/.gitattributes",
     "tools/audit/seat/hooks/.gitattributes",
@@ -7067,7 +7241,10 @@
     ".gitignore",
     "CLAUDE.md",
     "custom_components/heatpump_optimizer/services.yaml",
+    "dev/audit/harnesses/d907_kernel_band.py",
+    "dev/audit/harnesses/git_auto_maintenance_race.sh",
     "dev/audit/harnesses/mutant_guard.py",
+    "dev/audit/harnesses/r10_product_page.mjs",
     "dev/governance/config/corpus_excluded.json",
     "dev/governance/config/policy_budgets.json",
     "dev/governance/roles/COMMON.md",
@@ -7091,6 +7268,10 @@
     "tests/throwaway_git.py",
     "tests/throwaway_git.sh",
     "tools/audit/carry_audit.py",
+    "tools/audit/judge_batch.py",
+    "tools/audit/repo_root.mjs",
+    "tools/audit/repo_root.py",
+    "tools/audit/repo_root.sh",
     "tools/audit/seat/INSTRUMENTS.md",
     "tools/audit/seat/body_push.sh",
     "tools/audit/seat/cloud-setup.sh",
@@ -7166,6 +7347,7 @@
     ".cursor",
     ".cursor/rules",
     ".github",
+    ".github/ISSUE_TEMPLATE",
     ".github/actions",
     ".github/actions/nightly-ha",
     ".github/workflows",
@@ -7742,6 +7924,7 @@
     "tests/mutation_ledger/killed_by/quiet_windows.py",
     "tests/mutation_ledger/killed_by/repairs.py",
     "tests/mutation_ledger/killed_by/replay_doc.py",
+    "tests/mutation_ledger/killed_by/rooms.py",
     "tests/mutation_ledger/killed_by/running_signal.py",
     "tests/mutation_ledger/killed_by/runs.py",
     "tests/mutation_ledger/killed_by/sensor.py",
@@ -7790,6 +7973,7 @@
     "tests/mutation_ledger/survivor_triage/pump_mode.py",
     "tests/mutation_ledger/survivor_triage/quiet_windows.py",
     "tests/mutation_ledger/survivor_triage/repairs.py",
+    "tests/mutation_ledger/survivor_triage/rooms.py",
     "tests/mutation_ledger/survivor_triage/runs.py",
     "tests/mutation_ledger/survivor_triage/sensor.py",
     "tests/mutation_ledger/survivor_triage/slab_seed.py",
@@ -7982,7 +8166,6 @@
     "tools/audit/archscore/planted/perturb/.gitattributes",
     "tools/audit/archscore/planted/redteam/.gitattributes",
     "tools/audit/round4/**",
-    "tools/audit/round4/**",
     "tools/audit/seat",
     "tools/ci/.gitattributes",
     "tools/ci/fixtures/.gitattributes",
@@ -8638,11 +8821,13 @@
     ".gitignore",
     "AGENTS.md",
     "CLAUDE.md",
+    "CODE_OF_CONDUCT.md",
     "DISCLAIMER.md",
     "LICENSE",
     "NOTICE",
     "README.md",
     "RELEASE_NOTES.md",
+    "ROADMAP.md",
     "SECURITY.md",
     "VERSION",
     "blueprints/**",
@@ -8837,6 +9022,7 @@
     "tests/mutation_ledger/killed_by/quiet_windows.py",
     "tests/mutation_ledger/killed_by/repairs.py",
     "tests/mutation_ledger/killed_by/replay_doc.py",
+    "tests/mutation_ledger/killed_by/rooms.py",
     "tests/mutation_ledger/killed_by/running_signal.py",
     "tests/mutation_ledger/killed_by/runs.py",
     "tests/mutation_ledger/killed_by/sensor.py",
@@ -8884,6 +9070,7 @@
     "tests/mutation_ledger/survivor_triage/pump_mode.py",
     "tests/mutation_ledger/survivor_triage/quiet_windows.py",
     "tests/mutation_ledger/survivor_triage/repairs.py",
+    "tests/mutation_ledger/survivor_triage/rooms.py",
     "tests/mutation_ledger/survivor_triage/runs.py",
     "tests/mutation_ledger/survivor_triage/sensor.py",
     "tests/mutation_ledger/survivor_triage/slab_seed.py",
@@ -9006,6 +9193,7 @@
     "tools/audit/round4/**",
     "tools/audit/seat/INSTRUMENTS.md",
     "tools/audit/seat/a1_dispatch_arms.sh",
+    "tools/audit/seat/ancestry_calls.sh",
     "tools/audit/seat/autofix_statuses.sh",
     "tools/audit/seat/bare_array.py",
     "tools/audit/seat/beat_jobs.py",
@@ -9108,6 +9296,7 @@
     "tools/audit/seat/seat_gen_selftest.py",
     "tools/audit/seat/seat_venv.sh",
     "tools/audit/seat/selftest_wiring.py",
+    "tools/audit/seat/shell_hazard.py",
     "tools/audit/seat/shims/**",
     "tools/audit/seat/state_docs.py",
     "tools/audit/seat/survivor_list.py",
@@ -9527,6 +9716,7 @@
     "tests/mutation_ledger/killed_by/quiet_windows.py/.gitattributes",
     "tests/mutation_ledger/killed_by/repairs.py/.gitattributes",
     "tests/mutation_ledger/killed_by/replay_doc.py/.gitattributes",
+    "tests/mutation_ledger/killed_by/rooms.py/.gitattributes",
     "tests/mutation_ledger/killed_by/running_signal.py/.gitattributes",
     "tests/mutation_ledger/killed_by/runs.py/.gitattributes",
     "tests/mutation_ledger/killed_by/sensor.py/.gitattributes",
@@ -9575,6 +9765,7 @@
     "tests/mutation_ledger/survivor_triage/pump_mode.py/.gitattributes",
     "tests/mutation_ledger/survivor_triage/quiet_windows.py/.gitattributes",
     "tests/mutation_ledger/survivor_triage/repairs.py/.gitattributes",
+    "tests/mutation_ledger/survivor_triage/rooms.py/.gitattributes",
     "tests/mutation_ledger/survivor_triage/runs.py/.gitattributes",
     "tests/mutation_ledger/survivor_triage/sensor.py/.gitattributes",
     "tests/mutation_ledger/survivor_triage/slab_seed.py/.gitattributes",
@@ -9598,7 +9789,6 @@
     "tools/audit/archscore/planted/perturb/.gitattributes",
     "tools/audit/archscore/planted/redteam/.gitattributes",
     "tools/audit/round4/**",
-    "tools/audit/round4/**",
     "tools/audit/seat",
     "tools/ci/.gitattributes",
     "tools/ci/fixtures/.gitattributes",
@@ -9808,6 +9998,7 @@
     "tools/audit/repo_root.sh",
     "tools/audit/round4/**",
     "tools/audit/seat/a1_dispatch_arms.sh",
+    "tools/audit/seat/ancestry_calls.sh",
     "tools/audit/seat/autofix_statuses.sh",
     "tools/audit/seat/bare_array.py",
     "tools/audit/seat/beat_jobs.py",
@@ -9907,6 +10098,7 @@
     "tools/audit/seat/seat_gen_selftest.py",
     "tools/audit/seat/seat_venv.sh",
     "tools/audit/seat/selftest_wiring.py",
+    "tools/audit/seat/shell_hazard.py",
     "tools/audit/seat/state_docs.py",
     "tools/audit/seat/survivor_list.py",
     "tools/audit/seat/sweep_driver.py",
@@ -10008,7 +10200,6 @@
     "tools/audit/archscore/planted/perturb/.gitattributes",
     "tools/audit/archscore/planted/redteam/.gitattributes",
     "tools/audit/round4/**",
-    "tools/audit/round4/**",
     "tools/audit/seat",
     "tools/ci/.gitattributes",
     "tools/coverage/.gitattributes",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
