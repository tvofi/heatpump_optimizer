# Review packet #3091
head: 645643590632a8895affebdb1d81fc9d0f42fe66
base: f04b25a005f51b9df48154a6544c03e6873ed9de

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=124986075752 success
arch-score / arch-score id=124985798572 success
arm id=124985641998 skipped
budget-raise-gate / budget-raise-gate id=124985798800 success
cancel-superseded id=124985643025 success
codeql / Analyze (actions) id=124985798627 success
codeql / Analyze (javascript-typescript) id=124985798648 success
codeql / Analyze (python) id=124985798616 success
governance / delivery-status id=124985798772 failure
governance / delivery-status-publish id=124985799713 skipped
governance / env-matrix id=124985798676 in_progress
governance / instrument-self-tests id=124985798669 in_progress
governance / policy-docs id=124985798685 success
governance / record id=124985799947 skipped
governance / wave-script id=124985798708 success
hassfest / hassfest id=124985798558 success
kernel-points id=124985799739 skipped
prelude id=124985643147 in_progress
refresh id=124985642827 success
tests / arch-instrument id=124985969070 in_progress
tests / briefs id=124985798693 success
tests / browser id=124985969009 in_progress
tests / closure-scope id=124985798644 success
tests / closures id=124985969042 in_progress
tests / coverage id=124985969113 in_progress
tests / fast (3.14) id=124985968983 in_progress
tests / mutation id=124985798585 success
tests / mutation-autofix id=124986230359 skipped
tests / mutation-pins id=124986230145 skipped
tests / nightly-ha id=124985971010 skipped
tests / nightly-status id=124985798620 success
tests / replay id=124985970362 skipped
tests / typing id=124985969023 success
validate / validate-hacs id=124985798547 success

## Refusals
red-unanswered: concluded red check `governance / delivery-status` is not named in ## Red checks

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

## Three-dot diff
diff --git a/dev/programme/carries/carry-2674.json b/dev/programme/carries/carry-2674.json
deleted file mode 100644
index d3db95ab9..000000000
--- a/dev/programme/carries/carry-2674.json
+++ /dev/null
@@ -1,19 +0,0 @@
-{
-  "_comment": [
-    "Carry destination for #2674 (R10-LIVESTATE item ls-r2: seven unprobed",
-    "per-cycle store-load leads). No live roster group covers #2674, so this file",
-    "is its brief. Shape and required fields: dev/governance/rules/finding-propagation.md.",
-    "Linted by tools/policy/brief_lint.mjs (the `briefs` CI job)."
-  ],
-  "issue": 2674,
-  "stage": "#2674, probing the seven per-cycle writers that may run inside the first refresh before their store load resolves",
-  "carries": [
-    {
-      "from": "#2675 (R10-LIVESTATE), item ls-r2, with item ls-r1's probe recipe",
-      "effect": "narrows",
-      "control": "None of the seven leads is a finding: no harness has shown one lose a write. A lead becomes a finding only through item ls-r1's probe with its null: the load's store replaced by a stub whose async_load waits on an asyncio.Event; the load spawned, one yield, one coordinator cycle (the writer) run as a task, the event set, both awaited. Metric: the writer's increment absent after the load resolves, 1 (lost) or 0 (kept). Null control: the same cycle run after the load resolves, which must read 0; a lead whose null is not 0 is a broken probe, not a finding.",
-      "remeasure": "At your merge base, first establish per lead whether the writer runs in the first refresh at all (it may be gated on a sensor history or a previous-cycle value the first refresh lacks); a writer that cannot run before its load resolves is closed by that reading, with the gate cited. Only then run the probe and its null, per lead; re-anchor every writer by name, not by line.",
-      "brief": "The seven loads and their writers: `_async_load_thermal_learning` against `_async_learn_buffer_cooling`; `DhwLearner.async_load_profile` against `async_learn_dynamics`; the legionella store load against `async_track_cycle`; `_async_load_price_model` against `_async_learn_price_shape`; `_async_load_energy_totals` against the space-energy increment of `_energy_totals`; `_async_load_ledger` against the ledger's add; `_async_load_accuracy` against the accuracy tracker's record. This stage is narrowed to leads proven by the probe and its null; a fix without a reproducing probe is refused. Where a lead reproduces, the fix is the writer awaiting its store's `async_wait_for_read` before writing, as #2675 made `async_apply_manual_plan` and `async_clear_manual_plan` do for the manual plan store: not a per-lead flag. The user-command writers that race a load (item ls-r1) are carried to R10-PARAMS-OWNER, not here."
-    }
-  ]
-}
diff --git a/dev/programme/delivery/3048.md b/dev/programme/delivery/3048.md
index 4b2e56a01..d77fa64ab 100644
--- a/dev/programme/delivery/3048.md
+++ b/dev/programme/delivery/3048.md
@@ -1 +1,3 @@
 - [#3048](https://github.com/tvofi/heatpump_optimizer/pull/3048) — **merged `92588d5`**, R10-USER-DOCS-FINAL: user docs final.
+
+#3048: pre-flight waived for item 5017455b by orchestrator ruling under mandate: destination R10-USER-DOCS-VERIFY verified on origin/handoff/audit-r10-roster; pre-flight roster-ref defect carried to R10-TRAIN-OVERLAP-GRADE
diff --git a/dev/programme/delivery/3091.md b/dev/programme/delivery/3091.md
new file mode 100644
index 000000000..f47f63da4
--- /dev/null
+++ b/dev/programme/delivery/3091.md
@@ -0,0 +1 @@
+- [#3091](https://github.com/tvofi/heatpump_optimizer/pull/3091) — **open**, record: #3048 pre-flight waiver note; drop the answered #2674 carry file (R10-TRIAGE-S6)
diff --git a/tests/closures.json b/tests/closures.json
index 0875150fc..8b4523aba 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -1558,7 +1558,6 @@
    "dev/programme/carries/carry-2065.json",
    "dev/programme/carries/carry-2066.json",
    "dev/programme/carries/carry-2075.json",
-   "dev/programme/carries/carry-2674.json",
    "dev/programme/rosters/critical-path.json",
    "dev/programme/rosters/wave-r9-groups.json",
    "docs/architecture.md",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
