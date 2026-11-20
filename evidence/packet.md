# Review packet #3736
head: fe23416d408624f59f3d36dbbcea049d138ec764
base: b36742b17b7ea229b859fb86a43e74a562bb847b

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=135811617707 success
arch-score / arch-score id=135847463341 success
arm id=135808302652 skipped
budget-raise-gate / budget-raise-gate id=135847383595 failure
cancel-superseded id=135847381859 success
codeql id=135847466457 skipped
codeql / Analyze (actions) id=135810666892 success
codeql / Analyze (javascript-typescript) id=135810666635 success
codeql / Analyze (python) id=135810666602 success
gate id=135847382135 failure
governance id=135847485321 skipped
governance / env-matrix id=135810666547 success
governance / instrument-self-tests id=135810666786 success
governance / policy-docs id=135810666302 success
governance / record id=135810669919 skipped
governance / wave-script id=135810666138 success
hassfest id=135847458866 skipped
hassfest / hassfest id=135810666723 success
kernel-points id=135847458004 skipped
pr-contract id=135847385873 skipped
pr-contract / pr-contract id=135845410884 success
prelude id=135847483935 success
refresh id=135847459807 success
sweep-self id=135847985426 skipped
tests id=135847383805 skipped
tests / arch-instrument id=135813334684 success
tests / briefs id=135810666796 success
tests / browser id=135813335025 success
tests / ci-ratchet id=135836798490 skipped
tests / claims-autofix id=135834162921 skipped
tests / closure-scope id=135810666743 success
tests / closures id=135813335126 success
tests / closures-autofix id=135836798627 skipped
tests / coverage id=135813334896 success
tests / coverage-ratchet id=135830461370 success
tests / fast (3.14) id=135813334852 success
tests / graders-head-copy id=135830461365 success
tests / lane-proofs id=135834160497 success
tests / mutation id=135810666684 success
tests / mutation-autofix id=135845411934 skipped
tests / mutation-pins id=135845411951 skipped
tests / nightly-ha id=135813338245 skipped
tests / nightly-status id=135810666613 success
tests / replay id=135813335001 success
tests / typing id=135813334824 success
validate id=135847382672 skipped
validate / validate-hacs id=135810666970 success

## Refusals
none

## Advisories
approval-owed: required context `gate` concluded failure at fe23416d408624f59f3d36dbbcea049d138ec764 only on a budget raise's owed approval (merge_train.approval_owed): 3 budget raise(s), first tests/stress_budgets.json: summer/2z/space/wood-two-tank.ratio: 2.2 -> 7.46 (a cap went up): a raise is the owner's (0013): tvofi's approval is on ee9bfa8ac5c2, not this head fe23416d4086: an approval covers only the commit it was given on

## carry_audit at the head
NOTE stale tree: fe23416d408624f59f3d36dbbcea049d138ec764 lacks origin/main 698eeeb2ab94249ddf2c4c6e218556dc4e06c366; roster read at origin/main
NOTE body item 525b3b42: dismissed:outside D0-s2-01's mechanism by the finding's own perturbation; class P4's RCA, marked owed in ISSUES.json, is the seat that reads it
NOTE body item aa9c98dc: dismissed:corrected by the orchestrator's ruling before this fire
NOTE body item b2263e64: dismissed:the reproduction recipe is in this body's Figures, the reviewer's own surface
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: SCOPED -- 28 script(s) run, 5 scoped out.
             no segment of this names a program this check knows
  unverified git diff --stat 661c624c 261a3998 -- custom_components
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git archive 819aa2e3 dev/audit/rounds/round11
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified python3 $EXPORT/dev/audit/rounds/round11/D1/leads/slot_reason_hashseed.py
             the path `$EXPORT/dev/audit/rounds/round11/D1/leads/slot_reason_hashseed.py` is a template or an expansion, not a literal
  unverified python3 $EXPORT/dev/audit/rounds/round11/D2/s3/m3_risk.py
             the path `$EXPORT/dev/audit/rounds/round11/D2/s3/m3_risk.py` is a template or an expansion, not a literal
  unverified python3 $EXPORT/dev/audit/rounds/round11/D0/s3/offstart.py --workers 2
             the path `$EXPORT/dev/audit/rounds/round11/D0/s3/offstart.py` is a template or an expansion, not a literal
  unverified python3 $EXPORT/dev/audit/rounds/round11/D0/s2/wood_seeds.py --census
             the path `$EXPORT/dev/audit/rounds/round11/D0/s2/wood_seeds.py` is a template or an expansion, not a literal
  unverified python3 $EXPORT/dev/audit/rounds/round11/D0/s2/wood_seeds.py --race
             the path `$EXPORT/dev/audit/rounds/round11/D0/s2/wood_seeds.py` is a template or an expansion, not a literal
  ok         PYTHONPATH=tests/hastub python3 tests/env_drift.py --all bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f
             `tests/env_drift.py` is in the tree at this head
  ok         tools/audit/seat/cloud-setup.sh --kernels
             `tools/audit/seat/cloud-setup.sh` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff 7ae05284d5bceb254230b471a4eb936c2b072174
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/stress.py
             `tests/stress.py` is in the tree at this head
  unverified PYTHONPATH=tests/hastub:tests python3 -c
             python3 runs an inline script rather than a file
  ok         python3 tests/closure.py select --diff bc658f9d
             `tests/closure.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only
             `tests/env_drift.py` is in the tree at this head

FIGURES: 9 resolved, 9 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._optimize_space_only.GUARD_OFF.6a3be0ea.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._optimize_space_only.GUARD_OFF.6a3be0ea.json
deleted file mode 100644
index e6d1570aff..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._optimize_space_only.GUARD_OFF.6a3be0ea.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._optimize_space_only GUARD_OFF 6a3be0ea",
-  "killed_by": "tests/optimality.py",
-  "old": "        if self.model.params.two_zone_enabled:",
-  "reason": "arrived with round 7 D0-01 (#1447): the gate that scopes the deep low-energy anchor to the two-zone path, so every single-zone plan stays byte-identical to origin/main and the certificate's three claims keep their calibration. Killed by tests/optimality.py -- `if self.model.params.two_zone_enabled:` -> `if False:` never appends the anchor, which is the same tree as deleting it: FAIL two|winter_typical|winter_cold: no unclaimed gap above the bar [ladder 0.4374%, bar 0.4000%], 1 of 84, measured on this branch."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_objectives.RETURN_DEL.ac696c3f.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_objectives.RETURN_DEL.ac696c3f.json
deleted file mode 100644
index ee3dfe4d02..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_objectives.RETURN_DEL.ac696c3f.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._solve_objectives RETURN_DEL ac696c3f",
-  "killed_by": "tests/doc_claims.py",
-  "old": "        return _space_traj, objective, objective_batch, energy_cost_of",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 2b6c5b876ec297bf2b0ef4a127d09cf97fc40b5d: RETURN_DEL (`pass`) took tests/doc_claims.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_Horizon.money_prices.RETURN_DEL.281d99b3.json b/tests/mutation_ledger/killed_by/optimizer.py/_Horizon.money_prices.RETURN_DEL.281d99b3.json
new file mode 100644
index 0000000000..62d1a14ab1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_Horizon.money_prices.RETURN_DEL.281d99b3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_Horizon.money_prices RETURN_DEL 281d99b3",
+  "killed_by": "tests/plan_view.py",
+  "old": "        return self.prices if self.raw_prices is None else self.raw_prices",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_lower_bound_start.RETURN_DEL.0c801cad.json b/tests/mutation_ledger/killed_by/optimizer.py/_lower_bound_start.RETURN_DEL.0c801cad.json
new file mode 100644
index 0000000000..a25cfc9626
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_lower_bound_start.RETURN_DEL.0c801cad.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_lower_bound_start RETURN_DEL 0c801cad",
+  "killed_by": "tests/features.py",
+  "old": "    return np.array([low for low, _ in bounds], dtype=float)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_space_only_starts.RETURN_DEL.a961eef1.json b/tests/mutation_ledger/killed_by/optimizer.py/_space_only_starts.RETURN_DEL.a961eef1.json
new file mode 100644
index 0000000000..1eca0e6ad3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_space_only_starts.RETURN_DEL.a961eef1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_space_only_starts RETURN_DEL a961eef1",
+  "killed_by": "tests/doc_claims.py",
+  "old": "    return list(unique.values())",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/doc_claims.py from rc=0 failed=0 to rc=1 failed=3."
+}


## Review scope: delta (later round over the reviewed head ee9bfa8ac5c2c5cc5454f3c636cb627bcb29d565)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at ee9bfa8ac5c2c5cc5454f3c636cb627bcb29d565
Fix review: blocked ee9bfa8ac5c2c5cc5454f3c636cb627bcb29d565 mutation-vacuous: custom_components/heatpump_optimizer/plan_slots.py:89 lives: M1 (dict.fromkeys back to set) passes the D1-s1-51 tie check under some hash seeds, so the check's "whatever the hash seed" is not what it tests

bus-nonce: 660d8f04cbd4468a25be894b27de8a28

## Block

- M1, `plan_slots.py:89` `max(dict.fromkeys(codes), key=codes.count)` back to `max(set(codes), key=codes.count)`, run in a worktree at the head against the PR's features block (`features_block.py`, marker `# --- R11-SEAM-solver: the start set brackets`): ALL 9 FEATURES BLOCK PASSED under a random hash seed, rc=0 (ev/block-mutant-M1.log). Under fixed seeds: PYTHONHASHSEED=0 rc=1 (killed), 23 rc=0, 76 rc=0 (ev/M1-seeds.txt). The unmutated head passes at 23 and 76 too.
- The cause: for a two-element set the iteration order is insertion order when both strings land in the same table slot, which happens under some seeds. In that case `set` also returns the slot's first code for both spellings of the tie, so the check cannot tell the mutant from the fix. Over seeds 16-120, `max(set(...))` returned the first code for both orders at seeds 23, 24, 76 and 84. The body's M1 "FAIL" was one draw.
- Repair: make the check independent of the process's seed. For example, run the two tie spellings in subprocesses over a fixed seed list that includes a colliding seed (23) and a non-colliding one (0). Or check the order-preserving property directly, with a tie whose set order disagrees with its first code under the running seed. Re-run M1 at seeds 0, 23 and 76.
- The production fix is sound: `dict.fromkeys` keeps first-seen order, so a tie goes to the slot's first code under every seed. This block is on the pin only.

## Previous findings

- At bdf09624 the block was tests/doc_claims.py (2 of 411). Resolved: at this head `tests/doc_claims.py` reads ALL 439 checks PASSED (ev/local-doc_claims.log), and 61f2f4bbb2 rewords how-it-works.md to the five starts.
- Owed from the previous round, the other mutants (M1, M3-M6) and the other three `tests / fast` failures. The mutants are re-run here (ev/mutants.txt). M3, M4, M5 and M6 are killed; M1 is above. The fast failures are named in the body (`env_drift.py` confidence_margins, claimed at db6f2a664b, and `stress.py`), and `tests / fast (3.14)` is green at this head.

## Delta reviewed

`git diff bdf09624...ee9bfa8ac5`. The branch's own commits since bdf09624 are 61f2f4bbb2, 320c063489, bc33f25c50, d1e3701d13, 6a09ed087a, d63daa072e, f769d50c7f, a2236e189f and db6f2a664b. The rest are main merges (a7f9c27aee: the one `tests/features.py` end-of-file conflict, both blocks kept).

- Production delta, `optimizer.py` `_space_only_starts` (d1e3701d13, f769d50c7f). Byte-identical starts are kept once, first occurrence first. The reference-energy seeds are drawn unconditionally.
  - For covered == 0.0, `reference_power * (1.0 - 0.0)` is exact, so `energy == reference_kwh` bitwise and the filter drops the copies. The removed guard was dead.
  - `_wood_covered_share` returns a value in [0, 1], so no negative share adds a non-duplicate set.
  - Mutants: M7 (filter removed) is killed by `a space-only solve no wood covers hands the multi-start no duplicate start` [7 starts, 5 distinct]. M5 (reference-energy extend deleted) is killed by the whole-cover check.
  - Widened to `_space_only_starts`' callers only; nothing else in the delta touches the solve.
- `tests/stress.py` simulate allowance, with `tests/stress_budgets.json` `simulate_allowance` and the ratio 2.2 -> 7.46 (6a09ed087a, d63daa072e). The allowance applies to one scenario on one channel and expires once the baseline reads at or above 68093. `budget_table_problems` validates it. It carries four self-checks, whose mutants MA-MD the body reports (not re-run here). The body's `## Raise justification` names six payments and an `Architecture score:` line. `budget-raise-gate` is green at this head.
- `tests/features.py`, 320c063489 and bc33f25c50: the commit-stage checks now read candidate 1 as the descent's plan. Test only.
- Mutation pins (a2236e189f): three RETURN_DEL sites, killed per the ledger. Two ledger files are deleted for sites the diff removed. CI `tests / mutation` is green.

## Evidence

- Head: ee9bfa8ac5c2c5cc5454f3c636cb627bcb29d565 (ev/HEAD.txt). The live PR head was re-read before posting and is the same.
- Round: second (delta over bdf09624).
- `merge_train.py classify --pr 3736 ee9bfa8ac5`: `GREEN ... pending: none red: none` (ev/classify.txt). The packet's digest reads every required check success.
- `git merge-tree --write-tree origin/main ee9bfa8ac5` at origin/main e4a6cc6041: rc=0, no conflict (ev/merge-tree.txt).
- VERSION, manifest.json and RELEASE_NOTES.md: untouched in the three-dot diff.
- Local at the head: doc_claims.py ALL 439 PASSED; `env_drift.py --claims-only` rc=0; structure.py rc=0; the PR block ALL 9 PASSED.
- Finder's harness, D0-s2-01 `wood_seeds.py --race` over the finding's 7 cells from the plan/r11 export 819aa2e3 (sha1 1b03dd54), per-tree copies, on this arm64 host (numpy on Accelerate, not OpenBLAS). Summer_cool gap_abs, base cb8edb65 vs head:
  - winter_narrow 2.0292 -> 0.0022
  - winter_extreme 1.6782 -> 0.1210
  - winter_typical 1.6310 -> 0.0093
  - winter_moderate 1.3572 -> 0.0000
  - flat 1.6782 -> 0.1292

  At the head every summer_cool cell ships 3.0-3.8 kWh instead of 0, so the seed collapse is closed (ev/race-base.log, ev/race-head.log).

Note: figures-not-reproduced: the body's head race figures (0.0000, 0.0000, 0.0004, 0.0077, 0.0000) and its base shoulder figures (winter_typical 1.7251, flat 0.0001) do not reproduce on this host. Here winter_typical/shoulder reads 1.9945 at base and 1.7870 at head; flat/shoulder 1.3426 at base and 0.0002 at head.
  - A two-cell rerun at the head read flat/summer_cool 0.0043 where the seven-cell run read 0.1292 (ev/race-head-rerun.log). The race is order-dependent within one process, so its sub-0.13 residues are not a stable measurement on this host.
  - The previous head bdf09624 reads 0.1210 and 0.1292 on those two cells (ev/race-prev-bdf09624.log).
  - Bearing on the raise: the body rejects variant A for leaving 0.1287 and 0.1292 on winter_extreme and flat. This head reads 0.1210 and 0.1292 on those cells in one ordering here. The rejection rests on the fixer's host's figures, which this seat could not re-derive. Not re-derived: variant A itself, the stress counts (54/38 evaluations, 122592 simulate steps), MA-MD, and the `start_below_band` four-kernel claim.

Note: harness-unnamed: the review packet reports `Finder's harness: none named`. The body names the finder's scripts only through `$EXPORT` paths, which figure_lint cannot resolve.

## Red checks

None at this head: the classify read is GREEN, and every check in the packet digest is success or skipped. The body's `## Red checks` answers the reds at earlier heads and the cancelled jobs at this head, which have since been rerun green.

## Carry

Carry: dismissed: evidence, not a finding

## Delta diff: git diff ee9bfa8ac5c2c5cc5454f3c636cb627bcb29d565 fe23416d408624f59f3d36dbbcea049d138ec764
diff --git a/custom_components/heatpump_optimizer/__init__.py b/custom_components/heatpump_optimizer/__init__.py
index 459287d196..f40edd1307 100644
--- a/custom_components/heatpump_optimizer/__init__.py
+++ b/custom_components/heatpump_optimizer/__init__.py
@@ -29,10 +29,11 @@ from homeassistant.loader import async_get_integration
 from homeassistant.util import dt as dt_util
 
 from .const import (
+    CONFIG_ENTRY_MINOR_VERSION,
     CONFIG_ENTRY_VERSION,
     DOMAIN,
 )
-from .entry_config import EntryConfig
+from .entry_config import EntryConfig, placed
 
 # Bound here, not via ``_lazy``. Home Assistant 2026 evaluates
 # ``async_setup_entry``'s annotations with ``get_type_hints``, which looks
@@ -203,7 +204,7 @@ async def async_migrate_entry(hass: HomeAssistant, entry: HeatPumpOptimizerConfi
     """Migrate a config entry created by an older version of the integration.
 
     Every option the integration reads is looked up with a default, so older
-    entries only need their version stamped forward. Without this handler Home
+    entries need their keys placed (7.2) and their version stamped forward. Without this handler Home
     Assistant refuses to load entries created before the current
     ``ConfigFlow.VERSION`` and the integration appears broken after an upgrade.
     """
@@ -217,13 +218,26 @@ async def async_migrate_entry(hass: HomeAssistant, entry: HeatPumpOptimizerConfi
         )
         return False
 
-    if entry.version < CONFIG_ENTRY_VERSION:
+    minor = getattr(entry, "minor_version", 1)
+    if entry.version < CONFIG_ENTRY_VERSION or minor < CONFIG_ENTRY_MINOR_VERSION:
         _LOGGER.info(
-            "Migrating Heat Pump Optimizer config entry from version %s to %s",
+            "Migrating Heat Pump Optimizer config entry from version %s.%s to %s.%s",
             entry.version,
+            minor,
             CONFIG_ENTRY_VERSION,
+            CONFIG_ENTRY_MINOR_VERSION,
+        )
+        # 7.2 stores each key in its one place. Placing only moves keys, and
+        # on a key in both sides keeps the options value, the one in force,
+        # so the effective mapping every reader takes is unchanged.
+        data, options = placed({**entry.data, **entry.options})
+        hass.config_entries.async_update_entry(
+            entry,
+            data=data,
+            options=options,
+            version=CONFIG_ENTRY_VERSION,
+            minor_version=CONFIG_ENTRY_MINOR_VERSION,
         )
-        hass.config_entries.async_update_entry(entry, version=CONFIG_ENTRY_VERSION)
 
     return True
 
diff --git a/custom_components/heatpump_optimizer/config_flow.py b/custom_components/heatpump_optimizer/config_flow.py
index 4d721fb548..24858c41b9 100644
--- a/custom_components/heatpump_optimizer/config_flow.py
+++ b/custom_components/heatpump_optimizer/config_flow.py
@@ -42,6 +42,7 @@ class _ShowFormParent(Protocol):
 from .const import (
     FACTORY_RESET_SCOPES,
     DOMAIN,
+    CONFIG_ENTRY_MINOR_VERSION,
     CONFIG_ENTRY_VERSION,
     CONF_TIBBER_TOKEN,
     CONF_PRICE_SOURCE,
@@ -481,6 +482,7 @@ from . import (
     topology,
 )
 from .wood_fuel import wood_furnace_on
+from .entry_config import placed
 from .thermal_model import (
     ThermalParameters,
     dhw_enabled_from_config,
@@ -587,6 +589,11 @@ def entry_identity(user_input: Mapping[str, Any]) -> str:
 _KEEP_ID: UndefinedType = UNDEFINED
 
 
+def _in_force(entry: Any) -> dict[str, Any]:
+    """An entry's configuration in force: setup data with saved options applied."""
+    return {**entry.data, **entry.options}
+
+
 def identity_update(
     hass: HomeAssistant,
     entry: Any,
@@ -609,7 +616,7 @@ def identity_update(
         **(entry.options if options is None else options),
     }
     unique_id = entry_identity(new)
-    if unique_id == entry_identity({**entry.data, **entry.options}):
+    if unique_id == entry_identity(_in_force(entry)):
         return _KEEP_ID
     held = hass.config_entries.async_entry_for_domain_unique_id(DOMAIN, unique_id)
     if held is not None and held is not entry:
@@ -2222,21 +2229,69 @@ def _prefill_fits(key: str, value: Any) -> bool:
     return bool(widget.config["min"] <= value <= widget.config["max"])
 
 
-def _prefill_schema(keys: Iterable[str], values: Mapping[str, Any]) -> vol.Schema:
-    """The pre-fill preview: one flat, suggested field per key.
+#: A suggested key's companion field, shown beside it on a pre-fill page: a
+#: night-mode schedule caps the pump only through its power fraction, and a
+#: schedule kept at the fraction's 1.0 default plans exactly as none (D17-s2-04).
+_PREFILL_PAIRED: Final = {CONF_SILENT_MODE_WINDOWS: CONF_SILENT_MODE_FRACTION}
+
+
+def _prefill_fields(
+    keys: Iterable[str], values: Mapping[str, Any], current: Mapping[str, Any]
+) -> dict[Any, Any]:
+    """The pre-fill preview's fields: one flat, suggested field per key.
 
     Flat, because a suggested value does not reach a field inside a
     ``section()``; suggested rather than defaulted, so a field the user
-    clears is absent from the submit and nothing is written for it.
+    clears is absent from the submit and nothing is written for it. A
+    ``_PREFILL_PAIRED`` companion follows its key, suggested from ``values``
+    or else the value in force.
     """
-    return _options_schema({
+    keys = tuple(keys)
+    shown = dict.fromkeys(
+        name for key in keys for name in (key, _PREFILL_PAIRED.get(key)) if name is not None
+    )
+    in_force = {**_ABSENT_FALLBACKS, **current, **values}
+    return {
         (
-            vol.Optional(key, description={"suggested_value": values[key]})
-            if key in values
+            vol.Optional(key, description={"suggested_value": in_force[key]})
+            if key in values or (key not in keys and key in in_force)
             else vol.Optional(key)
         ): _prefill_row(key).widget
-        for key in keys
-    })
+        for key in shown
+    }
+
+
+def _prefill_schema(
+    keys: Iterable[str], values: Mapping[str, Any], current: Mapping[str, Any]
+) -> vol.Schema:
+    """The options flow's pre-fill preview, with its after-save choice; the
+    setup wizard's page posts none, its navigation being always ``finish_setup``."""
+    return _options_schema(_prefill_fields(keys, values, current))
+
+
+def _prefill_page(
+    flow: _StoredValuesAlwaysFit,
+    step_id: str,
+    schema: vol.Schema,
+    notes: dict[str, str],
+    errors: dict[str, str],
+) -> ConfigFlowResult:
+    """A pre-fill page -- the setup wizard's and the options flow's -- with every
+    placeholder its description and fields read.
+
+    ``device_prefill.disclaimer()`` with no resolution is the empty form, so
+    the pick and a refusal carry the keys the device route overrides; the
+    window placeholders are the night-mode and hot-water fields' own. A
+    refusal passes the preview's ``notes``, so it renders what the preview did.
+    """
+    return flow.async_show_form(
+        step_id=step_id,
+        errors=errors,
+        description_placeholders={
+            **_WINDOW_PLACEHOLDERS, **device_prefill.disclaimer(), **notes,
+        },
+        data_schema=schema,
+    )
 
 
 #: The pre-fill page's device pick. Transient: it names where to read the
@@ -2391,6 +2446,18 @@ def _written_entity_collision(merged: Mapping[str, Any]) -> dict[str, str]:
     return {}
 
 
+def _uncapped_schedule_errors(saved: Mapping[str, Any], current: Mapping[str, Any]) -> dict[str, str]:
+    """A kept night-mode schedule whose power fraction in force is 1.0 caps
+    nothing (D17-s2-04); the pre-fill page shows the fraction beside it
+    (``_PREFILL_PAIRED``), so the refusal lands on that field."""
+    if not saved.get(CONF_SILENT_MODE_WINDOWS):
+        return {}
+    fraction = {**current, **saved}.get(CONF_SILENT_MODE_FRACTION, DEFAULT_SILENT_MODE_FRACTION)
+    if float(fraction) >= 1.0:
+        return {CONF_SILENT_MODE_FRACTION: "silent_mode_fraction_uncapped"}
+    return {}
+
+
 def _prefill_errors(saved: dict[str, Any], current: dict[str, Any]) -> dict[str, str]:
     """The refusals of the pages the suggested keys live on, for this save.
 
@@ -2414,6 +2481,8 @@ def _prefill_errors(saved: dict[str, Any], current: dict[str, Any]) -> dict[str,
             problem = "silent_mode_window_too_short"
         if problem is not None:
             errors[key] = problem
+    if CONF_SILENT_MODE_WINDOWS not in errors:
+        errors.update(_uncapped_schedule_errors(saved, current))
     if {CONF_DHW_SETPOINT, CONF_DHW_MIN_TEMP} & saved.keys() and _dhw_min_too_close(
         saved, current
     ):
@@ -2449,13 +2518,18 @@ def _omit_unstored_computed(
     JSON bytes without changing the setting.
     """
     cleaned = dict(user_input)
-    for row in _OPTION_FIELDS:
-        if not isinstance(row.default, _Computed):
-            continue
+    computed_rows = [row for row in _OPTION_FIELDS if isinstance(row.default, _Computed)]
+    # A computed default is the one the saved configuration would derive: the
+    # weekday this save sets, not the one it replaces (D17-s1-02). Over the
+    # stored one, a weekend value shown and kept equals the OLD weekday's
+    # default, is dropped as unstored, and follows the new weekday instead.
+    computed_keys = {row.key for row in computed_rows}
+    saving = {**current, **{k: v for k, v in cleaned.items() if k not in computed_keys}}
+    for row in computed_rows:
         if row.key in current or row.key not in cleaned:
             continue
         try:
-            computed = row.default.of(current, hass)
+            computed = row.default.of(saving, hass)
         except Exception:  # noqa: BLE001 - leave a value we cannot recompute
             continue
         if _same_setting(computed, cleaned[row.key]):
@@ -2631,13 +2705,15 @@ class HeatPumpOptimizerConfigFlow(
     """Handle a config flow for Heat Pump Optimizer."""
 
     VERSION = CONFIG_ENTRY_VERSION
+    MINOR_VERSION = CONFIG_ENTRY_MINOR_VERSION
 
-    #: The suggested keys the offer page is showing, between its two submits
-    #: (#1067 W1067-POST1). None means the page is being opened; a tuple means
-    #: the preview was computed and the next submit is the one that keeps or
-    #: drops what it offered -- the same two-submit shape as the options
-    #: flow's pre-fill page, with the wizard's own data as the target.
-    _device_prefill: tuple[str, ...] | None = None
+    #: The suggested keys the offer page is showing and the preview's notes,
+    #: between its two submits (#1067 W1067-POST1). None means the page is
+    #: being opened; a pair means the preview was computed and the next submit
+    #: is the one that keeps or drops what it offered -- the options flow's
+    #: ``_prefill`` shape, with the wizard's own data as the target, so a
+    #: refusal re-renders the notes the preview showed.
+    _device_prefill: tuple[tuple[str, ...], dict[str, str]] | None = None
 
     def __init__(self) -> None:
         """Initialize the config flow."""
@@ -2699,7 +2775,7 @@ class HeatPumpOptimizerConfigFlow(
         schema = vol.Schema(_user_credentials_fields())
         if self._reconfigure_entry is not None:
             schema = self.add_suggested_values_to_schema(
-                schema, self._reconfigure_entry.data
+                schema, _in_force(self._reconfigure_entry)
             )
         return self.async_show_form(
             step_id="user",
@@ -2742,7 +2818,7 @@ class HeatPumpOptimizerConfigFlow(
         if self._reconfigure_entry is not None:
             schema = self.add_suggested_values_to_schema(
                 vol.Schema(_user_sensors_fields(self.hass)),
-                self._reconfigure_entry.data,
+                _in_force(self._reconfigure_entry),
             )
         else:
             schema = vol.Schema(_user_sensors_sections(self.hass))
@@ -2752,24 +2828,10 @@ class HeatPumpOptimizerConfigFlow(
         )
 
     def _device_prefill_form(
-        self,
-        schema: vol.Schema,
-        notes: dict[str, str],
-        errors: dict[str, str],
+        self, schema: vol.Schema, notes: dict[str, str], errors: dict[str, str]
     ) -> ConfigFlowResult:
-        """The offer page, with the placeholders its description always reads.
-
-        ``device_prefill.disclaimer()`` with no resolution is the empty form,
-        so the pick and the refusal both carry the two keys the device route
-        overrides rather than leaving the description's braces unrendered --
-        the options flow's pre-fill page, and its reason, in one place.
-        """
-        return self.async_show_form(
-            step_id="device_prefill",
-            errors=errors,
-            description_placeholders={**device_prefill.disclaimer(), **notes},
-            data_schema=schema,
-        )
+        """The setup wizard's pre-fill page (``_prefill_page``)."""
+        return _prefill_page(self, "device_prefill", schema, notes, errors)
 
     async def async_step_device_prefill(
         self, user_input: dict[str, Any] | None = None
@@ -2842,11 +2904,11 @@ class HeatPumpOptimizerConfigFlow(
                     resolution, _display_names(self.hass, records)
                 ),
             }
-            self._device_prefill = tuple(suggested)
+            self._device_prefill = (tuple(suggested), notes)
             return self._device_prefill_form(
-                _prefill_schema(suggested, suggested), notes, {}
+                vol.Schema(_prefill_fields(suggested, suggested, self._data)), notes, {}
             )
-        keys = self._device_prefill
+        keys, notes = self._device_prefill
         saved = {
             key: value
             for key, value in _flatten_section_input(user_input).items()
@@ -2854,7 +2916,9 @@ class HeatPumpOptimizerConfigFlow(
         }
         errors = _prefill_errors(saved, {**_ABSENT_FALLBACKS, **self._data})
         if errors:
-            return self._device_prefill_form(_prefill_schema(keys, saved), {}, errors)
+            return _prefill_page(
+                self, "device_prefill", vol.Schema(_prefill_fields(keys, saved, self._data)), notes, errors
+            )
         self._device_prefill = None
         self._data.update(
             _omit_unstored_defaults(
@@ -2870,7 +2934,7 @@ class HeatPumpOptimizerConfigFlow(
         """Write the first screen's answers back onto the entry they came from."""
         entry = self._reconfigure_entry
         assert entry is not None
-        data = dict(entry.data)
+        effective = _in_force(entry)
         for key in (
             str(getattr(marker, "schema", marker))
             for marker in _first_screen_schema(self.hass).schema
@@ -2879,14 +2943,18 @@ class HeatPumpOptimizerConfigFlow(
             # using; the user step's own description promises exactly that,
             # so the cleared value must not survive the update.
             if key in user_input:
-                data[key] = user_input[key]
+                effective[key] = user_input[key]
             else:
-                data.pop(key, None)
+                effective.pop(key, None)
+        # Both sides in one write, each key in its one place: an answer
+        # written to data under an options value would be shadowed by it.
+        data, options = placed(effective)
         self.hass.config_entries.async_update_entry(
             entry,
             data=data,
+            options=options,
             unique_id=self.unique_id,
-            title=data.get(CONF_NAME, entry.title),
+            title=effective.get(CONF_NAME, entry.title),
         )
         await self.hass.config_entries.async_reload(entry.entry_id)
         return self.async_abort(reason="reconfigure_successful")
@@ -2939,10 +3007,12 @@ class HeatPumpOptimizerConfigFlow(
         return _setup_overview_form(self, self._data, last_step=True)
 
     def _create_setup_entry(self) -> ConfigFlowResult:
-        """Persist whatever the wizard has collected so far."""
+        """Persist whatever the wizard has collected so far, each key in its one place."""
+        data, options = placed(self._data)
         return self.async_create_entry(
             title=self._data.get(CONF_NAME, "Heat Pump Optimizer"),
-            data=self._data,
+            data=data,
+            options=options,
         )
 
     async def async_step_quick_setup(
@@ -3303,11 +3373,16 @@ class HeatPumpOptimizerConfigFlow(
             if verdict == "ok":
                 entry = self._reauth_entry
                 assert entry is not None
-                data = {**entry.data, CONF_TIBBER_TOKEN: user_input[CONF_TIBBER_TOKEN]}
+                data, options = placed(
+                    {**_in_force(entry), CONF_TIBBER_TOKEN: user_input[CONF_TIBBER_TOKEN]}
+                )
                 # The token is identity: a unique id left on the old one let
                 # a fresh setup with the new token add the plant twice.
                 self.hass.config_entries.async_update_entry(
-                    entry, data=data, unique_id=identity_update(self.hass, entry, data=data)
+                    entry,
+                    data=data,
+                    options=options,
+                    unique_id=identity_update(self.hass, entry, data=data, options=options),
                 )
                 await self.hass.config_entries.async_reload(entry.entry_id)
                 return self.async_abort(reason="reauth_successful")
@@ -3390,7 +3465,7 @@ class HeatPumpOptimizerOptionsFlow(_StoredValuesAlwaysFit, config_entries.Option
     @property
     def _current(self) -> dict[str, Any]:
         """Effective configuration: setup data with saved options applied."""
-        return {**self._entry.data, **self._entry.options}
+        return _in_force(self._entry)
 
     def _save(self, user_input: dict[str, Any]) -> ConfigFlowResult:
         """Persist one page without discarding settings from the other pages."""
@@ -4029,21 +4104,8 @@ class HeatPumpOptimizerOptionsFlow(_StoredValuesAlwaysFit, config_entries.Option
     def _prefill_form(
         self, schema: vol.Schema, notes: dict[str, str], errors: dict[str, str]
     ) -> ConfigFlowResult:
-        """The page, with the placeholders its description always reads.
-
-        ``device_prefill.disclaimer()`` with no resolution is the empty form,
-        so the prefix route and the refusal below carry the same two keys the
-        device route overrides rather than leaving the description's braces
-        unrendered.
-        """
-        return self.async_show_form(
-            step_id="modbus_prefill",
-            errors=errors,
-            description_placeholders={
-                **_WINDOW_PLACEHOLDERS, **device_prefill.disclaimer(), **notes,
-            },
-            data_schema=schema,
-        )
+        """The options flow's pre-fill page (``_prefill_page``)."""
+        return _prefill_page(self, "modbus_prefill", schema, notes, errors)
 
     async def async_step_modbus_prefill(
         self, user_input: dict[str, Any] | None = None
@@ -4116,7 +4178,7 @@ class HeatPumpOptimizerOptionsFlow(_StoredValuesAlwaysFit, config_entries.Option
             }
             notes = {**modbus_prefill.notes(snap), **sourced}
             self._prefill = (prefix if snap else None, tuple(suggested), notes)
-            return self._prefill_form(_prefill_schema(suggested, suggested), notes, {})
+            return self._prefill_form(_prefill_schema(suggested, suggested, current), notes, {})
         matched_prefix, keys, notes = self._prefill
         saved = {
             key: value
@@ -4125,7 +4187,7 @@ class HeatPumpOptimizerOptionsFlow(_StoredValuesAlwaysFit, config_entries.Option
         }
         errors = _prefill_errors(saved, current)
         if errors:
-            return self._prefill_form(_prefill_schema(keys, saved), notes, errors)
+            return self._prefill_form(_prefill_schema(keys, saved, current), notes, errors)
         if self._prefill_offer is not None:
             # Carried from the first submit, and written with the rest of what
             # the page keeps: an off switch left off is an unchanged default
diff --git a/custom_components/heatpump_optimizer/const.py b/custom_components/heatpump_optimizer/const.py
index 9f2b6ee1e7..d21804be3e 100644
--- a/custom_components/heatpump_optimizer/const.py
+++ b/custom_components/heatpump_optimizer/const.py
@@ -22,6 +22,10 @@ PLATFORMS: Final = [
 # Schema version of the config entry. Bump when stored keys change in a way
 # that needs migrating, and handle it in ``async_migrate_entry``.
 CONFIG_ENTRY_VERSION: Final = 7
+# The minor version: 2 stores each key in its one place (``entry_config.placed``).
+# Minor, so a release that knows only 7.1 still loads the entry: it refuses only
+# a newer major, and reads ``{**data, **options}``, which placing leaves equal.
+CONFIG_ENTRY_MINOR_VERSION: Final = 2
 
 # How many intervals the forecast-accuracy ring keeps, and the cap on the
 # tariff's whole-house samples and the store's accuracy domain. At the default
@@ -775,9 +779,9 @@ CONF_HEAT_PUMP_COP_PARTLOAD_DERATE: Final = "heat_pump_cop_partload_derate"
 # Two-zone model parameters
 #
 # Whether the two-zone model runs was historically inferred from whether any
-# zone key exists at all — which an options page can never undo, because the
-# initial flow writes the keys into entry.data where options cannot erase
-# them. The mode is the explicit override (v4.0.0): "auto" (the default, and
+# zone key exists at all — which an options page can never undo, because an
+# options page saves a value and never removes a key. The mode is the explicit
+# override (v4.0.0): "auto" (the default, and
 # what every untouched install effectively has) keeps the presence rule
 # byte-for-byte; "on"/"off" force the model regardless of which keys exist.
 CONF_TWO_ZONE_MODE: Final = "two_zone_mode"
diff --git a/custom_components/heatpump_optimizer/entry_config.py b/custom_components/heatpump_optimizer/entry_config.py
index 71f5d73017..4a19640d9a 100644
--- a/custom_components/heatpump_optimizer/entry_config.py
+++ b/custom_components/heatpump_optimizer/entry_config.py
@@ -345,6 +345,20 @@ FACTORY_KEPT: Mapping[str, str] = MappingProxyType({
 
 Settings = tuple[Mapping[str, Any], Mapping[str, Any]]
 
+#: The keys ``entry.data`` stores: the first-screen answers no options page
+#: edits. Every other key is stored in ``entry.options``, so a key has one
+#: place and every writer agrees with the reader, ``{**data, **options}``
+#: (R11-SEAM-config). ``tests/config_flow_steps.py`` derives the set from the
+#: first screen and the options registry and fails when it moves.
+DATA_ONLY: frozenset[str] = frozenset({"name"})
+
+
+def placed(effective: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
+    """``effective`` -- an entry's ``{**data, **options}`` -- as the (data, options)
+    pair storing each key in its one place: ``DATA_ONLY`` in data, the rest in options."""
+    return ({k: v for k, v in effective.items() if k in DATA_ONLY},
+            {k: v for k, v in effective.items() if k not in DATA_ONLY})
+
 
 def settings_of(data: Mapping[str, Any], options: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
     """The (data, options) keys a factory reset drops: what its undo point keeps."""
@@ -394,7 +408,10 @@ def undone_settings(
         return None
     unpinned = [{k: v for k, v in side.items() if k not in FACTORY_PINNED} for side in (data, options)]
     wiring = ({**unpinned[0], **pinned[0]}, {**unpinned[1], **pinned[1]})
-    return with_settings(wiring, (settings[0], settings[1]))
+    # A record written before the placement migration holds settings in data:
+    # placing the restored pair stores each where the entry now keeps it.
+    data_side, options_side = with_settings(wiring, (settings[0], settings[1]))
+    return placed({**data_side, **options_side})
 
 
 def factory_settings(
@@ -409,4 +426,5 @@ def factory_settings(
     those would make it single-zone; the DHW and wood flags likewise.
     """
     pinned = dict(zip(FACTORY_PINNED, (const.TWO_ZONE_MODE_ON if two_zone else const.TWO_ZONE_MODE_OFF, dhw, wood)))
-    return with_settings((data, {**options, **pinned}), ({}, {}))
+    data_side, options_side = with_settings((data, {**options, **pinned}), ({}, {}))
+    return placed({**data_side, **options_side})
diff --git a/custom_components/heatpump_optimizer/strings.json b/custom_components/heatpump_optimizer/strings.json
index a2af59d608..b110a33448 100644
--- a/custom_components/heatpump_optimizer/strings.json
+++ b/custom_components/heatpump_optimizer/strings.json
@@ -342,6 +342,7 @@
           "dhw_legionella_temperature": "Anti-legionella temperature",
           "dhw_legionella_interval_days": "Anti-legionella interval",
           "silent_mode_windows": "Pump's own night-mode schedule",
+          "silent_mode_power_fraction": "Power kept in silent mode",
           "heat_pump_max_power": "Heat pump max power (kW)",
           "space_setpoint_unit": "What that set-point entity expects",
           "mixing_valve_write_target_kind": "What the control entity expects",
@@ -350,8 +351,7 @@
           "dhw_temp_entity": "Hot water tank temperature sensor",
           "heat_pump_supply_temp_entity": "Supply (flow) water temperature",
           "heat_pump_return_temp_entity": "Return water temperature",
-          "heat_pump_capacity_limited_entity": "Capacity limited (night mode)",
-          "after_save": "After saving"
+          "heat_pump_capacity_limited_entity": "Capacity limited (night mode)"
         },
         "data_description": {
           "prefill_device": "The pump's own device. Its entities are mapped to settings by that integration's published definitions, or by their names where nothing is published - not from a reading of your unit - so check the suggestions before keeping them. Leave it empty to continue setup without the pre-fill.",
@@ -361,6 +361,7 @@
           "dhw_legionella_temperature": "Read from the pump's DHW anti-legionella setpoint register (0195H), times 0.1.",
           "dhw_legionella_interval_days": "Seven days divided by the number of days set in the pump's anti-legionella schedule (02CAH), rounded down.",
           "silent_mode_windows": "Read from the pump's night mode start and end registers (0206H, 0207H), each hour times 256 plus minute.",
+          "silent_mode_power_fraction": "The share of the heat pump's maximum electrical power it still runs at inside the silent mode schedule. 1.0 caps nothing. The slider stops at the same floor as the measured capacity limit, so this can trim the plan but never leave the house without heat.",
           "heat_pump_max_power": "The pump's unit capacity register, in kW of heat, divided by the nominal COP in force.",
           "space_setpoint_unit": "Suggested as flow when the pump's control mode register (100DH) is water temperature control.",
           "mixing_valve_write_target_kind": "Suggested as flow on water temperature control, only where the two-zone model the building page requires for it is configured.",
@@ -369,8 +370,7 @@
           "dhw_temp_entity": "The heat pump's hot water tank temperature sensor, suggested only while this slot is empty.",
           "heat_pump_supply_temp_entity": "The heat pump's leaving water temperature (T1) sensor, suggested only while this slot is empty.",
           "heat_pump_return_temp_entity": "The heat pump's entering water temperature (Tw-in) sensor, suggested only while this slot is empty.",
-          "heat_pump_capacity_limited_entity": "The heat pump's night mode (frequency reduction) active sensor, suggested only while this slot is empty.",
-          "after_save": "Setup carries on to the next page whichever you choose; nothing is saved until setup finishes."
+          "heat_pump_capacity_limited_entity": "The heat pump's night mode (frequency reduction) active sensor, suggested only while this slot is empty."
         }
       }
     },
@@ -382,6 +382,7 @@
       "invalid_dhw_windows": "Those time frames could not be read. Use 24-hour times separated by commas, for example \"06:00-08:30, 17:00-22:00\".",
       "dhw_window_too_short": "A hot water time frame is shorter than {min_window_minutes} minutes. The plan is made in {min_window_minutes}-minute steps, so a shorter frame can fall between two steps and never take effect.",
       "silent_mode_window_too_short": "A silent mode time frame is shorter than {min_window_minutes} minutes. The plan is made in {min_window_minutes}-minute steps, so a shorter frame can fall between two steps and never take effect.",
+      "silent_mode_fraction_uncapped": "A kept silent mode schedule needs the power kept in silent mode below 1.0: at 1.0 the schedule caps nothing. Lower it, or clear the schedule.",
       "dhw_min_too_close": "A hot water minimum this close to the setpoint leaves the tank no working band; keep it at least 5 °C below the setpoint.",
       "min_above_target": "The minimum temperature is above the target temperature.",
       "max_below_target": "The maximum temperature is below the target temperature.",
@@ -1547,6 +1548,7 @@
           "dhw_legionella_temperature": "Anti-legionella temperature",
           "dhw_legionella_interval_days": "Anti-legionella interval",
           "silent_mode_windows": "Pump's own night-mode schedule",
+          "silent_mode_power_fraction": "Power kept in silent mode",
           "heat_pump_max_power": "Heat pump max power (kW)",
           "space_setpoint_unit": "What that set-point entity expects",
           "mixing_valve_write_target_kind": "What the control entity expects",
@@ -1568,6 +1570,7 @@
           "dhw_legionella_temperature": "Read from the pump's DHW anti-legionella setpoint register (0195H), times 0.1.",
           "dhw_legionella_interval_days": "Seven days divided by the number of days set in the pump's anti-legionella schedule (02CAH), rounded down.",
           "silent_mode_windows": "Read from the pump's night mode start and end registers (0206H, 0207H), each hour times 256 plus minute.",
+          "silent_mode_power_fraction": "The share of the heat pump's maximum electrical power it still runs at inside the silent mode schedule. 1.0 caps nothing. The slider stops at the same floor as the measured capacity limit, so this can trim the plan but never leave the house without heat.",
           "heat_pump_max_power": "The pump's unit capacity register, in kW of heat, divided by the nominal COP in force.",
           "space_setpoint_unit": "Suggested as flow when the pump's control mode register (100DH) is water temperature control.",
           "mixing_valve_write_target_kind": "Suggested as flow on water temperature control, only where the two-zone model the building page requires for it is configured.",
@@ -1603,6 +1606,7 @@
       "dhw_window_too_short": "A hot water time frame is shorter than {min_window_minutes} minutes. The plan is made in {min_window_minutes}-minute steps, so a shorter frame can fall between two steps and never take effect.",
       "freq_control_needs_number": "Control writes the frequency through a number entity. Choose one, or keep the mode on observe: a frequency sensor alone can only be observed.",
       "silent_mode_window_too_short": "A silent mode time frame is shorter than {min_window_minutes} minutes. The plan is made in {min_window_minutes}-minute steps, so a shorter frame can fall between two steps and never take effect.",
+      "silent_mode_fraction_uncapped": "A kept silent mode schedule needs the power kept in silent mode below 1.0: at 1.0 the schedule caps nothing. Lower it, or clear the schedule.",
       "disinfection_control_needs_entity": "Control turns the pump's disinfection switch on and off, so it needs one. Pick the switch above, or set the mode back to observe.",
       "dhw_min_too_close": "A hot water minimum this close to the setpoint leaves the tank no working band; keep it at least 5 °C below the setpoint.",
       "invalid_grid_fee_rules": "Those fee rules could not be read. One rule per line, like \"Nov-Mar Mon-Fri 06:00-22:00 = 0.25\".",
diff --git a/custom_components/heatpump_optimizer/thermal_model.py b/custom_components/heatpump_optimizer/thermal_model.py
index 86c79b9ef5..0a14a852e1 100644
--- a/custom_components/heatpump_optimizer/thermal_model.py
+++ b/custom_components/heatpump_optimizer/thermal_model.py
@@ -1153,10 +1153,10 @@ def two_zone_from_config(config: Mapping[str, Any]) -> bool:
     Two-zone and DHW are inferred from whether their settings are present
     at all, rather than from a flag, so an entry written before either
     existed keeps working. The mode key (v4.0.0) is an explicit override
-    on top: presence alone can never turn the model *off*, because the
-    initial flow writes the zone keys into entry.data where the options
-    flow cannot erase them. "auto" — the default, so every entry without
-    the key — is the presence rule unchanged; an unknown value is
+    on top: presence alone can never turn the model *off*, because an
+    options page saves a value and never removes a zone key. "auto" — the
+    default, so every entry without the key — is the presence rule
+    unchanged; an unknown value is
     treated as "auto" rather than silently disabling a running model.
     """
     two_zone_mode = str(
diff --git a/custom_components/heatpump_optimizer/translations/de.json b/custom_components/heatpump_optimizer/translations/de.json
index 71027b33d5..e9c245c876 100644
--- a/custom_components/heatpump_optimizer/translations/de.json
+++ b/custom_components/heatpump_optimizer/translations/de.json
@@ -342,6 +342,7 @@
           "dhw_legionella_temperature": "Temperatur der Legionellenschaltung",
           "dhw_legionella_interval_days": "Intervall der Legionellenschaltung",
           "silent_mode_windows": "Eigener Nachtmodus-Zeitplan der Pumpe",
+          "silent_mode_power_fraction": "Im Flüstermodus beibehaltene Leistung",
           "heat_pump_max_power": "Maximale Leistung der Wärmepumpe (kW)",
           "space_setpoint_unit": "Was diese Sollwert-Entität erwartet",
           "mixing_valve_write_target_kind": "Was die Steuerentität erwartet",
@@ -350,8 +351,7 @@
           "dhw_temp_entity": "Temperatursensor Warmwasserspeicher",
           "heat_pump_supply_temp_entity": "Vorlauftemperatur",
           "heat_pump_return_temp_entity": "Rücklauftemperatur",
-          "heat_pump_capacity_limited_entity": "Leistung begrenzt (Nachtmodus)",
-          "after_save": "Nach dem Speichern"
+          "heat_pump_capacity_limited_entity": "Leistung begrenzt (Nachtmodus)"
         },
         "data_description": {
           "prefill_device": "Das eigene Gerät der Pumpe. Seine Entitäten werden anhand der veröffentlichten Definitionen dieser Integration oder, wo nichts veröffentlicht ist, anhand ihrer Namen den Einstellungen zugeordnet – nicht aus einer Auslesung deines Geräts –, prüfe die Vorschläge daher, bevor du sie übernimmst. Lass es leer, um die Einrichtung ohne Vorausfüllung fortzusetzen.",
@@ -361,6 +361,7 @@
           "dhw_legionella_temperature": "Gelesen aus dem Register für den Legionellen-Sollwert der Pumpe (0195H), mal 0,1.",
           "dhw_legionella_interval_days": "Sieben Tage geteilt durch die Anzahl der im Legionellen-Zeitplan der Pumpe (02CAH) gesetzten Tage, abgerundet.",
           "silent_mode_windows": "Gelesen aus den Start- und Ende-Registern des Nachtmodus der Pumpe (0206H, 0207H), jeweils Stunde mal 256 plus Minute.",
+          "silent_mode_power_fraction": "Der Anteil der maximalen elektrischen Leistung der Wärmepumpe, mit dem sie im Flüstermodus-Zeitplan noch läuft. 1.0 begrenzt nichts. Der Regler endet an derselben Untergrenze wie die gemessene Leistungsgrenze, sodass dies den Plan zwar beschneiden, das Haus aber nie ohne Wärme lassen kann.",
           "heat_pump_max_power": "Das Register für die Gerätekapazität der Pumpe, in kW Wärme, geteilt durch den geltenden Nenn-COP.",
           "space_setpoint_unit": "Wird als Vorlauf vorgeschlagen, wenn das Register für den Regelmodus der Pumpe (100DH) auf Wassertemperaturregelung steht.",
           "mixing_valve_write_target_kind": "Wird bei Wassertemperaturregelung als Vorlauf vorgeschlagen, nur wenn das dafür erforderliche Zwei-Zonen-Modell der Gebäudeseite konfiguriert ist.",
@@ -369,8 +370,7 @@
           "dhw_temp_entity": "Der Temperatursensor des Warmwasserspeichers der Wärmepumpe, wird nur vorgeschlagen, solange dieser Platz leer ist.",
           "heat_pump_supply_temp_entity": "Der Sensor für die Austrittswassertemperatur (T1) der Wärmepumpe, wird nur vorgeschlagen, solange dieser Platz leer ist.",
           "heat_pump_return_temp_entity": "Der Sensor für die Eintrittswassertemperatur (Tw-in) der Wärmepumpe, wird nur vorgeschlagen, solange dieser Platz leer ist.",
-          "heat_pump_capacity_limited_entity": "Der Sensor der Wärmepumpe für aktiven Nachtmodus (Frequenzreduzierung), wird nur vorgeschlagen, solange dieser Platz leer ist.",
-          "after_save": "Die Einrichtung geht unabhängig von deiner Wahl auf der nächsten Seite weiter; gespeichert wird erst, wenn die Einrichtung abgeschlossen ist."
+          "heat_pump_capacity_limited_entity": "Der Sensor der Wärmepumpe für aktiven Nachtmodus (Frequenzreduzierung), wird nur vorgeschlagen, solange dieser Platz leer ist."
         }
       }
     },
@@ -382,6 +382,7 @@
       "invalid_dhw_windows": "Diese Zeitfenster konnten nicht gelesen werden. Verwende 24-Stunden-Zeiten, durch Kommas getrennt, zum Beispiel \"06:00-08:30, 17:00-22:00\".",
       "dhw_window_too_short": "Ein Warmwasser-Zeitfenster ist kürzer als {min_window_minutes} Minuten. Der Plan wird in {min_window_minutes}-Minuten-Schritten erstellt, daher kann ein kürzeres Fenster zwischen zwei Schritte fallen und nie wirksam werden.",
       "silent_mode_window_too_short": "Ein Flüstermodus-Zeitfenster ist kürzer als {min_window_minutes} Minuten. Der Plan wird in {min_window_minutes}-Minuten-Schritten erstellt, daher kann ein kürzeres Fenster zwischen zwei Schritte fallen und nie wirksam werden.",
+      "silent_mode_fraction_uncapped": "Ein übernommener Flüstermodus-Zeitplan braucht eine im Flüstermodus beibehaltene Leistung unter 1.0: bei 1.0 begrenzt der Zeitplan nichts. Senken Sie sie oder leeren Sie den Zeitplan.",
       "dhw_min_too_close": "Ein Warmwasser-Minimum so nahe am Sollwert lässt dem Speicher kein Arbeitsband; halte mindestens 5 °C Abstand unter dem Sollwert.",
       "min_above_target": "Die Mindesttemperatur liegt über der Zieltemperatur.",
       "max_below_target": "Die Höchsttemperatur liegt unter der Zieltemperatur.",
@@ -1547,6 +1548,7 @@
           "dhw_legionella_temperature": "Temperatur der Legionellenschaltung",
           "dhw_legionella_interval_days": "Intervall der Legionellenschaltung",
           "silent_mode_windows": "Eigener Nachtmodus-Zeitplan der Pumpe",
+          "silent_mode_power_fraction": "Im Flüstermodus beibehaltene Leistung",
           "heat_pump_max_power": "Maximale Leistung der Wärmepumpe (kW)",
           "space_setpoint_unit": "Was diese Sollwert-Entität erwartet",
           "mixing_valve_write_target_kind": "Was die Steuerentität erwartet",
@@ -1568,6 +1570,7 @@
           "dhw_legionella_temperature": "Gelesen aus dem Register für den Legionellen-Sollwert des Warmwassers der Pumpe (0195H), mal 0,1.",
           "dhw_legionella_interval_days": "Sieben Tage geteilt durch die Anzahl der im Legionellen-Zeitplan der Pumpe gesetzten Tage (02CAH), abgerundet.",
           "silent_mode_windows": "Gelesen aus den Start- und Ende-Registern des Nachtmodus der Pumpe (0206H, 0207H), jeweils Stunde mal 256 plus Minute.",
+          "silent_mode_power_fraction": "Der Anteil der maximalen elektrischen Leistung der Wärmepumpe, mit dem sie im Flüstermodus-Zeitplan noch läuft. 1.0 begrenzt nichts. Der Regler endet an derselben Untergrenze wie die gemessene Leistungsgrenze, sodass dies den Plan zwar beschneiden, das Haus aber nie ohne Wärme lassen kann.",
           "heat_pump_max_power": "Das Register für die Nennleistung der Pumpe, in kW Wärme, geteilt durch die geltende nominale Leistungszahl (COP).",
           "space_setpoint_unit": "Wird als Vorlauf vorgeschlagen, wenn das Register für den Regelmodus der Pumpe (100DH) auf Wassertemperaturregelung steht.",
           "mixing_valve_write_target_kind": "Wird bei Wassertemperaturregelung als Vorlauf vorgeschlagen, nur wenn das dafür erforderliche Zwei-Zonen-Modell der Gebäudeseite konfiguriert ist.",
@@ -1603,6 +1606,7 @@
       "dhw_window_too_short": "Ein Warmwasser-Zeitfenster ist kürzer als {min_window_minutes} Minuten. Der Plan wird in {min_window_minutes}-Minuten-Schritten erstellt, daher kann ein kürzeres Fenster zwischen zwei Schritte fallen und nie wirksam werden.",
       "freq_control_needs_number": "Steuern schreibt die Frequenz über eine Number-Entität. Wähle eine aus oder belasse den Modus auf Beobachten: Ein Frequenzsensor allein kann nur beobachtet werden.",
       "silent_mode_window_too_short": "Ein Flüstermodus-Zeitfenster ist kürzer als {min_window_minutes} Minuten. Der Plan wird in {min_window_minutes}-Minuten-Schritten erstellt, daher kann ein kürzeres Fenster zwischen zwei Schritte fallen und nie wirksam werden.",
+      "silent_mode_fraction_uncapped": "Ein übernommener Flüstermodus-Zeitplan braucht eine im Flüstermodus beibehaltene Leistung unter 1.0: bei 1.0 begrenzt der Zeitplan nichts. Senken Sie sie oder leeren Sie den Zeitplan.",
       "disinfection_control_needs_entity": "Steuern schaltet den Desinfektionsschalter der Pumpe ein und aus und braucht daher einen. Wähle oben den Schalter oder setze den Modus zurück auf Beobachten.",
       "dhw_min_too_close": "Ein Warmwasser-Minimum so nahe am Sollwert lässt dem Speicher kein Arbeitsband; halte mindestens 5 °C Abstand unter dem Sollwert.",
       "invalid_grid_fee_rules": "Diese Entgeltregeln konnten nicht gelesen werden. Eine Regel pro Zeile, etwa „Nov-Mar Mon-Fri 06:00-22:00 = 0.25“.",
diff --git a/custom_components/heatpump_optimizer/translations/en.json b/custom_components/heatpump_optimizer/translations/en.json
index a2af59d608..b110a33448 100644
--- a/custom_components/heatpump_optimizer/translations/en.json
+++ b/custom_components/heatpump_optimizer/translations/en.json
@@ -342,6 +342,7 @@
           "dhw_legionella_temperature": "Anti-legionella temperature",
           "dhw_legionella_interval_days": "Anti-legionella interval",
           "silent_mode_windows": "Pump's own night-mode schedule",
+          "silent_mode_power_fraction": "Power kept in silent mode",
           "heat_pump_max_power": "Heat pump max power (kW)",
           "space_setpoint_unit": "What that set-point entity expects",
           "mixing_valve_write_target_kind": "What the control entity expects",
@@ -350,8 +351,7 @@
           "dhw_temp_entity": "Hot water tank temperature sensor",
           "heat_pump_supply_temp_entity": "Supply (flow) water temperature",
           "heat_pump_return_temp_entity": "Return water temperature",
-          "heat_pump_capacity_limited_entity": "Capacity limited (night mode)",
-          "after_save": "After saving"
+          "heat_pump_capacity_limited_entity": "Capacity limited (night mode)"
         },
         "data_description": {
           "prefill_device": "The pump's own device. Its entities are mapped to settings by that integration's published definitions, or by their names where nothing is published - not from a reading of your unit - so check the suggestions before keeping them. Leave it empty to continue setup without the pre-fill.",
@@ -361,6 +361,7 @@
           "dhw_legionella_temperature": "Read from the pump's DHW anti-legionella setpoint register (0195H), times 0.1.",
           "dhw_legionella_interval_days": "Seven days divided by the number of days set in the pump's anti-legionella schedule (02CAH), rounded down.",
           "silent_mode_windows": "Read from the pump's night mode start and end registers (0206H, 0207H), each hour times 256 plus minute.",
+          "silent_mode_power_fraction": "The share of the heat pump's maximum electrical power it still runs at inside the silent mode schedule. 1.0 caps nothing. The slider stops at the same floor as the measured capacity limit, so this can trim the plan but never leave the house without heat.",
           "heat_pump_max_power": "The pump's unit capacity register, in kW of heat, divided by the nominal COP in force.",
           "space_setpoint_unit": "Suggested as flow when the pump's control mode register (100DH) is water temperature control.",
           "mixing_valve_write_target_kind": "Suggested as flow on water temperature control, only where the two-zone model the building page requires for it is configured.",
@@ -369,8 +370,7 @@
           "dhw_temp_entity": "The heat pump's hot water tank temperature sensor, suggested only while this slot is empty.",
           "heat_pump_supply_temp_entity": "The heat pump's leaving water temperature (T1) sensor, suggested only while this slot is empty.",
           "heat_pump_return_temp_entity": "The heat pump's entering water temperature (Tw-in) sensor, suggested only while this slot is empty.",
-          "heat_pump_capacity_limited_entity": "The heat pump's night mode (frequency reduction) active sensor, suggested only while this slot is empty.",
-          "after_save": "Setup carries on to the next page whichever you choose; nothing is saved until setup finishes."
+          "heat_pump_capacity_limited_entity": "The heat pump's night mode (frequency reduction) active sensor, suggested only while this slot is empty."
         }
       }
     },
@@ -382,6 +382,7 @@
       "invalid_dhw_windows": "Those time frames could not be read. Use 24-hour times separated by commas, for example \"06:00-08:30, 17:00-22:00\".",
       "dhw_window_too_short": "A hot water time frame is shorter than {min_window_minutes} minutes. The plan is made in {min_window_minutes}-minute steps, so a shorter frame can fall between two steps and never take effect.",
       "silent_mode_window_too_short": "A silent mode time frame is shorter than {min_window_minutes} minutes. The plan is made in {min_window_minutes}-minute steps, so a shorter frame can fall between two steps and never take effect.",
+      "silent_mode_fraction_uncapped": "A kept silent mode schedule needs the power kept in silent mode below 1.0: at 1.0 the schedule caps nothing. Lower it, or clear the schedule.",
       "dhw_min_too_close": "A hot water minimum this close to the setpoint leaves the tank no working band; keep it at least 5 °C below the setpoint.",
       "min_above_target": "The minimum temperature is above the target temperature.",
       "max_below_target": "The maximum temperature is below the target temperature.",
@@ -1547,6 +1548,7 @@
           "dhw_legionella_temperature": "Anti-legionella temperature",
           "dhw_legionella_interval_days": "Anti-legionella interval",
           "silent_mode_windows": "Pump's own night-mode schedule",
+          "silent_mode_power_fraction": "Power kept in silent mode",
           "heat_pump_max_power": "Heat pump max power (kW)",
           "space_setpoint_unit": "What that set-point entity expects",
           "mixing_valve_write_target_kind": "What the control entity expects",
@@ -1568,6 +1570,7 @@
           "dhw_legionella_temperature": "Read from the pump's DHW anti-legionella setpoint register (0195H), times 0.1.",
           "dhw_legionella_interval_days": "Seven days divided by the number of days set in the pump's anti-legionella schedule (02CAH), rounded down.",
           "silent_mode_windows": "Read from the pump's night mode start and end registers (0206H, 0207H), each hour times 256 plus minute.",
+          "silent_mode_power_fraction": "The share of the heat pump's maximum electrical power it still runs at inside the silent mode schedule. 1.0 caps nothing. The slider stops at the same floor as the measured capacity limit, so this can trim the plan but never leave the house without heat.",
           "heat_pump_max_power": "The pump's unit capacity register, in kW of heat, divided by the nominal COP in force.",
           "space_setpoint_unit": "Suggested as flow when the pump's control mode register (100DH) is water temperature control.",
           "mixing_valve_write_target_kind": "Suggested as flow on water temperature control, only where the two-zone model the building page requires for it is configured.",
@@ -1603,6 +1606,7 @@
       "dhw_window_too_short": "A hot water time frame is shorter than {min_window_minutes} minutes. The plan is made in {min_window_minutes}-minute steps, so a shorter frame can fall between two steps and never take effect.",
       "freq_control_needs_number": "Control writes the frequency through a number entity. Choose one, or keep the mode on observe: a frequency sensor alone can only be observed.",
       "silent_mode_window_too_short": "A silent mode time frame is shorter than {min_window_minutes} minutes. The plan is made in {min_window_minutes}-minute steps, so a shorter frame can fall between two steps and never take effect.",
+      "silent_mode_fraction_uncapped": "A kept silent mode schedule needs the power kept in silent mode below 1.0: at 1.0 the schedule caps nothing. Lower it, or clear the schedule.",
       "disinfection_control_needs_entity": "Control turns the pump's disinfection switch on and off, so it needs one. Pick the switch above, or set the mode back to observe.",
       "dhw_min_too_close": "A hot water minimum this close to the setpoint leaves the tank no working band; keep it at least 5 °C below the setpoint.",
       "invalid_grid_fee_rules": "Those fee rules could not be read. One rule per line, like \"Nov-Mar Mon-Fri 06:00-22:00 = 0.25\".",
diff --git a/custom_components/heatpump_optimizer/translations/sv.json b/custom_components/heatpump_optimizer/translations/sv.json
index 3dc86b5c04..a7a6a49042 100644
--- a/custom_components/heatpump_optimizer/translations/sv.json
+++ b/custom_components/heatpump_optimizer/translations/sv.json
@@ -342,6 +342,7 @@
           "dhw_legionella_temperature": "Legionellatemperatur",
           "dhw_legionella_interval_days": "Intervall för legionellaskydd",
           "silent_mode_windows": "Pumpens eget nattläge-schema",
+          "silent_mode_power_fraction": "Effekt som behålls i tyst läge",
           "heat_pump_max_power": "Värmepump max effekt (kW)",
           "space_setpoint_unit": "Vad den börvärdesentiteten förväntar sig",
           "mixing_valve_write_target_kind": "Vad styrenheten förväntar sig",
@@ -350,8 +351,7 @@
           "dhw_temp_entity": "Givare för varmvattenberedarens temperatur",
           "heat_pump_supply_temp_entity": "Framledningstemperatur",
           "heat_pump_return_temp_entity": "Returtemperatur",
-          "heat_pump_capacity_limited_entity": "Begränsad effekt (nattläge)",
-          "after_save": "Efter sparande"
+          "heat_pump_capacity_limited_entity": "Begränsad effekt (nattläge)"
         },
         "data_description": {
           "prefill_device": "Pumpens egen enhet. Dess entiteter mappas till inställningar av integrationens publicerade definitioner, eller av deras namn där inget publiceras - inte från en avläsning av din enhet - så kontrollera förslagen innan du behåller dem. Lämna tomt för att fortsätta installationen utan förifyllningen.",
@@ -361,6 +361,7 @@
           "dhw_legionella_temperature": "Läst ur pumpens register för legionellabörvärde (0195H), gånger 0,1.",
           "dhw_legionella_interval_days": "Sju dagar delat med antalet dagar som är valda i pumpens legionellaschema (02CAH), avrundat nedåt.",
           "silent_mode_windows": "Läst ur pumpens register för nattlägets start och slut (0206H, 0207H), vardera timme gånger 256 plus minut.",
+          "silent_mode_power_fraction": "Hur stor andel av värmepumpens maximala eleffekt den fortfarande går med inom schemat för tyst läge. 1,0 begränsar ingenting. Reglaget stannar vid samma golv som den uppmätta kapacitetsgränsen, så detta kan trimma planen men aldrig lämna huset utan värme.",
           "heat_pump_max_power": "Pumpens register för enhetens kapacitet, i kW värme, delat med den nominella COP som gäller.",
           "space_setpoint_unit": "Föreslås som framledning när pumpens register för styrläge (100DH) står på vattentemperaturstyrning.",
           "mixing_valve_write_target_kind": "Föreslås som framledning vid vattentemperaturstyrning, bara där tvåzonsmodellen som sidan för värmesystemet kräver för det är konfigurerad.",
@@ -369,8 +370,7 @@
           "dhw_temp_entity": "Värmepumpens givare för varmvattenberedarens temperatur, föreslås bara medan fältet är tomt.",
           "heat_pump_supply_temp_entity": "Värmepumpens givare för utgående vattentemperatur (T1), föreslås bara medan fältet är tomt.",
           "heat_pump_return_temp_entity": "Värmepumpens givare för ingående vattentemperatur (Tw-in), föreslås bara medan fältet är tomt.",
-          "heat_pump_capacity_limited_entity": "Värmepumpens givare för aktivt nattläge (frekvensbegränsning), föreslås bara medan fältet är tomt.",
-          "after_save": "Installationen fortsätter till nästa sida oavsett vad du väljer; inget sparas förrän installationen är klar."
+          "heat_pump_capacity_limited_entity": "Värmepumpens givare för aktivt nattläge (frekvensbegränsning), föreslås bara medan fältet är tomt."
         }
       }
     },
@@ -380,6 +380,7 @@
       "invalid_dhw_windows": "Tiderna kunde inte tolkas. Använd 24-timmarsformat separerat med komma, till exempel \"06:00-08:30, 17:00-22:00\".",
       "dhw_window_too_short": "En varmvattenperiod är kortare än {min_window_minutes} minuter. Planen görs i steg om {min_window_minutes} minuter, så en kortare period kan hamna mellan två steg och aldrig få någon verkan.",
       "silent_mode_window_too_short": "Ett tidsfönster för tyst läge är kortare än {min_window_minutes} minuter. Planen görs i steg om {min_window_minutes} minuter, så ett kortare fönster kan hamna mellan två steg och aldrig få effekt.",
+      "silent_mode_fraction_uncapped": "Ett behållet schema för tyst läge behöver en effekt i tyst läge under 1.0: vid 1.0 begränsar schemat ingenting. Sänk den, eller töm schemat.",
       "dhw_min_too_close": "Ett varmvattenminimum så nära börvärdet lämnar tanken utan arbetsband; håll det minst 5 °C under börvärdet.",
       "min_above_target": "Lägsta temperaturen ligger över måltemperaturen.",
       "max_below_target": "Högsta temperaturen ligger under måltemperaturen.",
@@ -1547,6 +1548,7 @@
           "dhw_legionella_temperature": "Legionellatemperatur",
           "dhw_legionella_interval_days": "Intervall för legionellaskydd",
           "silent_mode_windows": "Pumpens eget nattläge-schema",
+          "silent_mode_power_fraction": "Effekt som behålls i tyst läge",
           "heat_pump_max_power": "Värmepump max effekt (kW)",
           "space_setpoint_unit": "Vad den börvärdesentiteten förväntar sig",
           "mixing_valve_write_target_kind": "Vad styrenheten förväntar sig",
@@ -1568,6 +1570,7 @@
           "dhw_legionella_temperature": "Läst ur pumpens register för legionellabörvärde (0195H), gånger 0,1.",
           "dhw_legionella_interval_days": "Sju dagar delat med antalet dagar som är valda i pumpens legionellaschema (02CAH), avrundat nedåt.",
           "silent_mode_windows": "Läst ur pumpens register för nattlägets start och slut (0206H, 0207H), vardera timme gånger 256 plus minut.",
+          "silent_mode_power_fraction": "Hur stor andel av värmepumpens maximala eleffekt den fortfarande går med inom schemat för tyst läge. 1,0 begränsar ingenting. Reglaget stannar vid samma golv som den uppmätta kapacitetsgränsen, så detta kan trimma planen men aldrig lämna huset utan värme.",
           "heat_pump_max_power": "Pumpens register för enhetens kapacitet, i kW värme, delat med den nominella COP som gäller.",
           "space_setpoint_unit": "Föreslås som framledning när pumpens register för styrläge (100DH) står på vattentemperaturstyrning.",
           "mixing_valve_write_target_kind": "Föreslås som framledning vid vattentemperaturstyrning, bara där tvåzonsmodellen som sidan för värmesystemet kräver för det är konfigurerad.",
@@ -1601,6 +1604,7 @@
       "dhw_window_too_short": "En varmvattenperiod är kortare än {min_window_minutes} minuter. Planen görs i steg om {min_window_minutes} minuter, så en kortare period kan hamna mellan två steg och aldrig få någon verkan.",
       "freq_control_needs_number": "Styrning skriver frekvensen via en number-entitet. Välj en, eller behåll läget observera: en frekvenssensor ensam kan bara observeras.",
       "silent_mode_window_too_short": "Ett tidsfönster för tyst läge är kortare än {min_window_minutes} minuter. Planen görs i steg om {min_window_minutes} minuter, så ett kortare fönster kan hamna mellan två steg och aldrig få effekt.",
+      "silent_mode_fraction_uncapped": "Ett behållet schema för tyst läge behöver en effekt i tyst läge under 1.0: vid 1.0 begränsar schemat ingenting. Sänk den, eller töm schemat.",
       "disinfection_control_needs_entity": "Styra slår på och av pumpens desinfektionsbrytare, så det kräver en sådan. Välj brytaren ovan, eller ställ tillbaka läget på observera.",
       "dhw_min_too_close": "Ett varmvattenminimum så nära börvärdet lämnar tanken utan arbetsband; håll det minst 5 °C under börvärdet.",
       "invalid_grid_fee_rules": "Avgiftsreglerna kunde inte läsas. En regel per rad, som \"Nov-Mar Mån-Fre 06:00-22:00 = 0.25\".",
diff --git a/dev/audit/harnesses/r11_seam_config_silent_prefill.py b/dev/audit/harnesses/r11_seam_config_silent_prefill.py
new file mode 100644
index 0000000000..783ab6e106
--- /dev/null
+++ b/dev/audit/harnesses/r11_seam_config_silent_prefill.py
@@ -0,0 +1,58 @@
+"""R11-SEAM-config companion to round 11's D17/s2/silent_prefill.py (D17-s2-04).
+
+The finder's harness reads a created entry's ``data`` alone and posts a
+schedule the setup page never showed; once settings are stored in options and
+a kept schedule at fraction 1.0 is refused, its walk ends on the refusal and
+its cap arms read flat. This applies the pre-fill pages' own rule to the same
+inputs, at either end of the fix:
+
+- ``fraction_shown_beside_windows``: a page showing the schedule field shows
+  the power fraction beside it (1 fixed, 0 at the defect);
+- ``uncapped_schedule_accepted``: a kept schedule whose fraction in force is
+  the 1.0 default -- it caps nothing -- passes the page's refusals (0 fixed,
+  1 at the defect);
+- null controls, equal at both ends: ``capped_schedule_refused`` (schedule kept
+  with fraction 0.6) and ``no_schedule_refused`` (fraction 1.0, no schedule).
+
+Run from the tree root: ``PYTHONPATH=tests/hastub python3
+dev/audit/harnesses/r11_seam_config_silent_prefill.py``.
+"""
+import sys
+
+sys.path.insert(0, "custom_components")
+sys.path.insert(0, "tests")
+
+from heatpump_optimizer import config_flow  # noqa: E402
+from heatpump_optimizer.const import (  # noqa: E402
+    CONF_SILENT_MODE_FRACTION,
+    CONF_SILENT_MODE_WINDOWS,
+)
+
+SCHEDULE = {CONF_SILENT_MODE_WINDOWS: "06:00-10:00"}
+
+
+def shown(keys, values):
+    """The field names a pre-fill page renders for ``keys``."""
+    if hasattr(config_flow, "_prefill_fields"):
+        fields = config_flow._prefill_fields(keys, values, {})
+    else:  # the defect's tree: the page builder took no in-force mapping
+        fields = config_flow._prefill_schema(keys, values).schema
+    return {str(getattr(marker, "schema", marker)) for marker in fields}
+
+
+def refused(saved):
+    return bool(config_flow._prefill_errors(dict(saved), {}))
+
+
+def main():
+    page = shown((CONF_SILENT_MODE_WINDOWS,), SCHEDULE)
+    print(f"page fields for a suggested schedule: {sorted(page)}")
+    print(f"RESULT fraction_shown_beside_windows={int(CONF_SILENT_MODE_FRACTION in page)} count")
+    print(f"RESULT uncapped_schedule_accepted={int(not refused(SCHEDULE))} count")
+    print(f"RESULT capped_schedule_refused="
+          f"{int(refused({**SCHEDULE, CONF_SILENT_MODE_FRACTION: 0.6}))} count")
+    print(f"RESULT no_schedule_refused={int(refused({CONF_SILENT_MODE_FRACTION: 1.0}))} count")
+
+
+if __name__ == "__main__":
+    main()
diff --git a/dev/programme/delivery/3742.md b/dev/programme/delivery/3742.md
new file mode 100644
index 0000000000..d7907c379c
--- /dev/null
+++ b/dev/programme/delivery/3742.md
@@ -0,0 +1 @@
+- [#3742](https://github.com/tvofi/heatpump_optimizer/pull/3742) — **open**, R11-SEAM-config: one place per config entry key, entry version 7.2 (R11-SEAM-config)
diff --git a/dev/programme/delivery/3815.md b/dev/programme/delivery/3815.md
new file mode 100644
index 0000000000..632bc441d2
--- /dev/null
+++ b/dev/programme/delivery/3815.md
@@ -0,0 +1 @@
+- [#3815](https://github.com/tvofi/heatpump_optimizer/pull/3815) — **open**, R11-CARRY-ROOM-LIFT hotfix: lift-peak check within 1e-3 K across BLAS kernels (R11-CARRY-ROOM-LIFT)
diff --git a/docs/configuration.md b/docs/configuration.md
index 993932926d..a2c5686383 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -150,6 +150,7 @@ empty skips the screen. Where each suggestion comes from is listed under
 | When you need hot water | read from the device | The pump's hot water schedule. Keeping it turns hot water planning on. |
 | Anti-legionella interval | read from the device | The pump's anti-legionella schedule. |
 | Pump's own night-mode schedule | read from the device | When the pump limits itself to its quiet mode. |
+| Power kept in silent mode | the value in force | Shown beside the night-mode schedule: the share of the pump's maximum power it runs at inside it. At 1.0 the schedule caps nothing, so keeping a schedule with 1.0 is refused; lower it or clear the schedule. |
 | Heat pump max power (kW) | read from the device | The unit's capacity divided by the nominal COP. |
 | What that set-point entity expects | read from the device | Flow temperature when the pump runs on water temperature control. |
 | What the control entity expects | read from the device | The same, for a mixing valve, only where the two-zone model is configured. |
diff --git a/tests/closures.json b/tests/closures.json
index f7a8d916fc..d03a56cc2a 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4594,6 +4594,7 @@
    "dev/audit/harnesses/r11_owner_criteria.py",
    "dev/audit/harnesses/r11_plan_page_inventory.py",
    "dev/audit/harnesses/r11_relay_3358_skip.py",
+   "dev/audit/harnesses/r11_seam_config_silent_prefill.py",
    "dev/audit/harnesses/r11_selftest_static_edge.py",
    "dev/audit/harnesses/r11_toolchain_mutants.py",
    "dev/audit/harnesses/r11_why_hover_fit.mjs",
diff --git a/tests/config_flow_steps.py b/tests/config_flow_steps.py
index 6e73c9e1d1..1ce16fb27b 100644
--- a/tests/config_flow_steps.py
+++ b/tests/config_flow_steps.py
@@ -99,6 +99,7 @@ import asyncio  # noqa: E402
 import json  # noqa: E402
 import logging  # noqa: E402
 import pathlib  # noqa: E402
+import re  # noqa: E402
 import sys  # noqa: E402
 
 sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
@@ -125,6 +126,7 @@ from golden import (  # noqa: E402
 )
 
 from heatpump_optimizer import config_flow, const, quick_setup, topology  # noqa: E402
+from heatpump_optimizer.dhw_schedule import day_overrides_enabled  # noqa: E402
 from heatpump_optimizer.freq_control import (  # noqa: E402
     FREQ_MODE_CONTROL,
     FREQ_MODE_OBSERVE,
@@ -1079,7 +1081,7 @@ async def walk_questionnaire():
         config_flow.async_get_clientsession = real
         return
     result = await submit(flow, "setup_overview", {})
-    entry_data = result.get("data", {})
+    entry_data = {**result.get("data", {}), **result.get("options", {})}
     from_every_page = [
         key
         for key in (
@@ -1179,7 +1181,7 @@ async def walk_finish_now():
         config_flow.async_get_clientsession = real
         return
     result = await submit(flow, "setup_overview", {})
-    entry_data = result.get("data", {})
+    entry_data = {**result.get("data", {}), **result.get("options", {})}
     check(
         "setup_overview",
         "happy",
@@ -1309,10 +1311,10 @@ async def walk_expert():
         "happy",
         "confirming the expert overview creates the entry with the thermal values",
         result.get("type") == "create_entry"
-        and result.get("data", {}).get(const.CONF_HOUSE_THERMAL_MASS) == 10.0
-        and result.get("data", {}).get(const.CONF_INTER_ZONE_TRANSFER) == 0.1,
+        and {**result.get("data", {}), **result.get("options", {})}.get(const.CONF_HOUSE_THERMAL_MASS) == 10.0
+        and {**result.get("data", {}), **result.get("options", {})}.get(const.CONF_INTER_ZONE_TRANSFER) == 0.1,
         f"{result.get('type')} "
-        f"{result.get('data', {}).get(const.CONF_HOUSE_THERMAL_MASS)}",
+        f"{({**result.get('data', {}), **result.get('options', {})}).get(const.CONF_HOUSE_THERMAL_MASS)}",
     )
 
     config_flow.async_get_clientsession = real
@@ -1442,7 +1444,8 @@ async def reauth_round_trip():
     )
     round_trip_done = (
         fixed == {"type": "abort", "reason": "reauth_successful"}
-        and entry.data[const.CONF_TIBBER_TOKEN] == "brand-new-token"
+        and {**entry.data, **entry.options}[const.CONF_TIBBER_TOKEN] == "brand-new-token"
+        and set(entry.data) <= {"name"}
         and hass.config_entries.reloaded == ["reauth-1"]
     )
     check(
@@ -1450,7 +1453,7 @@ async def reauth_round_trip():
         "happy",
         "a new token is written through, the entry reloads, reauth_successful",
         round_trip_done,
-        f"{fixed} token={entry.data[const.CONF_TIBBER_TOKEN]} "
+        f"{fixed} token={({**entry.data, **entry.options}).get(const.CONF_TIBBER_TOKEN)} "
         f"reloaded={hass.config_entries.reloaded}",
     )
     # D10-s1-01 (#1644, P2): the token is identity, so the unique id must
@@ -1463,7 +1466,7 @@ async def reauth_round_trip():
         entry.unique_id
         == config_flow.entry_identity({**entry.data, **entry.options})
         != config_flow.entry_identity(
-            {**entry.data, const.CONF_TIBBER_TOKEN: "stale-token"}
+            {**entry.data, **entry.options, const.CONF_TIBBER_TOKEN: "stale-token"}
         ),
         f"unique_id={entry.unique_id!r}",
     )
@@ -1509,7 +1512,7 @@ async def options_entry_data():
     finally:
         config_flow.async_get_clientsession = real
     assert result.get("type") == "create_entry", str(result)[:200]
-    return dict(result["data"]), flow.unique_id
+    return {**result["data"], **result.get("options", {})}, flow.unique_id
 
 
 def fresh_options(pre_options=None, entry_id="opts-1"):
@@ -1896,7 +1899,7 @@ async def options_walk():
         "tuning",
         {**TUNING_ANSWERS, const.CONF_PRICE_WEIGHT: 3.0, const.CONF_AFTER_SAVE: const.AFTER_SAVE_CLOSE},
     )
-    close_data = result.get("data", {})
+    close_data = {**result.get("data", {}), **result.get("options", {})}
     round_trip_done = (
         result.get("type") == "create_entry"
         and close_data.get(const.CONF_PRICE_WEIGHT) == 3.0
@@ -3834,14 +3837,16 @@ async def residual_statement_branches():
     check(
         "opt_hot_water",
         "happy",
-        "a valid per-day save stores the flag and the two specs, not seven keys",
+        "a valid per-day save stores the two specs, not seven keys, and reads per-day on from them",
         shows_menu(result, "init")
-        and entry.options.get(const.CONF_DHW_WINDOWS_BY_DAY) is True
+        # The flag equals the default the saved specs derive (D17-s1-02), so
+        # it is not stored; the entry still reads as per-day on.
+        and const.CONF_DHW_WINDOWS_BY_DAY not in entry.options
+        and day_overrides_enabled(entry.options) is True
         and entry.options.get(const.CONF_DHW_WINDOWS_DAY[5]) == "10:00-12:00"
         and entry.options.get(const.CONF_DHW_WINDOWS_DAY[6]) == "12:00-14:00"
         and sorted(entry.options) == sorted(
-            [const.CONF_DHW_WINDOWS_BY_DAY,
-             const.CONF_DHW_WINDOWS_DAY[5],
+            [const.CONF_DHW_WINDOWS_DAY[5],
              const.CONF_DHW_WINDOWS_DAY[6],
              *HOT_WATER_PAGE_ANSWERS]
         ),
@@ -5036,8 +5041,9 @@ async def reconfigure_flow():
     result = await submit_reconfigure(flow, RC_SAME)
     round_trip_done = (
         result == {"type": "abort", "reason": "reconfigure_successful"}
-        and entry.data[const.CONF_TARGET_TEMP] == 21.5
-        and entry.data[const.CONF_TIBBER_TOKEN] == "stale-token"
+        and {**entry.data, **entry.options}[const.CONF_TARGET_TEMP] == 21.5
+        and {**entry.data, **entry.options}[const.CONF_TIBBER_TOKEN] == "stale-token"
+        and set(entry.data) <= {"name"}
         and hass.config_entries.reloaded == ["plant_a"]
         and entry.unique_id == config_flow.entry_identity(RC_ENTRY_DATA)
     )
@@ -5058,12 +5064,13 @@ async def reconfigure_flow():
         "happy",
         "a rotated token is written through and the entry keeps its other settings",
         result == {"type": "abort", "reason": "reconfigure_successful"}
-        and entry.data[const.CONF_TIBBER_TOKEN] == "tok-fresh"
-        and entry.data[const.CONF_TARGET_TEMP] == 21.5
+        and {**entry.data, **entry.options}[const.CONF_TIBBER_TOKEN] == "tok-fresh"
+        and {**entry.data, **entry.options}[const.CONF_TARGET_TEMP] == 21.5
+        and set(entry.data) <= {"name"}
         and hass.config_entries.reloaded == ["plant_a"]
         and entry.unique_id
         == config_flow.entry_identity({**RC_ENTRY_DATA, const.CONF_TIBBER_TOKEN: "tok-fresh"}),
-        f"{result} token={entry.data.get(const.CONF_TIBBER_TOKEN)} "
+        f"{result} token={({**entry.data, **entry.options}).get(const.CONF_TIBBER_TOKEN)} "
         f"reloaded={hass.config_entries.reloaded}",
     )
 
@@ -5091,8 +5098,9 @@ async def reconfigure_flow():
         "happy",
         "a slot the user cleared is dropped, not silently kept",
         result == {"type": "abort", "reason": "reconfigure_successful"}
-        and const.CONF_INDOOR_TEMP_ENTITY not in entry.data,
-        f"{result} indoor={entry.data.get(const.CONF_INDOOR_TEMP_ENTITY)!r}",
+        and const.CONF_INDOOR_TEMP_ENTITY not in {**entry.data, **entry.options}
+        and set(entry.data) <= {"name"},
+        f"{result} indoor={({**entry.data, **entry.options}).get(const.CONF_INDOOR_TEMP_ENTITY)!r}",
     )
 
     LEDGER.rows["_reconfigure"] = int(round_trip_done)
@@ -6248,6 +6256,7 @@ async def options_modbus_prefill():
             const.CONF_DHW_WINDOWS: "05:30-07:00",
             const.CONF_DHW_LEGIONELLA_INTERVAL_DAYS: 3.0,
             const.CONF_SILENT_MODE_WINDOWS: "22:00-06:00",
+            const.CONF_SILENT_MODE_FRACTION: 1.0,
             const.CONF_DHW_TEMP_ENTITY: "sensor.hp_dhw_tank_temperature",
         },
         f"{offered}",
@@ -6269,6 +6278,7 @@ async def options_modbus_prefill():
         const.CONF_DHW_LEGIONELLA_INTERVAL_DAYS: None,
         const.CONF_DHW_TEMP_ENTITY: None,
         const.CONF_SILENT_MODE_WINDOWS: "22:00-06:00",
+        const.CONF_SILENT_MODE_FRACTION: 0.5,
         const.CONF_AFTER_SAVE: const.AFTER_SAVE_MENU,
     })
     check(
@@ -6277,6 +6287,7 @@ async def options_modbus_prefill():
         shows_menu(result, "init") and entry.options == {
             const.CONF_DHW_SETPOINT: 52.0,
             const.CONF_SILENT_MODE_WINDOWS: "22:00-06:00",
+            const.CONF_SILENT_MODE_FRACTION: 0.5,
         },
         f"{result.get('type')}/{result.get('step_id')} options={entry.options}",
     )
@@ -7207,10 +7218,10 @@ async def config_flow_device_prefill_offer():
         "device_prefill", "happy",
         "the entry the wizard creates carries what the offer filled",
         created.get("type") == "create_entry"
-        and created.get("data", {}).get(const.CONF_DHW_SETPOINT) == 50.0
-        and created.get("data", {}).get(const.CONF_DHW_TEMP_ENTITY)
+        and {**created.get("data", {}), **created.get("options", {})}.get(const.CONF_DHW_SETPOINT) == 50.0
+        and {**created.get("data", {}), **created.get("options", {})}.get(const.CONF_DHW_TEMP_ENTITY)
         == f"sensor.{slug}_dhw_tank_temperature",
-        f"{created.get('type')} data={sorted(created.get('data') or {})}",
+        f"{created.get('type')} data={sorted(created.get('data') or {})} options={sorted(created.get('options') or {})}",
     )
 
     # #1107: the wizard's own data is what the omission rules read, so a
@@ -7355,7 +7366,7 @@ async def device_prefill_preview_texts():
         check(
             "device_prefill", "happy",
             f"every previewed field has a label where the frontend looks, in {name}",
-            not raw and len(preview_keys) > 6,
+            not raw and len(preview_keys) >= 6,
             f"{len(raw)} of {len(preview_keys)} render the raw key: {raw}",
         )
         # The labels are copies: the options pre-fill page translates the same
@@ -8065,6 +8076,150 @@ for _or_key in (const.CONF_PREFILL_OFFER, "no_such_option_key"):
     R.check(f"option_range refuses {_or_key!r}, which has no number field", _or_raised)
 
 
+
+async def seam_config_one_place():
+    """R11-SEAM-config: each key in one place, so every writer agrees with the reader."""
+    R.section("one place per key: reconfigure, setup, pre-fill and computed defaults agree (R11-SEAM-config)")
+    from heatpump_optimizer import entry_config  # noqa: PLC0415
+
+    # The data-only set is derived from the forms, never carried: a new options
+    # row for a first-screen key moves that key to options.
+    first = {
+        str(getattr(marker, "schema", marker))
+        for marker in config_flow._first_screen_schema(FakeHass()).schema
+    }
+    derived = first - {row.key for row in config_flow._OPTION_FIELDS}
+    check("reconfigure", "happy",
+          "entry.data stores exactly the first-screen keys no options page edits",
+          entry_config.DATA_ONLY == derived,
+          f"DATA_ONLY={sorted(entry_config.DATA_ONLY)} derived={sorted(derived)}")
+
+    # D10-s2-01: a reconfigure after an Entities save prefills the running value
+    # and its save takes effect; the arm with no options save is the null.
+    creds = {k: v for k, v in RC_ENTRY_DATA.items() if k in FIRST_SCREEN}
+    for saved_options in (True, False):
+        real = install_session(config_flow, FakeSession([TIBBER_VIEWER_OK]))
+        try:
+            flow, entry, _, _ = rc_setup()
+            if saved_options:
+                entry.options = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.running_indoor"}
+            running = {**entry.data, **entry.options}[const.CONF_INDOOR_TEMP_ENTITY]
+            sensors_form = await submit(flow, "reconfigure", creds)
+            prefilled = rc_suggested(sensors_form).get(const.CONF_INDOOR_TEMP_ENTITY)
+            sensors = {
+                k: v for k, v in RC_ENTRY_DATA.items()
+                if k not in FIRST_SCREEN and k in schema_keys(sensors_form)
+            }
+            done = await submit(flow, "user_sensors",
+                                {**sensors, const.CONF_INDOOR_TEMP_ENTITY: "sensor.new_indoor"})
+        finally:
+            config_flow.async_get_clientsession = real
+        effective = {**entry.data, **entry.options}
+        check("reconfigure", "happy",
+              f"reconfigure {'after' if saved_options else 'with no'} options save: the page "
+              "prefills the value in force, the save takes effect, data holds DATA_ONLY alone",
+              done.get("reason") == "reconfigure_successful"
+              and prefilled == running
+              and effective[const.CONF_INDOOR_TEMP_ENTITY] == "sensor.new_indoor"
+              and effective[const.CONF_TARGET_TEMP] == RC_ENTRY_DATA[const.CONF_TARGET_TEMP]
+              and set(entry.data) <= entry_config.DATA_ONLY,
+              f"done={done} prefilled={prefilled!r} running={running!r} data={entry.data} "
+              f"options={entry.options}")
+
+    # D10-s1-03: the created entry stores its settings in options.
+    answers = {config_flow.CONF_NAME: "Annex pump", const.CONF_TIBBER_TOKEN: "t",
+               const.CONF_TARGET_TEMP: 21.0}
+    created = fresh_flow(data=answers)._create_setup_entry()
+    check("setup_overview", "happy",
+          "the created entry stores DATA_ONLY in data and every setting in options, the "
+          "effective mapping unchanged",
+          set(created["data"]) <= entry_config.DATA_ONLY
+          and {**created["data"], **created["options"]} == answers,
+          f"data={created.get('data')} options={created.get('options')}")
+
+    # D17-s1-02: a computed default is judged over the save, not the stored
+    # configuration: the holiday start shown and kept survives a changed
+    # weekday start; resubmitting it unchanged is the null and stays unstored.
+    hass = FakeHass()
+    stored = {"day_start_hour": 8}
+    kept = config_flow._omit_unstored_computed(
+        {"day_start_hour": 7, "holiday_day_start_hour": 8}, stored, hass)
+    same = config_flow._omit_unstored_computed(
+        {"day_start_hour": 8, "holiday_day_start_hour": 8}, stored, hass)
+    check("comfort", "happy",
+          "a computed value kept while its source changes is stored; kept with its "
+          "source unchanged it stays unstored",
+          kept.get("holiday_day_start_hour") == 8 and "holiday_day_start_hour" not in same,
+          f"kept={kept} same={same}")
+
+    # D4-s2-01, D6-s3-01, D17-s2-05, D17-s2-04: the setup pre-fill page.
+    strings = json.loads(
+        (pathlib.Path(config_flow.__file__).parent / "strings.json").read_text())
+    step_text = strings["config"]["step"]["device_prefill"]
+    flow = fresh_flow(data=answers)
+    notes = {"found": "6", "backup_heater_type": "7"}
+    flow._device_prefill = ((const.CONF_SILENT_MODE_WINDOWS,), notes)
+    refused = await submit(flow, "device_prefill", {const.CONF_SILENT_MODE_WINDOWS: "06:00-10:00"})
+    placeholders = refused.get("description_placeholders") or {}
+    texts = [step_text["description"], *step_text.get("data_description", {}).values(),
+             *(strings["config"]["error"][e] for e in (refused.get("errors") or {}).values())]
+    needed = {name for text in texts for name in re.findall(r"{(\w+)}", text)}
+    check("device_prefill", "error",
+          "a kept schedule at fraction 1.0 is refused on the fraction, which the page "
+          "shows beside it, with every placeholder its strings read and the preview's notes",
+          shows(refused, "device_prefill")
+          and refused.get("errors") == {
+              const.CONF_SILENT_MODE_FRACTION: "silent_mode_fraction_uncapped"}
+          and const.CONF_SILENT_MODE_FRACTION in schema_keys(refused)
+          and needed <= placeholders.keys()
+          and all(placeholders.get(k) == v for k, v in notes.items()),
+          f"errors={refused.get('errors')} missing={sorted(needed - placeholders.keys())} "
+          f"placeholders={placeholders} fields={sorted(schema_keys(refused))}")
+    # A window refusal reads the page's window placeholder (D4-s2-01).
+    short = await submit(flow, "device_prefill", {
+        const.CONF_SILENT_MODE_WINDOWS: "06:00-06:05", const.CONF_SILENT_MODE_FRACTION: 0.6})
+    short_ph = short.get("description_placeholders") or {}
+    short_needed = {
+        name for e in (short.get("errors") or {}).values()
+        for name in re.findall(r"{(\w+)}", strings["config"]["error"][e])
+    }
+    check("device_prefill", "error",
+          "a too-short window refusal on the setup pre-fill page renders its placeholders",
+          shows(short, "device_prefill") and short_needed and short_needed <= short_ph.keys(),
+          f"errors={short.get('errors')} needed={sorted(short_needed)} placeholders={sorted(short_ph)}")
+    # A previewed field the user cleared stays cleared on the refused page's
+    # re-render, though the stored configuration holds a value for it: the
+    # value in force is suggested only for a companion the preview did not list.
+    cleared_flow = fresh_flow(data={**answers, const.CONF_SILENT_MODE_FRACTION: 0.6})
+    cleared_flow._device_prefill = (
+        (const.CONF_SILENT_MODE_WINDOWS, const.CONF_SILENT_MODE_FRACTION), notes)
+    cleared = await submit(cleared_flow, "device_prefill",
+                           {const.CONF_SILENT_MODE_WINDOWS: "06:00-06:05"})
+    check("device_prefill", "error",
+          "a listed field cleared on the setup pre-fill page re-renders empty, not "
+          "with the stored value",
+          shows(cleared, "device_prefill") and cleared.get("errors")
+          and const.CONF_SILENT_MODE_FRACTION in schema_keys(cleared)
+          and suggested_value(cleared, const.CONF_SILENT_MODE_FRACTION) is None
+          and suggested_value(cleared, const.CONF_SILENT_MODE_WINDOWS) == "06:00-06:05",
+          f"errors={cleared.get('errors')} "
+          f"fraction={suggested_value(cleared, const.CONF_SILENT_MODE_FRACTION)!r} "
+          f"windows={suggested_value(cleared, const.CONF_SILENT_MODE_WINDOWS)!r}")
+    check("device_prefill", "happy",
+          "the setup pre-fill page posts no after_save: its navigation is always finish_setup",
+          const.CONF_AFTER_SAVE not in schema_keys(refused),
+          f"fields={sorted(schema_keys(refused))}")
+    accepted = await submit(flow, "device_prefill", {
+        const.CONF_SILENT_MODE_WINDOWS: "06:00-10:00", const.CONF_SILENT_MODE_FRACTION: 0.6})
+    check("device_prefill", "happy",
+          "the schedule kept with a fraction below 1.0 is stored with it",
+          shows_menu(accepted, "finish_setup")
+          and flow._data.get(const.CONF_SILENT_MODE_WINDOWS) == "06:00-10:00"
+          and flow._data.get(const.CONF_SILENT_MODE_FRACTION) == 0.6
+          and const.CONF_AFTER_SAVE not in flow._data,
+          f"result={accepted.get('type')}/{accepted.get('step_id')} data={flow._data}")
+
+
 async def main() -> int:
     if "--self-check" in sys.argv:
         return await self_check()
@@ -8085,6 +8240,7 @@ async def main() -> int:
     await walk_expert()
     await temperature_error_branches()
     await reauth_round_trip()
+    await seam_config_one_place()
     await options_menus()
     await options_walk()
     await options_advanced_pages()
diff --git a/tests/entities.py b/tests/entities.py
index 5212ebe04e..4665bd8190 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -3391,7 +3391,7 @@ async def _walk_flow_untouched():
         result = await flow.async_step_user(None)
         for _ in range(20):
             if result.get("type") == "create_entry":
-                return dict(result["data"])
+                return {**result["data"], **result.get("options", {})}
             if result.get("type") == "menu":
                 # An untouched menu is its first option — except the finish
                 # menu, whose first option is now the quick-setup shortcut:
@@ -4036,6 +4036,27 @@ def _p2_registry(sources):
         # scalar and batch twins are both owners: the batch must equal the
         # scalar bit for bit (fixer.md step 15), and the scalar keeps its own
         # bisection for the per-day cost (ARCH2-s3 patch 01b).
+        # D10-s1-03, D10-s2-01 (R11-SEAM-config): where an entry stores a key
+        # is decided by entry_config.placed; every entry write passing data=
+        # writes a pair placed by it, so reconfigure, reauth, setup, the reset
+        # and the migration agree with the reader, {**data, **options}.
+        dict(fact="entry_key_placement", finding="D10-s1-03",
+             match=_p2_match_node(
+                 (ast.Call,), r"async_(update|create)_entry\(",
+                 lambda n: getattr(n.func, "attr", None) in (
+                     "async_update_entry", "async_create_entry")
+                 and any(k.arg == "data" for k in n.keywords)),
+             owners=["__init__.py::async_migrate_entry",
+                     "config_flow.py::HeatPumpOptimizerConfigFlow._async_save_reconfigure",
+                     "config_flow.py::HeatPumpOptimizerConfigFlow._create_setup_entry",
+                     "config_flow.py::HeatPumpOptimizerConfigFlow.async_step_reauth_confirm",
+                     "coordinator.py::_async_rewrite_entry"],
+             dispositions={
+                 "config_flow.py::HeatPumpOptimizerOptionsFlow._save":
+                     "an options flow's result data is the entry's options, never its data",
+                 "repairs.py::DhwSetpointRepairFlow.async_step_confirm":
+                     "a repair flow's result, not an entry write",
+             }),
         dict(fact="peak_tie_rule", finding="D7-s3-8x-tariff",
              match=_p2_match_node(
                  (ast.Name,), r"^_PEAK_TIE_BAND$",
@@ -14608,9 +14629,9 @@ try:
         R.check(
             "confirming the overview creates the entry",
             _early_entry.get("type") == "create_entry"
-            and _early_entry.get("data", {}).get(const.CONF_TIBBER_TOKEN)
+            and {**_early_entry.get("data", {}), **_early_entry.get("options", {})}.get(const.CONF_TIBBER_TOKEN)
             == _first_credentials[const.CONF_TIBBER_TOKEN]
-            and const.CONF_TARGET_TEMP not in _early_entry.get("data", {}),
+            and const.CONF_TARGET_TEMP not in {**_early_entry.get("data", {}), **_early_entry.get("options", {})},
             str(_early_entry)[:160],
         )
     # What the flow manager does when that flow finishes: an entry that holds
@@ -15557,6 +15578,7 @@ R.section("Config entry migration")
 _mig_hass = FakeHass()
 _mig = FakeEntry()
 _mig.version = const.CONFIG_ENTRY_VERSION
+_mig.minor_version = const.CONFIG_ENTRY_MINOR_VERSION
 R.check(
     "the current version is a no-op that reports success",
     asyncio.run(integration.async_migrate_entry(_mig_hass, _mig)) is True
@@ -15579,6 +15601,52 @@ R.check(
     asyncio.run(integration.async_migrate_entry(_mig_hass, _new)) is False,
 )
 
+# R11-SEAM-config: 7.2 stores each key in its one place (entry_config.placed).
+from heatpump_optimizer import entry_config as _mig_ec  # noqa: E402
+
+_m71 = FakeEntry(
+    data={"name": "Annex", const.CONF_TIBBER_TOKEN: "t", const.CONF_TARGET_TEMP: 21.0},
+    options={const.CONF_TARGET_TEMP: 22.0},
+)
+_m71.version = const.CONFIG_ENTRY_VERSION
+_m71_effective = {**_m71.data, **_m71.options}
+R.check(
+    "a 7.1 entry migrates to 7.2: data holds DATA_ONLY alone, the effective mapping is "
+    "unchanged and a key in both sides keeps the options value in force",
+    asyncio.run(integration.async_migrate_entry(_mig_hass, _m71)) is True
+    and (_m71.version, _m71.minor_version)
+    == (const.CONFIG_ENTRY_VERSION, const.CONFIG_ENTRY_MINOR_VERSION)
+    and set(_m71.data) <= _mig_ec.DATA_ONLY
+    and {**_m71.data, **_m71.options} == _m71_effective
+    and _m71.options[const.CONF_TARGET_TEMP] == 22.0,
+    f"data={_m71.data} options={_m71.options} minor={_m71.minor_version}",
+)
+# Null control: an entry already at the minor version is not rewritten, so a
+# 7.2 written under a downgraded release's reconfigure is left as it stands.
+_m72 = FakeEntry(data={"name": "Annex", const.CONF_TARGET_TEMP: 21.0})
+_m72.version = const.CONFIG_ENTRY_VERSION
+_m72.minor_version = const.CONFIG_ENTRY_MINOR_VERSION
+_m72_updates = len(_mig_hass.config_entries.updated)
+R.check(
+    "an entry at the current minor version is not rewritten",
+    asyncio.run(integration.async_migrate_entry(_mig_hass, _m72)) is True
+    and len(_mig_hass.config_entries.updated) == _m72_updates
+    and _m72.data == {"name": "Annex", const.CONF_TARGET_TEMP: 21.0},
+    f"data={_m72.data} updates={_mig_hass.config_entries.updated[_m72_updates:]}",
+)
+# An undo record written before the migration holds its settings in data:
+# undoing it stores each key where the entry now keeps it.
+_undo_rec = _mig_ec.undo_point(
+    const.FACTORY_RESET_SCOPES[0], {"name": "Annex", const.CONF_TARGET_TEMP: 21.0}, {})
+_undone = _mig_ec.undone_settings({"name": "Annex"}, {}, _undo_rec)
+R.check(
+    "undoing a reset recorded before 7.2 places the restored settings in options",
+    _undone is not None
+    and set(_undone[0]) <= _mig_ec.DATA_ONLY
+    and _undone[1].get(const.CONF_TARGET_TEMP) == 21.0,
+    f"record={_undo_rec} undone={_undone}",
+)
+
 
 # ===========================================================================
 # Service handlers, dispatched through the registry
@@ -26005,7 +26073,8 @@ R.check(
     "a valid token is written through and the entry reloads",
     _ra_out.get("reason") == "reauth_successful"
     and _ra_updates
-    and _ra_updates[0]["data"][_CONF_TOKEN] == "new-token"
+    and {**_ra_updates[0]["data"], **_ra_updates[0].get("options", {})}[_CONF_TOKEN] == "new-token"
+    and set(_ra_updates[0]["data"]) <= {"name"}
     and _ra_reloads == ["reauth-1"],
     f"result {_ra_out}, updates {_ra_updates}, reloads {_ra_reloads}",
 )
@@ -26215,7 +26284,8 @@ R.check(
     _rc_out_same.get("type") == "abort"
     and _rc_out_same.get("reason") == "reconfigure_successful"
     and _rc_updates
-    and _rc_updates[-1]["data"]["target_temp"] == 21.5,
+    and {**_rc_updates[-1]["data"], **_rc_updates[-1].get("options", {})}["target_temp"] == 21.5
+    and set(_rc_updates[-1]["data"]) <= {"name"},
     f"result {_rc_out_same}, updates {[k for k in _rc_updates]}",
 )
 R.check(
@@ -26230,7 +26300,7 @@ R.check(
         {**_rc_submit_same, _CONF_NAME: "Annex (renamed)"}
     ).get("reason")
     == "reconfigure_successful"
-    and _rc_updates[-1]["data"][_CONF_NAME] == "Annex (renamed)"
+    and {**_rc_updates[-1]["data"], **_rc_updates[-1].get("options", {})}[_CONF_NAME] == "Annex (renamed)"
     and _rc_updates[-1].get("title") == "Annex (renamed)",
     f"update kwargs keys {sorted(_rc_updates[-1]) if _rc_updates else []}",
 )
@@ -26241,9 +26311,10 @@ R.check(
     "a slot the user cleared is dropped, not silently kept",
     bool(_rc_updates)
     and _drive_reconfigure(_rc_cleared).get("reason") == "reconfigure_successful"
-    and const.CONF_INDOOR_TEMP_ENTITY not in _rc_updates[-1]["data"],
+    and const.CONF_INDOOR_TEMP_ENTITY not in {**_rc_updates[-1]["data"], **_rc_updates[-1].get("options", {})}
+    and set(_rc_updates[-1]["data"]) <= {"name"},
     f"cleared slot still in data: "
-    f"{_rc_updates[-1]['data'].get(const.CONF_INDOOR_TEMP_ENTITY) if _rc_updates else None!r}",
+    f"{({**_rc_updates[-1]['data'], **_rc_updates[-1].get('options', {})}).get(const.CONF_INDOOR_TEMP_ENTITY) if _rc_updates else None!r}",
 )
 R.check(
     "and the entry's unique id follows the picks, as a delete-and-recreate would",
diff --git a/tests/features.py b/tests/features.py
index 753227f748..00260e20fd 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -1651,7 +1651,7 @@ async def _r9f12_walk(choices, form_overrides):
     trail = []
     for _ in range(40):
         if result.get("type") == "create_entry":
-            return dict(result["data"]), trail
+            return {**result["data"], **result.get("options", {})}, trail
         if result.get("type") == "menu":
             options = list(result["menu_options"])
             step = choices[mi] if mi < len(choices) else options[0]
@@ -14798,7 +14798,7 @@ R.check(
     "a reset of both leaves the wiring alone and every learner at its initial state",
     _fr_learned(_fr_b_new) == _fr_learned(_fr_b_fresh)
     and set({**_fr_b_entry.data, **_fr_b_entry.options}) <= set(_fr_ec.FACTORY_KEPT)
-    and _fr_b_entry.data["indoor_temp_entity"] == "sensor.indoor",
+    and {**_fr_b_entry.data, **_fr_b_entry.options}["indoor_temp_entity"] == "sensor.indoor",
     f"stored {sorted({**_fr_b_entry.data, **_fr_b_entry.options})}",
 )
 _fr_undo = _fr_b_new._snapshot_ring.snapshots[-1]
@@ -14845,7 +14845,8 @@ R.check(
     f"refreshes asked {len(_fr_b_asked)}",
 )
 # The undo's pins, as stored: an explicit value, and one stored on the other
-# side (data versus options), each come back where and as they were.
+# side (data versus options), each come back as they were -- placed where the
+# entry now keeps them (only the name in data).
 _FR_PIN_DATA = {"name": "x", "two_zone_mode": "auto", "comfort_weight": 3.0, "indoor_temp_entity": "sensor.in"}
 _FR_PIN_OPTS = {"dhw_enabled": False, "target_temperature": 22.0}
 _fr_pin_reset = _fr_ec.factory_settings(_FR_PIN_DATA, _FR_PIN_OPTS, two_zone=True, dhw=True, wood=False)
@@ -14853,7 +14854,9 @@ _fr_pin_record = _fi_json.loads(_fi_json.dumps(_fr_ec.undo_point("both", _FR_PIN
 R.check(
     "an undo puts each pinned key back where and as it was stored, over the pins the reset wrote",
     _fr_pin_reset != (_FR_PIN_DATA, _FR_PIN_OPTS)
-    and _fr_ec.undone_settings(*_fr_pin_reset, _fr_pin_record) == (_FR_PIN_DATA, _FR_PIN_OPTS),
+    and (_fr_pin_undone := _fr_ec.undone_settings(*_fr_pin_reset, _fr_pin_record)) is not None
+    and {**_fr_pin_undone[0], **_fr_pin_undone[1]} == {**_FR_PIN_DATA, **_FR_PIN_OPTS}
+    and set(_fr_pin_undone[0]) <= {"name"},
     f"reset {_fr_pin_reset}, undone {_fr_ec.undone_settings(*_fr_pin_reset, _fr_pin_record)}",
 )
 # A record missing either half, or holding a half that is not a (data,
@@ -97539,19 +97542,35 @@ from unittest import mock as _sv_mock  # noqa: E402
 _sv_optmod = sys.modules[type(_rk["optimizer"]).__module__]
 
 # D1-s1-51: a 2:2 reason tie inside one slot. ``max`` over a ``set`` picks by
-# the set's iteration order, which is PYTHONHASHSEED's, so the two spellings
-# of one tie read the same winner and one of them is not its first code.
+# the set's iteration order, which is PYTHONHASHSEED's. For a two-code set that
+# order follows insertion when both codes land in one hash slot, and then a set
+# also returns each spelling's first code, so a fixed pair passes a ``set``
+# revert under some seeds. The pair is therefore chosen under the running seed:
+# the first pair of action codes (synthetic codes after them) whose set order
+# is the same whichever code is inserted first. For it, a ``set`` reads one
+# winner for both spellings of the tie, and the slot's first code differs
+# between them, whatever the hash seed.
+from itertools import combinations as _sv_pairs  # noqa: E402
+
+from heatpump_optimizer.const import HEAT_PUMP_ACTION_STATES as _sv_codes  # noqa: E402
+
+_sv_pair = next(
+    (a, b)
+    for a, b in _sv_pairs(
+        [c for c in _sv_codes if c != "idle"]
+        + [f"reason_{n}" for n in range(1000)], 2)
+    if list({a, b}) == list({b, a})
+)
 _sv_ts = [_G_START + timedelta(minutes=15 * i) for i in range(4)]
 _sv_ties = [
-    plan_slots(_sv_ts, [1.0] * 4, [1.0] * 4, 0.25, reasons=list(order))
-    for order in (("cheap_price", "cheap_price", "pre_heat", "pre_heat"),
-                  ("pre_heat", "pre_heat", "cheap_price", "cheap_price"))
+    plan_slots(_sv_ts, [1.0] * 4, [1.0] * 4, 0.25, reasons=[x, x, y, y])
+    for x, y in (_sv_pair, _sv_pair[::-1])
 ]
 R.check(
     "a plan slot's reason tie reads the slot's first code, whatever the "
     "hash seed (D1-s1-51)",
-    [s[0].get("reason") for s in _sv_ties] == ["cheap_price", "pre_heat"],
-    str([s[0].get("reason") for s in _sv_ties]),
+    [s[0].get("reason") for s in _sv_ties] == [_sv_pair[0], _sv_pair[1]],
+    f"{_sv_pair}: {[s[0].get('reason') for s in _sv_ties]}",
 )
 
 # D2-s3-01: the premium lambda*sigma prices the objective only. The reference
@@ -97736,14 +97755,21 @@ R.check(
     _rl_peak_gap is not None and _rl_peak_gap[0] > 0.0 and set(_rl_peak_gap[7:]) == {0.0},
     f"gap to target {_rl_peak_gap and sorted(set(_rl_peak_gap))}",
 )
+# The room trajectories are solver output (multi-start L-BFGS-B), so they are compared within
+# _RL_PEAK_TOL_K, never bit for bit: the same tree plans them differently under OpenBLAS's
+# Haswell and SkylakeX kernels, which CI's runners pick by CPU (CLAUDE.md rule 3). 1e-3 K is
+# far under what the checks separate: the lift's 0.1 K headroom mutant and the 0.2 K peak rise.
+_RL_PEAK_TOL_K = 1e-3
+_rl_peak_null_k = float(np.max(np.abs(_rl_peak["zeros"] - _rl_peak["none"])))
 R.check(
     "the lift may raise the plan's peak over the unlifted plan's, and the lifted plan holds the "
     "target past the ramp; null control, an all-zero margin array plans the unlifted plan",
-    float(_rl_peak["lift"].max()) > float(_rl_peak["none"].max())
-    and float(_rl_peak["lift"][12:].min()) >= 20.0 - 1e-6
-    and np.array_equal(_rl_peak["zeros"], _rl_peak["none"]),
-    f"peak none={_rl_peak['none'].max():.3f} zeros={_rl_peak['zeros'].max():.3f} "
-    f"lift={_rl_peak['lift'].max():.3f} lift min past 3 h={_rl_peak['lift'][12:].min():.3f}",
+    float(_rl_peak["lift"].max()) > float(_rl_peak["none"].max()) + _RL_PEAK_TOL_K
+    and float(_rl_peak["lift"][12:].min()) >= 20.0 - _RL_PEAK_TOL_K
+    and np.allclose(_rl_peak["zeros"], _rl_peak["none"], rtol=0.0, atol=_RL_PEAK_TOL_K),
+    f"peak none={_rl_peak['none'].max():.6f} zeros={_rl_peak['zeros'].max():.6f} "
+    f"lift={_rl_peak['lift'].max():.6f} lift min past 3 h={_rl_peak['lift'][12:].min():.6f} "
+    f"max |zeros-none|={_rl_peak_null_k:.6g} K, tolerance {_RL_PEAK_TOL_K} K",
 )
 
 
diff --git a/tests/harness.py b/tests/harness.py
index 6ca70cb5b7..56347324cd 100644
--- a/tests/harness.py
+++ b/tests/harness.py
@@ -504,6 +504,7 @@ class FakeEntry:
         self.options = dict(options or {})
         self.entry_id = entry_id
         self.version = 1
+        self.minor_version = 1
         self.domain = "heatpump_optimizer"
         self.title = "Heat Pump Optimizer"
         # What a pre-guard entry carries: nothing. The flow's duplicate guard
diff --git a/tests/hastub/homeassistant/config_entries.py b/tests/hastub/homeassistant/config_entries.py
index 60ae633a3f..3358de7267 100644
--- a/tests/hastub/homeassistant/config_entries.py
+++ b/tests/hastub/homeassistant/config_entries.py
@@ -88,6 +88,9 @@ class ConfigEntry(Generic[_DataT]):
         self.options = options or {}
         self.entry_id = entry_id
         self.version = 1
+        # Upstream's ConfigEntry default: an entry created before a flow set
+        # MINOR_VERSION carries 1.
+        self.minor_version = 1
         self.domain = domain
         self.unique_id = unique_id
         self.title = title
@@ -113,6 +116,10 @@ class ConfigFlow:
     # The real FlowHandler's class attributes, as of 2024.6.0: the manager
     # stamps per-instance values over these.
     context: dict[str, Any] = MappingProxyType({})
+    # FlowHandler's version pair: the manager stamps both on the entry it
+    # creates; a flow overriding neither creates 1.1.
+    VERSION = 1
+    MINOR_VERSION = 1
 
     def __init_subclass__(cls, domain=None, **kwargs):
         super().__init_subclass__(**kwargs)
diff --git a/tests/mutation_ledger/killed_by/__init__.py/async_migrate_entry.CMP_BOUND.f611f1d9.json b/tests/mutation_ledger/killed_by/__init__.py/async_migrate_entry.CMP_BOUND.f611f1d9.json
new file mode 100644
index 0000000000..ced354b600
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/__init__.py/async_migrate_entry.CMP_BOUND.f611f1d9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/__init__.py:async_migrate_entry CMP_BOUND f611f1d9",
+  "killed_by": "tests/entities.py",
+  "old": "    if entry.version < CONFIG_ENTRY_VERSION or minor < CONFIG_ENTRY_MINOR_VERSION:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if entry.version <= CONFIG_ENTRY_VERSION or minor < CONFIG_ENTRY_MINOR_VERSION:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/__init__.py/async_migrate_entry.GUARD_OFF.f611f1d9.json b/tests/mutation_ledger/killed_by/__init__.py/async_migrate_entry.GUARD_OFF.f611f1d9.json
new file mode 100644
index 0000000000..8ab84fe1d1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/__init__.py/async_migrate_entry.GUARD_OFF.f611f1d9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/__init__.py:async_migrate_entry GUARD_OFF f611f1d9",
+  "killed_by": "tests/entities.py",
+  "old": "    if entry.version < CONFIG_ENTRY_VERSION or minor < CONFIG_ENTRY_MINOR_VERSION:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerConfigFlow._device_prefill_form.RETURN_DEL.4e4b0c0a.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerConfigFlow._device_prefill_form.RETURN_DEL.4e4b0c0a.json
new file mode 100644
index 0000000000..7443cc6fd1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerConfigFlow._device_prefill_form.RETURN_DEL.4e4b0c0a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerConfigFlow._device_prefill_form RETURN_DEL 4e4b0c0a",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        return _prefill_page(self, \"device_prefill\", schema, notes, errors)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._current.RETURN_DEL.4d9564e1.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._current.RETURN_DEL.4d9564e1.json
new file mode 100644
index 0000000000..0f2733db89
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._current.RETURN_DEL.4d9564e1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._current RETURN_DEL 4d9564e1",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        return _in_force(self._entry)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._current.RETURN_DEL.7c625c8f.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._current.RETURN_DEL.7c625c8f.json
deleted file mode 100644
index 3c8fbcfaad..0000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._current.RETURN_DEL.7c625c8f.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._current RETURN_DEL 7c625c8f",
-  "killed_by": "tests/config_flow_steps.py",
-  "old": "        return {**self._entry.data, **self._entry.options}",
-  "reason": "Recorded by `mutation_table.py --drain` against e3f3b312fff572904f24d78a44a2c4492b1a8ddb: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._prefill_form.RETURN_DEL.bc63bb35.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._prefill_form.RETURN_DEL.bc63bb35.json
new file mode 100644
index 0000000000..c4b88f7359
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow._prefill_form.RETURN_DEL.bc63bb35.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow._prefill_form RETURN_DEL bc63bb35",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        return _prefill_page(self, \"modbus_prefill\", schema, notes, errors)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_modbus_prefill.RETURN_DEL.1541a81b.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_modbus_prefill.RETURN_DEL.c85dc677.json
similarity index 53%
rename from tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_modbus_prefill.RETURN_DEL.1541a81b.json
rename to tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_modbus_prefill.RETURN_DEL.c85dc677.json
index 342c02fbf1..11e2590b14 100644
--- a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_modbus_prefill.RETURN_DEL.1541a81b.json
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_modbus_prefill.RETURN_DEL.c85dc677.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_modbus_prefill RETURN_DEL 1541a81b",
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_modbus_prefill RETURN_DEL c85dc677",
   "killed_by": "tests/config_flow_steps.py",
-  "old": "            return self._prefill_form(_prefill_schema(suggested, suggested), notes, {})",
-  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=11."
+  "old": "            return self._prefill_form(_prefill_schema(suggested, suggested, current), notes, {})",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=11."
 }
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_in_force.RETURN_DEL.ad48f97f.json b/tests/mutation_ledger/killed_by/config_flow.py/_in_force.RETURN_DEL.ad48f97f.json
new file mode 100644
index 0000000000..eb3f3b243a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_in_force.RETURN_DEL.ad48f97f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_in_force RETURN_DEL ad48f97f",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    return {**entry.data, **entry.options}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_prefill_errors.GUARD_OFF.b92e179b.json b/tests/mutation_ledger/killed_by/config_flow.py/_prefill_errors.GUARD_OFF.b92e179b.json
new file mode 100644
index 0000000000..109a68b2be
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_prefill_errors.GUARD_OFF.b92e179b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_prefill_errors GUARD_OFF b92e179b",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    if CONF_SILENT_MODE_WINDOWS not in errors:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_prefill_fields.BOOLOP.7bbbd327.json b/tests/mutation_ledger/killed_by/config_flow.py/_prefill_fields.BOOLOP.7bbbd327.json
new file mode 100644
index 0000000000..9adb682127
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_prefill_fields.BOOLOP.7bbbd327.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_prefill_fields BOOLOP 7bbbd327",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "            if key in values or (key not in keys and key in in_force)",
+  "reason": "Killed by hand (repair seat): BOOLOP (`and` -> `or`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1 (\"a listed field cleared on the setup pre-fill page re-renders empty, not with the stored value\")."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_prefill_schema.RETURN_DEL.db481cd4.json b/tests/mutation_ledger/killed_by/config_flow.py/_prefill_schema.RETURN_DEL.db481cd4.json
new file mode 100644
index 0000000000..3222f86174
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_prefill_schema.RETURN_DEL.db481cd4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_prefill_schema RETURN_DEL db481cd4",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    return _options_schema(_prefill_fields(keys, values, current))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_uncapped_schedule_errors.CMP_BOUND.2973d6c6.json b/tests/mutation_ledger/killed_by/config_flow.py/_uncapped_schedule_errors.CMP_BOUND.2973d6c6.json
new file mode 100644
index 0000000000..fca3d80876
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_uncapped_schedule_errors.CMP_BOUND.2973d6c6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_uncapped_schedule_errors CMP_BOUND 2973d6c6",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    if float(fraction) >= 1.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if float(fraction) > 1.0:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_uncapped_schedule_errors.GUARD_OFF.2973d6c6.json b/tests/mutation_ledger/killed_by/config_flow.py/_uncapped_schedule_errors.GUARD_OFF.2973d6c6.json
new file mode 100644
index 0000000000..8bf3b48311
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_uncapped_schedule_errors.GUARD_OFF.2973d6c6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_uncapped_schedule_errors GUARD_OFF 2973d6c6",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    if float(fraction) >= 1.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_uncapped_schedule_errors.GUARD_OFF.430a8484.json b/tests/mutation_ledger/killed_by/config_flow.py/_uncapped_schedule_errors.GUARD_OFF.430a8484.json
new file mode 100644
index 0000000000..7280cf93e3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_uncapped_schedule_errors.GUARD_OFF.430a8484.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_uncapped_schedule_errors GUARD_OFF 430a8484",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    if not saved.get(CONF_SILENT_MODE_WINDOWS):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=15."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_uncapped_schedule_errors.RETURN_DEL.5e4fa825.json b/tests/mutation_ledger/killed_by/config_flow.py/_uncapped_schedule_errors.RETURN_DEL.5e4fa825.json
new file mode 100644
index 0000000000..03738564c5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_uncapped_schedule_errors.RETURN_DEL.5e4fa825.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_uncapped_schedule_errors RETURN_DEL 5e4fa825",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    return {}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/identity_update.GUARD_OFF.02ac0670.json b/tests/mutation_ledger/killed_by/config_flow.py/identity_update.GUARD_OFF.02ac0670.json
new file mode 100644
index 0000000000..003f7b7150
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/identity_update.GUARD_OFF.02ac0670.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:identity_update GUARD_OFF 02ac0670",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    if unique_id == entry_identity(_in_force(entry)):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/identity_update.GUARD_OFF.9c4f1415.json b/tests/mutation_ledger/killed_by/config_flow.py/identity_update.GUARD_OFF.9c4f1415.json
deleted file mode 100644
index 4d869e3064..0000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/identity_update.GUARD_OFF.9c4f1415.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:identity_update GUARD_OFF 9c4f1415",
-  "killed_by": "tests/entities.py",
-  "old": "    if unique_id == entry_identity({**entry.data, **entry.options}):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 59c2543bdbc244ff4f1e99fffe358edd92060995: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/entry_config.py/undone_settings.RETURN_DEL.a2e2bd26.json b/tests/mutation_ledger/killed_by/entry_config.py/factory_settings.RETURN_DEL.da986bc4.json
similarity index 68%
rename from tests/mutation_ledger/killed_by/entry_config.py/undone_settings.RETURN_DEL.a2e2bd26.json
rename to tests/mutation_ledger/killed_by/entry_config.py/factory_settings.RETURN_DEL.da986bc4.json
index 8806ee5bf9..9e15c90d3b 100644
--- a/tests/mutation_ledger/killed_by/entry_config.py/undone_settings.RETURN_DEL.a2e2bd26.json
+++ b/tests/mutation_ledger/killed_by/entry_config.py/factory_settings.RETURN_DEL.da986bc4.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/entry_config.py:undone_settings RETURN_DEL a2e2bd26",
+  "anchor": "custom_components/heatpump_optimizer/entry_config.py:factory_settings RETURN_DEL da986bc4",
   "killed_by": "tests/features.py",
-  "old": "    return with_settings(wiring, (settings[0], settings[1]))",
+  "old": "    return placed({**data_side, **options_side})",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
 }
diff --git a/tests/mutation_ledger/killed_by/entry_config.py/factory_settings.RETURN_DEL.9521dcc2.json b/tests/mutation_ledger/killed_by/entry_config.py/undone_settings.RETURN_DEL.da986bc4.json
similarity index 63%
rename from tests/mutation_ledger/killed_by/entry_config.py/factory_settings.RETURN_DEL.9521dcc2.json
rename to tests/mutation_ledger/killed_by/entry_config.py/undone_settings.RETURN_DEL.da986bc4.json
index cd6eacae1d..5d17647d95 100644
--- a/tests/mutation_ledger/killed_by/entry_config.py/factory_settings.RETURN_DEL.9521dcc2.json
+++ b/tests/mutation_ledger/killed_by/entry_config.py/undone_settings.RETURN_DEL.da986bc4.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/entry_config.py:factory_settings RETURN_DEL 9521dcc2",
+  "anchor": "custom_components/heatpump_optimizer/entry_config.py:undone_settings RETURN_DEL da986bc4",
   "killed_by": "tests/features.py",
-  "old": "    return with_settings((data, {**options, **pinned}), ({}, {}))",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+  "old": "    return placed({**data_side, **options_side})",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
 }
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 9fe74a122f..f3676b586c 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17334,
+ "class_excess_loc": 17322,
  "const_modules_over_50": 3,
  "coordinator_attrs": 136,
  "coordinator_multiassigned_attrs": 104,
@@ -16,6 +16,6 @@
  "methods_over_150": 14,
  "methods_over_200": 7,
  "name_kept_members": 38,
- "recorded_at": "bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f",
+ "recorded_at": "8751943e17ef4d3ec699e7859ae829b4528d8ce7",
  "seam_cut_total": 415
 }

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
