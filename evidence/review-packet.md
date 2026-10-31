# Review packet #3009
head: 1eadcbb3b41198cd4b74c7af16d6b6673308dd84
base: 7d6a95e5edb9564f8ab632bac2a0317c820bb29e

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=124267717027 neutral
arch-score / arch-score id=124267356710 success
arm id=124267138080 skipped
budget-raise-gate / budget-raise-gate id=124267356587 success
cancel-superseded id=124267156641 success
codeql / Analyze (actions) id=124267356302 success
codeql / Analyze (javascript-typescript) id=124267356294 success
codeql / Analyze (python) id=124267356531 in_progress
governance / delivery-status id=124267356288 success
governance / delivery-status-publish id=124267358779 skipped
governance / env-matrix id=124267356372 success
governance / instrument-self-tests id=124267356471 in_progress
governance / policy-docs id=124267356181 success
governance / record id=124267358759 skipped
governance / wave-script id=124267356197 success
hassfest / hassfest id=124267356367 success
kernel-points id=124267358659 skipped
prelude id=124267157063 success
refresh id=124267156907 success
tests / arch-instrument id=124267655464 success
tests / briefs id=124267356429 success
tests / browser id=124267655515 success
tests / closure-scope id=124267356465 success
tests / closures id=124267655694 in_progress
tests / coverage id=124267655636 in_progress
tests / fast (3.14) id=124267655597 in_progress
tests / mutation id=124267356692 failure
tests / mutation-pins (1) id=124267984628 in_progress
tests / nightly-ha id=124267657741 skipped
tests / nightly-status id=124267356638 success
tests / replay id=124267655656 success
tests / typing id=124267655539 success
validate / validate-hacs id=124267356342 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE stale tree: 1eadcbb3b41198cd4b74c7af16d6b6673308dd84 lacks origin/main 4d2f32b2e517c45c44eb0738dc5cb1e3c72287ad; roster read at origin/main
NOTE body item 3299292d: dismissed:a session plugin hook, not repository policy
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         dev/audit/harnesses/r10_cop_gate_vent.py
             `dev/audit/harnesses/r10_cop_gate_vent.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_cop_gate_vent.py
             `dev/audit/harnesses/r10_cop_gate_vent.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_heat_meter.py
             `dev/audit/harnesses/r10_heat_meter.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_thermal_power_option.py
             `dev/audit/harnesses/r10_thermal_power_option.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/features.py
             `tests/features.py` is in the tree at this head
  ok         GATE_SCOPE=auto GATE_SCOPE_BASE=$(git merge-base origin/main HEAD) GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh
             `tests/run.sh` is in the tree at this head
  unverified git diff $(git merge-base origin/main HEAD)...HEAD -- tests/golden/
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff cf4f6b7a660f5b61e0f2b933bd18647fe3ba90c7 HEAD
             `tools/audit/archscore/score.py` is in the tree at this head

FIGURES: 8 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.286162d5.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.286162d5.json
deleted file mode 100644
index cc98dbe3b..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.286162d5.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF 286162d5",
-  "killed_by": "tests/features.py",
-  "old": "        if self._learning_frozen(CONF_POWER_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 9586fce081411da3e552aab930919c40e2b2b233: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
-}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index 88ac5122a..213e679bd 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -3402,7 +3402,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             entry.entry_id,
             lambda: _ctx_of(self)._thermal_params,
             publish=functools.partial(_publish_params, self),
-            frozen=self._learning_frozen,
+            frozen=functools.partial(self._learning_frozen, room_air=False),
             heating_active=lambda: bool(planned().get("dhw_heating_active", False)),
             # The live detector, never a solve's copy of it: no solve runs
             # in comfort, boost or off to refresh one (#1736 H4).
@@ -5014,7 +5014,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         # counters' deltas, so a counter is exempt here; its floor is judged there.
         if self._measured_power is None and not heat_energy.meter_of(self).counter:
             return COP_REFUSED_NO_POWER
-        if self._learning_frozen(CONF_POWER_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY):
+        heat_kw = self._flow_bias.heat_output_kw  # read first: an open window moves no measured heat
+        if self._learning_frozen(CONF_POWER_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY, room_air=heat_kw is None and not heat_energy.meter_of(self).counter):
             return COP_REFUSED_FROZEN
 
         commanded = self._commanded_power()
@@ -5045,7 +5046,6 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         # against a walking ratio EWMA (a fixed gate deadlocks on a true
         # efficiency past it); a draw off the ask needs draw_range's
         # evidence. A measured heat (fold e) leaves the gates nothing to judge.
-        heat_kw = self._flow_bias.heat_output_kw
         ratio = float(cast(float, self._measured_power)) / max(commanded, 1e-6)  # the two guards leave a power here
         # Seeded at 1.0, the model's own expectation, and gated against the
         # value BEFORE this sample updates it, so a first-sample blip cannot
@@ -6571,7 +6571,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         """
         _publish_params(self, **self._model_corrections(dt_util.now()))
 
-    def _learning_frozen(self, *keys: str) -> str | None:
+    def _learning_frozen(self, *keys: str, room_air: bool = True) -> str | None:
         """Why learning should be skipped this interval, or ``None``.
 
         Fail closed. A learner that pauses for an hour loses an hour of
@@ -6637,8 +6637,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
                     return f"{reading.problem}:{key}"
         # #26: training on an open window teaches a phantom heat loss the
         # house does not have — measured in °C-scale residuals, far above
-        # any learning signal.
-        if self._vent_cusum.tripped:
+        # any learning signal. ``room_air=False``: a learner reading no room air.
+        if room_air and self._vent_cusum.tripped:
             return "ventilation"
         # #1935: boost space heating — either surface — actuates heat the
         # plan's trajectory never assumed, so the plant state the interval
@@ -9923,7 +9923,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             return None
         if not np.isfinite(value):
             return None
-        if self._learning_frozen(CONF_DHW_TEMP_ENTITY) is not None:
+        if self._learning_frozen(CONF_DHW_TEMP_ENTITY, room_air=False) is not None:
             return None
         return value
 
diff --git a/dev/audit/harnesses/r10_cop_gate_vent.py b/dev/audit/harnesses/r10_cop_gate_vent.py
new file mode 100755
index 000000000..bc349ddb0
--- /dev/null
+++ b/dev/audit/harnesses/r10_cop_gate_vent.py
@@ -0,0 +1,476 @@
+#!/usr/bin/env python3
+"""R10-COP-GATE item E (carries L1/L2, 8 and 9): the ventilation freeze.
+
+Four arms, all through production symbols at the tree under test:
+
+  cusum    drift.Cusum with the coordinator's constants (VENT_CUSUM_*),
+           fed a synthetic 30-min residual series for 30 days x seeds:
+             null     zero-mean noise only (the null control: must trip ~0)
+             window   noise + an open window every 2nd evening (19:00, 3 h,
+                      +k_vent kW/K air exchange at the interval's dT)
+             ua_bias  noise + a heat-loss scale error f (true UA = model UA
+                      x (1+f)) under a diurnal outdoor swing: the shape a
+                      wrong learned scale (L2, 2.09) puts in the residual
+           reports trips per 30 days and the share of tripped time.
+  learners which learners stop when the vent latch is set: _learning_frozen
+           per learner's own keys, plus the learner entry points
+           (_fold_measured_cop, DhwProfileLearner.async_learn_dynamics,
+           _async_learn_buffer_cooling, _run_system_identification).
+           Null control: latch clear. Perturbation (mutant): a
+           _learning_frozen that drops the vent branch must un-freeze each.
+  latch    carry 9: latch on, a cycle of _update_current_state, then latch
+           off and another cycle; the reason must read "ventilation" then None.
+
+    PYTHONPATH=tests/hastub python3 r10_cop_gate_vent.py
+"""
+from __future__ import annotations
+
+import asyncio
+import math
+import sys
+from datetime import datetime, timedelta, timezone
+
+sys.path[:0] = ["tests", "custom_components"]
+
+import numpy as np  # noqa: E402
+
+from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
+
+from heatpump_optimizer import const  # noqa: E402
+from heatpump_optimizer.drift import Cusum  # noqa: E402
+from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402
+
+P = ThermalParameters()
+UA, C = P.heat_loss_coefficient, P.room_thermal_mass  # kW/K, kWh/K
+DT_H = 0.5
+
+
+def detector() -> Cusum:
+    return Cusum(threshold=const.VENT_CUSUM_THRESHOLD_C, drift=const.VENT_CUSUM_DRIFT_C, side=-1,
+                 clip=const.VENT_CUSUM_CLIP_C, reference_hours=const.VENT_CUSUM_REFERENCE_HOURS)
+
+
+def run_cusum(sigma: float, *, window_k: float = 0.0, f: float = 0.0, seed: int = 0,
+              days: int = 30, t_mean: float = 2.0, t_swing: float = 5.0, room: float = 21.0,
+              front_k: float = 0.0):
+    rng = np.random.default_rng(seed)
+    d = detector()
+    t0 = datetime(2026, 10, 1, tzinfo=timezone.utc)
+    trips = tripped_n = 0
+    n = int(days * 24 / DT_H)
+    for i in range(n):
+        when = t0 + timedelta(hours=i * DT_H)
+        hour = when.hour + when.minute / 60
+        outdoor = t_mean - t_swing * math.cos(2 * math.pi * (hour - 15) / 24)  # coldest ~03:00
+        # A cold front: front_k K colder for two days in every ten, stepped in.
+        if front_k and when.day % 10 in (3, 4):
+            outdoor -= front_k
+        dT = room - outdoor
+        # Price-shaped heat, not dT-shaped: the planner shifts heat to cheap hours.
+        heat_kwh = (3.0 if hour < 6 or 13 <= hour < 16 else 0.6) * DT_H
+        r = rng.normal(0.0, sigma) - f * UA * dT * DT_H / C
+        if window_k and (when.day % 2 == 0) and 19 <= hour < 22:
+            r -= window_k * dT * DT_H / C
+        if d.update(when, float(r), (heat_kwh, 0.0)) and d.tripped:
+            trips += 1
+        tripped_n += d.tripped
+    return trips, tripped_n / n
+
+
+def arm_cusum() -> list[str]:
+    out = ["## cusum (trips / 30 d over 8 seeds: mean [min-max]; tripped share)"]
+    def row(label, **kw):
+        res = [run_cusum(seed=s, **kw) for s in range(8)]
+        t = [r[0] for r in res]
+        share = sum(r[1] for r in res) / len(res)
+        out.append(f"{label:44s} trips={np.mean(t):5.2f} [{min(t)}-{max(t)}] tripped={share:6.1%}")
+    for sigma in (0.05, 0.10, 0.15, 0.20):
+        row(f"null sigma={sigma}", sigma=sigma)
+    for sigma in (0.05, 0.10, 0.15):
+        for k in (0.15, 0.30):
+            row(f"window k={k}kW/K sigma={sigma} (15 events)", sigma=sigma, window_k=k)
+    for sigma in (0.05, 0.10):
+        for f in (0.5, 1.09, 2.0, -0.52):
+            row(f"ua_bias f={f:+.2f} sigma={sigma}", sigma=sigma, f=f)
+        row(f"ua_bias f=+1.09 swing=10 sigma={sigma}", sigma=sigma, f=1.09, t_swing=10.0)
+        row(f"front 8K, f=0 (null for front) sigma={sigma}", sigma=sigma, front_k=8.0)
+        for f in (0.5, 1.09):
+            row(f"front 8K + ua_bias f=+{f:.2f} sigma={sigma}", sigma=sigma, f=f, front_k=8.0)
+    return out
+
+
+CFG = {
+    "tibber_token": "x", "weather_entity": "weather.home",
+    "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
+    "heat_pump_power_entity": "sensor.pump_power",
+    "dhw_temp_entity": "sensor.dhw", "buffer_tank_temp_entity": "sensor.buffer",
+    "heat_pump_max_power": 14.0, "heat_pump_min_power": 1.0,
+}
+STATES = {
+    "sensor.indoor": FakeState("21.0", unit="°C"), "sensor.outdoor": FakeState("2.0", unit="°C"),
+    "sensor.pump_power": FakeState("2200", unit="W"), "sensor.dhw": FakeState("50.0", unit="°C"),
+    "sensor.buffer": FakeState("40.0", unit="°C"),
+}
+
+
+def coordinator():
+    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
+    return HeatPumpOptimizerCoordinator(FakeHass(dict(STATES)), FakeEntry(data=dict(CFG)))
+
+
+async def learner_outcomes(tripped: bool, mutant: bool) -> dict[str, str]:
+    c = coordinator()
+    c._vent_cusum.tripped = tripped
+    if mutant:
+        real = c._learning_frozen
+        c._learning_frozen = lambda *k, **kw: (None if (r := real(*k, **kw)) == "ventilation" else r)
+        c._dhw_learner._frozen = c._learning_frozen
+    out = {}
+    # COP: the guard's refusal code; anything past the freeze gate is "passes freeze".
+    c._measured_power, c._current_action = 2.2, {"power": 2.1, "dhw_power": 0.0}
+    code = c._fold_measured_cop(None)
+    out["cop(_fold_measured_cop)"] = f"refused:{code}" if code == const_cop_frozen() else f"passes freeze ({code})"
+    # The fixer's rows: the same fold with measured heat evidence, a counter
+    # install (its span gate) and a measured flow heat.
+    from heatpump_optimizer import heat_energy as _he
+    _he.meter_of(c).counter = True
+    code = c._fold_measured_cop(None)
+    out["cop counter(_fold_measured_cop)"] = f"refused:{code}" if code == const_cop_frozen() else f"passes freeze ({code})"
+    _he.meter_of(c).counter = False
+    c._flow_bias.heat_output_kw = 2.2 * 3.0
+    code = c._fold_measured_cop(None)
+    out["cop flow-heat(_fold_measured_cop)"] = f"refused:{code}" if code == const_cop_frozen() else f"passes freeze ({code})"
+    c._flow_bias.heat_output_kw = None
+    # DHW: returns the freeze reason, or None when it ran.
+    t0 = datetime.now(timezone.utc)
+    await c._dhw_learner.async_learn_dynamics(50.0)
+    c._dhw_learner.last_sample_time = t0 - timedelta(minutes=30)
+    r = await c._dhw_learner.async_learn_dynamics(49.8)
+    out["dhw(async_learn_dynamics)"] = f"frozen:{r}" if r else "runs"
+    # Buffer: sets _learner_freeze_reason on a freeze.
+    c._learner_freeze_reason = None
+    await c._async_learn_buffer_cooling(40.0)
+    out["buffer(_async_learn_buffer_cooling)"] = f"frozen:{c._learner_freeze_reason}" if c._learner_freeze_reason else "runs"
+    # sysid: aborts an active experiment with the freeze reason.
+    from heatpump_optimizer import sysid as _s
+    c._sysid.phase = next(v for k, v in vars(_s).items() if k.startswith("PHASE_") and v not in (_s.PHASE_ABORTED,) and k not in ("PHASE_IDLE", "PHASE_DONE", "PHASE_COMPLETE"))
+    try:
+        active = c._sysid.active
+    except Exception:  # noqa: BLE001
+        active = None
+    try:
+        await c._run_system_identification(np.full(48, 1.0))
+    except Exception as e:  # noqa: BLE001 - past the gate the experiment needs more state
+        out["sysid(_run_system_identification)"] = f"passes freeze (raised {type(e).__name__})"
+    else:
+        res = c._sysid.result
+        out["sysid(_run_system_identification)"] = (
+            f"aborted:{res.reason}" if res is not None and res.reason == "ventilation"
+            else f"passes freeze (later outcome {getattr(res, 'reason', None)!r}, active-before={active})")
+    # The house learner's own keys, for the record.
+    out["house(_learning_frozen keys)"] = str(c._learning_frozen("indoor_temp_entity", "outdoor_temp_entity"))
+    return out
+
+
+def const_cop_frozen():
+    from heatpump_optimizer import coordinator as co
+    return co.COP_REFUSED_FROZEN
+
+
+async def arm_learners() -> list[str]:
+    out = ["## learners on the vent latch (latch | null: latch clear | mutant: vent branch dropped)"]
+    a, b, m = (await learner_outcomes(True, False), await learner_outcomes(False, False),
+               await learner_outcomes(True, True))
+    for k in a:
+        out.append(f"{k:40s} {a[k]:34s} | {b[k]:30s} | {m[k]}")
+    return out
+
+
+async def arm_latch() -> list[str]:
+    c = coordinator()
+    seq = []
+    for tripped in (True, True, False, False):
+        c._vent_cusum.tripped = tripped
+        await c._update_current_state()
+        seq.append(f"latch={tripped}: learner_freeze_reason={c._learner_freeze_reason}")
+    return ["## latch on-then-off (carry 9), consecutive _update_current_state cycles"] + seq
+
+
+# --- round 2: the window through each lifted learner's production fold ---
+from heatpump_optimizer import draw_range as _dr  # noqa: E402
+
+OUT_C, ROOM_C = -10.0, 21.0          # outside the frost band (0..4 C), so no defrost gate
+DESIGN_DT = 31.0                     # steady room-outdoor dT at OUT_C
+
+
+def window_excess(k_vent: float, days: int = 30) -> list[float]:
+    """Per 30-min interval, the fractional rise of the emitters' heat at a FIXED
+    flow temperature: a first-order room (default UA, C) whose emitter UA is
+    backed out of the steady load at ``emitter_design_delta_t``; an open window
+    adds ``k_vent`` kW/K from 19:00 for 3 h every second day and the room then
+    recovers on the same emitters. 0.0 everywhere for k_vent=0 (the null)."""
+    q0 = UA * DESIGN_DT
+    u_em = q0 / P.emitter_design_delta_t_floored
+    t_flow = ROOM_C + q0 / u_em
+    room, out = ROOM_C, []
+    n = int(days * 24 / DT_H)
+    for i in range(n):
+        hour, day = (i * DT_H) % 24, int(i * DT_H // 24)
+        k = k_vent if (day % 2 == 0 and 19 <= hour < 22) else 0.0
+        for _ in range(30):                      # 1-min Euler steps
+            q_em = u_em * (t_flow - room)
+            room += (q_em - (UA + k) * (room - OUT_C)) * (1 / 60) / C
+        out.append(u_em * (ROOM_C - room) / q0)  # delta = extra heat / nominal heat
+    return out
+
+
+def cop_coordinator():
+    c = coordinator()
+    st = getattr(c, "_ctx", c)._current_state
+    st.outdoor_temperature = OUT_C
+    cop = c._thermal_model.compute_cop(OUT_C)
+    ask = UA * DESIGN_DT / cop
+    c._current_action = {"power": ask, "dhw_power": 0.0}
+    return c, ask, cop
+
+
+def follows_draw(ask: float) -> "_dr.DrawRange":
+    """A draw window whose evidence says the draw follows the ask."""
+    d = _dr.DrawRange()
+    rng = np.random.default_rng(7)
+    for _ in range(_dr.MIN_SAMPLES + 12):
+        a = ask * rng.choice((0.6, 1.0, 1.4))
+        d.observe(a * (1 + rng.normal(0, 0.02)), a, P.min_electrical_power, P.max_electrical_power)
+    return d
+
+
+def run_cop(path: str, k_vent: float, seed: int, evidence: str) -> tuple[float, int, int]:
+    """Feed 30 d of intervals through the production COP fold, latch clear.
+
+    path: inferred   _fold_measured_cop, no heat reading (cop_evidence's inference)
+          flow       _fold_measured_cop with a measured flow heat (_flow_bias.heat_output_kw)
+          span       _fold_cop_evidence on counter deltas, as _async_learn_heat_span calls it
+    The pump's true COP never changes: at a fixed flow the emitters take (1+d)
+    times the heat and the compressor draws (1+d) times the power. Returns
+    (final cop_scale, folds, folds inside a window-perturbed interval)."""
+    c, ask, cop = cop_coordinator()
+    rng = np.random.default_rng(seed)
+    draw = follows_draw(ask) if evidence == "follows" else None
+    folds = wfolds = 0
+    for d in window_excess(k_vent):
+        noise = rng.normal(0, 0.03)
+        elec = ask * (1 + d) * (1 + noise)
+        heat = cop * elec   # the true COP is the model's curve at scale 1, window or not
+        c._measured_power = elec
+        before = c._cop_samples
+        if path == "span":
+            c._flow_bias.heat_output_kw = None
+            c._fold_cop_evidence(ask, elec, heat, c._cop_reference_curve((heat, None)))
+        else:
+            c._flow_bias.heat_output_kw = heat if path == "flow" else None
+            c._fold_measured_cop(draw)
+        if c._cop_samples != before:
+            folds += 1
+            wfolds += d > 0.005
+    return c._cop_scale, folds, wfolds
+
+
+def arm_cop_window() -> list[str]:
+    out = ["## cop under a window, latch clear (cop_scale after 30 d; truth 1.000; 8 seeds mean [min-max]; folds; folds on an interval the window raised by >0.5 %)"]
+    for path, ev in (("inferred", "none"), ("inferred", "follows"), ("flow", "none"), ("span", "none")):
+        for k in (0.0, 0.15, 0.30):
+            res = [run_cop(path, k, s, ev) for s in range(8)]
+            sc = [r[0] for r in res]
+            out.append(f"{path:8s} draw-evidence={ev:7s} k={k:.2f} scale={np.mean(sc):.3f} [{min(sc):.3f}-{max(sc):.3f}] "
+                       f"folds={res[0][1]} window-folds={res[0][2]}")
+    ex = window_excess(0.30)
+    for k in (0.15, 0.30):
+        ex = window_excess(k)
+        out.append(f"(window k={k:.2f}: excess peak {max(ex):+.1%}, 30-d mean {np.mean(ex):+.2%}, intervals over COP_ASK_TOLERANCE {sum(e > 0.15 for e in ex)})")
+    out.append(f"(window excess at k=0.30: peak {max(ex):+.1%}, mean over perturbed intervals {np.mean([e for e in ex if e > 0.005]):+.1%};"
+               f" k=0.15 peak {max(window_excess(0.15)):+.1%})")
+    return out
+
+
+def run_draw(k_vent: float, seed: int):
+    """draw_range.fold, frozen=False, on a price-shaped ask; the drawn kW is the
+    ask times the window excess. Returns follows_ask, the log-log slope, engaged
+    and planned() after 30 d."""
+    d = _dr.DrawRange()
+    rng = np.random.default_rng(seed)
+    for i, e in enumerate(window_excess(k_vent)):
+        hour = (i * DT_H) % 24
+        ask = 2.4 if hour < 6 or 13 <= hour < 16 else (1.6 if 16 <= hour < 23 else 1.2)
+        drawn = ask * (1 + e) * (1 + rng.normal(0, 0.03))
+        _dr.fold(d, drawn, (ask, 0.0), P, frozen=False, distorted=False, defrost=False, command=None)
+    pairs = np.array([(dd, a) for dd, a, _ in d._evidence()], dtype=float)
+    la, ld = np.log(pairs[:, 1]), np.log(pairs[:, 0])
+    la = la - la.mean()
+    slope = float(np.dot(la, ld - ld.mean()) / np.dot(la, la))
+    return _dr.follows_ask(d), slope, d.engaged, d.planned(P.min_electrical_power, P.max_electrical_power), d.observed()
+
+
+def arm_draw_window() -> list[str]:
+    out = ["## draw_range.fold under a window, frozen=False (8 seeds: slope mean [min-max]; follows; engaged; planned)"]
+    for k in (0.0, 0.15, 0.30):
+        res = [run_draw(k, s) for s in range(8)]
+        sl = [r[1] for r in res]
+        out.append(f"k={k:.2f} slope={np.mean(sl):.3f} [{min(sl):.3f}-{max(sl):.3f}] follows={sorted({str(r[0]) for r in res})} "
+                   f"engaged={sorted({r[2] for r in res})} planned={sorted({str(r[3]) for r in res})} observed0={res[0][4]}")
+    return out
+
+
+async def run_buffer(g: float, k_vent: float) -> tuple[float, int]:
+    """_async_learn_buffer_cooling on pump-off 30-min intervals, latch clear.
+    The tank loses to its room (standby UA_s) and, with the circulation pump
+    running, ``g`` kW/K into the emitters at the ROOM's temperature, which the
+    window lowers. g=0 is the modelled no-valve topology (draw == pump heat)."""
+    c = coordinator()
+    c._current_action = {"power": 0.0, "dhw_power": 0.0}
+    cbuf = P.buffer_tank_volume * 1.163 / 1000.0          # kWh/K
+    ua_s = 0.04 * cbuf                                     # ~1 C/h at the 25 K reference
+    q0 = UA * DESIGN_DT
+    u_em = q0 / P.emitter_design_delta_t_floored
+    ex = window_excess(k_vent)
+    for i, e in enumerate(ex):
+        room = ROOM_C - e * q0 / u_em
+        tb0 = 45.0
+        k = (ua_s + g) / cbuf                               # per hour
+        t_inf = (ua_s * 20.0 + g * room) / (ua_s + g)
+        tb1 = t_inf + (tb0 - t_inf) * math.exp(-k * DT_H)
+        c._last_buffer_temp_sample = tb0
+        c._last_buffer_sample_time = datetime.now(timezone.utc) - timedelta(hours=DT_H)
+        c._buffer_heating_since_sample = False
+        await c._async_learn_buffer_cooling(tb1)
+    return c._buffer_cooling_rate, c._buffer_cooling_samples
+
+
+async def arm_buffer_window() -> list[str]:
+    out = ["## buffer cooling under a window, latch clear (learned C/h after 30 d; samples)"]
+    for g in (0.0, 0.0005, 0.002):
+        for k in (0.0, 0.30):
+            r, n = await run_buffer(g, k)
+            out.append(f"g={g:.4f}kW/K k={k:.2f} rate={r:.4f} samples={n}")
+    return out
+
+
+# --- round 3: the window through _fold_flow_lift (coordinator.py:878) ---
+SPREAD_K = 5.0      # flow-return design spread; supply = mean water + spread/2
+
+
+def room_series(k_vent: float, law: str, days: int = 30) -> list[tuple[float, float]]:
+    """Per 30-min interval, (room degC, emitter heat kW) under a plant law.
+
+    a   commanded heat: the emitters deliver the nominal hold heat q0 whatever
+        the room does (the reviewer's law); a window cools the room and the
+        room recovers only on the house's own constant.
+    a2  sensitivity, not the rule: the plan replans each interval, asking q0
+        plus C*(target-room)/6 h, capped at the nameplate heat.
+    b   the curve held (round 2's model): the flow temperature is fixed, so
+        supply is room-independent by construction (the null by construction).
+    Same window as round 2: +k_vent kW/K from 19:00 for 3 h every second day."""
+    q0 = UA * DESIGN_DT
+    u_em = q0 / P.emitter_design_delta_t_floored
+    t_flow = ROOM_C + q0 / u_em
+    qmax = P.max_electrical_power * P.cop_nominal_floored
+    room, out = ROOM_C, []
+    for i in range(int(days * 24 / DT_H)):
+        hour, day = (i * DT_H) % 24, int(i * DT_H // 24)
+        k = k_vent if (day % 2 == 0 and 19 <= hour < 22) else 0.0
+        if law == "a":
+            q = q0
+        elif law == "a2":
+            q = min(q0 + C * max(ROOM_C - room, 0.0) / 6.0, qmax)
+        for _ in range(30):
+            if law == "b":
+                q = u_em * (t_flow - room)
+            room += (q - (UA + k) * (room - OUT_C)) * (1 / 60) / C
+        out.append((room, q))
+    return out
+
+
+def flow_coordinator():
+    c = coordinator()
+    ctx = getattr(c, "_ctx", c)
+    ctx._current_state.outdoor_temperature = OUT_C
+    return c, ctx
+
+
+def run_flow(law: str, k_vent: float, seed: int, *, latch: bool = False) -> tuple[float, float, float, float, int, float]:
+    """30 d of cycles through the production _fold_flow_lift, latch clear.
+
+    Supply under law a/a2: room + Q/UA_em + SPREAD_K/2, with UA_em the model's
+    own (nameplate x COP_nominal / emitter_design_delta_t, the curve's), so the
+    no-window supply sits SPREAD_K/2 above the curve. Under law b: the curve
+    plus SPREAD_K/2. +-0.3 K sensor noise per sample. Returns (final bias_k,
+    30-d mean, min, max, folds, curve)."""
+    c, ctx = flow_coordinator()
+    c._vent_cusum.tripped = latch
+    p = c._thermal_model.params
+    ua_em = p.max_electrical_power * p.cop_nominal_floored / p.emitter_design_delta_t_floored
+    from heatpump_optimizer.flow_lift import curve_supply_temp
+    from heatpump_optimizer.coordinator import _fold_flow_lift
+    curve = curve_supply_temp(c._thermal_model, OUT_C, c.target_temperature)
+    cop = c._thermal_model.compute_cop(OUT_C)
+    rng = np.random.default_rng(seed)
+    hist, folds = [], 0
+    now = datetime.now(timezone.utc)
+    for room, q in room_series(k_vent, law):
+        supply = (curve if law == "b" else room + q / ua_em) + SPREAD_K / 2 + rng.normal(0, 0.3)
+        c._current_action = {"power": q / cop, "dhw_power": 0.0}
+        c._flow_bias.observe_temps(supply, None, None)
+        before = c._flow_bias.samples
+        _fold_flow_lift(c, now)
+        folds += c._flow_bias.samples != before
+        hist.append(c._flow_bias.bias_k)
+    return hist[-1], float(np.mean(hist)), min(hist), max(hist), folds, curve
+
+
+def arm_flow_window() -> list[str]:
+    out = ["## _fold_flow_lift under a window, latch clear (bias_k K after 30 d; 8 seeds: final mean [min-max] | 30-d mean [min-max] | run min..max; folds)"]
+    means = {}
+    for law in ("a", "b", "a2"):
+        for k in (0.0, 0.15, 0.30):
+            res = [run_flow(law, k, s) for s in range(8)]
+            fi, mn = [r[0] for r in res], [r[1] for r in res]
+            means[law, k] = float(np.mean(mn))
+            out.append(f"law={law:2s} k={k:.2f} final={np.mean(fi):+.3f} [{min(fi):+.3f}..{max(fi):+.3f}] "
+                       f"mean={np.mean(mn):+.3f} [{min(mn):+.3f}..{max(mn):+.3f}] "
+                       f"run={min(r[2] for r in res):+.3f}..{max(r[3] for r in res):+.3f} folds={res[0][4]}")
+    for law in ("a", "a2"):
+        for k in (0.15, 0.30):
+            rs = room_series(k, law)
+            out.append(f"(law {law} k={k:.2f}: room min {min(r for r, _ in rs):.2f} C, 30-d mean {np.mean([r for r, _ in rs]):.2f} C, last {rs[-1][0]:.2f} C)")
+    c, _ = flow_coordinator()
+    out.append(f"(curve at {OUT_C} C, target {c.target_temperature}: {run_flow('b', 0.0, 0)[5]:.2f} C; "
+               f"latch set, law a k=0.30: folds={run_flow('a', 0.30, 0, latch=True)[4]})")
+    # What a shift costs where it is priced: flow_lift_factor reads curve +
+    # bias only above cop_flow_reference_temp, so price each arm's 30-d mean
+    # shift (window minus its own no-window null) on plants at 25/40/50 C.
+    m = c._thermal_model
+    curve = m.curve_flow_temp(OUT_C)
+    out.append(f"(priced at {OUT_C} C; cop_flow_reference_temp={m.params.cop_flow_reference_temp} C)")
+    for plant in (25.0, 40.0, 50.0):
+        b0 = plant - curve
+        m.params.flow_curve_bias = b0
+        f0 = m.flow_lift_factor(OUT_C, m.curve_flow_temp(OUT_C))
+        row = []
+        for law, k in (("a", 0.15), ("a", 0.30), ("a2", 0.15), ("a2", 0.30), ("b", 0.30)):
+            d = means[law, k] - means[law, 0.0]
+            m.params.flow_curve_bias = b0 + d
+            f = m.flow_lift_factor(OUT_C, m.curve_flow_temp(OUT_C))
+            row.append(f"{law}/{k:.2f} shift {d:+.3f} K factor {f / f0 - 1:+.2%}")
+        out.append(f"(plant {plant:.0f} C, bias {b0:+.2f} K, factor {f0:.4f}: " + "; ".join(row) + ")")
+    m.params.flow_curve_bias = 0.0
+    return out
+
+
+async def main() -> None:
+    lines = (arm_cusum() + await arm_learners() + await arm_latch()
+             + arm_cop_window() + arm_draw_window() + await arm_buffer_window()
+             + arm_flow_window())
+    print("\n".join(lines))
+
+
+if __name__ == "__main__":
+    asyncio.run(main())
diff --git a/dev/audit/harnesses/r10_heat_meter.py b/dev/audit/harnesses/r10_heat_meter.py
index 222052bb3..408c203ef 100644
--- a/dev/audit/harnesses/r10_heat_meter.py
+++ b/dev/audit/harnesses/r10_heat_meter.py
@@ -129,7 +129,7 @@ class Gate:
         self._last_house_sample = None
         self._last_house_sample_time = None
 
-    def _learning_frozen(self, *keys):
+    def _learning_frozen(self, *keys, room_air=True):
         return None
 
     def _observe_cop_health(self, observed_cop, dhw_curve=False):
diff --git a/dev/audit/harnesses/r10_thermal_power_option.py b/dev/audit/harnesses/r10_thermal_power_option.py
index dcb109580..af2745d70 100644
--- a/dev/audit/harnesses/r10_thermal_power_option.py
+++ b/dev/audit/harnesses/r10_thermal_power_option.py
@@ -86,7 +86,7 @@ class Gate:
         self._immersion_active = False
         self._flow_bias = flow_lift.FlowCurveBias()
 
-    def _learning_frozen(self, *keys):
+    def _learning_frozen(self, *keys, room_air=True):
         return None
 
     def _observe_cop_health(self, observed_cop, dhw_curve=False):
diff --git a/dev/programme/delivery/3009.md b/dev/programme/delivery/3009.md
new file mode 100644
index 000000000..217b7f816
--- /dev/null
+++ b/dev/programme/delivery/3009.md
@@ -0,0 +1 @@
+- [#3009](https://github.com/tvofi/heatpump_optimizer/pull/3009) — **open**, R10-COP-GATE item E: vent freeze skips only learners room air cannot reach (R10-COP-GATE)
diff --git a/tests/closures.json b/tests/closures.json
index ceb95f3f0..22371b696 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3884,6 +3884,7 @@
    "dev/audit/harnesses/r10_codescan_wait_race.py",
    "dev/audit/harnesses/r10_configflow_pages.py",
    "dev/audit/harnesses/r10_cop_gate.py",
+   "dev/audit/harnesses/r10_cop_gate_vent.py",
    "dev/audit/harnesses/r10_cop_partload.py",
    "dev/audit/harnesses/r10_cop_partload_equiv.py",
    "dev/audit/harnesses/r10_critpath_archive_parity.py",
diff --git a/tests/features.py b/tests/features.py
index d82394cf4..9070611dd 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -8053,7 +8053,7 @@ class _CopGate:
         self._flow_bias = flow_lift.FlowCurveBias()
         self.cop_health_calls: list = []
 
-    def _learning_frozen(self, *entities):
+    def _learning_frozen(self, *entities, room_air=True):
         return None
 
     def _observe_cop_health(self, observed_cop, dhw_curve=False):
@@ -22129,12 +22129,12 @@ _t9 = datetime(2026, 1, 21, 6, 0, tzinfo=UTC)
 _c9._accuracy.note_lead_prediction(_t9 - timedelta(minutes=10), 1.0, 21.0)
 _dt5.freeze(_t9)
 try:
-    _c9._learning_frozen = lambda key: "stale"
+    _c9._learning_frozen = lambda key, **_kw: "stale"
     _c9._record_accuracy()
     _frozen_kept = (
         len(_c9._accuracy.lead_pending) == 1 and _c9._accuracy.sigma(1.0) == 0.0
     )
-    _c9._learning_frozen = lambda key: None
+    _c9._learning_frozen = lambda key, **_kw: None
     _c9._record_accuracy()
     _live_scored = (
         not _c9._accuracy.lead_pending
@@ -45570,7 +45570,7 @@ from homeassistant.util import dt as _t2_dt  # noqa: E402
 
 def _t2_room_readers(**config):
     c = _t2_coord(curve_learning_enabled=True, **config)
-    c._learning_frozen = lambda *keys: None
+    c._learning_frozen = lambda *keys, **_kw: None
     c._mode = "auto"
     now = datetime(2026, 1, 21, 6, 0, tzinfo=UTC)
     c._accuracy.note_lead_prediction(now - timedelta(minutes=10), 1.0, 21.5)
@@ -45610,7 +45610,7 @@ R.check(
     f"{_wzm((None, float('nan')), 19.0)!r}",
 )
 _t2_nan_zones = _t2_coord(curve_learning_enabled=True, indoor_temp_entity="sensor.indoor")
-_t2_nan_zones._learning_frozen = lambda *keys: None
+_t2_nan_zones._learning_frozen = lambda *keys, **_kw: None
 _t2_nan_zones._current_state = _dc_replace(
     _t2_nan_zones._current_state, room_temperature=float("nan"),
     upper_floor_temperature=float("nan"), lower_floor_temperature=float("nan"),
@@ -56053,7 +56053,7 @@ R.check(
 
 # _track_curve_comfort folds YESTERDAY's worst margin when a new day starts.
 _p8s_cc = _Coord(_FakeHass(), _FakeEntry(data={**_P8_CFG, "curve_learning_enabled": True}))
-_p8s_cc._learning_frozen = lambda key: None
+_p8s_cc._learning_frozen = lambda key, **_kw: None
 _p8s_days = []
 _p8s_cc._curve_learner = _p8s_ns(
     bias=0.0,
@@ -67091,7 +67091,7 @@ R.check(
     f"{_cf_diag._coordinator_snapshot(_cf_ref).get('cop_learner')}",
 )
 _cf_frz = _cf_coord()
-_cf_frz._learning_frozen = lambda *entities: "stale_inputs"
+_cf_frz._learning_frozen = lambda *entities, **_kw: "stale_inputs"
 _cf_learn(_cf_frz, 2.2)
 _cf_none = _cf_coord()
 _cf_none._measured_power = None
@@ -72375,6 +72375,156 @@ R.check(
 )
 
 
+# --- R10-COP-GATE item E: the open-window latch freezes only room-air learners --
+# ``_learning_frozen(room_air=False)`` skips the ventilation reason alone. The
+# measured-heat COP paths (a counter span, a measured flow heat) and hot water
+# lift; the inferred COP, the flow-curve bias and every room-air learner keep
+# the freeze (dev/audit/harnesses/r10_cop_gate_vent.py measures each arm).
+from heatpump_optimizer import coordinator as _cv_cm  # noqa: E402
+from heatpump_optimizer import draw_range as _cv_dr  # noqa: E402
+from heatpump_optimizer import heat_energy as _cv_he  # noqa: E402
+from heatpump_optimizer import sysid as _cv_sysid  # noqa: E402
+from heatpump_optimizer.accuracy import COP_REFUSED_SPAN_OPEN as _CV_OPEN  # noqa: E402
+
+
+def _cv_cop(latch, *, counter=False, heat_kw=None, heat_age_min=None):
+    """One COP fold on the real coordinator: (refusal, samples folded).
+
+    ``heat_age_min`` plants a thermal-power entity and reads it through the
+    cycle's own ``observe_water``; otherwise ``heat_kw`` is the flow heat."""
+    c = _t2_coord(heat_pump_power_entity="sensor.hp_power",
+                  **({_TP_KEY: "sensor.heat"} if heat_age_min is not None else {}))
+    c._vent_cusum.tripped = latch
+    if counter:
+        _cv_he.meter_of(c).counter = True
+    if heat_age_min is not None:
+        c.hass.states.set("sensor.heat", FakeState(
+            "6000", last_updated=minutes_ago(heat_age_min + 3, NOW),
+            last_reported=minutes_ago(heat_age_min, NOW), unit="W"))
+        reader = _fmReader(c.hass, c.effective_config, now=lambda: NOW)
+        _fm.observe_water(c._flow_bias, reader, c.effective_config)
+        c._input_health = reader.health
+    else:
+        c._flow_bias.heat_output_kw = heat_kw
+    c._measured_power = 2.0
+    c._current_action = {"power": 2.0}
+    c._current_state.outdoor_temperature = 8.0
+    before = c._cop_samples
+    c._learn_measured_cop()
+    return c._measured_cop.refusal, c._cop_samples - before
+
+
+_cv_counter, _cv_counter0 = _cv_cop(True, counter=True), _cv_cop(False, counter=True)
+R.check(
+    "R10-COP-GATE E: under the window latch a heat-counter install reaches the span "
+    "gate rather than the freeze (null control: latch clear reads the same)",
+    _cv_counter[0] == _CV_OPEN and _cv_counter0[0] == _CV_OPEN,
+    f"latch {_cv_counter!r} clear {_cv_counter0!r}",
+)
+_cv_flow, _cv_flow0 = _cv_cop(True, heat_kw=6.0), _cv_cop(False, heat_kw=6.0)
+R.check(
+    "R10-COP-GATE E: under the window latch a measured flow heat folds its COP "
+    "(null control: latch clear folds too)",
+    _cv_flow == (None, 1) and _cv_flow0 == (None, 1),
+    f"latch {_cv_flow!r} clear {_cv_flow0!r}",
+)
+_cv_stale, _cv_fresh = _cv_cop(True, heat_age_min=45), _cv_cop(True, heat_age_min=1)
+R.check(
+    "R10-COP-GATE E: a stale thermal-power entity read through observe_water still "
+    "freezes the COP fold under the latch (null control: a fresh one folds)",
+    _cv_stale == (_TP_FROZEN, 0) and _cv_fresh == (None, 1),
+    f"stale {_cv_stale!r} fresh {_cv_fresh!r}",
+)
+_cv_inf, _cv_inf0 = _cv_cop(True), _cv_cop(False)
+R.check(
+    "R10-COP-GATE E: an inferred COP (no heat reading) stays frozen under the "
+    "window latch (null control: latch clear passes the freeze)",
+    _cv_inf == (_TP_FROZEN, 0) and _cv_inf0[0] != _TP_FROZEN,
+    f"latch {_cv_inf!r} clear {_cv_inf0!r}",
+)
+
+
+def _cv_dhw(latch):
+    """(probe value, the learner's freeze reason) on a configured tank."""
+    c = _t2_coord(dhw_temp_entity="sensor.tank")
+    c._vent_cusum.tripped = latch
+    c._dhw_temperature = 55.0
+    learner = c._dhw_learner
+
+    async def learn():
+        await learner.async_learn_dynamics(50.0)
+        learner.last_sample_time = dt_util.now() - timedelta(minutes=30)
+        return await learner.async_learn_dynamics(49.8)
+
+    return c._dhw_probe_temperature(), _asyncio.run(learn())
+
+
+_cv_dhw1, _cv_dhw0 = _cv_dhw(True), _cv_dhw(False)
+R.check(
+    "R10-COP-GATE E: hot water learns and the probe answers under the window latch "
+    "(null control: latch clear reads the same)",
+    _cv_dhw1 == (55.0, None) and _cv_dhw0 == (55.0, None),
+    f"latch {_cv_dhw1!r} clear {_cv_dhw0!r}",
+)
+
+
+def _cv_room_air(latch):
+    """What each learner the latch must still freeze does with it set."""
+    out = {}
+    b = _t2_coord(buffer_tank_temp_entity="sensor.buffer")
+    b._vent_cusum.tripped = latch
+    b._learner_freeze_reason = None
+    _asyncio.run(b._async_learn_buffer_cooling(40.0))
+    out["buffer"] = b._learner_freeze_reason
+    d = _t2_coord(heat_pump_power_entity="sensor.hp_power")
+    d._vent_cusum.tripped = latch
+    d._measured_power = 2.0
+    d._pending_prediction = {"when": dt_util.now() - timedelta(minutes=30), "power": 2.0,
+                             "price": None, "predicted_temp": None, "outdoor": None,
+                             "split": (2.0, 0.0)}
+    seen, real = [], _cv_dr.fold
+    _cv_dr.fold = lambda *a, **k: seen.append(k["frozen"])
+    try:
+        d._record_accuracy()
+    finally:
+        _cv_dr.fold = real
+    out["draw_frozen"] = seen
+    s = _t2_coord()
+    s._vent_cusum.tripped = latch
+    s._sysid.phase = _cv_sysid.PHASE_STEP
+    _asyncio.run(s._run_system_identification(np.full(48, 1.0)))
+    out["sysid"] = getattr(s._sysid.result, "reason", None)
+    for name, method, kw in (("house", _HOUSE_LEARNER, {}), ("lower", _LOWER_LEARNER, {"two_zone": True})):
+        h = _t2_house(**kw)
+        h._vent_cusum.tripped = latch
+        before = (h._house_heat_loss_samples, h._thermal_params)
+        _t2_drive(h, method)
+        out[name] = (h._learner_freeze_reason, (h._house_heat_loss_samples, h._thermal_params) == before)
+    f = _t2_coord()
+    f._vent_cusum.tripped = latch
+    f._current_action = {"power": 2.0, "dhw_power": 0.0}
+    f._current_state.outdoor_temperature = -10.0
+    f._flow_bias.observe_temps(30.0, 25.0)
+    before = f._flow_bias.samples
+    _cv_cm._fold_flow_lift(f, dt_util.now())
+    out["flow_bias_folds"] = f._flow_bias.samples - before
+    return out
+
+
+_cv_ra1, _cv_ra0 = _cv_room_air(True), _cv_room_air(False)
+R.check(
+    "R10-COP-GATE E: the buffer, draw range, system identification, house and lower "
+    "floor still freeze on the window latch, and the flow-curve bias takes no sample "
+    "(null control: latch clear, the bias folds and nothing reads ventilation)",
+    _cv_ra1 == {"buffer": "ventilation", "draw_frozen": [True], "sysid": "ventilation",
+                "house": ("ventilation", True), "lower": ("ventilation", True),
+                "flow_bias_folds": 0}
+    and _cv_ra0["flow_bias_folds"] == 1 and _cv_ra0["draw_frozen"] == [False]
+    and "ventilation" not in repr(_cv_ra0),
+    f"latch {_cv_ra1!r} clear {_cv_ra0!r}",
+)
+
+
 # --- R10-COP-PARTLOAD: COP falls with compressor power ------------------------
 # Synthetic throughout. ``cop_partload_derate`` is the share of COP lost at max
 # power against min power (dev/audit/harnesses/r10_cop_partload.py measures it
@@ -73530,7 +73680,7 @@ def _he_heartbeat(reasons):
     c = _t2_coord()
     c._snapshots_loaded = True
     feed = iter(reasons)
-    c._learning_frozen = lambda *keys: next(feed)
+    c._learning_frozen = lambda *keys, **_kw: next(feed)
     saves = []
 
     async def _save():
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.286162d5.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.286162d5.json
deleted file mode 100644
index cc98dbe3b..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.286162d5.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF 286162d5",
-  "killed_by": "tests/features.py",
-  "old": "        if self._learning_frozen(CONF_POWER_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 9586fce081411da3e552aab930919c40e2b2b233: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
-}

