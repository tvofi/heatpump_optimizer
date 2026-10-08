diff --git a/tests/closures.json b/tests/closures.json
index ee854191..8eb15f9d 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3155,24 +3155,21 @@
  "inert_reads": {
   "tests/harness_headers.py": [
    "LICENSE",
-   "dev/audit/harnesses/boost_replay_fork_parity.py",
    "dev/audit/harnesses/ci-version-edit/pr_contract_shapes.py",
    "dev/audit/harnesses/ci-version-edit/recheck_stamp_forgery.py",
-   "dev/audit/harnesses/ci_script_seconds.py",
    "dev/audit/harnesses/d1_s3_02_queued_apply.py",
    "dev/audit/harnesses/d907_kernel_band.py",
    "dev/audit/harnesses/dual_path.py",
-   "dev/audit/harnesses/eg_b7_seam_hubs.py",
    "dev/audit/harnesses/h8_single_scenario.py",
    "dev/audit/harnesses/h9_basin_coverage.py",
    "dev/audit/harnesses/hpo_ci_container_setup.sh",
    "dev/audit/harnesses/j5_gil.py",
    "dev/audit/harnesses/k1725_blas_kernel_gap.py",
    "dev/audit/harnesses/r9_fr3_family_consumer.mjs",
-   "dev/audit/harnesses/r9_ro12_batch_mutants.sh",
    "dev/audit/harnesses/scale_writer_seams.py",
    "dev/audit/harnesses/solve_inputs_parity.py",
    "dev/audit/harnesses/thermal_parity.py",
+   "dev/audit/harnesses/ux5_idle_codes.py",
    "dev/audit/rounds/round3/D10/coverage_rule.sh",
    "dev/audit/rounds/round3/D10/strict_typing_rule.sh",
    "dev/audit/rounds/round3/D4/card_states_geometry.mjs",
@@ -3682,8 +3679,12 @@
    "dev/audit/waves/w5-g5-195-coverage/coverage_suite.sh",
    "dev/audit/waves/w5-g5-195-coverage/mutation_probe.py",
    "dev/programme/register/audit-2026-09.md",
+   "dev/audit/harnesses/eg_b7_seam_hubs.py",
    "tools/audit/repo_root.mjs",
-   "tools/audit/repo_root.sh"
+   "tools/audit/repo_root.sh",
+   "dev/audit/harnesses/boost_replay_fork_parity.py",
+   "dev/audit/harnesses/ci_script_seconds.py",
+   "dev/audit/harnesses/r9_ro12_batch_mutants.sh"
   ],
   "tests/doc_claims.py": [
    "docs/site/docs.css"
