# Review packet #3633
head: 39174541fd3707da591f62d5c08e21af06235d0f
base: b98c78e0f6144a5ea5b48a032e30bf2d085c2d61

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=133669739765 success
arch-score / arch-score id=133669599958 success
arm id=133669218736 skipped
budget-raise-gate / budget-raise-gate id=133669600297 success
cancel-superseded id=133669170595 success
codeql id=133669602001 skipped
codeql / Analyze (actions) id=133669546109 success
codeql / Analyze (javascript-typescript) id=133669546083 success
codeql / Analyze (python) id=133669547126 success
gate id=133693317030 success
governance id=133669601460 skipped
governance / env-matrix id=133669545964 success
governance / instrument-self-tests id=133669545824 success
governance / policy-docs id=133669545854 success
governance / record id=133669548317 skipped
governance / wave-script id=133669545862 success
hassfest id=133669601670 skipped
hassfest / hassfest id=133669545668 success
kernel-points id=133669602911 skipped
pr-contract id=133670442639 skipped
pr-contract / pr-contract id=133691760280 success
prelude id=133669171001 success
refresh id=133669170985 success
sweep-self id=133699525010 skipped
tests id=133669602210 skipped
tests / arch-instrument id=133670105173 success
tests / briefs id=133669545658 success
tests / browser id=133670105344 success
tests / ci-ratchet id=133685165553 skipped
tests / claims-autofix id=133678504990 skipped
tests / closure-scope id=133669545545 success
tests / closures id=133670105363 success
tests / closures-autofix id=133680323393 skipped
tests / coverage id=133670105368 success
tests / coverage-ratchet id=133685162767 success
tests / fast (3.14) id=133670105361 success
tests / graders-head-copy id=133685162878 success
tests / lane-proofs id=133685162783 success
tests / mutation id=133669545887 success
tests / mutation-autofix id=133670433844 skipped
tests / mutation-pins id=133670434460 skipped
tests / nightly-ha id=133670107327 skipped
tests / nightly-status id=133669545721 failure
tests / replay id=133670107443 skipped
tests / typing id=133670105284 success
validate id=133669601621 skipped
validate / validate-hacs id=133669545817 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 294410ff: R11-PRE-ROUND-CHECK-GATE: R11-PRE-ROUND-CHECK-GATE resolved on origin/handoff/audit-r10-roster
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: SCOPED -- 2 script(s) run, 31 scoped out.
             no segment of this names a program this check knows
  ok         python3 tools/audit/seat/roster_lib.py --self-test
             `tools/audit/seat/roster_lib.py` is in the tree at this head
  ok         python3 tools/audit/seat/roster_edit.py --self-test
             `tools/audit/seat/roster_edit.py` is in the tree at this head
  ok         node tools/policy/check-wave-script.mjs
             `tools/policy/check-wave-script.mjs` is in the tree at this head
  ok         .claude/workflows/audit-plan.js
             `.claude/workflows/audit-plan.js` is in the tree at this head
  ok         node tools/policy/brief_lint.mjs
             `tools/policy/brief_lint.mjs` is in the tree at this head
  ok         python3 tools/audit/check_scopes.py --repo . --self-test
             `tools/audit/check_scopes.py` is in the tree at this head

FIGURES: 6 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: delta (later round over the reviewed head 2061e87b067922853a5f890dad9ea21d835f593e)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at 2061e87b067922853a5f890dad9ea21d835f593e
Fix review: blocked 2061e87b067922853a5f890dad9ea21d835f593e merge-conflict: tools/audit/seat/roster_edit.py conflicts with origin/main 2c911234e1 (#3657's CONVERGENCE_FIELDS against this PR's gates_finders in set-field)

bus-nonce: e77914aa6a70ac7b56f89636d491c6d1

## Block

- merge-conflict (fix-review.md step 13). `git merge-tree --write-tree origin/main 2061e87b067922853a5f890dad9ea21d835f593e` exits 1 against origin/main 2c911234e1 with `CONFLICT (content): Merge conflict in tools/audit/seat/roster_edit.py` (ev/merge-tree.txt). The file is not a claim file, so no claimnotes driver is involved. Main gained #3657 after this head's merge base 6f422812d5. #3657 (commit 30d545ce63 and those after it) changed the same two lines this PR changes. In the usage text, `set-field <group> <...|class>` became the list with `|found_by|owned_by|caused_by|family|cm_kind|parent|follows`, where this PR adds `|gates_finders`. `SET_FIELDS` became `(...) + roster_lib.CONVERGENCE_FIELDS`, where this PR appends `"gates_finders"` (ev/conflict-hunks.txt). The resolution keeps both sides. In the code: `SET_FIELDS = ("source", "hotfix", "hotfix_by", "savings", "savings_source", "class", "gates_finders") + roster_lib.CONVERGENCE_FIELDS`, and the usage line lists both sets of fields. `op_set_field`'s branches auto-merge: this PR's `elif field in ("hotfix", "gates_finders")` and main's `elif field in roster_lib.CONVERGENCE_FIELDS` share no field. After the merge, the roster_edit self-test (with this PR's two gates_finders arms) and the check_scopes self-test must be re-run. Nothing else in the delta blocks. A re-review is the merge commit plus those two re-runs.

## Findings

- Note: figure-stale: the body's `## Figures` says `node tools/policy/check-wave-script.mjs` at this head prints `223 passed, 0 failed`. At 2061e87b06 it prints `249 passed, 0 failed` (ev/self-tests.txt). The 26 extra arms came in with the main merges; the 223 was measured at the code head a59eafe204/81119045726e. The body should say the count it measured at the head it names. The same holds for "Against part 3's audit-plan.js it also printed 223", which I did not re-derive. Carry: R11-PRE-ROUND-CHECK-GATE

## Evidence

- Head reviewed: 2061e87b067922853a5f890dad9ea21d835f593e (ev/HEAD.txt), the PR's head and the body's `## Head`. Round: later, over the reviewed head 416280f5c2e4e4a8274c32246128d2e7a1dd48e2. The scope is the delta and the previous verdict's items (packet `## Review scope: delta`). There is no custom_components/ delta, so the scope is not widened.
- Previous verdict, block 1 (carry-missing: own-group): resolved by the body. `## Forward-carry` now names the split "**pending the orchestrator's ruling** on the split; no plan names a part 3 yet", which is the cure the previous verdict named. It carries `Carry: R11-PRE-ROUND-CHECK-GATE`. The carry_audit at the head reads `1 routed, 0 unrouted, 0 bad destination(s)` (ev/review-packet.md).
- Previous verdict, block 2 (surviving mutant C7): resolved. The arm "a null, absent, blank or non-string reviewer or evaluator is refused" now tries `1` and `["x"]` (check_scopes.py diff). I re-ran it at this head (ev/mutant-C7.txt), applying each mutant alone to `check_scopes.py:342` and restoring it. RESULT C7 `norm(str(ev.get(k) or ""))`: KILLED (rc 1). RESULT C7b `norm(ev.get(k, ""))`: KILLED (rc 1). RESULT NULL: rc 0. The worktree was clean afterwards.
- Previous verdict, note 1 (a destination ref that does not exist): resolved. The body now names refs/heads/handoff-wip/r11-pre-round-check-gate-p3 at 9fb327ecb3, and `git ls-remote` prints `9fb327ecb3d544822071daee6201ff09f4827793 refs/heads/handoff-wip/r11-pre-round-check-gate-p3`.
- Previous verdict, note 2 (an undisclosed policy edit): resolved. The body's "Policy, minimal" bullet now lists the deletion of "read-only on code" as a change to what the seat may do, awaiting the owner's approving review.
- Main-merge resolutions, checked against `git diff 6f422812d5 2061e87b06`: tools/audit/check_scopes.py keeps main's `open_cards_cli`/`json_or_none` (part 1, #3620) and this PR's `architect_groups_report`/`p3_input` once each. Each def appears once (lines 426, 440, 449, 457, 492). `open_cards_cli`'s scratch repository now also carries a roster with a marked G1 and passes `--roster-ref`, so the card-half arms measure the card half alone. tools/policy/check-wave-script.mjs: the only delta against the base is a three-line comment above the `OPEN`/`MOVES` stubs, with no duplicated declaration. The grader runs green (249 passed, 0 failed).
- Figure block: `python3 tools/pr/figure_block.py verify <body block> --base 6f422812d5d8b918beace0283419c153f6df66ce --head 2061e87b067922853a5f890dad9ea21d835f593e` printed `figure_block verify: 1 block(s), 0 refused`, rc 0 (ev/figure-verify.txt), so the hand-rendered scope-line block `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` matches. Its base is the PR's base sha 6f422812d5, which is also the merge base with the base branch at the time of the merge.
- Self-tests re-run at the head (ev/self-tests.txt): `roster_lib self-test: 95 checks, 0 failed`; `roster_edit self-test: 313 checks, 0 failed`; `check_scopes.py --repo . --self-test` rc 0 with `evaluation arms: 66/66 held`, which matches the body; `node tools/policy/brief_lint.mjs` rc 0; `node tools/policy/check-wave-script.mjs` `249 passed, 0 failed`, which differs from the body (see Findings).
- CI: `merge_train.py classify 2061e87b06... --pr 3633` printed `WAIT 2061e87b067922853a5f890dad9ea21d835f593e pending: gate red: none` (ev/classify.txt). No owed red exists, so no `## Red checks` answer is owed. tests / nightly-status was failure in the packet's digest, but it is not in `merge_train.py owed-reds`. I stopped waiting once the merge conflict decided the verdict.
- VERSION, the manifest version, RELEASE_NOTES.md and the claim files are untouched in the three-dot diff (9 files: architect-planner.md, delivery/3633.md, check_scopes.py, check_scopes.py.md, roster_edit.py, roster_lib.py, brief_lint.mjs, check-wave-script.mjs, shape-defects.json).
- review_packet refusals at render: `structure: head does not merge cleanly with origin/main` (the same conflict) and `introduced-red: unreadable: instrument-self-tests in_progress` (still pending by classify; no red).

## Delta diff: git diff 2061e87b067922853a5f890dad9ea21d835f593e 39174541fd3707da591f62d5c08e21af06235d0f
diff --git a/.claude/workflows/audit-find.js b/.claude/workflows/audit-find.js
index a614582aec..1041c4a3c0 100644
--- a/.claude/workflows/audit-find.js
+++ b/.claude/workflows/audit-find.js
@@ -49,7 +49,7 @@ if (!scopes || typeof scopes !== 'object') throw new Error('args.scopes is requi
 if (from !== undefined && from !== 'intake') throw new Error(`args.from is "intake" or absent, not ${JSON.stringify(from)}`)
 if (from && box) throw new Error('args.box and args.from are exclusive: a box runs finders, intake gathers every box')
 
-const DIMS = ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12', 'D13', 'D14', 'D15']
+const DIMS = ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12', 'D13', 'D14', 'D15', 'D16', 'D17']
 // D11 audits the process itself, so it needs `.git` and the API: a worktree, not
 // an export. D13 reads the same sources and needs the same (dev/governance/dimensions/
 // D13.md), so it is isolated too. DIMS and ISOLATED are the schedule: EVERY brief
@@ -62,7 +62,10 @@ const DIMS = ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10',
 // An isolated seat gets its OWN worktree: seats of one dimension that share a
 // box would otherwise mutate one tree under each other.
 // D15 is isolated because its perturbations edit production (dev/governance/dimensions/D15.md).
-const ISOLATED = new Set(['D0', 'D3', 'D9', 'D11', 'D13', 'D14', 'D15'])
+// D16 is isolated because its two owed perturbations edit the write path, and its upgrade
+// state reads the previous tag's package from `.git` (dev/governance/dimensions/D16.md).
+// D17 perturbs configuration only and runs in the export.
+const ISOLATED = new Set(['D0', 'D3', 'D9', 'D11', 'D13', 'D14', 'D15', 'D16'])
 // WHICH FINDERS MAY READ GITHUB, narrower than ISOLATED on purpose: D0, D3 and D9
 // are isolated to MUTATE production, not to read the API, and the wall COMMON.md
 // draws (a finder's verdicts are its population, never its evidence) is what this
@@ -109,7 +112,8 @@ const seatsFromScopes = (table, dim) => {
 // sits alone (dev/audit/README.md, "Resource rules on the audit box"): D4-s1
 // drives the card and D4-s3 renders it for the visual and accessibility pass.
 // The leads seat runs after the fan-out, on the box named by LEADS_BOX.
-// B11-B13 hold the D5 and D6 ledger seats past the third (scopes.json `ledger`).
+// B11-B13 hold the D5 and D6 ledger seats past the third (scopes.json `ledger`);
+// B11 and B13 also the D16 and D17 seats, each driving cycles on a real loop.
 const BOXES = {
   B1: { heavy: ['D0-s1', 'D3-s1', 'D9-s1'], light: ['D5-s1', 'D6-s1', 'D10-s1'] },
   B2: { heavy: ['D0-s2', 'D3-s2', 'D9-s2'], light: ['D5-s2', 'D6-s2', 'D10-s2'] },
@@ -121,9 +125,9 @@ const BOXES = {
   B8: { heavy: ['D15-s2', 'D15-s3'], light: ['D13-s1', 'D13-s2', 'D13-s3', 'D15-s1'] },
   B9: { heavy: [], light: ['D4-s1'] },
   B10: { heavy: [], light: ['D4-s3'] },
-  B11: { heavy: [], light: ['D5-s4', 'D5-s5', 'D5-s6'] },
+  B11: { heavy: ['D16-s1', 'D16-s2', 'D16-s3'], light: ['D5-s4', 'D5-s5', 'D5-s6'] },
   B12: { heavy: [], light: ['D5-s7', 'D5-s8', 'D5-s9', 'D5-s10'] },
-  B13: { heavy: [], light: ['D6-s4', 'D6-s5', 'D6-s6', 'D6-s7'] },
+  B13: { heavy: ['D17-s1', 'D17-s2', 'D17-s3'], light: ['D6-s4', 'D6-s5', 'D6-s6', 'D6-s7'] },
 }
 const CHROMIUM = new Set(['D4-s1', 'D4-s3'])
 const LEADS_BOX = 'B8'
diff --git a/.github/CODEOWNERS b/.github/CODEOWNERS
index 3927adb946..c49d1d0551 100644
--- a/.github/CODEOWNERS
+++ b/.github/CODEOWNERS
@@ -65,6 +65,9 @@
 /dev/audit/config/objective.json          @tvofi
 /dev/audit/yardstick/                     @tvofi
 /tools/audit/check_scopes.py              @tvofi
+# Decision 0018's escapes, injected and refix reads and card L1's loop
+# (R11-PRE-ROUND-METRICS part 2): the convergence record's enumerator.
+/tools/audit/seat/loop_ledger.py          @tvofi
 # Decision 0018's enumerators are code-owned (section 5): the two held-out
 # instruments R11-PRE-ROUND-METRICS builds.
 /tools/audit/seat/plant_recall.py         @tvofi
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index 4990fb8817..99c5c76a36 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -527,6 +527,14 @@ jobs:
         if: steps.scope.outputs.finder-overlap == 'true'
         run: python3 -I tools/audit/seat/finder_overlap.py --self-test
 
+      # The convergence record's loop ledger (R11-PRE-ROUND-METRICS part 2; cards
+      # P7 and L1): escapes by found_by and owning dimension, injected, refix and
+      # the countermeasure loop per round and week; a partial ledger reads unread.
+      - name: Show the loop ledger reading unread on an empty or partial ledger and each read on a recorded one
+        id: loop-ledger
+        if: steps.scope.outputs.loop-ledger == 'true'
+        run: python3 -I tools/audit/seat/loop_ledger.py --self-test
+
       # The I3 barrier's own verdicts (BLIND, DEAD, REFUSED, unregistered) on a
       # synthetic registration, offline: `policy-docs` runs the base's copy,
       # which cannot answer for a change to this one.
diff --git a/CLAUDE.md b/CLAUDE.md
index c51d09f375..f1a8a04317 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -127,13 +127,12 @@ Under `dev/governance/roles/`.
 | `verifier.md` | the one verifier per dimension, carrying three lenses over findings with claim, evidence, harness, metric and perturbation; a refute sends one to the judge, never kills |
 | `COMMON.md` | **the finder's contract** — every audit dimension: what a finding is, what a non-finding is, and the report shape |
 
-**There is exactly one `COMMON.md`, and it is the finder's contract.** A running
-session may also hand its seats an out-of-tree shared block, named
-`SEAT-BLOCK.md`; that one is **not** policy but a convenience copy.
+**There is exactly one `COMMON.md`.** `SEAT-BLOCK.md`, an out-of-tree block a
+running session hands its seats, is a convenience copy, **not** policy.
 
 ### Dimension briefs — the audit rounds
 One per dimension, under `dev/governance/dimensions/`, in the owner's own words. Named
-individually, because a range reads as complete while covering a fraction:
+individually, never as a range:
 
 | brief | dimension |
 |---|---|
@@ -153,6 +152,8 @@ individually, because a range reads as complete while covering a fraction:
 | `D13.md` | process yield and cost |
 | `D14.md` | recurring bug classes |
 | `D15.md` | debugging run from a live diagnostics bundle |
+| `D16.md` | actuator writes, holds and releases against the plan |
+| `D17.md` | feature behaviour against its documented effect |
 
 Finder criteria (`owner_criteria`): `D4-criteria.md`,
 `D5-criteria.md`, `D9-criteria.md`, `D10-criteria.md`.
diff --git a/README.md b/README.md
index 30dab25208..de29c9d085 100644
--- a/README.md
+++ b/README.md
@@ -319,6 +319,9 @@ installing rather than discover it after:
   by name where it does not. The slab constants themselves are always
   trusted from configuration.
 
+Where the integration is heading, by what it will do, is in
+[ROADMAP.md](./ROADMAP.md).
+
 ## Installation
 
 > [!IMPORTANT]
diff --git a/ROADMAP.md b/ROADMAP.md
new file mode 100644
index 0000000000..fcb5f6a343
--- /dev/null
+++ b/ROADMAP.md
@@ -0,0 +1,31 @@
+# Roadmap
+
+Where the integration is heading, by what it will do. Each entry names what has
+to exist before it can start. Nothing here is a commitment to a date or an order.
+
+For what the integration does today and what it does not, see the
+[README](./README.md) and its [Known limitations](./README.md#known-limitations).
+
+## Zone groups
+
+Split a house into a few zone groups, for example a ground floor and an upper
+floor. Each group has its own thermal state in the model, and the number of
+groups is not fixed at two: groups are indexed, so a house can have as many as
+it needs.
+
+**Needs first:**
+
+- Room-level temperature history, so each group's thermal behaviour can be
+  learned from its own measurements.
+- Evidence from the room phases planned in round 11 that each group's thermal
+  parameters can be told apart from the others' using that history.
+
+## One zone per room
+
+Give each room its own zone, and let the integration write each room's
+thermostat target as part of the plan.
+
+**Needs first:**
+
+- The same room-level history and identifiability evidence as zone groups.
+- Zone groups, which this builds on.
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
diff --git a/dev/audit/config/rotation.json b/dev/audit/config/rotation.json
index feb2ca071a..a5ffff2b6a 100644
--- a/dev/audit/config/rotation.json
+++ b/dev/audit/config/rotation.json
@@ -801,5 +801,13 @@
         "yield": {}
       }
     }
+  },
+  "D16": {
+    "steps": ["M1", "M2", "M3", "M4", "M5", "M6"],
+    "rounds": {}
+  },
+  "D17": {
+    "steps": ["M1", "M2", "M3"],
+    "rounds": {}
   }
 }
diff --git a/dev/audit/config/scopes.json b/dev/audit/config/scopes.json
index 6aa17cb651..43262112ab 100644
--- a/dev/audit/config/scopes.json
+++ b/dev/audit/config/scopes.json
@@ -481,6 +481,7 @@
   "mode": "files",
   "universe": [
    "README.md",
+   "ROADMAP.md",
    "DISCLAIMER.md",
    "RELEASE_NOTES.md",
    "docs/index.html",
@@ -538,6 +539,7 @@
     {
      "files": [
       "README.md",
+      "ROADMAP.md",
       "DISCLAIMER.md",
       "RELEASE_NOTES.md",
       "docs/index.html",
@@ -1177,5 +1179,129 @@
     }
    ]
   }
+ },
+ "D16": {
+  "mode": "cells",
+  "universe": [
+   "custom_components/heatpump_optimizer/*.py"
+  ],
+  "steps": [
+   "M1",
+   "M2",
+   "M3",
+   "M4",
+   "M5",
+   "M6"
+  ],
+  "seats": {
+   "s1": [
+    {
+     "files": [
+      "**"
+     ],
+     "steps": [
+      "M1",
+      "M2"
+     ]
+    }
+   ],
+   "s2": [
+    {
+     "files": [
+      "**"
+     ],
+     "steps": [
+      "M3",
+      "M4"
+     ]
+    }
+   ],
+   "s3": [
+    {
+     "files": [
+      "**"
+     ],
+     "steps": [
+      "M5",
+      "M6"
+     ]
+    }
+   ]
+  }
+ },
+ "D17": {
+  "mode": "cells",
+  "universe": [
+   "custom_components/heatpump_optimizer/*.py",
+   "custom_components/heatpump_optimizer/{services.yaml,strings.json}",
+   "blueprints/**"
+  ],
+  "steps": [
+   "M1",
+   "M2",
+   "M3"
+  ],
+  "axis": {
+   "kind": [
+    "option",
+    "options-step",
+    "config-field",
+    "config-step",
+    "service",
+    "entity",
+    "blueprint"
+   ]
+  },
+  "seats": {
+   "s1": [
+    {
+     "files": [
+      "**"
+     ],
+     "steps": [
+      "M1",
+      "M2",
+      "M3"
+     ],
+     "axis": [
+      "option",
+      "options-step"
+     ]
+    }
+   ],
+   "s2": [
+    {
+     "files": [
+      "**"
+     ],
+     "steps": [
+      "M1",
+      "M2",
+      "M3"
+     ],
+     "axis": [
+      "config-field",
+      "config-step"
+     ]
+    }
+   ],
+   "s3": [
+    {
+     "files": [
+      "**"
+     ],
+     "steps": [
+      "M1",
+      "M2",
+      "M3"
+     ],
+     "axis": [
+      "service",
+      "entity",
+      "blueprint"
+     ]
+    }
+   ]
+  }
  }
 }
\ No newline at end of file
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
diff --git a/dev/audit/rounds/round11/evaluation/design_verdicts.py b/dev/audit/rounds/round11/evaluation/design_verdicts.py
new file mode 100644
index 0000000000..ecd62053b0
--- /dev/null
+++ b/dev/audit/rounds/round11/evaluation/design_verdicts.py
@@ -0,0 +1,37 @@
+#!/usr/bin/env python3
+"""First design-review verdict per group, from the design-verdict bus and its archive tags (git only).
+
+Usage: python3 dev/audit/rounds/round11/evaluation/design_verdicts.py --repo . --window FROM..UNTIL
+Each ref `design-verdict/<GROUP>` (a remote head or an `archive/design-verdict/` tag) holds one commit per verdict, subject
+`... Design review: approve|revise ...`. Prints groups whose first verdict falls in the window, how many of those were
+`approve`, and the verdict count per group (2 or more is a re-review).
+"""
+import argparse, datetime, re, subprocess
+
+
+def main():
+    ap = argparse.ArgumentParser(); ap.add_argument("--repo", default="."); ap.add_argument("--window", required=True)
+    a = ap.parse_args()
+    lo, hi = (datetime.datetime.fromisoformat(x.replace("Z", "+00:00")).timestamp() for x in a.window.split("..", 1))
+    git = lambda *x: subprocess.run(["git", "-C", a.repo, *x], capture_output=True, text=True).stdout
+    refs = {}
+    for l in git("for-each-ref", "--format=%(refname)", "refs/tags/archive/design-verdict", "refs/remotes/origin/design-verdict").split("\n"):
+        if l:
+            refs.setdefault(l.rsplit("/", 1)[-1].upper(), l)
+    n = first_ok = total = 0; multi = []
+    for g, ref in sorted(refs.items()):
+        log = [l.split("\t", 1) for l in git("log", "--reverse", "--format=%ct\t%s", ref).split("\n") if "Design review:" in l]
+        vs = [(t, re.search(r"Design review:\s*(approve|revise)", s).group(1)) for t, s in log if re.search(r"Design review:\s*(approve|revise)", s)]
+        if not vs:
+            continue
+        t0 = int(vs[0][0])
+        if not (lo <= t0 <= hi):
+            continue
+        n += 1; first_ok += vs[0][1] == "approve"; total += len(vs)
+        if len(vs) > 1:
+            multi.append(f"{g}:{len(vs)}")
+    print(f"groups with a design verdict in the window: {n}; first verdict approve: {first_ok}/{n}; verdicts: {total}; re-reviewed: {','.join(multi) or '-'}")
+
+
+if __name__ == "__main__":
+    main()
diff --git a/dev/audit/rounds/round11/evaluation/dimension_read.py b/dev/audit/rounds/round11/evaluation/dimension_read.py
new file mode 100644
index 0000000000..675d1d7edc
--- /dev/null
+++ b/dev/audit/rounds/round11/evaluation/dimension_read.py
@@ -0,0 +1,69 @@
+#!/usr/bin/env python3
+"""What a round's records say per dimension brief, for decision 0018 section 3's dimension row.
+
+Usage: python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref <graded sha> --round 10 --roster <SHA:PATH>
+Per dimension, one line: judged verdicts of the round (JUDGE.json and CATCHUP-JUDGE.json, a verdict id counted once, the later
+record winning), how many stand (verified or weakened), how many of those the judge classed `bug`, how many standing findings sit
+in a roster group whose stage is done (the removed count, by finding id in the group's `findings`), and the seats' own coverage
+rows from reports-B*.json: rows, steps, depth labels, steps no seat ran `deep`, rows carrying an examined/universe key (the
+denominator 0018's `coverage` needs) and rows whose evidence states a count as `N of M` or `N/M` in prose. An id with no D<k> prefix is attributed by its prefix (ARCH*: D7) or listed under `other`.
+"""
+import argparse, collections, glob, json, re, subprocess, sys
+
+
+def show(repo, spec):
+    r = subprocess.run(["git", "-C", repo, "show", spec], capture_output=True, text=True)
+    return r.stdout if r.returncode == 0 else None
+
+
+def main():
+    ap = argparse.ArgumentParser()
+    ap.add_argument("--repo", default="."); ap.add_argument("--ref", default="HEAD")
+    ap.add_argument("--round", type=int, required=True); ap.add_argument("--roster", required=True)
+    a = ap.parse_args()
+    base = f"dev/audit/rounds/round{a.round}/"
+    verdicts = {}
+    for f in ("JUDGE.json", "CATCHUP-JUDGE.json"):
+        t = show(a.repo, f"{a.ref}:{base}{f}")
+        for v in (json.loads(t)["verdicts"] if t else []):
+            verdicts[v["id"]] = v
+    groups = json.loads(show(a.repo, a.roster))["groups"]
+    done_ids, any_ids = set(), set()
+    for g in groups:
+        for fid in g.get("findings") or []:
+            any_ids.add(str(fid))
+            if (g.get("resume") or {}).get("stage") == "done":
+                done_ids.add(str(fid))
+    def dim(i):
+        m = re.match(r"D(\d+)-", i)
+        return f"D{m.group(1)}" if m else ("D7" if i.startswith("ARCH") else "other")
+    tab = collections.defaultdict(collections.Counter)
+    for i, v in verdicts.items():
+        d = tab[dim(i)]
+        d["judged"] += 1
+        if v.get("verdict") in ("verified", "weakened"):
+            d["stand"] += 1
+            d["bug"] += v.get("stop_rule_class") == "bug"
+            d["removed"] += i in done_ids
+            d["in_no_group"] += i not in any_ids
+    files = [l for l in subprocess.run(["git", "-C", a.repo, "ls-tree", "--name-only", a.ref, base], capture_output=True, text=True).stdout.split("\n") if re.search(r"reports-B\d+\.json$", l)]
+    cov = collections.defaultdict(lambda: {"rows": 0, "depth": collections.Counter(), "steps": collections.defaultdict(set), "denom": 0, "prose": 0, "seats": 0})
+    for f in files:
+        for seat, r in json.loads(show(a.repo, f"{a.ref}:{f}"))["reports"].items():
+            c = cov[r.get("dimension") or seat.split("-")[0]]
+            c["seats"] += 1
+            for row in r.get("coverage") or []:
+                c["rows"] += 1; c["depth"][str(row.get("depth"))] += 1; c["steps"][str(row.get("step"))].add(str(row.get("depth")))
+                c["denom"] += any(k in row for k in ("examined", "universe", "denominator"))
+                c["prose"] += bool(re.search(r"\b\d+\s*(?:of|/)\s*\d+\b", str(row.get("evidence", ""))))
+    print("dimension\tjudged\tstand\tbug\tremoved\tstand_in_no_group\tseats\tcoverage_rows\tsteps\tdepth\tsteps_not_deep\trows_with_examined_universe\trows_stating_a_count_in_prose")
+    for k in sorted(set(tab) | set(cov), key=lambda s: (s == "other", int(s[1:]) if s[1:].isdigit() else 0)):
+        d, c = tab[k], cov[k]
+        nd = sorted(s for s, ds in c["steps"].items() if "deep" not in ds)
+        print(f"{k}\t{d['judged']}\t{d['stand']}\t{d['bug']}\t{d['removed']}\t{d['in_no_group']}\t{c['seats']}\t{c['rows']}\t{len(c['steps'])}\t{dict(c['depth'])}\t{','.join(nd) or '-'}\t{c['denom']}\t{c['prose']}")
+    print(f"ROWS {sum(c['rows'] for c in cov.values())} WITH_EXAMINED_UNIVERSE {sum(c['denom'] for c in cov.values())} STATING_A_COUNT_IN_PROSE {sum(c['prose'] for c in cov.values())}")
+    print(f"VERDICTS {len(verdicts)} DIMENSIONS_REPORTED {sum(1 for c in cov.values() if c["seats"])}")
+
+
+if __name__ == "__main__":
+    main()
diff --git a/dev/audit/rounds/round11/evaluation/escapes.py b/dev/audit/rounds/round11/evaluation/escapes.py
new file mode 100644
index 0000000000..a8afe729fc
--- /dev/null
+++ b/dev/audit/rounds/round11/evaluation/escapes.py
@@ -0,0 +1,74 @@
+#!/usr/bin/env python3
+"""Check the by-hand escapes ledger against the roster and print what it counts.
+
+Usage: python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --roster <SHA:PATH> [--ref <graded sha>] [--ledger escapes_hand.tsv]
+The matching rule: a roster group is a candidate when it lists a file under custom_components/ or blueprints/ and its
+`source` is outside or user, or its `kind` is owner, bug, hotfix or owner-step, or its id holds HOTFIX or OUTSIDE, or its
+brief matches REPORT below. Refuses (rc 1) a candidate with no row, a row that is no candidate, a group rowed twice, an
+owner that is neither `none`, `-` nor a tracked dimension brief, and a window outside in, day0, unreleased, out. Prints rows
+per owner and per window (`in`: an escape; `day0`: dated the closeout stamp's own day; `unreleased`: injected and caught
+before a release; `out`: no escape, with its reason), the `none` rows of window `in` (the unowned items), the rows naming a
+cause pull request, and the in-window rows for which a root-cause record is tracked under dev/audit/rca/ at --ref (matched on
+the group id less its R10-, HOTFIX- and OUTSIDE- prefixes). A proxy for `escapes`, `unowned` and `injected`, never the terms:
+the roster records no found-by and no owning dimension, and a brief's cause is the fixer's unless a root-cause record names it.
+"""
+import argparse, collections, json, re, subprocess, sys
+from pathlib import Path
+
+REPORT = re.compile(r"owner[- ]report|outside report|owner request|owner order|owner question|outside pull request|outside contribution"
+                    r"|outside user|live user|live defect|live bug|reported by the owner|owner[- ]reported"
+                    r"|the owner's (own )?(install|export|house|live)|from his (own )?install|\(owner, 20"
+                    r"|found by (the )?R10-|found by the .{0,40}fixer|defect still in main|latent", re.I)
+PRODUCT = ("custom_components/", "blueprints/")
+
+
+def candidate(g):
+    if not any(str(f).startswith(PRODUCT) for f in g.get("files") or []):
+        return False
+    brief = " ".join(str(g.get("brief")).split())
+    return bool(g.get("source") in ("outside", "user") or str(g.get("kind")) in ("owner", "bug", "hotfix", "owner-step")
+                or "HOTFIX" in g["group"] or "OUTSIDE" in g["group"] or REPORT.search(brief))
+
+
+def main():
+    ap = argparse.ArgumentParser()
+    ap.add_argument("--repo", default="."); ap.add_argument("--roster", required=True); ap.add_argument("--ref", default="HEAD")
+    ap.add_argument("--ledger", default=str(Path(__file__).with_name("escapes_hand.tsv")))
+    a = ap.parse_args()
+    git = lambda *x: subprocess.run(["git", "-C", a.repo, *x], capture_output=True, text=True).stdout
+    groups = {g["group"]: g for g in json.loads(git("show", a.roster))["groups"]}
+    cands = {k for k, g in groups.items() if candidate(g)}
+    lines = [l.rstrip("\n").split("\t") for l in open(a.ledger) if l.strip() and not l.startswith("#")]
+    rows = [dict(zip(lines[0], r)) for r in lines[1:]]
+    bad = []
+    seen = collections.Counter(r["group"] for r in rows)
+    bad += [f"{k}: rowed {n} times" for k, n in seen.items() if n > 1]
+    bad += [f"{k}: a candidate with no row" for k in sorted(cands - set(seen))]
+    bad += [f"{k}: a row that is no candidate" for k in sorted(set(seen) - cands)]
+    for r in rows:
+        if r["window"] not in ("in", "day0", "unreleased", "out"):
+            bad.append(f"{r['group']}: window {r['window']}")
+        if r["owner"] not in ("none", "-") and not git("ls-tree", "--name-only", a.ref, f"dev/governance/dimensions/{r['owner']}.md").strip():
+            bad.append(f"{r['group']}: owner {r['owner']} is no dimension brief")
+        if (r["window"] == "out") != (r["owner"] == "-"):
+            bad.append(f"{r['group']}: an `out` row carries owner `-`, and no other row does")
+    for b in bad:
+        print("REFUSED", b)
+    order = lambda kv: (kv[0] in ("none", "-"), int(kv[0][1:]) if kv[0][1:].isdigit() else 0)
+    for w in ("in", "day0", "unreleased", "out"):
+        c = collections.Counter(r["owner"] for r in rows if r["window"] == w)
+        print(f"window={w}\trows={sum(c.values())}\t" + " ".join(f"{k}={v}" for k, v in sorted(c.items(), key=order)))
+    inw = [r for r in rows if r["window"] == "in"]
+    print("UNOWNED", ",".join(r["group"] for r in inw if r["owner"] == "none"))
+    print("CAUSE_NAMED", ",".join(f"{r['group']}<-#{r['cause_pr']}({r['window']})" for r in rows if r["cause_pr"] != "-"))
+    print("CAUSES", len({c for r in rows if r["cause_pr"] != "-" for c in r["cause_pr"].split(",")}))
+    print("REPORTERS", dict(collections.Counter(r["reporter"] for r in inw)))
+    rca = [l for l in git("ls-tree", "-r", "--name-only", a.ref, "dev/audit/rca/").split("\n") if l]
+    stem = lambda k: re.sub(r"^R1[01]-(HOTFIX-|OUTSIDE-)?", "", k)
+    print("RCA_TRACKED", ",".join(r["group"] for r in inw if any(stem(r["group"]) in f for f in rca)))
+    print(f"CANDIDATES {len(cands)} ROWS {len(rows)} REFUSED {len(bad)}")
+    sys.exit(1 if bad else 0)
+
+
+if __name__ == "__main__":
+    main()
diff --git a/dev/audit/rounds/round11/evaluation/escapes_hand.tsv b/dev/audit/rounds/round11/evaluation/escapes_hand.tsv
new file mode 100644
index 0000000000..96738901c6
--- /dev/null
+++ b/dev/audit/rounds/round11/evaluation/escapes_hand.tsv
@@ -0,0 +1,83 @@
+# The by-hand read decision 0018 section 3 allows for a dimension's escapes ("escapes by hand"), over the roster at the pinned commit cbd6d9185166 (`dev/programme/rosters/wave-r10-groups.json`).
+# Matching rule, enforced by escapes.py: a roster group is a candidate when it lists a file under custom_components/ or blueprints/ and (a) its `source` is outside or user, or (b) its `kind` is owner, bug, hotfix or owner-step, or (c) its id holds HOTFIX or OUTSIDE, or (d) its brief matches escapes.py's REPORT pattern (an owner or outside report, request or order, a live defect, the owner's install or export, a defect another group's seat found, a latent defect). Every candidate has exactly one row and every row is a candidate.
+# `window`: `in` = an objective bug on a released version, reported in round 10's window by someone who is no finder seat (an escape); `day0` = dated 2026-10-14, the closeout stamp's own day, the hour in no tracked record (counted in no verdict); `unreleased` = caused and caught inside the window before a release carried it (injected, no escape); `out` = no escape, the reason in `input_not_driven`.
+# Not selected by the rule, so unrowed: product groups whose brief reports no outside or owner report, among them the five the round's own D15 triage raised from the owner's live bundle (R10-IMMERSION-LATCH, R10-DIAG-REDACT, R10-HOUSE-GRADE, R10-LEGIONELLA-COMPLETION, R10-DIAG-AGES) and the fixer-found R10-TWO-ZONE-HHL: found by the audit's own work, they are no escapes. R10-FLY-REPLAY-MASK is rowed `in` because its brief places the find on the owner's export of 2026-11-04, after the finder pass and outside any D15 seat's run.
+# An escape is a report from an install, the owner's or an outsider's (0018 section 3's residual `reports depend on installs existing to report`, section 4 assumption 7): a defect a programme seat found, and an outside pull request the intake triage built as a need or a gap, are `out`.
+# `owner` is the dimension whose perfect result (0018 section 1) the bug violates, `none` where no brief owns it, `-` on an `out` row. `cause_pr` is each merged pull request the group's brief or its tracked root-cause record names as a cause, comma-separated. Attribution is the evaluator's, from each group's brief; the reviewer attacks it. Columns are tab-separated.
+group	pr	reporter	window	owner	step	input_not_driven	cause_pr
+R10-HOTFIX-AWAY-LIVE	3015	owner	in	D1	D1.M1	a stored away override across restore then resolve, switch then refresh, set-point reload then refresh	-
+R10-HOTFIX-AWAY-PRESENCE	3052	owner	in	D1	D1.M3	a presence entity changing between two scheduled updates	-
+R10-OUTSIDE-PRICE-OUTAGE-LAST-VALID	3454	outside	in	D1	D1.M3	a price fetch that raises while the last fetched prices still cover now	-
+R10-INPUT-REAPPEAR	3300	outside	in	D1	D1.M3	a configured input going missing or unavailable and reporting again inside one interval	-
+R10-LEARNED-STORE-LOAD	3185	-	out	-	-	found by a programme seat (the R10-FACTORY-RESET fixer), no report from an install: no escape; its input stays in card E11-D1 as a seat-found defect	-
+R10-HOTFIX-SAV-ESTIMATE	3220	owner	in	D2	D2.M3	the savings identity on a month booked from a valve house whose buffer sits above the curve	2411,2887
+R10-HOTFIX-LEARNER-INPUTS	3022	owner	in	D2	D2.M5	a power entity that is the pump's own estimate, and a learner covariate moved to another sensor	-
+R10-OUTSIDE-DHW-CHARGE-SETTLE	3444	outside	in	D2	D2.M5	the tank reading's fall in the minutes after a charge starts	-
+R10-HOTFIX-CARD-HEALTH-TEXT	3485	owner	in	D4	D4.M1	the Health tab's row labels on the released build in a real Home Assistant frontend	-
+R10-OUTSIDE-VALVE-TARGET-LABEL	3536	outside	in	D4	D4.M2	a flow temperature typed into the mixing-valve target on a combi entry	-
+R10-HOTFIX-COP-UNMEASURED	3297	owner	in	D6	D6.M2	the card's measured-COP sentence on an install with no heat input	-
+R10-HOTFIX-PREHEAT-LABEL	-	owner	in	D8	D8.M2	a step's reason on a house whose learned heat-loss scale is above 1.1 under flat weather	-
+R10-OUTSIDE-DIAG-REDACT-LOCATION	3447	outside	in	D10	D10.M1	the diagnostics rule driven with the solar-location option set	-
+R10-OUTSIDE-LEARNER-ROBUSTNESS	3468	outside	in	D12	D12.M3	a counter-metered pump whose spans hold hot-water charges, and a short boost	-
+R10-HOTFIX-AWAY-SETBACK	3013	owner	in	none	-	away with weekend or holiday comfort fields set: a feature against its documented effect	-
+R10-HOTFIX-BOOST-FLOW-CEILING	3562	owner	in	none	-	a boost over a step the plan books at partial power: the write against the plan's target	-
+R10-HOTFIX-FLOW-SETPOINT-STUCK	3561	owner	in	D1	D1.M2	the previous release's persisted arbiter record driven to the first write: a hold on a write with no release (also `operation`'s end state, a refusal with a release that needs no person)	3404
+R10-OUTSIDE-DISINFECTION-SETPOINT	3452	outside	in	none	-	the hot-water write on a disinfection step: the guard records attempts and no completion	-
+R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE	3512	-	out	-	-	triaged NEED by the feature triage (a new rule built from an outside pull request), no hotfix of a reported defect: no escape; card E11-U5 stands as an argument for the actuator-write dimension	-
+R10-OUTSIDE-SUPPLY-STALE-STEP	3478	outside	in	none	-	a cycle whose write lands in the step after the one its action was cut for	-
+R10-WATER-SETPOINT-FEEDBACK	3405	outside	in	none	-	a water set-point on a controller with an integrating speed loop: measured power against plan	-
+R10-MODE-BEFORE-SUPPLY-ON	3530	outside	in	none	-	the order of the mode write and the supply switch-on	-
+R10-SAV-BASELINE	-	owner	day0	D2	D2.M3	the month table's baseline against actual on the owner's months	-
+R10-SAV-REASONS	-	owner	day0	D8	D8.M2	cost attributed to a reason while idle, and a boost with no reason code	-
+R10-SCORES	-	owner	day0	D8	D8.M2	a score with no evidence published as 0	-
+R10-DEEPLINK	-	owner	day0	D4	D4.M1	every link-emitting button of the card followed to its target	-
+R10-UX-HEALTH	2976	owner	day0	D4	D4.M1	the Health tab on a wide screen and under the sticky header	-
+R10-UX-SETUP	-	-	out	-	-	conceded to round 10's objective record: a redesign the owner asked for, no defect report	-
+R10-ADVISOR	-	owner	day0	D2	D2.M3	the advisor's plus and minus one degree deltas for monotonicity	-
+R10-HOTFIX-REFERENCE-BASIS	3599	programme	unreleased	D2	D2.M3	the savings identity across a merge that changes the booked reference	3587
+R10-SAVINGS-NEGATIVE	-	owner	in	D2	D2.M3	the savings identity on a ledger month upgraded mid-month from the previous release	2411
+R10-SETPOINT-BOOST	-	owner	in	none	-	a heating step at minimum power on a tank at or below 20 C: the write equals the do-not-heat value; its second cause, the draw range learning from censored samples, is an estimator defect in D2 step 5's territory and is listed in card E11-D2	-
+R10-SETPOINT-POWER	-	owner	in	D0	D0.M4	an install whose pump power is set through a flow set-point behind a buffer and a mixing valve: the plan stays at the minimum level despite a price spread	-
+R10-DEMAND-OVERBOOK	2712	owner	in	D2	D2.M5	the plan's booked space energy against a metered month: the learned heat loss against metered delivery	-
+R10-BUFFER-STORE	-	-	out	-	-	found by a programme seat (R10-SETPOINT-BOOST's census), no report from an install: no escape; its input stays in card E11-D0 as a seat-found defect	-
+R10-COP-GATE-E	3371	-	out	-	-	found by a programme seat (R10-COP-GATE part D), no report from an install: no escape; its input stays in card E11-D2 as a seat-found defect	-
+R10-MIN-POWER-FLOOR	3308	outside	in	D8	D8.M2	a non-modulating pump with a minimum power: a merged slot's average-power attribute below the minimum (the brief leaves open whether the solver or the attribute is at fault)	-
+R10-FLY-REPLAY-MASK	3219	programme	in	D15	D15.M1	a real download whose replay half is empty because one entity id escapes the mask	-
+R10-RATIO-ANCHOR	-	-	out	-	-	a finder seat's finding (D12-s2-71), no report	-
+R10-LIVESTATE	-	-	out	-	-	finder seats' findings (D1-s1-02, D7-s1-51), no report	-
+R10-HEAT-METER	-	-	out	-	-	an owner request for a feature (a delivered-heat input), no defect	-
+R10-DIAG-REPLAY	-	-	out	-	-	an owner request for a feature (the replay in the diagnostics download), no defect	-
+R10-MARKETPLACE	-	-	out	-	-	an owner request (packaging for the marketplace), no defect	-
+R10-FACTORY-RESET	-	-	out	-	-	an owner request for a feature, no defect	-
+R10-WOOD-NOTIFY	-	-	out	-	-	an owner request for a feature, no defect	-
+R10-I18N-DE	-	-	out	-	-	an owner request (a German translation), no defect	-
+R10-CARD-COLLAPSE	-	-	out	-	-	an owner request for a feature, no defect	-
+R10-LIVE-BUNDLE-READS	-	-	out	-	-	an owner step (reads of a live bundle), no defect stated	-
+R10-SAV-COMFORT	-	-	out	-	-	the same report as R10-SAV-BASELINE's row (its residue)	-
+R10-SAV-ACTUATION	2968	-	out	-	-	conceded to round 10's objective record: built as a feature (actuation at step boundaries) out of R10-SAV-BASELINE's residue	-
+R10-ADVISOR-RESIDUE	-	-	out	-	-	the same report as R10-ADVISOR's row (its residue)	-
+R10-ADVISOR-WHATIF	-	-	out	-	-	the same report as R10-ADVISOR's row (its residue)	-
+R10-SAV-WOOD-MEASURED	-	-	out	-	-	the same report as R10-HOTFIX-SAV-ESTIMATE's row; the group was absorbed	-
+R10-OUTSIDE-LEARNER-ROBUSTNESS-P2	-	-	out	-	-	the same report as R10-OUTSIDE-LEARNER-ROBUSTNESS's row (part 2)	-
+R10-OUTSIDE-LEARNER-ROBUSTNESS-P3	-	-	out	-	-	the same report as R10-OUTSIDE-LEARNER-ROBUSTNESS's row (part 3)	-
+R10-DISINFECTION-STEP-NOTICE	-	-	out	-	-	the same report as R10-OUTSIDE-DISINFECTION-SETPOINT's row (its notice half)	-
+R10-COMBI-TANK	-	-	out	-	-	an outside request for a feature (a combi tank), no defect	-
+R10-COMBI-TANK-PR-B	-	-	out	-	-	an outside request for a feature (part B), no defect	-
+R10-GENERIC-HEAT-CURVE	-	-	out	-	-	an outside request for a feature, built on the owner's ruling	-
+R10-GENERIC-HEAT-CURVE-PERSISTENT	-	-	out	-	-	an outside request for a feature, built on the owner's ruling	-
+R10-WATER-SETPOINT-LIFT	-	-	out	-	-	an outside request for a feature (two expert options), no defect	-
+R10-DUTY-SWITCH-RESTART-LEARNING	-	-	out	-	-	an outside design note; part A builds a learner, no defect	-
+R10-DUTY-SWITCH-RESTART-LEARNING-PR-B	-	-	out	-	-	an outside design note; a feature part, no defect	-
+R10-DUTY-SWITCH-PLANNER-PRICE	-	-	out	-	-	an outside design note; a feature part, no defect	-
+R10-OUTSIDE-DHW-START-HYSTERESIS	3531	-	out	-	-	triaged GAP by the feature triage (a new optional input), no hotfix of a reported defect: no escape; card E11-U10 stands as an argument for the actuator-write dimension	-
+R10-OUTSIDE-CLIMATE-NATIVE-TEMP	-	-	out	-	-	a deprecation on the current core, no failure on a released version yet	-
+R10-START-COUNTER-EDGES	-	-	out	-	-	in progress at the close: no fix carries its failing-test-first proof yet	-
+R11-OUTSIDE-HONEST-STARTS-RUNS	-	-	out	-	-	accepted for round 11 and in progress at the close	-
+R10-DRAW-MAP-EVIDENCE	-	-	out	-	-	an owner order of 2026-11-14, in progress at the close: no fix carries its proof yet	-
+R10-DOCS-STRINGS-RESIDUE	-	-	out	-	-	a text-residue pass the owner asked for, not a report; a lead for D6	-
+R10-HOTFIX-STRESS-MEM-PEAK	-	-	out	-	-	a red stress probe on a pull request's own run, no report on a release	-
+R10-HOTFIX-STRESS-MEM-PEAK-2	-	-	out	-	-	a red test probe on main with no code moved, no report on a release	-
+R10-HOTFIX-MAIN-FAST-1109	-	-	out	-	-	a red main from a merge skew, caught by the gate before a release: `product_green`'s, not an escape	-
+R10-HOTFIX-COMBI-CENSUS-MAIN-RED	-	-	out	-	-	a red main after pull request 3398, caught by the gate before a release: `product_green`'s, not an escape	-
+R10-DEAD-RATE-LIMIT	-	-	out	-	-	a dead limit (hygiene), found by the seat whose own change caused it	-
+R10-COP-PARTLOAD	-	-	out	-	-	a model extension measured first, no defect stated	-
diff --git a/dev/audit/rounds/round11/evaluation/gate_reds.py b/dev/audit/rounds/round11/evaluation/gate_reds.py
new file mode 100644
index 0000000000..0715c3054f
--- /dev/null
+++ b/dev/audit/rounds/round11/evaluation/gate_reds.py
@@ -0,0 +1,131 @@
+#!/usr/bin/env python3
+"""Main's push runs of the CI workflow over a window: the `gate` share and the failed jobs per called workflow.
+
+Usage:
+  python3 dev/audit/rounds/round11/evaluation/gate_reds.py fetch --dir D --slug OWNER/REPO --from YYYY-MM-DD --to YYYY-MM-DD
+  python3 dev/audit/rounds/round11/evaluation/gate_reds.py report --dir D --window FROM..UNTIL (ISO instants, UTC)
+`fetch` reads GitHub with `gh api` (GET only): the workflow's push runs on main in three-day ranges, each listing's
+total_count beside the rows fetched so the 1000-result cap shows, then, for each run that concluded `failure`, its jobs that
+failed or timed out and its `gate` job. It appends, so an interrupted fetch resumes. `report` prints: runs in the window by
+conclusion; the `gate` share (runs whose `gate` job succeeded over concluded runs, a successful run counted as a succeeded
+gate, a failed run with no job listing fetched counted `unread`), with the cancelled count beside it; failed jobs per job
+name and per called workflow (the job-name prefix before ` / `), the failed jobs of the runs whose `gate` did not
+succeed, the job that failed alone on such a run, and those runs per called workflow. A run's cause is not printed: no red carries one.
+"""
+import argparse, collections, datetime, json, subprocess, sys, time
+from pathlib import Path
+
+
+def gh(path, jq, paginate=True):
+    r = subprocess.run(["gh", "api", path, *(["--paginate"] if paginate else []), "--jq", jq], capture_output=True, text=True)
+    if r.returncode:
+        raise SystemExit(f"gh api {path}: {r.stderr.strip()[:200]}")
+    return [json.loads(l) for l in r.stdout.split("\n") if l.strip()]
+
+
+def fetch(a):
+    d = Path(a.dir); d.mkdir(parents=True, exist_ok=True)
+    runs_f, jobs_f = d / "ci_runs.jsonl", d / "ci_failed_jobs.jsonl"
+    have = {json.loads(l)["id"] for l in open(runs_f)} if runs_f.exists() else set()
+    day, end = datetime.date.fromisoformat(getattr(a, "from")), datetime.date.fromisoformat(a.to)
+    base = f"repos/{a.slug}/actions/workflows/ci.yml/runs?branch=main&event=push"
+    with open(runs_f, "a") as out, open(d / "ci_runs.counts", "a") as counts:
+        while day <= end:
+            rng = f"{day}..{min(day + datetime.timedelta(days=2), end)}"
+            total = gh(f"{base}&created={rng}&per_page=1", ".total_count", paginate=False)[0]
+            rows = gh(f"{base}&created={rng}&per_page=100", ".workflow_runs[] | {id, name, run_number, run_attempt, head_sha, created_at, updated_at, status, conclusion}")
+            for r in rows:
+                if r["id"] not in have:
+                    out.write(json.dumps(r) + "\n"); have.add(r["id"])
+            counts.write(f"{rng} total_count={total} fetched={len(rows)}\n")
+            day += datetime.timedelta(days=3)
+    done = {json.loads(l)["run"] for l in open(jobs_f)} if jobs_f.exists() else set()
+    with open(jobs_f, "a") as out:
+        for l in open(runs_f):
+            r = json.loads(l)
+            if r["conclusion"] == "failure" and r["id"] not in done:
+                pages = gh(f"repos/{a.slug}/actions/runs/{r['id']}/jobs?filter=latest&per_page=100",
+                           '[.jobs[] | select(.conclusion=="failure" or .conclusion=="timed_out" or .name=="gate") | {name, conclusion}]')
+                out.write(json.dumps({"run": r["id"], "jobs": [j for p in pages for j in p]}) + "\n"); out.flush()
+                time.sleep(0.5)
+
+
+def report(a):
+    d = Path(a.dir)
+    lo, hi = a.window.split("..", 1)
+    runs = {}
+    for l in open(d / "ci_runs.jsonl"):
+        r = json.loads(l)
+        if lo <= r["created_at"] <= hi:
+            runs[r["id"]] = r
+    jobs = {}
+    if (d / "ci_failed_jobs.jsonl").exists():
+        for l in open(d / "ci_failed_jobs.jsonl"):
+            j = json.loads(l); jobs[j["run"]] = j["jobs"]
+    by = collections.Counter(r["conclusion"] for r in runs.values())
+    first = min((r["created_at"] for r in runs.values()), default="-")
+    print(f"window {a.window}: runs {len(runs)} first {first} " + " ".join(f"{k}={v}" for k, v in sorted(by.items(), key=str)))
+    ok = by.get("success", 0); bad = unread = nongate = 0
+    names, wf, gate_names = collections.Counter(), collections.Counter(), collections.Counter()
+    sole, wf_gate, wf_sole = collections.Counter(), collections.Counter(), collections.Counter()
+    runs_wf = collections.Counter()
+    for i, r in runs.items():
+        if r["conclusion"] != "failure":
+            continue
+        if i not in jobs:
+            unread += 1; continue
+        g = [j for j in jobs[i] if j["name"] == "gate"]
+        if g and g[0]["conclusion"] == "success":
+            ok += 1; nongate += 1
+        else:
+            bad += 1
+            for j in jobs[i]:
+                if j["name"] != "gate":
+                    gate_names[j["name"]] += 1
+            failed = sorted({j["name"] for j in jobs[i] if j["name"] != "gate"})
+            wfs = {n.split(" / ")[0] if " / " in n else "(ci.yml's own job)" for n in failed}
+            sole[failed[0] if len(failed) == 1 else "none" if not failed else "several"] += 1
+            for w in wfs:
+                wf_gate[w] += 1
+            if len(wfs) == 1:
+                wf_sole[next(iter(wfs))] += 1
+        seen = set()
+        for j in jobs[i]:
+            if j["name"] == "gate":
+                continue
+            names[j["name"]] += 1
+            w = j["name"].split(" / ")[0] if " / " in j["name"] else "(ci.yml's own job)"
+            wf[w] += 1; seen.add(w)
+        for w in seen:
+            runs_wf[w] += 1
+    concluded = ok + bad
+    share = f"{ok}/{concluded} ({ok / concluded:.3f})" if concluded and not unread else f"{ok}/{concluded} with {unread} failed run(s) unread: no share"
+    print(f"gate share: {share}; cancelled beside it: {by.get('cancelled', 0)}; failed runs whose gate job succeeded: {nongate}; failed runs read: {bad + nongate}; unread: {unread}")
+    print("failed jobs per called workflow (jobs; runs with at least one):")
+    for w, n in wf.most_common():
+        print(f"  {w}\t{n}\t{runs_wf[w]}")
+    print("failed jobs per job name:")
+    for n, c in names.most_common(25):
+        print(f"  {c}\t{n}")
+    print(f"failed jobs on the {bad} run(s) whose gate job did not succeed:")
+    for n, c in gate_names.most_common(25):
+        print(f"  gate-red {c}\t{n}")
+    print("the only failed job on a gate-red run:")
+    for n, c in sole.most_common():
+        print(f"  sole {c}\t{n}")
+    print("gate-red runs per called workflow (runs with a failed job of it; runs where only its jobs failed):")
+    for w, c in wf_gate.most_common():
+        print(f"  wf-gate {w}\t{c}\t{wf_sole[w]}")
+
+
+def main():
+    ap = argparse.ArgumentParser()
+    sub = ap.add_subparsers(dest="cmd", required=True)
+    f = sub.add_parser("fetch"); f.add_argument("--dir", required=True); f.add_argument("--slug", required=True); f.add_argument("--from", required=True); f.add_argument("--to", required=True)
+    r = sub.add_parser("report"); r.add_argument("--dir", required=True); r.add_argument("--window", required=True)
+    a = ap.parse_args()
+    (fetch if a.cmd == "fetch" else report)(a)
+
+
+if __name__ == "__main__":
+    main()
diff --git a/dev/audit/rounds/round11/evaluation/instrument_cost.py b/dev/audit/rounds/round11/evaluation/instrument_cost.py
new file mode 100644
index 0000000000..a1c15d495d
--- /dev/null
+++ b/dev/audit/rounds/round11/evaluation/instrument_cost.py
@@ -0,0 +1,55 @@
+#!/usr/bin/env python3
+"""Cost of each instrument object objective.json lists, by decision 0018 section 3 (its lines, the hotfix groups naming it).
+
+Usage: python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref <graded sha> --start <window start ref> --end <window end ref> --roster <REF:PATH>
+One TSV line per object: object, implementation, lines at --ref, lines at --start (0: absent), first-parent commits touching it in
+start..end, roster groups naming its basename (id, brief or files), and how many of those are hotfix groups. Then `OBJECTS <n>`.
+An instrument guide `tools/audit/seat/instruments/<name>.md` is costed on the tracked file whose basename is <name>; a guide
+with no such file is costed on itself and says so. Yield is not printed: nothing logs a refusal with its outcome.
+"""
+import argparse, json, re, subprocess, sys
+from pathlib import Path
+
+
+def git(repo, *a):
+    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True).stdout
+
+
+def main():
+    ap = argparse.ArgumentParser()
+    ap.add_argument("--repo", default="."); ap.add_argument("--ref", default="HEAD")
+    ap.add_argument("--start", required=True); ap.add_argument("--end", required=True); ap.add_argument("--roster", required=True)
+    a = ap.parse_args()
+    sys.path.insert(0, str(Path(a.repo) / "tools/audit"))
+    import check_scopes as cs
+    tree = [t for t in git(a.repo, "ls-tree", "-r", "--name-only", a.ref).split("\n") if t]
+    spec = json.loads(git(a.repo, "show", f"{a.ref}:dev/audit/config/objective.json"))
+    objs = sorted(cs.match(tree, spec["objects"]["instrument"]))
+    by_base = {}
+    for t in tree:
+        by_base.setdefault(t.rsplit("/", 1)[-1], []).append(t)
+    groups = json.loads(git(a.repo, "show", a.roster))["groups"]
+    texts = [(g["group"], str(g.get("kind")), g["group"] + " " + str(g.get("brief")) + " " + " ".join(map(str, g.get("files") or []))) for g in groups]
+    def lines(ref, p):
+        r = subprocess.run(["git", "-C", a.repo, "show", f"{ref}:{p}"], capture_output=True)
+        return r.stdout.count(b"\n") if r.returncode == 0 else 0
+    print("object\timplementation\tlines\tlines_at_start\twindow_commits\troster_groups\thotfix_groups")
+    for o in objs:
+        impl, note = o, ""
+        if o.startswith("tools/audit/seat/instruments/") and o.endswith(".md"):
+            name = o.rsplit("/", 1)[-1][:-3]
+            cands = [c for c in by_base.get(name, []) if c != o] or [c for c in by_base.get(name.replace("shims_", ""), []) if c != o]
+            pref = [c for c in cands if c.startswith(("tools/", "tests/", ".claude/"))]
+            impl = (pref or cands or [o])[0]
+            note = "" if impl != o else " (no tracked file of that basename: the guide itself)"
+        base = impl.rsplit("/", 1)[-1]
+        pat = re.compile(r"(?<![\w.-])" + re.escape(base) + r"(?![\w-])")
+        named = [(g, k) for g, k, t in texts if pat.search(t)]
+        hot = [g for g, k in named if k == "hotfix" or "HOTFIX" in g]
+        commits = len([l for l in git(a.repo, "log", "--first-parent", "--oneline", f"{a.start}..{a.end}", "--", impl).split("\n") if l])
+        print(f"{o}\t{impl}{note}\t{lines(a.ref, impl)}\t{lines(a.start, impl)}\t{commits}\t{len(named)}\t{len(hot)}")
+    print(f"OBJECTS {len(objs)}")
+
+
+if __name__ == "__main__":
+    main()
diff --git a/dev/audit/rounds/round11/evaluation/main_red_groups.py b/dev/audit/rounds/round11/evaluation/main_red_groups.py
new file mode 100644
index 0000000000..cfa39f640e
--- /dev/null
+++ b/dev/audit/rounds/round11/evaluation/main_red_groups.py
@@ -0,0 +1,30 @@
+#!/usr/bin/env python3
+"""Roster groups whose brief records a red main, and the job each hotfix among them names.
+
+Usage: python3 dev/audit/rounds/round11/evaluation/main_red_groups.py --repo . --roster <SHA:PATH>
+Prints one line per group (id, kind, stage, the brief's sentence about the red), then the count, the hotfix groups among
+them and how many of those name the `instrument-self-tests` job (`instrument[- ]self-tests` in the brief). The cause is the brief's own word: a lead for a gate's reds, never
+a cause record.
+"""
+import argparse, json, re, subprocess
+
+
+def main():
+    ap = argparse.ArgumentParser(); ap.add_argument("--repo", default="."); ap.add_argument("--roster", required=True)
+    a = ap.parse_args()
+    groups = json.loads(subprocess.run(["git", "-C", a.repo, "show", a.roster], capture_output=True, text=True).stdout)["groups"]
+    pat = re.compile(r"main (is |was |went |goes )?red|red on main|main red|MAIN-RED|main's (gate|push)", re.I)
+    hits = []
+    for g in sorted(groups, key=lambda g: g["group"]):
+        b = " ".join(str(g.get("brief")).split())
+        if pat.search(b + g["group"]):
+            m = re.search(r"(.{0,120})(main (?:is |was |went )?red|red on main)(.{0,200})", b, re.I)
+            hits.append(g["group"])
+            print(g["group"], g.get("kind"), (g.get("resume") or {}).get("stage"), "|", m.group(0) if m else b[:240])
+    hot = [h for h in hits if "HOTFIX" in h]
+    ist = [g["group"] for g in groups if g["group"] in hot and re.search(r"instrument[- ]self-tests", str(g.get("brief")), re.I)]
+    print(f"GROUPS {len(hits)} HOTFIX {len(hot)} NAMING_SELF_TESTS {len(ist)}")
+
+
+if __name__ == "__main__":
+    main()
diff --git a/dev/audit/rounds/round11/evaluation/tally.py b/dev/audit/rounds/round11/evaluation/tally.py
new file mode 100644
index 0000000000..4d0b50837e
--- /dev/null
+++ b/dev/audit/rounds/round11/evaluation/tally.py
@@ -0,0 +1,60 @@
+#!/usr/bin/env python3
+"""Count a start evaluation's verdicts, its unscored share and its cards.
+
+Usage: python3 dev/audit/rounds/round11/evaluation/tally.py [EVALUATION.json]
+Prints `keep`, `change` and `remove` per object class and in total; `NO-READ`, the kept objects whose evidence says NO-READ
+as words of its own (check_scopes.is_no_read's rule), with the unscored share 0018 section 3 asks for; the terms read and
+NO-READ; and the cards by what each answers. Exit 1 if an object of objective.json has no row or a non-keep row no card.
+"""
+import collections, json, re, subprocess, sys
+from pathlib import Path
+
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
+repo = repo_root(__file__)
+path = Path(sys.argv[1]) if len(sys.argv) > 1 else repo / "dev/audit/yardstick/round11/EVALUATION.json"
+ev = json.loads(path.read_text())
+sys.path.insert(0, str(repo / "tools/audit"))
+import check_scopes as cs
+
+tree = [t for t in subprocess.run(["git", "-C", str(repo), "ls-files"], capture_output=True, text=True).stdout.split("\n") if t]
+spec = json.loads((repo / "dev/audit/config/objective.json").read_text())
+rows, cards, bad = ev["objects"], ev["cards"], []
+tot = collections.Counter()
+print("class\tobjects\tkeep\tchange\tremove\tNO-READ")
+for cls, globs in spec["objects"].items():
+    c = collections.Counter()
+    objs = sorted(cs.match(tree, globs))
+    for f in objs:
+        r = rows.get(f)
+        if not r:
+            bad.append(f"{f}: no row"); continue
+        c[r["verdict"]] += 1
+        c["NO-READ"] += r["verdict"] == "keep" and cs.is_no_read(r["evidence"])
+        if r["verdict"] != "keep" and r.get("card") not in cards:
+            bad.append(f"{f}: {r['verdict']} names no card")
+    tot.update(c); tot["objects"] += len(objs)
+    print(f"{cls}\t{len(objs)}\t{c['keep']}\t{c['change']}\t{c['remove']}\t{c['NO-READ']}")
+print(f"TOTAL\t{tot['objects']}\tkeep={tot['keep']}\tchange={tot['change']}\tremove={tot['remove']}\tNO-READ={tot['NO-READ']}\tunscored share {tot['NO-READ']}/{tot['objects']} ({tot['NO-READ'] / max(tot['objects'], 1):.2f})")
+t = ev.get("terms", {})
+print(f"TERMS\t{len(t)}\tread={sum('value' in v for v in t.values())}\tNO-READ={sum('no_read' in v for v in t.values())}")
+kinds = collections.Counter()
+for cid, c in cards.items():
+    kinds["threshold" if c.get("threshold") else "criterion" if c.get("criterion") else "unowned" if c.get("unowned") else
+          "object" if any(r.get("card") == cid for r in rows.values()) else "no-read or other"] += 1
+print(f"CARDS\t{len(cards)}\t" + "\t".join(f"{k}={v}" for k, v in sorted(kinds.items())) + f"\tdecided={sum(1 for c in cards.values() if c.get('decision'))}")
+for b in bad:
+    print("REFUSED", b)
+sys.exit(1 if bad else 0)
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index eb5c2feced..d4674f29de 100644
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
@@ -965,9 +965,9 @@
  {
   "id": "C108",
   "source": "README.md + docs/*.md",
-  "claim": "every relative link resolves (92 links)",
+  "claim": "every relative link resolves (93 links)",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "92 links, broken=[], of which removed-by-the-export=[]",
+  "result": "93 links, broken=[], of which removed-by-the-export=[]",
   "verdict": "true",
   "truth": ""
  },
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index 2637058615..805dbac25d 100644
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
@@ -111,7 +111,7 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C105 | `docs/automations.md` | the Power Headroom sensor appears once anything bounds the house -- a main fuse OR a capacity tariff -- and a tariff-only install reads 0.0 kW with limit_source='capacity tariff with no peak reference yet' until the month's first metering window closes; with neither it stays unavailable | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | no fuse + capacity tariff enabled -> {'available': True, 'limit_kw': 0.0, 'headroom_kw': 0.0, 'baseline_source': 'planned power only (no meter)', 'limit_source': 'capacity tariff with no peak reference yet'}; fuse only -> available=True; neither -> available=False | **true** |  |
 | C106 | `docs/automations.md` | Power Headroom is min(main fuse, capacity threshold) - current house draw, clamped at zero, in kW | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | fuse 20 A 3-phase -> limit_kw=13.8, headroom_kw=13.8, limit_source='main fuse' | **true** |  |
 | C107 | `README.md + docs/*.md + the card` | every entity id quoted in the documentation is an entity the platforms construct | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 9 distinct ids cited, not constructed=[] | **true** |  |
-| C108 | `README.md + docs/*.md` | every relative link resolves (92 links) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 92 links, broken=[], of which removed-by-the-export=[] | **true** |  |
+| C108 | `README.md + docs/*.md` | every relative link resolves (93 links) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 93 links, broken=[], of which removed-by-the-export=[] | **true** |  |
 | C109 | `README.md + docs/how-it-works.md` | the links to docs/audit-2026-08.md, docs/audit-2026-09.md and docs/backlog.md resolve | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | finder_wall in tools/audit/prepare_baseline.sh removes docs/audit-*.md, dev/archive/audits/audit-*.md and dev/archive/backlog.md; this tree cannot answer | **unverifiable** | not checkable in the export -- finder_wall removes docs/audit-*.md, dev/archive/audits/audit-*.md and dev/archive/backlog.md |
 | C110 | `README.md + docs/*.md` | every image the documentation embeds exists (21 images) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 21 images, missing=[] | **true** |  |
 | C111 | `README.md + docs/*.md` | every external link answers 200 to a HEAD request (21 links) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py --links` | not run: pass --links | **unverifiable** | re-run with --links |
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
diff --git a/dev/audit/yardstick/round11/EVALUATION.json b/dev/audit/yardstick/round11/EVALUATION.json
new file mode 100644
index 0000000000..a145946887
--- /dev/null
+++ b/dev/audit/yardstick/round11/EVALUATION.json
@@ -0,0 +1,2115 @@
+{
+ "round": 11,
+ "reads": "dev/audit/yardstick/round10/OBJECTIVE.json",
+ "evaluator": "r11-evaluator (Fable 5.2)",
+ "reviewer": "r11-evaluation-reviewer (Fable 5.2)",
+ "review": {
+  "verdict": "approve",
+  "sha": "83dc9488180379b859042b5f24b87d94a5a02c95",
+  "round": 4,
+  "scope": "Delta only: `git diff c6ce415b7711d76cf6c08f926f30da91f7bda924 83dc9488180379b859042b5f24b87d94a5a02c95`, the `revision_4` block, read against origin/main 030a4d377f9f26f5b8befe5721d86aea454f29e0. No full re-review was made. The round-3 approve of 02a48db212e0e49af62863575cba86bc339d4958 is commit 92991d2a49cf72d182d3a8ac32ca378cca83069b on this line.",
+  "delta": [
+   {
+    "id": "R4-1",
+    "state": "confirmed",
+    "measured": "`git merge-base --is-ancestor 1ed1329e41 origin/main` -> rc 0 and its diff deletes dev/governance/roles/nudge.md; the row is dropped and nothing else of `objects` is removed."
+   },
+   {
+    "id": "R4-2",
+    "state": "confirmed",
+    "measured": "`python3 -I dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref 030a4d377f --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` -> rc 0, OBJECTS 128, rows enumerate.py 956 0 0 0 0, finder_overlap.py 263 0 0 0 0, plant_recall.py 443 0 0 0 0, round_metrics.py 452 0 0 0 0: the four new `keep` rows carry these figures. 267655f306, 2e7bced82e and 6c87325160 each add the guide named and none is an ancestor of v10.0.0 (rc 1). Each row is `keep` on a NO-READ yield with card E11-N-INSTRUMENT-YIELD as the builder; none is a `remove`."
+   },
+   {
+    "id": "R4-3",
+    "state": "confirmed",
+    "measured": "each of the 17 `merged` commits is on origin/main's first-parent line, an ancestor of origin/main (rc 0), no ancestor of 02a48db212, c6ce415b77 or 83dc948818 (rc 1 each), and `git diff --name-only <merged>^1 <merged>` names the card's object or a path: b94425b94f (pull request 3647) COMMON.md; f1520e3539 (3625) D0, D1, D2, D8, D9, D12, D15; 511cf165f7 (3618) D3, D4, D5, D6, D7, D10, D14; 62f6bb2006 (3642) D11; 921214bf42 (3626) orchestrator.md. Both `merged_note's hold: 511cf165f7 also changes D11.md, and 646352ff13 changes dev/audit/yardstick/round10/OBJECTIVE.json."
+   },
+   {
+    "id": "R4-4",
+    "state": "confirmed",
+    "measured": "check_scopes.py's own `match(tree, object_globs(spec))` over objective.json and the tree at origin/main 030a4d377f gives 201 objects; the record rows 201; none unrowed, none extra. Tally 176 keep, 23 change, 2 remove; 48 cards, 43 accepted and 5 deferred. A key-by-key comparison of the two records finds no verdict, evidence, `decision`, `ruling` or `gates_finders` moved outside the changes `revision_4` lists."
+   },
+   {
+    "id": "R4-5",
+    "state": "confirmed",
+    "measured": "both `remove's re-read at origin/main: `git grep -n -o claude/audit-fix-` -> one pattern in each script; `gh pr list --state all --search head:claude/audit-fix-` -> 9 pull requests, 2026-09-02T01:01:32Z to 2026-09-03T06:47:47Z, before v6.6.12 (2026-09-25); `git log -S RETIRED` -> 785963eba4 2026-09-08 for each; 37 and 109 lines at a39627da59 and at v7.0.0; 0 first-parent merges touched either in v7.0.0..v10.0.0 or since."
+   },
+   {
+    "id": "R4-6",
+    "state": "no false move found",
+    "measured": "E11-N-P744-SCOPE's new path, attacked for recording the card merged on a commit that builds neither read (0018 section 5: `defer scope`; a verdict moved with no read behind it). The one merge on main after the review sha that touches a path of the card is d4968fe08b (pull request 3644), and it changes scorecard.py, already a path, as well as round_metrics.py: the added path makes no commit eligible that was not. `merged` stays unset. `git grep -c -i -E closure_slip|unexamined origin/main -- tools/audit/seat/round_metrics.py` -> no match; at pull request 3658's head e91759e2fc -> 17, so the file is where the two reads are built."
+   },
+   {
+    "id": "R4-7",
+    "state": "as expected",
+    "measured": "`python3 -I tools/audit/check_scopes.py --repo . --ref <a scratch merge of origin/main 030a4d377f and this review commit> --round 11`: the result is in this commit's message, since the commit cannot name its own run."
+   }
+  ],
+  "notes": [
+   {
+    "id": "Q1",
+    "touches": "record only, no card's ruling",
+    "note": "check_scopes.py reads only that `merged` touches a path. d4968fe08b would pass that rule for E11-N-P744-SCOPE today, before and after this revision, and builds neither `closure_slip` nor `unexamined`. Whoever records the card's `merged` records the later of pull requests 3657 and 3658 once both are on main, and never 3644."
+   },
+   {
+    "id": "Q2",
+    "touches": "record only, no card's ruling",
+    "note": "The card's `paths_note` says round_metrics.py `is the enumerator that reads` the two terms and that pull request 3658 `changes only it among the tools`. On main it does not read them yet, and 3658 also changes tools/audit/seat/round_metrics_selftest.py and the guide. Neither moves a path or a ruling."
+   },
+   {
+    "id": "Q3",
+    "touches": "record only, no card's ruling",
+    "note": "The 17 `merged` reads were checked to check_scopes.py's rule and by each merge's file list, not by re-reading each brief against its card's proposal: that is each pull request's own review."
+   },
+   {
+    "id": "Q4",
+    "touches": "record only, no card's ruling",
+    "note": "P1 and P2 of the round-3 review stand: E11-N-INSTRUMENT-YIELD still has an empty `paths`, and D16.md and D17.md are not on main."
+   }
+  ]
+ },
+ "graded": {
+  "sha": "a39627da59acbfdcd576e87349167603e9dec734",
+  "window": "2026-10-14T13:27:06Z..2026-11-15T05:22:47Z",
+  "window_from": "v7.0.0 (the round-9 closeout stamp)",
+  "window_to": "v10.0.0 (13cbe48de4, the round-10 closeout stamp)",
+  "roster": "cbd6d9185166:dev/programme/rosters/wave-r10-groups.json (the tip of handoff/audit-r10-roster when the evaluation was first written; every roster command names this commit)",
+  "record": "dev/audit/yardstick/round10/OBJECTIVE.json: absent in every ref",
+  "evidence": "dev/audit/rounds/round11/evaluation/ holds the scripts this record's commands name; `escapes_hand.tsv` there is the by-hand escapes read. GitHub was read only through `gate_reds.py fetch`, the nightly count and one `gh pr list` for the retired scripts' branch pattern."
+ },
+ "terms": {
+  "regret": {
+   "record": "absent",
+   "no_read": "no enumerator: no same-information oracle, no realised-cost record per install-day",
+   "would_read": "the oracle harness (D0's step) and the realised-cost record from a bundle (D15's step)",
+   "builder": "R11-INTAKE-R10-RESIDUE",
+   "proxy": "`tests/optimality.py` reads the solver against its own model; a heavy suite this seat does not run (the tests / fast job on main is the record that reads it)"
+  },
+  "operation": {
+   "record": "absent",
+   "no_read": "no enumerator: no cell ledger over write and hold sites times plan states",
+   "would_read": "the actuator-write dimension's cell ledger",
+   "builder": "R11-INTAKE-R10-RESIDUE",
+   "lead": "`git grep -n 'async_call(' -- custom_components/ | wc -l` -> 8 candidate write sites at the graded SHA; 6 of the 7 unowned items of the hand ledger are defects of this term, and so is the stuck set-point the ledger gives D1"
+  },
+  "generality": {
+   "record": "absent",
+   "no_read": "the examined count has no enumerator (no cell ledger)",
+   "would_read": "D12's cell ledger",
+   "builder": "R11-INTAKE-R10-RESIDUE",
+   "denominator": {
+    "enumerator": "python3 tools/audit/check_scopes.py --repo . --ref a39627da59 --population",
+    "levels": 195,
+    "pairs": 18696,
+    "no_read_axes": 2
+   },
+   "lead": "defects the owner's install could not have shown: 11 of the 26 in-window rows of the hand ledger were reported by an outside install"
+  },
+  "unowned": {
+   "record": "absent",
+   "no_read": "no enumerator: `escapes` records no owner",
+   "would_read": "`escapes` once it records its owning dimension",
+   "builder": "R11-INTAKE-R10-RESIDUE",
+   "by_hand": {
+    "value": 7,
+    "command": "python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --ref a39627da59 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json",
+    "cards": [
+     "E11-U1",
+     "E11-U10",
+     "E11-U2",
+     "E11-U4",
+     "E11-U5",
+     "E11-U6",
+     "E11-U7",
+     "E11-U8",
+     "E11-U9"
+    ]
+   }
+  },
+  "escapes": {
+   "record": "absent",
+   "no_read": "no enumerator: the roster records no found-by and no owning dimension (`source` is set on 31 of 545 groups)",
+   "would_read": "the escapes record with found-by and owner, and the series R11-PRE-ROUND-METRICS prints",
+   "builder": "R11-INTAKE-R10-RESIDUE",
+   "by_hand": {
+    "in_window": 26,
+    "dated_the_stamp_day": 6,
+    "per_owner": {
+     "D0": 1,
+     "D1": 5,
+     "D2": 5,
+     "D4": 2,
+     "D6": 1,
+     "D8": 2,
+     "D10": 1,
+     "D12": 1,
+     "D15": 1,
+     "none": 7
+    },
+    "reporters": {
+     "owner": 14,
+     "outside": 11,
+     "fixer": 0,
+     "programme": 1
+    },
+    "candidates": 76,
+    "ruled_out": 43,
+    "command": "python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --ref a39627da59 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json",
+    "rule": "every roster group at the pinned commit that lists a product file and is an owner, bug, hotfix or outside group or whose brief matches escapes.py's REPORT pattern has one row; escapes.py refuses a candidate with no row"
+   },
+   "beside": {
+    "removed_floor": 54,
+    "standing_findings": 94,
+    "command": "python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json",
+    "releases_in_window": 24,
+    "note": "the judge's 9 verdicts whose id carries no dimension prefix (7 standing, 3 in a done group) are in neither figure; `dimension_read.py` prints them as the row `other`"
+   },
+   "proxy": "`scorecard.py` line `E`: unread (roster.json)"
+  },
+  "injected": {
+   "record": "absent",
+   "no_read": "no enumerator reads a cause; of the four causes named by hand, three are named by a root-cause record (two by a tracked one, one by a record that is not on main)",
+   "would_read": "the cause named on the fixing group by the root-cause seat",
+   "builder": "R11-INTAKE-R10-RESIDUE",
+   "by_hand": {
+    "named_causes": 4,
+    "named_by_a_root_cause_record": 3,
+    "production_merges_in_window": 155,
+    "per_100": 2.58,
+    "denominator_command": "python3 tools/audit/machinery_ratchet.py --measure --repo . --head 13cbe48de4 --window 1139",
+    "note": "pull request 3404 (the stuck set-point; cause named by R10-RCA-SETPOINT-LATCH-DEADLOCK.md on archive/handoff-wip/r10-rca-setpoint-latch-deadlock), pull requests 2411 and 2887 (R10-HOTFIX-SAV-ESTIMATE; both named by the tracked dev/audit/rca/R10-RCA-SAV-ESTIMATE.md; 2411 also by R10-SAVINGS-NEGATIVE's brief), pull request 3587 (R10-HOTFIX-REFERENCE-BASIS; the fixing group's word, caught before a release, so injected and no escape)"
+   },
+   "proxy": "`scorecard.py` line `H`: unread (merges.tsv)"
+  },
+  "product_green": {
+   "record": "absent",
+   "no_read": "its named enumerator prints `A_gate  unread (runs.json)`: no input producer, and the line has no window",
+   "would_read": "`scorecard.py report` line `A_gate` once fed and windowed",
+   "builder": "R11-PRE-ROUND-METRICS",
+   "proxy": {
+    "command": "python3 dev/audit/rounds/round11/evaluation/gate_reds.py report --dir <fetched> --window 2026-10-14T13:27:06Z..2026-11-15T05:22:47Z (after its `fetch`; GitHub reads only)",
+    "runs": "runs 830 first 2026-10-23T23:53:36Z cancelled=198 failure=291 success=341",
+    "gate_share": "528/632 (0.835); cancelled beside it: 198; failed runs whose gate job succeeded: 187; failed runs read: 291; unread: 0",
+    "only_failed_job_on_gate_red_runs": {
+     "tests / ci-ratchet": 69,
+     "several": 19,
+     "tests / fast (3.14)": 12,
+     "governance / instrument-self-tests": 3,
+     "none": 1
+    },
+    "note": "the CI workflow's first push run on main is dated 2026-10-23: nine days of the window have no `CI` run. `tests / ci-ratchet` left the push-required set at ef4556bb42 (2026-11-12), so the share is not one series across that commit; `gate`'s check count is 17 at the graded SHA"
+   }
+  },
+  "coverage": {
+   "record": "absent",
+   "no_read": "no enumerator: no report row carries examined over universe",
+   "would_read": "the per-step denominator in the finder's reports",
+   "builder": "R11-INTAKE-R10-RESIDUE",
+   "proxy": {
+    "command": "python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json",
+    "rows": 113,
+    "rows_with_examined_universe": 0,
+    "rows_stating_a_count_in_prose": 34,
+    "dimensions_with_a_step_no_seat_ran_deep": 11
+   },
+   "live_control": "python3 tools/audit/check_scopes.py --repo . --ref a39627da59 -> rc 0, unclassified=0"
+  },
+  "unexamined": {
+   "record": "absent",
+   "no_read": "no enumerator: no pass reports a universe over a late merge",
+   "would_read": "a read from the roster's group kinds and the examining passes' denominators",
+   "builder": "R11-PRE-ROUND-METRICS",
+   "lead": "the finder baseline is 17f1c55fad1b (2026-10-14, two hours after the window opened); the window holds 155 production merges by `machinery_ratchet.py`'s class, and the one later pass on record is the catch-up judged at d749c986d"
+  },
+  "first_pass": {
+   "record": "absent",
+   "value": {
+    "flow_metrics": 0.506,
+    "review_strength": 0.514
+   },
+   "enumerator": "python3 tools/audit/seat/flow_metrics.py --repo . --window 2026-10-14T13:27:06Z..2026-11-15T05:22:47Z --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json --prefix R10-",
+   "second_enumerator": "python3 tools/audit/seat/review_strength.py --repo . --window r10=2026-10-14T13:27:06Z..2026-11-15T05:22:47Z",
+   "detail": "flow_metrics.py: 436/862 merged fix pull requests with a bus verdict (18 merged with none); review_strength.py: 467/909 reviewed pull requests, real-catch incidence 214/909. The two enumerators 0018 names count different populations. Most frequent first blocks: mutation-vacuous 62, carry-missing 56, class-open 53, harness 26, ci-red 25 first blocks.",
+   "round_9": "`python3 tools/audit/seat/review_strength.py --repo . --window r9=2026-09-25T12:54:39Z..2026-10-14T13:27:06Z` (v6.6.12, the last stamp before round 9's baseline, to v7.0.0) -> first-pass 28/76 (0.368), real-catch incidence 19/76 (0.25). Both rounds are read here for the first time, so by 0018 section 2 this sets the baseline and is no move; the difference (0.146 against two standard errors of 0.116) is stated and ranks nothing."
+  },
+  "lead_time": {
+   "record": "absent",
+   "no_read": "`flow_metrics.py` prints merge hours only (517 of 759 hours had a merge; 1135 merges)",
+   "would_read": "hours from the roster commit that added a group to its merge, p50 and p90",
+   "builder": "R11-PRE-ROUND-METRICS"
+  },
+  "closure_slip": {
+   "record": "absent",
+   "no_read": "the forecast history exists only inside rendered plan pages",
+   "would_read": "the plan history after the register",
+   "builder": "R11-PRE-ROUND-METRICS",
+   "lead": "round start to closure: v7.0.0 (2026-10-14) to v10.0.0 (2026-11-15), 31.7 days by the two tags' commit times"
+  },
+  "tokens_per_change": {
+   "record": "absent",
+   "no_read": "no token ledger: every seat class is unledgered",
+   "would_read": "the ledger keyed by group, role and dimension",
+   "builder": "R11-PRE-TOKEN-LEDGER",
+   "beside": "`python3 tools/audit/machinery_ratchet.py --measure --repo . --head 13cbe48de4 --window 1139` -> the window's 1139 merges: production 155, machinery 516, record 468; churn 15167 nonproduct lines per 1000 product lines"
+  }
+ },
+ "not_followed": [
+  {
+   "clause": "0018 section 6, Reads: `the closing round's OBJECTIVE.json in its directory under dev/audit/yardstick/ ... which the orchestrator writes at closure`",
+   "why": "No such file exists in any ref. The evaluator could re-read no recorded term; `terms` holds this seat's own run of each enumerator instead, and card E11-N-OBJECTIVE-RECORD carries the gap."
+  },
+  {
+   "clause": "evaluator.md step 1: `the closing round's objective and judge records`",
+   "why": "The judge records were read; the objective record does not exist (as above)."
+  },
+  {
+   "clause": "0018 section 2: `The window of round N runs from the previous closeout stamp to its own (decision 0016)`",
+   "why": "Round 9's closeout is tagged v7.0.0 (`v7.0.0: stamp Round-9 closure`), not 9.0.0: decision 0016 landed during round 10. The window used here is v7.0.0's commit time to v10.0.0's. Round 9's own window, used for the two-round reads, is taken from v6.6.12 (`stamp round-8 fix wave`, the last stamp before round 9's audit baseline) to v7.0.0: no stamp is labelled round 8's closure."
+  },
+  {
+   "clause": "0018 section 2, `product_green`: `share of main's concluded CI push runs in the window`",
+   "why": "The `CI` workflow's first push run on main is dated 2026-10-23; before it the lanes ran as separate workflows, so the definition reads nine days of the window as empty."
+  },
+  {
+   "clause": "0018 section 3, remove: `measured yield of zero in two consecutive rounds`",
+   "why": "Followed where a two-round read exists. It exists for the two retired workflow scripts (the pull requests of their branch pattern, zero in both rounds: `remove`, card E11-R-WORKFLOWS) and for the fixer and fix-review roles (`review_strength.py` over round 9's window, not zero). No rule, instrument or other gate has a yield enumerator in either round, and `standing-tick.md` and `standing-roster.md` did not exist in round 9, so no other object can meet the clause at this evaluation."
+  },
+  {
+   "clause": "0018 section 3, dimension row: `found and escapes yes (judge record; escapes by hand)`",
+   "why": "Followed, by hand: the ledger `escapes_hand.tsv` rows every one of the 76 roster groups its stated rule selects at the pinned roster commit, 26 as escapes and 43 ruled out with the reason. The roster records no reporter time, so 7 owner reports dated the closeout stamp's own day are listed apart and counted in no verdict."
+  },
+  {
+   "clause": "0018 section 3, standing seat row: `local seats by hand from transcripts`",
+   "why": "Not followed: this seat was given no transcripts and re-runs only tracked commands; the standing roles are kept on a NO-READ."
+  },
+  {
+   "clause": "0018 section 6, Writes: `reviewer`, `review` (the reviewer's `verdict` and the `sha` it was given at)",
+   "why": "Left null by the evaluator: they are the reviewer's two fields. The first review (`Evaluation review: revise 33d89b15f3a7`, six findings and fourteen notes) is on the ref `eval-review/r11`; `revision` in this record lists what each finding changed."
+  },
+  {
+   "clause": "0018 section 6, Writes: cards carry `decision` with `ruling`, and `merged`",
+   "why": "Left out of every card: the evaluator never writes a ruling. `check_scopes.py --round 11` therefore prints one gap per card until each is ruled, which is the record's design. Each card carries `finder_critical`, a classification for the orchestrator and no ruling."
+  },
+  {
+   "clause": "objective.json `seats`: evaluator.md `on the model objective.json's seats names (unset: ask the owner)`",
+   "why": "Both are null. The seat ran on Fable on the dispatch brief's statement of the owner's ruling of 2026-11-15; card E11-S-SEATS."
+  },
+  {
+   "clause": "0018 section 1 table, D3, D4 and D15 enumerators (`tests/mutation_table.py --scope full`, `node tests/card_browser.mjs`, `tools/replay/debug_replay.py --bundle`)",
+   "why": "Not re-run by this seat: the full mutation table is the nightly's job, the card lane is a heavy suite, and the seat holds no bundle. Each is NO-READ here with the record that reads it: the Nightly workflow's mutation lane, the card lane of main's CI run at the graded SHA, and the owner's bundle for D15. D6's and D7's (`tests/doc_claims.py`, `tests/structure.py`) were re-run in this revision and are in those rows; `tools/audit/archscore/score.py --diff` against decision 0015's target was not run."
+  },
+  {
+   "clause": "0018 section 6, Refuses: `an evaluator and reviewer that are one name under case and punctuation, or either the orchestrator`",
+   "why": "`check_scopes.py --round` does not refuse a null reviewer (it normalises to `none`); card E11-N-NULL-REVIEWER."
+  }
+ ],
+ "revision": {
+  "of": "33d89b15f3a78836d880ade41dd28ecb9f7e1af1",
+  "review": "Evaluation review: revise 33d89b15f3a78836d880ade41dd28ecb9f7e1af1 (reviewer's fields on the ref eval-review/r11)",
+  "changes": {
+   "R1": "escapes_hand.tsv rebuilt on a stated rule over the pinned roster cbd6d9185166, enforced by escapes.py: 76 candidates, each rowed (30 `in`, 7 `day0`, 1 `unreleased`, 38 `out` with the reason). New `in` rows: R10-SAVINGS-NEGATIVE (D2, cause #2411), R10-SETPOINT-BOOST (none), R10-MIN-POWER-FLOOR (D8), R10-SETPOINT-POWER (D0, ruled in), R10-FLY-REPLAY-MASK (D15, ruled in), and three the wider rule found: R10-DEMAND-OVERBOOK (D2), R10-BUFFER-STORE (D0), R10-COP-GATE-E (D2). R10-SAV-WOOD-MEASURED is `out` (the report R10-HOTFIX-SAV-ESTIMATE's row carries). Moved: terms.escapes.by_hand (22 to 30, per_owner), terms.injected.by_hand (2 to 3 causes), terms.generality.lead, terms.unowned; objects D0, D1, D2, D8, D15 (evidence) and cards E11-D0, E11-D1, E11-D2, E11-D8, E11-D15 (proposal, term); card E11-INJECTED (`28 of 30`).",
+   "R2": "card E11-INJECTED rewritten: it names the root-cause record on archive/handoff-wip/r10-rca-setpoint-latch-deadlock and HANDOVER.md lines 1546 to 1557, carries the record's two drafted texts as the owed item and proposes none of its own; terms.injected.no_read and by_hand say which cause a root-cause record names; objects fixer.md, fix-review.md, root-cause.md and defect-root-cause.md (evidence).",
+   "R3": "objects arch-score.yml, budget-raise-gate.yml, kernel-points.yml, pr-contract.yml (evidence): the zero on main's push runs is replaced by `not run on a push to main` with the work-set command, and a NO-READ naming the record that would read them (each merged pull request head's check runs).",
+   "R4": "card E11-GATE-REDS: part (b) withdrawn; the card now says it moves no check out of `gate`, names 0018 section 5's false move and its control, and gives the push-required set and the only-failed-job counts; `paths` loses nightly.yml. Objects ci.yml, tests.yml, governance.yml (evidence re-read against `gate.REQUIRED['push']`); object nightly.yml moves from `change` to `keep` (`product_green` is not taken through it). gate_reds.py prints the only failed job per gate-red run.",
+   "R5": "objects .claude/workflows/audit-fix.js and audit-wave.js move from `keep` to `remove` on the branch-pattern read, with card E11-R-WORKFLOWS; not_followed's remove clause rewritten; fixer.md and fix-review.md carry round 9's read (first-pass 28/76, real-catch 19/76).",
+   "R6": "R10-HOTFIX-FLOW-SETPOINT-STUCK re-owned from `none` to D1 (step 2: the previous release's persisted record driven to the first write); card E11-U3 withdrawn; card E11-D1 gains the input. The seven other unowned cards each argue the nearest brief out, and R10-SETPOINT-BOOST is new as E11-U9.",
+   "N0": "D6 and D7 rows carry `tests/doc_claims.py` (ALL 410 checks PASSED) and `tests/structure.py` (STRUCTURE RATCHET PASSED); tests/structure.py's own row and not_followed updated.",
+   "N1": "object D9 moves from `keep` to `change` with card E11-D9; D13's keep states why it stands.",
+   "N2": "every roster-derived command names cbd6d9185166; flow_metrics.py, instrument_cost.py, dimension_read.py, escapes.py and main_red_groups.py were re-run at that pin: flow_metrics.py and all 124 instrument_cost.py rows print the same figures, dimension_read.py the same 16 rows.",
+   "N3": "terms.injected.by_hand and card E11-INJECTED divide by 162 production merges (machinery_ratchet.py's class over the window's 1210 merges); terms.unexamined.lead and terms.tokens_per_change.beside use the same read.",
+   "N4": "main_red_groups.py matches `instrument[- ]self-tests`: 12 of the 20, in governance.yml's and ci.yml's evidence.",
+   "N5": "standing-tick.md and standing-roster.md (evidence): the files did not exist in round 9.",
+   "N6": "new card E11-N-NULL-REVIEWER (tools/audit/check_scopes.py); not_followed gains the clause.",
+   "N7": "card E11-N-OBJECTIVE-RECORD (cost): nothing live guards the unowned cards until the record exists.",
+   "N8": "card E11-K-D9 (proposal): what tests/stress_budgets.json holds and why it is no Pi budget.",
+   "N9": "card E11-D4 (cost): the environment a real frontend render needs.",
+   "N10": "cards E11-GATE-REDS and E11-N-GATE-CAUSE cite process card P7; card E11-N-OBJECTIVE-RECORD cites P747 and says how part (b) differs.",
+   "N13": "terms.coverage.proxy gains the 34 rows that state a count in prose (dimension_read.py prints it); terms.escapes.beside notes the 9 verdicts with no dimension prefix.",
+   "finder_critical": "every card carries the field, yes or no with the reason: a classification for the orchestrator, no ruling.",
+   "stands": "N11, N12 and the reviewer's `reproduced` list needed no change. The seven day-of-stamp rows stay out of every verdict, as the record says."
+  }
+ },
+ "revision_2": {
+  "of": "7891b714f8cd02bf9eb472a3ae74a32560843cd2",
+  "review": "Evaluation review: revise 7891b714f8cd02bf9eb472a3ae74a32560843cd2 (round 2, delta only); this revision is bounded to its findings",
+  "changes": {
+   "S1": "escapes_hand.tsv: R10-HOTFIX-SAV-ESTIMATE's `cause_pr` is `2411,2887`, from the tracked dev/audit/rca/R10-RCA-SAV-ESTIMATE.md; escapes.py prints CAUSES. terms.injected (no_read, by_hand: 4 causes, 3 named by a root-cause record, 2.47 per 100); card E11-INJECTED (proposal, term, null_control); objects fixer.md and fix-review.md (evidence: 4 cause pull requests).",
+   "S2": "`paths` are exact files: E11-U1 names dev/governance/dimensions/D17.md, E11-U2 and U4 to U10 name D16.md, E11-N-GATE-CAUSE names tools/ci/gate.py; E11-N-INSTRUMENT-YIELD carries an empty `paths` and says why none can be named. Each carries `paths_note`.",
+   "M1": "the four criterion cards: `finder_critical` reads no as the card stands, with the measure, the condition that makes it yes and the preliminary ruling as relayed; `proposal` gains the brief citing the file. Counts: 27 yes, 21 no.",
+   "M2": "R10-OUTSIDE-DHW-START-HYSTERESIS is rowed `in`, owner none, with new card E11-U10; R10-SAV-ACTUATION is rowed `day0` as its own write-timing defect (no verdict moves). terms.escapes.by_hand (31), terms.unowned (9), terms.generality.lead.",
+   "M3": "escapes_hand.tsv gains a header line on what the rule does not select and why R10-FLY-REPLAY-MASK is in.",
+   "M4": "R10-SETPOINT-BOOST's second cause (the draw range on censored samples) is in card E11-D2's inputs and named in E11-U9 and the ledger row.",
+   "M5": "terms.first_pass.round_9 and fixer.md's evidence reworded: a first read, the baseline, no move."
+  }
+ },
+ "objects": {
+  ".claude/hooks/always-fails.sh": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `.claude/hooks/always-fails.sh` 13 lines (13 at the window's start), 0 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix. A fixture whose self-test is meant to fail, wired into no settings file; it has no refusal to log."
+  },
+  ".claude/hooks/pre-bash.sh": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `.claude/hooks/pre-bash.sh` 365 lines (0 at the window's start), 3 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix."
+  },
+  ".claude/hooks/pre-edit.sh": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `.claude/hooks/pre-edit.sh` 222 lines (205 at the window's start), 2 merges touched it in the window, 3 roster group(s) name it, 0 of them hotfix."
+  },
+  ".claude/hooks/session-start.sh": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `.claude/hooks/session-start.sh` 229 lines (126 at the window's start), 3 merges touched it in the window, 1 roster group(s) name it, 0 of them hotfix."
+  },
+  ".claude/hooks/stop-selfcheck.sh": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `.claude/hooks/stop-selfcheck.sh` 224 lines (208 at the window's start), 3 merges touched it in the window, 1 roster group(s) name it, 0 of them hotfix."
+  },
+  ".claude/skills/steward/SKILL.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `.claude/skills/steward/SKILL.md` 132 lines (134 at the window's start), 1 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix."
+  },
+  ".claude/workflows/audit-find.js": {
+   "verdict": "keep",
+   "evidence": "NO-READ: a workflow script's runs, the refusals it made and what followed are logged nowhere tracked (card E11-N-GATE-CAUSE covers the read). Cost read: `git show a39627da59:.claude/workflows/audit-find.js | wc -l` -> 412 lines (`git show v7.0.0:.claude/workflows/audit-find.js | wc -l` -> 368); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .claude/workflows/audit-find.js | wc -l` -> 20 merges touched it in round 10's window."
+  },
+  ".claude/workflows/audit-fix.js": {
+   "verdict": "remove",
+   "evidence": "`grep -n -o 'claude/audit-fix-[^ ]*' .claude/workflows/audit-fix.js` -> the one branch pattern its fixer pushes to; `gh pr list --state all --search 'head:claude/audit-fix-' --json number,createdAt --limit 300` -> 9 pull requests, created 2026-09-02T01:01:32Z to 2026-09-03T06:47:47Z, so 0 inside round 9's window (v6.6.12, 2026-09-25, to v7.0.0) and 0 inside round 10's (v7.0.0 to v10.0.0); `git log -S RETIRED --format='%h %cI' -- .claude/workflows/audit-fix.js` -> 785963eba4 2026-09-08: its own description has said RETIRED since before round 9 opened. Measured yield (a fix or a review verdict it produced) is zero in two consecutive rounds, and `product_green`, `coverage` and every other layer-1 term are taken through other objects. The measure's limit: a run that pushed nothing leaves no pull request; the live fix scripts' `fix/` pattern shows 880 merged fix branches in round 10's window by `flow_metrics.py`, so the same measure is not zero where a script is in use. Cost read: `git show a39627da59:.claude/workflows/audit-fix.js | wc -l` -> 37 lines (`git show v7.0.0:.claude/workflows/audit-fix.js | wc -l` -> 37); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .claude/workflows/audit-fix.js | wc -l` -> 0 merges touched it in round 10's window.",
+   "card": "E11-R-WORKFLOWS"
+  },
+  ".claude/workflows/audit-plan.js": {
+   "verdict": "keep",
+   "evidence": "NO-READ: a workflow script's runs, the refusals it made and what followed are logged nowhere tracked (card E11-N-GATE-CAUSE covers the read). Cost read: `git show a39627da59:.claude/workflows/audit-plan.js | wc -l` -> 188 lines (`git show v7.0.0:.claude/workflows/audit-plan.js | wc -l` -> 0); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .claude/workflows/audit-plan.js | wc -l` -> 1 merges touched it in round 10's window."
+  },
+  ".claude/workflows/audit-verify.js": {
+   "verdict": "keep",
+   "evidence": "NO-READ: a workflow script's runs, the refusals it made and what followed are logged nowhere tracked (card E11-N-GATE-CAUSE covers the read). Cost read: `git show a39627da59:.claude/workflows/audit-verify.js | wc -l` -> 288 lines (`git show v7.0.0:.claude/workflows/audit-verify.js | wc -l` -> 260); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .claude/workflows/audit-verify.js | wc -l` -> 2 merges touched it in round 10's window."
+  },
+  ".claude/workflows/audit-wave.js": {
+   "verdict": "remove",
+   "evidence": "`grep -n -o 'claude/audit-fix-[^ ]*' .claude/workflows/audit-wave.js` -> the one branch pattern its fixer pushes to; `gh pr list --state all --search 'head:claude/audit-fix-' --json number,createdAt --limit 300` -> 9 pull requests, created 2026-09-02T01:01:32Z to 2026-09-03T06:47:47Z, so 0 inside round 9's window (v6.6.12, 2026-09-25, to v7.0.0) and 0 inside round 10's (v7.0.0 to v10.0.0); `git log -S RETIRED --format='%h %cI' -- .claude/workflows/audit-wave.js` -> 785963eba4 2026-09-08: its own description has said RETIRED since before round 9 opened. Measured yield (a fix or a review verdict it produced) is zero in two consecutive rounds, and `product_green`, `coverage` and every other layer-1 term are taken through other objects. The measure's limit: a run that pushed nothing leaves no pull request; the live fix scripts' `fix/` pattern shows 880 merged fix branches in round 10's window by `flow_metrics.py`, so the same measure is not zero where a script is in use. Cost read: `git show a39627da59:.claude/workflows/audit-wave.js | wc -l` -> 109 lines (`git show v7.0.0:.claude/workflows/audit-wave.js | wc -l` -> 109); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .claude/workflows/audit-wave.js | wc -l` -> 0 merges touched it in round 10's window.",
+   "card": "E11-R-WORKFLOWS"
+  },
+  ".claude/workflows/web-decomp-stage.js": {
+   "verdict": "keep",
+   "evidence": "NO-READ: a workflow script's runs, the refusals it made and what followed are logged nowhere tracked (card E11-N-GATE-CAUSE covers the read). Cost read: `git show a39627da59:.claude/workflows/web-decomp-stage.js | wc -l` -> 192 lines (`git show v7.0.0:.claude/workflows/web-decomp-stage.js | wc -l` -> 192); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .claude/workflows/web-decomp-stage.js | wc -l` -> 1 merges touched it in round 10's window."
+  },
+  ".claude/workflows/web-fix-wave.js": {
+   "verdict": "keep",
+   "evidence": "NO-READ: a workflow script's runs, the refusals it made and what followed are logged nowhere tracked (card E11-N-GATE-CAUSE covers the read). Cost read: `git show a39627da59:.claude/workflows/web-fix-wave.js | wc -l` -> 532 lines (`git show v7.0.0:.claude/workflows/web-fix-wave.js | wc -l` -> 523); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .claude/workflows/web-fix-wave.js | wc -l` -> 3 merges touched it in round 10's window."
+  },
+  ".claude/workflows/web-stamp.js": {
+   "verdict": "keep",
+   "evidence": "NO-READ: a workflow script's runs, the refusals it made and what followed are logged nowhere tracked (card E11-N-GATE-CAUSE covers the read). Cost read: `git show a39627da59:.claude/workflows/web-stamp.js | wc -l` -> 174 lines (`git show v7.0.0:.claude/workflows/web-stamp.js | wc -l` -> 157); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .claude/workflows/web-stamp.js | wc -l` -> 3 merges touched it in round 10's window."
+  },
+  ".claude/workflows/web-triage.js": {
+   "verdict": "keep",
+   "evidence": "NO-READ: a workflow script's runs, the refusals it made and what followed are logged nowhere tracked (card E11-N-GATE-CAUSE covers the read). Cost read: `git show a39627da59:.claude/workflows/web-triage.js | wc -l` -> 177 lines (`git show v7.0.0:.claude/workflows/web-triage.js | wc -l` -> 177); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .claude/workflows/web-triage.js | wc -l` -> 1 merges touched it in round 10's window."
+  },
+  ".github/workflows/arch-score.yml": {
+   "verdict": "keep",
+   "evidence": "Not run on a push to main: `python3 -I -c \"import sys; sys.path.insert(0,'tools/ci'); import prelude; print(sorted(prelude.workset('code','')))\"` -> ['codeql', 'governance', 'hassfest', 'tests', 'validate'], so main's push runs do not read it, and a count of its failed jobs there is an absence, not a yield. NO-READ: its reds on pull-request heads and their causes; the record that would read them is each merged pull request head's check runs (`commits/<sha>/check-runs`), which D13's required output 4 takes per check-run name. NO-READ: cost (runner seconds per merge: R11-PRE-ROUND-METRICS) and the split of its reds by cause (no red carries its cause: card E11-N-GATE-CAUSE). Cost read: `git show a39627da59:.github/workflows/arch-score.yml | wc -l` -> 105 lines (`git show v7.0.0:.github/workflows/arch-score.yml | wc -l` -> 93); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .github/workflows/arch-score.yml | wc -l` -> 2 merges touched it in round 10's window."
+  },
+  ".github/workflows/budget-raise-gate.yml": {
+   "verdict": "keep",
+   "evidence": "Not run on a push to main: `python3 -I -c \"import sys; sys.path.insert(0,'tools/ci'); import prelude; print(sorted(prelude.workset('code','')))\"` -> ['codeql', 'governance', 'hassfest', 'tests', 'validate'], so main's push runs do not read it, and a count of its failed jobs there is an absence, not a yield. NO-READ: its reds on pull-request heads and their causes; the record that would read them is each merged pull request head's check runs (`commits/<sha>/check-runs`), which D13's required output 4 takes per check-run name. NO-READ: cost (runner seconds per merge: R11-PRE-ROUND-METRICS) and the split of its reds by cause (no red carries its cause: card E11-N-GATE-CAUSE). Cost read: `git show a39627da59:.github/workflows/budget-raise-gate.yml | wc -l` -> 110 lines (`git show v7.0.0:.github/workflows/budget-raise-gate.yml | wc -l` -> 136); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .github/workflows/budget-raise-gate.yml | wc -l` -> 4 merges touched it in round 10's window."
+  },
+  ".github/workflows/ci.yml": {
+   "verdict": "change",
+   "evidence": "`python3 dev/audit/rounds/round11/evaluation/gate_reds.py report --dir <fetched> --window 2026-10-14T13:27:06Z..2026-11-15T05:22:47Z` (after its `fetch`; GitHub reads only) -> runs 830 first 2026-10-23T23:53:36Z cancelled=198 failure=291 success=341; gate share: 528/632 (0.835); cancelled beside it: 198; failed runs whose gate job succeeded: 187; failed runs read: 291; unread: 0. The workflow's first push run on main is dated 2026-10-23, so the share covers the window from that day (0018 section 2 defines `product_green` over `CI` push runs; before it the lanes ran as separate workflows). On the 104 runs whose `gate` did not succeed the only failed job was `tests / ci-ratchet` on 69, `tests / fast (3.14)` on 12, `governance / instrument-self-tests` on 3, none on 1 and several on 19. `tests / ci-ratchet` grades the CI run's own shape, not the product: 69 gate reds with no product cause, read through this gate. It left the push-required set at ef4556bb42 (2026-11-12, `PUSH_REPORT_ONLY`), so the share before and after that commit is not one series; `python3 -I -c \"import sys; sys.path.insert(0,'tools/ci'); import gate; print(gate.REQUIRED['push'])\"` prints 17 checks at the graded SHA, the count 0018 section 5 names as this term's control and no command prints per window. `python3 dev/audit/rounds/round11/evaluation/main_red_groups.py --repo . --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` -> GROUPS 31 HOTFIX 20 NAMING_SELF_TESTS 12: of the 20 hotfix groups that record a red main, 2 name a product cause by their briefs. NO-READ: cost (runner seconds per merge: R11-PRE-ROUND-METRICS) and the split of its reds by cause (no red carries its cause: card E11-N-GATE-CAUSE). Cost read: `git show a39627da59:.github/workflows/ci.yml | wc -l` -> 413 lines (`git show v7.0.0:.github/workflows/ci.yml | wc -l` -> 0); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .github/workflows/ci.yml | wc -l` -> 9 merges touched it in round 10's window.",
+   "card": "E11-GATE-REDS"
+  },
+  ".github/workflows/codeql.yml": {
+   "verdict": "keep",
+   "evidence": "Run on a push to main (`python3 -I -c \"import sys; sys.path.insert(0,'tools/ci'); import prelude; print(sorted(prelude.workset('code','')))\"` -> ['codeql', 'governance', 'hassfest', 'tests', 'validate']). `python3 dev/audit/rounds/round11/evaluation/gate_reds.py report --dir <fetched> --window 2026-10-14T13:27:06Z..2026-11-15T05:22:47Z` (after its `fetch`; GitHub reads only) -> 0 failed job(s) of this workflow on main's 291 failed push runs. NO-READ: cost (runner seconds per merge: R11-PRE-ROUND-METRICS) and the split of its reds by cause (no red carries its cause: card E11-N-GATE-CAUSE). Its reds on pull-request heads are unread at this seat (one job listing per run). Cost read: `git show a39627da59:.github/workflows/codeql.yml | wc -l` -> 235 lines (`git show v7.0.0:.github/workflows/codeql.yml | wc -l` -> 113); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .github/workflows/codeql.yml | wc -l` -> 10 merges touched it in round 10's window."
+  },
+  ".github/workflows/dependabot-automerge.yml": {
+   "verdict": "keep",
+   "evidence": "Not called by the CI workflow on a push to main, so the window's push runs do not read it. NO-READ: cost (runner seconds per merge: R11-PRE-ROUND-METRICS) and the split of its reds by cause (no red carries its cause: card E11-N-GATE-CAUSE). Its reds on pull-request heads are unread at this seat (one job listing per run). Cost read: `git show a39627da59:.github/workflows/dependabot-automerge.yml | wc -l` -> 129 lines (`git show v7.0.0:.github/workflows/dependabot-automerge.yml | wc -l` -> 0); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .github/workflows/dependabot-automerge.yml | wc -l` -> 2 merges touched it in round 10's window."
+  },
+  ".github/workflows/dependency-graph.yml": {
+   "verdict": "keep",
+   "evidence": "Not called by the CI workflow on a push to main, so the window's push runs do not read it. NO-READ: cost (runner seconds per merge: R11-PRE-ROUND-METRICS) and the split of its reds by cause (no red carries its cause: card E11-N-GATE-CAUSE). Its reds on pull-request heads are unread at this seat (one job listing per run). Cost read: `git show a39627da59:.github/workflows/dependency-graph.yml | wc -l` -> 82 lines (`git show v7.0.0:.github/workflows/dependency-graph.yml | wc -l` -> 0); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .github/workflows/dependency-graph.yml | wc -l` -> 2 merges touched it in round 10's window."
+  },
+  ".github/workflows/gate-sweep.yml": {
+   "verdict": "keep",
+   "evidence": "Not called by the CI workflow on a push to main, so the window's push runs do not read it. NO-READ: cost (runner seconds per merge: R11-PRE-ROUND-METRICS) and the split of its reds by cause (no red carries its cause: card E11-N-GATE-CAUSE). Its reds on pull-request heads are unread at this seat (one job listing per run). Cost read: `git show a39627da59:.github/workflows/gate-sweep.yml | wc -l` -> 56 lines (`git show v7.0.0:.github/workflows/gate-sweep.yml | wc -l` -> 0); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .github/workflows/gate-sweep.yml | wc -l` -> 4 merges touched it in round 10's window."
+  },
+  ".github/workflows/governance.yml": {
+   "verdict": "change",
+   "evidence": "`python3 dev/audit/rounds/round11/evaluation/gate_reds.py report --dir <fetched> --window 2026-10-14T13:27:06Z..2026-11-15T05:22:47Z` (after its `fetch`; GitHub reads only) -> 217 failed job(s) of this workflow on 205 of main's failed push runs: governance / instrument-self-tests x157; governance / record x58; governance / env-matrix x2. On the 104 runs whose `gate` did not succeed a job of this workflow failed on 20, and only its jobs on 3. `python3 dev/audit/rounds/round11/evaluation/main_red_groups.py --repo . --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` -> GROUPS 31 HOTFIX 20 NAMING_SELF_TESTS 12: 12 of the 20 main-red hotfix groups name the `instrument-self-tests` job (the self-test scope table, timeouts, a runner image change) and none of the 12 names a product fault; the job failed alone on 3 gate-red runs: reds with no product cause, read through this gate. `governance / record` failed on 9 gate-red runs, never alone, and is not in the push-required set at the graded SHA (`python3 -I -c \"import sys; sys.path.insert(0,'tools/ci'); import gate; print(gate.REQUIRED['push'])\"` holds `governance / policy-docs`, `governance / wave-script` and `governance / env-matrix` of this workflow). NO-READ: cost (runner seconds per merge: R11-PRE-ROUND-METRICS) and the split of its reds by cause (no red carries its cause: card E11-N-GATE-CAUSE). Cost read: `git show a39627da59:.github/workflows/governance.yml | wc -l` -> 2137 lines (`git show v7.0.0:.github/workflows/governance.yml | wc -l` -> 1065); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .github/workflows/governance.yml | wc -l` -> 74 merges touched it in round 10's window.",
+   "card": "E11-GATE-REDS"
+  },
+  ".github/workflows/hassfest.yml": {
+   "verdict": "keep",
+   "evidence": "Run on a push to main (`python3 -I -c \"import sys; sys.path.insert(0,'tools/ci'); import prelude; print(sorted(prelude.workset('code','')))\"` -> ['codeql', 'governance', 'hassfest', 'tests', 'validate']). `python3 dev/audit/rounds/round11/evaluation/gate_reds.py report --dir <fetched> --window 2026-10-14T13:27:06Z..2026-11-15T05:22:47Z` (after its `fetch`; GitHub reads only) -> 0 failed job(s) of this workflow on main's 291 failed push runs. NO-READ: cost (runner seconds per merge: R11-PRE-ROUND-METRICS) and the split of its reds by cause (no red carries its cause: card E11-N-GATE-CAUSE). Its reds on pull-request heads are unread at this seat (one job listing per run). Cost read: `git show a39627da59:.github/workflows/hassfest.yml | wc -l` -> 71 lines (`git show v7.0.0:.github/workflows/hassfest.yml | wc -l` -> 83); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .github/workflows/hassfest.yml | wc -l` -> 3 merges touched it in round 10's window."
+  },
+  ".github/workflows/kernel-points.yml": {
+   "verdict": "keep",
+   "evidence": "Not run on a push to main: `python3 -I -c \"import sys; sys.path.insert(0,'tools/ci'); import prelude; print(sorted(prelude.workset('code','')))\"` -> ['codeql', 'governance', 'hassfest', 'tests', 'validate'], so main's push runs do not read it, and a count of its failed jobs there is an absence, not a yield. NO-READ: its reds on pull-request heads and their causes; the record that would read them is each merged pull request head's check runs (`commits/<sha>/check-runs`), which D13's required output 4 takes per check-run name. NO-READ: cost (runner seconds per merge: R11-PRE-ROUND-METRICS) and the split of its reds by cause (no red carries its cause: card E11-N-GATE-CAUSE). Cost read: `git show a39627da59:.github/workflows/kernel-points.yml | wc -l` -> 110 lines (`git show v7.0.0:.github/workflows/kernel-points.yml | wc -l` -> 0); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .github/workflows/kernel-points.yml | wc -l` -> 3 merges touched it in round 10's window."
+  },
+  ".github/workflows/marketplace.yml": {
+   "verdict": "keep",
+   "evidence": "Not called by the CI workflow on a push to main, so the window's push runs do not read it. NO-READ: cost (runner seconds per merge: R11-PRE-ROUND-METRICS) and the split of its reds by cause (no red carries its cause: card E11-N-GATE-CAUSE). Its reds on pull-request heads are unread at this seat (one job listing per run). Cost read: `git show a39627da59:.github/workflows/marketplace.yml | wc -l` -> 33 lines (`git show v7.0.0:.github/workflows/marketplace.yml | wc -l` -> 0); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .github/workflows/marketplace.yml | wc -l` -> 1 merges touched it in round 10's window."
+  },
+  ".github/workflows/merge-main.yml": {
+   "verdict": "keep",
+   "evidence": "Not called by the CI workflow on a push to main, so the window's push runs do not read it. NO-READ: cost (runner seconds per merge: R11-PRE-ROUND-METRICS) and the split of its reds by cause (no red carries its cause: card E11-N-GATE-CAUSE). Its reds on pull-request heads are unread at this seat (one job listing per run). Cost read: `git show a39627da59:.github/workflows/merge-main.yml | wc -l` -> 193 lines (`git show v7.0.0:.github/workflows/merge-main.yml | wc -l` -> 181); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .github/workflows/merge-main.yml | wc -l` -> 2 merges touched it in round 10's window."
+  },
+  ".github/workflows/nightly.yml": {
+   "verdict": "keep",
+   "evidence": "`product_green` is not taken through this workflow: it is no part of the CI workflow's `gate`, and `tests / nightly-status` is not in the push-required set at the graded SHA. Cost lead: `gh api 'repos/<slug>/actions/workflows/nightly.yml/runs?branch=main&created=2026-10-14..2026-11-15&status=<c>&per_page=1' --jq .total_count` -> success 931, failure 39, cancelled 9 (its runs on main in the window, any event); round 10's roster names the causes of its reds as the lane's own (R10-HOTFIX-NIGHTLY-STATUS, R10-HOTFIX-REPLAY-CLASS-CUT, R10-NIGHTLY-ABSENT-NEW), which is the brief's word and no cause record. NO-READ: cost (runner seconds per merge: R11-PRE-ROUND-METRICS) and the split of its reds by cause (no red carries its cause: card E11-N-GATE-CAUSE). Cost read: `git show a39627da59:.github/workflows/nightly.yml | wc -l` -> 1213 lines (`git show v7.0.0:.github/workflows/nightly.yml | wc -l` -> 0); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .github/workflows/nightly.yml | wc -l` -> 12 merges touched it in round 10's window."
+  },
+  ".github/workflows/pages.yml": {
+   "verdict": "keep",
+   "evidence": "Not called by the CI workflow on a push to main, so the window's push runs do not read it. NO-READ: cost (runner seconds per merge: R11-PRE-ROUND-METRICS) and the split of its reds by cause (no red carries its cause: card E11-N-GATE-CAUSE). Its reds on pull-request heads are unread at this seat (one job listing per run). Cost read: `git show a39627da59:.github/workflows/pages.yml | wc -l` -> 186 lines (`git show v7.0.0:.github/workflows/pages.yml | wc -l` -> 138); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .github/workflows/pages.yml | wc -l` -> 2 merges touched it in round 10's window."
+  },
+  ".github/workflows/pr-contract.yml": {
+   "verdict": "keep",
+   "evidence": "Not run on a push to main: `python3 -I -c \"import sys; sys.path.insert(0,'tools/ci'); import prelude; print(sorted(prelude.workset('code','')))\"` -> ['codeql', 'governance', 'hassfest', 'tests', 'validate'], so main's push runs do not read it, and a count of its failed jobs there is an absence, not a yield. NO-READ: its reds on pull-request heads and their causes; the record that would read them is each merged pull request head's check runs (`commits/<sha>/check-runs`), which D13's required output 4 takes per check-run name. NO-READ: cost (runner seconds per merge: R11-PRE-ROUND-METRICS) and the split of its reds by cause (no red carries its cause: card E11-N-GATE-CAUSE). Cost read: `git show a39627da59:.github/workflows/pr-contract.yml | wc -l` -> 488 lines (`git show v7.0.0:.github/workflows/pr-contract.yml | wc -l` -> 330); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .github/workflows/pr-contract.yml | wc -l` -> 13 merges touched it in round 10's window."
+  },
+  ".github/workflows/release.yml": {
+   "verdict": "keep",
+   "evidence": "Not called by the CI workflow on a push to main, so the window's push runs do not read it. NO-READ: cost (runner seconds per merge: R11-PRE-ROUND-METRICS) and the split of its reds by cause (no red carries its cause: card E11-N-GATE-CAUSE). Its reds on pull-request heads are unread at this seat (one job listing per run). Cost read: `git show a39627da59:.github/workflows/release.yml | wc -l` -> 293 lines (`git show v7.0.0:.github/workflows/release.yml | wc -l` -> 172); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .github/workflows/release.yml | wc -l` -> 3 merges touched it in round 10's window."
+  },
+  ".github/workflows/tests.yml": {
+   "verdict": "change",
+   "evidence": "`python3 dev/audit/rounds/round11/evaluation/gate_reds.py report --dir <fetched> --window 2026-10-14T13:27:06Z..2026-11-15T05:22:47Z` (after its `fetch`; GitHub reads only) -> 112 failed job(s) of this workflow on 109 of main's failed push runs: tests / ci-ratchet x90; tests / fast (3.14) x20; tests / coverage x1; tests / coverage-ratchet x1. On the 104 runs whose `gate` did not succeed a job of this workflow failed on 99, and only its jobs on 83. `tests / ci-ratchet` failed alone on 69 gate-red runs: it grades the CI run's own shape (critical-path minutes, script runs; a cancelled run with no tests job), not the product, as roster groups R10-CI-RATCHET-RED and R10-HOTFIX-CI-RATCHET-SKIPPED-RUN say: reds with no product cause, read through this gate, until it became report-only on a push at ef4556bb42 (2026-11-12). `tests / fast (3.14)` failed alone on 12: product tests, whose cause (a product fault, a flaky probe) no red carries. NO-READ: cost (runner seconds per merge: R11-PRE-ROUND-METRICS) and the split of its reds by cause (no red carries its cause: card E11-N-GATE-CAUSE). Cost read: `git show a39627da59:.github/workflows/tests.yml | wc -l` -> 3179 lines (`git show v7.0.0:.github/workflows/tests.yml | wc -l` -> 4246); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .github/workflows/tests.yml | wc -l` -> 20 merges touched it in round 10's window.",
+   "card": "E11-GATE-REDS"
+  },
+  ".github/workflows/validate.yml": {
+   "verdict": "keep",
+   "evidence": "Run on a push to main (`python3 -I -c \"import sys; sys.path.insert(0,'tools/ci'); import prelude; print(sorted(prelude.workset('code','')))\"` -> ['codeql', 'governance', 'hassfest', 'tests', 'validate']). `python3 dev/audit/rounds/round11/evaluation/gate_reds.py report --dir <fetched> --window 2026-10-14T13:27:06Z..2026-11-15T05:22:47Z` (after its `fetch`; GitHub reads only) -> 1 failed job(s) of this workflow on main's 291 failed push runs. NO-READ: cost (runner seconds per merge: R11-PRE-ROUND-METRICS) and the split of its reds by cause (no red carries its cause: card E11-N-GATE-CAUSE). Its reds on pull-request heads are unread at this seat (one job listing per run). Cost read: `git show a39627da59:.github/workflows/validate.yml | wc -l` -> 24 lines (`git show v7.0.0:.github/workflows/validate.yml | wc -l` -> 36); `git log --first-parent --oneline v7.0.0..v10.0.0 -- .github/workflows/validate.yml | wc -l` -> 3 merges touched it in round 10's window."
+  },
+  "AGENTS.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield is its bug class's instances after the rule merged, and `python3 -c \"import json;j=json.load(open('dev/audit/config/bugclasses.json'));print(sum(isinstance(i,dict) for c in j.values() if isinstance(c,dict) for i in (c.get('instances') or [])))\"` -> 0: no instance carries a date; nothing counts a load or the seconds of a refusal (0018 section 3: not scorable at round 10's close; no roster group builds it: card E11-N-RULE-YIELD). Scored as a rule (0018 section 3); it states no policy and binds a seat to CLAUDE.md. Cost read: `git show a39627da59:AGENTS.md | wc -l` -> 12 lines (`git show v7.0.0:AGENTS.md | wc -l` -> 12); `git log --first-parent --oneline v7.0.0..v10.0.0 -- AGENTS.md | wc -l` -> 0 merges touched it in round 10's window."
+  },
+  "CLAUDE.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield is its bug class's instances after the rule merged, and `python3 -c \"import json;j=json.load(open('dev/audit/config/bugclasses.json'));print(sum(isinstance(i,dict) for c in j.values() if isinstance(c,dict) for i in (c.get('instances') or [])))\"` -> 0: no instance carries a date; nothing counts a load or the seconds of a refusal (0018 section 3: not scorable at round 10's close; no roster group builds it: card E11-N-RULE-YIELD). Scored as a rule (0018 section 3). Cost read: `git show a39627da59:CLAUDE.md | wc -l` -> 213 lines (`git show v7.0.0:CLAUDE.md | wc -l` -> 199); `git log --first-parent --oneline v7.0.0..v10.0.0 -- CLAUDE.md | wc -l` -> 10 merges touched it in round 10's window."
+  },
+  "dev/governance/dimensions/D0.md": {
+   "verdict": "change",
+   "evidence": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row D0: 2 judged, 2 stand (2 classed bug), 2 in a roster group at stage done (0 standing ids are in no group's `findings`, so removed is a floor); coverage rows 10 over 7 steps, depth {'deep': 7, 'spot': 3}, steps no seat ran deep: D0.M3,D0.M6, rows carrying examined/universe: 0. `python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --ref a39627da59 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` over `dev/audit/rounds/round11/evaluation/escapes_hand.tsv` (the by-hand read 0018 section 3 allows): 1 escape(s) in the window in this brief's territory (R10-SETPOINT-POWER). In the brief: step 4 names the grid in prose (price and weather profiles, topologies, horizons) and no command prints its cells; 0018 section 1 makes `regret` this brief's distance and names no step for the same-information oracle. Cost: NO-READ (its seats' tokens and wall clock: no ledger keys a seat by dimension; builder R11-PRE-TOKEN-LEDGER); the brief is 65 lines.",
+   "card": "E11-D0"
+  },
+  "dev/governance/dimensions/D1.md": {
+   "verdict": "change",
+   "evidence": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row D1: 7 judged, 7 stand (6 classed bug), 7 in a roster group at stage done (0 standing ids are in no group's `findings`, so removed is a floor); coverage rows 6 over 6 steps, depth {'deep': 4, 'spot': 2}, steps no seat ran deep: D1.M4,D1.M5, rows carrying examined/universe: 0. `python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --ref a39627da59 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` over `dev/audit/rounds/round11/evaluation/escapes_hand.tsv` (the by-hand read 0018 section 3 allows): 5 escape(s) in the window in this brief's territory (R10-HOTFIX-AWAY-LIVE, R10-HOTFIX-AWAY-PRESENCE, R10-OUTSIDE-PRICE-OUTAGE-LAST-VALID, R10-INPUT-REAPPEAR, R10-HOTFIX-FLOW-SETPOINT-STUCK). In the brief: step 2 says `Enumerate every persisted payload` and step 5 `Each swallowing try/except` with no command that prints either list; 0018 section 1 owes the census of paths, stores, timers, listeners and guards. Cost: NO-READ (its seats' tokens and wall clock: no ledger keys a seat by dimension; builder R11-PRE-TOKEN-LEDGER); the brief is 60 lines.",
+   "card": "E11-D1"
+  },
+  "dev/governance/dimensions/D10.md": {
+   "verdict": "change",
+   "evidence": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row D10: 1 judged, 1 stand (1 classed bug), 1 in a roster group at stage done (0 standing ids are in no group's `findings`, so removed is a floor); coverage rows 7 over 3 steps, depth {'deep': 5, 'spot': 2}, steps no seat ran deep: -, rows carrying examined/universe: 0. `python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --ref a39627da59 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` over `dev/audit/rounds/round11/evaluation/escapes_hand.tsv` (the by-hand read 0018 section 3 allows): 1 escape(s) in the window in this brief's territory (R10-OUTSIDE-DIAG-REDACT-LOCATION). In the brief: the rule list is in the brief (one check per rule), which is a denominator; the tier the checks are graded against is `owner_criteria.D10`, unset. Cost: NO-READ (its seats' tokens and wall clock: no ledger keys a seat by dimension; builder R11-PRE-TOKEN-LEDGER); the brief is 43 lines.",
+   "card": "E11-D10"
+  },
+  "dev/governance/dimensions/D11.md": {
+   "verdict": "change",
+   "evidence": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row D11: 2 judged, 2 stand (1 classed bug), 0 in a roster group at stage done (2 standing ids are in no group's `findings`, so removed is a floor); coverage rows 4 over 4 steps, depth {'spot': 4}, steps no seat ran deep: D11.M1,D11.M2,D11.M3,D11.M4, rows carrying examined/universe: 0. `python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --ref a39627da59 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` over `dev/audit/rounds/round11/evaluation/escapes_hand.tsv` (the by-hand read 0018 section 3 allows): 0 escapes in the window in this brief's territory. In the brief: step 3 instructs `Conformance, sampled, with the sample and how it was drawn stated`; all four steps ran at depth `spot`; 0018 section 1: a mechanism with neither a mutant arm nor a `--self-test` is NO-READ. Cost: NO-READ (its seats' tokens and wall clock: no ledger keys a seat by dimension; builder R11-PRE-TOKEN-LEDGER); the brief is 99 lines.",
+   "card": "E11-D11"
+  },
+  "dev/governance/dimensions/D12.md": {
+   "verdict": "change",
+   "evidence": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row D12: 2 judged, 2 stand (2 classed bug), 1 in a roster group at stage done (1 standing ids are in no group's `findings`, so removed is a floor); coverage rows 6 over 6 steps, depth {'deep': 5, 'spot': 1}, steps no seat ran deep: D12.M3, rows carrying examined/universe: 0. `python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --ref a39627da59 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` over `dev/audit/rounds/round11/evaluation/escapes_hand.tsv` (the by-hand read 0018 section 3 allows): 1 escape(s) in the window in this brief's territory (R10-OUTSIDE-LEARNER-ROBUSTNESS). In the brief: step 1 says `Derive the cell count; do not carry one` and names no command, while `python3 tools/audit/check_scopes.py --repo . --population` now prints the denominator 0018 gives this brief (195 levels, 18696 pairs, 2 NO-READ axes). Cost: NO-READ (its seats' tokens and wall clock: no ledger keys a seat by dimension; builder R11-PRE-TOKEN-LEDGER); the brief is 70 lines.",
+   "card": "E11-D12"
+  },
+  "dev/governance/dimensions/D13.md": {
+   "verdict": "keep",
+   "evidence": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row D13: 5 judged, 5 stand (3 classed bug), 5 in a roster group at stage done (0 standing ids are in no group's `findings`, so removed is a floor); coverage rows 6 over 6 steps, depth {'deep': 6}, steps no seat ran deep: -, rows carrying examined/universe: 0. `python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --ref a39627da59 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` over `dev/audit/rounds/round11/evaluation/escapes_hand.tsv` (the by-hand read 0018 section 3 allows): 0 escapes in the window in this brief's territory. Every step ran deep, no escape lies in its territory by the hand read, its yield is not zero, and each of its required outputs names its enumerator and population in the brief (`Each with its rule beside it and its enumerator named`); the missing examined/universe key is the finder contract's and the schema's (card E11-COMMON), not this brief's. Cost: NO-READ (its seats' tokens and wall clock: no ledger keys a seat by dimension; builder R11-PRE-TOKEN-LEDGER); the brief is 79 lines."
+  },
+  "dev/governance/dimensions/D14.md": {
+   "verdict": "change",
+   "evidence": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row D14: 3 judged, 3 stand (3 classed bug), 3 in a roster group at stage done (0 standing ids are in no group's `findings`, so removed is a floor); coverage rows 13 over 10 steps, depth {'deep': 9, 'spot': 4}, steps no seat ran deep: D14.M2,D14.M3,D14.M4,D14.M5, rows carrying examined/universe: 0. `python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --ref a39627da59 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` over `dev/audit/rounds/round11/evaluation/escapes_hand.tsv` (the by-hand read 0018 section 3 allows): 0 escapes in the window in this brief's territory. In the brief: step 2 instructs `Pick two or three open production classes`: `dev/audit/config/bugclasses.json` holds 19 classes at status `open` at the graded SHA (`python3 -c \"import json;print(sum(c.get('status')=='open' for c in json.load(open('dev/audit/config/bugclasses.json')).values() if isinstance(c,dict)))\"`); steps 2 to 5 ran at depth `spot` or not at all. Cost: NO-READ (its seats' tokens and wall clock: no ledger keys a seat by dimension; builder R11-PRE-TOKEN-LEDGER); the brief is 32 lines.",
+   "card": "E11-D14"
+  },
+  "dev/governance/dimensions/D15.md": {
+   "verdict": "change",
+   "evidence": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row D15: 5 judged, 0 stand (0 classed bug), 0 in a roster group at stage done (0 standing ids are in no group's `findings`, so removed is a floor); coverage rows 8 over 8 steps, depth {'none': 2, 'deep': 5, 'spot': 1}, steps no seat ran deep: D15.M5,D15.M7,D15.M8, rows carrying examined/universe: 0. `python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --ref a39627da59 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` over `dev/audit/rounds/round11/evaluation/escapes_hand.tsv` (the by-hand read 0018 section 3 allows): 1 escape(s) in the window in this brief's territory (R10-FLY-REPLAY-MASK). In the brief: `No real bundle: every step unfinished, no finding`; the bundle set is in no tracked list (0018 section 1: NO-READ); steps 5, 7 and 8 never ran deep and all five findings were judged unreproduced. Cost: NO-READ (its seats' tokens and wall clock: no ledger keys a seat by dimension; builder R11-PRE-TOKEN-LEDGER); the brief is 36 lines.",
+   "card": "E11-D15"
+  },
+  "dev/governance/dimensions/D2.md": {
+   "verdict": "change",
+   "evidence": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row D2: 6 judged, 5 stand (5 classed bug), 2 in a roster group at stage done (3 standing ids are in no group's `findings`, so removed is a floor); coverage rows 5 over 5 steps, depth {'deep': 2, 'spot': 3}, steps no seat ran deep: D2.M3,D2.M4,D2.M5, rows carrying examined/universe: 0. `python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --ref a39627da59 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` over `dev/audit/rounds/round11/evaluation/escapes_hand.tsv` (the by-hand read 0018 section 3 allows): 5 escape(s) in the window in this brief's territory (R10-HOTFIX-SAV-ESTIMATE, R10-HOTFIX-LEARNER-INPUTS, R10-OUTSIDE-DHW-CHARGE-SETTLE, R10-SAVINGS-NEGATIVE, R10-DEMAND-OVERBOOK), 2 more dated the stamp's own day. In the brief: steps 1 to 5 list identities in prose and `sweep`; no tracked list names the identities and their grid (0018 section 1: NO-READ). Cost: NO-READ (its seats' tokens and wall clock: no ledger keys a seat by dimension; builder R11-PRE-TOKEN-LEDGER); the brief is 53 lines.",
+   "card": "E11-D2"
+  },
+  "dev/governance/dimensions/D3.md": {
+   "verdict": "change",
+   "evidence": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row D3: 3 judged, 3 stand (1 classed bug), 3 in a roster group at stage done (0 standing ids are in no group's `findings`, so removed is a floor); coverage rows 15 over 5 steps, depth {'deep': 11, 'spot': 4}, steps no seat ran deep: D3.M5, rows carrying examined/universe: 0. `python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --ref a39627da59 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` over `dev/audit/rounds/round11/evaluation/escapes_hand.tsv` (the by-hand read 0018 section 3 allows): 0 escapes in the window in this brief's territory. In the brief: step 1 instructs a sample, verbatim `Sample 30–40 mutants with a recorded seed, no module more than four`, and step 3 keeps `the top six survivors`; 0018's enumerator for this brief is `python3 tests/mutation_table.py --scope full`. Cost: NO-READ (its seats' tokens and wall clock: no ledger keys a seat by dimension; builder R11-PRE-TOKEN-LEDGER); the brief is 46 lines.",
+   "card": "E11-D3"
+  },
+  "dev/governance/dimensions/D4.md": {
+   "verdict": "change",
+   "evidence": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row D4: 3 judged, 0 stand (0 classed bug), 0 in a roster group at stage done (0 standing ids are in no group's `findings`, so removed is a floor); coverage rows 3 over 3 steps, depth {'spot': 3}, steps no seat ran deep: D4.M1,D4.M2,D4.M3, rows carrying examined/universe: 0. `python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --ref a39627da59 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` over `dev/audit/rounds/round11/evaluation/escapes_hand.tsv` (the by-hand read 0018 section 3 allows): 2 escape(s) in the window in this brief's territory (R10-HOTFIX-CARD-HEALTH-TEXT, R10-OUTSIDE-VALVE-TARGET-LABEL), 2 more dated the stamp's own day. In the brief: step 1 drives `sv` and `en` while `check_scopes.py --population` prints three shipped languages (de, en, sv); the brief's own limit is `There is no Home Assistant frontend locally`; all three steps ran at depth `spot`. Cost: NO-READ (its seats' tokens and wall clock: no ledger keys a seat by dimension; builder R11-PRE-TOKEN-LEDGER); the brief is 48 lines.",
+   "card": "E11-D4"
+  },
+  "dev/governance/dimensions/D5.md": {
+   "verdict": "change",
+   "evidence": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row D5: 4 judged, 4 stand (0 classed bug), 4 in a roster group at stage done (0 standing ids are in no group's `findings`, so removed is a floor); coverage rows 7 over 4 steps, depth {'deep': 3, 'spot': 2, 'none': 2}, steps no seat ran deep: D5.M3, rows carrying examined/universe: 0. `python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --ref a39627da59 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` over `dev/audit/rounds/round11/evaluation/escapes_hand.tsv` (the by-hand read 0018 section 3 allows): 0 escapes in the window in this brief's territory. In the brief: steps 1 to 3 (reader paths, structure, content) name no universe command; only step 4 does (`text_ledger.py units --dim D5`); two round-10 rows read depth `none`. Cost: NO-READ (its seats' tokens and wall clock: no ledger keys a seat by dimension; builder R11-PRE-TOKEN-LEDGER); the brief is 41 lines.",
+   "card": "E11-D5"
+  },
+  "dev/governance/dimensions/D6.md": {
+   "verdict": "change",
+   "evidence": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row D6: 0 judged, 0 stand (0 classed bug), 0 in a roster group at stage done (0 standing ids are in no group's `findings`, so removed is a floor); coverage rows 9 over 3 steps, depth {'spot': 6, 'deep': 3}, steps no seat ran deep: -, rows carrying examined/universe: 0. 0018's enumerator for this brief, re-run on the graded tree (this worktree: the graded SHA plus the evaluation's own files): `python3 tests/doc_claims.py | tail -1` -> `ALL 410 checks PASSED`, rc 0: no registered claim is false; a claim outside its register stays unread (carries 173 and 178 on R11-INTAKE-R10-RESIDUE). `python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --ref a39627da59 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` over `dev/audit/rounds/round11/evaluation/escapes_hand.tsv` (the by-hand read 0018 section 3 allows): 1 escape(s) in the window in this brief's territory (R10-HOTFIX-COP-UNMEASURED). In the brief: the brief at the graded SHA already names its universe by command (`text_ledger.py units --dim D6`) and refuses a skipped unit (`check --plant`), landed by pull request 3571 after round 10's finders ran; step 2 checks a claim once, against the code, and names no configuration. Cost: NO-READ (its seats' tokens and wall clock: no ledger keys a seat by dimension; builder R11-PRE-TOKEN-LEDGER); the brief is 28 lines.",
+   "card": "E11-D6"
+  },
+  "dev/governance/dimensions/D7.md": {
+   "verdict": "change",
+   "evidence": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row D7: 60 judged, 57 stand (6 classed bug), 23 in a roster group at stage done (34 standing ids are in no group's `findings`, so removed is a floor); coverage rows 6 over 6 steps, depth {'deep': 5, 'spot': 1}, steps no seat ran deep: D7.M5, rows carrying examined/universe: 0. 0018's enumerator for this brief, re-run on the graded tree: `python3 tests/structure.py | tail -1` -> `STRUCTURE RATCHET PASSED`, rc 0, 23 `ok` lines (the last `seam_cut_total 415 <= 415`): no gate metric has risen; `tools/audit/archscore/score.py --diff` against decision 0015's target was not run here. `python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --ref a39627da59 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` over `dev/audit/rounds/round11/evaluation/escapes_hand.tsv` (the by-hand read 0018 section 3 allows): 0 escapes in the window in this brief's territory. In the brief: step 5 instructs `a spot mutation a test fails on` per addition, a sample of one; steps 2 to 6 name no command that prints their universe. Cost: NO-READ (its seats' tokens and wall clock: no ledger keys a seat by dimension; builder R11-PRE-TOKEN-LEDGER); the brief is 40 lines.",
+   "card": "E11-D7"
+  },
+  "dev/governance/dimensions/D8.md": {
+   "verdict": "change",
+   "evidence": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row D8: 1 judged, 1 stand (1 classed bug), 1 in a roster group at stage done (0 standing ids are in no group's `findings`, so removed is a floor); coverage rows 5 over 5 steps, depth {'deep': 5}, steps no seat ran deep: -, rows carrying examined/universe: 0. `python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --ref a39627da59 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` over `dev/audit/rounds/round11/evaluation/escapes_hand.tsv` (the by-hand read 0018 section 3 allows): 2 escape(s) in the window in this brief's territory (R10-HOTFIX-PREHEAT-LABEL, R10-MIN-POWER-FLOOR), 2 more dated the stamp's own day. In the brief: step 1's matrix (topologies crossed with feature toggles) is prose and no command prints its cells; step 3 compares `strings.json with both languages` while three ship; 0018 section 1: nothing prints entity by state by language with the pinning test. Cost: NO-READ (its seats' tokens and wall clock: no ledger keys a seat by dimension; builder R11-PRE-TOKEN-LEDGER); the brief is 56 lines.",
+   "card": "E11-D8"
+  },
+  "dev/governance/dimensions/D9.md": {
+   "verdict": "change",
+   "evidence": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row D9: 3 judged, 2 stand (2 classed bug), 2 in a roster group at stage done (0 standing ids are in no group's `findings`, so removed is a floor); coverage rows 3 over 2 steps, depth {'deep': 3}, steps no seat ran deep: -, rows carrying examined/universe: 0. `python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --ref a39627da59 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` over `dev/audit/rounds/round11/evaluation/escapes_hand.tsv` (the by-hand read 0018 section 3 allows): 0 escapes in the window in this brief's territory. In the brief: the method's two steps name their universes in prose (`every coordinator collection`, `every entity's attributes`, `each DHW planning loop`) and no command prints them, as D1's `Enumerate every persisted payload` does not; its three round-10 rows carry no denominator. Cost: NO-READ (its seats' tokens and wall clock: no ledger keys a seat by dimension; builder R11-PRE-TOKEN-LEDGER); the brief is 62 lines.",
+   "card": "E11-D9"
+  },
+  "dev/governance/roles/COMMON.md": {
+   "verdict": "change",
+   "evidence": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json`: 0 of 113 coverage rows of round 10's 48 seat reports carry an examined/universe pair, in all 16 dimensions; `python3 -c \"import json;print(json.load(open('dev/audit/config/finding.schema.json'))['properties']['coverage']['items']['required'])\"` -> ['step', 'depth', 'evidence']. The contract's own text bounds a seat by time and count, not by a universe: `Measure only the cells your task names`, `Aim to return within about two hours of wall clock`, `Prefer three findings`. `coverage` (layer 1) read through this contract therefore counts 0 for every dimension. Cost read: `git show a39627da59:dev/governance/roles/COMMON.md | wc -l` -> 108 lines (`git show v7.0.0:dev/governance/roles/COMMON.md | wc -l` -> 108); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/roles/COMMON.md | wc -l` -> 1 merges touched it in round 10's window.",
+   "card": "E11-COMMON"
+  },
+  "dev/governance/roles/architect-planner.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: one plan per round, so a per-role first-pass share has one sample; the plan's verdict history sits on the plan branch's review refs, which no tracked enumerator reads. NO-READ: nothing counts which seats load a contract, so cost (its tokens times the seats that load it) is unread (builder R11-PRE-TOKEN-LEDGER), and a clause's yield is unread until a block's class names the clause (card E11-N-ROLE-CLAUSE). Cost read: `git show a39627da59:dev/governance/roles/architect-planner.md | wc -l` -> 84 lines (`git show v7.0.0:dev/governance/roles/architect-planner.md | wc -l` -> 0); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/roles/architect-planner.md | wc -l` -> 2 merges touched it in round 10's window."
+  },
+  "dev/governance/roles/design-review.md": {
+   "verdict": "keep",
+   "evidence": "`python3 dev/audit/rounds/round11/evaluation/design_verdicts.py --repo . --window 2026-10-14T13:27:06Z..2026-11-15T05:22:47Z` -> 25 groups, 56 verdicts, 19 groups reviewed twice or more; whether a `revise` was a real catch is unread (review_strength.py reads the fix bus only). A first read, no move. NO-READ: nothing counts which seats load a contract, so cost (its tokens times the seats that load it) is unread (builder R11-PRE-TOKEN-LEDGER), and a clause's yield is unread until a block's class names the clause (card E11-N-ROLE-CLAUSE). Cost read: `git show a39627da59:dev/governance/roles/design-review.md | wc -l` -> 52 lines (`git show v7.0.0:dev/governance/roles/design-review.md | wc -l` -> 0); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/roles/design-review.md | wc -l` -> 2 merges touched it in round 10's window."
+  },
+  "dev/governance/roles/designer.md": {
+   "verdict": "keep",
+   "evidence": "`python3 dev/audit/rounds/round11/evaluation/design_verdicts.py --repo . --window 2026-10-14T13:27:06Z..2026-11-15T05:22:47Z` -> 25 groups with a design verdict in the window, first verdict approve 3/25, 56 verdicts. A first read: it sets the baseline and is no move; no layer-1 term is read through it. NO-READ: nothing counts which seats load a contract, so cost (its tokens times the seats that load it) is unread (builder R11-PRE-TOKEN-LEDGER), and a clause's yield is unread until a block's class names the clause (card E11-N-ROLE-CLAUSE). Cost read: `git show a39627da59:dev/governance/roles/designer.md | wc -l` -> 60 lines (`git show v7.0.0:dev/governance/roles/designer.md | wc -l` -> 0); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/roles/designer.md | wc -l` -> 2 merges touched it in round 10's window."
+  },
+  "dev/governance/roles/evaluator.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: this evaluation is the contract's first run; 0018 section 6 makes its tokens the first row of round 12's ledger. Two clauses could not be followed as written and are reported in `not_followed`. Cost read: `git show a39627da59:dev/governance/roles/evaluator.md | wc -l` -> 27 lines (`git show v7.0.0:dev/governance/roles/evaluator.md | wc -l` -> 0); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/roles/evaluator.md | wc -l` -> 1 merges touched it in round 10's window."
+  },
+  "dev/governance/roles/fix-review.md": {
+   "verdict": "change",
+   "evidence": "`python3 tools/audit/seat/review_strength.py --repo . --window r10=2026-10-14T13:27:06Z..2026-11-15T05:22:47Z` -> 909 reviewed pull requests, 2537 verdicts, real-catch incidence 214/909 (0.24), first-pass 467/909; by kind: cloud 164/752 (0.22), local 59/228 (0.26). Round 9's window by the same instrument: real-catch incidence 19/76 (0.25), a tie with round 10's inside two standard errors. `--guardrail` (report-only) prints `would-trip` for the cloud arm (1/20) and the sonnet arm (1/20) at the round's end. `python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --ref a39627da59 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` over `dev/audit/rounds/round11/evaluation/escapes_hand.tsv` (the by-hand read 0018 section 3 allows): the 4 cause pull requests (#3404, #2411, #2887, #3587) each carried a `Fix review: merge` verdict under this contract: `injected` (layer 1), read by hand, is above 0. Cost read: `git show a39627da59:dev/governance/roles/fix-review.md | wc -l` -> 136 lines (`git show v7.0.0:dev/governance/roles/fix-review.md | wc -l` -> 140); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/roles/fix-review.md | wc -l` -> 21 merges touched it in round 10's window.",
+   "card": "E11-INJECTED"
+  },
+  "dev/governance/roles/fixer.md": {
+   "verdict": "change",
+   "evidence": "`python3 tools/audit/seat/flow_metrics.py --repo . --window 2026-10-14T13:27:06Z..2026-11-15T05:22:47Z --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json --prefix R10-` -> first-pass yield 436/862 (0.51), main absorbs per fix branch mean 3.58; `python3 tools/audit/seat/review_strength.py --repo . --window r10=2026-10-14T13:27:06Z..2026-11-15T05:22:47Z` -> first-pass 467/909, most frequent first blocks: mutation-vacuous 62, carry-missing 56, class-open 53, harness 26, ci-red 25 first blocks. Round 9's window by the same instrument (`--window r9=2026-09-25T12:54:39Z..2026-10-14T13:27:06Z`, v6.6.12 to v7.0.0): first-pass 28/76 (0.37), a first read that sets the baseline and is no move (0018 section 2), which ranks nothing while `injected` and `escapes` are NO-READ. `python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --ref a39627da59 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` over `dev/audit/rounds/round11/evaluation/escapes_hand.tsv` (the by-hand read 0018 section 3 allows): 4 pull requests merged in the window are named as causes (#3404 for R10-HOTFIX-FLOW-SETPOINT-STUCK, by the root-cause record off main; #2411 and #2887 for R10-HOTFIX-SAV-ESTIMATE, by the tracked `dev/audit/rca/R10-RCA-SAV-ESTIMATE.md`, #2411 also by R10-SAVINGS-NEGATIVE's brief; #3587 for R10-HOTFIX-REFERENCE-BASIS, by the fixing group, caught before a release), each of which passed this contract and a merge verdict: `injected` (layer 1), read by hand through the contract, is above 0. Cost read: `git show a39627da59:dev/governance/roles/fixer.md | wc -l` -> 315 lines (`git show v7.0.0:dev/governance/roles/fixer.md | wc -l` -> 315); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/roles/fixer.md | wc -l` -> 14 merges touched it in round 10's window.",
+   "card": "E11-INJECTED"
+  },
+  "dev/governance/roles/judge.md": {
+   "verdict": "keep",
+   "evidence": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` last line -> VERDICTS 116: round 10's judge and catch-up records hold 116 verdict ids; `python3 -c \"import json,collections;print(collections.Counter(v['verdict'] for f in ('JUDGE.json','CATCHUP-JUDGE.json') for v in json.load(open('dev/audit/rounds/round10/'+f))['verdicts']))\"` -> verified 111, weakened 15, unreproduced 8, refuted 6, merged 6 over 146 rows. Whether a finding the judge voided was real is unread (0018 section 4, assumption 3: no term reads it; planted-defect recall, R11-PRE-ROUND-METRICS). NO-READ: nothing counts which seats load a contract, so cost (its tokens times the seats that load it) is unread (builder R11-PRE-TOKEN-LEDGER), and a clause's yield is unread until a block's class names the clause (card E11-N-ROLE-CLAUSE). Cost read: `git show a39627da59:dev/governance/roles/judge.md | wc -l` -> 29 lines (`git show v7.0.0:dev/governance/roles/judge.md | wc -l` -> 30); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/roles/judge.md | wc -l` -> 1 merges touched it in round 10's window."
+  },
+  "dev/governance/roles/orchestrator.md": {
+   "verdict": "change",
+   "evidence": "`git ls-tree -r --name-only a39627da59 -- dev/audit/yardstick` -> nothing; `python3 tools/audit/check_scopes.py --repo . --ref a39627da59 --round 11` -> rc 1, `dev/audit/yardstick/round10/OBJECTIVE.json is not in the tree: round 10's close wrote no record to evaluate`. `grep -n -i '0018\\|objective' dev/governance/roles/orchestrator.md` -> one line (283, in section 14), none in its closure section; only `dev/audit/README.md` phase 13's artefact column names the record. Every layer-1 term read through the closing orchestrator's record is therefore unread for round 10. Cost read: `git show a39627da59:dev/governance/roles/orchestrator.md | wc -l` -> 289 lines (`git show v7.0.0:dev/governance/roles/orchestrator.md | wc -l` -> 319); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/roles/orchestrator.md | wc -l` -> 18 merges touched it in round 10's window.",
+   "card": "E11-N-OBJECTIVE-RECORD"
+  },
+  "dev/governance/roles/plan-review.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: as architect-planner.md, one plan per round and no enumerator over its verdicts. NO-READ: nothing counts which seats load a contract, so cost (its tokens times the seats that load it) is unread (builder R11-PRE-TOKEN-LEDGER), and a clause's yield is unread until a block's class names the clause (card E11-N-ROLE-CLAUSE). Cost read: `git show a39627da59:dev/governance/roles/plan-review.md | wc -l` -> 24 lines (`git show v7.0.0:dev/governance/roles/plan-review.md | wc -l` -> 0); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/roles/plan-review.md | wc -l` -> 2 merges touched it in round 10's window."
+  },
+  "dev/governance/roles/proposal-triage.md": {
+   "verdict": "keep",
+   "evidence": "`git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/programme/triage | wc -l` -> 144 merges landed triage records in the window; the contract changed shape at the graded SHA itself (pull request 3451, once per round at round end), so round 10's batches ran under the old shape and the new one has one run (dev/programme/triage/r10-round-end.md (pull request 3609; on main at 26dbf7c43e, after the graded SHA)). No before and after exists yet. NO-READ: nothing counts which seats load a contract, so cost (its tokens times the seats that load it) is unread (builder R11-PRE-TOKEN-LEDGER), and a clause's yield is unread until a block's class names the clause (card E11-N-ROLE-CLAUSE). Cost read: `git show a39627da59:dev/governance/roles/proposal-triage.md | wc -l` -> 40 lines (`git show v7.0.0:dev/governance/roles/proposal-triage.md | wc -l` -> 0); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/roles/proposal-triage.md | wc -l` -> 7 merges touched it in round 10's window."
+  },
+  "dev/governance/roles/root-cause.md": {
+   "verdict": "keep",
+   "evidence": "`git ls-tree --name-only a39627da59 dev/audit/rca/ | wc -l` -> 137 entries; `git show cbd6d9185166:dev/programme/rosters/wave-r10-groups.json | python3 -c \"import json,sys;print(sum(g.get('kind')=='rca' for g in json.load(sys.stdin)['groups']))\"` -> 30 root-cause groups on round 10's roster. Whether a countermeasure stopped its class is unread: `bugclasses.json` records no instance date (card E11-N-RULE-YIELD). `python3 dev/audit/rounds/round11/evaluation/escapes.py --repo . --ref a39627da59 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` over `dev/audit/rounds/round11/evaluation/escapes_hand.tsv` (the by-hand read 0018 section 3 allows) line RCA_TRACKED: of the 26 in-window escapes of the hand ledger, a root-cause record is tracked for 2 (SAV-ESTIMATE, COP-UNMEASURED); another, R10-RCA-SETPOINT-LATCH-DEADLOCK.md for the stuck set-point, is on the archive tag `archive/handoff-wip/r10-rca-setpoint-latch-deadlock` and not on main; the group for CARD-HEALTH-TEXT is `refused`. A lead for card E11-INJECTED, not a score. NO-READ: nothing counts which seats load a contract, so cost (its tokens times the seats that load it) is unread (builder R11-PRE-TOKEN-LEDGER), and a clause's yield is unread until a block's class names the clause (card E11-N-ROLE-CLAUSE). Cost read: `git show a39627da59:dev/governance/roles/root-cause.md | wc -l` -> 84 lines (`git show v7.0.0:dev/governance/roles/root-cause.md | wc -l` -> 84); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/roles/root-cause.md | wc -l` -> 0 merges touched it in round 10's window."
+  },
+  "dev/governance/roles/standing-dispatch.md": {
+   "verdict": "keep",
+   "evidence": "`git for-each-ref refs/tags/archive/dispatch | wc -l` -> 1453 archived dispatch refs, the dispatches the seat and its scripts wrote over rounds 9 and 10 (the archive carries no round). Tokens per session: NO-READ (R11-PRE-TOKEN-LEDGER). The round-end triage keeps R11-PRE-STANDING-SCRIPTS (P752), with the dispatch seats' scripts as its specification; this read does not contradict it. Cost read: `git show a39627da59:dev/governance/roles/standing-dispatch.md | wc -l` -> 32 lines (`git show v7.0.0:dev/governance/roles/standing-dispatch.md | wc -l` -> 0); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/roles/standing-dispatch.md | wc -l` -> 8 merges touched it in round 10's window."
+  },
+  "dev/governance/roles/standing-merge.md": {
+   "verdict": "keep",
+   "evidence": "`python3 tools/audit/seat/flow_metrics.py --repo . --window 2026-10-14T13:27:06Z..2026-11-15T05:22:47Z --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json --prefix R10-` -> merges 1135 in 759.9 h, hours with a merge 517/759 (0.68): the merges the seat operated. Against the script that would do them: NO-READ (tokens per session, R11-PRE-TOKEN-LEDGER). The round-end triage keeps R11-PRE-STANDING-SCRIPTS (P752) and R11-PRE-PARALLEL-PIPELINE (P754), which replace the seat by scripts; this read does not contradict them. Cost read: `git show a39627da59:dev/governance/roles/standing-merge.md | wc -l` -> 37 lines (`git show v7.0.0:dev/governance/roles/standing-merge.md | wc -l` -> 0); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/roles/standing-merge.md | wc -l` -> 4 merges touched it in round 10's window."
+  },
+  "dev/governance/roles/standing-roster.md": {
+   "verdict": "keep",
+   "evidence": "`sed -n 1,3p dev/governance/roles/standing-roster.md` -> `Retired (tvofi, 2026-10-24 card 1)` into beat rows: a 7-line pointer. `git log --diff-filter=A --format='%h %cI' -- dev/governance/roles/standing-roster.md` -> b160847947 2026-10-22: the file did not exist in round 9 (0 lines at v7.0.0), so a `remove` (zero in two consecutive rounds) fails for want of a second round, not for a yield; nothing counts a load of the pointer (NO-READ). It cites `tools/audit/seat/beatd.jobs.json`, and `git ls-tree -r --name-only a39627da59 | grep -c 'tools/audit/seat/beatd.jobs.json'` -> 1. Cost read: `git show a39627da59:dev/governance/roles/standing-roster.md | wc -l` -> 7 lines (`git show v7.0.0:dev/governance/roles/standing-roster.md | wc -l` -> 0); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/roles/standing-roster.md | wc -l` -> 2 merges touched it in round 10's window."
+  },
+  "dev/governance/roles/standing-tick.md": {
+   "verdict": "keep",
+   "evidence": "`sed -n 1,3p dev/governance/roles/standing-tick.md` -> `Retired (tvofi, 2026-10-24 card 1)` into beat rows: a 6-line pointer. `git log --diff-filter=A --format='%h %cI' -- dev/governance/roles/standing-tick.md` -> b160847947 2026-10-22: the file did not exist in round 9 (0 lines at v7.0.0), so a `remove` (zero in two consecutive rounds) fails for want of a second round, not for a yield; nothing counts a load of the pointer (NO-READ). It cites `tools/audit/seat/beatd.jobs.json`, and `git ls-tree -r --name-only a39627da59 | grep -c 'tools/audit/seat/beatd.jobs.json'` -> 1. Cost read: `git show a39627da59:dev/governance/roles/standing-tick.md | wc -l` -> 6 lines (`git show v7.0.0:dev/governance/roles/standing-tick.md | wc -l` -> 0); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/roles/standing-tick.md | wc -l` -> 3 merges touched it in round 10's window."
+  },
+  "dev/governance/roles/standing.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: tokens per session of the standing seats were read by hand from transcripts in no record this seat can re-run; R11-PRE-TOKEN-LEDGER makes it a read. Yield lead: `python3 tools/audit/seat/flow_metrics.py --repo . --window 2026-10-14T13:27:06Z..2026-11-15T05:22:47Z --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json --prefix R10-` -> 1135 merges and 528 groups added in the window, operated by the standing set and its beat rows. Cost read: `git show a39627da59:dev/governance/roles/standing.md | wc -l` -> 50 lines (`git show v7.0.0:dev/governance/roles/standing.md | wc -l` -> 0); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/roles/standing.md | wc -l` -> 1 merges touched it in round 10's window."
+  },
+  "dev/governance/roles/verifier.md": {
+   "verdict": "keep",
+   "evidence": "Same read as judge.md: 6 refuted and 8 unreproduced of 146 judged rows went no further; a refute that was wrong is unread until planted-defect recall counts after the judge (R11-PRE-ROUND-METRICS). NO-READ: nothing counts which seats load a contract, so cost (its tokens times the seats that load it) is unread (builder R11-PRE-TOKEN-LEDGER), and a clause's yield is unread until a block's class names the clause (card E11-N-ROLE-CLAUSE). Cost read: `git show a39627da59:dev/governance/roles/verifier.md | wc -l` -> 39 lines (`git show v7.0.0:dev/governance/roles/verifier.md | wc -l` -> 39); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/roles/verifier.md | wc -l` -> 1 merges touched it in round 10's window."
+  },
+  "dev/governance/rules/brief-citations.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield is its bug class's instances after the rule merged, and `python3 -c \"import json;j=json.load(open('dev/audit/config/bugclasses.json'));print(sum(isinstance(i,dict) for c in j.values() if isinstance(c,dict) for i in (c.get('instances') or [])))\"` -> 0: no instance carries a date; nothing counts a load or the seconds of a refusal (0018 section 3: not scorable at round 10's close; no roster group builds it: card E11-N-RULE-YIELD). Cost read: `git show a39627da59:dev/governance/rules/brief-citations.md | wc -l` -> 42 lines (`git show v7.0.0:dev/governance/rules/brief-citations.md | wc -l` -> 42); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/rules/brief-citations.md | wc -l` -> 0 merges touched it in round 10's window."
+  },
+  "dev/governance/rules/ci-autofix.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield is its bug class's instances after the rule merged, and `python3 -c \"import json;j=json.load(open('dev/audit/config/bugclasses.json'));print(sum(isinstance(i,dict) for c in j.values() if isinstance(c,dict) for i in (c.get('instances') or [])))\"` -> 0: no instance carries a date; nothing counts a load or the seconds of a refusal (0018 section 3: not scorable at round 10's close; no roster group builds it: card E11-N-RULE-YIELD). Cost read: `git show a39627da59:dev/governance/rules/ci-autofix.md | wc -l` -> 88 lines (`git show v7.0.0:dev/governance/rules/ci-autofix.md | wc -l` -> 91); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/rules/ci-autofix.md | wc -l` -> 7 merges touched it in round 10's window."
+  },
+  "dev/governance/rules/claim-files.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield is its bug class's instances after the rule merged, and `python3 -c \"import json;j=json.load(open('dev/audit/config/bugclasses.json'));print(sum(isinstance(i,dict) for c in j.values() if isinstance(c,dict) for i in (c.get('instances') or [])))\"` -> 0: no instance carries a date; nothing counts a load or the seconds of a refusal (0018 section 3: not scorable at round 10's close; no roster group builds it: card E11-N-RULE-YIELD). Cost read: `git show a39627da59:dev/governance/rules/claim-files.md | wc -l` -> 53 lines (`git show v7.0.0:dev/governance/rules/claim-files.md | wc -l` -> 53); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/rules/claim-files.md | wc -l` -> 3 merges touched it in round 10's window."
+  },
+  "dev/governance/rules/comment-readback.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield is its bug class's instances after the rule merged, and `python3 -c \"import json;j=json.load(open('dev/audit/config/bugclasses.json'));print(sum(isinstance(i,dict) for c in j.values() if isinstance(c,dict) for i in (c.get('instances') or [])))\"` -> 0: no instance carries a date; nothing counts a load or the seconds of a refusal (0018 section 3: not scorable at round 10's close; no roster group builds it: card E11-N-RULE-YIELD). Cost read: `git show a39627da59:dev/governance/rules/comment-readback.md | wc -l` -> 67 lines (`git show v7.0.0:dev/governance/rules/comment-readback.md | wc -l` -> 67); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/rules/comment-readback.md | wc -l` -> 0 merges touched it in round 10's window."
+  },
+  "dev/governance/rules/defect-root-cause.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield is its bug class's instances after the rule merged, and `python3 -c \"import json;j=json.load(open('dev/audit/config/bugclasses.json'));print(sum(isinstance(i,dict) for c in j.values() if isinstance(c,dict) for i in (c.get('instances') or [])))\"` -> 0: no instance carries a date; nothing counts a load or the seconds of a refusal (0018 section 3: not scorable at round 10's close; no roster group builds it: card E11-N-RULE-YIELD). Lead, not a score: the hand ledger's 26 in-window escapes each meet this rule's first trigger (a defect that reached a release); a root-cause record is tracked for 2 of them and another sits off main (see root-cause.md's row). Cost read: `git show a39627da59:dev/governance/rules/defect-root-cause.md | wc -l` -> 153 lines (`git show v7.0.0:dev/governance/rules/defect-root-cause.md | wc -l` -> 153); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/rules/defect-root-cause.md | wc -l` -> 4 merges touched it in round 10's window."
+  },
+  "dev/governance/rules/delivery-status-tracking.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield is its bug class's instances after the rule merged, and `python3 -c \"import json;j=json.load(open('dev/audit/config/bugclasses.json'));print(sum(isinstance(i,dict) for c in j.values() if isinstance(c,dict) for i in (c.get('instances') or [])))\"` -> 0: no instance carries a date; nothing counts a load or the seconds of a refusal (0018 section 3: not scorable at round 10's close; no roster group builds it: card E11-N-RULE-YIELD). Cost read: `git show a39627da59:dev/governance/rules/delivery-status-tracking.md | wc -l` -> 25 lines (`git show v7.0.0:dev/governance/rules/delivery-status-tracking.md | wc -l` -> 35); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/rules/delivery-status-tracking.md | wc -l` -> 1 merges touched it in round 10's window."
+  },
+  "dev/governance/rules/finding-propagation.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield is its bug class's instances after the rule merged, and `python3 -c \"import json;j=json.load(open('dev/audit/config/bugclasses.json'));print(sum(isinstance(i,dict) for c in j.values() if isinstance(c,dict) for i in (c.get('instances') or [])))\"` -> 0: no instance carries a date; nothing counts a load or the seconds of a refusal (0018 section 3: not scorable at round 10's close; no roster group builds it: card E11-N-RULE-YIELD). Cost read: `git show a39627da59:dev/governance/rules/finding-propagation.md | wc -l` -> 101 lines (`git show v7.0.0:dev/governance/rules/finding-propagation.md | wc -l` -> 100); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/rules/finding-propagation.md | wc -l` -> 5 merges touched it in round 10's window."
+  },
+  "dev/governance/rules/gate-scoping.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield is its bug class's instances after the rule merged, and `python3 -c \"import json;j=json.load(open('dev/audit/config/bugclasses.json'));print(sum(isinstance(i,dict) for c in j.values() if isinstance(c,dict) for i in (c.get('instances') or [])))\"` -> 0: no instance carries a date; nothing counts a load or the seconds of a refusal (0018 section 3: not scorable at round 10's close; no roster group builds it: card E11-N-RULE-YIELD). Cost read: `git show a39627da59:dev/governance/rules/gate-scoping.md | wc -l` -> 51 lines (`git show v7.0.0:dev/governance/rules/gate-scoping.md | wc -l` -> 61); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/rules/gate-scoping.md | wc -l` -> 7 merges touched it in round 10's window."
+  },
+  "dev/governance/rules/ratchet-budgets.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield is its bug class's instances after the rule merged, and `python3 -c \"import json;j=json.load(open('dev/audit/config/bugclasses.json'));print(sum(isinstance(i,dict) for c in j.values() if isinstance(c,dict) for i in (c.get('instances') or [])))\"` -> 0: no instance carries a date; nothing counts a load or the seconds of a refusal (0018 section 3: not scorable at round 10's close; no roster group builds it: card E11-N-RULE-YIELD). Cost read: `git show a39627da59:dev/governance/rules/ratchet-budgets.md | wc -l` -> 114 lines (`git show v7.0.0:dev/governance/rules/ratchet-budgets.md | wc -l` -> 111); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/rules/ratchet-budgets.md | wc -l` -> 3 merges touched it in round 10's window."
+  },
+  "dev/governance/rules/writing-for-agents.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield is its bug class's instances after the rule merged, and `python3 -c \"import json;j=json.load(open('dev/audit/config/bugclasses.json'));print(sum(isinstance(i,dict) for c in j.values() if isinstance(c,dict) for i in (c.get('instances') or [])))\"` -> 0: no instance carries a date; nothing counts a load or the seconds of a refusal (0018 section 3: not scorable at round 10's close; no roster group builds it: card E11-N-RULE-YIELD). Cost read: `git show a39627da59:dev/governance/rules/writing-for-agents.md | wc -l` -> 65 lines (`git show v7.0.0:dev/governance/rules/writing-for-agents.md | wc -l` -> 65); `git log --first-parent --oneline v7.0.0..v10.0.0 -- dev/governance/rules/writing-for-agents.md | wc -l` -> 1 merges touched it in round 10's window."
+  },
+  "tests/closure.py": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tests/closure.py` 5368 lines (5046 at the window's start), 46 merges touched it in the window, 16 roster group(s) name it, 1 of them hotfix."
+  },
+  "tests/mutation_table.py": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tests/mutation_table.py` 4327 lines (3858 at the window's start), 7 merges touched it in the window, 4 roster group(s) name it, 1 of them hotfix. 0018 names `python3 tests/mutation_table.py --scope full` as D3's enumerator: NO-READ at this seat (the nightly's job; the record that reads it is the Nightly workflow's mutation lane on main)."
+  },
+  "tests/structure.py": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tests/structure.py` 4426 lines (2702 at the window's start), 5 merges touched it in the window, 78 roster group(s) name it, 1 of them hotfix. 0018 names it D7's enumerator with `tools/audit/archscore/score.py --diff`; re-run at the graded SHA: `python3 tests/structure.py | tail -1` -> `STRUCTURE RATCHET PASSED`, rc 0."
+  },
+  "tools/audit/carry_audit.py": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/carry_audit.py` 2245 lines (0 at the window's start), 17 merges touched it in the window, 18 roster group(s) name it, 3 of them hotfix."
+  },
+  "tools/audit/seat/instruments/app_approve.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/pr/app_approve.sh` 2136 lines (1129 at the window's start), 12 merges touched it in the window, 8 roster group(s) name it, 1 of them hotfix."
+  },
+  "tools/audit/seat/instruments/app_comment.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/pr/app_comment.sh` 358 lines (304 at the window's start), 2 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/app_push.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/pr/app_push.sh` 1443 lines (894 at the window's start), 13 merges touched it in the window, 11 roster group(s) name it, 1 of them hotfix."
+  },
+  "tools/audit/seat/instruments/approve_held_runs.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/pr/approve_held_runs.sh` 352 lines (352 at the window's start), 0 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/autofix_statuses.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/autofix_statuses.sh` 76 lines (72 at the window's start), 2 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/bare_array.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/bare_array.py` 314 lines (0 at the window's start), 2 merges touched it in the window, 1 roster group(s) name it, 1 of them hotfix."
+  },
+  "tools/audit/seat/instruments/beat_jobs.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/beat_jobs.py` 808 lines (0 at the window's start), 12 merges touched it in the window, 12 roster group(s) name it, 2 of them hotfix."
+  },
+  "tools/audit/seat/instruments/beatd.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/beatd.py` 1524 lines (0 at the window's start), 5 merges touched it in the window, 5 roster group(s) name it, 1 of them hotfix."
+  },
+  "tools/audit/seat/instruments/beatd_shims_git.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/instruments/beatd_shims_git.md (no tracked file of that basename: the guide itself)` 11 lines (0 at the window's start), 1 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/body_patch.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/body_patch.sh` 658 lines (0 at the window's start), 9 merges touched it in the window, 3 roster group(s) name it, 1 of them hotfix."
+  },
+  "tools/audit/seat/instruments/body_push.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/body_push.sh` 262 lines (38 at the window's start), 14 merges touched it in the window, 18 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/bottleneck_check.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/bottleneck_check.py` 390 lines (0 at the window's start), 1 merges touched it in the window, 1 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/bus.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/bus.sh` 2564 lines (1033 at the window's start), 30 merges touched it in the window, 93 roster group(s) name it, 3 of them hotfix."
+  },
+  "tools/audit/seat/instruments/cancel_superseded.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/pr/cancel_superseded.py` 853 lines (0 at the window's start), 3 merges touched it in the window, 4 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/carry_fold.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/carry_fold.py` 156 lines (0 at the window's start), 2 merges touched it in the window, 1 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/check_scopes.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/check_scopes.py` 926 lines (142 at the window's start), 4 merges touched it in the window, 5 roster group(s) name it, 0 of them hotfix. Re-run: `python3 tools/audit/check_scopes.py --repo . --ref 13cbe48de4` -> rc 0, `coverage tracked=11218 in_universe=1596 excluded=9622 unclassified=0`; at a39627da59 -> rc 0, tracked=11244, unclassified=0; `--population` -> LEVELS 195, PAIRS 18696, NO-READ AXES 2; `--round 11` -> rc 1 with 2 gaps before this evaluation."
+  },
+  "tools/audit/seat/instruments/ci-watch.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/ci-watch.sh` 361 lines (244 at the window's start), 6 merges touched it in the window, 1 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/ci_critpath.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/ci_critpath.py` 486 lines (0 at the window's start), 1 merges touched it in the window, 2 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/ci_pause.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/ci_pause.py` 420 lines (0 at the window's start), 1 merges touched it in the window, 1 roster group(s) name it, 1 of them hotfix."
+  },
+  "tools/audit/seat/instruments/ci_priority.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/ci_priority.py` 308 lines (0 at the window's start), 1 merges touched it in the window, 1 roster group(s) name it, 1 of them hotfix."
+  },
+  "tools/audit/seat/instruments/ci_probe.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/ci_probe.py` 612 lines (0 at the window's start), 3 merges touched it in the window, 1 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/closeout.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/closeout.py` 802 lines (0 at the window's start), 3 merges touched it in the window, 1 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/cloud-setup.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/cloud-setup.sh` 240 lines (74 at the window's start), 9 merges touched it in the window, 6 roster group(s) name it, 1 of them hotfix."
+  },
+  "tools/audit/seat/instruments/cloud_dispatch.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/cloud_dispatch.py` 1608 lines (0 at the window's start), 30 merges touched it in the window, 16 roster group(s) name it, 1 of them hotfix."
+  },
+  "tools/audit/seat/instruments/cloud_relay.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/cloud_relay.sh` 2161 lines (0 at the window's start), 27 merges touched it in the window, 30 roster group(s) name it, 2 of them hotfix."
+  },
+  "tools/audit/seat/instruments/codeql-triage-poll.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/codeql-triage-poll.sh` 27 lines (27 at the window's start), 0 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/daemonize.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/daemonize.py` 279 lines (204 at the window's start), 3 merges touched it in the window, 2 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/delivery_row.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/delivery_row.sh` 95 lines (0 at the window's start), 4 merges touched it in the window, 1 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/depgraph.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/pr/depgraph.py` 341 lines (0 at the window's start), 1 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/enumerate.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD); the guide also landed after the graded window, so no round has run with it. Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref 030a4d377f --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/enumerate.py` 956 lines (0 at the window's start), 0 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix. The guide was added by 267655f306 (R11-PRE-BRIEFS-CENSUS, pull request 3625): `git merge-base --is-ancestor <sha> v10.0.0` -> rc 1, after v10.0.0, so it is an object of objective.json at origin/main 030a4d377f and not at the graded SHA a39627da59."
+  },
+  "tools/audit/seat/instruments/failure_logs.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/failure_logs.sh` 166 lines (163 at the window's start), 3 merges touched it in the window, 3 roster group(s) name it, 1 of them hotfix."
+  },
+  "tools/audit/seat/instruments/features_block.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/features_block.py` 218 lines (55 at the window's start), 2 merges touched it in the window, 2 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/figure_block.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/pr/figure_block.py` 304 lines (0 at the window's start), 1 merges touched it in the window, 3 roster group(s) name it, 3 of them hotfix."
+  },
+  "tools/audit/seat/instruments/finder_overlap.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD); the guide also landed after the graded window, so no round has run with it. Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref 030a4d377f --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/finder_overlap.py` 263 lines (0 at the window's start), 0 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix. The guide was added by 2e7bced82e (R11-PRE-ROUND-METRICS part 1, pull request 3612): `git merge-base --is-ancestor <sha> v10.0.0` -> rc 1, after v10.0.0, so it is an object of objective.json at origin/main 030a4d377f and not at the graded SHA a39627da59."
+  },
+  "tools/audit/seat/instruments/flow_metrics.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/flow_metrics.py` 290 lines (0 at the window's start), 1 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix. 0018 names it an enumerator of `first_pass` (layer 2); re-run over the window, see `terms.first_pass`."
+  },
+  "tools/audit/seat/instruments/fold_ledger.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/fold_ledger.py` 677 lines (476 at the window's start), 2 merges touched it in the window, 3 roster group(s) name it, 0 of them hotfix. 0018 names `python3 tools/audit/fold_ledger.py check` as D14's enumerator; re-run at the graded SHA: `python3 tools/audit/fold_ledger.py check` -> fold_ledger: 0 violation(s) | rc=0"
+  },
+  "tools/audit/seat/instruments/gantt_drift.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/gantt_drift.py` 284 lines (0 at the window's start), 1 merges touched it in the window, 1 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/gh_calls.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/gh_calls.py` 842 lines (0 at the window's start), 6 merges touched it in the window, 5 roster group(s) name it, 1 of them hotfix."
+  },
+  "tools/audit/seat/instruments/gh_read.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/gh_read.py` 654 lines (0 at the window's start), 4 merges touched it in the window, 3 roster group(s) name it, 2 of them hotfix."
+  },
+  "tools/audit/seat/instruments/gh_read_run.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/gh_read_run.py` 129 lines (0 at the window's start), 1 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/handoff_push.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/handoff_push.sh` 211 lines (120 at the window's start), 9 merges touched it in the window, 69 roster group(s) name it, 1 of them hotfix."
+  },
+  "tools/audit/seat/instruments/handover_prompt.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/handover_prompt.py` 304 lines (244 at the window's start), 8 merges touched it in the window, 2 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/head_note.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/pr/head_note.py` 96 lines (0 at the window's start), 1 merges touched it in the window, 1 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/heartbeat.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/heartbeat.sh` 118 lines (0 at the window's start), 3 merges touched it in the window, 1 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/hooks_setup.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/hooks_setup.py` 513 lines (0 at the window's start), 2 merges touched it in the window, 1 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/judge_batch.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/judge_batch.py` 432 lines (432 at the window's start), 1 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/ledger.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/ledger.py` 1359 lines (0 at the window's start), 17 merges touched it in the window, 16 roster group(s) name it, 2 of them hotfix."
+  },
+  "tools/audit/seat/instruments/machinery_ratchet.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/machinery_ratchet.py` 734 lines (0 at the window's start), 2 merges touched it in the window, 2 roster group(s) name it, 0 of them hotfix. 0018 names its `--measure` for rule 4; re-run: `python3 tools/audit/machinery_ratchet.py --measure --repo . --head 13cbe48de4` -> {\"churn_per_kilo_product_lines\": 13548, \"exempted\": [], \"head\": \"13cbe48de4236b7979c754640cc5b1a099ef7475\", \"machinery\": 320, \"nonproduct_lines\": 303475, \"nonproduction_merges\": 477, \"product_lines\": 22400, \"production\": 103, \"record\": 157, \"window\": 580} | rc=0"
+  },
+  "tools/audit/seat/instruments/merge_fastpath.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/merge_fastpath.py` 131 lines (131 at the window's start), 0 merges touched it in the window, 1 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/merge_pr.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/merge_pr.sh` 424 lines (41 at the window's start), 11 merges touched it in the window, 11 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/merge_throughput.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/merge_throughput.py` 1605 lines (335 at the window's start), 3 merges touched it in the window, 1 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/merge_train.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/merge_train.py` 11585 lines (2416 at the window's start), 50 merges touched it in the window, 52 roster group(s) name it, 7 of them hotfix. Its lines rose from 2416 to 11585 over the window; with yield unread this is no `change` under 0018 (cost beyond the band counts only at flat yield). The round-end triage rules no further patch on it and sends its residue to the redesign (P754, P775)."
+  },
+  "tools/audit/seat/instruments/moved_paths.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/moved_paths.py` 150 lines (136 at the window's start), 2 merges touched it in the window, 2 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/mutant_run.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/mutant_run.py` 1081 lines (0 at the window's start), 3 merges touched it in the window, 4 roster group(s) name it, 3 of them hotfix."
+  },
+  "tools/audit/seat/instruments/offline_spy.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/offline_spy.py` 305 lines (0 at the window's start), 1 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/open_driver.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/open_driver.py` 345 lines (0 at the window's start), 7 merges touched it in the window, 10 roster group(s) name it, 3 of them hotfix."
+  },
+  "tools/audit/seat/instruments/open_pr.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/open_pr.sh` 198 lines (62 at the window's start), 17 merges touched it in the window, 16 roster group(s) name it, 4 of them hotfix."
+  },
+  "tools/audit/seat/instruments/orchestrator_tick.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/orchestrator_tick.py` 5413 lines (2560 at the window's start), 34 merges touched it in the window, 36 roster group(s) name it, 1 of them hotfix. Its lines rose from 2560 to 5413 over the window; yield unread, so no `change`; the round-end triage sends its residue to R11-PRE-STANDING-SCRIPTS (P752)."
+  },
+  "tools/audit/seat/instruments/outside.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/pr/outside.py` 1158 lines (0 at the window's start), 1 merges touched it in the window, 1 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/outside_intake.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/outside_intake.py` 370 lines (0 at the window's start), 1 merges touched it in the window, 1 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/owed_unactioned.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/owed_unactioned.py` 478 lines (0 at the window's start), 7 merges touched it in the window, 9 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/plan_audit.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/plan_audit.py` 692 lines (0 at the window's start), 2 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/plan_page.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/plan_page.py` 1608 lines (0 at the window's start), 15 merges touched it in the window, 13 roster group(s) name it, 2 of them hotfix."
+  },
+  "tools/audit/seat/instruments/plan_public.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/plan_public.py` 246 lines (0 at the window's start), 1 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/plan_table.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/plan_table.py` 329 lines (319 at the window's start), 4 merges touched it in the window, 3 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/plant_recall.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD); the guide also landed after the graded window, so no round has run with it. Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref 030a4d377f --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/plant_recall.py` 443 lines (0 at the window's start), 0 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix. The guide was added by 2e7bced82e (R11-PRE-ROUND-METRICS part 1, pull request 3612): `git merge-base --is-ancestor <sha> v10.0.0` -> rc 1, after v10.0.0, so it is an object of objective.json at origin/main 030a4d377f and not at the graded SHA a39627da59."
+  },
+  "tools/audit/seat/instruments/policy_reread_check.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/policy_reread_check.py` 204 lines (0 at the window's start), 1 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/postmerge.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/postmerge.py` 211 lines (0 at the window's start), 3 merges touched it in the window, 3 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/pr_args.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/pr_args.sh` 2226 lines (0 at the window's start), 30 merges touched it in the window, 18 roster group(s) name it, 7 of them hotfix."
+  },
+  "tools/audit/seat/instruments/pr_cap.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/pr_cap.py` 351 lines (0 at the window's start), 3 merges touched it in the window, 8 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/preflight.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/pr/preflight.sh` 290 lines (225 at the window's start), 2 merges touched it in the window, 1 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/prepare_baseline.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/prepare_baseline.sh` 327 lines (295 at the window's start), 2 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/prepr.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/pr/prepr.sh` 4881 lines (2694 at the window's start), 44 merges touched it in the window, 34 roster group(s) name it, 8 of them hotfix."
+  },
+  "tools/audit/seat/instruments/probe_bridge.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/probe_bridge.py` 267 lines (0 at the window's start), 2 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/proof_watch.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/proof_watch.py` 869 lines (675 at the window's start), 9 merges touched it in the window, 5 roster group(s) name it, 1 of them hotfix."
+  },
+  "tools/audit/seat/instruments/prune_refs.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/prune_refs.py` 1121 lines (508 at the window's start), 4 merges touched it in the window, 4 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/pulse.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/pulse.py` 873 lines (0 at the window's start), 8 merges touched it in the window, 4 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/push.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/pr/push.sh` 741 lines (719 at the window's start), 2 merges touched it in the window, 2 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/queue_pre_flight.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/queue_pre_flight.py` 627 lines (415 at the window's start), 12 merges touched it in the window, 4 roster group(s) name it, 1 of them hotfix."
+  },
+  "tools/audit/seat/instruments/record_beat.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/record_beat.py` 250 lines (0 at the window's start), 2 merges touched it in the window, 3 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/record_row.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/record_row.py` 2070 lines (1537 at the window's start), 10 merges touched it in the window, 10 roster group(s) name it, 2 of them hotfix."
+  },
+  "tools/audit/seat/instruments/ref_privacy.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/ref_privacy.py` 1393 lines (0 at the window's start), 26 merges touched it in the window, 17 roster group(s) name it, 3 of them hotfix."
+  },
+  "tools/audit/seat/instruments/remerge_main.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/remerge_main.sh` 102 lines (27 at the window's start), 5 merges touched it in the window, 3 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/resume_doc.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/resume_doc.py` 250 lines (239 at the window's start), 4 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/review_carry.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/review_carry.py` 532 lines (0 at the window's start), 4 merges touched it in the window, 3 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/review_packet.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/review_packet.py` 1626 lines (0 at the window's start), 13 merges touched it in the window, 12 roster group(s) name it, 4 of them hotfix."
+  },
+  "tools/audit/seat/instruments/review_strength.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/review_strength.py` 1123 lines (0 at the window's start), 5 merges touched it in the window, 4 roster group(s) name it, 0 of them hotfix. 0018 names it an enumerator of `first_pass` (layer 2); re-run over the window, see `terms.first_pass`."
+  },
+  "tools/audit/seat/instruments/role_pack.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/policy/role_pack.py` 371 lines (0 at the window's start), 1 merges touched it in the window, 1 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/roster_edit.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/roster_edit.py` 3331 lines (696 at the window's start), 24 merges touched it in the window, 25 roster group(s) name it, 1 of them hotfix."
+  },
+  "tools/audit/seat/instruments/roster_lib.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/roster_lib.py` 1445 lines (199 at the window's start), 20 merges touched it in the window, 15 roster group(s) name it, 2 of them hotfix."
+  },
+  "tools/audit/seat/instruments/roster_queue.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/roster_queue.py` 1072 lines (0 at the window's start), 7 merges touched it in the window, 7 roster group(s) name it, 2 of them hotfix."
+  },
+  "tools/audit/seat/instruments/roster_sync.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/roster_sync.py` 1596 lines (0 at the window's start), 11 merges touched it in the window, 10 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/round_metrics.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD); the guide also landed after the graded window, so no round has run with it. Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref 030a4d377f --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/round_metrics.py` 452 lines (0 at the window's start), 0 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix. The guide was added by 6c87325160 (R11-PRE-ROUND-METRICS): `git merge-base --is-ancestor <sha> v10.0.0` -> rc 1, after v10.0.0, so it is an object of objective.json at origin/main 030a4d377f and not at the graded SHA a39627da59."
+  },
+  "tools/audit/seat/instruments/run_twins.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/run_twins.py` 131 lines (131 at the window's start), 0 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/scorecard.py.md": {
+   "verdict": "change",
+   "evidence": "`python3 tools/audit/seat/scorecard.py report --dir <empty dir> --train-log <empty file> --repo .` -> every line `unread`: `<state>/scorecard/` does not exist on the round-10 state directory (no input producer), so `product_green` (layer 1), which 0018 section 2 reads from line `A_gate`, has no value from its named enumerator for any day of round 10; line `A_gate` is defined over the last 20 runs, not the window. Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/scorecard.py` 276 lines (0 at the window's start), 1 merges touched it in the window, 2 roster group(s) name it, 1 of them hotfix.",
+   "card": "E11-SCORECARD"
+  },
+  "tools/audit/seat/instruments/seat_gen.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/seat_gen.py` 170 lines (0 at the window's start), 1 merges touched it in the window, 1 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/seat_venv.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/seat_venv.sh` 341 lines (281 at the window's start), 6 merges touched it in the window, 2 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/selftest_wiring.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/selftest_wiring.py` 304 lines (0 at the window's start), 3 merges touched it in the window, 6 roster group(s) name it, 1 of them hotfix."
+  },
+  "tools/audit/seat/instruments/shims_seat-gh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/shims/seat-gh` 361 lines (0 at the window's start), 6 merges touched it in the window, 3 roster group(s) name it, 1 of them hotfix."
+  },
+  "tools/audit/seat/instruments/shims_seat-python.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/shims/seat-python` 33 lines (33 at the window's start), 0 merges touched it in the window, 1 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/state_docs.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/state_docs.py` 1441 lines (743 at the window's start), 10 merges touched it in the window, 18 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/survivor_list.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/survivor_list.py` 180 lines (0 at the window's start), 1 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/sweep_driver.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/sweep_driver.py` 164 lines (0 at the window's start), 2 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/sweep_gantt.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/sweep_gantt.py` 252 lines (0 at the window's start), 1 merges touched it in the window, 1 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/sweep_render.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/sweep_render.py` 367 lines (0 at the window's start), 10 merges touched it in the window, 4 roster group(s) name it, 1 of them hotfix."
+  },
+  "tools/audit/seat/instruments/sweep_template.md.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/sweep_template.md` 94 lines (0 at the window's start), 23 merges touched it in the window, 13 roster group(s) name it, 1 of them hotfix."
+  },
+  "tools/audit/seat/instruments/text_ledger.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/text_ledger.py` 438 lines (0 at the window's start), 1 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/tick_loop.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/tick_loop.sh` 519 lines (0 at the window's start), 12 merges touched it in the window, 16 roster group(s) name it, 3 of them hotfix."
+  },
+  "tools/audit/seat/instruments/tmp_paths.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/tmp_paths.py` 378 lines (366 at the window's start), 6 merges touched it in the window, 0 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/train.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/train.sh` 490 lines (203 at the window's start), 7 merges touched it in the window, 13 roster group(s) name it, 1 of them hotfix."
+  },
+  "tools/audit/seat/instruments/update_pr.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/update_pr.sh` 153 lines (30 at the window's start), 15 merges touched it in the window, 21 roster group(s) name it, 2 of them hotfix."
+  },
+  "tools/audit/seat/instruments/verdict_audit.py.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/verdict_audit.py` 174 lines (0 at the window's start), 1 merges touched it in the window, 1 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/worktree_gc.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/worktree_gc.sh` 1188 lines (701 at the window's start), 3 merges touched it in the window, 7 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/audit/seat/instruments/wt_sync.sh.md": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/audit/seat/wt_sync.sh` 43 lines (37 at the window's start), 1 merges touched it in the window, 3 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/policy/brief_lint.mjs": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/policy/brief_lint.mjs` 1719 lines (1344 at the window's start), 7 merges touched it in the window, 12 roster group(s) name it, 2 of them hotfix."
+  },
+  "tools/policy/budget_raise_gate.py": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/policy/budget_raise_gate.py` 1648 lines (1323 at the window's start), 13 merges touched it in the window, 5 roster group(s) name it, 0 of them hotfix."
+  },
+  "tools/policy/policy_lint.mjs": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/policy/policy_lint.mjs` 8061 lines (6996 at the window's start), 26 merges touched it in the window, 28 roster group(s) name it, 2 of them hotfix."
+  },
+  "tools/release/stamp.py": {
+   "verdict": "keep",
+   "evidence": "NO-READ: yield (refusals a fix followed, or lead time removed) is unread: no refusal is logged with its outcome, and no roster group builds that log (card E11-N-INSTRUMENT-YIELD). Cost read: `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` row: `tools/release/stamp.py` 3165 lines (1998 at the window's start), 13 merges touched it in the window, 18 roster group(s) name it, 1 of them hotfix."
+  }
+ },
+ "cards": {
+  "E11-D0": {
+   "object": "dev/governance/dimensions/D0.md",
+   "proposal": "Change the brief: write the command that prints step 4's cells into the brief and have each report row carry examined over that universe; add to step 4 the cells the two escapes and seat-found defects show it did not drive (an install whose pump power is set through a flow set-point behind a buffer and a mixing valve, where the plan stayed at the minimum level despite a price spread; a configured manual-valve buffer, where the plan equalled the plan with no buffer); add the same-information oracle step of 0018 section 1 (exogenous inputs at decision time, the measured house) with the flat-price null it already has. Each escape row of the hand ledger names the step and the input.",
+   "term": "`escapes` owned by D0: 1 in round 10's window by the hand read, toward 0; `coverage` of D0: counts 0 today (0018 section 2: a step reporting no denominator counts 0; 0 of 10 round-10 rows carry one), toward a read share",
+   "null_control": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` on round 10's reports prints 0 rows with examined/universe for every dimension, this one included: a brief left unchanged keeps printing 0; the escapes ledger's row count for a dimension whose step gains no input does not move",
+   "cost": "The brief's own lines (65 today) and one policy pull request under the owner's review; the seats' token cost is NO-READ until R11-PRE-TOKEN-LEDGER lands. No figure for round 11's work is given here.",
+   "finder_critical": "yes: it changes this dimension's brief, which its finder seats run from",
+   "already_ruled": "tvofi, 2026-11-13: every dimension covers its whole scope each round with a reported denominator (roster group R10-DIMENSIONS-FULL-COVERAGE; carries 174 to 178 on R11-INTAKE-R10-RESIDUE name the brief edits decision 0018 owes; card E11-COMMON reports that no group builds the denominator rule itself). The round-end triage (dev/programme/triage/r10-round-end.md (pull request 3609; on main at 26dbf7c43e, after the graded SHA), P768) lists carries 173, 175, 177 and 178 as not instrument work and does not rule them. This card agrees with the ruling and adds the per-brief step and input.",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Accept all 14 (Recommended)\" (preliminary at 11:40Z, made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true,
+   "merged": "f1520e3539b82407e56be9fe915d8a57ad6aedef"
+  },
+  "E11-D1": {
+   "object": "dev/governance/dimensions/D1.md",
+   "proposal": "Change the brief: name the census command in steps 1 to 6 and add to step 3 the inputs the escapes and seat-found defects show it did not drive: a presence entity changing between two scheduled updates, a price fetch that raises while the last prices still cover now, an input that goes missing and reports again inside one interval; to step 2 a save during the learners' load and the previous release's persisted record driven to the first actuator write (the stuck set-point: a hold that no restart released); to step 1 a stored override carried across restore then resolve. Each escape row of the hand ledger names the step and the input.",
+   "term": "`escapes` owned by D1: 5 in round 10's window by the hand read, toward 0; `coverage` of D1: counts 0 today (0018 section 2: a step reporting no denominator counts 0; 0 of 6 round-10 rows carry one), toward a read share",
+   "null_control": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` on round 10's reports prints 0 rows with examined/universe for every dimension, this one included: a brief left unchanged keeps printing 0; the escapes ledger's row count for a dimension whose step gains no input does not move",
+   "cost": "The brief's own lines (60 today) and one policy pull request under the owner's review; the seats' token cost is NO-READ until R11-PRE-TOKEN-LEDGER lands. No figure for round 11's work is given here.",
+   "finder_critical": "yes: it changes this dimension's brief, which its finder seats run from",
+   "already_ruled": "tvofi, 2026-11-13: every dimension covers its whole scope each round with a reported denominator (roster group R10-DIMENSIONS-FULL-COVERAGE; carries 174 to 178 on R11-INTAKE-R10-RESIDUE name the brief edits decision 0018 owes; card E11-COMMON reports that no group builds the denominator rule itself). The round-end triage (dev/programme/triage/r10-round-end.md (pull request 3609; on main at 26dbf7c43e, after the graded SHA), P768) lists carries 173, 175, 177 and 178 as not instrument work and does not rule them. This card agrees with the ruling and adds the per-brief step and input.",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Accept all 14 (Recommended)\" (preliminary at 11:40Z, made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true,
+   "merged": "f1520e3539b82407e56be9fe915d8a57ad6aedef"
+  },
+  "E11-D10": {
+   "object": "dev/governance/dimensions/D10.md",
+   "proposal": "Change the brief: step 1's check of the gold rule `diagnostics` gains the input the redaction escape shows it did not drive: every option that can hold a location, the solar-location option among them. Each escape row of the hand ledger names the step and the input.",
+   "term": "`escapes` owned by D10: 1 in round 10's window by the hand read, toward 0; `coverage` of D10: counts 0 today (0018 section 2: a step reporting no denominator counts 0; 0 of 7 round-10 rows carry one), toward a read share",
+   "null_control": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` on round 10's reports prints 0 rows with examined/universe for every dimension, this one included: a brief left unchanged keeps printing 0; the escapes ledger's row count for a dimension whose step gains no input does not move",
+   "cost": "The brief's own lines (43 today) and one policy pull request under the owner's review; the seats' token cost is NO-READ until R11-PRE-TOKEN-LEDGER lands. No figure for round 11's work is given here.",
+   "finder_critical": "yes: it changes this dimension's brief, which its finder seats run from",
+   "already_ruled": "tvofi, 2026-11-13: every dimension covers its whole scope each round with a reported denominator (roster group R10-DIMENSIONS-FULL-COVERAGE; carries 174 to 178 on R11-INTAKE-R10-RESIDUE name the brief edits decision 0018 owes; card E11-COMMON reports that no group builds the denominator rule itself). The round-end triage (dev/programme/triage/r10-round-end.md (pull request 3609; on main at 26dbf7c43e, after the graded SHA), P768) lists carries 173, 175, 177 and 178 as not instrument work and does not rule them. This card agrees with the ruling and adds the per-brief step and input.",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Accept all 14 (Recommended)\" (preliminary at 11:40Z, made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true,
+   "merged": "511cf165f77359be8daf2b402e754d9dc0b6a5a2"
+  },
+  "E11-D11": {
+   "object": "dev/governance/dimensions/D11.md",
+   "proposal": "Change the brief: replace the sample by the population step 1's inventory prints (one row per refusal a seat can meet) and report conformance per obligation over every merged pull request of the window.",
+   "term": "`coverage` of D11: counts 0 today (0018 section 2: a step reporting no denominator counts 0; 0 of 4 round-10 rows carry one), toward a read share",
+   "null_control": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` on round 10's reports prints 0 rows with examined/universe for every dimension, this one included: a brief left unchanged keeps printing 0",
+   "cost": "The brief's own lines (99 today) and one policy pull request under the owner's review; the seats' token cost is NO-READ until R11-PRE-TOKEN-LEDGER lands. No figure for round 11's work is given here.",
+   "finder_critical": "yes: it changes this dimension's brief, which its finder seats run from",
+   "already_ruled": "tvofi, 2026-11-13: every dimension covers its whole scope each round with a reported denominator (roster group R10-DIMENSIONS-FULL-COVERAGE; carries 174 to 178 on R11-INTAKE-R10-RESIDUE name the brief edits decision 0018 owes; card E11-COMMON reports that no group builds the denominator rule itself). The round-end triage (dev/programme/triage/r10-round-end.md (pull request 3609; on main at 26dbf7c43e, after the graded SHA), P768) lists carries 173, 175, 177 and 178 as not instrument work and does not rule them. This card agrees with the ruling and adds the per-brief step and input.",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Accept all 14 (Recommended)\" (preliminary at 11:40Z, made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true,
+   "merged": "62f6bb2006892b59171b14ea4c3f7d025c2e74ce",
+   "merged_note": "Two merges built it: 511cf165f7 (pull request 3618) and 62f6bb2006 (pull request 3642); the later is recorded. Each changes dev/governance/dimensions/D11.md against its first parent."
+  },
+  "E11-D12": {
+   "object": "dev/governance/dimensions/D12.md",
+   "proposal": "Change the brief: name that command as the universe, add the card and the blueprints, declare the levels of tank volume and house size, keep the cell ledger 0018 section 1 describes, and add to step 3 the input the learner escape shows it did not drive: a counter-metered pump whose spans hold hot-water charges. Each escape row of the hand ledger names the step and the input.",
+   "term": "`escapes` owned by D12: 1 in round 10's window by the hand read, toward 0; `coverage` of D12: counts 0 today (0018 section 2: a step reporting no denominator counts 0; 0 of 6 round-10 rows carry one), toward a read share",
+   "null_control": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` on round 10's reports prints 0 rows with examined/universe for every dimension, this one included: a brief left unchanged keeps printing 0; the escapes ledger's row count for a dimension whose step gains no input does not move",
+   "cost": "The brief's own lines (70 today) and one policy pull request under the owner's review; the seats' token cost is NO-READ until R11-PRE-TOKEN-LEDGER lands. No figure for round 11's work is given here.",
+   "finder_critical": "yes: it changes this dimension's brief, which its finder seats run from",
+   "already_ruled": "tvofi, 2026-11-13: every dimension covers its whole scope each round with a reported denominator (roster group R10-DIMENSIONS-FULL-COVERAGE; carries 174 to 178 on R11-INTAKE-R10-RESIDUE name the brief edits decision 0018 owes; card E11-COMMON reports that no group builds the denominator rule itself). The round-end triage (dev/programme/triage/r10-round-end.md (pull request 3609; on main at 26dbf7c43e, after the graded SHA), P768) lists carries 173, 175, 177 and 178 as not instrument work and does not rule them. This card agrees with the ruling and adds the per-brief step and input.",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Accept all 14 (Recommended)\" (preliminary at 11:40Z, made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true,
+   "merged": "f1520e3539b82407e56be9fe915d8a57ad6aedef"
+  },
+  "E11-D14": {
+   "object": "dev/governance/dimensions/D14.md",
+   "proposal": "Change the brief: replace the pick by the whole `open` list the ledger prints, each class owned by a seat or carried by rotation with the reason.",
+   "term": "`coverage` of D14: counts 0 today (0018 section 2: a step reporting no denominator counts 0; 0 of 13 round-10 rows carry one), toward a read share",
+   "null_control": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` on round 10's reports prints 0 rows with examined/universe for every dimension, this one included: a brief left unchanged keeps printing 0",
+   "cost": "The brief's own lines (32 today) and one policy pull request under the owner's review; the seats' token cost is NO-READ until R11-PRE-TOKEN-LEDGER lands. No figure for round 11's work is given here.",
+   "finder_critical": "yes: it changes this dimension's brief, which its finder seats run from",
+   "already_ruled": "tvofi, 2026-11-13: every dimension covers its whole scope each round with a reported denominator (roster group R10-DIMENSIONS-FULL-COVERAGE; carries 174 to 178 on R11-INTAKE-R10-RESIDUE name the brief edits decision 0018 owes; card E11-COMMON reports that no group builds the denominator rule itself). The round-end triage (dev/programme/triage/r10-round-end.md (pull request 3609; on main at 26dbf7c43e, after the graded SHA), P768) lists carries 173, 175, 177 and 178 as not instrument work and does not rule them. This card agrees with the ruling and adds the per-brief step and input.",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Accept all 14 (Recommended)\" (preliminary at 11:40Z, made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true,
+   "merged": "511cf165f77359be8daf2b402e754d9dc0b6a5a2"
+  },
+  "E11-D15": {
+   "object": "dev/governance/dimensions/D15.md",
+   "proposal": "Change the brief: name the tracked list of installs that sent a bundle as the universe, each row with the bundle's date and the steps run on it, so a round with no bundle reports 0 of n and not `unfinished`; step 1 gains the input the replay-mask escape shows it did not drive: a real download whose replay half is empty because one entity id escapes the mask. Each escape row of the hand ledger names the step and the input.",
+   "term": "`escapes` owned by D15: 1 in round 10's window by the hand read, toward 0; `coverage` of D15: counts 0 today (0018 section 2: a step reporting no denominator counts 0; 0 of 8 round-10 rows carry one), toward a read share",
+   "null_control": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` on round 10's reports prints 0 rows with examined/universe for every dimension, this one included: a brief left unchanged keeps printing 0; the escapes ledger's row count for a dimension whose step gains no input does not move",
+   "cost": "The brief's own lines (36 today) and one policy pull request under the owner's review; the seats' token cost is NO-READ until R11-PRE-TOKEN-LEDGER lands. No figure for round 11's work is given here.",
+   "finder_critical": "yes: it changes this dimension's brief, which its finder seats run from",
+   "already_ruled": "tvofi, 2026-11-13: every dimension covers its whole scope each round with a reported denominator (roster group R10-DIMENSIONS-FULL-COVERAGE; carries 174 to 178 on R11-INTAKE-R10-RESIDUE name the brief edits decision 0018 owes; card E11-COMMON reports that no group builds the denominator rule itself). The round-end triage (dev/programme/triage/r10-round-end.md (pull request 3609; on main at 26dbf7c43e, after the graded SHA), P768) lists carries 173, 175, 177 and 178 as not instrument work and does not rule them. This card agrees with the ruling and adds the per-brief step and input.",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Accept all 14 (Recommended)\" (preliminary at 11:40Z, made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true,
+   "merged": "f1520e3539b82407e56be9fe915d8a57ad6aedef"
+  },
+  "E11-D2": {
+   "object": "dev/governance/dimensions/D2.md",
+   "proposal": "Change the brief: name the identity list and its grid as a command's output, and add the inputs the escapes and seat-found defects show steps 3 and 5 did not drive: the savings identity on a month booked from a valve house with the buffer above the curve and on a ledger month upgraded mid-month from the previous release; a power entity that is the pump's own estimate; a covariate moved to another sensor; the tank reading's fall after a charge starts; the plan's booked space energy against a metered month; a learned draw range fed censored samples (R10-SETPOINT-BOOST's second cause; its first, the written value, is card E11-U9's); to step 1 a switch-back interval after a hot-water run (the unsensed slab). Each escape row of the hand ledger names the step and the input.",
+   "term": "`escapes` owned by D2: 5 in round 10's window by the hand read, toward 0; `coverage` of D2: counts 0 today (0018 section 2: a step reporting no denominator counts 0; 0 of 5 round-10 rows carry one), toward a read share",
+   "null_control": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` on round 10's reports prints 0 rows with examined/universe for every dimension, this one included: a brief left unchanged keeps printing 0; the escapes ledger's row count for a dimension whose step gains no input does not move",
+   "cost": "The brief's own lines (53 today) and one policy pull request under the owner's review; the seats' token cost is NO-READ until R11-PRE-TOKEN-LEDGER lands. No figure for round 11's work is given here.",
+   "finder_critical": "yes: it changes this dimension's brief, which its finder seats run from",
+   "already_ruled": "tvofi, 2026-11-13: every dimension covers its whole scope each round with a reported denominator (roster group R10-DIMENSIONS-FULL-COVERAGE; carries 174 to 178 on R11-INTAKE-R10-RESIDUE name the brief edits decision 0018 owes; card E11-COMMON reports that no group builds the denominator rule itself). The round-end triage (dev/programme/triage/r10-round-end.md (pull request 3609; on main at 26dbf7c43e, after the graded SHA), P768) lists carries 173, 175, 177 and 178 as not instrument work and does not rule them. This card agrees with the ruling and adds the per-brief step and input.",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Accept all 14 (Recommended)\" (preliminary at 11:40Z, made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true,
+   "merged": "f1520e3539b82407e56be9fe915d8a57ad6aedef"
+  },
+  "E11-D3": {
+   "object": "dev/governance/dimensions/D3.md",
+   "proposal": "Change the brief: delete the sampling instruction: the universe is the unpinned sites and surviving mutants `tests/mutation_table.py --scope full` prints, each seat owning cells of it, rotation carrying what a round does not reach.",
+   "term": "`coverage` of D3: counts 0 today (0018 section 2: a step reporting no denominator counts 0; 0 of 15 round-10 rows carry one), toward a read share",
+   "null_control": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` on round 10's reports prints 0 rows with examined/universe for every dimension, this one included: a brief left unchanged keeps printing 0",
+   "cost": "The brief's own lines (46 today) and one policy pull request under the owner's review; the seats' token cost is NO-READ until R11-PRE-TOKEN-LEDGER lands. No figure for round 11's work is given here.",
+   "finder_critical": "yes: it changes this dimension's brief, which its finder seats run from",
+   "already_ruled": "tvofi, 2026-11-13: every dimension covers its whole scope each round with a reported denominator (roster group R10-DIMENSIONS-FULL-COVERAGE; carries 174 to 178 on R11-INTAKE-R10-RESIDUE name the brief edits decision 0018 owes; card E11-COMMON reports that no group builds the denominator rule itself). The round-end triage (dev/programme/triage/r10-round-end.md (pull request 3609; on main at 26dbf7c43e, after the graded SHA), P768) lists carries 173, 175, 177 and 178 as not instrument work and does not rule them. This card agrees with the ruling and adds the per-brief step and input.",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Accept all 14 (Recommended)\" (preliminary at 11:40Z, made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true,
+   "merged": "511cf165f77359be8daf2b402e754d9dc0b6a5a2"
+  },
+  "E11-D4": {
+   "object": "dev/governance/dimensions/D4.md",
+   "proposal": "Change the brief: step 1's universe becomes every state of `tests/card_drift.mjs --list` times every language the population prints, and step 1 gains the input the Health-tab escape shows it did not drive: the released build's card rendered in a real Home Assistant frontend; step 2 gains a value of the wrong physical kind typed into each numeric option. Each escape row of the hand ledger names the step and the input.",
+   "term": "`escapes` owned by D4: 2 in round 10's window by the hand read, toward 0; `coverage` of D4: counts 0 today (0018 section 2: a step reporting no denominator counts 0; 0 of 3 round-10 rows carry one), toward a read share",
+   "null_control": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` on round 10's reports prints 0 rows with examined/universe for every dimension, this one included: a brief left unchanged keeps printing 0; the escapes ledger's row count for a dimension whose step gains no input does not move",
+   "cost": "The brief's own lines (48 today) and one policy pull request under the owner's review; the seats' token cost is NO-READ until R11-PRE-TOKEN-LEDGER lands. No figure for round 11's work is given here. A real Home Assistant frontend is an environment the brief says no seat has (`There is no Home Assistant frontend locally`): the input costs standing one up, or a recorded render from the owner's install, which this card does not price.",
+   "finder_critical": "yes: it changes this dimension's brief, which its finder seats run from",
+   "already_ruled": "tvofi, 2026-11-13: every dimension covers its whole scope each round with a reported denominator (roster group R10-DIMENSIONS-FULL-COVERAGE; carries 174 to 178 on R11-INTAKE-R10-RESIDUE name the brief edits decision 0018 owes; card E11-COMMON reports that no group builds the denominator rule itself). The round-end triage (dev/programme/triage/r10-round-end.md (pull request 3609; on main at 26dbf7c43e, after the graded SHA), P768) lists carries 173, 175, 177 and 178 as not instrument work and does not rule them. This card agrees with the ruling and adds the per-brief step and input.",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Accept all 14 (Recommended)\" (preliminary at 11:40Z, made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true,
+   "merged": "511cf165f77359be8daf2b402e754d9dc0b6a5a2"
+  },
+  "E11-D5": {
+   "object": "dev/governance/dimensions/D5.md",
+   "proposal": "Change the brief: give steps 1 to 3 a universe by command (the documents `text_ledger.py units --dim D6` lists, the links and headings a tracked script prints) so each row reports examined over it.",
+   "term": "`coverage` of D5: counts 0 today (0018 section 2: a step reporting no denominator counts 0; 0 of 7 round-10 rows carry one), toward a read share",
+   "null_control": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` on round 10's reports prints 0 rows with examined/universe for every dimension, this one included: a brief left unchanged keeps printing 0",
+   "cost": "The brief's own lines (41 today) and one policy pull request under the owner's review; the seats' token cost is NO-READ until R11-PRE-TOKEN-LEDGER lands. No figure for round 11's work is given here.",
+   "finder_critical": "yes: it changes this dimension's brief, which its finder seats run from",
+   "already_ruled": "tvofi, 2026-11-13: every dimension covers its whole scope each round with a reported denominator (roster group R10-DIMENSIONS-FULL-COVERAGE; carries 174 to 178 on R11-INTAKE-R10-RESIDUE name the brief edits decision 0018 owes; card E11-COMMON reports that no group builds the denominator rule itself). The round-end triage (dev/programme/triage/r10-round-end.md (pull request 3609; on main at 26dbf7c43e, after the graded SHA), P768) lists carries 173, 175, 177 and 178 as not instrument work and does not rule them. This card agrees with the ruling and adds the per-brief step and input.",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Accept all 14 (Recommended)\" (preliminary at 11:40Z, made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true,
+   "merged": "511cf165f77359be8daf2b402e754d9dc0b6a5a2"
+  },
+  "E11-D6": {
+   "object": "dev/governance/dimensions/D6.md",
+   "proposal": "Change the brief: step 2 gains the input the COP escape shows it did not drive: a claim whose truth depends on the install (here `measured COP` with no heat input configured) is checked on each population level that decides it, the levels read from `check_scopes.py --population`. Each escape row of the hand ledger names the step and the input.",
+   "term": "`escapes` owned by D6: 1 in round 10's window by the hand read, toward 0; `coverage` of D6: counts 0 today (0018 section 2: a step reporting no denominator counts 0; 0 of 9 round-10 rows carry one), toward a read share",
+   "null_control": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` on round 10's reports prints 0 rows with examined/universe for every dimension, this one included: a brief left unchanged keeps printing 0; the escapes ledger's row count for a dimension whose step gains no input does not move",
+   "cost": "The brief's own lines (28 today) and one policy pull request under the owner's review; the seats' token cost is NO-READ until R11-PRE-TOKEN-LEDGER lands. No figure for round 11's work is given here.",
+   "finder_critical": "yes: it changes this dimension's brief, which its finder seats run from",
+   "already_ruled": "tvofi, 2026-11-13: every dimension covers its whole scope each round with a reported denominator (roster group R10-DIMENSIONS-FULL-COVERAGE; carries 174 to 178 on R11-INTAKE-R10-RESIDUE name the brief edits decision 0018 owes; card E11-COMMON reports that no group builds the denominator rule itself). The round-end triage (dev/programme/triage/r10-round-end.md (pull request 3609; on main at 26dbf7c43e, after the graded SHA), P768) lists carries 173, 175, 177 and 178 as not instrument work and does not rule them. This card agrees with the ruling and adds the per-brief step and input.",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Accept all 14 (Recommended)\" (preliminary at 11:40Z, made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true,
+   "merged": "511cf165f77359be8daf2b402e754d9dc0b6a5a2"
+  },
+  "E11-D7": {
+   "object": "dev/governance/dimensions/D7.md",
+   "proposal": "Change the brief: step 5's universe becomes the additions a command lists (the modules added since the previous baseline, `git diff --name-status`) each with its pinning test, replacing the spot mutation.",
+   "term": "`coverage` of D7: counts 0 today (0018 section 2: a step reporting no denominator counts 0; 0 of 6 round-10 rows carry one), toward a read share",
+   "null_control": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` on round 10's reports prints 0 rows with examined/universe for every dimension, this one included: a brief left unchanged keeps printing 0",
+   "cost": "The brief's own lines (40 today) and one policy pull request under the owner's review; the seats' token cost is NO-READ until R11-PRE-TOKEN-LEDGER lands. No figure for round 11's work is given here.",
+   "finder_critical": "yes: it changes this dimension's brief, which its finder seats run from",
+   "already_ruled": "tvofi, 2026-11-13: every dimension covers its whole scope each round with a reported denominator (roster group R10-DIMENSIONS-FULL-COVERAGE; carries 174 to 178 on R11-INTAKE-R10-RESIDUE name the brief edits decision 0018 owes; card E11-COMMON reports that no group builds the denominator rule itself). The round-end triage (dev/programme/triage/r10-round-end.md (pull request 3609; on main at 26dbf7c43e, after the graded SHA), P768) lists carries 173, 175, 177 and 178 as not instrument work and does not rule them. This card agrees with the ruling and adds the per-brief step and input.",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Accept all 14 (Recommended)\" (preliminary at 11:40Z, made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true,
+   "merged": "511cf165f77359be8daf2b402e754d9dc0b6a5a2"
+  },
+  "E11-D8": {
+   "object": "dev/governance/dimensions/D8.md",
+   "proposal": "Change the brief: name the command that prints step 1's cells (entity by state by language) and add to step 2 the inputs the escapes show it did not drive: a step's reason on a house whose learned heat-loss scale is above 1.1 under flat weather, and a merged plan slot's average-power attribute on a non-modulating pump with a minimum power. Each escape row of the hand ledger names the step and the input.",
+   "term": "`escapes` owned by D8: 2 in round 10's window by the hand read, toward 0; `coverage` of D8: counts 0 today (0018 section 2: a step reporting no denominator counts 0; 0 of 5 round-10 rows carry one), toward a read share",
+   "null_control": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` on round 10's reports prints 0 rows with examined/universe for every dimension, this one included: a brief left unchanged keeps printing 0; the escapes ledger's row count for a dimension whose step gains no input does not move",
+   "cost": "The brief's own lines (56 today) and one policy pull request under the owner's review; the seats' token cost is NO-READ until R11-PRE-TOKEN-LEDGER lands. No figure for round 11's work is given here.",
+   "finder_critical": "yes: it changes this dimension's brief, which its finder seats run from",
+   "already_ruled": "tvofi, 2026-11-13: every dimension covers its whole scope each round with a reported denominator (roster group R10-DIMENSIONS-FULL-COVERAGE; carries 174 to 178 on R11-INTAKE-R10-RESIDUE name the brief edits decision 0018 owes; card E11-COMMON reports that no group builds the denominator rule itself). The round-end triage (dev/programme/triage/r10-round-end.md (pull request 3609; on main at 26dbf7c43e, after the graded SHA), P768) lists carries 173, 175, 177 and 178 as not instrument work and does not rule them. This card agrees with the ruling and adds the per-brief step and input.",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Accept all 14 (Recommended)\" (preliminary at 11:40Z, made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true,
+   "merged": "f1520e3539b82407e56be9fe915d8a57ad6aedef"
+  },
+  "E11-D9": {
+   "object": "dev/governance/dimensions/D9.md",
+   "proposal": "Change the brief: name the command that prints each metric's universe (the coordinator's collections, the entities with attributes, the solve paths of a cycle) so each row reports examined over it.",
+   "term": "`coverage` of D9: counts 0 today (0018 section 2: a step reporting no denominator counts 0; 0 of 3 round-10 rows carry one), toward a read share",
+   "null_control": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` on round 10's reports prints 0 rows with examined/universe for every dimension, this one included: a brief left unchanged keeps printing 0",
+   "cost": "The brief's own lines (62 today) and one policy pull request under the owner's review; the seats' token cost is NO-READ until R11-PRE-TOKEN-LEDGER lands. No figure for round 11's work is given here.",
+   "finder_critical": "yes: it changes this dimension's brief, which its finder seats run from",
+   "already_ruled": "tvofi, 2026-11-13: every dimension covers its whole scope each round with a reported denominator (roster group R10-DIMENSIONS-FULL-COVERAGE; carries 174 to 178 on R11-INTAKE-R10-RESIDUE name the brief edits decision 0018 owes; card E11-COMMON reports that no group builds the denominator rule itself). The round-end triage (dev/programme/triage/r10-round-end.md (pull request 3609; on main at 26dbf7c43e, after the graded SHA), P768) lists carries 173, 175, 177 and 178 as not instrument work and does not rule them. This card agrees with the ruling and adds the per-brief step and input.",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Accept all four (Recommended)\" (cards E11-D9, E11-U9, E11-U10, E11-GATE-REDS). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true,
+   "merged": "f1520e3539b82407e56be9fe915d8a57ad6aedef"
+  },
+  "E11-COMMON": {
+   "object": "dev/governance/roles/COMMON.md",
+   "paths": [
+    "dev/governance/roles/COMMON.md",
+    "dev/audit/config/finding.schema.json",
+    ".claude/workflows/audit-find.js"
+   ],
+   "proposal": "Add the denominator rule to the finder's contract and to the coverage row of the finding schema (and the copy audit-find.js inlines): each row names the command that printed its step's universe and reports examined over universe; a step reporting none counts 0; what a seat did not reach is listed for rotation. Replace the count and clock bounds (`Prefer three findings`, `about two hours`) by the cells `check_scopes.py --seat` already hands a seat.",
+   "term": "`coverage` (layer 1): 0 in all 16 dimensions for round 10 (0 of 113 rows carry the pair as keys; 34 rows state a count in prose, which no command can sum), toward a read share per dimension; it is also the read `unexamined` needs for a pass over a late merge.",
+   "null_control": "`python3 dev/audit/rounds/round11/evaluation/dimension_read.py --repo . --ref a39627da59 --round 10 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` over round 10's reports prints `WITH_EXAMINED_UNIVERSE 0`; the same command over a round whose rows carry the pair prints their count, so the read moves only where the rule is present. `python3 tools/audit/check_scopes.py --repo . --ref a39627da59` stays rc 0: no universe changes.",
+   "cost": "One policy pull request under the owner's review: COMMON.md is 108 lines and budgeted by `policy_lint.mjs --budgets`; the schema row gains two required keys; every finder report grows by one pair per step. The seats' token cost of reporting it is NO-READ until R11-PRE-TOKEN-LEDGER.",
+   "already_ruled": "tvofi, 2026-11-13 (roster group R10-DIMENSIONS-FULL-COVERAGE's brief): every dimension reports a denominator, two dimensions are added (actuator write safety and liveness; feature behaviour against its documented effect). Only part 1 merged (pull request 3572: a grader in tools/policy/check-wave-script.mjs); the group's stage is `done`. No open group and no carry owes part 2 itself: carries 169 and 180 on R11-INTAKE-R10-RESIDUE only wait on it, and `git ls-remote origin | grep -i dimensions-full` shows archive tags of the merged part and no live branch. The round-end triage (dev/programme/triage/r10-round-end.md (pull request 3609; on main at 26dbf7c43e, after the graded SHA)) does not rule it. This card agrees with the owner's ruling and reports that nothing on the roster builds it.",
+   "finder_critical": "yes: it changes the finder's contract, the finding schema and audit-find.js's inlined copy, so every finder report of round 11",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Accept both parts (Recommended)\" (made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true,
+   "merged": "b94425b94f0d25a02576e98fa10a8ff324974a0c"
+  },
+  "E11-INJECTED": {
+   "paths": [
+    "dev/governance/roles/fix-review.md",
+    "dev/governance/roles/fixer.md"
+   ],
+   "proposal": "This card carries an item already owed to round 11; it proposes no text of its own. For pull request 3404 the root-cause seat's record exists: `git show archive/handoff-wip/r10-rca-setpoint-latch-deadlock:dev/audit/rca/R10-RCA-SETPOINT-LATCH-DEADLOCK.md` (442 lines, commit 2e20aa5d4e, on that archive tag and not on main). It names the cause (the off restore refused the write itself, not only the capture, so an install upgraded with a persisted record equal to the pump's reading never wrote again), process state (a) (`No contract asks that a refusal on an actuator write have a release that needs no person`), a cost test, a built detector, and drafted text: a new `fix-review.md` step, `A new refusal on an actuator write names its release`, which asks the body to name what ends the refusal on a valid configuration, a check that drives its entry state, `persisted state from the previous release included`, to that end, and `blocked` where the release needs a person `unless the owner, in person, accepted it on the pull request`; and one sentence for `fixer.md` step 3, `A guard that refuses an actuator write is also driven from the previous release's persisted state, and its release needs no person`. `git show a39627da59:dev/programme/HANDOVER.md | sed -n 1546,1557p` lists the record under `Owed to round 11, with the owner's ruling behind each` and says its countermeasure sections have `no roster group, carry or pull request`. Rule: land the record and its two drafted texts as written (the owner's review, or the mandate), or record the refusal. Two more causes are named by a tracked root-cause record, `dev/audit/rca/R10-RCA-SAV-ESTIMATE.md` at the graded SHA: pull request 2411 (line 17: it made the reference's first step steady and left the tanks as measured) and, as `a second, independent cause` from v7.1.0, pull request 2887 (lines 65 to 66; the fix of R10-BUFFER-STORE); the record reads 2411's own review and gives process state (c), so no further root-cause read is asked for the savings reference. What no root-cause seat has read: pull request 2411's other defect, the coverage factor of R10-SAVINGS-NEGATIVE (the fixing group's word), and pull request 3587 (R10-HOTFIX-REFERENCE-BASIS: the booked reference changed with no basis-stamp bump, caught before a release); 0018 section 3 asks for those two reviews to be read before any contract text is drafted for them.",
+   "term": "`injected` (layer 1): 4 causes named by hand (3404, 2411, 2887, 3587), 3 of them by a root-cause record, over 155 production merges of the window by 0018's own class (`python3 tools/audit/machinery_ratchet.py --measure --repo . --head 13cbe48de4 --window 1139` -> production 155; the window holds 1139 merges on the first-parent chain): 2.58 per 100, toward 0. A proxy while no enumerator reads the cause. Beside it `first_pass` 467/909 and real-catch incidence 214/909, which rank nothing while `injected` and `escapes` are NO-READ (0018 section 5).",
+   "null_control": "The record's own: its detector exits 0 at v7.1.11 (before pull request 3404) and 1 at v7.1.12, and 6 of 6 hand mutants are killed. On a merged pull request that adds no refusal on an actuator write the drafted step asks for nothing, so its first verdict cannot move; the hand ledger's in-window rows with no cause named (23 of 26) do not move either.",
+   "cost": "The record's cost test: about 1 s per run for the detector and about 20 min of reviewer time per 30 days for the policy line, against about 6 h of programme time per occurrence and a house without heat. `fix-review.md`'s `files_tokens` budget has no headroom (HANDOVER.md, the same paragraph), so the step needs an equal deletion or a raise under decision 0013. Report-only beside it: `review_strength.py --guardrail` prints `would-trip` for the cloud arm (1/20) and the sonnet arm (1/20) at the round's end, and its own action (audit the last reviews with a planted defect) is wired to nothing.",
+   "already_ruled": "tvofi, 2026-11-13 (HANDOVER.md lines 1546 to 1557 at the graded SHA): the release rule and the record are owed to round 11; the owner's rule overrides the record's refusal (iv), the stamp-time release-note rule. Not ruled in the round-end triage (P742 to P795 rule instruments); process card P7 (found_by and caused_by fields, folded into P744) builds the record of a cause, not the check.",
+   "finder_critical": "no: it changes nothing a finder seat reads or runs in round 11 (the fixer's and the fix reviewer's contracts)",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Accept, pay by deletion (Recommended)\" (a budget raise returns to tvofi only if no sound cut exists). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": false
+  },
+  "E11-N-OBJECTIVE-RECORD": {
+   "object": "dev/governance/roles/orchestrator.md",
+   "paths": [
+    "dev/audit/yardstick/round10/OBJECTIVE.json",
+    "dev/governance/roles/orchestrator.md"
+   ],
+   "proposal": "Round 10 closed with no objective record: `dev/audit/yardstick/round10/OBJECTIVE.json` is in no ref (`git log --all --oneline -- dev/audit/yardstick/round10` prints nothing). 0018 section 6 gives the write to the closing orchestrator, once. Two parts: (a) round 10's record is written now by the orchestrator, each term a value with a tracked enumerator or `no_read` with `would_read` and `builder`; the `terms` block of this evaluation holds a re-run read or a NO-READ for each of the 13 that it can be checked against; (b) orchestrator.md's closure section names the record as a closure criterion, since today only `dev/audit/README.md` phase 13's artefact column does and the contract's one mention of 0018 is in section 14.",
+   "term": "All 13 terms: from no record (every comparison with round 11 undecided on round 10's side) to read or NO-READ rows; `check_scopes.py --round 11` drops its first gap.",
+   "null_control": "`python3 tools/audit/check_scopes.py --repo . --ref a39627da59` (no `--round`) is rc 0 before and after; with `--round 11` the gap naming `dev/audit/yardstick/round10/OBJECTIVE.json` is printed only while the file is absent.",
+   "cost": "One JSON file of 13 rows and one sentence in a 289-line contract under a `--budgets` cap. Until R11-PRE-ROUND-METRICS and R11-PRE-TOKEN-LEDGER land, 9 of the 13 rows can only be `no_read`. A further cost of the record's absence, measured by the reviewer: nothing live guards the unowned cards, since `check_scopes.py --round` compares their count with the record's `unowned` value; dropping one leaves the check silent, while dropping a threshold or a criterion card is refused.",
+   "already_ruled": "Round-end triage P747 logs R11-PRE-OBJECTIVE-FUNCTION as done, its carry 5 (the playbook's pointer to the evaluator contract) landed at `dev/audit/README.md`. Part (b) is not that carry: it asks the orchestrator's own contract to name the closing record, which P747 does not list; if the owner reads P747 as closing it, part (b) falls and part (a) stands alone.",
+   "finder_critical": "no: it changes nothing a finder reads. It does gate the finder start mechanically: `audit-find.js` runs `check_scopes.py --round` in its Prepare step, which refuses the baseline while the record is absent",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Write it now (Recommended)\" (made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true,
+   "merged": "921214bf4246338c1a83fbc5269eaa0bfe91b7d5",
+   "merged_note": "Two merges built it: 646352ff13 (pull request 3611, part (a), dev/audit/yardstick/round10/OBJECTIVE.json) and 921214bf42 (pull request 3626, part (b), dev/governance/roles/orchestrator.md, the card's object); the object's is recorded."
+  },
+  "E11-SCORECARD": {
+   "object": "tools/audit/seat/instruments/scorecard.py.md",
+   "proposal": "The scorecard gets the input producer and the window 0018 section 2 asks of line `A_gate`: today every input-fed line prints `unread` because `<state>/scorecard/` is never written, and `A_gate` reads the last 20 runs.",
+   "term": "`product_green` (layer 1): no value from its named enumerator for round 10, toward a windowed share. This seat's own read, a proxy from GitHub: 528/632 (0.835); cancelled beside it: 198; failed runs whose gate job succeeded: 187; failed runs read: 291; unread: 0.",
+   "null_control": "`python3 tools/audit/seat/scorecard.py report --dir <empty dir> --train-log <empty file> --repo .` prints `A_gate  unread (runs.json)`: an empty input is never a value (re-run here).",
+   "cost": "The cost is roster group R11-PRE-ROUND-METRICS's; no figure is given here.",
+   "already_ruled": "Round-end triage P744 (ACCEPT, BUILD): the scorecard's input producer on R11-PRE-ROUND-METRICS. This scoring agrees.",
+   "finder_critical": "no: it changes nothing a finder seat reads or runs in round 11",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Accept, built beside finders (Recommended)\". Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": false
+  },
+  "E11-GATE-REDS": {
+   "paths": [
+    ".github/workflows/ci.yml",
+    ".github/workflows/tests.yml",
+    ".github/workflows/governance.yml"
+   ],
+   "proposal": "A red main run records its cause (product fault, instrument fault, runner or GitHub outage) where the hotfix or the re-run that cleared it is recorded, so a gate's yield (reds a product fault caused) and its cost (reds none caused) can be read. Nothing else is proposed: this card moves no check out of `gate`. Of the 104 runs whose `gate` did not succeed, the only failed job was `tests / ci-ratchet` on 69, `tests / fast (3.14)` on 12, `governance / instrument-self-tests` on 3, none on 1, several on 19; `never a product fault` cannot be decided for any of them while no red carries its cause.",
+   "term": "`product_green` (layer 1): 528/632 (0.835); cancelled beside it: 198; failed runs whose gate job succeeded: 187; failed runs read: 291; unread: 0 over the CI workflow's life in the window (from 2026-10-23); by run conclusion 341 of 632 concluded runs succeeded. The card moves the term by nothing; it makes the split of its misses readable. 0018 section 5 names `move a check out of gate` as this term's cheapest false move, with `gate`'s check count as the control: that move was made once inside the window (`tests / ci-ratchet` report-only on a push at ef4556bb42, 2026-11-12), so the share before and after it is not one series, and the count is `python3 -I -c \"import sys; sys.path.insert(0,'tools/ci'); import gate; print(gate.REQUIRED['push'])\"` -> 17 at the graded SHA with no command that prints it per window (R11-PRE-ROUND-METRICS).",
+   "null_control": "A run with no red job carries no cause field and reads as before; `gate_reds.py report` prints the same share before and after the field exists.",
+   "cost": "One field per red-main hotfix group or re-run record. The runner seconds these reds cost are NO-READ (R11-PRE-ROUND-METRICS).",
+   "already_ruled": "Process card P7 (tvofi yes, 2026-11-13; found_by and caused_by on hotfix and outside groups, folded into P744 by the round-end triage) already builds the group half of this record: a red main that got a hotfix group gains its cause there. What P7 does not reach is a red cleared by a re-run with no group. Round-end triage P786 rules the `policy-docs` timeout and P762/P763 the self-test scope table. This card agrees with those.",
+   "finder_critical": "no: it changes nothing a finder seat reads or runs in round 11",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Accept all four (Recommended)\" (cards E11-D9, E11-U9, E11-U10, E11-GATE-REDS). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": false
+  },
+  "E11-R-WORKFLOWS": {
+   "paths": [
+    ".claude/workflows/audit-fix.js",
+    ".claude/workflows/audit-wave.js"
+   ],
+   "proposal": "Remove the two retired workflow scripts. Both push their fixer to a branch `claude/audit-fix-<group>`; the 9 pull requests ever opened from that pattern date 2026-09-02 and 2026-09-03, none in round 9's window or round 10's, and both scripts have described themselves as RETIRED since 785963eba4 (2026-09-08).",
+   "term": "No term of 0018 section 2 moves: no layer-1 term is taken through either script. The machinery tie-break (`machinery_ratchet.py --measure`, rule 4) falls by their 146 lines.",
+   "null_control": "The same measure is not zero for a script in use: `flow_metrics.py` counts 880 merged fix branches of the live `fix/` pattern in round 10's window.",
+   "cost": "`git grep -l 'audit-fix\\|audit-wave' -- tests tools` -> `tests/closure.py`, `tests/closures.json`, `tools/ci/selftest_closures.json` and `tools/audit/seat/plan_audit.py` name them and each needs its entry dropped in the same pull request (a closure re-record on Linux, `gate-scoping.md`); the skill listing loses two entries marked RETIRED. `audit-wave.js`'s header says its prompts are hand-mirrored from `audit-fix.js`, so the pair goes together.",
+   "finder_critical": "no: it changes nothing a finder seat reads or runs in round 11 (`audit-find.js` is not touched)",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Accept both (Recommended)\" (cards E11-R-WORKFLOWS and E11-N-NULL-REVIEWER). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": false
+  },
+  "E11-N-ROLE-CLAUSE": {
+   "paths": [
+    "tools/audit/seat/review_strength.py",
+    ".claude/workflows/web-fix-wave.js"
+   ],
+   "proposal": "0018 section 3: a role contract is scorable per clause `never, until a block's class names the clause`. No roster group builds that. Rule one: name the group that makes a block's class cite the contract clause it enforces, or accept that role contracts stay scored per role only.",
+   "term": "The unscored share of role objects (15 of 19 keep on a NO-READ at this evaluation); no term of section 2 moves.",
+   "null_control": "`python3 tools/audit/seat/review_strength.py --repo . --window r10=2026-10-14T13:27:06Z..2026-11-15T05:22:47Z` `--by class` prints 2537 verdicts under class words and no clause id today; a class word that maps to no clause stays its own row.",
+   "cost": "Unmeasured; the verdict grammar is `web-fix-wave.js`'s VERDICT_CLASSES, read by review_strength.py.",
+   "finder_critical": "no: it changes nothing a finder seat reads or runs in round 11",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Build all four reads\" (made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": false
+  },
+  "E11-N-RULE-YIELD": {
+   "paths": [
+    "dev/audit/config/bugclasses.json",
+    "tools/audit/fold_ledger.py"
+   ],
+   "proposal": "0018 section 3: a rule is not scorable because `bugclasses.json` records no instance date and nothing counts a load. No roster group builds either. Rule one: name the group that dates each instance (the ledger holds 758 instances in 55 classes) and counts a rule's loads, or accept that all 12 rule objects stay unscored.",
+   "term": "The unscored share of rule objects (12 of 12 at this evaluation); beside it D14's read `fold_ledger.py check` (55 classes, 758 instances, 0 violations).",
+   "null_control": "`python3 tools/audit/fold_ledger.py check` reads 0 violations before and after a date field is added to an instance: the check does not move, only the rule's yield becomes readable.",
+   "cost": "Unmeasured. `.claude/rules/` is generated and loaded by path globs, so a load count would come from the harness, which no tracked script reads.",
+   "already_ruled": "Benchmark card G8 (a rule-enforcement registry, accepted; `dev/audit/README.md`) maps a rule to its enforcing check; roster group R10-ROUND-PLAYBOOK carried it and is done, and no open group holds it. Not ruled in the round-end triage.",
+   "finder_critical": "no: it changes nothing a finder seat reads or runs in round 11",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Build all four reads\" (made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": false
+  },
+  "E11-N-INSTRUMENT-YIELD": {
+   "paths": [],
+   "paths_note": "no exact file can be named: the queued builder group R11-PRE-NO-READ-BUILDERS lists no file for a refusal log, and `check_scopes.py` compares exact file names, so a directory can never match; the card needs the file its build adds written here before it is recorded merged",
+   "proposal": "0018 section 3: an instrument's yield is NO-READ `until a refusal is logged with its outcome`. No roster group builds that log. Rule one: name the group that makes an instrument's refusal a logged line with what followed (a fix, an override, nothing), or accept that all 124 instrument objects stay unscored on yield while their cost is read.",
+   "term": "The unscored share of instrument objects (123 of 124 keep on a NO-READ); cost beside it from `python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref a39627da59 --start v7.0.0 --end v10.0.0 --roster cbd6d9185166:dev/programme/rosters/wave-r10-groups.json`: `tools/audit/seat/merge_train.py` 2416 to 11585 lines over the window, the machinery over product ratio 1.91 (`scorecard.py` line `S`), 477 non-production merges in the newest 580.",
+   "null_control": "An instrument whose `--self-test` passes and that refused nothing logs nothing: its yield reads 0 refusals, not unread.",
+   "cost": "Unmeasured. The round-end triage keeps R11-PRE-MACHINERY-LIMITER (P742), which caps machinery by merges and churn, not by yield.",
+   "already_ruled": "Not ruled: P742 limits size, and loop-study card L1's enumerator (P744) counts changes per instrument, neither logs a refusal's outcome.",
+   "finder_critical": "no: it changes nothing a finder seat reads or runs in round 11",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Build all four reads\" (made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": false
+  },
+  "E11-N-GATE-CAUSE": {
+   "paths": [
+    "tools/ci/gate.py"
+   ],
+   "paths_note": "the file the queued builder group R11-PRE-NO-READ-BUILDERS lists for a cause per red gate run; no file is named there for a workflow script's run line",
+   "proposal": "0018 section 3: a gate's yield is NO-READ `until a red carries its cause`, and a `.claude/workflows/` script's runs are logged nowhere tracked. Rule one: name the group that records a cause per red run on a pull-request head and a run line per workflow script, or accept that the gate objects kept here stay unscored. For main, card E11-GATE-REDS asks the same record.",
+   "term": "The unscored share of gate objects (22 of 27 keep on a NO-READ).",
+   "null_control": "A successful run carries no cause field and reads as before.",
+   "cost": "Unmeasured.",
+   "already_ruled": "Process card P7 (tvofi yes, 2026-11-13, folded into P744) builds caused_by and found_by on hotfix and outside groups: the cause of a red that got a group. A red on a pull-request head and a workflow script's run have no group, and nothing ruled builds their record.",
+   "finder_critical": "no: it changes nothing a finder seat reads or runs in round 11",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Build all four reads\" (made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": false
+  },
+  "E11-N-INTAKE-BUILDER": {
+   "paths": [
+    "dev/programme/rosters/wave-r10-groups.json",
+    "dev/governance/decisions/0018-objective-function.md",
+    "dev/audit/config/objective.json"
+   ],
+   "proposal": "0018 and objective.json name R11-INTAKE-R10-RESIDUE as the builder of the reads behind `regret`, `operation`, `generality` (examined), `unowned`, `escapes` (found-by and owner), `coverage` (the denominator rule), `unexamined` (a late pass's denominator), the censuses of D1, D2, D8, D11 and D15, D12's cell ledger and the two NO-READ population axes. On the roster that group is a holding group: `git show cbd6d9185166:dev/programme/rosters/wave-r10-groups.json` reads size S, fixer model sonnet, stage not-started, 200 carries, note `holding group for round-10 residuals with no live owner; round-11 architect re-homes each carry`. `check_scopes.py --round` accepts it as a builder (`roster_lib.carry_receivable` is true), so the live control of 0018 section 5's last row passes while no group is sized or briefed to build these reads. Rule: which group builds each of carries 174 to 178, or which of these reads stay NO-READ for round 11 by the owner's acceptance.",
+   "term": "The distance of 7 of the 9 layer-1 terms stays unknown (never zero) until these reads exist; no term moves by this card.",
+   "null_control": "`roster_lib.carry_receivable` on a group at stage done reads false and `check_scopes.py --round` then refuses the builder: the control does fire on a closed group, it cannot tell a holding group from a builder.",
+   "cost": "Roster operations only for the re-homing; the builds' cost is not estimated here.",
+   "already_ruled": "Round-end triage P768 splits the group's instrument carries by seam and lists carries 173, 175, 177 and 178 as `Not instrument (the orchestrator's)`, 174 and 176 to P744. This card does not reopen P768; it reports that the non-instrument half, which holds the product terms' reads, has no builder ruled.",
+   "finder_critical": "yes in part: carries 175 and 177 are brief edits (D12's universe and cell ledger, the actuator-write draft, D0 and D15's oracle step, the censuses of D1, D2, D8, D11 and D15) and 174 and 176 hold the per-step denominator, all of which finders run from; the re-homing itself is roster work",
+   "decision": "accepted",
+   "ruling": "tvofi: \"New L group, design first (Recommended)\" (one new group for the product reads, beside the finders; terms first read at round 11's close). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": false
+  },
+  "E11-N-P744-SCOPE": {
+   "paths": [
+    "tools/audit/seat/scorecard.py",
+    "dev/programme/rosters/wave-r10-groups.json",
+    "tools/audit/seat/round_metrics.py"
+   ],
+   "proposal": "0018 section 2 names R11-PRE-ROUND-METRICS as the builder of `closure_slip` (the forecast history) and `unexamined` (from the roster's group kinds), and sections 4 and 5 of planted-defect recall and the two-finder overlap. The group's carries 1 and 3 name recall, overlap, `product_green`, the `lead_time` clock and runner seconds; neither its brief nor its carries name `closure_slip` or `unexamined` (only carry 0's general `build to 0018 section 2's definitions`), and P744's destination text names none of the four. Rule: P744's build includes carries 0 to 3 whole and the two terms by name, or each is carded elsewhere.",
+   "term": "`closure_slip` (layer 2), `unexamined` (layer 1) and the two held-out checks stay NO-READ past round 11's close if the narrowed group does not build them; 0018 section 4 is then claimed for no round.",
+   "null_control": "0018 itself: `an empty input prints unread, never a value`, the control carries 1 and 3 already ask of each enumerator.",
+   "cost": "Not estimated here; it is the group's.",
+   "already_ruled": "Round-end triage P744 (ACCEPT, BUILD, M) keeps the group, `narrowed by what is on main, widened by L1 and P7`. This scoring agrees with keeping it and asks only that the narrowing not drop the four reads.",
+   "finder_critical": "yes for two of the four reads: planted-defect recall writes defects into the baseline export the finders audit, and the two-finder overlap seats two finders on one universe, so both must exist before the finders run to be read for round 11; `closure_slip` and `unexamined` are read at the close and are not",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Wait for both (Recommended)\" (planted-defect recall and two-finder overlap gate the finders). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true,
+   "paths_note": "tools/audit/seat/round_metrics.py added at revision 4: it is the enumerator that reads `closure_slip` and `unexamined` (0018 section 2's builder R11-PRE-ROUND-METRICS put both there), and pull request 3658, which builds those two reads, changes only it among the tools. Planted-defect recall and the two-finder overlap are on main in tools/audit/seat/plant_recall.py and finder_overlap.py (2e7bced82e, pull request 3612). scorecard.py and the roster stay: pull request 3657 changes scorecard.py."
+  },
+  "E11-N-NULL-REVIEWER": {
+   "paths": [
+    "tools/audit/check_scopes.py"
+   ],
+   "proposal": "`check_scopes.py --round` lets a null `reviewer` pass its two-seats rule: `norm(ev.get('reviewer', ''))` turns JSON null into the string `none`, which is non-empty and differs from the evaluator's name. The reviewer measured it: with `review` set to approve at 33d89b15f3a7 and `reviewer` left null the check prints 45 gaps and none about the seats; with the evaluator's name respelled as reviewer it refuses. 0018 section 6 refuses `an evaluator and reviewer that are one name under case and punctuation, or either the orchestrator`; an absent reviewer should be refused with them. The file is code-owned and not this seat's to edit: rule a one-line refusal of a reviewer or evaluator that is not a non-empty string, with its `--self-test` arm.",
+   "term": "No term moves. It closes a way round the control 0018 section 5's last row calls live for a verdict: an evaluation approved by no named reviewer.",
+   "null_control": "`python3 tools/audit/check_scopes.py --self-test` drives a complete record that passes; the new arm refuses the same record with `reviewer` null and nothing else changed.",
+   "cost": "One condition and one self-test arm in a 926-line code-owned file; the check runs in under a second per round start.",
+   "finder_critical": "no: it changes no finder's work; it is a refusal at the round start, in the check `audit-find.js` runs before the baseline",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Accept both (Recommended)\" (cards E11-R-WORKFLOWS and E11-N-NULL-REVIEWER). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": false
+  },
+  "E11-T-product_green_floor": {
+   "object": "dev/audit/config/objective.json",
+   "threshold": "product_green_floor",
+   "proposal": "`thresholds.product_green_floor.value` is null (share of concluded runs): it is `product_green`'s target. Set it, or leave it unset. The file's `proposed` is 0.9, the round-10 orchestrator's, which 0018 says is read by nothing. Round 10's read beside it (a proxy, GitHub): 528/632 (0.835); cancelled beside it: 198; failed runs whose gate job succeeded: 187; failed runs read: 291; unread: 0.",
+   "term": "No term moves. While it is unset every comparison or result that needs it is undecided, neither held nor missed (0018 section 2).",
+   "null_control": "`check_scopes.py --round 11` refuses an unset threshold that no card carries and does not refuse one a card carries: the refusal moves with the card, no read does.",
+   "cost": "One value in a code-owned file, by the owner's own pull-request review; an accepted card must name the commit that set it.",
+   "finder_critical": "no: it changes nothing a finder seat reads or runs in round 11 (a threshold is read when two rounds are compared, at the close)",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Floor 0.90, rest unset (Recommended)\" (value 0.90; made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": false
+  },
+  "E11-T-closure_slip_ceiling": {
+   "object": "dev/audit/config/objective.json",
+   "threshold": "closure_slip_ceiling",
+   "proposal": "`thresholds.closure_slip_ceiling.value` is null (days per day): it is `closure_slip`'s target. Set it, or leave it unset. The file's `proposed` is 0.2, the round-10 orchestrator's, which 0018 says is read by nothing. Round 10's read: NO-READ (the forecast history exists only inside rendered plan pages; R11-PRE-ROUND-METRICS).",
+   "term": "No term moves. While it is unset every comparison or result that needs it is undecided, neither held nor missed (0018 section 2).",
+   "null_control": "`check_scopes.py --round 11` refuses an unset threshold that no card carries and does not refuse one a card carries: the refusal moves with the card, no read does.",
+   "cost": "One value in a code-owned file, by the owner's own pull-request review; an accepted card must name the commit that set it.",
+   "finder_critical": "no: it changes nothing a finder seat reads or runs in round 11 (a threshold is read when two rounds are compared, at the close)",
+   "decision": "deferred",
+   "ruling": "tvofi: \"Floor 0.90, rest unset (Recommended)\" (this threshold is left unset; made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record."
+  },
+  "E11-T-band_lead_time": {
+   "object": "dev/audit/config/objective.json",
+   "threshold": "band_lead_time",
+   "proposal": "`thresholds.band_lead_time.value` is null (relative difference): it is the band inside which two rounds' `lead_time` tie. Set it, or leave it unset. The file's `proposed` is 0.2, the round-10 orchestrator's, which 0018 says is read by nothing. Round 10's read: NO-READ (`flow_metrics.py` prints merge hours only: 517 of 759 hours had a merge).",
+   "term": "No term moves. While it is unset every comparison or result that needs it is undecided, neither held nor missed (0018 section 2).",
+   "null_control": "`check_scopes.py --round 11` refuses an unset threshold that no card carries and does not refuse one a card carries: the refusal moves with the card, no read does.",
+   "cost": "One value in a code-owned file, by the owner's own pull-request review; an accepted card must name the commit that set it.",
+   "finder_critical": "no: it changes nothing a finder seat reads or runs in round 11 (a threshold is read when two rounds are compared, at the close)",
+   "decision": "deferred",
+   "ruling": "tvofi: \"Floor 0.90, rest unset (Recommended)\" (this threshold is left unset; made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record."
+  },
+  "E11-T-band_closure_slip": {
+   "object": "dev/audit/config/objective.json",
+   "threshold": "band_closure_slip",
+   "proposal": "`thresholds.band_closure_slip.value` is null (relative difference): it is the band inside which two rounds' `closure_slip` tie. Set it, or leave it unset. The file's `proposed` is 0.2, the round-10 orchestrator's, which 0018 says is read by nothing. Round 10's read: NO-READ.",
+   "term": "No term moves. While it is unset every comparison or result that needs it is undecided, neither held nor missed (0018 section 2).",
+   "null_control": "`check_scopes.py --round 11` refuses an unset threshold that no card carries and does not refuse one a card carries: the refusal moves with the card, no read does.",
+   "cost": "One value in a code-owned file, by the owner's own pull-request review; an accepted card must name the commit that set it.",
+   "finder_critical": "no: it changes nothing a finder seat reads or runs in round 11 (a threshold is read when two rounds are compared, at the close)",
+   "decision": "deferred",
+   "ruling": "tvofi: \"Floor 0.90, rest unset (Recommended)\" (this threshold is left unset; made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record."
+  },
+  "E11-T-band_tokens_per_change": {
+   "object": "dev/audit/config/objective.json",
+   "threshold": "band_tokens_per_change",
+   "proposal": "`thresholds.band_tokens_per_change.value` is null (relative difference): it is the band inside which two rounds' `tokens_per_change` tie. Set it, or leave it unset. The file's `proposed` is 0.2, the round-10 orchestrator's, which 0018 says is read by nothing. Round 10's read: NO-READ (no token ledger; R11-PRE-TOKEN-LEDGER).",
+   "term": "No term moves. While it is unset every comparison or result that needs it is undecided, neither held nor missed (0018 section 2).",
+   "null_control": "`check_scopes.py --round 11` refuses an unset threshold that no card carries and does not refuse one a card carries: the refusal moves with the card, no read does.",
+   "cost": "One value in a code-owned file, by the owner's own pull-request review; an accepted card must name the commit that set it.",
+   "finder_critical": "no: it changes nothing a finder seat reads or runs in round 11 (a threshold is read when two rounds are compared, at the close)",
+   "decision": "deferred",
+   "ruling": "tvofi: \"Floor 0.90, rest unset (Recommended)\" (this threshold is left unset; made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record."
+  },
+  "E11-T-band_model_gap": {
+   "object": "dev/audit/config/objective.json",
+   "threshold": "band_model_gap",
+   "proposal": "`thresholds.band_model_gap.value` is null (share of C_real, per cell): it is the bound on one cell's model gap against its own `C_real`. Set it, or leave it unset. Round 10's read: NO-READ (no realised-cost record per install-day). The file carries no `proposed` for it.",
+   "term": "No term moves. While it is unset every comparison or result that needs it is undecided, neither held nor missed (0018 section 2).",
+   "null_control": "`check_scopes.py --round 11` refuses an unset threshold that no card carries and does not refuse one a card carries: the refusal moves with the card, no read does.",
+   "cost": "One value in a code-owned file, by the owner's own pull-request review; an accepted card must name the commit that set it.",
+   "finder_critical": "no: it changes nothing a finder seat reads or runs in round 11 (a threshold is read when two rounds are compared, at the close)",
+   "decision": "deferred",
+   "ruling": "tvofi: \"Floor 0.90, rest unset (Recommended)\" (this threshold is left unset; made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record."
+  },
+  "E11-K-D4": {
+   "object": "dev/audit/config/objective.json",
+   "criterion": "D4",
+   "proposal": "`owner_criteria.D4` is null: name the tracked file that holds the owner's acceptance criteria for the card and config flow beyond rendering (0018 section 1: measurement, then the owner). The brief quotes the owner: `It should be intuitive, user friendly and look professional`; no tracked file turns that into criteria. Or leave it unset. For the criterion to reach a finder, the same change makes D4's brief cite the criteria file; without that line the finders run as in round 10.",
+   "term": "No term moves. D4's perfect result stays undecided, not perfect (0018 section 1), and its distance has no enumerator until the criterion is set.",
+   "null_control": "`check_scopes.py --round 11` refuses a criterion that names a path not tracked at the ref, and an unset one with no card; `owner_criteria.D7`, already set to decision 0015, is refused by neither.",
+   "cost": "One path in a code-owned file, and the criteria file itself if none exists.",
+   "finder_critical": "no as the card stands: `git grep -l owner_criteria a39627da59` -> objective.json, decision 0018 and check_scopes.py only, so nothing a finder reads names the criterion file; it becomes yes only where D4's brief cites that file. tvofi ruled on 2026-11-15, preliminary (the coordinator's relay), `All four before finders`, with the group R11-PRE-OWNER-CRITERIA building them",
+   "decision": "accepted",
+   "ruling": "tvofi: \"All four before finders\" (finder-critical by this ruling; made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true,
+   "merged": "367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c"
+  },
+  "E11-K-D5": {
+   "object": "dev/audit/config/objective.json",
+   "criterion": "D5",
+   "proposal": "`owner_criteria.D5` is null: name the tracked file that holds the owner's acceptance criteria for docs structure and comments. The brief quotes the owner: `Comments in code should be concise but precise and easy to understand`; no tracked file turns that into criteria. Or leave it unset. For the criterion to reach a finder, the same change makes D5's brief cite the criteria file; without that line the finders run as in round 10.",
+   "term": "No term moves. D5's perfect result stays undecided, not perfect (0018 section 1), and its distance has no enumerator until the criterion is set.",
+   "null_control": "`check_scopes.py --round 11` refuses a criterion that names a path not tracked at the ref, and an unset one with no card; `owner_criteria.D7`, already set to decision 0015, is refused by neither.",
+   "cost": "One path in a code-owned file, and the criteria file itself if none exists.",
+   "finder_critical": "no as the card stands: `git grep -l owner_criteria a39627da59` -> objective.json, decision 0018 and check_scopes.py only, so nothing a finder reads names the criterion file; it becomes yes only where D5's brief cites that file. tvofi ruled on 2026-11-15, preliminary (the coordinator's relay), `All four before finders`, with the group R11-PRE-OWNER-CRITERIA building them",
+   "decision": "accepted",
+   "ruling": "tvofi: \"All four before finders\" (finder-critical by this ruling; made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true,
+   "merged": "367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c"
+  },
+  "E11-K-D9": {
+   "object": "dev/audit/config/objective.json",
+   "criterion": "D9",
+   "proposal": "`owner_criteria.D9` is null: name the tracked file that holds the owner's Pi-class budget per cost centre. No tracked file holds one. `tests/stress_budgets.json` exists at the graded SHA and is no such budget: `python3 -c \"import json;print(sorted({k for v in json.load(open('tests/stress_budgets.json')).values() for k in v}))\"` -> ['ratio', 'rss_attrib_mb', 'rss_peak_mb', 'traced_peak_mb'], memory peaks and a ratio per scenario as the code recorded them, with no CPU budget and no Pi figure (the brief says the ms budget is retired); named as the criterion it would grade D9 against the code's own recording. The brief's six metric definitions name what a budget would be set on. Or leave it unset. For the criterion to reach a finder, the same change makes D9's brief cite the criteria file; without that line the finders run as in round 10.",
+   "term": "No term moves. D9's perfect result stays undecided, not perfect (0018 section 1), and its distance has no enumerator until the criterion is set.",
+   "null_control": "`check_scopes.py --round 11` refuses a criterion that names a path not tracked at the ref, and an unset one with no card; `owner_criteria.D7`, already set to decision 0015, is refused by neither.",
+   "cost": "One path in a code-owned file, and the criteria file itself if none exists.",
+   "finder_critical": "no as the card stands: `git grep -l owner_criteria a39627da59` -> objective.json, decision 0018 and check_scopes.py only, so nothing a finder reads names the criterion file; it becomes yes only where D9's brief cites that file. tvofi ruled on 2026-11-15, preliminary (the coordinator's relay), `All four before finders`, with the group R11-PRE-OWNER-CRITERIA building them",
+   "decision": "accepted",
+   "ruling": "tvofi: \"All four before finders\" (finder-critical by this ruling; made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true,
+   "merged": "367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c"
+  },
+  "E11-K-D10": {
+   "object": "dev/audit/config/objective.json",
+   "criterion": "D10",
+   "proposal": "`owner_criteria.D10` is null: name the tracked file that holds the owner's target tier. The brief quotes the owner: `Adherence to home assistant integration platinum quality requirements`; `custom_components/heatpump_optimizer/quality_scale.yaml` exists at the graded SHA and lists each rule's state, which 0018 says is read once the tier is set. Or leave it unset. For the criterion to reach a finder, the same change makes D10's brief cite the criteria file; without that line the finders run as in round 10.",
+   "term": "No term moves. D10's perfect result stays undecided, not perfect (0018 section 1), and its distance has no enumerator until the criterion is set.",
+   "null_control": "`check_scopes.py --round 11` refuses a criterion that names a path not tracked at the ref, and an unset one with no card; `owner_criteria.D7`, already set to decision 0015, is refused by neither.",
+   "cost": "One path in a code-owned file, and the criteria file itself if none exists.",
+   "finder_critical": "no as the card stands: `git grep -l owner_criteria a39627da59` -> objective.json, decision 0018 and check_scopes.py only, so nothing a finder reads names the criterion file; it becomes yes only where D10's brief cites that file. tvofi ruled on 2026-11-15, preliminary (the coordinator's relay), `All four before finders`, with the group R11-PRE-OWNER-CRITERIA building them",
+   "decision": "accepted",
+   "ruling": "tvofi: \"All four before finders\" (finder-critical by this ruling; made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true,
+   "merged": "367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c"
+  },
+  "E11-S-SEATS": {
+   "object": "dev/audit/config/objective.json",
+   "proposal": "`seats.evaluator_model` and `seats.reviewer_model` are null, and evaluator.md says of the model `unset: ask the owner`. This seat's dispatch brief states that tvofi ruled on 2026-11-15 that the evaluator and its reviewer run on Fable; the file does not hold it. Set both fields, or leave them asked each round.",
+   "term": "No term moves; `check_scopes.py --round` does not read `seats`.",
+   "null_control": "`python3 tools/audit/check_scopes.py --self-test` does not read the two fields; setting them changes no refusal.",
+   "cost": "Two values in a code-owned file.",
+   "finder_critical": "no: it changes nothing a finder seat reads or runs in round 11",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Record Fable for both\" (evaluator and reviewer on claude-fable-5-2; made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": false
+  },
+  "E11-U1": {
+   "paths": [
+    "dev/governance/dimensions/D17.md"
+   ],
+   "paths_note": "the planned brief file of the new dimension (D16 actuator-write, D17 feature-behaviour), by the coordinator's word for the group R11-PRE-NEW-DIMENSIONS, whose queued brief names the directory and not the file; `check_scopes.py` compares exact file names (lines 375, 382, 716), so if the brief lands under another name this path must follow it before the card is recorded merged",
+   "unowned": "R10-HOTFIX-AWAY-SETBACK (pull request 3013), reported by the owner in round 10's window: away with weekend or holiday comfort fields set: a feature against its documented effect.",
+   "proposal": "No brief at the graded SHA owns this defect: `grep -c -i 'arbiter\\|set-point\\|setpoint\\|supply' dev/governance/dimensions/D*.md` -> 0 in all 16, and `grep -l -i 'actuator\\|async_call\\|write site'` over the same files prints nothing. It could instead widen D12 (a configuration with weekend or holiday comfort fields); the attribution to `none` is the evaluator's by hand, and the reviewer attacks it. Card: the feature-behaviour dimension (a feature against its documented effect) owns it once that dimension has a brief; until then 0018 section 1's clause 2 fails for it.",
+   "term": "`unowned` (layer 1): one item of the 7 this evaluation counts by hand in round 10's window, toward 0; `escapes` owned by `none` falls by one when a dimension owns it and that dimension's rises by one.",
+   "null_control": "The other 19 in-window rows of the hand ledger keep their owner; a report assigned to the nearest existing dimension instead would show as that dimension's `escapes` rising with no step named for it (0018 section 5's control for `unowned`).",
+   "cost": "One new brief (two for the pair of dimensions), its three seats per round and a `scopes.json` universe; the brief's wording is the owner's. No figure for round 11 is given here.",
+   "already_ruled": "tvofi, 2026-11-13 (roster group R10-DIMENSIONS-FULL-COVERAGE's brief): every dimension reports a denominator, two dimensions are added (actuator write safety and liveness; feature behaviour against its documented effect). The briefs are owed as drafts `for the owner's wording`; carries 175 and 177 on R11-INTAKE-R10-RESIDUE name the actuator-write draft, and no open carry names the feature-behaviour draft (see card E11-COMMON). This card agrees with the ruling.",
+   "finder_critical": "yes: the item is owned only when a new dimension brief exists and its finder seats run in round 11",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Both (Recommended)\" (both new dimensions, actuator-write and feature-behaviour; made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true
+  },
+  "E11-U2": {
+   "paths": [
+    "dev/governance/dimensions/D16.md"
+   ],
+   "paths_note": "the planned brief file of the new dimension (D16 actuator-write, D17 feature-behaviour), by the coordinator's word for the group R11-PRE-NEW-DIMENSIONS, whose queued brief names the directory and not the file; `check_scopes.py` compares exact file names (lines 375, 382, 716), so if the brief lands under another name this path must follow it before the card is recorded merged",
+   "unowned": "R10-HOTFIX-BOOST-FLOW-CEILING (pull request 3562), reported by the owner in round 10's window: a boost over a step the plan books at partial power: the write against the plan's target.",
+   "proposal": "No brief at the graded SHA owns this defect: `grep -c -i 'arbiter\\|set-point\\|setpoint\\|supply' dev/governance/dimensions/D*.md` -> 0 in all 16, and `grep -l -i 'actuator\\|async_call\\|write site'` over the same files prints nothing. Nearest brief argued out: D6 owns the documents' sentence that boost writes the ceiling, and would find the claim false; the defect is the write on a partial-power step, which no step of D6 or D8 drives. Card: the actuator-write dimension (write safety and liveness; 0018's `operation`: the write, its hold and its release equal the plan's target) owns it once that dimension has a brief; until then 0018 section 1's clause 2 fails for it.",
+   "term": "`unowned` (layer 1): one item of the 7 this evaluation counts by hand in round 10's window, toward 0; `escapes` owned by `none` falls by one when a dimension owns it and that dimension's rises by one.",
+   "null_control": "The other 19 in-window rows of the hand ledger keep their owner; a report assigned to the nearest existing dimension instead would show as that dimension's `escapes` rising with no step named for it (0018 section 5's control for `unowned`).",
+   "cost": "One new brief (two for the pair of dimensions), its three seats per round and a `scopes.json` universe; the brief's wording is the owner's. No figure for round 11 is given here.",
+   "already_ruled": "tvofi, 2026-11-13 (roster group R10-DIMENSIONS-FULL-COVERAGE's brief): every dimension reports a denominator, two dimensions are added (actuator write safety and liveness; feature behaviour against its documented effect). The briefs are owed as drafts `for the owner's wording`; carries 175 and 177 on R11-INTAKE-R10-RESIDUE name the actuator-write draft, and no open carry names the feature-behaviour draft (see card E11-COMMON). This card agrees with the ruling.",
+   "finder_critical": "yes: the item is owned only when a new dimension brief exists and its finder seats run in round 11",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Both (Recommended)\" (both new dimensions, actuator-write and feature-behaviour; made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true
+  },
+  "E11-U4": {
+   "paths": [
+    "dev/governance/dimensions/D16.md"
+   ],
+   "paths_note": "the planned brief file of the new dimension (D16 actuator-write, D17 feature-behaviour), by the coordinator's word for the group R11-PRE-NEW-DIMENSIONS, whose queued brief names the directory and not the file; `check_scopes.py` compares exact file names (lines 375, 382, 716), so if the brief lands under another name this path must follow it before the card is recorded merged",
+   "unowned": "R10-OUTSIDE-DISINFECTION-SETPOINT (pull request 3452), reported by the outside in round 10's window: the hot-water write on a disinfection step: the guard records attempts and no completion.",
+   "proposal": "No brief at the graded SHA owns this defect: `grep -c -i 'arbiter\\|set-point\\|setpoint\\|supply' dev/governance/dimensions/D*.md` -> 0 in all 16, and `grep -l -i 'actuator\\|async_call\\|write site'` over the same files prints nothing. Nearest brief argued out: D1 hunts wedges, leaks, races and stale data; here every cycle completes and the guard records an attempt, the written value is simply below the cycle's target. Card: the actuator-write dimension (write safety and liveness; 0018's `operation`: the write, its hold and its release equal the plan's target) owns it once that dimension has a brief; until then 0018 section 1's clause 2 fails for it.",
+   "term": "`unowned` (layer 1): one item of the 7 this evaluation counts by hand in round 10's window, toward 0; `escapes` owned by `none` falls by one when a dimension owns it and that dimension's rises by one.",
+   "null_control": "The other 19 in-window rows of the hand ledger keep their owner; a report assigned to the nearest existing dimension instead would show as that dimension's `escapes` rising with no step named for it (0018 section 5's control for `unowned`).",
+   "cost": "One new brief (two for the pair of dimensions), its three seats per round and a `scopes.json` universe; the brief's wording is the owner's. No figure for round 11 is given here.",
+   "already_ruled": "tvofi, 2026-11-13 (roster group R10-DIMENSIONS-FULL-COVERAGE's brief): every dimension reports a denominator, two dimensions are added (actuator write safety and liveness; feature behaviour against its documented effect). The briefs are owed as drafts `for the owner's wording`; carries 175 and 177 on R11-INTAKE-R10-RESIDUE name the actuator-write draft, and no open carry names the feature-behaviour draft (see card E11-COMMON). This card agrees with the ruling.",
+   "finder_critical": "yes: the item is owned only when a new dimension brief exists and its finder seats run in round 11",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Both (Recommended)\" (both new dimensions, actuator-write and feature-behaviour; made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true
+  },
+  "E11-U5": {
+   "paths": [
+    "dev/governance/dimensions/D16.md"
+   ],
+   "paths_note": "the planned brief file of the new dimension (D16 actuator-write, D17 feature-behaviour), by the coordinator's word for the group R11-PRE-NEW-DIMENSIONS, whose queued brief names the directory and not the file; `check_scopes.py` compares exact file names (lines 375, 382, 716), so if the brief lands under another name this path must follow it before the card is recorded merged",
+   "unowned": "R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE (pull request 3512): a re-solve landing minutes after the supply switched: no minimum run or pause. The intake triage built it as a need, so it is no escape and is not among the unowned items this evaluation counts; the card stands as an argument for the actuator-write dimension with no escape behind it.",
+   "proposal": "No brief at the graded SHA owns this item: `grep -c -i 'arbiter\\|set-point\\|setpoint\\|supply' dev/governance/dimensions/D*.md` -> 0 in all 16, and `grep -l -i 'actuator\\|async_call\\|write site'` over the same files prints nothing. Nearest brief argued out: D1's steps drive lifecycle, stores, staleness and guards; a minimum run and pause on a supply switch is a rule on the write that no D1 step names. Card: the actuator-write dimension (write safety and liveness; 0018's `operation`: the write, its hold and its release equal the plan's target) owns it once that dimension has a brief; until then 0018 section 1's clause 2 fails for it.",
+   "term": "No term moves by this item: it is none of the 7 unowned items this evaluation counts by hand. It bears on `operation`'s unknown distance (0018 section 1), which the actuator-write dimension's cell ledger would read.",
+   "null_control": "The other 19 in-window rows of the hand ledger keep their owner; a report assigned to the nearest existing dimension instead would show as that dimension's `escapes` rising with no step named for it (0018 section 5's control for `unowned`).",
+   "cost": "One new brief (two for the pair of dimensions), its three seats per round and a `scopes.json` universe; the brief's wording is the owner's. No figure for round 11 is given here.",
+   "already_ruled": "tvofi, 2026-11-13 (roster group R10-DIMENSIONS-FULL-COVERAGE's brief): every dimension reports a denominator, two dimensions are added (actuator write safety and liveness; feature behaviour against its documented effect). The briefs are owed as drafts `for the owner's wording`; carries 175 and 177 on R11-INTAKE-R10-RESIDUE name the actuator-write draft, and no open carry names the feature-behaviour draft (see card E11-COMMON). This card agrees with the ruling.",
+   "finder_critical": "yes: the item is owned only when a new dimension brief exists and its finder seats run in round 11",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Both (Recommended)\" (both new dimensions, actuator-write and feature-behaviour; made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true
+  },
+  "E11-U6": {
+   "paths": [
+    "dev/governance/dimensions/D16.md"
+   ],
+   "paths_note": "the planned brief file of the new dimension (D16 actuator-write, D17 feature-behaviour), by the coordinator's word for the group R11-PRE-NEW-DIMENSIONS, whose queued brief names the directory and not the file; `check_scopes.py` compares exact file names (lines 375, 382, 716), so if the brief lands under another name this path must follow it before the card is recorded merged",
+   "unowned": "R10-OUTSIDE-SUPPLY-STALE-STEP (pull request 3478), reported by the outside in round 10's window: a cycle whose write lands in the step after the one its action was cut for.",
+   "proposal": "No brief at the graded SHA owns this defect: `grep -c -i 'arbiter\\|set-point\\|setpoint\\|supply' dev/governance/dimensions/D*.md` -> 0 in all 16, and `grep -l -i 'actuator\\|async_call\\|write site'` over the same files prints nothing. Nearest brief argued out: D1's step 3 checks stale inputs and `the published and booked value`; here the inputs are fresh and the command written is one plan step old, which is the write against the plan and in no D1 step. Card: the actuator-write dimension (write safety and liveness; 0018's `operation`: the write, its hold and its release equal the plan's target) owns it once that dimension has a brief; until then 0018 section 1's clause 2 fails for it.",
+   "term": "`unowned` (layer 1): one item of the 7 this evaluation counts by hand in round 10's window, toward 0; `escapes` owned by `none` falls by one when a dimension owns it and that dimension's rises by one.",
+   "null_control": "The other 19 in-window rows of the hand ledger keep their owner; a report assigned to the nearest existing dimension instead would show as that dimension's `escapes` rising with no step named for it (0018 section 5's control for `unowned`).",
+   "cost": "One new brief (two for the pair of dimensions), its three seats per round and a `scopes.json` universe; the brief's wording is the owner's. No figure for round 11 is given here.",
+   "already_ruled": "tvofi, 2026-11-13 (roster group R10-DIMENSIONS-FULL-COVERAGE's brief): every dimension reports a denominator, two dimensions are added (actuator write safety and liveness; feature behaviour against its documented effect). The briefs are owed as drafts `for the owner's wording`; carries 175 and 177 on R11-INTAKE-R10-RESIDUE name the actuator-write draft, and no open carry names the feature-behaviour draft (see card E11-COMMON). This card agrees with the ruling.",
+   "finder_critical": "yes: the item is owned only when a new dimension brief exists and its finder seats run in round 11",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Both (Recommended)\" (both new dimensions, actuator-write and feature-behaviour; made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true
+  },
+  "E11-U7": {
+   "paths": [
+    "dev/governance/dimensions/D16.md"
+   ],
+   "paths_note": "the planned brief file of the new dimension (D16 actuator-write, D17 feature-behaviour), by the coordinator's word for the group R11-PRE-NEW-DIMENSIONS, whose queued brief names the directory and not the file; `check_scopes.py` compares exact file names (lines 375, 382, 716), so if the brief lands under another name this path must follow it before the card is recorded merged",
+   "unowned": "R10-WATER-SETPOINT-FEEDBACK (pull request 3405), reported by the outside in round 10's window: a water set-point on a controller with an integrating speed loop: measured power against plan.",
+   "proposal": "No brief at the graded SHA owns this defect: `grep -c -i 'arbiter\\|set-point\\|setpoint\\|supply' dev/governance/dimensions/D*.md` -> 0 in all 16, and `grep -l -i 'actuator\\|async_call\\|write site'` over the same files prints nothing. Nearest brief argued out: D2 lists identities of the thermal model, COP, objective, tariff and estimators and none over a written set-point against measured power. Card: the actuator-write dimension (write safety and liveness; 0018's `operation`: the write, its hold and its release equal the plan's target) owns it once that dimension has a brief; until then 0018 section 1's clause 2 fails for it.",
+   "term": "`unowned` (layer 1): one item of the 7 this evaluation counts by hand in round 10's window, toward 0; `escapes` owned by `none` falls by one when a dimension owns it and that dimension's rises by one.",
+   "null_control": "The other 19 in-window rows of the hand ledger keep their owner; a report assigned to the nearest existing dimension instead would show as that dimension's `escapes` rising with no step named for it (0018 section 5's control for `unowned`).",
+   "cost": "One new brief (two for the pair of dimensions), its three seats per round and a `scopes.json` universe; the brief's wording is the owner's. No figure for round 11 is given here.",
+   "already_ruled": "tvofi, 2026-11-13 (roster group R10-DIMENSIONS-FULL-COVERAGE's brief): every dimension reports a denominator, two dimensions are added (actuator write safety and liveness; feature behaviour against its documented effect). The briefs are owed as drafts `for the owner's wording`; carries 175 and 177 on R11-INTAKE-R10-RESIDUE name the actuator-write draft, and no open carry names the feature-behaviour draft (see card E11-COMMON). This card agrees with the ruling.",
+   "finder_critical": "yes: the item is owned only when a new dimension brief exists and its finder seats run in round 11",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Both (Recommended)\" (both new dimensions, actuator-write and feature-behaviour; made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true
+  },
+  "E11-U8": {
+   "paths": [
+    "dev/governance/dimensions/D16.md"
+   ],
+   "paths_note": "the planned brief file of the new dimension (D16 actuator-write, D17 feature-behaviour), by the coordinator's word for the group R11-PRE-NEW-DIMENSIONS, whose queued brief names the directory and not the file; `check_scopes.py` compares exact file names (lines 375, 382, 716), so if the brief lands under another name this path must follow it before the card is recorded merged",
+   "unowned": "R10-MODE-BEFORE-SUPPLY-ON (pull request 3530), reported by the outside in round 10's window: the order of the mode write and the supply switch-on.",
+   "proposal": "No brief at the graded SHA owns this defect: `grep -c -i 'arbiter\\|set-point\\|setpoint\\|supply' dev/governance/dimensions/D*.md` -> 0 in all 16, and `grep -l -i 'actuator\\|async_call\\|write site'` over the same files prints nothing. Nearest brief argued out: D1's step 4 lists races between the solve thread and loop-side writers; the order of two service calls in one pass is no such race. Card: the actuator-write dimension (write safety and liveness; 0018's `operation`: the write, its hold and its release equal the plan's target) owns it once that dimension has a brief; until then 0018 section 1's clause 2 fails for it.",
+   "term": "`unowned` (layer 1): one item of the 7 this evaluation counts by hand in round 10's window, toward 0; `escapes` owned by `none` falls by one when a dimension owns it and that dimension's rises by one.",
+   "null_control": "The other 19 in-window rows of the hand ledger keep their owner; a report assigned to the nearest existing dimension instead would show as that dimension's `escapes` rising with no step named for it (0018 section 5's control for `unowned`).",
+   "cost": "One new brief (two for the pair of dimensions), its three seats per round and a `scopes.json` universe; the brief's wording is the owner's. No figure for round 11 is given here.",
+   "already_ruled": "tvofi, 2026-11-13 (roster group R10-DIMENSIONS-FULL-COVERAGE's brief): every dimension reports a denominator, two dimensions are added (actuator write safety and liveness; feature behaviour against its documented effect). The briefs are owed as drafts `for the owner's wording`; carries 175 and 177 on R11-INTAKE-R10-RESIDUE name the actuator-write draft, and no open carry names the feature-behaviour draft (see card E11-COMMON). This card agrees with the ruling.",
+   "finder_critical": "yes: the item is owned only when a new dimension brief exists and its finder seats run in round 11",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Both (Recommended)\" (both new dimensions, actuator-write and feature-behaviour; made final by \"Final as given (Recommended)\"). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true
+  },
+  "E11-U9": {
+   "paths": [
+    "dev/governance/dimensions/D16.md"
+   ],
+   "paths_note": "the planned brief file of the new dimension (D16 actuator-write, D17 feature-behaviour), by the coordinator's word for the group R11-PRE-NEW-DIMENSIONS, whose queued brief names the directory and not the file; `check_scopes.py` compares exact file names (lines 375, 382, 716), so if the brief lands under another name this path must follow it before the card is recorded merged",
+   "unowned": "R10-SETPOINT-BOOST, reported by the owner in round 10's window: a heating step at minimum power on a tank at or below 20 C: the write equals the do-not-heat value; its second cause, the draw range learning from censored samples, is an estimator defect in D2 step 5's territory and is listed in card E11-D2.",
+   "proposal": "No brief at the graded SHA owns this defect: `grep -c -i 'arbiter\\|set-point\\|setpoint\\|supply' dev/governance/dimensions/D*.md` -> 0 in all 16, and `grep -l -i 'actuator\\|async_call\\|write site'` over the same files prints nothing. Nearest brief argued out for this cause: D2's step 1 asks that no store cross a physical bound and lists no identity over the set-point a heating step writes; the defect is a written value equal to the do-not-heat value. The group's second cause, the draw range learning from censored samples, is an estimator defect in D2 step 5's territory and is carried by card E11-D2, not here. Card: the actuator-write dimension (write safety and liveness; 0018's `operation`: the write, its hold and its release equal the plan's target) owns it once that dimension has a brief; until then 0018 section 1's clause 2 fails for it.",
+   "term": "`unowned` (layer 1): one item of the 7 this evaluation counts by hand in round 10's window, toward 0; `escapes` owned by `none` falls by one when a dimension owns it and that dimension's rises by one.",
+   "null_control": "The other 19 in-window rows of the hand ledger keep their owner; a report assigned to the nearest existing dimension instead would show as that dimension's `escapes` rising with no step named for it (0018 section 5's control for `unowned`).",
+   "cost": "One new brief (two for the pair of dimensions), its three seats per round and a `scopes.json` universe; the brief's wording is the owner's. No figure for round 11 is given here.",
+   "already_ruled": "tvofi, 2026-11-13 (roster group R10-DIMENSIONS-FULL-COVERAGE's brief): every dimension reports a denominator, two dimensions are added (actuator write safety and liveness; feature behaviour against its documented effect). The briefs are owed as drafts `for the owner's wording`; carries 175 and 177 on R11-INTAKE-R10-RESIDUE name the actuator-write draft, and no open carry names the feature-behaviour draft (see card E11-COMMON). This card agrees with the ruling.",
+   "finder_critical": "yes: the item is owned only when a new dimension brief exists and its finder seats run in round 11",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Accept all four (Recommended)\" (cards E11-D9, E11-U9, E11-U10, E11-GATE-REDS). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true
+  },
+  "E11-U10": {
+   "paths": [
+    "dev/governance/dimensions/D16.md"
+   ],
+   "paths_note": "the planned brief file of the new dimension (D16 actuator-write, D17 feature-behaviour), by the coordinator's word for the group R11-PRE-NEW-DIMENSIONS, whose queued brief names the directory and not the file; `check_scopes.py` compares exact file names (lines 375, 382, 716), so if the brief lands under another name this path must follow it before the card is recorded merged",
+   "unowned": "R10-OUTSIDE-DHW-START-HYSTERESIS (pull request 3531): a pump whose tank thermostat starts a charge only below its set-point less a hysteresis: planned hot-water runs the pump will not start. The intake triage built it as a gap, so it is no escape and is not among the unowned items this evaluation counts; the card stands as an argument for the actuator-write dimension with no escape behind it.",
+   "proposal": "No brief at the graded SHA owns this item: `grep -c -i 'arbiter\\|set-point\\|setpoint\\|supply' dev/governance/dimensions/D*.md` -> 0 in all 16, and `grep -l -i 'actuator\\|async_call\\|write site'` over the same files prints nothing. Nearest brief argued out: D0 races plans on the same objective and inputs and D12 asks that setup completes and a plan publishes; neither drives a planned run against whether the pump will start it, which is the plan against its execution. Card: the actuator-write dimension (write safety and liveness; 0018's `operation`: the write, its hold and its release equal the plan's target) owns it once that dimension has a brief; until then 0018 section 1's clause 2 fails for it.",
+   "term": "No term moves by this item: it is none of the 7 unowned items this evaluation counts by hand. It bears on `operation`'s unknown distance (0018 section 1), which the actuator-write dimension's cell ledger would read.",
+   "null_control": "The other 19 in-window rows of the hand ledger keep their owner; a report assigned to the nearest existing dimension instead would show as that dimension's `escapes` rising with no step named for it (0018 section 5's control for `unowned`).",
+   "cost": "One new brief (two for the pair of dimensions), its three seats per round and a `scopes.json` universe; the brief's wording is the owner's. No figure for round 11 is given here.",
+   "already_ruled": "tvofi, 2026-11-13 (roster group R10-DIMENSIONS-FULL-COVERAGE's brief): every dimension reports a denominator, two dimensions are added (actuator write safety and liveness; feature behaviour against its documented effect). The briefs are owed as drafts `for the owner's wording`; carries 175 and 177 on R11-INTAKE-R10-RESIDUE name the actuator-write draft, and no open carry names the feature-behaviour draft (see card E11-COMMON). This card agrees with the ruling.",
+   "finder_critical": "yes: the item is owned only when a new dimension brief exists and its finder seats run in round 11",
+   "decision": "accepted",
+   "ruling": "tvofi: \"Accept all four (Recommended)\" (cards E11-D9, E11-U9, E11-U10, E11-GATE-REDS). Given: tvofi, 2026-11-15, decision card (AskUserQuestion) in the round-11 orchestrator session, logged verbatim in the orchestrator sweep record.",
+   "gates_finders": true
+  }
+ },
+ "revision_3": {
+  "of": "ca3f872430d0f2863ac7bb7c3d4304fda538f7a5",
+  "why": "The fix review of pull request 3611 (round 10's objective record) measured three figures of this evaluation; each was re-measured here. No object verdict moves and no `decision` or `ruling` field is touched.",
+  "figures": {
+   "production merges in the window": {
+    "before": "162 (`machinery_ratchet.py --measure --window 1210`: the flag counts merges and 1210 is the window's first-parent commit count, so it reached 71 merges into round 9)",
+    "after": "155 (`python3 tools/audit/machinery_ratchet.py --measure --repo . --head 13cbe48de4 --window 1139`; `git log --first-parent --merges --oneline v7.0.0..v10.0.0 | wc -l` -> 1139)"
+   },
+   "injected per 100 production merges": {
+    "before": "2.47 (4 over 162)",
+    "after": "2.58 (4 over 155)"
+   },
+   "escapes in the window, by hand": {
+    "before": "31",
+    "after": "26: an escape is a report from an install. R10-BUFFER-STORE, R10-LEARNED-STORE-LOAD and R10-COP-GATE-E were found by programme seats (the ledger's header already ruled the fixer-found R10-TWO-ZONE-HHL out on that ground); R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE and R10-OUTSIDE-DHW-START-HYSTERESIS were triaged a need and a gap. The evaluator agrees with all five after reading the roster rows."
+   },
+   "escapes per owner": {
+    "before": "D0 2, D1 6, D2 6, none 9",
+    "after": "D0 1, D1 5, D2 5, none 7; the others unchanged"
+   },
+   "unowned": {
+    "before": "9",
+    "after": "7; cards E11-U5 and E11-U10 stand as arguments for the actuator-write dimension with no escape behind them"
+   },
+   "rows dated the stamp's own day": {
+    "before": "8",
+    "after": "6: R10-UX-SETUP and R10-SAV-ACTUATION conceded to round 10's objective record (a redesign; a feature). Counted in no verdict."
+   },
+   "R10-MIN-POWER-FLOOR's owner": {
+    "before": "D8",
+    "after": "D8, kept against the record's D2: the reported symptom is a sensor's attribute (a merged slot's average power below the minimum), which is D8 step 2's check of a published value, and the brief leaves open whether the solver is at fault. It moves no term."
+   },
+   "in-window escapes with a tracked root-cause record": {
+    "before": "3",
+    "after": "2 (R10-BUFFER-STORE is no longer a row in the window)"
+   }
+  },
+  "proposal_wording": "By tvofi's ruling `Fix the wording (Recommended)`, as the coordinator relayed it: `escapes` becomes `escapes and seat-found defects` in cards E11-D0, E11-D1 and E11-D2, and `this defect` becomes `this item` in cards E11-U5 and E11-U10. Nothing else in a proposal changed.",
+  "ledger": "dev/audit/rounds/round11/evaluation/escapes_hand.tsv: seven rows move to `out` with the reason (the five above and the two stamp-day rows), and the header gains the line that an escape is a report from an install.",
+  "changes": {
+   "terms.operation.lead": {
+    "before": "candidate write sites at the graded SHA; 7 of the 9 unowned items of the hand ledger are defects",
+    "after": "candidate write sites at the graded SHA; 6 of the 7 unowned items of the hand ledger are defects"
+   },
+   "terms.generality.lead": {
+    "before": "the owner's install could not have shown: 13 of the 31 in-window rows of the hand ledger were reported",
+    "after": "the owner's install could not have shown: 11 of the 26 in-window rows of the hand ledger were reported"
+   },
+   "terms.unowned.by_hand.value": {
+    "before": "9",
+    "after": "7"
+   },
+   "terms.escapes.by_hand.in_window": {
+    "before": "31",
+    "after": "26"
+   },
+   "terms.escapes.by_hand.dated_the_stamp_day": {
+    "before": "8",
+    "after": "6"
+   },
+   "terms.escapes.by_hand.per_owner.D0": {
+    "before": "2",
+    "after": "1"
+   },
+   "terms.escapes.by_hand.per_owner.D1": {
+    "before": "6",
+    "after": "5"
+   },
+   "terms.escapes.by_hand.per_owner.D2": {
+    "before": "6",
+    "after": "5"
+   },
+   "terms.escapes.by_hand.per_owner.none": {
+    "before": "9",
+    "after": "7"
+   },
+   "terms.escapes.by_hand.reporters.outside": {
+    "before": "13",
+    "after": "11"
+   },
+   "terms.escapes.by_hand.reporters.fixer": {
+    "before": "3",
+    "after": "0"
+   },
+   "terms.escapes.by_hand.ruled_out": {
+    "before": "36",
+    "after": "43"
+   },
+   "terms.injected.by_hand.production_merges_in_window": {
+    "before": "162",
+    "after": "155"
+   },
+   "terms.injected.by_hand.per_100": {
+    "before": "2.47",
+    "after": "2.58"
+   },
+   "terms.injected.by_hand.denominator_command": {
+    "before": "--measure --repo . --head 13cbe48de4 --window 1210",
+    "after": "--measure --repo . --head 13cbe48de4 --window 1139"
+   },
+   "terms.unexamined.lead": {
+    "before": "after the window opened); the window holds 162 production merges by `machinery_ratchet.py`'s",
+    "after": "after the window opened); the window holds 155 production merges by `machinery_ratchet.py`'s"
+   },
+   "terms.tokens_per_change.beside": {
+    "before": "--measure --repo . --head 13cbe48de4 --window 1210` -> the window's 1210 merges: production 162, machinery 565, record 483; churn 15156 nonproduct lines per 1000 product lines",
+    "after": "--measure --repo . --head 13cbe48de4 --window 1139` -> the window's 1139 merges: production 155, machinery 516, record 468; churn 15167 nonproduct lines per 1000 product lines"
+   },
+   "objects[dev/governance/dimensions/D0.md].evidence": {
+    "before": "(the by-hand read 0018 section 3 allows): 2 escape(s) in the window in this brief's territory (R10-SETPOINT-POWER, R10-BUFFER-STORE). In the brief: step 4 names the grid in",
+    "after": "(the by-hand read 0018 section 3 allows): 1 escape(s) in the window in this brief's territory (R10-SETPOINT-POWER). In the brief: step 4 names the grid in"
+   },
+   "objects[dev/governance/dimensions/D1.md].evidence": {
+    "before": "(the by-hand read 0018 section 3 allows): 6 escape(s) in the window in this brief's territory (R10-HOTFIX-AWAY-LIVE, R10-HOTFIX-AWAY-PRESENCE, R10-OUTSIDE-PRICE-OUTAGE-LAST-VALID, R10-INPUT-REAPPEAR, R10-LEARNED-STORE-LOAD, R10-HOTFIX-FLOW-SETPOINT-STUCK). In the",
+    "after": "(the by-hand read 0018 section 3 allows): 5 escape(s) in the window in this brief's territory (R10-HOTFIX-AWAY-LIVE, R10-HOTFIX-AWAY-PRESENCE, R10-OUTSIDE-PRICE-OUTAGE-LAST-VALID, R10-INPUT-REAPPEAR, R10-HOTFIX-FLOW-SETPOINT-STUCK). In the"
+   },
+   "objects[dev/governance/dimensions/D2.md].evidence": {
+    "before": "(the by-hand read 0018 section 3 allows): 6 escape(s) in the window in this brief's territory (R10-HOTFIX-SAV-ESTIMATE, R10-HOTFIX-LEARNER-INPUTS, R10-OUTSIDE-DHW-CHARGE-SETTLE, R10-SAVINGS-NEGATIVE, R10-DEMAND-OVERBOOK, R10-COP-GATE-E), 2 more dated the stamp's own day. In the",
+    "after": "(the by-hand read 0018 section 3 allows): 5 escape(s) in the window in this brief's territory (R10-HOTFIX-SAV-ESTIMATE, R10-HOTFIX-LEARNER-INPUTS, R10-OUTSIDE-DHW-CHARGE-SETTLE, R10-SAVINGS-NEGATIVE, R10-DEMAND-OVERBOOK), 2 more dated the stamp's own day. In the"
+   },
+   "objects[dev/governance/dimensions/D4.md].evidence": {
+    "before": "(R10-HOTFIX-CARD-HEALTH-TEXT, R10-OUTSIDE-VALVE-TARGET-LABEL), 3 more dated the stamp's own day. In the brief:",
+    "after": "(R10-HOTFIX-CARD-HEALTH-TEXT, R10-OUTSIDE-VALVE-TARGET-LABEL), 2 more dated the stamp's own day. In the brief:"
+   },
+   "objects[dev/governance/roles/root-cause.md].evidence": {
+    "before": "section 3 allows) line RCA_TRACKED: of the 31 in-window escapes of the hand ledger, a root-cause record is tracked for 3 (SAV-ESTIMATE, COP-UNMEASURED, BUFFER-STORE); a fourth, R10-RCA-SETPOINT-LATCH-DEADLOCK.md for",
+    "after": "section 3 allows) line RCA_TRACKED: of the 26 in-window escapes of the hand ledger, a root-cause record is tracked for 2 (SAV-ESTIMATE, COP-UNMEASURED); another, R10-RCA-SETPOINT-LATCH-DEADLOCK.md for"
+   },
+   "objects[dev/governance/rules/defect-root-cause.md].evidence": {
+    "before": "E11-N-RULE-YIELD). Lead, not a score: the hand ledger's 31 in-window escapes each meet this rule's first trigger (a defect that reached a release); a root-cause record is tracked for 3 of them and a fourth sits off main (see root-cause.md's row).",
+    "after": "E11-N-RULE-YIELD). Lead, not a score: the hand ledger's 26 in-window escapes each meet this rule's first trigger (a defect that reached a release); a root-cause record is tracked for 2 of them and another sits off main (see root-cause.md's row)."
+   },
+   "cards.E11-D0.proposal": {
+    "before": "add to step 4 the cells the two escapes show it did not drive (an install whose pump",
+    "after": "add to step 4 the cells the two escapes and seat-found defects show it did not drive (an install whose pump"
+   },
+   "cards.E11-D0.term": {
+    "before": "`escapes` owned by D0: 2 in round 10's window by the hand read, toward",
+    "after": "`escapes` owned by D0: 1 in round 10's window by the hand read, toward"
+   },
+   "cards.E11-D1.proposal": {
+    "before": "and add to step 3 the inputs the escapes show it did not drive: a presence entity",
+    "after": "and add to step 3 the inputs the escapes and seat-found defects show it did not drive: a presence entity"
+   },
+   "cards.E11-D1.term": {
+    "before": "`escapes` owned by D1: 6 in round 10's window by the hand read, toward",
+    "after": "`escapes` owned by D1: 5 in round 10's window by the hand read, toward"
+   },
+   "cards.E11-D2.proposal": {
+    "before": "command's output, and add the inputs the escapes show steps 3 and 5 did not drive: the savings",
+    "after": "command's output, and add the inputs the escapes and seat-found defects show steps 3 and 5 did not drive: the savings"
+   },
+   "cards.E11-D2.term": {
+    "before": "`escapes` owned by D2: 6 in round 10's window by the hand read, toward",
+    "after": "`escapes` owned by D2: 5 in round 10's window by the hand read, toward"
+   },
+   "cards.E11-INJECTED.term": {
+    "before": "3 of them by a root-cause record, over 162 production merges of the window by 0018's own class (`python3 tools/audit/machinery_ratchet.py --measure --repo . --head 13cbe48de4 --window 1210` -> production 162): 2.47 per 100, toward 0. A proxy while no enumerator",
+    "after": "3 of them by a root-cause record, over 155 production merges of the window by 0018's own class (`python3 tools/audit/machinery_ratchet.py --measure --repo . --head 13cbe48de4 --window 1139` -> production 155; the window holds 1139 merges on the first-parent chain): 2.58 per 100, toward 0. A proxy while no enumerator"
+   },
+   "cards.E11-INJECTED.null_control": {
+    "before": "ledger's in-window rows with no cause named (28 of 31) do not move either.",
+    "after": "ledger's in-window rows with no cause named (23 of 26) do not move either."
+   },
+   "cards.E11-U1.term": {
+    "before": "`unowned` (layer 1): one item of the 9 this evaluation counts by hand in round",
+    "after": "`unowned` (layer 1): one item of the 7 this evaluation counts by hand in round"
+   },
+   "cards.E11-U1.null_control": {
+    "before": "The other 22 in-window rows of the hand ledger keep their",
+    "after": "The other 19 in-window rows of the hand ledger keep their"
+   },
+   "cards.E11-U2.term": {
+    "before": "`unowned` (layer 1): one item of the 9 this evaluation counts by hand in round",
+    "after": "`unowned` (layer 1): one item of the 7 this evaluation counts by hand in round"
+   },
+   "cards.E11-U2.null_control": {
+    "before": "The other 22 in-window rows of the hand ledger keep their",
+    "after": "The other 19 in-window rows of the hand ledger keep their"
+   },
+   "cards.E11-U4.term": {
+    "before": "`unowned` (layer 1): one item of the 9 this evaluation counts by hand in round",
+    "after": "`unowned` (layer 1): one item of the 7 this evaluation counts by hand in round"
+   },
+   "cards.E11-U4.null_control": {
+    "before": "The other 22 in-window rows of the hand ledger keep their",
+    "after": "The other 19 in-window rows of the hand ledger keep their"
+   },
+   "cards.E11-U6.term": {
+    "before": "`unowned` (layer 1): one item of the 9 this evaluation counts by hand in round",
+    "after": "`unowned` (layer 1): one item of the 7 this evaluation counts by hand in round"
+   },
+   "cards.E11-U6.null_control": {
+    "before": "The other 22 in-window rows of the hand ledger keep their",
+    "after": "The other 19 in-window rows of the hand ledger keep their"
+   },
+   "cards.E11-U7.term": {
+    "before": "`unowned` (layer 1): one item of the 9 this evaluation counts by hand in round",
+    "after": "`unowned` (layer 1): one item of the 7 this evaluation counts by hand in round"
+   },
+   "cards.E11-U7.null_control": {
+    "before": "The other 22 in-window rows of the hand ledger keep their",
+    "after": "The other 19 in-window rows of the hand ledger keep their"
+   },
+   "cards.E11-U8.term": {
+    "before": "`unowned` (layer 1): one item of the 9 this evaluation counts by hand in round",
+    "after": "`unowned` (layer 1): one item of the 7 this evaluation counts by hand in round"
+   },
+   "cards.E11-U8.null_control": {
+    "before": "The other 22 in-window rows of the hand ledger keep their",
+    "after": "The other 19 in-window rows of the hand ledger keep their"
+   },
+   "cards.E11-U9.term": {
+    "before": "`unowned` (layer 1): one item of the 9 this evaluation counts by hand in round",
+    "after": "`unowned` (layer 1): one item of the 7 this evaluation counts by hand in round"
+   },
+   "cards.E11-U9.null_control": {
+    "before": "The other 22 in-window rows of the hand ledger keep their",
+    "after": "The other 19 in-window rows of the hand ledger keep their"
+   },
+   "cards.E11-U5.unowned": {
+    "before": "R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE (pull request 3512), reported by the outside in round 10's window: a re-solve landing minutes after the supply switched: no minimum run or pause.",
+    "after": "R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE (pull request 3512): a re-solve landing minutes after the supply switched: no minimum run or pause. The intake triage built it as a need, so it is no escape and is not among the unowned items this evaluation counts; the card stands as an argument for the actuator-write dimension with no escape behind it."
+   },
+   "cards.E11-U5.proposal": {
+    "before": "No brief at the graded SHA owns this defect: `grep -c -i 'arbiter\\|set-point\\|setpoint\\|supply'",
+    "after": "No brief at the graded SHA owns this item: `grep -c -i 'arbiter\\|set-point\\|setpoint\\|supply'"
+   },
+   "cards.E11-U5.term": {
+    "before": "`unowned` (layer 1): one item of the 9 this evaluation counts by hand in round 10's window, toward 0; `escapes` owned by `none` falls by one when a dimension owns it and that dimension's rises by one.",
+    "after": "No term moves by this item: it is none of the 7 unowned items this evaluation counts by hand. It bears on `operation`'s unknown distance (0018 section 1), which the actuator-write dimension's cell ledger would read."
+   },
+   "cards.E11-U5.null_control": {
+    "before": "The other 22 in-window rows of the hand ledger keep their",
+    "after": "The other 19 in-window rows of the hand ledger keep their"
+   },
+   "cards.E11-U10.unowned": {
+    "before": "R10-OUTSIDE-DHW-START-HYSTERESIS (pull request 3531), reported by the outside in round 10's window: a pump whose tank thermostat starts a charge only below its set-point less a hysteresis: 54 of 114 planned hot-water runs the pump will not start, booked as the pump's disobedience.",
+    "after": "R10-OUTSIDE-DHW-START-HYSTERESIS (pull request 3531): a pump whose tank thermostat starts a charge only below its set-point less a hysteresis: planned hot-water runs the pump will not start. The intake triage built it as a gap, so it is no escape and is not among the unowned items this evaluation counts; the card stands as an argument for the actuator-write dimension with no escape behind it."
+   },
+   "cards.E11-U10.proposal": {
+    "before": "No brief at the graded SHA owns this defect: `grep -c -i 'arbiter\\|set-point\\|setpoint\\|supply'",
+    "after": "No brief at the graded SHA owns this item: `grep -c -i 'arbiter\\|set-point\\|setpoint\\|supply'"
+   },
+   "cards.E11-U10.term": {
+    "before": "`unowned` (layer 1): one item of the 9 this evaluation counts by hand in round 10's window, toward 0; `escapes` owned by `none` falls by one when a dimension owns it and that dimension's rises by one.",
+    "after": "No term moves by this item: it is none of the 7 unowned items this evaluation counts by hand. It bears on `operation`'s unknown distance (0018 section 1), which the actuator-write dimension's cell ledger would read."
+   },
+   "cards.E11-U10.null_control": {
+    "before": "The other 22 in-window rows of the hand ledger keep their",
+    "after": "The other 19 in-window rows of the hand ledger keep their"
+   },
+   "not_followed.5.why": {
+    "before": "rule selects at the pinned roster commit, 31 as escapes and 36 ruled out with the reason. The roster records",
+    "after": "rule selects at the pinned roster commit, 26 as escapes and 43 ruled out with the reason. The roster records"
+   }
+  }
+ },
+ "revision_4": {
+  "of": "c6ce415b7711d76cf6c08f926f30da91f7bda924",
+  "by": "r11-evaluator (Opus 5.5; the owner set the evaluator model to opus, tvofi 2026-11-16)",
+  "why": "`python3 -I tools/audit/check_scopes.py --repo . --ref <origin/main 030a4d377f merged with c6ce415b77> --round 11` printed 41 gaps; this revision answers those that are the evaluation's own. No existing verdict, `decision`, `ruling` or `gates_finders` moves.",
+  "changes": {
+   "objects.dev/governance/roles/nudge.md": "row dropped (was `keep`, NO-READ): main retired the file in 1ed1329e41, so objective.json's globs no longer match it.",
+   "objects.tools/audit/seat/instruments/{enumerate,finder_overlap,plant_recall,round_metrics}.py.md": "four rows added, each `keep` on a NO-READ yield with its cost read; they landed after the graded SHA. objective.json's globs at 030a4d377f match no other unrowed object (check_scopes.py names only these four).",
+   "cards.*.merged": "17 accepted cards carry `merged`: E11-COMMON b94425b94f; E11-D0, D1, D2, D8, D9, D12, D15 f1520e3539; E11-D3, D4, D5, D6, D7, D10, D14 511cf165f7; E11-D11 62f6bb2006; E11-N-OBJECTIVE-RECORD 921214bf42. Verified: `git merge-base --is-ancestor <merged> <ref>` rc 0, `git merge-base --is-ancestor <merged> 02a48db212` rc 1 and `git merge-base --is-ancestor <merged> c6ce415b77` rc 1, and `git diff --name-only <merged>^1 <merged>` names the card's object or one of its paths, for each of the 17, on <ref> a scratch merge of origin/main 030a4d377f and this revision; each <merged> is a first-parent merge of main.",
+   "cards.E11-N-P744-SCOPE.paths": "gains tools/audit/seat/round_metrics.py (see the card's paths_note); `merged` stays unset while pull requests 3657 and 3658 are open."
+  },
+  "unset": "`merged` stays unset on the 14 accepted gating cards whose work is open: E11-K-D4, K-D5, K-D9, K-D10 (pull request 3641), E11-N-P744-SCOPE (3657, 3658), E11-U1, U2, U4 to U10 (NEW-DIMENSIONS part 2).",
+  "review_owed": "The objects differ from those at the review sha 02a48db212, so check_scopes.py refuses the review until a reviewer approves at a commit holding these objects; a delta review of this revision is owed. A review sha on this line keeps every `merged` above after the review."
+ }
+}
diff --git a/dev/governance/config/policy_budgets.json b/dev/governance/config/policy_budgets.json
index c3eab18fc4..634e0eeba9 100644
--- a/dev/governance/config/policy_budgets.json
+++ b/dev/governance/config/policy_budgets.json
@@ -6,7 +6,7 @@
   "_floor_is_not_the_cost": "always_loaded_tokens measures a session that opens nothing. Moving prose out of CLAUDE.md into a paths:-scoped rule lowers it without deleting a line: across the index split the floor fell by more than half while corpus_tokens moved a fraction of a percent. The two caps below are what stop that drop being recorded as headroom -- corpus_tokens does not move when prose moves, and roles charge a seat for what it loads once it opens a file. Policy: .claude/rules/ratchet-budgets.md.",
   "_band": 500,
   "_band_note": "Applies to the five aggregate caps only -- always_loaded_tokens, corpus_tokens and the three roles caps -- which are compared against cap+_band. Per-file caps below are compared exactly and keep zero headroom deliberately. A cap re-recorded to the measured value every time leaves the NEXT pull request refused by the previous seat's arithmetic rather than by its own prose: measured over 2026-09-08..17, twenty consecutive commits sat at exactly zero corpus headroom, 24 of 39 capped files sit there now, and the corpus still rose across a window where the cap was pinned at measured every commit. The recorded cap is the last measurement; the band is the room a seat works in without touching it. Re-record down when the measurement falls more than _band below the cap, and on any reclassification -- .claude/rules/ratchet-budgets.md.",
-  "corpus_tokens": 69244,
+  "corpus_tokens": 71212,
   "roles": {
     "fixer": {
       "opens": [
@@ -61,6 +61,8 @@
     "tools/audit/briefs/D13.md": 84,
     "tools/audit/briefs/D14.md": 35,
     "dev/governance/dimensions/D15.md": 40,
+    "dev/governance/dimensions/D16.md": 95,
+    "dev/governance/dimensions/D17.md": 37,
     "dev/governance/roles/design-review.md": 53,
     "dev/governance/roles/evaluator.md": 27,
     "dev/governance/roles/designer.md": 60,
@@ -107,10 +109,10 @@
     ".claude/workflows/web-fragments.md": 2427,
     ".github/PULL_REQUEST_TEMPLATE.md": 305,
     "AGENTS.md": 183,
-    "CLAUDE.md": 3605,
+    "CLAUDE.md": 3604,
     "tests/README.md": 6686,
     "tools/audit/README.md": 6059,
-    "tools/audit/briefs/COMMON.md": 1697,
+    "tools/audit/briefs/COMMON.md": 1691,
     "tools/audit/briefs/D0.md": 1112,
     "tools/audit/briefs/D1.md": 989,
     "tools/audit/briefs/D10.md": 410,
@@ -119,11 +121,13 @@
     "tools/audit/briefs/D13.md": 1217,
     "tools/audit/briefs/D14.md": 472,
     "dev/governance/dimensions/D15.md": 824,
+    "dev/governance/dimensions/D16.md": 1523,
+    "dev/governance/dimensions/D17.md": 450,
     "dev/governance/roles/design-review.md": 778,
     "dev/governance/roles/evaluator.md": 361,
     "dev/governance/roles/designer.md": 878,
     "tools/audit/briefs/D2.md": 869,
-    "tools/audit/briefs/D3.md": 607,
+    "tools/audit/briefs/D3.md": 600,
     "tools/audit/briefs/D4.md": 678,
     "tools/audit/briefs/D5.md": 624,
     "tools/audit/briefs/D6.md": 487,
diff --git a/dev/governance/dimensions/D16.md b/dev/governance/dimensions/D16.md
new file mode 100644
index 0000000000..23a5d3fae0
--- /dev/null
+++ b/dev/governance/dimensions/D16.md
@@ -0,0 +1,95 @@
+# D16 — Actuator write
+
+Owner's ruling (tvofi, 2026-11-15, "Both (Recommended)"); wording drafted by
+the seat under mandate 6893738184: *every write to the pump, its hold and its
+release equal the plan's target.*
+
+Read `COMMON.md` first. You have an isolated worktree (with `.git`): P1 and
+P2 below edit the write path, and the `upgrade` state reads the previous
+tag's package from it.
+
+## What you are hunting
+
+A command sent to the pump that is not what the plan booked for the step it
+lands in: a wrong value, the wrong step, the wrong order, a hold with no
+release, a baseline not restored. Neighbours, cited and never repeated: D1
+owns whether the cycle survives, and the hold no restart released after an
+upgrade (its step 2); D8 the published reason and state (an entity reporting
+a write wrongly is its lead); D12 a write wrong on one configuration level
+only (a lead naming the level: you run the reference plant,
+`coord_all_features`); D2 the model's identities; D6 a sentence true of the
+code; D17 whether a feature's write happens at all, you its value.
+
+## The oracle is the plan
+
+Your harness builds the solve result, so it chooses the step: set the clock
+to entry k of `timestamps` plus an offset of yours, and read index k of the
+result's own `power_schedule`, `dhw_power_schedule`, `optimal_setpoints`,
+`room_temp_trajectory` and `duty_floor_kw` by plain indexing. The oracle half
+imports nothing from `pump_arbiter` and calls no step selection of the
+package's: one obtained from `desired`, `step_duty` or `_step_kw` grades the
+arbiter against itself and is void (`tests/README.md`). A document is a lead
+for the wording below, never the oracle. With f the floor and P the pump's
+maximum, your pump has P >= 3f, so every state books a circuit at zero or at
+no less than 2f and no threshold enters; `min-cold-tank` alone sits on the
+floor and states its booked kW as a number.
+
+| state: space kW, hot-water kW at step k | what reached `services.async_call` |
+|---|---|
+| `idle`: 0, 0 | no mode written, no circuit asked to start |
+| `min-cold-tank`: f, 0, tank reading 20 C; `partial`: (f+P)/2, 0; `full`: P, 0 | nothing asks the tank to charge; an indoor set-point equals index k of `optimal_setpoints`; a water set-point is strictly above the do-not-heat value, does not fall as booked kW rises, and has step 4's effect |
+| `dhw-only`: 0, 2f or more | nothing asks the house circuit to start: the pump's hot-water-only mode where it offers one, else the space set-point that calls for no heat; the tank set-point is the configured one |
+| `both`: (f+P)/2, 2f or more | hot water asked first, then the house, inside the one step |
+| `boost-partial`: `partial`, a space boost live | the space channel's target is the top of its band, never between floor and top |
+| `disinfection`: `partial`, the cycle held on | the tank write reaches the disinfection target; the run is recorded complete only once it is reached |
+| `baseline`: the clock past the last step | the pump handed back to its own thermostats: both circuits allowed, the configured tank set-point |
+| `restart`, `upgrade`: `partial` after a reload on this release's store, on the previous tag's | `partial`'s row |
+| `unavailable`: `partial`, the written entity unavailable | no write recorded as made; `partial`'s row once it is back |
+| `observe`, `off`: `partial` under that duty mode | no write; each written entity returned to its baseline once |
+
+## Method
+
+1. **The universe.** `python3 tools/audit/enumerate.py d16-writes --cells`:
+   every call of, or reference to, the service call and every `log_held`
+   site, times the states above; report examined over its lines. A
+   `domain=?` line is a cell. A hold whose latch gates no actuator write (the
+   price, weather and solar fetches) is rowed "gates no write" with its
+   reason: examined, never dropped. A writer it misses is a finding against
+   the enumerator first. Write each cell's oracle before you read its site.
+2. **Value.** The command satisfies its state's row and lies inside the
+   entity's `min`, `max` and `step`. Cells owed: `boost-partial` (pull
+   request 3562), `disinfection` (3452), `min-cold-tank` (R10-SETPOINT-BOOST).
+3. **Timing and order.** The write lands in the step its action was cut for;
+   the mode before the supply; a minimum run and pause held across a
+   re-solve. Cells owed: `partial` with the cycle held across the end of step
+   k, step k-1 booked `idle` so that a step selected late moves the cell
+   (3478); `partial` entered from `idle` (3530); `idle` entered by a re-solve
+   minutes after `partial` switched the supply on (3512).
+4. **Effect.** Under a pump model with an integrating speed loop and a start
+   hysteresis, measured power and started runs equal the plan's. Cells owed:
+   `partial`, the water set-point (3405); `dhw-only`, the tank above its
+   set-point less the hysteresis (3531).
+5. **Hold and release.** Per hold, on a store this release wrote: a
+   transition table over every field that gates the write, and from each
+   reachable state a path to "writes again" that needs no person (no restart,
+   option change or service call). A state with no such path, or a table you
+   cannot close, is a finding; a state a gate reads and the table above lacks
+   is a row you add.
+6. **Restore.** Off, unload, remove and a duty-mode change return each
+   written entity to its baseline, once.
+
+## The perturbations you owe
+
+P1, the arbiter's step selection moved one step late: your k does not move
+and step 3 goes red. P2, the arbiter's docstring row for a house-only step
+and its code edited together to allow the tank: the row above does not move
+and step 2 goes red. Null controls: the unedited tree is green, and the
+docstring edited alone moves no cell.
+
+## Traps
+
+A write the stub accepts is not one Home Assistant accepts
+(`tests/ha_contract.py`). A hold is legitimate when its release is
+automatic: report the missing release, not the hold. A water set-point has
+no number in the plan: grade it by step 2's conditions and step 4's effect,
+never by re-deriving the arbiter's curve.
diff --git a/dev/governance/dimensions/D17.md b/dev/governance/dimensions/D17.md
new file mode 100644
index 0000000000..717e66e1e4
--- /dev/null
+++ b/dev/governance/dimensions/D17.md
@@ -0,0 +1,37 @@
+# D17 — Feature behaviour
+
+Ruled and worded as `D16.md`'s opening states: *each feature does what its
+documentation says, in every state that reaches it.*
+
+Read `COMMON.md` first. Your oracle is read from `README.md` and `docs/`.
+
+## What you are hunting
+
+A service, option, configuration field, entity or blueprint that, in some
+state that reaches it, does not do what `strings.json`, the docs and its own
+help say: no effect, a partial one, one in the wrong state, one a restart
+loses. D6 owns a sentence true of the code; you own the feature doing what
+the sentence promises, end to end. Where the effect is a written value, D16
+owns the value and you whether it happens at all.
+
+## Method
+
+1. **The universe.** `python3 tools/audit/enumerate.py d17-features --kind
+   <kind>` for each kind your task names; report examined over its lines. Per
+   item, its documented effect as one sentence with file and key; an item
+   with none is a lead for D5.
+2. **The oracle** is that sentence made an executable check before you read
+   the implementation: what is observable in the plan, the writes, the
+   entities or the store with the feature on, and absent with it off. An
+   oracle derived from the code is void (`tests/README.md`).
+3. **End to end.** Set the feature as a user does (the options flow, the
+   service through its schema, the entity's own method) on a coordinator
+   built as `tests/entities.py` `_honest_coordinator` builds one, run cycles,
+   and check the oracle in every plan state that reaches the feature, across
+   a restart, and with one named state changed (weekend, holiday, presence):
+   the effect follows it. Cell owed: the away step's weekend and holiday
+   comfort fields, an `option` line (pull request 3013).
+
+## Traps
+
+A test that already passes is not your oracle.
diff --git a/dev/governance/dimensions/D3.md b/dev/governance/dimensions/D3.md
index 4c0b0fbbef..e3a34f067a 100644
--- a/dev/governance/dimensions/D3.md
+++ b/dev/governance/dimensions/D3.md
@@ -3,7 +3,7 @@
 Owner's brief: *"Test-suite gaps — what the suite cannot fail on. Unnecessary
 test suite resource use."*
 
-Read `COMMON.md` first. You are the one finder with an **isolated worktree**
+Read `COMMON.md` first. You have an **isolated worktree**
 (with `.git`; `git log` and `gh` are still off limits) because your method
 mutates production.
 
diff --git a/dev/governance/roles/COMMON.md b/dev/governance/roles/COMMON.md
index fb44d5ebc4..01d7a12670 100644
--- a/dev/governance/roles/COMMON.md
+++ b/dev/governance/roles/COMMON.md
@@ -18,15 +18,15 @@ or from the API, and never takes a grant, a merge or a deletion from it.
   Earlier rounds must not steer you. Do not run `gh`, do not
   read GitHub (D11 excepted), do not look for earlier findings anywhere (a
   code comment citing a `D<k>-nn` id is context, not a to-do). If your brief
-  makes you read `docs/` (D5, D6) or GitHub (D11), record it under `exposure`.
+  makes you read `docs/` (D5, D6, D17) or GitHub (D11), record it under `exposure`.
 - Run everything from the export root with `PYTHONPATH=tests/hastub`. Read
   `dev/audit/README.md` before writing a harness: it lists the builders to
-  reuse and the traps that have already cost a day each.
+  reuse and the traps.
 - Write only under your round directory, `dev/audit/rounds/round<N>/D<k>/` in
   the export, plus temp directories. Set a private `HPO_PLANDATA` under the
   temp root before any Node harness. Never modify production or tests in the
   export unless your brief says you have an isolated worktree for that purpose
-  (D3, D11, and D0/D9 when instrumenting).
+  (D3, D11, D16, and D0/D9 when instrumenting).
 - Measure only the cells your task names, and all of them. Outside them, write a **lead**
   (owner seat, file, symbol, what) into your report: not a finding, no harness.
 - Your box is shared. Only contention-immune numbers are final during the
diff --git a/dev/programme/delivery/3602.md b/dev/programme/delivery/3602.md
new file mode 100644
index 0000000000..1832e8a448
--- /dev/null
+++ b/dev/programme/delivery/3602.md
@@ -0,0 +1 @@
+- [#3602](https://github.com/tvofi/heatpump_optimizer/pull/3602) — **merged `2c84a85`**, R11-OUTSIDE-HONEST-STARTS-RUNS: r11 outside honest starts runs (R11-OUTSIDE-HONEST-STARTS-RUNS).
diff --git a/dev/programme/delivery/3630.md b/dev/programme/delivery/3630.md
new file mode 100644
index 0000000000..e3490f5bde
--- /dev/null
+++ b/dev/programme/delivery/3630.md
@@ -0,0 +1 @@
+- [#3630](https://github.com/tvofi/heatpump_optimizer/pull/3630) — **merged `95e8178`**, R11-OWNER-ROADMAP: r11 owner roadmap.
diff --git a/dev/programme/delivery/3641.md b/dev/programme/delivery/3641.md
index bbb9f3a3a0..24d4782429 100644
--- a/dev/programme/delivery/3641.md
+++ b/dev/programme/delivery/3641.md
@@ -1 +1 @@
-- [#3641](https://github.com/tvofi/heatpump_optimizer/pull/3641) — **open**, R11-PRE-OWNER-CRITERIA: r11 pre owner criteria (R11-PRE-OWNER-CRITERIA)
+- [#3641](https://github.com/tvofi/heatpump_optimizer/pull/3641) — **merged `367c3b9`**, R11-PRE-OWNER-CRITERIA: r11 pre owner criteria.
diff --git a/dev/programme/delivery/3645.md b/dev/programme/delivery/3645.md
index 07902e592c..577b61ae14 100644
--- a/dev/programme/delivery/3645.md
+++ b/dev/programme/delivery/3645.md
@@ -1 +1 @@
-- [#3645](https://github.com/tvofi/heatpump_optimizer/pull/3645) — **open**, R11-PRE-TOOLCHAIN-PIN: r11 pre toolchain pin (R11-PRE-TOOLCHAIN-PIN)
+- [#3645](https://github.com/tvofi/heatpump_optimizer/pull/3645) — **merged `e352724`**, R11-PRE-TOOLCHAIN-PIN: r11 pre toolchain pin (R11-PRE-TOOLCHAIN-PIN).
diff --git a/dev/programme/delivery/3657.md b/dev/programme/delivery/3657.md
new file mode 100644
index 0000000000..0d5b486ddc
--- /dev/null
+++ b/dev/programme/delivery/3657.md
@@ -0,0 +1 @@
+- [#3657](https://github.com/tvofi/heatpump_optimizer/pull/3657) — **merged `2c91123`**, R11-PRE-ROUND-METRICS p2: r11 pre round metrics part 2 (R11-PRE-ROUND-METRICS).
diff --git a/dev/programme/delivery/3659.md b/dev/programme/delivery/3659.md
index f2ab8ad5f9..f2e6d8adf6 100644
--- a/dev/programme/delivery/3659.md
+++ b/dev/programme/delivery/3659.md
@@ -1 +1 @@
-- [#3659](https://github.com/tvofi/heatpump_optimizer/pull/3659) — **open**, R10-DRAW-MAP-EVIDENCE: r10 draw map evidence (R10-DRAW-MAP-EVIDENCE)
+- [#3659](https://github.com/tvofi/heatpump_optimizer/pull/3659) — **merged `6f42281`**, R10-DRAW-MAP-EVIDENCE: r10 draw map evidence (R10-DRAW-MAP-EVIDENCE).
diff --git a/dev/programme/delivery/3661.md b/dev/programme/delivery/3661.md
index 86c436944c..d67ef91f39 100644
--- a/dev/programme/delivery/3661.md
+++ b/dev/programme/delivery/3661.md
@@ -1 +1 @@
-- [#3661](https://github.com/tvofi/heatpump_optimizer/pull/3661) — **open**, R11-HOTFIX-TICK-SEAT-WINDOW: tick reads SEAT_WINDOW_MIN from owed_watch (R11-HOTFIX-TICK-SEAT-WINDOW)
+- [#3661](https://github.com/tvofi/heatpump_optimizer/pull/3661) — **merged `030a4d3`**, R11-HOTFIX-TICK-SEAT-WINDOW: tick reads SEAT_WINDOW_MIN from owed_watch.
diff --git a/dev/programme/delivery/3664.md b/dev/programme/delivery/3664.md
new file mode 100644
index 0000000000..d4ff4270ca
--- /dev/null
+++ b/dev/programme/delivery/3664.md
@@ -0,0 +1 @@
+- [#3664](https://github.com/tvofi/heatpump_optimizer/pull/3664) — **merged `ef6363d`**, R11-PRE-HANDOFF-BOOKKEEPING: r11 pre handoff bookkeeping (R11-PRE-HANDOFF-BOOKKEEPING).
diff --git a/dev/programme/delivery/3669.md b/dev/programme/delivery/3669.md
new file mode 100644
index 0000000000..ed1a6cb8ac
--- /dev/null
+++ b/dev/programme/delivery/3669.md
@@ -0,0 +1 @@
+- [#3669](https://github.com/tvofi/heatpump_optimizer/pull/3669) — **merged `92d38ec`**, R11-START-EVALUATION-LAND: r11 start evaluation land.
diff --git a/dev/programme/delivery/3671.md b/dev/programme/delivery/3671.md
new file mode 100644
index 0000000000..4a02b77e99
--- /dev/null
+++ b/dev/programme/delivery/3671.md
@@ -0,0 +1 @@
+- [#3671](https://github.com/tvofi/heatpump_optimizer/pull/3671) — **merged `30f9caa`**, R11-HOTFIX-MAIN-SELFTEST-DRIFT: re-record the self-test read table.
diff --git a/dev/programme/delivery/3672.md b/dev/programme/delivery/3672.md
new file mode 100644
index 0000000000..8d3313f9cf
--- /dev/null
+++ b/dev/programme/delivery/3672.md
@@ -0,0 +1 @@
+- [#3672](https://github.com/tvofi/heatpump_optimizer/pull/3672) — **open**, R11-PRE-NEW-DIMENSIONS (part 2): r11 pre new dimensions p2 (R11-PRE-NEW-DIMENSIONS)
diff --git a/dev/programme/delivery/3681.md b/dev/programme/delivery/3681.md
new file mode 100644
index 0000000000..fc38b2cdac
--- /dev/null
+++ b/dev/programme/delivery/3681.md
@@ -0,0 +1 @@
+- [#3681](https://github.com/tvofi/heatpump_optimizer/pull/3681) — **open**, record: delivery rows (autofix)
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
 
diff --git a/tests/closure.py b/tests/closure.py
index 8eeaaadb0e..7604b737df 100644
--- a/tests/closure.py
+++ b/tests/closure.py
@@ -362,6 +362,8 @@ INERT = (
     # it -- only this gate has no dependency on it beyond that.
     "AGENTS.md",
     "DISCLAIMER.md",
+    # The long-term direction page (#3616): prose linked from README.md, read by no gate script.
+    "ROADMAP.md",
     # The quality-scale register (#229) sat here from #229 to #951: no gate
     # script read it, so the INERT listing was honest. #951 ended that --
     # tests/entities.py now reads the register to pin its coverage-bearing
diff --git a/tests/closures.json b/tests/closures.json
index b8dcb0b629..c7c9764cb2 100644
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
@@ -1688,6 +1700,8 @@
    "dev/governance/dimensions/D13.md",
    "dev/governance/dimensions/D14.md",
    "dev/governance/dimensions/D15.md",
+   "dev/governance/dimensions/D16.md",
+   "dev/governance/dimensions/D17.md",
    "dev/governance/dimensions/D2.md",
    "dev/governance/dimensions/D3.md",
    "dev/governance/dimensions/D4.md",
@@ -2163,6 +2177,7 @@
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/replay_doc.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/services.yaml",
@@ -2359,6 +2374,7 @@
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/replay_doc.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/services.yaml",
@@ -2517,6 +2533,7 @@
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/replay_doc.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
@@ -2668,6 +2685,7 @@
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/replay_doc.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/services.yaml",
@@ -2850,6 +2868,7 @@
    "custom_components/heatpump_optimizer/quiet_windows.py",
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/slab_seed.py",
@@ -3032,6 +3051,7 @@
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/replay_doc.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/services.yaml",
@@ -3425,6 +3445,7 @@
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/replay_doc.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
@@ -3513,6 +3534,7 @@
    "custom_components/heatpump_optimizer/payload.py",
    "custom_components/heatpump_optimizer/plan_step.py",
    "custom_components/heatpump_optimizer/pv.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/tariff.py",
    "custom_components/heatpump_optimizer/thermal_model.py",
@@ -3595,6 +3617,7 @@
    "custom_components/heatpump_optimizer/quiet_windows.py",
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
@@ -3702,6 +3725,7 @@
    "custom_components/heatpump_optimizer/quiet_windows.py",
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
    "custom_components/heatpump_optimizer/slab_seed.py",
@@ -3765,6 +3789,7 @@
    "custom_components/heatpump_optimizer/plan_step.py",
    "custom_components/heatpump_optimizer/presets.py",
    "custom_components/heatpump_optimizer/pv.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/tariff.py",
    "custom_components/heatpump_optimizer/thermal_model.py",
@@ -3865,6 +3890,7 @@
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/replay_doc.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
@@ -3964,6 +3990,7 @@
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/replay_doc.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
@@ -4007,6 +4034,7 @@
    "custom_components/heatpump_optimizer/payload.py",
    "custom_components/heatpump_optimizer/plan_step.py",
    "custom_components/heatpump_optimizer/pv.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/tariff.py",
    "custom_components/heatpump_optimizer/thermal_model.py",
@@ -4089,6 +4117,7 @@
    "custom_components/heatpump_optimizer/quiet_windows.py",
    "custom_components/heatpump_optimizer/repairs.py",
    "custom_components/heatpump_optimizer/running_signal.py",
+   "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
@@ -4164,6 +4193,7 @@
    "tools/audit/seat/gh_read_run.py",
    "tools/audit/seat/hooks_setup.py",
    "tools/audit/seat/ledger.py",
+   "tools/audit/seat/loop_ledger.py",
    "tools/audit/seat/merge_train.py",
    "tools/audit/seat/moved_paths.py",
    "tools/audit/seat/mutant_run.py",
@@ -4517,6 +4547,7 @@
    "dev/audit/harnesses/r10_water_setpoint_feedback.py",
    "dev/audit/harnesses/r10_weekday_range_twins.py",
    "dev/audit/harnesses/r11_denominator_planted.py",
+   "dev/audit/harnesses/r11_honest_starts_runs.py",
    "dev/audit/harnesses/r11_main_cancel_mutants.py",
    "dev/audit/harnesses/r11_owner_criteria.py",
    "dev/audit/harnesses/r11_plan_page_inventory.py",
@@ -4751,6 +4782,13 @@
    "dev/audit/rounds/round10/study-reseed/reparam_sites.py",
    "dev/audit/rounds/round10/study-reseed/reseed_rolling.py",
    "dev/audit/rounds/round10/user-text/enumerate.py",
+   "dev/audit/rounds/round11/evaluation/design_verdicts.py",
+   "dev/audit/rounds/round11/evaluation/dimension_read.py",
+   "dev/audit/rounds/round11/evaluation/escapes.py",
+   "dev/audit/rounds/round11/evaluation/gate_reds.py",
+   "dev/audit/rounds/round11/evaluation/instrument_cost.py",
+   "dev/audit/rounds/round11/evaluation/main_red_groups.py",
+   "dev/audit/rounds/round11/evaluation/tally.py",
    "dev/audit/rounds/round3/D10/coverage_rule.sh",
    "dev/audit/rounds/round3/D10/strict_typing_rule.sh",
    "dev/audit/rounds/round3/D4/card_states_geometry.mjs",
@@ -5284,7 +5322,7 @@
   },
   "tests/boost_drift_replay.py": {
    "rc": 0,
-   "seconds": 150.2
+   "seconds": 341.1
   },
   "tests/card.mjs": {
    "rc": 0,
@@ -5319,7 +5357,7 @@
    "seconds": 21.5
   },
   "tests/entities.py": {
-   "rc": 0,
+   "rc": 1,
    "seconds": 867.9
   },
   "tests/env_drift.py": {
@@ -5352,7 +5390,7 @@
   },
   "tests/harness_headers.py": {
    "rc": 0,
-   "seconds": 126.6
+   "seconds": 327.6
   },
   "tests/layout.py": {
    "rc": 0,
@@ -5376,7 +5414,7 @@
   },
   "tests/plan_view.py": {
    "rc": 0,
-   "seconds": 0.8
+   "seconds": 1.8
   },
   "tests/solar_alignment.py": {
    "rc": 0,
@@ -5392,7 +5430,7 @@
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
index 8cb4cdb29d..14d9768ac3 100644
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
@@ -86772,7 +86819,8 @@ R.check(
 )
 # Only the arbiter (which reports and reads the split), the sensor (which
 # publishes) and the coordinator (whose factory reset voids the store, and which
-# hands the planner's read to a solve's configuration, R10-DUTY-SWITCH-PLANNER-PRICE)
+# hands the planner's read to a solve's configuration, R10-DUTY-SWITCH-PLANNER-PRICE,
+# and the settled running class to a solve's inputs, R11-OUTSIDE-HONEST-STARTS-RUNS)
 # name the module; arbiter and planner read the estimate through one leg rule.
 _ds_pkg = _DsPath("custom_components/heatpump_optimizer")
 _ds_readers = sorted(
@@ -86794,12 +86842,13 @@ _ds_rs_own = {n.module for n in _ds_ast.walk(_ds_ast.parse((_ds_pkg / "running_s
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
@@ -90877,8 +90926,6 @@ from heatpump_optimizer.dhw_planner import DhwPlanner as _DspPlanner  # noqa: E4
 from heatpump_optimizer.optimizer import (  # noqa: E402
     HeatPumpOptimizer as _DspOpt,
     OptimizationConfig as _DspCfg,
-    count_compressor_starts as _dsp_starts,
-    cycling_penalty as _dsp_cyc,
 )
 from heatpump_optimizer.thermal_model import (  # noqa: E402
     ThermalModel as _DspTM,
@@ -90891,6 +90938,8 @@ _DSP_STEPS = np.arange(96)
 _DSP_PRICES = 1.3 + 0.9 * np.sin(2 * np.pi * (_DSP_STEPS - 30) / 96.0)
 #: Bankaifan's table: every hot water to heating switch stopped the compressor,
 #: none the other way, median off time 501 s (8.2 and 8.5 minutes).
+from heatpump_optimizer import runs as _dsp_runs  # noqa: E402
+
 _DSP_PAIR, _DSP_OFF = (1.0, 0.0), (501.0, 0.0)
 
 
@@ -90900,14 +90949,16 @@ def _dsp_w(space, dhw, pair, floor=None, p_max=6.0):
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
@@ -90959,13 +91010,23 @@ def _dsp_opt(pair=(0.0, 0.0), off=(0.0, 0.0), *, clamp=False, p_min=1.5, p_max=5
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
@@ -91334,15 +91395,15 @@ R.check(
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
 
@@ -91350,7 +91411,11 @@ def _dsp_solve(pair=(0.0, 0.0), off=(0.0, 0.0), *, pins=None, legionella_h=20.0,
 
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
@@ -91363,6 +91428,7 @@ def _dsp_solve(pair=(0.0, 0.0), off=(0.0, 0.0), *, pins=None, legionella_h=20.0,
 
     def vector(*args):
         seen.vectors[0] += 1
+        seen.vectors_outside[0] += not seen.solving[0]
         return real_vector(*args)
 
     def min_run(self, **kwargs):
@@ -91384,12 +91450,16 @@ def _dsp_solve(pair=(0.0, 0.0), off=(0.0, 0.0), *, pins=None, legionella_h=20.0,
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
@@ -91405,7 +91475,7 @@ def _dsp_solve(pair=(0.0, 0.0), off=(0.0, 0.0), *, pins=None, legionella_h=20.0,
     finally:
         _DspPlanner._build_dhw_requirements = real_build
         _DspPlanner._apply_dhw_min_run = real_min_run
-        _dsp_om._stop_availability = real_vector
+        _dsp_om._stop_availability, _dsp_om._commit_runs = real_vector, real_stage
     seen.space = np.asarray(seen.result.power_schedule, float)
     seen.dhw = np.asarray(seen.result.dhw_power_schedule, float)
     seen.bans = [k["placement_ban"] for k, *_ in seen.builds if "placement_ban" in k]
@@ -91422,8 +91492,13 @@ def _dsp_same_plan(a, b):
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
@@ -91470,18 +91545,31 @@ R.check(
 
 
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
@@ -91491,11 +91579,79 @@ _dsp_accept = {
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
@@ -91580,11 +91736,11 @@ R.check(
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
@@ -91893,6 +92049,7 @@ R.check(
 # steps either side of each, and one at the running threshold.
 _dsp_e = _dsp_solve(_DSP_PAIR, (0.0, 0.0))
 _dsp_e0 = _dsp_solve((0.0, 0.0), (501.0, 0.0))
+_dsp_e_plain = _dsp_solve(None)  # the same day as the two above, not the install table's
 _dsp_e_tank = np.zeros(96)
 _dsp_e_tank[[40, 41]] = 1.5
 _DSP_EPS = 2.0 * _dsp_om._LBFGSB_FD_EPS
@@ -91920,7 +92077,7 @@ def _dsp_e_solve(seen, start):
 
 
 _dsp_e_runs = {
-    label: (_dsp_e_solve(_dsp_e, start), _dsp_e_solve(_dsp_e0, start), _dsp_e_solve(_dsp_base["duty-cycle"], start))
+    label: (_dsp_e_solve(_dsp_e, start), _dsp_e_solve(_dsp_e0, start), _dsp_e_solve(_dsp_e_plain, start))
     for label, start in _DSP_E_STARTS.items()
 }
 R.check(
@@ -91952,23 +92109,27 @@ R.check(
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
@@ -91999,29 +92160,32 @@ _dsp_mc_live = (
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
@@ -92060,15 +92224,17 @@ _dsp_fx_free = _dsp_solve(_DSP_PAIR, _DSP_OFF, clamp=True, p_min=5.5, cyc=0.0)
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
@@ -92099,9 +92265,13 @@ def _dsp_co_solve(dhw_plan, warm_start):
 
 
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
@@ -92377,6 +92547,1069 @@ R.check(
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
 
 
diff --git a/tests/layout.json b/tests/layout.json
index 0746b077df..54890ec847 100644
--- a/tests/layout.json
+++ b/tests/layout.json
@@ -10,6 +10,7 @@
     "NOTICE",
     "DISCLAIMER.md",
     "SECURITY.md",
+    "ROADMAP.md",
     "RELEASE_NOTES.md",
     "VERSION",
     "hacs.json",
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
diff --git a/tools/audit/check_scopes.py b/tools/audit/check_scopes.py
index eb5da7be15..815f0d94e0 100644
--- a/tools/audit/check_scopes.py
+++ b/tools/audit/check_scopes.py
@@ -6,10 +6,13 @@ Exit 0 only if every dimension passes and coverage passes; each failure prints t
 twice or not at all. Coverage: every tracked path at --ref is in some dimension's universe or
 matches one entry of scopes.json's `_coverage_excluded` (glob -> reason), never both, and every
 entry matches some path; a path in neither is refused by name, so no path goes unmeasured.
-Null control: --self-test duplicates one seat's block and empties another's, drops D10's
+An axis tools/audit/enumerate.py also prints (D17's `kind`, its d17-features prefixes) must name
+exactly those prefixes: a value in one copy alone is refused.
+Null control: --self-test duplicates one seat's block and empties another's (D1 and D2, then D16
+and D17, with a kind planted in either copy of D17's axis), drops D10's
 universe, strips the tests/ and blueprints/ globs, and excludes a covered path; it exits 0 only
 when the checker refuses each perturbed file by the path it names. It also runs the default
-invocation as a subprocess, on the live scopes (rc 0) and without D4's and D6's blueprints globs (rc 1).
+invocation as a subprocess, on the live scopes (rc 0) and with every universe's blueprints glob dropped (rc 1).
 Ledger dimensions (D5, D6): a dimension's `ledger` {step, max_units} caps each seat's text units
 (tools/audit/text_ledger.py, the dimension's own rule) over the files its blocks hold for that step,
 so a seat's cell is finishable; a seat over the cap is refused by name. Its `classify` globs and
@@ -61,6 +64,11 @@ import roster_lib
 _spec = importlib.util.spec_from_file_location("text_ledger", Path(__file__).with_name("text_ledger.py"))
 text_ledger = importlib.util.module_from_spec(_spec)
 _spec.loader.exec_module(text_ledger)
+_spec = importlib.util.spec_from_file_location("audit_enumerate", Path(__file__).with_name("enumerate.py"))
+audit_enumerate = importlib.util.module_from_spec(_spec)
+_spec.loader.exec_module(audit_enumerate)
+# An axis whose values are a second copy of an enumerator's line prefixes: (dimension, axis) -> the prefixes.
+AXIS_SOURCES = {("D17", "kind"): lambda: audit_enumerate.KINDS}
 
 def expand_braces(p):
     m = re.search(r"\{([^{}]*)\}", p)
@@ -122,6 +130,17 @@ def classify_errors(d, tree, uni, dim=None):
     return errs
 
 
+def axis_errors(dim, d):
+    """An axis the enumerator also prints must name exactly the enumerator's prefixes: a kind in one
+    copy alone is a cell no seat can print, or a line no seat owns."""
+    errs = []
+    for name, vals in d.get("axis", {}).items():
+        src = AXIS_SOURCES.get((dim, name))
+        if src and set(vals) != set(src()):
+            errs.append(f"axis {name} {sorted(set(vals) ^ set(src()))} in scopes.json or tools/audit/enumerate.py, not both")
+    return errs
+
+
 def check(scopes, tree, loc, units=lambda dim, f: 0):
     ok = True
     for dim, d in scopes.items():
@@ -153,7 +172,7 @@ def check(scopes, tree, loc, units=lambda dim, f: 0):
             dup = {k: v for k, v in owners.items() if len(v) > 1 and k[0] != "step"}
         missing = want - set(owners)
         extra = set(owners) - want
-        over, cls_errs, per_seat = [], classify_errors(d, tree, uni, dim), {}
+        over, cls_errs, per_seat = [], classify_errors(d, tree, uni, dim) + axis_errors(dim, d), {}
         if "ledger" in d:
             per_seat = ledger_units(dim, d, files_of, units)
             over = [s for s, n in per_seat.items() if n > d["ledger"]["max_units"]]
@@ -915,6 +934,38 @@ def main():
         none = copy.deepcopy(scopes)
         none["D2"]["seats"][list(none["D2"]["seats"])[-1]] = [{"files": ["**"], "steps": []}]
         res = [check(bad, tree, loc) for bad in (twice, none)]
+        # The same two on the plan-oracle dimensions, each refused by what it names, and the axis
+        # D17 shares with the enumerator: a kind planted in either copy alone is refused.
+        def _dim(bad, dim):
+            o = io.StringIO()
+            with contextlib.redirect_stdout(o):
+                r = check({dim: bad[dim]}, tree, loc)
+            return r, o.getvalue()
+        twice16 = copy.deepcopy(scopes)
+        a16, b16 = list(twice16["D16"]["seats"])[:2]
+        twice16["D16"]["seats"][b16].append(copy.deepcopy(twice16["D16"]["seats"][a16][0]))
+        none17 = copy.deepcopy(scopes)
+        none17["D17"]["seats"][list(none17["D17"]["seats"])[-1]] = [{"files": ["**"], "steps": []}]
+        kind17 = copy.deepcopy(scopes)
+        kind17["D17"]["axis"]["kind"].append("planted-kind")
+        kind17["D17"]["seats"][list(kind17["D17"]["seats"])[0]][0]["axis"].append("planted-kind")
+        r_t16, o_t16 = _dim(twice16, "D16")
+        r_n17, o_n17 = _dim(none17, "D17")
+        r_k17, o_k17 = _dim(kind17, "D17")
+        real_kinds = audit_enumerate.KINDS
+        try:
+            audit_enumerate.KINDS = real_kinds + ("planted-prefix",)
+            r_e17, o_e17 = _dim(scopes, "D17")
+        finally:
+            audit_enumerate.KINDS = real_kinds
+        new_dims = {
+            "null control: the live D16 and D17 pass": _dim(scopes, "D16")[0] is True and _dim(scopes, "D17")[0] is True,
+            "a D16 block owned by two seats is refused": not r_t16 and f"by ['{a16}', '{b16}']" in o_t16,
+            "a D17 seat emptied leaves its cells unowned": not r_n17 and "   unowned (" in o_n17,
+            "a D17 kind the enumerator does not print is refused": not r_k17 and "axis kind ['planted-kind']" in o_k17,
+            "a prefix the enumerator prints and no D17 seat owns is refused": not r_e17 and "axis kind ['planted-prefix']" in o_e17,
+        }
+        print(f"   D16 and D17 arms: {sum(new_dims.values())}/{len(new_dims)} held")
         # Coverage arms, each refused by the path it must name, so a broad
         # exclusion cannot satisfy an arm by rc alone. D10 is the one universe
         # that alone holds py.typed; stripping every tests/ and blueprints/ glob
@@ -935,7 +986,7 @@ def main():
             "drop D10's universe": (no_d10, [PKG + "py.typed"]),
             "strip tests/ and blueprints/ globs": (bare, ["tests/closure.py", "blueprints/automation/notifications.yaml"]),
         }
-        cov = {}
+        cov = dict(new_dims)
         for name, (bad, must) in arms.items():
             ok, unc = coverage(bad, tree, quiet=True)
             cov[name] = (not ok) and all(m in unc for m in must) and nulls not in unc
@@ -1026,12 +1077,13 @@ def main():
                     "and refuses an uncited brief-named harness": uncited_refused})
         print(f"   default verdict: live {live}, no D10 refused {no_d10_refused}, uncited refused {uncited_refused}")
         # The default invocation, run whole as a subprocess of this file with
-        # --repo/--ref: the live scopes exit 0, and the scopes with D4's and D6's
-        # blueprints/** globs dropped exit 1 naming a blueprint, both printing
+        # --repo/--ref: the live scopes exit 0, and the scopes with the blueprints/**
+        # glob dropped from every universe that names one exit 1 naming a blueprint, both printing
         # verdict()'s citation line. So coverage cannot fall out of main()'s exit
         # code, and that exit is verdict()'s, whose citation arm is pinned above.
         no_bp = copy.deepcopy(scopes)
-        for k in ("D4", "D6"):
+        bp_dims = [k for k, d in scopes.items() if not k.startswith("_") and any(g.startswith("blueprints/") for g in d["universe"])]
+        for k in bp_dims:
             no_bp[k]["universe"] = [g for g in no_bp[k]["universe"] if not g.startswith("blueprints/")]
         def default_run(sc, *more):
             with tempfile.NamedTemporaryFile("w", suffix=".json") as fh:
@@ -1042,7 +1094,7 @@ def main():
         run_live, run_bp = default_run(scopes), default_run(no_bp)
         cited = " harness citations: "
         cov["the default invocation exits 0 on the live scopes"] = run_live.returncode == 0 and cited in run_live.stdout
-        cov["and exits 1 without D4's and D6's blueprints globs"] = (run_bp.returncode == 1 and cited in run_bp.stdout
+        cov["and exits 1 with the blueprints globs dropped from every universe that names one"] = (run_bp.returncode == 1 and cited in run_bp.stdout
             and "in no universe and not excluded: blueprints/" in run_bp.stdout)
         print(f"   default invocation: live rc={run_live.returncode}, blueprints dropped rc={run_bp.returncode}")
         # The start evaluation: the rules as a function, then the default
diff --git a/tools/audit/enumerate.py b/tools/audit/enumerate.py
index dba42026bf..66e7b67c91 100644
--- a/tools/audit/enumerate.py
+++ b/tools/audit/enumerate.py
@@ -28,9 +28,12 @@ Usage: python3 -I tools/audit/enumerate.py <universe> [--repo DIR] [options]
                          an unlisted source or no test is refused
   d14-classes [--status open]   dev/audit/config/bugclasses.json entries that carry a status
   d15-installs           dev/audit/config/bundles.json, one line per bundle an install sent
-  d16-writes [--cells]   actuator `services.async_call` and `log_held` sites; --cells crosses each
-                         with the PUMP_DUTY_MODES parsed from const.py and the four lifecycle conditions
-  d17-features           services.yaml keys, strings.json steps/fields/entities, blueprints
+  d16-writes [--cells]   every call of, or reference to, `services.async_call` (`write ... domain=<literal>`,
+                         `domain=?` when the domain is no literal; a literal on READ_ONLY_DOMAINS is no write)
+                         and every `log_held` site; --cells crosses each with the plan states of STATES, and
+                         refuses unless const.py's PUMP_DUTY_MODES equal the duty modes those states name
+  d17-features [--kind K]   services.yaml keys, strings.json steps/fields/entities, blueprints; --kind prints
+                         the lines of one prefix (KINDS)
   --briefs               the acceptance of a brief that names a universe: every `enumerate.py <universe>`
                          a dev/governance/dimensions/D*.md cites, with its --cells or --pairs, runs
                          non-empty; an unknown universe or a tree citing none is refused
@@ -48,8 +51,15 @@ from pathlib import Path
 
 PKG = "custom_components/heatpump_optimizer"
 OBJECTIVE, IDENTITIES, BUNDLES = "dev/audit/config/objective.json", "dev/audit/config/identities.json", "dev/audit/config/bundles.json"
-# the conditions the actuator-write dimension drives
-CONDITIONS = ("running", "restart", "upgrade", "unavailable")
+# D16.md's plan states, one axis: (state, the duty mode it runs under). A seat adds rows, never drops one.
+STATES = (("idle", "control"), ("min-cold-tank", "control"), ("partial", "control"), ("full", "control"),
+          ("dhw-only", "control"), ("both", "control"), ("boost-partial", "control"), ("disinfection", "control"),
+          ("baseline", "control"), ("restart", "control"), ("upgrade", "control"), ("unavailable", "control"),
+          ("observe", "observe"), ("off", "off"))
+# service domains whose calls read and never command an entity
+READ_ONLY_DOMAINS = ("weather",)
+# d17-features' line prefixes; dev/audit/config/scopes.json's D17 `kind` axis is held equal by check_scopes.py
+KINDS = ("service", "config-step", "config-field", "options-step", "option", "entity", "blueprint")
 # D0.md step 4's axes; the last two plants are the cells round 10's escapes showed no seat drove
 TOPOLOGY, DHW, HORIZON_H = ("single-zone", "two-zone"), ("dhw", "no-dhw"), (6, 24, 48)
 PLANT = ("plain", "valve-storage", "wood", "manual-valve-buffer", "flow-setpoint-behind-valve")
@@ -110,21 +120,29 @@ def const_assign(tree, name):
 def d16(repo, cells=False, **_):
     out = []
     for p in pkg_files(repo):
-        for n, q in scoped(parse(p)):
-            if isinstance(n, ast.Call):
-                f = n.func
-                if isinstance(f, ast.Attribute) and f.attr == "async_call" and isinstance(f.value, ast.Attribute) and f.value.attr == "services":
-                    out.append(f"write {rel(repo, p)}:{n.lineno} {q}")
-                if fname(n) == "log_held":
-                    out.append(f"hold {rel(repo, p)}:{n.lineno} {q}")
+        tree = parse(p)
+        calls = {id(n.func): n for n in ast.walk(tree) if isinstance(n, ast.Call)}
+        for n, q in scoped(tree):
+            if isinstance(n, ast.Attribute) and n.attr == "async_call" and isinstance(n.value, ast.Attribute) and n.value.attr == "services":
+                # a reference handed on uncalled is a writer too: its domain is whatever the receiver passes
+                c = calls.get(id(n))
+                arg = c and (c.args[0] if c.args else next((k.value for k in c.keywords if k.arg == "domain"), None))
+                dom = arg.value if isinstance(arg, ast.Constant) and isinstance(arg.value, str) else "?"
+                if dom not in READ_ONLY_DOMAINS:
+                    out.append(f"write {rel(repo, p)}:{n.lineno} {q} domain={dom}")
+            if isinstance(n, ast.Call) and fname(n) == "log_held":
+                out.append(f"hold {rel(repo, p)}:{n.lineno} {q}")
     if cells:
         v = const_assign(parse(repo / PKG / "const.py"), "PUMP_DUTY_MODES")
-        modes = [e.value for e in getattr(v, "elts", []) if isinstance(e, ast.Constant)]
-        out = [f"{s} | duty={m} | {c}" for s in out for m in modes for c in CONDITIONS]
+        modes, named = {e.value for e in getattr(v, "elts", []) if isinstance(e, ast.Constant)}, {d for _, d in STATES}
+        if modes != named:
+            raise Refuse(f"const.py PUMP_DUTY_MODES {sorted(modes)} are not the duty modes STATES names {sorted(named)}: "
+                         "a duty mode with no plan state is unrowed, and a state under no duty mode cannot run")
+        out = [f"{s} | {name}" for s in out for name, _ in STATES]
     return out
 
 
-def d17(repo, **_):
+def d17(repo, kind=None, **_):
     out, base = [], repo / PKG
     out += [f"service {m}" for m in re.findall(r"^([a-z_]+):", (base / "services.yaml").read_text(), re.M)]
     s = json.loads((base / "strings.json").read_text())
@@ -134,7 +152,11 @@ def d17(repo, **_):
             out += [f"{kfield} {step}.{k}" for k in (body.get("data") or {})]
     ent = s.get("entity", {})
     out += [f"entity {pl}.{k}" for pl in USER_PLATFORMS for k in ent.get(pl, {})]
-    return out + [f"blueprint {b}" for b in sorted(tracked(repo)) if b.startswith("blueprints/")]
+    out += [f"blueprint {b}" for b in sorted(tracked(repo)) if b.startswith("blueprints/")]
+    stray = sorted({l.split(" ", 1)[0] for l in out} - set(KINDS))
+    if stray:
+        raise Refuse(f"d17-features prints a prefix KINDS does not name: {stray}")
+    return [l for l in out if not kind or l.split(" ", 1)[0] == kind]
 
 
 def d14(repo, status=None, **_):
@@ -621,7 +643,7 @@ def plant(root):
     w(f"{PKG}/p.py", "import json\ndef parse_a(x):\n    return json.loads(x)\nasync def g(r, m):\n    await r.json()\n    r.json('k')\n"
       "    await m.async_subscribe('t')\n")
     w(f"{PKG}/e.py", "class E:\n    @property\n    def extra_state_attributes(self):\n        return {}\nclass F:\n    _attr_extra_state_attributes = {}\nclass G:\n    pass\ndef use(c):\n    return c.cycle()\n")
-    w(f"{PKG}/const.py", "PUMP_DUTY_MODES: Final = ('off', 'control')\nCONFIG_ENTRY_VERSION: Final = 3\n"
+    w(f"{PKG}/const.py", "PUMP_DUTY_MODES: Final = ('off', 'observe', 'control')\nCONFIG_ENTRY_VERSION: Final = 3\n"
       "CONF_A_ENTITY = 'a_entity'\nCONF_B_ENTITY: Final = 'b_entity'\nCONF_F_SENSOR = 'f_sensor'\nCONF_H1 = 'h1'\nCONF_H2 = 'h2'\n"
       "CONF_W_SENSOR = 'w_sensor'\nCONF_NAME = 'n'\nX_ENTITY = 'x_entity'\nMODES = ('m1', 'm2')\n")
     w(f"{PKG}/config_flow.py", "def _entity_of(d):\n    return selector.EntitySelector(d)\ndef _text():\n    return selector.TextSelector()\n"
@@ -694,6 +716,7 @@ def edit_json(path, fn):
 
 
 X, CO, CF = f"{PKG}/x.py", f"{PKG}/coordinator.py", f"{PKG}/config_flow.py"
+DUTY = "PUMP_DUTY_MODES: Final = ('off', 'observe', 'control')\n"
 # the entry points the planted __init__.py defines, typed apart from ENTRY_FNS so a dropped one shows
 ENTRY = ("async_setup", "async_setup_entry", "async_unload_entry", "async_remove_entry", "async_migrate_entry", "async_update_options")
 # universe, options, the planted count, the edit deleting one item, the count after it, the edit emptying the source
@@ -721,8 +744,7 @@ PLANTED = [
     ("d14-classes", {}, 2, edit_json("dev/audit/config/bugclasses.json", lambda d: d.pop("B")), 1, put("dev/audit/config/bugclasses.json", "{}")),
     ("d15-installs", {}, 2, edit_json(BUNDLES, lambda d: d["bundles"].pop()), 1, edit_json(BUNDLES, lambda d: d["bundles"].clear())),
     ("d16-writes", {}, 3, cut(X, "    hass.services.async_call('a', 'b')\n"), 2, put(X, "")),
-    ("d16-writes", {"cells": True}, 3 * 2 * 4, cut(f"{PKG}/const.py", "('off', 'control')", "('off',)"), 3 * 1 * 4,
-     cut(f"{PKG}/const.py", "PUMP_DUTY_MODES: Final = ('off', 'control')\n")),
+    ("d16-writes", {"cells": True}, 3 * len(STATES), cut(X, "    log_held('x')\n"), 2 * len(STATES), cut(f"{PKG}/const.py", DUTY)),
     ("d17-features", {}, 9, cut(f"{PKG}/services.yaml", "set_b:\n"), 8,
      both(put(f"{PKG}/services.yaml", ""), put(f"{PKG}/strings.json", "{}"), rm("blueprints/automation/b.yaml"))),
 ]
@@ -807,7 +829,7 @@ def self_test():
         arm("d1-lifecycle lines: an async_track_* call, a LIFE_CALLS call and every entry point",
             run("d1-lifecycle", t), sorted([f"async_create_task {X}:12 f", f"async_track_time_interval {X}:11 f", *[f"entry {f}" for f in ENTRY]]))
         arm("d16-writes lines: the .services.async_call sites and log_held, not an async_call on another receiver",
-            run("d16-writes", t), [f"hold {X}:4 f", f"write {X}:2 f", f"write {X}:3 f"])
+            run("d16-writes", t), [f"hold {X}:4 f", f"write {X}:2 f domain=a", f"write {X}:3 f domain=a"])
         arm("d1-parsers lines: a parse def, json.loads, a bare .json() and async_subscribe, not a .json(x) with an argument",
             run("d1-parsers", t), [f"def {PKG}/p.py:2 parse_a", f"json {PKG}/p.py:3 parse_a", f"response {PKG}/p.py:5 g", f"subscribe {PKG}/p.py:7 g"])
         arm("d0-modules follows `from <package> import <module>`", f"{PKG}/t.py" in run("d0-modules", t), True)
@@ -815,6 +837,57 @@ def self_test():
         arm("d9-solves lines: the solver's call, the recursive call inside its module, the coordinator's call and its bare reference",
             [(l.split(" <- ")[0], l.rsplit(" ", 1)[-1]) for l in run("d9-solves", t)],
             [("path go", "C.cycle"), ("path go", "(ref)"), ("path go", "go"), ("solve _multi_start_minimize", "go")])
+        # D16's site rule and its one axis; D17's kinds. Each edit is of a fresh plant.
+        def planted(*edits, u="d16-writes", **opt):
+            d = Path(tempfile.mkdtemp())
+            try:
+                plant(d)
+                for e in edits:
+                    e(d)
+                with contextlib.redirect_stderr(io.StringIO()):
+                    return run(u, d, **opt)
+            except Refuse:
+                return "Refuse"
+            finally:
+                shutil.rmtree(d, ignore_errors=True)
+        CALL, more = "    hass.services.async_call('a', 'b')\n", lambda line: cut(X, "    log_held('x')\n", "    log_held('x')\n" + line)
+        writes = lambda ls: sorted(l.split(" ", 2)[2] for l in ls if l.startswith("write "))
+        arm("d16 a write line names its literal domain", writes(planted()), ["f domain=a", "f domain=a"])
+        arm("d16 a call on a read-only domain is no write (the count stays)", len(planted(more("    hass.services.async_call('weather', 'get_forecasts')\n"))), 3)
+        arm("d16 null control: the same call on another domain is a write", len(planted(more("    hass.services.async_call('number', 'set_value')\n"))), 4)
+        arm("d16 a reference handed on uncalled is a write with no literal domain", writes(planted(more("    g = hass.services.async_call\n"))), ["f domain=?", "f domain=a", "f domain=a"])
+        arm("d16 a call whose domain is no literal is a cell, never dropped", writes(planted(cut(X, CALL, "    hass.services.async_call(*svc(e), {})\n"))), ["f domain=?", "f domain=a"])
+        arm("d16 a domain passed by keyword is read", writes(planted(cut(X, CALL, "    hass.services.async_call(domain='weather', service='s')\n"))), ["f domain=a"])
+        real_states = STATES
+        try:
+            globals()["STATES"] = tuple(st for st in real_states if st[0] != "idle")
+            arm("d16 --cells is sites x states: one state cut drops one cell per site", len(planted(cells=True)), 3 * (len(real_states) - 1))
+        finally:
+            globals()["STATES"] = real_states
+        arm("d16 --cells each site carries every state once", sorted({l.rsplit(" | ", 1)[1] for l in planted(cells=True)}), sorted(n for n, _ in STATES))
+        arm("d16 --cells a duty mode added in production and rowed by no state is refused",
+            planted(cut(f"{PKG}/const.py", "('off', 'observe', 'control')", "('off', 'observe', 'control', 'eco')"), cells=True), "Refuse")
+        arm("d16 --cells a duty mode a state names and production dropped is refused",
+            planted(cut(f"{PKG}/const.py", "('off', 'observe', 'control')", "('off', 'control')"), cells=True), "Refuse")
+        arm("d17 --kind prints one prefix's lines", planted(u="d17-features", kind="service"), ["service set_a", "service set_b"])
+        def cli(*argv):
+            d = Path(tempfile.mkdtemp())
+            try:
+                plant(d)
+                buf = io.StringIO()
+                with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
+                    rc = main([*argv, "--repo", str(d)])
+                return rc, buf.getvalue().splitlines()
+            finally:
+                shutil.rmtree(d, ignore_errors=True)
+        arm("d17 the command line's --kind reaches the filter", cli("d17-features", "--kind", "service"), (0, ["service set_a", "service set_b"]))
+        arm("d17 the kinds partition the universe", sorted(l for k in KINDS for l in (lambda r: [] if r == "Refuse" else r)(planted(u="d17-features", kind=k))), planted(u="d17-features"))
+        real_kinds = KINDS
+        try:
+            globals()["KINDS"] = tuple(k for k in real_kinds if k != "blueprint")
+            arm("d17 a printed prefix KINDS does not name is refused", planted(u="d17-features"), "Refuse")
+        finally:
+            globals()["KINDS"] = real_kinds
         arm("d0-modules follows an absolute import of the package", f"{PKG}/u.py" in run("d0-modules", t), True)
         arm("d3-sites --ast --by-file counts the sites per file", run("d3-sites", t, ast_only=True, by_file=True), [f"{X} 5"])
         quiet = contextlib.redirect_stderr(io.StringIO())
@@ -877,7 +950,7 @@ def self_test():
         arm("briefs: a citation of no universe is refused", cited("1. `enumerate.py d1-nothing`\n"), "Refuse")
         arm("briefs: a tree whose briefs cite none is refused", cited("1. Enumerate by hand.\n"), "Refuse")
         arm("briefs: one refused citation beside a good one refuses the tree", cited("1. `enumerate.py d1-inputs` and `enumerate.py d1-nothing`\n"), "Refuse")
-        arm("briefs: a citation's options are run as cited", (cut(f"{PKG}/const.py", "PUMP_DUTY_MODES: Final = ('off', 'control')\n")(t), cited("1. `enumerate.py d16-writes --cells`\n"))[1], "Refuse")
+        arm("briefs: a citation's options are run as cited", (cut(f"{PKG}/const.py", DUTY)(t), cited("1. `enumerate.py d16-writes --cells`\n"))[1], "Refuse")
         (t / BUNDLES).write_text('{"bundles": []}')
         arm("briefs: a cited universe that is empty is refused", cited("1. `enumerate.py d15-installs`\n"), "Refuse")
         plant_bundles(t)
@@ -929,6 +1002,7 @@ def main(argv=None):
     ap.add_argument("--repo", default=".")
     ap.add_argument("--cells", action="store_true")
     ap.add_argument("--pairs", action="store_true")
+    ap.add_argument("--kind", choices=KINDS)
     ap.add_argument("--ledger")
     ap.add_argument("--status")
     ap.add_argument("--plane", choices=("price-weather",))
@@ -943,7 +1017,7 @@ def main(argv=None):
     if not a.universe and not a.briefs:
         ap.error("universe required")
     try:
-        ls = briefs(Path(a.repo)) if a.briefs else run(a.universe, a.repo, cells=a.cells, pairs=a.pairs, ledger=a.ledger, status=a.status, plane=a.plane,
+        ls = briefs(Path(a.repo)) if a.briefs else run(a.universe, a.repo, cells=a.cells, pairs=a.pairs, kind=a.kind, ledger=a.ledger, status=a.status, plane=a.plane,
                  state=a.state, by_file=a.by_file, ast_only=a.ast)
     except (Refuse, SyntaxError, json.JSONDecodeError) as e:
         print(f"REFUSE: {e}", file=sys.stderr)
diff --git a/tools/audit/prepare_baseline.sh b/tools/audit/prepare_baseline.sh
index 597a48f76d..52af3a9de8 100755
--- a/tools/audit/prepare_baseline.sh
+++ b/tools/audit/prepare_baseline.sh
@@ -7,7 +7,7 @@
 #
 # Run from any checkout of the repository. Creates, beside the repository's
 # worktrees directory:
-#   ../audit-r<round>-baseline        the export (D1, D2, D4, D5, D6, D7, D8, D10, D12)
+#   ../audit-r<round>-baseline        the export (D1, D2, D4, D5, D6, D7, D8, D10, D12, D17)
 #   ../audit-r<round>-<dim>           a worktree per dimension in ISOLATED_DIMS below
 #                                     (the instrumenting finders, D14, D15, D16, and D11 and D13, which
 #                                      audit the process and read `main`'s history and
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index 9e552da0cd..262b1adee1 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -126,6 +126,7 @@ standing-seat liveness step keep the seats alive.
 - [`round_metrics.py`](instruments/round_metrics.py.md) — decision 0018's flow reads per round and per week (merges by class, lead_time from the roster-entry commit per class, product_green with the gate's check count, restore, runner seconds and tokens per merge), unread on no input, and the producer of the scorecard's inputs
 - [`plant_recall.py`](instruments/plant_recall.py.md) — plants a held-out seat's objective bugs into the baseline export before the finders, refusing an unsound plant list, and counts recall after the judge (found / planted, whole, per space and per kind), unread on no input
 - [`finder_overlap.py`](instruments/finder_overlap.py.md) — seats a twin finder on one scopes.json seat's universe and estimates the bugs there from the two seats' judged-real overlap, with both models, unread on no input
+- [`loop_ledger.py`](instruments/loop_ledger.py.md) — the convergence record per round and week: escapes by found_by and owning dimension, injected, refix and card L1's countermeasure loop, read from the roster fields `roster_edit.py set-field` validates; unread on a partial ledger
 - [`outside_intake.py`](instruments/outside_intake.py.md) — lists submissions by outside users since a cursor with what each is owed (triage, answer, reply), and answers or refuses one, marked so none is answered twice
 - [`postmerge.py`](instruments/postmerge.py.md) — after a merge: the record-issue line, the roster stage and main's suite state (the state docs are the plan-beat's); a failed step is printed OWED and opens the ledger's `postmerge-owed`
 - [`record_beat.py`](instruments/record_beat.py.md) — one merged pull request's record-issue line from a fixed template, the full merge sha, read back byte-identical
diff --git a/tools/audit/seat/finder_overlap.py b/tools/audit/seat/finder_overlap.py
index 67c84ced45..164bd1f19f 100644
--- a/tools/audit/seat/finder_overlap.py
+++ b/tools/audit/seat/finder_overlap.py
@@ -47,7 +47,7 @@ TWIN_FROM = 71
 
 
 def seat_pair(scopes: dict, seat: str, model_a: str, model_b: str, rnd: int) -> tuple[dict | None, str]:
-    m = re.fullmatch(r"(D(?:1[0-5]|[0-9]))-(s[0-9]+)", seat)
+    m = re.fullmatch(r"(D(?:1[0-7]|[0-9]))-(s[0-9]+)", seat)
     if not m or m.group(2) not in ((scopes.get(m.group(1)) or {}).get("seats") or {}):
         return None, f"{seat!r} is no seat of scopes.json"
     if not model_a.strip() or not model_b.strip():
@@ -160,6 +160,11 @@ def cases(m) -> dict[str, bool]:
     r["seat: a seat scopes.json does not hold is refused"] = m.seat_pair(scopes, "D1-s2", "a", "b", 11)[0] is None and \
         m.seat_pair(scopes, "D2-s1", "a", "b", 11)[0] is None
     r["seat: a missing model is refused"] = m.seat_pair(scopes, "D1-s1", "a", " ", 11)[0] is None
+    hi = {"D16": {"seats": {"s1": []}}, "D17": {"seats": {"s3": []}}, "D18": {"seats": {"s1": []}}}
+    r["seat: a D16 and a D17 seat are seated, a D18 one refused"] = \
+        (m.seat_pair(hi, "D16-s1", "a", "b", 11)[0] or {}).get("universe") == "D16-s1" and \
+        (m.seat_pair(hi, "D17-s3", "a", "b", 11)[0] or {}).get("universe") == "D17-s3" and \
+        m.seat_pair(hi, "D18-s1", "a", "b", 11)[0] is None
     rep = lambda *ids: {"findings": [{"id": i} for i in ids]}
     A, B = m.report_ids(rep("D1-s1-01", "D1-s1-02", "D1-s1-03"), "x"), m.report_ids(rep("D1-s1-71", "D1-s1-72"), "x")
     r["report: a box file is read under the seat's name"] = \
@@ -212,6 +217,9 @@ def cases(m) -> dict[str, bool]:
 #: (needle, replacement, the case that must fail). One per predicate.
 MUTANTS = {
     "seat in scopes": ('m.group(2) not in ((scopes.get(m.group(1)) or {}).get("seats") or {})', "False", "does not hold"),
+    "seat bound D15": ("1[0-7]|[0-9]", "1[0-5]|[0-9]", "D17 seat are seated"),
+    "seat bound D16": ("1[0-7]|[0-9]", "1[0-6]|[0-9]", "D17 seat are seated"),
+    "seat bound D18": ("1[0-7]|[0-9]", "1[0-8]|[0-9]", "D17 seat are seated"),
     "seat models": ("if not model_a.strip() or not model_b.strip():", "if False:", "missing model"),
     "box key": ('rep = (rep.get("reports") or {}).get(name)', "rep = rep", "box file"),
     "shared": ("m = len(bugs_a), len(bugs_b), len(bugs_a & bugs_b)", "m = len(bugs_a), len(bugs_b), 0", "Chapman"),
diff --git a/tools/audit/seat/instruments/enumerate.py.md b/tools/audit/seat/instruments/enumerate.py.md
index 8daec72343..02eb0a46c7 100644
--- a/tools/audit/seat/instruments/enumerate.py.md
+++ b/tools/audit/seat/instruments/enumerate.py.md
@@ -4,9 +4,8 @@
   reports `universe=N examined=n` against a command and not a recollection.
   Path: `tools/audit/enumerate.py`; its docstring lists every universe and
   the rule each is read by. When: a dimension brief names it as a step's
-  universe (D0, D1, D2, D8, D9, D12, D15; `d3-sites`, `d14-classes`,
-  `d16-writes` and `d17-features` are ported for the briefs that will cite
-  them). Two universes are registers a round's register pull request
+  universe (D0, D1, D2, D8, D9, D12, D15, D16, D17; `d3-sites` and
+  `d14-classes` are ported for the briefs that will cite them). Two universes are registers a round's register pull request
   appends to: `dev/audit/config/identities.json` (D2) and
   `dev/audit/config/bundles.json` (D15). `--ledger TSV` joins a seat's
   ledger to any universe, each line beside its asserting test or `not run`
diff --git a/tools/audit/seat/instruments/loop_ledger.py.md b/tools/audit/seat/instruments/loop_ledger.py.md
new file mode 100644
index 0000000000..f494655df9
--- /dev/null
+++ b/tools/audit/seat/instruments/loop_ledger.py.md
@@ -0,0 +1,36 @@
+# `loop_ledger.py`
+
+- `loop_ledger.py` — the convergence record's enumerator (R11-PRE-ROUND-METRICS
+  part 2; decision 0018 sections 2 and 4; process cards P7 and L1). Report-only.
+  Its rules and null controls are the script's docstring. It reads seven
+  roster fields, each written only through `roster_edit.py set-field`, which
+  refuses a word outside its vocabulary (`roster_lib.convergence_why`):
+  - `found_by` — a finder dimension `D<n>`, `reviewer`, `ci-main`, `owner` or `outside`;
+  - `owned_by` — the owning dimension `D<n>`, or `none`;
+  - `caused_by` — `{"cause": "#<pr>" | <group> | "external" | "original", "rca": <id>}`,
+    the id a record under `dev/audit/rca/` that is one of the group's own `rca`
+    records or declares the group its subject in its title and opening paragraph,
+    table rows aside (`roster_lib.rca_lists`, `rca_subjects`), so the cause is the
+    root-cause seat's, never the fixer's; a group with no `rca` of its own takes
+    `caused_by` once a record declares it so, and until then that read stays `unread`;
+    a group a record names only later, as a status row or a sibling, is refused;
+  - `family` — a class of `dev/audit/config/bugclasses.json`;
+  - `cm_kind` — `delete`, `self-heal`, `narrow`, `widen`, `new-refusal` or `policy-text`;
+  - `parent` — the roster group this one descends from;
+  - `follows` — the fix a re-report follows (a fix that did not fix).
+
+  Every outside group and every hotfix or bug group touching the product owes
+  `found_by`, `owned_by` and `caused_by`; any other hotfix group `found_by` and
+  `caused_by`; a group with an `rca` record `caused_by`, `family` and
+  `cm_kind`. When: the orchestrator sets them at intake and at the RCA's
+  landing, and runs
+
+      python3 -I tools/audit/seat/loop_ledger.py [--roster-ref REF]
+
+  at a round's close and weekly; it prints, per round (each roster) and per
+  ISO week of roster entry, `escapes` by found_by and owned_by, `injected`,
+  `refix` and `loop` (countermeasures by family and cm_kind, k, generations).
+  A read whose owing groups are not all recorded prints `unread (k of n ...)`.
+  `scorecard.py`'s `E` line prints the owning-dimension split through
+  `owned_split`. `--self-test`: the null controls (an empty directory, one
+  dropped field per read), the vocabulary refusals and a two-commit history.
diff --git a/tools/audit/seat/instruments/roster_edit.py.md b/tools/audit/seat/instruments/roster_edit.py.md
index 825a266b13..379f7e9003 100644
--- a/tools/audit/seat/instruments/roster_edit.py.md
+++ b/tools/audit/seat/instruments/roster_edit.py.md
@@ -15,7 +15,11 @@
   `set-after <group> <G1,G2,...|->` (replaces the after-edges whole, `-` for
   none), `set-source <group> <outside|->` (a word of `roster_lib.SOURCES`, or
   `-` to drop the key; queue-only, like `set-after`; the plan's top tier reads
-  `outside` through `roster_lib.is_outside`), and `set-resume <group> --field
+  `outside` through `roster_lib.is_outside`), `set-field <group> <field> <value>`
+  (the P268 mapping fields, and the convergence record `loop_ledger.py` reads:
+  `found_by`, `owned_by`, `caused_by`, `family`, `cm_kind`, `parent`,
+  `follows`, each refused outside `roster_lib.convergence_why`'s vocabulary),
+  and `set-resume <group> --field
   <stage|commit|branch|last_step|next_step|note>` for the resume free-text
   fields a session restarts from. When: any roster change — never a string
   splice, which unbalanced the file twice. Refusals: the lint gate (run from
diff --git a/tools/audit/seat/instruments/scorecard.py.md b/tools/audit/seat/instruments/scorecard.py.md
index 9436eeaec4..fdbfd79259 100644
--- a/tools/audit/seat/instruments/scorecard.py.md
+++ b/tools/audit/seat/instruments/scorecard.py.md
@@ -21,7 +21,9 @@
   - `S` — size: `machinery_ratchet.py --measure` (non-production merges per
     window, churn per 1 000 product lines) and machinery lines over product lines.
   - `E` — roster groups whose source is `outside` and hotfix or bug groups
-    touching the product, and how many of both are still open.
+    touching the product, and how many of both are still open; beside them
+    both sets by owning dimension (`loop_ledger.owned_split`), unread while
+    any of them records no `owned_by`.
   - `C` — the longest run of consecutive cancelled main runs in the last 50.
   - `K` — `recycle` lines of the standing dispatch and triage seats in the
     day's sweep record.
diff --git a/tools/audit/seat/loop_ledger.py b/tools/audit/seat/loop_ledger.py
new file mode 100644
index 0000000000..476dde8a57
--- /dev/null
+++ b/tools/audit/seat/loop_ledger.py
@@ -0,0 +1,353 @@
+#!/usr/bin/env python3
+"""The loop ledger: the convergence record's reads, per round and per week.
+
+    python3 -I loop_ledger.py [--repo DIR] [--roster-ref REF]
+    python3 -I loop_ledger.py --dir DIR
+    python3 -I loop_ledger.py --self-test
+
+Report-only (R11-PRE-ROUND-METRICS part 2; decision 0018 sections 2 and 4;
+process cards P7 and L1). It reads the convergence fields `roster_edit.py
+set-field` writes (roster_lib.CONVERGENCE_FIELDS, each validated by
+roster_lib.convergence_why) from every `wave-r<N>-groups.json` roster: at
+`--roster-ref` (default roster_lib.reader_ref's answer) or in `--dir`.
+
+WHICH GROUPS OWE WHICH FIELDS (`owed`):
+  an escape (`is_escape`: source outside, or a hotfix or bug group whose files
+  include custom_components/; scorecard line E's two sets) owes found_by,
+  owned_by and caused_by; any other hotfix group (roster_lib.is_hotfix) owes
+  found_by and caused_by (card P7); a group with an `rca` record owes caused_by,
+  family and cm_kind (card L1). A field present but outside its vocabulary is
+  unrecorded.
+
+PERIODS: each roster is one round (its file's N). A week is the ISO week of
+the commit that last wrote the group's `"group":` line (`git blame` at the
+ref): the roster entry, since a group's name is not rewritten. `--dir` has no
+history, so its week lines are unread.
+
+THE READS, per period (rule, then the null control the self-test holds it to):
+  escapes   escape groups, split by found_by and by owned_by (`none` a value).
+  injected  escapes whose caused_by.cause is a pull request or a roster group
+            (beside it the external and original counts). Its denominator, the
+            window's production merges, is round_metrics.py's, not read here.
+  refix     groups naming in `follows` the fix they follow (link 3 of 0018
+            section 4: a fix that did not fix).
+  loop      over the groups with an rca record (the countermeasures): count by
+            family and by cm_kind; k, the children per countermeasure (groups
+            whose `parent` is one); the groups per generation (parent hops to
+            a group with no parent) and each generation's ratio to the one
+            before.
+  NO-READ: a read whose owing groups are not all recorded prints
+  `unread (k of n ... unrecorded: names)`, never a partial value; no roster
+  at all prints `loop_ledger unread`.
+  NULL: an empty input directory prints unread and no value; a roster whose
+  every owing group is recorded prints values, and dropping one field from one
+  group turns that read, and only that read, unread.
+"""
+from __future__ import annotations
+
+import argparse
+import collections
+import datetime
+import json
+import os
+import re
+import subprocess
+import sys
+import tempfile
+from pathlib import Path
+
+sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I drops the script's directory
+import roster_lib  # noqa: E402
+from scorecard import escape_sets  # noqa: E402  line E's two sets are the escapes
+
+ESCAPE_FIELDS = ("found_by", "owned_by", "caused_by")
+HOTFIX_FIELDS = ("found_by", "caused_by")
+CM_FIELDS = ("caused_by", "family", "cm_kind")
+SHOWN = 5  # unrecorded names printed per read
+_GROUP_LINE = re.compile(r'^\s*"group":\s*"([^"]+)"')
+
+
+def is_escape(g: dict) -> bool:
+    """Scorecard line E's two sets: an outside group, or a hotfix or bug group touching the product."""
+    return any(escape_sets([g]))
+
+
+def owed(g: dict) -> tuple:
+    """The convergence fields this group owes, in CONVERGENCE_FIELDS order."""
+    want = set()
+    if is_escape(g):
+        want.update(ESCAPE_FIELDS)
+    elif roster_lib.is_hotfix(g):
+        want.update(HOTFIX_FIELDS)
+    if g.get("rca"):
+        want.update(CM_FIELDS)
+    return tuple(f for f in roster_lib.CONVERGENCE_FIELDS if f in want)
+
+
+def _gap(groups: list, fields, names) -> list:
+    return [g["group"] for g in groups if not roster_lib.recorded(g, fields, names)]
+
+
+def _unread(what: str, gap: list, n: int) -> str:
+    shown = ", ".join(gap[:SHOWN]) + (" ..." if len(gap) > SHOWN else "")
+    return f"{what} unread ({len(gap)} of {n} owing groups unrecorded: {shown})"
+
+
+def _counts(c: collections.Counter) -> str:
+    return "{" + ", ".join(f"{k}: {v}" for k, v in sorted(c.items())) + "}"
+
+
+def owned_split(groups: list, names) -> str:
+    """Escapes by owning dimension, or unread while any escape has no admissible owned_by."""
+    esc = [g for g in groups if is_escape(g)]
+    gap = _gap(esc, ("owned_by",), names)
+    if gap:
+        return _unread("by owning dimension", gap, len(esc))
+    return "by owning dimension " + _counts(collections.Counter(g["owned_by"] for g in esc))
+
+
+def generation(g: dict, by_name: dict) -> int | None:
+    """Parent hops from `g` to a group with no parent; None on a cycle or a parent no roster holds."""
+    seen, n = set(), 0
+    while g.get("parent"):
+        if g["group"] in seen or g["parent"] not in by_name:
+            return None
+        seen.add(g["group"])
+        g, n = by_name[g["parent"]], n + 1
+    return n
+
+
+def reads(groups: list, every: list) -> list[str]:
+    """The four reads over one period's `groups`; `every` is all groups of all rosters (names, parents)."""
+    names = {g["group"] for g in every}
+    by_name = {g["group"]: g for g in every}
+    esc = [g for g in groups if is_escape(g)]
+    out = []
+    gap = _gap(esc, ("found_by", "owned_by"), names)
+    out.append(_unread("escapes", gap, len(esc)) if gap else
+               f"escapes {len(esc)} by found_by {_counts(collections.Counter(g['found_by'] for g in esc))} "
+               f"by owned_by {_counts(collections.Counter(g['owned_by'] for g in esc))}")
+    gap = _gap(esc, ("caused_by",), names)
+    if gap:
+        out.append(_unread("injected", gap, len(esc)))
+    else:
+        c = collections.Counter(g["caused_by"]["cause"] if g["caused_by"]["cause"] in roster_lib.CAUSES
+                                else "merged" for g in esc)
+        out.append(f"injected {c['merged']} (external {c['external']}, original {c['original']}; "
+                   "per production merge: round_metrics.py's denominator)")
+    owing = [g for g in groups if owed(g)]
+    gap = [g["group"] for g in owing if not roster_lib.recorded(g, owed(g), names)]
+    if gap:
+        out.append(_unread("refix", gap, len(owing)))
+    else:
+        fol = [g for g in groups if roster_lib.recorded(g, ("follows",), names)]
+        out.append(f"refix {len(fol)}" + "".join(f"; {g['group']} follows {g['follows']}" for g in fol))
+    cms = [g for g in groups if g.get("rca")]
+    gap = _gap(cms, CM_FIELDS, names)
+    if gap:
+        out.append(_unread("loop", gap, len(cms)))
+        return out
+    cm_names = {g["group"] for g in cms}
+    kids = sum(1 for g in every if g.get("parent") in cm_names)
+    gens = collections.Counter(generation(g, by_name) for g in groups if g.get("parent") or g["group"] in cm_names)
+    broken = gens.pop(None, 0)
+    ladder = " ".join(f"g{i}:{gens[i]}" + (f"({gens[i] / gens[i - 1]:.2f})" if i and gens[i - 1] else "")
+                      for i in range(max(gens) + 1)) if gens else ""
+    k = f"{kids / len(cms):.2f}" if cms else "none (no countermeasure)"
+    out.append(f"loop countermeasures {len(cms)} by family {_counts(collections.Counter(g['family'] for g in cms))} "
+               f"by cm_kind {_counts(collections.Counter(g['cm_kind'] for g in cms))}; k {k}; "
+               f"generations {ladder or 'none'}" + (f"; {broken} with a broken parent chain" if broken else ""))
+    return out
+
+
+def week_of(t: int) -> str:
+    y, w, _ = datetime.datetime.fromtimestamp(t, datetime.timezone.utc).isocalendar()
+    return f"{y}-W{w:02d}"
+
+
+def entered(blame: str) -> dict:
+    """Group name -> author time of the blame line that holds its `"group":` key (`--line-porcelain`)."""
+    out, t = {}, None
+    for ln in blame.splitlines():
+        if ln.startswith("author-time "):
+            t = int(ln.split()[1])
+        elif ln.startswith("\t") and (m := _GROUP_LINE.match(ln[1:])) and t is not None:
+            out[m.group(1)] = t  # a roster file holds each group's "group": line once
+    return out
+
+
+def load_ref(repo: str, ref: str) -> tuple[list, dict | None]:
+    """[(round, path, roster)] at `ref`, and each group's entry time (None when blame fails)."""
+    r = roster_lib._git(repo, "ls-tree", "--name-only", ref, roster_lib.ROSTERS_DIR + "/")
+    paths = sorted((p for p in r.stdout.split() if roster_lib.newest_roster([p])), key=roster_lib.roster_round)
+    out, when = [], {}
+    for p in paths:
+        out.append((roster_lib.roster_round(p), p, json.loads(roster_lib._git(repo, "show", f"{ref}:{p}").stdout)))
+        b = roster_lib._git(repo, "blame", "--line-porcelain", ref, "--", p)
+        when = None if when is None or b.returncode else {**entered(b.stdout), **when}
+    return out, when
+
+
+def load_dir(d: Path) -> list:
+    return sorted(((roster_lib.roster_round(p.name), str(p), roster_lib.load_roster_file(str(p)))
+                   for p in (d.iterdir() if d.is_dir() else []) if roster_lib.newest_roster([p.name])),
+                  key=lambda x: x[0])
+
+
+def report(rosters: list, when: dict | None) -> list[str]:
+    if not rosters:
+        return ["loop_ledger unread (no wave-r<N>-groups.json roster)"]
+    latest = {g["group"]: g for _, _, ro in rosters for g in roster_lib.groups_of(ro).values()}
+    every = list(latest.values())  # a group carried into a later round's roster is counted once, as there
+    out = []
+    for n, path, ro in rosters:
+        out.append(f"round {n} ({path})")
+        out += ["  " + ln for ln in reads(list(roster_lib.groups_of(ro).values()), every)]
+    if when is None:
+        return out + ["weeks unread (no roster history: --dir, or git blame failed)"]
+    weeks = collections.defaultdict(list)
+    for g in every:
+        weeks[week_of(when[g["group"]]) if g["group"] in when else "unentered"].append(g)
+    for wk in sorted(weeks):
+        out.append(f"week {wk}")
+        out += ["  " + ln for ln in reads(weeks[wk], every)]
+    return out
+
+
+def main(argv: list[str]) -> int:
+    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
+    ap.add_argument("--repo", default=".")
+    ap.add_argument("--roster-ref")
+    ap.add_argument("--dir")
+    ap.add_argument("--self-test", action="store_true")
+    a = ap.parse_args(argv)
+    if a.self_test:
+        return self_test()
+    if a.dir:
+        lines = report(load_dir(Path(a.dir)), None)
+    else:
+        lines = report(*load_ref(a.repo, roster_lib.reader_ref(a.repo, a.roster_ref)))
+    print("\n".join(lines))
+    return 0
+
+
+# ------------------------------------------------------------------ self-test
+
+def _fixture() -> list:
+    """Every owing group recorded: two escapes, one hotfix, two countermeasures, a child and a grandchild."""
+    rca = "R10-N-log-flood"
+    cb = lambda c: {"cause": c, "rca": rca}  # noqa: E731
+    return [
+        {"group": "R9-OUT", "source": "outside", "rca": [rca], "found_by": "outside", "owned_by": "D8",
+         "caused_by": cb("#3520"), "family": "N-log-flood", "cm_kind": "narrow"},
+        {"group": "R9-HOTFIX-A", "files": ["custom_components/x.py"], "rca": [rca], "found_by": "owner",
+         "owned_by": "none", "caused_by": cb("original"), "family": "N-log-flood", "cm_kind": "new-refusal"},
+        {"group": "R9-HOTFIX-M", "hotfix": True, "files": ["tools/x.py"], "found_by": "ci-main",
+         "caused_by": cb("external"), "rca": [rca], "family": "N-staleness", "cm_kind": "delete"},
+        {"group": "R9-KID", "parent": "R9-OUT"},
+        {"group": "R9-GRANDKID", "parent": "R9-KID", "follows": "R9-HOTFIX-A"},
+        {"group": "R9-PLAIN"},
+    ]
+
+
+def self_test() -> int:
+    fails = []
+
+    def check(name, ok):
+        print(("ok    " if ok else "FAIL  ") + name)
+        if not ok:
+            fails.append(name)
+
+    with tempfile.TemporaryDirectory() as tmp:
+        empty = Path(tmp, "empty")
+        empty.mkdir()
+        got = report(load_dir(empty), None)
+        check("NULL: an empty input directory prints unread and no value",
+              got == ["loop_ledger unread (no wave-r<N>-groups.json roster)"])
+        fx = _fixture()
+        got = reads(fx, fx)
+        check("a fully recorded roster reads every line",
+              got[0] == "escapes 2 by found_by {outside: 1, owner: 1} by owned_by {D8: 1, none: 1}"
+              and got[1].startswith("injected 1 (external 0, original 1;")
+              and got[2] == "refix 1; R9-GRANDKID follows R9-HOTFIX-A"
+              and got[3] == ("loop countermeasures 3 by family {N-log-flood: 2, N-staleness: 1} "
+                             "by cm_kind {delete: 1, narrow: 1, new-refusal: 1}; k 0.33; "
+                             "generations g0:3 g1:1(0.33) g2:1(1.00)"))
+        for drop, line in (("owned_by", 0), ("caused_by", 1), ("family", 3)):
+            g2 = [dict(g) for g in fx]
+            del g2[1][drop]
+            got2 = reads(g2, g2)
+            check(f"NULL: one escape without {drop} turns read {line} unread naming it, never a partial value",
+                  got2[line].endswith("unread (1 of 2 owing groups unrecorded: R9-HOTFIX-A)")
+                  if line < 2 else "unread (1 of 3 owing groups unrecorded: R9-HOTFIX-A)" in got2[line])
+            check(f"... and refix, which needs the whole ledger, is unread too, the other reads unchanged ({drop})",
+                  "refix unread (1 of 3" in got2[2]
+                  and all(got2[i] == got[i] for i in range(4) if i not in (2, line)
+                          and not (drop == "caused_by" and i == 3)))
+        g3 = [dict(g) for g in fx]
+        g3[0]["found_by"] = "nobody"
+        check("a value outside the vocabulary is unrecorded", "escapes unread (1 of 2" in reads(g3, g3)[0])
+        g5 = [dict(g) for g in fx]
+        g5[2]["family"] = "N-no-such-class"
+        check("a countermeasure whose family is no bug class reads loop unread, never the word",
+              reads(g5, g5)[3] == "loop unread (1 of 3 owing groups unrecorded: R9-HOTFIX-M)")
+        g4 = [dict(g) for g in fx]
+        g4[2]["found_by"] = "ci"
+        check("a non-escape hotfix owes found_by: refix reads unread, escapes stay read",
+              "refix unread (1 of 3 owing groups unrecorded: R9-HOTFIX-M)" == reads(g4, g4)[2]
+              and reads(g4, g4)[0] == got[0])
+        check("owned_split splits by dimension, and is unread with an unrecorded escape",
+              owned_split(fx, {g["group"] for g in fx}) == "by owning dimension {D8: 1, none: 1}"
+              and owned_split(g3[:1] + [{"group": "X", "source": "outside"}], {"X", "R9-OUT"})
+              .startswith("by owning dimension unread (1 of 2"))
+        x = fx[0]
+        cm, kid = {**fx[0], "group": "R9-CM"}, {"group": "R10-KID", "parent": "R9-CM"}
+        check("k counts a countermeasure's children in every period, not only its own",
+              reads([cm], [cm, kid])[3].endswith("k 1.00; generations g0:1"))
+        stray = [*fx, {"group": "R9-STRAY", "follows": "R9-NO-SUCH-GROUP"}]
+        check("refix counts only a follows naming a roster group",
+              reads(stray, stray)[2] == "refix 1; R9-GRANDKID follows R9-HOTFIX-A")
+        check("a group with no entry time falls in the week unentered",
+              "week unentered" in report([(9, "a", {"groups": [x]})], {}))
+        check("a group carried into a later roster is counted once in its week",
+              report([(9, "a", {"groups": [x]}), (10, "b", {"groups": [x]})], {"R9-OUT": 0})[-4]
+              .startswith("  escapes 1 "))
+        check("an unrecorded list names its first five groups, and an ellipsis only past five",
+              _unread("x", list("ABCDE"), 9) == "x unread (5 of 9 owing groups unrecorded: A, B, C, D, E)"
+              and _unread("x", list("ABCDEF"), 9) == "x unread (6 of 9 owing groups unrecorded: A, B, C, D, E ...)")
+        check("owed: a plain group owes nothing; a machinery hotfix owes no owned_by",
+              owed({"group": "P"}) == () and owed(fx[2]) == ("found_by", "caused_by", "family", "cm_kind"))
+        check("generation: a cycle and a missing parent are None",
+              generation({"group": "A", "parent": "B"}, {"B": {"group": "B", "parent": "A"},
+                                                         "A": {"group": "A", "parent": "B"}}) is None
+              and generation({"group": "A", "parent": "Z"}, {}) is None)
+        # history: a two-commit repository, so the week split is driven, not assumed
+        sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
+        from throwaway_git import throwaway_git_environ, throwaway_git_init
+        repo = Path(tmp, "repo")
+        rdir = repo / roster_lib.ROSTERS_DIR
+        rf = rdir / "wave-r9-groups.json"
+        with throwaway_git_environ():
+            throwaway_git_init(repo, "-q")
+            rdir.mkdir(parents=True)
+            for f, groups, stamp in ((rf, fx[:3], "2026-11-02T12:00:00Z"), (rf, fx, "2026-11-10T12:00:00Z"),
+                                     (rdir / "wave-r10-groups.json", fx[:1], "2026-11-17T12:00:00Z")):
+                f.write_text(json.dumps({"groups": groups}, indent=1))
+                subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
+                subprocess.run(["git", "commit", "-q", "-m", "r"], cwd=repo, check=True, capture_output=True,
+                               env={**os.environ, "GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp})
+            ros, when = load_ref(str(repo), "HEAD")
+        lines = report(ros, when)
+        check("history: each group's week is its first roster entry, carried into a later roster or not",
+              when is not None and week_of(when["R9-OUT"]) == "2026-W45" and week_of(when["R9-KID"]) == "2026-W46"
+              and "week 2026-W47" not in lines
+              and "week 2026-W45" in lines and "week 2026-W46" in lines
+              and lines[lines.index("week 2026-W46") + 1] == "  escapes 0 by found_by {} by owned_by {}")
+        check("--dir has no history: its weeks are unread",
+              report(load_dir(rdir), None)[-1].startswith("weeks unread"))
+    print(f"loop_ledger self-test: {len(fails)} failed")
+    return 1 if fails else 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/tools/audit/seat/roster_edit.py b/tools/audit/seat/roster_edit.py
index 9d16a3cf52..a0105cef96 100644
--- a/tools/audit/seat/roster_edit.py
+++ b/tools/audit/seat/roster_edit.py
@@ -16,7 +16,8 @@
     python3 tools/audit/seat/roster_edit.py set-size    <group> <size> [--cite <ref>@<sha>]
     python3 tools/audit/seat/roster_edit.py set-price   <group> <minutes> --price-cite <the owner's words>
     python3 tools/audit/seat/roster_edit.py set-source  <group> <outside | ->
-    python3 tools/audit/seat/roster_edit.py set-field   <group> <source|hotfix|hotfix_by|savings|savings_source|class|gates_finders> <value>
+    python3 tools/audit/seat/roster_edit.py set-field   <group> <source|hotfix|hotfix_by|savings|savings_source|class|gates_finders
+                                                         |found_by|owned_by|caused_by|family|cm_kind|parent|follows> <value>
     python3 tools/audit/seat/roster_edit.py set-files   <group> [--add <path>...] [--set-files <p,p | ->]
         [--set-hot <p,p | ->] [--cite <ref>@<sha>]
         [--at-sha SHA] [--checkout DIR] [--roster-ref BR] [--branch OUT]
@@ -460,7 +461,7 @@ def op_append_group(roster, json_file, rel="", sizes=(), reason=None):
 
 
 #: `set-field`'s fields (P268): the per-group mapping the CI-priority rule reads through roster_lib.
-SET_FIELDS = ("source", "hotfix", "hotfix_by", "savings", "savings_source", "class", "gates_finders")
+SET_FIELDS = ("source", "hotfix", "hotfix_by", "savings", "savings_source", "class", "gates_finders") + roster_lib.CONVERGENCE_FIELDS
 CITATION = re.compile(r"^[\w./-]+\.md#\w+$")
 REQUIRED_CONTEXTS = Path(__file__).resolve().parents[3] / "tools" / "policy" / "fixtures" / "required-contexts.json"
 
@@ -530,6 +531,14 @@ def op_set_field(roster, group, field, raw):
         if not CITATION.match(raw):
             raise Refuse("set-field: savings_source is a citation, dev/programme/triage/<batch>.md#P<n>")
         new = raw
+    elif field in roster_lib.CONVERGENCE_FIELDS:
+        try:
+            new = json.loads(raw) if field == "caused_by" else raw
+        except ValueError:
+            raise Refuse("set-field: caused_by must be a JSON object {cause, rca}")
+        why = roster_lib.convergence_why(field, new, g, {x.get("group") for x in roster.get("groups", [])})
+        if why:
+            raise Refuse(f"set-field: {why}")
     elif field == "source":
         if raw not in roster_lib.SOURCES:
             raise Refuse(f"set-field: {raw!r} is not a source; one of {', '.join(roster_lib.SOURCES)}")
@@ -1355,11 +1364,9 @@ def write_roster(checkout, ref, branch, worktree, roster_path, msg, push,
                             "origin", refspec],
                            capture_output=True, text=True)
         if r.returncode == 0:
-            # our own push: the tracking ref must follow it, or the next op
-            # in this run finds HEAD on no origin ref
-            subprocess.run(["git", "-C", str(checkout), "update-ref",
-                            f"refs/remotes/origin/{branch}", head],
-                           capture_output=True)
+            # No tracking-ref write here: every caller (main, roster_queue's
+            # batch, roster_sync) runs fetch_origin before write_roster, which
+            # moves origin/<branch> to this push for the next op.
             print(f"pushed {branch} at {head}")
             return 0
         why = (r.stderr or r.stdout).strip()[:400]
@@ -2237,6 +2244,70 @@ def _self_test() -> int:
           refuses("gates_finders is true or false", "set-field", "R9-S2", "gates_finders", rest=("yes",)) and tip() == t0)
     check("set-field class is accepted",
           edit("set-field", "R9-S2", "class", rest=("docs",)) == 0 and grp("R9-S2")["class"] == "docs")
+    # The convergence record (P7, L1): closed words, written through roster_lib.convergence_why.
+    t0 = tip()
+    check("set-field found_by, owned_by, family, cm_kind, parent, follows: each closed word reads back",
+          all(edit("set-field", "R9-S3", f, rest=(v,)) == 0 and grp("R9-S3")[f] == v for f, v in (
+              ("found_by", "owner"), ("owned_by", "D8"), ("family", "N-log-flood"),
+              ("cm_kind", "narrow"), ("parent", "R9-S2"), ("follows", "R9-S1"))))
+    # Both sides of the #3633/#3657 merge: a resolution dropping either SET_FIELDS half or its usage words fails here.
+    check("set-field gates_finders and a convergence field in one run: both read back, both in the usage line",
+          edit("set-field", "R9-S3", "gates_finders", rest=("true",)) == 0
+          and edit("set-field", "R9-S3", "found_by", rest=("reviewer",)) == 0
+          and grp("R9-S3")["gates_finders"] is True and grp("R9-S3")["found_by"] == "reviewer"
+          and all(f"|{f}" in __doc__ for f in ("gates_finders",) + roster_lib.CONVERGENCE_FIELDS))
+    t0 = tip()
+    check("set-field refuses a word outside each vocabulary and an unknown group, moving nothing",
+          refuses("finder dimension", "set-field", "R9-S3", "found_by", rest=("ci",))
+          and refuses("nor none", "set-field", "R9-S3", "owned_by", rest=("D99",))
+          and refuses("bugclasses", "set-field", "R9-S3", "family", rest=("N-nope",))
+          and refuses("cm_kind", "set-field", "R9-S3", "cm_kind", rest=("fix",))
+          and refuses("no other roster group", "set-field", "R9-S3", "parent", rest=("R9-S3",))
+          and refuses("no other roster group", "set-field", "R9-S3", "follows", rest=("R9-ZZ",))
+          and tip() == t0)
+    check("set-field caused_by is refused with no root-cause record of the group, and read back with its own",
+          refuses("rca record under", "set-field", "R9-S3", "caused_by",
+                  rest=('{"cause": "#3520", "rca": "R10-N-log-flood"}',))
+          and refuses("{cause, rca}", "set-field", "R9-S3", "caused_by", rest=("#3520",))
+          and tip() == t0
+          and edit("append-group", "R9-S4", new_group("R9-S4", source="audit", rca=["R10-N-log-flood"])) == 0
+          and edit("set-field", "R9-S4", "caused_by",
+                   rest=('{"cause": "R9-S3", "rca": "R10-N-log-flood"}',)) == 0
+          and grp("R9-S4")["caused_by"] == {"cause": "R9-S3", "rca": "R10-N-log-flood"})
+    # An escape that started with no rca: caused_by is written once a planted root-cause
+    # record declares it its subject (a status row naming it is refused), and the ledger's injected and refix then read values (verdict/3657).
+    import loop_ledger
+    edit("append-group", "R9-ESC", new_group("R9-ESC", source="outside"))
+    vroot = Path(tmp, "vocab")
+    for rel, text in (("dev/governance/dimensions/D8.md", "x\n"), ("dev/audit/rca/R10-N-log-flood.md", "x\n"),
+                      ("dev/audit/rca/R10-RCA-PLANT.md", "Root cause of R9-ESC, merged in #3520.\n"),
+                      ("dev/audit/rca/R10-RCA-BOARD.md", "# R10-RCA-BOARD: a process record\n\nWhy the board"
+                       " stalled.\n\n| group | state |\n|---|---|\n| R9-ESC | dispatched |\n"),
+                      ("dev/audit/config/bugclasses.json", '{"N-log-flood": {}}')):
+        (vroot / rel).parent.mkdir(parents=True, exist_ok=True)
+        (vroot / rel).write_text(text, encoding="utf-8")
+    keep_root, roster_lib._ROOT = roster_lib._ROOT, vroot
+    try:
+        def ledger():
+            every = branch_roster()["groups"]
+            return loop_ledger.reads([grp("R9-ESC")], every)
+        set_ok = all(edit("set-field", "R9-ESC", f, rest=(v,)) == 0 for f, v in (("found_by", "owner"),
+                                                                              ("owned_by", "D8")))
+        before = ledger()
+        t0 = tip()
+        refused = refuses("rca record under", "set-field", "R9-ESC", "caused_by",
+                          rest=('{"cause": "#3520", "rca": "R10-N-log-flood"}',)) and tip() == t0
+        refused = refused and refuses("rca record under", "set-field", "R9-ESC", "caused_by",
+                                      rest=('{"cause": "#3520", "rca": "R10-RCA-BOARD"}',)) and tip() == t0
+        wrote = edit("set-field", "R9-ESC", "caused_by", rest=('{"cause": "#3520", "rca": "R10-RCA-PLANT"}',)) == 0
+        after = ledger()
+    finally:
+        roster_lib._ROOT = keep_root
+    check("set-field caused_by on a group with no rca: admitted by a record declaring it its subject, not a status row, and injected and refix read",
+          set_ok and "rca" not in grp("R9-ESC") and refused and wrote
+          and before[1].startswith("injected unread (1 of 1") and before[2].startswith("refix unread (1 of 1")
+          and after[1].startswith("injected 1 (external 0, original 0;") and after[2] == "refix 0",
+          f"{before[1:3]} {after[1:3]}")
 
     # set-size / set-files (R10-ROSTER-OPS-2 part 1): one op pair for the
     # carries that asked for set-size (with and without a cite), set-files
diff --git a/tools/audit/seat/roster_lib.py b/tools/audit/seat/roster_lib.py
index ae7e56b659..c7b02453a2 100644
--- a/tools/audit/seat/roster_lib.py
+++ b/tools/audit/seat/roster_lib.py
@@ -860,6 +860,106 @@ def touches_production(group: dict) -> bool:
             or any(str(f).startswith("custom_components/") for f in group.get("files") or []))
 
 
+#: The convergence record (decision 0018 sections 2 and 4; process cards P7 and
+#: L1): what found an escape, which dimension owns it, what caused it, its
+#: symptom family, the countermeasure's kind, the group it descends from and
+#: the fix a re-report follows. `roster_edit.py set-field` writes each through
+#: `convergence_why`; `loop_ledger.py` reads them back.
+CONVERGENCE_FIELDS = ("found_by", "owned_by", "caused_by", "family", "cm_kind", "parent", "follows")
+#: `found_by` besides a finder dimension `D<n>` (card P7's list).
+FOUND_BY = ("reviewer", "ci-main", "owner", "outside")
+#: `caused_by.cause` besides a pull request `#<n>` or a roster group (card L1).
+CAUSES = ("external", "original")
+#: `cm_kind`, the countermeasure's kind (card L1's closed vocabulary).
+CM_KINDS = ("delete", "self-heal", "narrow", "widen", "new-refusal", "policy-text")
+_ROOT = Path(__file__).resolve().parents[3]
+_DIM = re.compile(r"\AD\d{1,2}\Z")
+_PR = re.compile(r"\A#[1-9]\d*\Z")
+_RCA_ID = re.compile(r"\A[A-Za-z0-9][\w-]*(?:\.[\w-]+)*\Z")  # a file stem, never a path
+
+
+def _dimension(word, root) -> bool:
+    """A finder dimension: `D<n>` with its brief under dev/governance/dimensions/."""
+    return isinstance(word, str) and bool(_DIM.match(word)) and (root / "dev/governance/dimensions" / f"{word}.md").is_file()
+
+
+def _bug_families(root) -> set:
+    try:
+        return set(json.loads((root / "dev/audit/config/bugclasses.json").read_text()))
+    except (OSError, ValueError, TypeError):
+        return set()
+
+
+def rca_lists(rca, group: dict, root=None) -> bool:
+    """Whether dev/audit/rca/<rca>.md is a root-cause record of `group`: the file
+    exists, and its id is one of the group's own `rca` records (the group is its
+    countermeasure; round 9's rosters hold a bool there, which lists no id) or the
+    group is one of `rca_subjects` of its text (the group is the defect it analyses;
+    a name in the record's body, a status table or a countermeasure line, is not).
+    `root` defaults to the repository at call time."""
+    if not isinstance(rca, str) or not _RCA_ID.match(rca):
+        return False
+    try:
+        text = ((root or _ROOT) / "dev/audit/rca" / f"{rca}.md").read_text(encoding="utf-8")
+    except (OSError, UnicodeDecodeError):
+        return False
+    me, own = group.get("group"), group.get("rca")
+    return (isinstance(own, list) and rca in own) or me in rca_subjects(text)
+
+
+def rca_subjects(text: str) -> set:
+    r"""The names a root-cause record declares as its subject: the whole tokens
+    (`[\w.-]+` runs, trailing dots and dashes stripped) of its opening block, which
+    is its first paragraph, and the one after it when the first is a one-line `# `
+    title, less any table row. A record states there what it analyses ("This is the root-cause seat for <group>", "beside <group>", a title's
+    "(<group>)"); a group it mentions later is a sibling, a countermeasure or a
+    dispatch-status row, which the record does not analyse (verdict/3657)."""
+    paras = [p for p in re.split(r"\n[ \t]*\n", text.strip()) if p.strip()]
+    title = bool(paras) and paras[0].startswith("# ") and "\n" not in paras[0]
+    block = [ln for p in paras[:2 if title else 1] for ln in p.splitlines() if not ln.lstrip().startswith("|")]
+    return {t.strip(".-") for t in re.findall(r"[\w.-]+", "\n".join(block))}
+
+
+def convergence_why(field: str, value, group: dict, names, root=None) -> "str | None":
+    """Why `value` is no admissible `field` of `group`, else None. `names` is every
+    group name the reader can see (the cause, parent and follows targets).
+    `caused_by` is {cause, rca}: `rca_lists(rca, group)`, so the cause is the
+    root-cause seat's record and never the fixer's (decision 0018 section 2,
+    `injected`), and a defect group with no `rca` of its own takes one once a
+    record under dev/audit/rca/ declares it as its subject (`rca_subjects`). `root` defaults to the repository."""
+    root = root or _ROOT
+    me = group.get("group")
+    if field == "found_by":
+        return None if value in FOUND_BY or _dimension(value, root) else (
+            f"found_by {value!r} is neither a finder dimension D<n> nor one of {', '.join(FOUND_BY)}")
+    if field == "owned_by":
+        return None if value == "none" or _dimension(value, root) else (
+            f"owned_by {value!r} is neither a dimension D<n> nor none")
+    if field == "family":
+        return None if value in _bug_families(root) else (
+            f"family {value!r} is no class of dev/audit/config/bugclasses.json")
+    if field == "cm_kind":
+        return None if value in CM_KINDS else f"cm_kind {value!r} is none of {', '.join(CM_KINDS)}"
+    if field in ("parent", "follows"):
+        return None if value in names and value != me else f"{field} {value!r} is no other roster group"
+    if field != "caused_by":
+        return f"{field!r} is no convergence field"
+    if not isinstance(value, dict) or set(value) != {"cause", "rca"}:
+        return "caused_by must be a JSON object {cause, rca}"
+    cause, rca = value["cause"], value["rca"]
+    if not (cause in CAUSES or (isinstance(cause, str) and _PR.match(cause)) or (cause in names and cause != me)):
+        return f"caused_by cause {cause!r} is no pull request #<n>, other roster group, or one of {', '.join(CAUSES)}"
+    if not rca_lists(rca, group, root):
+        return (f"caused_by rca {rca!r} is no rca record under dev/audit/rca/ that is the group's own"
+                f" or declares {me} its subject")
+    return None
+
+
+def recorded(group: dict, fields, names, root=None) -> bool:
+    """Whether every field of `fields` is present on the group and admissible."""
+    return all(f in group and convergence_why(f, group[f], group, names, root) is None for f in fields)
+
+
 def savings_h(group: dict) -> "float | None":
     """The group's recorded saving in hours (`savings`), or None when it is absent or not a number."""
     v = group.get("savings") if isinstance(group, dict) else None
@@ -870,7 +970,7 @@ def _replan_production(group: dict) -> bool:
     """Whether replan.py puts the group in one of its PRODUCTION lanes; False when replan is unreadable."""
     import importlib.util
     try:
-        path = Path(__file__).resolve().parents[2] / "tools" / "plan" / "replan.py"
+        path = _ROOT / "tools" / "plan" / "replan.py"
         spec = importlib.util.spec_from_file_location("replan_lanes_for_roster_lib", path)
         mod = importlib.util.module_from_spec(spec)
         spec.loader.exec_module(mod)
@@ -1272,7 +1372,69 @@ def _self_test() -> int:
         check("P268 readers: group_class is the class when present, lane-derived only when absent",
               group_class({"group": "X", "class": "instrument", "lane": "CORE"}) == "instrument"
               and group_class({"group": "X", "class": "production"}) == "production"
-              and group_class({"group": "X"}) in ("production", "instrument"))
+              and group_class({"group": "X"}) == "production"
+              and group_class({"group": "X", "files": ["tools/audit/seat/x.py"]}) == "instrument")
+        # a fixture root, so the vocabulary is read from planted files and never the tree's
+        froot = Path(td) / "vocab"
+        for rel in ("dev/governance/dimensions/D3.md", "dev/governance/dimensions/D8.md",
+                    "dev/governance/dimensions/D12.md", "dev/audit/rca/R10-N-log-flood.md",
+                    "dev/audit/rca/R10-N-staleness.md"):
+            (froot / rel).parent.mkdir(parents=True, exist_ok=True)
+            (froot / rel).write_text("x\n")
+        (froot / "dev/audit/rca/R10-RCA-NAMED.md").write_text("Cause of R10-D, found again in R10-E-2.\n")
+        # A process record (verdict/3657's R10-RCA-TICK-BLIND): its title and opening paragraph
+        # declare R10-S its subject; R10-T is a dispatch-status row and R10-U a later mention.
+        (froot / "dev/audit/rca/R10-RCA-STATUS.md").write_text(
+            "# R10-RCA-STATUS: why the board missed a dispatch\n\nThis is the root-cause seat for R10-S.\n"
+            "| group | state |\n|---|---|\n| R10-T | dispatched |\n\n## 1. Cases\n\n"
+            "| group | state |\n|---|---|\n| R10-T | stalled |\n\nR10-U waited on the same board.\n")
+        (froot / "dev/audit/config").mkdir(parents=True)
+        (froot / "dev/audit/config/bugclasses.json").write_text('{"N-log-flood": {}}')
+        cg = {"group": "R10-C", "rca": ["R10-N-log-flood"]}
+        cn = {"R10-C", "R10-P"}
+        cw = lambda f, v, g=cg: convergence_why(f, v, g, cn, froot)  # noqa: E731
+        check("convergence: each closed word is admitted, and its neighbour refused (null control)",
+              all(cw(f, ok) is None and cw(f, bad) for f, ok, bad in (
+                  ("found_by", "D3", "D99"), ("found_by", "ci-main", "ci"), ("owned_by", "none", "None"),
+                  ("owned_by", "D12", "D1x"), ("family", "N-log-flood", "N-no-such-class"),
+                  ("cm_kind", "new-refusal", "refusal"), ("parent", "R10-P", "R10-C"),
+                  ("follows", "R10-P", "R10-ZZ"))))
+        check("convergence: caused_by needs a root-cause record of the group, so the fixer cannot name it",
+              cw("caused_by", {"cause": "#3520", "rca": "R10-N-log-flood"}) is None
+              and cw("caused_by", {"cause": "R10-P", "rca": "R10-N-log-flood"}) is None
+              and cw("caused_by", {"cause": "original", "rca": "R10-N-log-flood"}) is None
+              and "rca record under" in cw("caused_by", {"cause": "#3520", "rca": "R10-N-staleness"})
+              and "rca record under" in cw("caused_by", {"cause": "#1", "rca": "R10-N-log-flood"}, {"group": "G"})
+              and "no pull request" in cw("caused_by", {"cause": "3520", "rca": "R10-N-log-flood"})
+              and "no pull request" in cw("caused_by", {"cause": "R10-C", "rca": "R10-N-log-flood"})
+              and "{cause, rca}" in cw("caused_by", "#3520")
+              and "no convergence field" in cw("source", "user"))
+        # A defect group with no rca of its own: the record that names it is its root-cause record.
+        check("convergence: caused_by admits a record naming a group with no rca, by whole token only",
+              cw("caused_by", {"cause": "#3520", "rca": "R10-RCA-NAMED"}, {"group": "R10-D"}) is None
+              and cw("caused_by", {"cause": "#3520", "rca": "R10-RCA-NAMED"}, {"group": "R10-E-2"}) is None
+              and all("rca record under" in (cw("caused_by", {"cause": "#3520", "rca": "R10-RCA-NAMED"},
+                                                {"group": n}) or "") for n in ("R10", "R10-E", "R10-D-1", "10-D", "G")))
+        check("convergence: caused_by admits only a group the record declares its subject, never a status row",
+              cw("caused_by", {"cause": "original", "rca": "R10-RCA-STATUS"}, {"group": "R10-S"}) is None
+              and all("rca record under" in (cw("caused_by", {"cause": "original", "rca": "R10-RCA-STATUS"},
+                                                {"group": n}) or "") for n in ("R10-T", "R10-U", "R10-RCA-STATUS-X"))
+              and rca_subjects("Cause of R10-D.\n\nR10-T later.\n") == {"Cause", "of", "R10-D"}
+              and rca_subjects("# R10-A\nCause.\n\nR10-T later.\n") == {"R10-A", "Cause"}
+              and rca_subjects("## R10-A\n\nR10-T later.\n") == {"R10-A"}
+              and rca_subjects("") == set())
+        check("convergence: an own rca id whose record file is missing, or a path for an id, is refused",
+              "rca record under" in cw("caused_by", {"cause": "#3520", "rca": "R10-N-gone"},
+                                       {"group": "R10-C", "rca": ["R10-N-gone"]})
+              and rca_lists("R10-N-log-flood", cg, froot) and not rca_lists("R10-N-gone", {"rca": ["R10-N-gone"]}, froot)
+              and not rca_lists("../rca/R10-N-log-flood", {"rca": ["../rca/R10-N-log-flood"]}, froot)
+              and not rca_lists(None, cg, froot)
+              and not rca_lists("R10-N-log-flood", {"group": "R10-C", "rca": True}, froot)
+              and rca_lists("R10-RCA-NAMED", {"group": "R10-D", "rca": True}, froot))
+        check("convergence: recorded needs every named field present and admissible",
+              recorded({**cg, "found_by": "owner", "owned_by": "none"}, ("found_by", "owned_by"), cn, froot)
+              and not recorded({**cg, "found_by": "owner"}, ("found_by", "owned_by"), cn, froot)
+              and not recorded({**cg, "found_by": "nobody", "owned_by": "none"}, ("found_by", "owned_by"), cn, froot))
         check("is_hotfix: kind bug or HOTFIX in the name only",
               is_hotfix({"group": "X", "kind": "bug"}) and is_hotfix({"group": "r10-hotfix-x"})
               and not is_hotfix({"group": "X"}) and not is_hotfix(None))
diff --git a/tools/audit/seat/roster_sync.py b/tools/audit/seat/roster_sync.py
index fd58d0787e..16b4e8459a 100644
--- a/tools/audit/seat/roster_sync.py
+++ b/tools/audit/seat/roster_sync.py
@@ -461,6 +461,28 @@ def finding_words(text: str) -> str:
     return " ".join(MARKUP.sub("", str(text)).lower().split())
 
 
+#: The two wrappers a carry's finding is stored in: the queue's landing
+#: (`carry_audit.land_ops`: `From <pr> (<topic>), body item <id>: <text> (items <id>)`)
+#: and the body's own `Carry: <GROUP>` clause, which the sync's derived text ends with.
+QUEUED_PREFIX = re.compile(r"\AFrom [^:]*?, body item [0-9a-f]{8}: ")
+ITEMS_TAG = re.compile(r"\s*\(items? [0-9a-f]{8}(?:[ ,]+[0-9a-f]{8})*\)\s*\Z")
+CARRY_CLAUSE = re.compile(r"\s*Carry:\s*[^\s()]+\s*\Z")
+ITEM_ID = re.compile(r"\bbody item ([0-9a-f]{8})\b|\(items? ([0-9a-f]{8}(?:[ ,]+[0-9a-f]{8})*)\)")
+
+
+def finding_core(text: str) -> str:
+    """`finding_words` of <text> with the queue's `From ..., body item <id>: `
+    prefix, its `(items <id>)` tag and the trailing `Carry: <GROUP>` clause
+    stripped: the finding one body item records, however it was landed."""
+    t = QUEUED_PREFIX.sub("", " ".join(str(text).split()))
+    return finding_words(CARRY_CLAUSE.sub("", ITEMS_TAG.sub("", t)))
+
+
+def item_ids(text: str) -> set[str]:
+    """The carry_audit body-item ids <text> names as a landing's own tag."""
+    return {i for a, b in ITEM_ID.findall(str(text)) for i in (a, *b.replace(",", " ").split()) if i}
+
+
 def rulings(text: str) -> set[tuple[str, str]]:
     """(round, item) for every triage ruling <text> cites, in the resolvable
     form (`triage: <file>#P<n>`) or the routing seat's prose form
@@ -480,7 +502,7 @@ def rulings(text: str) -> set[tuple[str, str]]:
     return out
 
 
-def already_carried(carries: list, text: str) -> str | None:
+def already_carried(carries: list, text: str, item: str | None = None) -> str | None:
     """The destination carry that records this same finding, or None.
 
     The key is the finding, never the pull request (#2889's B1): one pull
@@ -489,16 +511,18 @@ def already_carried(carries: list, text: str) -> str | None:
     a number in prose (`a second instance beside #2447's`) matches it too. Two
     records are the same finding when they cite the same triage ruling, or
     when their substantive text is equal once markup and whitespace are
-    normalised. A derived copy
+    normalised (`finding_core`: the queue's landing and the body's own
+    `Carry:` clause are wrappers, not the finding), or when the carry is tagged
+    with the body item's own carry_audit id `item`. A derived copy
     the destination already holds is refused before the write path's triage
     gate sees it: that gate refuses an unresolvable `triage P<n>` citation,
     and `write_roster` is atomic, so the duplicate would abort the stage
     changes that stop it being re-derived.
     """
-    want = finding_words(text)
+    want = finding_core(text)
     want_rulings = rulings(text)
     for c in carries:
-        if finding_words(c) == want:
+        if (want and finding_core(c) == want) or (item and item in item_ids(c)):  # mut:dupkey
             return str(c)
         if want_rulings & rulings(c):
             return str(c)
@@ -542,7 +566,7 @@ def carry_plan(roster: dict, transitions: list[PR], repo: str,
                     text = " ".join(BULLET.sub("", row["text"], count=1).split())
                     if text in (g.get("carry") or []) or (dest, text) in appends:
                         continue
-                    held = already_carried(g.get("carry") or [], text)
+                    held = already_carried(g.get("carry") or [], text, row["id"])
                     if held is not None:
                         refusals.append((pr.number, dest,
                                          "already carried (the same finding, "
@@ -1080,6 +1104,18 @@ def self_test() -> int:
          "after": [], "brief": "echo",
          "carry": ["the widget parser drops a unit. `Carry: R9-ECHO`"],
          "resume": {"stage": "not-started"}},
+        # The queue landed #15's item first, wrapped as carry_audit.land_ops
+        # writes it: the sync's own derived text is that finding again.
+        {"group": "R9-QUEUED", "lane": "L1", "issues": [], "fixes": [],
+         "after": [], "brief": "queued",
+         "carry": ["From #15 (r9-carry), body item 0badc0de: the queue landed "
+                   "this first. Carry: R9-QUEUED (items 0badc0de)"],
+         "resume": {"stage": "not-started"}},
+        # The queue's landing reworded, so only its `(items <id>)` tag, the
+        # body item's carry_audit id (set below, from BODY), names the item.
+        {"group": "R9-QID", "lane": "L1", "issues": [], "fixes": [],
+         "after": [], "brief": "qid", "carry": [],
+         "resume": {"stage": "not-started"}},
         # The done hold: #88 is open and only R9-HOLD lists it; #89 is closed.
         {"group": "R9-HOLD", "lane": "L1", "issues": [88], "fixes": [],
          "after": [], "brief": "hold",
@@ -1104,7 +1140,15 @@ def self_test() -> int:
             "- the prose control: a distinct finding for a destination that "
             "only mentions the number. Carry: R9-PROSE\n\n"
             "- the widget parser drops a unit. Carry: R9-ECHO\n\n"
+            "- the queue landed this first. Carry: R9-QUEUED\n\n"
+            "- a distinct finding for the queued group. Carry: R9-QUEUED\n\n"
+            "- the sync's words for the queued item. Carry: R9-QID\n\n"
             "- an issue keeps its own record. Carry: #77\n")
+    qid = next(r["id"] for r in carry_audit.audit(BODY, [], carry_audit.Dests(ROSTER_FIXTURE, set()))["rows"]
+               if "R9-QID" in r["dests"])
+    qid_landing = (f"From #15 (r9-carry), body item {qid}: reworded when the queue "
+                   f"landed it. Carry: R9-QID (items {qid})")
+    next(g for g in groups if g["group"] == "R9-QID")["carry"] = [qid_landing]
     PRS = [
         {"number": 11, "state": "MERGED", "headRefName": "fix/r9-live-pr",
          "mergeCommit": {"oid": "a" * 40}, "body": "## Friction\n\n- none\n"},
@@ -1244,6 +1288,16 @@ def self_test() -> int:
                   "the prose control: a distinct finding for a destination "
                   "that only mentions the number. Carry: R9-PROSE"],
               by["R9-PROSE"].get("carry"))
+        check("the queue's landing of the same item is not appended again: "
+              "its prefix, tag and Carry clause stripped, the text is equal",
+              by["R9-QUEUED"].get("carry")
+              == ["From #15 (r9-carry), body item 0badc0de: the queue landed "
+                  "this first. Carry: R9-QUEUED (items 0badc0de)",
+                  "a distinct finding for the queued group. Carry: R9-QUEUED"],
+              by["R9-QUEUED"].get("carry"))
+        check("a reworded queue landing tagged with the item's own id is not "
+              "appended again", by["R9-QID"].get("carry") == [qid_landing],
+              by["R9-QID"].get("carry"))
         check("a duplicate differing only in markup is not appended",
               by["R9-ECHO"].get("carry")
               == ["the widget parser drops a unit. `Carry: R9-ECHO`"],
diff --git a/tools/audit/seat/scorecard.py b/tools/audit/seat/scorecard.py
index b085052570..9734385d6d 100644
--- a/tools/audit/seat/scorecard.py
+++ b/tools/audit/seat/scorecard.py
@@ -50,7 +50,9 @@ THE LINES (rule, then the null control the self-test holds it to):
   E        escapes: roster groups whose source is `outside`, and hotfix or bug
            groups (group names HOTFIX, or kind bug|hotfix) whose files include
            the product (`custom_components/`); and how many of both are still
-           open (resume.stage not `done`).
+           open (resume.stage not `done`); beside them both sets split by
+           owning dimension (`owned_by`, card P7), unread while any of them
+           has none (loop_ledger.owned_split).
            NULL: a round with no escape adds none.
   C        detection delay: the longest run of consecutive cancelled main runs
            in the last 50 runs (cancelled runs included, ordered by stamp).
@@ -162,13 +164,31 @@ def line_hotfix(rows: list[dict]) -> str:
             f"production merges among them {prod}  (naming measure, no null control)")
 
 
-def line_escapes(groups: list[dict]) -> str:
+def escape_sets(groups: list[dict]) -> tuple[list, list]:
+    """Line E's two sets, which loop_ledger.py reads as the escapes: outside groups, and
+    hotfix or bug groups touching the product."""
     out = [x for x in groups if x.get("source") == "outside"]
     ph = [x for x in groups if ("HOTFIX" in x["group"] or x.get("kind") in ("bug", "hotfix"))
           and any(f.startswith("custom_components/") for f in (x.get("files") or []))]
+    return out, ph
+
+
+def owned_split(groups: list[dict]) -> str:
+    """loop_ledger.owned_split, imported here so this module's mutant copies, which run
+    without their siblings, still load: there the split prints unread."""
+    sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I drops the script's directory
+    try:
+        import loop_ledger
+    except ImportError:
+        return "by owning dimension unread (no loop_ledger.py beside scorecard.py)"
+    return loop_ledger.owned_split(groups, {x.get("group") for x in groups})
+
+
+def line_escapes(groups: list[dict]) -> str:
+    out, ph = escape_sets(groups)
     openn = sum((x.get("resume") or {}).get("stage") != "done" for x in out + ph)
     return (f"E       roster groups from outside reports {len(out)}; hotfix or bug groups touching the product "
-            f"{len(ph)}; open among both {openn}")
+            f"{len(ph)}; open among both {openn}; " + owned_split(groups))
 
 
 def cancel_streak(runs: list) -> int:
diff --git a/tools/audit/seat/scorecard_selftest.py b/tools/audit/seat/scorecard_selftest.py
index 3320eb4785..5c6abf5e86 100644
--- a/tools/audit/seat/scorecard_selftest.py
+++ b/tools/audit/seat/scorecard_selftest.py
@@ -101,6 +101,10 @@ def cases(sc) -> dict[str, bool]:
     e = sc.line_escapes(g)
     r["E planted: one outside, two product hotfix or bug groups, two open"] = "outside reports 1;" in e and "product 2;" in e and "open among both 2" in e
     r["E null: a round with no escape adds none"] = "reports 0; hotfix or bug groups touching the product 0; open among both 0" in sc.line_escapes([{"group": "D"}])
+    r["E split: unread, naming the count, while an escape records no owning dimension"] = "by owning dimension unread (3 of 3 owing groups unrecorded" in e
+    g[0]["owned_by"], g[1]["owned_by"], g[2]["owned_by"] = "D8", "none", "D8"
+    r["E split: by owning dimension once every escape records one"] = "by owning dimension {D8: 2, none: 1}" in sc.line_escapes(g)
+    r["E split null: a round with no escape splits none"] = sc.line_escapes([{"group": "D"}]).endswith("by owning dimension {}")
     # C / K
     cn = sc.line_ck(runs([("success", 1)] * 4), "all fine\n")
     r["C, K null: no cancelled run and no recycle line are both 0"] = "C 0; K 0" in cn
diff --git a/tools/ci/selftest_closures.json b/tools/ci/selftest_closures.json
index 2a07bf3bd8..411ecc31e2 100644
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
@@ -248,6 +249,7 @@
     "tools/audit/seat/hooks/**",
     "tools/audit/seat/hooks_setup.py",
     "tools/audit/seat/ledger.py",
+    "tools/audit/seat/loop_ledger.py",
     "tools/audit/seat/merge_pr.sh",
     "tools/audit/seat/merge_train.py",
     "tools/audit/seat/moved_paths.py",
@@ -263,6 +265,7 @@
     "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
+    "tools/audit/seat/plan_phases.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
     "tools/audit/seat/plant_recall.py",
@@ -2823,6 +2826,7 @@
    "run_sha": "8e2afa7d1084b7223a39f0ef593e419b78e3a724781a06ccb99196801427962a",
    "files": [
     "dev/governance/config/machinery_budgets.json",
+    "dev/governance/config/machinery_target_budgets.json",
     "dev/governance/config/policy_budgets.json",
     "tests/ci_budgets.json",
     "tests/coverage_budgets.json",
@@ -3825,6 +3829,7 @@
     "dev/governance/config",
     "dev/governance/decisions",
     "dev/governance/dimensions",
+    "dev/governance/dimensions/criteria",
     "dev/governance/roles",
     "dev/governance/rules",
     "dev/programme",
@@ -3835,6 +3840,7 @@
     "dev/programme/round10",
     "dev/programme/round10/rechain",
     "dev/programme/round10/state",
+    "dev/programme/round11",
     "dev/programme/round9",
     "dev/programme/round9/state",
     "dev/programme/triage",
@@ -3943,6 +3949,7 @@
     "tests/mutation_ledger/killed_by/services.py",
     "tests/mutation_ledger/killed_by/setpoint_check.py",
     "tests/mutation_ledger/killed_by/silent_mode.py",
+    "tests/mutation_ledger/killed_by/slab_seed.py",
     "tests/mutation_ledger/killed_by/slot_drivers.py",
     "tests/mutation_ledger/killed_by/snapshots.py",
     "tests/mutation_ledger/killed_by/store.py",
@@ -3985,6 +3992,7 @@
     "tests/mutation_ledger/survivor_triage/quiet_windows.py",
     "tests/mutation_ledger/survivor_triage/repairs.py",
     "tests/mutation_ledger/survivor_triage/sensor.py",
+    "tests/mutation_ledger/survivor_triage/slab_seed.py",
     "tests/mutation_ledger/survivor_triage/slot_drivers.py",
     "tests/mutation_ledger/survivor_triage/store.py",
     "tests/mutation_ledger/survivor_triage/sysid.py",
@@ -4067,7 +4075,10 @@
     "tools/audit/seat/roster_lib.py"
    ],
    "probes": [
-    "."
+    ".",
+    "tools",
+    "tools/audit",
+    "tools/audit/seat"
    ],
    "dirs": [],
    "index": false,
@@ -4160,6 +4171,7 @@
     "tools/audit/archscore/gate.py",
     "tools/audit/carry_audit.py",
     "tools/audit/check_scopes.py",
+    "tools/audit/enumerate.py",
     "tools/audit/fold_ledger.py",
     "tools/audit/machinery_ratchet.py",
     "tools/audit/merge_fastpath.py",
@@ -4198,6 +4210,7 @@
     "tools/audit/seat/heartbeat.sh",
     "tools/audit/seat/hooks_setup.py",
     "tools/audit/seat/ledger.py",
+    "tools/audit/seat/loop_ledger.py",
     "tools/audit/seat/merge_pr.sh",
     "tools/audit/seat/merge_train.py",
     "tools/audit/seat/moved_paths.py",
@@ -4213,6 +4226,7 @@
     "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
+    "tools/audit/seat/plan_phases.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
     "tools/audit/seat/plant_recall.py",
@@ -4526,6 +4540,7 @@
   "gantt-and-verdict-audit": {
    "run_sha": "16bbc5a7a78f977e26aabe9f3756fcab21ffc79c4ad03ac92f57d5a1fbfdc634",
    "files": [
+    "tests/throwaway_git.py",
     "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/roster_lib.py",
     "tools/audit/seat/sweep_gantt.py",
@@ -4534,11 +4549,16 @@
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
@@ -4786,6 +4806,7 @@
     "tools/audit/seat/hooks_setup.py",
     "tools/audit/seat/instruments/**",
     "tools/audit/seat/ledger.py",
+    "tools/audit/seat/loop_ledger.py",
     "tools/audit/seat/merge_pr.sh",
     "tools/audit/seat/merge_train.py",
     "tools/audit/seat/moved_paths.py",
@@ -4801,6 +4822,7 @@
     "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
+    "tools/audit/seat/plan_phases.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
     "tools/audit/seat/plant_recall.py",
@@ -4936,6 +4958,32 @@
    "objects": false,
    "git": []
   },
+  "loop-ledger": {
+   "run_sha": "95edb059af375232f0da09f23b7ab1bc4166923800970f72578cf90b3be9173a",
+   "files": [
+    "dev/audit/config/bugclasses.json",
+    "tests/throwaway_git.py",
+    "tools/audit/seat/loop_ledger.py",
+    "tools/audit/seat/roster_lib.py",
+    "tools/audit/seat/scorecard.py"
+   ],
+   "probes": [
+    ".",
+    "dev/audit/rca/R10-N-log-flood.md",
+    "dev/governance/dimensions/D8.md",
+    "tests",
+    "tools",
+    "tools/audit",
+    "tools/audit/seat"
+   ],
+   "dirs": [
+    "tests",
+    "tools/audit/seat"
+   ],
+   "index": false,
+   "objects": false,
+   "git": []
+  },
   "machinery-ratchet": {
    "run_sha": "27ea83021c2a8528abd0f1b88a9ebdb9dfa7346b4a8ca0609d11f72e80f2888d",
    "files": [
@@ -5076,6 +5124,7 @@
     "tools/audit/seat/review_packet.py",
     "tools/audit/seat/roster_lib.py",
     "tools/audit/seat/seat_gen.py",
+    "tools/audit/seat/topic_grammar.py",
     "tools/ci/gate.py",
     "tools/ci/ghapi.py",
     "tools/ci/prelude.py",
@@ -5249,6 +5298,7 @@
     "tools/audit/archscore/vector.py",
     "tools/audit/carry_audit.py",
     "tools/audit/check_scopes.py",
+    "tools/audit/enumerate.py",
     "tools/audit/fold_ledger.py",
     "tools/audit/judge_batch.py",
     "tools/audit/machinery_ratchet.py",
@@ -5298,6 +5348,7 @@
     "tools/audit/seat/hooks/**",
     "tools/audit/seat/hooks_setup.py",
     "tools/audit/seat/ledger.py",
+    "tools/audit/seat/loop_ledger.py",
     "tools/audit/seat/merge_pr.sh",
     "tools/audit/seat/merge_train.py",
     "tools/audit/seat/moved_paths.py",
@@ -5313,6 +5364,7 @@
     "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
+    "tools/audit/seat/plan_phases.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
     "tools/audit/seat/plant_recall.py",
@@ -5348,6 +5400,8 @@
     "tools/audit/seat/roster_lib.py",
     "tools/audit/seat/roster_queue.py",
     "tools/audit/seat/roster_sync.py",
+    "tools/audit/seat/round_metrics.py",
+    "tools/audit/seat/round_metrics_selftest.py",
     "tools/audit/seat/row_position.py",
     "tools/audit/seat/run_twins.py",
     "tools/audit/seat/scorecard.py",
@@ -5487,11 +5541,13 @@
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
@@ -5501,9 +5557,11 @@
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
@@ -5518,14 +5576,17 @@
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
@@ -5545,6 +5606,7 @@
     "tools/audit/archscore/**",
     "tools/audit/carry_audit.py",
     "tools/audit/check_scopes.py",
+    "tools/audit/enumerate.py",
     "tools/audit/fold_ledger.py",
     "tools/audit/judge_batch.py",
     "tools/audit/machinery_ratchet.py",
@@ -5598,6 +5660,7 @@
     "tools/audit/seat/hooks/**",
     "tools/audit/seat/hooks_setup.py",
     "tools/audit/seat/ledger.py",
+    "tools/audit/seat/loop_ledger.py",
     "tools/audit/seat/merge_pr.sh",
     "tools/audit/seat/merge_train.py",
     "tools/audit/seat/moved_paths.py",
@@ -5613,6 +5676,7 @@
     "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
+    "tools/audit/seat/plan_phases.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
     "tools/audit/seat/plant_recall.py",
@@ -5648,6 +5712,8 @@
     "tools/audit/seat/roster_lib.py",
     "tools/audit/seat/roster_queue.py",
     "tools/audit/seat/roster_sync.py",
+    "tools/audit/seat/round_metrics.py",
+    "tools/audit/seat/round_metrics_selftest.py",
     "tools/audit/seat/row_position.py",
     "tools/audit/seat/run_twins.py",
     "tools/audit/seat/scorecard.py",
@@ -5795,12 +5861,20 @@
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
@@ -5935,6 +6009,7 @@
     "dev/audit/**",
     "dev/governance/config/corpus_excluded.json",
     "dev/governance/config/machinery_budgets.json",
+    "dev/governance/config/machinery_target_budgets.json",
     "dev/governance/config/outside_contributors.json",
     "dev/governance/config/policy_budgets.json",
     "dev/governance/config/policy_known_bad.json",
@@ -5952,6 +6027,7 @@
     "dev/programme/register/audit-2026-09.md",
     "dev/programme/rosters/**",
     "dev/programme/round10/**",
+    "dev/programme/round11/phases.json",
     "dev/programme/round9/**",
     "dev/programme/triage/**",
     "docs/**",
@@ -6506,6 +6582,7 @@
     "dev/programme/round10/.gitattributes",
     "dev/programme/round10/rechain/.gitattributes",
     "dev/programme/round10/state/.gitattributes",
+    "dev/programme/round11/.gitattributes",
     "dev/programme/round9/.gitattributes",
     "dev/programme/round9/state/.gitattributes",
     "dev/programme/triage/.gitattributes",
@@ -6669,6 +6746,7 @@
     "tools/audit/archscore/vector.py",
     "tools/audit/carry_audit.py",
     "tools/audit/check_scopes.py",
+    "tools/audit/enumerate.py",
     "tools/audit/fold_ledger.py",
     "tools/audit/judge_batch.py",
     "tools/audit/machinery_ratchet.py",
@@ -6718,6 +6796,7 @@
     "tools/audit/seat/hooks/**",
     "tools/audit/seat/hooks_setup.py",
     "tools/audit/seat/ledger.py",
+    "tools/audit/seat/loop_ledger.py",
     "tools/audit/seat/merge_pr.sh",
     "tools/audit/seat/merge_train.py",
     "tools/audit/seat/moved_paths.py",
@@ -6733,6 +6812,7 @@
     "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
+    "tools/audit/seat/plan_phases.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
     "tools/audit/seat/plant_recall.py",
@@ -6768,6 +6848,8 @@
     "tools/audit/seat/roster_lib.py",
     "tools/audit/seat/roster_queue.py",
     "tools/audit/seat/roster_sync.py",
+    "tools/audit/seat/round_metrics.py",
+    "tools/audit/seat/round_metrics_selftest.py",
     "tools/audit/seat/row_position.py",
     "tools/audit/seat/run_twins.py",
     "tools/audit/seat/scorecard.py",
@@ -6984,6 +7066,7 @@
     "tools/audit/seat/ref_privacy.py",
     "tools/audit/seat/review_packet.py",
     "tools/audit/seat/roster_lib.py",
+    "tools/audit/seat/topic_grammar.py",
     "tools/audit/worktree_gc.sh",
     "tools/merge/ledger_merge.py",
     "tools/policy/brief_lint.mjs",
@@ -7503,6 +7586,7 @@
     "dev/governance/config",
     "dev/governance/decisions",
     "dev/governance/dimensions",
+    "dev/governance/dimensions/criteria",
     "dev/governance/roles",
     "dev/governance/rules",
     "dev/programme",
@@ -7513,6 +7597,7 @@
     "dev/programme/round10",
     "dev/programme/round10/rechain",
     "dev/programme/round10/state",
+    "dev/programme/round11",
     "dev/programme/round9",
     "dev/programme/round9/state",
     "dev/programme/triage",
@@ -7621,6 +7706,7 @@
     "tests/mutation_ledger/killed_by/services.py",
     "tests/mutation_ledger/killed_by/setpoint_check.py",
     "tests/mutation_ledger/killed_by/silent_mode.py",
+    "tests/mutation_ledger/killed_by/slab_seed.py",
     "tests/mutation_ledger/killed_by/slot_drivers.py",
     "tests/mutation_ledger/killed_by/snapshots.py",
     "tests/mutation_ledger/killed_by/store.py",
@@ -7663,6 +7749,7 @@
     "tests/mutation_ledger/survivor_triage/quiet_windows.py",
     "tests/mutation_ledger/survivor_triage/repairs.py",
     "tests/mutation_ledger/survivor_triage/sensor.py",
+    "tests/mutation_ledger/survivor_triage/slab_seed.py",
     "tests/mutation_ledger/survivor_triage/slot_drivers.py",
     "tests/mutation_ledger/survivor_triage/store.py",
     "tests/mutation_ledger/survivor_triage/sysid.py",
@@ -7735,6 +7822,7 @@
     "fetch",
     "hash-object",
     "log",
+    "ls-remote",
     "ls-tree",
     "merge-base",
     "merge-tree",
@@ -8115,6 +8203,7 @@
     "tools/audit/seat/ref_privacy.py",
     "tools/audit/seat/review_packet.py",
     "tools/audit/seat/roster_lib.py",
+    "tools/audit/seat/topic_grammar.py",
     "tools/policy/brief_lint.mjs",
     "tools/policy/counts.mjs",
     "tools/policy/dependabot_contract.mjs",
@@ -8185,16 +8274,24 @@
   "roster-editor": {
    "run_sha": "69d134ca93555d9ce85205a52a5eb7ef397b6bf559866955924dc0fee3152065",
    "files": [
+    "dev/audit/config/bugclasses.json",
+    "dev/audit/rca/R10-N-log-flood.md",
     "tests/throwaway_git.py",
     "tools/audit/carry_audit.py",
+    "tools/audit/seat/loop_ledger.py",
     "tools/audit/seat/ref_privacy.py",
     "tools/audit/seat/roster_edit.py",
     "tools/audit/seat/roster_lib.py",
+    "tools/audit/seat/round_metrics.py",
+    "tools/audit/seat/scorecard.py",
     "tools/policy/fixtures/required-contexts.json"
    ],
    "probes": [
     ".",
     "config",
+    "dev/audit/rca/R10-N-log-flood.md",
+    "dev/governance/dimensions/D8.md",
+    "dev/governance/dimensions/D99.md",
     "objects",
     "refs",
     "tests",
@@ -8213,18 +8310,29 @@
   "roster-library": {
    "run_sha": "ef4cbcbdebfe734c9270dab5c152611820d5f1abdb65bb51f459535bf08e8287",
    "files": [
+    "dev/audit/config/bugclasses.json",
     "tests/throwaway_git.py",
-    "tools/audit/seat/roster_lib.py"
+    "tools/audit/seat/roster_lib.py",
+    "tools/plan/replan.py",
+    "tools/release/stamp.py"
    ],
    "probes": [
     ".",
+    "dev/audit/rca/R10-N-log-flood.md",
+    "dev/governance/dimensions/D12.md",
+    "dev/governance/dimensions/D3.md",
+    "dev/governance/dimensions/D99.md",
     "tests",
     "tools",
     "tools/audit",
-    "tools/audit/seat"
+    "tools/audit/seat",
+    "tools/plan",
+    "tools/release"
    ],
    "dirs": [
-    "tests"
+    "tests",
+    "tools/audit/seat",
+    "tools/release"
    ],
    "index": false,
    "objects": false,
@@ -8398,12 +8506,15 @@
   "scorecard": {
    "run_sha": "3215c0b1f85e68b18dde7d804fdeca68363603e0bf8bb708323038e2801941ac",
    "files": [
+    "tools/audit/seat/loop_ledger.py",
+    "tools/audit/seat/roster_lib.py",
     "tools/audit/seat/round_metrics.py",
     "tools/audit/seat/scorecard.py",
     "tools/audit/seat/scorecard_selftest.py"
    ],
    "probes": [
     ".",
+    "dev/governance/dimensions/D8.md",
     "tools",
     "tools/audit",
     "tools/audit/seat"
@@ -8493,6 +8604,7 @@
     "dev/audit/**",
     "dev/governance/config/corpus_excluded.json",
     "dev/governance/config/machinery_budgets.json",
+    "dev/governance/config/machinery_target_budgets.json",
     "dev/governance/config/outside_contributors.json",
     "dev/governance/config/policy_budgets.json",
     "dev/governance/config/policy_known_bad.json",
@@ -8511,6 +8623,7 @@
     "dev/programme/register/audit-2026-09.md",
     "dev/programme/rosters/**",
     "dev/programme/round10/**",
+    "dev/programme/round11/phases.json",
     "dev/programme/round9/**",
     "dev/programme/triage/**",
     "docs/**",
@@ -8670,10 +8783,12 @@
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
@@ -8715,6 +8830,7 @@
     "tests/mutation_ledger/survivor_triage/quiet_windows.py",
     "tests/mutation_ledger/survivor_triage/repairs.py",
     "tests/mutation_ledger/survivor_triage/sensor.py",
+    "tests/mutation_ledger/survivor_triage/slab_seed.py",
     "tests/mutation_ledger/survivor_triage/slot_drivers.py",
     "tests/mutation_ledger/survivor_triage/store.py",
     "tests/mutation_ledger/survivor_triage/sysid.py",
@@ -8819,6 +8935,7 @@
     "tools/audit/archscore/weights.sha256",
     "tools/audit/carry_audit.py",
     "tools/audit/check_scopes.py",
+    "tools/audit/enumerate.py",
     "tools/audit/fold_ledger.py",
     "tools/audit/judge_batch.py",
     "tools/audit/machinery_ratchet.py",
@@ -8872,6 +8989,7 @@
     "tools/audit/seat/hooks_setup.py",
     "tools/audit/seat/instruments/**",
     "tools/audit/seat/ledger.py",
+    "tools/audit/seat/loop_ledger.py",
     "tools/audit/seat/merge_pr.sh",
     "tools/audit/seat/merge_train.py",
     "tools/audit/seat/moved_paths.py",
@@ -8887,6 +9005,7 @@
     "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
+    "tools/audit/seat/plan_phases.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
     "tools/audit/seat/plant_recall.py",
@@ -9103,6 +9222,7 @@
     "tools/audit/seat/bottleneck_check.py",
     "tools/audit/seat/handover_prompt.py",
     "tools/audit/seat/plan_page.py",
+    "tools/audit/seat/plan_phases.py",
     "tools/audit/seat/plan_table.py",
     "tools/audit/seat/pr_cap.py",
     "tools/audit/seat/ref_privacy.py",
@@ -9353,6 +9473,7 @@
     "tests/mutation_ledger/killed_by/services.py/.gitattributes",
     "tests/mutation_ledger/killed_by/setpoint_check.py/.gitattributes",
     "tests/mutation_ledger/killed_by/silent_mode.py/.gitattributes",
+    "tests/mutation_ledger/killed_by/slab_seed.py/.gitattributes",
     "tests/mutation_ledger/killed_by/slot_drivers.py/.gitattributes",
     "tests/mutation_ledger/killed_by/snapshots.py/.gitattributes",
     "tests/mutation_ledger/killed_by/store.py/.gitattributes",
@@ -9395,6 +9516,7 @@
     "tests/mutation_ledger/survivor_triage/quiet_windows.py/.gitattributes",
     "tests/mutation_ledger/survivor_triage/repairs.py/.gitattributes",
     "tests/mutation_ledger/survivor_triage/sensor.py/.gitattributes",
+    "tests/mutation_ledger/survivor_triage/slab_seed.py/.gitattributes",
     "tests/mutation_ledger/survivor_triage/slot_drivers.py/.gitattributes",
     "tests/mutation_ledger/survivor_triage/store.py/.gitattributes",
     "tests/mutation_ledger/survivor_triage/sysid.py/.gitattributes",
@@ -9578,6 +9700,7 @@
     "tools/audit/archscore/vector.py",
     "tools/audit/carry_audit.py",
     "tools/audit/check_scopes.py",
+    "tools/audit/enumerate.py",
     "tools/audit/fold_ledger.py",
     "tools/audit/judge_batch.py",
     "tools/audit/machinery_ratchet.py",
@@ -9627,6 +9750,7 @@
     "tools/audit/seat/hooks/**",
     "tools/audit/seat/hooks_setup.py",
     "tools/audit/seat/ledger.py",
+    "tools/audit/seat/loop_ledger.py",
     "tools/audit/seat/merge_pr.sh",
     "tools/audit/seat/merge_train.py",
     "tools/audit/seat/moved_paths.py",
@@ -9642,6 +9766,7 @@
     "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
+    "tools/audit/seat/plan_phases.py",
     "tools/audit/seat/plan_public.py",
     "tools/audit/seat/plan_table.py",
     "tools/audit/seat/plant_recall.py",
@@ -9677,6 +9802,8 @@
     "tools/audit/seat/roster_lib.py",
     "tools/audit/seat/roster_queue.py",
     "tools/audit/seat/roster_sync.py",
+    "tools/audit/seat/round_metrics.py",
+    "tools/audit/seat/round_metrics_selftest.py",
     "tools/audit/seat/row_position.py",
     "tools/audit/seat/run_twins.py",
     "tools/audit/seat/scorecard.py",
diff --git a/tools/pr/ci_predict.py b/tools/pr/ci_predict.py
index f260b5317b..b1dfde50b6 100644
--- a/tools/pr/ci_predict.py
+++ b/tools/pr/ci_predict.py
@@ -549,6 +549,26 @@ def names_changed(root: Path, run: str, changed: set[str]) -> bool:
     return False
 
 
+def recorded_readers(root: Path, changed: set[str]) -> set[str]:
+    """The instrument-self-tests steps whose recorded closure in `root`'s
+    tools/ci/selftest_closures.json holds a changed path in `files` -- the
+    readers a step's run text does not name: queue_pre_flight.py's step reads
+    merge_train.py, which 23b943c987 reddened unnamed. Parsed by
+    selftest_scope's own `job_steps` and `covers`; an unreadable table is none."""
+    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ci"))
+    try:
+        import selftest_scope as ss
+    finally:
+        sys.path.pop(0)
+    table = ss.load_table(root / ss.TABLE)
+    wf = root / INSTRUMENT_WF
+    if table is None or not wf.is_file():
+        return set()
+    return {st.name for st in ss.job_steps(wf.read_text(), INSTRUMENT_JOB)
+            if st.id in table["steps"]
+            and any(ss.covers(table["steps"][st.id].get("files", ()), c) for c in changed)}
+
+
 # A replay that ran out of time measured nothing about the tree: a loaded host
 # (load average 100+) timed out clean branches at 180 s while CI was green.
 STEP_REPLAY_TIMEOUT_ENV = "HPO_STEP_REPLAY_TIMEOUT_S"
@@ -582,14 +602,16 @@ def replay_step(tree: Path, run: str) -> int:
 
 def step_replay_preds(root: Path, base: str, changed: set[str],
                       notes: list | None = None) -> list[tuple[str, str]]:
-    """Each instrument-self-tests step whose run text names a changed file,
-    replayed at the head; one red there is replayed again, as the base's step of
+    """Each instrument-self-tests step whose run text names a changed file, or
+    whose recorded closure reads one (`recorded_readers`), replayed at the
+    head; one red there is replayed again, as the base's step of
     that name, in a detached worktree of the base, and predicted only where the
     base's is green -- so a step this container cannot run (a missing binary,
     an unset variable: red at both ends) is a note left to CI, never the branch's."""
     import tempfile
     head = instrument_steps(root)
-    hit = {n: r for n, r in head.items() if names_changed(root, r, changed)}
+    readers = recorded_readers(root, changed)  # mut:readers
+    hit = {n: r for n, r in head.items() if n in readers or names_changed(root, r, changed)}
     ran = {n: replay_step(root, r) for n, r in hit.items()}
     for n, rc in ran.items():
         if rc == TIMED_OUT:
@@ -637,7 +659,15 @@ def step_replay_self_test(root: Path) -> int:
                 "          grep -Eq '^{n} self-test: [1-9][0-9]* checks, 0 failed$' \"$RUNNER_TEMP/{n}.txt\"\n")
         (t / INSTRUMENT_WF).write_text(f"jobs:\n  {INSTRUMENT_JOB}:\n    steps:\n"
                                        + step.format(n="a") + step.format(n="b")
-                                       + "      - name: c\n        run: bash tools/c.sh\n")
+                                       + "      - name: c\n        run: bash tools/c.sh\n"
+                                       + "      - name: d\n        id: d\n        run: bash tools/d.sh\n")
+        # d's run text and d.sh name no file of tools/lib/: only its recorded closure reads x.sh.
+        (t / "tools" / "lib").mkdir()
+        (t / "tools" / "lib" / "x.sh").write_text("true\n")
+        (t / "tools" / "d.sh").write_text("set -e; for f in tools/lib/*.sh; do . \"$f\"; done\n")
+        (t / "tools" / "ci").mkdir()
+        table = t / "tools" / "ci" / "selftest_closures.json"
+        table.write_text(json.dumps({"steps": {"d": {"files": ["tools/d.sh", "tools/lib/x.sh"]}}}))
         # c's step names only c.sh, whose text drives a.sh (ref_privacy.py over body_push.sh).
         (t / "tools" / "c.sh").write_text("bash tools/a.sh --self-test | grep -q '^a self-test:'\n")
         ok = "echo '{n} self-test: 3 checks, 0 failed'\n"
@@ -683,6 +713,24 @@ def step_replay_self_test(root: Path) -> int:
                 os.environ.pop(STEP_REPLAY_TIMEOUT_ENV, None)
             else:
                 os.environ[STEP_REPLAY_TIMEOUT_ENV] = was
+        (t / "tools" / "lib" / "x.sh").write_text("exit 1\n")
+        got = [l for _, l in step_replay_preds(t, base, {"tools/lib/x.sh"})]
+        good = len(got) == 1 and got[0].startswith("STEP REPLAY d:")
+        print(f"  {'ok  ' if good else 'FAIL'} a step whose recorded closure reads the changed file, "
+              f"its run text naming none, is replayed and predicted red")
+        bad += not good
+        table.write_text(json.dumps({"steps": {"d": {"files": ["tools/d.sh"]}}}))
+        got = len(step_replay_preds(t, base, {"tools/lib/x.sh"}))
+        print(f"  {'ok  ' if got == 0 else 'FAIL'} null control: a closure not holding the changed file is not replayed")
+        bad += got != 0
+        table.write_text(json.dumps({"steps": {"d": {"files": ["tools/lib/**"]}}}))
+        got = len(step_replay_preds(t, base, {"tools/lib/x.sh"}))
+        print(f"  {'ok  ' if got == 1 else 'FAIL'} a closure's `tools/lib/**` entry covers the changed file")
+        bad += got != 1
+        table.unlink()
+        got = len(step_replay_preds(t, base, {"tools/lib/x.sh"}))
+        print(f"  {'ok  ' if got == 0 else 'FAIL'} no table: no recorded reader, nothing replayed, nothing raised")
+        bad += got != 0
     g = globals()
     real = g["step_replay_preds"]
     g["step_replay_preds"] = lambda *_a: [("instrument", "STEP REPLAY sentinel")]
@@ -858,6 +906,24 @@ def run_key(job: str, prog: str, argv) -> tuple[str, ...]:
     return (job, Path(prog).name, *(a for a in argv if a.startswith("--")))
 
 
+ROUND_ROSTERS = "+refs/heads/handoff/audit-r*-roster:refs/remotes/origin/handoff/audit-r*-roster"
+
+
+def refresh_round_rosters(root: Path) -> str | None:
+    """pr-contract fetches the round rosters before its carry check; a seat's
+    remote-tracking ref is as old as its last fetch, so a group the roster
+    gained since reads as a bad destination. Fetch them into `root` as CI does
+    (the grader arm's clone then takes them, `fetch_round_rosters`). None when
+    fetched, else the note that the roster read may be stale."""
+    try:
+        out = subprocess.run(["git", "fetch", "-q", "--no-tags", "origin", ROUND_ROSTERS],
+                             cwd=root, capture_output=True, text=True, timeout=60)
+        why = f"failed: {' '.join(out.stderr.split())[:240] or 'no output'}" if out.returncode else None
+    except subprocess.TimeoutExpired:
+        why = "timed out"
+    return None if why is None else f"ROSTER UNFETCHED: git fetch of the round rosters {why}; the carry check read this clone's refs"
+
+
 def fetch_round_rosters(run) -> None:
     """CI's pr-contract fetches the round rosters' remote-tracking refs; a
     --shared clone's own origin/handoff/* are root's local branches, so take
@@ -1174,6 +1240,10 @@ def predict(root: Path, base_ref: str, pairs: set | None = None,
     base = (git(root, "merge-base", base_ref, "HEAD") or "").strip()
     if not base:
         return 2, [], f"no merge base between {base_ref} and HEAD"
+    if body:  # the carry arm, and the graders arm's pr-contract run, read the round roster
+        stale = refresh_round_rosters(root)  # mut:roundfetch
+        if stale and notes is not None:
+            notes.append(stale)
     sys.path[:0] = [str(root / "tests"), str(root / "tests" / "hastub")]
     import closure
     names = git(root, "diff", "--name-only", "--no-renames", f"{base}...HEAD") or ""
@@ -1679,6 +1749,75 @@ def roundref_self_test(root: Path) -> int:
         shutil.rmtree(tmp, ignore_errors=True)
     line = [l for l in inspect.getsource(ci_tree_run).splitlines() if "fetch_round_rosters" in l]
     check("ci_tree_run calls fetch_round_rosters on one `# mut:roundrefs` line", len(line) == 1 and "# mut:roundrefs" in line[0])
+    return bad + roundfetch_self_test(root)
+
+
+def roundfetch_self_test(root: Path) -> int:
+    """refresh_round_rosters moves a seat's stale remote-tracking round ref to
+    origin's branch, as pr-contract's fetch does; null: an unreachable origin
+    leaves the ref, raises nothing and returns the note; predict refreshes
+    when given a body and only then."""
+    import shutil
+    import tempfile
+    sys.path.insert(0, str(root / "tests"))
+    from throwaway_git import throwaway_git_clone, throwaway_git_init
+    ref = "refs/remotes/origin/handoff/audit-r10-roster"
+    tmp = Path(tempfile.mkdtemp(prefix="hpo-ci-predict-roundfetch-"))
+    bad = 0
+
+    def check(label, ok):
+        nonlocal bad
+        print(f"  {'ok  ' if ok else 'FAIL'} {label}")
+        bad += not ok
+    try:
+        o = tmp / "o"  # origin: its branches are what pr-contract fetches
+        oenv = throwaway_git_init(o, "-q", "-b", "main")
+
+        def sgit(*a):
+            return subprocess.run(a, cwd=o, env=oenv, capture_output=True, text=True, check=True).stdout.strip()
+        sgit("git", "commit", "-q", "--allow-empty", "-m", "main")
+        sgit("git", "branch", "handoff/audit-r10-roster")
+        stale = sgit("git", "rev-parse", "HEAD")
+        r = tmp / "seat"
+        env = throwaway_git_clone(o, r, "-q")
+        sgit("git", "checkout", "-q", "handoff/audit-r10-roster")
+        sgit("git", "commit", "-q", "--allow-empty", "-m", "the roster gains a group")
+        newer = sgit("git", "rev-parse", "HEAD")
+
+        def got():
+            return subprocess.run(["git", "rev-parse", "-q", "--verify", ref], cwd=r, env=env,
+                                  capture_output=True, text=True).stdout.strip()
+        check("the seat's round ref is stale before the refresh", got() == stale)
+        note = refresh_round_rosters(r)
+        check("refresh_round_rosters moves it to origin's branch and returns no note",
+              note is None and got() == newer)
+        subprocess.run(["git", "update-ref", ref, stale], cwd=r, env=env, check=True)
+        subprocess.run(["git", "remote", "set-url", "origin", str(tmp / "absent.git")], cwd=r, env=env, check=True)
+        try:
+            note, raised = refresh_round_rosters(r), False
+        except Exception:
+            note, raised = None, True
+        check("an unreachable origin leaves the ref, raises nothing and notes ROSTER UNFETCHED with git's "
+              "reason (null control)", not raised and got() == stale
+              and (note or "").startswith("ROSTER UNFETCHED") and "absent.git" in (note or ""))
+    finally:
+        shutil.rmtree(tmp, ignore_errors=True)
+    g = globals()
+    real, calls = g["refresh_round_rosters"], []
+    g["refresh_round_rosters"] = lambda r: calls.append(r) or "ROSTER UNFETCHED sentinel"
+    try:
+        with tempfile.NamedTemporaryFile("w", suffix=".md") as f:
+            f.write("## Forward-carry\n\nnone\n")
+            f.flush()
+            notes: list[str] = []
+            predict(root, "HEAD", body=f.name, only="orphans", notes=notes)
+            check("predict with a body refreshes the round rosters and notes a failed refresh",
+                  len(calls) == 1 and "ROSTER UNFETCHED sentinel" in notes)
+            calls.clear()
+            predict(root, "HEAD", only="orphans", notes=[])
+            check("predict without a body fetches nothing (null control)", not calls)
+    finally:
+        g["refresh_round_rosters"] = real
     return bad
 
 
diff --git a/tools/pr/prepr.sh b/tools/pr/prepr.sh
index d588ad272f..1626906bea 100755
--- a/tools/pr/prepr.sh
+++ b/tools/pr/prepr.sh
@@ -2430,14 +2430,15 @@ EOS
   printf 'def f(x):\n    if x > 0:\n        return 1\n    return 0\n' > "$MR/lib.py"
   printf 'import sys\nsys.path.insert(0, ".")\nfrom lib import f\nsys.exit(0 if [f(v) for v in (-2, 0, 1, 2)] == [0, 0, 1, 1] else 1)\n' > "$MR/tests/check.py"
   (mg add -A && mg commit -qm branch) >/dev/null 2>&1
-  got=$(mutants_line "$MR" "$MB" "false"); r=$?
+  got=$(MUTANT_IN_PLACE= mutants_line "$MR" "$MB" "false"); r=$?
   st "$r" 1 "a MUTANT_CMD failing on the unedited tree is refused, never read as no survivor"
   case "$got" in *'BASELINE FAILS'*) st 1 1 "and the refusal quotes mutant_run's own reason";; *) st 0 1 "and the refusal quotes mutant_run's own reason";; esac
-  got=$(mutants_line "$MR" "$MB" "python3 tests/check.py"); r=$?
+  got=$(MUTANT_IN_PLACE= mutants_line "$MR" "$MB" "python3 tests/check.py"); r=$?
   st "$r" 0 "a check killing every mutant of the added lines passes (null control)"
   # A check that needs the checkout (git) fails the archive copy's baseline and
-  # passes in place: the case MUTANT_IN_PLACE exists for, measured on 3379.
-  got=$(mutants_line "$MR" "$MB" "sh -c 'git rev-parse HEAD >/dev/null && python3 tests/check.py'"); r=$?
+  # passes in place: the case MUTANT_IN_PLACE exists for, measured on 3379. The
+  # archive-copy rows clear MUTANT_IN_PLACE: a fixer runs prepr with it set (fixer.md step 2).
+  got=$(MUTANT_IN_PLACE= mutants_line "$MR" "$MB" "sh -c 'git rev-parse HEAD >/dev/null && python3 tests/check.py'"); r=$?
   st "$r" 1 "a check needing a git checkout measures nothing in the archive copy, and is refused"
   got=$(MUTANT_IN_PLACE=1 mutants_line "$MR" "$MB" "sh -c 'git rev-parse HEAD >/dev/null && python3 tests/check.py'"); r=$?
   st "$r" 0 "the same check under MUTANT_IN_PLACE=1 runs in the checkout and passes"

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
