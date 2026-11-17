# Review packet #3691
head: 4e85c6a50e3e234e428fad8402bbcdf623a796cb
base: 54cb7211642364d762ba47f42d5f7b8a5953f742

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=133704234862 skipped
cancel-superseded id=133705532542 queued
prelude id=133705532625 queued
refresh id=133705532229 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item fcac48c8: R11-VALVE-REFERENCE: R11-VALVE-REFERENCE resolved on origin/handoff/audit-r10-roster
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: SCOPED -- 0 script(s) run, 33 scoped out.
             no segment of this names a program this check knows
  ok         python3 dev/audit/harnesses/r10_advisor_steady_seams.py fields
             `dev/audit/harnesses/r10_advisor_steady_seams.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_advisor_steady_seams.py weekday
             `dev/audit/harnesses/r10_advisor_steady_seams.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r11_advisor_measures.py valve
             `dev/audit/harnesses/r11_advisor_measures.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r11_advisor_measures.py asks
             `dev/audit/harnesses/r11_advisor_measures.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r11_advisor_measures.py loop
             `dev/audit/harnesses/r11_advisor_measures.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r11_advisor_measures.py pv pvloop
             `dev/audit/harnesses/r11_advisor_measures.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 7 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_advisor_steady_seams.py b/dev/audit/harnesses/r10_advisor_steady_seams.py
index f4db59503f..78c9cd7fa7 100644
--- a/dev/audit/harnesses/r10_advisor_steady_seams.py
+++ b/dev/audit/harnesses/r10_advisor_steady_seams.py
@@ -23,6 +23,10 @@ not go through ``async_simulate``.
            (the ``holds`` line prints the room it settles at), so its day
            setpoints tie and two passes do not settle it: that row reads the
            thermostat reference on such a house, not the schedule arithmetic. Null: the same start twice.
+           A row is missed when it reads the pair, opposes its ask, or reads 0
+           where the ask binds; a 0 is correct (``zero_kind``) when, on every
+           distinct day of the week, neither schedule's thermostat draws on a
+           step the ask moves: the room coasts above both setpoints there.
   pair     item pair-other-asks: the steady pair's figure for a hot-water ask
            alone on a tanked house, by measured start and by hour. Null: the
            room and slab start (columns 1 and 2), which the held start holds.
@@ -125,6 +129,40 @@ def figure(opt, params, asked, given):
     return price_tiles.schedule_figure(*days, float(np.mean(given.forecast.prices)), 0.0, 24.0)[whatif.STEADY_KEY]
 
 
+#: A draw at or under this is none, kW: the thermostat's power is clipped at 0, never signed.
+IDLE_KW = 1e-9
+
+
+def zero_kind(opt, params, asked, given):
+    """Why a schedule figure reads 0: ``"idle"`` or ``"binds"``.
+
+    ``"idle"`` when, on every distinct day of ``reference_day``'s week, the
+    thermostat holding either schedule draws nothing, on its counted second
+    pass, at any step whose setpoint the ask moves: the room coasts above both
+    setpoints there, so the ask saves or costs nothing and 0 is the right
+    figure. Otherwise the ask moves a step the thermostat heats on, held at
+    the pump's maximum both ways or not, and a 0 says nothing of it: a miss.
+    """
+    sides = [shadow(opt, params, a) for a in ({}, asked)]
+    weather = optimizer._day_mean_weather(optimizer._horizon_weather(given.forecast, N), N)
+    seen = set()
+    for offset in range(7):
+        when, hours = optimizer._step_clock(given.start_time + timedelta(days=offset), N, DT)
+        comforts = [side._build_comfort_bounds(hours, N, None, None, when)[0] for side in sides]
+        targets = [np.asarray(optimizer._baseline_targets(c, N, side.config.target_temp)) for c, side in zip(comforts, sides)]
+        key = tuple(map(tuple, targets))
+        if key in seen:
+            continue
+        seen.add(key)
+        moved = targets[0] != targets[1]
+        for side, comfort in zip(sides, comforts):
+            _, settled = side._compute_baseline_power(weather, given.state, DT, comfort)
+            power, _ = side._compute_baseline_power(weather, given.state, DT, comfort, start=settled)
+            if np.any(np.asarray(power)[moved] > IDLE_KW):
+                return "binds"
+    return "idle"
+
+
 def arm_weekday():
     for label, config in (("weekend comfort set", WEEKEND), ("null, no weekend comfort", {})):
         opt, params = build(**config)
@@ -138,7 +176,7 @@ def arm_weekday():
         print(f"RESULT weekday {label}: asks whose figure moves with the weekday {moved}, "
               f"asks leaving the schedule branch on some day {pairs}")
     opt, params = build(**WEEKEND)
-    friday, rows, wrong, pairs, zero = MONDAY + timedelta(days=4), 0, 0, 0, 0
+    friday, rows, wrong, pairs, zero, idle = MONDAY + timedelta(days=4), 0, 0, 0, 0, 0
     for hour in HOURS:
         for _name, asked, want in asks(opt, WEEKEND_ASKS):
             f = figure(opt, params, asked, inputs(hour, start(), friday))
@@ -146,7 +184,9 @@ def arm_weekday():
             pairs += f is None
             wrong += f is not None and f * want < 0
             zero += f == 0
-    print(f"RESULT weekday friday: rows {rows} against the ask {wrong} rounding to 0.00 {zero} reading the pair {pairs}")
+            idle += f == 0 and zero_kind(opt, params, asked, inputs(hour, start(), friday)) == "idle"
+    print(f"RESULT weekday friday: rows {rows} against the ask {wrong} rounding to 0.00 {zero} "
+          f"(of them idle on every step the ask moves {idle}) reading the pair {pairs}")
 
 
 def arm_fields():
@@ -157,12 +197,16 @@ def arm_fields():
                       ("valve, one tank", {"valve": True}), ("two-zone valve two-tank", {"two_zone": True, "valve": True})):
         opt, params = build(**kw)
         worst = dict.fromkeys((m[0] for m in moves), 0.0)
-        rows = wrong = 0
+        rows = against = pairs = 0
+        zeros = {"idle": [], "binds": []}
         for hour in HOURS:
-            for _name, asked, want in asks(opt):
+            for name, asked, want in asks(opt):
                 base = figure(opt, params, asked, inputs(hour, start()))
                 rows += 1
-                wrong += base is None or base * want <= 0
+                pairs += base is None
+                against += base is not None and base * want < 0
+                if base == 0:
+                    zeros[zero_kind(opt, params, asked, inputs(hour, start()))].append(f"{name} {hour:02d}:00")
                 for move, change in moves:
                     other = figure(opt, params, asked, inputs(hour, start(**change)))
                     worst[move] = max(worst[move], abs(other - base))
@@ -171,7 +215,12 @@ def arm_fields():
         _, held = opt._compute_baseline_power(weather, start(), DT, np.full(N, 21.0), start=held)
         print(f"  fields {label} holds: a thermostat set to 21.0 all day ends its second pass with the room at "
               f"{held.room_temperature:.2f}")
-        print(f"RESULT fields {label}: rows {rows} at 0 or against the ask {wrong}; largest move of the figure by start: "
+        print(f"  fields {label} zeros: idle on every moved step {zeros['idle'] or 'none'}; "
+              f"binding {zeros['binds'] or 'none'}")
+        print(f"RESULT fields {label}: rows {rows} missed {pairs + against + len(zeros['binds'])} "
+              f"(reading the pair {pairs}, against the ask {against}, at 0 where the ask binds {len(zeros['binds'])}), "
+              f"at 0 and idle on every step the ask moves (a correct zero) {len(zeros['idle'])}; "
+              "largest move of the figure by start: "
               + ", ".join(f"{m} {v:.2f}" for m, v in worst.items()))
 
 
diff --git a/dev/audit/harnesses/r11_advisor_measures.py b/dev/audit/harnesses/r11_advisor_measures.py
index 40cb45e0f5..971ea60012 100644
--- a/dev/audit/harnesses/r11_advisor_measures.py
+++ b/dev/audit/harnesses/r11_advisor_measures.py
@@ -121,27 +121,31 @@ def arm_asks():
 def arm_valve():
     for label, config in (("weekend comfort set", seams.WEEKEND), ("null, no weekend comfort", {})):
         opt, params = seams.build(two_zone=True, valve=True, **config)
-        moved = pairs = wrong = zero = 0
+        moved = pairs = wrong = zero = idle = 0
         for name, asked, want in seams.asks(opt, seams.WEEKEND_ASKS if config else ()):
-            week = [seams.figure(opt, params, asked, seams.inputs(9, seams.start(), seams.MONDAY + timedelta(days=d)))
-                    for d in range(7)]
+            given = [seams.inputs(9, seams.start(), seams.MONDAY + timedelta(days=d)) for d in range(7)]
+            week = [seams.figure(opt, params, asked, g) for g in given]
             pairs += sum(f is None for f in week)
             moved += len({f for f in week if f is not None}) > 1
             wrong += sum(f is not None and f * want < 0 for f in week)
             zero += sum(f == 0 for f in week)
+            idle += sum(f == 0 and seams.zero_kind(opt, params, asked, g) == "idle" for f, g in zip(week, given))
             print(f"  valve {label}: {name} asked 09:00 Mon..Sun: " + " ".join("pair" if f is None else f"{f:+.1f}" for f in week))
         print(f"RESULT valve {label}: asks whose figure moves with the weekday {moved}, days against the ask {wrong}, "
-              f"days at 0.00 {zero}, days leaving the schedule branch {pairs}")
+              f"days at 0.00 {zero} (of them idle on every step the ask moves {idle}), days leaving the schedule branch {pairs}")
     opt, params = seams.build(two_zone=True, valve=True, **seams.WEEKEND)
-    friday, rows, wrong, pairs, zero = seams.MONDAY + timedelta(days=4), 0, 0, 0, 0
+    friday, rows, wrong, pairs, zero, idle = seams.MONDAY + timedelta(days=4), 0, 0, 0, 0, 0
     for hour in seams.HOURS:
         for _name, asked, want in seams.asks(opt, seams.WEEKEND_ASKS):
-            f = seams.figure(opt, params, asked, seams.inputs(hour, seams.start(), friday))
+            given = seams.inputs(hour, seams.start(), friday)
+            f = seams.figure(opt, params, asked, given)
             rows += 1
             pairs += f is None
             wrong += f is not None and f * want < 0
             zero += f == 0
-    print(f"RESULT valve friday: rows {rows} against the ask {wrong} at 0.00 {zero} reading the pair {pairs}")
+            idle += f == 0 and seams.zero_kind(opt, params, asked, given) == "idle"
+    print(f"RESULT valve friday: rows {rows} against the ask {wrong} at 0.00 {zero} "
+          f"(of them idle on every step the ask moves {idle}) reading the pair {pairs}")
     weather = seams.optimizer._day_mean_weather(seams.optimizer._horizon_weather(seams.inputs(9, seams.start()).forecast, seams.N), seams.N)
     for set_to in (21.0, 22.0, 23.0):
         _, held = opt._compute_baseline_power(weather, seams.start(), DT, np.full(seams.N, set_to))
diff --git a/dev/programme/delivery/3691.md b/dev/programme/delivery/3691.md
new file mode 100644
index 0000000000..d1dd75a177
--- /dev/null
+++ b/dev/programme/delivery/3691.md
@@ -0,0 +1 @@
+- [#3691](https://github.com/tvofi/heatpump_optimizer/pull/3691) — **open**, R11-ADVISOR-MEASURES part 2: carries (R11-ADVISOR-MEASURES)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
