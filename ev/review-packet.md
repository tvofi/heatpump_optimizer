# Review packet #3738
head: 1cf4d759c5022d4a51a93f2c6f9aaac2afe6d008
base: 8751943e17ef4d3ec699e7859ae829b4528d8ce7

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=135014359371 neutral
arch-score / arch-score id=135013679766 in_progress
arm id=135010958767 skipped
budget-raise-gate / budget-raise-gate id=135013680830 in_progress
cancel-superseded id=135010958157 success
codeql id=135013035975 skipped
codeql / Analyze (actions) id=135013680069 success
codeql / Analyze (javascript-typescript) id=135013680011 success
codeql / Analyze (python) id=135013680019 in_progress
gate id=135014735574 queued
governance id=135013035258 skipped
governance / env-matrix id=135013680487 queued
governance / instrument-self-tests id=135013680470 queued
governance / policy-docs id=135013680254 queued
governance / record id=135013683916 skipped
governance / wave-script id=135013680350 queued
hassfest id=135013034374 skipped
hassfest / hassfest id=135013679907 success
kernel-points id=135013682051 skipped
pr-contract id=135014721691 skipped
prelude id=135010958562 success
refresh id=135010958759 success
tests id=135013034715 skipped
tests / arch-instrument id=135015095221 queued
tests / briefs id=135013680208 queued
tests / browser id=135015095257 queued
tests / closure-scope id=135013680103 success
tests / closures id=135015095166 queued
tests / coverage id=135015095358 queued
tests / fast (3.14) id=135015095153 queued
tests / mutation id=135013680239 queued
tests / nightly-ha (2025.2.0) id=135015095467 queued
tests / nightly-ha (stable) id=135015095401 queued
tests / nightly-status id=135013680257 queued
tests / replay id=135015095174 queued
tests / typing id=135015095176 queued
validate id=135013035120 skipped
validate / validate-hacs id=135013679623 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 135013680470: queued has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
none

## carry_audit at the head
NOTE body item 401b4860: dismissed:built and pinned in this PR
NOTE body item 85ef765b: dismissed:built in this PR
NOTE body item db96b316: dismissed:no test shows the cancellation the note asks to report
NOTE body item bad27f92: dismissed:one re-raise per restart, re-latched on the next solve
NOTE body item a0ac6ffd: dismissed:the round-11 register owns its harnesses
NOTE body item 89a681d1: dismissed:a seat-environment conflict, recorded for the orchestrator
CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: SCOPED -- 27 script(s) run, 6 scoped out.
             no segment of this names a program this check knows
  unverified git archive 819aa2e354b4 dev/audit/rounds/round11
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified PYTHONPATH=tests/hastub python3 $EXPORT/<path> <args>
             the path `$EXPORT/<path>` is a template or an expansion, not a literal
  ok         PYTHONPATH=tests/hastub python3 tests/features.py
             `tests/features.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         tests/derive_closures.sh --single tests/config_flow_steps.py
             `tests/derive_closures.sh` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         python3 tests/structure.py --record
             `tests/structure.py` is in the tree at this head

FIGURES: 6 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._maybe_refresh_price_tile.GUARD_OFF.210c601b.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._maybe_refresh_price_tile.GUARD_OFF.210c601b.json
deleted file mode 100644
index 730e99cdc7..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._maybe_refresh_price_tile.GUARD_OFF.210c601b.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._maybe_refresh_price_tile GUARD_OFF 210c601b",
-  "killed_by": "tests/features.py",
-  "old": "        if (spec := price_tiles.take(price_tiles.rotation(self), specs, dt_util.now())) is None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_run_optimization.BOOLOP.502b669f.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_run_optimization.BOOLOP.502b669f.json
deleted file mode 100644
index 3419fbfbef..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_run_optimization.BOOLOP.502b669f.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_run_optimization BOOLOP 502b669f",
-  "killed_by": "tests/features.py",
-  "old": "            if self._optimization_rerun_requested and not self._entry_released:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against a15e3e33507bde9e566858ce32b2ded840edfa02: BOOLOP (`if self._optimization_rerun_requested or not self._entry_released:`) took tests/features.py from rc=0 failed=0 to rc=124 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_run_optimization.GUARD_OFF.502b669f.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_run_optimization.GUARD_OFF.502b669f.json
deleted file mode 100644
index 7b0f3e01e0..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_run_optimization.GUARD_OFF.502b669f.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_run_optimization GUARD_OFF 502b669f",
-  "killed_by": "tests/features.py",
-  "old": "            if self._optimization_rerun_requested and not self._entry_released:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against a15e3e33507bde9e566858ce32b2ded840edfa02: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_run_optimization.GUARD_OFF.cfa25e19.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_run_optimization.GUARD_OFF.cfa25e19.json
deleted file mode 100644
index a413c5f053..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_run_optimization.GUARD_OFF.cfa25e19.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_run_optimization GUARD_OFF cfa25e19",
-  "killed_by": "tests/features.py",
-  "old": "                if not _mode_superseded(entry_mode, self._mode):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against c5e1be1967de4b1d29b203aaf73162046dc85bd1: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.1550d375.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.1550d375.json
deleted file mode 100644
index 970af6401d..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.1550d375.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate BOOLOP 1550d375",
-  "killed_by": "tests/features.py",
-  "old": "        ) if steady and days is None else None",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`) if steady or days is None else None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.19646b85.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.19646b85.json
deleted file mode 100644
index 8a9575432a..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.19646b85.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate BOOLOP 19646b85",
-  "killed_by": "tests/features.py",
-  "old": "        banded = base is None and _whatif_banded(self._away_state)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`banded = base is None or _whatif_banded(self._away_state)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.6e295277.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.6e295277.json
deleted file mode 100644
index 0dafcbf4ce..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.6e295277.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate BOOLOP 6e295277",
-  "killed_by": "tests/features.py",
-  "old": "        if limited and (kept := whatif.limited_answer(held, now)) is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if limited or (kept := whatif.limited_answer(held, now)) is not None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.5f80a8b0.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.5f80a8b0.json
deleted file mode 100644
index a2d213e826..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.5f80a8b0.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate GUARD_OFF 5f80a8b0",
-  "killed_by": "tests/features.py",
-  "old": "        if limited:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.6e295277.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.6e295277.json
deleted file mode 100644
index 99ee505c09..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.6e295277.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate GUARD_OFF 6e295277",
-  "killed_by": "tests/structure.py",
-  "old": "        if limited and (kept := whatif.limited_answer(held, now)) is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.7f751e2c.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.7f751e2c.json
deleted file mode 100644
index d6338770e7..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.7f751e2c.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate GUARD_OFF 7f751e2c",
-  "killed_by": "tests/features.py",
-  "old": "        if result is None:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.b2dd1f84.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.b2dd1f84.json
deleted file mode 100644
index 54f7364aa6..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.b2dd1f84.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate GUARD_OFF b2dd1f84",
-  "killed_by": "tests/features.py",
-  "old": "        if limited:  # the slot is spent when a solve starts (#1448, #1753)",
-  "reason": "Recorded by `mutation_table.py --drain` against 994695e06c4c2b78d6420f82c322188317817f91: GUARD_OFF (`if False:  # the slot is spent when a solve starts (#1448, #1753)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.ddb12f29.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.ddb12f29.json
deleted file mode 100644
index 788ed7cc8e..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.ddb12f29.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate GUARD_OFF ddb12f29",
-  "killed_by": "tests/features.py",
-  "old": "        if base is None:",
-  "reason": "Recorded by hand for R9-EG-B1 (#1736) on the branch worktree, 2026-10-04, because `mutation_table.py --pin-killed` refuses on this machine (tests/features.py's baseline is red for the environment: R9-F2.1 P3, BLAS; green on CI) and the count rule cannot credit this kill against that red baseline: GUARD_OFF (`if False:`) takes tests/features.py from rc=1 failed=2 to rc=1 failed=1 -- the mutant's run aborts the whole file early with an uncaught AttributeError (\"'NoneType' object has no attribute 'config'\", the else-branch dereferencing the absent base record), before the environment-red check prints its FAIL line, so the failing-check count lands BELOW the baseline's. A kill is a red run naming a traceback the unmutated baseline does not carry (the hand rule this ledger's R9-EG-A2 entry set); on CI's green baseline the same abort reads failed=1 > 0 and the lane's own rule counts it. Reproduced at the head by applying the mutant alone and running the suite."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.RETURN_DEL.c0eb7824~2.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.RETURN_DEL.c0eb7824~2.json
deleted file mode 100644
index 862c349716..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.RETURN_DEL.c0eb7824~2.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate RETURN_DEL c0eb7824#2",
-  "killed_by": "tests/features.py",
-  "old": "            return {\"error\": str(err), \"rate_limited\": False}",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_clear_worker_fallback.GUARD_OFF.5e16cb51.json b/tests/mutation_ledger/killed_by/coordinator.py/_clear_worker_fallback.GUARD_OFF.5e16cb51.json
deleted file mode 100644
index ca424f3cc7..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/_clear_worker_fallback.GUARD_OFF.5e16cb51.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_clear_worker_fallback GUARD_OFF 5e16cb51",
-  "killed_by": "tests/features.py",
-  "old": "    if _WORKER_FALLBACK_CAUSES.pop(entry_id, None) is None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against a15e3e33507bde9e566858ce32b2ded840edfa02: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}


## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/boost.py b/custom_components/heatpump_optimizer/boost.py
index 7a54506a89..de0a58ebe8 100644
--- a/custom_components/heatpump_optimizer/boost.py
+++ b/custom_components/heatpump_optimizer/boost.py
@@ -126,8 +126,6 @@ class _BoostCoord(Protocol):
 
     def adopt_action(self, action: CurrentAction) -> None: ...
 
-    async def async_request_refresh(self) -> None: ...
-
 
 @dataclass
 class BoostState:
diff --git a/custom_components/heatpump_optimizer/button.py b/custom_components/heatpump_optimizer/button.py
index 6f94c7ebd8..4925b2a8d0 100644
--- a/custom_components/heatpump_optimizer/button.py
+++ b/custom_components/heatpump_optimizer/button.py
@@ -32,12 +32,13 @@ from homeassistant.helpers.entity_platform import AddEntitiesCallback
 from . import debugger
 from .const import DOMAIN
 from .coordinator import HeatPumpOptimizerConfigEntry, HeatPumpOptimizerCoordinator
+from .solve_gate import async_optimize_now
 from .entity import HeatPumpOptimizerEntity, off_the_action
 
 _LOGGER = logging.getLogger(__name__)
 
 # The coordinator is the serialization point, not this semaphore: the solve
-# guards itself on ``_optimization_running`` and every other press's setter
+# guards itself on its solve gate (``solve_gate``) and every other press's setter
 # is a single write. The optimize-now press must await its solve to answer
 # the tap (#1644, D10-s1-02), and under a held slot that wait queues the
 # other buttons' presses behind it -- the v6.6.12 bug-5 shape, where a
@@ -100,14 +101,13 @@ class ForceOptimizationButton(_OptimizerButtonBase):
         The press answers a tap with the same refusal the
         ``run_optimization`` action raises (#1644, D10-s1-02): reporting
         success behind a dead price feed is the silent failure the action
-        was fixed out of (#294). The solve is awaited here -- the platform
-        takes no parallel-updates slot, so nothing queues behind it -- and
-        the fetch-and-actuate cycle still runs off the press, as before
-        (#1641).
+        was fixed out of (#294). The press awaits the action's own path, one
+        fetch-solve-actuate refresh (D17-s3-01): the platform takes no
+        parallel-updates slot, so nothing queues behind it, which is what
+        took the cycle off the press before (#1641).
         """
         _LOGGER.info("Optimization run requested from the dashboard")
-        reason = await self.coordinator.async_run_optimization()
-        off_the_action(self, self.coordinator.async_request_refresh())
+        reason = await async_optimize_now(self.coordinator)
         if reason == "no_prices":
             # The action's own wording, on the action's own translation
             # keys: services.py owns them and this is its sibling surface.
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index 1f44ffc639..12ea303fcd 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -264,7 +264,7 @@ from . import issues, setpoint_check
 from . import quiet_windows
 from . import rooms, slab_seed
 from . import price_tiles
-from . import whatif
+from . import solve_gate, whatif
 from .pump_mode import ModeCapability
 from .pump_signals import PumpSignals, resistive_carve_out
 from .manual_plan import (
@@ -840,6 +840,15 @@ PROCESS_REPLY_TIMEOUT_S = 1800.0
 # is only bookkeeping, and neither a read the kill did not break nor a child
 # slow to die may hold a solve or Home Assistant's shutdown hostage.
 _SHUTDOWN_LOCK_TIMEOUT_S = 5.0
+#: ``hass.data`` key, set when Home Assistant stops: a solve the reap breaks is
+#: neither a worker fault nor a solve failure (D1-s1-01).
+_WORKER_STOPPING = f"{DOMAIN}_worker_stopping"
+
+
+def _worker_stopping(hass: Any) -> bool:
+    """Whether ``hass`` is stopping, as the worker reap marked it."""
+    data = getattr(hass, "data", None)
+    return isinstance(data, dict) and bool(data.get(_WORKER_STOPPING))
 # How long the reply frame may take to arrive once its first byte has. The
 # worker serialises its whole reply before writing it, so the frame then flows
 # at pipe speed (a 50 MB reply round-trips in about half a second); this only
@@ -1957,6 +1966,7 @@ def async_register_worker_shutdown(hass: HomeAssistant, entry: HeatPumpOptimizer
     """
 
     async def _stop(_event: Event) -> None:
+        hass.data[_WORKER_STOPPING] = True  # before the reap: the solve it breaks is not a fault
         await hass.async_add_executor_job(_shutdown_process_pool)
 
     entry.async_on_unload(
@@ -2049,6 +2059,21 @@ def _read_reply(stdout: Any) -> Any:
     return pickle.load(_frame_reader(fd, _REPLY_FRAME_TIMEOUT_S))
 
 
+def _reap_killed(worker: "subprocess.Popen[bytes]") -> None:
+    """Kill a worker whose stream is in an unknown state, and reap it, bounded.
+
+    Both of ``_run_in_process``'s fault arms hold ``_PROCESS_LOCK`` here: a
+    child the kill does not end at once (one stuck in the kernel on I/O) must
+    not hold every peer's solve behind an unbounded wait (D1-s3-04). Never
+    raises, so the cause the caller re-raises is not masked.
+    """
+    try:
+        worker.kill()
+        worker.wait(timeout=_SHUTDOWN_LOCK_TIMEOUT_S)
+    except Exception:  # noqa: BLE001 - must not mask the caller's cause
+        pass
+
+
 def _run_in_process(fn: Callable[..., Any], args: tuple[Any, ...]) -> Any:
     """Run ``fn(*args)`` in the process worker. ``fn`` must be picklable.
 
@@ -2083,14 +2108,7 @@ def _run_in_process(fn: Callable[..., Any], args: tuple[Any, ...]) -> Any:
                 status, payload = _read_reply(stdout)
             except ProcessWorkerTimeout:
                 _PROCESS_WORKER = None
-                # Bounded too: a child the kill does not end at once (one
-                # stuck in the kernel) must not turn this into the same
-                # unbounded wait one line further down.
-                try:
-                    worker.kill()
-                    worker.wait(timeout=_SHUTDOWN_LOCK_TIMEOUT_S)
-                except Exception:  # noqa: BLE001 - must not mask the timeout
-                    pass
+                _reap_killed(worker)
                 raise
         except ProcessWorkerUnavailable:
             # Already the class the fallback route catches; rewrapping it
@@ -2103,11 +2121,7 @@ def _run_in_process(fn: Callable[..., Any], args: tuple[Any, ...]) -> Any:
                     f"process worker cannot start: {err}"
                 ) from err
             rc = worker.poll()
-            try:  # a no-op on a child poll() has already reaped
-                worker.kill()
-                worker.wait()
-            except Exception:  # noqa: BLE001 - must not mask the cause
-                pass
+            _reap_killed(worker)  # a no-op on a child poll() has already reaped
             raise ProcessWorkerUnavailable(
                 f"process worker exited rc={rc}: {err}"
             ) from err
@@ -2259,8 +2273,9 @@ def _clear_worker_fallback(hass: HomeAssistant, entry_id: Any = None) -> None:
     success no longer resets entry A's #783 cap or flaps A's notice.
     """
     _reset_worker_fallback_streak(hass, entry_id)
-    if _WORKER_FALLBACK_CAUSES.pop(entry_id, None) is None:
-        return
+    _WORKER_FALLBACK_CAUSES.pop(entry_id, None)
+    # Also when nothing was latched: a notice restored from before a restart
+    # has no cause in this process and would otherwise never clear (D1-s1-01).
     if not _WORKER_FALLBACK_CAUSES:
         ir.async_delete_issue(hass, DOMAIN, "solve_worker_fallback")
 
@@ -2328,6 +2343,8 @@ async def _await_optimize(
             minutes=f"{PROCESS_REPLY_TIMEOUT_S / 60:.0f}",
         )
     except ProcessWorkerUnavailable as err:
+        if _worker_stopping(hass):
+            raise  # the stop killed the worker: no notice, no in-process rerun
         _note_worker_fallback(hass, err, entry_id)
         n = _bump_worker_fallback(hass, entry_id)
         if n > WORKER_FALLBACK_CAP:
@@ -3509,7 +3526,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
     thermal_model = _view("_thermal_model")
     away_state = _view("_away_state")
     mold_floor_series = _view("_mold_floor_series")
-    optimization_running = _view("_optimization_running")
+    optimization_running = property(lambda self: solve_gate.gate_for(self).solving)
     accuracy = _view("_accuracy")
     measured_cop = _view("_measured_cop")
     solve_failures = _view("_solve_failures")
@@ -3752,11 +3769,6 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         self._floor_return_temp: float | None = None
         self._solar_radiation_forecast: list[float] = []
         self._open_meteo: OpenMeteoSolar | None = None
-        # A run takes seconds, so a user tapping the button repeatedly must not
-        # be able to stack solves on top of each other.
-        self._optimization_running: bool = False
-        # #1754: a mid-solve refresh is recorded, not dropped; the finally re-runs it.
-        self._optimization_rerun_requested: bool = False
         # Set by ``async_setup_entry`` -- and by nothing else -- just before the
         # first refresh: that refresh runs inside setup, where a full cold
         # solve stalls the whole instance. Consumed on the next update cycle,
@@ -6084,7 +6096,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
 
             # Run optimization if in auto mode
             if self._mode in (MODE_AUTO, MODE_ECONOMY):
-                await self.async_run_optimization()
+                solve_gate.gate_for(self).reason = await self.async_run_optimization()
             elif self._mode in (MODE_COMFORT, MODE_BOOST, MODE_OFF):
                 boost.adopt_plan(self, self._fixed_mode_action())
 
@@ -6156,6 +6168,14 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             _raise_update_failed("update_failed", f"Error updating data: {err}", err, error=str(err))
         finally:
             self._refresh_task = None
+            if solve_gate.take_trailing(solve_gate.gate_for(self)) and not self._entry_released:
+                self._spawn(self.async_request_refresh())  # lands once the debouncer is free
+
+    async def async_request_refresh(self) -> None:
+        """Request a refresh; one landing on a running solve or refresh follows it (D1-s1-03)."""
+        if not solve_gate.absorb_request(solve_gate.gate_for(self), self._refresh_task is not None):
+            await super().async_request_refresh()
+
     async def _async_first_refresh_light(self) -> Payload:
         """The setup-time refresh: publish something valid without solving.
 
@@ -6359,13 +6379,11 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         ctx = getattr(self, "_ctx", self)
         _LOGGER.info("Running heat pump optimization (predictive MPC)")
 
-        if self._optimization_running:
-            # #1754: record the re-run; the in-flight solve's finally honours it.
-            self._optimization_rerun_requested = True
+        if not solve_gate.begin_solve(solve_gate.gate_for(self)):
+            # #1754: a re-run is recorded; the in-flight solve's finally honours it.
             _LOGGER.debug("An optimization is already in flight; recording a re-run")
             return None
 
-        self._optimization_running = True
         entry_mode = self._mode
         # Announce the flip: the Optimize Now button disables itself off this
         # flag, and without a listener update the change is invisible until
@@ -6457,8 +6475,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
 
             self._optimization_result = replace(result, solve_band=record.band.as_dict())
             self._last_optimization = dt_util.now()
-            if self._solve_failures >= SOLVE_FAILURE_ISSUE_COUNT:
-                ir.async_delete_issue(self.hass, DOMAIN, "solve_failures")
+            ir.async_delete_issue(self.hass, DOMAIN, "solve_failures")  # a restored one too
             self._solve_failures = 0
             log_held(self, "solve_failure", False)  # a later failure spell warns again
             # T5 #16: file this plan's promises at each lead bucket, to be
@@ -6511,20 +6528,17 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             return None
 
         except Exception as err:
+            if _worker_stopping(self.hass):
+                return "shutdown"  # the stop killed the worker; not a solve failure
             _note_solve_failure(self, err)
             return "solve_failed"
         finally:
-            self._optimization_running = False
+            rerun = solve_gate.end_solve(solve_gate.gate_for(self))
             self.async_update_listeners()
-            # #1754: honour a mid-solve refresh as ONE re-run, now that the flag
-            # is clear so it is not guarded out. Cleared first, so this recurses
-            # only if another refresh arrives during the re-run (a rate the
-            # debouncer bounds); skipped once the entry is released, and
-            # dropped where a fixed mode superseded the solve (D1-s1-02).
-            if self._optimization_rerun_requested and not self._entry_released:
-                self._optimization_rerun_requested = False
-                if not _mode_superseded(entry_mode, self._mode):
-                    await self.async_run_optimization()
+            # #1754: a request during the solve re-runs it ONCE; skipped once the
+            # entry is released, dropped where a fixed mode superseded it (D1-s1-02).
+            if rerun and not self._entry_released and not _mode_superseded(entry_mode, self._mode):
+                await self.async_run_optimization()
     async def async_set_mode(self, mode: str, *, refresh: bool = True) -> None:
         """Set the operation mode, once a startup load has landed (R6)."""
         await self._accuracy_store.async_wait_for_read()
@@ -8995,16 +9009,13 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             and (dt_util.as_utc(now) - dt_util.as_utc(self._fuse_advisor_at)
             ).total_seconds() < 7 * 24 * 3600.0
             and self._fuse_advisor.get("month") == month_key(now)
-        ):
+        ) or not solve_gate.admit_background(solve_gate.gate_for(self)):  # D9-s1-02
             return
 
         candidate_kw = self.effective_config.fuse_kw_at(smaller)
         baseline_now = float(self._baseline_house_load(1)[0])
         cap_kw = max(0.0, candidate_kw - baseline_now)
-        # Solve on the card's harness, never on its budget (#1753): with
-        # ``limited=False`` this neither spends the what-if's rate-limit
-        # slot nor writes its answer into the card cache.
-        simulated = await self.async_simulate(
+        simulated = await self.async_simulate(  # the background path (#1753)
             {"power_cap_kw": cap_kw}, limited=False, base=record, steady=True
         )
         echoed = (simulated.get("overrides") or {}).get("power_cap_kw")
@@ -10686,7 +10697,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
                 "No settled interval to diagnose yet — one full "
                 "optimization interval must pass first"
             )
-        await self.async_request_refresh()
+        if self.data is not None:  # D9-s1-01: publish the diagnosis, no cycle (``async_set_updated_data`` re-arms the interval)
+            self.data = {**self.data, "insight": self._insight_view()}
+            self.async_update_listeners()
         return report
 
     async def _maybe_refresh_price_tile(self, record: SolveRecord) -> None:
@@ -10694,10 +10707,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
 
         Rotating: one extra solve for a degree tile, three for the cap tile,
         whose steady figure (#2257) ``price_tiles.take`` holds to its own
-        clock. Through ``async_simulate``'s own solve path and executor, on
-        the card's harness but never on its budget (``limited=False``, #1753):
-        no rate-limit slot of the user what-if spent and no card cache written,
-        so an overlapping card drag is answered fresh and keeps both.
+        clock. ``async_simulate``'s background path (``limited=False``, #1753),
+        and only when the solve's one background what-if is free (D9-s1-02).
         """
         if not getattr(self, "_ctx", self)._config.price_tiles_enabled:
             # Gate off means gone: stale what-if money left published
@@ -10705,7 +10716,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             price_tiles.book(self).clear()
             return
         specs = price_tiles.specs(record.config, record.params.max_electrical_power)
-        if (spec := price_tiles.take(price_tiles.rotation(self), specs, dt_util.now())) is None:
+        if not solve_gate.admit_background(solve_gate.gate_for(self)) or (
+                spec := price_tiles.take(price_tiles.rotation(self), specs, dt_util.now())) is None:
             return
         name, overrides = spec
         try:
@@ -11188,7 +11200,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         * it is **rate-limited** for user callers, because a full solve is
           seconds of CPU and dragging a slider would otherwise trigger one
           per pixel. The slot is spent when a solve starts, so the failing
-          arm is limited (#1448). ``limited=False`` is the background
+          arm is limited (#1448); of the asks overlapping a solve only the
+          newest then solves (``solve_gate.user_slot``). ``limited=False``: the background
           callers' path — the price tile and the fuse advisor (#1753): it
           neither reads nor writes the user limiter or the card cache, so
           a card drag overlapping a background solve is answered fresh and
@@ -11202,99 +11215,101 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         solves, off the loop and outside the #783 streak, never a seed and
         never the plan (``whatif.steady_pair``).
         """
-        ctx = getattr(self, "_ctx", self)
-        now = dt_util.now()
         held = whatif.state_for(self)
-        if limited and (kept := whatif.limited_answer(held, now)) is not None:
+        if limited and (kept := whatif.limited_answer(held, dt_util.now())) is not None:
             return kept
+        async with solve_gate.user_slot(solve_gate.gate_for(self), limited) as admitted:
+            if not admitted:  # D9-s1-03: a newer ask overtook this one while it waited
+                return {**held.answer, "rate_limited": True}
+            ctx = getattr(self, "_ctx", self)
+            now = dt_util.now()
+            result = self._optimization_result
+            if result is None:
+                return {"error": "no_plan", "rate_limited": False}
 
-        result = self._optimization_result
-        if result is None:
-            return {"error": "no_plan", "rate_limited": False}
-
-        # Same shared-instant discipline as the live solve: the shadow
-        # solve's anchor and its arrays must not straddle a quarter
-        # boundary, or its predicted_cost stops being comparable to the
-        # plan it is differenced against below.
-        horizon = self._forecast_arrays(now)
-        if len(horizon.prices) < 4:
-            return {"error": "no_prices", "rate_limited": False}
-
-        banded = base is None and _whatif_banded(self._away_state)
-        if base is None:
-            config, params, state = self._solve_hubs(len(horizon.prices), banded=banded)
-        else:
-            config, params, state = base.config, base.params, base.inputs.state
-        # One snap for slot stamps and the shadow solve (#463).
-        solve_at = plan_step_start(now)
+            # Same shared-instant discipline as the live solve: the shadow
+            # solve's anchor and its arrays must not straddle a quarter
+            # boundary, or its predicted_cost stops being comparable to the
+            # plan it is differenced against below.
+            horizon = self._forecast_arrays(now)
+            if len(horizon.prices) < 4:
+                return {"error": "no_prices", "rate_limited": False}
 
-        def _scratch(asked: Mapping[str, Any], held_start: bool = False) -> tuple[HeatPumpOptimizer, SolveInputs, float]:
-            return self._whatif_solve(asked, config, params, state, horizon, solve_at, held_start)
+            banded = base is None and _whatif_banded(self._away_state)
+            if base is None:
+                config, params, state = self._solve_hubs(len(horizon.prices), banded=banded)
+            else:
+                config, params, state = base.config, base.params, base.inputs.state
+            # One snap for slot stamps and the shadow solve (#463).
+            solve_at = plan_step_start(now)
 
-        try:
-            scratch, inputs, wood_sek = _scratch(overrides)
-        except whatif.Refused as err:
-            return {"error": str(err), "rate_limited": False}
-        if limited:  # the slot is spent when a solve starts (#1448, #1753)
-            held.last_at = now
-        try:
-            _CURRENT_ENTRY_ID.set(self.entry.entry_id)  # #1755: per-entry fallback key
-            simulated = await _await_optimize(self.hass, scratch, inputs)
-        except Exception as err:  # noqa: BLE001 - a what-if must never break ops
-            _LOGGER.warning("What-if simulation failed: %s", err)
-            return {"error": str(err), "rate_limited": False}
-
-        async def _held_solve(asked: Mapping[str, Any]) -> Any:
-            return await _await_off_loop(self.hass, optimize_in_process, *_scratch(asked, True)[:2])
-
-        horizon_hours, dt_hours = ctx._opt_config.horizon_hours, ctx._opt_config.dt_hours
-        # A schedule change is priced by the thermostat's day energy on both
-        # sides, at this instant on these arrays; anything else by the pair.
-        days = whatif.schedule_days(_scratch({})[:2], (scratch, inputs)) if steady else None
-        pair = await whatif.steady_pair(
-            held, result if base is None else base, (solve_at, state, banded), _held_solve, overrides,
-        ) if steady and days is None else None
-        figure = {} if days is None else price_tiles.schedule_figure(
-            *days, float(np.mean(inputs.forecast.prices)), wood_sek, horizon_hours,
-            price_tiles.realised_price(simulated, dt_hours))
-        delta = simulated.predicted_cost - result.predicted_cost + wood_sek
-
-        payload = {
-            "baseline_cost": round(result.predicted_cost, 2),
-            "simulated_cost": round(simulated.predicted_cost + wood_sek, 2),
-            "cost_delta": round(delta, 2),
-            **({"wood_sek": round(wood_sek, 2)} if "wood_slots" in overrides else {}),
-            **price_tiles.monthly_deltas(result, simulated, wood_sek, horizon_hours, pair),
-            **figure,
-            # T2: present only when the what-if capped power — the worst
-            # comfort-floor shortfall that cap forced, 0.0 when feasible.
-            **(
-                {
-                    "power_cap_breach_c": simulated.predictive_info.get(
-                        "power_cap_breach_c", 0.0
-                    )
-                }
-                if "power_cap_kw" in overrides and simulated.predictive_info
-                else {}
-            ),
-            "savings_percentage": round(simulated.savings_percentage, 1),
-            "min_room_temperature": _sim_coldest(simulated),
-            # The comfort consequence, alongside the money. A cheaper plan that
-            # is colder or leaves the tank short is not the same trade, and a
-            # simulator that reported only the saving would be inviting the
-            # user to make exactly that mistake.
-            "baseline_min_room_temperature": _sim_coldest(result),
-            "min_dhw_temperature": _sim_dhw_low(simulated),
-            "baseline_min_dhw_temperature": _sim_dhw_low(result),
-            **whatif.slot_counts(simulated, dt_hours),
-            "compressor_starts": simulated.compressor_starts,
-            "projected_peak_kw": simulated.projected_peak_kw,
-            "overrides": overrides,
-            "rate_limited": False,
-        }
-        if limited:
-            held.answer = payload
-        return payload
+            def _scratch(asked: Mapping[str, Any], held_start: bool = False) -> tuple[HeatPumpOptimizer, SolveInputs, float]:
+                return self._whatif_solve(asked, config, params, state, horizon, solve_at, held_start)
+
+            try:
+                scratch, inputs, wood_sek = _scratch(overrides)
+            except whatif.Refused as err:
+                return {"error": str(err), "rate_limited": False}
+            if limited:  # the slot is spent when a solve starts (#1448, #1753)
+                held.last_at = now
+            try:
+                _CURRENT_ENTRY_ID.set(self.entry.entry_id)  # #1755: per-entry fallback key
+                simulated = await _await_optimize(self.hass, scratch, inputs)
+            except Exception as err:  # noqa: BLE001 - a what-if must never break ops
+                _LOGGER.warning("What-if simulation failed: %s", err)
+                return {"error": str(err), "rate_limited": False}
+
+            async def _held_solve(asked: Mapping[str, Any]) -> Any:
+                return await _await_off_loop(self.hass, optimize_in_process, *_scratch(asked, True)[:2])
+
+            horizon_hours, dt_hours = ctx._opt_config.horizon_hours, ctx._opt_config.dt_hours
+            # A schedule change is priced by the thermostat's day energy on both
+            # sides, at this instant on these arrays; anything else by the pair.
+            days = whatif.schedule_days(*await _await_off_loop(self.hass, whatif.reference_days, _scratch({})[:2], (scratch, inputs))) if steady else None  # D9-s1-04
+            pair = await whatif.steady_pair(
+                held, result if base is None else base, (solve_at, state, banded), _held_solve, overrides,
+            ) if steady and days is None else None
+            figure = {} if days is None else price_tiles.schedule_figure(
+                *days, float(np.mean(inputs.forecast.prices)), wood_sek, horizon_hours,
+                price_tiles.realised_price(simulated, dt_hours))
+            delta = simulated.predicted_cost - result.predicted_cost + wood_sek
+
+            payload = {
+                "baseline_cost": round(result.predicted_cost, 2),
+                "simulated_cost": round(simulated.predicted_cost + wood_sek, 2),
+                "cost_delta": round(delta, 2),
+                **({"wood_sek": round(wood_sek, 2)} if "wood_slots" in overrides else {}),
+                **price_tiles.monthly_deltas(result, simulated, wood_sek, horizon_hours, pair),
+                **figure,
+                # T2: present only when the what-if capped power — the worst
+                # comfort-floor shortfall that cap forced, 0.0 when feasible.
+                **(
+                    {
+                        "power_cap_breach_c": simulated.predictive_info.get(
+                            "power_cap_breach_c", 0.0
+                        )
+                    }
+                    if "power_cap_kw" in overrides and simulated.predictive_info
+                    else {}
+                ),
+                "savings_percentage": round(simulated.savings_percentage, 1),
+                "min_room_temperature": _sim_coldest(simulated),
+                # The comfort consequence, alongside the money. A cheaper plan that
+                # is colder or leaves the tank short is not the same trade, and a
+                # simulator that reported only the saving would be inviting the
+                # user to make exactly that mistake.
+                "baseline_min_room_temperature": _sim_coldest(result),
+                "min_dhw_temperature": _sim_dhw_low(simulated),
+                "baseline_min_dhw_temperature": _sim_dhw_low(result),
+                **whatif.slot_counts(simulated, dt_hours),
+                "compressor_starts": simulated.compressor_starts,
+                "projected_peak_kw": simulated.projected_peak_kw,
+                "overrides": overrides,
+                "rate_limited": False,
+            }
+            if limited:
+                held.answer = payload
+            return payload
 
     def _whatif_solve(
         self, overrides: Mapping[str, Any], config: OptimizationConfig, params: ThermalParameters,
diff --git a/custom_components/heatpump_optimizer/services.py b/custom_components/heatpump_optimizer/services.py
index 238fb48c13..6f41f2a72f 100644
--- a/custom_components/heatpump_optimizer/services.py
+++ b/custom_components/heatpump_optimizer/services.py
@@ -92,6 +92,7 @@ from .coordinator import (
     async_adopt_heat_loss_refit,
     async_factory_reset,
 )
+from .solve_gate import async_optimize_now
 from .dhw_schedule import (
     DHWWindowError,
     format_weekly_windows,
@@ -591,6 +592,8 @@ def _loaded_coordinators(
 async def handle_run_optimization(hass: HomeAssistant, call: ServiceCall) -> None:
     """Handle the run_optimization service call.
 
+    One refresh per entry, the Optimize Now button's path: prices and weather
+    are fetched, then the plan is solved, actuated and published (D17-s3-01).
     The coordinator reports a reason code when the solve could not run
     rather than raising — its own ``except Exception`` fence (which feeds
     the repair issue) would swallow one — so a run that quietly did not
@@ -601,7 +604,7 @@ async def handle_run_optimization(hass: HomeAssistant, call: ServiceCall) -> Non
     _LOGGER.info("Manual optimization triggered via service call")
     not_run: dict[str, str] = {}
     for entry_id, coord in _loaded_coordinators(hass):
-        reason = await coord.async_run_optimization()
+        reason = await async_optimize_now(coord)
         if reason is not None:
             not_run[entry_id] = reason
     if not_run:
diff --git a/custom_components/heatpump_optimizer/solve_gate.py b/custom_components/heatpump_optimizer/solve_gate.py
new file mode 100644
index 0000000000..819d5b3f64
--- /dev/null
+++ b/custom_components/heatpump_optimizer/solve_gate.py
@@ -0,0 +1,164 @@
+"""When a solve runs: the cycle's one in-flight guard and its budgets.
+
+The coordinator keeps the solve paths; this module owns the questions every
+one of them asks before it starts, in a per-coordinator side table
+(``boost.py``'s and ``whatif.py``'s discipline), so the coordinator class
+holds no state it never computes with.
+
+THE MAIN SOLVE. One in flight. A request that lands while it runs is recorded
+as ONE re-run the in-flight solve's ``finally`` honours (#1754), so an input
+changed mid-solve is actuated in the cycle that is running, not dropped until
+the next. A request that lands while a refresh is fetching or actuating but
+not solving is recorded as ONE trailing refresh, scheduled when that refresh
+ends: Home Assistant's debouncer drops a call made while it executes, which
+left a write made then unplanned until the next interval (D1-s1-03).
+
+THE BACKGROUND BUDGET. One background what-if (the fuse advisor, a price
+tile) per main solve, so a cycle never stacks them (D9-s1-02). The debug
+collection's finalize self-test is exempt: it runs once per finalize, never
+per cycle, and exists to answer.
+
+THE USER'S SLOT. One user what-if solving and the newest one waiting: an ask
+overtaken by a newer one while it waits is answered from the held answer,
+unsolved (D9-s1-03), so a burst of K asks solves at most two.
+
+THE RUN-NOW PATH. The Optimize Now button and the ``run_optimization``
+action are one refresh, fetch to publish (D17-s3-01): ``async_optimize_now``.
+"""
+from __future__ import annotations
+
+import asyncio
+from collections.abc import AsyncIterator
+from contextlib import asynccontextmanager
+from dataclasses import dataclass, field
+from typing import Any
+from weakref import WeakKeyDictionary
+
+from .const import MODE_AUTO, MODE_ECONOMY
+
+
+@dataclass
+class SolveGate:
+    """One coordinator's answer to "may this solve start now"."""
+
+    #: A main solve is in flight.
+    solving: bool = False
+    #: A request landed during that solve; it re-runs once (#1754).
+    rerun: bool = False
+    #: A request landed during a refresh that was not solving; one refresh follows it.
+    trailing: bool = False
+    #: The current main solve's one background what-if has been spent.
+    background_taken: bool = False
+    #: The last refresh's solve answer: None ran, else its reason code.
+    reason: str | None = None
+    #: A user what-if is solving.
+    user_running: bool = False
+    #: The newest waiting user ask's ticket; a waiter holding an older one is superseded.
+    user_waiting: int = 0
+    #: Set when the user what-if in flight ends.
+    user_freed: asyncio.Event = field(default_factory=asyncio.Event, repr=False)
+
+
+_GATES: WeakKeyDictionary[Any, SolveGate] = WeakKeyDictionary()
+
+
+def gate_for(owner: Any) -> SolveGate:
+    """``owner``'s gate, created on first use."""
+    return _GATES.setdefault(owner, SolveGate())
+
+
+def absorb_request(gate: SolveGate, refreshing: bool) -> bool:
+    """Whether a refresh request is absorbed by work already running.
+
+    Solving: the in-flight solve re-runs once. Refreshing without a solve:
+    one refresh trails it. Otherwise False, and the caller requests as usual.
+    """
+    if gate.solving:
+        gate.rerun = True
+        return True
+    if refreshing:
+        gate.trailing = True
+        return True
+    return False
+
+
+def begin_solve(gate: SolveGate) -> bool:
+    """Start a main solve; False, with a re-run recorded, when one is in flight.
+
+    A started solve opens a fresh background budget.
+    """
+    if absorb_request(gate, False):
+        return False
+    gate.solving = True
+    gate.background_taken = False
+    return True
+
+
+def end_solve(gate: SolveGate) -> bool:
+    """End the main solve; whether a re-run was recorded during it (taken)."""
+    gate.solving = False
+    rerun, gate.rerun = gate.rerun, False
+    return rerun
+
+
+def take_trailing(gate: SolveGate) -> bool:
+    """Whether a refresh was requested during the one ending (taken)."""
+    trailing, gate.trailing = gate.trailing, False
+    return trailing
+
+
+def admit_background(gate: SolveGate) -> bool:
+    """Whether a background what-if may run: once per main solve.
+
+    Asked before the caller chooses its work, so a denied price tile moves no rotation.
+    """
+    if gate.background_taken:
+        return False
+    gate.background_taken = True
+    return True
+
+
+@asynccontextmanager
+async def user_slot(gate: SolveGate, user: bool = True) -> AsyncIterator[bool]:
+    """Wait for the user what-if in flight; yield whether this ask may solve.
+
+    False when a newer ask arrived while this one waited: the newest supersedes.
+    The slot is held while the body runs and freed on any exit. A background
+    caller (``user`` False) neither waits nor holds it (#1753): yields True.
+    """
+    if not user:
+        yield True
+        return
+    freed = gate.user_freed
+    gate.user_waiting += 1
+    ticket = gate.user_waiting
+    while gate.user_running:
+        freed.clear()
+        await freed.wait()
+    if ticket != gate.user_waiting:
+        yield False
+        return
+    gate.user_running = True
+    try:
+        yield True
+    finally:
+        gate.user_running = False
+        freed.set()
+
+
+async def async_optimize_now(coord: Any) -> str | None:
+    """Optimize Now and ``run_optimization``: one fetch-solve-actuate-publish refresh (D17-s3-01).
+
+    A fixed mode's refresh solves nothing, so its private plan is solved first.
+    None when the solve ran, else why not: the solve's reason, or a failed
+    refresh's (``"no_prices"`` when no published price covers now).
+    """
+    gate = gate_for(coord)
+    gate.reason = None
+    if coord.mode not in (MODE_AUTO, MODE_ECONOMY):
+        gate.reason = await coord.async_run_optimization()
+    await coord.async_refresh()
+    if coord.last_update_success:
+        return gate.reason
+    key = getattr(coord.last_exception, "translation_key", None)
+    return "no_prices" if key == "tibber_fetch_failed" else "solve_failed"
diff --git a/custom_components/heatpump_optimizer/strings.json b/custom_components/heatpump_optimizer/strings.json
index 50adf9c1e2..ab35974351 100644
--- a/custom_components/heatpump_optimizer/strings.json
+++ b/custom_components/heatpump_optimizer/strings.json
@@ -2290,7 +2290,7 @@
   "services": {
     "run_optimization": {
       "name": "Run Optimization",
-      "description": "Manually trigger the heat pump cost optimization. This recomputes the optimal heat pump schedule for the next 24 hours from the electricity prices and weather forecast already loaded (it does not fetch new ones) using predictive MPC with solar/wind/rain anticipation and DHW coordination. The call fails with an error when the optimization cannot run — for example fewer than four electricity price steps are available, or the solve failed — instead of returning as if a new plan had been computed."
+      "description": "Manually trigger the heat pump cost optimization. This fetches the electricity prices and weather forecast, then recomputes the optimal heat pump schedule for the next 24 hours, actuates it and publishes it, the same run as the Optimize Now button, using predictive MPC with solar/wind/rain anticipation and DHW coordination. The call fails with an error when the optimization cannot run — for example fewer than four electricity price steps are available, or the solve failed — instead of returning as if a new plan had been computed."
     },
     "set_away": {
       "name": "Set Away",
diff --git a/custom_components/heatpump_optimizer/translations/de.json b/custom_components/heatpump_optimizer/translations/de.json
index acfdce719d..6ddaf6923f 100644
--- a/custom_components/heatpump_optimizer/translations/de.json
+++ b/custom_components/heatpump_optimizer/translations/de.json
@@ -2290,7 +2290,7 @@
   "services": {
     "run_optimization": {
       "name": "Optimierung ausführen",
-      "description": "Startet die Kostenoptimierung der Wärmepumpe manuell. Dabei wird der optimale Wärmepumpen-Zeitplan für die nächsten 24 Stunden aus den bereits geladenen Strompreisen und der Wettervorhersage neu berechnet (neue werden nicht abgerufen), mit prädiktivem MPC unter Berücksichtigung von Sonne, Wind und Regen sowie Abstimmung mit der Warmwasserbereitung. Kann die Optimierung nicht laufen, schlägt der Aufruf mit einem Fehler fehl, zum Beispiel wenn weniger als vier Strompreisschritte vorliegen oder die Lösung fehlgeschlagen ist, statt so zurückzukehren, als wäre ein neuer Plan berechnet worden."
+      "description": "Startet die Kostenoptimierung der Wärmepumpe manuell. Dabei werden Strompreise und Wettervorhersage abgerufen, dann wird der optimale Wärmepumpen-Zeitplan für die nächsten 24 Stunden neu berechnet, angewendet und veröffentlicht, derselbe Lauf wie die Schaltfläche „Jetzt optimieren“, mit prädiktivem MPC unter Berücksichtigung von Sonne, Wind und Regen sowie Abstimmung mit der Warmwasserbereitung. Kann die Optimierung nicht laufen, schlägt der Aufruf mit einem Fehler fehl, zum Beispiel wenn weniger als vier Strompreisschritte vorliegen oder die Lösung fehlgeschlagen ist, statt so zurückzukehren, als wäre ein neuer Plan berechnet worden."
     },
     "set_away": {
       "name": "Abwesenheit setzen",
diff --git a/custom_components/heatpump_optimizer/translations/en.json b/custom_components/heatpump_optimizer/translations/en.json
index 50adf9c1e2..ab35974351 100644
--- a/custom_components/heatpump_optimizer/translations/en.json
+++ b/custom_components/heatpump_optimizer/translations/en.json
@@ -2290,7 +2290,7 @@
   "services": {
     "run_optimization": {
       "name": "Run Optimization",
-      "description": "Manually trigger the heat pump cost optimization. This recomputes the optimal heat pump schedule for the next 24 hours from the electricity prices and weather forecast already loaded (it does not fetch new ones) using predictive MPC with solar/wind/rain anticipation and DHW coordination. The call fails with an error when the optimization cannot run — for example fewer than four electricity price steps are available, or the solve failed — instead of returning as if a new plan had been computed."
+      "description": "Manually trigger the heat pump cost optimization. This fetches the electricity prices and weather forecast, then recomputes the optimal heat pump schedule for the next 24 hours, actuates it and publishes it, the same run as the Optimize Now button, using predictive MPC with solar/wind/rain anticipation and DHW coordination. The call fails with an error when the optimization cannot run — for example fewer than four electricity price steps are available, or the solve failed — instead of returning as if a new plan had been computed."
     },
     "set_away": {
       "name": "Set Away",
diff --git a/custom_components/heatpump_optimizer/translations/sv.json b/custom_components/heatpump_optimizer/translations/sv.json
index 2131630df4..b97827bdf7 100644
--- a/custom_components/heatpump_optimizer/translations/sv.json
+++ b/custom_components/heatpump_optimizer/translations/sv.json
@@ -2290,7 +2290,7 @@
   "services": {
     "run_optimization": {
       "name": "Kör optimering",
-      "description": "Starta kostnadsoptimeringen för värmepumpen manuellt. Integrationen beräknar om det billigaste körschemat för de kommande 24 timmarna utifrån de elpriser och den väderprognos som redan är inlästa (nya hämtas inte) med prediktiv MPC, med hänsyn till sol, vind och regn samt samordning med varmvattnet. Anropet svarar med ett fel när optimeringen inte kan köras — till exempel när färre än fyra prissteg finns tillgängliga, eller när lösningen misslyckades — i stället för att svara som om en ny plan hade beräknats."
+      "description": "Starta kostnadsoptimeringen för värmepumpen manuellt. Integrationen hämtar elpriser och väderprognos och beräknar sedan om det billigaste körschemat för de kommande 24 timmarna, styr efter det och publicerar det, samma körning som knappen Optimera nu, med prediktiv MPC, med hänsyn till sol, vind och regn samt samordning med varmvattnet. Anropet svarar med ett fel när optimeringen inte kan köras — till exempel när färre än fyra prissteg finns tillgängliga, eller när lösningen misslyckades — i stället för att svara som om en ny plan hade beräknats."
     },
     "set_away": {
       "name": "Ställ in bortaläge",
diff --git a/custom_components/heatpump_optimizer/whatif.py b/custom_components/heatpump_optimizer/whatif.py
index 2d19e2f255..532014a287 100644
--- a/custom_components/heatpump_optimizer/whatif.py
+++ b/custom_components/heatpump_optimizer/whatif.py
@@ -173,19 +173,27 @@ def slot_counts(simulated: Any, dt_hours: float) -> dict[str, int]:
     }
 
 
+def reference_days(live: tuple[Any, Any], sim: tuple[Any, Any]) -> tuple[Any, Any]:
+    """Each side's ``reference_day``: its setpoints over the week ahead and its day energy.
+
+    Each side is an unsolved optimizer and its inputs, built at one instant
+    from one set of arrays. Model work, shipped off the loop (P10, D9-s1-04).
+    """
+    return tuple(o.reference_day(i) for o, i in (live, sim))
+
+
 def schedule_days(live: tuple[Any, Any], sim: tuple[Any, Any]) -> tuple[float, float] | None:
     """The live and the what-if side's day energy when the ask moves a comfort target; else None.
 
-    Each side is an unsolved optimizer and its inputs, built at one instant
-    from one set of arrays, and ``reference_day`` gives each one's setpoints
-    over the week ahead and the energy a thermostat holding them draws on its
-    average day. The branch is taken on
+    ``live`` and ``sim`` are each side's ``reference_day``: the setpoints a
+    thermostat holds over the week ahead and the energy it draws holding them
+    on its average day. The branch is taken on
     the setpoints, element by element, never on the energies: two schedules
     a thermostat cannot tell apart (held at the pump's maximum both ways) are
     still a schedule ask, whose figure is then 0, and an ask that moves no
     setpoint reads the pair whatever its energies.
     """
-    (live_targets, live_kwh), (sim_targets, sim_kwh) = (o.reference_day(i) for o, i in (live, sim))
+    (live_targets, live_kwh), (sim_targets, sim_kwh) = live, sim
     return None if live_targets == sim_targets else (live_kwh, sim_kwh)
 
 
diff --git a/dev/audit/harnesses/r10_registry_leak.py b/dev/audit/harnesses/r10_registry_leak.py
index a5e21b6b1d..681c6b90d5 100644
--- a/dev/audit/harnesses/r10_registry_leak.py
+++ b/dev/audit/harnesses/r10_registry_leak.py
@@ -157,7 +157,7 @@ async def main():
     for _ in range(N):
         assert await ha_setup_entry(integration, hass, entry)
         c = entry.runtime_data
-        ok = await wait_for(lambda: c._optimization_result is not None and not c._optimization_running)
+        ok = await wait_for(lambda: c._optimization_result is not None and not c.optimization_running)
         assert ok, "cycle did not complete"
         await asyncio.sleep(0.05)
         await ha_unload_entry(integration, hass, entry)
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index aa4b8d93c5..5483fa64a7 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -283,7 +283,7 @@
   "source": "docs/architecture.md",
   "claim": "45 modules",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=96 measured=96",
+  "result": "documented=97 measured=97",
   "verdict": "true",
   "truth": ""
  },
@@ -292,7 +292,7 @@
   "source": "docs/architecture.md",
   "claim": "the module map is the package's module list",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "on disk=96, listed=96, missing=[], phantom=[]",
+  "result": "on disk=97, listed=97, missing=[], phantom=[]",
   "verdict": "true",
   "truth": "0 modules are absent from the map: "
  },
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index 06602a3ea7..d6175bda36 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -35,8 +35,8 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C29 | `docs/architecture.md:module map` | config_flow.py -- Setup flow plus 25 option pages behind two menus | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=25 measured=25 | **true** |  |
 | C30 | `docs/configuration.md` | every documented Default (97 rows) is the default the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 97 compared, mismatches=[] | **true** |  |
 | C31 | `docs/configuration.md` | every documented Range (104 rows) is the NumberSelector min/max the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 104 compared, mismatches=[] | **true** |  |
-| C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=96 measured=96 | **true** |  |
-| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=96, listed=96, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
+| C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=97 measured=97 | **true** |  |
+| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=97, listed=97, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
 | C34 | `docs/architecture.md:The Home Assistant boundary` | the boundary sentence's count of modules importing `homeassistant` at module level | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=33 measured=33 | **true** |  |
 | C35 | `docs/architecture.md:The Home Assistant boundary` | the named modules are the complete set of module-level importers | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | named=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], measured=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], unnamed=[] | **true** | unnamed module-level importers:  |
 | C36 | `docs/architecture.md:The Home Assistant boundary` | everything outside the named set is free of homeassistant, so each module can be driven with no Home Assistant running | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 0 modules outside the named set import homeassistant at module level | **true** | modules outside the named set import homeassistant at module level and cannot be imported without it:  |
diff --git a/dev/audit/rounds/round4/D6/claims.py b/dev/audit/rounds/round4/D6/claims.py
index 8013697404..11b03e3f0f 100644
--- a/dev/audit/rounds/round4/D6/claims.py
+++ b/dev/audit/rounds/round4/D6/claims.py
@@ -91,7 +91,7 @@ against a document that is CORRECT.
                                          Range row on the expert thermal-model
                                          table; 101 with R10-USER-DOCS-FINAL's
                                          per-field rows on the options pages)
-    RESULT arch_modules_on_disk=96       (95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 85 until R10-WHY-NOW-WIDGET's slot_drivers.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
+    RESULT arch_modules_on_disk=97       (96 until R11-SEAM-cycle-solve's solve_gate.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 85 until R10-WHY-NOW-WIDGET's slot_drivers.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
                                          66 until R9 F2.5's batchmath.py;
                                          65 until #1588's pump_arbiter.py; 64
                                          until #1408's store.py;
@@ -117,7 +117,7 @@ against a document that is CORRECT.
                                          bytes of, so nothing compared these
                                          numbers to a run between 2026-09-17
                                          and then)
-    RESULT arch_map_listed=96            (95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
+    RESULT arch_map_listed=97            (96 until R11-SEAM-cycle-solve's solve_gate.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
                                          66 until R9 F2.5's batchmath.py;
                                          was 45; 11 were missing; 66 with
                                          #1588's pump_arbiter.py added to
diff --git a/dev/programme/delivery/3738.md b/dev/programme/delivery/3738.md
new file mode 100644
index 0000000000..e2e6a36205
--- /dev/null
+++ b/dev/programme/delivery/3738.md
@@ -0,0 +1 @@
+- [#3738](https://github.com/tvofi/heatpump_optimizer/pull/3738) — **open**, R11-SEAM-cycle-solve: cycle solve (R11-SEAM-cycle-solve)
diff --git a/docs/architecture.md b/docs/architecture.md
index e0e2b86045..61b21354b3 100644
--- a/docs/architecture.md
+++ b/docs/architecture.md
@@ -5,7 +5,7 @@ integration does rather than how it is built, start with
 [how-it-works.md](how-it-works.md).
 
 The shape is a thin Home Assistant layer wrapped around a much larger core that
-knows nothing about Home Assistant: 96 modules, of which 33 import the
+knows nothing about Home Assistant: 97 modules, of which 33 import the
 `homeassistant` package at module level, one more touches it inside a single
 function, and the rest take numbers in and give numbers back. The glue reads
 entity states, writes actuators and persists learned state. Keeping those two
@@ -269,6 +269,7 @@ custom_components/heatpump_optimizer/
 │                         #   copy for that bundle and the repository's export
 ├── diagnostics.py        # Redacted config-entry diagnostics, that bundle included
 ├── repairs.py            # Fix flows Home Assistant loads by name when the user clicks Fix
+├── solve_gate.py         # When a solve runs: the one in-flight guard, the trailing refresh, the background budget, the user slot, the run-now path
 │
 ├── www/                  # The dashboard card, one self-contained file
 ├── brand/                # Icon and logo
@@ -284,7 +285,7 @@ custom_components/heatpump_optimizer/
 
 ## The Home Assistant boundary
 
-33 of the 96 modules import `homeassistant` at module level: `__init__`,
+33 of the 97 modules import `homeassistant` at module level: `__init__`,
 `config_flow`, `coordinator`, `open_meteo`, `frontend`, the six entity
 platforms `sensor`, `binary_sensor`, `button`, `climate`, `switch`, `datetime`,
 and the supporting modules `accuracy`, `away`, `boost`, `currency`, `debugger`, `defrost`,
@@ -293,7 +294,7 @@ and the supporting modules `accuracy`, `away`, `boost`, `currency`, `debugger`,
 reaches for `homeassistant.util.dt` inside a function, as the fallback when no
 clock function was injected.
 
-The other 62 modules are deliberately free of it, so each can be driven
+The other 63 modules are deliberately free of it, so each can be driven
 directly by `tests/features.py` with no Home Assistant running. That matters
 because the failure mode of this integration is a *plausible* plan: a detector
 that never fires, or a watchdog that lets a flatline through, produces output
diff --git a/tests/closures.json b/tests/closures.json
index ec631afefa..bb67ff70c6 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -270,6 +270,7 @@
    "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
+   "custom_components/heatpump_optimizer/solve_gate.py",
    "custom_components/heatpump_optimizer/store.py",
    "custom_components/heatpump_optimizer/strings.json",
    "custom_components/heatpump_optimizer/supply_hold.py",
@@ -441,6 +442,7 @@
    "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
+   "custom_components/heatpump_optimizer/solve_gate.py",
    "custom_components/heatpump_optimizer/store.py",
    "custom_components/heatpump_optimizer/supply_hold.py",
    "custom_components/heatpump_optimizer/switch.py",
@@ -551,6 +553,7 @@
    "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
+   "custom_components/heatpump_optimizer/solve_gate.py",
    "custom_components/heatpump_optimizer/store.py",
    "custom_components/heatpump_optimizer/supply_hold.py",
    "custom_components/heatpump_optimizer/sysid.py",
@@ -659,6 +662,7 @@
    "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
+   "custom_components/heatpump_optimizer/solve_gate.py",
    "custom_components/heatpump_optimizer/store.py",
    "custom_components/heatpump_optimizer/strings.json",
    "custom_components/heatpump_optimizer/supply_hold.py",
@@ -781,6 +785,7 @@
    "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
+   "custom_components/heatpump_optimizer/solve_gate.py",
    "custom_components/heatpump_optimizer/store.py",
    "custom_components/heatpump_optimizer/supply_hold.py",
    "custom_components/heatpump_optimizer/sysid.py",
@@ -915,6 +920,7 @@
    "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
+   "custom_components/heatpump_optimizer/solve_gate.py",
    "custom_components/heatpump_optimizer/store.py",
    "custom_components/heatpump_optimizer/strings.json",
    "custom_components/heatpump_optimizer/supply_hold.py",
@@ -1046,6 +1052,7 @@
    "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
+   "custom_components/heatpump_optimizer/solve_gate.py",
    "custom_components/heatpump_optimizer/store.py",
    "custom_components/heatpump_optimizer/supply_hold.py",
    "custom_components/heatpump_optimizer/sysid.py",
@@ -1190,6 +1197,7 @@
    "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
+   "custom_components/heatpump_optimizer/solve_gate.py",
    "custom_components/heatpump_optimizer/store.py",
    "custom_components/heatpump_optimizer/strings.json",
    "custom_components/heatpump_optimizer/supply_hold.py",
@@ -1330,6 +1338,7 @@
    "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
+   "custom_components/heatpump_optimizer/solve_gate.py",
    "custom_components/heatpump_optimizer/store.py",
    "custom_components/heatpump_optimizer/strings.json",
    "custom_components/heatpump_optimizer/supply_hold.py",
@@ -1665,6 +1674,7 @@
    "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
+   "custom_components/heatpump_optimizer/solve_gate.py",
    "custom_components/heatpump_optimizer/store.py",
    "custom_components/heatpump_optimizer/strings.json",
    "custom_components/heatpump_optimizer/supply_hold.py",
@@ -2202,6 +2212,7 @@
    "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
+   "custom_components/heatpump_optimizer/solve_gate.py",
    "custom_components/heatpump_optimizer/store.py",
    "custom_components/heatpump_optimizer/strings.json",
    "custom_components/heatpump_optimizer/supply_hold.py",
@@ -2400,6 +2411,7 @@
    "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
+   "custom_components/heatpump_optimizer/solve_gate.py",
    "custom_components/heatpump_optimizer/store.py",
    "custom_components/heatpump_optimizer/strings.json",
    "custom_components/heatpump_optimizer/supply_hold.py",
@@ -2559,6 +2571,7 @@
    "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
+   "custom_components/heatpump_optimizer/solve_gate.py",
    "custom_components/heatpump_optimizer/store.py",
    "custom_components/heatpump_optimizer/supply_hold.py",
    "custom_components/heatpump_optimizer/switch.py",
@@ -2713,6 +2726,7 @@
    "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
+   "custom_components/heatpump_optimizer/solve_gate.py",
    "custom_components/heatpump_optimizer/store.py",
    "custom_components/heatpump_optimizer/strings.json",
    "custom_components/heatpump_optimizer/supply_hold.py",
@@ -2894,6 +2908,7 @@
    "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
+   "custom_components/heatpump_optimizer/solve_gate.py",
    "custom_components/heatpump_optimizer/store.py",
    "custom_components/heatpump_optimizer/supply_hold.py",
    "custom_components/heatpump_optimizer/sysid.py",
@@ -3081,6 +3096,7 @@
    "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
+   "custom_components/heatpump_optimizer/solve_gate.py",
    "custom_components/heatpump_optimizer/store.py",
    "custom_components/heatpump_optimizer/strings.json",
    "custom_components/heatpump_optimizer/supply_hold.py",
@@ -3476,6 +3492,7 @@
    "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
+   "custom_components/heatpump_optimizer/solve_gate.py",
    "custom_components/heatpump_optimizer/store.py",
    "custom_components/heatpump_optimizer/supply_hold.py",
    "custom_components/heatpump_optimizer/sysid.py",
@@ -3649,6 +3666,7 @@
    "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
+   "custom_components/heatpump_optimizer/solve_gate.py",
    "custom_components/heatpump_optimizer/store.py",
    "custom_components/heatpump_optimizer/supply_hold.py",
    "custom_components/heatpump_optimizer/sysid.py",
@@ -3757,6 +3775,7 @@
    "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
+   "custom_components/heatpump_optimizer/solve_gate.py",
    "custom_components/heatpump_optimizer/store.py",
    "custom_components/heatpump_optimizer/supply_hold.py",
    "custom_components/heatpump_optimizer/sysid.py",
@@ -3926,6 +3945,7 @@
    "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
+   "custom_components/heatpump_optimizer/solve_gate.py",
    "custom_components/heatpump_optimizer/store.py",
    "custom_components/heatpump_optimizer/supply_hold.py",
    "custom_components/heatpump_optimizer/switch.py",
@@ -4027,6 +4047,7 @@
    "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
+   "custom_components/heatpump_optimizer/solve_gate.py",
    "custom_components/heatpump_optimizer/store.py",
    "custom_components/heatpump_optimizer/supply_hold.py",
    "custom_components/heatpump_optimizer/switch.py",
@@ -4155,6 +4176,7 @@
    "custom_components/heatpump_optimizer/slab_seed.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/snapshots.py",
+   "custom_components/heatpump_optimizer/solve_gate.py",
    "custom_components/heatpump_optimizer/store.py",
    "custom_components/heatpump_optimizer/supply_hold.py",
    "custom_components/heatpump_optimizer/sysid.py",
@@ -5402,7 +5424,7 @@
    "seconds": 21.5
   },
   "tests/entities.py": {
-   "rc": 0,
+   "rc": 1,
    "seconds": 867.9
   },
   "tests/env_drift.py": {
@@ -5423,19 +5445,19 @@
   },
   "tests/golden.py": {
    "rc": 0,
-   "seconds": 1.2
+   "seconds": 0.5
   },
   "tests/guard_pins.py": {
    "rc": 0,
-   "seconds": 18.0
+   "seconds": 6.0
   },
   "tests/ha_contract.py": {
    "rc": 0,
    "seconds": 0.5
   },
   "tests/harness_headers.py": {
-   "rc": 0,
-   "seconds": 327.6
+   "rc": 1,
+   "seconds": 135.7
   },
   "tests/layout.py": {
    "rc": 0,
diff --git a/tests/deployment_shape.py b/tests/deployment_shape.py
index 09c86c8c14..6f88881ce6 100644
--- a/tests/deployment_shape.py
+++ b/tests/deployment_shape.py
@@ -37,9 +37,9 @@ child from ``inspect.getfile``.
 
 COST OF THE SHAPE (#1218, round-5 D3-08). Materialising the shape copies the
 tracked package file by file (``_materialise``, below), and the gate's tracer
-records every read, so this lane's recorded closure is the package: all 115
+records every read, so this lane's recorded closure is the package: all 116
 files under ``custom_components/heatpump_optimizer/``, Python and non-Python
-alike (114 until R11-OUTSIDE-ROOMS-P1's ``rooms.py``, 113 until R11-OUTSIDE-HONEST-STARTS-RUNS's ``runs.py``, 112 until #3616's ``slab_seed.py``, 111 until R10-START-COUNTER-EDGES's ``running_signal.py``, 110 until
+alike (115 until R11-SEAM-cycle-solve's ``solve_gate.py``, 114 until R11-OUTSIDE-ROOMS-P1's ``rooms.py``, 113 until R11-OUTSIDE-HONEST-STARTS-RUNS's ``runs.py``, 112 until #3616's ``slab_seed.py``, 111 until R10-START-COUNTER-EDGES's ``running_signal.py``, 110 until
 R10-ADVISOR-STEADY-START's ``whatif.py``, 109 until R10-DUTY-SWITCH-PLANNER-PRICE's
 ``duty_legs.py``, 108 until the supply-hold PR's ``supply_hold.py``, 107 until
 R10-DUTY-SWITCH-RESTART-LEARNING's ``duty_switch.py``, 78 until R9 F2.5's ``batchmath.py``, 79 until R9 UI-1's six brand
diff --git a/tests/entities.py b/tests/entities.py
index 7782c6a294..db4f010d66 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -3950,6 +3950,18 @@ def _p2_registry(sources):
                      "the explicit answer is stored and takes its verdict from "
                      "_dhw_enabled_from_config",
              }),
+        # D1-s3-04: a killed worker's reap. The transport arm waited without a
+        # bound, holding the lock every peer's solve waits on, where its
+        # timeout sibling bounded the same wait.
+        dict(fact="killed_worker_reap", finding="D1-s3-04",
+             match=_p2_match_node(
+                 (ast.Call,), r"^worker\.wait\(",
+                 lambda n: getattr(n.func, "attr", None) == "wait"),
+             owners=["coordinator.py::_reap_killed"], dispositions={
+                 "coordinator.py::_shutdown_process_pool":
+                     "the stop's own reap, outside the lock: terminate's bounded "
+                     "wait, and at interpreter exit #533's kill and timeout-less "
+                     "wait, when no peer's solve is left to wait"}),
         # D1-s5-01: a state's age. inputs.state_stamp owns the stamp rule
         # (last_reported first, #775); age_of re-derived it.
         dict(fact="state_age", finding="D1-s5-01",
diff --git a/tests/features.py b/tests/features.py
index 0868f72811..4fa3591f59 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -23,6 +23,8 @@ from heatpump_optimizer import away as away_mode
 from heatpump_optimizer import boost as boost_mod
 from heatpump_optimizer import battery as battery_view
 from heatpump_optimizer import presets, price_tiles, pv
+from heatpump_optimizer import solve_gate
+
 from heatpump_optimizer.accuracy import (
     AccuracySample,
     AccuracyTracker,
@@ -719,6 +721,14 @@ def _fi_restart(at, store_of, payload, loader):
     return c
 
 
+def _next_main_solve(coord):
+    """One main solve's start and end through the solve gate, so the background
+    what-if a test drives next is admitted, as a cycle's would be (D9-s1-02)."""
+    gate = solve_gate.gate_for(coord)
+    solve_gate.begin_solve(gate)
+    solve_gate.end_solve(gate)
+
+
 def _fi_fuse_held(stamp, gate):
     """FI-sw1: the 7-day recompute cooldown still holds at ``gate``."""
     c = _fi_restart(
@@ -730,6 +740,7 @@ def _fi_fuse_held(stamp, gate):
         _fi_dt.freeze(when)
         before = c._fuse_advisor_at
         try:
+            _next_main_solve(c)
             _fi_aio.run(c._maybe_run_fuse_advisor(_solve_record_now(c)))
         except Exception:  # noqa: BLE001 -- only whether the cooldown held is read
             pass
@@ -1307,63 +1318,93 @@ class _R9F13Hass(FakeHass):
         return _r9f13_aio.get_running_loop().create_task(coro)
 
 
-def _r9f13_press(reason):
-    """Press the button with the coordinator refusing `reason`; `None` runs."""
-    hass, entry, coord = _r9f13_make(f"f13_press_{reason}")
-    requested = []
+def _r9f13_press(reason, failed_key=None, mode=None):
+    """Press the button with the refresh's solve answering `reason`; `None` runs.
+
+    The press awaits ``solve_gate.async_optimize_now`` (D17-s3-01): one real
+    refresh, whose cycle records its solve's answer on the gate. `failed_key`
+    fails the refresh's price fetch with that translation key instead; `mode`
+    sets a fixed mode, whose refresh solves nothing. Returns the press's
+    outcome and the solves and refreshes it cost.
+    """
+    hass, entry, coord = _r9f13_make(f"f13_press_{reason}_{failed_key}_{mode}")
+    calls = {"solve": 0, "refresh": 0}
+    real_refresh = coord.async_refresh
 
     async def _solve():
+        calls["solve"] += 1
         return reason
 
     async def _refresh():
-        requested.append(True)
-        await _r9f13_aio.Event().wait()
+        calls["refresh"] += 1
+        await real_refresh()
+
+    async def _no_prices():
+        raise _r9f13_update_failed("injected", translation_key=failed_key)
 
     coord.async_run_optimization = _solve
-    coord.async_request_refresh = _refresh
+    coord.async_refresh = _refresh
+    if failed_key is not None:
+        coord._fetch_tibber_prices = _no_prices
+    if mode is not None:
+        coord._mode = mode
     ent = _r9f13_button.ForceOptimizationButton(coord, entry)
     ent.hass = _R9F13Hass()
 
     async def _scenario():
         try:
-            await _r9f13_aio.wait_for(ent.async_press(), timeout=5.0)
+            await _r9f13_aio.wait_for(ent.async_press(), timeout=30.0)
             out = "returned"
         except _r9f13_err as err:
             out = getattr(err, "translation_key", None) or "raised:plain"
         except TimeoutError:
             out = "hung"
-        # One yield: 3.12's wait_for awaits the inner coroutine inline, so
-        # the refresh task the press scheduled has not started yet here;
-        # without this the `requested` read races the interpreter version.
-        await _r9f13_aio.sleep(0)
         for task in _r9f13_aio.all_tasks() - {_r9f13_aio.current_task()}:
             task.cancel()
-        return out, bool(requested)
+        return out, calls["solve"], calls["refresh"]
 
     return _r9f13_aio.run(_scenario())
 
 
+from homeassistant.helpers.update_coordinator import UpdateFailed as _r9f13_update_failed  # noqa: E402
+
 _r9f13_press_refused = _r9f13_press("no_prices")
 _r9f13_press_ran = _r9f13_press(None)
 R.check(
     "D10-s1-02: the press raises the action's own no-prices refusal when the "
     "solve did not run",
-    _r9f13_press_refused == ("run_optimization_no_prices", True),
-    f"got {_r9f13_press_refused} (want ('run_optimization_no_prices', True))",
+    _r9f13_press_refused == ("run_optimization_no_prices", 1, 1),
+    f"got {_r9f13_press_refused} (want ('run_optimization_no_prices', 1, 1))",
 )
 R.check(
-    "D10-s1-02: the press returns normally when the solve ran, still off "
-    "the refresh it asked for",
-    _r9f13_press_ran == ("returned", True),
-    f"got {_r9f13_press_ran} (want ('returned', True))",
+    "D17-s3-01: the press returns normally when the solve ran, and costs one "
+    "refresh and the one solve inside it -- never a second solve beside it",
+    _r9f13_press_ran == ("returned", 1, 1),
+    f"got {_r9f13_press_ran} (want ('returned', 1, 1))",
 )
 _r9f13_press_solve_failed = _r9f13_press("solve_failed")
 R.check(
     "D10-s1-02: the press raises the action's solve-failed refusal when the "
     "solve died (the reason-is-not-None arm of the same refusal -- the "
     "mutation survivor at button.py's second guard)",
-    _r9f13_press_solve_failed == ("run_optimization_solve_failed", True),
-    f"got {_r9f13_press_solve_failed} (want ('run_optimization_solve_failed', True))",
+    _r9f13_press_solve_failed == ("run_optimization_solve_failed", 1, 1),
+    f"got {_r9f13_press_solve_failed} (want ('run_optimization_solve_failed', 1, 1))",
+)
+_r9f13_press_no_cover = _r9f13_press(None, failed_key="tibber_fetch_failed")
+_r9f13_press_cycle_failed = _r9f13_press(None, failed_key="update_failed")
+R.check(
+    "D17-s3-01: a refresh failed on prices that cover no step is the no-prices "
+    "refusal, any other failed refresh the solve-failed one; neither solved",
+    _r9f13_press_no_cover == ("run_optimization_no_prices", 0, 1)
+    and _r9f13_press_cycle_failed == ("run_optimization_solve_failed", 0, 1),
+    f"no cover {_r9f13_press_no_cover}, other {_r9f13_press_cycle_failed}",
+)
+_r9f13_press_fixed = _r9f13_press(None, mode=_r9f13_const.MODE_COMFORT)
+R.check(
+    "D17-s3-01: in a fixed mode, whose refresh solves nothing, the press "
+    "solves the private plan once and then refreshes",
+    _r9f13_press_fixed == ("returned", 1, 1),
+    f"got {_r9f13_press_fixed} (want ('returned', 1, 1))",
 )
 R.check(
     "D10-s1-02: no button press queues behind another (PARALLEL_UPDATES 0, "
@@ -19653,6 +19694,7 @@ _cad = _advisor_coord()
 from heatpump_optimizer import whatif as _whatif_mod
 _whatif_mod.state_for(_cad).answer = {"marker": "card"}
 _whatif_mod.state_for(_cad).last_at = None
+_next_main_solve(_cad)
 _asyncio.run(_cad._maybe_run_fuse_advisor(_solve_record_now(_cad)))
 _adv = _cad._fuse_advisor
 R.check(
@@ -19674,6 +19716,7 @@ R.check(
     _whatif_mod.state_for(_cad).answer == {"marker": "card"}
     and _whatif_mod.state_for(_cad).last_at is None,
 )
+_next_main_solve(_cad)
 _asyncio.run(_cad._maybe_run_fuse_advisor(_solve_record_now(_cad)))
 R.check(
     "a second run inside the week is skipped",
@@ -19689,6 +19732,7 @@ _cad2 = _advisor_coord(
         "min_room_temperature": 19.5,
     }
 )
+_next_main_solve(_cad2)
 _asyncio.run(_cad2._maybe_run_fuse_advisor(_solve_record_now(_cad2)))
 R.check(
     "a shortfall the baseline plan shares is not blamed on the fuse",
@@ -19704,6 +19748,7 @@ _cad3 = _advisor_coord(
         "min_room_temperature": 19.5,
     }
 )
+_next_main_solve(_cad3)
 _asyncio.run(_cad3._maybe_run_fuse_advisor(_solve_record_now(_cad3)))
 R.check(
     "a shortfall the cap itself forces still fails the candidate",
@@ -19719,6 +19764,7 @@ R.check(
 _adv_calls.clear()
 _cad4 = _advisor_coord(payload_extra={"error": "no_prices"})
 _cad4._fuse_advisor = {"candidate_kw": 11.04, "feasible": True}
+_next_main_solve(_cad4)
 _asyncio.run(_cad4._maybe_run_fuse_advisor(_solve_record_now(_cad4)))
 R.check(
     "an errored what-if keeps last month's real verdict",
@@ -19730,6 +19776,7 @@ R.check(
 # --- #782 the weekly guard survives a store round-trip ----------------------
 _adv_calls.clear()
 _cad_persist = _advisor_coord()
+_next_main_solve(_cad_persist)
 _asyncio.run(_cad_persist._maybe_run_fuse_advisor(_solve_record_now(_cad_persist)))
 _persist_payload = {}
 
@@ -19758,6 +19805,7 @@ R.check(
 _cad_restore = _advisor_coord()
 _cad_restore._ledger_store = _FuseStore()
 _adv_calls.clear()
+_next_main_solve(_cad_restore)
 _asyncio.run(_cad_restore._maybe_run_fuse_advisor(_solve_record_now(_cad_restore)))
 R.check(
     "a restored advisor timestamp still skips a second run inside the week",
@@ -19777,6 +19825,7 @@ class _OldLed:
 _cad_old = _advisor_coord()
 _cad_old._ledger_store = _OldLed()
 _adv_before = list(_adv_calls)
+_next_main_solve(_cad_old)
 _asyncio.run(_cad_old._maybe_run_fuse_advisor(_solve_record_now(_cad_old)))
 R.check(
     "an older ledger store without advisor keys still runs the what-if",
@@ -26222,6 +26271,7 @@ async def _fake_sim(overrides, limited=True, base=None, steady=False):
 
 
 _ctile.async_simulate = _fake_sim
+_next_main_solve(_ctile)
 _asyncio.run(_ctile._maybe_refresh_price_tile(_solve_record_now(_ctile)))
 R.check(
     "with the flag off no tile ever computes, whatever solves happen",
@@ -26229,6 +26279,7 @@ R.check(
 )
 _ctile2 = _t2_coord(price_tiles_enabled=True)
 _ctile2.async_simulate = _fake_sim
+_next_main_solve(_ctile2)
 _asyncio.run(_ctile2._maybe_refresh_price_tile(_solve_record_now(_ctile2)))
 R.check(
     "one solve refreshes exactly one tile, in rotation",
@@ -26252,6 +26303,7 @@ async def _fake_sim_route(overrides, limited=True, base=None, steady=False):
 
 
 _ctile2.async_simulate = _fake_sim_route
+_next_main_solve(_ctile2)
 _asyncio.run(_ctile2._maybe_refresh_price_tile(_solve_record_now(_ctile2)))
 R.check(
     "#1753: the tile solves through the user-limit-free path, so its turn "
@@ -26450,6 +26502,7 @@ async def _fake_sim_poison(overrides, limited=True, _c=_ctile3, base=None, stead
 
 
 _ctile3.async_simulate = _fake_sim_poison
+_next_main_solve(_ctile3)
 _asyncio.run(_ctile3._maybe_refresh_price_tile(_solve_record_now(_ctile3)))
 R.check(
     "#1753: the tile takes the limited=False path -- no borrow to restore",
@@ -26481,6 +26534,7 @@ async def _fake_sim_err(overrides, limited=True, base=None, steady=False):
 
 
 _ctile4.async_simulate = _fake_sim_err
+_next_main_solve(_ctile4)
 _asyncio.run(_ctile4._maybe_refresh_price_tile(_solve_record_now(_ctile4)))
 R.check(
     "an erroring tile spec advances the rotation instead of stalling it",
@@ -26490,6 +26544,7 @@ R.check(
 # Turning the flag off retires the published tiles too.
 _ctile5 = _t2_coord()
 price_tiles.book(_ctile5)["stale"] = {"monthly_cost_delta": 1.0}
+_next_main_solve(_ctile5)
 _asyncio.run(_ctile5._maybe_refresh_price_tile(_solve_record_now(_ctile5)))
 R.check(
     "gate off means gone: no stale what-if money outlives the flag",
@@ -27503,6 +27558,8 @@ R.check(
     f"plan={_svc_coord._optimization_result is not None}",
 )
 
+# D17-s3-01: the action fetches before it solves, so the dead feed is the sensor's too.
+_svc_hass.states.set("sensor.prices", FakeState("unavailable"))
 _svc_check(
     "run_optimization with no usable prices raises a translated operational error",
     _svc_call(_svc_hass, "run_optimization", {}),
@@ -27555,6 +27612,7 @@ R.check(
     _asyncio.run(_stale_coord.async_run_optimization()) == "no_prices"
     and _stale_coord._optimization_result is None,
 )
+_stale_hass.states.set("sensor.prices", FakeState("unavailable"))  # the fetch finds nothing newer
 _svc_check(
     "run_optimization on a stale list raises the same no-prices error",
     _svc_call(_stale_hass, "run_optimization", {}),
@@ -27849,6 +27907,7 @@ async def _svc_ok_restore():
 
 
 _svc_coord.async_run_optimization = _svc_ok_run
+_seed_prices(_svc_hass)  # the feed back: the refresh the action runs fetches
 _svc_out = _svc_call(_svc_hass, "run_optimization", {})
 R.check(
     "run_optimization returns normally when the solve ran",
@@ -32150,6 +32209,7 @@ async def _st_failures():
             price_tiles.monthly_figure(cap, answer), _st_whatif.state_for(coord).live_steady,
         )
         coord._fuse_advisor_at = _st_dt.now() - timedelta(days=8)
+        _next_main_solve(coord)
         await coord._maybe_run_fuse_advisor(record)
         out["fuse_failed"] = dict(coord._fuse_advisor)
     # And healthy: the fuse advisor's money is the answer's steady key.
@@ -32163,6 +32223,7 @@ async def _st_failures():
     coord.async_simulate = _spy
     try:
         coord._fuse_advisor_at = _st_dt.now() - timedelta(days=8)
+        _next_main_solve(coord)
         await coord._maybe_run_fuse_advisor(record)
     finally:
         del coord.async_simulate
@@ -32222,6 +32283,7 @@ async def _st_tiles():
         # tile's clock and solves nothing.
         before = seams.counts()
         for _ in names:
+            _next_main_solve(coord)
             await coord._maybe_refresh_price_tile(record)
         out["clock_first"] = (tuple(b - a for a, b in zip(before, seams.counts())), sorted(price_tiles.book(coord)))
         price_tiles.book(coord).clear()
@@ -32229,12 +32291,14 @@ async def _st_tiles():
         # The rotation position is whatever the seeding solve left it at.
         for _ in names:
             before, had = seams.counts(), {k: len(v.get("days", [])) for k, v in price_tiles.book(coord).items()}
+            _next_main_solve(coord)
             await coord._maybe_refresh_price_tile(record)
             name = next(k for k, v in price_tiles.book(coord).items() if len(v.get("days", [])) != had.get(k, 0)
                         or k not in had)
             out[name] = tuple(b - a for a, b in zip(before, seams.counts()))
         before = seams.counts()
         coord._fuse_advisor_at = _st_dt.now() - timedelta(days=8)
+        _next_main_solve(coord)
         await coord._maybe_run_fuse_advisor(record)
         out["fuse"] = tuple(b - a for a, b in zip(before, seams.counts()))
         user = _st_whatif.state_for(coord)
@@ -32248,6 +32312,7 @@ async def _st_tiles():
             _st_dt.freeze(start + age)
             before, stamp = seams.counts(), price_tiles.book(coord)["power_cap_75"]["computed_at"]
             for _ in names:
+                _next_main_solve(coord)
                 await coord._maybe_refresh_price_tile(record)
             out["clock_" + label] = (tuple(b - a for a, b in zip(before, seams.counts())),
                                      price_tiles.book(coord)["power_cap_75"]["computed_at"] != stamp)
@@ -32655,14 +32720,14 @@ _st_tie_sides = [_st_ns(reference_day=lambda inputs, d=d: d) for d in _st_tie_da
 R.check(
     "and the branch is taken on the setpoints, never the energies: the tie is a "
     "schedule ask, equal setpoints with unequal energies are not",
-    _st_whatif.schedule_days((_st_tie_sides[0], None), (_st_tie_sides[1], None))
+    _st_whatif.schedule_days(*_st_whatif.reference_days((_st_tie_sides[0], None), (_st_tie_sides[1], None)))
     == (_st_tie_days[0][1], _st_tie_days[1][1])
-    and _st_whatif.schedule_days(
+    and _st_whatif.schedule_days(*_st_whatif.reference_days(
         (_st_ns(reference_day=lambda inputs: ([21.0], 5.0)), None),
-        (_st_ns(reference_day=lambda inputs: ([21.0], 6.0)), None)) is None
-    and _st_whatif.schedule_days(
+        (_st_ns(reference_day=lambda inputs: ([21.0], 6.0)), None))) is None
+    and _st_whatif.schedule_days(*_st_whatif.reference_days(
         (_st_ns(reference_day=lambda inputs: ([21.0, 19.5], 5.0)), None),
-        (_st_ns(reference_day=lambda inputs: ([21.0, 19.51], 6.0)), None)) == (5.0, 6.0),
+        (_st_ns(reference_day=lambda inputs: ([21.0, 19.51], 6.0)), None))) == (5.0, 6.0),
     "schedule_days",
 )
 
@@ -32673,6 +32738,13 @@ async def _st_nan_day(energy=_st_math.nan):
     coord = await _st_coord()
     real = _st_omod.HeatPumpOptimizer.reference_day
     _st_omod.HeatPumpOptimizer.reference_day = lambda self, inputs: (real(self, inputs)[0], energy)
+    real_off = _coord_mod._await_off_loop
+
+    async def _here(hass, fn, *args):
+        # The patch above lives in this process; the reference days run here.
+        return fn(*args) if fn is _st_whatif.reference_days else await real_off(hass, fn, *args)
+
+    _coord_mod._await_off_loop = _here
     try:
         with _StSeams() as seams:
             record = _solve_record_now(coord)
@@ -32682,6 +32754,7 @@ async def _st_nan_day(energy=_st_math.nan):
                     answer.get(_ST_KEY))
     finally:
         _st_omod.HeatPumpOptimizer.reference_day = real
+        _coord_mod._await_off_loop = real_off
 
 
 _st_dt.freeze(_st_dt.now().replace(hour=7, minute=7, second=0, microsecond=0))
@@ -55214,12 +55287,11 @@ def _t4_count_solve_work(coord):
 _t4_force_busy = _t4_coord()
 _t4_count_refresh(_t4_force_busy)
 _t4_count_solve_work(_t4_force_busy)
-_t4_force_busy._optimization_running = True
+solve_gate.gate_for(_t4_force_busy).solving = True
 _t4_drive(_t4_force_busy, "async_run_optimization")
 _t4_force_idle = _t4_coord()
 _t4_count_refresh(_t4_force_idle)
 _t4_count_solve_work(_t4_force_idle)
-_t4_force_idle._optimization_running = False
 _t4_drive(_t4_force_idle, "async_run_optimization")
 R.check(
     "forcing an optimization while one runs is dropped, not queued "
@@ -56271,7 +56343,7 @@ R.check(
 )
 
 _t5_opt_busy = _t5_solve_spy()
-_t5_opt_busy._optimization_running = True
+solve_gate.gate_for(_t5_opt_busy).solving = True
 _t5_run(_t5_opt_busy)
 R.check(
     "a solve already in flight is skipped rather than run a second time",
@@ -56382,7 +56454,6 @@ _T6_PROPERTY_PAIRS = (
     ("mode", "_mode", "boost"),
     ("prices", "_prices", [{"total": 9.99}]),
     ("dhw_temperature", "_dhw_temperature", 53.75),
-    ("optimization_running", "_optimization_running", True),
     # The read-only views the entity platforms read (R9-EG-B2, #1739).
     ("thermal_params", "_thermal_params", "sentinel-params"),
     ("thermal_model", "_thermal_model", "sentinel-model"),
@@ -56393,7 +56464,7 @@ _t6_prop_moved = _t6_coord()
 for _t6_pname, _t6_attr, _t6_value in _T6_PROPERTY_PAIRS:
     setattr(_t6_prop_moved, _t6_attr, _t6_value)
 R.check(
-    "seven published properties and views each read the attribute they front, not a neighbour",
+    "six published properties and views each read the attribute they front, not a neighbour",
     all(
         getattr(_t6_prop_moved, name) == value
         and getattr(_t6_prop_start, name) != value
@@ -58179,11 +58250,18 @@ _g8_cyc_floor = _g8_cyc._ctx._opt_config.min_temp
 _g8_cyc_real = _coord_mod._await_optimize
 
 
+_g8_cyc_calls = []
+
+
 async def _g8_cyc_mid_solve(*_args, **_kwargs):
-    await _g8_cyc.async_update_thermal_params(
-        {"dhw_min_temperature": 38.0, "dhw_idle_min_temperature": 31.0}
-    )
-    await _g8_cyc.async_set_target_temperature(19.5)
+    # Each cycle's first solve takes the writes; their request re-runs it once
+    # (#1754, D1-s1-03), and the re-run is left quiet so it ends.
+    _g8_cyc_calls.append(1)
+    if len(_g8_cyc_calls) % 2:
+        await _g8_cyc.async_update_thermal_params(
+            {"dhw_min_temperature": 38.0, "dhw_idle_min_temperature": 31.0}
+        )
+        await _g8_cyc.async_set_target_temperature(19.5)
     raise RuntimeError("the solve is not the point here")
 
 
@@ -72243,6 +72321,7 @@ def _r9egb9_borrow_arm(borrower, kind):
             coord._fuse_advisor_at = _r9egb9_dt.now() - timedelta(days=8)
             call = _f25_partial(
                 coord._maybe_run_fuse_advisor, _solve_record_now(coord))
+        _next_main_solve(coord)  # the borrower runs after a solve of its own (D9-s1-02)
         out = {"U0": _r9egb9_ov(u0)}
         if kind == "null":
             await call()
@@ -73997,9 +74076,9 @@ async def _dbg_week(flush):
         first = _dbg.collector_for(coord)
         out = {"subscribed": len(coord._listeners) - listeners}
         t = await _dbg_cycles(hass, coord, _DBG_T0, 1)
-        coord._optimization_running = True
+        solve_gate.gate_for(coord).solving = True
         coord.async_update_listeners()
-        coord._optimization_running = False
+        solve_gate.gate_for(coord).solving = False
         coord.async_update_listeners()
         t = await _dbg_cycles(hass, coord, t, 1)
         out["walls"] = [r.get("solve_wall_ms") for r in first.rows]
@@ -82761,9 +82840,11 @@ async def _ls_tile_cancel():
 
     coord.async_simulate = _sim
     try:
+        _next_main_solve(coord)
         await coord._maybe_refresh_price_tile(record)
     except _ls_aio.CancelledError:
         pass
+    _next_main_solve(coord)
     await coord._maybe_refresh_price_tile(record)
     return [dict(o) for o in seen], [dict(o) for _n, o in specs]
 
@@ -96912,4 +96993,319 @@ R.check(
 )
 
 
+
+# -- R11-SEAM-cycle-solve: when a solve runs (solve_gate) ------------------------
+import asyncio as _sg_aio  # noqa: E402
+import subprocess as _sg_sp  # noqa: E402
+from heatpump_optimizer import coordinator as _sg_cm  # noqa: E402
+from heatpump_optimizer import whatif as _sg_whatif  # noqa: E402
+
+_sg_g = solve_gate.SolveGate()
+_sg_idle = solve_gate.absorb_request(_sg_g, False)
+_sg_idle_flags = (_sg_g.rerun, _sg_g.trailing)
+_sg_refreshing = solve_gate.absorb_request(_sg_g, True)
+_sg_first, _sg_second = solve_gate.begin_solve(_sg_g), solve_gate.begin_solve(_sg_g)
+_sg_ends = (solve_gate.end_solve(_sg_g), solve_gate.end_solve(_sg_g))
+_sg_trails = (solve_gate.take_trailing(_sg_g), solve_gate.take_trailing(_sg_g))
+R.check(
+    "solve_gate: an idle request is not absorbed and sets nothing; one during a refresh "
+    "trails it once; a second solve start is refused and recorded as one re-run, taken once",
+    _sg_idle is False and _sg_idle_flags == (False, False) and _sg_refreshing is True
+    and (_sg_first, _sg_second) == (True, False) and _sg_ends == (True, False)
+    and _sg_trails == (True, False) and not _sg_g.solving,
+    f"idle={_sg_idle} {_sg_idle_flags} refreshing={_sg_refreshing} starts={(_sg_first, _sg_second)} "
+    f"ends={_sg_ends} trails={_sg_trails}",
+)
+_sg_b = solve_gate.SolveGate()
+solve_gate.begin_solve(_sg_b)
+_sg_bg = [solve_gate.admit_background(_sg_b), solve_gate.admit_background(_sg_b)]
+solve_gate.end_solve(_sg_b)
+solve_gate.begin_solve(_sg_b)
+_sg_bg.append(solve_gate.admit_background(_sg_b))
+R.check(
+    "D9-s1-02: one background what-if per main solve -- the second is denied, and the next "
+    "solve opens a fresh budget",
+    _sg_bg == [True, False, True],
+    f"admissions {_sg_bg}",
+)
+
+
+async def _sg_slot_burst(k):
+    """K user asks overlapping the first one's solve: which solve, which are held."""
+    gate, solved, release = solve_gate.SolveGate(), [], _sg_aio.Event()
+
+    async def ask(i):
+        async with solve_gate.user_slot(gate) as ok:
+            if not ok:
+                return "held"
+            solved.append(i)
+            if i == 0:
+                await release.wait()
+            return "solved"
+
+    tasks = [_sg_aio.create_task(ask(i)) for i in range(k)]
+    for _ in range(3):
+        await _sg_aio.sleep(0)
+    async with solve_gate.user_slot(gate, False) as background:  # never waits on the user slot
+        pass
+    release.set()
+    answers = await _sg_aio.gather(*tasks)
+    return solved, answers, background, gate.user_running
+
+
+_sg_burst4 = _sg_aio.run(_sg_slot_burst(4))
+_sg_burst1 = _sg_aio.run(_sg_slot_burst(1))
+R.check(
+    "D9-s1-03: of four overlapping user what-ifs only the one in flight and the newest solve; "
+    "the two overtaken are held, a background caller never waits, and the slot is freed; "
+    "null control, one ask solves",
+    _sg_burst4 == ([0, 3], ["solved", "held", "held", "solved"], True, False)
+    and _sg_burst1 == ([0], ["solved"], True, False),
+    f"four {_sg_burst4}, one {_sg_burst1}",
+)
+
+
+class _SgOpt:
+    def __init__(self, day):
+        self.day = day
+
+    def reference_day(self, _inputs):
+        return self.day
+
+
+_sg_days = _sg_whatif.reference_days((_SgOpt(([20.0], 3.0)), None), (_SgOpt(([19.0], 2.5)), None))
+R.check(
+    "D9-s1-04: the reference days are one shippable function of the two sides, and the "
+    "schedule branch reads them -- a moved setpoint prices the pair, an unmoved one is None",
+    _sg_days == (([20.0], 3.0), ([19.0], 2.5))
+    and _sg_whatif.schedule_days(*_sg_days) == (3.0, 2.5)
+    and _sg_whatif.schedule_days(([20.0], 3.0), ([20.0], 9.0)) is None,
+    f"{_sg_days}",
+)
+
+
+async def _sg_requests():
+    """The coordinator's own request path, against a counted debouncer."""
+    _hass, _entry, coord = _r9f13_make("sg_requests")
+    calls = []
+
+    async def _call():
+        calls.append(1)
+
+    coord._debounced_refresh.async_call = _call
+    gate = solve_gate.gate_for(coord)
+    coord._refresh_task = object()
+    await coord.async_request_refresh()
+    during_refresh = (len(calls), gate.trailing)
+    coord._refresh_task = None
+    gate.solving = True
+    await coord.async_request_refresh()
+    during_solve = (len(calls), gate.rerun)
+    gate.solving = gate.rerun = gate.trailing = False
+    await coord.async_request_refresh()
+    return during_refresh, during_solve, len(calls)
+
+
+_sg_req = _sg_aio.run(_sg_requests())
+R.check(
+    "D1-s1-03: a request during a refresh trails it, one during a solve re-runs it, and only an "
+    "idle one reaches the debouncer -- which drops a call made while it executes",
+    _sg_req == ((0, True), (0, True), 1),
+    f"{_sg_req}",
+)
+
+
+async def _sg_trailing():
+    """A write lands while the refresh fetches: the refresh's end requests one more."""
+    _hass, _entry, coord = _r9f13_make("sg_trailing")
+    loop = _sg_aio.get_running_loop()
+    coord.hass.async_create_task = lambda coro: loop.create_task(coro)
+    calls = []
+
+    async def _call():
+        calls.append(1)
+
+    async def _solve():
+        return None
+
+    real_state = coord._update_current_state
+
+    async def _state_with_write():
+        await real_state()
+        await coord.async_request_refresh()  # a user write mid-refresh
+
+    coord._debounced_refresh.async_call = _call
+    coord.async_run_optimization = _solve
+    coord._update_current_state = _state_with_write
+    await coord.async_refresh()
+    for _ in range(5):
+        await _sg_aio.sleep(0)
+    return len(calls), solve_gate.gate_for(coord).trailing
+
+
+_sg_trail = _sg_aio.run(_sg_trailing())
+R.check(
+    "D1-s1-03: a request landing while a refresh runs is answered by one more debounced "
+    "refresh once it ends, and the trailing mark is spent",
+    _sg_trail == (1, False),
+    f"{_sg_trail}",
+)
+
+
+async def _sg_diagnose():
+    """A diagnose publishes the insight view and asks for no cycle."""
+    _hass, _entry, coord = _r9f13_make("sg_diagnose")
+    coord.data = {"insight": "stale", "sensor_advisor": ["kept"]}
+    requests = []
+
+    async def _req():
+        requests.append(1)
+
+    async def _proc(_hass, _fn, *_args):
+        return None
+
+    coord.async_request_refresh = _req
+    real_proc, real_payload = _sg_cm._await_process, _sg_cm._diagnose_payload
+    _sg_cm._await_process, _sg_cm._diagnose_payload = _proc, lambda _c: ()
+    try:
+        await coord.async_diagnose_interval()
+    finally:
+        _sg_cm._await_process, _sg_cm._diagnose_payload = real_proc, real_payload
+    return len(requests), isinstance(coord.data["insight"], dict), coord.data["sensor_advisor"]
+
+
+_sg_diag = _sg_aio.run(_sg_diagnose())
+R.check(
+    "D9-s1-01: a diagnose press republishes the insight view with the advisor ranking kept, "
+    "and requests no refresh -- so no solve",
+    _sg_diag == (0, True, ["kept"]),
+    f"{_sg_diag}",
+)
+
+
+class _SgDeaf:
+    """A child the kill does not end: every wait times out."""
+
+    def __init__(self):
+        self.killed, self.waits = 0, []
+
+    def kill(self):
+        self.killed += 1
+
+    def wait(self, timeout=None):
+        self.waits.append(timeout)
+        if timeout is None:
+            raise AssertionError("an unbounded wait on a kill-deaf child")
+        raise _sg_sp.TimeoutExpired("worker", timeout)
+
+
+_sg_deaf = _SgDeaf()
+_sg_cm._reap_killed(_sg_deaf)
+R.check(
+    "D1-s3-04: the fault arms' reap of a kill-deaf worker is bounded by the shutdown "
+    "timeout and does not raise",
+    _sg_deaf.killed == 1 and _sg_deaf.waits == [_sg_cm._SHUTDOWN_LOCK_TIMEOUT_S],
+    f"kills={_sg_deaf.killed} waits={_sg_deaf.waits}",
+)
+
+
+class _SgHass:
+    def __init__(self):
+        self.data, self.executor_jobs = {}, 0
+
+    async def async_add_executor_job(self, *_a):
+        self.executor_jobs += 1
+        return "in-process plan"
+
+
+def _sg_fallback_probe(stopping):
+    hass, notes = _SgHass(), []
+
+    async def _dead(*_a):
+        raise _sg_cm.ProcessWorkerUnavailable("killed by the stop")
+
+    real = (_sg_cm._await_process, _sg_cm._note_worker_fallback)
+    _sg_cm._await_process = _dead
+    _sg_cm._note_worker_fallback = lambda *a: notes.append(a)
+    if stopping:
+        hass.data[_sg_cm._WORKER_STOPPING] = True
+    try:
+        out = _sg_aio.run(_sg_cm._await_optimize(hass, None, None))
+    except _sg_cm.ProcessWorkerUnavailable:
+        out = "raised"
+    finally:
+        _sg_cm._await_process, _sg_cm._note_worker_fallback = real
+    return out, len(notes), hass.executor_jobs
+
+
+_sg_stop = _sg_fallback_probe(True)
+_sg_run = _sg_fallback_probe(False)
+R.check(
+    "D1-s1-01: a worker the stop killed raises no fallback notice and runs no in-process "
+    "solve; null control, the same death while running falls back with its notice",
+    _sg_stop == ("raised", 0, 0) and _sg_run == ("in-process plan", 1, 1),
+    f"stopping {_sg_stop}, running {_sg_run}",
+)
+
+
+def _sg_clear_probe(latched):
+    deleted = []
+    real_delete, causes = _sg_cm.ir.async_delete_issue, dict(_sg_cm._WORKER_FALLBACK_CAUSES)
+    _sg_cm.ir.async_delete_issue = lambda _h, _d, issue: deleted.append(issue)
+    _sg_cm._WORKER_FALLBACK_CAUSES.clear()
+    _sg_cm._WORKER_FALLBACK_CAUSES.update(latched)
+    try:
+        _sg_cm._clear_worker_fallback(_SgHass(), "entry-a")
+    finally:
+        _sg_cm.ir.async_delete_issue = real_delete
+        _sg_cm._WORKER_FALLBACK_CAUSES.clear()
+        _sg_cm._WORKER_FALLBACK_CAUSES.update(causes)
+    return deleted
+
+
+_sg_restored = _sg_clear_probe({})
+_sg_other = _sg_clear_probe({"entry-b": "OSError: x"})
+R.check(
+    "D1-s1-01: a healthy solve clears a fallback notice restored from before a restart, "
+    "with no cause latched in this process; null control, another entry's latched cause keeps it",
+    _sg_restored == ["solve_worker_fallback"] and _sg_other == [],
+    f"restored {_sg_restored}, other entry latched {_sg_other}",
+)
+
+
+async def _sg_stop_midsolve():
+    _hass, _entry, coord = _r9f13_make("sg_stop_midsolve")
+
+    async def _killed(*_a):
+        raise _sg_cm.ProcessWorkerUnavailable("killed by the stop")
+
+    real = _sg_cm._await_optimize
+    _sg_cm._await_optimize = _killed
+    coord.hass.data[_sg_cm._WORKER_STOPPING] = True
+    try:
+        reason = await coord.async_run_optimization()
+    finally:
+        _sg_cm._await_optimize = real
+        coord.hass.data.pop(_sg_cm._WORKER_STOPPING, None)
+    return reason, coord._solve_failures, solve_gate.gate_for(coord).solving
+
+
+_r9f13_dt.freeze(_R9F13_NOW)
+_sg_midsolve = _sg_aio.run(_sg_stop_midsolve())
+_r9f13_dt.freeze(None)
+R.check(
+    "D1-s1-01: a solve the stop broke answers 'shutdown', counts no solve failure and "
+    "frees the gate",
+    _sg_midsolve == ("shutdown", 0, False),
+    f"{_sg_midsolve}",
+)
+_sg_view = _r9f13_make("sg_view")[2]
+_sg_view_idle = _sg_view.optimization_running
+solve_gate.gate_for(_sg_view).solving = True
+R.check(
+    "the published optimization_running view reads the solve gate",
+    _sg_view_idle is False and _sg_view.optimization_running is True,
+    f"idle {_sg_view_idle}, solving {_sg_view.optimization_running}",
+)
+
 sys.exit(R.close("FEATURE CHECKS"))
diff --git a/tests/harness.py b/tests/harness.py
index 6ca70cb5b7..5151660edf 100644
--- a/tests/harness.py
+++ b/tests/harness.py
@@ -475,6 +475,12 @@ class FakeCoordinator:
         """The topology the plan sensors publish for the card's setup page."""
         return {"two_zone": False, "dhw": False, "slots": []}
 
+    async def async_refresh(self):
+        """The press's one refresh (D17-s3-01): in an optimizing mode its
+        cycle is what solves, so the fake's refresh runs the fake's solve."""
+        if self.mode in ("auto", "economy"):
+            await self.async_run_optimization()
+
     async def async_run_optimization(self):
         """The press's solve: the fake's answer is that it ran (#1644,
         D10-s1-02 -- the button calls the action's own entry point)."""
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._maybe_refresh_price_tile.GUARD_OFF.210c601b.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._maybe_refresh_price_tile.GUARD_OFF.210c601b.json
deleted file mode 100644
index 730e99cdc7..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._maybe_refresh_price_tile.GUARD_OFF.210c601b.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._maybe_refresh_price_tile GUARD_OFF 210c601b",
-  "killed_by": "tests/features.py",
-  "old": "        if (spec := price_tiles.take(price_tiles.rotation(self), specs, dt_util.now())) is None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_run_optimization.BOOLOP.502b669f.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_run_optimization.BOOLOP.502b669f.json
deleted file mode 100644
index 3419fbfbef..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_run_optimization.BOOLOP.502b669f.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_run_optimization BOOLOP 502b669f",
-  "killed_by": "tests/features.py",
-  "old": "            if self._optimization_rerun_requested and not self._entry_released:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against a15e3e33507bde9e566858ce32b2ded840edfa02: BOOLOP (`if self._optimization_rerun_requested or not self._entry_released:`) took tests/features.py from rc=0 failed=0 to rc=124 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_run_optimization.GUARD_OFF.502b669f.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_run_optimization.GUARD_OFF.502b669f.json
deleted file mode 100644
index 7b0f3e01e0..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_run_optimization.GUARD_OFF.502b669f.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_run_optimization GUARD_OFF 502b669f",
-  "killed_by": "tests/features.py",
-  "old": "            if self._optimization_rerun_requested and not self._entry_released:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against a15e3e33507bde9e566858ce32b2ded840edfa02: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_run_optimization.GUARD_OFF.cfa25e19.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_run_optimization.GUARD_OFF.cfa25e19.json
deleted file mode 100644
index a413c5f053..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_run_optimization.GUARD_OFF.cfa25e19.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_run_optimization GUARD_OFF cfa25e19",
-  "killed_by": "tests/features.py",
-  "old": "                if not _mode_superseded(entry_mode, self._mode):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against c5e1be1967de4b1d29b203aaf73162046dc85bd1: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.1550d375.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.1550d375.json
deleted file mode 100644
index 970af6401d..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.1550d375.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate BOOLOP 1550d375",
-  "killed_by": "tests/features.py",
-  "old": "        ) if steady and days is None else None",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`) if steady or days is None else None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.19646b85.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.19646b85.json
deleted file mode 100644
index 8a9575432a..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.19646b85.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate BOOLOP 19646b85",
-  "killed_by": "tests/features.py",
-  "old": "        banded = base is None and _whatif_banded(self._away_state)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`banded = base is None or _whatif_banded(self._away_state)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.6e295277.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.6e295277.json
deleted file mode 100644
index 0dafcbf4ce..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.6e295277.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate BOOLOP 6e295277",
-  "killed_by": "tests/features.py",
-  "old": "        if limited and (kept := whatif.limited_answer(held, now)) is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if limited or (kept := whatif.limited_answer(held, now)) is not None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.5f80a8b0.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.5f80a8b0.json
deleted file mode 100644
index a2d213e826..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.5f80a8b0.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate GUARD_OFF 5f80a8b0",
-  "killed_by": "tests/features.py",
-  "old": "        if limited:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.6e295277.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.6e295277.json
deleted file mode 100644
index 99ee505c09..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.6e295277.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate GUARD_OFF 6e295277",
-  "killed_by": "tests/structure.py",
-  "old": "        if limited and (kept := whatif.limited_answer(held, now)) is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.7f751e2c.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.7f751e2c.json
deleted file mode 100644
index d6338770e7..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.7f751e2c.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate GUARD_OFF 7f751e2c",
-  "killed_by": "tests/features.py",
-  "old": "        if result is None:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.b2dd1f84.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.b2dd1f84.json
deleted file mode 100644
index 54f7364aa6..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.b2dd1f84.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate GUARD_OFF b2dd1f84",
-  "killed_by": "tests/features.py",
-  "old": "        if limited:  # the slot is spent when a solve starts (#1448, #1753)",
-  "reason": "Recorded by `mutation_table.py --drain` against 994695e06c4c2b78d6420f82c322188317817f91: GUARD_OFF (`if False:  # the slot is spent when a solve starts (#1448, #1753)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.ddb12f29.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.ddb12f29.json
deleted file mode 100644
index 788ed7cc8e..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.ddb12f29.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate GUARD_OFF ddb12f29",
-  "killed_by": "tests/features.py",
-  "old": "        if base is None:",
-  "reason": "Recorded by hand for R9-EG-B1 (#1736) on the branch worktree, 2026-10-04, because `mutation_table.py --pin-killed` refuses on this machine (tests/features.py's baseline is red for the environment: R9-F2.1 P3, BLAS; green on CI) and the count rule cannot credit this kill against that red baseline: GUARD_OFF (`if False:`) takes tests/features.py from rc=1 failed=2 to rc=1 failed=1 -- the mutant's run aborts the whole file early with an uncaught AttributeError (\"'NoneType' object has no attribute 'config'\", the else-branch dereferencing the absent base record), before the environment-red check prints its FAIL line, so the failing-check count lands BELOW the baseline's. A kill is a red run naming a traceback the unmutated baseline does not carry (the hand rule this ledger's R9-EG-A2 entry set); on CI's green baseline the same abort reads failed=1 > 0 and the lane's own rule counts it. Reproduced at the head by applying the mutant alone and running the suite."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.RETURN_DEL.c0eb7824~2.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.RETURN_DEL.c0eb7824~2.json
deleted file mode 100644
index 862c349716..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.RETURN_DEL.c0eb7824~2.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate RETURN_DEL c0eb7824#2",
-  "killed_by": "tests/features.py",
-  "old": "            return {\"error\": str(err), \"rate_limited\": False}",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_clear_worker_fallback.GUARD_OFF.5e16cb51.json b/tests/mutation_ledger/killed_by/coordinator.py/_clear_worker_fallback.GUARD_OFF.5e16cb51.json
deleted file mode 100644
index ca424f3cc7..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/_clear_worker_fallback.GUARD_OFF.5e16cb51.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_clear_worker_fallback GUARD_OFF 5e16cb51",
-  "killed_by": "tests/features.py",
-  "old": "    if _WORKER_FALLBACK_CAUSES.pop(entry_id, None) is None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against a15e3e33507bde9e566858ce32b2ded840edfa02: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/seam_map.json b/tests/seam_map.json
index 00c8668eb9..40e33dcc40 100644
--- a/tests/seam_map.json
+++ b/tests/seam_map.json
@@ -268,6 +268,7 @@
   "system_identification_active": "core",
   "target_temperature": "core",
   "weather_stale_hours": "fetch",
-  "configured_quiet_windows": "dhw"
+  "configured_quiet_windows": "dhw",
+  "async_request_refresh": "core"
  }
 }
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 8f925f20e3..8d4322ca8b 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,8 +1,8 @@
 {
- "class_excess_loc": 17382,
+ "class_excess_loc": 17380,
  "const_modules_over_50": 3,
- "coordinator_attrs": 136,
- "coordinator_multiassigned_attrs": 104,
+ "coordinator_attrs": 135,
+ "coordinator_multiassigned_attrs": 102,
  "coordinator_private_reach": 0,
  "dead_methods": 0,
  "dead_top_level_symbols": 1,
@@ -11,11 +11,11 @@
  "functions_cc_over_25": 7,
  "import_cycle_modules": 0,
  "max_cc": 44,
- "max_class_loc": 7875,
+ "max_class_loc": 7873,
  "max_method_loc": 373,
  "methods_over_150": 14,
  "methods_over_200": 7,
  "name_kept_members": 38,
- "recorded_at": "e352724335c136b65562cd3e71f728549ad04a82",
+ "recorded_at": "ae0ed64af898d8923ac35afe6e9c031ac1e6b111",
  "seam_cut_total": 415
 }

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
