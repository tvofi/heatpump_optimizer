# Review packet #3602
head: bca2e138252ed1176e517aca6f3bcb47588cd2af
base: 367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=133336314793 success
arch-score / arch-score id=133381278703 success
arm id=133334268669 skipped
budget-raise-gate / budget-raise-gate id=133381278685 success
cancel-superseded id=133381277958 success
codeql id=133381353598 skipped
codeql / Analyze (actions) id=133335712564 success
codeql / Analyze (javascript-typescript) id=133335712184 success
codeql / Analyze (python) id=133335712363 success
gate id=133381277820 success
governance id=133381278807 skipped
governance / env-matrix id=133335712379 success
governance / instrument-self-tests id=133335712541 success
governance / policy-docs id=133335712436 success
governance / record id=133335715644 skipped
governance / wave-script id=133335712501 success
hassfest id=133381354406 skipped
hassfest / hassfest id=133335712626 success
kernel-points id=133381336606 skipped
pr-contract id=133381280521 skipped
pr-contract / pr-contract id=133379544698 success
prelude id=133381277549 success
refresh id=133381372244 success
sweep-self id=133381786266 skipped
tests id=133381341054 skipped
tests / arch-instrument id=133336415833 success
tests / briefs id=133335712721 success
tests / browser id=133336415927 success
tests / ci-ratchet id=133358991672 skipped
tests / claims-autofix id=133357766976 skipped
tests / closure-scope id=133335712676 success
tests / closures id=133336415987 success
tests / closures-autofix id=133351939430 skipped
tests / coverage id=133336416004 success
tests / coverage-ratchet id=133358989668 success
tests / fast (3.14) id=133336415776 success
tests / graders-head-copy id=133358989595 success
tests / lane-proofs id=133358989531 success
tests / mutation id=133335712520 success
tests / mutation-autofix id=133379520199 skipped
tests / mutation-pins id=133379504274 skipped
tests / nightly-ha id=133336418729 skipped
tests / nightly-status id=133335712727 failure
tests / replay id=133336415994 failure
tests / typing id=133336415617 success
validate id=133381348849 skipped
validate / validate-hacs id=133335712221 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item d4d3c33a: R11-OUTSIDE-HONEST-STARTS-RUNS
NOTE body item 0661d6fd: R11-OUTSIDE-HONEST-STARTS-RUNS
NOTE body item 6f871e1c: R11-OUTSIDE-HONEST-STARTS-RUNS
NOTE body item b442ffd0: dismissed:groups done, no live brief
NOTE body item 33dab917: dismissed:recorded in this pull request
NOTE body item a1470143: dismissed:stress budget holds at both ends
NOTE body item d6509d5b: dismissed:built here, the measurement is in this body and in the harness's `gradient` mode
NOTE body item 0b91ed5e: dismissed:built here
NOTE body item 71b9ba33: R11-OUTSIDE-HONEST-STARTS-RUNS
NOTE body item 83d7ca8c: R11-OUTSIDE-HONEST-STARTS-RUNS
NOTE body item 7d014dd5: dismissed:measured here, the figure and its null are in this body and the harness's `stress` mode re-takes them
NOTE body item 06bac6b6: dismissed:stated in this body, the note asks for no more
NOTE body item 4f5d2d4f: dismissed:not designed here
NOTE body item a4ac1e10: R11-PRE-TOOLCHAIN-PIN
NOTE body item 3bf377c4: dismissed:a process observation for the round-end triage, with no stage brief it changes
NOTE body item 6157844a: R11-OUTSIDE-HONEST-STARTS-RUNS
NOTE body item 7e48b773: R11-OUTSIDE-HONEST-STARTS-RUNS
NOTE body item ab721197: R11-OUTSIDE-HONEST-STARTS-RUNS
NOTE body item a01a82b7: dismissed:one dispatch's wording, reported here for the orchestrator
CARRY-AUDIT: 19 finding item(s): 19 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git diff d73ec97da1 HEAD --stat -- custom_components
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r11_honest_starts_runs.py kernels
             `dev/audit/harnesses/r11_honest_starts_runs.py` is in the tree at this head
  ok         OPENBLAS_CORETYPE=SkylakeX GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=5825e1346c ./tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/features.py
             `tests/features.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/deployment_shape.py
             `tests/deployment_shape.py` is in the tree at this head
  ok         OPENBLAS_CORETYPE=SkylakeX PYTHONPATH=tests/hastub python3 tests/features.py
             `tests/features.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff 6077c3e1ab
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff a39627da59
             `tests/closure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r11_honest_starts_runs.py fixtures
             `dev/audit/harnesses/r11_honest_starts_runs.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r11_honest_starts_runs.py c1
             `dev/audit/harnesses/r11_honest_starts_runs.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r11_honest_starts_runs.py gradient
             `dev/audit/harnesses/r11_honest_starts_runs.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/stress.py
             `tests/stress.py` is in the tree at this head
  ok         python3 tests/gate_lock.py take --label
             `tests/gate_lock.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r11_honest_starts_runs.py stress
             `dev/audit/harnesses/r11_honest_starts_runs.py` is in the tree at this head
  ok         tests/stress.py
             `tests/stress.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r11_honest_starts_runs.py descents
             `dev/audit/harnesses/r11_honest_starts_runs.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 23cc7b8e1d004279d99bd59f3d2bd2a8f885b426
             `tests/env_drift.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff 23cc7b8e1d
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py --base origin/main
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/features.py
             `tests/features.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff ceced961d1
             `tests/closure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/env_drift.py --all a340b4ac63
             `tests/env_drift.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_setpoint_power.py
             `dev/audit/harnesses/r10_setpoint_power.py` is in the tree at this head
  ok         tests/optimality.py
             `tests/optimality.py` is in the tree at this head
  ok         tests/golden.py
             `tests/golden.py` is in the tree at this head
  ok         tests/backtest.py
             `tests/backtest.py` is in the tree at this head
  ok         tests/validate.py
             `tests/validate.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py
             `tools/pr/ci_predict.py` is in the tree at this head
  unverified git grep -n -w -E "cycling_penalty|cycling_penalty_batch|count_compressor_starts|_relaxed_starts|_scores_rounded" -- . ':!dev/archive' ':!dev/audit/rounds' ':!dev/audit/rca' ':!dev/audit/waves' ':!docs/design' ':!dev/audit/harnesses/r10_mutant_skip'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         node tools/policy/brief_lint.mjs
             `tools/policy/brief_lint.mjs` is in the tree at this head
  unverified git grep -n "round9/D3/s2/witness" -- . ':!dev/audit/rounds'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 34 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_humidity_with_data.BOOLOP.445c4ae4.json b/tests/mutation_ledger/killed_by/coordinator.py/_humidity_with_data.BOOLOP.445c4ae4.json
new file mode 100644
index 0000000000..7b38f4880a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_humidity_with_data.BOOLOP.445c4ae4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_humidity_with_data BOOLOP 445c4ae4",
+  "killed_by": "tests/features.py",
+  "old": "    return series if series.size and bool(np.any(np.isfinite(series))) else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return series if series.size or bool(np.any(np.isfinite(series))) else None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_humidity_with_data.RETURN_DEL.445c4ae4.json b/tests/mutation_ledger/killed_by/coordinator.py/_humidity_with_data.RETURN_DEL.445c4ae4.json
new file mode 100644
index 0000000000..7ab35b9784
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_humidity_with_data.RETURN_DEL.445c4ae4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_humidity_with_data RETURN_DEL 445c4ae4",
+  "killed_by": "tests/features.py",
+  "old": "    return series if series.size and bool(np.any(np.isfinite(series))) else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.GUARD_OFF.22c1b1ab.json b/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.GUARD_OFF.22c1b1ab.json
new file mode 100644
index 0000000000..059f58fec6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.GUARD_OFF.22c1b1ab.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:switch_weights_batch GUARD_OFF 22c1b1ab",
+  "killed_by": "tests/features.py",
+  "old": "    if level is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/running_now.GUARD_OFF.bf27f328.json b/tests/mutation_ledger/killed_by/duty_switch.py/running_now.GUARD_OFF.bf27f328.json
new file mode 100644
index 0000000000..2eb28572f9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/running_now.GUARD_OFF.bf27f328.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:running_now GUARD_OFF bf27f328",
+  "killed_by": "tests/features.py",
+  "old": "    if running is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/running_now.RETURN_DEL.574e850d.json b/tests/mutation_ledger/killed_by/duty_switch.py/running_now.RETURN_DEL.574e850d.json
new file mode 100644
index 0000000000..a2cfdbac6f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/running_now.RETURN_DEL.574e850d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:running_now RETURN_DEL 574e850d",
+  "killed_by": "tests/features.py",
+  "old": "    return running",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._grid_terms.RETURN_DEL.7a832a1f.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._grid_terms.RETURN_DEL.7a832a1f.json
new file mode 100644
index 0000000000..2d4579af54
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._grid_terms.RETURN_DEL.7a832a1f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._grid_terms RETURN_DEL 7a832a1f",
+  "killed_by": "tests/features.py",
+  "old": "        return capacity, capacity_batch",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._grid_terms.RETURN_DEL.8c52a9ac.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._grid_terms.RETURN_DEL.8c52a9ac.json
deleted file mode 100644
index 77f82b6754..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._grid_terms.RETURN_DEL.8c52a9ac.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._grid_terms RETURN_DEL 8c52a9ac",
-  "killed_by": "tests/plan_view.py",
-  "old": "        return cycling, capacity, baseline, cycling_batch, capacity_batch",
-  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_space.CLAMP_DROP.2fc0dff9.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_space.CLAMP_DROP.2fc0dff9.json
deleted file mode 100644
index 38cf99b737..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_space.CLAMP_DROP.2fc0dff9.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._solve_space CLAMP_DROP 2fc0dff9",
-  "killed_by": "tests/features.py",
-  "old": "            power = np.clip(res.x, 0.0, headroom)",
-  "reason": "Recorded by `mutation_table.py --drain`: CLAMP_DROP (`power = (res.x)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_space.CLAMP_DROP.f53c3bd9.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_space.CLAMP_DROP.f53c3bd9.json
deleted file mode 100644
index ba2a4f6ea0..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_space.CLAMP_DROP.f53c3bd9.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._solve_space CLAMP_DROP f53c3bd9",
-  "killed_by": "tests/features.py",
-  "old": "                np.maximum(0.0, h.power_caps_extra - dhw_plan),",
-  "reason": "Recorded by `mutation_table.py --drain`: CLAMP_DROP (`(0.0),`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_batch_fd_gradient.BOOLOP.91ef23e1.json b/tests/mutation_ledger/killed_by/optimizer.py/_batch_fd_gradient.BOOLOP.91ef23e1.json
new file mode 100644
index 0000000000..7bcd4042ea
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_batch_fd_gradient.BOOLOP.91ef23e1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_batch_fd_gradient BOOLOP 91ef23e1",
+  "killed_by": "tests/features.py",
+  "old": "    if lead == 0 and not free.any():",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if lead == 0 or not free.any():`) took tests/features.py from rc=0 failed=0 to rc=1 failed=25."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_batch_fd_gradient.GUARD_OFF.91ef23e1.json b/tests/mutation_ledger/killed_by/optimizer.py/_batch_fd_gradient.GUARD_OFF.91ef23e1.json
new file mode 100644
index 0000000000..7dd73959cc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_batch_fd_gradient.GUARD_OFF.91ef23e1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_batch_fd_gradient GUARD_OFF 91ef23e1",
+  "killed_by": "tests/features.py",
+  "old": "    if lead == 0 and not free.any():",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.CLAMP_DROP.baabd38e.json b/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.CLAMP_DROP.baabd38e.json
new file mode 100644
index 0000000000..2537f67e7d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.CLAMP_DROP.baabd38e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_best_runs CLAMP_DROP baabd38e",
+  "killed_by": "tests/features.py",
+  "old": "        scoped = [(np.clip(x, *_stage_box(opt, sc[0], dhw)[:2]), sc) for x, sc in zip(plans, scopes)]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`scoped = [((x), sc) for x, sc in zip(plans, scopes)]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.CLAMP_DROP.bef3bfe7.json b/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.CLAMP_DROP.bef3bfe7.json
new file mode 100644
index 0000000000..714224c3d1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.CLAMP_DROP.bef3bfe7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_best_runs CLAMP_DROP bef3bfe7",
+  "killed_by": "tests/features.py",
+  "old": "    return min((float(scores[order[0]]), *scoped[order[0]]), resolved, key=lambda c: c[0])",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return ((float(scores[order[0]]), *scoped[order[0]]))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.GUARD_OFF.7bfa6521.json b/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.GUARD_OFF.7bfa6521.json
new file mode 100644
index 0000000000..d6afe1b632
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.GUARD_OFF.7bfa6521.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_best_runs GUARD_OFF 7bfa6521",
+  "killed_by": "tests/features.py",
+  "old": "    if rescope is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.RETURN_DEL.bef3bfe7.json b/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.RETURN_DEL.bef3bfe7.json
new file mode 100644
index 0000000000..7b6b14d63e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.RETURN_DEL.bef3bfe7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_best_runs RETURN_DEL bef3bfe7",
+  "killed_by": "tests/features.py",
+  "old": "    return min((float(scores[order[0]]), *scoped[order[0]]), resolved, key=lambda c: c[0])",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=13."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.BOOLOP.a5a6e190.json b/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.BOOLOP.a5a6e190.json
new file mode 100644
index 0000000000..8b2a963bae
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.BOOLOP.a5a6e190.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_commit_runs BOOLOP a5a6e190",
+  "killed_by": "tests/features.py",
+  "old": "    if not opt.config.cycling_cost > 0 and np.array_equal(first, relaxed[0]):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if not opt.config.cycling_cost > 0 or np.array_equal(first, relaxed[0]):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.CMP_BOUND.a5a6e190.json b/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.CMP_BOUND.a5a6e190.json
new file mode 100644
index 0000000000..4e309042f4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.CMP_BOUND.a5a6e190.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_commit_runs CMP_BOUND a5a6e190",
+  "killed_by": "tests/features.py",
+  "old": "    if not opt.config.cycling_cost > 0 and np.array_equal(first, relaxed[0]):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if not opt.config.cycling_cost >= 0 and np.array_equal(first, relaxed[0]):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.GUARD_OFF.32c4a23e.json b/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.GUARD_OFF.32c4a23e.json
new file mode 100644
index 0000000000..51904b83e3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.GUARD_OFF.32c4a23e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_commit_runs GUARD_OFF 32c4a23e",
+  "killed_by": "tests/features.py",
+  "old": "    if not _engaged(opt):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.GUARD_OFF.a5a6e190.json b/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.GUARD_OFF.a5a6e190.json
new file mode 100644
index 0000000000..e284c1cd91
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.GUARD_OFF.a5a6e190.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_commit_runs GUARD_OFF a5a6e190",
+  "killed_by": "tests/features.py",
+  "old": "    if not opt.config.cycling_cost > 0 and np.array_equal(first, relaxed[0]):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.RETURN_DEL.71e1357e.json b/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.RETURN_DEL.71e1357e.json
new file mode 100644
index 0000000000..baa26b60cf
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.RETURN_DEL.71e1357e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_commit_runs RETURN_DEL 71e1357e",
+  "killed_by": "tests/features.py",
+  "old": "        return first, scope",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_descent_pair.GUARD_OFF.32c4a23e.json b/tests/mutation_ledger/killed_by/optimizer.py/_descent_pair.GUARD_OFF.32c4a23e.json
new file mode 100644
index 0000000000..2144578491
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_descent_pair.GUARD_OFF.32c4a23e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_descent_pair GUARD_OFF 32c4a23e",
+  "killed_by": "tests/features.py",
+  "old": "    if not _engaged(opt):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_descent_pair.RETURN_DEL.80e8593e.json b/tests/mutation_ledger/killed_by/optimizer.py/_descent_pair.RETURN_DEL.80e8593e.json
new file mode 100644
index 0000000000..f2c976a428
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_descent_pair.RETURN_DEL.80e8593e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_descent_pair RETURN_DEL 80e8593e",
+  "killed_by": "tests/features.py",
+  "old": "    return partial(objective, descent=descent), partial(objective_batch, descent=descent)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_engaged.CMP_BOUND.0d0861f2.json b/tests/mutation_ledger/killed_by/optimizer.py/_engaged.CMP_BOUND.0d0861f2.json
new file mode 100644
index 0000000000..162a778d06
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_engaged.CMP_BOUND.0d0861f2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_engaged CMP_BOUND 0d0861f2",
+  "killed_by": "tests/features.py",
+  "old": "    return opt.config.cycling_cost > 0 or opt.config.clamp_planned_levels",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return opt.config.cycling_cost >= 0 or opt.config.clamp_planned_levels`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_engaged.RETURN_DEL.0d0861f2.json b/tests/mutation_ledger/killed_by/optimizer.py/_engaged.RETURN_DEL.0d0861f2.json
new file mode 100644
index 0000000000..a0caaeb577
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_engaged.RETURN_DEL.0d0861f2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_engaged RETURN_DEL 0d0861f2",
+  "killed_by": "tests/features.py",
+  "old": "    return opt.config.cycling_cost > 0 or opt.config.clamp_planned_levels",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_projection.CMP_BOUND.4bfc55a3.json b/tests/mutation_ledger/killed_by/optimizer.py/_projection.CMP_BOUND.4bfc55a3.json
new file mode 100644
index 0000000000..6baa7bf304
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_projection.CMP_BOUND.4bfc55a3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_projection CMP_BOUND 4bfc55a3",
+  "killed_by": "tests/features.py",
+  "old": "    return np.where(cycled, space, np.where(raised > hi, 0.0, raised))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return np.where(cycled, space, np.where(raised >= hi, 0.0, raised))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_projection.RETURN_DEL.4bfc55a3.json b/tests/mutation_ledger/killed_by/optimizer.py/_projection.RETURN_DEL.4bfc55a3.json
new file mode 100644
index 0000000000..fcd0917a24
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_projection.RETURN_DEL.4bfc55a3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_projection RETURN_DEL 4bfc55a3",
+  "killed_by": "tests/features.py",
+  "old": "    return np.where(cycled, space, np.where(raised > hi, 0.0, raised))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.BOOLOP.70252daa.json b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.BOOLOP.70252daa.json
new file mode 100644
index 0000000000..be24e0d98e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.BOOLOP.70252daa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_plans BOOLOP 70252daa",
+  "killed_by": "tests/features.py",
+  "old": "    if opt.config.cycling_cost > 0 and _priced_stops(opt) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if opt.config.cycling_cost > 0 or _priced_stops(opt) is not None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.CLAMP_DROP.0d5ce844.json b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.CLAMP_DROP.0d5ce844.json
new file mode 100644
index 0000000000..1092beacb8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.CLAMP_DROP.0d5ce844.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_plans CLAMP_DROP 0d5ce844",
+  "killed_by": "tests/features.py",
+  "old": "    plans = [np.clip(res.x, 0.0, headroom)]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`plans = [(res.x)]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.CMP_BOUND.70252daa.json b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.CMP_BOUND.70252daa.json
new file mode 100644
index 0000000000..9fcbda06d8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.CMP_BOUND.70252daa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_plans CMP_BOUND 70252daa",
+  "killed_by": "tests/features.py",
+  "old": "    if opt.config.cycling_cost > 0 and _priced_stops(opt) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if opt.config.cycling_cost >= 0 and _priced_stops(opt) is not None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.GUARD_OFF.70252daa.json b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.GUARD_OFF.70252daa.json
new file mode 100644
index 0000000000..e9c5cd543c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.GUARD_OFF.70252daa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_plans GUARD_OFF 70252daa",
+  "killed_by": "tests/features.py",
+  "old": "    if opt.config.cycling_cost > 0 and _priced_stops(opt) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.RETURN_DEL.4921045b.json b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.RETURN_DEL.4921045b.json
new file mode 100644
index 0000000000..2a6de7499a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.RETURN_DEL.4921045b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_plans RETURN_DEL 4921045b",
+  "killed_by": "tests/features.py",
+  "old": "    return res, plans",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_starts.CMP_BOUND.7615699d.json b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_starts.CMP_BOUND.7615699d.json
deleted file mode 100644
index 5b852dbf9f..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_starts.CMP_BOUND.7615699d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_starts CMP_BOUND 7615699d",
-  "killed_by": "tests/features.py",
-  "old": "    if not opt.config.clamp_planned_levels or first >= len(cands):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against fb9b3fc1fe16a174476c8571c40b4b7d2d3c089c: CMP_BOUND (`if not opt.config.clamp_planned_levels or first > len(cands):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_starts.GUARD_OFF.7615699d.json b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_starts.GUARD_OFF.7615699d.json
deleted file mode 100644
index 18f4f00acc..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_starts.GUARD_OFF.7615699d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_starts GUARD_OFF 7615699d",
-  "killed_by": "tests/features.py",
-  "old": "    if not opt.config.clamp_planned_levels or first >= len(cands):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against fb9b3fc1fe16a174476c8571c40b4b7d2d3c089c: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_starts.RETURN_DEL.93f85d7e.json b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_starts.RETURN_DEL.93f85d7e.json
deleted file mode 100644
index 0573f4b736..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_starts.RETURN_DEL.93f85d7e.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_starts RETURN_DEL 93f85d7e",
-  "killed_by": "tests/features.py",
-  "old": "    return [*cands, np.asarray(moved.x, dtype=float)]",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against fb9b3fc1fe16a174476c8571c40b4b7d2d3c089c: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_resolved_runs.RETURN_DEL.97ab3094.json b/tests/mutation_ledger/killed_by/optimizer.py/_resolved_runs.RETURN_DEL.97ab3094.json
new file mode 100644
index 0000000000..1daba196c1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_resolved_runs.RETURN_DEL.97ab3094.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_resolved_runs RETURN_DEL 97ab3094",
+  "killed_by": "tests/features.py",
+  "old": "    return float(scope[1](x, *args)), x, scope",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_run_bounds.RETURN_DEL.12b1b723.json b/tests/mutation_ledger/killed_by/optimizer.py/_run_bounds.RETURN_DEL.12b1b723.json
new file mode 100644
index 0000000000..ebde80a367
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_run_bounds.RETURN_DEL.12b1b723.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_run_bounds RETURN_DEL 12b1b723",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    return [b if on[i] or off[i] else (float(plan[i]), float(plan[i])) for i, b in enumerate(pinned)]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.CLAMP_DROP.6e1de491.json b/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.CLAMP_DROP.6e1de491.json
new file mode 100644
index 0000000000..5d95338890
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.CLAMP_DROP.6e1de491.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_run_plans CLAMP_DROP 6e1de491",
+  "killed_by": "tests/features.py",
+  "old": "    plans = [np.where(m & heats, np.clip(space, np.maximum(lo, floor), hi), idle) for m in masks]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`plans = [np.where(m & heats, (space), idle) for m in masks]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.CMP_BOUND.fd3d5485.json b/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.CMP_BOUND.fd3d5485.json
new file mode 100644
index 0000000000..097adbd645
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.CMP_BOUND.fd3d5485.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_run_plans CMP_BOUND fd3d5485",
+  "killed_by": "tests/features.py",
+  "old": "        forced=np.where((other > 0.0) | (lo > 0.0), 1.0, np.where(hi + other <= 0.0, 0.0, np.nan)),",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`forced=np.where((other >= 0.0) | (lo > 0.0), 1.0, np.where(hi + other <= 0.0, 0.0, np.nan)),`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8. Each of the 3 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.GUARD_OFF.741ebb88.json b/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.GUARD_OFF.741ebb88.json
new file mode 100644
index 0000000000..1d3f402a89
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.GUARD_OFF.741ebb88.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_run_plans GUARD_OFF 741ebb88",
+  "killed_by": "tests/features.py",
+  "old": "    if runs.realizable(np.where(cycled, 0.0, space), floor):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.RETURN_DEL.d87d3a8b.json b/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.RETURN_DEL.d87d3a8b.json
new file mode 100644
index 0000000000..811e1bbd94
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.RETURN_DEL.d87d3a8b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_run_plans RETURN_DEL d87d3a8b",
+  "killed_by": "tests/features.py",
+  "old": "    return plans",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_scores_rounded.BOOLOP.b14c9b26.json b/tests/mutation_ledger/killed_by/optimizer.py/_scores_rounded.BOOLOP.b14c9b26.json
deleted file mode 100644
index b1374c373a..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/_scores_rounded.BOOLOP.b14c9b26.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_scores_rounded BOOLOP b14c9b26",
-  "killed_by": "tests/features.py",
-  "old": "    return opt.config.clamp_planned_levels and not opt._levels_relaxed",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against fb9b3fc1fe16a174476c8571c40b4b7d2d3c089c: BOOLOP (`return opt.config.clamp_planned_levels or not opt._levels_relaxed`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_scores_rounded.RETURN_DEL.b14c9b26.json b/tests/mutation_ledger/killed_by/optimizer.py/_scores_rounded.RETURN_DEL.b14c9b26.json
deleted file mode 100644
index 31baccd9da..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/_scores_rounded.RETURN_DEL.b14c9b26.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_scores_rounded RETURN_DEL b14c9b26",
-  "killed_by": "tests/features.py",
-  "old": "    return opt.config.clamp_planned_levels and not opt._levels_relaxed",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against fb9b3fc1fe16a174476c8571c40b4b7d2d3c089c: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.GUARD_OFF.34c17bb7.json b/tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.GUARD_OFF.34c17bb7.json
new file mode 100644
index 0000000000..e767cf5de3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.GUARD_OFF.34c17bb7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_shipped_and_received GUARD_OFF 34c17bb7",
+  "killed_by": "tests/features.py",
+  "old": "    if dhw is not None and opt.config.clamp_planned_levels and not descent:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.CLAMP_DROP.11d6f2e0.json b/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.CLAMP_DROP.11d6f2e0.json
new file mode 100644
index 0000000000..78d3256246
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.CLAMP_DROP.11d6f2e0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_space_scope CLAMP_DROP 11d6f2e0",
+  "killed_by": "tests/features.py",
+  "old": "        headroom = np.minimum(headroom, np.maximum(0.0, h.power_caps_extra - dhw_plan))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`headroom = (headroom)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.CLAMP_DROP.7b421902.json b/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.CLAMP_DROP.7b421902.json
new file mode 100644
index 0000000000..1373e19410
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.CLAMP_DROP.7b421902.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_space_scope CLAMP_DROP 7b421902",
+  "killed_by": "tests/features.py",
+  "old": "        headroom = np.minimum(headroom, h.power_caps)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`headroom = (headroom)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.GUARD_OFF.0429ccf6.json b/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.GUARD_OFF.0429ccf6.json
new file mode 100644
index 0000000000..20f1ee4f67
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.GUARD_OFF.0429ccf6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_space_scope GUARD_OFF 0429ccf6",
+  "killed_by": "tests/guard_pins.py",
+  "old": "    if h.power_caps is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.GUARD_OFF.41fbb204.json b/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.GUARD_OFF.41fbb204.json
new file mode 100644
index 0000000000..4c9055e6f9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.GUARD_OFF.41fbb204.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_space_scope GUARD_OFF 41fbb204",
+  "killed_by": "tests/features.py",
+  "old": "    if h.power_caps_extra is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.RETURN_DEL.b137c24a.json b/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.RETURN_DEL.b137c24a.json
new file mode 100644
index 0000000000..63f44bbdcc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.RETURN_DEL.b137c24a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_space_scope RETURN_DEL b137c24a",
+  "killed_by": "tests/features.py",
+  "old": "    return headroom, (bounds, objective, objective_batch, opt._space_avail)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_stage_box.GUARD_OFF.80bd8784.json b/tests/mutation_ledger/killed_by/optimizer.py/_stage_box.GUARD_OFF.80bd8784.json
new file mode 100644
index 0000000000..d1f6938af0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_stage_box.GUARD_OFF.80bd8784.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_stage_box GUARD_OFF 80bd8784",
+  "killed_by": "tests/features.py",
+  "old": "    if dhw is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_stage_box.RETURN_DEL.92f7c0da.json b/tests/mutation_ledger/killed_by/optimizer.py/_stage_box.RETURN_DEL.92f7c0da.json
new file mode 100644
index 0000000000..ac038df05c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_stage_box.RETURN_DEL.92f7c0da.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_stage_box RETURN_DEL 92f7c0da",
+  "killed_by": "tests/features.py",
+  "old": "    return lo, hi, other, cycled",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=13."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.RETURN_DEL.c29a3a4d.json b/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.RETURN_DEL.c29a3a4d.json
new file mode 100644
index 0000000000..d1afa16bdd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.RETURN_DEL.c29a3a4d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_start_cost_fn RETURN_DEL c29a3a4d",
+  "killed_by": "tests/plan_view.py",
+  "old": "    return start_cost",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.start_cost.CMP_BOUND.81fa75c5.json b/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.start_cost.CMP_BOUND.81fa75c5.json
new file mode 100644
index 0000000000..c5a94cf720
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.start_cost.CMP_BOUND.81fa75c5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_start_cost_fn.start_cost CMP_BOUND 81fa75c5",
+  "killed_by": "tests/features.py",
+  "old": "        if descent or not cost > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if descent or not cost >= 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.start_cost.GUARD_OFF.81fa75c5.json b/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.start_cost.GUARD_OFF.81fa75c5.json
new file mode 100644
index 0000000000..eef24e824f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.start_cost.GUARD_OFF.81fa75c5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_start_cost_fn.start_cost GUARD_OFF 81fa75c5",
+  "killed_by": "tests/features.py",
+  "old": "        if descent or not cost > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.start_cost.RETURN_DEL.5b562f2d.json b/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.start_cost.RETURN_DEL.5b562f2d.json
new file mode 100644
index 0000000000..711056cd91
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.start_cost.RETURN_DEL.5b562f2d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_start_cost_fn.start_cost RETURN_DEL 5b562f2d",
+  "killed_by": "tests/features.py",
+  "old": "        return cost * count(power, p_min, running)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.CMP_BOUND.b0a491aa.json b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.CMP_BOUND.747c72fe.json
similarity index 51%
rename from tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.CMP_BOUND.b0a491aa.json
rename to tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.CMP_BOUND.747c72fe.json
index 318c16b96c..6ae00c8053 100644
--- a/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.CMP_BOUND.b0a491aa.json
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.CMP_BOUND.747c72fe.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_switch_cost_fn.switch_cost CMP_BOUND b0a491aa",
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_switch_cost_fn.switch_cost CMP_BOUND 747c72fe",
   "killed_by": "tests/features.py",
-  "old": "        if stops is None or dhw is None or not cost > 0:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if stops is None or dhw is None or not cost >= 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+  "old": "        if stops is None or dhw is None or not cost > 0 or descent == _UNPRICED:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if stops is None or dhw is None or not cost >= 0 or descent == _UNPRICED:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
 }
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.GUARD_OFF.b0a491aa.json b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.GUARD_OFF.747c72fe.json
similarity index 80%
rename from tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.GUARD_OFF.b0a491aa.json
rename to tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.GUARD_OFF.747c72fe.json
index 899cb46f4a..f4e8567697 100644
--- a/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.GUARD_OFF.b0a491aa.json
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.GUARD_OFF.747c72fe.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_switch_cost_fn.switch_cost GUARD_OFF b0a491aa",
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_switch_cost_fn.switch_cost GUARD_OFF 747c72fe",
   "killed_by": "tests/plan_view.py",
-  "old": "        if stops is None or dhw is None or not cost > 0:",
+  "old": "        if stops is None or dhw is None or not cost > 0 or descent == _UNPRICED:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
 }
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/count_compressor_starts.RETURN_DEL.c953de7d.json b/tests/mutation_ledger/killed_by/optimizer.py/count_compressor_starts.RETURN_DEL.c953de7d.json
deleted file mode 100644
index d404d7f819..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/count_compressor_starts.RETURN_DEL.c953de7d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:count_compressor_starts RETURN_DEL c953de7d",
-  "killed_by": "tests/features.py",
-  "old": "    return starts",
-  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/runs.py/@module.CONST.0a7cde76.json b/tests/mutation_ledger/killed_by/runs.py/@module.CONST.0a7cde76.json
new file mode 100644
index 0000000000..f5f12e186c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/@module.CONST.0a7cde76.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:<module> CONST 0a7cde76",
+  "killed_by": "tests/features.py",
+  "old": "OUT_OF_BAND = 10.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`OUT_OF_BAND = 20.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/@module.CONST.7f5866e2.json b/tests/mutation_ledger/killed_by/runs.py/@module.CONST.7f5866e2.json
new file mode 100644
index 0000000000..5b7d71bcd1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/@module.CONST.7f5866e2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:<module> CONST 7f5866e2",
+  "killed_by": "tests/features.py",
+  "old": "_SLACK = 1e-9",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`_SLACK = 0.0e-9`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/@module.CONST.b713a5a2.json b/tests/mutation_ledger/killed_by/runs.py/@module.CONST.b713a5a2.json
new file mode 100644
index 0000000000..fac764e760
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/@module.CONST.b713a5a2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:<module> CONST b713a5a2",
+  "killed_by": "tests/features.py",
+  "old": "QUANTA_PER_STEP = 4",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`QUANTA_PER_STEP = 8`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/@module.CONST.e51c2039.json b/tests/mutation_ledger/killed_by/runs.py/@module.CONST.e51c2039.json
new file mode 100644
index 0000000000..b976b0852d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/@module.CONST.e51c2039.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:<module> CONST e51c2039",
+  "killed_by": "tests/features.py",
+  "old": "_TIE_BREAK = 1e-9",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`_TIE_BREAK = 0.0e-9`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.3103be9a.json b/tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.3103be9a.json
new file mode 100644
index 0000000000..82e9874454
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.3103be9a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:_advance CLAMP_DROP 3103be9a",
+  "killed_by": "tests/features.py",
+  "old": "        outside = np.maximum(np.abs(b) - half * quantum, 0.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`outside = (np.abs(b) - half * quantum)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.faf454fb.json b/tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.faf454fb.json
new file mode 100644
index 0000000000..a0591e68f6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.faf454fb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:_advance CLAMP_DROP faf454fb",
+  "killed_by": "tests/features.py",
+  "old": "        j = np.clip(np.rint(b / quantum).astype(np.int64) + half, 0, 2 * half)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`j = (np.rint(b / quantum).astype(np.int64) + half)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_advance.CMP_BOUND.a2abb9b6.json b/tests/mutation_ledger/killed_by/runs.py/_advance.CMP_BOUND.a2abb9b6.json
new file mode 100644
index 0000000000..4c13f622b6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/_advance.CMP_BOUND.a2abb9b6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:_advance CMP_BOUND a2abb9b6",
+  "killed_by": "tests/features.py",
+  "old": "        change, paid = step[0] if dest < min_on else step[1]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`change, paid = step[0] if dest <= min_on else step[1]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_advance.GUARD_OFF.329931dd.json b/tests/mutation_ledger/killed_by/runs.py/_advance.GUARD_OFF.329931dd.json
new file mode 100644
index 0000000000..c82853e3a0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/_advance.GUARD_OFF.329931dd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:_advance GUARD_OFF 329931dd",
+  "killed_by": "tests/features.py",
+  "old": "        if not ok.any():",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_advance.RETURN_DEL.e82fb19a.json b/tests/mutation_ledger/killed_by/runs.py/_advance.RETURN_DEL.e82fb19a.json
new file mode 100644
index 0000000000..2cd18bdda4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/_advance.RETURN_DEL.e82fb19a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:_advance RETURN_DEL e82fb19a",
+  "killed_by": "tests/features.py",
+  "old": "    return new_cost, new_bal, back",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.89e6a09b.json b/tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.89e6a09b.json
new file mode 100644
index 0000000000..65d574631c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.89e6a09b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:_moves CLAMP_DROP 89e6a09b",
+  "killed_by": "tests/features.py",
+  "old": "        out += [(i, min(i + 1, states - 1), False) for i in range(min_on, states)]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`out += [(i, (i + 1), False) for i in range(min_on, states)]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.b33258f0.json b/tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.b33258f0.json
new file mode 100644
index 0000000000..84a00e6ada
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.b33258f0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:_moves CLAMP_DROP b33258f0",
+  "killed_by": "tests/features.py",
+  "old": "        out += [(i, min(i + 1, last_on), False) for i in range(min_on)]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`out += [(i, (i + 1), False) for i in range(min_on)]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.853776b6.json b/tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.853776b6.json
new file mode 100644
index 0000000000..520a00450d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.853776b6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:_moves GUARD_OFF 853776b6",
+  "killed_by": "tests/features.py",
+  "old": "    if not want == 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.edbdf8a8.json b/tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.edbdf8a8.json
new file mode 100644
index 0000000000..83e3505d83
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.edbdf8a8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:_moves GUARD_OFF edbdf8a8",
+  "killed_by": "tests/features.py",
+  "old": "    if not want == 1.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=14."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_moves.RETURN_DEL.a8227ccf.json b/tests/mutation_ledger/killed_by/runs.py/_moves.RETURN_DEL.a8227ccf.json
new file mode 100644
index 0000000000..7fec4cdf5a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/_moves.RETURN_DEL.a8227ccf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:_moves RETURN_DEL a8227ccf",
+  "killed_by": "tests/features.py",
+  "old": "    return out",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/candidates.BOOLOP.48f957af.json b/tests/mutation_ledger/killed_by/runs.py/candidates.BOOLOP.48f957af.json
new file mode 100644
index 0000000000..d3528f5510
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/candidates.BOOLOP.48f957af.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:candidates BOOLOP 48f957af",
+  "killed_by": "tests/features.py",
+  "old": "        if tracked and band > BANDS[-1]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if tracked or band > BANDS[-1]:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/candidates.CMP_BOUND.48f957af.json b/tests/mutation_ledger/killed_by/runs.py/candidates.CMP_BOUND.48f957af.json
new file mode 100644
index 0000000000..54a87f627e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/candidates.CMP_BOUND.48f957af.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:candidates CMP_BOUND 48f957af",
+  "killed_by": "tests/features.py",
+  "old": "        if tracked and band > BANDS[-1]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if tracked and band >= BANDS[-1]:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/candidates.GUARD_OFF.48f957af.json b/tests/mutation_ledger/killed_by/runs.py/candidates.GUARD_OFF.48f957af.json
new file mode 100644
index 0000000000..1b6ef09c8b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/candidates.GUARD_OFF.48f957af.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:candidates GUARD_OFF 48f957af",
+  "killed_by": "tests/features.py",
+  "old": "        if tracked and band > BANDS[-1]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/candidates.GUARD_OFF.d75cfe9e.json b/tests/mutation_ledger/killed_by/runs.py/candidates.GUARD_OFF.d75cfe9e.json
new file mode 100644
index 0000000000..fddb10c238
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/candidates.GUARD_OFF.d75cfe9e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:candidates GUARD_OFF d75cfe9e",
+  "killed_by": "tests/features.py",
+  "old": "        if not any(np.array_equal(mask, m) for m in masks):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/candidates.RETURN_DEL.97969b54.json b/tests/mutation_ledger/killed_by/runs.py/candidates.RETURN_DEL.97969b54.json
new file mode 100644
index 0000000000..4f269a61a8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/candidates.RETURN_DEL.97969b54.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:candidates RETURN_DEL 97969b54",
+  "killed_by": "tests/features.py",
+  "old": "    return masks",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.BOOLOP.3f04b002.json b/tests/mutation_ledger/killed_by/runs.py/commit.BOOLOP.3f04b002.json
new file mode 100644
index 0000000000..5ab295238b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/commit.BOOLOP.3f04b002.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit BOOLOP 3f04b002",
+  "killed_by": "tests/features.py",
+  "old": "        np.all(np.abs(walk) <= half * quantum + _SLACK) and abs(walk[-1]) <= f * dt / 2.0 + _SLACK)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`np.all(np.abs(walk) <= half * quantum + _SLACK) or abs(walk[-1]) <= f * dt / 2.0 + _SLACK)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.CLAMP_DROP.66553920.json b/tests/mutation_ledger/killed_by/runs.py/commit.CLAMP_DROP.66553920.json
new file mode 100644
index 0000000000..d312d90153
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/commit.CLAMP_DROP.66553920.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit CLAMP_DROP 66553920",
+  "killed_by": "tests/features.py",
+  "old": "    level = np.minimum(np.maximum(q, f), cap)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`level = (np.maximum(q, f))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.CLAMP_DROP.a4b85c7c.json b/tests/mutation_ledger/killed_by/runs.py/commit.CLAMP_DROP.a4b85c7c.json
new file mode 100644
index 0000000000..8af8759ea0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/commit.CLAMP_DROP.a4b85c7c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit CLAMP_DROP a4b85c7c",
+  "killed_by": "tests/features.py",
+  "old": "    ending = cost + fine * np.maximum(np.abs(bal) - f * dt / 2.0, 0.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`ending = cost + fine * (np.abs(bal) - f * dt / 2.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.056c259e.json b/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.056c259e.json
new file mode 100644
index 0000000000..556f4a03bc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.056c259e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit CMP_BOUND 056c259e",
+  "killed_by": "tests/features.py",
+  "old": "        asked = bool(q[k] > 0.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`asked = bool(q[k] >= 0.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.344874f5.json b/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.344874f5.json
new file mode 100644
index 0000000000..0be4279f3e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.344874f5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit CMP_BOUND 344874f5",
+  "killed_by": "tests/features.py",
+  "old": "    want = np.where(np.isnan(want) & (cap < f - _SLACK), 0.0, want)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`want = np.where(np.isnan(want) & (cap <= f - _SLACK), 0.0, want)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.d914b133.json b/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.d914b133.json
new file mode 100644
index 0000000000..4bc0e47f2f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.d914b133.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit CMP_BOUND d914b133",
+  "killed_by": "tests/features.py",
+  "old": "        mask[k] = u < min_on",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`mask[k] = u <= min_on`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.RETURN_DEL.1ec24ddf.json b/tests/mutation_ledger/killed_by/runs.py/commit.RETURN_DEL.1ec24ddf.json
new file mode 100644
index 0000000000..fbece04c55
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/commit.RETURN_DEL.1ec24ddf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit RETURN_DEL 1ec24ddf",
+  "killed_by": "tests/features.py",
+  "old": "    return mask, tracked",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/edge_count.CMP_BOUND.503f62fe.json b/tests/mutation_ledger/killed_by/runs.py/edge_count.CMP_BOUND.503f62fe.json
new file mode 100644
index 0000000000..f4a8a70730
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/edge_count.CMP_BOUND.503f62fe.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:edge_count CMP_BOUND 503f62fe",
+  "killed_by": "tests/features.py",
+  "old": "    on = np.asarray(total, dtype=float) > MIN_RUNNING_DRAW_KW",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`on = np.asarray(total, dtype=float) >= MIN_RUNNING_DRAW_KW`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/edge_count.RETURN_DEL.82a582db.json b/tests/mutation_ledger/killed_by/runs.py/edge_count.RETURN_DEL.82a582db.json
new file mode 100644
index 0000000000..7aa961fefd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/edge_count.RETURN_DEL.82a582db.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:edge_count RETURN_DEL 82a582db",
+  "killed_by": "tests/features.py",
+  "old": "    return int(np.sum(on & ~np.r_[bool(running), on[:-1]]))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/floor_kw.CLAMP_DROP.23807357.json b/tests/mutation_ledger/killed_by/runs.py/floor_kw.CLAMP_DROP.23807357.json
new file mode 100644
index 0000000000..ecd2a6979d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/floor_kw.CLAMP_DROP.23807357.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:floor_kw CLAMP_DROP 23807357",
+  "killed_by": "tests/features.py",
+  "old": "    return max(float(floor), MIN_RUNNING_DRAW_KW)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return (float(floor))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/floor_kw.RETURN_DEL.23807357.json b/tests/mutation_ledger/killed_by/runs.py/floor_kw.RETURN_DEL.23807357.json
new file mode 100644
index 0000000000..61fcf26542
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/floor_kw.RETURN_DEL.23807357.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:floor_kw RETURN_DEL 23807357",
+  "killed_by": "tests/features.py",
+  "old": "    return max(float(floor), MIN_RUNNING_DRAW_KW)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/realizable.CMP_BOUND.7069a02a.json b/tests/mutation_ledger/killed_by/runs.py/realizable.CMP_BOUND.7069a02a.json
new file mode 100644
index 0000000000..863f11d0a2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/realizable.CMP_BOUND.7069a02a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:realizable CMP_BOUND 7069a02a",
+  "killed_by": "tests/features.py",
+  "old": "    return bool(np.all((q <= 0.0) | (q >= floor_kw(floor) - _SLACK)))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return bool(np.all((q < 0.0) | (q >= floor_kw(floor) - _SLACK)))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/realizable.RETURN_DEL.7069a02a.json b/tests/mutation_ledger/killed_by/runs.py/realizable.RETURN_DEL.7069a02a.json
new file mode 100644
index 0000000000..dd3eb2a59f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/realizable.RETURN_DEL.7069a02a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:realizable RETURN_DEL 7069a02a",
+  "killed_by": "tests/features.py",
+  "old": "    return bool(np.all((q <= 0.0) | (q >= floor_kw(floor) - _SLACK)))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/running_share.CLAMP_DROP.63c654e6.json b/tests/mutation_ledger/killed_by/runs.py/running_share.CLAMP_DROP.63c654e6.json
new file mode 100644
index 0000000000..0a5034a776
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/running_share.CLAMP_DROP.63c654e6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:running_share CLAMP_DROP 63c654e6",
+  "killed_by": "tests/features.py",
+  "old": "    return np.clip(np.asarray(total, dtype=float) / floor_kw(floor), 0.0, 1.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return (np.asarray(total, dtype=float) / floor_kw(floor))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/running_share.RETURN_DEL.63c654e6.json b/tests/mutation_ledger/killed_by/runs.py/running_share.RETURN_DEL.63c654e6.json
new file mode 100644
index 0000000000..cee456d40c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/running_share.RETURN_DEL.63c654e6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:running_share RETURN_DEL 63c654e6",
+  "killed_by": "tests/features.py",
+  "old": "    return np.clip(np.asarray(total, dtype=float) / floor_kw(floor), 0.0, 1.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/start_count.RETURN_DEL.59dd2f98.json b/tests/mutation_ledger/killed_by/runs.py/start_count.RETURN_DEL.59dd2f98.json
new file mode 100644
index 0000000000..881cfef107
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/start_count.RETURN_DEL.59dd2f98.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:start_count RETURN_DEL 59dd2f98",
+  "killed_by": "tests/features.py",
+  "old": "    return float(start_count_batch(np.asarray(total, dtype=float)[None, :], floor, running)[0])",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/start_count_batch.CLAMP_DROP.0275c9ad.json b/tests/mutation_ledger/killed_by/runs.py/start_count_batch.CLAMP_DROP.0275c9ad.json
new file mode 100644
index 0000000000..b476743c7a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/start_count_batch.CLAMP_DROP.0275c9ad.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:start_count_batch CLAMP_DROP 0275c9ad",
+  "killed_by": "tests/features.py",
+  "old": "    needs = np.clip(rows / MIN_RUNNING_DRAW_KW, 0.0, 1.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`needs = (rows / MIN_RUNNING_DRAW_KW)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=18."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/start_count_batch.RETURN_DEL.5cb47597.json b/tests/mutation_ledger/killed_by/runs.py/start_count_batch.RETURN_DEL.5cb47597.json
new file mode 100644
index 0000000000..a0e9def044
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/start_count_batch.RETURN_DEL.5cb47597.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:start_count_batch RETURN_DEL 5cb47597",
+  "killed_by": "tests/features.py",
+  "old": "    return count",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/steps_at_least.CLAMP_DROP.e5f3ee1d.json b/tests/mutation_ledger/killed_by/runs.py/steps_at_least.CLAMP_DROP.e5f3ee1d.json
new file mode 100644
index 0000000000..34cd32cef1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/steps_at_least.CLAMP_DROP.e5f3ee1d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:steps_at_least CLAMP_DROP e5f3ee1d",
+  "killed_by": "tests/features.py",
+  "old": "    return max(1, int(np.ceil(span.total_seconds() / 3600.0 / dt_hours - _SLACK)))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return (1)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/steps_at_least.RETURN_DEL.e5f3ee1d.json b/tests/mutation_ledger/killed_by/runs.py/steps_at_least.RETURN_DEL.e5f3ee1d.json
new file mode 100644
index 0000000000..030c5b83f8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/steps_at_least.RETURN_DEL.e5f3ee1d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:steps_at_least RETURN_DEL e5f3ee1d",
+  "killed_by": "tests/features.py",
+  "old": "    return max(1, int(np.ceil(span.total_seconds() / 3600.0 / dt_hours - _SLACK)))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/@module.CONST.a4245540.json b/tests/mutation_ledger/survivor_triage/optimizer.py/@module.CONST.a4245540.json
new file mode 100644
index 0000000000..f08d48722c
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/@module.CONST.a4245540.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:<module> CONST a4245540",
+  "old": "_RESOLVED_CANDIDATES = 2",
+  "reason": "Survived tests/features.py, the one driver run, under `mutation_table.py --pin-killed --scripts tests/features.py` at 3f0149a81b (R11-OUTSIDE-HONEST-STARTS-RUNS, repair round 4; pull request 3602, the build of Bankaifan's pull request 3529); the other drivers of the file's closure were not run. Re-solving four candidates instead of two can only lower the lowest score the stage ships, so every selection check still holds, and no check counts the L-BFGS-B runs a stage call makes. A killing check is in R11-OUTSIDE-HONEST-STARTS-RUNS-P2's brief (item i).",
+  "verdict": "gap"
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/_projection.GUARD_OFF.ab0c3e65.json b/tests/mutation_ledger/survivor_triage/optimizer.py/_projection.GUARD_OFF.ab0c3e65.json
new file mode 100644
index 0000000000..0a4a9ff55a
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/_projection.GUARD_OFF.ab0c3e65.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_projection GUARD_OFF ab0c3e65",
+  "old": "    if opt.config.clamp_planned_levels:",
+  "reason": "Survived tests/features.py, the one driver run, under `mutation_table.py --pin-killed --scripts tests/features.py` at 3f0149a81b (R11-OUTSIDE-HONEST-STARTS-RUNS, repair round 4; pull request 3602, the build of Bankaifan's pull request 3529); the other drivers of the file's closure were not run. With the clamped arm off, a clamped install's candidate (1) is built by the duty-cycle arm (each level raised to the floor against its cap). On the block's clamped fixtures the stage ships a committed candidate either way, and no check compares a clamped install's projection with `_realize_draw`'s. A check on `_projection` alone, clamped against unclamped on one relaxed plan with a sub-floor level beside hot water, would kill it; none is recorded.",
+  "verdict": "gap"
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/_relaxed_plans.CLAMP_DROP.b076955e.json b/tests/mutation_ledger/survivor_triage/optimizer.py/_relaxed_plans.CLAMP_DROP.b076955e.json
new file mode 100644
index 0000000000..474642483b
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/_relaxed_plans.CLAMP_DROP.b076955e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_plans CLAMP_DROP b076955e",
+  "old": "            pair[0], [np.minimum(x, free_room) for x in starts], free[0], args=(dhw_plan,),",
+  "reason": "Survived tests/features.py, the one driver run, under `mutation_table.py --pin-killed --scripts tests/features.py` at 3f0149a81b (R11-OUTSIDE-HONEST-STARTS-RUNS, repair round 4; pull request 3602, the build of Bankaifan's pull request 3529); the other drivers of the file's closure were not run. The mutant hands the second descent's multi-start its starts unclipped to the bound no stop cuts. The plan it returns is clipped to that bound on the next line and L-BFGS-B projects a start into its bounds, so no shipped plan moved on the block's priced installs; not shown equivalent on a start far outside the bound. A check that reads the starts the second multi-start is handed would kill it; none is recorded.",
+  "verdict": "gap"
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/_run_bounds.CMP_BOUND.ac17e14b.json b/tests/mutation_ledger/survivor_triage/optimizer.py/_run_bounds.CMP_BOUND.ac17e14b.json
new file mode 100644
index 0000000000..a6e1648830
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/_run_bounds.CMP_BOUND.ac17e14b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_run_bounds CMP_BOUND ac17e14b",
+  "old": "    on, off = plan >= floor - 1e-9, plan <= 0.0",
+  "reason": "Survived tests/features.py, the one driver run, under `mutation_table.py --pin-killed --scripts tests/features.py` at 3f0149a81b (R11-OUTSIDE-HONEST-STARTS-RUNS, repair round 4; pull request 3602, the build of Bankaifan's pull request 3529); the other drivers of the file's closure were not run. `_run_bounds` reads a level as on at the floor less 1e-9 and as off at zero; the variants differ only for a level exactly on either edge, and no candidate of the block's fixtures holds one (a committed step is at the floor or above, an idle one at zero or at its pin). A check that hands `_run_bounds` a plan with a level at the floor less 1e-9 would kill the first; none is recorded.",
+  "verdict": "gap"
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/_run_plans.CMP_BOUND.eaf0d1e3.json b/tests/mutation_ledger/survivor_triage/optimizer.py/_run_plans.CMP_BOUND.eaf0d1e3.json
new file mode 100644
index 0000000000..cf478b7720
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/_run_plans.CMP_BOUND.eaf0d1e3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_run_plans CMP_BOUND eaf0d1e3",
+  "old": "    heats = (hi >= floor) & ((other <= 0.0) | (space >= floor / 2.0))",
+  "reason": "Survived tests/features.py, the one driver run, under `mutation_table.py --pin-killed --scripts tests/features.py` at 3f0149a81b (R11-OUTSIDE-HONEST-STARTS-RUNS, repair round 4; pull request 3602, the build of Bankaifan's pull request 3529); the other drivers of the file's closure were not run. The heats predicate's three boundaries: a cap exactly at the floor, hot water exactly at zero, a space level exactly at half the floor. One of the three variants is killed by tests/features.py; the fixtures hold no step on the other two equalities. A killing check is in R11-OUTSIDE-HONEST-STARTS-RUNS-P2's brief (item i).",
+  "verdict": "gap"
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/_stage_box.CLAMP_DROP.60ed0d0d.json b/tests/mutation_ledger/survivor_triage/optimizer.py/_stage_box.CLAMP_DROP.60ed0d0d.json
new file mode 100644
index 0000000000..dc1ffdba89
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/_stage_box.CLAMP_DROP.60ed0d0d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_stage_box CLAMP_DROP 60ed0d0d",
+  "old": "        hi = np.minimum(hi, np.maximum(p_max - other, 0.0))",
+  "reason": "Survived tests/features.py, the one driver run, under `mutation_table.py --pin-killed --scripts tests/features.py` at 3f0149a81b (R11-OUTSIDE-HONEST-STARTS-RUNS, repair round 4; pull request 3602, the build of Bankaifan's pull request 3529); the other drivers of the file's closure were not run. The stage box's tank room: the space cap less what the tank draws, never under zero. The block's solves beside hot water never hand the stage a cap above that room, so dropping either clamp moves no candidate. A killing check is in R11-OUTSIDE-HONEST-STARTS-RUNS-P2's brief (item i).",
+  "verdict": "gap"
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/_stage_box.CLAMP_DROP.b07febdf.json b/tests/mutation_ledger/survivor_triage/optimizer.py/_stage_box.CLAMP_DROP.b07febdf.json
new file mode 100644
index 0000000000..5b7557a111
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/_stage_box.CLAMP_DROP.b07febdf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_stage_box CLAMP_DROP b07febdf",
+  "old": "        lo = np.minimum(lo, hi)",
+  "reason": "Survived tests/features.py, the one driver run, under `mutation_table.py --pin-killed --scripts tests/features.py` at 3f0149a81b (R11-OUTSIDE-HONEST-STARTS-RUNS, repair round 4; pull request 3602, the build of Bankaifan's pull request 3529); the other drivers of the file's closure were not run. The lower bound held under the tank room. It binds only where a forced-on space pin sits beside a charge that leaves less than the pin's level, and no fixture of the block pins space beside hot water at the stage. A check on `_stage_box` with such a pin would kill it; none is recorded.",
+  "verdict": "gap"
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/_stage_box.CMP_BOUND.ccc99b4a.json b/tests/mutation_ledger/survivor_triage/optimizer.py/_stage_box.CMP_BOUND.ccc99b4a.json
new file mode 100644
index 0000000000..6e46eb9c1e
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/_stage_box.CMP_BOUND.ccc99b4a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_stage_box CMP_BOUND ccc99b4a",
+  "old": "    cycled = (not opt.config.clamp_planned_levels) & (other <= 0.0) & (hi < runs.floor_kw(p_min))",
+  "reason": "Survived tests/features.py, the one driver run, under `mutation_table.py --pin-killed --scripts tests/features.py` at 3f0149a81b (R11-OUTSIDE-HONEST-STARTS-RUNS, repair round 4; pull request 3602, the build of Bankaifan's pull request 3529); the other drivers of the file's closure were not run. The `cycled` reading's two boundaries: hot water exactly at zero and a cap exactly at the floor. With `other < 0.0` no step is ever read as cycled, yet the block's capped fixture (the named mutant CYCLED_KEPT, killed) keeps its capped steps through another arm of the same candidates; with `hi <= floor` a cap exactly at the floor would cycle. A check on `_stage_box`'s fourth value at a cap under, at and above the floor would kill both; none is recorded.",
+  "verdict": "gap"
+}
diff --git a/tests/mutation_ledger/survivor_triage/runs.py/commit.CLAMP_DROP.54895a3e.json b/tests/mutation_ledger/survivor_triage/runs.py/commit.CLAMP_DROP.54895a3e.json
new file mode 100644
index 0000000000..7247f523cd
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/runs.py/commit.CLAMP_DROP.54895a3e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit CLAMP_DROP 54895a3e",
+  "old": "    fine = OUT_OF_BAND * max(float(np.max(np.abs(price))), 1e-6)",
+  "reason": "Survived tests/features.py, the one driver run, under `mutation_table.py --pin-killed --scripts tests/features.py` at 3f0149a81b (R11-OUTSIDE-HONEST-STARTS-RUNS, repair round 4; pull request 3602, the build of Bankaifan's pull request 3529); the other drivers of the file's closure were not run. The floor of 1e-6 under the out-of-band price matters only where every price of the horizon is zero: there the mutant's penalty is zero and a balance outside the band is free. No fixture commits at an all-zero price with a mask that would leave its band. A leaf check like the block's late-cheap trickle at price zero and a start price would kill it; none is recorded.",
+  "verdict": "gap"
+}
diff --git a/tests/mutation_ledger/survivor_triage/runs.py/commit.CMP_BOUND.3f04b002.json b/tests/mutation_ledger/survivor_triage/runs.py/commit.CMP_BOUND.3f04b002.json
new file mode 100644
index 0000000000..75948d7be3
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/runs.py/commit.CMP_BOUND.3f04b002.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit CMP_BOUND 3f04b002",
+  "old": "        np.all(np.abs(walk) <= half * quantum + _SLACK) and abs(walk[-1]) <= f * dt / 2.0 + _SLACK)",
+  "reason": "Survived tests/features.py, the one driver run, under `mutation_table.py --pin-killed --scripts tests/features.py` at 3f0149a81b (R11-OUTSIDE-HONEST-STARTS-RUNS, repair round 4; pull request 3602, the build of Bankaifan's pull request 3529); the other drivers of the file's closure were not run. The two comparisons of `tracked` against the band edge and the end balance carry the float slack, so the variants differ only for a walk exactly at an edge plus 1e-9; the leaf fixtures sit exactly on the band edge (2.0 and 6.0 floor steps), inside the slack under both forms. Equivalent for every walk not within 1e-9 of that sum; not shown for one that is.",
+  "verdict": "gap"
+}


## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/batchmath.py b/custom_components/heatpump_optimizer/batchmath.py
index 30ed5eeb8d..c38805bd96 100644
--- a/custom_components/heatpump_optimizer/batchmath.py
+++ b/custom_components/heatpump_optimizer/batchmath.py
@@ -16,6 +16,10 @@ from __future__ import annotations
 
 import numpy as np
 
+#: The two sides of every boundary between consecutive steps of a ``[B, n]``
+#: batch: each step but the last, and the step after it.
+BEFORE, AFTER = np.s_[:, :-1], np.s_[:, 1:]
+
 #: numpy's unrolled pairwise block: under this width a fresh 1-D sum is
 #: eight interleaved partials combined in a fixed tree, above it halving.
 #: The value is numpy's own (``PW_BLOCKSIZE`` in ``loops_utils.h``); the
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index f16081f02e..9f256d6271 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -560,6 +560,12 @@ def _within_window(value: float | None, window: tuple[float, float]) -> float |
 FORECAST_STEP = timedelta(minutes=PLAN_STEP_MINUTES)
 
 
+def _humidity_with_data(series: np.ndarray) -> np.ndarray | None:
+    """#21: a solve's humidity series only when it carries data, which keeps
+    the solve's inner loop free of dead lookups."""
+    return series if series.size and bool(np.any(np.isfinite(series))) else None
+
+
 def _comparable_ts(raw: Any, reference: datetime) -> datetime | None:
     """Parse an entry timestamp so it can be ordered against the step grid.
 
@@ -6297,10 +6303,10 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         if env_caps is not None:
             caps = env_caps if caps is None else np.minimum(caps, env_caps)
         quiet = quiet_windows.compose_with_silent(caps, ctx._config, ctx.hass.states.get, solve_now, n, config.dt_hours, params.max_electrical_power, optimizer_active=self._mode != MODE_OFF)
-        humidity = horizon.humidity
         return SolveRecord(config, params, SolveInputs(
             state=state,
             start_time=solve_now,
+            compressor_running=duty_switch.running_now(duty_switch.record_for(self), self._current_action),
             forecast=ForecastSeries(
                 prices=horizon.prices,
                 outdoor_temps=horizon.outdoor_temps,
@@ -6310,12 +6316,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
                 price_known=horizon.price_known,
                 pv_surplus=horizon.pv_surplus,
                 price_sigma=horizon.price_sigma,
-                # #21: the humidity series only when it carries data, which
-                # keeps the solve's inner loop free of dead lookups.
-                humidity=(
-                    humidity if humidity.size
-                    and bool(np.any(np.isfinite(humidity))) else None
-                ),
+                humidity=_humidity_with_data(horizon.humidity),
                 external_heat_kw=self._external_heat_forecast(n),
             ),
             limits=SolveLimits(
@@ -11311,12 +11312,12 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         )
         if wood_err:
             raise whatif.Refused(wood_err)
-        humidity = horizon.humidity
         return HeatPumpOptimizer(ThermalModel(scratch_params), scratch_config), SolveInputs(
             # Shallow deliberately: ``ThermalState`` is scalars only.
             state=replace(state),
             start_time=solve_at,
             held_start=held_start,
+            compressor_running=duty_switch.record_for(self).solved_running,
             forecast=ForecastSeries(
                 prices=horizon.prices,
                 outdoor_temps=horizon.outdoor_temps,
@@ -11331,10 +11332,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
                 price_sigma=horizon.price_sigma,
                 # #21: the what-if is compared against a plan that saw
                 # the humidity series, so it must see the same one.
-                humidity=(
-                    humidity if humidity.size
-                    and bool(np.any(np.isfinite(humidity))) else None
-                ),
+                humidity=_humidity_with_data(horizon.humidity),
                 external_heat_kw=(
                     np.asarray(wood_kw, dtype=float)
                     if wood_kw is not None else None
diff --git a/custom_components/heatpump_optimizer/duty_legs.py b/custom_components/heatpump_optimizer/duty_legs.py
index 99df5c4b4e..bfa9caf15c 100644
--- a/custom_components/heatpump_optimizer/duty_legs.py
+++ b/custom_components/heatpump_optimizer/duty_legs.py
@@ -6,13 +6,14 @@ the optimizer prices the switches that serving makes, so two modules need one
 rule and neither may import the other. A leaf: numpy, the plan's running rule
 and the step width, nothing of Home Assistant.
 
-A switch between duties at constant draw is invisible to the cycling term,
-which prices the swing of the combined draw. On an install whose compressor
-stops at such a switch (pull request 3420, Bankaifan: hot water to heating,
-three times out of three) the stop turns the swing ``|a - b|`` into ``a + b``.
-The difference, ``2 * min(a, b)``, is ``min(a, b) / p_max`` cycles in the
-cycling term's own unit, and that is the weight a switch carries here, taken
-with the learned probability that the direction stops the compressor.
+A switch between duties inside a run is invisible to the start term, which
+counts the off-to-on edges of the combined draw (``runs``). On an install
+whose compressor stops at such a switch (pull request 3420, Bankaifan: hot
+water to heating, three times out of three) the stop is a start the plan did
+not count. A switch between the levels ``a`` and ``b`` weighs
+``min(a, b) / p_max`` cycles, taken with the learned probability that the
+direction stops the compressor; weighed at ``p_max`` times the running share
+it is that probability of one start.
 
 A pair of per-direction values is always ``(hot water to heating, heating to
 hot water)``.
@@ -24,7 +25,7 @@ from typing import Any
 
 import numpy as np
 
-from .batchmath import row_sums
+from .batchmath import AFTER as _AFTER, BEFORE as _BEFORE, row_sums
 from .plan_step import PLAN_STEP_MINUTES
 from .thermal_model import MIN_RUNNING_DRAW_KW
 
@@ -148,11 +149,6 @@ def priced_pair(values: Any, upper: float = math.inf) -> tuple[float, float]:
     return a, b
 
 
-#: A boundary pairs each step but the last with the step after it; the legs
-#: that meet there and the levels they run at are read through the same pair.
-_BEFORE, _AFTER = np.s_[:, :-1], np.s_[:, 1:]
-
-
 def switch_weights_batch(
     space_matrix: np.ndarray,
     dhw_kw: np.ndarray,
@@ -160,21 +156,28 @@ def switch_weights_batch(
     p_max: float,
     floor: float | None = None,
     rule: LegRule = DEFAULT_RULE,
+    *,
+    level: np.ndarray | None = None,
 ) -> np.ndarray:
     """Expected compressor stops at duty switches, in cycles, per row of plans.
 
     Every pair of consecutive legs of different duty with no idle step
     between weighs ``p * level / p_max``, in the direction ``rule`` orders the
     legs: inside a two-leg step both legs run at the step's combined level; across a boundary the stop adds the smaller
-    of the two levels. ``row_sums`` reduces each row on its own, so a row is
-    :func:`switch_weight` of that plan bit for bit.
+    of the two levels. ``level`` is what the pairs are weighed at, the
+    combined draw unless given: ``p_max`` times the running share
+    (``runs.running_share``) weighs a pair in starts, so a boundary's switch
+    weight and its start share never sum past one start. ``row_sums`` reduces
+    each row on its own, so a row is :func:`switch_weight` of that plan bit
+    for bit.
     """
     space = np.asarray(space_matrix, dtype=float)
     p_ds, p_sd = stop_probability
     if p_max <= 0:
         return np.zeros(space.shape[0])
     first, last, two = leg_ends(space, dhw_kw, floor, rule=rule)
-    level = space + np.asarray(dhw_kw, dtype=float)
+    if level is None:
+        level = space + np.asarray(dhw_kw, dtype=float)
     before, after = last[_BEFORE], first[_AFTER]
     stops = np.where(
         (before == DHW) & (after == SPACE),
@@ -193,10 +196,13 @@ def switch_weight(
     p_max: float,
     floor: float | None = None,
     rule: LegRule = DEFAULT_RULE,
+    *,
+    level: np.ndarray | None = None,
 ) -> float:
     """The one-row case of :func:`switch_weights_batch`."""
     return float(switch_weights_batch(
-        np.asarray(space_kw, dtype=float)[None, :], dhw_kw, stop_probability, p_max, floor, rule
+        np.asarray(space_kw, dtype=float)[None, :], dhw_kw, stop_probability, p_max, floor, rule,
+        level=None if level is None else np.asarray(level, dtype=float)[None, :],
     )[0])
 
 
diff --git a/custom_components/heatpump_optimizer/duty_switch.py b/custom_components/heatpump_optimizer/duty_switch.py
index 824b0b5f6d..9851bc3071 100644
--- a/custom_components/heatpump_optimizer/duty_switch.py
+++ b/custom_components/heatpump_optimizer/duty_switch.py
@@ -58,6 +58,7 @@ from . import duty_legs, pump_mode, running_signal
 from .const import DOMAIN
 from .drift import stored_instant, utc_elapsed_seconds
 from .store import QuarantiningStore
+from .thermal_model import planned_draw_runs
 
 _LOGGER = logging.getLogger(__name__)
 
@@ -442,6 +443,8 @@ class _Record:
     #: The both step whose legs were decided, and the legs, latched so
     #: neither the tick nor a re-solve inside the step flips them.
     order: tuple[datetime, duty_legs.Legs] | None = None
+    #: Whether the compressor ran as the last scheduled solve started (:func:`running_now`).
+    solved_running: bool = False
 
     def feed(self, edge: tuple[datetime, bool | None] | None) -> None:
         """Hand a confirmed edge, if any, to the learner."""
@@ -537,6 +540,25 @@ def both_step_duty(rec: _Record, start: datetime, now: datetime, space_kw: float
     return legs[0][0] if now - start < timedelta(minutes=legs[0][1]) else legs[-1][0]
 
 
+def running_now(rec: _Record, action: Any) -> bool:
+    """Whether the compressor runs as a scheduled solve starts, for the plan's start count.
+
+    The running signal's settled class with no change pending
+    (:func:`running_signal.running_now`); otherwise the executing step's
+    planned draw (``action``, the coordinator's current one) by the plan's
+    own running rule. Never the
+    start counter, which follows one sample per interval. The record keeps
+    the reading (``solved_running``) for a solve compared against that plan:
+    a what-if's start count stands beside the live plan's on the card, and
+    read afresh, a compressor that started in between would move it by one.
+    """
+    running = running_signal.running_now(rec.signal)
+    if running is None:
+        running = planned_draw_runs(float(action.get("power", 0.0)), float(action.get("dhw_power", 0.0)))
+    rec.solved_running = running
+    return running
+
+
 def planner_fields(coord: Any) -> dict[str, tuple[float, float]]:
     """The ``OptimizationConfig`` fields a solve prices a duty switch by; a pump never arbitrated reads zeros."""
     rec = _RECORDS.get(coord)
diff --git a/custom_components/heatpump_optimizer/early_cutoff.py b/custom_components/heatpump_optimizer/early_cutoff.py
index d5e13e636d..95baee29fa 100644
--- a/custom_components/heatpump_optimizer/early_cutoff.py
+++ b/custom_components/heatpump_optimizer/early_cutoff.py
@@ -81,7 +81,8 @@ from .const import MODE_AUTO, MODE_ECONOMY, ROOM_AIR_RANGE_C
 from .entry_config import EntryConfig
 from .inputs import parse_bool, temperature_c
 from .pump_arbiter import ArbiterInputs, step_duty, supply_switch, switch_supply
-from .supply_hold import MIN_PAUSE, MIN_RUN, switch_age, tank_reason
+from .runs import MIN_PAUSE, MIN_RUN
+from .supply_hold import switch_age, tank_reason
 
 _LOGGER = logging.getLogger(__name__)
 
diff --git a/custom_components/heatpump_optimizer/optimizer.py b/custom_components/heatpump_optimizer/optimizer.py
index 5a35bfbafb..267dd9e530 100644
--- a/custom_components/heatpump_optimizer/optimizer.py
+++ b/custom_components/heatpump_optimizer/optimizer.py
@@ -16,7 +16,7 @@ for the compressor.
 
     grid_cost(P_space + P_dhw)        piecewise in PV surplus, × price_weight
     + comfort terms                   pull-to-target, floor/ceiling penalties
-    + (cycling + capacity tariff)     × price_weight
+    + (starts + capacity tariff)      × price_weight
     + terminal cost                   value of heat stored at the horizon end
 
 Every term but the comfort penalties is in currency. There used to be one more
@@ -24,12 +24,13 @@ Every term but the comfort penalties is in currency. There used to be one more
 because it was priced in invented units and cost real money: about 5 % of the
 two-zone winter bill, at no reduction in compressor starts. Discouraging
 chatter is `cycling_cost`'s job, and that is denominated in currency per
-start-stop cycle, so the trade against electricity is one the user can read.
+start, so the trade against electricity is one the user can read.
 
 subject to 0 ≤ P_space[k] ≤ P_max − P_dhw[k] (the pump can be off; values
-below its modulation floor read as duty cycling within the step, unless the
-install probe says the write surface cannot realize that and
-``clamp_planned_levels`` projects them onto ``{0} ∪ [p_min, p_max]``) and the
+below its modulation floor read as duty cycling within the step, unless a
+start has a price or the install probe says the write surface cannot realize
+that (``clamp_planned_levels``): the plan is then committed to runs in
+``{0} ∪ [p_min, p_max]``, ``_commit_runs``) and the
 thermal dynamics of the configured model. Comfort bounds are soft penalties,
 not constraints — a hard band could make a cold morning infeasible.
 
@@ -130,7 +131,7 @@ from .tariff import (
     window_factors,
 )
 from .dhw_schedule import format_resolved_day_spec
-from . import duty_legs
+from . import duty_legs, runs
 
 _LOGGER = logging.getLogger(__name__)
 
@@ -190,9 +191,67 @@ def _realize_joint(
     return project_space_against(space, tank, p_min, p_max), tank
 
 
-def _scores_rounded(opt: HeatPumpOptimizer) -> bool:
-    """Whether the objective scores the levels that ship rounded."""
-    return opt.config.clamp_planned_levels and not opt._levels_relaxed
+def _engaged(opt: HeatPumpOptimizer) -> bool:
+    """A start has a price, or the install cannot duty-cycle: the solve plans runs.
+
+    Engaged, a solve descends on the relaxed objective and ships the best of
+    :func:`_commit_runs`' candidates; unengaged it is the duty-cycle reading,
+    with no start term to price.
+    """
+    return opt.config.cycling_cost > 0 or opt.config.clamp_planned_levels
+
+
+#: The objectives a multi-start descends on in place of the true one
+#: (:func:`_descent_pair`): without the start term, and without the
+#: duty-switch term as well.
+_RELAXED, _UNPRICED = "relaxed", "unpriced"
+
+
+def _descent_pair(
+    opt: HeatPumpOptimizer, objective: Callable[..., float], objective_batch: Callable[..., np.ndarray],
+    descent: str = _RELAXED,
+) -> tuple[Callable[..., float], Callable[..., np.ndarray]]:
+    """The objective and batch twin a solve's multi-start descends on.
+
+    An engaged solve's are the relaxed pair, without the start term: a step's
+    start share ``a[k] * (1 - r[k-1])`` is a product of two neighbouring
+    unknowns, so its gradient in either is zero wherever the other sits at
+    its end, and a descent priced with it stays where its start lay
+    (measured by Bankaifan, pull request 3529). The duty-switch operand
+    stays: every summand of it is a level or the smaller of two, never a
+    product. Unengaged, the pair handed in.
+    """
+    if not _engaged(opt):
+        return objective, objective_batch
+    return partial(objective, descent=descent), partial(objective_batch, descent=descent)
+
+
+def _relaxed_plans(
+    opt: HeatPumpOptimizer, rescope: Callable[[np.ndarray | None], tuple[np.ndarray, _Scope]],
+    scope: _Scope, headroom: np.ndarray, starts: list[np.ndarray], dhw_plan: np.ndarray,
+) -> tuple[Any, list[np.ndarray]]:
+    """The multi-start's result for a space solve beside ``dhw_plan``, and the
+    relaxed plans the candidate stage commits.
+
+    The first is that result. Where a switch has a price (a stop is learned
+    and a start costs) the solve adds the plan a solve that prices no stop
+    descends to, in the bound no stop cuts: the relaxed descent weighs a switch at the combined draw and the
+    true objective in starts, so the descent that avoids a switch can commit
+    to a plan the true objective scores above the one that kept it (measured
+    on R10-DUTY-SWITCH-PLANNER-PRICE's fixture). The true objective judges
+    the candidates of both.
+    """
+    pair = _descent_pair(opt, scope[1], scope[2])
+    res = _multi_start_minimize(
+        pair[0], starts, scope[0], args=(dhw_plan,), maxiter=300, batch_objective=pair[1])
+    plans = [np.clip(res.x, 0.0, headroom)]
+    if opt.config.cycling_cost > 0 and _priced_stops(opt) is not None:
+        free_room, free = rescope(None)
+        pair = _descent_pair(opt, free[1], free[2], _UNPRICED)
+        plans.append(np.clip(_multi_start_minimize(
+            pair[0], [np.minimum(x, free_room) for x in starts], free[0], args=(dhw_plan,),
+            maxiter=300, batch_objective=pair[1]).x, 0.0, free_room))
+    return res, plans
 
 
 def _priced_stops(opt: HeatPumpOptimizer) -> tuple[float, float] | None:
@@ -238,7 +297,7 @@ def _stop_availability(
 
 def _with_stop_availability(
     opt: HeatPumpOptimizer,
-    start: np.ndarray,
+    start: np.ndarray | None,
     dhw_plan: np.ndarray,
     p_max: float,
     objective: Callable[..., float],
@@ -251,9 +310,10 @@ def _with_stop_availability(
     it into the step that follows. The availability vector is constant for
     the solve and is kept on the optimizer beside the requirement, so the
     plan that is adopted publishes with the vector it was scored with. With
-    none, the bound is ``p_max - dhw`` and the objectives the ones handed in.
+    none, the bound is ``p_max - dhw`` and the objectives the ones handed in;
+    so with no ``start``, the solve of an install that prices no stop.
     """
-    avail = opt._space_avail = _stop_availability(opt, start, dhw_plan, p_max)
+    avail = opt._space_avail = None if start is None else _stop_availability(opt, start, dhw_plan, p_max)
     headroom = duty_legs.space_headroom(p_max, dhw_plan, avail, _duty_floor(opt))
     if avail is None:
         return headroom, objective, objective_batch
@@ -265,19 +325,20 @@ def _shipped_and_received(
     space: np.ndarray,
     dhw: np.ndarray | None,
     avail: np.ndarray | None,
+    descent: str | None = None,
 ) -> tuple[np.ndarray, np.ndarray | None, np.ndarray]:
     """The level each circuit ships at, and the space draw the house receives.
 
     The two differ only where a priced stop keeps the compressor off for part
     of a step (``duty_legs.delivered_space``); with no availability vector the
-    received draw is the shipped array itself, the same object. A relaxed
-    start of a clamped install gets the clamped reading on its unrounded
-    level: the stop is the install's, whatever the rounding.
+    received draw is the shipped array itself, the same object. Space is
+    scored as it stands, and what stands is a committed plan
+    (:func:`_commit_runs`); hot water is its planner's, so a clamped install's
+    ships as its projection, which a descent leaves out.
     """
-    space, dhw = _realize_draw(
-        _scores_rounded(opt), space, dhw,
-        opt.model.params.min_electrical_power, opt.model.params.max_electrical_power,
-    )
+    if dhw is not None and opt.config.clamp_planned_levels and not descent:
+        dhw = project_planned_levels(
+            dhw, opt.model.params.min_electrical_power, opt.model.params.max_electrical_power)
     if avail is None or dhw is None:
         return space, dhw, space
     return space, dhw, duty_legs.delivered_space(space, dhw, avail, _duty_floor(opt))
@@ -285,32 +346,58 @@ def _shipped_and_received(
 
 def _switch_cost_fn(
     opt: HeatPumpOptimizer,
-) -> Callable[[np.ndarray, np.ndarray | None], Any]:
-    """The duty-switch term of shipped plans, beside the cycling term.
+) -> Callable[..., Any]:
+    """The duty-switch term of shipped plans, beside the start term.
 
     One entry per row of a ``[B, n]`` batch, a float for one plan: the
     one-row case of the same reduction, so the two agree bit for bit.
     ``None`` when no direction is priced or there is no hot-water plan, and
-    :func:`_with_switch_cost` then adds no operand at all.
+    :func:`_with_switch_cost` then adds no operand at all. The true
+    objective weighs a pair at ``p_max`` times the running share, in starts:
+    a boundary's start share is ``1 - r`` and its switch weight at most
+    ``p * r``, so one stop is never priced twice. The relaxed descent weighs
+    it at the combined draw, which is never more and has a slope above the
+    floor, where the running share is flat; the unpriced descent has none.
     """
     stops, floor, rule = _priced_stops(opt), _duty_floor(opt), _leg_rule(opt)
     p_max, cost = opt.model.params.max_electrical_power, opt.config.cycling_cost
+    p_min = opt.model.params.min_electrical_power
 
-    def switch_cost(space: np.ndarray, dhw: np.ndarray | None) -> Any:
-        if stops is None or dhw is None or not cost > 0:
+    def switch_cost(space: np.ndarray, dhw: np.ndarray | None, descent: str | None = None) -> Any:
+        if stops is None or dhw is None or not cost > 0 or descent == _UNPRICED:
             return None
+        rows = np.atleast_2d(space)
         term = cost * duty_legs.switch_weights_batch(
-            np.atleast_2d(space), dhw, stops, p_max, floor, rule)
+            rows, dhw, stops, p_max, floor, rule,
+            level=None if descent else p_max * runs.running_share(rows + dhw, p_min))
         return term if np.ndim(space) == 2 else float(term[0])
 
     return switch_cost
 
 
 def _with_switch_cost(level_cost: Any, switch_cost: Any) -> Any:
-    """The cycling and capacity terms plus the duty-switch term, when there is one."""
+    """A level cost plus the start term or the duty-switch term, when there is one."""
     return level_cost if switch_cost is None else level_cost + switch_cost
 
 
+def _start_cost_fn(opt: HeatPumpOptimizer, running: bool) -> Callable[[np.ndarray, str | None], Any]:
+    """The start term: ``cycling_cost`` per start of the combined draw (``runs``).
+
+    One entry per row of a ``[B, n]`` batch, a float for one plan. ``None``
+    at zero cost and on a descent (:func:`_descent_pair`), and
+    :func:`_with_switch_cost` then adds no operand.
+    """
+    cost, p_min = opt.config.cycling_cost, opt.model.params.min_electrical_power
+
+    def start_cost(power: np.ndarray, descent: str | None) -> Any:
+        if descent or not cost > 0:
+            return None
+        count = runs.start_count_batch if np.ndim(power) == 2 else runs.start_count
+        return cost * count(power, p_min, running)
+
+    return start_cost
+
+
 def _dhw_build(
     planner: DhwPlanner, h: _Horizon, p_max: float, **extra: Any
 ) -> tuple[Any, np.ndarray]:
@@ -412,43 +499,212 @@ def _avoid_priced_switches(
     return incumbent
 
 
-def _relaxed_starts(
+#: How many of :func:`_commit_runs`' candidates get their levels re-solved,
+#: best first: a constant from the contributor's spike on one install. Every
+#: candidate is scored as it stands in one batch; a re-solve moves levels
+#: inside a candidate's runs and costs an L-BFGS-B run.
+_RESOLVED_CANDIDATES = 2
+
+
+def _projection(
+    opt: HeatPumpOptimizer, space: np.ndarray, dhw: np.ndarray | None,
+    hi: np.ndarray, cycled: np.ndarray,
+) -> np.ndarray:
+    """The per-step projection of a relaxed space plan: each level under the
+    floor raised to it on its own, what a clamped install shipped before
+    runs were committed. On an install that can duty-cycle, a step its cap
+    cannot raise is switched off, or kept where cycling under the cap is the
+    only way it delivers (``cycled``)."""
+    p_min, p_max = opt.model.params.min_electrical_power, opt.model.params.max_electrical_power
+    if opt.config.clamp_planned_levels:
+        return _realize_draw(True, space, dhw, p_min, p_max)[0]
+    raised = project_space_against(space, 0.0 if dhw is None else dhw, runs.floor_kw(p_min), p_max)
+    return np.where(cycled, space, np.where(raised > hi, 0.0, raised))
+
+
+def _run_plans(
+    opt: HeatPumpOptimizer, h: _Horizon, space: np.ndarray, other: np.ndarray,
+    lo: np.ndarray, hi: np.ndarray, cycled: np.ndarray,
+) -> list[np.ndarray]:
+    """:func:`_commit_runs`' candidates beside the projection.
+
+    Each band's ``runs.commit`` mask of the combined draw, at the relaxed
+    levels with a step the mask adds at the floor, and the relaxed plan
+    itself where it already runs. ``other`` is the hot water beside the
+    plan. A committed space step runs at the floor or above on its own;
+    beside a hot-water charge, only where the relaxed plan asked for half
+    the floor. A forced-on pin, an off window and a cap under the floor are
+    held by every mask.
+    """
+    floor = runs.floor_kw(opt.model.params.min_electrical_power)
+    heats = (hi >= floor) & ((other <= 0.0) | (space >= floor / 2.0))
+    masks = runs.candidates(
+        space + other, h.prices, floor, hi + other, opt.config.cycling_cost,
+        dt=h.dt, running=h.compressor_running,
+        forced=np.where((other > 0.0) | (lo > 0.0), 1.0, np.where(hi + other <= 0.0, 0.0, np.nan)),
+    )
+    idle = np.where(cycled, space, lo)
+    plans = [np.where(m & heats, np.clip(space, np.maximum(lo, floor), hi), idle) for m in masks]
+    if runs.realizable(np.where(cycled, 0.0, space), floor):
+        plans.append(space)
+    return plans
+
+
+def _run_bounds(
+    plan: np.ndarray, lo: np.ndarray, hi: np.ndarray, floor: float,
+) -> list[tuple[float, float]]:
+    """The bounds a candidate's levels are re-solved in: its runs as pins.
+
+    Built by ``_apply_pins_to_bounds`` from the mask and never through the
+    horizon's manual pins, whose safety release would report a committed
+    step as a released pin. A step that is neither off nor at the floor
+    (cycled under a cap, or beside a charge) is held as it stands, so the
+    start count is constant inside the bounds.
+    """
+    on, off = plan >= floor - 1e-9, plan <= 0.0
+    pinned = _apply_pins_to_bounds(
+        list(zip(lo.tolist(), hi.tolist())), np.where(on, 1.0, np.where(off, 0.0, np.nan)), floor)
+    return [b if on[i] or off[i] else (float(plan[i]), float(plan[i])) for i, b in enumerate(pinned)]
+
+
+#: What one space solve is bounded and scored by: its bounds, its objective
+#: and batch twin, and the availability vector the two carry.
+_Scope = tuple[list[tuple[float, float]], Callable[..., float], Callable[..., np.ndarray], "np.ndarray | None"]
+
+
+def _space_scope(
+    opt: HeatPumpOptimizer, h: _Horizon, start: np.ndarray | None, dhw_plan: np.ndarray, p_max: float,
+    objective: Callable[..., float], objective_batch: Callable[..., np.ndarray],
+) -> tuple[np.ndarray, _Scope]:
+    """Space heating's headroom beside ``dhw_plan`` for a solve started from
+    ``start``, and the scope that solve is held to, pins applied. With no
+    ``start``, those of a solve that prices no stop."""
+    headroom, objective, objective_batch = _with_stop_availability(
+        opt, start, dhw_plan, p_max, objective, objective_batch)
+    if h.power_caps is not None:
+        headroom = np.minimum(headroom, h.power_caps)
+    if h.power_caps_extra is not None:
+        # power_caps bounds space heating alone, so during a DHW block
+        # space + DHW could still exceed an external *total* cap. The
+        # fuse guard's whole promise is that total draw stays under
+        # the limit, so subtract the block from the cap here too.
+        headroom = np.minimum(headroom, np.maximum(0.0, h.power_caps_extra - dhw_plan))
+    # Manual space pins apply here just as in the DHW-free path. Forcing
+    # a step on raises its lower bound, but only as far as the headroom
+    # the DHW block left it — a slot the user pinned for both channels
+    # cannot demand more than the compressor has.
+    bounds = _apply_pins_to_bounds(
+        [(0.0, float(v)) for v in headroom], h.space_pins, opt._pin_on_power(p_max))
+    return headroom, (bounds, objective, objective_batch, opt._space_avail)
+
+
+def _stage_box(
+    opt: HeatPumpOptimizer, bounds: list[tuple[float, float]], dhw: np.ndarray | None,
+) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
+    """A scope's bounds as the candidate stage reads them, the hot water
+    beside the plan, and the steps that stay as solved.
+
+    On a clamped install the tank ships as its projection, and space may not
+    pass what that leaves. Under a cap below the floor an install that can
+    duty-cycle delivers only by cycling: such a step stays as solved, in
+    every candidate.
+    """
+    p_min, p_max = opt.model.params.min_electrical_power, opt.model.params.max_electrical_power
+    lo, hi = (np.array(b, dtype=float) for b in zip(*bounds))
+    other = np.zeros_like(hi)
+    if dhw is not None:
+        other = project_planned_levels(dhw, p_min, p_max) if opt.config.clamp_planned_levels else dhw
+        hi = np.minimum(hi, np.maximum(p_max - other, 0.0))
+        lo = np.minimum(lo, hi)
+    cycled = (not opt.config.clamp_planned_levels) & (other <= 0.0) & (hi < runs.floor_kw(p_min))
+    return lo, hi, other, cycled
+
+
+def _resolved_runs(
+    opt: HeatPumpOptimizer, dhw: np.ndarray | None, maxiter: int,
+    scoped: list[tuple[np.ndarray, _Scope]],
+) -> tuple[float, np.ndarray, _Scope]:
+    """The best of one L-BFGS-B run per plan, each inside its own runs
+    (:func:`_run_bounds`) and scope, polished once: its score, the plan and
+    the scope it was scored in."""
+    floor, args = runs.floor_kw(opt.model.params.min_electrical_power), () if dhw is None else (dhw,)
+    found = []
+    for plan, scope in scoped:
+        lo, hi, _, _ = _stage_box(opt, scope[0], dhw)
+        box = _run_bounds(plan, lo, hi, floor)
+        run = _lbfgsb_run(scope[1], scope[2], plan, box, args, maxiter)
+        found.append((float(scope[1](np.asarray(run.x, dtype=float), *args)), run, box, scope))
+    _, run, box, scope = min(found, key=lambda c: c[0])
+    x = np.asarray(_lbfgsb_restart(run, scope[1], box, args, maxiter, scope[2]).x, dtype=float)
+    return float(scope[1](x, *args)), x, scope
+
+
+def _best_runs(
+    opt: HeatPumpOptimizer, h: _Horizon, scope: _Scope, space: np.ndarray, dhw: np.ndarray | None,
+    first: np.ndarray, maxiter: int, rescope: Callable[[np.ndarray], _Scope] | None,
+) -> tuple[float, np.ndarray, _Scope]:
+    """The lowest-scoring committed form of one relaxed plan: its score, the
+    plan and the scope it was scored in.
+
+    ``first``, the plan's projection, and :func:`_run_plans`' candidates are
+    scored on the true objective, start term included, and the best
+    :data:`_RESOLVED_CANDIDATES` have their levels re-solved inside their
+    own runs (:func:`_resolved_runs`). ``rescope`` gives each candidate the
+    scope of a solve started from it, and holds it to that bound: a priced
+    stop's lost running time belongs to the switches the candidate makes,
+    which are not those of the relaxed solve's start.
+    """
+    args = () if dhw is None else (dhw,)
+    lo, hi, other, cycled = _stage_box(opt, scope[0], dhw)
+    plans = [first, *_run_plans(opt, h, space, other, lo, hi, cycled)]
+    plans = [x for i, x in enumerate(plans) if not any(np.array_equal(x, y) for y in plans[:i])]
+    if rescope is None:
+        scoped = [(x, scope) for x in plans]
+        scores = np.asarray(scope[2](np.array(plans), *args), dtype=float)
+    else:
+        scopes = [rescope(x) for x in plans]
+        scoped = [(np.clip(x, *_stage_box(opt, sc[0], dhw)[:2]), sc) for x, sc in zip(plans, scopes)]
+        scores = np.array([float(sc[1](x, *args)) for x, sc in scoped])
+    order = np.argsort(scores, kind="stable")
+    resolved = _resolved_runs(opt, dhw, maxiter, [scoped[i] for i in order[:_RESOLVED_CANDIDATES]])
+    return min((float(scores[order[0]]), *scoped[order[0]]), resolved, key=lambda c: c[0])
+
+
+def _commit_runs(
     opt: HeatPumpOptimizer,
-    objective: Callable[..., float],
-    objective_batch: Callable[..., np.ndarray],
-    bounds: list[tuple[float, float]],
-    first: int,
-    args: tuple[Any, ...],
-    cands: list[np.ndarray],
+    h: _Horizon,
+    scope: _Scope,
+    relaxed: list[np.ndarray],
+    dhw: np.ndarray | None,
     maxiter: int,
-) -> list[np.ndarray]:
-    """``cands`` plus the first structural start refined unrounded.
-
-    On an install whose levels ship projected onto ``{0} ∪ [p_min,
-    p_max]`` the objective scores the projection, so it is flat between 0
-    and ``p_min``: a start descending into that band stalls there with a
-    zero gradient, and the plan books the floor whatever the price spread.
-    One L-BFGS-B run scoring the duty-cycle reading instead -- no flat
-    band -- carries the guess to where heat is cheap; the result rides as
-    one more candidate, which the multi-start refines and ranks on the
-    rounded objective like every other, so what ships is still scored as
-    it ships and is never scored worse than without it. Alternatives that
-    lost: smoothing the projection scores a level the install does not
-    deliver; moving the start in place, as the two-zone continuation does,
-    re-plans through another basin even where this candidate loses; price-
-    ranked seeds at fixed levels moved no stalled plan. Identity on an
-    install that can duty-cycle.
+    rescope: Callable[[np.ndarray], _Scope] | None = None,
+) -> tuple[np.ndarray, _Scope]:
+    """A solve's relaxed plans as runs the pump can run, and the scope the
+    plan that ships was scored in (Bankaifan, pull request 3529).
+
+    Identity on the first relaxed plan unengaged, and where no start has a
+    price and the projection changes nothing. Each relaxed plan is committed
+    on its own (:func:`_best_runs`) and the lowest score ships: a committed
+    plan never scores above the first plan's projection, one more relaxed
+    plan never raises the score, and a failure anywhere in this stage ships
+    that projection.
     """
-    if not opt.config.clamp_planned_levels or first >= len(cands):
-        return cands
-    opt._levels_relaxed = True
+    if not _engaged(opt):
+        return relaxed[0], scope
+    _, hi, _, cycled = _stage_box(opt, scope[0], dhw)
+    first = _projection(opt, relaxed[0], dhw, hi, cycled)
+    if not opt.config.cycling_cost > 0 and np.array_equal(first, relaxed[0]):
+        return relaxed[0], scope
     try:
-        moved = _lbfgsb_run(
-            objective, objective_batch, cands[first], bounds, args, maxiter,
-        )
-    finally:
-        opt._levels_relaxed = False
-    return [*cands, np.asarray(moved.x, dtype=float)]
+        return min((
+            _best_runs(
+                opt, h, scope, space, dhw,
+                first if space is relaxed[0] else _projection(opt, space, dhw, hi, cycled), maxiter, rescope)
+            for space in relaxed
+        ), key=lambda c: c[0])[1:]
+    except Exception as err:  # noqa: BLE001 - the stage is optional: the projection ships
+        _LOGGER.debug("Committing runs failed, the projection ships: %s", err)
+        return first, scope
 
 
 def _padded_nonneg(values: Any, n_steps: int) -> np.ndarray:
@@ -1253,9 +1509,10 @@ def _batch_fd_gradient(
     batched objective's rows are byte-identical to the scalar one --
     which is the batched simulation's contract (issue #97).
 
-    The 97 perturbed schedules are evaluated by ONE call to
-    ``batch_objective``: the simulation, which is nearly the whole cost,
-    runs vectorized across the batch instead of 97 times sequentially.
+    The perturbed schedules, 97 where every one of 96 steps is free, are
+    evaluated by ONE call to ``batch_objective``: the simulation, which is
+    nearly the whole cost, runs vectorized across the batch instead of once
+    per schedule.
 
     A FIXED variable (``lb == ub``) is the one place this deliberately
     departs from scipy (D9-01): there the one-sided rule leaves a zero step
@@ -1274,10 +1531,20 @@ def _batch_fd_gradient(
     differences against that row, so a caller that needs ``f(x0)`` as well
     reads it from the same batch instead of the scalar objective
     (``_fused_value_and_gradient``, R9 D9-s1-02).
+
+    The batch holds one row per FREE variable. A fixed variable's step is
+    zero, so its row would be ``x0`` again: a whole simulated horizon whose
+    value the division then never reads. A committed mask, a full DHW block
+    and a manual plan fix most of the horizon, so those rows were most of
+    such a gradient's cost. The free rows are the same rows as before, and
+    each row's value does not depend on which other rows share its batch
+    (the batched simulation's contract, #97), so no entry moves.
     """
     h, free = _fd_steps(x0, eps, bounds)
     lead = 1 if f0 is None else 0
-    f = batch_objective(_fd_rows(x0, h, lead), *args)
+    if lead == 0 and not free.any():
+        return np.zeros(x0.size, dtype=float)
+    f = batch_objective(_fd_rows(x0, h, lead, free), *args)
     if f0 is None:
         f0 = float(f[0])
     return _fd_divide(f[lead:], f0, x0, h, free)
@@ -1317,25 +1584,26 @@ def _fd_steps(
     return h, free
 
 
-def _fd_rows(x0: np.ndarray, h: np.ndarray, lead: int) -> np.ndarray:
-    """``lead`` copies of ``x0``, then ``x0`` with each variable stepped by ``h``."""
-    n = x0.size
-    rows = np.tile(x0, (lead + n, 1))
-    rows[lead + np.arange(n), np.arange(n)] = x0 + h
+def _fd_rows(
+    x0: np.ndarray, h: np.ndarray, lead: int, free: np.ndarray,
+) -> np.ndarray:
+    """``lead`` copies of ``x0``, then one row per free variable, stepped by ``h``."""
+    stepped = np.flatnonzero(free)
+    rows = np.tile(x0, (lead + stepped.size, 1))
+    rows[lead + np.arange(stepped.size), stepped] = (x0 + h)[stepped]
     return rows
 
 
 def _fd_divide(
     f: np.ndarray, f0: float, x0: np.ndarray, h: np.ndarray, free: np.ndarray,
 ) -> np.ndarray:
-    """The divided differences of the stepped rows' values against ``f0``."""
+    """The free rows' divided differences against ``f0``; 0.0 at a fixed variable."""
     dx = (x0 + h) - x0
-    # ``where=free`` leaves the fixed entries at the 0.0 they start as and
-    # never performs their division, so no 0/0 is computed and no invalid-
-    # value warning is raised. On an all-free bound set this is elementwise
-    # the same IEEE division as before, bit for bit.
+    # ``f`` holds the free variables' rows only (``_fd_rows``), so a fixed
+    # entry keeps the 0.0 it starts as and its 0/0 is never computed. A free
+    # entry is elementwise the IEEE division it always was, bit for bit.
     grad = np.zeros(x0.size, dtype=float)
-    np.divide(f - f0, dx, out=grad, where=free)
+    grad[free] = (f - f0) / dx[free]
     return grad
 
 
@@ -1908,64 +2176,6 @@ def _power_fraction(power: float, params: ThermalParameters) -> float:
     return float(min(1.0, max(0.0, (power - low) / band)))
 
 
-def count_compressor_starts(
-    power: np.ndarray, threshold: float = MIN_RUNNING_DRAW_KW
-) -> int:
-    """Number of off→on transitions in a schedule.
-
-    Measurement first: the backlog note for this feature was explicit that a
-    cycling penalty should only be paid for if realistic plans actually
-    chatter. This is what the validation harness reports, and it is published
-    on the result so the question stays answerable after the fact.
-
-    The default is the plan's own running rule (``MIN_RUNNING_DRAW_KW``, and
-    ``planned_draws_run`` is the same comparison), so the count this publishes
-    and the on schedule beside it on the same result cannot disagree about
-    which steps ran (R9 D12-s2-01).
-    """
-    running = np.asarray(power, dtype=float) > threshold
-    if running.size == 0:
-        return 0
-    starts = int(running[0])
-    starts += int(np.sum(running[1:] & ~running[:-1]))
-    return starts
-
-
-#: numpy's pairwise-summation block: a reduction longer than this is split in
-#: two (at a multiple of 8) and each half summed on its own.
-
-
-def cycling_penalty(
-    power: np.ndarray, cost_per_cycle: float, p_max: float
-) -> float:
-    """Smooth stand-in for a per-start cost.
-
-    ``sum |ΔP|`` over the schedule counts total power swing. One complete
-    start-stop cycle at full power contributes ``2·p_max``, so dividing by that
-    expresses the L1 term in units of whole cycles and makes ``cost_per_cycle``
-    mean what its name says. The one-row case of ``cycling_penalty_batch``.
-    """
-    return float(cycling_penalty_batch(
-        np.asarray(power, dtype=float)[None, :], cost_per_cycle, p_max
-    )[0])
-
-
-def cycling_penalty_batch(
-    power_matrix: np.ndarray, cost_per_cycle: float, p_max: float
-) -> np.ndarray:
-    """``cycling_penalty`` for a [B, n] batch of plans, one entry per row (#948).
-
-    The swings are elementwise and ``row_sums`` reduces them in numpy's own
-    order, so each row is the scalar penalty bit for bit on every backend
-    without a per-row interpreter loop (RC-sw1).
-    """
-    shape = np.shape(power_matrix)
-    if cost_per_cycle <= 0 or p_max <= 0 or shape[1] < 2:
-        return np.zeros(shape[0])
-    swing = row_sums(np.abs(np.diff(np.asarray(power_matrix, dtype=float), axis=1)))
-    return cost_per_cycle * swing / (2.0 * p_max)
-
-
 # ---------------------------------------------------------------------------
 # Plan reason codes (item 16): the codes and which of them mean idle are the
 # payload's vocabulary (``IDLE_REASONS``), because the settlement reads the
@@ -2464,12 +2674,12 @@ class OptimizationConfig:
     # defrost penalty. Nothing in either optimizer path used to stop a plan
     # from chattering between steps.
     #
-    # Modelled as a smooth L1 term on the step-to-step power difference rather
-    # than a true minimum-runtime constraint. The L1 keeps the problem
-    # continuous and cheap; a minimum-runtime constraint would make it a MILP,
-    # which is not affordable inside a 30-second Home Assistant update on the
-    # hardware this usually runs on.
-    #: Currency cost attributed to one full start-stop cycle.
+    # Priced as the plan's start count (``runs.start_count``) on candidates
+    # committed to runs after a relaxed solve (``_commit_runs``), rather than
+    # as a minimum-runtime constraint: that would make it a MILP, which is not
+    # affordable inside a 30-second Home Assistant update on the hardware
+    # this usually runs on.
+    #: Currency cost attributed to one compressor start.
     #: Mirrors ``const.DEFAULT_CYCLING_COST`` rather than restating it, so the
     #: objective a harness builds directly is the objective that ships. The two
     #: had silently drifted apart once before, which meant the tests were
@@ -2742,6 +2952,8 @@ class _Horizon:
     comfort_floors: np.ndarray | None = None
     mold_floors: np.ndarray | None = None
     away_floor_drops: np.ndarray | None = None
+    #: ``SolveInputs.compressor_running``.
+    compressor_running: bool = False
 
     @property
     def timestamps(self) -> list[datetime]:
@@ -2805,6 +3017,9 @@ class SolveInputs:
     #: schedule would have it (``_held_reference``), not as measured, so the
     #: cost carries no one-off coast or heat-up. The what-if's steady pair.
     held_start: bool = False
+    #: The compressor runs at solve time: a run that continues from it is no
+    #: start, in the start term and in the published count alike.
+    compressor_running: bool = False
 
 
 def _horizon_weather(series: ForecastSeries, n_steps: int) -> WeatherSeries:
@@ -3132,8 +3347,6 @@ class HeatPumpOptimizer:
     #: 0.5 for the continuation ``_optimize_space_only`` runs on its first
     #: start -- see there.
     _floor_l1_scale = 1.0
-    #: True while :func:`_relaxed_starts` scores the duty-cycle reading.
-    _levels_relaxed = False
 
     def __init__(
         self,
@@ -3626,7 +3839,7 @@ class HeatPumpOptimizer:
         # The published grid figures are folded at ``h.start_time``
         # (``_grid_report``); only the baseline load array is wanted here.
         baseline_load = self.config.baseline_load_array(h.n_steps)
-        grid = self._grid_report(total_power, baseline_load, h.dt, h.start_time)
+        grid = self._grid_report(total_power, baseline_load, h.dt, h.start_time, h.compressor_running)
         upper_setpoints, lower_setpoints = self._zone_setpoints(space_power)
         room = upper_temps if self.model.params.two_zone_enabled else room_temps
 
@@ -3857,37 +4070,22 @@ class HeatPumpOptimizer:
 
     def _grid_terms(
         self, n_steps: int, dt: float, start_time: datetime | None = None
-    ) -> tuple[
-        Callable[[np.ndarray], float],
-        Callable[[np.ndarray], float],
-        np.ndarray,
-        Callable[[np.ndarray], np.ndarray],
-        Callable[[np.ndarray], np.ndarray],
-    ]:
-        """Closures for the cycling and capacity-tariff penalties.
+    ) -> tuple[Callable[[np.ndarray], float], Callable[[np.ndarray], np.ndarray]]:
+        """The capacity-tariff penalty and its batch twin.
 
-        Both are shared between the space-only and DHW paths. Keeping them in
-        one place is not just tidiness: the previous divergence between the two
+        Shared between the space-only and DHW paths. Keeping it in one place
+        is not just tidiness: the previous divergence between the two
         objectives meant that simply enabling hot water changed the space
         heating objective, which is a class of bug worth designing out.
 
-        Each scalar closure comes with its batch twin (#948), the same
-        penalty over a [B, n] matrix of plans with one entry per row. The
-        twins close over exactly the arguments the scalar closures close
-        over -- one tariff, one offset, one factor walk -- so a twin cannot
-        diverge from its scalar by configuration.
+        The batch twin (#948) is the same penalty over a [B, n] matrix of
+        plans with one entry per row. It closes over exactly the arguments
+        the scalar closure closes over -- one tariff, one offset, one factor
+        walk -- so it cannot diverge from its scalar by configuration.
         """
-        cfg = self.config
-        p_max = self.model.params.max_electrical_power
-        baseline = cfg.baseline_load_array(n_steps)
+        baseline = self.config.baseline_load_array(n_steps)
         bill = self._peak_billing(n_steps, dt, start_time)
 
-        def cycling(power: np.ndarray) -> float:
-            return cycling_penalty(power, cfg.cycling_cost, p_max)
-
-        def cycling_batch(power_matrix: np.ndarray) -> np.ndarray:
-            return cycling_penalty_batch(power_matrix, cfg.cycling_cost, p_max)
-
         # One billing record for the scalar closure and its batch twin, so
         # the two can never disagree about the tariff they are pricing. The
         # term the SOLVER minimizes is the smooth surrogate (#232/#1210): on
@@ -3904,7 +4102,7 @@ class HeatPumpOptimizer:
         def capacity_batch(total_power_matrix: np.ndarray) -> np.ndarray:
             return peak_cost_batch(total_power_matrix, baseline, bill)
 
-        return cycling, capacity, baseline, cycling_batch, capacity_batch
+        return capacity, capacity_batch
 
     def _peak_billing(
         self, n_steps: int, dt: float, start_time: datetime | None
@@ -4287,6 +4485,7 @@ class HeatPumpOptimizer:
                 comfort_floors=floors[0],
                 mold_floors=floors[1],
                 away_floor_drops=away_drops,
+                compressor_running=inputs.compressor_running,
             )
             if dhw_enabled:
                 return self._optimize_with_dhw(horizon, planner)
@@ -4736,28 +4935,12 @@ class HeatPumpOptimizer:
     ) -> tuple[np.ndarray, str, float]:
         """Optimize space heating around a fixed DHW schedule."""
         guess = init_base if warm_start is None else warm_start
-        headroom, objective, objective_batch = _with_stop_availability(
-            self, guess, dhw_plan, p_max, objective, objective_batch)
-        if h.power_caps is not None:
-            headroom = np.minimum(headroom, h.power_caps)
-        if h.power_caps_extra is not None:
-            # power_caps bounds space heating alone, so during a DHW block
-            # space + DHW could still exceed an external *total* cap. The
-            # fuse guard's whole promise is that total draw stays under
-            # the limit, so subtract the block from the cap here too.
-            headroom = np.minimum(
-                headroom,
-                np.maximum(0.0, h.power_caps_extra - dhw_plan),
-            )
+        rescope = partial(
+            _space_scope, self, h, dhw_plan=dhw_plan, p_max=p_max,
+            objective=objective, objective_batch=objective_batch)
+        headroom, scope = rescope(guess)
+        bounds, objective, objective_batch, _ = scope
         guess = np.minimum(np.clip(guess, 0.0, p_max), headroom)
-        bounds = [(0.0, float(headroom[i])) for i in range(n_steps)]
-        # Manual space pins apply here just as in the DHW-free path. Forcing
-        # a step on raises its lower bound, but only as far as the headroom
-        # the DHW block left it — a slot the user pinned for both channels
-        # cannot demand more than the compressor has.
-        bounds = _apply_pins_to_bounds(
-            bounds, h.space_pins, self._pin_on_power(p_max)
-        )
         guess = self._seed_pinned_guess(guess, bounds)
         # A warm start is a genuinely good lead, so keep it first; the
         # extra structural candidates only matter on the initial solve.
@@ -4786,23 +4969,21 @@ class HeatPumpOptimizer:
                     headroom,
                 )
             )
+        descent = _descent_pair(self, objective, objective_batch)[0]
         try:
-            res = _multi_start_minimize(
-                objective, starts, bounds, args=(dhw_plan,), maxiter=300,
-                batch_objective=objective_batch,
-                move_starts=partial(  # the initial solve's alone: a warm pass adds none
-                    _relaxed_starts, self, objective, objective_batch, bounds,
-                    len(h.extra_starts or ()) if warm_start is None else len(starts),
-                    (dhw_plan,),
-                ),
+            res, relaxed = _relaxed_plans(self, rescope, scope, headroom, starts, dhw_plan)
+            power, shipped = _commit_runs(
+                self, h, scope, relaxed, dhw_plan, 300,
+                (lambda start: rescope(start)[1]) if _priced_stops(self) else None,
             )
-            power = np.clip(res.x, 0.0, headroom)
+            # The adopted plan publishes with the vector it was scored with.
+            self._space_avail = shipped[3]
             return (
                 power,
                 _solver_status(
-                    res, lambda x: objective(x, dhw_plan), guess
+                    res, lambda x: descent(x, dhw_plan), guess
                 ),
-                float(objective(power, dhw_plan)),
+                float(shipped[1](power, dhw_plan)),
             )
         except Exception as e:
             # On the first pass the ``failed (...)`` status below reaches the
@@ -4811,6 +4992,7 @@ class HeatPumpOptimizer:
             # keeps the first pass's status and stays at DEBUG, as its sibling
             # except does (R10-N-log-flood, #2337).
             _LOGGER.debug("Space heating optimization (with DHW) failed: %s", e)
+            self._space_avail = scope[3]
             return (
                 guess,
                 f"failed ({e})",
@@ -5138,11 +5320,9 @@ class HeatPumpOptimizer:
         terminal_cost, terminal_cost_batch = self._terminal_cost(
             prices, outdoor_temps, h.solar_gains, h.humidity
         )
-        cycling, capacity, _, cycling_batch, capacity_batch = (
-            self._grid_terms(h.n_steps, dt, h.start_time)
-        )
+        capacity, capacity_batch = self._grid_terms(h.n_steps, dt, h.start_time)
         energy_cost_of = self._energy_cost_fn(prices, dt)
-        switch_cost = _switch_cost_fn(self)
+        start_cost, switch_cost = _start_cost_fn(self, h.compressor_running), _switch_cost_fn(self)
 
         def _space_traj(power_schedule: np.ndarray, buffer_exo_kw: Any = None) -> Any:
             return self.model.simulate_trajectory(
@@ -5159,10 +5339,11 @@ class HeatPumpOptimizer:
             dhw_plan_power: np.ndarray | None = None,
             buffer_exo_kw: np.ndarray | None = None,
             avail: np.ndarray | None = None,
+            descent: str | None = None,
         ) -> float:
             """Compute the total cost with predictive weather anticipation."""
             space_power, dhw_plan_power, heat_power = _shipped_and_received(
-                self, space_power, dhw_plan_power, avail)
+                self, space_power, dhw_plan_power, avail, descent)
             room_temps, slab_temps, upper_temps, lower_temps, buffer_temps, _, _ = (
                 _space_traj(heat_power, buffer_exo_kw)
             )
@@ -5198,8 +5379,8 @@ class HeatPumpOptimizer:
                 # does, or a non-default weight silently re-prices starts and
                 # peaks relative to the electricity they trade against.
                 + float(_with_switch_cost(
-                    cycling(combined) + capacity(combined),
-                    switch_cost(space_power, dhw_plan_power)))
+                    _with_switch_cost(capacity(combined), start_cost(combined, descent)),
+                    switch_cost(space_power, dhw_plan_power, descent)))
                 * self.config.price_weight
                 + terminal_cost(
                     room_temps,
@@ -5215,6 +5396,7 @@ class HeatPumpOptimizer:
             dhw_plan_power: np.ndarray | None = None,
             buffer_exo_kw: np.ndarray | None = None,
             avail: np.ndarray | None = None,
+            descent: str | None = None,
         ) -> np.ndarray:
             """The same objective, for B schedules at once (issue #97).
 
@@ -5227,7 +5409,7 @@ class HeatPumpOptimizer:
             silently.
             """
             space_matrix, dhw_plan_power, heat_matrix = _shipped_and_received(
-                self, space_matrix, dhw_plan_power, avail)
+                self, space_matrix, dhw_plan_power, avail, descent)
             traj = self.model.simulate_trajectory_batch(
                 initial_state=initial_state,
                 power_matrix=heat_matrix,
@@ -5245,8 +5427,8 @@ class HeatPumpOptimizer:
                 traj,
                 grid_power if heat_matrix is space_matrix else heat_matrix + dhw_plan_power,
                 level_cost=_with_switch_cost(
-                    cycling_batch(grid_power) + capacity_batch(grid_power),
-                    switch_cost(space_matrix, dhw_plan_power)),
+                    _with_switch_cost(capacity_batch(grid_power), start_cost(grid_power, descent)),
+                    switch_cost(space_matrix, dhw_plan_power, descent)),
                 energy_cost_of=energy_cost_of,
                 terminal_cost_batch=terminal_cost_batch,
                 comfort_targets=comfort_targets,
@@ -5348,6 +5530,8 @@ class HeatPumpOptimizer:
                     dt,
                 )
             )
+        descent, descent_batch = _descent_pair(self, objective, objective_batch)
+
         def move_starts(
             cands: list[np.ndarray], maxiter: int
         ) -> list[np.ndarray]:
@@ -5363,14 +5547,12 @@ class HeatPumpOptimizer:
             start, it is not one.
             """
             first = len(h.extra_starts or ())
-            cands = _relaxed_starts(self, objective, objective_batch, bounds, first, (),
-                                    cands, maxiter)
             if not self.model.params.two_zone_enabled:
                 return cands
             self._floor_l1_scale = 0.5
             try:
                 cands[first] = np.asarray(_lbfgsb_run(
-                    objective, objective_batch, cands[first], bounds, (),
+                    descent, descent_batch, cands[first], bounds, (),
                     maxiter,
                 ).x, dtype=float)
             finally:
@@ -5382,13 +5564,14 @@ class HeatPumpOptimizer:
 
         try:
             result = _multi_start_minimize(
-                objective, starts, bounds, maxiter=200,
-                batch_objective=objective_batch, move_starts=move_starts,
-            )
-            optimal_power = _published_levels(
-                self.config.clamp_planned_levels, result.x, p_min, p_max
+                descent, starts, bounds, maxiter=200,
+                batch_objective=descent_batch, move_starts=move_starts,
             )
-            status = _solver_status(result, objective, initial_power)
+            optimal_power = _commit_runs(
+                self, h, (bounds, objective, objective_batch, None),
+                [np.asarray(result.x, dtype=float)], None, 200,
+            )[0]
+            status = _solver_status(result, descent, initial_power)
         except Exception as e:
             # The ``failed (...)`` status reaches the coordinator, which
             # reports the failure once through its own latched
@@ -5465,6 +5648,7 @@ class HeatPumpOptimizer:
         baseline_load: np.ndarray,
         dt: float,
         start_time: datetime | None = None,
+        running: bool = False,
     ) -> dict[str, Any]:
         """Peak and cycling figures for the solved plan."""
         bill = self._peak_billing(len(np.asarray(total_power)), dt, start_time)
@@ -5495,7 +5679,7 @@ class HeatPumpOptimizer:
         return {
             "peak_kw": round(peak_kw, 3),
             "peak_cost": round(peak_cost(total_power, baseline_load, bill), 3),
-            "starts": count_compressor_starts(total_power),
+            "starts": runs.edge_count(total_power, running),
         }
 
     def _price_known_list(self, n_steps: int) -> list[bool]:
diff --git a/custom_components/heatpump_optimizer/runs.py b/custom_components/heatpump_optimizer/runs.py
new file mode 100644
index 0000000000..049e4734de
--- /dev/null
+++ b/custom_components/heatpump_optimizer/runs.py
@@ -0,0 +1,247 @@
+"""Compressor starts and runs: what a start is in a plan, and which runs ship.
+
+The finding, the count and the commit program are Bankaifan's (pull request
+3529), rebuilt here on one owner.
+
+A start is an off-to-on edge of the compressor, whatever level it starts to; a
+level change inside a run is none. :func:`start_count` reads them off the
+combined draw ``q``. With ``f`` the pump's running floor, a step runs the
+share ``r = min(1, q / f)`` of itself and needs the compressor running as it
+begins by ``a = min(1, q / MIN_RUNNING_DRAW_KW)``, so it makes the share of a
+start its predecessor left open, ``a[k] * (1 - r[k-1])``. On a plan whose
+steps are all off or at the floor or above, the sum is the integer number of
+off-to-on edges (:func:`edge_count`). A level under the floor is a duty-cycle
+average: it leaves its successor a start to make and makes one itself, so
+cycling under the floor is counted as the starts it is.
+
+:func:`commit` turns a relaxed plan, one that books levels under the floor as
+duty-cycle averages, into an on/off mask of runs and pauses the pump can run
+at the relaxed plan's energy: a step raised to the floor is paid for by a step
+left out, never raised on its own.
+
+A leaf: numpy, ``row_sums`` and the plan's running rule, nothing of Home
+Assistant, so the optimizer, the supply gate and the early cut-off read one
+shortest run and pause.
+"""
+from __future__ import annotations
+
+from datetime import timedelta
+from typing import Any
+
+import numpy as np
+
+from .batchmath import AFTER, BEFORE, row_sums
+from .thermal_model import MIN_RUNNING_DRAW_KW
+
+#: The shortest run and pause: the supply gate lets no write end a younger
+#: one, the early cut-off cuts none, and :func:`candidates` plans none.
+MIN_RUN = timedelta(minutes=10)
+MIN_PAUSE = timedelta(minutes=10)
+
+#: :func:`commit`'s energy bands, in floor steps either side of the relaxed
+#: plan's cumulative energy. These three, :data:`QUANTA_PER_STEP` and
+#: :data:`OUT_OF_BAND` are constants from the contributor's spike on one
+#: install, not measured thresholds.
+BANDS = (2, 6, 24)
+#: The balance grid: cells per floor step of energy.
+QUANTA_PER_STEP = 4
+#: A balance outside its band pays this many times the horizon's dearest
+#: price per kWh outside it: penalised, never refused.
+OUT_OF_BAND = 10.0
+#: What a step pays for leaving the relaxed plan's own on/off reading: a tie
+#: break, so a mask that saves nothing keeps the plan's runs.
+_TIE_BREAK = 1e-9
+#: Float slack on a level or an energy compared against the floor, kW or kWh.
+_SLACK = 1e-9
+
+
+def floor_kw(floor: float) -> float:
+    """The running floor a start is counted against, kW; a configured 0 still
+    runs at ``MIN_RUNNING_DRAW_KW``."""
+    return max(float(floor), MIN_RUNNING_DRAW_KW)
+
+
+def steps_at_least(span: timedelta, dt_hours: float) -> int:
+    """Whole plan steps covering ``span``, at least one."""
+    return max(1, int(np.ceil(span.total_seconds() / 3600.0 / dt_hours - _SLACK)))
+
+
+def running_share(total: Any, floor: float) -> np.ndarray:
+    """``r``: the share of each step the compressor runs at the combined draw."""
+    return np.clip(np.asarray(total, dtype=float) / floor_kw(floor), 0.0, 1.0)
+
+
+def start_count_batch(total: np.ndarray, floor: float, running: bool = False) -> np.ndarray:
+    """The start count of each row of a ``[B, n]`` batch of combined draws.
+
+    ``running``: the compressor runs at solve time, so a run continuing from
+    it is no start. Elementwise up to ``row_sums``, so each row is
+    :func:`start_count` of that plan bit for bit.
+    """
+    rows = np.asarray(total, dtype=float)
+    through = np.empty_like(rows)
+    through[:, 0] = 1.0 if running else 0.0
+    through[AFTER] = running_share(rows, floor)[BEFORE]
+    needs = np.clip(rows / MIN_RUNNING_DRAW_KW, 0.0, 1.0)
+    count: np.ndarray = row_sums(needs * (1.0 - through))
+    return count
+
+
+def start_count(total: Any, floor: float, running: bool = False) -> float:
+    """The one-row case of :func:`start_count_batch`."""
+    return float(start_count_batch(np.asarray(total, dtype=float)[None, :], floor, running)[0])
+
+
+def edge_count(total: Any, running: bool = False) -> int:
+    """The off-to-on edges of a plan by its running rule
+    (``MIN_RUNNING_DRAW_KW``); none at step 0 while the compressor runs."""
+    on = np.asarray(total, dtype=float) > MIN_RUNNING_DRAW_KW
+    return int(np.sum(on & ~np.r_[bool(running), on[:-1]]))
+
+
+def realizable(total: Any, floor: float) -> bool:
+    """Every step off or at the floor or above: the plan runs as it stands."""
+    q = np.asarray(total, dtype=float)
+    return bool(np.all((q <= 0.0) | (q >= floor_kw(floor) - _SLACK)))
+
+
+def commit(
+    q: Any, prices: Any, floor: float, caps: Any, start_cost: float, band: int,
+    *, dt: float, running: bool = False, forced: Any = None,
+    lengths: tuple[int, int] = (1, 1),
+) -> tuple[np.ndarray, bool]:
+    """The on/off mask that runs the relaxed plan ``q`` cheapest, and whether
+    it tracked ``q``'s energy within its band.
+
+    A dynamic program over the steps with the state (on or off, run or pause
+    length up to ``lengths``, energy balance). The balance is the committed
+    energy less ``q``'s up to that step, on a grid of
+    :data:`QUANTA_PER_STEP` cells per floor step, held within ``band`` floor
+    steps and within half a floor step at the end. An on step runs at
+    ``max(q, floor)`` under ``caps`` and pays its price; an off-to-on edge
+    pays ``start_cost``. ``forced`` is the pin encoding (NaN free, 0 off, 1
+    on), and a cap under the floor forces a free step off; a forced step may
+    cut a run or a pause short. A balance outside the band is held at the
+    edge cell and pays :data:`OUT_OF_BAND` for the energy outside: ``False``
+    says the mask left the band, a best effort and never a refusal.
+    """
+    q = np.asarray(q, dtype=float)
+    n = q.size
+    min_on = lengths[0]
+    f = floor_kw(floor)
+    cap = np.broadcast_to(np.asarray(caps, dtype=float), (n,))
+    want = np.full(n, np.nan) if forced is None else np.array(forced, dtype=float)[:n]
+    want = np.where(np.isnan(want) & (cap < f - _SLACK), 0.0, want)
+    level = np.minimum(np.maximum(q, f), cap)
+    price = np.broadcast_to(np.asarray(prices, dtype=float), (n,))
+    quantum = f * dt / QUANTA_PER_STEP
+    half = QUANTA_PER_STEP * int(band)
+    fine = OUT_OF_BAND * max(float(np.max(np.abs(price))), 1e-6)
+    cost = np.full((sum(lengths), 2 * half + 1), np.inf)
+    bal = np.zeros_like(cost)
+    cost[min_on - 1 if running else sum(lengths) - 1, half] = 0.0
+    trail = []
+    for k in range(n):
+        asked = bool(q[k] > 0.0)
+        step = (
+            ((level[k] - q[k]) * dt, price[k] * level[k] * dt + _TIE_BREAK * (not asked)),
+            (-q[k] * dt, _TIE_BREAK * asked),
+        )
+        cost, bal, back = _advance(
+            cost, bal, _moves(*lengths, want[k]), step, float(start_cost), (quantum, half, fine), min_on)
+        trail.append(back)
+    ending = cost + fine * np.maximum(np.abs(bal) - f * dt / 2.0, 0.0)
+    u, j = (int(a) for a in np.unravel_index(np.argmin(ending), ending.shape))
+    mask = np.zeros(n, dtype=bool)
+    for k in range(n - 1, -1, -1):
+        mask[k] = u < min_on
+        u, j = (int(v) for v in trail[k][:, u, j])
+    walk = np.cumsum(np.where(mask, level, 0.0) - q) * dt
+    tracked = bool(
+        np.all(np.abs(walk) <= half * quantum + _SLACK) and abs(walk[-1]) <= f * dt / 2.0 + _SLACK)
+    return mask, tracked
+
+
+def candidates(
+    q: Any, prices: Any, floor: float, caps: Any, start_cost: float,
+    *, dt: float, running: bool = False, forced: Any = None,
+) -> list[np.ndarray]:
+    """:func:`commit`'s distinct masks over :data:`BANDS`, tightest first, at
+    the step counts of :data:`MIN_RUN` and :data:`MIN_PAUSE`.
+
+    Where no band tracks, the whole horizon is one more; every mask is
+    returned, best efforts included, for the true objective to judge.
+    """
+    masks: list[np.ndarray] = []
+    lengths = (steps_at_least(MIN_RUN, dt), steps_at_least(MIN_PAUSE, dt))
+    tracked = False
+    for band in (*BANDS, int(np.size(q))):
+        if tracked and band > BANDS[-1]:
+            break
+        mask, exact = commit(
+            q, prices, floor, caps, start_cost, band, dt=dt, running=running,
+            forced=forced, lengths=lengths,
+        )
+        tracked |= exact
+        if not any(np.array_equal(mask, m) for m in masks):
+            masks.append(mask)
+    return masks
+
+
+def _moves(min_on: int, min_off: int, want: float) -> list[tuple[int, int, bool]]:
+    """``(source, destination, starts)`` state moves one step allows.
+
+    States ``0 .. min_on - 1`` are a run of that many steps plus one (the last
+    one long enough to stop), then the pauses alike. A forced step may leave
+    any run or pause; otherwise only the long-enough one switches.
+    """
+    last_on, states = min_on - 1, min_on + min_off
+    free = bool(np.isnan(want))
+    out: list[tuple[int, int, bool]] = []
+    if not want == 0.0:
+        out += [(i, min(i + 1, last_on), False) for i in range(min_on)]
+        out += [(i, 0, True) for i in range(min_on, states) if not free or i == states - 1]
+    if not want == 1.0:
+        out += [(i, min(i + 1, states - 1), False) for i in range(min_on, states)]
+        out += [(i, min_on, False) for i in range(min_on) if not free or i == last_on]
+    return out
+
+
+def _advance(
+    cost: np.ndarray, bal: np.ndarray, moves: list[tuple[int, int, bool]],
+    step: tuple[tuple[float, float], tuple[float, float]], start_cost: float,
+    grid: tuple[float, int, float], min_on: int,
+) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
+    """One step of :func:`commit`: the cheapest arrival per cell, its exact
+    balance, and where it came from.
+
+    ``step`` is ``(balance change, cost)`` for running and for pausing;
+    ``grid`` is the cell width, the band's half width in cells and the price
+    of a kWh outside the band.
+    """
+    quantum, half, fine = grid
+    width = cost.shape[1]
+    new_cost = np.full_like(cost, np.inf)
+    new_bal = np.zeros_like(bal)
+    back = np.zeros((2,) + cost.shape, dtype=np.int32)
+    cells = np.arange(width)
+    for dest in sorted({m[1] for m in moves}):
+        srcs = [(s, starts) for s, d, starts in moves if d == dest]
+        change, paid = step[0] if dest < min_on else step[1]
+        b = np.concatenate([bal[s] + change for s, _ in srcs])
+        outside = np.maximum(np.abs(b) - half * quantum, 0.0)
+        c = np.concatenate([cost[s] + paid + start_cost * starts for s, starts in srcs]) + fine * outside
+        origin = np.concatenate([np.full(width, s) for s, _ in srcs])
+        came = np.tile(cells, len(srcs))
+        j = np.clip(np.rint(b / quantum).astype(np.int64) + half, 0, 2 * half)
+        ok = np.isfinite(c)
+        if not ok.any():
+            continue
+        c, b, origin, came, j = c[ok], b[ok], origin[ok], came[ok], j[ok]
+        order = np.lexsort((c, j))
+        first = order[np.r_[True, j[order][1:] != j[order][:-1]]]
+        new_cost[dest, j[first]] = c[first]
+        new_bal[dest, j[first]] = b[first]
+        back[0, dest, j[first]] = origin[first]
+        back[1, dest, j[first]] = came[first]
+    return new_cost, new_bal, back
diff --git a/custom_components/heatpump_optimizer/supply_hold.py b/custom_components/heatpump_optimizer/supply_hold.py
index 0bfa4d85ff..7b101d6525 100644
--- a/custom_components/heatpump_optimizer/supply_hold.py
+++ b/custom_components/heatpump_optimizer/supply_hold.py
@@ -41,7 +41,8 @@ so a write on a step boundary after a step-long run or pause is never held.
 (:data:`FREEZE_HELD`), as ``early_cutoff`` freezes a cut one.
 
 The minimums are constants, not options, for the reason ``early_cutoff``
-gives for its margin; ``early_cutoff`` reads them too.
+gives for its margin; they are ``runs``', which ``early_cutoff`` and the
+optimizer read too.
 """
 from __future__ import annotations
 
@@ -55,10 +56,7 @@ from .const import MODE_AUTO, MODE_ECONOMY
 from .entry_config import EntryConfig
 from .plan_step import PLAN_STEP_MINUTES, plan_step_start
 from .pump_arbiter import ArbiterInputs, ArbiterState, step_duty, step_supply, supply_switch
-
-#: The shortest run and pause the gate lets a write end; the early cut-off's too.
-MIN_RUN = timedelta(minutes=10)
-MIN_PAUSE = timedelta(minutes=10)
+from .runs import MIN_PAUSE, MIN_RUN
 
 #: The ``_learning_frozen`` reason for an interval in which a write was held.
 FREEZE_HELD = "supply_held"
diff --git a/custom_components/heatpump_optimizer/thermal_model.py b/custom_components/heatpump_optimizer/thermal_model.py
index 05f21f899b..6760bc994f 100644
--- a/custom_components/heatpump_optimizer/thermal_model.py
+++ b/custom_components/heatpump_optimizer/thermal_model.py
@@ -1185,7 +1185,7 @@ def _dhw_enabled_from_config(config: Mapping[str, Any]) -> bool:
 #: and ``_compute_baseline_power`` says why flooring them would burn
 #: ``min_electrical_power`` around the clock -- so every watt a plan books
 #: above this floor is heat its trajectory, its cost and its published
-#: savings all count as delivered, and it is what ``count_compressor_starts``
+#: savings all count as delivered, and it is what ``runs.edge_count``
 #: counts as a run. No seam that actuates or reports the plan may call such a
 #: step off. Until this owner existed the switch schedule called it off at
 #: half the modulation floor instead (see ``on_threshold_kw``), which on a
diff --git a/dev/audit/harnesses/r10_partload_residue.py b/dev/audit/harnesses/r10_partload_residue.py
index d362b2fdd8..7f06ae3149 100644
--- a/dev/audit/harnesses/r10_partload_residue.py
+++ b/dev/audit/harnesses/r10_partload_residue.py
@@ -10,15 +10,16 @@ is held against is the shortest optimisation interval the options flow
 accepts (``config_flow``'s ``CONF_OPTIMIZATION_INTERVAL`` slider minimum,
 10 min); the default interval is 30 min.
 
-``relaxed``: the relaxed duty-cycle pass (``optimizer._relaxed_starts``) on
-R10-SETPOINT-BOOST's 16 installs, spread and flat price days, at ``d = 0``
-and at the central plant's derate (``r10_partload_pricing.solve``). Two arms
-per cell: production, and the pass removed (``_relaxed_starts`` as
-identity, ``r10_setpoint_boost.solve``'s own perturbation). Printed: the
-seconds spent inside ``_relaxed_starts`` and how many relaxed L-BFGS-B runs
-it started, and the whole solve's seconds at both arms. Null control: the
-cells whose levels do not ship clamped must start 0 relaxed runs; the
-harness exits 1 otherwise.
+``relaxed``: the candidate stage of an engaged solve
+(``optimizer._commit_runs``, which replaced the relaxed duty-cycle pass
+``_relaxed_starts`` in R11-OUTSIDE-HONEST-STARTS-RUNS) on R10-SETPOINT-BOOST's
+16 installs, spread and flat price days, at ``d = 0`` and at the central
+plant's derate (``r10_partload_pricing.solve``). Two arms per cell:
+production, and the stage removed (its candidates refused, so it ships the
+projection). Printed: the seconds spent inside ``_commit_runs`` and how many
+L-BFGS-B runs it started, and the whole solve's seconds at both arms. Null
+control: the cells whose levels do not ship clamped must start 0 such runs;
+the harness exits 1 otherwise.
 
 ``buffer N``: the live buffer store's solve cost, one lever at a time:
 ``r10_buffer_store.solve``'s owner shape (750 L behind a manual valve, slab,
@@ -99,26 +100,40 @@ def central_derate() -> float:
 
 
 def timed_solve(cell, prices, derate: float, relaxed: bool) -> tuple[float, float, int]:
-    """(solve s, seconds inside the relaxed pass, relaxed runs started)."""
-    kept = opt_mod._relaxed_starts
-    seen = {"s": 0.0, "runs": 0}
+    """(solve s, seconds inside the candidate stage, L-BFGS-B runs it started)."""
+    kept, kept_plans = opt_mod._commit_runs, opt_mod._run_plans
+    kept_run, kept_restart = opt_mod._lbfgsb_run, opt_mod._lbfgsb_restart
+    seen = {"s": 0.0, "runs": 0, "inside": False}
 
-    def wrapped(opt, objective, objective_batch, bounds, first, args, cands, maxiter):
-        if not relaxed:
-            return cands
+    def refused(*_args):
+        raise RuntimeError("control arm: the stage ships its projection")
+
+    def counted(real):
+        def run(*args, **kwargs):
+            seen["runs"] += seen["inside"]
+            return real(*args, **kwargs)
+        return run
+
+    def wrapped(*args):
+        seen["inside"] = True
         t = time.process_time()
-        out = kept(opt, objective, objective_batch, bounds, first, args, cands, maxiter)
-        seen["s"] += time.process_time() - t
-        seen["runs"] += len(out) - len(cands)
-        return out
+        try:
+            return kept(*args)
+        finally:
+            seen["s"] += time.process_time() - t
+            seen["inside"] = False
 
-    opt_mod._relaxed_starts = wrapped
+    opt_mod._commit_runs = wrapped
+    opt_mod._lbfgsb_run, opt_mod._lbfgsb_restart = counted(kept_run), counted(kept_restart)
+    if not relaxed:
+        opt_mod._run_plans = refused
     try:
         t = time.process_time()
         pp.solve(cell, prices, derate)
         return time.process_time() - t, seen["s"], seen["runs"]
     finally:
-        opt_mod._relaxed_starts = kept
+        opt_mod._commit_runs, opt_mod._run_plans = kept, kept_plans
+        opt_mod._lbfgsb_run, opt_mod._lbfgsb_restart = kept_run, kept_restart
 
 
 def relaxed() -> int:
@@ -133,9 +148,9 @@ def relaxed() -> int:
                 on, inside, runs = timed_solve(cell, prices, d, True)
                 off, _, _ = timed_solve(cell, prices, d, False)
                 clamped = cell[3]
-                print(f"  {tag} {cell} d={d} clamped {clamped} relaxed_runs {runs}"
-                      f" relaxed_pass_s {inside:.3f} solve_s {on:.3f}"
-                      f" pass_removed_solve_s {off:.3f} delta_s {on - off:+.3f}")
+                print(f"  {tag} {cell} d={d} clamped {clamped} stage_runs {runs}"
+                      f" stage_s {inside:.3f} solve_s {on:.3f}"
+                      f" stage_removed_solve_s {off:.3f} delta_s {on - off:+.3f}")
                 if clamped:
                     clamped_solves.append(on)
                     clamped_pass.append(inside)
@@ -143,9 +158,9 @@ def relaxed() -> int:
                     null_bad += 1
     a, b = np.array(clamped_solves), np.array(clamped_pass)
     print(f"clamped solves {a.size}: solve_s p50 {np.median(a):.3f} max {a.max():.3f};"
-          f" relaxed_pass_s p50 {np.median(b):.3f} max {b.max():.3f};"
+          f" stage_s p50 {np.median(b):.3f} max {b.max():.3f};"
           f" worst solve share of budget {a.max() / BUDGET_S:.5f}")
-    print(f"null (unclamped) cells with a relaxed run {null_bad}")
+    print(f"null (unclamped) cells with a stage run {null_bad}")
     return 1 if null_bad else 0
 
 
diff --git a/dev/audit/harnesses/r10_setpoint_boost.py b/dev/audit/harnesses/r10_setpoint_boost.py
index d7ebbadfd4..ae2182793a 100644
--- a/dev/audit/harnesses/r10_setpoint_boost.py
+++ b/dev/audit/harnesses/r10_setpoint_boost.py
@@ -20,8 +20,8 @@ harness runs in (a tree without a symbol falls back to what main does):
 3. ``solves`` (skipped with ``--no-solves``): 16 synthetic installs -- UA
    scale 0.6/1.7 x 750 L buffer or none x hot water off/on x set-point-driven
    (levels ship rounded) or duty-cycling -- each solved at one spread price
-   day starting 21:00 and at its flat mean, with and without #2445's relaxed
-   start. Printed per cell and price: the sha1 of the published plan (the
+   day starting 21:00 and at its flat mean, with and without the relaxed
+   descent (#2445's relaxed start until R11-OUTSIDE-HONEST-STARTS-RUNS). Printed per cell and price: the sha1 of the published plan (the
    byte-identity null across trees), the objective delta of the relaxed
    start, the share of space kWh at near-floor levels (<= 1.1 x p_min) in
    steps priced above the day's median, the cheapest quarter's share of
@@ -125,9 +125,15 @@ def solve(cell, prices, relaxed: bool):
     p.min_electrical_power, p.max_electrical_power = CFG_MIN, CFG_MAX
     p.dhw_enabled, p.house_heat_loss_scale = dhw, loss
     opt = HeatPumpOptimizer(ThermalModel(p), OptimizationConfig(clamp_planned_levels=rounded))
-    kept = getattr(opt_mod, "_relaxed_starts", None)
-    if not relaxed and kept is not None:
-        opt_mod._relaxed_starts = lambda _opt, *args: args[-2]
+    # The control arm removes the relaxed descent: the multi-start returns its
+    # first start as it stands and the candidate stage commits that. Ported in
+    # R11-OUTSIDE-HONEST-STARTS-RUNS from ``_relaxed_starts`` as identity, the
+    # function that pull request deleted; a tree before it has no relaxed
+    # descent to remove, so run the harness of that tree there.
+    kept = opt_mod._multi_start_minimize
+    if not relaxed and rounded:
+        opt_mod._multi_start_minimize = lambda _objective, starts, _bounds, **_kw: NS(
+            x=np.asarray(starts[0], float), success=True)
     try:
         return opt.optimize(inputs=solve_inputs(
             initial_state=ThermalState(
@@ -139,8 +145,7 @@ def solve(cell, prices, relaxed: bool):
             prices=prices, outdoor_temps=np.full(96, 5.0), start_time=T0,
         ))
     finally:
-        if kept is not None:
-            opt_mod._relaxed_starts = kept
+        opt_mod._multi_start_minimize = kept
 
 
 def shape(result, prices) -> tuple[float, float]:
diff --git a/dev/audit/harnesses/r10_setpoint_power.py b/dev/audit/harnesses/r10_setpoint_power.py
index 0608e85848..013bd05ecd 100644
--- a/dev/audit/harnesses/r10_setpoint_power.py
+++ b/dev/audit/harnesses/r10_setpoint_power.py
@@ -8,9 +8,9 @@ whose levels ship rounded (``clamp_planned_levels``), p_min 1.5 kW, p_max
 5.5 kW: two-zone off/on x hot water off/on x heat-loss scale 0.6/1.0 x outdoor
 mean -4/+2 degC x starting tank 25/34 degC = 32 cells, one sinusoidal price
 day (1.3 +/- 0.9) and its flat mean. Each cell is solved twice per price
-vector on the tree it runs in: as shipped, and with
-``optimizer._relaxed_starts`` replaced by the identity (the control arm; on a
-tree without the function both arms are the tree). Printed per price vector:
+vector on the tree it runs in: as shipped, and with the relaxed descent
+removed (the control arm: ``optimizer._multi_start_minimize`` returning its
+first start, which the candidate stage then commits). Printed per price vector:
 how many cells the shipped solve scores lower / higher by the plan's own
 ``objective_value`` than the control arm, how many publish the identical plan,
 and the failure count. No private data: every input is written here.
@@ -19,6 +19,7 @@ from __future__ import annotations
 
 import itertools
 from datetime import datetime, timezone
+from types import SimpleNamespace
 
 import numpy as np
 
@@ -45,9 +46,15 @@ def solve(cell: tuple, prices: np.ndarray, relaxed: bool) -> tuple[np.ndarray, f
     params.house_heat_loss_scale = loss
     outdoor = out_mean + 3.0 * np.sin(2 * np.pi * (STEPS - 50) / 96.0)
     opt = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(clamp_planned_levels=True))
-    kept = getattr(opt_mod, "_relaxed_starts", None)
-    if not relaxed and kept is not None:
-        opt_mod._relaxed_starts = lambda _opt, *args: args[-2]
+    # The control arm removes the relaxed descent: the multi-start returns its
+    # first start as it stands and the candidate stage commits that. Ported in
+    # R11-OUTSIDE-HONEST-STARTS-RUNS from ``_relaxed_starts`` as identity, the
+    # function that pull request deleted; a tree before it has no relaxed
+    # descent to remove, so run the harness of that tree there.
+    kept = opt_mod._multi_start_minimize
+    if not relaxed:
+        opt_mod._multi_start_minimize = lambda _objective, starts, _bounds, **_kw: SimpleNamespace(
+            x=np.asarray(starts[0], float), success=True)
     try:
         result = opt.optimize(inputs=solve_inputs(
             initial_state=ThermalState(
@@ -60,8 +67,7 @@ def solve(cell: tuple, prices: np.ndarray, relaxed: bool) -> tuple[np.ndarray, f
             start_time=datetime(2026, 1, 10, tzinfo=timezone.utc),
         ))
     finally:
-        if kept is not None:
-            opt_mod._relaxed_starts = kept
+        opt_mod._multi_start_minimize = kept
     return np.asarray(result.power_schedule, float), float(result.objective_value)
 
 
diff --git a/dev/audit/harnesses/r11_honest_starts_runs.py b/dev/audit/harnesses/r11_honest_starts_runs.py
new file mode 100644
index 0000000000..9f868ce24e
--- /dev/null
+++ b/dev/audit/harnesses/r11_honest_starts_runs.py
@@ -0,0 +1,488 @@
+"""R11-OUTSIDE-HONEST-STARTS-RUNS: what the committed runs ship, measured on one tree.
+
+    PYTHONPATH=tests/hastub:custom_components:tests \\
+        python3 dev/audit/harnesses/r11_honest_starts_runs.py fixtures|c1|descents|grid|gradient|stress|kernels
+
+Synthetic throughout; no private data. The finding is outside pull request
+3529 (Bankaifan), which has no finder harness; this one reproduces the pull
+request body's figures.
+
+``fixtures``: the two golden plan scenarios that set a cycling cost
+(``cycling_cost``, ``everything_on``), captured by ``tests/golden.py`` on the
+tree this runs in. Printed per scenario: the space plan's steps between the
+plan's running rule (0.1 kW) and the 1.0 kW floor, the same for the combined
+draw (hot-water levels are the planner's), off-to-on edges of the combined
+draw, energy, ``predicted_cost`` and the lowest room temperature. Runs on a
+tree before the pull request too: it reads the published arrays only.
+
+``c1``: the same two lines with ``optimizer._engaged`` reduced to
+``clamp_planned_levels`` alone, ruling c1's other arm as one predicate and
+nothing else (the swing term stays deleted). Read against ``fixtures`` on
+this tree and on the merge base: the arm is a null only where its lines
+equal the merge base's. Exits 2 on a tree without ``_engaged``.
+
+``descents``: a solve that prices a duty switch descends twice, with the
+switch operand and as a solve that prices no stop would
+(``optimizer._relaxed_plans``). Three installs (duty-cycle, modulating
+clamped, fixed-speed) x four days, the contributor's pair (a certain stop
+from hot water to heating, 501 s off), cycling cost 0.3. Per cell and arm
+(both descents, the operand's alone, the unpriced one alone): the published
+objective and the shipped plan's switch weight at the combined draw. Null
+control: with an empty pair the arms have one descent each and print one
+plan; the harness exits 1 otherwise. On a tree without ``_relaxed_plans`` it
+prints that there is nothing to compare and exits 0.
+
+``grid``: a buffered single-zone house, space only, at cycling cost 0 / 0.25
+and clamped or not: steps under the floor, edges, energy and solve seconds
+(``time.process_time``) per cell. The unpriced duty-cycle cell is the null:
+it must never enter the candidate stage where the tree has one.
+
+``gradient``: what the batched finite-difference gradient simulates
+(``optimizer._batch_fd_gradient``, design note n6). Four goldens that fix
+part of the horizon (a committed mask, hot-water blocks) and one grid cell
+that fixes none, the null. Per solve: gradient calls, the share of their
+variables the bounds fix, the rows the batch objective was handed against
+the rows a batch of every variable holds, CPU seconds, and a sha1 over
+every gradient returned and over the shipped plan. Runs on a tree before
+the change too: there the two row counts are equal on every line, and the
+two digests are what the change must not move. Exits 1 when the null cell
+has a fixed variable or was handed fewer rows than the full batch.
+
+``stress``: what the second descent costs, by ``tests/stress.py``'s own
+measure (design verdict item r3). The sweep's scenarios that price a cycle
+(``sweep_combinations()``, ``cycling`` above zero; all hold hot water) are
+built by its ``build_case`` with a duty-switch pair on the config the case
+constructs, and each solve's CPU is divided by the trailing median of its
+reference solve, sampled beside it, as the sweep does. Arms: the
+contributor's pair as the tree solves it; the same with the second
+descent's guard reading no stop for the length of ``_relaxed_plans`` (one
+descent and one relaxed plan for the stage to commit; the solve's other
+readers of the stops run outside that call); and an
+empty pair in both forms, the null, which descends once either way. Per
+scenario and arm: the median ratio over ``STRESS_REPEATS`` solves (default
+3), descents per space solve, the calls of the multi-start, and the
+scenario's own recorded budget from ``tests/stress_budgets.json``. The last
+lines print the second descent's cost per scenario and the null's two forms
+against each other, the noise this box puts on such a difference. Runs on a
+tree without ``_relaxed_plans`` too: there each pair has the one arm. Exits
+1 when a null solve descends twice, the null's two forms ship different
+plans, or the pair's solve never descends twice on a tree that can.
+
+``kernels``: the acceptance checks of the two ``tests/features.py`` blocks
+that solve this group's fixtures, once per OpenBLAS kernel (``tests/README.md``,
+"A knife-edge optimizer comparison must be measured across BLAS kernels").
+Per kernel (``OPENBLAS_CORETYPE``; SkylakeX, Haswell, Sandybridge and Nehalem,
+or those named after the mode) both blocks run through
+``tools/audit/seat/features_block.py`` in the checkout this is run from, one thread,
+and each check whose name starts ``acceptance`` is printed with its verdict
+and its detail string. Beside them, on the same solves, the two clauses the
+round-4 repair replaced: the order of the two switch weights in starts on
+the modulating clamped install, and the shipped energy within one floor step
+of the relaxed plan's, with the figures each reads, and the two start counts
+of the kept clause. The replaced clauses are
+the null control of the restated ones: they read False under the kernels the
+restated checks read True on. Runs on a tree before the restatement too,
+where the checks printed are the replaced clauses themselves. Exits 1 when
+a block fails a check or does not complete under any kernel, so the mode
+with one kernel named is a command ``tools/audit/seat/mutant_run.py`` can
+drive; a kernel this processor cannot run is printed as such and counted as
+not completed.
+"""
+from __future__ import annotations
+
+import hashlib
+import os
+import subprocess
+import sys
+import time
+from concurrent.futures import ThreadPoolExecutor
+from datetime import datetime, timezone
+
+import numpy as np
+
+import heatpump_optimizer.optimizer as om
+from heatpump_optimizer import duty_legs
+from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
+from profiles import solve_inputs
+
+STEPS = np.arange(96)
+T0 = datetime(2026, 1, 10, tzinfo=timezone.utc)
+RUNS_AT = 0.1
+PAIR, OFF = (1.0, 0.0), (501.0, 0.0)
+INSTALLS = (("duty-cycle", False, 1.5), ("modulating clamped", True, 1.5), ("fixed-speed", True, 5.5))
+DAYS = ((30, 2.0), (60, 2.0), (30, -4.0), (0, 6.0))
+
+
+def edges(total) -> int:
+    on = np.asarray(total, float) > RUNS_AT
+    return int(np.sum(on & ~np.r_[False, on[:-1]]))
+
+
+def under(plan, floor: float) -> int:
+    plan = np.asarray(plan, float)
+    return int(np.sum((plan > RUNS_AT) & (plan < floor - 1e-9)))
+
+
+def fixtures() -> int:
+    import golden
+
+    for name in ("cycling_cost", "everything_on"):
+        got = golden.capture(name, golden.SCENARIOS[name])
+        space = np.asarray(got["power_schedule"], float)
+        dhw = np.asarray(got.get("dhw_power_schedule") or np.zeros_like(space), float)
+        rooms = np.asarray(got["room_temp_trajectory"], float)
+        print(f"{name}: space steps under 1.0 kW {under(space, 1.0)}, combined {under(space + dhw, 1.0)},"
+              f" edges {edges(space + dhw)}, published starts {got['compressor_starts']},"
+              f" energy_kwh {float(np.sum(space + dhw)) * 0.25:.2f},"
+              f" predicted_cost {got['predicted_cost']:.2f}, lowest_room {float(rooms.min()):.2f}")
+    return 0
+
+
+def c1() -> int:
+    if not hasattr(om, "_engaged"):
+        print("this tree has no optimizer._engaged: nothing to reduce")
+        return 2
+    kept = om._engaged
+    om._engaged = lambda opt: opt.config.clamp_planned_levels
+    try:
+        return fixtures()
+    finally:
+        om._engaged = kept
+
+
+def _switch_solve(clamp: bool, p_min: float, pair, arm: str, phase: int, out_mean: float):
+    params = ThermalParameters()
+    params.mixing_valve_mode, params.buffer_tank_volume = "none", 750.0
+    params.min_electrical_power, params.max_electrical_power = p_min, 5.5
+    params.dhw_enabled = True
+    cfg = om.OptimizationConfig(clamp_planned_levels=clamp, cycling_cost=0.3)
+    cfg.duty_switch_stop_probability, cfg.duty_switch_off_seconds = pair, OFF
+    opt = om.HeatPumpOptimizer(ThermalModel(params), cfg)
+    kept, counts = om._relaxed_plans, []
+
+    def plans(*args):
+        res, relaxed = kept(*args)
+        counts.append(len(relaxed))
+        return res, {"operand": relaxed[:1], "unpriced": relaxed[-1:]}.get(arm, relaxed)
+
+    om._relaxed_plans = plans
+    outdoor = out_mean + 3.0 * np.sin(2 * np.pi * (STEPS - 50) / 96.0)
+    try:
+        result = opt.optimize(inputs=solve_inputs(
+            initial_state=ThermalState(
+                room_temperature=20.5, upper_floor_temperature=20.5,
+                lower_floor_temperature=20.5, slab_temperature=21.0,
+                outdoor_temperature=float(outdoor[0]), buffer_tank_temperature=30.0,
+                dhw_temperature=45.0, dhw_hours_since_legionella=20.0,
+            ),
+            prices=1.3 + 0.9 * np.sin(2 * np.pi * (STEPS - phase) / 96.0),
+            outdoor_temps=outdoor, start_time=T0,
+        ))
+    finally:
+        om._relaxed_plans = kept
+    space = np.asarray(result.power_schedule, float)
+    dhw = np.asarray(result.dhw_power_schedule, float)
+    weight = duty_legs.switch_weight(space, dhw, PAIR, 5.5, p_min if clamp else None, om._leg_rule(opt))
+    return float(result.objective_value), float(weight), set(counts), space, dhw
+
+
+def descents() -> int:
+    if not hasattr(om, "_relaxed_plans"):
+        print("this tree has one descent per space solve: nothing to compare")
+        return 0
+    null_bad = 0
+    for name, clamp, p_min in INSTALLS:
+        for phase, out_mean in DAYS:
+            row = {arm: _switch_solve(clamp, p_min, PAIR, arm, phase, out_mean)
+                   for arm in ("both", "operand", "unpriced")}
+            print(f"{name} price phase {phase} outdoor {out_mean}: " + ", ".join(
+                f"{arm} objective {got[0]:.4f} switch_weight {got[1]:.4f}" for arm, got in row.items()))
+        nulls = [_switch_solve(clamp, p_min, (0.0, 0.0), arm, 30, 2.0) for arm in ("both", "operand", "unpriced")]
+        same = all(np.array_equal(nulls[0][3], n[3]) and np.array_equal(nulls[0][4], n[4]) for n in nulls)
+        descended = set().union(*(n[2] for n in nulls))
+        print(f"{name} null (empty pair): one plan across the arms {same}, descents per space solve {sorted(descended)}")
+        null_bad += (not same) or descended != {1}
+    print(f"null cells that moved or descended twice {null_bad}")
+    return 1 if null_bad else 0
+
+
+def grid() -> int:
+    prices = 1.3 + 0.9 * np.sin(2 * np.pi * (STEPS - 30) / 96.0)
+    staged, bad = [], 0
+    kept = getattr(om, "_run_plans", None)
+    if kept is not None:
+        om._run_plans = lambda *args: (staged.append(1), kept(*args))[1]
+    try:
+        for cost, clamp, p_min, loss, out_mean in (
+            (0.0, False, 1.1, 0.4, 8.0), (0.25, False, 1.1, 0.4, 8.0), (0.25, False, 0.53, 0.4, 8.0),
+            (0.0, True, 1.1, 0.4, 8.0), (0.25, True, 1.1, 0.4, 8.0), (0.25, False, 1.1, 1.0, 2.0),
+        ):
+            params = ThermalParameters()
+            params.mixing_valve_mode, params.buffer_tank_volume = "none", 750.0
+            params.min_electrical_power, params.max_electrical_power = p_min, 5.5
+            params.dhw_enabled, params.house_heat_loss_scale = False, loss
+            opt = om.HeatPumpOptimizer(
+                ThermalModel(params), om.OptimizationConfig(clamp_planned_levels=clamp, cycling_cost=cost))
+            outdoor = out_mean + 3.0 * np.sin(2 * np.pi * (STEPS - 50) / 96.0)
+            staged.clear()
+            t = time.process_time()
+            result = opt.optimize(inputs=solve_inputs(
+                initial_state=ThermalState(
+                    room_temperature=20.5, upper_floor_temperature=20.5,
+                    lower_floor_temperature=20.5, slab_temperature=21.0,
+                    outdoor_temperature=float(outdoor[0]), buffer_tank_temperature=30.0,
+                    dhw_temperature=50.0,
+                ),
+                prices=prices, outdoor_temps=outdoor, start_time=T0,
+            ))
+            seconds = time.process_time() - t
+            plan = np.asarray(result.power_schedule, float)
+            print(f"cost {cost} clamp {clamp} p_min {p_min} loss {loss}: steps under the floor"
+                  f" {under(plan, max(p_min, RUNS_AT))}, edges {edges(plan)},"
+                  f" energy_kwh {float(plan.sum()) * 0.25:.2f}, objective {float(result.objective_value):.4f},"
+                  f" stage entered {bool(staged)}, solve_s {seconds:.2f}")
+            bad += bool(staged) and not (cost > 0 or clamp)
+    finally:
+        if kept is not None:
+            om._run_plans = kept
+    print(f"null (unpriced duty-cycle) cells that entered the stage {bad}")
+    return 1 if bad else 0
+
+
+def _metered(solve):
+    """Run ``solve`` with the batched gradient metered; its plan and the meter."""
+    kept = om._batch_fd_gradient
+    seen = {"calls": 0, "variables": 0, "fixed": 0, "rows": 0, "full": 0}
+    digest = hashlib.sha1()
+
+    def metered(batch_objective, args, x0, f0, eps, bounds):
+        def counted(rows, *a):
+            seen["rows"] += int(np.asarray(rows).shape[0])
+            return batch_objective(rows, *a)
+
+        grad = kept(counted, args, x0, f0, eps, bounds)
+        seen["calls"] += 1
+        seen["variables"] += len(bounds)
+        seen["fixed"] += sum(1 for lo, hi in bounds if not lo < hi)
+        seen["full"] += len(bounds) + (1 if f0 is None else 0)
+        digest.update(np.asarray(grad, float).tobytes())
+        return grad
+
+    om._batch_fd_gradient = metered
+    t = time.process_time()
+    try:
+        plan = solve()
+    finally:
+        om._batch_fd_gradient = kept
+    seen["seconds"] = time.process_time() - t
+    seen["gradients"] = digest.hexdigest()[:12]
+    seen["plan"] = hashlib.sha1(np.asarray(plan, float).tobytes()).hexdigest()[:12]
+    return seen
+
+
+def _null_cell():
+    params = ThermalParameters()
+    params.mixing_valve_mode, params.buffer_tank_volume = "none", 750.0
+    params.min_electrical_power, params.max_electrical_power = 1.1, 5.5
+    params.dhw_enabled, params.house_heat_loss_scale = False, 0.4
+    opt = om.HeatPumpOptimizer(ThermalModel(params), om.OptimizationConfig())
+    outdoor = 8.0 + 3.0 * np.sin(2 * np.pi * (STEPS - 50) / 96.0)
+    result = opt.optimize(inputs=solve_inputs(
+        initial_state=ThermalState(
+            room_temperature=20.5, upper_floor_temperature=20.5,
+            lower_floor_temperature=20.5, slab_temperature=21.0,
+            outdoor_temperature=float(outdoor[0]), buffer_tank_temperature=30.0,
+            dhw_temperature=50.0,
+        ),
+        prices=1.3 + 0.9 * np.sin(2 * np.pi * (STEPS - 30) / 96.0),
+        outdoor_temps=outdoor, start_time=T0,
+    ))
+    return result.power_schedule
+
+
+def gradient() -> int:
+    import golden
+
+    def fixture(name):
+        got = golden.capture(name, golden.SCENARIOS[name])
+        return np.r_[got["power_schedule"], got.get("dhw_power_schedule") or []]
+
+    cells = [(name, lambda name=name: fixture(name))
+             for name in ("cycling_cost", "everything_on", "winter_two_zone_dhw", "valve_storage")]
+    cells.append(("null: unpriced duty-cycle, space only", _null_cell))
+    bad = 0
+    for name, solve in cells:
+        got = _metered(solve)
+        print(f"{name}: gradients {got['calls']}, variables fixed {got['fixed']} of {got['variables']},"
+              f" rows simulated {got['rows']} of {got['full']} in a full batch,"
+              f" cpu_s {got['seconds']:.2f}, gradients sha1 {got['gradients']}, plan sha1 {got['plan']}")
+        if name.startswith("null"):
+            bad += got["fixed"] != 0 or got["rows"] != got["full"]
+    print(f"null cell with a fixed variable or a short batch {bad}")
+    return 1 if bad else 0
+
+
+def _stress_case(stress, spec: dict, pair, first_alone: bool) -> dict:
+    """One build of a sweep scenario with ``pair`` on its config: the solve's
+    CPU ms, descents per space solve, multi-start calls and the plan."""
+    kept_cfg, kept_min = stress.OptimizationConfig, om._multi_start_minimize
+    kept_plans, kept_stops = getattr(om, "_relaxed_plans", None), om._priced_stops
+    seen = {"descents": [], "multi_starts": 0}
+
+    def config(**kw):
+        cfg = kept_cfg(**kw)
+        cfg.duty_switch_stop_probability, cfg.duty_switch_off_seconds = pair, OFF
+        return cfg
+
+    def counted(*args, **kw):
+        seen["multi_starts"] += 1
+        return kept_min(*args, **kw)
+
+    def plans(*args):
+        if first_alone:
+            om._priced_stops = lambda opt: None
+        try:
+            out = kept_plans(*args)
+        finally:
+            om._priced_stops = kept_stops
+        seen["descents"].append(len(out[1]))
+        return out
+
+    stress.OptimizationConfig, om._multi_start_minimize = config, counted
+    if kept_plans is not None:
+        om._relaxed_plans = plans
+    try:
+        run = stress.build_case(**{k: v for k, v in spec.items() if k != "label"})
+    finally:
+        stress.OptimizationConfig, om._multi_start_minimize = kept_cfg, kept_min
+        if kept_plans is not None:
+            om._relaxed_plans = kept_plans
+    result = run["result"]
+    seen["cpu_ms"] = float(run["solve_cpu_ms"])
+    seen["plan"] = np.r_[result.power_schedule, result.dhw_power_schedule]
+    return seen
+
+
+def stress_cost() -> int:
+    import stress
+
+    repeats = int(os.environ.get("STRESS_REPEATS", "3"))
+    table = stress.load_budget_table()
+    specs = [spec for spec in stress.sweep_combinations() if spec.get("cycling")]
+    two = hasattr(om, "_relaxed_plans")
+    arms = [("pair", PAIR, False), ("null", (0.0, 0.0), False)]
+    if two:
+        arms[1:1] = [("pair, first descent alone", PAIR, True)]
+        arms.append(("null, guard off", (0.0, 0.0), True))
+    cal = stress.Calibration(stress.CALIBRATION_WINDOW)
+    cal.warm_up()
+    bad, cost, noise = 0, [], []
+    for spec in specs:
+        row = {}
+        for name, pair, first_alone in arms:
+            ratios = []
+            for _ in range(repeats):
+                cal.sample()
+                got = _stress_case(stress, spec, pair, first_alone)
+                ratios.append(got["cpu_ms"] / max(cal.unit_ms, 1e-6))
+            row[name] = (float(np.median(ratios)), sorted(set(got["descents"])), got["multi_starts"], got["plan"])
+        budget = stress.scenario_budget(spec["label"], table)
+        print(f"{spec['label']} (recorded budget {budget:.1f}x): " + "; ".join(
+            f"{name} {ratio:.1f}x, descents {descents or 'one per solve, no stage to count'},"
+            f" multi-starts {calls}" for name, (ratio, descents, calls, _plan) in row.items()))
+        if two:
+            cost.append(row["pair"][0] - row["pair, first descent alone"][0])
+            noise.append(row["null"][0] - row["null, guard off"][0])
+            bad += row["null"][1] != [1] or row["null, guard off"][1] != [1]
+            bad += not np.array_equal(row["null"][3], row["null, guard off"][3])
+            bad += 2 not in row["pair"][1] or row["pair, first descent alone"][1] != [1]
+    lo, mid, hi = cal.spread()
+    print(f"reference solve {mid:.1f} ms of CPU (min {lo:.1f}, max {hi:.1f}) over {cal.count} samples;"
+          f" {repeats} solve(s) per arm, the median ratio printed")
+    if two:
+        print("second descent, pair less its first descent alone, x reference per scenario: "
+              + ", ".join(f"{c:+.1f}" for c in cost) + f"; median {float(np.median(cost)):+.1f}")
+        print("null, as the tree less guard off (one descent in both), x reference per scenario: "
+              + ", ".join(f"{c:+.1f}" for c in noise) + f"; median {float(np.median(noise)):+.1f}")
+    else:
+        print("this tree has one descent per space solve: no second descent to cost")
+    print(f"scenarios whose null descended twice or moved, or whose pair never descended twice {bad}")
+    return 1 if bad else 0
+
+
+KERNELS = ("SkylakeX", "Haswell", "Sandybridge", "Nehalem")
+_BLOCK = 'R.section("R11-OUTSIDE-HONEST-STARTS-RUNS: the start count and committed runs")'
+# The block that follows this group's in tests/features.py; the block runs up to it.
+_NEXT = "# --- R10-START-COUNTER-EDGES: the start counter fed from running-signal edges ---"
+_BLOCKS = (
+    ("duty-switch block", ("from types import SimpleNamespace as _DspNS", _BLOCK)),
+    ("starts-and-runs block", (_BLOCK, _NEXT)),
+)
+# Run as a prelude inside the features namespace: wraps ``R.check``.
+_KERNEL_PROBE = r'''
+import sys as _kp_sys
+_kp_check = R.check
+def _kp_probe(name, cond, detail="", _real=_kp_check):
+    g = _kp_sys._getframe(1).f_globals
+    if name.startswith("acceptance"):
+        print("ACCEPT", bool(cond), "|", name, "|", detail, flush=True)
+    if name.startswith("acceptance: priced on the contributor's table"):
+        old_w, new_w = g["_dsp_accept_starts"]["modulating clamped"]
+        print("REPLACED", bool(new_w <= old_w + 1e-9), "| modulating clamped, switch weight in starts,"
+              " priced no higher than unpriced |", f"unpriced {old_w:g}, priced {new_w:g}", flush=True)
+    if name.startswith("acceptance: a priced plan holds no more starts"):
+        cells = {k: v for k, v in g["_hsr_engaged"].items() if k[0] > 0 and not k[1]}
+        kwh = {k: float(g["np"].sum(v.space - v.relaxed[-1])) * 0.25 for k, v in cells.items()}
+        step = {k: g["_hsr_runs"].floor_kw(k[2]) * 0.25 for k in cells}
+        count, free = g["_hsr_count"], {k: g["_hsr_solve"](0.0, False, k[2]).space for k in cells}
+        print("KEPT", all(count(v.space, k[2]) <= count(free[k], k[2]) + 1e-9 for k, v in cells.items()),
+              "| priced starts no higher than the unpriced plan's by the same count |",
+              "; ".join(f"floor {k[2]} kW: {count(v.space, k[2]):g} against {count(free[k], k[2]):.2f}"
+                        for k, v in cells.items()), flush=True)
+        print("REPLACED", all(abs(kwh[k]) <= step[k] + 1e-9 for k in cells),
+              "| shipped energy within one floor step of the relaxed plan's |",
+              "; ".join(f"floor {k[2]} kW: {kwh[k]:+.4f} kWh against a step of {step[k]:.4f}" for k in cells),
+              flush=True)
+    return _real(name, cond, detail)
+R.check = _kp_probe
+'''
+
+
+def _kernel_blocks(kernel: str) -> list[tuple[str, int, list[str]]]:
+    env = dict(os.environ, PYTHONPATH="tests/hastub", OPENBLAS_CORETYPE=kernel, R11_HSR_KERNEL_PROBE=_KERNEL_PROBE,
+               OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
+    out = []
+    with open("tests/features.py", encoding="utf-8") as fh:
+        present = fh.read()
+    for label, markers in _BLOCKS:
+        markers = tuple(m for m in markers if m in present)  # a tree before the next block holds no _NEXT
+        run = subprocess.run(
+            [sys.executable, "tools/audit/seat/features_block.py",
+             "--prelude", 'import os as _kp_os; exec(_kp_os.environ["R11_HSR_KERNEL_PROBE"])', *markers],
+            env=env, capture_output=True, text=True)
+        lines = (run.stdout + run.stderr).splitlines()
+        out.append((label, run.returncode, [
+            ln for ln in lines if ln.startswith(("ACCEPT ", "KEPT ", "REPLACED ")) or "FEATURES BLOCK" in ln]))
+    return out
+
+
+def kernels() -> int:
+    names = tuple(sys.argv[2:]) or KERNELS
+    with ThreadPoolExecutor(max(1, min(len(names), os.cpu_count() or 1))) as pool:
+        results = list(pool.map(_kernel_blocks, names))
+    bad = 0
+    for kernel, blocks in zip(names, results):
+        for label, rc, lines in blocks:
+            done = any("FEATURES BLOCK" in ln for ln in lines)
+            print(f"{kernel}, {label}: " + (
+                f"exit {rc}" if done else f"did not complete (exit {rc}): not runnable on this processor, or the block raised"))
+            for ln in lines:
+                print("  " + ln)
+            bad += not done or rc != 0
+    print(f"kernels {', '.join(names)}: blocks that failed a check or did not complete {bad}")
+    return 1 if bad else 0
+
+
+if __name__ == "__main__":
+    sys.exit({"fixtures": fixtures, "c1": c1, "descents": descents, "grid": grid, "gradient": gradient,
+              "stress": stress_cost, "kernels": kernels}[sys.argv[1]]())
diff --git a/dev/audit/harnesses/r11_honest_starts_runs_mutants.json b/dev/audit/harnesses/r11_honest_starts_runs_mutants.json
new file mode 100644
index 0000000000..5df857c96a
--- /dev/null
+++ b/dev/audit/harnesses/r11_honest_starts_runs_mutants.json
@@ -0,0 +1,290 @@
+[
+ {
+  "name": "R_MINUS_1",
+  "file": "custom_components/heatpump_optimizer/runs.py",
+  "old": "    through[:, 0] = 1.0 if running else 0.0\n",
+  "new": "    through[:, 0] = 0.0\n"
+ },
+ {
+  "name": "ONE_MINUS_R",
+  "file": "custom_components/heatpump_optimizer/runs.py",
+  "old": "    count: np.ndarray = row_sums(needs * (1.0 - through))\n",
+  "new": "    count: np.ndarray = row_sums(needs)\n"
+ },
+ {
+  "name": "A_AGAINST_FLOOR",
+  "file": "custom_components/heatpump_optimizer/runs.py",
+  "old": "    needs = np.clip(rows / MIN_RUNNING_DRAW_KW, 0.0, 1.0)\n",
+  "new": "    needs = np.clip(rows / floor_kw(floor), 0.0, 1.0)\n"
+ },
+ {
+  "name": "FLOOR_ZERO_GUARD",
+  "file": "custom_components/heatpump_optimizer/runs.py",
+  "old": "    return max(float(floor), MIN_RUNNING_DRAW_KW)\n",
+  "new": "    return max(float(floor), 1e-12)\n"
+ },
+ {
+  "name": "EDGE_RUNNING",
+  "file": "custom_components/heatpump_optimizer/runs.py",
+  "old": "    return int(np.sum(on & ~np.r_[bool(running), on[:-1]]))\n",
+  "new": "    return int(np.sum(on & ~np.r_[False, on[:-1]]))\n"
+ },
+ {
+  "name": "LEVEL_DEFAULT",
+  "file": "custom_components/heatpump_optimizer/duty_legs.py",
+  "old": "    if level is None:\n        level = space + np.asarray(dhw_kw, dtype=float)\n",
+  "new": "    if True:\n        level = space + np.asarray(dhw_kw, dtype=float)\n"
+ },
+ {
+  "name": "MIN_R_BEFORE_AFTER",
+  "file": "custom_components/heatpump_optimizer/duty_legs.py",
+  "old": "    across = stops * np.minimum(level[_BEFORE], level[_AFTER])\n",
+  "new": "    across = stops * level[_BEFORE]\n"
+ },
+ {
+  "name": "RELAXED_SWITCH_OPERAND",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "        if stops is None or dhw is None or not cost > 0 or descent == _UNPRICED:\n",
+  "new": "        if stops is None or dhw is None or not cost > 0 or descent:\n"
+ },
+ {
+  "name": "TRUE_SWITCH_LEVEL",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "            level=None if descent else p_max * runs.running_share(rows + dhw, p_min))\n",
+  "new": "            level=None)\n"
+ },
+ {
+  "name": "START_TERM_IN_DESCENT",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "        if descent or not cost > 0:\n            return None\n        count =",
+  "new": "        if not cost > 0:\n            return None\n        count ="
+ },
+ {
+  "name": "ENGAGED_COST_ARM",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "    return opt.config.cycling_cost > 0 or opt.config.clamp_planned_levels\n",
+  "new": "    return opt.config.clamp_planned_levels\n"
+ },
+ {
+  "name": "ENGAGED_CLAMP_ARM",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "    return opt.config.cycling_cost > 0 or opt.config.clamp_planned_levels\n",
+  "new": "    return opt.config.cycling_cost > 0\n"
+ },
+ {
+  "name": "CANDIDATE_1_LEFT_OUT",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "    plans = [first, *_run_plans(opt, h, space, other, lo, hi, cycled)]\n",
+  "new": "    plans = [*_run_plans(opt, h, space, other, lo, hi, cycled)]\n"
+ },
+ {
+  "name": "LOWEST_SCORE_CHOICE",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "    return min((float(scores[order[0]]), *scoped[order[0]]), resolved, key=lambda c: c[0])\n",
+  "new": "    return max((float(scores[order[0]]), *scoped[order[0]]), resolved, key=lambda c: c[0])\n"
+ },
+ {
+  "name": "LOWEST_RELAXED_PLAN",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "            for space in relaxed\n        ), key=lambda c: c[0])[1:]\n",
+  "new": "            for space in relaxed[:1]\n        ), key=lambda c: c[0])[1:]\n"
+ },
+ {
+  "name": "MASK_TO_BOUNDS",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "        list(zip(lo.tolist(), hi.tolist())), np.where(on, 1.0, np.where(off, 0.0, np.nan)), floor)\n",
+  "new": "        list(zip(lo.tolist(), hi.tolist())), None, floor)\n"
+ },
+ {
+  "name": "HELD_AS_IT_STANDS",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "    return [b if on[i] or off[i] else (float(plan[i]), float(plan[i])) for i, b in enumerate(pinned)]\n",
+  "new": "    return pinned\n"
+ },
+ {
+  "name": "FALLBACK",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "        _LOGGER.debug(\"Committing runs failed, the projection ships: %s\", err)\n        return first, scope\n",
+  "new": "        _LOGGER.debug(\"Committing runs failed, the projection ships: %s\", err)\n        return relaxed[0], scope\n"
+ },
+ {
+  "name": "IDENTITY_GUARD",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "    if not opt.config.cycling_cost > 0 and np.array_equal(first, relaxed[0]):\n        return relaxed[0], scope\n",
+  "new": "    if np.array_equal(first, relaxed[0]):\n        return relaxed[0], scope\n"
+ },
+ {
+  "name": "UNPRICED_DESCENT",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "    if opt.config.cycling_cost > 0 and _priced_stops(opt) is not None:\n        free_room, free = rescope(None)\n",
+  "new": "    if False:\n        free_room, free = rescope(None)\n"
+ },
+ {
+  "name": "RESCOPE_OFF",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "                (lambda start: rescope(start)[1]) if _priced_stops(self) else None,\n",
+  "new": "                None,\n"
+ },
+ {
+  "name": "CYCLED_KEPT",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "    idle = np.where(cycled, space, lo)\n",
+  "new": "    idle = lo\n"
+ },
+ {
+  "name": "FORCED_PINS",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "        forced=np.where((other > 0.0) | (lo > 0.0), 1.0, np.where(hi + other <= 0.0, 0.0, np.nan)),\n",
+  "new": "        forced=None,\n"
+ },
+ {
+  "name": "RELAXED_AS_CANDIDATE",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "    if runs.realizable(np.where(cycled, 0.0, space), floor):\n        plans.append(space)\n",
+  "new": "    if False:\n        plans.append(space)\n"
+ },
+ {
+  "name": "OUT_OF_BAND_PENALTY",
+  "file": "custom_components/heatpump_optimizer/runs.py",
+  "old": "        c = np.concatenate([cost[s] + paid + start_cost * starts for s, starts in srcs]) + fine * outside\n",
+  "new": "        c = np.concatenate([cost[s] + paid + start_cost * starts for s, starts in srcs])\n"
+ },
+ {
+  "name": "END_BALANCE_HALF_STEP",
+  "file": "custom_components/heatpump_optimizer/runs.py",
+  "old": "    ending = cost + fine * np.maximum(np.abs(bal) - f * dt / 2.0, 0.0)\n",
+  "new": "    ending = cost + fine * np.maximum(np.abs(bal) - f * dt * 8.0, 0.0)\n"
+ },
+ {
+  "name": "TRACKED_HALF_STEP",
+  "file": "custom_components/heatpump_optimizer/runs.py",
+  "old": "        np.all(np.abs(walk) <= half * quantum + _SLACK) and abs(walk[-1]) <= f * dt / 2.0 + _SLACK)\n",
+  "new": "        np.all(np.abs(walk) <= half * quantum + _SLACK))\n"
+ },
+ {
+  "name": "START_COST_EDGE",
+  "file": "custom_components/heatpump_optimizer/runs.py",
+  "old": "        c = np.concatenate([cost[s] + paid + start_cost * starts for s, starts in srcs]) + fine * outside\n",
+  "new": "        c = np.concatenate([cost[s] + paid for s, starts in srcs]) + fine * outside\n"
+ },
+ {
+  "name": "RUN_PAUSE_COUNTS",
+  "file": "custom_components/heatpump_optimizer/runs.py",
+  "old": "    lengths = (steps_at_least(MIN_RUN, dt), steps_at_least(MIN_PAUSE, dt))\n",
+  "new": "    lengths = (1, 1)\n"
+ },
+ {
+  "name": "CAP_UNDER_FLOOR_OFF",
+  "file": "custom_components/heatpump_optimizer/runs.py",
+  "old": "    want = np.where(np.isnan(want) & (cap < f - _SLACK), 0.0, want)\n",
+  "new": "    want = want\n"
+ },
+ {
+  "name": "COORD_ARGUMENT",
+  "file": "custom_components/heatpump_optimizer/coordinator.py",
+  "old": "            compressor_running=duty_switch.running_now(duty_switch.record_for(self), self._current_action),\n",
+  "new": ""
+ },
+ {
+  "name": "WHATIF_ARGUMENT",
+  "file": "custom_components/heatpump_optimizer/coordinator.py",
+  "old": "            compressor_running=duty_switch.record_for(self).solved_running,\n",
+  "new": ""
+ },
+ {
+  "name": "HORIZON_RUNNING",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "                compressor_running=inputs.compressor_running,\n",
+  "new": ""
+ },
+ {
+  "name": "PUBLISHED_RUNNING",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "            \"starts\": runs.edge_count(total_power, running),",
+  "new": "            \"starts\": runs.edge_count(total_power),"
+ },
+ {
+  "name": "SETTLED_CLASS",
+  "file": "custom_components/heatpump_optimizer/duty_switch.py",
+  "old": "    running = running_signal.running_now(rec.signal)\n",
+  "new": "    running = None\n"
+ },
+ {
+  "name": "LATCH_READING",
+  "file": "custom_components/heatpump_optimizer/duty_switch.py",
+  "old": "    rec.solved_running = running\n",
+  "new": "    pass\n"
+ },
+ {
+  "name": "UNPRICED_DESCENT_COST_ARM",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "    if opt.config.cycling_cost > 0 and _priced_stops(opt) is not None:\n        free_room, free = rescope(None)\n",
+  "new": "    if _priced_stops(opt) is not None:\n        free_room, free = rescope(None)\n"
+ },
+ {
+  "name": "CANDIDATE_OWN_BOUND",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "        scoped = [(np.clip(x, *_stage_box(opt, sc[0], dhw)[:2]), sc) for x, sc in zip(plans, scopes)]\n",
+  "new": "        scoped = [(x, sc) for x, sc in zip(plans, scopes)]\n"
+ },
+ {
+  "name": "ADOPTED_VECTOR",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "            self._space_avail = shipped[3]\n",
+  "new": "            pass\n"
+ },
+ {
+  "name": "N6_ROW_PER_VARIABLE",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "    stepped = np.flatnonzero(free)\n",
+  "new": "    stepped = np.arange(x0.size)\n"
+ },
+ {
+  "name": "N6_EMPTY_BATCH_SIMULATED",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "    if lead == 0 and not free.any():\n",
+  "new": "    if False:\n"
+ },
+ {
+  "name": "N6_FIXED_ENTRY_WRITTEN",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "    grad[free] = (f - f0) / dx[free]\n",
+  "new": "    grad[:] = np.resize((f - f0) / dx[free], x0.size)\n"
+ },
+ {
+  "name": "N6_EMPTY_GUARD_OR",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "    if lead == 0 and not free.any():\n",
+  "new": "    if lead == 0 or not free.any():\n"
+ },
+ {
+  "name": "TIE_BREAK_ZERO",
+  "file": "custom_components/heatpump_optimizer/runs.py",
+  "old": "_TIE_BREAK = 1e-9\n",
+  "new": "_TIE_BREAK = 0.0\n"
+ },
+ {
+  "name": "COMMIT_INITIAL_STATE",
+  "file": "custom_components/heatpump_optimizer/runs.py",
+  "old": "    cost[min_on - 1 if running else sum(lengths) - 1, half] = 0.0\n",
+  "new": "    cost[sum(lengths) - 1, half] = 0.0\n"
+ },
+ {
+  "name": "COMMIT_RUNNING",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "        dt=h.dt, running=h.compressor_running,\n",
+  "new": "        dt=h.dt, running=False,\n"
+ },
+ {
+  "name": "OUT_OF_BAND_CLAMP",
+  "file": "custom_components/heatpump_optimizer/runs.py",
+  "old": "        outside = np.maximum(np.abs(b) - half * quantum, 0.0)\n",
+  "new": "        outside = np.maximum(np.abs(b) - half * quantum, 1.0)\n"
+ },
+ {
+  "name": "SPACE_SCOPE_LOWER_BOUND",
+  "file": "custom_components/heatpump_optimizer/optimizer.py",
+  "old": "        [(0.0, float(v)) for v in headroom], h.space_pins, opt._pin_on_power(p_max))\n",
+  "new": "        [(1.0, float(v)) for v in headroom], h.space_pins, opt._pin_on_power(p_max))\n"
+ }
+]
\ No newline at end of file
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index eb5c2feced..d45b059141 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -283,7 +283,7 @@
   "source": "docs/architecture.md",
   "claim": "45 modules",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=94 measured=94",
+  "result": "documented=95 measured=95",
   "verdict": "true",
   "truth": ""
  },
@@ -292,7 +292,7 @@
   "source": "docs/architecture.md",
   "claim": "the module map is the package's module list",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "on disk=94, listed=94, missing=[], phantom=[]",
+  "result": "on disk=95, listed=95, missing=[], phantom=[]",
   "verdict": "true",
   "truth": "0 modules are absent from the map: "
  },
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index 2637058615..ef52edf482 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -35,8 +35,8 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C29 | `docs/architecture.md:module map` | config_flow.py -- Setup flow plus 24 option pages behind two menus | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=24 measured=24 | **true** |  |
 | C30 | `docs/configuration.md` | every documented Default (97 rows) is the default the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 97 compared, mismatches=[] | **true** |  |
 | C31 | `docs/configuration.md` | every documented Range (104 rows) is the NumberSelector min/max the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 104 compared, mismatches=[] | **true** |  |
-| C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=94 measured=94 | **true** |  |
-| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=94, listed=94, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
+| C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=95 measured=95 | **true** |  |
+| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=95, listed=95, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
 | C34 | `docs/architecture.md:The Home Assistant boundary` | the boundary sentence's count of modules importing `homeassistant` at module level | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=33 measured=33 | **true** |  |
 | C35 | `docs/architecture.md:The Home Assistant boundary` | the named modules are the complete set of module-level importers | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | named=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], measured=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], unnamed=[] | **true** | unnamed module-level importers:  |
 | C36 | `docs/architecture.md:The Home Assistant boundary` | everything outside the named set is free of homeassistant, so each module can be driven with no Home Assistant running | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 0 modules outside the named set import homeassistant at module level | **true** | modules outside the named set import homeassistant at module level and cannot be imported without it:  |
diff --git a/dev/audit/rounds/round4/D6/claims.py b/dev/audit/rounds/round4/D6/claims.py
index 090b5d503b..96126d028f 100644
--- a/dev/audit/rounds/round4/D6/claims.py
+++ b/dev/audit/rounds/round4/D6/claims.py
@@ -91,7 +91,7 @@ against a document that is CORRECT.
                                          Range row on the expert thermal-model
                                          table; 101 with R10-USER-DOCS-FINAL's
                                          per-field rows on the options pages)
-    RESULT arch_modules_on_disk=94       (93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 85 until R10-WHY-NOW-WIDGET's slot_drivers.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
+    RESULT arch_modules_on_disk=95       (94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 85 until R10-WHY-NOW-WIDGET's slot_drivers.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
                                          66 until R9 F2.5's batchmath.py;
                                          65 until #1588's pump_arbiter.py; 64
                                          until #1408's store.py;
@@ -117,7 +117,7 @@ against a document that is CORRECT.
                                          bytes of, so nothing compared these
                                          numbers to a run between 2026-09-17
                                          and then)
-    RESULT arch_map_listed=94            (93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
+    RESULT arch_map_listed=95            (94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
                                          66 until R9 F2.5's batchmath.py;
                                          was 45; 11 were missing; 66 with
                                          #1588's pump_arbiter.py added to
diff --git a/dev/programme/delivery/3602.md b/dev/programme/delivery/3602.md
new file mode 100644
index 0000000000..92286b5d71
--- /dev/null
+++ b/dev/programme/delivery/3602.md
@@ -0,0 +1 @@
+- [#3602](https://github.com/tvofi/heatpump_optimizer/pull/3602) — **open**, R11-OUTSIDE-HONEST-STARTS-RUNS: r11 outside honest starts runs (R11-OUTSIDE-HONEST-STARTS-RUNS)
diff --git a/docs/architecture.md b/docs/architecture.md
index e69e659580..a56ebd065a 100644
--- a/docs/architecture.md
+++ b/docs/architecture.md
@@ -5,7 +5,7 @@ integration does rather than how it is built, start with
 [how-it-works.md](how-it-works.md).
 
 The shape is a thin Home Assistant layer wrapped around a much larger core that
-knows nothing about Home Assistant: 94 modules, of which 33 import the
+knows nothing about Home Assistant: 95 modules, of which 33 import the
 `homeassistant` package at module level, one more touches it inside a single
 function, and the rest take numbers in and give numbers back. The glue reads
 entity states, writes actuators and persists learned state. Keeping those two
@@ -128,6 +128,8 @@ custom_components/heatpump_optimizer/
 │                         #   falls in, for the solve and the pump arbiter
 ├── duty_legs.py          # The legs a step is served in, the switches between
 │                         #   them, and what a stop at one costs the plan
+├── runs.py               # What a compressor start is in a plan, which runs of
+│                         #   a relaxed plan ship, and the shortest run and pause
 ├── plan_slots.py         # A channel's step schedule as the heating slots a plan publishes
 ├── slot_drivers.py       # Why each step runs or idles: five signed driver weights,
 │                         #   and the current step's "why now" for the card
@@ -280,7 +282,7 @@ custom_components/heatpump_optimizer/
 
 ## The Home Assistant boundary
 
-33 of the 94 modules import `homeassistant` at module level: `__init__`,
+33 of the 95 modules import `homeassistant` at module level: `__init__`,
 `config_flow`, `coordinator`, `open_meteo`, `frontend`, the six entity
 platforms `sensor`, `binary_sensor`, `button`, `climate`, `switch`, `datetime`,
 and the supporting modules `accuracy`, `away`, `boost`, `currency`, `debugger`, `defrost`,
@@ -289,7 +291,7 @@ and the supporting modules `accuracy`, `away`, `boost`, `currency`, `debugger`,
 reaches for `homeassistant.util.dt` inside a function, as the fallback when no
 clock function was injected.
 
-The other 60 modules are deliberately free of it, so each can be driven
+The other 61 modules are deliberately free of it, so each can be driven
 directly by `tests/features.py` with no Home Assistant running. That matters
 because the failure mode of this integration is a *plausible* plan: a detector
 that never fires, or a watchdog that lets a flatline through, produces output
@@ -342,7 +344,7 @@ solar  ─┘        │                                                    │
 ```
 
 Both optimizer paths share one set of cost terms — the comfort penalty, the
-terminal cost, the cycling and capacity charges — so enabling hot water cannot
+terminal cost, the start and capacity charges — so enabling hot water cannot
 change the space-heating objective. That is not hypothetical tidiness: it used
 to, and the two objectives had silently drifted apart.
 
diff --git a/docs/configuration.md b/docs/configuration.md
index ae9cef0a84..e8c1d0c36b 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -489,7 +489,7 @@ warmth.
 | How hard to chase low prices | 1.0 | 0.1–10 | Higher moves more heating into cheap hours and allows more swing. |
 | How strictly to hold the temperature | 5.0 | 0.1–20 | The most effective knob you have. It is weighed against the range you allow, so widening that range makes the optimizer bolder. |
 | Recalculate every | 30 min | 10–120, 5 steps | More often reacts quicker and does more work. |
-| Cost of one compressor start | 0.0 | 0–10, 0.05 steps | In the same currency as your prices. Discourages plans that switch on and off repeatedly. The **Compressor Starts** sensor counts *realised* starts and needs a power meter; the plan's own projected start count is not published on any entity. |
+| Cost of one compressor start | 0.0 | 0–10, 0.05 steps | In the same currency as your prices. Discourages plans that switch on and off repeatedly: above 0, the plan runs the pump in whole runs at or above its minimum power instead of averaging a lower level within a step. The **Compressor Starts** sensor counts *realised* starts and needs a power meter; the plan's own projected start count is not published on any entity. |
 | Caution with guessed prices | 0.0 | 0.0–2.0, 0.05 steps | Beyond the published horizon prices come from your learned daily shape. This adds a premium proportional to how wrong those guesses have tended to be. 0 trusts them at face value. |
 | Hold a safety margin where the model is unsure | off | on/off | Raises the comfort floor by the model's own expected error at that horizon, capped at 0.8 °C and shrinking as accuracy improves. |
 | Compressor replacement cost | 0 | 0–100 000, 100 steps | What a compressor swap costs including labour, in your price currency. Divided by the rated starts below it prices each realised start. 0 keeps the start counter pure observation. |
diff --git a/docs/design/2026-11-12-honest-starts-and-runs/design.md b/docs/design/2026-11-12-honest-starts-and-runs/design.md
new file mode 100644
index 0000000000..721abadec9
--- /dev/null
+++ b/docs/design/2026-11-12-honest-starts-and-runs/design.md
@@ -0,0 +1,168 @@
+# Honest starts and contiguous runs: price a start as one start, ship runs the pump can run
+
+Outside proposal. The design below was written before any code, against tvofi/main `fc2a7edcf2` (v7.1.11), and every line it cites is at that SHA; the build this pull request carries is recorded in the last two sections, at base `870238eb21`. The production files cited are unchanged since `14f227c5b`, where the report was taken. No finder harness: outside report. The "Spike" figures are from a throwaway script on the golden profiles: they show the shape, they are not acceptance evidence.
+
+## Finding (Bankaifan, 2026-11-12, alpha innotec LWDV 91-1/3, Luxtronik 2.1)
+
+Install: 600 l combi store (`dhw_combi_tank_enabled`, 504 l around a 40 l coil), `single_tank_valve`, floor heating on a slab, `space_setpoint_unit: return`, `flow_min_lift_k` 0.5, controller hysteresis 0.5 K heating and 4 K hot water, `wear_autotune_enabled` with a wear price of 0.25 per start. The metered running draw is 1.1 to 3.3 kW. The datasheet minimum of 0.53 kW is never held: under about 1 kW the compressor cycles. Day: flat prices 0.34 to 0.45 per kWh, house at 24.1 °C, band 21.5 to 25.5 °C.
+
+| | modulation / min power / cycling cost | Plan for 24 h | Published saving | What is wrong |
+|---|---|---|---|---|
+| 1 | modulating / 0.53 / 10 | space at 0.13 to 0.37 kW for hours; hot water in 7 charges of 15 to 30 min, each 51 to 52 °C; about 7 kWh | -0.24 | the plan shows almost no start, the pump cycles all day |
+| 2 | on_off / 1.1 / 10 | 1.1 kW nearly without a pause, 25 kWh | -6.27 | running through is cheaper than one stop |
+| 3 | on_off / 1.1 / 0.25 | 16 blocks, 11 of them hot water (11.1 of 12.8 kWh) | -1.44 | the store is charged through the hot-water channel, one start per block |
+
+No setting yields a few long runs in the cheap hours. Four causes, each read off the code:
+
+1. **The start term prices swing, not starts.** `cycling_penalty_batch` (`optimizer.py:1620`) is `cost * sum|dP| / (2 * p_max)` over the combined draw (`optimizer.py:4834`). A constant level under the floor has no swing and is free, while each such step ends in a stop (row 1). A start to level P costs `P / p_max` of the configured cost, a third at 1.1 of 3.3 kW, so the number is not "per start-stop cycle". A level change inside a run is charged though nothing starts. `count_compressor_starts` (`optimizer.py:1578`) books a start at step 0 whether or not the compressor already runs.
+2. **The projection raises, step by step.** `_onto_band` (`thermal_model.py:1700`) lifts every value in `(0, p_min)` to `p_min` on its own step: the energy there grows by the factor `p_min / P`, or the solve avoids it and leaves single steps (rows 2 and 3). `_relaxed_starts` (`optimizer.py:195`) adds one candidate; nothing bundles.
+3. **The metered floor never reaches the plan.** `solve_band` (`draw_range.py:637`) learns the top only. `DrawRange.observed` (`draw_range.py:229`) already holds the low end, for diagnostics.
+4. **Hot-water starts are priced nowhere.** `_plan_dhw_min_cost` (`dhw_planner.py:1326`) is a linear program without a start term, and on a combi store `_co_optimize` returns `_combi_flux_exchange`'s re-plan unscored (`optimizer.py:3360`). Reading, to confirm on the replay: the exchange re-plans hot water against the space side's drain with the space plan held, so the heat the house takes from the store is re-bought on the hot-water channel (row 3).
+
+## Scope: four parts, one owning seam each
+
+| Part | What | Owner | Callers |
+|---|---|---|---|
+| P1 | the start count | new pure module `runs.py`, beside `wear.py` | `_grid_terms` (`optimizer.py:3462`), the published count (`optimizer.py:5129`) |
+| P2 | commit and dispatch: plans in `{0} ∪ [floor, cap]` as bundled runs | `runs.py` (commit), `optimizer.py` (dispatch, selection) | `_optimize_space_only` (`:4891`), `_optimize_with_dhw` (`:5154`) |
+| P3 | the metered floor in the solve band | `draw_range.py` | `coordinator._solve_band` (`coordinator.py:2442`), unchanged |
+| P4 | duty changes and hot-water charges as part of a run | `dhw_planner.py`; the term is P1's | `_co_optimize`, `_combi_flux_exchange` |
+
+P1 and P2 are best landed together: they move the same three goldens. P4's switch price is the planned item R10-DUTY-SWITCH-PLANNER-PRICE and waits for part A (#3461); its hot-water half waits for R10-OUTSIDE-DHW-START-HYSTERESIS (#3440). `pump_arbiter.py` is not touched by any part.
+
+**Engaged.** A solve is engaged when a start has a price (`_effective_cycling_cost() > 0`, `coordinator.py:10477`) or the install cannot duty-cycle (`levels_clamped`, `thermal_model.py:1573`). An unengaged solve takes today's path with a zero start term and is byte-identical: its owner has said a start costs nothing and the probe says a sub-floor average is deliverable.
+
+## Shape
+
+```
+coordinator: running now (StartCounter.running), band (solve_band, P3), learned switch (duty_switch, P4)
+   -> optimize: hot-water plan (LP, then runs.commit in P4)
+   -> relaxed space solve: multi-start as today, objective scores the levels as solved, start term = P1
+   -> engaged and not realizable?  runs.commit -> masks -> dispatch each (pinned bounds) -> lowest objective ships
+   -> result: every running step in [floor, cap]; compressor_starts = P1's integer count
+```
+
+**P1, the count.** With `q` the combined draw, `f` the band's floor and `r[k] = min(1, q[k] / f)` the share of step k the compressor runs:
+
+`starts(q) = sum over k of r[k] * (1 - r[k-1])`, with `r[-1]` 1 if the compressor runs at solve time, else 0.
+
+On a plan whose steps are all off or at the floor or above, this is the integer number of off-to-on edges. A trickle at share `r` costs `r * (1 - r)` per step and is never free. A level change inside a run costs nothing. A run that continues from the measured state costs nothing, so a re-solve does not charge a running pump for staying on and does charge it for stopping and coming back. The term is `cycling_cost * starts`, zero at zero cost as today. One formula serves the gradient and the selection: products of clipped linear terms, with a batch twin through `row_sums` like every other term. `SolveInputs` (`optimizer.py:2457`) gains `compressor_running: bool = False`; the coordinator fills it from `_start_counter.running` (`coordinator.py:3908`).
+
+**P2, commit and dispatch.** The relaxed solve drops the projection from its objective: `_realize_draw`, `_realize_joint`, `_published_levels`, `_scores_rounded`, `_relaxed_starts`, `_levels_relaxed` and with them `project_planned_levels`, `_onto_band` and `project_space_against` go. If the relaxed plan is realizable (no running step under the floor), it ships as it is. Otherwise:
+
+- `runs.commit(q, prices, floor, caps, start_cost, band, running, forced) -> mask` is a dynamic program over the steps with the state (on or off, energy balance). The balance is the committed energy less the relaxed plan's up to that step, in quarters of one floor step, held inside `±band` floor steps and within half a floor step at the end. An on step runs at `max(q[k], floor)` and costs its price; an off-to-on edge costs `start_cost`. Pins, off windows, blocks and a cap under the floor are forced. The balance is what replaces "raise": a step lifted to the floor is paid for by a step left out, so the plan's energy stays the relaxed plan's.
+- Three bands (2, 6 and 24 floor steps: tight tracking to "same energy, any time") give at most three distinct masks. Each is dispatched: `_apply_pins_to_bounds` (`optimizer.py:1851`) with the mask as pins gives on steps `[floor, cap]` and off steps `(0, 0)`, the bounds a manual plan already produces, and one warm `_lbfgsb_run` with its polish sets the levels. The lowest objective ships. Beside a fixed hot-water plan a step it already runs is forced on and the space floor there is the floor less `dhw[k]`, the rule `project_space_against` has today.
+- Run and pause lengths: on the 15-minute grid every run and pause is at least one step, above `early_cutoff.MIN_ON` and `MIN_OFF` (`early_cutoff.py:90`). `commit` takes both as step counts, so a shorter plan step keeps them.
+
+**P3, the floor.** `solve_band` books `min_kw = max(configured, learned floor)`, never above the top. The learned floor is the 10th percentile (`LOW_PERCENTILE`) of the window's running samples whose ask was at or under the floor in force (within `AGREE_TOLERANCE`), once `MIN_SAMPLES` of those exist: the pump was asked for its least and drew more. Restricting to those asks is the guard that matters: a cold week of high asks would otherwise raise the floor to the draw of those. It only raises, and only by more than `AGREE_TOLERANCE`, so a pump that draws what it is asked keeps its figure. It lapses like the ceiling store, is keyed to the configuration like the latch, and stays out where `plan_writes_power()`. It moves the band on engaged solves only; `SolveBand` gains the floor's source and sample count.
+
+**P4, duties and hot water.** The start count takes both series and adds, for each duty change inside a run, that direction's learned stop probability (`Direction.p` while `usable`, #3461), in the order `step_duty` and `_share` serve them (`pump_arbiter.py:492`, `:1680`): a both step is hot water first, so it holds one change into space. `median_off_s` cuts the next step's headroom in `_solve_space` (`optimizer.py:4372`), as the R10 note sketched. The hot-water schedule passes through the same `runs.commit` inside `_build_dhw_requirements` (`dhw_planner.py:951`), accepted only if the planner's own tank walk holds every floor and ceiling the uncommitted plan held and every run meets the planner's start rule (#3440's rebuild); the disinfection step is forced. Where the space plan is known (the `_co_optimize` re-plan and each round of the combi exchange), a charge that begins right after a space run pays only `p(space to hot water)` of a start, so hot water joins the end of a run. On a combi store that is the "one charge": the run is formed and priced on the store's total draw, and the split inside it only chooses the COP curve and the mode written.
+
+## Alternatives
+
+- **Scale the swing term, or add a penalty on levels under the floor.** A local method does not move a block across off steps: the trickle stalls at partial levels, and the flat band `_relaxed_starts` was written for returns.
+- **Minimum run time as constraints (MILP).** `OptimizationConfig`'s own comment rules it out for the hardware; the commit program is the same decision on a separable surrogate, with the true objective choosing among its answers.
+- **Keep the projection, repair it with a bundling pass.** Two owners of what ships, and the objective would still score a plan the repair then changes.
+- **Sigma-delta rounding of the relaxed plan.** It keeps the energy and spreads the pulses evenly: the most starts, not the fewest.
+- **Enforce runs in the arbiter or the supply gate (#3456) alone.** The plan would still price heat it does not get; the gate guards writes, it cannot move energy.
+
+## Sibling sites
+
+`git grep -n -E "cycling_penalty|count_compressor_starts|project_planned_levels|project_space_against|_onto_band|_realize_|_relaxed_starts|_scores_rounded|_published_levels" -- 'custom_components/heatpump_optimizer/*.py'` prints `optimizer.py` and `thermal_model.py` only. Covered: both solve paths, the published count, the batch twin. Kept: `duty_floor_kw` (`optimizer.py:3316`) and `planned_draw_runs`' floor argument, which the arbiter reads. Out of scope: the two-zone continuation in `move_starts`, the valve-schedule comparison (`optimizer.py:4028`; commit runs on each candidate or once on the winner, the fixer measures), the stratification of a combi store (#3398).
+
+## Open pull requests
+
+Read on 2026-11-12 from the pull-request list (35 open), the threads of #3440, #3456 and #3461, and the heads by git.
+
+| PR | State | Relation |
+|---|---|---|
+| #3456 supply minimum run and pause | open; accepted as R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE, timing to move to the switch's own state | builds on. Its open owner decision (a planned run that ends inside the minimum is skipped, "a trade between delivered heat and compressor starts") meets a committed plan only off the grid: commit keeps every planned run and pause at or above the gate's minimums, so the plan no longer books heat the gate would skip |
+| #3457 stale step write | open; its change is on main as #3478 | builds on |
+| #3461 duty-switch learning, part A | open, draft | builds on. P4's switch price is the item that body names R10-DUTY-SWITCH-PLANNER-PRICE; it adds the reader and its first caller, as the body asks of the first part that reads the estimate. R10-DUTY-SWITCH-RESTART-LEARNING-PR-B (order latch, minimum share) stays the arbiter's: a committed plan holds no both step into the costly direction, so B acts on unengaged installs and on leases. Edges into the start counter (part D of the design review's split) would feed `compressor_running` better than the per-cycle counter |
+| #3440 start hysteresis | open; to be rebuilt as R10-OUTSIDE-DHW-START-HYSTERESIS after its own design note | complements, and P4 goes after it (`dhw_planner.py`). The maintainer's ruling there makes the start condition a rule the planner follows when it places a run, against the temperature written to the pump. `runs.commit` on the hot-water schedule takes that rule as its feasibility check, so the two do not place runs twice. The maintainer measured 64 of 114 planned hot-water runs starting within 4 K of the set-point, mostly short top-ups: the same shape as row 1. The raised heating lift becomes the one value for the write and the plan's pricing there; P3 is the metered check beside it, not a second source |
+| #3439 disinfection hold; #3497 R10-OUTSIDE-DISINFECTION-SETPOINT | open | `pump_arbiter.py` and `setpoint_check.py` only. P4 forces the disinfection step, so no commit moves or drops it |
+| #3434, #3435 learners | open; #3444 and #3468 on main touch the same learners | no planner file either way |
+| #3481 R10-ADVISOR-STEADY-START | open | conflict in text only: it also adds a `SolveInputs` field |
+| the other open pull requests | | checked by diff for every head from #3000 that is not on main: none touches `optimizer.py`, `dhw_planner.py`, `draw_range.py`, `wear.py` or `thermal_model.py` (#3356 does, and is on main as #3372) |
+
+Already on main and relied on: #3308 (replaced by P2), #3405 and #3433 (the feedback loop is no longer asked to hold a level under the pump's floor), #3358 and #3398, #3372.
+
+## Evidence, by file
+
+`tests/features.py`, failing today:
+1. Start count: integer edges on a realizable plan; a constant sub-floor level costs more than zero; a level change inside a run costs zero; a start to the floor and a start to the maximum cost the same; a running compressor continues free; batch rows equal the scalar.
+2. Commit: every on step in `[floor, cap]`; forced steps kept; end balance within half a floor step where one exists; identity on a realizable input; run and pause lengths.
+3. Floor: high asks alone never raise it; `MIN_SAMPLES` floor asks drawing 1.1 against a configured 0.53 raise it to 1.1; a pump drawing its ask keeps the configured figure; lapse and reconfiguration drop it.
+4. P4: a both step and a hot-water-then-space boundary each count `p`; with no usable direction the count is P1's; a committed hot-water plan holds the uncommitted plan's floors.
+
+Null controls: (a) at zero cost on an install that can duty-cycle, every plan is byte-identical: 53 of the 55 value goldens. (b) An empty duty-switch learner against one saturated at p = 1 with a zero cost: identical plans. (c) A relaxed plan that is already realizable ships unchanged.
+
+Goldens that move, claimed with direction in `tests/golden/claimed_drift.txt`: `cycling_cost` and `everything_on`, the two solver goldens that price a start (`coord_all_features` also prices one, but its capture does not solve); their plans hold 9 and 11 sub-floor steps today (first two, measured). `runs.py` enters a measured closure in `tests/closures.json`; the deleted projection pays `tests/structure_budgets.json`.
+
+Replay: the reporter's day as `tests/replay/bankaifan-2026-11-12.json` (`hpo-replay/1`, from the debug bundle), run with modulating, 0.53 kW configured and the wear price. Acceptance on it:
+- at most 4 compressor starts in 24 h, no planned run or pause under 10 min, no planned level between 0.1 kW and the band's floor;
+- plan energy not above the relaxed plan's by more than one floor step (no running through as in row 2), and the published saving not negative: cost at or under the plan's own reference;
+- room inside 21.5 to 25.5 °C and tap temperature at or above 47 °C throughout.
+
+**Spike** (golden house, no hot water, floor 1.1, max 3.3, start cost 2.5, 96 steps; commit as above, dispatch through pins; script `dev/audit/harnesses/honest_starts_spike.py` on the branch `spike/honest-starts-and-runs` of Bankaifan/heatpump_optimizer, which never merges):
+
+| Profile | Today, modulating | Today, on_off | Relaxed, no start term | Committed |
+|---|---|---|---|---|
+| shoulder weather, flat prices | 18 sub-floor steps, 0.86 kWh | 1 run, 5.78 kWh | 16 sub-floor steps, 5.79 kWh | 1 run, 5.98 kWh, same lowest room temperature, objective without starts 9.58 against 9.60 |
+| shoulder weather and prices | 15 sub-floor steps, 1.03 kWh | 1 run, 4.40 kWh | 16 sub-floor steps, 7.20 kWh | 1 run, 6.33 kWh (wins at this cost) or 2 runs, 7.26 kWh |
+| mild winter, typical prices | realizable | realizable | realizable, 2 runs | unchanged |
+
+## Solve time
+
+Measured on the golden scenarios: a space solve makes 8 `_lbfgsb_run` calls today (4 starts, each with its polish). An unengaged solve gains nothing but a boolean. An engaged one gains the commit program (2 to 63 ms in plain Python in the spike, the widest band the slowest; states are 96 × 2 × at most 193) and 2 calls per distinct mask, at most 6, warm and mostly at a bound. An on_off install loses the rounded scoring's flat band and the `_relaxed_starts` run. In the spike the three candidates, each re-solved through the whole `optimize`, added 0.10 to 0.62 s to a 0.08 to 0.52 s solve on x86; that is an upper bound. `tests/stress_budgets.json` decides.
+
+## Decisions for the owner
+
+1. A priced start engages bundling on a modulating install too, which moves the three goldens. Engaging on on_off alone would leave row 1 as it is.
+2. P3: the learned floor moves the plan (proposed), or stays a notice beside the configured figure.
+3. Whether P4's hot-water half joins R10-DUTY-SWITCH-PLANNER-PRICE or R10-OUTSIDE-DHW-START-HYSTERESIS or is a group of its own, and whether P1 and P2 land as one group.
+
+## As built in this pull request
+
+Base `870238eb21` (v7.1.12, with #3461 merged). Where the build differs from the sections above, this section is the record.
+
+- **P1, the count.** `runs.start_count` and its batch twin count `a[k] * (1 - r[k-1])`, with `a[k] = min(1, q[k] / MIN_RUNNING_DRAW_KW)` (the step runs at all) and `r` as above. The form proposed above, `r[k] * (1 - r[k-1])`, charges a trickle at most a quarter of a start per step, and on the reporter's install a trickle plan won the comparison against a plan of runs. Now a step under the floor leaves its successor the start that step is. On a plan whose steps are all off or at the floor or above, both forms are the integer edge count. `SolveInputs.compressor_running` is the duty-switch learner's settled running signal where one is listened to, else the metered draw against `on_threshold_kw`, else the executing step; the start counter follows one sample per optimization interval and is no reading for it. `compressor_starts` publishes the shipped plan's integer edge count.
+- **P2, commit.** The relaxed multi-start runs with the start term off (`_start_term_off`). The count is bilinear in neighbouring steps, and a descent priced with it stayed where its start lay: a trickle it did not leave, or one run it did not break. `_commit_runs` then builds the candidates (`_run_plans`): the per-step projection, raised and rounded; each band's `runs.commit` mask (`BANDS`, widening to the whole horizon; a balance outside its band is penalised by `OUT_OF_BAND`, never refused); the relaxed plan where it already runs. It scores all of them in one `objective_batch` call on the true objective with the start term, re-solves the levels of the best two inside their runs, polishes the better one (`_pinned_runs`) and ships the lowest score. So no plan ships worse than the projection, and a failure anywhere in the stage ships the projection. A committed space step runs at the floor or above on its own, also beside a hot-water charge: the plan stays one the pump can run when the combi exchange moves the charge afterwards. On an install that can duty-cycle, a step capped under the floor still cycles; on one that cannot, it stays off.
+- **P3, the floor.** The floor store admits only asks at or under the configured floor × (1 + `AGREE_TOLERANCE`), and each sample lapses on its own age, so an engaged plan cannot ratchet the floor: it lapses back to the configured figure and is learned again. Persisted as `draw/floor`.
+- **P4, hot water.** `runs.commit_store` is a program on the planner's linear store (`runs.Store`, 0.25 K grid). A charge runs whole steps at the run power and may end inside its last step where the store is full: the pump runs at its level and stops, so that step is no level under the floor (a tail). A charge that starts in the step it ends in is a whole run and must last `MIN_ON`. On an install that cannot duty-cycle a tail stays at the floor or above, the level contract `clamp_planned_levels` has today. A step without a charge is not bound by the charge ceiling, because a combi store's space side heats it past, and stops at the store's rating, as `thermal_model.store_step` does. Without those two rules the program had no feasible path in most exchange rounds on the reporter's install and the planners' trickle plan shipped. What a charge pays besides its energy follows the compressor (`_charge_costs`): a start where it is off, the learned share of one for each duty change where the space plan runs. The hot-water plan that ships is the cheaper, in energy at the planning prices plus starts, of the committed plan and the planners' own plan with every step under the floor run at the floor (`_commit_charges`); so an engaged plan holds no charge step under the floor but a tail. Limit: the program charges at the run power only, so a modulating pump's long part-load charge comes from the second candidate.
+- **Combi store.** The space plan is not re-solved after the flux exchange. Charges move the store in whole steps, the space side's flux moves with the store, and the rounds need not settle: `_held_round` keeps the round whose store, walked by the model, falls least under the requirement, and of those the cheapest. `_settled` then settles the space plan against that hot-water plan. The space plan was solved around the first hot-water plan; the exchange's charges hold the store afterwards; the space runs still carry heat for a store those charges had not warmed (measured on the reporter's install: one hour at 3.4 to 3.5 kW into a store at its 55 °C limit), and a charge that left its step leaves a pause in the space run it sat in. Each space run is tried switched off and lower (`_TRIM_SHARES`), each pause run through at the floor. A candidate is kept only where the pair's objective on the model's own walk is lower and the store falls no further under the hot-water requirement, the promise a free re-solve cannot make. An unengaged solve does not run this stage and is byte-identical; its plans hold the same double heating, a finding for R10-COMBI-TANK that this pull request does not act on.
+- **Duty-switch price** (R10-DUTY-SWITCH-PLANNER-PRICE). `duty_switch.planner_reading` is the reader and the coordinator its one caller: per direction `Direction.p` while `usable`, else 0.0, into `OptimizationConfig.duty_stop_to_space` and `duty_stop_to_dhw`, priced by the start count and by the charge program. The `median_off_s` headroom cut is not built.
+- **`dhw_floor_breach_c`** is published under a block always, and on a solve that plans runs when a cap leaves some step under the pump's floor and the tank falls short.
+- **Tried and dropped, measured.** A store-hold term in the space objective (the space channel carries the store through the hot-water window): 16 % cheaper in the model, L-BFGS-B up to 24 s, and on a stratified combi store heating mode does not raise the top sensor. A hot-water re-plan pass on every priced solve with a separate tank: the same starts and costs on eight golden variants, more solve time.
+- **Not built**: the previous plan's mask as a candidate; #3440's start rule; the reporter's replay file.
+- **Run and pause minimums** `MIN_ON`, `MIN_OFF` live in `runs.py`; `early_cutoff` imports them.
+
+**Measured on the reporter's install.** Config entry of 2026-11-12 (504 l store around a 40 l coil, 0.53 kW configured and 1.1 kW metered floor, 3.5 kW, manual valve at 24 °C, hot water 47 °C minimum and 52 °C set-point in a 06:00 to 18:00 window, wear price 0.25 per start), the day-ahead prices of 12 and 13 November, synthetic weather, 24 h at 15 minutes. Script outside the tree; base `870238eb21` → head, one machine. A start is a running step after a step under the floor; "under the floor" excludes a charge's tail.
+
+| Day | Variant | Starts | Steps under the floor | kWh | Cost | Store at the end, °C |
+|---|---|---|---|---|---|---|
+| 12 Nov | modulating, 0.53 kW, 0.25 | 35 → 5 | 32 → 0 | 14.52 → 12.17 | 5.61 → 4.80 | 55.0 → 54.8 |
+| 12 Nov | modulating, 1.1 kW, 0.25 | 34 → 6 | 30 → 0 | 14.97 → 12.24 | 5.85 → 4.87 | 55.0 → 55.0 |
+| 12 Nov | on_off, 1.1 kW, 0.25 | 10 → 7 | 0 → 0 | 17.60 → 12.33 | 7.11 → 4.90 | 55.0 → 55.0 |
+| 12 Nov | modulating, 0.53 kW, 10 | 77 → 1 | 76 → 0 | 11.33 → 11.00 | 4.63 → 4.56 | 51.9 → 43.0 |
+| 13 Nov | modulating, 0.53 kW, 0.25 | 26 → 1 | 21 → 0 | 11.92 → 9.61 | 4.01 → 3.31 | 49.5 → 43.0 |
+| 13 Nov | modulating, 1.1 kW, 0.25 | 32 → 5 | 29 → 0 | 12.65 → 10.48 | 4.23 → 3.48 | 48.9 → 43.5 |
+| 13 Nov | on_off, 1.1 kW, 0.25 | 8 → 6 | 0 → 0 | 15.51 → 10.65 | 5.34 → 3.55 | 55.0 → 43.5 |
+| 13 Nov | modulating, 0.53 kW, 10 | 14 → 1 | 10 → 0 | 11.32 → 9.60 | 3.70 → 3.30 | 43.8 → 43.0 |
+
+Tap temperature inside the window is 47.0 °C or above on every row, base and head; the room trajectory is the same on every row (22.2 to 24.1 °C), since the valve feeds the floor from the store. Read the cost column with the last one: where the head ends the day with a colder store, part of the saving is heat not bought for the next day, which the objective's terminal term prices and a rolling re-solve never executes. The rows with the same end state are the first three: 14 to 31 % less cost. Part of what the base plans there is energy into a store at its limit, which a real pump would refuse, so the metered saving will be smaller than the modelled one.
+
+**Measured on the golden scenarios with runs planned** (the two goldens that price a start, and twelve variants of others with `cycling_cost` or `clamp_planned_levels` set; base → head): starts 2 to 29 → 2 to 8; steps under the floor up to 28 → none but four charge tails; the tank's worst shortfall 0.56 K at most → 0.42 K at most; lowest room between 0.54 K under and 0.32 K over the base's. Cost moves between −15 % and +9 %, and on `shoulder` at 0.5 per start from 3.33 to 6.96: the base plan there is 28 steps under the floor that the pump cannot deliver, and the base's own on_off projection of that scenario costs 7.39. The 54 goldens that price no start and can duty-cycle are byte-identical (`tests/env_drift.py --all`).
+
+## Solve time, as built
+
+One machine (2 cores, x86), base → head, wall seconds for one `optimize`. The fourteen golden variants above sum to 15.8 → 15.3: `cycling_cost` 1.04 → 0.20, `everything_on` 3.00 → 3.43, `winter_two_zone_dhw` 1.25 → 1.46, `valve_storage` 4.01 → 4.61, `shoulder` as on_off 0.96 → 1.76. The reporter's install: 0.8 to 3.8 → 1.5 to 1.8 at 0.25 per start, 5.3 to 6.4 → 1.5 to 1.8 at 10. The relaxed solve without the start term converges sooner than the priced one did; the commit stage adds two warm L-BFGS-B runs and one polish; `_settled` adds about twenty walks of the pair at about 3 ms each. `tests/stress.py` passes.
+
+## Notes for the fixer
+
+- 2, 6, 24 and the quarter-step balance grid are constants from the spike, not measured thresholds; name them.
+- The start count's floor needs a guard for a configured floor of 0 (`MIN_RUNNING_DRAW_KW`, `thermal_model.py:1194`).
+- Dispatch must not go through `h.space_pins`: the safety release of manual pins would report committed steps as released.
+- `_batch_fd_gradient` should skip fixed variables on a committed mask; most of the 96 are fixed.
+- The previous plan's mask, shifted by the elapsed steps, is a free fourth candidate and keeps ties from moving a standing run.
+- A commit that finds no mask inside any band (caps, pins) ships the tightest band's best effort and says so in the status; it never falls back to raising.
diff --git a/docs/how-it-works.md b/docs/how-it-works.md
index 797a51c760..ab6125273e 100644
--- a/docs/how-it-works.md
+++ b/docs/how-it-works.md
@@ -124,7 +124,7 @@ What the space heating solve minimizes:
 |---|---|
 | `grid_cost(P_space + P_dhw)` | Electricity, piecewise in PV surplus, × `price_weight` |
 | comfort terms | Pull toward the target, plus penalties for breaching the floor/ceiling |
-| cycling cost | Compressor start-stop wear, × `price_weight` |
+| cycling cost | Compressor wear: the cost of one start × the plan's starts, × `price_weight` |
 | capacity tariff | The month's peak charge exposure, × `price_weight` |
 | terminal cost | The value of heat left stored at the end of the horizon |
 
@@ -157,7 +157,17 @@ trade off.
 would be priced in invented units, and measured, it costs about 5% of the
 two-zone winter bill for no reduction in compressor starts. Discouraging
 chatter is the cycling cost's job, and that is denominated in currency per
-start-stop cycle.
+compressor start.
+
+**A priced start is counted as one start.** A start is an off-to-on edge of the
+compressor, whatever level it starts to; changing level inside a run is free.
+A level under the pump's minimum power is a duty-cycle average, so the solve
+counts it as the starts it is. With a start priced, or on an install that
+cannot duty-cycle, the solve first plans without the start cost, then commits
+that plan to whole runs at or above the minimum power, at the same energy: a
+step lifted to the minimum is paid for by a step left out. Several such plans
+are scored with the start cost included, and the cheapest ships. (Finding and
+method: Bankaifan, pull request 3529.)
 
 ### Weather anticipation is emergent, not a bonus
 
diff --git a/tests/backtest.py b/tests/backtest.py
index d3a63a7a72..f6cdd1917e 100644
--- a/tests/backtest.py
+++ b/tests/backtest.py
@@ -38,8 +38,8 @@ from profiles import DT, house, prices, weather
 from heatpump_optimizer.optimizer import (
     HeatPumpOptimizer,
     OptimizationConfig,
-    count_compressor_starts,
 )
+from heatpump_optimizer.runs import edge_count
 from heatpump_optimizer.thermal_model import (
     ThermalModel,
     ThermalParameters,
@@ -100,7 +100,7 @@ def score(model, opt_cfg, power, price_series, outdoor, wind, rain, solar, state
         # Degree-hours below the comfort floor: the honest way to compare
         # strategies, since a plan can always be made cheaper by being colder.
         "violation": float(np.sum(np.maximum(0.0, floor - indoor)) * DT),
-        "starts": count_compressor_starts(power),
+        "starts": edge_count(power),
         "peak": float(np.max(power)),
     }
 
diff --git a/tests/closures.json b/tests/closures.json
index e29b8ded09..e3fd59f47b 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -260,6 +260,7 @@
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/replay_doc.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/services.yaml",
@@ -331,6 +332,7 @@
    "custom_components/heatpump_optimizer/payload.py",
    "custom_components/heatpump_optimizer/plan_step.py",
    "custom_components/heatpump_optimizer/pv.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/tariff.py",
    "custom_components/heatpump_optimizer/thermal_model.py",
@@ -428,6 +430,7 @@
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/replay_doc.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
@@ -538,6 +541,7 @@
    "custom_components/heatpump_optimizer/quiet_windows.py",
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
    "custom_components/heatpump_optimizer/slab_seed.py",
@@ -643,6 +647,7 @@
    "custom_components/heatpump_optimizer/quiet_windows.py",
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
@@ -763,6 +768,7 @@
    "custom_components/heatpump_optimizer/quiet_windows.py",
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
@@ -894,6 +900,7 @@
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/replay_doc.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
@@ -1025,6 +1032,7 @@
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/replay_doc.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
    "custom_components/heatpump_optimizer/slab_seed.py",
@@ -1164,6 +1172,7 @@
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/replay_doc.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/services.yaml",
@@ -1302,6 +1311,7 @@
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/replay_doc.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/services.yaml",
@@ -1471,6 +1481,7 @@
    "custom_components/heatpump_optimizer/payload.py",
    "custom_components/heatpump_optimizer/plan_step.py",
    "custom_components/heatpump_optimizer/pv.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/tariff.py",
    "custom_components/heatpump_optimizer/thermal_model.py",
@@ -1632,6 +1643,7 @@
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/replay_doc.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/services.yaml",
@@ -2163,6 +2175,7 @@
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/replay_doc.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/services.yaml",
@@ -2359,6 +2372,7 @@
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/replay_doc.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/services.yaml",
@@ -2517,6 +2531,7 @@
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/replay_doc.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
@@ -2668,6 +2683,7 @@
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/replay_doc.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/services.yaml",
@@ -2850,6 +2866,7 @@
    "custom_components/heatpump_optimizer/quiet_windows.py",
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/slab_seed.py",
@@ -3032,6 +3049,7 @@
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/replay_doc.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/services.yaml",
@@ -3425,6 +3443,7 @@
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/replay_doc.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
@@ -3513,6 +3532,7 @@
    "custom_components/heatpump_optimizer/payload.py",
    "custom_components/heatpump_optimizer/plan_step.py",
    "custom_components/heatpump_optimizer/pv.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/tariff.py",
    "custom_components/heatpump_optimizer/thermal_model.py",
@@ -3595,6 +3615,7 @@
    "custom_components/heatpump_optimizer/quiet_windows.py",
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
@@ -3702,6 +3723,7 @@
    "custom_components/heatpump_optimizer/quiet_windows.py",
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
    "custom_components/heatpump_optimizer/slab_seed.py",
@@ -3765,6 +3787,7 @@
    "custom_components/heatpump_optimizer/plan_step.py",
    "custom_components/heatpump_optimizer/presets.py",
    "custom_components/heatpump_optimizer/pv.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/tariff.py",
    "custom_components/heatpump_optimizer/thermal_model.py",
@@ -3865,6 +3888,7 @@
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/replay_doc.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
@@ -3964,6 +3988,7 @@
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/replay_doc.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
@@ -4007,6 +4032,7 @@
    "custom_components/heatpump_optimizer/payload.py",
    "custom_components/heatpump_optimizer/plan_step.py",
    "custom_components/heatpump_optimizer/pv.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/tariff.py",
    "custom_components/heatpump_optimizer/thermal_model.py",
@@ -4089,6 +4115,7 @@
    "custom_components/heatpump_optimizer/quiet_windows.py",
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
@@ -4516,6 +4543,7 @@
    "dev/audit/harnesses/r10_water_setpoint_feedback.py",
    "dev/audit/harnesses/r10_weekday_range_twins.py",
    "dev/audit/harnesses/r11_denominator_planted.py",
+   "dev/audit/harnesses/r11_honest_starts_runs.py",
    "dev/audit/harnesses/r11_owner_criteria.py",
    "dev/audit/harnesses/r11_plan_page_inventory.py",
    "dev/audit/harnesses/r11_relay_3358_skip.py",
@@ -5282,7 +5310,7 @@
   },
   "tests/boost_drift_replay.py": {
    "rc": 0,
-   "seconds": 150.2
+   "seconds": 341.1
   },
   "tests/card.mjs": {
    "rc": 0,
@@ -5317,7 +5345,7 @@
    "seconds": 21.5
   },
   "tests/entities.py": {
-   "rc": 0,
+   "rc": 1,
    "seconds": 867.9
   },
   "tests/env_drift.py": {
@@ -5374,7 +5402,7 @@
   },
   "tests/plan_view.py": {
    "rc": 0,
-   "seconds": 0.8
+   "seconds": 1.8
   },
   "tests/solar_alignment.py": {
    "rc": 0,
@@ -5390,7 +5418,7 @@
   },
   "tests/typing_ruler.py": {
    "rc": 0,
-   "seconds": 30.8
+   "seconds": 20.8
   },
   "tests/validate.py": {
    "rc": 0,
diff --git a/tests/deployment_shape.py b/tests/deployment_shape.py
index f1e6575540..5008f65f55 100644
--- a/tests/deployment_shape.py
+++ b/tests/deployment_shape.py
@@ -37,9 +37,9 @@ child from ``inspect.getfile``.
 
 COST OF THE SHAPE (#1218, round-5 D3-08). Materialising the shape copies the
 tracked package file by file (``_materialise``, below), and the gate's tracer
-records every read, so this lane's recorded closure is the package: all 113
+records every read, so this lane's recorded closure is the package: all 114
 files under ``custom_components/heatpump_optimizer/``, Python and non-Python
-alike (112 until #3616's ``slab_seed.py``, 111 until R10-START-COUNTER-EDGES's ``running_signal.py``, 110 until
+alike (113 until R11-OUTSIDE-HONEST-STARTS-RUNS's ``runs.py``, 112 until #3616's ``slab_seed.py``, 111 until R10-START-COUNTER-EDGES's ``running_signal.py``, 110 until
 R10-ADVISOR-STEADY-START's ``whatif.py``, 109 until R10-DUTY-SWITCH-PLANNER-PRICE's
 ``duty_legs.py``, 108 until the supply-hold PR's ``supply_hold.py``, 107 until
 R10-DUTY-SWITCH-RESTART-LEARNING's ``duty_switch.py``, 78 until R9 F2.5's ``batchmath.py``, 79 until R9 UI-1's six brand
@@ -57,9 +57,10 @@ which drives the CI ratchet's archscore measurement and so opens the package
 the way this lane's recorder does. A diff touching any production file
 therefore selects this lane. That is a selection cost, not a
 duplicate-assertion one: the same
-recording finds 163 of the 528 script pairs (33 choose 2) sharing 0.80 or more
+recording finds 164 of the 528 script pairs (33 choose 2) sharing 0.80 or more
 of their production-module closure (162 before #3616 re-recorded the closures
-that import the coordinator), all 163 among the 406 pairs whose two
+that import the coordinator; 163 before R11-OUTSIDE-HONEST-STARTS-RUNS's recordings joined
+config_flow_steps.py/debug_collect.py at 0.80), all 164 among the 406 pairs whose two
 scripts each have a non-empty production closure (``tests/arch_score.py``,
 ``tests/ha_contract.py``, ``tests/layout.py`` and ``tests/md_tables.mjs`` have none;
 ``tests/harness_headers.py`` joined the comparable set, and ten pairs, when
@@ -104,7 +105,8 @@ R10-OUTSIDE-DHW-START-HYSTERESIS's block_duty.py check that the coordinator's
 input read puts the pump's start hysteresis on the state builds a coordinator,
 which grew that script's closure from 74 to 91 production files (75 to 92
 beside whatif.py): nine pairs joined at the 0.80 floor and one left, the
-count from 154 to 162).
+count from 154 to 162; #3616's re-record moved it to 163, and
+R11-OUTSIDE-HONEST-STARTS-RUNS's recordings, which add runs.py, to 164).
 Eighteen of the pairs sit at exactly 1.00 -- arch_score_head.py/deployment_shape.py,
 arch_score_head.py/entities.py and deployment_shape.py/entities.py
 (98 shared production files each), doc_claims.py/harness_headers.py
diff --git a/tests/features.py b/tests/features.py
index f8a7f6c15a..53946f1be4 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -7063,6 +7063,68 @@ R.check(
     f"NaN and nowhere else",
 )
 
+# A fixed variable costs no simulated row (design note n6): its step is zero,
+# so its row would be x0 again and the division never reads the value. The
+# batch is the free variables' rows, behind x0 itself when the caller asks the
+# batch for f(x0) too; counted on the production symbol, at a bound set that
+# is mostly fixed, the shape a committed mask and a full DHW block produce.
+_gate_rows_seen: list[int] = []
+
+
+_gate_wide_x0 = np.array([1.0, 2.0, 0.0, 4.0, 0.5, 6.0])
+_gate_wide_bounds = [
+    (0.0, 6.0), (2.0, 2.0), (0.0, 0.0), (4.0, 4.0), (0.0, 6.0), (6.0, 6.0),
+]
+
+
+def _gate_wide_batch(mat, *_a):
+    m = np.atleast_2d(np.asarray(mat, dtype=float))
+    _gate_rows_seen.append(m.shape[0])
+    return np.sum((m - np.array([3.0, 1.0, 5.0, 2.0, 0.0, 1.0])) ** 2, axis=1)
+
+
+_gate_wide_f0 = float(_gate_wide_batch(_gate_wide_x0[None, :])[0])
+_gate_rows_seen.clear()
+_gate_wide_grad = _grad_optmod._batch_fd_gradient(
+    _gate_wide_batch, (), _gate_wide_x0, _gate_wide_f0, 1e-4, _gate_wide_bounds,
+)
+_gate_wide_fused = _grad_optmod._batch_fd_gradient(
+    _gate_wide_batch, (), _gate_wide_x0, None, 1e-4, _gate_wide_bounds,
+)
+R.check(
+    "the batched jac simulates one row per free variable, none for a fixed one",
+    _gate_rows_seen == [2, 3],
+    f"batch heights {_gate_rows_seen} for 2 free of 6 variables: [2, 3] is "
+    f"the free rows alone, then the same behind x0; [6, 7] simulates the "
+    f"four fixed variables' copies of x0 as well",
+)
+R.check(
+    "that jac is the full batch's: scipy's estimate where free, 0.0 where fixed",
+    np.array_equal(_gate_wide_grad, _gate_wide_fused)
+    and np.array_equal(
+        _gate_wide_grad[[0, 4]],
+        np.array([
+            (float(_gate_wide_batch(
+                (_gate_wide_x0 + 1e-4 * np.eye(6)[i])[None, :])[0])
+             - _gate_wide_f0)
+            / ((_gate_wide_x0[i] + 1e-4) - _gate_wide_x0[i])
+            for i in (0, 4)
+        ]),
+    )
+    and not np.any(_gate_wide_grad[[1, 2, 3, 5]]),
+    f"gradient {_gate_wide_grad}, fused {_gate_wide_fused}",
+)
+_gate_rows_seen.clear()
+_gate_all_fixed = _grad_optmod._batch_fd_gradient(
+    _gate_wide_batch, (), _gate_wide_x0, _gate_wide_f0, 1e-4,
+    [(float(v), float(v)) for v in _gate_wide_x0],
+)
+R.check(
+    "with every variable fixed and f(x0) supplied, no batch is simulated",
+    _gate_rows_seen == [] and np.array_equal(_gate_all_fixed, np.zeros(6)),
+    f"batch heights {_gate_rows_seen}, gradient {_gate_all_fixed}",
+)
+
 from scipy.optimize._numdiff import approx_derivative as _gate_approx
 
 R.check(
@@ -7263,7 +7325,7 @@ def _check_batch_cost_948(label, cap):
     # objective_batch call on the 6-row matrix above.
     with _count_entries_948(
         (_PvOpt, "_comfort_terms"),
-        (_grad_optmod, "cycling_penalty"),
+        (_grad_optmod.runs, "start_count"),
         (_grad_optmod, "peak_cost_smooth"),
         (_PvModel, "simulate_trajectory"),
         (_PvModel, "simulate_trajectory_batch"),
@@ -7280,7 +7342,7 @@ def _check_batch_cost_948(label, cap):
     R.check(
         f"and without the per-row grid-term helpers: {label}",
         cyc == 0 and peak == 0,
-        f"cycling_penalty entered {cyc} times, peak_cost_smooth {peak} times "
+        f"runs.start_count entered {cyc} times, peak_cost_smooth {peak} times "
         f"(the solver's capacity term is the smooth surrogate since #1210; "
         f"the exact peak_cost is billed/published only and never batched)",
     )
@@ -7348,7 +7410,7 @@ _check_batch_cost_948(
 )
 
 # The batch twins under their own branch grids, one level below the
-# objective: every arm peak_cost and cycling_penalty branch on, priced per
+# objective: every arm peak_cost and the start count branch on, priced per
 # row against the scalar function on the same plan. Rule: row b of the
 # batch result must equal the scalar function on row b's plan, exactly,
 # for every (offset, window length, factors) arm -- separated peaks, the
@@ -7360,9 +7422,9 @@ _check_batch_cost_948(
 # it); the extra checks below pin that the two scalars agree everywhere
 # the plateau gate does not fire.
 from heatpump_optimizer.tariff import peak_cost_batch as _pcb948
-from heatpump_optimizer.optimizer import (
-    cycling_penalty as _cyc948,
-    cycling_penalty_batch as _cpb948,
+from heatpump_optimizer.runs import (
+    start_count as _cyc948,
+    start_count_batch as _cpb948,
 )
 
 _rows948 = np.vstack([
@@ -7427,11 +7489,13 @@ R.check(
 _cyc_bad948 = [
     _b948
     for _b948 in range(_rows948.shape[0])
-    if _cpb948(_rows948[_b948 : _b948 + 1], 2.0, 6.0)[0]
-    != _cyc948(_rows948[_b948], 2.0, 6.0)
+    for _run948 in (False, True)
+    if _cpb948(_rows948[_b948 : _b948 + 1], 2.0, _run948)[0]
+    != _cyc948(_rows948[_b948], 2.0, _run948)
 ]
 R.check(
-    "cycling_penalty_batch is cycling_penalty on every row, bit for bit",
+    "runs.start_count_batch is runs.start_count on every row, bit for bit, "
+    "from a stopped and from a running compressor",
     not _cyc_bad948,
     f"divergent rows: {_cyc_bad948}",
 )
@@ -69011,9 +69075,9 @@ import sys as _f22_sys  # noqa: E402
 
 from heatpump_optimizer import thermal_model as _f22_tm  # noqa: E402
 from heatpump_optimizer.dhw_planner import _DHW_MIN_RUN_CHUNK as _F22_CHUNK  # noqa: E402
-from heatpump_optimizer.optimizer import (  # noqa: E402
-    cycling_penalty as _f22_cyc,
-    cycling_penalty_batch as _f22_cyc_batch,
+from heatpump_optimizer.runs import (  # noqa: E402
+    start_count as _f22_cyc,
+    start_count_batch as _f22_cyc_batch,
 )
 
 
@@ -69064,14 +69128,14 @@ for _f22_two in (False, True):
 for _f22_rows in (2, 97):
     _f22_pm = np.random.default_rng(3).uniform(0.0, 6.0, size=(_f22_rows, 96))
     _f22_cost[("cycling", None, _f22_rows)] = _f22_calls(
-        _f22_cyc_batch, _f22_pm, 2.0, 6.0
+        _f22_cyc_batch, _f22_pm, 2.0, True
     )[0]
 _f22_growth = {
     k[:2]: (_f22_cost[k[:2] + (97,)], _f22_cost[k[:2] + (2,)])
     for k in _f22_cost if k[2] == 2
 }
 R.check(
-    "R9-F2.2 D9-s1-01/RC-sw1: the batched comfort terms and cycling penalty "
+    "R9-F2.2 D9-s1-01/RC-sw1: the batched comfort terms and start count "
     "make the same calls for 97 rows as for 2 (no per-row interpreter loop)",
     all(big == small for big, small in _f22_growth.values()),
     f"(97-row calls, 2-row calls) per twin: {_f22_growth}",
@@ -69110,35 +69174,18 @@ for _f22_two in (False, True):
         _f22_pm[0] = 3.0
         for _f22_order in ("C", "F"):
             _f22_pmo = np.asarray(_f22_pm, order=_f22_order)
-            _f22_got = _f22_cyc_batch(_f22_pmo, 2.0, 6.0)
-            for _f22_b in range(_f22_pmo.shape[0]):
-                if (np.float64(_f22_got[_f22_b]).tobytes()
-                        != np.float64(_f22_cyc(np.array(_f22_pmo[_f22_b]), 2.0, 6.0)).tobytes()):
-                    _f22_bad.append(("cycling", _f22_n, _f22_order, _f22_b))
-R.check(
-    "R9-F2.2: every batched comfort and cycling row is its scalar twin byte "
+            for _f22_run in (False, True):
+                _f22_got = _f22_cyc_batch(_f22_pmo, 2.0, _f22_run)
+                for _f22_b in range(_f22_pmo.shape[0]):
+                    if (np.float64(_f22_got[_f22_b]).tobytes()
+                            != np.float64(_f22_cyc(np.array(_f22_pmo[_f22_b]), 2.0, _f22_run)).tobytes()):
+                        _f22_bad.append(("starts", _f22_n, _f22_order, _f22_run, _f22_b))
+R.check(
+    "R9-F2.2: every batched comfort and start-count row is its scalar twin byte "
     "for byte, C- and Fortran-order, widths 1 to 192 including the production 96",
     not _f22_bad,
     f"first divergences: {_f22_bad[:4]}",
 )
-# The scalar twins' own value is unchanged by the fix: each is the sum numpy
-# gives a fresh 1-D array, which is what they returned before (null control
-# for the rows above agreeing only with each other).
-# Twenty-five schedules per width, because one reordered addition changes the
-# last bit of only some sums.
-_f22_ref_bad = []
-for _f22_n in (1, 5, 7, 8, 9, 95, 96, 97, 128, 129, 192):
-    for _f22_seed in range(25):
-        _f22_x = np.random.default_rng((_f22_n, _f22_seed)).uniform(0.0, 6.0, size=_f22_n)
-        _f22_want = 2.0 * float(np.sum(np.abs(np.diff(_f22_x)))) / (2.0 * 6.0) if _f22_n > 1 else 0.0
-        if np.float64(_f22_cyc(_f22_x, 2.0, 6.0)).tobytes() != np.float64(_f22_want).tobytes():
-            _f22_ref_bad.append((_f22_n, _f22_seed))
-R.check(
-    "R9-F2.2: the scalar cycling penalty is still numpy's own sum of the "
-    "swings, to the byte",
-    not _f22_ref_bad,
-    f"(width, seed) that moved: {_f22_ref_bad[:6]} of {len(_f22_ref_bad)}",
-)
 
 
 # D9-s1-02: with a batched objective served, L-BFGS-B takes f(x) from the same
@@ -70481,7 +70528,7 @@ R.check(
 # actuated house 17.2 K*h below the trajectory the plan was priced on. The plan
 # side now reads the plan's own running rule -- the floor the solve's bounds
 # already assume, a sub-floor step being duty cycling WITHIN the step, and the
-# floor count_compressor_starts already counts -- and the meter side keeps its
+# floor the plan's start count already counts -- and the meter side keeps its
 # threshold behind a name that says it reads a meter.
 #
 # This PR's P4 arm (D0-s2-02, #1664) widens no seed set and tightens no
@@ -70497,8 +70544,8 @@ from heatpump_optimizer.optimizer import (  # noqa: E402
     HeatPumpOptimizer as _f24_Opt,
     OptimizationConfig as _f24_Cfg,
     OptimizationResult as _f24_Res,
-    count_compressor_starts as _f24_starts,
 )
+from heatpump_optimizer.runs import edge_count as _f24_starts  # noqa: E402
 from heatpump_optimizer.thermal_model import (  # noqa: E402
     ThermalModel as _f24_Model,
     ThermalParameters as _f24_Params,
@@ -71017,8 +71064,8 @@ R.check(
 # simulations made while it runs, and every one must read zero. That reaches
 # a third such site the day one is written, where a check keyed on the two
 # fixed here would not. The census asserts its own preconditions -- one solve
-# that runs the continuation, the relaxed candidate and the multi-start's
-# own runs, each seen at least once -- so a solve that stopped reaching a
+# that runs the continuation, the committed candidates' re-solves and the
+# multi-start's own runs, each seen at least once -- so a solve that stopped reaching a
 # kind refuses instead of passing on an empty population. Positive control:
 # the same solve with ``_lbfgsb_run`` taking ``f`` from the scalar objective
 # reads nonzero, so the meter sees a scalar evaluation when one is made.
@@ -71080,9 +71127,17 @@ def _r10s_solve(run=None):
         lower_floor_temperature=21.0, slab_temperature=22.0,
         outdoor_temperature=float(out[0]),
     )
-    runs, live = [], []
+    runs, live, committing = [], [], []
     real_sm = _r10s_optmod._scoped_minimize
     real_traj = _r10s_Model.simulate_trajectory
+    real_commit = _r10s_optmod._commit_runs
+
+    def commit(*a, **k):
+        committing.append(True)
+        try:
+            return real_commit(*a, **k)
+        finally:
+            committing.pop()
 
     def traj(self, *a, **k):
         for rec in live:
@@ -71093,7 +71148,7 @@ def _r10s_solve(run=None):
         rec = {
             "jac": kw.get("jac") is not None, "scalar": 0,
             "kind": ("continuation" if opt._floor_l1_scale != 1.0
-                     else "relaxed" if opt._levels_relaxed else "multi-start"),
+                     else "committed" if committing else "multi-start"),
         }
         runs.append(rec)
         live.append(rec)
@@ -71103,6 +71158,7 @@ def _r10s_solve(run=None):
             live.remove(rec)
 
     with _r10s_mock.patch.object(_r10s_optmod, "_scoped_minimize", sm), \
+            _r10s_mock.patch.object(_r10s_optmod, "_commit_runs", commit), \
             _r10s_mock.patch.object(_r10s_Model, "simulate_trajectory", traj), \
             (_r10s_mock.patch.object(_r10s_optmod, "_lbfgsb_run", run, create=True)
              if run is not None else _r10s_ctx.nullcontext()):
@@ -71133,10 +71189,10 @@ _r10s_ref = _r10s_census(_r10s_ref_runs)
 print(f"RESULT r10_solver_runs fused={_r10s_got} scalar_valued={_r10s_ref}")
 R.check(
     "R10-SOLVER D9-s1-01 (census precondition): the metered solve runs the "
-    "continuation, the relaxed candidate and the multi-start's own runs on "
-    "the batched jac",
+    "continuation, the committed candidates' re-solves and the multi-start's "
+    "own runs on the batched jac",
     all(_r10s_got.get(k, (0, 0))[0] > 0
-        for k in ("continuation", "relaxed", "multi-start")),
+        for k in ("continuation", "committed", "multi-start")),
     f"(supplied-jac runs, scalar simulations) per kind: {_r10s_got}",
 )
 R.check(
@@ -71149,7 +71205,7 @@ R.check(
     "R10-SOLVER D9-s1-01 (positive control): the scalar-valued form of the "
     "same runs is seen by the meter",
     _r10s_ref.get("continuation", (0, 0))[1] > 0
-    and _r10s_ref.get("relaxed", (0, 0))[1] > 0,
+    and _r10s_ref.get("committed", (0, 0))[1] > 0,
     f"(supplied-jac runs, scalar simulations) per kind: {_r10s_ref}",
 )
 R.check(
@@ -74538,7 +74594,7 @@ R.check(
 
 # The objective scores the rounded levels a clamped install ships, so it is
 # flat between 0 and p_min and a start descending into that band stalls
-# there. The relaxed candidate (``_relaxed_starts``) is the fix; the
+# there. Descending on the relaxed objective (``_descent_pair``) is the fix; the
 # control arm is the same solve with it removed, which is the mutant. A
 # synthetic 750 L tank with no valve, space-only and with hot water, so both
 # solve paths carry the tank's state without the store credit. The valve was
@@ -74559,6 +74615,8 @@ R.check(
 # basin. In the hot-water cells space ships projected against the DHW plan
 # (#3289, ``project_space_against``): before that, two cells shipped space
 # plus DHW above their 5.5 kW p_max; the checks' predicates hold either way.
+from types import SimpleNamespace as _SpNS  # noqa: E402
+
 import heatpump_optimizer.optimizer as _sp_opt_mod  # noqa: E402
 from heatpump_optimizer.optimizer import (  # noqa: E402
     HeatPumpOptimizer as _SpOpt,
@@ -74583,13 +74641,16 @@ def _sp_solve(prices, dhw, loss, relaxed=True, out_mean=2.0):
     params.min_electrical_power, params.max_electrical_power = 1.5, 5.5
     params.dhw_enabled, params.house_heat_loss_scale = dhw, loss
     opt = _SpOpt(_SpTM(params), _SpCfg(clamp_planned_levels=True))
-    kept = _sp_opt_mod._relaxed_starts
+    # The control arm removes the relaxed descent: the multi-start returns its
+    # first start as it stands, and the candidate stage commits that.
+    kept = _sp_opt_mod._multi_start_minimize
     if not relaxed:
-        _sp_opt_mod._relaxed_starts = lambda _opt, *a: a[-2]
+        _sp_opt_mod._multi_start_minimize = lambda _objective, starts, _bounds, **_kw: _SpNS(
+            x=np.asarray(starts[0], float), success=True)
     try:
         result = _sp_run(opt, prices, out_mean)
     finally:
-        _sp_opt_mod._relaxed_starts = kept
+        _sp_opt_mod._multi_start_minimize = kept
     return np.asarray(result.power_schedule, float), float(result.objective_value)
 
 
@@ -74656,45 +74717,31 @@ R.check(
     f"{({k: (round(f[1], 3), round(c[1], 3)) for k, (f, c) in _sp_flat.items()})}",
 )
 
-# The two helpers at the edges the solves above do not reach: an install that
-# can duty-cycle, a start index past the last (the warm pass), and the flag the
-# relaxed run scores under. A quadratic stands in for the objective.
-_sp_clamped = _SpOpt(_SpTM(_SpTP()), _SpCfg(clamp_planned_levels=True))
-_sp_free = _SpOpt(_SpTM(_SpTP()), _SpCfg(clamp_planned_levels=False))
-_sp_rounded_seen = []
-
-
-def _sp_quad(x, *_args):
-    _sp_rounded_seen.append(_sp_opt_mod._scores_rounded(_sp_clamped))
-    return float(np.sum((np.asarray(x, float) - 1.0) ** 2))
+# Which pair a solve descends on: the relaxed one where it plans runs (a start
+# has a price, or the install cannot duty-cycle), else the objects handed in.
+# A recorder stands in for the objective and reports the keyword it was given.
+def _sp_seen(*_args, descent=None):
+    return descent
 
 
-def _sp_quad_batch(rows, *_args):
-    return np.array([_sp_quad(row) for row in np.atleast_2d(rows)])
-
-
-_SP_BOUNDS = [(0.0, 2.0)] * 3
-_sp_moved = _sp_opt_mod._relaxed_starts(
-    _sp_clamped, _sp_quad, _sp_quad_batch, _SP_BOUNDS, 0, (), [np.zeros(3)], 50,
-)
-R.check(
-    "a clamped install gains one candidate, refined while the objective scores the "
-    "duty-cycle reading, and rounds again after",
-    len(_sp_moved) == 2 and np.allclose(_sp_moved[1], 1.0, atol=1e-3)
-    and _sp_rounded_seen and not any(_sp_rounded_seen)
-    and _sp_opt_mod._scores_rounded(_sp_clamped) is True,
-    f"{len(_sp_moved)} {_sp_moved[-1]} seen {set(_sp_rounded_seen)}",
-)
+_sp_pairs = {
+    (cost, clamp): _sp_opt_mod._descent_pair(
+        _SpOpt(_SpTM(_SpTP()), _SpCfg(clamp_planned_levels=clamp, cycling_cost=cost)),
+        _sp_seen, _sp_seen)
+    for cost in (0.0, 0.25) for clamp in (False, True)
+}
 R.check(
-    "an install that can duty-cycle gains none and never scores rounded; a start past "
-    "the last (the warm pass) adds none",
-    len(_sp_opt_mod._relaxed_starts(
-        _sp_free, _sp_quad, _sp_quad_batch, _SP_BOUNDS, 0, (), [np.zeros(3)], 50,
-    )) == 1
-    and _sp_opt_mod._scores_rounded(_sp_free) is False
-    and len(_sp_opt_mod._relaxed_starts(
-        _sp_clamped, _sp_quad, _sp_quad_batch, _SP_BOUNDS, 1, (), [np.zeros(3)], 50,
-    )) == 1,
+    "a solve descends on the relaxed pair where a start has a price or the install "
+    "cannot duty-cycle, each alone and both; with neither it descends on the objects "
+    "it was handed",
+    [(k, pair[0](None), pair[1](None)) for k, pair in sorted(_sp_pairs.items())]
+    == [((0.0, False), None, None), ((0.0, True), "relaxed", "relaxed"),
+        ((0.25, False), "relaxed", "relaxed"), ((0.25, True), "relaxed", "relaxed")]
+    and _sp_pairs[(0.0, False)] == (_sp_seen, _sp_seen)
+    and _sp_opt_mod._descent_pair(
+        _SpOpt(_SpTM(_SpTP()), _SpCfg(cycling_cost=0.25)), _sp_seen, _sp_seen, _sp_opt_mod._UNPRICED,
+    )[0](None) == "unpriced",
+    f"{({k: (pair[0](None), pair[1](None)) for k, pair in _sp_pairs.items()})}",
 )
 
 R.section("#1913 SW-4 — GCHV Modbus silent transport via night-mode 518/519")
@@ -86725,7 +86772,8 @@ R.check(
 )
 # Only the arbiter (which reports and reads the split), the sensor (which
 # publishes) and the coordinator (whose factory reset voids the store, and which
-# hands the planner's read to a solve's configuration, R10-DUTY-SWITCH-PLANNER-PRICE)
+# hands the planner's read to a solve's configuration, R10-DUTY-SWITCH-PLANNER-PRICE,
+# and the settled running class to a solve's inputs, R11-OUTSIDE-HONEST-STARTS-RUNS)
 # name the module; arbiter and planner read the estimate through one leg rule.
 _ds_pkg = _DsPath("custom_components/heatpump_optimizer")
 _ds_readers = sorted(
@@ -86747,12 +86795,13 @@ _ds_rs_own = {n.module for n in _ds_ast.walk(_ds_ast.parse((_ds_pkg / "running_s
 R.check(
     "only the arbiter, the sensor and the coordinator name duty_switch, through its report, attach, publish and "
     "store calls, and the estimate is read only by the arbiter's split and, once in the coordinator, the planner's "
-    "read; the module imports none of them, and the running signal it hears imports none of them nor it; the pure "
-    "half of wear stays pure",
+    "read, beside the running class a solve starts from; the module imports none of them, and the running "
+    "signal it hears imports none of them nor it; the pure half of wear stays pure",
     _ds_readers == ["coordinator.py", "pump_arbiter.py", "sensor.py"]
-    and _ds_plan_uses == ["planner_fields", "record_for"]
+    and sorted(set(_ds_plan_uses)) == ["planner_fields", "record_for", "running_now"]
     and _ds_uses == ["STOP_WINDOW_S", "SwitchContext", "attach", "both_step_duty", "detach",
-                     "note_mode_write", "note_pass", "planner_fields", "record_for", "starts_attributes"]
+                     "note_mode_write", "note_pass", "planner_fields", "record_for", "running_now",
+                     "starts_attributes"]
     and not _ds_own & {"pump_arbiter", "sensor", "coordinator"}
     and not _ds_rs_own & {"duty_switch", "pump_arbiter", "sensor", "coordinator"}
     and "homeassistant" not in (_ds_pkg / "wear.py").read_text(),
@@ -90830,8 +90879,6 @@ from heatpump_optimizer.dhw_planner import DhwPlanner as _DspPlanner  # noqa: E4
 from heatpump_optimizer.optimizer import (  # noqa: E402
     HeatPumpOptimizer as _DspOpt,
     OptimizationConfig as _DspCfg,
-    count_compressor_starts as _dsp_starts,
-    cycling_penalty as _dsp_cyc,
 )
 from heatpump_optimizer.thermal_model import (  # noqa: E402
     ThermalModel as _DspTM,
@@ -90844,6 +90891,8 @@ _DSP_STEPS = np.arange(96)
 _DSP_PRICES = 1.3 + 0.9 * np.sin(2 * np.pi * (_DSP_STEPS - 30) / 96.0)
 #: Bankaifan's table: every hot water to heating switch stopped the compressor,
 #: none the other way, median off time 501 s (8.2 and 8.5 minutes).
+from heatpump_optimizer import runs as _dsp_runs  # noqa: E402
+
 _DSP_PAIR, _DSP_OFF = (1.0, 0.0), (501.0, 0.0)
 
 
@@ -90853,14 +90902,16 @@ def _dsp_w(space, dhw, pair, floor=None, p_max=6.0):
     )
 
 
-# 1. The finding. Equal draw on both sides of the switch: the cycling term
-# sees no swing; the switch weight is p x draw / p_max.
+# 1. The finding. Equal draw on both sides of the switch: the boundary is
+# inside a run, so its start share is nothing (the one start of the pair is
+# step 0's, from a stopped pump); the switch weight is p x draw / p_max.
 R.check(
-    "a hot-water step into a heating step at equal draw costs the cycling term "
-    "nothing and weighs p x draw / p_max as a switch",
-    _dsp_cyc(np.array([3.0, 3.0]), 2.0, 6.0) == 0.0
+    "a hot-water step into a heating step at equal draw costs the start term "
+    "nothing at the boundary and weighs p x draw / p_max as a switch",
+    _dsp_runs.start_count(np.array([3.0, 3.0]), 2.0, True) == 0.0
+    and _dsp_runs.start_count(np.array([3.0, 3.0]), 2.0) == 1.0
     and _dsp_w([0, 3], [3, 0], (0.8, 0.0)) == 0.8 * 3.0 / 6.0,
-    f"{_dsp_cyc(np.array([3.0, 3.0]), 2.0, 6.0)}, {_dsp_w([0, 3], [3, 0], (0.8, 0.0))}",
+    f"{_dsp_runs.start_count(np.array([3.0, 3.0]), 2.0, True)}, {_dsp_w([0, 3], [3, 0], (0.8, 0.0))}",
 )
 R.check(
     "the stop adds the smaller of the two levels across a boundary",
@@ -90912,13 +90963,23 @@ def _dsp_opt(pair=(0.0, 0.0), off=(0.0, 0.0), *, clamp=False, p_min=1.5, p_max=5
 _dsp_term_opt = _dsp_opt((0.8, 0.0), cyc=2.0, p_max=6.0)
 _dsp_term = _dsp_om._switch_cost_fn(_dsp_term_opt)
 _dsp_term_pair = (np.array([0.0, 3.0]), np.array([3.0, 0.0]))
-R.check(
-    "the objective's term is cycling_cost x that weight, a float for one plan "
-    "and one entry per row for a batch",
-    _dsp_term(*_dsp_term_pair) == 2.0 * (0.8 * 3.0 / 6.0)
+# Restated in R11-OUTSIDE-HONEST-STARTS-RUNS: the weight above is what the
+# relaxed descent prices (cycles of the combined draw); the true objective
+# weighs the same pair at p_max x the running share, in starts, so a switch
+# between two steps that both run is the probability of one start whatever
+# their level. Until then both read 2.0 x (0.8 x 3.0 / 6.0).
+R.check(
+    "the relaxed descent's term is cycling_cost x that weight and the true "
+    "objective's cycling_cost x the probability of one start, a float for one "
+    "plan and one entry per row for a batch; the unpriced descent has none",
+    _dsp_term(*_dsp_term_pair, _dsp_om._RELAXED) == 2.0 * (0.8 * 3.0 / 6.0)
+    and _dsp_term(np.stack([_dsp_term_pair[0]] * 2), _dsp_term_pair[1], _dsp_om._RELAXED).tolist()
+    == [2.0 * (0.8 * 3.0 / 6.0)] * 2
+    and abs(_dsp_term(*_dsp_term_pair) - 2.0 * 0.8) < 1e-12
     and _dsp_term(np.stack([_dsp_term_pair[0]] * 2), _dsp_term_pair[1]).tolist()
-    == [2.0 * (0.8 * 3.0 / 6.0)] * 2,
-    f"{_dsp_term(*_dsp_term_pair)}",
+    == [_dsp_term(*_dsp_term_pair)] * 2
+    and _dsp_term(*_dsp_term_pair, _dsp_om._UNPRICED) is None,
+    f"{_dsp_term(*_dsp_term_pair, _dsp_om._RELAXED)} {_dsp_term(*_dsp_term_pair)}",
 )
 R.check(
     "and it is no operand at all with a zero pair, a zero cycling cost or no "
@@ -91287,15 +91348,15 @@ R.check(
 )
 
 
-def _dsp_solve(pair=(0.0, 0.0), off=(0.0, 0.0), *, pins=None, legionella_h=20.0, **install):
+def _dsp_solve(pair=(0.0, 0.0), off=(0.0, 0.0), *, pins=None, legionella_h=20.0, out_mean=2.0, **install):
     """One full ``optimize``; the planner builds, the published simulation's
     inputs and the objective closures are recorded beside the result."""
     opt = _dsp_opt(pair, off, **install)
     seen = _DspNS(
         builds=[], sims=[], objectives=[], solves=[], solved=[], min_runs=[],
-        energy=[None], vectors=[0], opt=opt,
+        energy=[None], vectors=[0], vectors_outside=[0], solving=[0], stages=[], opt=opt,
     )
-    real_build = _DspPlanner._build_dhw_requirements
+    real_build, real_stage = _DspPlanner._build_dhw_requirements, _dsp_om._commit_runs
     real_sim, real_objectives = opt.model.simulate_trajectory_with_dhw, opt._solve_objectives
     real_solve, real_min_run = opt._solve_space, _DspPlanner._apply_dhw_min_run
 
@@ -91303,7 +91364,11 @@ def _dsp_solve(pair=(0.0, 0.0), off=(0.0, 0.0), *, pins=None, legionella_h=20.0,
 
     def solve_space(*args):
         seen.solves.append(args)
-        seen.solved.append(real_solve(*args))
+        seen.solving[0] += 1
+        try:
+            seen.solved.append(real_solve(*args))
+        finally:
+            seen.solving[0] -= 1
         return seen.solved[-1]
 
     def energy_cost_fn(*args):
@@ -91316,6 +91381,7 @@ def _dsp_solve(pair=(0.0, 0.0), off=(0.0, 0.0), *, pins=None, legionella_h=20.0,
 
     def vector(*args):
         seen.vectors[0] += 1
+        seen.vectors_outside[0] += not seen.solving[0]
         return real_vector(*args)
 
     def min_run(self, **kwargs):
@@ -91337,12 +91403,16 @@ def _dsp_solve(pair=(0.0, 0.0), off=(0.0, 0.0), *, pins=None, legionella_h=20.0,
         seen.objectives.append(out)
         return out
 
+    def stage(*args):
+        seen.stages.append((args, real_stage(*args)))
+        return seen.stages[-1][1]
+
     opt.model.simulate_trajectory_with_dhw, opt._solve_objectives = sim, objectives
     opt._solve_space, opt._energy_cost_fn = solve_space, energy_cost_fn
-    _dsp_om._stop_availability = vector
+    _dsp_om._stop_availability, _dsp_om._commit_runs = vector, stage
     _DspPlanner._build_dhw_requirements = build
     _DspPlanner._apply_dhw_min_run = min_run
-    outdoor = 2.0 + 3.0 * np.sin(2 * np.pi * (_DSP_STEPS - 50) / 96.0)
+    outdoor = out_mean + 3.0 * np.sin(2 * np.pi * (_DSP_STEPS - 50) / 96.0)
     try:
         seen.result = opt.optimize(inputs=solve_inputs(
             initial_state=_DspTS(
@@ -91358,7 +91428,7 @@ def _dsp_solve(pair=(0.0, 0.0), off=(0.0, 0.0), *, pins=None, legionella_h=20.0,
     finally:
         _DspPlanner._build_dhw_requirements = real_build
         _DspPlanner._apply_dhw_min_run = real_min_run
-        _dsp_om._stop_availability = real_vector
+        _dsp_om._stop_availability, _dsp_om._commit_runs = real_vector, real_stage
     seen.space = np.asarray(seen.result.power_schedule, float)
     seen.dhw = np.asarray(seen.result.dhw_power_schedule, float)
     seen.bans = [k["placement_ban"] for k, *_ in seen.builds if "placement_ban" in k]
@@ -91375,8 +91445,13 @@ def _dsp_same_plan(a, b):
     )
 
 
+# The duty-cycle install's day is 2 K colder since R11-OUTSIDE-HONEST-STARTS-RUNS:
+# with a start priced as a start that install plans runs, and on the 2 degC day
+# the plan it ships makes no priced switch at all (the mild day of the two
+# descents below), so the checks of a charged step and of the banned candidate
+# had nothing to read there.
 _DSP_INSTALLS = {
-    "duty-cycle": dict(clamp=False),
+    "duty-cycle": dict(clamp=False, out_mean=0.0),
     "modulating clamped": dict(clamp=True),
     "fixed-speed": dict(clamp=True, p_min=5.5),
 }
@@ -91423,18 +91498,31 @@ R.check(
 
 
 # 5. Acceptance, on the contributor's table.
-def _dsp_plan_weight(seen, name):
+def _dsp_plan_weight(seen, name, starts=False):
+    """A plan's summed switch weight: at the combined draw, as the relaxed
+    descent prices it, or in starts, as the true objective does."""
     kw = {"clamp": False, "p_min": 1.5, **_DSP_INSTALLS[name]}
     return _dsp_dl.switch_weight(
-        seen.space, seen.dhw, _DSP_PAIR, 5.5, kw["p_min"] if kw["clamp"] else None
+        seen.space, seen.dhw, _DSP_PAIR, 5.5, kw["p_min"] if kw["clamp"] else None,
+        level=5.5 * _dsp_runs.running_share(seen.space + seen.dhw, kw["p_min"]) if starts else None,
     )
 
 
 def _dsp_old_under_new(name):
-    """The unpriced plan's score under the priced solve's own objective."""
+    """The unpriced plan's score under the priced solve's own objective, held
+    to the bound the stops it makes leave it.
+
+    Restated in R11-OUTSIDE-HONEST-STARTS-RUNS: on a duty-cycle install the
+    bound, not the objective, carries a stop's lost running time
+    (``duty_legs.space_headroom``), so the plan as solved without the pair
+    was scored with heat its own stop does not let it deliver (3.36 kW in a
+    step the stop leaves 2.44 kW). On a clamped install the bound is
+    ``p_max - dhw`` and the clip moves nothing.
+    """
     old, new = _dsp_base[name], _dsp_priced[name]
     avail = _dsp_om._stop_availability(new.opt, old.space, old.dhw, 5.5)
-    return float(new.objectives[-1][1](old.space, old.dhw, None, avail))
+    bound = _dsp_dl.space_headroom(5.5, old.dhw, avail, _dsp_om._duty_floor(new.opt))
+    return float(new.objectives[-1][1](np.minimum(old.space, bound), old.dhw, None, avail))
 
 
 _dsp_accept = {
@@ -91444,11 +91532,79 @@ _dsp_accept = {
     )
     for name in ("duty-cycle", "modulating clamped")
 }
+# Restated in R11-OUTSIDE-HONEST-STARTS-RUNS. The true objective weighs a
+# switch in starts, the probability of one start whatever the level, so a
+# priced solve no longer buys a lower weight by lowering the level at a
+# switch it keeps. On the duty-cycle install it still carries no more
+# switches in the objective's own unit, and its weight at the combined draw,
+# which its relaxed descent prices, still falls.
+#
+# On the clamped install no order of the two plans' weights is asked
+# (``tests/README.md``, "A knife-edge optimizer comparison must be measured
+# across BLAS kernels"). That order raced two independent multi-start
+# descents, and nothing in the stage holds it: under one of four OpenBLAS
+# kernels the unpriced solve lands on a one-switch plan and the priced solve
+# on a two-switch plan the priced objective scores lower, the switches' price
+# included. What the stage does hold is asked in its place, inside the priced
+# solve alone, where the basin both sides start from is the same: each
+# candidate stage returns a plan that scores, in the scope it ships in, no
+# higher than the projection of the relaxed plan the stage was handed, scored
+# as the stage scores it (in the scope of a solve started from it, held to
+# that scope's bound), so a switch the priced plan keeps is one its own
+# objective was charged for; and the plan that publishes is one a stage
+# returned, at that score.
+_dsp_accept_starts = {
+    name: (_dsp_plan_weight(_dsp_base[name], name, True), _dsp_plan_weight(_dsp_priced[name], name, True))
+    for name in _dsp_accept
+}
+
+
+def _dsp_stage_scores(seen):
+    """Per candidate-stage call of one solve: the score of the plan the stage
+    returned in the scope it returned, the score of the first relaxed plan's
+    projection in the scope of a solve started from it, and whether the
+    returned plan is the one that ships."""
+    out, kept = [], seen.opt._space_avail
+    try:
+        for (opt, _h, scope, relaxed, dhw, _maxiter, *rest), (plan, shipped) in seen.stages:
+            args = () if dhw is None else (dhw,)
+            _, hi, _, cycled = _dsp_om._stage_box(opt, scope[0], dhw)
+            first = _dsp_om._projection(opt, relaxed[0], dhw, hi, cycled)
+            own = rest[0](first) if rest and rest[0] is not None else scope
+            first = np.clip(first, *_dsp_om._stage_box(opt, own[0], dhw)[:2])
+            out.append((
+                float(shipped[1](plan, *args)), float(own[1](first, *args)),
+                bool(np.array_equal(plan, seen.space)),
+            ))
+    finally:
+        seen.opt._space_avail = kept
+    return out
+
+
+_dsp_stage = {name: _dsp_stage_scores(_dsp_priced[name]) for name in _dsp_accept}
 R.check(
-    "acceptance: priced on the contributor's table the plan carries a lower "
-    "summed switch weight, on a duty-cycle and on a modulating clamped install",
-    all(new_w < old_w and old_w > 0 for old_w, new_w, _, _ in _dsp_accept.values()),
-    f"{_dsp_accept}",
+    "acceptance: priced on the contributor's table the duty-cycle plan carries "
+    "no higher a switch weight in starts and a lower one at the combined draw, "
+    "and the unpriced plan of both installs carries a switch to price",
+    all(old_w > 0 for old_w, _ in _dsp_accept_starts.values())
+    and _dsp_accept_starts["duty-cycle"][1] <= _dsp_accept_starts["duty-cycle"][0] + 1e-9
+    and _dsp_accept["duty-cycle"][1] < _dsp_accept["duty-cycle"][0],
+    f"{_dsp_accept} {_dsp_accept_starts}",
+)
+R.check(
+    "acceptance: on both installs every candidate stage of the priced solve "
+    "returns a plan that scores no higher under the priced objective of the "
+    "scope it ships in than the projection of the relaxed plan it was handed, "
+    "and strictly lower in at least one call; the plan that publishes is one a "
+    "stage returned, at that score",
+    all(
+        calls and all(got <= first + 1e-9 for got, first, _ in calls)
+        and any(got < first - 0.01 for got, first, _ in calls)
+        and [got for got, _, ships in calls if ships]
+        == [float(_dsp_priced[name].result.objective_value)]
+        for name, calls in _dsp_stage.items()
+    ),
+    f"{_dsp_stage} {({n: float(_dsp_priced[n].result.objective_value) for n in _dsp_stage})}",
 )
 R.check(
     "at no higher cost under the plan's own objective: the new plan scores no "
@@ -91533,11 +91689,11 @@ R.check(
     f"fed {_dsp_fx_fed[_dsp_fx_charged]}, live {_dsp_fx_live}",
 )
 R.check(
-    "fixed-speed: the published start count is count_compressor_starts on the "
+    "fixed-speed: the published start count is runs.edge_count on the "
     "shipped total, unchanged by the pairs on the same arrays",
-    _dsp_fx.result.compressor_starts == _dsp_starts(_dsp_fx_total)
+    _dsp_fx.result.compressor_starts == _dsp_runs.edge_count(_dsp_fx_total)
     and _dsp_base["fixed-speed"].result.compressor_starts
-    == _dsp_starts(_dsp_fx0.space + _dsp_fx0.dhw),
+    == _dsp_runs.edge_count(_dsp_fx0.space + _dsp_fx0.dhw),
     f"{_dsp_fx.result.compressor_starts}",
 )
 R.check(
@@ -91846,6 +92002,7 @@ R.check(
 # steps either side of each, and one at the running threshold.
 _dsp_e = _dsp_solve(_DSP_PAIR, (0.0, 0.0))
 _dsp_e0 = _dsp_solve((0.0, 0.0), (501.0, 0.0))
+_dsp_e_plain = _dsp_solve(None)  # the same day as the two above, not the install table's
 _dsp_e_tank = np.zeros(96)
 _dsp_e_tank[[40, 41]] = 1.5
 _DSP_EPS = 2.0 * _dsp_om._LBFGSB_FD_EPS
@@ -91873,7 +92030,7 @@ def _dsp_e_solve(seen, start):
 
 
 _dsp_e_runs = {
-    label: (_dsp_e_solve(_dsp_e, start), _dsp_e_solve(_dsp_e0, start), _dsp_e_solve(_dsp_base["duty-cycle"], start))
+    label: (_dsp_e_solve(_dsp_e, start), _dsp_e_solve(_dsp_e0, start), _dsp_e_solve(_dsp_e_plain, start))
     for label, start in _DSP_E_STARTS.items()
 }
 R.check(
@@ -91905,23 +92062,27 @@ R.check(
     ),
 )
 
-# Item r14: a relaxed start of a clamped install scores unrounded levels; the
-# delivered draw gives it the clamped reading on that unrounded level.
+# Item r14, restated in R11-OUTSIDE-HONEST-STARTS-RUNS: no objective rounds
+# the space level any more (what the true objective scores is a committed
+# plan), so a descent and the true objective both charge the vector on the
+# level as it stands, with the clamped reading. What still differs is the
+# tank: the true objective scores hot water as a clamped install ships it,
+# projected, and a descent leaves it as planned. Until then the true
+# objective rounded 0.7 kW of space to 1.5 and a relaxed start did not.
 _dsp_rx_opt = _dsp_opt(_DSP_PAIR, _DSP_OFF, clamp=True)
-_dsp_rx_args = (np.array([0.7, 3.0]), np.array([0.0, 0.0]), np.array([0.5, 0.5]))
+_dsp_rx_args = (np.array([0.7, 3.0]), np.array([0.7, 0.0]), np.array([0.5, 0.5]))
 _dsp_rx_rounded = _dsp_om._shipped_and_received(_dsp_rx_opt, *_dsp_rx_args)
-_dsp_rx_opt._levels_relaxed = True
-try:
-    _dsp_rx_relaxed = _dsp_om._shipped_and_received(_dsp_rx_opt, *_dsp_rx_args)
-finally:
-    _dsp_rx_opt._levels_relaxed = False
-R.check(
-    "a relaxed start carrying a vector is charged on its unrounded level, the "
-    "rounded objective on the level that ships",
-    _dsp_rx_relaxed[0].tolist() == [0.7, 3.0] and _dsp_rx_relaxed[2].tolist() == [0.35, 1.5]
-    and _dsp_rx_rounded[0].tolist() != [0.7, 3.0]
-    and _dsp_rx_rounded[2].tolist() == (_dsp_rx_rounded[0] * 0.5).tolist(),
-    f"{_dsp_rx_relaxed[2]}, {_dsp_rx_rounded[0]}, {_dsp_rx_rounded[2]}",
+_dsp_rx_relaxed = _dsp_om._shipped_and_received(_dsp_rx_opt, *_dsp_rx_args, _dsp_om._RELAXED)
+R.check(
+    "a descent and the true objective both charge a vector on the space level "
+    "as it stands; the true objective reads the tank as it ships, projected, "
+    "and a descent as planned",
+    _dsp_rx_relaxed[0].tolist() == _dsp_rx_rounded[0].tolist() == [0.7, 3.0]
+    and _dsp_rx_relaxed[1].tolist() == [0.7, 0.0] and _dsp_rx_rounded[1].tolist() == [1.5, 0.0]
+    and _dsp_rx_relaxed[2].tolist() == [0.0, 1.5] and _dsp_rx_rounded[2].tolist() == [0.0, 1.5]
+    and _dsp_om._shipped_and_received(_dsp_rx_opt, _dsp_rx_args[0], np.zeros(2), _dsp_rx_args[2])[2].tolist()
+    == [0.35, 1.5],
+    f"{_dsp_rx_relaxed}, {_dsp_rx_rounded}",
 )
 _dsp_rx_plain = _dsp_om._shipped_and_received(_dsp_rx_opt, *_dsp_rx_args[:2], None)
 R.check(
@@ -91952,29 +92113,32 @@ _dsp_mc_live = (
     else [i for i in np.flatnonzero(_dsp_mc_avail < 1.0).tolist() if _dsp_mc.space[i] > 0]
 )
 _dsp_mc_obj, _dsp_mc_batch, _dsp_mc_energy = (_dsp_mc.objectives[-1][i] for i in (1, 2, 3))
-_dsp_mc_rebuilt = (
-    None if _dsp_mc_avail is None
-    else _dsp_om._stop_availability(_dsp_mc.opt, _dsp_mc.space, _dsp_mc.dhw, 5.5)
-)
+# Restated in R11-OUTSIDE-HONEST-STARTS-RUNS, whose approved design builds the
+# vector from the profile a committed candidate's re-solve starts from: a
+# candidate makes its own switches, and the lost running time of a switch
+# belongs to the plan that makes it. So a space solve builds one vector for its
+# start and one per candidate it scores, and the plan that ships carries the
+# one it was scored with. Until then: one per space solve, built from the
+# solve's start, "not the vector the final plan would rebuild". Kept: the
+# simulation is fed through the adopted vector, and none is built at
+# publication.
 R.check(
     "modulating clamped: the simulation is fed the delivered draw of the "
-    "vector the adopted solve scored with, which is not the vector the final "
-    "plan would rebuild",
+    "vector the adopted plan was scored with, whose charged steps hold "
+    "heating in that plan",
     bool(_dsp_mc_live)
     and np.array_equal(
         _dsp_mc_fed, _dsp_dl.delivered_space(_dsp_mc.space, _dsp_mc.dhw, _dsp_mc_avail, 1.5)
     )
-    and not np.array_equal(_dsp_mc_fed, _dsp_mc.space)
-    and (_dsp_mc_rebuilt is None or not np.array_equal(
-        _dsp_mc_fed, _dsp_dl.delivered_space(_dsp_mc.space, _dsp_mc.dhw, _dsp_mc_rebuilt, 1.5)
-    )),
+    and not np.array_equal(_dsp_mc_fed, _dsp_mc.space),
     f"live {_dsp_mc_live}",
 )
 R.check(
-    "the vector is built once per space solve and never at publication, on "
-    "every priced solve above",
-    all(s.vectors[0] == len(s.solves) for s in [*_dsp_priced.values(), _dsp_mc]),
-    f"{[(s.vectors[0], len(s.solves)) for s in [*_dsp_priced.values(), _dsp_mc]]}",
+    "a vector is built inside a space solve, at least one per solve, and never "
+    "at publication, on every priced solve above",
+    all(s.vectors[0] >= len(s.solves) > 0 and s.vectors_outside[0] == 0
+        for s in [*_dsp_priced.values(), _dsp_mc]),
+    f"{[(s.vectors[0], s.vectors_outside[0], len(s.solves)) for s in [*_dsp_priced.values(), _dsp_mc]]}",
 )
 R.check(
     "modulating clamped (item r15): the achieved objective is the closure on "
@@ -92013,15 +92177,17 @@ _dsp_fx_free = _dsp_solve(_DSP_PAIR, _DSP_OFF, clamp=True, p_min=5.5, cyc=0.0)
 _dsp_fx_obj, _dsp_fx_batch = _dsp_fx.objectives[-1][1], _dsp_fx.objectives[-1][2]
 _dsp_fx_score = float(_dsp_fx_obj(_dsp_fx.space, _dsp_fx.dhw, None, _dsp_fx_avail))
 _dsp_fx_level_terms = _dsp_fx.opt.config.price_weight * (
-    _dsp_cyc(_dsp_fx_total, 0.3, 5.5)
-    + 0.3 * _dsp_dl.switch_weight(_dsp_fx.space, _dsp_fx.dhw, _DSP_PAIR, 5.5, 5.5)
+    0.3 * _dsp_runs.start_count(_dsp_fx_total, 5.5)
+    + 0.3 * _dsp_dl.switch_weight(
+        _dsp_fx.space, _dsp_fx.dhw, _DSP_PAIR, 5.5, 5.5,
+        level=5.5 * _dsp_runs.running_share(_dsp_fx_total, 5.5))
 )
 _dsp_fx_unpriced = float(
     _dsp_fx_free.objectives[-1][1](_dsp_fx.space, _dsp_fx.dhw, None, _dsp_fx_avail)
 )
 R.check(
-    "fixed-speed: what pricing a cycle adds to a plan's score is the cycling "
-    "term plus cycling_cost x the switch weight of the shipped levels",
+    "fixed-speed: what pricing a start adds to a plan's score is cycling_cost x "
+    "(the start count plus the switch weight at p_max x the running share)",
     _dsp_dl.switch_weight(_dsp_fx.space, _dsp_fx.dhw, _DSP_PAIR, 5.5, 5.5) > 0
     and abs(_dsp_fx_score - _dsp_fx_unpriced - _dsp_fx_level_terms) < 1e-9,
     f"{_dsp_fx_score - _dsp_fx_unpriced} vs {_dsp_fx_level_terms}",
@@ -92052,9 +92218,13 @@ def _dsp_co_solve(dhw_plan, warm_start):
 
 
 _dsp_co_kept = _dsp_co.opt._space_avail = np.ones(96)
+# The incumbent handed in asks for the whole compressor in every step, so the
+# re-plan differs from the first hot-water plan whatever the fixture's own
+# space plan is (R11-OUTSIDE-HONEST-STARTS-RUNS: the committed plan of this
+# install no longer presses a step the re-plan moves).
 _dsp_co_out = _dsp_co.opt._co_optimize(
     _dsp_co.builds[0][2],
-    space_power=_dsp_co.solved[0][0],
+    space_power=np.full(96, 5.5),
     dhw_power=np.asarray(_dsp_co.builds[0][1][0].schedule, float),
     status="first", best_score=-1e9, solve_space=_dsp_co_solve, p_max=5.5,
     planner=_dsp_co.builds[0][3],
@@ -92330,6 +92500,1069 @@ R.check(
 )
 
 
+# R11-OUTSIDE-HONEST-STARTS-RUNS, the descents of a solve that prices a stop.
+# The relaxed descent weighs a switch at the combined draw and the true
+# objective in starts, so the descent that avoids a switch can commit to a
+# plan the true objective scores above the one that kept it. Such a solve
+# therefore descends twice, with the switch operand and as a solve that
+# prices no stop would, and the true objective judges the candidates of both.
+# Two duty-cycle days, one where each descent supplies the plan that ships.
+# The scores are of one non-convex solve per arm (``fixer.md`` step 15): the
+# margins measured on x86_64 are 0.07 and 0.39, the checks ask for 0.01.
+_dsp_real_plans, _dsp_real_term = _dsp_om._relaxed_plans, _dsp_om._switch_cost_fn
+_dsp_descents = []
+
+
+def _dsp_arm(arm, **kw):
+    """One priced duty-cycle solve with an arm of the two descents removed."""
+    def plans(*args):
+        res, relaxed = _dsp_real_plans(*args)
+        _dsp_descents.append(len(relaxed))
+        return res, {"operand": relaxed[:1], "unpriced": relaxed[-1:]}.get(arm, relaxed)
+
+    def term(opt):
+        inner = _dsp_real_term(opt)
+        return lambda space, dhw, descent=None: (
+            None if descent == _dsp_om._RELAXED else inner(space, dhw, descent))
+
+    _dsp_om._relaxed_plans = plans
+    if arm == "no operand":
+        _dsp_om._switch_cost_fn = term
+    try:
+        return float(_dsp_solve(_DSP_PAIR, _DSP_OFF, **kw).result.objective_value)
+    finally:
+        _dsp_om._relaxed_plans, _dsp_om._switch_cost_fn = _dsp_real_plans, _dsp_real_term
+
+
+_dsp_days = {
+    day: {arm: _dsp_arm(arm, **kw) for arm in ("both", "operand", "unpriced", "no operand")}
+    for day, kw in (("mild", {}), ("cold", {"out_mean": -4.0}))
+}
+R.check(
+    "a solve that prices a stop commits both descents and ships the lower: on "
+    "the mild day the unpriced descent's plan, which the operand's descent "
+    "alone scores above; on the cold day the operand's, which the unpriced "
+    "descent alone scores above",
+    _dsp_days["mild"]["both"] <= _dsp_days["mild"]["unpriced"] + 1e-9
+    and _dsp_days["mild"]["both"] < _dsp_days["mild"]["operand"] - 0.01
+    and _dsp_days["cold"]["both"] <= _dsp_days["cold"]["operand"] + 1e-9
+    and _dsp_days["cold"]["both"] < _dsp_days["cold"]["unpriced"] - 0.01,
+    f"{_dsp_days}",
+)
+R.check(
+    "the relaxed descent still leaves a priced switch: with the switch operand "
+    "taken out of the relaxed closure the cold day's plan scores higher on the "
+    "true objective",
+    _dsp_days["cold"]["both"] < _dsp_days["cold"]["no operand"] - 0.01,
+    f"{_dsp_days['cold']}",
+)
+_dsp_descents.clear()
+_dsp_real_min = _dsp_om._multi_start_minimize
+_dsp_caps, _dsp_call_caps = [], []
+
+
+def _dsp_counted_plans(*args):
+    """The real relaxed plans, their count and the caps their multi-starts ran under."""
+    seen = len(_dsp_caps)
+    out = _dsp_real_plans(*args)
+    _dsp_descents.append(len(out[1]))
+    _dsp_call_caps.append(tuple(_dsp_caps[seen:]))
+    return out
+
+
+def _dsp_capped_min(*args, **kw):
+    _dsp_caps.append(kw.get("maxiter"))
+    return _dsp_real_min(*args, **kw)
+
+
+_dsp_om._relaxed_plans, _dsp_om._multi_start_minimize = _dsp_counted_plans, _dsp_capped_min
+try:
+    _dsp_once = [_dsp_solve(*pairs, **kw) for pairs, kw in (
+        ((None,), {}), (((0.0, 0.0), (0.0, 0.0)), {}), ((_DSP_PAIR, _DSP_OFF), {"cyc": 0.0}))]
+    _dsp_once_n, _dsp_twice_n = set(_dsp_descents), None
+    _dsp_descents.clear()
+    _dsp_call_caps.clear()
+    _dsp_solve(_DSP_PAIR, _DSP_OFF)
+    _dsp_twice_n = set(_dsp_descents)
+finally:
+    _dsp_om._relaxed_plans, _dsp_om._multi_start_minimize = _dsp_real_plans, _dsp_real_min
+R.check(
+    "null control: with no pair, an empty learner or no priced cycle every space "
+    "solve descends once, and the empty learner's plan is the plan of a config "
+    "that never heard of the pair; with the contributor's pair it descends twice",
+    _dsp_once_n == {1} and _dsp_twice_n == {2} and _dsp_same_plan(_dsp_once[0], _dsp_once[1]),
+    f"{_dsp_once_n} {_dsp_twice_n}",
+)
+# The second descent is one more multi-start and no more than that: it runs
+# under the cap the first was handed, read off the two calls of each space
+# solve of the pair's own solve (no cap is restated here).
+R.check(
+    "a space solve that descends twice hands both multi-starts the same "
+    "iteration cap",
+    bool(_dsp_call_caps)
+    and all(len(c) == 2 and c[0] is not None and c[0] == c[1] for c in _dsp_call_caps),
+    f"caps per space solve {_dsp_call_caps}",
+)
+
+
+# The plan a space solve adopts publishes with the vector of the scope the
+# stage scored it in, not the last one built: the stage is stood in for by one
+# that hands back a marked vector.
+_dsp_marked = np.full(96, 0.5)
+_dsp_real_commit = _dsp_om._commit_runs
+_dsp_om._commit_runs = lambda _opt, _h, scope, relaxed, *_rest: (relaxed[0], (*scope[:3], _dsp_marked))
+try:
+    _dsp_e.opt._solve_space(*_dsp_e.solves[0])
+finally:
+    _dsp_om._commit_runs = _dsp_real_commit
+R.check(
+    "the plan a space solve adopts publishes with the vector of the scope it "
+    "was scored in",
+    _dsp_e.opt._space_avail is _dsp_marked,
+)
+
+# The commit's tie break, read at the stage beside a hot-water charge (design
+# note round 3, test 3 and item a3). On an install that prices no start, at a
+# zero price, no mask buys anything, so every band's mask is the relaxed
+# plan's own runs and each candidate of the stage is that plan. Corpus: 60
+# realizable plans of 24 steps, one charge each, from a stopped and a running
+# compressor. At a flat price the same plans get another candidate.
+_dsp_tie_rng = np.random.default_rng(3602)
+_dsp_tie_opt = _dsp_opt(clamp=True, cyc=0.0)
+_dsp_tie_moved = {"zero price": 0, "flat price": 0}
+for _dsp_tie_i in range(60):
+    _dsp_tie_space = np.where(_dsp_tie_rng.random(24) < 0.5, 0.0, _dsp_tie_rng.uniform(1.5, 3.0, 24))
+    _dsp_tie_dhw = np.zeros(24)
+    _dsp_tie_dhw[int(_dsp_tie_rng.integers(0, 24))] = 2.5
+    _dsp_tie_space[_dsp_tie_dhw > 0.0] = 0.0
+    for _dsp_tie_name, _dsp_tie_price in (("zero price", 0.0), ("flat price", 0.2)):
+        _dsp_tie_moved[_dsp_tie_name] += not all(
+            np.array_equal(c, _dsp_tie_space) for c in _dsp_om._run_plans(
+                _dsp_tie_opt,
+                _DspNS(prices=np.full(24, _dsp_tie_price), dt=0.25, compressor_running=bool(_dsp_tie_i % 2)),
+                _dsp_tie_space, _dsp_tie_dhw, np.zeros(24), 5.5 - _dsp_tie_dhw, np.zeros(24, dtype=bool)))
+R.check(
+    "beside a hot-water charge, at a zero price on an install that prices no "
+    "start, every candidate of the stage is the realizable relaxed plan itself; "
+    "at a flat price the same plans get another",
+    _dsp_tie_moved == {"zero price": 0, "flat price": 60},
+    f"{_dsp_tie_moved}",
+)
+
+
+# ===========================================================================
+# R11-OUTSIDE-HONEST-STARTS-RUNS (pull request 3529, Bankaifan): a start is
+# priced as one start, and an engaged solve ships runs the pump can run.
+# ===========================================================================
+R.section("R11-OUTSIDE-HONEST-STARTS-RUNS: the start count and committed runs")
+from dataclasses import replace as _hsr_replace  # noqa: E402
+from types import SimpleNamespace as _HsrNS  # noqa: E402
+
+import heatpump_optimizer.optimizer as _hsr_om  # noqa: E402
+from heatpump_optimizer import duty_legs as _hsr_dl  # noqa: E402
+from heatpump_optimizer import duty_switch as _hsr_ds  # noqa: E402
+from heatpump_optimizer import early_cutoff as _hsr_ec  # noqa: E402
+from heatpump_optimizer import runs as _hsr_runs  # noqa: E402
+from heatpump_optimizer import supply_hold as _hsr_sh  # noqa: E402
+from heatpump_optimizer.thermal_model import (  # noqa: E402
+    MIN_RUNNING_DRAW_KW as _HSR_RUNS_AT,
+    ThermalModel as _HsrTM,
+    ThermalParameters as _HsrTP,
+    ThermalState as _HsrTS,
+)
+
+_hsr_count, _hsr_edges = _hsr_runs.start_count, _hsr_runs.edge_count
+
+# 1. The count. Generated plans whose every step is off or at the floor or
+# above: the count is the integer number of off-to-on edges, from a stopped
+# and from a running compressor. Corpus: 400 plans, widths 1 to 96.
+_hsr_rng = np.random.default_rng(3529)
+_hsr_int_bad = []
+for _hsr_i in range(400):
+    _hsr_n = int(_hsr_rng.integers(1, 97))
+    _hsr_f = float(_hsr_rng.choice([0.0, 0.53, 1.1, 5.5]))
+    _hsr_q = np.where(
+        _hsr_rng.random(_hsr_n) < 0.5, 0.0,
+        _hsr_rng.uniform(max(_hsr_f, 0.11), 5.5 + 1e-12, _hsr_n),
+    )
+    for _hsr_run in (False, True):
+        if _hsr_count(_hsr_q, _hsr_f, _hsr_run) != _hsr_edges(_hsr_q, _hsr_run):
+            _hsr_int_bad.append((_hsr_i, _hsr_run))
+R.check(
+    "on a plan whose steps are all off or at the floor or above, the start count "
+    "is the integer number of off-to-on edges, from a stopped and a running compressor",
+    not _hsr_int_bad,
+    f"{_hsr_int_bad[:5]} of {len(_hsr_int_bad)}",
+)
+R.check(
+    "a constant level under the floor is counted as the starts it is, and a level "
+    "change inside a run is none",
+    _hsr_count(np.full(8, 0.55), 1.1) == 1.0 + 7 * 0.5
+    and _hsr_count([2.0, 4.0, 2.0, 5.5], 1.1, True) == 0.0
+    and _hsr_count([2.0, 4.0, 2.0, 5.5], 1.1) == 1.0,
+    f"{_hsr_count(np.full(8, 0.55), 1.1)}",
+)
+R.check(
+    "a start to the floor and a start to the maximum cost the same one start",
+    _hsr_count([0.0, 1.1, 1.1], 1.1) == _hsr_count([0.0, 5.5, 5.5], 1.1) == 1.0,
+)
+R.check(
+    "a running compressor continues free, and pays for a stop and a return; a "
+    "stopped one pays for its first step",
+    _hsr_count([3.0, 3.0, 3.0], 1.1, True) == 0.0
+    and _hsr_count([3.0, 0.0, 3.0], 1.1, True) == 1.0
+    and _hsr_count([3.0, 0.0, 3.0], 1.1) == 2.0
+    and _hsr_edges([3.0, 0.0, 3.0], True) == 1 and _hsr_edges([3.0, 0.0, 3.0]) == 2,
+)
+R.check(
+    "a step needs the compressor by the plan's running rule, not by the floor, "
+    "and leaves its successor the share of a start it did not run",
+    _hsr_count([0.0, 0.2], 1.1) == 1.0
+    and _hsr_count([0.55, 3.0], 1.1, True) == 0.5
+    and _hsr_count([0.0, _HSR_RUNS_AT / 2.0], 1.1) == 0.5,
+    f"{_hsr_count([0.0, 0.2], 1.1)} {_hsr_count([0.55, 3.0], 1.1, True)}",
+)
+R.check(
+    "a configured floor of zero still counts against the plan's running rule",
+    _hsr_runs.floor_kw(0.0) == _HSR_RUNS_AT and _hsr_runs.floor_kw(1.1) == 1.1
+    and _hsr_count([0.0, 0.2, 0.0, 0.05], 0.0) == 1.5
+    and _hsr_runs.realizable([0.0, 0.1, 3.0], 0.0)
+    and not _hsr_runs.realizable([0.0, 0.5, 3.0], 1.1)
+    and _hsr_runs.realizable([0.0, 1.1, 3.0], 1.1),
+    f"{_hsr_count([0.0, 0.2, 0.0, 0.05], 0.0)}",
+)
+
+# 2. Composition with the duty-switch term: weighed at p_max x the running
+# share, a boundary's switch weight and its start share never pass one start.
+_HSR_PMAX = 6.0
+
+
+def _hsr_switch(space, dhw, pair, floor, level_floor=None):
+    """The switch weight in starts (``level_floor`` given) or as today."""
+    space, dhw = np.asarray(space, float), np.asarray(dhw, float)
+    level = None if level_floor is None else _HSR_PMAX * _hsr_runs.running_share(space + dhw, level_floor)
+    return _hsr_dl.switch_weight(space, dhw, pair, _HSR_PMAX, floor, level=level)
+
+
+def _hsr_pair_cost(space, dhw, pair, floor=1.0, running=False):
+    return _hsr_count(np.add(space, dhw), floor, running) + _hsr_switch(space, dhw, pair, None, floor)
+
+
+R.check(
+    "hot water then heating at equal draw with a certain stop costs exactly two "
+    "starts with the steps adjacent, and exactly two with an idle step between",
+    _hsr_pair_cost([0.0, 3.0], [3.0, 0.0], (1.0, 0.0)) == 2.0
+    and _hsr_pair_cost([0.0, 0.0, 3.0], [3.0, 0.0, 0.0], (1.0, 0.0)) == 2.0
+    and _hsr_switch([0.0, 0.0, 3.0], [3.0, 0.0, 0.0], (1.0, 0.0), None, 1.0) == 0.0,
+    f"{_hsr_pair_cost([0.0, 3.0], [3.0, 0.0], (1.0, 0.0))}, "
+    f"{_hsr_pair_cost([0.0, 0.0, 3.0], [3.0, 0.0, 0.0], (1.0, 0.0))}",
+)
+# Grid: 2-step plans, each step one duty, levels from off through the floor to
+# p_max, both orders, three probabilities, duty-cycle and clamped leg reading.
+_HSR_LEVELS = (0.0, 0.05, 0.3, 0.99, 1.0, 2.5, 6.0)
+_hsr_grid_bad, _hsr_grid_n, _hsr_grid_kinds = [], 0, set()
+for _hsr_a in _HSR_LEVELS:
+    for _hsr_b in _HSR_LEVELS:
+        for _hsr_first_dhw in (True, False):
+            for _hsr_p in (0.3, 0.8, 1.0):
+                for _hsr_leg_floor in (None, 1.0):
+                    _hsr_sp = [0.0, _hsr_b] if _hsr_first_dhw else [_hsr_a, 0.0]
+                    _hsr_dh = [_hsr_a, 0.0] if _hsr_first_dhw else [0.0, _hsr_b]
+                    _hsr_share = _hsr_count(np.add(_hsr_sp, _hsr_dh), 1.0, True)
+                    _hsr_w = _hsr_switch(_hsr_sp, _hsr_dh, (_hsr_p, _hsr_p), _hsr_leg_floor, 1.0)
+                    _hsr_grid_n += 1
+                    if _hsr_share + _hsr_w > 1.0 + 1e-12:
+                        _hsr_grid_bad.append((_hsr_sp, _hsr_dh, _hsr_p, _hsr_leg_floor))
+                    if all(level == 0.0 or level >= 1.0 for level in (_hsr_a, _hsr_b)):
+                        # A committed pair: a start, a priced switch, or neither.
+                        _hsr_grid_kinds.add(round((_hsr_share + _hsr_w) / (_hsr_p if _hsr_w else 1.0), 12))
+R.check(
+    "over a grid of boundaries a step's start share plus the switch weight never "
+    "passes one start, and on a committed pair it is a start, the priced switch or nothing",
+    not _hsr_grid_bad and _hsr_grid_n == 588 and _hsr_grid_kinds == {0.0, 1.0},
+    f"{_hsr_grid_bad[:3]} of {len(_hsr_grid_bad)}; n {_hsr_grid_n}; kinds {_hsr_grid_kinds}",
+)
+R.check(
+    "the grid has something to detect: weighed at the combined draw beside the "
+    "start count (the keyword omitted) a boundary passes one start",
+    _hsr_count([0.5, 6.0], 1.0, True) + _hsr_switch([0.0, 6.0], [0.5, 0.0], (1.0, 1.0), None) < 1.0
+    < _hsr_count([0.5, 6.0], 1.0, True) + 1.0 * min(1.0, 6.0) / 1.0
+    and _hsr_switch([0.0, 3.0], [6.0, 0.0], (1.0, 0.0), None, 1.0) == 1.0
+    != _hsr_switch([0.0, 3.0], [6.0, 0.0], (1.0, 0.0), None),
+)
+_hsr_sw_rows = _hsr_rng.uniform(0.0, 3.0, size=(7, 12)) * (_hsr_rng.random((7, 12)) < 0.6)
+_hsr_sw_dhw = np.where(np.arange(12) % 4 == 1, 2.5, 0.0)
+R.check(
+    "with the level keyword omitted switch_weights_batch weighs at the combined "
+    "draw, value for value what the explicit draw gives, and a different level moves it",
+    np.array_equal(
+        _hsr_dl.switch_weights_batch(_hsr_sw_rows, _hsr_sw_dhw, (0.8, 0.6), _HSR_PMAX),
+        _hsr_dl.switch_weights_batch(
+            _hsr_sw_rows, _hsr_sw_dhw, (0.8, 0.6), _HSR_PMAX, level=_hsr_sw_rows + _hsr_sw_dhw),
+    )
+    and float(np.sum(_hsr_dl.switch_weights_batch(_hsr_sw_rows, _hsr_sw_dhw, (0.8, 0.6), _HSR_PMAX))) > 0.0
+    and not np.array_equal(
+        _hsr_dl.switch_weights_batch(_hsr_sw_rows, _hsr_sw_dhw, (0.8, 0.6), _HSR_PMAX),
+        _hsr_dl.switch_weights_batch(
+            _hsr_sw_rows, _hsr_sw_dhw, (0.8, 0.6), _HSR_PMAX,
+            level=_HSR_PMAX * _hsr_runs.running_share(_hsr_sw_rows + _hsr_sw_dhw, 1.0)),
+    ),
+)
+
+# 3. The commit. Generated relaxed plans (300), caps, forced steps, both step
+# widths: every mask's on steps lie in [floor, cap], forced steps are kept, a
+# mask that tracked ends within half a floor step, and at a 5-minute step no
+# unforced run or pause is shorter than the 10-minute minimums.
+
+
+def _hsr_stretches(mask):
+    edges = np.flatnonzero(np.diff(np.r_[False, mask, False]))
+    return list(zip(edges[::2].tolist(), edges[1::2].tolist()))
+
+
+_hsr_commit_bad, _hsr_commit_n, _hsr_tracked_n = [], 0, 0
+for _hsr_i in range(300):
+    _hsr_n = int(_hsr_rng.integers(6, 97))
+    _hsr_f = float(_hsr_rng.choice([0.53, 1.1]))
+    _hsr_dt = float(_hsr_rng.choice([0.25, 1.0 / 12.0]))
+    _hsr_q = np.where(_hsr_rng.random(_hsr_n) < 0.4, 0.0, _hsr_rng.random(_hsr_n) * _hsr_rng.choice([0.4, 1.5, 3.0]))
+    _hsr_caps = np.where(_hsr_rng.random(_hsr_n) < 0.1, 0.3, 3.0)
+    _hsr_forced = np.where(_hsr_rng.random(_hsr_n) < 0.1, _hsr_rng.integers(0, 2, _hsr_n).astype(float), np.nan)
+    _hsr_lengths = (_hsr_runs.steps_at_least(_hsr_runs.MIN_RUN, _hsr_dt),
+                    _hsr_runs.steps_at_least(_hsr_runs.MIN_PAUSE, _hsr_dt))
+    for _hsr_band in _hsr_runs.BANDS:
+        _hsr_mask, _hsr_ok = _hsr_runs.commit(
+            _hsr_q, _hsr_rng.random(_hsr_n) * 0.4, _hsr_f, _hsr_caps, 0.25, _hsr_band,
+            dt=_hsr_dt, running=bool(_hsr_i % 2), forced=_hsr_forced, lengths=_hsr_lengths)
+        _hsr_commit_n += 1
+        _hsr_level = np.minimum(np.maximum(_hsr_q, _hsr_f), _hsr_caps)
+        _hsr_free_on = _hsr_mask & np.isnan(_hsr_forced)
+        _hsr_end = float(np.sum(np.where(_hsr_mask, _hsr_level, 0.0) - _hsr_q) * _hsr_dt)
+        _hsr_short = [
+            (a, z) for keep, least in ((_hsr_mask, _hsr_lengths[0]), (~_hsr_mask, _hsr_lengths[1]))
+            for a, z in _hsr_stretches(keep)
+            if z - a < least and 0 < a and z < _hsr_n
+            and np.all(np.isnan(_hsr_forced[max(a - 1, 0):z + 1]))
+            and np.all(_hsr_caps[max(a - 1, 0):z + 1] >= _hsr_f)
+        ]
+        _hsr_tracked_n += _hsr_ok
+        if (
+            np.any(_hsr_level[_hsr_free_on] < _hsr_f - 1e-12)
+            or np.any(_hsr_mask[_hsr_forced == 0.0]) or not np.all(_hsr_mask[_hsr_forced == 1.0])
+            or (_hsr_ok and abs(_hsr_end) > _hsr_f * _hsr_dt / 2.0 + 1e-9)
+            or _hsr_short
+        ):
+            _hsr_commit_bad.append((_hsr_i, _hsr_band, _hsr_short[:1]))
+R.check(
+    "every committed mask runs its unforced on steps in [floor, cap], keeps every "
+    "forced step, ends within half a floor step where it tracked, and holds the "
+    "run and pause minimums as step counts",
+    not _hsr_commit_bad and _hsr_commit_n == 900 and 0 < _hsr_tracked_n < _hsr_commit_n,
+    f"{_hsr_commit_bad[:3]} of {len(_hsr_commit_bad)}; tracked {_hsr_tracked_n} of {_hsr_commit_n}",
+)
+R.check(
+    "the run and pause minimums are one pair: the supply gate's and the early "
+    "cut-off's are the leaf's own objects, two steps at 5 minutes and one at 15",
+    _hsr_sh.MIN_RUN is _hsr_runs.MIN_RUN and _hsr_sh.MIN_PAUSE is _hsr_runs.MIN_PAUSE
+    and _hsr_ec.MIN_ON is _hsr_runs.MIN_RUN and _hsr_ec.MIN_OFF is _hsr_runs.MIN_PAUSE
+    and _hsr_runs.steps_at_least(_hsr_runs.MIN_RUN, 1.0 / 12.0) == 2
+    and _hsr_runs.steps_at_least(_hsr_runs.MIN_PAUSE, 0.25) == 1,
+)
+_hsr_real = np.array([0.0, 0.0, 1.1, 2.0, 3.0, 0.0, 0.0, 0.0, 1.5, 1.5, 0.0, 0.0])
+_hsr_trickle = np.full(12, 0.55)
+_hsr_flat = np.full(12, 0.2)
+R.check(
+    "on a trickle at half the floor commit runs half the steps at the floor in one "
+    "run: the same energy, never a step raised on its own",
+    all(int(np.sum(m)) == 6 and _hsr_edges(np.where(m, 1.1, 0.0)) == 1 for m in _hsr_runs.candidates(
+        _hsr_trickle, _hsr_flat, 1.1, 3.0, 0.25, dt=0.25))
+    and _hsr_count(_hsr_trickle, 1.1) == 6.5,
+    f"{[m.astype(int).tolist() for m in _hsr_runs.candidates(_hsr_trickle, _hsr_flat, 1.1, 3.0, 0.25, dt=0.25)]}",
+)
+_hsr_far = np.r_[np.full(6, 3.0), np.zeros(6)]
+_hsr_far_mask, _hsr_far_ok = _hsr_runs.commit(
+    _hsr_far, _hsr_flat, 1.1, np.r_[np.zeros(6), np.full(6, 3.0)], 0.25, 2, dt=0.25)
+R.check(
+    "a balance its band cannot hold is penalised and never refused: the mask is a "
+    "best effort that says it did not track, and still buys the energy back",
+    _hsr_far_ok is False and not _hsr_far_mask[:6].any() and _hsr_far_mask[6:].any(),
+    f"{_hsr_far_mask.astype(int).tolist()} tracked {_hsr_far_ok}",
+)
+# On a realizable plan the program is the identity only where nothing can be
+# bought (design note round 3, test 3 and item a3): at a zero price and a zero
+# start price every mask ties and the tie break keeps the plan's own runs.
+# With a price on the steps, or on a start alone, the cheapest mask is another
+# one. Corpus: 300 realizable plans x the three bands, both step widths, from
+# a stopped and a running compressor, one-step lengths.
+_hsr_own_moved = {"nothing priced": 0, "steps priced": 0, "a start priced": 0}
+_hsr_own_n = 0
+for _hsr_i in range(300):
+    _hsr_n = int(_hsr_rng.integers(6, 97))
+    _hsr_f = float(_hsr_rng.choice([0.53, 1.1]))
+    _hsr_dt = float(_hsr_rng.choice([0.25, 1.0 / 12.0]))
+    _hsr_q = np.where(_hsr_rng.random(_hsr_n) < 0.5, 0.0, _hsr_rng.uniform(_hsr_f, 3.0, _hsr_n))
+    for _hsr_band in _hsr_runs.BANDS:
+        _hsr_own_n += 1
+        for _hsr_k, _hsr_p, _hsr_start in (
+            ("nothing priced", 0.0, 0.0), ("steps priced", 0.2, 0.0), ("a start priced", 0.0, 0.25),
+        ):
+            _hsr_own_moved[_hsr_k] += not np.array_equal(
+                _hsr_runs.commit(
+                    _hsr_q, _hsr_p, _hsr_f, 3.0, _hsr_start, _hsr_band,
+                    dt=_hsr_dt, running=bool(_hsr_i % 2))[0],
+                _hsr_q > 0.0)
+R.check(
+    "on a realizable plan commit returns the plan's own runs at a zero price and "
+    "a zero start price, and is not the identity where a step or a start has a price",
+    _hsr_own_n == 900 and _hsr_own_moved["nothing priced"] == 0
+    and _hsr_own_moved["steps priced"] > 0 and _hsr_own_moved["a start priced"] > 0,
+    f"{_hsr_own_moved} of {_hsr_own_n}",
+)
+
+# The leaf's edges and constants, read where no solve enters. Each clause
+# below is the boundary a pin drive left alive under this script: the running
+# rule is strict, an off step is realizable, the float slack counts a level
+# or a cap a hair under the floor as at it and one clearly under as under,
+# and the band constants are the approved design's (BANDS, the balance grid
+# and the out-of-band price: the contributor's spike, pinned as values).
+_hsr_f = _hsr_runs.floor_kw(1.1)
+R.check(
+    "a step at the running rule itself does not run, and one a hair above "
+    "starts the compressor",
+    _hsr_edges(np.array([0.0, _HSR_RUNS_AT, 0.0])) == 0
+    and _hsr_edges(np.array([0.0, _HSR_RUNS_AT + 1e-6])) == 1,
+)
+R.check(
+    "a plan is realizable with an off step and with a level inside the float "
+    "slack under the floor, at the slack's own edge too, and not with a level "
+    "clearly under it",
+    _hsr_runs.realizable(np.array([0.0, _hsr_f]), 1.1)
+    and _hsr_runs.realizable(np.array([_hsr_f - 1e-9]), 1.1)
+    and _hsr_runs.realizable(np.array([_hsr_f - 5e-10]), 1.1)
+    and not _hsr_runs.realizable(np.array([_hsr_f - 1e-6]), 1.1),
+)
+_hsr_cap_masks = [
+    _hsr_runs.commit(np.full(4, 1.1), 1.0, 1.1, _hsr_cap, 0.0, 2, dt=0.25)[0]
+    for _hsr_cap in (_hsr_f - 5e-10, _hsr_f - 1e-9, _hsr_f - 1e-6)
+]
+R.check(
+    "a cap inside the float slack under the floor still runs, at the slack's "
+    "own edge too, and a cap clearly under the floor forces the step off",
+    bool(_hsr_cap_masks[0].all()) and bool(_hsr_cap_masks[1].all()) and not _hsr_cap_masks[2].any(),
+    f"{[m.tolist() for m in _hsr_cap_masks]}",
+)
+R.check(
+    "the commit's bands, its balance grid and its out-of-band price are the "
+    "approved design's values",
+    (_hsr_runs.BANDS, _hsr_runs.QUANTA_PER_STEP, _hsr_runs.OUT_OF_BAND) == ((2, 6, 24), 4, 10.0),
+)
+
+_hsr_long_masks = _hsr_runs.candidates(
+    np.full(200, 0.55), np.r_[np.full(100, 2.0), np.full(100, 1.0)], 1.1, 5.5, 0.0, dt=0.25)
+R.check(
+    "where a band tracks the plan, the candidates are one mask per band and "
+    "no whole-horizon mask: three distinct masks on a trickle whose cheapest "
+    "mask of all is fifty floor steps from the plan",
+    len(_hsr_long_masks) == len(_hsr_runs.BANDS) == 3,
+    f"{len(_hsr_long_masks)} mask(s)",
+)
+
+# The band is held by a price, step by step (the design's mutation target "the
+# out-of-band penalty"), read at the leaf, where no solve and so no BLAS
+# kernel enters. A trickle at half the floor whose cheap steps are all in the
+# second half: the cheapest mask of all runs that half alone and is ten floor
+# steps behind the plan at mid-horizon. Each band's mask stays inside its
+# band and says so, and a wider band buys a cheaper mask.
+_hsr_late_q, _hsr_late_p = np.full(40, 0.55), np.r_[np.full(20, 2.0), np.full(20, 1.0)]
+_hsr_late = {}
+for _hsr_band in _hsr_runs.BANDS:
+    _hsr_m, _hsr_ok = _hsr_runs.commit(_hsr_late_q, _hsr_late_p, 1.1, 5.5, 0.0, _hsr_band, dt=0.25)
+    _hsr_late[_hsr_band] = (
+        _hsr_ok,
+        float(np.max(np.abs(np.cumsum(np.where(_hsr_m, 1.1, 0.0) - _hsr_late_q)))) / 1.1,
+        float(np.sum(_hsr_late_p[_hsr_m])) * 1.1 * 0.25,
+    )
+R.check(
+    "a balance outside its band is paid for at every step: where the cheapest "
+    "mask of all leaves the band, each band's mask stays within its band of the "
+    "plan's energy and reports it tracked, and a wider band buys a cheaper mask",
+    all(ok and far <= band + 1e-9 for band, (ok, far, _) in _hsr_late.items())
+    and _hsr_late[_hsr_runs.BANDS[-1]][1] > _hsr_runs.BANDS[1]
+    and [c for _, _, c in _hsr_late.values()] == sorted({c for _, _, c in _hsr_late.values()}, reverse=True),
+    f"band: (tracked, floor steps from the plan, price paid) {_hsr_late}",
+)
+
+# 4 and 6. The engaged solve. A buffered single-zone house on a mild day, where
+# the relaxed plan trickles under the floor; 15-minute steps, the contributor's
+# two floors (0.53 and 1.1 kW) and wear price (0.25). No private bundle.
+_HSR_STEPS = np.arange(96)
+_HSR_PRICES = 1.3 + 0.9 * np.sin(2 * np.pi * (_HSR_STEPS - 30) / 96.0)
+
+
+def _hsr_opt(cost, clamp, p_min, loss=0.4):
+    params = _HsrTP()
+    params.mixing_valve_mode = "none"
+    params.buffer_tank_volume = 750.0
+    params.min_electrical_power, params.max_electrical_power = p_min, 5.5
+    params.dhw_enabled, params.house_heat_loss_scale = False, loss
+    return _hsr_om.HeatPumpOptimizer(
+        _HsrTM(params), _hsr_om.OptimizationConfig(clamp_planned_levels=clamp, cycling_cost=cost))
+
+
+def _hsr_solve(cost, clamp, p_min, *, running=False, loss=0.4, out_mean=8.0, room=20.5, raises=False):
+    """One full ``optimize``: the result, the candidate lists the stage scored,
+    the relaxed plans it was handed and the true objective pair."""
+    opt = _hsr_opt(cost, clamp, p_min, loss)
+    seen = _HsrNS(plans=[], first=[], relaxed=[], objectives=[], stages=[], opt=opt)
+    real_plans, real_objectives = _hsr_om._run_plans, opt._solve_objectives
+    real_first, real_stage = _hsr_om._projection, _hsr_om._commit_runs
+
+    def stage(*args):
+        seen.stages.append(args)
+        return real_stage(*args)
+
+    def run_plans(o, h, space, *rest):
+        seen.relaxed.append(np.array(space, float))
+        seen.plans.append(real_plans(o, h, space, *rest))
+        if raises:
+            raise RuntimeError("the stage fails after its candidates are built")
+        return seen.plans[-1]
+
+    def projection(*args):
+        seen.first.append(real_first(*args))
+        return seen.first[-1]
+
+    def objectives(h):
+        seen.objectives.append(real_objectives(h))
+        return seen.objectives[-1]
+
+    _hsr_om._run_plans, opt._solve_objectives = run_plans, objectives
+    _hsr_om._projection, _hsr_om._commit_runs = projection, stage
+    outdoor = out_mean + 3.0 * np.sin(2 * np.pi * (_HSR_STEPS - 50) / 96.0)
+    try:
+        seen.result = opt.optimize(inputs=_hsr_replace(solve_inputs(
+            initial_state=_HsrTS(
+                room_temperature=room, upper_floor_temperature=room,
+                lower_floor_temperature=room, slab_temperature=room + 0.5,
+                outdoor_temperature=float(outdoor[0]),
+                buffer_tank_temperature=30.0, dhw_temperature=50.0,
+            ),
+            prices=_HSR_PRICES, outdoor_temps=outdoor,
+            start_time=datetime(2026, 1, 10, tzinfo=UTC),
+        ), compressor_running=running))
+    finally:
+        _hsr_om._run_plans, _hsr_om._projection = real_plans, real_first
+        _hsr_om._commit_runs = real_stage
+    seen.space = np.asarray(seen.result.power_schedule, float)
+    return seen
+
+
+def _hsr_under(plan, p_min):
+    """Steps that run under the floor."""
+    return int(np.sum((plan > _HSR_RUNS_AT) & (plan < _hsr_runs.floor_kw(p_min) - 1e-9)))
+
+
+_hsr_cells = {
+    (cost, clamp, p_min): _hsr_solve(cost, clamp, p_min)
+    for cost, clamp, p_min in (
+        (0.0, False, 1.1), (0.25, False, 1.1), (0.25, False, 0.53),
+        (0.0, True, 1.1), (0.25, True, 1.1),
+    )
+}
+_hsr_free = _hsr_cells[(0.0, False, 1.1)]
+_hsr_engaged = {k: v for k, v in _hsr_cells.items() if k != (0.0, False, 1.1)}
+R.check(
+    "the fixture has something to commit: the unpriced duty-cycle plan runs steps "
+    "under the floor, and every engaged solve was handed a relaxed plan that does",
+    _hsr_under(_hsr_free.space, 1.1) > 0 and not _hsr_free.plans
+    and all(v.plans and _hsr_under(v.relaxed[-1], k[2]) > 0 for k, v in _hsr_engaged.items()),
+    f"free {_hsr_under(_hsr_free.space, 1.1)}; "
+    f"{({k: _hsr_under(v.relaxed[-1], k[2]) if v.relaxed else None for k, v in _hsr_engaged.items()})}",
+)
+R.check(
+    "acceptance: an engaged plan ships no step between the running rule and the "
+    "floor, on a priced modulating install at both floors and on a clamped one",
+    all(_hsr_under(v.space, k[2]) == 0 for k, v in _hsr_engaged.items()),
+    f"{({k: _hsr_under(v.space, k[2]) for k, v in _hsr_engaged.items()})}",
+)
+
+
+def _hsr_scores(seen):
+    """The true-objective score of the shipped plan and of candidate (1)."""
+    _, objective, _, _ = seen.objectives[-1]
+    return float(objective(seen.space)), float(objective(seen.first[-1]))
+
+
+# The energy half of this acceptance is restated (``tests/README.md``, "A
+# knife-edge optimizer comparison must be measured across BLAS kernels"). It
+# read "within one floor step of the relaxed plan's energy", which no line of
+# the stage holds: a balance outside its band is penalised, never refused,
+# and the levels of the best candidates are re-solved inside their runs.
+# Under three of four OpenBLAS kernels the 1.1 kW cell ships one run where
+# the fourth ships two, almost two floor steps under its relaxed plan, at a
+# lower true objective: the plan a priced start is meant to buy. What the
+# stage does hold is asked in its place, a quantity of one solve: the shipped
+# plan scores no higher on its own objective than the projection of the
+# relaxed plan it was committed from. The energy difference is reported in
+# the detail and asserted nowhere.
+R.check(
+    "acceptance: a priced plan holds no more starts than the unpriced plan of the "
+    "same install by the same count, and scores no higher on its own objective "
+    "than the projection of the relaxed plan it was committed from",
+    all(
+        _hsr_count(v.space, k[2]) <= _hsr_count(_hsr_solve(0.0, False, k[2]).space, k[2]) + 1e-9
+        and _hsr_scores(v)[0] <= _hsr_scores(v)[1] + 1e-12
+        for k, v in _hsr_engaged.items() if k[0] > 0 and not k[1]
+    ),
+    f"starts, scores (shipped, projection), kWh against the relaxed plan: "
+    f"{({k: (round(_hsr_count(v.space, k[2]), 3), tuple(round(x, 4) for x in _hsr_scores(v)), round(float(np.sum(v.space - v.relaxed[-1])) * 0.25, 3)) for k, v in _hsr_engaged.items()})}",
+)
+R.check(
+    "selection: the shipped plan never scores above the projection (candidate 1) "
+    "on the true objective, and where a start has a price it scores strictly lower",
+    all(_hsr_scores(v)[0] <= _hsr_scores(v)[1] + 1e-12 for v in _hsr_engaged.values())
+    and any(_hsr_scores(v)[0] < _hsr_scores(v)[1] - 1e-6 for k, v in _hsr_engaged.items() if k[0] > 0),
+    f"{({k: tuple(round(s, 4) for s in _hsr_scores(v)) for k, v in _hsr_engaged.items()})}",
+)
+# A realizable relaxed plan is a candidate, never a result the stage is held
+# to (design note round 3, test 4): the relaxed descent prices no start, so
+# such a plan carries starts nobody priced. The fixture is the plan the same
+# house ships clamped at no price, which already runs, handed as the relaxed
+# plan to the stage of the priced solve, in that solve's own scope: the stage
+# ships another plan, with fewer starts, that the scope it ships in scores
+# strictly below the plan handed in. One non-convex stage per arm
+# (``fixer.md`` step 15): the margin measured on x86_64 is 0.70, the check
+# asks for 0.01.
+_hsr_ran = _hsr_cells[(0.0, True, 1.1)].space
+_hsr_ran_stage = _hsr_cells[(0.25, False, 1.1)].stages[-1]
+_hsr_ran_shipped, _hsr_ran_scope = _hsr_om._commit_runs(
+    *_hsr_ran_stage[:3], [_hsr_ran], *_hsr_ran_stage[4:])
+_hsr_ran_scores = float(_hsr_ran_scope[1](_hsr_ran)), float(_hsr_ran_scope[1](_hsr_ran_shipped))
+R.check(
+    "selection: a realizable relaxed plan that ships changed scores strictly "
+    "below itself in the scope it ships in, and its start count falls",
+    len(_hsr_cells[(0.25, False, 1.1)].stages) == 1 and _hsr_ran_stage[4] is None
+    and _hsr_runs.realizable(_hsr_ran, 1.1)
+    and not np.array_equal(_hsr_ran_shipped, _hsr_ran)
+    and _hsr_ran_scores[1] < _hsr_ran_scores[0] - 0.01
+    and _hsr_edges(_hsr_ran_shipped) < _hsr_edges(_hsr_ran),
+    f"scores {_hsr_ran_scores}, edges {_hsr_edges(_hsr_ran)} to {_hsr_edges(_hsr_ran_shipped)}",
+)
+_hsr_failed = _hsr_solve(0.25, False, 1.1, raises=True)
+R.check(
+    "selection: a stage that raises ships the projection, and the solve still "
+    "reports its own status",
+    np.array_equal(_hsr_failed.space, _hsr_failed.first[-1])
+    and not np.array_equal(_hsr_failed.space, _hsr_cells[(0.25, False, 1.1)].space)
+    and _hsr_failed.result.status == _hsr_cells[(0.25, False, 1.1)].result.status,
+    f"{_hsr_failed.result.status}",
+)
+R.check(
+    "the true objective prices cycling_cost per start of the shipped plan: the "
+    "published objective of a priced plan less the same plan's unpriced score is "
+    "cycling_cost x its start count",
+    abs(
+        float(_hsr_cells[(0.25, False, 1.1)].result.objective_value)
+        - float(_hsr_free.objectives[-1][1](_hsr_cells[(0.25, False, 1.1)].space))
+        - 0.25 * _hsr_count(_hsr_cells[(0.25, False, 1.1)].space, 1.1)
+    ) < 1e-9
+    and _hsr_count(_hsr_cells[(0.25, False, 1.1)].space, 1.1) >= 1.0,
+    f"{_hsr_cells[(0.25, False, 1.1)].result.objective_value}",
+)
+_hsr_obj, _hsr_obj_batch = _hsr_cells[(0.25, False, 1.1)].objectives[-1][1:3]
+_hsr_rows = np.stack([_hsr_cells[(0.25, False, 1.1)].space, _hsr_free.space, _hsr_trickle.repeat(8)])
+R.check(
+    "the relaxed objective is the true one less the start term, scalar and batch "
+    "bit for bit, and it is the unpriced solve's own objective",
+    all(
+        float(_hsr_obj_batch(_hsr_rows, descent=d)[i]) == float(_hsr_obj(_hsr_rows[i], descent=d))
+        for i in range(3) for d in (None, _hsr_om._RELAXED, _hsr_om._UNPRICED)
+    )
+    and all(
+        float(_hsr_obj(row, descent=_hsr_om._RELAXED)) == float(_hsr_free.objectives[-1][1](row))
+        and abs(float(_hsr_obj(row)) - float(_hsr_obj(row, descent=_hsr_om._RELAXED))
+                - 0.25 * _hsr_count(row, 1.1)) < 1e-9
+        for row in _hsr_rows
+    ),
+)
+
+# The running reading, r[-1]: the same solve from a running compressor ships a
+# plan whose published count is the integer edge count with no start at step 0.
+_hsr_run_on = _hsr_solve(0.25, False, 1.1, running=True, loss=1.0, out_mean=2.0, room=17.5)
+_hsr_run_off = _hsr_solve(0.25, False, 1.1, running=False, loss=1.0, out_mean=2.0, room=17.5)
+_hsr_free_on = _hsr_solve(0.0, False, 1.1, running=True, loss=1.0, out_mean=2.0, room=17.5)
+_hsr_free_off = _hsr_solve(0.0, False, 1.1, running=False, loss=1.0, out_mean=2.0, room=17.5)
+R.check(
+    "the published start count is the edge count of the shipped plan with the "
+    "solve's running reading, on an engaged and an unengaged install alike",
+    all(
+        v.result.compressor_starts == _hsr_edges(v.space, on)
+        for v, on in ((_hsr_run_on, True), (_hsr_run_off, False), (_hsr_free_on, True), (_hsr_free_off, False))
+    )
+    and _hsr_free_on.space[0] > _HSR_RUNS_AT
+    and _hsr_free_on.result.compressor_starts == _hsr_free_off.result.compressor_starts - 1,
+    f"{[v.result.compressor_starts for v in (_hsr_run_on, _hsr_run_off, _hsr_free_on, _hsr_free_off)]}",
+)
+
+# Null controls, each a full optimize twice with the arrays compared equal.
+R.check(
+    "null control, zero cost on a duty-cycle install: the solve never enters the "
+    "candidate stage, and the running reading moves no array of its plan",
+    not _hsr_free_on.plans and not _hsr_free_off.plans
+    and np.array_equal(_hsr_free_on.space, _hsr_free_off.space)
+    and _hsr_free_on.result.objective_value == _hsr_free_off.result.objective_value,
+)
+R.check(
+    "and that control has something to detect: where a start has a price the "
+    "running reading moves the score by the start it saves",
+    _hsr_run_on.result.objective_value != _hsr_run_off.result.objective_value,
+    f"{_hsr_run_on.result.objective_value} vs {_hsr_run_off.result.objective_value}",
+)
+# A realizable relaxed plan on a clamped install that prices no start ships
+# as it stands: the stage is the identity, the objective never called.
+
+
+def _hsr_never(*_args, **_kw):
+    raise AssertionError("the objective is not consulted")
+
+
+_hsr_h = _HsrNS(prices=_hsr_flat, dt=0.25, compressor_running=False)
+_hsr_box = [(0.0, 5.5)] * 12
+
+
+def _hsr_commit(opt, objective, batch, space, maxiter=5):
+    """The stage on one relaxed plan, in a scope with no priced stop: the plan it ships."""
+    return _hsr_om._commit_runs(opt, _hsr_h, (_hsr_box, objective, batch, None), [space], None, maxiter)[0]
+
+
+R.check(
+    "null control, a realizable relaxed plan: a clamped install that prices no "
+    "start ships it unchanged, the very array, and an unengaged solve any plan",
+    _hsr_commit(_hsr_opt(0.0, True, 1.1), _hsr_never, _hsr_never, _hsr_real) is _hsr_real
+    and _hsr_commit(_hsr_opt(0.0, False, 1.1), _hsr_never, _hsr_never, _hsr_trickle) is _hsr_trickle,
+)
+R.check(
+    "and with a plan that is not realizable the same call ships the projection "
+    "when its objective fails: every step at the floor, as a clamped install shipped before",
+    np.array_equal(
+        _hsr_commit(_hsr_opt(0.0, True, 1.1), _hsr_never, _hsr_never, _hsr_trickle), np.full(12, 1.1)),
+)
+# Identity on a plan that already runs is the stage's, not the program's: the
+# program buys the cheapest mask inside half a floor step of the plan's
+# energy, so it may run a step at the floor where the plan asked for more. The
+# stage keeps the relaxed plan as a candidate, and where no start has a price
+# it is the identity (the null control below).
+R.check(
+    "the stage offers the relaxed plan itself where it already runs, and never "
+    "where a step sits under the floor",
+    any(c is _hsr_real for c in _hsr_om._run_plans(
+        _hsr_opt(0.25, False, 1.1), _HsrNS(prices=_hsr_flat, dt=0.25, compressor_running=False),
+        _hsr_real, np.zeros(12), np.zeros(12), np.full(12, 5.5), np.zeros(12, dtype=bool)))
+    and not any(c is _hsr_trickle for c in _hsr_om._run_plans(
+        _hsr_opt(0.25, False, 1.1), _HsrNS(prices=_hsr_flat, dt=0.25, compressor_running=False),
+        _hsr_trickle, np.zeros(12), np.zeros(12), np.full(12, 5.5), np.zeros(12, dtype=bool))),
+)
+# The candidates of one stage: the projection, the masks, and the relaxed plan
+# where it runs; a pin, an off window and a cap under the floor are held by
+# every one.
+_hsr_lo = np.zeros(12)
+_hsr_lo[3] = 1.1
+_hsr_hi = np.full(12, 5.5)
+_hsr_hi[5], _hsr_hi[7] = 0.0, 0.4
+_hsr_cycled = np.arange(12) == 7
+_hsr_asked = np.clip(_hsr_trickle, _hsr_lo, _hsr_hi)
+_hsr_cands = [
+    _hsr_om._projection(_hsr_opt(0.25, False, 1.1), _hsr_asked, None, _hsr_hi, _hsr_cycled),
+    *_hsr_om._run_plans(_hsr_opt(0.25, False, 1.1), _hsr_h, _hsr_asked, np.zeros(12), _hsr_lo, _hsr_hi, _hsr_cycled),
+]
+_hsr_cands_clamp = _hsr_om._run_plans(
+    _hsr_opt(0.25, True, 1.1), _hsr_h, _hsr_asked, np.zeros(12), _hsr_lo, _hsr_hi, np.zeros(12, dtype=bool))
+R.check(
+    "the stage's candidates hold a forced-on pin, an off window and a cap under "
+    "the floor: on a duty-cycle install the capped step cycles as solved, on a "
+    "clamped one every mask leaves it off",
+    len(_hsr_cands) >= 2
+    and all(c[3] >= 1.1 and c[5] == 0.0 and c[7] == 0.4 for c in _hsr_cands)
+    and all(np.all((c[np.arange(12) != 7] == 0.0) | (c[np.arange(12) != 7] >= 1.1)) for c in _hsr_cands)
+    and _hsr_cands_clamp and all(c[3] >= 1.1 and c[5] == 0.0 and c[7] == 0.0 for c in _hsr_cands_clamp),
+    f"{[c.round(2).tolist() for c in _hsr_cands]}",
+)
+# A run that continues from a running compressor pays no start, in the
+# program and in the masks the stage builds from the horizon's reading. The
+# start price here (5.0) outbids the energy of the plan's opening run (0.55
+# kWh, which unbought costs 0.83 at the end of the band), so that run is
+# kept from a running compressor and dropped from a stopped one.
+_hsr_open = np.array([1.1, 1.1, 0.0, 0.0, 0.0, 0.0])
+_hsr_open_masks = {
+    on: [_hsr_runs.commit(_hsr_open, 0.2, 1.1, 3.0, 5.0, b, dt=0.25, running=on)[0].tolist() for b in _hsr_runs.BANDS]
+    for on in (True, False)
+}
+_hsr_open_plans = {
+    on: [c.tolist() for c in _hsr_om._run_plans(
+        _hsr_opt(5.0, False, 1.1), _HsrNS(prices=np.full(6, 0.2), dt=0.25, compressor_running=on),
+        _hsr_open, np.zeros(6), np.zeros(6), np.full(6, 5.5), np.zeros(6, dtype=bool))[:-1]]
+    for on in (True, False)
+}
+R.check(
+    "a run that continues from a running compressor pays no start: at a start "
+    "price that outbids its energy the plan's opening run is kept from a running "
+    "compressor and dropped from a stopped one, by the program in every band",
+    _hsr_open_masks == {True: [(_hsr_open > 0.0).tolist()] * 3, False: [[False] * 6] * 3},
+    f"{_hsr_open_masks}",
+)
+R.check(
+    "and the stage commits with the horizon's running reading: its masks keep "
+    "that opening run from a running compressor and drop it from a stopped one",
+    _hsr_open_plans == {True: [_hsr_open.tolist()], False: [[0.0] * 6]},
+    f"{_hsr_open_plans}",
+)
+_hsr_box_of = _hsr_om._run_bounds(np.array([0.0, 1.1, 3.0, 0.4]), np.zeros(4), np.array([5.5, 5.5, 5.5, 0.4]), 1.1)
+R.check(
+    "a candidate's levels are re-solved inside its own runs: an off step is held "
+    "shut, an on step bounded at the floor, a step cycled under its cap held as it stands",
+    _hsr_box_of == [(0.0, 0.0), (1.1, 5.5), (1.1, 5.5), (0.4, 0.4)],
+    f"{_hsr_box_of}",
+)
+
+# The running reading: the running signal's settled class with no change
+# pending, else the executing step's planned draw; the record keeps it.
+_hsr_rec = _hsr_ds._Record(None, None)
+_HSR_IDLE, _HSR_HEATS = {"power": 0.0, "dhw_power": 0.0}, {"power": 3.0}
+_hsr_reads = [_hsr_ds.running_now(_hsr_rec, action) for action in (
+    {}, _HSR_IDLE, {"power": _HSR_RUNS_AT}, {"power": 0.11}, _HSR_HEATS, {"power": 0.0, "dhw_power": 2.0})]
+_hsr_rec.signal.tracker.settled = True
+_hsr_rec.signal.tracker.pending = (False, datetime(2026, 1, 1, tzinfo=timezone.utc))
+_hsr_reads.append(_hsr_ds.running_now(_hsr_rec, _HSR_IDLE))  # a change pending: the step
+_hsr_rec.signal.tracker.pending = None
+_hsr_reads += [_hsr_ds.running_now(_hsr_rec, _HSR_IDLE), _hsr_rec.solved_running]  # settled running beats an idle step
+_hsr_rec.signal.tracker.settled = False
+_hsr_reads += [_hsr_ds.running_now(_hsr_rec, _HSR_HEATS), _hsr_rec.solved_running]  # settled stopped beats a planned draw
+_hsr_rec.signal.tracker.settled = None
+_hsr_reads += [_hsr_ds.running_now(_hsr_rec, _HSR_HEATS), _hsr_ds.running_now(_hsr_rec, _HSR_IDLE)]
+R.check(
+    "the running reading is the running signal's settled class where it has "
+    "settled with no change pending, else the executing step's planned draw of "
+    "either circuit by the plan's running rule, and the pump's record keeps the last one",
+    _hsr_reads == [False, False, False, True, True, True, False, True, True, False, False, True, False]
+    and _hsr_ds._Record(None, None).solved_running is False,
+    f"{_hsr_reads}",
+)
+
+# At a 5-minute step ``candidates`` plans no unforced run or pause shorter
+# than the two-step minimums; the same plans committed with one-step lengths
+# do hold such a run or pause, so the lengths are what keeps them out.
+_hsr_len_short = {"candidates": 0, "one-step lengths": 0}
+for _hsr_i in range(60):
+    _hsr_q = np.where(_hsr_rng.random(48) < 0.5, 0.0, _hsr_rng.random(48) * 1.5)
+    _hsr_p = _hsr_rng.random(48) * 0.4
+    _hsr_masks = {
+        "candidates": _hsr_runs.candidates(_hsr_q, _hsr_p, 1.1, 3.0, 0.02, dt=1.0 / 12.0),
+        "one-step lengths": [_hsr_runs.commit(_hsr_q, _hsr_p, 1.1, 3.0, 0.02, b, dt=1.0 / 12.0)[0]
+                             for b in _hsr_runs.BANDS],
+    }
+    for _hsr_k, _hsr_ms in _hsr_masks.items():
+        _hsr_len_short[_hsr_k] += sum(
+            1 for m in _hsr_ms for keep in (m, ~m) for a, z in _hsr_stretches(keep)
+            if z - a < 2 and 0 < a and z < 48
+        )
+R.check(
+    "at a 5-minute step the stage's masks hold no run or pause shorter than the "
+    "10-minute minimums; committed at one-step lengths the same plans do",
+    _hsr_len_short["candidates"] == 0 and _hsr_len_short["one-step lengths"] > 0,
+    f"{_hsr_len_short}",
+)
+
+# Selection on a stand-in objective, the distance to a chosen plan: the stage
+# ships whichever candidate scores lowest, the projection included.
+
+
+def _hsr_toward(target):
+    def objective(x, *_args, **_kw):
+        return float(np.sum((np.asarray(x, float) - target) ** 2))
+
+    def batch(rows, *_args, **_kw):
+        return np.sum((np.atleast_2d(rows) - target) ** 2, axis=1)
+
+    return objective, batch
+
+
+_hsr_sel_opt = _hsr_opt(0.25, False, 1.1)
+_hsr_sel_first = _hsr_om._projection(_hsr_sel_opt, _hsr_trickle, None, np.full(12, 5.5), np.zeros(12, dtype=bool))
+_hsr_sel_masks = _hsr_om._run_plans(
+    _hsr_sel_opt, _hsr_h, _hsr_trickle, np.zeros(12), np.zeros(12), np.full(12, 5.5), np.zeros(12, dtype=bool))
+_hsr_sel = {
+    name: _hsr_commit(_hsr_sel_opt, *_hsr_toward(target), _hsr_trickle, 20)
+    for name, target in (("projection", _hsr_sel_first), ("mask", _hsr_sel_masks[-1]))
+}
+R.check(
+    "selection on a stand-in objective: the stage ships the projection where it "
+    "scores lowest and a committed mask where that does, and the two differ",
+    np.allclose(_hsr_sel["projection"], _hsr_sel_first, atol=1e-6)
+    and np.allclose(_hsr_sel["mask"], _hsr_sel_masks[-1], atol=1e-6)
+    and not np.allclose(_hsr_sel_first, _hsr_sel_masks[-1]),
+    f"{_hsr_sel['projection'].round(3).tolist()} {_hsr_sel['mask'].round(3).tolist()}",
+)
+# The re-solve moves levels inside a candidate's runs: toward a plan that
+# keeps a mask's runs at a higher level, the shipped plan reaches that level
+# on the mask's on steps and stays off on the rest.
+_hsr_sel_high = np.where(_hsr_sel_masks[-1] > 0.0, 2.5, 0.0)
+_hsr_sel_lifted = _hsr_commit(_hsr_sel_opt, *_hsr_toward(_hsr_sel_high), _hsr_trickle, 50)
+R.check(
+    "the best candidates' levels are re-solved inside their own runs: toward the "
+    "same runs at 2.5 kW the shipped plan reaches it, off steps held shut",
+    np.allclose(_hsr_sel_lifted, _hsr_sel_high, atol=1e-3)
+    and not np.allclose(_hsr_sel_masks[-1], _hsr_sel_high),
+    f"{_hsr_sel_lifted.round(3).tolist()}",
+)
+# Several relaxed plans: each is committed on its own and the lowest ships,
+# so a second plan can lower the score and never raise it.
+_hsr_two_obj = _hsr_toward(_hsr_sel_high)
+_hsr_two = {
+    name: _hsr_om._commit_runs(_hsr_sel_opt, _hsr_h, (_hsr_box, *_hsr_two_obj, None), plans, None, 50)[0]
+    for name, plans in (
+        ("far", [np.zeros(12)]), ("far then near", [np.zeros(12), _hsr_trickle]),
+        ("near then far", [_hsr_trickle, np.zeros(12)]),
+    )
+}
+_hsr_two_score = {name: _hsr_two_obj[0](plan) for name, plan in _hsr_two.items()}
+R.check(
+    "each relaxed plan is committed on its own and the lowest score ships: a "
+    "second relaxed plan lowers the score where its runs are the better ones, in "
+    "either order, and never raises it",
+    _hsr_two_score["far then near"] == _hsr_two_score["near then far"] < _hsr_two_score["far"] - 1.0,
+    f"{_hsr_two_score}",
+)
+R.check(
+    "in the full solves the shipped plan scores no higher on the true objective "
+    "than any candidate the stage scored",
+    all(
+        float(v.objectives[-1][1](v.space))
+        <= min(float(v.objectives[-1][1](c)) for c in (v.first[-1], *v.plans[-1])) + 1e-12
+        for v in _hsr_engaged.values()
+    ),
+)
+
+# The coordinator hands the reading to the scheduled solve and keeps it for a
+# solve compared against that plan.
+from harness import FakeEntry as _HsrEntry  # noqa: E402
+from heatpump_optimizer.plan_step import plan_step_start as _hsr_pss  # noqa: E402
+
+_hsr_live = Coord(FakeHass(), _HsrEntry(data={"tibber_token": "x", "weather_entity": "weather.home"}))
+
+
+def _hsr_record_reading(action):
+    _hsr_live._current_action = action
+    now = _hsr_pss(datetime(2026, 1, 10, 12, 0, tzinfo=UTC))
+    read = _hsr_live._solve_record(now, _hsr_live._forecast_arrays(now)).inputs.compressor_running
+    return read, _hsr_ds.record_for(_hsr_live).solved_running
+
+
+_hsr_wired = [
+    _hsr_ds.record_for(_hsr_live).solved_running,
+    _hsr_record_reading({"power": 3.0, "dhw_power": 0.0}),
+    _hsr_record_reading({"power": 0.0, "dhw_power": 2.0}),
+    _hsr_record_reading({}),
+]
+R.check(
+    "the coordinator's scheduled solve reads whether the compressor runs from "
+    "its executing step, either circuit, and keeps the reading; before any "
+    "solve the kept reading is not running",
+    _hsr_wired == [False, (True, True), (True, True), (False, False)],
+    f"{_hsr_wired}",
+)
+import inspect as _hsr_inspect  # noqa: E402
+
+R.check(
+    "the what-if solve takes the reading the live plan was solved with, not a "
+    "fresh one: the two start counts the card compares share r[-1]",
+    "compressor_running=duty_switch.record_for(self).solved_running" in _hsr_inspect.getsource(Coord._whatif_solve)
+    and "compressor_running=duty_switch.running_now(duty_switch.record_for(self), self._current_action)"
+    in _hsr_inspect.getsource(Coord._solve_record),
+)
+
+# What the commit program is told is fixed: a forced-on pin and a step hot
+# water runs in are on, a step with no room at all is off, the rest are free.
+_hsr_forced_seen = []
+_hsr_real_candidates = _hsr_runs.candidates
+
+
+def _hsr_spy(*args, **kwargs):
+    _hsr_forced_seen.append(np.array(kwargs["forced"], float))
+    return _hsr_real_candidates(*args, **kwargs)
+
+
+_hsr_tank = np.zeros(12)
+_hsr_tank[9] = 2.0
+_hsr_runs.candidates = _hsr_spy
+try:
+    _hsr_om._run_plans(
+        _hsr_opt(0.25, False, 1.1), _hsr_h, _hsr_asked, _hsr_tank, _hsr_lo, _hsr_hi, _hsr_cycled)
+finally:
+    _hsr_runs.candidates = _hsr_real_candidates
+_hsr_forced_want = np.full(12, np.nan)
+_hsr_forced_want[[3, 9]], _hsr_forced_want[5] = 1.0, 0.0
+R.check(
+    "the commit program is handed a forced-on pin and a hot-water step as on, "
+    "a step with no room as off, and every other step free",
+    len(_hsr_forced_seen) == 1
+    and np.array_equal(_hsr_forced_seen[0], _hsr_forced_want, equal_nan=True),
+    f"{_hsr_forced_seen}",
+)
+
+# A candidate is held to the bound of its own scope. A stand-in rescope hands
+# every candidate a 2.0 kW ceiling and an objective that wants 3.0 kW: the
+# plan that ships stays under the ceiling, where the relaxed plan's own 3.0 kW
+# would have scored lowest unheld.
+_hsr_own_relaxed = np.where(np.arange(12) < 6, 3.0, 0.0)
+_hsr_own_obj = _hsr_toward(_hsr_own_relaxed)
+_hsr_own_calls = []
+
+
+def _hsr_own_scope(plan):
+    _hsr_own_calls.append(np.array(plan, float))
+    return [(0.0, 2.0)] * 12, *_hsr_own_obj, None
+
+
+_hsr_own, _hsr_own_shipped_scope = _hsr_om._commit_runs(
+    _hsr_sel_opt, _hsr_h, (_hsr_box, *_hsr_own_obj, None), [_hsr_own_relaxed], None, 30, _hsr_own_scope)
+R.check(
+    "each candidate is scored in the scope of a solve started from it and held "
+    "to that scope's bound, and the plan ships with the scope it was scored in",
+    len(_hsr_own_calls) >= 1 and float(_hsr_own.max()) <= 2.0 + 1e-9
+    and np.allclose(_hsr_own[:6], 2.0, atol=1e-3)
+    and _hsr_own_shipped_scope[0] == [(0.0, 2.0)] * 12
+    and float(_hsr_commit(_hsr_sel_opt, *_hsr_own_obj, _hsr_own_relaxed, 30).max()) == 3.0,
+    f"{_hsr_own.round(3).tolist()}",
+)
+
+# The start term's closure: nothing at zero cost and on a descent (no operand
+# is added), cycling_cost x the count otherwise, a float or one entry per row.
+_hsr_term = _hsr_om._start_cost_fn(_hsr_opt(0.25, False, 1.1), False)
+R.check(
+    "the start term is no operand at zero cost or on a descent, and "
+    "cycling_cost x the start count otherwise, scalar and batch",
+    _hsr_om._start_cost_fn(_hsr_opt(0.0, False, 1.1), False)(_hsr_trickle, None) is None
+    and _hsr_term(_hsr_trickle, _hsr_om._RELAXED) is None
+    and _hsr_term(_hsr_trickle, _hsr_om._UNPRICED) is None
+    and _hsr_term(_hsr_trickle, None) == 0.25 * _hsr_count(_hsr_trickle, 1.1)
+    and _hsr_term(np.stack([_hsr_trickle, _hsr_real]), None).tolist()
+    == [0.25 * _hsr_count(_hsr_trickle, 1.1), 0.25 * _hsr_count(_hsr_real, 1.1)]
+    and _hsr_om._start_cost_fn(_hsr_opt(0.25, False, 1.1), True)(_hsr_real, None)
+    == 0.25 * _hsr_count(_hsr_real, 1.1, True),
+)
+# The humidity guard the two SolveInputs sites share.
+from heatpump_optimizer.coordinator import _humidity_with_data as _hsr_humidity  # noqa: E402
+
+_hsr_rh = np.array([np.nan, 55.0, np.nan])
+R.check(
+    "a solve is handed its humidity series only when it carries data: the very "
+    "array with one finite value, None when empty or all unknown",
+    _hsr_humidity(_hsr_rh) is _hsr_rh
+    and _hsr_humidity(np.array([], dtype=float)) is None
+    and _hsr_humidity(np.full(4, np.nan)) is None,
+)
+
+
 # --- #3616: an implausible slab seed is refused --------------------------------
 R.section("#3616: a floor-return reading far above the room does not seed the slab")
 
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index b4a0d77201..0c54d4baee 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -67,6 +67,8 @@
 # v10.0.2: card applies a plan only up to the manual-plan window; implausible floor-return readings no longer seed the slab. The stamp empties the list; the
 # next branch restates its own footprint, claims included.
 #
+cycling_cost  # space steps under the floor 5 -> 0, starts 5 -> 4, energy 44.96 -> 40.97 kWh, predicted_cost 34.48 -> 32.07, lowest room 17.20 -> 17.16
+everything_on  # space steps under the floor 12 -> 0, starts 4 -> 5, energy 67.18 -> 68.83 kWh, predicted_cost 60.27 -> 61.48, lowest room 17.78 -> 17.88
 # may-drift: flat_prices -- #1208 polish-every-candidate, owner ruling #1208 comment 208bed25
 # (option (a)): the move's margin is inside the noise band (objective rel
 # -1.2171e-03, deterministic on one box), so which runner sees it move is the
@@ -117,13 +119,15 @@
 # keys (prices/outdoor_temps/price_known/baseline_cost) still fail. Remove
 # when drift lanes are pinned or the polish improvement scale leaves
 # 5e-5-2e-2.
-# may-drift: cycling_cost -- #1207 keep-gate (2e-2 -> 2e-5), owner directive
+# (R11-OUTSIDE-HONEST-STARTS-RUNS suspends cycling_cost's may-drift entry for its claim below; restore it,
+#  verbatim, when the stamp empties the list) cycling_cost -- #1207 keep-gate (2e-2 -> 2e-5), owner directive
 # #1207 comment c1329fe (2026-09-20): the move's margin is inside the noise
 # band (objective rel -1.7666e-04, deterministic on one box),
 # runner-conditional for the same reason; judged keys still fail. Remove
 # when drift lanes are pinned or the polish improvement scale leaves
 # 5e-5-2e-2.
-# may-drift: everything_on -- #1207 keep-gate (2e-2 -> 2e-5), owner
+# (R11-OUTSIDE-HONEST-STARTS-RUNS suspends everything_on's may-drift entry for its claim below; restore it,
+#  verbatim, when the stamp empties the list) everything_on -- #1207 keep-gate (2e-2 -> 2e-5), owner
 # directive #1207 comment c1329fe (2026-09-20): the move's margin is inside
 # the noise band (objective rel -5.2974e-03, deterministic on one box),
 # runner-conditional for the same reason; judged keys still fail. Remove
@@ -772,3 +776,17 @@
 # baseline_cost is a judged key a may-drift entry cannot excuse, so the six
 # with one are suspended above for this release (the wood_coil precedent).
 # Direction per fixture, branch vs base:
+# R11-OUTSIDE-HONEST-STARTS-RUNS (pull request 3529, Bankaifan): a start is
+# priced as one start (`runs.start_count`) in place of the swing of the
+# combined draw, and a solve that prices a start, or whose install cannot
+# duty-cycle, ships the lowest-scoring of its relaxed plan's committed runs.
+# Measured with tests/env_drift.py --all against the merge base in one
+# environment: exactly the two plan fixtures that set a cycling cost move, and
+# every other fixture is byte-identical, which is the null. The third fixture
+# with a cycling cost, coord_all_features, is byte-identical too and is not
+# claimed: a coord capture holds no plan. Both entries were may-drift, which a
+# claim cannot stand beside, so they are suspended above for this release.
+# Direction per fixture, base -> head, one box; the space plan's steps between
+# the running rule and the 1.0 kW floor, starts by the edge count
+# (`runs.edge_count`), energy, predicted_cost, lowest room. Hot-water levels
+# under the floor are the planner's and are not committed here.
diff --git a/tests/guard_pins.py b/tests/guard_pins.py
index e0ac504b8b..e5fbc8f3a9 100644
--- a/tests/guard_pins.py
+++ b/tests/guard_pins.py
@@ -181,6 +181,54 @@ def _runup_stops_at_the_ordinary_floor() -> bool:
     return len(at_or_below) == 1
 
 
+def _space_scope_caps_pins() -> dict[str, bool]:
+    """R11-OUTSIDE-HONEST-STARTS-RUNS: ``_space_scope`` bounds space heating by
+    the horizon's space caps, and by a total cap less the hot water beside it.
+
+    Each guard is driven with its cap set and the other unset; the uncapped
+    scope is the null control, the plain ``p_max - dhw`` headroom.
+    """
+    from heatpump_optimizer.optimizer import _space_scope
+
+    n = 4
+    opt = HeatPumpOptimizer(
+        ThermalModel(ThermalParameters()),
+        OptimizationConfig(
+            horizon_hours=n, time_step_minutes=60, target_temp=21.0,
+            min_temp=18.0, max_temp=24.0,
+        ),
+    )
+    p_max = opt.model.params.max_electrical_power
+    dhw = np.array([0.0, 1.0, 0.0, 0.0])
+    cap = np.array([p_max, 2.0, 0.5, p_max + 4.0])
+    zero = np.zeros(n)
+
+    def headroom(caps, extra) -> list[float]:
+        h = _Horizon(
+            initial_state=ThermalState(room_temperature=21.0),
+            prices=zero, outdoor_temps=zero, wind_speeds=zero,
+            precipitation=zero, solar_radiation=zero, start_time=None,
+            n_steps=n, dt=1.0, comfort_targets=np.full(n, 21.0),
+            temp_min_bounds=np.full(n, 17.0), temp_max_bounds=np.full(n, 23.0),
+            step_hours=np.arange(n) * 1.0, solar_gains=zero,
+            heat_loss_factors=np.ones(n), forecast={}, t_start=0.0,
+            power_caps=caps, power_caps_extra=extra,
+        )
+        got, scope = _space_scope(
+            opt, h, None, dhw, p_max, lambda *a, **k: 0.0, lambda *a, **k: zero)
+        return got.tolist() if [b[1] for b in scope[0]] == got.tolist() else []
+
+    plain = (p_max - dhw).tolist()
+    return {
+        "uncapped headroom is p_max less the hot water (null control)":
+            headroom(None, None) == plain,
+        "a space cap bounds the scope's headroom":
+            headroom(cap, None) == np.minimum(plain, cap).tolist(),
+        "a total cap bounds it less the hot water beside it":
+            headroom(None, cap) == np.minimum(plain, cap - dhw).tolist(),
+    }
+
+
 def _pinned_guess_respects_the_lower_bound() -> bool:
     """M11: ``min(max(out[i], low), high)`` must keep a warm start above low."""
     out = HeatPumpOptimizer._seed_pinned_guess(
@@ -1117,6 +1165,8 @@ def main() -> int:
         R.check(f"R10-ARCH-SHAPES {name}", ok)
     for name, ok in _off_step_notice_pins().items():
         R.check(f"R10-DISINFECTION-STEP-NOTICE {name}", ok)
+    for name, ok in _space_scope_caps_pins().items():
+        R.check(f"R11-OUTSIDE-HONEST-STARTS-RUNS {name}", ok)
     return R.close("GUARD PIN CHECKS")
 
 
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_humidity_with_data.BOOLOP.445c4ae4.json b/tests/mutation_ledger/killed_by/coordinator.py/_humidity_with_data.BOOLOP.445c4ae4.json
new file mode 100644
index 0000000000..7b38f4880a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_humidity_with_data.BOOLOP.445c4ae4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_humidity_with_data BOOLOP 445c4ae4",
+  "killed_by": "tests/features.py",
+  "old": "    return series if series.size and bool(np.any(np.isfinite(series))) else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return series if series.size or bool(np.any(np.isfinite(series))) else None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_humidity_with_data.RETURN_DEL.445c4ae4.json b/tests/mutation_ledger/killed_by/coordinator.py/_humidity_with_data.RETURN_DEL.445c4ae4.json
new file mode 100644
index 0000000000..7ab35b9784
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_humidity_with_data.RETURN_DEL.445c4ae4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_humidity_with_data RETURN_DEL 445c4ae4",
+  "killed_by": "tests/features.py",
+  "old": "    return series if series.size and bool(np.any(np.isfinite(series))) else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.GUARD_OFF.22c1b1ab.json b/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.GUARD_OFF.22c1b1ab.json
new file mode 100644
index 0000000000..059f58fec6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.GUARD_OFF.22c1b1ab.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:switch_weights_batch GUARD_OFF 22c1b1ab",
+  "killed_by": "tests/features.py",
+  "old": "    if level is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/running_now.GUARD_OFF.bf27f328.json b/tests/mutation_ledger/killed_by/duty_switch.py/running_now.GUARD_OFF.bf27f328.json
new file mode 100644
index 0000000000..2eb28572f9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/running_now.GUARD_OFF.bf27f328.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:running_now GUARD_OFF bf27f328",
+  "killed_by": "tests/features.py",
+  "old": "    if running is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/running_now.RETURN_DEL.574e850d.json b/tests/mutation_ledger/killed_by/duty_switch.py/running_now.RETURN_DEL.574e850d.json
new file mode 100644
index 0000000000..a2cfdbac6f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/running_now.RETURN_DEL.574e850d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:running_now RETURN_DEL 574e850d",
+  "killed_by": "tests/features.py",
+  "old": "    return running",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._grid_terms.RETURN_DEL.7a832a1f.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._grid_terms.RETURN_DEL.7a832a1f.json
new file mode 100644
index 0000000000..2d4579af54
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._grid_terms.RETURN_DEL.7a832a1f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._grid_terms RETURN_DEL 7a832a1f",
+  "killed_by": "tests/features.py",
+  "old": "        return capacity, capacity_batch",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._grid_terms.RETURN_DEL.8c52a9ac.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._grid_terms.RETURN_DEL.8c52a9ac.json
deleted file mode 100644
index 77f82b6754..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._grid_terms.RETURN_DEL.8c52a9ac.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._grid_terms RETURN_DEL 8c52a9ac",
-  "killed_by": "tests/plan_view.py",
-  "old": "        return cycling, capacity, baseline, cycling_batch, capacity_batch",
-  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_space.CLAMP_DROP.2fc0dff9.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_space.CLAMP_DROP.2fc0dff9.json
deleted file mode 100644
index 38cf99b737..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_space.CLAMP_DROP.2fc0dff9.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._solve_space CLAMP_DROP 2fc0dff9",
-  "killed_by": "tests/features.py",
-  "old": "            power = np.clip(res.x, 0.0, headroom)",
-  "reason": "Recorded by `mutation_table.py --drain`: CLAMP_DROP (`power = (res.x)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_space.CLAMP_DROP.f53c3bd9.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_space.CLAMP_DROP.f53c3bd9.json
deleted file mode 100644
index ba2a4f6ea0..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_space.CLAMP_DROP.f53c3bd9.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._solve_space CLAMP_DROP f53c3bd9",
-  "killed_by": "tests/features.py",
-  "old": "                np.maximum(0.0, h.power_caps_extra - dhw_plan),",
-  "reason": "Recorded by `mutation_table.py --drain`: CLAMP_DROP (`(0.0),`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_batch_fd_gradient.BOOLOP.91ef23e1.json b/tests/mutation_ledger/killed_by/optimizer.py/_batch_fd_gradient.BOOLOP.91ef23e1.json
new file mode 100644
index 0000000000..7bcd4042ea
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_batch_fd_gradient.BOOLOP.91ef23e1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_batch_fd_gradient BOOLOP 91ef23e1",
+  "killed_by": "tests/features.py",
+  "old": "    if lead == 0 and not free.any():",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if lead == 0 or not free.any():`) took tests/features.py from rc=0 failed=0 to rc=1 failed=25."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_batch_fd_gradient.GUARD_OFF.91ef23e1.json b/tests/mutation_ledger/killed_by/optimizer.py/_batch_fd_gradient.GUARD_OFF.91ef23e1.json
new file mode 100644
index 0000000000..7dd73959cc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_batch_fd_gradient.GUARD_OFF.91ef23e1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_batch_fd_gradient GUARD_OFF 91ef23e1",
+  "killed_by": "tests/features.py",
+  "old": "    if lead == 0 and not free.any():",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.CLAMP_DROP.baabd38e.json b/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.CLAMP_DROP.baabd38e.json
new file mode 100644
index 0000000000..2537f67e7d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.CLAMP_DROP.baabd38e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_best_runs CLAMP_DROP baabd38e",
+  "killed_by": "tests/features.py",
+  "old": "        scoped = [(np.clip(x, *_stage_box(opt, sc[0], dhw)[:2]), sc) for x, sc in zip(plans, scopes)]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`scoped = [((x), sc) for x, sc in zip(plans, scopes)]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.CLAMP_DROP.bef3bfe7.json b/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.CLAMP_DROP.bef3bfe7.json
new file mode 100644
index 0000000000..714224c3d1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.CLAMP_DROP.bef3bfe7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_best_runs CLAMP_DROP bef3bfe7",
+  "killed_by": "tests/features.py",
+  "old": "    return min((float(scores[order[0]]), *scoped[order[0]]), resolved, key=lambda c: c[0])",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return ((float(scores[order[0]]), *scoped[order[0]]))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.GUARD_OFF.7bfa6521.json b/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.GUARD_OFF.7bfa6521.json
new file mode 100644
index 0000000000..d6afe1b632
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.GUARD_OFF.7bfa6521.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_best_runs GUARD_OFF 7bfa6521",
+  "killed_by": "tests/features.py",
+  "old": "    if rescope is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.RETURN_DEL.bef3bfe7.json b/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.RETURN_DEL.bef3bfe7.json
new file mode 100644
index 0000000000..7b6b14d63e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_best_runs.RETURN_DEL.bef3bfe7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_best_runs RETURN_DEL bef3bfe7",
+  "killed_by": "tests/features.py",
+  "old": "    return min((float(scores[order[0]]), *scoped[order[0]]), resolved, key=lambda c: c[0])",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=13."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.BOOLOP.a5a6e190.json b/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.BOOLOP.a5a6e190.json
new file mode 100644
index 0000000000..8b2a963bae
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.BOOLOP.a5a6e190.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_commit_runs BOOLOP a5a6e190",
+  "killed_by": "tests/features.py",
+  "old": "    if not opt.config.cycling_cost > 0 and np.array_equal(first, relaxed[0]):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if not opt.config.cycling_cost > 0 or np.array_equal(first, relaxed[0]):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.CMP_BOUND.a5a6e190.json b/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.CMP_BOUND.a5a6e190.json
new file mode 100644
index 0000000000..4e309042f4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.CMP_BOUND.a5a6e190.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_commit_runs CMP_BOUND a5a6e190",
+  "killed_by": "tests/features.py",
+  "old": "    if not opt.config.cycling_cost > 0 and np.array_equal(first, relaxed[0]):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if not opt.config.cycling_cost >= 0 and np.array_equal(first, relaxed[0]):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.GUARD_OFF.32c4a23e.json b/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.GUARD_OFF.32c4a23e.json
new file mode 100644
index 0000000000..51904b83e3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.GUARD_OFF.32c4a23e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_commit_runs GUARD_OFF 32c4a23e",
+  "killed_by": "tests/features.py",
+  "old": "    if not _engaged(opt):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.GUARD_OFF.a5a6e190.json b/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.GUARD_OFF.a5a6e190.json
new file mode 100644
index 0000000000..e284c1cd91
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.GUARD_OFF.a5a6e190.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_commit_runs GUARD_OFF a5a6e190",
+  "killed_by": "tests/features.py",
+  "old": "    if not opt.config.cycling_cost > 0 and np.array_equal(first, relaxed[0]):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.RETURN_DEL.71e1357e.json b/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.RETURN_DEL.71e1357e.json
new file mode 100644
index 0000000000..baa26b60cf
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.RETURN_DEL.71e1357e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_commit_runs RETURN_DEL 71e1357e",
+  "killed_by": "tests/features.py",
+  "old": "        return first, scope",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_descent_pair.GUARD_OFF.32c4a23e.json b/tests/mutation_ledger/killed_by/optimizer.py/_descent_pair.GUARD_OFF.32c4a23e.json
new file mode 100644
index 0000000000..2144578491
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_descent_pair.GUARD_OFF.32c4a23e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_descent_pair GUARD_OFF 32c4a23e",
+  "killed_by": "tests/features.py",
+  "old": "    if not _engaged(opt):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_descent_pair.RETURN_DEL.80e8593e.json b/tests/mutation_ledger/killed_by/optimizer.py/_descent_pair.RETURN_DEL.80e8593e.json
new file mode 100644
index 0000000000..f2c976a428
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_descent_pair.RETURN_DEL.80e8593e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_descent_pair RETURN_DEL 80e8593e",
+  "killed_by": "tests/features.py",
+  "old": "    return partial(objective, descent=descent), partial(objective_batch, descent=descent)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_engaged.CMP_BOUND.0d0861f2.json b/tests/mutation_ledger/killed_by/optimizer.py/_engaged.CMP_BOUND.0d0861f2.json
new file mode 100644
index 0000000000..162a778d06
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_engaged.CMP_BOUND.0d0861f2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_engaged CMP_BOUND 0d0861f2",
+  "killed_by": "tests/features.py",
+  "old": "    return opt.config.cycling_cost > 0 or opt.config.clamp_planned_levels",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return opt.config.cycling_cost >= 0 or opt.config.clamp_planned_levels`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_engaged.RETURN_DEL.0d0861f2.json b/tests/mutation_ledger/killed_by/optimizer.py/_engaged.RETURN_DEL.0d0861f2.json
new file mode 100644
index 0000000000..a0caaeb577
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_engaged.RETURN_DEL.0d0861f2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_engaged RETURN_DEL 0d0861f2",
+  "killed_by": "tests/features.py",
+  "old": "    return opt.config.cycling_cost > 0 or opt.config.clamp_planned_levels",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_projection.CMP_BOUND.4bfc55a3.json b/tests/mutation_ledger/killed_by/optimizer.py/_projection.CMP_BOUND.4bfc55a3.json
new file mode 100644
index 0000000000..6baa7bf304
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_projection.CMP_BOUND.4bfc55a3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_projection CMP_BOUND 4bfc55a3",
+  "killed_by": "tests/features.py",
+  "old": "    return np.where(cycled, space, np.where(raised > hi, 0.0, raised))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return np.where(cycled, space, np.where(raised >= hi, 0.0, raised))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_projection.RETURN_DEL.4bfc55a3.json b/tests/mutation_ledger/killed_by/optimizer.py/_projection.RETURN_DEL.4bfc55a3.json
new file mode 100644
index 0000000000..fcd0917a24
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_projection.RETURN_DEL.4bfc55a3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_projection RETURN_DEL 4bfc55a3",
+  "killed_by": "tests/features.py",
+  "old": "    return np.where(cycled, space, np.where(raised > hi, 0.0, raised))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.BOOLOP.70252daa.json b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.BOOLOP.70252daa.json
new file mode 100644
index 0000000000..be24e0d98e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.BOOLOP.70252daa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_plans BOOLOP 70252daa",
+  "killed_by": "tests/features.py",
+  "old": "    if opt.config.cycling_cost > 0 and _priced_stops(opt) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if opt.config.cycling_cost > 0 or _priced_stops(opt) is not None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.CLAMP_DROP.0d5ce844.json b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.CLAMP_DROP.0d5ce844.json
new file mode 100644
index 0000000000..1092beacb8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.CLAMP_DROP.0d5ce844.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_plans CLAMP_DROP 0d5ce844",
+  "killed_by": "tests/features.py",
+  "old": "    plans = [np.clip(res.x, 0.0, headroom)]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`plans = [(res.x)]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.CMP_BOUND.70252daa.json b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.CMP_BOUND.70252daa.json
new file mode 100644
index 0000000000..9fcbda06d8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.CMP_BOUND.70252daa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_plans CMP_BOUND 70252daa",
+  "killed_by": "tests/features.py",
+  "old": "    if opt.config.cycling_cost > 0 and _priced_stops(opt) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if opt.config.cycling_cost >= 0 and _priced_stops(opt) is not None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.GUARD_OFF.70252daa.json b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.GUARD_OFF.70252daa.json
new file mode 100644
index 0000000000..e9c5cd543c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.GUARD_OFF.70252daa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_plans GUARD_OFF 70252daa",
+  "killed_by": "tests/features.py",
+  "old": "    if opt.config.cycling_cost > 0 and _priced_stops(opt) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.RETURN_DEL.4921045b.json b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.RETURN_DEL.4921045b.json
new file mode 100644
index 0000000000..2a6de7499a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.RETURN_DEL.4921045b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_plans RETURN_DEL 4921045b",
+  "killed_by": "tests/features.py",
+  "old": "    return res, plans",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_starts.CMP_BOUND.7615699d.json b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_starts.CMP_BOUND.7615699d.json
deleted file mode 100644
index 5b852dbf9f..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_starts.CMP_BOUND.7615699d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_starts CMP_BOUND 7615699d",
-  "killed_by": "tests/features.py",
-  "old": "    if not opt.config.clamp_planned_levels or first >= len(cands):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against fb9b3fc1fe16a174476c8571c40b4b7d2d3c089c: CMP_BOUND (`if not opt.config.clamp_planned_levels or first > len(cands):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_starts.GUARD_OFF.7615699d.json b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_starts.GUARD_OFF.7615699d.json
deleted file mode 100644
index 18f4f00acc..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_starts.GUARD_OFF.7615699d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_starts GUARD_OFF 7615699d",
-  "killed_by": "tests/features.py",
-  "old": "    if not opt.config.clamp_planned_levels or first >= len(cands):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against fb9b3fc1fe16a174476c8571c40b4b7d2d3c089c: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_starts.RETURN_DEL.93f85d7e.json b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_starts.RETURN_DEL.93f85d7e.json
deleted file mode 100644
index 0573f4b736..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_starts.RETURN_DEL.93f85d7e.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_starts RETURN_DEL 93f85d7e",
-  "killed_by": "tests/features.py",
-  "old": "    return [*cands, np.asarray(moved.x, dtype=float)]",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against fb9b3fc1fe16a174476c8571c40b4b7d2d3c089c: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_resolved_runs.RETURN_DEL.97ab3094.json b/tests/mutation_ledger/killed_by/optimizer.py/_resolved_runs.RETURN_DEL.97ab3094.json
new file mode 100644
index 0000000000..1daba196c1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_resolved_runs.RETURN_DEL.97ab3094.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_resolved_runs RETURN_DEL 97ab3094",
+  "killed_by": "tests/features.py",
+  "old": "    return float(scope[1](x, *args)), x, scope",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_run_bounds.RETURN_DEL.12b1b723.json b/tests/mutation_ledger/killed_by/optimizer.py/_run_bounds.RETURN_DEL.12b1b723.json
new file mode 100644
index 0000000000..ebde80a367
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_run_bounds.RETURN_DEL.12b1b723.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_run_bounds RETURN_DEL 12b1b723",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    return [b if on[i] or off[i] else (float(plan[i]), float(plan[i])) for i, b in enumerate(pinned)]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.CLAMP_DROP.6e1de491.json b/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.CLAMP_DROP.6e1de491.json
new file mode 100644
index 0000000000..5d95338890
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.CLAMP_DROP.6e1de491.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_run_plans CLAMP_DROP 6e1de491",
+  "killed_by": "tests/features.py",
+  "old": "    plans = [np.where(m & heats, np.clip(space, np.maximum(lo, floor), hi), idle) for m in masks]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`plans = [np.where(m & heats, (space), idle) for m in masks]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.CMP_BOUND.fd3d5485.json b/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.CMP_BOUND.fd3d5485.json
new file mode 100644
index 0000000000..097adbd645
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.CMP_BOUND.fd3d5485.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_run_plans CMP_BOUND fd3d5485",
+  "killed_by": "tests/features.py",
+  "old": "        forced=np.where((other > 0.0) | (lo > 0.0), 1.0, np.where(hi + other <= 0.0, 0.0, np.nan)),",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`forced=np.where((other >= 0.0) | (lo > 0.0), 1.0, np.where(hi + other <= 0.0, 0.0, np.nan)),`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8. Each of the 3 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.GUARD_OFF.741ebb88.json b/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.GUARD_OFF.741ebb88.json
new file mode 100644
index 0000000000..1d3f402a89
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.GUARD_OFF.741ebb88.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_run_plans GUARD_OFF 741ebb88",
+  "killed_by": "tests/features.py",
+  "old": "    if runs.realizable(np.where(cycled, 0.0, space), floor):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.RETURN_DEL.d87d3a8b.json b/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.RETURN_DEL.d87d3a8b.json
new file mode 100644
index 0000000000..811e1bbd94
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_run_plans.RETURN_DEL.d87d3a8b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_run_plans RETURN_DEL d87d3a8b",
+  "killed_by": "tests/features.py",
+  "old": "    return plans",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_scores_rounded.BOOLOP.b14c9b26.json b/tests/mutation_ledger/killed_by/optimizer.py/_scores_rounded.BOOLOP.b14c9b26.json
deleted file mode 100644
index b1374c373a..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/_scores_rounded.BOOLOP.b14c9b26.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_scores_rounded BOOLOP b14c9b26",
-  "killed_by": "tests/features.py",
-  "old": "    return opt.config.clamp_planned_levels and not opt._levels_relaxed",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against fb9b3fc1fe16a174476c8571c40b4b7d2d3c089c: BOOLOP (`return opt.config.clamp_planned_levels or not opt._levels_relaxed`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_scores_rounded.RETURN_DEL.b14c9b26.json b/tests/mutation_ledger/killed_by/optimizer.py/_scores_rounded.RETURN_DEL.b14c9b26.json
deleted file mode 100644
index 31baccd9da..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/_scores_rounded.RETURN_DEL.b14c9b26.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_scores_rounded RETURN_DEL b14c9b26",
-  "killed_by": "tests/features.py",
-  "old": "    return opt.config.clamp_planned_levels and not opt._levels_relaxed",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against fb9b3fc1fe16a174476c8571c40b4b7d2d3c089c: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.GUARD_OFF.34c17bb7.json b/tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.GUARD_OFF.34c17bb7.json
new file mode 100644
index 0000000000..e767cf5de3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.GUARD_OFF.34c17bb7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_shipped_and_received GUARD_OFF 34c17bb7",
+  "killed_by": "tests/features.py",
+  "old": "    if dhw is not None and opt.config.clamp_planned_levels and not descent:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.CLAMP_DROP.11d6f2e0.json b/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.CLAMP_DROP.11d6f2e0.json
new file mode 100644
index 0000000000..78d3256246
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.CLAMP_DROP.11d6f2e0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_space_scope CLAMP_DROP 11d6f2e0",
+  "killed_by": "tests/features.py",
+  "old": "        headroom = np.minimum(headroom, np.maximum(0.0, h.power_caps_extra - dhw_plan))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`headroom = (headroom)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.CLAMP_DROP.7b421902.json b/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.CLAMP_DROP.7b421902.json
new file mode 100644
index 0000000000..1373e19410
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.CLAMP_DROP.7b421902.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_space_scope CLAMP_DROP 7b421902",
+  "killed_by": "tests/features.py",
+  "old": "        headroom = np.minimum(headroom, h.power_caps)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`headroom = (headroom)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.GUARD_OFF.0429ccf6.json b/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.GUARD_OFF.0429ccf6.json
new file mode 100644
index 0000000000..20f1ee4f67
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.GUARD_OFF.0429ccf6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_space_scope GUARD_OFF 0429ccf6",
+  "killed_by": "tests/guard_pins.py",
+  "old": "    if h.power_caps is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.GUARD_OFF.41fbb204.json b/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.GUARD_OFF.41fbb204.json
new file mode 100644
index 0000000000..4c9055e6f9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.GUARD_OFF.41fbb204.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_space_scope GUARD_OFF 41fbb204",
+  "killed_by": "tests/features.py",
+  "old": "    if h.power_caps_extra is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.RETURN_DEL.b137c24a.json b/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.RETURN_DEL.b137c24a.json
new file mode 100644
index 0000000000..63f44bbdcc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_space_scope.RETURN_DEL.b137c24a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_space_scope RETURN_DEL b137c24a",
+  "killed_by": "tests/features.py",
+  "old": "    return headroom, (bounds, objective, objective_batch, opt._space_avail)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_stage_box.GUARD_OFF.80bd8784.json b/tests/mutation_ledger/killed_by/optimizer.py/_stage_box.GUARD_OFF.80bd8784.json
new file mode 100644
index 0000000000..d1f6938af0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_stage_box.GUARD_OFF.80bd8784.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_stage_box GUARD_OFF 80bd8784",
+  "killed_by": "tests/features.py",
+  "old": "    if dhw is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_stage_box.RETURN_DEL.92f7c0da.json b/tests/mutation_ledger/killed_by/optimizer.py/_stage_box.RETURN_DEL.92f7c0da.json
new file mode 100644
index 0000000000..ac038df05c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_stage_box.RETURN_DEL.92f7c0da.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_stage_box RETURN_DEL 92f7c0da",
+  "killed_by": "tests/features.py",
+  "old": "    return lo, hi, other, cycled",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=13."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.RETURN_DEL.c29a3a4d.json b/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.RETURN_DEL.c29a3a4d.json
new file mode 100644
index 0000000000..d1afa16bdd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.RETURN_DEL.c29a3a4d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_start_cost_fn RETURN_DEL c29a3a4d",
+  "killed_by": "tests/plan_view.py",
+  "old": "    return start_cost",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.start_cost.CMP_BOUND.81fa75c5.json b/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.start_cost.CMP_BOUND.81fa75c5.json
new file mode 100644
index 0000000000..c5a94cf720
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.start_cost.CMP_BOUND.81fa75c5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_start_cost_fn.start_cost CMP_BOUND 81fa75c5",
+  "killed_by": "tests/features.py",
+  "old": "        if descent or not cost > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if descent or not cost >= 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.start_cost.GUARD_OFF.81fa75c5.json b/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.start_cost.GUARD_OFF.81fa75c5.json
new file mode 100644
index 0000000000..eef24e824f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.start_cost.GUARD_OFF.81fa75c5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_start_cost_fn.start_cost GUARD_OFF 81fa75c5",
+  "killed_by": "tests/features.py",
+  "old": "        if descent or not cost > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.start_cost.RETURN_DEL.5b562f2d.json b/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.start_cost.RETURN_DEL.5b562f2d.json
new file mode 100644
index 0000000000..711056cd91
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_start_cost_fn.start_cost.RETURN_DEL.5b562f2d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_start_cost_fn.start_cost RETURN_DEL 5b562f2d",
+  "killed_by": "tests/features.py",
+  "old": "        return cost * count(power, p_min, running)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.CMP_BOUND.b0a491aa.json b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.CMP_BOUND.747c72fe.json
similarity index 51%
rename from tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.CMP_BOUND.b0a491aa.json
rename to tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.CMP_BOUND.747c72fe.json
index 318c16b96c..6ae00c8053 100644
--- a/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.CMP_BOUND.b0a491aa.json
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.CMP_BOUND.747c72fe.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_switch_cost_fn.switch_cost CMP_BOUND b0a491aa",
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_switch_cost_fn.switch_cost CMP_BOUND 747c72fe",
   "killed_by": "tests/features.py",
-  "old": "        if stops is None or dhw is None or not cost > 0:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if stops is None or dhw is None or not cost >= 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+  "old": "        if stops is None or dhw is None or not cost > 0 or descent == _UNPRICED:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if stops is None or dhw is None or not cost >= 0 or descent == _UNPRICED:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
 }
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.GUARD_OFF.b0a491aa.json b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.GUARD_OFF.747c72fe.json
similarity index 80%
rename from tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.GUARD_OFF.b0a491aa.json
rename to tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.GUARD_OFF.747c72fe.json
index 899cb46f4a..f4e8567697 100644
--- a/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.GUARD_OFF.b0a491aa.json
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.GUARD_OFF.747c72fe.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_switch_cost_fn.switch_cost GUARD_OFF b0a491aa",
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_switch_cost_fn.switch_cost GUARD_OFF 747c72fe",
   "killed_by": "tests/plan_view.py",
-  "old": "        if stops is None or dhw is None or not cost > 0:",
+  "old": "        if stops is None or dhw is None or not cost > 0 or descent == _UNPRICED:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
 }
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/count_compressor_starts.RETURN_DEL.c953de7d.json b/tests/mutation_ledger/killed_by/optimizer.py/count_compressor_starts.RETURN_DEL.c953de7d.json
deleted file mode 100644
index d404d7f819..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/count_compressor_starts.RETURN_DEL.c953de7d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:count_compressor_starts RETURN_DEL c953de7d",
-  "killed_by": "tests/features.py",
-  "old": "    return starts",
-  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/runs.py/@module.CONST.0a7cde76.json b/tests/mutation_ledger/killed_by/runs.py/@module.CONST.0a7cde76.json
new file mode 100644
index 0000000000..f5f12e186c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/@module.CONST.0a7cde76.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:<module> CONST 0a7cde76",
+  "killed_by": "tests/features.py",
+  "old": "OUT_OF_BAND = 10.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`OUT_OF_BAND = 20.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/@module.CONST.7f5866e2.json b/tests/mutation_ledger/killed_by/runs.py/@module.CONST.7f5866e2.json
new file mode 100644
index 0000000000..5b7d71bcd1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/@module.CONST.7f5866e2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:<module> CONST 7f5866e2",
+  "killed_by": "tests/features.py",
+  "old": "_SLACK = 1e-9",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`_SLACK = 0.0e-9`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/@module.CONST.b713a5a2.json b/tests/mutation_ledger/killed_by/runs.py/@module.CONST.b713a5a2.json
new file mode 100644
index 0000000000..fac764e760
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/@module.CONST.b713a5a2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:<module> CONST b713a5a2",
+  "killed_by": "tests/features.py",
+  "old": "QUANTA_PER_STEP = 4",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`QUANTA_PER_STEP = 8`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/@module.CONST.e51c2039.json b/tests/mutation_ledger/killed_by/runs.py/@module.CONST.e51c2039.json
new file mode 100644
index 0000000000..b976b0852d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/@module.CONST.e51c2039.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:<module> CONST e51c2039",
+  "killed_by": "tests/features.py",
+  "old": "_TIE_BREAK = 1e-9",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`_TIE_BREAK = 0.0e-9`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.3103be9a.json b/tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.3103be9a.json
new file mode 100644
index 0000000000..82e9874454
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.3103be9a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:_advance CLAMP_DROP 3103be9a",
+  "killed_by": "tests/features.py",
+  "old": "        outside = np.maximum(np.abs(b) - half * quantum, 0.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`outside = (np.abs(b) - half * quantum)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.faf454fb.json b/tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.faf454fb.json
new file mode 100644
index 0000000000..a0591e68f6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.faf454fb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:_advance CLAMP_DROP faf454fb",
+  "killed_by": "tests/features.py",
+  "old": "        j = np.clip(np.rint(b / quantum).astype(np.int64) + half, 0, 2 * half)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`j = (np.rint(b / quantum).astype(np.int64) + half)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_advance.CMP_BOUND.a2abb9b6.json b/tests/mutation_ledger/killed_by/runs.py/_advance.CMP_BOUND.a2abb9b6.json
new file mode 100644
index 0000000000..4c13f622b6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/_advance.CMP_BOUND.a2abb9b6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:_advance CMP_BOUND a2abb9b6",
+  "killed_by": "tests/features.py",
+  "old": "        change, paid = step[0] if dest < min_on else step[1]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`change, paid = step[0] if dest <= min_on else step[1]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_advance.GUARD_OFF.329931dd.json b/tests/mutation_ledger/killed_by/runs.py/_advance.GUARD_OFF.329931dd.json
new file mode 100644
index 0000000000..c82853e3a0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/_advance.GUARD_OFF.329931dd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:_advance GUARD_OFF 329931dd",
+  "killed_by": "tests/features.py",
+  "old": "        if not ok.any():",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_advance.RETURN_DEL.e82fb19a.json b/tests/mutation_ledger/killed_by/runs.py/_advance.RETURN_DEL.e82fb19a.json
new file mode 100644
index 0000000000..2cd18bdda4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/_advance.RETURN_DEL.e82fb19a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:_advance RETURN_DEL e82fb19a",
+  "killed_by": "tests/features.py",
+  "old": "    return new_cost, new_bal, back",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.89e6a09b.json b/tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.89e6a09b.json
new file mode 100644
index 0000000000..65d574631c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.89e6a09b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:_moves CLAMP_DROP 89e6a09b",
+  "killed_by": "tests/features.py",
+  "old": "        out += [(i, min(i + 1, states - 1), False) for i in range(min_on, states)]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`out += [(i, (i + 1), False) for i in range(min_on, states)]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.b33258f0.json b/tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.b33258f0.json
new file mode 100644
index 0000000000..84a00e6ada
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.b33258f0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:_moves CLAMP_DROP b33258f0",
+  "killed_by": "tests/features.py",
+  "old": "        out += [(i, min(i + 1, last_on), False) for i in range(min_on)]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`out += [(i, (i + 1), False) for i in range(min_on)]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.853776b6.json b/tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.853776b6.json
new file mode 100644
index 0000000000..520a00450d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.853776b6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:_moves GUARD_OFF 853776b6",
+  "killed_by": "tests/features.py",
+  "old": "    if not want == 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.edbdf8a8.json b/tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.edbdf8a8.json
new file mode 100644
index 0000000000..83e3505d83
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.edbdf8a8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:_moves GUARD_OFF edbdf8a8",
+  "killed_by": "tests/features.py",
+  "old": "    if not want == 1.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=14."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_moves.RETURN_DEL.a8227ccf.json b/tests/mutation_ledger/killed_by/runs.py/_moves.RETURN_DEL.a8227ccf.json
new file mode 100644
index 0000000000..7fec4cdf5a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/_moves.RETURN_DEL.a8227ccf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:_moves RETURN_DEL a8227ccf",
+  "killed_by": "tests/features.py",
+  "old": "    return out",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/candidates.BOOLOP.48f957af.json b/tests/mutation_ledger/killed_by/runs.py/candidates.BOOLOP.48f957af.json
new file mode 100644
index 0000000000..d3528f5510
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/candidates.BOOLOP.48f957af.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:candidates BOOLOP 48f957af",
+  "killed_by": "tests/features.py",
+  "old": "        if tracked and band > BANDS[-1]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if tracked or band > BANDS[-1]:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/candidates.CMP_BOUND.48f957af.json b/tests/mutation_ledger/killed_by/runs.py/candidates.CMP_BOUND.48f957af.json
new file mode 100644
index 0000000000..54a87f627e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/candidates.CMP_BOUND.48f957af.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:candidates CMP_BOUND 48f957af",
+  "killed_by": "tests/features.py",
+  "old": "        if tracked and band > BANDS[-1]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if tracked and band >= BANDS[-1]:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/candidates.GUARD_OFF.48f957af.json b/tests/mutation_ledger/killed_by/runs.py/candidates.GUARD_OFF.48f957af.json
new file mode 100644
index 0000000000..1b6ef09c8b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/candidates.GUARD_OFF.48f957af.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:candidates GUARD_OFF 48f957af",
+  "killed_by": "tests/features.py",
+  "old": "        if tracked and band > BANDS[-1]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/candidates.GUARD_OFF.d75cfe9e.json b/tests/mutation_ledger/killed_by/runs.py/candidates.GUARD_OFF.d75cfe9e.json
new file mode 100644
index 0000000000..fddb10c238
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/candidates.GUARD_OFF.d75cfe9e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:candidates GUARD_OFF d75cfe9e",
+  "killed_by": "tests/features.py",
+  "old": "        if not any(np.array_equal(mask, m) for m in masks):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/candidates.RETURN_DEL.97969b54.json b/tests/mutation_ledger/killed_by/runs.py/candidates.RETURN_DEL.97969b54.json
new file mode 100644
index 0000000000..4f269a61a8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/candidates.RETURN_DEL.97969b54.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:candidates RETURN_DEL 97969b54",
+  "killed_by": "tests/features.py",
+  "old": "    return masks",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.BOOLOP.3f04b002.json b/tests/mutation_ledger/killed_by/runs.py/commit.BOOLOP.3f04b002.json
new file mode 100644
index 0000000000..5ab295238b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/commit.BOOLOP.3f04b002.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit BOOLOP 3f04b002",
+  "killed_by": "tests/features.py",
+  "old": "        np.all(np.abs(walk) <= half * quantum + _SLACK) and abs(walk[-1]) <= f * dt / 2.0 + _SLACK)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`np.all(np.abs(walk) <= half * quantum + _SLACK) or abs(walk[-1]) <= f * dt / 2.0 + _SLACK)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.CLAMP_DROP.66553920.json b/tests/mutation_ledger/killed_by/runs.py/commit.CLAMP_DROP.66553920.json
new file mode 100644
index 0000000000..d312d90153
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/commit.CLAMP_DROP.66553920.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit CLAMP_DROP 66553920",
+  "killed_by": "tests/features.py",
+  "old": "    level = np.minimum(np.maximum(q, f), cap)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`level = (np.maximum(q, f))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.CLAMP_DROP.a4b85c7c.json b/tests/mutation_ledger/killed_by/runs.py/commit.CLAMP_DROP.a4b85c7c.json
new file mode 100644
index 0000000000..8af8759ea0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/commit.CLAMP_DROP.a4b85c7c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit CLAMP_DROP a4b85c7c",
+  "killed_by": "tests/features.py",
+  "old": "    ending = cost + fine * np.maximum(np.abs(bal) - f * dt / 2.0, 0.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`ending = cost + fine * (np.abs(bal) - f * dt / 2.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.056c259e.json b/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.056c259e.json
new file mode 100644
index 0000000000..556f4a03bc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.056c259e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit CMP_BOUND 056c259e",
+  "killed_by": "tests/features.py",
+  "old": "        asked = bool(q[k] > 0.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`asked = bool(q[k] >= 0.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.344874f5.json b/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.344874f5.json
new file mode 100644
index 0000000000..0be4279f3e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.344874f5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit CMP_BOUND 344874f5",
+  "killed_by": "tests/features.py",
+  "old": "    want = np.where(np.isnan(want) & (cap < f - _SLACK), 0.0, want)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`want = np.where(np.isnan(want) & (cap <= f - _SLACK), 0.0, want)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.d914b133.json b/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.d914b133.json
new file mode 100644
index 0000000000..4bc0e47f2f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.d914b133.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit CMP_BOUND d914b133",
+  "killed_by": "tests/features.py",
+  "old": "        mask[k] = u < min_on",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`mask[k] = u <= min_on`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.RETURN_DEL.1ec24ddf.json b/tests/mutation_ledger/killed_by/runs.py/commit.RETURN_DEL.1ec24ddf.json
new file mode 100644
index 0000000000..fbece04c55
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/commit.RETURN_DEL.1ec24ddf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit RETURN_DEL 1ec24ddf",
+  "killed_by": "tests/features.py",
+  "old": "    return mask, tracked",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/edge_count.CMP_BOUND.503f62fe.json b/tests/mutation_ledger/killed_by/runs.py/edge_count.CMP_BOUND.503f62fe.json
new file mode 100644
index 0000000000..f4a8a70730
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/edge_count.CMP_BOUND.503f62fe.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:edge_count CMP_BOUND 503f62fe",
+  "killed_by": "tests/features.py",
+  "old": "    on = np.asarray(total, dtype=float) > MIN_RUNNING_DRAW_KW",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`on = np.asarray(total, dtype=float) >= MIN_RUNNING_DRAW_KW`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/edge_count.RETURN_DEL.82a582db.json b/tests/mutation_ledger/killed_by/runs.py/edge_count.RETURN_DEL.82a582db.json
new file mode 100644
index 0000000000..7aa961fefd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/edge_count.RETURN_DEL.82a582db.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:edge_count RETURN_DEL 82a582db",
+  "killed_by": "tests/features.py",
+  "old": "    return int(np.sum(on & ~np.r_[bool(running), on[:-1]]))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/floor_kw.CLAMP_DROP.23807357.json b/tests/mutation_ledger/killed_by/runs.py/floor_kw.CLAMP_DROP.23807357.json
new file mode 100644
index 0000000000..ecd2a6979d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/floor_kw.CLAMP_DROP.23807357.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:floor_kw CLAMP_DROP 23807357",
+  "killed_by": "tests/features.py",
+  "old": "    return max(float(floor), MIN_RUNNING_DRAW_KW)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return (float(floor))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/floor_kw.RETURN_DEL.23807357.json b/tests/mutation_ledger/killed_by/runs.py/floor_kw.RETURN_DEL.23807357.json
new file mode 100644
index 0000000000..61fcf26542
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/floor_kw.RETURN_DEL.23807357.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:floor_kw RETURN_DEL 23807357",
+  "killed_by": "tests/features.py",
+  "old": "    return max(float(floor), MIN_RUNNING_DRAW_KW)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/realizable.CMP_BOUND.7069a02a.json b/tests/mutation_ledger/killed_by/runs.py/realizable.CMP_BOUND.7069a02a.json
new file mode 100644
index 0000000000..863f11d0a2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/realizable.CMP_BOUND.7069a02a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:realizable CMP_BOUND 7069a02a",
+  "killed_by": "tests/features.py",
+  "old": "    return bool(np.all((q <= 0.0) | (q >= floor_kw(floor) - _SLACK)))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return bool(np.all((q < 0.0) | (q >= floor_kw(floor) - _SLACK)))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/realizable.RETURN_DEL.7069a02a.json b/tests/mutation_ledger/killed_by/runs.py/realizable.RETURN_DEL.7069a02a.json
new file mode 100644
index 0000000000..dd3eb2a59f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/realizable.RETURN_DEL.7069a02a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:realizable RETURN_DEL 7069a02a",
+  "killed_by": "tests/features.py",
+  "old": "    return bool(np.all((q <= 0.0) | (q >= floor_kw(floor) - _SLACK)))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/running_share.CLAMP_DROP.63c654e6.json b/tests/mutation_ledger/killed_by/runs.py/running_share.CLAMP_DROP.63c654e6.json
new file mode 100644
index 0000000000..0a5034a776
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/running_share.CLAMP_DROP.63c654e6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:running_share CLAMP_DROP 63c654e6",
+  "killed_by": "tests/features.py",
+  "old": "    return np.clip(np.asarray(total, dtype=float) / floor_kw(floor), 0.0, 1.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return (np.asarray(total, dtype=float) / floor_kw(floor))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/running_share.RETURN_DEL.63c654e6.json b/tests/mutation_ledger/killed_by/runs.py/running_share.RETURN_DEL.63c654e6.json
new file mode 100644
index 0000000000..cee456d40c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/running_share.RETURN_DEL.63c654e6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:running_share RETURN_DEL 63c654e6",
+  "killed_by": "tests/features.py",
+  "old": "    return np.clip(np.asarray(total, dtype=float) / floor_kw(floor), 0.0, 1.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/start_count.RETURN_DEL.59dd2f98.json b/tests/mutation_ledger/killed_by/runs.py/start_count.RETURN_DEL.59dd2f98.json
new file mode 100644
index 0000000000..881cfef107
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/start_count.RETURN_DEL.59dd2f98.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:start_count RETURN_DEL 59dd2f98",
+  "killed_by": "tests/features.py",
+  "old": "    return float(start_count_batch(np.asarray(total, dtype=float)[None, :], floor, running)[0])",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/start_count_batch.CLAMP_DROP.0275c9ad.json b/tests/mutation_ledger/killed_by/runs.py/start_count_batch.CLAMP_DROP.0275c9ad.json
new file mode 100644
index 0000000000..b476743c7a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/start_count_batch.CLAMP_DROP.0275c9ad.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:start_count_batch CLAMP_DROP 0275c9ad",
+  "killed_by": "tests/features.py",
+  "old": "    needs = np.clip(rows / MIN_RUNNING_DRAW_KW, 0.0, 1.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`needs = (rows / MIN_RUNNING_DRAW_KW)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=18."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/start_count_batch.RETURN_DEL.5cb47597.json b/tests/mutation_ledger/killed_by/runs.py/start_count_batch.RETURN_DEL.5cb47597.json
new file mode 100644
index 0000000000..a0e9def044
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/start_count_batch.RETURN_DEL.5cb47597.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:start_count_batch RETURN_DEL 5cb47597",
+  "killed_by": "tests/features.py",
+  "old": "    return count",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/steps_at_least.CLAMP_DROP.e5f3ee1d.json b/tests/mutation_ledger/killed_by/runs.py/steps_at_least.CLAMP_DROP.e5f3ee1d.json
new file mode 100644
index 0000000000..34cd32cef1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/steps_at_least.CLAMP_DROP.e5f3ee1d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:steps_at_least CLAMP_DROP e5f3ee1d",
+  "killed_by": "tests/features.py",
+  "old": "    return max(1, int(np.ceil(span.total_seconds() / 3600.0 / dt_hours - _SLACK)))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return (1)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/steps_at_least.RETURN_DEL.e5f3ee1d.json b/tests/mutation_ledger/killed_by/runs.py/steps_at_least.RETURN_DEL.e5f3ee1d.json
new file mode 100644
index 0000000000..030c5b83f8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/steps_at_least.RETURN_DEL.e5f3ee1d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:steps_at_least RETURN_DEL e5f3ee1d",
+  "killed_by": "tests/features.py",
+  "old": "    return max(1, int(np.ceil(span.total_seconds() / 3600.0 / dt_hours - _SLACK)))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/@module.CONST.a4245540.json b/tests/mutation_ledger/survivor_triage/optimizer.py/@module.CONST.a4245540.json
new file mode 100644
index 0000000000..f08d48722c
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/@module.CONST.a4245540.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:<module> CONST a4245540",
+  "old": "_RESOLVED_CANDIDATES = 2",
+  "reason": "Survived tests/features.py, the one driver run, under `mutation_table.py --pin-killed --scripts tests/features.py` at 3f0149a81b (R11-OUTSIDE-HONEST-STARTS-RUNS, repair round 4; pull request 3602, the build of Bankaifan's pull request 3529); the other drivers of the file's closure were not run. Re-solving four candidates instead of two can only lower the lowest score the stage ships, so every selection check still holds, and no check counts the L-BFGS-B runs a stage call makes. A killing check is in R11-OUTSIDE-HONEST-STARTS-RUNS-P2's brief (item i).",
+  "verdict": "gap"
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/_projection.GUARD_OFF.ab0c3e65.json b/tests/mutation_ledger/survivor_triage/optimizer.py/_projection.GUARD_OFF.ab0c3e65.json
new file mode 100644
index 0000000000..0a4a9ff55a
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/_projection.GUARD_OFF.ab0c3e65.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_projection GUARD_OFF ab0c3e65",
+  "old": "    if opt.config.clamp_planned_levels:",
+  "reason": "Survived tests/features.py, the one driver run, under `mutation_table.py --pin-killed --scripts tests/features.py` at 3f0149a81b (R11-OUTSIDE-HONEST-STARTS-RUNS, repair round 4; pull request 3602, the build of Bankaifan's pull request 3529); the other drivers of the file's closure were not run. With the clamped arm off, a clamped install's candidate (1) is built by the duty-cycle arm (each level raised to the floor against its cap). On the block's clamped fixtures the stage ships a committed candidate either way, and no check compares a clamped install's projection with `_realize_draw`'s. A check on `_projection` alone, clamped against unclamped on one relaxed plan with a sub-floor level beside hot water, would kill it; none is recorded.",
+  "verdict": "gap"
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/_relaxed_plans.CLAMP_DROP.b076955e.json b/tests/mutation_ledger/survivor_triage/optimizer.py/_relaxed_plans.CLAMP_DROP.b076955e.json
new file mode 100644
index 0000000000..474642483b
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/_relaxed_plans.CLAMP_DROP.b076955e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_plans CLAMP_DROP b076955e",
+  "old": "            pair[0], [np.minimum(x, free_room) for x in starts], free[0], args=(dhw_plan,),",
+  "reason": "Survived tests/features.py, the one driver run, under `mutation_table.py --pin-killed --scripts tests/features.py` at 3f0149a81b (R11-OUTSIDE-HONEST-STARTS-RUNS, repair round 4; pull request 3602, the build of Bankaifan's pull request 3529); the other drivers of the file's closure were not run. The mutant hands the second descent's multi-start its starts unclipped to the bound no stop cuts. The plan it returns is clipped to that bound on the next line and L-BFGS-B projects a start into its bounds, so no shipped plan moved on the block's priced installs; not shown equivalent on a start far outside the bound. A check that reads the starts the second multi-start is handed would kill it; none is recorded.",
+  "verdict": "gap"
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/_run_bounds.CMP_BOUND.ac17e14b.json b/tests/mutation_ledger/survivor_triage/optimizer.py/_run_bounds.CMP_BOUND.ac17e14b.json
new file mode 100644
index 0000000000..a6e1648830
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/_run_bounds.CMP_BOUND.ac17e14b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_run_bounds CMP_BOUND ac17e14b",
+  "old": "    on, off = plan >= floor - 1e-9, plan <= 0.0",
+  "reason": "Survived tests/features.py, the one driver run, under `mutation_table.py --pin-killed --scripts tests/features.py` at 3f0149a81b (R11-OUTSIDE-HONEST-STARTS-RUNS, repair round 4; pull request 3602, the build of Bankaifan's pull request 3529); the other drivers of the file's closure were not run. `_run_bounds` reads a level as on at the floor less 1e-9 and as off at zero; the variants differ only for a level exactly on either edge, and no candidate of the block's fixtures holds one (a committed step is at the floor or above, an idle one at zero or at its pin). A check that hands `_run_bounds` a plan with a level at the floor less 1e-9 would kill the first; none is recorded.",
+  "verdict": "gap"
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/_run_plans.CMP_BOUND.eaf0d1e3.json b/tests/mutation_ledger/survivor_triage/optimizer.py/_run_plans.CMP_BOUND.eaf0d1e3.json
new file mode 100644
index 0000000000..cf478b7720
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/_run_plans.CMP_BOUND.eaf0d1e3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_run_plans CMP_BOUND eaf0d1e3",
+  "old": "    heats = (hi >= floor) & ((other <= 0.0) | (space >= floor / 2.0))",
+  "reason": "Survived tests/features.py, the one driver run, under `mutation_table.py --pin-killed --scripts tests/features.py` at 3f0149a81b (R11-OUTSIDE-HONEST-STARTS-RUNS, repair round 4; pull request 3602, the build of Bankaifan's pull request 3529); the other drivers of the file's closure were not run. The heats predicate's three boundaries: a cap exactly at the floor, hot water exactly at zero, a space level exactly at half the floor. One of the three variants is killed by tests/features.py; the fixtures hold no step on the other two equalities. A killing check is in R11-OUTSIDE-HONEST-STARTS-RUNS-P2's brief (item i).",
+  "verdict": "gap"
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/_stage_box.CLAMP_DROP.60ed0d0d.json b/tests/mutation_ledger/survivor_triage/optimizer.py/_stage_box.CLAMP_DROP.60ed0d0d.json
new file mode 100644
index 0000000000..dc1ffdba89
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/_stage_box.CLAMP_DROP.60ed0d0d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_stage_box CLAMP_DROP 60ed0d0d",
+  "old": "        hi = np.minimum(hi, np.maximum(p_max - other, 0.0))",
+  "reason": "Survived tests/features.py, the one driver run, under `mutation_table.py --pin-killed --scripts tests/features.py` at 3f0149a81b (R11-OUTSIDE-HONEST-STARTS-RUNS, repair round 4; pull request 3602, the build of Bankaifan's pull request 3529); the other drivers of the file's closure were not run. The stage box's tank room: the space cap less what the tank draws, never under zero. The block's solves beside hot water never hand the stage a cap above that room, so dropping either clamp moves no candidate. A killing check is in R11-OUTSIDE-HONEST-STARTS-RUNS-P2's brief (item i).",
+  "verdict": "gap"
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/_stage_box.CLAMP_DROP.b07febdf.json b/tests/mutation_ledger/survivor_triage/optimizer.py/_stage_box.CLAMP_DROP.b07febdf.json
new file mode 100644
index 0000000000..5b7557a111
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/_stage_box.CLAMP_DROP.b07febdf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_stage_box CLAMP_DROP b07febdf",
+  "old": "        lo = np.minimum(lo, hi)",
+  "reason": "Survived tests/features.py, the one driver run, under `mutation_table.py --pin-killed --scripts tests/features.py` at 3f0149a81b (R11-OUTSIDE-HONEST-STARTS-RUNS, repair round 4; pull request 3602, the build of Bankaifan's pull request 3529); the other drivers of the file's closure were not run. The lower bound held under the tank room. It binds only where a forced-on space pin sits beside a charge that leaves less than the pin's level, and no fixture of the block pins space beside hot water at the stage. A check on `_stage_box` with such a pin would kill it; none is recorded.",
+  "verdict": "gap"
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/_stage_box.CMP_BOUND.ccc99b4a.json b/tests/mutation_ledger/survivor_triage/optimizer.py/_stage_box.CMP_BOUND.ccc99b4a.json
new file mode 100644
index 0000000000..6e46eb9c1e
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/_stage_box.CMP_BOUND.ccc99b4a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_stage_box CMP_BOUND ccc99b4a",
+  "old": "    cycled = (not opt.config.clamp_planned_levels) & (other <= 0.0) & (hi < runs.floor_kw(p_min))",
+  "reason": "Survived tests/features.py, the one driver run, under `mutation_table.py --pin-killed --scripts tests/features.py` at 3f0149a81b (R11-OUTSIDE-HONEST-STARTS-RUNS, repair round 4; pull request 3602, the build of Bankaifan's pull request 3529); the other drivers of the file's closure were not run. The `cycled` reading's two boundaries: hot water exactly at zero and a cap exactly at the floor. With `other < 0.0` no step is ever read as cycled, yet the block's capped fixture (the named mutant CYCLED_KEPT, killed) keeps its capped steps through another arm of the same candidates; with `hi <= floor` a cap exactly at the floor would cycle. A check on `_stage_box`'s fourth value at a cap under, at and above the floor would kill both; none is recorded.",
+  "verdict": "gap"
+}
diff --git a/tests/mutation_ledger/survivor_triage/runs.py/commit.CLAMP_DROP.54895a3e.json b/tests/mutation_ledger/survivor_triage/runs.py/commit.CLAMP_DROP.54895a3e.json
new file mode 100644
index 0000000000..7247f523cd
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/runs.py/commit.CLAMP_DROP.54895a3e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit CLAMP_DROP 54895a3e",
+  "old": "    fine = OUT_OF_BAND * max(float(np.max(np.abs(price))), 1e-6)",
+  "reason": "Survived tests/features.py, the one driver run, under `mutation_table.py --pin-killed --scripts tests/features.py` at 3f0149a81b (R11-OUTSIDE-HONEST-STARTS-RUNS, repair round 4; pull request 3602, the build of Bankaifan's pull request 3529); the other drivers of the file's closure were not run. The floor of 1e-6 under the out-of-band price matters only where every price of the horizon is zero: there the mutant's penalty is zero and a balance outside the band is free. No fixture commits at an all-zero price with a mask that would leave its band. A leaf check like the block's late-cheap trickle at price zero and a start price would kill it; none is recorded.",
+  "verdict": "gap"
+}
diff --git a/tests/mutation_ledger/survivor_triage/runs.py/commit.CMP_BOUND.3f04b002.json b/tests/mutation_ledger/survivor_triage/runs.py/commit.CMP_BOUND.3f04b002.json
new file mode 100644
index 0000000000..75948d7be3
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/runs.py/commit.CMP_BOUND.3f04b002.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit CMP_BOUND 3f04b002",
+  "old": "        np.all(np.abs(walk) <= half * quantum + _SLACK) and abs(walk[-1]) <= f * dt / 2.0 + _SLACK)",
+  "reason": "Survived tests/features.py, the one driver run, under `mutation_table.py --pin-killed --scripts tests/features.py` at 3f0149a81b (R11-OUTSIDE-HONEST-STARTS-RUNS, repair round 4; pull request 3602, the build of Bankaifan's pull request 3529); the other drivers of the file's closure were not run. The two comparisons of `tracked` against the band edge and the end balance carry the float slack, so the variants differ only for a walk exactly at an edge plus 1e-9; the leaf fixtures sit exactly on the band edge (2.0 and 6.0 floor steps), inside the slack under both forms. Equivalent for every walk not within 1e-9 of that sum; not shown for one that is.",
+  "verdict": "gap"
+}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 6c3a7f099d..92990e3b2a 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,17 +1,17 @@
 {
- "class_excess_loc": 17446,
+ "class_excess_loc": 17407,
  "const_modules_over_50": 3,
  "coordinator_attrs": 136,
  "coordinator_multiassigned_attrs": 104,
  "coordinator_private_reach": 0,
  "dead_methods": 0,
  "dead_top_level_symbols": 1,
- "duplication_copies": 9,
+ "duplication_copies": 8,
  "functions_cc_over_15": 26,
  "functions_cc_over_25": 7,
  "import_cycle_modules": 0,
  "max_cc": 44,
- "max_class_loc": 7885,
+ "max_class_loc": 7877,
  "max_method_loc": 373,
  "methods_over_150": 14,
  "methods_over_200": 7,
diff --git a/tests/validate.py b/tests/validate.py
index 6ab94d6ab8..5511924e64 100644
--- a/tests/validate.py
+++ b/tests/validate.py
@@ -8,8 +8,8 @@ from profiles import prices, weather, house, DT, N
 from profiles import solve_inputs  # noqa: E402
 from heatpump_optimizer.thermal_model import (
     ThermalModel, ThermalParameters, ThermalState, WeatherSeries)
-from heatpump_optimizer.optimizer import (
-    HeatPumpOptimizer, OptimizationConfig, count_compressor_starts)
+from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
+from heatpump_optimizer.runs import edge_count
 from heatpump_optimizer.dhw_schedule import parse_windows, hour_in_windows
 
 START = datetime(2026,1,15,0,0)
@@ -170,9 +170,7 @@ def run(scen, price_p, weather_p, two_zone=False, dhw=True, start=START, **over)
     # does not chatter does not need one, and the penalty is not free: it buys
     # smoothness with savings.
     starts = r.compressor_starts
-    total_starts = starts + count_compressor_starts(
-        np.asarray(r.dhw_power_schedule or [])
-    )
+    total_starts = starts + edge_count(np.asarray(r.dhw_power_schedule or []))
     if total_starts > N * DT:  # more than one start per hour of horizon
         issue(scen, f"plan chatters: {total_starts} compressor starts in "
                     f"{N*DT:.0f} h")

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
