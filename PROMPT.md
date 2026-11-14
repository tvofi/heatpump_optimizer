CLOUD REVIEWER seat for PR #3573 of tvofi/heatpump_optimizer, at head 5a11c05d816dd1dfca988dcba1ca625f74137107. Bus nonce: aa3689bb81c1890c0d69818756a112f9. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fix-review --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fix-review.md and its rules from main, and follow them exactly. Fetch the PR head with `git fetch origin 5a11c05d816dd1dfca988dcba1ca625f74137107`; the PR body is in the PR. Start from the review packet, which you render here rather than read from the dispatcher, whose copy is a path on its own machine: `python3 -I tools/audit/seat/review_packet.py render --pr 3573 --head 5a11c05d816dd1dfca988dcba1ca625f74137107 --reviewed-head 868f8a726bf29471b5f0b42b2e514b83e03cd865 --out $HOME/review-packet.md`. A refusal names its signal and the packet is still written unless the signal is `host-path`; re-read the live checks either way. This is a later round over the reviewed head 868f8a726bf29471b5f0b42b2e514b83e03cd865: its scope is the packet's `## Review scope` line, the delta and the previous verdict's findings when it reads `delta`, widened only to the exact already-reviewed code a production (custom_components/) delta puts at non-obvious risk that CI would not detect, the verdict naming path and risk; an instrument, test, policy or body delta never widens it (fix-review.md step 12). Verify each claim adversarially: mutate the fix and check the tests fail, and check every figure in the body at this head. Check that it merges with origin/main (`git merge-tree --write-tree origin/main <head>`); block on main only when that reports a conflict, never on a head that is behind main but merges cleanly (the train re-proves it on the current main). Wait for CI on this head only by re-running `python3 tools/audit/seat/merge_train.py classify 5a11c05d816dd1dfca988dcba1ca625f74137107 --pr 3573` in the background, at least 60 s between runs, until it exits 0 (GREEN), 1 (RED), 2 (unreadable: say so in the verdict) or 4 (APPROVAL-OWED: the only red is the budget raise's approval, which follows your verdict; judge the head as GREEN and quote the line); 3 is WAIT, so run it again. Never wait with `pgrep` or `pkill`, whose `-f` pattern matches the waiter's own command line, nor on a context the ruleset does not require, such as `prelude`. A review_packet `required-red` signal does not stop you while classify prints WAIT: classify decides. If your review is otherwise complete and classify still prints WAIT after about 30 minutes of polling, stop waiting: put the line `pending-ci: <the context names it printed>` straight after the `bus-nonce:` line and return the verdict as below; the relay posts it once CI is green at this head, refuses it over a red, and refuses it if the head moves. If the review is not complete then, push `Fix review: blocked 5a11c05d816dd1dfca988dcba1ca625f74137107 ci-wait: <the last classify line>` as below.
Output: in a fresh directory of your own (`W=$(mktemp -d)`), write verdict.md, whose first line is exactly `Fix review: merge 5a11c05d816dd1dfca988dcba1ca625f74137107` or `Fix review: blocked 5a11c05d816dd1dfca988dcba1ca625f74137107 <class>: <reason>` (no brackets; the class is lower-case letters and dashes), in the format the role file gives, then a blank line, then `bus-nonce: aa3689bb81c1890c0d69818756a112f9`, then the body in sections. A blocked verdict's block goes under `## Block`. Each finding this PR does not settle (a defect, a surviving mutant, a deferral, a follow-up, a task owed after the merge) is its own bullet under `## Findings` ending in its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>` (finding-propagation.md). Everything else (RESULT lines, re-runs, CI state, figures you could not re-derive) goes under `## Evidence`: tools/audit/carry_audit.py reads an item there, and under any heading of a merge verdict but `## Findings`, `## Friction`, a block heading and a note heading (Residuals, Follow-ups, Notes ...), by its shape alone: a finding only when it opens with a lead word (Residual:, Follow-up:, Out of scope: ...) or carries a `Carry:`, so a defect you hand on goes under `## Findings`, and bus.sh refuses a verdict holding a finding with no valid `Carry:`. Put the evidence files in `ev/` beside it, under 25 MB in all (cite a large log by path and keep its tail: a ~30 MB ev/ once failed its push), and make at least one file under `ev/` contain the full 40-hex head `5a11c05d816dd1dfca988dcba1ca625f74137107` (e.g. `ev/HEAD.txt` holding the head you reviewed, beside your command output): bus.sh refuses a verdict whose `ev/` names no head. Do NOT run bus.sh: its dispatch record lives on the orchestrator's machine, which publishes the verdict there (cloud_relay.sh). Return the verdict on a probe ref, and push nothing else; this builds one parentless commit with a private index and touches no branch of your checkout: `R=$(git rev-parse --show-toplevel); G=$(git rev-parse --absolute-git-dir); mkdir -p $W/pr && cp -r $W/verdict.md $W/ev $W/pr/ && cd $W/pr && T=$(GIT_DIR=$G GIT_INDEX_FILE=$W/idx GIT_WORK_TREE=$W/pr sh -c 'git add -A -f . && git write-tree') && C=$(GIT_DIR=$G git -c user.name=hpo-fixer -c user.email=70032254+tvofi@users.noreply.github.com commit-tree $T -m "verdict 3573 5a11c05d816dd1dfca988dcba1ca625f74137107") && git -C $R push -q origin $C:refs/heads/probe/rev-3573-aa3689bb`. That ref is the return signal. Do not post comments, approve or merge.
Every way your turn ends pushes a verdict to that ref: a setup or hook refusal that stops you pushes `Fix review: blocked 5a11c05d816dd1dfca988dcba1ca625f74137107 seat-refused: <the refusing line>`; never end your turn while a background poll runs. After the push, read the ref back with `git ls-remote origin refs/heads/probe/rev-3573-aa3689bb`, and push again if it does not print your commit.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# Review packet #3573
head: 5a11c05d816dd1dfca988dcba1ca625f74137107
base: 50373173d486faf394b24637c177ab38b691b394

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=132237318919 success
arch-score / arch-score id=132249147634 success
arm id=132236971714 skipped
budget-raise-gate / budget-raise-gate id=132249195095 success
cancel-superseded id=132249146983 success
codeql id=132249147506 skipped
codeql / Analyze (actions) id=132237197614 success
codeql / Analyze (javascript-typescript) id=132237197615 success
codeql / Analyze (python) id=132237197597 success
gate id=132249146249 success
governance id=132249146409 skipped
governance / delivery-status id=132237197652 success
governance / delivery-status-publish id=132237200084 skipped
governance / env-matrix id=132237197635 success
governance / instrument-self-tests id=132237197852 success
governance / policy-docs id=132237197662 success
governance / record id=132237199641 skipped
governance / wave-script id=132237197706 success
hassfest id=132249213324 skipped
hassfest / hassfest id=132237197527 success
kernel-points id=132249184867 skipped
pr-contract id=132249147674 skipped
pr-contract / pr-contract id=132248461329 success
prelude id=132249146086 success
refresh id=132249197365 success
sweep-self id=132249489648 skipped
tests id=132249202239 skipped
tests / arch-instrument id=132237509095 success
tests / briefs id=132237198077 success
tests / browser id=132237509057 success
tests / ci-ratchet id=132248407902 skipped
tests / claims-autofix id=132248406961 skipped
tests / closure-scope id=132237197854 success
tests / closures id=132237509061 success
tests / closures-autofix id=132248255107 skipped
tests / coverage id=132237509103 success
tests / coverage-ratchet id=132246101925 success
tests / fast (3.14) id=132237509051 success
tests / graders-head-copy id=132246097763 success
tests / lane-proofs id=132248405139 success
tests / mutation id=132237197833 success
tests / mutation-autofix id=132237669338 skipped
tests / mutation-pins id=132237668244 skipped
tests / nightly-ha id=132237511089 skipped
tests / nightly-status id=132237198015 success
tests / replay id=132237511141 skipped
tests / typing id=132237509065 success
validate id=132249204917 skipped
validate / validate-hacs id=132237197569 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item fc4b1f77: dismissed:not reproduced at origin/main, with the untested arms named
NOTE body item b5ad8c6e: dismissed:carried in part 1 (#3499)
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         python3 -I tools/ci/gate.py --self-test
             `tools/ci/gate.py` is in the tree at this head
  ok         python3 -I tools/ci/prelude.py --self-test
             `tools/ci/prelude.py` is in the tree at this head
  ok         tools/ci/codescan_wait.py
             `tools/ci/codescan_wait.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py
             `tools/pr/ci_predict.py` is in the tree at this head

FIGURES: 6 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: delta (later round over the reviewed head 868f8a726bf29471b5f0b42b2e514b83e03cd865)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at 868f8a726bf29471b5f0b42b2e514b83e03cd865
Fix review: blocked 868f8a726bf29471b5f0b42b2e514b83e03cd865 class-open: prelude.judging prior overlay reads a run re-running a FAILED unit job (attempt 1 failure, attempt 2 queued) as not busy, so other gates at the head stop deferring while gate() still sources only the latest listing

bus-nonce: cf063d4f4beb65016992d970d3a771f7

## Block

- Carry 7's predicate has an unguarded domain the body does not disposition. `prior_jobs` fires on any run with `run_attempt` > 1 and an owed need unfinished, and `judging()`'s `seen()` then substitutes the previous attempt's job for ANY listed prelude/unit job that is unfinished now and completed before, whatever its conclusion. A "re-run failed jobs" on a run whose `tests / mutation` failed in attempt 1 (re-queued in attempt 2, `gate` re-queued) is therefore read `judging=True`, `busy=[]`, after 1 read; at the merge base e23124ff the same run is `busy=[1]` (ev/attack-failed-rerun.txt, script ev/attack.py, built by this reviewer on the committed fixture). That run is genuinely about to add a new source, which is exactly what `busy()` exists to wait on.
- The overlay is also one-sided: `judging()` treats the pre-rerun job as the standing source ("the pre-rerun source stands until the need finishes"), but `gate()`'s source read (gate.py ~222/228/236, `r["jobs"]`, freshest completed source wins) never reads `prior`. So a gate released by the overlay judges as if the re-running run had no source for that unit: it falls to an older run's completed source (a green from a superseded run where attempt 1's failure was freshest) or to "no run at this head judged base" (red). Neither is what the docstring claims.
- The body's interpretation ("the state that makes a run busy is a re-queued need") names the fixture shape only; it states no rule separating a re-queued need of the run's own gate re-run from a deliberately re-run failed (or re-run-all) unit, and no null control covers the latter. Owed of the fixer: guard the overlay to the domain the ruling meant (e.g. only a need whose attempt-1 conclusion is success and that the re-run re-queued as a dependent of `gate`, or make gate()'s source read honour `prior` identically), with a failing check on the failed-unit re-run shape first and its null control.

## Evidence

- Round 1 of this review. Handoff review: no pull request, no review packet and no CI exists at this head, so no check runs were read and step 11 has nothing to answer; `merge_train.py owed-reds` prints `tests / mutation`, `tests / typing`, `validate / validate-hacs`, among others.
- Head measured: 868f8a726bf29471b5f0b42b2e514b83e03cd865 (ev/HEAD.txt), equal to the body's `## Head`. Merge base e23124ff6e45bac1d48b4a775dad555a37965355 = origin/main; `git merge-tree --write-tree origin/main <head>` rc=0, no conflict (ev/merge-tree.txt). Role contracts unchanged between merge base and origin/main.
- RESULT self-tests at head (ev/selftests-head.txt): gate 97 checks 0 failed; prelude 81, 0 failed; merge_train 753, 0 failed; merge_pr 28, 0 failed: every figure in `## Figures` re-derived.
- RESULT mutants (ev/mutants.txt): overlay to `False` fails gate 1 and prelude 1 named checks; dropping the attempt guard fails the single-attempt null; merge_pr posted-verdict condition to `false` fails "a verdict the bus already posted ...". Matches the body. Carry 5 and carry 9 mutants not re-run by me: not verified here.
- VERSION, manifest version, RELEASE_NOTES heading and tests/golden untouched (diff empty against the merge base). Gate scope MODE: FULL per the body, not re-run (CI's heavy run).
- Carries 5, 8, 9 read and found consistent with the body; the 11 diff-mutant survivors are the body's figure, not re-derived (no prepr.sh run).

## Delta diff: git diff 868f8a726bf29471b5f0b42b2e514b83e03cd865 5a11c05d816dd1dfca988dcba1ca625f74137107
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
index d7503a17af..c4d284756d 100644
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
index fc4b26a157..cd0e495d1c 100644
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
@@ -208,6 +211,108 @@ def _drop_off_steps(mask: np.ndarray, off: np.ndarray | None) -> np.ndarray:
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
 
@@ -1180,17 +1285,8 @@ class DhwPlanner:
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
@@ -1200,15 +1296,17 @@ class DhwPlanner:
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
@@ -1263,19 +1361,10 @@ class DhwPlanner:
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
@@ -1533,10 +1622,7 @@ class DhwPlanner:
 
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
@@ -1616,6 +1702,25 @@ class DhwPlanner:
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
@@ -1626,6 +1731,7 @@ class DhwPlanner:
         requirement: np.ndarray,
         max_temp: np.ndarray,
         forced_off: np.ndarray | None = None,
+        start_below: np.ndarray | None = None,
     ) -> np.ndarray:
         """Top up the plan until the SIMULATED trajectory meets the floor.
 
@@ -1697,6 +1803,7 @@ class DhwPlanner:
             usable = headroom > 1e-6
             if forced_off is not None:
                 usable &= ~np.asarray(forced_off[lo : b + 1], dtype=bool)
+            usable &= startable_steps(plan, temps, start_below)[lo : b + 1]
             # Degrees of room under the ceiling for heat added at each
             # candidate. The heat is stored from the candidate to the breach,
             # decaying as it leaks away, so the bound is the tightest of
@@ -1782,17 +1889,7 @@ class DhwPlanner:
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
@@ -1800,10 +1897,7 @@ class DhwPlanner:
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
diff --git a/custom_components/heatpump_optimizer/pump_arbiter.py b/custom_components/heatpump_optimizer/pump_arbiter.py
index 7ffaff4ccc..e3afe6c67d 100644
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
@@ -187,7 +189,8 @@ from .freq_control import defrost_interval, resolve_reading
 from .modbus_prefill import night_mode_write_ids, package_prefix
 from .const import finite_float
 from .inputs import (
-    InputReader, quantise_setpoint_c, read_setpoint, setpoint_range_c, state_power_kw, write_setpoint_c,
+    InputReader, SetpointGrid, quantise_setpoint_c, read_setpoint, setpoint_grid, setpoint_range_c, state_power_kw,
+    write_setpoint_c,
 )
 from .log_latch import log_held
 from .payload import REASON_LEGIONELLA, CurrentAction
@@ -198,7 +201,9 @@ from .drift import stored_instant
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
@@ -586,29 +591,17 @@ def _bounded(
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
@@ -877,7 +870,8 @@ def _flow_target(inp: ArbiterInputs, duty: str | None, now: datetime) -> float |
     2026-09-26). A step that heats writes a flow that follows the planned
     level: :data:`FLOW_HEAT_C` (or the configured ceiling, ``flow_heat_c``)
     at full power, sliding to the measured inlet plus a minimum lift
-    (``flow_min_lift_k``, else ``thermal_model.FLOW_MIN_LIFT_K``) at the
+    (``thermal_model.start_flow_min_lift_k``: ``flow_min_lift_k``, never
+    below the pump's own heating start hysteresis where one is read) at the
     modulation floor, so the pump's own water thermostat can realize a
     lower level.
     With no inlet reading the floor is the rated :data:`FLOW_HOLD_C`, in
@@ -893,7 +887,8 @@ def _flow_target(inp: ArbiterInputs, duty: str | None, now: datetime) -> float |
         p_min, p_max = _band_kw(inp)
         heat_c = _heat_ceiling_c(inp.config)
         floor_c = _or_hold(modulation_floor_flow_c(
-            _flow_inlet_c(inp), _gate_c(inp), configured_flow_min_lift_k(inp.config),
+            _flow_inlet_c(inp), _gate_c(inp),
+            start_flow_min_lift_k(inp.config, getattr(inp.state, "space_start_hysteresis_k", None)),
         ), inp.config)
         return _bounded(
             inp,
@@ -1184,26 +1179,22 @@ def _silent_target(coord: Any, inp: ArbiterInputs, now: datetime) -> bool | None
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
@@ -1686,6 +1677,7 @@ def _observe(held: ArbiterState, inp: ArbiterInputs, duty: str | None, now: date
             held.log.append(_verdict(row, tank))
         held.step = row = {"start": start, "planned": duty, "plan": inp.plan, "tank": tank,
                            "measured": False, "ran": False, "dhw_mode": False}
+        row["start_below"] = _dhw_start_below_c(inp)
     elif row["plan"] is not inp.plan:
         row["planned"], row["plan"] = duty, inp.plan
     power = inp.measured_power_kw
@@ -1696,6 +1688,33 @@ def _observe(held: ArbiterState, inp: ArbiterInputs, duty: str | None, now: date
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
@@ -1712,7 +1731,7 @@ def _verdict(row: dict[str, Any], tank: Any) -> dict[str, Any]:
     elif actual == planned or (planned == "both" and actual != "idle"):
         verdict = "delivered"
     else:
-        verdict = f"{actual}-instead"
+        verdict = _missed(row, planned, actual)
     return {"start": row["start"].isoformat(), "planned": planned,
             "actual": actual, "verdict": verdict}
 
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
index 00095880b4..5b5bba0267 100644
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
           "pump_duty_mode": "Off (the default) never writes the pump. Observe writes nothing and keeps a 24-hour ledger, in the diagnostics, of the duty each plan step asked for against what the pump did (from the power entity, the mode and the tank temperature). Control writes the operating mode above (hot water only on hot-water-only steps, heating only on space-heating-only steps, Heating + DHW when both are planned or a disinfection cycle is on, unchanged on idle steps), the hot water set-point entity (the hot water set-point configured on the hot water page) and the space set-point entity (for a flow set-point, a target that follows the planned power — the heating flow (55 °C, or flow_heat_c) at full power, toward 5 °C (or flow_min_lift_k) above the first fresh reading of the heat-pump return, buffer tank, floor return or valve outlet (35 °C when none is configured) at the modulation floor — or the entity maximum on steps that heat the house, its minimum on steps that do not, and 35 °C or the weather curve when the plan is not in charge; for an indoor one, the planned room temperature). Where the mode offers no single-duty option, as on the GCHV Modbus package, the other duty's set-point is lowered to its minimum instead. A hot-water-only stretch is capped at 90 minutes (30 below -10 °C outdoors), unless the room is already at its planned temperature. While Optimizer active is on, any change to those entities the optimizer did not make is written back at once; turn Optimizer active off to change the pump by hand. A value the pump does not hold raises a warning and is sent again every 5 minutes.",
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
index 20c8f0db92..fe8fa30fb7 100644
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
diff --git a/custom_components/heatpump_optimizer/translations/de.json b/custom_components/heatpump_optimizer/translations/de.json
index cefe0e204c..dfba34dc50 100644
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
           "pump_duty_mode": "Aus (Standard) schreibt nie auf die Wärmepumpe. Beobachten schreibt nichts und führt in den Diagnosedaten ein 24-Stunden-Protokoll darüber, welche Funktion jeder Planschritt angefordert hat und was die Wärmepumpe getan hat (aus der Leistungsentität, dem Modus und der Speichertemperatur). Steuern schreibt den oben gewählten Betriebsmodus (nur Warmwasser bei reinen Warmwasserschritten, nur Heizen bei reinen Raumheizungsschritten, Heizen + Warmwasser, wenn beides geplant ist oder ein Desinfektionszyklus läuft, unverändert bei Leerlaufschritten), die Entität für den Warmwasser-Sollwert (der auf der Warmwasserseite konfigurierte Warmwasser-Sollwert) und die Entität für den Raumheizungs-Sollwert (bei einem Vorlauf-Sollwert ein Ziel, das der geplanten Leistung folgt – die Heizungsvorlauftemperatur (55 °C, oder flow_heat_c) bei voller Leistung, in Richtung 5 °C (oder flow_min_lift_k) über dem ersten aktuellen Wert von Wärmepumpen-Rücklauf, Pufferspeicher, Fußbodenrücklauf oder Ventilauslass (35 °C, wenn keiner konfiguriert ist) an der Modulationsuntergrenze – oder das Maximum der Entität bei Schritten, die das Haus heizen, ihr Minimum bei Schritten, die es nicht tun, und 35 °C oder die Wetterkurve, wenn der Plan nicht die Führung hat; bei einem Raum-Sollwert die geplante Raumtemperatur). Wo der Modus keine Einzelfunktion anbietet, etwa beim GCHV-Modbus-Paket, wird stattdessen der Sollwert der anderen Funktion auf sein Minimum gesenkt. Ein reiner Warmwasserabschnitt ist auf 90 Minuten begrenzt (30 unter -10 °C Außentemperatur), außer der Raum hat bereits seine geplante Temperatur. Solange Optimierer aktiv eingeschaltet ist, wird jede Änderung an diesen Entitäten, die der Optimierer nicht vorgenommen hat, sofort zurückgeschrieben; schalte Optimierer aktiv aus, um die Wärmepumpe von Hand zu ändern. Ein Wert, den die Wärmepumpe nicht übernimmt, löst eine Warnung aus und wird alle 5 Minuten erneut gesendet.",
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
index 00095880b4..5b5bba0267 100644
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
           "pump_duty_mode": "Off (the default) never writes the pump. Observe writes nothing and keeps a 24-hour ledger, in the diagnostics, of the duty each plan step asked for against what the pump did (from the power entity, the mode and the tank temperature). Control writes the operating mode above (hot water only on hot-water-only steps, heating only on space-heating-only steps, Heating + DHW when both are planned or a disinfection cycle is on, unchanged on idle steps), the hot water set-point entity (the hot water set-point configured on the hot water page) and the space set-point entity (for a flow set-point, a target that follows the planned power — the heating flow (55 °C, or flow_heat_c) at full power, toward 5 °C (or flow_min_lift_k) above the first fresh reading of the heat-pump return, buffer tank, floor return or valve outlet (35 °C when none is configured) at the modulation floor — or the entity maximum on steps that heat the house, its minimum on steps that do not, and 35 °C or the weather curve when the plan is not in charge; for an indoor one, the planned room temperature). Where the mode offers no single-duty option, as on the GCHV Modbus package, the other duty's set-point is lowered to its minimum instead. A hot-water-only stretch is capped at 90 minutes (30 below -10 °C outdoors), unless the room is already at its planned temperature. While Optimizer active is on, any change to those entities the optimizer did not make is written back at once; turn Optimizer active off to change the pump by hand. A value the pump does not hold raises a warning and is sent again every 5 minutes.",
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
index a5bd2a1003..ae8c426623 100644
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
           "pump_duty_mode": "Av (standard) skriver aldrig till pumpen. Observera skriver inget och för en logg över det senaste dygnet, i diagnostiken, över vilken uppgift varje planerat steg bad om och vad pumpen gjorde (från effektentiteten, driftläget och tanktemperaturen). Styr skriver driftläget ovan (bara varmvatten på steg med bara varmvatten, bara värme på steg med bara rumsvärme, Värme + varmvatten när båda planeras eller en desinfektion pågår, oförändrat på vilande steg), varmvattnets börvärdesentitet (varmvattnets börvärde från varmvattensidan) och rumsvärmens börvärdesentitet (för ett framledningsbörvärde 55 °C eller entitetens maximum på steg som värmer huset, dess minimum på steg som inte gör det, och 35 °C eller värmekurvan när planen inte styr; för ett innebörvärde den planerade rumstemperaturen). Där driftläget saknar ett läge för bara en uppgift, som i GCHV Modbus-paketet, sänks den andra uppgiftens börvärde till sitt minimum i stället. En sträcka med bara varmvatten begränsas till 90 minuter (30 under -10 °C ute), om inte rummet redan har sin planerade temperatur. Medan Optimerare aktiv är på skrivs varje ändring av entiteterna som optimeraren inte gjorde tillbaka direkt; stäng av Optimerare aktiv för att ändra pumpen för hand. Ett värde som pumpen inte behåller ger en varning och skickas igen var femte minut.",
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
diff --git a/dev/programme/delivery/3531.md b/dev/programme/delivery/3531.md
new file mode 100644
index 0000000000..9660f4a574
--- /dev/null
+++ b/dev/programme/delivery/3531.md
@@ -0,0 +1 @@
+- [#3531](https://github.com/tvofi/heatpump_optimizer/pull/3531) — **open**, R10-OUTSIDE-DHW-START-HYSTERESIS: r10 outside dhw start hysteresis (R10-OUTSIDE-DHW-START-HYSTERESIS)
diff --git a/dev/programme/delivery/3557.md b/dev/programme/delivery/3557.md
new file mode 100644
index 0000000000..75c0acc522
--- /dev/null
+++ b/dev/programme/delivery/3557.md
@@ -0,0 +1 @@
+- [#3557](https://github.com/tvofi/heatpump_optimizer/pull/3557) — **open**, R10-HOTFIX-SELFTEST-SCOPE-TABLE: r10 hotfix selftest scope table (R10-HOTFIX-SELFTEST-SCOPE-TABLE)
diff --git a/dev/programme/delivery/3573.md b/dev/programme/delivery/3573.md
new file mode 100644
index 0000000000..ba0941933f
--- /dev/null
+++ b/dev/programme/delivery/3573.md
@@ -0,0 +1 @@
+- [#3573](https://github.com/tvofi/heatpump_optimizer/pull/3573) — **open**, R10-GATE-DEFER-BARRIER: r10 gate defer barrier (R10-GATE-DEFER-BARRIER)
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
index 1d12ff8abb..23e59f4c8b 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -353,19 +353,27 @@
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
@@ -379,6 +387,7 @@
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
    "custom_components/heatpump_optimizer/freq_control.py",
+   "custom_components/heatpump_optimizer/frontend.py",
    "custom_components/heatpump_optimizer/grid_fee.py",
    "custom_components/heatpump_optimizer/heat_curve.py",
    "custom_components/heatpump_optimizer/heat_energy.py",
@@ -391,7 +400,9 @@
    "custom_components/heatpump_optimizer/manual_plan.py",
    "custom_components/heatpump_optimizer/mixing_valve.py",
    "custom_components/heatpump_optimizer/modbus_prefill.py",
+   "custom_components/heatpump_optimizer/name_match.py",
    "custom_components/heatpump_optimizer/narrative.py",
+   "custom_components/heatpump_optimizer/notifier.py",
    "custom_components/heatpump_optimizer/off_restore.py",
    "custom_components/heatpump_optimizer/open_meteo.py",
    "custom_components/heatpump_optimizer/optimizer.py",
@@ -399,16 +410,22 @@
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
@@ -448,7 +465,8 @@
    "tests/hastub/homeassistant/helpers/update_coordinator.py",
    "tests/hastub/homeassistant/loader.py",
    "tests/hastub/homeassistant/util/__init__.py",
-   "tests/hastub/homeassistant/util/dt.py"
+   "tests/hastub/homeassistant/util/dt.py",
+   "tests/profiles.py"
   ],
   "tests/boost_drift_replay.py": [
    "custom_components/heatpump_optimizer/__init__.py",
@@ -4238,6 +4256,8 @@
    "dev/audit/harnesses/r10_demand_overbook.py",
    "dev/audit/harnesses/r10_dhw_charge_settle_p90.py",
    "dev/audit/harnesses/r10_dhw_lift_law_grid.py",
+   "dev/audit/harnesses/r10_dhw_start_hysteresis.py",
+   "dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py",
    "dev/audit/harnesses/r10_diag_ages_export.py",
    "dev/audit/harnesses/r10_disinfection_setpoint.py",
    "dev/audit/harnesses/r10_duty_switch_price_section.py",
@@ -5157,7 +5177,7 @@
   },
   "tests/block_duty.py": {
    "rc": 0,
-   "seconds": 1.1
+   "seconds": 8.3
   },
   "tests/boost_drift_replay.py": {
    "rc": 0,
@@ -5173,7 +5193,7 @@
   },
   "tests/config_flow_steps.py": {
    "rc": 0,
-   "seconds": 29.8
+   "seconds": 32.5
   },
   "tests/debug_collect.py": {
    "rc": 0,
@@ -5205,7 +5225,7 @@
   },
   "tests/features.py": {
    "rc": 1,
-   "seconds": 531.8
+   "seconds": 1040.5
   },
   "tests/finite_boundary.py": {
    "rc": 0,
@@ -5217,7 +5237,7 @@
   },
   "tests/golden.py": {
    "rc": 0,
-   "seconds": 0.9
+   "seconds": 1.2
   },
   "tests/guard_pins.py": {
    "rc": 0,
@@ -5225,11 +5245,11 @@
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
@@ -5265,7 +5285,7 @@
   },
   "tests/structure.py": {
    "rc": 2,
-   "seconds": 14.0
+   "seconds": 51.2
   },
   "tests/typing_ruler.py": {
    "rc": 0,
@@ -5277,7 +5297,7 @@
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
index 7c74c96fb5..50d029db56 100644
--- a/tests/deployment_shape.py
+++ b/tests/deployment_shape.py
@@ -56,8 +56,8 @@ which drives the CI ratchet's archscore measurement and so opens the package
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
@@ -96,7 +96,11 @@ supply_hold.py, read by every closure that imports the coordinator, from 148 to
 R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py, read by every closure that
 imports the optimizer or the arbiter, left it at 154: measured alone on the
 148 recording it moves the same count to 154, the pairs it lifts being ones
-supply_hold.py lifts too).
+supply_hold.py lifts too; R10-OUTSIDE-DHW-START-HYSTERESIS's block_duty.py
+check that the coordinator's input read puts the pump's start hysteresis on
+the state builds a coordinator, which grew that script's closure from 74 to
+91 production files: nine pairs joined at the 0.80 floor and one left, the
+count from 154 to 162).
 Eighteen of the pairs sit at exactly 1.00 -- arch_score_head.py/deployment_shape.py,
 arch_score_head.py/entities.py and deployment_shape.py/entities.py
 (98 shared production files each), doc_claims.py/harness_headers.py
diff --git a/tests/features.py b/tests/features.py
index c582c70b28..a663d02b74 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -66328,6 +66328,9 @@ _P6_READ_ONLY = {
         "heat_pump_dhw_booster_entity", "heat_pump_fault_entity",
         "heat_pump_online_entity",
     )},
+    **{key: "the pump's own start hysteresis, read_temperature_delta_k reads it" for key in (
+        hp_const.CONF_SPACE_HYSTERESIS_ENTITY, hp_const.CONF_DHW_HYSTERESIS_ENTITY,
+    )},
 }
 
 
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
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index c9a4648ed9..f0b2e8461e 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17514,
+ "class_excess_loc": 17503,
  "const_modules_over_50": 3,
  "coordinator_attrs": 139,
  "coordinator_multiassigned_attrs": 108,
@@ -16,6 +16,6 @@
  "methods_over_150": 15,
  "methods_over_200": 8,
  "name_kept_members": 38,
- "recorded_at": "005eed2573da9e946fa4838de147401d0ff36cc1",
+ "recorded_at": "f44e761c19dc07fff222bbd6a323bdc847ea9f04",
  "seam_cut_total": 421
 }
diff --git a/tools/ci/fixtures/gate_requeued_needs_runs.json b/tools/ci/fixtures/gate_requeued_needs_runs.json
index 357766f765..1735d28f65 100644
--- a/tools/ci/fixtures/gate_requeued_needs_runs.json
+++ b/tools/ci/fixtures/gate_requeued_needs_runs.json
@@ -4,106 +4,127 @@
    {
     "conclusion": "success",
     "name": "prelude",
+    "started_at": "2026-11-11T12:39:05Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "arch-score / arch-score",
+    "started_at": "2026-11-11T12:39:07Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "budget-raise-gate / budget-raise-gate",
+    "started_at": "2026-11-11T12:39:14Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "codeql / Analyze (actions)",
+    "started_at": "2026-11-11T12:39:21Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "codeql / Analyze (javascript-typescript)",
+    "started_at": "2026-11-11T12:39:28Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "codeql / Analyze (python)",
+    "started_at": "2026-11-11T12:39:35Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "governance / policy-docs",
+    "started_at": "2026-11-11T12:40:42Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "governance / wave-script",
+    "started_at": "2026-11-11T12:40:49Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "governance / env-matrix",
+    "started_at": "2026-11-11T12:40:56Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "hassfest / hassfest",
+    "started_at": "2026-11-11T12:40:03Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "pr-contract / pr-contract",
+    "started_at": "2026-11-11T12:40:10Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "tests / fast (3.14)",
+    "started_at": "2026-11-11T12:40:17Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "tests / arch-instrument",
+    "started_at": "2026-11-11T12:41:24Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "tests / browser",
+    "started_at": "2026-11-11T12:41:31Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "tests / briefs",
+    "started_at": "2026-11-11T12:41:38Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "tests / typing",
+    "started_at": "2026-11-11T12:41:45Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "tests / mutation",
+    "started_at": "2026-11-11T12:41:52Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "tests / closures",
+    "started_at": "2026-11-11T12:41:59Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "tests / closure-scope",
+    "started_at": "2026-11-11T12:42:06Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "validate / validate-hacs",
+    "started_at": "2026-11-11T12:42:13Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "gate",
+    "started_at": "2026-11-11T12:42:20Z",
     "status": "completed"
    }
   ],
@@ -111,119 +132,141 @@
    {
     "conclusion": "success",
     "name": "prelude",
+    "started_at": "2026-11-11T12:39:05Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "arch-score / arch-score",
+    "started_at": "2026-11-11T12:39:07Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "budget-raise-gate / budget-raise-gate",
+    "started_at": "2026-11-11T12:39:14Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "codeql / Analyze (actions)",
+    "started_at": "2026-11-11T12:39:21Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "codeql / Analyze (javascript-typescript)",
+    "started_at": "2026-11-11T12:39:28Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "codeql / Analyze (python)",
+    "started_at": "2026-11-11T12:39:35Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "governance / policy-docs",
+    "started_at": "2026-11-11T12:40:42Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "governance / wave-script",
+    "started_at": "2026-11-11T12:40:49Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "governance / env-matrix",
+    "started_at": "2026-11-11T12:40:56Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "hassfest / hassfest",
+    "started_at": "2026-11-11T12:40:03Z",
     "status": "completed"
    },
    {
     "conclusion": null,
     "name": "pr-contract / pr-contract",
+    "started_at": null,
     "status": "queued"
    },
    {
     "conclusion": "success",
     "name": "tests / fast (3.14)",
+    "started_at": "2026-11-11T12:40:17Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "tests / arch-instrument",
+    "started_at": "2026-11-11T12:41:24Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "tests / browser",
+    "started_at": "2026-11-11T12:41:31Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "tests / briefs",
+    "started_at": "2026-11-11T12:41:38Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "tests / typing",
+    "started_at": "2026-11-11T12:41:45Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "tests / mutation",
+    "started_at": "2026-11-11T12:41:52Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "tests / closures",
+    "started_at": "2026-11-11T12:41:59Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "tests / closure-scope",
+    "started_at": "2026-11-11T12:42:06Z",
     "status": "completed"
    },
    {
     "conclusion": "success",
     "name": "validate / validate-hacs",
+    "started_at": "2026-11-11T12:42:13Z",
     "status": "completed"
    },
    {
     "conclusion": null,
     "name": "gate",
+    "started_at": null,
     "status": "in_progress"
    }
   ]
  },
  "base": "main",
  "head": "H",
- "note": "Constructed (not recorded) two-attempt run in the shape of run 43022147048: attempt 1 every need concluded; attempt 2, the gate re-run, has its re-queued need `pr-contract / pr-contract` listed queued (GATE-BUSY-REQUEUED-NEEDS).",
+ "note": "Constructed (not recorded) two-attempt run in the shape of run 43022147048: attempt 1 every need concluded; attempt 2, the gate re-run, has its re-queued need `pr-contract / pr-contract` listed queued (GATE-BUSY-REQUEUED-NEEDS). Timestamps follow run 43022147048's latest listing (read 2026-11-13): attempt 2 started 14:08:41Z (run_started_at); the carried prelude started 12:39:05Z; the re-queued need started 14:12:53Z. Every job of that listing reports run_attempt 2, carried or re-run, so a job's run_attempt does not tell them apart; its started_at against run_started_at does.",
  "pr": "7",
  "repo": "o/r",
  "run": {
   "display_title": "CI code pr=7 base=main sha=M",
   "id": 43022147048,
   "run_attempt": 2,
+  "run_started_at": "2026-11-11T14:08:41Z",
   "status": "in_progress"
  }
 }
diff --git a/tools/ci/gate.py b/tools/ci/gate.py
index 955476f785..8ad794c5f4 100644
--- a/tools/ci/gate.py
+++ b/tools/ci/gate.py
@@ -64,7 +64,7 @@ HERE = Path(__file__).resolve().parent
 sys.path.insert(0, str(HERE))                      # -I drops the script's directory
 import ghapi  # noqa: E402
 from prelude import (BODY_UNITS, CODE_UNITS, POLL_S, STARTED, UNITS, context, derive, judging, parse_title, prior_jobs,  # noqa: E402,F401
-                     run_jobs, title, workset)
+                     run_jobs, standing, title, workset)
 
 PUSH_ONLY = {"tests": ("coverage", "coverage-ratchet")}      # B3
 # The push-only job that is graded on its own and never fails the gate: a red
@@ -207,6 +207,9 @@ def gate(ctx: dict, api: dict) -> tuple[bool, list[str]]:
         if r is me and any((r["jobs"].get(f"{unit} / {n}") or ("",))[0] != "completed" for n in names):
             return "~", r["id"]
         return max(((r.get("starts") or {}).get(f"{unit} / {n}") or "" for n in names), default=""), r["id"]
+    # One standing view per run for busy() and the source read alike (GATE-BUSY-REQUEUED-NEEDS):
+    # a gate the overlay released judges the re-running run's need where busy() read it.
+    others = [{**r, **dict(zip(("jobs", "starts"), standing(r)))} for r in others]
     for unit, names in required.items():
         src = None
         for r in sorted(others + [me], key=lambda r: fresh(r, names), reverse=True):
@@ -271,10 +274,11 @@ def read_api(ctx: dict, claim: dict, reaches_cc, get) -> dict:
         if r["id"] != ctx["run_id"]:
             st: dict = {}
             row = {"id": r["id"], "title": r.get("display_title") or "", "status": r["status"],
+                   "attempt": r.get("run_attempt"), "run_started_at": r.get("run_started_at"),
                    "starts": st, "jobs": {} if r["status"] == "action_required"
                    else run_jobs(get, repo, r["id"], st)}
             if r["status"] not in ("completed", "action_required"):     # only an unfinished run is busy()'s to judge
-                row["prior"] = prior_jobs(get, repo, row, r.get("run_attempt"))
+                row["prior"] = prior_jobs(get, repo, row)
             api["runs_at_head"].append(row)
     return api
 
@@ -1028,6 +1032,63 @@ def self_test() -> int:
           got[:2], ([], 0))
     got = requeue_busy(prior=[j for j in rq["attempts"]["1"] if j["name"] != "pr-contract / pr-contract"])
     check("requeued needs null: a need the previous attempt never listed stays busy", got[:2], ([rq_id], 1))
+    # Repair round (review blocked at 868f8a72): the overlay's domain is the run's OWN gate re-run, and
+    # gate()'s source read takes the same standing view as busy(). A need is read from the previous
+    # attempt only when (R1) the run is past attempt 1, (R2) the latest attempt did not re-run the
+    # prelude (a re-run-all did: its prelude started at or after run_started_at), (R3) the need is
+    # owed and listed unfinished, and (R4) its previous attempt concluded success or skipped; a
+    # failed, cancelled or timed-out need is what "re-run failed jobs" re-queues, a new source.
+    MUT, PRC = "tests / mutation", "pr-contract / pr-contract"
+    a1 = {j["name"]: j for j in rq["attempts"]["1"]}
+    queued = {"status": "queued", "conclusion": None, "started_at": None}
+
+    def shape(was=None, now=None):
+        return ([dict(j, **(was or {}).get(j["name"], {})) for j in rq["attempts"]["1"]],
+                [dict(j, **(now or {}).get(j["name"], {})) for j in rq["attempts"]["2"]])
+    p1, l2 = shape({MUT: {"conclusion": "failure"}, "gate": {"conclusion": "failure"}},
+                   {MUT: queued, "gate": queued, PRC: a1[PRC]})
+    check("requeued needs, re-run failed jobs: a unit that failed in attempt 1 and is queued again keeps the run "
+          "busy (the reviewer's attack shape)", requeue_busy(prior=p1, listing=l2)[:2], ([rq_id], 1))
+    p1, l2 = shape({MUT: {"conclusion": "cancelled"}}, {MUT: queued})
+    check("requeued needs, re-run failed jobs: a unit cancelled in attempt 1 and queued again keeps the run busy",
+          requeue_busy(prior=p1, listing=l2)[:2], ([rq_id], 1))
+    p1, l2 = shape({MUT: {"conclusion": "failure"}}, {MUT: queued})
+    check("requeued needs, re-run failed jobs beside the re-queued need: the failed unit still holds the run busy",
+          requeue_busy(prior=p1, listing=[dict(j, **queued) if j["name"] == PRC else j for j in l2])[:2], ([rq_id], 1))
+    rerun_all = [dict(j, started_at="2026-11-11T14:09:00Z") if j["status"] == "completed" else j
+                 for j in rq["attempts"]["2"]]
+    check("requeued needs, re-run all: the prelude re-ran in this attempt, so a queued need is a new source: busy, "
+          "no extra read", requeue_busy(listing=rerun_all)[:2], ([rq_id], 0))
+    check("requeued needs, re-run all: a prelude still queued in this attempt: busy, no extra read",
+          requeue_busy(listing=[dict(j, **queued) if j["name"] == "prelude" else j for j in rerun_all])[:2],
+          ([rq_id], 0))
+    p1, _ = shape({PRC: {"conclusion": "skipped"}})
+    check("requeued needs: a need the previous attempt skipped (C3, the gate re-run's documented re-queue) is not "
+          "busy", requeue_busy(prior=p1)[:2], ([], 1))
+    no_start = {**rq["run"]}
+    no_start.pop("run_started_at")
+    rq_saved, rq["run"] = rq["run"], no_start
+    check("requeued needs null: a run listing no run_started_at keeps today's reading: busy, no extra read",
+          requeue_busy()[:2], ([rq_id], 0))
+    rq["run"] = rq_saved
+    # One-sided (verdict point 2): a gate released by the overlay judges the re-running run's unit from
+    # the same standing source busy() read, never from an older run behind it.
+    get, _ = requeue_world()
+    api = read_api(rq_ctx, claim, True, get)
+    stale = {k: v for k, v in api["runs_at_head"][0]["jobs"].items()}
+    api["runs_at_head"].append({"id": 5, "title": title("code", "7", "main"), "status": "completed",
+                                "jobs": {**{k: ("completed", "success") for k in stale}, PRC: ("completed", "failure")},
+                                "starts": {PRC: "2026-11-11T12:00:00Z"}})
+    check("requeued needs, one source read: the released gate takes the re-running run's standing pr-contract "
+          "(attempt 1 success, started after the older red) as busy() did", gate(rq_ctx, api), (True, []))
+    p1, _ = shape({PRC: {"conclusion": "skipped"}})
+    get, _ = requeue_world(prior=p1)
+    api = read_api(rq_ctx, claim, True, get)
+    api["runs_at_head"].append({"id": 5, "title": title("code", "7", "main"), "status": "completed",
+                                "jobs": {**{k: ("completed", "success") for k in stale}, PRC: ("completed", "failure")},
+                                "starts": {PRC: "2026-11-11T12:00:00Z"}})
+    check("requeued needs, one source read: a need skipped before the re-run is no source there either, so the "
+          "older red stands", gate(rq_ctx, api), (False, ["pr-contract / pr-contract: failure (run 5)"]))
     print(f"gate self-test: {n} checks, {fails} failed")
     return 1 if fails else 0
 
diff --git a/tools/ci/prelude.py b/tools/ci/prelude.py
index 1096948b77..b600be6919 100644
--- a/tools/ci/prelude.py
+++ b/tools/ci/prelude.py
@@ -214,26 +214,61 @@ def owed_needs(run: dict) -> list[str]:
             if not (u == "tests" and n == "closure-scope" and not t[1])]
 
 
-def prior_jobs(get, repo: str, run: dict, attempt, log=lambda m: print(m, file=sys.stderr)) -> dict:
-    """The previous attempt's jobs of a run, name -> (status, conclusion), read ONLY when
-    the run's attempt is above 1 and an owed need is missing or unfinished in its latest
-    listing: a re-run re-queues the skipped needs of its own gate (run 43022147048
-    attempt 2: `pr-contract / pr-contract` queued 14:08:44Z, ran 14:12:53Z), and judging()
-    then reads the run busy to every other gate at the head. One GET per such run per
-    poll; `{}` (today's reading) when the read fails, logged with its reason. A skipped
-    need is no trigger: it is a completed job and judging() already reads it finished."""
-    attempt = int(attempt or 1)
-    jobs = run.get("jobs") or {}
-    if attempt <= 1 or all((jobs.get(k) or ("",))[0] == "completed" for k in owed_needs(run)):
+#: A previous attempt's conclusion that still stands while its re-queued need runs again (R4):
+#: the need ran green, or never ran (a skipped need, C3). Failure, cancelled and timed_out are
+#: what GitHub's "re-run failed jobs" re-queues: a new source, which busy() waits on.
+STANDS = ("success", "skipped")
+
+
+def requeued(run: dict) -> list[str]:
+    """The owed needs of a run that its own gate re-run re-queued (GATE-BUSY-REQUEUED-NEEDS),
+    from its latest listing alone; the one owner of the domain rule, read by prior_jobs (whether
+    to read the previous attempt) and standing() (where to overlay it):
+      R1 the run is past attempt 1;
+      R2 its latest attempt did not re-run the prelude: the listed prelude completed green and
+         started before the attempt's run_started_at. A re-run-all re-runs the prelude too, so
+         its queued needs are new sources. Every job of run 43022147048's latest listing reports
+         run_attempt 2, carried or re-run, so started_at is the separator; a run or prelude
+         with no timestamp reads as today (no overlay);
+      R3 the need is owed by the run's title and listed unfinished."""
+    if int(run.get("attempt") or 1) <= 1:
+        return []                                                                    # R1
+    jobs, began = run.get("jobs") or {}, run.get("run_started_at") or ""
+    pre = (run.get("starts") or {}).get("prelude") or ""
+    if jobs.get("prelude") != ("completed", "success") or not began or not pre or pre >= began:
+        return []                                                                    # R2
+    return [k for k in owed_needs(run) if k in jobs and jobs[k][0] != "completed"]   # R3
+
+
+def prior_jobs(get, repo: str, run: dict, log=lambda m: print(m, file=sys.stderr)) -> dict:
+    """The previous attempt's jobs of a run, name -> (status, conclusion, started_at), read ONLY
+    when requeued(run) names a need: a gate re-run re-queues its skipped needs (run 43022147048
+    attempt 2: `pr-contract / pr-contract` queued 14:08:44Z, ran 14:12:53Z). One GET per such
+    run per poll; `{}` (today's reading) when the read fails, logged with its reason."""
+    if not requeued(run):
         return {}
-    path = f"repos/{repo}/actions/runs/{run['id']}/attempts/{attempt - 1}/jobs"
+    path = f"repos/{repo}/actions/runs/{run['id']}/attempts/{int(run['attempt']) - 1}/jobs"
     st, _, doc = get(path, {"per_page": 100})
     rows = doc.get("jobs") if st == 200 and isinstance(doc, dict) else None
     if rows is None or doc.get("total_count", len(rows)) > len(rows):
         log(f"prior attempt of run {run['id']} unread ({path}: HTTP {st}"
             f"{'' if rows is None else ', more than one page'}): judged from the latest listing")
         return {}
-    return {j["name"]: (j["status"], j["conclusion"]) for j in rows}
+    return {j["name"]: (j["status"], j["conclusion"], j.get("started_at")) for j in rows}
+
+
+def standing(run: dict) -> tuple[dict, dict]:
+    """A run's jobs and job starts as both readers judge them, busy() through judging() and
+    gate()'s source read: the latest listing, with each requeued() need whose previous attempt
+    concluded in STANDS (R4) read from that attempt, its start included, until it finishes.
+    A need absent from `prior`, or unfinished there, keeps its latest (unfinished) row."""
+    jobs, starts = dict(run.get("jobs") or {}), dict(run.get("starts") or {})
+    prior = run.get("prior") or {}
+    for k in requeued(run):
+        p = prior.get(k)
+        if p and p[0] == "completed" and p[1] in STANDS:                             # R4
+            jobs[k], starts[k] = (p[0], p[1]), (p[2] if len(p) > 2 else None)
+    return jobs, starts
 
 
 def judging(run: dict) -> bool:
@@ -245,19 +280,10 @@ def judging(run: dict) -> bool:
     run's skipped `pr-contract` (C3), adds no source. Read as owed, it made every
     such run busy to every other gate and prelude at its head (#3263, run
     42338396358 beside code run 42338396871).
-    A need the run's re-run re-queued is read from `run["prior"]` (prior_jobs: the
-    previous attempt, where it concluded) instead of its unfinished latest listing
-    (GATE-BUSY-REQUEUED-NEEDS): the pre-rerun source stands until the need finishes.
-    A need unfinished in both attempts, or absent from `prior`, keeps the run busy."""
-    jobs = run.get("jobs") or {}
-    prior = run.get("prior") or {}
-
-    def seen(k):
-        st = jobs.get(k)
-        if (st is None or st[0] != "completed") and (prior.get(k) or ("",))[0] == "completed":
-            return prior[k]
-        return st
-    if "gate" not in jobs or not all(seen(k)[0] == "completed" for k in jobs
+    The jobs are standing(run)'s (GATE-BUSY-REQUEUED-NEEDS): a need the run's own gate
+    re-run re-queued is read where it concluded before, as gate()'s source read reads it."""
+    jobs = standing(run)[0]
+    if "gate" not in jobs or not all(st[0] == "completed" for k, st in jobs.items()
                                      if k == "prelude" or k.split(" / ")[0] in UNITS):
         return False
     t = parse_title(run.get("title") or "")
@@ -269,7 +295,7 @@ def judging(run: dict) -> bool:
         for k in owed_needs(run):
             if k.split(" / ")[0] != u:
                 continue
-            st = seen(k)
+            st = jobs.get(k)
             if st is None or st[0] != "completed":
                 return False
     return True
@@ -291,11 +317,12 @@ def wait_sources(ctx: dict, get, sleep=time.sleep, now=time.monotonic) -> str:
             return f"runs at {ctx['head'][:12]}: HTTP {st}"
         busy = []
         for r in doc.get("workflow_runs", []):
-            run = {"id": r["id"], "title": r.get("display_title") or ""}
+            run = {"id": r["id"], "title": r.get("display_title") or "", "attempt": r.get("run_attempt"),
+                   "run_started_at": r.get("run_started_at"), "starts": {}}
             if r["status"] in UNFINISHED and waits_on(ctx["run_id"], run):
                 try:
-                    run["jobs"] = run_jobs(get, ctx["repo"], r["id"])
-                    run["prior"] = prior_jobs(get, ctx["repo"], run, r.get("run_attempt"))
+                    run["jobs"] = run_jobs(get, ctx["repo"], r["id"], run["starts"])
+                    run["prior"] = prior_jobs(get, ctx["repo"], run)
                 except ghapi.ApiError as e:
                     return str(e)
                 if not judging(run):
@@ -543,6 +570,18 @@ def self_test() -> int:
         return 200, {}, {"jobs": rqfx["attempts"][att]}
     check("requeued needs: wait_sources does not wait on a lower run whose only unfinished job is a need finished "
           "in attempt 1", wait_sources(rctx, rq_get, lambda s: None, iter(range(0, 10 ** 6, 3000)).__next__), "")
+
+    def rq_failed_get(path, params=None):          # re-run failed jobs: `tests / mutation` failed in attempt 1
+        if path.endswith("ci.yml/runs"):
+            return 200, {}, {"workflow_runs": [{**rqfx["run"], "id": 40, "status": "in_progress"}]}
+        if "/attempts/1/" in path:
+            return 200, {}, {"jobs": [dict(j, conclusion="failure") if j["name"] == "tests / mutation" else j
+                                      for j in rqfx["attempts"]["1"]]}
+        return 200, {}, {"jobs": [dict(j, status="queued", conclusion=None, started_at=None)
+                                  if j["name"] == "tests / mutation" else j for j in rqfx["attempts"]["2"]]}
+    check("requeued needs null: wait_sources still waits on a lower run re-running a unit that failed in attempt 1",
+          wait_sources(rctx, rq_failed_get, lambda s: None, iter(range(0, 10 ** 6, 3000)).__next__).startswith(
+              "run(s) [40] still adding sources"), True)
     # C3 (option A): an edit run beside a code run that has not started its
     # pr-contract exits at once with the body units less pr-contract; beside one
     # whose pr-contract has started, or a finished one, it waits as before.
diff --git a/tools/ci/selftest_closures.json b/tools/ci/selftest_closures.json
index f5a326bae7..e81ad4d9d5 100644
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
@@ -2532,6 +2539,7 @@
     "tools/audit/seat/body_push.sh",
     "tools/audit/seat/carry_fold.py",
     "tools/audit/seat/gh_read.py",
+    "tools/audit/seat/pr_args.sh",
     "tools/audit/seat/record_row.py",
     "tools/audit/seat/ref_privacy.py",
     "tools/audit/seat/roster_lib.py",
@@ -2544,9 +2552,9 @@
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
@@ -2560,9 +2568,9 @@
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
@@ -2592,9 +2600,9 @@
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
@@ -2703,6 +2711,7 @@
     "commit-tree",
     "describe",
     "diff",
+    "fetch",
     "log",
     "ls-tree",
     "merge",
@@ -2734,9 +2743,9 @@
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
@@ -2769,20 +2778,21 @@
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
@@ -2794,9 +2804,9 @@
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
@@ -2880,18 +2890,20 @@
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
@@ -2902,9 +2914,9 @@
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
@@ -2923,9 +2935,9 @@
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
@@ -2943,11 +2955,11 @@
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
@@ -2972,9 +2984,9 @@
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
@@ -3000,11 +3012,11 @@
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
@@ -3026,10 +3038,12 @@
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
@@ -3037,9 +3051,9 @@
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
@@ -3053,9 +3067,9 @@
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
@@ -3603,6 +3617,7 @@
     "tests/mutation_ledger/killed_by/draw_range.py",
     "tests/mutation_ledger/killed_by/drift.py",
     "tests/mutation_ledger/killed_by/driving_grade.py",
+    "tests/mutation_ledger/killed_by/duty_legs.py",
     "tests/mutation_ledger/killed_by/duty_switch.py",
     "tests/mutation_ledger/killed_by/early_cutoff.py",
     "tests/mutation_ledger/killed_by/entity.py",
@@ -3654,6 +3669,7 @@
     "tests/mutation_ledger/killed_by/slot_drivers.py",
     "tests/mutation_ledger/killed_by/snapshots.py",
     "tests/mutation_ledger/killed_by/store.py",
+    "tests/mutation_ledger/killed_by/supply_hold.py",
     "tests/mutation_ledger/killed_by/switch.py",
     "tests/mutation_ledger/killed_by/sysid.py",
     "tests/mutation_ledger/killed_by/tariff.py",
@@ -3761,9 +3777,9 @@
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
@@ -3775,16 +3791,17 @@
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
@@ -3796,9 +3813,9 @@
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
@@ -3835,12 +3852,16 @@
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
@@ -3927,6 +3948,7 @@
     "tools/audit/seat/record_beat.py",
     "tools/audit/seat/record_row.py",
     "tools/audit/seat/ref_privacy.py",
+    "tools/audit/seat/remerge_main.sh",
     "tools/audit/seat/resume_doc.py",
     "tools/audit/seat/review_carry.py",
     "tools/audit/seat/review_packet.py",
@@ -3981,6 +4003,7 @@
     "tools/policy/figure_lint.mjs",
     "tools/policy/fragments_sync.mjs",
     "tools/policy/friction_issues.mjs",
+    "tools/policy/legacy_control_files.json",
     "tools/policy/policy_lint.mjs",
     "tools/policy/policy_lint_envmatrix.mjs",
     "tools/policy/policy_lint_mutants.mjs",
@@ -4073,9 +4096,9 @@
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
@@ -4098,9 +4121,9 @@
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
@@ -4188,9 +4211,9 @@
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
@@ -4202,9 +4225,9 @@
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
@@ -4215,9 +4238,9 @@
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
@@ -4238,9 +4261,9 @@
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
@@ -4255,9 +4278,9 @@
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
@@ -4273,9 +4296,9 @@
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
@@ -4305,9 +4328,9 @@
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
@@ -4325,6 +4348,7 @@
     "config",
     "objects",
     "refs",
+    "tests",
     "tests/env_drift.py",
     "tools",
     "tools/audit",
@@ -4334,9 +4358,9 @@
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
@@ -4373,6 +4397,7 @@
    "files": [
     "tests/throwaway_git.sh",
     "tools/audit/seat/heartbeat.sh",
+    "tools/audit/seat/pr_args.sh",
     "tools/audit/seat/ref_privacy.py"
    ],
    "probes": [
@@ -4381,14 +4406,15 @@
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
@@ -4535,9 +4561,9 @@
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
@@ -4558,9 +4584,9 @@
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
@@ -4576,9 +4602,9 @@
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
@@ -4595,9 +4621,9 @@
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
@@ -4613,9 +4639,9 @@
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
@@ -4645,9 +4671,9 @@
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
@@ -4660,6 +4686,7 @@
     "tools/policy/brief_lint.mjs",
     "tools/policy/counts.mjs",
     "tools/policy/dependabot_contract.mjs",
+    "tools/policy/legacy_control_files.json",
     "tools/policy/policy_lint.mjs",
     "tools/policy/render_md.mjs",
     "tools/policy/vendor/markdown-it.min.js",
@@ -4682,13 +4709,14 @@
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
@@ -4703,7 +4731,9 @@
     "tools/audit/merge_fastpath.py",
     "tools/audit/seat/gh_read.py",
     "tools/audit/seat/ledger.py",
+    "tools/audit/seat/merge_pr.sh",
     "tools/audit/seat/merge_train.py",
+    "tools/audit/seat/orchestrator_tick.py",
     "tools/audit/seat/pr_args.sh",
     "tools/audit/seat/proof_watch.py",
     "tools/audit/seat/queue_pre_flight.py",
@@ -4729,13 +4759,13 @@
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
@@ -4753,9 +4783,9 @@
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
@@ -4810,9 +4840,9 @@
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
@@ -4825,14 +4855,15 @@
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
@@ -4861,9 +4892,9 @@
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
@@ -5059,11 +5090,14 @@
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
@@ -5142,11 +5176,11 @@
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
@@ -5171,9 +5205,9 @@
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
@@ -5184,9 +5218,9 @@
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
@@ -5204,9 +5238,9 @@
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
@@ -5231,9 +5265,9 @@
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
@@ -5296,9 +5330,9 @@
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
@@ -5315,9 +5349,9 @@
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
@@ -5432,6 +5466,7 @@
     "tools/policy/fixtures/required-contexts.json",
     "tools/policy/fragments_sync.mjs",
     "tools/policy/friction_issues.mjs",
+    "tools/policy/legacy_control_files.json",
     "tools/policy/policy_lint.mjs",
     "tools/policy/policy_lint_envmatrix.mjs",
     "tools/policy/policy_lint_mutants.mjs",
@@ -6254,11 +6289,14 @@
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
@@ -6299,6 +6337,7 @@
     "tools/audit/seat/gh_read.py",
     "tools/audit/seat/merge_pr.sh",
     "tools/audit/seat/merge_train.py",
+    "tools/audit/seat/pr_args.sh",
     "tools/policy/budget_raise_gate.py"
    ],
    "probes": [
@@ -6321,9 +6360,9 @@
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
@@ -6403,6 +6442,7 @@
     "tools/policy/fixtures/policy-rot/prepr/wrong-head.md",
     "tools/policy/fixtures/red-ancestry/**",
     "tools/policy/fixtures/required-contexts.json",
+    "tools/policy/legacy_control_files.json",
     "tools/policy/policy_lint.mjs",
     "tools/policy/render_md.mjs",
     "tools/policy/role_pack.py",
@@ -6950,6 +6990,7 @@
     "tests/mutation_ledger/killed_by/draw_range.py",
     "tests/mutation_ledger/killed_by/drift.py",
     "tests/mutation_ledger/killed_by/driving_grade.py",
+    "tests/mutation_ledger/killed_by/duty_legs.py",
     "tests/mutation_ledger/killed_by/duty_switch.py",
     "tests/mutation_ledger/killed_by/early_cutoff.py",
     "tests/mutation_ledger/killed_by/entity.py",
@@ -7001,6 +7042,7 @@
     "tests/mutation_ledger/killed_by/slot_drivers.py",
     "tests/mutation_ledger/killed_by/snapshots.py",
     "tests/mutation_ledger/killed_by/store.py",
+    "tests/mutation_ledger/killed_by/supply_hold.py",
     "tests/mutation_ledger/killed_by/switch.py",
     "tests/mutation_ledger/killed_by/sysid.py",
     "tests/mutation_ledger/killed_by/tariff.py",
@@ -7135,9 +7177,9 @@
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
@@ -7185,9 +7227,9 @@
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
@@ -7262,6 +7304,7 @@
    "index": false,
    "objects": true,
    "git": [
+    "?",
     "diff",
     "merge-base",
     "show"
@@ -7286,6 +7329,7 @@
     "tools/policy/fixtures/policy-rot/prepr/good.md",
     "tools/policy/fixtures/policy-rot/prepr/no-figures.md",
     "tools/policy/fixtures/policy-rot/prepr/wrong-head.md",
+    "tools/policy/legacy_control_files.json",
     "tools/policy/policy_lint.mjs",
     "tools/policy/render_md.mjs",
     "tools/policy/vendor/markdown-it.min.js",
@@ -7298,6 +7342,7 @@
     "objects",
     "package.json",
     "refs",
+    "tests",
     "tools",
     "tools/audit",
     "tools/audit/seat",
@@ -7312,12 +7357,12 @@
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
@@ -7331,9 +7376,9 @@
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
@@ -7355,6 +7400,7 @@
     "tools/policy/brief_lint.mjs",
     "tools/policy/counts.mjs",
     "tools/policy/dependabot_contract.mjs",
+    "tools/policy/legacy_control_files.json",
     "tools/policy/policy_lint.mjs",
     "tools/policy/render_md.mjs",
     "tools/policy/vendor/markdown-it.min.js",
@@ -7385,11 +7431,11 @@
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
@@ -7413,9 +7459,9 @@
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
@@ -7432,9 +7478,9 @@
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
@@ -7456,9 +7502,9 @@
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
@@ -7486,6 +7532,7 @@
     "tools/policy/counts.mjs",
     "tools/policy/dependabot_contract.mjs",
     "tools/policy/fixtures/required-contexts.json",
+    "tools/policy/legacy_control_files.json",
     "tools/policy/policy_lint.mjs",
     "tools/policy/render_md.mjs",
     "tools/policy/vendor/markdown-it.min.js"
@@ -7544,9 +7591,9 @@
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
@@ -7571,9 +7618,9 @@
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
@@ -7591,9 +7638,9 @@
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
@@ -7613,9 +7660,9 @@
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
@@ -7678,9 +7725,9 @@
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
@@ -7711,9 +7758,9 @@
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
@@ -7732,9 +7779,9 @@
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
@@ -7761,6 +7808,7 @@
     "tests/requirements-typing.txt",
     "tests/typing_budgets.json",
     "tools/audit/seat/cloud-setup.sh",
+    "tools/audit/seat/pr_args.sh",
     "tools/audit/seat/seat_venv.sh",
     "tools/audit/seat/shims/**"
    ],
@@ -7768,9 +7816,9 @@
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
@@ -7886,6 +7934,7 @@
     "tools/policy/fixtures/required-contexts.json",
     "tools/policy/fragments_sync.mjs",
     "tools/policy/friction_issues.mjs",
+    "tools/policy/legacy_control_files.json",
     "tools/policy/policy_lint.mjs",
     "tools/policy/policy_lint_envmatrix.mjs",
     "tools/policy/policy_lint_mutants.mjs",
@@ -8259,9 +8308,9 @@
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
@@ -8325,9 +8374,9 @@
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
@@ -8369,9 +8418,9 @@
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
@@ -8405,9 +8454,9 @@
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
@@ -8470,6 +8519,7 @@
     "tests/mutation_ledger/killed_by/draw_range.py/.gitattributes",
     "tests/mutation_ledger/killed_by/drift.py/.gitattributes",
     "tests/mutation_ledger/killed_by/driving_grade.py/.gitattributes",
+    "tests/mutation_ledger/killed_by/duty_legs.py/.gitattributes",
     "tests/mutation_ledger/killed_by/duty_switch.py/.gitattributes",
     "tests/mutation_ledger/killed_by/early_cutoff.py/.gitattributes",
     "tests/mutation_ledger/killed_by/entity.py/.gitattributes",
@@ -8521,6 +8571,7 @@
     "tests/mutation_ledger/killed_by/slot_drivers.py/.gitattributes",
     "tests/mutation_ledger/killed_by/snapshots.py/.gitattributes",
     "tests/mutation_ledger/killed_by/store.py/.gitattributes",
+    "tests/mutation_ledger/killed_by/supply_hold.py/.gitattributes",
     "tests/mutation_ledger/killed_by/switch.py/.gitattributes",
     "tests/mutation_ledger/killed_by/sysid.py/.gitattributes",
     "tests/mutation_ledger/killed_by/tariff.py/.gitattributes",
@@ -8625,221 +8676,12 @@
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
@@ -8851,6 +8693,8 @@
    "files": [
     "tests/throwaway_git.sh",
     "tools/audit/seat/heartbeat.sh",
+    "tools/audit/seat/offline_spy.py",
+    "tools/audit/seat/pr_args.sh",
     "tools/audit/seat/ref_privacy.py",
     "tools/audit/seat/tick_loop.sh"
    ],
@@ -8860,6 +8704,7 @@
     "config",
     "objects",
     "refs",
+    "tests",
     "tools",
     "tools/.git",
     "tools/HEAD",
@@ -8888,9 +8733,9 @@
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
@@ -8912,9 +8757,9 @@
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
@@ -8925,9 +8770,9 @@
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
@@ -9123,12 +8968,14 @@
    ],
    "probes": [
     "-",
+    "-c",
     ".",
     "config",
     "dev/programme/delivery/5.md",
     "objects",
     "packed-refs",
     "refs",
+    "tests",
     "tests/env_drift.py",
     "tools",
     "tools/.gitattributes",
@@ -9217,6 +9064,7 @@
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
