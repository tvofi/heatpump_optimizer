# Review packet #3371
head: ce4cdb2271c3a3883c422e228f55d526d93827e2
base: a5dce6b9ed4588e3be4fb67305aa09b34074b3a4

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arch-score / arch-score id=129094382497 success
budget-raise-gate / budget-raise-gate id=129094382569 success
cancel-superseded id=129097841340 success
codeql id=129094383962 skipped
governance id=129094384047 skipped
hassfest id=129094383714 skipped
kernel-points id=129094385073 skipped
pr-contract / pr-contract id=129095034381 in_progress
prelude id=129097841605 in_progress
refresh id=129097841571 success
tests id=129094384671 skipped
validate id=129094384411 skipped

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 9282cb09: #3106
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude 'from datetime import datetime, timedelta, UTC' --prelude 'import asyncio as _r9f12_aio' --prelude 'from harness import FakeEntry as _r9f12_entry' --prelude 'from homeassistant.util import dt as _r9f12_dt' --prelude 'from types import SimpleNamespace as _r9f12_ns' 'R.section("R10-DEMAND-OVERBOOK' 'R.section("R9 P2: stamp owner, plausib'
             `tools/audit/seat/features_block.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_cop_gate_slab.py [--drawn 6.0]
             `dev/audit/harnesses/r10_cop_gate_slab.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r10_cop_gate_band.py --synthetic
             `dev/audit/harnesses/r10_cop_gate_band.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=ba6fd7e8b0b0502dfcce26df781810e474fc1d2f PYTHONPATH=tests/hastub ./tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         dev/audit/harnesses/r10_cop_gate_band.py
             `dev/audit/harnesses/r10_cop_gate_band.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         tests/stress.py
             `tests/stress.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/stress.py --memory-probe '{"season":"<s>","building":"typical_slab"}'
             `tests/stress.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  unverified git merge-tree --write-tree origin/main HEAD
             `git merge-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git diff --stat $(git merge-base origin/main HEAD)...HEAD -- '*_budgets.json'
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n "_commanded_split()" -- custom_components
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 10 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index aee0ae2b8..671eda224 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -985,9 +985,7 @@ def _interval_measured_heat_kw(coord: Any) -> float | None:
     The one place the substitution is decided, so the two interval learners
     and the slab estimate cannot diverge about what the interval delivered.
     """
-    meter = heat_energy.meter_of(coord)
-    split = coord._commanded_split()
-    a = meter.attribution(split)
+    a = heat_energy.meter_of(coord).attribution(coord._commanded_split())
     return heat_energy.space_heat_kw(coord._flow_bias.heat_output_kw, a, integrated=False)
 
 
@@ -1080,12 +1078,14 @@ async def _propagated_slab(coord: Any, prior: Any, prior_at: datetime | None) ->
     now = dt_util.now()
     dt_h = 0.0 if prior_at is None else utc_elapsed_seconds(now, prior_at) / 3600.0
     signals = coord._pump_signals
+    # Observed, the dwell's hours apportion the draw; none on space books 0 kW.
+    a = heat_energy.meter_of(coord).attribution(coord._commanded_split())
     kw = draw_range.space_draw_kw(
         coord._accuracy.draw,
         coord._measured_power,
-        coord._commanded_split(),
+        (a.space, a.dhw),
         shared=coord._immersion_active or signals.electric_heat.resistive_heat,
-        space_served=signals.space_heat or not signals.mode_observed,
+        space_served=a.observed or signals.space_heat or not signals.mode_observed,
     )
     if kw is not None and prior_at is not None and 0.0 < dt_h <= HOUSE_LOSS_MAX_SAMPLE_HOURS and (state := await _replay_interval(
         coord, prior, kw, prior.outdoor_temperature, prior_at, dt_h, "Slab estimate",
diff --git a/custom_components/heatpump_optimizer/draw_range.py b/custom_components/heatpump_optimizer/draw_range.py
index 6615fa7a4..803243f06 100644
--- a/custom_components/heatpump_optimizer/draw_range.py
+++ b/custom_components/heatpump_optimizer/draw_range.py
@@ -405,8 +405,9 @@ def space_draw_kw(
 ) -> float | None:
     """The space circuit's metered draw over one interval, or ``None``.
 
-    The running draw apportioned by ``split``, the plan's (space, hot water)
-    ask as the pump could serve it. ``None`` with no reading, or one a
+    The running draw apportioned by ``split``, the interval's (space, hot
+    water) weights: the mode dwell's hours where observed, else the plan's ask
+    as the pump could serve it. ``None`` with no reading, or one a
     resistive element ``shared``; ``0.0`` while the pump's mode heats no
     rooms. Not gated on the pump drawing what it was asked: a pump drawing
     less is what this measures.
diff --git a/dev/audit/harnesses/r10_cop_gate_band.py b/dev/audit/harnesses/r10_cop_gate_band.py
new file mode 100644
index 000000000..bb392dc43
--- /dev/null
+++ b/dev/audit/harnesses/r10_cop_gate_band.py
@@ -0,0 +1,109 @@
+#!/usr/bin/env python3
+"""R10-COP-GATE-E (#3106): drawn power against the flow set-point between the duty gate and the ceiling.
+
+Reads every recorded replay fixture under ``tests/replay/`` (format: each
+``states[entity]`` a list of ``[last_changed, state, attrs, last_updated]``)
+whose ``entry.options`` name a flow set-point and a power entity. A
+set-point step counts when it lies strictly inside the band,
+``pump_arbiter.FLOW_GATE_C + draw_range.GATE_TOLERANCE_K`` to the configured
+ceiling (``thermal_model.configured_flow_heat_c`` on the entry's options) less ``draw_range.CEILING_TOLERANCE_K``,
+and the mode entity reads space heat alone (``pump_mode.resolve`` is
+``MODE_HEAT``) for the whole step: a combined or hot-water mode's draw is
+not the space set-point's. Its draw is the last power reading inside the
+step (the settled one), and a step with no reading is not counted.
+
+Per fixture one ``RESULT`` line: ``steps`` (counted), ``distinct_c``
+(distinct set-points among them) and, where ``distinct_c >= 3``, the fitted
+``gain_kw_per_k`` (least squares) and ``max_resid_kw`` (the largest departure
+from that line: linear where it is within the readings' own spread). Fewer
+than three distinct set-points fit no line and its curvature: ``fit=none``.
+
+    PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r10_cop_gate_band.py [--synthetic] [FIXTURE.json ...]
+
+Each ``FIXTURE.json`` named is read beside the committed ones (an owner's
+recording in the same format, kept out of the tree).
+
+Null control: ``--synthetic`` adds a fixture made here, four in-band steps
+drawing exactly ``0.1 kW/K`` above the gate, through the same pairing; it
+must read ``distinct_c=4 gain_kw_per_k=0.1 max_resid_kw=0.0``, so a fixture
+reading ``fit=none`` lacks the data rather than the instrument a fit.
+"""
+from __future__ import annotations
+
+import glob
+import json
+import sys
+from datetime import datetime, timedelta, timezone
+
+
+def steps(data: dict) -> list[tuple[float, float]]:
+    from heatpump_optimizer import draw_range, pump_arbiter, pump_mode
+    from heatpump_optimizer.thermal_model import configured_flow_heat_c
+
+    opts = data.get("entry", {}).get("options", {})
+    sp_id, pw_id = opts.get("space_setpoint_entity"), opts.get("heat_pump_power_entity")
+    mode_id = opts.get("heat_pump_mode_entity")
+    if not sp_id or not pw_id or opts.get("space_setpoint_unit", "flow") != "flow":
+        return []
+    states = data["states"]
+    lo = pump_arbiter.FLOW_GATE_C + draw_range.GATE_TOLERANCE_K
+    hi = configured_flow_heat_c(opts) - draw_range.CEILING_TOLERANCE_K
+    at = lambda row: datetime.fromisoformat(row[0])  # noqa: E731
+    sps = [(at(r), float(r[1])) for r in states.get(sp_id, []) if _num(r[1])]
+    pws = [(at(r), float(r[1])) for r in states.get(pw_id, []) if _num(r[1])]
+    modes = [(at(r), pump_mode.resolve(r[1])) for r in states.get(mode_id, [])] if mode_id else []
+    out = []
+    for i, (start, sp) in enumerate(sps):
+        end = sps[i + 1][0] if i + 1 < len(sps) else datetime.max.replace(tzinfo=timezone.utc)
+        if not lo < sp < hi:
+            continue
+        held = [m for t, m in modes if t <= start][-1:] + [m for t, m in modes if start < t < end]
+        if held != [pump_mode.MODE_HEAT] * len(held) or not held:
+            continue
+        inside = [kw for t, kw in pws if start <= t < end]
+        if inside:
+            out.append((sp, inside[-1]))
+    return out
+
+
+def _num(s: object) -> bool:
+    try:
+        float(s)  # type: ignore[arg-type]
+        return True
+    except (TypeError, ValueError):
+        return False
+
+
+def fit(points: list[tuple[float, float]]) -> str:
+    xs = sorted({sp for sp, _ in points})
+    if len(xs) < 3:
+        return f"steps={len(points)} distinct_c={len(xs)} fit=none"
+    n = len(points)
+    mx = sum(p[0] for p in points) / n
+    my = sum(p[1] for p in points) / n
+    gain = sum((x - mx) * (y - my) for x, y in points) / sum((x - mx) ** 2 for x, _ in points)
+    resid = max(abs(y - (my + gain * (x - mx))) for x, y in points)
+    return f"steps={n} distinct_c={len(xs)} gain_kw_per_k={round(gain, 6)} max_resid_kw={round(resid, 6)}"
+
+
+def synthetic() -> dict:
+    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
+    sp = [[(t0 + timedelta(hours=i)).isoformat(), str(c), None, None] for i, c in enumerate((30.0, 35.0, 40.0, 45.0))]
+    pw = [[(t0 + timedelta(hours=i, minutes=20)).isoformat(), str(round(0.1 * (c - 25.0), 6)), None, None]
+          for i, c in enumerate((30.0, 35.0, 40.0, 45.0))]
+    return {"entry": {"options": {"space_setpoint_entity": "number.sp", "heat_pump_power_entity": "sensor.p",
+                                  "heat_pump_mode_entity": "select.m", "space_setpoint_unit": "flow"}},
+            "states": {"number.sp": sp, "sensor.p": pw, "select.m": [[t0.isoformat(), "Heating", None, None]]}}
+
+
+def main() -> None:
+    named = [a for a in sys.argv[1:] if not a.startswith("--")]
+    fixtures = {path: json.load(open(path)) for path in sorted(glob.glob("tests/replay/*.json")) + named}
+    if "--synthetic" in sys.argv[1:]:
+        fixtures["synthetic-linear"] = synthetic()
+    for name, data in fixtures.items():
+        print(f"RESULT {name} {fit(steps(data))}")
+
+
+if __name__ == "__main__":
+    main()
diff --git a/dev/audit/harnesses/r10_cop_gate_slab.py b/dev/audit/harnesses/r10_cop_gate_slab.py
new file mode 100644
index 000000000..5a6951d0f
--- /dev/null
+++ b/dev/audit/harnesses/r10_cop_gate_slab.py
@@ -0,0 +1,118 @@
+#!/usr/bin/env python3
+"""R10-COP-GATE-E (#3106): the unsensed slab across a mode switch, through ``_propagated_slab``.
+
+Two coordinator cycles 30 min apart through ``_update_current_state`` on an
+install with a power meter, a live mode entity and no floor sensor; the plan
+asks 4 kW of space heat and none of hot water. The first cycle reads the mode
+of the interval's start, the second reads ``DRAWN_KW`` and the mode at the
+close, its ``last_changed`` at the switch. ``_replay_interval`` is wrapped to
+record the kW the slab is advanced by.
+
+Arms:
+
+  * ``all_space`` (the null control): heating at both reads. The dwell is all
+    space, so the booked kW is the draw at both ends of any fix.
+  * ``switch_back``: hot water for the first half, heating at the close.
+  * ``switch_out``: heating for the first half, hot water at the close.
+  * ``truth``: ``all_space`` drawing ``DRAWN_KW`` x the switch arms' space
+    share, the same space energy spread over the interval (a pump drawing a
+    constant kW while on space heat). Its slab is the reference the two
+    candidate rules are scored against.
+
+Per arm one ``RESULT`` line: ``booked_kw`` (``None`` when nothing was
+replayed and the plan's trajectory stands), ``space_share`` (the dwell's
+space hours over the interval's), ``over_kw`` = booked minus ``DRAWN_KW`` x
+the share, and ``slab``. ``plan`` is the plan's trajectory at the close,
+the fall-back rule's value.
+
+    PYTHONPATH=tests/hastub:custom_components:tests \\
+        python3 dev/audit/harnesses/r10_cop_gate_slab.py [--drawn KW]
+
+Perturbation: ``--drawn`` scales the draw; ``over_kw`` on ``switch_back``
+scales with it at the base (direction: up with the draw) and stays 0 at
+the head, and ``all_space`` reads ``over_kw=0`` at both ends.
+"""
+from __future__ import annotations
+
+import argparse
+import asyncio
+from datetime import datetime, timedelta, timezone
+
+DRAWN_KW = 4.0
+T0 = datetime(2026, 10, 5, 3, 0, tzinfo=timezone.utc)
+STEP = timedelta(minutes=30)
+HEAT, DHW = "Heating", "DHW (Hot Water)"
+
+
+def arm(start_mode: str, close_mode: str, drawn_kw: float) -> tuple[float | None, float | None, float]:
+    import homeassistant.util.dt as dt_mod
+    from harness import FakeEntry, FakeHass, FakeState
+
+    import heatpump_optimizer.coordinator as C
+    from heatpump_optimizer import heat_energy
+    from heatpump_optimizer.thermal_model import ThermalState
+
+    cfg = {
+        "tibber_token": "x", "weather_entity": "weather.home",
+        "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
+        "optimization_interval": 30.0, "heat_pump_power_entity": "sensor.hp_power",
+        "heat_pump_mode_entity": "select.pump_mode",
+    }
+    coord = C.HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
+    coord._snapshots_loaded = True
+    ctx = getattr(coord, "_ctx", coord)
+    ctx._thermal_params.dhw_enabled = False
+    booked: list[float] = []
+    replay = C._replay_interval
+
+    async def recording(c, prior, kw, *rest):
+        booked.append(kw)
+        return await replay(c, prior, kw, *rest)
+
+    C._replay_interval = recording
+    t1 = T0 + STEP
+    switch = T0 + STEP / 2
+    try:
+        for at, mode, changed, kw in ((T0, start_mode, T0 - STEP, 0.0), (t1, close_mode, switch, drawn_kw)):
+            ctx.publish(coord, ThermalState(room_temperature=21.0, outdoor_temperature=5.0, slab_temperature=23.0))
+            coord._last_house_sample_time = at - STEP
+            coord._optimization_result = type("R", (), {
+                "slab_temp_trajectory": [25.0, 25.5, 26.0],
+                "timestamps": [at + STEP * i for i in range(3)],
+            })()
+            coord._current_action = {"power": 4.0, "dhw_power": 0.0, "mode": "auto", "heat_pump_on": True}
+            dt_mod.freeze(at)
+            for entity, value, unit in (("sensor.indoor", "21.0", "°C"), ("sensor.outdoor", "5.0", "°C"),
+                                        ("sensor.hp_power", f"{kw}", "kW")):
+                coord.hass.states.set(entity, FakeState(value, last_updated=at, unit=unit))
+            state = FakeState(mode, last_updated=at, attributes={"options": [HEAT, DHW]})
+            state.last_changed = changed if start_mode != close_mode or at == T0 else T0 - STEP
+            coord.hass.states.set("select.pump_mode", state)
+            booked.clear()
+            asyncio.run(coord._update_current_state())
+    finally:
+        dt_mod.freeze(None)
+        C._replay_interval = replay
+    a = heat_energy.meter_of(coord).attribution((4.0, 0.0))
+    share = a.space / (a.space + a.dhw) if a.observed and a.space + a.dhw > 0 else None
+    slab = float(getattr(coord, "_ctx", coord)._current_state.slab_temperature)
+    return (booked[-1] if booked else None), share, slab
+
+
+def main() -> None:
+    ap = argparse.ArgumentParser()
+    ap.add_argument("--drawn", type=float, default=DRAWN_KW)
+    drawn = ap.parse_args().drawn
+    shares = {}
+    for name, (start, close) in (("all_space", (HEAT, HEAT)), ("switch_back", (DHW, HEAT)),
+                                 ("switch_out", (HEAT, DHW))):
+        kw, share, slab = arm(start, close, drawn)
+        shares[name] = share
+        over = None if kw is None or share is None else round(kw - drawn * share, 6)
+        print(f"RESULT {name} booked_kw={kw} space_share={share} over_kw={over} slab={slab:.4f}")
+    kw, _share, slab = arm(HEAT, HEAT, drawn * shares["switch_back"])
+    print(f"RESULT truth booked_kw={kw} slab={slab:.4f} plan=25.0000")
+
+
+if __name__ == "__main__":
+    main()
diff --git a/dev/programme/delivery/3371.md b/dev/programme/delivery/3371.md
new file mode 100644
index 000000000..0e047cfa6
--- /dev/null
+++ b/dev/programme/delivery/3371.md
@@ -0,0 +1 @@
+- [#3371](https://github.com/tvofi/heatpump_optimizer/pull/3371) — **open**, R10-COP-GATE-E: cop gate e (R10-COP-GATE-E)
diff --git a/tests/closures.json b/tests/closures.json
index 1629cf8ff..2d3e579c7 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4043,6 +4043,8 @@
    "dev/audit/harnesses/r10_configflow_pages.py",
    "dev/audit/harnesses/r10_cop_conversions.py",
    "dev/audit/harnesses/r10_cop_gate.py",
+   "dev/audit/harnesses/r10_cop_gate_band.py",
+   "dev/audit/harnesses/r10_cop_gate_slab.py",
    "dev/audit/harnesses/r10_cop_gate_top.py",
    "dev/audit/harnesses/r10_cop_gate_vent.py",
    "dev/audit/harnesses/r10_cop_partload.py",
diff --git a/tests/features.py b/tests/features.py
index 7851bf475..81ec024a8 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -2198,12 +2198,13 @@ R.section("R10-DEMAND-OVERBOOK: the unsensed slab advances by metered heat (#249
 # draw instead. The previous plan says 25 degC after 30 min of 4 kW; the
 # prior slab is 23 degC.
 from heatpump_optimizer import draw_range as _r10do_draw  # noqa: E402
+from heatpump_optimizer import heat_energy as _r10do_energy  # noqa: E402
 from heatpump_optimizer.thermal_model import ThermalState as _r10do_state  # noqa: E402
 
 _r10do_t0 = datetime(2026, 10, 5, 3, 0, tzinfo=UTC)
 
 
-def _r10do_slab(meter, drawn_kw, sampled=True, gap_h=0.5, *, mode=None, immersion=False):
+def _r10do_slab(meter, drawn_kw, sampled=True, gap_h=0.5, *, mode=None, immersion=False, before=None, switched=True):
     cfg = {
         "tibber_token": "x",
         "weather_entity": "weather.home",
@@ -2239,8 +2240,16 @@ def _r10do_slab(meter, drawn_kw, sampled=True, gap_h=0.5, *, mode=None, immersio
             unit = "kW" if entity == "sensor.hp_power" else "°C"
             coord.hass.states.set(entity, FakeState(value, last_updated=now, unit=unit))
         if mode is not None:
-            coord.hass.states.set("select.pump_mode", FakeState(
-                mode, last_updated=now, attributes={"options": [mode]}))
+            mode_state = FakeState(mode, last_updated=now, attributes={"options": [mode]})
+            if before is not None:
+                # The previous cycle read ``before`` live at the interval's
+                # start; the pump switched to ``mode`` halfway through it.
+                start = now - timedelta(hours=gap_h)
+                meter = _r10do_energy.meter_of(coord)
+                meter.observe_mode(start, before, True, start - timedelta(hours=1))
+                meter.cycle = (None, start)
+                mode_state.last_changed = now - timedelta(hours=gap_h / 2 if switched else gap_h + 1)
+            coord.hass.states.set("select.pump_mode", mode_state)
         _r9f12_aio.run(coord._update_current_state())
     finally:
         _r9f12_dt.freeze(None)
@@ -2293,6 +2302,34 @@ R.check(
     "slab dhw-only/off=%.3f/%.3f heating/full=%.3f/%.3f"
     % (_r10do_dhw_only, _r10do_off, _r10do_heating, _r10do_full),
 )
+# R10-COP-GATE-E (#3106): a mode switch inside the interval. The draw read at
+# the close is apportioned by the dwell's hours in each duty, not by the live
+# mode alone: hot water for the first half and heating at the close books half
+# the draw as space heat, the slab of a pump that drew half as much all
+# interval long; the reverse switch books the same half, not 0 kW. A dwell
+# all on one duty reads as before (the null control).
+_r10do_half = _r10do_slab(True, 2.0, mode="Heating", before=_r10do_energy.MODE_HEAT, switched=False)
+_r10do_swback = _r10do_slab(True, 4.0, mode="Heating", before=_r10do_energy.MODE_DHW)
+_r10do_out = _r10do_slab(True, 4.0, mode="DHW (Hot Water)", before=_r10do_energy.MODE_HEAT)
+_r10do_still = _r10do_slab(True, 4.0, mode="Heating", before=_r10do_energy.MODE_HEAT, switched=False)
+R.check(
+    "R10-COP-GATE-E: a switch back from hot water to heating advances the slab "
+    "by the dwell's space share of the draw, not the whole draw as space heat",
+    _r10do_swback == _r10do_half and _r10do_swback < _r10do_heating,
+    "slab switch-back/half-draw/heating=%.4f/%.4f/%.4f" % (_r10do_swback, _r10do_half, _r10do_heating),
+)
+R.check(
+    "R10-COP-GATE-E: a switch from heating to hot water books the dwell's "
+    "space share of the draw, not 0 kW",
+    _r10do_out == _r10do_half and _r10do_out > _r10do_dhw_only,
+    "slab switch-out/half-draw/dhw-only=%.4f/%.4f/%.4f" % (_r10do_out, _r10do_half, _r10do_dhw_only),
+)
+R.check(
+    "R10-COP-GATE-E: a dwell all on space heat advances the slab by the whole "
+    "draw, as with the live mode alone (null control)",
+    _r10do_still == _r10do_heating,
+    "slab all-space/heating=%.4f/%.4f" % (_r10do_still, _r10do_heating),
+)
 R.check(
     "#2499: a resistive element sharing the meter gives no space draw; a pump "
     "not serving rooms gives 0 kW",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
