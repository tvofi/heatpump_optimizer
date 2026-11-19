# Review packet #3803
head: 338aa528f9c50def49f173137a9588d7a7f39574
base: 1723f9fdc9d8a6e6987190d2887686297a621dd4

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=135272844027 success
arch-score / arch-score id=135270354168 success
arm id=135268956859 skipped
budget-raise-gate / budget-raise-gate id=135270354096 success
cancel-superseded id=135268972917 success
codeql id=135270355998 skipped
codeql / Analyze (actions) id=135270298498 success
codeql / Analyze (javascript-typescript) id=135270298520 success
codeql / Analyze (python) id=135270298694 success
gate id=135272655493 failure
governance id=135270355842 skipped
governance / env-matrix id=135270298557 success
governance / instrument-self-tests id=135270298623 success
governance / policy-docs id=135270298642 success
governance / record id=135270301452 skipped
governance / wave-script id=135270298589 success
hassfest id=135270356719 skipped
hassfest / hassfest id=135270298489 success
kernel-points id=135270355920 skipped
pr-contract id=135272656340 skipped
prelude id=135268972688 success
refresh id=135268972944 success
sweep-self id=135274308842 skipped
tests id=135270355808 skipped
tests / arch-instrument id=135272490347 success
tests / briefs id=135270298611 success
tests / browser id=135272490092 success
tests / closure-scope id=135270298669 success
tests / closures id=135272490650 in_progress
tests / coverage id=135272490241 in_progress
tests / fast (3.14) id=135272490119 in_progress
tests / mutation id=135270298659 success
tests / mutation-autofix id=135273838388 skipped
tests / mutation-pins id=135273835662 skipped
tests / nightly-ha id=135272491630 skipped
tests / nightly-status id=135270298672 failure
tests / replay id=135272493129 skipped
tests / typing id=135272490218 success
validate id=135270356234 skipped
validate / validate-hacs id=135270298696 success

## Refusals
none

## Advisories
required-wait: required context `gate` reads concluded failure at 338aa528f9c50def49f173137a9588d7a7f39574 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: SCOPED -- 28 script(s) run, 5 scoped out.
             no segment of this names a program this check knows
  ok         PYTHONPATH=tests/hastub:custom_components:tests OPENBLAS_NUM_THREADS=1 python3 dev/audit/harnesses/room_lift_solve.py
             `dev/audit/harnesses/room_lift_solve.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 2 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/rooms.py b/custom_components/heatpump_optimizer/rooms.py
index dd2a05e4c3..8cb4c05b88 100644
--- a/custom_components/heatpump_optimizer/rooms.py
+++ b/custom_components/heatpump_optimizer/rooms.py
@@ -286,8 +286,11 @@ def lifted(
 
     Per step the lift is the smallest of the held lift, the ramp, and what
     the step's band leaves over ``base`` under its comfort target, so the
-    lifted floor never passes the target the same solve pulls towards. The
-    ramp starts at the house's margin over the floor ``base`` already
+    lifted floor never passes the target the same solve pulls towards. It
+    reaches the target, with no headroom kept under it, and the plan's peak
+    may then pass the unlifted plan's: the plan stores heat above a floor held
+    at the target, a rise accepted rather than clipped (round-11 ruling,
+    2026-11-18; ``tests/features.py`` pins it). The ramp starts at the house's margin over the floor ``base`` already
     raised, never under zero. A step on a holiday date takes no lift, as a
     house that is away takes none.
 
diff --git a/dev/audit/harnesses/room_lift_solve.py b/dev/audit/harnesses/room_lift_solve.py
index d492cf30c7..5d81997ca0 100644
--- a/dev/audit/harnesses/room_lift_solve.py
+++ b/dev/audit/harnesses/room_lift_solve.py
@@ -23,9 +23,17 @@ power schedule``:
   * ``lift`` -- the fixture's lift (ramped from the house's 0.1 K margin, to
     the 0.5 K day band, 1.0 K at night). Expect more space energy, a higher
     lowest temperature, and a lifted floor (the configuration's floor plus
-    the array) at or under the comfort target at every step. The highest
-    planned temperature is printed, not judged: a floor held at the target
-    leaves the plan's stored heat above it.
+    the array) at or under the comfort target at every step, and at it once
+    the ramp has caught up. The highest planned temperature may rise above
+    ``none``'s: a floor held at the target leaves the plan's stored heat above
+    it, and that rise is accepted (round-11 ruling of 2026-11-18, option A:
+    no clip and no headroom under the target), so it is printed and its
+    direction checked, never bounded.
+  * ``lift_cap_removed`` / ``lift_cap_zero`` -- the null control for the
+    peak: ``rooms.ROOM_LIFT_CAP_C`` set to infinity and to zero around
+    ``rooms.resolve``. With the cap removed the peak still rises over
+    ``none``'s (the rise is the floor's, not the cap's); at zero no lift is
+    held and the plan is ``none``'s.
   * ``lift_pinned_off`` / ``none_pinned_off`` -- a forced-off space pin for
     hours 1 to 3 with the lifted array forced in (the coordinator never
     builds this: a pin gates the lift) against the same pin unlifted: the
@@ -118,12 +126,25 @@ def main() -> int:
     print("lift margins, first 8 steps and the largest:",
           np.round(lift_margins[:8], 4).tolist(), float(lift_margins.max()))
     lift = row("lift", solve(lift_margins))
+    capped = {}
+    for name, cap in (("lift_cap_removed", float("inf")), ("lift_cap_zero", 0.0)):
+        saved, rooms.ROOM_LIFT_CAP_C = rooms.ROOM_LIFT_CAP_C, cap
+        try:
+            got = margins()
+        finally:
+            rooms.ROOM_LIFT_CAP_C = saved
+        capped[name] = (got, row(name, solve(got)))
     config = _config()
     clock = [START + timedelta(hours=DT * i) for i in range(N)]
     lifted_floor_ok = all(
         config.get_temp_bounds(t.hour + t.minute / 60.0, when=t)[0] + lift_margins[i]
         <= config.get_comfort_temp(t.hour + t.minute / 60.0, when=t) + 1e-9
         for i, t in enumerate(clock))
+    ramped = int(np.argmax(lift_margins >= 0.5))
+    lifted_floor_at_target = ramped > 0 and all(
+        abs(config.get_temp_bounds(t.hour + t.minute / 60.0, when=t)[0] + lift_margins[i]
+            - config.get_comfort_temp(t.hour + t.minute / 60.0, when=t)) < 1e-9
+        for i, t in enumerate(clock) if i >= ramped)
     pins = np.full(N, np.nan)
     pins[int(1 / DT):int(3 / DT)] = 0.0
     pinned_none, pinned_lift = solve(None, pins), solve(lift_margins, pins)
@@ -138,6 +159,13 @@ def main() -> int:
         "the lift plans more space energy": lift[0] > none[0],
         "the lift raises the lowest planned temperature": lift[1] > none[1],
         "the lifted floor is at or under the comfort target at every step": lifted_floor_ok,
+        "the lifted floor is at the comfort target at every step past the ramp": lifted_floor_at_target,
+        "the lift may raise the plan peak over the unlifted plan's (accepted)": lift[2] > none[2],
+        "the zeros control leaves the peak at the unlifted plan's": zeros[2] == none[2],
+        "null control: with the cap removed the peak still rises":
+            capped["lift_cap_removed"][1][2] > none[2],
+        "null control: at a zero cap nothing is lifted and the plan is none's":
+            capped["lift_cap_zero"][0] is None and capped["lift_cap_zero"][1][3] == none[3],
     }
     for name, ok in checks.items():
         print(f"{'ok  ' if ok else 'FAIL'} {name}")
diff --git a/docs/configuration.md b/docs/configuration.md
index ed7cb18556..993932926d 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -971,7 +971,7 @@ neither.
 | Setting | Default | Range | What it means |
 |---|---|---|---|
 | Room thermometers | none | up to 32 `climate` entities or `temperature` sensors | Optional, one per room. A room thermostat's own room temperature (its `current_temperature`) is read, not its HVAC mode; a temperature sensor's state is read as it is. Two sensors appear once the list is saved: **Room Average Temperature**, the mean over the rooms that read, and **Room Temperature Spread**, the warmest room less the coldest, in K. A room that is unavailable, older than six hours (times the staleness scale) or outside -30 to 60 °C is left out and listed under the average's `dropped` attribute; it never raises an input problem. With fewer than half the rooms readable both sensors read unknown. The indoor temperature sensor on **Sensors and entities** is still the one the model runs on, and the plan uses the rooms only with the setting below. Clearing the list removes it; a factory reset keeps it, as it keeps every sensor. |
-| Let a cold room raise the planned minimum | off | on / off | Off, a room list changes nothing in the plan. On, a room thermostat that reads further below its own target than the house reads below yours raises the minimum temperature the plan holds. Only a `climate` in `heat` or `auto` mode counts: a room switched off or cooling, a plain temperature sensor (it has no target) and a dropped room do not. The raise is the coldest such room's shortfall less the house's own, at most 1 °C, and it never lifts the minimum above your comfort target for that hour — so the plan holds the house at its target while a room is short, and never plans the house above it; raise the target for more. It rises from where the house is now by 0.25 °C an hour, moves only when the rooms ask for 0.2 °C more or less, and drops at once when it yields: in Economy mode, while a window is detected open, while away, on a holiday, while a heating slot is planned by hand, and in two-zone mode (the list does not say which floor a room is on). **Room Temperature Spread**'s `lift` attribute shows the size asked for, the room that set it and, when it yielded, to what. |
+| Let a cold room raise the planned minimum | off | on / off | Off, a room list changes nothing in the plan. On, a room thermostat that reads further below its own target than the house reads below yours raises the minimum temperature the plan holds. Only a `climate` in `heat` or `auto` mode counts: a room switched off or cooling, a plain temperature sensor (it has no target) and a dropped room do not. The raise is the coldest such room's shortfall less the house's own, at most 1 °C, and it never lifts the minimum above your comfort target for that hour — so the plan holds the house at its target while a room is short; raise the target for more. The minimum is not held back below the target, so the plan may store heat above the target, and its warmest planned temperature can be higher than it would be with the setting off. It rises from where the house is now by 0.25 °C an hour, moves only when the rooms ask for 0.2 °C more or less, and drops at once when it yields: in Economy mode, while a window is detected open, while away, on a holiday, while a heating slot is planned by hand, and in two-zone mode (the list does not say which floor a room is on). **Room Temperature Spread**'s `lift` attribute shows the size asked for, the room that set it and, when it yielded, to what. |
 
 ### Heating system and heat storage
 
diff --git a/tests/features.py b/tests/features.py
index 0852a921de..6b1170dca0 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -97117,4 +97117,57 @@ R.check(
 )
 
 
+# -- The plan peak under the lift: accepted, never clipped (round-11 ruling, 2026-11-18,
+# option A). The lifted floor reaches the comfort target and the plan may store heat above
+# it, so its peak may pass the unlifted plan's. These checks encode that choice: a clip of
+# the lift short of the target, or a headroom under it, fails the first; the zeros array
+# is the solver's own null control. The fixture is the design note's, solved through
+# the production optimizer on dev/audit/harnesses/room_lift_solve.py's inputs.
+from heatpump_optimizer.thermal_model import ThermalState as _rl_State  # noqa: E402
+
+_RL_PEAK_START = datetime(2026, 4, 15, 12, 0, tzinfo=UTC)
+_rl_peak_cfg = _rl_Config(horizon_hours=24, time_step_minutes=15, target_temp=20.0, min_temp=19.5,
+                          max_temp=23.0, comfort_temp_day=20.0, comfort_temp_night=20.0)
+_RL_PEAK_N = 96
+
+
+def _rl_peak_solve(margins):
+    """The plan's room temperatures past step 0 for ``margins``, from the harness's inputs."""
+    cfg = _grad_house(target_temperature=20.0, min_temperature=19.5)
+    outdoor, wind, rain, solar = _grad_weather("shoulder", _RL_PEAK_START)
+    state = _rl_State(
+        room_temperature=19.6, slab_temperature=20.6, outdoor_temperature=float(outdoor[0]),
+        dhw_temperature=50.0, dhw_hours_since_legionella=20.0, upper_floor_temperature=19.6,
+        lower_floor_temperature=19.6, buffer_tank_temperature=40.0)
+    result = _PvOpt(_PvModel(_PvParams.from_config(cfg)), _rl_peak_cfg).optimize(inputs=solve_inputs(
+        initial_state=state, prices=_grad_prices("winter_typical", _RL_PEAK_START),
+        outdoor_temps=outdoor, wind_speeds=wind, precipitation=rain, solar_radiation=solar,
+        start_time=_RL_PEAK_START, min_temp_margins=margins))
+    return np.asarray(result.room_temp_trajectory[1:], dtype=float)
+
+
+_rl_peak_m, _ = _rl_solve(cfg=_rl_peak_cfg, start=_RL_PEAK_START, n=_RL_PEAK_N)
+_rl_peak = {k: _rl_peak_solve(m) for k, m in
+            (("none", None), ("zeros", np.zeros(_RL_PEAK_N)), ("lift", _rl_peak_m))}
+_rl_peak_gap = None if _rl_peak_m is None else [
+    round(float(_rl_peak_cfg.get_comfort_temp(t.hour + t.minute / 60.0, when=t)
+                - _rl_peak_cfg.get_temp_bounds(t.hour + t.minute / 60.0, when=t)[0] - _rl_peak_m[i]), 9)
+    for i, t in enumerate(_RL_PEAK_START + timedelta(minutes=15 * i) for i in range(_RL_PEAK_N))]
+R.check(
+    "the lifted floor reaches the comfort target, no headroom under it, at every step past the "
+    "ramp (0.1 K at step 0, 0.25 K an hour, so from step 7)",
+    _rl_peak_gap is not None and _rl_peak_gap[0] > 0.0 and set(_rl_peak_gap[7:]) == {0.0},
+    f"gap to target {_rl_peak_gap and sorted(set(_rl_peak_gap))}",
+)
+R.check(
+    "the lift may raise the plan's peak over the unlifted plan's, and the lifted plan holds the "
+    "target past the ramp; null control, an all-zero margin array plans the unlifted plan",
+    float(_rl_peak["lift"].max()) > float(_rl_peak["none"].max())
+    and float(_rl_peak["lift"][12:].min()) >= 20.0 - 1e-6
+    and np.array_equal(_rl_peak["zeros"], _rl_peak["none"]),
+    f"peak none={_rl_peak['none'].max():.3f} zeros={_rl_peak['zeros'].max():.3f} "
+    f"lift={_rl_peak['lift'].max():.3f} lift min past 3 h={_rl_peak['lift'][12:].min():.3f}",
+)
+
+
 sys.exit(R.close("FEATURE CHECKS"))

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
