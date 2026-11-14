CLOUD REVIEWER seat for PR #3564 of tvofi/heatpump_optimizer, at head 9a524d703f3a25325c71f1fe888a35ab53147189. Bus nonce: d82428ee2068935c8dab85be3b59d4e4. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fix-review --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fix-review.md and its rules from main, and follow them exactly. Fetch the PR head with `git fetch origin 9a524d703f3a25325c71f1fe888a35ab53147189`; the PR body is in the PR. Start from the review packet, which you render here rather than read from the dispatcher, whose copy is a path on its own machine: `python3 -I tools/audit/seat/review_packet.py render --pr 3564 --head 9a524d703f3a25325c71f1fe888a35ab53147189 --reviewed-head 8c9dc2697a74ebb036f4dddb8557edd57664d8bd --out $HOME/review-packet.md`. A refusal names its signal and the packet is still written unless the signal is `host-path`; re-read the live checks either way. This is a later round over the reviewed head 8c9dc2697a74ebb036f4dddb8557edd57664d8bd: its scope is the packet's `## Review scope` line, the delta and the previous verdict's findings when it reads `delta`, widened only to the exact already-reviewed code a production (custom_components/) delta puts at non-obvious risk that CI would not detect, the verdict naming path and risk; an instrument, test, policy or body delta never widens it (fix-review.md step 12). Verify each claim adversarially: mutate the fix and check the tests fail, and check every figure in the body at this head. Check that it merges with origin/main (`git merge-tree --write-tree origin/main <head>`); block on main only when that reports a conflict, never on a head that is behind main but merges cleanly (the train re-proves it on the current main). Wait for CI on this head only by re-running `python3 tools/audit/seat/merge_train.py classify 9a524d703f3a25325c71f1fe888a35ab53147189 --pr 3564` in the background, at least 60 s between runs, until it exits 0 (GREEN), 1 (RED), 2 (unreadable: say so in the verdict) or 4 (APPROVAL-OWED: the only red is the budget raise's approval, which follows your verdict; judge the head as GREEN and quote the line); 3 is WAIT, so run it again. Never wait with `pgrep` or `pkill`, whose `-f` pattern matches the waiter's own command line, nor on a context the ruleset does not require, such as `prelude`. A review_packet `required-red` signal does not stop you while classify prints WAIT: classify decides. If your review is otherwise complete and classify still prints WAIT after about 30 minutes of polling, stop waiting: put the line `pending-ci: <the context names it printed>` straight after the `bus-nonce:` line and return the verdict as below; the relay posts it once CI is green at this head, refuses it over a red, and refuses it if the head moves. If the review is not complete then, push `Fix review: blocked 9a524d703f3a25325c71f1fe888a35ab53147189 ci-wait: <the last classify line>` as below.
Output: in a fresh directory of your own (`W=$(mktemp -d)`), write verdict.md, whose first line is exactly `Fix review: merge 9a524d703f3a25325c71f1fe888a35ab53147189` or `Fix review: blocked 9a524d703f3a25325c71f1fe888a35ab53147189 <class>: <reason>` (no brackets; the class is lower-case letters and dashes), in the format the role file gives, then a blank line, then `bus-nonce: d82428ee2068935c8dab85be3b59d4e4`, then the body in sections. A blocked verdict's block goes under `## Block`. Each finding this PR does not settle (a defect, a surviving mutant, a deferral, a follow-up, a task owed after the merge) is its own bullet under `## Findings` ending in its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>` (finding-propagation.md). Everything else (RESULT lines, re-runs, CI state, figures you could not re-derive) goes under `## Evidence`: tools/audit/carry_audit.py reads an item there, and under any heading of a merge verdict but `## Findings`, `## Friction`, a block heading and a note heading (Residuals, Follow-ups, Notes ...), by its shape alone: a finding only when it opens with a lead word (Residual:, Follow-up:, Out of scope: ...) or carries a `Carry:`, so a defect you hand on goes under `## Findings`, and bus.sh refuses a verdict holding a finding with no valid `Carry:`. Put the evidence files in `ev/` beside it, under 25 MB in all (cite a large log by path and keep its tail: a ~30 MB ev/ once failed its push), and make at least one file under `ev/` contain the full 40-hex head `9a524d703f3a25325c71f1fe888a35ab53147189` (e.g. `ev/HEAD.txt` holding the head you reviewed, beside your command output): bus.sh refuses a verdict whose `ev/` names no head. Do NOT run bus.sh: its dispatch record lives on the orchestrator's machine, which publishes the verdict there (cloud_relay.sh). Return the verdict on a probe ref, and push nothing else; this builds one parentless commit with a private index and touches no branch of your checkout: `R=$(git rev-parse --show-toplevel); G=$(git rev-parse --absolute-git-dir); mkdir -p $W/pr && cp -r $W/verdict.md $W/ev $W/pr/ && cd $W/pr && T=$(GIT_DIR=$G GIT_INDEX_FILE=$W/idx GIT_WORK_TREE=$W/pr sh -c 'git add -A -f . && git write-tree') && C=$(GIT_DIR=$G git -c user.name=hpo-fixer -c user.email=70032254+tvofi@users.noreply.github.com commit-tree $T -m "verdict 3564 9a524d703f3a25325c71f1fe888a35ab53147189") && git -C $R push -q origin $C:refs/heads/probe/rev-3564-d82428ee`. That ref is the return signal. Do not post comments, approve or merge.
Every way your turn ends pushes a verdict to that ref: a setup or hook refusal that stops you pushes `Fix review: blocked 9a524d703f3a25325c71f1fe888a35ab53147189 seat-refused: <the refusing line>`; never end your turn while a background poll runs. After the push, read the ref back with `git ls-remote origin refs/heads/probe/rev-3564-d82428ee`, and push again if it does not print your commit.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# Review packet #3564
head: 9a524d703f3a25325c71f1fe888a35ab53147189
base: 50373173d486faf394b24637c177ab38b691b394

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=132264574602 skipped
cancel-superseded id=132264578974 queued
prelude id=132264578932 queued
refresh id=132264578720 queued

## Refusals
none

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

## Review scope: delta (later round over the reviewed head 8c9dc2697a74ebb036f4dddb8557edd57664d8bd)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at 8c9dc2697a74ebb036f4dddb8557edd57664d8bd
Fix review: merge 8c9dc2697a74ebb036f4dddb8557edd57664d8bd

bus-nonce: f3dea7a3ccd3b8c7452547c4e275712f

Round 1, handoff review: the head is the handoff tip, and the body's `## Head` names the same SHA. There is no pull request, no review packet and no CI run yet, so no live checks were read. The `## Red checks` section says none, and there is no run to contradict it. Role contracts: `git diff 154dbb4c...origin/main -- dev/governance/roles/` is empty, so the contract is current.

## Findings

- Main-merge break: the head merges into current origin/main (e23124ff6e) without a textual conflict, but `tests/doc_claims.py` then exits 1 at `tests/doc_claims.py:4739` with `AttributeError: module 'heatpump_optimizer.pump_arbiter' has no attribute 'SPLIT_MIN_MINUTES'` (ev/doc_claims_on_main_merge.txt). Main's 4a8115bc10 (R10-DUTY-SWITCH-PLANNER-PRICE) moved the constant to `duty_legs.SPLIT_MIN_MINUTES` with the same value, 5.0, and kept the 5-minute rule. I monkeypatched the pin to point at `duty_legs`; all 19 pins and the written-slot arm then come back empty on the main merge, so the text stays true and only the import is stale. The brief forbids blocking on a head that merges cleanly, so this is a merge verdict. The train's re-proof on current main will go red here until the pin reads `duty_legs.SPLIT_MIN_MINUTES`. That one-line test delta needs no wider review, but a red CI never carries. Carry: dismissed: the train re-proves at current main and this red returns the branch to its fixer; the repair is the one-line pin repoint named here
- Conflict with #3561 (a02783d4). The two wordings agree: both say that under Control the optimizer writes the space set-point entity (3561: "writes it on every plan step"; this branch: writes the plan's room or water temperature), and that under Off or Observe it is only read. This branch will conflict with #3561 once #3561 merges. `git merge-tree --write-tree a02783d4 <head>` exits 1 with CONFLICT (content) in strings.json, en.json, sv.json and de.json (ev/merge_tree.txt). The cause is adjacent-line edits: #3561 changes `space_setpoint_entity` and this branch changes `space_setpoint_unit` on the next line. The resolution is to keep both lines. I resolved it that way and checked the result: `flow_write_findings` returns [] with and without `_OWNED_ELSEWHERE`, so the exemption expires as the body says and #3561's text passes the written-slot arm. Carry: dismissed: a hand resolution the orchestrator makes at the second merge, both sides kept; measured here
- Translations are not pinned (brief item 3). The written-slot arm reads only strings.json. Mutant M7 plants "never writes" in sv.json's `space_setpoint_unit` and stays green (`ALL 354 checks PASSED`, ev/mutants.txt). sv and de are covered only for keys, by entities.py. Carry: R11-INTAKE-R10-RESIDUE
- The written-slot set is narrower than the set of written entities (brief item 3). It is derived from `pump_arbiter._entities`, which returns mode, dhw_setpoint, space_setpoint and silent. The heat pump on/off switch (`heat_pump_switch_entity`) is also written: the body's own `pump_duty_mode` correction says the plan switches it under all three modes. Mutant M9 appends "The optimizer never writes it." to that key's help and stays green. The `dhw_disinfection_switch_entity` written under Control is outside the set too. No shipped sentence is false today, so this is a gap in pin coverage, not an open seam. Carry: R11-INTAKE-R10-RESIDUE
- Two rows in the record cite strings.json (`options.step.advanced.menu_options`) rather than the code that builds the menu: `options.step.init.description` and `options.step.advanced.description`, both judged true. Neither rests on a comment or docstring, so brief item 1 does not block. Carry: R11-INTAKE-R10-RESIDUE
- `pump_duty_mode` says "toward 5 °C (or the Minimum lift above the inlet water)". This is a temperature difference (FLOW_MIN_LIFT_K), so the unit should be K. The wording predates this branch ("toward 5 °C (or flow_min_lift_k)" at the merge base), and the pin keys on "°C", so the unit fix also needs the regex changed. Carry: R11-INTAKE-R10-RESIDUE

## Evidence

- RESULT mutation: 9 mutants at the head, using ev/mutants.sh with doc_claims.py as the closure check (ev/mutants.txt).
  - Killed:
    - M1: `space_setpoint_unit` restored to its merge-base text gives the written-slot FAIL.
    - M2: `LEASE_MINUTES` set to 60 in pump_arbiter.py gives the figure-pin FAIL plus the null control.
    - M3: `SPLIT_MIN_MINUTES` set to 6 gives the figure-pin FAIL.
    - M4: `_OWNED_ELSEWHERE` emptied gives the `space_setpoint_entity` FAIL. This is the body's null control.
    - M5: `ECONOMY_MIN_TEMP_WIDENING` set to 2.0 gives the figure-pin FAIL.
    - M6: `curve_learning.STEP_K` set to 0.3 gives the figure-pin FAIL ("quotes six tenths, the code holds 0.9").
    - M8: "never writes" planted on `heat_pump_capacity_limited_entity` (the silent slot) gives the written-slot FAIL.
  - Survived: M7 (sv.json) and M9 (`heat_pump_switch_entity`). Both are gaps in coverage, not in the claims the diff pins; they are listed under Findings.
  - Baseline: `ALL 354 checks PASSED` in 11.9 s.
- RESULT figures at the head (ev/head_figures.txt):
  - Flow strings: 1074 per catalogue for strings, en, sv and de.
  - Claim set: 370 distinct texts at the head. The record has 369 rows, matching the stated 369 at the merge base.
  - Verdict counts: {'true': 286, 'false': 27, 'stale': 12, 'unverifiable': 4, 'no-claim': 40}.
  - `git diff --stat` prints 112/112/112/110 for strings, de, en and sv.
  - tests/doc_claims.py: ALL 354 checks PASSED.
  - tests/entities.py: completed with exit 0.
  - tests/structure.py: STRUCTURE RATCHET PASSED.
  - All figures match the body.
- Not re-derived: the scoped-gate figures (`MODE: SCOPED -- 11 script(s) run, 22 scoped out` and run.sh's 13/21). The gate is a heavy run, CI has not run, and the contract has CI's figures cited rather than re-run. Also not re-derived: the move of `tests/closures.json` `tests/harness_headers.py` from rc 1 to rc 0 and its added `flow_claims.py` entry, which is a recorded measurement I did not re-run.
- RESULT brief item 1: ev/evidence_kind.py classified every evidence `path:line` at the merge base by AST and tokenize as code versus comment or docstring. Every row judged true, false, stale or unverifiable cites at least one code line, apart from the two strings.json-cited rows under Findings. I spot-checked rows against the code: `flow_curve_cop_enabled`, `dhw_setpoint`, `away_dhw_min_temperature`, `min_temperature`, `max_temperature`, `space_setpoint_unit` and `pump_duty_mode`. In each, the why and the correction are grounded in code lines such as constants, `_entities` and `_share`, not in comments.
- RESULT brief item 3, pinned claims: the 19 figure pins and the written-slot arm are pinned and every pin was killed by a mutant. Unpinned: translations, the switch slots outside `_entities`, and the prose-only rows the body names (the 0.5 K night floor literal and the pre-fill registers).
- Merge with origin/main: `git merge-tree --write-tree origin/main <head>` exits 0. The claimnotes driver line is `LEDGER-MERGE: resolved tests/closures.json` and no claim file conflicts (ev/merge_tree.txt).
- VERSION, the manifest version and RELEASE_NOTES.md are untouched: `git diff 154dbb4c <head>` is empty for all three. The claim files are untouched, and no golden fixtures were moved.
- owed-reds set read with `merge_train.py owed-reds`. There are no runs, so no red is owed an answer.
- Forward-carry: every body line carries `R11-INTAKE-R10-RESIDUE`. With no pull request, carry_audit's `pr` check cannot run against a body yet.

## Delta diff: git diff 8c9dc2697a74ebb036f4dddb8557edd57664d8bd 9a524d703f3a25325c71f1fe888a35ab53147189
diff --git a/README.md b/README.md
index b917dacc89..e4c5f4b273 100644
--- a/README.md
+++ b/README.md
@@ -1078,6 +1078,7 @@ Each clears itself once the cause is gone.
 - **The heat pump does not hold a setting the optimizer wrote** — the pump reads back something else after two writes. To change the pump by hand, turn **Optimizer Active** off first.
 - **Stored learning could not be read** — stored data from another version could not be read, so that part of what was learned starts again from defaults. The integration keeps running.
 - **Silent windows are not enforced** — the capacity-limited slot is not a switch the integration can hold. Assign the pump's own night-mode switch, or remove the silent windows.
+- **The heat pump cannot hold the hot water minimum** — You named a *Hot water start hysteresis* entity, and the hot water minimum sits above the temperature the pump starts a charge at (its hot water target less that hysteresis). The plan places no charge the pump would not start, so it shows the tank falling under the minimum before each charge. Lower the minimum to the start temperature or less, raise the hot water set-point, or reduce the hysteresis on the pump.
 
 ## ECL110 heat-curve control
 
diff --git a/custom_components/heatpump_optimizer/config_flow.py b/custom_components/heatpump_optimizer/config_flow.py
index 80e187f0af..c7afb1923a 100644
--- a/custom_components/heatpump_optimizer/config_flow.py
+++ b/custom_components/heatpump_optimizer/config_flow.py
@@ -412,6 +412,8 @@ from .const import (
     CONF_PUMP_DUTY_MODE,
     DEFAULT_PUMP_DUTY_MODE,
     PUMP_DUTY_MODES,
+    CONF_SPACE_HYSTERESIS_ENTITY,
+    CONF_DHW_HYSTERESIS_ENTITY,
     CONF_MOLD_GUARD_ENABLED,
     DEFAULT_MOLD_GUARD_ENABLED,
     CONF_INDOOR_HUMIDITY_ENTITY,
@@ -1725,6 +1727,11 @@ _OPTION_FIELDS: Final[tuple[_F, ...]] = (
     # -- entities_pump
     _F("entities_pump", CONF_HEAT_PUMP_MODE_ENTITY, _STORED, _entity_of(list(topology.ASSIGNABLE_KEYS[CONF_HEAT_PUMP_MODE_ENTITY]))),
     _F("entities_pump", CONF_PUMP_DUTY_MODE, DEFAULT_PUMP_DUTY_MODE, _select(list(PUMP_DUTY_MODES), 'pump_duty_mode')),
+    # The pump's own start hysteresis per duty: one picker each, a number or a sensor.
+    *(
+        _F("entities_pump", key, _STORED, _entity_of(['sensor', 'number', 'input_number']))
+        for key in (CONF_SPACE_HYSTERESIS_ENTITY, CONF_DHW_HYSTERESIS_ENTITY)
+    ),
     _F("entities_pump", CONF_HEAT_PUMP_DEFROST_ENTITY, _STORED, _entity_of(list(topology.ASSIGNABLE_KEYS[CONF_HEAT_PUMP_DEFROST_ENTITY]))),
     _F("entities_pump", CONF_HEAT_PUMP_ONLINE_ENTITY, _STORED, _entity_of(list(topology.ASSIGNABLE_KEYS[CONF_HEAT_PUMP_ONLINE_ENTITY]))),
     _F("entities_pump", CONF_HEAT_PUMP_FAULT_ENTITY, _STORED, _entity_of(list(topology.ASSIGNABLE_KEYS[CONF_HEAT_PUMP_FAULT_ENTITY]))),
diff --git a/custom_components/heatpump_optimizer/const.py b/custom_components/heatpump_optimizer/const.py
index a77cdc98b2..24f7060188 100644
--- a/custom_components/heatpump_optimizer/const.py
+++ b/custom_components/heatpump_optimizer/const.py
@@ -1036,6 +1036,15 @@ DEFAULT_DHW_DISINFECTION_MODE: Final = "observe"
 CONF_PUMP_DUTY_MODE: Final = "pump_duty_mode"
 DEFAULT_PUMP_DUTY_MODE: Final = "off"
 PUMP_DUTY_MODES: Final = ("off", "observe", "control")
+#: The pump's own start hysteresis per duty, K, read from an entity as a
+#: temperature difference (``inputs.read_temperature_delta_k``) with no age
+#: gate: a setting changes only when someone changes it. Hot water: the pump
+#: starts a charge only below its target less this, so the plan places no
+#: charge on a warmer tank. Heating: its controller starts only once the
+#: target sits this far above the water, so the floor's lift is never below
+#: it (``thermal_model.start_flow_min_lift_k``).
+CONF_SPACE_HYSTERESIS_ENTITY: Final = "space_hysteresis_entity"
+CONF_DHW_HYSTERESIS_ENTITY: Final = "dhw_hysteresis_entity"
 #: How long a switch the optimizer turned on may stay unreadable before its
 #: record is dropped with a repair, when it is no longer the configured
 #: switch or has no state at all (renamed or deleted). Not immediate: at
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index a362be579d..c4d284756d 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -206,6 +206,7 @@ from .inputs import (
     age_of,
     normalize_price_per_kwh,
     parse_bool,
+    read_start_hysteresis,
     price_per_kwh,
     stale_summary,
     state_power_kw,
@@ -256,7 +257,7 @@ from .accuracy import (
 )
 from .comfort_learning import ComfortLearner, OverrideEvent
 from .defrost import DefrostDerate, DefrostWindow, in_frost_band
-from . import early_cutoff, pump_arbiter, pump_signals, supply_hold
+from . import duty_switch, early_cutoff, pump_arbiter, pump_signals, supply_hold
 from . import issues, setpoint_check
 from . import quiet_windows
 from . import price_tiles
@@ -6220,13 +6221,14 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         share no mutable state with the event loop (#240).
         """
         ctx = getattr(self, "_ctx", self)
+        now = dt_util.now()
         tariff = self._capacity_tariff()
         threshold = self._peak_tracker.threshold_kw(tariff)
         # Post-outage recovery (#22): every neighbour restarts at once, so
         # the fresh-month "no reference yet" free pass is exactly wrong now.
         # Force the peak term active by pricing from zero when the threshold
         # would otherwise be infinite.
-        if self._outage_recovery_active(dt_util.now()) and not np.isfinite(threshold):
+        if self._outage_recovery_active(now) and not np.isfinite(threshold):
             threshold = 0.0
         config_bands: dict[str, float] = {}
         dhw_bands: dict[str, float] = {}
@@ -6241,17 +6243,16 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             price_risk_lambda=ctx._config.price_risk_lambda,
             baseline_load_kw=self._baseline_house_load(n_steps),
             cycling_cost=self._effective_cycling_cost(),
+            **duty_switch.planner_fields(self),
             # The optimizer prices surplus consumption at this; an
             # entity-supplied compensation can change between runs.
             pv_export_price=self._pv_export_price(),
             comfort_weight=self._comfort_weight(),
             holiday_dates=away_mode.holiday_dates(
-                self.hass, ctx._config.holiday_calendar_entity,
-                dt_util.now(),
+                self.hass, ctx._config.holiday_calendar_entity, now,
             ),
             **config_bands,
         )
-        now = dt_util.now()
         params = replace(
             copy.deepcopy(ctx._thermal_params),
             **dhw_bands,
@@ -6732,13 +6733,13 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         # DHW, 40 °C buffer) reached every solve otherwise (D12-s1-01).
         dhw = reader.read(CONF_DHW_TEMP_ENTITY)
         buffer_reading = reader.read(CONF_BUFFER_TANK_TEMP_ENTITY)
-        plan, seeded_at = self._optimization_result, dt_util.now()
         if dhw.ok:
             self._dhw_temperature = dhw.value
         combi = _ctx_of(self)._thermal_params.combi_tank_active
-        level, buffer_level = tank_levels(combi, dhw, buffer_reading, plan, seeded_at)
+        level, buffer_level = tank_levels(combi, dhw, buffer_reading, self._optimization_result, dt_util.now())
         state.dhw_temperature = state.dhw_temperature if level is None else level
         state.buffer_tank_temperature = state.buffer_tank_temperature if buffer_level is None else buffer_level
+        read_start_hysteresis(state, self.hass, self.effective_config)
 
         # Wood tank temperature (issue #40): re-read from the physical tank
         # each cycle through the same stale-aware reader — the model never
diff --git a/custom_components/heatpump_optimizer/dhw_planner.py b/custom_components/heatpump_optimizer/dhw_planner.py
index 03b5171370..cd0e495d1c 100644
--- a/custom_components/heatpump_optimizer/dhw_planner.py
+++ b/custom_components/heatpump_optimizer/dhw_planner.py
@@ -20,6 +20,7 @@ from __future__ import annotations
 
 import logging
 from dataclasses import dataclass
+from functools import partial
 from typing import Any, Callable, NamedTuple, Protocol
 
 import numpy as np
@@ -51,6 +52,8 @@ from .thermal_model import (
     dhw_draw_scale,
     added_power_for_heat_per_cop_kw,
     delivered_heat_kw,
+    dhw_start_below_c,
+    dhw_step_target_c,
     heat_per_cop_kw,
     power_for_heat_per_cop_kw,
 )
@@ -137,6 +140,18 @@ def _forced_off_with(
     return forced_off | mask
 
 
+def _with_placement_ban(
+    forced_off: np.ndarray | None, ban: np.ndarray | None, n_steps: int
+) -> np.ndarray | None:
+    """``forced_off`` with a caller's placement ban OR'd in; unchanged with none.
+
+    The optimizer's duty-switch candidate enters here and nowhere else: unlike
+    ``off_steps`` a ban moves no disinfection step, and a manual force-on pin
+    inside it still wins, because the pins are overlaid after the placement.
+    """
+    return forced_off if ban is None else _forced_off_with(forced_off, ban, n_steps)
+
+
 def _legionella_off_mask(off_steps: Any, n_steps: int) -> np.ndarray | None:
     """The Off window as a horizon mask, or None when there is no window."""
     if off_steps is None:
@@ -196,6 +211,108 @@ def _drop_off_steps(mask: np.ndarray, off: np.ndarray | None) -> np.ndarray:
     return kept
 
 
+#: How many times :func:`place_startable` re-buys what the start condition
+#: barred before it settles for dropping. A round re-buys under the charges
+#: the round before kept, and the measured placements settle in two or three
+#: (``dev/audit/harnesses/r10_dhw_start_hysteresis.py``, repair_rounds_max),
+#: so eight is that with room to spare and still a bound.
+STARTABLE_ROUNDS = 8
+
+
+def dhw_start_temps(
+    params: ThermalParameters, state: ThermalState, n_steps: int, cycle_step: int | None
+) -> np.ndarray | None:
+    """Per step, the tank temperature below which the pump starts a charge, °C.
+
+    The target the arbiter writes on that step (``dhw_step_target_c`` on the
+    set-point entity's grid, ``state.dhw_setpoint_grid``: the cycle's on
+    ``cycle_step``, the everyday one elsewhere) less the pump's start
+    hysteresis (``state.dhw_start_hysteresis_k``), so a disinfection charge
+    is judged against its own target and a stepped entity's against the step
+    it lands on. ``None`` where no start condition is known
+    (``dhw_start_below_c``).
+    """
+    hysteresis_k, grid = state.dhw_start_hysteresis_k, state.dhw_setpoint_grid
+    everyday = dhw_start_below_c(dhw_step_target_c(params, False, grid), hysteresis_k)
+    if everyday is None:
+        return None
+    start = np.full(n_steps, everyday)
+    if cycle_step is not None and 0 <= cycle_step < n_steps:
+        start[cycle_step] = dhw_start_below_c(dhw_step_target_c(params, True, grid), hysteresis_k)
+    return start
+
+
+def startable_steps(
+    plan: np.ndarray, temps: np.ndarray, start_below: np.ndarray | None
+) -> np.ndarray:
+    """The steps where charging is something the pump does.
+
+    A step that opens on a tank below its start temperature (``temps[i]``,
+    the simulated level at its start), and the step after one of a charge
+    under way, which runs on to its target. A charge is under way from the
+    step it opens below its start temperature, or from the first step, where
+    it is kept as one that may be (:func:`drop_unstartable`); a charge the
+    pump would not start carries nothing on, so the repair buys neither
+    inside it nor behind it. Every step where no start condition is known
+    (``start_below`` ``None``).
+    """
+    on = np.asarray(plan, dtype=float) > 0.0
+    if start_below is None:
+        return np.ones(on.size, dtype=bool)
+    ok: np.ndarray = np.asarray(temps, dtype=float)[: on.size] < start_below[: on.size]
+    under_way = bool(on[:1].any())
+    for i in range(1, on.size):
+        ok[i] |= under_way
+        under_way = bool(on[i] and ok[i])
+    return ok
+
+
+def drop_unstartable(
+    plan: np.ndarray, start_below: np.ndarray, temps_of: Callable[[np.ndarray], np.ndarray]
+) -> np.ndarray:
+    """``plan`` without the charges the pump would never start.
+
+    Each run is judged in time order on the trajectory ``temps_of`` simulates
+    for the runs kept before it: one that begins on a tank at or above its
+    step's start temperature is removed whole. A run at the first step is
+    kept, as it may be a charge already under way (Bankaifan, #3440).
+    """
+    plan = np.array(plan, dtype=float)
+    on = plan > 0.0
+    for i in np.flatnonzero(on[1:] & ~on[:-1]) + 1:
+        end = i + int(np.argmin(np.append(on[i:], False)))
+        if temps_of(plan)[i] >= start_below[i]:
+            plan[i:end] = 0.0
+    return plan
+
+
+def place_startable(
+    plan: np.ndarray,
+    start_below: np.ndarray | None,
+    temps_of: Callable[[np.ndarray], np.ndarray],
+    repair: Callable[..., np.ndarray],
+) -> np.ndarray:
+    """The floor repair of ``plan`` under the pump's start condition.
+
+    With no condition, ``repair(plan=plan)``, the call as it always was. With
+    one, the charges the pump would not start are dropped and ``repair``,
+    handed the condition so it places only on :func:`startable_steps`,
+    re-buys what the floor still needs; a top-up
+    warms the tank under every later charge, so the two repeat until the
+    plan stands, at most :data:`STARTABLE_ROUNDS` times. The plan that leaves
+    holds no charge the pump would not start, and is short of the floor only
+    where no startable step can hold it.
+    """
+    if start_below is None:
+        return repair(plan=plan)
+    for _ in range(STARTABLE_ROUNDS):
+        fixed = repair(plan=drop_unstartable(plan, start_below, temps_of), start_below=start_below)
+        if np.array_equal(fixed, plan):
+            break
+        plan = fixed
+    return drop_unstartable(plan, start_below, temps_of)
+
+
 class _DhwLegionellaPlan(NamedTuple):
     """What the anti-legionella stage decides, and the ceilings it sets."""
 
@@ -959,6 +1076,7 @@ class DhwPlanner:
         off_steps: np.ndarray | None = None,
         wood_temps: np.ndarray | None = None,
         tank_exo_kw: np.ndarray | None = None,
+        placement_ban: np.ndarray | None = None,
     ) -> tuple[DhwPlan, np.ndarray]:
         """Build the DHW availability requirements and a cheapest-first plan.
 
@@ -1087,6 +1205,7 @@ class DhwPlanner:
             # remain. Not a pin: the window is a scheduled decision, so the
             # pin-safety release loop in ``optimize`` never frees these.
             forced_off = _forced_off_with(forced_off, off_steps, n_steps)
+        forced_off = _with_placement_ban(forced_off, placement_ban, n_steps)
 
         # Pre-heating is allowed anywhere in the horizon: the planners price the
         # standby losses of storing heat, so an early cheap hour wins only when
@@ -1166,17 +1285,8 @@ class DhwPlanner:
         # below the pump's practical minimum is then zeroed, never re-raised:
         # the rating always wins, and a published trickle is a power level the
         # on/off hardware cannot deliver.
-        schedule = self._clamp_dhw_to_capacity(
-            plan=schedule,
-            initial_temp=initial_state.dhw_temperature,
-            outdoor_temps=outdoor_temps,
-            draw_rates=draw_rates,
-            dt=dt,
-            max_temp=max_temp,
-            humidity=humidity,
-            exo_kw=tank_exo_kw,
-        )
-        schedule = np.where(schedule < min_run_power - 1e-9, 0.0, schedule)
+        schedule = self._ctx_clamp(
+            ctx, initial_state.dhw_temperature, draw_rates, max_temp, schedule)
 
         # The floor gets the same physics check the rating just got. The LP
         # and the greedy passes plan on an affine tank; the trajectory the
@@ -1186,15 +1296,17 @@ class DhwPlanner:
         # window (stress: winter_mild). Top up at the cheapest usable step
         # before each breach until the simulated trajectory honours the
         # requirement, then re-apply the rating, which always wins.
-        schedule = self._repair_dhw_floor(
+        start_below = dhw_start_temps(params, initial_state, n_steps, legionella_step)
+        tank = (ctx, initial_state.dhw_temperature, draw_rates)
+        schedule = place_startable(schedule, start_below, partial(self._ctx_temps, *tank), partial(
+            self._repair_dhw_floor,
             ctx,
-            plan=schedule,
             initial_temp=initial_state.dhw_temperature,
             draw_rates=draw_rates,
             requirement=requirement,
             max_temp=max_temp,
             forced_off=forced_off,
-        )
+        ))
         # Not re-clamped here, because the repair now carries the clamp
         # inside its own loop: every top-up it places is followed by one,
         # so a plan leaves this stage already bounded by the per-step
@@ -1249,19 +1361,10 @@ class DhwPlanner:
         # it. The requirement is stashed for that loop to check against.
         if dhw_pins is not None:
             schedule = self._apply_dhw_pins(schedule, dhw_pins, min_run_power)
-            schedule = self._clamp_dhw_to_capacity(
-                plan=schedule,
-                initial_temp=initial_state.dhw_temperature,
-                outdoor_temps=outdoor_temps,
-                draw_rates=draw_rates,
-                dt=dt,
-                max_temp=max_temp,
-                humidity=humidity,
-                exo_kw=tank_exo_kw,
-            )
             # Same hygiene as the automatic path: a step the rating truncated
             # below the pump's minimum cannot actually run, even a pinned one.
-            schedule = np.where(schedule < min_run_power - 1e-9, 0.0, schedule)
+            schedule = self._ctx_clamp(
+                ctx, initial_state.dhw_temperature, draw_rates, max_temp, schedule)
         if blocked:
             # The invariant, restated after every path that can add energy —
             # including the manual force-on overlay directly above, which a
@@ -1519,10 +1622,7 @@ class DhwPlanner:
 
             # Refine the COP estimate against the tank temperatures this plan
             # actually produces, so the cost ranking reflects reality.
-            temps = self._dhw_plan_temps(
-                best, initial_temp, outdoor_temps, draw_rates, dt, humidity,
-                ctx.tank_exo_kw,
-            )
+            temps = self._ctx_temps(ctx, initial_temp, draw_rates, best)
             refined = self._dhw_cop_profile(outdoor_temps, temps[:-1], humidity)
             if np.allclose(refined, cop, rtol=0.02):
                 break
@@ -1602,6 +1702,25 @@ class DhwPlanner:
             )
         )
 
+    def _ctx_temps(
+        self, ctx: _DhwPlanContext, initial_temp: float, draw_rates: np.ndarray, plan: np.ndarray
+    ) -> np.ndarray:
+        """The tank trajectory under ``plan`` on the context's own weather, step and inflow."""
+        return self._dhw_plan_temps(
+            plan, initial_temp, ctx.outdoor_temps, draw_rates, ctx.dt, ctx.humidity, ctx.tank_exo_kw)
+
+    def _ctx_clamp(
+        self, ctx: _DhwPlanContext, initial_temp: float, draw_rates: np.ndarray,
+        max_temp: np.ndarray, plan: np.ndarray,
+    ) -> np.ndarray:
+        """``plan`` held to the tank's capacity on the context's own weather, step
+        and inflow, a step the clamp leaves below a runnable block zeroed: the
+        rating always wins, and a trickle is a power the hardware cannot deliver."""
+        plan = self._clamp_dhw_to_capacity(
+            plan, initial_temp, ctx.outdoor_temps, draw_rates, ctx.dt, max_temp,
+            ctx.humidity, ctx.tank_exo_kw)
+        return np.where(plan < ctx.min_run_power - 1e-9, 0.0, plan)
+
     def _repair_dhw_floor(
         self,
         ctx: _DhwPlanContext,
@@ -1612,6 +1731,7 @@ class DhwPlanner:
         requirement: np.ndarray,
         max_temp: np.ndarray,
         forced_off: np.ndarray | None = None,
+        start_below: np.ndarray | None = None,
     ) -> np.ndarray:
         """Top up the plan until the SIMULATED trajectory meets the floor.
 
@@ -1683,6 +1803,7 @@ class DhwPlanner:
             usable = headroom > 1e-6
             if forced_off is not None:
                 usable &= ~np.asarray(forced_off[lo : b + 1], dtype=bool)
+            usable &= startable_steps(plan, temps, start_below)[lo : b + 1]
             # Degrees of room under the ceiling for heat added at each
             # candidate. The heat is stored from the candidate to the breach,
             # decaying as it leaks away, so the bound is the tightest of
@@ -1768,17 +1889,7 @@ class DhwPlanner:
                 # truncates below a runnable block is zeroed, the same rule
                 # the caller applies to its own clamp: a published trickle is
                 # a power the on/off hardware cannot deliver.
-                plan = self._clamp_dhw_to_capacity(
-                    plan=plan,
-                    initial_temp=initial_temp,
-                    outdoor_temps=outdoor_temps,
-                    draw_rates=draw_rates,
-                    dt=dt,
-                    max_temp=ceiling,
-                    humidity=humidity,
-                    exo_kw=ctx.tank_exo_kw,
-                )
-                plan = np.where(plan < min_run_power - 1e-9, 0.0, plan)
+                plan = self._ctx_clamp(ctx, initial_temp, draw_rates, ceiling, plan)
                 if np.array_equal(plan, before):
                     # The block went in and came straight back out. Repeating
                     # it is a loop, not a repair, so this breach is recorded
@@ -1786,10 +1897,7 @@ class DhwPlanner:
                     # on to the next.
                     unreachable.add(b)
                 else:
-                    temps = self._dhw_plan_temps(
-                        plan, initial_temp, outdoor_temps, draw_rates, dt, humidity,
-                        ctx.tank_exo_kw,
-                    )
+                    temps = self._ctx_temps(ctx, initial_temp, draw_rates, plan)
             else:
                 # Nothing ceiling-legal can fix this step; move on rather than
                 # abandoning every later breach with it.
diff --git a/custom_components/heatpump_optimizer/duty_legs.py b/custom_components/heatpump_optimizer/duty_legs.py
new file mode 100644
index 0000000000..ecb3c6b38f
--- /dev/null
+++ b/custom_components/heatpump_optimizer/duty_legs.py
@@ -0,0 +1,236 @@
+"""The legs a plan step is served in, the switches between them, and what a stop costs.
+
+One concern with one owner, on ``plan_step.py``'s own argument: the pump
+arbiter serves a planned both step as a hot-water leg and a heating leg, and
+the optimizer prices the switches that serving makes, so two modules need one
+rule and neither may import the other. A leaf: numpy, the plan's running rule
+and the step width, nothing of Home Assistant.
+
+A switch between duties at constant draw is invisible to the cycling term,
+which prices the swing of the combined draw. On an install whose compressor
+stops at such a switch (pull request 3420, Bankaifan: hot water to heating,
+three times out of three) the stop turns the swing ``|a - b|`` into ``a + b``.
+The difference, ``2 * min(a, b)``, is ``min(a, b) / p_max`` cycles in the
+cycling term's own unit, and that is the weight a switch carries here, taken
+with the learned probability that the direction stops the compressor.
+
+A pair of per-direction values is always ``(hot water to heating, heating to
+hot water)``.
+"""
+from __future__ import annotations
+
+import math
+from typing import Any
+
+import numpy as np
+
+from .batchmath import row_sums
+from .plan_step import PLAN_STEP_MINUTES
+from .thermal_model import MIN_RUNNING_DRAW_KW
+
+#: The shortest single-duty share of a both step; a shorter share goes to
+#: the other duty for the whole step (valve travel and compressor cycling).
+SPLIT_MIN_MINUTES = 5.0
+
+#: Leg codes of :func:`leg_ends`.
+IDLE, SPACE, DHW = 0, 1, 2
+
+
+def both_step_legs(
+    space_kw: float, dhw_kw: float, step_minutes: float = PLAN_STEP_MINUTES
+) -> tuple[tuple[str, float], ...]:
+    """The legs of a step both circuits run in, in order, each with its minutes.
+
+    Hot water's share is the step's hot-water power over its total (tvofi,
+    2026-09-27); a share under :data:`SPLIT_MIN_MINUTES` on either side
+    collapses the step onto the other duty. Hot water goes first.
+    """
+    dhw_min = step_minutes * dhw_kw / (space_kw + dhw_kw)
+    if dhw_min < SPLIT_MIN_MINUTES:
+        return (("space", step_minutes),)
+    if step_minutes - dhw_min < SPLIT_MIN_MINUTES:
+        return (("dhw", step_minutes),)
+    return (("dhw", dhw_min), ("space", step_minutes - dhw_min))
+
+
+def _runs(kw: np.ndarray, floor: float | None) -> np.ndarray:
+    """``planned_draw_runs`` for one circuit, elementwise (pinned equal by test)."""
+    on = kw > MIN_RUNNING_DRAW_KW
+    return on if floor is None else on & ~(kw < floor)
+
+
+def leg_ends(
+    space_kw: Any,
+    dhw_kw: Any,
+    floor: float | None = None,
+    step_minutes: float = PLAN_STEP_MINUTES,
+) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
+    """Per step: the first leg, the last leg, and whether the step has two.
+
+    The arbiter's rule elementwise: ``step_duty`` reads each circuit alone
+    against the plan's ``floor``, and a both step splits by
+    :func:`both_step_legs`. ``space_kw`` may be a ``[B, n]`` batch against one
+    ``[n]`` hot-water plan.
+    """
+    space = np.asarray(space_kw, dtype=float)
+    dhw = np.asarray(dhw_kw, dtype=float)
+    s_on, d_on = _runs(space, floor), _runs(dhw, floor)
+    both = s_on & d_on
+    dhw_min = step_minutes * dhw / np.where(both, space + dhw, 1.0)
+    to_space = both & (dhw_min < SPLIT_MIN_MINUTES)
+    to_dhw = both & ~to_space & (step_minutes - dhw_min < SPLIT_MIN_MINUTES)
+    two = both & ~to_space & ~to_dhw
+    single = np.where(
+        (s_on & ~d_on) | to_space, SPACE, np.where((d_on & ~s_on) | to_dhw, DHW, IDLE)
+    )
+    return np.where(two, DHW, single), np.where(two, SPACE, single), two
+
+
+def priced_pair(values: Any, upper: float = math.inf) -> tuple[float, float]:
+    """A per-direction pair as two floats in ``[0, upper]``, else zero."""
+    try:
+        pair = [float(v) for v in values]
+    except (TypeError, ValueError):
+        return 0.0, 0.0
+    if len(pair) != 2:
+        return 0.0, 0.0
+    a, b = (max(v, 0.0) if math.isfinite(v) and v <= upper else 0.0 for v in pair)
+    return a, b
+
+
+#: A boundary pairs each step but the last with the step after it; the legs
+#: that meet there and the levels they run at are read through the same pair.
+_BEFORE, _AFTER = np.s_[:, :-1], np.s_[:, 1:]
+
+
+def switch_weights_batch(
+    space_matrix: np.ndarray,
+    dhw_kw: np.ndarray,
+    stop_probability: tuple[float, float],
+    p_max: float,
+    floor: float | None = None,
+) -> np.ndarray:
+    """Expected compressor stops at duty switches, in cycles, per row of plans.
+
+    Every pair of consecutive legs of different duty with no idle step
+    between weighs ``p * level / p_max``: inside a two-leg step both legs run
+    at the step's combined level; across a boundary the stop adds the smaller
+    of the two levels. ``row_sums`` reduces each row on its own, so a row is
+    :func:`switch_weight` of that plan bit for bit.
+    """
+    space = np.asarray(space_matrix, dtype=float)
+    p_ds, p_sd = stop_probability
+    if p_max <= 0:
+        return np.zeros(space.shape[0])
+    first, last, two = leg_ends(space, dhw_kw, floor)
+    level = space + np.asarray(dhw_kw, dtype=float)
+    before, after = last[_BEFORE], first[_AFTER]
+    stops = np.where(
+        (before == DHW) & (after == SPACE),
+        p_ds,
+        np.where((before == SPACE) & (after == DHW), p_sd, 0.0),
+    )
+    across = stops * np.minimum(level[_BEFORE], level[_AFTER])
+    inside = np.where(two, p_ds * level, 0.0)
+    return row_sums(np.concatenate([inside, across], axis=1)) / p_max
+
+
+def switch_weight(
+    space_kw: np.ndarray,
+    dhw_kw: np.ndarray,
+    stop_probability: tuple[float, float],
+    p_max: float,
+    floor: float | None = None,
+) -> float:
+    """The one-row case of :func:`switch_weights_batch`."""
+    return float(switch_weights_batch(
+        np.asarray(space_kw, dtype=float)[None, :], dhw_kw, stop_probability, p_max, floor
+    )[0])
+
+
+def lost_share(
+    stop_probability: tuple[float, float],
+    off_seconds: tuple[float, float],
+    step_minutes: float = PLAN_STEP_MINUTES,
+) -> float:
+    """The share of one step a hot-water to heating stop keeps the compressor off.
+
+    Only that direction carries lost time: its stop shortens the heating leg
+    that follows, and no install has measured an off time the other way.
+    """
+    return min(1.0, stop_probability[0] * off_seconds[0] / (step_minutes * 60.0))
+
+
+def availability(
+    space_start_kw: np.ndarray,
+    dhw_kw: np.ndarray,
+    lost: float,
+    floor: float | None = None,
+) -> np.ndarray | None:
+    """Per step, the share of it the compressor can run after a priced stop.
+
+    One step is charged per hot-water block end: the step holding the heating
+    leg that follows the hot-water leg in ``space_start_kw``, the profile the
+    solve starts from, because which step that is is the solve's own variable.
+    ``None`` when nothing is charged, so the caller makes today's calls on
+    today's arrays instead of multiplying by ones.
+    """
+    if not lost > 0:
+        return None
+    first, last, two = leg_ends(space_start_kw, dhw_kw, floor)
+    charged = two.copy()
+    charged[1:] |= (last[:-1] == DHW) & (first[1:] == SPACE)
+    if not charged.any():
+        return None
+    return np.where(charged, 1.0 - lost, 1.0)
+
+
+def space_headroom(
+    p_max: float, dhw_kw: np.ndarray, avail: np.ndarray | None, floor: float | None
+) -> np.ndarray:
+    """The space draw a hot-water plan leaves, less a stop's lost running time.
+
+    On a duty-cycle install (no ``floor``) a schedule value is a step average
+    and the stop is part of the off time, so the bound carries it. On a
+    clamped install a value is the level the compressor runs at and the bound
+    is today's; :func:`delivered_space` carries the lost time there.
+    """
+    if avail is None or floor is not None:
+        return np.maximum(0.0, p_max - dhw_kw)
+    charged: np.ndarray = np.maximum(0.0, avail * p_max - dhw_kw)
+    return charged
+
+
+def delivered_space(
+    space_kw: np.ndarray, dhw_kw: np.ndarray, avail: np.ndarray, floor: float | None
+) -> np.ndarray:
+    """The step average the house receives from a shipped space level.
+
+    On a clamped install the compressor is off for ``1 - avail`` of a step it
+    runs at level ``space + dhw``, and hot water keeps the level its planner
+    booked. On a duty-cycle install the shipped draw is already the average.
+    """
+    if floor is None:
+        return space_kw
+    delivered: np.ndarray = np.maximum(0.0, space_kw - (1.0 - avail) * (space_kw + dhw_kw))
+    return delivered
+
+
+def switch_ban(
+    space_kw: np.ndarray, stop_probability: tuple[float, float], floor: float | None
+) -> np.ndarray:
+    """The steps hot water may not be placed on to avoid a priced switch.
+
+    For hot water to heating: where heating runs in that step or the next, so
+    a block can only end into a planned stop or into more hot water. For
+    heating to hot water it mirrors onto the previous step.
+    """
+    on = _runs(np.asarray(space_kw, dtype=float), floor)
+    ban = np.zeros(on.shape, dtype=bool)
+    if stop_probability[0] > 0:
+        ban |= on
+        ban[:-1] |= on[1:]
+    if stop_probability[1] > 0:
+        ban |= on
+        ban[1:] |= on[:-1]
+    return ban
diff --git a/custom_components/heatpump_optimizer/duty_switch.py b/custom_components/heatpump_optimizer/duty_switch.py
index 802bfc8624..2beb1c35b7 100644
--- a/custom_components/heatpump_optimizer/duty_switch.py
+++ b/custom_components/heatpump_optimizer/duty_switch.py
@@ -4,9 +4,10 @@ Design: ``docs/design/2026-11-10-duty-switch-restart-learning/design.md``,
 part A. On some pumps a mode write from hot water to heating while the
 compressor runs stops it: the controller judges the heating request on a
 return the hot-water leg has just heated. Whether it does, and for how long
-the pump then stays off, is learned per install and per direction. **Nothing
-reads the estimate to change a plan or a write**; it is recorded, persisted
-and published on the compressor-starts sensor.
+the pump then stays off, is learned per install and per direction. It is
+recorded, persisted and published on the compressor-starts sensor, and a
+latched direction is read by the planner (:func:`planner_fields`), which
+prices the switch through ``duty_legs``. No write reads it.
 
 **Observe** (:class:`DutySwitchLearner`, no Home Assistant object). An
 episode opens at a landed mode write between the two single duties while the
@@ -33,6 +34,9 @@ weigh under five, and a sixth latches), spanning :data:`SPAN_DAYS_ON` days with
 the evidence that still weighs: under :data:`SPAN_FLOOR_N` the days are
 forgotten with it. Every threshold
 here is a named constant from one day on one install, not a measurement.
+``n`` is held at :data:`N_CAP` by scaling both counts alike at a booking, so
+evidence from before a firmware change is outvoted in a bounded number of
+episodes and an install that stops switching unlatches in a bounded time.
 """
 from __future__ import annotations
 
@@ -69,6 +73,11 @@ HEATED_MARGIN_K = 2.0
 SOURCE_LEG_MIN_S = 60.0
 HALF_LIFE_DAYS = 14.0
 N_ON, N_OFF = 5.0, 2.5
+#: The most decayed episodes a direction holds, twice the on-threshold. With
+#: every later episode kept, ``p`` falls from 1 by 10/11 per booking and is
+#: under :data:`P_OFF` at the thirteenth; with none, ``n`` is under
+#: :data:`N_OFF` just past two half-lives.
+N_CAP = 2.0 * N_ON
 P_ON, P_OFF = 0.5, 0.3
 SPAN_DAYS_ON = 2
 #: Decayed episodes under which a direction's days span nothing any more: one
@@ -213,6 +222,9 @@ class Direction:
                 self.censored += 1
             else:
                 self.off_s = [*self.off_s, off_s][-OFF_SAMPLES_MAX:]
+        if self.n > N_CAP:
+            scale = N_CAP / self.n
+            self.k, self.kept_w = self.k * scale, self.kept_w * scale
         self._latch()
 
     def stored_row(self) -> dict[str, Any]:
@@ -373,6 +385,14 @@ class DutySwitchLearner:
             out.update({f"duty_switch_{name}_{key}": value for key, value in row.items() if value is not None})
         return out
 
+    def planner_pairs(self) -> tuple[tuple[float, float], tuple[float, float]]:
+        """Per direction, in :data:`DIRECTIONS`' order: the stop probability
+        and the median off seconds the planner prices a switch by. Zeros
+        unless the direction's latch is on, and no off time while every
+        stop's was censored."""
+        read = [d if d.usable else Direction() for d in map(self.directions.__getitem__, DIRECTIONS)]
+        return (read[0].p, read[1].p), (read[0].median_off_s or 0.0, read[1].median_off_s or 0.0)
+
     def stored_record(self) -> dict[str, Any]:
         return {"directions": {name: d.stored_row() for name, d in self.directions.items()}}
 
@@ -503,3 +523,10 @@ def starts_attributes(coord: Any) -> dict[str, float]:
     """The compressor-starts sensor's duty-switch attributes; a pump never arbitrated reads empty."""
     rec = _RECORDS.get(coord)
     return (rec.learner if rec is not None else DutySwitchLearner()).published(dt_util.now())
+
+
+def planner_fields(coord: Any) -> dict[str, tuple[float, float]]:
+    """The ``OptimizationConfig`` fields a solve prices a duty switch by; a pump never arbitrated reads zeros."""
+    rec = _RECORDS.get(coord)
+    stops, off_s = (rec.learner if rec is not None else DutySwitchLearner()).planner_pairs()
+    return {"duty_switch_stop_probability": stops, "duty_switch_off_seconds": off_s}
diff --git a/custom_components/heatpump_optimizer/entry_config.py b/custom_components/heatpump_optimizer/entry_config.py
index 3643712fbc..c240553f20 100644
--- a/custom_components/heatpump_optimizer/entry_config.py
+++ b/custom_components/heatpump_optimizer/entry_config.py
@@ -94,6 +94,7 @@ class EntryConfig(Mapping[str, Any]):
     compressor_freq_entity: str | None = _entity_slot()
     compressor_freq_sensor: str | None = _entity_slot()
     dhw_disinfection_switch_entity: str | None = _entity_slot()
+    dhw_hysteresis_entity: str | None = _entity_slot()
     dhw_inlet_entity: str | None = _entity_slot()
     dhw_setpoint_entity: str | None = _entity_slot()
     dhw_temp_entity: str | None = _entity_slot()
@@ -115,6 +116,7 @@ class EntryConfig(Mapping[str, Any]):
     pv_export_price_entity: str | None = _entity_slot()
     pv_production_entity: str | None = _entity_slot()
     space_circulation_pump_entity: str | None = _entity_slot()
+    space_hysteresis_entity: str | None = _entity_slot()
     space_setpoint_entity: str | None = _entity_slot()
     vvc_pump_entity: str | None = _entity_slot()
     weather_entity: str | None = _entity_slot()
diff --git a/custom_components/heatpump_optimizer/inputs.py b/custom_components/heatpump_optimizer/inputs.py
index e201b73377..4ad3a0d256 100644
--- a/custom_components/heatpump_optimizer/inputs.py
+++ b/custom_components/heatpump_optimizer/inputs.py
@@ -41,7 +41,7 @@ import math
 import time
 from dataclasses import dataclass, field
 from datetime import datetime, timedelta
-from collections.abc import Callable, Collection
+from collections.abc import Callable, Collection, Mapping
 from typing import Any, Literal, NamedTuple
 from weakref import WeakKeyDictionary
 
@@ -60,6 +60,7 @@ from .const import (
     TEMPERATURE_UNIT_TO_C,
 )
 from .const import finite_float
+from .entry_config import EntryConfig
 from .log_latch import log_held
 from .payload import InputProblem
 
@@ -509,6 +510,50 @@ def read_setpoint(hass: Any, entity_id: str | None) -> float | None:
     return None if reading is None else reading[0]
 
 
+#: The widest temperature difference :func:`read_temperature_delta_k` reads
+#: as one, K: a larger number is a wrong entity (a tank probe, a set-point),
+#: which as a start hysteresis would bar every planned charge.
+TEMPERATURE_DELTA_MAX_K = 20.0
+
+
+def read_temperature_delta_k(hass: Any, entity_id: str | None) -> float | None:
+    """A temperature *difference* in K (a hysteresis), or ``None`` unread.
+
+    The unit's scale without its zero: K and °C stand as they are and °F is
+    scaled by 5/9, where the absolute readers (:func:`normalize_temperature_c`)
+    would read 2 K as -271 °C. A state with no unit is taken as K; a unit
+    outside the temperature family, a non-number, or a value outside 0 to
+    :data:`TEMPERATURE_DELTA_MAX_K` is no reading.
+    """
+    state = hass.states.get(entity_id) if entity_id else None
+    value = finite_float(getattr(state, "state", None))
+    unit = str(state_unit(state) or "").strip()
+    scale = (TEMPERATURE_UNIT_TO_C.get(unit) or (None, None))[1] if unit else 1.0
+    if value is None or scale is None:
+        return None
+    delta_k = value * scale
+    return delta_k if 0.0 <= delta_k <= TEMPERATURE_DELTA_MAX_K else None
+
+
+def read_start_hysteresis(state: Any, hass: Any, config: Mapping[str, Any]) -> None:
+    """Put the pump's own start hysteresis per duty, K, on ``state``.
+
+    ``state`` is the cycle's ``ThermalState`` and ``config`` the entry's
+    effective options: ``dhw_start_hysteresis_k`` and
+    ``space_start_hysteresis_k`` take what ``dhw_hysteresis_entity`` and
+    ``space_hysteresis_entity`` read (:func:`read_temperature_delta_k`), and
+    ``None`` for an option left empty or an entity that does not read, so a
+    reading that goes away stops binding the plan the same cycle.
+    ``dhw_setpoint_grid`` takes the grid a hot-water target is written on
+    (:func:`setpoint_grid`), so the plan judges a charge against the target
+    the pump is handed.
+    """
+    cfg = EntryConfig.from_mapping(config)
+    state.dhw_setpoint_grid = setpoint_grid(hass, cfg.dhw_setpoint_entity)
+    state.dhw_start_hysteresis_k = read_temperature_delta_k(hass, cfg.dhw_hysteresis_entity)
+    state.space_start_hysteresis_k = read_temperature_delta_k(hass, cfg.space_hysteresis_entity)
+
+
 def setpoint_range_c(hass: Any, entity_id: str | None) -> tuple[float | None, float | None]:
     """The set-point entity's own (min, max) in degC, ``None`` where it states none.
 
@@ -565,6 +610,88 @@ def _setpoint_unit_of(hass: Any, entity_id: str) -> Any:
     )
 
 
+class SetpointGrid(NamedTuple):
+    """What a write to one set-point entity lands on: its unit, step and range.
+
+    Plain values, so a reader with no ``hass`` (the plan, through
+    ``ThermalState.dhw_setpoint_grid``) puts a target on the same step the
+    write does.
+    """
+
+    unit: Any
+    step: float
+    low_c: float | None
+    high_c: float | None
+
+    def on_step(
+        self,
+        value_c: float,
+        *,
+        rounding: str = "nearest",
+        lo_c: float | None = None,
+        hi_c: float | None = None,
+    ) -> float:
+        """``value_c`` on the entity's step, in its own unit, returned in degC.
+
+        ``rounding`` is ``nearest``, ``up`` or ``down``; ``lo_c`` rounds up and
+        ``hi_c`` down, and the result stays between them, so a caller keeps a
+        floor above its gate and a ceiling inside its configured maximum while
+        the levels between round to nearest, monotone in the value. The step is
+        the entity's own (``setpoint_step``) in the unit the write uses
+        (#2285), so a Fahrenheit entity is quantised in Fahrenheit.
+        """
+        out = _on_step(temperature_from_c(value_c, self.unit), self.step, rounding)
+        if lo_c is not None:
+            out = max(out, _on_step(temperature_from_c(lo_c, self.unit), self.step, "up"))
+        if hi_c is not None:
+            out = min(out, _on_step(temperature_from_c(hi_c, self.unit), self.step, "down"))
+        converted = temperature_c(out, self.unit)
+        return out if converted is None else converted
+
+    def bounded(
+        self,
+        value: float,
+        floor: float = -1e9,
+        *,
+        rounding: str = "nearest",
+        lo: float | None = None,
+        hi: float | None = None,
+    ) -> float:
+        """``value`` (degC) inside the entity's own range, on its step.
+
+        ``rounding`` for the value itself, ``lo`` (a heating floor) up and
+        ``hi`` (a ceiling) down, the entity's own minimum up and maximum down.
+        """
+        low, high = self.low_c, self.high_c
+        value = max(value, floor, low if low is not None else floor)
+        lows = [v for v in (lo, low) if v is not None]
+        highs = [high] if high is not None else []
+        # The entity's range outranks a caller's ceiling: a write under its
+        # minimum on the step is refused, so a ceiling below that is dropped and
+        # the minimum, rounded up onto the step, holds.
+        if hi is not None and (low is None or hi >= self.on_step(low, rounding="up")):
+            highs.append(hi)
+        return self.on_step(
+            value, rounding=rounding,
+            lo_c=max(lows) if lows else None, hi_c=min(highs) if highs else None,
+        )
+
+
+def _grid_of(hass: Any, entity_id: str) -> SetpointGrid:
+    return SetpointGrid(
+        _setpoint_unit_of(hass, entity_id), setpoint_step(hass, entity_id),
+        *setpoint_range_c(hass, entity_id),
+    )
+
+
+def setpoint_grid(hass: Any, entity_id: str | None) -> SetpointGrid | None:
+    """The grid a write to ``entity_id`` lands on; ``None`` for no entity or
+    one with no state, which nothing is written to."""
+    if not entity_id or hass.states.get(entity_id) is None:
+        return None
+    return _grid_of(hass, entity_id)
+
+
 def quantise_setpoint_c(
     hass: Any,
     entity_id: str,
@@ -574,24 +701,8 @@ def quantise_setpoint_c(
     lo_c: float | None = None,
     hi_c: float | None = None,
 ) -> float:
-    """``value_c`` on the entity's step, in its own unit, returned in degC.
-
-    ``rounding`` is ``nearest``, ``up`` or ``down``; ``lo_c`` rounds up and
-    ``hi_c`` down, and the result stays between them, so a caller keeps a
-    floor above its gate and a ceiling inside its configured maximum while
-    the levels between round to nearest, monotone in the value. The step is
-    the entity's own (``setpoint_step``) in the unit the write uses
-    (#2285), so a Fahrenheit entity is quantised in Fahrenheit.
-    """
-    unit = _setpoint_unit_of(hass, entity_id)
-    step = setpoint_step(hass, entity_id)
-    out = _on_step(temperature_from_c(value_c, unit), step, rounding)
-    if lo_c is not None:
-        out = max(out, _on_step(temperature_from_c(lo_c, unit), step, "up"))
-    if hi_c is not None:
-        out = min(out, _on_step(temperature_from_c(hi_c, unit), step, "down"))
-    converted = temperature_c(out, unit)
-    return out if converted is None else converted
+    """``value_c`` on the entity's step (:meth:`SetpointGrid.on_step`), degC."""
+    return _grid_of(hass, entity_id).on_step(value_c, rounding=rounding, lo_c=lo_c, hi_c=hi_c)
 
 
 async def write_setpoint(hass: Any, entity_id: str, value: float) -> bool:
diff --git a/custom_components/heatpump_optimizer/optimizer.py b/custom_components/heatpump_optimizer/optimizer.py
index 45f71299ac..a7bb65b82e 100644
--- a/custom_components/heatpump_optimizer/optimizer.py
+++ b/custom_components/heatpump_optimizer/optimizer.py
@@ -111,6 +111,7 @@ from .thermal_model import (
     project_space_against,
     valve_charge_demand,
     valve_hold_temperature,
+    valve_top_draw,
     weather_or_calm,
     power_for_heat_per_cop_kw,
     added_power_for_heat_per_cop_kw,
@@ -128,6 +129,7 @@ from .tariff import (
     window_factors,
 )
 from .dhw_schedule import format_resolved_day_spec
+from . import duty_legs
 
 _LOGGER = logging.getLogger(__name__)
 
@@ -192,6 +194,215 @@ def _scores_rounded(opt: HeatPumpOptimizer) -> bool:
     return opt.config.clamp_planned_levels and not opt._levels_relaxed
 
 
+def _priced_stops(opt: HeatPumpOptimizer) -> tuple[float, float] | None:
+    """The learned stop probability per switch direction, ``None`` when no direction stops.
+
+    The lost running time is charged on this alone; the price is this times
+    ``cycling_cost``, so an install that prices no cycle prices no switch.
+    """
+    stops = duty_legs.priced_pair(opt.config.duty_switch_stop_probability, 1.0)
+    return stops if max(stops) > 0 else None
+
+
+def _stop_availability(
+    opt: HeatPumpOptimizer, start: np.ndarray, dhw_plan: np.ndarray, p_max: float
+) -> np.ndarray | None:
+    """The running share a priced stop leaves each step of the profile a solve starts from.
+
+    Read on the levels that profile ships, so the charged step holds a
+    heating leg the arbiter serves. ``None`` unless a stop with a measured off
+    time is priced: the caller then makes today's calls.
+    """
+    stops = _priced_stops(opt)
+    if stops is None:
+        return None
+    lost = duty_legs.lost_share(
+        stops, duty_legs.priced_pair(opt.config.duty_switch_off_seconds)
+    )
+    space, tank = _realize_joint(
+        opt.config.clamp_planned_levels,
+        np.minimum(start, np.maximum(0.0, p_max - dhw_plan)),
+        dhw_plan, opt.model.params.min_electrical_power, p_max,
+    )
+    return duty_legs.availability(space, tank, lost, _duty_floor(opt))
+
+
+def _with_stop_availability(
+    opt: HeatPumpOptimizer,
+    start: np.ndarray,
+    dhw_plan: np.ndarray,
+    p_max: float,
+    objective: Callable[..., float],
+    objective_batch: Callable[..., np.ndarray],
+) -> tuple[np.ndarray, Callable[..., float], Callable[..., np.ndarray]]:
+    """What a priced stop changes about one space solve: its bound and its objectives.
+
+    The heat pump serves one circuit at a time, so a DHW block eats into the
+    capacity available for space heating during that step, and a stop after
+    it into the step that follows. The availability vector is constant for
+    the solve and is kept on the optimizer beside the requirement, so the
+    plan that is adopted publishes with the vector it was scored with. With
+    none, the bound is ``p_max - dhw`` and the objectives the ones handed in.
+    """
+    avail = opt._space_avail = _stop_availability(opt, start, dhw_plan, p_max)
+    headroom = duty_legs.space_headroom(p_max, dhw_plan, avail, _duty_floor(opt))
+    if avail is None:
+        return headroom, objective, objective_batch
+    return headroom, partial(objective, avail=avail), partial(objective_batch, avail=avail)
+
+
+def _shipped_and_received(
+    opt: HeatPumpOptimizer,
+    space: np.ndarray,
+    dhw: np.ndarray | None,
+    avail: np.ndarray | None,
+) -> tuple[np.ndarray, np.ndarray | None, np.ndarray]:
+    """The level each circuit ships at, and the space draw the house receives.
+
+    The two differ only where a priced stop keeps the compressor off for part
+    of a step (``duty_legs.delivered_space``); with no availability vector the
+    received draw is the shipped array itself, the same object. A relaxed
+    start of a clamped install gets the clamped reading on its unrounded
+    level: the stop is the install's, whatever the rounding.
+    """
+    space, dhw = _realize_draw(
+        _scores_rounded(opt), space, dhw,
+        opt.model.params.min_electrical_power, opt.model.params.max_electrical_power,
+    )
+    if avail is None or dhw is None:
+        return space, dhw, space
+    return space, dhw, duty_legs.delivered_space(space, dhw, avail, _duty_floor(opt))
+
+
+def _switch_cost_fn(
+    opt: HeatPumpOptimizer,
+) -> Callable[[np.ndarray, np.ndarray | None], Any]:
+    """The duty-switch term of shipped plans, beside the cycling term.
+
+    One entry per row of a ``[B, n]`` batch, a float for one plan: the
+    one-row case of the same reduction, so the two agree bit for bit.
+    ``None`` when no direction is priced or there is no hot-water plan, and
+    :func:`_with_switch_cost` then adds no operand at all.
+    """
+    stops, floor = _priced_stops(opt), _duty_floor(opt)
+    p_max, cost = opt.model.params.max_electrical_power, opt.config.cycling_cost
+
+    def switch_cost(space: np.ndarray, dhw: np.ndarray | None) -> Any:
+        if stops is None or dhw is None or not cost > 0:
+            return None
+        term = cost * duty_legs.switch_weights_batch(
+            np.atleast_2d(space), dhw, stops, p_max, floor)
+        return term if np.ndim(space) == 2 else float(term[0])
+
+    return switch_cost
+
+
+def _with_switch_cost(level_cost: Any, switch_cost: Any) -> Any:
+    """The cycling and capacity terms plus the duty-switch term, when there is one."""
+    return level_cost if switch_cost is None else level_cost + switch_cost
+
+
+def _dhw_build(
+    planner: DhwPlanner, h: _Horizon, p_max: float, **extra: Any
+) -> tuple[Any, np.ndarray]:
+    """One hot-water build, with what every pass of a solve hands the planner.
+
+    The block honours an external ceiling through one scalar, the horizon's
+    minimum -- the same conservative, never-over-the-line approximation the
+    fuse guard's cap already makes. A quiet silent window's cap therefore
+    bounds every block the same way (#1910); its OFF steps are per-step,
+    through the forced-off door where the energy is re-bought elsewhere. The
+    mode's block rides every build (#1747): a replan without it plans hot
+    water the mode cannot make, and masks the breach.
+    """
+    return planner._build_dhw_requirements(
+        h,
+        p_max=p_max,
+        p_run_cap=(
+            float(np.min(h.power_caps_extra))
+            if h.power_caps_extra is not None
+            else None
+        ),
+        blocked=h.dhw_blocked,
+        off_steps=h.off_steps,
+        **extra,
+    )
+
+
+def _avoid_priced_switches(
+    opt: HeatPumpOptimizer,
+    h: _Horizon,
+    planner: DhwPlanner,
+    solve_space: Callable[..., Any],
+    objective: Callable[..., float],
+    p_max: float,
+    incumbent: tuple[np.ndarray, np.ndarray, str],
+) -> tuple[np.ndarray, np.ndarray, str]:
+    """Try one hot-water plan placed where no priced switch follows it.
+
+    Where the block sits is combinatorial, so it is taken by candidate and
+    score, as ``_co_optimize`` takes its own: hot water is banned from the
+    steps whose heating would make the switch, and the plan is adopted only
+    if it scores lower on the same objective, keeps off every banned step a
+    manual pin does not force on, and holds its own requirement wherever the
+    incumbent holds its. A refused candidate leaves the incumbent's
+    requirement and availability in place. Not on a combi store, whose
+    hot-water plan is a feasibility repair and never a scored candidate.
+    """
+    space, dhw, _ = incumbent
+    stops = _priced_stops(opt)
+    if stops is None or not opt.config.cycling_cost > 0 or opt.model.params.dhw_store.combi:
+        return incumbent
+    floor = _duty_floor(opt)
+    shipped, tank = _realize_joint(
+        opt.config.clamp_planned_levels, space, dhw,
+        opt.model.params.min_electrical_power, p_max,
+    )
+    kept_avail, kept_requirement = opt._space_avail, opt._dhw_requirement
+    if kept_requirement is None or not duty_legs.switch_weight(shipped, tank, stops, p_max, floor) > 0:
+        return incumbent
+    try:
+        ban = duty_legs.switch_ban(shipped, stops, floor)
+        plan, requirement = _dhw_build(
+            planner, h, p_max,
+            wood_temps=planner._dhw_coil_wood_forecast(h), placement_ban=ban,
+        )
+        forced_on = (
+            np.zeros(ban.shape, dtype=bool) if h.dhw_pins is None
+            else np.nan_to_num(_padded(h.dhw_pins, ban.size)) >= 0.5
+        )
+
+        def first_short(
+            schedule: np.ndarray, floor_temps: np.ndarray, excused: set[int]
+        ) -> tuple[Any, int | None]:
+            """The planner's own tank walk and shortfall rule, past ``excused`` steps."""
+            temps, _, step = planner._dhw_shortfall(
+                temps_of.get(id(schedule)), schedule, h.initial_state.dhw_temperature,
+                h.outdoor_temps, plan.draw_rates, h.dt, h.humidity, floor_temps, excused,
+            )
+            temps_of[id(schedule)] = temps
+            return temps, step
+
+        # The steps the incumbent is itself short on excuse the candidate there.
+        temps_of: dict[int, Any] = {}
+        unheld: set[int] = set()
+        while (step := first_short(dhw, kept_requirement, unheld)[1]) is not None:
+            unheld.add(step)
+        if (
+            not np.any(plan.schedule[ban & ~forced_on] > 0)
+            and first_short(plan.schedule, requirement, unheld)[1] is None
+        ):
+            base = float(objective(space, dhw, None, kept_avail))
+            candidate_space, candidate_status, score = solve_space(plan.schedule, space)
+            if score < base - 1e-9:
+                opt._dhw_requirement = requirement
+                return candidate_space, plan.schedule, candidate_status
+    except Exception as err:  # noqa: BLE001 - a candidate is optional: the incumbent stands
+        _LOGGER.debug("Duty-switch candidate pass skipped: %s", err)
+    opt._space_avail = kept_avail
+    return incumbent
+
+
 def _relaxed_starts(
     opt: HeatPumpOptimizer,
     objective: Callable[..., float],
@@ -579,46 +790,77 @@ def _wood_covered_share(model: ThermalModel, state: ThermalState, reference_kwh:
     return min(1.0, usable_kwh_th / p.cop_nominal_floored / reference_kwh)
 
 
+def _held_zones(
+    model: ThermalModel, state: ThermalState, weather0: tuple[float, float, float, float],
+    temp: float,
+) -> ThermalState:
+    """``state`` with the zones at ``temp`` and the slab at the temperature that
+    delivers the floor's steady demand there -- the cascade's own slab target
+    with no pull-back."""
+    q_floor = _floor_demand_at_target(model, temp, *weather0)
+    return replace(
+        state,
+        room_temperature=temp,
+        upper_floor_temperature=temp,
+        lower_floor_temperature=temp,
+        slab_temperature=temp + max(0.0, q_floor) / model.params.slab_heat_transfer_floored,
+    )
+
+
+#: Bisection steps for the held zone temperature: 2**-40 of the
+#: outdoor-to-target span, far below any sensor's resolution.
+_HELD_BISECTIONS = 40
+
+
 def _thermostat_held_state(
     model: ThermalModel, state: ThermalState, weather: WeatherSeries, target: float
 ) -> ThermalState:
     """``state`` as a thermostat holding ``target`` all along would have it (#2255).
 
-    The zones at ``target`` and the slab at the temperature that delivers the
-    step's demand -- the cascade's own slab target with no pull-back -- so the
-    first step draws the steady holding power. Behind a valve its tank sits at
-    the temperature that delivers the need, whatever the plan left in the
-    measured one. Every other field stays as measured.
+    The zones at ``target`` (``_held_zones``), so the first step draws the
+    steady holding power. Behind a valve its tank sits at the temperature
+    that delivers the need, whatever the plan left in the measured one.
+    Where the reference cannot deliver that steady heat at ``target`` --
+    either bound its own step clips at (``_held_unreachable``) -- a
+    thermostat running all along has sagged to where it can: the zones sit
+    at the highest temperature the step can hold, an equilibrium, so the
+    booked steps draw no stored heat (R10-SAV-VALUATION-RESIDUE).
+    Every other field stays as measured.
     """
     if not len(weather.outdoor_temps):
         return state
     assert weather.wind_speeds is not None and weather.precipitation is not None
     assert weather.solar_radiation is not None
-    q_floor = _floor_demand_at_target(
-        model, target, float(weather.outdoor_temps[0]), float(weather.wind_speeds[0]),
-        float(weather.precipitation[0]), float(weather.solar_radiation[0]),
-    )
-    held = replace(
-        state,
-        room_temperature=target,
-        upper_floor_temperature=target,
-        lower_floor_temperature=target,
-        slab_temperature=target + max(0.0, q_floor) / model.params.slab_heat_transfer_floored,
-    )
+    outdoor, wind = float(weather.outdoor_temps[0]), float(weather.wind_speeds[0])
+    rain, solar = float(weather.precipitation[0]), float(weather.solar_radiation[0])
+    weather0 = (outdoor, wind, rain, solar)
+    humidity = None if weather.humidity is None else float(weather.humidity[0])
     p = model.params
-    if not mixing_valve.is_throttling(p.mixing_valve_mode):
-        return held
-    wind, rain = float(weather.wind_speeds[0]), float(weather.precipitation[0])
-    outdoor = float(weather.outdoor_temps[0])
+    valved = mixing_valve.is_throttling(p.mixing_valve_mode)
     zoned = _thermostat_demand_two_zone if p.two_zone_enabled else _thermostat_demand_single
-    need = zoned(
-        model, held, target, outdoor, wind, rain, float(weather.solar_radiation[0]),
-        0.25, p.slab_heat_transfer_floored,
-    )
-    held.buffer_tank_temperature = (
-        valve_hold_temperature(model, held, need, outdoor, wind, rain)
-        if need > 0.0 else held.buffer_tank_temperature
-    )
+
+    def need(h: ThermalState) -> float:
+        # Zones level at their own temperature: no pull-back, the steady need.
+        return zoned(model, h, h.room_temperature, *weather0, 0.25, p.slab_heat_transfer_floored)
+
+    def held_at(temp: float) -> ThermalState:
+        h = _held_zones(model, state, weather0, temp)
+        if valved and (h_need := need(h)) > 0.0:
+            h.buffer_tank_temperature = valve_hold_temperature(
+                model, h, h_need, outdoor, wind, rain)
+        return h
+
+    def unreachable(h: ThermalState) -> bool:
+        return _held_unreachable(model, h, need(h), weather0, humidity)
+
+    held = held_at(target)
+    if unreachable(held):
+        # Unreachable needs heat, so the outdoor is below the target: the span is ordered.
+        lo, hi = min(outdoor, target), target
+        for _ in range(_HELD_BISECTIONS):
+            mid = 0.5 * (lo + hi)
+            lo, hi = (lo, mid) if unreachable(held_at(mid)) else (mid, hi)
+        held = held_at(lo)
     if p.two_tank_modelled:
         # The reference has no wood: below every zone the valve takes nothing
         # from this side (``wood_share`` 0), so the step is the plain valve's.
@@ -626,6 +868,33 @@ def _thermostat_held_state(
     return held
 
 
+def _held_unreachable(
+    model: ThermalModel, held: ThermalState, need_kw: float,
+    weather0: tuple[float, float, float, float], humidity: float | None,
+) -> bool:
+    """Whether the reference's own step cannot deliver ``need_kw``, the held
+    zones' steady emitter need, from ``held``: every bound on the heat it
+    delivers (R10-SAV-VALUATION-RESIDUE).
+
+    Behind a valve, the curve's top draw (``valve_top_draw``): a hotter tank
+    reaches no emitter. On every install, the pump: the steady heat the
+    step makes (``_thermostat_demand``, the tank's standing loss on top)
+    needs a draw past ``max_electrical_power`` at the step's own COP
+    (``_reference_cop``, defrost and part-load included), where the step
+    clips. Nothing else bounds it: the wood side is off in the reference and
+    ``buffer_max_temp`` caps the curve's top.
+    """
+    p = model.params
+    outdoor, wind, rain, solar = weather0
+    if mixing_valve.is_throttling(p.mixing_valve_mode) and need_kw > valve_top_draw(
+            model, held, outdoor, wind, rain):
+        return True
+    made = _thermostat_demand(
+        model, held, held.room_temperature, *weather0, 0.25, p.slab_heat_transfer_floored)
+    cop = _reference_cop(model, held, outdoor, humidity)
+    return bool(power_for_heat_per_cop_kw(p, made / cop) > p.max_electrical_power)
+
+
 def _thermostat_demand_single(
     model: ThermalModel,
     state: ThermalState,
@@ -1457,11 +1726,8 @@ def _combi_flux_exchange(
             weather=_with_buffer_exo(weather, dhw_exo), dt_hours=h.dt,
             valve_targets=h.valve_targets, start_hour=float(h.step_hours[0]))[4]
         space_net = combi_space_net_kw(store, buffer_temps, dhw_exo, h.dt)
-        plan, opt._dhw_requirement = planner._build_dhw_requirements(
-            h, p_max=p_max, space_demand=space_power,
-            p_run_cap=None if h.power_caps_extra is None else float(np.min(h.power_caps_extra)),
-            blocked=h.dhw_blocked, off_steps=h.off_steps, tank_exo_kw=space_net,
-        )
+        plan, opt._dhw_requirement = _dhw_build(
+            planner, h, p_max, space_demand=space_power, tank_exo_kw=space_net)
         if np.allclose(plan.schedule, dhw_power, atol=1e-4):
             break
         dhw_power = plan.schedule
@@ -2142,6 +2408,12 @@ class OptimizationConfig:
     #: had silently drifted apart once before, which meant the tests were
     #: measuring a slightly different optimizer from the integration.
     cycling_cost: float = DEFAULT_CYCLING_COST
+    #: Per direction (hot water to heating, heating to hot water): the learned
+    #: probability that a duty switch stops the compressor, and the seconds it
+    #: then stays off. Zeros price nothing and leave every plan as it was;
+    #: ``duty_legs`` owns what they mean.
+    duty_switch_stop_probability: tuple[float, float] = (0.0, 0.0)
+    duty_switch_off_seconds: tuple[float, float] = (0.0, 0.0)
 
     # --- Capacity tariff (item 8) --------------------------------------
     #: Currency per kW of new monthly peak, already divided by the number of
@@ -2753,6 +3025,9 @@ class HeatPumpOptimizer:
         # loop: the tank temperature the plan must keep the DHW trajectory
         # above. Assigned at each build, so the last build of a solve wins.
         self._dhw_requirement: np.ndarray | None = None
+        #: The ``duty_legs.availability`` vector the last space solve scored
+        #: with, riding beside its plan; ``None`` when no stop is charged.
+        self._space_avail: np.ndarray | None = None
         #: The solve's starting buffer temperature; floors the settlement
         #: value cap so pre-stored heat cannot be drained for free.
         self._initial_buffer_temp: float | None = None
@@ -2907,9 +3182,8 @@ class HeatPumpOptimizer:
         traj: dict[str, np.ndarray],
         grid_power: np.ndarray,
         *,
+        level_cost: np.ndarray,
         energy_cost_of: Callable[[np.ndarray], Any],
-        cycling_batch: Callable[[np.ndarray], np.ndarray],
-        capacity_batch: Callable[[np.ndarray], np.ndarray],
         terminal_cost_batch: Callable[[dict[str, np.ndarray]], np.ndarray],
         comfort_targets: np.ndarray,
         temp_min_bounds: np.ndarray,
@@ -2930,6 +3204,8 @@ class HeatPumpOptimizer:
         path -- because the energy, cycling and capacity terms are
         properties of the combined draw, while the comfort and terminal
         terms read ``traj``, which the space schedule alone produces.
+        ``level_cost`` is what the caller priced on the shipped level, which
+        a priced stop makes differ from that draw: cycling, capacity, switches.
         """
         weight = self.config.price_weight
         penalty, comfort_cost = self._comfort_terms_batch(
@@ -2942,7 +3218,7 @@ class HeatPumpOptimizer:
             energy_cost_of(grid_power) * weight
             + penalty
             + comfort_cost
-            + (cycling_batch(grid_power) + capacity_batch(grid_power)) * weight
+            + level_cost * weight
             + terminal_cost_batch(traj)
         )
 
@@ -3345,7 +3621,8 @@ class HeatPumpOptimizer:
         it (``combi_space_net_kw``, R10-COMBI-TANK), the flux exchange.
         """
         try:
-            headroom = np.maximum(0.0, p_max - dhw_power)
+            headroom = duty_legs.space_headroom(
+                p_max, dhw_power, self._space_avail, _duty_floor(self))
             # Where space heating sits hard against the ceiling hot water left
             # it, it wanted more power than it could have; its unconstrained
             # demand there is at least the full compressor.
@@ -3364,30 +3641,22 @@ class HeatPumpOptimizer:
             if not bool(np.any(pinned)) and not coil_replan:
                 return space_power, dhw_power, status
 
-            replanned_plan, self._dhw_requirement = planner._build_dhw_requirements(
-                h,
-                p_max=p_max,
+            replanned_plan, self._dhw_requirement = _dhw_build(
+                planner, h, p_max,
                 space_demand=np.where(pinned, p_max, space_power),
-                p_run_cap=(
-                    float(np.min(h.power_caps_extra))
-                    if h.power_caps_extra is not None
-                    else None
-                ),
-                # The first build's block (#1747): a replan without it plans
-                # hot water the mode cannot make, and masks the breach.
-                blocked=h.dhw_blocked,
-                off_steps=h.off_steps,
                 wood_temps=wood_temps,
             )
             replanned = replanned_plan.schedule
             if np.allclose(replanned, dhw_power, atol=1e-4):
                 return space_power, dhw_power, status
 
+            kept_avail = self._space_avail
             candidate_space, candidate_status, score = solve_space(
                 replanned, space_power
             )
             if score < best_score - 1e-9:
                 return candidate_space, replanned, candidate_status
+            self._space_avail = kept_avail
         except Exception as err:  # pragma: no cover - defensive
             _LOGGER.debug("DHW/space co-optimization pass skipped: %s", err)
 
@@ -4367,9 +4636,9 @@ class HeatPumpOptimizer:
         objective_batch: Callable[..., np.ndarray],
     ) -> tuple[np.ndarray, str, float]:
         """Optimize space heating around a fixed DHW schedule."""
-        # The heat pump serves one circuit at a time, so a DHW block eats
-        # into the capacity available for space heating during that step.
-        headroom = np.maximum(0.0, p_max - dhw_plan)
+        guess = init_base if warm_start is None else warm_start
+        headroom, objective, objective_batch = _with_stop_availability(
+            self, guess, dhw_plan, p_max, objective, objective_batch)
         if h.power_caps is not None:
             headroom = np.minimum(headroom, h.power_caps)
         if h.power_caps_extra is not None:
@@ -4381,7 +4650,6 @@ class HeatPumpOptimizer:
                 headroom,
                 np.maximum(0.0, h.power_caps_extra - dhw_plan),
             )
-        guess = init_base if warm_start is None else warm_start
         guess = np.minimum(np.clip(guess, 0.0, p_max), headroom)
         bounds = [(0.0, float(headroom[i])) for i in range(n_steps)]
         # Manual space pins apply here just as in the DHW-free path. Forcing
@@ -4759,9 +5027,7 @@ class HeatPumpOptimizer:
         initial_state, prices, dt, comfort_targets = (
             h.initial_state, h.prices, h.dt, h.comfort_targets
         )
-        outdoor_temps, wind_speeds, precipitation, solar_radiation = (
-            h.outdoor_temps, h.wind_speeds, h.precipitation, h.solar_radiation
-        )
+        outdoor_temps = h.outdoor_temps
         weather = WeatherSeries.from_horizon(h)
         temp_min_bounds, temp_max_bounds = h.temp_min_bounds, h.temp_max_bounds
 
@@ -4777,6 +5043,7 @@ class HeatPumpOptimizer:
             self._grid_terms(h.n_steps, dt, h.start_time)
         )
         energy_cost_of = self._energy_cost_fn(prices, dt)
+        switch_cost = _switch_cost_fn(self)
 
         def _space_traj(power_schedule: np.ndarray, buffer_exo_kw: Any = None) -> Any:
             return self.model.simulate_trajectory(
@@ -4792,14 +5059,13 @@ class HeatPumpOptimizer:
             space_power: np.ndarray,
             dhw_plan_power: np.ndarray | None = None,
             buffer_exo_kw: np.ndarray | None = None,
+            avail: np.ndarray | None = None,
         ) -> float:
             """Compute the total cost with predictive weather anticipation."""
-            space_power, dhw_plan_power = _realize_draw(
-                _scores_rounded(self), space_power, dhw_plan_power,
-                self.model.params.min_electrical_power, self.model.params.max_electrical_power,
-            )
+            space_power, dhw_plan_power, heat_power = _shipped_and_received(
+                self, space_power, dhw_plan_power, avail)
             room_temps, slab_temps, upper_temps, lower_temps, buffer_temps, _, _ = (
-                _space_traj(space_power, buffer_exo_kw)
+                _space_traj(heat_power, buffer_exo_kw)
             )
 
             # The compressor is one machine: the grid sees the *combined*
@@ -4813,8 +5079,9 @@ class HeatPumpOptimizer:
 
             # Electricity cost, piecewise in PV surplus. ``float()`` is
             # identity on the 1-D branch's return and states it.
+            drawn = combined if heat_power is space_power else heat_power + dhw_plan_power
             energy_cost = (
-                float(energy_cost_of(combined)) * self.config.price_weight
+                float(energy_cost_of(drawn)) * self.config.price_weight
             )
 
             penalty, comfort_cost = self._comfort_terms(
@@ -4831,7 +5098,9 @@ class HeatPumpOptimizer:
                 # Currency terms scale with price_weight as the energy cost
                 # does, or a non-default weight silently re-prices starts and
                 # peaks relative to the electricity they trade against.
-                + (cycling(combined) + capacity(combined))
+                + float(_with_switch_cost(
+                    cycling(combined) + capacity(combined),
+                    switch_cost(space_power, dhw_plan_power)))
                 * self.config.price_weight
                 + terminal_cost(
                     room_temps,
@@ -4846,6 +5115,7 @@ class HeatPumpOptimizer:
             space_matrix: np.ndarray,
             dhw_plan_power: np.ndarray | None = None,
             buffer_exo_kw: np.ndarray | None = None,
+            avail: np.ndarray | None = None,
         ) -> np.ndarray:
             """The same objective, for B schedules at once (issue #97).
 
@@ -4857,13 +5127,11 @@ class HeatPumpOptimizer:
             asserted by test, because a divergence here would move plans
             silently.
             """
-            space_matrix, dhw_plan_power = _realize_draw(
-                _scores_rounded(self), space_matrix, dhw_plan_power,
-                self.model.params.min_electrical_power, self.model.params.max_electrical_power,
-            )
+            space_matrix, dhw_plan_power, heat_matrix = _shipped_and_received(
+                self, space_matrix, dhw_plan_power, avail)
             traj = self.model.simulate_trajectory_batch(
                 initial_state=initial_state,
-                power_matrix=space_matrix,
+                power_matrix=heat_matrix,
                 weather=_with_buffer_exo(weather, buffer_exo_kw),
                 dt_hours=dt,
                 valve_targets=h.valve_targets,
@@ -4875,10 +5143,12 @@ class HeatPumpOptimizer:
                 else space_matrix + dhw_plan_power
             )
             return self._cost_terms_batch(
-                traj, grid_power,
+                traj,
+                grid_power if heat_matrix is space_matrix else heat_matrix + dhw_plan_power,
+                level_cost=_with_switch_cost(
+                    cycling_batch(grid_power) + capacity_batch(grid_power),
+                    switch_cost(space_matrix, dhw_plan_power)),
                 energy_cost_of=energy_cost_of,
-                cycling_batch=cycling_batch,
-                capacity_batch=capacity_batch,
                 terminal_cost_batch=terminal_cost_batch,
                 comfort_targets=comfort_targets,
                 temp_min_bounds=temp_min_bounds,
@@ -5165,8 +5435,7 @@ class HeatPumpOptimizer:
         initial_state, prices, dt, n_steps = (
             h.initial_state, h.prices, h.dt, h.n_steps
         )
-        outdoor_temps, wind_speeds = h.outdoor_temps, h.wind_speeds
-        precipitation, solar_radiation = h.precipitation, h.solar_radiation
+        outdoor_temps = h.outdoor_temps
         weather = WeatherSeries.from_horizon(h)
         comfort_targets = h.comfort_targets
         step_hours, solar_gains_per_step = h.step_hours, h.solar_gains
@@ -5192,24 +5461,8 @@ class HeatPumpOptimizer:
         # hot water must be available; outside it there is no requirement, so
         # the only reason to run the pump is to be ready for the *next* window
         # — and the energy-cost term then decides *when* that happens.
-        dhw_plan, self._dhw_requirement = planner._build_dhw_requirements(
-            h,
-            p_max=p_max,
-            # The DHW block honours an external ceiling through this scalar,
-            # the horizon's minimum — the same conservative, never-over-the-
-            # line approximation the fuse guard's cap already makes here. A
-            # quiet silent window's cap therefore bounds every DHW block the
-            # same way (#1910); its OFF steps are per-step, below, through
-            # the forced-off door where the energy is re-bought elsewhere.
-            p_run_cap=(
-                float(np.min(h.power_caps_extra))
-                if h.power_caps_extra is not None
-                else None
-            ),
-            blocked=h.dhw_blocked,
-            off_steps=h.off_steps,
-            wood_temps=planner._dhw_coil_wood_forecast(h),
-        )
+        dhw_plan, self._dhw_requirement = _dhw_build(
+            planner, h, p_max, wood_temps=planner._dhw_coil_wood_forecast(h))
 
         dhw_floor_temps = dhw_plan.floor_temps
         dhw_ready_temps = dhw_plan.ready_temps
@@ -5286,10 +5539,18 @@ class HeatPumpOptimizer:
             planner=planner,
             draw_rates=dhw_draw_rates,
         )
+        optimal_space, optimal_dhw, status = _avoid_priced_switches(
+            self, h, planner, solve_space, objective, p_max,
+            (optimal_space, optimal_dhw, status),
+        )
         optimal_space, optimal_dhw = _realize_joint(
             self.config.clamp_planned_levels, optimal_space, optimal_dhw,
             p_min, p_max,
         )
+        # Received through the vector the adopted solve scored with, never a
+        # rebuilt one; the schedule and the achieved objective keep the level.
+        heat_space = optimal_space if self._space_avail is None else duty_legs.delivered_space(
+            optimal_space, optimal_dhw, self._space_avail, _duty_floor(self))
 
         # Simulate with optimal schedule
         published_end: list[ThermalState] = []
@@ -5303,7 +5564,7 @@ class HeatPumpOptimizer:
             wood_temps,
         ) = self.model.simulate_trajectory_with_dhw(
             initial_state=initial_state,
-            space_power_schedule=optimal_space,
+            space_power_schedule=heat_space,
             dhw_power_schedule=optimal_dhw,
             weather=WeatherSeries.from_horizon(h),
             start_hour=start_hour,
@@ -5319,6 +5580,7 @@ class HeatPumpOptimizer:
             combi_dhw_net_series(
                 self.model, buffer_temps, optimal_dhw, dhw_draw_rates, outdoor_temps, h.humidity)
             if self.model.params.dhw_store.combi else None,
+            self._space_avail,
         ))
 
         # Baseline cost. The reference holds the comfort schedule, not the comfort the plan
@@ -5329,7 +5591,7 @@ class HeatPumpOptimizer:
         baseline_dhw, baseline_cost, predicted_cost, dhw_cost = (
             planner._baseline_dhw_economics(
                 initial_state, outdoor_temps, n_steps, dhw_setpoint,
-                energy_cost_of, baseline_power, optimal_space, optimal_dhw, h.humidity,
+                energy_cost_of, baseline_power, heat_space, optimal_dhw, h.humidity,
             )
         )
 
diff --git a/custom_components/heatpump_optimizer/pump_arbiter.py b/custom_components/heatpump_optimizer/pump_arbiter.py
index 608b1efee1..e3afe6c67d 100644
--- a/custom_components/heatpump_optimizer/pump_arbiter.py
+++ b/custom_components/heatpump_optimizer/pump_arbiter.py
@@ -131,8 +131,10 @@ the planned duty against what the pump did, read from what the integration
 already reads -- the measured electrical draw (running or not), the mode
 select (DHW only) and the tank temperature (a rise of :data:`TANK_RISE_C`
 over the step is hot water). Each step is ``delivered``,
-``space-instead``, ``dhw-instead``, ``idle-instead``, ``unknown`` (no power
-meter and no tank rise) or ``baseline``. A concurrent Heating + DHW run
+``space-instead``, ``dhw-instead``, ``idle-instead``, ``not-startable`` (a
+hot-water step left idle on a tank at or above the pump's own start
+temperature, the step's target less ``dhw_hysteresis_entity``), ``unknown``
+(no power meter and no tank rise) or ``baseline``. A concurrent Heating + DHW run
 reads as hot water; a big draw can hide a tank rise. The last
 :func:`log_steps` steps and their counts are in the diagnostics; the ledger
 is not persisted. It is what decides whether control is worth turning on:
@@ -187,17 +189,21 @@ from .freq_control import defrost_interval, resolve_reading
 from .modbus_prefill import night_mode_write_ids, package_prefix
 from .const import finite_float
 from .inputs import (
-    InputReader, quantise_setpoint_c, read_setpoint, setpoint_range_c, state_power_kw, write_setpoint_c,
+    InputReader, SetpointGrid, quantise_setpoint_c, read_setpoint, setpoint_grid, setpoint_range_c, state_power_kw,
+    write_setpoint_c,
 )
 from .log_latch import log_held
 from .payload import REASON_LEGIONELLA, CurrentAction
 from .plan_step import PLAN_STEP_HOURS, PLAN_STEP_MINUTES, plan_step_start
 from .drift import utc_elapsed_seconds, utc_shift
+from .duty_legs import both_step_legs
 from .drift import stored_instant
 from .store import QuarantiningStore, load_mapping
 from .thermal_model import (
     configured_flow_heat_c,
-    configured_flow_min_lift_k,
+    dhw_start_below_c,
+    dhw_step_target_c,
+    start_flow_min_lift_k,
     FLOW_MIN_LIFT_K,
     flow_setpoint_driven,
     flow_setpoint_for_level,
@@ -245,9 +251,6 @@ ISSUE_MANUAL = "pump_manual_change"
 ISSUE_IGNORED = "pump_write_ignored"
 #: How long an ignored write waits before it is sent again.
 RETRY_MINUTES = 5.0
-#: The shortest single-duty share of a both step; a shorter share goes to
-#: the other duty for the whole step (valve travel and compressor cycling).
-SPLIT_MIN_MINUTES = 5.0
 TANK_RISE_C = 0.5
 _STORE_VERSION = 1
 
@@ -588,29 +591,17 @@ def _bounded(
     lo: float | None = None,
     hi: float | None = None,
 ) -> float | None:
-    """``value`` (degC) inside the slot entity's own range, on its step.
-
-    ``quantise_setpoint_c`` rounds it in the entity's unit: ``rounding``
-    for the value itself, ``lo`` (a heating floor) up and ``hi`` (a
-    ceiling) down, the entity's own minimum up and maximum down.
-    """
-    if value is None or _slot_state(inp, slot) is None:
+    """``value`` (degC) inside the slot entity's own range, on its step
+    (``inputs.SetpointGrid.bounded``); ``None`` for no value or no entity state."""
+    grid = _grid(inp, slot)
+    if value is None or grid is None:
         return None
-    entity = _entities(inp.config)[slot]
-    low, high = setpoint_range_c(inp.hass, entity)
-    value = max(value, floor, low if low is not None else floor)
-    value = min(value, high) if high is not None else value
-    lows = [v for v in (lo, low) if v is not None]
-    highs = [high] if high is not None else []
-    # The entity's range outranks a caller's ceiling: a write under its
-    # minimum on the step is refused, so a ceiling below that is dropped and
-    # the minimum, rounded up onto the step, holds.
-    if hi is not None and (low is None or hi >= quantise_setpoint_c(inp.hass, entity, low, rounding="up")):
-        highs.append(hi)
-    return quantise_setpoint_c(
-        inp.hass, entity, value, rounding=rounding,
-        lo_c=max(lows) if lows else None, hi_c=min(highs) if highs else None,
-    )
+    return grid.bounded(value, floor, rounding=rounding, lo=lo, hi=hi)
+
+
+def _grid(inp: ArbiterInputs, slot: str) -> SetpointGrid | None:
+    """The grid a write to the slot's entity lands on, ``None`` with none."""
+    return setpoint_grid(inp.hass, _entities(inp.config)[slot])
 
 
 def _planned_room(
@@ -879,7 +870,8 @@ def _flow_target(inp: ArbiterInputs, duty: str | None, now: datetime) -> float |
     2026-09-26). A step that heats writes a flow that follows the planned
     level: :data:`FLOW_HEAT_C` (or the configured ceiling, ``flow_heat_c``)
     at full power, sliding to the measured inlet plus a minimum lift
-    (``flow_min_lift_k``, else ``thermal_model.FLOW_MIN_LIFT_K``) at the
+    (``thermal_model.start_flow_min_lift_k``: ``flow_min_lift_k``, never
+    below the pump's own heating start hysteresis where one is read) at the
     modulation floor, so the pump's own water thermostat can realize a
     lower level.
     With no inlet reading the floor is the rated :data:`FLOW_HOLD_C`, in
@@ -895,7 +887,8 @@ def _flow_target(inp: ArbiterInputs, duty: str | None, now: datetime) -> float |
         p_min, p_max = _band_kw(inp)
         heat_c = _heat_ceiling_c(inp.config)
         floor_c = _or_hold(modulation_floor_flow_c(
-            _flow_inlet_c(inp), _gate_c(inp), configured_flow_min_lift_k(inp.config),
+            _flow_inlet_c(inp), _gate_c(inp),
+            start_flow_min_lift_k(inp.config, getattr(inp.state, "space_start_hysteresis_k", None)),
         ), inp.config)
         return _bounded(
             inp,
@@ -1186,26 +1179,22 @@ def _silent_target(coord: Any, inp: ArbiterInputs, now: datetime) -> bool | None
 def _dhw_write(inp: ArbiterInputs) -> float | None:
     """The hot-water set-point this step holds, °C on the entity's step.
 
-    A cycle runs while the plan's step books hot water for it (``dhw_reason``
-    legionella) or the integration holds the pump's disinfection switch on;
-    its temperature is the thermal parameters' (``dhw_cycle_temp``, the higher
-    of the everyday set-point and the disinfection temperature), on the
-    entity's step at or below the tank's hard maximum (``dhw_hard_max_temp``,
-    that temperature capped at 70 °C), which no write exceeds: an off-step
-    target is held a step below it (everyday 57, disinfection 50, step 5:
-    55, not 60). No cycle, the everyday set-point is written on the step
-    at or below the charge limit (``dhw_max_temp``): rounding it up would
-    hold the tank above the user's own limit for good (everyday 58, step 5:
-    55, not 60). Holding the everyday set-point through a cycle
-    stopped the pump's own thermostat short of the cycle's target (2026-11-01:
-    60 °C planned, 55 °C written back within a minute).
-    """
-    everyday = float(inp.params.dhw_setpoint)
-    booked = (inp.action or {}).get("dhw_reason") == REASON_LEGIONELLA
-    cycle = inp.params.dhw_cycle_temp if booked or inp.disinfecting else None
-    if cycle is None:
-        return _bounded(inp, "dhw_setpoint", everyday, hi=inp.params.dhw_max_temp)
-    return _bounded(inp, "dhw_setpoint", float(cycle), hi=inp.params.dhw_hard_max_temp)
+    The step's target (:func:`_dhw_target`); ``None`` with no entity state
+    to write it to.
+    """
+    return None if _grid(inp, "dhw_setpoint") is None else _dhw_target(inp)
+
+
+def _dhw_target(inp: ArbiterInputs) -> float:
+    """This step's hot-water target, °C (``thermal_model.dhw_step_target_c``).
+
+    A cycle step is one the plan books hot water on for the cycle
+    (``dhw_reason`` legionella) or one on which the integration holds the
+    pump's disinfection switch on; the target is on the set-point entity's
+    grid, or with no entity the one the step holds before any.
+    """
+    cycle = (inp.action or {}).get("dhw_reason") == REASON_LEGIONELLA or inp.disinfecting
+    return dhw_step_target_c(inp.params, cycle, _grid(inp, "dhw_setpoint"))
 
 
 def desired(coord: Any, inp: ArbiterInputs, duty: str | None, now: datetime) -> PumpCommand:
@@ -1688,6 +1677,7 @@ def _observe(held: ArbiterState, inp: ArbiterInputs, duty: str | None, now: date
             held.log.append(_verdict(row, tank))
         held.step = row = {"start": start, "planned": duty, "plan": inp.plan, "tank": tank,
                            "measured": False, "ran": False, "dhw_mode": False}
+        row["start_below"] = _dhw_start_below_c(inp)
     elif row["plan"] is not inp.plan:
         row["planned"], row["plan"] = duty, inp.plan
     power = inp.measured_power_kw
@@ -1698,6 +1688,33 @@ def _observe(held: ArbiterState, inp: ArbiterInputs, duty: str | None, now: date
     row["dhw_mode"] = row["dhw_mode"] or mode == pump_mode.MODE_DHW
 
 
+def _dhw_start_below_c(inp: ArbiterInputs) -> float | None:
+    """The tank temperature below which the pump starts this step's charge, °C.
+
+    The step's target (:func:`_dhw_target`) less the pump's hot-water start
+    hysteresis (``thermal_model.dhw_start_below_c``); ``None`` with none read.
+    """
+    hysteresis = getattr(inp.state, "dhw_start_hysteresis_k", None)
+    return None if hysteresis is None else dhw_start_below_c(_dhw_target(inp), hysteresis)
+
+
+def _not_startable(row: dict[str, Any]) -> bool:
+    """Whether the step's tank opened at or above the pump's start temperature.
+
+    Its own hysteresis then kept the pump off, so an idle hot-water step says
+    nothing about whether the pump obeys the plan (Bankaifan, #3440).
+    """
+    start, tank = row.get("start_below"), row["tank"]
+    return start is not None and tank is not None and float(tank) >= start
+
+
+def _missed(row: dict[str, Any], planned: str, actual: str) -> str:
+    """The verdict for a step that did something other than its plan."""
+    if planned == "dhw" and actual == "idle" and _not_startable(row):
+        return "not-startable"
+    return f"{actual}-instead"
+
+
 def _verdict(row: dict[str, Any], tank: Any) -> dict[str, Any]:
     """What the pump did over one step, against what the plan wanted."""
     rose = None not in (tank, row["tank"]) and float(tank) - float(row["tank"]) >= TANK_RISE_C
@@ -1714,7 +1731,7 @@ def _verdict(row: dict[str, Any], tank: Any) -> dict[str, Any]:
     elif actual == planned or (planned == "both" and actual != "idle"):
         verdict = "delivered"
     else:
-        verdict = f"{actual}-instead"
+        verdict = _missed(row, planned, actual)
     return {"start": row["start"].isoformat(), "planned": planned,
             "actual": actual, "verdict": verdict}
 
@@ -1807,13 +1824,11 @@ def _share(coord: Any, inp: ArbiterInputs, duty: str | None, now: datetime) -> s
         return duty
     result = inp.plan
     i = bisect.bisect_right(result.timestamps, now) - 1
-    space, dhw = result.power_schedule[i], result.dhw_power_schedule[i]
-    dhw_min = PLAN_STEP_MINUTES * dhw / (space + dhw)
-    if dhw_min < SPLIT_MIN_MINUTES:
-        return "space"
-    if PLAN_STEP_MINUTES - dhw_min < SPLIT_MIN_MINUTES:
-        return "dhw"
-    return "dhw" if (now - result.timestamps[i]) < timedelta(minutes=dhw_min) else "space"
+    legs = both_step_legs(
+        result.power_schedule[i], result.dhw_power_schedule[i], PLAN_STEP_MINUTES
+    )
+    first_ends = timedelta(minutes=legs[0][1])
+    return legs[0][0] if (now - result.timestamps[i]) < first_ends else legs[-1][0]
 
 
 def on_off_service(entity_id: str, on: bool) -> tuple[str, str]:
diff --git a/custom_components/heatpump_optimizer/setpoint_check.py b/custom_components/heatpump_optimizer/setpoint_check.py
index 7146b04c07..108b478f43 100644
--- a/custom_components/heatpump_optimizer/setpoint_check.py
+++ b/custom_components/heatpump_optimizer/setpoint_check.py
@@ -14,12 +14,15 @@ from .const import MIXING_VALVE_WRITE_EPSILON
 from .entry_config import EntryConfig
 from .issues import clear_issue, set_issue
 from .inputs import (
+    read_temperature_delta_k,
     quantise_setpoint_c,
     read_setpoint,
     setpoint_and_unit,
+    setpoint_grid,
     temperature_from_c,
 )
 from .quiet_windows import silent_unenforceable
+from .thermal_model import dhw_start_below_c, dhw_step_target_c
 
 _LOGGER = logging.getLogger(__name__)
 
@@ -29,6 +32,7 @@ ISSUE_SPACE = "space_setpoint_unreadable"
 #: them. A warning, not a fix -- the remedy is an assignment only the
 #: setup diagram (or SW-4's Modbus schedule) can make.
 ISSUE_QUIET = "quiet_silent_not_enforced"
+ISSUE_DHW_START = "dhw_minimum_above_start"
 
 
 class ConfigNotices:
@@ -90,10 +94,41 @@ def _evaluate(coord: Any, gated: Callable[[float], bool] | None) -> None:
     config = coord.effective_config
     params = coord.thermal_params
     _dhw(hass, config, params, gated)
+    _dhw_start(hass, config, params)
     _space(hass, config)
     _quiet(hass, config)
 
 
+def _dhw_start(hass: Any, config: dict[str, Any], params: Any) -> None:
+    """One warning when this pump cannot hold the hot-water minimum.
+
+    A pump with a start hysteresis (``dhw_hysteresis_entity``) starts a charge
+    only below its target less that (``thermal_model.dhw_start_below_c``, on
+    the everyday target as written, ``thermal_model.dhw_step_target_c`` on the
+    set-point entity's grid), and the plan places no charge it will not start.
+    A minimum above that start temperature is therefore one the tank must fall
+    through before any charge can begin: the plan shows the tank under it,
+    and this says why. Cleared with no hysteresis read, and with hot water
+    disabled (``dhw_enabled``): no charge is planned then and no minimum held.
+    """
+    cfg = EntryConfig.from_mapping(config)
+    hysteresis = read_temperature_delta_k(hass, cfg.dhw_hysteresis_entity)
+    target = dhw_step_target_c(params, False, setpoint_grid(hass, cfg.dhw_setpoint_entity))
+    start = dhw_start_below_c(target, hysteresis)
+    floor = float(params.dhw_min_temp)
+    set_issue(
+        hass,
+        ISSUE_DHW_START,
+        bool(params.dhw_enabled) and start is not None and floor > start,
+        placeholders={
+            "floor": f"{floor:.1f}",
+            "start": "" if start is None else f"{start:.1f}",
+            "target": f"{target:.1f}",
+            "hysteresis": "" if hysteresis is None else f"{hysteresis:.1f}",
+        },
+    )
+
+
 def _quiet(hass: Any, config: dict[str, Any]) -> None:
     """#1910: one warning when silent rows cannot be enforced.
 
diff --git a/custom_components/heatpump_optimizer/strings.json b/custom_components/heatpump_optimizer/strings.json
index 18e8349a1d..1e09b13a40 100644
--- a/custom_components/heatpump_optimizer/strings.json
+++ b/custom_components/heatpump_optimizer/strings.json
@@ -1259,6 +1259,8 @@
         "data": {
           "heat_pump_mode_entity": "Heat pump operating mode",
           "pump_duty_mode": "Pump duty control",
+          "space_hysteresis_entity": "Heating start hysteresis (optional)",
+          "dhw_hysteresis_entity": "Hot water start hysteresis (optional)",
           "heat_pump_defrost_entity": "Defrosting",
           "heat_pump_online_entity": "Pump online",
           "heat_pump_fault_entity": "Fault alarm",
@@ -1272,6 +1274,8 @@
         "data_description": {
           "heat_pump_mode_entity": "Optional. The pump's own mode selector - cooling, heating, hot water, or a combination of two. Read only, unless Pump duty control is set to Control. A pump in a cooling or hot-water-only mode cannot heat the house, and one in a heating-only mode cannot make hot water, so without this the plan can promise heat the pump is not currently able to deliver. Left empty, the optimizer assumes the pump can do everything.",
           "pump_duty_mode": "Off (the default) never writes the pump's operating mode or set-points. Observe writes none either and keeps a 24-hour ledger, in the diagnostics, of the duty each plan step asked for against what the pump did (from the power entity, the mode and the tank temperature). With any of the three, the heat pump on/off switch, if you have set one, is still switched by the plan. Control writes the operating mode above (hot water only on hot-water-only steps, heating only on space-heating-only steps, unchanged on idle steps; on a step that plans both, hot water only for the hot-water share of the step and then heating, a share under 5 minutes going to the other duty; Heating + DHW while a boost or an anti-legionella cycle calls for both, and whenever the plan is not in charge), the hot water set-point entity (the hot water set-point configured on the hot water page, or the anti-legionella temperature during a cycle) and the space set-point entity (for a flow set-point, a target that follows the planned power — the heating flow (55 °C, or the Heating flow ceiling) at full power, toward 5 °C (or the Minimum lift above the inlet water) above the first fresh reading of the heat-pump return, buffer tank, floor return or valve outlet (35 °C when none is configured) at the modulation floor — on steps that heat the house, 25 °C on steps that do not (20 °C for a Return temperature set-point, or the entity's own minimum if that is higher), and 35 °C or the weather curve, whichever is higher, when the plan is not in charge; for an indoor one, the planned room temperature). Where the mode offers no single-duty option, as on the GCHV Modbus package, the other duty's set-point is lowered instead: the hot water one to 30 °C, a flow set-point to the same 25 °C (20 °C for Return temperature), an indoor one to 5 °C, each never below the entity's own minimum. A hot-water-only stretch is capped at 90 minutes (30 below -10 °C outdoors), unless the room is already at its planned temperature. Where Capacity limited (night mode) is a switch and silent windows are scheduled, Control also holds that switch on inside a silent window and off outside one. While Optimizer active is on, any change to those entities the optimizer did not make is written back at once; turn Optimizer active off to change the pump by hand. A value the pump does not hold raises a warning and is sent again every 5 minutes.",
+          "space_hysteresis_entity": "Optional. A sensor or number holding the pump's own heating start hysteresis as a temperature difference in K (°C reads the same, °F is scaled; 0 to 20 K): its controller starts heating only once the target sits that far above the water. On a flow or return set-point the lift written above the measured water at the lowest planned level is then never smaller than it, so a planned heating step is one the pump starts. A controller that publishes only the start threshold itself (a Luxtronik's Demand border, input 10107) needs a template sensor of the return target minus that threshold. Left empty or unreadable, the configured lift stands.",
+          "dhw_hysteresis_entity": "Optional. A sensor or number holding the pump's own hot water start hysteresis as a temperature difference in K (°C reads the same, °F is scaled; 0 to 20 K): the pump starts a charge only once the tank is below the hot water target minus this. The plan then places no charge on a tank warmer than that (a charge planned for the current step is kept, as it may already be running; a disinfection charge is judged against the disinfection temperature), and the duty ledger marks an idle hot water step on such a tank not-startable instead of idle-instead. A hot water minimum above that start temperature cannot be held by the pump and raises a warning. Left empty, unreadable or 0, every planned charge is taken to start.",
           "heat_pump_defrost_entity": "Optional. On while the pump reverses to melt frost off the outdoor coil. The electricity bought during a defrost goes into the coil rather than into the house. Note that many pumps are only polled every few minutes, so short defrosts are missed entirely: this is a sample of defrost activity, not a stopwatch.",
           "heat_pump_online_entity": "Optional, and strongly recommended for a cloud-connected pump. On while the pump is actually reachable. A cloud integration can keep republishing its last known readings while the pump itself has dropped off the network, which leaves every other sensor looking perfectly fresh; this is the one signal that says otherwise. On a local (LAN) connection the sensors go unavailable by themselves and this adds little.",
           "heat_pump_fault_entity": "Optional. On while the pump is reporting a fault. Only whether there is a fault is used, never the code itself.",
@@ -1897,6 +1901,10 @@
     "quiet_silent_not_enforced": {
       "title": "Silent windows are not enforced",
       "description": "Silent windows are configured, but the capacity-limited slot ({entity}) is not a switch this integration can hold on, so the plan is not capped for them and the heat pump is never asked to run silently. Assign the heat pump's own night/silent-mode switch as the capacity-limited entity, or remove the silent rows."
+    },
+    "dhw_minimum_above_start": {
+      "title": "The heat pump cannot hold the hot water minimum",
+      "description": "The hot water minimum is {floor} °C, but with a start hysteresis of {hysteresis} K the heat pump starts a charge only once the tank is below {start} °C (its {target} °C target less the hysteresis). The plan places no charge the pump would not start, so it shows the tank falling below the minimum before each charge. Lower the hot water minimum to {start} °C or less, raise the hot water set-point, or reduce the hysteresis on the heat pump."
     }
   },
   "entity": {
diff --git a/custom_components/heatpump_optimizer/thermal_model.py b/custom_components/heatpump_optimizer/thermal_model.py
index b297aaf44c..fe8fa30fb7 100644
--- a/custom_components/heatpump_optimizer/thermal_model.py
+++ b/custom_components/heatpump_optimizer/thermal_model.py
@@ -1875,6 +1875,67 @@ def configured_flow_min_lift_k(config: Any) -> float:
         number if number is not None and number > 0.0 else FLOW_MIN_LIFT_K
     )
 
+def start_flow_min_lift_k(config: Any, start_hysteresis_k: Any = None) -> float:
+    """The modulation floor's lift a heating write uses, K.
+
+    The configured lift (:func:`configured_flow_min_lift_k`), never below the
+    pump's own heating start hysteresis where one is read
+    (``ThermalState.space_start_hysteresis_k``): its controller starts only
+    once the target sits that far above the water, so a floor written closer
+    books heat on a step the pump never starts. The one lift every reader of
+    the floor takes; no hysteresis, or one at or below the configured lift,
+    is the configured lift.
+    """
+    lift = configured_flow_min_lift_k(config)
+    hysteresis = finite_float(start_hysteresis_k)
+    return lift if hysteresis is None else max(lift, hysteresis)
+
+
+def dhw_step_target_c(params: ThermalParameters, cycle: bool, grid: Any = None) -> float:
+    """The hot-water target a step holds on the pump, °C: the one statement
+    of it, which the write, the plan, the duty ledger and the start notice read.
+
+    On a ``cycle`` step (the plan books a disinfection cycle or the pump's
+    disinfection switch is held on) the cycle's temperature (``dhw_cycle_temp``,
+    the higher of the everyday set-point and the disinfection temperature) at
+    or below the tank's hard maximum (``dhw_hard_max_temp``, that temperature
+    capped at 70 °C), which no write exceeds. On any other, and where no cycle
+    is active, the everyday set-point at or below the charge limit
+    (``dhw_max_temp``): above it the tank would be held over the user's own
+    limit for good. Holding the everyday set-point through a cycle stopped the
+    pump's own thermostat short of the cycle's target (2026-11-01: 60 °C
+    planned, 55 °C written back within a minute).
+
+    ``grid`` is the set-point entity's (``inputs.SetpointGrid``): the value
+    goes on its step and never above the bound, which is rounded down (everyday
+    58, step 5: 55, not 60; everyday 57, disinfection 50, step 5: a cycle
+    writes 55). With none, no entity is written and the target stands as it is.
+    """
+    target = params.dhw_cycle_temp if cycle else None
+    value, limit = (
+        (params.dhw_setpoint, params.dhw_max_temp) if target is None
+        else (target, params.dhw_hard_max_temp)
+    )
+    if grid is None:
+        return min(float(value), float(limit))
+    return cast(float, grid.bounded(float(value), hi=limit))
+
+
+def dhw_start_below_c(target_c: Any, start_hysteresis_k: Any) -> float | None:
+    """The tank temperature below which the pump starts a charge, °C, or ``None``.
+
+    The target the step holds less the pump's own hot-water start hysteresis
+    (``ThermalState.dhw_start_hysteresis_k``): its tank thermostat starts a
+    charge only below that, whatever mode it is handed. ``None`` with no
+    target, no hysteresis read, or one not above zero: every charge is then
+    taken to start, which is the pump that starts on the mode alone.
+    """
+    target, hysteresis = finite_float(target_c), finite_float(start_hysteresis_k)
+    if target is None or hysteresis is None or hysteresis <= 0.0:
+        return None
+    return target - hysteresis
+
+
 def on_threshold_kw(params: ThermalParameters) -> float:
     """The MEASURED draw above which the compressor counts as running, in kW.
 
@@ -1929,6 +1990,14 @@ class ThermalState:
     # Hours since the tank was last known to be at anti-legionella temperature.
     # None means "unknown" and is treated as not due.
     dhw_hours_since_legionella: float | None = None
+    # The pump's own start hysteresis per duty, K (``dhw_hysteresis_entity``,
+    # ``space_hysteresis_entity``). None: not configured or unread, and every
+    # planned charge and every heating write is taken to start the pump.
+    dhw_start_hysteresis_k: float | None = None
+    space_start_hysteresis_k: float | None = None
+    # The grid the hot-water set-point entity is written on
+    # (``inputs.SetpointGrid``); None with no entity to write.
+    dhw_setpoint_grid: Any = None
 
     # ECL110 control state
     ecl110_displace_command: float = 0.0  # °C requested parallel shift
@@ -2291,6 +2360,17 @@ def valve_hold_temperature(
     return float(np.interp(need_kw, [_circuit_draw(circuits, k) for k in kinks], kinks))
 
 
+def valve_top_draw(
+    model: "ThermalModel", state: ThermalState, outdoor_temp: float,
+    wind_speed: float, precipitation: float,
+) -> float:
+    """The most the emitters can draw behind the valve, kW: the tank at the
+    curve's top (or ``buffer_max_temp``), past which a hotter tank adds nothing."""
+    circuits = _valve_draw_circuits(
+        model, state, outdoor_temp, wind_speed, precipitation)
+    return _circuit_draw(circuits, model.params.buffer_max_temp)
+
+
 def valve_charge_demand(
     model: "ThermalModel", state: ThermalState, need_kw: float,
     outdoor_temp: float, wind_speed: float, precipitation: float,
diff --git a/custom_components/heatpump_optimizer/translations/de.json b/custom_components/heatpump_optimizer/translations/de.json
index 84f2038a4a..bd78fd8c7b 100644
--- a/custom_components/heatpump_optimizer/translations/de.json
+++ b/custom_components/heatpump_optimizer/translations/de.json
@@ -1259,6 +1259,8 @@
         "data": {
           "heat_pump_mode_entity": "Betriebsart der Wärmepumpe",
           "pump_duty_mode": "Steuerung der Pumpenfunktion",
+          "space_hysteresis_entity": "Starthysterese Heizen (optional)",
+          "dhw_hysteresis_entity": "Starthysterese Warmwasser (optional)",
           "heat_pump_defrost_entity": "Abtauen",
           "heat_pump_online_entity": "Pumpe online",
           "heat_pump_fault_entity": "Störungsmeldung",
@@ -1272,6 +1274,8 @@
         "data_description": {
           "heat_pump_mode_entity": "Optional. Die eigene Modusauswahl der Wärmepumpe – Kühlen, Heizen, Warmwasser oder eine Kombination aus zwei. Nur lesend, außer die Steuerung der Pumpenfunktion steht auf Steuern. Eine Wärmepumpe im Kühl- oder reinen Warmwassermodus kann das Haus nicht heizen, und eine im reinen Heizmodus kann kein Warmwasser bereiten; ohne diese Angabe kann der Plan Wärme versprechen, die die Wärmepumpe gerade nicht liefern kann. Bleibt sie leer, geht der Optimierer davon aus, dass die Wärmepumpe alles kann.",
           "pump_duty_mode": "Aus (Standard) schreibt nie den Betriebsmodus oder die Sollwerte der Wärmepumpe. Beobachten schreibt ebenfalls nichts und führt in den Diagnosedaten ein 24-Stunden-Protokoll darüber, welche Funktion jeder Planschritt angefordert hat und was die Wärmepumpe getan hat (aus der Leistungsentität, dem Modus und der Speichertemperatur). Bei jeder der drei Einstellungen wird der Ein/Aus-Schalter der Wärmepumpe, falls du einen eingerichtet hast, weiterhin vom Plan geschaltet. Steuern schreibt den oben gewählten Betriebsmodus (nur Warmwasser bei reinen Warmwasserschritten, nur Heizen bei reinen Raumheizungsschritten, unverändert bei Leerlaufschritten; bei einem Schritt, der beides plant, nur Warmwasser für den Warmwasseranteil des Schritts und danach Heizen, wobei ein Anteil unter 5 Minuten der anderen Funktion zugeschlagen wird; Heizen + Warmwasser, solange ein Boost oder ein Anti-Legionellen-Zyklus beides verlangt, und immer dann, wenn der Plan nicht die Führung hat), die Entität für den Warmwasser-Sollwert (der auf der Warmwasserseite konfigurierte Warmwasser-Sollwert oder während eines Zyklus die Anti-Legionellen-Temperatur) und die Entität für den Raumheizungs-Sollwert (bei einem Vorlauf-Sollwert ein Ziel, das der geplanten Leistung folgt – die Heizungsvorlauftemperatur (55 °C, oder Obergrenze der Heizungsvorlauftemperatur) bei voller Leistung, in Richtung 5 °C (oder Mindesthub über dem Eingangswasser) über dem ersten aktuellen Wert von Wärmepumpen-Rücklauf, Pufferspeicher, Fußbodenrücklauf oder Ventilauslass (35 °C, wenn keiner konfiguriert ist) an der Modulationsuntergrenze – bei Schritten, die das Haus heizen, 25 °C bei Schritten, die es nicht tun (20 °C bei einem Rücklauftemperatur-Sollwert oder das eigene Minimum der Entität, falls höher), und 35 °C oder die Wetterkurve, je nachdem, was höher ist, wenn der Plan nicht die Führung hat; bei einem Raum-Sollwert die geplante Raumtemperatur). Wo der Modus keine Einzelfunktion anbietet, etwa beim GCHV-Modbus-Paket, wird stattdessen der Sollwert der anderen Funktion gesenkt: der für Warmwasser auf 30 °C, ein Vorlauf-Sollwert auf dieselben 25 °C (20 °C bei Rücklauftemperatur), ein Raum-Sollwert auf 5 °C, jeweils nie unter das eigene Minimum der Entität. Ein reiner Warmwasserabschnitt ist auf 90 Minuten begrenzt (30 unter -10 °C Außentemperatur), außer der Raum hat bereits seine geplante Temperatur. Wo Leistung begrenzt (Nachtmodus) ein Schalter ist und Ruhefenster geplant sind, hält Steuern diesen Schalter außerdem innerhalb eines Ruhefensters an und außerhalb aus. Solange Optimierer aktiv eingeschaltet ist, wird jede Änderung an diesen Entitäten, die der Optimierer nicht vorgenommen hat, sofort zurückgeschrieben; schalte Optimierer aktiv aus, um die Wärmepumpe von Hand zu ändern. Ein Wert, den die Wärmepumpe nicht übernimmt, löst eine Warnung aus und wird alle 5 Minuten erneut gesendet.",
+          "space_hysteresis_entity": "Optional. Ein Sensor oder eine Zahl mit der eigenen Starthysterese der Pumpe fürs Heizen als Temperaturdifferenz in K (°C gilt unverändert, °F wird umgerechnet; 0 bis 20 K): Ihre Regelung beginnt erst zu heizen, wenn das Ziel so weit über dem Wasser liegt. Bei einem Vorlauf- oder Rücklauf-Sollwert ist die Anhebung über dem gemessenen Wasser auf der niedrigsten geplanten Stufe dann nie kleiner, sodass ein geplanter Heizschritt auch wirklich von der Pumpe gestartet wird. Eine Regelung, die nur die Startschwelle selbst veröffentlicht (bei einer Luxtronik der Bedarfsgrenzwert, Eingang 10107), braucht einen Template-Sensor aus Rücklaufziel minus dieser Schwelle. Bleibt sie leer oder unlesbar, gilt die konfigurierte Anhebung.",
+          "dhw_hysteresis_entity": "Optional. Ein Sensor oder eine Zahl mit der eigenen Starthysterese der Pumpe für Warmwasser als Temperaturdifferenz in K (°C gilt unverändert, °F wird umgerechnet; 0 bis 20 K): Die Pumpe startet eine Ladung erst, wenn der Speicher unter dem Warmwasser-Sollwert minus diesem Wert liegt. Der Plan setzt dann keine Ladung auf einen wärmeren Speicher (eine für den aktuellen Schritt geplante Ladung bleibt, da sie schon laufen kann; eine Desinfektionsladung wird an der Desinfektionstemperatur gemessen), und das Funktionsprotokoll markiert einen Warmwasser-Leerlaufschritt auf so einem Speicher als not-startable statt idle-instead. Ein Warmwasser-Minimum über dieser Starttemperatur kann die Pumpe nicht halten und löst eine Warnung aus. Bleibt sie leer, unlesbar oder 0, gilt jede geplante Ladung als startend.",
           "heat_pump_defrost_entity": "Optional. Ein, solange die Wärmepumpe den Kreislauf umkehrt, um Frost vom Außenwärmetauscher zu schmelzen. Der während einer Abtauung bezogene Strom geht in den Wärmetauscher statt ins Haus. Beachte, dass viele Wärmepumpen nur alle paar Minuten abgefragt werden, kurze Abtauvorgänge also komplett übersehen werden: Dies ist eine Stichprobe der Abtauaktivität, keine Stoppuhr.",
           "heat_pump_online_entity": "Optional und bei einer cloudverbundenen Wärmepumpe dringend empfohlen. Ein, solange die Wärmepumpe tatsächlich erreichbar ist. Eine Cloud-Integration kann ihre letzten bekannten Werte weiter veröffentlichen, obwohl die Wärmepumpe selbst vom Netzwerk getrennt ist, sodass alle anderen Sensoren völlig aktuell aussehen; dies ist das einzige Signal, das etwas anderes sagt. Bei einer lokalen Verbindung (LAN) werden die Sensoren von selbst nicht verfügbar, und dies bringt wenig.",
           "heat_pump_fault_entity": "Optional. Ein, solange die Wärmepumpe eine Störung meldet. Verwendet wird nur, ob eine Störung vorliegt, nie der Code selbst.",
@@ -1897,6 +1901,10 @@
     "quiet_silent_not_enforced": {
       "title": "Ruhezeiten werden nicht durchgesetzt",
       "description": "Ruhezeiten sind konfiguriert, aber der Slot für die leistungsbegrenzte Entität ({entity}) ist kein Schalter, den diese Integration halten kann, daher wird der Plan dafür nicht begrenzt und die Wärmepumpe wird nie zum leisen Betrieb aufgefordert. Weise den eigenen Nacht-/Flüstermodus-Schalter der Wärmepumpe als leistungsbegrenzte Entität zu oder entferne die Leise-Zeilen."
+    },
+    "dhw_minimum_above_start": {
+      "title": "Die Wärmepumpe kann das Warmwasser-Minimum nicht halten",
+      "description": "Das Warmwasser-Minimum beträgt {floor} °C, aber bei einer Starthysterese von {hysteresis} K startet die Wärmepumpe eine Ladung erst, wenn der Speicher unter {start} °C liegt (ihr Ziel von {target} °C abzüglich der Hysterese). Der Plan setzt keine Ladung an, die die Pumpe nicht starten würde, und zeigt daher den Speicher vor jeder Ladung unter das Minimum fallen. Senke das Warmwasser-Minimum auf {start} °C oder weniger, erhöhe den Warmwasser-Sollwert oder verringere die Hysterese an der Wärmepumpe."
     }
   },
   "entity": {
diff --git a/custom_components/heatpump_optimizer/translations/en.json b/custom_components/heatpump_optimizer/translations/en.json
index 18e8349a1d..1e09b13a40 100644
--- a/custom_components/heatpump_optimizer/translations/en.json
+++ b/custom_components/heatpump_optimizer/translations/en.json
@@ -1259,6 +1259,8 @@
         "data": {
           "heat_pump_mode_entity": "Heat pump operating mode",
           "pump_duty_mode": "Pump duty control",
+          "space_hysteresis_entity": "Heating start hysteresis (optional)",
+          "dhw_hysteresis_entity": "Hot water start hysteresis (optional)",
           "heat_pump_defrost_entity": "Defrosting",
           "heat_pump_online_entity": "Pump online",
           "heat_pump_fault_entity": "Fault alarm",
@@ -1272,6 +1274,8 @@
         "data_description": {
           "heat_pump_mode_entity": "Optional. The pump's own mode selector - cooling, heating, hot water, or a combination of two. Read only, unless Pump duty control is set to Control. A pump in a cooling or hot-water-only mode cannot heat the house, and one in a heating-only mode cannot make hot water, so without this the plan can promise heat the pump is not currently able to deliver. Left empty, the optimizer assumes the pump can do everything.",
           "pump_duty_mode": "Off (the default) never writes the pump's operating mode or set-points. Observe writes none either and keeps a 24-hour ledger, in the diagnostics, of the duty each plan step asked for against what the pump did (from the power entity, the mode and the tank temperature). With any of the three, the heat pump on/off switch, if you have set one, is still switched by the plan. Control writes the operating mode above (hot water only on hot-water-only steps, heating only on space-heating-only steps, unchanged on idle steps; on a step that plans both, hot water only for the hot-water share of the step and then heating, a share under 5 minutes going to the other duty; Heating + DHW while a boost or an anti-legionella cycle calls for both, and whenever the plan is not in charge), the hot water set-point entity (the hot water set-point configured on the hot water page, or the anti-legionella temperature during a cycle) and the space set-point entity (for a flow set-point, a target that follows the planned power — the heating flow (55 °C, or the Heating flow ceiling) at full power, toward 5 °C (or the Minimum lift above the inlet water) above the first fresh reading of the heat-pump return, buffer tank, floor return or valve outlet (35 °C when none is configured) at the modulation floor — on steps that heat the house, 25 °C on steps that do not (20 °C for a Return temperature set-point, or the entity's own minimum if that is higher), and 35 °C or the weather curve, whichever is higher, when the plan is not in charge; for an indoor one, the planned room temperature). Where the mode offers no single-duty option, as on the GCHV Modbus package, the other duty's set-point is lowered instead: the hot water one to 30 °C, a flow set-point to the same 25 °C (20 °C for Return temperature), an indoor one to 5 °C, each never below the entity's own minimum. A hot-water-only stretch is capped at 90 minutes (30 below -10 °C outdoors), unless the room is already at its planned temperature. Where Capacity limited (night mode) is a switch and silent windows are scheduled, Control also holds that switch on inside a silent window and off outside one. While Optimizer active is on, any change to those entities the optimizer did not make is written back at once; turn Optimizer active off to change the pump by hand. A value the pump does not hold raises a warning and is sent again every 5 minutes.",
+          "space_hysteresis_entity": "Optional. A sensor or number holding the pump's own heating start hysteresis as a temperature difference in K (°C reads the same, °F is scaled; 0 to 20 K): its controller starts heating only once the target sits that far above the water. On a flow or return set-point the lift written above the measured water at the lowest planned level is then never smaller than it, so a planned heating step is one the pump starts. A controller that publishes only the start threshold itself (a Luxtronik's Demand border, input 10107) needs a template sensor of the return target minus that threshold. Left empty or unreadable, the configured lift stands.",
+          "dhw_hysteresis_entity": "Optional. A sensor or number holding the pump's own hot water start hysteresis as a temperature difference in K (°C reads the same, °F is scaled; 0 to 20 K): the pump starts a charge only once the tank is below the hot water target minus this. The plan then places no charge on a tank warmer than that (a charge planned for the current step is kept, as it may already be running; a disinfection charge is judged against the disinfection temperature), and the duty ledger marks an idle hot water step on such a tank not-startable instead of idle-instead. A hot water minimum above that start temperature cannot be held by the pump and raises a warning. Left empty, unreadable or 0, every planned charge is taken to start.",
           "heat_pump_defrost_entity": "Optional. On while the pump reverses to melt frost off the outdoor coil. The electricity bought during a defrost goes into the coil rather than into the house. Note that many pumps are only polled every few minutes, so short defrosts are missed entirely: this is a sample of defrost activity, not a stopwatch.",
           "heat_pump_online_entity": "Optional, and strongly recommended for a cloud-connected pump. On while the pump is actually reachable. A cloud integration can keep republishing its last known readings while the pump itself has dropped off the network, which leaves every other sensor looking perfectly fresh; this is the one signal that says otherwise. On a local (LAN) connection the sensors go unavailable by themselves and this adds little.",
           "heat_pump_fault_entity": "Optional. On while the pump is reporting a fault. Only whether there is a fault is used, never the code itself.",
@@ -1897,6 +1901,10 @@
     "quiet_silent_not_enforced": {
       "title": "Silent windows are not enforced",
       "description": "Silent windows are configured, but the capacity-limited slot ({entity}) is not a switch this integration can hold on, so the plan is not capped for them and the heat pump is never asked to run silently. Assign the heat pump's own night/silent-mode switch as the capacity-limited entity, or remove the silent rows."
+    },
+    "dhw_minimum_above_start": {
+      "title": "The heat pump cannot hold the hot water minimum",
+      "description": "The hot water minimum is {floor} °C, but with a start hysteresis of {hysteresis} K the heat pump starts a charge only once the tank is below {start} °C (its {target} °C target less the hysteresis). The plan places no charge the pump would not start, so it shows the tank falling below the minimum before each charge. Lower the hot water minimum to {start} °C or less, raise the hot water set-point, or reduce the hysteresis on the heat pump."
     }
   },
   "entity": {
diff --git a/custom_components/heatpump_optimizer/translations/sv.json b/custom_components/heatpump_optimizer/translations/sv.json
index 34a284f142..44ec92979f 100644
--- a/custom_components/heatpump_optimizer/translations/sv.json
+++ b/custom_components/heatpump_optimizer/translations/sv.json
@@ -1259,6 +1259,8 @@
         "data": {
           "heat_pump_mode_entity": "Värmepumpens driftläge",
           "pump_duty_mode": "Styrning av pumpens uppgift",
+          "space_hysteresis_entity": "Starthysteres uppvärmning (valfritt)",
+          "dhw_hysteresis_entity": "Starthysteres varmvatten (valfritt)",
           "heat_pump_defrost_entity": "Avfrostning",
           "heat_pump_online_entity": "Pumpen är uppkopplad",
           "heat_pump_fault_entity": "Felindikering",
@@ -1272,6 +1274,8 @@
         "data_description": {
           "heat_pump_mode_entity": "Valfritt. Pumpens eget lägesval - kyla, värme, varmvatten eller en kombination av två. Läses bara av, om inte Styrning av pumpens uppgift står på Styrning. En pump som står i kylläge eller enbart varmvatten kan inte värma huset, och en som står i enbart värmeläge kan inte göra varmvatten. Utan det här kan planen alltså lova värme som pumpen just då inte kan leverera. Lämnas fältet tomt antar optimeringen att pumpen klarar allt.",
           "pump_duty_mode": "Av (standard) skriver aldrig pumpens driftläge eller börvärden. Observera skriver inte heller något och för en 24-timmarslogg, i diagnostiken, över vilken uppgift varje planerat steg bad om och vad pumpen gjorde (från effektentiteten, driftläget och tanktemperaturen). Med något av de tre styrs strömbrytaren för värmepumpen, om du har ställt in en, ändå av planen. Styrning skriver driftläget ovan (bara varmvatten på steg med bara varmvatten, bara värme på steg med bara rumsvärme, oförändrat på vilande steg; på ett steg som planerar båda bara varmvatten under stegets varmvattendel och sedan värme, där en andel under 5 minuter går till den andra uppgiften; Värme + varmvatten medan en boost eller en legionellacykel kräver båda, och närhelst planen inte styr), varmvattnets börvärdesentitet (varmvattnets börvärde från varmvattensidan, eller legionellatemperaturen under en cykel) och rumsvärmens börvärdesentitet (för ett framledningsbörvärde ett mål som följer den planerade effekten — värmeframledningen (55 °C, eller Högsta framledning vid värme) vid full effekt, mot 5 °C (eller Minsta höjning över inkommande vatten) över den första färska avläsningen av värmepumpens retur, ackumulatortanken, golvreturen eller ventilens utlopp (35 °C när ingen är inställd) vid moduleringsgolvet — på steg som värmer huset, 25 °C på steg som inte gör det (20 °C för ett Returtemperatur-börvärde, eller entitetens eget minimum om det är högre), och 35 °C eller värmekurvan, det som är högst, när planen inte styr; för ett inomhusbörvärde den planerade rumstemperaturen). Där driftläget saknar ett läge för bara en uppgift, som i GCHV Modbus-paketet, sänks i stället den andra uppgiftens börvärde: varmvattnets till 30 °C, ett framledningsbörvärde till samma 25 °C (20 °C för Returtemperatur), ett inomhusbörvärde till 5 °C, aldrig under entitetens eget minimum. En sträcka med bara varmvatten begränsas till 90 minuter (30 under -10 °C ute), om inte rummet redan har sin planerade temperatur. Där Begränsad effekt (nattläge) är en brytare och tysta tidsfönster är schemalagda håller Styrning också den brytaren på inom ett tyst fönster och av utanför ett. Medan Optimeraren aktiv är på skrivs varje ändring av entiteterna som optimeraren inte gjorde tillbaka direkt; stäng av Optimeraren aktiv för att ändra pumpen för hand. Ett värde som pumpen inte behåller ger en varning och skickas igen var 5:e minut.",
+          "space_hysteresis_entity": "Valfritt. En sensor eller ett tal med pumpens egen starthysteres för uppvärmning som temperaturskillnad i K (°C läses likadant, °F räknas om; 0 till 20 K): dess styrning börjar värma först när målet ligger så mycket över vattnet. För ett framlednings- eller returbörvärde blir lyftet över det uppmätta vattnet på den lägsta planerade nivån då aldrig mindre, så ett planerat värmesteg är ett som pumpen startar. En styrning som bara publicerar själva startgränsen (en Luxtroniks Demand border, ingång 10107) behöver en mallsensor av returmålet minus den gränsen. Lämnas fältet tomt eller oläsbart gäller det konfigurerade lyftet.",
+          "dhw_hysteresis_entity": "Valfritt. En sensor eller ett tal med pumpens egen starthysteres för varmvatten som temperaturskillnad i K (°C läses likadant, °F räknas om; 0 till 20 K): pumpen startar en laddning först när tanken ligger under varmvattenbörvärdet minus detta. Planen lägger då ingen laddning på en varmare tank (en laddning som planerats för det aktuella steget behålls, eftersom den kan redan pågå; en desinfektionsladdning bedöms mot desinfektionstemperaturen), och pumploggen märker ett vilande varmvattensteg på en sådan tank not-startable i stället för idle-instead. Ett varmvattenminimum över den starttemperaturen kan pumpen inte hålla och ger en varning. Lämnas fältet tomt, oläsbart eller 0 antas varje planerad laddning starta.",
           "heat_pump_defrost_entity": "Valfritt. På medan pumpen vänder cykeln för att smälta bort frost från utomhusbatteriet. Elen som köps under en avfrostning går till batteriet i stället för in i huset. Tänk på att många pumpar bara avfrågas med några minuters mellanrum, så korta avfrostningar missas helt: det här är ett stickprov på avfrostning, inte ett tidtagarur.",
           "heat_pump_online_entity": "Valfritt, men varmt rekommenderat för en molnansluten pump. På medan pumpen faktiskt går att nå. En molnintegration kan fortsätta publicera sina senast kända värden medan pumpen själv har tappat nätverket, vilket får alla andra givare att se alldeles färska ut. Det här är den enda signal som avslöjar det. Vid lokal anslutning (LAN) blir givarna otillgängliga av sig själva och fältet tillför då lite.",
           "heat_pump_fault_entity": "Valfritt. På medan pumpen larmar om ett fel. Bara om det finns ett fel används, aldrig själva felkoden.",
@@ -1897,6 +1901,10 @@
     "quiet_silent_not_enforced": {
       "title": "Tysta fönster genomförs inte",
       "description": "Tysta fönster är konfigurerade, men kapacitetsbegränsningsplatsen ({entity}) är inte en brytare som integrationen kan hålla, så planen begränsas inte för dem och värmepumpen ombeds aldrig köra tyst. Tilldela värmepumpens egna natt-/tystlägesbrytare som kapacitetsbegränsad entitet, eller ta bort de tysta raderna."
+    },
+    "dhw_minimum_above_start": {
+      "title": "Värmepumpen kan inte hålla varmvattenminimum",
+      "description": "Varmvattenminimum är {floor} °C, men med en starthysteres på {hysteresis} K startar värmepumpen en laddning först när tanken ligger under {start} °C (dess mål på {target} °C minus hysteresen). Planen lägger ingen laddning som pumpen inte skulle starta, så den visar tanken falla under minimum före varje laddning. Sänk varmvattenminimum till {start} °C eller lägre, höj varmvattenbörvärdet eller minska hysteresen på värmepumpen."
     }
   },
   "entity": {
diff --git a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
index 909ac11216..c586c82225 100644
--- a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
+++ b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
@@ -126,6 +126,8 @@ const STRINGS = {
     "health.input_heat_pump_fault_entity": "Fault alarm",
     "health.input_heat_pump_heat_energy_entity": "Heat pump heat energy meter",
     "health.input_heat_pump_mode_entity": "Heat pump operating mode",
+    "health.input_space_hysteresis_entity": "Heating start hysteresis",
+    "health.input_dhw_hysteresis_entity": "Hot water start hysteresis",
     "health.input_heat_pump_online_entity": "Pump online",
     "health.input_heat_pump_power_entity": "Heat pump power meter",
     "health.input_heat_pump_return_temp_entity": "Return water temperature",
@@ -1027,6 +1029,8 @@ const STRINGS = {
     "health.input_heat_pump_fault_entity": "Felindikering",
     "health.input_heat_pump_heat_energy_entity": "Värmemängdsmätare för värmepumpen",
     "health.input_heat_pump_mode_entity": "Värmepumpens driftläge",
+    "health.input_space_hysteresis_entity": "Starthysteres uppvärmning",
+    "health.input_dhw_hysteresis_entity": "Starthysteres varmvatten",
     "health.input_heat_pump_online_entity": "Pumpen är uppkopplad",
     "health.input_heat_pump_power_entity": "Effektmätare för värmepumpen",
     "health.input_heat_pump_return_temp_entity": "Returtemperatur",
@@ -1881,6 +1885,8 @@ const STRINGS = {
     "health.input_heat_pump_fault_entity": "Störungsmeldung",
     "health.input_heat_pump_heat_energy_entity": "Wärmemengenzähler der Wärmepumpe",
     "health.input_heat_pump_mode_entity": "Betriebsart der Wärmepumpe",
+    "health.input_space_hysteresis_entity": "Starthysterese Heizen",
+    "health.input_dhw_hysteresis_entity": "Starthysterese Warmwasser",
     "health.input_heat_pump_online_entity": "Pumpe online",
     "health.input_heat_pump_power_entity": "Leistungsmesser der Wärmepumpe",
     "health.input_heat_pump_return_temp_entity": "Rücklauftemperatur",
diff --git a/dev/audit/harnesses/r10_dhw_start_hysteresis.py b/dev/audit/harnesses/r10_dhw_start_hysteresis.py
new file mode 100644
index 0000000000..ad2de645ee
--- /dev/null
+++ b/dev/audit/harnesses/r10_dhw_start_hysteresis.py
@@ -0,0 +1,167 @@
+"""R10-OUTSIDE-DHW-START-HYSTERESIS: planned hot-water runs the pump would not start.
+
+Drives the optimizer as ``tests/validate.py`` drives it, over 18 solves (price
+profiles winter_typical and flat; weather winter_cold, winter_mild and
+summer_warm; starting tank 45, 50 and 53 degC; everyday set-point 55; 24 h at
+15 minutes), and counts the planned hot-water runs that do not begin at step 0
+against a start temperature of the set-point less each of 2, 4 and 6 K.
+
+    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_dhw_start_hysteresis.py [TREE] [--hysteresis K]
+        [--setpoint C] [--step S]
+
+TREE is a checkout root (default: this one; a ``git archive`` export of the
+merge base reads the gap). ``--hysteresis K`` hands the planner the pump's
+start hysteresis (``ThermalState.dhw_start_hysteresis_k``); a tree without the
+field prints ``hysteresis=unsupported`` and plans as it always did.
+``--setpoint C`` is the everyday set-point (default 55). ``--step S`` is the
+step of the set-point entity the target is written to: the written target is
+then the set-point rounded down onto it (the charge limit is the set-point),
+every count below is against that written target less K, and the planner is
+handed the entity's grid (``ThermalState.dhw_setpoint_grid``); a tree without
+that field prints ``step=<S> unsupported`` and judges against the set-point
+as it stands, which is the gap a stepped entity opens (58 on a 5 degC step:
+written 55, judged against 58).
+
+RESULT lines, each a sum over the 18 solves:
+  runs_not_at_step0                      planned runs beginning after step 0
+  runs_at_or_above_minus_{2,4,6}k        of those, begun on a tank at or above the written target - K
+  kwh_planned / kwh_at_or_above_minus_4k planned hot-water kWh, and the share in those runs
+  write_to_start_max_c                   the highest set-point that would start one of the
+                                         minus-4 K runs with a 4 K hysteresis (tank + 4);
+                                         above 55 it is over the user's charge limit
+  floor_deficit_k_steps                  degree-steps of the simulated tank under 45 degC
+  dhw_cost                               the planned hot-water energy at the day's prices
+  plan_sha1                              sha1 over the 18 hot-water schedules and trajectories
+  repair_rounds_max / placements         the most floor-repair calls one placement under a start
+                                         condition made (``dhw_planner.place_startable``), and
+                                         how many placements were counted; "none" with no condition
+Null control: ``--hysteresis`` unset and ``--hysteresis 0`` print the
+plan_sha1 the merge base prints; a hysteresis of 4 prints
+runs_at_or_above_minus_4k=0 only on a tree whose planner reads it.
+"""
+import hashlib
+import math
+import os
+import sys
+from datetime import datetime
+
+import numpy as np
+
+ARGS = sys.argv[1:]
+HYSTERESIS = None
+if "--hysteresis" in ARGS:
+    at = ARGS.index("--hysteresis")
+    HYSTERESIS = float(ARGS[at + 1])
+    del ARGS[at : at + 2]
+OPTS = {"--setpoint": 55.0, "--step": None}
+for flag in OPTS:
+    if flag in ARGS:
+        at = ARGS.index(flag)
+        OPTS[flag] = float(ARGS[at + 1])
+        del ARGS[at : at + 2]
+TREE = os.path.abspath(ARGS[0] if ARGS else os.path.join(os.path.dirname(__file__), "..", "..", ".."))
+sys.path[:0] = [os.path.join(TREE, "tests"), os.path.join(TREE, "custom_components")]
+
+from profiles import house, prices, solve_inputs, weather  # noqa: E402
+from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig  # noqa: E402
+from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402
+
+from heatpump_optimizer import dhw_planner  # noqa: E402
+
+START = datetime(2026, 1, 15, 0, 0)
+ROUNDS: list[int] = []
+if hasattr(dhw_planner, "place_startable"):
+    _place = dhw_planner.place_startable
+
+    def _counted(plan, start_below, temps_of, repair):
+        calls = [0]
+
+        def counting(**kwargs):
+            calls[0] += 1
+            return repair(**kwargs)
+
+        out = _place(plan, start_below, temps_of, counting)
+        if start_below is not None:
+            ROUNDS.append(calls[0])
+        return out
+
+    dhw_planner.place_startable = _counted
+STEP_C = OPTS["--step"]
+SETPOINT_C, FLOOR_C, DT_H = OPTS["--setpoint"], 45.0, 0.25
+#: The target the pump is handed: the set-point, rounded down onto the entity's step.
+WRITTEN_C = SETPOINT_C if STEP_C is None else math.floor(SETPOINT_C / STEP_C + 1e-9) * STEP_C
+SUPPORTED = hasattr(ThermalState(), "dhw_start_hysteresis_k")
+STEP_SUPPORTED = hasattr(ThermalState(), "dhw_setpoint_grid")
+
+
+def solve(price_p: str, weather_p: str, tank_c: float):
+    cfg = house()
+    params = ThermalParameters.from_config(cfg)
+    params.dhw_enabled = True
+    params.dhw_setpoint = SETPOINT_C
+    opt = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(
+        horizon_hours=24, time_step_minutes=15, target_temp=cfg["target_temperature"],
+        min_temp=cfg["min_temperature"], max_temp=cfg["max_temperature"]))
+    outdoor, wind, rain, sun = weather(weather_p, START)
+    state = ThermalState(
+        room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=float(outdoor[0]),
+        dhw_temperature=tank_c, dhw_hours_since_legionella=20.0, upper_floor_temperature=21.0,
+        lower_floor_temperature=21.0, buffer_tank_temperature=40.0)
+    if SUPPORTED and HYSTERESIS is not None:
+        state.dhw_start_hysteresis_k = HYSTERESIS
+    if STEP_SUPPORTED and STEP_C is not None:
+        from heatpump_optimizer.inputs import SetpointGrid
+
+        state.dhw_setpoint_grid = SetpointGrid("°C", STEP_C, None, None)
+    price = np.asarray(prices(price_p, START), dtype=float)
+    result = opt.optimize(inputs=solve_inputs(
+        initial_state=state, prices=price, outdoor_temps=outdoor, wind_speeds=wind,
+        precipitation=rain, solar_radiation=sun, start_time=START))
+    return (np.asarray(result.dhw_power_schedule, dtype=float),
+            np.asarray(result.dhw_temp_trajectory, dtype=float), price)
+
+
+def main() -> int:
+    total = {"runs": 0, 2: 0, 4: 0, 6: 0}
+    kwh = kwh_4k = deficit = cost = 0.0
+    write_max = float("-inf")
+    digest = hashlib.sha1()
+    for price_p in ("winter_typical", "flat"):
+        for weather_p in ("winter_cold", "winter_mild", "summer_warm"):
+            for tank_c in (45.0, 50.0, 53.0):
+                plan, temps, price = solve(price_p, weather_p, tank_c)
+                digest.update(np.round(plan, 9).tobytes() + np.round(temps, 9).tobytes())
+                on = plan > 0.0
+                kwh += float(plan.sum()) * DT_H
+                cost += float((plan * price[: plan.size]).sum()) * DT_H
+                deficit += float(np.clip(FLOOR_C - temps, 0.0, None).sum())
+                for i in range(1, plan.size):
+                    if not on[i] or on[i - 1]:
+                        continue
+                    end = i + int(np.argmin(np.append(on[i:], False)))
+                    total["runs"] += 1
+                    for k in (2, 4, 6):
+                        total[k] += int(temps[i] >= WRITTEN_C - k)
+                    if temps[i] >= WRITTEN_C - 4:
+                        kwh_4k += float(plan[i:end].sum()) * DT_H
+                        write_max = max(write_max, float(temps[i]) + 4.0)
+    shown = "unset" if HYSTERESIS is None else f"{HYSTERESIS:g}" if SUPPORTED else "unsupported"
+    print(f"RESULT hysteresis={shown}")
+    if STEP_C is not None or SETPOINT_C != 55.0:
+        step = "none" if STEP_C is None else f"{STEP_C:g}" + ("" if STEP_SUPPORTED else " unsupported")
+        print(f"RESULT setpoint={SETPOINT_C:g} step={step} written={WRITTEN_C:g} degC")
+    print(f"RESULT runs_not_at_step0={total['runs']} count")
+    for k in (2, 4, 6):
+        print(f"RESULT runs_at_or_above_minus_{k}k={total[k]} count")
+    print(f"RESULT kwh_planned={kwh:.2f} kWh")
+    print(f"RESULT kwh_at_or_above_minus_4k={kwh_4k:.2f} kWh")
+    print("RESULT write_to_start_max_c=" + ("none" if write_max == float("-inf") else f"{write_max:.1f} degC"))
+    print(f"RESULT floor_deficit_k_steps={deficit:.2f} K*steps")
+    print(f"RESULT dhw_cost={cost:.2f} price-units")
+    print(f"RESULT plan_sha1={digest.hexdigest()}")
+    print("RESULT repair_rounds_max=" + (f"{max(ROUNDS)} of {len(ROUNDS)} placements" if ROUNDS else "none"))
+    return 0
+
+
+if __name__ == "__main__":
+    raise SystemExit(main())
diff --git a/dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py b/dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py
new file mode 100644
index 0000000000..665fcad57a
--- /dev/null
+++ b/dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py
@@ -0,0 +1,81 @@
+"""R10-OUTSIDE-DHW-START-HYSTERESIS: the named mutants of the start-hysteresis build.
+
+Applies each mutant, one at a time, to the production file it names under a
+checkout, runs ``tests/block_duty.py`` there, prints KILLED or SURVIVED with
+the failing check names, and restores the file.
+
+    python3 dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py WORKTREE [M1 M4 NULL ...]
+
+WORKTREE is a checkout to mutate in place: a ``git worktree`` of the head,
+never the tree a gate is running in. With no names every mutant runs. A
+mutant whose anchor text is not found exactly once prints ANCHOR and is not
+run, so a moved line reads as unproven, never as killed.
+Null control: the NULL mutant changes a comment only and must print SURVIVED;
+a harness that kills it is failing for a reason of its own.
+"""
+import subprocess, sys, os
+W = sys.argv[1]
+CC = os.path.join(W, "custom_components/heatpump_optimizer")
+M = [
+ ("M1 lift owner returns the configured lift", "thermal_model.py", "    return lift if hysteresis is None else max(lift, hysteresis)\n", "    return lift\n"),
+ ("M2 drop_unstartable >= to >", "dhw_planner.py", "        if temps_of(plan)[i] >= start_below[i]:", "        if temps_of(plan)[i] > start_below[i]:"),
+ ("M3 ledger not-startable branch removed", "pump_arbiter.py", '    if planned == "dhw" and actual == "idle" and _not_startable(row):\n        return "not-startable"\n', ""),
+ ("M4 repair places without the start mask", "dhw_planner.py", "            usable &= startable_steps(plan, temps, start_below)[lo : b + 1]\n", ""),
+ ("M5 startable_steps < to <=", "dhw_planner.py", "[: on.size] < start_below[: on.size]\n", "[: on.size] <= start_below[: on.size]\n"),
+ ("M6 a zero hysteresis is a start condition", "thermal_model.py", "hysteresis is None or hysteresis <= 0.0:", "hysteresis is None or hysteresis < 0.0:"),
+ ("M7 the difference reader ignores the unit's scale", "inputs.py", "    delta_k = value * scale\n", "    delta_k = value\n"),
+ ("M8 the cycle step judged against the everyday target", "dhw_planner.py", "        start[cycle_step] = dhw_start_below_c(dhw_step_target_c(params, True, grid), hysteresis_k)\n", "        pass\n"),
+ ("M9 notice at a minimum equal to the start temperature", "setpoint_check.py", "start is not None and floor > start,", "start is not None and floor >= start,"),
+ ("M10 place_startable returns without the final drop", "dhw_planner.py", "        plan = fixed\n    return drop_unstartable(plan, start_below, temps_of)\n", "        plan = fixed\n    return plan\n"),
+ ("M11 coordinator does not read the options", "coordinator.py", "        read_start_hysteresis(state, self.hass, self.effective_config)\n", ""),
+ ("M12 the floor write ignores the hysteresis", "pump_arbiter.py", 'start_flow_min_lift_k(inp.config, getattr(inp.state, "space_start_hysteresis_k", None)),', "start_flow_min_lift_k(inp.config, None),"),
+ ("M13 the planner ignores the hysteresis", "dhw_planner.py", "dhw_start_temps(params, initial_state, n_steps, legionella_step)", "dhw_start_temps(params, type(initial_state)(), n_steps, legionella_step)"),
+ ("M14 ledger start ignores the written target", "pump_arbiter.py", "dhw_start_below_c(_dhw_target(inp), hysteresis)", "dhw_start_below_c(dhw_step_target_c(inp.params, False), hysteresis)"),
+ ("M15 delta reader accepts above the maximum", "inputs.py", "    return delta_k if 0.0 <= delta_k <= TEMPERATURE_DELTA_MAX_K else None", "    return delta_k if 0.0 <= delta_k else None"),
+ ("M16 a run at step 0 is judged too", "dhw_planner.py", "    for i in np.flatnonzero(on[1:] & ~on[:-1]) + 1:\n", "    for i in np.flatnonzero(on & ~np.append(False, on[:-1])):\n"),
+ ("M17 the round bound is nine", "dhw_planner.py", "STARTABLE_ROUNDS = 8\n", "STARTABLE_ROUNDS = 9\n"),
+ ("M18 a cycle on the first step is not a cycle step", "dhw_planner.py", "if cycle_step is not None and 0 <= cycle_step < n_steps:", "if cycle_step is not None and 0 < cycle_step < n_steps:"),
+ ("M19 a run at the second step is not judged", "dhw_planner.py", "    for i in np.flatnonzero(on[1:] & ~on[:-1]) + 1:\n", "    for i in np.flatnonzero(on[2:] & ~on[1:-1]) + 2:\n"),
+ ("M20 the loop never ends early", "dhw_planner.py", "        if np.array_equal(fixed, plan):\n", "        if False:\n"),
+ ("M21 a cycle past the horizon is written", "dhw_planner.py", "if cycle_step is not None and 0 <= cycle_step < n_steps:", "if cycle_step is not None and 0 <= cycle_step <= n_steps:"),
+ ("M22 the shared clamp zeroes a step on the runnable block", "dhw_planner.py", "        return np.where(plan < ctx.min_run_power - 1e-9, 0.0, plan)\n", "        return np.where(plan <= ctx.min_run_power - 1e-9, 0.0, plan)\n"),
+ ("M23 no step is a cycle step for the write or the ledger", "pump_arbiter.py", '    cycle = (inp.action or {}).get("dhw_reason") == REASON_LEGIONELLA or inp.disinfecting\n', "    cycle = False\n"),
+ ("M24 the set-point check never reaches the start notice", "setpoint_check.py", "    _dhw_start(hass, config, params)\n", "    pass\n"),
+ ("M25 the notice judges the cycle's target", "setpoint_check.py", "    target = dhw_step_target_c(params, False, setpoint_grid(", "    target = dhw_step_target_c(params, True, setpoint_grid("),
+ ("M26 a hysteresis under one kelvin is none", "thermal_model.py", "hysteresis is None or hysteresis <= 0.0:", "hysteresis is None or hysteresis <= 1.0:"),
+ ("M27 pinned hot water is not held to the tank's capacity", "dhw_planner.py", "            schedule = self._ctx_clamp(\n                ctx, initial_state.dhw_temperature, draw_rates, max_temp, schedule)\n", "            pass\n"),
+ ("M28 the write and the ledger ignore the entity's grid", "pump_arbiter.py", 'return dhw_step_target_c(inp.params, cycle, _grid(inp, "dhw_setpoint"))', "return dhw_step_target_c(inp.params, cycle, None)"),
+ ("M29 the planner ignores the entity's grid", "dhw_planner.py", "hysteresis_k, grid = state.dhw_start_hysteresis_k, state.dhw_setpoint_grid\n", "hysteresis_k, grid = state.dhw_start_hysteresis_k, None\n"),
+ ("M30 the notice ignores the entity's grid", "setpoint_check.py", "dhw_step_target_c(params, False, setpoint_grid(hass, cfg.dhw_setpoint_entity))", "dhw_step_target_c(params, False)"),
+ ("M31 the notice is raised with hot water disabled", "setpoint_check.py", "bool(params.dhw_enabled) and start is not None", "start is not None"),
+ ("M32 the everyday target ignores the charge limit", "thermal_model.py", "(params.dhw_setpoint, params.dhw_max_temp) if target is None", "(params.dhw_setpoint, 1e9) if target is None"),
+ ("M33 the cycle's target ignores the hard maximum", "thermal_model.py", "else (target, params.dhw_hard_max_temp)", "else (target, 1e9)"),
+ ("M34 the input read leaves the grid off the state", "inputs.py", "    state.dhw_setpoint_grid = setpoint_grid(hass, cfg.dhw_setpoint_entity)\n", ""),
+ ("M35 the step after a charge the pump would not start is startable", "dhw_planner.py", "        under_way = bool(on[i] and ok[i])\n", "        under_way = bool(on[i])\n"),
+ ("M36 a charge at the first step carries nothing on", "dhw_planner.py", "    under_way = bool(on[:1].any())\n", "    under_way = False\n"),
+ ("M37 no charge under way carries on", "dhw_planner.py", "        ok[i] |= under_way\n", "        pass\n"),
+ ("M38 an entity with no state has a grid", "inputs.py", "    if not entity_id or hass.states.get(entity_id) is None:\n        return None\n    return _grid_of", "    if not entity_id:\n        return None\n    return _grid_of"),
+ ("M39 with no entity the target ignores its bound", "thermal_model.py", "        return min(float(value), float(limit))\n", "        return float(value)\n"),
+ ("M40 the hot-water write goes to an entity with no state", "pump_arbiter.py", 'return None if _grid(inp, "dhw_setpoint") is None else _dhw_target(inp)', "return _dhw_target(inp)"),
+ ("M41 the bound is handed to the grid as the value's own", "thermal_model.py", "grid.bounded(float(value), hi=limit)", "grid.bounded(float(value), hi=float(value))"),
+ ("M42 a charge kept at the first step is itself startable on a warm tank", "dhw_planner.py", "    under_way = bool(on[:1].any())\n", "    under_way = bool(on[:1].any())\n    ok[:1] |= on[:1]\n"),
+ ("M43 the notice is never raised", "setpoint_check.py", "        bool(params.dhw_enabled) and start is not None and floor > start,\n", "        False,\n"),
+ ("NULL comment-only change", "dhw_planner.py", "    on = plan > 0.0\n    for i in", "    on = plan > 0.0  # null mutant\n    for i in"),
+]
+only = sys.argv[2:] 
+for name, f, old, new in M:
+    if only and name.split()[0] not in only: continue
+    p = os.path.join(CC, f); src = open(p).read()
+    if src.count(old) != 1:
+        print(f"{name}: ANCHOR x{src.count(old)}"); continue
+    open(p, "w").write(src.replace(old, new))
+    try:
+        r = subprocess.run([sys.executable, "tests/block_duty.py"], cwd=W, capture_output=True, text=True,
+                           env={**os.environ, "PYTHONPATH": "tests/hastub"}, timeout=600)
+        fails = [l.strip() for l in (r.stdout + r.stderr).splitlines() if l.strip().startswith("FAIL")]
+        tail = (r.stdout + r.stderr).strip().splitlines()[-1][:160] if not fails else ""
+        print(f"{name}: {'KILLED' if r.returncode else 'SURVIVED'} rc={r.returncode} {len(fails)} failing")
+        for l in fails[:6]: print("    " + l[:170])
+        if r.returncode and not fails: print("    " + tail)
+    finally:
+        open(p, "w").write(src)
diff --git a/dev/audit/harnesses/r10_duty_switch_price_section.py b/dev/audit/harnesses/r10_duty_switch_price_section.py
new file mode 100644
index 0000000000..6f6895aca6
--- /dev/null
+++ b/dev/audit/harnesses/r10_duty_switch_price_section.py
@@ -0,0 +1,223 @@
+#!/usr/bin/env python3
+"""Run R10-DUTY-SWITCH-PLANNER-PRICE's section of ``tests/features.py`` alone, and its mutants.
+
+WHY IT EXISTS. ``tests/features.py`` has no section filter, and the mutation
+proof of the group (the leg rule's leaf, the switch term, the lost running
+time, the banned candidate, the learner's count cap and its read for the
+planner) runs the section once per mutant. This cuts the section out of the
+script at its two markers, binds the six names the script had bound by then,
+and runs it. It executes the tree's own text: a check edited in
+``tests/features.py`` is the check run here.
+
+It refuses (exit 2) when a marker is missing or the section holds no check,
+so a moved marker cannot read as a pass.
+
+    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_price_section.py
+    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_price_section.py --mutants [name ...]
+
+``--mutants`` copies the package and ``tests/`` to a private directory per
+mutant, applies one edit there (the tree is never written), runs the section
+on the copy and prints the checks that went red. An unmutated copy runs
+first as the control and must pass. A mutant whose pattern is not found
+exactly once, or that turns no check red, is printed as such and the exit
+code is 1. The coordinator's one argument is outside the section (its check
+sits beside #1512's in the lifecycle part of the script) and is proven by a
+whole run of ``tests/features.py``.
+"""
+from __future__ import annotations
+
+import os
+import shutil
+import subprocess
+import sys
+import tempfile
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
+ROOT = repo_root(os.environ.get("DSP_SECTION_ROOT") or __file__)
+START = "from types import SimpleNamespace as _DspNS"
+END = '\nsys.exit(R.close("FEATURE CHECKS"))'
+PRELUDE = """
+from datetime import datetime, timedelta
+import numpy as np
+from harness import Results, UTC
+from profiles import solve_inputs
+R = Results("R10-DUTY-SWITCH-PLANNER-PRICE's section of tests/features.py")
+"""
+PKG = "custom_components/heatpump_optimizer/"
+
+#: name, file, the text to find exactly once, its replacement.
+MUTANTS: list[tuple[str, str, str, str]] = [
+    ("optimizer: a candidate is tried with no requirement to hold it to", PKG + "optimizer.py",
+     "if kept_requirement is None or not duty_legs.switch_weight(", "if not duty_legs.switch_weight("),
+    ("optimizer: a candidate pass that raises is not caught", PKG + "optimizer.py",
+     "    except Exception as err:  # noqa: BLE001 - a candidate is optional", "    except KeyError as err:  # a candidate is optional"),
+    ("learner: no count cap", PKG + "duty_switch.py",
+     "        if self.n > N_CAP:\n", "        if False:\n"),
+    ("learner: the cap scales the stops alone", PKG + "duty_switch.py",
+     "self.k, self.kept_w = self.k * scale, self.kept_w * scale", "self.k = self.k * scale"),
+    ("learner: the cap is three times the on-threshold", PKG + "duty_switch.py",
+     "N_CAP = 2.0 * N_ON", "N_CAP = 3.0 * N_ON"),
+    ("learner: the read ignores the latch", PKG + "duty_switch.py",
+     "read = [d if d.usable else Direction() for", "read = [d for"),
+    ("learner: the read swaps the directions", PKG + "duty_switch.py",
+     "return (read[0].p, read[1].p), (read[0].median_off_s or 0.0, read[1].median_off_s or 0.0)",
+     "return (read[1].p, read[0].p), (read[1].median_off_s or 0.0, read[0].median_off_s or 0.0)"),
+    ("learner: the read hands the off time of the other direction", PKG + "duty_switch.py",
+     "(read[0].median_off_s or 0.0, read[1].median_off_s or 0.0)",
+     "(read[1].median_off_s or 0.0, read[0].median_off_s or 0.0)"),
+    ("leaf: the hot-water-to-heating switch reads the other direction", PKG + "duty_legs.py",
+     "(before == DHW) & (after == SPACE),\n        p_ds,", "(before == DHW) & (after == SPACE),\n        p_sd,"),
+    ("leaf: the switch weight takes the larger neighbouring draw", PKG + "duty_legs.py",
+     "np.minimum(level[_BEFORE], level[_AFTER])", "np.maximum(level[_BEFORE], level[_AFTER])"),
+    ("leaf: the in-step weight draws the smaller circuit, not the combined draw", PKG + "duty_legs.py",
+     "np.where(two, p_ds * level, 0.0)",
+     "np.where(two, p_ds * np.minimum(space, np.asarray(dhw_kw, dtype=float)), 0.0)"),
+    ("leaf: the weight is not divided by the maximum draw", PKG + "duty_legs.py",
+     "axis=1)) / p_max", "axis=1))"),
+    ("leaf: a small hot-water share no longer collapses to heating", PKG + "duty_legs.py",
+     "to_space = both & (dhw_min < SPLIT_MIN_MINUTES)", "to_space = both & (dhw_min > SPLIT_MIN_MINUTES)"),
+    ("leaf: a small heating share no longer collapses to hot water", PKG + "duty_legs.py",
+     "~to_space & (step_minutes - dhw_min < SPLIT_MIN_MINUTES)",
+     "~to_space & (step_minutes - dhw_min > SPLIT_MIN_MINUTES)"),
+    ("leaf: the leg classification ignores the duty floor", PKG + "duty_legs.py",
+     "_runs(space, floor), _runs(dhw, floor)", "_runs(space, None), _runs(dhw, None)"),
+    # The leaf has no zero-pair return: zero probabilities weigh zero on the
+    # full path, and the optimizer never calls it without a priced direction.
+    ("leaf: a pump with no maximum draw is not returned early", PKG + "duty_legs.py",
+     "    if p_max <= 0:\n        return np.zeros(space.shape[0])", "    if p_max < 0:\n        return np.zeros(space.shape[0])"),
+    ("leaf: a negative learned value is kept", PKG + "duty_legs.py",
+     "max(v, 0.0) if math.isfinite(v) and v <= upper", "v if math.isfinite(v) and v <= upper"),
+    ("leaf: a learned value on its upper bound reads as zero", PKG + "duty_legs.py",
+     "max(v, 0.0) if math.isfinite(v) and v <= upper", "max(v, 0.0) if math.isfinite(v) and v < upper"),
+    ("leaf: the early return is one entry per step, not per row", PKG + "duty_legs.py",
+     "return np.zeros(space.shape[0])", "return np.zeros(space.shape[1])"),
+    ("optimizer: no priced direction still returns a pair", PKG + "optimizer.py",
+     "return stops if max(stops) > 0 else None", "return stops"),
+    ("leaf: the charged step is the hot-water block's last step", PKG + "duty_legs.py",
+     "charged[1:] |= (last[:-1] == DHW) & (first[1:] == SPACE)",
+     "charged[:-1] |= (last[:-1] == DHW) & (first[1:] == SPACE)"),
+    ("leaf: the delivered draw is keyed on the clamped install", PKG + "duty_legs.py",
+     "    if floor is None:\n        return space_kw", "    if floor is not None:\n        return space_kw"),
+    ("leaf: the delivered draw loses only the space share", PKG + "duty_legs.py",
+     "(1.0 - avail) * (space_kw + dhw_kw)", "(1.0 - avail) * space_kw"),
+    ("optimizer: the switch term is handed the delivered draw", PKG + "optimizer.py",
+     "switch_cost(space_power, dhw_plan_power)", "switch_cost(heat_power, dhw_plan_power)"),
+    ("optimizer: the simulation is handed the shipped draw", PKG + "optimizer.py",
+     "_space_traj(heat_power, buffer_exo_kw)", "_space_traj(space_power, buffer_exo_kw)"),
+    ("optimizer: the energy cost is handed the shipped draw", PKG + "optimizer.py",
+     "drawn = combined if heat_power is space_power else heat_power + dhw_plan_power",
+     "drawn = combined"),
+    ("optimizer: the publication drops the solve's availability vector", PKG + "optimizer.py",
+     "heat_space = optimal_space if self._space_avail is None else duty_legs",
+     "heat_space = optimal_space if True else duty_legs"),
+    ("planner: the placement ban is not OR'd into forced_off", PKG + "dhw_planner.py",
+     "return forced_off if ban is None else _forced_off_with(forced_off, ban, n_steps)",
+     "return forced_off"),
+    ("optimizer: a candidate short of its requirement is adopted", PKG + "optimizer.py",
+     "            and first_short(plan.schedule, requirement, unheld)[1] is None\n",
+     "            and True\n"),
+    ("optimizer: a candidate with hot water on a banned step is adopted", PKG + "optimizer.py",
+     "            not np.any(plan.schedule[ban & ~forced_on] > 0)\n", "            True\n"),
+    ("optimizer: the candidate is adopted on a higher score", PKG + "optimizer.py",
+     "if score < base - 1e-9:", "if score > base - 1e-9:"),
+    ("leaf: the lost share is not capped at one", PKG + "duty_legs.py",
+     "return min(1.0, stop_probability[0] * off_seconds[0] / (step_minutes * 60.0))",
+     "return stop_probability[0] * off_seconds[0] / (step_minutes * 60.0)"),
+    ("leaf: the lost share ignores the stop probability", PKG + "duty_legs.py",
+     "min(1.0, stop_probability[0] * off_seconds[0] /", "min(1.0, off_seconds[0] /"),
+    # The fix reviewer's three survivors at ee89d50b2b (R5, R9, R11), its texts.
+    ("optimizer: the co-optimisation headroom ignores the availability vector", PKG + "optimizer.py",
+     "p_max, dhw_power, self._space_avail, _duty_floor(self))", "p_max, dhw_power, None, _duty_floor(self))"),
+    ("optimizer: the availability vector is classified with no duty floor", PKG + "optimizer.py",
+     "return duty_legs.availability(space, tank, lost, _duty_floor(opt))",
+     "return duty_legs.availability(space, tank, lost, None)"),
+    ("optimizer: the candidate pass runs on a combi store", PKG + "optimizer.py",
+     "or not opt.config.cycling_cost > 0 or opt.model.params.dhw_store.combi:",
+     "or not opt.config.cycling_cost > 0:"),
+    ("optimizer: the co-optimisation headroom is handed no duty floor", PKG + "optimizer.py",
+     "p_max, dhw_power, self._space_avail, _duty_floor(self))", "p_max, dhw_power, self._space_avail, None)"),
+    # Repair round 2: the two clamps left on the line the availability reads
+    # its start through, the mutation table's CLAMP_DROP twins of one anchor.
+    ("optimizer: the start is read with no cap beside hot water", PKG + "optimizer.py",
+     "np.minimum(start, np.maximum(0.0, p_max - dhw_plan)),", "(start),"),
+    ("optimizer: the start is capped at zero in every step", PKG + "optimizer.py",
+     "np.minimum(start, np.maximum(0.0, p_max - dhw_plan)),", "np.minimum(start, (0.0)),"),
+    ("arbiter: the share serves the legs in reverse order", PKG + "pump_arbiter.py",
+     "return legs[0][0] if (now - result.timestamps[i]) < first_ends else legs[-1][0]",
+     "return legs[-1][0] if (now - result.timestamps[i]) < first_ends else legs[0][0]"),
+]
+
+
+def run_section(root: Path) -> int:
+    text = (root / "tests" / "features.py").read_text()
+    if text.count(START) != 1 or text.count(END) != 1:
+        print("REFUSED: a section marker is missing or repeated in tests/features.py")
+        return 2
+    section = text[text.index(START):text.index(END)]
+    sys.path[:0] = [str(root / "tests"), str(root / "custom_components")]
+    scope: dict = {"__name__": "duty_switch_price_section"}
+    exec(compile(PRELUDE + section, "tests/features.py[duty-switch-price]", "exec"), scope)
+    results = scope["R"]
+    if not results.checks:
+        print("REFUSED: the section ran no check")
+        return 2
+    return results.close("DUTY-SWITCH PLANNER-PRICE SECTION CHECKS")
+
+
+def _copy_run(edit: tuple[str, str, str] | None) -> tuple[int | None, list[str]]:
+    """The section's exit code and red check names on a private copy, ``None`` when the pattern is not there once."""
+    with tempfile.TemporaryDirectory() as tmp:
+        copy = Path(tmp)
+        for part in ("custom_components", "tests"):
+            shutil.copytree(ROOT / part, copy / part, ignore=shutil.ignore_patterns("__pycache__", "golden"))
+        if edit is not None:
+            path, old, new = edit
+            text = (copy / path).read_text()
+            if text.count(old) != 1:
+                return None, []
+            (copy / path).write_text(text.replace(old, new))
+        env = {**os.environ, "DSP_SECTION_ROOT": str(copy / "custom_components"),
+               "PYTHONPATH": str(copy / "tests" / "hastub"), "PYTHONDONTWRITEBYTECODE": "1"}
+        out = subprocess.run([sys.executable, __file__], cwd=copy, env=env, capture_output=True, text=True)
+        red = [line[7:].split("  [")[0] for line in out.stdout.splitlines() if line.startswith("  FAIL ")]
+        if "SECTION CHECKS" not in out.stdout:  # a traceback exits 1 too, and closes nothing
+            red.append(f"the section stopped: {(out.stderr.strip().splitlines() or ['no output'])[-1]}")
+        return out.returncode, red
+
+
+def run_mutants(names: list[str]) -> int:
+    code, red = _copy_run(None)
+    print(f"== control, no edit: exit {code}, {len(red)} red")
+    if code != 0:
+        print("\n".join(f"     {name}" for name in red))
+        return 1
+    bad = 0
+    for name, path, old, new in MUTANTS:
+        if names and name not in names:
+            continue
+        code, red = _copy_run((path, old, new))
+        verdict = "PATTERN NOT FOUND ONCE" if code is None else f"{len(red)} red" if red else "SURVIVED"
+        bad += not red
+        print(f"== {name}: {verdict}")
+        print("\n".join(f"     {check}" for check in red), end="\n" if red else "")
+    print(f"RESULT mutants_not_killed={bad}")
+    return 1 if bad else 0
+
+
+if __name__ == "__main__":
+    os.chdir(ROOT)
+    sys.exit(run_mutants(sys.argv[2:]) if sys.argv[1:2] == ["--mutants"] else run_section(ROOT))
diff --git a/dev/audit/harnesses/r10_sav_held_capacity_census.py b/dev/audit/harnesses/r10_sav_held_capacity_census.py
new file mode 100644
index 0000000000..5b597dec0c
--- /dev/null
+++ b/dev/audit/harnesses/r10_sav_held_capacity_census.py
@@ -0,0 +1,100 @@
+"""R10-SAV-VALUATION-RESIDUE: the held state's census over every bound on the reference's heat.
+
+    PYTHONPATH=tests/hastub:tests:custom_components \\
+        python3 dev/audit/harnesses/r10_sav_held_capacity_census.py
+
+Drives ``_thermostat_held_state`` over a grid of installs -- no valve and the
+three throttling valve modes, both zonings, the derived and the
+``two_tank_4way`` layout, pumps of 4, 6 and 9 kW, valve targets 21 to 40 C,
+outdoor -25 to 18 C -- and books one reference step from each held state at
+``_compute_baseline_power``'s power on a one-step horizon (nothing to
+apportion). The property is the phenomenon's, not an instance's: a held state
+the reference step can keep draws no stored heat on its first booked step.
+Prints the case count, the worst first-step store change in kWh_th and the
+count over 0.02 kWh_th, then the capacity control: at -25 C a 9 kW pump holds
+21 C (valved and not), a 4 kW pump does not.
+
+Preconditions, asserted (exit 1): every grid case ran without an exception,
+every held room lies in [min(outdoor, 21), 21], and the case count is the
+grid's product.
+"""
+
+import itertools
+import sys
+
+import numpy as np
+
+from heatpump_optimizer.optimizer import (
+    HeatPumpOptimizer,
+    OptimizationConfig,
+    _thermostat_held_state,
+)
+from heatpump_optimizer.thermal_model import (
+    ThermalModel,
+    ThermalParameters,
+    ThermalState,
+    WeatherSeries,
+)
+from profiles import house
+
+TARGET_C = 21.0
+MODES = ("none", "manual", "smart_read", "smart_write")
+ZONINGS = (True, False)
+LAYOUTS = (None, "two_tank_4way")
+PUMPS_KW = (4.0, 6.0, 9.0)
+VALVE_TARGETS_C = (21.0, 25.0, 30.0, 40.0)
+OUTDOORS_C = (-25.0, -15.0, -5.0, 0.0, 5.0, 10.0, 14.0, 16.0, 18.0)
+
+
+def first_step(mode, two_zone, layout, pump_kw, valve_target, outdoor):
+    """The held state and its first booked reference step's store change, kWh_th."""
+    cfg = {"buffer_tank_volume": 750.0, "buffer_max_temperature": 56.0,
+           "heat_pump_max_power": pump_kw}
+    if mode != "none":
+        cfg.update(mixing_valve_mode=mode, mixing_valve_target=valve_target)
+    if layout:
+        cfg["topology_layout"] = layout
+    model = ThermalModel(ThermalParameters.from_config(house(two_zone=two_zone, dhw=False, **cfg)))
+    opt = HeatPumpOptimizer(model, OptimizationConfig(
+        horizon_hours=1, time_step_minutes=15, target_temp=TARGET_C))
+    weather = WeatherSeries(outdoor_temps=np.array([outdoor]), wind_speeds=np.zeros(1),
+                            precipitation=np.zeros(1), solar_radiation=np.zeros(1))
+    start = ThermalState(room_temperature=20.5, slab_temperature=22.0,
+                         outdoor_temperature=outdoor, upper_floor_temperature=20.5,
+                         lower_floor_temperature=20.5, buffer_tank_temperature=30.0)
+    held = _thermostat_held_state(model, start, weather, TARGET_C)
+    power = float(opt._compute_baseline_power(weather, start, 0.25)[0][0])
+    nxt = model.simulate_step(held, power, outdoor, 0.0, 0.0, 0.0, 0.25)
+    return held, opt._stored_thermal_energy(nxt) - opt._stored_thermal_energy(held), power
+
+
+def main() -> int:
+    grid = list(itertools.product(MODES, ZONINGS, LAYOUTS, PUMPS_KW, VALVE_TARGETS_C, OUTDOORS_C))
+    ran, worst, worst_case, over, refused = 0, 0.0, None, 0, []
+    for case in grid:
+        try:
+            held, ds, power = first_step(*case)
+        except Exception as exc:  # a refusal is a precondition failure, reported
+            refused.append((case, repr(exc)[:120]))
+            continue
+        ran += 1
+        outdoor = case[-1]
+        if not min(outdoor, TARGET_C) - 1e-9 <= held.room_temperature <= TARGET_C:
+            refused.append((case, f"held room {held.room_temperature:.3f} out of range"))
+        if abs(ds) > abs(worst):
+            worst, worst_case = ds, (*case, round(held.room_temperature, 3), round(power, 3))
+        over += abs(ds) > 0.02
+    print(f"RESULT census: cases {ran} of {len(grid)}, worst first-step dS {worst:+.4f} kWh_th "
+          f"at {worst_case}, over 0.02 kWh_th {over}")
+    for mode in ("none", "manual"):
+        for pump_kw in (4.0, 9.0):
+            held, ds, power = first_step(mode, True, None, pump_kw, 40.0, -25.0)
+            print(f"RESULT control two-zone -25 C mode={mode} pump {pump_kw} kW: held room "
+                  f"{held.room_temperature:.3f} power {power:.3f} first-step dS {ds:+.4f} kWh_th")
+    for case, why in refused[:10]:
+        print("REFUSED", case, why)
+    return 1 if refused or ran != len(grid) else 0
+
+
+if __name__ == "__main__":
+    sys.exit(main())
diff --git a/dev/audit/rounds/round3/D5/option_doc_coverage.py b/dev/audit/rounds/round3/D5/option_doc_coverage.py
index e21fc9f616..23ee15ecc2 100644
--- a/dev/audit/rounds/round3/D5/option_doc_coverage.py
+++ b/dev/audit/rounds/round3/D5/option_doc_coverage.py
@@ -105,9 +105,9 @@ EXPECTED on this tree (ae36eff printed option_fields_rendered=174 and
     is reached by a shell-out the closure recorder cannot see, so it does not
     go red on a pull request: it is re-measured in the commit that changes
     what the script prints, or main's forced-full run finds it):
-    RESULT option_fields_rendered=216 count   (211 until R10-COMBI-TANK's five combi fields; 208 until R10-GENERIC-HEAT-CURVE's three heat_curve fields)
+    RESULT option_fields_rendered=218 count   (216 until the two start-hysteresis pickers; 211 until R10-COMBI-TANK's five combi fields; 208 until R10-GENERIC-HEAT-CURVE's three heat_curve fields)
     RESULT option_fields_undocumented=0 count
-    RESULT option_schema_keys_rendered=250 count   (244 until R10-COMBI-TANK; 241 until R10-GENERIC-HEAT-CURVE)
+    RESULT option_schema_keys_rendered=252 count   (250 until the two start-hysteresis pickers; 244 until R10-COMBI-TANK; 241 until R10-GENERIC-HEAT-CURVE)
     RESULT wood_economics_fields_rendered=4 count
     RESULT wood_economics_doc_lines=8 count      (tolerance: exact;
     moved 6 -> 8 by #1645/F8.1: the Services section's `simulate_plan`
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index e67593e30e..e3d6e2186d 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -283,7 +283,7 @@
   "source": "docs/architecture.md",
   "claim": "45 modules",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=90 measured=90",
+  "result": "documented=91 measured=91",
   "verdict": "true",
   "truth": ""
  },
@@ -292,7 +292,7 @@
   "source": "docs/architecture.md",
   "claim": "the module map is the package's module list",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "on disk=90, listed=90, missing=[], phantom=[]",
+  "result": "on disk=91, listed=91, missing=[], phantom=[]",
   "verdict": "true",
   "truth": "0 modules are absent from the map: "
  },
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index 95033a6826..e4521e8162 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -35,8 +35,8 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C29 | `docs/architecture.md:module map` | config_flow.py -- Setup flow plus 24 option pages behind two menus | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=24 measured=24 | **true** |  |
 | C30 | `docs/configuration.md` | every documented Default (97 rows) is the default the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 97 compared, mismatches=[] | **true** |  |
 | C31 | `docs/configuration.md` | every documented Range (104 rows) is the NumberSelector min/max the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 104 compared, mismatches=[] | **true** |  |
-| C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=90 measured=90 | **true** |  |
-| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=90, listed=90, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
+| C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=91 measured=91 | **true** |  |
+| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=91, listed=91, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
 | C34 | `docs/architecture.md:The Home Assistant boundary` | the boundary sentence's count of modules importing `homeassistant` at module level | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=32 measured=32 | **true** |  |
 | C35 | `docs/architecture.md:The Home Assistant boundary` | the named modules are the complete set of module-level importers | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | named=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], measured=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], unnamed=[] | **true** | unnamed module-level importers:  |
 | C36 | `docs/architecture.md:The Home Assistant boundary` | everything outside the named set is free of homeassistant, so each module can be driven with no Home Assistant running | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 0 modules outside the named set import homeassistant at module level | **true** | modules outside the named set import homeassistant at module level and cannot be imported without it:  |
diff --git a/dev/audit/rounds/round4/D6/claims.py b/dev/audit/rounds/round4/D6/claims.py
index 6c6056f2b9..53645fb18f 100644
--- a/dev/audit/rounds/round4/D6/claims.py
+++ b/dev/audit/rounds/round4/D6/claims.py
@@ -91,7 +91,7 @@ against a document that is CORRECT.
                                          Range row on the expert thermal-model
                                          table; 101 with R10-USER-DOCS-FINAL's
                                          per-field rows on the options pages)
-    RESULT arch_modules_on_disk=90       (89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 85 until R10-WHY-NOW-WIDGET's slot_drivers.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
+    RESULT arch_modules_on_disk=91       (90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 85 until R10-WHY-NOW-WIDGET's slot_drivers.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
                                          66 until R9 F2.5's batchmath.py;
                                          65 until #1588's pump_arbiter.py; 64
                                          until #1408's store.py;
@@ -117,7 +117,7 @@ against a document that is CORRECT.
                                          bytes of, so nothing compared these
                                          numbers to a run between 2026-09-17
                                          and then)
-    RESULT arch_map_listed=90            (89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
+    RESULT arch_map_listed=91            (90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
                                          66 until R9 F2.5's batchmath.py;
                                          was 45; 11 were missing; 66 with
                                          #1588's pump_arbiter.py added to
diff --git a/dev/programme/delivery/3499.md b/dev/programme/delivery/3499.md
index ab08e8486e..e6f9d2f65f 100644
--- a/dev/programme/delivery/3499.md
+++ b/dev/programme/delivery/3499.md
@@ -1 +1 @@
-- [#3499](https://github.com/tvofi/heatpump_optimizer/pull/3499) — **open**, R10-GATE-DEFER-BARRIER: r10 gate defer barrier (R10-GATE-DEFER-BARRIER)
+- [#3499](https://github.com/tvofi/heatpump_optimizer/pull/3499) — **merged `6142f48`**, R10-GATE-DEFER-BARRIER: r10 gate defer barrier (R10-GATE-DEFER-BARRIER).
diff --git a/dev/programme/delivery/3511.md b/dev/programme/delivery/3511.md
new file mode 100644
index 0000000000..071ec1a8dc
--- /dev/null
+++ b/dev/programme/delivery/3511.md
@@ -0,0 +1 @@
+- [#3511](https://github.com/tvofi/heatpump_optimizer/pull/3511) — **merged `90c6bc3`**, R10-SAV-VALUATION-RESIDUE: r10 sav valuation residue.
diff --git a/dev/programme/delivery/3520.md b/dev/programme/delivery/3520.md
index 99ff6e09e8..622ef34ae4 100644
--- a/dev/programme/delivery/3520.md
+++ b/dev/programme/delivery/3520.md
@@ -1 +1 @@
-- [#3520](https://github.com/tvofi/heatpump_optimizer/pull/3520) — **open**, R10-HOTFIX-TICK-SELFTEST-CHECKOUT: r10 hotfix tick selftest checkout (R10-HOTFIX-TICK-SELFTEST-CHECKOUT)
+- [#3520](https://github.com/tvofi/heatpump_optimizer/pull/3520) — **merged `ad95665`**, R10-HOTFIX-TICK-SELFTEST-CHECKOUT: r10 hotfix tick selftest checkout.
diff --git a/dev/programme/delivery/3526.md b/dev/programme/delivery/3526.md
new file mode 100644
index 0000000000..34a6cfc62c
--- /dev/null
+++ b/dev/programme/delivery/3526.md
@@ -0,0 +1 @@
+- [#3526](https://github.com/tvofi/heatpump_optimizer/pull/3526) — **merged `c67c193`**, R10-DUTY-SWITCH-PLANNER-PRICE: r10 duty switch planner price (R10-DUTY-SWITCH-PLANNER-PRICE).
diff --git a/dev/programme/delivery/3531.md b/dev/programme/delivery/3531.md
new file mode 100644
index 0000000000..9660f4a574
--- /dev/null
+++ b/dev/programme/delivery/3531.md
@@ -0,0 +1 @@
+- [#3531](https://github.com/tvofi/heatpump_optimizer/pull/3531) — **open**, R10-OUTSIDE-DHW-START-HYSTERESIS: r10 outside dhw start hysteresis (R10-OUTSIDE-DHW-START-HYSTERESIS)
diff --git a/dev/programme/delivery/3539.md b/dev/programme/delivery/3539.md
index 80a5e06e48..310486959d 100644
--- a/dev/programme/delivery/3539.md
+++ b/dev/programme/delivery/3539.md
@@ -1 +1 @@
-- [#3539](https://github.com/tvofi/heatpump_optimizer/pull/3539) — **open**, R10-REVIEW-DISPATCH-RESIDUE (part 6): r10 review dispatch residue p6 (R10-REVIEW-DISPATCH-RESIDUE)
+- [#3539](https://github.com/tvofi/heatpump_optimizer/pull/3539) — **merged `1906e79`**, R10-REVIEW-DISPATCH-RESIDUE (part 6): r10 review dispatch residue p6.
diff --git a/dev/programme/delivery/3546.md b/dev/programme/delivery/3546.md
new file mode 100644
index 0000000000..375ea41b10
--- /dev/null
+++ b/dev/programme/delivery/3546.md
@@ -0,0 +1 @@
+- [#3546](https://github.com/tvofi/heatpump_optimizer/pull/3546) — **open**, R10-HOTFIX-UPDATEPR-FIGURE-REFRESH: r10 hotfix updatepr figure refresh (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH)
diff --git a/dev/programme/delivery/3549.md b/dev/programme/delivery/3549.md
index b2769f696d..7ceb24fe6f 100644
--- a/dev/programme/delivery/3549.md
+++ b/dev/programme/delivery/3549.md
@@ -1 +1 @@
-- [#3549](https://github.com/tvofi/heatpump_optimizer/pull/3549) — **open**, R10-HOTFIX-OPENER-REFUSALS: open_pr.sh shares one body file across two runs, and ci_predict reads a stale roster ref (R10-HOTFIX-OPENER-REFUSALS)
+- [#3549](https://github.com/tvofi/heatpump_optimizer/pull/3549) — **merged `cfa8683`**, R10-HOTFIX-OPENER-REFUSALS: open_pr.sh shares one body file across two runs, and ci_predict reads a stale roster ref (R10-HOTFIX-OPENER-REFUSALS).
diff --git a/dev/programme/delivery/3554.md b/dev/programme/delivery/3554.md
index 8c6d8f8d39..2d2eff2c46 100644
--- a/dev/programme/delivery/3554.md
+++ b/dev/programme/delivery/3554.md
@@ -1 +1 @@
-- [#3554](https://github.com/tvofi/heatpump_optimizer/pull/3554) — **open**, roster: land the round-10 roster from handoff/audit-r10-roster ce60e992 (v7.1.15) (R10-ROSTER-BATCH24)
+- [#3554](https://github.com/tvofi/heatpump_optimizer/pull/3554) — **merged `e28a310`**, roster: land the round-10 roster from handoff/audit-r10-roster ce60e992 (v7.1.15).
diff --git a/dev/programme/delivery/3555.md b/dev/programme/delivery/3555.md
index 04eb95d993..4d785d436a 100644
--- a/dev/programme/delivery/3555.md
+++ b/dev/programme/delivery/3555.md
@@ -1 +1 @@
-- [#3555](https://github.com/tvofi/heatpump_optimizer/pull/3555) — **open**, roster: land the round-10 roster from handoff/audit-r10-roster b1697d36 (carry-201 entry 6 remeasure) (R10-ROSTER-BATCH24)
+- [#3555](https://github.com/tvofi/heatpump_optimizer/pull/3555) — **merged `154dbb4`**, roster: land the round-10 roster from handoff/audit-r10-roster b1697d36 (carry-201 entry 6 remeasure).
diff --git a/dev/programme/delivery/3557.md b/dev/programme/delivery/3557.md
new file mode 100644
index 0000000000..75c0acc522
--- /dev/null
+++ b/dev/programme/delivery/3557.md
@@ -0,0 +1 @@
+- [#3557](https://github.com/tvofi/heatpump_optimizer/pull/3557) — **open**, R10-HOTFIX-SELFTEST-SCOPE-TABLE: r10 hotfix selftest scope table (R10-HOTFIX-SELFTEST-SCOPE-TABLE)
diff --git a/dev/programme/delivery/3558.md b/dev/programme/delivery/3558.md
new file mode 100644
index 0000000000..ba59b6fa03
--- /dev/null
+++ b/dev/programme/delivery/3558.md
@@ -0,0 +1 @@
+- [#3558](https://github.com/tvofi/heatpump_optimizer/pull/3558) — **open**, R10-HOTFIX-TICK-BASH32: r10 hotfix tick bash32 (R10-HOTFIX-TICK-BASH32)
diff --git a/dev/programme/delivery/3559.md b/dev/programme/delivery/3559.md
new file mode 100644
index 0000000000..c2150aeb02
--- /dev/null
+++ b/dev/programme/delivery/3559.md
@@ -0,0 +1 @@
+- [#3559](https://github.com/tvofi/heatpump_optimizer/pull/3559) — **open**, record: delivery rows (autofix)
diff --git a/dev/programme/delivery/3564.md b/dev/programme/delivery/3564.md
new file mode 100644
index 0000000000..4c41327f7f
--- /dev/null
+++ b/dev/programme/delivery/3564.md
@@ -0,0 +1 @@
+- [#3564](https://github.com/tvofi/heatpump_optimizer/pull/3564) — **open**, R10-CONFIG-FLOW-TEXT-VERIFY: r10 config flow text verify (R10-CONFIG-FLOW-TEXT-VERIFY)
diff --git a/docs/architecture.md b/docs/architecture.md
index 779d4e609c..b8d322ea01 100644
--- a/docs/architecture.md
+++ b/docs/architecture.md
@@ -5,7 +5,7 @@ integration does rather than how it is built, start with
 [how-it-works.md](how-it-works.md).
 
 The shape is a thin Home Assistant layer wrapped around a much larger core that
-knows nothing about Home Assistant: 90 modules, of which 32 import the
+knows nothing about Home Assistant: 91 modules, of which 32 import the
 `homeassistant` package at module level, one more touches it inside a single
 function, and the rest take numbers in and give numbers back. The glue reads
 entity states, writes actuators and persists learned state. Keeping those two
@@ -126,6 +126,8 @@ custom_components/heatpump_optimizer/
 ├── optimizer.py          # The MPC solve: DHW by LP, space by L-BFGS-B, reason codes
 ├── plan_step.py          # The plan step: its width, and which step an instant
 │                         #   falls in, for the solve and the pump arbiter
+├── duty_legs.py          # The legs a step is served in, the switches between
+│                         #   them, and what a stop at one costs the plan
 ├── plan_slots.py         # A channel's step schedule as the heating slots a plan publishes
 ├── slot_drivers.py       # Why each step runs or idles: five signed driver weights,
 │                         #   and the current step's "why now" for the card
@@ -189,7 +191,8 @@ custom_components/heatpump_optimizer/
 ├── supply_hold.py        # The supply switch's minimum run and pause, held
 │                         #   across a re-solve, a cycle or a restart
 ├── duty_switch.py        # Learns per direction whether a duty switch stops
-│                         #   the running compressor; observes, changes nothing
+│                         #   the running compressor; a latched direction's
+│                         #   estimate is what the solve prices that switch by
 ├── heat_curve.py         # The heat-curve displace's outputs: the ECL110 MQTT
 │                         #   topics and an offset number entity
 ├── off_restore.py        # The one owner of the off and unload restore: what
@@ -270,7 +273,7 @@ custom_components/heatpump_optimizer/
 
 ## The Home Assistant boundary
 
-32 of the 90 modules import `homeassistant` at module level: `__init__`,
+32 of the 91 modules import `homeassistant` at module level: `__init__`,
 `config_flow`, `coordinator`, `open_meteo`, `frontend`, the six entity
 platforms `sensor`, `binary_sensor`, `button`, `climate`, `switch`, `datetime`,
 and the supporting modules `accuracy`, `away`, `boost`, `currency`, `debugger`, `defrost`,
@@ -279,7 +282,7 @@ and the supporting modules `accuracy`, `away`, `boost`, `currency`, `debugger`,
 reaches for `homeassistant.util.dt` inside a function, as the fallback when no
 clock function was injected.
 
-The other 57 modules are deliberately free of it, so each can be driven
+The other 58 modules are deliberately free of it, so each can be driven
 directly by `tests/features.py` with no Home Assistant running. That matters
 because the failure mode of this integration is a *plausible* plan: a detector
 that never fires, or a watchdog that lets a flatline through, produces output
diff --git a/docs/configuration.md b/docs/configuration.md
index 5aba0aca4a..d8ded8775a 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -658,6 +658,8 @@ are on **Power and solar sensors**; mode / defrost / online / fault are on
 |---|---|---|---|
 | Heat pump operating mode | from setup | the pump's mode entity | Read only unless **Pump duty control** is set to Control. Left empty, the optimizer assumes the pump can do everything. |
 | Pump duty control | Off | Off / Observe / Control | Whether the optimizer tells the pump which duty to serve on each plan step. See [Pump duty control](#pump-duty-control) below. |
+| Heating start hysteresis | none | `sensor` / `number` / `input_number`, K | Optional. The pump's own heating start hysteresis, a temperature difference; the heating floor's lift is never below it. |
+| Hot water start hysteresis | none | `sensor` / `number` / `input_number`, K | Optional. The pump's own hot water start hysteresis, a temperature difference; the plan places no charge on a tank at or above the hot water target less this. |
 | Defrosting | from setup | a binary sensor | On while the pump reverses to melt frost off the outdoor coil. |
 | Pump online | from setup | a binary sensor | On while the pump is actually reachable. |
 | Fault alarm | from setup | a binary sensor | On while the pump is reporting a fault. Only whether there is a fault is used. |
@@ -754,7 +756,7 @@ writes, at every 15-minute plan step:
     effect (the return target less the hysteresis) is input 10107 of its Smart Home Interface, which
     ha-luxtronik-shi publishes as its *Demand border* sensor
     ([the contributor's answers](https://github.com/tvofi/heatpump_optimizer/pull/3372#issuecomment-6756915104)).
-    This integration does not read it. On the install this was written for, a
+    The *Heating start hysteresis* option above takes the hysteresis itself; for a controller that publishes only this threshold, give it a template sensor of the return target minus the threshold. On the install this was written for, a
     0.5 K lift held 26–31 Hz once running, 1–1.5 K ramped to 73–81 Hz. For a low-temperature floor
     heating, 0.5–2 K and 30–40 °C may be a starting point; check them against the compressor's
     frequency and power.
@@ -894,6 +896,18 @@ writes, at every 15-minute plan step:
   disinfection temperature" notice does not fire on any hot water set-point
   the optimizer wrote; it still fires on a value set by anybody else, and,
   with *Control* off, on the pump's own set-point.
+- **The pump's start hysteresis, if you name it.** *Hot water start hysteresis*
+  (K): the pump starts a charge only once the tank is below its target less
+  this, so the plan places no charge on a warmer tank and buys what the hot
+  water minimum still needs at a step the pump will start; the step's target is
+  the disinfection temperature on a disinfection step and the hot water
+  set-point on any other. A charge planned for the current step is kept, as it
+  may already be running. A hot water minimum above the start temperature
+  cannot be held by such a pump: the plan shows the tank under it and a repair
+  notice says so. *Heating start hysteresis* (K): on a flow or return set-point
+  the lift over the measured water at the lowest planned level is never below
+  it. Both are temperature differences (K or °C as they stand, °F scaled, 0 to
+  20 K); left empty, nothing changes.
 - **Its own mode is not a pump limit.** A mode the optimizer wrote does not
   stop the next plan from heating the house or making hot water, even when the
   pump has not shown it yet or after a restart; one set by anybody else
@@ -902,7 +916,7 @@ writes, at every 15-minute plan step:
 **Observe** writes nothing. In *Observe* and *Control* the optimizer keeps a
 ledger of the last 24 hours: per 15-minute step, the duty the plan wanted
 against what the pump did, and a verdict — *delivered*, *space-instead*,
-*dhw-instead*, *idle-instead*, *unknown* or *baseline* (no plan duty). What the
+*dhw-instead*, *idle-instead*, *not-startable* (a hot-water step left idle on a tank at or above the pump's own start temperature), *unknown* or *baseline* (no plan duty). What the
 pump did is read from what the integration already reads: the **power
 entity** (running or not), the operating mode (*DHW (Hot Water)*) and the
 **tank temperature** (a rise of 0.5 °C over the step counts as hot water).
diff --git a/tests/block_duty.py b/tests/block_duty.py
index e837fc3227..139bd1601c 100644
--- a/tests/block_duty.py
+++ b/tests/block_duty.py
@@ -501,6 +501,7 @@ def main() -> int:
     )
 
     disinfection_checks()
+    hysteresis_checks()
     return R.close("BLOCK DUTY CHECKS")
 
 
@@ -776,5 +777,517 @@ def disinfection_checks() -> None:
     )
 
 
+def _hyst_snap(hysteresis=None, *, action=None, space=None, disinfecting=False, reading=55.0):
+    """``_dhw_snap`` (real parameters, a 0.1 step number) over a state with the pump's hysteresis."""
+    snap = _dhw_snap(action=action, disinfecting=disinfecting, reading=reading,
+                     attrs={"min": 30, "max": 75, "step": 0.1})
+    return replace(snap, state=SimpleNamespace(
+        room_temperature=21.0, outdoor_temperature=5.0, dhw_temperature=52.0,
+        dhw_start_hysteresis_k=hysteresis, space_start_hysteresis_k=space,
+    ))
+
+
+def _start_state(hysteresis, attrs=None):
+    """A ``ThermalState`` with the pump's hot-water hysteresis and, with ``attrs``, the grid of a
+    set-point number carrying them, read as the coordinator's input read reads it."""
+    from heatpump_optimizer import inputs as inputs_mod
+    from heatpump_optimizer.thermal_model import ThermalState
+
+    state = ThermalState()
+    hass = FakeHass({"sensor.h": FakeState("" if hysteresis is None else str(hysteresis), unit="K"),
+                     "number.dhw": FakeState("55", attributes=attrs or {})})
+    inputs_mod.read_start_hysteresis(state, hass, {
+        "dhw_hysteresis_entity": "sensor.h", "dhw_setpoint_entity": "number.dhw" if attrs else None})
+    return state
+
+
+def hysteresis_checks() -> None:
+    """The pump's own start hysteresis: read, planned, written and logged."""
+    import ast
+    import pathlib
+
+    import numpy as np
+
+    from heatpump_optimizer import dhw_planner as planner
+    from heatpump_optimizer import inputs as inputs_mod
+    from heatpump_optimizer import thermal_model as tm
+
+    # 1. The reading is a temperature difference.
+    hass = FakeHass({
+        "sensor.k2": FakeState("2", unit="K"), "sensor.f9": FakeState("9", unit="\u00b0F"),
+        "sensor.c3": FakeState("3", unit="\u00b0C"), "sensor.nu": FakeState("4"),
+        "sensor.k20": FakeState("20", unit="K"), "sensor.k0": FakeState("0", unit="K"),
+        "sensor.big": FakeState("25"), "sensor.neg": FakeState("-1"),
+        "sensor.na": FakeState("unavailable"), "sensor.pct": FakeState("2", unit="%"),
+    })
+    read = lambda e: inputs_mod.read_temperature_delta_k(hass, e)  # noqa: E731
+    check("a hysteresis in K reads as it stands", lambda: read("sensor.k2") == 2.0)
+    check("a hysteresis in degF is scaled by 5/9, not offset", lambda: abs(read("sensor.f9") - 5.0) < 1e-9)
+    check("a hysteresis in degC reads as it stands", lambda: read("sensor.c3") == 3.0)
+    check("a hysteresis with no unit is taken as K", lambda: read("sensor.nu") == 4.0)
+    check("the bounds of the hysteresis range, 20 K and 0 K, are readings",
+          lambda: read("sensor.k20") == 20.0 and read("sensor.k0") == 0.0
+          and inputs_mod.TEMPERATURE_DELTA_MAX_K == 20.0)
+    check("a hysteresis outside 0 to 20 K, unavailable, in a non-temperature unit, unset or unknown is no reading",
+          lambda: read("sensor.big") is None and read("sensor.neg") is None
+          and read("sensor.na") is None and read("sensor.pct") is None
+          and read(None) is None and read("sensor.nowhere") is None)
+
+    # 2. One lift.
+    lift = tm.start_flow_min_lift_k
+    half = {"flow_min_lift_k": 0.5}
+    check("a heating hysteresis above the configured lift is the lift",
+          lambda: lift(half, 2.0) == 2.0 and lift({}, 7.0) == 7.0)
+    check("a heating hysteresis at or below the configured lift, or none, leaves the configured lift",
+          lambda: lift(half, None) == 0.5 and lift(half, 0.3) == 0.5 and lift(half, 0.0) == 0.5
+          and lift({}, None) == tm.FLOW_MIN_LIFT_K)
+    check("null control: no hysteresis gives configured_flow_min_lift_k exactly",
+          lambda: all(lift(c, None) == tm.configured_flow_min_lift_k(c)
+                      for c in ({}, half, {"flow_min_lift_k": 0.0}, {"flow_min_lift_k": "x"}, None)))
+
+    # 3. The start temperature.
+    below = tm.dhw_start_below_c
+    check("the start temperature is the target less the hysteresis",
+          lambda: below(55, 4) == 51.0)
+    check("no target, or a hysteresis that is missing, zero or negative, is no start temperature",
+          lambda: below(55, None) is None and below(55, 0) is None and below(55, -1) is None
+          and below(None, 4) is None)
+
+    check("a hysteresis under one kelvin is still a start condition",
+          lambda: tm.dhw_start_below_c(55.0, 0.5) == 54.5)
+
+    # 4. The step targets, on real parameters.
+    cyc = ThermalParameters(dhw_setpoint=55.0, dhw_legionella_temp=60.0, dhw_legionella_enabled=True)
+    nocyc = ThermalParameters(dhw_setpoint=55.0, dhw_legionella_temp=60.0, dhw_legionella_enabled=False)
+    check("precondition: the cycle is 60 over a 55 set-point, and absent where disabled",
+          lambda: cyc.dhw_cycle_temp == 60.0 and nocyc.dhw_cycle_temp is None)
+    check("the step target is the everyday set-point, or the cycle's on a cycle step",
+          lambda: tm.dhw_step_target_c(cyc, False) == 55.0 and tm.dhw_step_target_c(cyc, True) == 60.0)
+    check("null control: with no cycle active a cycle step holds the everyday set-point",
+          lambda: tm.dhw_step_target_c(nocyc, True) == 55.0)
+    check("each step's start temperature is its own target less the hysteresis, the cycle step the cycle's",
+          lambda: list(planner.dhw_start_temps(cyc, _start_state(4.0), 6, 3)) == [51, 51, 51, 56, 51, 51]
+          and list(planner.dhw_start_temps(cyc, _start_state(4.0), 6, None)) == [51.0] * 6)
+    check("a cycle on the first step is judged against its own target; one past the horizon moves no step",
+          lambda: list(planner.dhw_start_temps(cyc, _start_state(4.0), 3, 0)) == [56, 51, 51]
+          and list(planner.dhw_start_temps(cyc, _start_state(4.0), 3, 3)) == [51, 51, 51]
+          and list(planner.dhw_start_temps(cyc, _start_state(4.0), 3, 2)) == [51, 51, 56])
+    check("with no or zero hysteresis no step has a start temperature",
+          lambda: planner.dhw_start_temps(cyc, _start_state(None), 6, 3) is None
+          and planner.dhw_start_temps(cyc, _start_state(0.0), 6, 3) is None
+          and planner.dhw_start_temps(cyc, _start_state(0.0, _step(5)), 6, 3) is None)
+
+    # 5. One owner of the target: what the arbiter writes.
+    check("the arbiter writes dhw_step_target_c: the everyday set-point with no cycle booked",
+          lambda: arb._dhw_write(_hyst_snap(4.0)) == tm.dhw_step_target_c(cyc, False))
+    check("the arbiter writes dhw_step_target_c: the cycle's temperature on a booked legionella step",
+          lambda: arb._dhw_write(_hyst_snap(4.0, action={"dhw_reason": "legionella"}))
+          == tm.dhw_step_target_c(cyc, True) == 60.0)
+
+    # 5b. One owner, read by the write: the two values, the two bounds and the entity's step.
+    hot = ThermalParameters(dhw_setpoint=72.0, dhw_legionella_temp=60.0, dhw_legionella_enabled=False)
+    hot_cycle = ThermalParameters(dhw_setpoint=55.0, dhw_legionella_temp=72.0, dhw_legionella_enabled=True)
+    check("the everyday step target never exceeds the charge limit (dhw_max_temp, 70 over a 72 set-point)",
+          lambda: hot.dhw_max_temp == 70.0 and tm.dhw_step_target_c(hot, False) == 70.0)
+    check("the cycle's step target never exceeds the tank's hard maximum (70 over a 72 disinfection temperature)",
+          lambda: hot_cycle.dhw_hard_max_temp == 70.0 and hot_cycle.dhw_cycle_temp == 72.0
+          and tm.dhw_step_target_c(hot_cycle, True) == 70.0)
+
+    def owner_gaps():
+        # Every write the arbiter makes against the owner handed the same entity's grid.
+        gaps = []
+        for step in (0.1, 0.5, 1, 5):
+            for configured in (55.0, 57.0, 58.0, 60.4, 72.0):
+                for disinfection in (50.0, 60.0, 60.3, 72.0):
+                    for cycle in (True, False):
+                        for booking in _BOOKINGS:
+                            snap = _dhw_snap(configured=configured, disinfection=disinfection, cycle=cycle,
+                                             attrs=_step(step), **booking)
+                            grid = inputs_mod.setpoint_grid(snap.hass, "number.dhw")
+                            on_cycle = bool(booking.get("disinfecting")) or bool(booking.get("action"))
+                            if arb._dhw_write(snap) != tm.dhw_step_target_c(snap.params, on_cycle, grid):
+                                gaps.append((step, configured, disinfection, cycle, booking))
+        return gaps
+
+    check("the arbiter's hot-water write is dhw_step_target_c on the entity's grid, over every step size, "
+          "set-point, disinfection temperature and booking", lambda: owner_gaps() == [])
+    write_names = {n.attr for n in ast.walk(next(
+        f for f in ast.parse(pathlib.Path("custom_components/heatpump_optimizer/pump_arbiter.py").read_text(
+            encoding="utf-8")).body if getattr(f, "name", "") == "_dhw_write")) if isinstance(n, ast.Attribute)}
+    check("_dhw_write states no value and no bound of its own: it names none of the four parameters",
+          lambda: not write_names & {"dhw_setpoint", "dhw_max_temp", "dhw_hard_max_temp", "dhw_cycle_temp"})
+    check("a set-point entity with no state has no grid, and the target is then the one before any step",
+          lambda: inputs_mod.setpoint_grid(FakeHass({}), "number.dhw") is None
+          and inputs_mod.setpoint_grid(FakeHass({}), None) is None
+          and tm.dhw_step_target_c(ThermalParameters(dhw_setpoint=58.0), False, None) == 58.0)
+
+    grid_of = inputs_mod.SetpointGrid
+    check("a grid holds a write at its caller's floor, which is no part of the entity's range, and at the "
+          "entity's minimum where that is higher",
+          lambda: grid_of("°C", 1.0, None, None).bounded(20.0, 25.0) == 25.0
+          and grid_of("°C", 1.0, 30.0, 65.0).bounded(20.0, 25.0) == 30.0
+          and grid_of("°C", 1.0, 30.0, 65.0).bounded(20.0, 35.0) == 35.0
+          and grid_of("°C", 1.0, None, None).bounded(20.0) == 20.0)
+
+    # 5c. The planner judges against what is written: a stepped entity.
+    stepped = ThermalParameters(dhw_setpoint=58.0, dhw_legionella_temp=62.0, dhw_legionella_enabled=True)
+    five = _dhw_snap(configured=58.0, disinfection=62.0, attrs=_step(5))
+    five_cycle = _dhw_snap(configured=58.0, disinfection=62.0, attrs=_step(5), disinfecting=True)
+    check("precondition: an everyday 58 on a 5 degC step is written 55, its cycle of 62 written 60",
+          lambda: arb._dhw_write(five) == 55.0 and arb._dhw_write(five_cycle) == 60.0)
+    check("on a stepped entity each step's start temperature is the written target less the hysteresis",
+          lambda: list(planner.dhw_start_temps(stepped, _start_state(4.0, _step(5)), 4, 2))
+          == [arb._dhw_write(five) - 4.0] * 2 + [arb._dhw_write(five_cycle) - 4.0, arb._dhw_write(five) - 4.0]
+          == [51.0, 51.0, 56.0, 51.0])
+    check("null control: with no set-point entity the same parameters start below 58 and 62 less the hysteresis",
+          lambda: list(planner.dhw_start_temps(stepped, _start_state(4.0), 4, 2)) == [54.0, 54.0, 58.0, 54.0])
+    check("the ledger's start temperature on the stepped entity is the planner's",
+          lambda: arb._dhw_start_below_c(replace(five, state=_start_state(4.0, _step(5)))) == 51.0
+          and arb._dhw_start_below_c(replace(five_cycle, state=_start_state(4.0, _step(5)))) == 56.0)
+
+    # 6. Which steps the pump starts.
+    startable = planner.startable_steps
+    check("a step is startable where it opens on a tank below its start temperature or follows a charge under way",
+          lambda: list(startable(np.array([0, 0, 1, 0, 0.]), np.array([54, 52, 50, 53, 50.9, 50.]),
+                                 np.full(5, 51.0))) == [False, False, True, True, True])
+    check("a tank exactly at the start temperature, not charging, does not start",
+          lambda: list(startable(np.zeros(2), np.array([51.0, 51.0, 51.0]), np.full(2, 51.0)))
+          == [False, False])
+
+    warm = np.array([54.0, 55.0, 54.0, 53.0, 52.0])
+    check("the step after a charge kept at the first step continues it; the kept step itself is not added to",
+          lambda: list(startable(np.array([1.0, 0.0, 0.0, 0.0]), warm, np.full(4, 51.0)))
+          == [False, True, False, False])
+    check("a charge begun after the first step on a warm tank is one the pump does not start: neither its "
+          "steps nor the step after it are startable",
+          lambda: list(startable(np.array([0.0, 1.0, 1.0, 0.0]), warm, np.full(4, 51.0))) == [False] * 4)
+    check("a charge the pump starts carries on: every step of it after the first, and the step after it",
+          lambda: list(startable(np.array([0.0, 1.0, 1.0, 0.0]), np.array([54.0, 50.0, 53.0, 55.0, 54.0]),
+                                 np.full(4, 51.0))) == [False, True, True, True])
+    check("a charge the pump did not start is under way from the step that opens below the start temperature",
+          lambda: list(startable(np.array([0.0, 1.0, 1.0, 1.0, 0.0]), np.array([54.0, 53.0, 50.0, 53.0, 54.0]),
+                                 np.full(5, 51.0))) == [False, False, True, True, True])
+    check("with no start condition every step is startable",
+          lambda: list(startable(np.zeros(3), np.array([60.0, 60.0, 60.0]), None)) == [True] * 3)
+
+    # 7. Dropping the charges the pump would not start.
+    def temps_of(plan):
+        # 1 K lost per step, 3 K gained per charging step, from 54 degC.
+        out = [54.0]
+        for p in plan:
+            out.append(out[-1] - 1.0 + (3.0 if p > 0 else 0.0))
+        return np.array(out)
+
+    plan = np.array([1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0])
+    kept = plan.copy()
+    drop = planner.drop_unstartable
+    check("a charge begun above its start temperature is dropped whole; the first step and a cooled tank's run are kept",
+          lambda: list(drop(plan, np.full(8, 51.0), temps_of)) == [1, 0, 0, 0, 0, 0, 0, 1])
+    check("a tank exactly at the start temperature does not start",
+          lambda: list(drop(np.array([0.0, 0.0, 1.0]), np.full(3, 52.0),
+                            lambda p: np.array([54.0, 53.0, 52.0, 55.0]))) == [0, 0, 0])
+    check("a run is judged against its own step's start temperature (a disinfection step's is higher)",
+          lambda: list(drop(plan, np.where(np.arange(8) == 2, 56.0, 51.0), temps_of))
+          == [1, 0, 1, 1, 0, 0, 0, 0])
+    check("dropping unstartable charges does not mutate its input", lambda: np.array_equal(plan, kept))
+    check("a run that begins at the second step on a warm tank is dropped",
+          lambda: list(drop(np.array([0.0, 1.0, 0.0]), np.full(3, 51.0), temps_of)) == [0, 0, 0])
+    check("a run at the first step is kept on a warm tank, with nothing planned at the horizon's end",
+          lambda: list(drop(np.array([1.0, 0.0, 0.0]), np.full(3, 51.0), temps_of)) == [1, 0, 0])
+
+    # 8. The repair loop.
+    def raises(_plan):
+        raise AssertionError("temps_of must not be read")
+
+    marker = np.array([0.0, 1.0])
+    check("with no start temperature the repair's own answer stands and no trajectory is read",
+          lambda: planner.place_startable(plan, None, raises, lambda plan: marker) is marker)
+    calls, original = [], plan
+
+    def stubborn(plan, start_below):
+        calls.append(1)
+        return original.copy()
+
+    check("a repair that keeps re-placing the unstartable plan still leaves a plan with none, in bounded rounds",
+          lambda: list(planner.place_startable(plan, np.full(8, 51.0), temps_of, stubborn))
+          == list(drop(plan, np.full(8, 51.0), temps_of))
+          and 1 <= len(calls) <= planner.STARTABLE_ROUNDS)
+    rounds = []
+
+    def counting(plan, start_below):
+        rounds.append(1)
+        return plan
+
+    planner.place_startable(plan, np.full(8, 51.0), temps_of, counting)
+    check("a repair that changes nothing ends the loop: one round to drop, one to see the plan stand",
+          lambda: len(rounds) == 2)
+    turns = []
+
+    def restless(plan, start_below):
+        # Never the plan it was handed: step 4 flips on every call.
+        turns.append(1)
+        out = original.copy()
+        out[4] = float(len(turns) % 2)
+        return out
+
+    settled = planner.place_startable(plan, np.full(8, 51.0), temps_of, restless)
+    check("a repair that never settles is asked the documented eight rounds, and what leaves still holds no unstartable charge",
+          lambda: planner.STARTABLE_ROUNDS == 8 and len(turns) == 8
+          and np.array_equal(settled, drop(settled, np.full(8, 51.0), temps_of)))
+    check("an identity repair leaves the dropped plan",
+          lambda: list(planner.place_startable(plan, np.full(8, 51.0), temps_of, lambda plan, start_below: plan))
+          == list(drop(plan, np.full(8, 51.0), temps_of)))
+
+    # 8b. The clamp-then-zero step the placement stages share.
+    from heatpump_optimizer.dhw_planner import DhwPlanner
+    floor_kw = 1.0
+    handed = np.array([floor_kw, floor_kw - 1e-9, floor_kw - 2e-9, 0.4, 0.0])
+    clamp_ctx = SimpleNamespace(outdoor_temps=None, dt=0.25, humidity=None, tank_exo_kw=None,
+                                min_run_power=floor_kw)
+    clamp_self = SimpleNamespace(_clamp_dhw_to_capacity=lambda *args: handed.copy())
+    check("a step the capacity clamp leaves below a runnable block is zeroed; one on the block, to the 1e-9 the rule allows, is kept",
+          lambda: list(DhwPlanner._ctx_clamp(clamp_self, clamp_ctx, 50.0, None, None, np.ones(5)))
+          == [floor_kw, floor_kw - 1e-9, 0.0, 0.0, 0.0])
+
+    # 9. End to end, on the real optimizer.
+    solved = {}
+
+    def solve(hysteresis):
+        if hysteresis not in solved:
+            solved[hysteresis] = _solve_winter_mild(hysteresis)
+        return solved[hysteresis]
+
+    def late_runs(hysteresis):
+        sched, temps = solve(hysteresis)
+        on = sched > 0.0
+        return sum(1 for i in range(1, on.size) if on[i] and not on[i - 1] and temps[i] >= 51.0)
+
+    check("precondition: with no hysteresis the plan begins a charge on a tank at or above 51 degC",
+          lambda: late_runs(None) > 0)
+    check("with a 4 K hysteresis no planned charge after step 0 begins at or above 51 degC",
+          lambda: late_runs(4.0) == 0)
+    check("null control: a zero hysteresis plans exactly as none",
+          lambda: np.array_equal(solve(0.0)[0], solve(None)[0]))
+
+    def under_floor(hysteresis):
+        # Degree-steps of the simulated tank under the 45 degC minimum.
+        return float(np.clip(45.0 - solve(hysteresis)[1], 0.0, None).sum())
+
+    check("what the start condition bars is re-bought where the pump starts: the tank is no further "
+          "under its minimum with a 4 K hysteresis than with none",
+          lambda: under_floor(4.0) <= under_floor(None) + 0.5)
+
+    def stepped_late(attrs):
+        # Everyday 58 on the entity's grid (5 degC: written 55, start below 51 with 4 K).
+        sched, temps = _solve_winter_mild(4.0, setpoint_c=58.0, attrs=attrs)
+        on = sched > 0.0
+        return sum(1 for i in range(1, on.size) if on[i] and not on[i - 1] and temps[i] >= 51.0)
+
+    check("precondition: judged against the unstepped 58, the plan begins a charge at or above the 51 degC "
+          "a 5 degC entity's pump starts below", lambda: stepped_late(None) > 0)
+    check("handed the 5 degC entity's grid, no planned charge after step 0 begins at or above 51 degC",
+          lambda: stepped_late(_step(5)) == 0)
+
+    pinned_plan, pinned_temps = _solve_winter_mild(None, dhw_pins=np.ones(96))
+    check("a day with hot water pinned on at every step is still held to the tank's charge limit of 55 degC",
+          lambda: float(pinned_temps.max()) <= 55.0 + 0.05 and int((pinned_plan > 0.0).sum()) < 96)
+
+    # 10. The ledger.
+    def held_row(snap):
+        held = arb.ArbiterState()
+        arb._observe(held, snap, "dhw", NOW)
+        return held.step
+
+    check("the ledger's start temperature is the written set-point less the hysteresis",
+          lambda: held_row(_hyst_snap(4.0))["start_below"] == 51.0)
+    check("the ledger's start temperature on a booked cycle step is the cycle's less the hysteresis",
+          lambda: held_row(_hyst_snap(4.0, action={"dhw_reason": "legionella"}))["start_below"] == 56.0)
+    check("null control: with no hysteresis read the ledger has no start temperature",
+          lambda: held_row(_hyst_snap(None))["start_below"] is None)
+    row = {"start": NOW, "planned": "dhw", "tank": 52.0, "measured": True, "ran": False,
+           "dhw_mode": False, "start_below": 51.0}
+
+    def verdict(tank=52.0, **over):
+        return arb._verdict({**row, "tank": tank, **over}, tank)["verdict"]
+
+    check("an idle hot water step on a tank above the start temperature is not-startable",
+          lambda: verdict() == "not-startable")
+    check("an idle hot water step on a tank exactly at the start temperature is not-startable",
+          lambda: verdict(51.0) == "not-startable")
+    check("an idle hot water step on a tank below the start temperature is idle-instead",
+          lambda: verdict(50.0) == "idle-instead")
+    check("an idle hot water step with no start temperature, or a row without the key, is idle-instead",
+          lambda: verdict(start_below=None) == "idle-instead"
+          and arb._verdict({k: v for k, v in row.items() if k != "start_below"}, 52.0)["verdict"]
+          == "idle-instead")
+    check("a planned both step idle above the start temperature is idle-instead",
+          lambda: verdict(planned="both") == "idle-instead")
+    check("a hot water step that ran the space pump on a warm tank is space-instead",
+          lambda: verdict(ran=True) == "space-instead")
+
+    def unwritten(**kwargs):
+        snap = _hyst_snap(4.0, **kwargs)
+        return replace(snap, config={k: v for k, v in snap.config.items() if k != "dhw_setpoint_entity"})
+
+    check("with no set-point entity to write, the ledger's start is the plan step's target less the hysteresis",
+          lambda: arb._dhw_write(unwritten()) is None
+          and arb._dhw_start_below_c(unwritten()) == 51.0
+          and arb._dhw_start_below_c(unwritten(action={"dhw_reason": "legionella"})) == 56.0
+          and arb._dhw_start_below_c(unwritten(disinfecting=True)) == 56.0)
+
+    # 11. The heating write at the modulation floor.
+    def floor_write(config, state):
+        full = {"flow_heat_c": 48.0, "space_setpoint_entity": "number.flow",
+                "heat_pump_return_temp_entity": "sensor.ret", **config}
+        states = {"number.flow": FakeState("40", attributes={"min": 20, "max": 70, "step": 0.1}),
+                  "sensor.ret": FakeState("27.0", unit="\u00b0C")}
+        at = datetime(2026, 1, 10, 6, 0, tzinfo=UTC)
+        return arb._flow_target(SimpleNamespace(
+            config=full, hass=FakeHass(states), state=state, thermal=SimpleNamespace(params=None),
+            params=SimpleNamespace(min_electrical_power=1.5, max_electrical_power=5.5),
+            plan=SimpleNamespace(timestamps=[at], power_schedule=[1.5]), action=None,
+        ), "space", at)
+
+    def heat_state(**kw):
+        return SimpleNamespace(outdoor_temperature=0.0, buffer_tank_temperature=40.0,
+                               floor_return_temperature=None, **kw)
+
+    lifted = {"flow_min_lift_k": 0.5}
+    bare = floor_write(lifted, heat_state())
+    check("precondition: the floor write is the return plus the configured lift",
+          lambda: abs(bare - 27.5) < 1e-9)
+    check("a heating hysteresis above the lift moves the floor write to return + hysteresis",
+          lambda: abs(floor_write(lifted, heat_state(space_start_hysteresis_k=2.0)) - bare - 1.5) < 1e-9
+          and abs(floor_write(lifted, heat_state(space_start_hysteresis_k=2.0)) - 29.0) < 1e-9)
+    check("null control: a hysteresis below the lift, or none, writes what a state without the attribute writes",
+          lambda: floor_write(lifted, heat_state(space_start_hysteresis_k=0.3)) == bare
+          and floor_write(lifted, heat_state(space_start_hysteresis_k=None)) == bare)
+
+    # 12. The lift has one owner.
+    root = pathlib.Path("custom_components/heatpump_optimizer")
+    stray, bad_calls, sites = [], [], 0
+    for path in sorted(root.glob("*.py")):
+        tree = ast.parse(path.read_text(encoding="utf-8"))
+        for node in ast.walk(tree):
+            names = {getattr(node, "id", None), getattr(node, "attr", None)}
+            if isinstance(node, (ast.Import, ast.ImportFrom)):
+                names |= {a.name.split(".")[-1] for a in node.names}
+            if "configured_flow_min_lift_k" in names and path.name != "thermal_model.py":
+                stray.append(path.name)
+            if path.name == "thermal_model.py" or not isinstance(node, ast.Call):
+                continue
+            fn = node.func
+            if (getattr(fn, "id", None) or getattr(fn, "attr", None)) != "modulation_floor_flow_c":
+                continue
+            sites += 1
+            third = node.args[2] if len(node.args) > 2 else next(
+                (k.value for k in node.keywords if k.arg == "lift_k"), None)
+            callee = None if not isinstance(third, ast.Call) else (
+                getattr(third.func, "id", None) or getattr(third.func, "attr", None))
+            if callee != "start_flow_min_lift_k":
+                bad_calls.append((path.name, node.lineno))
+    check("precondition: the census finds a call of modulation_floor_flow_c outside thermal_model",
+          lambda: sites >= 1)
+    check("configured_flow_min_lift_k is referenced by no module but its owner",
+          lambda: not stray)
+    check("every floor call outside thermal_model takes its lift from start_flow_min_lift_k",
+          lambda: not bad_calls)
+
+    # 13. The hot water minimum above the start temperature.
+    def raised(floor, entity="sensor.h", cycle=False, through=None, enabled=True, setpoint=55.0, attrs=None,
+               hysteresis="4"):
+        hass = FakeHass({"sensor.h": FakeState(hysteresis, unit="K"),
+                         "number.dhw": FakeState("55", attributes=attrs or {})})
+        params = ThermalParameters(dhw_setpoint=setpoint, dhw_legionella_temp=60.0, dhw_enabled=enabled,
+                                   dhw_legionella_enabled=cycle, dhw_min_temp=floor)
+        config = {"dhw_hysteresis_entity": entity} if entity else {}
+        if attrs:
+            config["dhw_setpoint_entity"] = "number.dhw"
+        if through is None:
+            setpoint_check._dhw_start(hass, config, params)
+        else:
+            through(SimpleNamespace(hass=hass, effective_config=config, thermal_params=params))
+        return [i for i in getattr(hass, "issues", []) if i[1] == setpoint_check.ISSUE_DHW_START]
+
+    check("a minimum above the start temperature raises dhw_minimum_above_start with its figures",
+          lambda: setpoint_check.ISSUE_DHW_START == "dhw_minimum_above_start"
+          and len(raised(52.0)) == 1
+          and raised(52.0)[0][2]["translation_placeholders"]
+          == {"floor": "52.0", "start": "51.0", "target": "55.0", "hysteresis": "4.0"})
+    check("the start temperature is the everyday target's even with a disinfection cycle active",
+          lambda: len(raised(52.0, cycle=True)) == 1
+          and raised(52.0, cycle=True)[0][2]["translation_placeholders"]["target"] == "55.0")
+    check("the set-point check's own entry raises it: evaluate() reaches the start notice",
+          lambda: len(raised(52.0, through=setpoint_check.evaluate)) == 1)
+    check("a minimum below the start temperature raises nothing", lambda: raised(45.0) == [])
+    check("a minimum exactly at the start temperature raises nothing", lambda: raised(51.0) == [])
+    check("with no hysteresis entity configured a minimum of 52 raises nothing",
+          lambda: raised(52.0, entity=None) == [])
+
+    check("with hot water disabled no minimum raises it, whatever the hysteresis reads",
+          lambda: raised(52.0, enabled=False) == [] and raised(45.0, enabled=False, hysteresis="20") == []
+          and len(raised(45.0, hysteresis="20")) == 1)
+    check("the notice judges the written target: an everyday 58 on a 5 degC step starts below 51, not 54",
+          lambda: len(raised(52.0, setpoint=58.0, attrs=_step(5))) == 1
+          and raised(52.0, setpoint=58.0, attrs=_step(5))[0][2]["translation_placeholders"]
+          == {"floor": "52.0", "start": "51.0", "target": "55.0", "hysteresis": "4.0"}
+          and raised(52.0, setpoint=58.0) == [])
+
+    # 14. The coordinator reads both into the state.
+    def read_state(config):
+        from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
+        h = FakeHass({"sensor.dh": FakeState("4", unit="K"), "sensor.sh": FakeState("2", unit="K"),
+                      "number.dhw": FakeState("55", attributes=_step(5)),
+                      "sensor.indoor": FakeState("21.4"), "sensor.outdoor": FakeState("-3.0")})
+        coord = HeatPumpOptimizerCoordinator(h, FakeEntry(data={
+            "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor", **config}))
+        asyncio.run(coord._update_current_state())
+        return coord._current_state
+
+    both = read_state({"dhw_hysteresis_entity": "sensor.dh", "space_hysteresis_entity": "sensor.sh"})
+    none = read_state({})
+    check("the coordinator's input read puts both hysteresis sensors into the state",
+          lambda: both.dhw_start_hysteresis_k == 4.0 and both.space_start_hysteresis_k == 2.0)
+    check("null control: with neither entity configured both state fields are None",
+          lambda: none.dhw_start_hysteresis_k is None and none.space_start_hysteresis_k is None)
+    gridded = read_state({"dhw_setpoint_entity": "number.dhw"})
+    check("the coordinator's input read puts the hot-water set-point entity's grid into the state",
+          lambda: gridded.dhw_setpoint_grid == inputs_mod.setpoint_grid(
+              FakeHass({"number.dhw": FakeState("55", attributes=_step(5))}), "number.dhw")
+          and gridded.dhw_setpoint_grid.step == 5.0 and none.dhw_setpoint_grid is None)
+
+
+def _solve_winter_mild(hysteresis, dhw_pins=None, setpoint_c=None, attrs=None):
+    """The 24 h solve of ``dev/audit/harnesses/r10_dhw_start_hysteresis.py`` (winter_typical, winter_mild, 53 degC)."""
+    import numpy as np
+    from profiles import house, prices, solve_inputs, weather
+    from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
+    from heatpump_optimizer.thermal_model import ThermalModel, ThermalState
+
+    begin = datetime(2026, 1, 15, 0, 0)
+    cfg = house()
+    params = ThermalParameters.from_config(cfg)
+    params.dhw_enabled = True
+    if setpoint_c is not None:
+        params.dhw_setpoint = setpoint_c
+    opt = HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(
+        horizon_hours=24, time_step_minutes=15, target_temp=cfg["target_temperature"],
+        min_temp=cfg["min_temperature"], max_temp=cfg["max_temperature"]))
+    outdoor, wind, rain, sun = weather("winter_mild", begin)
+    state = ThermalState(
+        room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=float(outdoor[0]),
+        dhw_temperature=53.0, dhw_hours_since_legionella=20.0, upper_floor_temperature=21.0,
+        lower_floor_temperature=21.0, buffer_tank_temperature=40.0)
+    state.dhw_start_hysteresis_k = hysteresis
+    if attrs:
+        state.dhw_setpoint_grid = _start_state(hysteresis, attrs).dhw_setpoint_grid
+    result = opt.optimize(inputs=solve_inputs(
+        initial_state=state, prices=np.asarray(prices("winter_typical", begin), dtype=float),
+        outdoor_temps=outdoor, wind_speeds=wind, precipitation=rain, solar_radiation=sun,
+        start_time=begin, dhw_pins=dhw_pins))
+    return (np.asarray(result.dhw_power_schedule, dtype=float),
+            np.asarray(result.dhw_temp_trajectory, dtype=float))
+
+
 if __name__ == "__main__":
     raise SystemExit(main())
diff --git a/tests/closures.json b/tests/closures.json
index 2908999177..84537ffb10 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -208,6 +208,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -315,6 +316,7 @@
    "custom_components/heatpump_optimizer/dhw_schedule.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/freq_control.py",
@@ -324,6 +326,7 @@
    "custom_components/heatpump_optimizer/mixing_valve.py",
    "custom_components/heatpump_optimizer/optimizer.py",
    "custom_components/heatpump_optimizer/payload.py",
+   "custom_components/heatpump_optimizer/plan_step.py",
    "custom_components/heatpump_optimizer/pv.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/tariff.py",
@@ -350,23 +353,32 @@
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
+   "custom_components/heatpump_optimizer/binary_sensor.py",
    "custom_components/heatpump_optimizer/boost.py",
+   "custom_components/heatpump_optimizer/button.py",
+   "custom_components/heatpump_optimizer/climate.py",
    "custom_components/heatpump_optimizer/comfort_band.py",
    "custom_components/heatpump_optimizer/comfort_learning.py",
+   "custom_components/heatpump_optimizer/config_flow.py",
    "custom_components/heatpump_optimizer/const.py",
    "custom_components/heatpump_optimizer/coordinator.py",
    "custom_components/heatpump_optimizer/currency.py",
    "custom_components/heatpump_optimizer/curve_learning.py",
+   "custom_components/heatpump_optimizer/datetime.py",
+   "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
+   "custom_components/heatpump_optimizer/device_prefill.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
+   "custom_components/heatpump_optimizer/diagnostics.py",
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -375,6 +387,7 @@
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
+   "custom_components/heatpump_optimizer/frontend.py",
    "custom_components/heatpump_optimizer/grid_fee.py",
    "custom_components/heatpump_optimizer/heat_curve.py",
    "custom_components/heatpump_optimizer/heat_energy.py",
@@ -387,7 +400,9 @@
    "custom_components/heatpump_optimizer/manual_plan.py",
    "custom_components/heatpump_optimizer/mixing_valve.py",
    "custom_components/heatpump_optimizer/modbus_prefill.py",
+   "custom_components/heatpump_optimizer/name_match.py",
    "custom_components/heatpump_optimizer/narrative.py",
+   "custom_components/heatpump_optimizer/notifier.py",
    "custom_components/heatpump_optimizer/off_restore.py",
    "custom_components/heatpump_optimizer/open_meteo.py",
    "custom_components/heatpump_optimizer/optimizer.py",
@@ -395,16 +410,22 @@
    "custom_components/heatpump_optimizer/plan_slots.py",
    "custom_components/heatpump_optimizer/plan_step.py",
    "custom_components/heatpump_optimizer/power_guard.py",
+   "custom_components/heatpump_optimizer/prefill_offer.py",
    "custom_components/heatpump_optimizer/presets.py",
    "custom_components/heatpump_optimizer/price_model.py",
    "custom_components/heatpump_optimizer/price_tiles.py",
+   "custom_components/heatpump_optimizer/process_worker.py",
    "custom_components/heatpump_optimizer/pump_arbiter.py",
    "custom_components/heatpump_optimizer/pump_mode.py",
    "custom_components/heatpump_optimizer/pump_schedule.py",
    "custom_components/heatpump_optimizer/pump_signals.py",
    "custom_components/heatpump_optimizer/pv.py",
+   "custom_components/heatpump_optimizer/quick_setup.py",
    "custom_components/heatpump_optimizer/quiet_windows.py",
    "custom_components/heatpump_optimizer/repairs.py",
+   "custom_components/heatpump_optimizer/replay_doc.py",
+   "custom_components/heatpump_optimizer/sensor.py",
+   "custom_components/heatpump_optimizer/services.py",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
@@ -444,7 +465,8 @@
    "tests/hastub/homeassistant/helpers/update_coordinator.py",
    "tests/hastub/homeassistant/loader.py",
    "tests/hastub/homeassistant/util/__init__.py",
-   "tests/hastub/homeassistant/util/dt.py"
+   "tests/hastub/homeassistant/util/dt.py",
+   "tests/profiles.py"
   ],
   "tests/boost_drift_replay.py": [
    "custom_components/heatpump_optimizer/__init__.py",
@@ -469,6 +491,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -571,6 +594,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -687,6 +711,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -805,6 +830,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -939,6 +965,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -1063,6 +1090,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -1199,6 +1227,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -1401,6 +1430,7 @@
    "custom_components/heatpump_optimizer/dhw_schedule.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/freq_control.py",
@@ -1410,6 +1440,7 @@
    "custom_components/heatpump_optimizer/mixing_valve.py",
    "custom_components/heatpump_optimizer/optimizer.py",
    "custom_components/heatpump_optimizer/payload.py",
+   "custom_components/heatpump_optimizer/plan_step.py",
    "custom_components/heatpump_optimizer/pv.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/tariff.py",
@@ -1520,6 +1551,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -2042,6 +2074,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -2238,6 +2271,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -2392,6 +2426,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -2535,6 +2570,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -2724,6 +2760,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -2892,6 +2929,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -3284,6 +3322,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -3402,6 +3441,7 @@
    "custom_components/heatpump_optimizer/dhw_schedule.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/freq_control.py",
@@ -3411,6 +3451,7 @@
    "custom_components/heatpump_optimizer/mixing_valve.py",
    "custom_components/heatpump_optimizer/optimizer.py",
    "custom_components/heatpump_optimizer/payload.py",
+   "custom_components/heatpump_optimizer/plan_step.py",
    "custom_components/heatpump_optimizer/pv.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/tariff.py",
@@ -3454,6 +3495,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -3557,6 +3599,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -3643,6 +3686,7 @@
    "custom_components/heatpump_optimizer/dhw_schedule.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/freq_control.py",
@@ -3652,6 +3696,7 @@
    "custom_components/heatpump_optimizer/mixing_valve.py",
    "custom_components/heatpump_optimizer/optimizer.py",
    "custom_components/heatpump_optimizer/payload.py",
+   "custom_components/heatpump_optimizer/plan_step.py",
    "custom_components/heatpump_optimizer/presets.py",
    "custom_components/heatpump_optimizer/pv.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
@@ -3707,6 +3752,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -3802,6 +3848,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -3876,6 +3923,7 @@
    "custom_components/heatpump_optimizer/dhw_schedule.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/freq_control.py",
@@ -3885,6 +3933,7 @@
    "custom_components/heatpump_optimizer/mixing_valve.py",
    "custom_components/heatpump_optimizer/optimizer.py",
    "custom_components/heatpump_optimizer/payload.py",
+   "custom_components/heatpump_optimizer/plan_step.py",
    "custom_components/heatpump_optimizer/pv.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/tariff.py",
@@ -3928,6 +3977,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -4207,8 +4257,11 @@
    "dev/audit/harnesses/r10_demand_overbook.py",
    "dev/audit/harnesses/r10_dhw_charge_settle_p90.py",
    "dev/audit/harnesses/r10_dhw_lift_law_grid.py",
+   "dev/audit/harnesses/r10_dhw_start_hysteresis.py",
+   "dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py",
    "dev/audit/harnesses/r10_diag_ages_export.py",
    "dev/audit/harnesses/r10_disinfection_setpoint.py",
+   "dev/audit/harnesses/r10_duty_switch_price_section.py",
    "dev/audit/harnesses/r10_duty_switch_section.py",
    "dev/audit/harnesses/r10_envmatrix_noremote.sh",
    "dev/audit/harnesses/r10_errexit_capture.py",
@@ -4316,6 +4369,7 @@
    "dev/audit/harnesses/r10_sav_actuation_phase.py",
    "dev/audit/harnesses/r10_sav_baseline.py",
    "dev/audit/harnesses/r10_sav_baseline_mutants.py",
+   "dev/audit/harnesses/r10_sav_held_capacity_census.py",
    "dev/audit/harnesses/r10_sav_null_settled.py",
    "dev/audit/harnesses/r10_sav_null_terms.py",
    "dev/audit/harnesses/r10_sav_receipt_render.py",
@@ -5124,7 +5178,7 @@
   },
   "tests/block_duty.py": {
    "rc": 0,
-   "seconds": 1.1
+   "seconds": 8.3
   },
   "tests/boost_drift_replay.py": {
    "rc": 0,
@@ -5140,7 +5194,7 @@
   },
   "tests/config_flow_steps.py": {
    "rc": 0,
-   "seconds": 29.8
+   "seconds": 32.5
   },
   "tests/debug_collect.py": {
    "rc": 0,
@@ -5160,7 +5214,7 @@
   },
   "tests/edge.py": {
    "rc": 0,
-   "seconds": 17.9
+   "seconds": 21.5
   },
   "tests/entities.py": {
    "rc": 0,
@@ -5172,7 +5226,7 @@
   },
   "tests/features.py": {
    "rc": 1,
-   "seconds": 531.8
+   "seconds": 1040.5
   },
   "tests/finite_boundary.py": {
    "rc": 0,
@@ -5184,7 +5238,7 @@
   },
   "tests/golden.py": {
    "rc": 0,
-   "seconds": 0.9
+   "seconds": 1.2
   },
   "tests/guard_pins.py": {
    "rc": 0,
@@ -5192,11 +5246,11 @@
   },
   "tests/ha_contract.py": {
    "rc": 0,
-   "seconds": 0.2
+   "seconds": 0.5
   },
   "tests/harness_headers.py": {
    "rc": 0,
-   "seconds": 118.2
+   "seconds": 274.5
   },
   "tests/layout.py": {
    "rc": 0,
@@ -5228,15 +5282,15 @@
   },
   "tests/stress.py": {
    "rc": 0,
-   "seconds": 443.5
+   "seconds": 463.0
   },
   "tests/structure.py": {
    "rc": 2,
-   "seconds": 14.0
+   "seconds": 51.2
   },
   "tests/typing_ruler.py": {
    "rc": 0,
-   "seconds": 0.4
+   "seconds": 33.9
   },
   "tests/validate.py": {
    "rc": 0,
@@ -5244,7 +5298,7 @@
   },
   "tests/wood_advisor.py": {
    "rc": 0,
-   "seconds": 0.6
+   "seconds": 1.3
   }
  }
 }
diff --git a/tests/config_flow_steps.py b/tests/config_flow_steps.py
index 724c499ec8..fc299dd87d 100644
--- a/tests/config_flow_steps.py
+++ b/tests/config_flow_steps.py
@@ -4500,6 +4500,9 @@ async def registry_walk_recurses():
         # #1067 again: the pump's own supply and return water, same page.
         const.CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY,
         const.CONF_HEAT_PUMP_RETURN_TEMP_ENTITY,
+        # The pump's own start hysteresis per duty.
+        const.CONF_SPACE_HYSTERESIS_ENTITY,
+        const.CONF_DHW_HYSTERESIS_ENTITY,
     }
     check(
         "registry",
diff --git a/tests/deployment_shape.py b/tests/deployment_shape.py
index 05ea531ba6..50d029db56 100644
--- a/tests/deployment_shape.py
+++ b/tests/deployment_shape.py
@@ -37,9 +37,10 @@ child from ``inspect.getfile``.
 
 COST OF THE SHAPE (#1218, round-5 D3-08). Materialising the shape copies the
 tracked package file by file (``_materialise``, below), and the gate's tracer
-records every read, so this lane's recorded closure is the package: all 109
+records every read, so this lane's recorded closure is the package: all 110
 files under ``custom_components/heatpump_optimizer/``, Python and non-Python
-alike (108 until the supply-hold PR's ``supply_hold.py``, 107 until
+alike (109 until R10-DUTY-SWITCH-PLANNER-PRICE's ``duty_legs.py``, 108 until the supply-hold PR's
+``supply_hold.py``, 107 until
 R10-DUTY-SWITCH-RESTART-LEARNING's ``duty_switch.py``, 78 until R9 F2.5's ``batchmath.py``, 79 until R9 UI-1's six brand
 images, 85 until R9 EG-B5's ``dhw_planner.py``, 86 until R9-EG-B3a's
 ``payload.py``, 87 until R9-UX-4's ``notifier.py``, 88 until R9-SW-1's
@@ -55,8 +56,8 @@ which drives the CI ratchet's archscore measurement and so opens the package
 the way this lane's recorder does. A diff touching any production file
 therefore selects this lane. That is a selection cost, not a
 duplicate-assertion one: the same
-recording finds 154 of the 528 script pairs (33 choose 2) sharing 0.80 or more
-of their production-module closure, all 154 among the 406 pairs whose two
+recording finds 162 of the 528 script pairs (33 choose 2) sharing 0.80 or more
+of their production-module closure, all 162 among the 406 pairs whose two
 scripts each have a non-empty production closure (``tests/arch_score.py``,
 ``tests/ha_contract.py``, ``tests/layout.py`` and ``tests/md_tables.mjs`` have none;
 ``tests/harness_headers.py`` joined the comparable set, and ten pairs, when
@@ -91,7 +92,15 @@ reads the catalogues, moved card.mjs with config_flow_steps.py from 0.800 to
 off_restore.py, read by every closure that imports the coordinator, moved it
 from 145 to 146; R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py, read by every
 closure that imports the arbiter, the sensor platform or the store, from 146 to 148; the supply-hold PR's
-supply_hold.py, read by every closure that imports the coordinator, from 148 to 154).
+supply_hold.py, read by every closure that imports the coordinator, from 148 to 154;
+R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py, read by every closure that
+imports the optimizer or the arbiter, left it at 154: measured alone on the
+148 recording it moves the same count to 154, the pairs it lifts being ones
+supply_hold.py lifts too; R10-OUTSIDE-DHW-START-HYSTERESIS's block_duty.py
+check that the coordinator's input read puts the pump's start hysteresis on
+the state builds a coordinator, which grew that script's closure from 74 to
+91 production files: nine pairs joined at the 0.80 floor and one left, the
+count from 154 to 162).
 Eighteen of the pairs sit at exactly 1.00 -- arch_score_head.py/deployment_shape.py,
 arch_score_head.py/entities.py and deployment_shape.py/entities.py
 (98 shared production files each), doc_claims.py/harness_headers.py
diff --git a/tests/doc_claims.py b/tests/doc_claims.py
index fed610afda..7dadc4197c 100644
--- a/tests/doc_claims.py
+++ b/tests/doc_claims.py
@@ -4728,7 +4728,7 @@ def flow_number_pins() -> list[tuple[str, str, float]]:
     """``(dotted key, regex with one number group, the production value)``."""
     import math
 
-    from heatpump_optimizer import const, curve_learning, flow_lift, thermal_model
+    from heatpump_optimizer import const, curve_learning, duty_legs, flow_lift, thermal_model
     from heatpump_optimizer import pump_arbiter as pa
 
     pins = [
@@ -4736,7 +4736,7 @@ def flow_number_pins() -> list[tuple[str, str, float]]:
         (_FLOW_DD, r"\((\d+) below -?\d+ °C outdoors\)", pa.COLD_LEASE_MINUTES),
         (_FLOW_DD, r"\(\d+ below (-?\d+) °C outdoors\)", pa.COLD_RAIL_C),
         (_FLOW_DD, r"sent again every (\d+) minutes", pa.RETRY_MINUTES),
-        (_FLOW_DD, r"a share under (\d+) minutes", pa.SPLIT_MIN_MINUTES),
+        (_FLOW_DD, r"a share under (\d+) minutes", duty_legs.SPLIT_MIN_MINUTES),
         (_FLOW_DD, r"the heating flow \((\d+) °C", pa.FLOW_HEAT_C),
         (_FLOW_DD, r"\((\d+) °C when none is configured\)", pa.FLOW_HOLD_C),
         (_FLOW_DD, r"(\d+) °C on steps that do not", pa.FLOW_GATE_C),
diff --git a/tests/features.py b/tests/features.py
index 97be3cc73f..a663d02b74 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -27662,6 +27662,45 @@ R.check(
     f"(solve, hub): config False -> {_dd_off!r}, default -> {_dd_default!r}",
 )
 
+# R10-DUTY-SWITCH-PLANNER-PRICE: and the duty-switch learner's read for the
+# planner, by the same copy.
+from heatpump_optimizer import duty_switch as _dsp_push_ds  # noqa: E402
+
+
+def _dsp_pushed(learner):
+    hass = FakeHass()
+    _seed_prices(hass)
+    entry = FakeEntry(data={**_LC_DATA}, entry_id="dsp_push")
+    _asyncio.run(_ha_setup_entry(_integ, hass, entry))
+    coord = entry.runtime_data
+    coord._prices = list(_svc_crash_coord._prices)
+    never = coord._solve_hubs(4, banded=True)[0]
+    _dsp_push_ds.record_for(coord).learner = learner
+    return never, coord._solve_hubs(4, banded=True)[0], coord._opt_config
+
+
+_dsp_push_d = _dsp_push_ds.Direction
+_dsp_push_day = datetime(2026, 11, 10, tzinfo=UTC).date()
+_dsp_push_l = _dsp_push_ds.DutySwitchLearner({
+    "dhw_space": _dsp_push_d(k=3.0, kept_w=1.0, first_day=_dsp_push_day, last_day=_dsp_push_day,
+                             usable=True, off_s=[400.0, 501.0, 620.0, 700.0]),
+    "space_dhw": _dsp_push_d(k=2.0, kept_w=2.0, first_day=_dsp_push_day, last_day=_dsp_push_day, usable=True),
+})
+_dsp_cfg_never, _dsp_cfg_read, _dsp_cfg_hub = _dsp_pushed(_dsp_push_l)
+R.check(
+    "the coordinator passes the learner's read to the solve's configuration "
+    "copy: zeros on a pump never arbitrated, both pairs once latched, and the "
+    "configured hub keeps its zeros",
+    (_dsp_cfg_never.duty_switch_stop_probability, _dsp_cfg_never.duty_switch_off_seconds)
+    == ((0.0, 0.0), (0.0, 0.0))
+    and (_dsp_cfg_read.duty_switch_stop_probability, _dsp_cfg_read.duty_switch_off_seconds)
+    == ((0.75, 0.5), (560.5, 0.0))
+    and _dsp_cfg_hub.duty_switch_stop_probability == (0.0, 0.0)
+    and _dsp_cfg_hub.duty_switch_off_seconds == (0.0, 0.0),
+    f"never {_dsp_cfg_never.duty_switch_stop_probability}, read "
+    f"{_dsp_cfg_read.duty_switch_stop_probability} {_dsp_cfg_read.duty_switch_off_seconds}",
+)
+
 _svc_sim_hass = FakeHass()
 _seed_prices(_svc_sim_hass)  # #924
 _svc_sim_entry = FakeEntry(data=_LC_DATA, entry_id="sim_pump")
@@ -66289,6 +66328,9 @@ _P6_READ_ONLY = {
         "heat_pump_dhw_booster_entity", "heat_pump_fault_entity",
         "heat_pump_online_entity",
     )},
+    **{key: "the pump's own start hysteresis, read_temperature_delta_k reads it" for key in (
+        hp_const.CONF_SPACE_HYSTERESIS_ENTITY, hp_const.CONF_DHW_HYSTERESIS_ENTITY,
+    )},
 }
 
 
@@ -83518,7 +83560,8 @@ from harness import FakeCoordinator as _DsFakeCoord, FakeEntry as _DsFakeEntry
 R.section("duty-switch restart learning, part A (design duty-switch-restart-learning)")
 # A hot water -> heating mode write while the compressor runs stops it on some
 # pumps (Bankaifan, pull request 3420). Part A observes, estimates, persists
-# and publishes; nothing reads the estimate. The learner is driven directly
+# and publishes; the planner's read of it is R10-DUTY-SWITCH-PLANNER-PRICE's
+# section. The learner is driven directly
 # with the install's own table, then through ``pump_arbiter.apply`` and the
 # listener ``duty_switch`` arms.
 _DS_T0 = datetime(2026, 1, 10, 0, 0, tzinfo=UTC)
@@ -84586,8 +84629,11 @@ R.check(
     and all(calls != [] for calls, _split in _ds_flat_runs[0]),
     f"{[split for _c, split in _ds_flat_runs[0]]} {[split for _c, split in _ds_flat_runs[1]]}",
 )
-# Both controls hold by construction: only the arbiter (which reports) and the
-# sensor (which publishes) name the module, and neither reads the estimate.
+# Both controls hold by construction: the arbiter (which reports) and the
+# sensor (which publishes) never read the estimate. Its one reader is the
+# coordinator, which hands the planner's read to a solve's configuration
+# (R10-DUTY-SWITCH-PLANNER-PRICE): the estimate reaches a write only through
+# the plan, and both controls hold the plan fixed.
 _ds_pkg = _DsPath("custom_components/heatpump_optimizer")
 _ds_readers = sorted(
     p.name for p in _ds_pkg.glob("*.py") if p.name != "duty_switch.py" and any(
@@ -84596,19 +84642,23 @@ _ds_readers = sorted(
 _ds_uses = sorted({
     n.attr for name in ("pump_arbiter.py", "sensor.py") for n in _ds_ast.walk(_ds_ast.parse((_ds_pkg / name).read_text()))
     if isinstance(n, _ds_ast.Attribute) and isinstance(n.value, _ds_ast.Name) and n.value.id == "duty_switch"})
+_ds_plan_uses = sorted(
+    n.attr for n in _ds_ast.walk(_ds_ast.parse((_ds_pkg / "coordinator.py").read_text()))
+    if isinstance(n, _ds_ast.Attribute) and isinstance(n.value, _ds_ast.Name) and n.value.id == "duty_switch")
 _ds_own = {n.module for n in _ds_ast.walk(_ds_ast.parse((_ds_pkg / "duty_switch.py").read_text()))
            if isinstance(n, _ds_ast.ImportFrom) and n.level == 1} | {
     a.name for n in _ds_ast.walk(_ds_ast.parse((_ds_pkg / "duty_switch.py").read_text()))
     if isinstance(n, _ds_ast.ImportFrom) and n.level == 1 and n.module is None for a in n.names}
 R.check(
-    "only the arbiter and the sensor name duty_switch, through its report, attach and publish calls and "
-    "never a read of the estimate; the module imports neither of them; the pure half of wear stays pure",
-    _ds_readers == ["pump_arbiter.py", "sensor.py"]
+    "the arbiter and the sensor name duty_switch through its report, attach and publish calls and never a "
+    "read of the estimate; the coordinator names it once, for the planner's read; the module imports none "
+    "of the three; the pure half of wear stays pure",
+    _ds_readers == ["coordinator.py", "pump_arbiter.py", "sensor.py"] and _ds_plan_uses == ["planner_fields"]
     and _ds_uses == ["Reader", "STOP_WINDOW_S", "SwitchContext", "attach", "detach", "note_mode_write", "note_pass", "record_for",
                      "starts_attributes"]
     and not _ds_own & {"pump_arbiter", "sensor", "coordinator"}
     and "homeassistant" not in (_ds_pkg / "wear.py").read_text(),
-    f"{_ds_readers} {_ds_uses} {_ds_own}",
+    f"{_ds_readers} {_ds_uses} {_ds_plan_uses} {_ds_own}",
 )
 # Published on the compressor-starts sensor, beside the counter, off the payload.
 from heatpump_optimizer import sensor as _ds_sensor  # noqa: E402
@@ -87095,6 +87145,154 @@ R.check(
 )
 
 
+# --- R10-SAV-VALUATION-RESIDUE: the reference held where its valve curve can hold it ---
+from profiles import house as _svh_house  # noqa: E402
+from heatpump_optimizer.optimizer import _thermostat_held_state as _svh_held  # noqa: E402
+from heatpump_optimizer.thermal_model import WeatherSeries as _SVH_WS  # noqa: E402
+
+_SVH_VALVE = {"mixing_valve_mode": "manual", "mixing_valve_target": 21.0,
+              "buffer_tank_volume": 750.0, "buffer_max_temperature": 56.0,
+              "heat_pump_max_power": 4.0}
+
+
+def _svh_case(two_zone, outdoor, **over):
+    """The held state, the stored-heat change of its first reference step, the step's room."""
+    p = _SVR_PARAMS.from_config(_svh_house(two_zone=two_zone, dhw=False, **{**_SVH_VALVE, **over}))
+    model = _SVR_MODEL(p)
+    opt = _SVR_OPT(model, _SVR_CFG(horizon_hours=1, time_step_minutes=15, target_temp=21.0))
+    w = _SVH_WS(outdoor_temps=np.array([outdoor]), wind_speeds=np.zeros(1),
+                precipitation=np.zeros(1), solar_radiation=np.zeros(1))
+    start = _SVR_STATE(room_temperature=20.5, slab_temperature=22.0, outdoor_temperature=outdoor,
+                       upper_floor_temperature=20.5, lower_floor_temperature=20.5,
+                       buffer_tank_temperature=30.0)
+    held = _svh_held(model, start, w, 21.0)
+    # A one-step horizon books the simulated step itself (nothing to apportion).
+    power = float(opt._compute_baseline_power(w, start, 0.25)[0][0])
+    nxt = model.simulate_step(held, power, outdoor, 0.0, 0.0, 0.0, 0.25)
+    return held, opt._stored_thermal_energy(nxt) - opt._stored_thermal_energy(held), nxt
+
+
+# -10 and -15 C sag far; at 14 C the two-zone house falls just short of the
+# target (a shortfall under 1 kW) and at 16 C holds it on a need under 1 kW.
+_svh_rows = {(tz, t): _svh_case(tz, t) for tz in (True, False) for t in (-10.0, -15.0, 14.0, 16.0)}
+R.check(
+    "R10-SAV-VALUATION-RESIDUE: behind a valve whose curve cannot hold the "
+    "setpoint, the thermostat reference starts where that curve holds the "
+    "house -- its first booked step draws no stored heat (the held 21 C "
+    "drew it every step, booked as unpaid reference heat); both zonings, "
+    "from a deep shortfall to a mild day the curve holds",
+    all(abs(ds) < 0.02 for h, ds, _ in _svh_rows.values())
+    and all(_svh_rows[(tz, t)][0].room_temperature < 21.0 - 0.1
+            for tz in (True, False) for t in (-10.0, -15.0)),
+    {k: (round(h.room_temperature, 3), round(ds, 4)) for k, (h, ds, _) in _svh_rows.items()},
+)
+# Null control: a curve that holds the setpoint keeps the held state at target.
+_svh_ok = {tz: _svh_case(tz, -10.0, mixing_valve_target=40.0) for tz in (True, False)}
+R.check(
+    "R10-SAV-VALUATION-RESIDUE: null control -- a valve curve able to hold "
+    "the setpoint leaves the held state's zones at the target",
+    all(h.room_temperature == 21.0 and h.upper_floor_temperature == 21.0
+        and h.lower_floor_temperature == 21.0 for h, _, _ in _svh_ok.values()),
+    {tz: round(h.room_temperature, 4) for tz, (h, _, _) in _svh_ok.items()},
+)
+
+# The pump's capacity is the held state's other bound, valved or not: at -25 C
+# a 4 kW pump cannot hold 21 C (the held 21 C drew ~1.07 kWh_th of stored
+# heat per booked step), a 9 kW one can.
+_SVH_CAP = {"buffer_tank_volume": 750.0, "buffer_max_temperature": 56.0}
+
+
+def _svh_cap(two_zone, valved, hp):
+    cfg = {**_SVH_CAP, "heat_pump_max_power": hp}
+    if valved:
+        cfg.update(mixing_valve_mode="manual", mixing_valve_target=40.0)
+    p = _SVR_PARAMS.from_config(_svh_house(two_zone=two_zone, dhw=False, **cfg))
+    model = _SVR_MODEL(p)
+    opt = _SVR_OPT(model, _SVR_CFG(horizon_hours=1, time_step_minutes=15, target_temp=21.0))
+    w = _SVH_WS(outdoor_temps=np.array([-25.0]), wind_speeds=np.zeros(1),
+                precipitation=np.zeros(1), solar_radiation=np.zeros(1),
+                humidity=np.array([85.0]))
+    start = _SVR_STATE(room_temperature=20.5, slab_temperature=22.0, outdoor_temperature=-25.0,
+                       upper_floor_temperature=20.5, lower_floor_temperature=20.5,
+                       buffer_tank_temperature=30.0)
+    held = _svh_held(model, start, w, 21.0)
+    power = float(opt._compute_baseline_power(w, start, 0.25)[0][0])
+    nxt = model.simulate_step(held, power, -25.0, 0.0, 0.0, 0.0, 0.25)
+    return held, opt._stored_thermal_energy(nxt) - opt._stored_thermal_energy(held), power
+
+
+_svh_caps = {(tz, v, hp): _svh_cap(tz, v, hp)
+             for tz in (True, False) for v in (True, False) for hp in (4.0, 9.0)}
+R.check(
+    "R10-SAV-VALUATION-RESIDUE: a pump too small to hold the setpoint starts "
+    "the reference where its capacity holds the house, valved or not -- the "
+    "first booked step runs at max power and draws no stored heat",
+    all(abs(ds) < 0.02 for h, ds, _ in _svh_caps.values())
+    and all(_svh_caps[(tz, v, 4.0)][0].room_temperature < 21.0 - 0.1
+            for tz in (True, False) for v in (True, False)),
+    {k: (round(h.room_temperature, 3), round(ds, 4), round(pw, 3))
+     for k, (h, ds, pw) in _svh_caps.items()},
+)
+R.check(
+    "R10-SAV-VALUATION-RESIDUE: null control -- a pump able to hold the "
+    "setpoint leaves the held state's zones at the target, valved or not",
+    all(_svh_caps[(tz, v, 9.0)][0].room_temperature == 21.0
+        for tz in (True, False) for v in (True, False)),
+    {k: round(h.room_temperature, 4) for k, (h, _, _) in _svh_caps.items() if k[2] == 9.0},
+)
+
+# A warm day under a pump too small for the tank's standing loss: unreachable
+# needs no zone heat there, so the held zones stay at the target, never above.
+_svh_warm_p = _SVR_PARAMS.from_config(_svh_house(
+    two_zone=True, dhw=False, buffer_tank_volume=2000.0, heat_pump_max_power=0.01))
+_svh_warm = _svh_held(
+    _SVR_MODEL(_svh_warm_p),
+    _SVR_STATE(room_temperature=20.5, slab_temperature=22.0, outdoor_temperature=25.0,
+               upper_floor_temperature=20.5, lower_floor_temperature=20.5,
+               buffer_tank_temperature=80.0),
+    _SVH_WS(outdoor_temps=np.array([25.0]), wind_speeds=np.zeros(1),
+            precipitation=np.zeros(1), solar_radiation=np.zeros(1)), 21.0)
+R.check(
+    "R10-SAV-VALUATION-RESIDUE: outdoors above the target, a pump unable to "
+    "cover the tank's standing loss leaves the held zones at the target, not "
+    "at the outdoor temperature",
+    _svh_warm.room_temperature == 21.0,
+    round(_svh_warm.room_temperature, 4),
+)
+
+# The reference has no wood: a modelled wood tank is emptied in the held state.
+_svh_wood_p = _SVR_PARAMS.from_config(_svh_house(
+    two_zone=True, dhw=False, wood_tank_top_entity="sensor.w", **_SVH_VALVE))
+_svh_wood = _svh_held(
+    _SVR_MODEL(_svh_wood_p),
+    _SVR_STATE(room_temperature=20.5, slab_temperature=22.0, outdoor_temperature=-10.0,
+               upper_floor_temperature=20.5, lower_floor_temperature=20.5,
+               buffer_tank_temperature=30.0, wood_tank_temperature=80.0),
+    _SVH_WS(outdoor_temps=np.array([-10.0]), wind_speeds=np.zeros(1),
+            precipitation=np.zeros(1), solar_radiation=np.zeros(1)), 21.0)
+R.check(
+    "R10-SAV-VALUATION-RESIDUE: a modelled wood tank holds no heat in the "
+    "thermostat reference's held state, whatever was measured in it",
+    _svh_wood_p.two_tank_modelled and _svh_wood.wood_tank_temperature == 0.0,
+    (_svh_wood_p.two_tank_modelled, _svh_wood.wood_tank_temperature),
+)
+
+# At zero demand (a warm day, two zones: each zone's need floors at exactly
+# 0.0) the valve-held tank keeps its measured temperature.
+_svh_idle = _svh_held(
+    _SVR_MODEL(_SVR_PARAMS.from_config(_svh_house(two_zone=True, dhw=False, **_SVH_VALVE))),
+    _SVR_STATE(room_temperature=20.5, slab_temperature=22.0, outdoor_temperature=25.0,
+               upper_floor_temperature=20.5, lower_floor_temperature=20.5,
+               buffer_tank_temperature=30.0),
+    _SVH_WS(outdoor_temps=np.array([25.0]), wind_speeds=np.zeros(1),
+            precipitation=np.zeros(1), solar_radiation=np.zeros(1)), 21.0)
+R.check(
+    "R10-SAV-VALUATION-RESIDUE: behind a valve at zero demand the held tank "
+    "keeps its measured temperature and the zones the target",
+    _svh_idle.buffer_tank_temperature == 30.0 and _svh_idle.room_temperature == 21.0,
+    (_svh_idle.buffer_tank_temperature, _svh_idle.room_temperature),
+)
+
 # --- R10-WATER-SETPOINT-FEEDBACK (outside report #3380, adopted by design
 # note design/R10-WATER-SETPOINT-FEEDBACK at 1442f906, approved d3623f5b):
 # a water set-point under Pump duty control was inlet + lift, re-anchored on
@@ -88182,4 +88380,1459 @@ R.check(
     "a plausible target raised a notice",
 )
 
+R.section(
+    "R10-DUTY-SWITCH-PLANNER-PRICE: the planner prices a duty switch that stops "
+    "the compressor (pull request 3420, Bankaifan)"
+)
+
+from types import SimpleNamespace as _DspNS  # noqa: E402
+
+import heatpump_optimizer.optimizer as _dsp_om  # noqa: E402
+from heatpump_optimizer import duty_legs as _dsp_dl, pump_arbiter as _dsp_pa  # noqa: E402
+from heatpump_optimizer.const import MODE_AUTO as _DSP_AUTO  # noqa: E402
+from heatpump_optimizer.dhw_planner import DhwPlanner as _DspPlanner  # noqa: E402
+from heatpump_optimizer.optimizer import (  # noqa: E402
+    HeatPumpOptimizer as _DspOpt,
+    OptimizationConfig as _DspCfg,
+    count_compressor_starts as _dsp_starts,
+    cycling_penalty as _dsp_cyc,
+)
+from heatpump_optimizer.thermal_model import (  # noqa: E402
+    ThermalModel as _DspTM,
+    ThermalParameters as _DspTP,
+    ThermalState as _DspTS,
+)
+
+_DSP_T0 = datetime(2026, 1, 10, 6, 0, tzinfo=UTC)
+_DSP_STEPS = np.arange(96)
+_DSP_PRICES = 1.3 + 0.9 * np.sin(2 * np.pi * (_DSP_STEPS - 30) / 96.0)
+#: Bankaifan's table: every hot water to heating switch stopped the compressor,
+#: none the other way, median off time 501 s (8.2 and 8.5 minutes).
+_DSP_PAIR, _DSP_OFF = (1.0, 0.0), (501.0, 0.0)
+
+
+def _dsp_w(space, dhw, pair, floor=None, p_max=6.0):
+    return _dsp_dl.switch_weight(
+        np.asarray(space, float), np.asarray(dhw, float), pair, p_max, floor
+    )
+
+
+# 1. The finding. Equal draw on both sides of the switch: the cycling term
+# sees no swing; the switch weight is p x draw / p_max.
+R.check(
+    "a hot-water step into a heating step at equal draw costs the cycling term "
+    "nothing and weighs p x draw / p_max as a switch",
+    _dsp_cyc(np.array([3.0, 3.0]), 2.0, 6.0) == 0.0
+    and _dsp_w([0, 3], [3, 0], (0.8, 0.0)) == 0.8 * 3.0 / 6.0,
+    f"{_dsp_cyc(np.array([3.0, 3.0]), 2.0, 6.0)}, {_dsp_w([0, 3], [3, 0], (0.8, 0.0))}",
+)
+R.check(
+    "the stop adds the smaller of the two levels across a boundary",
+    _dsp_w([0, 2], [3, 0], (0.8, 0.0)) == 0.8 * 2.0 / 6.0
+    and _dsp_w([0, 3], [2, 0], (0.8, 0.0)) == 0.8 * 2.0 / 6.0,
+)
+R.check(
+    "an idle step between the two duties is no switch",
+    _dsp_w([0, 0, 3], [3, 0, 0], (0.8, 0.6)) == 0.0,
+)
+R.check(
+    "the reverse order is the other direction: unpriced with a zero there, "
+    "priced by its own probability",
+    _dsp_w([3, 0], [0, 3], (0.8, 0.0)) == 0.0
+    and _dsp_w([3, 0], [0, 3], (0.8, 0.6)) == 0.6 * 3.0 / 6.0,
+)
+R.check(
+    "a two-leg both step alone weighs p x (space + dhw) / p_max: both legs run "
+    "at the step's combined level",
+    _dsp_w([2], [2], (0.8, 0.0)) == 0.8 * 4.0 / 6.0,
+    f"{_dsp_w([2], [2], (0.8, 0.0))}",
+)
+R.check(
+    "a both step followed by heating is one switch, not two: its last leg is "
+    "already heating",
+    _dsp_w([2, 3], [2, 0], (0.8, 0.0)) == 0.8 * 4.0 / 6.0,
+)
+R.check(
+    "null control: a zero pair weighs every one of those plans zero",
+    all(
+        _dsp_w(s, d, (0.0, 0.0)) == 0.0
+        for s, d in (([0, 3], [3, 0]), ([2], [2]), ([3, 0], [0, 3]))
+    ),
+)
+
+
+def _dsp_opt(pair=(0.0, 0.0), off=(0.0, 0.0), *, clamp=False, p_min=1.5, p_max=5.5, cyc=0.3):
+    params = _DspTP()
+    params.mixing_valve_mode = "none"
+    params.buffer_tank_volume = 750.0
+    params.min_electrical_power, params.max_electrical_power = p_min, p_max
+    params.dhw_enabled = True
+    cfg = _DspCfg(clamp_planned_levels=clamp, cycling_cost=cyc)
+    if pair is not None:
+        cfg.duty_switch_stop_probability, cfg.duty_switch_off_seconds = pair, off
+    return _DspOpt(_DspTM(params), cfg)
+
+
+_dsp_term_opt = _dsp_opt((0.8, 0.0), cyc=2.0, p_max=6.0)
+_dsp_term = _dsp_om._switch_cost_fn(_dsp_term_opt)
+_dsp_term_pair = (np.array([0.0, 3.0]), np.array([3.0, 0.0]))
+R.check(
+    "the objective's term is cycling_cost x that weight, a float for one plan "
+    "and one entry per row for a batch",
+    _dsp_term(*_dsp_term_pair) == 2.0 * (0.8 * 3.0 / 6.0)
+    and _dsp_term(np.stack([_dsp_term_pair[0]] * 2), _dsp_term_pair[1]).tolist()
+    == [2.0 * (0.8 * 3.0 / 6.0)] * 2,
+    f"{_dsp_term(*_dsp_term_pair)}",
+)
+R.check(
+    "and it is no operand at all with a zero pair, a zero cycling cost or no "
+    "hot-water plan",
+    _dsp_om._switch_cost_fn(_dsp_opt((0.0, 0.0), cyc=2.0))(*_dsp_term_pair) is None
+    and _dsp_om._switch_cost_fn(_dsp_opt((0.8, 0.0), cyc=0.0))(*_dsp_term_pair) is None
+    and _dsp_term(_dsp_term_pair[0], None) is None
+    and _dsp_om._with_switch_cost(1.25, None) == 1.25,
+)
+R.check(
+    "a non-finite, negative, over-one or misshapen learned pair reads as zero",
+    [
+        _dsp_dl.priced_pair(v, 1.0)
+        for v in ((float("nan"), 0.5), (-0.1, 1.5), (0.4,), None, ("x", 0.2), (1.0, 0.0))
+    ]
+    == [(0.0, 0.5), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (1.0, 0.0)]
+    and _dsp_dl.priced_pair((float("inf"), 30.0)) == (0.0, 30.0),
+)
+
+# 2. Leg-rule agreement: drive step_duty, then _share, and compare what the
+# arbiter serves with the legs the leaf reads from the same two draws.
+_DSP_NAMES = {_dsp_dl.IDLE: "idle", _dsp_dl.SPACE: "space", _dsp_dl.DHW: "dhw"}
+
+
+class _DspCoord:
+    """A coordinator with no boost held: ``_share`` reads nothing else of it."""
+
+
+_dsp_coord = _DspCoord()
+
+
+def _dsp_served(space, dhw, minute, floor):
+    plan = _DspNS(
+        timestamps=[_DSP_T0], power_schedule=[space], dhw_power_schedule=[dhw],
+        optimal_setpoints=[21.0], duty_floor_kw=floor,
+    )
+    now = _DSP_T0 + timedelta(minutes=minute)
+    inp = _DspNS(mode=_DSP_AUTO, disinfecting=False, plan=plan)
+    return _dsp_pa._share(_dsp_coord, inp, _dsp_pa.step_duty(plan, now), now)
+
+
+def _dsp_leg_mismatches(cells, floor):
+    """Cells where the arbiter's serving is not the leaf's legs, and the two-leg count."""
+    bad, two_leg = [], 0
+    for space, dhw in cells:
+        first, last, two = (v[0] for v in _dsp_dl.leg_ends([space], [dhw], floor))
+        served = [_dsp_served(space, dhw, m, floor) for m in (0.0, 4.9, 5.1, 7.4, 9.9, 10.1, 14.9)]
+        two_leg += int(two)
+        ends = (_DSP_NAMES[int(first)], _DSP_NAMES[int(last)])
+        if (
+            (served[0], served[-1]) != ends
+            or not set(served) <= set(ends)
+            or (len(set(served)) == 2) != bool(two)
+        ):
+            bad.append((space, dhw, floor, served, ends, bool(two)))
+    return bad, two_leg
+
+
+_DSP_LEVELS = (0.0, 0.05, 0.1, 0.11, 0.5, 1.0, 1.49, 1.5, 2.0, 3.0, 4.0, 5.5)
+_DSP_CELLS = [(s, d) for s in _DSP_LEVELS for d in _DSP_LEVELS]
+_dsp_grid = {floor: _dsp_leg_mismatches(_DSP_CELLS, floor) for floor in (None, 1.5)}
+R.check(
+    "the leaf's legs are what step_duty and _share serve over the probe grid, "
+    "floor unset and set: idle, one duty, both collapse edges and two legs",
+    not _dsp_grid[None][0] and not _dsp_grid[1.5][0],
+    f"{_dsp_grid[None][0][:3]} {_dsp_grid[1.5][0][:3]}",
+)
+R.check(
+    "and the grid holds what it claims: two-leg cells under both floors, fewer "
+    "with the floor set, and both exact collapse edges (shares of 5 and 10 minutes)",
+    _dsp_grid[None][1] > _dsp_grid[1.5][1] > 0
+    and (2.0, 1.0) in _DSP_CELLS and (1.0, 2.0) in _DSP_CELLS
+    and [bool(_dsp_dl.leg_ends([s], [d])[2][0]) for s, d in ((2.0, 1.0), (1.0, 2.0), (2.0, 0.5), (0.5, 2.0))]
+    == [True, True, False, False],
+    f"{_dsp_grid[None][1]}, {_dsp_grid[1.5][1]}",
+)
+
+
+def _dsp_realised_cells(p_min, p_max):
+    out = []
+    for space, dhw in _DSP_CELLS:
+        s, d = _dsp_om._realize_joint(True, np.array([space]), np.array([dhw]), p_min, p_max)
+        out.append((float(s[0]), float(d[0])))
+    return out
+
+
+_dsp_mod_cells = _dsp_realised_cells(1.5, 5.5)
+_dsp_fix_cells = _dsp_realised_cells(5.5, 5.5)
+_dsp_mod_grid = _dsp_leg_mismatches(_dsp_mod_cells, 1.5)
+_dsp_fix_grid = _dsp_leg_mismatches(_dsp_fix_cells, 5.5)
+R.check(
+    "the same agreement on the levels a clamped install ships: a modulating "
+    "pump keeps two-leg steps, each circuit at or above p_min",
+    not _dsp_mod_grid[0] and _dsp_mod_grid[1] > 0,
+    f"{_dsp_mod_grid[0][:3]}, two-leg {_dsp_mod_grid[1]}",
+)
+R.check(
+    "and on a fixed-speed pump the leaf never returns two legs, while the row "
+    "still holds heating-only and hot-water-only steps",
+    not _dsp_fix_grid[0] and _dsp_fix_grid[1] == 0
+    and {(5.5, 0.0), (0.0, 5.5)} <= set(_dsp_fix_cells),
+    f"{_dsp_fix_grid[0][:3]}, two-leg {_dsp_fix_grid[1]}",
+)
+
+# 3. Scalar against batch, bit for bit per row, the way the cycling term is pinned.
+_dsp_rng = np.random.default_rng(3420)
+_dsp_rows = _dsp_rng.uniform(0.0, 5.5, size=(64, 96))
+_dsp_rows[_dsp_rng.uniform(size=_dsp_rows.shape) < 0.35] = 0.0
+_dsp_tank = np.zeros(96)
+_dsp_tank[[5, 6, 20, 40, 41, 42, 70, 95]] = (4.4, 4.4, 2.0, 1.2, 4.4, 0.6, 3.0, 4.4)
+_dsp_batch_w = {
+    floor: _dsp_dl.switch_weights_batch(_dsp_rows, _dsp_tank, (0.7, 0.4), 5.5, floor)
+    for floor in (None, 1.5)
+}
+_dsp_row_bad = [
+    (floor, b)
+    for floor in (None, 1.5)
+    for b in range(_dsp_rows.shape[0])
+    if _dsp_batch_w[floor][b] != _dsp_dl.switch_weight(_dsp_rows[b], _dsp_tank, (0.7, 0.4), 5.5, floor)
+]
+R.check(
+    "switch_weights_batch is switch_weight on every row, bit for bit, floor "
+    "unset and set",
+    not _dsp_row_bad and len(set(_dsp_batch_w[None].tolist())) > 32,
+    f"divergent rows: {_dsp_row_bad[:5]}",
+)
+_dsp_no_pmax = _dsp_dl.switch_weights_batch(_dsp_rows, _dsp_tank, (0.7, 0.4), 0.0)
+R.check(
+    "a pump with no maximum draw weighs every row zero, one finite entry per "
+    "row and not per step, on the rows the priced pair weighs above",
+    _dsp_no_pmax.shape == (_dsp_rows.shape[0],)
+    and _dsp_rows.shape[0] != _dsp_rows.shape[1]
+    and not _dsp_no_pmax.any()
+    and bool(_dsp_batch_w[None].any()),
+    f"shape {_dsp_no_pmax.shape}",
+)
+
+# Availability: one step charged per block end, on the profile the solve starts from.
+_dsp_blk = np.array([0.0, 3.0, 3.0, 0.0, 0.0, 0.0])
+
+
+def _dsp_charged(start, lost=0.5, floor=None, tank=_dsp_blk):
+    avail = _dsp_dl.availability(np.asarray(start, float), tank, lost, floor)
+    return None if avail is None else (np.flatnonzero(avail < 1.0).tolist(), sorted(set(avail.tolist())))
+
+
+R.check(
+    "a block end charges one step, the one holding the heating leg that "
+    "follows it: the step after the block when heating starts there, not the "
+    "block's last",
+    _dsp_charged([1, 0, 0, 2, 2, 0]) == ([3], [0.5, 1.0]),
+    f"{_dsp_charged([1, 0, 0, 2, 2, 0])}",
+)
+R.check(
+    "the block's own last step when it is a two-leg step, and then not the "
+    "step after",
+    _dsp_charged([0, 0, 2, 2, 0, 0]) == ([2], [0.5, 1.0]),
+    f"{_dsp_charged([0, 0, 2, 2, 0, 0])}",
+)
+R.check(
+    "no vector at all with a zero lost share, with an idle step after the "
+    "block, or with no hot water: the caller makes today's calls",
+    _dsp_charged([1, 0, 0, 2, 2, 0], lost=0.0) is None
+    and _dsp_charged([1, 0, 0, 0, 2, 0]) is None
+    and _dsp_charged([1, 1, 1, 1, 1, 1], tank=np.zeros(6)) is None,
+)
+R.check(
+    "the lost share is p x off seconds over the step, capped at the whole "
+    "step, and only hot water to heating carries one",
+    _dsp_dl.lost_share((1.0, 0.0), (501.0, 0.0)) == 501.0 / 900.0
+    and _dsp_dl.lost_share((0.5, 1.0), (501.0, 900.0)) == 0.5 * 501.0 / 900.0
+    and _dsp_dl.lost_share((1.0, 0.0), (5000.0, 0.0)) == 1.0
+    and _dsp_dl.lost_share((0.0, 1.0), (0.0, 501.0)) == 0.0,
+)
+R.check(
+    "a duty-cycle install carries the lost time on the bound, a clamped one on "
+    "the delivered draw, and neither moves anything with no vector",
+    _dsp_dl.space_headroom(6.0, _dsp_blk, np.array([1, 1, 1, 0.5, 1, 1.0]), None).tolist()
+    == [6.0, 3.0, 3.0, 3.0, 6.0, 6.0]
+    and _dsp_dl.space_headroom(6.0, _dsp_blk, np.array([1, 1, 1, 0.5, 1, 1.0]), 6.0).tolist()
+    == _dsp_dl.space_headroom(6.0, _dsp_blk, None, None).tolist()
+    == [6.0, 3.0, 3.0, 6.0, 6.0, 6.0]
+    and _dsp_dl.delivered_space(
+        np.array([0, 0, 0, 6.0, 6.0, 0]), _dsp_blk, np.array([1, 1, 1, 0.5, 1, 1.0]), 6.0
+    ).tolist() == [0.0, 0.0, 0.0, 3.0, 6.0, 0.0],
+)
+_dsp_same = np.array([0, 0, 0, 6.0, 6.0, 0])
+R.check(
+    "on a duty-cycle install the delivered draw is the shipped array itself",
+    _dsp_dl.delivered_space(_dsp_same, _dsp_blk, np.array([1, 1, 1, 0.5, 1, 1.0]), None)
+    is _dsp_same,
+)
+R.check(
+    "in a charged two-leg step the stop takes its share of the combined level "
+    "from the heating draw, and never below zero",
+    _dsp_dl.delivered_space(
+        np.array([2.0, 0.5]), np.array([2.0, 4.0]), np.array([0.75, 0.5]), 1.5
+    ).tolist() == [1.0, 0.0],
+)
+# Item r16: on a modulating clamped install the charged step is chosen on the
+# levels the start profile ships, so it never holds a heating level under p_min.
+_dsp_mod_opt = _dsp_opt(_DSP_PAIR, _DSP_OFF, clamp=True)
+_dsp_r16_tank = np.zeros(8)
+_dsp_r16_tank[[1, 4]] = 4.4
+_dsp_r16_start = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 3.0, 3.0, 0.0])
+_dsp_r16_avail = _dsp_om._stop_availability(_dsp_mod_opt, _dsp_r16_start, _dsp_r16_tank, 5.5)
+_dsp_r16_ship = _dsp_om._realize_joint(True, _dsp_r16_start, _dsp_r16_tank, 1.5, 5.5)[0]
+R.check(
+    "on a modulating clamped install no charged step ships heating under the "
+    "floor: a start under p_min after a block is charged only once it ships at "
+    "p_min or above",
+    _dsp_r16_avail is not None
+    and bool(np.all(_dsp_r16_ship[_dsp_r16_avail < 1.0] >= 1.5))
+    and np.flatnonzero(_dsp_r16_avail < 1.0).tolist()
+    == [i for i in (2, 5) if _dsp_r16_ship[i] >= 1.5],
+    f"{_dsp_r16_avail}, shipped {_dsp_r16_ship}",
+)
+# The same item on a both step: heating shipped under p_min beside hot water is
+# no leg the arbiter serves, so the stop belongs to the heating step after it.
+_dsp_r16_both = (np.array([0.0, 1.0, 2.5, 0.0]), np.array([0.0, 2.0, 0.0, 0.0]))
+_dsp_r16_both_avail = _dsp_om._stop_availability(_dsp_mod_opt, *_dsp_r16_both, 5.5)
+_dsp_r16_both_ship = _dsp_om._realize_joint(True, *_dsp_r16_both, 1.5, 5.5)[0]
+_dsp_r16_both_dc = _dsp_om._stop_availability(_dsp_opt(_DSP_PAIR, _DSP_OFF), *_dsp_r16_both, 5.5)
+R.check(
+    "on a modulating clamped install heating shipped under p_min beside hot "
+    "water takes no charge: the stop is charged to the heating step after the "
+    "both step, and no charged step ships heating under the floor",
+    _dsp_r16_both_ship.tolist() == [0.0, 1.0, 2.5, 0.0]
+    and _dsp_r16_both_avail is not None
+    and np.flatnonzero(_dsp_r16_both_avail < 1.0).tolist() == [2]
+    and bool(np.all(_dsp_r16_both_ship[_dsp_r16_both_avail < 1.0] >= 1.5)),
+    f"{_dsp_r16_both_avail}, shipped {_dsp_r16_both_ship}",
+)
+R.check(
+    "null control: with no duty floor (a duty-cycle install) the same arrays "
+    "charge the both step itself, so the floor is what moved the charge",
+    _dsp_r16_both_dc is not None
+    and np.flatnonzero(_dsp_r16_both_dc < 1.0).tolist() == [1],
+    f"{_dsp_r16_both_dc}",
+)
+# The start profile is capped at what hot water leaves and never raised: a step
+# the start leaves idle after a block holds no heating leg to charge.
+_dsp_idle_after = _dsp_om._stop_availability(
+    _dsp_opt(_DSP_PAIR, _DSP_OFF), np.array([0.0, 0.0, -0.4, 2.0]), np.array([0.0, 2.0, 0.0, 0.0]), 5.5
+)
+_dsp_run_after = _dsp_om._stop_availability(
+    _dsp_opt(_DSP_PAIR, _DSP_OFF), np.array([0.0, 0.0, 2.0, 2.0]), np.array([0.0, 2.0, 0.0, 0.0]), 5.5
+)
+R.check(
+    "a start that is idle, or below zero, in the step after a block charges "
+    "nothing; the same block followed by heating charges that step",
+    _dsp_idle_after is None
+    and _dsp_run_after is not None and np.flatnonzero(_dsp_run_after < 1.0).tolist() == [2],
+    f"{_dsp_idle_after}, {_dsp_run_after}",
+)
+# The cap is the reading's own: a start that asks for heating beside hot water
+# at p_max ships none there, so that step holds no heating leg and the idle step
+# after it charges nothing. Beside a block that leaves room the same start is a
+# two-leg step, and charged.
+_dsp_full_blk = _dsp_om._stop_availability(
+    _dsp_opt(_DSP_PAIR, _DSP_OFF), np.array([0.0, 3.0, 0.0, 0.0]), np.array([0.0, 5.5, 0.0, 0.0]), 5.5
+)
+_dsp_part_blk = _dsp_om._stop_availability(
+    _dsp_opt(_DSP_PAIR, _DSP_OFF), np.array([0.0, 3.0, 0.0, 0.0]), np.array([0.0, 2.5, 0.0, 0.0]), 5.5
+)
+R.check(
+    "heating asked beside hot water at p_max is no heating leg: nothing is "
+    "charged; beside a block that leaves room the same start is charged there",
+    _dsp_full_blk is None
+    and _dsp_part_blk is not None and np.flatnonzero(_dsp_part_blk < 1.0).tolist() == [1],
+    f"{_dsp_full_blk}, {_dsp_part_blk}",
+)
+# The reading takes the start as it comes: the cap, the running threshold and
+# the clamped projection already read a value under zero as idle and one over
+# p_max as the cap, so clipping the start into [0, p_max] first moves no step
+# of it, on either install kind. The grid holds starts outside the band, and
+# blocks that charge a step, or the comparison would be of nothing.
+import itertools as _dsp_it  # noqa: E402
+
+_DSP_BAND_STARTS = [np.array(s) for s in _dsp_it.product((-0.4, 0.0, 1.0, 3.0, 9.0), repeat=4)]
+_DSP_BAND_TANKS = [np.array(t) for t in ((0.0, 2.5, 0.0, 0.0), (4.4, 0.0, 5.5, 0.0), (0.0, 0.0, 2.0, 2.0))]
+
+
+def _dsp_band_read(clamp, start, tank):
+    avail = _dsp_om._stop_availability(_dsp_opt(_DSP_PAIR, _DSP_OFF, clamp=clamp), start, tank, 5.5)
+    return None if avail is None else avail.tolist()
+
+
+_dsp_band_rows = [
+    (_dsp_band_read(clamp, start, tank), _dsp_band_read(clamp, np.clip(start, 0.0, 5.5), tank), start)
+    for clamp in (False, True) for tank in _DSP_BAND_TANKS for start in _DSP_BAND_STARTS
+]
+_dsp_band_moved = [(raw, clipped, start.tolist()) for raw, clipped, start in _dsp_band_rows if raw != clipped]
+R.check(
+    "a start outside [0, p_max] reads as the same start clipped into it, on a "
+    "duty-cycle and on a clamped install; the grid holds starts outside the "
+    "band and readings that charge a step",
+    not _dsp_band_moved
+    and any(raw is not None for raw, _, _ in _dsp_band_rows)
+    and any(raw is None for raw, _, _ in _dsp_band_rows)
+    and sum(bool(np.any((start < 0.0) | (start > 5.5))) for _, _, start in _dsp_band_rows) > len(_dsp_band_rows) // 2,
+    f"{len(_dsp_band_moved)} of {len(_dsp_band_rows)} moved, first {_dsp_band_moved[:1]}",
+)
+R.check(
+    "the bound is what hot water leaves and never under zero: 0.5 kW beside "
+    "5.5 of 6, nothing beside 7, with no vector and with one",
+    _dsp_dl.space_headroom(6.0, np.array([5.5, 7.0]), None, None).tolist() == [0.5, 0.0]
+    and _dsp_dl.space_headroom(6.0, np.array([5.5, 7.0]), np.array([1.0, 0.5]), None).tolist()
+    == [0.5, 0.0],
+)
+R.check(
+    "a pump under 1 kW weighs its switch like any other: p x draw / p_max at "
+    "a maximum draw of 0.5 kW",
+    _dsp_dl.switch_weight(np.array([0.0, 0.4]), np.array([0.4, 0.0]), (1.0, 0.0), 0.5) == 0.8,
+)
+
+
+def _dsp_obj_a(*_a, **_k):
+    return 0.0
+
+
+def _dsp_obj_b(*_a, **_k):
+    return np.zeros(1)
+
+
+_dsp_plain_solve = _dsp_om._with_stop_availability(
+    _dsp_opt(None, None), np.array([0.0, 0.0, 2.0, 2.0]), np.array([0.0, 2.0, 0.0, 0.0]),
+    5.5, _dsp_obj_a, _dsp_obj_b,
+)
+_dsp_vector_solve = _dsp_om._with_stop_availability(
+    _dsp_opt(_DSP_PAIR, _DSP_OFF), np.array([0.0, 0.0, 2.0, 2.0]), np.array([0.0, 2.0, 0.0, 0.0]),
+    5.5, _dsp_obj_a, _dsp_obj_b,
+)
+R.check(
+    "with no vector a space solve gets the two objectives it handed in, the "
+    "same objects, and today's bound; with one it gets them bound to the vector",
+    _dsp_plain_solve[1] is _dsp_obj_a and _dsp_plain_solve[2] is _dsp_obj_b
+    and _dsp_plain_solve[0].tolist() == [5.5, 3.5, 5.5, 5.5]
+    and _dsp_vector_solve[1] is not _dsp_obj_a
+    and np.flatnonzero(_dsp_vector_solve[1].keywords["avail"] < 1.0).tolist() == [2]
+    and _dsp_vector_solve[2].keywords["avail"] is _dsp_vector_solve[1].keywords["avail"],
+)
+
+
+def _dsp_solve(pair=(0.0, 0.0), off=(0.0, 0.0), *, pins=None, legionella_h=20.0, **install):
+    """One full ``optimize``; the planner builds, the published simulation's
+    inputs and the objective closures are recorded beside the result."""
+    opt = _dsp_opt(pair, off, **install)
+    seen = _DspNS(
+        builds=[], sims=[], objectives=[], solves=[], solved=[], min_runs=[],
+        energy=[None], vectors=[0], opt=opt,
+    )
+    real_build = _DspPlanner._build_dhw_requirements
+    real_sim, real_objectives = opt.model.simulate_trajectory_with_dhw, opt._solve_objectives
+    real_solve, real_min_run = opt._solve_space, _DspPlanner._apply_dhw_min_run
+
+    real_energy, real_vector = opt._energy_cost_fn, _dsp_om._stop_availability
+
+    def solve_space(*args):
+        seen.solves.append(args)
+        seen.solved.append(real_solve(*args))
+        return seen.solved[-1]
+
+    def energy_cost_fn(*args):
+        cost_of = real_energy(*args)
+
+        def recorded(power):
+            seen.energy[0] = np.array(power, float)
+            return cost_of(power)
+        return recorded
+
+    def vector(*args):
+        seen.vectors[0] += 1
+        return real_vector(*args)
+
+    def min_run(self, **kwargs):
+        out = real_min_run(self, **kwargs)
+        seen.min_runs.append((np.array(kwargs["plan"], float), np.array(out, float)))
+        return out
+
+    def build(self, h, **kwargs):
+        out = real_build(self, h, **kwargs)
+        seen.builds.append((kwargs, out, h, self))
+        return out
+
+    def sim(**kwargs):
+        seen.sims.append(kwargs)
+        return real_sim(**kwargs)
+
+    def objectives(h):
+        out = real_objectives(h)
+        seen.objectives.append(out)
+        return out
+
+    opt.model.simulate_trajectory_with_dhw, opt._solve_objectives = sim, objectives
+    opt._solve_space, opt._energy_cost_fn = solve_space, energy_cost_fn
+    _dsp_om._stop_availability = vector
+    _DspPlanner._build_dhw_requirements = build
+    _DspPlanner._apply_dhw_min_run = min_run
+    outdoor = 2.0 + 3.0 * np.sin(2 * np.pi * (_DSP_STEPS - 50) / 96.0)
+    try:
+        seen.result = opt.optimize(inputs=solve_inputs(
+            initial_state=_DspTS(
+                room_temperature=20.5, upper_floor_temperature=20.5,
+                lower_floor_temperature=20.5, slab_temperature=21.0,
+                outdoor_temperature=float(outdoor[0]),
+                buffer_tank_temperature=30.0, dhw_temperature=45.0,
+                dhw_hours_since_legionella=legionella_h,
+            ),
+            prices=_DSP_PRICES, outdoor_temps=outdoor,
+            start_time=datetime(2026, 1, 10, tzinfo=UTC), dhw_pins=pins,
+        ))
+    finally:
+        _DspPlanner._build_dhw_requirements = real_build
+        _DspPlanner._apply_dhw_min_run = real_min_run
+        _dsp_om._stop_availability = real_vector
+    seen.space = np.asarray(seen.result.power_schedule, float)
+    seen.dhw = np.asarray(seen.result.dhw_power_schedule, float)
+    seen.bans = [k["placement_ban"] for k, *_ in seen.builds if "placement_ban" in k]
+    return seen
+
+
+def _dsp_same_plan(a, b):
+    return (
+        np.array_equal(a.space, b.space) and np.array_equal(a.dhw, b.dhw)
+        and a.result.room_temp_trajectory == b.result.room_temp_trajectory
+        and a.result.objective_value == b.result.objective_value
+        and a.result.predicted_cost == b.result.predicted_cost
+        and a.result.status == b.result.status
+    )
+
+
+_DSP_INSTALLS = {
+    "duty-cycle": dict(clamp=False),
+    "modulating clamped": dict(clamp=True),
+    "fixed-speed": dict(clamp=True, p_min=5.5),
+}
+_dsp_base = {name: _dsp_solve(None, **kw) for name, kw in _DSP_INSTALLS.items()}
+_dsp_priced = {name: _dsp_solve(_DSP_PAIR, _DSP_OFF, **kw) for name, kw in _DSP_INSTALLS.items()}
+
+# 4. Null controls, each a full optimize whose arrays are compared equal with
+# the plan a config that never heard of the fields returns.
+_DSP_NULLS = {
+    "an empty learner (zero pair, no off time)": ((0.0, 0.0), (0.0, 0.0)),
+    "a learner under its on-threshold (zero pair, an off time stored)": ((0.0, 0.0), (501.0, 0.0)),
+    "a learned pair that is not a probability": ((float("nan"), 1.7), (501.0, 501.0)),
+}
+_dsp_null_bad = []
+for _dsp_name, _dsp_kw in _DSP_INSTALLS.items():
+    for _dsp_label, (_dsp_p, _dsp_o) in _DSP_NULLS.items():
+        _dsp_null = _dsp_solve(_dsp_p, _dsp_o, **_dsp_kw)
+        if (
+            not _dsp_same_plan(_dsp_null, _dsp_base[_dsp_name])
+            or _dsp_null.bans or _dsp_null.opt._space_avail is not None
+            or len(_dsp_null.builds) != len(_dsp_base[_dsp_name].builds)
+        ):
+            _dsp_null_bad.append((_dsp_name, _dsp_label))
+R.check(
+    "null controls: an empty learner, one under its threshold and a pair that "
+    "is no probability each leave the plan identical on all three install "
+    "classes, with no availability vector, no banned build and the planner "
+    "called as often",
+    not _dsp_null_bad,
+    f"{_dsp_null_bad}",
+)
+_dsp_free = _dsp_solve(_DSP_PAIR, (0.0, 0.0), cyc=0.0)
+R.check(
+    "null control: a stopping switch with no measured off time on an install "
+    "that prices no cycle moves nothing either",
+    _dsp_same_plan(_dsp_free, _dsp_solve(None, cyc=0.0)) and not _dsp_free.bans,
+)
+R.check(
+    "and the nulls have something to detect: with the contributor's pair the "
+    "plan moves on every install class",
+    all(not _dsp_same_plan(_dsp_priced[n], _dsp_base[n]) for n in _DSP_INSTALLS),
+    f"{[n for n in _DSP_INSTALLS if _dsp_same_plan(_dsp_priced[n], _dsp_base[n])]}",
+)
+
+
+# 5. Acceptance, on the contributor's table.
+def _dsp_plan_weight(seen, name):
+    kw = {"clamp": False, "p_min": 1.5, **_DSP_INSTALLS[name]}
+    return _dsp_dl.switch_weight(
+        seen.space, seen.dhw, _DSP_PAIR, 5.5, kw["p_min"] if kw["clamp"] else None
+    )
+
+
+def _dsp_old_under_new(name):
+    """The unpriced plan's score under the priced solve's own objective."""
+    old, new = _dsp_base[name], _dsp_priced[name]
+    avail = _dsp_om._stop_availability(new.opt, old.space, old.dhw, 5.5)
+    return float(new.objectives[-1][1](old.space, old.dhw, None, avail))
+
+
+_dsp_accept = {
+    name: (
+        _dsp_plan_weight(_dsp_base[name], name), _dsp_plan_weight(_dsp_priced[name], name),
+        _dsp_old_under_new(name), float(_dsp_priced[name].result.objective_value),
+    )
+    for name in ("duty-cycle", "modulating clamped")
+}
+R.check(
+    "acceptance: priced on the contributor's table the plan carries a lower "
+    "summed switch weight, on a duty-cycle and on a modulating clamped install",
+    all(new_w < old_w and old_w > 0 for old_w, new_w, _, _ in _dsp_accept.values()),
+    f"{_dsp_accept}",
+)
+R.check(
+    "at no higher cost under the plan's own objective: the new plan scores no "
+    "higher than the old plan does under the priced objective",
+    all(new_s <= old_s + 1e-9 for _, _, old_s, new_s in _dsp_accept.values()),
+    f"{_dsp_accept}",
+)
+R.check(
+    "the published objective of a priced plan is its closure's value on the "
+    "arrays that ship, with the vector the solve scored with",
+    all(
+        float(s.objectives[-1][1](s.space, s.dhw, None, s.opt._space_avail))
+        == float(s.result.objective_value)
+        for s in _dsp_priced.values()
+    ),
+)
+_dsp_dc = _dsp_priced["duty-cycle"]
+_dsp_dc_avail = _dsp_dc.opt._space_avail
+R.check(
+    "on the duty-cycle install the solved heating in every charged step is at "
+    "most avail x p_max - dhw, and a charged step exists",
+    _dsp_dc_avail is not None and bool(np.any(_dsp_dc_avail < 1.0))
+    and bool(np.all(
+        _dsp_dc.space <= np.maximum(0.0, _dsp_dc_avail * 5.5 - _dsp_dc.dhw) + 1e-9
+    )),
+    f"{None if _dsp_dc_avail is None else np.flatnonzero(_dsp_dc_avail < 1.0).tolist()}",
+)
+R.check(
+    "and there the simulation is fed the shipped schedule itself: the bound "
+    "carried the lost time",
+    np.array_equal(_dsp_dc.sims[-1]["space_power_schedule"], _dsp_dc.space),
+)
+
+# 9. A fixed-speed install: the level cannot carry the lost time.
+_dsp_fx, _dsp_fx0 = _dsp_priced["fixed-speed"], _dsp_base["fixed-speed"]
+_dsp_fx_avail = _dsp_fx.opt._space_avail
+_dsp_fx_charged = [] if _dsp_fx_avail is None else np.flatnonzero(_dsp_fx_avail < 1.0).tolist()
+_dsp_fx_total = _dsp_fx.space + _dsp_fx.dhw
+#: The charged steps the solve kept its heating leg on. Where it moved the leg
+#: off one, that block end's lost time is uncharged (its pair is still
+#: priced): the design's stated residual, at most one step's share per block end.
+_dsp_fx_live = [i for i in _dsp_fx_charged if _dsp_fx.space[i] > 0]
+R.check(
+    "fixed-speed: every shipped total is 0 or p_max and the plan's duty floor "
+    "is p_min, with a hot-water block followed by a charged heating step",
+    bool(np.all((_dsp_fx_total == 0.0) | (_dsp_fx_total == 5.5)))
+    and _dsp_fx.result.duty_floor_kw == 5.5
+    and bool(_dsp_fx_live)
+    and all(_dsp_fx.dhw[i - 1] == 5.5 and _dsp_fx.space[i] == 5.5 for i in _dsp_fx_live),
+    f"charged {_dsp_fx_charged}, live {_dsp_fx_live}",
+)
+R.check(
+    "fixed-speed: step_duty inside a charged step returns space, and the leaf "
+    "weighs the block end into it p x 1 from the result's own schedules and floor",
+    all(
+        _dsp_pa.step_duty(_dsp_fx.result, _dsp_fx.result.timestamps[i] + timedelta(minutes=7))
+        == "space"
+        and _dsp_dl.switch_weight(
+            _dsp_fx.space[i - 1 : i + 1], _dsp_fx.dhw[i - 1 : i + 1], _DSP_PAIR, 5.5,
+            _dsp_fx.result.duty_floor_kw,
+        ) == 1.0
+        for i in _dsp_fx_live
+    ),
+)
+_dsp_fx_sim = _dsp_fx.sims[-1]
+_dsp_fx_fed = np.asarray(_dsp_fx_sim["space_power_schedule"], float)
+_dsp_fx_expect = _dsp_fx.space.copy()
+_dsp_fx_expect[_dsp_fx_live] = (1.0 - 501.0 / 900.0) * 5.5
+_dsp_fx_at_level = _dsp_fx.opt.model.simulate_trajectory_with_dhw(
+    **{**_dsp_fx_sim, "space_power_schedule": _dsp_fx.space, "end_state": []}
+)
+_dsp_fx_at_avail = _dsp_fx.opt.model.simulate_trajectory_with_dhw(
+    **{**_dsp_fx_sim, "space_power_schedule": _dsp_fx_expect, "end_state": []}
+)
+R.check(
+    "fixed-speed: the published room trajectory is the simulation at "
+    "avail x p_max in the charged steps that hold heating and at the shipped "
+    "level everywhere else, and differs from the one at p_max",
+    np.array_equal(_dsp_fx_fed, _dsp_fx_expect)
+    and list(_dsp_fx_at_avail[0]) == list(_dsp_fx.result.room_temp_trajectory)
+    and list(_dsp_fx_at_level[0]) != list(_dsp_fx.result.room_temp_trajectory),
+    f"fed {_dsp_fx_fed[_dsp_fx_charged]}, live {_dsp_fx_live}",
+)
+R.check(
+    "fixed-speed: the published start count is count_compressor_starts on the "
+    "shipped total, unchanged by the pairs on the same arrays",
+    _dsp_fx.result.compressor_starts == _dsp_starts(_dsp_fx_total)
+    and _dsp_base["fixed-speed"].result.compressor_starts
+    == _dsp_starts(_dsp_fx0.space + _dsp_fx0.dhw),
+    f"{_dsp_fx.result.compressor_starts}",
+)
+R.check(
+    "fixed-speed null control: with a zero pair the simulation is fed the "
+    "shipped schedule and no vector exists",
+    np.array_equal(_dsp_fx0.sims[-1]["space_power_schedule"], _dsp_fx0.space)
+    and _dsp_fx0.opt._space_avail is None,
+)
+
+# 6. The banned candidate: its channel, its ban, its guard.
+R.check(
+    "a priced plan with a priced switch tries exactly one more hot-water plan, "
+    "the first build's own arguments plus the ban, and no unpriced solve "
+    "builds one",
+    all(
+        len(s.bans) == 1
+        and sorted(s.builds[-1][0]) == sorted([*s.builds[0][0], "placement_ban"])
+        and np.array_equal(
+            s.bans[0],
+            _dsp_dl.switch_ban(
+                _dsp_om._realize_joint(
+                    s.opt.config.clamp_planned_levels, s.solves[-1][1], s.solves[0][0],
+                    s.opt.model.params.min_electrical_power, 5.5,
+                )[0],
+                _DSP_PAIR, _dsp_om._duty_floor(s.opt),
+            ),
+        )
+        for s in _dsp_priced.values()
+    )
+    and not any(s.bans for s in _dsp_base.values()),
+    f"{[(n, len(s.bans), len(s.builds), len(s.solves)) for n, s in _dsp_priced.items()]}",
+)
+R.check(
+    "the ban is the steps heating runs in or runs in next, for hot water to "
+    "heating, and mirrors onto the previous step for the other direction",
+    _dsp_dl.switch_ban(np.array([0, 0, 2.0, 0, 0]), (1.0, 0.0), None).tolist()
+    == [False, True, True, False, False]
+    and _dsp_dl.switch_ban(np.array([0, 0, 2.0, 0, 0]), (0.0, 1.0), None).tolist()
+    == [False, False, True, True, False]
+    and not _dsp_dl.switch_ban(np.array([0, 0, 2.0, 0, 0]), (1.0, 0.0), 3.0).any(),
+)
+_dsp_ban_writes = [
+    (name, np.flatnonzero(out[0].schedule[kwargs["placement_ban"]] > 0).tolist())
+    for name, s in _dsp_priced.items()
+    for kwargs, out, *_ in s.builds
+    if "placement_ban" in kwargs
+]
+_dsp_min_run_moves = [
+    int(np.sum(before != after))
+    for s in _dsp_priced.values()
+    for (kwargs, *_), (before, after) in zip(s.builds, s.min_runs)
+    if "placement_ban" in kwargs
+]
+R.check(
+    "the ban holds: the candidate's schedule is zero on every banned step, on "
+    "builds whose min-run stage rewrote the plan",
+    all(not steps for _, steps in _dsp_ban_writes)
+    and len(_dsp_min_run_moves) == 3 and all(n > 0 for n in _dsp_min_run_moves),
+    f"{_dsp_ban_writes}, min-run rewrote {_dsp_min_run_moves} steps",
+)
+
+# The channel: a due disinfection, no Off window, a manual force-on pin.
+_dsp_pin = np.full(96, np.nan)
+_dsp_pin[12] = 1.0
+_dsp_leg = _dsp_solve(None, legionella_h=200.0, pins=_dsp_pin)
+_dsp_leg_kw, (_dsp_leg_plan, _dsp_leg_req), _dsp_leg_h, _dsp_leg_planner = _dsp_leg.builds[0]
+_dsp_leg_ban = np.zeros(96, dtype=bool)
+_dsp_leg_ban[:16] = True
+_dsp_by_ban = _dsp_leg_planner._build_dhw_requirements(
+    _dsp_leg_h, **_dsp_leg_kw, placement_ban=_dsp_leg_ban
+)
+_dsp_by_off = _dsp_leg_planner._build_dhw_requirements(
+    _dsp_leg_h, **{**_dsp_leg_kw, "off_steps": _dsp_leg_ban}
+)
+_dsp_by_none = _dsp_leg_planner._build_dhw_requirements(
+    _dsp_leg_h, **_dsp_leg_kw, placement_ban=None
+)
+R.check(
+    "the ban's channel: with a disinfection due inside it and no Off window, a "
+    "banned build returns the same legionella_step and the same requirement, "
+    "and a manual force-on pin inside the ban survives",
+    _dsp_leg_plan.legionella_due and _dsp_leg_plan.legionella_step is not None
+    and bool(_dsp_leg_ban[_dsp_leg_plan.legionella_step])
+    and _dsp_by_ban[0].legionella_step == _dsp_leg_plan.legionella_step
+    and np.array_equal(_dsp_by_ban[1], _dsp_leg_req)
+    and _dsp_by_ban[0].schedule[12] > 0
+    and not np.any(np.delete(_dsp_by_ban[0].schedule[:16], 12) > 0),
+    f"step {_dsp_by_ban[0].legionella_step} vs {_dsp_leg_plan.legionella_step}, "
+    f"banned {np.flatnonzero(_dsp_by_ban[0].schedule[:16] > 0).tolist()}",
+)
+R.check(
+    "and the check tells the two doors apart: the same mask through off_steps "
+    "moves the disinfection step and zeroes the pinned step",
+    _dsp_by_off[0].legionella_step != _dsp_leg_plan.legionella_step
+    and _dsp_by_off[0].schedule[12] == 0,
+    f"step {_dsp_by_off[0].legionella_step}",
+)
+R.check(
+    "null control: a build with no ban is the build the solve made",
+    np.array_equal(_dsp_by_none[0].schedule, _dsp_leg_plan.schedule)
+    and np.array_equal(_dsp_by_none[1], _dsp_leg_req)
+    and _dsp_by_none[0].legionella_step == _dsp_leg_plan.legionella_step,
+)
+
+# The guard, on that disinfection fixture: heating right after the run-up
+# makes a priced switch, the ban then forbids the run-up steps, and the banned
+# candidate cannot hold the requirement the planner returns beside it.
+_dsp_g_opt = _dsp_opt(_DSP_PAIR, _DSP_OFF)
+_dsp_g_step = int(_dsp_leg_plan.legionella_step)
+_dsp_g_space = np.zeros(96)
+_dsp_g_space[_dsp_g_step + 1 : _dsp_g_step + 3] = 3.0
+_dsp_g_dhw = np.asarray(_dsp_leg_plan.schedule, float)
+_dsp_g_incumbent = (_dsp_g_space, _dsp_g_dhw, "optimal")
+_dsp_g_avail = np.ones(96)
+_dsp_g_calls = []
+
+
+def _dsp_g_solve(score):
+    def solve_space(dhw_plan, warm_start):
+        _dsp_g_calls.append(np.array(dhw_plan, float))
+        _dsp_g_opt._space_avail = None
+        return np.asarray(warm_start, float) * 0.5, "candidate", score
+    return solve_space
+
+
+def _dsp_g_run(score, shortfall=None, requirement=True):
+    """One candidate pass; returns what it returned and what it left behind."""
+    _dsp_g_opt._dhw_requirement = _dsp_leg_req if requirement else None
+    _dsp_g_opt._space_avail = _dsp_g_avail
+    del _dsp_g_calls[:]
+    planner = _dsp_leg_planner
+    if shortfall is not None:
+        planner = _DspNS(
+            _build_dhw_requirements=_dsp_leg_planner._build_dhw_requirements,
+            _dhw_coil_wood_forecast=_dsp_leg_planner._dhw_coil_wood_forecast,
+            _dhw_shortfall=shortfall,
+        )
+    out = _dsp_om._avoid_priced_switches(
+        _dsp_g_opt, _dsp_leg_h, planner, _dsp_g_solve(score),
+        lambda *a: 0.0, 5.5, _dsp_g_incumbent,
+    )
+    return out, _dsp_g_opt._dhw_requirement, _dsp_g_opt._space_avail, len(_dsp_g_calls)
+
+
+_dsp_g_ban = _dsp_dl.switch_ban(_dsp_g_space, _DSP_PAIR, None)
+_dsp_g_short = _dsp_g_run(-1e9)
+R.check(
+    "the guard's fixture is the one it names: the incumbent holds a priced "
+    "switch after the disinfection run-up and the ban forbids the run-up step",
+    _dsp_dl.switch_weight(_dsp_g_space, _dsp_g_dhw, _DSP_PAIR, 5.5) > 0
+    and bool(_dsp_g_ban[_dsp_g_step]) and _dsp_g_dhw[_dsp_g_step] > 0,
+)
+R.check(
+    "a banned candidate that scores lower but falls short of its returned "
+    "requirement where the incumbent holds its own is refused before any "
+    "solve, and the incumbent's requirement and availability stay in place",
+    _dsp_g_short[0] is _dsp_g_incumbent and _dsp_g_short[1] is _dsp_leg_req
+    and _dsp_g_short[2] is _dsp_g_avail and _dsp_g_short[3] == 0,
+    f"{_dsp_g_short[3]} solves, incumbent kept {_dsp_g_short[0] is _dsp_g_incumbent}",
+)
+_dsp_g_held = _dsp_g_run(-1e9, shortfall=lambda *a: (None, np.zeros(96), None))
+R.check(
+    "control: the same candidate with the shortfall reading zero is adopted on "
+    "its lower score, with the requirement returned beside it",
+    _dsp_g_held[0] is not _dsp_g_incumbent and _dsp_g_held[0][2] == "candidate"
+    and _dsp_g_held[1] is not _dsp_leg_req and _dsp_g_held[3] == 1
+    and not np.any(_dsp_g_held[0][1][_dsp_g_ban & ~(np.nan_to_num(_dsp_pin) >= 0.5)] > 0),
+    f"{_dsp_g_held[3]} solves",
+)
+_dsp_g_dear = _dsp_g_run(1e9, shortfall=lambda *a: (None, np.zeros(96), None))
+R.check(
+    "a candidate that does not score lower is refused after its solve, and the "
+    "incumbent's requirement and availability are put back",
+    _dsp_g_dear[0] is _dsp_g_incumbent and _dsp_g_dear[1] is _dsp_leg_req
+    and _dsp_g_dear[2] is _dsp_g_avail and _dsp_g_dear[3] == 1,
+)
+_dsp_g_bare = _dsp_g_run(-1e9, shortfall=lambda *a: (None, np.zeros(96), None), requirement=False)
+R.check(
+    "an incumbent with no requirement to hold a candidate to gets no candidate: "
+    "the pass the control adopts from returns the incumbent without a solve",
+    _dsp_g_bare[0] is _dsp_g_incumbent and _dsp_g_bare[1] is None
+    and _dsp_g_bare[2] is _dsp_g_avail and _dsp_g_bare[3] == 0,
+    f"{_dsp_g_bare[3]} solves, incumbent kept {_dsp_g_bare[0] is _dsp_g_incumbent}",
+)
+
+
+def _dsp_g_raises(*_a):
+    raise RuntimeError("the planner's tank walk failed")
+
+
+_dsp_g_broke = _dsp_g_run(-1e9, shortfall=_dsp_g_raises)
+R.check(
+    "a candidate pass that raises is skipped: the incumbent, its requirement "
+    "and its availability stand, and nothing is solved",
+    _dsp_g_broke[0] is _dsp_g_incumbent and _dsp_g_broke[1] is _dsp_leg_req
+    and _dsp_g_broke[2] is _dsp_g_avail and _dsp_g_broke[3] == 0,
+)
+_dsp_g_real_build = _dsp_om._dhw_build
+_dsp_om._dhw_build = lambda *a, **k: (_dsp_leg_plan, _dsp_leg_req)
+try:
+    _dsp_g_on_ban = _dsp_g_run(-1e9, shortfall=lambda *a: (None, np.zeros(96), None))
+finally:
+    _dsp_om._dhw_build = _dsp_g_real_build
+R.check(
+    "a candidate with hot water on a banned step no pin forces on is refused "
+    "before any solve",
+    _dsp_g_on_ban[0] is _dsp_g_incumbent and _dsp_g_on_ban[3] == 0
+    and _dsp_g_on_ban[1] is _dsp_leg_req,
+)
+# The pin rule is the planner's own (``_apply_dhw_pins``): a pin of 0.5 forces on.
+_dsp_g_pins = _dsp_leg_h.dhw_pins
+_dsp_g_half = np.full(96, np.nan)
+_dsp_g_half[_dsp_g_ban & (np.asarray(_dsp_leg_plan.schedule, float) > 0)] = 0.5
+_dsp_om._dhw_build = lambda *a, **k: (_dsp_leg_plan, _dsp_leg_req)
+try:
+    object.__setattr__(_dsp_leg_h, "dhw_pins", _dsp_g_half)
+    _dsp_g_half_on = _dsp_g_run(-1e9, shortfall=lambda *a: (None, np.zeros(96), None))
+finally:
+    object.__setattr__(_dsp_leg_h, "dhw_pins", _dsp_g_pins)
+    _dsp_om._dhw_build = _dsp_g_real_build
+R.check(
+    "the same candidate with each of those steps pinned at 0.5, which the "
+    "planner's pin rule forces on, is solved and adopted on its lower score",
+    int(np.sum(_dsp_g_half == 0.5)) > 0
+    and _dsp_g_half_on[3] == 1 and _dsp_g_half_on[0][2] == "candidate"
+    and _dsp_g_half_on[0][1] is _dsp_leg_plan.schedule,
+    f"{_dsp_g_half_on[3]} solve(s), {int(np.sum(_dsp_g_half == 0.5))} pinned step(s)",
+)
+_dsp_g_trickle = np.asarray(_dsp_leg_plan.schedule, float).copy()
+_dsp_g_trickle[_dsp_g_ban] = np.where(_dsp_g_trickle[_dsp_g_ban] > 0, 0.8, 0.0)
+_dsp_om._dhw_build = lambda *a, **k: (
+    _DspNS(schedule=_dsp_g_trickle, draw_rates=_dsp_leg_plan.draw_rates), _dsp_leg_req
+)
+try:
+    _dsp_g_low_on_ban = _dsp_g_run(-1e9, shortfall=lambda *a: (None, np.zeros(96), None))
+finally:
+    _dsp_om._dhw_build = _dsp_g_real_build
+R.check(
+    "any hot water on a banned step refuses the candidate, 0.8 kW as much as "
+    "a full block",
+    bool(np.any(_dsp_g_trickle[_dsp_g_ban] == 0.8))
+    and _dsp_g_low_on_ban[0] is _dsp_g_incumbent and _dsp_g_low_on_ban[3] == 0,
+    f"{_dsp_g_low_on_ban[3]} solve(s)",
+)
+_dsp_g_tie = _dsp_g_run(-1e-9, shortfall=lambda *a: (None, np.zeros(96), None))
+R.check(
+    "a candidate lower by exactly the 1e-9 margin, and so by no more than "
+    "it, is a tie: refused after its solve, as _co_optimize refuses its own",
+    _dsp_g_tie[0] is _dsp_g_incumbent and _dsp_g_tie[3] == 1
+    and _dsp_g_tie[1] is _dsp_leg_req and _dsp_g_tie[2] is _dsp_g_avail,
+    f"{_dsp_g_tie[3]} solve(s)",
+)
+_dsp_g_walks = []
+
+
+def _dsp_g_walk(temps, schedule, *rest):
+    """A tank walk short at step 5 until that step is excused."""
+    _dsp_g_walks.append(temps)
+    return "walked", np.zeros(96), (None if rest[-1] else 5)
+
+
+_dsp_g_run(-1e9, shortfall=_dsp_g_walk)
+R.check(
+    "the incumbent's tank is walked once: the read past its excused step is "
+    "handed the first walk's temperatures",
+    _dsp_g_walks[:2] == [None, "walked"],
+    f"{_dsp_g_walks}",
+)
+R.check(
+    "a configuration that never heard of the learner holds a zero pair in "
+    "both fields, and an optimizer that has solved nothing holds no vector",
+    _DspCfg().duty_switch_stop_probability == (0.0, 0.0)
+    and _DspCfg().duty_switch_off_seconds == (0.0, 0.0)
+    and _dsp_opt(None, None)._space_avail is None,
+)
+_dsp_g_opt.config.duty_switch_stop_probability = (0.0, 0.0)
+_dsp_g_unpriced = _dsp_g_run(-1e9, shortfall=lambda *a: (None, np.zeros(96), None))
+_dsp_g_opt.config.duty_switch_stop_probability = _DSP_PAIR
+R.check(
+    "null control: with a zero pair the pass returns the incumbent without a "
+    "build or a solve",
+    _dsp_g_unpriced[0] is _dsp_g_incumbent and _dsp_g_unpriced[3] == 0,
+)
+
+# 8. The term's edges. Hot water under a third of p_max puts both collapse
+# edges of a both step inside the bounds; warm starts sit two finite-difference
+# steps either side of each, and one at the running threshold.
+_dsp_e = _dsp_solve(_DSP_PAIR, (0.0, 0.0))
+_dsp_e0 = _dsp_solve((0.0, 0.0), (501.0, 0.0))
+_dsp_e_tank = np.zeros(96)
+_dsp_e_tank[[40, 41]] = 1.5
+_DSP_EPS = 2.0 * _dsp_om._LBFGSB_FD_EPS
+
+
+def _dsp_e_start(step, level):
+    start = np.full(96, 2.0)
+    start[step] = level
+    return start
+
+
+_DSP_E_STARTS = {
+    "under the lower collapse edge": _dsp_e_start(40, 0.75 - _DSP_EPS),
+    "over the lower collapse edge": _dsp_e_start(40, 0.75 + _DSP_EPS),
+    "under the upper collapse edge": _dsp_e_start(41, 3.0 - _DSP_EPS),
+    "over the upper collapse edge": _dsp_e_start(41, 3.0 + _DSP_EPS),
+    "at the running threshold": _dsp_e_start(42, 0.1 + _DSP_EPS),
+}
+
+
+def _dsp_e_solve(seen, start):
+    args = seen.solves[0]
+    power, status, score = seen.opt._solve_space(_dsp_e_tank, start, *args[2:])
+    return power, status, score, float(args[8](start, _dsp_e_tank))
+
+
+_dsp_e_runs = {
+    label: (_dsp_e_solve(_dsp_e, start), _dsp_e_solve(_dsp_e0, start), _dsp_e_solve(_dsp_base["duty-cycle"], start))
+    for label, start in _DSP_E_STARTS.items()
+}
+R.check(
+    "the edge fixture is the one it names: 1.5 kW of hot water under a third "
+    "of p_max, and the starts straddle a change in the legs",
+    1.5 < 5.5 / 3.0
+    and [bool(_dsp_dl.leg_ends(s, _dsp_e_tank)[2][i]) for s, i in (
+        (_DSP_E_STARTS["under the lower collapse edge"], 40),
+        (_DSP_E_STARTS["over the lower collapse edge"], 40),
+        (_DSP_E_STARTS["under the upper collapse edge"], 41),
+        (_DSP_E_STARTS["over the upper collapse edge"], 41),
+    )] == [False, True, True, False],
+)
+R.check(
+    "from each edge start the priced solve returns a score no higher than its "
+    "start's, with a solver status no worse than the same start solved unpriced",
+    all(
+        priced[2] <= priced[3] + 1e-9 and (priced[1] == null[1] or priced[1] == "optimal")
+        for priced, null, _ in _dsp_e_runs.values()
+    ),
+    f"{[(k, round(p[3] - p[2], 4), p[1], n[1]) for k, (p, n, _) in _dsp_e_runs.items()]}",
+)
+R.check(
+    "null control: with a zero pair the same starts return the arrays of a "
+    "config that never heard of the fields",
+    all(
+        np.array_equal(null[0], plain[0]) and null[1:] == plain[1:]
+        for _, null, plain in _dsp_e_runs.values()
+    ),
+)
+
+# Item r14: a relaxed start of a clamped install scores unrounded levels; the
+# delivered draw gives it the clamped reading on that unrounded level.
+_dsp_rx_opt = _dsp_opt(_DSP_PAIR, _DSP_OFF, clamp=True)
+_dsp_rx_args = (np.array([0.7, 3.0]), np.array([0.0, 0.0]), np.array([0.5, 0.5]))
+_dsp_rx_rounded = _dsp_om._shipped_and_received(_dsp_rx_opt, *_dsp_rx_args)
+_dsp_rx_opt._levels_relaxed = True
+try:
+    _dsp_rx_relaxed = _dsp_om._shipped_and_received(_dsp_rx_opt, *_dsp_rx_args)
+finally:
+    _dsp_rx_opt._levels_relaxed = False
+R.check(
+    "a relaxed start carrying a vector is charged on its unrounded level, the "
+    "rounded objective on the level that ships",
+    _dsp_rx_relaxed[0].tolist() == [0.7, 3.0] and _dsp_rx_relaxed[2].tolist() == [0.35, 1.5]
+    and _dsp_rx_rounded[0].tolist() != [0.7, 3.0]
+    and _dsp_rx_rounded[2].tolist() == (_dsp_rx_rounded[0] * 0.5).tolist(),
+    f"{_dsp_rx_relaxed[2]}, {_dsp_rx_rounded[0]}, {_dsp_rx_rounded[2]}",
+)
+_dsp_rx_plain = _dsp_om._shipped_and_received(_dsp_rx_opt, *_dsp_rx_args[:2], None)
+R.check(
+    "and with no vector the received draw is the shipped array itself",
+    _dsp_rx_plain[2] is _dsp_rx_plain[0],
+)
+
+# What reads the shipped level and what reads the delivered draw, on a
+# modulating clamped install that prices no cycle (so nothing steers the plan
+# off its charged steps) and on the fixed-speed plan above.
+R.check(
+    "the plan's duty floor reaches the switch weight: heating under the floor "
+    "after a block is no leg and no switch",
+    _dsp_w([0, 1.0], [3, 0], (0.8, 0.0)) == 0.8 * 1.0 / 6.0
+    and _dsp_w([0, 1.0], [3, 0], (0.8, 0.0), floor=1.5) == 0.0,
+)
+R.check(
+    "at the exact minute the hot-water share ends the arbiter serves heating "
+    "(a strict <, as before the rule moved)",
+    [_dsp_served(3.0, 2.0, m, None) for m in (5.99, 6.0, 6.01)] == ["dhw", "space", "space"],
+    f"{[_dsp_served(3.0, 2.0, m, None) for m in (5.99, 6.0, 6.01)]}",
+)
+_dsp_mc = _dsp_solve(_DSP_PAIR, _DSP_OFF, clamp=True, cyc=0.0)
+_dsp_mc_avail = _dsp_mc.opt._space_avail
+_dsp_mc_fed = np.asarray(_dsp_mc.sims[-1]["space_power_schedule"], float)
+_dsp_mc_live = (
+    [] if _dsp_mc_avail is None
+    else [i for i in np.flatnonzero(_dsp_mc_avail < 1.0).tolist() if _dsp_mc.space[i] > 0]
+)
+_dsp_mc_obj, _dsp_mc_batch, _dsp_mc_energy = (_dsp_mc.objectives[-1][i] for i in (1, 2, 3))
+_dsp_mc_rebuilt = (
+    None if _dsp_mc_avail is None
+    else _dsp_om._stop_availability(_dsp_mc.opt, _dsp_mc.space, _dsp_mc.dhw, 5.5)
+)
+R.check(
+    "modulating clamped: the simulation is fed the delivered draw of the "
+    "vector the adopted solve scored with, which is not the vector the final "
+    "plan would rebuild",
+    bool(_dsp_mc_live)
+    and np.array_equal(
+        _dsp_mc_fed, _dsp_dl.delivered_space(_dsp_mc.space, _dsp_mc.dhw, _dsp_mc_avail, 1.5)
+    )
+    and not np.array_equal(_dsp_mc_fed, _dsp_mc.space)
+    and (_dsp_mc_rebuilt is None or not np.array_equal(
+        _dsp_mc_fed, _dsp_dl.delivered_space(_dsp_mc.space, _dsp_mc.dhw, _dsp_mc_rebuilt, 1.5)
+    )),
+    f"live {_dsp_mc_live}",
+)
+R.check(
+    "the vector is built once per space solve and never at publication, on "
+    "every priced solve above",
+    all(s.vectors[0] == len(s.solves) for s in [*_dsp_priced.values(), _dsp_mc]),
+    f"{[(s.vectors[0], len(s.solves)) for s in [*_dsp_priced.values(), _dsp_mc]]}",
+)
+R.check(
+    "modulating clamped (item r15): the achieved objective is the closure on "
+    "the shipped arrays with that vector, not on the delivered draw, which "
+    "would charge the lost time twice",
+    bool(_dsp_mc_live)
+    and float(_dsp_mc_obj(_dsp_mc.space, _dsp_mc.dhw, None, _dsp_mc_avail))
+    == float(_dsp_mc.result.objective_value)
+    != float(_dsp_mc_obj(_dsp_mc_fed, _dsp_mc.dhw, None, _dsp_mc_avail))
+    and float(_dsp_mc_obj(_dsp_mc.space, _dsp_mc.dhw)) != float(_dsp_mc.result.objective_value),
+)
+R.check(
+    "modulating clamped: the predicted cost is the energy of the delivered "
+    "draw, not of the shipped level",
+    bool(_dsp_mc_live)
+    and float(_dsp_mc.result.predicted_cost) == float(_dsp_mc_energy(_dsp_mc_fed + _dsp_mc.dhw))
+    != float(_dsp_mc_energy(_dsp_mc.space + _dsp_mc.dhw)),
+)
+_dsp_mc_scalar = float(_dsp_mc_obj(_dsp_mc.space, _dsp_mc.dhw, None, _dsp_mc_avail))
+_dsp_mc_scalar_energy = _dsp_mc.energy[0]
+_dsp_mc_rows = float(
+    _dsp_mc_batch(np.stack([_dsp_mc.space, _dsp_mc.space]), _dsp_mc.dhw, None, _dsp_mc_avail)[1]
+)
+_dsp_mc_batch_energy = _dsp_mc.energy[0]
+R.check(
+    "the scalar and the batch objective both price the energy of the "
+    "delivered draw plus hot water, and agree bit for bit with a vector",
+    np.array_equal(_dsp_mc_scalar_energy, _dsp_mc_fed + _dsp_mc.dhw)
+    and np.array_equal(_dsp_mc_batch_energy[1], _dsp_mc_fed + _dsp_mc.dhw)
+    and _dsp_mc_rows == _dsp_mc_scalar,
+    f"{_dsp_mc_rows} vs {_dsp_mc_scalar}",
+)
+# The switch term reads the shipped level: on the fixed-speed plan the
+# delivered draw of a charged step is under the floor and would be no leg.
+_dsp_fx_free = _dsp_solve(_DSP_PAIR, _DSP_OFF, clamp=True, p_min=5.5, cyc=0.0)
+_dsp_fx_obj, _dsp_fx_batch = _dsp_fx.objectives[-1][1], _dsp_fx.objectives[-1][2]
+_dsp_fx_score = float(_dsp_fx_obj(_dsp_fx.space, _dsp_fx.dhw, None, _dsp_fx_avail))
+_dsp_fx_level_terms = _dsp_fx.opt.config.price_weight * (
+    _dsp_cyc(_dsp_fx_total, 0.3, 5.5)
+    + 0.3 * _dsp_dl.switch_weight(_dsp_fx.space, _dsp_fx.dhw, _DSP_PAIR, 5.5, 5.5)
+)
+_dsp_fx_unpriced = float(
+    _dsp_fx_free.objectives[-1][1](_dsp_fx.space, _dsp_fx.dhw, None, _dsp_fx_avail)
+)
+R.check(
+    "fixed-speed: what pricing a cycle adds to a plan's score is the cycling "
+    "term plus cycling_cost x the switch weight of the shipped levels",
+    _dsp_dl.switch_weight(_dsp_fx.space, _dsp_fx.dhw, _DSP_PAIR, 5.5, 5.5) > 0
+    and abs(_dsp_fx_score - _dsp_fx_unpriced - _dsp_fx_level_terms) < 1e-9,
+    f"{_dsp_fx_score - _dsp_fx_unpriced} vs {_dsp_fx_level_terms}",
+)
+R.check(
+    "fixed-speed: the batch objective is the scalar one bit for bit with a "
+    "priced pair and a vector",
+    float(
+        _dsp_fx_batch(np.stack([_dsp_fx.space, _dsp_fx.space]), _dsp_fx.dhw, None, _dsp_fx_avail)[1]
+    ) == _dsp_fx_score,
+)
+_dsp_quiet = _dsp_solve(_DSP_PAIR, _DSP_OFF, legionella_h=200.0)
+R.check(
+    "a priced install whose plan holds no priced switch builds no candidate",
+    _dsp_dl.switch_weight(_dsp_quiet.space, _dsp_quiet.dhw, _DSP_PAIR, 5.5) == 0.0
+    and not _dsp_quiet.bans and len(_dsp_quiet.builds) == 1,
+    f"{len(_dsp_quiet.bans)} banned build(s) of {len(_dsp_quiet.builds)}",
+)
+# _co_optimize's own candidate: refused, it leaves the incumbent's vector.
+_dsp_co = _dsp_base["fixed-speed"]
+_dsp_co_calls = []
+
+
+def _dsp_co_solve(dhw_plan, warm_start):
+    _dsp_co_calls.append(1)
+    _dsp_co.opt._space_avail = None
+    return np.asarray(warm_start, float), "candidate", 0.0
+
+
+_dsp_co_kept = _dsp_co.opt._space_avail = np.ones(96)
+_dsp_co_out = _dsp_co.opt._co_optimize(
+    _dsp_co.builds[0][2],
+    space_power=_dsp_co.solved[0][0],
+    dhw_power=np.asarray(_dsp_co.builds[0][1][0].schedule, float),
+    status="first", best_score=-1e9, solve_space=_dsp_co_solve, p_max=5.5,
+    planner=_dsp_co.builds[0][3],
+)
+R.check(
+    "a refused co-optimisation candidate leaves the vector its incumbent was "
+    "scored with",
+    len(_dsp_co_calls) == 1 and _dsp_co_out[2] == "first"
+    and _dsp_co.opt._space_avail is _dsp_co_kept,
+    f"{len(_dsp_co_calls)} candidate solve(s), status {_dsp_co_out[2]}",
+)
+# _co_optimize's headroom is the charged bound: on a duty-cycle install heating
+# solved hard against avail x p_max - dhw wanted more than it could have, so
+# the step is pinned and hot water is re-planned against a full compressor.
+_dsp_hr_dhw = np.zeros(96)
+_dsp_hr_dhw[40] = 2.0
+_dsp_hr_avail = np.ones(96)
+_dsp_hr_avail[40] = 1.0 - _dsp_dl.lost_share(_DSP_PAIR, _DSP_OFF)
+_dsp_hr_at_bound = np.zeros(96)
+_dsp_hr_at_bound[40] = _dsp_hr_avail[40] * 5.5 - 2.0
+_dsp_hr_at_bound[41] = 2.0
+_dsp_hr_at_plain = _dsp_hr_at_bound.copy()
+_dsp_hr_at_plain[40] = 5.5 - 2.0
+
+
+def _dsp_hr_demand(space, avail, **install):
+    """The space demand ``_co_optimize`` hands its replan, ``None`` when it builds none."""
+    opt = _dsp_opt(_DSP_PAIR, _DSP_OFF, **install)
+    opt._space_avail = avail
+    seen = []
+
+    def build(h, **kw):
+        seen.append(np.asarray(kw["space_demand"], float))
+        return _DspNS(schedule=_dsp_hr_dhw.copy()), None
+
+    opt._co_optimize(
+        _dsp_co.builds[0][2], space_power=space, dhw_power=_dsp_hr_dhw,
+        status="first", best_score=0.0, solve_space=_dsp_g_raises, p_max=5.5,
+        planner=_DspNS(
+            _dhw_coil_wood_forecast=lambda *a: None, _build_dhw_requirements=build
+        ),
+    )
+    return seen[0] if seen else None
+
+
+_dsp_hr_pinned = _dsp_hr_demand(_dsp_hr_at_bound, _dsp_hr_avail)
+R.check(
+    "the co-optimisation reads the charged bound: on a duty-cycle install "
+    "heating at avail x p_max - dhw in a charged step is pinned, and the "
+    "replan is built against a full compressor there and nowhere else",
+    _dsp_hr_at_bound[40] < 5.5 - 2.0 - 1e-3
+    and _dsp_hr_pinned is not None
+    and np.flatnonzero(_dsp_hr_pinned == 5.5).tolist() == [40]
+    and _dsp_hr_pinned[41] == 2.0,
+    f"{None if _dsp_hr_pinned is None else np.flatnonzero(_dsp_hr_pinned == 5.5).tolist()}",
+)
+R.check(
+    "null controls: the same heating with no vector, or with the vector on a "
+    "clamped install whose bound carries no lost time, is under its bound and "
+    "builds no replan; at the uncharged bound each of the two builds one",
+    _dsp_hr_demand(_dsp_hr_at_bound, None) is None
+    and _dsp_hr_demand(_dsp_hr_at_bound, _dsp_hr_avail, clamp=True) is None
+    and _dsp_hr_demand(_dsp_hr_at_plain, None) is not None
+    and _dsp_hr_demand(_dsp_hr_at_plain, _dsp_hr_avail, clamp=True) is not None,
+)
+
+# The candidate pass is not for a combi store, whose hot-water plan is a
+# feasibility repair scored with no buffer flux: nothing is built or solved.
+import heatpump_optimizer.mixing_valve as _dsp_mv  # noqa: E402
+
+
+def _dsp_combi_pass(combi):
+    """What the candidate pass asks of its planner on a store-buffer install."""
+    params = _DspTP(
+        buffer_tank_volume=504.0, mixing_valve_mode=_dsp_mv.MODE_SMART_WRITE,
+        dhw_enabled=True, dhw_tank_volume=200.0, dhw_combi_tank_enabled=combi,
+    )
+    params.min_electrical_power, params.max_electrical_power = 1.5, 5.5
+    cfg = _DspCfg(cycling_cost=0.3)
+    cfg.duty_switch_stop_probability, cfg.duty_switch_off_seconds = _DSP_PAIR, _DSP_OFF
+    opt = _DspOpt(_DspTM(params), cfg)
+    opt._dhw_requirement, opt._space_avail = _dsp_leg_req, _dsp_g_avail
+    asked = []
+
+    def build(h, **kw):
+        asked.append(kw.get("placement_ban"))
+        raise RuntimeError("the fixture's build")
+
+    out = _dsp_om._avoid_priced_switches(
+        opt, _dsp_leg_h,
+        _DspNS(_dhw_coil_wood_forecast=lambda *a: asked.append(None), _build_dhw_requirements=build),
+        _dsp_g_raises, lambda *a: 0.0, 5.5, _dsp_g_incumbent,
+    )
+    return opt.model.params.dhw_store.combi, out, asked, opt
+
+
+_dsp_combi_on, _dsp_combi_off = _dsp_combi_pass(True), _dsp_combi_pass(False)
+R.check(
+    "on a combi store the candidate pass asks its planner nothing and returns "
+    "the incumbent, its requirement and its availability in place, on an "
+    "incumbent holding a priced switch",
+    _dsp_combi_on[0] is True and _dsp_combi_on[1] is _dsp_g_incumbent
+    and _dsp_combi_on[2] == []
+    and _dsp_combi_on[3]._dhw_requirement is _dsp_leg_req
+    and _dsp_combi_on[3]._space_avail is _dsp_g_avail,
+    f"combi {_dsp_combi_on[0]}, {len(_dsp_combi_on[2])} planner call(s)",
+)
+R.check(
+    "null control: the same install with the store's hot water in its own "
+    "tank reaches the banned build",
+    _dsp_combi_off[0] is False and _dsp_combi_off[1] is _dsp_g_incumbent
+    and len(_dsp_combi_off[2]) == 2 and _dsp_combi_off[2][1] is not None,
+    f"combi {_dsp_combi_off[0]}, {len(_dsp_combi_off[2])} planner call(s)",
+)
+
+
+# 7. The learner's side: the bound on the decayed count, and the read the
+# planner prices by. Everything below needs the predecessor's module.
+import json  # noqa: E402
+
+from heatpump_optimizer import duty_switch as _dsp_ds, pump_mode as _dsp_pm  # noqa: E402
+
+_DSP_DAY = datetime(2026, 11, 10, tzinfo=UTC)
+
+
+def _dsp_stop(learner, at, off_s):
+    """One hot water to heating switch at ``at`` that stops the compressor 19 s
+    later, void-checked on the next pass, restarting after ``off_s``."""
+    ctx = _dsp_ds.SwitchContext(
+        mode_written_at=at, last_write_at=at, inlet_c=44.2, water_setpoint_c=32.0,
+        target_demand=True, plan_stays=True)
+    learner.mode_write(at, _dsp_pm.MODE_DHW, _dsp_pm.MODE_HEAT, True, ctx)
+    learner.edge(at + timedelta(seconds=19), False)
+    learner.note_pass(at + timedelta(seconds=60), ctx, False)
+    learner.edge(at + timedelta(seconds=19 + off_s), True)
+
+
+def _dsp_dir(k, kept_w, usable=True, off_s=()):
+    return _dsp_ds.Direction(k=k, kept_w=kept_w, decayed_at=_DSP_DAY, first_day=_DSP_DAY.date(),
+                 last_day=_DSP_DAY.date() + timedelta(days=1), usable=usable, off_s=list(off_s))
+
+
+def _dsp_kept(count, days=0):
+    """A direction latched at the cap on stops alone, then ``count`` kept
+    episodes at one instant, then aged ``days``; and the largest n it held."""
+    d = _dsp_dir(_dsp_ds.N_CAP, 0.0)
+    held = d.n
+    for _ in range(count):
+        d.book(_DSP_DAY, False, None)
+        held = max(held, d.n)
+    d.decay(_DSP_DAY + timedelta(days=days))
+    return d, held
+
+
+_dsp_fill = _dsp_ds.Direction()
+_dsp_fill_n = []
+for _dsp_i in range(40):
+    _dsp_fill.book(_DSP_DAY + timedelta(hours=_dsp_i), _dsp_i % 3 != 0, 501.0)
+    _dsp_fill_n.append(_dsp_fill.n)
+R.check(
+    "the decayed count is held at the cap, twice the on-threshold: forty "
+    "bookings an hour apart end on it and none leaves it above (to 1e-9, the "
+    "rounding of two scaled addends)",
+    _dsp_ds.N_CAP == 10.0 == 2 * _dsp_ds.N_ON
+    and max(_dsp_fill_n) <= _dsp_ds.N_CAP + 1e-9 and abs(_dsp_fill_n[-1] - _dsp_ds.N_CAP) < 0.05
+    and _dsp_fill_n[8] < _dsp_ds.N_CAP - 0.5,
+    f"largest n {max(_dsp_fill_n)!r}, last {_dsp_fill_n[-1]!r}, after nine {_dsp_fill_n[8]!r}",
+)
+_dsp_mix = _dsp_dir(6.0, 4.0)
+_dsp_mix.book(_DSP_DAY, True, None)
+R.check(
+    "the cap scales both counts alike: a stop booked on six of ten leaves "
+    "p at seven of eleven",
+    abs(_dsp_mix.p - 7.0 / 11.0) < 1e-12 and abs(_dsp_mix.n - _dsp_ds.N_CAP) < 1e-9,
+    f"p={_dsp_mix.p!r} n={_dsp_mix.n!r}",
+)
+_dsp_k12, _dsp_k12_held = _dsp_kept(12)
+_dsp_k13, _dsp_k13_held = _dsp_kept(13)
+R.check(
+    "from p = 1 at the cap the latch holds after twelve kept episodes and "
+    "drops at the thirteenth, each multiplying p by 10/11",
+    _dsp_k12.usable and not _dsp_k13.usable
+    and abs(_dsp_k12.p - (10.0 / 11.0) ** 12) < 1e-9 and abs(_dsp_k13.p - (10.0 / 11.0) ** 13) < 1e-9
+    and max(_dsp_k12_held, _dsp_k13_held) <= _dsp_ds.N_CAP + 1e-9,
+    f"p after 12 {_dsp_k12.p!r} usable={_dsp_k12.usable}; after 13 {_dsp_k13.p!r} usable={_dsp_k13.usable}",
+)
+R.check(
+    "with no episodes a capped direction is latched at 28 days and not the day after",
+    _dsp_kept(0, 28)[0].usable and not _dsp_kept(0, 29)[0].usable,
+    f"n at 28 days {_dsp_kept(0, 28)[0].n!r}, at 29 {_dsp_kept(0, 29)[0].n!r}",
+)
+_dsp_rt = _dsp_ds.DutySwitchLearner({"dhw_space": _dsp_k12, "space_dhw": _dsp_fill})
+_dsp_rt_back = _dsp_ds.DutySwitchLearner.from_record(json.loads(json.dumps(_dsp_rt.stored_record())))
+R.check(
+    "a capped record round-trips through its stored form",
+    _dsp_rt_back.directions == _dsp_rt.directions and _dsp_rt_back.directions["dhw_space"].usable,
+    f"{_dsp_rt_back.directions}",
+)
+
+# The read: both pairs in the leaf's order, zeros unless the stored latch is on.
+_dsp_table = _dsp_ds.DutySwitchLearner()
+for _dsp_i in range(6):
+    _dsp_stop(_dsp_table, _DSP_DAY + timedelta(hours=7 * _dsp_i), 501)
+R.check(
+    "six stopping switches over two days, each off 501 s, latch the direction "
+    "and the planner reads the acceptance fixture's pairs from the learner",
+    _dsp_table.directions["dhw_space"].usable
+    and _dsp_table.planner_pairs() == (_DSP_PAIR, _DSP_OFF),
+    f"{_dsp_table.planner_pairs()} against {(_DSP_PAIR, _DSP_OFF)}",
+)
+_DSP_LEARNERS = {
+    "an empty learner": _dsp_ds.DutySwitchLearner(),
+    "a learner under its on-threshold, off times stored": _dsp_ds.DutySwitchLearner(
+        {"dhw_space": _dsp_dir(4.0, 0.0, usable=False, off_s=[501.0, 492.0]), "space_dhw": _dsp_ds.Direction()}),
+    "an install whose every switch was kept": _dsp_ds.DutySwitchLearner(
+        {"dhw_space": _dsp_dir(0.0, 10.0, usable=False), "space_dhw": _dsp_dir(0.0, 10.0, usable=False)}),
+}
+R.check(
+    "the read returns zeros while a direction is unlatched, its off times with it",
+    all(l.planner_pairs() == ((0.0, 0.0), (0.0, 0.0)) for l in _DSP_LEARNERS.values()),
+    f"{ {n: l.planner_pairs() for n, l in _DSP_LEARNERS.items()} }",
+)
+_dsp_two = _dsp_ds.DutySwitchLearner({
+    "dhw_space": _dsp_dir(3.0, 1.0, off_s=[400.0, 501.0, 620.0, 700.0]),
+    "space_dhw": _dsp_dir(2.0, 2.0),
+})
+R.check(
+    "a latched direction reads its own p and median off time in its own slot, "
+    "hot water to heating first, and no off time while every stop's was censored",
+    _dsp_two.planner_pairs() == ((0.75, 0.5), (560.5, 0.0)),
+    f"{_dsp_two.planner_pairs()}",
+)
+
+# 4, the learner arm: each null state's read, handed to a full optimize.
+_dsp_arm_bad = []
+for _dsp_name, _dsp_kw in _DSP_INSTALLS.items():
+    for _dsp_label, _dsp_l in _DSP_LEARNERS.items():
+        _dsp_null = _dsp_solve(*_dsp_l.planner_pairs(), **_dsp_kw)
+        if (
+            not _dsp_same_plan(_dsp_null, _dsp_base[_dsp_name])
+            or _dsp_null.bans or _dsp_null.opt._space_avail is not None
+            or len(_dsp_null.builds) != len(_dsp_base[_dsp_name].builds)
+        ):
+            _dsp_arm_bad.append((_dsp_name, _dsp_label))
+R.check(
+    "null controls from learner state: an empty learner, one under its "
+    "on-threshold and an install whose every switch was kept each read a plan "
+    "identical to today's on all three install classes",
+    not _dsp_arm_bad,
+    f"{_dsp_arm_bad}",
+)
+R.check(
+    "and that arm has something to detect: the latched learner's read returns "
+    "the priced plan on every install class",
+    all(_dsp_same_plan(_dsp_solve(*_dsp_table.planner_pairs(), **kw), _dsp_priced[n])
+        for n, kw in _DSP_INSTALLS.items()),
+)
+
+
 sys.exit(R.close("FEATURE CHECKS"))
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index db62936365..a107b76be2 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -67,6 +67,7 @@
 # v7.1.15: Supply minimum run and pause, valve target label, boost settling, card folds. The stamp empties the list; the
 # next branch restates its own footprint, claims included.
 #
+config_flow # R10-OUTSIDE-DHW-START-HYSTERESIS: the entities_pump page gains the two start-hysteresis pickers (space_hysteresis_entity, dhw_hysteresis_entity), so the plain render, the seeded render and the seed each gain those two keys; every leaf that moves is "present on one side only" and ADDED at this head. Float-free and compared exactly, so re-recorded in the committed file (golden.py --record --only config_flow). No plan reads the options unset: the other 55 fixtures are byte-identical to the merge base (env_drift.py --all, one environment), which is the null.
 # may-drift: flat_prices -- #1208 polish-every-candidate, owner ruling #1208 comment 208bed25
 # (option (a)): the move's margin is inside the noise band (objective rel
 # -1.2171e-03, deterministic on one box), so which runner sees it move is the
diff --git a/tests/golden/config_flow.json b/tests/golden/config_flow.json
index 1b36fae2fe..19f6075781 100644
--- a/tests/golden/config_flow.json
+++ b/tests/golden/config_flow.json
@@ -1048,6 +1048,7 @@
   "dhw_disinfection_switch_entity": "sensor.seed_dhw_disinfection_switch_entity",
   "dhw_elastic_legionella_enabled": true,
   "dhw_free_disinfection_enabled": true,
+  "dhw_hysteresis_entity": "sensor.seed_dhw_hysteresis_entity",
   "dhw_inlet_entity": "sensor.seed_dhw_inlet_entity",
   "dhw_legionella_enabled": true,
   "dhw_quantile_targets_enabled": true,
@@ -1110,6 +1111,7 @@
   "solar_aperture_learning_enabled": true,
   "solar_radiation_entity": "sensor.seed_solar_radiation_entity",
   "space_circulation_pump_entity": "sensor.seed_space_circulation_pump_entity",
+  "space_hysteresis_entity": "sensor.seed_space_hysteresis_entity",
   "space_setpoint_entity": "sensor.seed_space_setpoint_entity",
   "staleness_watchdog_enabled": true,
   "system_identification_enabled": true,
@@ -2315,6 +2317,14 @@
     "required": "Optional",
     "selector": "SelectSelector"
    },
+   "dhw_hysteresis_entity": {
+    "config": {
+     "filter": "[{'domain': ['sensor', 'number', 'input_number']}]"
+    },
+    "default": "'sensor.seed_dhw_hysteresis_entity'",
+    "required": "Optional",
+    "selector": "EntitySelector"
+   },
    "heat_pump_backup_heater_entity": {
     "config": {
      "filter": "[{'domain': ['binary_sensor', 'switch', 'input_boolean', 'sensor']}]"
@@ -2396,6 +2406,14 @@
     "default": "'off'",
     "required": "Optional",
     "selector": "SelectSelector"
+   },
+   "space_hysteresis_entity": {
+    "config": {
+     "filter": "[{'domain': ['sensor', 'number', 'input_number']}]"
+    },
+    "default": "'sensor.seed_space_hysteresis_entity'",
+    "required": "Optional",
+    "selector": "EntitySelector"
    }
   },
   "factory_reset": {
@@ -5027,6 +5045,14 @@
    "required": "Optional",
    "selector": "SelectSelector"
   },
+  "dhw_hysteresis_entity": {
+   "config": {
+    "filter": "[{'domain': ['sensor', 'number', 'input_number']}]"
+   },
+   "default": null,
+   "required": "Optional",
+   "selector": "EntitySelector"
+  },
   "heat_pump_backup_heater_entity": {
    "config": {
     "filter": "[{'domain': ['binary_sensor', 'switch', 'input_boolean', 'sensor']}]"
@@ -5108,6 +5134,14 @@
    "default": "'off'",
    "required": "Optional",
    "selector": "SelectSelector"
+  },
+  "space_hysteresis_entity": {
+   "config": {
+    "filter": "[{'domain': ['sensor', 'number', 'input_number']}]"
+   },
+   "default": null,
+   "required": "Optional",
+   "selector": "EntitySelector"
   }
  },
  "factory_reset": {
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.BOOLOP.3f0ec24b.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.BOOLOP.3f0ec24b.json
new file mode 100644
index 0000000000..7ad128228f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.BOOLOP.3f0ec24b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._solve_hubs BOOLOP 3f0ec24b",
+  "killed_by": "tests/features.py",
+  "old": "        if self._outage_recovery_active(now) and not np.isfinite(threshold):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if self._outage_recovery_active(now) or not np.isfinite(threshold):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.BOOLOP.855f1fe1.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.BOOLOP.855f1fe1.json
deleted file mode 100644
index 730dc42456..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.BOOLOP.855f1fe1.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._solve_hubs BOOLOP 855f1fe1",
-  "killed_by": "tests/features.py",
-  "old": "        if self._outage_recovery_active(dt_util.now()) and not np.isfinite(threshold):",
-  "reason": "Recorded by hand for R9-EG-B1 (#1736) on the branch worktree, 2026-10-04, because `mutation_table.py --pin-killed` refuses on this machine (tests/features.py's baseline is red for the environment: R9-F2.1 P3, BLAS; green on CI). The drive is mutation_table's own pool, mutant application, driver invocation and kill rule, run with the red baseline kept: a kill is a failing-check count the unmutated baseline does not already have, here against 1913f0dd736cb66b800b5eabfa6973a917459d83: BOOLOP (`if self._outage_recovery_active(dt_util.now()) or not np.isfinite(threshold):`) took tests/features.py from rc=1 failed=2 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.GUARD_OFF.3f0ec24b.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.GUARD_OFF.3f0ec24b.json
new file mode 100644
index 0000000000..98e0d67655
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.GUARD_OFF.3f0ec24b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._solve_hubs GUARD_OFF 3f0ec24b",
+  "killed_by": "tests/features.py",
+  "old": "        if self._outage_recovery_active(now) and not np.isfinite(threshold):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.GUARD_OFF.855f1fe1.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.GUARD_OFF.855f1fe1.json
deleted file mode 100644
index 68a52c8a16..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.GUARD_OFF.855f1fe1.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._solve_hubs GUARD_OFF 855f1fe1",
-  "killed_by": "tests/features.py",
-  "old": "        if self._outage_recovery_active(dt_util.now()) and not np.isfinite(threshold):",
-  "reason": "Recorded by hand for R9-EG-B1 (#1736) on the branch worktree, 2026-10-04, because `mutation_table.py --pin-killed` refuses on this machine (tests/features.py's baseline is red for the environment: R9-F2.1 P3, BLAS; green on CI). The drive is mutation_table's own pool, mutant application, driver invocation and kill rule, run with the red baseline kept: a kill is a failing-check count the unmutated baseline does not already have, here against 1913f0dd736cb66b800b5eabfa6973a917459d83: GUARD_OFF (`if False:`) took tests/features.py from rc=1 failed=2 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/@module.CONST.c95e30be.json b/tests/mutation_ledger/killed_by/dhw_planner.py/@module.CONST.c95e30be.json
new file mode 100644
index 0000000000..6778cf2e61
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/@module.CONST.c95e30be.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:<module> CONST c95e30be",
+  "killed_by": "tests/block_duty.py",
+  "old": "STARTABLE_ROUNDS = 8",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`STARTABLE_ROUNDS = 16`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._ctx_clamp.CMP_BOUND.0b090e57.json b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._ctx_clamp.CMP_BOUND.0b090e57.json
new file mode 100644
index 0000000000..5acd71ffd6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._ctx_clamp.CMP_BOUND.0b090e57.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._ctx_clamp CMP_BOUND 0b090e57",
+  "killed_by": "tests/block_duty.py",
+  "old": "        return np.where(plan < ctx.min_run_power - 1e-9, 0.0, plan)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return np.where(plan <= ctx.min_run_power - 1e-9, 0.0, plan)`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._ctx_clamp.RETURN_DEL.0b090e57.json b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._ctx_clamp.RETURN_DEL.0b090e57.json
new file mode 100644
index 0000000000..895b576fa9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._ctx_clamp.RETURN_DEL.0b090e57.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._ctx_clamp RETURN_DEL 0b090e57",
+  "killed_by": "tests/manual_plan.py",
+  "old": "        return np.where(plan < ctx.min_run_power - 1e-9, 0.0, plan)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/_with_placement_ban.RETURN_DEL.d48232ce.json b/tests/mutation_ledger/killed_by/dhw_planner.py/_with_placement_ban.RETURN_DEL.d48232ce.json
new file mode 100644
index 0000000000..824fb6b1d7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/_with_placement_ban.RETURN_DEL.d48232ce.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:_with_placement_ban RETURN_DEL d48232ce",
+  "killed_by": "tests/manual_plan.py",
+  "old": "    return forced_off if ban is None else _forced_off_with(forced_off, ban, n_steps)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.BOOLOP.6c096d09.json b/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.BOOLOP.6c096d09.json
new file mode 100644
index 0000000000..ab09d83fe4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.BOOLOP.6c096d09.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps BOOLOP 6c096d09",
+  "killed_by": "tests/block_duty.py",
+  "old": "    if cycle_step is not None and 0 <= cycle_step < n_steps:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if cycle_step is not None or 0 <= cycle_step < n_steps:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.CMP_BOUND.6c096d09.json b/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.CMP_BOUND.6c096d09.json
new file mode 100644
index 0000000000..d702531e8c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.CMP_BOUND.6c096d09.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps CMP_BOUND 6c096d09",
+  "killed_by": "tests/block_duty.py",
+  "old": "    if cycle_step is not None and 0 <= cycle_step < n_steps:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if cycle_step is not None and 0 < cycle_step < n_steps:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.6c096d09.json b/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.6c096d09.json
new file mode 100644
index 0000000000..3a532a0795
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.6c096d09.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps GUARD_OFF 6c096d09",
+  "killed_by": "tests/block_duty.py",
+  "old": "    if cycle_step is not None and 0 <= cycle_step < n_steps:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.cccafcc1.json b/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.cccafcc1.json
new file mode 100644
index 0000000000..a26a52429d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.cccafcc1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps GUARD_OFF cccafcc1",
+  "killed_by": "tests/manual_plan.py",
+  "old": "    if everyday is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.RETURN_DEL.87df096e.json b/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.RETURN_DEL.87df096e.json
new file mode 100644
index 0000000000..5ed862def7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.RETURN_DEL.87df096e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps RETURN_DEL 87df096e",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return start",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.064a19f6.json b/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.064a19f6.json
new file mode 100644
index 0000000000..a4e8b3a54d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.064a19f6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:drop_unstartable CMP_BOUND 064a19f6",
+  "killed_by": "tests/block_duty.py",
+  "old": "        if temps_of(plan)[i] >= start_below[i]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if temps_of(plan)[i] > start_below[i]:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.b56fd264.json b/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.b56fd264.json
new file mode 100644
index 0000000000..3d43b90b16
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.b56fd264.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:drop_unstartable CMP_BOUND b56fd264",
+  "killed_by": "tests/block_duty.py",
+  "old": "    on = plan > 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`on = plan >= 0.0`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.GUARD_OFF.064a19f6.json b/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.GUARD_OFF.064a19f6.json
new file mode 100644
index 0000000000..f68b057eb8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.GUARD_OFF.064a19f6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:drop_unstartable GUARD_OFF 064a19f6",
+  "killed_by": "tests/block_duty.py",
+  "old": "        if temps_of(plan)[i] >= start_below[i]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.RETURN_DEL.c913c48e.json b/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.RETURN_DEL.c913c48e.json
new file mode 100644
index 0000000000..bba12cc624
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.RETURN_DEL.c913c48e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:drop_unstartable RETURN_DEL c913c48e",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return plan",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.99a579b8.json b/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.99a579b8.json
new file mode 100644
index 0000000000..a9e44056f4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.99a579b8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:place_startable GUARD_OFF 99a579b8",
+  "killed_by": "tests/manual_plan.py",
+  "old": "    if start_below is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.e4a2bfaa.json b/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.e4a2bfaa.json
new file mode 100644
index 0000000000..0c4ceb6b59
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.e4a2bfaa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:place_startable GUARD_OFF e4a2bfaa",
+  "killed_by": "tests/block_duty.py",
+  "old": "        if np.array_equal(fixed, plan):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.RETURN_DEL.68208daf.json b/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.RETURN_DEL.68208daf.json
new file mode 100644
index 0000000000..9e7ca6a749
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.RETURN_DEL.68208daf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:place_startable RETURN_DEL 68208daf",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return drop_unstartable(plan, start_below, temps_of)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.BOOLOP.3d3ec5bc.json b/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.BOOLOP.3d3ec5bc.json
new file mode 100644
index 0000000000..6443097405
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.BOOLOP.3d3ec5bc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps BOOLOP 3d3ec5bc",
+  "killed_by": "tests/block_duty.py",
+  "old": "        under_way = bool(on[i] and ok[i])",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`under_way = bool(on[i] or ok[i])`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.1edfe326.json b/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.1edfe326.json
new file mode 100644
index 0000000000..f11e540a53
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.1edfe326.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps CMP_BOUND 1edfe326",
+  "killed_by": "tests/block_duty.py",
+  "old": "    on = np.asarray(plan, dtype=float) > 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`on = np.asarray(plan, dtype=float) >= 0.0`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.6e3a088f.json b/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.6e3a088f.json
new file mode 100644
index 0000000000..94c3474d95
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.6e3a088f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps CMP_BOUND 6e3a088f",
+  "killed_by": "tests/block_duty.py",
+  "old": "    ok: np.ndarray = np.asarray(temps, dtype=float)[: on.size] < start_below[: on.size]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`ok: np.ndarray = np.asarray(temps, dtype=float)[: on.size] <= start_below[: on.size]`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.GUARD_OFF.99a579b8.json b/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.GUARD_OFF.99a579b8.json
new file mode 100644
index 0000000000..26c5b81261
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.GUARD_OFF.99a579b8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps GUARD_OFF 99a579b8",
+  "killed_by": "tests/manual_plan.py",
+  "old": "    if start_below is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.RETURN_DEL.82bc35de.json b/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.RETURN_DEL.82bc35de.json
new file mode 100644
index 0000000000..1fc93528fd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.RETURN_DEL.82bc35de.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps RETURN_DEL 82bc35de",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return ok",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/@module.CONST.eef42148.json b/tests/mutation_ledger/killed_by/duty_legs.py/@module.CONST.eef42148.json
new file mode 100644
index 0000000000..77e37b81a7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/@module.CONST.eef42148.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:<module> CONST eef42148",
+  "killed_by": "tests/features.py",
+  "old": "SPLIT_MIN_MINUTES = 5.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`SPLIT_MIN_MINUTES = 10.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=27."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/_runs.CMP_BOUND.2759517c.json b/tests/mutation_ledger/killed_by/duty_legs.py/_runs.CMP_BOUND.2759517c.json
new file mode 100644
index 0000000000..ac236d62b2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/_runs.CMP_BOUND.2759517c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:_runs CMP_BOUND 2759517c",
+  "killed_by": "tests/features.py",
+  "old": "    on = kw > MIN_RUNNING_DRAW_KW",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`on = kw >= MIN_RUNNING_DRAW_KW`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/_runs.CMP_BOUND.ad1b10bc.json b/tests/mutation_ledger/killed_by/duty_legs.py/_runs.CMP_BOUND.ad1b10bc.json
new file mode 100644
index 0000000000..f0a0669888
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/_runs.CMP_BOUND.ad1b10bc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:_runs CMP_BOUND ad1b10bc",
+  "killed_by": "tests/features.py",
+  "old": "    return on if floor is None else on & ~(kw < floor)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return on if floor is None else on & ~(kw <= floor)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=13."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/_runs.RETURN_DEL.ad1b10bc.json b/tests/mutation_ledger/killed_by/duty_legs.py/_runs.RETURN_DEL.ad1b10bc.json
new file mode 100644
index 0000000000..53a11e8033
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/_runs.RETURN_DEL.ad1b10bc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:_runs RETURN_DEL ad1b10bc",
+  "killed_by": "tests/features.py",
+  "old": "    return on if floor is None else on & ~(kw < floor)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/availability.CMP_BOUND.7944d7be.json b/tests/mutation_ledger/killed_by/duty_legs.py/availability.CMP_BOUND.7944d7be.json
new file mode 100644
index 0000000000..a9bfee0d6f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/availability.CMP_BOUND.7944d7be.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:availability CMP_BOUND 7944d7be",
+  "killed_by": "tests/features.py",
+  "old": "    if not lost > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if not lost >= 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.GUARD_OFF.4f254e46.json b/tests/mutation_ledger/killed_by/duty_legs.py/availability.GUARD_OFF.7944d7be.json
similarity index 53%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_share.GUARD_OFF.4f254e46.json
rename to tests/mutation_ledger/killed_by/duty_legs.py/availability.GUARD_OFF.7944d7be.json
index 076c143a46..5fe8ddf5cc 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.GUARD_OFF.4f254e46.json
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/availability.GUARD_OFF.7944d7be.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_share GUARD_OFF 4f254e46",
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:availability GUARD_OFF 7944d7be",
   "killed_by": "tests/features.py",
-  "old": "    if PLAN_STEP_MINUTES - dhw_min < SPLIT_MIN_MINUTES:",
+  "old": "    if not lost > 0:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/availability.GUARD_OFF.c8a3376c.json b/tests/mutation_ledger/killed_by/duty_legs.py/availability.GUARD_OFF.c8a3376c.json
new file mode 100644
index 0000000000..4c0fa43148
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/availability.GUARD_OFF.c8a3376c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:availability GUARD_OFF c8a3376c",
+  "killed_by": "tests/features.py",
+  "old": "    if not charged.any():",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/availability.RETURN_DEL.1e8a99b4.json b/tests/mutation_ledger/killed_by/duty_legs.py/availability.RETURN_DEL.1e8a99b4.json
new file mode 100644
index 0000000000..8b77a58bd7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/availability.RETURN_DEL.1e8a99b4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:availability RETURN_DEL 1e8a99b4",
+  "killed_by": "tests/features.py",
+  "old": "    return np.where(charged, 1.0 - lost, 1.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=14."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.CMP_BOUND.8cc0b854.json b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.CMP_BOUND.8cc0b854.json
new file mode 100644
index 0000000000..5b9f922606
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.CMP_BOUND.8cc0b854.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:both_step_legs CMP_BOUND 8cc0b854",
+  "killed_by": "tests/features.py",
+  "old": "    if dhw_min < SPLIT_MIN_MINUTES:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if dhw_min <= SPLIT_MIN_MINUTES:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.CMP_BOUND.b7055f00.json b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.CMP_BOUND.b7055f00.json
new file mode 100644
index 0000000000..281083ad1c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.CMP_BOUND.b7055f00.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:both_step_legs CMP_BOUND b7055f00",
+  "killed_by": "tests/features.py",
+  "old": "    if step_minutes - dhw_min < SPLIT_MIN_MINUTES:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if step_minutes - dhw_min <= SPLIT_MIN_MINUTES:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.GUARD_OFF.8cc0b854.json b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.GUARD_OFF.8cc0b854.json
new file mode 100644
index 0000000000..8bf42582fa
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.GUARD_OFF.8cc0b854.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:both_step_legs GUARD_OFF 8cc0b854",
+  "killed_by": "tests/features.py",
+  "old": "    if dhw_min < SPLIT_MIN_MINUTES:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.GUARD_OFF.b7055f00.json b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.GUARD_OFF.b7055f00.json
new file mode 100644
index 0000000000..a78fee0176
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.GUARD_OFF.b7055f00.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:both_step_legs GUARD_OFF b7055f00",
+  "killed_by": "tests/features.py",
+  "old": "    if step_minutes - dhw_min < SPLIT_MIN_MINUTES:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.RETURN_DEL.123675c1.json b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.RETURN_DEL.123675c1.json
new file mode 100644
index 0000000000..fa73675963
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.RETURN_DEL.123675c1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:both_step_legs RETURN_DEL 123675c1",
+  "killed_by": "tests/features.py",
+  "old": "    return ((\"dhw\", dhw_min), (\"space\", step_minutes - dhw_min))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/delivered_space.CLAMP_DROP.e5a67d12.json b/tests/mutation_ledger/killed_by/duty_legs.py/delivered_space.CLAMP_DROP.e5a67d12.json
new file mode 100644
index 0000000000..26a3168afc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/delivered_space.CLAMP_DROP.e5a67d12.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:delivered_space CLAMP_DROP e5a67d12",
+  "killed_by": "tests/features.py",
+  "old": "    delivered: np.ndarray = np.maximum(0.0, space_kw - (1.0 - avail) * (space_kw + dhw_kw))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`delivered: np.ndarray = (0.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/delivered_space.GUARD_OFF.756d2076.json b/tests/mutation_ledger/killed_by/duty_legs.py/delivered_space.GUARD_OFF.756d2076.json
new file mode 100644
index 0000000000..5fbb4f2f56
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/delivered_space.GUARD_OFF.756d2076.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:delivered_space GUARD_OFF 756d2076",
+  "killed_by": "tests/features.py",
+  "old": "    if floor is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/delivered_space.RETURN_DEL.e6a4147a.json b/tests/mutation_ledger/killed_by/duty_legs.py/delivered_space.RETURN_DEL.e6a4147a.json
new file mode 100644
index 0000000000..f14739b0f2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/delivered_space.RETURN_DEL.e6a4147a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:delivered_space RETURN_DEL e6a4147a",
+  "killed_by": "tests/features.py",
+  "old": "    return delivered",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.CMP_BOUND.c6cf73a1.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.CMP_BOUND.c6cf73a1.json
new file mode 100644
index 0000000000..a4272a0a60
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.CMP_BOUND.c6cf73a1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_ends CMP_BOUND c6cf73a1",
+  "killed_by": "tests/features.py",
+  "old": "    to_space = both & (dhw_min < SPLIT_MIN_MINUTES)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`to_space = both & (dhw_min <= SPLIT_MIN_MINUTES)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.CMP_BOUND.d90f16a9.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.CMP_BOUND.d90f16a9.json
new file mode 100644
index 0000000000..f780f7f6c2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.CMP_BOUND.d90f16a9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_ends CMP_BOUND d90f16a9",
+  "killed_by": "tests/features.py",
+  "old": "    to_dhw = both & ~to_space & (step_minutes - dhw_min < SPLIT_MIN_MINUTES)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`to_dhw = both & ~to_space & (step_minutes - dhw_min <= SPLIT_MIN_MINUTES)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.RETURN_DEL.6b97afd0.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.RETURN_DEL.6b97afd0.json
new file mode 100644
index 0000000000..cac585d618
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.RETURN_DEL.6b97afd0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_ends RETURN_DEL 6b97afd0",
+  "killed_by": "tests/features.py",
+  "old": "    return np.where(two, DHW, single), np.where(two, SPACE, single), two",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/lost_share.CLAMP_DROP.2b3e0bf8.json b/tests/mutation_ledger/killed_by/duty_legs.py/lost_share.CLAMP_DROP.2b3e0bf8.json
new file mode 100644
index 0000000000..f52deda746
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/lost_share.CLAMP_DROP.2b3e0bf8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:lost_share CLAMP_DROP 2b3e0bf8",
+  "killed_by": "tests/features.py",
+  "old": "    return min(1.0, stop_probability[0] * off_seconds[0] / (step_minutes * 60.0))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return (1.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/lost_share.RETURN_DEL.2b3e0bf8.json b/tests/mutation_ledger/killed_by/duty_legs.py/lost_share.RETURN_DEL.2b3e0bf8.json
new file mode 100644
index 0000000000..fc492f71dd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/lost_share.RETURN_DEL.2b3e0bf8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:lost_share RETURN_DEL 2b3e0bf8",
+  "killed_by": "tests/features.py",
+  "old": "    return min(1.0, stop_probability[0] * off_seconds[0] / (step_minutes * 60.0))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.BOOLOP.8175604f.json b/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.BOOLOP.8175604f.json
new file mode 100644
index 0000000000..2e112ac8dc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.BOOLOP.8175604f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:priced_pair BOOLOP 8175604f",
+  "killed_by": "tests/features.py",
+  "old": "    a, b = (max(v, 0.0) if math.isfinite(v) and v <= upper else 0.0 for v in pair)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`a, b = (max(v, 0.0) if math.isfinite(v) or v <= upper else 0.0 for v in pair)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.CLAMP_DROP.8175604f.json b/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.CLAMP_DROP.8175604f.json
new file mode 100644
index 0000000000..eac72596e1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.CLAMP_DROP.8175604f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:priced_pair CLAMP_DROP 8175604f",
+  "killed_by": "tests/features.py",
+  "old": "    a, b = (max(v, 0.0) if math.isfinite(v) and v <= upper else 0.0 for v in pair)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`a, b = ((v) if math.isfinite(v) and v <= upper else 0.0 for v in pair)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.CMP_BOUND.8175604f.json b/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.CMP_BOUND.8175604f.json
new file mode 100644
index 0000000000..d51ffb60ea
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.CMP_BOUND.8175604f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:priced_pair CMP_BOUND 8175604f",
+  "killed_by": "tests/features.py",
+  "old": "    a, b = (max(v, 0.0) if math.isfinite(v) and v <= upper else 0.0 for v in pair)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`a, b = (max(v, 0.0) if math.isfinite(v) and v < upper else 0.0 for v in pair)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=24."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.GUARD_OFF.f30e646b.json b/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.GUARD_OFF.f30e646b.json
new file mode 100644
index 0000000000..ae5de54bf4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.GUARD_OFF.f30e646b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:priced_pair GUARD_OFF f30e646b",
+  "killed_by": "tests/features.py",
+  "old": "    if len(pair) != 2:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.RETURN_DEL.8a3f76e4.json b/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.RETURN_DEL.8a3f76e4.json
new file mode 100644
index 0000000000..0f37aa2b17
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.RETURN_DEL.8a3f76e4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:priced_pair RETURN_DEL 8a3f76e4",
+  "killed_by": "tests/plan_view.py",
+  "old": "    return a, b",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.CLAMP_DROP.311fd6bd.json b/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.CLAMP_DROP.311fd6bd.json
new file mode 100644
index 0000000000..cd4f589a5b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.CLAMP_DROP.311fd6bd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:space_headroom CLAMP_DROP 311fd6bd",
+  "killed_by": "tests/features.py",
+  "old": "    charged: np.ndarray = np.maximum(0.0, avail * p_max - dhw_kw)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`charged: np.ndarray = (0.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.CLAMP_DROP.f6750244.json b/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.CLAMP_DROP.f6750244.json
new file mode 100644
index 0000000000..87c84d51eb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.CLAMP_DROP.f6750244.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:space_headroom CLAMP_DROP f6750244",
+  "killed_by": "tests/plan_view.py",
+  "old": "        return np.maximum(0.0, p_max - dhw_kw)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return (0.0)`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.GUARD_OFF.bc40ec59.json b/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.GUARD_OFF.bc40ec59.json
new file mode 100644
index 0000000000..7a9c12aa4b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.GUARD_OFF.bc40ec59.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:space_headroom GUARD_OFF bc40ec59",
+  "killed_by": "tests/plan_view.py",
+  "old": "    if avail is None or floor is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.RETURN_DEL.013354f1.json b/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.RETURN_DEL.013354f1.json
new file mode 100644
index 0000000000..ec5f61af9b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.RETURN_DEL.013354f1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:space_headroom RETURN_DEL 013354f1",
+  "killed_by": "tests/features.py",
+  "old": "    return charged",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.CMP_BOUND.0b540c5f.json b/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.CMP_BOUND.0b540c5f.json
new file mode 100644
index 0000000000..11cd93ab9a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.CMP_BOUND.0b540c5f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:switch_ban CMP_BOUND 0b540c5f",
+  "killed_by": "tests/features.py",
+  "old": "    if stop_probability[1] > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if stop_probability[1] >= 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.CMP_BOUND.44023c38.json b/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.CMP_BOUND.44023c38.json
new file mode 100644
index 0000000000..61fb080bd0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.CMP_BOUND.44023c38.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:switch_ban CMP_BOUND 44023c38",
+  "killed_by": "tests/features.py",
+  "old": "    if stop_probability[0] > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if stop_probability[0] >= 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.GUARD_OFF.0b540c5f.json b/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.GUARD_OFF.0b540c5f.json
new file mode 100644
index 0000000000..c397ca41c3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.GUARD_OFF.0b540c5f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:switch_ban GUARD_OFF 0b540c5f",
+  "killed_by": "tests/features.py",
+  "old": "    if stop_probability[1] > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.GUARD_OFF.44023c38.json b/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.GUARD_OFF.44023c38.json
new file mode 100644
index 0000000000..29c4b165af
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.GUARD_OFF.44023c38.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:switch_ban GUARD_OFF 44023c38",
+  "killed_by": "tests/features.py",
+  "old": "    if stop_probability[0] > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.RETURN_DEL.1f9c227b.json b/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.RETURN_DEL.1f9c227b.json
new file mode 100644
index 0000000000..bfe95e968e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.RETURN_DEL.1f9c227b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:switch_ban RETURN_DEL 1f9c227b",
+  "killed_by": "tests/features.py",
+  "old": "    return ban",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.CLAMP_DROP.22691b9b.json b/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.CLAMP_DROP.22691b9b.json
new file mode 100644
index 0000000000..c15ca2b5b9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.CLAMP_DROP.22691b9b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:switch_weights_batch CLAMP_DROP 22691b9b",
+  "killed_by": "tests/features.py",
+  "old": "    across = stops * np.minimum(level[_BEFORE], level[_AFTER])",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`across = stops * (level[_BEFORE])`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.CMP_BOUND.ba504464.json b/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.CMP_BOUND.ba504464.json
new file mode 100644
index 0000000000..f624b4f139
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.CMP_BOUND.ba504464.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:switch_weights_batch CMP_BOUND ba504464",
+  "killed_by": "tests/features.py",
+  "old": "    if p_max <= 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if p_max < 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.GUARD_OFF.ba504464.json b/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.GUARD_OFF.ba504464.json
new file mode 100644
index 0000000000..b672965db5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.GUARD_OFF.ba504464.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:switch_weights_batch GUARD_OFF ba504464",
+  "killed_by": "tests/features.py",
+  "old": "    if p_max <= 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.RETURN_DEL.8d49450a.json b/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.RETURN_DEL.8d49450a.json
new file mode 100644
index 0000000000..873a7bf127
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.RETURN_DEL.8d49450a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:switch_weights_batch RETURN_DEL 8d49450a",
+  "killed_by": "tests/features.py",
+  "old": "    return row_sums(np.concatenate([inside, across], axis=1)) / p_max",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/Direction.book.GUARD_OFF.3e106b06.json b/tests/mutation_ledger/killed_by/duty_switch.py/Direction.book.GUARD_OFF.3e106b06.json
new file mode 100644
index 0000000000..a620063d0e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/Direction.book.GUARD_OFF.3e106b06.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:Direction.book GUARD_OFF 3e106b06",
+  "killed_by": "tests/features.py",
+  "old": "        if self.n > N_CAP:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.planner_pairs.RETURN_DEL.fc67f05d.json b/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.planner_pairs.RETURN_DEL.fc67f05d.json
new file mode 100644
index 0000000000..a10a5b3c92
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.planner_pairs.RETURN_DEL.fc67f05d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:DutySwitchLearner.planner_pairs RETURN_DEL fc67f05d",
+  "killed_by": "tests/features.py",
+  "old": "        return (read[0].p, read[1].p), (read[0].median_off_s or 0.0, read[1].median_off_s or 0.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/planner_fields.RETURN_DEL.77cc0eae.json b/tests/mutation_ledger/killed_by/duty_switch.py/planner_fields.RETURN_DEL.77cc0eae.json
new file mode 100644
index 0000000000..5d0d9757be
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/planner_fields.RETURN_DEL.77cc0eae.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:planner_fields RETURN_DEL 77cc0eae",
+  "killed_by": "tests/features.py",
+  "old": "    return {\"duty_switch_stop_probability\": stops, \"duty_switch_off_seconds\": off_s}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/@module.CONST.2902e226.json b/tests/mutation_ledger/killed_by/inputs.py/@module.CONST.2902e226.json
new file mode 100644
index 0000000000..efee388ba0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/@module.CONST.2902e226.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:<module> CONST 2902e226",
+  "killed_by": "tests/block_duty.py",
+  "old": "TEMPERATURE_DELTA_MAX_K = 20.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`TEMPERATURE_DELTA_MAX_K = 40.0`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.bounded.BOOLOP.f12dbe4b.json b/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.bounded.BOOLOP.f12dbe4b.json
new file mode 100644
index 0000000000..d2a4fa1668
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.bounded.BOOLOP.f12dbe4b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:SetpointGrid.bounded BOOLOP f12dbe4b",
+  "killed_by": "tests/guard_pins.py",
+  "old": "        if hi is not None and (low is None or hi >= self.on_step(low, rounding=\"up\")):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if hi is not None or (low is None or hi >= self.on_step(low, rounding=\"up\")):`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.bounded.CLAMP_DROP.a2d9a525.json b/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.bounded.CLAMP_DROP.a2d9a525.json
new file mode 100644
index 0000000000..6ca47d7b2f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.bounded.CLAMP_DROP.a2d9a525.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:SetpointGrid.bounded CLAMP_DROP a2d9a525",
+  "killed_by": "tests/block_duty.py",
+  "old": "        value = max(value, floor, low if low is not None else floor)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`value = (value)`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.bounded.CMP_BOUND.f12dbe4b.json b/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.bounded.CMP_BOUND.f12dbe4b.json
new file mode 100644
index 0000000000..418662c1ca
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.bounded.CMP_BOUND.f12dbe4b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:SetpointGrid.bounded CMP_BOUND f12dbe4b",
+  "killed_by": "tests/block_duty.py",
+  "old": "        if hi is not None and (low is None or hi >= self.on_step(low, rounding=\"up\")):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if hi is not None and (low is None or hi > self.on_step(low, rounding=\"up\")):`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.bounded.GUARD_OFF.f12dbe4b.json b/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.bounded.GUARD_OFF.f12dbe4b.json
new file mode 100644
index 0000000000..b682e1134d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.bounded.GUARD_OFF.f12dbe4b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:SetpointGrid.bounded GUARD_OFF f12dbe4b",
+  "killed_by": "tests/block_duty.py",
+  "old": "        if hi is not None and (low is None or hi >= self.on_step(low, rounding=\"up\")):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.on_step.CLAMP_DROP.5ca7e3c5.json b/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.on_step.CLAMP_DROP.5ca7e3c5.json
new file mode 100644
index 0000000000..4f090f520b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.on_step.CLAMP_DROP.5ca7e3c5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:SetpointGrid.on_step CLAMP_DROP 5ca7e3c5",
+  "killed_by": "tests/block_duty.py",
+  "old": "            out = min(out, _on_step(temperature_from_c(hi_c, self.unit), self.step, \"down\"))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`out = (out)`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=13."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.on_step.CLAMP_DROP.c7ccb5e4.json b/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.on_step.CLAMP_DROP.c7ccb5e4.json
new file mode 100644
index 0000000000..d03faf7e28
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.on_step.CLAMP_DROP.c7ccb5e4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:SetpointGrid.on_step CLAMP_DROP c7ccb5e4",
+  "killed_by": "tests/block_duty.py",
+  "old": "            out = max(out, _on_step(temperature_from_c(lo_c, self.unit), self.step, \"up\"))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`out = (out)`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.on_step.GUARD_OFF.1edccb87.json b/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.on_step.GUARD_OFF.1edccb87.json
new file mode 100644
index 0000000000..dd2daac61d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.on_step.GUARD_OFF.1edccb87.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:SetpointGrid.on_step GUARD_OFF 1edccb87",
+  "killed_by": "tests/block_duty.py",
+  "old": "        if hi_c is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=13."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.on_step.GUARD_OFF.27656e08.json b/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.on_step.GUARD_OFF.27656e08.json
new file mode 100644
index 0000000000..e82e153f17
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.on_step.GUARD_OFF.27656e08.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:SetpointGrid.on_step GUARD_OFF 27656e08",
+  "killed_by": "tests/block_duty.py",
+  "old": "        if lo_c is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.on_step.RETURN_DEL.cccd5bed.json b/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.on_step.RETURN_DEL.cccd5bed.json
new file mode 100644
index 0000000000..3fe910b239
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/SetpointGrid.on_step.RETURN_DEL.cccd5bed.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:SetpointGrid.on_step RETURN_DEL cccd5bed",
+  "killed_by": "tests/guard_pins.py",
+  "old": "        return out if converted is None else converted",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/quantise_setpoint_c.CLAMP_DROP.d6c6d067.json b/tests/mutation_ledger/killed_by/inputs.py/quantise_setpoint_c.CLAMP_DROP.d6c6d067.json
deleted file mode 100644
index 8bf2dd89fb..0000000000
--- a/tests/mutation_ledger/killed_by/inputs.py/quantise_setpoint_c.CLAMP_DROP.d6c6d067.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/inputs.py:quantise_setpoint_c CLAMP_DROP d6c6d067",
-  "killed_by": "tests/features.py",
-  "old": "        out = max(out, _on_step(temperature_from_c(lo_c, unit), step, \"up\"))",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against d5cd003111277faa3f2abd7fbe6c9157d2e48ed7: CLAMP_DROP (`out = (out)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/quantise_setpoint_c.CLAMP_DROP.f00b74a6.json b/tests/mutation_ledger/killed_by/inputs.py/quantise_setpoint_c.CLAMP_DROP.f00b74a6.json
deleted file mode 100644
index 259593aee0..0000000000
--- a/tests/mutation_ledger/killed_by/inputs.py/quantise_setpoint_c.CLAMP_DROP.f00b74a6.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/inputs.py:quantise_setpoint_c CLAMP_DROP f00b74a6",
-  "killed_by": "tests/features.py",
-  "old": "        out = min(out, _on_step(temperature_from_c(hi_c, unit), step, \"down\"))",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against d5cd003111277faa3f2abd7fbe6c9157d2e48ed7: CLAMP_DROP (`out = (out)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/quantise_setpoint_c.GUARD_OFF.28fe16ee.json b/tests/mutation_ledger/killed_by/inputs.py/quantise_setpoint_c.GUARD_OFF.28fe16ee.json
deleted file mode 100644
index ba480eab05..0000000000
--- a/tests/mutation_ledger/killed_by/inputs.py/quantise_setpoint_c.GUARD_OFF.28fe16ee.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/inputs.py:quantise_setpoint_c GUARD_OFF 28fe16ee",
-  "killed_by": "tests/features.py",
-  "old": "    if lo_c is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against d5cd003111277faa3f2abd7fbe6c9157d2e48ed7: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/quantise_setpoint_c.GUARD_OFF.998f9edd.json b/tests/mutation_ledger/killed_by/inputs.py/quantise_setpoint_c.GUARD_OFF.998f9edd.json
deleted file mode 100644
index 28c97d99d2..0000000000
--- a/tests/mutation_ledger/killed_by/inputs.py/quantise_setpoint_c.GUARD_OFF.998f9edd.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/inputs.py:quantise_setpoint_c GUARD_OFF 998f9edd",
-  "killed_by": "tests/features.py",
-  "old": "    if hi_c is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against d5cd003111277faa3f2abd7fbe6c9157d2e48ed7: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/quantise_setpoint_c.RETURN_DEL.6672b360.json b/tests/mutation_ledger/killed_by/inputs.py/quantise_setpoint_c.RETURN_DEL.6672b360.json
deleted file mode 100644
index 381ff1b63d..0000000000
--- a/tests/mutation_ledger/killed_by/inputs.py/quantise_setpoint_c.RETURN_DEL.6672b360.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/inputs.py:quantise_setpoint_c RETURN_DEL 6672b360",
-  "killed_by": "tests/guard_pins.py",
-  "old": "    return out if converted is None else converted",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against d5cd003111277faa3f2abd7fbe6c9157d2e48ed7: RETURN_DEL (`pass`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/quantise_setpoint_c.RETURN_DEL.7b938550.json b/tests/mutation_ledger/killed_by/inputs.py/quantise_setpoint_c.RETURN_DEL.7b938550.json
new file mode 100644
index 0000000000..861974c51b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/quantise_setpoint_c.RETURN_DEL.7b938550.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:quantise_setpoint_c RETURN_DEL 7b938550",
+  "killed_by": "tests/guard_pins.py",
+  "old": "    return _grid_of(hass, entity_id).on_step(value_c, rounding=rounding, lo_c=lo_c, hi_c=hi_c)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/read_temperature_delta_k.CMP_BOUND.6e16edbd.json b/tests/mutation_ledger/killed_by/inputs.py/read_temperature_delta_k.CMP_BOUND.6e16edbd.json
new file mode 100644
index 0000000000..6df8a522b3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/read_temperature_delta_k.CMP_BOUND.6e16edbd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:read_temperature_delta_k CMP_BOUND 6e16edbd",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return delta_k if 0.0 <= delta_k <= TEMPERATURE_DELTA_MAX_K else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return delta_k if 0.0 < delta_k <= TEMPERATURE_DELTA_MAX_K else None`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/read_temperature_delta_k.GUARD_OFF.68b50374.json b/tests/mutation_ledger/killed_by/inputs.py/read_temperature_delta_k.GUARD_OFF.68b50374.json
new file mode 100644
index 0000000000..40d932f7c5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/read_temperature_delta_k.GUARD_OFF.68b50374.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:read_temperature_delta_k GUARD_OFF 68b50374",
+  "killed_by": "tests/features.py",
+  "old": "    if value is None or scale is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/read_temperature_delta_k.RETURN_DEL.6e16edbd.json b/tests/mutation_ledger/killed_by/inputs.py/read_temperature_delta_k.RETURN_DEL.6e16edbd.json
new file mode 100644
index 0000000000..59a1198758
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/read_temperature_delta_k.RETURN_DEL.6e16edbd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:read_temperature_delta_k RETURN_DEL 6e16edbd",
+  "killed_by": "tests/structure.py",
+  "old": "    return delta_k if 0.0 <= delta_k <= TEMPERATURE_DELTA_MAX_K else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/setpoint_grid.GUARD_OFF.dd8ba768.json b/tests/mutation_ledger/killed_by/inputs.py/setpoint_grid.GUARD_OFF.dd8ba768.json
new file mode 100644
index 0000000000..a998533702
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/setpoint_grid.GUARD_OFF.dd8ba768.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:setpoint_grid GUARD_OFF dd8ba768",
+  "killed_by": "tests/block_duty.py",
+  "old": "    if not entity_id or hass.states.get(entity_id) is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=38."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/setpoint_grid.RETURN_DEL.32680ebe.json b/tests/mutation_ledger/killed_by/inputs.py/setpoint_grid.RETURN_DEL.32680ebe.json
new file mode 100644
index 0000000000..5dd94f83f9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/setpoint_grid.RETURN_DEL.32680ebe.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:setpoint_grid RETURN_DEL 32680ebe",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return _grid_of(hass, entity_id)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=29."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._co_optimize.CLAMP_DROP.f79618d7.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._co_optimize.CLAMP_DROP.f79618d7.json
deleted file mode 100644
index 653d27989e..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._co_optimize.CLAMP_DROP.f79618d7.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._co_optimize CLAMP_DROP f79618d7",
-  "killed_by": "tests/env_drift.py",
-  "old": "            headroom = np.maximum(0.0, p_max - dhw_power)",
-  "reason": "Recorded by `mutation_table.py --drain`: CLAMP_DROP (`headroom = (0.0)`) took tests/env_drift.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_space.CLAMP_DROP.4ad2d781.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_space.CLAMP_DROP.4ad2d781.json
deleted file mode 100644
index 8829d1f7f0..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_space.CLAMP_DROP.4ad2d781.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._solve_space CLAMP_DROP 4ad2d781",
-  "killed_by": "tests/plan_view.py",
-  "old": "        headroom = np.maximum(0.0, p_max - dhw_plan)",
-  "reason": "Recorded by `mutation_table.py --drain`: CLAMP_DROP (`headroom = (0.0)`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.11566350.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.11566350.json
new file mode 100644
index 0000000000..a5ed8ad60c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.11566350.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches CMP_BOUND 11566350",
+  "killed_by": "tests/features.py",
+  "old": "            if score < base - 1e-9:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if score <= base - 1e-9:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.1cd8047f.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.1cd8047f.json
new file mode 100644
index 0000000000..0f8c0eb779
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.1cd8047f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches CMP_BOUND 1cd8047f",
+  "killed_by": "tests/features.py",
+  "old": "            else np.nan_to_num(_padded(h.dhw_pins, ban.size)) >= 0.5",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`else np.nan_to_num(_padded(h.dhw_pins, ban.size)) > 0.5`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.7b6d787d.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.7b6d787d.json
new file mode 100644
index 0000000000..fa48feb1d0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.7b6d787d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches CMP_BOUND 7b6d787d",
+  "killed_by": "tests/features.py",
+  "old": "    if stops is None or not opt.config.cycling_cost > 0 or opt.model.params.dhw_store.combi:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if stops is None or not opt.config.cycling_cost >= 0 or opt.model.params.dhw_store.combi:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.95d10ca9.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.95d10ca9.json
new file mode 100644
index 0000000000..6cf8195176
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.95d10ca9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches CMP_BOUND 95d10ca9",
+  "killed_by": "tests/features.py",
+  "old": "    if kept_requirement is None or not duty_legs.switch_weight(shipped, tank, stops, p_max, floor) > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if kept_requirement is None or not duty_legs.switch_weight(shipped, tank, stops, p_max, floor) >= 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.CMP_BOUND.76b8fad3.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.fdd63b1a.json
similarity index 55%
rename from tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.CMP_BOUND.76b8fad3.json
rename to tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.fdd63b1a.json
index 7c9f2e5ea1..77e81068d3 100644
--- a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.CMP_BOUND.76b8fad3.json
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.fdd63b1a.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_thermostat_held_state CMP_BOUND 76b8fad3",
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches CMP_BOUND fdd63b1a",
   "killed_by": "tests/features.py",
-  "old": "        if need > 0.0 else held.buffer_tank_temperature",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if need >= 0.0 else held.buffer_tank_temperature`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+  "old": "            not np.any(plan.schedule[ban & ~forced_on] > 0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`not np.any(plan.schedule[ban & ~forced_on] >= 0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
 }
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.11566350.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.11566350.json
new file mode 100644
index 0000000000..195f6f6c2b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.11566350.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches GUARD_OFF 11566350",
+  "killed_by": "tests/features.py",
+  "old": "            if score < base - 1e-9:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.7b6d787d.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.7b6d787d.json
new file mode 100644
index 0000000000..ba5f280182
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.7b6d787d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches GUARD_OFF 7b6d787d",
+  "killed_by": "tests/plan_view.py",
+  "old": "    if stops is None or not opt.config.cycling_cost > 0 or opt.model.params.dhw_store.combi:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.95d10ca9.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.95d10ca9.json
new file mode 100644
index 0000000000..e5059f5c83
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.95d10ca9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches GUARD_OFF 95d10ca9",
+  "killed_by": "tests/structure.py",
+  "old": "    if kept_requirement is None or not duty_legs.switch_weight(shipped, tank, stops, p_max, floor) > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.RETURN_DEL.98a00538.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.RETURN_DEL.98a00538.json
new file mode 100644
index 0000000000..0fbe7e8d76
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.RETURN_DEL.98a00538.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches RETURN_DEL 98a00538",
+  "killed_by": "tests/features.py",
+  "old": "                return candidate_space, plan.schedule, candidate_status",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.RETURN_DEL.b66b6c96.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.RETURN_DEL.b66b6c96.json
new file mode 100644
index 0000000000..a4ef8f8ec0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.RETURN_DEL.b66b6c96.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches RETURN_DEL b66b6c96",
+  "killed_by": "tests/features.py",
+  "old": "    return incumbent",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.first_short.RETURN_DEL.d8594a7d.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.first_short.RETURN_DEL.d8594a7d.json
new file mode 100644
index 0000000000..3059c08a57
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.first_short.RETURN_DEL.d8594a7d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches.first_short RETURN_DEL d8594a7d",
+  "killed_by": "tests/features.py",
+  "old": "            return temps, step",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_held_unreachable.RETURN_DEL.ebd24b04.json b/tests/mutation_ledger/killed_by/optimizer.py/_held_unreachable.RETURN_DEL.ebd24b04.json
new file mode 100644
index 0000000000..2f21f5a74e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_held_unreachable.RETURN_DEL.ebd24b04.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_held_unreachable RETURN_DEL ebd24b04",
+  "killed_by": "tests/features.py",
+  "old": "    return bool(power_for_heat_per_cop_kw(p, made / cop) > p.max_electrical_power)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_held_zones.CLAMP_DROP.afb64a55.json b/tests/mutation_ledger/killed_by/optimizer.py/_held_zones.CLAMP_DROP.afb64a55.json
new file mode 100644
index 0000000000..ffc4d68e52
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_held_zones.CLAMP_DROP.afb64a55.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_held_zones CLAMP_DROP afb64a55",
+  "killed_by": "tests/features.py",
+  "old": "        slab_temperature=temp + max(0.0, q_floor) / model.params.slab_heat_transfer_floored,",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`slab_temperature=temp + (0.0) / model.params.slab_heat_transfer_floored,`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_priced_stops.CMP_BOUND.5a0db715.json b/tests/mutation_ledger/killed_by/optimizer.py/_priced_stops.CMP_BOUND.5a0db715.json
new file mode 100644
index 0000000000..3a61ffa90f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_priced_stops.CMP_BOUND.5a0db715.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_priced_stops CMP_BOUND 5a0db715",
+  "killed_by": "tests/features.py",
+  "old": "    return stops if max(stops) > 0 else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return stops if max(stops) >= 0 else None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_priced_stops.RETURN_DEL.5a0db715.json b/tests/mutation_ledger/killed_by/optimizer.py/_priced_stops.RETURN_DEL.5a0db715.json
new file mode 100644
index 0000000000..76b7d07cbf
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_priced_stops.RETURN_DEL.5a0db715.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_priced_stops RETURN_DEL 5a0db715",
+  "killed_by": "tests/features.py",
+  "old": "    return stops if max(stops) > 0 else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=24."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.GUARD_OFF.dfc20e22.json b/tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.GUARD_OFF.dfc20e22.json
new file mode 100644
index 0000000000..956c2f31c5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.GUARD_OFF.dfc20e22.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_shipped_and_received GUARD_OFF dfc20e22",
+  "killed_by": "tests/features.py",
+  "old": "    if avail is None or dhw is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.RETURN_DEL.d631f182.json b/tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.RETURN_DEL.d631f182.json
new file mode 100644
index 0000000000..f1bc862fd8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.RETURN_DEL.d631f182.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_shipped_and_received RETURN_DEL d631f182",
+  "killed_by": "tests/features.py",
+  "old": "    return space, dhw, duty_legs.delivered_space(space, dhw, avail, _duty_floor(opt))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.CLAMP_DROP.13234cde.json b/tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.CLAMP_DROP.13234cde.json
new file mode 100644
index 0000000000..1ad9e15a67
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.CLAMP_DROP.13234cde.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_stop_availability CLAMP_DROP 13234cde",
+  "killed_by": "tests/features.py",
+  "old": "        np.minimum(start, np.maximum(0.0, p_max - dhw_plan)),",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`(start),`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.GUARD_OFF.1bb04241.json b/tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.GUARD_OFF.1bb04241.json
new file mode 100644
index 0000000000..1c267e14ee
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.GUARD_OFF.1bb04241.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_stop_availability GUARD_OFF 1bb04241",
+  "killed_by": "tests/plan_view.py",
+  "old": "    if stops is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.RETURN_DEL.9325b601.json b/tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.RETURN_DEL.9325b601.json
new file mode 100644
index 0000000000..b8c8493e56
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.RETURN_DEL.9325b601.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_stop_availability RETURN_DEL 9325b601",
+  "killed_by": "tests/structure.py",
+  "old": "    return duty_legs.availability(space, tank, lost, _duty_floor(opt))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.RETURN_DEL.0bf003bf.json b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.RETURN_DEL.0bf003bf.json
new file mode 100644
index 0000000000..fd1ab2e18d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.RETURN_DEL.0bf003bf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_switch_cost_fn RETURN_DEL 0bf003bf",
+  "killed_by": "tests/plan_view.py",
+  "old": "    return switch_cost",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.CMP_BOUND.b0a491aa.json b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.CMP_BOUND.b0a491aa.json
new file mode 100644
index 0000000000..318c16b96c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.CMP_BOUND.b0a491aa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_switch_cost_fn.switch_cost CMP_BOUND b0a491aa",
+  "killed_by": "tests/features.py",
+  "old": "        if stops is None or dhw is None or not cost > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if stops is None or dhw is None or not cost >= 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.GUARD_OFF.b0a491aa.json b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.GUARD_OFF.b0a491aa.json
new file mode 100644
index 0000000000..899cb46f4a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.GUARD_OFF.b0a491aa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_switch_cost_fn.switch_cost GUARD_OFF b0a491aa",
+  "killed_by": "tests/plan_view.py",
+  "old": "        if stops is None or dhw is None or not cost > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.RETURN_DEL.0f24df73.json b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.RETURN_DEL.0f24df73.json
new file mode 100644
index 0000000000..0ec1daa260
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.RETURN_DEL.0f24df73.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_switch_cost_fn.switch_cost RETURN_DEL 0f24df73",
+  "killed_by": "tests/features.py",
+  "old": "        return term if np.ndim(space) == 2 else float(term[0])",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.CLAMP_DROP.5c7d4c36.json b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.CLAMP_DROP.5c7d4c36.json
deleted file mode 100644
index d98970a2c9..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.CLAMP_DROP.5c7d4c36.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_thermostat_held_state CLAMP_DROP 5c7d4c36",
-  "killed_by": "tests/stress.py",
-  "old": "        slab_temperature=target + max(0.0, q_floor) / model.params.slab_heat_transfer_floored,",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 413944b6772fa7f2f38cef7ea2f667a64d79251a: CLAMP_DROP (`slab_temperature=target + (0.0) / model.params.slab_heat_transfer_floored,`) took tests/stress.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.CLAMP_DROP.c7dd28c1.json b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.CLAMP_DROP.c7dd28c1.json
new file mode 100644
index 0000000000..6074494c36
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.CLAMP_DROP.c7dd28c1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_thermostat_held_state CLAMP_DROP c7dd28c1",
+  "killed_by": "tests/features.py",
+  "old": "        lo, hi = min(outdoor, target), target",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`lo, hi = (outdoor), target`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.GUARD_OFF.1ecfa785.json b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.GUARD_OFF.1ecfa785.json
new file mode 100644
index 0000000000..2d50218447
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.GUARD_OFF.1ecfa785.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_thermostat_held_state GUARD_OFF 1ecfa785",
+  "killed_by": "tests/features.py",
+  "old": "    if unreachable(held):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.GUARD_OFF.5c05badb.json b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.GUARD_OFF.5c05badb.json
deleted file mode 100644
index 6b9fa738c0..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.GUARD_OFF.5c05badb.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_thermostat_held_state GUARD_OFF 5c05badb",
-  "killed_by": "tests/env_drift.py",
-  "old": "    if not mixing_valve.is_throttling(p.mixing_valve_mode):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/env_drift.py from rc=0 failed=0 to rc=1 failed=5."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.BOOLOP.1b4f8e62.json b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.BOOLOP.1b4f8e62.json
new file mode 100644
index 0000000000..80cbda2495
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.BOOLOP.1b4f8e62.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_thermostat_held_state.held_at BOOLOP 1b4f8e62",
+  "killed_by": "tests/features.py",
+  "old": "        if valved and (h_need := need(h)) > 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if valved or (h_need := need(h)) > 0.0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.CMP_BOUND.1b4f8e62.json b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.CMP_BOUND.1b4f8e62.json
new file mode 100644
index 0000000000..62565cb378
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.CMP_BOUND.1b4f8e62.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_thermostat_held_state.held_at CMP_BOUND 1b4f8e62",
+  "killed_by": "tests/features.py",
+  "old": "        if valved and (h_need := need(h)) > 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if valved and (h_need := need(h)) >= 0.0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.GUARD_OFF.1b4f8e62.json b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.GUARD_OFF.1b4f8e62.json
new file mode 100644
index 0000000000..7485dcd3ea
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.GUARD_OFF.1b4f8e62.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_thermostat_held_state.held_at GUARD_OFF 1b4f8e62",
+  "killed_by": "tests/features.py",
+  "old": "        if valved and (h_need := need(h)) > 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.RETURN_DEL.b87482f7.json b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.RETURN_DEL.b87482f7.json
new file mode 100644
index 0000000000..efc2598a06
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.RETURN_DEL.b87482f7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_thermostat_held_state.held_at RETURN_DEL b87482f7",
+  "killed_by": "tests/plan_view.py",
+  "old": "        return h",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_with_stop_availability.GUARD_OFF.ee2cd78c.json b/tests/mutation_ledger/killed_by/optimizer.py/_with_stop_availability.GUARD_OFF.ee2cd78c.json
new file mode 100644
index 0000000000..9e0692cadf
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_with_stop_availability.GUARD_OFF.ee2cd78c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_with_stop_availability GUARD_OFF ee2cd78c",
+  "killed_by": "tests/features.py",
+  "old": "    if avail is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_with_stop_availability.RETURN_DEL.f73e18ce.json b/tests/mutation_ledger/killed_by/optimizer.py/_with_stop_availability.RETURN_DEL.f73e18ce.json
new file mode 100644
index 0000000000..7d6d925b39
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_with_stop_availability.RETURN_DEL.f73e18ce.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_with_stop_availability RETURN_DEL f73e18ce",
+  "killed_by": "tests/features.py",
+  "old": "    return headroom, partial(objective, avail=avail), partial(objective_batch, avail=avail)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_with_switch_cost.RETURN_DEL.65006bb8.json b/tests/mutation_ledger/killed_by/optimizer.py/_with_switch_cost.RETURN_DEL.65006bb8.json
new file mode 100644
index 0000000000..bbb19961f6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_with_switch_cost.RETURN_DEL.65006bb8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_with_switch_cost RETURN_DEL 65006bb8",
+  "killed_by": "tests/plan_view.py",
+  "old": "    return level_cost if switch_cost is None else level_cost + switch_cost",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/@module.CONST.eef42148.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/@module.CONST.eef42148.json
deleted file mode 100644
index 8634d02df4..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/@module.CONST.eef42148.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:<module> CONST eef42148",
-  "killed_by": "tests/features.py",
-  "old": "SPLIT_MIN_MINUTES = 5.0",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against cfa2cb07b1474ed3b405787d3b41978e9be61d2f: CONST (`SPLIT_MIN_MINUTES = 10.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_bounded.BOOLOP.ebd65023.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_bounded.BOOLOP.ebd65023.json
deleted file mode 100644
index 6b77c340aa..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_bounded.BOOLOP.ebd65023.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_bounded BOOLOP ebd65023",
-  "killed_by": "tests/guard_pins.py",
-  "old": "    if hi is not None and (low is None or hi >= quantise_setpoint_c(inp.hass, entity, low, rounding=\"up\")):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if hi is not None or (low is None or hi >= quantise_setpoint_c(inp.hass, entity, low, rounding=\"up\")):`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_bounded.CLAMP_DROP.2609ebb9.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_bounded.CLAMP_DROP.2609ebb9.json
deleted file mode 100644
index a5f1d4b3a1..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_bounded.CLAMP_DROP.2609ebb9.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_bounded CLAMP_DROP 2609ebb9",
-  "killed_by": "tests/features.py",
-  "old": "    value = min(value, high) if high is not None else value",
-  "reason": "pump-duty arbiter revision; `value = min(value, high) if high is not None else value` -> `value = (value) if high is not None else value` fails 1 of the arbiter checks in tests/features.py's pump-duty arbiter section, against a green baseline. Measured by driving that section, 2026-09-24."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_bounded.CMP_BOUND.ebd65023.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_bounded.CMP_BOUND.ebd65023.json
deleted file mode 100644
index 3b75747e63..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_bounded.CMP_BOUND.ebd65023.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_bounded CMP_BOUND ebd65023",
-  "killed_by": "tests/block_duty.py",
-  "old": "    if hi is not None and (low is None or hi >= quantise_setpoint_c(inp.hass, entity, low, rounding=\"up\")):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if hi is not None and (low is None or hi > quantise_setpoint_c(inp.hass, entity, low, rounding=\"up\")):`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_bounded.GUARD_OFF.ebd65023.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_bounded.GUARD_OFF.835d5167.json
similarity index 57%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_bounded.GUARD_OFF.ebd65023.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_bounded.GUARD_OFF.835d5167.json
index 41b1534c76..f1a0d063aa 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_bounded.GUARD_OFF.ebd65023.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_bounded.GUARD_OFF.835d5167.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_bounded GUARD_OFF ebd65023",
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_bounded GUARD_OFF 835d5167",
   "killed_by": "tests/block_duty.py",
-  "old": "    if hi is not None and (low is None or hi >= quantise_setpoint_c(inp.hass, entity, low, rounding=\"up\")):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=6."
+  "old": "    if value is None or grid is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=23."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_bounded.GUARD_OFF.c781efce.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_bounded.GUARD_OFF.c781efce.json
deleted file mode 100644
index 2bfeddfefe..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_bounded.GUARD_OFF.c781efce.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_bounded GUARD_OFF c781efce",
-  "killed_by": "tests/features.py",
-  "old": "    if value is None or _slot_state(inp, slot) is None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 694120d5aa296b65c7d7be097f8684e7bc3b5f61: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_dhw_write.RETURN_DEL.d4401a97.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_bounded.RETURN_DEL.f7af5135.json
similarity index 60%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_dhw_write.RETURN_DEL.d4401a97.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_bounded.RETURN_DEL.f7af5135.json
index a13a4d7b8f..42fa09ee3e 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_dhw_write.RETURN_DEL.d4401a97.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_bounded.RETURN_DEL.f7af5135.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_dhw_write RETURN_DEL d4401a97",
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_bounded RETURN_DEL f7af5135",
   "killed_by": "tests/block_duty.py",
-  "old": "    return _bounded(inp, \"dhw_setpoint\", float(cycle), hi=inp.params.dhw_hard_max_temp)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=13."
+  "old": "    return grid.bounded(value, floor, rounding=rounding, lo=lo, hi=hi)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=5."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_dhw_start_below_c.RETURN_DEL.8751d1cd.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_dhw_start_below_c.RETURN_DEL.8751d1cd.json
new file mode 100644
index 0000000000..ca3084b6a5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_dhw_start_below_c.RETURN_DEL.8751d1cd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_dhw_start_below_c RETURN_DEL 8751d1cd",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return None if hysteresis is None else dhw_start_below_c(_dhw_target(inp), hysteresis)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_dhw_target.RETURN_DEL.85cd72f1.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_dhw_target.RETURN_DEL.85cd72f1.json
new file mode 100644
index 0000000000..c2b682a8dd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_dhw_target.RETURN_DEL.85cd72f1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_dhw_target RETURN_DEL 85cd72f1",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return dhw_step_target_c(inp.params, cycle, _grid(inp, \"dhw_setpoint\"))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=27."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_dhw_write.GUARD_OFF.90de19e4.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_dhw_write.GUARD_OFF.90de19e4.json
deleted file mode 100644
index 847ff69bac..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_dhw_write.GUARD_OFF.90de19e4.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_dhw_write GUARD_OFF 90de19e4",
-  "killed_by": "tests/guard_pins.py",
-  "old": "    if cycle is None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_dhw_write.RETURN_DEL.f98d0fea.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_dhw_write.RETURN_DEL.f98d0fea.json
new file mode 100644
index 0000000000..808ed46115
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_dhw_write.RETURN_DEL.f98d0fea.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_dhw_write RETURN_DEL f98d0fea",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return None if _grid(inp, \"dhw_setpoint\") is None else _dhw_target(inp)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=23."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_grid.RETURN_DEL.e5fcebab.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_grid.RETURN_DEL.e5fcebab.json
new file mode 100644
index 0000000000..fdb3c2d8fb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_grid.RETURN_DEL.e5fcebab.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_grid RETURN_DEL e5fcebab",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return setpoint_grid(inp.hass, _entities(inp.config)[slot])",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=26."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_missed.GUARD_OFF.f28578a3.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_missed.GUARD_OFF.f28578a3.json
new file mode 100644
index 0000000000..06a73a0923
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_missed.GUARD_OFF.f28578a3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_missed GUARD_OFF f28578a3",
+  "killed_by": "tests/block_duty.py",
+  "old": "    if planned == \"dhw\" and actual == \"idle\" and _not_startable(row):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_missed.RETURN_DEL.0733b5f7.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_missed.RETURN_DEL.0733b5f7.json
new file mode 100644
index 0000000000..def8c438c7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_missed.RETURN_DEL.0733b5f7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_missed RETURN_DEL 0733b5f7",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return f\"{actual}-instead\"",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_not_startable.CMP_BOUND.452b7046.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_not_startable.CMP_BOUND.452b7046.json
new file mode 100644
index 0000000000..7d77e34542
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_not_startable.CMP_BOUND.452b7046.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_not_startable CMP_BOUND 452b7046",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return start is not None and tank is not None and float(tank) >= start",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return start is not None and tank is not None and float(tank) > start`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_not_startable.RETURN_DEL.452b7046.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_not_startable.RETURN_DEL.452b7046.json
new file mode 100644
index 0000000000..2694a83b80
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_not_startable.RETURN_DEL.452b7046.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_not_startable RETURN_DEL 452b7046",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return start is not None and tank is not None and float(tank) >= start",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.CMP_BOUND.3eede229.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.CMP_BOUND.3eede229.json
new file mode 100644
index 0000000000..ac6a436217
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.CMP_BOUND.3eede229.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_share CMP_BOUND 3eede229",
+  "killed_by": "tests/features.py",
+  "old": "    return legs[0][0] if (now - result.timestamps[i]) < first_ends else legs[-1][0]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return legs[0][0] if (now - result.timestamps[i]) <= first_ends else legs[-1][0]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.CMP_BOUND.4f254e46.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.CMP_BOUND.4f254e46.json
deleted file mode 100644
index a6d4dc03ea..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.CMP_BOUND.4f254e46.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_share CMP_BOUND 4f254e46",
-  "killed_by": "tests/features.py",
-  "old": "    if PLAN_STEP_MINUTES - dhw_min < SPLIT_MIN_MINUTES:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if PLAN_STEP_MINUTES - dhw_min <= SPLIT_MIN_MINUTES:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.GUARD_OFF.8cc0b854.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.GUARD_OFF.8cc0b854.json
deleted file mode 100644
index f4206bfefb..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.GUARD_OFF.8cc0b854.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_share GUARD_OFF 8cc0b854",
-  "killed_by": "tests/features.py",
-  "old": "    if dhw_min < SPLIT_MIN_MINUTES:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against cfa2cb07b1474ed3b405787d3b41978e9be61d2f: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.RETURN_DEL.0008eae9.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.RETURN_DEL.0008eae9.json
deleted file mode 100644
index ccfca9bee7..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.RETURN_DEL.0008eae9.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_share RETURN_DEL 0008eae9",
-  "killed_by": "tests/features.py",
-  "old": "    return \"dhw\" if (now - result.timestamps[i]) < timedelta(minutes=dhw_min) else \"space\"",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against cfa2cb07b1474ed3b405787d3b41978e9be61d2f: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.RETURN_DEL.3eede229.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.RETURN_DEL.3eede229.json
new file mode 100644
index 0000000000..1af67f301a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.RETURN_DEL.3eede229.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_share RETURN_DEL 3eede229",
+  "killed_by": "tests/features.py",
+  "old": "    return legs[0][0] if (now - result.timestamps[i]) < first_ends else legs[-1][0]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/setpoint_check.py/_dhw_start.CMP_BOUND.06352141.json b/tests/mutation_ledger/killed_by/setpoint_check.py/_dhw_start.CMP_BOUND.06352141.json
new file mode 100644
index 0000000000..d5d21332a5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/setpoint_check.py/_dhw_start.CMP_BOUND.06352141.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/setpoint_check.py:_dhw_start CMP_BOUND 06352141",
+  "killed_by": "tests/block_duty.py",
+  "old": "        bool(params.dhw_enabled) and start is not None and floor > start,",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`bool(params.dhw_enabled) and start is not None and floor >= start,`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_start_below_c.CMP_BOUND.f85d8f1a.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_start_below_c.CMP_BOUND.f85d8f1a.json
new file mode 100644
index 0000000000..1be2cb8c64
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_start_below_c.CMP_BOUND.f85d8f1a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_start_below_c CMP_BOUND f85d8f1a",
+  "killed_by": "tests/block_duty.py",
+  "old": "    if target is None or hysteresis is None or hysteresis <= 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if target is None or hysteresis is None or hysteresis < 0.0:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_start_below_c.GUARD_OFF.f85d8f1a.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_start_below_c.GUARD_OFF.f85d8f1a.json
new file mode 100644
index 0000000000..067e7b2ba7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_start_below_c.GUARD_OFF.f85d8f1a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_start_below_c GUARD_OFF f85d8f1a",
+  "killed_by": "tests/features.py",
+  "old": "    if target is None or hysteresis is None or hysteresis <= 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_start_below_c.RETURN_DEL.50d494cc.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_start_below_c.RETURN_DEL.50d494cc.json
new file mode 100644
index 0000000000..14671b9162
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_start_below_c.RETURN_DEL.50d494cc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_start_below_c RETURN_DEL 50d494cc",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return target - hysteresis",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_step_target_c.CLAMP_DROP.b7aa4192.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_step_target_c.CLAMP_DROP.b7aa4192.json
new file mode 100644
index 0000000000..0f11499b74
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_step_target_c.CLAMP_DROP.b7aa4192.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_step_target_c CLAMP_DROP b7aa4192",
+  "killed_by": "tests/block_duty.py",
+  "old": "        return min(float(value), float(limit))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return (float(value))`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_step_target_c.GUARD_OFF.17d5218f.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_step_target_c.GUARD_OFF.17d5218f.json
new file mode 100644
index 0000000000..07af2df978
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_step_target_c.GUARD_OFF.17d5218f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_step_target_c GUARD_OFF 17d5218f",
+  "killed_by": "tests/block_duty.py",
+  "old": "    if grid is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=17."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/dhw_step_target_c.RETURN_DEL.0ac6eb76.json b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_step_target_c.RETURN_DEL.0ac6eb76.json
new file mode 100644
index 0000000000..3127cbd96f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/dhw_step_target_c.RETURN_DEL.0ac6eb76.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:dhw_step_target_c RETURN_DEL 0ac6eb76",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return cast(float, grid.bounded(float(value), hi=limit))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=27."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/start_flow_min_lift_k.CLAMP_DROP.1241fe6f.json b/tests/mutation_ledger/killed_by/thermal_model.py/start_flow_min_lift_k.CLAMP_DROP.1241fe6f.json
new file mode 100644
index 0000000000..1a18e068dd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/start_flow_min_lift_k.CLAMP_DROP.1241fe6f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:start_flow_min_lift_k CLAMP_DROP 1241fe6f",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return lift if hysteresis is None else max(lift, hysteresis)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return lift if hysteresis is None else (lift)`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/start_flow_min_lift_k.RETURN_DEL.1241fe6f.json b/tests/mutation_ledger/killed_by/thermal_model.py/start_flow_min_lift_k.RETURN_DEL.1241fe6f.json
new file mode 100644
index 0000000000..8f82eb0d8a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/start_flow_min_lift_k.RETURN_DEL.1241fe6f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:start_flow_min_lift_k RETURN_DEL 1241fe6f",
+  "killed_by": "tests/features.py",
+  "old": "    return lift if hysteresis is None else max(lift, hysteresis)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/valve_top_draw.RETURN_DEL.21d92eb4.json b/tests/mutation_ledger/killed_by/thermal_model.py/valve_top_draw.RETURN_DEL.21d92eb4.json
new file mode 100644
index 0000000000..ea6965068f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/valve_top_draw.RETURN_DEL.21d92eb4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:valve_top_draw RETURN_DEL 21d92eb4",
+  "killed_by": "tests/features.py",
+  "old": "    return _circuit_draw(circuits, model.params.buffer_max_temp)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/survivor_triage/duty_switch.py/Direction.book.CMP_BOUND.3e106b06.json b/tests/mutation_ledger/survivor_triage/duty_switch.py/Direction.book.CMP_BOUND.3e106b06.json
new file mode 100644
index 0000000000..2f2183aa51
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/duty_switch.py/Direction.book.CMP_BOUND.3e106b06.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:Direction.book CMP_BOUND 3e106b06",
+  "old": "        if self.n > N_CAP:",
+  "reason": "Equivalent (CMP_BOUND, `self.n > N_CAP` -> `self.n >= N_CAP`). The two differ only at n == N_CAP exactly, where the guarded body computes scale = N_CAP / self.n = 1.0 and multiplies k and kept_w by it: IEEE multiplication by 1.0 returns its operand, so both counts, and the latch read after them, are the same floats on either branch. Measured by the R10-DUTY-SWITCH-PLANNER-PRICE fixer's diff drive (tools/audit/seat/mutant_run.py --diff over the section harness dev/audit/harnesses/r10_duty_switch_price_section.py): SURVIVED, while the same line's GUARD_OFF and the section's cap mutants (no cap, the cap scaling the stops alone, three times the on-threshold) are each killed by the cap checks.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/@module.CONST.4bcd4baf.json b/tests/mutation_ledger/survivor_triage/optimizer.py/@module.CONST.4bcd4baf.json
new file mode 100644
index 0000000000..19f0e79441
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/@module.CONST.4bcd4baf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:<module> CONST 4bcd4baf",
+  "old": "_HELD_BISECTIONS = 40",
+  "reason": "Equivalent to every reader's resolution, and measured (CONST, 40 -> 80). `_HELD_BISECTIONS` is the bisection count `_thermostat_held_state` uses to find the highest zone temperature the reference step can hold under both of `_held_unreachable`'s bounds. At 40 the bracket is 2**-40 of the outdoor-to-target span, under 4e-11 K for a 46 K span; 80 only narrows it further. Measured against the group's block (`features_block.py` from `# --- R10-SAV-VALUATION-RESIDUE: stored heat` to `# --- R10-WATER-SETPOINT-FEEDBACK`): `ALL 10 FEATURES BLOCK PASSED` under the mutant. No reader of the held state (the booked reference and the start's stored-heat settlement) resolves a change that size.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/_held_unreachable.CMP_BOUND.ebd24b04.json b/tests/mutation_ledger/survivor_triage/optimizer.py/_held_unreachable.CMP_BOUND.ebd24b04.json
new file mode 100644
index 0000000000..f5f9d850b5
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/_held_unreachable.CMP_BOUND.ebd24b04.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_held_unreachable CMP_BOUND ebd24b04",
+  "old": "    return bool(power_for_heat_per_cop_kw(p, made / cop) > p.max_electrical_power)",
+  "reason": "Equivalent on every reachable input, and measured (CMP_BOUND, `>` -> `>=`). The two arms differ only where the steady heat's draw equals `max_electrical_power` to the last bit, which is the pump-bound equilibrium itself. At the target the mutant then bisects and lands within 2**-40 of the span below it; inside the bisection either branch keeps a bracket holding that equilibrium. Both move the held zones by under the final bracket, 4e-11 K. The group's block (the 4 kW and 9 kW pumps at -25 C, valved and not, both zonings) reads `ALL 10 FEATURES BLOCK PASSED` under the mutant.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/pump_arbiter.py/_share.CMP_BOUND.8cc0b854.json b/tests/mutation_ledger/survivor_triage/pump_arbiter.py/_share.CMP_BOUND.8cc0b854.json
deleted file mode 100644
index 994b799f7b..0000000000
--- a/tests/mutation_ledger/survivor_triage/pump_arbiter.py/_share.CMP_BOUND.8cc0b854.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_share CMP_BOUND 8cc0b854",
-  "old": "    if dhw_min < SPLIT_MIN_MINUTES:",
-  "reason": "R10 mutation-anchor: the `killed_by: tests/entities.py` pin was vacuous. Re-driven at 0be5e2de5 by dev/audit/harnesses/r10_anchor_vacuous.py with the 2 ledger row(s) the mutant itself makes stale hidden from its tree, 0 of 1 site(s) were killed by tests/entities.py: the recorded kill was a check refusing a ledger row the mutant made stale (the --anchor self-test, or the survivor_triage staleness check), not one that saw the mutation. Was: Recorded by `mutation_table.py --drain` against 816547efe270a08e18e3b92f52185fe8c1fee2ef: CMP_BOUND (`if dhw_min <= SPLIT_MIN_MINUTES:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1. Not re-driven here against the other drivers in its closure, so a gap until one is shown to kill it.",
-  "verdict": "gap"
-}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 34471a37be..f0b2e8461e 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17522,
+ "class_excess_loc": 17503,
  "const_modules_over_50": 3,
  "coordinator_attrs": 139,
  "coordinator_multiassigned_attrs": 108,
@@ -16,6 +16,6 @@
  "methods_over_150": 15,
  "methods_over_200": 8,
  "name_kept_members": 38,
- "recorded_at": "8c10361eb1fea539dc5acb8f7442eac2810faa47",
+ "recorded_at": "f44e761c19dc07fff222bbd6a323bdc847ea9f04",
  "seam_cut_total": 421
 }
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index 72b0b6dca2..c89b3c07f0 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -126,7 +126,7 @@ standing-seat liveness step keep the seats alive.
 - [`sweep_gantt.py`](instruments/sweep_gantt.py.md) — compares the live state to the plan's Gantt and prints each unacknowledged `GANTT-SLIP`
 - [`verdict_audit.py`](instruments/verdict_audit.py.md) — maps every open PR to its latest verdict and holder; prints `UNHELD` lines
 - [`survivor_list.py`](instruments/survivor_list.py.md) — refuses a `mutation-vacuous` verdict that omits a survivor its evidence's driver output reports; `bus.sh push-verdict` runs it
-- [`bare_array.py`](instruments/bare_array.py.md) — refuses a bare `"${name[@]}"` in any tracked `tools/**/*.sh` script (a sourced library runs under its caller's `set -u`), which macOS bash 3.2 dies on when the array is empty (`--check`, `--self-test`)
+- [`bare_array.py`](instruments/bare_array.py.md) — refuses two macOS bash 3.2 failures in tracked `tools/**/*.sh`: a bare `"${name[@]}"` (empty under a caller's `set -u`) and a `case` pattern lacking its `(` in `$( )` (`--check`, `--self-test`)
 - [`tmp_paths.py`](instruments/tmp_paths.py.md) — refuses a tracked script, workflow or decision record that depends on a temp or machine path (`--check`, `--self-test`)
 - [`update_pr.sh`](instruments/update_pr.sh.md) — brings an open PR branch to its head + a code SHA (merge) + origin/main (merge), adds the PR's own delivery row when the head lacks it (`delivery_row.sh`), prefixes ## Head with what happened, pushes as `hpo-author`
 - [`wt_sync.sh`](instruments/wt_sync.sh.md) — snapshots every worktree whose state is not already on origin (unpushed commits, uncommitted or untracked files) to `origin/wip-sync/<slug>`
diff --git a/tools/audit/seat/bare_array.py b/tools/audit/seat/bare_array.py
index 1d3386a916..676db44d89 100644
--- a/tools/audit/seat/bare_array.py
+++ b/tools/audit/seat/bare_array.py
@@ -1,5 +1,5 @@
 #!/usr/bin/env python3
-"""Refuse a bare `"${name[@]}"` in a tracked tools/ shell script.
+"""Refuse two bash-3.2-only failures in a tracked tools/ shell script.
 
     python3 -I tools/audit/seat/bare_array.py --check [--ref <commit>]
     python3 -I tools/audit/seat/bare_array.py --self-test
@@ -24,6 +24,19 @@ the mutant line by that marker at the line's end (`pr_args.sh`'s header), so a
 reason appended after the marker unanchors the mutant, and any line carrying
 one is refused. `"${name[*]}"`, `${#name[@]}` and `"${name[@]:...}"` are not
 matched.
+
+THE SECOND RULE: a `case` pattern without its leading `(` inside a `$( ... )`
+command substitution, or a `<( ... )`/`>( ... )` process substitution, quoted
+or not. Bash 3.2 finds the end of a substitution by counting parentheses, so
+the pattern's `)` closes it early: unquoted, `bash -n` fails (`tick_loop.sh`,
+PR 3520, the tick loop's own freshness check refusing on every pass); inside
+double quotes `bash -n` passes and the substitution dies at run time. Bash 4+
+parses both. The way out is the pattern's own `(`: `(func) ...;;`. A case in a
+plain `( ... )` subshell, in backquotes, or at top level is not refused, since
+3.2 parses those; there is no opt-out marker, because a refused site never
+parses on 3.2. Comments, quotes and here-document bodies are skipped (an
+unbalanced `)` in a here-document inside a substitution is a 3.2 hazard of its
+own, which this rule does not judge).
 """
 from __future__ import annotations
 
@@ -61,6 +74,88 @@ def sites(text: str) -> list[tuple[int, str]]:
     return [(n, lines[n - 1].strip()) for n in sorted(out)]
 
 
+WORD = re.compile(r"\w+")  # a word; only case, in and esac are read
+HEREDOC = re.compile(r"""<<(-?)[ \t]*(['"]?)\\?([A-Za-z_][A-Za-z0-9_]*)\2""")
+COMMAND = re.compile(r"(?:\A|[\n;&|(){!`]|(?:\A|\W)(?:then|do|else|time))[ \t]*\Z")  # `case` is a keyword here
+BEFORE, AFTER = " \t\n;&|(){`", " \t\n;&|()`"
+EOL = re.compile(r".*")  # to the end of the line, the newline left
+SQUOTE = re.compile(r"'[^']*'?")
+PATTERN = re.compile(r"""(?:\\.|'[^']*'?|"(?:\\.|[^"\\])*"?|[^)'"\\])*\)?""", re.S)  # through its `)`
+
+
+def case_sites(text: str) -> list[tuple[int, str]]:
+    """(line number, line) of each case pattern lacking `(` inside a substitution."""
+    stack: list = []  # "sub", "paren", "dq", "bt", "param", or a case: [case, head|pat|body]
+    hits, docs, i, n = set(), [], 0, len(text)
+    lines = text.splitlines()
+    while i < n:
+        c, t = text[i], stack[-1] if stack else None
+        if isinstance(t, list) and t[1] == "pat":
+            m = WORD.match(text, i)
+            if c in " \t\n":
+                i += 1
+            elif c == "#":
+                i = EOL.match(text, i).end()
+            elif m and m.group() == "esac" and text[m.end():m.end() + 1] in AFTER:
+                stack.pop()  # the keyword is then read again, in the enclosing context
+            else:
+                outer = [e for e in stack if e in ("sub", "bt")]
+                if c != "(" and outer[-1:] == ["sub"]:
+                    hits.add(text.count("\n", 0, i) + 1)
+                t[1], i = "body", PATTERN.match(text, i + (c == "(")).end()
+            continue
+        if t == "dq" and c not in "\\$`":
+            stack.pop() if c == '"' else None
+            i += 1
+            continue
+        word = text[i - 1:i] in BEFORE  # at i == 0 the slice is "", which is in any string
+        m = WORD.match(text, i) if word else None
+        kw = m.group() if m and text[m.end():m.end() + 1] in AFTER else None
+        if c == "\\":
+            i += 1
+        elif c == "}" and t == "param":
+            stack.pop()
+        elif c == "#" and word and t != "param":
+            i = EOL.match(text, i).end() - 1
+        elif c == "'" and t != "dq":
+            i = SQUOTE.match(text, i).end() - 1
+        elif c == '"':
+            stack.append("dq")
+        elif c == "`":
+            stack.pop() if t == "bt" else stack.append("bt")
+        elif text.startswith(("$(", "<(", ">("), i):
+            stack.append("sub")  # `$((` too: its `((` and `))` then pair as a paren
+            i += 1
+        elif text.startswith("${", i):
+            stack.append("param")
+        elif c == "(":
+            stack.append("paren")
+        elif c == ")" and t in ("sub", "paren"):
+            stack.pop()
+        elif HEREDOC.match(text, i) and not text.startswith("<<<", i):
+            h = HEREDOC.match(text, i)
+            docs.append(re.compile("^" + "\t*" * len(h.group(1)) + h.group(3) + "$", re.M))
+        elif c == "\n" and docs:
+            for d in docs:  # each body in turn, to its delimiter line or the end
+                e = d.search(text, i + 1)
+                i = e.end() if e else n
+            docs = []
+            continue
+        elif isinstance(t, list) and t[1] == "body" and text.startswith((";;", ";&"), i):
+            t[1] = "pat"
+            i += 2 if text.startswith(";;&", i) else 1
+        elif m:
+            if kw == "case" and COMMAND.search(text, max(0, i - 9), i):
+                stack.append(["case", "head"])
+            elif kw == "in" and t == ["case", "head"]:
+                t[1] = "pat"
+            elif kw == "esac" and t == ["case", "body"]:
+                stack.pop()
+            i = m.end() - 1
+        i += 1
+    return [(k, lines[k - 1].strip()) for k in sorted(hits)]
+
+
 def scan(ref: str | None = None) -> list[str]:
     """`path:line: text` per refused site across tracked tools/**/*.sh."""
     root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
@@ -76,7 +171,7 @@ def scan(ref: str | None = None) -> list[str]:
             text = subprocess.check_output(["git", "show", f"{ref}:{p}"], text=True, cwd=root)
         else:
             text = (Path(root) / p).read_text()
-        out += [f"{p}:{n}: {t}" for n, t in sites(text)]
+        out += [f"{p}:{n}: {t}" for n, t in sorted(set(sites(text) + case_sites(text)))]
     return out
 
 
@@ -121,6 +216,85 @@ def self_test() -> int:
        "a reason after a mut marker is refused in a judged file on a guarded line")
     st(sites(head + 'f x  # never-empty: argv  # mut:x\n'), [],
        "a judged file's non-bare line with the reason before the marker passes (null)")
+    # The second rule: the line numbers each text refuses. Run against bash 3.2.57, every refused
+    # shape fails, at `bash -n` or (quoted, or in backquotes) at run time.
+    def cs(text, want, name):
+        st([k for k, _ in case_sites(text)], want, name)
+
+    tick = ('out=$(export A=1\n  case $1 in\n    func) . "$t/e"; export -f exec; "$B" --n ;;\n'
+            '    bashenv) BASH_ENV=$t/e "$B" --n ;;\n    none) "$B" --n ;;\n  esac 2>&1); src=$?\n')
+    cs(tick, [3, 4, 5], "planted: tick_loop.sh's shape at PR 3520, three bare patterns in $( )")
+    cs(tick.replace("func)", "(func)").replace("bashenv)", "(bashenv)").replace("none)", "(none)"), [],
+       "the same with each pattern's own ( passes (null)")
+    cs("case a in a) x=$(echo 1);; esac\n", [], "a case at top level passes, its body's $( ) too")
+    cs("( case a in a) :;; esac )\nx=`case a in a) :;; esac`\n", [], "a subshell or backquotes pass")
+    cs("x=$(y=`case a in a) :;; esac`)\n", [], "backquotes inside $( ) reset it")
+    cs("x=$(y=`echo $(case a in a) :;; esac)`)\n", [1], "a $( ) inside those backquotes counts")
+    cs("cat <(case a in a) :;; esac)\ncat >(case a in\n b) :;; esac)\n", [1, 3],
+       "a process substitution counts, either direction")
+    cs('x="$(case a in a) :;; esac)"\n', [1], "a quoted $( ) counts: bash -n passes, the run dies")
+    cs("x=$(case a in (a|b) :;& c) :;; esac)\nx=$(case a in (a) :;;& (b) :;; d) :;; esac)\n", [1, 2],
+       "a bare pattern after ;& or ;;& is refused, a led one after ;; passes")
+    cs("x=$(case a in (a) :;; esac; echo b)\nx=$(echo)\ncase a in a) :;; esac\n", [],
+       "esac and the closing ) end the substitution's reach")
+    cs("x=$(case a in\n  # c) a comment\n  (a) :;;\nesac; echo '# case a in a)' \"case a in a)\")\n", [],
+       "comments and quoted text are not patterns")
+    cs("x=$(echo a#b $# \"\\\"\" \"$(echo \\\")\"; case a in a) :;; esac)\n", [1],
+       "a mid-word # is no comment; escapes in and out of quotes")
+    cs("x=$(echo \\)\ncase a in a) :;; esac)\n", [2], "an escaped ) does not close the substitution")
+    cs("x=$(cat <<E\ncase a in a) x;; esac\nE\ncat <<-'F'\n\tb) )\n\tF\ncase a in a) :;; esac)\n", [7],
+       "here-document bodies are skipped, and scanning resumes after the delimiter")
+    cs("x=$(cat <<<case; case a in a) :;; esac)\n", [1], "a here-string is not a here-document")
+    cs("x=$(echo $(( (1)+2 )) ${y:-z}; case a in a) :;; esac)\nx=$(( (1) ))${y}\ncase a in a) :;; esac\n",
+       [1], "arithmetic and ${ } nest and close")
+    cs("x=$(f() { case a in a) :;; esac; }; ( case b in b) :;; esac ))\n", [1],
+       "a function or subshell inside $( ) is still inside it")
+    cs("x=$(if t; then case a in a) :;; esac; fi; while t; do case b in\n b) :;; esac; done)\n", [1, 2],
+       "case after then and do is a keyword")
+    cs("x=$(t && case a in a) :;; esac)\nx=$(case a in (a) case b in b) :;; esac;; esac)\n", [1, 2],
+       "case after && and a nested case after a pattern are keywords")
+    cs("local rt case\ncase=$(echo case a in b)\nx=$(mycase a in b)\n", [],
+       "case as an argument, a variable or inside a word is not the keyword")
+    cs('x=$(case "$y" in ("a)") :;; \'b)\'|c) :;; esac)\n', [1], "a pattern's quoted ) is not its end")
+    cs("$(case a in a) :;; esac)\n\nx=$(case a in (a\\'\"\") :;;\n c) :;; esac)\n", [1, 4],
+       "a $( ) at the text's start; an escaped quote and an empty quote inside a led pattern")
+    cs("\n# $(\ncase a in a) :;; esac\nx=$(case a in (a);;\n b) :;; esac)\n", [5],
+       "a leading newline counts; a comment opens no $( ); ;; right after a pattern")
+    cs("x=$(echo ')' '' \")\" ${#a} $((1)) $(((1)+(2))); case a in a) :;; esac)\n", [1],
+       "quoted ), an empty quote, ${#...}, arithmetic: none closes the substitution")
+    cs("x=$(echo $((1)))\ncase a in a) :;; esac\nx=${y}$(case a in a) :;; esac)\n", [3],
+       "arithmetic and ${ } close where they end")
+    cs("x=$(echo # )\ncase a in a) :;; esac)\nx=$(case a in (a) :;;&(b) :;;\n c) :;; esac)\n", [2, 4],
+       "a comment's ) closes nothing; ;;& is consumed whole")
+    cs("x=$(cat <<E\nE\ncase a in a) :;; esac)\nx=$(case a in (a) :\nesac)\ncase b in b) :;; esac\n", [3],
+       "a here-document's delimiter can be its first line; esac after a body without ;; ends the case")
+    cs("x=$(cat <<-E\n\t\tE\ncase a in a) :;; esac)\nx=$(cat <<E\n\tE\ncase a in a) :;; esac\nE\n)\n", [3],
+       "<<- strips tabs before its delimiter, << does not")
+    cs("x=`echo $(case a in a) :;; esac)`; y=$(z=`case a in a) :;; esac`)\n", [1],
+       "case right after a backquote is a keyword; a $( ) inside backquotes counts")
+    # The CLI over a scratch repository: both rules, `--check` on the tree and at a ref.
+    import tempfile
+    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
+    from throwaway_git import throwaway_git_init
+    with tempfile.TemporaryDirectory() as d:
+        env = throwaway_git_init(d, "-q")
+        (Path(d) / "tools").mkdir()
+        (Path(d) / "tools/a.sh").write_text('f "${a[@]}"\nx=$(case a in a) :;; esac)\n')
+        (Path(d) / "tools/b.txt").write_text('f "${a[@]}"\n')
+
+        def cli(*args):
+            r = subprocess.run([sys.executable, "-I", __file__, *args], cwd=d, env=env,
+                               capture_output=True, text=True)
+            return r.returncode, r.stdout.split("\n")[:-1]
+
+        subprocess.run(["git", "add", "-A"], cwd=d, env=env, check=True)
+        subprocess.run(["git", "commit", "-qm", "x"], cwd=d, env=env, check=True)
+        want = (1, ['tools/a.sh:1: f "${a[@]}"', "tools/a.sh:2: x=$(case a in a) :;; esac)"])
+        st(cli("--check"), want, "--check prints each site of both rules in .sh files, rc 1")
+        (Path(d) / "tools/a.sh").write_text("x=$(case a in (a) :;; esac)\n")
+        st(cli("--check"), (0, []), "--check on the repaired tree passes (null)")
+        st(cli("--check", "--ref", "HEAD"), want, "--check --ref reads the commit, not the tree")
+        st(cli()[0], 2, "no arm prints the usage, rc 2")
     for f in fails:
         print("FAIL", f)
     print("bare_array self-test:", "FAILED" if fails else "ok")
@@ -133,7 +307,8 @@ if __name__ == "__main__":
     if "--check" in sys.argv:
         ref = sys.argv[sys.argv.index("--ref") + 1] if "--ref" in sys.argv else None
         hits = scan(ref)
-        print("\n".join(hits))
+        if hits:
+            print("\n".join(hits))
         sys.exit(1 if hits else 0)
     print(__doc__)
     sys.exit(2)
diff --git a/tools/audit/seat/instruments/bare_array.py.md b/tools/audit/seat/instruments/bare_array.py.md
index 529187f451..f3c694b6b2 100644
--- a/tools/audit/seat/instruments/bare_array.py.md
+++ b/tools/audit/seat/instruments/bare_array.py.md
@@ -11,3 +11,9 @@
   on the line or on a comment-only line directly above it; a line ending in
   `# mut:<name>` takes the reason above, and a reason placed after that marker
   is refused on any line, because it unanchors the self-test's mutant.
+  Second rule: a `case` pattern without its leading `(` inside a `$( ... )`,
+  `<( ... )` or `>( ... )` substitution, quoted or not, is refused: bash 3.2
+  ends the substitution at the pattern's `)`, so `bash -n` fails (PR 3520 put
+  one in `tick_loop.sh`, whose freshness check then refused every tick pass),
+  or, quoted, the run dies. The way out is the `(`, as in `(func) ...;;`; no
+  marker excuses one, since 3.2 never parses it.
diff --git a/tools/audit/seat/instruments/update_pr.sh.md b/tools/audit/seat/instruments/update_pr.sh.md
index f964bc717c..eac78f7f29 100644
--- a/tools/audit/seat/instruments/update_pr.sh.md
+++ b/tools/audit/seat/instruments/update_pr.sh.md
@@ -17,6 +17,7 @@
   body move of a PR whose head holds its handoff, with `HPO_UPDATE_BODY_ONLY=1`:
   a run that would then move the head (a DIRTY PR's clean main merge, an added
   row) refuses and pushes nothing, since that move skipped the review freeze.
+  A body carrying a generated figure block has it re-rendered (`figure_block.py refresh`, as `open_pr.sh` does) at the head the run pushes or patches, on both paths, before app_push.sh or body_patch.sh; a failed refresh refuses, pushing and patching nothing; a body with no block is untouched.
   When: updating a PR after review prep or a main merge, or re-bodying it.
   Refusal: as `remerge_main.sh` — a conflict stops, it is never resolved
   silently; no open PR at the branch stops before any push. Up front, each an
diff --git a/tools/audit/seat/pr_args.sh b/tools/audit/seat/pr_args.sh
index 63c2e08c89..dbf53479dc 100644
--- a/tools/audit/seat/pr_args.sh
+++ b/tools/audit/seat/pr_args.sh
@@ -485,9 +485,17 @@ pr_pushers() { # [<root>] [<rev>]: the census; one line per seam, exit 1 on any
 # copyin carries ref_privacy.py for the same reason: handoff_push.sh's guard
 # fails closed without it, so its reap arms never reached a push (#2668's CI).
 pr_args_self_test() (
-  local src t f=0 n=0 o m base code side body i reapsha UNREL
+  local src seat t f=0 n=0 o m base code side body i reapsha UNREL
   src=$PR_ARGS_DIR
   t=$(mktemp -d) || { echo "pr_args self-test: no temporary directory"; return 1; }
+  # The programs under test are copied from a snapshot of them taken here, never from the live
+  # checkout: a job step that moves the checkout mid-run (tick_loop.sh's restart onto origin/main)
+  # would otherwise hand the later arms the base's copies (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH).
+  # Only the files the arms copy in, and roster_lib.py, which pr_cap.py loads from beside itself: an arm
+  # naming one not listed fails at its cp, never reads the tree.
+  seat=$t/seat; mkdir "$seat" && (cd "$src" && cp -p delivery_row.sh gh_read.py handoff_push.sh open_pr.sh \
+    pr_args.sh pr_cap.py ref_privacy.py remerge_main.sh roster_lib.py update_pr.sh "$seat/") \
+    || { echo "pr_args self-test: no snapshot of the programs under test"; rm -rf "$t"; return 1; }
   # The pusher stubs the reap arms drive read this directory ($T is open_pr's topic).
   REAP_DIR=$t; export REAP_DIR
   # A stopped pusher's stub app_push: it records itself and a two-level sleep
@@ -542,8 +550,8 @@ STUB
   copyin() { # <mutant|->: copies of the scripts, less the named mutant's line
     local g
     for g in open_pr.sh update_pr.sh handoff_push.sh remerge_main.sh delivery_row.sh pr_args.sh pr_cap.py ref_privacy.py gh_read.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"
-      else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"
+      else grep -v "# mut:$1\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi
     done
   }
   i=0
@@ -692,8 +700,8 @@ STUB
   git -C "$o" reset -q --hard "$base"
   relsrc() { # <mutant|-> <fresh clone> <sibling>: source by a relative path, cd to the sibling, ask
     mkdir -p "$2/tools/audit/seat"
-    if [ "$1" = - ]; then cp "$src/pr_args.sh" "$2/tools/audit/seat/pr_args.sh"
-    else grep -v "# mut:$1\$" "$src/pr_args.sh" > "$2/tools/audit/seat/pr_args.sh"; fi
+    if [ "$1" = - ]; then cp "$seat/pr_args.sh" "$2/tools/audit/seat/pr_args.sh"
+    else grep -v "# mut:$1\$" "$seat/pr_args.sh" > "$2/tools/audit/seat/pr_args.sh"; fi
     ( unset PR_ARGS_DIR; cd "$2" && . ./tools/audit/seat/pr_args.sh && cd "$3" && PR_NAME=fresh pr_tools_fresh ) > "$t/out" 2>&1
   }
   relsrc - "$t/fr" "$t/st"; ck "pr_args: sourced by a relative path from a fresh clone, then cd'd into a stale sibling, passes" $?
@@ -1259,8 +1267,8 @@ STUB
     git -C "$m" worktree prune; git -C "$m" branch -qD fix/r 2>/dev/null
     git -C "$o" branch -qD fix/r 2>/dev/null
     for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"
-      else grep -v -e "# mut:${1%%+*}\$" -e "# mut:${1##*+}\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi  # a+b: two mutants at once
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"
+      else grep -v -e "# mut:${1%%+*}\$" -e "# mut:${1##*+}\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi  # a+b: two mutants at once
     done
     cp "$t/body.md" "$t/bR.md"
     HPO_STATE_DIR=$sd STUB_DIR=$sdir BR=fix/r BR_FIXED=1 bash "$m/tools/audit/seat/open_pr.sh" r "$codeR" T G > "$t/outo" 2>&1 & op=$!
@@ -1412,7 +1420,7 @@ STUB
     sd=$(cd "$sd" && pwd -P); rm -rf "$sdir"; mkdir -p "$sdir"; figbody "$2"
     printf 'z\n' > "$o/zz" && git -C "$o" add zz && git -C "$o" -c user.name=t -c user.email=t@t commit -q -m "main file"
     for g in open_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi
     done
     HPO_STATE_DIR=$sd STUB_DIR=$sdir bash "$m/tools/audit/seat/open_pr.sh" f "$codeF" T G > "$t/fo" 2>&1; echo $? > "$t/frc"
     git -C "$o" cat-file -e fix/f-pr:dev/programme/delivery/5.md 2>/dev/null && echo 1 > "$t/frow" || echo 0 > "$t/frow"
@@ -1435,6 +1443,59 @@ STUB
   ck "open_pr: a re-run after an open closed at its row push clears the left-over branch and worktree and opens" $?
   figrun opfig2 block; figrun opclear block keep; [ "$(cat "$t/frc")" != 0 ] && [ "$(cat "$t/frow")" = 0 ]
   ck "  mutant mut:opclear (its line deleted): the re-run fails at git worktree add -b on the left-over branch (the defect)" $?
+  # R10-HOTFIX-UPDATEPR-FIGURE-REFRESH: update_pr.sh re-renders the body's figure blocks at the head it
+  # pushes (moved-head path, before app_push) or patches (body-only path, before body_patch.sh), as
+  # open_pr.sh's op_figures does. fix/g starts at $base; handoff/f's pusher stub is lint's figure-block
+  # head check; the stub figure_block.py rewrites head= to HEAD, notes each call and fails while $t/figfail exists.
+  cat > "$m/tools/pr/figure_block.py" <<STUBF
+import os, re, subprocess, sys
+open("$t/figcalled", "a").close()
+if os.path.exists("$t/figfail"): sys.exit(1)
+f = sys.argv[sys.argv.index("refresh") + 1]
+h = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
+t = re.sub(r"head=[0-9a-f]{40}", "head=" + h, open(f).read())
+open(f, "w").write(t)
+STUBF
+  cp "$t/bin/gh" "$t/gh.orig"
+  printf '#!/bin/sh\ncase "$*" in *--head*) echo 5 ;; *mergeStateStatus*) echo CLEAN ;; "pr view"*) echo "a title" ;; *) exit 99 ;; esac\n' > "$t/bin/gh"
+  printf '#!/bin/bash\necho called >> "%s/ubp.log"\nh=$(grep -o "^<!-- figure-block: [a-z-]* mb=[0-9a-f]* head=[0-9a-f]*" "$5" | grep -o "head=.*" | cut -c6-)\n[ -z "$h" ] || [ "$h" = "$4" ] || { echo "body_patch: REFUSE: figure-block scope-line names another head ($h)"; exit 1; }\necho "body_patch: OK"\n' "$t" > "$t/ubp.sh"
+  ufig() { # <mutant|-> <code sha|-> <block|none>: update_pr.sh fix/g over a body with (or without) a figure block naming the code head
+    rm -f "$t/figcalled"
+    if [ "$3" = block ]; then printf '## Head\n\nthe body\n\n## Figures\n\n<!-- figure-block: scope-line mb=%s head=%s -->\n~~~text\nx\n~~~\n<!-- /figure-block -->\n' "$base" "$codeF" > "$t/bu.md"
+    else printf '## Head\n\nthe body\n' > "$t/bu.md"; fi
+    git -C "$o" rev-parse fix/g > "$t/ubefore" 2>/dev/null || echo none > "$t/ubefore"
+    HANDOFF_TOPIC=f HPO_BODY_PATCH=$t/ubp.sh run "$1" update_pr.sh fix/g "$2" "$t/bu.md"
+    git -C "$o" rev-parse fix/g > "$t/uafter"
+  }
+  ufresh() { git -C "$o" branch -f fix/g "$base"; rm -f "$t/figfail" "$t/ubp.log"; }
+  ubody() { grep -o '^<!-- figure-block: [a-z-]* mb=[0-9a-f]* head=[0-9a-f]*' "$t/bu.md" | grep -o 'head=.*' | cut -c6-; }
+  ufresh; ufig - "$codeF" block
+  [ "$(cat "$t/rc")" = 0 ] && [ "$(ubody)" = "$(cat "$t/uafter")" ] && [ "$(cat "$t/uafter")" != "$(cat "$t/ubefore")" ]
+  ck "update_pr: a moved head with a figure block pushes a body whose block names the new head" $?
+  ufresh; ufig updfig1 "$codeF" block
+  [ "$(cat "$t/rc")" != 0 ] && grep -qF "figure-block scope-line names another head" "$t/out"
+  ck "  mutant mut:updfig1 (its line deleted): the push carries a block naming another head and is refused" $?
+  ufresh; touch "$t/figfail"; ufig - "$codeF" block
+  [ "$(cat "$t/rc")" != 0 ] && grep -qF "update_pr: REFUSE: the figure-block refresh at the head to push failed" "$t/out" && [ "$(cat "$t/uafter")" = "$base" ]
+  ck "update_pr: a failing refresh at the head to push refuses and pushes nothing" $?
+  ufresh; ufig - "$codeF" block; rm -f "$t/ubp.log"
+  ufig - - block
+  [ "$(cat "$t/rc")" = 0 ] && [ "$(cat "$t/ubefore")" = "$(cat "$t/uafter")" ] && grep -qF "update_pr: BODY-ONLY" "$t/out" && [ "$(ubody)" = "$(cat "$t/uafter")" ] && [ "$(wc -l < "$t/ubp.log")" = 1 ]
+  ck "update_pr: a body-only run over a block naming the code head patches a body naming the live head" $?
+  ufig updfig2 - block
+  [ "$(cat "$t/rc")" != 0 ] && grep -qF "body_patch: REFUSE: figure-block scope-line names another head" "$t/out"
+  ck "  mutant mut:updfig2 (its line deleted): body_patch.sh is handed a block naming another head and refuses" $?
+  rm -f "$t/ubp.log"; touch "$t/figfail"; ufig - - block
+  [ "$(cat "$t/rc")" != 0 ] && grep -qF "update_pr: REFUSE: the figure-block refresh at the unmoved head failed" "$t/out" && [ ! -e "$t/ubp.log" ] && [ "$(cat "$t/ubefore")" = "$(cat "$t/uafter")" ]
+  ck "update_pr: a failing refresh on the body-only path refuses and patches nothing" $?
+  ufresh; ufig - "$codeF" none
+  [ "$(cat "$t/rc")" = 0 ] && [ ! -e "$t/figcalled" ] && ! grep -q 'figure-block' "$t/bu.md"
+  ck "null control: a body with no figure block never reaches the refresh and is pushed as before" $?
+  ufresh; ufig - "$codeF" none; ufig - - none
+  [ "$(cat "$t/rc")" = 0 ] && [ ! -e "$t/figcalled" ] && grep -qF "update_pr: BODY-ONLY" "$t/out"
+  ck "null control: a body-only run over a body with no figure block never reaches the refresh" $?
+  git -C "$o" branch -qD fix/g; git -C "$o" reset -q --hard "$base"; cp "$t/gh.orig" "$t/bin/gh"
+  git -C "$m" worktree prune; git -C "$m" branch -qD fix/g 2>/dev/null; git -C "$m" update-ref -d refs/remotes/origin/fix/g; true
   # R10-FLOW-BODY-ONLY parts (a) and (b), ruling R4: update_pr.sh merges origin/main only when the PR
   # is DIRTY or the merge would conflict, and a head the run leaves unmoved is re-bodied by
   # body_patch.sh (here a stub, HPO_BODY_PATCH) with no push. handoff/v carries a push stub that
@@ -1558,7 +1619,7 @@ GH
     rm -rf "$sd" "$sdir"; mkdir -p "$sdir" "$sd"; sd=$(cd "$sd" && pwd -P)
     git -C "$m" worktree prune; git -C "$m" branch -qD fix/r 2>/dev/null; git -C "$o" branch -qD fix/r 2>/dev/null
     for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi
     done
     case ${2:-} in edit) touch "$sdir/editfail" ;; postpush) touch "$sdir/p2postfail" ;; selftest) touch "$sdir/p2selftest" ;; host) touch "$sdir/p2selftest" "$sdir/hostfail" ;; stmix|body) touch "$sdir/p2$2" "$sdir/hostfail" ;;
       stalefig) touch "$sdir/hostfail" "$sdir/figfail"; mkdir -p "$sd/pr/r" && printf '  REFUSE   self-test             FAIL x\n' > "$sd/pr/r/p2.log" ;; *) touch "$sdir/p2fail" ;; esac
@@ -1650,11 +1711,11 @@ STUB
   }
   hrlib() { # <-|mutant|ret:tag|shared>: the library the next hrrun sources; ret:<tag> turns that line's `|| return 1` into `|| return 0`
     case $1 in
-      -) cp "$src/pr_args.sh" "$t/hr/lib.sh" ;;
-      ret:*) sed "/# $1\$/s/|| return 1/|| return 0/" "$src/pr_args.sh" > "$t/hr/lib.sh" ;;
+      -) cp "$seat/pr_args.sh" "$t/hr/lib.sh" ;;
+      ret:*) sed "/# $1\$/s/|| return 1/|| return 0/" "$seat/pr_args.sh" > "$t/hr/lib.sh" ;;
       # one tree for every measurement, replaced by whichever run starts next: the blocked head's pr_step_sig
-      shared) sed '/# ret:sigpriv$/s|w=.*|w=$3/tree; git -C "$1" worktree remove --force "$w" >/dev/null 2>\&1; rm -rf "$w"; mkdir -p "$w"|' "$src/pr_args.sh" > "$t/hr/lib.sh" ;;
-      *) grep -v "# mut:$1\$" "$src/pr_args.sh" > "$t/hr/lib.sh" ;;
+      shared) sed '/# ret:sigpriv$/s|w=.*|w=$3/tree; git -C "$1" worktree remove --force "$w" >/dev/null 2>\&1; rm -rf "$w"; mkdir -p "$w"|' "$seat/pr_args.sh" > "$t/hr/lib.sh" ;;
+      *) grep -v "# mut:$1\$" "$seat/pr_args.sh" > "$t/hr/lib.sh" ;;
     esac
   }
   hrrun() { # <head sha> [main sha] [log] -> pr_host_refusal's status
@@ -1823,7 +1884,7 @@ STUB
     local sd=$t/mconf-$1 g
     rm -rf "$sd"; mkdir -p "$sd"; sd=$(cd "$sd" && pwd -P); git -C "$m" worktree prune; git -C "$m" branch -qD fix/q 2>/dev/null
     for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi
     done
     HPO_STATE_DIR=$sd BR=fix/q BR_FIXED=1 bash "$m/tools/audit/seat/open_pr.sh" q "$codeR" T G > "$t/outq" 2>&1; echo $? > "$t/rcq"
     [ -d "$sd/pr/q/wt" ] && echo kept > "$t/wtq" || echo gone > "$t/wtq"
@@ -1846,8 +1907,8 @@ STUB
     local sd=$t/unp-$1-$2-${3:--} g
     rm -rf "$sd" "$sd.link" "$t/s$i"; git -C "$m" worktree prune; git -C "$m" branch -qD fix/u 2>/dev/null; mkdir -p "$sd/pr/u"; sd=$(cd "$sd" && pwd -P)
     for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"
-      else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"
+      else grep -v "# mut:$1\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi
     done
     git -C "$m" fetch -q origin fix/u && git -C "$m" worktree add -q -b fix/u "$sd/pr/u/wt" origin/fix/u || return 1
     [ "$2" = 0 ] || { printf 'row\n' > "$sd/pr/u/wt/row" && git -C "$sd/pr/u/wt" add row && git -C "$sd/pr/u/wt" commit -q -m row; }
@@ -1948,7 +2009,7 @@ STUB
   fi
   rmrun() { # <mutant|-> <branch>: remerge_main.sh on <branch> in worktree $t/rmw; the output in $t/out
     local g; git -C "$t/rmm" worktree remove --force "$t/rmw" 2>/dev/null; rm -rf "$t/rmw"; git -C "$t/rmm" worktree prune
-    for g in remerge_main.sh pr_args.sh gh_read.py; do grep -v "# mut:$1\$" "$src/$g" > "$t/rmm/tools/audit/seat/$g"; done
+    for g in remerge_main.sh pr_args.sh gh_read.py; do grep -v "# mut:$1\$" "$seat/$g" > "$t/rmm/tools/audit/seat/$g"; done
     git -C "$t/rmm" fetch -q origin "$2" && git -C "$t/rmm" worktree add -q -B "$2" "$t/rmw" "origin/$2" \
       && PATH="$t/rmgit:$PATH" bash "$t/rmm/tools/audit/seat/remerge_main.sh" 7 "$t/rmw" "$2" "$t/body.md" > "$t/out" 2>&1
     echo $? > "$t/rc"
@@ -2113,7 +2174,7 @@ print(n)' "$1"
   # line above leaves that line running on into the next (round 2's first mut:fggc did, and its arm
   # read the broken copy as a pass). mutshape <files...>: exit 1 naming each such line.
   mutshape() { awk 'prev ~ /\\$/ && /# mut:[A-Za-z0-9]+$/ { print FILENAME ":" FNR; bad = 1 } { prev = $0 } END { exit bad }' "$@"; }
-  (cd "$src" && mutshape open_pr.sh update_pr.sh handoff_push.sh remerge_main.sh delivery_row.sh pr_args.sh)
+  (cd "$seat" && mutshape open_pr.sh update_pr.sh handoff_push.sh remerge_main.sh delivery_row.sh pr_args.sh)
   ck "every # mut: line is a whole statement, never one continued from the line above" $?
   printf 'a \\\n  b  # mut:x\n' > "$t/mutshape.sh"; ! mutshape "$t/mutshape.sh" >/dev/null
   ck "null control: a # mut: line continued from the line above is named" $?
@@ -2125,7 +2186,7 @@ print(n)' "$1"
   rkrun() { # <mutant|-> <stub rc> -> $t/rk.argv: what the stub saw; $t/rk.err: the statement's stderr
     : > "$t/rk.argv"
     printf '#!/bin/bash\necho "$*" >> "%s/rk.argv"\nexit %s\n' "$t" "$2" > "$t/rkseat/bus.sh"
-    if [ "$1" = - ]; then grep -h '# mut:rekey$' "$src/open_pr.sh"; else grep -h '# mut:rekey$' "$src/open_pr.sh" | grep -v "# mut:$1\$"; fi > "$t/rk.line"
+    if [ "$1" = - ]; then grep -h '# mut:rekey$' "$seat/open_pr.sh"; else grep -h '# mut:rekey$' "$seat/open_pr.sh" | grep -v "# mut:$1\$"; fi > "$t/rk.line"
     SEAT=$t/rkseat PR_NAME=open_pr T=ht N=77 bash "$t/rk.line" 2> "$t/rk.err"
     echo $? > "$t/rk.rc"
   }
@@ -2138,7 +2199,7 @@ print(n)' "$1"
   rkrun rekey 0; [ ! -s "$t/rk.argv" ]
   ck "  mutant mut:rekey (its line deleted) re-keys nothing" $?
   # The cap's own counting rule, which orchestrator_tick.py imports too.
-  python3 -I "$src/pr_cap.py" --self-test > "$t/cap.out" 2>&1 && grep -q 'pr_cap self-test: [1-9][0-9]* checks, 0 failed' "$t/cap.out"
+  python3 -I "$seat/pr_cap.py" --self-test > "$t/cap.out" 2>&1 && grep -q 'pr_cap self-test: [1-9][0-9]* checks, 0 failed' "$t/cap.out"
   ck "pr_cap.py --self-test: its tally says 0 failed" $?
   reap
   kill "$UNREL" 2>/dev/null; wait "$UNREL" 2>/dev/null || :
diff --git a/tools/audit/seat/tick_loop.sh b/tools/audit/seat/tick_loop.sh
index d0b7147789..0b35a54fa4 100644
--- a/tools/audit/seat/tick_loop.sh
+++ b/tools/audit/seat/tick_loop.sh
@@ -463,9 +463,9 @@ f = open(sys.argv[1], "a"); fcntl.flock(f, fcntl.LOCK_EX); open(sys.argv[1] + ".
       local v=$t/victim-$1.git; rm -f "$t/shadow"; throwaway_git_init "$v" -q --bare || return 1
       out=$(export HPO_HEARTBEAT_REMOTE=$v TICK_RC=1
         case $1 in
-          func) . "$t/execfn"; export -f exec; "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
-          bashenv) BASH_ENV=$t/execfn "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
-          none) "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
+          (func) . "$t/execfn"; export -f exec; "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
+          (bashenv) BASH_ENV=$t/execfn "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
+          (none) "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
         esac 2>&1); src=$?
       refs=$(git -C "$v" for-each-ref | grep -c .); }
     for c in func bashenv; do
diff --git a/tools/audit/seat/update_pr.sh b/tools/audit/seat/update_pr.sh
index 611d4360f3..bd00868f07 100755
--- a/tools/audit/seat/update_pr.sh
+++ b/tools/audit/seat/update_pr.sh
@@ -97,6 +97,15 @@ TTL=$(gh pr view "$N" -R $R --json title -q .title)
 _added=$(ensure_row . "$N" "$(row_line "$N" $R "$TTL")")
 ROW=""; [ -z "$_added" ] || ROW="adds one commit containing only this PR's own row, \`$_added\`"
 M=$(git rev-parse --short origin/main); H=$(git rev-parse HEAD)
+# A generated figure block names the head it was rendered at (figure_block.py refresh, as open_pr.sh's
+# op_figures), and the merges and the row above moved it: re-render at the head this run pushes or patches,
+# before either. A body with no block is untouched; a failed refresh refuses, pushing and patching nothing.
+upd_figures() { # <where>
+  grep -q '^<!-- figure-block: ' "$B" || return 0
+  python3 -I "$PRT/figure_block.py" refresh "$B" --base origin/main --head HEAD > $WT.fig.log 2>&1 && return 0
+  pr_refuse "the figure-block refresh $1 failed; nothing is pushed or patched:
+$(tail -n 20 $WT.fig.log)"
+}
 # HPO_UPDATE_BODY_ONLY (cloud_relay.sh's handoff_arm, on a body-only move it does not review-freeze):
 # the head must stay the live head, so a DIRTY merge of main or an added row refuses, pushing nothing
 # (#3089 review round 2): only the orchestrator, past the freeze, moves a head under review.
@@ -117,6 +126,7 @@ import sys; from head_note import prefix
 p,H=sys.argv[1:3]; s=open(p).read()
 s=prefix(s,"`%s` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.\n\n"%H); open(p,'w').write(s)
 E
+  upd_figures "at the unmoved head"  # mut:updfig2
   rc=0; ( cd "$WT" && bash "${HPO_BODY_PATCH:-$SEAT/body_patch.sh}" --repo $R "$N" "$H" "$B" ) > $WT.log 2>&1 || rc=$?
   cat $WT.log
   [ "$rc" = 0 ] || pr_refuse "body-only: body_patch.sh refused #$N at $H (exit $rc); its log is $WT.log"
@@ -131,6 +141,7 @@ if MM: pre="`%s` "%H + ((N+" and then ") if N else "") + "merges origin/main `%s
 else: pre="`%s` "%H + " and then ".join(x for x in (N, R) if x) + ".\n\n"  # main merged cleanly: not merged (R4)
 s=prefix(s,pre); open(p,'w').write(s)
 E
+upd_figures "at the head to push"  # mut:updfig1
 if test -f tools/audit/app_push.sh; then _push=tools/audit/app_push.sh; else _push=tools/pr/app_push.sh; fi
 RO=""; [ "$(git rev-parse "$H^@")" != "$LIVE" ] || RO=--row-only  # mut:rowonly
 [ -n "$RO" ] || RO=--reuse  # mut:updreuse
diff --git a/tools/ci/selftest_closures.json b/tools/ci/selftest_closures.json
index d56ec9a60d..e81ad4d9d5 100644
--- a/tools/ci/selftest_closures.json
+++ b/tools/ci/selftest_closures.json
@@ -13,9 +13,9 @@
     "."
    ],
    "dirs": [],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "app-approval": {
    "run_sha": "3ef1d085ae4e19ef74bdbdc0ca3474ec99634299b24b819a9239ec197b09ef16",
@@ -31,9 +31,9 @@
     ".",
     "tools/audit/seat"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "app-push": {
    "run_sha": "26cc360dafe7a744810e0897ce086c705735b348b8f5bc4834ff9f42326ae45b",
@@ -81,11 +81,11 @@
     "tools/policy/vendor",
     "tools/pr"
    ],
+   "index": true,
+   "objects": true,
    "git": [
     "merge-base"
-   ],
-   "index": true,
-   "objects": true
+   ]
   },
   "app-verdict-poster": {
    "run_sha": "c71974e46a67a03947b4fa59b07a99c75e6a8895c556223f837636fe1440ae70",
@@ -116,13 +116,14 @@
     "tools/policy",
     "tools/pr"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "bare-array-expansion": {
    "run_sha": "88034369e109a71b0f038cb5eea66a1b3947a7c215421e4cd0f53cff38d2578b",
    "files": [
+    "tests/throwaway_git.py",
     "tools/audit/prepare_baseline.sh",
     "tools/audit/repo_root.sh",
     "tools/audit/seat/a1_dispatch_arms.sh",
@@ -165,12 +166,18 @@
     "tools/pr/push.sh"
    ],
    "probes": [
-    "."
+    ".",
+    "tests",
+    "tools",
+    "tools/audit",
+    "tools/audit/seat"
+   ],
+   "dirs": [
+    "tests"
    ],
-   "dirs": [],
-   "git": [],
    "index": true,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "beat-job-rows": {
    "run_sha": "277c2a90e900de88586526a82d6e3ca9ae9f278481064ce379d931a1d7e36364",
@@ -1387,22 +1394,7 @@
     "dev/audit/rounds/round4/D1/verify2_d102.py",
     "dev/audit/rounds/round4/D1/verify2_d1inst.py",
     "dev/audit/rounds/round4/D10",
-    "dev/audit/rounds/round4/D10/coverage_measure.sh",
-    "dev/audit/rounds/round4/D10/d10_own_D10-01.py",
-    "dev/audit/rounds/round4/D10/d10_own_D10-01.sh",
-    "dev/audit/rounds/round4/D10/d10_own_D10-02.py",
-    "dev/audit/rounds/round4/D10/d10_own_D10-03.py",
-    "dev/audit/rounds/round4/D10/log_when_unavailable.py",
-    "dev/audit/rounds/round4/D10/mypy_arms.sh",
-    "dev/audit/rounds/round4/D10/qs_rules.out.txt",
-    "dev/audit/rounds/round4/D10/qs_rules.py",
-    "dev/audit/rounds/round4/D10/quality_scale.draft.yaml",
-    "dev/audit/rounds/round4/D10/reports",
-    "dev/audit/rounds/round4/D10/reports/FINDER.md",
-    "dev/audit/rounds/round4/D10/verify-0-1.md",
-    "dev/audit/rounds/round4/D10/verify-0-2.md",
-    "dev/audit/rounds/round4/D10/verify-0-3.md",
-    "dev/audit/rounds/round4/D10/verify3",
+    "dev/audit/rounds/round4/D10/**",
     "dev/audit/rounds/round4/D10/verify3/**",
     "dev/audit/rounds/round4/D11",
     "dev/audit/rounds/round4/D11/d11_own_D11-01.py",
@@ -1664,9 +1656,7 @@
     "dev/audit/rounds/round4/resume_row.py",
     "dev/audit/rounds/round5",
     "dev/audit/rounds/round5-fix",
-    "dev/audit/rounds/round5-fix/R5-D7",
-    "dev/audit/rounds/round5-fix/R5-D7/learner_guard_ends.py",
-    "dev/audit/rounds/round5-fix/R5-INST-01",
+    "dev/audit/rounds/round5-fix/**",
     "dev/audit/rounds/round5-fix/R5-INST-01/**",
     "dev/audit/rounds/round5/D0",
     "dev/audit/rounds/round5/D0/seat-a",
@@ -1709,9 +1699,7 @@
     "dev/audit/rounds/round5/D4/seat-a",
     "dev/audit/rounds/round5/D4/seat-a/sweep.mjs",
     "dev/audit/rounds/round5/D7",
-    "dev/audit/rounds/round5/D7/seat-a",
-    "dev/audit/rounds/round5/D7/seat-a/sysid_step_bias.py",
-    "dev/audit/rounds/round5/D7/seat-b",
+    "dev/audit/rounds/round5/D7/**",
     "dev/audit/rounds/round5/D7/seat-b/**",
     "dev/audit/rounds/round5/D8",
     "dev/audit/rounds/round5/D8/seat-b",
@@ -2419,23 +2407,8 @@
     "tools/audit/seat/wt_sync.sh",
     "tools/audit/worktree_gc.sh",
     "tools/ci",
-    "tools/ci/alert_list.py",
-    "tools/ci/alert_list_mutants.sh",
-    "tools/ci/codescan_wait.py",
-    "tools/ci/fixtures",
-    "tools/ci/fixtures/gate_busy_defer_runs.json",
-    "tools/ci/fixtures/ruleset",
+    "tools/ci/**",
     "tools/ci/fixtures/ruleset/**",
-    "tools/ci/gate.py",
-    "tools/ci/ghapi.py",
-    "tools/ci/prelude.py",
-    "tools/ci/ruleset_cutover.py",
-    "tools/ci/selftest_closures.json",
-    "tools/ci/selftest_scope.py",
-    "tools/ci/selftest_scope_mutants.sh",
-    "tools/ci/selftest_step.sh",
-    "tools/ci/sweep.py",
-    "tools/ci/sweep_selftest.py",
     "tools/coverage",
     "tools/coverage/**",
     "tools/devices",
@@ -2566,6 +2539,7 @@
     "tools/audit/seat/body_push.sh",
     "tools/audit/seat/carry_fold.py",
     "tools/audit/seat/gh_read.py",
+    "tools/audit/seat/pr_args.sh",
     "tools/audit/seat/record_row.py",
     "tools/audit/seat/ref_privacy.py",
     "tools/audit/seat/roster_lib.py",
@@ -2578,9 +2552,9 @@
     "tools/audit",
     "tools/audit/seat"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "bottleneck-alert": {
    "run_sha": "ed4dead33c2d118cec7a83aa53d6448d96c28ed9b4b8f3880bc9fb7d275eb144",
@@ -2594,9 +2568,9 @@
     "tools/audit/seat"
    ],
    "dirs": [],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "budget-raise-gate": {
    "run_sha": "8e2afa7d1084b7223a39f0ef593e419b78e3a724781a06ccb99196801427962a",
@@ -2626,9 +2600,9 @@
     "tests",
     "tools/policy"
    ],
-   "git": [],
    "index": true,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "carry-check-and-the": {
    "run_sha": "f974a043ac14814d7a3782bea1f5b9cfe6a2c26dbba0f5a88b81031484603058",
@@ -2737,6 +2711,7 @@
     "commit-tree",
     "describe",
     "diff",
+    "fetch",
     "log",
     "ls-tree",
     "merge",
@@ -2768,9 +2743,9 @@
     "tools/ci",
     "tools/pr"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "ci-probe-instrument": {
    "run_sha": "80189dc4b271d2c5242734dec361f9fa8920e2beb5a67d7965c979630570ca57",
@@ -2803,20 +2778,21 @@
     "tests",
     "tools/audit/seat"
    ],
+   "index": true,
+   "objects": true,
    "git": [
     "fetch",
     "maintenance",
     "rev-list"
-   ],
-   "index": true,
-   "objects": true
+   ]
   },
   "ci-watcher": {
    "run_sha": "820b4913eacfeeee41bc39a41bfb2b5cf11e5d7350295ebc90b3b3dc65d18da7",
    "files": [
     "tools/audit/seat/ci-watch.sh",
     "tools/audit/seat/gh_read.py",
-    "tools/audit/seat/merge_train.py"
+    "tools/audit/seat/merge_train.py",
+    "tools/audit/seat/pr_args.sh"
    ],
    "probes": [
     ".",
@@ -2828,9 +2804,9 @@
    "dirs": [
     "tools/audit/seat"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "cloud-dispatcher": {
    "run_sha": "e49c5d629ee31f1ed994740ee1ca890f3771bd1c231c59a91cab8b879ac0191e",
@@ -2914,18 +2890,20 @@
    "run_sha": "0a2fb43948f79c43c90c697eeff8b63e4c98d7ab176a35b3e06398f29fcd69a8",
    "files": [
     "tests/throwaway_git.sh",
-    "tools/audit/seat/cloud-setup.sh"
+    "tools/audit/seat/cloud-setup.sh",
+    "tools/audit/seat/pr_args.sh"
    ],
    "probes": [
     ".",
+    "tests",
     "tools",
     "tools/audit",
     "tools/audit/seat"
    ],
    "dirs": [],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "code-scanning-alert-lister": {
    "run_sha": "4c9e65ae7052e1b039877a4cfeed610ecaf150af983cf72654f5abbf6c161cad",
@@ -2936,9 +2914,9 @@
     "."
    ],
    "dirs": [],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "code-scanning-wait": {
    "run_sha": "919a02871862a9dee51633b9df10d74fea148fd920c3f71e01a60aec416a14ee",
@@ -2957,9 +2935,9 @@
    "dirs": [
     "tools/ci"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "codeql-leg-scope": {
    "run_sha": "949543911e071c99df910451558db232c5be07b3c50fd8b5c797aa510e2660e0",
@@ -2977,11 +2955,11 @@
    "dirs": [
     "tests"
    ],
+   "index": false,
+   "objects": true,
    "git": [
     "diff"
-   ],
-   "index": false,
-   "objects": true
+   ]
   },
   "comment-poster": {
    "run_sha": "9991c3bb0ea6050b48c71c087bd66e39bd2058e14bc412b8e0191c56fb27febe",
@@ -3006,9 +2984,9 @@
     "tools/policy",
     "tools/pr"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "critical-path-and-flow": {
    "run_sha": "0ba2529c06b1249ce07c70b8c93a13dea43c594e2cae1de8dc3daf1e3a2e2d1a",
@@ -3034,11 +3012,11 @@
     "tools/audit/seat",
     "tools/audit/seat/fixtures/ci_critpath"
    ],
+   "index": false,
+   "objects": true,
    "git": [
     "show"
-   ],
-   "index": false,
-   "objects": true
+   ]
   },
   "day-chart": {
    "run_sha": "baf2fd4638f92c6a5b8d925f01b49a3d02568db7ee93785ddb86c60126ce82a4",
@@ -3060,10 +3038,12 @@
    "files": [
     "tests/throwaway_git.sh",
     "tools/audit/seat/delivery_row.sh",
+    "tools/audit/seat/pr_args.sh",
     "tools/audit/seat/ref_privacy.py"
    ],
    "probes": [
     ".",
+    "tests",
     "tools",
     "tools/audit",
     "tools/audit/seat"
@@ -3071,9 +3051,9 @@
    "dirs": [
     "tools/audit/seat"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "dependabot-merge-decision": {
    "run_sha": "a7d826e0398adb40091c4957951beec5a48cd9edba2f8729f222b5c07f562291",
@@ -3087,9 +3067,9 @@
     "tools/pr"
    ],
    "dirs": [],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "dependency-graph-census": {
    "run_sha": "2fc275964d5628cecf27226ec91672f83abf35c8fd29a39db34fe589e240479d",
@@ -3637,6 +3617,7 @@
     "tests/mutation_ledger/killed_by/draw_range.py",
     "tests/mutation_ledger/killed_by/drift.py",
     "tests/mutation_ledger/killed_by/driving_grade.py",
+    "tests/mutation_ledger/killed_by/duty_legs.py",
     "tests/mutation_ledger/killed_by/duty_switch.py",
     "tests/mutation_ledger/killed_by/early_cutoff.py",
     "tests/mutation_ledger/killed_by/entity.py",
@@ -3688,6 +3669,7 @@
     "tests/mutation_ledger/killed_by/slot_drivers.py",
     "tests/mutation_ledger/killed_by/snapshots.py",
     "tests/mutation_ledger/killed_by/store.py",
+    "tests/mutation_ledger/killed_by/supply_hold.py",
     "tests/mutation_ledger/killed_by/switch.py",
     "tests/mutation_ledger/killed_by/sysid.py",
     "tests/mutation_ledger/killed_by/tariff.py",
@@ -3795,9 +3777,9 @@
     "."
    ],
    "dirs": [],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "dispatch-cap": {
    "run_sha": "e142fa84a5fb375179e966f5d9a0bf6c3b83fe2ca152c16f90a04bc8c8ee2085",
@@ -3809,16 +3791,17 @@
     "."
    ],
    "dirs": [],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "failure-log-reader": {
    "run_sha": "79b967aa875bee34c43b9c4194bda86510bdb0f9e98c3df4174bb87462f8852b",
    "files": [
     "tools/audit/seat/failure_logs.sh",
     "tools/audit/seat/gh_read.py",
-    "tools/audit/seat/merge_train.py"
+    "tools/audit/seat/merge_train.py",
+    "tools/audit/seat/pr_args.sh"
    ],
    "probes": [
     ".",
@@ -3830,9 +3813,9 @@
    "dirs": [
     "tools/audit/seat"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "features-block": {
    "run_sha": "b7aa6fd84535cc431422519c2871f860cb64a70b49eda145e6c5e9df4937aefc",
@@ -3869,12 +3852,16 @@
     "tests/delivery_status.py",
     "tests/derive_closures.sh",
     "tests/dom_stub.mjs",
+    "tests/entities.py",
     "tests/env_drift.py",
     "tests/features.py",
     "tests/finite_boundary.py",
+    "tests/gate_lock.py",
     "tests/golden.py",
+    "tests/ha_floor.py",
     "tests/harness.py",
     "tests/host_probe.py",
+    "tests/issue996_count.py",
     "tests/lane_skip.py",
     "tests/layout.json",
     "tests/layout.py",
@@ -3961,6 +3948,7 @@
     "tools/audit/seat/record_beat.py",
     "tools/audit/seat/record_row.py",
     "tools/audit/seat/ref_privacy.py",
+    "tools/audit/seat/remerge_main.sh",
     "tools/audit/seat/resume_doc.py",
     "tools/audit/seat/review_carry.py",
     "tools/audit/seat/review_packet.py",
@@ -4015,6 +4003,7 @@
     "tools/policy/figure_lint.mjs",
     "tools/policy/fragments_sync.mjs",
     "tools/policy/friction_issues.mjs",
+    "tools/policy/legacy_control_files.json",
     "tools/policy/policy_lint.mjs",
     "tools/policy/policy_lint_envmatrix.mjs",
     "tools/policy/policy_lint_mutants.mjs",
@@ -4107,9 +4096,9 @@
     "tools/policy/fixtures/figures"
    ],
    "dirs": [],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "figure-check": {
    "run_sha": "385940e6e44c968a26113faff8251f21802f10fc64d3fecfbed2011e28f66b58",
@@ -4132,9 +4121,9 @@
     "tools/pr/prepr.sh"
    ],
    "dirs": [],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "fragment-check": {
    "run_sha": "90a2ee3e4d234a1f84217fe48e0e88ef1d01dafc9a49c331c518bf0a43063d7b",
@@ -4222,9 +4211,9 @@
    "dirs": [
     ".claude/workflows"
    ],
-   "git": [],
    "index": true,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "gantt-and-verdict-audit": {
    "run_sha": "d1f9161e487c99eb5be4378579e90ac6800a56240f6f3d5a8bd71abdc277e1ae",
@@ -4236,9 +4225,9 @@
     "."
    ],
    "dirs": [],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "gantt-drift": {
    "run_sha": "166a86552d93555728edf76ea5296105cfd058e20150f8cc1dcd4d417cf9f209",
@@ -4249,9 +4238,9 @@
     "."
    ],
    "dirs": [],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "gate-predicate": {
    "run_sha": "dbd1cf4a4f40114a4869ab0943a911f0f65164587b81ebe19d3336a05aae01d7",
@@ -4272,9 +4261,9 @@
    "dirs": [
     "tools/ci"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "gate-sweep": {
    "run_sha": "14332389bd39165ea708fc743382f9b3ce8bb13b261a96f1394443e1dabbf103",
@@ -4289,9 +4278,9 @@
    "dirs": [
     "tools/ci"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "gh-call-log-shim": {
    "run_sha": "f7b00abdc16649eff7027d19450a7c15669e548a86651f6ef8562e43e4c31489",
@@ -4307,9 +4296,9 @@
     ".",
     "tests"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "gh-read-run": {
    "run_sha": "e1e5f1991f49a10657c6a31af7ad709b63607e00b2da49b7313f4c8b05cb2214",
@@ -4339,9 +4328,9 @@
     "."
    ],
    "dirs": [],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "handoff-push": {
    "run_sha": "6f2675909677bd166b3afeb42900c406946ff121e3decd3f80bb1927db92c038",
@@ -4359,6 +4348,7 @@
     "config",
     "objects",
     "refs",
+    "tests",
     "tests/env_drift.py",
     "tools",
     "tools/audit",
@@ -4368,9 +4358,9 @@
    "dirs": [
     "tools/audit/seat"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "handover-prompt": {
    "run_sha": "978bb964bf6f2b3577322b27c19093a8d35e6e9ed1da21d05f37a4dd47b0644f",
@@ -4407,6 +4397,7 @@
    "files": [
     "tests/throwaway_git.sh",
     "tools/audit/seat/heartbeat.sh",
+    "tools/audit/seat/pr_args.sh",
     "tools/audit/seat/ref_privacy.py"
    ],
    "probes": [
@@ -4415,14 +4406,15 @@
     "objects",
     "packed-refs",
     "refs",
+    "tests",
     "tools",
     "tools/audit",
     "tools/audit/seat"
    ],
    "dirs": [],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "hooks-setup": {
    "run_sha": "9f46638b450f0c1c11914f0ab66e131f73054dd3ce75d039a317d7657bb4a921",
@@ -4569,9 +4561,9 @@
    "dirs": [
     "tests"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "ledger-mutation-harness": {
    "run_sha": "0638a2c8c16dd37e4ee44287fd87c16b49ab5cf7999594462d4e205c0b71558d",
@@ -4592,9 +4584,9 @@
     "tools/audit/seat"
    ],
    "dirs": [],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "local-alert-lister": {
    "run_sha": "310e0c54c961574777d44e6d821ca44ee2415edd85fdb4ba2baa5653bf7b55ca",
@@ -4610,9 +4602,9 @@
    "dirs": [
     "tools/ci"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "machinery-ratchet": {
    "run_sha": "27ea83021c2a8528abd0f1b88a9ebdb9dfa7346b4a8ca0609d11f72e80f2888d",
@@ -4629,9 +4621,9 @@
    "dirs": [
     "tests"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "mandate-guard-mutation-harness": {
    "run_sha": "27411fc800ebfa05d4598e2d1740983a5e83e1f46a2a31148907b16d01d310a6",
@@ -4647,9 +4639,9 @@
     "tools/audit/seat"
    ],
    "dirs": [],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "merge-fast-path": {
    "run_sha": "6fc9020ca7715276e8de746b245c014d20a362b7392d89a8b8b4051850beafb2",
@@ -4679,9 +4671,9 @@
     "tests",
     "tools/audit"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "merge-main-bot": {
    "run_sha": "f78803bb77a7d5e82fc4e2272d206f64c6e029e0003fbbee5defebfcb90f295a",
@@ -4694,6 +4686,7 @@
     "tools/policy/brief_lint.mjs",
     "tools/policy/counts.mjs",
     "tools/policy/dependabot_contract.mjs",
+    "tools/policy/legacy_control_files.json",
     "tools/policy/policy_lint.mjs",
     "tools/policy/render_md.mjs",
     "tools/policy/vendor/markdown-it.min.js",
@@ -4716,13 +4709,14 @@
     "tests",
     "tools/pr"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "merge-train": {
    "run_sha": "f79ca10ea5b68ac69e0666ca998dae7e3a7a0d3f7c9f1b9bfe1a52f010667c36",
    "files": [
+    ".gitattributes",
     ".github/workflows/ci.yml",
     ".github/workflows/nightly.yml",
     "dev/audit/rounds/round6/D11/fix/codeowners_gap.py",
@@ -4737,7 +4731,9 @@
     "tools/audit/merge_fastpath.py",
     "tools/audit/seat/gh_read.py",
     "tools/audit/seat/ledger.py",
+    "tools/audit/seat/merge_pr.sh",
     "tools/audit/seat/merge_train.py",
+    "tools/audit/seat/orchestrator_tick.py",
     "tools/audit/seat/pr_args.sh",
     "tools/audit/seat/proof_watch.py",
     "tools/audit/seat/queue_pre_flight.py",
@@ -4763,13 +4759,13 @@
     "tools/ci",
     "tools/release"
    ],
+   "index": false,
+   "objects": true,
    "git": [
     "diff",
     "ls-tree",
     "show"
-   ],
-   "index": false,
-   "objects": true
+   ]
   },
   "moved-path-reader": {
    "run_sha": "5375b0fa5ad187f70df1285f4fc746f92b11055f02ad8c6d4361a43ec0781392",
@@ -4787,9 +4783,9 @@
    "dirs": [
     "tests"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "mutant-driver": {
    "run_sha": "8a12b8665684a89b1d235783bfcda1ebb1ccafa0299a5b924e594cc3ed18e62b",
@@ -4844,9 +4840,9 @@
     "tests",
     "tools/audit/seat"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "offline-spy": {
    "run_sha": "a51b4727e58f96a4e0a1789ef50339ed073e735eea6652a342706135df2012ba",
@@ -4859,14 +4855,15 @@
     "config",
     "objects",
     "refs",
+    "tests",
     "tools",
     "tools/audit",
     "tools/audit/seat"
    ],
    "dirs": [],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "open-driver": {
    "run_sha": "a40d900542b0c730d047b4001cadd56bed0c7c18e86c0ec66e9065f0f75f5f64",
@@ -4895,9 +4892,9 @@
     "tests",
     "tools/audit/seat"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "open-pr": {
    "run_sha": "2e72b01d52ab1335bcc6a6db4394748eb22981395369e23d9d38c81e856bc2a4",
@@ -5093,11 +5090,14 @@
    ],
    "probes": [
     "-",
+    "-c",
     ".",
     "config",
+    "dev/programme/delivery/5.md",
     "objects",
     "packed-refs",
     "refs",
+    "tests",
     "tests/env_drift.py",
     "tools",
     "tools/.gitattributes",
@@ -5176,11 +5176,11 @@
     "tools/audit/seat",
     "tools/ci"
    ],
+   "index": false,
+   "objects": true,
    "git": [
     "merge-base"
-   ],
-   "index": false,
-   "objects": true
+   ]
   },
   "outside-intake": {
    "run_sha": "b1886dcd342b9193dbbf0aaac201f4682a3d288dae24feb1275aaba678eecf4d",
@@ -5205,9 +5205,9 @@
     "tools/audit",
     "tools/audit/seat"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "owed-line-reader": {
    "run_sha": "188ebdb9f5731a219d6cc2d96a08494415aeb1b5d68c579f1c25d4c697992e2d",
@@ -5218,9 +5218,9 @@
     "."
    ],
    "dirs": [],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "p3-move-ledger-and": {
    "run_sha": "e7e5dd164671c2df456aec3377e7e82b9a039b6acef2d838ba2325504fb28eee",
@@ -5238,9 +5238,9 @@
    "dirs": [
     "tests"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "pin-rule": {
    "run_sha": "b6dfcf435a5771251bbbd2085b46d16057ce68105bf3fc4e891aefb63dd9dcde",
@@ -5265,9 +5265,9 @@
    "dirs": [
     "tests"
    ],
-   "git": [],
    "index": true,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "plan-page": {
    "run_sha": "87be7bdeb72cf26e61fa3d08fdbf093158083de1b44904cad7a2b2f150cf5736",
@@ -5330,9 +5330,9 @@
     "tools/audit",
     "tools/audit/seat"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "plan-table": {
    "run_sha": "2d928df151f580316fcbf48a195ec5c1d6b9dd3aefdaa7ba1a8334e19f930565",
@@ -5349,9 +5349,9 @@
    "dirs": [
     "tools/audit/seat"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "policy-lint-mutants": {
    "run_sha": "3e1b10dc363352e2251bc6cdc07107e2356a527ac64ad9c790f61a2c37015d9f",
@@ -5466,6 +5466,7 @@
     "tools/policy/fixtures/required-contexts.json",
     "tools/policy/fragments_sync.mjs",
     "tools/policy/friction_issues.mjs",
+    "tools/policy/legacy_control_files.json",
     "tools/policy/policy_lint.mjs",
     "tools/policy/policy_lint_envmatrix.mjs",
     "tools/policy/policy_lint_mutants.mjs",
@@ -6288,11 +6289,14 @@
    ],
    "probes": [
     "-",
+    "-c",
     ".",
     "config",
+    "dev/programme/delivery/5.md",
     "objects",
     "packed-refs",
     "refs",
+    "tests",
     "tests/env_drift.py",
     "tools",
     "tools/.gitattributes",
@@ -6333,6 +6337,7 @@
     "tools/audit/seat/gh_read.py",
     "tools/audit/seat/merge_pr.sh",
     "tools/audit/seat/merge_train.py",
+    "tools/audit/seat/pr_args.sh",
     "tools/policy/budget_raise_gate.py"
    ],
    "probes": [
@@ -6355,9 +6360,9 @@
     "tools/audit/seat",
     "tools/policy"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "prepr": {
    "run_sha": "81b5b27a77597fc4f4cc0ef7df3f26ae0c869c3a9ef9ae7a0b76c3db2b8af521",
@@ -6437,6 +6442,7 @@
     "tools/policy/fixtures/policy-rot/prepr/wrong-head.md",
     "tools/policy/fixtures/red-ancestry/**",
     "tools/policy/fixtures/required-contexts.json",
+    "tools/policy/legacy_control_files.json",
     "tools/policy/policy_lint.mjs",
     "tools/policy/render_md.mjs",
     "tools/policy/role_pack.py",
@@ -6984,6 +6990,7 @@
     "tests/mutation_ledger/killed_by/draw_range.py",
     "tests/mutation_ledger/killed_by/drift.py",
     "tests/mutation_ledger/killed_by/driving_grade.py",
+    "tests/mutation_ledger/killed_by/duty_legs.py",
     "tests/mutation_ledger/killed_by/duty_switch.py",
     "tests/mutation_ledger/killed_by/early_cutoff.py",
     "tests/mutation_ledger/killed_by/entity.py",
@@ -7035,6 +7042,7 @@
     "tests/mutation_ledger/killed_by/slot_drivers.py",
     "tests/mutation_ledger/killed_by/snapshots.py",
     "tests/mutation_ledger/killed_by/store.py",
+    "tests/mutation_ledger/killed_by/supply_hold.py",
     "tests/mutation_ledger/killed_by/switch.py",
     "tests/mutation_ledger/killed_by/sysid.py",
     "tests/mutation_ledger/killed_by/tariff.py",
@@ -7169,9 +7177,9 @@
     "tests",
     "tools/audit/seat"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "programme-pulse": {
    "run_sha": "9727fc2f45263c9c62fb3d38e423f05fc851d3f7df647baa2ae57be613cfc41f",
@@ -7219,9 +7227,9 @@
     "tools/audit/seat",
     "tools/ci"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "push-names-the-host": {
    "run_sha": "a492e10b008367971423622e5d3d5f84f6c9302f39c7a7504905ba3080bae85d",
@@ -7296,6 +7304,7 @@
    "index": false,
    "objects": true,
    "git": [
+    "?",
     "diff",
     "merge-base",
     "show"
@@ -7320,6 +7329,7 @@
     "tools/policy/fixtures/policy-rot/prepr/good.md",
     "tools/policy/fixtures/policy-rot/prepr/no-figures.md",
     "tools/policy/fixtures/policy-rot/prepr/wrong-head.md",
+    "tools/policy/legacy_control_files.json",
     "tools/policy/policy_lint.mjs",
     "tools/policy/render_md.mjs",
     "tools/policy/vendor/markdown-it.min.js",
@@ -7332,6 +7342,7 @@
     "objects",
     "package.json",
     "refs",
+    "tests",
     "tools",
     "tools/audit",
     "tools/audit/seat",
@@ -7346,12 +7357,12 @@
    "dirs": [
     "dev/governance/dimensions"
    ],
+   "index": true,
+   "objects": true,
    "git": [
     "merge-base",
     "show"
-   ],
-   "index": true,
-   "objects": true
+   ]
   },
   "record-predicate-sweep": {
    "run_sha": "f092f3910b4b4b6c698000cd683d2c7a0843a4a3788bfa108ae63f5b6f81d705",
@@ -7365,9 +7376,9 @@
     "tools/policy/record-predicate"
    ],
    "dirs": [],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "record-row-generator": {
    "run_sha": "9a9a4ca26cb18dee16f8e861a3fc734dbb6ea002a7db16b4316b99ecbad449ec",
@@ -7389,6 +7400,7 @@
     "tools/policy/brief_lint.mjs",
     "tools/policy/counts.mjs",
     "tools/policy/dependabot_contract.mjs",
+    "tools/policy/legacy_control_files.json",
     "tools/policy/policy_lint.mjs",
     "tools/policy/render_md.mjs",
     "tools/policy/vendor/markdown-it.min.js",
@@ -7419,11 +7431,11 @@
     "tools/audit/seat",
     "tools/release"
    ],
+   "index": true,
+   "objects": true,
    "git": [
     "diff"
-   ],
-   "index": true,
-   "objects": true
+   ]
   },
   "ref-pruner": {
    "run_sha": "e9a4011f002b3591593de2307fd743aa0477052bc058be6cff2970467a11f0b9",
@@ -7447,9 +7459,9 @@
     "tests",
     "tools/audit/seat"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "resume-renderer": {
    "run_sha": "78b863f6f1c6616877dd271c57f41953f997c677d1c4c4adfd177ccb35892f75",
@@ -7466,9 +7478,9 @@
    "dirs": [
     "tools/audit/seat"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "review-carry": {
    "run_sha": "02aaf8bcf11f88f6d26667091882c9f79e22ecdc327f914b0686f1d3f81f657d",
@@ -7490,9 +7502,9 @@
    "dirs": [
     "tests"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "review-packet": {
    "run_sha": "5cd83d880b60b227f269115fd2e37e970b8eb1970bd7639d87faf881775b4155",
@@ -7520,6 +7532,7 @@
     "tools/policy/counts.mjs",
     "tools/policy/dependabot_contract.mjs",
     "tools/policy/fixtures/required-contexts.json",
+    "tools/policy/legacy_control_files.json",
     "tools/policy/policy_lint.mjs",
     "tools/policy/render_md.mjs",
     "tools/policy/vendor/markdown-it.min.js"
@@ -7578,9 +7591,9 @@
    "dirs": [
     "tests"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "roster-editor": {
    "run_sha": "69d134ca93555d9ce85205a52a5eb7ef397b6bf559866955924dc0fee3152065",
@@ -7605,9 +7618,9 @@
     "tools/audit",
     "tools/audit/seat"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "roster-library": {
    "run_sha": "ef4cbcbdebfe734c9270dab5c152611820d5f1abdb65bb51f459535bf08e8287",
@@ -7625,9 +7638,9 @@
    "dirs": [
     "tests"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "roster-ops-mutation-harness": {
    "run_sha": "ff64ecaef9c502f634ec498485bc646c76e67e625d81961b0ab116701e85812d",
@@ -7647,9 +7660,9 @@
     "tools/audit/seat"
    ],
    "dirs": [],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "roster-queue-runner": {
    "run_sha": "d5cd705b4d2a5ded00be29cdd0c36a43a31afc42011bdb9205b6cf665468041f",
@@ -7712,9 +7725,9 @@
     "tools/audit",
     "tools/audit/seat"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "round-closeout": {
    "run_sha": "e63320b15f7e6afe184cddd447296bdc858f072014643de2b7db1af60929a6da",
@@ -7745,9 +7758,9 @@
     "tools/audit",
     "tools/audit/seat"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "ruleset-cut-over-instrument": {
    "run_sha": "8eade8ef98320d326fd120c27f5825f3096030e499f8d8be5f51a2f9a91e073e",
@@ -7766,9 +7779,9 @@
    "dirs": [
     "tools/ci"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "scorecard": {
    "run_sha": "3215c0b1f85e68b18dde7d804fdeca68363603e0bf8bb708323038e2801941ac",
@@ -7795,6 +7808,7 @@
     "tests/requirements-typing.txt",
     "tests/typing_budgets.json",
     "tools/audit/seat/cloud-setup.sh",
+    "tools/audit/seat/pr_args.sh",
     "tools/audit/seat/seat_venv.sh",
     "tools/audit/seat/shims/**"
    ],
@@ -7802,9 +7816,9 @@
    "dirs": [
     "."
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "self-tests-outside-seat": {
    "run_sha": "f74f563517915a57fe460412e738e310a7b60174f1d47ff211e4ed8e856a3c3b",
@@ -7920,6 +7934,7 @@
     "tools/policy/fixtures/required-contexts.json",
     "tools/policy/fragments_sync.mjs",
     "tools/policy/friction_issues.mjs",
+    "tools/policy/legacy_control_files.json",
     "tools/policy/policy_lint.mjs",
     "tools/policy/policy_lint_envmatrix.mjs",
     "tools/policy/policy_lint_mutants.mjs",
@@ -8293,9 +8308,9 @@
     "tools/release"
    ],
    "dirs": [],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "state-doc-writer": {
    "run_sha": "78e714c49c75381ec173e957096d960d7899d651c3167a99cbf70097d17ee208",
@@ -8359,9 +8374,9 @@
    "dirs": [
     "tools/pr"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "survivor-list": {
    "run_sha": "644c9178e34209c89b429f7eaa62936c767c0dae6fe9fb2401b395a3c883baed",
@@ -8403,9 +8418,9 @@
     "tools/audit/seat",
     "tools/ci"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "sweep-template": {
    "run_sha": "1d49f84bb509400c39fadeae7a53e0c6b2f3c504729c313b927bdc034000604c",
@@ -8439,9 +8454,9 @@
    "dirs": [
     "tools/audit/seat"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "temp-or-machine-path": {
    "run_sha": "5de9df182b392af5fbf8cfe28d3fb7d5c980b09492dc638523bde313ec1770fb",
@@ -8504,6 +8519,7 @@
     "tests/mutation_ledger/killed_by/draw_range.py/.gitattributes",
     "tests/mutation_ledger/killed_by/drift.py/.gitattributes",
     "tests/mutation_ledger/killed_by/driving_grade.py/.gitattributes",
+    "tests/mutation_ledger/killed_by/duty_legs.py/.gitattributes",
     "tests/mutation_ledger/killed_by/duty_switch.py/.gitattributes",
     "tests/mutation_ledger/killed_by/early_cutoff.py/.gitattributes",
     "tests/mutation_ledger/killed_by/entity.py/.gitattributes",
@@ -8555,6 +8571,7 @@
     "tests/mutation_ledger/killed_by/slot_drivers.py/.gitattributes",
     "tests/mutation_ledger/killed_by/snapshots.py/.gitattributes",
     "tests/mutation_ledger/killed_by/store.py/.gitattributes",
+    "tests/mutation_ledger/killed_by/supply_hold.py/.gitattributes",
     "tests/mutation_ledger/killed_by/switch.py/.gitattributes",
     "tests/mutation_ledger/killed_by/sysid.py/.gitattributes",
     "tests/mutation_ledger/killed_by/tariff.py/.gitattributes",
@@ -8659,221 +8676,12 @@
     "tests/throwaway_git.sh"
    ],
    "probes": [
+    "tools/audit/round4/**"
+   ],
+   "dirs": [
     ".",
-    ".claude/.gitattributes",
-    ".claude/hooks/.gitattributes",
-    ".claude/rules/.gitattributes",
-    ".claude/skills/.gitattributes",
-    ".claude/skills/steward/.gitattributes",
-    ".claude/workflows/.gitattributes",
-    "config",
-    "dev/.gitattributes",
-    "dev/audit/.gitattributes",
-    "dev/audit/harnesses/.gitattributes",
-    "dev/audit/harnesses/ci-version-edit/.gitattributes",
-    "dev/audit/harnesses/r10_ci_layout_p1/.gitattributes",
-    "dev/audit/harnesses/r10_ci_layout_p2_u1u2u7/.gitattributes",
-    "dev/audit/harnesses/r10_ci_layout_u0c/.gitattributes",
-    "dev/audit/harnesses/r10_ci_layout_u10/.gitattributes",
-    "dev/audit/harnesses/r10_ci_layout_u11/.gitattributes",
-    "dev/audit/harnesses/r10_ci_layout_u3/.gitattributes",
-    "dev/audit/harnesses/r10_ci_layout_u4/.gitattributes",
-    "dev/audit/harnesses/r10_ci_layout_u5/.gitattributes",
-    "dev/audit/harnesses/r10_ci_layout_u6/.gitattributes",
-    "dev/audit/harnesses/r10_ci_layout_u8/.gitattributes",
-    "dev/audit/harnesses/r10_ci_slim/.gitattributes",
-    "dev/audit/harnesses/r10_gate_stale_jobs/.gitattributes",
-    "dev/audit/harnesses/r10_hotfix_ci_critpath_3/.gitattributes",
-    "dev/audit/harnesses/r10_hotfix_ci_critpath_4/.gitattributes",
-    "dev/audit/harnesses/r10_mutant_skip/.gitattributes",
-    "dev/audit/harnesses/r10_rca_ci_critpath_3/.gitattributes",
-    "objects",
-    "refs",
-    "tests",
-    "tests/.gitattributes",
-    "tests/fixtures/.gitattributes",
-    "tests/golden/.gitattributes",
-    "tests/hastub/.gitattributes",
-    "tests/hastub/homeassistant/.gitattributes",
-    "tests/hastub/homeassistant/components/.gitattributes",
-    "tests/hastub/homeassistant/components/recorder/.gitattributes",
-    "tests/hastub/homeassistant/helpers/.gitattributes",
-    "tests/hastub/homeassistant/util/.gitattributes",
-    "tests/mutation_ledger/.gitattributes",
-    "tests/mutation_ledger/killed_by/.gitattributes",
-    "tests/mutation_ledger/killed_by/__init__.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/accuracy.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/away.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/batchmath.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/battery.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/binary_sensor.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/boost.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/button.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/climate.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/comfort_band.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/comfort_learning.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/config_flow.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/const.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/coordinator.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/currency.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/curve_learning.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/datetime.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/debugger.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/defrost.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/device_prefill.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/dhw_draws.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/dhw_learning.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/dhw_planner.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/dhw_schedule.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/diagnosis.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/diagnostics.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/disinfection.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/draw_range.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/drift.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/driving_grade.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/duty_switch.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/early_cutoff.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/entity.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/entry_config.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/external_heat.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/flow_lift.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/flow_meter.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/freq_control.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/frontend.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/grid_fee.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/heat_curve.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/heat_energy.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/inputs.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/issues.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/learner_progress.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/ledger.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/legionella.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/log_latch.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/manual_plan.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/mixing_valve.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/modbus_prefill.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/name_match.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/narrative.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/notifier.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/off_restore.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/open_meteo.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/optimizer.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/plan_slots.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/plan_step.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/power_guard.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/prefill_offer.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/presets.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/price_model.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/price_tiles.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/process_worker.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/pump_arbiter.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/pump_mode.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/pump_schedule.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/pump_signals.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/pv.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/quick_setup.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/quiet_windows.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/repairs.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/replay_doc.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/sensor.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/services.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/setpoint_check.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/silent_mode.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/slot_drivers.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/snapshots.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/store.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/switch.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/sysid.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/tariff.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/thermal_model.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/topology.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/wear.py/.gitattributes",
-    "tests/mutation_ledger/killed_by/wood_fuel.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/accuracy.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/away.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/battery.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/binary_sensor.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/boost.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/config_flow.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/coordinator.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/debugger.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/dhw_planner.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/dhw_schedule.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/draw_range.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/drift.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/duty_switch.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/early_cutoff.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/entry_config.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/heat_curve.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/heat_energy.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/inputs.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/ledger.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/manual_plan.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/notifier.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/off_restore.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/optimizer.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/payload.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/pump_arbiter.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/pump_mode.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/quiet_windows.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/repairs.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/sensor.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/slot_drivers.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/store.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/sysid.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/tariff.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/thermal_model.py/.gitattributes",
-    "tests/mutation_ledger/survivor_triage/wood_fuel.py/.gitattributes",
-    "tests/pwlane/.gitattributes",
-    "tests/replay/.gitattributes",
-    "tools/.gitattributes",
-    "tools/audit/.gitattributes",
-    "tools/audit/archscore/.gitattributes",
-    "tools/audit/archscore/calibration/.gitattributes",
-    "tools/audit/archscore/metrics/.gitattributes",
-    "tools/audit/archscore/planted/.gitattributes",
-    "tools/audit/archscore/planted/perturb/.gitattributes",
-    "tools/audit/archscore/planted/redteam/.gitattributes",
-    "tools/audit/round4/**",
-    "tools/audit/seat/.gitattributes",
-    "tools/audit/seat/beatd_shims/.gitattributes",
-    "tools/audit/seat/fixtures/.gitattributes",
-    "tools/audit/seat/fixtures/beat_jobs/.gitattributes",
-    "tools/audit/seat/fixtures/ci_critpath/.gitattributes",
-    "tools/audit/seat/hooks/.gitattributes",
-    "tools/audit/seat/instruments/.gitattributes",
-    "tools/audit/seat/shims/.gitattributes",
-    "tools/ci/.gitattributes",
-    "tools/ci/fixtures/.gitattributes",
-    "tools/ci/fixtures/ruleset/.gitattributes",
-    "tools/coverage/.gitattributes",
-    "tools/devices/.gitattributes",
-    "tools/merge/.gitattributes",
-    "tools/plan/.gitattributes",
-    "tools/policy/.gitattributes",
-    "tools/policy/fixtures/.gitattributes",
-    "tools/policy/fixtures/figures/.gitattributes",
-    "tools/policy/fixtures/policy-loop/.gitattributes",
-    "tools/policy/fixtures/policy-rot/.gitattributes",
-    "tools/policy/fixtures/policy-rot/hooks/.gitattributes",
-    "tools/policy/fixtures/policy-rot/prepr/.gitattributes",
-    "tools/policy/fixtures/policy-rot/prepr/raise/.gitattributes",
-    "tools/policy/fixtures/policy-rot/prepr/raise/recorded/.gitattributes",
-    "tools/policy/fixtures/policy-rot/prepr/upstream/.gitattributes",
-    "tools/policy/fixtures/red-ancestry/.gitattributes",
-    "tools/policy/fixtures/red-ancestry/bare/.gitattributes",
-    "tools/policy/fixtures/red-ancestry/green/.gitattributes",
-    "tools/policy/fixtures/red-ancestry/red/.gitattributes",
-    "tools/policy/fixtures/roster-probe/.gitattributes",
-    "tools/policy/record-predicate/.gitattributes",
-    "tools/policy/vendor/.gitattributes",
-    "tools/pr/.gitattributes",
-    "tools/release/.gitattributes",
-    "tools/replay/.gitattributes",
-    "tools/site/.gitattributes"
+    "tests"
    ],
-   "dirs": [],
    "index": false,
    "objects": true,
    "git": [
@@ -8885,6 +8693,8 @@
    "files": [
     "tests/throwaway_git.sh",
     "tools/audit/seat/heartbeat.sh",
+    "tools/audit/seat/offline_spy.py",
+    "tools/audit/seat/pr_args.sh",
     "tools/audit/seat/ref_privacy.py",
     "tools/audit/seat/tick_loop.sh"
    ],
@@ -8894,6 +8704,7 @@
     "config",
     "objects",
     "refs",
+    "tests",
     "tools",
     "tools/.git",
     "tools/HEAD",
@@ -8922,9 +8733,9 @@
     "."
    ],
    "dirs": [],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "train-launcher": {
    "run_sha": "355bdc1a9838e18c3149643e9127300c16aec234aa95e15e88d57bb5da836aeb",
@@ -8946,9 +8757,9 @@
     "tools/audit/seat/HEAD"
    ],
    "dirs": [],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "twin-run-reader": {
    "run_sha": "05d5e8a0774d34d43a926f9e8f18f1f73669f536617125148a2486baaf87907b",
@@ -8959,9 +8770,9 @@
     "."
    ],
    "dirs": [],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "update-pr": {
    "run_sha": "dfbf8038803e4743ee467e3e656bf0f20c07675e47ed36302f4cef35a276b277",
@@ -9157,11 +8968,14 @@
    ],
    "probes": [
     "-",
+    "-c",
     ".",
     "config",
+    "dev/programme/delivery/5.md",
     "objects",
     "packed-refs",
     "refs",
+    "tests",
     "tests/env_drift.py",
     "tools",
     "tools/.gitattributes",
@@ -9250,6 +9064,7 @@
     "tools/policy/counts.mjs",
     "tools/policy/dependabot_contract.mjs",
     "tools/policy/fixtures/required-contexts.json",
+    "tools/policy/legacy_control_files.json",
     "tools/policy/policy_lint.mjs",
     "tools/policy/render_md.mjs",
     "tools/policy/vendor/markdown-it.min.js",
diff --git a/tools/ci/selftest_scope.py b/tools/ci/selftest_scope.py
index 124ce4bbd2..fa822a99d0 100644
--- a/tools/ci/selftest_scope.py
+++ b/tools/ci/selftest_scope.py
@@ -46,9 +46,13 @@ THE DRIFT CHECK, `check`, runs on every push to main over the traces that
 run took: it fails naming every step whose committed entry misses a file,
 probe, directory or flag the run measured, and every gated step with no
 entry. Over-approximation (an entry naming a file no longer read) is safe
-and is reported, not refused. `--write` saves the run's own measurement,
-which main uploads as the `selftest-closures` artifact: commit that file, or
-re-record with `record` (Linux, strace).
+and is reported, not refused. `--write` saves the table to commit, which
+main uploads as the `selftest-closures` artifact: the committed table unioned
+with this run's measurement, per step (lists unioned, flags OR'd, run_sha the
+run's; `union_entries`), because one run measures one environment and a read
+only another measured (a seat's Linux `record`: objects, index) is not stale
+for this run missing it. Commit that file, or re-record with `record` (Linux,
+strace) and union the same way.
 THE SETTLED INDEX, `settle`, runs untraced before any step is (CI's strace
 step; `record` itself): a fresh checkout leaves racily clean index entries,
 whose content the first index-refreshing git command re-reads, so without it
@@ -623,8 +627,12 @@ def drift(table: dict | None, measured: dict[str, dict], steps: list[Step]) -> t
         probes = set(e.get("probes", ()))
         misses = {
             "files": [f for f in m["files"] if not covers(have, f)],
+            # A probe under a directory the run listed is answered by that
+            # directory: excused here, refused once as a `dirs` miss when the
+            # table lacks it. So a measurement `write_table` compacted (the
+            # artifact) and the live one refuse the same lines.
             "probes": [p for p in m["probes"] if not covers(probes, p)
-                       and not any(a in dirs for a in _ancestors(p))],
+                       and not any(a in dirs or a in set(m["dirs"]) for a in _ancestors(p))],
             "dirs": sorted(set(m["dirs"]) - dirs)}
         refuse += [_under_scoped(sid, k, sorted(v)) for k, v in misses.items() if v]
         gone = {"files": [f for f in have if f not in set(m["files"]) and not (
@@ -784,13 +792,29 @@ def write_table(out: Path, entries: dict[str, dict], root: Path = ROOT) -> None:
                                "steps": dict(sorted(entries.items()))}, indent=1) + "\n")
 
 
+def union_entries(table: dict | None, measured: dict[str, dict]) -> dict[str, dict]:
+    """Each measured step's entry unioned with the committed one: files,
+    probes, dirs and git markers unioned, index and objects OR'd, run_sha the measurement's.
+    A step the run did not measure keeps no entry (the measurement names every
+    gated step, else drift refuses UNMEASURED)."""
+    old = (table or {}).get("steps", {})
+    out = {}
+    for sid, m in measured.items():
+        e = old.get(sid, {})
+        out[sid] = {**m, "run_sha": m["run_sha"],
+                    **{k: sorted(set(e.get(k, ())) | set(m.get(k, ()))) for k in ("files", "probes", "dirs", "git")},
+                    **{k: bool(e.get(k) or m.get(k)) for k in ("index", "objects")}}
+    return out
+
+
 def check_cli(trace_dir: Path, write: Path | None = None, root: Path = ROOT) -> int:
     steps = workflow_steps(root)
     gaps = wiring_gaps(steps)
     measured, broken = fold(trace_dir, steps, root)
+    table = load_table(root / TABLE)
     if write is not None:
-        write_table(write, measured, root)  # this run's measurement, to commit as the table
-    refuse, notes = drift(load_table(root / TABLE), measured, steps)
+        write_table(write, union_entries(table, measured), root)  # the table to commit
+    refuse, notes = drift(table, measured, steps)
     refuse = broken + refuse
     for line in gaps + refuse:
         print(f"  {line}")
@@ -1095,6 +1119,35 @@ def self_test(wrapper: Path = ROOT / WRAPPER, workflow: Path = ROOT / WORKFLOW)
         ck("drift: a step this run did not trace is refused",
            drift(full_table, {k: v for k, v in measured.items() if k != "slow"}, st2)[0]
            == ["UNMEASURED step slow: this run left no trace of it"])
+        # The artifact `check --write` uploads is a compacted measurement: a
+        # probe under a directory the run listed is dropped. Drift over it and
+        # over the live measurement must refuse the same lines (the 33 against
+        # 34 gap of #3557's review).
+        dm = json.loads(json.dumps(measured))
+        dm["a"]["dirs"] += ["docs"]
+        dm["a"]["probes"] += ["docs/new.md"]
+        compacted = json.loads(json.dumps(dm))
+        compacted["a"]["probes"] = compact_probes(set(dm["a"]["probes"]), set(dm["a"]["dirs"]), set())
+        ck("drift: a probe under a directory the run listed is refused once, as the dirs miss, "
+           "live and compacted alike (null control: the compaction dropped it)",
+           "docs/new.md" not in compacted["a"]["probes"]
+           and drift(full_table, dm, st2)[0] == drift(full_table, compacted, st2)[0]
+           == ["UNDER-SCOPED step a: dirs misses ['docs']"])
+        # `check --write`'s table is the union: a planted committed read this
+        # run did not measure survives, and the run's own reads are added.
+        planted = json.loads(json.dumps(full_table))
+        planted["steps"]["b"].update(objects=True, files=["tools/x/only-elsewhere.py"],
+                                     probes=["tools/x/p.json"], git=["merge-base"])
+        planted["steps"]["gone"] = entry(st2[4], files=["x"])
+        planted["steps"]["a"]["run_sha"] = "old"
+        un = union_entries(planted, measured)
+        ck("union_entries keeps a committed read and flag the run did not measure, adds the run's, "
+           "takes the run's run_sha and drops an entry no step measured",
+           sorted(un) == ["a", "b", "slow"] and un["b"]["objects"] is True
+           and un["b"]["files"] == ["tools/x/only-elsewhere.py"] and un["b"]["git"] == ["merge-base"]
+           and un["b"]["probes"] == ["tools/x/p.json"] and un["a"]["index"] is True
+           and un["a"]["files"] == measured["a"]["files"] and un["a"]["run_sha"] == measured["a"]["run_sha"]
+           and drift({"steps": un}, measured, st2)[0] == [])
 
     # The edges a seat's run reaches but the cases above do not.
     ck("a duplicated step id is named", "DUPLICATE id a" in wiring_gaps(
@@ -1328,6 +1381,20 @@ def self_test(wrapper: Path = ROOT / WRAPPER, workflow: Path = ROOT / WORKFLOW)
         ck("check: a table naming every read passes, and --write saves the measurement",
            rc_ok == 0 and "2 gated step(s), 0 refusal(s)" in out.getvalue()
            and (load_table(root / "m.json") or {}).get("steps", {}).get("a", {}).get("files") == ["tools/x/a.py"])
+        # --write writes the committed table unioned with the run: a planted
+        # committed read and flag this run did not measure survive the write.
+        was_table = (root / TABLE).read_text()
+        pt = json.loads(was_table)
+        pt["steps"]["slow"].update(objects=True, probes=["tools/x/planted.json"])
+        (root / TABLE).write_text(json.dumps(pt))
+        with contextlib.redirect_stdout(io.StringIO()):
+            main(["check", "--traces", str(tdir), "--write", str(root / "u.json")], root)
+        (root / TABLE).write_text(was_table)
+        us = (load_table(root / "u.json") or {}).get("steps", {})
+        ck("check --write: a planted committed read and flag the run did not measure survive the write",
+           us.get("slow", {}).get("objects") is True
+           and us.get("slow", {}).get("probes") == ["tools/x/planted.json"]
+           and us.get("a", {}).get("files") == ["tools/x/a.py"])
         (tdir / "step-slow.trace").write_text(whole(
             f'5 openat(AT_FDCWD<{root}>, "docs/d.md", O_RDONLY) = 3<{root}/docs/d.md>'))
         out = io.StringIO()
diff --git a/tools/ci/selftest_scope_mutants.sh b/tools/ci/selftest_scope_mutants.sh
index 7d2ff3123d..45fa19ff72 100644
--- a/tools/ci/selftest_scope_mutants.sh
+++ b/tools/ci/selftest_scope_mutants.sh
@@ -49,6 +49,10 @@ scope_mutant "settle never rewrites the index" '["git", "update-index", "-q", "-
 scope_mutant "the settle command a no-op" 'return settle_index(root)' 'return 0'
 scope_mutant "settle_gaps reads no job" 'if any(s.id in UNGATED and SETTLE_CALL.search' 'if True or any(s.id in UNGATED and SETTLE_CALL.search'
 scope_mutant "static skips the settle check" 'problems = wiring_gaps(steps) + settle_gaps(steps)' 'problems = wiring_gaps(steps)'
+scope_mutant "check --write writes the bare measurement" 'write_table(write, union_entries(table, measured), root)' 'write_table(write, measured, root)'
+scope_mutant "the union drops a committed list entry" 'sorted(set(e.get(k, ())) | set(m.get(k, ())))' 'sorted(set(m.get(k, ())))'
+scope_mutant "the union drops a committed flag" 'bool(e.get(k) or m.get(k))' 'bool(m.get(k))'
+scope_mutant "drift refuses a probe the run's own listed dir answers" 'a in dirs or a in set(m["dirs"])' 'a in dirs'
 workflow_mutant "CI never settles the index" 'python3 -I tools/ci/selftest_scope.py settle' 'true'
 workflow_mutant "CI swallows a failed settle" 'python3 -I tools/ci/selftest_scope.py settle' 'python3 -I tools/ci/selftest_scope.py settle || true'
 wrapper_mutant "only launch untraced (the incident's wrapper)" 'case "$UNTRACED" in *" ${GITHUB_ACTION:-} "*)' 'case " launch " in *" ${GITHUB_ACTION:-} "*)'

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
