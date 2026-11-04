# Review packet #3189
head: 5ae7dc79b8c5b67eb0d521d725adbd7e698ec769
base: d7582ed404a87603bd02fefda610d7ebbe4181e1

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=126804609863 neutral
arch-score / arch-score id=126803031526 success
arm id=126802050675 skipped
budget-raise-gate / budget-raise-gate id=126803031655 success
cancel-superseded id=126806720711 success
codeql / Analyze (actions) id=126803031225 success
codeql / Analyze (javascript-typescript) id=126803031328 success
codeql / Analyze (python) id=126803031255 in_progress
governance / delivery-status id=126803031189 success
governance / delivery-status-publish id=126803034925 skipped
governance / env-matrix id=126803031606 success
governance / instrument-self-tests id=126803031136 in_progress
governance / policy-docs id=126803031401 success
governance / record id=126803033665 skipped
governance / wave-script id=126803031199 success
hassfest / hassfest id=126803030917 success
kernel-points id=126803032562 skipped
prelude id=126806717074 in_progress
refresh id=126806719154 success
tests / arch-instrument id=126804185633 success
tests / briefs id=126803031077 success
tests / browser id=126804185647 success
tests / claims-autofix id=126811899942 skipped
tests / closure-scope id=126803031076 success
tests / closures id=126804185734 in_progress
tests / coverage id=126804185480 in_progress
tests / fast (3.14) id=126804185619 success
tests / mutation id=126803031072 success
tests / mutation-autofix id=126803957236 skipped
tests / mutation-pins id=126803955693 skipped
tests / nightly-ha id=126804187776 skipped
tests / nightly-status id=126803031119 failure
tests / replay id=126804187963 skipped
tests / typing id=126804185484 success
validate / validate-hacs id=126803031899 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item ce268b05: R10-PREPR-CAP
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified python3 -c "import sys; sys.path.insert(0,'tests'); import harness_headers as h; print(h.depth_root_seams())"
             python3 runs an inline script rather than a file
  ok         PYTHONPATH=tests/hastub python3 tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_rca_ci_critpath_3/replay.py
             `dev/audit/harnesses/r10_rca_ci_critpath_3/replay.py` is in the tree at this head
  ok         bash tests/derive_closures.sh --single tests/harness_headers.py
             `tests/derive_closures.sh` is in the tree at this head
  ok         tests/harness_headers.py    401 files
             `tests/harness_headers.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 6 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_rca_ci_critpath_3/ci_logs.json b/dev/audit/harnesses/r10_rca_ci_critpath_3/ci_logs.json
new file mode 100644
index 000000000..aad67eec0
--- /dev/null
+++ b/dev/audit/harnesses/r10_rca_ci_critpath_3/ci_logs.json
@@ -0,0 +1,737 @@
+{
+ "source": "GitHub Actions job logs, read 2026-11-04 13:55-14:10 UTC: the closures jobs' first `lane plan:` line and its three lane lines; each fast (3.14) job's per-script `ok ... (Ns)` lines (40-hex SHAs stripped); every successful `tests / closures` and `tests / fast (3.14)` job of the ci.yml push runs 3770..4128 on main with its runner image version (the log's `Runner Image` group)",
+ "closures_lane_plan": {
+  "125121503116": [
+   "lane plan: 3 lane(s) for 34 script(s), bound 3",
+   "  lane 1 (1345.6s recorded): tests/stress.py, tests/harness_headers.py, tests/arch_score_head.py, tests/backtest.py, tests/doc_claims.py, tests/guard_pins.py, tests/typing_ruler.py, tests/frontend.py",
+   "  lane 2 (1345.7s recorded): tests/entities.py, tests/arch_score.py, tests/finite_boundary.py, tests/structure.py, tests/edge.py, tests/config_flow_steps.py, tests/deployment_shape.py, tests/wood_advisor.py, tests/debug_collect.py, tests/solar_alignment.py, tests/block_duty.py, tests/golden.py, tests/open_meteo.py",
+   "  lane 3 (1345.6s recorded): tests/features.py, tests/dst_checks.py, tests/boost_drift_replay.py, tests/plan_view.py, tests/card.mjs, tests/card_drift.mjs, tests/optimality.py, tests/validate.py, tests/layout.py, tests/manual_plan.py, tests/env_drift.py, tests/ha_contract.py, tests/md_tables.mjs"
+  ],
+  "125653313138": [
+   "lane plan: 3 lane(s) for 34 script(s), bound 3",
+   "  lane 1 (1345.6s recorded): tests/stress.py, tests/harness_headers.py, tests/arch_score_head.py, tests/backtest.py, tests/doc_claims.py, tests/guard_pins.py, tests/typing_ruler.py, tests/frontend.py",
+   "  lane 2 (1345.7s recorded): tests/entities.py, tests/arch_score.py, tests/finite_boundary.py, tests/structure.py, tests/edge.py, tests/config_flow_steps.py, tests/deployment_shape.py, tests/wood_advisor.py, tests/debug_collect.py, tests/solar_alignment.py, tests/block_duty.py, tests/golden.py, tests/open_meteo.py",
+   "  lane 3 (1345.6s recorded): tests/features.py, tests/dst_checks.py, tests/boost_drift_replay.py, tests/plan_view.py, tests/card.mjs, tests/card_drift.mjs, tests/optimality.py, tests/validate.py, tests/layout.py, tests/manual_plan.py, tests/env_drift.py, tests/ha_contract.py, tests/md_tables.mjs"
+  ]
+ },
+ "fast_lane_scripts": {
+  "3868": {
+   "job": 125112098863,
+   "script_seconds": {
+    "python3 tests/env_drift.py --claims-only": 0,
+    "python3 tests/closure.py selftest": 5,
+    "python3 tests/validate.py": 22,
+    "python3 tests/edge.py": 27,
+    "python3 tests/backtest.py": 46,
+    "python3 tests/env_drift.py --all": 210,
+    "python3 tests/boost_drift_replay.py": 181,
+    "python3 tests/features.py": 326,
+    "python3 tests/optimality.py": 86,
+    "python3 tests/plan_view.py": 0,
+    "python3 tests/frontend.py": 0,
+    "node tests/card.mjs": 62,
+    "node tests/setup_qa_render.mjs": 1,
+    "node tests/card_drift.mjs": 3,
+    "python3 tests/entities.py": 330,
+    "python3 tests/block_duty.py": 1,
+    "python3 tests/doc_claims.py": 6,
+    "node tests/md_tables.mjs": 0,
+    "python3 tests/wood_advisor.py": 1,
+    "python3 tests/config_flow_steps.py": 10,
+    "python3 tests/structure.py": 13,
+    "python3 tests/typing_ruler.py": 1,
+    "python3 tests/ha_contract.py": 0,
+    "python3 tests/manual_plan.py": 5,
+    "python3 tests/open_meteo.py": 0,
+    "python3 tests/solar_alignment.py": 1,
+    "python3 tests/guard_pins.py": 0,
+    "python3 tests/debug_collect.py": 1,
+    "python3 tests/finite_boundary.py": 42,
+    "python3 tests/layout.py": 3,
+    "python3 tests/deployment_shape.py": 2,
+    "python3 tests/stress.py": 173,
+    "python3 tests/harness_headers.py": 113
+   }
+  },
+  "4009": {
+   "job": 125436393198,
+   "script_seconds": {
+    "python3 tests/env_drift.py --claims-only": 0,
+    "python3 tests/closure.py selftest": 4,
+    "python3 tests/validate.py": 21,
+    "python3 tests/edge.py": 27,
+    "python3 tests/backtest.py": 47,
+    "python3 tests/env_drift.py --all": 231,
+    "python3 tests/boost_drift_replay.py": 188,
+    "python3 tests/features.py": 359,
+    "python3 tests/optimality.py": 89,
+    "python3 tests/plan_view.py": 0,
+    "python3 tests/frontend.py": 1,
+    "node tests/card.mjs": 70,
+    "node tests/setup_qa_render.mjs": 1,
+    "node tests/card_drift.mjs": 3,
+    "python3 tests/entities.py": 374,
+    "python3 tests/block_duty.py": 1,
+    "python3 tests/doc_claims.py": 7,
+    "node tests/md_tables.mjs": 0,
+    "python3 tests/wood_advisor.py": 1,
+    "python3 tests/config_flow_steps.py": 14,
+    "python3 tests/structure.py": 15,
+    "python3 tests/typing_ruler.py": 0,
+    "python3 tests/ha_contract.py": 1,
+    "python3 tests/manual_plan.py": 5,
+    "python3 tests/open_meteo.py": 1,
+    "python3 tests/solar_alignment.py": 0,
+    "python3 tests/guard_pins.py": 1,
+    "python3 tests/debug_collect.py": 1,
+    "python3 tests/finite_boundary.py": 48,
+    "python3 tests/layout.py": 3,
+    "python3 tests/deployment_shape.py": 1,
+    "python3 tests/stress.py": 187,
+    "python3 tests/harness_headers.py": 123
+   }
+  },
+  "4128": {
+   "job": 126534731510,
+   "script_seconds": {
+    "python3 tests/env_drift.py --claims-only": 1,
+    "python3 tests/closure.py selftest": 6,
+    "python3 tests/validate.py": 38,
+    "python3 tests/edge.py": 34,
+    "python3 tests/backtest.py": 145,
+    "python3 tests/env_drift.py --all": 364,
+    "python3 tests/boost_drift_replay.py": 326,
+    "python3 tests/features.py": 673,
+    "python3 tests/optimality.py": 147,
+    "python3 tests/plan_view.py": 1,
+    "python3 tests/frontend.py": 0,
+    "node tests/card.mjs": 114,
+    "node tests/setup_qa_render.mjs": 1,
+    "node tests/card_drift.mjs": 6,
+    "python3 tests/entities.py": 544,
+    "python3 tests/block_duty.py": 1,
+    "python3 tests/doc_claims.py": 11,
+    "node tests/md_tables.mjs": 0,
+    "python3 tests/wood_advisor.py": 1,
+    "python3 tests/config_flow_steps.py": 21,
+    "python3 tests/structure.py": 25,
+    "python3 tests/typing_ruler.py": 0,
+    "python3 tests/ha_contract.py": 0,
+    "python3 tests/manual_plan.py": 9,
+    "python3 tests/open_meteo.py": 0,
+    "python3 tests/solar_alignment.py": 1,
+    "python3 tests/guard_pins.py": 1,
+    "python3 tests/debug_collect.py": 1,
+    "python3 tests/finite_boundary.py": 83,
+    "python3 tests/layout.py": 5,
+    "python3 tests/deployment_shape.py": 3,
+    "python3 tests/stress.py": 367,
+    "python3 tests/harness_headers.py": 208
+   }
+  }
+ },
+ "lane_jobs": [
+  {
+   "run": 3770,
+   "job": 125018714846,
+   "name": "tests / closures",
+   "minutes": 20.1,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3770,
+   "job": 125018714841,
+   "name": "tests / fast (3.14)",
+   "minutes": 24.0,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3771,
+   "job": 125018822399,
+   "name": "tests / closures",
+   "minutes": 33.5,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3771,
+   "job": 125018822416,
+   "name": "tests / fast (3.14)",
+   "minutes": 24.3,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3772,
+   "job": 125019009522,
+   "name": "tests / closures",
+   "minutes": 34.1,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3772,
+   "job": 125019009483,
+   "name": "tests / fast (3.14)",
+   "minutes": 23.6,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3775,
+   "job": 125019516199,
+   "name": "tests / closures",
+   "minutes": 21.2,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3775,
+   "job": 125019516117,
+   "name": "tests / fast (3.14)",
+   "minutes": 18.5,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3779,
+   "job": 125024642530,
+   "name": "tests / closures",
+   "minutes": 33.7,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3779,
+   "job": 125024642293,
+   "name": "tests / fast (3.14)",
+   "minutes": 32.4,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3790,
+   "job": 125038748078,
+   "name": "tests / closures",
+   "minutes": 34.1,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3790,
+   "job": 125038748099,
+   "name": "tests / fast (3.14)",
+   "minutes": 31.9,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3800,
+   "job": 125052214798,
+   "name": "tests / closures",
+   "minutes": 24.4,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3800,
+   "job": 125052214799,
+   "name": "tests / fast (3.14)",
+   "minutes": 31.8,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3817,
+   "job": 125064984425,
+   "name": "tests / closures",
+   "minutes": 33.9,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3817,
+   "job": 125064984409,
+   "name": "tests / fast (3.14)",
+   "minutes": 31.8,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3833,
+   "job": 125082373899,
+   "name": "tests / closures",
+   "minutes": 24.8,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3833,
+   "job": 125082373940,
+   "name": "tests / fast (3.14)",
+   "minutes": 18.2,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3838,
+   "job": 125082717533,
+   "name": "tests / closures",
+   "minutes": 38.6,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3838,
+   "job": 125082717721,
+   "name": "tests / fast (3.14)",
+   "minutes": 30.1,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3849,
+   "job": 125096775127,
+   "name": "tests / fast (3.14)",
+   "minutes": 23.8,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3850,
+   "job": 125097116915,
+   "name": "tests / closures",
+   "minutes": 29.3,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3850,
+   "job": 125097116753,
+   "name": "tests / fast (3.14)",
+   "minutes": 32.5,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3858,
+   "job": 125098039348,
+   "name": "tests / fast (3.14)",
+   "minutes": 24.5,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3859,
+   "job": 125100532528,
+   "name": "tests / closures",
+   "minutes": 21.1,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3859,
+   "job": 125100532526,
+   "name": "tests / fast (3.14)",
+   "minutes": 29.2,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3860,
+   "job": 125110596293,
+   "name": "tests / closures",
+   "minutes": 20.6,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3860,
+   "job": 125110596411,
+   "name": "tests / fast (3.14)",
+   "minutes": 24.8,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3865,
+   "job": 125110920073,
+   "name": "tests / closures",
+   "minutes": 37.7,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3865,
+   "job": 125110919984,
+   "name": "tests / fast (3.14)",
+   "minutes": 19.9,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3867,
+   "job": 125111767216,
+   "name": "tests / closures",
+   "minutes": 38.4,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3867,
+   "job": 125111767352,
+   "name": "tests / fast (3.14)",
+   "minutes": 19.2,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3868,
+   "job": 125112098772,
+   "name": "tests / closures",
+   "minutes": 38.2,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3868,
+   "job": 125112098863,
+   "name": "tests / fast (3.14)",
+   "minutes": 17.7,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3870,
+   "job": 125121503116,
+   "name": "tests / closures",
+   "minutes": 38.2,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3870,
+   "job": 125121503189,
+   "name": "tests / fast (3.14)",
+   "minutes": 32.5,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3896,
+   "job": 125156256364,
+   "name": "tests / closures",
+   "minutes": 39.2,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3896,
+   "job": 125156256327,
+   "name": "tests / fast (3.14)",
+   "minutes": 32.6,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3912,
+   "job": 125171622506,
+   "name": "tests / closures",
+   "minutes": 40.0,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3912,
+   "job": 125171622424,
+   "name": "tests / fast (3.14)",
+   "minutes": 25.3,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3922,
+   "job": 125196988316,
+   "name": "tests / closures",
+   "minutes": 20.9,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3922,
+   "job": 125196988481,
+   "name": "tests / fast (3.14)",
+   "minutes": 24.9,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3937,
+   "job": 125237867631,
+   "name": "tests / closures",
+   "minutes": 39.0,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3937,
+   "job": 125237867493,
+   "name": "tests / fast (3.14)",
+   "minutes": 32.7,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3963,
+   "job": 125292930412,
+   "name": "tests / closures",
+   "minutes": 38.7,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3963,
+   "job": 125292930221,
+   "name": "tests / fast (3.14)",
+   "minutes": 33.5,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3978,
+   "job": 125320698444,
+   "name": "tests / closures",
+   "minutes": 26.8,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3978,
+   "job": 125320698417,
+   "name": "tests / fast (3.14)",
+   "minutes": 29.9,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3984,
+   "job": 125350661773,
+   "name": "tests / closures",
+   "minutes": 21.8,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3984,
+   "job": 125350661907,
+   "name": "tests / fast (3.14)",
+   "minutes": 33.7,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3991,
+   "job": 125379248933,
+   "name": "tests / closures",
+   "minutes": 39.4,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 3991,
+   "job": 125379246970,
+   "name": "tests / fast (3.14)",
+   "minutes": 32.8,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4009,
+   "job": 125436393109,
+   "name": "tests / closures",
+   "minutes": 34.0,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4009,
+   "job": 125436393198,
+   "name": "tests / fast (3.14)",
+   "minutes": 20.4,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4015,
+   "job": 125459855157,
+   "name": "tests / closures",
+   "minutes": 39.0,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4015,
+   "job": 125459855200,
+   "name": "tests / fast (3.14)",
+   "minutes": 34.0,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4028,
+   "job": 125487992256,
+   "name": "tests / closures",
+   "minutes": 18.6,
+   "image": "20261018.50.1"
+  },
+  {
+   "run": 4028,
+   "job": 125487991987,
+   "name": "tests / fast (3.14)",
+   "minutes": 34.9,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4035,
+   "job": 125510679102,
+   "name": "tests / closures",
+   "minutes": 39.7,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4035,
+   "job": 125510679191,
+   "name": "tests / fast (3.14)",
+   "minutes": 27.3,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4036,
+   "job": 125510959329,
+   "name": "tests / closures",
+   "minutes": 38.9,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4036,
+   "job": 125510959429,
+   "name": "tests / fast (3.14)",
+   "minutes": 33.0,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4037,
+   "job": 125511205527,
+   "name": "tests / closures",
+   "minutes": 39.1,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4037,
+   "job": 125511205029,
+   "name": "tests / fast (3.14)",
+   "minutes": 32.6,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4038,
+   "job": 125511409110,
+   "name": "tests / closures",
+   "minutes": 26.9,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4038,
+   "job": 125511409083,
+   "name": "tests / fast (3.14)",
+   "minutes": 30.2,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4040,
+   "job": 125511888757,
+   "name": "tests / closures",
+   "minutes": 20.8,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4040,
+   "job": 125511889110,
+   "name": "tests / fast (3.14)",
+   "minutes": 33.2,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4044,
+   "job": 125511986586,
+   "name": "tests / closures",
+   "minutes": 39.3,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4044,
+   "job": 125511986604,
+   "name": "tests / fast (3.14)",
+   "minutes": 33.7,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4045,
+   "job": 125512444818,
+   "name": "tests / closures",
+   "minutes": 39.6,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4045,
+   "job": 125512444712,
+   "name": "tests / fast (3.14)",
+   "minutes": 32.7,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4046,
+   "job": 125514460617,
+   "name": "tests / closures",
+   "minutes": 39.0,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4046,
+   "job": 125514460092,
+   "name": "tests / fast (3.14)",
+   "minutes": 33.6,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4055,
+   "job": 125653313138,
+   "name": "tests / closures",
+   "minutes": 20.6,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4055,
+   "job": 125653312947,
+   "name": "tests / fast (3.14)",
+   "minutes": 32.1,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4056,
+   "job": 125725515174,
+   "name": "tests / closures",
+   "minutes": 24.1,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4056,
+   "job": 125725515225,
+   "name": "tests / fast (3.14)",
+   "minutes": 32.7,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4080,
+   "job": 126466350856,
+   "name": "tests / closures",
+   "minutes": 20.1,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4080,
+   "job": 126466350742,
+   "name": "tests / fast (3.14)",
+   "minutes": 33.8,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4107,
+   "job": 126498194600,
+   "name": "tests / closures",
+   "minutes": 39.4,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4107,
+   "job": 126498194813,
+   "name": "tests / fast (3.14)",
+   "minutes": 33.4,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4116,
+   "job": 126516291086,
+   "name": "tests / closures",
+   "minutes": 26.6,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4116,
+   "job": 126516291606,
+   "name": "tests / fast (3.14)",
+   "minutes": 33.2,
+   "image": "20261025.179.1"
+  },
+  {
+   "run": 4128,
+   "job": 126534731365,
+   "name": "tests / closures",
+   "minutes": 38.5,
+   "image": "20261101.186.1"
+  },
+  {
+   "run": 4128,
+   "job": 126534731510,
+   "name": "tests / fast (3.14)",
+   "minutes": 33.4,
+   "image": "20261101.186.1"
+  }
+ ]
+}
diff --git a/dev/audit/harnesses/r10_rca_ci_critpath_3/replay.py b/dev/audit/harnesses/r10_rca_ci_critpath_3/replay.py
new file mode 100644
index 000000000..f95c1f93b
--- /dev/null
+++ b/dev/audit/harnesses/r10_rca_ci_critpath_3/replay.py
@@ -0,0 +1,285 @@
+#!/usr/bin/env python3
+"""R10-RCA-CI-CRITPATH-3: replay main's third and fourth `GREW critical_path_minutes`.
+
+Reads the tree, three git objects and the fixtures beside this file. No network.
+Every grade runs the ratchet the red commit itself ran: tests/ci_ratchet.py as
+of that commit, read with `git show` and imported by spec, so a later change to
+the live file cannot move a reproduction (review of #3189: the live file graded
+the third red's window 21.967 after #3180).
+
+  runs.json      ci.yml push runs on main 3775..4056 with their jobs
+  runs_red4.json ci.yml push runs on main 4009..4128 with their jobs
+  ci_logs.json   lane-plan lines of two closures jobs, the per-script seconds of
+                 three fast (3.14) jobs, every heavy-lane job's runner image
+
+  1. reproduce  -- the window graded at 8f286293b, through that commit's
+                   run_minutes and critical_path_minutes: 36.5, GREW against
+                   budget 34.267 + band 1.3.
+  2. cause      -- every graded window from 11-02, the 8-run median beside the
+                   count of runs whose `tests / closures` lane drew the slow
+                   host class (> 30 min for the same 34-script plan).
+  3. candidate  -- the PLANNED critical path (tests/closure.py lane_plan over
+                   tests/closures.json's recorded seconds, 3 lanes) at this tree;
+                   a determinism check (the same input twice: it controls
+                   nothing about hosts); a perturbation it must detect (one
+                   script +300 s); and the lane totals CI printed in a 38.2-min
+                   and a 20.6-min closures job, which must equal the tree's.
+  4. fourth red -- the window graded at 8e90d8144, through that commit's
+                   window_work_minutes: 29.067, GREW against 21.983 + 1.3; the
+                   window one push earlier (616868bdc) ok; the fast (3.14)
+                   price in each, the last fast (3.14) run under 26 min, and
+                   the fast (3.14) price in the window #3180 recorded 21.983 from.
+  5. host       -- the same 33 fast (3.14) scripts in runs 4009 and 4128: every
+                   one slower, none added; the runner image of every heavy-lane
+                   job, which does not separate fast from slow.
+  6. at red 4   -- the planned path read from tests/closures.json at c3a279e32
+                   (red 3) and 8e90d8144 (red 4): equal.
+
+Exit 0 when every step holds as the record states, 1 otherwise.
+"""
+from __future__ import annotations
+
+import importlib.util
+import json
+import statistics
+import subprocess
+import sys
+import tempfile
+from pathlib import Path
+
+def repo_root(start):
+    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
+    from pathlib import Path
+    here = Path(start).resolve()
+    if here.is_file():
+        here = here.parent
+    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
+    for cand in (here, *here.parents):
+        if (cand / marker).is_file():
+            return cand
+    raise RuntimeError(f"no repository root above {start}")
+
+
+HERE = Path(__file__).resolve().parent
+ROOT = repo_root(HERE)
+sys.path.insert(0, str(ROOT))
+sys.path.insert(0, str(ROOT / "tests"))
+
+import closure  # noqa: E402
+
+RED3_SHA, RED3_BUDGET, RED3_BAND = "8f286293b", 34.267, 1.3
+RED4_SHA, RED4_BUDGET, RED4_BAND = "8e90d8144", 21.983, 1.3
+SLOW_CLOSURES_MIN = 30.0
+FAST_HOST_FAST_LANE_MIN = 26.0
+FAST_LANE = "tests / fast (3.14)"
+
+
+def _ratchet_at(sha: str, td: str):
+    """tests/ci_ratchet.py exactly as `sha` ran it."""
+    src = subprocess.run(["git", "show", f"{sha}:tests/ci_ratchet.py"], cwd=ROOT,
+                         check=True, capture_output=True, text=True).stdout
+    path = Path(td) / f"ci_ratchet_{sha}.py"
+    path.write_text(src)
+    spec = importlib.util.spec_from_file_location(f"ci_ratchet_{sha}", path)
+    mod = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(mod)
+    return mod
+
+
+def _runs(name: str) -> list[dict]:
+    runs = json.loads((HERE / name).read_text())["workflow_runs"]
+    return sorted(runs, key=lambda r: r["created_at"])
+
+
+def _lane_minutes(cr, r: dict, lane: str) -> "float | None":
+    for j in r["jobs"]:
+        if j["name"] == lane and j.get("started_at") and j.get("completed_at"):
+            return (cr._at(j["completed_at"]) - cr._at(j["started_at"])).total_seconds() / 60
+    return None
+
+
+def _graded_window(runs: list[dict], sha: str, width: int) -> list[dict]:
+    """What ci-ratchet's gather read on `sha`'s own push run: that run, still
+    in progress, and the `width - 1` runs before it."""
+    i = next(k for k, r in enumerate(runs) if r["head_sha"].startswith(sha))
+    return runs[max(0, i - width + 1):i] + [{**runs[i], "status": "in_progress"}]
+
+
+def reproduce(cr3, td: str) -> bool:
+    window = _graded_window(_runs("runs.json"), RED3_SHA, 8)
+    p = Path(td) / "red3.json"
+    p.write_text(json.dumps({"workflow_runs": window}))
+    graded = cr3.critical_path_minutes(p)
+    grew = graded > RED3_BUDGET + RED3_BAND
+    print(f"1. reproduce: window at {RED3_SHA} grades {graded} with ci_ratchet.py as of "
+          f"{RED3_SHA} (budget {RED3_BUDGET} + band {RED3_BAND} = "
+          f"{RED3_BUDGET + RED3_BAND:.3f}): {'GREW' if grew else 'ok'}")
+    return graded == 36.5 and grew
+
+
+def cause(cr3) -> bool:
+    runs = _runs("runs.json")
+    print("2. cause: graded median vs slow-host draws in the window")
+    rows = []
+    for i in range(8, len(runs) + 1):
+        w = runs[i - 8:i]
+        counted = [r for r in w if cr3.run_minutes(r) is not None]
+        ms = [cr3.run_minutes(r) for r in counted]
+        slow = sum(1 for r in counted
+                   if (_lane_minutes(cr3, r, "tests / closures") or 0) > SLOW_CLOSURES_MIN)
+        med = statistics.median(ms)
+        rows.append((slow / len(counted), med))
+        print(f"   after {w[-1]['head_sha'][:9]}  median {med:6.3f}  "
+              f"slow closures draws {slow}/{len(counted)}  "
+              f"{'GREW' if med > RED3_BUDGET + RED3_BAND else 'ok'}")
+    lo = [m for s, m in rows if s < 0.5]
+    hi = [m for s, m in rows if s > 0.7]
+    graded = sum(1 for r in runs if cr3.run_minutes(r) is not None)
+    print(f"   windows where under half the graded runs drew the slow closures "
+          f"host: {len(lo)}, max median {max(lo):.3f}; over 70%: {len(hi)}, "
+          f"min median {min(hi):.3f}")
+    print(f"   runs.json: {len(runs)} runs {runs[0]['run_number']}..{runs[-1]['run_number']}, "
+          f"{graded} graded by run_minutes")
+    return bool(lo and hi) and max(lo) <= RED3_BUDGET + RED3_BAND < min(hi)
+
+
+def _secs(recorded: dict, s: str) -> float:
+    r = recorded.get(s)
+    return float(r.get("seconds", 0.0)) if isinstance(r, dict) else 0.0
+
+
+def _planned(recorded: dict, scripts: list[str]) -> float:
+    lanes = closure.lane_plan(scripts, recorded, 3)
+    return round(max(sum(_secs(recorded, s) for s in ln) for ln in lanes), 1)
+
+
+def _scripts(td: str) -> list[str]:
+    out = Path(td) / "lane-plan"
+    subprocess.run([sys.executable, str(ROOT / "tests/closure.py"), "lane-plan",
+                    "--all-scripts", "--lanes", "3", "--out-dir", str(out)],
+                   cwd=ROOT, check=True, capture_output=True, text=True)
+    return (out / "scripts.txt").read_text().split()
+
+
+def candidate(scripts: list[str]) -> bool:
+    recorded = json.loads((ROOT / "tests/closures.json").read_text())["recorded"]
+    a, b = _planned(recorded, scripts), _planned(recorded, scripts)
+    bumped = json.loads(json.dumps(recorded))
+    bumped["tests/stress.py"]["seconds"] = float(bumped["tests/stress.py"]["seconds"]) + 300
+    c = _planned(bumped, scripts)
+    print(f"3. candidate: planned critical path {a}s over {len(scripts)} scripts; "
+          f"determinism (same input again) {b}s; stress.py +300s -> {c}s")
+    logs = json.loads((HERE / "ci_logs.json").read_text())["closures_lane_plan"]
+    ci_ok = True
+    for job, lines in logs.items():
+        totals = [float(ln.split("(")[1].split("s recorded")[0]) for ln in lines[1:]]
+        print(f"   CI job {job}: {lines[0].strip()!r}, lane totals {totals}, longest {max(totals)}")
+        ci_ok = ci_ok and max(totals) == a and len(totals) == 3
+    return a == b and c > a and ci_ok
+
+
+def fourth(cr4, td: str) -> bool:
+    runs = _runs("runs_red4.json")
+    out = []
+    for sha in ("616868bdc", RED4_SHA):
+        window = _graded_window(runs, sha, cr4.PUSH_WINDOW)
+        p = Path(td) / f"red4-{sha}.json"
+        p.write_text(json.dumps({"workflow_runs": window}))
+        graded = cr4.critical_path_minutes(p)
+        fast = [(round(m, 2), r["run_number"]) for r in window
+                if cr4._walk(r) is not None
+                for j in r["jobs"] if j["name"] == FAST_LANE and j["conclusion"] == "success"
+                for m in [_lane_minutes(cr4, r, FAST_LANE)]]
+        floor = statistics.median(m for m, _ in fast) * cr4.OTHER_WORK_FRACTION
+        price = min((m, n) for m, n in fast if m >= floor)
+        under = [n for m, n in fast if m < FAST_HOST_FAST_LANE_MIN]
+        grew = graded > RED4_BUDGET + RED4_BAND
+        print(f"4. window at {sha} (runs {window[0]['run_number']}..{window[-1]['run_number']}) "
+              f"grades {graded} with ci_ratchet.py as of {RED4_SHA} (budget {RED4_BUDGET} + "
+              f"band {RED4_BAND}): {'GREW' if grew else 'ok'}; fast (3.14) priced {price[0]} "
+              f"(run {price[1]}) over {len(fast)} success runs, under "
+              f"{FAST_HOST_FAST_LANE_MIN:.0f} min: {under or 'none'}")
+        out.append((graded, grew, price, under))
+    (_, grew3, _, under3), (g4, grew4, price4, under4) = out
+    rec = _record_fast_price(cr4)
+    print(f"   #3180's record: its largest window ({rec[2]}) reads {rec[0]}, fast (3.14) "
+          f"priced {rec[1]}; red 4 reads {g4 - rec[0]:.3f} over it, fast (3.14) "
+          f"{price4[0] - rec[1]:.2f} over")
+    return (not grew3 and grew4 and g4 == 29.067 and under3 == [4009] and not under4
+            and price4 == (27.33, 4035) and rec[0] == RED4_BUDGET)
+
+
+def _record_fast_price(cr4) -> tuple[float, float, str]:
+    """The fast (3.14) price in the window #3180 recorded its budget from:
+    its own runs.json, read as critical_path_minutes(stat="record") reads it."""
+    p = ROOT / "dev/audit/harnesses/r10_hotfix_ci_critpath_3/runs.json"
+    runs = sorted(json.loads(p.read_text())["workflow_runs"],
+                  key=lambda r: r.get("created_at") or "", reverse=True)
+    spans = [runs[i:i + cr4.PUSH_WINDOW] for i in range(len(runs) - cr4.PUSH_WINDOW + 1)]
+    value, span = max(((cr4.window_work_minutes(s), s) for s in spans), key=lambda t: t[0])
+    seen = [w["work"] for r in span for w in (cr4._walk(r) or [])
+            if w["name"] == FAST_LANE and w["priced"]]
+    floor = statistics.median(seen) * cr4.OTHER_WORK_FRACTION
+    price = round(min(x for x in seen if x >= floor) / 60, 2)
+    nums = [r.get("run_number") for r in span]
+    return value, price, f"runs {min(nums)}..{max(nums)}"
+
+
+def host() -> bool:
+    logs = json.loads((HERE / "ci_logs.json").read_text())
+    fast_run, slow_run = logs["fast_lane_scripts"]["4009"], logs["fast_lane_scripts"]["4128"]
+    f, s = fast_run["script_seconds"], slow_run["script_seconds"]
+    same = set(f) == set(s)
+    ratios = sorted(s[k] / f[k] for k in f if f[k] >= 10)
+    print(f"5. host: fast (3.14) job {fast_run['job']} (run 4009) vs {slow_run['job']} (run 4128): "
+          f"{len(f)} vs {len(s)} scripts, same set {same}; summed {sum(f.values())}s vs "
+          f"{sum(s.values())}s (x{sum(s.values()) / sum(f.values()):.2f}); per-script ratio "
+          f"{ratios[0]:.2f}..{ratios[-1]:.2f} over the {len(ratios)} scripts of >= 10 s")
+    jobs = logs["lane_jobs"]
+    fast_lane = [j for j in jobs if j["name"] == FAST_LANE]
+    by_img: dict[str, list[float]] = {}
+    for j in fast_lane:
+        by_img.setdefault(j["image"], []).append(j["minutes"])
+    span = {k: (len(v), min(v), max(v)) for k, v in sorted(by_img.items())}
+    first = [j for j in fast_lane if j["run"] <= 4009]
+    later = [j for j in fast_lane if j["run"] > 4009]
+    nf = sum(j["minutes"] < FAST_HOST_FAST_LANE_MIN for j in first)
+    nl = sum(j["minutes"] < FAST_HOST_FAST_LANE_MIN for j in later)
+    cl = [j for j in jobs if j["name"] == "tests / closures" and j["run"] > 4009]
+    ncl = sum(j["minutes"] < 27 for j in cl)
+    print(f"   fast (3.14) by runner image (n, min, max): {span}")
+    img_pair = (next(j["image"] for j in fast_lane if j["run"] == 4009),
+                next(j["image"] for j in fast_lane if j["run"] == 4128))
+    print(f"   the 4009 vs 4128 comparison crosses an image change: {img_pair[0] != img_pair[1]} "
+          f"({img_pair[0]} vs {img_pair[1]}); same-image slow job, run 4035: "
+          f"{next(j['minutes'] for j in fast_lane if j['run'] == 4035)} min on "
+          f"{next(j['image'] for j in fast_lane if j['run'] == 4035)}")
+    print(f"   fast (3.14) under {FAST_HOST_FAST_LANE_MIN:.0f} min: {nf} of {len(first)} "
+          f"runs 3770..4009, {nl} of {len(later)} after; closures under 27 min after "
+          f"4009: {ncl} of {len(cl)}")
+    img_4009_4116 = {j["image"] for j in fast_lane if 4009 <= j["run"] <= 4116}
+    return same and ratios[0] > 1 and nl == 0 and nf > 0 and len(img_4009_4116) == 1
+
+
+def at_red4(scripts: list[str]) -> bool:
+    vals = {}
+    for sha in ("c3a279e32", RED4_SHA):
+        rec = json.loads(subprocess.run(["git", "show", f"{sha}:tests/closures.json"], cwd=ROOT,
+                                        check=True, capture_output=True, text=True).stdout)["recorded"]
+        vals[sha] = _planned(rec, scripts)
+    print(f"6. planned critical path from tests/closures.json at red 3 / red 4: {vals}")
+    return len(set(vals.values())) == 1
+
+
+def main() -> int:
+    with tempfile.TemporaryDirectory() as td:
+        cr3, cr4 = _ratchet_at(RED3_SHA, td), _ratchet_at(RED4_SHA, td)
+        scripts = _scripts(td)
+        ok = [reproduce(cr3, td), cause(cr3), candidate(scripts), fourth(cr4, td),
+              host(), at_red4(scripts)]
+    print("RESULT:", "holds" if all(ok) else f"does NOT hold {ok}")
+    return 0 if all(ok) else 1
+
+
+if __name__ == "__main__":
+    sys.exit(main())
diff --git a/dev/audit/harnesses/r10_rca_ci_critpath_3/runs.json b/dev/audit/harnesses/r10_rca_ci_critpath_3/runs.json
new file mode 100644
index 000000000..9b483e789
--- /dev/null
+++ b/dev/audit/harnesses/r10_rca_ci_critpath_3/runs.json
@@ -0,0 +1,9088 @@
+{
+"source":"GitHub Actions API: ci.yml push runs on main 2026-11-01T23:43Z..2026-11-03T04:23Z, each with its latest-attempt jobs, reduced to the fields tests/ci_ratchet.py run_minutes reads",
+"workflow_runs":[
+{
+"id":41363701362,
+"run_number":3775,
+"head_sha":"9644fb7d02d7c5e175ae5a1a91128e3556baf6b1",
+"created_at":"2026-11-01T23:46:08Z",
+"status":"completed",
+"conclusion":"success",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-01T23:46:09Z",
+"started_at":"2026-11-01T23:46:45Z",
+"completed_at":"2026-11-01T23:47:03Z",
+"conclusion":"success"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-01T23:46:09Z",
+"started_at":"2026-11-01T23:46:09Z",
+"completed_at":"2026-11-01T23:46:09Z",
+"conclusion":"skipped"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-01T23:46:09Z",
+"started_at":"2026-11-01T23:46:09Z",
+"completed_at":"2026-11-01T23:46:09Z",
+"conclusion":"skipped"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-01T23:47:06Z",
+"completed_at":"2026-11-01T23:47:43Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-01T23:50:52Z",
+"completed_at":"2026-11-02T00:33:22Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-02T00:04:55Z",
+"completed_at":"2026-11-02T00:05:24Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-01T23:48:40Z",
+"completed_at":"2026-11-01T23:49:49Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-01T23:48:40Z",
+"completed_at":"2026-11-01T23:49:30Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-02T00:05:00Z",
+"completed_at":"2026-11-02T00:05:48Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-01T23:57:09Z",
+"completed_at":"2026-11-02T00:03:50Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-01T23:57:22Z",
+"completed_at":"2026-11-02T00:22:42Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-02T00:02:25Z",
+"completed_at":"2026-11-02T00:05:40Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-02T00:01:50Z",
+"completed_at":"2026-11-02T00:02:38Z",
+"conclusion":"success"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-01T23:47:48Z",
+"completed_at":"2026-11-01T23:48:06Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-02T00:06:01Z",
+"completed_at":"2026-11-02T00:24:33Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-02T00:05:43Z",
+"completed_at":"2026-11-02T00:37:22Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-02T00:08:30Z",
+"completed_at":"2026-11-02T00:10:20Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-02T00:08:36Z",
+"completed_at":"2026-11-02T00:12:56Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-02T00:07:50Z",
+"completed_at":"2026-11-02T00:29:04Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-02T00:02:45Z",
+"completed_at":"2026-11-02T00:03:11Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-02T00:03:14Z",
+"completed_at":"2026-11-02T00:04:34Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-02T00:09:22Z",
+"completed_at":"2026-11-02T00:27:01Z",
+"conclusion":"success"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-01T23:47:03Z",
+"completed_at":"2026-11-01T23:47:03Z",
+"conclusion":"skipped"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-01T23:47:03Z",
+"completed_at":"2026-11-01T23:47:03Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-01T23:47:03Z",
+"completed_at":"2026-11-01T23:47:03Z",
+"conclusion":"skipped"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-01T23:47:03Z",
+"completed_at":"2026-11-01T23:47:03Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-01T23:47:03Z",
+"completed_at":"2026-11-01T23:47:03Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-01T23:47:03Z",
+"completed_at":"2026-11-01T23:47:03Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-01T23:47:03Z",
+"completed_at":"2026-11-01T23:47:03Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-01T23:47:03Z",
+"started_at":"2026-11-01T23:47:03Z",
+"completed_at":"2026-11-01T23:47:03Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T00:05:49Z",
+"started_at":"2026-11-02T00:05:49Z",
+"completed_at":"2026-11-02T00:05:48Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T00:05:49Z",
+"started_at":"2026-11-02T00:05:49Z",
+"completed_at":"2026-11-02T00:05:48Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T00:24:33Z",
+"started_at":"2026-11-02T00:24:33Z",
+"completed_at":"2026-11-02T00:24:33Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T00:27:01Z",
+"started_at":"2026-11-02T00:27:04Z",
+"completed_at":"2026-11-02T00:27:12Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T00:27:02Z",
+"started_at":"2026-11-02T00:27:02Z",
+"completed_at":"2026-11-02T00:27:01Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T00:29:05Z",
+"started_at":"2026-11-02T00:29:07Z",
+"completed_at":"2026-11-02T00:30:18Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T00:29:05Z",
+"started_at":"2026-11-02T00:29:05Z",
+"completed_at":"2026-11-02T00:29:05Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T00:37:22Z",
+"started_at":"2026-11-02T00:37:24Z",
+"completed_at":"2026-11-02T00:37:43Z",
+"conclusion":"success"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T00:37:22Z",
+"started_at":"2026-11-02T00:37:22Z",
+"completed_at":"2026-11-02T00:37:22Z",
+"conclusion":"skipped"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T00:37:22Z",
+"started_at":"2026-11-02T00:37:22Z",
+"completed_at":"2026-11-02T00:37:22Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41365303753,
+"run_number":3779,
+"head_sha":"78dd34354e8300bdff2f660db9cc778ab4a9e4d7",
+"created_at":"2026-11-02T00:05:51Z",
+"status":"completed",
+"conclusion":"success",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T00:05:52Z",
+"started_at":"2026-11-02T00:07:40Z",
+"completed_at":"2026-11-02T00:07:57Z",
+"conclusion":"success"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T00:05:52Z",
+"started_at":"2026-11-02T00:05:52Z",
+"completed_at":"2026-11-02T00:05:52Z",
+"conclusion":"skipped"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T00:05:52Z",
+"started_at":"2026-11-02T00:05:52Z",
+"completed_at":"2026-11-02T00:05:52Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:08:44Z",
+"completed_at":"2026-11-02T00:13:52Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:11:23Z",
+"completed_at":"2026-11-02T00:15:25Z",
+"conclusion":"success"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:12:13Z",
+"completed_at":"2026-11-02T00:12:54Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:09:33Z",
+"completed_at":"2026-11-02T00:10:19Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:13:42Z",
+"completed_at":"2026-11-02T00:15:07Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:11:37Z",
+"completed_at":"2026-11-02T00:38:12Z",
+"conclusion":"success"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:14:56Z",
+"completed_at":"2026-11-02T00:15:17Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:13:45Z",
+"completed_at":"2026-11-02T00:40:56Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:12:59Z",
+"completed_at":"2026-11-02T00:13:42Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:12:45Z",
+"completed_at":"2026-11-02T00:13:17Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:14:19Z",
+"completed_at":"2026-11-02T00:14:59Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:15:21Z",
+"completed_at":"2026-11-02T00:19:36Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:15:42Z",
+"completed_at":"2026-11-02T00:16:25Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:13:54Z",
+"completed_at":"2026-11-02T00:43:50Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:13:26Z",
+"completed_at":"2026-11-02T00:45:52Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:14:26Z",
+"completed_at":"2026-11-02T00:46:24Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:15:19Z",
+"completed_at":"2026-11-02T00:16:45Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:14:46Z",
+"completed_at":"2026-11-02T00:19:00Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:16:24Z",
+"completed_at":"2026-11-02T00:50:07Z",
+"conclusion":"success"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:07:58Z",
+"completed_at":"2026-11-02T00:07:57Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:07:58Z",
+"completed_at":"2026-11-02T00:07:58Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:07:58Z",
+"completed_at":"2026-11-02T00:07:57Z",
+"conclusion":"skipped"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:07:58Z",
+"completed_at":"2026-11-02T00:07:57Z",
+"conclusion":"skipped"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:07:58Z",
+"completed_at":"2026-11-02T00:07:57Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:07:58Z",
+"completed_at":"2026-11-02T00:07:58Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:07:58Z",
+"completed_at":"2026-11-02T00:07:58Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T00:07:58Z",
+"started_at":"2026-11-02T00:07:58Z",
+"completed_at":"2026-11-02T00:07:58Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T00:13:18Z",
+"started_at":"2026-11-02T00:13:18Z",
+"completed_at":"2026-11-02T00:13:17Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T00:13:18Z",
+"started_at":"2026-11-02T00:13:18Z",
+"completed_at":"2026-11-02T00:13:17Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T00:43:50Z",
+"started_at":"2026-11-02T00:43:53Z",
+"completed_at":"2026-11-02T00:44:00Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T00:43:51Z",
+"started_at":"2026-11-02T00:43:51Z",
+"completed_at":"2026-11-02T00:43:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T00:45:53Z",
+"started_at":"2026-11-02T00:45:53Z",
+"completed_at":"2026-11-02T00:45:52Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T00:46:24Z",
+"started_at":"2026-11-02T00:46:24Z",
+"completed_at":"2026-11-02T00:46:24Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T00:50:07Z",
+"started_at":"2026-11-02T00:50:11Z",
+"completed_at":"2026-11-02T00:51:35Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T00:50:08Z",
+"started_at":"2026-11-02T00:50:08Z",
+"completed_at":"2026-11-02T00:50:07Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T00:51:35Z",
+"started_at":"2026-11-02T00:51:38Z",
+"completed_at":"2026-11-02T00:51:59Z",
+"conclusion":"success"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T00:51:36Z",
+"started_at":"2026-11-02T00:51:36Z",
+"completed_at":"2026-11-02T00:51:35Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41370135038,
+"run_number":3790,
+"head_sha":"76801494f3ab8639797a96622d5da427a28b03ee",
+"created_at":"2026-11-02T01:00:11Z",
+"status":"completed",
+"conclusion":"success",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T01:00:12Z",
+"started_at":"2026-11-02T01:00:15Z",
+"completed_at":"2026-11-02T01:00:36Z",
+"conclusion":"success"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T01:00:12Z",
+"started_at":"2026-11-02T01:00:12Z",
+"completed_at":"2026-11-02T01:00:12Z",
+"conclusion":"skipped"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T01:00:12Z",
+"started_at":"2026-11-02T01:00:12Z",
+"completed_at":"2026-11-02T01:00:12Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:00:39Z",
+"completed_at":"2026-11-02T01:01:22Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:00:42Z",
+"completed_at":"2026-11-02T01:01:19Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:00:39Z",
+"completed_at":"2026-11-02T01:01:48Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:00:39Z",
+"completed_at":"2026-11-02T01:27:30Z",
+"conclusion":"success"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:00:39Z",
+"completed_at":"2026-11-02T01:01:18Z",
+"conclusion":"success"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:00:44Z",
+"completed_at":"2026-11-02T01:01:02Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:00:40Z",
+"completed_at":"2026-11-02T01:07:23Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:00:39Z",
+"completed_at":"2026-11-02T01:01:23Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:00:39Z",
+"completed_at":"2026-11-02T01:02:19Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:00:39Z",
+"completed_at":"2026-11-02T01:01:23Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:00:48Z",
+"completed_at":"2026-11-02T01:33:49Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:00:58Z",
+"completed_at":"2026-11-02T01:01:25Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:01:02Z",
+"completed_at":"2026-11-02T01:01:32Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:00:57Z",
+"completed_at":"2026-11-02T01:05:13Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:01:05Z",
+"completed_at":"2026-11-02T01:01:42Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:00:59Z",
+"completed_at":"2026-11-02T01:32:47Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:01:25Z",
+"completed_at":"2026-11-02T01:35:33Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:01:34Z",
+"completed_at":"2026-11-02T01:33:25Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:01:48Z",
+"completed_at":"2026-11-02T01:03:11Z",
+"conclusion":"success"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:00:37Z",
+"completed_at":"2026-11-02T01:00:36Z",
+"conclusion":"skipped"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:00:37Z",
+"completed_at":"2026-11-02T01:00:36Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:00:37Z",
+"completed_at":"2026-11-02T01:00:36Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:00:37Z",
+"completed_at":"2026-11-02T01:00:36Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:00:37Z",
+"completed_at":"2026-11-02T01:00:37Z",
+"conclusion":"skipped"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:00:37Z",
+"completed_at":"2026-11-02T01:00:36Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:00:37Z",
+"completed_at":"2026-11-02T01:00:37Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T01:00:37Z",
+"started_at":"2026-11-02T01:00:37Z",
+"completed_at":"2026-11-02T01:00:36Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T01:01:19Z",
+"started_at":"2026-11-02T01:01:19Z",
+"completed_at":"2026-11-02T01:01:19Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T01:01:19Z",
+"started_at":"2026-11-02T01:01:19Z",
+"completed_at":"2026-11-02T01:01:19Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T01:01:42Z",
+"started_at":"2026-11-02T01:02:44Z",
+"completed_at":"2026-11-02T01:02:55Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T01:01:43Z",
+"started_at":"2026-11-02T01:01:43Z",
+"completed_at":"2026-11-02T01:01:42Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T01:33:26Z",
+"started_at":"2026-11-02T01:33:26Z",
+"completed_at":"2026-11-02T01:33:25Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T01:33:26Z",
+"started_at":"2026-11-02T01:33:26Z",
+"completed_at":"2026-11-02T01:33:25Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T01:35:35Z",
+"started_at":"2026-11-02T01:35:38Z",
+"completed_at":"2026-11-02T01:36:50Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T01:35:35Z",
+"started_at":"2026-11-02T01:35:35Z",
+"completed_at":"2026-11-02T01:35:35Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T01:36:51Z",
+"started_at":"2026-11-02T01:36:53Z",
+"completed_at":"2026-11-02T01:37:18Z",
+"conclusion":"success"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T01:36:51Z",
+"started_at":"2026-11-02T01:36:51Z",
+"completed_at":"2026-11-02T01:36:50Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41374627366,
+"run_number":3800,
+"head_sha":"94d8b47f6c6bf6ace1191280ffdd41dba6b13ab4",
+"created_at":"2026-11-02T01:51:19Z",
+"status":"completed",
+"conclusion":"success",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T01:51:20Z",
+"started_at":"2026-11-02T01:51:23Z",
+"completed_at":"2026-11-02T01:51:50Z",
+"conclusion":"success"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T01:51:20Z",
+"started_at":"2026-11-02T01:51:20Z",
+"completed_at":"2026-11-02T01:51:19Z",
+"conclusion":"skipped"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T01:51:20Z",
+"started_at":"2026-11-02T01:51:20Z",
+"completed_at":"2026-11-02T01:51:19Z",
+"conclusion":"skipped"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T01:51:50Z",
+"started_at":"2026-11-02T01:51:53Z",
+"completed_at":"2026-11-02T01:52:13Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T01:51:50Z",
+"started_at":"2026-11-02T01:51:53Z",
+"completed_at":"2026-11-02T02:19:23Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T01:51:50Z",
+"started_at":"2026-11-02T01:51:54Z",
+"completed_at":"2026-11-02T01:52:37Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T01:51:50Z",
+"started_at":"2026-11-02T01:51:53Z",
+"completed_at":"2026-11-02T01:53:37Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T01:51:50Z",
+"started_at":"2026-11-02T01:51:53Z",
+"completed_at":"2026-11-02T01:52:25Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T01:51:50Z",
+"started_at":"2026-11-02T01:51:53Z",
+"completed_at":"2026-11-02T02:29:58Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T01:51:50Z",
+"started_at":"2026-11-02T01:51:53Z",
+"completed_at":"2026-11-02T01:52:30Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T01:51:50Z",
+"started_at":"2026-11-02T01:52:08Z",
+"completed_at":"2026-11-02T01:55:57Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T01:51:50Z",
+"started_at":"2026-11-02T01:51:54Z",
+"completed_at":"2026-11-02T01:52:41Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T01:51:50Z",
+"started_at":"2026-11-02T01:52:14Z",
+"completed_at":"2026-11-02T01:56:07Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T01:51:50Z",
+"started_at":"2026-11-02T01:51:56Z",
+"completed_at":"2026-11-02T01:52:22Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T01:51:51Z",
+"started_at":"2026-11-02T01:51:54Z",
+"completed_at":"2026-11-02T01:53:24Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T01:51:51Z",
+"started_at":"2026-11-02T01:51:53Z",
+"completed_at":"2026-11-02T02:24:01Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T01:51:51Z",
+"started_at":"2026-11-02T01:52:08Z",
+"completed_at":"2026-11-02T01:52:35Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T01:51:51Z",
+"started_at":"2026-11-02T01:51:53Z",
+"completed_at":"2026-11-02T02:11:20Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T01:51:51Z",
+"started_at":"2026-11-02T01:51:53Z",
+"completed_at":"2026-11-02T01:55:44Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T01:51:51Z",
+"started_at":"2026-11-02T01:51:53Z",
+"completed_at":"2026-11-02T02:16:18Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T01:51:51Z",
+"started_at":"2026-11-02T01:51:53Z",
+"completed_at":"2026-11-02T02:23:42Z",
+"conclusion":"success"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T01:51:50Z",
+"started_at":"2026-11-02T01:51:53Z",
+"completed_at":"2026-11-02T01:52:29Z",
+"conclusion":"success"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T01:51:51Z",
+"started_at":"2026-11-02T01:51:51Z",
+"completed_at":"2026-11-02T01:51:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T01:51:51Z",
+"started_at":"2026-11-02T01:51:51Z",
+"completed_at":"2026-11-02T01:51:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T01:51:51Z",
+"started_at":"2026-11-02T01:51:51Z",
+"completed_at":"2026-11-02T01:51:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T01:51:51Z",
+"started_at":"2026-11-02T01:51:51Z",
+"completed_at":"2026-11-02T01:51:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T01:51:51Z",
+"started_at":"2026-11-02T01:51:51Z",
+"completed_at":"2026-11-02T01:51:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T01:51:51Z",
+"started_at":"2026-11-02T01:51:51Z",
+"completed_at":"2026-11-02T01:51:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T01:51:51Z",
+"started_at":"2026-11-02T01:51:51Z",
+"completed_at":"2026-11-02T01:51:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T01:51:51Z",
+"started_at":"2026-11-02T01:51:51Z",
+"completed_at":"2026-11-02T01:51:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T01:52:37Z",
+"started_at":"2026-11-02T01:52:37Z",
+"completed_at":"2026-11-02T01:52:37Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T01:52:37Z",
+"started_at":"2026-11-02T01:52:37Z",
+"completed_at":"2026-11-02T01:52:37Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T02:11:20Z",
+"started_at":"2026-11-02T02:13:23Z",
+"completed_at":"2026-11-02T02:13:35Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T02:11:21Z",
+"started_at":"2026-11-02T02:11:21Z",
+"completed_at":"2026-11-02T02:11:20Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T02:16:18Z",
+"started_at":"2026-11-02T02:16:18Z",
+"completed_at":"2026-11-02T02:16:18Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T02:23:42Z",
+"started_at":"2026-11-02T02:24:04Z",
+"completed_at":"2026-11-02T02:25:13Z",
+"conclusion":"success"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T02:23:43Z",
+"started_at":"2026-11-02T02:23:43Z",
+"completed_at":"2026-11-02T02:23:42Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T02:24:02Z",
+"started_at":"2026-11-02T02:24:02Z",
+"completed_at":"2026-11-02T02:24:01Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T02:29:58Z",
+"started_at":"2026-11-02T02:34:09Z",
+"completed_at":"2026-11-02T02:34:37Z",
+"conclusion":"success"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T02:29:59Z",
+"started_at":"2026-11-02T02:29:59Z",
+"completed_at":"2026-11-02T02:29:58Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41378499375,
+"run_number":3817,
+"head_sha":"8247a1ed10f66baaa173d30be1696907c6bbae32",
+"created_at":"2026-11-02T02:34:59Z",
+"status":"completed",
+"conclusion":"success",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T02:35:00Z",
+"started_at":"2026-11-02T02:38:27Z",
+"completed_at":"2026-11-02T02:38:54Z",
+"conclusion":"success"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T02:35:00Z",
+"started_at":"2026-11-02T02:35:00Z",
+"completed_at":"2026-11-02T02:35:00Z",
+"conclusion":"skipped"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T02:35:00Z",
+"started_at":"2026-11-02T02:35:00Z",
+"completed_at":"2026-11-02T02:35:00Z",
+"conclusion":"skipped"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T02:38:54Z",
+"started_at":"2026-11-02T02:39:53Z",
+"completed_at":"2026-11-02T02:41:07Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T02:38:54Z",
+"started_at":"2026-11-02T02:41:48Z",
+"completed_at":"2026-11-02T03:22:30Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T02:38:54Z",
+"started_at":"2026-11-02T02:40:14Z",
+"completed_at":"2026-11-02T02:41:00Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T02:38:54Z",
+"started_at":"2026-11-02T02:41:58Z",
+"completed_at":"2026-11-02T02:42:29Z",
+"conclusion":"success"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T02:38:54Z",
+"started_at":"2026-11-02T02:41:37Z",
+"completed_at":"2026-11-02T02:41:56Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T02:38:54Z",
+"started_at":"2026-11-02T02:44:00Z",
+"completed_at":"2026-11-02T02:44:45Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T02:38:54Z",
+"started_at":"2026-11-02T02:44:30Z",
+"completed_at":"2026-11-02T02:45:38Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T02:38:54Z",
+"started_at":"2026-11-02T02:43:56Z",
+"completed_at":"2026-11-02T03:11:07Z",
+"conclusion":"success"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T02:38:54Z",
+"started_at":"2026-11-02T02:42:18Z",
+"completed_at":"2026-11-02T02:42:54Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T02:38:54Z",
+"started_at":"2026-11-02T02:42:27Z",
+"completed_at":"2026-11-02T02:43:23Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T02:38:54Z",
+"started_at":"2026-11-02T02:44:35Z",
+"completed_at":"2026-11-02T02:49:47Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T02:38:54Z",
+"started_at":"2026-11-02T02:43:26Z",
+"completed_at":"2026-11-02T02:43:53Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T02:38:54Z",
+"started_at":"2026-11-02T02:41:27Z",
+"completed_at":"2026-11-02T02:41:56Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T02:38:54Z",
+"started_at":"2026-11-02T02:41:11Z",
+"completed_at":"2026-11-02T03:01:05Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T02:38:54Z",
+"started_at":"2026-11-02T02:41:58Z",
+"completed_at":"2026-11-02T03:13:21Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T02:38:54Z",
+"started_at":"2026-11-02T02:44:47Z",
+"completed_at":"2026-11-02T03:16:32Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T02:38:54Z",
+"started_at":"2026-11-02T02:42:57Z",
+"completed_at":"2026-11-02T03:16:50Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T02:38:54Z",
+"started_at":"2026-11-02T02:45:51Z",
+"completed_at":"2026-11-02T02:47:19Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T02:38:54Z",
+"started_at":"2026-11-02T02:46:08Z",
+"completed_at":"2026-11-02T02:50:29Z",
+"conclusion":"success"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T02:38:54Z",
+"started_at":"2026-11-02T02:38:54Z",
+"completed_at":"2026-11-02T02:38:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T02:38:54Z",
+"started_at":"2026-11-02T02:38:54Z",
+"completed_at":"2026-11-02T02:38:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T02:38:54Z",
+"started_at":"2026-11-02T02:38:54Z",
+"completed_at":"2026-11-02T02:38:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T02:38:54Z",
+"started_at":"2026-11-02T02:38:54Z",
+"completed_at":"2026-11-02T02:38:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T02:38:55Z",
+"started_at":"2026-11-02T02:38:55Z",
+"completed_at":"2026-11-02T02:38:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T02:38:55Z",
+"started_at":"2026-11-02T02:38:55Z",
+"completed_at":"2026-11-02T02:38:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T02:38:55Z",
+"started_at":"2026-11-02T02:38:55Z",
+"completed_at":"2026-11-02T02:38:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T02:38:55Z",
+"started_at":"2026-11-02T02:38:55Z",
+"completed_at":"2026-11-02T02:38:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T02:42:29Z",
+"started_at":"2026-11-02T02:42:29Z",
+"completed_at":"2026-11-02T02:42:29Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T02:42:29Z",
+"started_at":"2026-11-02T02:42:29Z",
+"completed_at":"2026-11-02T02:42:29Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T03:01:06Z",
+"started_at":"2026-11-02T03:01:15Z",
+"completed_at":"2026-11-02T03:01:25Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T03:01:06Z",
+"started_at":"2026-11-02T03:01:06Z",
+"completed_at":"2026-11-02T03:01:06Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T03:16:33Z",
+"started_at":"2026-11-02T03:16:33Z",
+"completed_at":"2026-11-02T03:16:32Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T03:16:33Z",
+"started_at":"2026-11-02T03:16:33Z",
+"completed_at":"2026-11-02T03:16:32Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T03:16:50Z",
+"started_at":"2026-11-02T03:16:53Z",
+"completed_at":"2026-11-02T03:18:09Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T03:16:51Z",
+"started_at":"2026-11-02T03:16:51Z",
+"completed_at":"2026-11-02T03:16:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T03:22:30Z",
+"started_at":"2026-11-02T03:22:33Z",
+"completed_at":"2026-11-02T03:22:57Z",
+"conclusion":"success"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T03:22:31Z",
+"started_at":"2026-11-02T03:22:31Z",
+"completed_at":"2026-11-02T03:22:30Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41384505496,
+"run_number":3833,
+"head_sha":"48216600f5d51ef665c3787c0e81e8396fd33c74",
+"created_at":"2026-11-02T03:42:02Z",
+"status":"completed",
+"conclusion":"success",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T03:42:03Z",
+"started_at":"2026-11-02T03:42:05Z",
+"completed_at":"2026-11-02T03:42:30Z",
+"conclusion":"success"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T03:42:03Z",
+"started_at":"2026-11-02T03:42:03Z",
+"completed_at":"2026-11-02T03:42:03Z",
+"conclusion":"skipped"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T03:42:03Z",
+"started_at":"2026-11-02T03:42:03Z",
+"completed_at":"2026-11-02T03:42:03Z",
+"conclusion":"skipped"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T03:42:30Z",
+"started_at":"2026-11-02T03:42:33Z",
+"completed_at":"2026-11-02T03:42:55Z",
+"conclusion":"success"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T03:42:30Z",
+"started_at":"2026-11-02T03:42:33Z",
+"completed_at":"2026-11-02T03:43:06Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T03:42:30Z",
+"started_at":"2026-11-02T03:42:33Z",
+"completed_at":"2026-11-02T03:43:20Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T03:42:30Z",
+"started_at":"2026-11-02T03:42:33Z",
+"completed_at":"2026-11-02T03:46:53Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T03:42:30Z",
+"started_at":"2026-11-02T03:42:34Z",
+"completed_at":"2026-11-02T03:43:04Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T03:42:30Z",
+"started_at":"2026-11-02T03:42:33Z",
+"completed_at":"2026-11-02T03:44:06Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T03:42:30Z",
+"started_at":"2026-11-02T03:42:34Z",
+"completed_at":"2026-11-02T03:43:22Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T03:42:30Z",
+"started_at":"2026-11-02T03:42:33Z",
+"completed_at":"2026-11-02T04:09:28Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T03:42:30Z",
+"started_at":"2026-11-02T03:42:33Z",
+"completed_at":"2026-11-02T04:07:34Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T03:42:30Z",
+"started_at":"2026-11-02T03:42:33Z",
+"completed_at":"2026-11-02T03:43:28Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T03:42:30Z",
+"started_at":"2026-11-02T03:42:34Z",
+"completed_at":"2026-11-02T03:43:23Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T03:42:30Z",
+"started_at":"2026-11-02T03:42:34Z",
+"completed_at":"2026-11-02T03:42:55Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T03:42:30Z",
+"started_at":"2026-11-02T03:42:33Z",
+"completed_at":"2026-11-02T03:42:59Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T03:42:30Z",
+"started_at":"2026-11-02T03:42:34Z",
+"completed_at":"2026-11-02T03:46:53Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T03:42:30Z",
+"started_at":"2026-11-02T03:42:34Z",
+"completed_at":"2026-11-02T04:01:42Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T03:42:30Z",
+"started_at":"2026-11-02T03:42:34Z",
+"completed_at":"2026-11-02T04:07:21Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T03:42:30Z",
+"started_at":"2026-11-02T03:42:34Z",
+"completed_at":"2026-11-02T04:00:47Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T03:42:30Z",
+"started_at":"2026-11-02T03:42:34Z",
+"completed_at":"2026-11-02T04:12:04Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T03:42:31Z",
+"started_at":"2026-11-02T03:42:34Z",
+"completed_at":"2026-11-02T03:44:11Z",
+"conclusion":"success"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T03:42:31Z",
+"started_at":"2026-11-02T03:42:31Z",
+"completed_at":"2026-11-02T03:42:30Z",
+"conclusion":"skipped"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T03:42:31Z",
+"started_at":"2026-11-02T03:42:31Z",
+"completed_at":"2026-11-02T03:42:30Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T03:42:31Z",
+"started_at":"2026-11-02T03:42:31Z",
+"completed_at":"2026-11-02T03:42:30Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T03:42:31Z",
+"started_at":"2026-11-02T03:42:31Z",
+"completed_at":"2026-11-02T03:42:30Z",
+"conclusion":"skipped"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T03:42:31Z",
+"started_at":"2026-11-02T03:42:31Z",
+"completed_at":"2026-11-02T03:42:30Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T03:42:31Z",
+"started_at":"2026-11-02T03:42:31Z",
+"completed_at":"2026-11-02T03:42:30Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T03:42:31Z",
+"started_at":"2026-11-02T03:42:31Z",
+"completed_at":"2026-11-02T03:42:30Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T03:42:31Z",
+"started_at":"2026-11-02T03:42:31Z",
+"completed_at":"2026-11-02T03:42:30Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T03:43:20Z",
+"started_at":"2026-11-02T03:43:20Z",
+"completed_at":"2026-11-02T03:43:20Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T03:43:21Z",
+"started_at":"2026-11-02T03:43:21Z",
+"completed_at":"2026-11-02T03:43:20Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T04:00:48Z",
+"started_at":"2026-11-02T04:00:48Z",
+"completed_at":"2026-11-02T04:00:47Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T04:01:42Z",
+"started_at":"2026-11-02T04:01:45Z",
+"completed_at":"2026-11-02T04:01:53Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T04:01:43Z",
+"started_at":"2026-11-02T04:01:43Z",
+"completed_at":"2026-11-02T04:01:42Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T04:07:22Z",
+"started_at":"2026-11-02T04:07:24Z",
+"completed_at":"2026-11-02T04:08:51Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T04:07:22Z",
+"started_at":"2026-11-02T04:07:22Z",
+"completed_at":"2026-11-02T04:07:22Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T04:12:04Z",
+"started_at":"2026-11-02T04:12:07Z",
+"completed_at":"2026-11-02T04:12:35Z",
+"conclusion":"success"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T04:12:04Z",
+"started_at":"2026-11-02T04:12:04Z",
+"completed_at":"2026-11-02T04:12:04Z",
+"conclusion":"skipped"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T04:12:04Z",
+"started_at":"2026-11-02T04:12:04Z",
+"completed_at":"2026-11-02T04:12:04Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41384617176,
+"run_number":3838,
+"head_sha":"3dd3697228dfac221f90915c6060bb8ad794e99f",
+"created_at":"2026-11-02T03:43:22Z",
+"status":"completed",
+"conclusion":"success",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T03:43:23Z",
+"started_at":"2026-11-02T03:43:25Z",
+"completed_at":"2026-11-02T03:43:50Z",
+"conclusion":"success"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T03:43:23Z",
+"started_at":"2026-11-02T03:43:23Z",
+"completed_at":"2026-11-02T03:43:23Z",
+"conclusion":"skipped"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T03:43:32Z",
+"started_at":"2026-11-02T03:43:32Z",
+"completed_at":"2026-11-02T03:43:23Z",
+"conclusion":"skipped"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T03:43:50Z",
+"started_at":"2026-11-02T03:44:07Z",
+"completed_at":"2026-11-02T04:24:16Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T03:43:50Z",
+"started_at":"2026-11-02T03:43:56Z",
+"completed_at":"2026-11-02T03:45:18Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T03:43:50Z",
+"started_at":"2026-11-02T03:44:07Z",
+"completed_at":"2026-11-02T04:06:48Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T03:43:50Z",
+"started_at":"2026-11-02T03:44:01Z",
+"completed_at":"2026-11-02T03:44:45Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T03:43:50Z",
+"started_at":"2026-11-02T03:44:09Z",
+"completed_at":"2026-11-02T03:44:56Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T03:43:50Z",
+"started_at":"2026-11-02T03:44:01Z",
+"completed_at":"2026-11-02T03:44:41Z",
+"conclusion":"success"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T03:43:50Z",
+"started_at":"2026-11-02T03:44:47Z",
+"completed_at":"2026-11-02T03:45:07Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T03:43:50Z",
+"started_at":"2026-11-02T03:44:13Z",
+"completed_at":"2026-11-02T03:44:55Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T03:43:50Z",
+"started_at":"2026-11-02T03:44:09Z",
+"completed_at":"2026-11-02T03:48:09Z",
+"conclusion":"success"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T03:43:50Z",
+"started_at":"2026-11-02T03:44:19Z",
+"completed_at":"2026-11-02T03:44:54Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T03:43:50Z",
+"started_at":"2026-11-02T03:44:58Z",
+"completed_at":"2026-11-02T03:45:39Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T03:43:50Z",
+"started_at":"2026-11-02T03:44:32Z",
+"completed_at":"2026-11-02T03:45:08Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T03:43:50Z",
+"started_at":"2026-11-02T03:44:32Z",
+"completed_at":"2026-11-02T03:44:56Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T03:43:50Z",
+"started_at":"2026-11-02T03:44:28Z",
+"completed_at":"2026-11-02T03:48:26Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T03:43:50Z",
+"started_at":"2026-11-02T03:44:14Z",
+"completed_at":"2026-11-02T04:22:50Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T03:43:50Z",
+"started_at":"2026-11-02T03:44:57Z",
+"completed_at":"2026-11-02T03:46:22Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T03:43:50Z",
+"started_at":"2026-11-02T03:44:37Z",
+"completed_at":"2026-11-02T04:11:03Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T03:43:50Z",
+"started_at":"2026-11-02T03:44:36Z",
+"completed_at":"2026-11-02T04:16:21Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T03:43:50Z",
+"started_at":"2026-11-02T03:44:59Z",
+"completed_at":"2026-11-02T04:15:02Z",
+"conclusion":"success"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T03:43:50Z",
+"started_at":"2026-11-02T03:43:50Z",
+"completed_at":"2026-11-02T03:43:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T03:43:51Z",
+"started_at":"2026-11-02T03:43:51Z",
+"completed_at":"2026-11-02T03:43:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T03:43:51Z",
+"started_at":"2026-11-02T03:43:51Z",
+"completed_at":"2026-11-02T03:43:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T03:43:51Z",
+"started_at":"2026-11-02T03:43:51Z",
+"completed_at":"2026-11-02T03:43:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T03:43:51Z",
+"started_at":"2026-11-02T03:43:51Z",
+"completed_at":"2026-11-02T03:43:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T03:43:51Z",
+"started_at":"2026-11-02T03:43:51Z",
+"completed_at":"2026-11-02T03:43:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T03:43:51Z",
+"started_at":"2026-11-02T03:43:51Z",
+"completed_at":"2026-11-02T03:43:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T03:43:51Z",
+"started_at":"2026-11-02T03:43:51Z",
+"completed_at":"2026-11-02T03:43:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T03:44:42Z",
+"started_at":"2026-11-02T03:44:42Z",
+"completed_at":"2026-11-02T03:44:42Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T03:44:42Z",
+"started_at":"2026-11-02T03:44:42Z",
+"completed_at":"2026-11-02T03:44:42Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T04:11:04Z",
+"started_at":"2026-11-02T04:11:07Z",
+"completed_at":"2026-11-02T04:11:18Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T04:11:04Z",
+"started_at":"2026-11-02T04:11:04Z",
+"completed_at":"2026-11-02T04:11:04Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T04:15:02Z",
+"started_at":"2026-11-02T04:15:02Z",
+"completed_at":"2026-11-02T04:15:02Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T04:16:22Z",
+"started_at":"2026-11-02T04:16:22Z",
+"completed_at":"2026-11-02T04:16:22Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T04:22:51Z",
+"started_at":"2026-11-02T04:22:53Z",
+"completed_at":"2026-11-02T04:24:08Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T04:22:51Z",
+"started_at":"2026-11-02T04:22:51Z",
+"completed_at":"2026-11-02T04:22:51Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T04:24:17Z",
+"started_at":"2026-11-02T04:24:20Z",
+"completed_at":"2026-11-02T04:24:47Z",
+"conclusion":"success"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T04:24:17Z",
+"started_at":"2026-11-02T04:24:17Z",
+"completed_at":"2026-11-02T04:24:17Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41389212994,
+"run_number":3849,
+"head_sha":"432e25c60bea0532cb68ab09dc8b499826185541",
+"created_at":"2026-11-02T04:34:19Z",
+"status":"completed",
+"conclusion":"cancelled",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T04:34:20Z",
+"started_at":"2026-11-02T04:34:23Z",
+"completed_at":"2026-11-02T04:34:41Z",
+"conclusion":"success"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T04:34:20Z",
+"started_at":"2026-11-02T04:34:20Z",
+"completed_at":"2026-11-02T04:34:20Z",
+"conclusion":"skipped"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T04:34:20Z",
+"started_at":"2026-11-02T04:34:20Z",
+"completed_at":"2026-11-02T04:34:20Z",
+"conclusion":"skipped"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:44Z",
+"completed_at":"2026-11-02T04:36:25Z",
+"conclusion":"success"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:44Z",
+"completed_at":"2026-11-02T04:35:08Z",
+"conclusion":"success"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:44Z",
+"completed_at":"2026-11-02T04:35:21Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:44Z",
+"completed_at":"2026-11-02T04:35:29Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:44Z",
+"completed_at":"2026-11-02T04:35:12Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:44Z",
+"completed_at":"2026-11-02T04:35:36Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:44Z",
+"completed_at":"2026-11-02T04:35:27Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:44Z",
+"completed_at":"2026-11-02T05:05:01Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:45Z",
+"completed_at":"2026-11-02T05:02:43Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:45Z",
+"completed_at":"2026-11-02T04:41:26Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:44Z",
+"completed_at":"2026-11-02T04:35:16Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:44Z",
+"completed_at":"2026-11-02T04:35:15Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:44Z",
+"completed_at":"2026-11-02T04:35:14Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:45Z",
+"completed_at":"2026-11-02T04:38:44Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:44Z",
+"completed_at":"2026-11-02T04:35:39Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:44Z",
+"completed_at":"2026-11-02T04:58:32Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:44Z",
+"completed_at":"2026-11-02T05:05:51Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:44Z",
+"completed_at":"2026-11-02T04:47:06Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:45Z",
+"completed_at":"2026-11-02T05:13:09Z",
+"conclusion":"cancelled"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:41Z",
+"completed_at":"2026-11-02T04:34:41Z",
+"conclusion":"skipped"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:41Z",
+"completed_at":"2026-11-02T04:34:41Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:41Z",
+"completed_at":"2026-11-02T04:34:41Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:41Z",
+"completed_at":"2026-11-02T04:34:41Z",
+"conclusion":"skipped"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:41Z",
+"completed_at":"2026-11-02T04:34:41Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:41Z",
+"completed_at":"2026-11-02T04:34:41Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T04:34:41Z",
+"started_at":"2026-11-02T04:34:41Z",
+"completed_at":"2026-11-02T04:34:41Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T04:34:42Z",
+"started_at":"2026-11-02T04:34:42Z",
+"completed_at":"2026-11-02T04:34:41Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T04:35:12Z",
+"started_at":"2026-11-02T04:35:12Z",
+"completed_at":"2026-11-02T04:35:12Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T04:35:12Z",
+"started_at":"2026-11-02T04:35:12Z",
+"completed_at":"2026-11-02T04:35:12Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T04:47:06Z",
+"started_at":"2026-11-02T04:47:50Z",
+"completed_at":"2026-11-02T04:47:58Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T04:47:06Z",
+"started_at":"2026-11-02T04:47:06Z",
+"completed_at":"2026-11-02T04:47:06Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T04:58:33Z",
+"started_at":"2026-11-02T04:58:33Z",
+"completed_at":"2026-11-02T04:58:33Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T05:05:52Z",
+"started_at":"2026-11-02T05:05:52Z",
+"completed_at":"2026-11-02T05:05:51Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T05:13:10Z",
+"started_at":"2026-11-02T05:13:10Z",
+"completed_at":"2026-11-02T05:13:09Z",
+"conclusion":"cancelled"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T05:13:10Z",
+"started_at":"2026-11-02T05:13:10Z",
+"completed_at":"2026-11-02T05:13:09Z",
+"conclusion":"cancelled"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T05:13:10Z",
+"started_at":"2026-11-02T05:13:10Z",
+"completed_at":"2026-11-02T05:13:10Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T05:13:10Z",
+"started_at":"2026-11-02T05:13:10Z",
+"completed_at":"2026-11-02T05:13:10Z",
+"conclusion":"cancelled"
+}
+]
+},
+{
+"id":41389318801,
+"run_number":3850,
+"head_sha":"35b711976ffd9d7222d87e78addc8e945b20a1cf",
+"created_at":"2026-11-02T04:35:26Z",
+"status":"completed",
+"conclusion":"cancelled",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T04:35:27Z",
+"started_at":"2026-11-02T04:35:29Z",
+"completed_at":"2026-11-02T04:35:54Z",
+"conclusion":"success"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T04:35:27Z",
+"started_at":"2026-11-02T04:35:27Z",
+"completed_at":"2026-11-02T04:35:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T04:35:27Z",
+"started_at":"2026-11-02T04:35:27Z",
+"completed_at":"2026-11-02T04:35:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T04:35:54Z",
+"started_at":"2026-11-02T04:35:57Z",
+"completed_at":"2026-11-02T04:36:30Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T04:35:54Z",
+"started_at":"2026-11-02T04:35:57Z",
+"completed_at":"2026-11-02T04:37:42Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T04:35:54Z",
+"started_at":"2026-11-02T04:35:57Z",
+"completed_at":"2026-11-02T04:37:04Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T04:35:54Z",
+"started_at":"2026-11-02T04:35:57Z",
+"completed_at":"2026-11-02T04:42:49Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T04:35:54Z",
+"started_at":"2026-11-02T04:35:57Z",
+"completed_at":"2026-11-02T04:59:14Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T04:35:54Z",
+"started_at":"2026-11-02T04:35:57Z",
+"completed_at":"2026-11-02T04:36:31Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T04:35:54Z",
+"started_at":"2026-11-02T04:35:57Z",
+"completed_at":"2026-11-02T05:12:58Z",
+"conclusion":"cancelled"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T04:35:54Z",
+"started_at":"2026-11-02T04:35:58Z",
+"completed_at":"2026-11-02T04:36:18Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T04:35:54Z",
+"started_at":"2026-11-02T04:35:58Z",
+"completed_at":"2026-11-02T04:36:57Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T04:35:54Z",
+"started_at":"2026-11-02T04:35:57Z",
+"completed_at":"2026-11-02T04:36:41Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T04:35:54Z",
+"started_at":"2026-11-02T04:35:58Z",
+"completed_at":"2026-11-02T04:36:45Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T04:35:54Z",
+"started_at":"2026-11-02T04:35:58Z",
+"completed_at":"2026-11-02T04:36:26Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T04:35:54Z",
+"started_at":"2026-11-02T04:35:57Z",
+"completed_at":"2026-11-02T04:36:33Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T04:35:54Z",
+"started_at":"2026-11-02T04:35:57Z",
+"completed_at":"2026-11-02T04:53:23Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T04:35:54Z",
+"started_at":"2026-11-02T04:35:58Z",
+"completed_at":"2026-11-02T04:40:12Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T04:35:54Z",
+"started_at":"2026-11-02T04:35:57Z",
+"completed_at":"2026-11-02T05:07:50Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T04:35:54Z",
+"started_at":"2026-11-02T04:35:57Z",
+"completed_at":"2026-11-02T05:08:27Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T04:35:54Z",
+"started_at":"2026-11-02T04:35:57Z",
+"completed_at":"2026-11-02T04:37:20Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T04:35:54Z",
+"started_at":"2026-11-02T04:35:57Z",
+"completed_at":"2026-11-02T05:05:17Z",
+"conclusion":"success"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T04:35:54Z",
+"started_at":"2026-11-02T04:35:54Z",
+"completed_at":"2026-11-02T04:35:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T04:35:55Z",
+"started_at":"2026-11-02T04:35:55Z",
+"completed_at":"2026-11-02T04:35:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T04:35:55Z",
+"started_at":"2026-11-02T04:35:55Z",
+"completed_at":"2026-11-02T04:35:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T04:35:55Z",
+"started_at":"2026-11-02T04:35:55Z",
+"completed_at":"2026-11-02T04:35:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T04:35:55Z",
+"started_at":"2026-11-02T04:35:55Z",
+"completed_at":"2026-11-02T04:35:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T04:35:55Z",
+"started_at":"2026-11-02T04:35:55Z",
+"completed_at":"2026-11-02T04:35:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T04:35:55Z",
+"started_at":"2026-11-02T04:35:55Z",
+"completed_at":"2026-11-02T04:35:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T04:35:55Z",
+"started_at":"2026-11-02T04:35:55Z",
+"completed_at":"2026-11-02T04:35:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T04:36:32Z",
+"started_at":"2026-11-02T04:36:32Z",
+"completed_at":"2026-11-02T04:36:31Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T04:36:32Z",
+"started_at":"2026-11-02T04:36:32Z",
+"completed_at":"2026-11-02T04:36:31Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T04:53:24Z",
+"started_at":"2026-11-02T05:02:02Z",
+"completed_at":"2026-11-02T05:02:11Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T04:53:24Z",
+"started_at":"2026-11-02T04:53:24Z",
+"completed_at":"2026-11-02T04:53:24Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T05:05:18Z",
+"started_at":"2026-11-02T05:05:18Z",
+"completed_at":"2026-11-02T05:05:17Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T05:08:28Z",
+"started_at":"2026-11-02T05:08:30Z",
+"completed_at":"2026-11-02T05:09:31Z",
+"conclusion":"success"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T05:08:28Z",
+"started_at":"2026-11-02T05:08:28Z",
+"completed_at":"2026-11-02T05:08:28Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T05:08:28Z",
+"started_at":"2026-11-02T05:08:28Z",
+"completed_at":"2026-11-02T05:08:28Z",
+"conclusion":"skipped"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T05:12:58Z",
+"started_at":"2026-11-02T05:12:58Z",
+"completed_at":"2026-11-02T05:12:58Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T05:12:59Z",
+"started_at":"2026-11-02T05:12:59Z",
+"completed_at":"2026-11-02T05:12:58Z",
+"conclusion":"cancelled"
+}
+]
+},
+{
+"id":41389536586,
+"run_number":3858,
+"head_sha":"158c3e0e5527d598ff1adf9b4bcd9e2a102d11cd",
+"created_at":"2026-11-02T04:37:50Z",
+"status":"completed",
+"conclusion":"cancelled",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T04:37:50Z",
+"started_at":"2026-11-02T04:38:49Z",
+"completed_at":"2026-11-02T04:39:16Z",
+"conclusion":"success"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T04:37:51Z",
+"started_at":"2026-11-02T04:37:51Z",
+"completed_at":"2026-11-02T04:37:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T04:37:59Z",
+"started_at":"2026-11-02T04:37:59Z",
+"completed_at":"2026-11-02T04:37:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T04:39:16Z",
+"started_at":"2026-11-02T04:42:52Z",
+"completed_at":"2026-11-02T04:43:26Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T04:39:16Z",
+"started_at":"2026-11-02T04:40:32Z",
+"completed_at":"2026-11-02T04:41:18Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T04:39:16Z",
+"started_at":"2026-11-02T04:39:53Z",
+"completed_at":"2026-11-02T04:41:34Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T04:39:16Z",
+"started_at":"2026-11-02T04:41:03Z",
+"completed_at":"2026-11-02T04:41:46Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T04:39:16Z",
+"started_at":"2026-11-02T04:41:40Z",
+"completed_at":"2026-11-02T05:10:08Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T04:39:16Z",
+"started_at":"2026-11-02T04:39:41Z",
+"completed_at":"2026-11-02T04:40:22Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T04:39:16Z",
+"started_at":"2026-11-02T04:42:28Z",
+"completed_at":"2026-11-02T04:43:19Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T04:39:16Z",
+"started_at":"2026-11-02T04:40:24Z",
+"completed_at":"2026-11-02T04:46:25Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T04:39:16Z",
+"started_at":"2026-11-02T04:40:25Z",
+"completed_at":"2026-11-02T04:41:19Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T04:39:16Z",
+"started_at":"2026-11-02T04:45:50Z",
+"completed_at":"2026-11-02T05:12:27Z",
+"conclusion":"success"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T04:39:16Z",
+"started_at":"2026-11-02T04:39:20Z",
+"completed_at":"2026-11-02T04:39:39Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T04:39:16Z",
+"started_at":"2026-11-02T04:43:12Z",
+"completed_at":"2026-11-02T04:43:41Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T04:39:16Z",
+"started_at":"2026-11-02T04:45:28Z",
+"completed_at":"2026-11-02T04:45:57Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T04:39:17Z",
+"started_at":"2026-11-02T04:41:30Z",
+"completed_at":"2026-11-02T04:45:44Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T04:39:17Z",
+"started_at":"2026-11-02T04:41:48Z",
+"completed_at":"2026-11-02T05:12:44Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T04:39:17Z",
+"started_at":"2026-11-02T04:43:53Z",
+"completed_at":"2026-11-02T05:01:59Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T04:39:17Z",
+"started_at":"2026-11-02T04:43:43Z",
+"completed_at":"2026-11-02T04:44:38Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T04:39:17Z",
+"started_at":"2026-11-02T04:43:18Z",
+"completed_at":"2026-11-02T05:07:48Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T04:39:17Z",
+"started_at":"2026-11-02T04:44:42Z",
+"completed_at":"2026-11-02T05:13:11Z",
+"conclusion":"cancelled"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T04:39:17Z",
+"started_at":"2026-11-02T04:39:17Z",
+"completed_at":"2026-11-02T04:39:16Z",
+"conclusion":"skipped"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T04:39:17Z",
+"started_at":"2026-11-02T04:39:17Z",
+"completed_at":"2026-11-02T04:39:16Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T04:39:17Z",
+"started_at":"2026-11-02T04:39:17Z",
+"completed_at":"2026-11-02T04:39:16Z",
+"conclusion":"skipped"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T04:39:17Z",
+"started_at":"2026-11-02T04:39:17Z",
+"completed_at":"2026-11-02T04:39:16Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T04:39:17Z",
+"started_at":"2026-11-02T04:39:17Z",
+"completed_at":"2026-11-02T04:39:16Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T04:39:17Z",
+"started_at":"2026-11-02T04:39:17Z",
+"completed_at":"2026-11-02T04:39:16Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T04:39:17Z",
+"started_at":"2026-11-02T04:39:17Z",
+"completed_at":"2026-11-02T04:39:17Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T04:39:17Z",
+"started_at":"2026-11-02T04:39:17Z",
+"completed_at":"2026-11-02T04:39:17Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T04:41:46Z",
+"started_at":"2026-11-02T04:41:46Z",
+"completed_at":"2026-11-02T04:41:46Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T04:41:46Z",
+"started_at":"2026-11-02T04:41:46Z",
+"completed_at":"2026-11-02T04:41:46Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T05:07:49Z",
+"started_at":"2026-11-02T05:07:49Z",
+"completed_at":"2026-11-02T05:07:49Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T05:12:45Z",
+"started_at":"2026-11-02T05:12:48Z",
+"completed_at":"2026-11-02T05:12:57Z",
+"conclusion":"cancelled"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T05:12:45Z",
+"started_at":"2026-11-02T05:12:45Z",
+"completed_at":"2026-11-02T05:12:45Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T05:12:45Z",
+"started_at":"2026-11-02T05:12:45Z",
+"completed_at":"2026-11-02T05:12:45Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T05:13:12Z",
+"started_at":"2026-11-02T05:13:12Z",
+"completed_at":"2026-11-02T05:13:11Z",
+"conclusion":"cancelled"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T05:13:12Z",
+"started_at":"2026-11-02T05:13:12Z",
+"completed_at":"2026-11-02T05:13:11Z",
+"conclusion":"cancelled"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T05:13:12Z",
+"started_at":"2026-11-02T05:13:12Z",
+"completed_at":"2026-11-02T05:13:12Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T05:13:12Z",
+"started_at":"2026-11-02T05:13:12Z",
+"completed_at":"2026-11-02T05:13:12Z",
+"conclusion":"cancelled"
+}
+]
+},
+{
+"id":41390010494,
+"run_number":3859,
+"head_sha":"ea6ae27736631e9987fe20a9b4f86ad5e8b79acb",
+"created_at":"2026-11-02T04:43:10Z",
+"status":"completed",
+"conclusion":"success",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T04:43:11Z",
+"started_at":"2026-11-02T04:47:47Z",
+"completed_at":"2026-11-02T04:48:22Z",
+"conclusion":"success"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T04:43:11Z",
+"started_at":"2026-11-02T04:43:11Z",
+"completed_at":"2026-11-02T04:43:11Z",
+"conclusion":"skipped"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T04:43:11Z",
+"started_at":"2026-11-02T04:43:11Z",
+"completed_at":"2026-11-02T04:43:11Z",
+"conclusion":"skipped"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:54:15Z",
+"completed_at":"2026-11-02T04:55:41Z",
+"conclusion":"success"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:52:00Z",
+"completed_at":"2026-11-02T04:52:23Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:57:44Z",
+"completed_at":"2026-11-02T04:58:24Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:55:44Z",
+"completed_at":"2026-11-02T05:35:26Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:51:14Z",
+"completed_at":"2026-11-02T05:13:31Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:53:26Z",
+"completed_at":"2026-11-02T04:54:12Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:58:58Z",
+"completed_at":"2026-11-02T04:59:50Z",
+"conclusion":"success"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:48:38Z",
+"completed_at":"2026-11-02T04:49:15Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:58:13Z",
+"completed_at":"2026-11-02T04:58:56Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:59:10Z",
+"completed_at":"2026-11-02T05:00:16Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:58:27Z",
+"completed_at":"2026-11-02T04:58:55Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:58:35Z",
+"completed_at":"2026-11-02T05:04:42Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:59:16Z",
+"completed_at":"2026-11-02T04:59:46Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:59:52Z",
+"completed_at":"2026-11-02T05:29:02Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T05:01:48Z",
+"completed_at":"2026-11-02T05:26:00Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:58:59Z",
+"completed_at":"2026-11-02T05:20:06Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T05:00:19Z",
+"completed_at":"2026-11-02T05:01:29Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T05:01:32Z",
+"completed_at":"2026-11-02T05:19:15Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:59:48Z",
+"completed_at":"2026-11-02T05:03:51Z",
+"conclusion":"success"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:48:23Z",
+"completed_at":"2026-11-02T04:48:23Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:48:23Z",
+"completed_at":"2026-11-02T04:48:23Z",
+"conclusion":"skipped"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:48:23Z",
+"completed_at":"2026-11-02T04:48:23Z",
+"conclusion":"skipped"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:48:23Z",
+"completed_at":"2026-11-02T04:48:23Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:48:23Z",
+"completed_at":"2026-11-02T04:48:23Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:48:23Z",
+"completed_at":"2026-11-02T04:48:23Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:48:23Z",
+"completed_at":"2026-11-02T04:48:23Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T04:48:23Z",
+"started_at":"2026-11-02T04:48:23Z",
+"completed_at":"2026-11-02T04:48:23Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T04:58:25Z",
+"started_at":"2026-11-02T04:58:25Z",
+"completed_at":"2026-11-02T04:58:25Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T04:58:25Z",
+"started_at":"2026-11-02T04:58:25Z",
+"completed_at":"2026-11-02T04:58:25Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T05:20:07Z",
+"started_at":"2026-11-02T05:20:07Z",
+"completed_at":"2026-11-02T05:20:06Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T05:26:00Z",
+"started_at":"2026-11-02T05:26:03Z",
+"completed_at":"2026-11-02T05:26:13Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T05:26:01Z",
+"started_at":"2026-11-02T05:26:01Z",
+"completed_at":"2026-11-02T05:26:00Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T05:29:03Z",
+"started_at":"2026-11-02T05:30:30Z",
+"completed_at":"2026-11-02T05:31:38Z",
+"conclusion":"success"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T05:29:03Z",
+"started_at":"2026-11-02T05:29:03Z",
+"completed_at":"2026-11-02T05:29:02Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T05:29:03Z",
+"started_at":"2026-11-02T05:29:03Z",
+"completed_at":"2026-11-02T05:29:02Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T05:35:26Z",
+"started_at":"2026-11-02T05:35:29Z",
+"completed_at":"2026-11-02T05:35:58Z",
+"conclusion":"success"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T05:35:26Z",
+"started_at":"2026-11-02T05:35:26Z",
+"completed_at":"2026-11-02T05:35:26Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41393728768,
+"run_number":3860,
+"head_sha":"8cdb5dd5b93ef6732b90664b6b9a8b9382ea124e",
+"created_at":"2026-11-02T05:23:18Z",
+"status":"completed",
+"conclusion":"success",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T05:23:19Z",
+"started_at":"2026-11-02T05:23:22Z",
+"completed_at":"2026-11-02T05:23:45Z",
+"conclusion":"success"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T05:23:19Z",
+"started_at":"2026-11-02T05:23:19Z",
+"completed_at":"2026-11-02T05:23:19Z",
+"conclusion":"skipped"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T05:23:25Z",
+"started_at":"2026-11-02T05:23:25Z",
+"completed_at":"2026-11-02T05:23:19Z",
+"conclusion":"skipped"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T05:23:45Z",
+"started_at":"2026-11-02T05:23:48Z",
+"completed_at":"2026-11-02T05:24:23Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T05:23:45Z",
+"started_at":"2026-11-02T05:23:49Z",
+"completed_at":"2026-11-02T05:55:24Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T05:23:45Z",
+"started_at":"2026-11-02T05:23:48Z",
+"completed_at":"2026-11-02T05:24:38Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T05:23:45Z",
+"started_at":"2026-11-02T05:23:49Z",
+"completed_at":"2026-11-02T05:25:31Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T05:23:45Z",
+"started_at":"2026-11-02T05:23:48Z",
+"completed_at":"2026-11-02T05:24:32Z",
+"conclusion":"success"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T05:23:45Z",
+"started_at":"2026-11-02T05:23:49Z",
+"completed_at":"2026-11-02T05:24:09Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T05:23:45Z",
+"started_at":"2026-11-02T05:23:48Z",
+"completed_at":"2026-11-02T05:24:29Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T05:23:45Z",
+"started_at":"2026-11-02T05:23:48Z",
+"completed_at":"2026-11-02T05:27:51Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T05:23:45Z",
+"started_at":"2026-11-02T05:23:49Z",
+"completed_at":"2026-11-02T05:51:03Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T05:23:45Z",
+"started_at":"2026-11-02T05:23:48Z",
+"completed_at":"2026-11-02T05:24:28Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T05:23:45Z",
+"started_at":"2026-11-02T05:23:48Z",
+"completed_at":"2026-11-02T05:24:29Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T05:23:45Z",
+"started_at":"2026-11-02T05:23:49Z",
+"completed_at":"2026-11-02T05:24:18Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T05:23:45Z",
+"started_at":"2026-11-02T05:23:48Z",
+"completed_at":"2026-11-02T05:24:21Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T05:23:45Z",
+"started_at":"2026-11-02T05:23:48Z",
+"completed_at":"2026-11-02T05:41:57Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T05:23:45Z",
+"started_at":"2026-11-02T05:23:49Z",
+"completed_at":"2026-11-02T05:25:13Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T05:23:45Z",
+"started_at":"2026-11-02T05:23:48Z",
+"completed_at":"2026-11-02T05:44:26Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T05:23:46Z",
+"started_at":"2026-11-02T05:23:49Z",
+"completed_at":"2026-11-02T05:27:49Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T05:23:46Z",
+"started_at":"2026-11-02T05:23:49Z",
+"completed_at":"2026-11-02T05:55:54Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T05:23:46Z",
+"started_at":"2026-11-02T05:23:49Z",
+"completed_at":"2026-11-02T05:48:34Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T05:23:46Z",
+"started_at":"2026-11-02T05:23:46Z",
+"completed_at":"2026-11-02T05:23:45Z",
+"conclusion":"skipped"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T05:23:46Z",
+"started_at":"2026-11-02T05:23:46Z",
+"completed_at":"2026-11-02T05:23:45Z",
+"conclusion":"skipped"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T05:23:46Z",
+"started_at":"2026-11-02T05:23:46Z",
+"completed_at":"2026-11-02T05:23:45Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T05:23:46Z",
+"started_at":"2026-11-02T05:23:46Z",
+"completed_at":"2026-11-02T05:23:45Z",
+"conclusion":"skipped"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T05:23:46Z",
+"started_at":"2026-11-02T05:23:46Z",
+"completed_at":"2026-11-02T05:23:45Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T05:23:46Z",
+"started_at":"2026-11-02T05:23:46Z",
+"completed_at":"2026-11-02T05:23:45Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T05:23:46Z",
+"started_at":"2026-11-02T05:23:46Z",
+"completed_at":"2026-11-02T05:23:45Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T05:23:46Z",
+"started_at":"2026-11-02T05:23:46Z",
+"completed_at":"2026-11-02T05:23:45Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T05:24:29Z",
+"started_at":"2026-11-02T05:24:29Z",
+"completed_at":"2026-11-02T05:24:28Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T05:24:29Z",
+"started_at":"2026-11-02T05:24:29Z",
+"completed_at":"2026-11-02T05:24:29Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T05:44:26Z",
+"started_at":"2026-11-02T05:44:26Z",
+"completed_at":"2026-11-02T05:44:26Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T05:48:34Z",
+"started_at":"2026-11-02T05:48:34Z",
+"completed_at":"2026-11-02T05:48:34Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T05:55:54Z",
+"started_at":"2026-11-02T05:55:57Z",
+"completed_at":"2026-11-02T05:57:05Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T05:55:54Z",
+"started_at":"2026-11-02T05:55:57Z",
+"completed_at":"2026-11-02T05:56:08Z",
+"conclusion":"success"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T05:55:55Z",
+"started_at":"2026-11-02T05:55:55Z",
+"completed_at":"2026-11-02T05:55:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T05:55:55Z",
+"started_at":"2026-11-02T05:55:55Z",
+"completed_at":"2026-11-02T05:55:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T05:57:05Z",
+"started_at":"2026-11-02T05:57:08Z",
+"completed_at":"2026-11-02T05:57:37Z",
+"conclusion":"success"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T05:57:05Z",
+"started_at":"2026-11-02T05:57:05Z",
+"completed_at":"2026-11-02T05:57:05Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41393840932,
+"run_number":3865,
+"head_sha":"907d29f0e5295c5e7f3fa5bbcf5477d56ff9563d",
+"created_at":"2026-11-02T05:24:26Z",
+"status":"completed",
+"conclusion":"success",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T05:24:27Z",
+"started_at":"2026-11-02T05:24:30Z",
+"completed_at":"2026-11-02T05:24:49Z",
+"conclusion":"success"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T05:24:27Z",
+"started_at":"2026-11-02T05:24:27Z",
+"completed_at":"2026-11-02T05:24:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T05:24:37Z",
+"started_at":"2026-11-02T05:24:37Z",
+"completed_at":"2026-11-02T05:24:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T05:24:49Z",
+"started_at":"2026-11-02T05:24:53Z",
+"completed_at":"2026-11-02T05:25:13Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T05:24:49Z",
+"started_at":"2026-11-02T05:25:09Z",
+"completed_at":"2026-11-02T05:26:35Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T05:24:49Z",
+"started_at":"2026-11-02T05:25:15Z",
+"completed_at":"2026-11-02T06:08:03Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T05:24:49Z",
+"started_at":"2026-11-02T05:25:05Z",
+"completed_at":"2026-11-02T05:25:59Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T05:24:49Z",
+"started_at":"2026-11-02T05:24:52Z",
+"completed_at":"2026-11-02T05:25:32Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T05:24:49Z",
+"started_at":"2026-11-02T05:24:52Z",
+"completed_at":"2026-11-02T05:25:38Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T05:24:49Z",
+"started_at":"2026-11-02T05:24:52Z",
+"completed_at":"2026-11-02T05:25:31Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T05:24:49Z",
+"started_at":"2026-11-02T05:24:52Z",
+"completed_at":"2026-11-02T05:25:36Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T05:24:49Z",
+"started_at":"2026-11-02T05:24:52Z",
+"completed_at":"2026-11-02T05:31:35Z",
+"conclusion":"success"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T05:24:49Z",
+"started_at":"2026-11-02T05:24:52Z",
+"completed_at":"2026-11-02T05:25:31Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T05:24:49Z",
+"started_at":"2026-11-02T05:24:59Z",
+"completed_at":"2026-11-02T05:51:47Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T05:24:50Z",
+"started_at":"2026-11-02T05:24:59Z",
+"completed_at":"2026-11-02T05:25:27Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T05:24:50Z",
+"started_at":"2026-11-02T05:24:59Z",
+"completed_at":"2026-11-02T05:25:27Z",
+"conclusion":"success"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T05:24:50Z",
+"started_at":"2026-11-02T05:24:50Z",
+"completed_at":"2026-11-02T05:24:49Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T05:24:50Z",
+"started_at":"2026-11-02T05:24:59Z",
+"completed_at":"2026-11-02T05:48:28Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T05:24:50Z",
+"started_at":"2026-11-02T05:25:11Z",
+"completed_at":"2026-11-02T05:29:12Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T05:24:50Z",
+"started_at":"2026-11-02T05:25:15Z",
+"completed_at":"2026-11-02T05:43:32Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T05:24:50Z",
+"started_at":"2026-11-02T05:25:18Z",
+"completed_at":"2026-11-02T05:26:32Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T05:24:50Z",
+"started_at":"2026-11-02T05:24:50Z",
+"completed_at":"2026-11-02T05:24:49Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T05:24:50Z",
+"started_at":"2026-11-02T05:25:23Z",
+"completed_at":"2026-11-02T05:45:20Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T05:24:50Z",
+"started_at":"2026-11-02T05:25:19Z",
+"completed_at":"2026-11-02T06:03:02Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T05:24:50Z",
+"started_at":"2026-11-02T05:24:50Z",
+"completed_at":"2026-11-02T05:24:49Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T05:24:50Z",
+"started_at":"2026-11-02T05:24:50Z",
+"completed_at":"2026-11-02T05:24:49Z",
+"conclusion":"skipped"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T05:24:50Z",
+"started_at":"2026-11-02T05:24:50Z",
+"completed_at":"2026-11-02T05:24:49Z",
+"conclusion":"skipped"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T05:24:50Z",
+"started_at":"2026-11-02T05:24:50Z",
+"completed_at":"2026-11-02T05:24:49Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T05:24:50Z",
+"started_at":"2026-11-02T05:24:50Z",
+"completed_at":"2026-11-02T05:24:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T05:24:50Z",
+"started_at":"2026-11-02T05:24:50Z",
+"completed_at":"2026-11-02T05:24:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T05:25:32Z",
+"started_at":"2026-11-02T05:25:32Z",
+"completed_at":"2026-11-02T05:25:32Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T05:25:33Z",
+"started_at":"2026-11-02T05:25:33Z",
+"completed_at":"2026-11-02T05:25:32Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T05:45:21Z",
+"started_at":"2026-11-02T05:45:21Z",
+"completed_at":"2026-11-02T05:45:21Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T05:48:28Z",
+"started_at":"2026-11-02T05:48:30Z",
+"completed_at":"2026-11-02T05:48:38Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T05:48:28Z",
+"started_at":"2026-11-02T05:48:28Z",
+"completed_at":"2026-11-02T05:48:28Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T05:48:28Z",
+"started_at":"2026-11-02T05:48:28Z",
+"completed_at":"2026-11-02T05:48:28Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T06:03:02Z",
+"started_at":"2026-11-02T06:03:05Z",
+"completed_at":"2026-11-02T06:04:07Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T06:03:02Z",
+"started_at":"2026-11-02T06:03:02Z",
+"completed_at":"2026-11-02T06:03:02Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T06:08:04Z",
+"started_at":"2026-11-02T06:08:06Z",
+"completed_at":"2026-11-02T06:08:29Z",
+"conclusion":"success"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T06:08:04Z",
+"started_at":"2026-11-02T06:08:04Z",
+"completed_at":"2026-11-02T06:08:04Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41394108723,
+"run_number":3867,
+"head_sha":"5e9c392946d4d55296c2c5a138e13eb8b8fe4dd3",
+"created_at":"2026-11-02T05:27:12Z",
+"status":"completed",
+"conclusion":"success",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T05:27:12Z",
+"started_at":"2026-11-02T05:27:15Z",
+"completed_at":"2026-11-02T05:27:42Z",
+"conclusion":"success"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T05:27:13Z",
+"started_at":"2026-11-02T05:27:13Z",
+"completed_at":"2026-11-02T05:27:12Z",
+"conclusion":"skipped"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T05:27:13Z",
+"started_at":"2026-11-02T05:27:13Z",
+"completed_at":"2026-11-02T05:27:12Z",
+"conclusion":"skipped"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:27:45Z",
+"completed_at":"2026-11-02T05:28:17Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:27:45Z",
+"completed_at":"2026-11-02T05:28:23Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:27:46Z",
+"completed_at":"2026-11-02T05:34:29Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:27:46Z",
+"completed_at":"2026-11-02T05:28:15Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:27:46Z",
+"completed_at":"2026-11-02T05:31:24Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:27:45Z",
+"completed_at":"2026-11-02T05:52:55Z",
+"conclusion":"success"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:27:51Z",
+"completed_at":"2026-11-02T05:28:12Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:27:46Z",
+"completed_at":"2026-11-02T05:28:28Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:27:45Z",
+"completed_at":"2026-11-02T05:29:24Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:27:45Z",
+"completed_at":"2026-11-02T05:28:30Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:27:46Z",
+"completed_at":"2026-11-02T06:06:58Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:27:46Z",
+"completed_at":"2026-11-02T05:28:15Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:27:53Z",
+"completed_at":"2026-11-02T05:28:24Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:27:46Z",
+"completed_at":"2026-11-02T06:06:10Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:28:03Z",
+"completed_at":"2026-11-02T05:29:12Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:28:13Z",
+"completed_at":"2026-11-02T05:31:56Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:28:07Z",
+"completed_at":"2026-11-02T06:00:06Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:28:14Z",
+"completed_at":"2026-11-02T05:58:32Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:28:17Z",
+"completed_at":"2026-11-02T05:47:32Z",
+"conclusion":"success"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:27:43Z",
+"completed_at":"2026-11-02T05:27:43Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:27:43Z",
+"completed_at":"2026-11-02T05:27:43Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:27:43Z",
+"completed_at":"2026-11-02T05:27:43Z",
+"conclusion":"skipped"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:27:43Z",
+"completed_at":"2026-11-02T05:27:43Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:27:43Z",
+"completed_at":"2026-11-02T05:27:43Z",
+"conclusion":"skipped"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:27:43Z",
+"completed_at":"2026-11-02T05:27:43Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:27:43Z",
+"completed_at":"2026-11-02T05:27:43Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T05:27:43Z",
+"started_at":"2026-11-02T05:27:43Z",
+"completed_at":"2026-11-02T05:27:43Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T05:28:28Z",
+"started_at":"2026-11-02T05:28:28Z",
+"completed_at":"2026-11-02T05:28:28Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T05:28:29Z",
+"started_at":"2026-11-02T05:28:29Z",
+"completed_at":"2026-11-02T05:28:28Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T05:47:32Z",
+"started_at":"2026-11-02T05:47:32Z",
+"completed_at":"2026-11-02T05:47:32Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T05:58:32Z",
+"started_at":"2026-11-02T05:58:35Z",
+"completed_at":"2026-11-02T05:58:43Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T05:58:32Z",
+"started_at":"2026-11-02T05:58:32Z",
+"completed_at":"2026-11-02T05:58:32Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T06:00:07Z",
+"started_at":"2026-11-02T06:00:07Z",
+"completed_at":"2026-11-02T06:00:07Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T06:06:11Z",
+"started_at":"2026-11-02T06:06:14Z",
+"completed_at":"2026-11-02T06:07:26Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T06:06:11Z",
+"started_at":"2026-11-02T06:06:11Z",
+"completed_at":"2026-11-02T06:06:11Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T06:07:26Z",
+"started_at":"2026-11-02T06:07:29Z",
+"completed_at":"2026-11-02T06:07:56Z",
+"conclusion":"success"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T06:07:26Z",
+"started_at":"2026-11-02T06:07:26Z",
+"completed_at":"2026-11-02T06:07:26Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41394217043,
+"run_number":3868,
+"head_sha":"c7aa121650058ec9f1540b5bf60ffd69eea75298",
+"created_at":"2026-11-02T05:28:21Z",
+"status":"completed",
+"conclusion":"success",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T05:28:22Z",
+"started_at":"2026-11-02T05:28:24Z",
+"completed_at":"2026-11-02T05:28:51Z",
+"conclusion":"success"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T05:28:22Z",
+"started_at":"2026-11-02T05:28:22Z",
+"completed_at":"2026-11-02T05:28:22Z",
+"conclusion":"skipped"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T05:28:22Z",
+"started_at":"2026-11-02T05:28:22Z",
+"completed_at":"2026-11-02T05:28:22Z",
+"conclusion":"skipped"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T05:28:51Z",
+"started_at":"2026-11-02T05:28:54Z",
+"completed_at":"2026-11-02T06:08:51Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T05:28:51Z",
+"started_at":"2026-11-02T05:29:15Z",
+"completed_at":"2026-11-02T05:29:53Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T05:28:51Z",
+"started_at":"2026-11-02T05:28:54Z",
+"completed_at":"2026-11-02T05:30:35Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T05:28:51Z",
+"started_at":"2026-11-02T05:29:04Z",
+"completed_at":"2026-11-02T05:55:48Z",
+"conclusion":"success"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T05:28:51Z",
+"started_at":"2026-11-02T05:28:54Z",
+"completed_at":"2026-11-02T05:29:15Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T05:28:51Z",
+"started_at":"2026-11-02T05:28:54Z",
+"completed_at":"2026-11-02T05:29:41Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T05:28:51Z",
+"started_at":"2026-11-02T05:29:18Z",
+"completed_at":"2026-11-02T05:32:19Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T05:28:51Z",
+"started_at":"2026-11-02T05:29:05Z",
+"completed_at":"2026-11-02T05:29:58Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T05:28:51Z",
+"started_at":"2026-11-02T05:29:26Z",
+"completed_at":"2026-11-02T05:34:55Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T05:28:51Z",
+"started_at":"2026-11-02T05:29:00Z",
+"completed_at":"2026-11-02T05:29:41Z",
+"conclusion":"success"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T05:28:51Z",
+"started_at":"2026-11-02T05:29:14Z",
+"completed_at":"2026-11-02T05:29:51Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T05:28:51Z",
+"started_at":"2026-11-02T05:29:18Z",
+"completed_at":"2026-11-02T05:29:51Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T05:28:51Z",
+"started_at":"2026-11-02T05:29:53Z",
+"completed_at":"2026-11-02T05:30:21Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T05:28:51Z",
+"started_at":"2026-11-02T05:29:57Z",
+"completed_at":"2026-11-02T05:31:00Z",
+"conclusion":"success"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T05:28:51Z",
+"started_at":"2026-11-02T05:28:51Z",
+"completed_at":"2026-11-02T05:28:51Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T05:28:51Z",
+"started_at":"2026-11-02T05:29:44Z",
+"completed_at":"2026-11-02T05:34:00Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T05:28:51Z",
+"started_at":"2026-11-02T05:30:00Z",
+"completed_at":"2026-11-02T06:08:15Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T05:28:51Z",
+"started_at":"2026-11-02T05:29:44Z",
+"completed_at":"2026-11-02T05:51:48Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T05:28:51Z",
+"started_at":"2026-11-02T05:29:54Z",
+"completed_at":"2026-11-02T06:00:53Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T05:28:51Z",
+"started_at":"2026-11-02T05:30:18Z",
+"completed_at":"2026-11-02T05:48:02Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T05:28:51Z",
+"started_at":"2026-11-02T05:28:51Z",
+"completed_at":"2026-11-02T05:28:51Z",
+"conclusion":"skipped"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T05:28:51Z",
+"started_at":"2026-11-02T05:28:51Z",
+"completed_at":"2026-11-02T05:28:51Z",
+"conclusion":"skipped"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T05:28:51Z",
+"started_at":"2026-11-02T05:28:51Z",
+"completed_at":"2026-11-02T05:28:51Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T05:28:52Z",
+"started_at":"2026-11-02T05:28:52Z",
+"completed_at":"2026-11-02T05:28:51Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T05:28:52Z",
+"started_at":"2026-11-02T05:28:52Z",
+"completed_at":"2026-11-02T05:28:51Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T05:28:52Z",
+"started_at":"2026-11-02T05:28:52Z",
+"completed_at":"2026-11-02T05:28:51Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T05:28:52Z",
+"started_at":"2026-11-02T05:28:52Z",
+"completed_at":"2026-11-02T05:28:51Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T05:29:42Z",
+"started_at":"2026-11-02T05:29:42Z",
+"completed_at":"2026-11-02T05:29:41Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T05:29:42Z",
+"started_at":"2026-11-02T05:29:42Z",
+"completed_at":"2026-11-02T05:29:41Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T05:48:03Z",
+"started_at":"2026-11-02T05:48:03Z",
+"completed_at":"2026-11-02T05:48:02Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T05:51:49Z",
+"started_at":"2026-11-02T05:51:51Z",
+"completed_at":"2026-11-02T05:51:59Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T05:51:49Z",
+"started_at":"2026-11-02T05:51:49Z",
+"completed_at":"2026-11-02T05:51:49Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T06:00:54Z",
+"started_at":"2026-11-02T06:00:54Z",
+"completed_at":"2026-11-02T06:00:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T06:08:15Z",
+"started_at":"2026-11-02T06:08:18Z",
+"completed_at":"2026-11-02T06:09:36Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T06:08:15Z",
+"started_at":"2026-11-02T06:08:15Z",
+"completed_at":"2026-11-02T06:08:15Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T06:09:36Z",
+"started_at":"2026-11-02T06:09:39Z",
+"completed_at":"2026-11-02T06:09:58Z",
+"conclusion":"success"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T06:09:36Z",
+"started_at":"2026-11-02T06:09:36Z",
+"completed_at":"2026-11-02T06:09:36Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41397326281,
+"run_number":3870,
+"head_sha":"8f286293be2d03817a2de23a3a0c884ec2e94fab",
+"created_at":"2026-11-02T06:00:58Z",
+"status":"completed",
+"conclusion":"failure",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T06:00:59Z",
+"started_at":"2026-11-02T06:01:02Z",
+"completed_at":"2026-11-02T06:01:27Z",
+"conclusion":"success"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T06:00:59Z",
+"started_at":"2026-11-02T06:00:59Z",
+"completed_at":"2026-11-02T06:00:59Z",
+"conclusion":"skipped"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T06:00:59Z",
+"started_at":"2026-11-02T06:00:59Z",
+"completed_at":"2026-11-02T06:00:59Z",
+"conclusion":"skipped"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:30Z",
+"completed_at":"2026-11-02T06:01:51Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:30Z",
+"completed_at":"2026-11-02T06:06:45Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:30Z",
+"completed_at":"2026-11-02T06:02:10Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:30Z",
+"completed_at":"2026-11-02T06:02:09Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:30Z",
+"completed_at":"2026-11-02T06:02:19Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:30Z",
+"completed_at":"2026-11-02T06:03:12Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:30Z",
+"completed_at":"2026-11-02T06:42:32Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:30Z",
+"completed_at":"2026-11-02T06:28:31Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:29Z",
+"completed_at":"2026-11-02T06:02:20Z",
+"conclusion":"success"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:30Z",
+"completed_at":"2026-11-02T06:02:07Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:30Z",
+"completed_at":"2026-11-02T06:02:15Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:30Z",
+"completed_at":"2026-11-02T06:02:04Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:30Z",
+"completed_at":"2026-11-02T06:02:00Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:30Z",
+"completed_at":"2026-11-02T06:02:09Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:30Z",
+"completed_at":"2026-11-02T06:39:42Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:30Z",
+"completed_at":"2026-11-02T06:02:51Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:30Z",
+"completed_at":"2026-11-02T06:05:29Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:30Z",
+"completed_at":"2026-11-02T06:33:03Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:30Z",
+"completed_at":"2026-11-02T06:34:03Z",
+"conclusion":"success"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:27Z",
+"completed_at":"2026-11-02T06:01:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:27Z",
+"completed_at":"2026-11-02T06:01:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:27Z",
+"completed_at":"2026-11-02T06:01:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:27Z",
+"completed_at":"2026-11-02T06:01:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:27Z",
+"completed_at":"2026-11-02T06:01:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:27Z",
+"completed_at":"2026-11-02T06:01:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T06:01:27Z",
+"started_at":"2026-11-02T06:01:27Z",
+"completed_at":"2026-11-02T06:01:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T06:01:28Z",
+"started_at":"2026-11-02T06:01:28Z",
+"completed_at":"2026-11-02T06:01:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T06:02:09Z",
+"started_at":"2026-11-02T06:02:11Z",
+"completed_at":"2026-11-02T06:02:19Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T06:02:09Z",
+"started_at":"2026-11-02T06:02:09Z",
+"completed_at":"2026-11-02T06:02:09Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T06:02:10Z",
+"started_at":"2026-11-02T06:02:10Z",
+"completed_at":"2026-11-02T06:02:10Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T06:02:10Z",
+"started_at":"2026-11-02T06:02:10Z",
+"completed_at":"2026-11-02T06:02:10Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T06:34:03Z",
+"started_at":"2026-11-02T06:34:03Z",
+"completed_at":"2026-11-02T06:34:03Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T06:34:04Z",
+"started_at":"2026-11-02T06:34:04Z",
+"completed_at":"2026-11-02T06:34:03Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T06:39:42Z",
+"started_at":"2026-11-02T06:39:45Z",
+"completed_at":"2026-11-02T06:40:48Z",
+"conclusion":"failure"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T06:39:42Z",
+"started_at":"2026-11-02T06:39:42Z",
+"completed_at":"2026-11-02T06:39:42Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T06:42:33Z",
+"started_at":"2026-11-02T06:42:36Z",
+"completed_at":"2026-11-02T06:43:00Z",
+"conclusion":"failure"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T06:42:33Z",
+"started_at":"2026-11-02T06:42:33Z",
+"completed_at":"2026-11-02T06:42:32Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41408568169,
+"run_number":3896,
+"head_sha":"dfb4ce2b52fafb340e0320bc2efb870099a53884",
+"created_at":"2026-11-02T07:47:27Z",
+"status":"completed",
+"conclusion":"failure",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T07:47:28Z",
+"started_at":"2026-11-02T07:47:31Z",
+"completed_at":"2026-11-02T07:47:54Z",
+"conclusion":"success"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T07:47:29Z",
+"started_at":"2026-11-02T07:47:29Z",
+"completed_at":"2026-11-02T07:47:28Z",
+"conclusion":"skipped"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T07:47:29Z",
+"started_at":"2026-11-02T07:47:29Z",
+"completed_at":"2026-11-02T07:47:28Z",
+"conclusion":"skipped"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T07:47:54Z",
+"started_at":"2026-11-02T07:47:57Z",
+"completed_at":"2026-11-02T07:48:21Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T07:47:54Z",
+"started_at":"2026-11-02T07:47:57Z",
+"completed_at":"2026-11-02T07:48:37Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T07:47:54Z",
+"started_at":"2026-11-02T07:47:57Z",
+"completed_at":"2026-11-02T07:48:41Z",
+"conclusion":"success"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T07:47:54Z",
+"started_at":"2026-11-02T07:47:57Z",
+"completed_at":"2026-11-02T07:48:35Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T07:47:54Z",
+"started_at":"2026-11-02T07:47:57Z",
+"completed_at":"2026-11-02T08:27:21Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T07:47:54Z",
+"started_at":"2026-11-02T07:47:57Z",
+"completed_at":"2026-11-02T08:15:48Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T07:47:54Z",
+"started_at":"2026-11-02T07:47:57Z",
+"completed_at":"2026-11-02T07:49:30Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T07:47:54Z",
+"started_at":"2026-11-02T07:47:58Z",
+"completed_at":"2026-11-02T07:48:40Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T07:47:54Z",
+"started_at":"2026-11-02T07:47:57Z",
+"completed_at":"2026-11-02T07:48:51Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T07:47:54Z",
+"started_at":"2026-11-02T07:47:58Z",
+"completed_at":"2026-11-02T07:51:43Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T07:47:54Z",
+"started_at":"2026-11-02T07:47:58Z",
+"completed_at":"2026-11-02T07:54:41Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T07:47:54Z",
+"started_at":"2026-11-02T07:47:57Z",
+"completed_at":"2026-11-02T07:48:22Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T07:47:54Z",
+"started_at":"2026-11-02T07:47:57Z",
+"completed_at":"2026-11-02T07:48:27Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T07:47:54Z",
+"started_at":"2026-11-02T07:47:57Z",
+"completed_at":"2026-11-02T08:20:34Z",
+"conclusion":"success"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T07:47:54Z",
+"started_at":"2026-11-02T07:47:54Z",
+"completed_at":"2026-11-02T07:47:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T07:47:54Z",
+"started_at":"2026-11-02T07:47:58Z",
+"completed_at":"2026-11-02T08:19:12Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T07:47:54Z",
+"started_at":"2026-11-02T07:48:01Z",
+"completed_at":"2026-11-02T08:17:43Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T07:47:54Z",
+"started_at":"2026-11-02T07:47:58Z",
+"completed_at":"2026-11-02T08:27:12Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T07:47:54Z",
+"started_at":"2026-11-02T07:47:57Z",
+"completed_at":"2026-11-02T07:52:11Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T07:47:54Z",
+"started_at":"2026-11-02T07:47:58Z",
+"completed_at":"2026-11-02T07:49:28Z",
+"conclusion":"success"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T07:47:54Z",
+"started_at":"2026-11-02T07:47:54Z",
+"completed_at":"2026-11-02T07:47:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T07:47:54Z",
+"started_at":"2026-11-02T07:47:54Z",
+"completed_at":"2026-11-02T07:47:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T07:47:54Z",
+"started_at":"2026-11-02T07:47:54Z",
+"completed_at":"2026-11-02T07:47:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T07:47:55Z",
+"started_at":"2026-11-02T07:47:55Z",
+"completed_at":"2026-11-02T07:47:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T07:47:55Z",
+"started_at":"2026-11-02T07:47:55Z",
+"completed_at":"2026-11-02T07:47:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T07:47:55Z",
+"started_at":"2026-11-02T07:47:55Z",
+"completed_at":"2026-11-02T07:47:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T07:47:55Z",
+"started_at":"2026-11-02T07:47:55Z",
+"completed_at":"2026-11-02T07:47:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T07:48:38Z",
+"started_at":"2026-11-02T07:48:38Z",
+"completed_at":"2026-11-02T07:48:38Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T07:48:38Z",
+"started_at":"2026-11-02T07:48:38Z",
+"completed_at":"2026-11-02T07:48:38Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T08:19:12Z",
+"started_at":"2026-11-02T08:19:15Z",
+"completed_at":"2026-11-02T08:19:24Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T08:19:12Z",
+"started_at":"2026-11-02T08:19:12Z",
+"completed_at":"2026-11-02T08:19:12Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T08:20:35Z",
+"started_at":"2026-11-02T08:20:35Z",
+"completed_at":"2026-11-02T08:20:34Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T08:20:35Z",
+"started_at":"2026-11-02T08:20:35Z",
+"completed_at":"2026-11-02T08:20:34Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T08:27:12Z",
+"started_at":"2026-11-02T08:27:15Z",
+"completed_at":"2026-11-02T08:28:45Z",
+"conclusion":"failure"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T08:27:12Z",
+"started_at":"2026-11-02T08:27:12Z",
+"completed_at":"2026-11-02T08:27:12Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T08:28:46Z",
+"started_at":"2026-11-02T08:28:49Z",
+"completed_at":"2026-11-02T08:29:18Z",
+"conclusion":"failure"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T08:28:46Z",
+"started_at":"2026-11-02T08:28:46Z",
+"completed_at":"2026-11-02T08:28:46Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41413405880,
+"run_number":3912,
+"head_sha":"8fcaf47e1d6989b6c5f2a053aaa0f2b79c24067a",
+"created_at":"2026-11-02T08:29:08Z",
+"status":"completed",
+"conclusion":"failure",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T08:29:09Z",
+"started_at":"2026-11-02T08:29:12Z",
+"completed_at":"2026-11-02T08:29:39Z",
+"conclusion":"success"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T08:29:09Z",
+"started_at":"2026-11-02T08:29:09Z",
+"completed_at":"2026-11-02T08:29:09Z",
+"conclusion":"skipped"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T08:29:09Z",
+"started_at":"2026-11-02T08:29:09Z",
+"completed_at":"2026-11-02T08:29:09Z",
+"conclusion":"skipped"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:42Z",
+"completed_at":"2026-11-02T08:30:18Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:51Z",
+"completed_at":"2026-11-02T08:33:53Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:43Z",
+"completed_at":"2026-11-02T08:30:29Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:43Z",
+"completed_at":"2026-11-02T08:30:15Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:48Z",
+"completed_at":"2026-11-02T08:30:36Z",
+"conclusion":"success"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:42Z",
+"completed_at":"2026-11-02T08:30:02Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:42Z",
+"completed_at":"2026-11-02T09:13:16Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:42Z",
+"completed_at":"2026-11-02T08:30:34Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:43Z",
+"completed_at":"2026-11-02T08:57:11Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:43Z",
+"completed_at":"2026-11-02T08:31:18Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:43Z",
+"completed_at":"2026-11-02T08:33:34Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:43Z",
+"completed_at":"2026-11-02T08:30:24Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:43Z",
+"completed_at":"2026-11-02T08:30:12Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:44Z",
+"completed_at":"2026-11-02T08:41:14Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:43Z",
+"completed_at":"2026-11-02T08:54:59Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:43Z",
+"completed_at":"2026-11-02T09:09:44Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:43Z",
+"completed_at":"2026-11-02T08:31:07Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:43Z",
+"completed_at":"2026-11-02T08:58:42Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:43Z",
+"completed_at":"2026-11-02T08:33:30Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:40Z",
+"completed_at":"2026-11-02T08:29:40Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:40Z",
+"completed_at":"2026-11-02T08:29:40Z",
+"conclusion":"skipped"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:40Z",
+"completed_at":"2026-11-02T08:29:40Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:40Z",
+"completed_at":"2026-11-02T08:29:40Z",
+"conclusion":"skipped"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:40Z",
+"completed_at":"2026-11-02T08:29:40Z",
+"conclusion":"skipped"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:40Z",
+"completed_at":"2026-11-02T08:29:40Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:40Z",
+"completed_at":"2026-11-02T08:29:40Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T08:29:40Z",
+"started_at":"2026-11-02T08:29:40Z",
+"completed_at":"2026-11-02T08:29:40Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T08:30:15Z",
+"started_at":"2026-11-02T08:30:15Z",
+"completed_at":"2026-11-02T08:30:15Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T08:30:15Z",
+"started_at":"2026-11-02T08:30:15Z",
+"completed_at":"2026-11-02T08:30:15Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T08:41:15Z",
+"started_at":"2026-11-02T08:41:17Z",
+"completed_at":"2026-11-02T08:41:26Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T08:41:15Z",
+"started_at":"2026-11-02T08:41:15Z",
+"completed_at":"2026-11-02T08:41:14Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T08:54:59Z",
+"started_at":"2026-11-02T08:54:59Z",
+"completed_at":"2026-11-02T08:54:59Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T08:58:43Z",
+"started_at":"2026-11-02T08:58:43Z",
+"completed_at":"2026-11-02T08:58:42Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T09:09:44Z",
+"started_at":"2026-11-02T09:10:05Z",
+"completed_at":"2026-11-02T09:11:28Z",
+"conclusion":"failure"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T09:09:44Z",
+"started_at":"2026-11-02T09:09:44Z",
+"completed_at":"2026-11-02T09:09:44Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T09:13:16Z",
+"started_at":"2026-11-02T09:13:19Z",
+"completed_at":"2026-11-02T09:13:44Z",
+"conclusion":"failure"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T09:13:17Z",
+"started_at":"2026-11-02T09:13:17Z",
+"completed_at":"2026-11-02T09:13:16Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41421154794,
+"run_number":3922,
+"head_sha":"279cb497fa764f89a961d94c87e57f16176c2fcc",
+"created_at":"2026-11-02T09:30:03Z",
+"status":"completed",
+"conclusion":"failure",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T09:30:04Z",
+"started_at":"2026-11-02T09:30:16Z",
+"completed_at":"2026-11-02T09:30:35Z",
+"conclusion":"success"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T09:30:04Z",
+"started_at":"2026-11-02T09:30:04Z",
+"completed_at":"2026-11-02T09:30:03Z",
+"conclusion":"skipped"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T09:30:04Z",
+"started_at":"2026-11-02T09:30:04Z",
+"completed_at":"2026-11-02T09:30:03Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:37Z",
+"completed_at":"2026-11-02T09:31:26Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:38Z",
+"completed_at":"2026-11-02T09:35:58Z",
+"conclusion":"success"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:38Z",
+"completed_at":"2026-11-02T09:31:16Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:38Z",
+"completed_at":"2026-11-02T09:31:33Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:37Z",
+"completed_at":"2026-11-02T09:31:45Z",
+"conclusion":"success"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:38Z",
+"completed_at":"2026-11-02T09:30:56Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:38Z",
+"completed_at":"2026-11-02T09:34:22Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:45Z",
+"completed_at":"2026-11-02T09:31:25Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:38Z",
+"completed_at":"2026-11-02T09:57:49Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:47Z",
+"completed_at":"2026-11-02T09:31:19Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:38Z",
+"completed_at":"2026-11-02T10:10:08Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:38Z",
+"completed_at":"2026-11-02T09:31:18Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:38Z",
+"completed_at":"2026-11-02T09:31:08Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:38Z",
+"completed_at":"2026-11-02T09:34:37Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:38Z",
+"completed_at":"2026-11-02T09:51:35Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:38Z",
+"completed_at":"2026-11-02T10:01:48Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:37Z",
+"completed_at":"2026-11-02T09:32:00Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:38Z",
+"completed_at":"2026-11-02T09:45:39Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:48Z",
+"completed_at":"2026-11-02T09:55:41Z",
+"conclusion":"success"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:35Z",
+"completed_at":"2026-11-02T09:30:35Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:35Z",
+"completed_at":"2026-11-02T09:30:35Z",
+"conclusion":"skipped"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:35Z",
+"completed_at":"2026-11-02T09:30:35Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:35Z",
+"completed_at":"2026-11-02T09:30:35Z",
+"conclusion":"skipped"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:35Z",
+"completed_at":"2026-11-02T09:30:35Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:35Z",
+"completed_at":"2026-11-02T09:30:35Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:35Z",
+"completed_at":"2026-11-02T09:30:35Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T09:30:35Z",
+"started_at":"2026-11-02T09:30:35Z",
+"completed_at":"2026-11-02T09:30:35Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T09:31:25Z",
+"started_at":"2026-11-02T09:31:25Z",
+"completed_at":"2026-11-02T09:31:25Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T09:31:26Z",
+"started_at":"2026-11-02T09:31:26Z",
+"completed_at":"2026-11-02T09:31:25Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T09:45:39Z",
+"started_at":"2026-11-02T09:45:42Z",
+"completed_at":"2026-11-02T09:45:52Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T09:45:39Z",
+"started_at":"2026-11-02T09:45:39Z",
+"completed_at":"2026-11-02T09:45:39Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T09:51:36Z",
+"started_at":"2026-11-02T09:51:36Z",
+"completed_at":"2026-11-02T09:51:35Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T09:55:41Z",
+"started_at":"2026-11-02T09:55:44Z",
+"completed_at":"2026-11-02T09:56:54Z",
+"conclusion":"failure"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T09:55:42Z",
+"started_at":"2026-11-02T09:55:42Z",
+"completed_at":"2026-11-02T09:55:41Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T10:01:49Z",
+"started_at":"2026-11-02T10:01:49Z",
+"completed_at":"2026-11-02T10:01:49Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T10:10:09Z",
+"started_at":"2026-11-02T10:10:12Z",
+"completed_at":"2026-11-02T10:10:44Z",
+"conclusion":"failure"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T10:10:09Z",
+"started_at":"2026-11-02T10:10:09Z",
+"completed_at":"2026-11-02T10:10:09Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41433471201,
+"run_number":3937,
+"head_sha":"3905069f38a60559186fef916b0241e311cc81cd",
+"created_at":"2026-11-02T11:01:48Z",
+"status":"completed",
+"conclusion":"failure",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T11:01:49Z",
+"started_at":"2026-11-02T11:02:02Z",
+"completed_at":"2026-11-02T11:02:37Z",
+"conclusion":"success"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T11:01:49Z",
+"started_at":"2026-11-02T11:01:49Z",
+"completed_at":"2026-11-02T11:01:49Z",
+"conclusion":"skipped"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T11:01:49Z",
+"started_at":"2026-11-02T11:01:49Z",
+"completed_at":"2026-11-02T11:01:49Z",
+"conclusion":"skipped"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:40Z",
+"completed_at":"2026-11-02T11:03:03Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:40Z",
+"completed_at":"2026-11-02T11:03:36Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:40Z",
+"completed_at":"2026-11-02T11:03:29Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:40Z",
+"completed_at":"2026-11-02T11:29:40Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:41Z",
+"completed_at":"2026-11-02T11:06:27Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:40Z",
+"completed_at":"2026-11-02T11:07:00Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:50Z",
+"completed_at":"2026-11-02T11:45:26Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:40Z",
+"completed_at":"2026-11-02T11:03:21Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:47Z",
+"completed_at":"2026-11-02T11:04:17Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:40Z",
+"completed_at":"2026-11-02T11:03:19Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:40Z",
+"completed_at":"2026-11-02T11:03:26Z",
+"conclusion":"success"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:41Z",
+"completed_at":"2026-11-02T11:03:20Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:40Z",
+"completed_at":"2026-11-02T11:03:08Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:50Z",
+"completed_at":"2026-11-02T11:34:14Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:50Z",
+"completed_at":"2026-11-02T11:14:54Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:41Z",
+"completed_at":"2026-11-02T11:04:08Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:41Z",
+"completed_at":"2026-11-02T11:35:24Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:40Z",
+"completed_at":"2026-11-02T11:41:43Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:40Z",
+"completed_at":"2026-11-02T11:06:54Z",
+"conclusion":"success"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:37Z",
+"completed_at":"2026-11-02T11:02:37Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:37Z",
+"completed_at":"2026-11-02T11:02:37Z",
+"conclusion":"skipped"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:37Z",
+"completed_at":"2026-11-02T11:02:37Z",
+"conclusion":"skipped"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:37Z",
+"completed_at":"2026-11-02T11:02:37Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:37Z",
+"completed_at":"2026-11-02T11:02:37Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:37Z",
+"completed_at":"2026-11-02T11:02:37Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:37Z",
+"completed_at":"2026-11-02T11:02:37Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T11:02:37Z",
+"started_at":"2026-11-02T11:02:37Z",
+"completed_at":"2026-11-02T11:02:37Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T11:03:21Z",
+"started_at":"2026-11-02T11:03:21Z",
+"completed_at":"2026-11-02T11:03:21Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T11:03:22Z",
+"started_at":"2026-11-02T11:03:22Z",
+"completed_at":"2026-11-02T11:03:21Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T11:14:55Z",
+"started_at":"2026-11-02T11:14:57Z",
+"completed_at":"2026-11-02T11:15:05Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T11:14:55Z",
+"started_at":"2026-11-02T11:14:55Z",
+"completed_at":"2026-11-02T11:14:54Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T11:35:24Z",
+"started_at":"2026-11-02T11:35:24Z",
+"completed_at":"2026-11-02T11:35:24Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T11:35:24Z",
+"started_at":"2026-11-02T11:35:24Z",
+"completed_at":"2026-11-02T11:35:24Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T11:41:43Z",
+"started_at":"2026-11-02T11:41:46Z",
+"completed_at":"2026-11-02T11:43:09Z",
+"conclusion":"failure"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T11:41:43Z",
+"started_at":"2026-11-02T11:41:43Z",
+"completed_at":"2026-11-02T11:41:43Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T11:45:26Z",
+"started_at":"2026-11-02T11:45:29Z",
+"completed_at":"2026-11-02T11:45:58Z",
+"conclusion":"failure"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T11:45:26Z",
+"started_at":"2026-11-02T11:45:26Z",
+"completed_at":"2026-11-02T11:45:26Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41450035669,
+"run_number":3963,
+"head_sha":"a9c149289922e92bae57cad87afc4abd3ef6c235",
+"created_at":"2026-11-02T13:05:55Z",
+"status":"completed",
+"conclusion":"failure",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T13:05:56Z",
+"started_at":"2026-11-02T13:05:59Z",
+"completed_at":"2026-11-02T13:06:27Z",
+"conclusion":"success"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T13:05:56Z",
+"started_at":"2026-11-02T13:05:56Z",
+"completed_at":"2026-11-02T13:05:56Z",
+"conclusion":"skipped"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T13:05:56Z",
+"started_at":"2026-11-02T13:05:56Z",
+"completed_at":"2026-11-02T13:05:56Z",
+"conclusion":"skipped"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T13:06:27Z",
+"started_at":"2026-11-02T13:06:30Z",
+"completed_at":"2026-11-02T13:08:09Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T13:06:27Z",
+"started_at":"2026-11-02T13:06:40Z",
+"completed_at":"2026-11-02T13:33:49Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T13:06:27Z",
+"started_at":"2026-11-02T13:06:31Z",
+"completed_at":"2026-11-02T13:07:17Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T13:06:27Z",
+"started_at":"2026-11-02T13:06:38Z",
+"completed_at":"2026-11-02T13:37:09Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T13:06:27Z",
+"started_at":"2026-11-02T13:06:31Z",
+"completed_at":"2026-11-02T13:07:15Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T13:06:27Z",
+"started_at":"2026-11-02T13:06:30Z",
+"completed_at":"2026-11-02T13:07:01Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T13:06:27Z",
+"started_at":"2026-11-02T13:06:31Z",
+"completed_at":"2026-11-02T13:10:19Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T13:06:27Z",
+"started_at":"2026-11-02T13:06:31Z",
+"completed_at":"2026-11-02T13:10:59Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T13:06:27Z",
+"started_at":"2026-11-02T13:06:32Z",
+"completed_at":"2026-11-02T13:07:20Z",
+"conclusion":"success"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T13:06:27Z",
+"started_at":"2026-11-02T13:06:31Z",
+"completed_at":"2026-11-02T13:06:49Z",
+"conclusion":"success"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T13:06:27Z",
+"started_at":"2026-11-02T13:06:31Z",
+"completed_at":"2026-11-02T13:07:25Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T13:06:28Z",
+"started_at":"2026-11-02T13:06:31Z",
+"completed_at":"2026-11-02T13:07:02Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T13:06:28Z",
+"started_at":"2026-11-02T13:06:31Z",
+"completed_at":"2026-11-02T13:07:04Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T13:06:28Z",
+"started_at":"2026-11-02T13:06:41Z",
+"completed_at":"2026-11-02T13:39:06Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T13:06:28Z",
+"started_at":"2026-11-02T13:06:31Z",
+"completed_at":"2026-11-02T13:10:48Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T13:06:28Z",
+"started_at":"2026-11-02T13:06:34Z",
+"completed_at":"2026-11-02T13:57:44Z",
+"conclusion":"failure"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T13:06:28Z",
+"started_at":"2026-11-02T13:06:30Z",
+"completed_at":"2026-11-02T13:07:55Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T13:06:28Z",
+"started_at":"2026-11-02T13:06:30Z",
+"completed_at":"2026-11-02T13:39:59Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T13:06:28Z",
+"started_at":"2026-11-02T13:06:30Z",
+"completed_at":"2026-11-02T13:45:13Z",
+"conclusion":"success"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T13:06:28Z",
+"started_at":"2026-11-02T13:06:28Z",
+"completed_at":"2026-11-02T13:06:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T13:06:28Z",
+"started_at":"2026-11-02T13:06:28Z",
+"completed_at":"2026-11-02T13:06:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T13:06:28Z",
+"started_at":"2026-11-02T13:06:28Z",
+"completed_at":"2026-11-02T13:06:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T13:06:28Z",
+"started_at":"2026-11-02T13:06:28Z",
+"completed_at":"2026-11-02T13:06:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T13:06:28Z",
+"started_at":"2026-11-02T13:06:28Z",
+"completed_at":"2026-11-02T13:06:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T13:06:28Z",
+"started_at":"2026-11-02T13:06:28Z",
+"completed_at":"2026-11-02T13:06:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T13:06:28Z",
+"started_at":"2026-11-02T13:06:28Z",
+"completed_at":"2026-11-02T13:06:28Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T13:06:28Z",
+"started_at":"2026-11-02T13:06:28Z",
+"completed_at":"2026-11-02T13:06:28Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T13:07:16Z",
+"started_at":"2026-11-02T13:07:16Z",
+"completed_at":"2026-11-02T13:07:16Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T13:07:16Z",
+"started_at":"2026-11-02T13:07:16Z",
+"completed_at":"2026-11-02T13:07:16Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T13:40:00Z",
+"started_at":"2026-11-02T13:40:00Z",
+"completed_at":"2026-11-02T13:40:00Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T13:45:14Z",
+"started_at":"2026-11-02T13:45:14Z",
+"completed_at":"2026-11-02T13:45:13Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T13:57:44Z",
+"started_at":"2026-11-02T13:57:47Z",
+"completed_at":"2026-11-02T13:59:06Z",
+"conclusion":"failure"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T13:57:44Z",
+"started_at":"2026-11-02T13:57:52Z",
+"completed_at":"2026-11-02T13:58:04Z",
+"conclusion":"failure"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T13:57:45Z",
+"started_at":"2026-11-02T13:57:45Z",
+"completed_at":"2026-11-02T13:57:44Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T13:57:45Z",
+"started_at":"2026-11-02T13:57:45Z",
+"completed_at":"2026-11-02T13:57:44Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T13:59:06Z",
+"started_at":"2026-11-02T13:59:09Z",
+"completed_at":"2026-11-02T13:59:36Z",
+"conclusion":"failure"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T13:59:06Z",
+"started_at":"2026-11-02T13:59:06Z",
+"completed_at":"2026-11-02T13:59:06Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41458260834,
+"run_number":3978,
+"head_sha":"45fc769da4b65d63a9525a10b26e703780d20232",
+"created_at":"2026-11-02T14:02:52Z",
+"status":"completed",
+"conclusion":"failure",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T14:02:53Z",
+"started_at":"2026-11-02T14:02:56Z",
+"completed_at":"2026-11-02T14:03:26Z",
+"conclusion":"success"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T14:02:54Z",
+"started_at":"2026-11-02T14:02:54Z",
+"completed_at":"2026-11-02T14:02:53Z",
+"conclusion":"skipped"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T14:02:54Z",
+"started_at":"2026-11-02T14:02:54Z",
+"completed_at":"2026-11-02T14:02:53Z",
+"conclusion":"skipped"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:30Z",
+"completed_at":"2026-11-02T14:03:51Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:30Z",
+"completed_at":"2026-11-02T14:10:23Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:29Z",
+"completed_at":"2026-11-02T14:04:17Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:30Z",
+"completed_at":"2026-11-02T14:04:12Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:30Z",
+"completed_at":"2026-11-02T14:04:44Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:29Z",
+"completed_at":"2026-11-02T14:31:20Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:30Z",
+"completed_at":"2026-11-02T14:43:21Z",
+"conclusion":"success"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:30Z",
+"completed_at":"2026-11-02T14:04:02Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:29Z",
+"completed_at":"2026-11-02T14:04:15Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:30Z",
+"completed_at":"2026-11-02T14:05:12Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:40Z",
+"completed_at":"2026-11-02T14:04:25Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:30Z",
+"completed_at":"2026-11-02T14:04:03Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:30Z",
+"completed_at":"2026-11-02T14:03:52Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:30Z",
+"completed_at":"2026-11-02T14:36:46Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:30Z",
+"completed_at":"2026-11-02T14:07:30Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:30Z",
+"completed_at":"2026-11-02T14:34:42Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:30Z",
+"completed_at":"2026-11-02T14:04:55Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:35Z",
+"completed_at":"2026-11-02T14:33:32Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:30Z",
+"completed_at":"2026-11-02T14:30:18Z",
+"conclusion":"success"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:27Z",
+"completed_at":"2026-11-02T14:03:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:27Z",
+"completed_at":"2026-11-02T14:03:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:27Z",
+"completed_at":"2026-11-02T14:03:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:27Z",
+"completed_at":"2026-11-02T14:03:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:27Z",
+"completed_at":"2026-11-02T14:03:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:27Z",
+"completed_at":"2026-11-02T14:03:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:27Z",
+"completed_at":"2026-11-02T14:03:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T14:03:27Z",
+"started_at":"2026-11-02T14:03:27Z",
+"completed_at":"2026-11-02T14:03:27Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T14:04:25Z",
+"started_at":"2026-11-02T14:04:25Z",
+"completed_at":"2026-11-02T14:04:25Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T14:04:25Z",
+"started_at":"2026-11-02T14:04:25Z",
+"completed_at":"2026-11-02T14:04:25Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T14:30:19Z",
+"started_at":"2026-11-02T14:30:19Z",
+"completed_at":"2026-11-02T14:30:18Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T14:33:32Z",
+"started_at":"2026-11-02T14:33:32Z",
+"completed_at":"2026-11-02T14:33:32Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T14:36:46Z",
+"started_at":"2026-11-02T14:36:49Z",
+"completed_at":"2026-11-02T14:37:02Z",
+"conclusion":"success"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T14:36:46Z",
+"started_at":"2026-11-02T14:36:49Z",
+"completed_at":"2026-11-02T14:37:59Z",
+"conclusion":"failure"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T14:36:46Z",
+"started_at":"2026-11-02T14:36:46Z",
+"completed_at":"2026-11-02T14:36:46Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T14:36:46Z",
+"started_at":"2026-11-02T14:36:46Z",
+"completed_at":"2026-11-02T14:36:46Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T14:43:21Z",
+"started_at":"2026-11-02T14:43:34Z",
+"completed_at":"2026-11-02T14:44:02Z",
+"conclusion":"failure"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T14:43:21Z",
+"started_at":"2026-11-02T14:43:21Z",
+"completed_at":"2026-11-02T14:43:21Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41466997614,
+"run_number":3984,
+"head_sha":"a568a2e128f8df25eb6a960838737c0bda277fac",
+"created_at":"2026-11-02T14:58:18Z",
+"status":"completed",
+"conclusion":"failure",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T14:58:18Z",
+"started_at":"2026-11-02T14:58:21Z",
+"completed_at":"2026-11-02T14:58:46Z",
+"conclusion":"success"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T14:58:19Z",
+"started_at":"2026-11-02T14:58:19Z",
+"completed_at":"2026-11-02T14:58:18Z",
+"conclusion":"skipped"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T14:58:19Z",
+"started_at":"2026-11-02T14:58:19Z",
+"completed_at":"2026-11-02T14:58:18Z",
+"conclusion":"skipped"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:49Z",
+"completed_at":"2026-11-02T14:59:28Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:49Z",
+"completed_at":"2026-11-02T15:27:42Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:49Z",
+"completed_at":"2026-11-02T15:00:12Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:49Z",
+"completed_at":"2026-11-02T15:00:27Z",
+"conclusion":"success"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:52Z",
+"completed_at":"2026-11-02T14:59:12Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:50Z",
+"completed_at":"2026-11-02T15:05:29Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:52Z",
+"completed_at":"2026-11-02T14:59:27Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:51Z",
+"completed_at":"2026-11-02T14:59:30Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:49Z",
+"completed_at":"2026-11-02T15:00:17Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:50Z",
+"completed_at":"2026-11-02T15:24:58Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:49Z",
+"completed_at":"2026-11-02T15:01:32Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:49Z",
+"completed_at":"2026-11-02T14:59:25Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:49Z",
+"completed_at":"2026-11-02T14:59:32Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:49Z",
+"completed_at":"2026-11-02T15:17:58Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:49Z",
+"completed_at":"2026-11-02T15:20:35Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:49Z",
+"completed_at":"2026-11-02T15:03:04Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:49Z",
+"completed_at":"2026-11-02T15:32:32Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:49Z",
+"completed_at":"2026-11-02T15:00:28Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:51Z",
+"completed_at":"2026-11-02T15:18:25Z",
+"conclusion":"success"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:46Z",
+"completed_at":"2026-11-02T14:58:46Z",
+"conclusion":"skipped"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:46Z",
+"completed_at":"2026-11-02T14:58:46Z",
+"conclusion":"skipped"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:46Z",
+"completed_at":"2026-11-02T14:58:46Z",
+"conclusion":"skipped"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:46Z",
+"completed_at":"2026-11-02T14:58:46Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:46Z",
+"completed_at":"2026-11-02T14:58:46Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:46Z",
+"completed_at":"2026-11-02T14:58:46Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:46Z",
+"completed_at":"2026-11-02T14:58:46Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T14:58:46Z",
+"started_at":"2026-11-02T14:58:46Z",
+"completed_at":"2026-11-02T14:58:46Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T14:59:31Z",
+"started_at":"2026-11-02T14:59:31Z",
+"completed_at":"2026-11-02T14:59:30Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T14:59:31Z",
+"started_at":"2026-11-02T14:59:31Z",
+"completed_at":"2026-11-02T14:59:30Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T15:18:25Z",
+"started_at":"2026-11-02T15:18:28Z",
+"completed_at":"2026-11-02T15:18:41Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T15:18:26Z",
+"started_at":"2026-11-02T15:18:26Z",
+"completed_at":"2026-11-02T15:18:25Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T15:20:36Z",
+"started_at":"2026-11-02T15:20:36Z",
+"completed_at":"2026-11-02T15:20:35Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T15:32:32Z",
+"started_at":"2026-11-02T15:32:40Z",
+"completed_at":"2026-11-02T15:33:54Z",
+"conclusion":"failure"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T15:32:32Z",
+"started_at":"2026-11-02T15:32:32Z",
+"completed_at":"2026-11-02T15:32:32Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T15:32:32Z",
+"started_at":"2026-11-02T15:32:32Z",
+"completed_at":"2026-11-02T15:32:32Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T15:33:54Z",
+"started_at":"2026-11-02T15:33:58Z",
+"completed_at":"2026-11-02T15:34:29Z",
+"conclusion":"failure"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T15:33:55Z",
+"started_at":"2026-11-02T15:33:55Z",
+"completed_at":"2026-11-02T15:33:54Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41475249173,
+"run_number":3991,
+"head_sha":"ea59e9a09de56447326ae71d8a45fec81c3cc275",
+"created_at":"2026-11-02T15:48:41Z",
+"status":"completed",
+"conclusion":"failure",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T15:48:42Z",
+"started_at":"2026-11-02T15:48:45Z",
+"completed_at":"2026-11-02T15:49:09Z",
+"conclusion":"success"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T15:48:42Z",
+"started_at":"2026-11-02T15:48:42Z",
+"completed_at":"2026-11-02T15:48:42Z",
+"conclusion":"skipped"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T15:48:51Z",
+"started_at":"2026-11-02T15:48:51Z",
+"completed_at":"2026-11-02T15:48:42Z",
+"conclusion":"skipped"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:12Z",
+"completed_at":"2026-11-02T15:49:33Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:12Z",
+"completed_at":"2026-11-02T15:50:55Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:12Z",
+"completed_at":"2026-11-02T15:50:07Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:20Z",
+"completed_at":"2026-11-02T16:17:45Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:12Z",
+"completed_at":"2026-11-02T15:49:59Z",
+"conclusion":"success"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:17Z",
+"completed_at":"2026-11-02T15:49:54Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:12Z",
+"completed_at":"2026-11-02T15:50:01Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:12Z",
+"completed_at":"2026-11-02T15:52:17Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:13Z",
+"completed_at":"2026-11-02T16:16:37Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:12Z",
+"completed_at":"2026-11-02T15:49:53Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:12Z",
+"completed_at":"2026-11-02T15:56:15Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:12Z",
+"completed_at":"2026-11-02T15:49:43Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:12Z",
+"completed_at":"2026-11-02T15:49:49Z",
+"conclusion":"success"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:09Z",
+"completed_at":"2026-11-02T15:49:09Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:13Z",
+"completed_at":"2026-11-02T16:18:18Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:12Z",
+"completed_at":"2026-11-02T15:50:19Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:12Z",
+"completed_at":"2026-11-02T16:08:39Z",
+"conclusion":"success"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:09Z",
+"completed_at":"2026-11-02T15:49:09Z",
+"conclusion":"skipped"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:09Z",
+"completed_at":"2026-11-02T15:49:09Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:09Z",
+"completed_at":"2026-11-02T15:49:09Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:12Z",
+"completed_at":"2026-11-02T16:22:01Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:13Z",
+"completed_at":"2026-11-02T15:53:33Z",
+"conclusion":"success"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:09Z",
+"completed_at":"2026-11-02T15:49:09Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T15:49:09Z",
+"started_at":"2026-11-02T15:49:09Z",
+"completed_at":"2026-11-02T15:49:09Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T15:49:10Z",
+"started_at":"2026-11-02T15:49:10Z",
+"completed_at":"2026-11-02T15:49:09Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T15:49:10Z",
+"started_at":"2026-11-02T15:49:12Z",
+"completed_at":"2026-11-02T16:28:37Z",
+"conclusion":"success"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T15:49:10Z",
+"started_at":"2026-11-02T15:49:10Z",
+"completed_at":"2026-11-02T15:49:09Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T15:50:00Z",
+"started_at":"2026-11-02T15:50:00Z",
+"completed_at":"2026-11-02T15:50:00Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T15:50:00Z",
+"started_at":"2026-11-02T15:50:00Z",
+"completed_at":"2026-11-02T15:50:00Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T16:08:39Z",
+"started_at":"2026-11-02T16:08:48Z",
+"completed_at":"2026-11-02T16:11:01Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T16:08:39Z",
+"started_at":"2026-11-02T16:08:39Z",
+"completed_at":"2026-11-02T16:08:39Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T16:22:02Z",
+"started_at":"2026-11-02T16:22:02Z",
+"completed_at":"2026-11-02T16:22:01Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T16:22:02Z",
+"started_at":"2026-11-02T16:22:02Z",
+"completed_at":"2026-11-02T16:22:01Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T16:28:37Z",
+"started_at":"2026-11-02T16:28:40Z",
+"completed_at":"2026-11-02T16:29:39Z",
+"conclusion":"failure"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T16:28:37Z",
+"started_at":"2026-11-02T16:28:37Z",
+"completed_at":"2026-11-02T16:28:37Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T16:29:40Z",
+"started_at":"2026-11-02T16:29:43Z",
+"completed_at":"2026-11-02T16:30:11Z",
+"conclusion":"failure"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T16:29:40Z",
+"started_at":"2026-11-02T16:29:40Z",
+"completed_at":"2026-11-02T16:29:40Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41491607650,
+"run_number":4009,
+"head_sha":"d40e377e5d1d7fba3fae4bbbd9311e14fa47a988",
+"created_at":"2026-11-02T17:29:09Z",
+"status":"completed",
+"conclusion":"failure",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T17:29:10Z",
+"started_at":"2026-11-02T17:29:13Z",
+"completed_at":"2026-11-02T17:30:20Z",
+"conclusion":"success"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T17:29:10Z",
+"started_at":"2026-11-02T17:29:10Z",
+"completed_at":"2026-11-02T17:29:10Z",
+"conclusion":"skipped"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T17:29:10Z",
+"started_at":"2026-11-02T17:29:10Z",
+"completed_at":"2026-11-02T17:29:10Z",
+"conclusion":"skipped"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:23Z",
+"completed_at":"2026-11-02T17:30:59Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:23Z",
+"completed_at":"2026-11-02T17:34:05Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:23Z",
+"completed_at":"2026-11-02T17:37:06Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:24Z",
+"completed_at":"2026-11-02T17:31:27Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:24Z",
+"completed_at":"2026-11-02T17:31:08Z",
+"conclusion":"success"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:23Z",
+"completed_at":"2026-11-02T17:31:25Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:34Z",
+"completed_at":"2026-11-02T17:31:37Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:23Z",
+"completed_at":"2026-11-02T17:34:24Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:24Z",
+"completed_at":"2026-11-02T17:31:12Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:24Z",
+"completed_at":"2026-11-02T18:05:51Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:24Z",
+"completed_at":"2026-11-02T17:57:29Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:24Z",
+"completed_at":"2026-11-02T17:30:49Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:23Z",
+"completed_at":"2026-11-02T17:30:57Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:24Z",
+"completed_at":"2026-11-02T18:04:24Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:24Z",
+"completed_at":"2026-11-02T18:03:09Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:23Z",
+"completed_at":"2026-11-02T17:50:46Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:23Z",
+"completed_at":"2026-11-02T17:58:55Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:24Z",
+"completed_at":"2026-11-02T17:31:56Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:23Z",
+"completed_at":"2026-11-02T17:34:47Z",
+"conclusion":"success"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:21Z",
+"completed_at":"2026-11-02T17:30:20Z",
+"conclusion":"skipped"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:21Z",
+"completed_at":"2026-11-02T17:30:20Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:21Z",
+"completed_at":"2026-11-02T17:30:20Z",
+"conclusion":"skipped"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:21Z",
+"completed_at":"2026-11-02T17:30:20Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:21Z",
+"completed_at":"2026-11-02T17:30:21Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:21Z",
+"completed_at":"2026-11-02T17:30:21Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:21Z",
+"completed_at":"2026-11-02T17:30:20Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T17:30:21Z",
+"started_at":"2026-11-02T17:30:21Z",
+"completed_at":"2026-11-02T17:30:21Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T17:31:37Z",
+"started_at":"2026-11-02T17:31:37Z",
+"completed_at":"2026-11-02T17:31:37Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T17:31:37Z",
+"started_at":"2026-11-02T17:31:37Z",
+"completed_at":"2026-11-02T17:31:37Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T17:50:47Z",
+"started_at":"2026-11-02T17:50:47Z",
+"completed_at":"2026-11-02T17:50:47Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T17:58:55Z",
+"started_at":"2026-11-02T17:58:58Z",
+"completed_at":"2026-11-02T17:59:59Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T17:58:55Z",
+"started_at":"2026-11-02T17:58:55Z",
+"completed_at":"2026-11-02T17:58:55Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T18:03:09Z",
+"started_at":"2026-11-02T18:03:09Z",
+"completed_at":"2026-11-02T18:03:09Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T18:04:24Z",
+"started_at":"2026-11-02T18:04:28Z",
+"completed_at":"2026-11-02T18:06:17Z",
+"conclusion":"failure"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T18:04:25Z",
+"started_at":"2026-11-02T18:04:25Z",
+"completed_at":"2026-11-02T18:04:24Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T18:06:17Z",
+"started_at":"2026-11-02T18:06:20Z",
+"completed_at":"2026-11-02T18:06:48Z",
+"conclusion":"failure"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T18:06:17Z",
+"started_at":"2026-11-02T18:06:17Z",
+"completed_at":"2026-11-02T18:06:17Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41498469873,
+"run_number":4015,
+"head_sha":"38dcb6c5dbade5206f2fae885334483082f36d10",
+"created_at":"2026-11-02T18:13:14Z",
+"status":"completed",
+"conclusion":"failure",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T18:13:15Z",
+"started_at":"2026-11-02T18:13:18Z",
+"completed_at":"2026-11-02T18:13:52Z",
+"conclusion":"success"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T18:13:15Z",
+"started_at":"2026-11-02T18:13:15Z",
+"completed_at":"2026-11-02T18:13:15Z",
+"conclusion":"skipped"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T18:13:15Z",
+"started_at":"2026-11-02T18:13:15Z",
+"completed_at":"2026-11-02T18:13:15Z",
+"conclusion":"skipped"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:13:55Z",
+"completed_at":"2026-11-02T18:14:15Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:13:55Z",
+"completed_at":"2026-11-02T18:14:29Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:13:59Z",
+"completed_at":"2026-11-02T18:14:45Z",
+"conclusion":"success"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:13:55Z",
+"completed_at":"2026-11-02T18:14:32Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:14:05Z",
+"completed_at":"2026-11-02T18:15:08Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:13:55Z",
+"completed_at":"2026-11-02T18:20:49Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:13:55Z",
+"completed_at":"2026-11-02T18:14:49Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:13:56Z",
+"completed_at":"2026-11-02T18:17:51Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:13:55Z",
+"completed_at":"2026-11-02T18:39:37Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:14:00Z",
+"completed_at":"2026-11-02T18:15:46Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:13:55Z",
+"completed_at":"2026-11-02T18:55:06Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:14:02Z",
+"completed_at":"2026-11-02T18:14:40Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:14:03Z",
+"completed_at":"2026-11-02T18:14:32Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:13:55Z",
+"completed_at":"2026-11-02T18:45:43Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:13:56Z",
+"completed_at":"2026-11-02T18:15:24Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:14:00Z",
+"completed_at":"2026-11-02T18:53:01Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:13:58Z",
+"completed_at":"2026-11-02T18:17:45Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:13:55Z",
+"completed_at":"2026-11-02T18:47:54Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:13:55Z",
+"completed_at":"2026-11-02T18:25:51Z",
+"conclusion":"success"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:13:52Z",
+"completed_at":"2026-11-02T18:13:52Z",
+"conclusion":"skipped"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:13:52Z",
+"completed_at":"2026-11-02T18:13:52Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:13:52Z",
+"completed_at":"2026-11-02T18:13:52Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:13:52Z",
+"completed_at":"2026-11-02T18:13:52Z",
+"conclusion":"skipped"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:13:52Z",
+"completed_at":"2026-11-02T18:13:52Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:13:52Z",
+"completed_at":"2026-11-02T18:13:52Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T18:13:52Z",
+"started_at":"2026-11-02T18:13:52Z",
+"completed_at":"2026-11-02T18:13:52Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T18:13:53Z",
+"started_at":"2026-11-02T18:13:53Z",
+"completed_at":"2026-11-02T18:13:52Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T18:15:09Z",
+"started_at":"2026-11-02T18:15:09Z",
+"completed_at":"2026-11-02T18:15:09Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T18:15:09Z",
+"started_at":"2026-11-02T18:15:09Z",
+"completed_at":"2026-11-02T18:15:09Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T18:25:52Z",
+"started_at":"2026-11-02T18:25:54Z",
+"completed_at":"2026-11-02T18:26:13Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T18:25:52Z",
+"started_at":"2026-11-02T18:25:52Z",
+"completed_at":"2026-11-02T18:25:51Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T18:47:55Z",
+"started_at":"2026-11-02T18:47:55Z",
+"completed_at":"2026-11-02T18:47:55Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T18:47:55Z",
+"started_at":"2026-11-02T18:47:55Z",
+"completed_at":"2026-11-02T18:47:55Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T18:53:02Z",
+"started_at":"2026-11-02T18:53:05Z",
+"completed_at":"2026-11-02T18:54:19Z",
+"conclusion":"failure"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T18:53:02Z",
+"started_at":"2026-11-02T18:53:02Z",
+"completed_at":"2026-11-02T18:53:02Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T18:55:07Z",
+"started_at":"2026-11-02T18:55:09Z",
+"completed_at":"2026-11-02T18:55:37Z",
+"conclusion":"failure"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T18:55:07Z",
+"started_at":"2026-11-02T18:55:07Z",
+"completed_at":"2026-11-02T18:55:06Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41506687984,
+"run_number":4028,
+"head_sha":"871a20da138592ac892f4652a4f82992a6626783",
+"created_at":"2026-11-02T19:05:34Z",
+"status":"completed",
+"conclusion":"failure",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T19:05:35Z",
+"started_at":"2026-11-02T19:05:38Z",
+"completed_at":"2026-11-02T19:06:09Z",
+"conclusion":"success"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T19:05:35Z",
+"started_at":"2026-11-02T19:05:35Z",
+"completed_at":"2026-11-02T19:05:35Z",
+"conclusion":"skipped"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T19:05:35Z",
+"started_at":"2026-11-02T19:05:35Z",
+"completed_at":"2026-11-02T19:05:35Z",
+"conclusion":"skipped"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:13Z",
+"completed_at":"2026-11-02T19:07:01Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:12Z",
+"completed_at":"2026-11-02T19:06:52Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:13Z",
+"completed_at":"2026-11-02T19:06:54Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:14Z",
+"completed_at":"2026-11-02T19:07:05Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:14Z",
+"completed_at":"2026-11-02T19:41:35Z",
+"conclusion":"success"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:10Z",
+"completed_at":"2026-11-02T19:06:09Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:13Z",
+"completed_at":"2026-11-02T19:30:28Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:13Z",
+"completed_at":"2026-11-02T19:08:04Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:20Z",
+"completed_at":"2026-11-02T19:13:35Z",
+"conclusion":"success"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:10Z",
+"completed_at":"2026-11-02T19:06:09Z",
+"conclusion":"skipped"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:16Z",
+"completed_at":"2026-11-02T19:06:40Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:27Z",
+"completed_at":"2026-11-02T19:09:04Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:14Z",
+"completed_at":"2026-11-02T19:07:08Z",
+"conclusion":"success"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:10Z",
+"completed_at":"2026-11-02T19:06:09Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:10Z",
+"completed_at":"2026-11-02T19:06:09Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:13Z",
+"completed_at":"2026-11-02T19:07:18Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:12Z",
+"completed_at":"2026-11-02T19:08:37Z",
+"conclusion":"success"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:10Z",
+"completed_at":"2026-11-02T19:06:09Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:10Z",
+"completed_at":"2026-11-02T19:06:10Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:13Z",
+"completed_at":"2026-11-02T19:41:07Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:13Z",
+"completed_at":"2026-11-02T19:31:46Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:13Z",
+"completed_at":"2026-11-02T19:07:54Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:16Z",
+"completed_at":"2026-11-02T19:10:23Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:13Z",
+"completed_at":"2026-11-02T19:26:39Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:13Z",
+"completed_at":"2026-11-02T19:24:50Z",
+"conclusion":"success"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:10Z",
+"completed_at":"2026-11-02T19:06:10Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T19:06:10Z",
+"started_at":"2026-11-02T19:06:10Z",
+"completed_at":"2026-11-02T19:06:10Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T19:07:05Z",
+"started_at":"2026-11-02T19:07:05Z",
+"completed_at":"2026-11-02T19:07:05Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T19:07:05Z",
+"started_at":"2026-11-02T19:07:05Z",
+"completed_at":"2026-11-02T19:07:05Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T19:24:51Z",
+"started_at":"2026-11-02T19:24:51Z",
+"completed_at":"2026-11-02T19:24:51Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T19:26:39Z",
+"started_at":"2026-11-02T19:26:42Z",
+"completed_at":"2026-11-02T19:26:57Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T19:26:40Z",
+"started_at":"2026-11-02T19:26:40Z",
+"completed_at":"2026-11-02T19:26:39Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T19:41:07Z",
+"started_at":"2026-11-02T19:41:10Z",
+"completed_at":"2026-11-02T19:42:22Z",
+"conclusion":"failure"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T19:41:07Z",
+"started_at":"2026-11-02T19:41:07Z",
+"completed_at":"2026-11-02T19:41:07Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T19:41:07Z",
+"started_at":"2026-11-02T19:41:07Z",
+"completed_at":"2026-11-02T19:41:07Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T19:42:23Z",
+"started_at":"2026-11-02T19:42:26Z",
+"completed_at":"2026-11-02T19:44:23Z",
+"conclusion":"failure"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T19:42:23Z",
+"started_at":"2026-11-02T19:42:23Z",
+"completed_at":"2026-11-02T19:42:23Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41513327647,
+"run_number":4035,
+"head_sha":"d15a2d7df189cf48a24abd8d62e032696652549c",
+"created_at":"2026-11-02T19:48:18Z",
+"status":"completed",
+"conclusion":"failure",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T19:48:19Z",
+"started_at":"2026-11-02T19:48:21Z",
+"completed_at":"2026-11-02T19:48:46Z",
+"conclusion":"success"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T19:48:19Z",
+"started_at":"2026-11-02T19:48:19Z",
+"completed_at":"2026-11-02T19:48:19Z",
+"conclusion":"skipped"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T19:48:19Z",
+"started_at":"2026-11-02T19:48:19Z",
+"completed_at":"2026-11-02T19:48:19Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:49Z",
+"completed_at":"2026-11-02T19:49:30Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:50Z",
+"completed_at":"2026-11-02T19:49:45Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:49Z",
+"completed_at":"2026-11-02T20:17:12Z",
+"conclusion":"success"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:50Z",
+"completed_at":"2026-11-02T19:49:12Z",
+"conclusion":"success"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:50Z",
+"completed_at":"2026-11-02T19:49:33Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:49Z",
+"completed_at":"2026-11-02T19:55:32Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:51Z",
+"completed_at":"2026-11-02T19:49:41Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:50Z",
+"completed_at":"2026-11-02T19:49:51Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:50Z",
+"completed_at":"2026-11-02T19:50:06Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:50Z",
+"completed_at":"2026-11-02T20:20:39Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:50Z",
+"completed_at":"2026-11-02T19:49:36Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:50Z",
+"completed_at":"2026-11-02T19:49:38Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:49Z",
+"completed_at":"2026-11-02T19:49:14Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:50Z",
+"completed_at":"2026-11-02T19:50:38Z",
+"conclusion":"success"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:47Z",
+"completed_at":"2026-11-02T19:48:46Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:50Z",
+"completed_at":"2026-11-02T20:28:31Z",
+"conclusion":"success"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:47Z",
+"completed_at":"2026-11-02T19:48:46Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:50Z",
+"completed_at":"2026-11-02T19:53:06Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:50Z",
+"completed_at":"2026-11-02T19:50:21Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:50Z",
+"completed_at":"2026-11-02T20:21:05Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:50Z",
+"completed_at":"2026-11-02T20:16:10Z",
+"conclusion":"success"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:47Z",
+"completed_at":"2026-11-02T19:48:46Z",
+"conclusion":"skipped"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:47Z",
+"completed_at":"2026-11-02T19:48:46Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:47Z",
+"completed_at":"2026-11-02T19:48:46Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:47Z",
+"completed_at":"2026-11-02T19:48:46Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:47Z",
+"completed_at":"2026-11-02T19:48:47Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T19:48:47Z",
+"started_at":"2026-11-02T19:48:47Z",
+"completed_at":"2026-11-02T19:48:47Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T19:49:30Z",
+"started_at":"2026-11-02T19:49:30Z",
+"completed_at":"2026-11-02T19:49:30Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T19:49:30Z",
+"started_at":"2026-11-02T19:49:30Z",
+"completed_at":"2026-11-02T19:49:30Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T19:50:38Z",
+"started_at":"2026-11-02T19:55:51Z",
+"completed_at":"2026-11-02T19:56:03Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T19:50:38Z",
+"started_at":"2026-11-02T19:50:38Z",
+"completed_at":"2026-11-02T19:50:38Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T20:16:11Z",
+"started_at":"2026-11-02T20:16:11Z",
+"completed_at":"2026-11-02T20:16:11Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T20:21:05Z",
+"started_at":"2026-11-02T20:21:05Z",
+"completed_at":"2026-11-02T20:21:05Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T20:28:31Z",
+"started_at":"2026-11-02T20:28:34Z",
+"completed_at":"2026-11-02T20:29:45Z",
+"conclusion":"failure"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T20:28:31Z",
+"started_at":"2026-11-02T20:28:31Z",
+"completed_at":"2026-11-02T20:28:31Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T20:29:45Z",
+"started_at":"2026-11-02T20:29:48Z",
+"completed_at":"2026-11-02T20:30:12Z",
+"conclusion":"failure"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T20:29:45Z",
+"started_at":"2026-11-02T20:29:45Z",
+"completed_at":"2026-11-02T20:29:45Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41513913688,
+"run_number":4046,
+"head_sha":"b8e823699981866383f1afa54ce708ded3419316",
+"created_at":"2026-11-02T19:52:09Z",
+"status":"completed",
+"conclusion":"failure",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-02T19:52:10Z",
+"started_at":"2026-11-02T19:55:34Z",
+"completed_at":"2026-11-02T19:56:01Z",
+"conclusion":"success"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-02T19:52:10Z",
+"started_at":"2026-11-02T19:52:10Z",
+"completed_at":"2026-11-02T19:52:10Z",
+"conclusion":"skipped"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-02T19:52:10Z",
+"started_at":"2026-11-02T19:52:10Z",
+"completed_at":"2026-11-02T19:52:10Z",
+"conclusion":"skipped"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-02T19:56:01Z",
+"started_at":"2026-11-02T20:00:26Z",
+"completed_at":"2026-11-02T20:01:13Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-02T19:56:01Z",
+"started_at":"2026-11-02T19:57:40Z",
+"completed_at":"2026-11-02T19:58:49Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-02T19:56:01Z",
+"started_at":"2026-11-02T20:16:52Z",
+"completed_at":"2026-11-02T20:17:44Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-02T19:56:01Z",
+"started_at":"2026-11-02T20:03:21Z",
+"completed_at":"2026-11-02T20:04:14Z",
+"conclusion":"success"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-02T19:56:01Z",
+"started_at":"2026-11-02T19:57:08Z",
+"completed_at":"2026-11-02T19:57:29Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-02T19:56:01Z",
+"started_at":"2026-11-02T19:57:27Z",
+"completed_at":"2026-11-02T20:37:31Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-02T19:56:01Z",
+"started_at":"2026-11-02T20:06:06Z",
+"completed_at":"2026-11-02T20:30:05Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-02T19:56:01Z",
+"started_at":"2026-11-02T20:10:28Z",
+"completed_at":"2026-11-02T20:17:43Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-02T19:56:01Z",
+"started_at":"2026-11-02T19:57:59Z",
+"completed_at":"2026-11-02T19:59:02Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-02T19:56:01Z",
+"started_at":"2026-11-02T19:58:52Z",
+"completed_at":"2026-11-02T20:00:24Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-02T19:56:01Z",
+"started_at":"2026-11-02T20:17:46Z",
+"completed_at":"2026-11-02T20:18:18Z",
+"conclusion":"success"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-02T19:56:01Z",
+"started_at":"2026-11-02T19:56:01Z",
+"completed_at":"2026-11-02T19:56:01Z",
+"conclusion":"skipped"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-02T19:56:01Z",
+"started_at":"2026-11-02T19:56:01Z",
+"completed_at":"2026-11-02T19:56:01Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-02T19:56:02Z",
+"started_at":"2026-11-02T19:56:02Z",
+"completed_at":"2026-11-02T19:56:01Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-02T19:56:02Z",
+"started_at":"2026-11-02T20:14:44Z",
+"completed_at":"2026-11-02T20:15:21Z",
+"conclusion":"success"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-02T19:56:02Z",
+"started_at":"2026-11-02T19:56:02Z",
+"completed_at":"2026-11-02T19:56:01Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-02T19:56:02Z",
+"started_at":"2026-11-02T20:18:36Z",
+"completed_at":"2026-11-02T20:52:12Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-02T19:56:02Z",
+"started_at":"2026-11-02T20:18:44Z",
+"completed_at":"2026-11-02T20:20:18Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-02T19:56:02Z",
+"started_at":"2026-11-02T20:18:58Z",
+"completed_at":"2026-11-02T20:37:06Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-02T19:56:02Z",
+"started_at":"2026-11-02T20:19:05Z",
+"completed_at":"2026-11-02T20:19:56Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-02T19:56:02Z",
+"started_at":"2026-11-02T20:14:51Z",
+"completed_at":"2026-11-02T20:15:51Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-02T19:56:02Z",
+"started_at":"2026-11-02T19:56:02Z",
+"completed_at":"2026-11-02T19:56:01Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-02T19:56:02Z",
+"started_at":"2026-11-02T20:19:55Z",
+"completed_at":"2026-11-02T20:24:11Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-02T19:56:02Z",
+"started_at":"2026-11-02T20:19:32Z",
+"completed_at":"2026-11-02T20:58:29Z",
+"conclusion":"success"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-02T19:56:02Z",
+"started_at":"2026-11-02T19:56:02Z",
+"completed_at":"2026-11-02T19:56:01Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-02T19:56:02Z",
+"started_at":"2026-11-02T19:56:02Z",
+"completed_at":"2026-11-02T19:56:02Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-02T19:56:02Z",
+"started_at":"2026-11-02T19:56:02Z",
+"completed_at":"2026-11-02T19:56:02Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-02T20:17:45Z",
+"started_at":"2026-11-02T20:17:45Z",
+"completed_at":"2026-11-02T20:17:44Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-02T20:17:45Z",
+"started_at":"2026-11-02T20:17:45Z",
+"completed_at":"2026-11-02T20:17:44Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-02T20:19:56Z",
+"started_at":"2026-11-02T20:21:18Z",
+"completed_at":"2026-11-02T20:21:29Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-02T20:19:57Z",
+"started_at":"2026-11-02T20:19:57Z",
+"completed_at":"2026-11-02T20:19:56Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-02T20:52:13Z",
+"started_at":"2026-11-02T20:52:13Z",
+"completed_at":"2026-11-02T20:52:13Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-02T20:52:13Z",
+"started_at":"2026-11-02T20:52:13Z",
+"completed_at":"2026-11-02T20:52:13Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-02T20:58:29Z",
+"started_at":"2026-11-02T20:58:34Z",
+"completed_at":"2026-11-02T21:00:03Z",
+"conclusion":"failure"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-02T20:58:29Z",
+"started_at":"2026-11-02T20:58:29Z",
+"completed_at":"2026-11-02T20:58:29Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-02T21:00:03Z",
+"started_at":"2026-11-02T21:00:11Z",
+"completed_at":"2026-11-02T21:00:32Z",
+"conclusion":"failure"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-02T21:00:03Z",
+"started_at":"2026-11-02T21:00:03Z",
+"completed_at":"2026-11-02T21:00:03Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41555455326,
+"run_number":4055,
+"head_sha":"f8bab78d109bac47dd3931a6d90032343388de47",
+"created_at":"2026-11-03T00:48:28Z",
+"status":"completed",
+"conclusion":"failure",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-03T00:48:29Z",
+"started_at":"2026-11-03T00:48:31Z",
+"completed_at":"2026-11-03T00:48:56Z",
+"conclusion":"success"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-03T00:48:29Z",
+"started_at":"2026-11-03T00:48:29Z",
+"completed_at":"2026-11-03T00:48:29Z",
+"conclusion":"skipped"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-03T00:48:29Z",
+"started_at":"2026-11-03T00:48:29Z",
+"completed_at":"2026-11-03T00:48:29Z",
+"conclusion":"skipped"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-03T00:48:56Z",
+"started_at":"2026-11-03T00:49:09Z",
+"completed_at":"2026-11-03T00:49:28Z",
+"conclusion":"success"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-03T00:48:56Z",
+"started_at":"2026-11-03T00:48:59Z",
+"completed_at":"2026-11-03T00:49:34Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-03T00:48:56Z",
+"started_at":"2026-11-03T00:48:59Z",
+"completed_at":"2026-11-03T00:50:09Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-03T00:48:56Z",
+"started_at":"2026-11-03T00:48:59Z",
+"completed_at":"2026-11-03T00:55:39Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-03T00:48:56Z",
+"started_at":"2026-11-03T00:48:59Z",
+"completed_at":"2026-11-03T01:17:52Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-03T00:48:56Z",
+"started_at":"2026-11-03T00:48:59Z",
+"completed_at":"2026-11-03T00:50:00Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-03T00:48:56Z",
+"started_at":"2026-11-03T00:48:59Z",
+"completed_at":"2026-11-03T01:25:29Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-03T00:48:56Z",
+"started_at":"2026-11-03T00:48:59Z",
+"completed_at":"2026-11-03T00:49:55Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-03T00:48:56Z",
+"started_at":"2026-11-03T00:48:59Z",
+"completed_at":"2026-11-03T00:50:36Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-03T00:48:56Z",
+"started_at":"2026-11-03T00:48:59Z",
+"completed_at":"2026-11-03T00:49:44Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-03T00:48:56Z",
+"started_at":"2026-11-03T00:49:00Z",
+"completed_at":"2026-11-03T00:49:47Z",
+"conclusion":"success"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-03T00:48:56Z",
+"started_at":"2026-11-03T00:48:56Z",
+"completed_at":"2026-11-03T00:48:56Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-03T00:48:56Z",
+"started_at":"2026-11-03T00:48:59Z",
+"completed_at":"2026-11-03T00:49:29Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-03T00:48:56Z",
+"started_at":"2026-11-03T00:48:59Z",
+"completed_at":"2026-11-03T00:49:34Z",
+"conclusion":"success"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-03T00:48:56Z",
+"started_at":"2026-11-03T00:48:56Z",
+"completed_at":"2026-11-03T00:48:56Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-03T00:48:57Z",
+"started_at":"2026-11-03T00:48:59Z",
+"completed_at":"2026-11-03T01:21:07Z",
+"conclusion":"success"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-03T00:48:57Z",
+"started_at":"2026-11-03T00:48:57Z",
+"completed_at":"2026-11-03T00:48:56Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-03T00:48:57Z",
+"started_at":"2026-11-03T00:48:59Z",
+"completed_at":"2026-11-03T01:20:26Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-03T00:48:57Z",
+"started_at":"2026-11-03T00:48:59Z",
+"completed_at":"2026-11-03T00:49:50Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-03T00:48:57Z",
+"started_at":"2026-11-03T00:48:59Z",
+"completed_at":"2026-11-03T00:52:39Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-03T00:48:57Z",
+"started_at":"2026-11-03T00:48:59Z",
+"completed_at":"2026-11-03T01:09:33Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-03T00:48:57Z",
+"started_at":"2026-11-03T00:49:00Z",
+"completed_at":"2026-11-03T00:50:00Z",
+"conclusion":"success"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-03T00:48:57Z",
+"started_at":"2026-11-03T00:48:57Z",
+"completed_at":"2026-11-03T00:48:56Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-03T00:48:57Z",
+"started_at":"2026-11-03T00:48:57Z",
+"completed_at":"2026-11-03T00:48:56Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-03T00:48:57Z",
+"started_at":"2026-11-03T00:48:57Z",
+"completed_at":"2026-11-03T00:48:56Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-03T00:48:57Z",
+"started_at":"2026-11-03T00:48:57Z",
+"completed_at":"2026-11-03T00:48:56Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-03T00:48:57Z",
+"started_at":"2026-11-03T00:48:57Z",
+"completed_at":"2026-11-03T00:48:56Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-03T00:49:47Z",
+"started_at":"2026-11-03T00:49:47Z",
+"completed_at":"2026-11-03T00:49:47Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-03T00:49:48Z",
+"started_at":"2026-11-03T00:49:48Z",
+"completed_at":"2026-11-03T00:49:47Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-03T00:49:50Z",
+"started_at":"2026-11-03T00:49:53Z",
+"completed_at":"2026-11-03T00:50:01Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-03T00:49:50Z",
+"started_at":"2026-11-03T00:49:50Z",
+"completed_at":"2026-11-03T00:49:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-03T01:09:34Z",
+"started_at":"2026-11-03T01:09:34Z",
+"completed_at":"2026-11-03T01:09:33Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-03T01:21:07Z",
+"started_at":"2026-11-03T01:21:09Z",
+"completed_at":"2026-11-03T01:22:06Z",
+"conclusion":"failure"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-03T01:21:07Z",
+"started_at":"2026-11-03T01:21:07Z",
+"completed_at":"2026-11-03T01:21:07Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-03T01:21:07Z",
+"started_at":"2026-11-03T01:21:07Z",
+"completed_at":"2026-11-03T01:21:07Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-03T01:25:30Z",
+"started_at":"2026-11-03T01:25:33Z",
+"completed_at":"2026-11-03T01:26:01Z",
+"conclusion":"failure"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-03T01:25:30Z",
+"started_at":"2026-11-03T01:25:30Z",
+"completed_at":"2026-11-03T01:25:29Z",
+"conclusion":"skipped"
+}
+]
+},
+{
+"id":41577822624,
+"run_number":4056,
+"head_sha":"c3a279e3252a8b57bb00b5a677318cd4fe20387f",
+"created_at":"2026-11-03T04:23:15Z",
+"status":"completed",
+"conclusion":"failure",
+"path":".github/workflows/ci.yml",
+"event":"push",
+"head_branch":"main",
+"jobs":[
+{
+"name":"prelude",
+"created_at":"2026-11-03T04:23:16Z",
+"started_at":"2026-11-03T04:23:27Z",
+"completed_at":"2026-11-03T04:23:49Z",
+"conclusion":"success"
+},
+{
+"name":"cancel-superseded",
+"created_at":"2026-11-03T04:23:16Z",
+"started_at":"2026-11-03T04:23:16Z",
+"completed_at":"2026-11-03T04:23:16Z",
+"conclusion":"skipped"
+},
+{
+"name":"refresh",
+"created_at":"2026-11-03T04:23:16Z",
+"started_at":"2026-11-03T04:23:16Z",
+"completed_at":"2026-11-03T04:23:16Z",
+"conclusion":"skipped"
+},
+{
+"name":"validate / validate-hacs",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:52Z",
+"completed_at":"2026-11-03T04:24:22Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (python)",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:52Z",
+"completed_at":"2026-11-03T04:55:06Z",
+"conclusion":"success"
+},
+{
+"name":"tests / briefs",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:52Z",
+"completed_at":"2026-11-03T04:24:39Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (javascript-typescript)",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:52Z",
+"completed_at":"2026-11-03T04:25:31Z",
+"conclusion":"success"
+},
+{
+"name":"governance / policy-docs",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:52Z",
+"completed_at":"2026-11-03T04:24:36Z",
+"conclusion":"success"
+},
+{
+"name":"hassfest / hassfest",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:52Z",
+"completed_at":"2026-11-03T04:24:23Z",
+"conclusion":"success"
+},
+{
+"name":"governance / wave-script",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:52Z",
+"completed_at":"2026-11-03T04:24:31Z",
+"conclusion":"success"
+},
+{
+"name":"codeql / Analyze (actions)",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:53Z",
+"completed_at":"2026-11-03T04:24:48Z",
+"conclusion":"success"
+},
+{
+"name":"governance / instrument-self-tests",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:57Z",
+"completed_at":"2026-11-03T04:52:23Z",
+"conclusion":"success"
+},
+{
+"name":"tests / mutation",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:53Z",
+"completed_at":"2026-11-03T04:24:38Z",
+"conclusion":"success"
+},
+{
+"name":"governance / env-matrix",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:52Z",
+"completed_at":"2026-11-03T04:30:48Z",
+"conclusion":"success"
+},
+{
+"name":"governance / record",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:52Z",
+"completed_at":"2026-11-03T04:24:13Z",
+"conclusion":"success"
+},
+{
+"name":"governance / delivery-status-publish",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:53Z",
+"completed_at":"2026-11-03T04:24:22Z",
+"conclusion":"success"
+},
+{
+"name":"tests / typing",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:52Z",
+"completed_at":"2026-11-03T04:24:57Z",
+"conclusion":"success"
+},
+{
+"name":"tests / closures",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:52Z",
+"completed_at":"2026-11-03T04:48:01Z",
+"conclusion":"success"
+},
+{
+"name":"tests / fast (3.14)",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:53Z",
+"completed_at":"2026-11-03T04:56:35Z",
+"conclusion":"success"
+},
+{
+"name":"tests / arch-instrument",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:52Z",
+"completed_at":"2026-11-03T04:42:45Z",
+"conclusion":"success"
+},
+{
+"name":"tests / browser",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:52Z",
+"completed_at":"2026-11-03T04:27:36Z",
+"conclusion":"success"
+},
+{
+"name":"tests / coverage",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:52Z",
+"completed_at":"2026-11-03T04:40:50Z",
+"conclusion":"success"
+},
+{
+"name":"arch-score",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:49Z",
+"completed_at":"2026-11-03T04:23:49Z",
+"conclusion":"skipped"
+},
+{
+"name":"kernel-points",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:49Z",
+"completed_at":"2026-11-03T04:23:49Z",
+"conclusion":"skipped"
+},
+{
+"name":"budget-raise-gate",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:49Z",
+"completed_at":"2026-11-03T04:23:49Z",
+"conclusion":"skipped"
+},
+{
+"name":"governance / delivery-status",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:49Z",
+"completed_at":"2026-11-03T04:23:49Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-status",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:49Z",
+"completed_at":"2026-11-03T04:23:49Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closure-scope",
+"created_at":"2026-11-03T04:23:49Z",
+"started_at":"2026-11-03T04:23:49Z",
+"completed_at":"2026-11-03T04:23:49Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / replay",
+"created_at":"2026-11-03T04:23:50Z",
+"started_at":"2026-11-03T04:23:50Z",
+"completed_at":"2026-11-03T04:23:49Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / nightly-ha",
+"created_at":"2026-11-03T04:23:50Z",
+"started_at":"2026-11-03T04:23:50Z",
+"completed_at":"2026-11-03T04:23:49Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-pins",
+"created_at":"2026-11-03T04:24:38Z",
+"started_at":"2026-11-03T04:24:38Z",
+"completed_at":"2026-11-03T04:24:38Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / mutation-autofix",
+"created_at":"2026-11-03T04:24:38Z",
+"started_at":"2026-11-03T04:24:38Z",
+"completed_at":"2026-11-03T04:24:38Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / coverage-ratchet",
+"created_at":"2026-11-03T04:40:50Z",
+"started_at":"2026-11-03T04:41:03Z",
+"completed_at":"2026-11-03T04:41:13Z",
+"conclusion":"success"
+},
+{
+"name":"tests / graders-head-copy",
+"created_at":"2026-11-03T04:40:50Z",
+"started_at":"2026-11-03T04:40:50Z",
+"completed_at":"2026-11-03T04:40:50Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / closures-autofix",
+"created_at":"2026-11-03T04:48:01Z",
+"started_at":"2026-11-03T04:48:01Z",
+"completed_at":"2026-11-03T04:48:01Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / ci-ratchet",
+"created_at":"2026-11-03T04:56:35Z",
+"started_at":"2026-11-03T04:56:38Z",
+"completed_at":"2026-11-03T04:58:14Z",
+"conclusion":"failure"
+},
+{
+"name":"tests / lane-proofs",
+"created_at":"2026-11-03T04:56:36Z",
+"started_at":"2026-11-03T04:56:36Z",
+"completed_at":"2026-11-03T04:56:35Z",
+"conclusion":"skipped"
+},
+{
+"name":"tests / claims-autofix",
+"created_at":"2026-11-03T04:56:36Z",
+"started_at":"2026-11-03T04:56:36Z",
+"completed_at":"2026-11-03T04:56:35Z",
+"conclusion":"skipped"
+},
+{
+"name":"gate",
+"created_at":"2026-11-03T04:58:15Z",
+"started_at":"2026-11-03T04:58:17Z",
+"completed_at":"2026-11-03T04:58:42Z",
+"conclusion":"failure"
+},
+{
+"name":"pr-contract",
+"created_at":"2026-11-03T04:58:15Z",
+"started_at":"2026-11-03T04:58:15Z",
+"completed_at":"2026-11-03T04:58:14Z",
+"conclusion":"skipped"
+}
+]
+}
+]
+}
\ No newline at end of file
diff --git a/dev/audit/harnesses/r10_rca_ci_critpath_3/runs_red4.json b/dev/audit/harnesses/r10_rca_ci_critpath_3/runs_red4.json
new file mode 100644
index 000000000..31441dac4
--- /dev/null
+++ b/dev/audit/harnesses/r10_rca_ci_critpath_3/runs_red4.json
@@ -0,0 +1,4986 @@
+{
+ "source": "GitHub Actions API, read 2026-11-04 14:00 UTC: every ci.yml push run on main numbered 4009..4128 (cancelled runs included), each with its latest-attempt jobs, reduced to the fields tests/ci_ratchet.py's _walk reads",
+ "workflow_runs": [
+  {
+   "id": 41491607650,
+   "run_number": 4009,
+   "head_sha": "d40e377e5d1d7fba3fae4bbbd9311e14fa47a988",
+   "created_at": "2026-11-02T17:29:09Z",
+   "status": "completed",
+   "conclusion": "failure",
+   "path": ".github/workflows/ci.yml",
+   "event": "push",
+   "head_branch": "main",
+   "jobs": [
+    {
+     "name": "prelude",
+     "created_at": "2026-11-02T17:29:10Z",
+     "started_at": "2026-11-02T17:29:13Z",
+     "completed_at": "2026-11-02T17:30:20Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "cancel-superseded",
+     "created_at": "2026-11-02T17:29:10Z",
+     "started_at": "2026-11-02T17:29:10Z",
+     "completed_at": "2026-11-02T17:29:10Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "refresh",
+     "created_at": "2026-11-02T17:29:10Z",
+     "started_at": "2026-11-02T17:29:10Z",
+     "completed_at": "2026-11-02T17:29:10Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "validate / validate-hacs",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:23Z",
+     "completed_at": "2026-11-02T17:30:59Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / policy-docs",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:23Z",
+     "completed_at": "2026-11-02T17:34:05Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / env-matrix",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:23Z",
+     "completed_at": "2026-11-02T17:37:06Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (actions)",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:24Z",
+     "completed_at": "2026-11-02T17:31:27Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / wave-script",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:24Z",
+     "completed_at": "2026-11-02T17:31:08Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "hassfest / hassfest",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:23Z",
+     "completed_at": "2026-11-02T17:31:25Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / mutation",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:34Z",
+     "completed_at": "2026-11-02T17:31:37Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (javascript-typescript)",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:23Z",
+     "completed_at": "2026-11-02T17:34:24Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / briefs",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:24Z",
+     "completed_at": "2026-11-02T17:31:12Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (python)",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:24Z",
+     "completed_at": "2026-11-02T18:05:51Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / instrument-self-tests",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:24Z",
+     "completed_at": "2026-11-02T17:57:29Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / delivery-status-publish",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:24Z",
+     "completed_at": "2026-11-02T17:30:49Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / record",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:23Z",
+     "completed_at": "2026-11-02T17:30:57Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / closures",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:24Z",
+     "completed_at": "2026-11-02T18:04:24Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / arch-instrument",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:24Z",
+     "completed_at": "2026-11-02T18:03:09Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / fast (3.14)",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:23Z",
+     "completed_at": "2026-11-02T17:50:46Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / coverage",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:23Z",
+     "completed_at": "2026-11-02T17:58:55Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / typing",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:24Z",
+     "completed_at": "2026-11-02T17:31:56Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / browser",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:23Z",
+     "completed_at": "2026-11-02T17:34:47Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "arch-score",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:21Z",
+     "completed_at": "2026-11-02T17:30:20Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "kernel-points",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:21Z",
+     "completed_at": "2026-11-02T17:30:20Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / closure-scope",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:21Z",
+     "completed_at": "2026-11-02T17:30:20Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "budget-raise-gate",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:21Z",
+     "completed_at": "2026-11-02T17:30:20Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-ha",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:21Z",
+     "completed_at": "2026-11-02T17:30:21Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / replay",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:21Z",
+     "completed_at": "2026-11-02T17:30:21Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / delivery-status",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:21Z",
+     "completed_at": "2026-11-02T17:30:20Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-status",
+     "created_at": "2026-11-02T17:30:21Z",
+     "started_at": "2026-11-02T17:30:21Z",
+     "completed_at": "2026-11-02T17:30:21Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-pins",
+     "created_at": "2026-11-02T17:31:37Z",
+     "started_at": "2026-11-02T17:31:37Z",
+     "completed_at": "2026-11-02T17:31:37Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-autofix",
+     "created_at": "2026-11-02T17:31:37Z",
+     "started_at": "2026-11-02T17:31:37Z",
+     "completed_at": "2026-11-02T17:31:37Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / claims-autofix",
+     "created_at": "2026-11-02T17:50:47Z",
+     "started_at": "2026-11-02T17:50:47Z",
+     "completed_at": "2026-11-02T17:50:47Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / coverage-ratchet",
+     "created_at": "2026-11-02T17:58:55Z",
+     "started_at": "2026-11-02T17:58:58Z",
+     "completed_at": "2026-11-02T17:59:59Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / graders-head-copy",
+     "created_at": "2026-11-02T17:58:55Z",
+     "started_at": "2026-11-02T17:58:55Z",
+     "completed_at": "2026-11-02T17:58:55Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / lane-proofs",
+     "created_at": "2026-11-02T18:03:09Z",
+     "started_at": "2026-11-02T18:03:09Z",
+     "completed_at": "2026-11-02T18:03:09Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / ci-ratchet",
+     "created_at": "2026-11-02T18:04:24Z",
+     "started_at": "2026-11-02T18:04:28Z",
+     "completed_at": "2026-11-02T18:06:17Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "tests / closures-autofix",
+     "created_at": "2026-11-02T18:04:25Z",
+     "started_at": "2026-11-02T18:04:25Z",
+     "completed_at": "2026-11-02T18:04:24Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "gate",
+     "created_at": "2026-11-02T18:06:17Z",
+     "started_at": "2026-11-02T18:06:20Z",
+     "completed_at": "2026-11-02T18:06:48Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "pr-contract",
+     "created_at": "2026-11-02T18:06:17Z",
+     "started_at": "2026-11-02T18:06:17Z",
+     "completed_at": "2026-11-02T18:06:17Z",
+     "conclusion": "skipped"
+    }
+   ]
+  },
+  {
+   "id": 41498469873,
+   "run_number": 4015,
+   "head_sha": "38dcb6c5dbade5206f2fae885334483082f36d10",
+   "created_at": "2026-11-02T18:13:14Z",
+   "status": "completed",
+   "conclusion": "failure",
+   "path": ".github/workflows/ci.yml",
+   "event": "push",
+   "head_branch": "main",
+   "jobs": [
+    {
+     "name": "prelude",
+     "created_at": "2026-11-02T18:13:15Z",
+     "started_at": "2026-11-02T18:13:18Z",
+     "completed_at": "2026-11-02T18:13:52Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "refresh",
+     "created_at": "2026-11-02T18:13:15Z",
+     "started_at": "2026-11-02T18:13:15Z",
+     "completed_at": "2026-11-02T18:13:15Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "cancel-superseded",
+     "created_at": "2026-11-02T18:13:15Z",
+     "started_at": "2026-11-02T18:13:15Z",
+     "completed_at": "2026-11-02T18:13:15Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "hassfest / hassfest",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:13:55Z",
+     "completed_at": "2026-11-02T18:14:15Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / briefs",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:13:55Z",
+     "completed_at": "2026-11-02T18:14:29Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / wave-script",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:13:59Z",
+     "completed_at": "2026-11-02T18:14:45Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "validate / validate-hacs",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:13:55Z",
+     "completed_at": "2026-11-02T18:14:32Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / mutation",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:14:05Z",
+     "completed_at": "2026-11-02T18:15:08Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / env-matrix",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:13:55Z",
+     "completed_at": "2026-11-02T18:20:49Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (actions)",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:13:55Z",
+     "completed_at": "2026-11-02T18:14:49Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / policy-docs",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:13:56Z",
+     "completed_at": "2026-11-02T18:17:51Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / instrument-self-tests",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:13:55Z",
+     "completed_at": "2026-11-02T18:39:37Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (javascript-typescript)",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:14:00Z",
+     "completed_at": "2026-11-02T18:15:46Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (python)",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:13:55Z",
+     "completed_at": "2026-11-02T18:55:06Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / record",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:14:02Z",
+     "completed_at": "2026-11-02T18:14:40Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / delivery-status-publish",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:14:03Z",
+     "completed_at": "2026-11-02T18:14:32Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / arch-instrument",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:13:55Z",
+     "completed_at": "2026-11-02T18:45:43Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / typing",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:13:56Z",
+     "completed_at": "2026-11-02T18:15:24Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / closures",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:14:00Z",
+     "completed_at": "2026-11-02T18:53:01Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / browser",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:13:58Z",
+     "completed_at": "2026-11-02T18:17:45Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / fast (3.14)",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:13:55Z",
+     "completed_at": "2026-11-02T18:47:54Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / coverage",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:13:55Z",
+     "completed_at": "2026-11-02T18:25:51Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "kernel-points",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:13:52Z",
+     "completed_at": "2026-11-02T18:13:52Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "budget-raise-gate",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:13:52Z",
+     "completed_at": "2026-11-02T18:13:52Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / delivery-status",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:13:52Z",
+     "completed_at": "2026-11-02T18:13:52Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / closure-scope",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:13:52Z",
+     "completed_at": "2026-11-02T18:13:52Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "arch-score",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:13:52Z",
+     "completed_at": "2026-11-02T18:13:52Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-status",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:13:52Z",
+     "completed_at": "2026-11-02T18:13:52Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-ha",
+     "created_at": "2026-11-02T18:13:52Z",
+     "started_at": "2026-11-02T18:13:52Z",
+     "completed_at": "2026-11-02T18:13:52Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / replay",
+     "created_at": "2026-11-02T18:13:53Z",
+     "started_at": "2026-11-02T18:13:53Z",
+     "completed_at": "2026-11-02T18:13:52Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-pins",
+     "created_at": "2026-11-02T18:15:09Z",
+     "started_at": "2026-11-02T18:15:09Z",
+     "completed_at": "2026-11-02T18:15:09Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-autofix",
+     "created_at": "2026-11-02T18:15:09Z",
+     "started_at": "2026-11-02T18:15:09Z",
+     "completed_at": "2026-11-02T18:15:09Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / coverage-ratchet",
+     "created_at": "2026-11-02T18:25:52Z",
+     "started_at": "2026-11-02T18:25:54Z",
+     "completed_at": "2026-11-02T18:26:13Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / graders-head-copy",
+     "created_at": "2026-11-02T18:25:52Z",
+     "started_at": "2026-11-02T18:25:52Z",
+     "completed_at": "2026-11-02T18:25:51Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / claims-autofix",
+     "created_at": "2026-11-02T18:47:55Z",
+     "started_at": "2026-11-02T18:47:55Z",
+     "completed_at": "2026-11-02T18:47:55Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / lane-proofs",
+     "created_at": "2026-11-02T18:47:55Z",
+     "started_at": "2026-11-02T18:47:55Z",
+     "completed_at": "2026-11-02T18:47:55Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / ci-ratchet",
+     "created_at": "2026-11-02T18:53:02Z",
+     "started_at": "2026-11-02T18:53:05Z",
+     "completed_at": "2026-11-02T18:54:19Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "tests / closures-autofix",
+     "created_at": "2026-11-02T18:53:02Z",
+     "started_at": "2026-11-02T18:53:02Z",
+     "completed_at": "2026-11-02T18:53:02Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "gate",
+     "created_at": "2026-11-02T18:55:07Z",
+     "started_at": "2026-11-02T18:55:09Z",
+     "completed_at": "2026-11-02T18:55:37Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "pr-contract",
+     "created_at": "2026-11-02T18:55:07Z",
+     "started_at": "2026-11-02T18:55:07Z",
+     "completed_at": "2026-11-02T18:55:06Z",
+     "conclusion": "skipped"
+    }
+   ]
+  },
+  {
+   "id": 41506687984,
+   "run_number": 4028,
+   "head_sha": "871a20da138592ac892f4652a4f82992a6626783",
+   "created_at": "2026-11-02T19:05:34Z",
+   "status": "completed",
+   "conclusion": "failure",
+   "path": ".github/workflows/ci.yml",
+   "event": "push",
+   "head_branch": "main",
+   "jobs": [
+    {
+     "name": "prelude",
+     "created_at": "2026-11-02T19:05:35Z",
+     "started_at": "2026-11-02T19:05:38Z",
+     "completed_at": "2026-11-02T19:06:09Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "refresh",
+     "created_at": "2026-11-02T19:05:35Z",
+     "started_at": "2026-11-02T19:05:35Z",
+     "completed_at": "2026-11-02T19:05:35Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "cancel-superseded",
+     "created_at": "2026-11-02T19:05:35Z",
+     "started_at": "2026-11-02T19:05:35Z",
+     "completed_at": "2026-11-02T19:05:35Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "validate / validate-hacs",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:13Z",
+     "completed_at": "2026-11-02T19:07:01Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / briefs",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:12Z",
+     "completed_at": "2026-11-02T19:06:52Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (actions)",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:13Z",
+     "completed_at": "2026-11-02T19:06:54Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / mutation",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:14Z",
+     "completed_at": "2026-11-02T19:07:05Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (python)",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:14Z",
+     "completed_at": "2026-11-02T19:41:35Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "budget-raise-gate",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:10Z",
+     "completed_at": "2026-11-02T19:06:09Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / instrument-self-tests",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:13Z",
+     "completed_at": "2026-11-02T19:30:28Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (javascript-typescript)",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:13Z",
+     "completed_at": "2026-11-02T19:08:04Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / env-matrix",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:20Z",
+     "completed_at": "2026-11-02T19:13:35Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "arch-score",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:10Z",
+     "completed_at": "2026-11-02T19:06:09Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "hassfest / hassfest",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:16Z",
+     "completed_at": "2026-11-02T19:06:40Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / policy-docs",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:27Z",
+     "completed_at": "2026-11-02T19:09:04Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / wave-script",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:14Z",
+     "completed_at": "2026-11-02T19:07:08Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "kernel-points",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:10Z",
+     "completed_at": "2026-11-02T19:06:09Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / closure-scope",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:10Z",
+     "completed_at": "2026-11-02T19:06:09Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / record",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:13Z",
+     "completed_at": "2026-11-02T19:07:18Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / delivery-status-publish",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:12Z",
+     "completed_at": "2026-11-02T19:08:37Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / nightly-status",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:10Z",
+     "completed_at": "2026-11-02T19:06:09Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / delivery-status",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:10Z",
+     "completed_at": "2026-11-02T19:06:10Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / fast (3.14)",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:13Z",
+     "completed_at": "2026-11-02T19:41:07Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / arch-instrument",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:13Z",
+     "completed_at": "2026-11-02T19:31:46Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / typing",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:13Z",
+     "completed_at": "2026-11-02T19:07:54Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / browser",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:16Z",
+     "completed_at": "2026-11-02T19:10:23Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / coverage",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:13Z",
+     "completed_at": "2026-11-02T19:26:39Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / closures",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:13Z",
+     "completed_at": "2026-11-02T19:24:50Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / replay",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:10Z",
+     "completed_at": "2026-11-02T19:06:10Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-ha",
+     "created_at": "2026-11-02T19:06:10Z",
+     "started_at": "2026-11-02T19:06:10Z",
+     "completed_at": "2026-11-02T19:06:10Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-pins",
+     "created_at": "2026-11-02T19:07:05Z",
+     "started_at": "2026-11-02T19:07:05Z",
+     "completed_at": "2026-11-02T19:07:05Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-autofix",
+     "created_at": "2026-11-02T19:07:05Z",
+     "started_at": "2026-11-02T19:07:05Z",
+     "completed_at": "2026-11-02T19:07:05Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / closures-autofix",
+     "created_at": "2026-11-02T19:24:51Z",
+     "started_at": "2026-11-02T19:24:51Z",
+     "completed_at": "2026-11-02T19:24:51Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / coverage-ratchet",
+     "created_at": "2026-11-02T19:26:39Z",
+     "started_at": "2026-11-02T19:26:42Z",
+     "completed_at": "2026-11-02T19:26:57Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / graders-head-copy",
+     "created_at": "2026-11-02T19:26:40Z",
+     "started_at": "2026-11-02T19:26:40Z",
+     "completed_at": "2026-11-02T19:26:39Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / ci-ratchet",
+     "created_at": "2026-11-02T19:41:07Z",
+     "started_at": "2026-11-02T19:41:10Z",
+     "completed_at": "2026-11-02T19:42:22Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "tests / lane-proofs",
+     "created_at": "2026-11-02T19:41:07Z",
+     "started_at": "2026-11-02T19:41:07Z",
+     "completed_at": "2026-11-02T19:41:07Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / claims-autofix",
+     "created_at": "2026-11-02T19:41:07Z",
+     "started_at": "2026-11-02T19:41:07Z",
+     "completed_at": "2026-11-02T19:41:07Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "gate",
+     "created_at": "2026-11-02T19:42:23Z",
+     "started_at": "2026-11-02T19:42:26Z",
+     "completed_at": "2026-11-02T19:44:23Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "pr-contract",
+     "created_at": "2026-11-02T19:42:23Z",
+     "started_at": "2026-11-02T19:42:23Z",
+     "completed_at": "2026-11-02T19:42:23Z",
+     "conclusion": "skipped"
+    }
+   ]
+  },
+  {
+   "id": 41513327647,
+   "run_number": 4035,
+   "head_sha": "d15a2d7df189cf48a24abd8d62e032696652549c",
+   "created_at": "2026-11-02T19:48:18Z",
+   "status": "completed",
+   "conclusion": "failure",
+   "path": ".github/workflows/ci.yml",
+   "event": "push",
+   "head_branch": "main",
+   "jobs": [
+    {
+     "name": "prelude",
+     "created_at": "2026-11-02T19:48:19Z",
+     "started_at": "2026-11-02T19:48:21Z",
+     "completed_at": "2026-11-02T19:48:46Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "refresh",
+     "created_at": "2026-11-02T19:48:19Z",
+     "started_at": "2026-11-02T19:48:19Z",
+     "completed_at": "2026-11-02T19:48:19Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "cancel-superseded",
+     "created_at": "2026-11-02T19:48:19Z",
+     "started_at": "2026-11-02T19:48:19Z",
+     "completed_at": "2026-11-02T19:48:19Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:49Z",
+     "completed_at": "2026-11-02T19:49:30Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / briefs",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:50Z",
+     "completed_at": "2026-11-02T19:49:45Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / instrument-self-tests",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:49Z",
+     "completed_at": "2026-11-02T20:17:12Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "hassfest / hassfest",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:50Z",
+     "completed_at": "2026-11-02T19:49:12Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "validate / validate-hacs",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:50Z",
+     "completed_at": "2026-11-02T19:49:33Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / env-matrix",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:49Z",
+     "completed_at": "2026-11-02T19:55:32Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / policy-docs",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:51Z",
+     "completed_at": "2026-11-02T19:49:41Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (actions)",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:50Z",
+     "completed_at": "2026-11-02T19:49:51Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (javascript-typescript)",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:50Z",
+     "completed_at": "2026-11-02T19:50:06Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (python)",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:50Z",
+     "completed_at": "2026-11-02T20:20:39Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / wave-script",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:50Z",
+     "completed_at": "2026-11-02T19:49:36Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / record",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:50Z",
+     "completed_at": "2026-11-02T19:49:38Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / delivery-status-publish",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:49Z",
+     "completed_at": "2026-11-02T19:49:14Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / coverage",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:50Z",
+     "completed_at": "2026-11-02T19:50:38Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "arch-score",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:47Z",
+     "completed_at": "2026-11-02T19:48:46Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / closures",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:50Z",
+     "completed_at": "2026-11-02T20:28:31Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "budget-raise-gate",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:47Z",
+     "completed_at": "2026-11-02T19:48:46Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / browser",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:50Z",
+     "completed_at": "2026-11-02T19:53:06Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / typing",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:50Z",
+     "completed_at": "2026-11-02T19:50:21Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / arch-instrument",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:50Z",
+     "completed_at": "2026-11-02T20:21:05Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / fast (3.14)",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:50Z",
+     "completed_at": "2026-11-02T20:16:10Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / nightly-status",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:47Z",
+     "completed_at": "2026-11-02T19:48:46Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "kernel-points",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:47Z",
+     "completed_at": "2026-11-02T19:48:46Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / delivery-status",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:47Z",
+     "completed_at": "2026-11-02T19:48:46Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / closure-scope",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:47Z",
+     "completed_at": "2026-11-02T19:48:46Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-ha",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:47Z",
+     "completed_at": "2026-11-02T19:48:47Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / replay",
+     "created_at": "2026-11-02T19:48:47Z",
+     "started_at": "2026-11-02T19:48:47Z",
+     "completed_at": "2026-11-02T19:48:47Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-pins",
+     "created_at": "2026-11-02T19:49:30Z",
+     "started_at": "2026-11-02T19:49:30Z",
+     "completed_at": "2026-11-02T19:49:30Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-autofix",
+     "created_at": "2026-11-02T19:49:30Z",
+     "started_at": "2026-11-02T19:49:30Z",
+     "completed_at": "2026-11-02T19:49:30Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / coverage-ratchet",
+     "created_at": "2026-11-02T19:50:38Z",
+     "started_at": "2026-11-02T19:55:51Z",
+     "completed_at": "2026-11-02T19:56:03Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / graders-head-copy",
+     "created_at": "2026-11-02T19:50:38Z",
+     "started_at": "2026-11-02T19:50:38Z",
+     "completed_at": "2026-11-02T19:50:38Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / claims-autofix",
+     "created_at": "2026-11-02T20:16:11Z",
+     "started_at": "2026-11-02T20:16:11Z",
+     "completed_at": "2026-11-02T20:16:11Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / lane-proofs",
+     "created_at": "2026-11-02T20:21:05Z",
+     "started_at": "2026-11-02T20:21:05Z",
+     "completed_at": "2026-11-02T20:21:05Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / ci-ratchet",
+     "created_at": "2026-11-02T20:28:31Z",
+     "started_at": "2026-11-02T20:28:34Z",
+     "completed_at": "2026-11-02T20:29:45Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "tests / closures-autofix",
+     "created_at": "2026-11-02T20:28:31Z",
+     "started_at": "2026-11-02T20:28:31Z",
+     "completed_at": "2026-11-02T20:28:31Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "gate",
+     "created_at": "2026-11-02T20:29:45Z",
+     "started_at": "2026-11-02T20:29:48Z",
+     "completed_at": "2026-11-02T20:30:12Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "pr-contract",
+     "created_at": "2026-11-02T20:29:45Z",
+     "started_at": "2026-11-02T20:29:45Z",
+     "completed_at": "2026-11-02T20:29:45Z",
+     "conclusion": "skipped"
+    }
+   ]
+  },
+  {
+   "id": 41513400917,
+   "run_number": 4036,
+   "head_sha": "59b7c077152c79e4e328b065d7516a9badb55292",
+   "created_at": "2026-11-02T19:48:47Z",
+   "status": "completed",
+   "conclusion": "cancelled",
+   "path": ".github/workflows/ci.yml",
+   "event": "push",
+   "head_branch": "main",
+   "jobs": [
+    {
+     "name": "prelude",
+     "created_at": "2026-11-02T19:48:48Z",
+     "started_at": "2026-11-02T19:48:51Z",
+     "completed_at": "2026-11-02T19:49:19Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "refresh",
+     "created_at": "2026-11-02T19:48:48Z",
+     "started_at": "2026-11-02T19:48:48Z",
+     "completed_at": "2026-11-02T19:48:48Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "cancel-superseded",
+     "created_at": "2026-11-02T19:48:48Z",
+     "started_at": "2026-11-02T19:48:48Z",
+     "completed_at": "2026-11-02T19:48:48Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "hassfest / hassfest",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:22Z",
+     "completed_at": "2026-11-02T19:49:43Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (actions)",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:22Z",
+     "completed_at": "2026-11-02T19:50:10Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / env-matrix",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:22Z",
+     "completed_at": "2026-11-02T19:53:41Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / briefs",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:22Z",
+     "completed_at": "2026-11-02T19:50:07Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / wave-script",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:22Z",
+     "completed_at": "2026-11-02T19:50:07Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (javascript-typescript)",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:23Z",
+     "completed_at": "2026-11-02T19:50:51Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (python)",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:22Z",
+     "completed_at": "2026-11-02T20:29:33Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / mutation",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:23Z",
+     "completed_at": "2026-11-02T19:50:00Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / policy-docs",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:22Z",
+     "completed_at": "2026-11-02T19:50:36Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "validate / validate-hacs",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:22Z",
+     "completed_at": "2026-11-02T19:49:58Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / instrument-self-tests",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:23Z",
+     "completed_at": "2026-11-02T20:14:42Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / delivery-status-publish",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:23Z",
+     "completed_at": "2026-11-02T19:49:54Z",
+     "conclusion": "cancelled"
+    },
+    {
+     "name": "tests / typing",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:25Z",
+     "completed_at": "2026-11-02T19:50:30Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / browser",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:22Z",
+     "completed_at": "2026-11-02T19:53:43Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / arch-instrument",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:23Z",
+     "completed_at": "2026-11-02T20:21:08Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / closures",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:22Z",
+     "completed_at": "2026-11-02T20:28:18Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "arch-score",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:19Z",
+     "completed_at": "2026-11-02T19:49:19Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / coverage",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:27Z",
+     "completed_at": "2026-11-02T19:50:17Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / fast (3.14)",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:24Z",
+     "completed_at": "2026-11-02T20:22:25Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / record",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:41Z",
+     "completed_at": "2026-11-02T19:50:28Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "budget-raise-gate",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:19Z",
+     "completed_at": "2026-11-02T19:49:19Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / delivery-status",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:19Z",
+     "completed_at": "2026-11-02T19:49:19Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / closure-scope",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:19Z",
+     "completed_at": "2026-11-02T19:49:19Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "kernel-points",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:19Z",
+     "completed_at": "2026-11-02T19:49:19Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-status",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:19Z",
+     "completed_at": "2026-11-02T19:49:19Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-ha",
+     "created_at": "2026-11-02T19:49:19Z",
+     "started_at": "2026-11-02T19:49:19Z",
+     "completed_at": "2026-11-02T19:49:19Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / replay",
+     "created_at": "2026-11-02T19:49:20Z",
+     "started_at": "2026-11-02T19:49:20Z",
+     "completed_at": "2026-11-02T19:49:19Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-pins",
+     "created_at": "2026-11-02T19:50:01Z",
+     "started_at": "2026-11-02T19:50:01Z",
+     "completed_at": "2026-11-02T19:50:01Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-autofix",
+     "created_at": "2026-11-02T19:50:01Z",
+     "started_at": "2026-11-02T19:50:01Z",
+     "completed_at": "2026-11-02T19:50:01Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / coverage-ratchet",
+     "created_at": "2026-11-02T19:50:18Z",
+     "started_at": "2026-11-02T19:55:48Z",
+     "completed_at": "2026-11-02T19:55:58Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / graders-head-copy",
+     "created_at": "2026-11-02T19:50:18Z",
+     "started_at": "2026-11-02T19:50:18Z",
+     "completed_at": "2026-11-02T19:50:18Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / lane-proofs",
+     "created_at": "2026-11-02T20:22:26Z",
+     "started_at": "2026-11-02T20:22:26Z",
+     "completed_at": "2026-11-02T20:22:26Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / claims-autofix",
+     "created_at": "2026-11-02T20:22:26Z",
+     "started_at": "2026-11-02T20:22:26Z",
+     "completed_at": "2026-11-02T20:22:26Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / ci-ratchet",
+     "created_at": "2026-11-02T20:28:19Z",
+     "started_at": "2026-11-02T20:28:21Z",
+     "completed_at": "2026-11-02T20:29:27Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "tests / closures-autofix",
+     "created_at": "2026-11-02T20:28:19Z",
+     "started_at": "2026-11-02T20:28:19Z",
+     "completed_at": "2026-11-02T20:28:18Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "gate",
+     "created_at": "2026-11-02T20:29:33Z",
+     "started_at": "2026-11-02T20:29:36Z",
+     "completed_at": "2026-11-02T20:30:03Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "pr-contract",
+     "created_at": "2026-11-02T20:29:33Z",
+     "started_at": "2026-11-02T20:29:33Z",
+     "completed_at": "2026-11-02T20:29:33Z",
+     "conclusion": "skipped"
+    }
+   ]
+  },
+  {
+   "id": 41513472149,
+   "run_number": 4037,
+   "head_sha": "489d93fa7441768b2e6d5fb5fd4731d8da39f4ea",
+   "created_at": "2026-11-02T19:49:15Z",
+   "status": "completed",
+   "conclusion": "cancelled",
+   "path": ".github/workflows/ci.yml",
+   "event": "push",
+   "head_branch": "main",
+   "jobs": [
+    {
+     "name": "prelude",
+     "created_at": "2026-11-02T19:49:16Z",
+     "started_at": "2026-11-02T19:49:19Z",
+     "completed_at": "2026-11-02T19:49:47Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "cancel-superseded",
+     "created_at": "2026-11-02T19:49:16Z",
+     "started_at": "2026-11-02T19:49:16Z",
+     "completed_at": "2026-11-02T19:49:16Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "refresh",
+     "created_at": "2026-11-02T19:49:16Z",
+     "started_at": "2026-11-02T19:49:16Z",
+     "completed_at": "2026-11-02T19:49:16Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "validate / validate-hacs",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:49:50Z",
+     "completed_at": "2026-11-02T19:50:27Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / briefs",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:49:50Z",
+     "completed_at": "2026-11-02T19:50:42Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (actions)",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:49:50Z",
+     "completed_at": "2026-11-02T19:50:44Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / env-matrix",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:49:50Z",
+     "completed_at": "2026-11-02T19:56:39Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "hassfest / hassfest",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:49:49Z",
+     "completed_at": "2026-11-02T19:50:08Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (javascript-typescript)",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:49:50Z",
+     "completed_at": "2026-11-02T19:51:34Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / policy-docs",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:49:50Z",
+     "completed_at": "2026-11-02T19:51:02Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / wave-script",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:50:01Z",
+     "completed_at": "2026-11-02T19:50:45Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (python)",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:49:54Z",
+     "completed_at": "2026-11-02T20:28:23Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / mutation",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:49:57Z",
+     "completed_at": "2026-11-02T19:50:37Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / instrument-self-tests",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:50:03Z",
+     "completed_at": "2026-11-02T20:15:34Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / arch-instrument",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:50:08Z",
+     "completed_at": "2026-11-02T20:06:58Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / record",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:49:47Z",
+     "completed_at": "2026-11-02T19:50:11Z",
+     "conclusion": "cancelled"
+    },
+    {
+     "name": "kernel-points",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:49:47Z",
+     "completed_at": "2026-11-02T19:49:47Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / fast (3.14)",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:50:09Z",
+     "completed_at": "2026-11-02T20:22:48Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / browser",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:50:12Z",
+     "completed_at": "2026-11-02T19:54:29Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / coverage",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:50:17Z",
+     "completed_at": "2026-11-02T19:51:07Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "arch-score",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:49:47Z",
+     "completed_at": "2026-11-02T19:49:47Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / typing",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:50:17Z",
+     "completed_at": "2026-11-02T19:51:37Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / closures",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:50:37Z",
+     "completed_at": "2026-11-02T20:29:42Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / delivery-status-publish",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:50:10Z",
+     "completed_at": "2026-11-02T19:50:34Z",
+     "conclusion": "cancelled"
+    },
+    {
+     "name": "budget-raise-gate",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:49:47Z",
+     "completed_at": "2026-11-02T19:49:47Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / delivery-status",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:49:47Z",
+     "completed_at": "2026-11-02T19:49:47Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / replay",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:49:47Z",
+     "completed_at": "2026-11-02T19:49:47Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-status",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:49:47Z",
+     "completed_at": "2026-11-02T19:49:47Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / closure-scope",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:49:47Z",
+     "completed_at": "2026-11-02T19:49:47Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-ha",
+     "created_at": "2026-11-02T19:49:47Z",
+     "started_at": "2026-11-02T19:49:47Z",
+     "completed_at": "2026-11-02T19:49:47Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-pins",
+     "created_at": "2026-11-02T19:50:37Z",
+     "started_at": "2026-11-02T19:50:37Z",
+     "completed_at": "2026-11-02T19:50:37Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-autofix",
+     "created_at": "2026-11-02T19:50:37Z",
+     "started_at": "2026-11-02T19:50:37Z",
+     "completed_at": "2026-11-02T19:50:37Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / coverage-ratchet",
+     "created_at": "2026-11-02T19:51:07Z",
+     "started_at": "2026-11-02T20:03:08Z",
+     "completed_at": "2026-11-02T20:03:18Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / graders-head-copy",
+     "created_at": "2026-11-02T19:51:07Z",
+     "started_at": "2026-11-02T19:51:07Z",
+     "completed_at": "2026-11-02T19:51:07Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / claims-autofix",
+     "created_at": "2026-11-02T20:22:48Z",
+     "started_at": "2026-11-02T20:22:48Z",
+     "completed_at": "2026-11-02T20:22:48Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / lane-proofs",
+     "created_at": "2026-11-02T20:22:48Z",
+     "started_at": "2026-11-02T20:22:48Z",
+     "completed_at": "2026-11-02T20:22:48Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / ci-ratchet",
+     "created_at": "2026-11-02T20:29:42Z",
+     "started_at": "2026-11-02T20:29:45Z",
+     "completed_at": "2026-11-02T20:31:01Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "tests / closures-autofix",
+     "created_at": "2026-11-02T20:29:42Z",
+     "started_at": "2026-11-02T20:29:42Z",
+     "completed_at": "2026-11-02T20:29:42Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "gate",
+     "created_at": "2026-11-02T20:31:02Z",
+     "started_at": "2026-11-02T20:31:05Z",
+     "completed_at": "2026-11-02T20:31:29Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "pr-contract",
+     "created_at": "2026-11-02T20:31:02Z",
+     "started_at": "2026-11-02T20:31:02Z",
+     "completed_at": "2026-11-02T20:31:01Z",
+     "conclusion": "skipped"
+    }
+   ]
+  },
+  {
+   "id": 41513537435,
+   "run_number": 4038,
+   "head_sha": "7a92dcec703fd4d8f873fbfb5fd558ce68a2f23e",
+   "created_at": "2026-11-02T19:49:40Z",
+   "status": "completed",
+   "conclusion": "cancelled",
+   "path": ".github/workflows/ci.yml",
+   "event": "push",
+   "head_branch": "main",
+   "jobs": [
+    {
+     "name": "prelude",
+     "created_at": "2026-11-02T19:49:41Z",
+     "started_at": "2026-11-02T19:49:47Z",
+     "completed_at": "2026-11-02T19:50:10Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "cancel-superseded",
+     "created_at": "2026-11-02T19:49:41Z",
+     "started_at": "2026-11-02T19:49:41Z",
+     "completed_at": "2026-11-02T19:49:41Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "refresh",
+     "created_at": "2026-11-02T19:49:42Z",
+     "started_at": "2026-11-02T19:49:42Z",
+     "completed_at": "2026-11-02T19:49:41Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "codeql / Analyze (python)",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:50:39Z",
+     "completed_at": "2026-11-02T20:29:36Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (actions)",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:50:36Z",
+     "completed_at": "2026-11-02T19:51:31Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / env-matrix",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:50:13Z",
+     "completed_at": "2026-11-02T19:55:28Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / wave-script",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:50:30Z",
+     "completed_at": "2026-11-02T19:51:15Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (javascript-typescript)",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:51:10Z",
+     "completed_at": "2026-11-02T19:53:01Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / policy-docs",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:50:41Z",
+     "completed_at": "2026-11-02T19:51:54Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "hassfest / hassfest",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:50:24Z",
+     "completed_at": "2026-11-02T19:50:47Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / instrument-self-tests",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:50:46Z",
+     "completed_at": "2026-11-02T20:14:23Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / briefs",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:50:45Z",
+     "completed_at": "2026-11-02T19:51:44Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "validate / validate-hacs",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:50:30Z",
+     "completed_at": "2026-11-02T19:51:09Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / mutation",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:51:57Z",
+     "completed_at": "2026-11-02T19:52:43Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / arch-instrument",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:53:44Z",
+     "completed_at": "2026-11-02T20:22:59Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / browser",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:51:18Z",
+     "completed_at": "2026-11-02T19:55:02Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / typing",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:52:15Z",
+     "completed_at": "2026-11-02T19:53:45Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / coverage",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:52:16Z",
+     "completed_at": "2026-11-02T19:53:03Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / fast (3.14)",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:53:49Z",
+     "completed_at": "2026-11-02T20:24:00Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / closures",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:52:22Z",
+     "completed_at": "2026-11-02T20:19:15Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / delivery-status-publish",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:50:49Z",
+     "completed_at": "2026-11-02T19:51:21Z",
+     "conclusion": "cancelled"
+    },
+    {
+     "name": "kernel-points",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:50:10Z",
+     "completed_at": "2026-11-02T19:50:10Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / record",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:50:49Z",
+     "completed_at": "2026-11-02T19:51:33Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "arch-score",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:50:10Z",
+     "completed_at": "2026-11-02T19:50:10Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "budget-raise-gate",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:50:10Z",
+     "completed_at": "2026-11-02T19:50:10Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / delivery-status",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:50:10Z",
+     "completed_at": "2026-11-02T19:50:10Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / closure-scope",
+     "created_at": "2026-11-02T19:50:10Z",
+     "started_at": "2026-11-02T19:50:10Z",
+     "completed_at": "2026-11-02T19:50:10Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-status",
+     "created_at": "2026-11-02T19:50:11Z",
+     "started_at": "2026-11-02T19:50:11Z",
+     "completed_at": "2026-11-02T19:50:10Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / replay",
+     "created_at": "2026-11-02T19:50:11Z",
+     "started_at": "2026-11-02T19:50:11Z",
+     "completed_at": "2026-11-02T19:50:10Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-ha",
+     "created_at": "2026-11-02T19:50:11Z",
+     "started_at": "2026-11-02T19:50:11Z",
+     "completed_at": "2026-11-02T19:50:10Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-pins",
+     "created_at": "2026-11-02T19:52:44Z",
+     "started_at": "2026-11-02T19:52:44Z",
+     "completed_at": "2026-11-02T19:52:44Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-autofix",
+     "created_at": "2026-11-02T19:52:44Z",
+     "started_at": "2026-11-02T19:52:44Z",
+     "completed_at": "2026-11-02T19:52:44Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / coverage-ratchet",
+     "created_at": "2026-11-02T19:53:04Z",
+     "started_at": "2026-11-02T20:16:36Z",
+     "completed_at": "2026-11-02T20:16:49Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / graders-head-copy",
+     "created_at": "2026-11-02T19:53:04Z",
+     "started_at": "2026-11-02T19:53:04Z",
+     "completed_at": "2026-11-02T19:53:04Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / closures-autofix",
+     "created_at": "2026-11-02T20:19:16Z",
+     "started_at": "2026-11-02T20:19:16Z",
+     "completed_at": "2026-11-02T20:19:16Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / ci-ratchet",
+     "created_at": "2026-11-02T20:24:01Z",
+     "started_at": "2026-11-02T20:25:38Z",
+     "completed_at": "2026-11-02T20:26:42Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "tests / claims-autofix",
+     "created_at": "2026-11-02T20:24:01Z",
+     "started_at": "2026-11-02T20:24:01Z",
+     "completed_at": "2026-11-02T20:24:00Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / lane-proofs",
+     "created_at": "2026-11-02T20:24:01Z",
+     "started_at": "2026-11-02T20:24:01Z",
+     "completed_at": "2026-11-02T20:24:00Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "gate",
+     "created_at": "2026-11-02T20:29:37Z",
+     "started_at": "2026-11-02T20:29:40Z",
+     "completed_at": "2026-11-02T20:30:09Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "pr-contract",
+     "created_at": "2026-11-02T20:29:37Z",
+     "started_at": "2026-11-02T20:29:37Z",
+     "completed_at": "2026-11-02T20:29:36Z",
+     "conclusion": "skipped"
+    }
+   ]
+  },
+  {
+   "id": 41513617168,
+   "run_number": 4040,
+   "head_sha": "8b823e7f4be79373dd4255f78caa73cb83005e71",
+   "created_at": "2026-11-02T19:50:11Z",
+   "status": "completed",
+   "conclusion": "cancelled",
+   "path": ".github/workflows/ci.yml",
+   "event": "push",
+   "head_branch": "main",
+   "jobs": [
+    {
+     "name": "prelude",
+     "created_at": "2026-11-02T19:50:12Z",
+     "started_at": "2026-11-02T19:50:38Z",
+     "completed_at": "2026-11-02T19:51:04Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "cancel-superseded",
+     "created_at": "2026-11-02T19:50:12Z",
+     "started_at": "2026-11-02T19:50:12Z",
+     "completed_at": "2026-11-02T19:50:12Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "refresh",
+     "created_at": "2026-11-02T19:50:12Z",
+     "started_at": "2026-11-02T19:50:12Z",
+     "completed_at": "2026-11-02T19:50:12Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:55:52Z",
+     "completed_at": "2026-11-02T19:56:39Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "validate / validate-hacs",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:52:10Z",
+     "completed_at": "2026-11-02T19:52:52Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / env-matrix",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:53:06Z",
+     "completed_at": "2026-11-02T19:57:02Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / instrument-self-tests",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:53:06Z",
+     "completed_at": "2026-11-02T20:22:10Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / policy-docs",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:51:37Z",
+     "completed_at": "2026-11-02T19:52:23Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / briefs",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:56:04Z",
+     "completed_at": "2026-11-02T19:56:39Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (javascript-typescript)",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:51:17Z",
+     "completed_at": "2026-11-02T19:53:04Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (actions)",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:51:12Z",
+     "completed_at": "2026-11-02T19:52:06Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "hassfest / hassfest",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:52:55Z",
+     "completed_at": "2026-11-02T19:53:27Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (python)",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:51:24Z",
+     "completed_at": "2026-11-02T20:34:34Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / wave-script",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:53:31Z",
+     "completed_at": "2026-11-02T19:54:38Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / typing",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:56:02Z",
+     "completed_at": "2026-11-02T19:57:34Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / coverage",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:57:38Z",
+     "completed_at": "2026-11-02T19:58:22Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / browser",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:57:05Z",
+     "completed_at": "2026-11-02T20:01:27Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / closures",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:56:52Z",
+     "completed_at": "2026-11-02T20:17:37Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / arch-instrument",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:57:31Z",
+     "completed_at": "2026-11-02T20:27:57Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / fast (3.14)",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:58:04Z",
+     "completed_at": "2026-11-02T20:31:18Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / record",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:51:05Z",
+     "completed_at": "2026-11-02T19:51:17Z",
+     "conclusion": "cancelled"
+    },
+    {
+     "name": "governance / delivery-status-publish",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:51:05Z",
+     "completed_at": "2026-11-02T19:51:17Z",
+     "conclusion": "cancelled"
+    },
+    {
+     "name": "tests / nightly-status",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:51:05Z",
+     "completed_at": "2026-11-02T19:51:04Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "arch-score",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:51:05Z",
+     "completed_at": "2026-11-02T19:51:04Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "budget-raise-gate",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:51:05Z",
+     "completed_at": "2026-11-02T19:51:04Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "kernel-points",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:51:05Z",
+     "completed_at": "2026-11-02T19:51:04Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / delivery-status",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:51:05Z",
+     "completed_at": "2026-11-02T19:51:05Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / closure-scope",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:51:05Z",
+     "completed_at": "2026-11-02T19:51:05Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / replay",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:51:05Z",
+     "completed_at": "2026-11-02T19:51:05Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-ha",
+     "created_at": "2026-11-02T19:51:05Z",
+     "started_at": "2026-11-02T19:51:05Z",
+     "completed_at": "2026-11-02T19:51:05Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-pins",
+     "created_at": "2026-11-02T19:56:40Z",
+     "started_at": "2026-11-02T19:56:40Z",
+     "completed_at": "2026-11-02T19:56:39Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-autofix",
+     "created_at": "2026-11-02T19:56:40Z",
+     "started_at": "2026-11-02T19:56:40Z",
+     "completed_at": "2026-11-02T19:56:40Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / coverage-ratchet",
+     "created_at": "2026-11-02T19:58:22Z",
+     "started_at": "2026-11-02T20:20:20Z",
+     "completed_at": "2026-11-02T20:20:37Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / graders-head-copy",
+     "created_at": "2026-11-02T19:58:23Z",
+     "started_at": "2026-11-02T19:58:23Z",
+     "completed_at": "2026-11-02T19:58:22Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / closures-autofix",
+     "created_at": "2026-11-02T20:17:38Z",
+     "started_at": "2026-11-02T20:17:38Z",
+     "completed_at": "2026-11-02T20:17:37Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / ci-ratchet",
+     "created_at": "2026-11-02T20:31:19Z",
+     "started_at": "2026-11-02T20:31:22Z",
+     "completed_at": "2026-11-02T20:32:48Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "tests / lane-proofs",
+     "created_at": "2026-11-02T20:31:19Z",
+     "started_at": "2026-11-02T20:31:19Z",
+     "completed_at": "2026-11-02T20:31:19Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / claims-autofix",
+     "created_at": "2026-11-02T20:31:19Z",
+     "started_at": "2026-11-02T20:31:19Z",
+     "completed_at": "2026-11-02T20:31:19Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "gate",
+     "created_at": "2026-11-02T20:34:34Z",
+     "started_at": "2026-11-02T20:34:37Z",
+     "completed_at": "2026-11-02T20:35:11Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "pr-contract",
+     "created_at": "2026-11-02T20:34:34Z",
+     "started_at": "2026-11-02T20:34:34Z",
+     "completed_at": "2026-11-02T20:34:34Z",
+     "conclusion": "skipped"
+    }
+   ]
+  },
+  {
+   "id": 41513704131,
+   "run_number": 4044,
+   "head_sha": "1599dd264385149f514e16c5ed8bbcd48546b4c7",
+   "created_at": "2026-11-02T19:50:44Z",
+   "status": "completed",
+   "conclusion": "cancelled",
+   "path": ".github/workflows/ci.yml",
+   "event": "push",
+   "head_branch": "main",
+   "jobs": [
+    {
+     "name": "prelude",
+     "created_at": "2026-11-02T19:50:45Z",
+     "started_at": "2026-11-02T19:50:54Z",
+     "completed_at": "2026-11-02T19:51:16Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "refresh",
+     "created_at": "2026-11-02T19:50:46Z",
+     "started_at": "2026-11-02T19:50:46Z",
+     "completed_at": "2026-11-02T19:50:45Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "cancel-superseded",
+     "created_at": "2026-11-02T19:50:46Z",
+     "started_at": "2026-11-02T19:50:46Z",
+     "completed_at": "2026-11-02T19:50:45Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "codeql / Analyze (actions)",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T19:51:34Z",
+     "completed_at": "2026-11-02T19:52:19Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (python)",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T19:51:24Z",
+     "completed_at": "2026-11-02T20:24:26Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / instrument-self-tests",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T19:54:32Z",
+     "completed_at": "2026-11-02T20:20:55Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "validate / validate-hacs",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T19:52:12Z",
+     "completed_at": "2026-11-02T19:52:48Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (javascript-typescript)",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T19:51:36Z",
+     "completed_at": "2026-11-02T19:53:19Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / wave-script",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T19:54:03Z",
+     "completed_at": "2026-11-02T19:54:57Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "hassfest / hassfest",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T19:53:04Z",
+     "completed_at": "2026-11-02T19:54:31Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / mutation",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T20:03:46Z",
+     "completed_at": "2026-11-02T20:04:21Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / env-matrix",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T19:54:40Z",
+     "completed_at": "2026-11-02T20:00:50Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / briefs",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T20:05:08Z",
+     "completed_at": "2026-11-02T20:05:58Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / policy-docs",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T19:55:58Z",
+     "completed_at": "2026-11-02T19:57:55Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / coverage",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T20:05:09Z",
+     "completed_at": "2026-11-02T20:06:03Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / browser",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T20:06:25Z",
+     "completed_at": "2026-11-02T20:10:15Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / record",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T19:56:05Z",
+     "completed_at": "2026-11-02T19:56:50Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / closures",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T20:06:53Z",
+     "completed_at": "2026-11-02T20:46:09Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / arch-instrument",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T20:05:57Z",
+     "completed_at": "2026-11-02T20:38:05Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / fast (3.14)",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T19:52:16Z",
+     "completed_at": "2026-11-02T20:25:58Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / typing",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T20:06:00Z",
+     "completed_at": "2026-11-02T20:07:24Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / delivery-status-publish",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T19:51:16Z",
+     "completed_at": "2026-11-02T19:52:10Z",
+     "conclusion": "cancelled"
+    },
+    {
+     "name": "kernel-points",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T19:51:16Z",
+     "completed_at": "2026-11-02T19:51:16Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-status",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T19:51:16Z",
+     "completed_at": "2026-11-02T19:51:16Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / closure-scope",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T19:51:16Z",
+     "completed_at": "2026-11-02T19:51:16Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "budget-raise-gate",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T19:51:16Z",
+     "completed_at": "2026-11-02T19:51:16Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "arch-score",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T19:51:16Z",
+     "completed_at": "2026-11-02T19:51:16Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / delivery-status",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T19:51:16Z",
+     "completed_at": "2026-11-02T19:51:16Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-ha",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T19:51:16Z",
+     "completed_at": "2026-11-02T19:51:16Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / replay",
+     "created_at": "2026-11-02T19:51:16Z",
+     "started_at": "2026-11-02T19:51:16Z",
+     "completed_at": "2026-11-02T19:51:16Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-pins",
+     "created_at": "2026-11-02T20:04:21Z",
+     "started_at": "2026-11-02T20:04:21Z",
+     "completed_at": "2026-11-02T20:04:21Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-autofix",
+     "created_at": "2026-11-02T20:04:21Z",
+     "started_at": "2026-11-02T20:04:21Z",
+     "completed_at": "2026-11-02T20:04:21Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / coverage-ratchet",
+     "created_at": "2026-11-02T20:06:03Z",
+     "started_at": "2026-11-02T20:20:41Z",
+     "completed_at": "2026-11-02T20:20:50Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / graders-head-copy",
+     "created_at": "2026-11-02T20:06:03Z",
+     "started_at": "2026-11-02T20:06:03Z",
+     "completed_at": "2026-11-02T20:06:03Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / claims-autofix",
+     "created_at": "2026-11-02T20:25:58Z",
+     "started_at": "2026-11-02T20:25:58Z",
+     "completed_at": "2026-11-02T20:25:58Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / lane-proofs",
+     "created_at": "2026-11-02T20:38:06Z",
+     "started_at": "2026-11-02T20:38:06Z",
+     "completed_at": "2026-11-02T20:38:05Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / ci-ratchet",
+     "created_at": "2026-11-02T20:46:09Z",
+     "started_at": "2026-11-02T20:46:12Z",
+     "completed_at": "2026-11-02T20:47:53Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "tests / closures-autofix",
+     "created_at": "2026-11-02T20:46:09Z",
+     "started_at": "2026-11-02T20:46:09Z",
+     "completed_at": "2026-11-02T20:46:09Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "gate",
+     "created_at": "2026-11-02T20:47:53Z",
+     "started_at": "2026-11-02T20:47:56Z",
+     "completed_at": "2026-11-02T20:48:21Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "pr-contract",
+     "created_at": "2026-11-02T20:47:54Z",
+     "started_at": "2026-11-02T20:47:54Z",
+     "completed_at": "2026-11-02T20:47:53Z",
+     "conclusion": "skipped"
+    }
+   ]
+  },
+  {
+   "id": 41513774351,
+   "run_number": 4045,
+   "head_sha": "b469696335e91d9ad2f3a7f39c5de51d26415061",
+   "created_at": "2026-11-02T19:51:13Z",
+   "status": "completed",
+   "conclusion": "cancelled",
+   "path": ".github/workflows/ci.yml",
+   "event": "push",
+   "head_branch": "main",
+   "jobs": [
+    {
+     "name": "prelude",
+     "created_at": "2026-11-02T19:51:14Z",
+     "started_at": "2026-11-02T19:51:47Z",
+     "completed_at": "2026-11-02T19:52:09Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "cancel-superseded",
+     "created_at": "2026-11-02T19:51:14Z",
+     "started_at": "2026-11-02T19:51:14Z",
+     "completed_at": "2026-11-02T19:51:13Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "refresh",
+     "created_at": "2026-11-02T19:51:14Z",
+     "started_at": "2026-11-02T19:51:14Z",
+     "completed_at": "2026-11-02T19:51:13Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "hassfest / hassfest",
+     "created_at": "2026-11-02T19:52:09Z",
+     "started_at": "2026-11-02T19:53:30Z",
+     "completed_at": "2026-11-02T19:53:53Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / mutation",
+     "created_at": "2026-11-02T19:52:09Z",
+     "started_at": "2026-11-02T20:07:01Z",
+     "completed_at": "2026-11-02T20:07:33Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / policy-docs",
+     "created_at": "2026-11-02T19:52:09Z",
+     "started_at": "2026-11-02T19:56:41Z",
+     "completed_at": "2026-11-02T19:57:37Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / briefs",
+     "created_at": "2026-11-02T19:52:09Z",
+     "started_at": "2026-11-02T20:07:27Z",
+     "completed_at": "2026-11-02T20:08:02Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / wave-script",
+     "created_at": "2026-11-02T19:52:09Z",
+     "started_at": "2026-11-02T19:56:41Z",
+     "completed_at": "2026-11-02T19:57:28Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "validate / validate-hacs",
+     "created_at": "2026-11-02T19:52:09Z",
+     "started_at": "2026-11-02T19:53:51Z",
+     "completed_at": "2026-11-02T19:54:23Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (actions)",
+     "created_at": "2026-11-02T19:52:09Z",
+     "started_at": "2026-11-02T19:54:46Z",
+     "completed_at": "2026-11-02T19:55:41Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (javascript-typescript)",
+     "created_at": "2026-11-02T19:52:09Z",
+     "started_at": "2026-11-02T19:52:46Z",
+     "completed_at": "2026-11-02T19:54:31Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / env-matrix",
+     "created_at": "2026-11-02T19:52:09Z",
+     "started_at": "2026-11-02T19:56:42Z",
+     "completed_at": "2026-11-02T20:03:43Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (python)",
+     "created_at": "2026-11-02T19:52:09Z",
+     "started_at": "2026-11-02T19:55:44Z",
+     "completed_at": "2026-11-02T20:36:24Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / instrument-self-tests",
+     "created_at": "2026-11-02T19:52:09Z",
+     "started_at": "2026-11-02T19:57:31Z",
+     "completed_at": "2026-11-02T20:21:15Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / fast (3.14)",
+     "created_at": "2026-11-02T19:52:09Z",
+     "started_at": "2026-11-02T20:08:07Z",
+     "completed_at": "2026-11-02T20:40:51Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / arch-instrument",
+     "created_at": "2026-11-02T19:52:09Z",
+     "started_at": "2026-11-02T20:07:35Z",
+     "completed_at": "2026-11-02T20:39:55Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / typing",
+     "created_at": "2026-11-02T19:52:09Z",
+     "started_at": "2026-11-02T20:13:30Z",
+     "completed_at": "2026-11-02T20:15:05Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / closures",
+     "created_at": "2026-11-02T19:52:09Z",
+     "started_at": "2026-11-02T20:15:54Z",
+     "completed_at": "2026-11-02T20:55:31Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / browser",
+     "created_at": "2026-11-02T19:52:09Z",
+     "started_at": "2026-11-02T20:01:30Z",
+     "completed_at": "2026-11-02T20:05:53Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / coverage",
+     "created_at": "2026-11-02T19:52:09Z",
+     "started_at": "2026-11-02T20:15:58Z",
+     "completed_at": "2026-11-02T20:16:34Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / record",
+     "created_at": "2026-11-02T19:52:09Z",
+     "started_at": "2026-11-02T19:52:09Z",
+     "completed_at": "2026-11-02T19:56:02Z",
+     "conclusion": "cancelled"
+    },
+    {
+     "name": "kernel-points",
+     "created_at": "2026-11-02T19:52:09Z",
+     "started_at": "2026-11-02T19:52:09Z",
+     "completed_at": "2026-11-02T19:52:09Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / delivery-status-publish",
+     "created_at": "2026-11-02T19:52:09Z",
+     "started_at": "2026-11-02T19:52:09Z",
+     "completed_at": "2026-11-02T19:56:02Z",
+     "conclusion": "cancelled"
+    },
+    {
+     "name": "governance / delivery-status",
+     "created_at": "2026-11-02T19:52:09Z",
+     "started_at": "2026-11-02T19:52:09Z",
+     "completed_at": "2026-11-02T19:52:09Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "arch-score",
+     "created_at": "2026-11-02T19:52:09Z",
+     "started_at": "2026-11-02T19:52:09Z",
+     "completed_at": "2026-11-02T19:52:09Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / closure-scope",
+     "created_at": "2026-11-02T19:52:10Z",
+     "started_at": "2026-11-02T19:52:10Z",
+     "completed_at": "2026-11-02T19:52:09Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-status",
+     "created_at": "2026-11-02T19:52:10Z",
+     "started_at": "2026-11-02T19:52:10Z",
+     "completed_at": "2026-11-02T19:52:09Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / replay",
+     "created_at": "2026-11-02T19:52:10Z",
+     "started_at": "2026-11-02T19:52:10Z",
+     "completed_at": "2026-11-02T19:52:09Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "budget-raise-gate",
+     "created_at": "2026-11-02T19:52:10Z",
+     "started_at": "2026-11-02T19:52:10Z",
+     "completed_at": "2026-11-02T19:52:09Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-ha",
+     "created_at": "2026-11-02T19:52:10Z",
+     "started_at": "2026-11-02T19:52:10Z",
+     "completed_at": "2026-11-02T19:52:09Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-pins",
+     "created_at": "2026-11-02T20:07:33Z",
+     "started_at": "2026-11-02T20:07:33Z",
+     "completed_at": "2026-11-02T20:07:33Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-autofix",
+     "created_at": "2026-11-02T20:07:33Z",
+     "started_at": "2026-11-02T20:07:33Z",
+     "completed_at": "2026-11-02T20:07:33Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / coverage-ratchet",
+     "created_at": "2026-11-02T20:16:34Z",
+     "started_at": "2026-11-02T20:21:07Z",
+     "completed_at": "2026-11-02T20:21:28Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / graders-head-copy",
+     "created_at": "2026-11-02T20:16:34Z",
+     "started_at": "2026-11-02T20:16:34Z",
+     "completed_at": "2026-11-02T20:16:34Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / lane-proofs",
+     "created_at": "2026-11-02T20:40:52Z",
+     "started_at": "2026-11-02T20:40:52Z",
+     "completed_at": "2026-11-02T20:40:52Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / claims-autofix",
+     "created_at": "2026-11-02T20:40:52Z",
+     "started_at": "2026-11-02T20:40:52Z",
+     "completed_at": "2026-11-02T20:40:52Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / ci-ratchet",
+     "created_at": "2026-11-02T20:55:32Z",
+     "started_at": "2026-11-02T20:55:35Z",
+     "completed_at": "2026-11-02T20:56:55Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "tests / closures-autofix",
+     "created_at": "2026-11-02T20:55:32Z",
+     "started_at": "2026-11-02T20:55:32Z",
+     "completed_at": "2026-11-02T20:55:32Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "gate",
+     "created_at": "2026-11-02T20:56:56Z",
+     "started_at": "2026-11-02T20:56:59Z",
+     "completed_at": "2026-11-02T20:57:27Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "pr-contract",
+     "created_at": "2026-11-02T20:56:56Z",
+     "started_at": "2026-11-02T20:56:56Z",
+     "completed_at": "2026-11-02T20:56:56Z",
+     "conclusion": "skipped"
+    }
+   ]
+  },
+  {
+   "id": 41513913688,
+   "run_number": 4046,
+   "head_sha": "b8e823699981866383f1afa54ce708ded3419316",
+   "created_at": "2026-11-02T19:52:09Z",
+   "status": "completed",
+   "conclusion": "failure",
+   "path": ".github/workflows/ci.yml",
+   "event": "push",
+   "head_branch": "main",
+   "jobs": [
+    {
+     "name": "prelude",
+     "created_at": "2026-11-02T19:52:10Z",
+     "started_at": "2026-11-02T19:55:34Z",
+     "completed_at": "2026-11-02T19:56:01Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "refresh",
+     "created_at": "2026-11-02T19:52:10Z",
+     "started_at": "2026-11-02T19:52:10Z",
+     "completed_at": "2026-11-02T19:52:10Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "cancel-superseded",
+     "created_at": "2026-11-02T19:52:10Z",
+     "started_at": "2026-11-02T19:52:10Z",
+     "completed_at": "2026-11-02T19:52:10Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "validate / validate-hacs",
+     "created_at": "2026-11-02T19:56:01Z",
+     "started_at": "2026-11-02T20:00:26Z",
+     "completed_at": "2026-11-02T20:01:13Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / policy-docs",
+     "created_at": "2026-11-02T19:56:01Z",
+     "started_at": "2026-11-02T19:57:40Z",
+     "completed_at": "2026-11-02T19:58:49Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / mutation",
+     "created_at": "2026-11-02T19:56:01Z",
+     "started_at": "2026-11-02T20:16:52Z",
+     "completed_at": "2026-11-02T20:17:44Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / wave-script",
+     "created_at": "2026-11-02T19:56:01Z",
+     "started_at": "2026-11-02T20:03:21Z",
+     "completed_at": "2026-11-02T20:04:14Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "hassfest / hassfest",
+     "created_at": "2026-11-02T19:56:01Z",
+     "started_at": "2026-11-02T19:57:08Z",
+     "completed_at": "2026-11-02T19:57:29Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (python)",
+     "created_at": "2026-11-02T19:56:01Z",
+     "started_at": "2026-11-02T19:57:27Z",
+     "completed_at": "2026-11-02T20:37:31Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / instrument-self-tests",
+     "created_at": "2026-11-02T19:56:01Z",
+     "started_at": "2026-11-02T20:06:06Z",
+     "completed_at": "2026-11-02T20:30:05Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / env-matrix",
+     "created_at": "2026-11-02T19:56:01Z",
+     "started_at": "2026-11-02T20:10:28Z",
+     "completed_at": "2026-11-02T20:17:43Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (actions)",
+     "created_at": "2026-11-02T19:56:01Z",
+     "started_at": "2026-11-02T19:57:59Z",
+     "completed_at": "2026-11-02T19:59:02Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (javascript-typescript)",
+     "created_at": "2026-11-02T19:56:01Z",
+     "started_at": "2026-11-02T19:58:52Z",
+     "completed_at": "2026-11-02T20:00:24Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / briefs",
+     "created_at": "2026-11-02T19:56:01Z",
+     "started_at": "2026-11-02T20:17:46Z",
+     "completed_at": "2026-11-02T20:18:18Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "arch-score",
+     "created_at": "2026-11-02T19:56:01Z",
+     "started_at": "2026-11-02T19:56:01Z",
+     "completed_at": "2026-11-02T19:56:01Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "kernel-points",
+     "created_at": "2026-11-02T19:56:01Z",
+     "started_at": "2026-11-02T19:56:01Z",
+     "completed_at": "2026-11-02T19:56:01Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / delivery-status",
+     "created_at": "2026-11-02T19:56:02Z",
+     "started_at": "2026-11-02T19:56:02Z",
+     "completed_at": "2026-11-02T19:56:01Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / delivery-status-publish",
+     "created_at": "2026-11-02T19:56:02Z",
+     "started_at": "2026-11-02T20:14:44Z",
+     "completed_at": "2026-11-02T20:15:21Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "budget-raise-gate",
+     "created_at": "2026-11-02T19:56:02Z",
+     "started_at": "2026-11-02T19:56:02Z",
+     "completed_at": "2026-11-02T19:56:01Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / fast (3.14)",
+     "created_at": "2026-11-02T19:56:02Z",
+     "started_at": "2026-11-02T20:18:36Z",
+     "completed_at": "2026-11-02T20:52:12Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / typing",
+     "created_at": "2026-11-02T19:56:02Z",
+     "started_at": "2026-11-02T20:18:44Z",
+     "completed_at": "2026-11-02T20:20:18Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / arch-instrument",
+     "created_at": "2026-11-02T19:56:02Z",
+     "started_at": "2026-11-02T20:18:58Z",
+     "completed_at": "2026-11-02T20:37:06Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / coverage",
+     "created_at": "2026-11-02T19:56:02Z",
+     "started_at": "2026-11-02T20:19:05Z",
+     "completed_at": "2026-11-02T20:19:56Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / record",
+     "created_at": "2026-11-02T19:56:02Z",
+     "started_at": "2026-11-02T20:14:51Z",
+     "completed_at": "2026-11-02T20:15:51Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / closure-scope",
+     "created_at": "2026-11-02T19:56:02Z",
+     "started_at": "2026-11-02T19:56:02Z",
+     "completed_at": "2026-11-02T19:56:01Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / browser",
+     "created_at": "2026-11-02T19:56:02Z",
+     "started_at": "2026-11-02T20:19:55Z",
+     "completed_at": "2026-11-02T20:24:11Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / closures",
+     "created_at": "2026-11-02T19:56:02Z",
+     "started_at": "2026-11-02T20:19:32Z",
+     "completed_at": "2026-11-02T20:58:29Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / nightly-status",
+     "created_at": "2026-11-02T19:56:02Z",
+     "started_at": "2026-11-02T19:56:02Z",
+     "completed_at": "2026-11-02T19:56:01Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / replay",
+     "created_at": "2026-11-02T19:56:02Z",
+     "started_at": "2026-11-02T19:56:02Z",
+     "completed_at": "2026-11-02T19:56:02Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-ha",
+     "created_at": "2026-11-02T19:56:02Z",
+     "started_at": "2026-11-02T19:56:02Z",
+     "completed_at": "2026-11-02T19:56:02Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-pins",
+     "created_at": "2026-11-02T20:17:45Z",
+     "started_at": "2026-11-02T20:17:45Z",
+     "completed_at": "2026-11-02T20:17:44Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-autofix",
+     "created_at": "2026-11-02T20:17:45Z",
+     "started_at": "2026-11-02T20:17:45Z",
+     "completed_at": "2026-11-02T20:17:44Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / coverage-ratchet",
+     "created_at": "2026-11-02T20:19:56Z",
+     "started_at": "2026-11-02T20:21:18Z",
+     "completed_at": "2026-11-02T20:21:29Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / graders-head-copy",
+     "created_at": "2026-11-02T20:19:57Z",
+     "started_at": "2026-11-02T20:19:57Z",
+     "completed_at": "2026-11-02T20:19:56Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / lane-proofs",
+     "created_at": "2026-11-02T20:52:13Z",
+     "started_at": "2026-11-02T20:52:13Z",
+     "completed_at": "2026-11-02T20:52:13Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / claims-autofix",
+     "created_at": "2026-11-02T20:52:13Z",
+     "started_at": "2026-11-02T20:52:13Z",
+     "completed_at": "2026-11-02T20:52:13Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / ci-ratchet",
+     "created_at": "2026-11-02T20:58:29Z",
+     "started_at": "2026-11-02T20:58:34Z",
+     "completed_at": "2026-11-02T21:00:03Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "tests / closures-autofix",
+     "created_at": "2026-11-02T20:58:29Z",
+     "started_at": "2026-11-02T20:58:29Z",
+     "completed_at": "2026-11-02T20:58:29Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "gate",
+     "created_at": "2026-11-02T21:00:03Z",
+     "started_at": "2026-11-02T21:00:11Z",
+     "completed_at": "2026-11-02T21:00:32Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "pr-contract",
+     "created_at": "2026-11-02T21:00:03Z",
+     "started_at": "2026-11-02T21:00:03Z",
+     "completed_at": "2026-11-02T21:00:03Z",
+     "conclusion": "skipped"
+    }
+   ]
+  },
+  {
+   "id": 41555455326,
+   "run_number": 4055,
+   "head_sha": "f8bab78d109bac47dd3931a6d90032343388de47",
+   "created_at": "2026-11-03T00:48:28Z",
+   "status": "completed",
+   "conclusion": "failure",
+   "path": ".github/workflows/ci.yml",
+   "event": "push",
+   "head_branch": "main",
+   "jobs": [
+    {
+     "name": "prelude",
+     "created_at": "2026-11-03T00:48:29Z",
+     "started_at": "2026-11-03T00:48:31Z",
+     "completed_at": "2026-11-03T00:48:56Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "cancel-superseded",
+     "created_at": "2026-11-03T00:48:29Z",
+     "started_at": "2026-11-03T00:48:29Z",
+     "completed_at": "2026-11-03T00:48:29Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "refresh",
+     "created_at": "2026-11-03T00:48:29Z",
+     "started_at": "2026-11-03T00:48:29Z",
+     "completed_at": "2026-11-03T00:48:29Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "hassfest / hassfest",
+     "created_at": "2026-11-03T00:48:56Z",
+     "started_at": "2026-11-03T00:49:09Z",
+     "completed_at": "2026-11-03T00:49:28Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "validate / validate-hacs",
+     "created_at": "2026-11-03T00:48:56Z",
+     "started_at": "2026-11-03T00:48:59Z",
+     "completed_at": "2026-11-03T00:49:34Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / policy-docs",
+     "created_at": "2026-11-03T00:48:56Z",
+     "started_at": "2026-11-03T00:48:59Z",
+     "completed_at": "2026-11-03T00:50:09Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / env-matrix",
+     "created_at": "2026-11-03T00:48:56Z",
+     "started_at": "2026-11-03T00:48:59Z",
+     "completed_at": "2026-11-03T00:55:39Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / instrument-self-tests",
+     "created_at": "2026-11-03T00:48:56Z",
+     "started_at": "2026-11-03T00:48:59Z",
+     "completed_at": "2026-11-03T01:17:52Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (actions)",
+     "created_at": "2026-11-03T00:48:56Z",
+     "started_at": "2026-11-03T00:48:59Z",
+     "completed_at": "2026-11-03T00:50:00Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (python)",
+     "created_at": "2026-11-03T00:48:56Z",
+     "started_at": "2026-11-03T00:48:59Z",
+     "completed_at": "2026-11-03T01:25:29Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / briefs",
+     "created_at": "2026-11-03T00:48:56Z",
+     "started_at": "2026-11-03T00:48:59Z",
+     "completed_at": "2026-11-03T00:49:55Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (javascript-typescript)",
+     "created_at": "2026-11-03T00:48:56Z",
+     "started_at": "2026-11-03T00:48:59Z",
+     "completed_at": "2026-11-03T00:50:36Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / wave-script",
+     "created_at": "2026-11-03T00:48:56Z",
+     "started_at": "2026-11-03T00:48:59Z",
+     "completed_at": "2026-11-03T00:49:44Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / mutation",
+     "created_at": "2026-11-03T00:48:56Z",
+     "started_at": "2026-11-03T00:49:00Z",
+     "completed_at": "2026-11-03T00:49:47Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "kernel-points",
+     "created_at": "2026-11-03T00:48:56Z",
+     "started_at": "2026-11-03T00:48:56Z",
+     "completed_at": "2026-11-03T00:48:56Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / record",
+     "created_at": "2026-11-03T00:48:56Z",
+     "started_at": "2026-11-03T00:48:59Z",
+     "completed_at": "2026-11-03T00:49:29Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / delivery-status-publish",
+     "created_at": "2026-11-03T00:48:56Z",
+     "started_at": "2026-11-03T00:48:59Z",
+     "completed_at": "2026-11-03T00:49:34Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "budget-raise-gate",
+     "created_at": "2026-11-03T00:48:56Z",
+     "started_at": "2026-11-03T00:48:56Z",
+     "completed_at": "2026-11-03T00:48:56Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / fast (3.14)",
+     "created_at": "2026-11-03T00:48:57Z",
+     "started_at": "2026-11-03T00:48:59Z",
+     "completed_at": "2026-11-03T01:21:07Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "arch-score",
+     "created_at": "2026-11-03T00:48:57Z",
+     "started_at": "2026-11-03T00:48:57Z",
+     "completed_at": "2026-11-03T00:48:56Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / arch-instrument",
+     "created_at": "2026-11-03T00:48:57Z",
+     "started_at": "2026-11-03T00:48:59Z",
+     "completed_at": "2026-11-03T01:20:26Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / coverage",
+     "created_at": "2026-11-03T00:48:57Z",
+     "started_at": "2026-11-03T00:48:59Z",
+     "completed_at": "2026-11-03T00:49:50Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / browser",
+     "created_at": "2026-11-03T00:48:57Z",
+     "started_at": "2026-11-03T00:48:59Z",
+     "completed_at": "2026-11-03T00:52:39Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / closures",
+     "created_at": "2026-11-03T00:48:57Z",
+     "started_at": "2026-11-03T00:48:59Z",
+     "completed_at": "2026-11-03T01:09:33Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / typing",
+     "created_at": "2026-11-03T00:48:57Z",
+     "started_at": "2026-11-03T00:49:00Z",
+     "completed_at": "2026-11-03T00:50:00Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / nightly-status",
+     "created_at": "2026-11-03T00:48:57Z",
+     "started_at": "2026-11-03T00:48:57Z",
+     "completed_at": "2026-11-03T00:48:56Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / delivery-status",
+     "created_at": "2026-11-03T00:48:57Z",
+     "started_at": "2026-11-03T00:48:57Z",
+     "completed_at": "2026-11-03T00:48:56Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / closure-scope",
+     "created_at": "2026-11-03T00:48:57Z",
+     "started_at": "2026-11-03T00:48:57Z",
+     "completed_at": "2026-11-03T00:48:56Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-ha",
+     "created_at": "2026-11-03T00:48:57Z",
+     "started_at": "2026-11-03T00:48:57Z",
+     "completed_at": "2026-11-03T00:48:56Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / replay",
+     "created_at": "2026-11-03T00:48:57Z",
+     "started_at": "2026-11-03T00:48:57Z",
+     "completed_at": "2026-11-03T00:48:56Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-pins",
+     "created_at": "2026-11-03T00:49:47Z",
+     "started_at": "2026-11-03T00:49:47Z",
+     "completed_at": "2026-11-03T00:49:47Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-autofix",
+     "created_at": "2026-11-03T00:49:48Z",
+     "started_at": "2026-11-03T00:49:48Z",
+     "completed_at": "2026-11-03T00:49:47Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / coverage-ratchet",
+     "created_at": "2026-11-03T00:49:50Z",
+     "started_at": "2026-11-03T00:49:53Z",
+     "completed_at": "2026-11-03T00:50:01Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / graders-head-copy",
+     "created_at": "2026-11-03T00:49:50Z",
+     "started_at": "2026-11-03T00:49:50Z",
+     "completed_at": "2026-11-03T00:49:50Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / closures-autofix",
+     "created_at": "2026-11-03T01:09:34Z",
+     "started_at": "2026-11-03T01:09:34Z",
+     "completed_at": "2026-11-03T01:09:33Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / ci-ratchet",
+     "created_at": "2026-11-03T01:21:07Z",
+     "started_at": "2026-11-03T01:21:09Z",
+     "completed_at": "2026-11-03T01:22:06Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "tests / claims-autofix",
+     "created_at": "2026-11-03T01:21:07Z",
+     "started_at": "2026-11-03T01:21:07Z",
+     "completed_at": "2026-11-03T01:21:07Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / lane-proofs",
+     "created_at": "2026-11-03T01:21:07Z",
+     "started_at": "2026-11-03T01:21:07Z",
+     "completed_at": "2026-11-03T01:21:07Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "gate",
+     "created_at": "2026-11-03T01:25:30Z",
+     "started_at": "2026-11-03T01:25:33Z",
+     "completed_at": "2026-11-03T01:26:01Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "pr-contract",
+     "created_at": "2026-11-03T01:25:30Z",
+     "started_at": "2026-11-03T01:25:30Z",
+     "completed_at": "2026-11-03T01:25:29Z",
+     "conclusion": "skipped"
+    }
+   ]
+  },
+  {
+   "id": 41577822624,
+   "run_number": 4056,
+   "head_sha": "c3a279e3252a8b57bb00b5a677318cd4fe20387f",
+   "created_at": "2026-11-03T04:23:15Z",
+   "status": "completed",
+   "conclusion": "failure",
+   "path": ".github/workflows/ci.yml",
+   "event": "push",
+   "head_branch": "main",
+   "jobs": [
+    {
+     "name": "prelude",
+     "created_at": "2026-11-03T04:23:16Z",
+     "started_at": "2026-11-03T04:23:27Z",
+     "completed_at": "2026-11-03T04:23:49Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "cancel-superseded",
+     "created_at": "2026-11-03T04:23:16Z",
+     "started_at": "2026-11-03T04:23:16Z",
+     "completed_at": "2026-11-03T04:23:16Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "refresh",
+     "created_at": "2026-11-03T04:23:16Z",
+     "started_at": "2026-11-03T04:23:16Z",
+     "completed_at": "2026-11-03T04:23:16Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "validate / validate-hacs",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:52Z",
+     "completed_at": "2026-11-03T04:24:22Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (python)",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:52Z",
+     "completed_at": "2026-11-03T04:55:06Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / briefs",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:52Z",
+     "completed_at": "2026-11-03T04:24:39Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (javascript-typescript)",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:52Z",
+     "completed_at": "2026-11-03T04:25:31Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / policy-docs",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:52Z",
+     "completed_at": "2026-11-03T04:24:36Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "hassfest / hassfest",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:52Z",
+     "completed_at": "2026-11-03T04:24:23Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / wave-script",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:52Z",
+     "completed_at": "2026-11-03T04:24:31Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (actions)",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:53Z",
+     "completed_at": "2026-11-03T04:24:48Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / instrument-self-tests",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:57Z",
+     "completed_at": "2026-11-03T04:52:23Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / mutation",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:53Z",
+     "completed_at": "2026-11-03T04:24:38Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / env-matrix",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:52Z",
+     "completed_at": "2026-11-03T04:30:48Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / record",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:52Z",
+     "completed_at": "2026-11-03T04:24:13Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / delivery-status-publish",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:53Z",
+     "completed_at": "2026-11-03T04:24:22Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / typing",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:52Z",
+     "completed_at": "2026-11-03T04:24:57Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / closures",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:52Z",
+     "completed_at": "2026-11-03T04:48:01Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / fast (3.14)",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:53Z",
+     "completed_at": "2026-11-03T04:56:35Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / arch-instrument",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:52Z",
+     "completed_at": "2026-11-03T04:42:45Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / browser",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:52Z",
+     "completed_at": "2026-11-03T04:27:36Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / coverage",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:52Z",
+     "completed_at": "2026-11-03T04:40:50Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "arch-score",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:49Z",
+     "completed_at": "2026-11-03T04:23:49Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "kernel-points",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:49Z",
+     "completed_at": "2026-11-03T04:23:49Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "budget-raise-gate",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:49Z",
+     "completed_at": "2026-11-03T04:23:49Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / delivery-status",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:49Z",
+     "completed_at": "2026-11-03T04:23:49Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-status",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:49Z",
+     "completed_at": "2026-11-03T04:23:49Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / closure-scope",
+     "created_at": "2026-11-03T04:23:49Z",
+     "started_at": "2026-11-03T04:23:49Z",
+     "completed_at": "2026-11-03T04:23:49Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / replay",
+     "created_at": "2026-11-03T04:23:50Z",
+     "started_at": "2026-11-03T04:23:50Z",
+     "completed_at": "2026-11-03T04:23:49Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-ha",
+     "created_at": "2026-11-03T04:23:50Z",
+     "started_at": "2026-11-03T04:23:50Z",
+     "completed_at": "2026-11-03T04:23:49Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-pins",
+     "created_at": "2026-11-03T04:24:38Z",
+     "started_at": "2026-11-03T04:24:38Z",
+     "completed_at": "2026-11-03T04:24:38Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-autofix",
+     "created_at": "2026-11-03T04:24:38Z",
+     "started_at": "2026-11-03T04:24:38Z",
+     "completed_at": "2026-11-03T04:24:38Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / coverage-ratchet",
+     "created_at": "2026-11-03T04:40:50Z",
+     "started_at": "2026-11-03T04:41:03Z",
+     "completed_at": "2026-11-03T04:41:13Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / graders-head-copy",
+     "created_at": "2026-11-03T04:40:50Z",
+     "started_at": "2026-11-03T04:40:50Z",
+     "completed_at": "2026-11-03T04:40:50Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / closures-autofix",
+     "created_at": "2026-11-03T04:48:01Z",
+     "started_at": "2026-11-03T04:48:01Z",
+     "completed_at": "2026-11-03T04:48:01Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / ci-ratchet",
+     "created_at": "2026-11-03T04:56:35Z",
+     "started_at": "2026-11-03T04:56:38Z",
+     "completed_at": "2026-11-03T04:58:14Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "tests / lane-proofs",
+     "created_at": "2026-11-03T04:56:36Z",
+     "started_at": "2026-11-03T04:56:36Z",
+     "completed_at": "2026-11-03T04:56:35Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / claims-autofix",
+     "created_at": "2026-11-03T04:56:36Z",
+     "started_at": "2026-11-03T04:56:36Z",
+     "completed_at": "2026-11-03T04:56:35Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "gate",
+     "created_at": "2026-11-03T04:58:15Z",
+     "started_at": "2026-11-03T04:58:17Z",
+     "completed_at": "2026-11-03T04:58:42Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "pr-contract",
+     "created_at": "2026-11-03T04:58:15Z",
+     "started_at": "2026-11-03T04:58:15Z",
+     "completed_at": "2026-11-03T04:58:14Z",
+     "conclusion": "skipped"
+    }
+   ]
+  },
+  {
+   "id": 41797862663,
+   "run_number": 4080,
+   "head_sha": "a9c2f90fc77be2e7a870f3f2735dcd0f79b5f475",
+   "created_at": "2026-11-04T08:13:36Z",
+   "status": "completed",
+   "conclusion": "success",
+   "path": ".github/workflows/ci.yml",
+   "event": "push",
+   "head_branch": "main",
+   "jobs": [
+    {
+     "name": "prelude",
+     "created_at": "2026-11-04T08:13:37Z",
+     "started_at": "2026-11-04T08:13:40Z",
+     "completed_at": "2026-11-04T08:14:04Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "cancel-superseded",
+     "created_at": "2026-11-04T08:13:37Z",
+     "started_at": "2026-11-04T08:13:37Z",
+     "completed_at": "2026-11-04T08:13:36Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "refresh",
+     "created_at": "2026-11-04T08:13:37Z",
+     "started_at": "2026-11-04T08:13:37Z",
+     "completed_at": "2026-11-04T08:13:36Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "validate / validate-hacs",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:07Z",
+     "completed_at": "2026-11-04T08:14:43Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (python)",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:07Z",
+     "completed_at": "2026-11-04T08:41:58Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (actions)",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:07Z",
+     "completed_at": "2026-11-04T08:15:10Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (javascript-typescript)",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:07Z",
+     "completed_at": "2026-11-04T08:16:02Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / mutation",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:07Z",
+     "completed_at": "2026-11-04T08:14:51Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / policy-docs",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:07Z",
+     "completed_at": "2026-11-04T08:14:49Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / briefs",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:07Z",
+     "completed_at": "2026-11-04T08:14:38Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / instrument-self-tests",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:07Z",
+     "completed_at": "2026-11-04T08:43:16Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / env-matrix",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:07Z",
+     "completed_at": "2026-11-04T08:19:29Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / wave-script",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:07Z",
+     "completed_at": "2026-11-04T08:14:52Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "hassfest / hassfest",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:07Z",
+     "completed_at": "2026-11-04T08:14:29Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / delivery-status-publish",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:07Z",
+     "completed_at": "2026-11-04T08:14:35Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / record",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:07Z",
+     "completed_at": "2026-11-04T08:14:35Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / coverage",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:07Z",
+     "completed_at": "2026-11-04T08:25:46Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / browser",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:07Z",
+     "completed_at": "2026-11-04T08:18:08Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / fast (3.14)",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:07Z",
+     "completed_at": "2026-11-04T08:47:53Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / arch-instrument",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:07Z",
+     "completed_at": "2026-11-04T08:33:37Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / typing",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:07Z",
+     "completed_at": "2026-11-04T08:15:26Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / closures",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:07Z",
+     "completed_at": "2026-11-04T08:34:16Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "kernel-points",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:04Z",
+     "completed_at": "2026-11-04T08:14:04Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-status",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:04Z",
+     "completed_at": "2026-11-04T08:14:04Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "budget-raise-gate",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:04Z",
+     "completed_at": "2026-11-04T08:14:04Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / closure-scope",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:04Z",
+     "completed_at": "2026-11-04T08:14:04Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "arch-score",
+     "created_at": "2026-11-04T08:14:04Z",
+     "started_at": "2026-11-04T08:14:04Z",
+     "completed_at": "2026-11-04T08:14:04Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / delivery-status",
+     "created_at": "2026-11-04T08:14:05Z",
+     "started_at": "2026-11-04T08:14:05Z",
+     "completed_at": "2026-11-04T08:14:04Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-ha",
+     "created_at": "2026-11-04T08:14:05Z",
+     "started_at": "2026-11-04T08:14:05Z",
+     "completed_at": "2026-11-04T08:14:04Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / replay",
+     "created_at": "2026-11-04T08:14:05Z",
+     "started_at": "2026-11-04T08:14:05Z",
+     "completed_at": "2026-11-04T08:14:04Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-pins",
+     "created_at": "2026-11-04T08:14:52Z",
+     "started_at": "2026-11-04T08:14:52Z",
+     "completed_at": "2026-11-04T08:14:51Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-autofix",
+     "created_at": "2026-11-04T08:14:52Z",
+     "started_at": "2026-11-04T08:14:52Z",
+     "completed_at": "2026-11-04T08:14:51Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / coverage-ratchet",
+     "created_at": "2026-11-04T08:25:47Z",
+     "started_at": "2026-11-04T08:25:49Z",
+     "completed_at": "2026-11-04T08:25:58Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / graders-head-copy",
+     "created_at": "2026-11-04T08:25:47Z",
+     "started_at": "2026-11-04T08:25:47Z",
+     "completed_at": "2026-11-04T08:25:47Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / closures-autofix",
+     "created_at": "2026-11-04T08:34:17Z",
+     "started_at": "2026-11-04T08:34:17Z",
+     "completed_at": "2026-11-04T08:34:17Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / ci-ratchet",
+     "created_at": "2026-11-04T08:47:53Z",
+     "started_at": "2026-11-04T08:47:56Z",
+     "completed_at": "2026-11-04T08:49:33Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / lane-proofs",
+     "created_at": "2026-11-04T08:47:54Z",
+     "started_at": "2026-11-04T08:47:54Z",
+     "completed_at": "2026-11-04T08:47:53Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / claims-autofix",
+     "created_at": "2026-11-04T08:47:54Z",
+     "started_at": "2026-11-04T08:47:54Z",
+     "completed_at": "2026-11-04T08:47:53Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "gate",
+     "created_at": "2026-11-04T08:49:34Z",
+     "started_at": "2026-11-04T08:50:28Z",
+     "completed_at": "2026-11-04T08:50:51Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "pr-contract",
+     "created_at": "2026-11-04T08:49:34Z",
+     "started_at": "2026-11-04T08:49:34Z",
+     "completed_at": "2026-11-04T08:49:33Z",
+     "conclusion": "skipped"
+    }
+   ]
+  },
+  {
+   "id": 41807454797,
+   "run_number": 4107,
+   "head_sha": "fad43b0471b9cef3c563d2c2ae1eab3d87a34190",
+   "created_at": "2026-11-04T09:26:01Z",
+   "status": "completed",
+   "conclusion": "success",
+   "path": ".github/workflows/ci.yml",
+   "event": "push",
+   "head_branch": "main",
+   "jobs": [
+    {
+     "name": "prelude",
+     "created_at": "2026-11-04T09:26:02Z",
+     "started_at": "2026-11-04T09:26:05Z",
+     "completed_at": "2026-11-04T09:26:37Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "cancel-superseded",
+     "created_at": "2026-11-04T09:26:02Z",
+     "started_at": "2026-11-04T09:26:02Z",
+     "completed_at": "2026-11-04T09:26:02Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "refresh",
+     "created_at": "2026-11-04T09:26:02Z",
+     "started_at": "2026-11-04T09:26:02Z",
+     "completed_at": "2026-11-04T09:26:02Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "validate / validate-hacs",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:26:47Z",
+     "completed_at": "2026-11-04T09:27:22Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "hassfest / hassfest",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:26:40Z",
+     "completed_at": "2026-11-04T09:26:58Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / policy-docs",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:27:06Z",
+     "completed_at": "2026-11-04T09:31:00Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (actions)",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:26:55Z",
+     "completed_at": "2026-11-04T09:27:48Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (python)",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:26:40Z",
+     "completed_at": "2026-11-04T10:09:26Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / wave-script",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:26:42Z",
+     "completed_at": "2026-11-04T09:27:15Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / env-matrix",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:26:42Z",
+     "completed_at": "2026-11-04T09:31:14Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / instrument-self-tests",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:26:40Z",
+     "completed_at": "2026-11-04T09:49:56Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / briefs",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:26:40Z",
+     "completed_at": "2026-11-04T09:27:17Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (javascript-typescript)",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:26:53Z",
+     "completed_at": "2026-11-04T09:28:07Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / mutation",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:26:40Z",
+     "completed_at": "2026-11-04T09:27:16Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / delivery-status-publish",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:27:10Z",
+     "completed_at": "2026-11-04T09:27:38Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / record",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:27:20Z",
+     "completed_at": "2026-11-04T09:27:52Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / closures",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:27:19Z",
+     "completed_at": "2026-11-04T10:06:42Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / arch-instrument",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:27:18Z",
+     "completed_at": "2026-11-04T09:51:32Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / coverage",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:27:20Z",
+     "completed_at": "2026-11-04T09:39:47Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / browser",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:26:40Z",
+     "completed_at": "2026-11-04T09:30:41Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / typing",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:26:40Z",
+     "completed_at": "2026-11-04T09:27:40Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / fast (3.14)",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:27:24Z",
+     "completed_at": "2026-11-04T10:00:47Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "arch-score",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:26:37Z",
+     "completed_at": "2026-11-04T09:26:37Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-status",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:26:37Z",
+     "completed_at": "2026-11-04T09:26:37Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "budget-raise-gate",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:26:37Z",
+     "completed_at": "2026-11-04T09:26:37Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "kernel-points",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:26:37Z",
+     "completed_at": "2026-11-04T09:26:37Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / closure-scope",
+     "created_at": "2026-11-04T09:26:37Z",
+     "started_at": "2026-11-04T09:26:37Z",
+     "completed_at": "2026-11-04T09:26:37Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / delivery-status",
+     "created_at": "2026-11-04T09:26:38Z",
+     "started_at": "2026-11-04T09:26:38Z",
+     "completed_at": "2026-11-04T09:26:37Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / replay",
+     "created_at": "2026-11-04T09:26:38Z",
+     "started_at": "2026-11-04T09:26:38Z",
+     "completed_at": "2026-11-04T09:26:37Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-ha",
+     "created_at": "2026-11-04T09:26:38Z",
+     "started_at": "2026-11-04T09:26:38Z",
+     "completed_at": "2026-11-04T09:26:37Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-pins",
+     "created_at": "2026-11-04T09:27:17Z",
+     "started_at": "2026-11-04T09:27:17Z",
+     "completed_at": "2026-11-04T09:27:16Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-autofix",
+     "created_at": "2026-11-04T09:27:17Z",
+     "started_at": "2026-11-04T09:27:17Z",
+     "completed_at": "2026-11-04T09:27:16Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / coverage-ratchet",
+     "created_at": "2026-11-04T09:39:47Z",
+     "started_at": "2026-11-04T09:39:50Z",
+     "completed_at": "2026-11-04T09:40:00Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / graders-head-copy",
+     "created_at": "2026-11-04T09:39:48Z",
+     "started_at": "2026-11-04T09:39:48Z",
+     "completed_at": "2026-11-04T09:39:47Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / claims-autofix",
+     "created_at": "2026-11-04T10:00:48Z",
+     "started_at": "2026-11-04T10:00:48Z",
+     "completed_at": "2026-11-04T10:00:47Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / lane-proofs",
+     "created_at": "2026-11-04T10:00:48Z",
+     "started_at": "2026-11-04T10:00:48Z",
+     "completed_at": "2026-11-04T10:00:47Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / ci-ratchet",
+     "created_at": "2026-11-04T10:06:43Z",
+     "started_at": "2026-11-04T10:06:46Z",
+     "completed_at": "2026-11-04T10:08:23Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / closures-autofix",
+     "created_at": "2026-11-04T10:06:43Z",
+     "started_at": "2026-11-04T10:06:43Z",
+     "completed_at": "2026-11-04T10:06:42Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "gate",
+     "created_at": "2026-11-04T10:09:26Z",
+     "started_at": "2026-11-04T10:09:29Z",
+     "completed_at": "2026-11-04T10:09:55Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "pr-contract",
+     "created_at": "2026-11-04T10:09:26Z",
+     "started_at": "2026-11-04T10:09:26Z",
+     "completed_at": "2026-11-04T10:09:26Z",
+     "conclusion": "skipped"
+    }
+   ]
+  },
+  {
+   "id": 41812846310,
+   "run_number": 4116,
+   "head_sha": "616868bdc5ca54d9555cfc89715f05a33527661e",
+   "created_at": "2026-11-04T10:14:21Z",
+   "status": "completed",
+   "conclusion": "success",
+   "path": ".github/workflows/ci.yml",
+   "event": "push",
+   "head_branch": "main",
+   "jobs": [
+    {
+     "name": "prelude",
+     "created_at": "2026-11-04T10:14:22Z",
+     "started_at": "2026-11-04T10:14:25Z",
+     "completed_at": "2026-11-04T10:14:49Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "refresh",
+     "created_at": "2026-11-04T10:14:22Z",
+     "started_at": "2026-11-04T10:14:22Z",
+     "completed_at": "2026-11-04T10:14:22Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "cancel-superseded",
+     "created_at": "2026-11-04T10:14:24Z",
+     "started_at": "2026-11-04T10:14:24Z",
+     "completed_at": "2026-11-04T10:14:22Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / instrument-self-tests",
+     "created_at": "2026-11-04T10:14:49Z",
+     "started_at": "2026-11-04T10:14:52Z",
+     "completed_at": "2026-11-04T10:38:48Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "validate / validate-hacs",
+     "created_at": "2026-11-04T10:14:49Z",
+     "started_at": "2026-11-04T10:14:52Z",
+     "completed_at": "2026-11-04T10:15:31Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / policy-docs",
+     "created_at": "2026-11-04T10:14:49Z",
+     "started_at": "2026-11-04T10:14:52Z",
+     "completed_at": "2026-11-04T10:18:48Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / delivery-status-publish",
+     "created_at": "2026-11-04T10:14:49Z",
+     "started_at": "2026-11-04T10:14:53Z",
+     "completed_at": "2026-11-04T10:15:15Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (actions)",
+     "created_at": "2026-11-04T10:14:50Z",
+     "started_at": "2026-11-04T10:14:53Z",
+     "completed_at": "2026-11-04T10:15:51Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / wave-script",
+     "created_at": "2026-11-04T10:14:50Z",
+     "started_at": "2026-11-04T10:14:53Z",
+     "completed_at": "2026-11-04T10:15:43Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / closures",
+     "created_at": "2026-11-04T10:14:50Z",
+     "started_at": "2026-11-04T10:14:53Z",
+     "completed_at": "2026-11-04T10:41:27Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (javascript-typescript)",
+     "created_at": "2026-11-04T10:14:50Z",
+     "started_at": "2026-11-04T10:14:52Z",
+     "completed_at": "2026-11-04T10:16:36Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / typing",
+     "created_at": "2026-11-04T10:14:50Z",
+     "started_at": "2026-11-04T10:14:53Z",
+     "completed_at": "2026-11-04T10:16:15Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / briefs",
+     "created_at": "2026-11-04T10:14:50Z",
+     "started_at": "2026-11-04T10:14:53Z",
+     "completed_at": "2026-11-04T10:15:31Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / fast (3.14)",
+     "created_at": "2026-11-04T10:14:50Z",
+     "started_at": "2026-11-04T10:14:53Z",
+     "completed_at": "2026-11-04T10:48:08Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / arch-instrument",
+     "created_at": "2026-11-04T10:14:50Z",
+     "started_at": "2026-11-04T10:14:52Z",
+     "completed_at": "2026-11-04T10:35:40Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / browser",
+     "created_at": "2026-11-04T10:14:50Z",
+     "started_at": "2026-11-04T10:14:52Z",
+     "completed_at": "2026-11-04T10:18:51Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / record",
+     "created_at": "2026-11-04T10:14:50Z",
+     "started_at": "2026-11-04T10:14:52Z",
+     "completed_at": "2026-11-04T10:15:20Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / coverage",
+     "created_at": "2026-11-04T10:14:50Z",
+     "started_at": "2026-11-04T10:14:52Z",
+     "completed_at": "2026-11-04T10:33:12Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (python)",
+     "created_at": "2026-11-04T10:14:50Z",
+     "started_at": "2026-11-04T10:14:53Z",
+     "completed_at": "2026-11-04T10:46:01Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / closure-scope",
+     "created_at": "2026-11-04T10:14:50Z",
+     "started_at": "2026-11-04T10:14:50Z",
+     "completed_at": "2026-11-04T10:14:49Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / delivery-status",
+     "created_at": "2026-11-04T10:14:50Z",
+     "started_at": "2026-11-04T10:14:50Z",
+     "completed_at": "2026-11-04T10:14:49Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "kernel-points",
+     "created_at": "2026-11-04T10:14:50Z",
+     "started_at": "2026-11-04T10:14:50Z",
+     "completed_at": "2026-11-04T10:14:49Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "arch-score",
+     "created_at": "2026-11-04T10:14:50Z",
+     "started_at": "2026-11-04T10:14:50Z",
+     "completed_at": "2026-11-04T10:14:49Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / env-matrix",
+     "created_at": "2026-11-04T10:14:50Z",
+     "started_at": "2026-11-04T10:14:52Z",
+     "completed_at": "2026-11-04T10:19:17Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / replay",
+     "created_at": "2026-11-04T10:14:50Z",
+     "started_at": "2026-11-04T10:14:50Z",
+     "completed_at": "2026-11-04T10:14:49Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-ha",
+     "created_at": "2026-11-04T10:14:50Z",
+     "started_at": "2026-11-04T10:14:50Z",
+     "completed_at": "2026-11-04T10:14:49Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-status",
+     "created_at": "2026-11-04T10:14:50Z",
+     "started_at": "2026-11-04T10:14:50Z",
+     "completed_at": "2026-11-04T10:14:49Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation",
+     "created_at": "2026-11-04T10:14:51Z",
+     "started_at": "2026-11-04T10:14:54Z",
+     "completed_at": "2026-11-04T10:15:40Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "budget-raise-gate",
+     "created_at": "2026-11-04T10:14:51Z",
+     "started_at": "2026-11-04T10:14:51Z",
+     "completed_at": "2026-11-04T10:14:49Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "hassfest / hassfest",
+     "created_at": "2026-11-04T10:14:58Z",
+     "started_at": "2026-11-04T10:15:01Z",
+     "completed_at": "2026-11-04T10:15:19Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / mutation-pins",
+     "created_at": "2026-11-04T10:15:40Z",
+     "started_at": "2026-11-04T10:15:40Z",
+     "completed_at": "2026-11-04T10:15:40Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-autofix",
+     "created_at": "2026-11-04T10:15:41Z",
+     "started_at": "2026-11-04T10:15:41Z",
+     "completed_at": "2026-11-04T10:15:40Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / coverage-ratchet",
+     "created_at": "2026-11-04T10:33:13Z",
+     "started_at": "2026-11-04T10:33:15Z",
+     "completed_at": "2026-11-04T10:33:26Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / graders-head-copy",
+     "created_at": "2026-11-04T10:33:13Z",
+     "started_at": "2026-11-04T10:33:13Z",
+     "completed_at": "2026-11-04T10:33:12Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / closures-autofix",
+     "created_at": "2026-11-04T10:41:27Z",
+     "started_at": "2026-11-04T10:41:27Z",
+     "completed_at": "2026-11-04T10:41:27Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / ci-ratchet",
+     "created_at": "2026-11-04T10:48:08Z",
+     "started_at": "2026-11-04T10:48:10Z",
+     "completed_at": "2026-11-04T10:49:32Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / claims-autofix",
+     "created_at": "2026-11-04T10:48:08Z",
+     "started_at": "2026-11-04T10:48:08Z",
+     "completed_at": "2026-11-04T10:48:08Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / lane-proofs",
+     "created_at": "2026-11-04T10:48:08Z",
+     "started_at": "2026-11-04T10:48:08Z",
+     "completed_at": "2026-11-04T10:48:08Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "gate",
+     "created_at": "2026-11-04T10:49:32Z",
+     "started_at": "2026-11-04T10:49:35Z",
+     "completed_at": "2026-11-04T10:49:55Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "pr-contract",
+     "created_at": "2026-11-04T10:49:33Z",
+     "started_at": "2026-11-04T10:49:33Z",
+     "completed_at": "2026-11-04T10:49:32Z",
+     "conclusion": "skipped"
+    }
+   ]
+  },
+  {
+   "id": 41818271680,
+   "run_number": 4128,
+   "head_sha": "8e90d81443317f76f22602a89651f7ca17c633f9",
+   "created_at": "2026-11-04T11:03:14Z",
+   "status": "completed",
+   "conclusion": "failure",
+   "path": ".github/workflows/ci.yml",
+   "event": "push",
+   "head_branch": "main",
+   "jobs": [
+    {
+     "name": "prelude",
+     "created_at": "2026-11-04T11:03:15Z",
+     "started_at": "2026-11-04T11:03:18Z",
+     "completed_at": "2026-11-04T11:03:44Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "cancel-superseded",
+     "created_at": "2026-11-04T11:03:16Z",
+     "started_at": "2026-11-04T11:03:16Z",
+     "completed_at": "2026-11-04T11:03:15Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "refresh",
+     "created_at": "2026-11-04T11:03:16Z",
+     "started_at": "2026-11-04T11:03:16Z",
+     "completed_at": "2026-11-04T11:03:15Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "codeql / Analyze (actions)",
+     "created_at": "2026-11-04T11:03:44Z",
+     "started_at": "2026-11-04T11:03:47Z",
+     "completed_at": "2026-11-04T11:04:34Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "validate / validate-hacs",
+     "created_at": "2026-11-04T11:03:44Z",
+     "started_at": "2026-11-04T11:03:47Z",
+     "completed_at": "2026-11-04T11:04:23Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / mutation",
+     "created_at": "2026-11-04T11:03:44Z",
+     "started_at": "2026-11-04T11:03:47Z",
+     "completed_at": "2026-11-04T11:04:27Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "hassfest / hassfest",
+     "created_at": "2026-11-04T11:03:44Z",
+     "started_at": "2026-11-04T11:03:48Z",
+     "completed_at": "2026-11-04T11:04:06Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / env-matrix",
+     "created_at": "2026-11-04T11:03:44Z",
+     "started_at": "2026-11-04T11:03:47Z",
+     "completed_at": "2026-11-04T11:09:00Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / instrument-self-tests",
+     "created_at": "2026-11-04T11:03:44Z",
+     "started_at": "2026-11-04T11:03:48Z",
+     "completed_at": "2026-11-04T11:32:38Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / briefs",
+     "created_at": "2026-11-04T11:03:44Z",
+     "started_at": "2026-11-04T11:03:47Z",
+     "completed_at": "2026-11-04T11:04:35Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / wave-script",
+     "created_at": "2026-11-04T11:03:44Z",
+     "started_at": "2026-11-04T11:03:48Z",
+     "completed_at": "2026-11-04T11:04:31Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (python)",
+     "created_at": "2026-11-04T11:03:44Z",
+     "started_at": "2026-11-04T11:03:47Z",
+     "completed_at": "2026-11-04T11:29:34Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "codeql / Analyze (javascript-typescript)",
+     "created_at": "2026-11-04T11:03:44Z",
+     "started_at": "2026-11-04T11:03:48Z",
+     "completed_at": "2026-11-04T11:05:21Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / policy-docs",
+     "created_at": "2026-11-04T11:03:44Z",
+     "started_at": "2026-11-04T11:03:48Z",
+     "completed_at": "2026-11-04T11:08:01Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "kernel-points",
+     "created_at": "2026-11-04T11:03:44Z",
+     "started_at": "2026-11-04T11:03:44Z",
+     "completed_at": "2026-11-04T11:03:44Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / coverage",
+     "created_at": "2026-11-04T11:03:44Z",
+     "started_at": "2026-11-04T11:03:47Z",
+     "completed_at": "2026-11-04T11:33:17Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / browser",
+     "created_at": "2026-11-04T11:03:44Z",
+     "started_at": "2026-11-04T11:03:47Z",
+     "completed_at": "2026-11-04T11:08:01Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / typing",
+     "created_at": "2026-11-04T11:03:44Z",
+     "started_at": "2026-11-04T11:03:48Z",
+     "completed_at": "2026-11-04T11:05:11Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / record",
+     "created_at": "2026-11-04T11:03:44Z",
+     "started_at": "2026-11-04T11:03:47Z",
+     "completed_at": "2026-11-04T11:04:18Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "governance / delivery-status-publish",
+     "created_at": "2026-11-04T11:03:44Z",
+     "started_at": "2026-11-04T11:03:48Z",
+     "completed_at": "2026-11-04T11:04:20Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / closures",
+     "created_at": "2026-11-04T11:03:44Z",
+     "started_at": "2026-11-04T11:03:48Z",
+     "completed_at": "2026-11-04T11:42:17Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / arch-instrument",
+     "created_at": "2026-11-04T11:03:44Z",
+     "started_at": "2026-11-04T11:03:47Z",
+     "completed_at": "2026-11-04T11:36:08Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / fast (3.14)",
+     "created_at": "2026-11-04T11:03:44Z",
+     "started_at": "2026-11-04T11:03:47Z",
+     "completed_at": "2026-11-04T11:37:12Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "arch-score",
+     "created_at": "2026-11-04T11:03:44Z",
+     "started_at": "2026-11-04T11:03:44Z",
+     "completed_at": "2026-11-04T11:03:44Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-status",
+     "created_at": "2026-11-04T11:03:45Z",
+     "started_at": "2026-11-04T11:03:45Z",
+     "completed_at": "2026-11-04T11:03:44Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "budget-raise-gate",
+     "created_at": "2026-11-04T11:03:45Z",
+     "started_at": "2026-11-04T11:03:45Z",
+     "completed_at": "2026-11-04T11:03:44Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / closure-scope",
+     "created_at": "2026-11-04T11:03:45Z",
+     "started_at": "2026-11-04T11:03:45Z",
+     "completed_at": "2026-11-04T11:03:44Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "governance / delivery-status",
+     "created_at": "2026-11-04T11:03:45Z",
+     "started_at": "2026-11-04T11:03:45Z",
+     "completed_at": "2026-11-04T11:03:44Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / nightly-ha",
+     "created_at": "2026-11-04T11:03:45Z",
+     "started_at": "2026-11-04T11:03:45Z",
+     "completed_at": "2026-11-04T11:03:44Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / replay",
+     "created_at": "2026-11-04T11:03:45Z",
+     "started_at": "2026-11-04T11:03:45Z",
+     "completed_at": "2026-11-04T11:03:44Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-autofix",
+     "created_at": "2026-11-04T11:04:29Z",
+     "started_at": "2026-11-04T11:04:29Z",
+     "completed_at": "2026-11-04T11:04:28Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / mutation-pins",
+     "created_at": "2026-11-04T11:04:29Z",
+     "started_at": "2026-11-04T11:04:29Z",
+     "completed_at": "2026-11-04T11:04:28Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / coverage-ratchet",
+     "created_at": "2026-11-04T11:33:17Z",
+     "started_at": "2026-11-04T11:33:20Z",
+     "completed_at": "2026-11-04T11:33:31Z",
+     "conclusion": "success"
+    },
+    {
+     "name": "tests / graders-head-copy",
+     "created_at": "2026-11-04T11:33:17Z",
+     "started_at": "2026-11-04T11:33:17Z",
+     "completed_at": "2026-11-04T11:33:17Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / claims-autofix",
+     "created_at": "2026-11-04T11:37:13Z",
+     "started_at": "2026-11-04T11:37:13Z",
+     "completed_at": "2026-11-04T11:37:13Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / lane-proofs",
+     "created_at": "2026-11-04T11:37:13Z",
+     "started_at": "2026-11-04T11:37:13Z",
+     "completed_at": "2026-11-04T11:37:13Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "tests / ci-ratchet",
+     "created_at": "2026-11-04T11:42:17Z",
+     "started_at": "2026-11-04T11:42:26Z",
+     "completed_at": "2026-11-04T11:44:14Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "tests / closures-autofix",
+     "created_at": "2026-11-04T11:42:18Z",
+     "started_at": "2026-11-04T11:42:18Z",
+     "completed_at": "2026-11-04T11:42:17Z",
+     "conclusion": "skipped"
+    },
+    {
+     "name": "gate",
+     "created_at": "2026-11-04T11:44:15Z",
+     "started_at": "2026-11-04T11:44:18Z",
+     "completed_at": "2026-11-04T11:44:42Z",
+     "conclusion": "failure"
+    },
+    {
+     "name": "pr-contract",
+     "created_at": "2026-11-04T11:44:15Z",
+     "started_at": "2026-11-04T11:44:15Z",
+     "completed_at": "2026-11-04T11:44:15Z",
+     "conclusion": "skipped"
+    }
+   ]
+  }
+ ]
+}
diff --git a/dev/audit/rca/r10-ci-critpath-3.md b/dev/audit/rca/r10-ci-critpath-3.md
new file mode 100644
index 000000000..f3b04d8e1
--- /dev/null
+++ b/dev/audit/rca/r10-ci-critpath-3.md
@@ -0,0 +1,301 @@
+# R10-RCA-CI-CRITPATH-3: a timed gate graded which host class the runs drew
+
+The root-cause seat for the third `GREW critical_path_minutes` on `main`, extended to the
+fourth. It ran beside the fixers of `r10-hotfix-ci-critpath-3` and `-4` and not inside them
+(`dev/governance/roles/root-cause.md`), and touches none of their files. Every time below is
+UTC. The replay is `dev/audit/harnesses/r10_rca_ci_critpath_3/replay.py`, offline, under a
+second. It grades each red with `tests/ci_ratchet.py` as of the red commit itself
+(`git show <sha>:tests/ci_ratchet.py`, imported by spec), never the live file. Its fixtures,
+beside it, were read from the Actions API:
+
+- `runs.json` (11-04 05:20): 31 completed `ci.yml` push runs on `main`, numbered 3775..4056,
+  with their jobs. `run_minutes` grades 29 of them; two return None. The fixture omits the
+  cancelled runs 3770–3772 and 4036–4045.
+- `runs_red4.json` (11-04 14:00): every `ci.yml` push run on `main` numbered 4009..4128,
+  with the cancelled ones, which is the fourth red's 16-run window and the one before it.
+- `ci_logs.json` (11-04 14:10): the `lane plan:` lines of two closures jobs, the per-script
+  seconds of three `tests / fast (3.14)` jobs, and the runner image of every successful
+  closures and fast (3.14) job in runs 3770..4128.
+
+**Defect, third red.** `tests / ci-ratchet` on `8f286293b` (run 41397326281, job
+125133539981, 06:40:46) printed `GREW critical_path_minutes: 36.5 (budget 34.267, band 1.3)`.
+Every later push to `main` read the same verdict through `c3a279e32`. The merge was
+`#3162`, seven delivery-row `.md` files, and cannot move CI work. Neither could the two
+earlier reds: `05c0d6d5d` (seven delivery rows) and `f3ffb1c63`, whose own fix says that
+"no merge grew the work".
+
+**Defect, fourth red.** After `#3180` replaced the statistic, `tests / ci-ratchet` on
+`8e90d8144` (run 41818271680, job 126550827525, 11:44:11) printed
+`GREW critical_path_minutes: 29.067 (budget 21.983, band 1.3)`. The merge was `#3182`. Its
+diff adds one entry to `tests/closures.json`, and the planned path is unchanged by it
+(replay step 6). Replay steps 4 and 5 show that the grade moved with the host draw, not with
+the work. Section 2b covers it.
+
+## 1. Cause, reproduced
+
+- **The grade reproduces exactly.** Replay step 1 grades the window `ci-ratchet` read at
+  `8f286293b`: the 7 runs before it plus its own run, still in progress. It uses that
+  commit's `run_minutes` and `critical_path_minutes`. The result is 36.5, GREW against
+  35.567.
+- **The work did not move.** `python3 tests/closure.py lane-plan --all-scripts --lanes 3`
+  reads `tests/closures.json`'s recorded seconds. Its longest lane is 1332.8 s at
+  `9f800cdca` (10-25). It is 1345.7 s at `b8a027974` (10-31), at `c7aa12165` (the last
+  green), at `c3a279e32` (the last red-3 push) and at `8e90d8144` (replay step 6). On CI the
+  closures lane printed `lane plan: 3 lane(s) for 34 script(s), bound 3` with lane totals
+  1345.6 / 1345.7 / 1345.6 s in two jobs (replay step 3, from `ci_logs.json`). One job took
+  38.2 min (job 125121503116, run 3870). The other took 20.6 min (job 125653313138,
+  run 4055). These totals are recorded seconds and read no clock. That they agree shows the
+  plan was the same in both runs. It does not show how fast either host was.
+- **The host slowed every script.** The closures job logs print no per-script seconds, so
+  this is measured on the fast lane, whose logs do. Fast (3.14) job 125436393198 (run 4009,
+  20.4 min) and job 126534731510 (run 4128, 33.4 min) ran the same 33 scripts with none
+  added. Summed script time was 1824 s against 3137 s, ×1.72. Every one of the 14 scripts
+  of at least 10 s was slower, by a ratio of 1.26..3.09 (replay step 5). For example,
+  `features.py` took 359 s against 673 s, and `stress.py` 187 s against 367 s. Neither log
+  prints a CPU model, so the host class has no name here. This per-script comparison
+  crosses an image change: run 4009 ran image 20261025.179.1 and run 4128, the only
+  fast (3.14) job on image 20261101.186.1, ran that one, so the ×1.72 exhibit is confounded
+  with the image and by itself does not separate host from image. The claim that the image
+  does not separate the classes rests on the wider set: the fast (3.14) jobs of runs
+  3770..4116 all ran image 20261025.179.1, at 17.7..34.9 min, and run 4035 of that image
+  took 27.3 min against run 4009's 20.4 min. No per-script log was kept for run 4035, so
+  the same-image slow comparison is by job minutes only.
+- **The lanes are bimodal, and the 8-run median flips with the mixture.** In the 29 graded
+  runs of `runs.json`, `tests / closures` took either 18.6–29.3 min or 33.7–40.0 min.
+  `tests / fast (3.14)` was split the same way, at about 18–25 and 30–35 min. Replay step 2
+  counts slow closures draws among the runs the median actually reads. It finds 3 windows
+  with under half slow (max median 33.767, ok) and 6 windows with over 70 % slow (min median
+  39.667, GREW). The windows in between are mixed because the fast lane draws its host
+  independently. From run 3865 (05:24 on 11-02) the slow class won most draws: 13 of the
+  next 19 closures jobs were slow, against 5 of the 12 before. The median moved from the
+  fast mode to the slow mode, and the work moved by zero.
+- **What else the cause reaches.** `critical_path_minutes` is the only timing row in any
+  `*_budgets.json`. That is still true at `8e90d8144`. The other rows of
+  `tests/ci_budgets.json` are counts (`script_runs_*`, `archscore.*`).
+  `orchestrator_tick.py:381` reads the same budget only to bound a WAITING line, and grades
+  nothing. So the class stops at this one row, and it has hit that row four times.
+
+| red | onset (push) | hotfix merged | red for | the hotfix's reading |
+|---|---|---|---|---|
+| 1 | `f3ffb1c63` 10-25 20:21 | `#2839` 10-26 00:58 | 4.6 h | runner queue, so grade work instead of wall |
+| 2 | `05c0d6d5d` 10-31 10:43 | `#3045` 11-01 14:39 | 27.9 h | 8-run median spread, so a 1.3 band |
+| 3 | `8f286293b` 11-02 06:01 | `#3180` 11-04 09:26 | 51.4 h | host draw, so price each job at its fastest of 16 runs |
+| 4 | `8e90d8144` 11-04 11:03 | open (`r10-hotfix-ci-critpath-4` dispatched 11:46) | ≥ 2.9 h at 14:00 | — |
+
+Red 3 ended under its own statistic before `#3180` merged. Run 4080 (`a9c2f90fc`, pushed
+08:13) graded 35.1 against 35.567, because the median fell back with the draw. On that rule
+the red lasted 50.2 h. The table keeps the rule the earlier rows use: onset to hotfix merged.
+
+Each hotfix was correct about the symptom it was shown. The first three each left the gate
+grading elapsed time on hosts the repository does not choose. Red 4 is that cause's next
+instance.
+
+## 2. Process state: (c) — followed, and it did not produce the intended result
+
+The process is the ratchet's own calibration rule, as the red commit ran it
+(`git show 8f286293b:tests/ci_ratchet.py`, lines 41–52 of the module docstring and the
+`BAND_KEYS` comment at lines 106–111). It grades the 8-run median, records the p90 of a
+wider window, and sizes the band "at the measured maximum |8-run median − window median|
+over 145 runs, 1.3", "never padded". Hotfix 2 followed it to the digit. It reproduced the
+p90 34.267 exactly and set the band at the measured 1.300.
+
+It did not produce the intended result because the measure assumes unimodal noise around
+the work. The lane timings are a two-class mixture. Under a mixture, a median's spread
+measured in a sample where the slow class stays under half says nothing about a day when
+it goes over half. The bimodality was already in the calibration-era data, so this is not
+a precondition that changed underneath the process (d). Hotfix 1's own message says the
+work was "flat at 20.1..34.65 min" over 40 runs. In this sample both modes appear before
+the step: runs 3779–3838 hold both 21–25 and 34–39 min closures jobs. It is not (b), since
+nothing was skipped. A firmer instruction would only repeat the calibration that was
+followed.
+
+## 2b. The fourth red: the same state, one statistic later
+
+**#3180 followed the calibration rule too.** It recorded 21.983 as the largest of the 25
+sixteen-run windows over 40 runs. It kept the band at 1.3 against a measured
+window-to-window excess of 0.55 (its reason in `tests/ci_budgets.json` at `8e90d8144`). Its
+statistic, `window_work_minutes`, prices each job at its fastest successful run among the
+newest 16. That assumes every heavy job draws at least one fast host per 16 runs. The
+module named the failure mode itself: "fifteen of sixteen runs drawing slow moves it as
+growth would" (`git show 8e90d8144:tests/ci_ratchet.py`, the `window_work_minutes`
+docstring at line 662).
+
+**What the data show** (replay steps 4 and 5):
+
+- The record's largest window priced fast (3.14) at 17.73 min. The window at `616868bdc`
+  (runs 4009..4116) priced it at 20.38, on run 4009, and graded 22.367, which is ok. That
+  matches the 22.367 the CI job printed there.
+- One push later the window at `8e90d8144` (runs 4015..4128) had lost run 4009. Its 15
+  successful fast (3.14) runs all took 27.3 min or more. The price became 27.33 (run 4035),
+  and the chain `prelude` 0.37 + fast (3.14) 27.33 + `ci-ratchet` 1.37 reads 29.067, GREW.
+  Nothing grew: replay step 5 shows the same 33 scripts, each slower on the slow draw.
+- Run 4009 was the last fast-host draw of the fast lane. Fast (3.14) ran under 26 min in 14
+  of 28 runs from 3770 to 4009, and in 0 of 16 after. In the same 16 runs the closures lane
+  still drew under 27 min 7 times. If draws were independent at the earlier rate of 1 in 2,
+  0 of 16 would have a probability of 0.5^16 ≈ 1.5 × 10⁻⁵. So the fast lane's draws are not
+  independent from run to run. The runner image is the same throughout. What does correlate
+  them is not in the logs.
+
+**State: (c).** The rule was followed and the measure was still wrong for a mixture. The
+40-run calibration sample never held a 16-run stretch without a fast fast-lane draw: the
+newest recorded window still contained run 4009. So the sample could not price the case
+the docstring named. The draw pattern did change after 4009, and one could read that as (d).
+But the failure was predicted in the statistic's own text, and the calibration was the
+process that should have tested it. The countermeasure is the same as in section 4: stop
+grading elapsed time. It is not a fifth recalibration.
+
+## 3. Cost test, re-taken at four occurrences
+
+`cost(countermeasure, recurring) < cost(defect) × P(recurrence)`, in wall-clock.
+
+- **P(recurrence)** is measured from the table: 4 onsets in 9.61 days (10-25 20:21 →
+  11-04 11:03), which is 0.42 a day. The gaps were 5.6, 1.8 and 2.2 days, so the rate is
+  not falling.
+- **cost(defect)** has two parts. The first is red-main time: 4.6, 27.9 and 51.4 h for the
+  closed reds, a mean of 28.0 h. With red 4 at its lower bound of 2.9 h the mean is
+  ≥ 21.7 h. The second is three seats per occurrence: fixer, review and root-cause. The red
+  also blinds the gate. 19 pull requests merged onto `main` while it was red on 11-02
+  (06:41–21:10), and any real growth among them reads as the same GREW. Taking only the red
+  time gives ≥ 21.7 h × 0.42 a day ≈ 9.0 h of red main a day.
+- **cost(countermeasure, recurring)** is the planned critical path below. The whole replay,
+  including a `lane-plan` subprocess and two git reads, takes 0.31 s here. The run count is
+  rounded up to 300 a day: the run numbers moved 4056 − 3775 = 281 in the 28.6 h between
+  those runs (11-01 23:46 → 11-03 04:23), about 236 a day. That makes about 90 s a day.
+
+90 s a day against about 9.0 h a day: the test passes by more than two orders of magnitude.
+
+## 4. Countermeasure — proposed, owner's decision, not landed
+
+This changes what a ratchet row grades, and that is policy (CLAUDE.md rule 2). It also
+touches `tests/ci_ratchet.py` and `tests/ci_budgets.json`, which the hotfix seats own. So it
+is a draft for the owner, aimed at state (c): replace the measure, not the instruction.
+
+**Grade the planned critical path, not elapsed minutes.** The new row is the longest lane of
+`closure.lane_plan(--all-scripts, 3 lanes)` over `tests/closures.json`'s recorded seconds.
+Today it reads 1345.7 s. `critical_path_minutes` would be kept as a printed observation that
+does not gate, or as a nightly trend with a band sized to the mixture.
+
+- **It reads no clock.** Its only input is the recorded-seconds table. CI printed the same
+  lane totals in a 38.2-min and a 20.6-min closures job (replay step 3). Replay step 3's
+  repeat is a determinism check only. It calls a pure function twice on one input, so it
+  cannot fail and controls nothing about hosts.
+- **It detects growth.** Add 300 s to `tests/stress.py`'s recorded seconds and the planned
+  path goes 1345.7 → 1445.7 (replay step 3).
+- **It is diff-attributable and runs at PR time.** The value moves only with a
+  `tests/closures.json` change. That makes it a cheaper, earlier detector:
+  `tools/pr/prepr.sh` could grade it in under a second. The timed row runs only on a push to
+  `main` (`tests.yml:2265-2267`), so it can only ever go red after the merge.
+
+**How it relates to what #3180 landed: complementary, not superseded.** `#3180` kept a timed
+gate and made it narrower. It goes red only when a heavy job draws no fast host in 16 runs,
+where the median went red when the slow class took half. Red 4 is exactly that case, 15 of
+15. The draft removes the host from the grade instead.
+
+- **Would it have prevented red 4?** As the gate, yes. The planned path read 1345.7 s at red
+  3 and at red 4 (replay step 6), so nothing would have gone red.
+- **Would it have caught growth there?** No. Red 4 was carried by the fast lane, and the
+  draft grades only the closures lane (limitation 1 below). Had the fast lane really grown,
+  the draft would have missed it, and the non-gating observation would have shown it.
+- **What #3180 still adds beside it.** As that observation, a fastest-of-16 reading is a
+  better trend than a median. A move in it is worth a look, but it must not gate.
+
+What the draft does not cover, stated so nobody over-reads it:
+
+1. **Only the closures lane.** The fast lane's work would need the same recorded-seconds
+   table before it could join. Red 4 sat in that lane.
+2. **The recordings lag real growth.** Recorded seconds change only when a branch
+   re-records (`stable_seconds` smooths them). A script that slows without a re-record is
+   invisible until one happens.
+3. **Runner-level regressions.** A setup step growing, for example, never reaches the
+   recordings. The timed observation is what would still show these.
+
+If the owner refuses: the alternative is to keep a timed gate and size it from a sample that
+holds the worst draw. Red 3's windows reach a median of 40.909 on unchanged work, 6.6 min
+over that budget. Red 4's statistic read 7.08 over its record with the fast lane alone
+mispriced by 9.6 min (27.33 against 17.73). A margin that wide would hide that much real
+growth indefinitely. That trade is worse than grading the plan, and it is why this seat
+does not propose it.
+
+## 5. Why `main` sat red with no seat reacting (red 3)
+
+Measured from git only. The counts below are over unique commits on every `origin` ref
+fetched 11-04 14:05 (`git log --remotes --since … --until … --format='%H %s' | sort -u`),
+matched by subject: ` dispatch:`, `roster_edit`, and
+`state: … regenerated (state_docs.py)`. PR merges are first-parent `Merge pull request`
+commits on `origin/main`. The tick board itself is stdout-only and was never persisted:
+`heartbeat/orchestrator` holds one `TICK-PASS` in all its history, at 11-04 05:19. So this
+seat cannot confirm from the record what any pass of the board printed.
+
+| phase | interval | what the record shows |
+|---|---|---|
+| driving, main red | 11-02 06:40 → 21:06 (14.4 h) | 108 `dispatch:` commits (a dispatch writes two, as this seat's own did), 31 `roster_edit`, 19 PR merges onto red `main`; no dispatch for the red (the only ratchet-named dispatch is `fixer-r10-machinery-ratchets`, an unrelated group) |
+| not driving | 11-02 21:06 → 11-04 05:13 (32.1 h) | no dispatch, roster edit or merge by any seat; only bot commits (`#3178` record merge 00:48, `ci: record nightly kills` 04:23) and `state_docs.py` regenerations about twice an hour (no gap over 2 h), run by a loop still alive |
+| dispatch | 11-04 05:13 | `dispatch/fixer-r10-hotfix-ci-critpath-3` and this seat |
+
+The brief's "about 25 h" runs from the last red push run (`c3a279e32`, concluded
+11-03 04:58) to the dispatch, which is 24.3 h. Red to dispatch was 46.5 h in all.
+
+- **The expedite rule existed.** `dev/governance/roles/nudge.md:105` says: "An expedite item
+  (red main, quota exhaustion, outage, security) bypasses the caps, one at a time." In the
+  driving phase it was not acted on, while about 54 other dispatches went out. Each one is a
+  pair of commits.
+- **The durable record cannot tell (b) from (c).** The only durable per-pass artifact is the
+  state docs, regenerated 108 times between 11-01 18:00 and 11-04 07:00. They carry no
+  main-red line: `FLOW-BOARD.md`'s `ci-red:N` counts pull requests in the blocked mix
+  (8a867118f, 12:04 on 11-02; 41769608c, 12:30 on 11-03). The board line
+  `REQUIRED not green … a red main admits nothing` (`orchestrator_tick.py:1393`) is printed
+  with `flag=True` and goes nowhere else. There is no record of whether the driver saw it and
+  went on (b) or never had it in front of them (c). This seat records the state as
+  **undetermined between (b) and (c)**, not as (b).
+- **The not-driving phase owes nothing.** With no driver, nothing merged and nothing could:
+  the bottleneck was the absent session, red or not. The red added no cost beyond delaying
+  its own fix. A countermeasure there would have to drive a session, which is outside this
+  defect. Recorded refusal: cost(defect) is about 0 for this phase.
+- **For the driving phase**, one draft for the owner serves either state. The dispatch gate
+  that already runs before every dispatch (`tools/audit/seat/pr_cap.py dispatch-gate`) would
+  refuse a non-expedite dispatch while `main`'s required checks are red. That turns the
+  expedite rule into a stop instead of a reading. Its standing cost is one check-runs read
+  per dispatch, which the tick already makes. Its value: in this occurrence it would have
+  stopped the first of about 54 dispatches at 06:40 and forced the hotfix dispatch then,
+  rather than 46.5 h later. Not built: it changes what a seat must do, so it is policy.
+- **Red 4 did not repeat this.** The GREW printed at 11:44:11, and
+  `dispatch/fixer-r10-hotfix-ci-critpath-4` was committed at 11:46:27, 2 min later.
+
+## 6. Also found: no root-cause record reached the first two reds
+
+`grep -rn 'CRITPATH' dev/audit/rca` found nothing before this file. The delivery rows of
+`#2839` and `#3045` record no cause or process state. The cause is a reach gap in the
+enforcement. `defect-root-cause.md` enforces its second trigger at "a check that went red on
+a commit in the branch", and the fix reviewer checks it. `tests / ci-ratchet` runs only on a
+push to `main` (`tests.yml:2265-2267`), so it can never be red on a branch, and the enforced
+trigger cannot reach any red from a push-only check. This document is that check's first
+root-cause record. Whether the rule should name push-only checks is the owner's call.
+
+## 7. What this record does not cover
+
+- **Reds 1 and 2 are not re-measured.** Their onsets, hotfix merges and readings come from
+  git and their hotfix messages, not from a fixture.
+- **Why the fast lane stopped drawing fast hosts after run 4009.** The logs carry no CPU
+  model, and the image is the same before and after. The record shows that the draws are
+  correlated, not by what.
+- **Red 4's end and its hotfix.** Both are the orchestrator's. When this was written
+  (11-04 14:00) `main` was still red at `8e90d8144`. This record proposes nothing for that
+  hotfix's code.
+- **The planned path for the fast lane.** It does not exist yet (section 4, limitation 1).
+- **Red 4's driving-phase behaviour.** Only its dispatch latency is measured; no section-5
+  table is taken for it.
+
+## Return
+
+- **State:** (c) for reds 3 and 4: a calibration followed and a measure wrong for a
+  two-class host mixture. For red 3's 14.4 h driving phase, undetermined between (b) and
+  (c). For its 32.1 h undriven phase, a recorded refusal (cost ≈ 0).
+- **Cost test:** passes at four occurrences. About 90 s a day standing against about 9.0 h a
+  day of red main (P = 0.42 a day, mean red ≥ 21.7 h).
+- **Countermeasures:** two drafts for the owner, neither landed. First, grade the planned
+  closures critical path at PR time and keep elapsed minutes non-gating. This complements
+  `#3180`, it is not superseded by it, and it would have kept red 4 off `main`. Second,
+  `dispatch-gate` refuses non-expedite dispatches while `main`'s required checks are red.
+- **Self-correction against the first draft of this record:** it gave the first three onsets
+  as 8.4 days apart and P = 0.36 a day. They are 7.40 days apart: 10-25 20:21 → 11-02 06:01,
+  with gaps of 5.6 and 1.8 days, not 6.6 and 1.8.
diff --git a/dev/programme/delivery/3189.md b/dev/programme/delivery/3189.md
new file mode 100644
index 000000000..e01df9afb
--- /dev/null
+++ b/dev/programme/delivery/3189.md
@@ -0,0 +1 @@
+- [#3189](https://github.com/tvofi/heatpump_optimizer/pull/3189) — **open**, R10-RCA-CI-CRITPATH-3: rca ci critpath 3 (R10-RCA-CI-CRITPATH-3)
diff --git a/tests/closures.json b/tests/closures.json
index dfa5dbfcb..168c532e4 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4015,6 +4015,7 @@
    "dev/audit/harnesses/r10_pusher_reap_launch_mutants.sh",
    "dev/audit/harnesses/r10_raise_paths.sh",
    "dev/audit/harnesses/r10_ratio_anchor.py",
+   "dev/audit/harnesses/r10_rca_ci_critpath_3/replay.py",
    "dev/audit/harnesses/r10_rca_name_kept_plant.py",
    "dev/audit/harnesses/r10_readme_marketplace_pipeline.mjs",
    "dev/audit/harnesses/r10_recarry_head.py",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
